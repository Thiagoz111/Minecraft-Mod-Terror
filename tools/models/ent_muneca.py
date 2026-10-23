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
THREAD = hx('#08060a')
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
BRASS = pal('#3b2a10', '#6e5220', '#a8853a', '#dcc070')
CORD = pal('#1a120c', '#33251a', '#4e3a28', '#6d553d')
# the 1961 blessed thread: sixty years buried in a biscuit tin -- dried, brown-shifted, faded red
OLDT = pal('#1e0508', '#3e0d12', '#64181b', '#862823', '#a8442f', '#c4683f')
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
#  p/P blush  k tear  g tear gloss  M lip line  R/Q lip  S stitch thread
FACE_A = [
    # 0123456789ABCD
    "oooooOOOoohXXX",   # r0  forehead (bangs over the left); a chunk broken out of the corner
    "oooooooooochXX",   # r1  the crack leaves the chunk, chipped lip of the break
    "lololoooocsohh",   # r2  single spiky lashes | crack runs into the socket
    "eWWWWWoos..soo",   # r3  lid line over the glass eye | round socket
    "s.....os....so",   # r4  glass eye (eyeball behind) | socket (ember deep inside)
    "s.....os....so",   # r5
    "o.....oos..soo",   # r6
    "oeoeoeooChhkoo",   # r7  lower lashes | hairline crack + chipped lower lip | the tear leaves the socket
    "pPpMoSoSoChkpp",   # r8  blush | smile curls up | stitch ends above the lip | crack reaches the mouth | tear
    "ppooMNRNRNogPp",   # r9  rosebud upper lip pulled in by three stitches (N) | tear gloss
]
# Lower face 12 x 2 (x -6..6, y 8.5..10.5); the chin slot (x -3..3) is open.
FACE_B = [
    "pps......skp",
    "sos......oks",
]
# Chin 6 x 2 (x -3..3, y 8.5..10.5) + chin tip 4 x 1
CHIN = [
    "oNQNQN",
    "odododo"[:6],
]
CHIN_TIP = ["soos"]
FACE_COLS = {
    'h': CHIP, 'c': CRACK_D, 'r': hx('#2a2026'), 'l': LASH[0], 'e': LASH[1], 'W': LASH[0],
    'k': TEAR[0], 'g': TEAR[3], 'M': LIP[0], 'R': LIP[2], 'Q': LIP[3], 'S': THREAD, 'N': hx('#43070f'),
    'C': CRACK,
    'L': LIP[1],
}
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
            ch, fx, fy = FACE_A[ctx.j][ctx.i], ctx.i, ctx.j
        else:
            ch, fx, fy = FACE_B[ctx.j][ctx.i], ctx.i + 1, ctx.j + 10
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
        rows = CHIN if t == 'chin' else CHIN_TIP
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


def hair_shell(ctx):
    """Wig over the skull: side parting on top, strands radiating from it, bare over the face/cheeks."""
    f = ctx.face
    x, y, z = A(ctx)
    t = tag(ctx)
    if f == 'front':
        return None
    if chunk3(x, y, z):
        return None
    if f == 'bottom':
        return pick(HAIR, 0.18) if z > 2 else None
    if f in ('west', 'east') and z < -2.0 and y > 2.5:
        return None                                   # cheek / jaw left bare
    if near_chunk(x, y, z, 0.7):
        return pick(HAIR, 0.08)                       # torn wig edge
    if f == 'top':
        if t == 'crown_hair' and abs(x + 1.5) < 0.5 and z < 3.5:
            return pick(HAIR, 0.14)                   # side parting: 1 px of darker hair
        u = z
        v = abs(x + 1.5)
        return pick(HAIR, strand(u, v, ctx, 3, sheen_at=2.5) + 0.04)
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
        if t == 'toe':
            return pick(SOLE, 0.55 if ctx.i == 1 else 0.3)
        if lz > d - 1.6:
            return SOLE[0] if ctx.j == 0 else pick(SOLE, 0.3)      # heel block
        if ctx.i in (0, ctx.w - 1):
            return pick(SOLE, 0.3)                                 # welt
        return pick(SOLE, 0.8 if (ctx.j + ctx.i) % 3 else 0.55)    # worn leather sole
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


# ------------------------------------------------------------------ module contract
DEFAULT_MAT = dress_mat
FOCUS = 'head'


def build():
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
    bone('head', (0, 10.2, 0.5), parent='neck', rot=(4, -8, -14), mat=porcelain)
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

    m = Model('muneca', 128, 128, r.roots)
    m.scale = 0.5
    return m


