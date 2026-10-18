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
SKIN = pal('#0c0a0a', '#181414', '#262020', '#362d2b', '#473b38', '#5a4c47', '#6f5e57', '#86736a', '#a08b7e')
FROST = pal('#060405', '#0d0a0b', '#151011', '#1e1718', '#282020', '#342a29', '#433634', '#544541', '#67554f')
BONE = pal('#17120f', '#2c241d', '#463b2f', '#635543', '#80715a', '#9e8f72', '#bbad8e', '#d5cbab', '#ece5cc')
ANTLER = pal('#110d0b', '#211914', '#352a20', '#4b3c2e', '#635140', '#7d6953', '#99836a', '#b6a085', '#d0bfa2')
FUR = pal('#060404', '#0d0a09', '#16110f', '#211915', '#2c221c', '#3a2d25', '#4b3b31', '#5e4b3e')
FLESH = pal('#160607', '#290b0c', '#3f1213', '#581c1a', '#722823', '#8b392e', '#a44d3c')
BLOOD = pal('#110203', '#1f0405', '#300709', '#430b0d', '#581012', '#6e1618')
CLAW = pal('#040304', '#09080b', '#110f14', '#1a171e', '#25212a', '#332e39', '#4a4452')
GAP = pal('#040202', '#0a0505', '#120808', '#1b0d0c', '#251412')
VOID = hx('#040203')
VEIN = hx('#2c2234')


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


# ------------------------------------------------------------------ blood
def drip_len(col, seed, lo, length):
    h = hash3(col, 0, 0, seed)
    if h < lo:
        return -1.0
    return 1.0 + (h - lo) / (1 - lo) * length


