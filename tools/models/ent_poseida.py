"""Lucia, la Poseida -- possessed nine-year-old girl of Casa Morales (DEAD LINE).

Authored at 2x texel density (model.scale = 0.5) with rig.Rig absolute coordinates:
+Y down, ground at y = 24, the creature faces -Z, right_* parts on -X. Real height 1.5 blocks
(top of the hair at y = -24).

Silhouette: an oversized cracked-plaster head (18 x 18 face) on a tiny body, cocked at a broken
angle inside a tangled black mane; a grin torn ear to ear (the jaw bone hinges along the cheek
tears); white glowing eyes sunk in real recessed sockets; spider arms so long the clawed fingers
hang past the knees; a filthy ruffled Victorian nightgown flared into a bell with a shredded hem;
thin bruised knock-kneed legs and dirty bare pigeon-toed feet.

Rig: base (pelvis) -> body -> neck -> head -> jaw; arms with forearm / hand / 5 finger bones;
legs with shin / foot; skirt hangs from base. Every cube is authored in its bone's unrotated frame.
"""
import math

from mcmodel import Model, fbm, vnoise, hash3, face_light, pick
from rig import Rig
from paint import hx, mix, scale


def pal(*h):
    return [hx(c) for c in h]


# ------------------------------------------------------------------ palettes (dark -> light, hue shifted)
SKIN = pal('#0f0c13', '#1f1a26', '#332d3b', '#4a4452', '#645e6b', '#827c86', '#a19ba2', '#beb9bb', '#d8d4d0', '#ece8e1')
GOWN = pal('#1f1b19', '#332e2a', '#4b443e', '#665e55', '#82796e', '#9f9588', '#bab1a2', '#d1c9b9', '#e4ddcd', '#f2ecdf')
LACE = pal('#4a453f', '#77716a', '#a39d92', '#cbc4b7', '#e9e3d6', '#faf6ec')
BLOOD = pal('#140103', '#280306', '#41060a', '#5e0a10', '#7c1016', '#9a1b1f')
BILE = pal('#050504', '#0c0b08', '#16140d', '#221f14', '#302c1c')
HAIR = pal('#020203', '#060508', '#0b0a0e', '#121016', '#1a171f', '#24202b', '#322d3b', '#463f52')
MOUTH = pal('#020102', '#0a0304', '#170508', '#2a090e', '#420f16', '#5d1820', '#7a242b')
TEETH = pal('#2f2718', '#4f432b', '#766540', '#9d8a58', '#bfae76', '#dacd98', '#ece4bc')
NAIL = pal('#0e0b09', '#1d1712', '#30271e', '#463a2c')
DIRT = pal('#120d09', '#211810', '#322519', '#453523', '#5a4730')
RIBBON = pal('#1e0306', '#3a070c', '#5a0d14', '#7c161c', '#9c2428')
BRUISE = pal('#2a1a30', '#3e2a46', '#56405c', '#6d6250', '#7d7a62')
VEIN = hx('#170b1b')
VEIN2 = hx('#2e1a33')


def clamp(v, a=0.0, b=1.0):
    return a if v < a else b if v > b else v


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
    """Authoring-space position of the texel (bone abs pivot + local): ignores rest rotations."""
    lx, ly, lz = local(ctx)
    a = ctx.bone.abs
    return a[0] + lx, a[1] + ly, a[2] + lz


def edge(ctx):
    return min(ctx.i, ctx.j, ctx.w - 1 - ctx.i, ctx.h - 1 - ctx.j)


def flat(ctx):
    return 0 in ctx.cube.size


def is_side(ctx):
    return ctx.face not in ('top', 'bottom')


def tag(ctx):
    return ctx.cube.name or ''


def uv2(ctx, p):
    """2D painting coordinates on the face plane (authoring space)."""
    x, y, z = p
    if ctx.face in ('front', 'back'):
        return x, y
    if ctx.face in ('west', 'east'):
        return z, y
    return x, z


def worley(u, v, seed):
    xi, yi = math.floor(u), math.floor(v)
    d1 = d2 = 9.0
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            cx, cy = xi + dx, yi + dy
            px = cx + 0.15 + 0.7 * hash3(cx, cy, 0, seed)
            py = cy + 0.15 + 0.7 * hash3(cx, cy, 1, seed)
            d = math.hypot(px - u, py - v)
            if d < d1:
                d1, d2 = d, d1
            elif d < d2:
                d2 = d
    return d1, d2


def crack(ctx, p, cell=5.5, seed=3, width=0.1, density=0.52):
    """Plaster crack network: 1 = crack line, 2 = chipped lit lip below it, 0 none."""
    if flat(ctx):
        return 0
    u, v = uv2(ctx, p)
    if fbm(u * 0.11 + 7, v * 0.11, ord(ctx.face[0]) * 0.3, 2, seed + 40) < density:
        return 0
    d1, d2 = worley(u / cell, v / cell, seed)
    if d2 - d1 < width:
        return 1
    d1b, d2b = worley(u / cell, (v - 1) / cell, seed)
    if d2b - d1b < width:
        return 2
    return 0


