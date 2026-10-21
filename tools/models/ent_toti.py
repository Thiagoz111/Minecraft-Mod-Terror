"""Toti Morales (15) -- the gamer son in the wardrobe (DEAD LINE, case 'casa', beats casa.ropero / casa.desayuno).

(docstring finalised below, see DOC)
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
HAIR = H('#070504', '#0e0907', '#160f0b', '#20160f', '#2b1e15', '#38271b', '#473222', '#58402c', '#6d5038',
         '#866449')
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
SCLERA = hx('#eae2de')
SCLERA_S = hx('#c4b4b2')
IRIS_RIM = hx('#2a150c')
IRIS_L = hx('#8a5530')
PUPIL = hx('#0d0605')
GLINT = hx('#f4feff')
LASH = hx('#24120f')
BAG = hx('#6a4a72')
PIMPLE = hx('#de7f86')

# RGB light
RIM_R = (0.25, 0.92, 1.00)            # cyan rim on his right (-X, viewer's left)
RIM_L = (1.00, 0.20, 0.82)            # magenta rim on his left (+X, viewer's right)
PAD_GLOW = (0.40, 0.92, 1.00)         # the pad's light / the screen
SCREEN = (0.80, 0.95, 1.00)           # cold white reflection of the screen in the eyes


def hsv(h, s, v, a=255):
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, s, v)
    return (int(r * 255), int(g * 255), int(b * 255), a)


def rgbf(c, k, a=255):
    return (min(255, int(c[0] * 255 * k)), min(255, int(c[1] * 255 * k)), min(255, int(c[2] * 255 * k)), a)


def ring_hue(side, ang):
    """Hue of the RGB ring at angle ang (radians) round a cup.  Right cup cyan->blue->violet, left magenta->pink."""
    t = 0.5 + 0.5 * math.sin(ang)
    if side < 0:
        return 0.50 + 0.24 * t                       # cyan .. violet
    return 0.83 + 0.13 * t                           # magenta .. pink-red


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


class Light:
    """Accumulates additive light contributions for one emissive texel."""
    def __init__(self):
        self.c = [0.0, 0.0, 0.0]

    def add(self, col, k):
        if k > 0:
            for n in range(3):
                self.c[n] += col[n] * k
        return self

    def rgba(self, floor=0.012):
        if max(self.c) < floor:
            return None
        return (min(255, int(self.c[0] * 255)), min(255, int(self.c[1] * 255)), min(255, int(self.c[2] * 255)), 255)


# ------------------------------------------------------------------ the face
# Skull front 16 x 12: col c <-> x [-8 + c, -7 + c], row r <-> y [-33 + r, -32 + r].  The fringe root covers rows
# 0-2, its strands hang in front of rows 2-6 (one lock over his right eye's outer corner, one down the nose bridge);
# the brow bones sit over rows 3-4 (cols 1-5 / 10-14); the nose cube over cols 7-8, rows 7-9.
#   0-9 skin ramp   h hairline   k lid crease   L lash line   w / W sclera (lid shadow / lit)   g screen glint (emissive)
#   R iris rim   K pupil   i lit lower iris   d sleepless bag (2 texels)   c cheekbone   f peach fuzz   s philtrum
#   P pimple (a single pink dot)   M mouth corner   m mouth line   x under-lip shade   v / V lower lip   U chin undercut
FACE = [
    # 0123456789ABCDEF
    "hhhhhhhhhhhhhhhh",   # r0  y-33  hairline (under the fringe root)
    "5678888888888765",   # r1  y-32  forehead (under the root)
    "5678888888888765",   # r2  y-31  forehead (behind the strands)
    "5667777777777665",   # r3  y-30  shadow of the fringe (the brows cover cols 1-5 / 10-14)
    "5667777887777665",   # r4  y-29  (brows)
    "5kLLLL7777LLLLk5",   # r5  y-28  lash lines, flicked out at the outer corners
    "56wgRw7887wgRw65",   # r6  y-27  eyes: sclera in the lid's shadow, screen glint (emissive), dark iris rim
    "56WKKW7887WKKW65",   # r7  y-26  pupils (centred: he looks wherever the head points)
    "56WiiW7887WiiW65",   # r8  y-25  lit lower iris
    "567dd778877dd765",   # r9  y-24  two-texel sleepless bags under the irises
    "5678c8fssfM87P65",   # r10 y-23  cheekbones, peach fuzz, philtrum, the left mouth corner pinched up, a pimple
    "45677Mmmmmm77654",   # r11 y-22  the mouth line (dark), crooked
]
# Lower face 14 x 4: col c <-> x [-7 + c, -6 + c], row r <-> y [-21 + r, -20 + r].  Jowls = cols 0-3 / 10-13, rows
# 0-2 (static, on the head); chin = cols 4-9, rows 0-3 (the jaw bone, one row lower than the jowls: a narrow V chin).
JAW = [
    # 01234567890123
    "45676vVVv67654",     # j0 y-21  lower lip
    "456667xx766654",     # j1 y-20  shade under the lip
    "345567P8765543",     # j2 y-19  jawline turning under | lit chin with a pimple
    "....345543....",     # j3 y-18  chin bottom row (chin only), darker undercut so a small open shows no step
]
assert all(len(r) == 16 for r in FACE) and len(FACE) == 12, [len(r) for r in FACE]
assert all(len(r) == 14 for r in JAW) and len(JAW) == 4


def face_rgba(ch):
    if ch.isdigit():
        return SKIN[int(ch)]
    return {
        'h': mix(SKIN[4], HAIR[3], 0.55), 'k': SKIN[5], 'L': LASH, 'w': SCLERA_S, 'W': SCLERA, 'g': GLINT,
        'R': IRIS_RIM, 'K': PUPIL, 'i': IRIS_L, 'd': mix(SKIN[6], BAG, 0.28), 'c': mix(SKIN[8], hx('#eaa3a0'), 0.25),
        'f': mix(SKIN[7], HAIR[6], 0.16), 's': SKIN[6], 'P': PIMPLE, 'M': mix(hx('#3b151b'), SKIN[5], 0.45),
        'm': hx('#3b151b'), 'x': SKIN[5], 'v': LIP[2], 'V': LIP[3], 'U': SKIN[3],
    }.get(ch, SKIN[7])


# ---- emissive face light (additive): rims from the cups, under-glow from the pad, the screen in his eyes
RIM_COLS = {0: 0.30, 1: 0.15, 2: 0.06}                     # skull front, counted from each outer edge
UNDER_ROW = {8: 0.03, 9: 0.08, 10: 0.11, 11: 0.14}          # skull front rows lit from below
UNDER_JAW = {0: 0.19, 1: 0.22, 2: 0.25, 3: 0.29}            # lower face rows lit from below


def glow_face(i, j, w, h):
    ch = FACE[j][i]
    if ch == 'g':
        return GLINT
    L = Light()
    if ch == 'W':
        L.add(SCREEN, 0.3)                                  # the whites of his eyes catch the screen
    elif ch == 'w':
        L.add(SCREEN, 0.17)
    elif ch == 'i':
        L.add(PAD_GLOW, 0.1)
    if j >= 5:
        for sd, col in ((-1, i), (1, w - 1 - i)):
            k = RIM_COLS.get(col, 0.0)
            L.add(RIM_R if sd < 0 else RIM_L, k * (0.7 if j == 5 else 1.0))
    if ch not in 'mMLK':
        k = UNDER_ROW.get(j, 0.0)
        if ch == 's':
            k = 0.15                                        # philtrum right under the nose
        L.add(PAD_GLOW, k)
    return L.rgba()


def glow_lower(x0):
    """Front of a lower-face cube (jowl or chin) whose left edge is at absolute x0."""
    def fn(i, j, w, h):
        col = int(round(x0 + 7)) + i
        L = Light()
        L.add(PAD_GLOW, UNDER_JAW.get(j, 0.0) * (0.85 if JAW[j][col] in 'x' else 1.0))
        for sd, c in ((-1, col), (1, 13 - col)):
            L.add(RIM_R if sd < 0 else RIM_L, {0: 0.3, 1: 0.14, 2: 0.05}.get(c, 0.0))
        return L.rgba()
    return fn


def glow_under(k):
    def fn(i, j, w, h):
        return rgbf(PAD_GLOW, k)
    return fn


def glow_nose_front(i, j, w, h):
    return rgbf(PAD_GLOW, {0: 0.0, 1: 0.05, 2: 0.13}[min(j, 2)]) if j > 0 else None


def glow_side_skin(sd):
    """Cheek / temple skin on the side of the skull, in front of the cup (west face i = 0 at the back)."""
    def fn(i, j, w, h):
        zi = (w - 1 - i) if sd < 0 else i                   # 0 at the front edge
        y = -33 + j + 0.5
        if zi > 2 or y < -26.5:
            return None
        return rgbf(RIM_R if sd < 0 else RIM_L, (0.32, 0.18, 0.08)[zi])
    return fn


def glow_jowl_side(sd):
    def fn(i, j, w, h):
        zi = (w - 1 - i) if sd < 0 else i
        if zi > 3:
            return None
        return rgbf(RIM_R if sd < 0 else RIM_L, (0.3, 0.2, 0.1, 0.04)[zi])
    return fn


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
            return face_rgba(FACE[ctx.j][ctx.i])
        if f in ('west', 'east'):
            if z > -4.0 or y < -26.5:
                return pick(HAIR, 0.18)                     # under the hair shell / behind the cup
            v = skin_v(ctx, 0.66) - clamp((z + 8.0) / 4.0) * 0.12
            if y > -22.5:
                v -= 0.06                                   # jawline turning under
            if y < -25.5:
                v -= 0.05                                   # temple in the hair's shadow
            return pick(SKIN, v)
        if f == 'bottom':
            if abs(x) < 3.0 and z < -2.0:
                return MOUTH[2] if z < -5 else MOUTH[1]     # roof of the mouth (seen with the jaw open)
            return pick(SKIN, 0.36)
        return pick(HAIR, 0.15)                             # top / back: under the hair
    if t == 'nose':
        if f == 'front':
            return (SKIN[8], SKIN[8], SKIN[7])[min(ctx.j, 2)] if ctx.i == 0 else (SKIN[9], SKIN[8], SKIN[7])[min(ctx.j, 2)]
        if f == 'bottom':
            return SKIN[3] if ctx.i == 0 else SKIN[4]       # nostrils
        if f in ('west', 'east'):
            return pick(SKIN, 0.6 - ly / h * 0.1)
        return SKIN[7]
    if t in ('jaw', 'jowl'):
        if f == 'front':
            col = int(clamp(math.floor(x + 7.0), 0, 13))
            return face_rgba(JAW[ctx.j][col])
        if f == 'bottom':
            v = 0.42 - lz / d * 0.12
            return pick(SKIN, v)
        if f == 'top':
            if t == 'jaw':
                return TONGUE[1] if 1 <= lz < 5 and 1 <= lx < w - 1 else MOUTH[1]   # tongue bed (jaw open)
            return SKIN[3]
        if f in ('west', 'east'):
            v = skin_v(ctx, 0.62) - lz / d * 0.14 - ly / h * 0.08
            if t == 'jaw':
                return pick(SKIN, v - (0.0 if ly > h - 1.0 else 0.08))   # the chin's sides below the jowls
            if f == inner_face(ctx):
                return pick(SKIN, v - 0.12)                 # only seen with the chin dropped
            return pick(SKIN, v)
        return pick(SKIN, 0.4)
    if t == 'neck':
        if f in ('top', 'bottom'):
            return SKIN[3]
        v = skin_v(ctx, 0.6) - (0.2 if ly < 1.5 else 0.0)   # shadow under the jaw
        if f == 'front' and ctx.i == 2 and ctx.j == 2:
            v += 0.05                                       # adam's apple
        return pick(SKIN, v)
    if t == 'tongue':
        v = 0.55 + face_light(ctx)
        if f == 'top' and ctx.i == ctx.w // 2:
            v -= 0.25                                       # the groove down the middle
        return pick(TONGUE, v)
    return pick(SKIN, skin_v(ctx))


# brows (front face, col 0 = the outer tail, col 4 = the thick inner end): straight, heavy, tapering outward
BROW_ART = [
    "..bBB",
    "bBBBB",
]


def brow_mat(ctx):
    f = ctx.face
    sx = side_of(ctx)
    w = ctx.cube.size[0]
    if f == 'back':
        return None
    if f in ('front', 'top', 'bottom'):
        i = ctx.i if sx < 0 else w - 1 - ctx.i
        if f == 'front':
            ch = BROW_ART[min(ctx.j, 1)][min(i, 4)]
        else:
            ch = BROW_ART[0 if f == 'top' else 1][min(i, 4)]
        if ch == '.':
            return None
        if f == 'top':
            return HAIR[4]
        if f == 'bottom':
            return HAIR[1]
        return HAIR[2] if ch == 'B' else HAIR[4]
    inner = (f == 'east') if sx < 0 else (f == 'west')
    if inner:
        return HAIR[1]
    return HAIR[3] if ctx.j == 1 else None


def hand_mat(ctx):
    """Bony pale hands round the pad grips.  In the pad frame the palm is a vertical plate on the outside of the grip
    (its outer face = back of the hand), the fingers come out of its lower edge and wrap under the grip toward the pad
    centre (tips on the inner end), the thumb lies over the stick (nail on its inner end).  Palm, fingers and thumb
    share one tone so the open hand (slam / stand) reads as one flat hand, not stacked boxes."""
    t = tag(ctx)
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    sd = side_of(ctx)
    v = skin_v(ctx, 0.66)
    tip_face = 'west' if sd > 0 else 'east'                 # the inner end of fingers / thumb
    root_face = 'east' if sd > 0 else 'west'
    if t == 'palm':
        if f == outer_face(ctx):
            if ly > h - 1.0:
                v += 0.05 if int(lz) % 2 == 0 else -0.04    # knuckle row along the lower edge
            if lz > d - 1.0:
                v -= 0.07                                   # wrist going into the cuff
            if 1.0 <= ly < 3.0 and int(lz) == 1:
                v += 0.03                                   # a tendon
            return pick(SKIN, v)
        if f == inner_face(ctx):
            v -= 0.06
            if abs(ly - 1.5) < 0.5 and 1 <= lz < d - 1:
                v -= 0.06                                   # palm crease
            return pick(SKIN, v)
        if f == 'back':
            return pick(SKIN, v - 0.06)
        return pick(SKIN, v)
    if t == 'fingers':
        k = int(math.floor(A(ctx)[2] * 1.0 + 100)) % 2   # alternate fingers along z
        if f == tip_face:
            c = pick(SKIN, v + 0.02 - 0.03 * k)
            if ctx.j == 0 and (ctx.i % 2 == 0):
                c = mix(SKIN[8], hx('#f4e4dc'), 0.5)        # nails
            if h2(ctx.i, ctx.j, 3) > 0.55:
                c = mix(c, ORANGE[2], 0.4)                  # cheese-snack dust on the fingertips
            return c
        if f in ('front', 'back'):
            return pick(SKIN, v - 0.03)
        # top / bottom: split lines between the fingers (every texel along z alternates), knuckle crease
        v += 0.03 if k == 0 else -0.04
        if abs(lx - (w - 1.5 if sd > 0 else 1.5)) < 0.5:
            v -= 0.06                                       # middle-joint crease
        return pick(SKIN, v)
    if t == 'thumb':
        if f == 'top':
            if (lx < 1.0) if sd > 0 else (lx > w - 1.0):
                return mix(SKIN[8], hx('#f4e4dc'), 0.55)    # thumbnail
            if abs(lx - w / 2.0) < 0.5:
                return pick(SKIN, v - 0.06)                 # knuckle crease
            return pick(SKIN, v + 0.04)
        if f == tip_face:
            return mix(pick(SKIN, v), ORANGE[2], 0.35)
        if f == 'bottom':
            return pick(SKIN, v - 0.1)
        return pick(SKIN, v)
    return pick(SKIN, v)


# ------------------------------------------------------------------ hair: tapered clumps, dark roots -> lighter tips
def clump_at(u, seed):
    """(k, p, width) for coordinate u: clump index, position 0..1 across it, width (3-5 texels, irregular)."""
    b = -40.0
    k = 0
    while True:
        wk = 3 + int(h2(k, seed, 77) * 2.99)
        if u < b + wk:
            return k, (u - b) / wk, wk
        b += wk
        k += 1


def hair_v(u, along, seed, sheen=0.38):
    """Value of a hair texel: clumps across u, `along` 0 (root) .. 1 (tip).  Rounded clumps lit on their left edge,
    1-texel dark splits that open up toward the tips, a broken sheen band, roots darker than the tips."""
    k, p, wk = clump_at(u, seed)
    v = 0.30 + along * 0.16 + (h2(k, seed, 5) - 0.5) * 0.08
    v += 0.07 * (1.0 - abs(2.0 * p - 1.0)) - 0.04 * p        # rounded clump, lit from his right
    split = p * wk < 1.0
    if split:
        v -= 0.16 * clamp((along - 0.12) / 0.3)             # the clumps separate toward the tips
    else:
        dist = abs(along - sheen - (h2(k, seed, 9) - 0.5) * 0.1)
        if dist < 0.09:
            v += 0.16 * (1.0 - dist / 0.09)                 # sheen band, broken per clump
    return v


def tip_cut(u, from_bottom, seed):
    """True where a clump's pointed tip is cut away: from_bottom = texels above the lower edge of the face."""
    k, p, wk = clump_at(u, seed)
    short = h2(k, seed, 11) * 0.9                           # some clumps end higher than others
    return from_bottom < short + 1.3 * abs(2.0 * p - 1.0) ** 0.8


