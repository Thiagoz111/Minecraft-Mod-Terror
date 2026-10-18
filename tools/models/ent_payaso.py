"""Sonrisas -- the demonic circus clown of DEAD LINE (module key: payaso).

Authored at 2x texel density (model.scale = 0.5) with rig.Rig absolute coordinates:
+Y down, ground at y = 24, the creature faces -Z, right_* parts on -X.
Every cube is authored in its bone's *unrotated* frame; bone rotations fold the hunch.
The face is painted from one 2D face map in head-local design coordinates, so every
front-facing cube of the head (skull, brows, cheeks, muzzle, jaw, lips) shares the same
painting and the features line up across the stacked layers.
"""
import math

from mcmodel import Model, fbm, vnoise, hash3, face_light, pick
from rig import Rig
from paint import hx, mix, scale, edge


def pal(*h):
    return [hx(c) for c in h]


# ------------------------------------------------------------------ palettes (dark -> light)
PAINT = pal('#25212a', '#3d3842', '#5b5560', '#7d7780', '#a09aa0', '#c2bdbd', '#dcd8d1', '#eeebe2', '#faf8f0')
SKIN = pal('#0f110f', '#1a1d19', '#272b24', '#363b31', '#474b3f', '#595c4e', '#6d6e5d', '#83826e')
RED = pal('#140103', '#2a0306', '#470609', '#6a0b10', '#8e1217', '#b31d1f', '#d2352a', '#ec5b3c')
BLOOD = pal('#100103', '#1e0205', '#300508', '#44080c', '#5a0d10')
VOID = hx('#030103')
SOCKET = pal('#0b0509', '#1a0d15', '#2c1825', '#3e2433')
PUPIL = hx('#fff2a0')
PUPIL_DIM = hx('#f0a81c')
HAIR = pal('#1e0503', '#3a0a04', '#5e1306', '#87200a', '#ad320d', '#cf4b12', '#ea6e1f', '#ff9a3c')
PURPLE = pal('#0c0610', '#170c1e', '#24132f', '#331b41', '#432454', '#552e66', '#683a78')
MUSTARD = pal('#1d1505', '#33270a', '#4d3b0f', '#6a5316', '#886c1e', '#a58729', '#bea036')
RUFF_W = pal('#2f2b2c', '#4d4847', '#6f6965', '#928b84', '#b3aca2', '#cfc8bc', '#e4ded2', '#f2eee4')
GLOVE = pal('#2b2722', '#45403a', '#635c53', '#837a6e', '#a39888', '#bfb4a2', '#d6ccba', '#e8e0d0')
CLAW = pal('#030203', '#09070a', '#121014', '#1d1a20', '#2b2730', '#3f3a45')
SHOE = pal('#120203', '#250406', '#3e070b', '#5c0c11', '#7c1318', '#9d1c1f', '#bd2b28', '#d84535')
SOLE = pal('#070607', '#100e10', '#1b181b', '#2a2529', '#3a3439')
FELT = pal('#050406', '#0b090d', '#131016', '#1c1820', '#27222c', '#342d3a')
TEETH = pal('#3a2f22', '#5e4f39', '#857456', '#ab9a75', '#cbbd96', '#e4d9b6', '#f4eed6')
GUM = pal('#0c0204', '#1d0508', '#33090e', '#4e1016', '#6b1a20', '#8a2a2e')
BALLOON = pal('#2a0105', '#4a030a', '#710711', '#9a0d19', '#c21823', '#e23434', '#ff6a5c', '#ffc4b4')
STRING = pal('#3a3631', '#615b53', '#8c857a', '#b5ad9f')

HEAD_ABS = (0.0, 0.0, 0.0)  # set by build(): design-space pivot of the head
FZ = -19  # head-local z of the skull's front face


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


# ------------------------------------------------------------------ 2D shape helpers (texel centres)
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


# ------------------------------------------------------------------ the face map
EYES = [  # centre x, centre y, radius x, radius y, pupil texel
    (-7.0, -8.6, 3.4, 3.1, (-7, -9)),
    (7.2, -8.4, 3.9, 3.5, (6, -9)),
]
DIAMOND = (5.4, 8.6, 5.6)  # half width, half height up, half height down


def eye_d(x, y, e):
    cx, cy, rx, ry, _ = e
    return ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2


def in_diamond(ix, iy):
    x, y = ix + 0.5, iy + 0.5
    for cx, cy, _, _, _ in EYES:
        hw, hu, hd = DIAMOND
        hh = hu if y < cy else hd
        if abs(x - cx) / hw + abs(y - cy) / hh <= 1.0:
            return True
    return False


