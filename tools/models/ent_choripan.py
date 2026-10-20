"""Choripan -- the Morales family dachshund, normal form (DEAD LINE, case 20 'La Muneca').

Authored at 2x texel density (model.scale = 0.5).  +Y down, ground y = 24, faces -Z, right_* on -X.

Design
------
The dog the audience has to fall in love with before he turns into a 4.5-block worm-dog, so every
choice is about charm.  About 0.62 blocks tall and 1.25 blocks from nose to rump (plus the tail).
A long low red sausage: core + taller/narrower barrel give a rounded cross-section, a chest prow and a
low keel give the proud dachshund chest, and a rump cap rounds the back end.  Four stubby legs, each
with its own paw bone (toe beans, tiny claws) so paws can curl in 'beg' and flop in 'belly_up'.  A plush
oversized head (13 wide, puppy proportions) on a short neck, huge floppy ears hanging to chest level,
chubby cream jowls, and a long whip tail (two bones) carried up in a happy curve.

Face (the 'aww' close-up), laid out so the eyes and the nose never overlap in any view:
* big glossy BROWN eyes (6x6) on their own cubes that bulge a little past the skull: a dark-brown upper
  lid, a warm iris that runs from dark chestnut under the lid to amber at the bottom, a 2x2 pupil with a
  big cream glint on its upper-left edge, a second 1-px glint low-right in the iris and a pale peach wet
  line on the lower lid.  The eye cubes are 2 deep and their outer side is painted too (iris + glint),
  so the profile has a real eye.  Only 2 px per eye are emissive (warm #fff1dc) so at night they
  sparkle instead of glowing like a hostile mob's.
* a light tan stop band under the eyes, then the long muzzle coming out of chubby cream jowls BELOW the
  eye line; a big shiny black nose (1 texel wider than the muzzle, a rounded leather bulb on top with a
  crisp wet highlight, nostrils, a black underside); a single dark philtrum + mouth line; thin tan
  eyebrow planes (puppy-worried at rest, raised in 'tilt', furrowed in 'growl').
* the upper lip is its own bone: it lifts in 'growl' to show the upper teeth row, two real canine cubes
  and pink gums painted on the sides of the mouth (they show in profile too); the jaw opens and a pink
  tongue bone pokes out.
Coat: #7a3a1c -> #c06a33 hue-shifted ramp painted as soft directional hair strokes, darker dorsal stripe,
cream chest / muzzle / jowls, pink tummy, dark tail tip, pink inner ears with wavy locks on the outside.

Outfit: the red Aran sweater the Nona knitted: two shells over the barrel, a raised rope cable down the
spine between purl gutters, chevron stockinette, side panels with two 4-px S-twist rope cables framing
a cream 'C' with a dark-red outline (reads at night), ribbed cuffs at the neck and tail ends, and an open
belly (dog sweaters are) so 'belly_up' and 'beg' show the pink tummy.  A celeste collar (white saddle
stitch, gold buckle on the right) sits low on the throat so it shows under the chin, with a small
bone-shaped gold name tag (engraved line) on its own swinging bone.
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
NOSE = pal('#020102', '#08060a', '#110d10', '#1c1619', '#2b2327', '#463c42', '#776c72', '#f4eef0')
PINK = pal('#4a1520', '#7a2534', '#a83c4c', '#cf5e6c', '#e8848f', '#f6aab2')
TEETH = pal('#8a8378', '#c4bdb0', '#ece8de', '#fbfaf5')
MOUTH = pal('#12040a', '#2a0a12', '#4a1420', '#6e2232')
WHITE = hx('#ffffff')

# eyes
EYE_LID = hx('#2e1409')
EYE_RING = [hx('#2e1409'), hx('#33170a'), hx('#3d1c0c'), hx('#47220e'), hx('#52290f')]
IRIS = [hx('#5f2e12'), hx('#7e3f18'), hx('#a95e24'), hx('#d08a40')]
PUPIL = hx('#100604')
GLINT = hx('#fff4e2')          # big glint in the base texture: cream, not pure white
GLINT_SOFT = hx('#e9cdb0')     # the rest of the 2x2 glint: soft, so the eye still reads brown
GLINT2 = hx('#ffe2bc')
GLOW = hx('#fff1dc')           # the only emissive pixels: warm
WET = hx('#d99a72')            # pale peach wet line on the lower lid
WET_D = hx('#b57a52')


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


def front_u(ctx):
    """Side faces: texel column counted from the cube's front (-Z) edge."""
    return (ctx.w - 1 - ctx.i) if ctx.face == 'west' else ctx.i


