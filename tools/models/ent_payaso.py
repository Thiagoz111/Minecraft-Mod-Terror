"""Sonrisas -- the demonic circus clown of DEAD LINE (module key: payaso).

Authored at 2x texel density (model.scale = 0.5) with rig.Rig absolute coordinates:
+Y down, ground at y = 24, the creature faces -Z, right_* parts on -X.
Every cube is authored in its bone's *unrotated* frame; bone rotations fold the hunch.
The face is painted from one 2D face map in head-local design coordinates, so every
front-facing cube of the head (cranium, brows, cheeks, muzzle, jaw, lips, chin) shares the
same painting and the features line up across the stacked layers.
"""
import math

from mcmodel import Model, fbm, vnoise, hash3, face_light, pick
from rig import Rig
from paint import hx, mix, scale, edge


def pal(*h):
    return [hx(c) for c in h]


# ------------------------------------------------------------------ palettes (dark -> light)
PAINT = pal('#221e27', '#38333e', '#544e59', '#756f78', '#989198', '#bab4b4', '#d5d0c8', '#e9e5da', '#f8f6ec')
SKIN = pal('#0e100e', '#181b17', '#242822', '#32372e', '#41463b', '#52564a', '#64675a', '#78796a', '#8c8b79')
RED = pal('#120103', '#280306', '#45060a', '#680b10', '#8d1216', '#b21c1e', '#d3332a', '#ef5a3b', '#ff8a5c')
BLOOD = pal('#0e0102', '#1c0204', '#2c0507', '#3e080b', '#530c0f', '#6a1215')
VOID = hx('#020102')
SOCKET = pal('#070305', '#130a10', '#22121c', '#331b29')
PUPIL = hx('#fff4a6')
PUPIL_DIM = hx('#f2a51c')
HAIR = pal('#160302', '#2c0703', '#480d05', '#6b1607', '#90220a', '#b5340d', '#d64e13', '#ef7220', '#ff9f45')
PURPLE = pal('#09050c', '#130a19', '#1f1128', '#2c1838', '#3b2049', '#4b295b', '#5d336d', '#703f80')
MUSTARD = pal('#151004', '#271d07', '#3c2d0b', '#544010', '#6d5415', '#87691c', '#a08125')
RUFF_W = pal('#28252a', '#433f43', '#635e5f', '#87807e', '#a9a29c', '#c8c1b8', '#e0dacf', '#f1ede4')
GLOVE = pal('#27231f', '#403a34', '#5d564d', '#7c7367', '#9b9182', '#b8ad9b', '#d0c6b3', '#e4dcca')
CLAW = pal('#020102', '#070608', '#0f0d11', '#19161b', '#252128', '#38323b')
SHOE = pal('#100203', '#210406', '#38070a', '#560b10', '#761217', '#971a1e', '#b72827', '#d34232', '#ea6a4a')
SOLE = pal('#060506', '#0e0c0e', '#181518', '#252124', '#353034')
FELT = pal('#040305', '#09080b', '#110e14', '#1a161e', '#241f29', '#302936', '#3f3646')
TEETH = pal('#33291e', '#574a36', '#7d6d52', '#a39271', '#c5b791', '#e0d6b4', '#f3eed8')
GUM = pal('#0a0203', '#180407', '#2c080c', '#451014', '#62191d', '#80282a', '#9c3c3a')
BALLOON = pal('#250104', '#430209', '#69060f', '#930b17', '#bb1421', '#dc2a2f', '#f75348', '#ff9a86', '#ffe0d6')
STRING = pal('#2f2b27', '#524c45', '#7c756a', '#a69e90', '#c9c1b2')

HEAD_ABS = (0.0, 0.0, 0.0)  # set by build(): design-space pivot of the head
FZ = -19  # head-local z of the cranium's front face


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
    lx, ly, lz = local(ctx)
    a = ctx.bone.abs
    return a[0] + lx, a[1] + ly, a[2] + lz


def hpos(ctx):
    x, y, z = dpos(ctx)
    return x - HEAD_ABS[0], y - HEAD_ABS[1], z - HEAD_ABS[2]


def flat(ctx):
    return 0 in ctx.cube.size


def fl(v):
    return int(math.floor(v))


def light(ctx, k=1.0):
    return face_light(ctx) * k


def rim(ctx, v, amt=0.07):
    if not flat(ctx) and edge(ctx) == 0:
        return v - amt
    return v


def raster(points):
    """Hand-placed polyline -> set of integer texels (Bresenham)."""
    out = set()
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
        err = dx + dy
        x, y = x0, y0
        while True:
            out.add((x, y))
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy
    return out


def outline_of(inside, ix, iy):
    """inside(ix, iy)->bool. 2 = border texel, 1 = interior, 0 = outside."""
    if not inside(ix, iy):
        return 0
    for ox, oy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        if not inside(ix + ox, iy + oy):
            return 2
    return 1


# ------------------------------------------------------------------ the face map (head-local texels)
EYES = [  # centre x, centre y, radius x, radius y, pupil texel
    (-7.0, -9.4, 3.5, 3.0, (-7, -10)),
    (7.2, -9.2, 4.0, 3.5, (6, -10)),
]
DIAMOND = (5.2, 8.4, 6.0)  # half width, half height up, half height down


def in_diamond(ix, iy):
    x, y = ix + 0.5, iy + 0.5
    for cx, cy, _, _, _ in EYES:
        hw, hu, hd = DIAMOND
        hh = hu if y < cy else hd
        if abs(x - cx) / hw + abs(y - cy) / hh <= 1.0:
            return True
    return False