def grin_u(ax):
    return -2.6 - 0.023 * ax * ax


def grin_l(ax):
    return 3.2 - 0.0574 * ax * ax


def in_grin(ix, iy):
    x, y = ix + 0.5, iy + 0.5
    ax = abs(x)
    if ax > 13.4:
        return False
    return grin_u(ax) <= y <= grin_l(ax)


CRACKS = set()
for _pl in [
    [(-3, -21), (-2, -19), (-4, -17), (-3, -15)],
    [(5, -21), (4, -19), (6, -18), (5, -16)],
    [(11, -15), (12, -13), (11, -11)],
    [(-12, -17), (-10, -15), (-11, -13)],
    [(3, 2), (4, 4), (2, 6), (3, 8)],
    [(-9, -2), (-11, 0), (-10, 2)],
    [(-1, -18), (0, -16), (-1, -14)],
    [(9, -2), (10, -4), (12, -5)],
    [(-6, 3), (-7, 5), (-5, 7)],
]:
    CRACKS |= raster(_pl)

FLAKES = [(-10.5, -17.0, 2.4, 1.7), (10.0, -1.0, 1.9, 1.4), (-5.5, 5.5, 2.2, 1.4), (2.5, -19.5, 1.8, 1.1),
          (12.0, -17.5, 1.5, 2.0)]
TEARS = {(-8, -5): 4, (-6, -5): 2, (8, -4): 6, (6, -4): 3}  # start texel -> length (black mascara runs)
BLOOD_DRIPS = {-3: 5, 1: 3, 4: 6, -6: 2}  # jaw column -> length below the lower lip


def in_flake(x, y, grow=0.0):
    for cx, cy, rx, ry in FLAKES:
        if ((x - cx) / (rx + grow)) ** 2 + ((y - cy) / (ry + grow)) ** 2 <= 1.0:
            return True
    return False


def face_px(ix, iy, base_shift=0.0):
    """Front face colour at head-local integer texel (ix, iy)."""
    x, y = ix + 0.5, iy + 0.5
    # --- greasepaint base value
    v = 0.74 + base_shift - 0.13 * (abs(x) / 13.0) ** 2
    if iy <= -19:
        v += 0.05
    if -12 <= iy <= -11 and abs(x) < 12:
        v -= 0.16  # shadow under the brow ridge
    if 3.5 < abs(x) < 6 and -10 <= iy <= -3:
        v -= 0.08  # shadow beside the nose
    if iy >= 5:
        v -= 0.06
    # forehead furrows + frown lines
    if iy == -17 and abs(x) < 6 and (ix % 3 != 0):
        v -= 0.12
    if ix in (-1, 0) and -15 <= iy <= -13:
        v -= 0.2
    col = pick(PAINT, v)
    # --- flaked paint: grey rotting skin with a dark paint lip
    if in_flake(x, y):
        col = pick(SKIN, 0.45 + 0.15 * (hash3(ix, iy, 0, 41) - 0.5))
    elif in_flake(x, y, 0.7):
        col = pick(PAINT, v - 0.22)
    # --- red diamonds
    o = outline_of(in_diamond, ix, iy)
    if o:
        if o == 2:
            col = pick(RED, 0.2)
        else:
            col = pick(RED, 0.55 + (0.12 if (in_diamond(ix + 1, iy + 1) is False) else 0)
                       - (0.1 if not in_diamond(ix - 1, iy - 1) else 0))
    # --- the painted grin
    g = outline_of(in_grin, ix, iy)
    if g:
        ax = abs(x)
        if g == 2:
            col = pick(RED, 0.18)
        else:
            vv = 0.56
            if not in_grin(ix, iy - 1) or not in_grin(ix, iy - 2):
                vv += 0.14  # glossy top edge
            if iy == -1 or iy == 0:
                vv -= 0.25  # lip line
            if ax > 10:
                vv -= 0.06
            col = pick(RED, vv)
    # --- mascara tears
    for (tx, ty), L in TEARS.items():
        if ix == tx and ty <= iy < ty + L:
            col = pick(SOCKET, 0.1) if iy < ty + L - 1 else pick(BLOOD, 0.7)
    # --- cracks (dark line, light lip below-right)
    if (ix, iy) in CRACKS:
        col = scale(col, 0.42)
    elif (ix - 1, iy - 1) in CRACKS and not in_grin(ix, iy):
        col = scale(col, 1.08)
    # --- blood running from the mouth over the chin
    if iy >= 2:
        L = BLOOD_DRIPS.get(ix)
        if L and iy < 2 + L:
            col = pick(BLOOD, 0.75 - 0.08 * (iy - 2)) if iy < 1 + L else pick(BLOOD, 0.35)
    # --- eye sockets (black), bruised rim, pinpoint pupils
    for e in EYES:
        d = eye_d(x, y, e)
        if d <= 1.0:
            col = VOID
            if d > 0.62 and y < e[1]:
                col = pick(SOCKET, 0.3)
            px, py = e[4]
            if (ix, iy) == (px, py):
                col = PUPIL
            elif (ix, iy) == (px, py + 1):
                col = PUPIL_DIM
        elif d <= 1.55:
            col = mix(col, pick(SOCKET, 0.6), 0.75)
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
def paint_or_skin(ctx, x, y, z, v):
    """Side/top/back of the head: greasepaint fading into grey rot towards the back."""
    s = z - FZ
    edge_z = 9 + 4 * (fbm(x * 0.2, y * 0.2, 3, 2, 61) - 0.5) * 2
    if s < edge_z:
        if s > edge_z - 1.2:
            return pick(PAINT, v - 0.25)
        return pick(PAINT, v + 0.04)
    sv = 0.42 + (v - 0.6) * 0.8 + (0.06 if fbm(x * 0.3, y * 0.3, z * 0.3, 2, 63) > 0.55 else 0)
    if hash3(x, y, z, 65) > 0.985:
        sv -= 0.2
    return pick(SKIN, sv)