# fringe strand plane 17 x 5: col p <-> x [-8.5 + p, -7.5 + p], row t <-> y [-31 + t, -30 + t]; '#' hair, '.' cut
FRINGE = [
    # 01234567890123456
    "#################",   # t0 y-31 (mostly inside the root)
    "##.#####.####.###",   # t1 y-30
    "#.##.##.##.#.##.#",   # t2 y-29 choppy tips (the brows sit in front, cols 1.5-6.5 / 10.5-15.5)
    "..##....#.......#",   # t3 y-28 one lock over his right eye's outer corner, one down the nose bridge
    "...#............."    # t4 y-27 ... its tip across the outer white of the right eye
]
assert all(len(r) == 17 for r in FRINGE)


def hair_mat(ctx):
    t = tag(ctx)
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    x, y, z = A(ctx)
    lt = face_light(ctx) * 0.7
    if t == 'fringe_tips':
        if f != 'front' or FRINGE[ctx.j][ctx.i] != '#':
            return None
        below = ctx.j + 1 < len(FRINGE) and FRINGE[ctx.j + 1][ctx.i] == '#'
        u = x + (y + 31.0) * 0.6                            # strands swept toward his right
        v = hair_v(u, 0.55 + ctx.j * 0.1, 7, sheen=2.0) + 0.04
        if not below:
            v -= 0.06                                       # thinner, darker tip
        return pick(HAIR, v)
    if t == 'fringe_root':
        if f == 'back':
            return None
        if f == 'front':
            u = x + (y + 33.6) * 0.6
            return pick(HAIR, hair_v(u, 0.25 + ly / h * 0.3, 7, sheen=0.38) + 0.06)
        if f == 'top':
            return pick(HAIR, hair_v(x, 0.1 + (1.0 - lz / d) * 0.15, 7, sheen=0.2) + 0.1)
        if f == 'bottom':
            return pick(HAIR, 0.1)
        return pick(HAIR, hair_v(z * 1.3, 0.3 + ly / h * 0.4, 9) + lt)
    if t == 'shell':
        if f in ('front', 'bottom'):
            return None                                     # the fringe owns the hairline
        if f == 'top':
            # strands radiate from the crown (0, 3) and are combed forward over the head; the band crosses at z ~0
            dx, dz = x, z - 3.0
            r = math.hypot(dx, dz)
            ang = math.atan2(dx, -dz)
            u = ang * 9.0 if r > 1.2 else 0.0
            return pick(HAIR, hair_v(u, clamp(r / 12.0) * 0.55, 13, sheen=0.33) + 0.1)
        along = clamp((y + 33.5) / 10.0) * 0.75 + 0.2
        if f in ('west', 'east'):
            sd = -1 if f == 'west' else 1
            if z < -4.0:
                # in front of the cup: temple hair ends in a ragged edge at ~y -26.5 with a sideburn tab
                lim = -26.8 + (1.6 if -6.2 < z < -5.0 else 0.0) + h2(int(math.floor(z * 2)), 5, 2) * 0.8
                if y > lim:
                    return None
            v = hair_v(z * sd * 1.1, along, 17 if sd < 0 else 19, sheen=0.42) + lt
            return pick(HAIR, v)
        if f == 'back':
            # two layers: the upper clumps end in points round y -27 over a darker lower layer (it reads as hair
            # layers, not planks)
            k, p, wk = clump_at(x, 23)
            tip_y = -28.6 + h2(k, 23, 11) * 1.3 + (1.0 - abs(2.0 * p - 1.0)) * 1.5
            if y > tip_y:
                v = hair_v(x + 2.0, 0.55 + (y - tip_y) * 0.05, 29, sheen=0.85) - 0.04
                if y - tip_y < 0.9:
                    v -= 0.1                                # shadow under the upper layer's points
                return pick(HAIR, v + lt)
            return pick(HAIR, hair_v(x, along, 23, sheen=0.42) + lt - 0.01)
    if t == 'nape':
        if f in ('front', 'top'):
            return None
        if f == 'bottom':
            return pick(HAIR, 0.08)
        u = x if f == 'back' else z * (1 if f == 'east' else -1) * 1.1
        along = 0.8 + ly / h * 0.2
        if tip_cut(u, (h - ly) * (h + 1.0) / h, 23 if f == 'back' else 29):
            return None                                     # staggered, pointed ends at the nape
        return pick(HAIR, hair_v(u, along, 23 if f == 'back' else 29, sheen=0.4) + lt - 0.03)
    if t == 'tuft_side':
        if f == 'bottom':
            return pick(HAIR, 0.08)
        if f == inner_face(ctx):
            return pick(HAIR, 0.12)
        if f == 'top':
            return pick(HAIR, hair_v(lz * 1.3 + x, 0.3, 45, sheen=0.3) + 0.12)
        u = (lz if f in ('west', 'east') else lx) * 1.3 + x
        if tip_cut(u, (h - ly) * 1.15, 47):
            return None                                     # pointed clump ends flaring over the cup
        return pick(HAIR, hair_v(u, 0.45 + ly / h * 0.45, 47, sheen=0.55) + lt)
    if t == 'tuft':
        if f == 'bottom':
            return pick(HAIR, 0.1)
        along = 0.35 + (1.0 - ly / max(h, 1)) * 0.5
        u = (lx if f in ('front', 'back', 'top') else lz) * 1.4 + x * 0.3
        return pick(HAIR, hair_v(u, along, 37 + int(z), sheen=0.6) + lt + 0.04)
    if t == 'spikes':
        # zero-thickness cut-out planes: jagged messy tips sticking up round the headband
        if f not in ('front', 'back', 'west', 'east'):
            return None
        ii = ctx.i
        col_h = SPIKES[tag2(ctx)][ii] if ii < len(SPIKES[tag2(ctx)]) else 0
        if (h - ctx.j) > col_h:
            return None
        along = 0.5 + (ctx.j - (h - col_h)) / max(1.0, col_h) * 0.4
        return pick(HAIR, hair_v(ii * 1.0, 1.0 - along, 41, sheen=0.75) + 0.08 + lt)
    return pick(HAIR, 0.3 + lt)


