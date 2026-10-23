"""Ofelia -- the cursed antique porcelain doll, anchor of CASO 2 'Casa Morales' (DEAD LINE).

Authored at 2x texel density (model.scale = 0.5).  +Y down, ground y = 24, faces -Z, right_* on -X.

Story beat she carries: in 1961 Padre Anselmo shut the demon AZAMEL inside her by sewing her mouth shut with
blessed red thread: three cross-stitches over the lip seam.  Lucia (8) snipped them, so she arrives with the mouth
CUT ('cortado', the default look): two loose ends of the old brick-red thread hang from her lips and sway (bones
thread_right / thread_left, two segments each, a pale frayed tuft at each cut end) and three short snipped stubs
stand in the needle holes (bone thread_stubs).  In the finale the Nona sews it shut again with FRESH scarlet thread
through the SAME holes: look 'cosida' = three solid cross-stitches standing proud of the face (toggle bones
stitch_1..3 under 'stitches', shown one by one in the stitch minigame) over lips pressed into a seam; the loose ends
and the stubs are hidden.  Both looks share one hole layout, so 'cortado' reads as 'sewn, then snipped' and 'cosida'
as the same X rhythm closed again.

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

Face (the jumpscare portrait), front of a 2-texel porcelain mask so every break has real depth.  Few, grouped
darks: the glass eye, the socket and the tear are the only big ones.
* her right eye (viewer's left) is a glossy blue glass eye recessed behind the mask, dilated pupil,
  one glint, a painted lid line, two slanted lash strokes at the outer corner and two below;
* her left eye is gone: a round black socket with a soft rim and a dying 2-px ember deep inside; a glossy
  black tear runs from it over clean porcelain and drips off the jaw;
* the top corner of her left temple is broken away (a real notch through mask, wig and crown, dark
  inside) and one hairline crack runs from it into the socket and on (fading to grey) to a torn needle hole;
* a small rosebud mouth under a blush-tipped button nose (its shadow painted under it); the needle holes of
  the three X's sit above (y 7) and below (y 10) the lips at x -4.5 / -1.5 / 1.5 / 4.5;
* the chin is a marionette jaw in two slots: it drops straight down (and hinges a little) to show a
  black throat (one clean void) with uneven bisque teeth top and bottom, one missing.
A dusty red bow (loops with real depth) is pinned on the top-left of her hairline, its notched tails hanging over the
ringlets.  The wig top, what players see most, is clean: a 1-px side parting, strands combed off it in a chevron,
one bright satin ring round the crown.
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
LIP = pal('#4e1426', '#7e2440', '#a83a58', '#c95a74')   # faded rose doll paint: the orange-red thread pops off it
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
# the 1961 blessed thread: sixty years in a biscuit tin, but still the brightest thing on her -- an orange-shifted
# brick red that separates from the burgundy dress in value AND hue (mid #c23a30, top #e8604a, pale ply #f39a7a)
OLDT = pal('#2a0708', '#5e1512', '#8f261f', '#c23a30', '#e8604a', '#f39a7a')
FRAY = pal('#e07a62', '#f39a7a')                      # the cut end splits into pale fibres
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
    "eoeooooooochXX",   # r1  lash tips | the crack leaves the chunk, chipped lip of the break
    "ololooooocoohh",   # r2  two slanted lash strokes at the outer corner | crack runs to the socket | chipped edge
    "oWWWWWoos..soo",   # r3  lid line over the glass eye | round socket
    "s.....os....so",   # r4  glass eye (eyeball behind) | socket (ember deep inside)
    "s.....os....so",   # r5
    "o.....oos..soo",   # r6
    "oeoeooooCookoo",   # r7  two lower lashes | the crack leaves the socket (mid grey) | the tear leaves it
]
# The mouth, per look.  Plate rows r8 (above the lip) and r9 (upper lip) are 14 wide (x -7..7); the chin rows c10
# (lower lip) and c11 (needle holes) are 6 wide (x -3..3, face columns 4..9); 'tip' is the chin tip (columns 5..8).
# Both looks share ONE row of needle holes: the 1961 cross-stitches and the Nona's new ones go through the same
# punctures, at x -4.5, -1.5, 1.5, 4.5 (columns 2, 5, 8, 11) above the lip (y 7) and below it (y 10), three X's
# centred on the lip seam at x -3, 0, 3.  So 'cortado' and 'cosida' rhyme: the same X rhythm, snipped / sewn.
MOUTH_ROWS = {
    'cortado': {
        # Lucia snipped every stitch at the lip seam.  r8: col 2 = cut stub (geometry, thread_stubs) | col 5 =
        # thread_right leaves this hole | 6-7 shadow under the nose | col 8 = torn empty (the crack ends in it) |
        # col 11 = the black tear runs over the last hole
        'r8': "pPuooHssuookpp",
        'r9': "ppooMLRRLMogPp",   # rosebud upper lip (shadowed) with dark corners
        'c10': "sRQQRs",          # fuller lower lip catching the light
        'c11': "oTooHo",          # holes: a short cut stub left in col 5 | col 8: thread_left leaves this hole
        'tip': "soos",
    },
    'cosida': {
        # three fresh cross-stitches (geometry, stitch_1..3) cross the seam at x -3, 0, 3 through the same holes.
        # Under them the lips are pulled into a tight seam and the porcelain puckers toward the holes.
        'r8': "pPuzoussuzokpp",
        'r9': "ppozMLRRLMogPp",
        'c10': "ziiiiz",
        'c11': "zuoouz",
        'tip': "soos",
    },
}
# Lower face 12 x 2 (x -6..6, y 8.5..10.5); the chin slot (x -3..3) is open.  Column 1 of the lower row is the
# hole at x -4.5 (a cut stub in 'cortado'), column 10 the tear.
FACE_B = {
    'cortado': ["pps......skp", "sus......oks"],
    'cosida': ["pzs......skp", "suz......zks"],
}
FACE_COLS = {
    'h': CHIP, 'c': CRACK_D, 'l': LASH[0], 'e': LASH[1], 'W': LASH[0],
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


def nose_mat(ctx):
    """A tiny button nose: a warm blush on the tip so it separates from the white mask, a soft rose underside (no
    grey grime: under horror lighting that read as a lavender bar).  The plate paints its cast shadow below it."""
    f = ctx.face
    if f == 'back':
        return None
    if f == 'bottom':
        return mix(PORC[4], ROUGE[0], 0.35)
    if f == 'top':
        return PORC[7]
    if f == 'front':
        return mix(PORC[6], ROUGE[1], 0.45 if ctx.i == 1 else 0.3)
    return mix(PORC[5], ROUGE[1], 0.2)


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
    # the throat's underside and walls show inside the dropped jaw: part of the same black void as the gullet
    return MOUTH[1] if f in ('bottom', 'west', 'east') else MOUTH[0]


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
    """Top of the wig, the surface players see most (she is under 1 block tall and usually seen from above).  Clean,
    readable shapes instead of noise: a crisp 1-px parting from the fringe to the crown; on each side the strands are
    combed away from it in 3 tone bands (a dark gap, a lit strand, the mid tone) that slant back, so the two sides
    meet in a chevron at the parting; one continuous 2-tone satin 'angel ring' round the crown; the rim darkens
    where the head rounds over."""
    d = x - PART_X
    ad = abs(d)
    if z < WHORL_Z + 0.5 and ad < 0.5:
        return 0.14                                   # the parting
    u = z - ad * 0.5 + (0.0 if d < 0 else 2.0)
    gap = u % 4.0 < 1.0 and ad > 1.5                  # (no gap touches the parting: no stray cross shapes)
    v = 0.34 if gap else 0.47                         # strand gaps every 4 texels, slanting back off the parting
    if ad < 1.5 and z < WHORL_Z + 0.5:
        v -= 0.07                                     # hair lifting off the parting, in its shadow
    r = math.sqrt((x / 1.4) ** 2 + (z - 1.0) ** 2)    # elliptical ring round the crown (centred on the head)
    if 3.4 <= r < 4.4:
        v = 0.78                                      # the satin ring: one bright continuous arc...
    elif 4.4 <= r < 5.4:
        v = 0.64 if not gap else 0.55                 # ...with a softer tone on its outer edge
    if edge(ctx) == 0 and tag(ctx) == 'wig':
        v -= 0.08                                     # rounds over at the outer rim (the stepped layers above it
    return v                                          # keep clean edges: an outline there reads as a box)


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
    """The 1961 thread, a full texel thick: a two-ply twist (light / mid texels stepping round the strand) with a
    pale ply highlight now and then, a little darker down the strand; the cut end of each tip is pale and frayed
    and splits into fibres (the 'fray' planes).  Stubs (thread_stubs) are the same twist, the end in the hole dark."""
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    t = tag(ctx)
    if t == 'fray':
        if f != 'front':
            return None                                 # one face only (planes are drawn double-sided)
        ch = FRAY_ROWS[ctx.j][ctx.i]
        return None if ch == '.' else FRAY[0] if ch == 'f' else FRAY[1]
    if t == 'stub':
        if f == 'back':
            return None
        L = max(w, h)
        u = (lx / w) if w > h else (ly / h)             # 0 = the end in the needle hole
        if f == 'front':
            if ctx.cube.flip:
                u = 1 - u
            return OLDT[1] if u < 0.5 else OLDT[5]      # dark where it dives into the hole, pale cut end
        return OLDT[3] if f in ('top', 'west') else OLDT[2]
    tip = t == 'thread_tip'
    if f == 'top':
        return OLDT[2]
    if f == 'bottom':
        return FRAY[0] if tip else OLDT[2]
    k = {'front': 0, 'east': 1, 'back': 2, 'west': 3}[f]
    last = tip and ctx.j == ctx.h - 1
    if last:
        return FRAY[1] if f in ('front', 'west') else FRAY[0]   # the pale frayed end
    if f in ('front', 'west'):
        c = OLDT[4] if (ctx.j + k) % 2 == 0 else OLDT[3]     # the lit plies
        if (ctx.j + k + cseed(ctx)) % 5 == 0:
            c = OLDT[5]                                      # 1-px pale ply highlight
    else:
        c = OLDT[3] if (ctx.j + k) % 2 == 0 else OLDT[2]
    return c


FRAY_ROWS = [
    # 3 x 1 under the cut end: the two plies split apart into pale fibres
    "f.f",
]


# fresh cross-stitch (look 'cosida'): each stitch is a '+' of two thin solid strands that its bone turns 45 degrees
# into an X, so both threads are clean straight lines at any distance (painted diagonals on a rotated plane read as a
# chain of diamonds in close-ups).  The 'over' strand ('/', lit, a hot highlight on the crossing) lies in front of the
# 'under' strand ('\'); both ends darken where they dive into the shared needle holes.
def stitch_mat(ctx):
    f = ctx.face
    if f == 'back':
        return None
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    u = (lx / w) if w > h else (ly / h)
    end = u < 0.2 or u > 0.8
    if tag(ctx) == 'over':
        if f == 'front':
            return NEWT[2] if end else (NEWT[5] if 0.4 < u < 0.6 else NEWT[4])
        return NEWT[2] if end else NEWT[3]
    if f == 'front':
        return NEWT[1] if end else NEWT[3]
    return NEWT[1] if end else NEWT[2]


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
TOGGLE_DEFAULT = {'thread_right': True, 'thread_left': True, 'thread_stubs': True, 'stitches': False,
                  'stitch_1': True, 'stitch_2': True, 'stitch_3': True}
VARIANT_TOGGLES = {
    'cortado': {},
    'cosida': {'thread_right': False, 'thread_left': False, 'thread_stubs': False, 'stitches': True},
}
# her mouth is sewn in these looks: Java must never move the jaw there (idle clacks and the jaw values of every pose
# are dropped), because the cross-stitches are children of head and an open jaw would leave them floating
JAW_LOCKED_VARIANTS = ('cosida',)
VARIANT_POSE_MASK = {'cosida': ('jaw',)}             # bones whose pose values Java skips in that look


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
                        'variants': {k: dict(v) for k, v in VARIANT_TOGGLES.items()}, 'poses': {},
                        'jaw_locked': list(JAW_LOCKED_VARIANTS),
                        'pose_mask': {k: list(v) for k, v in VARIANT_POSE_MASK.items()}}
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
TIP_REST = {'thread_right_tip': (-6, 0, 10), 'thread_left_tip': (6, 0, 12)}      # degrees: a slight curl


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
        bone(ab, (ax, ay, 0), parent='body', rot=((3, 0, -18) if broken else (-4, 0, 19)), mat=limb_mat)
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
    box('bow', (-11.5, -3.9, -7.4), (5, 4, 2), name='loop', side='l')
    box('bow', (-4.5, -3.9, -7.4), (5, 4, 2), name='loop', side='r')
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

    # ---------------- needle holes and stitches: ONE layout for both looks.  Three X's centred on the lip seam
    # (y 8.5) at x -3, 0, 3; each arm reaches 1.7 along both axes, so the corner holes sit at x -4.5/-1.5/1.5/4.5,
    # y ~6.8 (above the upper lip) and ~10.2 (on the chin), shared by neighbours like a real row of cross-stitch.
    seam = 8.5
    rz = rot_matrix(0, 0, math.radians(45))

    def diag_box(bn, pivot, centre, size, z0, mat, name, inflate):
        """A cube of a bone turned +45 deg about Z, placed so its centre lands on `centre` (head space)."""
        lc = rz.T @ np.array([centre[0] - pivot[0], centre[1] - pivot[1], 0.0])
        c = box(bn, (pivot[0] + lc[0] - size[0] / 2, pivot[1] + lc[1] - size[1] / 2, z0), size, mat=mat,
                inflate=inflate, name=name)
        return c

    # ---------------- the 1961 thread, cut (look 'cortado').  Lucia snipped the three X's at the seam: two loose
    # ends hang from shared holes and sway, short stubs stay in three others.  Each end is a full-texel strand: a root
    # + a lagging tip (double pendulum) ending in a pale frayed tuft over the light lace collar / jabot.  Rest
    # rotations cancel the rolled head so they hang plumb.  thread_right leaves the upper hole at x -1.5 (child of
    # head: it stays when the chin drops and hangs across the open mouth); thread_left leaves the lower hole at x 1.5
    # on the chin (child of jaw: it drops with the chin).
    tz = -6.55                                          # strand centre: its back face just clears the porcelain
    bone('thread_right', (-1.5, 6.9, tz), parent='head', rot=thread_rest_deg('thread_right'), mat=thread_mat)
    box('thread_right', (-2, 6.9, tz - 0.5), (1, 3, 1), inflate=-0.03, name='thread')
    bone('thread_right_tip', (-1.5, 9.85, tz), parent='thread_right', rot=TIP_REST['thread_right_tip'], mat=thread_mat)
    box('thread_right_tip', (-2, 9.8, tz - 0.5), (1, 2, 1), inflate=-0.03, name='thread_tip')
    box('thread_right_tip', (-2.5, 11.75, tz), (3, 1, 0), name='fray')
    bone('thread_left', (1.5, 10.2, tz), parent='jaw', rot=thread_rest_deg('thread_left'), mat=thread_mat)
    box('thread_left', (1, 10.2, tz - 0.5), (1, 2, 1), inflate=-0.03, name='thread')
    bone('thread_left_tip', (1.5, 12.15, tz), parent='thread_left', rot=TIP_REST['thread_left_tip'], mat=thread_mat)
    box('thread_left_tip', (1, 12.1, tz - 0.5), (1, 1, 1), inflate=-0.03, name='thread_tip')
    box('thread_left_tip', (0.5, 13.05, tz), (3, 1, 0), name='fray')
    # cut stubs (child of head, turned 45 deg like the X arms): the outer halves of the first and last X survive as
    # short snipped strands, 1.8 long and as thick as the new stitches, each from its hole toward the X's centre:
    # a '>' at her right lip corner and a '<' at her left one bracket the mouth; the middle of the row was cut out and
    # hangs (thread_right, thread_left) or tore (the hole the crack ends in)
    bone('thread_stubs', (0, seam, tz), parent='head', rot=(0, 0, 45), mat=thread_mat)
    for hole, xc in (((-4.5, 6.85), -3.0), ((-4.5, 10.15), -3.0), ((4.5, 6.85), 3.0), ((4.5, 10.15), 3.0)):
        d = np.array([xc - hole[0], seam - hole[1]])
        d /= np.linalg.norm(d)
        axis = 'x' if d[0] * d[1] > 0 else 'y'          # local x = the '\' diagonal, local y = the '/' one
        centre = (hole[0] + d[0] * 0.8, hole[1] + d[1] * 0.8)
        c = diag_box('thread_stubs', (0, seam, tz), centre, (2, 1, 2) if axis == 'x' else (1, 2, 2), -6.5,
                     thread_mat, 'stub', -0.12)
        # 'flip' when the hole end is the far end of the strand's local axis (front face texel order)
        loc_dir = rz.T @ np.array([d[0], d[1], 0.0])
        c.flip = (loc_dir[0] if axis == 'x' else loc_dir[1]) < 0

    # ---------------- fresh cross-stitches (look 'cosida'): one bone per stitch, turned 45 deg; its '+' of two
    # solid strands becomes the X.  'over' ('/', lit) in front of 'under' ('\'), both sunk into the porcelain at
    # the holes; neighbours share their holes.
    bone('stitches', (0, seam, -6.2), parent='head', mat=stitch_mat)
    for k, cx in enumerate((-3.0, 0.0, 3.0)):
        bn = f'stitch_{k + 1}'
        bone(bn, (cx, seam, -6.2), parent='stitches', rot=(0, 0, 45), mat=stitch_mat)
        box(bn, (cx - 0.5, seam - 2.5, -6.8), (1, 5, 1), inflate=-0.1, name='over')
        box(bn, (cx - 2.5, seam - 0.5, -6.5), (5, 1, 1), inflate=-0.1, name='under')

    m = MunecaModel('muneca', 128, 128, r.roots)
    m.scale = 0.5
    m.visible = visible_set(variant)
    return m


_POSES = {
    # the scare beat, played as a joke: her head flops ~33 deg onto her LEFT shoulder (resting on the puff sleeve,
    # not swallowing it; that shoulder sags 1 texel), the jaw ajar, and the good right hand pops up beside the empty
    # side of her head in a stiff little wave -- palm to camera, fingers splayed, wrist cocked -- clear of the wig
    'creep': {'head': (0.2, 0.15, 0.82, 0, 0, 0), 'jaw': (0.25, 0, 0, 0, 0.8, 0),
              'body': (0.08, 0, 0, 0, -0.05, 0), 'right_leg': (-0.08, 0, 0, 0, 0, 0),
              'left_leg': (-0.08, 0, 0, 0, 0, 0),
              'right_arm': (-2.26, -0.22, -1.09, -0.75, -1.5, 0), 'right_forearm': (0.13, 0, 0.27, 0, 0, 0),
              'right_hand': (0.19, 0, -0.31, 0, 0, 0), 'right_finger1': (-0.5, 0, 0.45, 0, 0, 0),
              'right_finger2': (-0.6, 0, 0.05, 0, 0, 0), 'right_finger3': (-0.5, 0, -0.4, 0, 0, 0),
              'left_arm': (0.13, -0.08, 0.0, 1.16, 1.0, 0), 'left_forearm': (-0.38, 0, -0.1, 0, 0, 0),
              'thread_right_tip': (0, 0, -0.3, 0, 0, 0), 'thread_left_tip': (-0.2, 0, -0.35, 0, 0, 0)},
    # lunge: jaw dropped, both arms flung out and forward at the viewer, the splayed hands wide beside the dropped
    # jaw and in front of the face plane (solved so no hand or finger enters the oversized head)
    'attack': {'body': (0.3, 0, 0, 0, 0.0, -1.0), 'right_leg': (-0.3, 0, 0, 0, 0, 0), 'left_leg': (-0.3, 0, 0, 0, 0, 0),
               'head': (-0.3, 0.12, 0.12, 0, 0, 0), 'jaw': (0.4, 0, 0, 0, 3.0, 0),
               'right_arm': (-0.91, -0.1, 1.23, -0.8, 0.3, 0), 'left_arm': (-2.39, 0.3, 1.01, 0, 0, 0),
               'right_forearm': (0.28, 0, 0.6, 0, 0, 0), 'left_forearm': (0.38, 0, 0.42, 0, 0, 0),
               'right_finger1': (0, 0, 0.5, 0, 0, 0), 'right_finger3': (0, 0, -0.5, 0, 0, 0),
               'left_finger1': (0.7, 0, 0.4, 0, 0, 0), 'left_finger3': (0.7, 0, -0.4, 0, 0, 0),
               'thread_right_tip': (0.35, 0, 0.25, 0, 0, 0), 'thread_left_tip': (0.4, 0, -0.3, 0, 0, 0)},
    # head thrown back and rolled AWAY from the good arm, jaw fully dropped; both hands flung up beside her face: the
    # good right arm raised high and wide (shoulder hitched up), its splayed claw beside her cheek and temple, clear
    # of wig and ringlets; the broken left arm yanked up on its cord, the dead hand dangling beside the jaw.  Solved
    # against head, curls, skirt and body: no arm, hand or finger enters them.
    'scream': {'head': (-0.5, 0.1, 0.28, 0, 0, 0), 'jaw': (0.55, 0, 0, 0, 1.3, 0),
               'right_arm': (-2.27, -0.56, -1.54, -1.14, -0.9, 0), 'right_forearm': (-0.05, 0, -0.33, 0, 0, 0),
               'right_hand': (-0.04, 0, -0.27, 0, 0, 0),
               'left_arm': (-2.36, 0.75, 1.67, 0.19, -0.36, 0), 'left_forearm': (-0.46, 0, -0.53, 0, 0, 0),
               'left_hand': (0.68, 0, 0.25, 0, 0, 0),
               'right_finger1': (0, 0, 0.5, 0, 0, 0), 'right_finger3': (0, 0, -0.5, 0, 0, 0),
               'left_finger1': (0.7, 0, 0.4, 0, 0, 0), 'left_finger3': (0.7, 0, -0.4, 0, 0, 0)},
    # "just a doll", propped up on a bed / chair seat / lap: bottom on the surface (the entity origin), the torso
    # leaning BACK a little (so the face tips up toward a player standing over her), legs STRAIGHT out in a V along
    # the surface (thigh sockets slid 5.8 forward, under the skirt's front edge), heels down, toes up and out; the
    # skirt fanned round her; the long arms down at her sides, hands resting palm-down on the surface beside the
    # thighs (the broken forearm folded in on its cord); the head keeps its rest loll onto her right shoulder
    'sit': {'body': (-0.2, 0, 0, 0, 3.0, 0),
            'right_leg': (-1.37, 0.25, 0, -0.3, 2.9, -5.8), 'left_leg': (-1.37, -0.2, 0, 0.3, 2.9, -5.8),
            'skirt_front': (-0.3, 0, 0, 0, 0, 0), 'skirt_front_right': (-0.05, 0, 0, 0, 0, 0),
            'skirt_front_left': (-0.05, 0, 0, 0, 0, 0), 'skirt_right': (-0.2, 0, 0, 0, 0, 0),
            'skirt_left': (-0.2, 0, 0, 0, 0, 0), 'skirt_back_right': (-0.4, 0, 0, 0, 0, 0),
            'skirt_back_left': (-0.4, 0, 0, 0, 0, 0), 'skirt_back': (-0.45, 0, 0, 0, 0, 0),
            'hem_front': (-0.1, 0, 0, 0, 0, 0), 'hem_front_right': (0.15, 0, 0, 0, 0, 0),
            'hem_front_left': (0.15, 0, 0, 0, 0, 0),
            'head': (0.15, 0.06, 0.0, 0, 0, 0),
            'right_arm': (-0.49, -0.07, 0.25, -0.6, 0.3, 0), 'right_forearm': (0.2, 0, -0.27, 0, 0, 0),
            'right_hand': (-0.24, 0, -0.46, 0, 0, 0),
            'left_arm': (-0.31, 0.08, -0.37, 0, 0, 0), 'left_forearm': (-0.12, 0, 1.08, 0, 0, 0),
            'left_hand': (-0.13, 0, -0.26, 0, 0, 0)},
}
# world-space swing of the two loose thread ends per pose (xRot, zRot; -x = lower end toward the viewer): the jaw
# snap of the attack flings them forward and apart across the black mouth; they are still swinging from the head
# snap of 'creep'; the plumb() entries keep them hanging under gravity otherwise
THREAD_SWAY = {
    'creep': {'thread_right': (-0.15, -0.3), 'thread_left': (-0.6, -0.15)},
    'attack': {'thread_right': (-0.5, 0.3), 'thread_left': (-0.65, -0.35)},
    'scream': {'thread_right': (-0.55, 0.1), 'thread_left': (-0.15, 0.1)},
    'sit': {'thread_right': (-0.15, 0.08), 'thread_left': (-0.12, -0.08)},
}
POSES = {k: dict(v, **plumb(v, THREAD_SWAY.get(k))) for k, v in _POSES.items()}

ANIM_NOTES = """Ofelia (MunecaEntity, CURSED_DOLL) -- animation notes.  Units: radians, offsets in model texels
(2x density inside scale_root, so 2 texels = 1 vanilla pixel, 32 texels = 1 block).  t = ageInTicks, s = walk speed
0..1; every pose is ADDED to the rest pose.
Her rule: she moves ONLY while nobody looks at her (weeping angel; scripted relocations via UnseenSwap).  She is
porcelain: no breathing, no squash.  Head, jaw and arms move in stop-motion (quantise time to 2-3 tick steps,
tq = floor(t / 2) * 2); only hair, ribbons, cloth and the two loose threads move smoothly.  While a player looks straight
at her, freeze EVERY bone (cloth and threads included) on the current frame; resume when nobody looks.

