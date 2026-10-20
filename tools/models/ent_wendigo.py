"""El Wendigo -- starving deer-skull horror of the Bosque Negro (DEAD LINE).

Authored at 2x texel density (model.scale = 0.5) with rig.Rig absolute coordinates:
+Y down, ground at y = 24, the creature faces -Z, right_* parts on -X.
Every cube is authored in its bone's *unrotated* frame (limbs hanging straight down, neck/torso
straight up, skull facing -Z); bone rotations fold it into the hunched pose. Empty "mount" bones
(skull_mount, *_shoulder) cancel the torso lean so head/arm animation axes are world-aligned.
"""
import math

from mcmodel import Model, fbm, vnoise, hash3, face_light, pick
from rig import Rig
from paint import hx, mix, scale, edge, pixelart


def pal(*h):
    return [hx(c) for c in h]


# ------------------------------------------------------------------ palettes (dark -> light)
SKIN = pal('#0b0909', '#161212', '#221c1b', '#302826', '#403532', '#524440', '#66554f', '#7c6a61', '#958075')
FROST = pal('#070506', '#0e0b0c', '#161213', '#201a1a', '#2a2221', '#352b29', '#423634', '#524440', '#62524c')
BONE = pal('#17120f', '#2c241d', '#463b2f', '#635543', '#80715a', '#9e8f72', '#bbad8e', '#d5cbab', '#ece5cc')
ANTLER = pal('#110d0b', '#211914', '#352a20', '#4b3c2e', '#635140', '#7d6953', '#99836a', '#b8a386', '#d6c6a8')
FUR = pal('#060404', '#0d0a09', '#16110f', '#211915', '#2c221c', '#3a2d25', '#4b3b31', '#5e4b3e')
FLESH = pal('#160607', '#290b0c', '#3f1213', '#581c1a', '#722823', '#8b392e', '#a44d3c')
BLOOD = pal('#110203', '#1f0405', '#300709', '#430b0d', '#581012', '#6e1618')      # dried, near black
FRESH = pal('#2a0306', '#4a070c', '#6c0d12', '#8e1418', '#ae1f1d', '#c93226')      # wet, mouth + chest
CLAW = pal('#040304', '#09080b', '#110f14', '#1a171e', '#25212a', '#332e39', '#4a4452')
GAP = pal('#040202', '#0a0505', '#120808', '#1b0d0c', '#251412')
VOID = hx('#040203')
VEIN = hx('#2c2234')
CLAW_HI = hx('#6a6472')

VERT_Y = []     # design-space y of each spinal knob (filled by build; back_mat paints their shadows)


# ------------------------------------------------------------------ texel helpers
def local(ctx):
    """Texel centre in the cube's bone frame (unrotated, relative to the bone pivot)."""
    c = ctx.cube
    x0, y0, z0 = c.origin
    w, h, d = c.size
    x1, y1, z1 = x0 + w, y0 + h, z0 + d
    s, t, f = ctx.s, ctx.t, ctx.face
    if f == 'front':
        return x0 + s * w, y0 + t * h, z0
    if f == 'back':
        return x1 - s * w, y0 + t * h, z1
    if f == 'west':
        return x0, y0 + t * h, z1 - s * d
    if f == 'east':
        return x1, y0 + t * h, z0 + s * d
    if f == 'top':
        return x0 + s * w, y0, z1 - t * d
    return x0 + s * w, y1, z1 - t * d


def dpos(ctx):
    """Design-space (authoring) position of the texel: bone abs pivot + local."""
    lx, ly, lz = local(ctx)
    a = ctx.bone.abs
    return a[0] + lx, a[1] + ly, a[2] + lz


def light(ctx, k=1.0):
    return face_light(ctx) * k


def is_side(ctx):
    return ctx.face not in ('top', 'bottom')


def flat(ctx):
    return 0 in ctx.cube.size


def wcol(ctx):
    """Horizontal texel coordinate that wraps continuously around a cube's four sides."""
    w, h, d = ctx.cube.size
    f = ctx.face
    if f == 'front':
        return ctx.i
    if f == 'east':
        return w + ctx.i
    if f == 'back':
        return w + d + ctx.i
    if f == 'west':
        return 2 * w + d + ctx.i
    return ctx.i


def bands(n, lo=0.4, hi=0.6, amt=0.07):
    return amt if n > hi else (-amt if n < lo else 0.0)


def drip_len(col, seed, lo, length):
    h = hash3(col, 0, 0, seed)
    if h < lo:
        return -1.0
    return 1.0 + (h - lo) / (1 - lo) * length


def sub(ramp, a, b, v):
    """Pick from ramp[a..b] with v in 0..1."""
    return pick(ramp[a:b + 1], v)


# ------------------------------------------------------------------ blood
def blood_here(ctx):
    """Dried blood on the hands: 0 none, 1 blood, 2 dark crust edge."""
    n = ctx.bone.name
    col = wcol(ctx) + int(hash3(*ctx.cube.size, 3) * 50)
    if '_finger' in n:
        return 1
    if n.endswith('_hand'):
        if ctx.face == 'bottom':
            return 1
        if not is_side(ctx):
            return 0
        lim = 0.62 - hash3(col, 0, 0, 11) * 0.22      # ~40% of the palm, ragged upper edge
        return 1 if ctx.t > lim else (2 if ctx.t > lim - 0.1 else 0)
    if n.endswith('_forearm') and is_side(ctx):
        from_bottom = ctx.h - 1 - ctx.j
        if ctx.h >= 12:
            L = drip_len(col, 13, 0.45, 5)            # drips <= 6 texels up from the wrist
            return 1 if from_bottom < L else 0
        if ctx.cube.origin[1] > 15:                   # wrist knob: lower half crusted
            return 1 if ctx.t > 0.45 + hash3(col, 1, 0, 14) * 0.3 else 0
    return 0


def dried(v):
    return sub(BLOOD, 1, 3, v)


# ------------------------------------------------------------------ hide (skin) materials
EXTREMITY = {'_arm': (0.0, 0.1), '_forearm': (0.12, 0.55), '_hand': (0.55, 0.75), '_leg': (0.0, 0.05),
             '_shin': (0.05, 0.4), '_foot': (0.4, 0.65)}

# hand-placed creases: bone suffix -> rows (local y; negative = measured up from the segment end)
CREASES = {'_arm': (-7, -4), '_leg': (-8, -5), '_shin': (-6,), '_forearm': (-6,)}
BODY_CREASES = (-19, -16, -13)


def frost(ctx):
    """0..1: frostbitten / necrotic darkening toward the hands and feet (along the bone axis)."""
    n = ctx.bone.name
    if '_finger' in n:
        return 1.0
    for suf, (a, b) in EXTREMITY.items():
        if n.endswith(suf):
            ln = getattr(ctx.bone, 'flen', 20.0)
            t = max(0.0, min(1.0, local(ctx)[1] / ln))
            return a + (b - a) * t
    return 0.0