def tag2(ctx):
    return getattr(ctx.cube, 'variant', 'front')


# spike planes: per column, how many rows of hair rise from the bottom (0 = cut).  Read from the viewer's side.
SPIKES = {
    'front': [0, 1, 2, 3, 2, 1, 0, 2, 3, 3, 1, 0, 1, 2, 1, 0],
    'side': [0, 2, 3, 1, 0, 1, 3, 2, 1, 0],
    'crown': [1, 3, 2, 0, 2, 3, 1],
}


# ------------------------------------------------------------------ hoodie
FONT_G = [".###", "#...", "#.##", "#..#", ".###"]
GG_ROW = 1                     # first row of the print on the torso front (y -13)
GG_COLS = (1, 9)               # the two letters (4 wide) at x -6..-2 / 2..6; the drawstrings hang in the gap


def gg_px(i, j):
    r = j - GG_ROW
    for c0 in GG_COLS:
        c = i - c0
        if 0 <= r < 5 and 0 <= c < 4 and FONT_G[r][c] == '#':
            return 'ink'
    for c0 in GG_COLS:                                      # drop shadow down-right
        c = i - c0 - 1
        rr = r - 1
        if 0 <= c < 4 and 0 <= rr < 5 and FONT_G[rr][c] == '#':
            return 'shadow'
    return None