def veins(ctx, p, cell=2.6, seed=11, width=0.09):
    u, v = uv2(ctx, p)
    d1, d2 = worley(u / cell, v / cell, seed)
    return d2 - d1 < width


# ------------------------------------------------------------------ skin
LIMB = ('_arm', '_forearm', '_hand', '_leg', '_shin', '_foot', '_finger', '_thumb')


def skin_value(ctx, p, base=0.62):
    v = base + face_light(ctx) * 1.15
    if not flat(ctx) and edge(ctx) == 0:
        v -= 0.07
    x, y, z = p
    v += (vnoise(x * 0.12, y * 0.12, z * 0.12, 5) - 0.5) * 0.12
    return v


def vein_mask(ctx, p):
    """0..1 how strongly the black spider-web veins show here."""
    n = ctx.bone.name
    x, y, z = p
    if n == 'neck':
        return 0.9
    if n.endswith('_forearm'):
        return 0.55 + 0.4 * clamp((y - 6) / 9)
    if n.endswith('_arm'):
        return 0.35
    if n.endswith('_hand'):
        return 0.6
    if n.endswith('_shin'):
        return 0.35
    if n.endswith('_leg'):
        return 0.25
    if n == 'body':
        return 0.5
    return 0.0


def bruise_at(ctx, p):
    """Hand-placed bruises: finger marks round the neck, grip marks on the arms, battered knees."""
    n = ctx.bone.name
    x, y, z = p
    if n == 'neck' and ctx.face in ('west', 'east', 'front'):
        # four finger-shaped blotches on each side of the throat
        k = (z + 2) / 1.3 if ctx.face != 'front' else (abs(x) + 1.0)
        if ctx.face == 'front':
            return 2 if abs(x) > 1 and -5 < y < -3 else 0
        if int(k) % 2 == 0 and -5.5 < y < -2.5:
            return 2 if -5 < y < -3 else 1
        return 0
    if n.endswith('_arm') and 1.5 < y < 5 and ctx.face in ('front', 'west', 'east'):
        u, _ = uv2(ctx, p)
        return 2 if int(math.floor(u * 0.9 + 5)) % 2 == 0 else 1
    if n.endswith('_shin') and y < 18 and ctx.face in ('front', 'west', 'east'):
        b = fbm(x * 0.4 + 3, y * 0.4, z * 0.4, 2, 61)
        return 2 if b > 0.6 else (1 if b > 0.53 else 0)
    if n.endswith('_leg') and ctx.face in ('front', 'west', 'east'):
        b = fbm(x * 0.35, y * 0.35 + 9, z * 0.35, 2, 63)
        return 2 if b > 0.62 else (1 if b > 0.56 else 0)
    if n.endswith('_forearm') and ctx.face == 'west' and 10 < y < 13:
        return 1
    return 0


def dirt_amount(ctx, p):
    n = ctx.bone.name
    x, y, z = p
    if n.endswith('_foot'):
        return 0.55 + 0.4 * clamp((y - 22) / 2)
    if n.endswith('_shin'):
        return clamp((y - 17) / 5) * 0.6
    if n.endswith('_hand') or '_finger' in n or '_thumb' in n:
        return 0.35
    if n.endswith('_forearm'):
        return clamp((y - 11) / 4) * 0.3
    return 0.0


def skin_mat(ctx):
    p = dpos(ctx)
    x, y, z = p
    n = ctx.bone.name
    v = skin_value(ctx, p)
    limb = n.endswith(LIMB)
    if limb and is_side(ctx) and not flat(ctx):
        v -= ctx.t * 0.06
    if n == 'neck':
        v -= 0.1  # in the shadow of the huge head
    c = pick(SKIN, v)
    vm = vein_mask(ctx, p)
    if vm > 0 and not flat(ctx) and veins(ctx, p) and fbm(x * 0.2, y * 0.2, z * 0.2, 2, 13) < vm:
        c = mix(c, VEIN, 0.75)
    else:
        k = crack(ctx, p)
        if k == 1:
            c = pick(SKIN, v - 0.32)
        elif k == 2:
            c = pick(SKIN, v + 0.1)
    b = bruise_at(ctx, p)
    if b:
        c = mix(c, BRUISE[1] if b == 2 else BRUISE[3], 0.6 if b == 2 else 0.45)
    d = dirt_amount(ctx, p)
    if d > 0:
        dn = fbm(x * 0.5, y * 0.5, z * 0.5, 2, 71)
        if dn < d:
            c = mix(c, pick(DIRT, v * 0.7), 0.75)
    return c


def knob_mat(ctx):
    """Skin stretched over sharp bone (elbows, knees): pale polished tip, bruised base."""
    p = dpos(ctx)
    v = skin_value(ctx, p, 0.66)
    if ctx.face == 'top' or (is_side(ctx) and ctx.j == 0):
        v += 0.1
    c = pick(SKIN, v)
    if is_side(ctx) and ctx.j == ctx.h - 1:
        c = mix(c, BRUISE[1], 0.5)
    d = dirt_amount(ctx, p)
    if d > 0.3:
        c = mix(c, DIRT[2], 0.4)
    return c