def side_grin(s, y):
    """Painted grin running back along the cheeks onto the sides of the head."""
    if s > 6.5:
        return 0
    c = -6.3 - 0.75 * max(s, -2)
    half = 1.7 - 0.25 * max(s, -2)
    d = abs(y - c)
    if d <= half - 0.8:
        return 1
    if d <= half:
        return 2
    return 0


def head_mat(ctx):
    x, y, z = hpos(ctx)
    f = ctx.face
    ix, iy = fl(x), fl(y)
    if f == 'front':
        shift = 0.0
        if ctx.bone.name.endswith('_brow'):
            shift = -0.06
        return face_px(ix, iy, shift)
    v = 0.66 + light(ctx, 0.9)
    v = rim(ctx, v, 0.06)
    if f in ('west', 'east'):
        s = z - FZ
        g = side_grin(s, y)
        if g and y > -15:
            return pick(RED, 0.18 if g == 2 else 0.5)
        return paint_or_skin(ctx, x, y, z, v - 0.05)
    if f == 'top':
        # bald, blotched scalp: paint at the brow, rot further back, liver spots, a stitched scar
        if (abs(x - (-3 + 0.3 * (z - FZ - 10))) < 0.6) and 2 < z - FZ < 15:
            return pick(SKIN, 0.15) if fl(z) % 2 == 0 else pick(PAINT, 0.35)
        if fbm(x * 0.35, z * 0.35, 1, 2, 67) > 0.66:
            return pick(SKIN, 0.3)
        return paint_or_skin(ctx, x, y, z, v)
    if f == 'bottom':
        if ctx.cube.size[1] >= 16:  # the skull's underside is the palate
            s = z - FZ
            if s < 14:
                return pick(GUM, 0.45 + (0.18 if fl(z) % 3 == 0 else 0) - s * 0.02)
            return pick(GUM, 0.08)
        return pick(PAINT, 0.4)
    return paint_or_skin(ctx, x, y, z, v)


def jaw_mat(ctx):
    x, y, z = hpos(ctx)
    f = ctx.face
    ix, iy = fl(x), fl(y)
    if f == 'front':
        return face_px(ix, iy)
    if f == 'top':
        # inside of the mouth: tongue bed and gullet
        s = z - FZ
        if abs(x) < 4 and s < 14:
            return pick(GUM, 0.62 - s * 0.02 + (0.1 if abs(x) < 1 else 0))
        return pick(GUM, 0.3 - s * 0.015)
    v = 0.6 + light(ctx, 0.9)
    v = rim(ctx, v, 0.06)
    if f in ('west', 'east'):
        return paint_or_skin(ctx, x, y, z, v - 0.06)
    if f == 'bottom':
        return pick(SKIN, 0.38 + (0.08 if hash3(ix, 0, fl(z), 69) > 0.7 else 0))
    return paint_or_skin(ctx, x, y, z, v)


