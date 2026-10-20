"""Sonrisas -- the demonic circus clown of DEAD LINE (module key: payaso).

Authored at 2x texel density (model.scale = 0.5) with rig.Rig absolute coordinates:
+Y down, ground at y = 24, the creature faces -Z, right_* parts on -X.
Every cube is authored in its bone's *unrotated* design frame; bone rotations fold the hunch.

Silhouette: lanky stilt legs with knobbly knees, a narrow waist, a spine that tips forward into a
hump of shoulder blades, long dangling arms, an onion-shaped bald head (swollen stepped dome,
pinched temples, cheek ledges, long pointed jaw) with flaming horns of red hair, a flared two-tier
pleated ruff and enormous red shoes. The face is painted from one 2D face map in head-local
coordinates, so every front-facing cube of the head and jaw shares the same painting.
"""
import math

import numpy as np

from mcmodel import Model, fbm, hash3, face_light, pick
from rig import Rig
from paint import hx, mix, scale, edge


def pal(*h):
    return [hx(c) for c in h]


# ------------------------------------------------------------------ palettes (dark -> light)
PAINT = pal('#24202a', '#3a3540', '#57505b', '#78717a', '#9a939a', '#bdb7b5', '#d9d4cb', '#ece9df', '#fbfaf2')
SKIN = pal('#0f100f', '#1b1d1a', '#292c26', '#383c33', '#494d41', '#5c5f51', '#717363', '#888977', '#a09f8b', '#b6b39d')
RED = pal('#130104', '#2a0307', '#47060b', '#6a0b11', '#8f1217', '#b41c1f', '#d5332b', '#f05a3c', '#ff8d5f')
BLOOD = pal('#0e0102', '#1c0204', '#2c0507', '#3e080b', '#530c0f', '#6a1215', '#821a1a')
VOID = hx('#020102')
SOCKET = pal('#060204', '#12070b', '#200d14', '#30131c')
PUPIL = hx('#fff6b0')
PUPIL_DIM = hx('#b8400c')
HAIR = pal('#1a0402', '#330803', '#540f05', '#781a08', '#9c280b', '#c03b0f', '#df5715', '#f57d24', '#ffad52')
PURPLE = pal('#0a050d', '#150b1b', '#22122b', '#311a3c', '#41224e', '#522b61', '#653574', '#7a4288')
MUSTARD = pal('#161004', '#291e07', '#3f2f0b', '#584311', '#735817', '#8f6f1f', '#a98a2b', '#c4a63e')
RUFF_W = pal('#2a272c', '#454146', '#666062', '#8a8381', '#ada6a0', '#cbc5bc', '#e2ddd3', '#f3f0e8')
GLOVE = pal('#28241f', '#423b34', '#5f574d', '#7e7467', '#9d9282', '#bbb09c', '#d4cab6', '#e8e0cf')
CLAW = pal('#020102', '#070608', '#0f0d11', '#19161b', '#252128', '#38323b', '#4e4752')
SHOE = pal('#110203', '#230407', '#3b070b', '#5a0c11', '#7b1318', '#9c1c1f', '#bc2a28', '#d84634', '#ef7050')
SOLE = pal('#060506', '#0e0c0e', '#181518', '#252124', '#353034')
FELT = pal('#040305', '#09080b', '#110e14', '#1a161e', '#241f29', '#302936', '#3f3646', '#51475a')
TEETH = pal('#2d2216', '#4d3d27', '#71603f', '#988457', '#bba86f', '#d6c88f', '#ebe2b6', '#f8f3dc')
GUM = pal('#0a0203', '#180407', '#2c080c', '#451014', '#62191d', '#80282a', '#9c3c3a', '#b8564f')
BALLOON = pal('#260104', '#450209', '#6b060f', '#950b17', '#bd1421', '#de2a2f', '#f85548', '#ff9c88', '#ffe4da')
STRING = pal('#2f2b27', '#524c45', '#7c756a', '#a69e90', '#c9c1b2')
POM_Y = pal('#2a1a04', '#4d3307', '#7a540c', '#a87a12', '#cf9d1c', '#ecc236', '#fbe06a', '#fff3a8')
PATCH = pal('#0d1514', '#16231f', '#22332c', '#304538', '#405846', '#536b55')

HEAD_ABS = (0.0, 0.0, 0.0)  # set by build(): design-space pivot of the head
STRING_DIR = (-0.36, -0.93, 0.08)  # world direction of the balloon string (hand -> balloon)
RUFF_ROLL, RUFF_DROOP = 62, 14
FZ = -11.0  # head-local z of the face plane (cranium / eye block fronts)


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
            if e2 >= dy and e2 <= dx:  # diagonal step: add the elbow texel so lines stay 4-connected
                out.add((x + sx, y))
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