def rib(ctx, v, period=2):
    return v + (0.045 if int(math.floor(around(ctx))) % period == 0 else -0.03)


def seg_dist(px, py, seg):
    x0, y0, x1, y1 = seg
    dx, dy = x1 - x0, y1 - y0
    t = clamp(((px - x0) * dx + (py - y0) * dy) / (dx * dx + dy * dy))
    cx, cy = x0 + t * dx, y0 + t * dy
    n = math.hypot(dx, dy)
    sd = ((px - cx) * -dy + (py - cy) * dx) / n
    return math.hypot(px - cx, py - cy), sd, t


def folds(ctx, segs, crease=0.1, ridge=0.05):
    """Hand-placed cloth folds on a face (segments in face-texel coords): a 1-texel crease + a lit ridge beside it."""
    px, py = ctx.i + 0.5, ctx.j + 0.5
    dv = 0.0
    for seg in segs:
        dist, sd, t = seg_dist(px, py, seg)
        taper = 0.5 if t in (0.0, 1.0) else 1.0
        if dist < 0.55:
            dv -= crease * taper
        elif dist < 1.45 and sd > 0:
            dv += ridge * taper
    return dv


def knit(ctx, amt=0.008, seed=0):
    return (hash3(ctx.i, ctx.j, ctx.w * 7 + ctx.h * 3 + seed, 91) - 0.5) * amt


# fold layouts (face-texel coordinates): few, long, deliberate
FOLD_TORSO_FRONT = [(0.5, 3.5, 4.5, 9.5), (13.5, 3.5, 9.5, 9.5), (1.0, 13.2, 6.0, 12.4), (8.5, 12.4, 13.0, 13.3)]
FOLD_TORSO_SIDE = [(1.0, 1.5, 6.5, 6.5), (1.0, 12.8, 6.5, 13.4)]
FOLD_TORSO_BACK = [(3.5, 7.5, 1.5, 13.0), (10.5, 7.5, 12.5, 13.0), (5.0, 13.4, 9.0, 13.4)]
FOLD_SLEEVE = {'front': [(0.3, 7.0, 4.7, 8.2)], 'back': [(0.3, 7.6, 4.7, 6.8)],
               'out': [(0.3, 7.2, 4.7, 6.4)], 'in': [(0.3, 1.5, 4.7, 2.5), (0.3, 7.6, 4.7, 8.4)]}
FOLD_FOREARM = [(0.0, 1.6, 4.0, 2.6), (0.0, 4.8, 4.0, 5.4)]


def hoodie_mat(ctx):
    t = tag(ctx)
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    x, y, z = A(ctx)
    v = 0.52 + face_light(ctx) * 0.9 + knit(ctx)
    if edge(ctx) == 0 and f not in ('top', 'bottom'):
        v -= 0.035
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
                if h2(ctx.i, ctx.j, 51) > 0.9:
                    return pick(HOOD, v + 0.02)             # cracked print: the fleece shows through
                return ACID[6] if ctx.j == GG_ROW else (ACID[5] if ctx.j <= GG_ROW + 2 else ACID[4])
            if g == 'shadow':
                return mix(pick(HOOD, v), ACID[1], 0.5)
            cx = abs(lx - w / 2.0)
            v += 0.04 * clamp(1.0 - cx / 6.0) * clamp(1.0 - ly / 8.0)     # chest catches the light
            v -= 0.04 * clamp((cx - 5.0) / 2.0)             # sides turn away
            v += folds(ctx, FOLD_TORSO_FRONT)
            return pick(HOOD, v)
        if f in ('west', 'east'):
            if abs(lz - 4.0) < 0.5:
                v -= 0.04                                   # side seam
            v -= 0.06 * clamp((3.0 - ly) / 3.0)            # armpit shadow under the sleeve
            v += folds(ctx, FOLD_TORSO_SIDE)
            return pick(HOOD, v)
        if f == 'back':
            v += folds(ctx, FOLD_TORSO_BACK) - 0.02
            v -= 0.05 * clamp((3.0 - ly) / 3.0)             # shadow under the bunched hood
            return pick(HOOD, v)
    if t == 'hem':
        if f == 'top':
            return HOOD[1]
        if f == 'bottom':
            return HOOD[0] if abs(x) < 6 and abs(z) < 3.4 else HOOD[2]
        return pick(HOOD, rib(ctx, v - 0.07))
    if t == 'pocket':
        if f == 'back':
            return None
        if f == 'front':
            if ctx.i in (0, w - 1):
                return HOOD[1] if ctx.j >= 1 else pick(HOOD, v - 0.06)      # pocket mouths
            if ctx.i in (1, w - 2) and ctx.j <= 2:
                return pick(HOOD, v - 0.11)
            if ctx.j == 0:
                if ctx.i in (2, 3) and h2(ctx.i, 1, 5) > 0.3:
                    return mix(pick(HOOD, v + 0.04), ORANGE[2], 0.45)       # snack dust wiped on the pocket edge
                return pick(HOOD, v + 0.06) if ctx.i % 2 else pick(HOOD, v + 0.01)   # top seam stitches
            if 6 <= ctx.i <= 8 and 1 <= ctx.j <= 3:
                v += 0.07 if ctx.j == 1 else 0.03           # phone-shaped bulge
                if ctx.i == 8:
                    v -= 0.05
            return pick(HOOD, v - 0.02)
        if f == 'top':
            return pick(HOOD, v + 0.06)
        return pick(HOOD, v - 0.1)
    if t == 'sleeve':
        if f == 'top':
            return pick(HOOD, v + 0.03)
        if f == 'bottom':
            return HOOD[1]
        key = 'out' if f == outer_face(ctx) else ('in' if f == inner_face(ctx) else f)
        v += folds(ctx, FOLD_SLEEVE[key])
        if ly < 1.5:
            v += 0.04                                       # shoulder catches the light
        if key == 'in':
            v -= 0.06
        return pick(HOOD, v)
    if t == 'forearm':
        if f in ('top', 'bottom'):
            return HOOD[1]
        v += folds(ctx, FOLD_FOREARM if f in ('front', 'back') else [(0.0, 2.2, 4.0, 1.4)])
        if f == inner_face(ctx):
            v -= 0.06
        return pick(HOOD, v)
    if t == 'cuff':
        if f == 'bottom':
            return SKIN[3]                                  # wrist inside the cuff
        if f == 'top':
            return HOOD[1]
        return pick(HOOD, rib(ctx, v - 0.05))
    if t in ('hood_roll', 'hood_tip', 'collar_side'):
        return hood_mat(ctx, t, v)
    return pick(HOOD, v)


def lining(ctx, v=0.5):
    lv = v + face_light(ctx) * 0.6
    lv += 0.04 if int(around(ctx) if ctx.face != 'top' else ctx.i) % 3 == 0 else 0.0     # gathered ripples
    return pick(ACID, lv)