POSES = {
    # head rolled to 40 degrees in total, the intact right arm raised beside the head, reaching for the viewer
    'creep': {'head': (0.1, 0.1, 0.94, 0, 0, 0), 'jaw': (0.25, 0, 0, 0, 0.8, 0),
              'body': (0.08, 0, 0, 0, -0.05, 0), 'right_leg': (-0.08, 0, 0, 0, 0, 0),
              'left_leg': (-0.08, 0, 0, 0, 0, 0),
              'right_arm': (-1.85, 0.4, -0.2, 0, 0, 0), 'right_forearm': (-0.3, 0, 0, 0, 0, 0),
              'right_hand': (-0.45, 0, 0.2, 0, 0, 0), 'right_finger1': (-0.5, 0, 0.45, 0, 0, 0),
              'right_finger2': (-0.6, 0, 0.05, 0, 0, 0), 'right_finger3': (-0.5, 0, -0.4, 0, 0, 0),
              'left_arm': (0.12, 0, -0.1, 0, 0, 0)},
    # lunge: jaw dropped, arms spread wide and high framing the face, fingers splayed
    'attack': {'body': (0.3, 0, 0, 0, 0.0, -1.0), 'right_leg': (-0.3, 0, 0, 0, 0, 0), 'left_leg': (-0.3, 0, 0, 0, 0, 0),
               'head': (-0.3, 0.12, 0.12, 0, 0, 0), 'jaw': (0.4, 0, 0, 0, 3.0, 0),
               'right_arm': (-1.95, 0.85, 0.2, 0, 0, 0), 'left_arm': (-1.95, -0.85, -0.2, 0, 0, 0),
               'right_forearm': (-0.6, 0, 0, 0, 0, 0), 'left_forearm': (-0.4, 0, 0.45, 0, 0, 0),
               'right_finger1': (0, 0, 0.5, 0, 0, 0), 'right_finger3': (0, 0, -0.5, 0, 0, 0),
               'left_finger1': (0.7, 0, 0.4, 0, 0, 0), 'left_finger3': (0.7, 0, -0.4, 0, 0, 0)},
    # head thrown back, jaw fully dropped, arms raised up beside the head with bent forearms
    'scream': {'head': (-0.5, 0, -0.22, 0, 0, 0), 'jaw': (0.55, 0, 0, 0, 1.3, 0),
               'right_arm': (-2.25, 0.3, -0.6, 0, 0, 0), 'left_arm': (-2.2, -0.3, 0.55, 0, 0, 0),
               'right_forearm': (-0.7, 0, 0, 0, 0, 0), 'left_forearm': (-0.4, 0, 0.3, 0, 0, 0),
               'right_finger1': (0, 0, 0.5, 0, 0, 0), 'right_finger3': (0, 0, -0.5, 0, 0, 0),
               'left_finger1': (0.7, 0, 0.4, 0, 0, 0), 'left_finger3': (0.7, 0, -0.4, 0, 0, 0)},
    # dropped on the floor like a toy: legs splayed forward, arms limp, head lolling
    'sit': {'body': (0, 0, 0, 0, 4.0, 0), 'right_leg': (-1.5, 0.4, 0, 0, 0, 0), 'left_leg': (-1.5, -0.4, 0, 0, 0, 0),
            'head': (0.25, 0, -0.3, 0, 0, 0), 'right_arm': (-0.15, 0, 0.2, 0, 0, 0), 'left_arm': (-0.1, 0, -0.4, 0, 0, 0),
            'right_forearm': (0.1, 0, 0.25, 0, 0, 0), 'right_hand': (0, 0, 0.5, 0, 0, 0)},
}

