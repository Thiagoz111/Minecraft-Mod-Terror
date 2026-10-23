"""Ofelia -- the cursed antique porcelain doll, anchor of CASO 2 'Casa Morales' (DEAD LINE).

Authored at 2x texel density (model.scale = 0.5).  +Y down, ground y = 24, faces -Z, right_* on -X.

Story beat she carries: in 1961 Padre Anselmo shut the demon AZAMEL inside her by sewing her mouth with blessed red
thread.  Lucia (8) cut those stitches, so she arrives with the mouth CUT ('cortado', the default look): the old thread
is dried, faded red; stubs stay in the needle holes and two loose ends hang from her lips and sway (bones
thread_right / thread_left, two segments each).  In the finale the Nona sews it shut again with FRESH red thread:
look 'cosida' = three bright cross-stitches standing proud of the face (toggle bones stitch_1..3 under 'stitches',
shown one by one in the stitch minigame) over lips pressed into a seam; the hanging ends are hidden.

Design
------
Silhouette: a bisque toddler doll whose head is about half her height: a domed cranium under a
chestnut wig with sausage ringlets, cheeks as wide as the skull and a tapered marionette chin.  A thin
porcelain neck on a ball joint, a short burgundy bodice with puffed sleeves and a lace bertha collar,
a two-tier bell skirt (8 gathered panels, each with a flared, torn hem panel hinged under it) over a
torn lace petticoat, ball knees, porcelain shins,
frilled socks and black Mary Janes.  The arms are too long (hands at shin level) with spidery
three-fingered porcelain hands.  The rest pose is wrong on purpose: the head is rolled 14 degrees onto
her right shoulder and turned a little, the left shoulder is dropped and the left forearm hangs loose
below the elbow, held on only by the stringing cord (a visible gap with the cord in it).

Face (the jumpscare portrait), front of a 2-texel porcelain mask so every break has real depth:
* her right eye (viewer's left) is a glossy blue glass eye recessed behind the mask, dilated pupil,
  one glint, a painted lid line and single spiky lashes;
* her left eye is gone: a round black socket with a shaded rim, a bright chipped lower lip and a dying
  2-px ember deep inside; a glossy black tear runs from it over clean porcelain and drips off the jaw;
* the top corner of her left temple is broken away (a real notch through mask, wig and crown, dark
  inside) and one hairline crack runs from it through the socket to the corner of the mouth;
* a small rosebud mouth whose three 1961 stitches were cut: needle holes above and below the lips, short
  frayed stubs left in some of them, one hole torn empty where the crack from the socket ends; her right
  corner curls up.  The long loose ends are geometry (thread_right from the upper hole, thread_left from
  the lower hole on the chin) hanging plumb in front of chin and collar;
* the chin is a marionette jaw in two slots: it drops straight down (and hinges a little) to show a
  black throat with uneven bisque teeth top and bottom, one missing.
A dusty red bow is pinned on the top-left of her hairline, its notched tails hanging over the ringlets.
"""
import math
import os

import numpy as np

from mcmodel import Model, hash3, face_light, pick, rot_matrix
from rig import Rig
from paint import hx, mix


def pal(*h):
    return [hx(c) for c in h]


# ------------------------------------------------------------------ palettes (dark -> light, hue shifted)
PORC = pal('#20223a', '#383f5e', '#5a6386', '#808bac', '#a4b0d0', '#c0cbe8', '#d6e0f8', '#e9f0ff')
CHIP = hx('#ffffff')
CRACK = hx('#5a5260')
CRACK_D = hx('#17121b')
GRIME = hx('#8a7d74')
ROUGE = pal('#c9737d', '#dc8f96', '#eab0b3')
LIP = pal('#4a0812', '#7a121e', '#a8202c', '#cf4446')
TEAR = pal('#020203', '#0a090d', '#1f1d27', '#9aa3c0')
VOID = pal('#000000', '#030204', '#07050a', '#0d0a10')
GLASS = pal('#06102a', '#0e2152', '#173c88', '#2462bd', '#468ce2', '#86c0f6', '#e8f8ff')
LASH = pal('#0b070a', '#2a1c22', '#5c4a50')
MOUTH = pal('#020102', '#10030a', '#260812', '#45101e', '#6a1f2c')
GUM = pal('#2a0710', '#4a0f1b', '#6e1d29', '#93323b')
TEETH = pal('#6a6458', '#a8a294', '#dcd8cc', '#f6f4ec')
EMBER = pal('#3a0503', '#7a0f06', '#d0300e', '#ff7a2a')

HAIR = pal('#140905', '#24100a', '#3a1b0f', '#532714', '#6d3519', '#89461f', '#a65d2c', '#c98048')
BOW = pal('#250a0e', '#421318', '#621d22', '#82292c', '#9e3a38', '#b9554b', '#cc7363')
DRESS = pal('#1e0b14', '#35111f', '#4f1829', '#6a2033', '#862a3e', '#a0384a', '#b84d59', '#cc6a6c')
LACE = pal('#3a332b', '#5d5447', '#857a68', '#ab9f88', '#cbc0a6', '#e2d8bf', '#f2ebd6')
MUD = pal('#120c08', '#22170f', '#352516', '#4a3520')
SHOE = pal('#040305', '#0b0a0f', '#15131b', '#221f2a', '#3a3646', '#6c6880', '#a9a7bd')
SOLE = pal('#2a2420', '#43392f', '#5e5144', '#7a6b5a')
SOLE_L = pal('#120b08', '#22160e', '#332217', '#4b3322', '#6a4a31')   # old leather sole, scuffed
BRASS = pal('#3b2a10', '#6e5220', '#a8853a', '#dcc070')
CORD = pal('#1a120c', '#33251a', '#4e3a28', '#6d553d')
# the 1961 blessed thread: sixty years buried in a biscuit tin -- dried, brown-shifted, faded red
OLDT = pal('#1c0507', '#3c0c12', '#621519', '#882224', '#a63834', '#c25c55')
# the new thread the Nona sews with: vivid scarlet with a hot highlight (reads on white porcelain and in the dark)
NEWT = pal('#3a0206', '#7a050c', '#b80d14', '#e3241f', '#ff5a3c', '#ffa07a')
HOLE = hx('#2b0b12')

# ------------------------------------------------------------------ looks
# VARIANT_MATS index 0 'cortado' (default, cut thread) / 1 'cosida' (sewn shut again).  The face materials read the
# look being painted from _LOOK (set by MunecaModel.paint from the material's .look).
LOOKS = ('cortado', 'cosida')
_LOOK = ['cortado']


def clamp(v, a=0.0, b=1.0):
    return a if v < a else b if v > b else v


# ------------------------------------------------------------------ texel helpers
def local(ctx):
    """Texel centre in cube-local texel units (independent of bone rotation)."""
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


def A(ctx):
    """Absolute authoring coordinates (rest pose, before any bone rotation)."""
    lx, ly, lz = local(ctx)
    o = ctx.cube.a0
    return o[0] + lx, o[1] + ly, o[2] + lz


def edge(ctx):
    return min(ctx.i, ctx.j, ctx.w - 1 - ctx.i, ctx.h - 1 - ctx.j)


def tag(ctx):
    return ctx.cube.name or ''


def cseed(ctx):
    o, sz = ctx.cube.a0, ctx.cube.size
    return int(abs(o[0]) * 13.1 + abs(o[1]) * 7.3 + abs(o[2]) * 3.7 + sz[0] * 31 + sz[1] * 17 + sz[2] * 5) % 9973


def is_plane(ctx):
    return 0 in ctx.cube.size


def at(points):
    """Decal painting single texels: points = [(i, j, rgba), ...] relative to the face rect."""
    def fn(img, u0, v0, w, h):
        px = img.load()
        for i, j, c in points:
            if 0 <= i < w and 0 <= j < h:
                px[u0 + i, v0 + j] = c
    return fn


# ------------------------------------------------------------------ porcelain (limbs, neck, skull)
def porc_v(ctx, base=0.78):
    v = base + face_light(ctx) * 1.05
    if edge(ctx) == 0 and ctx.face != 'top' and not is_plane(ctx):
        v -= 0.07
    return v


def porcelain(ctx):
    return pick(PORC, porc_v(ctx))


def limb_mat(ctx):
    """Clean porcelain limbs: round-shaded ball joints, dirt only in the joint sockets, one hairline crack."""
    x, y, z = A(ctx)
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    t = tag(ctx)
    f = ctx.face
    v = porc_v(ctx, 0.76)
    if t == 'ball':
        if f not in ('top', 'bottom'):
            v += 0.06 - abs(ly / max(1, h) - 0.4) * 0.4
            u = lx / max(1, w) if f in ('front', 'back') else lz / max(1, d)
            v -= abs(u - 0.5) * 0.3
        c = pick(PORC, v)
        if f not in ('top', 'bottom') and ly > h - 0.9:
            c = mix(c, GRIME, 0.45)                    # grime in the socket under the ball
        return c
    if t in ('forearm', 'shin', 'upper', 'neck') and f not in ('top', 'bottom') and ly < 0.9:
        return mix(pick(PORC, v - 0.18), GRIME, 0.35)    # socket shadow under the joint above
    if t in ('palm', 'finger', 'thumb') and f == 'bottom':
        v -= 0.08
    c = pick(PORC, v)
    if t in ('finger', 'thumb') and ly > h - 0.9 and f != 'top':
        c = mix(c, GRIME, 0.5)                          # dirty fingertips
    if t == 'shin' and f == 'front' and ctx.i == 0 and 0 < ctx.j < h - 1:
        c = CRACK                                       # hairline crack down one shin
    if t == 'forearm' and f in ('front', 'east') and ctx.j == 1 and ctx.i == 1 and x > 0:
        c = CRACK_D                                     # chipped broken forearm
    return c