def hood_mat(ctx, t, v):
    """The hood lying down: a thick bunched roll on the upper back (outer fabric a value lighter than the torso so it
    reads from behind) whose opening shows the acid-green lining as a U, and a pointed tip hanging below it."""
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    v += 0.07
    if t == 'hood_roll':
        if f == 'top':
            # looking down into the opening: green lining rim round a dark inside
            e = min(ctx.i, ctx.w - 1 - ctx.i, ctx.j)
            if e == 0:
                return lining(ctx, 0.55)
            if e == 1:
                return lining(ctx, 0.3)
            return HOOD[1]
        if f == 'back':
            # the opening seen from behind: a U of lining (rim on top and down both sides to row 3) round dark fabric
            cu = min(ctx.i, w - 1 - ctx.i)
            if ly < 1.0 or (cu == 0 and ly < 4.0):
                return lining(ctx, 0.6 - ly * 0.05)
            if cu == 1 and ly < 3.0 and ly >= 1.0:
                return lining(ctx, 0.28)                    # the lining turning inward (shadowed)
            if ly < 3.0 and cu >= 2:
                return HOOD[1] if ly < 2.0 else HOOD[2]     # the hood's dark inside
            v += folds(ctx, [(1.5, 3.4, 5.5, 4.4), (10.5, 3.4, 6.5, 4.4), (3.0, 5.6, 9.0, 5.6)], 0.09, 0.05)
            v -= abs(lx - w / 2.0) / (w / 2.0) * 0.05
            return pick(HOOD, v)
        if f in ('west', 'east'):
            if ly < 1.0:
                return lining(ctx, 0.5)
            v += folds(ctx, [(0.5, 2.5, 4.5, 4.0)], 0.09, 0.05)
            return pick(HOOD, v - 0.03)
        if f == 'front':
            return HOOD[1]
        return HOOD[2]
    if t == 'hood_tip':
        if f == 'back':
            if ctx.j == h - 1 and ctx.i in (0, w - 1):
                return None                                 # rounded point
            if abs(lx - w / 2.0) < 0.5:
                return pick(HOOD, v - 0.1)                  # centre seam of the hood
            v -= abs(lx - w / 2.0) / (w / 2.0) * 0.06
            return pick(HOOD, v - ly * 0.015)
        if f == 'bottom':
            return HOOD[1]
        return pick(HOOD, v - 0.04)
    # collar sides (the hood's rim lying round the neck on the shoulders): lining on top and on the inner face
    if f == 'top' or f == inner_face(ctx):
        return lining(ctx, 0.48 if f == 'top' else 0.32)
    if f == 'bottom':
        return HOOD[1]
    return pick(HOOD, v + (0.04 if ly < 1 else 0.0))


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
    """Heather-grey fleece: rare flecks over a near-flat base."""
    n = hash3(ctx.i, ctx.j, ctx.w * 5 + ctx.h, 71)
    if n > 0.975:
        return v + 0.035
    if n < 0.025:
        return v - 0.03
    return v


FOLD_THIGH_FRONT = [(0.5, 7.6, 5.5, 8.6)]
FOLD_THIGH_SIDE = [(0.6, 7.8, 5.4, 8.6)]
FOLD_THIGH_BACK = [(0.5, 1.6, 5.5, 2.4)]
FOLD_SHIN = [(0.0, 2.6, 2.5, 3.6), (2.5, 3.6, 5.0, 2.6), (0.0, 4.6, 5.0, 4.6)]


def jogger_mat(ctx):
    t = tag(ctx)
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    v = heather(ctx, 0.52 + face_light(ctx) * 0.9)
    if edge(ctx) == 0 and f not in ('top', 'bottom'):
        v -= 0.035
    if t == 'thigh':
        if f in ('top', 'bottom'):
            return JOG[1]
        v -= 0.09 * clamp((1.6 - ly) / 1.6)                 # in the shadow of the hoodie hem
        if f == outer_face(ctx):
            if abs(lz - d / 2.0) < 0.5:
                return pick(JOG, v - 0.08)                  # side seam
            v += folds(ctx, FOLD_THIGH_SIDE)
        elif f == 'front':
            v += folds(ctx, FOLD_THIGH_FRONT)
            if ctx.i in (2, 3) and ly < 7:
                v += 0.025                                  # the front of the thigh catches the light
        elif f == 'back':
            v += folds(ctx, FOLD_THIGH_BACK)
        else:
            v -= 0.07
        return pick(JOG, v)
    if t == 'shin':
        if f in ('top', 'bottom'):
            return JOG[1]
        v += folds(ctx, FOLD_SHIN, crease=0.1, ridge=0.06)  # bunched over the cuff
        if f == inner_face(ctx):
            v -= 0.06
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
            return pick(PLASTIC, 0.42 + (0.06 if (ctx.i + ctx.j) % 3 == 0 else 0.0))   # grey treads
        if f == 'top':
            return pick(WHITE, 0.62)
        if ly > h - 1.0:
            return pick(PLASTIC, 0.62 + (0.05 if h2(ctx.i, 2, 81) > 0.7 else 0.0))   # grey outsole edge
        return pick(WHITE, v - 0.02 - (0.05 if h2(ctx.i, 4, 85) > 0.85 else 0.0))
    if t == 'upper':
        if f == 'bottom':
            return WHITE[3]
        if f == 'back':
            if abs(lx - w / 2.0) < 1.6:
                return pick(RED, 0.6 + face_light(ctx))     # red heel tab
            return pick(WHITE, v - 0.05)
        if f == 'front':
            return pick(WHITE, v - 0.12 - (0.06 if ly < 1 else 0.0))   # grey toe box
        if f == 'top':
            if lz < 2.5:
                return pick(WHITE, v - 0.14 - (0.06 if (ctx.i + int(lz)) % 2 == 0 and 1 <= ctx.i <= w - 2 else 0.0))
            k = int(math.floor(lz))
            if ctx.i in (0, w - 1):
                return pick(WHITE, v - 0.04)
            if ctx.i in (1, w - 2):
                return PLASTIC[5] if k % 2 == 0 else pick(WHITE, v - 0.02)   # eyelets
            return WHITE[8] if k % 2 == 1 else WHITE[4]               # lace bars over the grey tongue
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
                return pick(RED, 0.55) if 1 <= ctx.i <= 2 else pick(WHITE, v - 0.04)
            return WHITE[8] if 0 < ctx.i < w - 1 else PLASTIC[5]
        return pick(WHITE, v - 0.07)
    if t == 'lace':
        if f not in ('west', 'east'):
            return None
        if (ctx.i + ctx.j) % 3 == 2 and ctx.j > 0:
            return None
        return WHITE[7] if ctx.j < 2 else WHITE[5]
    return pick(WHITE, v)


# ------------------------------------------------------------------ headset + mic
LOGO = [".....", "#####", ".###.", "..#..", "....."]


def logo_px(i, j):
    a, b = i - 1, j - 1
    return 0 <= a < 5 and 0 <= b < 5 and LOGO[b][a] == '#'


def cup_arc(sd, i, j, w, h):
    """LED arc on a cup's FRONT face (seen head-on): the outer column full height + the top / bottom rows bending
    in, like the front edge of the ring.  Returns the ring angle or None."""
    oc = (w - 1 - i) if sd > 0 else i                     # 0 = outer column
    if oc == 0 and 0 < j < h - 1:
        return 3.1 + (j - h / 2.0) * 0.25
    if oc == 1 and j in (0, 1, h - 2, h - 1):
        return 3.1 + (j - h / 2.0) * 0.25
    if oc == 2 and j in (0, h - 1):
        return 3.1 + (j - h / 2.0) * 0.25
    return None


