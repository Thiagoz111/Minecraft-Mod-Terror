"""Choripan -- the Morales family dachshund, normal form (DEAD LINE, case 20 'La Muneca').

Authored at 2x texel density (model.scale = 0.5).  +Y down, ground y = 24, faces -Z, right_* on -X.

Design
------
The dog the audience has to fall in love with before he turns into a 4.5-block worm-dog, so every
choice is about charm.  About 0.62 blocks tall and 1.24 blocks from nose to rump (plus the tail).
A long low red sausage (three stepped cubes -- core, taller/narrower barrel, prow keel -- give the round
profile and the proud dachshund chest), four stubby legs with toe-bean paws, a plush oversized head
(12 wide, puppy proportions) held forward on a short neck, huge floppy ears that hang to chest level,
chubby jowls, and a long whip tail (two bones) carried up in a happy curve.

Face (the 'aww' close-up): big glossy brown eyes (5x6) on their own slightly protruding cubes, each with
a 2x2 white glint tucked in the top-left corner, a 1-px glint bottom-right and a warm brown lower iris;
the eyes wrap round the corner of the skull (with a glint) so the profile still has an eye.  All glints
are in the emissive 'eyes' layer, so the eyes sparkle in the flashlight at night.  Little tan eyebrow
tufts on their own bones (puppy-worried at rest, raised in 'tilt', furrowed in 'growl').  A long narrow
muzzle, a big shiny black nose with nostrils and a wet leather bulb on top, a soft philtrum and mouth
corners, dark lip edges that curl up into a smile, whisker dots.  The upper lip is its own bone so it
lifts into a snarl over small white teeth and canines; the jaw opens and a pink tongue bone pokes out.
Coat: #7a3a1c -> #c06a33 hue-shifted ramp painted as directional hair strokes, darker dorsal stripe,
cream chest blaze / muzzle / cheeks, pink tummy, dark tail tip, pink inner ears.

Outfit: the red cable-knit sweater the Nona knitted: two shells over the barrel, a raised rope cable
down the spine between purl gutters, Aran side panels (a rope cable, a purl column, then the white
intarsia 'C' on stockinette, mirrored), ribbed rolled cuffs at the neck and tail end, and an open belly
(dog sweaters are) so 'belly_up' and 'beg' show the pink tummy.  A celeste collar (white saddle stitch,
gold buckle on the right) with a small gold name tag on its own swinging bone.
"""
import math

from mcmodel import Model, hash3, face_light, pick
from rig import Rig
from paint import hx, mix


def pal(*h):
    return [hx(c) for c in h]


# ------------------------------------------------------------------ palettes (dark -> light, hue shifted)
COAT = pal('#2a0f07', '#3d160a', '#52200f', '#672a15', '#7a3a1c', '#8c4422', '#a05129', '#b25d2f',
           '#c06a33', '#cd7b3e', '#da914e', '#e6a965')
LIGHT = pal('#7d4320', '#9a5728', '#b46c33', '#c98243', '#d99a57', '#e6b16d', '#f0c687', '#f8dcab')
BELLY = pal('#8a4a3a', '#b0685a', '#cf8a78', '#e2a690', '#efc0a8', '#f8d8c4')
SWEATER = pal('#2a0509', '#45080e', '#610d14', '#7e131a', '#9a1c20', '#b42828', '#c93a33', '#dc5445',
              '#ea735c')
YARN = pal('#8f857e', '#b8aea6', '#d8d0c6', '#eee8de', '#fbf8f1')
CELESTE = pal('#1d3f5c', '#2c5d84', '#3f7fae', '#5ea3d1', '#86c3e8', '#b4e0f6')
GOLD = pal('#3e2606', '#6b4510', '#9c6a1a', '#c99426', '#e7bd45', '#f8e08a', '#fff6cf')
NOSE = pal('#050304', '#0d090b', '#191215', '#2a2125', '#43383d', '#6e6268', '#a89ca3')
EYE = pal('#0c0503', '#1c0d06', '#34190b', '#4f2711', '#6d3817', '#8f4e1f', '#b0692b')
PINK = pal('#4a1520', '#7a2534', '#a83c4c', '#cf5e6c', '#e8848f', '#f6aab2')
TEETH = pal('#8a8378', '#c4bdb0', '#ece8de', '#fbfaf5')
MOUTH = pal('#12040a', '#2a0a12', '#4a1420', '#6e2232')
WHITE = hx('#ffffff')
GLINT2 = hx('#fff1dc')


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


def side(ctx):
    return getattr(ctx.cube, 'side', '')


def outward(ctx):
    """True on the side face that points away from the body midline (x)."""
    return (ctx.face == 'west' and side(ctx) == 'r') or (ctx.face == 'east' and side(ctx) == 'l')


def at(points):
    def fn(img, u0, v0, w, h):
        px = img.load()
        for i, j, c in points:
            if 0 <= i < w and 0 <= j < h:
                px[u0 + i, v0 + j] = c
    return fn


def art(rows, cols, ctx, default=None):
    """Look up a pixel-art grid by face texel; returns colour, None (transparent) or default."""
    if ctx.j < len(rows) and ctx.i < len(rows[ctx.j]):
        ch = rows[ctx.j][ctx.i]
        if ch in cols:
            c = cols[ch]
            return c(ctx) if callable(c) else c
    return default