def at(points):
    def fn(img, u0, v0, w, h):
        px = img.load()
        for i, j, c in points:
            if 0 <= i < w and 0 <= j < h:
                px[u0 + i, v0 + j] = c
    return fn


def art(rows, cols, ctx, default=None, i=None, j=None):
    """Look up a pixel-art grid by face texel; returns colour, None (transparent) or default."""
    i = ctx.i if i is None else i
    j = ctx.j if j is None else j
    if 0 <= j < len(rows) and 0 <= i < len(rows[j]):
        ch = rows[j][i]
        if ch in cols:
            c = cols[ch]
            return c(ctx) if callable(c) else c
    return default


# ------------------------------------------------------------------ fur
VERTICAL_FUR = ('leg', 'paw', 'thigh', 'ear', 'lobe', 'fold', 'neck')


def fur_noise(ctx, k=0.09):
    """Smooth short coat: 1-texel strokes 3 texels long in the direction the hair lies (back along the body and
    head, down the legs and ears), each stroke a little lighter or darker than its neighbours.  No static.
    Vertical parts (legs, ears, neck) get half the contrast so they read as fur, not wood grain."""
    x, y, z = A(ctx)
    xi = math.floor(x)
    if tag(ctx) in VERTICAL_FUR:
        zi = math.floor(z)
        off = hash3(xi, zi, 0, 3) * 3
        a = hash3(xi, math.floor((y + off) / 3.0), zi, 11)
        return (a - 0.5) * k * 0.5
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
    if t == 'prow':
        if f == 'front':
            # proud chest: cream blaze, a little darker at the rim so the prow reads as a rounded bulge
            v = coat_v(ctx, 0.6) - (0.08 if edge(ctx) == 0 else 0) - clamp((16 - y) / 3) * 0.1
            return mix(pick(COAT, v), pick(LIGHT, v), clamp(0.9 - abs(x) * 0.35) * clamp((y - 15) / 3))
        if f == 'top':
            return coat(ctx, 0.6)
        return mix(coat(ctx, 0.6, False), pick(LIGHT, coat_v(ctx, 0.58)), clamp((y - 15) / 3))
    if t == 'rump':
        if f == 'back':
            v = coat_v(ctx, 0.56) - abs(x) * 0.02 - (0.06 if edge(ctx) == 0 else 0)
            if abs(x) < 0.6 and y > 15.5:
                v -= 0.12                                   # crease between the haunches
            c = pick(COAT, v)
            if y > 16.5 and abs(x) > 0.6:
                c = mix(c, pick(LIGHT, v), 0.35)           # paler fur under the tail
            return c
        return coat(ctx, 0.6, light_below=(17, 19))
    if f == 'front':
        cx = abs(x) / 5.0
        c = coat(ctx, 0.62, False)
        return mix(c, pick(LIGHT, coat_v(ctx, 0.6)), clamp(1.15 - cx * 1.1 + (y - 14) * 0.08))
    if f == 'back':
        v = coat_v(ctx, 0.56) - abs(x) * 0.025 + (0.04 if y < 14 else 0)
        if abs(x) < 1.6 and y < 13.5:
            v -= 0.14                                   # tail root shadow / end of the dorsal stripe
        return pick(COAT, v)
    return coat(ctx, 0.6, light_below=(17.5, 20.5))


# ------------------------------------------------------------------ the sweater
C_MASK = [".CC", "C..", "C..", "C..", ".CC"]             # 3x5 letter, placed at (1, 1) of a 5x7 block
_C = {(r + 1, c + 1) for r, row in enumerate(C_MASK) for c, ch in enumerate(row) if ch == 'C'}
_C_OUT = {(r, c) for r in range(7) for c in range(5)
          if (r, c) not in _C and any((r + a, c + b) in _C for a, b in ((-1, 0), (1, 0), (0, -1), (0, 1)))}

STOCK = ["LmmL", "sLLs", "dssd"]          # chevron stockinette: a light V over a darker gap, 4 x 3 repeat
CABLE = ["dHLs", "dmHL", "sdmH", "Lsdm"]  # 4-px rope cable, S-twist: lit strand, shadow at the crossing
KNIT_D = {'H': 0.2, 'L': 0.11, 'm': 0.0, 's': -0.1, 'd': -0.2}


def knit_v(ctx, u, j):
    """Stockinette V chevrons; u = across-wale index, j = course index."""
    v = 0.6 + face_light(ctx) * 0.9
    return v + KNIT_D[STOCK[j % 3][u % 4]]