def headset_mat(ctx):
    t = tag(ctx)
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    sd = side_of(ctx)
    v = 0.36 + face_light(ctx) * 1.2
    if edge(ctx) == 0:
        v += 0.07                                           # crisp lit rims on the matte plastic
    if t in ('band', 'band_end'):
        if f == 'top':
            if abs(lz - d / 2.0) < 0.6:
                xx = A(ctx)[0]
                return hsv(0.5 + 0.45 * clamp((xx + 11.0) / 22.0), 0.85, 0.9)   # LED strip
            return pick(PLASTIC, v + 0.05)
        if f == 'bottom':
            return pick(CUSHION, 0.45)
        return pick(PLASTIC, v)
    if t == 'slider':
        if f in ('west', 'east', 'front', 'back') and ctx.j in (2, 4):
            return STEEL[0]                                 # size notches on the slider
        return pick(STEEL, 0.18 + face_light(ctx) * 0.8)
    if t == 'cup':
        if f in ('front', 'back'):
            ang = cup_arc(sd, ctx.i, ctx.j, w, h)
            if ang is not None:
                return hsv(ring_hue(sd, ang if f == 'front' else ang - 3.1), 0.8, 0.85)
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
            return PLASTIC[2] if e == 1 else PLASTIC[3]     # dark smoked plate, recessed edge
        if f == inner_face(ctx):
            return PLASTIC[1]
        ang = {'top': -1.57, 'bottom': 1.57, 'front': 3.1, 'back': 0.0}.get(f, 0.0) + (ctx.i - ctx.w / 2.0) * 0.2
        return hsv(ring_hue(sd, ang), 0.8, 0.85)            # the ring's thickness glows too
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


# ------------------------------------------------------------------ gamepad
# Pad body top face, 10 x 5: i = lx 0..9 from his right (-X) to his left (+X), j = 0 at the near edge (toward him) ..
# 4 at the far edge.  Far half: face buttons under his right thumb, touchpad in the middle, d-pad under his left
# thumb; near half: the two sticks (their own cubes) and the glowing home button between them.
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
    if (i, j) in ((4, 1), (5, 1)):
        return 'home', None
    return None, None


def pad_mat(ctx):
    t = tag(ctx)
    f = ctx.face
    w, h, d = ctx.cube.size
    v = 0.74 + face_light(ctx) * 0.9
    if edge(ctx) == 0 and f != 'top':
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
        edge_t = ctx.i in (0, ctx.w - 1)
        if ctx.j == 0:
            return TEETH[1] if edge_t else TEETH[3]         # upper teeth
        if ctx.j == 1:
            if edge_t:
                return MOUTH[1]
            return BRACE if ctx.i % 2 == 1 else BRACE_D     # brackets on the wire
        return TONGUE[1] if 2 <= ctx.i <= ctx.w - 3 else MOUTH[0]
    if t == 'teeth':
        if f != 'front':
            return None
        if ctx.j == 0:
            return BRACE if ctx.i % 2 == 0 else BRACE_D     # lower brackets on the wire
        return TEETH[2] if ctx.i in (0, ctx.w - 1) else TEETH[3]
    return MOUTH[1]


KINDS = {'skin': skin_mat, 'hand': hand_mat, 'hair': hair_mat, 'hoodie': hoodie_mat, 'string': string_mat,
         'jogger': jogger_mat, 'shoe': shoe_mat, 'headset': headset_mat, 'pad': pad_mat, 'mouth': mouth_mat,
         'brow': brow_mat}


def toti_mat(ctx):
    return KINDS.get(kind(ctx), hoodie_mat)(ctx)


DEFAULT_MAT = toti_mat
FOCUS = 'head'


# ------------------------------------------------------------------ emissive decals: headset, pad, fists, braces
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
        return hsv(ring_hue(sd, ang), 0.8, 0.85)
    return fn


def glow_cup_face(sd, face):
    def fn(i, j, w, h):
        ang = cup_arc(sd, i, j, w, h)
        if ang is None:
            return None
        return hsv(ring_hue(sd, ang if face == 'front' else ang - 3.1), 0.8, 0.95)
    return fn


def glow_band_end(sd):
    def fn(i, j, w, h):
        if j != h // 2:
            return None
        t = ((i + 0.5) / w * 4.0 + (0.0 if sd < 0 else 18.0)) / 22.0
        return hsv(0.5 + 0.45 * t, 0.85, 0.85)
    return fn


def glow_band_top(i, j, w, h):
    if j == h // 2:
        return hsv(0.5 + 0.45 * ((i + 0.5) / w * 15.0 + 3.5) / 22.0, 0.85, 0.85)
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
    if kd == 'touch':
        return rgbf(PAD_GLOW, 0.18)
    return None


def glow_brace_up(i, j, w, h):
    return rgbf(PAD_GLOW, 0.32) if j == 1 and 1 <= i <= w - 2 and i % 2 == 1 else None


def glow_brace_lo(i, j, w, h):
    return rgbf(PAD_GLOW, 0.28) if j == 0 and i % 2 == 0 else None


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
SLOUCH = 6.0             # the whole torso leans forward over the hips (legs counter-rotated: soles stay flat)
NECK_FWD = 15.0          # gamer neck: head jutted forward
HEAD_DOWN = 2.0          # and bowed a little more over the pad
ARM = (-14.0, 8.0, -8.0)         # LEFT upper arm (right = (x, -y, -z)): forward, rolled in (rounded shoulders), elbow out
FOREARM = (-56.0, 18.0, 0.0)     # LEFT forearm: up in front of the belly, angled in toward the pad
PAD_TILT = -36.0         # the pad's face tilted up toward his eyes
WRIST_P = (1.0, 4.5)     # (y, z) of the wrist in the pad frame (x comes out of the arm FK)
CUP_YAW = 16.0           # cups yawed so the outer RGB plates turn toward the front (left = +, right = -)
BROW_FOCUS = 5.0         # brows' rest zRot, inner ends down a touch: absorbed
ARM_X = 9.5              # shoulder pivot x
LEG_X = 3.75             # hip pivot x (0.5 gap between the soles)


