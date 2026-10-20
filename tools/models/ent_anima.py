"""Ánima -- the lost soul (DEAD LINE).

Authored at 2x texel density (model.scale = 0.5) in absolute rig coordinates: +Y down, ground y = 24,
faces -Z, right_* on -X.

Silhouette: a hunched, floating wraith.  An oversized, elongated skull juts forward between shrugged
shoulders; its dislocated jaw hangs open in front of the sternum (a tall black scream).  The open rib cage
shows a cold soul-light glowing inside.  Two over-long arms reach forward and outward, ending in jointed
claw fingers, with torn ectoplasm hanging under the forearms like burial-shroud sleeves.  No legs: the
torso narrows into a ragged shroud and a four-segment tail that curls back and frays into nothing.
Hair streams up and back like cold flame.

Translucent + emissive (entityTranslucentEmissive): core ~205 alpha, wisps ~110, frayed hems cut to 0.
"""
import math

from mcmodel import Model, hash3, face_light, pick
from rig import Rig
from paint import hx, mix

RIG = None  # set by build(); materials need absolute pivots
DY = 2.0    # design frame -> model frame vertical offset (keeps the face map in design coordinates)

# ------------------------------------------------------------------ palettes (hand-picked, hue shifted)
SPEC = [hx('#031018'), hx('#06232d'), hx('#0a3742'), hx('#0f4e58'), hx('#166970'),
        hx('#21878a'), hx('#36a6a3'), hx('#5ac4bb'), hx('#93e0d4'), hx('#d4fbf1')]
CYAN = hx('#24c9da')
CYAN_HI = hx('#6deef4')
VOIDC = {'K': hx('#010507'), 'k': hx('#04151b'), 'v': hx('#0b3c45'), 'g': hx('#1a6a70')}
TEETH = [hx('#1d4446'), hx('#467d7a'), hx('#7fb7ad'), hx('#bfe6da'), hx('#eafff8')]
HAIR = [hx('#01080c'), hx('#03161d'), hx('#062530'), hx('#0b3743'), hx('#124c58'),
        hx('#1d6670'), hx('#2f868c'), hx('#52aaa8'), hx('#8fd6cf')]
SOUL = [hx('#7fe9e0'), hx('#b9fbf3'), hx('#effffc')]
GLOW_EYE = (226, 255, 250, 255)
GLOW_EYE2 = (110, 240, 246, 255)
GLOW_RIM = (12, 92, 104, 255)

# ------------------------------------------------------------------ the face (projected onto every front face
# of the head bone).  cols x = -8..7, rows y = -34..-20.  digits = SPEC tone, K/k/v = void, g = pupil glint,
# c = crack / black tear.
FACE = [
    "3455667777665543",  # y-34
    "4566778888776654",  # y-33
    "4567c78998877654",  # y-32
    "45678c7667887654",  # y-31
    "567889c799988765",  # y-30  brow ridge (top)
    "4567778558777654",  # y-29  brow ridge (front)
    "3444vkK77Kkv4443",  # y-28  sockets begin (inner corners raised: anguish)
    "34vkKKK66KKKkv43",  # y-27
    "4vkKKKK66KKKKkv4",  # y-26
    "vkKKKKk55kKKKKkv",  # y-25
    "kKKKgKvkkvKgKKKk",  # y-24  glints (pinprick pupils)
    "kKKKKvkKKkvKKKKk",  # y-23  nasal cavity opens
    "5vkkv5vKKv5vkkv5",  # y-22  sockets droop at the outer corners
    "7c8995vKKv5998c7",  # y-21  cheekbones, black tears start
    "5c66654vv45666c5",  # y-20
]


def clamp(v, a=0.0, b=1.0):
    return a if v < a else b if v > b else v


def loc(ctx):
    """Texel centre in cube-local texel units."""
    w, h, d = ctx.cube.size
    s, t, f = ctx.s, ctx.t, ctx.face
    if f == 'front':
        return s * w, t * h, 0.0
    if f == 'back':
        return (1 - s) * w, t * h, float(d)
    if f == 'west':
        return 0.0, t * h, (1 - s) * d
    if f == 'east':
        return float(w), t * h, s * d
    if f == 'top':
        return s * w, 0.0, (1 - t) * d
    return s * w, float(h), (1 - t) * d


def apos(ctx):
    """Texel centre in authored (rest, unrotated) absolute coordinates."""
    p = RIG.abs_pivot[ctx.bone.name]
    o = ctx.cube.origin
    lx, ly, lz = loc(ctx)
    return p[0] + o[0] + lx, p[1] + o[1] + ly - DY, p[2] + o[2] + lz


def edge(ctx):
    return min(ctx.i, ctx.j, ctx.w - 1 - ctx.i, ctx.h - 1 - ctx.j)