def grin_u(ax):
    return -2.4 - 0.026 * ax * ax


def grin_l(ax):
    return 3.4 - 0.062 * ax * ax


def in_grin(ix, iy):
    x, y = ix + 0.5, iy + 0.5
    ax = abs(x)
    if ax > 13.2:
        return False
    return grin_u(ax) <= y <= grin_l(ax)


CRACKS = set()
for _pl in [
    [(-3, -20), (-2, -18), (-4, -16), (-3, -14)],
    [(5, -18), (4, -17), (6, -15)],
    [(12, -15), (11, -13), (12, -11)],
    [(-12, -17), (-11, -15), (-12, -13)],
    [(3, 3), (4, 5), (2, 7), (3, 9)],
    [(-9, -2), (-11, 0)],
    [(-1, -18), (0, -16)],
    [(-5, 4), (-6, 6), (-4, 8)],
    [(-13, -6), (-11, -5)],
]:
    CRACKS |= raster(_pl)

FLAKES = [(-10.5, -17.2, 2.3, 1.6), (11.0, -3.5, 1.6, 1.2), (-5.5, 7.0, 1.8, 1.2), (12.0, -18.0, 1.4, 1.6)]
TEARS = {(-8, -6): 5, (-5, -6): 3, (8, -5): 7, (5, -5): 4}  # start texel -> length (black mascara runs)
BLOOD_DRIPS = {-3: 6, 1: 4, 4: 8, -6: 3, 7: 2}  # jaw column -> length below the lower lip


def in_flake(x, y, grow=0.0):
    for cx, cy, rx, ry in FLAKES:
        if ((x - cx) / (rx + grow)) ** 2 + ((y - cy) / (ry + grow)) ** 2 <= 1.0:
            return True
    return False


def eye_d(x, y, e):
    cx, cy, rx, ry, _ = e
    return ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2


def face_px(ix, iy, shift=0.0):
    """Front colour of the face map at head-local integer texel (ix, iy)."""
    x, y = ix + 0.5, iy + 0.5
    # --- greasepaint base: lit forehead, cooler lower face, darker towards the edges
    v = 0.76 + shift - 0.11 * (abs(x) / 13.0) ** 2
    if iy <= -18:
        v += 0.05
    if iy >= 3:
        v -= 0.07
    if -12 <= iy <= -11 and abs(x) < 12:
        v -= 0.14  # under the brow ridge
    if 3.5 < abs(x) < 5.5 and -10 <= iy <= -4:
        v -= 0.08  # beside the nose
    if iy == -16 and abs(x) < 6 and ix % 4 != 0:
        v -= 0.1  # forehead furrow
    if ix in (-1, 0) and -15 <= iy <= -13:
        v -= 0.18  # frown line
    col = pick(PAINT, v)
    # --- flaked paint showing the grey rot under it (dark paint lip around the hole)
    if in_flake(x, y):
        col = pick(SKIN, 0.5 if (ix + iy) % 3 else 0.42)
    elif in_flake(x, y, 0.75):
        col = pick(PAINT, v - 0.24)
    # --- red diamonds
    o = outline_of(in_diamond, ix, iy)
    if o == 2:
        col = pick(RED, 0.22)
    elif o == 1:
        vv = 0.64
        if not in_diamond(ix - 1, iy) or not in_diamond(ix, iy - 1):
            vv += 0.14
        elif not in_diamond(ix + 1, iy) or not in_diamond(ix, iy + 1):
            vv -= 0.14
        col = pick(RED, vv)
    # --- the painted grin (outline, glossy upper edge, dark lip line)
    g = outline_of(in_grin, ix, iy)
    if g == 2:
        col = pick(RED, 0.2)
    elif g == 1:
        vv = 0.6
        if not in_grin(ix, iy - 2):
            vv += 0.14
        if iy in (-1, 0):
            vv -= 0.22
        col = pick(RED, vv)
    # --- black mascara tears
    for (tx, ty), L in TEARS.items():
        if ix == tx and ty <= iy < ty + L:
            col = pick(SOCKET, 0.05) if iy < ty + L - 1 else pick(SOCKET, 0.4)
        if ix == tx + (1 if tx > 0 else -1) and iy == ty:
            col = pick(SOCKET, 0.3)
    # --- cracks: dark line + light paint lip below-right
    if (ix, iy) in CRACKS:
        col = scale(col, 0.38)
    elif (ix - 1, iy - 1) in CRACKS:
        col = scale(col, 1.07)
    # --- blood running from the mouth over the chin
    if iy >= 2:
        L = BLOOD_DRIPS.get(ix)
        if L and iy < 2 + L:
            col = pick(BLOOD, 5 / 6.0 - 0.06 * (iy - 2)) if iy < 1 + L else pick(BLOOD, 0.45)
    # --- eye sockets: black hollows, thin raw rim, pinpoint pupils
    for e in EYES:
        d = eye_d(x, y, e)
        if d <= 1.0:
            col = VOID
            if d > 0.55 and y < e[1] - 1:
                col = pick(SOCKET, 0.35)
            px, py = e[4]
            if (ix, iy) == (px, py):
                col = PUPIL
            elif (ix, iy) == (px, py + 1):
                col = PUPIL_DIM
        elif d <= 1.42:
            col = pick(RED, 0.08) if y > e[1] else pick(SOCKET, 0.5)
    return col