Looks (VARIANT_MATS; Java picks the texture by the entity's variant index)
* 0 'cortado' -> muneca.png (+ muneca_eyes.png).  The whole case: the 1961 stitches Lucia snipped.  Brick-red old
  thread, a full texel thick, brighter and more orange than the burgundy dress: two loose ends hang from the lips
  (thread_right, thread_left) ending in pale frayed tufts over the lace collar / jabot, three snipped stubs stand in
  the needle holes (thread_stubs: two make a '>' at her right lip corner, one hangs over the black tear), one hole is
  torn empty where the crack from the socket ends, clean rosebud lips.  Visible: thread_right, thread_left,
  thread_stubs.  Hidden: stitches.
* 1 'cosida' -> muneca_cosida.png (+ muneca_cosida_eyes.png, same glow).  From the seal on (end of casa.puntadas, the
  shelf in transition 2, the bed in the post-credits): lips pressed into a dark seam, the porcelain dimpled toward the
  needle holes, three fresh scarlet cross-stitches through the same holes, standing proud of the face.  Visible:
  stitches (+ stitch_1..3).  Hidden: thread_right, thread_left, thread_stubs.
* JAW LOCK (data: JAW_LOCKED_VARIANTS = ('cosida',), VARIANT_POSE_MASK = {'cosida': ('jaw',)}): her mouth is SEWN
  in 'cosida'.  Never move the jaw there: skip the idle clacks and drop the 'jaw' entry of EVERY pose ('attack',
  'scream', 'creep'), because the stitches are children of head, not jaw, and an open jaw would leave them floating
  in front of a black mouth.

Toggles (ModelPart.visible).  Every frame: start from TOGGLE_DEFAULT, apply VARIANT_TOGGLES[look], then the minigame
state on top.  Hiding a parent hides its children.
* thread_right (child of head) + thread_right_tip   visible in 'cortado', hidden in 'cosida'.
* thread_left  (child of jaw)  + thread_left_tip    visible in 'cortado', hidden in 'cosida'.
* thread_stubs (child of head; the three snipped stubs)   visible in 'cortado', hidden in 'cosida'.
* stitches (child of head)   hidden in 'cortado', visible in 'cosida'.  Holder of the three cross-stitches.
* stitch_1, stitch_2, stitch_3 (children of stitches; her right / centre / her left = viewer's left -> right)   visible
  by default, so 'cosida' shows all three.  Stitch minigame (casa.puntadas, Ofelia on the Nona's lap, texture still
  'cortado', jaw already locked): set stitches visible with stitch_1..3 hidden; when puntada k completes show stitch_k
  with a pop (xScale = yScale 1.35 -> 1 over 3 ticks).  After stitch_1 hide thread_stubs (the Nona pulls the old
  stubs out of the holes she reuses), after stitch_2 hide thread_left, after stitch_3 hide thread_right.  A failed
  puntada ("se suelta"): hide that stitch_k again on the same frame and jolt the head (zRot +0.25 for 2 ticks).
  "Se cose sola": swap to 'cosida' (all three visible, loose ends and stubs hidden).

Bones
* body (root, pivot at the waist): whole doll.  Idle: perfectly still, a single 0.02 zRot "settle" jolt every 4-8 s.
  Chase: stiff toy waddle, zRot = sin(walk) * 0.12 * s toward the planted foot, dy = -abs(sin(walk)) * 0.4 (hop), no
  xRot sway.  Closing in (< 3 blocks): pitch forward 0.15.
* neck (ball joint on the collar): takes 30% of the head-look yaw/pitch (look(state, 0.3)).
* head: 70% of the head-look.  Rest pose is rolled 14 deg onto her right shoulder and turned 8 deg; keep it.  Idle: slow
  drift of +-0.05 then a SNAP of zRot +-0.3 in 2 ticks, hold 10-30 ticks, drift back.  Chase: head locked on the player
  (overshoot 0.1 and settle).  Pose 'creep' flops it ~33 deg to the OTHER side - make that change in 2 ticks.
* jaw: marionette chin in two slots ('cortado' only).  Opens by sliding DOWN (dy) plus a small hinge (xRot) around the
  back of the skull.  Idle: closed; every 6-12 s a single dummy clack (dy 0.8 for 2 ticks).  Attack: pose value (0.4,
  dy 3) reached in 2 ticks, then 3 fast clacks.  Scream: hold (0.55, dy 1.3).  Never ease it - stepped only.  Locked
  closed in 'cosida' (see JAW LOCK).
* thread_right (root strand, 3 long, from the upper needle hole at x -1.5; child of head, so when the chin drops it
  hangs across the black mouth) and thread_left (root strand, 2 long, from the lower hole at x 1.5 on the chin; child
  of jaw, so it drops with the chin): the cut loose ends of the 1961 thread, a full texel thick.  GRAVITY every frame:
  set the root's rotation to the inverse of its parent's world rotation (the rest values (-2.0, 8.7, 13.6) deg already
  cancel the rest head roll; plumb() in this file is the reference maths) and ADD a swing: a damped pendulum (xRot,
  zRot, world space; -xRot = lower end toward her front) kicked by the parent's angular velocity and by body hops
  (impulse -k * dAngle, k ~ 0.8, damping 0.88 per tick, clamp +-0.7), plus an idle drift sin(t * 0.07 + phase) * 0.04.
  The swing keeps going 2-3 s after a head snap or a jaw clack.
  COLLISION CLAMP (no live collision in MC): the strands must never pass into the face, chin, legs or skirt.  After
  adding the swing, clamp the world xRot of each root to at most  fwd = -max(0, -headPitchWorld) * 1.1  (i.e. when the
  head is thrown back by p rad, the strand is kicked forward by at least 1.1 * p so it drapes over the chin; scream
  needs -0.55 for thread_right), and in 'creep' (head flopped onto the skirt side) keep thread_left at <= -0.6.  The
  frozen THREAD_SWAY values per pose below are verified clean (point-in-cube check against head, jaw, legs, skirt,
  body and arms in rest, sit, creep, attack and scream).
* thread_right_tip, thread_left_tip: the lower segments (2 and 1 long, each ending in a 3x1 frayed 'fray' plane: the
  pale cut end).  Follow their root's swing with 2-3 ticks of lag and 1.5x the amplitude (double pendulum); rest curl
  (-6, 0, 10) / (6, 0, 12) deg.  At rest the tufts end over the lace collar / jabot (y ~13.7 / ~14.3).
* thread_stubs (child of head, rest zRot 45 deg so its three 1.6-long stubs lie along the diagonals of the old X's):
  no motion; toggle only.
* stitches, stitch_1..3 (each stitch bone turned 45 deg holds a '+' of two solid strands = the X; 'over' in front):
  no motion (sewn into porcelain); only the toggle pops above.
* bow (hair bow on the top-left of the wig): secondary, spring-lagged zRot following head snaps (+-0.12), tiny flutter.
* curl_r1, curl_r2, curl_r3 (ringlets on her right), curl_l0, curl_l1, curl_l2 (on the broken left; curl_l0 is the short
  one hanging past the broken temple), curl_b1, curl_b2, curl_b3, curl_b4 (down the back): pendulums.  Each follows the
  head with 3-5 tick lag: xRot/zRot += spring(head motion), amplitude 0.08-0.15, a different phase per curl
  (ripple("curl_", t, 0.12, 0.9, 0.06, 0.05, 0)).  Chase: +0.15 xRot bounce on footfall.
* skirt (core + torn petticoat): counter-yaw to the body in chase (yRot = -sin(walk) * 0.05).
* skirt_front, skirt_front_right, skirt_right, skirt_back_right, skirt_back, skirt_back_left, skirt_left,
  skirt_front_left: the 8 gathered upper tiers of the bell.  Tiny ripple idle (ripple("skirt_", t, 0.05, 0.8, 0.02,
  0.01, 0)), open on each step in chase (xRot -0.06 * s).  Fanned out in 'sit'.
* hem_front, hem_front_right, hem_right, hem_back_right, hem_back, hem_back_left, hem_left, hem_front_left (one child
  per upper tier): the flared, torn lower tiers.  Lag the upper tier by ~3 ticks and swing twice as far
  (ripple("hem_", t, 0.09, 0.8, 0.05, 0.03, -0.04 * s)); flare out on the attack lunge (xRot -0.2) and on landing a hop.
* right_leg, left_leg: stiff doll legs (no knee bend).  Chase: xRot = +-sin(walk) * 0.45 * s, alternating; the right
  foot stays turned in (rest yaw).  Idle: still.  'sit': straight out along the surface (see Poses).
* right_arm (intact) / left_arm (shoulder dropped 0.6 texel): idle hang, splayed just clear of the bell skirt, no
  natural swing.  Chase: arms stay stiff, jerk xRot -0.2 on each footfall; when closing in, pop the right hand up into
  the 'creep' wave.
* right_forearm: elbow of the good arm, follows the pose values.
* left_forearm: the BROKEN forearm hanging off its stringing cord (visible gap + cord at the elbow).  Never driven
  directly outside the poses: pendulum with lag and overshoot from the body/arm motion, amplitude up to 0.4 in chase,
  keeps swinging 2-3 s after she stops.  In 'attack' it flails outward.
* right_hand, left_hand: wrists.  Right: tiny tremor while idle (zRot 0.03).  Left: limp, swings with the forearm.
* right_finger1, right_finger2, right_finger3: spidery fingers of the good hand; idle twitch (one random finger xRot
  -0.3 for 3 ticks every 2-5 s); splay in 'creep' / 'attack' / 'scream' (pose values).
* left_finger1, left_finger2, left_finger3: the dead hand, curled; they only follow the swing.
* Emissive layer 'eyes' (muneca_eyes.png, same for both looks): dim iris + full-bright glint on the glass eye, a 2-px
  ember deep in the empty socket and the gloss on the black tear.  Optional: flicker the ember alpha in the renderer.

Poses (POSES; the thread_* entries are the plumb + swing of a frozen frame, computed by plumb() from THREAD_SWAY; Java
may replace them with the live gravity above, respecting the clamp).  Arms, hands and fingers of every pose were
solved against head, ringlets, skirt and body: none enters them -- keep it that way when blending.
* creep: the scare beat, played for the laugh.  Her head flops ~33 deg onto her LEFT shoulder (opposite to her rest
  roll; it rests on the dropped left puff sleeve, the shoulder sags 1 texel out and down), jaw ajar (dy 0.8), and the
  good right hand pops up beside the empty side of her head in a stiff little WAVE: palm to the camera, fingers
  splayed, wrist cocked, shoulder hitched up (it is a wave, not a reach -- "hola"); the loose threads still swinging
  forward from the snap.  Snap into it from 'sit' or idle in 1-2 ticks while the player is not looking, then freeze.
* attack: lunge.  Body pitches forward and slides 1 texel forward, legs counter-rotate so the shoes stay planted, head
  tilts up to show the face, the jaw drops (marionette, dy 3), both arms flung out and forward at the viewer so the
  splayed hands sit wide beside the dropped jaw, in front of the face plane (face, glass eye and open mouth stay
  unobstructed); the jaw snap flings both loose threads forward and apart across the black mouth.  Hold 6 ticks,
  then clack.
* scream: head thrown back (-0.5) and rolled AWAY from the good arm, jaw dropped; both hands flung up beside her face:
  the good right arm raised high and wide (shoulder hitched up and out 1 texel), the splayed claw beside her cheek and
  temple, outside the wig and ringlets (fingertips to x -13); the broken left arm yanked up on its cord, the dead hand
  dangling beside the jaw.  thread_right is kicked forward so it drapes over the chin instead of through it.
* sit: the dormant "just a doll" state and her warning: she sits next to whoever will be possessed next (on the roof of
  the doghouse, on Jorge's chair by the grill, on Lucia's pillow, on the Nona's lap) and on the shelf / bed in
  'cosida'.  Spawn the entity with its origin ON the seat surface (mattress / pillow top, chair seat, doghouse roof,
  top of the Nona's lap = the rocker seat height + lap): petticoat, heels and fingertips rest exactly on y = 24.  A
  propped-up doll: torso leaning BACK 0.2 (the face tips up toward a player standing over her: from 35-60 deg above
  you meet the glass eye and the socket), legs STRAIGHT out along the surface in a V (world angle ~90 deg, thigh
  sockets slid 5.8 texels forward under the skirt's front edge), heels down, soles facing forward and toes up and out
  -- the shoes clear the face plate by ~6.8 texels in side view; the skirt fanned round her; the long arms hang at her
  sides with the hands resting palm-down on the surface beside the thighs (the broken forearm folded in on its cord);
  the head keeps its rest loll onto her right shoulder.  Footprint from the origin: shoes 13.4 texels (0.42 block)
  forward, hair / skirt 11.7 (0.37 block) back, hands 9.9 texels (0.31 block) to each side (the bow on her head reaches
  x -13.5 but floats 0.5 block up) -> on a chair put the origin ~0.15 block behind the seat's front edge, facing out;
  on the Nona's lap face the same way as the Nona, origin on top of her thighs, the hands land beside her own thighs
  (inside the Nona's lap, clear of the Nona's arms).  Only the head (look, unseen) and the cloth/threads (frozen while
  seen) animate in this pose.

Jumpscare portrait ("el ultimo giro hasta la cara"): FOCUS 'head', look 'cortado', pose 'attack' -- glass eye, ember
socket, black tear, the dropped jaw and the cut threads flung across the open mouth full frame.
"""