# ------------------------------------------------------------------ fur
VERTICAL_FUR = ('leg', 'paw', 'thigh', 'ear', 'lobe', 'fold', 'neck')


def fur_noise(ctx, k=0.09):
    """Smooth short coat: 1-texel strokes 3 texels long in the direction the hair lies (back along the body and
    head, down the legs and ears), each stroke a little lighter or darker than its neighbours.  No static."""
    x, y, z = A(ctx)
    xi = math.floor(x)
    if tag(ctx) in VERTICAL_FUR:
        zi = math.floor(z)
        off = hash3(xi, zi, 0, 3) * 3
        a = hash3(xi, math.floor((y + off) / 3.0), zi, 11)
    else:
        yi = math.floor(y)
        off = hash3(xi, yi, 0, 3) * 3
        a = hash3(xi, yi, math.floor((z + off) / 3.0), 11)
    return (a - 0.5) * k * 1.1


def coat_v(ctx, base=0.6):
    v = base + face_light(ctx) * 1.05 + fur_noise(ctx)
    if ctx.face in ('west', 'east') and 0 not in ctx.cube.size:
        v += (0.35 - ctx.t) * 0.08                  # soft sheen on the upper half of every side
    if edge(ctx) == 0 and ctx.face not in ('top',) and 0 not in ctx.cube.size:
        v -= 0.05
    return v


def coat(ctx, base=0.6, stripe=True, light_below=None):
    """Red coat; darker dorsal stripe on top, optional blend to the light chest/muzzle colour below a y."""
    x, y, z = A(ctx)
    v = coat_v(ctx, base)
    if stripe and ctx.face == 'top' and abs(x) < 2.2:
        v -= 0.16 - abs(x) * 0.04
    c = pick(COAT, v)
    if light_below is not None and ctx.face != 'top':
        y0, y1 = light_below
        t = clamp((y - y0) / max(0.1, (y1 - y0)))
        if t > 0:
            c = mix(c, pick(LIGHT, v + 0.05), t)
    return c


# ------------------------------------------------------------------ body
def body_mat(ctx):
    x, y, z = A(ctx)
    t = tag(ctx)
    f = ctx.face
    if f == 'bottom':
        # pink tummy (seen in belly_up), furrier toward the chest
        v = 0.55 + fur_noise(ctx, 0.06)
        c = pick(BELLY, v)
        if z < -1:
            c = mix(c, pick(LIGHT, 0.6), clamp((-1 - z) / 4))
        return c
    if t == 'keel':
        return pick(LIGHT, coat_v(ctx, 0.62))
    if f == 'front':
        # proud chest: light cream blaze on the prow
        cx = abs(x) / 5.0
        c = coat(ctx, 0.62, False)
        return mix(c, pick(LIGHT, coat_v(ctx, 0.6)), clamp(1.15 - cx * 1.1 + (y - 14) * 0.08))
    if f == 'back':
        v = coat_v(ctx, 0.58) - abs(x) * 0.025 + (0.04 if y < 14 else 0)
        if abs(x) < 1.6 and y < 13.5:
            v -= 0.14                                   # tail root shadow / end of the dorsal stripe
        if abs(x) < 0.6 and y > 16.5:
            v -= 0.12                                   # crease between the haunches
        c = pick(COAT, v)
        if y > 17.5 and abs(x) > 0.6:
            c = mix(c, pick(LIGHT, v), 0.35)           # paler fur under the tail
        return c
    return coat(ctx, 0.6, light_below=(17.5, 20.5))


# ------------------------------------------------------------------ the sweater
C_ART = [
    ".WWWW",
    "WW..W",
    "WW...",
    "WW...",
    "WW..W",
    ".WWWW",
]


def knit_v(ctx, u, w):
    """Stockinette: wales run along the body (u = along-length index, w = across index).

    Each wale is a light row of V's; every V is broken by a darker texel every 2 stitches, alternating
    between wales so the rows read as interlocking loops rather than stripes."""
    v = 0.58 + face_light(ctx) * 0.9
    if w % 2 == 0:
        v += 0.06 if u % 2 == 0 else 0.0           # light wale, a V every 2 stitches
    else:
        v -= 0.05 if u % 2 == 0 else 0.02          # the shadow between wales
    return v


def roundness(ctx):
    """Side faces of the barrel: lighter on the shoulder of the curve, darker toward the belly."""
    if ctx.face in ('west', 'east'):
        return (0.45 - ctx.t) * 0.22
    return 0.0


CABLE = [          # rope cable, 4 stitches across, repeats every 4 rows along the spine
    "dLLm",
    "LLmd",
    "Lmdd",
    "mddL",
]


def cable_v(ctx, u, k):
    v = 0.62 + face_light(ctx) * 0.9
    ch = CABLE[u % 4][k]
    return v + {'L': 0.12, 'm': 0.0, 'd': -0.14}[ch]


def rib_v(ctx, w):
    return 0.5 + face_light(ctx) * 0.9 + (0.1 if w % 2 == 0 else -0.08)