def cable_v(ctx, k, j):
    """Rope cable column k (0..3) at row j."""
    v = 0.6 + face_light(ctx) * 0.9 + KNIT_D[CABLE[j % 4][k]]
    if k in (0, 3):
        v -= 0.04                                   # the rope is round: darker at its edges
    return v


def purl_v(ctx, j):
    return 0.42 + face_light(ctx) * 0.9 + (0.05 if j % 2 else -0.03)


def rib_v(ctx, w):
    return 0.5 + face_light(ctx) * 0.9 + (0.1 if w % 2 == 0 else -0.08)


def roundness(ctx):
    """Side faces of the barrel: lighter on the shoulder of the curve, darker toward the belly."""
    if ctx.face in ('west', 'east'):
        return (0.45 - ctx.t) * 0.24
    return 0.0


def sweater_mat(ctx):
    f = ctx.face
    t = tag(ctx)
    x, y, z = A(ctx)
    if t == 'cuff':
        if f in ('front', 'back'):
            return pick(SWEATER, rib_v(ctx, ctx.i) - 0.02)   # ribbed rolled edge, ribs run round the opening
        if f in ('west', 'east'):
            return pick(SWEATER, rib_v(ctx, ctx.j))
        return pick(SWEATER, rib_v(ctx, ctx.i))
    if f == 'bottom':
        # open belly: only the front chest band and the side wraps exist
        if z > -2.5 and 1 <= ctx.i <= ctx.w - 2:
            return None
        return pick(SWEATER, knit_v(ctx, ctx.i, ctx.j) - 0.12)
    if f in ('front', 'back'):
        return pick(SWEATER, rib_v(ctx, ctx.i) - 0.04)
    if f == 'top':
        u = ctx.j                                   # along the spine
        across = ctx.i
        n = ctx.w
        if t == 'shell_t':
            mid = (n - 4) // 2
            k = across - mid
            if 0 <= k < 4:
                return pick(SWEATER, 0.4)           # under the raised spine cable
            if k in (-1, 4):
                return pick(SWEATER, purl_v(ctx, u))
            # chevrons point away from the spine on both sides
            a = (mid - 2 - across) if k < 0 else (across - mid - 5)
            return pick(SWEATER, knit_v(ctx, u, a))
        return pick(SWEATER, knit_v(ctx, u, ctx.i))
    # sides: an Aran panel  [cable A 4][purl][ cream C with a dark-red outline ][purl][cable B 4]
    u = front_u(ctx)                                 # 0 at the neck end on both sides
    j = ctx.j
    rnd = roundness(ctx)
    if t == 'shell_w':
        if u <= 3:
            return pick(SWEATER, cable_v(ctx, u if f == 'east' else 3 - u, j) + rnd)
        if u >= 11:
            k = u - 11
            return pick(SWEATER, cable_v(ctx, k if f == 'east' else 3 - k, j) + rnd)
        if u in (4, 10):
            return pick(SWEATER, purl_v(ctx, j) + rnd)
        ci = ctx.i - (ctx.w - 5) // 2
        if 0 <= ci < 5 and 0 <= j < 7:
            if (j, ci) in _C:
                return pick(YARN, 0.72 + face_light(ctx) * 0.8 + (0.08 if (ci + j) % 2 == 0 else -0.04) + rnd * 0.5)
            if (j, ci) in _C_OUT:
                return pick(SWEATER, 0.27 + rnd * 0.3)
        return pick(SWEATER, knit_v(ctx, u, j) + rnd)
    # shell_t sides only peek out above / below shell_w: chevron knit
    return pick(SWEATER, knit_v(ctx, u, j) + rnd - 0.03)


def cable_mat(ctx):
    f = ctx.face
    if f == 'top':
        return pick(SWEATER, cable_v(ctx, min(3, ctx.i), ctx.j) + 0.04)
    if f in ('west', 'east'):
        return pick(SWEATER, 0.48 + face_light(ctx) * 0.9 + (0.1 if ctx.i % 4 < 2 else -0.06))
    return pick(SWEATER, 0.45 + face_light(ctx) * 0.9)


# ------------------------------------------------------------------ neck, collar, tag
def neck_mat(ctx):
    x, y, z = A(ctx)
    if ctx.face == 'top':
        return coat(ctx, 0.6)
    if ctx.face == 'bottom':
        return pick(LIGHT, coat_v(ctx, 0.55))
    return coat(ctx, 0.62, light_below=(12.5, 16.5)) if z < -7 else coat(ctx, 0.6, light_below=(14, 18))