def crease(ctx, v):
    """Curved dark wrinkle lines with a lit lip under them (above elbows, knees, hocks, waist)."""
    if not is_side(ctx) or flat(ctx) or ctx.h < 6:
        return v
    n = ctx.bone.name
    if n == 'body':
        rows, ln = BODY_CREASES, 0.0
    else:
        rows = None
        for suf, rr in CREASES.items():
            if n.endswith(suf):
                rows = rr
        if rows is None:
            return v
        ln = getattr(ctx.bone, 'flen', 0.0)
    ly = math.floor(local(ctx)[1])
    col = wcol(ctx)
    for k, r in enumerate(rows):
        yc = (ln + r) if r < 0 and n != 'body' else r
        yc = math.floor(yc + 1.3 * math.sin(col * 0.42 + k * 2.3))
        if ly == yc and hash3(col, k, 0, 77) > 0.15:
            return v - 0.17
        if ly == yc + 1:
            v += 0.07
    return v


def hide_value(ctx, base=0.50):
    x, y, z = dpos(ctx)
    v = base + light(ctx, 1.0)
    if not flat(ctx) and edge(ctx) == 0:
        v -= 0.06
    n = fbm(x * 0.075 + 3, y * 0.075, z * 0.075, 2, 11)       # broad value groups, not static
    v += 0.06 if n > 0.6 else (-0.05 if n < 0.38 else 0.0)
    return v


def hide_mat(ctx):
    """Grey-brown leathery hide stretched over bone."""
    v = hide_value(ctx)
    name = ctx.bone.name
    side = is_side(ctx)
    if side and not flat(ctx):
        v -= ctx.t * 0.07                      # occlusion toward the far end of the segment
    v = crease(ctx, v)
    if ctx.face == 'front' and name.endswith(('_shin', '_forearm')) and ctx.w >= 5 and ctx.h >= 8:
        c0 = ctx.w // 2 - 1                    # tibia / ulna pressing through, off-centre
        if ctx.i == c0:
            v += 0.11
        elif ctx.i == c0 + 1:
            v -= 0.07
    if name.endswith('_leg') and ctx.cube.size[0] >= 9:
        v -= 0.05                              # thighs one step darker: continuous leg gradient
    fr = frost(ctx)
    c = pick(SKIN, v) if fr <= 0 else mix(pick(SKIN, v), pick(FROST, v + 0.05), fr)
    if name.endswith(('_arm', '_forearm', '_shin')) and side and ctx.h >= 12 and ctx.face in ('front', 'east', 'west'):
        seed = int(hash3(ctx.cube.size[1], ctx.w, ord(ctx.face[0]), 9) * 100)
        vc = int(ctx.w * 0.3 + 1.4 * math.sin(ctx.j * 0.33 + seed))
        if ctx.i == vc and 0.12 < ctx.t < 0.8 and hash3(seed, 0, 0, 1) > 0.4:
            c = mix(c, VEIN, 0.5)
    b = blood_here(ctx)
    if b == 1:
        c = dried(v * 0.9)
    elif b == 2:
        c = BLOOD[0]
    return c


def knob_mat(ctx, boost=0.0):
    """Skin pulled tight over bony knobs (knees, elbows, hip points): pale, polished tops."""
    v = hide_value(ctx, 0.55 + boost)
    if ctx.face == 'top' or (is_side(ctx) and ctx.j == 0):
        v += 0.08
    if ctx.bone.name.endswith('_shin') and ctx.cube.origin[1] < 0:
        v += 0.08                              # kneecap catches light (no black "socks")
    fr = frost(ctx) * 0.8
    c = pick(SKIN, v) if fr <= 0 else mix(pick(SKIN, v), pick(FROST, v + 0.05), fr)
    b = blood_here(ctx)
    if b:
        c = dried(0.5) if b == 1 else BLOOD[0]
    return c


def vert_mat(ctx):
    """Spinous process: bone-tinted knob."""
    v = hide_value(ctx, 0.6)
    if ctx.face == 'top' or (is_side(ctx) and ctx.j == 0):
        v += 0.1
    return mix(pick(SKIN, v), pick(BONE, v - 0.05), 0.45)


def gap_mat(ctx):
    """Deep shadow inside the ribcage (bottom = belly hide)."""
    if ctx.face == 'bottom':
        return hide_mat(ctx)
    p = dpos(ctx)
    v = 0.4 + light(ctx, 0.4) + bands(fbm(p[0] * 0.3, p[1] * 0.3, p[2] * 0.3, 2, 3), 0.4, 0.6, 0.2)
    return pick(GAP, v)