def tag(ctx):
    return ctx.cube.name or ''


def tone(v):
    return pick(SPEC, v)


def digit(ch):
    return SPEC[int(ch)]


def with_a(c, a):
    return (c[0], c[1], c[2], int(clamp(a, 0, 255)))


def h2(a, b, seed=0):
    return hash3(a, b, seed * 7 + 3, seed)


# ------------------------------------------------------------------ alpha
BONE_ALPHA = {
    'body': 205, 'ribs_right': 210, 'ribs_left': 210, 'neck': 200, 'head': 212, 'jaw': 212, 'hair': 190,
    'right_arm': 196, 'left_arm': 196, 'right_forearm': 186, 'left_forearm': 186,
    'right_hand': 180, 'left_hand': 180,
    'tail1': 190, 'tail2': 170, 'tail3': 148, 'tail4': 124,
}


def base_alpha(ctx):
    n = ctx.bone.name
    if n in BONE_ALPHA:
        return BONE_ALPHA[n]
    if 'finger' in n or 'thumb' in n:
        return 170
    if n.startswith('hair_'):
        return 172
    if n.startswith('shroud'):
        return 150
    return 190


def frayed(ctx, lo, hi, seed=0, cols=1.0):
    """Ragged hem: True where the texel lies past this column's frayed strand length.
    lo/hi: authored-y range where fraying happens (above lo solid, below hi gone)."""
    x, y, z = apos(ctx)
    col = math.floor((x + z) * cols)
    ln = lo + (hi - lo) * (0.35 + 0.65 * h2(col, seed, seed))
    return y > ln


# ------------------------------------------------------------------ materials
def rim(ctx, c, amount=0.55):
    """Cyan glow on face borders: the silhouette of every mass reads as a glowing edge."""
    e = edge(ctx)
    if e == 0 and ctx.face in ('west', 'east', 'top', 'front', 'back'):
        return mix(c, CYAN, amount * 0.6)
    return c


def face_mat(ctx):
    """Head bone: skull, brow, cheekbones, maxilla, stretched cheeks."""
    x, y, z = apos(ctx)
    t = tag(ctx)
    a = 212
    f = ctx.face
    if t == 'throat':
        return throat_mat(ctx)
    if t == 'tooth':
        return tooth_mat(ctx)
    # front faces carry the projected face map
    if f in ('front', 'back') and t in ('cranium', 'brow', 'bridge', 'cheekbone'):
        ri = int(math.floor(y)) + 34
        ci = int(math.floor(x)) + 8
        if f == 'back' and t == 'cranium':
            return back_skull(ctx)
        if 0 <= ri < len(FACE) and 0 <= ci < 16:
            ch = FACE[ri][ci]
            if ch in VOIDC:
                return with_a(VOIDC[ch], 240 if ch in 'Kk' else 228)
            if ch == 'c':
                return with_a(hx('#03171c'), 236)
            c = digit(ch)
            return with_a(c, a)
    if t == 'maxilla' and f == 'front':
        # upper lip: skin over the gum, gum line black
        ly = loc(ctx)[1]
        xc = abs(x + 0.5 - 0.0) / 5.0
        if ly > 2:
            return with_a(VOIDC['v'], 230)
        v = 0.66 - xc * 0.25 - ly * 0.06
        return with_a(tone(v), a)
    if t == 'maxilla' and f == 'bottom':
        return with_a(VOIDC['k'], 238)  # palate
    if t == 'cheekwall':
        return cheekwall_mat(ctx)
    if t == 'cranium':
        return back_skull(ctx)
    # protrusion sides / undersides
    v = 0.6 + face_light(ctx) * 1.3
    if f == 'bottom':
        v = 0.22
    c = tone(v)
    return with_a(rim(ctx, c, 0.4), a)


def back_skull(ctx):
    """Sides/top/back of the elongated cranium: temples sunken, sutures, rim glow."""
    x, y, z = apos(ctx)
    f = ctx.face
    v = 0.58 + face_light(ctx) * 1.2
    if f in ('west', 'east'):
        # sunken temple behind the socket, cheek hollow
        if -29 < y < -21 and z < -6:
            v -= 0.16
        if z < -10.5:
            v -= 0.06
        # suture zigzag
        if abs((z + 2) - (1 if int(y) % 2 else 0)) < 0.5 and y < -27:
            v -= 0.14
    if f == 'top':
        # sagittal suture
        if abs(x - (0.5 if int(z) % 2 else -0.5)) < 0.6:
            v -= 0.14
    if f == 'back':
        v -= 0.05
        if abs(x) < 0.6 and int(y) % 3 == 0:
            v -= 0.1
    v += (h2(math.floor(x * 1.0 + z), math.floor(y), 5) - 0.5) * 0.08
    c = tone(v)
    return with_a(rim(ctx, c, 0.5), 205)