def build():
    r = Rig()

    def bone(name, pivot, parent=None, rot=(0, 0, 0)):
        return r.bone(name, pivot, parent=parent, rot=rot)

    def box(b, frm, size, kd, name, inflate=0.0, decals=None, sx=1, variant=None):
        c = r.box(b, frm, size, inflate=inflate, decals=decals)
        c.a0 = tuple(float(v) for v in frm)
        c.kind = kd
        c.name = name
        c.sx = sx
        if variant:
            c.variant = variant
        return c

    # ---------------- body: root at the hips (slouched forward).  Hoodie torso, ribbed hem, kangaroo pocket, the hood
    # lying down (a thick bunched roll on the upper back + its rim round the neck + its tip), the drawstrings
    bone('body', (0, 2, 0), rot=(SLOUCH, 0, 0))
    box('body', (-7, -14, -4), (14, 15, 8), 'hoodie', 'torso')
    box('body', (-7, 1, -4), (14, 2, 8), 'hoodie', 'hem', inflate=0.3)
    box('body', (-5, -3, -5), (10, 4, 1), 'hoodie', 'pocket')
    box('body', (-6.5, -17, 2), (13, 8, 6), 'hoodie', 'hood_roll')
    box('body', (-3.5, -9.5, 4.5), (7, 5, 3), 'hoodie', 'hood_tip')
    box('body', (-7, -15.5, -3.5), (3, 2, 6), 'hoodie', 'collar_side', sx=-1)
    box('body', (4, -15.5, -3.5), (3, 2, 6), 'hoodie', 'collar_side', sx=1)
    for sx in (-1, 1):
        box('body', (1.0 * sx - 0.5, -14.5, -4.6), (1, 6, 1), 'string', 'string', sx=sx)

    # ---------------- neck + head
    bone('neck', (0, -14, 0.5), 'body', rot=(NECK_FWD, 0, 0))
    box('neck', (-2.5, -18, -2), (5, 4, 5), 'skin', 'neck', decals={'eyes:front': glow(glow_under(0.1))})
    bone('head', (0, -17.5, 0.5), 'neck', rot=(HEAD_DOWN, 0, 0))
    box('head', (-8, -33, -8), (16, 12, 14), 'skin', 'skull',
        decals={'eyes:front': glow(glow_face), 'eyes:west': glow(glow_side_skin(-1)),
                'eyes:east': glow(glow_side_skin(1))})
    box('head', (-1, -26, -9), (2, 3, 1), 'skin', 'nose',
        decals={'eyes:bottom': glow(glow_under(0.3)), 'eyes:front': glow(glow_nose_front)})
    box('head', (-3, -21, -7.6), (6, 3, 4), 'mouth', 'mouth', decals={'eyes:front': glow(glow_brace_up)})
    for sx in (-1, 1):                                      # static jowls either side of the chin
        x0 = -7 if sx < 0 else 3
        box('head', (x0, -21, -8), (4, 3, 10), 'skin', 'jowl', sx=sx,
            decals={'eyes:front': glow(glow_lower(x0)), 'eyes:bottom': glow(glow_under(0.24)),
                    ('eyes:west' if sx < 0 else 'eyes:east'): glow(glow_jowl_side(sx))})
    box('head', (-8, -33, -8), (16, 9, 14), 'hair', 'shell', inflate=0.5)
    box('head', (-7.5, -23, 0), (15, 6, 6), 'hair', 'nape', inflate=0.5)
    # messy clumps poking up round the headband and out over the cups
    box('head', (-6.5, -35.5, -7), (4, 2, 3), 'hair', 'tuft', sx=-1)
    box('head', (2, -35, -6.5), (3, 2, 3), 'hair', 'tuft', sx=1)
    box('head', (-2.5, -35.5, 2.5), (4, 2, 3), 'hair', 'tuft', sx=1)
    box('head', (-10.2, -32.5, -6.5), (2, 4, 5), 'hair', 'tuft_side', sx=-1)    # puffing out over the cups,
    box('head', (8.2, -32, -6), (2, 4, 4), 'hair', 'tuft_side', sx=1)          # in front of the sliders
    box('head', (8.4, -31.5, 2.5), (2, 3, 3), 'hair', 'tuft_side', sx=1)       # and one behind the left slider
    box('head', (-8, -36.5, -5.6), (16, 3, 0), 'hair', 'spikes', variant='front')
    box('head', (0.3, -36.5, 0.5), (0, 3, 7), 'hair', 'spikes', variant='crown')

    bone('fringe', (0, -33, -9), 'head')
    box('fringe', (-8.5, -33.6, -9.3), (17, 3, 2), 'hair', 'fringe_root')
    box('fringe', (-8.5, -31, -8.9), (17, 5, 0), 'hair', 'fringe_tips')

    for side, sx in (('right', -1), ('left', 1)):
        bb = f'{side}_brow'
        bone(bb, (4.5 * sx, -29, -9), 'head', rot=(0, 0, BROW_FOCUS * -sx))
        box(bb, (4.5 * sx - 2.5, -30, -9.5), (5, 2, 2), 'brow', 'brow', sx=sx)

    bone('jaw', (0, -21, 2), 'head')
    box('jaw', (-3, -21, -8), (6, 4, 10), 'skin', 'jaw',
        decals={'eyes:front': glow(glow_lower(-3)), 'eyes:bottom': glow(glow_under(0.3))})
    box('jaw', (-2.5, -22.5, -7.4), (5, 2, 0), 'mouth', 'teeth', decals={'eyes:front': glow(glow_brace_lo)})
    bone('tongue', (2.5, -21, -5.5), 'jaw')
    box('tongue', (1.5, -21.6, -7.2), (2, 1, 3), 'skin', 'tongue')

    # ---------------- headset: band + sliders on 'headphones'; each cup (cushion, cup, RGB plate) on its own bone,
    # yawed so the plate turns toward the front; boom mic on the left cup
    bone('headphones', (0, -34, 0.5), 'head')
    box('headphones', (-7.5, -35.8, -1.5), (15, 2, 4), 'headset', 'band', decals={'eyes:top': glow(glow_band_top)})
    for side, sx in (('right', -1), ('left', 1)):
        box('headphones', ((7 if sx > 0 else -11), -35.0, -1.5), (4, 2, 4), 'headset', 'band_end', sx=sx,
            decals={'eyes:top': glow(glow_band_end(sx))})
        box('headphones', ((10 if sx > 0 else -12), -33.5, -2), (2, 6, 2), 'headset', 'slider', sx=sx)
        cb = f'{side}_cup'
        bone(cb, (9.0 * sx, -24, -0.5), 'headphones', rot=(0, CUP_YAW * sx, 0))
        box(cb, ((7.5 if sx > 0 else -9.5), -27.5, -4), (2, 7, 7), 'headset', 'cushion', sx=sx)
        box(cb, ((9.5 if sx > 0 else -12.5), -28.5, -5), (3, 9, 9), 'headset', 'cup', sx=sx,
            decals={'eyes:front': glow(glow_cup_face(sx, 'front')), 'eyes:back': glow(glow_cup_face(sx, 'back'))})
        dec = {('eyes:east' if sx > 0 else 'eyes:west'): glow(glow_plate(sx))}
        for fc in ('top', 'bottom', 'front', 'back'):
            dec['eyes:' + fc] = glow(glow_plate_rim(sx, fc))
        box(cb, ((12.5 if sx > 0 else -13.5), -27.5, -4), (1, 7, 7), 'headset', 'plate', sx=sx, decals=dec)
    # the mic boom points at his left mouth corner: aim the bone (pitch, yaw) from the FK of head -> cup
    mic_piv = (10.5, -21.5, -4.5)
    bone('mic', mic_piv, 'left_cup', rot=mic_aim(mic_piv))
    box('mic', (10, -22, -11), (1, 1, 7), 'headset', 'boom')
    box('mic', (9.5, -22.5, -13), (2, 2, 2), 'headset', 'mic_tip', decals={'eyes:front': glow(glow_mic)})

    # ---------------- arms (bind: hanging straight), rest rotations mirrored; hands aligned to the pad frame
    arm_rot = {1: ARM, -1: (ARM[0], -ARM[1], -ARM[2])}
    fa_rot = {1: FOREARM, -1: (FOREARM[0], -FOREARM[1], -FOREARM[2])}
    for side, sx in (('right', -1), ('left', 1)):
        arm, fa = f'{side}_arm', f'{side}_forearm'
        ax = ARM_X * sx
        bone(arm, (ax, -12.5, 0), 'body', rot=arm_rot[sx])
        box(arm, (ax - 2.5, -14, -2.5), (5, 10, 5), 'hoodie', 'sleeve', sx=sx)
        bone(fa, (ax, -4.5, 0), arm, rot=fa_rot[sx])
        box(fa, (ax - 2, -5, -2), (4, 7, 4), 'hoodie', 'forearm', sx=sx)
        box(fa, (ax - 2, 1, -2), (4, 2, 4), 'hoodie', 'cuff', sx=sx, inflate=0.35)

    # FK: where do the wrists land, and which hand rotation squares each fist to the pad?
    M_fa = _fk([((0, 2, 0), (SLOUCH, 0, 0)), ((ARM_X, -12.5, 0), ARM), ((ARM_X, -4.5, 0), FOREARM)])
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

    gp = round(gx * 2) / 2.0                                # palm centre x in the pad frame (grip outer edge = gp-1)
    for side, sx in (('right', -1), ('left', 1)):
        hb = f'{side}_hand'
        hr = hand_rot if sx > 0 else (hand_rot[0], -hand_rot[1], -hand_rot[2])
        bone(hb, (ARM_X * sx, 3.0, 0.0), f'{side}_forearm', rot=hr)
        PADP[hb] = (gx * sx, WY, WZ)
        # fist round the grip: palm on the outside (back of the hand out), fingers wrapping under the grip
        pc = gp * sx
        pbox(hb, (pc - 1.0, -1.5, 0.5), (2, 4, 4), 'hand', 'palm', sx=sx,
             decals={'eyes:top': glow(glow_under(0.14))})
        f0 = pc - 4.0 if sx > 0 else pc
        if sx > 0:
            pbox(hb, (f0, 2.0, 0.5), (4, 2, 4), 'hand', 'fingers', sx=sx)
        else:
            pbone('right_fingers', (pc + 0.5, 2.5, 2.5), hb)
            pbox('right_fingers', (f0, 2.0, 0.4), (4, 2, 2), 'hand', 'fingers', sx=sx)
            pbox('right_fingers', (f0, 2.0, 2.6), (4, 2, 2), 'hand', 'fingers', sx=sx)
        tb = f'{side}_thumb'
        pbone(tb, (pc - 0.5 * sx, -1.5, 2.5), hb)
        t0 = pc - 6.0 if sx > 0 else pc
        pbox(tb, (t0, -2.8, 1.5), (6, 2, 2), 'hand', 'thumb', sx=sx, decals={'eyes:top': glow(glow_under(0.12))})

    # gamepad: centre of the pad frame, child of the left hand
    pbone('gamepad', (0.0, 0.0, 0.0), 'left_hand')
    pbox('gamepad', (-5, -1.5, -2.5), (10, 3, 5), 'pad', 'pad',
         decals={'eyes:front': glow(glow_pad_front), 'eyes:top': glow(glow_pad_top)})
    for sx in (-1, 1):
        g0 = (gp - 4.0) if sx > 0 else -(gp - 1.0)
        pbox('gamepad', (g0, -0.5, -0.5), (3, 3, 5), 'pad', 'grip', sx=sx)
        s0 = 1.0 if sx > 0 else -3.0
        pbox('gamepad', (s0, -2.5, 0.5), (2, 1, 2), 'pad', 'stick', sx=sx)

    # ---------------- legs: joggers + chunky sneakers (hips counter-rotated against the slouch)
    for side, sx in (('right', -1), ('left', 1)):
        leg, shin, foot = f'{side}_leg', f'{side}_shin', f'{side}_foot'
        lx = LEG_X * sx
        bone(leg, (lx, 3, 0), 'body', rot=(-SLOUCH, 0, 0))
        box(leg, (lx - 3, 2, -3), (6, 10, 6), 'jogger', 'thigh', sx=sx)
        bone(shin, (lx, 12, 0), leg)
        box(shin, (lx - 2.5, 12, -2.5), (5, 6, 5), 'jogger', 'shin', sx=sx)
        box(shin, (lx - 2.5, 17, -2.5), (5, 2, 5), 'jogger', 'jcuff', sx=sx, inflate=0.4)
        bone(foot, (lx, 19, 0), shin)
        box(foot, (lx - 3, 19, -6), (6, 3, 9), 'shoe', 'upper', sx=sx)
        box(foot, (lx - 3.5, 22, -6.5), (7, 2, 10), 'shoe', 'sole', sx=sx)
        box(foot, (lx - 2, 17.5, -4), (4, 2, 2), 'shoe', 'shoe_tongue', sx=sx)
    box('right_foot', (-LEG_X - 3.8, 21, -5), (0, 3, 3), 'shoe', 'lace', sx=-1)

    m = Model('toti', 256, 128, r.roots)
    m.scale = 0.5
    m.pad_info = {'gx': gx, 'gp': gp, 'wrist': wrist_w.tolist(), 'hand_rot': hand_rot}
    return m


