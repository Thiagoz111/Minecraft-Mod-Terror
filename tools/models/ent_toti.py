"""Toti Morales (15) -- the gamer son in the wardrobe (DEAD LINE, case 'casa', beats casa.ropero / casa.desayuno).

Authored at 2x texel density (model.scale = 0.5).  +Y down, ground y = 24, faces -Z, right_* on -X.  Centred on
x = 0, z = 0 (only the pad and the boom mic leave the column, in front).  Height 1.8 blocks: crown of the hair
y = -33.5 -> soles y = 24 (57.5 texels, rest pose); the headset band reaches -33.9 and the cowlick -34.3 (1.82
blocks).  69 cubes, 28 bones, texture 256 x 128 + the emissive 'eyes' layer.  Rest pose = standing and playing (the
idle he walks around in).

Design sketch
-------------
The gag (BIBLIA 2.2 h, beat 8): in the middle of the chase the player dives into the wardrobe and it is already
OCCUPIED.  For half a second the dark box holds a MONSTER: a hunched shape with two rings of coloured light where its
ears should be, a cold glow from below on a face whose eyes hide under a fringe, two pin-point reflections in them.
Then it yells "¡OCUPADO! ¡ESTOY EN RANKED!" and becomes the most ordinary thing in the case: a fifteen-year-old with a
gaming headset.  Horror read = the dark silhouette, the RGB rim light and the under-glow.  Comedy read = everything
you see a beat later.

Silhouette: a LOLLIPOP.  A skinny teen on a stick (16-wide hoodie, 6-wide legs with a gap between them) carrying a
big round mass on top -- the 14-wide head inside a 24-wide over-ear headset whose cups stick out 5 texels on each side,
a boom mic and hair tufts poking up round the headband.  Gamer posture: the head is jutted forward and bowed over the
pad (neck +16 deg, head +8 deg), the shoulders are rounded under the hood bunched on the back, the elbows are tucked
and both fists hold a chunky white gamepad in front of the belly.  The only other big shapes are the shoes: chunky
white sneakers, wider than the legs.

Proportions (texels at 2x): head 15 (skull top -32 .. chin -17) + 1-2 of hair, neck 3, hoodie 17 (shoulders -14 ..
hem 3), legs 21 (hips 3 .. soles 24), sneakers 5 of those.  Head + headset 24 wide, shoulders + sleeves 26 wide.

Face (skull front 14 x 11 + jaw front 12 x 4, hand-placed in the FACE / JAW grids): pale indoor skin with cool
shadows; a greasy dark-brown fringe on its own bone (a 1-texel solid root + a cut-out strand plane 1.3 texels in front
of the face, swept to his right: one strand crosses the right eye, the left brow peeks through); two low brows whose
inner ends drop onto the lids (concentration = annoyance); heavy half-shut lids; brown irises looking DOWN and IN at
the pad (slightly cross-eyed), each with one emissive cyan reflection of the screen; purple sleepless bags; acne (a
whitehead on the nose tip, a cluster on the left cheek, one on the chin, one on the forehead under the fringe); a teen
moustache (peach fuzz) over a dusky, crooked upper lip; a pouting lower lip.  The lower face is two static lower-cheek
blocks on the head with a 6-wide CHIN (the jaw bone) between them, so the mouth opens mouth-sized -- not the whole
lower face -- on a dark mouth with METAL BRACES on both rows of teeth (the "¡OCUPADO!" reveal).  A tongue on its own
bone parked in the mouth slides out of the left corner in concentration.

The RGB rig (emissive 'eyes' layer, additive in game): two big matte-black cups whose outer plates carry a gradient
ring (cyan -> blue -> violet on his right, magenta -> pink -> violet on his left) and a little diamond logo, an LED
strip along the headband, a red "muted" LED on the boom mic.  The cups RIM-LIGHT his face: the outer face columns,
the cheeks in front of the cups and the jaw edges carry a dim cyan (right) / magenta (left) glow -- in the dark cell
the face reads as two coloured edges.  The pad lights him from below: a cyan light bar, four coloured face buttons and
a dim cyan glow on the underside of the jaw, the nose and the fists.

Wardrobe: a charcoal pull-over hoodie with the hood down (a rolled collar round the neck, lined in acid green, the hood
lying on his back), white drawstrings with green aglets, a big cracked acid-green "GG" print, a kangaroo pocket with a
phone-shaped bulge, ribbed hem and cuffs; heather-grey joggers with orange snack-dust finger smears on the thighs,
bunched over ribbed ankle cuffs; chunky white sneakers (grey toe box, red heel tab and side stripes, puffy tongue,
the right shoe's lace untied and trailing).  Orange dust on the fingertips too.

Palette: pale pink-beige skin with violet shadows, cold charcoal, acid green, heather grey, cold white, RGB.  He is the
only cold, desaturated member of a warm family (celeste/white dad, pink mum, bordo nona, red sister) -- and the only
one who glows.
"""
import colorsys
import math

import numpy as np

from mcmodel import Model, hash3, face_light, pick, rot_matrix
from rig import Rig
from paint import hx, mix


def H(*cs):
    return [hx(c) for c in cs]


# ------------------------------------------------------------------ palettes (dark -> light, hue shifted)
SKIN = H('#2a1b20', '#432c32', '#5f4046', '#7c5659', '#9a6f6d', '#b48a83', '#c9a399', '#dabbaf', '#e8d0c4',
         '#f3e2d8')
HAIR = H('#090605', '#120c0a', '#1b130f', '#261a14', '#33231a', '#422e22', '#543a2b', '#6a4b37', '#86624a')
HOOD = H('#07080b', '#0d0f14', '#14171e', '#1c2028', '#252a34', '#2f3542', '#3b4252', '#4b5366', '#5f687e')
ACID = H('#0c2207', '#173d0b', '#255f10', '#378316', '#4fa61d', '#6cc528', '#93df44', '#bff27a')
JOG = H('#24252b', '#313239', '#41424a', '#53545d', '#666770', '#7b7c85', '#91929a', '#a7a8af', '#bebfc5')
WHITE = H('#3c414e', '#575d6b', '#767c8a', '#969ca8', '#b4b9c3', '#ccd1d9', '#dfe3e9', '#eef0f4', '#f9fafc')
RED = H('#33090d', '#561016', '#7d161d', '#a42127', '#c73330', '#e1523f', '#f17a5c')
PLASTIC = H('#030304', '#08080b', '#0e0f13', '#15171c', '#1e2027', '#292c35', '#373b46', '#4b505e', '#676d7e')
CUSHION = H('#0b0b0e', '#131318', '#1b1b22', '#25252d', '#30303a', '#3e3e4a')
STEEL = H('#3b404a', '#5d636e', '#868c97', '#b0b6bf', '#d8dde3', '#f4f6f8')
ORANGE = H('#9a4a12', '#c4661a', '#e0862a', '#f2a443')
MOUTH = H('#0c0306', '#1c070c', '#300d14', '#4a141e', '#66202a')
TONGUE = H('#6e2a34', '#93404a', '#b45a62', '#cf7a7e', '#e69a9a')
TEETH = H('#7d7466', '#a8a08e', '#cfc8b4', '#ebe6d6', '#f8f5ec')
LIP = H('#6e4446', '#8e5a5a', '#a87270', '#bf8a85', '#d3a49c')
BRACE = hx('#c9d1da')
BRACE_D = hx('#6c7580')
SCLERA = hx('#e4d9d6')
SCLERA_S = hx('#b9a7a6')
VEIN = hx('#d48f92')
IRIS = hx('#4a2a19')
IRIS_L = hx('#74482a')
PUPIL = hx('#120806')
LID = hx('#2e161b')
BAG = hx('#5b3b60')
PIMPLE = hx('#b9575c')
WHITEHEAD = hx('#f3d6c8')

# RGB light: hue ranges of the two cups (his right = cyan side, his left = magenta side)
RIM_R = (0.30, 0.95, 1.00)            # cyan rim on his right (-X, viewer's left)
RIM_L = (1.00, 0.22, 0.86)            # magenta rim on his left (+X, viewer's right)
PAD_GLOW = (0.45, 0.95, 1.00)         # the pad's light bar


def hsv(h, s, v, a=255):
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, s, v)
    return (int(r * 255), int(g * 255), int(b * 255), a)


def rgbf(c, k, a=255):
    return (int(c[0] * 255 * k), int(c[1] * 255 * k), int(c[2] * 255 * k), a)


def ring_hue(side, ang):
    """Hue of the RGB ring at angle ang (radians) round a cup.  Right cup cyan->blue->violet, left magenta->pink."""
    t = 0.5 + 0.5 * math.sin(ang)
    if side < 0:
        return 0.50 + 0.25 * t                       # cyan .. violet
    return 0.83 + 0.14 * t                           # magenta .. pink-red


def clamp(v, a=0.0, b=1.0):
    return a if v < a else b if v > b else v


# ------------------------------------------------------------------ texel helpers
def local(ctx):
    """Texel centre in cube-local texel units (independent of bone rotation): lz = 0 at the front face."""
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
    """Absolute authoring (bind-frame) coordinates of the texel centre."""
    lx, ly, lz = local(ctx)
    o = ctx.cube.a0
    return o[0] + lx, o[1] + ly, o[2] + lz


def tag(ctx):
    return ctx.cube.name or ''


def kind(ctx):
    return getattr(ctx.cube, 'kind', '')


def side_of(ctx):
    return getattr(ctx.cube, 'sx', 1)


def edge(ctx):
    return min(ctx.i, ctx.j, ctx.w - 1 - ctx.i, ctx.h - 1 - ctx.j)


def outer_face(ctx):
    return 'west' if side_of(ctx) < 0 else 'east'


def inner_face(ctx):
    return 'east' if side_of(ctx) < 0 else 'west'


def h2(a, b, s=0):
    return hash3(a, b, 0, s)


def around(ctx):
    """Continuous horizontal coordinate wrapping round a cube (front -> east -> back -> west)."""
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    f = ctx.face
    if f == 'front':
        return lx
    if f == 'east':
        return w + lz
    if f == 'back':
        return w + d + (w - lx)
    if f == 'west':
        return 2 * w + d + (d - lz)
    return lx


def glow(fn):
    """Emissive decal: fn(i, j, w, h) -> rgba | None for every texel of the face rect."""
    def deco(img, u0, v0, w, h):
        px = img.load()
        for j in range(h):
            for i in range(w):
                c = fn(i, j, w, h)
                if c is not None:
                    px[u0 + i, v0 + j] = c
    return deco