def sweater_mat(ctx):
    f = ctx.face
    t = tag(ctx)
    x, y, z = A(ctx)
    if t == 'cuff':
        if f in ('front', 'back'):
            # ribbed rolled edge: ribs run around the opening
            return pick(SWEATER, rib_v(ctx, ctx.i) - 0.02)
        if f in ('west', 'east'):
            return pick(SWEATER, rib_v(ctx, ctx.j))
        return pick(SWEATER, rib_v(ctx, ctx.i))
    if f == 'bottom':
        # open belly: only the front chest band and the side wraps exist
        if z > -2.5 and 1 <= ctx.i <= ctx.w - 2:
            return None
        return pick(SWEATER, knit_v(ctx, ctx.j, ctx.i) - 0.12)
    if f in ('front', 'back'):
        return pick(SWEATER, rib_v(ctx, ctx.i) - 0.04)
    # along-length index (u) increases toward the tail on every face
    if f == 'top':
        u = ctx.j
        across = ctx.i
        n = ctx.w
        if t == 'shell_t':
            # cuffs at both ends
            if u <= 1 or u >= ctx.h - 2:
                return pick(SWEATER, rib_v(ctx, across))
            mid = (n - 4) // 2
            k = across - mid
            if 0 <= k < 4:
                return pick(SWEATER, 0.4)               # under the raised cable
            if k in (-1, 4):
                return pick(SWEATER, 0.38 + face_light(ctx) * 0.9 + (0.05 if u % 2 else 0))   # purl gutter
            return pick(SWEATER, knit_v(ctx, u, across))
        return pick(SWEATER, knit_v(ctx, u, across))
    # sides (u = 0 at the neck end on both sides): an Aran panel
    #   [rib][cable A][purl][ white C on stockinette ][purl][cable B][rib]
    u = (ctx.w - 1 - ctx.i) if f == 'west' else ctx.i
    j = ctx.j
    rnd = roundness(ctx)
    if u <= 0 or u >= ctx.w - 1:
        return pick(SWEATER, rib_v(ctx, j) + rnd)
    if t == 'shell_w':
        if 1 <= u <= 3 or 11 <= u <= 13:
            k = (u - 1) if u <= 3 else (2 - (u - 11))           # mirrored twist on the two cables
            return pick(SWEATER, cable_v(ctx, j, k) + rnd)
        if u in (4, 10):
            return pick(SWEATER, 0.4 + face_light(ctx) * 0.9 + (0.06 if j % 2 else -0.02) + rnd)  # purl
        ci = ctx.i - (ctx.w - 5) // 2
        cj = j - 1
        if 0 <= cj < 6 and 0 <= ci < 5:
            ch = C_ART[cj][ci]
            if ch == 'W':
                return pick(YARN, 0.66 + face_light(ctx) + (0.1 if (ci + cj) % 2 == 0 else -0.04) + rnd * 0.5)
    return pick(SWEATER, knit_v(ctx, u, j) + rnd)


def cable_mat(ctx):
    f = ctx.face
    if f == 'top':
        return pick(SWEATER, cable_v(ctx, ctx.j, min(3, ctx.i)))
    if f in ('west', 'east'):
        return pick(SWEATER, 0.5 + face_light(ctx) * 0.9 + (0.1 if ctx.i % 4 < 2 else -0.06))
    return pick(SWEATER, 0.45 + face_light(ctx) * 0.9)


# ------------------------------------------------------------------ neck, collar, tag
def neck_mat(ctx):
    x, y, z = A(ctx)
    if ctx.face == 'top':
        return coat(ctx, 0.6)
    return coat(ctx, 0.62, light_below=(12.5, 15.5)) if z < -7 else coat(ctx, 0.6)


def collar_mat(ctx):
    f = ctx.face
    v = 0.55 + face_light(ctx) * 1.0
    if ctx.j == 0 and f not in ('top', 'bottom'):
        v += 0.12
    c = pick(CELESTE, v)
    if f in ('front', 'back', 'west', 'east') and ctx.j == 1 and ctx.i % 2 == 0:
        c = mix(c, WHITE, 0.55)                        # white saddle stitching
    if f == 'west' and ctx.w >= 5 and ctx.i in (3, 4):
        c = GOLD[4] if ctx.j == 0 else GOLD[3]         # buckle on the right side
    return c


TAG_ART = ["hSG", "SGd", "Gdd"]


def tag_mat(ctx):
    if ctx.face == 'front':
        return art(TAG_ART, {'h': GOLD[5], 'S': GOLD[6], 'G': GOLD[4], 'd': GOLD[2], '.': None}, ctx, GOLD[3])
    if ctx.face == 'back':
        return GOLD[2]
    return GOLD[3]


# ------------------------------------------------------------------ head
def skull_mat(ctx):
    x, y, z = A(ctx)
    f = ctx.face
    if f == 'front':
        v = coat_v(ctx, 0.62)
        if abs(x) < 1.0 and y < 8.5:
            v -= 0.1                                    # soft stop groove between the eyes
        c = pick(COAT, v)
        if y > 10.3:
            c = mix(c, pick(LIGHT, v), clamp((y - 10.3) / 1.2))  # light cheeks under the eyes
        return c
    if f == 'bottom':
        return pick(LIGHT, coat_v(ctx, 0.55))
    if f in ('west', 'east'):
        if 5 <= y < 11 and z < -14:
            # the eye wraps round the corner of the skull so the profile still has an eye
            if z < -15:
                return EYE_SIDE[int(y - 5)]
            return pick(COAT, 0.36 if 5.5 < y < 10.5 else 0.44)
        c = coat(ctx, 0.6, False)
        if z < -12 and y > 10:
            c = mix(c, pick(LIGHT, coat_v(ctx, 0.6)), clamp((y - 10) / 2))
        return c
    return coat(ctx, 0.6)