def finger_mat(ctx):
    """Long grey finger, dark knuckle creases, broken black nail at the tip."""
    lx, ly, lz = local(ctx)
    L = ctx.cube.size[1]
    p = dpos(ctx)
    v = skin_value(ctx, p, 0.6)
    if ly > L - 2.0:
        if ctx.face == 'bottom':
            return NAIL[0]
        return pick(NAIL, 0.4 + face_light(ctx) + (0.3 if ctx.face in ('front', 'east', 'west') and ly > L - 1 else 0))
    if int(ly) in (2, 4) and is_side(ctx):
        v -= 0.16
    v -= ly / L * 0.12
    c = pick(SKIN, v)
    if ly > L - 3.5:
        c = mix(c, DIRT[2], 0.55)
    return c


def foot_mat(ctx):
    """Bare dirty foot: grey skin, black soles, toes with dark nails on the front."""
    p = dpos(ctx)
    x, y, z = p
    if ctx.face == 'bottom':
        return pick(DIRT, 0.2 + hash3(ctx.i, ctx.j, 0, 81) * 0.25)
    lx, ly, lz = local(ctx)
    c = skin_mat(ctx)
    toe_zone = (lz - ctx.cube.origin[2]) < 2.2
    if ctx.face == 'front':
        # four toes: dark gaps between, nails on the top row
        if ctx.i % 2 == 1 and ctx.i < ctx.w - 1:
            return pick(DIRT, 0.3)
        if ctx.j == 0:
            return NAIL[2]
        return mix(c, DIRT[3], 0.5)
    if ctx.face == 'top' and toe_zone:
        if ctx.i % 2 == 1 and ctx.i < ctx.w - 1:
            return pick(DIRT, 0.35)
        if (lz - ctx.cube.origin[2]) < 1.0:
            return NAIL[2]
    if is_side(ctx) and ctx.j >= ctx.h - 1:
        return mix(c, DIRT[1], 0.7)
    return c


# ------------------------------------------------------------------ the face (one 18 x 18 pixel-art map)
# Covers the whole front of the head: col = x + 9 (x -9..9), row = y + 23 (y -23..-5).
# Painted on every front face of the head / jaw cubes by position, so the recessed sockets, nose,
# cheek plate and jaw all share one coherent drawing.
FPAL = {
    '0': SKIN[0], '1': SKIN[1], '2': SKIN[2], '3': SKIN[3], '4': SKIN[4], '5': SKIN[5], '6': SKIN[6],
    '7': SKIN[7], '8': SKIN[8], '9': SKIN[9],
    'K': hx('#050307'), 'k': hx('#1d1220'), 'q': hx('#3a2840'), 'Q': hx('#54405a'),
    'W': hx('#f6f4ee'), 'w': hx('#d9d6d0'), 'v': hx('#aaa6a6'), 'e': hx('#c46a6c'),
    'r': hx('#86141c'), 'R': hx('#b52a30'),
    'G': MOUTH[0], 'g': MOUTH[3], 'h': MOUTH[5],
    'T': TEETH[6], 't': TEETH[4], 'y': TEETH[2], 'Y': TEETH[1],
    'L': hx('#6f5a66'), 'l': hx('#4c3a48'), 'x': BLOOD[4], 'X': BLOOD[1], 'b': BLOOD[3], 'B': BLOOD[2],
    'V': VEIN, 'u': VEIN2,
}

FACE_BASE = [
    # 012345678901234567
    "567888888888888765",  # r0  y-23 forehead (under the fringe)
    "678888899888888876",  # r1
    "678888888888888876",  # r2
    "567777777777777765",  # r3  brow line (bottom of the forehead plate)
    "4.......76.......4",  # r4  socket band: cols 1-7 / 10-16 recessed pockets
    "4.......76.......4",  # r5
    "4.......76.......4",  # r6
    "4.......66.......4",  # r7
    "456666677766666654",  # r8  cheek plate (nose = cols 8-9, rows 8-9)
    "456677776677776654",  # r9
    "456677777777776654",  # r10
    "4566666666666666654"[:18],  # r11
    "455555555555555554",  # r12
    "-45666666666666654"[:18],  # r13 jaw (cols 1-16)
    "-45667777777766654"[:18],  # r14
    "-45677788887776654"[:18],  # r15
    "-34566777777665443"[:18],  # r16
    "-23455666666554332"[:18],  # r17
]

EYE = [
    # 7 wide: cols 1-7 (right eye, viewer's left); mirrored for the left eye
    "KrvwwrK",  # r4 top of the white in the lid's shadow
    "rWWWWWr",  # r5
    "rWWWWWr",  # r6
    "KrWWWrK",  # r7
    "kKRrRKk",  # r8 inflamed red lower rim
    "qkkkkkq",  # r9 dark circles
    "Qqqqqq4",  # r10
]