def mic_aim(piv, target=(6.2, -19.6, -9.0)):
    """Rest rotation (deg) of the mic bone (child of left_cup) so its boom (local -Z) points from piv at the target
    (head-bind coordinates: just off his left mouth corner)."""
    cup_piv = np.array((9.0, -24.0, -0.5))
    Rc = rot_matrix(0, math.radians(CUP_YAW), 0)
    # mic pivot in head-bind space (the cup rotates about its own pivot)
    p = cup_piv + Rc @ (np.array(piv) - cup_piv)
    dw = np.array(target) - p
    dl = Rc.T @ dw                                          # direction in the cup's frame
    dl /= np.linalg.norm(dl)
    # local -Z rotated by Ry(yaw) Rx(pitch): (-sin(yaw)cos(p), sin(p)... ) solve for -Z -> dl
    pitch = math.asin(clamp(dl[1], -1, 1))                  # +y (down) needs +pitch about x for -Z
    yaw = math.atan2(-dl[0], -dl[2])
    return (math.degrees(pitch), math.degrees(yaw), 0.0)


POSES = {
    'crouch_closet': {
        'body': (0.384, 0, 0, 0, 12.298, 3.895),
        'right_leg': (-2.129, 0, 0.05, 0, 0, 0),
        'right_shin': (2.443, 0, 0, 0, 0, 0),
        'right_foot': (-0.698, 0, -0.05, 0, 0, 0),
        'left_leg': (-2.129, 0, -0.05, 0, 0, 0),
        'left_shin': (2.443, 0, 0, 0, 0, 0),
        'left_foot': (-0.698, 0, 0.05, 0, 0, 0),
        'neck': (-0.3, 0, 0, 0, 0, 0),
        'head': (-0.06, 0, 0, 0, 0, 0),
        'left_arm': (-0.989, -0.093, 0.18, 0, 0, 0),
        'left_forearm': (-0.349, -0.149, 0.021, 0, 0, 0),
        'left_hand': (1.15, 0.392, 0.197, 0, 0, 0),
        'right_arm': (-0.989, 0.093, -0.18, 0, 0, 0),
        'right_forearm': (-0.349, 0.149, -0.021, 0, 0, 0),
        'right_hand': (1.15, -0.392, -0.197, 0, 0, 0),
        'jaw': (0.06, 0, 0, 0, 0, 0),
        'tongue': (0.12, 0, 0.3, 0, 0.45, -2.4),
        'left_thumb': (0, 0, 0.12, 0, 0, 0),
        'right_brow': (0, 0, 0.06, 0, 0, 0),
        'left_brow': (0, 0, -0.06, 0, 0, 0),
    },
    'slam': {
        'body': (0.384, 0, 0, 0, 12.298, 3.895),
        'right_leg': (-2.129, 0, 0.05, 0, 0, 0),
        'right_shin': (2.443, 0, 0, 0, 0, 0),
        'right_foot': (-0.698, 0, -0.05, 0, 0, 0),
        'left_leg': (-2.129, 0, -0.05, 0, 0, 0),
        'left_shin': (2.443, 0, 0, 0, 0, 0),
        'left_foot': (-0.698, 0, 0.05, 0, 0, 0),
        'neck': (-0.3, -0.12, 0, 0, 0, 0),
        'head': (0, -0.42, 0.1, 0, 0, 0),
        'left_arm': (-0.927, -0.104, 0.151, 0, 0, 0),
        'left_forearm': (-0.316, -0.145, 0.012, 0, 0, 0),
        'left_hand': (1.093, 0.351, 0.176, 0, 0, 0),
        'right_arm': (-0.924, 0.866, 0.7, 0, 0, 0),
        'right_forearm': (0.295, 0.172, 0.252, 0, 0, 0),
        'right_hand': (-0.902, -0.675, 1.073, 0, 0, 0),
        'right_fingers': (0, 0, 1.571, 0, 0, 0),
        'right_thumb': (0, 0, -0.4, 0, 0, 0),
        'jaw': (0.34, 0, 0, 0, 0, 0),
        'left_thumb': (0, 0, 0.2, 0, 0, 0),
        'fringe': (-0.1, 0, 0, 0, 0, 0),
        'right_brow': (0, 0, 0.3, 0, 0.4, 0),
        'left_brow': (0, 0, -0.3, 0, 0.4, 0),
    },
    'stand': {
        'body': (-0.05, 0, 0, 0, 0, 0),
        'right_leg': (0.05, 0, 0, 0, 0, 0),
        'left_leg': (0.05, 0, 0, 0, 0, 0),
        'neck': (-0.22, 0, 0, 0, 0, 0),
        'head': (-0.14, 0.14, 0.16, 0, 0, 0),
        'jaw': (0.14, 0, 0, 0, 0, 0),
        'right_arm': (0.189, 0.198, 0.281, 0, -1.4, 0),
        'left_arm': (0.316, 0.014, -0.118, 0, -1.4, 0),
        'right_brow': (0, 0, -0.26, 0, -1, 0),
        'left_brow': (0, 0, 0.26, 0, -1.3, 0),
        'left_forearm': (0.169, 0.016, -0.04, 0, 0, 0),
        'left_hand': (0.119, -0.192, 0.237, 0, 0, 0),
        'right_forearm': (-0.217, 0.193, 0.05, 0, 0, 0),
        'right_hand': (-2.653, 0.603, -2.825, 0, 0, 0),
        'right_fingers': (0, 0, 1.571, 0, 0, 0),
        'right_thumb': (0, 0, -0.5, 0, 0, 0),
    },
}