def blood_here(ctx):
    """Clean dried-blood shapes (drips/streaks, not speckle). Returns 0 none, 1 blood, 2 dark edge."""
    n = ctx.bone.name
    if not is_side(ctx):
        if '_finger' in n or n.endswith('_hand'):
            return 1 if ctx.face == 'bottom' or hash3(ctx.i // 2, ctx.j // 2, 0, 5) > 0.4 else 0
        return 0
    col = wcol(ctx) + hash3(ctx.cube.size[0], ctx.cube.size[1], ctx.cube.size[2], 3) * 50
    from_bottom = ctx.h - 1 - ctx.j
    if '_finger' in n:
        return 1 if ctx.t > 0.25 or hash3(col, 0, 0, 7) > 0.5 else 0
    if n.endswith('_hand'):
        L = drip_len(col, 11, 0.15, ctx.h * 0.9)
        return 1 if from_bottom < L else (2 if from_bottom < L + 1 else 0)
    if n.endswith('_forearm') and ctx.h > 12:
        L = drip_len(col, 13, 0.35, 9)
        return 1 if from_bottom < L else 0
    if n == 'jaw':
        if dpos(ctx)[2] > ctx.bone.abs[2] - 14 or ctx.face in ('back', 'front'):
            return 0
        L = drip_len(col, 17, 0.35, ctx.h * 0.7)
        return 1 if ctx.j < L else 0
    return 0


# ------------------------------------------------------------------ materials
def skin_value(ctx, p, base=0.50):
    x, y, z = p
    v = base + light(ctx, 1.0)
    if not flat(ctx) and edge(ctx) == 0:
        v -= 0.07
    v += bands(fbm(x * 0.09 + 3, y * 0.09, z * 0.09, 2, 11), 0.42, 0.6, 0.07)
    if hash3(x, y, z, 5) > 0.988:
        v -= 0.15  # pores / old scars
    return v


EXTREMITY = {'_arm': (0.0, 0.15), '_forearm': (0.25, 0.85), '_hand': (0.85, 0.95), '_leg': (0.0, 0.1),
             '_shin': (0.2, 0.55), '_foot': (0.6, 0.85)}


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


def hide_mat(ctx):
    """Grey-brown leathery hide stretched over bone: sinew ridges, veins, rot, drips of blood."""
    p = dpos(ctx)
    x, y, z = p
    v = skin_value(ctx, p)
    name = ctx.bone.name
    side = is_side(ctx)
    if side and not flat(ctx):
        v -= ctx.t * 0.08  # occlusion toward the far end of the segment
        # leathery wrinkles: scattered short dark dashes with a lit lip underneath
        def dash(i, j):
            return hash3((i + 3 * j) // 3, j, ctx.w * 7 + ctx.h, 17) > 0.86
        if dash(ctx.i, ctx.j):
            v -= 0.12
        elif ctx.j > 0 and dash(ctx.i, ctx.j - 1):
            v += 0.06
    limb = name.endswith(('_arm', '_forearm', '_leg', '_shin', '_foot', '_hand')) or '_finger' in name
    if limb and side and ctx.w >= 4:
        mid = ctx.w // 2
        if ctx.i == mid:
            v += 0.11  # bone ridge pressing through
        elif ctx.i == mid + 1:
            v -= 0.09
    fr = frost(ctx)
    c = pick(SKIN, v) if fr <= 0 else mix(pick(SKIN, v), pick(FROST, v + 0.05), fr)
    if limb and side and ctx.h >= 12 and ctx.face in ('front', 'west', 'east'):
        # one wandering vein per face
        seed = int(hash3(ctx.cube.size[1], ctx.w, ord(ctx.face[0]), 9) * 100)
        vc = int(ctx.w * 0.3 + 1.6 * math.sin(ctx.j * 0.35 + seed))
        if ctx.i == vc and 0.15 < ctx.t < 0.85 and hash3(seed, 0, 0, 1) > 0.35:
            c = mix(c, VEIN, 0.55)
    r = fbm(x * 0.1, y * 0.1, z * 0.1, 2, 31)
    if r > 0.71:
        c = pick(FLESH, v - 0.02)
    elif r > 0.68:
        c = pick(SKIN, v - 0.22)
    b = blood_here(ctx)
    if b == 1:
        c = pick(BLOOD, v * 0.85 + 0.05)
    elif b == 2:
        c = pick(BLOOD, 0.1)
    return c


def knob_mat(ctx):
    """Skin pulled tight over bony knobs (knees, elbows, spine, hip points): pale, polished tops."""
    p = dpos(ctx)
    v = skin_value(ctx, p, 0.53)
    if ctx.face == 'top' or (is_side(ctx) and ctx.j == 0):
        v += 0.07
    fr = frost(ctx)
    c = pick(SKIN, v) if fr <= 0 else mix(pick(SKIN, v), pick(FROST, v + 0.05), fr)
    b = blood_here(ctx)
    if b:
        c = pick(BLOOD, 0.45 if b == 1 else 0.1)
    return c


def gap_mat(ctx):
    """Deep shadow between the ribs."""
    p = dpos(ctx)
    v = 0.4 + light(ctx, 0.4) + bands(fbm(p[0] * 0.3, p[1] * 0.3, p[2] * 0.3, 2, 3), 0.4, 0.6, 0.2)
    return pick(GAP, v)


def rib_mat(ctx):
    """A rib slat: hide shrink-wrapped over a curved bone (lit top row, shadowed underside)."""
    p = dpos(ctx)
    x, y, z = p
    v = 0.58 + light(ctx, 0.9)
    if is_side(ctx) and ctx.h <= 3:
        v += (0.17, 0.0, -0.15)[min(2, ctx.j)]
    if ctx.face == 'bottom':
        v -= 0.25
    v += bands(fbm(x * 0.2, y * 0.2, z * 0.2, 2, 7), 0.4, 0.6, 0.06)
    c = pick(SKIN, v)
    if v > 0.78:
        c = pick(BONE, v - 0.3)
    # blood from the mouth has run down the front of the chest
    if ctx.face == 'front' and abs(x) < 7:
        L = drip_len(math.floor(x), 401, 0.4, 3)
        if L > 0 and (ctx.bone.name == 'chest') and (y + 32) < L * 5:
            c = pick(BLOOD, v * 0.8)
    return c


def bone_value(ctx, p, base=0.62):
    x, y, z = p
    v = base + light(ctx, 1.0)
    if not flat(ctx) and edge(ctx) == 0:
        v -= 0.09
    v += bands(fbm(x * 0.16, y * 0.16, z * 0.16, 2, 21), 0.4, 0.62, 0.07)
    return v


def skull_mat(ctx):
    p = dpos(ctx)
    x, y, z = p
    v = bone_value(ctx, p)
    if ctx.face == 'bottom':
        v -= 0.15
    c = pick(BONE, v)
    if hash3(x, y, z, 23) > 0.97:
        c = pick(BONE, v - 0.3)  # pits
    st = fbm(x * 0.2, y * 0.2, z * 0.2, 2, 24)
    if st > 0.66:
        c = mix(c, hx('#4b3122'), 0.35)  # tannin stains
    return c


def palate_mat(ctx):
    """Snout: bone outside, raw gums + old blood on the underside (seen when the jaw drops)."""
    if ctx.face == 'bottom':
        p = dpos(ctx)
        v = 0.42 + bands(fbm(p[0] * 0.4, 0, p[2] * 0.4, 2, 51), 0.4, 0.6, 0.15)
        if ctx.i in (0, ctx.w - 1):
            return pick(BLOOD, 0.3)
        return pick(FLESH, v)
    c = skull_mat(ctx)
    if is_side(ctx) and ctx.j >= ctx.h - 2:
        p = dpos(ctx)
        L = drip_len(math.floor(p[2] if ctx.face in ('west', 'east') else p[0]), 57, 0.55, 2)
        if L > 0 and ctx.h - 1 - ctx.j < L:
            c = pick(BLOOD, 0.45)
    return c


def antler_mat(ctx):
    p = dpos(ctx)
    x, y, z = p
    n = ctx.bone.name
    base = 0.42 if n.endswith('antler') else (0.54 if n.endswith('_b') else 0.66)
    v = base + light(ctx, 1.1)
    if not flat(ctx) and edge(ctx) == 0:
        v -= 0.09
    if is_side(ctx) and ctx.w >= 2 and hash3(ctx.i, ctx.cube.size[1], ctx.cube.size[0], 61) > 0.6:
        v -= 0.11  # longitudinal grooves
    v += bands(vnoise(x * 0.5, y * 0.5, z * 0.5, 62), 0.35, 0.65, 0.06)
    return pick(ANTLER, v)


def burr_mat(ctx):
    p = dpos(ctx)
    v = 0.36 + light(ctx, 1.0) + bands(hash3(p[0], p[1], p[2], 63), 0.35, 0.65, 0.1)
    return pick(ANTLER, v)


def broken_mat(ctx):
    """Antler snapped off: pale splintered core on the break face."""
    if ctx.face == 'top' or (is_side(ctx) and ctx.j == 0):
        p = dpos(ctx)
        return pick(BONE, 0.72 + bands(hash3(p[0], p[1], p[2], 64), 0.3, 0.7, 0.12))
    return antler_mat(ctx)


def splinter_mat(ctx):
    """A snapped rib punching out through the hide: bloody at the root, pale splintered tip."""
    p = dpos(ctx)
    lx = local(ctx)[0] - ctx.cube.origin[0]
    v = bone_value(ctx, p, 0.6)
    if lx < 1.6:
        return pick(BLOOD, 0.35 + light(ctx, 0.5))
    if ctx.face == 'east':
        return pick(BONE, 0.85)
    return pick(BONE, v)


def claw_mat(ctx):
    v = 0.40 + light(ctx, 1.2)
    if is_side(ctx) and ctx.i == 0:
        v += 0.25  # glossy edge
    if is_side(ctx):
        v -= ctx.t * 0.12
    return pick(CLAW, v)


def hoof_mat(ctx):
    p = dpos(ctx)
    v = 0.38 + light(ctx, 1.1) + bands(hash3(p[0], p[1] // 2, p[2], 72), 0.3, 0.7, 0.06)
    if is_side(ctx) and ctx.j == 0:
        v += 0.2
    if ctx.face == 'bottom':
        return pick(CLAW, 0.1)
    return pick(CLAW, v)


def fur_value(ctx, col, rowpos):
    """Matted strands: per-strand value, dark partings, lighter clumped tips."""
    strand = hash3(col // 2, ctx.cube.size[1], 0, 81)
    v = 0.30 + strand * 0.32 + light(ctx, 0.9)
    if col % 3 == 0:
        v -= 0.12
    v += rowpos * 0.12
    return v


def fur_shell(axis='y', depth=4.0, seed=90, holes=0.0, solid_top=True):
    """Matted fur shell with a ragged hanging edge.

    axis 'y': strands hang toward local +y; '-z': fur ends toward local -z (front)."""
    def f(ctx):
        c = ctx.cube
        lx, ly, lz = local(ctx)
        if axis == 'y':
            if ctx.face == 'bottom':
                return None
            span = c.size[1]
            pos = (ly - c.origin[1]) / span
            col = math.floor(lx * 1.0) if ctx.face in ('front', 'back') else math.floor(lz * 1.0) + 50
            if ctx.face == 'top':
                pos, col = 0.0, ctx.i
        else:
            span = c.size[2]
            pos = (c.origin[2] + span - lz) / span
            col = math.floor(ly) if ctx.face != 'top' and ctx.face != 'bottom' else math.floor(lx) + 50
            if ctx.face == 'front':
                return None
        lim = 1.0 - (depth * (0.2 + hash3(col, 0, 0, seed) * 0.8)) / span
        if pos > lim:
            return None
        p = dpos(ctx)
        if holes and fbm(p[0] * 0.3, p[1] * 0.3, p[2] * 0.3, 2, seed + 1) < holes:
            return None
        v = fur_value(ctx, col, max(0.0, pos - lim + 0.25) * 2)
        return pick(FUR, v)
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
            v += 0.1  # lighter split ends catch the light
        return pick(FUR, v)
    return f


def string_mat(seed):
    """Strings of bloody drool / sinew hanging from the mouth (thin, ragged, mostly transparent)."""
    def f(ctx):
        lx, ly, lz = local(ctx)
        c = ctx.cube
        col = math.floor(lx)
        h = hash3(col, 0, 0, seed)
        if h < 0.45 or col % 2:
            return None
        depth = ly - c.origin[1]
        if depth > c.size[1] * (0.3 + 0.7 * (h - 0.45) / 0.55):
            return None
        return pick(BLOOD, 0.55 - depth / c.size[1] * 0.3)
    return f


def crest_mat(seed):
    """Matted fur crest standing off the spine (zero-thickness plane, ragged free edge toward +z)."""
    def f(ctx):
        lx, ly, lz = local(ctx)
        c = ctx.cube
        depth = lz - c.origin[2]
        col = math.floor(ly)
        lim = c.size[2] * (0.3 + 0.7 * hash3(col // 1, 0, 0, seed))
        if depth > lim or hash3(col, 2, 0, seed) < 0.12:
            return None
        v = 0.36 + (hash3(col // 2, 0, 0, seed + 1) * 0.3) + depth / c.size[2] * 0.2 + light(ctx, 0.5)
        if col % 3 == 0:
            v -= 0.12
        return pick(FUR, v)
    return f


def back_mat(ctx):
    """Back: hide with the ribs showing through as ridges and the spine groove."""
    c = hide_mat(ctx)
    if ctx.face == 'back':
        p = dpos(ctx)
        if abs(p[0]) < 1.6:
            return scale(c, 0.62)
        if abs(p[0]) < 2.6:
            return scale(c, 1.15)
        k = (ctx.j + 2) % 4
        if k == 0 and abs(p[0]) > 4:
            return scale(c, 0.8)
        if k == 1 and abs(p[0]) > 4:
            return scale(c, 1.1)
    return c


def rotskin_shell(holes=0.45, seed=95):
    """Rotten hide still clinging to the bone: torn patches (alpha holes) with raw red edges."""
    def f(ctx):
        p = dpos(ctx)
        x, y, z = p
        n = fbm(x * 0.22, y * 0.22, z * 0.22, 2, seed)
        if n < holes:
            return None
        v = 0.44 + light(ctx, 1.0) + bands(fbm(x * 0.5, y * 0.5, z * 0.5, 2, seed + 2), 0.4, 0.6, 0.06)
        if n < holes + 0.035:
            return pick(FLESH, v + 0.05)
        return pick(SKIN, v)
    return f


def flap_mat(seed=97, kind='skin'):
    """Hanging strip of skin (zero-thickness plane) with a torn, ragged lower edge."""
    def f(ctx):
        lx, ly, lz = local(ctx)
        c = ctx.cube
        depth = ly - c.origin[1]
        col = math.floor(lz) if c.size[0] == 0 else math.floor(lx)
        h = hash3(col, 0, 0, seed)
        lim = c.size[1] * (0.3 + 0.7 * h)
        if depth > lim or hash3(col, 1, 0, seed) < 0.15:
            return None
        v = 0.44 + light(ctx, 0.5) - depth / c.size[1] * 0.2
        if kind == 'fur':
            return pick(FUR, v + 0.1 + (col % 2) * 0.1)
        if depth > lim - 1.5:
            return pick(FLESH, v + 0.05)
        if (col + int(depth)) % 5 == 0:
            v -= 0.1
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
        elif h < 0.24:
            L = 0.8  # missing tooth
        else:
            L = 1.2 + ((h - 0.24) / 0.76) ** 1.6 * (maxlen - 1.8)
        depth = (ly - root_y) * grow
        if depth < 0 or depth > L:
            return None
        if depth < 1.0:
            return pick(FLESH, 0.25) if h > 0.5 else pick(BLOOD, 0.35)
        t = depth / max(1.0, L)
        v = 0.95 - t * 0.3 + light(ctx, 0.3)
        if hash3(col, 3, 0, seed) > 0.78 and depth < 1.0 + hash3(col, 4, 0, seed) * L * 0.6:
            return pick(BLOOD, 0.4 + t * 0.3)  # blood caked from the roots down
        if hash3(col, 5, 0, seed) > 0.8:
            v -= 0.25  # rotten, yellowed tooth
        return pick(BONE, v)
    return f


def jaw_mat(ctx):
    """Mandible: bone outside, the top face is the gum bed / rotten tongue seen when it gapes."""
    if ctx.face == 'top':
        p = dpos(ctx)
        v = 0.40 + bands(fbm(p[0] * 0.4, 0, p[2] * 0.4, 2, 53), 0.4, 0.6, 0.12)
        if ctx.i in (0, ctx.w - 1):
            return pick(BLOOD, 0.35)
        return pick(FLESH, v)
    return skull_mat(ctx)


def tongue_mat(ctx):
    p = dpos(ctx)
    v = 0.38 + light(ctx, 0.6) + bands(fbm(p[0] * 0.5, p[1] * 0.5, p[2] * 0.5, 2, 55), 0.4, 0.6, 0.1)
    return pick(FLESH, v)


def throat_mat(ctx):
    return pick(GAP, 0.2 if ctx.face != 'front' else 0.05)


def neck_mat(ctx):
    """Neck: hide with cords of tendon (vertical lines) on the sides."""
    c = hide_mat(ctx)
    if ctx.face in ('west', 'east') and ctx.i % 3 == 1:
        return scale(c, 0.78)
    return c


# ------------------------------------------------------------------ pixel-art decals
K = VOID
SOCK_PAL = {'K': K, '1': BONE[1], '2': BONE[2], '3': BONE[3], '4': BONE[4], 'r': BLOOD[2]}
WH = hx('#f6f8ff')

# right eye socket (viewer's left). (4, 8) is the pupil position; '.' untouched.
SOCKET_R = [
    "32.......",
    "2K23.....",
    "1KK12....",
    "1KKKK123.",
    "2KKKKKK12",
    "1KKKKKKK1",
    "21KKKKKK1",
    ".21KKKKK1",
    "..21KKK12",
    "...3211r.",
    "....3.r..",
    "......r..",
]
PUPIL_R = (4, 10)  # in face texels


def socket_decal(img, u0, v0, w, h):
    """Cranium front: deep slanted sockets, pupils, a forehead crack, tear-streaks of old blood."""
    pixelart(SOCKET_R, SOCK_PAL, anchor='topleft', dx=0, dy=3)(img, u0, v0, w, h)
    pixelart(SOCKET_R, SOCK_PAL, anchor='topleft', dx=w - 9, dy=3, flip=True)(img, u0, v0, w, h)
    px = img.load()
    pi, pj = PUPIL_R
    for i in (pi, w - 1 - pi):
        px[u0 + i, v0 + pj] = WH
    for i, j in ((6, 0), (6, 1), (7, 2)):
        px[u0 + i, v0 + j] = BONE[1]
    for i, j in ((w - 5, 0), (w - 6, 1)):
        px[u0 + i, v0 + j] = BONE[2]


def eyes_decal(img, u0, v0, w, h):
    px = img.load()
    pi, pj = PUPIL_R
    for i in (pi, w - 1 - pi):
        px[u0 + i, v0 + pj] = WH
        for di, dj in ((1, 0), (-1, 0), (0, -1), (0, 1)):
            px[u0 + i + di, v0 + pj + dj] = hx('#2a3446')


def side_socket_decal(right):
    """Orbit wrapping around the corner of the cranium onto the side face (no pupil)."""
    rows = [
        "....32",
        "..321K",
        ".21KKK",
        "21KKKK",
        ".1KKKK",
        "..21KK",
        "...321",
    ]
    rows2 = [
        "..........",
        "...3......",
        "..2.3.....",
        "...1.2....",
        "....1.....",
    ]

    def fn(img, u0, v0, w, h):
        # west face: front edge at high i; east face: front edge at i=0 (flip)
        if right:
            pixelart(rows, SOCK_PAL, anchor='topleft', dx=w - 6, dy=4)(img, u0, v0, w, h)
            pixelart(rows2, SOCK_PAL, anchor='topleft', dx=1, dy=6)(img, u0, v0, w, h)
        else:
            pixelart(rows, SOCK_PAL, anchor='topleft', dx=0, dy=4, flip=True)(img, u0, v0, w, h)
            pixelart(rows2, SOCK_PAL, anchor='topleft', dx=w - 11, dy=6, flip=True)(img, u0, v0, w, h)
    return fn


def cranium_top_decal(img, u0, v0, w, h):
    px = img.load()
    path = [(5, 0), (5, 1), (6, 2), (6, 3), (7, 4), (8, 5), (8, 6), (9, 7), (9, 8), (10, 9), (10, 10), (11, 11), (11, 12)]
    for i, j in path:
        if 0 <= i < w and 0 <= j < h:
            px[u0 + i, v0 + j] = BONE[1]
    for i, j in ((8, 6), (7, 7), (6, 8), (12, 3), (13, 4), (14, 4), (15, 5)):
        px[u0 + i, v0 + j] = BONE[2]


def nasal_front_decal(img, u0, v0, w, h):
    """Premaxilla tip seen from the front: two split nasal slits over the incisors."""
    rows = [
        "2K1K2",
        "1K2K1",
        ".2.2.",
    ]
    pixelart(rows, SOCK_PAL, anchor='topleft')(img, u0, v0, w, h)


def nasal_top_decal(img, u0, v0, w, h):
    """Top of the snout: the nasal aperture opens toward the front (high j)."""
    rows = [
        "...2...",
        "..212..",
        ".21K12.",
        ".1KKK1.",
        "21KKK12",
        "1KK1KK1",
        "KKK1KKK",
    ]
    pixelart(rows, SOCK_PAL, anchor='bottom')(img, u0, v0, w, h)


def ridge_decal(img, u0, v0, w, h):
    px = img.load()
    for j in range(h):
        if j % 5 != 4:
            px[u0 + w // 2, v0 + j] = BONE[2]


# ------------------------------------------------------------------ build
def build():
    r = Rig()

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
        'right': ((-38.0, 16.0), (-14.0, 1.0), (5.0, 15.0), (20.0, 8.0)),
        'left': ((-38.0, 16.0), (-12.0, 7.0), (7.0, 23.0), (20.0, 17.0)),
    }
    for side, sx in (('right', -1), ('left', 1)):
        hip, knee, hock, fet = LEGS[side]
        L1, a1 = seg(hip, knee)
        L2, a2 = seg(knee, hock)
        L3, a3 = seg(hock, fet)
        leg = bone(f'{side}_leg', (7.0 * sx, hip[0], hip[1]), rot=(a1, 0, -2 * sx), mat=hide_mat, flen=L1)
        mbox(leg.name, sx, (-5.5, -5, -6), (11, 16, 12))
        mbox(leg.name, sx, (-3.5, 10, -3.5), (7, int(L1) - 10, 7))
        mbox(leg.name, sx, (-7, -2, -2.5), (3, 6, 6), mat=knob_mat)
        # matted tufts on the hip
        mbox(leg.name, sx, (-8, -6, -4.5), (4, 14, 10), mat=clump_mat(301 + sx))
        mbox(leg.name, sx, (-6, -6.5, -7), (6, 7, 3), mat=clump_mat(309 + sx))
        shin = bone(f'{side}_shin', at(leg.name, 0, L1, 0), leg.name, rot=(a2 - a1, 0, 0), mat=hide_mat, flen=L2)
        box(shin.name, (-3.5, -3, -6.5), (7, 7, 6), mat=knob_mat)
        box(shin.name, (-3, 1, -2.5), (6, 9, 7))
        box(shin.name, (-2, 9, -2), (4, int(L2) - 11, 4))
        box(shin.name, (-1, 5, 2), (2, int(L2) - 10, 2), mat=knob_mat)
        box(shin.name, (-3, L2 - 5, -2), (6, 6, 7), mat=knob_mat)
        foot = bone(f'{side}_foot', at(shin.name, 0, L2, 0), shin.name, rot=(a3 - a2, 0, 0), mat=hide_mat, flen=L3)
        box(foot.name, (-2, 0, -2), (4, int(L3), 4))
        box(foot.name, (-2.5, L3 - 4, -2.5), (5, 5, 5), mat=knob_mat)
        hoof = bone(f'{side}_hoof', at(foot.name, 0, L3, 0), foot.name, rot=(-a3, 0, 0), mat=hoof_mat)
        box(hoof.name, (-3.2, 0, -6.5), (3, 4, 8))
        box(hoof.name, (0.2, 0, -6.5), (3, 4, 8))
        box(hoof.name, (-1.5, -2.5, 1.5), (3, 2, 2))
    hip = LEGS['right'][0]

    # ---------------- body: pelvis + sunken abdomen
    bone('body', (0, hip[0], hip[1]), rot=(22, 0, 0), mat=hide_mat)
    box('body', (-8, -6, -5), (16, 9, 11))
    for sx in (-1, 1):
        mbox('body', sx, (-10, -9, -4), (4, 5, 7), mat=knob_mat)
    box('body', (-2, -6, 5), (4, 6, 3), mat=knob_mat)
    box('body', (-7, -8, 5.5), (14, 9, 3), mat=clump_mat(321))
    box('body', (-6, -21, -3), (12, 16, 8))
    for yy in (-20, -15, -10):
        box('body', (-1.5, yy, 4.5), (3, 3, 3), mat=knob_mat)
    bone('tail', at('body', 0, 0, 7), 'body', rot=(38, 0, 0), mat=fur_shell('y', 6, seed=131))
    box('tail', (-2.5, -1, -1), (5, 10, 2))

    # ---------------- chest: ribcage with separate slats, withers, fur crest
    CH = 32  # chest lean relative to body (net 54)
    bone('chest', at('body', 0, -17, 0), 'body', rot=(CH, 0, 0), mat=hide_mat)
    box('chest', (-10, -29, -8), (20, 28, 9), mat=gap_mat)
    box('chest', (-10.5, -32, 1), (21, 31, 7), mat=back_mat)
    for k, wdt in enumerate([20, 22, 24, 24, 23, 21]):
        box('chest', (-wdt / 2, -28 + 4 * k, -9.5), (wdt, 2, 11), mat=rib_mat)
    box('chest', (-1.5, -29, -10.5), (3, 22, 2), mat=knob_mat)
    box('chest', (11, -12.5, -6), (5, 2, 2), mat=splinter_mat)
    box('chest', (-12.5, -35, -6), (25, 6, 13))
    box('chest', (-10, -31.5, -9), (20, 2, 3), mat=knob_mat)
    for k, d in enumerate([8, 8, 6, 5, 4, 3]):
        box('chest', (-1.5, -34 + 5 * k, 7), (3, 3, d), mat=knob_mat)
    box('chest', (0, -36, 8), (0, 24, 9), mat=crest_mat(145))
    box('chest', (-12.5, -35, -6), (25, 6, 13), mat=fur_shell('y', 9, seed=141, holes=0.25), inflate=1.0)
    for side, sx in (('right', -1), ('left', 1)):
        sc = bone(f'{side}_scapula', at('chest', 6.5 * sx, -31, 7.5), 'chest', rot=(22, 0, -10 * sx), mat=knob_mat)
        box(sc.name, (-4.5, 0, -1.5), (9, 15, 2))
    NET = 22 + CH

    # ---------------- neck + skull
    NK = 76
    bone('neck', at('chest', 0, -33, -1), 'chest', rot=(NK, 0, 0), mat=neck_mat)
    box('neck', (-4, -16, -4.5), (8, 17, 9))
    for yy in (-13, -7):
        box('neck', (-1, yy, 4), (2, 3, 4), mat=knob_mat)
    box('neck', (0, -18, 4.5), (0, 19, 7), mat=crest_mat(155))
    box('neck', (-4, -16, -4.5), (8, 17, 9), mat=fur_shell('y', 7, seed=151, holes=0.2), inflate=0.9)
    bone('skull_mount', at('neck', 0, -15, 0), 'neck', rot=(-(NET + NK), 0, 0))
    bone('head', at('skull_mount', 0, 0, 0), 'skull_mount', rot=(26, 0, 7), mat=skull_mat)
    box('head', (-10, -17, -12), (20, 16, 15), decals={
        'front': socket_decal, 'eyes:front': eyes_decal, 'top': cranium_top_decal,
        'west': side_socket_decal(True), 'east': side_socket_decal(False)})
    box('head', (-8, -19.5, -10), (16, 3, 12))
    box('head', (-8, -15, 2.5), (16, 9, 2))
    for sx in (-1, 1):
        mbox('head', sx, (-11.5, -5, -14), (5, 3, 9))
    box('head', (-2, -11, -27), (4, 3, 16), decals={'top': ridge_decal})
    box('head', (-5, -8, -23), (10, 9, 11), mat=palate_mat)
    box('head', (-3.5, -7, -33), (7, 8, 10), mat=palate_mat, decals={'top': nasal_top_decal})
    box('head', (-2.5, -4, -36), (5, 5, 3), mat=palate_mat, decals={'front': nasal_front_decal})
    box('head', (-4, -1, -15), (8, 6, 3), mat=throat_mat)
    # upper teeth (zero-thickness planes): incisors at the tip, long fangs along the sides
    box('head', (-3.5, 1, -35.6), (7, 6, 0), mat=teeth_mat(1, 6, 'x', 201, canines=(-3, 2)))
    for side, sx in (('right', -1), ('left', 1)):
        # side rows live on bones yawed 90 deg so each strip is a cheap (L, h, 0) plane along -Z
        tb = bone(f'{side}_fangs', at('head', 3.9 * sx, 1, -23), 'head', rot=(0, 90, 0), mat=skull_mat)
        box(tb.name, (0, 0, 0), (11, 7, 0), mat=teeth_mat(0, 6.5, 'x', 203 + sx, canines=(1, 6)))
        box(tb.name, (-10, 0, -1.5 * sx), (10, 5, 0), mat=teeth_mat(0, 4, 'x', 207 + sx))
    # rot + fur over the skull, torn flaps
    box('head', (-10, -17, -5), (20, 16, 8), mat=fur_shell('-z', 6, seed=161), inflate=0.7)
    box('head', (-5, -8, -23), (10, 9, 11), mat=rotskin_shell(0.46, 171), inflate=0.45)
    box('head', (-11.6, -3, -13), (0, 12, 7), mat=flap_mat(181))
    box('head', (11.6, -3, -11), (0, 9, 5), mat=flap_mat(183))
    box('head', (-11.5, -2, -14.2), (5, 13, 0), mat=flap_mat(193))
    box('head', (7, -2, -14.2), (4, 9, 0), mat=flap_mat(195))
    for side, sx in (('right', -1), ('left', 1)):
        br = bone(f'{side}_brow', at('head', 0.5 * sx, -13, -12.5), 'head', rot=(0, 0, -16 * sx), mat=skull_mat)
        mbox(br.name, sx, (-10, -1.5, -1.5), (10, 3, 3))

    bone('jaw', at('head', 0, -1, -9), 'head', rot=(15, 0, 0), mat=skull_mat)
    box('jaw', (-3, 5, -33.5), (6, 3, 24), mat=jaw_mat, ref='head')
    for sx in (-1, 1):
        mbox('jaw', sx, (-5.5, -2, -13), (2, 9, 5), ref='head')
        mbox('jaw', sx, (-4.5, 5, -16), (2, 3, 6), ref='head')
    box('jaw', (-2.5, 7.5, -34.2), (5, 2, 6), ref='head')
    box('jaw', (-2.5, 2, -33.2), (5, 3, 0), mat=teeth_mat(5, 3.5, 'x', 211, canines=(-3, 1), grow=-1), ref='head')
    for side, sx in (('right', -1), ('left', 1)):
        lt = bone(f'{side}_lower_teeth', at('head', 2.6 * sx, 5, -13), 'jaw', rot=(0, 90, 0), mat=skull_mat)
        box(lt.name, (0, -4, 0), (20, 4, 0), mat=teeth_mat(0, 4, 'x', 213 + sx, grow=-1, canines=(18,)))
    box('jaw', (0, 8, -28), (0, 10, 14), mat=flap_mat(185), ref='head')
    box('jaw', (-2, 6, -31), (4, 9, 0), mat=string_mat(191), ref='head')

    # ---------------- antlers (asymmetric crown; the left one is snapped)
    ra = bone('right_antler', at('head', -5.5, -19, -3), 'head', rot=(-34, 0, -66), mat=antler_mat)
    box(ra.name, (-3.5, -2, -3.5), (7, 2, 7), mat=burr_mat)
    box(ra.name, (-2, -14, -2), (4, 13, 4))
    box(ra.name, (-1, -9, -10), (2, 3, 9))
    box(ra.name, (-1, -12, -10), (2, 4, 2))
    box(ra.name, (2, -10, -1), (8, 2, 2))
    rb = bone('right_antler_b', at(ra.name, 0, -13, 0), ra.name, rot=(12, 0, 18), mat=antler_mat)
    box(rb.name, (-1.5, -14, -1.5), (3, 14, 3))
    box(rb.name, (1.5, -9, -1), (11, 2, 2))
    box(rb.name, (-1, -5, 1.5), (2, 2, 8))
    box(rb.name, (-6, -12, -1), (5, 2, 2))
    rc = bone('right_antler_c', at(rb.name, 0, -13, 0), rb.name, rot=(8, 0, 8), mat=antler_mat)
    box(rc.name, (-1, -11, -1), (2, 11, 2))
    box(rc.name, (1, -7, -1), (9, 2, 2))
    box(rc.name, (-5, -10, -1), (4, 2, 2))

    la = bone('left_antler', at('head', 5.5, -19, -3), 'head', rot=(-34, 0, 56), mat=antler_mat)
    box(la.name, (-3.5, -2, -3.5), (7, 2, 7), mat=burr_mat)
    box(la.name, (-2, -14, -2), (4, 13, 4))
    box(la.name, (-1, -9, -9), (2, 3, 8))
    box(la.name, (-9, -10, -1), (7, 2, 2))
    lb = bone('left_antler_b', at(la.name, 0, -13, 0), la.name, rot=(10, 0, -30), mat=antler_mat)
    box(lb.name, (-1.5, -11, -1.5), (3, 11, 3))
    box(lb.name, (-1, -16, -1), (2, 5, 2), mat=broken_mat)
    box(lb.name, (-4.5, -8, -1), (3, 2, 2), mat=broken_mat)
    box(lb.name, (1.5, -6, -1), (6, 2, 2))
    box(lb.name, (-1, -4, 1.5), (2, 2, 7))
    box(lb.name, (0, -10, -0.5), (0, 15, 2), mat=flap_mat(187))

    # ---------------- arms: grotesquely long, knobby, 4 clawed fingers
    for side, sx in (('right', -1), ('left', 1)):
        sh = bone(f'{side}_shoulder', at('chest', 14 * sx, -32 if sx < 0 else -29, -1), 'chest', rot=(-NET, 0, 0))
        fwd = -10 if sx < 0 else -4
        arm = bone(f'{side}_arm', at(sh.name, 0, 0, 0), sh.name, rot=(fwd, 0, (-12 if sx < 0 else -9) * sx), mat=hide_mat, flen=30)
        box(arm.name, (-4.5, -4.5, -4.5), (9, 9, 9), mat=knob_mat)
        box(arm.name, (-3.5, 3, -3.5), (7, 11, 7))
        box(arm.name, (-2.5, 13, -2.5), (5, 16, 5))
        # matted tufts over the shoulder
        mbox(arm.name, sx, (-7.5, -6.5, -4.5), (4, 17, 9), mat=clump_mat(331 + sx))
        mbox(arm.name, sx, (-4, -6.5, 2.5), (8, 12, 3), mat=clump_mat(335 + sx))
        mbox(arm.name, sx, (-4, -6.5, -6), (7, 8, 3), mat=clump_mat(339 + sx))
        mbox(arm.name, sx, (-5, -7, -4), (8, 3, 7), mat=clump_mat(343 + sx, 0.3))
        fa = bone(f'{side}_forearm', at(arm.name, 0, 30, 0), arm.name, rot=(-16 if sx < 0 else -8, 0, 5 * sx), mat=hide_mat, flen=29)
        box(fa.name, (-3.5, -3, -1.5), (7, 6, 7), mat=knob_mat)
        box(fa.name, (-3, 1, -3), (6, 11, 6))
        box(fa.name, (-2, 11, -2), (4, 15, 4))
        box(fa.name, (-2.5, 25, -2.5), (5, 4, 5), mat=knob_mat)
        hd = bone(f'{side}_hand', at(fa.name, 0, 29, 0), fa.name, rot=(10, 0, 4 * sx), mat=hide_mat, flen=10)
        box(hd.name, (-1.5, 0, -4.5), (3, 9, 9))
        box(hd.name, (-2, 7, -4.5), (4, 3, 9), mat=knob_mat)
        for k, zc in enumerate((-3.4, -1.15, 1.15, 3.4)):
            fg = bone(f'{side}_finger{k}', at(hd.name, 0, 9.5, zc), hd.name,
                      rot=((k - 1.5) * 8, 0, 16 * sx), mat=hide_mat)
            box(fg.name, (-1, 0, -1), (2, 11, 2))
            box(fg.name, (-1, 10, -1), (2, 5, 2), mat=claw_mat)
            box(fg.name, (-0.5 - 0.7 * sx, 14, -0.5), (1, 5, 1), mat=claw_mat)

    m = Model('wendigo', 256, 256, r.roots)
    m.scale = 0.5
    return m


DEFAULT_MAT = hide_mat
FOCUS = 'head'

POSES = {
    # jaw unhinged, claws thrown forward, skull lunging
    'attack': {
        'body': (0.12, 0, 0, 0, 0, 0),
        'neck': (-0.25, 0, 0, 0, 0, 0),
        'head': (-0.45, 0, 0, 0, 0, 0),
        'jaw': (0.95, 0, 0, 0, 0, 0),
        'right_arm': (-1.5, 0, 0.35, 0, 0, 0),
        'left_arm': (-1.3, 0, -0.4, 0, 0, 0),
        'right_forearm': (-0.5, 0, 0, 0, 0, 0),
        'left_forearm': (-0.7, 0, 0, 0, 0, 0),
        'right_hand': (-0.5, 0, 0, 0, 0, 0),
        'left_hand': (-0.5, 0, 0, 0, 0, 0),
    },
    # skull thrown back, jaw at max, arms spread wide
    'scream': {
        'body': (-0.15, 0, 0, 0, 0, 0),
        'chest': (-0.2, 0, 0, 0, 0, 0),
        'neck': (-0.5, 0, 0, 0, 0, 0),
        'head': (-0.8, 0, 0, 0, 0, 0),
        'jaw': (1.15, 0, 0, 0, 0, 0),
        'right_arm': (-0.4, 0, 1.1, 0, 0, 0),
        'left_arm': (-0.4, 0, -1.1, 0, 0, 0),
        'right_forearm': (-0.3, 0, 0, 0, 0, 0),
        'left_forearm': (-0.3, 0, 0, 0, 0, 0),
    },
}

ANIM_NOTES = """placeholder"""