def eyes_glow(ix, iy):
    for e in EYES:
        px, py = e[4]
        if (ix, iy) == (px, py):
            return PUPIL
        if (ix, iy) == (px, py + 1):
            return PUPIL_DIM
    return None


# ------------------------------------------------------------------ head materials
SCALP_SPOTS = [(-6.0, 9.0, 1.6, 1.2), (4.5, 13.0, 1.2, 1.0), (8.0, 6.0, 1.0, 0.8), (-2.0, 15.0, 2.0, 1.4)]
SCAR = raster([(-8, 4), (-5, 7), (-4, 11), (-1, 14), (0, 17)])


def paint_depth(y):
    """How far back from the face plane the greasepaint reaches on the sides (ragged, per row)."""
    return 6.5 + fl(hash3(fl(y), 0, 0, 61) * 3.5)


def skin_px(ctx, x, y, z, v):
    sv = 0.5 + (v - 0.66) * 0.9
    if hash3(fl(x * 0.5), fl(y * 0.5), fl(z * 0.5), 63) > 0.86:
        sv -= 0.1
    return pick(SKIN, sv)


def side_grin(s, y):
    """The painted grin continues back along the cheeks towards the ears."""
    if s > 6.5:
        return 0
    c = -5.8 - 0.8 * max(s, -2)
    half = 1.8 - 0.25 * max(s, -2)
    d = abs(y - c)
    if d <= half - 0.9:
        return 1
    if d <= half:
        return 2
    return 0


def head_mat(ctx):
    x, y, z = hpos(ctx)
    f = ctx.face
    ix, iy = fl(x), fl(y)
    if f == 'front':
        return face_px(ix, iy, -0.07 if ctx.bone.name.endswith('_brow') else 0.0)
    s = z - FZ
    v = 0.68 + light(ctx, 0.9)
    v = rim(ctx, v, 0.06)
    if f in ('west', 'east'):
        g = side_grin(s, y)
        if g and y > -15:
            return pick(RED, 0.2 if g == 2 else 0.52)
        pd = paint_depth(y)
        if s < pd:
            return pick(PAINT, v - 0.04)
        if s < pd + 1:
            return pick(PAINT, v - 0.3)
        return skin_px(ctx, x, y, z, v)
    if f == 'top':
        if s < 1.5 + hash3(ix, 0, 0, 67) * 2.5:
            return pick(PAINT, v)
        if s < 2.5 + hash3(ix, 0, 0, 67) * 2.5:
            return pick(PAINT, v - 0.3)
        if (ix, fl(s)) in SCAR:
            return pick(SKIN, 0.12)
        if (ix - 1, fl(s)) in SCAR or (ix + 1, fl(s)) in SCAR:
            if fl(s) % 2 == 0:
                return pick(SKIN, 0.2)  # stitches
        for cx, cs, rx, rs in SCALP_SPOTS:
            if ((x - cx) / rx) ** 2 + ((s - cs) / rs) ** 2 <= 1:
                return pick(SKIN, 0.3)
        return skin_px(ctx, x, y, z, v + 0.06)
    if f == 'bottom':
        if ctx.cube.size[1] >= 5 and ctx.cube.size[2] >= 16:  # underside of the muzzle = palate
            if s < 15:
                return pick(GUM, 0.42 + (0.16 if fl(s) % 3 == 0 else 0) - s * 0.015)
            return pick(GUM, 0.05)
        return pick(PAINT, 0.36)
    return skin_px(ctx, x, y, z, v)


def jaw_mat(ctx):
    x, y, z = hpos(ctx)
    f = ctx.face
    ix, iy = fl(x), fl(y)
    s = z - FZ
    if f == 'front':
        return face_px(ix, iy)
    if f == 'top':
        if ctx.cube.size[2] >= 14:  # inside of the mouth: tongue groove and gullet
            if abs(x) < 3.5 and s < 13:
                return pick(GUM, 0.56 - s * 0.02 + (0.1 if abs(x) < 1 else 0))
            return pick(GUM, 0.3 - s * 0.015)
        return pick(PAINT, 0.6)
    v = 0.62 + light(ctx, 0.9)
    v = rim(ctx, v, 0.06)
    if f in ('west', 'east'):
        if s < paint_depth(y + 40):
            return pick(PAINT, v - 0.06)
        return skin_px(ctx, x, y, z, v)
    if f == 'bottom':
        return pick(SKIN, 0.4 + (0.08 if hash3(ix, 0, fl(z), 69) > 0.7 else 0))
    return skin_px(ctx, x, y, z, v)


def nose_mat(ctx):
    x, y, z = hpos(ctx)
    v = 0.56 + light(ctx, 1.2)
    cx, cy = -1.0, -8.6
    d2 = (x - cx) ** 2 + (y - cy) ** 2
    if ctx.face == 'front':
        if d2 < 1.6:
            v += 0.36
        elif d2 < 5.0:
            v += 0.13
        if x > 1.5 and y > -6:
            v -= 0.1
    if ctx.face == 'top':
        v += 0.05
    if ctx.face == 'bottom':
        v -= 0.25
    v = rim(ctx, v, 0.12)
    c = pick(RED, v)
    if ctx.face == 'front' and (fl(x), fl(y)) in {(1, -6), (2, -5), (2, -7), (-2, -5)}:
        c = pick(RED, 0.15)  # cracked rubber
    return c