# ------------------------------------------------------------------ the broken temple
def chunk3(x, y, z):
    """The broken-away corner of her left temple (shared by mask, crown and wig)."""
    return (7.0 - x) / 4.0 + (y + 1.5) / 2.6 + (z + 6.0) / 4.6 < 1.0


def near_chunk(x, y, z, r=0.9):
    for dx, dy, dz in ((r, 0, 0), (-r, 0, 0), (0, r, 0), (0, -r, 0), (0, 0, r), (0, 0, -r)):
        if chunk3(x + dx, y + dy, z + dz):
            return True
    return False


# ------------------------------------------------------------------ the face
# Mask front, 14 x 10 (x -7..7, y -1.5..8.5).  Legend:
#  o porcelain  O highlight  s soft shade  x crease dirt   h chip (bright break edge)  c crack
#  . hole (glass eye / socket)  X broken chunk  r socket rim  l/e lash  W lid line
#  p/P blush  k tear  g tear gloss  M lip line  L/R/Q lip (dark -> light)
#  u empty needle hole   H needle hole with old thread in it   T/t old thread stub (light/dark)  F frayed fibre
#  i lips pressed into a seam (cosida)   z porcelain puckered toward a stitch hole (cosida)
FACE_TOP = [
    # 0123456789ABCD
    "oooooOOOoohXXX",   # r0  forehead (bangs over the left); a chunk broken out of the corner
    "oooooooooochXX",   # r1  the crack leaves the chunk, chipped lip of the break
    "lololoooocsohh",   # r2  single spiky lashes | crack runs into the socket
    "eWWWWWoos..soo",   # r3  lid line over the glass eye | round socket
    "s.....os....so",   # r4  glass eye (eyeball behind) | socket (ember deep inside)
    "s.....os....so",   # r5
    "o.....oos..soo",   # r6
    "oeoeoeooChhkoo",   # r7  lower lashes | hairline crack + chipped lower lip | the tear leaves the socket
]
# The mouth, per look.  Plate rows r8 (above the lip) and r9 (upper lip) are 14 wide (x -7..7); the chin rows c10
# (lower lip) and c11 (needle holes) are 6 wide (x -3..3, face columns 4..9); 'tip' is the chin tip (columns 5..8).
# The three 1961 stitches went through columns 5, 7 and 9.
MOUTH_ROWS = {
    'cortado': {
        # Nothing crosses the lips any more: the stitches were snipped at the seam.  What is left sits in the
        # holes: r8 col 5 = thread_right leaves it, col 7 = a cut stub (T) whose frayed end (F) lies sideways toward
        # col 9 = torn empty (the crack ends in it)
        'r8': "pPpMoHoTFuhkpp",   # ... | 10 chip | 11 the black tear
        'r9': "ppooMLRRLMogPp",   # rosebud upper lip (shadowed) with dark corners
        'c10': "sRQQRs",          # fuller lower lip catching the light
        'c11': "FTouoH",          # holes: cut stub in 5, frayed end lying out to 4 | torn-out 7 | 9: thread_left
        'tip': "soos",
    },
    'cosida': {
        # three fresh cross-stitches (geometry planes, stitch_1..3) cross the seam at x -3, 0, 3; their corner
        # holes are columns 2, 5, 8, 11.  Under them the lips are pulled into a tight seam and the porcelain
        # puckers toward every hole; the old 1961 holes (7, 9) stay as empty punctures.
        'r8': "pPuzouoouuhkpp",
        'r9': "ppozMLRRLMogPp",
        'c10': "ziiiiz",
        'c11': "zuoouz",
        'tip': "soos",
    },
}
# Lower face 12 x 2 (x -6..6, y 8.5..10.5); the chin slot (x -3..3) is open.
FACE_B = {
    'cortado': ["pps......skp", "sos......oks"],
    'cosida': ["pzs......skp", "suz......zks"],
}
FACE_COLS = {
    'h': CHIP, 'c': CRACK_D, 'r': hx('#2a2026'), 'l': LASH[0], 'e': LASH[1], 'W': LASH[0],
    'k': TEAR[0], 'g': TEAR[3], 'M': LIP[0], 'R': LIP[2], 'Q': LIP[3],
    'C': CRACK,
    'L': LIP[1],
    'H': OLDT[2], 'T': OLDT[4], 't': OLDT[2], 'F': OLDT[5], 'i': hx('#3a0711'),
}


def mouth():
    return MOUTH_ROWS[_LOOK[0]]


def face_row(j):
    """Plate front row j (0..9) for the look being painted."""
    return FACE_TOP[j] if j < 8 else mouth()['r%d' % j]
# ember deep in the socket, in skull-front texels (i = face column, j = face row - 1)
EMBER_PX = {(9, 4): EMBER[2], (10, 4): EMBER[3]}
NOSE_FRONT = [None, None]   # filled after PORC (see nose_mat)


def face_base(fx, fy):
    """Clean porcelain shading of the face mask, by face pixel (fx 0..13, fy 0..12)."""
    cx = (fx - 6.5) / 7.0
    v = 0.92 - cx * cx * 0.16
    if fy >= 9:
        v -= (fy - 8) * 0.04                     # jaw rounds under
    if 2 <= fx <= 11 and fy <= 1:
        v += 0.04                                # domed forehead catches the light
    return v


def face_px(ch, fx, fy):
    if ch in FACE_COLS:
        return FACE_COLS[ch]
    base = face_base(fx, fy)
    if ch == 'O':
        return PORC[7]
    if ch == 's':
        return pick(PORC, base - 0.12)
    if ch == 'x':
        return mix(pick(PORC, base - 0.1), GRIME, 0.45)
    if ch == 'd':
        return mix(pick(PORC, base - 0.1), LIP[0], 0.35)   # needle puncture
    if ch == 'u':
        return mix(pick(PORC, base - 0.2), HOLE, 0.8)      # empty needle hole
    if ch == 'z':
        return mix(pick(PORC, base - 0.13), ROUGE[0], 0.22)  # porcelain dimpled toward a hole (blush shows in it)
    if ch == 'p':
        return mix(pick(PORC, base), ROUGE[2], 0.75)
    if ch == 'P':
        return ROUGE[1]
    return pick(PORC, base)


def plate_mat(ctx):
    """The porcelain face mask (front 2 texels of the head) and the lower face."""
    f = ctx.face
    part = tag(ctx)
    if f == 'back':
        return None
    x, y, z = A(ctx)
    if part == 'cheek':
        if f == 'back':
            return None
        v = porc_v(ctx, 0.86)
        c = pick(PORC, v)
        if f in ('front', 'west', 'east') and 0 < ctx.j < 3:
            c = mix(c, ROUGE[2], 0.6)                   # blush wraps round the cheek pads
        if f == 'bottom':
            c = mix(pick(PORC, 0.55), GRIME, 0.25)
        return c
    if f == 'front':
        if part == 'plate':
            ch, fx, fy = face_row(ctx.j)[ctx.i], ctx.i, ctx.j
        else:
            ch, fx, fy = FACE_B[_LOOK[0]][ctx.j][ctx.i], ctx.i + 1, ctx.j + 10
        if ch in '.X':
            return None
        return face_px(ch, fx, fy)
    if chunk3(x, y, z):
        return None
    if near_chunk(x, y, z, 0.8):
        return CHIP
    if f == 'top':
        return pick(HAIR, 0.32 + face_light(ctx))      # hairline over the forehead
    if f == 'bottom':
        if part == 'plate':
            if -3 < x < 3:
                # upper gum + uneven bisque teeth roots, only seen when the jaw drops
                return pick(GUM, 0.5) if z > -5.0 else pick(TEETH, 0.45)
            return pick(PORC, 0.5)
        if -3 < x < 3:
            return None
        if 4.0 < x < 5.0:
            return TEAR[0]                              # the tear drips off the jaw line
        return pick(PORC, 0.5)
    # cheek sides: porcelain with the blush wrapping round, crease dirt at the jaw line
    v = porc_v(ctx, 0.8)
    c = pick(PORC, v)
    if 5.5 <= y <= 9.5 and z < -4.6:
        c = mix(c, ROUGE[2], 0.55)
    if part == 'lower' and ctx.j == ctx.h - 1:
        c = mix(c, GRIME, 0.3)
    return c


def skull_mat(ctx):
    """Skull behind the mask: darkness inside (seen through the holes), one dying ember in the socket."""
    f = ctx.face
    x, y, z = A(ctx)
    if f == 'front':
        return skull_front_px(ctx.i, ctx.j)
    if chunk3(x, y, z):
        return None
    if f == 'top' and not near_chunk(x, y, z, 1.2):
        return pick(HAIR, 0.2)                          # under the wig: the wig cap (never flashes white)
    return porcelain(ctx)


def skull_front_px(i, j):
    return EMBER_PX.get((i, j), VOID[1])


def void_mat(ctx):
    """Inside of the broken head."""
    return pick(VOID, 0.15 + hash3(ctx.i, ctx.j, ord(ctx.face[0]), 3) * 0.3)


EYEBALL = [
    "nbBbn",
    "bwKKb",
    "lbKKl",
]
EYE_COL = {'n': GLASS[1], 'b': GLASS[3], 'B': GLASS[4], 'l': GLASS[4], 'K': hx('#020208'), 'w': GLASS[6]}
EYE_GLOW = {'n': hx('#123068'), 'b': hx('#1f4f9c'), 'B': hx('#3b7bd0'), 'l': hx('#3b7bd0'), 'w': hx('#ffffff')}