MOUTH_ART = [
    # 012345678901234567
    "ll..............ll",  # r9  corners of the grin climbing the cheeks
    "xGlLLlLLllLLlLLlGx",  # r10 cracked upper lip
    "xGGyyGyyGyyGyyGGGx",  # r11 upper teeth roots + black gums
    ".gtTGGTGGTGGTGGtg.",  # r12 upper fangs (tips)
    ".lGGTGGTGGTGGTGGl.",  # r13 lower fangs (tips)  -- jaw starts here
    "..lGyyGyyGyyGyyl..",  # r14 lower roots
    "..LlxLLlbLLlLxlL..",  # r15 cracked lower lip, blood
]

# hand-placed details: (row, col, char)
FACE_MARKS = [
    # three self-inflicted scratches over the left eye (viewer's right)
    (0, 14, 'X'), (1, 13, 'x'), (2, 12, 'x'), (3, 11, 'b'),
    (0, 16, 'X'), (1, 15, 'x'), (2, 14, 'x'), (3, 13, 'b'),
    (1, 17, 'X'), (2, 16, 'x'), (3, 15, 'x'),
    # spider veins from the outer eye corners over the temples
    (2, 0, 'V'), (3, 0, 'V'), (4, 0, 'u'), (1, 1, 'u'), (2, 2, 'u'),
    (5, 17, 'V'), (6, 17, 'u'), (3, 17, 'u'), (8, 16, 'u'), (9, 17, 'V'),
    (8, 0, 'u'), (9, 0, 'V'), (10, 1, 'u'),
    # veins from the mouth corners down the jaw
    (13, 1, 'V'), (14, 2, 'V'), (15, 2, 'u'), (16, 3, 'V'), (13, 16, 'V'), (14, 15, 'V'), (16, 14, 'u'),
    (17, 4, 'u'), (17, 13, 'V'),
    # blood running from the lower lip down the chin
    (16, 8, 'b'), (17, 8, 'B'), (16, 5, 'b'), (16, 12, 'b'), (17, 12, 'b'), (16, 13, 'B'),
    # blood tear from the right eye
    (10, 3, 'b'), (11, 3, 'B'),
]

NOSE_FRONT = ["76", "54"]  # nose cube front (cols 8-9, rows 8-9)


def build_face():
    g = [list(r) for r in FACE_BASE]
    for j, row in enumerate(EYE):
        for i, ch in enumerate(row):
            g[4 + j][1 + i] = ch
            g[4 + j][16 - i] = ch
    for j, row in enumerate(MOUTH_ART):
        for i, ch in enumerate(row):
            if ch != '.':
                g[9 + j][i] = ch
    for r_, c_, ch in FACE_MARKS:
        g[r_][c_] = ch
    # a red vein in each white
    g[5][2] = 'e'
    g[6][14] = 'e'
    return g


FACE = build_face()


def face_px(x, y):
    c = int(math.floor(x + 9))
    r = int(math.floor(y + 23))
    if 0 <= r < 18 and 0 <= c < 18:
        ch = FACE[r][c]
        return FPAL.get(ch)
    return None


def in_pocket(x, y):
    return -19 <= y <= -15 and (-8 <= x <= -1 or 1 <= x <= 8)


def head_mat(ctx):
    """Cranium / face plates / jaw: the face map on the front, plaster skin elsewhere,
    dark pocket walls, the ear-to-ear tear on the sides, palate + tongue inside the mouth."""
    p = dpos(ctx)
    x, y, z = p
    t = tag(ctx)
    f = ctx.face
    if f == 'front':
        if t == 'nose':
            r = int(math.floor(y + 23)) - 8
            c = int(math.floor(x + 9)) - 8
            if 0 <= r < 2 and 0 <= c < 2:
                return FPAL[NOSE_FRONT[r][c]]
        c = face_px(x, y)
        if c is not None:
            return c
        return skin_mat(ctx)
    if t == 'nose' and f == 'bottom':
        return FPAL['K'] if ctx.j == 0 else FPAL['q']
    # walls of the eye pockets
    if t in ('brow', 'cheek', 'bridge', 'temple') and in_pocket(x, y) or (t == 'bridge' and f in ('west', 'east')) \
            or (t == 'temple' and f in ('west', 'east') and abs(x) < 8.6):
        return FPAL['k'] if f != 'top' else FPAL['K']
    if t == 'cranium' and f == 'bottom':
        # palate: black gums at the front, raw red roof further in
        dz = z + 8
        if dz < 1.2:
            return MOUTH[1]
        return pick(MOUTH, 0.35 + face_light(ctx) + (vnoise(x * 0.6, 0, z * 0.6, 91) - 0.5) * 0.25)
    if t == 'jaw' and f == 'top':
        if abs(x) > 6.5 or z < -8:
            return MOUTH[1]
        return pick(MOUTH, 0.55 + (vnoise(x * 0.5, 1, z * 0.5, 93) - 0.5) * 0.3)
    if f in ('west', 'east'):
        k = cheek_tear(t, y, z)
        if k:
            return k
    if t == 'jaw' and f == 'bottom':
        c = skin_mat(ctx)
        return scale(c, 0.75)
    return skin_mat(ctx)