def cheekwall_mat(ctx):
    """Stretched cheek skin framing the scream: tear streaks outside, wet dark gums inside."""
    x, y, z = apos(ctx)
    f = ctx.face
    inner = (f == 'east' and x < 0) or (f == 'west' and x > 0)
    if inner:
        v = 0.12 + clamp((-z - 8) / 6) * 0.14 - clamp((y + 16) / 8) * 0.06
        if int(y) % 3 == 0:
            v -= 0.05
        return with_a(tone(v), 236)
    if f == 'front':
        ci = int(math.floor(x)) + 8
        tear = ci in (1, 14)
        if tear and h2(y, ci, 2) > 0.15:
            return with_a(hx('#03171c'), 236)
        v = 0.5 - clamp((y + 19) / 12) * 0.12
        if ci in (2, 13):
            v += 0.06
        return with_a(rim(ctx, tone(v), 0.3), 212)
    if f == 'bottom':
        return with_a(tone(0.18), 220)
    # outer side: stretched skin with long vertical tendons
    v = 0.48 + face_light(ctx) * 1.2 - clamp((y + 19) / 12) * 0.12
    lz = loc(ctx)[2]
    if int(lz) in (2, 5):
        v -= 0.1
    if int(lz) == 3:
        v += 0.05
    return with_a(rim(ctx, tone(v), 0.5), 208)


def throat_mat(ctx):
    x, y, z = apos(ctx)
    # deep throat: pure black centre, faint dark-cyan toward the edges
    d = max(abs(x) / 5.0, 0)
    c = mix(VOIDC['K'], VOIDC['k'], clamp(d * 1.2 - 0.2))
    return with_a(c, 242)


def tooth_mat(ctx):
    lx, ly, lz = loc(ctx)
    h = ctx.cube.size[1]
    up = ctx.bone.name == 'head'
    tip = ly / max(1.0, h) if up else 1 - ly / max(1.0, h)  # 0 at root, 1 at tip
    v = 0.72 - tip * 0.25 + face_light(ctx) * 0.8
    if ctx.face in ('west', 'east'):
        v -= 0.18
    if tip < 0.25:
        v -= 0.28  # gum root, stained
    c = pick(TEETH, v)
    return with_a(c, 236)


def jaw_mat(ctx):
    x, y, z = apos(ctx)
    t = tag(ctx)
    f = ctx.face
    if t == 'throat':
        return throat_mat(ctx)
    if t == 'tooth':
        return tooth_mat(ctx)
    if t == 'chin':
        ly = loc(ctx)[1]
        if f == 'top':
            # tongue-less floor of the mouth
            return with_a(mix(VOIDC['k'], VOIDC['v'], 0.4 if edge(ctx) == 0 else 0.0), 238)
        if f == 'front':
            xc = abs(x) / 5.0
            rows = [0.18, 0.62, 0.74, 0.58]  # lower lip (dark gum), chin highlight, chin, underside
            v = rows[min(3, int(ly))] - xc * xc * 0.2
            if int(ly) == 0:
                return with_a(VOIDC['v'], 230)
            ci = int(math.floor(x)) + 8
            if int(ly) >= 2 and ci in (5, 10) and h2(ci, 1) > 0.3:
                v -= 0.18  # chin dimples / cracks
            return with_a(rim(ctx, tone(v), 0.4), 212)
        if f == 'bottom':
            return with_a(tone(0.3), 210)
        v = 0.5 + face_light(ctx) * 1.2
        return with_a(rim(ctx, tone(v), 0.5), 210)
    if t == 'jawwall':
        v = 0.2
        return with_a(tone(v), 236)
    return face_mat(ctx)


def bone_mat(ctx):
    """Ribs, clavicles, sternum, spine, shoulders: pale teal-white bone under a thin glowing skin."""
    x, y, z = apos(ctx)
    t = tag(ctx)
    f = ctx.face
    lx, ly, lz = loc(ctx)
    w, h, d = ctx.cube.size
    a = base_alpha(ctx)
    v = 0.68 + face_light(ctx) * 1.3
    if t == 'rib':
        # rounded bar: bright top edge, dark underside line
        if f in ('front', 'back', 'west', 'east'):
            if ctx.j == 0:
                v += 0.14
            elif ctx.j == ctx.h - 1:
                v -= 0.22
        # fade toward the spine (back of the rib)
        if f in ('top', 'bottom', 'west', 'east'):
            v -= clamp(lz / max(1, d)) * 0.18
        # lateral end darker
        if f == 'front':
            far = lx / max(1, w) if x < 0 else 1 - lx / max(1, w)
            v -= (1 - far) * 0.0 + (far < 0.2) * 0.08
        if f == 'back':
            v -= 0.25
    elif t == 'sternum':
        if ctx.j % 3 == 2:
            v -= 0.16
        v += 0.04
    elif t == 'clav':
        if ctx.j == 0:
            v += 0.1
        if ctx.j == ctx.h - 1:
            v -= 0.2
    elif t == 'vert':
        if ctx.j == ctx.h - 1:
            v -= 0.22
        if f == 'back' and ctx.j == 0:
            v += 0.08
    elif t == 'shoulder':
        v -= 0.04
        if f == 'top' and edge(ctx) > 0:
            v += 0.06
    c = tone(v)
    c = rim(ctx, c, 0.55)
    return with_a(c, a)