def cheek_mat(ctx):
    """Chubby jowls under the eyes: light muzzle colour blending into the coat at the back."""
    x, y, z = A(ctx)
    v = coat_v(ctx, 0.6)
    if ctx.face == 'bottom':
        return pick(LIGHT, v - 0.05)
    c = pick(COAT, v)
    return mix(c, pick(LIGHT, v), clamp(0.9 - (z + 15) * 0.15))


def dome_mat(ctx):
    return coat(ctx, 0.62)


def muzzle_mat(ctx):
    x, y, z = A(ctx)
    f = ctx.face
    if f == 'top':
        v = coat_v(ctx, 0.66)
        if abs(x) < 1.0:
            v -= 0.06
        c = pick(COAT, v)
        return mix(c, pick(LIGHT, v), 0.25)
    if f == 'front':
        if ctx.j == ctx.h - 1 and ctx.i == ctx.w // 2:
            return COAT[1]                              # philtrum
        return pick(LIGHT, coat_v(ctx, 0.6))
    if f in ('west', 'east'):
        c = pick(LIGHT, coat_v(ctx, 0.56))
        u = (ctx.w - 1 - ctx.i) if f == 'west' else ctx.i   # 0 = front
        if (u, ctx.j) in ((3, 1),):
            c = pick(LIGHT, 0.3)                        # whisker dot
        return c
    return pick(LIGHT, coat_v(ctx, 0.5))


NOSE_ART = ["dSsKd", "KNdNK"]


def nose_mat(ctx):
    f = ctx.face
    if tag(ctx) == 'bulb':
        # leather bulb on top of the nose: the wet shine lives here
        if f == 'front':
            return [NOSE[5], NOSE[6], NOSE[4]][min(2, ctx.i)]
        if f == 'top':
            return NOSE[6] if ctx.i == 1 else NOSE[4]
        return NOSE[3]
    if f == 'front':
        return art(NOSE_ART, {'S': NOSE[6], 's': NOSE[4], 'K': NOSE[2], 'N': NOSE[0], 'd': NOSE[1]}, ctx, NOSE[2])
    if f == 'top':
        return NOSE[5] if 0 < ctx.i < ctx.w - 1 and ctx.j == ctx.h - 1 else NOSE[3]
    if f in ('west', 'east'):
        return NOSE[2] if ctx.j == 0 else NOSE[1]
    return NOSE[1]


def lips_mat(ctx):
    f = ctx.face
    if f == 'front':
        rows = ["..K..", ".k.k."]
        c = art(rows, {'K': COAT[1], 'k': COAT[5]}, ctx)
        return c or pick(LIGHT, coat_v(ctx, 0.62))
    if f in ('west', 'east'):
        u = (ctx.w - 1 - ctx.i) if f == 'west' else ctx.i   # 0 = front
        c = pick(LIGHT, coat_v(ctx, 0.58))
        if ctx.j == ctx.h - 1 and u < ctx.w - 1:
            c = COAT[1]                                 # dark lip edge
        if ctx.j == ctx.h - 2 and u == ctx.w - 1:
            c = COAT[1]                                 # ...curling up at the corner: a smile
        if ctx.j == 0 and u in (2, 4):
            c = pick(LIGHT, 0.3)                        # whisker dots
        return c
    if f == 'bottom':
        # roof of the mouth: pink with ridges
        return pick(PINK, 0.5 + (0.12 if ctx.j % 2 == 0 else 0))
    return pick(LIGHT, coat_v(ctx, 0.55))


def jaw_mat(ctx):
    f = ctx.face
    if f == 'top':
        return pick(MOUTH, 0.6)
    if f == 'front':
        return pick(LIGHT, coat_v(ctx, 0.6) - (0.12 if ctx.j == 0 else 0))
    if f in ('west', 'east'):
        return pick(LIGHT, coat_v(ctx, 0.5 if ctx.j == 0 else 0.58))
    return pick(LIGHT, coat_v(ctx, 0.5))


def mouth_mat(ctx):
    return pick(MOUTH, 0.25)


def tongue_mat(ctx):
    f = ctx.face
    v = 0.62 + face_light(ctx) * 0.8
    if f == 'top' and ctx.i == ctx.w // 2:
        v -= 0.18                                       # centre groove
    if f == 'front':
        v += 0.05
    return pick(PINK, v)


def teeth_mat(rows):
    def f(ctx):
        if ctx.face != 'front':
            return None
        ch = rows[ctx.j][ctx.i]
        return {'T': TEETH[3], 't': TEETH[2], 'g': PINK[2], 'm': MOUTH[1], '.': None}[ch]
    return f


# eyes: 4 x 5, the same glint side on both eyes (key light from the upper left)
EYE_ART = [
    "cKKKc",
    "KWWpK",
    "KWWpI",
    "IpPPI",
    "iIIIw",
    "cLLLc",
]


def eye_mat(ctx):
    f = ctx.face
    if f == 'front':
        return art(EYE_ART, {'c': lambda c: pick(COAT, 0.42), 'K': EYE[0], 'P': EYE[0], 'p': EYE[1], 'W': WHITE,
                             'w': GLINT2, 'I': EYE[3], 'i': EYE[4], 'L': EYE[5]}, ctx, EYE[1])
    return pick(COAT, 0.4 + face_light(ctx))            # lids blend into the face