def eyeball_mat(ctx):
    if ctx.face != 'front':
        return GLASS[0]
    return EYE_COL[EYEBALL[ctx.j][ctx.i]]


NOSE_FRONT = [PORC[7], PORC[6]]


def nose_mat(ctx):
    f = ctx.face
    if f == 'back':
        return None
    if f == 'bottom':
        return mix(pick(PORC, 0.55), GRIME, 0.35)
    if f == 'top':
        return PORC[7]
    if f == 'front':
        return NOSE_FRONT[ctx.i]
    return PORC[5]


def chin_mat(ctx):
    f = ctx.face
    lx, ly, lz = local(ctx)
    t = tag(ctx)
    if f == 'front':
        mo = mouth()
        rows = (mo['c10'], mo['c11']) if t == 'chin' else (mo['tip'],)
        ch = rows[ctx.j][ctx.i]
        fx = ctx.i + (4 if t == 'chin' else 5)
        fy = ctx.j + (10 if t == 'chin' else 12)
        return face_px(ch, fx, fy)
    if f == 'top':
        if t != 'chin':
            return pick(PORC, 0.6)
        # lower gum (only seen when the jaw drops)
        return pick(GUM, 0.65 - lz * 0.15)
    if f == 'back':
        return pick(MOUTH, 0.2)
    if f == 'bottom':
        return pick(PORC, 0.5)
    # the sides slide in the slots: darker, dirty
    return mix(pick(PORC, 0.62 - (0.1 if ctx.i == 0 else 0)), GRIME, 0.35)


def teeth_mat(rows):
    """Uneven bisque teeth on a zero-thickness plane; one missing tooth."""
    def f(ctx):
        if ctx.face != 'front':
            return None                      # one face only: the plane is drawn double-sided
        i = ctx.i
        ch = rows[ctx.j][i]
        if ch == '.':
            return None
        v = {'T': 0.9, 't': 0.62, 'g': None}[ch]
        if v is None:
            return GUM[1]
        if ctx.face == 'back':
            v -= 0.3
        return pick(TEETH, v)
    return f


def throat_mat(ctx):
    f = ctx.face
    if f == 'front':
        lx, ly, lz = local(ctx)
        if tag(ctx) == 'gullet':
            return pick(MOUTH, 0.55 if ly > 3 and 1 <= ctx.i <= 4 else 0.12)   # a dark tongue
        if ly < 1.0:
            return pick(GUM, 0.3)
        return pick(MOUTH, 0.3 - ly * 0.1)
    if f in ('bottom', 'west', 'east'):
        return pick(PORC, 0.52)
    return MOUTH[0]


# ------------------------------------------------------------------ hair
def strand(u, v, ctx, seed, sheen_at=None, light=1.0):
    """Painted wig: clumps of 2-3 strands, dark gaps between clumps, one sheen band."""
    cl = math.floor((u + hash3(seed, 1, 0, 9) * 3) / 2.5)
    k = hash3(cl, seed, 0, 71)
    val = 0.42 + k * 0.18 + face_light(ctx) * light
    fu = ((u + hash3(seed, 1, 0, 9) * 3) / 2.5) % 1.0
    if fu < 0.3:
        val -= 0.16                                  # gap between clumps
    if sheen_at is not None:
        band = sheen_at + (k - 0.5) * 1.4
        if band <= v < band + 1.0:
            val += 0.26
        elif band + 1.0 <= v < band + 1.8:
            val += 0.1
    return val


PART_X = -1.5      # side parting over her right eye
WHORL_Z = 2.5      # where the parting ends at the crown


def hair_top_v(x, z, ctx):
    """Top of the wig, the surface players see most (she is under 1 block tall and usually below eye level).
    Strands leave the parting and are combed out and back (slanted, slightly wavy), so clumps never line up into
    planks; the gaps between clumps are broken into dashes; the sheen is a curved 'angel ring' round the crown,
    not a straight line; the rim darkens where the head rounds over."""
    d = x - PART_X
    ad = abs(d)
    u = z - ad * 0.7 + math.sin(ad * 0.7 + (0.0 if d < 0 else 2.0)) * 0.6 + (0.0 if d < 0 else 1.1)
    cl = math.floor(u / 2.4)
    fu = (u / 2.4) % 1.0
    k = hash3(cl, 1 if d < 0 else 2, 0, 71)
    v = 0.44 + k * 0.06 - min(ad, 7.0) * 0.008
    gap = fu < 0.3 and hash3(cl, int(ad * 0.8), 0, 13) > 0.15
    if gap:
        v -= 0.11                                     # gap between clumps (only now and then interrupted)
    r = math.sqrt((d / 1.25) ** 2 + (z - 0.4) ** 2)   # elliptical ring round the crown
    band = 4.2 + (k - 0.5) * 0.5
    if band <= r < band + 1.1:
        v += 0.16 if gap else 0.3                     # the satin 'angel ring' of an old mohair wig
    elif band - 0.8 <= r < band and not gap:
        v += 0.1                                      # soft inner edge of the ring
    if z < WHORL_Z:
        if ad < 0.5 and hash3(int(z + 9), 4, 0, 5) > 0.25:
            v = 0.2                                   # the parting: a broken seam of shadow, not a line
        elif ad < 1.1:
            v -= 0.08                                 # hair lifting off the parting, shadowed
    if edge(ctx) == 0:
        v -= 0.07                                     # rounds over at the rim
    return v


def wig_top_px(x, z, ctx):
    return pick(HAIR, hair_top_v(x, z, ctx))


def hair_shell(ctx):
    """Wig over the skull: side parting on top, strands radiating from it, bare over the face/cheeks."""
    f = ctx.face
    x, y, z = A(ctx)
    t = tag(ctx)
    if f == 'front' and t not in ('dome', 'crown_hair'):
        return None
    if chunk3(x, y, z):
        return None
    if f == 'bottom':
        return pick(HAIR, 0.18) if z > 2 else None
    if f == 'front':
        if t == 'crown_hair':
            # only its top sliver shows above the face plate: the hairline, dark and shadowed under the fringe
            return pick(HAIR, 0.3 + (0.08 if ctx.i % 3 == 0 else 0))
    if t == 'dome' and f != 'top':
        # the crown's rounded step: short strands combed down over it, darker toward the lower rim
        u = x if f in ('front', 'back') else z
        return pick(HAIR, strand(u, y, ctx, 11, sheen_at=None) + 0.04 - (0.06 if ctx.j == ctx.h - 1 else 0))
    if f in ('west', 'east') and z < -2.0 and y > 2.5:
        return None                                   # cheek / jaw left bare
    if near_chunk(x, y, z, 0.7):
        return pick(HAIR, 0.08)                       # torn wig edge
    if f == 'top':
        return wig_top_px(x, z, ctx)
    if f in ('west', 'east'):
        u = z + (0 if f == 'west' else 40)
        val = strand(u, y, ctx, 5 if f == 'west' else 6, sheen_at=1.0) - clamp((y - 5) / 6) * 0.14
        return pick(HAIR, val)
    val = strand(x, y, ctx, 7, sheen_at=1.5) - clamp((y - 4) / 7) * 0.16
    return pick(HAIR, val)


BANGS = [
    # 8 wide x 2 tall, side-swept fringe over her right brow (x -7..1)
    "aBbaBbaB",
    "Bb.Bb...",
]


def bangs_px(ch, j):
    return pick(HAIR, {'a': 0.62, 'B': 0.4, 'b': 0.52}[ch] - j * 0.1)


def bangs_mat(ctx):
    f = ctx.face
    if f != 'front':
        return None
    ch = BANGS[ctx.j][ctx.i]
    if ch == '.':
        return None
    return bangs_px(ch, ctx.j)


def curl_mat(ctx):
    """Sausage ringlet: a 2-tone diagonal spiral wrapping the tube, one highlight per turn."""
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    if f == 'top':
        return pick(HAIR, 0.4)
    if f == 'bottom':
        return pick(HAIR, 0.25)
    if f == 'front':
        u = lx
    elif f == 'east':
        u = w + lz
    elif f == 'back':
        u = w + d + (w - lx)
    else:
        u = 2 * w + d + (d - lz)
    per = 2 * (w + d)
    turn = 3.0 if tag(ctx) == 'coil' else 2.0
    phase = (ly + u / per * turn + cseed(ctx) * 0.37) % turn
    v = 0.44 + face_light(ctx) * 0.8 - clamp(ly / h) * 0.06
    if phase < turn * 0.42:
        v += 0.1                                      # coil body
        if f in ('front', 'west') and phase < 0.9 and (ctx.i == 0 if f == 'front' else ctx.i == ctx.w - 1):
            v += 0.24                                 # single highlight on the lit edge
    else:
        v -= 0.16                                     # shadowed groove
    if tag(ctx) == 'tip' and ly > h - 1:
        v -= 0.08
    return pick(HAIR, v)


def stray_mat(ctx):
    if ctx.face not in ('front', 'west'):
        return None                          # one face per plane (no coplanar z-fighting)
    lx, ly, lz = local(ctx)
    h = ctx.cube.size[1]
    if ly > h - 1 and hash3(ctx.i, cseed(ctx), 0, 5) > 0.5:
        return None
    return pick(HAIR, 0.5 - ly / h * 0.15 + (0.12 if ctx.face in ('front', 'west') else 0))


# ------------------------------------------------------------------ bow
LOOP = [
    # 5 x 4 left loop (the right loop is this mirrored): wide rounded far end, pinched at the knot (col 4)
    ".##..",
    "#####",
    "#####",
    ".###.",
]