def back_mat(ctx):
    """The skin of the back: drawn tight over spine, ribs and shoulder blades."""
    x, y, z = apos(ctx)
    f = ctx.face
    a = 200
    v = 0.56 + face_light(ctx) * 1.2
    if f == 'back':
        # rib ridges under the skin
        if int(y + 100) % 3 == 0:
            v -= 0.12
        elif int(y + 100) % 3 == 1:
            v += 0.05
        # spine groove
        if abs(x) < 1.5:
            v -= 0.14
        # scapula outline
        for sx in (-1, 1):
            dx = x * sx
            if 2.5 < dx < 8.5 and -17 < y < -8:
                v += 0.07
        v -= clamp((y + 4) / 6) * 0.15
    elif f == 'front':
        v = 0.2  # inner wall of the rib cage
        a = 228
    elif f in ('west', 'east'):
        if int(y + 100) % 3 == 0:
            v -= 0.12
    c = tone(v)
    return with_a(rim(ctx, c, 0.5), a)


def void_mat(ctx):
    """Inside of the chest: black-teal hollow, lit faintly by the soul."""
    x, y, z = apos(ctx)
    d = math.sqrt((x - 1) ** 2 + (y + 9.5) ** 2) / 8.0
    v = 0.24 - d * 0.18
    c = tone(v)
    return with_a(c, 230)


def soul_mat(ctx):
    lx, ly, lz = loc(ctx)
    e = edge(ctx)
    c = SOUL[2] if e > 0 else SOUL[1]
    if ctx.face == 'bottom':
        c = SOUL[0]
    return with_a(c, 235)


def waist_mat(ctx):
    x, y, z = apos(ctx)
    v = 0.48 + face_light(ctx) * 1.2
    if ctx.face == 'front':
        # sunken belly with the lumbar spine showing through
        if abs(x) < 1:
            v += 0.08
        if int(y) % 2 == 0 and abs(x) < 1.5:
            v -= 0.06
        v -= abs(x) / 4 * 0.14
    c = tone(v)
    return with_a(rim(ctx, c, 0.45), 200)


def arm_mat(ctx):
    """Emaciated limbs: bone-thin, knotted joints, ridged knuckles, black claw tips."""
    x, y, z = apos(ctx)
    n = ctx.bone.name
    t = tag(ctx)
    f = ctx.face
    lx, ly, lz = loc(ctx)
    w, h, d = ctx.cube.size
    a = base_alpha(ctx)
    if t == 'drape':
        return ecto_mat(ctx)
    v = 0.62 + face_light(ctx) * 1.3
    if f in ('front', 'back'):
        # round limb: bright centre stripe
        cx = lx / max(1, w)
        v += 0.08 - abs(cx - 0.5) * 0.3
    if t == 'knob':
        if ctx.j == 0:
            v += 0.1
        if ctx.j == ctx.h - 1:
            v -= 0.2
    if t in ('upper', 'fore'):
        # tendons: two dark lines along the forearm (radius / ulna split)
        if t == 'fore' and f in ('front', 'back') and ctx.i == 1:
            v -= 0.12
        v -= (ly / max(1, h)) * 0.08
    if 'finger' in n or 'thumb' in n:
        seg = ly / max(1, h)
        if int(ly) % 3 == 2 and f != 'bottom':
            v -= 0.12  # knuckle creases
        if 'tip' in n or 'thumb' in n:
            if seg > 0.62:
                # black claw
                c = mix(VOIDC['k'], CYAN, 0.12 if f in ('front', 'west') and ctx.i == 0 else 0.0)
                return with_a(c, 230)
            if seg > 0.5:
                v -= 0.2
        a -= int(seg * 10)
    if t == 'palm':
        if f == 'back':
            # palm side (faces the victim when grabbing): deep creases
            if ctx.j in (2, 4) and 1 <= ctx.i <= ctx.w - 2:
                v -= 0.16
        if f == 'front':
            # back of the hand: metacarpal ridges
            if ctx.i % 2 == 1:
                v -= 0.08
    c = tone(v)
    return with_a(rim(ctx, c, 0.5), a)