EYE_SIDE = [EYE[0], WHITE, EYE[0], EYE[1], EYE[3], EYE[5]]
EYE_GLOW = [(i, j, WHITE if ch == 'W' else GLINT2) for j, row in enumerate(EYE_ART) for i, ch in enumerate(row)
            if ch in 'Ww']


def brow_mat(ctx):
    v = 0.66 + face_light(ctx) * 0.9
    return pick(LIGHT, v)


# ------------------------------------------------------------------ ears
def ear_mat(ctx):
    x, y, z = A(ctx)
    f = ctx.face
    lx, ly, lz = local(ctx)
    t = tag(ctx)
    if outward(ctx):
        # soft wavy feathering, darker leather tips
        v = 0.5 + fur_noise(ctx, 0.07)
        wave = math.sin(y * 0.9 + (z * 1.3)) * 0.05
        v += wave
        if t == 'lobe' or y > 13.5:
            v -= 0.1 + (y - 13.5) * 0.03
        if edge(ctx) == 0:
            v -= 0.07
        return pick(COAT, v)
    if f in ('west', 'east'):
        # inner ear: warm pink skin with fur edges
        if edge(ctx) == 0:
            return pick(COAT, 0.42)
        return mix(pick(PINK, 0.62), pick(LIGHT, 0.6), 0.45)
    if f == 'top':
        return pick(COAT, 0.62)
    if f == 'bottom':
        return pick(COAT, 0.3)
    return pick(COAT, 0.44 + fur_noise(ctx, 0.05))


# ------------------------------------------------------------------ legs, paws, tail
PAD_FRONT = [".PP.", ".PP.", "p..p", ".pp."]
PAD_BACK = [".P.", "PPP", "...", "p.p"]


def leg_mat(ctx):
    x, y, z = A(ctx)
    f = ctx.face
    t = tag(ctx)
    if t == 'paw':
        if f == 'bottom':
            rows = PAD_FRONT if ctx.w == 4 else PAD_BACK
            return art(rows, {'P': PINK[1], 'p': PINK[2]}, ctx, pick(LIGHT, 0.45))
        v = coat_v(ctx, 0.66)
        c = mix(pick(COAT, v), pick(LIGHT, v), 0.35)
        if f == 'front':
            if ctx.j == ctx.h - 1 and ctx.i % 2 == 0:
                c = NOSE[2]                             # tiny claws
            elif ctx.i % 2 == 1 and ctx.j == 0:
                c = pick(COAT, v - 0.15)                # toe split
        if f == 'top' and ctx.j == ctx.h - 1 and ctx.i % 2 == 1:
            c = pick(COAT, v - 0.15)
        return c
    if f == 'back':
        return pick(COAT, coat_v(ctx, 0.52))
    if t == 'thigh':
        return coat(ctx, 0.6)
    return coat(ctx, 0.6, False)


def tail_mat(ctx):
    x, y, z = A(ctx)
    t = tag(ctx)
    c = coat(ctx, 0.58 if t == 'tip' else 0.62)
    if t == 'tip':
        lx, ly, lz = local(ctx)
        if lz > ctx.cube.size[2] - 2:
            c = pick(COAT, coat_v(ctx, 0.36))           # dark tail tip
    return c


# ------------------------------------------------------------------ module contract
DEFAULT_MAT = body_mat
FOCUS = 'head'
DZ = -0.5          # authoring z -> model z (recentres the long dog on the entity origin)
HY = 1.0           # the whole head subtree sits this much lower than authored
HEAD_BONES = {'head', 'lips', 'jaw', 'tongue', 'right_brow', 'left_brow', 'right_ear', 'left_ear'}