def bow_mat(ctx):
    """Dusty faded satin: pinched folds at the knot, sun-faded crests, dust in the creases."""
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    t = tag(ctx)
    side = getattr(ctx.cube, 'side', '')
    if is_plane(ctx) and f != 'front':
        return None                          # ribbon tails: one face only (drawn double-sided)
    v = 0.52 + face_light(ctx) * 1.0
    if t == 'loop':
        if f in ('front', 'back'):
            i = ctx.i if f == 'front' else ctx.w - 1 - ctx.i
            ii = i if side == 'l' else ctx.w - 1 - i     # 0 = far end, 4 = at the knot
            if LOOP[ctx.j][ii] == '.':
                return None
            v += 0.16 - ii * 0.07                       # light on the rounded far end
            if ctx.j == 2 and 1 <= ii <= 3:
                v -= 0.15                               # fold crease
            if ctx.j == 0 or LOOP[max(0, ctx.j - 1)][ii] == '.':
                v += 0.07                               # lit rolled top edge
            if f == 'back':
                v -= 0.22
        else:
            if f in ('top', 'bottom'):
                ii = ctx.i if side == 'l' else ctx.w - 1 - ctx.i
                if LOOP[0 if f == 'top' else 3][ii] == '.':
                    return None
            if f in ('west', 'east'):
                far = (f == 'west') == (side == 'l')
                if not far or LOOP[ctx.j][0] == '.':
                    return None                         # only the rounded far end, shaped like the mask
            v -= 0.08
    elif t == 'knot':
        v -= 0.06
        if f == 'front' and ctx.j == ctx.h - 1:
            v -= 0.14
        if f == 'front' and ctx.i == 0:
            v += 0.1
    elif t == 'tail':
        if f not in ('front', 'back'):
            return None
        if ly > h - 1 and ctx.i == 1:
            return None                                 # notched ribbon end
        v -= ly / max(1, h) * 0.16 + (0.18 if f == 'back' else 0)
        if ctx.i == 0:
            v += 0.06
    c = pick(BOW, v)
    if hash3(int(lx * 2) + cseed(ctx), int(ly * 2), int(lz * 2), 33) > 0.86:
        c = mix(c, LACE[2], 0.3)                        # dust
    return c


# ------------------------------------------------------------------ dress
def dress_mat(ctx):
    """Victorian burgundy wool-silk: pleats, edge wear, grime rising from the hem, a few hand stains."""
    x, y, z = A(ctx)
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    t = tag(ctx)
    f = ctx.face
    v = 0.56 + face_light(ctx) * 1.1
    if edge(ctx) == 0 and f != 'top':
        v -= 0.06
    if t == 'panel':
        if f == 'back':
            return pick(DRESS, 0.16)
        cut = HEM_CUTS.get((cseed(ctx) % 7, ctx.i), 0) if f == 'front' else 0
        if f in ('front', 'west', 'east') and ly > h - cut:
            return None                                 # torn notches in the hem
        if f == 'front':
            pl = ctx.i % 3
            v += (0.1, 0.02, -0.12)[pl]                 # box pleats
            v -= clamp((ly - 1) / h) * 0.1
            if ly > h - 1 - (cut > 0):
                v -= 0.1
        if f == 'bottom':
            v -= 0.2
        c = pick(DRESS, v)
        if f in ('front', 'west', 'east'):
            m = clamp((ly - (h - 2.2)) / 2.0)
            c = mix(c, MUD[2], m * 0.55)                # grime soaked up from the floor
        return c
    if t == 'puff':
        if f in ('front', 'back', 'west', 'east'):
            v += 0.1 * (1 if ctx.i % 2 == 0 else -0.6)  # gathers
            v -= abs(ly / max(1, h) - 0.45) * 0.4
    if t == 'bodice':
        if f == 'front':
            if ctx.i in (3, 4):
                v -= 0.1                                # placket
                if ctx.i == 4 and ctx.j % 2 == 1:
                    return pick(LACE, 0.88)             # pearl buttons
            if ctx.j == 0:
                v -= 0.1
    if t == 'core' and f in ('front', 'west', 'east', 'back'):
        v -= 0.1
    if t == 'panel_top':
        if f == 'back':
            return pick(DRESS, 0.16)
        if f == 'front':
            v += (0.08, 0.0, -0.12)[ctx.i % 3] - 0.06 * (1 - ctx.j)   # gathers, shadowed under the sash
    c = pick(DRESS, v)
    # hand-placed stains: the black tear dripped onto the chest, a dark smear on her left side
    if t == 'bodice' and f == 'front' and ctx.i == 6 and ctx.j >= 1:
        c = mix(c, TEAR[0], 0.35)
    if t == 'bodice' and f == 'east' and ctx.j == 2:
        c = mix(c, MUD[1], 0.5)
    return c


HEM_CUTS = {(0, 1): 1, (0, 4): 2, (1, 2): 1, (2, 0): 2, (2, 5): 1, (3, 3): 2, (4, 1): 1, (5, 4): 1, (6, 2): 2,
            (1, 5): 1, (3, 0): 1, (5, 0): 2}