def collar_mat(ctx):
    f = ctx.face
    v = 0.55 + face_light(ctx) * 1.0
    if ctx.j == 0 and f not in ('top', 'bottom'):
        v += 0.12
    c = pick(CELESTE, v)
    if f in ('front', 'back', 'west', 'east') and ctx.j == 1 and ctx.i % 2 == 0:
        c = mix(c, WHITE, 0.55)                        # white saddle stitching
    if f == 'front' and ctx.i == ctx.w // 2 and ctx.j == 1:
        c = GOLD[4]                                    # the D-ring the tag hangs from
    if f == 'west' and ctx.w >= 5 and ctx.i in (3, 4):
        c = GOLD[5] if ctx.j == 0 else GOLD[3]         # buckle on the right side
    return c


TAG_ART = ["..rr..",
           "hS..SG",
           ".GeeG.",
           "Gd..dd"]
TAG_COLS = {'h': GOLD[6], 'S': GOLD[5], 'G': GOLD[4], 'd': GOLD[2], 'e': GOLD[1], 'r': GOLD[3]}


def tag_mat(ctx):
    """Bone-shaped gold name tag (alpha cutout), engraved line along the shaft."""
    f = ctx.face
    if f == 'front':
        return art(TAG_ART, TAG_COLS, ctx)
    if f == 'back':
        return art(TAG_ART, {'h': GOLD[3], 'S': GOLD[3], 'G': GOLD[3], 'd': GOLD[2], 'e': GOLD[3], 'r': GOLD[2]}, ctx,
                   i=ctx.w - 1 - ctx.i)
    if f in ('west', 'east'):
        col = 0 if f == 'west' else 5
        return GOLD[3] if TAG_ART[ctx.j][col] != '.' else None
    row = 0 if f == 'top' else 3
    return (GOLD[5] if f == 'top' else GOLD[2]) if TAG_ART[row][ctx.i] != '.' else None


# ------------------------------------------------------------------ head
def skull_mat(ctx):
    x, y, z = A(ctx)
    f = ctx.face
    if f == 'front':
        v = coat_v(ctx, 0.62)
        if abs(x) < 0.5 and 5 <= y < 10:
            v -= 0.08                                   # soft stop groove between the eyes
        if 4 <= y < 5 and abs(x) < 2:
            v += 0.05                                   # light forehead between the brows
        return pick(COAT, v)
    if f == 'bottom':
        return pick(LIGHT, coat_v(ctx, 0.55))
    if f in ('west', 'east'):
        c = coat(ctx, 0.6, False)
        if z < -12 and y > 10.5:
            c = mix(c, pick(LIGHT, coat_v(ctx, 0.6)), clamp((y - 10.5) / 2))
        return c
    return coat(ctx, 0.6)


def cheek_mat(ctx):
    """Chubby cream jowls under the eyes with the muzzle coming out of them; a light stop band on top."""
    x, y, z = A(ctx)
    f = ctx.face
    v = coat_v(ctx, 0.62)
    if f == 'bottom':
        return pick(LIGHT, v - 0.05)
    if f == 'top':
        return pick(LIGHT, v + 0.04) if z < -14 else coat(ctx, 0.6, False)
    if f == 'front':
        if ctx.j == 0 and abs(x) < 3.5:
            return pick(LIGHT, 0.7)                     # the stop band between the eyes and the nose
        c = mix(pick(COAT, v), pick(LIGHT, v + 0.04), clamp(1.0 - abs(x) * 0.17))
        if ctx.j == 2 and abs(x) in (3.5, 4.5):
            c = pick(LIGHT, 0.28)                       # whisker dots
        if edge(ctx) == 0 and ctx.j > 0:
            c = mix(c, pick(COAT, 0.45), 0.35)
        return c
    # sides: coat at the back blending to cream jowls at the front and bottom
    c = pick(COAT, v)
    return mix(c, pick(LIGHT, v), clamp((-13 - z) * 0.18 + (y - 12.5) * 0.18))


def dome_mat(ctx):
    return coat(ctx, 0.63)


def muzzle_mat(ctx):
    x, y, z = A(ctx)
    f = ctx.face
    if f == 'top':
        v = coat_v(ctx, 0.66)
        c = pick(COAT, v)
        return mix(c, pick(LIGHT, v), 0.3 + clamp((-z - 17) * 0.08) + (0.2 if abs(x) < 1 else 0))
    if f in ('west', 'east'):
        c = pick(LIGHT, coat_v(ctx, 0.56))
        u = front_u(ctx)
        if (u, ctx.j) in ((2, 1), (4, 1), (3, 0)):
            c = pick(LIGHT, 0.28)                       # whisker dots
        return c
    return pick(LIGHT, coat_v(ctx, 0.5))