def build():
    r = Rig()

    def box(bone, frm, size, mat=None, inflate=0.0, decals=None, name=None, side=''):
        dy = HY if bone in HEAD_BONES else 0.0
        c = r.box(bone, (frm[0], frm[1] + dy, frm[2] + DZ), size, mat=mat, inflate=inflate, decals=decals)
        c.a0 = tuple(float(v) for v in frm)            # materials work in authoring coordinates
        c.name = name
        c.side = side
        return c

    def bone(name, pivot, parent=None, rot=(0, 0, 0), mat=None):
        dy = HY if name in HEAD_BONES else 0.0
        return r.bone(name, (pivot[0], pivot[1] + dy, pivot[2] + DZ), parent=parent, rot=rot, mat=mat)

    # ---------------- body (root, pivot at the hips so sit / beg rotate around the rump)
    bone('body', (0, 16, 11), mat=body_mat)
    box('body', (-5, 12, -6), (10, 7, 22), name='core')
    box('body', (-4, 11, -4.5), (8, 9, 19), name='tall')
    box('body', (-2, 19, -6.6), (4, 2, 8), name='keel')
    # sweater: two shells (open belly), ribbed cuff rings at the neck and the tail end
    box('body', (-5, 12, -4.5), (10, 7, 15), mat=sweater_mat, inflate=0.55, name='shell_w')
    box('body', (-4, 11, -4.5), (8, 9, 15), mat=sweater_mat, inflate=0.55, name='shell_t')
    box('body', (-2, 9.8, -3.5), (4, 1, 13), mat=cable_mat, name='cable')
    box('body', (-5, 12, -5.2), (10, 7, 1), mat=sweater_mat, inflate=0.85, name='cuff')
    box('body', (-4, 11, -5.2), (8, 9, 1), mat=sweater_mat, inflate=0.85, name='cuff')
    box('body', (-5, 12, 10.2), (10, 7, 1), mat=sweater_mat, inflate=0.8, name='cuff')
    box('body', (-4, 11, 10.2), (8, 9, 1), mat=sweater_mat, inflate=0.8, name='cuff')

    # ---------------- legs
    for sd, sx in (('right', -1), ('left', 1)):
        fl = f'{sd}_front_leg'
        cx = 2.6 * sx
        bone(fl, (cx, 18, -2.5), parent='body', mat=leg_mat)
        box(fl, (cx - 1.5, 16.5, -4), (3, 6, 3), name='leg', side=sd[0])
        box(fl, (cx - 2, 22, -5.5), (4, 2, 4), name='paw', side=sd[0])
        bl = f'{sd}_back_leg'
        cx = 3.0 * sx
        bone(bl, (cx, 16, 12.5), parent='body', mat=leg_mat)
        box(bl, (cx - 2 + 0.6 * sx, 14.5, 10), (4, 5, 5), name='thigh', side=sd[0])
        box(bl, (cx - 1.5 + 0.3 * sx, 19.5, 11.5), (3, 3, 3), name='leg', side=sd[0])
        box(bl, (cx - 1.5 + 0.3 * sx, 22, 10.5), (3, 2, 4), name='paw', side=sd[0])

    # ---------------- tail (raised, happy curve)
    bone('tail', (0, 12.8, 15.5), parent='body', rot=(32, 0, 0), mat=tail_mat)
    box('tail', (-1.5, 11.3, 15), (3, 3, 6), name='base')
    bone('tail_tip', (0, 12.8, 20.5), parent='tail', rot=(18, 0, 0), mat=tail_mat)
    box('tail_tip', (-1, 11.8, 20), (2, 2, 5), name='tip')

    # ---------------- neck, collar, tag
    bone('neck', (0, 13, -4.5), parent='body', mat=neck_mat)
    box('neck', (-3, 9, -11), (6, 7, 6), name='neck')
    box('neck', (-3.5, 13.4, -11.5), (7, 2, 7), mat=collar_mat, inflate=0.15, name='collar')
    bone('tag', (0, 15.5, -11.9), parent='neck', mat=tag_mat)
    box('tag', (-1.5, 15.3, -12.3), (3, 3, 1), name='tag')

    # ---------------- head
    bone('head', (0, 11, -8.5), parent='neck', mat=skull_mat)
    box('head', (-6, 4, -16), (12, 9, 9), name='skull',
        decals={'eyes:west': at([(8, 2, WHITE)]), 'eyes:east': at([(0, 2, WHITE)])})
    box('head', (-5, 3, -15), (10, 1, 7), mat=dome_mat, name='dome')
    box('head', (-6.5, 9, -15.2), (13, 3, 7), mat=cheek_mat, name='cheek')
    box('head', (-2.5, 9.5, -23), (5, 2, 7), mat=muzzle_mat, name='muzzle')
    box('head', (-2.5, 9, -23.6), (5, 2, 1), mat=nose_mat, name='nose')
    box('head', (-1.5, 8.5, -23.3), (3, 1, 1), mat=nose_mat, name='bulb')
    for sd, x0 in (('r', -6.5), ('l', 1.5)):
        box('head', (x0, 5, -16.3), (5, 6, 1), mat=eye_mat, name='eye', side=sd,
            decals={'eyes:front': at(EYE_GLOW)})
    box('head', (-2.5, 11.5, -22.7), (5, 2, 0), mat=teeth_mat(["TgggT", "TtgtT"]), name='teeth')
    box('head', (-2, 11.7, -22.4), (4, 2, 6), mat=mouth_mat, name='mouth')

    bone('lips', (0, 11.5, -16), parent='head', mat=lips_mat)
    box('lips', (-2.5, 11.5, -23), (5, 2, 7), inflate=0.06, name='lips')

    bone('jaw', (0, 13.5, -16), parent='head', mat=jaw_mat)
    box('jaw', (-2, 13.5, -22.4), (4, 2, 6), name='jaw')
    box('jaw', (-2, 12.5, -22.1), (4, 1, 0), mat=teeth_mat(["T..T"]), name='teeth')
    bone('tongue', (0, 13.5, -17), parent='jaw', mat=tongue_mat)
    box('tongue', (-1.5, 13.1, -22), (3, 1, 5), name='tongue')

    for sd, sx in (('right', -1), ('left', 1)):
        b = f'{sd}_brow'
        bx = 4.0 * sx
        bone(b, (bx, 4.0, -16.2), parent='head', rot=(0, 0, 9 * sx), mat=brow_mat)
        box(b, (bx - 1.5, 3.5, -16.8), (3, 1, 1), name='brow', side=sd[0])

    for sd, sx in (('right', -1), ('left', 1)):
        e = f'{sd}_ear'
        ex = 6.0 * sx
        bone(e, (ex, 5.0, -10.5), parent='head', rot=(0, -10 * sx, 12 * -sx), mat=ear_mat)
        x0 = ex if sx > 0 else ex - 2
        box(e, (x0, 4.5, -13.5), (2, 10, 6), name='ear', side=sd[0])
        box(e, (x0, 14.5, -12.5), (2, 2, 4), name='lobe', side=sd[0])
        box(e, (x0, 3.9, -13), (2, 2, 5), inflate=0.25, name='fold', side=sd[0])

    m = Model('choripan', 128, 128, r.roots)
    m.scale = 0.5
    return m