def ecto_mat(ctx):
    """Ectoplasm: tail, shroud tatters, sleeve drapes. Long flowing streaks, frayed dissolving hems."""
    x, y, z = apos(ctx)
    n = ctx.bone.name
    t = tag(ctx)
    f = ctx.face
    lx, ly, lz = loc(ctx)
    w, h, d = ctx.cube.size
    a = base_alpha(ctx)
    # flow streaks: per-column tone offsets that run the whole length
    col = math.floor(x * 0.9 + z * 0.9) if f in ('front', 'back') else math.floor(z * 0.9 + x * 0.9)
    s = h2(col, 3, 11)
    v = 0.6 + face_light(ctx) * 1.1 + (s - 0.5) * 0.22
    if s > 0.82:
        v += 0.1
    if t in ('shroud', 'drape'):
        # thin torn cloth of light
        prog = ly / max(1, h)
        v = 0.66 + (s - 0.5) * 0.3 - prog * 0.18
        a = int(160 - prog * 50)
        if frayed(ctx, (RIG.abs_pivot[n][1] + ctx.cube.origin[1]) + h * 0.45,
                  (RIG.abs_pivot[n][1] + ctx.cube.origin[1]) + h * 1.05, seed=len(n), cols=1.0):
            return None
        # a few holes eaten through the cloth
        if h2(math.floor(lx + lz), math.floor(ly), 9 + len(n)) > 0.9 and prog > 0.25:
            return None
        if ctx.i % 4 == 0:
            v -= 0.08
        return with_a(rim(ctx, tone(v), 0.4), a)
    if n.startswith('tail'):
        k = int(n[-1])
        v -= k * 0.05
        prog = ly / max(1, h)
        a = int(a - prog * 18)
        if k == 4:
            if frayed(ctx, RIG.abs_pivot[n][1] + 1.5, RIG.abs_pivot[n][1] + h + 1, seed=7, cols=1.0):
                return None
        if k >= 3 and h2(math.floor(lx + lz * 1.3), math.floor(ly), 30 + k) > (0.93 if k == 3 else 0.8):
            return None
        if t == 'wisp':
            if frayed(ctx, RIG.abs_pivot[n][1] + 1, RIG.abs_pivot[n][1] + h + 1, seed=13, cols=1.0):
                return None
            a = int(120 - prog * 30)
    c = tone(v)
    return with_a(rim(ctx, c, 0.6), a)


def hair_mat(ctx):
    """Hair drifting upward: deep teal strands, light catching on the ridges, tips dissolving."""
    x, y, z = apos(ctx)
    n = ctx.bone.name
    t = tag(ctx)
    f = ctx.face
    lx, ly, lz = loc(ctx)
    w, h, d = ctx.cube.size
    a = 190
    if n == 'hair':
        # scalp mass: dark roots, strands combed backward
        col = math.floor(x) if f in ('top', 'front', 'back') else math.floor(z)
        s = h2(col, 1, 21)
        v = 0.45 + (s - 0.5) * 0.35 + face_light(ctx) * 0.8
        if f == 'front':
            # ragged hairline over the forehead
            if ly > 1.5 + 3.5 * h2(math.floor(x), 2, 22):
                return None
            v -= ly * 0.06
        if f == 'back' or f in ('west', 'east'):
            if t == 'backhair' and ly > h * 0.55 + h * 0.45 * h2(col, 4, 23):
                return None
        return with_a(pick(HAIR, v), a)
    # strands: length 0 at root -> 1 at tip (authored upward = -y)
    prog = 1 - ly / max(1, h)
    seg = tag(ctx)
    if seg == 'b':
        prog = 0.45 + prog * 0.35
    elif seg == 'c':
        prog = 0.8 + prog * 0.2
    else:
        prog = prog * 0.45
    col = ctx.i
    s = h2(col, len(n), 31)
    v = 0.35 + prog * 0.45 + (s - 0.5) * 0.25 + face_light(ctx) * 0.6
    if ctx.i == 0 or ctx.i == ctx.w - 1:
        v -= 0.08
    a = int(185 - prog * 75)
    if prog > 0.7 and h2(ctx.i, math.floor(ly), len(n) + 40) < (prog - 0.7) * 2.2:
        return None
    return with_a(pick(HAIR, v), a)