def nose_mat(ctx):
    x, y, z = hpos(ctx)
    lx, ly, lz = local(ctx)
    v = 0.55 + light(ctx, 1.2)
    # specular blob up-left on the bulb
    cx, cy = -1.2, -8.6
    if ctx.face == 'front' and ((x - cx) ** 2 + (y - cy) ** 2) < 2.2:
        v += 0.32
    elif ctx.face == 'front' and ((x - cx) ** 2 + (y - cy) ** 2) < 5.0:
        v += 0.12
    if ctx.face == 'bottom':
        v -= 0.2
    v = rim(ctx, v, 0.1)
    c = pick(RED, v)
    ix, iy = fl(x), fl(y)
    if (ix, iy) in {(1, -6), (2, -5), (1, -4), (2, -7)} and ctx.face == 'front':
        c = pick(RED, 0.12)  # cracked rubber
    return c


def teeth_mat(root, maxlen, axis, seed, grow=1, gap=2):
    """Needle teeth on a zero-thickness plane. root: head-local y of the gum line; teeth grow along
    +y (upper teeth, grow=1) or -y (lower, grow=-1). Position-only so both faces of the plane agree."""
    def f(ctx):
        x, y, z = hpos(ctx)
        u = x if axis == 'x' else z
        col = fl(u)
        if col % gap != 0:
            return None
        h = hash3(col, 0, 0, seed)
        L = 1.5 + (h ** 0.7) * (maxlen - 1.5)
        depth = (y - root) * grow
        if depth < 0 or depth > L:
            return None
        if depth < 0.8:
            return pick(GUM, 0.55)
        t = depth / L
        v = 0.75 - t * 0.12 + (0.12 if t > 0.7 else 0)
        if hash3(col, 5, 0, seed) > 0.8:
            v -= 0.3
        if hash3(col, 7, 0, seed) > 0.7 and t < 0.45:
            return pick(BLOOD, 0.75)
        return pick(TEETH, v)
    return f


# ------------------------------------------------------------------ body materials
def wrap_u(ctx, x, z):
    f = ctx.face
    if f in ('front', 'back', 'top', 'bottom'):
        return x
    return z