POSES = {
    'sit': {'body': (-0.34, 0, 0, 0, 3.06, 0),
            'right_front_leg': (0.34, 0, 0.04, 0, 1.6, 0), 'left_front_leg': (0.34, 0, -0.04, 0, 1.6, 0),
            'right_back_leg': (-1.25, 0.25, 0, 0, 1.6, 0), 'left_back_leg': (-1.25, -0.25, 0, 0, 1.6, 0),
            'neck': (0.16, 0, 0, 0, 0, 0), 'head': (0.08, 0, 0, 0, 0, 0),
            'tail': (-0.95, 0.6, 0, 0, 0, 0), 'tail_tip': (-0.25, 0.35, 0, 0, 0, 0)},
    'beg': {'body': (-1.2, 0, 0, 0, 2.25, 0),
            'right_front_leg': (0.95, 0.1, 0.22, 0, -0.6, 0), 'left_front_leg': (0.95, -0.1, -0.22, 0, -0.6, 0),
            'right_back_leg': (-0.1, 0.3, 0, 0, -0.9, 0), 'left_back_leg': (-0.1, -0.3, 0, 0, -0.9, 0),
            'neck': (0.62, 0, 0, 0, 0, 0), 'head': (0.3, 0, 0, 0, 0, 0),
            'right_ear': (0.2, 0, 0, 0, 0, 0), 'left_ear': (0.2, 0, 0, 0, 0, 0),
            'right_brow': (0, 0, 0.15, 0, -0.3, 0), 'left_brow': (0, 0, -0.15, 0, -0.3, 0),
            'jaw': (0.16, 0, 0, 0, 0, 0), 'tongue': (0.6, 0, 0, 0, 0.6, -1.7),
            'tail': (1.45, 0.35, 0, 0, 0, 0), 'tail_tip': (-0.25, 0.3, 0, 0, 0, 0)},
    'belly_up': {'body': (0, 0, math.pi, 0, 1.6, 0),
                 'right_front_leg': (0.45, 0, -0.2, 0, 0, 0), 'left_front_leg': (0.6, 0, 0.3, 0, 0, 0),
                 'right_back_leg': (-0.45, 0, -0.45, 0, 0, 0), 'left_back_leg': (-0.3, 0, 0.5, 0, 0, 0),
                 'neck': (1.3, 0, 0, 0, 0, 0), 'head': (-0.7, 0, 0.3, 0, 0, 0),
                 'right_ear': (0, 0, -1.8, 0, 0, 0), 'left_ear': (0, 0, 1.8, 0, 0, 0),
                 'jaw': (0.12, 0, 0, 0, 0, 0), 'tongue': (-0.15, 0.85, 0, 1.2, 0.2, -1.0),
                 'right_brow': (0, 0, 0.12, 0, -0.3, 0), 'left_brow': (0, 0, -0.12, 0, -0.3, 0),
                 'tail': (-0.9, 0.5, 0, 0, 0, 0), 'tail_tip': (0, 0.4, 0, 0, 0, 0)},
    'tilt': {'head': (0, 0, 0.38, 0, 0, 0), 'left_ear': (0, 0, -0.9, 0, 0, 0),
             'left_brow': (0, 0, -0.3, 0, -0.4, 0), 'right_brow': (0, 0, 0.2, 0, 0, 0)},
    'growl': {'neck': (0.35, 0, 0, 0, 0.5, 0), 'head': (0.1, 0, 0, 0, 0, 0),
              'lips': (-0.1, 0, 0, 0, -1.4, 0), 'jaw': (0.07, 0, 0, 0, 0, 0),
              'right_brow': (0, 0, -0.45, 0, 0.3, 0), 'left_brow': (0, 0, 0.45, 0, 0.3, 0),
              'right_ear': (0, -0.4, 0.3, 0, 0, 0), 'left_ear': (0, 0.4, -0.3, 0, 0, 0),
              'tail': (-0.6, 0, 0, 0, 0, 0), 'body': (0.06, 0, 0, 0, 0.6, 0)},
}

