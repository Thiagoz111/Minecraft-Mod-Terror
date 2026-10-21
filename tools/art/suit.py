"""DEAD LINE exorcist suit: armour textures (HD, 128x64), 3D hat item model, item icons and previews.

    python3 tools/art/suit.py            -> writes assets + scratchpad/suit/preview.png

Pieces
  * hat      - a real 3D model (wide-brimmed black 'saturno' with a violet band). It is an item with an `equippable`
               HEAD component but no equipment asset, so vanilla renders its item model on the head (like a pumpkin).
  * cassock  - chestplate: black cassock torso + sleeves, roman collar, violet stole, leather belt with holy water vials,
               rosary wrapped around the wrists. Equipment layer `humanoid`.
  * skirt    - leggings: cassock skirt panels with button placket, stole ends with gold crosses and fringe, hem.
               Equipment layer `humanoid_leggings`.
  * boots    - lace-up leather ankle boots (bottom rows of the `humanoid` legs region).

Armour UVs use the vanilla 64x32 box layout; textures are painted at 2x (128x64) so every armour pixel is half size.
Mirrored limbs (left arm/leg) reuse the right limb's texture flipped, so limb designs are symmetric on purpose.
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'tools', 'blocks'))
sys.path.insert(0, os.path.join(ROOT, 'tools', 'models'))
import bkit  # noqa: E402
from bkit import Part  # noqa: E402

ASSETS = os.path.join(ROOT, 'src/main/resources/assets/deadline')
SP = '/tmp/claude-0/-home-user-Minecraft-Mod-Terror/f464a6ad-b203-50f8-a993-93d7fecfc5d1/scratchpad'
OUT = os.path.join(SP, 'suit')
K = 2  # texture pixels per armour unit


def hx(h, a=255):
    h = h.lstrip('#')
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def pick(r, v):
    v = max(0.0, min(0.999, v))
    return r[int(v * len(r))]


BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]

CASS = [hx(c) for c in ('#08070c', '#0e0d14', '#14131c', '#1a1924', '#21202c', '#292735', '#322f40', '#3e3a4e', '#4d4860')]
VIOLET = [hx(c) for c in ('#1c0927', '#290e3b', '#37144f', '#461a64', '#56217a', '#682a8f', '#7c36a5', '#934abb')]
GOLD = [hx(c) for c in ('#3a2208', '#5e3c0e', '#8a5f17', '#b78524', '#d9a93c', '#f0cd67', '#fbe9a6')]
LEATH = [hx(c) for c in ('#160c07', '#24140c', '#331d12', '#45281a', '#593522', '#70452d', '#8a5a3b', '#a5714c')]
BOOT = [hx(c) for c in ('#070605', '#0e0c0b', '#161311', '#201b18', '#2b2420', '#382f29', '#4a3f37', '#655a50')]
WHITE = [hx(c) for c in ('#6b6a68', '#8e8b86', '#b0aca4', '#cdc8bd', '#e3dfd4', '#f4f1e8')]
BRASS = [hx(c) for c in ('#2d1d07', '#523610', '#7b5519', '#a67826', '#cc9c3a', '#ead06e', '#fff2b8')]
SILVER = [hx(c) for c in ('#2a2c36', '#474a58', '#6a6e7e', '#9095a5', '#b8bdca', '#e2e6ee')]
BEAD = [hx(c) for c in ('#120906', '#24120b', '#3a1f12', '#55301c', '#7a4a2c')]
GLASS = [hx(c, a) for c, a in (('#14324a', 255), ('#1e5a86', 255), ('#2f86c0', 255), ('#58b6ea', 255), ('#a9e4ff', 255), ('#eafaff', 255))]


# ------------------------------------------------------------------------------------------------ armour painting
class C:
    """Texel context: part, face, i/j/w/h inside the face (texture pixels), X/Y/Z model-space position (Y down)."""
    __slots__ = ('part', 'face', 'i', 'j', 'w', 'h', 'X', 'Y', 'Z', 's', 't')

    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)

    def edge(self):
        return min(self.i, self.j, self.w - 1 - self.i, self.h - 1 - self.j)


def rects(u, v, w, h, d):
    return {'top': (u + d, v, w, d), 'bottom': (u + d + w, v, w, d), 'west': (u, v + d, d, h),
            'front': (u + d, v + d, w, h), 'east': (u + d + w, v + d, d, h), 'back': (u + 2 * d + w, v + d, w, h)}


def point(face, origin, size, s, t):
    (x0, y0, z0), (W, H, D) = origin, size
    x1, y1, z1 = x0 + W, y0 + H, z0 + D
    return {'front': (x0 + s * W, y0 + t * H, z0), 'back': (x1 - s * W, y0 + t * H, z1),
            'west': (x0, y0 + t * H, z1 - s * D), 'east': (x1, y0 + t * H, z0 + s * D),
            'top': (x0 + s * W, y0, z1 - t * D), 'bottom': (x0 + s * W, y1, z1 - t * D)}[face]


def paint_box(img, part, uv, origin, size, mat):
    W, H, D = size
    for face, (fu, fv, fw, fh) in rects(uv[0], uv[1], W, H, D).items():
        pw, ph = fw * K, fh * K
        for j in range(ph):
            for i in range(pw):
                s, t = (i + 0.5) / pw, (j + 0.5) / ph
                X, Y, Z = point(face, origin, size, s, t)
                c = mat(C(part=part, face=face, i=i, j=j, w=pw, h=ph, X=X, Y=Y, Z=Z, s=s, t=t))
                if c is not None:
                    img[fv * K + j, fu * K + i] = c


def cloth(c, base=0.47, fold=1.0):
    """Black wool cassock: twill weave, soft vertical folds, crisp face borders."""
    v = base
    if (c.i + c.j) % 4 == 0:
        v -= 0.035
    if (c.i + c.j) % 4 == 2:
        v += 0.018
    # folds hang vertically; the coordinate runs around the body so folds continue across faces
    a = c.X * 1.3 + c.Z * 0.9 + (0.0 if c.face in ('front', 'back') else 2.1)
    v += fold * (0.07 * math.sin(a * 1.7 + 0.6 * math.sin(c.Y * 0.35)) + 0.035 * math.sin(a * 4.3 + 1.3))
    v += (BAYER[c.j % 4][c.i % 4] / 16 - 0.5) * 0.04
    if c.edge() == 0 and c.face not in ('top', 'bottom'):
        v -= 0.06
    return v


def cross_px(ci, cj, x, y, size=2):
    """Latin cross centred at (x, y) in face pixels: arms `size`, long foot. Returns 0 none, 1 body, 2 shadow."""
    dx, dy = ci - x, cj - y
    if dx == 0 and -size <= dy <= size + 2:
        return 1
    if dy == 0 and -size <= dx <= size:
        return 1
    if (dx == 1 and -size <= dy <= size + 2 and dy != 0) or (dy == 1 and 1 <= dx <= size) or (dy == 1 and -size <= dx <= -1):
        return 2
    return 0


def stole(c, col, top, bottom, vbase=0.5):
    """Violet stole band: damask lattice, gold piping on both edges. col: band start column (4 px wide)."""
    k = c.i - col
    if c.i < col or c.i > col + 3 or c.j < top or c.j > bottom:
        return None
    if k in (0, 3):
        return pick(GOLD, 0.45 + (0.25 if (c.j % 3 == 0) else 0.0) - (0.15 if k == 3 else 0.0))
    v = vbase
    lat = abs((c.j % 6) - 3) + abs(((k + c.j // 6) % 2) - 0)
    if lat == 3:
        v += 0.12
    if c.j % 6 == 0:
        v -= 0.05
    v += (BAYER[c.j % 4][c.i % 4] / 16 - 0.5) * 0.05
    return pick(VIOLET, v)


def buttons(c, col, start, step, end):
    """Cassock placket: 2px column of small round buttons (2x2) every `step` rows. Returns colour or None."""
    if c.i not in (col, col + 1) or c.j < start or c.j > end:
        return None
    r = (c.j - start) % step
    left = c.i == col
    if r == 0:
        return pick(CASS, 0.97) if left else pick(CASS, 0.62)
    if r == 1:
        return pick(CASS, 0.55) if left else pick(CASS, 0.06)
    return pick(CASS, 0.36 if left else 0.3)


def belt(c, top=19, bottom=22):
    """Leather belt with stitching, brass buckle at the front."""
    if c.j < top or c.j > bottom:
        return None
    v = 0.52
    if c.j in (top, bottom):
        v = 0.32
    if c.j == top + 1 and c.i % 2 == 0:
        v = 0.75  # stitching
    if c.j == bottom - 1 and c.i % 2 == 1:
        v = 0.7
    v += ((c.i * 7 + c.j * 3) % 5 - 2) * 0.02
    col = pick(LEATH, v)
    if c.face == 'front' and c.part == 'body':
        bi = c.i - 6
        if 0 <= bi <= 3:
            if bi in (0, 3) or c.j in (top, bottom):
                return pick(BRASS, 0.75 if (bi == 0 or c.j == top) else 0.45)
            if bi == 1:
                return pick(BRASS, 0.3)  # prong
            return pick(LEATH, 0.25)
    return col


def vial(c, x, top):
    """Glass vial of holy water held by a leather loop: 2 px wide, cork on top."""
    di, dj = c.i - x, c.j - top
    if not (0 <= di <= 1 and 0 <= dj <= 6):
        return None
    if dj == 0:
        return pick(LEATH, 0.85 if di == 0 else 0.6)  # cork
    if dj == 1:
        return pick(GLASS, 0.9 if di == 0 else 0.55)
    if dj in (4, 5):
        return pick(LEATH, 0.55 if di == 0 else 0.35)  # belt loop over the vial
    return pick(GLASS, (0.78 if di == 0 else 0.5) - 0.06 * (dj - 2))


def cassock_body(c):
    # roman collar + shoulders
    if c.face == 'top':
        v = cloth(c, 0.46, 0.4)
        x = int((c.X + 4) * K)
        if 3 <= x <= 6 or 9 <= x <= 12:
            return pick(VIOLET, 0.5 + (0.12 if (x in (3, 12)) else 0))
        return pick(CASS, v)
    if c.face == 'bottom':
        return pick(CASS, 0.2)
    if c.face == 'front':
        if c.j <= 2 and 6 <= c.i <= 9:
            if 7 <= c.i <= 8:
                return pick(WHITE, 0.85 if c.j < 2 else 0.6)  # the white tab
            return pick(CASS, 0.15)  # collar band
        b = belt(c)
        if b is not None:
            return b
        for x, top in ((1, 15), (13, 15)):
            g = vial(c, x, top)
            if g is not None:
                return g
        for col in (3, 9):
            s = stole(c, col, 0, 18)
            if s is not None:
                return s
        p = buttons(c, 7, 4, 3, 18)
        if p is not None:
            return p
        v = cloth(c)
        if c.i in (6, 9) and c.j > 2:
            v -= 0.05  # shadow under the stole edges
        return pick(CASS, v)
    if c.face == 'back':
        b = belt(c)
        if b is not None:
            return b
        # stole goes around the neck in a U, gold cross at the nape
        u_depth = 3 + (3 if 5 <= c.i <= 10 else (1 if c.i in (4, 11) else 0))
        if 3 <= c.i <= 12 and c.j <= u_depth:
            if c.j == u_depth:
                return pick(GOLD, 0.5)
            if (c.i in (7, 8) and 1 <= c.j <= 5) or (c.j == 2 and 5 <= c.i <= 10):
                return pick(GOLD, 0.85 if (c.i == 7 or c.j == 2 and c.i < 8) else 0.5)
            return pick(VIOLET, 0.48 + (0.1 if (c.i + c.j) % 5 == 0 else 0))
        v = cloth(c)
        if c.i in (7, 8):
            v -= 0.06 if c.i == 7 else -0.03  # centre back seam
        return pick(CASS, v)
    # sides
    b = belt(c)
    if b is not None:
        return b
    v = cloth(c, 0.38)
    if c.i == c.w // 2:
        v -= 0.07  # side seam
    if c.face == 'east':  # rosary tucked into the belt on the left hip: a loop of beads below the belt line
        if 18 <= c.j <= 18 and c.i % 2 == 0:
            return pick(BEAD, 0.75)
    return pick(CASS, v)


def cassock_arm(c):
    if c.face == 'top':
        v = cloth(c, 0.44, 0.3)
        if c.j == 0 or c.i == 0:
            v -= 0.08
        return pick(CASS, v)
    if c.face == 'bottom':
        return None  # hand shows through the sleeve
    if c.j >= 19:
        # dangling crucifix of the wrist rosary on the outer side
        if c.face == 'west':
            k = cross_px(c.i, c.j, 3, 20, 1)
            if k:
                return pick(SILVER, 0.85 if k == 1 else 0.4)
        return None
    if c.j in (17, 18):
        return pick(WHITE, 0.8 if c.j == 17 else 0.55)  # shirt cuff
    if c.j == 15:
        # rosary beads wound around the wrist
        if (c.i + (2 if c.face in ('front', 'back') else 0)) % 2 == 0:
            return pick(BEAD, 0.9)
        return pick(CASS, 0.18)
    if c.j == 16:
        if (c.i + (2 if c.face in ('front', 'back') else 0)) % 2 == 1:
            return pick(BEAD, 0.5)
        return pick(CASS, 0.26)
    if c.j == 14:
        return pick(CASS, 0.52)  # cuff edge
    v = cloth(c, 0.42, 0.5)
    # elbow creases
    if 9 <= c.j <= 12 and c.face in ('front', 'east'):
        v += 0.08 if (c.i + c.j) % 4 == 0 else (-0.06 if (c.i + c.j) % 4 == 2 else 0)
    if c.j == 0:
        v -= 0.08  # shoulder seam
    return pick(CASS, v)


def skirt_leg(c):
    if c.face == 'top':
        return pick(CASS, cloth(c, 0.3, 0.2))
    if c.face == 'bottom':
        return None
    if c.j >= 20:
        return None  # below the hem: trousers/boots show
    if c.j == 19:
        return pick(CASS, 0.18)
    if c.j == 18:
        return pick(CASS, 0.58 if c.i % 2 == 0 else 0.46)  # hem stitching
    v = cloth(c, 0.4, 1.4)
    if c.j >= 15:
        v += 0.06 * (1 if (c.i * 3 + c.j) % 7 == 0 else 0) - 0.02  # dust near the hem
    if c.face == 'front':
        if 2 <= c.i <= 6 and c.j <= 10:  # flared stole end with an embroidered cross
            if c.i in (2, 6):
                return pick(GOLD, 0.5 + (0.2 if c.j % 3 == 0 else 0) - (0.12 if c.i == 6 else 0))
            if c.j == 10:
                return pick(GOLD, 0.62)
            if (c.i == 4 and 2 <= c.j <= 8) or (c.j == 4 and 3 <= c.i <= 5):
                return pick(GOLD, 0.88 if (c.i == 4 and c.j != 4) or c.i == 3 else 0.7)
            return pick(VIOLET, 0.5 + (0.1 if (c.i + c.j) % 4 == 0 else 0) - 0.04 * (c.i == 5))
        if 2 <= c.i <= 6 and c.j in (11, 12):  # gold fringe
            if c.i % 2 == 0:
                return pick(GOLD, 0.7 if c.j == 11 else 0.42)
        if c.i == 7:
            p = buttons(c, 7, 1, 3, 17)
            if p is not None:
                return p
            v -= 0.04
    elif c.face == 'west':
        if c.i in (3, 4):
            v -= 0.06 if c.i == 3 else -0.02
    elif c.face == 'east':
        v -= 0.07  # between the legs
    return pick(CASS, v)


def skirt_stole_cross(img):
    """Embroidered crosses at the stole ends (painted after the band so they sit on top)."""
    fu, fv, fw, fh = rects(0, 16, 4, 12, 4)['front']
    for j in range(fh * K):
        for i in range(fw * K):
            k = cross_px(i, j, 4, 4, 1)
            if k and 3 <= i <= 6:
                img[fv * K + j, fu * K + i] = pick(GOLD, 0.82) if k == 1 else pick(GOLD, 0.38)


def waist(c):
    if c.face in ('top', 'bottom'):
        return None
    if c.j < 14:
        return None
    b = belt(c)
    if b is not None:
        return b
    return pick(CASS, cloth(c))


def boot(c):
    if c.face == 'top':
        return None
    if c.face == 'bottom':
        # sole: tread grid, heel block at the back (top of this face = back of the foot)
        if c.edge() == 0:
            return pick(BOOT, 0.18)
        if c.j <= 2:
            return pick(BOOT, 0.32 if (c.i + c.j) % 2 == 0 else 0.2)
        return pick(BOOT, 0.28 if (c.i % 3 == 0 or c.j % 3 == 0) else 0.12)
    if c.j < 18:
        return None
    if c.j == 18:
        return pick(BOOT, 0.62 if c.i % 2 == 0 else 0.5)  # rolled top edge
    if c.j >= 22:
        if c.j == 22:
            return pick(BOOT, 0.45) if c.i % 2 == 0 else pick(BOOT, 0.2)  # welt stitch
        return pick(BOOT, 0.08)  # sole
    v = 0.36 + (BAYER[c.j % 4][c.i % 4] / 16 - 0.5) * 0.06
    if c.face == 'front':
        if 2 <= c.i <= 5 and c.j <= 20:
            if (c.i + c.j) % 3 == 0:
                return pick(BOOT, 0.72)  # laces
            return pick(BOOT, 0.2)
        if c.j == 21 and 2 <= c.i <= 5:
            return pick(BOOT, 0.85 if c.i in (3, 4) else 0.6)  # polished toe cap highlight
    if c.face == 'west' and c.j == 20:
        v += 0.12  # crease
    if c.face == 'east':
        v -= 0.06
    return pick(BOOT, v)


def armour_textures():
    hum = np.zeros((32 * K, 64 * K, 4), np.uint8)
    paint_box(hum, 'body', (16, 16), (-4, 0, -2), (8, 12, 4), cassock_body)
    paint_box(hum, 'arm', (40, 16), (-8, 0, -2), (4, 12, 4), cassock_arm)
    paint_box(hum, 'leg', (0, 16), (-4, 12, -2), (4, 12, 4), boot)
    leg = np.zeros((32 * K, 64 * K, 4), np.uint8)
    paint_box(leg, 'lbody', (16, 16), (-4, 0, -2), (8, 12, 4), waist)
    paint_box(leg, 'skirt', (0, 16), (-4, 12, -2), (4, 12, 4), skirt_leg)
    return Image.fromarray(hum, 'RGBA'), Image.fromarray(leg, 'RGBA')


def sleeve_texture():
    """First-person cassock sleeves, painted on the 64x64 player-skin layout (right arm 40,16; left arm 32,48) so the
    client can draw them over the vanilla first-person arm (FirstPersonSleeve)."""
    sl = np.zeros((64 * K, 64 * K, 4), np.uint8)
    paint_box(sl, 'arm', (40, 16), (-8, 0, -2), (4, 12, 4), cassock_arm)
    paint_box(sl, 'arm', (32, 48), (4, 0, -2), (4, 12, 4), cassock_arm)
    return Image.fromarray(sl, 'RGBA')


# ------------------------------------------------------------------------------------------------ 3D hat (item model)
FELT = [hx(c) for c in ('#060508', '#0b0a0e', '#111015', '#17151c', '#1e1b24', '#26222d', '#302b38', '#3c3646')]


def _rot_y(p, ang, origin=(8, 8, 8)):
    a = math.radians(ang)
    x, y, z = p[0] - origin[0], p[1] - origin[1], p[2] - origin[2]
    c, s = math.cos(a), math.sin(a)
    return (x * c + z * s + origin[0], y + origin[1], -x * s + z * c + origin[2])


def felt_mat(kind):
    def m(ctx):
        p = ctx.pos
        if ctx.part.rot:
            p = _rot_y(p, ctx.part.rot[1])
        r = math.hypot(p[0] - 8, p[2] - 8)
        ang = math.atan2(p[2] - 8, p[0] - 8)
        v = 0.5 + 0.05 * math.sin(ang * 7 + r * 0.9) + (BAYER[ctx.j % 4][ctx.i % 4] / 16 - 0.5) * 0.05
        if kind == 'brim':
            if ctx.face == 'up':
                if r > 11.2:
                    return pick(FELT, 0.62 if (int(ang * 12) % 2) else 0.55)  # grosgrain binding
                if abs(r - 9.6) < 0.3 or abs(r - 10.6) < 0.25:
                    return pick(FELT, 0.35)  # concentric stitching
                v += (r - 7) * 0.02
                return pick(FELT, v)
            if ctx.face == 'down':
                return pick(FELT, 0.26 + (0.08 if r > 11.2 else 0))
            return pick(FELT, 0.6)  # edge binding
        if kind == 'band':
            if ctx.face in ('up', 'down'):
                return pick(FELT, v)
            y = p[1]
            if 14.3 <= y <= 15.5:
                vb = 0.5 + (0.18 if abs(y - 15.0) < 0.25 else 0) - (0.15 if y < 14.6 else 0)
                return pick(VIOLET, vb)  # violet ribbon band
            return pick(FELT, v + (y - 15) * 0.04)
        # crown dome: lighter towards the top, faint pinch line
        if ctx.face == 'up':
            v += 0.08 - r * 0.012
            if r < 1.2:
                v -= 0.08
        else:
            v += (p[1] - 16) * 0.05
        return pick(FELT, v)
    return m


def octagon(y0, y1, a, kind, eps0=0.0):
    """Regular octagon prism (apothem a, centred on 8,8) from 4 overlapping bars; only outer faces are emitted."""
    w = a * math.tan(math.radians(22.5))
    parts = []
    for n, (ang, along) in enumerate(((0, 'x'), (0, 'z'), (45, 'x'), (45, 'z'))):
        e = eps0 + n * 0.03
        if along == 'x':
            frm, to, ends = (8 - a, y0 - e, 8 - w), (8 + a, y1 + e, 8 + w), ('west', 'east')
        else:
            frm, to, ends = (8 - w, y0 - e, 8 - a), (8 + w, y1 + e, 8 + a), ('north', 'south')
        rot = ('y', 45, (8, 8, 8)) if ang else None
        parts.append(Part(frm, to, felt_mat(kind), faces=ends + ('up', 'down'), rot=rot))
    return parts


def hat_parts():
    parts = []
    # the head top is at y=14.4 (1 head pixel = 1.6 units); the crown starts there so the square head never pokes through
    parts += octagon(13.75, 14.35, 12.0, 'brim')
    parts += octagon(14.35, 16.0, 6.9, 'band')
    parts += octagon(16.0, 17.5, 6.5, 'crown')
    parts += octagon(17.5, 18.6, 5.6, 'crown')
    parts += octagon(18.6, 19.4, 4.2, 'crown')
    parts += octagon(19.4, 19.8, 2.4, 'crown')
    return parts


def export_hat():
    parts = hat_parts()
    rects_, slots = [], []
    for p in parts:
        for f in p.faces:
            rects_.append(p.face_px(f))
            slots.append((p, f))
    size, pos = bkit._pack(rects_)
    tex = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    for (p, f), (w, h), (x, y) in zip(slots, rects_, pos):
        p.uv[f] = (x, y, w, h)
    elements = []
    for n, p in enumerate(parts):
        for f in p.faces:
            bkit._paint_face(tex, p.uv[f], p, f, p.mat, None, bkit.shash('hat', n, f))
        el = {'from': [round(v, 4) for v in p.frm], 'to': [round(v, 4) for v in p.to], 'faces': {}}
        if p.rot:
            el['rotation'] = {'angle': p.rot[1], 'axis': p.rot[0], 'origin': list(p.rot[2])}
        k = 16.0 / size
        for f in p.faces:
            u0, v0, w, h = p.uv[f]
            el['faces'][f] = {'uv': [round(u0 * k, 4), round(v0 * k, 4), round((u0 + w) * k, 4), round((v0 + h) * k, 4)],
                              'texture': '#t'}
        elements.append(el)
    model = {
        'textures': {'t': 'deadline:item/exorcist_hat', 'particle': 'deadline:item/exorcist_hat'},
        'elements': elements,
        'display': {
            'head': {'rotation': [0, 0, 0], 'translation': [0, 0, 0], 'scale': [1, 1, 1]},
            'gui': {'rotation': [28, 45, 0], 'translation': [0, -3.9, 0], 'scale': [0.46, 0.46, 0.46]},
            'ground': {'rotation': [0, 0, 0], 'translation': [0, -2, 0], 'scale': [0.3, 0.3, 0.3]},
            'fixed': {'rotation': [-90, 0, 0], 'translation': [0, 0, -4], 'scale': [0.5, 0.5, 0.5]},
            'thirdperson_righthand': {'rotation': [10, -30, 10], 'translation': [0, -1.5, -2], 'scale': [0.34, 0.34, 0.34]},
            'thirdperson_lefthand': {'rotation': [10, 30, -10], 'translation': [0, -1.5, -2], 'scale': [0.34, 0.34, 0.34]},
            'firstperson_righthand': {'rotation': [0, -20, 8], 'translation': [1, -2, 0], 'scale': [0.34, 0.34, 0.34]},
            'firstperson_lefthand': {'rotation': [0, 20, -8], 'translation': [1, -2, 0], 'scale': [0.34, 0.34, 0.34]},
        },
    }
    return model, tex, elements


# ------------------------------------------------------------------------------------------------ icons (32x32)
def icons():
    sys.path.insert(0, HERE)
    from px import Sprite, Material
    cass = Material(['#07070b', '#100f16', '#1a1924', '#26242f', '#34313f', '#46425a'], ambient=0.38)
    vio = Material(['#1c0927', '#331248', '#4c1d6c', '#682a8f', '#8a43b4', '#a865cf'], ambient=0.4)
    gold = Material(['#3a2208', '#6a4510', '#a8761f', '#d9a93c', '#f6dd84', '#fff6d0'], spec=0.5, shininess=8)
    white = Material(['#7d7a73', '#a8a49b', '#cdc8bd', '#e8e4da', '#ffffff'], ambient=0.45)
    leath = Material(['#160c07', '#2c1a0f', '#45281a', '#64402a', '#8a5a3b', '#a5714c'], ambient=0.35)
    boot = Material(['#050404', '#0e0c0b', '#1a1613', '#2a231f', '#3e342d', '#5a4e44'], spec=0.45, shininess=12)
    out = {}

    s = Sprite(32, seed=11)
    s.poly([(10, 3), (22, 3), (27, 7), (30, 22), (26, 23), (24, 12), (24, 30), (8, 30), (8, 12), (6, 23), (2, 22), (5, 7)], cass)
    s.poly([(12, 3), (15, 3), (14, 29), (11, 29)], vio, bevel=1)
    s.poly([(17, 3), (20, 3), (21, 29), (18, 29)], vio, bevel=1)
    s.rect(8, 22, 24, 24, leath, bevel=1)
    s.rect(14, 22, 17, 24, gold, bevel=1)
    img = s.render()
    px = img.load()
    for (x, y) in ((15, 3), (16, 3), (15, 4), (16, 4)):
        px[x, y] = (236, 232, 222, 255)  # roman collar tab
    for y in range(6, 21, 3):
        px[15, y] = (70, 66, 86, 255); px[16, y + 1] = (20, 18, 26, 255)
    for (x, y) in ((12, 26), (19, 26)):
        for dx, dy in ((0, 0), (0, -1), (0, 1), (0, 2), (-1, 0), (1, 0)):
            px[x + dx, y + dy] = (240, 205, 103, 255)
    out['exorcist_cassock'] = img

    s = Sprite(32, seed=12)
    s.poly([(8, 3), (24, 3), (27, 29), (17, 29), (16, 12), (15, 29), (5, 29)], cass)
    s.rect(8, 3, 24, 6, leath, bevel=1)
    s.rect(14, 3, 17, 6, gold, bevel=1)
    s.poly([(9, 7), (12, 7), (11, 19), (8, 19)], vio, bevel=1)
    s.poly([(20, 7), (23, 7), (24, 19), (21, 19)], vio, bevel=1)
    img = s.render()
    px = img.load()
    for x in range(8, 12):
        px[x, 20] = (240, 205, 103, 255) if x % 2 == 0 else (150, 110, 30, 255)
    for x in range(21, 25):
        px[x, 20] = (240, 205, 103, 255) if x % 2 == 0 else (150, 110, 30, 255)
    for y in range(8, 28, 3):
        px[15, y] = (70, 66, 86, 255)
    out['exorcist_skirt'] = img

    s = Sprite(32, seed=13)
    for ox in (0, 13):
        s.poly([(4 + ox, 9), (11 + ox, 9), (12 + ox, 20), (17 + ox, 22), (18 + ox, 26), (3 + ox, 26)], boot, dome=True)
        s.rect(3 + ox, 25, 18 + ox, 27, Material(['#030303', '#0a0909', '#141211', '#1e1b19'], ambient=0.3), bevel=1)
    img = s.render()
    px = img.load()
    for ox in (0, 13):
        for y in range(11, 20, 2):
            px[7 + ox, y] = (120, 104, 88, 255); px[8 + ox, y + 1] = (120, 104, 88, 255)
        px[15 + ox, 23] = (120, 110, 100, 255)
    out['exorcist_boots'] = img
    return out


# ------------------------------------------------------------------------------------------------ preview
def base_skin():
    """Neutral player skin (64x32 legacy layout, 2x) used only under the armour in previews."""
    img = np.zeros((32 * K, 64 * K, 4), np.uint8)
    SKIN = [hx(c) for c in ('#5a3b2c', '#7d553f', '#a07153', '#b98666', '#cf9d7d')]
    HAIR = [hx(c) for c in ('#120c08', '#21160f', '#2f2016')]
    PANTS = [hx(c) for c in ('#141820', '#1d2330', '#283041')]

    def head(c):
        if c.face == 'top' or (c.face in ('back', 'west', 'east') and c.j < 9) or (c.face == 'front' and c.j < 4):
            return pick(HAIR, 0.5 + 0.2 * ((c.i * 3 + c.j) % 3 == 0))
        if c.face == 'front':
            if c.j in (8, 9) and c.i in (3, 4, 11, 12):
                return (240, 240, 240, 255) if c.i in (3, 12) else (40, 30, 26, 255)
            if c.j == 7 and 2 <= c.i <= 5 or c.j == 7 and 10 <= c.i <= 13:
                return pick(HAIR, 0.3)
            if c.j == 12 and 6 <= c.i <= 9:
                return pick(SKIN, 0.1)
        return pick(SKIN, 0.6)

    paint_box(img, 'head', (0, 0), (-4, -8, -4), (8, 8, 8), head)
    paint_box(img, 'body', (16, 16), (-4, 0, -2), (8, 12, 4), lambda c: pick(PANTS, 0.5))
    paint_box(img, 'arm', (40, 16), (-8, 0, -2), (4, 12, 4), lambda c: pick(SKIN, 0.6))
    paint_box(img, 'leg', (0, 16), (-4, 12, -2), (4, 12, 4), lambda c: pick(PANTS, 0.5))
    return Image.fromarray(img, 'RGBA')


def mannequin():
    from mcmodel import Bone, Cube, Model

    def cube(o, s, uv, row, inflate=0.0, mirror=False):
        return Cube(o, s, uv=(uv[0], uv[1] + row), inflate=inflate, mirror=mirror)
    rows = {'skin': 0, 'hum': 32, 'leg': 64}
    head = Bone('head', (0, 0, 0), cubes=[cube((-4, -8, -4), (8, 8, 8), (0, 0), 0)])
    body = Bone('body', (0, 0, 0), cubes=[cube((-4, 0, -2), (8, 12, 4), (16, 16), 0),
                                         cube((-4, 0, -2), (8, 12, 4), (16, 16), 64, 0.5),
                                         cube((-4, 0, -2), (8, 12, 4), (16, 16), 32, 1.0)])
    arms = []
    for name, px_, mir in (('right_arm', -5, False), ('left_arm', 5, True)):
        o = (-3, -2, -2) if not mir else (-1, -2, -2)
        arms.append(Bone(name, (px_, 2, 0), cubes=[cube(o, (4, 12, 4), (40, 16), 0, 0, mir), cube(o, (4, 12, 4), (40, 16), 32, 1.0, mir)]))
    legs = []
    for name, px_, mir in (('right_leg', -1.9, False), ('left_leg', 1.9, True)):
        legs.append(Bone(name, (px_, 12, 0), cubes=[cube((-2, 0, -2), (4, 12, 4), (0, 16), 0, 0, mir),
                                                    cube((-2, 0, -2), (4, 12, 4), (0, 16), 64, 0.5, mir),
                                                    cube((-2, 0, -2), (4, 12, 4), (0, 16), 32, 1.0, mir)]))
    return Model('exorcist', 64, 96, [head, body] + arms + legs)


PAGE = r'''<!doctype html><html><body style="margin:0;background:#000">
<canvas id=c></canvas>
<script src="file://%(three)s"></script>
<script src="file://%(mcv)s"></script>
<script src="file://%(bv)s"></script>
<script>
const SPEC = %(spec)s;
const renderer = new THREE.WebGLRenderer({canvas: document.getElementById('c'), antialias: false, preserveDrawingBuffer: true});
renderer.setSize(SPEC.w, SPEC.h); renderer.setScissorTest(true);
function load(uri) { return new Promise(r => { const i = new Image(); i.onload = () => { const t = new THREE.Texture(i); t.needsUpdate = true;
  t.magFilter = THREE.NearestFilter; t.minFilter = THREE.NearestFilter; t.generateMipmaps = false; if (THREE.SRGBColorSpace) t.colorSpace = THREE.SRGBColorSpace; r(t); }; i.src = uri; }); }
Promise.all([load(SPEC.body), load(SPEC.hat)]).then(([bt, ht]) => {
  for (const v of SPEC.views) {
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(v.dark ? 0x050408 : 0x2b2733);
    if (v.dark) {
      scene.add(new THREE.AmbientLight(0x6a6a8a, 0.35));
      const spot = new THREE.SpotLight(0xfff0d8, 9, 200, Math.PI / 7, 0.45, 0.6); spot.position.set(-30, 30, 60); spot.target.position.set(0, 16, 0);
      scene.add(spot); scene.add(spot.target);
      const rim = new THREE.DirectionalLight(0x8a2030, 0.9); rim.position.set(-1, 0.6, -1); scene.add(rim);
    } else {
      scene.add(new THREE.AmbientLight(0xffffff, 1.15));
      const key = new THREE.DirectionalLight(0xffffff, 1.4); key.position.set(-0.6, 1, 1.2); scene.add(key);
      const fill = new THREE.DirectionalLight(0xffffff, 0.45); fill.position.set(0.8, 0.3, -1); scene.add(fill);
    }
    const built = MCViewer.buildModel(THREE, SPEC.data, bt);
    if (v.pose) for (const [k, p] of Object.entries(v.pose)) built.pose(k, ...p);
    const hat = BlockView.buildElements(THREE, SPEC.hatEls, ht, {});
    hat.scale.set(10, 10, -10); hat.position.set(-5, -1, 5);
    built.groups['head'].add(hat);
    scene.add(built.object);
    const cam = new THREE.PerspectiveCamera(v.fov || 30, v.w / v.h, 0.5, 500);
    const a = v.angle * Math.PI / 180, el = (v.elev || 6) * Math.PI / 180, d = v.dist || 78, cy = v.cy || 17;
    cam.position.set(Math.sin(a) * Math.cos(el) * d, cy + Math.sin(el) * d, Math.cos(a) * Math.cos(el) * d);
    cam.lookAt(0, cy, 0);
    renderer.setViewport(v.x, SPEC.h - v.y - v.h, v.w, v.h); renderer.setScissor(v.x, SPEC.h - v.y - v.h, v.w, v.h);
    renderer.render(scene, cam);
  }
  window.__done = true;
});
</script></body></html>'''


def preview(hum, leg, hat_tex, hat_els):
    import base64
    import io
    import subprocess
    import tempfile
    sys.path.insert(0, os.path.join(ROOT, 'tools', 'models'))
    import render
    atlas = Image.new('RGBA', (64 * K, 96 * K), (0, 0, 0, 0))
    atlas.paste(base_skin(), (0, 0))
    atlas.paste(hum, (0, 32 * K))
    atlas.paste(leg, (0, 64 * K))

    def uri(im):
        b = io.BytesIO()
        im.save(b, 'PNG')
        return 'data:image/png;base64,' + base64.b64encode(b.getvalue()).decode()
    m = mannequin()
    walk = {'right_arm': [-0.5, 0, 0.1], 'left_arm': [0.45, 0, -0.1], 'right_leg': [0.4, 0, 0], 'left_leg': [-0.4, 0, 0]}
    hold = {'right_arm': [-1.45, -0.25, 0], 'left_arm': [-0.2, 0, -0.1], 'head': [0.1, 0, 0]}
    views = []
    cw, ch = 300, 520
    for n, a in enumerate((0, 35, 90, 160, 200)):
        views.append({'angle': a, 'x': n * cw, 'y': 0, 'w': cw, 'h': ch})
    views.append({'angle': 25, 'x': 0, 'y': ch, 'w': 500, 'h': 420, 'dist': 34, 'cy': 25, 'elev': 4, 'pose': hold})
    views.append({'angle': -30, 'x': 500, 'y': ch, 'w': 500, 'h': 420, 'dark': True, 'pose': walk, 'dist': 70})
    views.append({'angle': 140, 'x': 1000, 'y': ch, 'w': 500, 'h': 420, 'dist': 40, 'cy': 22, 'elev': 22})
    spec = {'w': 1500, 'h': ch + 420, 'views': views, 'data': m.to_json(), 'body': uri(atlas), 'hat': uri(hat_tex), 'hatEls': hat_els}
    html = PAGE % {'three': render.THREE, 'mcv': os.path.join(ROOT, 'tools/preview/mcviewer.js'),
                   'bv': os.path.join(ROOT, 'tools/blocks/bview.js'), 'spec': json.dumps(spec)}
    os.makedirs(OUT, exist_ok=True)
    fd, path = tempfile.mkstemp(suffix='.html', dir=os.path.join(SP, 'render'))
    with os.fdopen(fd, 'w') as fh:
        fh.write(html)
    out = os.path.join(OUT, 'preview.png')
    r = subprocess.run(['node', render.SHOT, path, out, str(spec['w']), str(spec['h'])], capture_output=True, text=True, timeout=180)
    if r.returncode:
        print(r.stdout[-1500:], r.stderr[-1500:])
    os.unlink(path)
    return out


def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as fh:
        json.dump(data, fh, indent=1)


def main():
    hum, leg = armour_textures()
    eq = os.path.join(ASSETS, 'textures/entity/equipment')
    os.makedirs(os.path.join(eq, 'humanoid'), exist_ok=True)
    os.makedirs(os.path.join(eq, 'humanoid_leggings'), exist_ok=True)
    hum.save(os.path.join(eq, 'humanoid', 'exorcista.png'))
    leg.save(os.path.join(eq, 'humanoid_leggings', 'exorcista.png'))
    sleeve_texture().save(os.path.join(ASSETS, 'textures/entity', 'exorcist_sleeve.png'))
    write_json(os.path.join(ASSETS, 'equipment', 'exorcista.json'),
               {'layers': {'humanoid': [{'texture': 'deadline:exorcista'}], 'humanoid_leggings': [{'texture': 'deadline:exorcista'}]}})
    model, hat_tex, els = export_hat()
    hat_tex.save(os.path.join(ASSETS, 'textures/item', 'exorcist_hat.png'))
    write_json(os.path.join(ASSETS, 'models/item', 'exorcist_hat.json'), model)
    write_json(os.path.join(ASSETS, 'items', 'exorcist_hat.json'), {'model': {'type': 'minecraft:model', 'model': 'deadline:item/exorcist_hat'}})
    for key, img in icons().items():
        img.save(os.path.join(ASSETS, 'textures/item', key + '.png'))
        write_json(os.path.join(ASSETS, 'models/item', key + '.json'),
                   {'parent': 'minecraft:item/generated', 'textures': {'layer0': f'deadline:item/{key}'}})
        write_json(os.path.join(ASSETS, 'items', key + '.json'), {'model': {'type': 'minecraft:model', 'model': f'deadline:item/{key}'}})
    os.makedirs(OUT, exist_ok=True)
    hum.resize((hum.width * 4, hum.height * 4), Image.NEAREST).save(os.path.join(OUT, 'humanoid_x4.png'))
    leg.resize((leg.width * 4, leg.height * 4), Image.NEAREST).save(os.path.join(OUT, 'leggings_x4.png'))
    print(preview(hum, leg, hat_tex, els))


if __name__ == '__main__':
    main()