NOSE_ART = ["kmskkk",
            "kNkkNk"]
NOSE_COLS = {'k': NOSE[2], 'm': NOSE[6], 's': NOSE[4], 'N': NOSE[0]}


def nose_mat(ctx):
    f = ctx.face
    if tag(ctx) == 'bulb':
        # leather bulb on top of the nose: the crisp wet highlight lives here
        if f == 'front':
            return [NOSE[3], NOSE[7], NOSE[5], NOSE[2]][min(3, ctx.i)]
        if f == 'top':
            return NOSE[6] if ctx.i == 1 else NOSE[3]
        return NOSE[2]
    if f == 'front':
        return art(NOSE_ART, NOSE_COLS, ctx, NOSE[2])
    if f == 'top':
        return NOSE[5] if ctx.i in (1, 2) and ctx.j == ctx.h - 1 else NOSE[3]
    if f == 'bottom':
        return NOSE[0]                                  # dark underside
    if f in ('west', 'east'):
        return NOSE[3] if ctx.j == 0 else NOSE[1]
    return NOSE[1]


LIPS_FRONT = ["..K..",
              "k.K.k"]


def lips_mat(ctx):
    f = ctx.face
    if f == 'front':
        c = art(LIPS_FRONT, {'K': COAT[2], 'k': COAT[4]}, ctx)
        return c or pick(LIGHT, coat_v(ctx, 0.62))
    if f in ('west', 'east'):
        u = front_u(ctx)
        c = pick(LIGHT, coat_v(ctx, 0.58))
        if ctx.j == ctx.h - 1 and u < ctx.w - 1:
            c = COAT[2]                                 # dark lip edge
        if ctx.j == ctx.h - 2 and u == ctx.w - 1:
            c = COAT[2]                                 # ...curling up at the corner: a smile
        if ctx.j == 0 and u in (2, 4):
            c = pick(LIGHT, 0.28)                       # whisker dots
        return c
    if f == 'bottom':
        return pick(PINK, 0.5 + (0.12 if ctx.j % 2 == 0 else 0))   # roof of the mouth with ridges
    return pick(LIGHT, coat_v(ctx, 0.55))


def jaw_mat(ctx):
    f = ctx.face
    x, y, z = A(ctx)
    if f == 'top':
        return pick(MOUTH, 0.6)
    if f == 'front':
        return pick(LIGHT, coat_v(ctx, 0.62) - (0.12 if ctx.j == 0 else 0))
    if f in ('west', 'east'):
        if ctx.j == 0 and z < -16:
            return COAT[3]                              # lower lip line
        return pick(LIGHT, coat_v(ctx, 0.56))
    return pick(LIGHT, coat_v(ctx, 0.52))


def mouth_mat(ctx):
    """Dark mouth box under the upper lip; its sides carry gums + upper teeth for the profile snarl."""
    f = ctx.face
    if f in ('west', 'east'):
        u = front_u(ctx)
        if ctx.j == ctx.h - 1:
            if u == 0:
                return TEETH[3]
            return TEETH[2] if u % 2 else TEETH[1]
        return pick(PINK, 0.42 if u % 2 else 0.5)
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


def canine_mat(ctx):
    if ctx.face == 'bottom' or ctx.face == 'front':
        return TEETH[3]
    return TEETH[2]


# eyes: 6 x 6.  Same glint side on both eyes (key light from the upper left).
EYE_ART = [
    "cLLLLc",
    "L1111L",
    "rWVK2r",
    "rVKKwr",
    "r4444r",
    "cqppqc",
]
EYE_SIDE = ["LL", "1r", "Wr", "3r", "4r", "pc"]     # outer side face, column 0 = front edge


def _eye_cols(j):
    return {'c': lambda ctx: pick(COAT, 0.36), 'L': EYE_LID, 'W': GLINT, 'V': GLINT_SOFT, 'w': GLINT2,
            'K': PUPIL, '1': IRIS[0], '2': IRIS[1], '3': IRIS[2], '4': IRIS[3], 'p': WET, 'q': WET_D,
            'r': EYE_RING[min(j, 4)]}


def eye_mat(ctx):
    f = ctx.face
    if f == 'front':
        return art(EYE_ART, _eye_cols(ctx.j), ctx, IRIS[0])
    if outward(ctx):
        u = front_u(ctx)
        return art(EYE_SIDE, _eye_cols(ctx.j), ctx, IRIS[0], i=u)
    if f == 'top':
        return EYE_LID
    if f == 'bottom':
        return pick(LIGHT, 0.6)
    return pick(COAT, 0.4 + face_light(ctx))