ANIM_NOTES = """Muneca Maldita -- animation notes.  Units: radians, offsets in model texels (2x density inside
scale_root, so 2 texels = 1 vanilla pixel).  t = ageInTicks, s = walk speed 0..1, all poses are ADDED to the rest pose.
She is porcelain: no breathing, no squash.  Drive head, jaw and arms in stop-motion (quantise time to 2-3 tick steps,
e.g. tq = floor(t / 2) * 2) and only let hair, ribbons and cloth move smoothly.  When the player looks straight at her,
freeze every bone (including the cloth) on the current frame; resume when the player looks away.

Bones
* body (root, pivot at the waist): whole doll.  Idle: perfectly still, a single 0.02 zRot "settle" jolt every 4-8 s.
  Chase: stiff toy waddle, zRot = sin(walk) * 0.12 * s toward the planted foot, dy = -abs(sin(walk)) * 0.4 (hop),
  no xRot sway.  Closing in (< 3 blocks): pitch forward 0.15.
* neck (ball joint on the collar): takes 30% of the head-look yaw/pitch (look(state, 0.3)).
* head: 70% of the head-look.  Rest pose is rolled 14 deg onto her right shoulder and turned 8 deg; keep it.  Idle: slow
  drift of +-0.05 then a SNAP of zRot +-0.3 in 2 ticks, hold 10-30 ticks, drift back.  Chase: head stays locked on the
  player (overshoot 0.1 and settle).  Pose 'creep' flops it 40 deg to the OTHER side - make that change in 2 ticks.
* jaw: marionette chin in two slots.  Opens by sliding DOWN (dy) plus a small hinge (xRot) around the back of the
  skull.  Idle: closed; every 6-12 s a single dummy clack (dy 0.8 for 2 ticks).  Attack: pose value (0.4 xRot, dy 3)
  reached in 2 ticks, then 3 fast clacks.  Scream: hold (0.55, dy 1.3).  Never ease it - stepped only.
* bow (hair bow on the top-left of the wig): secondary, spring-lagged zRot following head snaps (+-0.12), tiny flutter.
* curl_r1, curl_r2, curl_r3 (ringlets on her right), curl_l1, curl_l2 (on the broken left), curl_b1..curl_b4 (down the
  back): pendulums.  Each follows the head with 3-5 tick lag: xRot/zRot += spring(head motion) with amplitude 0.08-0.15
  and a different phase per curl (ripple("curl_", t, 0.12, 0.9, 0.06, 0.05, 0)).  Chase: +0.15 xRot bounce on footfall.
* skirt (core + torn petticoat): counter-yaw to the body in chase (yRot = -sin(walk) * 0.05).
* skirt_front, skirt_front_right, skirt_right, skirt_back_right, skirt_back, skirt_back_left, skirt_left,
  skirt_front_left: the 8 gathered upper tiers of the bell.  Tiny ripple idle (ripple("skirt_", t, 0.05, 0.8, 0.02, 0.01, 0)),
  open on each step in chase (xRot -0.06 * s).
* hem_front ... hem_front_left (one child per upper tier): the flared, torn lower tiers.  Lag the upper tier by ~3
  ticks and swing twice as far (ripple("hem_", t, 0.09, 0.8, 0.05, 0.03, -0.04 * s)); flare out on the attack lunge
  (xRot -0.2) and when she lands from a hop.
* right_leg, left_leg: stiff doll legs (no knee bend).  Chase: xRot = +-sin(walk) * 0.45 * s, alternating; the right
  foot stays turned in (rest yaw).  Idle: still.  Sit: pose 'sit'.
* right_arm (intact) / left_arm (shoulder dropped 0.6 texel): idle hang, no natural swing.  Chase: arms stay stiff,
  jerk xRot -0.2 on each footfall; when closing in raise the right arm toward the player (blend into 'creep').
* right_forearm: elbow of the good arm, follows the pose values.
* left_forearm: the BROKEN forearm hanging off its stringing cord (visible gap + cord at the elbow).  Never driven
  directly: pendulum with lag and overshoot from the body/arm motion, amplitude up to 0.4 in chase, keeps swinging
  2-3 s after she stops.  In 'attack' it flails outward.
* right_hand, left_hand: wrists.  Right: tiny tremor while idle (zRot 0.03).  Left: limp, swings with the forearm.
* right_finger1..3: spidery fingers of the good hand; idle twitch (one random finger xRot -0.3 for 3 ticks every 2-5 s);
  splay in 'creep'/'attack'/'scream' (pose values).  left_finger1..3: the dead hand, curled; only follows the swing.
* Emissive layer 'eyes': dim iris + full-bright glint on the glass eye, a 2-px ember deep in the empty socket and the
  gloss on the black tear.  Optional: flicker the ember alpha in the renderer.

Poses
* creep: the scare beat.  Head flops 40 deg to her left (net, opposite to her rest roll), jaw ajar (dy 0.8), the right
  arm rises toward the viewer with the wrist cocked and fingers splayed, left arm hangs.  Snap into it from 'sit' or idle
  in 1-2 ticks while the player is not looking, then freeze.
* attack: lunge.  Body pitches forward and slides 1 texel forward, legs counter-rotate so the shoes stay planted, head
  tilts up to show the face, the jaw drops (marionette, dy 3), both arms thrown forward, wide and high so the hands frame
  the face with splayed fingers (the open mouth stays visible).  Hold 6 ticks, then clack.
* scream: head thrown back with extra roll, jaw dropped, both arms raised up beside the head with bent forearms.
* sit: dormant "just a doll" state: dropped on the floor (body dy +3.8), legs straight out and splayed, arms limp,
  head lolling.  Leave her like this when spawned on shelves / beds.

Jumpscare portrait = FOCUS 'head' with the 'attack' jaw: glass eye, ember socket, tear and the dropped jaw full frame.
"""