def teeth_mat(root, maxlen, axis, seed, grow=1, gap=2):
    """Needle teeth on a zero-thickness plane. root: head-local y of the gum line; teeth grow along
    +y (upper, grow=1) or -y (lower, grow=-1). Position-only so both faces of the plane agree."""
    def f(ctx):
        x, y, z = hpos(ctx)
        u = x if axis == 'x' else z
        col = fl(u)
        if col % gap != 0:
            return None
        h = hash3(col, 0, 0, seed)
        L = 1.5 + (h ** 0.6) * (maxlen - 1.5)
        depth = (y - root) * grow
        if depth < 0 or depth > L:
            return None
        if depth < 0.8:
            return pick(GUM, 0.6)
        t = depth / L
        v = 0.78 - t * 0.1 + (0.1 if t > 0.75 else 0)
        if hash3(col, 5, 0, seed) > 0.8:
            v -= 0.32
        if hash3(col, 7, 0, seed) > 0.72 and t < 0.5:
            return pick(BLOOD, 0.8)
        return pick(TEETH, v)
    return f


def membrane_mat(ctx):
    """Stretched cheek flesh tearing between skull and jaw (seen only when the mouth gapes)."""
    x, y, z = hpos(ctx)
    col = fl(z)
    if hash3(col, 0, 0, 97) > 0.55 and hash3(col, fl(y), 0, 98) > 0.35:
        return None
    return pick(GUM, 0.35 + hash3(col, 1, 0, 99) * 0.25)


# ------------------------------------------------------------------ hair
def hair_mat(seed):
    def f(ctx):
        x, y, z = hpos(ctx)
        out = max(0.0, abs(x) - 11.0)
        fc = ctx.face
        if fc in ('front', 'back'):
            key = (fl(y), fl(out / 4))
        elif fc in ('top', 'bottom'):
            key = (fl(z), fl(out / 4))
        else:
            key = (fl(y / 2) * 7 + fl(z / 2), 0)
        st = hash3(key[0], key[1], 0, seed)
        if not flat(ctx) and edge(ctx) == 0 and hash3(fl(x), fl(y), fl(z), seed + 3) > 0.5:
            return None  # frizz eats the box outline
        v = 0.36 + min(out, 14) * 0.022 + light(ctx, 1.3)
        v += 0.16 if st > 0.72 else (-0.14 if st < 0.25 else 0)
        if fc in ('west', 'east') and abs(x) > 14:
            v += 0.06
        return pick(HAIR, v)
    return f


def frizz_mat(seed):
    """Front-facing plane: ragged halo of loose hair around a tuft (alpha cut-out)."""
    def f(ctx):
        x, y, z = hpos(ctx)
        lx, ly, lz = local(ctx)
        w, h, _ = ctx.cube.size
        u = (lx - ctx.cube.origin[0]) / w
        t = (ly - ctx.cube.origin[1]) / h
        r = math.hypot((u - 0.5) * 2, (t - 0.5) * 2)
        lim = 0.78 + 0.28 * (hash3(fl(y / 2), 0, 0, seed) - 0.5) + 0.2 * (hash3(fl(x), fl(y), 0, seed) - 0.5)
        if r > lim:
            return None
        st = hash3(fl(y), 0, 0, seed + 1)
        return pick(HAIR, 0.42 + (0.18 if st > 0.7 else 0) - (0.12 if st < 0.25 else 0) + (r - 0.5) * 0.2)
    return f


# ------------------------------------------------------------------ body materials
def wrap_u(ctx, x, z):
    return x if ctx.face in ('front', 'back', 'top', 'bottom') else z


def suit_value(ctx, x, y, z):
    v = 0.56 + light(ctx, 1.0)
    v = rim(ctx, v, 0.09)
    n = fbm(x * 0.1, y * 0.1, z * 0.1, 2, 71)
    v += 0.06 if n > 0.6 else (-0.06 if n < 0.38 else 0)
    return v