def tear_y(z):
    """Centre line of the ear-to-ear tear along the side of the head (authoring y for a given z)."""
    if z < -3:
        return -10.0
    return -10.0 - (z + 3) * 1.1


def cheek_tear(t, y, z):
    if z > 0.5:
        return None
    yc = tear_y(z)
    d = y - yc
    if t == 'jaw':
        if z > -2.5:
            return None
        if d < 1.0:
            return MOUTH[1]
        if d < 2.0:
            return BLOOD[4]
        if d < 3.0 and int(z * 3) % 2 == 0:
            return BLOOD[3]
        return None
    if -1.0 < d <= 0.0 and z > -3:
        return MOUTH[1]
    if d > -1.0:
        return BLOOD[4] if d > -0.0 or z < -3 else MOUTH[1]
    if d > -2.0:
        return BLOOD[3] if int(z * 2) % 2 == 0 else BLOOD[4]
    return None


def throat_mat(ctx):
    return MOUTH[0] if ctx.face != 'top' else MOUTH[2]


def teeth_mat(grow):
    """Small yellowed needle teeth on a zero-thickness plane (revealed when the jaw drops).
    grow=+1: teeth hang from the top edge; -1: teeth stand up from the bottom edge."""
    def f(ctx):
        lx, ly, lz = local(ctx)
        c = ctx.cube
        col = int(math.floor(lx - c.origin[0]))
        depth = (ly - c.origin[1]) if grow > 0 else (c.origin[1] + c.size[1] - ly)
        h = hash3(col, 0, 0, 97 + grow)
        L = 1.0 + h * 1.4
        if col % 2 == 1:
            return MOUTH[1] if depth < 0.8 else None
        if depth > L:
            return None
        if depth < 0.7:
            return MOUTH[2]
        return pick(TEETH, 0.85 - (depth / L) * 0.15 - (0.35 if h > 0.8 else 0))
    return f