EYE_GLOW = [(1, 2, GLOW), (4, 3, GLOW)]           # only 2 px per eye are full-bright


def brow_mat(ctx):
    return pick(LIGHT, 0.7)


# ------------------------------------------------------------------ ears
EAR_LOCKS = {(1, 6), (2, 7), (2, 8), (1, 9),       # 3 wavy lock lines near the tip (u from front, row)
             (3, 5), (4, 6), (4, 7), (3, 8), (3, 9),
             (5, 7), (5, 8)}


def ear_mat(ctx):
    x, y, z = A(ctx)
    f = ctx.face
    t = tag(ctx)
    if outward(ctx):
        u = front_u(ctx)
        # form shading: lighter at the top front, darker toward the bottom and the back edge
        v = 0.6 + fur_noise(ctx, 0.07) - clamp((y - 6) / 12) * 0.16 - u * 0.012
        if t == 'lobe':
            v -= 0.12
        if t == 'ear' and (u, ctx.j) in EAR_LOCKS:
            v -= 0.11
        if edge(ctx) == 0:
            v -= 0.06
        return pick(COAT, v)
    if f in ('west', 'east'):
        # inner ear: warm pink skin with fur edges
        if edge(ctx) == 0:
            return pick(COAT, 0.42)
        return mix(pick(PINK, 0.62), pick(LIGHT, 0.6), 0.45)
    if f == 'top':
        return pick(COAT, 0.62)
    if f == 'bottom':
        return pick(COAT, 0.32)
    return pick(COAT, 0.44 + fur_noise(ctx, 0.05) - (0.06 if f == 'back' else 0))


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
                c = NOSE[3]                             # tiny claws
            elif ctx.i % 2 == 1 and ctx.j == 0:
                c = pick(COAT, v - 0.15)                # toe split
        if f == 'top' and ctx.j == ctx.h - 1 and ctx.i % 2 == 1:
            c = pick(COAT, v - 0.15)
        return c
    # form shading: lighter on top/front, darker toward the ankle and the back
    v = coat_v(ctx, 0.62) - clamp((y - 16) / 7) * 0.1
    if f == 'back':
        v -= 0.07
    if t == 'thigh':
        if f in ('west', 'east') and ctx.t < 0.35:
            v += 0.04
        return pick(COAT, v)
    return pick(COAT, v)