# ------------------------------------------------------------------ rotation helpers
def _rx(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def _ry(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def _rz(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def euler_zyx(R):
    """Rotation matrix -> Minecraft bone rotation (x, y, z) in degrees (R = Rz * Ry * Rx)."""
    b = math.asin(max(-1.0, min(1.0, -R[2, 0])))
    a = math.atan2(R[2, 1], R[2, 2])
    c = math.atan2(R[1, 0], R[0, 0])
    return math.degrees(a), math.degrees(b), math.degrees(c)


def aim_matrix(d, normal_hint):
    d = np.array(d, float)
    d /= np.linalg.norm(d)
    e2 = -d
    n = np.array(normal_hint, float)
    n = n - np.dot(n, e2) * e2
    n /= np.linalg.norm(n)
    e1 = np.cross(e2, n)
    return np.column_stack([e1, e2, n])


def aim(d, normal_hint):
    """Bone rotation whose local -Y points along d and whose local Z leans towards normal_hint."""
    return euler_zyx(aim_matrix(d, normal_hint))


def world_rot(b):
    """Rest-pose world rotation matrix of a rig bone (product of the parent chain)."""
    chain = []
    while b is not None:
        chain.append(b)
        b = b.parent
    R = np.eye(3)
    for bb in reversed(chain):
        R = R @ _rz(math.radians(bb.rot[2])) @ _ry(math.radians(bb.rot[1])) @ _rx(math.radians(bb.rot[0]))
    return R


def rot_in(parent, R_world):
    """Local rotation (degrees) that gives a child of `parent` the world orientation R_world."""
    return euler_zyx(world_rot(parent).T @ R_world)


def petal(theta, droop, roll):
    """Ruff panel: authored hanging along +Y; yaw theta around the neck (0 = front, 90 = -X side),
    droop below the horizontal, roll around its own radial axis (the pleat). Degrees."""
    r = math.radians
    R = _ry(r(theta)) @ _rx(-r(90 - droop)) @ _ry(r(roll))
    return euler_zyx(R)


# ------------------------------------------------------------------ the face map (head-local texels)
EYES = [  # centre x, centre y, radius x, radius y, glow core top-left texel
    (-7.3, -9.7, 3.5, 3.0, (-8, -10)),
    (7.4, -10.0, 3.8, 3.3, (7, -11)),   # the clown's left eye: bigger, a crack runs through it
]
DIAMOND = (5.0, 11.5, 4.2)  # half width, half height up, half height down


def in_diamond(ix, iy):
    x, y = ix + 0.5, iy + 0.5
    for cx, cy, _, _, _ in EYES:
        hw, hu, hd = DIAMOND
        hh = hu if y < cy else hd
        if abs(x - cx) / hw + abs(y - cy) / hh <= 1.0:
            return True
    return False


def grin_top(x):
    return -1.3 - 0.05 * x * x


def grin_bot(x):
    return min(1.0, 2.5 - 0.052 * x * x)


def in_grin(ix, iy):
    """The painted red smile on the head: upper lip over the real mouth, curling up the cheeks."""
    x, y = ix + 0.5, iy + 0.5
    if abs(x) > 14.5:
        return False
    return grin_top(abs(x)) <= y <= grin_bot(abs(x))


def grin_slit(ix, iy):
    """Glasgow smile: the paint hides a cut that runs from the mouth corners up the cheeks, stitched."""
    x, y = ix + 0.5, iy + 0.5
    ax = abs(x)
    if ax < 8.2 or not in_grin(ix, iy):
        return 0
    mid = (grin_top(ax) + grin_bot(ax)) / 2
    if abs(y - mid) < 0.55:
        return 1
    if ix % 3 == 0 and abs(y - mid) < 1.6:
        return 2
    return 0


def lower_lip(x):
    return 1.0 + 2.7 * max(0.0, 1.0 - (x / 8.4) ** 2)


CRACKS = set()
for _pl in [
    [(6, -25), (7, -23), (6, -21), (8, -19), (8, -16), (9, -14)],   # dome down into the left eye
    [(8, -19), (11, -18), (12, -16)],                                # branch to the temple
    [(9, -6), (10, -4)],                                             # ...and out below the socket
    [(-3, -24), (-4, -22), (-3, -20), (-5, -18)],                    # forehead split
]:
    CRACKS |= raster(_pl)
BLOOD_DRIPS = {-6: 5, -3: 9, -2: 4, 1: 7, 3: 3, 5: 10, 6: 4}  # jaw column -> drip length below the lower lip


def eye_d(x, y, e):
    cx, cy, rx, ry, _ = e
    return ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2


def paint_line(ix):
    """Head-local y where the greasepaint ends on the forehead and the grey dome begins."""
    return -23.0 + (hash3(ix, 3, 0, 57) - 0.5) * 2.4 + (1.2 if ix % 5 == 0 else 0)


def face_px(ix, iy):
    """Front colour of the face map at head-local integer texel (ix, iy)."""
    x, y = ix + 0.5, iy + 0.5
    ax = abs(x)
    # --- greasepaint base with volume (key light from the upper left)
    v = 0.87 - 0.22 * (ax / 13.5) ** 2.4
    if y < -13:
        v += 0.04 * max(0.0, 1 - ax / 9)
    for e in EYES:  # brow shadow over each socket
        dy = y - (e[1] - e[3] - 1.0)
        if abs(x - e[0]) < e[2] + 2.5 and -2.5 < dy < 0.8:
            v -= 0.09
    if -7 < y < -2 and 8 < ax < 13:
        v += 0.05  # cheekbones
    if 3.4 < x < 6.5 and -10 < y < -2:
        v -= 0.09  # nose shadow
    if y > 2:
        v -= 0.05 + 0.016 * (y - 2)
    if x > 9:
        v -= 0.04
    col = pick(PAINT, v)
    # --- grey rotting dome above the paint line
    pl = paint_line(ix)
    if y < pl:
        return skin_front(ix, iy)
    if y < pl + 1:
        col = pick(PAINT, v - 0.25)
    # --- red diamonds (long, from the forehead to the cheekbone)
    o = outline_of(in_diamond, ix, iy)
    if o == 2:
        col = pick(BLOOD, 0.2)
    elif o == 1:  # deep crimson, darker than the grin and the nose
        vv = 0.5
        if not in_diamond(ix - 1, iy) or not in_diamond(ix, iy - 1):
            vv += 0.1
        elif not in_diamond(ix + 1, iy) or not in_diamond(ix, iy + 1):
            vv -= 0.12
        col = pick(RED, vv)
    # --- the painted grin (outline, glossy upper edge, dark crease where it meets the real lips)
    g = outline_of(in_grin, ix, iy)
    if g == 2:
        col = pick(RED, 0.2)
    elif g == 1:
        vv = 0.6
        if not in_grin(ix, iy - 1):
            vv += 0.16
        elif not in_grin(ix, iy - 2):
            vv += 0.07
        if not in_grin(ix, iy + 1):
            vv -= 0.16
        col = pick(RED, vv)
    gs = grin_slit(ix, iy)
    if gs == 1:
        col = pick(BLOOD, 0.45)
    elif gs == 2:
        col = pick(SOCKET, 0.35)
    # --- long branching cracks: dark split with a lit lip above-left
    if (ix, iy) in CRACKS:
        col = pick(SKIN, 0.16)
    elif (ix + 1, iy + 1) in CRACKS or (ix + 1, iy) in CRACKS:
        col = scale(col, 1.1)
    # --- eye sockets: thin dark ring, black hollow, emissive 2x2 pupil + dim halo
    for e in EYES:
        d = eye_d(x, y, e)
        if d <= 1.0:
            col = VOID
            if d > 0.7 and y < e[1] - 1.5:
                col = pick(SOCKET, 0.35)
            gl = eyes_glow(ix, iy)
            if gl is PUPIL:
                col = gl
            elif gl is PUPIL_DIM:
                col = pick(RED, 0.3)  # the halo only blazes on the emissive layer
        elif d <= 1.38:
            col = pick(SOCKET, 0.6)
    return col


def eyes_glow(ix, iy):
    for e in EYES:
        px, py = e[4]
        if px <= ix <= px + 1 and py <= iy <= py + 1:
            return PUPIL
        if (px - 1 <= ix <= px + 2 and py <= iy <= py + 1) or (px <= ix <= px + 1 and py - 1 <= iy <= py + 2):
            return PUPIL_DIM
    return None


SCALP_SPOTS = [(-6.0, 6.0, 1.8, 1.3), (4.5, 12.0, 1.3, 1.1), (8.0, 4.0, 1.1, 0.9), (-2.0, 15.0, 2.0, 1.5)]
SCAR = raster([(-8, 2), (-5, 5), (-4, 9), (-1, 12), (0, 16)])
VEINS = raster([(3, -26), (4, -24), (3, -22)]) | raster([(-6, -25), (-7, -23)]) | raster([(9, -24), (11, -23)])


def skin_front(ix, iy):
    v = 0.74 - 0.12 * (abs(ix + 0.5) / 12.0) ** 2
    if (ix, iy) in VEINS:
        return pick(SKIN, 0.42)
    if hash3(ix, iy, 0, 59) > 0.86:
        v -= 0.12
    return pick(SKIN, v)


def skin_px(x, y, z, v):
    sv = 0.62 + (v - 0.66) * 0.9
    if hash3(fl(x * 0.5), fl(y * 0.5), fl(z * 0.5), 63) > 0.84:
        sv -= 0.12
    return pick(SKIN, sv)


def paint_depth(y):
    """How far back from the face plane the greasepaint reaches on the sides (ragged, per row)."""
    return 6.5 + fl(hash3(fl(y), 0, 0, 61) * 3.5)


def side_grin(s, y):
    """The painted grin continues back along the temples towards the ears, narrowing to a hook."""
    if s > 9.5:
        return 0
    top = -8.5 - 0.5 * s
    bot = -6.0 - 0.75 * s
    if bot < top:
        return 0
    if top <= y <= bot:
        return 2 if (y - top < 0.9 or bot - y < 0.9) else 1
    return 0


def head_mat(ctx):
    x, y, z = hpos(ctx)
    f = ctx.face
    ix, iy = fl(x), fl(y)
    if f == 'front':
        return face_px(ix, iy)
    s = z - FZ
    v = 0.7 + light(ctx, 0.9)
    v = rim(ctx, v, 0.06)
    if f in ('west', 'east'):
        if y > -14:
            g = side_grin(s, y)
            if g:
                return pick(RED, 0.2 if g == 2 else 0.55)
        if y < paint_line(fl(z)) - 1:
            return skin_px(x, y, z, v)
        pd = paint_depth(y)
        if s < pd:
            return pick(PAINT, v - 0.1 - 0.012 * s)
        if s < pd + 1:
            return pick(PAINT, v - 0.34)
        return skin_px(x, y, z, v)
    if f == 'top':
        if y > -20 and s < 1.5 + hash3(ix, 0, 0, 67) * 2.0:
            return pick(PAINT, v - 0.05)
        if (ix, fl(s)) in SCAR:
            return pick(SKIN, 0.1)
        if (ix - 1, fl(s)) in SCAR or (ix + 1, fl(s)) in SCAR:
            if fl(s) % 2 == 0:
                return pick(SKIN, 0.22)  # stitches
        for cx, cs, rx, rs in SCALP_SPOTS:
            if ((x - cx) / rx) ** 2 + ((s - cs) / rs) ** 2 <= 1:
                return pick(SKIN, 0.3)
        return skin_px(x, y, z, v + 0.06)
    if f == 'bottom':
        if ctx.cube.size[1] == 5 and ctx.cube.size[0] == 18:  # maxilla underside = palate
            if abs(x) < 8 and s < 4:
                return pick(GUM, 0.5 + (0.14 if fl(s) % 2 == 0 else 0) - s * 0.03)
            return pick(GUM, 0.12)
        return pick(PAINT, 0.3) if s < 4 else skin_px(x, y, z, 0.5)
    return skin_px(x, y, z, v)


def jaw_mat(ctx):
    x, y, z = hpos(ctx)
    f = ctx.face
    ix, iy = fl(x), fl(y)
    s = z - FZ
    if f == 'front':
        col = face_px(ix, iy)
        lip = lower_lip(x + 0.0)
        if y < lip:
            vv = 0.56
            if y < 1.9:
                vv = 0.22  # where the lips part
            elif y < 2.9:
                vv = 0.7   # wet highlight
            if y > lip - 1:
                vv = 0.2
            col = pick(RED, vv)
        L = BLOOD_DRIPS.get(ix)
        if L and lip - 1 <= y < lip + L:
            col = pick(BLOOD, 0.85 - 0.06 * (y - lip)) if y < lip + L - 1 else pick(BLOOD, 0.4)
        return col
    if f == 'top':
        if ctx.cube.size[2] >= 12:  # inside of the mouth: tongue groove, gums and gullet
            if abs(x) < 3 and s < 11:
                return pick(GUM, 0.62 - s * 0.03 + (0.1 if abs(x) < 1 else 0))
            if s < 1.2:
                return pick(GUM, 0.42)
            return pick(GUM, 0.32 - s * 0.015)
        return pick(PAINT, 0.5)
    v = 0.6 + light(ctx, 0.9)
    v = rim(ctx, v, 0.06)
    if f in ('west', 'east'):
        if s < paint_depth(y + 40) - 1:
            return pick(PAINT, v - 0.1)
        return skin_px(x, y, z, v)
    if f == 'bottom':
        return pick(SKIN, 0.38 + (0.08 if hash3(ix, 0, fl(z), 69) > 0.7 else 0))
    return skin_px(x, y, z, v)


def nose_mat(ctx):
    x, y, z = hpos(ctx)
    v = 0.56 + light(ctx, 1.2)
    cx, cy = -1.0, -8.2
    d2 = (x - cx) ** 2 + (y - cy) ** 2
    if ctx.face == 'front':
        if d2 < 1.6:
            v += 0.36
        elif d2 < 5.0:
            v += 0.13
        if x > 1.5 and y > -5.5:
            v -= 0.1
    if ctx.face == 'top':
        v += 0.05
    if ctx.face == 'bottom':
        v -= 0.25
    v = rim(ctx, v, 0.12)
    c = pick(RED, v)
    if ctx.face in ('front', 'east') and (fl(x), fl(y)) in {(1, -5), (2, -4), (2, -6), (3, -7), (-2, -4), (-3, -3)}:
        c = pick(RED, 0.12)  # cracked rubber
    return c


# needle teeth: (centre x, half width at the root, length, lean per texel, broken)
UPPER_TEETH = [(-7.5, 0.6, 3.5, 0.25, False), (-5.5, 1.1, 10.0, 0.12, False), (-3.7, 0.6, 4.0, -0.2, True),
               (-2.3, 0.8, 6.5, 0.05, False), (-0.5, 0.6, 3.0, -0.3, False), (1.0, 0.8, 7.5, -0.08, False),
               (2.7, 0.6, 4.0, 0.22, False), (4.2, 0.6, 5.0, -0.25, True), (5.6, 1.1, 9.5, -0.14, False),
               (7.5, 0.5, 3.0, -0.3, False)]
LOWER_TEETH = [(-6.8, 0.6, 3.5, -0.25, False), (-4.8, 1.0, 8.5, 0.1, False), (-3.0, 0.6, 3.0, 0.2, True),
               (-1.5, 0.7, 5.5, -0.18, False), (0.4, 0.6, 3.0, 0.0, False), (2.0, 0.7, 6.0, 0.22, False),
               (3.6, 0.6, 3.5, -0.1, True), (5.2, 1.0, 8.0, 0.12, False), (7.0, 0.5, 3.0, -0.3, False)]


def teeth_mat(teeth, root, grow):
    """Needle teeth on a zero-thickness plane: root = head-local y of the gum line, teeth grow along
    +y (upper, grow=1) or -y (lower, grow=-1). Uneven, crooked, some snapped; bloody at the root."""
    def f(ctx):
        x, y, z = hpos(ctx)
        depth = (y - root) * grow
        if depth < 0:
            return None
        if depth < 0.9:
            return pick(GUM, 0.5 + (0.12 if fl(x) % 3 == 0 else 0))
        for k, (cx, hw, L, lean, broken) in enumerate(teeth):
            if depth > L:
                continue
            t = depth / L
            c = cx + lean * depth
            half = hw * (1 - t) ** 1.2 + 0.1
            dx = x - c
            if abs(dx) > half and fl(x) != fl(c):
                continue
            if broken and t > 0.62:
                return pick(TEETH, 0.18)  # snapped stump
            if t < 0.22:
                vv = 0.62 - 0.2 * (1 - t / 0.22)
                return pick(BLOOD, vv + 0.25) if hash3(k, fl(depth), 0, 223) > 0.35 else pick(GUM, 0.55)
            if t < 0.45:
                v = 0.32 + t * 0.4
            else:
                v = 0.55 + t * 0.32
            if dx > half - 0.7:
                v -= 0.16  # shaded flank
            if k % 4 == 1:
                v -= 0.08
            return pick(TEETH, v)
        return None
    return f


def throat_mat(ctx):
    """Black void curtain right behind the teeth: the mouth always reads as a dark hole."""
    x, y, z = hpos(ctx)
    if y < 2.2:
        return pick(GUM, 0.28 - (y + 1) * 0.06)
    if abs(x) > 6.5:
        return pick(GUM, 0.08)
    return VOID


# ------------------------------------------------------------------ hair
JAG = [1.0, 0.66, 0.9, 0.55, 0.97, 0.74, 1.0, 0.6, 0.88, 0.7, 0.95, 0.58, 0.84, 0.68, 1.0, 0.63]
STRAND_V = [0.06, -0.08, 0.12, 0.0, -0.12, 0.08, -0.04, 0.14, -0.1, 0.02]


def tuft_len(i, w, h, phase):
    u = (i + 0.5) / w - 0.5
    env = 1.0 - 0.8 * (2 * abs(u)) ** 1.7
    return h * env * JAG[(i + phase) % len(JAG)]


def tuft_plane_mat(phase):
    """Flame-shaped frizz plane authored at (-w/2, -h, 0): zig-zag strand tips, strand shading."""
    def f(ctx):
        lx, ly, lz = local(ctx)
        c = ctx.cube
        w, h, _ = c.size
        i = fl(lx - c.origin[0])
        depth = -ly
        L = tuft_len(i, w, h, phase)
        if depth > L:
            return None
        t = depth / max(L, 1)
        v = 0.3 + 0.48 * t + STRAND_V[(i // 2 + phase) % len(STRAND_V)]
        if depth > L - 1.5:
            v += 0.1  # light tips
        edge_l = i == 0 or tuft_len(i - 1, w, h, phase) < depth
        edge_r = i == w - 1 or tuft_len(i + 1, w, h, phase) < depth
        if edge_l or edge_r:
            v -= 0.16  # dark strand outline
        return pick(HAIR, v)
    return f


def tuft_mat(phase, length):
    """Hair cubes in a tuft's frame (tuft grows along local -Y): strands follow the tuft axis."""
    def f(ctx):
        lx, ly, lz = local(ctx)
        fc = ctx.face
        depth = -ly
        if fc in ('front', 'back'):
            col = fl(lx * 1.0)
        elif fc in ('west', 'east'):
            col = fl(lz * 1.0) + 3
        else:
            col = fl(lx) + fl(lz) * 3
        t = max(0.0, min(1.0, depth / length))
        v = 0.3 + 0.42 * t + STRAND_V[(col // 1 + phase) % len(STRAND_V)] + light(ctx, 1.0)
        if fc == 'top':
            v += 0.12
        if fc == 'bottom':
            v -= 0.1
        return pick(HAIR, v)
    return f


def frizz_back_mat(ctx):
    """Back horseshoe of hair: vertical strands with a ragged lower edge over the collar."""
    lx, ly, lz = local(ctx)
    c = ctx.cube
    w, h, _ = c.size
    i = fl(lx - c.origin[0])
    depth = ly - c.origin[1]
    u = abs((i + 0.5) / w - 0.5) * 2
    L = h * (0.62 + 0.38 * JAG[(i + 3) % len(JAG)]) - 3 * u * u
    if depth > L:
        return None
    if depth < 2.5 + 2.5 * (1 - u) and u < 0.75:
        top = True
    else:
        top = False
    v = 0.36 + 0.3 * (depth / h) + STRAND_V[(i // 2) % len(STRAND_V)]
    if depth > L - 1.5:
        v += 0.08
    if top:
        v -= 0.08
    return pick(HAIR, v)


# ------------------------------------------------------------------ body materials
def stripe_u(ctx, lx, lz):
    return lx if ctx.face in ('front', 'back', 'top', 'bottom') else lz


JOINT_ENDS = {'_arm': 'both', '_forearm': 'top', '_shin': 'top', '_leg': 'bottom'}


def suit_mat(ctx):
    x, y, z = dpos(ctx)
    lx, ly, lz = local(ctx)
    bn = ctx.bone.name
    u = stripe_u(ctx, lx, lz)
    wob = 0.9 * math.sin(ly * 0.33 + u * 0.21 + (1.7 if bn.startswith('left') else 0))
    k = fl(u + wob + 0.5)
    stripe = (k % 6) in (0, 1)
    v = 0.6 + light(ctx, 1.0)
    v = rim(ctx, v, 0.1)
    n = fbm(x * 0.11, y * 0.11, z * 0.11, 2, 71)
    v += 0.07 if n > 0.6 else (-0.07 if n < 0.38 else 0)
    # folds: diagonal creases near the joints
    c0, h0 = ctx.cube.origin[1], ctx.cube.size[1]
    near_top = ly - c0 < 3.5
    near_bot = c0 + h0 - ly < 3.5
    jt = next((m for s_, m in JOINT_ENDS.items() if bn.endswith(s_)), None)
    if (jt in ('top', 'both') and near_top) or (jt in ('bottom', 'both') and near_bot) or (bn == 'body' and -9 < ly < -6):
        v -= 0.1
        if (fl(u) + fl(ly)) % 4 == 0:
            v -= 0.14
    if hash3(fl(ly), fl(u) // 4, 0, 73) > 0.92:
        v -= 0.12
    c = pick(MUSTARD, v - 0.02) if stripe else pick(PURPLE, v)
    # patch on the left thigh, stitched
    if bn == 'left_leg' and ctx.face == 'front' and -2 <= lx < 2 and 4 <= ly < 10:
        c = pick(PATCH, 0.55 + light(ctx) + (0.1 if (fl(lx) // 2 + fl(ly) // 2) % 2 else -0.05))
        if (lx < -1 or ly < 5) and (fl(lx) + fl(ly)) % 2 == 0:
            c = pick(PURPLE, 0.1)  # coarse stitches on the patch edge
    # mud on the hems
    if y > 8:
        c = mix(c, pick(SKIN, 0.16), min(0.6, (y - 8) / 14))
    # blood bib: from the mouth down the shirt front
    if ctx.face == 'front' and bn in ('chest', 'body'):
        top = -14 if bn == 'chest' else -13
        ax = abs(lx + 1.2)
        L = (14 if bn == 'chest' else 6) - ax * 1.1 + hash3(fl(lx), 0, 0, 75 if bn == 'chest' else 76) * 7
        if ax < 6.5 and ly < top + L:
            c = pick(BLOOD, 0.8 - 0.25 * (ly - top) / max(L, 1)) if ly < top + L - 1.2 else pick(BLOOD, 0.45)
    # torn back: grey skin and vertebrae showing through a rip
    if bn == 'chest' and ctx.face == 'back' and abs(lx) < 3.2 - 0.25 * abs(ly + 6) + hash3(fl(ly), 0, 0, 77):
        c = pick(SKIN, 0.4 + light(ctx))
    # frayed trouser hems
    if bn.endswith('_shin') and ly > c0 + h0 - 2.0 and ctx.face in ('front', 'back', 'west', 'east'):
        if hash3(fl(u), 1, 0, 79) > 0.45:
            c = pick(PURPLE, 0.15)
    return c


def ruff_mat(kind, seed, splatter=False):
    """Pleated ruff panel authored hanging along +Y: scalloped outer edge, fold shading, trim."""
    def f(ctx):
        lx, ly, lz = local(ctx)
        w, h, d = ctx.cube.size
        u = (lx - ctx.cube.origin[0]) / w   # 0..1 across the pleat
        ci = fl(lx - ctx.cube.origin[0])
        rad = ly
        scal = 1.6 * abs(math.sin((ci + 0.5) * math.pi / 4.0))
        if rad > h - scal - (1.0 if hash3(ci, 1, 0, seed) > 0.75 else 0):
            return None
        fold = math.cos((u - 0.3) * math.pi * 2)
        v = 0.6 + 0.16 * fold - (0.12 if abs(u - 0.8) < 0.07 else 0)
        if rad < 3:
            v -= 0.18 * (3 - rad) / 3
        if kind == 'white':
            c = pick(RUFF_W, v + 0.06)
            if rad > h - scal - 2.6:
                c = pick(RED, v - 0.02)
        elif kind == 'red':
            c = pick(RED, v - 0.02)
            if rad > h - scal - 2.6:
                c = pick(RUFF_W, v)
        else:  # cream upper tier with purple trim
            c = pick(RUFF_W, v - 0.02)
            if rad > h - scal - 2.2:
                c = pick(PURPLE, v + 0.18)
        if splatter:
            x, y, z = dpos(ctx)
            if hash3(fl(x / 2), fl(y / 2), fl(z / 2), seed + 7) > 0.55 and rad < h * 0.7:
                c = pick(BLOOD, 0.7)
        elif hash3(fl(lx / 2), fl(ly / 2), 0, seed + 7) > 0.93:
            c = pick(BLOOD, 0.6)
        return c
    return f


def glove_mat(ctx):
    x, y, z = dpos(ctx)
    lx, ly, lz = local(ctx)
    v = 0.66 + light(ctx, 1.0)
    v = rim(ctx, v, 0.1)
    if hash3(fl(x / 2), fl(y / 2), fl(z / 2), 85) > 0.78:
        v -= 0.14  # grime
    c = pick(GLOVE, v)
    o, sz = ctx.cube.origin, ctx.cube.size
    if sz[0] == 6 and ctx.face == 'back' and lx in () or False:
        pass
    if sz[0] == 6 and sz[1] == 6 and ctx.face == 'back':  # cartoon glove stitching on the back of the hand
        if fl(lx - o[0]) in (1, 3, 5) and ly - o[1] > 1.5:
            c = pick(GLOVE, v - 0.24)
    if sz[0] == 2 and sz[1] >= 6:  # fingers: torn tips show grey skin, dark ragged edge
        tip = ly - o[1]
        if tip > sz[1] - 2.0:
            c = pick(SKIN, 0.45 + light(ctx))
        elif tip > sz[1] - 3.2:
            c = pick(GLOVE, 0.2) if hash3(fl(x), fl(z), fl(y), 86) > 0.3 else pick(BLOOD, 0.4)
        elif hash3(fl(x), 0, 0, 87) > 0.6 and tip > sz[1] * 0.4:
            c = pick(BLOOD, 0.7)
    return c


def claw_mat(ctx):
    v = 0.3 + light(ctx, 1.4)
    if ctx.face in ('front', 'west'):
        v += 0.25
    lx, ly, lz = local(ctx)
    if ly - ctx.cube.origin[1] > ctx.cube.size[1] - 1.2:
        v += 0.15  # glinting tip
    return pick(CLAW, v)


def shoe_mat(ctx):
    x, y, z = dpos(ctx)
    lx, ly, lz = local(ctx)
    o, sz = ctx.cube.origin, ctx.cube.size
    if ctx.face == 'bottom' or (ctx.face != 'top' and ly > o[1] + sz[1] - 1.6 and sz[1] >= 6):
        return pick(SOLE, 0.5 + light(ctx, 1.0) + (0.15 if ctx.face != 'bottom' and ly < o[1] + sz[1] - 1 else 0))
    v = 0.56 + light(ctx, 1.4)
    v = rim(ctx, v, 0.12)
    if ctx.face == 'top' and lz < -9 and -3.5 < lx < 0.5:
        v += 0.22  # glossy toe highlight
    if ctx.face == 'front' and -3 < lx < 0 and ly < o[1] + 3:
        v += 0.14
    n = fbm(x * 0.25, y * 0.25, z * 0.25, 2, 87)
    if n > 0.66:
        v -= 0.2  # scuffs
    if hash3(fl(x), fl(y), fl(z), 88) > 0.95:
        v -= 0.25
    c = pick(SHOE, v)
    if ctx.bone.name == 'left_shoe' and ctx.face in ('front', 'top') and lz < -10 and abs(lx + 0.5) < 3.2 and hash3(fl(lx), fl(ly), 0, 89) > 0.35:
        c = pick(SHOE, 0.12)  # split leather around the poking claws
    return c


def hat_mat(ctx):
    v = 0.5 + light(ctx, 1.3)
    v = rim(ctx, v, 0.15)
    x, y, z = dpos(ctx)
    if hash3(fl(x), fl(y), fl(z), 91) > 0.86:
        v += 0.16  # dust
    lx, ly, lz = local(ctx)
    if ctx.face in ('east', 'front') and -6 < ly < -3 and lz > 0 and hash3(fl(lz), fl(ly), 0, 92) > 0.4:
        v -= 0.25  # dent / tear
    return pick(FELT, v)


def band_mat(ctx):
    lx, ly, lz = local(ctx)
    return pick(RED, 0.4 + light(ctx, 1.0) + (0.12 if fl(lx + lz) % 3 == 0 else 0))


def neck_mat(ctx):
    x, y, z = dpos(ctx)
    lx, ly, lz = local(ctx)
    v = 0.45 + light(ctx, 1.0)
    if fl(lx) % 3 == 0 and ctx.face in ('front', 'back'):
        v -= 0.12  # stretched cords
    if ctx.face == 'front' and ly < -5:
        return pick(PAINT, 0.62 + light(ctx)) if hash3(fl(lx), fl(ly), 0, 95) > 0.3 else pick(BLOOD, 0.6)
    return pick(SKIN, v)


BALLOON_C = (0.0, -9.0, 0.0)   # balloon-local centre of the sphere the cubes approximate


def balloon_mat(ctx):
    """Shade the stepped cubes as one sphere: key light from the upper left front, hot specular, dark rim."""
    lx, ly, lz = local(ctx)
    n = np.array([lx - BALLOON_C[0], ly - BALLOON_C[1], lz - BALLOON_C[2]], float)
    n /= max(1e-6, np.linalg.norm(n))
    L = np.array([-0.5, -0.65, -0.58])
    L /= np.linalg.norm(L)
    d = float(np.dot(n, L))
    v = 0.42 + 0.36 * d
    if d > 0.93:
        v = 0.98
    elif d > 0.85:
        v += 0.18
    v = rim(ctx, v, 0.08)
    if ly > -3.2:
        v -= 0.1
    return pick(BALLOON, v)


def knot_mat(ctx):
    return pick(BALLOON, 0.3 + light(ctx, 1.0))


def string_mat(ctx):
    x, y, z = dpos(ctx)
    lx, ly, lz = local(ctx)
    return pick(STRING, 0.5 + (0.22 if fl(ly) % 3 == 0 else 0))


def skin_mat(ctx):
    return pick(SKIN, rim(ctx, 0.48 + light(ctx, 1.0)))


def pompom_mat(kind):
    ramp = {'red': RED, 'yellow': POM_Y, 'white': RUFF_W}[kind]

    def f(ctx):
        x, y, z = dpos(ctx)
        lx, ly, lz = local(ctx)
        o, sz = ctx.cube.origin, ctx.cube.size
        v = 0.56 + light(ctx, 1.3) + (hash3(fl(x), fl(y), fl(z), 93) - 0.5) * 0.28
        if ctx.face == 'front':
            cx, cy = o[0] + sz[0] * 0.38, o[1] + sz[1] * 0.38
            d = math.hypot(lx - cx, ly - cy)
            v += 0.2 - d * 0.07
        if edge(ctx) == 0:
            v -= 0.12
        return pick(ramp, v)
    return f


def coat_mat(ctx):
    """Tattered tailcoat plane hanging behind the legs."""
    lx, ly, lz = local(ctx)
    c = ctx.cube
    w, h, _ = c.size
    i = fl(lx - c.origin[0])
    depth = ly - c.origin[1]
    L = h - 1 - 3.5 * hash3(i, 0, 0, 101) - (2 if i % 3 == 0 else 0)
    if depth > L:
        return None
    k = fl(lx + 0.6 * math.sin(ly * 0.3) + 0.5)
    v = 0.48 + (0.08 if i % 4 == 1 else 0) - depth * 0.006
    if depth > L - 1.2:
        v -= 0.16
    return pick(MUSTARD, v - 0.04) if k % 6 in (0, 1) else pick(PURPLE, v)


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

    HIP, HZ = -15.0, 6.0
    BODY_LEAN, CHEST_TIP, NECK_TIP = 8, 24, 4

    # ---------------- legs: long thin stilts, knobbly knees, baggy frayed hems, enormous shoes
    LEG = {'right': ((-12, 0, 2), (22, 0, -2), (-10, 14, 0)), 'left': ((-9, 0, -3), (16, 0, 3), (-7, -12, 0))}
    for side, sx in (('right', -1), ('left', 1)):
        r_thigh, r_shin, r_shoe = LEG[side]
        leg = bone(f'{side}_leg', (5.2 * sx, HIP, HZ), rot=r_thigh, mat=suit_mat)
        box(leg.name, (-3, -2, -3), (6, 19, 6))
        shin = bone(f'{side}_shin', at(leg.name, 0, 16, 0), leg.name, rot=r_shin, mat=suit_mat)
        box(shin.name, (-3.5, -2.5, -4), (7, 4, 7))           # knobbly knee
        box(shin.name, (-2.5, 1, -2.5), (5, 15, 5))
        box(shin.name, (-3, 12.5, -3), (6, 4, 6))             # frayed hem
        shoe = bone(f'{side}_shoe', at(shin.name, 0, 17, 0), shin.name, rot=r_shoe, mat=shoe_mat)
        box(shoe.name, (-4.5, -1, -3), (9, 7, 8))             # heel
        box(shoe.name, (-6, 0, -15), (12, 6, 12))             # bulbous toe box
        box(shoe.name, (-5, -1.5, -14), (10, 2, 10))          # rounded toe cap
        if side == 'left':  # split toe, black claws poking out
            for k, cx in enumerate((-3, -0.5, 2)):
                box(shoe.name, (cx, 1.5 + (k % 2), -18), (1, 2, 4), mat=claw_mat)

    # ---------------- torso: narrow waist, spine tipping forward into a hump of shoulder blades
    bone('body', (0, HIP, HZ), rot=(BODY_LEAN, 0, 0), mat=suit_mat)
    box('body', (-8.5, -4, -4.5), (17, 7, 9))                 # hips / baggy seat
    box('body', (-6.5, -11, -4), (13, 8, 8))                  # narrow waist
    box('body', (-3, -10, -7), (6, 6, 4), mat=pompom_mat('red'))
    box('body', (-3, -3, -8), (6, 6, 4), mat=pompom_mat('yellow'))
    bone('coattails', at('body', 0, -9, 4), 'body', rot=(14, 0, 0), mat=coat_mat)
    box('coattails', (-7.5, 0, 0), (7, 24, 0))
    box('coattails', (0.5, 0, 0), (7, 22, 0))

    bone('chest', at('body', 0, -10, 0), 'body', rot=(CHEST_TIP, 0, 0), mat=suit_mat)
    box('chest', (-8.5, -11, -3.5), (17, 11, 8))              # sunken ribcage
    for sx in (-1, 1):
        mbox('chest', sx, (-14, -13, -3.5), (6, 6, 7))        # bony raised shoulders
        mbox('chest', sx, (-8.5, -12, 4), (7, 9, 6))          # shoulder-blade humps
    box('chest', (-6, -14, 3), (12, 9, 10))                   # the hunch
    for k in range(3):
        box('chest', (-1, -13.5 + 3.5 * k, 12.5), (2, 2, 2), mat=skin_mat)   # vertebrae through the torn suit

    # ---------------- ruff: two tiers of big pleated panels, a wide flared disc around the neck
    bone('ruff', at('chest', 0, -10, -1.5), 'chest', rot=(-(BODY_LEAN + CHEST_TIP) + 8, 0, 0))
    for i in range(8):
        th = 22.5 + 45 * i
        front = abs(((th + 180) % 360) - 180) < 60
        back = abs(((th + 180) % 360) - 180) > 120
        kind = 'white' if i % 2 == 0 else 'red'
        pn = f'ruff_lo{i}'
        roll = RUFF_ROLL if i % 2 else -RUFF_ROLL
        bone(pn, r.abs_pivot['ruff'], 'ruff', rot=petal(th, 64 if front else (44 if back else RUFF_DROOP), roll * (0.4 if front else (0.6 if back else 1))),
             mat=ruff_mat(kind, 400 + i, splatter=front))
        box(pn, (-8, 2.5, 0), (16, 12 if front else (17 if back else 20), 0))
    for i in range(5):
        th = 60 * i + 60
        pn = f'ruff_hi{i}'
        bone(pn, at('ruff', 0, -1.5, 0), 'ruff', rot=petal(th, -4, -24 if i % 2 else 24), mat=ruff_mat('cream', 420 + i))
        box(pn, (-6, 2, 0), (12, 13, 0))

    # ---------------- neck + head (an onion: swollen stepped dome, pinched temples, long pointed jaw)
    bone('neck', at('chest', 0, -10.5, -0.5), 'chest', rot=(NECK_TIP, 0, 0), mat=neck_mat)
    box('neck', (-3.5, -7, -3.5), (7, 8, 7))
    head = bone('head', at('neck', 0, -5, -0.5), 'neck', rot=(-(BODY_LEAN + CHEST_TIP + NECK_TIP) + 6, 0, -8), mat=head_mat)
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

    box('head', (-8, -25, -6), (16, 3, 13))                   # dome cap
    box('head', (-12, -22, -9), (24, 4, 18))                  # upper dome
    box('head', (-14, -18, FZ), (28, 5, 20))                  # swollen brow (widest)
    box('head', (-6, -23, FZ - 3), (12, 7, 5))                # forehead bulge
    box('head', (-12, -13, FZ), (24, 9, 18), decals={'eyes:front': eyes_decal(-12, -13)})   # pinched temples / eyes
    for sx in (-1, 1):
        mbox('head', sx, (-13, -6, FZ - 1), (6, 4, 9))        # cheekbone ledges
    box('head', (-9, -4, FZ - 1), (18, 5, 15))                # maxilla (underside = palate)
    box('head', (-3.5, -10, FZ - 5), (7, 7, 5), mat=nose_mat)       # bulbous nose
    box('head', (-2.5, -11, FZ - 4), (5, 8, 4), mat=nose_mat)
    box('head', (-4.5, -8.5, FZ - 4), (9, 4, 4), mat=nose_mat)
    box('head', (-8.5, 1, FZ - 0.4), (17, 10, 0), mat=teeth_mat(UPPER_TEETH, 1.0, 1))
    box('head', (-7, -1, FZ + 5), (14, 6, 0), mat=throat_mat)     # black gullet right behind the needles

    # the real mouth: a long pointed jaw, resting agape so the black gap always shows
    bone('jaw', at('head', 0, 0.5, -1), 'head', rot=(32, 0, 0), mat=jaw_mat)
    box('jaw', (-8, 1, FZ - 0.5), (16, 4, 14), ref='head')
    box('jaw', (-6, 5, FZ + 0.5), (12, 5, 9), ref='head')     # narrowing chin
    box('jaw', (-3, 10, FZ + 1), (6, 4, 5), ref='head')       # long pointed chin tip
    # lower needles on their own hinge so they stand upright at rest and still face the camera when it gapes
    bone('lower_teeth', at('head', 0, 1, FZ + 0.5), 'jaw', rot=(-30, 0, 0), mat=teeth_mat(LOWER_TEETH, 1.0, -1))
    box('lower_teeth', (-7.5, -8, FZ + 0.5), (15, 9, 0), ref='head')

    # tiny dented top hat, jammed askew on the dome
    bone('hat', at('head', 6.5, -23.5, 1), 'head', rot=(-6, 12, 32), mat=hat_mat)
    box('hat', (-6, -1, -5.5), (12, 1, 11))
    box('hat', (-4, -9, -3.5), (8, 8, 7))
    box('hat', (-4, -3.5, -3.5), (8, 2, 7), mat=band_mat, inflate=0.3)

    # frizzy red hair: flaming horns from the temples, a ragged horseshoe at the back (bald on top)
    TUFTS = [  # direction (left side), length, root offset (head-local, left side), phase
        ((0.75, -0.62, -0.2), 21, (0, -2, -2), 0),
        ((0.95, -0.25, 0.1), 23, (0, 2, 0), 5),
        ((0.8, 0.1, 0.55), 18, (-1, 4, 4), 9),
    ]
    for side, sx in (('right', -1), ('left', 1)):
        hn = f'hair_{side}'
        bone(hn, at('head', 12.5 * sx, -17, 2), 'head', mat=tuft_mat(1, 10))
        mbox(hn, sx, (-3, -5, -5), (5, 9, 10))
        for t, (d, L, ro, ph) in enumerate(TUFTS):
            tn = f'hair_{side}_{"abc"[t]}'
            dd = (d[0] * sx, d[1], d[2])
            bone(tn, at(hn, ro[0] * sx, ro[1], ro[2]), hn, rot=aim(dd, (0, 0.25, -1)), mat=tuft_mat(ph, L))
            box(tn, (-3.5, -6, -3.5), (7, 7, 7))
            box(tn, (-2.5 + 0.5 * sx, -13, -2.5), (5, 8, 5))
            box(tn, (-1.5 + 1.0 * sx, -L + 4, -1.5), (3, L - 12, 3))
            box(tn, (-7, -L - 1, 0), (14, L + 1, 0), mat=tuft_plane_mat(ph))
    bone('hair_back', at('head', 0, -12, 9), 'head', mat=tuft_mat(2, 10))
    box('hair_back', (-13, 0, 0.5), (26, 13, 0), mat=frizz_back_mat)
    for t, (d, L, ox) in enumerate((((0.0, 0.8, 0.6), 13, 0), ((-0.75, 0.55, 0.45), 15, -7), ((0.75, 0.55, 0.45), 15, 7))):
        tn = f'hair_back_{"abc"[t]}'
        bone(tn, at('hair_back', ox, 0, -1), 'hair_back', rot=aim(d, (1, 0, 0) if t == 0 else (0, 1, 0)), mat=tuft_mat(t * 3, L))
        box(tn, (-3, -6, -3), (6, 6, 6))
        box(tn, (-2, -11, -2), (4, 6, 4))
        box(tn, (-6, -L - 1, 0), (12, L + 1, 0), mat=tuft_plane_mat(t * 4 + 2))

    # ---------------- arms: long and thin, puffed shoulders, frilled cuffs, torn gloves with claws
    ARM = {'right': ((-(BODY_LEAN + CHEST_TIP) - 4, 0, 10), (-38, 0, 0), (10, 0, -6)),
           'left': ((-(BODY_LEAN + CHEST_TIP) - 8, 0, -6), (-14, 0, 0), (6, 0, 4))}
    for side, sx in (('right', -1), ('left', 1)):
        ra, rf, rh = ARM[side]
        arm = bone(f'{side}_arm', at('chest', 11.5 * sx, -9.5, 0.5), 'chest', rot=ra, mat=suit_mat)
        box(arm.name, (-3.5, -3, -3.5), (7, 7, 7))
        box(arm.name, (-2.5, 3, -2.5), (5, 14, 5))
        fa = bone(f'{side}_forearm', at(arm.name, 0, 16.5, 0), arm.name, rot=rf, mat=suit_mat)
        box(fa.name, (-2, -1, -2), (4, 15, 4))
        box(fa.name, (-3.5, 11.5, -3.5), (7, 3, 7), mat=ruff_mat('white', 451 + sx))
        hand = bone(f'{side}_hand', at(fa.name, 0, 14.5, 0), fa.name, rot=rh, mat=glove_mat)
        box(hand.name, (-3, -0.5, -2), (6, 6, 4))
        for i, (fx, ln) in enumerate(((-3, 9), (-1, 10), (1, 8))):
            box(hand.name, (fx, 5, -1.5), (2, ln, 2))
            box(hand.name, (fx, 5 + ln - 0.5, -1.5), (2, 3, 1), mat=claw_mat)          # hooked claw base
            box(hand.name, (fx + 0.5, 7 + ln, -2.2), (1, 3, 1), mat=claw_mat)          # bent tip
        mbox(hand.name, -sx, (-5, 1, -1.5), (2, 6, 2))                                  # thumb
        mbox(hand.name, -sx, (-5, 6.5, -2), (2, 3, 1), mat=claw_mat)

    # balloon on a long string, floating above and beside the head
    SL = 58
    bs = bone('balloon_string', at('right_hand', -1, 4, 0), 'right_hand', mat=string_mat)
    bs.rot = rot_in(r.bones['right_hand'], aim_matrix(STRING_DIR, (0, 0, -1)))
    box('balloon_string', (0, -SL, -0.5), (0, SL, 1))
    box('balloon_string', (-0.5, -SL, 0), (1, SL, 0))
    bl = bone('balloon', at('balloon_string', 0, -SL, 0), 'balloon_string', mat=balloon_mat)
    bl.rot = rot_in(bs, _rz(math.radians(-12)) @ _rx(math.radians(-6)))
    box('balloon', (-1.5, -2, -1.5), (3, 2, 3), mat=knot_mat)
    box('balloon', (-5, -17, -5), (10, 15, 10))
    box('balloon', (-7, -14, -7), (14, 9, 14))

    m = Model('payaso', 256, 256, r.roots)
    m.scale = 0.5
    _ground(m)
    return m


def _ground(m):
    """Shift the roots so the lowest point of the shoes touches y = 24."""
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
        'jaw': (0.75, 0, 0, 0, 0, 0),
        'head': (-0.32, 0, 0.55, 0, 0, 0),
        'neck': (0.05, 0, 0, 0, 0, 0),
        'chest': (0.12, 0, 0, 0, 0, 0),
        'right_arm': (-1.1, 0, 0.75, 0, 0, 0),
        'left_arm': (-1.0, 0, -0.75, 0, 0, 0),
        'right_forearm': (0.2, 0, 0, 0, 0, 0),
        'left_forearm': (-0.9, 0, 0, 0, 0, 0),
        'balloon_string': (1.0, 0, -0.5, 0, 0, 0),
    },
    'laugh': {
        'jaw': (0.75, 0, 0, 0, 0, 0),
        'head': (-0.65, 0, -0.15, 0, 0, 0),
        'neck': (-0.3, 0, 0, 0, 0, 0),
        'chest': (-0.25, 0, 0, 0, 0, 0),
        'right_arm': (0.15, 0, 0.3, 0, 0, 0),
        'left_arm': (0.3, 0, -0.55, 0, 0, 0),
        'left_forearm': (-0.7, 0, 0, 0, 0, 0),
        'balloon_string': (-0.3, 0, 0, 0, 0, 0),
    },
    'scream': {
        'jaw': (0.95, 0, 0, 0, 0, 0),
        'head': (-0.25, 0, 0, 0, 0, 0),
        'neck': (-0.1, 0, 0, 0, 0, 0),
        'right_arm': (-0.4, 0, 0.9, 0, 0, 0),
        'left_arm': (-0.4, 0, -1.0, 0, 0, 0),
        'hair_right': (0, 0, 0.25, 0, 0, 0),
        'hair_left': (0, 0, -0.25, 0, 0, 0),
        'balloon_string': (0.4, 0, -0.7, 0, 0, 0),
    },
    'offer': {
        'jaw': (-0.35, 0, 0, 0, 0, 0),
        'head': (0.05, 0, 0.45, 0, 0, 0),
        'right_arm': (-0.9, 0, -0.1, 0, 0, 0),
        'right_forearm': (0.75, 0, 0, 0, 0, 0),
        'balloon_string': (0.0, 0, 0.2, 0, 0, 0),
    },
}
ANIM_NOTES = """
body: hips + narrow waist, pivot at the hips; walk bob +-2 deg, lean +0.15 rad more when chasing.
chest: upper spine tipped forward (the hunch, shoulder-blade humps); breathing +-0.03 rad, lunges +0.12 in attack.
coattails: tattered tailcoat behind the legs; lagged X swing opposite to the walk (0.2 rad).
ruff: rigid collar on the chest; ruff_lo0..7 / ruff_hi0..4: pleated panels, optional tiny X flutter (+-0.05) when running.
neck/head: share look-at (neckShare 0.35); idle: slow head roll on Z (+-0.15 rad, 6 s period) with sudden
  'tilt snaps' every few seconds (head Z +-0.5 in 2 ticks, hold, ease back).
jaw: rests agape (29 deg); idle chatter 0..0.1 rad; attack/scream/laugh open +0.75..1.0 rad; offer closes it (-0.35).
lower_teeth: needle row hinged on the jaw lip; static (or a tiny shiver when screaming).
hat: rides the head, lagged wobble on Z with the head roll.
hair_left/hair_right (+ hair_*_a/b/c tufts): spring-lagged Z wobble when the head moves; tufts flare out in scream.
hair_back (+ hair_back_a/b/c): lagged X sway with the head.
right_arm/left_arm (+ _forearm, _hand): long dangling swing on walk (armAmp 0.45), left arm swings loose and late;
  chase: arms reach forward/out (-1.0 rad X, +-0.7 Z). The right forearm stays bent holding the string.
balloon_string: counter-rotates the net right-arm swing so the balloon stays above; balloon bobs (+-0.12 rad Z, 3 s).
right_leg/left_leg (+ _shin, _shoe): stilt walk (legAmp 0.6) with shin flex 0..0.6 rad; the big shoes slap flat.
Poses: attack (lunge, jaw open huge, arms flung wide framing the face, head tilted 30 deg), laugh (head thrown
back, jaw open), scream (jaw max, arms spread, hair flared), offer (holds the balloon out, mouth shut, head tilted).
"""