# ------------------------------------------------------------------ hair
def hair_v(ctx, col, ly_frac, seed=0):
    strand = hash3(col // 2, seed, 0, 101)
    v = 0.28 + strand * 0.34 + face_light(ctx) * 0.9
    if col % 3 == 0:
        v -= 0.12
    v -= ly_frac * 0.1
    return v


def hair_color(ctx, p, v, col):
    x, y, z = p
    # matted with dried blood in clumps
    if fbm(x * 0.25, y * 0.18, z * 0.25, 2, 107) > 0.66 and col % 4 != 0:
        return pick(BLOOD, v * 0.6 + 0.1)
    return pick(HAIR, v)


def hair_cap_mat(ctx):
    """Shell over the cranium: open over the face, sideburn cut-outs to show the cheek tears."""
    p = dpos(ctx)
    x, y, z = p
    f = ctx.face
    if f in ('bottom', 'front'):
        return None
    if f in ('west', 'east'):
        lim = -16.5 + hash3(math.floor(z), 0, 0, 111) * 3.0
        if z < -3.5 and y > lim:
            return None
        if z < -6.5 and y > -20:
            return None
        col = int(math.floor(z * 1.0)) + 40
    elif f == 'top':
        col = int(math.floor(x)) + 20
    else:
        col = int(math.floor(x)) + 60
    v = hair_v(ctx, col, 0, 3)
    return hair_color(ctx, p, v, col)


def hang_mat(seed, ragged=0.45, axis='x'):
    """Hanging hair curtain / lock: per-strand values, ragged free ends toward +y."""
    def f(ctx):
        c = ctx.cube
        lx, ly, lz = local(ctx)
        if ctx.face == 'bottom':
            return None
        if ctx.face == 'top':
            col = ctx.i + 30
            frac = 0.0
        else:
            col = int(math.floor(lx if ctx.face in ('front', 'back') else lz)) + (0 if ctx.face in ('front', 'back') else 50)
            frac = (ly - c.origin[1]) / c.size[1]
            lim = 1.0 - ragged * hash3(col, 0, 0, seed)
            if frac > lim:
                return None
            if frac > lim - 0.08:
                return pick(HAIR, 0.55)  # split ends catch the light
        v = hair_v(ctx, col, frac, seed)
        if ctx.face == 'front' and ctx.bone.name == 'hair_back':
            v -= 0.18  # underside of the curtain, against the back
        return hair_color(ctx, dpos(ctx), v, col)
    return f


def strand_plane(paths, seed):
    """Zero-thickness plane with hand-drawn wavy 1-px strands. paths: list of (x_start, dx_per_row, length)."""
    def f(ctx):
        lx, ly, lz = local(ctx)
        c = ctx.cube
        i = int(math.floor(lx - c.origin[0]))
        j = int(math.floor(ly - c.origin[1]))
        for k, (x0, slope, L) in enumerate(paths):
            if j >= L:
                continue
            xs = int(round(x0 + slope * j + 0.6 * math.sin(j * 0.7 + k)))
            if i == xs:
                v = 0.3 + hash3(k, j // 3, 0, seed) * 0.3 + (0.2 if j % 5 == 0 else 0)
                if j > L - 3 and k % 2 == 0:
                    return pick(BLOOD, 0.5)
                return pick(HAIR, v)
        return None
    return f


# ------------------------------------------------------------------ the nightgown
def gown_value(ctx, p, base=0.66):
    x, y, z = p
    v = base + face_light(ctx) * 1.1
    if not flat(ctx) and edge(ctx) == 0:
        v -= 0.06
    return v


def stain(ctx, p):
    """Blood + black bile vomited down the front: returns a colour or None."""
    x, y, z = p
    if ctx.face != 'front' and not (ctx.face == 'top' and z < -3):
        return None
    col = math.floor(x)
    # main streak: wide under the chin, narrowing and dripping lower down
    w = 3.2 - (y + 3) * 0.1 + (vnoise(col * 0.7, 0, 0, 121) - 0.5) * 1.6
    xc = 0.6 + math.sin(y * 0.25) * 0.8
    if abs(x - xc) < w and y < 9:
        core = abs(x - xc) < w * 0.45
        return BILE[1] if core and (y < 2 or hash3(col, 0, 0, 123) > 0.5) else BLOOD[3] if core else BLOOD[4]
    # drips running from the streak down the skirt
    L = hash3(col, 0, 0, 125)
    if abs(x - 0.5) < 6 and L > 0.45 and y < 9 + (L - 0.45) * 22:
        return BLOOD[3] if hash3(col, 1, 0, 125) > 0.4 else BILE[2]
    return None


def handprint(x, y, cx, cy):
    """A small bloody handprint (5 x 6) on the skirt, palm + four fingers."""
    i, j = int(math.floor(x - cx)), int(math.floor(y - cy))
    art = [
        "x.x.x",
        "x.x.x.",
        "xxxxx",
        "xxxx.",
        ".xxx.",
    ]
    if 0 <= j < len(art) and 0 <= i < len(art[j]):
        return art[j][i] == 'x'
    return False


def gown_mat(ctx):
    p = dpos(ctx)
    x, y, z = p
    t = tag(ctx)
    f = ctx.face
    v = gown_value(ctx, p)
    # pin-tucked bodice / vertical folds
    if is_side(ctx):
        u = x if f in ('front', 'back') else z
        k = math.floor(u) % 3
        v += (-0.07, 0.05, 0.0)[k]
    c = pick(GOWN, v)
    # filth: grime creeping up from the hem, grey sweat stains
    g = fbm(x * 0.3, y * 0.3, z * 0.3, 2, 131)
    if g > 0.62:
        c = mix(c, hx('#6b5b41'), 0.45)
    s = stain(ctx, p)
    if s is not None:
        c = s
    if t == 'bodice' and f == 'front' and abs(x - 0.5) < 0.6 and int(y) % 2 == 0 and -2 < y < 5 and s is None:
        c = LACE[4]  # pearl buttons
    return c


def skirt_mat(ctx):
    """Ruffled tier of the bell skirt: shredded hem (alpha), lace edge, folds, blood and grime."""
    p = dpos(ctx)
    x, y, z = p
    f = ctx.face
    c_ = ctx.cube
    if f == 'bottom':
        return None
    if f == 'top':
        # the ruffle shelf of a lower tier: lace frill
        v = 0.72 + ((ctx.i + ctx.j) % 2) * 0.08
        return pick(LACE, v)
    u = x if f in ('front', 'back') else z
    col = math.floor(u)
    lx, ly, lz = local(ctx)
    depth = (ly - c_.origin[1])
    hgt = c_.size[1]
    torn = tag(ctx) == 'hem'
    if torn:
        lim = hgt * (0.45 + 0.55 * hash3(col // 1, 0, ord(f[0]), 141))
        if hash3(col, 1, 0, 143) > 0.82:
            lim = hgt * 0.25  # a deep rip showing the legs
        if depth > lim:
            return None
    v = gown_value(ctx, p, 0.64)
    k = col % 4
    v += (-0.1, 0.04, 0.07, 0.0)[k]
    v -= (depth / hgt) * 0.1
    if f == 'back':
        v -= 0.04
    c = pick(GOWN, v)
    # lace hem line at the bottom of each tier
    if not torn and depth > hgt - 1.0:
        c = pick(LACE, 0.5 + (col % 2) * 0.3)
    g = fbm(x * 0.28, y * 0.2, z * 0.28, 2, 147) + (y - 8) * 0.03
    if g > 0.68:
        c = mix(c, hx('#5c4b33'), 0.5)
    if torn and depth > lim - 1.0:
        c = mix(c, DIRT[2], 0.6)
    s = stain(ctx, p)
    if s is not None:
        c = s
    if f == 'front' and handprint(x, y, -6, 13):
        c = BLOOD[3]
    return c


def sleeve_mat(ctx):
    p = dpos(ctx)
    x, y, z = p
    f = ctx.face
    if f == 'bottom':
        return GOWN[1]
    lx, ly, lz = local(ctx)
    depth = ly - ctx.cube.origin[1]
    v = gown_value(ctx, p, 0.68)
    if is_side(ctx):
        u = x if f in ('front', 'back') else z
        v += (-0.08, 0.06)[math.floor(u * 0.7) % 2]  # gathered puff
        if depth > ctx.cube.size[1] - 1:
            return pick(LACE, 0.6 + (ctx.i % 2) * 0.25) if ctx.i % 3 != 2 else None
    c = pick(GOWN, v)
    if fbm(x * 0.3, y * 0.3, z * 0.3, 2, 151) > 0.64:
        c = mix(c, hx('#6b5b41'), 0.45)
    return c


def lace_mat(ctx):
    """High lace collar: scalloped top edge with holes."""
    f = ctx.face
    if f in ('bottom', 'top'):
        return None if f == 'top' else LACE[1]
    j, i = ctx.j, ctx.i
    if j == 0 and i % 2 == 1:
        return None
    if j == 1 and i % 4 == 2:
        return None
    p = dpos(ctx)
    v = 0.62 + face_light(ctx) + (0.12 if (i + j) % 2 == 0 else 0)
    c = pick(LACE, v)
    if f == 'front' and abs(p[0] - 0.5) < 3 and j >= 1:
        c = BLOOD[3] if hash3(i, j, 0, 161) > 0.4 else BILE[2]
    return c


def ribbon_mat(ctx):
    v = 0.5 + face_light(ctx) + (0.15 if ctx.j == 0 else 0)
    return pick(RIBBON, v)


def petticoat_mat(ctx):
    return pick(GOWN, 0.18 + face_light(ctx) * 0.5)


DEFAULT_MAT = skin_mat
FOCUS = 'head'


# ------------------------------------------------------------------ build
def build():
    r = Rig()

    def bone(name, pivot, parent=None, rot=(0, 0, 0), mat=None):
        b = r.bone(name, pivot, parent, rot, mat)
        b.abs = r.abs_pivot[name]
        return b

    def box(b, frm, size, mat=None, inflate=0.0, decals=None, name=None):
        c = r.box(b, frm, size, mat=mat, inflate=inflate, decals=decals)
        c.name = name
        return c

    # ---------------- base (pelvis) + legs
    bone('base', (0, 8, 0))
    box('base', (-5.5, 4, -3), (11, 6, 6), mat=petticoat_mat)
    for side, sx in (('right', -1), ('left', 1)):
        leg = bone(f'{side}_leg', (3 * sx, 8, 0), 'base', rot=(-3 if sx < 0 else 4, 0, 5 * sx), mat=skin_mat)
        box(leg.name, (3 * sx - 2.5, 7, -2.5), (5, 8, 5))
        shin = bone(f'{side}_shin', (3 * sx, 15, 0), leg.name, rot=(4 if sx < 0 else -2, 0, -9 * sx), mat=skin_mat)
        box(shin.name, (3 * sx - 2, 14.2, -3.4), (4, 2, 2), mat=knob_mat)
        box(shin.name, (3 * sx - 2, 15, -2), (4, 7, 4))
        foot = bone(f'{side}_foot', (3 * sx, 22, 0), shin.name, rot=(0, -18 if sx < 0 else 6, 0), mat=foot_mat)
        box(foot.name, (3 * sx - 2, 22, -6), (4, 2, 8))

    # ---------------- skirt (three ruffled tiers + shredded hem)
    bone('skirt', (0, 4, 0), 'base', mat=skirt_mat)
    box('skirt', (-7, 4, -4.5), (14, 5, 9))
    box('skirt', (-8, 9, -5.5), (16, 4, 11))
    box('skirt', (-9, 13, -6.5), (18, 6, 13), name='hem')

    # ---------------- torso
    bone('body', (0, 7, 0), 'base', rot=(7, 0, 0), mat=gown_mat)
    box('body', (-6, -3, -3.5), (12, 11, 7), name='bodice')
    box('body', (-4.5, -4.5, -3.2), (9, 3, 7), mat=lace_mat, inflate=0.3)
    box('body', (-2, -1.6, -4.3), (4, 2, 1), mat=ribbon_mat)

    # ---------------- neck + head
    bone('neck', (0, -2, 0.5), 'body', rot=(-4, 0, 0), mat=skin_mat)
    box('neck', (-2.5, -7, -2), (5, 7, 5))
    bone('head', (0, -7, 1), 'neck', rot=(4, 0, -16), mat=head_mat)
    box('head', (-9, -23, -8), (18, 13, 15), name='cranium')
    box('head', (-9, -23, -9), (18, 4, 1), name='brow')
    box('head', (-9, -15, -9), (18, 5, 1), name='cheek')
    box('head', (-9, -19, -9), (1, 4, 1), name='temple')
    box('head', (8, -19, -9), (1, 4, 1), name='temple')
    box('head', (-1, -19, -9), (2, 4, 1), name='bridge')
    box('head', (-1, -15, -10), (2, 2, 1), name='nose')
    box('head', (-6, -10, -1), (12, 4, 3), mat=throat_mat)
    box('head', (-8, -10, -8.5), (16, 2, 0), mat=teeth_mat(1))
    # hair cap (shell) + fringe strands over the forehead and the right eye
    box('head', (-9, -23, -8), (18, 13, 15), mat=hair_cap_mat, inflate=1.0)
    box('head', (-9, -24, -9.6), (8, 13, 0), mat=strand_plane([(1, 0.25, 12), (3, 0.35, 10), (5, 0.1, 6), (0, 0.05, 9)], 171))
    box('head', (1, -24, -9.6), (8, 6, 0), mat=strand_plane([(6, -0.4, 5), (2, 0.2, 3), (4, -0.1, 4)], 173))

    bone('jaw', (0, -10, 1), 'head', mat=head_mat)
    box('jaw', (-8, -10, -9), (16, 5, 10), name='jaw')
    box('jaw', (-7, -12, -8.5), (14, 2, 0), mat=teeth_mat(-1))

    # long tangled hair: back curtain + two side locks hanging over the shoulders
    bone('hair_back', (0, -17, 7.5), 'head', rot=(-6, 0, 14), mat=hang_mat(181, 0.5))
    box('hair_back', (-10, -17, 6.5), (20, 24, 3))
    for side, sx in (('right', -1), ('left', 1)):
        hl = bone(f'hair_{side}', (9.5 * sx, -16, -1), 'head', rot=(0, 0, 14 + 8 * sx), mat=hang_mat(185 + sx, 0.4))
        box(hl.name, (9.5 * sx - 2, -16, -4), (4, 20, 5))

    # ---------------- arms: puffed sleeves, sharp elbows, spider hands
    for side, sx in (('right', -1), ('left', 1)):
        sh_y = -1 if sx > 0 else 0  # right shoulder dropped
        ax = 6.8 * sx
        arm = bone(f'{side}_arm', (ax, sh_y, 0.5), 'body', rot=(-12, 0, -6 * sx), mat=skin_mat)
        box(arm.name, (ax - 2, sh_y - 1, -1.5), (4, 8, 4))
        box(arm.name, (ax - 3, sh_y - 2.5, -2.5), (6, 5, 6), mat=sleeve_mat)
        fa = bone(f'{side}_forearm', (ax, sh_y + 7, 0.5), arm.name, rot=(-14, 0, 4 * sx), mat=skin_mat)
        box(fa.name, (ax - 1.5, sh_y + 7, -1), (3, 9, 3))
        box(fa.name, (ax - 1.5, sh_y + 6, 1.5), (3, 2, 2), mat=knob_mat)
        hy = sh_y + 16
        hd = bone(f'{side}_hand', (ax, hy, 0.5), fa.name, rot=(6, 0, 0), mat=skin_mat)
        box(hd.name, (ax - 1, hy, -1.5), (2, 4, 4))
        th = bone(f'{side}_thumb', (ax, hy + 1, -1.5), hd.name, rot=(-25, 0, -20 * sx), mat=finger_mat)
        box(th.name, (ax - 0.5, hy + 1, -2), (1, 4, 1))
        for k, zc in enumerate((-1.0, 0.0, 1.0, 2.0)):
            L = (7, 8, 7, 6)[k]
            fg = bone(f'{side}_finger{k + 1}', (ax, hy + 4, zc + 0.5), hd.name,
                      rot=((k - 1.5) * 7, 0, -26 * sx), mat=finger_mat)
            box(fg.name, (ax - 0.5, hy + 4, zc), (1, L, 1))

    m = Model('poseida', 256, 256, r.roots)
    m.scale = 0.5
    return m


POSES = {
    'attack': {
        'body': (0.35, 0, 0, 0, 0, 0),
        'head': (-0.35, 0, 0.2, 0, 0, 0),
        'jaw': (0.75, 0, 0, 0, 0, 0),
        'right_arm': (-1.6, 0, 0.25, 0, 0, 0),
        'left_arm': (-1.5, 0, -0.25, 0, 0, 0),
        'right_forearm': (-0.3, 0, 0, 0, 0, 0),
        'left_forearm': (-0.4, 0, 0, 0, 0, 0),
    },
    'scream': {
        'head': (-0.45, 0, 0.25, 0, 0, 0),
        'jaw': (0.9, 0, 0, 0, 0, 0),
        'right_arm': (0.3, 0, 0.5, 0, 0, 0),
        'left_arm': (0.3, 0, -0.5, 0, 0, 0),
    },
}

ANIM_NOTES = "todo"