ANIM_NOTES = """Choripan (normal form) -- animation notes.  Units: radians, offsets in model texels (2x density
inside scale_root, so 2 texels = 1 vanilla pixel).  t = ageInTicks, s = walk speed 0..1, all poses are ADDED to the
rest pose.  He is the comic relief and the audience's sweetheart: everything is bouncy, quick and overshooting
(springs, never linear eases), and the TAIL NEVER STOPS unless he is scared or growling.

Bones (17)
* body (root, pivot at the HIPS): the sausage + sweater + raised spine cable.  Idle: breathing dy = sin(t*0.16)*0.15
  and xRot = sin(t*0.16)*0.012.  Walk (wolf-like follow AI): low trot, dy = -abs(sin(walk*2))*0.35*s, roll
  zRot = sin(walk)*0.04*s; the long body never pitches while walking.  Run: add xRot = sin(walk*2)*0.05 (the
  sausage rocks like a see-saw around the hips).  Sit / beg / belly_up move it through the poses below.
* right_front_leg, left_front_leg, right_back_leg, left_back_leg: one bone per stubby leg (pivot at the shoulder /
  hip, thigh haunch is part of the back leg).  Walk: diagonal pairs (right_front with left_back), xRot =
  +-sin(walk)*0.9*s -- big swings on short legs make the comic 'scurry'; at s > 0.7 switch to a gallop (front pair
  together, back pair together, half a cycle apart).  Idle: still; every 6-10 s lift one front paw (xRot -0.5,
  dy -0.5) for 10 ticks.
* tail, tail_tip: THE happiness meter.  Wag = yRot sin(t*1.4)*0.55 on tail and the same with 2 ticks of lag and
  x1.4 amplitude on tail_tip (a whip).  Excited (player near, holding food, after a pet): frequency x1.6, amplitude
  0.8, and let the body follow with zRot = -tail.yRot*0.08 (the whole butt wags).  Scared / growl: tail xRot -0.6
  (low), no wag.  In sit / beg / belly_up the tail lies on the floor and sweeps it (yRot only).
* neck: carries the head.  Takes 40% of the head-look pitch.  Sniff: neck xRot +0.35 (nose down) while walking.
* tag: the gold name tag on the celeste collar.  Pendulum from the body motion: xRot = spring(-body accel)*0.6,
  plus a tiny jingle (xRot 0.25) on every footstep; zRot follows head shakes.
* head: 60% of the head-look (yaw and pitch).  Tilt on demand (pose 'tilt'), alternating sides, when the player
  talks (voice capture), crouches or calls him.  Sneeze: head xRot +0.3 snap + body dy +0.4 in 2 ticks.
  Transformation start (beat 9): from 'sit', head yRot ramps to PI over 20 ticks with a 2-tick hitch every 45
  degrees (wet cracks) -- then the demon model takes over.
* lips: the upper lip/flews.  Only moves for the snarl: dy -1.4, xRot -0.1 (pose 'growl') reveals the upper
  teeth and canines; add a quiver dy += sin(t*3)*0.15 while growling.
* jaw: lower jaw (pivot at the hinge).  Bark: xRot 0.35 open in 1 tick, close in 2 (with a head jolt xRot -0.08).
  Pant (warm, after running, beg / belly_up): xRot 0.12 + sin(t*0.9)*0.06.  Growl: 0.07 (teeth just apart).
* tongue: hidden inside the mouth at rest.  Pant / beg: pose values (xRot 0.6, dy 0.6, dz -1.7) so it hangs out
  over the chin, bobbing with the pant.  belly_up: lolls out the side (yRot 0.85).  Lick (after a treat):
  dz -2 and xRot -0.3 then back, 6 ticks.
* right_brow, left_brow: the little tan eyebrow tufts.  Default: inner ends up (puppy eyes).  Worried / dog-sense:
  both dy -0.4 and inner ends rise more (zRot +-0.15).  Tilt: the brow on the raised side lifts (dy -0.4).
  Growl: furrowed (zRot -+0.45, dy +0.3).  Random 'eyebrow dance' every 4-8 s: one brow dy -0.3 for 8 ticks.
* right_ear, left_ear: huge floppy ears, pivot at the top of the skull.  Spring pendulums: zRot/xRot follow head
  and body acceleration with 3-4 ticks of lag and overshoot (amplitude up to 0.6 while running so they flap like
  wings).  Alert (a sound, hallucination tell): both xRot -0.3, yRot outward 0.2 (ears perked).  Tilt: the ear on
  the high side flips up (zRot -+0.9) showing the pink inside.  Growl: pinned back (yRot +-0.4).
* Emissive layer 'eyes': the 2x2 + 1px glints on both eyes and a 1px glint where each eye wraps round the side of
  the skull.  Keep them full-bright so the eyes sparkle in the flashlight; this is his whole charm at night.

Poses
* sit: hips on the floor, chest up, front legs straight (pose stretches them 1.6 to keep the paws on the floor),
  hind legs folded forward, tail curled on the floor to one side.  Use when the player stands still near him, and
  as the starting pose of the transformation.
* beg: sitting up on his hind legs, belly out (the open-bellied sweater shows his pink tummy), front paws curled in
  front of the chest showing the toe beans, head up, tongue out.  Trigger: player holding any chorizo / choripan
  item within 4 blocks.  Animate: paws paddle (front legs xRot +-0.15, alternating, 6-tick period), body sways
  zRot sin(t*0.3)*0.05.
* belly_up: on his back for 'rascar la panza' (right-click while sitting): legs in the air, hind legs splayed, head
  upside down with the chin up and the tongue lolling, ears flopped onto the floor.  Animate: the legs kick
  (random leg xRot +-0.3 bursts, the classic leg-scratch reflex while being rubbed), tail sweeps the floor, body
  wiggles zRot +-0.1.
* tilt: the confused head tilt (0.38 rad) with one ear flipped up and one brow raised.
* growl: dog-sense tell.  Head and neck low, body dropped 0.6 at the front, upper lip lifted over small teeth,
  furrowed brows, ears pinned back, tail low and still.  Hold it facing the stairs / empty corner where the
  hallucination will happen; rumble jaw quiver.  Funny because he is tiny and wearing a sweater.

Close-up portrait = FOCUS 'head' in rest or 'tilt': big wet eyes, black shiny nose, brows, floppy ears.
"""