# ------------------------------------------------------------------ the face
# Skull front: 14 x 11, col c <-> x in [-7 + c, -6 + c], row r <-> y in [-32 + r, -31 + r].  The fringe root covers
# rows 0-2, the strand plane hangs in front of rows 3-7.  The nose cube covers cols 6-7, rows 6-8.
#   0-9 skin ramp   h hair shadow at the hairline   b / B brow (light / heavy)   L upper lid   k lid crease
#   W sclera   w sclera in the lid's shadow   I iris   i lit iris   K pupil   g screen glint (emissive)   l lower lid
#   d / D sleepless bags   P pimple   Q whitehead   q pimple halo   f peach-fuzz moustache   s philtrum / nostril shade
#   m mouth line   M mouth corner   x under-lip shade   v / V lower lip (body / highlight)
FACE = [
    # 0123456789ABCD
    "hhhhhhhhhhhhhh",   # r0  y-32  hairline (under the fringe root)
    "67888888888876",   # r1  y-31  forehead (behind the fringe)
    "678888qPq88876",   # r2  y-30  forehead pimple (peeks between the strands)
    "56777777777765",   # r3  y-29  shadow cast by the fringe
    "6bBBb7777bBBb6",   # r4  y-28  low brows (soft brown) ...
    "6kLLLB77BLLLk6",   # r5  y-27  ... whose inner ends drop onto the dark lash line: concentration = annoyance
    "65wgIw77wIgw56",   # r6  y-26  half-lidded: sclera in the lid's shadow, iris top + screen glint (emissive)
    "65WiKW77WKiW56",   # r7  y-25  lit lower iris, pupils low and in: looking DOWN at the pad, a bit cross-eyed
    "66dDDd77dDDd66",   # r8  y-24  sleepless purple bags
    "678874ss47qPq6",   # r9  y-23  lit cheekbones, philtrum, faint fuzz at the corners, cheek pimple
    "66777Muuuu7766",   # r10 y-22  dusky upper lip, the right corner pinched up
]
# Jaw front: 12 x 4, col c <-> x in [-6 + c, -5 + c] (= skull col c + 1), row r <-> y in [-21 + r, -20 + r]
JAW = [
    # 0123456789AB
    "56777vVvvM65",     # j0 y-21  pouting lower lip, the left corner dips (crooked mouth)
    "567776xx6765",     # j1 y-20  shade under the lip
    "467P88887764",     # j2 y-19  lit chin, chin pimple
    "345666666543",     # j3 y-18  chin turning under
]
assert all(len(r) == 14 for r in FACE) and len(FACE) == 11
assert all(len(r) == 12 for r in JAW) and len(JAW) == 4
GLINTS = [(3, 6), (10, 6)]         # skull-front texels holding the emissive screen reflections


def face_rgba(ch, c, r):
    if ch.isdigit():
        return SKIN[int(ch)]
    return {
        'h': mix(SKIN[4], HAIR[3], 0.55), 'b': mix(HAIR[5], SKIN[5], 0.45), 'B': mix(HAIR[4], SKIN[4], 0.2), 'L': LID,
        'u': mix(LIP[1], SKIN[5], 0.35), '4': SKIN[4],
        'k': SKIN[5], 'W': SCLERA, 'w': SCLERA_S, 'I': IRIS, 'i': IRIS_L, 'K': PUPIL, 'g': hx('#bff4ff'),
        'l': mix(SKIN[5], VEIN, 0.3), 'd': mix(SKIN[6], BAG, 0.33), 'D': mix(SKIN[5], BAG, 0.5),
        'P': PIMPLE, 'Q': WHITEHEAD, 'q': mix(SKIN[7], PIMPLE, 0.3), 'f': mix(SKIN[7], HAIR[6], 0.2),
        's': SKIN[6], 'm': hx('#3b151b'), 'M': hx('#6a3439'), 'x': SKIN[5], 'v': LIP[2], 'V': LIP[3],
    }.get(ch, SKIN[7])


def rim(c, side, k):
    """Bake the RGB rim light into the base texture (side -1 = cyan / +1 = magenta), strength k 0..1."""
    col = RIM_R if side < 0 else RIM_L
    tgt = (int(col[0] * 255), int(col[1] * 255), int(col[2] * 255), 255)
    return mix(c, tgt, k)


def rim_glow(side, k):
    """Emissive (additive) rim value."""
    return rgbf(RIM_R if side < 0 else RIM_L, k)


# ------------------------------------------------------------------ materials
def skin_v(ctx, base=0.72):
    v = base + face_light(ctx)
    if edge(ctx) == 0 and ctx.face not in ('top', 'bottom') and 0 not in ctx.cube.size:
        v -= 0.04
    return v


def skin_mat(ctx):
    t = tag(ctx)
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    x, y, z = A(ctx)
    if t == 'skull':
        if f == 'front':
            c = face_rgba(FACE[ctx.j][ctx.i], ctx.i, ctx.j)
            if 4 <= ctx.j and ctx.i in (0, 13):
                c = rim(c, -1 if ctx.i == 0 else 1, 0.2)
            elif 5 <= ctx.j and ctx.i in (1, 12):
                c = rim(c, -1 if ctx.i == 1 else 1, 0.06)
            return c
        if f in ('west', 'east'):
            sd = -1 if f == 'west' else 1
            if y < -24.0 or z > -3.5:
                return pick(HAIR, 0.22)                     # under the hair shell / behind the cup
            v = skin_v(ctx, 0.62) - (0.06 if z > -5 else 0.0)
            if y > -22.5:
                v -= 0.08                                   # jawline turning under
            c = pick(SKIN, v)
            return rim(c, sd, 0.1 if z > -5.5 else 0.06)
        if f == 'bottom':
            if abs(x) < 4.0 and z < -2.0:
                return MOUTH[2] if z < -5 else MOUTH[1]     # roof of the mouth (seen with the jaw open)
            return pick(SKIN, 0.36)                         # under the cheeks, beside the narrower jaw
        return pick(HAIR, 0.15)                             # top / back: under the hair
    if t == 'nose':
        if f == 'front':
            if ctx.j == 2 and ctx.i == 1:
                return WHITEHEAD
            if ctx.j == 2 and ctx.i == 0:
                return mix(SKIN[7], PIMPLE, 0.55)
            return SKIN[8] if ctx.j == 0 else SKIN[7]
        if f == 'bottom':
            return SKIN[3] if ctx.i == 0 else SKIN[4]
        if f in ('west', 'east'):
            return pick(SKIN, 0.55 - ly / h * 0.08)
        return SKIN[7]
    if t in ('jaw', 'cheek'):
        # lower face = right cheek | chin (the jaw bone, 6 wide) | left cheek, painted from one 12-wide JAW grid
        if f == 'front':
            col = int(clamp(math.floor(x + 6.0), 0, 11))
            c = face_rgba(JAW[ctx.j][col], col, ctx.j)
            if col in (0, 11):
                c = rim(c, -1 if col == 0 else 1, 0.2)
            return c
        if f == 'bottom':
            v = 0.42 - lz / d * 0.12
            return mix(pick(SKIN, v), hx('#5fd8e8'), 0.22 if lz < 5 else 0.08)   # lit from below by the pad
        if f == 'top':
            if t == 'jaw':
                return TONGUE[1] if 1 <= lz < 5 and 1 <= lx < w - 1 else MOUTH[1]   # tongue bed (jaw open)
            return SKIN[3]
        if f in ('west', 'east'):
            sd = -1 if f == 'west' else 1
            v = skin_v(ctx, 0.58) - lz / d * 0.12 - ly / h * 0.06
            if t == 'jaw' or f == ('east' if x < 0 else 'west'):
                return pick(SKIN, v - 0.1)                  # inner faces: only seen with the chin dropped
            return rim(pick(SKIN, v), sd, 0.09 if lz < 4 else 0.03)
        return pick(SKIN, 0.4)
    if t == 'neck':
        if f in ('top', 'bottom'):
            return SKIN[3]
        v = skin_v(ctx, 0.58) - (0.18 if ly < 1.5 else 0.0)
        if f == 'front' and ctx.i == 2 and ctx.j == 2:
            v += 0.05                                       # adam's apple
        return pick(SKIN, v)
    if t == 'tongue':
        v = 0.55 + face_light(ctx)
        if f == 'top' and ctx.i == ctx.w // 2:
            v -= 0.25                                       # the groove down the middle
        return pick(TONGUE, v)
    return pick(SKIN, skin_v(ctx))


def hand_mat(ctx):
    """Bony pale hands round the pad grips: knuckles, finger splits, nails, cheese-snack dust on the tips.

    In the pad frame the palm is a vertical plate on the outside of the grip (its outer face = back of the hand), the
    four fingers come out of its lower edge and wrap under the grip toward the pad centre (tips on the inner end),
    the thumb lies on top of the pad over the stick (nail on its inner end)."""
    t = tag(ctx)
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    sd = side_of(ctx)
    v = skin_v(ctx, 0.66)
    tip_face = 'west' if sd > 0 else 'east'                 # the inner end of fingers / thumb
    if t == 'palm':
        if f == outer_face(ctx):
            if ly > h - 1.0:
                v += 0.07 if int(lz) % 2 == 0 else -0.03    # knuckle row along the lower edge
            elif ly < 1.0:
                v += 0.03
            if lz > d - 1.0:
                v -= 0.06                                   # wrist going into the cuff
            if 1.0 <= ly < 3.0 and int(lz) == 1:
                v += 0.03                                   # a tendon
            return pick(SKIN, v)
        if f == inner_face(ctx):
            return pick(SKIN, v - 0.12)                     # palm pressed on the grip
        if f == 'back':
            return pick(SKIN, v - 0.05)
        return pick(SKIN, v)
    if t == 'fingers':
        finger = int(min(3, lz))                            # four fingers side by side along z
        v += 0.03 if finger % 2 == 0 else -0.03
        if f == tip_face:
            c = pick(SKIN, v + 0.02)
            if ctx.j == 0:
                c = mix(SKIN[8], hx('#f0dcd2'), 0.5)        # nails
            if h2(ctx.i, ctx.j, 3) > 0.5:
                c = mix(c, ORANGE[2], 0.35)                 # cheese-snack dust
            return c
        if f in ('top', 'bottom') and abs(lx - (w - 1.5 if sd > 0 else 1.5)) < 0.5:
            v -= 0.07                                       # middle-joint crease
        return pick(SKIN, v)
    if t == 'thumb':
        if f == 'top':
            if (lx < 1.0) if sd > 0 else (lx > w - 1.0):
                return mix(SKIN[8], hx('#f0dcd2'), 0.55)    # thumbnail
            if abs(lx - w / 2.0) < 0.5:
                return pick(SKIN, v - 0.06)                 # knuckle crease
            return pick(SKIN, v + 0.04)
        if f == tip_face:
            return mix(pick(SKIN, v), ORANGE[2], 0.3)
        if f == 'bottom':
            return pick(SKIN, v - 0.1)
        return pick(SKIN, v)
    return pick(SKIN, v)