def anima_mat(ctx):
    n = ctx.bone.name
    t = tag(ctx)
    if n == 'head':
        return face_mat(ctx)
    if n == 'jaw':
        return jaw_mat(ctx)
    if n == 'hair' or n.startswith('hair_'):
        return hair_mat(ctx)
    if n.startswith('tail') or n.startswith('shroud'):
        return ecto_mat(ctx)
    if t == 'void':
        return void_mat(ctx)
    if t == 'soul':
        return soul_mat(ctx)
    if t == 'back':
        return back_mat(ctx)
    if t == 'waist':
        return waist_mat(ctx)
    if n in ('body', 'ribs_right', 'ribs_left', 'neck'):
        return bone_mat(ctx)
    return arm_mat(ctx)


DEFAULT_MAT = anima_mat


# ------------------------------------------------------------------ emissive decals (layer 'eyes')
def eyes_face(img, u0, v0, w, h):
    """Cranium front: pinprick pupils deep in the sockets + faint cyan socket rims."""
    px = img.load()
    for j, row in enumerate(FACE):
        for i, ch in enumerate(row):
            if i >= w or j >= h:
                continue
            if ch == 'v' and j >= 6:
                px[u0 + i, v0 + j] = GLOW_RIM
            if ch == 'g':
                px[u0 + i, v0 + j] = GLOW_EYE
                if j + 1 < h:
                    px[u0 + i, v0 + j + 1] = GLOW_EYE2


def eyes_soul(img, u0, v0, w, h):
    px = img.load()
    for j in range(h):
        for i in range(w):
            e = min(i, j, w - 1 - i, h - 1 - j)
            px[u0 + i, v0 + j] = (200, 255, 248, 255) if e > 0 else (90, 220, 214, 255)