def rib_mat(ctx):
    """A rib: hide shrink-wrapped over bone: tight pale top row, shadowed underside."""
    x, y, z = dpos(ctx)
    if ctx.face == 'bottom':
        return SKIN[1]
    if ctx.face == 'top':
        return pick(BONE, 0.68 + light(ctx, 0.4) + bands(hash3(x, y, z, 7), 0.3, 0.7, 0.05))
    if ctx.j == 0:
        c = sub(BONE, 5, 6, 0.5 + bands(hash3(x // 2, y, z // 2, 8), 0.4, 0.6, 0.5))
    else:
        c = pick(SKIN, 0.52 + light(ctx, 0.8) - (0.1 if ctx.j == ctx.h - 1 else 0))
    # blood from the mouth has run down the centre of the chest
    if ctx.face == 'front' and abs(x) < 6:
        L = drip_len(math.floor(x), 401, 0.35, 4)
        if L > 0 and hash3(math.floor(x), math.floor(y), 0, 402) > 0.3:
            c = sub(FRESH, 1, 4, 0.35 + ctx.j * 0.2)
    return c


def sternum_mat(ctx):
    x, y, z = dpos(ctx)
    v = 0.6 + light(ctx, 0.9)
    if is_side(ctx) and edge(ctx) == 0:
        v -= 0.08
    c = mix(pick(SKIN, v), pick(BONE, v - 0.08), 0.5)
    if ctx.face == 'front' and hash3(math.floor(x), 0, 0, 403) > 0.25:
        c = sub(FRESH, 1, 4, 0.55 - ctx.t * 0.4)       # bright fresh blood down the breastbone
    return c


def back_mat(ctx):
    """Back: hide with the ribs showing through as curved ridges, the spine groove, shadows under knobs."""
    c = hide_mat(ctx)
    x, y, z = dpos(ctx)
    ax = abs(x)
    if ctx.face == 'back':
        if ax < 1.2:
            return scale(c, 0.6)
        if ax < 2.2:
            return scale(c, 1.12)
        for vy in VERT_Y:
            if ax < 2.6 and 0 <= y - vy < 1:
                return scale(c, 0.55)
    if ctx.face in ('back', 'east', 'west') and ax > 3.5:
        # ribs: 2-texel lit ridge + 1-texel groove, sloping down and outward from the spine
        r = (y + 0.38 * ax + 0.25 * max(0.0, z - 2)) % 4.0
        if r < 1.0:
            return scale(c, 0.62)
        if r < 2.0:
            return scale(c, 1.16)
        if r < 3.0:
            return scale(c, 1.05)
    return c


def neck_mat(ctx):
    """Neck: hide with cords of tendon on the sides."""
    c = hide_mat(ctx)
    if ctx.face in ('west', 'east') and ctx.i % 3 == 1:
        return scale(c, 0.8)
    return c


# ------------------------------------------------------------------ bone materials
def bone_value(ctx, p, base=0.62):
    x, y, z = p
    v = base + light(ctx, 1.0)
    if not flat(ctx) and edge(ctx) == 0:
        v -= 0.09
    v += bands(fbm(x * 0.13, y * 0.13, z * 0.13, 2, 21), 0.36, 0.66, 0.05)
    return v


def skull_mat(ctx):
    p = dpos(ctx)
    x, y, z = p
    v = bone_value(ctx, p)
    if ctx.face == 'bottom':
        v -= 0.15
    if is_side(ctx):
        v -= ctx.t * 0.06                        # occlusion toward the jaw line
    c = pick(BONE, v)
    if hash3(x, y, z, 23) > 0.975:
        c = pick(BONE, v - 0.28)                 # pits
    st = fbm(x * 0.17, y * 0.17, z * 0.17, 2, 24)
    if st > 0.68:
        c = mix(c, hx('#4b3122'), 0.3)           # tannin stains
    return c


def palate_mat(ctx):
    """Snout: bone outside, raw gums + fresh blood on the underside (seen when the jaw drops)."""
    if ctx.face == 'bottom':
        p = dpos(ctx)
        if ctx.i in (0, ctx.w - 1):
            return sub(FRESH, 0, 2, 0.5)
        return pick(FLESH, 0.4 + bands(fbm(p[0] * 0.4, 0, p[2] * 0.4, 2, 51), 0.4, 0.6, 0.15))
    c = skull_mat(ctx)
    if is_side(ctx) and ctx.j >= ctx.h - 3:
        p = dpos(ctx)
        L = drip_len(math.floor(p[2] if ctx.face in ('west', 'east') else p[0]), 57, 0.4, 2)
        if L > 0 and ctx.h - 1 - ctx.j < L:
            c = sub(FRESH, 1, 3, 0.5)            # lips of blood along the tooth row
    return c


def tip_mat(ctx):
    """Premaxilla: plain bone with a single centre seam."""
    c = palate_mat(ctx)
    if ctx.face in ('front', 'top') and ctx.i == ctx.w // 2:
        return BONE[2]
    return c


def jaw_mat(ctx):
    """Mandible ramus: bone, 1-texel gum strip on top, fresh blood toward the chin."""
    p = dpos(ctx)
    if ctx.face == 'top':
        return sub(FLESH, 2, 4, 0.5 + bands(hash3(p[0], 0, p[2], 53), 0.3, 0.7, 0.4))
    c = skull_mat(ctx)
    if is_side(ctx) and ctx.j == 0:
        c = sub(FRESH, 1, 3, 0.5)
    elif is_side(ctx):
        col = math.floor(p[2]) if ctx.face in ('west', 'east') else math.floor(p[0]) + 40
        L = drip_len(col, 59, 0.45, 3)
        if L > 0 and ctx.j < L + 1:
            c = sub(FRESH, 1, 4, 0.6 - ctx.j * 0.15)
    return c


def chin_mat(ctx):
    p = dpos(ctx)
    if ctx.face == 'top':
        return sub(FLESH, 2, 4, 0.5)
    c = skull_mat(ctx)
    col = wcol(ctx)
    if is_side(ctx) and (ctx.j <= 1 or hash3(col, 0, 0, 61) > 0.45):
        c = sub(FRESH, 1, 4, 0.7 - ctx.t * 0.5)   # chin soaked in fresh blood
    return c


def tongue_mat(ctx):
    lx, ly, lz = local(ctx)
    t = (lz - ctx.cube.origin[2]) / max(1, ctx.cube.size[2])   # 0 = tip (front)
    v = 0.25 + t * 0.55 + light(ctx, 0.5)
    if ctx.face == 'top' and ctx.i == ctx.w // 2:
        v -= 0.15
    return sub(FLESH, 2, 4, v) if t > 0.2 else sub(FLESH, 1, 2, v)


def gullet_mat(ctx):
    if ctx.face == 'front':
        return VOID
    return pick(GAP, 0.15 + light(ctx, 0.3))


def antler_mat(ctx):
    p = dpos(ctx)
    x, y, z = p
    n = ctx.bone.name
    base = {'a': 0.40, 'b': 0.50, 'c': 0.60}.get(n[-1], 0.55) if 'antler' in n else 0.52
    if 'tine' in n:
        base = 0.50 + (1 - ctx.t) * 0.12 if is_side(ctx) else 0.6
    v = base + light(ctx, 1.1)
    if not flat(ctx) and edge(ctx) == 0:
        v -= 0.09
    if is_side(ctx) and ctx.w >= 2 and hash3(ctx.i, ctx.cube.size[1], ctx.cube.size[0], 61) > 0.62:
        v -= 0.1                                  # longitudinal grooves
    v += bands(vnoise(x * 0.5, y * 0.5, z * 0.5, 62), 0.35, 0.65, 0.05)
    return pick(ANTLER, v)


def antler_tip_mat(ctx):
    """Polished tine points: 2 ramp steps lighter (survive the night shot)."""
    v = 0.5 + light(ctx, 0.8) + (0.3 if (is_side(ctx) and ctx.j == 0) or ctx.face == 'top' else 0)
    return sub(ANTLER, 6, 8, v)


def burr_mat(ctx):
    p = dpos(ctx)
    v = 0.36 + light(ctx, 1.0) + bands(hash3(p[0], p[1], p[2], 63), 0.35, 0.65, 0.1)
    return pick(ANTLER, v)


def broken_mat(ctx):
    """Antler snapped off: pale splintered core, jagged rim."""
    if ctx.face == 'top':
        e = edge(ctx)
        if e >= 1:
            return BONE[7] if hash3(ctx.i, ctx.j, 0, 64) > 0.3 else BONE[5]
        return BONE[4] if hash3(ctx.i, ctx.j, 1, 64) > 0.4 else None
    if is_side(ctx) and ctx.j == 0:
        return BONE[6] if hash3(ctx.i, 0, ord(ctx.face[0]), 65) > 0.45 else None
    return antler_mat(ctx)


def splinter_mat(ctx):
    """A snapped rib punching out through the hide: blood ring at the root, pale splintered tip."""
    p = dpos(ctx)
    lx = local(ctx)[0]
    v = bone_value(ctx, p, 0.64)
    if lx < 1.5:
        return sub(FRESH, 1, 3, 0.5 + light(ctx, 0.5))
    if lx < 2.5:
        return dried(0.5)
    if ctx.face == 'east':
        return BONE[8]
    return pick(BONE, v)


def claw_mat(ctx):
    v = 0.40 + light(ctx, 1.2)
    if is_side(ctx):
        v -= ctx.t * 0.1
    c = pick(CLAW, v)
    if ctx.face in ('front', 'top') and is_side(ctx) and ctx.i == 0:
        c = CLAW_HI                                 # glossy outer curve
    elif ctx.face == 'top':
        c = CLAW_HI
    if ctx.cube.size[1] >= 5 and ctx.cube.size[0] >= 2 and is_side(ctx) and ctx.t < 0.35:
        c = dried(0.5)                              # blood caked at the claw roots
    return c


def hoof_mat(ctx):
    p = dpos(ctx)
    v = 0.38 + light(ctx, 1.1) + bands(hash3(p[0], p[1] // 2, p[2], 72), 0.3, 0.7, 0.06)
    if is_side(ctx) and ctx.j == 0:
        v += 0.2
    if ctx.face == 'bottom':
        return pick(CLAW, 0.1)
    return pick(CLAW, v)


# ------------------------------------------------------------------ fur / flaps / strands
def fur_value(ctx, col, rowpos):
    strand = hash3(col // 2, ctx.cube.size[1], 0, 81)
    v = 0.30 + strand * 0.32 + light(ctx, 0.9)
    if col % 3 == 0:
        v -= 0.12
    v += rowpos * 0.12
    return v


def fur_shell(depth=4.0, seed=90, holes=0.0):
    """Matted fur shell: strands hang toward local +y with a ragged hem; optional bald holes."""
    def f(ctx):
        c = ctx.cube
        lx, ly, lz = local(ctx)
        if ctx.face == 'bottom':
            return None
        span = c.size[1]
        pos = (ly - c.origin[1]) / span
        col = math.floor(lx) if ctx.face in ('front', 'back') else math.floor(lz) + 50
        if ctx.face == 'top':
            pos, col = 0.0, ctx.i
        lim = 1.0 - (depth * (0.2 + hash3(col, 0, 0, seed) * 0.8)) / span
        if pos > lim:
            return None
        p = dpos(ctx)
        if holes and fbm(p[0] * 0.3, p[1] * 0.3, p[2] * 0.3, 2, seed + 1) < holes:
            return None
        return pick(FUR, fur_value(ctx, col, max(0.0, pos - lim + 0.25) * 2))
    return f


def clump_mat(seed, ragged=0.65):
    """A matted tuft of fur: solid on top, strands of random length hanging toward local +y."""
    def f(ctx):
        if ctx.face == 'bottom':
            return None
        c = ctx.cube
        lx, ly, lz = local(ctx)
        depth = (ly - c.origin[1]) / c.size[1]
        if ctx.face == 'top':
            col, depth = ctx.i + 40, 0.0
        else:
            col = math.floor(lx) if ctx.face in ('front', 'back') else math.floor(lz) + 20
        lim = 1.0 - ragged * hash3(col, 0, 0, seed)
        if depth > lim:
            return None
        v = 0.30 + hash3(col // 2, 1, 0, seed) * 0.3 + depth * 0.25 + light(ctx, 0.9)
        if col % 3 == 0:
            v -= 0.12
        if depth > lim - 0.12:
            v += 0.1
        return pick(FUR, v)
    return f


def string_mat(seed, kind='drool'):
    """Strings of bloody drool / sinew (zero-thickness, ragged, mostly transparent)."""
    def f(ctx):
        lx, ly, lz = local(ctx)
        c = ctx.cube
        col = math.floor(lz if c.size[0] == 0 else lx)
        h = hash3(col, 0, 0, seed)
        if h < 0.4 or col % 2:
            return None
        depth = ly - c.origin[1]
        if depth > c.size[1] * (0.35 + 0.65 * (h - 0.4) / 0.6):
            return None
        if kind == 'sinew':
            return sub(FLESH, 2, 5, 0.6 - depth / c.size[1] * 0.4)
        return sub(FRESH, 0, 3, 0.75 - depth / c.size[1] * 0.5)
    return f


def crest_mat(seed):
    """Sparse matted fur crest standing off the spine (zero-thickness plane, ragged free edge +z)."""
    def f(ctx):
        lx, ly, lz = local(ctx)
        c = ctx.cube
        depth = lz - c.origin[2]
        col = math.floor(ly)
        if col % 3 == 2 or hash3(col, 2, 0, seed) < 0.3:
            return None                               # sparse: the vertebrae read through
        lim = c.size[2] * (0.25 + 0.75 * hash3(col, 0, 0, seed))
        if depth > lim:
            return None
        v = 0.36 + hash3(col // 2, 0, 0, seed + 1) * 0.3 + depth / c.size[2] * 0.2 + light(ctx, 0.5)
        return pick(FUR, v)
    return f


def flap_mat(seed=97, kind='skin'):
    """Hanging torn hide (zero-thickness plane): ragged hem, raw red edge, dark creases."""
    def f(ctx):
        lx, ly, lz = local(ctx)
        c = ctx.cube
        depth = ly - c.origin[1]
        col = math.floor(lz) if c.size[0] == 0 else math.floor(lx)
        h = hash3(col, 0, 0, seed)
        lim = c.size[1] * (0.45 + 0.55 * h)
        if depth > lim or (hash3(col, 1, 0, seed) < 0.12 and depth > 2):
            return None
        v = 0.46 + light(ctx, 0.5) - depth / c.size[1] * 0.18
        if kind == 'velvet':
            return pick(FUR, v + 0.12 + (col % 2) * 0.08)
        if depth > lim - 1.6:
            return sub(FLESH, 2, 5, v + 0.1)          # raw torn hem
        if (col + int(depth * 0.5)) % 4 == 0:
            v -= 0.12
        return pick(SKIN, v)
    return f


def teeth_mat(root_y, maxlen, axis, seed, canines=(), grow=1):
    """Jagged teeth on a zero-thickness plane; gum line at local y=root_y, teeth grow along
    +y (upper teeth, grow=1) or -y (lower teeth, grow=-1)."""
    def f(ctx):
        lx, ly, lz = local(ctx)
        col = math.floor(lx if axis == 'x' else lz)
        h = hash3(col, 0, 0, seed)
        if col in canines:
            L = maxlen
        elif h < 0.22:
            L = 0.8                                   # missing tooth
        else:
            L = 1.4 + ((h - 0.22) / 0.78) ** 1.4 * (maxlen - 2.2)
        depth = (ly - root_y) * grow
        if depth < 0 or depth > L:
            return None
        if depth < 1.0:
            return sub(FRESH, 0, 2, h)                # bleeding gum line
        t = depth / max(1.0, L)
        v = 0.95 - t * 0.28 + light(ctx, 0.3)
        if hash3(col, 3, 0, seed) > 0.75 and depth < 1.0 + hash3(col, 4, 0, seed) * L * 0.6:
            return sub(FRESH, 1, 3, 0.4 + t * 0.3)   # blood caked from the roots down
        if hash3(col, 5, 0, seed) > 0.8:
            v -= 0.22                                 # rotten, yellowed tooth
        return pick(BONE, v)
    return f


def brow_mat(ctx):
    """Brow ridge: BONE[7] highlight on the top row, deep shadow underneath."""
    if ctx.face == 'top':
        return BONE[7]
    if ctx.face == 'bottom':
        return BONE[1]
    if ctx.j == 0:
        return BONE[7]
    if ctx.j == ctx.h - 1:
        return BONE[3]
    return skull_mat(ctx)


def cheek_mat(ctx):
    """Zygomatic arch under each orbit: lit top lip, BONE[3] shading below."""
    if ctx.face == 'top':
        return BONE[6]
    if is_side(ctx):
        return BONE[6] if ctx.j == 0 else (BONE[3] if ctx.j >= ctx.h - 1 else BONE[4])
    return BONE[2]


# ------------------------------------------------------------------ pixel-art decals
K = VOID
SOCK_PAL = {'K': K, '1': BONE[1], '2': BONE[2], '3': BONE[3], '4': BONE[4], '7': BONE[7], 'r': BLOOD[2]}
WH = hx('#f6f8ff')
GLOW_O = hx('#8fa8d8')
GLOW_D = hx('#34446a')

# right eye socket (viewer's left) on the 22-wide cranium front; '.' untouched.
SOCKET_R = [
    "32........",
    "1K32......",
    "KKKK32....",
    "KKKKKKK32.",
    "KKKKKKKKK2",
    "KKKKKKKKK2",
    "1KKKKKKKK2",
    "21KKKKKK2.",
    "321KKKK21.",
    ".3221112..",
    "..r3333...",
    "..r.......",
]
SOCK_DY = 2
PUPIL_R = (3, 6)   # top-left texel of the 2x2 pupil core (face texels)


def pupil_cols(w):
    pi, _ = PUPIL_R
    return (pi, w - 2 - pi)


def socket_decal(img, u0, v0, w, h):
    """Cranium front: deep slanted sockets, pupils, a crack from the left orbit to the crown,
    nasal sutures around the snout root, cheek shading."""
    pixelart(SOCKET_R, SOCK_PAL, anchor='topleft', dx=0, dy=SOCK_DY)(img, u0, v0, w, h)
    pixelart(SOCKET_R, SOCK_PAL, anchor='topleft', dx=w - 10, dy=SOCK_DY, flip=True)(img, u0, v0, w, h)
    px = img.load()
    _, pj = PUPIL_R
    for pi in pupil_cols(w):
        for di in (0, 1):
            for dj in (0, 1):
                px[u0 + pi + di, v0 + pj + dj] = WH
    # crack from the left orbit (viewer's right) up to the crown
    for i, j in ((14, 3), (14, 2), (13, 1), (13, 0)):
        px[u0 + i, v0 + j] = BONE[1]
    for i, j in ((15, 2), (12, 1)):
        px[u0 + i, v0 + j] = BONE[3]
    # nasal sutures framing the snout root + frontal suture
    for j in range(9, h):
        px[u0 + 6, v0 + j] = BONE[2]
        px[u0 + w - 7, v0 + j] = BONE[2]
    for j in range(0, 6):
        if j % 3 != 2:
            px[u0 + w // 2, v0 + j] = BONE[3]


def eyes_decal(img, u0, v0, w, h):
    """Emissive layer: 2x2 white core, cold blue orthogonal halo, dim diagonals."""
    px = img.load()
    _, pj = PUPIL_R
    for pi in pupil_cols(w):
        for di in (0, 1):
            for dj in (0, 1):
                px[u0 + pi + di, v0 + pj + dj] = WH
        for di, dj in ((0, -1), (1, -1), (0, 2), (1, 2), (-1, 0), (-1, 1), (2, 0), (2, 1)):
            px[u0 + pi + di, v0 + pj + dj] = GLOW_O
        for di, dj in ((-1, -1), (2, -1), (-1, 2), (2, 2)):
            px[u0 + pi + di, v0 + pj + dj] = GLOW_D


SIDE_SOCK = [
    "....32",
    "...21K",
    "..21KK",
    ".21KKK",
    "21KKKK",
    "1KKKKK",
    "1KKKKK",
    "21KKKK",
    ".21KKK",
    "..2111",
    "...33.",
]


def side_socket_decal(right):
    """Orbit wrapping around the corner of the cranium onto the side face."""
    def fn(img, u0, v0, w, h):
        if right:   # west face: front edge at high i
            pixelart(SIDE_SOCK, SOCK_PAL, anchor='topleft', dx=w - 6, dy=SOCK_DY)(img, u0, v0, w, h)
        else:
            pixelart(SIDE_SOCK, SOCK_PAL, anchor='topleft', dx=0, dy=SOCK_DY, flip=True)(img, u0, v0, w, h)
    return fn


def side_glint(right):
    def fn(img, u0, v0, w, h):
        px = img.load()
        i = w - 1 if right else 0
        px[u0 + i, v0 + PUPIL_R[1] + 1] = hx('#9fb4e0')
    return fn


def cap_top_decal(img, u0, v0, w, h):
    """Crack continuing over the crown (top face: high j = front)."""
    px = img.load()
    path = [(12, h - 1), (12, h - 2), (11, h - 3), (11, h - 4), (10, h - 5), (10, h - 6), (9, h - 7),
            (9, h - 8), (8, h - 9), (8, h - 10)]
    for i, j in path:
        if 0 <= i < w and 0 <= j < h:
            px[u0 + i, v0 + j] = BONE[1]
    for i, j in ((13, h - 4), (14, h - 5), (7, h - 9), (12, h - 6)):
        px[u0 + i, v0 + j] = BONE[3]


def cap_front_decal(img, u0, v0, w, h):
    px = img.load()
    px[u0 + 12, v0 + 0] = BONE[1]
    px[u0 + 12, v0 + 1] = BONE[1]


def nasal_top_decal(img, u0, v0, w, h):
    """Top of the mid snout: the nasal aperture opening toward the front (high j)."""
    rows = [
        "..2..",
        ".212.",
        ".1K1.",
        "21K12",
        "1KKK1",
        "1K1K1",
    ]
    pixelart(rows, SOCK_PAL, anchor='bottom')(img, u0, v0, w, h)


def ridge_decal(img, u0, v0, w, h):
    px = img.load()
    for j in range(h):
        if j % 6 != 5:
            px[u0 + w // 2, v0 + j] = BONE[3]


def gash_decal(img, u0, v0, w, h):
    """6x2 gash on the thigh: GAP core, FLESH rim, 1px FLESH[6] highlight."""
    rows = [
        "..ffff..",
        ".fGGGGf.",
        "fGGGGGGf",
        ".fhffff.",
    ]
    p = {'f': FLESH[3], 'G': GAP[0], 'h': FLESH[6]}
    pixelart(rows, p, anchor='topleft', dx=1, dy=3)(img, u0, v0, w, h)


def bite_decal(img, u0, v0, w, h):
    """Bite on the neck: ring of punctures around raw flesh."""
    rows = [
        ".K.K.K.",
        "KfffffK",
        ".fFFFf.",
        "KfFGFfK",
        ".fFFFf.",
        "KfffffK",
        ".K.K.K.",
    ]
    p = {'K': GAP[0], 'f': FLESH[2], 'F': FLESH[4], 'G': GAP[1]}
    pixelart(rows, p, anchor='center', dy=-2)(img, u0, v0, w, h)


def tear_decal(img, u0, v0, w, h):
    """Left flank: torn hide around the splintered rib's exit wound."""
    rows = [
        "..fff...",
        ".fFFFf..",
        "fFGGGFf.",
        "fGGGGGFf",
        "fFGGGFf.",
        ".fFFf...",
        "..r.r...",
        "..r.....",
    ]
    p = {'f': FLESH[2], 'F': FLESH[4], 'G': GAP[0], 'r': BLOOD[3]}
    pixelart(rows, p, anchor='topleft', dx=2, dy=6)(img, u0, v0, w, h)


# ------------------------------------------------------------------ build
def build():
    r = Rig()
    VERT_Y.clear()

    def bone(name, pivot, parent=None, rot=(0, 0, 0), mat=None, flen=None):
        b = r.bone(name, pivot, parent, rot, mat)
        b.abs = r.abs_pivot[name]
        if flen:
            b.flen = flen
        return b

    def at(parent, dx, dy, dz):
        a = r.abs_pivot[parent]
        return (a[0] + dx, a[1] + dy, a[2] + dz)

    def box(b, frm, size, mat=None, inflate=0.0, decals=None, ref=None):
        """frm relative to the pivot of `ref` (default: the bone itself), unrotated frame."""
        a = r.abs_pivot[ref or b]
        return r.box(b, (a[0] + frm[0], a[1] + frm[1], a[2] + frm[2]), size, mat=mat, inflate=inflate, decals=decals)

    def mx(sx, frm, size):
        """Mirror a right-side (-X) box description to side sx (+1 = left)."""
        return frm if sx < 0 else (-(frm[0] + size[0]), frm[1], frm[2])

    def mbox(b, sx, frm, size, **kw):
        return box(b, mx(sx, frm, size), size, **kw)

    def seg(p, q):
        dy, dz = q[0] - p[0], q[1] - p[1]
        return math.hypot(dy, dz), math.degrees(math.atan2(dz, dy))

    # ---------------- legs (digitigrade): joint targets in world (y, z); asymmetric stance
    LEGS = {
        'right': ((-38.0, 5.0), (-15.0, -9.0), (4.0, 5.0), (19.0, -1.0)),
        'left': ((-38.0, 5.0), (-13.0, -4.0), (6.0, 11.0), (19.0, 6.0)),
    }
    for side, sx in (('right', -1), ('left', 1)):
        hip, knee, hock, fet = LEGS[side]
        L1, a1 = seg(hip, knee)
        L2, a2 = seg(knee, hock)
        L3, a3 = seg(hock, fet)
        leg = bone(f'{side}_leg', (6.0 * sx, hip[0], hip[1]), rot=(a1, 0, -3 * sx), mat=hide_mat, flen=L1)
        mbox(leg.name, sx, (-4.5, -5, -5), (9, 14, 10), decals={'front': gash_decal} if sx < 0 else None)
        mbox(leg.name, sx, (-3.5, 9, -3.5), (7, int(L1) - 9, 7))
        mbox(leg.name, sx, (-7.5, -3, -2), (3, 5, 4), mat=lambda c: knob_mat(c, 0.04))   # trochanter
        mbox(leg.name, sx, (-7, -6, -4.5), (4, 13, 9), mat=clump_mat(301 + sx))
        shin = bone(f'{side}_shin', at(leg.name, 0, L1, 0), leg.name, rot=(a2 - a1, 0, 0), mat=hide_mat, flen=L2)
        box(shin.name, (-3.5, -3.5, -5), (7, 7, 7), mat=lambda c: knob_mat(c, 0.08))     # kneecap
        box(shin.name, (-3, 1, -3), (6, 9, 6))
        box(shin.name, (-2.5, 9, -2.5), (5, int(L2) - 12, 5))
        box(shin.name, (-3, L2 - 4.5, -3), (6, 6, 6), mat=knob_mat)                        # hock
        foot = bone(f'{side}_foot', at(shin.name, 0, L2, 0), shin.name, rot=(a3 - a2, 0, 0), mat=hide_mat, flen=L3)
        box(foot.name, (-2.5, 0, -2.5), (5, int(L3) - 2, 5))
        box(foot.name, (-3, L3 - 4, -3), (6, 5, 6), mat=knob_mat)                          # fetlock
        hoof = bone(f'{side}_hoof', at(foot.name, 0, L3, 0), foot.name, rot=(-a3, 0, 0), mat=hoof_mat)
        box(hoof.name, (-3.4, 0.5, -6.5), (3, 4, 8))
        box(hoof.name, (0.4, 0.5, -6.5), (3, 4, 8))
        box(hoof.name, (-1.5, -2, 1.5), (3, 2, 2))
    hip = LEGS['right'][0]

    # ---------------- body: pelvis + sunken abdomen
    BODY = 18
    bone('body', (0, hip[0], hip[1]), rot=(BODY, 0, 0), mat=hide_mat)
    box('body', (-8, -6, -5), (16, 9, 11))
    for sx in (-1, 1):
        mbox('body', sx, (-10, -9, -4), (4, 5, 7), mat=knob_mat)        # iliac crests
    box('body', (-2, -6, 5), (4, 6, 3), mat=knob_mat)
    box('body', (-7, -8, 5.5), (14, 9, 3), mat=clump_mat(321))
    box('body', (-6, -21, -3), (12, 16, 8))                              # sunken belly / waist
    for k, yy in enumerate((-20, -14, -8)):
        box('body', (-2, yy, 4.5), (4, 3, 3 + (k % 2) * 2), mat=vert_mat)
        VERT_Y.append(r.abs_pivot['body'][1] + yy + 3)
    bone('tail', at('body', 0, 0, 7), 'body', rot=(40, 0, 0), mat=fur_shell(6, seed=131))
    box('tail', (-2.5, -1, -1), (5, 10, 2))

    # ---------------- chest: ribcage, stepped back, vulture hump, spine, scapulae
    CH = 24
    NET = BODY + CH
    bone('chest', at('body', 0, -17, 0), 'body', rot=(CH, 0, 0), mat=hide_mat)
    box('chest', (-9.5, -29, -8), (19, 28, 9), mat=gap_mat,
        decals={'east': tear_decal})
    box('chest', (-10.5, -32, 1), (21, 12, 7), mat=back_mat)
    box('chest', (-9, -20, 1), (18, 10, 6), mat=back_mat)
    box('chest', (-7, -10, 1), (14, 10, 5), mat=back_mat)
    box('chest', (-12.5, -35, -6), (25, 6, 13))                          # withers / shoulder girdle
    box('chest', (-10, -31.5, -9), (20, 2, 3), mat=knob_mat)             # clavicles
    box('chest', (-1.5, -29, -10.5), (3, 16, 2), mat=sternum_mat)
    box('chest', (-9, -41, -4), (18, 7, 13))                             # trapezius hump
    box('chest', (-9, -41, -4), (18, 7, 13), mat=fur_shell(8, seed=141, holes=0.3), inflate=1.0)
    for k, (yy, d) in enumerate(zip((-40, -34, -28, -22, -16, -10), (9, 6, 8, 5, 7, 4))):
        zb = 7 if yy < -33 else (6 if yy < -18 else 5)
        box('chest', (-2, yy, zb), (4, 3, d), mat=vert_mat)
        VERT_Y.append(r.abs_pivot['chest'][1] + yy + 3)
    box('chest', (0, -43, 9), (0, 30, 8), mat=crest_mat(145))
    # ribs: one rolled bone per side so every rib slopes down toward the sternum (chevrons)
    RIBS = [(-28, 10.0), (-24, 11.0), (-20, 12.0), (-17, 12.0), (-14, 11.5), (-11, 10.5)]
    for side, sx in (('right', -1), ('left', 1)):
        rb = bone(f'{side}_ribs', at('chest', 0, -19, -9.5), 'chest', rot=(10, 0, -22 * sx), mat=rib_mat)
        for k, (yy, hw) in enumerate(RIBS):
            inner = 1.5 + max(0.0, (-19 - yy)) * 0.45        # upper ribs start further out (no crossing)
            if side == 'left' and k == 3:
                mbox(rb.name, sx, (-7.5, yy, -9.5), (6, 2, 11), ref='chest')    # broken rib stub
                continue
            wdt = round(hw - inner)
            mbox(rb.name, sx, (-(inner + wdt), yy, -9.5), (wdt, 2, 11), ref='chest')
    sp = bone('rib_splinter', at('chest', 9.5, -16, -6), 'chest', rot=(0, 25, -8), mat=splinter_mat)
    box(sp.name, (0, -1, -1), (8, 2, 2))
    box(sp.name, (8, -0.5, -0.5), (3, 1, 1))
    box('chest', (9.7, -16, -9), (0, 7, 6), mat=flap_mat(189))
    for side, sx in (('right', -1), ('left', 1)):
        sc = bone(f'{side}_scapula', at('chest', 11 * sx, -33, 8), 'chest', rot=(14, -20 * sx, -6 * sx), mat=knob_mat)
        mbox(sc.name, sx, (0, 0, -1.5), (9, 4, 2))
        mbox(sc.name, sx, (1.5, 4, -1.5), (6, 5, 2))
        mbox(sc.name, sx, (3, 9, -1.5), (3, 5, 2))
        mbox(sc.name, sx, (1.5, 9, -1.6), (6, 1, 0), mat=lambda c: GAP[1])

    # ---------------- neck + skull
    NK = 64
    bone('neck', at('chest', 0, -33, -4), 'chest', rot=(NK, 0, 0), mat=neck_mat)
    box('neck', (-4, -16, -4.5), (8, 17, 9), decals={'west': bite_decal})
    for yy in (-14, -8):
        box('neck', (-1.5, yy, 4), (3, 3, 4), mat=vert_mat)
    box('neck', (0, -18, 4.5), (0, 19, 7), mat=crest_mat(155))
    box('neck', (-4, -16, -4.5), (8, 17, 9), mat=fur_shell(7, seed=151, holes=0.28), inflate=0.9)
    HP = 22
    bone('skull_mount', at('neck', 0, -15, 0), 'neck', rot=(-(NET + NK), 0, 0))
    bone('head', at('skull_mount', 0, 0, 0), 'skull_mount', rot=(HP, 0, 6), mat=skull_mat)
    box('head', (-11, -16, -15), (22, 16, 15), decals={
        'front': socket_decal, 'eyes:front': eyes_decal,
        'west': side_socket_decal(True), 'east': side_socket_decal(False),
        'eyes:west': side_glint(True), 'eyes:east': side_glint(False)})
    box('head', (-10, -18, -14), (20, 2, 13), decals={'top': cap_top_decal, 'front': cap_front_decal})
    for sx in (-1, 1):
        mbox('head', sx, (-12, -14, -13), (1, 10, 11))                 # temporal bevel
        mbox('head', sx, (-12, -5, -15), (6, 3, 10), mat=cheek_mat)    # zygomatic arch under the orbit
    box('head', (-8, -14, 0), (16, 11, 2))                              # occiput
    box('head', (-3, 0, -24), (6, 7, 10), mat=gullet_mat)               # gullet: any gape shows black
    box('head', (-5, -14, 2.2), (10, 14, 0), mat=flap_mat(181))         # torn hide hanging from the nape
    box('head', (-9, -15, -2), (18, 10, 4), mat=fur_shell(6, seed=161, holes=0.35), inflate=0.6)
    for side, sx in (('right', -1), ('left', 1)):
        bone(f'{side}_brow', at('head', 1.0 * sx, -12.5, -15.5), 'head', rot=(0, 0, -14 * sx), mat=brow_mat)
        mbox(f'{side}_brow', sx, (-12, -1.5, -1.5), (11, 3, 3), ref=f'{side}_brow')

    # snout: drops away below the orbits so the muzzle never points at the camera
    bone('snout', at('head', 0, -3, -15), 'head', rot=(18, 0, 0), mat=palate_mat)
    box('snout', (-4, -3, -11), (8, 8, 11))
    box('snout', (-3, -2, -21), (6, 7, 10), decals={'top': nasal_top_decal})
    box('snout', (-1.5, 0, -24), (3, 5, 3), mat=tip_mat)
    box('snout', (-1.5, -4, -20), (3, 2, 20), mat=skull_mat, decals={'top': ridge_decal})
    for sx in (-1, 1):
        mbox('snout', sx, (-4.4, 4, -11), (0, 8, 11), mat=teeth_mat(4, 7.5, 'z', 203 + sx, canines=(-3,)))
        mbox('snout', sx, (-3.4, 4, -21), (0, 7, 10), mat=teeth_mat(4, 5.5, 'z', 207 + sx, canines=(-19,)))
    box('snout', (-1.5, 4, -23.6), (3, 4, 0), mat=teeth_mat(4, 3.5, 'x', 201))
    for sx in (-1, 1):
        mbox('head', sx, (-4.6, -1, -23), (0, 11, 7), mat=string_mat(191 + sx))   # drool at the corners

    # mandible: two rami converging into a chin (a V from the front and below)
    JR = 21
    bone('jaw', at('head', 0, -1, -13), 'head', rot=(JR, 0, 0), mat=jaw_mat)
    for sx in (-1, 1):
        mbox('jaw', sx, (-4.4, 3, -14), (2, 4, 14))                    # rear ramus
        mbox('jaw', sx, (-3.4, 3, -25), (2, 4, 11))                    # front ramus
        mbox('jaw', sx, (-4.6, -1, -4), (2, 7, 5), mat=skull_mat)       # ascending ramus to the hinge
        mbox('jaw', sx, (-2.3, -1, -24), (0, 4, 20), mat=teeth_mat(3, 4, 'z', 213 + sx, grow=-1))
    box('jaw', (-2.5, 3, -30), (5, 4, 6), mat=chin_mat)
    box('jaw', (-2.5, -2, -29.6), (5, 5, 0), mat=teeth_mat(3, 5, 'x', 211, canines=(-2, 1), grow=-1))
    box('jaw', (-1.5, 4, -24), (3, 2, 14), mat=tongue_mat)
    box('jaw', (0.5, 7, -24), (0, 9, 12), mat=flap_mat(185))           # strip of hide under the jaw

    # ---------------- antlers (asymmetric crown; the left one is snapped)
    def tine(name, parent, y, rot, L):
        bone(name, at(parent, 0, y, 0), parent, rot=rot, mat=antler_mat)
        box(name, (-1, -L, -1), (2, L, 2))
        box(name, (-0.5, -L - 3, -0.5), (1, 3, 1), mat=antler_tip_mat)

    ra = bone('right_antler', at('head', -7, -17, -7), 'head', rot=(-38, 0, -46), mat=antler_mat)
    box(ra.name, (-3.5, -2, -3.5), (7, 2, 7), mat=burr_mat)
    box(ra.name, (-2, -13, -2), (4, 12, 4))
    tine('right_tine0', ra.name, -4, (58, 0, 22), 6)                    # brow tine, forward
    rb = bone('right_antler_b', at(ra.name, 0, -12, 0), ra.name, rot=(-14, 0, -16), mat=antler_mat)
    box(rb.name, (-1.5, -11, -1.5), (3, 11, 3))
    tine('right_tine1', rb.name, -4, (46, 0, 14), 7)
    tine('right_tine2', rb.name, -9, (38, 0, 36), 5)
    rc = bone('right_antler_c', at(rb.name, 0, -10, 0), rb.name, rot=(6, 0, 30), mat=antler_mat)
    box(rc.name, (-1, -7, -1), (2, 7, 2))
    box(rc.name, (-0.5, -10, -0.5), (1, 3, 1), mat=antler_tip_mat)
    tine('right_tine3', rc.name, -4, (44, 0, -24), 4)

    la = bone('left_antler', at('head', 7, -17, -7), 'head', rot=(-36, 0, 42), mat=antler_mat)
    box(la.name, (-3.5, -2, -3.5), (7, 2, 7), mat=burr_mat)
    box(la.name, (-2, -13, -2), (4, 12, 4))
    tine('left_tine0', la.name, -4, (56, 0, -26), 7)
    tine('left_tine1', la.name, -10, (36, 0, -40), 6)
    lb = bone('left_antler_b', at(la.name, 0, -12, 0), la.name, rot=(-10, 0, 22), mat=antler_mat)
    box(lb.name, (-1.5, -5, -1.5), (3, 5, 3))
    box(lb.name, (-1.5, -7, -1.5), (3, 2, 3), mat=broken_mat)
    box(lb.name, (1.6, -4, -1), (0, 13, 2), mat=flap_mat(187, 'velvet'))

    # ---------------- arms: grotesquely long, knobby, 4 clawed fingers
    for side, sx in (('right', -1), ('left', 1)):
        sh = bone(f'{side}_shoulder', at('chest', 13 * sx, -32 if sx < 0 else -30, -2), 'chest', rot=(-NET, 0, 0))
        # big matted tufts live on the static mount so they keep hanging when the arm moves
        mbox(sh.name, sx, (-7.5, -7, -5), (5, 15, 10), mat=clump_mat(331 + sx))
        mbox(sh.name, sx, (-5, -8, -5), (10, 4, 9), mat=clump_mat(343 + sx, 0.3))
        mbox(sh.name, sx, (-4, -7, 3), (8, 11, 3), mat=clump_mat(335 + sx))
        fwd = -12 if sx < 0 else -6
        arm = bone(f'{side}_arm', at(sh.name, 0, 0, 0), sh.name, rot=(fwd, 0, (-11 if sx < 0 else -8) * sx), mat=hide_mat, flen=30)
        box(arm.name, (-4, -4, -4), (8, 8, 8), mat=knob_mat)
        box(arm.name, (-3.5, 3, -3.5), (7, 11, 7))
        box(arm.name, (-2.5, 13, -2.5), (5, 16, 5))
        mbox(arm.name, sx, (-5, 4, -1.5), (3, 8, 4), mat=clump_mat(339 + sx))
        fa = bone(f'{side}_forearm', at(arm.name, 0, 30, 0), arm.name, rot=(-18 if sx < 0 else -10, 0, 5 * sx), mat=hide_mat, flen=29)
        box(fa.name, (-3.5, -3, -1.5), (7, 6, 8), mat=lambda c: knob_mat(c, 0.04))      # elbow
        box(fa.name, (-3, 1, -3), (6, 11, 6))
        box(fa.name, (-2.5, 11, -2.5), (5, 15, 5))
        box(fa.name, (-3, 25, -3), (6, 4, 6), mat=knob_mat)                              # wrist
        hd = bone(f'{side}_hand', at(fa.name, 0, 29, 0), fa.name, rot=(8, -40 * sx, 4 * sx), mat=hide_mat, flen=10)
        box(hd.name, (-1.5, 0, -4.5), (3, 9, 9))
        box(hd.name, (-2, 7, -4.5), (4, 3, 9), mat=knob_mat)
        for k, zc in enumerate((-3.4, -1.15, 1.15, 3.4)):
            alt = 6 if k % 2 else -6
            fg = bone(f'{side}_finger{k}', at(hd.name, 0, 9.5, zc), hd.name,
                      rot=((k - 1.5) * 14, 0, 12 * sx + alt), mat=hide_mat)
            box(fg.name, (-1, 0, -1), (2, 12, 2))
            box(fg.name, (-1.5, 10, -1.5), (3, 3, 3), mat=knob_mat)
            cl = bone(f'{side}_claw{k}', at(fg.name, 0, 12.5, 0), fg.name, rot=(0, 0, 30 * sx), mat=claw_mat)
            box(cl.name, (-1, 0, -1), (2, 5, 2))
            box(cl.name, (-0.5 - 0.6 * sx, 4.5, -0.5), (1, 5, 1))

    m = Model('wendigo', 256, 256, r.roots)
    m.scale = 0.5
    return m


DEFAULT_MAT = hide_mat
FOCUS = 'head'

POSES = {
    # the jumpscare: skull lunging, jaw unhinged, arms raised wide so the claws frame the face
    'attack': {
        'body': (0.12, 0, 0, 0, 0, 0),
        'neck': (-0.3, 0, 0, 0, 0, 0),
        'head': (-0.5, 0, 0, 0, 0, 0),
        'jaw': (1.0, 0, 0, 0, 0, 0),
        'right_arm': (-1.2, 0.6, 0, 0, 0, 0),
        'left_arm': (-1.1, -0.6, 0, 0, 0, 0),
        'right_forearm': (-0.4, 0, 0, 0, 0, 0),
        'left_forearm': (-0.5, 0, 0, 0, 0, 0),
        'right_hand': (0.35, 0, 0, 0, 0, 0),
        'left_hand': (0.35, 0, 0, 0, 0, 0),
        'right_finger0': (0, 0, 0.2, 0, 0, 0), 'right_finger1': (0, 0, -0.2, 0, 0, 0),
        'right_finger2': (0, 0, 0.2, 0, 0, 0), 'right_finger3': (0, 0, -0.2, 0, 0, 0),
        'left_finger0': (0, 0, -0.2, 0, 0, 0), 'left_finger1': (0, 0, 0.2, 0, 0, 0),
        'left_finger2': (0, 0, -0.2, 0, 0, 0), 'left_finger3': (0, 0, 0.2, 0, 0, 0),
    },
    # head thrown back (sockets still on the camera), jaw at max, claws curled forward: crucifixion
    'scream': {
        'body': (-0.05, 0, 0, 0, 0, 0),
        'chest': (-0.15, 0, 0, 0, 0, 0),
        'neck': (-0.35, 0, 0, 0, 0, 0),
        'head': (-0.35, 0, 0, 0, 0, 0),
        'jaw': (1.15, 0, 0, 0, 0, 0),
        'right_arm': (-0.5, 0.4, 0.55, 0, 0, 0),
        'left_arm': (-0.5, -0.4, -0.55, 0, 0, 0),
        'right_forearm': (-0.6, 0, 0, 0, 0, 0),
        'left_forearm': (-0.6, 0, 0, 0, 0, 0),
        'right_hand': (0.4, 0, 0, 0, 0, 0),
        'left_hand': (0.4, 0, 0, 0, 0, 0),
    },
    # creeping on all fours, face kept on the player
    'stalk': {
        'chest': (0.35, 0, 0, 0, 0, 0),
        'neck': (-0.2, 0, 0, 0, 0, 0),
        'head': (-0.6, 0, 0, 0, 0, 0),
        'right_arm': (-0.9, 0, 0, 0, 0, 0),
        'left_arm': (-0.9, 0, 0, 0, 0, 0),
        'right_forearm': (0.3, 0, 0, 0, 0, 0),
        'left_forearm': (0.3, 0, 0, 0, 0, 0),
        'jaw': (0.1, 0, 0, 0, 0, 0),
    },
    # uncanny curious tilt
    'head_tilt': {
        'neck': (0, 0, 0.2, 0, 0, 0),
        'head': (0, 0, 0.7, 0, 0, 0),
        'jaw': (0.15, 0, 0, 0, 0, 0),
    },
}

ANIM_NOTES = """placeholder"""