def _split(k, seed):
    """Is texel column k a dark split between two hair clumps?  (never two splits side by side)"""
    return h2(k, seed, 41) > 0.6 and h2(k - 1, seed, 41) <= 0.6


def strand_v(u, along, seed, sheen=None):
    """Greasy hair clumps: a 1-texel dark split every 2-4 texels, a lit edge on each clump's left, a darker right edge,
    and an optional sheen band across the strands at `along` = sheen."""
    ui = int(math.floor(u))
    v = 0.44 + (h2(ui // 3, seed, 43) - 0.5) * 0.06
    split = _split(ui, seed)
    if split:
        v -= 0.17
    elif _split(ui - 1, seed):
        v += 0.07
    elif _split(ui + 1, seed):
        v -= 0.04
    if sheen is not None and not split:
        dist = abs(along - sheen)
        if dist < 1.1:
            v += 0.2 * (1.0 - dist / 1.1)
    return v


# fringe strand plane 16 x 7: col p <-> x in [-8 + p, -7 + p], row t <-> y in [-31 + t, -30 + t]; '#' hair, '.' cut
FRINGE = [
    # 0123456789ABCDEF
    "################",   # t0 y-31 (inside the root)
    "################",   # t1 y-30
    "################",   # t2 y-29
    "##########.#.###",   # t3 y-28 brows (the left brow peeks through)
    "####.#.##.#.#..#",   # t4 y-27 lids
    ".###...........#",   # t5 y-26 one clump over the outer corner of the right eye
    "..##............",   # t6 y-25 ... its tip crossing the right eye
]
assert all(len(r) == 16 for r in FRINGE)


def hair_mat(ctx):
    t = tag(ctx)
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    x, y, z = A(ctx)
    lt = face_light(ctx) * 0.8
    if t == 'fringe_tips':
        if f != 'front':
            return None
        if FRINGE[ctx.j][ctx.i] != '#':
            return None
        below = ctx.j + 1 < len(FRINGE) and FRINGE[ctx.j + 1][ctx.i] == '#'
        u = ctx.i + ctx.j * 0.45                            # strands swept toward his right
        v = strand_v(u, ctx.j, 7) - ctx.j * 0.035
        if not below:
            v -= 0.1                                        # darker, thinner tip
        return pick(HAIR, v + 0.06)
    if t == 'fringe_root':
        if f == 'back':
            return None
        if f == 'front':
            return pick(HAIR, strand_v(lx + ly * 0.45, ly, 7, sheen=1.0) + 0.08)
        if f == 'top':
            return pick(HAIR, strand_v(lx, lz, 7) + 0.14)
        if f == 'bottom':
            return pick(HAIR, 0.12)
        return pick(HAIR, strand_v(lz, ly, 9) + lt)
    if t == 'shell':
        if f == 'front':
            return None                                     # the fringe owns the hairline
        if f == 'bottom':
            return None
        if f == 'top':
            # strands combed forward from the crown (z 3) toward the fringe, fanning a little; sheen before the band
            u = x * (1.0 + (3.0 - z) * 0.025)
            return pick(HAIR, strand_v(u, z, 13, sheen=-3.5) + 0.1)
        if f in ('west', 'east'):
            # ragged lower edge (cut out: the skull side shows through) in front of the cups
            if z < -3.5:
                cut = -24.6 + h2(int(math.floor(z)), 5, 2) * 1.6 - (0.6 if z < -6 else 0.0)
                if y > cut:
                    return None
            v = strand_v(z * 0.9, y, 17 if f == 'west' else 19, sheen=-29.0) + lt
            if y > -26:
                v -= 0.06
            return pick(HAIR, v)
        if f == 'back':
            return pick(HAIR, strand_v(x, y, 23, sheen=-29.5) + lt - 0.02)
    if t == 'nape':
        if f in ('front', 'top'):
            return None
        if f == 'bottom':
            return pick(HAIR, 0.1)
        u = x if f == 'back' else z
        v = strand_v(u, y, 29) + lt - 0.04
        tip = h2(int(math.floor(u)), 3, 31)
        if ly > h - 1.0 - tip * 1.5:
            v -= 0.12                                       # ragged dark ends at the nape
        return pick(HAIR, v)
    if t == 'tuft':
        if f == 'bottom':
            return pick(HAIR, 0.1)
        v = strand_v(lx + lz, ly, 37 + int(x), sheen=0.6) + lt
        return pick(HAIR, v + 0.04)
    if t == 'lock':
        if f not in ('west', 'east'):
            return None
        tipcut = 6 - (1 if h2(ctx.i, 3, 5) > 0.5 else 0)
        if ctx.j > tipcut and ctx.i != 1:
            return None
        return pick(HAIR, strand_v(ctx.i * 1.0, ctx.j, 43) + 0.04 - ctx.j * 0.02)
    return pick(HAIR, 0.3 + lt)


# ------------------------------------------------------------------ hoodie
FONT_G = [".###", "#...", "#.##", "#..#", ".###"]
GG_ROW = 1                     # first row of the print on the torso front (y -13): above the pad, between the strings
GG_COLS = (2, 10)              # the two letters (4 wide); the drawstrings hang in the gap (cols 6-9)


def gg_px(i, j):
    """'GG' print on the torso front (16 wide): two 4 x 5 letters at cols 2-5 / 10-13, rows 1-5 (y -13 .. -8)."""
    r = j - GG_ROW
    for c0 in GG_COLS:
        c = i - c0
        if 0 <= r < 5 and 0 <= c < 4 and FONT_G[r][c] == '#':
            return 'ink'
    # drop shadow down-right
    for c0 in GG_COLS:
        c = i - c0 - 1
        rr = r - 1
        if 0 <= c < 4 and 0 <= rr < 5 and FONT_G[rr][c] == '#':
            return 'shadow'
    return None


def rib(ctx, v, period=2):
    return v + (0.05 if int(math.floor(around(ctx))) % period == 0 else -0.03)


def seg_dist(px, py, seg):
    """Distance from (px, py) to a segment, signed side (+ = left of its direction) and the projection t."""
    x0, y0, x1, y1 = seg
    dx, dy = x1 - x0, y1 - y0
    t = clamp(((px - x0) * dx + (py - y0) * dy) / (dx * dx + dy * dy))
    cx, cy = x0 + t * dx, y0 + t * dy
    n = math.hypot(dx, dy)
    sd = ((px - cx) * -dy + (py - cy) * dx) / n
    return math.hypot(px - cx, py - cy), sd, t


def folds(ctx, segs, crease=0.11, ridge=0.05):
    """Hand-placed cloth folds on a face (segments in face-texel coords): a 1-texel crease + a lit ridge beside it."""
    px, py = ctx.i + 0.5, ctx.j + 0.5
    dv = 0.0
    for seg in segs:
        dist, sd, t = seg_dist(px, py, seg)
        taper = 0.55 if t in (0.0, 1.0) else 1.0
        if dist < 0.55:
            dv -= crease * taper
        elif dist < 1.45 and sd > 0:
            dv += ridge * taper
    return dv


def knit(ctx, amt=0.018, seed=0):
    return (hash3(ctx.i, ctx.j, ctx.w * 7 + ctx.h * 3 + seed, 91) - 0.5) * amt


# fold layouts (face-texel coordinates)
FOLD_TORSO_FRONT = [(0.5, 4.0, 4.2, 8.6), (15.5, 4.0, 11.8, 8.6), (1.5, 12.8, 5.5, 12.1), (9.8, 12.2, 14.2, 13.0),
                    (5.8, 13.6, 8.6, 13.8)]
FOLD_TORSO_SIDE = [(1.5, 9.0, 5.0, 12.2), (4.8, 2.6, 7.5, 5.8), (0.5, 13.0, 3.5, 13.6)]
FOLD_TORSO_BACK = [(1.5, 10.8, 6.8, 12.4), (9.2, 12.4, 14.5, 11.2), (5.8, 13.6, 10.2, 13.7)]
FOLD_SLEEVE = {'front': [(0.0, 6.4, 5.0, 7.6), (0.4, 8.6, 4.6, 8.1)], 'back': [(0.0, 7.6, 5.0, 6.6)],
               'out': [(0.0, 6.9, 5.0, 6.3), (0.5, 8.7, 4.5, 9.2)], 'in': [(0.0, 7.8, 5.0, 8.6)]}
FOLD_FOREARM = [(0.0, 1.4, 4.0, 2.9), (0.0, 4.6, 4.0, 5.6)]


def hoodie_mat(ctx):
    t = tag(ctx)
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    x, y, z = A(ctx)
    v = 0.52 + face_light(ctx) * 0.9 + knit(ctx)
    if edge(ctx) == 0 and f not in ('top', 'bottom'):
        v -= 0.04
    if t == 'torso':
        if f == 'top':
            if abs(x) < 3.6 and -3.0 < z < 3.8:
                return HOOD[0]                              # neck hole
            return pick(HOOD, v + 0.04)
        if f == 'bottom':
            return HOOD[1]
        if f == 'front':
            g = gg_px(ctx.i, ctx.j)
            if g == 'ink':
                crack = h2(ctx.i, ctx.j, 51)
                if crack > 0.88:
                    return pick(HOOD, v + 0.02)             # cracked print: the fleece shows through
                return ACID[6] if ctx.j == GG_ROW else (ACID[5] if ctx.j <= GG_ROW + 2 else ACID[4])
            if g == 'shadow':
                return mix(pick(HOOD, v), ACID[1], 0.5)
            cx = abs(lx - w / 2.0)
            v += 0.05 * clamp(1.0 - cx / 6.0) * clamp(1.0 - ly / 8.0)    # chest catches the light
            v -= 0.05 * clamp((cx - 6.0) / 2.0)             # sides turn away
            v += folds(ctx, FOLD_TORSO_FRONT)
            return pick(HOOD, v)
        if f in ('west', 'east'):
            if abs(lz - 4.0) < 0.5:
                v -= 0.04                                   # side seam
            v -= 0.06 * clamp((4.0 - ly) / 4.0)            # armpit shadow under the sleeve
            v += folds(ctx, FOLD_TORSO_SIDE)
            return pick(HOOD, v)
        if f == 'back':
            v += folds(ctx, FOLD_TORSO_BACK) - 0.02
            return pick(HOOD, v)
    if t == 'hem':
        if f == 'top':
            return HOOD[1]
        if f == 'bottom':
            return HOOD[0] if abs(x) < 7 and abs(z) < 3.4 else HOOD[2]
        return pick(HOOD, rib(ctx, v - 0.07))
    if t == 'pocket':
        if f == 'back':
            return None
        if f == 'front':
            # pocket mouths at the sides (curved dark slits), stitched top seam, phone-shaped bulge on his left
            if ctx.i in (0, w - 1):
                return HOOD[1] if ctx.j >= 1 else pick(HOOD, v - 0.06)
            if ctx.i in (1, w - 2) and ctx.j <= 2:
                return pick(HOOD, v - 0.12)
            if ctx.j == 0:
                return pick(HOOD, v + 0.07) if ctx.i % 2 else pick(HOOD, v + 0.01)   # top seam stitches
            if 6 <= ctx.i <= 8 and 1 <= ctx.j <= 3:
                v += 0.08 if ctx.j == 1 else 0.03           # phone-shaped bulge
                if ctx.i == 8:
                    v -= 0.05
            return pick(HOOD, v - 0.02)
        if f == 'top':
            return pick(HOOD, v + 0.06)
        return pick(HOOD, v - 0.1)
    if t == 'sleeve':
        if f == 'top':
            return pick(HOOD, v + 0.02)
        if f == 'bottom':
            return HOOD[1]
        key = 'out' if f == outer_face(ctx) else ('in' if f == inner_face(ctx) else f)
        v += folds(ctx, FOLD_SLEEVE[key])
        if ly < 1.5:
            v += 0.04                                       # shoulder catches the light
        if key == 'in':
            v -= 0.07
        return pick(HOOD, v)
    if t == 'forearm':
        if f in ('top', 'bottom'):
            return HOOD[1]
        v += folds(ctx, FOLD_FOREARM if f in ('front', 'back') else [(0.0, 2.2, 4.0, 1.4), (0.0, 5.4, 4.0, 4.4)])
        if f == inner_face(ctx):
            v -= 0.06
        return pick(HOOD, v)
    if t == 'cuff':
        if f == 'bottom':
            return SKIN[3]                                  # wrist inside the cuff
        if f == 'top':
            return HOOD[1]
        return pick(HOOD, rib(ctx, v - 0.05))
    if t in ('collar_back', 'collar_side'):
        lining = (f in ('top', 'front')) if t == 'collar_back' else (f in ('top', 'front') or f == inner_face(ctx))
        if lining:
            lv = 0.5 + face_light(ctx) * 0.7
            if edge(ctx) == 0:
                lv += 0.07 if f == 'top' else -0.1          # the rolled rim catches the light
            lv += 0.04 if int(around(ctx) if f != 'top' else lx) % 3 == 0 else 0.0     # gathered ripples
            return pick(ACID, lv - 0.06)
        if f == 'bottom':
            return HOOD[1]
        return pick(HOOD, v + (0.05 if ly < 1 else 0.0))
    if t in ('drape', 'drape_tip'):
        if f == 'front':
            return HOOD[1]
        if f == 'top':
            return pick(ACID, 0.45)                         # the lining shows where the hood folds over
        if f == 'bottom':
            return HOOD[1]
        if f == 'back':
            mid = w / 2.0
            if abs(lx - mid - 0.5) < 0.5:
                return pick(HOOD, v - 0.11)                 # centre seam of the hood
            if abs(lx - mid + 0.5) < 0.5:
                v += 0.03
            if t == 'drape' and ctx.j == 0:
                return pick(ACID, 0.4 + (0.06 if ctx.i % 3 == 0 else 0.0))   # lining rolled over the top edge
            v += 0.05 - ly / 10.0 * 0.08 if t == 'drape' else -0.05
            v -= abs(lx - mid) / mid * 0.06                 # the hood is round: darker toward its sides
            if t == 'drape_tip' and ctx.j == h - 1 and ctx.i in (0, w - 1):
                return None                                 # rounded point
            if edge(ctx) == 0 and ctx.i in (0, w - 1):
                v += 0.04                                   # lit rim of the hood's edge
            return pick(HOOD, v)
        return pick(HOOD, v - 0.04)
    return pick(HOOD, v)


def string_mat(ctx):
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    if ly > h - 2.0:
        return ACID[5] if f in ('front', 'west', 'east') and ly < h - 1 else ACID[3]   # aglet
    v = 0.7 + face_light(ctx) - (0.08 if f in ('west', 'east') else 0.0)
    if h2(ctx.j, 1, 61) > 0.8:
        v -= 0.1                                            # chewed / dirty
    return pick(WHITE, v)


# ------------------------------------------------------------------ joggers + sneakers
def heather(ctx, v):
    """Heather-grey fleece: sparse light and dark flecks over a near-flat base."""
    n = hash3(ctx.i, ctx.j, ctx.w * 5 + ctx.h, 71)
    if n > 0.95:
        return v + 0.05
    if n < 0.05:
        return v - 0.045
    return v + (n - 0.5) * 0.02


# orange snack-dust finger streaks on the thigh fronts (he wipes his fingers): (i, j) -> strength
SMEAR_L = {(1, 2): 0.55, (2, 3): 0.45, (3, 4): 0.3, (3, 2): 0.5, (4, 3): 0.38, (4, 4): 0.2}
SMEAR_R = {(3, 3): 0.45, (2, 4): 0.36, (1, 5): 0.22, (4, 4): 0.3}
FOLD_THIGH_FRONT = [(0.4, 7.4, 3.0, 8.3), (3.0, 8.3, 5.6, 7.5), (1.0, 9.3, 5.0, 9.5)]
FOLD_THIGH_SIDE = [(0.6, 7.8, 5.4, 8.6), (1.5, 2.5, 4.5, 3.4)]
FOLD_THIGH_BACK = [(0.5, 1.8, 5.5, 2.6), (0.8, 8.4, 5.2, 8.0)]
FOLD_SHIN = [(0.0, 2.6, 2.5, 3.5), (2.5, 3.5, 5.0, 2.6), (0.0, 4.4, 2.5, 5.3), (2.5, 5.3, 5.0, 4.4)]


def jogger_mat(ctx):
    t = tag(ctx)
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    sd = side_of(ctx)
    v = heather(ctx, 0.52 + face_light(ctx) * 0.9)
    if edge(ctx) == 0 and f not in ('top', 'bottom'):
        v -= 0.04
    if t == 'thigh':
        if f in ('top', 'bottom'):
            return JOG[1]
        v -= 0.09 * clamp((1.6 - ly) / 1.6)                 # in the shadow of the hoodie hem
        if f == outer_face(ctx):
            if abs(lz - d / 2.0) < 0.5:
                return pick(JOG, v - 0.1)                   # side seam
            v += folds(ctx, FOLD_THIGH_SIDE)
        elif f == 'front':
            v += folds(ctx, FOLD_THIGH_FRONT)
            if ctx.i in (2, 3) and ly < 7:
                v += 0.025                                  # the front of the thigh catches the light
            smears = SMEAR_L if sd > 0 else SMEAR_R
            if (ctx.i, ctx.j) in smears:
                return mix(pick(JOG, v), ORANGE[2], smears[(ctx.i, ctx.j)])
        elif f == 'back':
            v += folds(ctx, FOLD_THIGH_BACK)
        else:
            v -= 0.08
        return pick(JOG, v)
    if t == 'shin':
        if f in ('top', 'bottom'):
            return JOG[1]
        v += folds(ctx, FOLD_SHIN, crease=0.1, ridge=0.06)  # bunched over the cuff
        if f == inner_face(ctx):
            v -= 0.07
        return pick(JOG, v)
    if t == 'jcuff':
        if f == 'bottom':
            return JOG[0]
        if f == 'top':
            return JOG[1]
        return pick(JOG, rib(ctx, v - 0.1))
    return pick(JOG, v)


# sneaker side, 3 rows x 9 (lz 0 = toe .. 8 = heel): g grey toe box, R / r red swoosh (lit / shade), c collar
SHOE_SIDE = [
    "gg...rRcc",
    "ggg.rR...",
    "gggrR....",
]


def shoe_mat(ctx):
    t = tag(ctx)
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    v = 0.74 + face_light(ctx) * 0.8
    if t == 'sole':
        if f == 'bottom':
            v2 = 0.12 + (0.06 if (ctx.i + ctx.j) % 3 == 0 else 0.0)
            return pick(PLASTIC, v2 + 0.3)                  # grey treads
        if f == 'top':
            return pick(WHITE, 0.62)
        if ly > h - 1.0:
            return pick(PLASTIC, 0.62 + (0.05 if h2(ctx.i, 2, 81) > 0.7 else 0.0))   # grey outsole edge
        return pick(WHITE, v - 0.02 - (0.05 if h2(ctx.i, 4, 85) > 0.85 else 0.0))
    if t == 'upper':
        if f == 'bottom':
            return WHITE[3]
        if f == 'back':
            # red heel tab
            if abs(lx - w / 2.0) < 1.6:
                return pick(RED, 0.6 + face_light(ctx))
            return pick(WHITE, v - 0.05)
        if f == 'front':
            return pick(WHITE, v - 0.12 - (0.06 if ly < 1 else 0.0))   # grey toe box
        if f == 'top':
            # perforated grey toe box, then the lacing: eyelets on both edges, a lace bar every other row
            if lz < 2.5:
                return pick(WHITE, v - 0.14 - (0.06 if (ctx.i + int(lz)) % 2 == 0 and 1 <= ctx.i <= w - 2 else 0.0))
            k = int(math.floor(lz))
            if ctx.i in (0, w - 1):
                return pick(WHITE, v - 0.04)
            if ctx.i in (1, w - 2):
                return PLASTIC[5] if k % 2 == 0 else pick(WHITE, v - 0.02)   # eyelets
            return WHITE[8] if k % 2 == 1 else WHITE[4]               # lace bars over the grey tongue
        # sides (lz 0 = toe on both): grey toe panel, one bold red swoosh stepping up toward the heel, white quarter
        ch = SHOE_SIDE[min(2, int(ly))][min(8, int(lz))]
        if ch == 'g':
            return pick(WHITE, v - 0.14)
        if ch == 'R':
            return pick(RED, 0.62 + face_light(ctx))
        if ch == 'r':
            return pick(RED, 0.4 + face_light(ctx))
        if ch == 'c':
            return pick(WHITE, v - 0.06)                    # collar padding
        return pick(WHITE, v)
    if t == 'shoe_tongue':
        if f == 'top':
            return pick(RED, 0.55) if 1 <= ctx.i <= 2 else pick(WHITE, 0.66)   # pull tab
        if f == 'front':
            if ctx.j == 0:
                return pick(RED, 0.55) if 1 <= ctx.i <= 2 else pick(WHITE, v - 0.04)   # red tongue tag
            return WHITE[8] if 0 < ctx.i < w - 1 else PLASTIC[5]  # top lace bar + eyelets
        return pick(WHITE, v - 0.07)
    if t == 'lace':
        if f not in ('west', 'east'):
            return None
        if (ctx.i + ctx.j) % 3 == 2 and ctx.j > 0:
            return None
        return WHITE[7] if ctx.j < 2 else WHITE[5]
    return pick(WHITE, v)


# ------------------------------------------------------------------ headset + mic
def headset_mat(ctx):
    t = tag(ctx)
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    sd = side_of(ctx)
    v = 0.36 + face_light(ctx) * 1.2
    if edge(ctx) == 0:
        v += 0.08                                           # crisp lit rims on the matte plastic
    if t == 'band':
        if f == 'top':
            if abs(lz - d / 2.0) < 0.6:
                hue = 0.5 + 0.45 * (lx / w)
                return hsv(hue, 0.85, 0.9)                  # LED strip
            return pick(PLASTIC, v + 0.05)
        if f == 'bottom':
            return pick(CUSHION, 0.45)
        return pick(PLASTIC, v)
    if t == 'slider':
        if f in ('west', 'east', 'front', 'back') and ctx.j in (2, 4):
            return STEEL[0]                                 # size notches on the slider
        return pick(STEEL, 0.18 + face_light(ctx) * 0.8)
    if t == 'cup':
        if f in ('front', 'back') and (ctx.i == (0 if sd < 0 else w - 1)) and 1 <= ctx.j <= h - 2:
            ang = 3.1 if f == 'front' else 0.0
            return hsv(ring_hue(sd, ang + (ctx.j - h / 2.0) * 0.2), 0.8, 0.85)   # LED edge strip
        if f == outer_face(ctx):
            return pick(PLASTIC, v - 0.04)
        if f == inner_face(ctx):
            return PLASTIC[1]
        return pick(PLASTIC, v - 0.04)
    if t == 'plate':
        if f == outer_face(ctx):
            cy, cz = (h - 1) / 2.0, (w - 1) / 2.0
            e = edge(ctx)
            ang = math.atan2(ctx.j - cy, ctx.i - cz)
            if e == 0:
                return hsv(ring_hue(sd, ang), 0.85, 0.95)
            if logo_px(ctx.i, ctx.j):
                return hsv(ring_hue(sd, ang + 1.5), 0.55, 0.55)
            return PLASTIC[2] if e == 1 else PLASTIC[3]             # dark smoked plate, recessed edge
        if f == inner_face(ctx):
            return PLASTIC[1]
        # the ring's thickness glows too
        ang = {'top': -1.57, 'bottom': 1.57, 'front': 3.1, 'back': 0.0}.get(f, 0.0)
        ang += (ctx.i - ctx.w / 2.0) * 0.2
        return hsv(ring_hue(sd, ang), 0.8, 0.85)
    if t == 'cushion':
        if f == inner_face(ctx):
            return CUSHION[1]
        v2 = 0.45 + face_light(ctx) + (0.1 if edge(ctx) == 0 else 0.0)
        if f in ('front', 'back', 'top', 'bottom') and ctx.i % 3 == 1:
            v2 -= 0.08                                      # quilted leatherette
        return pick(CUSHION, v2)
    if t == 'boom':
        return pick(PLASTIC, v + 0.02)
    if t == 'mic_tip':
        if f == 'front' and ctx.i == 1 and ctx.j == 0:
            return hx('#ff3a3a')                            # muted LED
        return pick(CUSHION, 0.5 + face_light(ctx) + (0.06 if (ctx.i + ctx.j) % 2 else 0.0))
    return pick(PLASTIC, v)


LOGO = [".....", "#####", ".###.", "..#..", "....."]


def logo_px(i, j):
    a, b = i - 1, j - 1
    return 0 <= a < 5 and 0 <= b < 5 and LOGO[b][a] == '#'


# ------------------------------------------------------------------ gamepad
# Pad body top face, 10 x 5: i = lx 0..9 from his right (-X) to his left (+X), j = 0 at the near edge (toward him) ..
# 4 at the far edge.  Far half: face buttons under his right thumb, touchpad in the middle, d-pad under his left
# thumb; near half: the two sticks (their own cubes, i 2-3 and 6-7, j 0-1) and the glowing home button between them.
BTN = {'tri': hx('#3ce07a'), 'cir': hx('#ff4a5a'), 'crs': hx('#4aa8ff'), 'sqr': hx('#ff7ad8')}
BTN_POS = {(1, 4): 'tri', (0, 3): 'cir', (1, 2): 'crs', (2, 3): 'sqr'}
DPAD = {(8, 2), (7, 3), (8, 3), (9, 3), (8, 4)}


def pad_top_px(i, j):
    if (i, j) in BTN_POS:
        return 'btn', BTN_POS[(i, j)]
    if (i, j) in DPAD:
        return 'dpad', None
    if 4 <= i <= 5 and 3 <= j <= 4:
        return 'touch', None
    if (i, j) == (4, 1) or (i, j) == (5, 1):
        return 'home', None
    return None, None


def pad_mat(ctx):
    t = tag(ctx)
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    v = 0.74 + face_light(ctx) * 0.9
    if edge(ctx) == 0 and f not in ('top',):
        v -= 0.06
    if t == 'pad':
        if f == 'top':
            kd, which = pad_top_px(ctx.i, ctx.j)
            if kd == 'btn':
                return BTN[which]
            if kd == 'dpad':
                return PLASTIC[4]
            if kd == 'touch':
                return pick(WHITE, 0.5)
            if kd == 'home':
                return PLASTIC[5]
            return pick(WHITE, v + 0.04)
        if f == 'front':
            if ctx.j == 0 and 2 <= ctx.i <= w - 3:
                return rgbf(PAD_GLOW, 0.9)                  # light bar
            return pick(WHITE, v - 0.06)
        if f == 'bottom':
            return pick(WHITE, 0.42)
        return pick(WHITE, v - 0.04)
    if t == 'grip':
        if f == 'bottom':
            return pick(WHITE, 0.4)
        return pick(WHITE, v - (0.08 if f in ('west', 'east') else 0.0))
    if t == 'stick':
        if f == 'top':
            return PLASTIC[6] if edge(ctx) == 0 else PLASTIC[4]
        return PLASTIC[3]
    return pick(WHITE, v)


# ------------------------------------------------------------------ mouth
def mouth_mat(ctx):
    t = tag(ctx)
    f = ctx.face
    if t == 'mouth':
        if f != 'front':
            return MOUTH[0]
        # upper teeth row with braces, dark throat, the tongue rising at the bottom
        edge_t = ctx.i in (0, ctx.w - 1)
        if ctx.j == 0:
            return TEETH[1] if edge_t else TEETH[3]         # upper teeth
        if ctx.j == 1:
            if edge_t:
                return MOUTH[1]
            return BRACE if ctx.i % 2 == 1 else BRACE_D     # brackets on the wire
        return TONGUE[1] if 2 <= ctx.i <= ctx.w - 3 else MOUTH[0]
    if t == 'teeth':
        if f not in ('front',):
            return None
        if ctx.j == 0:
            return BRACE if ctx.i % 2 == 0 else BRACE_D     # lower brackets on the wire
        return TEETH[2] if ctx.i in (0, ctx.w - 1) else TEETH[3]
    return MOUTH[1]


KINDS = {'skin': skin_mat, 'hand': hand_mat, 'hair': hair_mat, 'hoodie': hoodie_mat, 'string': string_mat,
         'jogger': jogger_mat, 'shoe': shoe_mat, 'headset': headset_mat, 'pad': pad_mat, 'mouth': mouth_mat}


def toti_mat(ctx):
    return KINDS.get(kind(ctx), hoodie_mat)(ctx)


DEFAULT_MAT = toti_mat
FOCUS = 'head'


# ------------------------------------------------------------------ emissive layer ('eyes')
def glow_face(i, j, w, h):
    if (i, j) in GLINTS:
        return hx('#c8f8ff')
    if 4 <= j and i in (0, 13):
        return rim_glow(-1 if i == 0 else 1, 0.30)
    if 6 <= j and i in (1, 12):
        return rim_glow(-1 if i == 1 else 1, 0.12)
    return None


def glow_cheek_front(sd):
    def fn(i, j, w, h):
        return rim_glow(sd, 0.28) if i == (0 if sd < 0 else w - 1) else None
    return fn


def glow_jaw_bottom(i, j, w, h):
    return rgbf(PAD_GLOW, 0.16 if j > h // 2 else 0.08)


def glow_skull_side(sd):
    def fn(i, j, w, h):
        # west face: i = 0 at the back; east face: i = 0 at the front.  Skin in front of the cup: z < -3.5
        zi = (w - 1 - i) if sd < 0 else i                   # 0 at the front
        if zi <= 2 and j >= 8:
            return rim_glow(sd, 0.26 if zi <= 1 else 0.14)
        return None
    return fn


def glow_jaw_side(sd):
    def fn(i, j, w, h):
        zi = (w - 1 - i) if sd < 0 else i
        if zi <= 3:
            return rim_glow(sd, 0.22 if zi <= 1 else 0.12)
        return None
    return fn


def glow_nose_bottom(i, j, w, h):
    return rgbf(PAD_GLOW, 0.12)


def glow_plate(sd):
    def fn(i, j, w, h):
        cy, cz = (h - 1) / 2.0, (w - 1) / 2.0
        e = min(i, j, w - 1 - i, h - 1 - j)
        ang = math.atan2(j - cy, i - cz)
        if e == 0:
            return hsv(ring_hue(sd, ang), 0.85, 1.0)
        if logo_px(i, j):
            return hsv(ring_hue(sd, ang + 1.5), 0.65, 0.42)
        return None
    return fn


def glow_plate_rim(sd, face):
    def fn(i, j, w, h):
        ang = {'top': -1.57, 'bottom': 1.57, 'front': 3.1, 'back': 0.0}.get(face, 0.0) + (i - w / 2.0) * 0.2
        return hsv(ring_hue(sd, ang), 0.8, 0.8)
    return fn


def glow_cup_edge(sd, face):
    def fn(i, j, w, h):
        if i == (0 if sd < 0 else w - 1) and 1 <= j <= h - 2:
            ang = (3.1 if face == 'front' else 0.0) + (j - h / 2.0) * 0.2
            return hsv(ring_hue(sd, ang), 0.8, 0.9)
        return None
    return fn


def glow_band_top(i, j, w, h):
    if j == h // 2:
        return hsv(0.5 + 0.45 * (i / max(1, w - 1)), 0.85, 0.85)
    return None


def glow_mic(i, j, w, h):
    return hx('#ff2a2a') if (i, j) == (1, 0) else None


def glow_pad_front(i, j, w, h):
    if j == 0 and 2 <= i <= w - 3:
        return rgbf(PAD_GLOW, 1.0)
    if j == 1 and 3 <= i <= w - 4:
        return rgbf(PAD_GLOW, 0.25)
    return None


def glow_pad_top(i, j, w, h):
    kd, which = pad_top_px(i, j)
    if kd == 'btn':
        return BTN[which]
    if kd == 'home':
        return hx('#9fdcff')
    return None


def glow_brace_up(i, j, w, h):
    return rgbf(PAD_GLOW, 0.32) if j == 1 and 1 <= i <= w - 2 and i % 2 == 1 else None   # brackets catch the pad light


def glow_brace_lo(i, j, w, h):
    return rgbf(PAD_GLOW, 0.28) if j == 0 and i % 2 == 0 else None


def glow_fist(i, j, w, h):
    return rgbf(PAD_GLOW, 0.1)


# ------------------------------------------------------------------ rig helpers (FK in the authoring frame)
def _T(p):
    M = np.eye(4)
    M[:3, 3] = p
    return M


def _Rm(rot_deg):
    M = np.eye(4)
    M[:3, :3] = rot_matrix(*[math.radians(a) for a in rot_deg])
    return M


def _fk(chain):
    """chain: [(abs_pivot, rot_deg), ...] root -> bone.  Returns the bone's 4x4 world matrix (rest pose)."""
    M = np.eye(4)
    prev = np.zeros(3)
    for piv, rot in chain:
        M = M @ _T(np.subtract(piv, prev)) @ _Rm(rot)
        prev = np.array(piv, float)
    return M


def _euler_deg(R):
    """Inverse of rot_matrix (Rz @ Ry @ Rx) -> (x, y, z) degrees."""
    y = math.asin(max(-1.0, min(1.0, -R[2][0])))
    x = math.atan2(R[2][1], R[2][2])
    z = math.atan2(R[1][0], R[0][0])
    return math.degrees(x), math.degrees(y), math.degrees(z)


# ------------------------------------------------------------------ rest pose (degrees)
NECK_FWD = 8.0          # gamer neck: head jutted forward
HEAD_DOWN = 6.0          # looking down at the pad
ARM = (-10.0, 0.0, -5.0)         # LEFT upper arm (right mirrored): a little forward, elbow a little out
FOREARM = (-62.0, 34.0, 0.0)     # LEFT forearm: up in front of the belly, angled in toward the pad
PAD_TILT = -38.0         # the pad's face tilted up toward his eyes
WRIST_P = (1.0, 4.5)     # (y, z) of the wrist in the pad frame (x comes out of the arm FK)
MIC_YAW = 40.0
STRING_SWING = 4.0


def build():
    r = Rig()

    def bone(name, pivot, parent=None, rot=(0, 0, 0)):
        return r.bone(name, pivot, parent=parent, rot=rot)

    def box(b, frm, size, kd, name, inflate=0.0, decals=None, sx=1):
        c = r.box(b, frm, size, inflate=inflate, decals=decals)
        c.a0 = tuple(float(v) for v in frm)
        c.kind = kd
        c.name = name
        c.sx = sx
        return c

    # ---------------- body: root at the hips.  Hoodie torso, ribbed hem, kangaroo pocket
    bone('body', (0, 2, 0))
    box('body', (-8, -14, -4), (16, 15, 8), 'hoodie', 'torso')
    box('body', (-8, 1, -4), (16, 2, 8), 'hoodie', 'hem', inflate=0.3)
    box('body', (-5, -3, -5), (10, 4, 1), 'hoodie', 'pocket')

    # ---------------- hood (down): rolled collar round the neck, lined in acid green, hood lying on the back
    bone('hood', (0, -14, 2), 'body')
    box('hood', (-6, -17, 1), (12, 4, 4), 'hoodie', 'collar_back')
    box('hood', (-7, -16, -3), (3, 3, 4), 'hoodie', 'collar_side', sx=-1)
    box('hood', (4, -16, -3), (3, 3, 4), 'hoodie', 'collar_side', sx=1)
    box('hood', (-6, -13, 4), (12, 7, 2), 'hoodie', 'drape')
    box('hood', (-4, -6, 4), (8, 3, 2), 'hoodie', 'drape_tip')

    # ---------------- drawstrings
    for side, sx in (('right', -1), ('left', 1)):
        sb = f'{side}_string'
        bone(sb, (1.5 * sx, -14, -4.5), 'body', rot=(0, 0, STRING_SWING * sx))
        box(sb, (1.5 * sx - 0.5, -14, -5), (1, 6, 1), 'string', 'string', sx=sx)

    # ---------------- neck + head
    bone('neck', (0, -14, 0.5), 'body', rot=(NECK_FWD, 0, 0))
    box('neck', (-2.5, -18, -2), (5, 4, 5), 'skin', 'neck')
    bone('head', (0, -17.5, 0.5), 'neck', rot=(HEAD_DOWN, 0, 0))
    box('head', (-7, -32, -7), (14, 11, 13), 'skin', 'skull',
        decals={'eyes:front': glow(glow_face), 'eyes:west': glow(glow_skull_side(-1)),
                'eyes:east': glow(glow_skull_side(1))})
    box('head', (-1, -26, -8), (2, 3, 1), 'skin', 'nose', decals={'eyes:bottom': glow(glow_nose_bottom)})
    box('head', (-3, -21, -6.6), (6, 3, 4), 'mouth', 'mouth', decals={'eyes:front': glow(glow_brace_up)})
    for sx in (-1, 1):                                      # lower cheeks either side of the chin: the mouth opens
        cx0 = -6 if sx < 0 else 3                           # between them, not across the whole face
        box('head', (cx0, -21, -7), (3, 4, 10), 'skin', 'cheek', sx=sx,
            decals={'eyes:front': glow(glow_cheek_front(sx)), 'eyes:bottom': glow(glow_jaw_bottom),
                    ('eyes:west' if sx < 0 else 'eyes:east'): glow(glow_jaw_side(sx))})
    box('head', (-7, -32, -7), (14, 8, 13), 'hair', 'shell', inflate=0.5)
    box('head', (-7, -24, 1), (14, 5, 5), 'hair', 'nape', inflate=0.5)
    box('head', (-5, -34, -6.5), (3, 2, 3), 'hair', 'tuft', sx=-1)           # messy lock in front of the band
    box('head', (1, -33.5, -6), (2, 1, 2), 'hair', 'tuft', sx=1)
    box('head', (0.5, -33.6, 3.5), (2, 2, 2), 'hair', 'tuft', sx=1)          # cowlick at the crown
    box('head', (-7.5, -32, 3), (1, 2, 3), 'hair', 'tuft', sx=-1)            # sticking out over the right cup
    box('head', (-7.6, -30, -7.6), (0, 7, 3), 'hair', 'lock', sx=-1)

    bone('fringe', (0, -32.5, -8), 'head')
    box('fringe', (-7.5, -33, -8.5), (15, 3, 1), 'hair', 'fringe_root')
    box('fringe', (-8, -31, -8.3), (16, 7, 0), 'hair', 'fringe_tips')

    bone('jaw', (0, -21, 2), 'head')
    box('jaw', (-3, -21, -7), (6, 4, 11), 'skin', 'jaw', decals={'eyes:bottom': glow(glow_jaw_bottom)})
    box('jaw', (-3, -22.8, -6.75), (6, 2, 0), 'mouth', 'teeth', decals={'eyes:front': glow(glow_brace_lo)})
    bone('tongue', (2.5, -21, -5), 'jaw')
    box('tongue', (1.5, -21.6, -6.5), (2, 1, 3), 'skin', 'tongue')

    # ---------------- headset: band, sliders, cups with RGB plates, cushions; boom mic on the left cup
    bone('headphones', (0, -33, 0.5), 'head')
    box('headphones', (-9, -33.9, -1.5), (18, 2, 4), 'headset', 'band', decals={'eyes:top': glow(glow_band_top)})
    for sx in (-1, 1):
        x_in = 8 if sx > 0 else -11                          # cup min-x
        box('headphones', ((8.5 if sx > 0 else -10.5), -33.5, -1), (2, 6, 3), 'headset', 'slider', sx=sx)
        box('headphones', (x_in, -28, -4), (3, 9, 9), 'headset', 'cup', sx=sx,
            decals={'eyes:front': glow(glow_cup_edge(sx, 'front')), 'eyes:back': glow(glow_cup_edge(sx, 'back'))})
        px0 = 11 if sx > 0 else -12
        dec = {('eyes:east' if sx > 0 else 'eyes:west'): glow(glow_plate(sx))}
        for fc in ('top', 'bottom', 'front', 'back'):
            dec['eyes:' + fc] = glow(glow_plate_rim(sx, fc))
        box('headphones', (px0, -27, -3), (1, 7, 7), 'headset', 'plate', sx=sx, decals=dec)
        box('headphones', ((7 if sx > 0 else -8), -27, -3), (1, 7, 7), 'headset', 'cushion', sx=sx)
    bone('mic', (9.5, -21.5, -3.5), 'headphones', rot=(10, MIC_YAW, 0))
    box('mic', (9, -22, -8.5), (1, 1, 5), 'headset', 'boom')
    box('mic', (8.5, -22.5, -10.5), (2, 2, 2), 'headset', 'mic_tip', decals={'eyes:front': glow(glow_mic)})

    # ---------------- arms (bind: hanging straight), rest rotations mirrored; hands aligned to the pad frame
    arm_rot = {1: ARM, -1: (ARM[0], -ARM[1], -ARM[2])}
    fa_rot = {1: FOREARM, -1: (FOREARM[0], -FOREARM[1], -FOREARM[2])}
    for side, sx in (('right', -1), ('left', 1)):
        arm, fa = f'{side}_arm', f'{side}_forearm'
        ax = 10.5 * sx
        bone(arm, (ax, -12.5, 0), 'body', rot=arm_rot[sx])
        box(arm, (ax - 2.5, -14, -2.5), (5, 10, 5), 'hoodie', 'sleeve', sx=sx)
        bone(fa, (ax, -4.5, 0), arm, rot=fa_rot[sx])
        box(fa, (ax - 2, -5, -2), (4, 7, 4), 'hoodie', 'forearm', sx=sx)
        box(fa, (ax - 2, 1, -2), (4, 2, 4), 'hoodie', 'cuff', sx=sx, inflate=0.35)

    # FK: where do the wrists land, and which hand rotation squares each fist to the pad?
    M_fa = _fk([((0, 2, 0), (0, 0, 0)), ((10.5, -12.5, 0), ARM), ((10.5, -4.5, 0), FOREARM)])
    wrist_w = (M_fa @ np.array([0.0, 7.5, 0.0, 1.0]))[:3]
    R_pad = rot_matrix(math.radians(PAD_TILT), 0, 0)
    hand_rot = _euler_deg(M_fa[:3, :3].T @ R_pad)
    gx = float(wrist_w[0])
    WY, WZ = WRIST_P
    PADP = {}

    def pbone(name, p, parent, rot=(0, 0, 0)):
        """Bone whose pivot is given in pad-frame coordinates p (parent frame aligned with the pad)."""
        pa = r.abs_pivot[parent]
        pp = PADP[parent]
        b = bone(name, tuple(pa[i] + p[i] - pp[i] for i in range(3)), parent, rot=rot)
        PADP[name] = tuple(float(v) for v in p)
        return b

    def pbox(b, p_frm, size, kd, name, sx=1, inflate=0.0, decals=None):
        pa = r.abs_pivot[b]
        pp = PADP[b]
        return box(b, tuple(pa[i] + p_frm[i] - pp[i] for i in range(3)), size, kd, name, sx=sx,
                   inflate=inflate, decals=decals)

    for side, sx in (('right', -1), ('left', 1)):
        hb = f'{side}_hand'
        wrist_abs = (10.5 * sx, 3.0, 0.0)
        hr = hand_rot if sx > 0 else (hand_rot[0], -hand_rot[1], -hand_rot[2])
        bone(hb, wrist_abs, f'{side}_forearm', rot=hr)
        PADP[hb] = (gx * sx, WY, WZ)
        # fist round the grip: palm on the outside (back of the hand out), fingers wrapping under the grip
        px_out = gx * sx                                    # palm centre x in the pad frame
        pbox(hb, (px_out - 1.0, -1.0, 0.5), (2, 4, 4), 'hand', 'palm', sx=sx,
             decals={'eyes:' + ('east' if sx < 0 else 'west'): glow(glow_fist)})
        fb = f'{side}_fingers'
        pbone(fb, (px_out - 1.0 * sx, 3.0, 2.5), hb)
        f0 = px_out - 4.0 if sx > 0 else px_out + 1.0
        pbox(fb, (f0, 2.0, 0.5), (3, 2, 4), 'hand', 'fingers', sx=sx)
        tb = f'{side}_thumb'
        pbone(tb, (px_out - 1.0 * sx, -2.0, 2.5), hb, rot=(0, 0, 0))
        t0 = px_out - 5.0 if sx > 0 else px_out + 1.0
        pbox(tb, (t0, -3.0, 1.5), (4, 1, 2), 'hand', 'thumb', sx=sx)

    # gamepad: centre of the pad frame, child of the left hand
    pbone('gamepad', (0.0, 0.0, 0.0), 'left_hand')
    pbox('gamepad', (-5, -1.5, -2.5), (10, 3, 5), 'pad', 'pad',
         decals={'eyes:front': glow(glow_pad_front), 'eyes:top': glow(glow_pad_top)})
    for sx in (-1, 1):
        g0 = 4 if sx > 0 else -7
        pbox('gamepad', (g0, -0.5, -0.5), (3, 3, 5), 'pad', 'grip', sx=sx)
        s0 = 1.0 if sx > 0 else -3.0
        pbox('gamepad', (s0, -2.5, 0.5), (2, 1, 2), 'pad', 'stick', sx=sx)

    # ---------------- legs: joggers + chunky sneakers
    for side, sx in (('right', -1), ('left', 1)):
        leg, shin, foot = f'{side}_leg', f'{side}_shin', f'{side}_foot'
        lx = 3.5 * sx
        bone(leg, (lx, 3, 0), 'body')
        box(leg, (lx - 3, 2, -3), (6, 10, 6), 'jogger', 'thigh', sx=sx)
        bone(shin, (lx, 12, 0), leg)
        box(shin, (lx - 2.5, 12, -2.5), (5, 6, 5), 'jogger', 'shin', sx=sx)
        box(shin, (lx - 2.5, 17, -2.5), (5, 2, 5), 'jogger', 'jcuff', sx=sx, inflate=0.4)
        bone(foot, (lx, 19, 0), shin)
        box(foot, (lx - 3, 19, -6), (6, 3, 9), 'shoe', 'upper', sx=sx)
        box(foot, (lx - 3.5, 22, -6.5), (7, 2, 10), 'shoe', 'sole', sx=sx)
        box(foot, (lx - 2, 17.5, -4), (4, 2, 2), 'shoe', 'shoe_tongue', sx=sx)
    box('right_foot', (-7.1, 21, -5), (0, 3, 3), 'shoe', 'lace', sx=-1)

    m = Model('toti', 256, 128, r.roots)
    m.scale = 0.5
    m.pad_info = {'gx': gx, 'wrist': wrist_w.tolist(), 'hand_rot': hand_rot}
    return m


POSES = {
    'crouch_closet': {
        'body': (0.489, 0, 0, 0, 12.272, 3.899),
        'right_leg': (-2.234, 0, -0.12, 0, 0, 0),
        'right_shin': (2.443, 0, 0, 0, 0, 0),
        'right_foot': (-0.698, 0, 0.12, 0, 0, 0),
        'left_leg': (-2.234, 0, 0.12, 0, 0, 0),
        'left_shin': (2.443, 0, 0, 0, 0, 0),
        'left_foot': (-0.698, 0, -0.12, 0, 0, 0),
        'neck': (-0.28, 0, 0, 0, 0, 0),
        'head': (-0.12, 0, 0, 0, 0, 0),
        'left_arm': (-1.047, 0.073, 0.342, 0, 0, 0),
        'left_forearm': (-0.322, -0.196, 0.094, 0, 0, 0),
        'left_hand': (0.973, 0.563, 0.3, 0, 0, 0),
        'right_arm': (-1.047, -0.073, -0.342, 0, 0, 0),
        'right_forearm': (-0.322, 0.196, -0.094, 0, 0, 0),
        'right_hand': (0.973, -0.563, -0.3, 0, 0, 0),
        'jaw': (0.07, 0, 0, 0, 0, 0),
        'tongue': (0.3, 0, 0.35, 0, 0.6, -1.8),
        'left_thumb': (0, 0, 0.12, 0, 0, 0),
    },
    'slam': {
        'body': (0.489, 0, 0, 0, 12.272, 3.899),
        'right_leg': (-2.234, 0, -0.12, 0, 0, 0),
        'right_shin': (2.443, 0, 0, 0, 0, 0),
        'right_foot': (-0.698, 0, 0.12, 0, 0, 0),
        'left_leg': (-2.234, 0, 0.12, 0, 0, 0),
        'left_shin': (2.443, 0, 0, 0, 0, 0),
        'left_foot': (-0.698, 0, -0.12, 0, 0, 0),
        'neck': (-0.28, -0.12, 0, 0, 0, 0),
        'head': (-0.06, -0.42, 0.1, 0, 0, 0),
        'left_arm': (-0.97, 0.036, 0.298, 0, 0, 0),
        'left_forearm': (-0.347, -0.189, 0.111, 0, 0, 0),
        'left_hand': (0.973, 0.545, 0.263, 0, 0, 0),
        'right_arm': (-0.984, 0.786, 0.657, 0, 0, 0),
        'right_forearm': (0.1, 0.367, 0.261, 0, 0, 0),
        'right_hand': (-0.971, -0.814, 0.892, 0, 0, 0),
        'right_fingers': (0, 0, 1.571, 0, 0, 0),
        'right_thumb': (0, 0, -0.35, 0, 0, 0),
        'jaw': (0.34, 0, 0, 0, 0, 0),
        'left_thumb': (0, 0, 0.2, 0, 0, 0),
        'fringe': (-0.12, 0, 0, 0, 0, 0),
        'right_string': (0.3, 0, 0.25, 0, 0, 0),
        'left_string': (0.25, 0, 0.1, 0, 0, 0),
    },
    'stand': {
        'neck': (-0.16, 0, 0, 0, 0, 0),
        'head': (-0.16, 0.12, 0.14, 0, 0, 0),
        'jaw': (0.12, 0, 0, 0, 0, 0),
        'left_arm': (0.316, 0.035, -0.107, 0, 0, 0),
        'left_forearm': (0.359, 0.074, -0.156, 0, 0, 0),
        'left_hand': (-2.999, 0.73, -0.863, 0, 0, 0),
        'right_arm': (0.161, 0.245, 0.313, 0, 0, 0),
        'right_forearm': (-0.373, 0.198, -0.123, 0, 0, 0),
        'right_hand': (2.961, 0.91, 3.004, 0, 0, 0),
        'right_fingers': (0, 0, 1.571, 0, 0, 0),
        'right_thumb': (0, 0, -0.5, 0, 0, 0),
        'body': (-0.04, 0, 0, 0, 0, 0),
        'right_leg': (0.04, 0, 0, 0, 0, 0),
        'left_leg': (0.04, 0, 0, 0, 0, 0),
    },
}

ANIM_NOTES = """
Toti -- animation contract.  Angles in radians, ADDED to the rest pose; offsets (dx, dy, dz) in model texels at 2x
density (inside scale_root: 2 texels = 1 vanilla pixel), in the PARENT bone's space.  t = ageInTicks.  28 bones,
69 cubes, texture 256 x 128 (+ toti_eyes.png).  No variants (one look), no toggles (see the end).  Poses (exported as
POSE_CROUCH_CLOSET / POSE_SLAM / POSE_STAND): crouch_closet, slam, stand -- every value quoted is the table's.

CHARACTER: never stops playing.  Every idle / walk animation keeps both fists on the pad (the rest pose IS "standing
and playing"); he only lets go with the right hand to slam the door (slam) or to shrug at breakfast (stand).  He
never looks at anything but the screen except in stand.  Motion is small and twitchy (gamer reflexes): thumbs never
stop, the head flinches with the game, the body barely moves.

EMISSIVE LAYER ('eyes', RenderTypes.eyes = additive, full-bright): the RGB ring on each cup's outer plate (+ its
1-texel rim and an LED strip on the cups' front / back edges: cyan -> violet on his right, magenta -> pink on his
left), the chevron logos, the headband's LED strip, the red "muted" LED on the mic tip, the pad's cyan light bar and
its four face buttons + home button, the two SCREEN GLINTS in his eyes, and the dim RIM LIGHT the cups throw on his
face (outer face columns, cheeks in front of the cups, jaw edges: cyan right / magenta left) plus the pad's cyan
under-glow on the jaw's underside, the nose's underside, the inner faces of the fists and the braces' brackets.  In
the dark wardrobe that layer IS the scare: two coloured rings, two pin-point eyes and a face lit from below.
Suggested: pulse the layer 0.85..1.0 with sin(t * 0.12) ("breathing" RGB); spike it to 1.0 for 2 ticks on every
in-game "kill" beat while idling; drop it to 0.6 while he talks to the player at breakfast.

PLACEMENT (beat casa.ropero): the crouch spans x -13.7..13.7, z -20.4 (pad / face) .. +8.3 (hood), top y -21.4
(1.42 blocks) above the floor, soles exactly on y 24.  In the 2 x 1 x 3 wardrobe put the entity origin ~0.3 block in
front of the back wall, facing the doors; slam reaches 19.9 texels (0.62 block) to his right and 20.9 forward -- put
the door that slams on his RIGHT-front.

BODY / CLOTHES
* body -- ROOT at the hips (pivot 0, 2, 0): hoodie torso (with the "GG" print), ribbed hem, kangaroo pocket.  Idle:
  breathing xRot sin(t*0.08)*0.012; every 3-6 s a tiny flinch with the game (xRot -0.03 over 2 ticks, back over 6).
  Walk: no arm swing (he plays while walking), bob dy = abs(sin(walk))*0.5*s, zRot sin(walk)*0.03*s.
  crouch_closet / slam: (0.489, dy 12.272, dz 3.899) -- the squat: hips drop 12.3, back 3.9 (over the heels), torso
  pitched 28 deg over the knees.  stand: xRot -0.04 (leans back, relaxed; legs +0.04 keep the soles flat).
* hood -- the hood lying down: rolled collar round the neck (acid-green lining), the hood on his back.  Secondary:
  lags the body pitch by 3 ticks (xRot += -0.4 * d(body xRot)), clamp +-0.15; small bounce on footfalls.
* right_string / left_string -- hoodie drawstrings (white, green aglets), rest zRot -+4 deg.  Pendulums: zRot
  sin(t*0.1 + side)*0.06, xRot follows body pitch changes with lag (keep them hanging: xRot ~= -body xRot when he
  crouches -- not needed in the tables, they read fine pressed on the chest); slam: right (0.3, 0, 0.25), left
  (0.25, 0, 0.1) -- flung by the shove.
* neck -- rest xRot 8 deg (gamer neck).  Takes 30 % of head-look.  crouch_closet -0.28 / slam (-0.28, yaw -0.12)
  straighten it so the face stays readable over the pad; stand -0.16.
* head -- FOCUS bone: skull + face, nose, the two static lower cheeks, mouth interior (upper teeth with BRACES),
  hair shell, nape, 4 tufts, the temple lock.  Rest xRot 6 deg (looking down at the pad).  Head-look only in stand
  (otherwise his eyes stay on the screen: clamp yaw +-0.2 while playing).  Gameplay twitches: every 2-4 s a quick tilt
  zRot +-0.08 (dodging in the game) over 2 ticks, back over 5.  crouch_closet -0.12; slam (-0.06, -0.42, 0.1) = turned
  AWAY from the door, eyes still on the game; stand (-0.16, 0.12, 0.14) = looks up at the player, head tilted:
  "¿Qué me perdí?".
* fringe -- the greasy fringe (solid root + cut-out strand plane over the eyes).  Secondary: xRot lags the head
  pitch (spring, 0.1 amplitude), flicks -0.12 on the slam jolt (table value) and settles over 8 ticks.  Never rotate
  it positive by more than 0.05 (it would clip into the forehead).
* jaw -- the 6-wide chin between the lower cheeks (lower lip, lower teeth with braces), hinge behind the mouth at
  (0, -21, 2).  Voice-driven: xRot = amp * 0.3 (max 0.36).  Rest closed (pouting lower lip).
  crouch_closet 0.07 (mouth-breathing, tongue out); slam 0.34 = yelling "¡Callate, Chori!" (braces glint: the
  brackets carry pad-glow pixels on the emissive layer); stand 0.12 = "¿Qué me perdí?".  "¡OCUPADO! ¡ESTOY EN
  RANKED!" = four fast opens 0.3 / 0.15 / 0.34 / 0.2, 3 ticks each.
* tongue -- parked INSIDE the closed mouth (never visible at rest).  crouch_closet (0.3, 0, 0.35, dy 0.6, dz -1.8):
  slides out of the LEFT corner of the mouth onto the lower lip (concentration).  While out: zRot wiggle
  sin(t*0.5)*0.12 when he is "clutching".  Slide it in (dz back to 0) before any jaw open > 0.15.

HEADSET (all children of head)
* headphones -- band (LED strip), steel sliders, two big cups with RGB plates, leatherette cushions.  Rigid with the
  head: no animation.  (If he ever takes them off at breakfast: dy -6 over 6 ticks then hide; not in the tables.)
* mic -- boom mic on the LEFT cup, rest (10, 40, 0) deg: the foam tip sits at the left corner of his mouth, red
  muted LED.  Idle: nothing.  When he yells, push it 0.1 xRot away (spit) and back.  Can flip up: xRot -1.3.

ARMS -- right_* is -X.  The rest pose holds the pad in front of the belly: upper arms (-10, 0, -+5) deg, forearms
(-62, +-34, 0) deg; the hand rest rotations ((37.8, -+20.1, -+29.5) deg) are COMPUTED so both fists are square to the
pad.  The arms and hands are mirror images, so ANY symmetric arm animation (left values, right = (x, -y, -z)) keeps
the right fist on the right grip (measured gap 0.0).  Never rotate the gamepad, one forearm, or both forearms the
same way while the right hand holds the pad: an asymmetric 0.05 on the forearms already opens a 1.1-texel gap at the
right grip.  To fake "steering" tilt the head (zRot +-0.12) and roll the whole body (zRot <= +-0.03: fists stay on
the pad, the soles move < 0.25 texel).
* right_arm / left_arm -- sleeves (shoulder pivot).  Walk: no swing; tiny bob xRot sin(walk)*0.04*s (mirrored).
* right_forearm / left_forearm -- forearm + ribbed cuff (elbow pivot).
* right_hand / left_hand -- fists round the grips (palm on the outside of the grip, back of the hand out).
* right_fingers / left_fingers -- the four fingers wrapping under the grip (one block, pivot at the palm's lower
  inner corner).  zRot +pi/2 (1.571, table value, RIGHT hand) straightens them into an open flat hand: slam (the
  shove) and stand (palm up).  Left fingers never open (they hold the pad).
* right_thumb / left_thumb -- thumbs on the sticks.  NEVER still while he plays: alternate zRot sin(t*0.9)*0.12 and
  sin(t*1.3 + 1)*0.1, plus random 2-tick "mashes" of -0.25.  crouch_closet left 0.12; slam left 0.2, right -0.35
  (spread out of the shove); stand right -0.5.
* gamepad -- child of left_hand (pad frame = hand frame): white body with the cyan light bar, two grips, two sticks.
  Rides the left hand: in stand it dangles from his left fist by the grip, beside the leg.

Pose values for the arms come from IK: crouch_closet holds the pad up under his face (left arm (-1.047, 0.073,
0.342), forearm (-0.322, -0.196, 0.094), hand (0.973, 0.563, 0.3); right = mirrored); slam keeps the left side
(-0.97, 0.036, 0.298) / (-0.347, -0.189, 0.111) / (0.973, 0.545, 0.263) and throws the right arm straight out to the
right-front at shoulder height, palm forward, fingers up: arm (-0.984, 0.786, 0.657), forearm (0.1, 0.367, 0.261),
hand (-0.971, -0.814, 0.892), fingers 1.571; stand: left arm hangs (0.316, 0.035, -0.107) / (0.359, 0.074, -0.156) /
hand (-2.999, 0.73, -0.863), right forearm forward palm up (0.161, 0.245, 0.313) / (-0.373, 0.198, -0.123) / hand
(2.961, 0.91, 3.004), fingers 1.571.  The hand deltas in stand are large (the wrist turns over): blend into stand
over >= 8 ticks (or slerp the hand rotations).

LEGS -- joggers + chunky sneakers.  right_leg / left_leg (hip), right_shin / left_shin (knee), right_foot /
left_foot (ankle; the sneaker, puffy tongue, the right shoe's untied lace).  Walk: thigh xRot +-sin(walk)*0.6*s,
shin xRot max(0, -sin(walk))*0.5*s (knee bend on the back swing), foot counter-rotates -shin*0.6.
crouch_closet / slam: thighs (-2.234, 0, -+0.12) = pointing up-forward (knees spread a little), shins 2.443, feet
(-0.698, 0, +-0.12) = soles flat on the floor (verified: lowest point y 24.0 in both poses).

TRANSITIONS
* enter the wardrobe beat: Toti is already IN crouch_closet (spawned that way, eyes layer on).  "¡OCUPADO!": jaw
  sequence above, head snaps 0.15 toward the player for 4 ticks and back to the screen.
* crouch_closet -> slam -> crouch_closet: the two tables share the body / legs / feet / neck pitch, so the blend only
  moves the right arm, the head, the jaw, the fringe and the strings.  Snap INTO slam in 3 ticks (the shove), hold 6
  ticks (door.slam on tick 3), ease back over 10 ticks; the right thumb returns to the stick last.
* stand (beat casa.desayuno, "¿Qué me perdí?"): he steps out of the wardrobe from the rest pose; blend rest -> stand
  over 10 ticks; talk with the jaw; return to rest (playing) when the dialogue ends.

TOGGLES: none.  One look, no variant textures, no geometry that switches on or off: the tongue and the mouth
interior / braces are always present and simply hidden inside the closed mouth (the poses and the jaw reveal them).
"""