# ------------------------------------------------------------------ build
def build():
    global RIG
    r = Rig()
    RIG = r

    _bone = r.bone

    def bone(name, pivot, **kw):
        return _bone(name, (pivot[0], pivot[1] + DY, pivot[2]), **kw)
    r.bone = bone

    def B(bone, frm, size, name, **kw):
        c = r.box(bone, (frm[0], frm[1] + DY, frm[2]), size, **kw)
        c.name = name
        return c

    # ---------------- body (root): waist pivot, leaning into the hunt
    r.bone('body', (0, 0, 2), rot=(10, 0, 0))
    B('body', (-6, -16, -3), (12, 15, 6), 'void')
    B('body', (-1, -12, -2), (4, 5, 3), 'soul',
      decals={'eyes:front': eyes_soul, 'eyes:west': eyes_soul, 'eyes:east': eyes_soul, 'eyes:top': eyes_soul})
    B('body', (-8, -18, 2), (16, 18, 3), 'back')
    B('body', (-4, -2, -2), (8, 6, 6), 'waist')
    B('body', (-5, -21, -1), (10, 4, 6), 'shoulder')       # trapezius hump behind the skull
    B('body', (-11, -20, -2), (6, 5, 6), 'shoulder')       # shrugged shoulders
    B('body', (5, -20, -2), (6, 5, 6), 'shoulder')
    B('body', (-9, -18, -5), (8, 2, 3), 'clav')
    B('body', (1, -18, -5), (8, 2, 3), 'clav')
    B('body', (-1, -16, -5.5), (2, 11, 2), 'sternum')
    for y in (-20, -17, -14, -11, -8, -5, -2):
        B('body', (-1.5, y, 4), (3, 2, 3), 'vert')
    B('body', (-8, -17, 4.5), (5, 8, 1), 'clav')           # shoulder blades
    B('body', (3, -17, 4.5), (5, 8, 1), 'clav')

    # ---------------- rib cage: slanted slats, the hollow shows between them
    ribs = [(-15, 6), (-12, 8), (-9, 9), (-6, 8), (-3, 6)]
    r.bone('ribs_right', (-1, -9, -4.5), parent='body', rot=(0, 0, -15))
    r.bone('ribs_left', (1, -9, -4.5), parent='body', rot=(0, 0, 15))
    for y, w in ribs:
        B('ribs_right', (-1 - w, y, -5), (w, 2, 8), 'rib')
        B('ribs_left', (1, y, -5), (w, 2, 8), 'rib')

    # ---------------- neck + head
    r.bone('neck', (0, -19, 0), parent='body', rot=(8, 0, 0))
    B('neck', (-1.5, -24, -2), (3, 5, 3), 'vert')
    r.bone('head', (0, -22, -3), parent='neck', rot=(-6, 0, 7))
    cr = B('head', (-8, -34, -11.9), (16, 16, 13), 'cranium', decals={'eyes:front': eyes_face})
    B('head', (-7, -31, 1), (14, 11, 2), 'cranium')         # occipital bulge
    B('head', (-8, -30, -14), (16, 2, 3), 'brow')
    B('head', (-1, -28, -13), (2, 4, 2), 'bridge')
    B('head', (-8, -21, -14), (5, 2, 3), 'cheekbone')
    B('head', (3, -21, -14), (5, 2, 3), 'cheekbone')
    B('head', (-5, -19, -14), (10, 3, 5), 'maxilla')
    B('head', (-7, -19, -13), (2, 10, 7), 'cheekwall')
    B('head', (5, -19, -13), (2, 10, 7), 'cheekwall')
    B('head', (-5, -17, -7.4), (10, 9, 1), 'throat')
    # upper teeth: broken, irregular, one long fang
    for tx, tw, th in ((-5, 1, 3), (-3.5, 2, 2), (-1, 1, 4), (1, 2, 2), (3.5, 1, 3)):
        B('head', (tx, -16, -13.8), (tw, th, 1), 'tooth')

    # ---------------- jaw: hangs dislocated in front of the sternum
    r.bone('jaw', (0, -17, -8), parent='head')
    B('jaw', (-5, -17, -8.6), (10, 12, 1), 'throat')
    B('jaw', (-5, -9, -14), (10, 4, 6), 'chin')
    for tx, tw, th in ((-4.5, 1, 2), (-2.5, 2, 3), (0.5, 1, 2), (2.5, 2, 3)):
        B('jaw', (tx, -9 - th, -13.8), (tw, th, 1), 'tooth')

    # ---------------- hair: scalp mass + strands drifting up and back
    r.bone('hair', (0, -34, -3), parent='head')
    B('hair', (-8, -36, -12), (16, 4, 14), 'cap', inflate=0.5)
    B('hair', (-8, -33, 1), (16, 12, 2), 'backhair', inflate=0.5)
    strands = [  # x, z, rotX, rotZ, length scale
        (-6.5, -9, -35, -30, 0.8), (-3.5, -10, -22, -12, 1.0), (-0.5, -10, -18, -2, 0.9),
        (2.5, -10, -26, 10, 1.0), (5.5, -9, -38, 26, 0.8), (-4, -3, -62, -14, 1.2), (3, -2, -66, 15, 1.2),
    ]
    for k, (sx, sz, rx, rz, ls) in enumerate(strands):
        nm = 'hair_%d' % (k + 1)
        r.bone(nm, (sx, -35, sz), parent='hair', rot=(rx, 0, rz))
        la = int(round(7 * ls))
        lb = int(round(6 * ls))
        B(nm, (sx - 1.5, -35 - la, sz - 1), (3, la, 2), 'a')
        B(nm, (sx - 1 + (0.5 if k % 2 else -0.5), -35 - la - lb + 1, sz - 0.8), (2, lb, 2), 'b')
        B(nm, (sx - 1, -35 - la - lb - 4 + 1, sz), (2, 5, 0), 'c')

    # ---------------- arms (authored hanging, posed reaching forward)
    def arm(side, sx, rot_arm, rot_fore, rot_hand, curl):
        def X(x0, w):
            return x0 if sx > 0 else -(x0 + w)
        arm_n, fore_n, hand_n = side + '_arm', side + '_forearm', side + '_hand'
        r.bone(arm_n, (9 * sx, -17, 1), parent='body', rot=(rot_arm[0], -rot_arm[1] * sx, -rot_arm[2] * sx))
        B(arm_n, (X(7, 4), -18, -1), (4, 14, 4), 'upper')
        B(arm_n, (X(6.5, 5), -6, -1.5), (5, 4, 5), 'knob')
        B(arm_n, (X(9, 0), -15, 3), (0, 10, 6), 'drape')
        r.bone(fore_n, (9 * sx, -5, 1), parent=arm_n, rot=(rot_fore, 0, 0))
        B(fore_n, (X(7.5, 3), -4, -0.5), (3, 12, 3), 'fore')
        B(fore_n, (X(7, 4), 6, -1), (4, 3, 4), 'knob')
        B(fore_n, (X(9, 0), -3, 2.5), (0, 12, 7), 'drape')
        r.bone(hand_n, (9 * sx, 8, 1), parent=fore_n, rot=(rot_hand, 0, 0))
        B(hand_n, (X(5, 8), 8, 0), (8, 6, 2), 'palm')
        # fingers: index (medial) .. pinky (lateral)
        fingers = [(6, -15, 7, 7), (8, -5, 8, 8), (10, 5, 8, 7), (12, 15, 6, 6)]
        for k, (fx, splay, lp, ld) in enumerate(fingers):
            fn = '%s_finger_%d' % (side, k + 1)
            tn = fn + '_tip'
            r.bone(fn, (fx * sx, 13.5, 1), parent=hand_n, rot=(curl[0], 0, -splay * sx))
            B(fn, (X(fx - 1, 2), 13.5, 0), (2, lp, 2), 'finger')
            r.bone(tn, (fx * sx, 13 + lp, 1), parent=fn, rot=(curl[1], 0, 0))
            B(tn, (X(fx - 1, 2), 13 + lp, 0.05), (2, ld, 2), 'finger')
        th = side + '_thumb'
        r.bone(th, (4.5 * sx, 9, 1), parent=hand_n, rot=(10, 0, 35 * sx))
        B(th, (X(3.5, 2), 9, 0), (2, 8, 2), 'finger')

    arm('right', -1, (-62, 22, 0), -22, 28, (14, 26))
    arm('left', 1, (-92, 16, 0), -12, 20, (20, 32))

    # ---------------- shroud tatters around the waist
    r.bone('shroud_front', (0, -1, -5), parent='body', rot=(-12, 0, 0))
    B('shroud_front', (-6, -1, -5), (12, 13, 0), 'shroud')
    r.bone('shroud_back', (0, -2, 5.2), parent='body', rot=(16, 0, 0))
    B('shroud_back', (-7, -2, 5.2), (14, 15, 0), 'shroud')
    r.bone('shroud_right', (-6.5, -2, 0), parent='body', rot=(0, 0, 14))
    B('shroud_right', (-6.5, -2, -4), (0, 12, 8), 'shroud')
    r.bone('shroud_left', (6.5, -2, 0), parent='body', rot=(0, 0, -14))
    B('shroud_left', (6.5, -2, -4), (0, 12, 8), 'shroud')

    # ---------------- tail: no legs, the soul trails off and frays
    r.bone('tail1', (0, 1, 1.5), parent='body', rot=(14, 0, 0))
    B('tail1', (-5, 0, -3), (10, 9, 8), 'tail')
    r.bone('tail2', (0, 8, 1.5), parent='tail1', rot=(20, 0, 6))
    B('tail2', (-4, 7.5, -2.5), (8, 8, 7), 'tail')
    r.bone('tail3', (0, 15, 2), parent='tail2', rot=(24, 0, -8))
    B('tail3', (-3, 14.5, -1.5), (6, 7, 5), 'tail')
    B('tail3', (-2, 15, 3.5), (4, 8, 0), 'wisp')
    r.bone('tail4', (0, 21, 2), parent='tail3', rot=(26, 0, -10))
    B('tail4', (-1.5, 20.5, 0.5), (3, 8, 3), 'tail')
    B('tail4', (-3, 21, 2), (6, 9, 0), 'wisp')
    B('tail4', (0, 21, -1), (0, 9, 6), 'wisp')

    m = Model('anima', 256, 256, r.roots)
    m.scale = 0.5
    m.render_type = 'entityTranslucentEmissive'
    return m