def lace_mat(ctx):
    """Yellowed lace: scalloped edge, eyelets, a fine net above; grime only toward the hem and in creases."""
    x, y, z = A(ctx)
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    f = ctx.face
    t = tag(ctx)
    v = 0.68 + face_light(ctx) * 1.0
    if f == 'bottom':
        return None if t in ('collar', 'cuff', 'sock', 'jabot') else pick(LACE, 0.3)
    if f == 'back' and t == 'jabot':
        return None
    if f != 'top':
        u = ctx.i
        if ctx.j == ctx.h - 1:
            if u % 3 == 2:
                return None                             # scallop gaps
            if t == 'petticoat' and (u // 3 + cseed(ctx)) % 5 == 0:
                return None                             # torn-out scallop
            v -= 0.04
        elif ctx.j == ctx.h - 2 and u % 3 == 0 and h > 1:
            return pick(LACE, 0.42)                     # eyelet
        if t == 'jabot':
            if ctx.i in (0, ctx.w - 1) and ctx.j < ctx.h - 1:
                v -= 0.1
    else:
        if t == 'collar':
            r = max(abs(x) / 5.0, abs(z) / 3.0)
            if int(r * 6) % 2 == 0:
                v -= 0.07
    c = pick(LACE, v)
    if t == 'petticoat' and f != 'top':
        c = mix(c, MUD[3], clamp((ly - 0.5) / h) * 0.5)   # dirtier toward the hem
    if t in ('cuff', 'sock') and f != 'top' and ctx.j == ctx.h - 1:
        c = mix(c, MUD[3], 0.3)
    # the black tear stains the collar under her left cheek
    if t == 'collar' and f in ('top', 'front') and 3.5 < x < 4.5 and z < -1.5:
        c = mix(c, TEAR[1], 0.6)
    return c


def shoe_mat(ctx):
    """Black patent Mary Jane: glossy toe, strap with a tarnished buckle, grey sole and heel."""
    x, y, z = A(ctx)
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    f = ctx.face
    t = tag(ctx)
    if f == 'bottom':
        # the leather sole: what faces you when she sits with her legs out (toes up).  Read heel -> toe:
        # heel block (a tarnished nail), the shadowed breast of the heel, the narrow waist (darker at the sides),
        # the worn pale ball of the foot, and a rounded toe (black patent wraps its corners)
        i, j = ctx.i, ctx.j
        if t == 'toe':
            return pick(SHOE, 0.28) if i != 1 else SOLE_L[3]
        if j == 0:
            return BRASS[1] if i == 1 else SOLE_L[2]
        if j == 1:
            return SOLE_L[0]
        if j == 2:
            return SOLE_L[1] if i != 1 else SOLE_L[2]
        return SOLE_L[4] if i == 1 else SOLE_L[3]
    v = 0.3 + face_light(ctx) * 1.2
    if f == 'top':
        if t == 'shoe' and lz > d - 2.5:
            v = 0.1                                     # opening (the shin stands here)
        if t == 'shoe' and 1.0 < (d - lz) < 2.5 and 0.5 < lz:
            v = 0.42                                    # strap
        if t == 'toe':
            v = 0.62 if ctx.i == 1 else 0.48            # patent gloss on the rounded toe
    if f == 'front' and t == 'toe':
        v += 0.15 if ctx.i == 1 else 0.0
    if f in ('front', 'west', 'east') and ly > h - 1:
        return pick(SOLE, 0.5)                          # sole edge
    c = pick(SHOE, v)
    if t == 'shoe' and f in ('west', 'east') and ly < 1.0 and 1.0 < lz < 2.0:
        outer = (f == 'east') == (x > 0)
        if outer:
            c = BRASS[2]
    return c


def cord_mat(ctx):
    lx, ly, lz = local(ctx)
    return pick(CORD, 0.45 + face_light(ctx) + (0.25 if int(ly * 2) % 2 == 0 else 0))


def thread_mat(ctx):
    """Loose end of the 1961 thread: a two-ply twist (light / dark texels stepping round the strand), darker down
    the strand, the very end split into pale frayed fibres (front/back texel gone, the side plies left)."""
    f = ctx.face
    lx, ly, lz = local(ctx)
    h = ctx.cube.size[1]
    tip = tag(ctx) == 'thread_tip'
    if f == 'top':
        return OLDT[1]
    if f == 'bottom':
        return None if tip else OLDT[1]
    k = {'front': 0, 'east': 1, 'back': 2, 'west': 3}[f]
    last = tip and ctx.j == ctx.h - 1
    if last and f in ('front', 'back'):
        return None                                     # the plies split apart at the cut
    v = 0.6 + face_light(ctx) * 0.9 + (0.08 if (ctx.j + k) % 2 == 0 else -0.06)
    v -= (ly / max(1, h)) * (0.14 if tip else 0.05)
    if last:
        v = 0.86                                        # pale, frayed fibres
    return pick(OLDT, v)


# fresh cross-stitch: a '+' painted on a 5 x 5 plane that the stitch bone turns 45 degrees, so both threads are
# clean 1-texel diagonals (a pixel-drawn 4 x 4 X closes into a blob).  V = the top thread (lit, drawn over the
# crossing), h = the under thread, d = the ends diving into the needle holes.
XSTITCH = [
    "..d..",
    "..V..",
    "dhVhd",
    "..V..",
    "..d..",
]


def stitch_mat(ctx):
    if ctx.face != 'front':
        return None                                     # one face only (planes are drawn double-sided)
    ch = XSTITCH[ctx.j][ctx.i]
    if ch == '.':
        return None
    if ch == 'd':
        return NEWT[1]
    if ch == 'h':
        return NEWT[2]
    return NEWT[4] if ctx.j < 2 else (NEWT[5] if ctx.j == 2 else NEWT[3])   # sheen peaks on the crossing


# ------------------------------------------------------------------ module contract
def make_mat(lk):
    """Fallback material of look `lk`; MunecaModel.paint reads .look and every face material follows it."""
    def mat(ctx):
        return dress_mat(ctx)
    mat.look = lk
    return mat


DEFAULT_MAT = make_mat('cortado')
VARIANT_MATS = {'cortado': DEFAULT_MAT, 'cosida': make_mat('cosida')}
FOCUS = 'head'

# ------------------------------------------------------------------ toggles (Java: ModelPart.visible)
# bone -> visible in the default look 'cortado'.  stitch_1..3 live under 'stitches': in the stitch minigame Java shows
# 'stitches' with all three hidden and reveals one per completed puntada, then switches the texture to 'cosida'.
TOGGLE_DEFAULT = {'thread_right': True, 'thread_left': True, 'stitches': False,
                  'stitch_1': True, 'stitch_2': True, 'stitch_3': True}
VARIANT_TOGGLES = {
    'cortado': {},
    'cosida': {'thread_right': False, 'thread_left': False, 'stitches': True},
}


def visible_set(variant=None):
    vis = dict(TOGGLE_DEFAULT)
    vis.update(VARIANT_TOGGLES.get(variant or 'cortado', {}))
    show = os.environ.get('MUNECA_SHOW', '')            # preview helper: 'all' or 'bone,-bone' (- hides)
    items = show.split(',') if show else []
    for k in vis:
        if show == 'all' or k in items:
            vis[k] = True
        if '-' + k in items:
            vis[k] = False
    return {k for k, v in vis.items() if v}


class MunecaModel(Model):
    """Exports every bone to Java; the preview / gallery JSON hides the toggle bones the current look hides.
    paint() tells the face materials which look ('cortado' / 'cosida') is being painted."""
    visible = None

    def paint(self, default_mat, seed=1, layer='base'):
        _LOOK[0] = getattr(default_mat, 'look', 'cortado')
        try:
            return super().paint(default_mat, seed, layer)
        finally:
            _LOOK[0] = 'cortado'

    def to_json(self):
        d = super().to_json()
        d['toggles'] = {'default': dict(TOGGLE_DEFAULT),
                        'variants': {k: dict(v) for k, v in VARIANT_TOGGLES.items()}, 'poses': {}}
        if self.visible is None:
            return d
        hide = set()
        for b in self.bones():
            if b.name in TOGGLE_DEFAULT and b.name not in self.visible:
                for sub in b.walk():
                    hide.add(sub.name)
        for bd in d['bones']:
            if bd['name'] in hide and bd['cubes']:
                bd['hidden_cubes'] = bd['cubes']                       # a toggle-aware viewer can still show them
                bd['cubes'] = []
        return d


# ------------------------------------------------------------------ gravity for the loose thread ends
HEAD_REST = (4, -8, -14)                                                # degrees, see build()
REST_DEG = {'body': (0, 0, 0), 'neck': (0, 0, 0), 'head': HEAD_REST, 'jaw': (0, 0, 0)}
THREAD_CHAIN = {'thread_right': ('body', 'neck', 'head'), 'thread_left': ('body', 'neck', 'head', 'jaw')}


def _euler(R):
    """MC ZYX angles (radians) of R = Rz * Ry * Rx."""
    y = math.asin(max(-1.0, min(1.0, -R[2, 0])))
    return math.atan2(R[2, 1], R[2, 2]), y, math.atan2(R[1, 0], R[0, 0])


def _chain_rot(chain, pose):
    R = np.eye(3)
    for b in chain:
        r = REST_DEG[b]
        p = pose.get(b, (0, 0, 0, 0, 0, 0))
        R = R @ rot_matrix(math.radians(r[0]) + p[0], math.radians(r[1]) + p[1], math.radians(r[2]) + p[2])
    return R


def thread_rest_deg(name):
    """Rest rotation that cancels the rolled head so the thread hangs plumb."""
    return tuple(math.degrees(a) for a in _euler(_chain_rot(THREAD_CHAIN[name], {}).T))


def plumb(pose, sway=None):
    """Pose entries for the thread roots so they still hang plumb (plus an optional world-space sway, radians
    (xRot, zRot)) under `pose`.  Java does the same every frame: parent world rotation inverted + swing."""
    out = {}
    for name, chain in THREAD_CHAIN.items():
        sx, sz = (sway or {}).get(name, (0.0, 0.0))
        loc = _euler(_chain_rot(chain, pose).T @ rot_matrix(sx, 0, sz))
        rest = [math.radians(a) for a in thread_rest_deg(name)]
        d = [((loc[i] - rest[i] + math.pi) % (2 * math.pi)) - math.pi for i in range(3)]
        out[name] = (d[0], d[1], d[2], 0, 0, 0)
    return out


def build(variant=None):
    r = Rig()

    def box(bone, frm, size, mat=None, inflate=0.0, decals=None, name=None, side=''):
        c = r.box(bone, frm, size, mat=mat, inflate=inflate, decals=decals)
        c.a0 = tuple(float(v) for v in frm)
        c.name = name
        c.side = side
        return c

    bone = r.bone

    # ---------------- body (root, at the waist): bodice, lace bertha + jabot, sash with a back bow
    bone('body', (0, 15.0, 0), mat=dress_mat)
    box('body', (-4, 12.0, -2.5), (8, 3, 5), name='bodice')
    box('body', (-4.5, 14.4, -3), (9, 1, 6), mat=bow_mat, name='sash', inflate=0.1)
    box('body', (-5, 11.8, -3), (10, 1, 6), mat=lace_mat, name='collar', inflate=0.2)
    box('body', (-2, 12.6, -2.75), (4, 3, 0), mat=lace_mat, name='jabot')
    box('body', (-4.5, 13.2, 3.1), (3, 2, 1), mat=bow_mat, name='knot')
    box('body', (1.5, 13.2, 3.1), (3, 2, 1), mat=bow_mat, name='knot')
    box('body', (-1, 13.5, 3.2), (2, 2, 1), mat=bow_mat, name='knot')
    box('body', (-2.2, 15.0, 4.6), (2, 4, 0), mat=bow_mat, name='tail')
    box('body', (0.4, 15.0, 4.5), (2, 5, 0), mat=bow_mat, name='tail')

    # ---------------- neck on a ball joint
    bone('neck', (0, 12.0, 0.5), parent='body', mat=limb_mat)
    box('neck', (-1.5, 9.8, -1.0), (3, 2, 3), name='ball', inflate=0.25)
    box('neck', (-1, 11.6, -0.5), (2, 1, 2), name='neck')

    # ---------------- skirt: two-tier bell (8 gathered panels + 8 hinged, torn hem panels), torn lace petticoat
    bone('skirt', (0, 15.0, 0), parent='body', mat=dress_mat)
    box('skirt', (-4, 15.0, -3), (8, 3, 6), name='core')
    box('skirt', (-5, 17.8, -3.5), (10, 2, 7), mat=lace_mat, name='petticoat', inflate=0.2)
    box('skirt', (-3.5, 17.8, -5), (7, 2, 10), mat=lace_mat, name='petticoat', inflate=0.2)
    panels = [('skirt_front', 0, 2.2), ('skirt_front_right', 45, 3.0), ('skirt_right', 90, 3.4),
              ('skirt_back_right', 135, 3.0), ('skirt_back', 180, 2.2), ('skirt_back_left', -135, 3.0),
              ('skirt_left', -90, 3.4), ('skirt_front_left', -45, 3.0)]
    for k, (name, yaw, rad) in enumerate(panels):
        # bell: a steep gathered upper tier, then a flared, torn lower tier hinged on it
        bone(name, (0, 15.0, 0), parent='skirt', rot=(-12 - (k % 2) * 2, yaw, 0), mat=dress_mat)
        box(name, (-3, 15.0, -rad - 1), (6, 2, 1), name='panel_top')
        hem = name.replace('skirt_', 'hem_')
        bone(hem, (0, 17.0, -rad - 0.5), parent=name, rot=(-26 - (k % 3) * 3, 0, 0), mat=dress_mat)
        box(hem, (-3.5, 16.8, -rad - 1), (7, 3, 1), name='panel')

    # ---------------- legs: hidden thigh, ball knee, porcelain shin, frilled sock, Mary Jane
    for side, sx, yaw in (('right', -1, -14), ('left', 1, 5)):
        lb = f'{side}_leg'
        cx = 2.2 * sx
        bone(lb, (cx, 17.5, 0), parent='body', rot=(0, yaw, 0), mat=limb_mat)
        box(lb, (cx - 1.5, 17.0, -1.5), (3, 3, 3), name='upper')
        box(lb, (cx - 1.5, 19.6, -1.5), (3, 2, 3), name='ball', inflate=0.1)
        box(lb, (cx - 1, 21.2, -1), (2, 2, 2), name='shin', inflate=0.2)
        box(lb, (cx - 1.5, 21.6, -1.5), (3, 1, 3), mat=lace_mat, name='sock', inflate=0.2)
        box(lb, (cx - 1.5, 22, -2.2), (3, 2, 4), mat=shoe_mat, name='shoe')
        box(lb, (cx - 1.5, 23, -3.2), (3, 1, 1), mat=shoe_mat, name='toe')

    # ---------------- arms: puffed sleeve, lace cuff, ball elbow, porcelain forearm, spidery hand
    for side, sx in (('right', -1), ('left', 1)):
        ab, fb, hb = f'{side}_arm', f'{side}_forearm', f'{side}_hand'
        broken = sx > 0
        drop = 0.6 if broken else 0.0                   # her left shoulder sags
        ax, ay = 4.6 * sx, 12.6 + drop
        bone(ab, (ax, ay, 0), parent='body', rot=((3, 0, -13) if broken else (-4, 0, 15)), mat=limb_mat)
        cx = ax + 1.0 * sx
        box(ab, (cx - 2, ay - 0.8, -2), (4, 3, 4), mat=dress_mat, name='puff', inflate=0.35)
        box(ab, (cx - 2, ay + 2.0, -2), (4, 1, 4), mat=lace_mat, name='cuff', inflate=0.15)
        box(ab, (cx - 1, ay + 2.6, -1), (2, 1, 2), name='upper', inflate=0.15)
        box(ab, (cx - 1.5, ay + 3.4, -1.5), (3, 2, 3), name='ball', inflate=-0.15)
        ey = ay + 4.4 + (0.9 if broken else 0.0)        # the broken forearm hangs off the cord
        bone(fb, (cx, ey, 0), parent=ab, rot=((-34, 0, -34) if broken else (-10, 0, -3)), mat=limb_mat)
        if broken:
            box(fb, (cx - 0.5, ey - 1.5, -0.5), (1, 2, 1), mat=cord_mat, name='cord')
        box(fb, (cx - 1, ey + 0.4, -1), (2, 2, 2), name='forearm', inflate=0.2)
        hy = ey + 2.6
        bone(hb, (cx, hy, 0), parent=fb, rot=((30, 0, 10) if broken else (-6, 0, 6)), mat=limb_mat)
        box(hb, (cx - 0.5, hy, -1.5), (1, 2, 3), name='palm', inflate=0.2)
        box(hb, (cx - 0.5, hy + 0.3, -2.4), (1, 2, 1), name='thumb')
        for k, fz in enumerate((-1.4, -0.4, 0.6)):
            fn = f'{side}_finger{k + 1}'
            fy = hy + 1.8
            splay = (-12, 0, 6 * sx) if k == 0 else ((0, 0, 3 * sx) if k == 1 else (12, 0, 0))
            if broken:
                splay = (splay[0] - 50, 0, 0)          # dead hand: fingers curled in
            bone(fn, (cx, fy, fz + 0.5), parent=hb, rot=splay, mat=limb_mat)
            box(fn, (cx - 0.5, fy, fz), (1, 2, 1), name='finger')

    # ---------------- head: porcelain mask, skull, crown, wig; jaw, bow, ringlets
    bone('head', (0, 10.2, 0.5), parent='neck', rot=HEAD_REST, mat=porcelain)
    box('head', (-7, -1.5, -6), (14, 10, 2), mat=plate_mat, name='plate',
        decals={'eyes:front': at([(11, 9, hx('#6f7a9e'))])})
    box('head', (-6, 8.5, -6), (12, 2, 2), mat=plate_mat, name='lower')
    box('head', (-8, 4.5, -5.6), (1, 4, 3), mat=plate_mat, name='cheek')
    box('head', (7, 4.5, -5.6), (1, 4, 3), mat=plate_mat, name='cheek')
    ember = [(i, j, EMBER[3] if (i, j) == (10, 4) else EMBER[2] if (i, j) == (9, 4) else EMBER[1])
             for (i, j) in EMBER_PX]
    box('head', (-7, -0.5, -4), (14, 10, 10), mat=skull_mat, name='skull', decals={'eyes:front': at(ember)})
    box('head', (-6, -1.5, -4), (12, 1, 9), mat=skull_mat, name='crown')
    box('head', (2.5, -1.2, -5.6), (4, 3, 5), mat=void_mat, name='void')
    eye_glow = [(i, j, EYE_GLOW[EYEBALL[j][i]]) for j in range(3) for i in range(5) if EYEBALL[j][i] in EYE_GLOW]
    box('head', (-6, 2.5, -5.3), (5, 3, 1), mat=eyeball_mat, name='eyeball', decals={'eyes:front': at(eye_glow)})
    box('head', (-1, 5.5, -7), (2, 1, 1), mat=nose_mat, name='nose')
    box('head', (-3, 8.5, -4), (6, 3, 2), mat=throat_mat, name='throat')
    box('head', (-1, 9.6, -1), (2, 6, 2), mat=limb_mat, name='neck')
    box('head', (-3, 8.5, -5.4), (6, 2, 0), mat=teeth_mat(["gTTgTg", ".Tt.T."]), name='teeth')
    box('head', (-7, -0.5, -4), (14, 10, 10), mat=hair_shell, inflate=0.5, name='wig')
    box('head', (-6, -1.5, -4), (12, 1, 9), mat=hair_shell, inflate=0.35, name='crown_hair')
    # domed cranium: one more stepped layer of wig, centred on the parting (clear of the broken temple)
    box('head', (-5, -2.6, -2.5), (8, 1, 7), mat=hair_shell, inflate=0.3, name='dome')
    box('head', (-7.2, -1.9, -6.35), (8, 2, 0), mat=bangs_mat, name='bangs')
    # stray strands: one across the broken temple, one off the back
    box('head', (6.4, -0.8, -3.4), (0, 5, 1), mat=stray_mat, name='stray')
    box('head', (-2.5, 6.0, 6.6), (1, 6, 0), mat=stray_mat, name='stray')
    box('head', (-7.7, 3.0, 1.5), (0, 8, 1), mat=stray_mat, name='stray')
    box('head', (3.2, 5.0, 6.7), (1, 7, 0), mat=stray_mat, name='stray')

    bone('jaw', (0, 8.5, 1.0), parent='head', mat=chin_mat)
    box('jaw', (-3, 8.5, -6), (6, 2, 2), name='chin')
    box('jaw', (-2, 10.5, -6), (4, 1, 2), name='tip')
    box('jaw', (-3, 6.5, -5.4), (6, 2, 0), mat=teeth_mat([".t.T..", "gTgTTg"]), name='teeth')
    box('jaw', (-3, 6.5, -3.9), (6, 5, 1), mat=throat_mat, name='gullet', inflate=-0.1)

    # dusty bow pinned on the top-left of her hairline, in front of the fringe
    bone('bow', (-5.5, -1.9, -6.9), parent='head', rot=(0, 0, -3), mat=bow_mat)
    box('bow', (-6.5, -2.9, -7.4), (2, 2, 1), name='knot')
    box('bow', (-11.5, -3.9, -7.2), (5, 4, 1), name='loop', side='l')
    box('bow', (-4.5, -3.9, -7.2), (5, 4, 1), name='loop', side='r')
    box('bow', (-9.4, -1.6, -7.0), (2, 6, 0), name='tail')
    box('bow', (-11.0, -1.8, -6.8), (2, 5, 0), name='tail')

    # ringlets: 3 on her right, 2 on the broken left, 4 down the back (varied width, length, hang)
    curls = [('curl_r1', (-7.9, 1.6, -2.4), 2, 8, (0, 0, 6)), ('curl_r2', (-8.0, 1.2, 0.6), 3, 10, (6, 0, 4)),
             ('curl_r3', (-7.6, 1.8, 3.4), 2, 9, (12, 0, 3)),
             ('curl_l0', (8.6, 0.8, -3.0), 2, 6, (-4, 0, -10)),
             ('curl_l1', (7.9, 2.6, 0.2), 3, 7, (4, 0, -5)), ('curl_l2', (7.6, 1.4, 3.2), 2, 10, (10, 0, -3)),
             ('curl_b1', (-4.6, 3.0, 6.4), 3, 10, (14, 0, 5)), ('curl_b2', (-1.6, 3.6, 6.8), 2, 12, (11, 0, 1)),
             ('curl_b3', (1.4, 3.0, 6.7), 3, 11, (13, 0, -2)), ('curl_b4', (4.4, 3.8, 6.3), 2, 9, (16, 0, -6))]
    for name, (px, py, pz), wd, ln, rot in curls:
        bone(name, (px, py, pz), parent='head', rot=rot, mat=curl_mat)
        box(name, (px - wd / 2, py - 1, pz - wd / 2), (wd, ln, wd), name='coil')
        tw = max(1, wd - 1)
        box(name, (px - tw / 2, py - 1 + ln, pz - tw / 2), (tw, 2, tw), name='tip')

    # ---------------- the 1961 thread, cut: two loose ends hanging from the lips (look 'cortado').  Each is a root
    # strand + a lagging tip (double pendulum).  Rest rotations cancel the rolled head so they hang plumb.
    # thread_right leaves the upper needle hole at her right (child of head: it stays when the chin drops and hangs
    # across the open mouth); thread_left leaves the lower hole at her left (child of jaw: it drops with the chin).
    bone('thread_right', (-1.5, 7.0, -6.2), parent='head', rot=thread_rest_deg('thread_right'), mat=thread_mat)
    box('thread_right', (-2, 7.0, -6.7), (1, 5, 1), inflate=-0.22, name='thread')
    bone('thread_right_tip', (-1.5, 11.75, -6.2), parent='thread_right', rot=(-6, 0, 14), mat=thread_mat)
    box('thread_right_tip', (-2, 11.6, -6.7), (1, 4, 1), inflate=-0.26, name='thread_tip')
    bone('thread_left', (2.5, 10.0, -6.2), parent='jaw', rot=thread_rest_deg('thread_left'), mat=thread_mat)
    box('thread_left', (2, 10.0, -6.7), (1, 3, 1), inflate=-0.22, name='thread')
    bone('thread_left_tip', (2.5, 12.75, -6.2), parent='thread_left', rot=(8, 0, -18), mat=thread_mat)
    box('thread_left_tip', (2, 12.6, -6.7), (1, 3, 1), inflate=-0.26, name='thread_tip')

    # ---------------- fresh cross-stitches (look 'cosida'): one bone per stitch, its '+' plane turned 45 degrees
    # into an X centred on the lip seam at x -3, 0, 3; neighbours share their needle holes like a real row of
    # cross-stitch, the middle one a hair in front so the shared tips never z-fight
    bone('stitches', (0, 8.5, -6.2), parent='head', mat=stitch_mat)
    for k, (cx, z) in enumerate(((-3.0, -6.14), (0.0, -6.26), (3.0, -6.14))):
        bn = f'stitch_{k + 1}'
        bone(bn, (cx, 8.5, z), parent='stitches', rot=(0, 0, 45 if k != 1 else -45), mat=stitch_mat)
        box(bn, (cx - 2.5, 6.0, z), (5, 5, 0), name='xstitch')

    m = MunecaModel('muneca', 128, 128, r.roots)
    m.scale = 0.5
    m.visible = visible_set(variant)
    return m


_POSES = {
    # head rolled to 40 degrees in total, the intact right arm raised beside the head, reaching for the viewer
    'creep': {'head': (0.1, 0.1, 0.94, 0, 0, 0), 'jaw': (0.25, 0, 0, 0, 0.8, 0),
              'body': (0.08, 0, 0, 0, -0.05, 0), 'right_leg': (-0.08, 0, 0, 0, 0, 0),
              'left_leg': (-0.08, 0, 0, 0, 0, 0),
              'right_arm': (-1.85, 0.4, -0.2, 0, 0, 0), 'right_forearm': (-0.3, 0, 0, 0, 0, 0),
              'right_hand': (-0.45, 0, 0.2, 0, 0, 0), 'right_finger1': (-0.5, 0, 0.45, 0, 0, 0),
              'right_finger2': (-0.6, 0, 0.05, 0, 0, 0), 'right_finger3': (-0.5, 0, -0.4, 0, 0, 0),
              'left_arm': (0.12, 0, -0.1, 0, 0, 0),
              'thread_right_tip': (0, 0, -0.3, 0, 0, 0), 'thread_left_tip': (0, 0, -0.35, 0, 0, 0)},
    # lunge: jaw dropped, both arms flung out and forward at the viewer, the splayed hands wide beside the dropped
    # jaw and in front of the face plane (solved so no hand or finger enters the oversized head)
    'attack': {'body': (0.3, 0, 0, 0, 0.0, -1.0), 'right_leg': (-0.3, 0, 0, 0, 0, 0), 'left_leg': (-0.3, 0, 0, 0, 0, 0),
               'head': (-0.3, 0.12, 0.12, 0, 0, 0), 'jaw': (0.4, 0, 0, 0, 3.0, 0),
               'right_arm': (-0.91, -0.1, 1.23, 0, 0, 0), 'left_arm': (-2.39, 0.3, 1.01, 0, 0, 0),
               'right_forearm': (0.28, 0, 0.6, 0, 0, 0), 'left_forearm': (0.38, 0, 0.42, 0, 0, 0),
               'right_finger1': (0, 0, 0.5, 0, 0, 0), 'right_finger3': (0, 0, -0.5, 0, 0, 0),
               'left_finger1': (0.7, 0, 0.4, 0, 0, 0), 'left_finger3': (0.7, 0, -0.4, 0, 0, 0),
               'thread_right_tip': (0.35, 0, 0.25, 0, 0, 0), 'thread_left_tip': (0.4, 0, -0.3, 0, 0, 0)},
    # head thrown back, jaw fully dropped; the good arm straight up with the hand clawing beside her temple, the
    # broken one raised as far as its cord lets it, the hand dangling beside the jaw (no hand enters the head)
    'scream': {'head': (-0.5, 0, -0.22, 0, 0, 0), 'jaw': (0.55, 0, 0, 0, 1.3, 0),
               'right_arm': (-2.88, -0.02, -1.28, 0, 0, 0), 'left_arm': (-3.2, 0.33, 0.6, 0, 0, 0),
               'right_forearm': (0.23, 0, -0.15, 0, 0, 0), 'left_forearm': (0.54, 0, 0.82, 0, 0, 0),
               'right_finger1': (0, 0, 0.5, 0, 0, 0), 'right_finger3': (0, 0, -0.5, 0, 0, 0),
               'left_finger1': (0.7, 0, 0.4, 0, 0, 0), 'left_finger3': (0.7, 0, -0.4, 0, 0, 0)},
    # "just a doll", put down on a bed / chair seat / lap: bottom on the surface (the entity origin), a slight
    # slump, legs STRAIGHT out in a V (thigh sockets slid forward so shins and shoes clear the skirt, toes up), the
    # skirt fanned over the thighs and spread behind, the long arms limp with the hands palm-down on the surface,
    # the head lolling onto her right shoulder
    'sit': {'body': (0.07, 0, 0, 0, 3.6, 0),
            'right_leg': (-1.6, 0.3, 0, -0.3, 0.6, -3.3), 'left_leg': (-1.6, -0.24, 0, 0.3, 0.6, -3.3),
            'skirt_front': (-0.55, 0, 0, 0, 0, 0), 'skirt_front_right': (-0.45, 0, 0, 0, 0, 0),
            'skirt_front_left': (-0.45, 0, 0, 0, 0, 0), 'skirt_right': (-0.3, 0, 0, 0, 0, 0),
            'skirt_left': (-0.3, 0, 0, 0, 0, 0), 'skirt_back_right': (-0.35, 0, 0, 0, 0, 0),
            'skirt_back_left': (-0.35, 0, 0, 0, 0, 0), 'skirt_back': (-0.4, 0, 0, 0, 0, 0),
            'hem_front': (-0.3, 0, 0, 0, 0, 0), 'hem_front_right': (-0.25, 0, 0, 0, 0, 0),
            'hem_front_left': (-0.25, 0, 0, 0, 0, 0),
            'head': (0.1, 0.06, -0.32, 0, 0, 0),
            'right_arm': (-0.15, 0, 0.2, 0, 0, 0), 'left_arm': (-0.1, 0, -0.4, 0, 0, 0),
            'right_forearm': (0.1, 0, 0.25, 0, 0, 0), 'right_hand': (0, 0, 0.5, 0, 0, 0)},
}
# world-space swing of the two loose thread ends per pose (xRot, zRot; -x = lower end toward the viewer): the jaw
# snap of the attack flings them forward and apart across the black mouth; they are still swinging from the head
# snap of 'creep'; the plumb() entries keep them hanging under gravity otherwise
THREAD_SWAY = {
    'creep': {'thread_right': (-0.12, -0.32), 'thread_left': (-0.1, -0.26)},
    'attack': {'thread_right': (-0.5, 0.3), 'thread_left': (-0.65, -0.35)},
    'scream': {'thread_right': (0.1, 0.12), 'thread_left': (0.12, 0.08)},
}
POSES = {k: dict(v, **plumb(v, THREAD_SWAY.get(k))) for k, v in _POSES.items()}

ANIM_NOTES = """Ofelia (MunecaEntity, CURSED_DOLL) -- animation notes.  Units: radians, offsets in model texels
(2x density inside scale_root, so 2 texels = 1 vanilla pixel).  t = ageInTicks, s = walk speed 0..1; every pose is
ADDED to the rest pose.
Her rule: she moves ONLY while nobody looks at her (weeping angel; scripted relocations via UnseenSwap).  She is
porcelain: no breathing, no squash.  Head, jaw and arms move in stop-motion (quantise time to 2-3 tick steps,
tq = floor(t / 2) * 2); only hair, ribbons, cloth and the two loose threads move smoothly.  While a player looks straight
at her, freeze EVERY bone (cloth and threads included) on the current frame; resume when nobody looks.

Looks (VARIANT_MATS; Java picks the texture by the entity's variant index)
* 0 'cortado' -> muneca.png (+ muneca_eyes.png).  The whole case: the 1961 stitches Lucia cut.  Old faded red thread:
  a cut stub in two needle holes, one hole torn empty (the hairline crack from the socket ends in it), clean rosebud
  lips, and two loose ends hanging from the mouth (thread_right / thread_left visible, stitches hidden).
* 1 'cosida' -> muneca_cosida.png (+ muneca_cosida_eyes.png, same glow).  From the seal on (end of casa.puntadas, the
  shelf in transition 2, the bed in the post-credits): lips pressed into a dark seam, the porcelain dimpled toward the
  needle holes, three fresh scarlet cross-stitches standing proud of the face (stitches visible, both loose ends
  hidden).  Her mouth is SEWN in this look: never move the jaw (skip the idle clacks and the jaw values of
  'attack' / 'scream' / 'creep'); the stitches are children of head, not jaw, so an open jaw would leave them behind.

Toggles (ModelPart.visible).  Every frame: start from TOGGLE_DEFAULT, apply VARIANT_TOGGLES[look], then the minigame
state on top.  Hiding a parent hides its children.
* thread_right (child of head) + thread_right_tip   visible in 'cortado', hidden in 'cosida'.
* thread_left  (child of jaw)  + thread_left_tip    visible in 'cortado', hidden in 'cosida'.
* stitches (child of head)   hidden in 'cortado', visible in 'cosida'.  Holder of the three cross-stitches.
* stitch_1, stitch_2, stitch_3 (children of stitches; her right / centre / her left = viewer's left -> right)   visible
  by default, so 'cosida' shows all three.  Stitch minigame (casa.puntadas, Ofelia on the Nona's lap, texture still
  'cortado'): set stitches visible with stitch_1..3 hidden; when puntada k completes show stitch_k with a pop
  (xScale = yScale 1.35 -> 1 over 3 ticks).  After stitch_2 hide thread_left, after stitch_3 hide thread_right (the old
  ends are pulled through).  A failed puntada ("se suelta"): hide that stitch_k again on the same frame and jolt the
  head (zRot +0.25 for 2 ticks).  "Se cose sola": swap to 'cosida' (all three visible, loose ends hidden).

Bones
* body (root, pivot at the waist): whole doll.  Idle: perfectly still, a single 0.02 zRot "settle" jolt every 4-8 s.
  Chase: stiff toy waddle, zRot = sin(walk) * 0.12 * s toward the planted foot, dy = -abs(sin(walk)) * 0.4 (hop), no
  xRot sway.  Closing in (< 3 blocks): pitch forward 0.15.
* neck (ball joint on the collar): takes 30% of the head-look yaw/pitch (look(state, 0.3)).
* head: 70% of the head-look.  Rest pose is rolled 14 deg onto her right shoulder and turned 8 deg; keep it.  Idle: slow
  drift of +-0.05 then a SNAP of zRot +-0.3 in 2 ticks, hold 10-30 ticks, drift back.  Chase: head locked on the player
  (overshoot 0.1 and settle).  Pose 'creep' flops it 40 deg to the OTHER side - make that change in 2 ticks.
* jaw: marionette chin in two slots ('cortado' only).  Opens by sliding DOWN (dy) plus a small hinge (xRot) around the
  back of the skull.  Idle: closed; every 6-12 s a single dummy clack (dy 0.8 for 2 ticks).  Attack: pose value (0.4,
  dy 3) reached in 2 ticks, then 3 fast clacks.  Scream: hold (0.55, dy 1.3).  Never ease it - stepped only.  Locked
  closed in 'cosida'.
* thread_right (root strand, 5 long, from the upper needle hole at her right; child of head, so when the chin drops it
  hangs across the black mouth) and thread_left (4 long, from the lower hole at her left on the chin; child of jaw, so
  it drops with the chin): the cut loose ends of the 1961 thread.  GRAVITY every frame: set the root's rotation to the
  inverse of its parent's world rotation (the rest values (-2.0, 8.7, 13.6) deg already cancel the rest head roll;
  plumb() in this file is the reference maths) and ADD a swing: a damped pendulum (xRot, zRot) kicked by the parent's
  angular velocity and by body hops (impulse -k * dAngle, k ~ 0.8, damping 0.88 per tick, clamp +-0.7), plus an idle
  drift sin(t * 0.07 + phase) * 0.04.  The swing keeps going 2-3 s after a head snap or a jaw clack.
* thread_right_tip, thread_left_tip: the lower segments (4 and 3 long; the frayed ends).  Follow their root's swing
  with 2-3 ticks of lag and 1.5x the amplitude (double pendulum); rest curl (-6, 0, 14) / (8, 0, -18) deg.
* stitches, stitch_1..3: no motion (sewn into porcelain); only the toggle pops above.
* bow (hair bow on the top-left of the wig): secondary, spring-lagged zRot following head snaps (+-0.12), tiny flutter.
* curl_r1, curl_r2, curl_r3 (ringlets on her right), curl_l0, curl_l1, curl_l2 (on the broken left; curl_l0 is the short
  one hanging past the broken temple), curl_b1, curl_b2, curl_b3, curl_b4 (down the back): pendulums.  Each follows the head with 3-5
  tick lag: xRot/zRot += spring(head motion), amplitude 0.08-0.15, a different phase per curl
  (ripple("curl_", t, 0.12, 0.9, 0.06, 0.05, 0)).  Chase: +0.15 xRot bounce on footfall.
* skirt (core + torn petticoat): counter-yaw to the body in chase (yRot = -sin(walk) * 0.05).
* skirt_front, skirt_front_right, skirt_right, skirt_back_right, skirt_back, skirt_back_left, skirt_left,
  skirt_front_left: the 8 gathered upper tiers of the bell.  Tiny ripple idle (ripple("skirt_", t, 0.05, 0.8, 0.02,
  0.01, 0)), open on each step in chase (xRot -0.06 * s).  Fanned out in 'sit'.
* hem_front, hem_front_right, hem_right, hem_back_right, hem_back, hem_back_left, hem_left, hem_front_left (one child
  per upper tier): the flared, torn lower tiers.  Lag the upper tier by ~3 ticks and swing twice as far
  (ripple("hem_", t, 0.09, 0.8, 0.05, 0.03, -0.04 * s)); flare out on the attack lunge (xRot -0.2) and on landing a hop.
* right_leg, left_leg: stiff doll legs (no knee bend).  Chase: xRot = +-sin(walk) * 0.45 * s, alternating; the right
  foot stays turned in (rest yaw).  Idle: still.  'sit': straight out (see Poses).
* right_arm (intact) / left_arm (shoulder dropped 0.6 texel): idle hang, no natural swing.  Chase: arms stay stiff,
  jerk xRot -0.2 on each footfall; when closing in raise the right arm toward the player (blend into 'creep').
* right_forearm: elbow of the good arm, follows the pose values.
* left_forearm: the BROKEN forearm hanging off its stringing cord (visible gap + cord at the elbow).  Never driven
  directly: pendulum with lag and overshoot from the body/arm motion, amplitude up to 0.4 in chase, keeps swinging 2-3 s
  after she stops.  In 'attack' it flails outward.
* right_hand, left_hand: wrists.  Right: tiny tremor while idle (zRot 0.03).  Left: limp, swings with the forearm.
* right_finger1, right_finger2, right_finger3: spidery fingers of the good hand; idle twitch (one random finger xRot
  -0.3 for 3 ticks every 2-5 s); splay in 'creep' / 'attack' / 'scream' (pose values).
* left_finger1, left_finger2, left_finger3: the dead hand, curled; they only follow the swing.
* Emissive layer 'eyes' (muneca_eyes.png, same for both looks): dim iris + full-bright glint on the glass eye, a 2-px
  ember deep in the empty socket and the gloss on the black tear.  Optional: flicker the ember alpha in the renderer.

Poses (POSES; the thread_* entries are the plumb + swing of a frozen frame, computed by plumb(); Java may replace
them with the live gravity above)
* creep: the scare beat.  Head flops 40 deg to her left (net, opposite to her rest roll), jaw ajar (dy 0.8), the right
  arm rises toward the viewer with the wrist cocked and fingers splayed, left arm hangs; the loose threads still
  swinging from the snap.  Snap into it from 'sit' or idle in 1-2 ticks while the player is not looking, then freeze.
* attack: lunge.  Body pitches forward and slides 1 texel forward, legs counter-rotate so the shoes stay planted, head
  tilts up to show the face, the jaw drops (marionette, dy 3), both arms flung out and forward at the viewer so the
  splayed hands sit wide beside the dropped jaw, in front of the face plane (face, glass eye and open mouth stay
  unobstructed; no hand or finger enters the head -- keep it that way when blending); the jaw snap flings both loose
  threads forward and apart across the black mouth.  Hold 6 ticks, then clack.
* scream: head thrown back with extra roll, jaw dropped; the good right arm straight up with the hand clawing beside
  her temple, the broken left arm raised as far as its cord lets it, its hand dangling beside the jaw.
* sit: the dormant "just a doll" state and her warning: she sits next to whoever will be possessed next (on the roof of
  the doghouse, on Jorge's chair by the grill, on Lucia's pillow, on the Nona's lap) and on the shelf / bed in
  'cosida'.  Spawn the entity with its origin ON the seat surface (mattress / pillow top, chair seat, doghouse roof,
  top of the Nona's lap = the rocker seat height + lap): the skirt rests exactly on y = 24.  Slight slump (0.07), legs
  STRAIGHT out in a V (xRot -1.6, splay 0.3 / -0.24, thigh sockets slid 3.3 texels forward) so shins, socks and toes-up
  shoes clear the skirt; the skirt fanned over the thighs and spread behind; long limp arms with the hands
  palm-down on the surface beside her; head lolling onto her right shoulder but pitched only 0.1 forward, so a
  player standing over the bed / chair still meets the glass eye and the black socket (she is under 1 block tall and
  almost always seen from above; the soles of her shoes face you).  Footprint from the origin: legs reach
  0.31 block forward, the skirt 0.17 block back, the fingers 0.44 block to each side -> on a chair put the origin
  ~0.15 block behind the seat's front edge, facing out; on a lap face the same way as the Nona.  Only the head
  (look, unseen) and the cloth/threads (frozen while seen) animate in this pose.

Jumpscare portrait ("el ultimo giro hasta la cara"): FOCUS 'head', look 'cortado', pose 'attack' -- glass eye, ember
socket, black tear, the dropped jaw and the cut threads flung across the open mouth full frame.
"""