def tail_mat(ctx):
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
    box('body', (-3, 13, -7.2), (6, 6, 3), name='prow')
    box('body', (-4, 12.5, 15.5), (8, 6, 2), name='rump')
    # sweater: two shells (open belly), raised spine cable, ribbed cuff rings at the neck and the tail end
    box('body', (-5, 12, -4.5), (10, 7, 15), mat=sweater_mat, inflate=0.55, name='shell_w')
    box('body', (-4, 11, -4.5), (8, 9, 15), mat=sweater_mat, inflate=0.55, name='shell_t')
    box('body', (-2, 9.8, -3.5), (4, 1, 13), mat=cable_mat, name='cable')
    box('body', (-5, 12, -5.2), (10, 7, 1), mat=sweater_mat, inflate=1.0, name='cuff')
    box('body', (-4, 11, -5.2), (8, 9, 1), mat=sweater_mat, inflate=1.0, name='cuff')
    box('body', (-5, 12, 10.2), (10, 7, 1), mat=sweater_mat, inflate=0.8, name='cuff')
    box('body', (-4, 11, 10.2), (8, 9, 1), mat=sweater_mat, inflate=0.8, name='cuff')

    # ---------------- legs + paws (paw bones pivot at the wrist / ankle)
    for sd, sx in (('right', -1), ('left', 1)):
        fl = f'{sd}_front_leg'
        cx = 2.6 * sx
        bone(fl, (cx, 18, -2.5), parent='body', mat=leg_mat)
        box(fl, (cx - 1.5, 16.5, -4), (3, 6, 3), name='leg', side=sd[0])
        fp = f'{sd}_front_paw'
        bone(fp, (cx, 22.2, -2.5), parent=fl, mat=leg_mat)
        box(fp, (cx - 2, 22, -5.5), (4, 2, 4), name='paw', side=sd[0])
        bl = f'{sd}_back_leg'
        cx = 3.0 * sx
        bone(bl, (cx, 16, 12.5), parent='body', mat=leg_mat)
        box(bl, (cx - 2 + 0.6 * sx, 14.5, 10), (4, 5, 5), name='thigh', side=sd[0])
        box(bl, (cx - 1.5 + 0.3 * sx, 19.5, 11.5), (3, 3, 3), name='leg', side=sd[0])
        bp = f'{sd}_back_paw'
        bone(bp, (cx + 0.3 * sx, 22.2, 13), parent=bl, mat=leg_mat)
        box(bp, (cx - 1.5 + 0.3 * sx, 22, 10.5), (3, 2, 4), name='paw', side=sd[0])

    # ---------------- tail (raised, happy curve)
    bone('tail', (0, 12.8, 15.5), parent='body', rot=(32, 0, 0), mat=tail_mat)
    box('tail', (-1.5, 11.3, 15), (3, 3, 6), name='base')
    bone('tail_tip', (0, 12.8, 20.5), parent='tail', rot=(18, 0, 0), mat=tail_mat)
    box('tail_tip', (-1, 11.8, 20), (2, 2, 5), name='tip')

    # ---------------- neck, collar (low on the throat), bone-shaped tag
    bone('neck', (0, 13, -4.5), parent='body', mat=neck_mat)
    box('neck', (-3, 9, -11), (6, 9, 6), name='neck')
    box('neck', (-3.5, 15, -11.5), (7, 2, 7), mat=collar_mat, inflate=0.2, name='collar')
    bone('tag', (0, 17.2, -11.9), parent='neck', mat=tag_mat)
    box('tag', (-3, 17.4, -12.4), (6, 4, 1), name='tag')

    # ---------------- head
    bone('head', (0, 11, -8.5), parent='neck', mat=skull_mat)
    box('head', (-6.5, 4, -16), (13, 9, 9), name='skull')
    box('head', (-5.5, 3, -15), (11, 1, 7), mat=dome_mat, name='dome')
    box('head', (-6, 11, -16.5), (12, 4, 6), mat=cheek_mat, name='cheek')
    box('head', (-2.5, 12.5, -23), (5, 2, 7), mat=muzzle_mat, name='muzzle')
    box('head', (-1.5, 11.5, -20), (3, 1, 4), mat=muzzle_mat, name='bridge')
    box('head', (-3, 12.5, -23.6), (6, 2, 1), mat=nose_mat, name='nose')
    box('head', (-2, 12, -23.35), (4, 1, 1), mat=nose_mat, name='bulb')
    for sd, x0 in (('r', -7.3), ('l', 1.3)):
        box('head', (x0, 5, -16.3), (6, 6, 2), mat=eye_mat, name='eye', side=sd,
            decals={'eyes:front': at(EYE_GLOW)})
    box('head', (-2.5, 14.5, -22.75), (5, 2, 0), mat=teeth_mat(["TgggT", "TtgtT"]), name='teeth')
    box('head', (-2.5, 15.5, -22.65), (1, 1, 1), mat=canine_mat, name='canine')
    box('head', (1.5, 15.5, -22.65), (1, 1, 1), mat=canine_mat, name='canine')
    box('head', (-2, 14.7, -22.4), (4, 2, 6), mat=mouth_mat, inflate=-0.1, name='mouth')

    bone('lips', (0, 14.5, -16), parent='head', mat=lips_mat)
    box('lips', (-2.5, 14.5, -23), (5, 2, 7), inflate=0.06, name='lips')

    bone('jaw', (0, 16.5, -16), parent='head', mat=jaw_mat)
    box('jaw', (-2, 16.5, -22.4), (4, 2, 10), name='jaw')
    box('jaw', (-2, 15.5, -22.1), (4, 1, 0), mat=teeth_mat(["T..T"]), name='teeth')
    bone('tongue', (0, 16.5, -17), parent='jaw', mat=tongue_mat)
    box('tongue', (-1.5, 16.1, -22), (3, 1, 5), name='tongue')

    for sd, sx in (('right', -1), ('left', 1)):
        b = f'{sd}_brow'
        bx = 4.3 * sx
        bone(b, (bx, 4.5, -16.45), parent='head', rot=(0, 0, 9 * sx), mat=brow_mat)
        box(b, (bx - 1.5, 4, -16.45), (3, 1, 0), name='brow', side=sd[0])

    for sd, sx in (('right', -1), ('left', 1)):
        e = f'{sd}_ear'
        ex = 6.5 * sx
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
    'beg': {'body': (-1.2, 0, 0, 0, 1.04, 0),
            'right_front_leg': (0.95, 0.1, 0.22, 0, -0.6, 0), 'left_front_leg': (0.95, -0.1, -0.22, 0, -0.6, 0),
            'right_front_paw': (1.2, 0, 0, 0, 0, 0), 'left_front_paw': (1.2, 0, 0, 0, 0, 0),
            'right_back_leg': (-0.25, 0.3, 0, 0, 0, 2.05), 'left_back_leg': (-0.25, -0.3, 0, 0, 0, 2.05),
            'right_back_paw': (1.35, 0, 0, 0, 0, 0), 'left_back_paw': (1.35, 0, 0, 0, 0, 0),
            'neck': (0.62, 0, 0, 0, 0, 0), 'head': (0.3, 0, 0, 0, 0, 0),
            'right_ear': (0.2, 0, 0, 0, 0, 0), 'left_ear': (0.2, 0, 0, 0, 0, 0),
            'right_brow': (0, 0, 0.15, 0, -0.3, 0), 'left_brow': (0, 0, -0.15, 0, -0.3, 0),
            'jaw': (0.16, 0, 0, 0, 0, 0), 'tongue': (0.6, 0, 0, 0, 0.6, -1.7), 'tag': (-0.9, 0, 0, 0, 0, 0),
            'tail': (1.45, 0.35, 0, 0, 0, 0), 'tail_tip': (-0.25, 0.3, 0, 0, 0, 0)},
    'belly_up': {'body': (0, 0, math.pi, 0, 1.6, 0),
                 'right_front_leg': (0.45, 0, -0.2, 0, 0, 0), 'left_front_leg': (0.6, 0, 0.3, 0, 0, 0),
                 'right_front_paw': (1.0, 0, 0, 0, 0, 0), 'left_front_paw': (1.0, 0, 0, 0, 0, 0),
                 'right_back_leg': (-0.45, 0, -0.45, 0, 0, 0), 'left_back_leg': (-0.3, 0, 0.5, 0, 0, 0),
                 'right_back_paw': (1.0, 0, 0, 0, 0, 0), 'left_back_paw': (1.0, 0, 0, 0, 0, 0),
                 'neck': (1.3, 0, 0, 0, 0, 0), 'head': (-0.7, 0, 0.3, 0, 0, 0),
                 'right_ear': (0, 0, -1.8, 0, 0, 0), 'left_ear': (0, 0, 1.8, 0, 0, 0),
                 'jaw': (0.12, 0, 0, 0, 0, 0), 'tongue': (-0.15, 0.85, 0, 1.2, 0.2, -1.0),
                 'right_brow': (0, 0, 0.12, 0, -0.3, 0), 'left_brow': (0, 0, -0.12, 0, -0.3, 0),
                 'tail': (-0.9, 0.5, 0, 0, 0, 0), 'tail_tip': (0, 0.4, 0, 0, 0, 0)},
    'tilt': {'head': (0, 0, 0.38, 0, 0, 0), 'right_ear': (0, 0, -2.3, 0, 0, 0),
             'right_brow': (0, 0, -0.2, 0, -0.4, 0), 'left_brow': (0, 0, -0.1, 0, 0, 0)},
    'growl': {'body': (0.07, 0, 0, 0, 0, 0),
              'right_front_leg': (-0.07, 0, 0, 0, -1.1, 0), 'left_front_leg': (-0.07, 0, 0, 0, -1.1, 0),
              'right_back_leg': (-0.07, 0, 0, 0, 0, 0), 'left_back_leg': (-0.07, 0, 0, 0, 0, 0),
              'neck': (0.2, 0, 0, 0, 0, 0), 'head': (-0.3, 0, 0, 0, 0, 0), 'tag': (0.6, 0, 0, 0, 0, 0),
              'lips': (-0.1, 0, 0, 0, -1.4, 0), 'jaw': (0.1, 0, 0, 0, 0, 0),
              'right_brow': (0, 0, -0.45, 0, 0.3, 0), 'left_brow': (0, 0, 0.45, 0, 0.3, 0),
              'right_ear': (0.35, 0, -0.15, 0, 0, 0), 'left_ear': (0.35, 0, 0.15, 0, 0, 0),
              'tail': (-0.6, 0, 0, 0, 0, 0)},
    'turn': {'body': (-0.34, 0, 0, 0, 3.06, 0),
             'right_front_leg': (0.34, 0, 0.04, 0, 1.6, 0), 'left_front_leg': (0.34, 0, -0.04, 0, 1.6, 0),
             'right_back_leg': (-1.25, 0.25, 0, 0, 1.6, 0), 'left_back_leg': (-1.25, -0.25, 0, 0, 1.6, 0),
             'neck': (-0.8, 0, 0, 0, 0, 0), 'head': (0, math.pi, 0, 0, -3, 0),
             'tail': (-0.95, 0.6, 0, 0, 0, 0), 'tail_tip': (-0.25, 0.35, 0, 0, 0, 0)},
}

ANIM_NOTES = """(rewritten below)"""