FOCUS = 'head'

POSES = {
    # jaw dislocates downward, head thrown back, arms flung wide, fingers splayed
    'scream': {
        'head': (-0.42, 0, -0.08, 0, 0, 0),
        'neck': (-0.15, 0, 0, 0, 0, 0),
        'jaw': (0.22, 0, 0, 0, 5.0, -1.0),
        'body': (-0.12, 0, 0, 0, 0, 0),
        'right_arm': (0.35, 0, 0.75, 0, 0, 0),
        'left_arm': (0.55, 0, -0.75, 0, 0, 0),
        'right_forearm': (0.25, 0, 0, 0, 0, 0),
        'left_forearm': (0.15, 0, 0, 0, 0, 0),
        'right_hand': (-0.4, 0, 0, 0, 0, 0),
        'left_hand': (-0.4, 0, 0, 0, 0, 0),
        'hair': (-0.2, 0, 0, 0, 0, 0),
        'tail1': (0.1, 0, 0, 0, 0, 0),
        'tail2': (0.15, 0, 0, 0, 0, 0),
    },
    # lunge: both arms snap forward, jaw gapes, claws curl
    'attack': {
        'body': (0.25, 0, 0, 0, 0, -2.0),
        'head': (0.12, 0, -0.1, 0, 0, 0),
        'jaw': (0.12, 0, 0, 0, 3.5, -0.5),
        'right_arm': (-0.45, -0.2, 0, 0, 0, 0),
        'left_arm': (0.1, -0.15, 0, 0, 0, 0),
        'right_forearm': (0.2, 0, 0, 0, 0, 0),
        'left_forearm': (0.1, 0, 0, 0, 0, 0),
        'right_hand': (-0.3, 0, 0, 0, 0, 0),
        'left_hand': (-0.2, 0, 0, 0, 0, 0),
        'tail1': (-0.2, 0, 0, 0, 0, 0),
        'tail2': (-0.15, 0, 0, 0, 0, 0),
        'tail3': (-0.1, 0, 0, 0, 0, 0),
    },
}

ANIM_NOTES = """placeholder"""