def suit_mat(ctx):
    x, y, z = dpos(ctx)
    u = wrap_u(ctx, x, z)
    v = suit_value(ctx, x, y, z)
    sleeve = ctx.bone.name.endswith('_arm') or ctx.bone.name.endswith('_forearm')
    k = fl(y + 0.5) if sleeve else fl(u + 0.5)
    stripe = (k % 6) in (0, 1)
    if hash3(fl(y), fl(u) // 5, 0, 73) > 0.9:
        v -= 0.12  # cloth creases
    c = pick(MUSTARD, v - 0.04) if stripe else pick(PURPLE, v)
    if y > 10:
        c = mix(c, pick(SKIN, 0.18), min(0.55, (y - 10) / 16))  # mud on the hems
    bn = ctx.bone.name
    if bn == 'body' and ctx.face == 'front':
        bx = fl(x)
        if abs(bx) < 8:
            L = 5 + hash3(bx, 0, 0, 75) * 14
            top = -40
            if y < top + L:
                c = pick(BLOOD, 0.78 if y < top + L - 1.5 else 0.5)
    return c


def ruff_mat(kind, seed):
    def f(ctx):
        x, y, z = dpos(ctx)
        lx, ly, lz = local(ctx)
        w, h, d = ctx.cube.size
        ci = fl(lx - ctx.cube.origin[0])
        rad = -lz
        # scalloped, frayed outer edge
        scal = 1.2 * abs(math.sin((ci + 0.5) * math.pi / 3.0))
        if rad > d - scal - (1.0 if hash3(ci, 1, 0, seed) > 0.7 else 0):
            return None
        pleat = ci % 3
        v = 0.62 + (0.13 if pleat == 0 else (-0.15 if pleat == 2 else 0)) - rad * 0.008
        if kind == 'white':
            c = pick(RUFF_W, v)
            if rad > d - 3.2:
                c = pick(RED, v - 0.02)
        elif kind == 'purple':
            c = pick(PURPLE, v + 0.12)
            if rad > d - 3.2:
                c = pick(MUSTARD, v + 0.05)
        else:
            c = pick(RUFF_W, v - 0.08)
            if rad > d - 3.2:
                c = pick(PURPLE, v + 0.1)
        if hash3(fl(x / 2), fl(y / 2), fl(z / 2), seed + 7) > 0.9:
            c = pick(BLOOD, 0.75)
        if rad < 2.5:
            c = scale(c, 0.7)
        return c
    return f


def glove_mat(ctx):
    x, y, z = dpos(ctx)
    lx, ly, lz = local(ctx)
    v = 0.64 + light(ctx, 1.0)
    v = rim(ctx, v, 0.1)
    if hash3(fl(x / 2), fl(y / 2), fl(z / 2), 85) > 0.8:
        v -= 0.14  # grime
    c = pick(GLOVE, v)
    o, sz = ctx.cube.origin, ctx.cube.size
    if sz[0] <= 2 and sz[1] >= 4:  # fingers: torn tips show grey skin; blood under the nails
        tip = ly - o[1]
        if tip > sz[1] - 2.5:
            c = pick(SKIN, 0.45 + light(ctx))
        elif tip > sz[1] - 3.5:
            c = pick(GLOVE, 0.25) if hash3(fl(x), fl(z), 0, 86) > 0.4 else c
        elif hash3(fl(x), 0, 0, 87) > 0.6 and tip > sz[1] * 0.4:
            c = pick(BLOOD, 0.7)
    return c


def claw_mat(ctx):
    v = 0.35 + light(ctx, 1.4)
    if ctx.face in ('front', 'west', 'east') and ctx.t < 0.5:
        v += 0.3
    return pick(CLAW, v)


def shoe_mat(ctx):
    x, y, z = dpos(ctx)
    lx, ly, lz = local(ctx)
    v = 0.56 + light(ctx, 1.4)
    v = rim(ctx, v, 0.12)
    if ctx.face == 'top' and lz < -11 and abs(lx) < 3:
        v += 0.18  # glossy toe highlight
    n = fbm(x * 0.25, y * 0.25, z * 0.25, 2, 87)
    if n > 0.66:
        v -= 0.2  # scuffs
    return pick(SHOE, v)


def sole_mat(ctx):
    return pick(SOLE, rim(ctx, 0.5 + light(ctx, 1.0)))


def hat_mat(ctx):
    v = 0.5 + light(ctx, 1.3)
    v = rim(ctx, v, 0.15)
    x, y, z = dpos(ctx)
    if hash3(fl(x), fl(y), fl(z), 91) > 0.88:
        v += 0.18  # dust
    return pick(FELT, v)


def band_mat(ctx):
    return pick(RED, 0.42 + light(ctx, 1.0))


def neck_mat(ctx):
    x, y, z = dpos(ctx)
    v = 0.45 + light(ctx, 1.0)
    if fl(x) % 3 == 0:
        v -= 0.1  # cords
    return pick(SKIN, v)


def balloon_mat(ctx):
    lx, ly, lz = local(ctx)
    v = 0.5 + light(ctx, 1.5)
    v = rim(ctx, v, 0.08)
    f = ctx.face
    if f == 'front' or f == 'west':
        u = lx if f == 'front' else lz
        if ly < -12 and u < -1:
            v += 0.16
            if ly < -14 and u < -3:
                v += 0.3
    if ly > -8:
        v -= 0.08
    return pick(BALLOON, v)


def string_mat(ctx):
    x, y, z = dpos(ctx)
    return pick(STRING, 0.5 + (0.22 if fl(y) % 3 == 0 else 0))


def skin_mat(ctx):
    return pick(SKIN, rim(ctx, 0.5 + light(ctx, 1.0)))


def pompom_mat(ctx):
    x, y, z = dpos(ctx)
    v = 0.5 + light(ctx, 1.2) + (hash3(fl(x), fl(y), fl(z), 93) - 0.5) * 0.3
    return pick(RED, v)


# ------------------------------------------------------------------ geometry
def build():
    global HEAD_ABS
    r = Rig()

    def bone(name, pivot, parent=None, rot=(0, 0, 0), mat=None):
        b = r.bone(name, pivot, parent, rot, mat)
        b.abs = r.abs_pivot[name]
        return b

    def at(parent, dx, dy, dz):
        a = r.abs_pivot[parent]
        return (a[0] + dx, a[1] + dy, a[2] + dz)

    def box(b, frm, size, mat=None, inflate=0.0, decals=None, ref=None):
        a = r.abs_pivot[ref or b]
        return r.box(b, (a[0] + frm[0], a[1] + frm[1], a[2] + frm[2]), size, mat=mat, inflate=inflate, decals=decals)

    def mx(sx, frm, size):
        return frm if sx < 0 else (-(frm[0] + size[0]), frm[1], frm[2])

    def mbox(b, sx, frm, size, **kw):
        return box(b, mx(sx, frm, size), size, **kw)

    HIP = -14.0
    LEAN = 14  # torso hunch

    # ---------------- legs: baggy striped trousers, knobbly knees, enormous shoes
    LEG = {'right': ((-7, 0, -3), (15, 0, 6), (-8, 0, -3)), 'left': ((-2, 0, 3), (10, 0, -7), (-8, 0, 4))}
    for side, sx in (('right', -1), ('left', 1)):
        r_thigh, r_shin, r_shoe = LEG[side]
        leg = bone(f'{side}_leg', (5.5 * sx, HIP, 1), rot=r_thigh, mat=suit_mat)
        box(leg.name, (-4.5, -2, -4.5), (9, 18, 9))
        shin = bone(f'{side}_shin', at(leg.name, 0, 16, 0), leg.name, rot=r_shin, mat=suit_mat)
        box(shin.name, (-3.5, -1, -3.5), (7, 14, 7))
        box(shin.name, (-5, 11, -5), (10, 4, 10))
        shoe = bone(f'{side}_shoe', at(shin.name, 0, 16, 0), shin.name, rot=r_shoe, mat=shoe_mat)
        box(shoe.name, (-5.5, 5, -19), (11, 1, 24), mat=sole_mat)
        box(shoe.name, (-4.5, -1, -7), (9, 6, 11))
        box(shoe.name, (-6, -0.5, -19), (12, 5.5, 12) if False else (12, 5, 12))
        box(shoe.name, (-5, -2, -18), (10, 2, 10))
        box(shoe.name, (-5, 0.5, -20), (10, 4, 2))
        box(shoe.name, (-2.5, -2.5, -8), (5, 2, 4))
        if side == 'left':  # split toe, black claws poking out
            for k, cx in enumerate((-3.5, -0.5, 2.5)):
                box(shoe.name, (cx, 1.5 + (k % 2), -24), (1, 1, 5), mat=claw_mat)

    # ---------------- torso (hunched)
    bone('body', (0, HIP, 1), rot=(LEAN, 0, 0), mat=suit_mat)
    box('body', (-10, -6, -6), (20, 8, 12))
    box('body', (-8, -13, -5), (16, 8, 10))
    box('body', (-10, -22, -5.5), (20, 10, 11))
    box('body', (-12.5, -24, -5), (25, 5, 10))
    box('body', (-8, -25, 1), (16, 11, 8))
    for k in range(3):
        box('body', (-1.5, -23 + 4 * k, 8.5), (3, 3, 2), mat=skin_mat)
    for k, (yy, zz) in enumerate(((-18, -8), (-12, -7.5), (-5, -8.5))):
        box('body', (-2, yy, zz), (4, 4, 3), mat=pompom_mat)
    bone('coattails', at('body', 0, -6, 6), 'body', rot=(-LEAN + 10, 0, 0), mat=suit_mat)
    box('coattails', (-8.5, 0, 0), (8, 22, 0))
    box('coattails', (0.5, 0, 0), (8, 20, 0))

    # ---------------- ruff: two tiers of pleated panels; flares up behind the head like a fan
    bone('ruff', at('body', 0, -23, -1.5), 'body', rot=(-LEAN + 6, 0, 0))
    tiers = [  # (count, radius, width, length, y offset, phase, kinds, droop front, droop back)
        (10, 4.5, 12, 16, 1.0, 0.0, ('white', 'purple'), 62, -16),
        (10, 3.5, 10, 11, -1.0, 18.0, ('cream',), 46, -28),
    ]
    for t, (n, rad, wdt, ln, yo, ph, kinds, dfront, dback) in enumerate(tiers):
        for k in range(n):
            th = ph + 360.0 * k / n
            a = math.radians(th)
            pn = f'ruff_{"lo" if t == 0 else "hi"}{k}'
            dr = dback + (dfront - dback) * (0.5 + 0.5 * math.cos(a)) + (6 if k % 2 else -4)
            bone(pn, at('ruff', -rad * math.sin(a), yo, -rad * math.cos(a)), 'ruff', rot=(dr, th, 0),
                 mat=ruff_mat(kinds[k % len(kinds)], 400 + 10 * t + k))
            box(pn, (-wdt / 2, 0, -ln), (wdt, 0, ln))

    # ---------------- neck + head
    NECK = 30
    bone('neck', at('body', 0, -22, -2), 'body', rot=(NECK, 0, 0), mat=neck_mat)
    box('neck', (-4, -8, -4), (8, 9, 8))
    head = bone('head', at('neck', 0, -7, -1), 'neck', rot=(-(LEAN + NECK) + 4, 0, 6), mat=head_mat)
    HEAD_ABS = r.abs_pivot['head']

    def eyes_decal(ox, oy):
        def fn(img, u0, v0, w, h):
            px = img.load()
            for j in range(h):
                for i in range(w):
                    c = eyes_glow(ox + i, oy + j)
                    if c:
                        px[u0 + i, v0 + j] = c
        return fn

    box('head', (-13, -18, FZ), (26, 13, 22), decals={'eyes:front': eyes_decal(-13, -18)})   # cranium
    box('head', (-12, -5, FZ + 1), (24, 5, 19))                     # muzzle (its underside is the palate)
    box('head', (-11, -20, FZ + 2), (22, 2, 18))                    # bald dome
    box('head', (-10, -16, FZ + 22), (20, 11, 3))                   # swollen occiput
    box('head', (2, -21, FZ - 2), (8, 5, 3))                        # tumorous bulge over the left brow
    box('head', (-12.5, -5, FZ - 2), (8, 5, 3))                     # right cheek
    box('head', (4.5, -5, FZ - 2), (8, 5, 3))                       # left cheek
    box('head', (-4.5, -3, FZ - 2), (9, 3, 3))                      # upper lip
    box('head', (-3, -10, FZ - 5), (6, 6, 5), mat=nose_mat)         # bulbous nose
    box('head', (-4, -9, FZ - 4), (8, 4, 4), mat=nose_mat)
    box('head', (-2, -11, FZ - 4), (4, 8, 4), mat=nose_mat)
    # upper needle teeth: three rows + side rows
    box('head', (-11, 0, FZ - 1.5), (22, 6, 0), mat=teeth_mat(0, 6, 'x', 201))
    box('head', (-10, 0, FZ + 1.5), (20, 5, 0), mat=teeth_mat(0, 5, 'x', 203))
    box('head', (-9, 0, FZ + 4.5), (18, 4, 0), mat=teeth_mat(0, 4, 'x', 205))
    for sx in (-1, 1):
        box('head', (11 * sx, 0, FZ), (0, 5, 15), mat=teeth_mat(0, 5, 'z', 207 + sx))
    for side, sx in (('right', -1), ('left', 1)):
        bone(f'{side}_brow', at('head', 1.0 * sx, -13, FZ), 'head', rot=(0, 0, 15 * -sx), mat=head_mat)
        mbox(f'{side}_brow', sx, (-11, -1.5, -2), (11, 3, 2))

    # the real mouth: a long dislocated jaw hanging slightly crooked, permanently agape
    bone('jaw', at('head', 0, -1, FZ + 17), 'head', rot=(17, 0, -4), mat=jaw_mat)
    box('jaw', (-10.5, 0, FZ), (21, 5, 17), ref='head')
    box('jaw', (-9.5, 0, FZ - 2), (19, 2, 2), ref='head')            # lower lip
    box('jaw', (-7, 5, FZ - 1), (14, 4, 13), ref='head')             # chin
    box('jaw', (-4, 9, FZ - 1.5), (8, 2, 7), ref='head')             # pointed chin tip
    box('jaw', (-10, -6, FZ - 1.2), (20, 6, 0), mat=teeth_mat(0, 6, 'x', 211, grow=-1), ref='head')
    box('jaw', (-9, -5, FZ + 1.8), (18, 5, 0), mat=teeth_mat(0, 5, 'x', 213, grow=-1), ref='head')
    for sx in (-1, 1):
        box('jaw', (9.6 * sx, -5, FZ + 1), (0, 5, 14), mat=teeth_mat(0, 5, 'z', 215 + sx, grow=-1), ref='head')
        box('jaw', (10.3 * sx, -9, FZ + 1), (0, 9, 13), mat=membrane_mat, ref='head')

    # tiny dented top hat, jammed askew
    bone('hat', at('head', 6, -20.5, FZ + 11), 'head', rot=(-10, 0, 30), mat=hat_mat)
    box('hat', (-6.5, -1, -6), (13, 1, 12))
    box('hat', (-4.5, -9, -4), (5, 8, 8))
    box('hat', (0.5, -7, -4), (4, 6, 8))
    box('hat', (-4.5, -3, -4), (9, 2, 8), mat=band_mat, inflate=0.3)

    # frizzy red hair exploding from the temples + a horseshoe around the back (bald on top)
    for side, sx in (('right', -1), ('left', 1)):
        hn = f'hair_{side}'
        bone(hn, at('head', 12.5 * sx, -10, FZ + 13), 'head', rot=(0, 0, 6 * -sx), mat=hair_mat(311 + sx))
        mbox(hn, sx, (-6, -8, -8), (8, 15, 15))
        mbox(hn, sx, (-10, -12, -6), (6, 11, 12))
        mbox(hn, sx, (-11, -2, -5), (6, 10, 10))
        mbox(hn, sx, (-13, -9, -3), (5, 8, 7))
        mbox(hn, sx, (-7, 6, -6), (6, 6, 9))
        mbox(hn, sx, (-16, -16, 0), (13, 30, 0), mat=frizz_mat(331 + sx))
    bone('hair_back', at('head', 0, -10, FZ + 24), 'head', mat=hair_mat(341))
    box('hair_back', (-13, -5, -2), (26, 13, 6))
    box('hair_back', (-10, 7, -3), (20, 5, 5))

    # ---------------- arms: long, with puffed shoulders and frilled cuffs
    ARM = {'right': ((-LEAN - 10, 0, 9), (-40, 0, 0), (14, 0, 0)), 'left': ((-LEAN - 4, 0, -5), (-12, 0, 0), (-4, 0, 0))}
    for side, sx in (('right', -1), ('left', 1)):
        ra, rf, rh = ARM[side]
        arm = bone(f'{side}_arm', at('body', 12.5 * sx, -21, 0), 'body', rot=ra, mat=suit_mat)
        box(arm.name, (-4.5, -3, -4.5), (9, 8, 9))
        box(arm.name, (-3, 2, -3), (6, 16, 6))
        fa = bone(f'{side}_forearm', at(arm.name, 0, 17, 0), arm.name, rot=rf, mat=suit_mat)
        box(fa.name, (-2.5, -1, -2.5), (5, 15, 5))
        box(fa.name, (-4, 11, -4), (8, 3, 8), mat=ruff_mat('white', 451 + sx))
        hand = bone(f'{side}_hand', at(fa.name, 0, 14, 0), fa.name, rot=rh, mat=glove_mat)
        box(hand.name, (-3.5, -1, -2.5), (7, 3, 5))
        box(hand.name, (-3, 1, -2), (6, 7, 4))
        for k, fx in enumerate((-3, -1, 1)):
            ln = (10, 11, 9)[k]
            box(hand.name, (fx, 7, -1.5), (2, ln, 2))
            box(hand.name, (fx + 0.5, 7 + ln - 0.5, -1), (1, 5, 1), mat=claw_mat)
        mbox(hand.name, -sx, (-5, 2, -2), (2, 6, 2))
        mbox(hand.name, -sx, (-4.5, 7.5, -1.5), (1, 3, 1), mat=claw_mat)

    # balloon on a string, held up from the right hand
    ra, rf, rh = ARM['right']
    net = ra[0] + LEAN + rf[0] + rh[0]
    bone('balloon_string', at('right_hand', 0, 5, 0), 'right_hand', rot=(-net, 0, -28), mat=string_mat)
    SL = 36
    box('balloon_string', (0, -SL, -0.5), (0, SL, 1))
    box('balloon_string', (-0.5, -SL, 0), (1, SL, 0))
    bone('balloon', at('balloon_string', 0, -SL, 0), 'balloon_string', rot=(0, 0, 18), mat=balloon_mat)
    box('balloon', (-1, -3, -1), (2, 3, 2))
    box('balloon', (-4, -5, -4), (8, 2, 8))
    box('balloon', (-6, -19, -6), (12, 14, 12))
    box('balloon', (-7, -17, -5), (14, 10, 10))
    box('balloon', (-5, -17, -7), (10, 10, 14))
    box('balloon', (-4, -20, -4), (8, 1, 8))

    m = Model('payaso', 256, 256, r.roots)
    m.scale = 0.5
    _ground(m)
    return m


def _ground(m):
    """Shift the roots so the lowest point of the shoes touches y = 24."""
    import numpy as np
    low = -1e9
    for b in m.bones():
        if not b.name.endswith('_shoe'):
            continue
        M = m.world_matrix(b)
        for c in b.cubes:
            x0, y0, z0 = c.origin
            w, h, d = c.size
            for cx in (x0, x0 + w):
                for cy in (y0, y0 + h):
                    for cz in (z0, z0 + d):
                        low = max(low, (M @ np.array([cx, cy, cz, 1.0]))[1])
    dy = 24.0 - low
    for rb in m.roots:
        rb.pivot = (rb.pivot[0], rb.pivot[1] + dy, rb.pivot[2])


DEFAULT_MAT = suit_mat
FOCUS = 'head'
POSES = {
    'attack': {
        'jaw': (0.85, 0, 0, 0, 0, 0),
        'head': (-0.2, 0, 0.52, 0, 0, 0),
        'neck': (0.2, 0, 0, 0, 0, 0),
        'body': (0.2, 0, 0, 0, 0, 0),
        'right_arm': (-1.25, 0, 0.1, 0, 0, 0),
        'left_arm': (-1.45, 0, -0.15, 0, 0, 0),
        'right_forearm': (0.55, 0, 0, 0, 0, 0),
        'left_forearm': (-0.15, 0, 0, 0, 0, 0),
    },
    'laugh': {
        'jaw': (0.7, 0, 0, 0, 0, 0),
        'head': (-0.6, 0, -0.12, 0, 0, 0),
        'neck': (-0.35, 0, 0, 0, 0, 0),
        'body': (-0.2, 0, 0, 0, 0, 0),
        'right_arm': (0.1, 0, 0.3, 0, 0, 0),
        'left_arm': (0.25, 0, -0.5, 0, 0, 0),
        'left_forearm': (-0.6, 0, 0, 0, 0, 0),
    },
    'scream': {
        'jaw': (1.0, 0, 0, 0, 0, 0),
        'head': (0.2, 0, 0, 0, 0, 0),
        'neck': (0.2, 0, 0, 0, 0, 0),
        'right_arm': (-0.3, 0, 0.7, 0, 0, 0),
        'left_arm': (-0.3, 0, -0.8, 0, 0, 0),
        'hair_right': (0, 0, 0.2, 0, 0, 0),
        'hair_left': (0, 0, -0.2, 0, 0, 0),
    },
}
ANIM_NOTES = """
body: hunched torso pivoting at the hips; bob +-2 deg on each step, lean further (+0.2 rad) when chasing.
neck/head: share look-at (neckShare 0.4); idle: slow head roll on Z (+-0.15 rad, 6 s period) and sudden
  'tilt snaps' every few seconds. jaw: rests agape; idle chatter 0..0.12 rad; attack/scream/laugh open to ~1 rad.
right_brow/left_brow: tiny Z twitch when the jaw opens (furrow). hat: wobbles with head roll (lagged).
hair_left/hair_right/hair_back: spring-lagged Z wobble when the head moves.
ruff (+ ruff_lo*/ruff_hi* panels): rigid; optional tiny flutter on the panels' X rotation.
right_arm/left_arm (+ _forearm, _hand): long dangling swing on walk (armAmp 0.5), left arm sways loosely;
  chase: both arms forward reaching (-1.2..-1.5 rad). The right hand keeps the balloon:
  balloon_string should counter-rotate the net arm swing so it stays upright; balloon bobs (+-0.1 rad Z).
right_leg/left_leg (+ _shin, _shoe): walk swing (legAmp 0.7) with shin flex 0..0.5 rad; big shoes flap.
coattails: lagged X swing behind the legs.
Poses: attack (lunge, jaw open huge, arms reaching, head tilted 30 deg), laugh (head thrown back, jaw open),
scream (jaw max, arms spread).
"""