def suit_mat(ctx):
    x, y, z = dpos(ctx)
    lx, ly, lz = local(ctx)
    u = wrap_u(ctx, x, z)
    stripe = (fl(u + 0.5) // 3) % 2
    v = 0.56 + light(ctx, 1.0)
    v = rim(ctx, v, 0.08)
    n = fbm(x * 0.12, y * 0.12, z * 0.12, 2, 71)
    v += 0.06 if n > 0.6 else (-0.06 if n < 0.38 else 0)
    # horizontal creases where cloth bunches
    if hash3(fl(y), fl(u) // 4, 0, 73) > 0.9:
        v -= 0.12
    c = pick(MUSTARD if stripe else PURPLE, v - (0.06 if stripe else 0))
    # grime toward the hems
    if y > 12:
        c = mix(c, pick(SKIN, 0.2), min(0.6, (y - 12) / 14))
    # blood soaked into the chest under the mouth, drips running down
    if ctx.bone.name == 'body' and ctx.face == 'front':
        bx = fl(x)
        top = -40
        L = 6 + hash3(bx, 0, 0, 75) * 16 if abs(bx) < 9 else 3
        if y < top + L and hash3(bx // 2, 0, 0, 77) > 0.35:
            c = pick(BLOOD, 0.5 + (0.2 if y < top + L - 1 else -0.2))
    return c


def ruff_mat(kind):
    def f(ctx):
        x, y, z = dpos(ctx)
        lx, ly, lz = local(ctx)
        w, h, d = ctx.cube.size
        ox = ctx.cube.origin[0]
        # radial pleats across the panel width + a frayed outer edge
        col_i = fl(lx - ox)
        rad = -lz  # distance outward along the panel
        if rad > d - 1.5 and hash3(col_i, 1, 0, 81) > 0.55:
            return None
        if rad > d - 0.5:
            return None
        pleat = (col_i % 3)
        v = 0.6 + (0.12 if pleat == 0 else (-0.14 if pleat == 2 else 0)) - rad * 0.01
        if kind == 'white':
            c = pick(RUFF_W, v)
            if rad > d - 3:
                c = pick(RED, v - 0.05)
        elif kind == 'purple':
            c = pick(PURPLE, v + 0.08)
            if rad > d - 3:
                c = pick(MUSTARD, v)
        else:
            c = pick(MUSTARD, v)
            if rad > d - 3:
                c = pick(PURPLE, v)
        if hash3(fl(x), fl(y), fl(z), 83) > 0.93:
            c = pick(BLOOD, 0.6)
        return c
    return f


def glove_mat(ctx):
    x, y, z = dpos(ctx)
    lx, ly, lz = local(ctx)
    v = 0.62 + light(ctx, 1.0)
    v = rim(ctx, v, 0.08)
    if hash3(fl(x), fl(y), fl(z), 85) > 0.86:
        v -= 0.15
    c = pick(GLOVE, v - max(0, ly - 6) * 0.04)
    if ctx.cube.size[1] >= 6 and ctx.cube.size[0] <= 2:  # fingers: torn tips -> grey skin
        if ly - ctx.cube.origin[1] > ctx.cube.size[1] - 3:
            c = pick(SKIN, 0.4 + light(ctx))
    return c


def claw_mat(ctx):
    v = 0.4 + light(ctx, 1.4)
    if ctx.face in ('front', 'west') and ctx.t < 0.6:
        v += 0.25
    return pick(CLAW, v)


def shoe_mat(ctx):
    x, y, z = dpos(ctx)
    lx, ly, lz = local(ctx)
    v = 0.55 + light(ctx, 1.3)
    v = rim(ctx, v, 0.1)
    if ctx.face == 'top' and lz < -10:
        v += 0.12
    n = fbm(x * 0.3, y * 0.3, z * 0.3, 2, 87)
    if n > 0.64:
        v -= 0.18  # scuffs
    c = pick(SHOE, v)
    if hash3(fl(x), fl(y), fl(z), 89) > 0.95:
        c = pick(SOLE, 0.3)
    return c


def sole_mat(ctx):
    return pick(SOLE, 0.45 + light(ctx, 1.0))


def hair_mat(seed):
    def f(ctx):
        x, y, z = dpos(ctx)
        lx, ly, lz = local(ctx)
        n = fbm(x * 0.45, y * 0.45, z * 0.45, 2, seed)
        e = edge(ctx)
        if not flat(ctx) and e == 0 and hash3(fl(x), fl(y), fl(z), seed) > 0.55:
            return None  # frizz breaking the box outline
        v = 0.5 + light(ctx, 1.2) + (n - 0.5) * 0.9
        if hash3(fl(x * 0.7), fl(y * 1.3), fl(z * 0.7), seed + 1) > 0.8:
            v += 0.18
        return pick(HAIR, v)
    return f


def hat_mat(ctx):
    v = 0.5 + light(ctx, 1.2)
    v = rim(ctx, v, 0.12)
    x, y, z = dpos(ctx)
    if hash3(fl(x), fl(y), fl(z), 91) > 0.9:
        v += 0.2
    return pick(FELT, v)


def band_mat(ctx):
    return pick(RED, 0.4 + light(ctx, 1.0))


def neck_mat(ctx):
    x, y, z = dpos(ctx)
    v = 0.45 + light(ctx, 1.0)
    if fl(x) % 3 == 0:
        v -= 0.1  # tendons
    return pick(SKIN, v)


def balloon_mat(ctx):
    x, y, z = dpos(ctx)
    lx, ly, lz = local(ctx)
    v = 0.52 + light(ctx, 1.4)
    v = rim(ctx, v, 0.08)
    if ctx.face in ('front', 'west') and ly < -9 and (lx < -1 if ctx.face == 'front' else lz < -1):
        v += 0.2
        if ly < -11 and (lx < -3 if ctx.face == 'front' else lz < -3):
            v += 0.2
    return pick(BALLOON, v)


def string_mat(ctx):
    x, y, z = dpos(ctx)
    return pick(STRING, 0.5 + (0.2 if fl(y) % 3 == 0 else 0))


def skin_mat(ctx):
    v = 0.48 + light(ctx, 1.0)
    return pick(SKIN, rim(ctx, v))


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

    HIP = -16.0
    LEAN = 16  # torso hunch

    # ---------------- legs: baggy striped trousers, knobbly knees, enormous shoes
    LEG = {'right': ((-6, 0, -2), (14, 0, 5), (-8, 0, -3)), 'left': ((-2, 0, 3), (9, 0, -6), (-7, 0, 3))}
    for side, sx in (('right', -1), ('left', 1)):
        r_thigh, r_shin, r_shoe = LEG[side]
        leg = bone(f'{side}_leg', (5.5 * sx, HIP, 1), rot=r_thigh, mat=suit_mat)
        box(leg.name, (-4.5, -2, -4.5), (9, 19, 9))
        shin = bone(f'{side}_shin', at(leg.name, 0, 17, 0), leg.name, rot=r_shin, mat=suit_mat)
        box(shin.name, (-3.5, -1, -3.5), (7, 15, 7))
        box(shin.name, (-5, 12, -5), (10, 4, 10))
        shoe = bone(f'{side}_shoe', at(shin.name, 0, 17, 0), shin.name, rot=r_shoe, mat=shoe_mat)
        box(shoe.name, (-5.5, 5, -19), (11, 1, 24), mat=sole_mat)
        box(shoe.name, (-4.5, -1, -8), (9, 6, 13))
        box(shoe.name, (-6, 0, -19), (12, 5, 11))
        box(shoe.name, (-5, -1.5, -18), (10, 2, 9))
        if side == 'left':  # split toe, black claws poking out
            for k, cx in enumerate((-3.5, -0.5, 2.5)):
                box(shoe.name, (cx, 2 + (k % 2), -22), (1, 1, 4), mat=claw_mat)

    # ---------------- torso (hunched)
    bone('body', (0, HIP, 1), rot=(LEAN, 0, 0), mat=suit_mat)
    box('body', (-9.5, -7, -5.5), (19, 9, 11))
    box('body', (-8.5, -16, -5), (17, 10, 10))
    box('body', (-10, -25, -6), (20, 10, 12))
    box('body', (-12.5, -28, -5.5), (25, 5, 11))
    box('body', (-8, -29, 1.5), (16, 13, 8))
    for k in range(3):
        box('body', (-1.5, -26 + 4 * k, 9), (3, 3, 2), mat=skin_mat)
    for k, (yy, zz) in enumerate(((-22, -8), (-15, -7.5), (-8, -7.5))):
        box('body', (-1.5, yy, zz), (3, 3, 3), mat=hair_mat(301 + k))
    bone('coattails', at('body', 0, -7, 5.5), 'body', rot=(-LEAN + 10, 0, 0), mat=suit_mat)
    box('coattails', (-8.5, 0, 0), (8, 24, 0))
    box('coattails', (0.5, 0, 0), (8, 22, 0))

    # ---------------- ruff: two tiers of pleated panels around the neck
    bone('ruff', at('body', 0, -28, -0.5), 'body', rot=(-LEAN + 4, 0, 0))
    tiers = [  # (count, radius, width, length, droop, y offset, phase, kinds)
        (9, 4.5, 11, 13, 34, 1.0, 0.0, ('purple', 'mustard')),
        (9, 3.5, 9, 10, 18, -1.0, 20.0, ('white',)),
    ]
    for t, (n, rad, wdt, ln, droop, yo, ph, kinds) in enumerate(tiers):
        for k in range(n):
            th = ph + 360.0 * k / n
            a = math.radians(th)
            pn = f'ruff_{"lo" if t == 0 else "hi"}{k}'
            dr = droop + (8 if k % 2 else -4)
            bone(pn, at('ruff', -rad * math.sin(a), yo, -rad * math.cos(a)), 'ruff', rot=(dr, th, 0),
                 mat=ruff_mat(kinds[k % len(kinds)]))
            box(pn, (-wdt / 2, 0, -ln), (wdt, 0, ln))

    # ---------------- neck + head
    NECK = 24
    bone('neck', at('body', 0, -27, -1.5), 'body', rot=(NECK, 0, 0), mat=neck_mat)
    box('neck', (-4, -9, -4), (8, 10, 8))
    HEAD_ROT = (-(LEAN + NECK) + 6, 0, 7)
    head = bone('head', at('neck', 0, -8, -1), 'neck', rot=HEAD_ROT, mat=head_mat)
    HEAD_ABS = r.abs_pivot['head']

    def eyes_decal(cube_frm, cube_size):
        def fn(img, u0, v0, w, h):
            px = img.load()
            for j in range(h):
                for i in range(w):
                    c = eyes_glow(cube_frm[0] + i, cube_frm[1] + j)
                    if c:
                        px[u0 + i, v0 + j] = c
        return fn

    box('head', (-13, -18, FZ), (26, 18, 22), decals={'eyes:front': eyes_decal((-13, -18), (26, 18))})
    box('head', (-11, -21, FZ + 3), (22, 3, 17))                 # bald dome
    box('head', (-10, -16, FZ + 22), (20, 12, 4))                # swollen occiput
    box('head', (1, -21, FZ - 2), (9, 5, 3))                     # tumorous bulge over the left brow
    box('head', (-13, -5, FZ - 2), (9, 5, 2))                    # right cheek
    box('head', (4, -5, FZ - 2), (9, 5, 2))                      # left cheek
    box('head', (-4, -3, FZ - 2), (8, 3, 2))                     # upper lip / muzzle
    box('head', (-3, -10, FZ - 5), (6, 6, 5), mat=nose_mat)      # bulbous nose
    box('head', (-4, -9, FZ - 4), (8, 4, 4), mat=nose_mat)
    box('head', (-2, -11, FZ - 4), (4, 8, 4), mat=nose_mat)
    # upper needle teeth: three rows
    box('head', (-10, 0, FZ - 1), (20, 5, 0), mat=teeth_mat(0, 5, 'x', 201))
    box('head', (-9, 0, FZ + 2), (18, 4, 0), mat=teeth_mat(0, 4, 'x', 203))
    box('head', (-8, 0, FZ + 5), (16, 3, 0), mat=teeth_mat(0, 3, 'x', 205))
    for sx in (-1, 1):
        box('head', (10.5 * sx, 0, FZ), (0, 4, 15), mat=teeth_mat(0, 4, 'z', 207 + sx))
    for side, sx in (('right', -1), ('left', 1)):
        bone(f'{side}_brow', at('head', 1.0 * sx, -13, FZ), 'head', rot=(0, 0, 14 * -sx), mat=head_mat)
        mbox(f'{side}_brow', sx, (-11, -1.5, -2), (11, 3, 2))

    bone('jaw', at('head', 0, -1, FZ + 17), 'head', rot=(11, 0, 0), mat=jaw_mat)
    box('jaw', (-11, 0, FZ), (22, 6, 18), ref='head')
    box('jaw', (-10, 0, FZ - 2.5), (20, 2, 3), ref='head')        # lower lip
    box('jaw', (-6, 5, FZ - 1.5), (12, 4, 9), ref='head')          # long jutting chin
    box('jaw', (-10, -5, FZ - 1.6), (20, 5, 0), mat=teeth_mat(0, 5, 'x', 211, grow=-1), ref='head')
    box('jaw', (-9, -4, FZ + 1.5), (18, 4, 0), mat=teeth_mat(0, 4, 'x', 213, grow=-1), ref='head')
    for sx in (-1, 1):
        box('jaw', (9.8 * sx, -4, FZ + 1), (0, 4, 14), mat=teeth_mat(0, 4, 'z', 215 + sx, grow=-1), ref='head')

    # tiny dented top hat, jammed askew
    bone('hat', at('head', 5, -21, FZ + 12), 'head', rot=(-8, 0, 22), mat=hat_mat)
    box('hat', (-6.5, -1, -6), (13, 1, 12))
    box('hat', (-4.5, -10, -4), (5, 9, 8))
    box('hat', (0.5, -8, -4), (4, 7, 8))
    box('hat', (-4.5, -3, -4), (9, 2, 8), mat=band_mat, inflate=0.3)

    # frizzy red hair exploding from the temples
    for side, sx in (('right', -1), ('left', 1)):
        hn = f'hair_{side}'
        bone(hn, at('head', 12.5 * sx, -11, FZ + 13), 'head', rot=(0, 0, 8 * -sx), mat=hair_mat(311 + sx))
        mbox(hn, sx, (-8, -7, -7), (9, 14, 13))
        mbox(hn, sx, (-13, -13, -5), (9, 9, 10))
        mbox(hn, sx, (-12, 3, -5), (8, 9, 10))
        mbox(hn, sx, (-16, -4, -4), (6, 9, 8))
        mbox(hn, sx, (-15, -16, 0), (10, 30, 0))

    # ---------------- arms: long, with puffed shoulders and frilled cuffs
    ARM = {'right': ((-LEAN - 30, 0, 6), (-55, 0, 0), (10, 0, 0)), 'left': ((-LEAN + 10, 0, -4), (-14, 0, 0), (-6, 0, 0))}
    for side, sx in (('right', -1), ('left', 1)):
        ra, rf, rh = ARM[side]
        arm = bone(f'{side}_arm', at('body', 12.5 * sx, -25, 0), 'body', rot=ra, mat=suit_mat)
        box(arm.name, (-4.5, -3, -4.5), (9, 8, 9))
        box(arm.name, (-3, 2, -3), (6, 17, 6))
        fa = bone(f'{side}_forearm', at(arm.name, 0, 18, 0), arm.name, rot=rf, mat=suit_mat)
        box(fa.name, (-2.5, -1, -2.5), (5, 16, 5))
        box(fa.name, (-4, 12, -4), (8, 3, 8), mat=ruff_mat('white'))
        hand = bone(f'{side}_hand', at(fa.name, 0, 15, 0), fa.name, rot=rh, mat=glove_mat)
        box(hand.name, (-3.5, -1, -2.5), (7, 3, 5))
        box(hand.name, (-3, 1, -2), (6, 7, 4))
        for k, fx in enumerate((-3, -1, 1)):
            ln = (9, 10, 8)[k]
            box(hand.name, (fx, 7, -1.5), (2, ln, 2))
            box(hand.name, (fx + 0.5, 7 + ln - 0.5, -1), (1, 4, 1), mat=claw_mat)
        mbox(hand.name, -sx, (-5, 2, -2), (2, 6, 2))
        mbox(hand.name, -sx, (-4.5, 7.5, -1.5), (1, 3, 1), mat=claw_mat)

    # balloon on a string, held up from the right hand
    ra, rf, rh = ARM['right']
    net = ra[0] + LEAN + rf[0] + rh[0]
    bone('balloon_string', at('right_hand', 0, 5, 0), 'right_hand', rot=(-net, 0, -14), mat=string_mat)
    SL = 46
    box('balloon_string', (0, -SL, -0.5), (0, SL, 1))
    box('balloon_string', (-0.5, -SL, 0), (1, SL, 0))
    bone('balloon', at('balloon_string', 0, -SL, 0), 'balloon_string', rot=(0, 0, 10), mat=balloon_mat)
    box('balloon', (-1, -2, -1), (2, 2, 2))
    box('balloon', (-6, -15, -6), (12, 13, 12))
    box('balloon', (-7, -13, -5), (14, 9, 10))
    box('balloon', (-5, -13, -7), (10, 9, 14))
    box('balloon', (-5, -16, -5), (10, 15, 10))

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
        'jaw': (0.95, 0, 0, 0, 0, 0),
        'head': (-0.15, 0, 0.52, 0, 0, 0),
        'neck': (0.25, 0, 0, 0, 0, 0),
        'body': (0.18, 0, 0, 0, 0, 0),
        'right_arm': (-1.2, 0, 0.15, 0, 0, 0),
        'left_arm': (-1.5, 0, -0.2, 0, 0, 0),
        'right_forearm': (0.6, 0, 0, 0, 0, 0),
        'left_forearm': (-0.2, 0, 0, 0, 0, 0),
    },
    'laugh': {
        'jaw': (0.75, 0, 0, 0, 0, 0),
        'head': (-0.6, 0, -0.12, 0, 0, 0),
        'neck': (-0.35, 0, 0, 0, 0, 0),
        'body': (-0.2, 0, 0, 0, 0, 0),
        'right_arm': (0.1, 0, 0.3, 0, 0, 0),
        'left_arm': (0.25, 0, -0.5, 0, 0, 0),
        'left_forearm': (-0.6, 0, 0, 0, 0, 0),
    },
    'scream': {
        'jaw': (1.05, 0, 0, 0, 0, 0),
        'head': (0.2, 0, 0, 0, 0, 0),
        'neck': (0.2, 0, 0, 0, 0, 0),
        'right_arm': (-0.3, 0, 0.7, 0, 0, 0),
        'left_arm': (-0.3, 0, -0.8, 0, 0, 0),
        'right_hair': (0, 0, 0.2, 0, 0, 0),
    },
}
ANIM_NOTES = """
body: hunched torso pivoting at the hips; bob +-2 deg on each step, lean further (+0.2 rad) when chasing.
neck/head: share look-at (neckShare 0.4); idle: slow head roll on Z (+-0.15 rad, 6 s period) and sudden
  'tilt snaps' every few seconds. jaw: idle chatter 0..0.12 rad; attack/scream/laugh open to ~1 rad.
right_brow/left_brow: tiny Z twitch when the jaw opens (furrow). hat: wobbles with head roll (lagged).
hair_left/hair_right: spring-lagged Z wobble when the head moves. ruff (+ ruff_lo*/ruff_hi* panels): rigid.
right_arm/left_arm (+ _forearm, _hand): long dangling swing on walk (armAmp 0.5), left arm sways loosely;
  chase: both arms forward reaching (-1.2..-1.5 rad). Right hand keeps the balloon:
  balloon_string should counter-rotate the net arm swing so it stays upright; balloon bobs (+-0.1 rad Z).
right_leg/left_leg (+ _shin, _shoe): walk swing (legAmp 0.7) with shin flex 0..0.5 rad; big shoes flap.
coattails: lagged X swing behind the legs.
Poses: attack (lunge, jaw open huge, arms reaching, head tilted 30 deg), laugh (head thrown back, jaw open),
scream (jaw max, arms spread).
"""
