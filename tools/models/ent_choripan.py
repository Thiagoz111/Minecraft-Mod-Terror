"""Choripan -- the Morales family dachshund, host #1 of CASO 2 'Casa Morales' (DEAD LINE).  DOG form of ChoripanEntity.

Authored at 2x texel density (model.scale = 0.5).  +Y down, ground y = 24, faces -Z, right_* on -X.

Design
------
The dog the audience has to fall in love with before he turns into a 4.5-block worm-dog (ent_choripan_demonio), so
every choice is about charm -- until 3:33, when he stands up on two legs, turns his head all the way round and says in
a deep voice "¿Quién es un buen chico?... YO NO."  About 0.62 blocks tall and 1.25 blocks from nose to rump (plus the
tail).  A long low red sausage: core + taller/narrower barrel give a rounded cross-section, a chest prow and a low keel
give the proud dachshund chest, and a rump cap rounds the back end.  Four stubby legs, each with its own paw bone (toe
beans, tiny claws) so paws can curl in 'beg' and flop in 'belly_up'.  A plush oversized head (13 wide, puppy
proportions) on a short neck, huge floppy ears hanging to chest level, chubby cream jowls, and a long whip tail (two
bones) carried up in a happy curve.

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
* closed lids (toggle 'eyelids', shown in 'sleep' and 'sneeze'): fur-coloured lid caps over both eyes with a
  curved dark lash line -- the content little "u u" of a sleeping puppy.
Coat: #7a3a1c -> #c06a33 hue-shifted ramp painted as soft directional hair strokes, darker dorsal stripe,
cream chest / muzzle / jowls, pink tummy, dark tail tip, pink inner ears with wavy locks on the outside.

Outfit: the red Aran sweater the Nona knitted: two shells over the barrel, a raised rope cable down the
spine between purl gutters, chevron stockinette, side panels with two 4-px S-twist rope cables framing
a cream 'C' with a dark-red outline (reads at night), ribbed cuffs at the neck and tail ends, and an open
belly (dog sweaters are) so 'belly_up' and 'beg' show the pink tummy.  A celeste collar (white saddle
stitch, gold buckle on the right) sits low on the throat so it shows under the chin.

The name tag (BIBLIA: "la chapita 'CHORIPÁN' tiene que leerse"): a gold tag hanging plumb from a split ring under
the chin, the SAME design as the demon form's big brass tag (ent_choripan_demonio) so the audience recognises it after
the transformation: rounded corners, bevelled rim, "CHORI" / "PÁN" engraved in two lines.  A
3x5 font needs 17 x 14 texels and there are only ~4.8 texels between the throat and the floor, so the engraved face is
a HIGH-DENSITY PLATE: a (17, 14, 10) box with CubeDeformation -5 renders as a 7 x 4 x 0 card (2.4 x 3.5 texels per
unit; the font is drawn 6 rows tall so the letters keep a 0.7 aspect), laid 0.05 in front of a normal-density gold
backing (rim, rounded corners, scratched back).  Box UV ignores the deformation, so the 17 x 14 face keeps every texel.

Looks (VARIANT_MATS): 'normal' (the sweater) and 'bufanda' (the ending, casa.desayuno + the base: the demon shredded
the sweater, so in the last look he wears the Nona's red SCARF instead -- the sweater texels are transparent in that
texture and the 'scarf' toggle bone is shown: a chunky garter-stitch wrap on the shoulders that rides over the collar
at the nape, a fat knot on his left under the chin and two long tails with cream bands and fringe hanging down his
left side, too long for a sausage dog -- the collar, the D-ring and the tag stay visible in front of it).
"""
import math
import os
import sys

import numpy as np

from mcmodel import Model, hash3, fbm, vnoise, face_light, pick, rot_matrix
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
GLOW2 = hx('#f3d6b4')          # the small second glint, a step dimmer
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


def _face_axes(ctx):
    """(u, v, w) authoring coordinates of a texel: u = the direction the hair lies in on this face, v = across it,
    w = the face's constant coordinate.  Hair runs back along the body / head (z), down the legs, ears and neck (y)."""
    x, y, z = A(ctx)
    f = ctx.face
    vertical = tag(ctx) in VERTICAL_FUR
    if f in ('west', 'east'):
        return (y, z, x) if vertical else (z, y, x)
    if f in ('top', 'bottom'):
        return (z, x, y)
    return (y, x, z)                                    # front / back: hair falls down


def fur_noise(ctx, k=0.09):
    """Short smooth coat: staggered 2-texel TICKS in the direction the hair lies, two tones only (a lighter tick
    catching the light, a darker one in the gap) on about half the texels; the rest is the clean base tone.  Every
    other row is offset by one texel so the ticks interlock like a short-haired coat instead of lining up into the
    long horizontal stripes of wood grain."""
    u, v, w = _face_axes(ctx)
    vi = math.floor(v)
    cell = math.floor((u + (vi % 2)) / 2.0)
    a = hash3(vi, cell, math.floor(w), 11)
    amt = k * (0.62 if tag(ctx) in VERTICAL_FUR else 0.8)
    if a > 0.74:
        return amt
    if a < 0.26:
        return -amt
    return 0.0


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
    if stripe and ctx.face == 'top':
        if abs(x) < 0.5:
            v += 0.07                                   # the spine ridge catches the light
        elif abs(x) < 2.6:
            v -= 0.12 - abs(x) * 0.02                   # darker saddle either side of it
    c = pick(COAT, v)
    if light_below is not None and ctx.face != 'top':
        y0, y1 = light_below
        t = clamp((y - y0) / max(0.1, (y1 - y0)))
        if t > 0:
            c = mix(c, pick(LIGHT, v + 0.05), t)
    return c


# ------------------------------------------------------------------ body
def _blob(a, b, ca, cb, ra, rb):
    """1 at the centre of an ellipse, falling to 0 at its rim."""
    d = ((a - ca) / ra) ** 2 + ((b - cb) / rb) ** 2
    return clamp(1.0 - d)


# hand-placed coat tufts: (face, cube tag, side, list of (u from the cube's front edge, row, +-step))
CHEST_TUFT = [(2, 4, 1), (3, 5, 1), (4, 4, 1), (3, 3, -1), (1, 3, 1), (5, 3, 1)]


def body_mat(ctx):
    """Bare coat on the barrel (only seen in the 'bufanda' look and round the sweater): form shading so it reads as
    a round, short-haired dog and not a plank -- a lit spine ridge, lighter masses over the shoulder and the haunch,
    a darker band where the barrel turns under, and the cream chest carried back under the belly to the pink tummy."""
    x, y, z = A(ctx)
    t = tag(ctx)
    f = ctx.face
    if f == 'bottom':
        # cream chest fur carried back under the barrel, the pink tummy behind the ribs (seen in belly_up)
        v = 0.6 + fur_noise(ctx, 0.07)
        c = pick(BELLY, v - 0.04)
        cream = pick(LIGHT, v + 0.02)
        c = mix(cream, c, clamp((z - 3.5) / 4))
        if abs(x) > 3.6:
            c = mix(c, pick(LIGHT, v - 0.12), 0.6)       # the flanks turning up into the side
        return c
    if t == 'keel':
        v = coat_v(ctx, 0.66)
        if f == 'front' and ctx.j == 0:
            v += 0.05
        return pick(LIGHT, v)
    if t == 'prow':
        if f == 'front':
            # proud chest: cream blaze with a hand-placed V tuft, darker at the rim so the prow reads as a bulge
            v = coat_v(ctx, 0.62) - (0.07 if edge(ctx) == 0 else 0) - clamp((16 - y) / 3) * 0.08
            for i, j, s in CHEST_TUFT:
                if (ctx.i, ctx.j) == (i, j):
                    v += 0.09 * s
            return mix(pick(COAT, v), pick(LIGHT, v + 0.04), clamp(1.0 - abs(x) * 0.3) * clamp((y - 14.5) / 2.5))
        if f == 'top':
            return coat(ctx, 0.6)
        return mix(coat(ctx, 0.6, False), pick(LIGHT, coat_v(ctx, 0.6)), clamp((y - 15) / 3))
    if t == 'rump':
        if f == 'back':
            v = coat_v(ctx, 0.56) - abs(x) * 0.02 - (0.06 if edge(ctx) == 0 else 0)
            v += _blob(x, y, 0, 13.5, 4, 2.2) * 0.06            # the round top of the rump
            if abs(x) < 0.6 and y > 15.5:
                v -= 0.12                                   # crease between the haunches
            c = pick(COAT, v)
            if y > 16.5 and abs(x) > 0.6:
                c = mix(c, pick(LIGHT, v), 0.35)           # paler fur under the tail
            return c
        v = coat_v(ctx, 0.6) + _blob(z, y, 16, 13.8, 3, 2.5) * 0.07
        c = pick(COAT, v)
        return mix(c, pick(LIGHT, v), clamp((y - 17) / 2))
    if f == 'front':
        cx = abs(x) / 5.0
        c = coat(ctx, 0.62, False)
        return mix(c, pick(LIGHT, coat_v(ctx, 0.62)), clamp(1.15 - cx * 1.1 + (y - 14) * 0.08))
    if f == 'back':
        v = coat_v(ctx, 0.56) - abs(x) * 0.025 + (0.04 if y < 14 else 0)
        if abs(x) < 1.6 and y < 13.5:
            v -= 0.14                                   # tail root shadow / end of the dorsal stripe
        return pick(COAT, v)
    if f == 'top':
        return coat(ctx, 0.6)
    # the flanks
    v = coat_v(ctx, 0.6)
    v += _blob(z, y, -1.5, 13.6, 4.2, 2.6) * 0.08          # shoulder mass
    v += _blob(z, y, 12.0, 13.8, 4.0, 2.6) * 0.08          # haunch mass
    v -= _blob(z, y, 5.0, 14.2, 3.5, 1.4) * 0.04           # the soft hollow of the ribs behind the shoulder
    if t == 'tall':
        # the 1-texel strips of the taller box show above (spine) and below (belly) the core
        if y > 19:
            return pick(LIGHT, coat_v(ctx, 0.48))
        return pick(COAT, v + 0.04)
    if 16.8 <= y < 18.8:
        v -= 0.09                                       # the barrel turning under: a darker 2-texel band
    c = pick(COAT, v)
    if y >= 18.8:
        c = mix(c, pick(LIGHT, v - 0.06), 0.7)          # pale belly fringe on the last row
    elif z < -3.5 and y > 15:
        c = mix(c, pick(LIGHT, v), clamp((-3.5 - z) / 3) * clamp((y - 15) / 3))   # the chest cream wraps the side
    return c


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
    if t == 'bib':
        # the turtleneck chest panel (brings the red to the front view): k1p1 ribs running down, a fat rolled
        # edge on top under the collar, shadowed where it tucks between the forelegs
        if f == 'front':
            v = rib_v(ctx, ctx.i) + 0.04
            if ctx.j <= 1:
                v = 0.62 + face_light(ctx) * 0.9 + (0.08 if ctx.j == 0 else -0.02) + (0.05 if ctx.i % 2 else 0)
            v -= clamp((ctx.j - 4) / 3) * 0.1
            if ctx.i in (0, ctx.w - 1):
                v -= 0.06
            return pick(SWEATER, v)
        if f == 'top':
            return pick(SWEATER, 0.66 + (0.05 if ctx.i % 2 else 0))
        return pick(SWEATER, rib_v(ctx, ctx.j) - 0.06)
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
NECK_TUFT = {(1, 6): 1, (2, 7): 1, (1, 7): -1, (3, 8): 1, (2, 8): -1}   # (u from front, row): a ruff behind the jaw


def neck_mat(ctx):
    x, y, z = A(ctx)
    if ctx.face == 'top':
        return coat(ctx, 0.6)
    if ctx.face == 'bottom':
        return pick(LIGHT, coat_v(ctx, 0.6))
    if ctx.face in ('west', 'east'):
        s = NECK_TUFT.get((front_u(ctx), ctx.j))
        if s:
            v = coat_v(ctx, 0.62) + 0.1 * s
            return mix(pick(COAT, v), pick(LIGHT, v), 0.5 if s > 0 else 0.2)
    return coat(ctx, 0.62, light_below=(12.5, 16.5)) if z < -7 else coat(ctx, 0.6, light_below=(14, 18))


def twist_mat(ctx):
    """Toggle 'neck_twist' (bipedal_180 only): the neck fur WRUNG like a towel -- two dark helical creases with a
    lit ridge beside each, wrapping round the neck axis; everything else transparent so the coat shows through."""
    if ctx.face in ('front', 'back'):
        return None
    x, y, z = A(ctx)
    phi = math.atan2(y - 13.5, x) / (2 * math.pi)
    ph = (z / 4.5 + 2 * phi) % 1.0
    if ph < 0.18:
        return pick(COAT, 0.16)
    if ph < 0.32:
        return pick(COAT, 0.34)
    if 0.42 < ph < 0.56:
        return pick(LIGHT, 0.42)
    return None


def collar_mat(ctx):
    """Celeste nylon band: light top edge, white saddle stitch down the middle, gold buckle on the right side,
    gold D-ring at the throat (bottom end of the slab, where the tag hangs)."""
    f = ctx.face
    x, y, z = A(ctx)
    v = 0.56 + face_light(ctx) * 1.0
    if f in ('west', 'east'):
        # 2 wide x 11 long: edges lighter/darker, stitching on the inner column
        v += 0.1 if front_u(ctx) == 1 else -0.04
        c = pick(CELESTE, v)
        if front_u(ctx) == 0 and ctx.j % 2 == 0:
            c = mix(c, WHITE, 0.55)
        if f == 'west' and 3 <= ctx.j <= 5:
            c = GOLD[5] if ctx.j == 3 else GOLD[3]       # buckle on the right side of the neck
        return c
    if f in ('front', 'back'):
        c = pick(CELESTE, v + (0.08 if ctx.i in (0, ctx.w - 1) else 0))
        if ctx.i == ctx.w // 2 and ctx.j % 2 == 0:
            c = mix(c, WHITE, 0.55)
        if f == 'front' and ctx.j == ctx.h - 1 and ctx.i == ctx.w // 2:
            c = GOLD[4]                                  # D-ring
        return c
    c = pick(CELESTE, v)
    if ctx.i == ctx.w // 2:
        c = mix(c, WHITE, 0.5)
    return c


# The name tag.  Same lettering as the demon form's tag (ent_choripan_demonio): 3-wide glyphs (N is 4 wide: a 3-wide N
# reads as H), here 6 rows tall because the high-density card squeezes rows harder than columns (see build()).
FONT6 = {
    'C': [".##", "#..", "#..", "#..", "#..", ".##"],
    'H': ["#.#", "#.#", "###", "#.#", "#.#", "#.#"],
    'O': [".#.", "#.#", "#.#", "#.#", "#.#", ".#."],
    'R': ["##.", "#.#", "#.#", "##.", "#.#", "#.#"],
    'I': ["#", "#", "#", "#", "#", "#"],
    'P': ["##.", "#.#", "#.#", "##.", "#..", "#.."],
    'A': [".#.", "#.#", "#.#", "###", "#.#", "#.#"],
    'N': ["#..#", "##.#", "##.#", "#.##", "#.##", "#..#"],
}
TXT_W, TXT_H = 19, 16              # 1-texel margin, "CHORI" rows 1-6, gap, the accent row, "PAN" rows 9-14, margin
TXT_K = 6.0                        # CubeDeformation of the card: (19, 16, 12) -> 7 x 4 x 0
ENGRAVE = hx('#1c0f05')


def _tag_text():
    rows = [[0] * TXT_W for _ in range(TXT_H)]

    def put(word, x0, y0):
        x = x0
        for ch in word:
            g = FONT6[ch]
            for j, r in enumerate(g):
                for i, c in enumerate(r):
                    if c == '#':
                        rows[y0 + j][x + i] = 1
            x += len(g[0]) + 1

    put('CHORI', 1, 1)
    w2 = sum(len(FONT6[c][0]) for c in 'PAN') + 2
    x2 = 1 + (TXT_W - 2 - w2) // 2
    put('PAN', x2, 9)
    rows[8][x2 + len(FONT6['P'][0]) + 1 + 2] = 1          # the acute accent: up-right of the A's apex
    return rows


TAG_TXT = _tag_text()


def tag_text_mat(ctx):
    """The engraved face (high-density card): letters cut flat-dark into polished gold, the gold lighter toward the
    top, a soft sheen line in the gap between the two words.  Only the front face exists (the card has zero
    thickness; its back is transparent so it never z-fights its own front)."""
    if ctx.face != 'front':
        return None
    i, j, w, h = ctx.i, ctx.j, ctx.w, ctx.h
    if i in (0, w - 1) and j in (0, h - 1):
        return None                                          # rounded corners
    if TAG_TXT[j][i]:
        return ENGRAVE
    if j in (7, 8) and not TAG_TXT[j][i]:
        return GOLD[5]                                       # sheen across the gap between the lines
    if j == 0 or i == 0:
        return GOLD[5]
    if j == h - 1 or i == w - 1:
        return GOLD[3]
    return GOLD[4]


def tag_plate_mat(ctx):
    """Normal-density backing: bevelled rim (lit top / left, shaded bottom / right), rounded corners, a scratched
    back with a darker rim, gold edges."""
    f = ctx.face
    i, j, w, h = ctx.i, ctx.j, ctx.w, ctx.h
    if f in ('front', 'back'):
        if i in (0, w - 1) and j in (0, h - 1):
            return None
        if f == 'back':
            if edge(ctx) == 0:
                return GOLD[2]
            return pick(GOLD, 0.48 + (0.1 if (i - j) % 3 == 0 else 0) - (0.1 if hash3(i, j, 4, 41) > 0.8 else 0))
        if j == 0 or i == 0:
            return GOLD[5]
        if j == h - 1 or i == w - 1:
            return GOLD[2]
        return GOLD[4]
    if f == 'top':
        return GOLD[5]
    if f in ('west', 'east'):
        return GOLD[3] if 0 < ctx.j < ctx.h - 1 else None
    return GOLD[2]


def tag_ring_mat(ctx):
    """Split ring: a gold square loop (the centre texel of the front / back is the hole)."""
    f = ctx.face
    if f in ('front', 'back') and ctx.i == 1 and ctx.j == 1:
        return None
    if f in ('front', 'back'):
        return GOLD[5] if (ctx.i + ctx.j) % 2 == 0 else GOLD[3]
    return GOLD[3]


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
        if ctx.j == 0 and abs(x) < 1.3:
            return pick(LIGHT, 0.74)                    # the stop between the eyes, above the bridge
        c = mix(pick(COAT, v), pick(LIGHT, v + 0.08), clamp(1.05 - abs(x) * 0.17))
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


def _muzzle_top(ctx, x, z):
    v = 0.66 + 0.16 + fur_noise(ctx, 0.05)              # lit like a top face whatever face it is painted on
    return mix(pick(COAT, v), pick(LIGHT, v + 0.04), 0.42 + clamp((-z - 17) * 0.08) + (0.2 if abs(x) < 1 else 0))


def muzzle_mat(ctx):
    x, y, z = A(ctx)
    f = ctx.face
    if tag(ctx) == 'bridge':
        # the rise of the muzzle into the stop: the SAME tone as the muzzle top on every face, no edge line, so it
        # melts into the muzzle instead of reading as a brick glued on top
        return _muzzle_top(ctx, x, z)
    if f == 'top':
        return _muzzle_top(ctx, x, z)
    if f in ('west', 'east'):
        c = pick(LIGHT, coat_v(ctx, 0.62))
        u = front_u(ctx)
        if (u, ctx.j) in ((2, 1), (4, 1), (3, 0)):
            c = pick(LIGHT, 0.32)                       # whisker dots
        return c
    return pick(LIGHT, coat_v(ctx, 0.58))


# the nose: a 5-wide leather pad (same width as the muzzle) under a 3-wide rounded bulb.  Charcoal, not pure black,
# so the two comma nostrils (curling out and down) read; the 2-texel wet shine sits on the bulb.
NOSE_ART = ["kNsNk",
            "NkskN"]
NOSE_COLS = {'k': NOSE[4], 's': NOSE[5], 'N': NOSE[0]}


def nose_mat(ctx):
    f = ctx.face
    if tag(ctx) == 'bulb':
        if f == 'front':
            return [NOSE[7], NOSE[6], NOSE[4]][min(2, ctx.i)]
        if f == 'top':
            return [NOSE[6], NOSE[7], NOSE[5]][min(2, ctx.i)]
        return NOSE[4]
    if f == 'front':
        return art(NOSE_ART, NOSE_COLS, ctx, NOSE[3])
    if f == 'top':
        return NOSE[5] if ctx.j == ctx.h - 1 else NOSE[4]
    if f == 'bottom':
        return NOSE[1]                                  # dark underside
    if f in ('west', 'east'):
        return NOSE[4] if ctx.j == 0 else NOSE[2]
    return NOSE[2]


# the mouth on the lip front: a 1-texel philtrum under the nose that splits into two diagonal strokes (an inverted
# Y), the dog's mouth -- not a vertical bar between two blocks
LIPS_FRONT = ["..K..",
              ".K.K."]


def lips_mat(ctx):
    f = ctx.face
    if f == 'front':
        c = art(LIPS_FRONT, {'K': COAT[3]}, ctx)
        return c or pick(LIGHT, coat_v(ctx, 0.66))
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
    "rWWK2r",
    "rVKKwr",
    "r3443r",
    "ccppcc",
]
EYE_SIDE = ["LL", "1r", "Wr", "3r", "4r", "cc"]     # outer side face, column 0 = front edge


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


EYE_GLOW = [(1, 2, GLOW), (2, 2, GLOW), (4, 3, GLOW2)]   # a 2-px main glint + the small one: warm, never a mob glow


# toggle 'wrong_face' (bipedal_180 only): caps over the eyes -- the lids pulled back so the eyeball shows white all
# round, milk-white like the demon's (ent_choripan_demonio), a 1-texel red pinpoint pupil turned slightly inward and
# NO glint.  The pinpoint is the only emissive texel: two tiny red dots in the 3:33 blackout.
WRONG_EYE = [
    "cLLLLc",
    "LHHHHL",
    "rHaaHr",
    "rabbar",
    "rbbbbr",
    "cwwwwc",
]
MILK = pal('#56606e', '#7d8894', '#a3adb6', '#c3cbd0', '#dce1e2', '#eef0ee', '#ffffff')
PIN = hx('#ff2a14')
PIN_D = hx('#9a0e10')
BLOODSHOT = hx('#c4706c')


def _wrong_pupil(side):
    return (3, 2) if side == 'r' else (2, 2)          # looking slightly inward (toward the nose)


def wrong_eye_mat(ctx):
    f = ctx.face
    side = getattr(ctx.cube, 'side', 'r')
    if f == 'front':
        i, j = ctx.i, ctx.j
        if (i, j) == _wrong_pupil(side):
            return PIN
        pi, pj = _wrong_pupil(side)
        if (i, j) == (pi, pj + 1):
            return PIN_D
        ch = WRONG_EYE[j][i]
        c = {'c': pick(COAT, 0.36), 'L': EYE_LID, 'H': MILK[6], 'a': MILK[5], 'b': MILK[4], 'r': EYE_RING[2],
             'w': WET_D}[ch]
        if ch in 'ab' and abs(i - pi) + abs(j - pj) == 1:
            c = mix(c, BLOODSHOT, 0.35)                 # pink ring round the pinpoint
        if ch in 'ab' and ((side == 'r' and (i, j) in ((1, 3), (1, 4))) or (side == 'l' and (i, j) in ((4, 3), (4, 4)))):
            c = mix(c, BLOODSHOT, 0.45)                 # bloodshot thread from the outer corner
        return c
    if outward(ctx):
        return [EYE_LID, MILK[4], MILK[4], MILK[3], MILK[3], WET_D][min(ctx.j, 5)]
    if f == 'top':
        return EYE_LID
    return pick(COAT, 0.4)


def wrong_eye_glow(side):
    pi, pj = _wrong_pupil(side)
    return at([(pi, pj, hx('#ff3a1e'))])


# toggle 'wrong_face': the GRIN.  A zero-thickness plane on the front of the jowls: a crescent of small clenched
# teeth between two dark lip lines that runs from the corners of the real mouth UP into the cheeks, far wider than
# any dog's mouth -- the 'deeply wrong' read from the player's side.  The centre is behind the muzzle (unpainted).
GRIN = [
    "Kt........tK",
    "dTK......KTd",
    ".dtK....KtD.",
    "..dTK..KTd..",
]


def grin_mat(ctx):
    if ctx.face != 'front':
        return None
    return art(GRIN, {'K': MOUTH[1], 'd': MOUTH[2], 'D': MOUTH[2], 'T': TEETH[3], 't': TEETH[1]}, ctx)


def brow_mat(ctx):
    return pick(LIGHT, 0.7)


# closed lids (toggle 'eyelids'): fur caps over the eye cubes; a curved dark lash line, lower lid in cream.
LID_ART = [
    "cLLLLc",
    "LllllL",
    "llllll",
    "KllllK",
    "kKKKKk",
    "cwwwwc",
]
LID_SIDE = ["L", "l", "l", "K", "l", "w"]           # outer side face (1 wide), top to bottom


def _lid_cols(ctx):
    return {'c': pick(COAT, 0.36), 'L': pick(COAT, 0.52), 'l': pick(COAT, 0.62 + (0.03 if ctx.j == 1 else 0)),
            'K': EYE_LID, 'k': pick(COAT, 0.3), 'w': pick(LIGHT, 0.62)}


def lid_mat(ctx):
    f = ctx.face
    if f == 'front':
        return art(LID_ART, _lid_cols(ctx), ctx, pick(COAT, 0.6))
    if outward(ctx):
        return _lid_cols(ctx)[LID_SIDE[min(ctx.j, 5)]]
    if f == 'top':
        return pick(COAT, 0.58)
    if f == 'bottom':
        return pick(LIGHT, 0.6)
    return pick(COAT, 0.45)


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
    if t == 'leg' and ctx.h == 6:
        # the elbow tuft: a little feathering of longer hair at the back of the foreleg, under the chest
        if f == 'back' and (ctx.i, ctx.j) in ((1, 0), (0, 1), (2, 1), (1, 2)):
            v += 0.1 if ctx.j != 1 else -0.06
        if outward(ctx) and (front_u(ctx), ctx.j) in ((2, 0), (2, 1), (1, 1)):
            v += 0.08
        if f == 'front' and ctx.j >= 4:
            return mix(pick(COAT, v), pick(LIGHT, v), 0.3)   # paler 'socks' toward the paw
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


# ------------------------------------------------------------------ the Nona's scarf (toggle 'scarf', look 'bufanda')
def garter_v(ctx, row):
    """Garter stitch: a raised lit ridge every other row, the purl row between in shadow."""
    return 0.58 + face_light(ctx) * 0.9 + (0.11 if row % 2 == 0 else -0.09)


ROLL_SHADE = [0.05, 0.1, 0.06, 0.0, -0.07, -0.15]     # the roll is round: lit on top, tucked into shadow below


def scarf_mat(ctx):
    """Chunky red garter-stitch scarf in the same wool as the sweater.  The wrap is a fat ROLL on the shoulders,
    wider than the jowls (it bulges past the cheeks in the front view): garter ridges running across the scarf (so
    vertical on the roll), round shading, a diagonal crease where the outer turn crosses the inner one; the knot:
    ridges + a pinched waist; the tails: ridges across, two cream bands and a cut-out fringe at the end."""
    f = ctx.face
    t = tag(ctx)
    h = ctx.h
    if t == 'wrap':
        if f == 'bottom':
            return pick(SWEATER, 0.3 + (0.05 if ctx.i % 2 else 0))
        if f in ('front', 'back'):
            v = 0.58 + ROLL_SHADE[min(ctx.j * 6 // max(1, h), 5)] + (0.07 if ctx.i % 2 == 0 else -0.06)
            if f == 'front' and ctx.i - ctx.j in (3, 4) and ctx.i < ctx.w // 2:
                v -= 0.16 if ctx.i - ctx.j == 3 else -0.05     # the outer turn crossing over: crease + lit edge
            if f == 'front' and ctx.i + ctx.j in (ctx.w - 3,) and ctx.i > ctx.w // 2:
                v -= 0.12
            if ctx.i in (0, ctx.w - 1):
                v -= 0.06
            return pick(SWEATER, v)
        if f in ('west', 'east'):
            # the ends of the roll: the scarf wrapping round, ridges in rings
            v = 0.56 + ROLL_SHADE[min(ctx.j * 6 // max(1, h), 5)] + (0.07 if (ctx.i + ctx.j) % 2 == 0 else -0.05)
            if edge(ctx) == 0:
                v -= 0.05
            return pick(SWEATER, v)
        # top: ridges across, the lit crown of the roll
        v = 0.7 + (0.07 if ctx.i % 2 == 0 else -0.05) - (0.06 if ctx.j in (0, ctx.h - 1) else 0)
        return pick(SWEATER, v)
    if t == 'knot':
        v = garter_v(ctx, ctx.j) + 0.03
        if ctx.i == ctx.w // 2 and f in ('front', 'back', 'top', 'bottom'):
            v -= 0.16                                       # the pinch of the knot
        if f == 'front' and ctx.j in (1, 2) and ctx.i in (1, ctx.w - 2):
            v += 0.06                                       # the two lobes catch the light
        if edge(ctx) == 0:
            v -= 0.07
        return pick(SWEATER, v)
    # tails: soft ridges across, two cream bands, then a two-row red fringe (cut-out tassels)
    j = ctx.j
    fringe = h - 2
    sx, _, sz = ctx.cube.size
    broad = f in ('front', 'back') if sx >= sz else f in ('west', 'east')
    if f == 'top':
        return pick(SWEATER, 0.6)
    if f == 'bottom':
        return None
    if j >= fringe:
        if broad and (ctx.i + j) % 2 == 0:
            return pick(SWEATER, 0.56 if j == fringe else 0.44)
        return None
    if j in (fringe - 1, fringe - 3):
        v = 0.56 + face_light(ctx) * 0.6 + (0.1 if ctx.i % 2 == 0 else 0) - (0.08 if f in ('west', 'east') else 0)
        return pick(YARN, v)
    v = 0.56 + face_light(ctx) * 0.9 + (0.06 if j % 2 == 0 else -0.05) - (0.06 if f in ('west', 'east') else 0)
    if broad and ctx.i in (0, ctx.w - 1):
        v -= 0.05
    return pick(SWEATER, v)


# ------------------------------------------------------------------ looks (VARIANT_MATS) + toggles
def make_mat(look):
    """Every cube keeps its painter in cube.fn (no per-cube / per-bone mat), so one look-aware material paints the
    whole sheet.  'bufanda': the sweater (cube.knit) is gone -- those texels are transparent.  'muerto': the same
    painters, then the dead-dog pass (muerto_px) on top."""
    def mat(ctx):
        c = ctx.cube
        if look == 'bufanda' and getattr(c, 'knit', False):
            return None
        col = c.fn(ctx)
        if look == 'muerto' and col is not None:
            return muerto_px(ctx, col)
        return col
    mat.look = look
    return mat


# ------------------------------------------------------------------ look 'muerto' (B3: the dog that watches the house)
# What stands on two legs at the back of the patio is not the dog any more: the eyes are fully black and wet (a single
# cold glint), the gums are raw and bloody, blood has dried down the chin, the throat and the sweater, and the coat is
# matted into wet dark clumps with mud on the paws.  Same geometry and poses; only the texture changes.
DEAD_BLACK = pal('#020102', '#070407', '#0e080c', '#1a1016')
DEAD_GLINT = hx('#b9b4bc')
GORE = pal('#140103', '#2a0306', '#46070b', '#650d12', '#86171b', '#a52824')
MUD = pal('#1a120c', '#2b1e14', '#3d2b1c')
FUR_PARTS = ('core', 'tall', 'keel', 'prow', 'rump', 'leg', 'paw', 'thigh', 'base', 'tip', 'neck', 'skull', 'dome',
             'cheek', 'muzzle', 'bridge', 'ear', 'lobe', 'fold', 'brow', 'lid', 'twist')
MOUTH_PARTS = ('lips', 'jaw', 'mouth', 'teeth', 'canine', 'tongue')


def _lum(c):
    return (c[0] * 0.3 + c[1] * 0.59 + c[2] * 0.11) / 255.0


def _dead_tone(c, k=0.72, grey=0.35):
    """Darker, colder, greyer: the colour of a coat soaked and dried many times."""
    g = int(_lum(c) * 255)
    r = int((c[0] * (1 - grey) + g * grey) * k)
    gg = int((c[1] * (1 - grey) + g * grey) * k * 0.97)
    b = int((c[2] * (1 - grey) + g * grey) * k * 0.95)
    return (max(0, min(255, r)), max(0, min(255, gg)), max(0, min(255, b)), c[3])


def _blood_at(x, y, z, seed, thresh):
    """Organic stain mask in model space (blotches that run downward: +y is down)."""
    v = fbm(x * 0.33, y * 0.16, z * 0.33, 3, seed)
    return v > thresh


def muerto_px(ctx, col):
    c = ctx.cube
    name = getattr(c, 'name', '') or ''
    f = ctx.face
    x, y, z = ctx.pos
    # the eyes: fully black and wet; one cold glint, a raw red rim on the lower lid
    if name == 'eye':
        if f == 'front':
            if (ctx.i, ctx.j) in ((1, 1), (2, 1)):
                return DEAD_GLINT if ctx.i == 1 else mix(DEAD_GLINT, DEAD_BLACK[2], 0.55)
            if ctx.j == ctx.h - 1:
                return GORE[2] if ctx.i % 2 else GORE[1]
            if ctx.j == 0:
                return DEAD_BLACK[3]
            return DEAD_BLACK[0] if (ctx.i + ctx.j) % 3 else DEAD_BLACK[1]
        if outward(ctx):
            return DEAD_BLACK[1] if ctx.j < ctx.h - 1 else GORE[1]
        return _dead_tone(col)
    if name in ('wrong_eye',):
        return col
    # the mouth: gums raw, teeth stained brown at the roots, a grey dead tongue, blood pooled in it
    if name in MOUTH_PARTS:
        lum = _lum(col)
        if name == 'tongue':
            return mix(_dead_tone(col, 0.7, 0.6), hx('#4a3a46'), 0.35)
        if name in ('teeth', 'canine'):
            if col[3] == 0:
                return col
            if lum > 0.6:                                   # enamel: yellowed, a red line at the gum
                stain = mix(col, hx('#a08a5c'), 0.4)
                return mix(stain, GORE[3], 0.5) if (ctx.j == 0 or hash3(x * 3, y * 3, z * 3, 5) > 0.7) else stain
            return GORE[3]                                  # the gum rows between the teeth
        pinkish = col[0] > 110 and col[2] >= col[1] - 6     # PINK gums / palate (tan fur has blue well under green)
        if pinkish or name == 'mouth':
            return pick(GORE, 0.25 + 0.6 * lum)            # -> raw red
        base = _dead_tone(col, 0.78, 0.25)
        # dried blood running from the lips down the chin: a few drips of different lengths
        if f in ('front', 'west', 'east'):
            k = hash3(ctx.i * 3 + (7 if f == 'front' else 0), 0, 1, 31 + len(name))
            if k > 0.62 and ctx.j <= int(hash3(ctx.i, 2, 3, 17) * ctx.h * 1.2):
                return GORE[1] if ctx.j > 0 else GORE[2]
        return base
    if getattr(c, 'knit', False) or name in ('bib', 'collar', 'wrap', 'knot'):
        # the sweater: soaked dark, blood dried down the front
        base = _dead_tone(col, 0.62, 0.3)
        if y > 12 and z < -2 and _blood_at(x, y, z, 7, 0.52):
            return mix(base, GORE[2], 0.75)
        if _blood_at(x, y, z, 19, 0.66):
            return mix(base, GORE[1], 0.6)
        return base
    if name in FUR_PARTS:
        # matted coat: dark wet clumps along the hair direction, a few lighter dried tips, mud on the paws
        clump = vnoise(x * 0.9, y * 0.45, z * 0.9, 41)
        strand = hash3(math.floor(x * 1.3), math.floor(y * 0.5), math.floor(z * 1.3), 43)
        base = _dead_tone(col, 0.44 + 0.3 * clump + 0.12 * strand, 0.3)
        if hash3(x * 2, y * 2, z * 2, 77) > 0.93:
            base = mix(base, hx('#8a7a6c'), 0.25)              # dried, stiff tips
        if name in ('paw',) or (name == 'leg' and y > 20.5):
            return mix(base, MUD[1], 0.55)
        # blood: down the chin and the throat, crusted round the muzzle
        if name in ('muzzle', 'bridge', 'cheek') and y > 13.5 and _blood_at(x, y, z, 3, 0.58):
            return mix(base, GORE[1], 0.8)
        if name in ('neck', 'prow', 'keel') and z < -5 and y > 13 and _blood_at(x, y, z, 11, 0.5):
            return mix(base, GORE[2], 0.7)
        # black tears from the eyes
        if name in ('skull', 'cheek') and f == 'front':
            for ex in (-4.8, 3.8):
                if abs(x - ex) < 0.6 and 12.0 < y < 16.5 and hash3(ex * 7, math.floor(y), 0, 9) > 0.2:
                    return DEAD_BLACK[2]
        return base
    return _dead_tone(col, 0.8, 0.3)


DEFAULT_MAT = make_mat('normal')
VARIANT_MATS = {'normal': DEFAULT_MAT, 'bufanda': make_mat('bufanda'), 'muerto': make_mat('muerto')}
FOCUS = 'head'

TOGGLE_DEFAULT = {'scarf': False, 'eyelids': False, 'wrong_face': False, 'neck_twist': False}
VARIANT_TOGGLES = {'normal': {}, 'bufanda': {'scarf': True}}
POSE_TOGGLES = {'sleep': {'eyelids': True}, 'sneeze': {'eyelids': True},
                'bipedal_180': {'wrong_face': True, 'neck_twist': True}}


def visible_set(variant=None, pose=None):
    vis = dict(TOGGLE_DEFAULT)
    vis.update(VARIANT_TOGGLES.get(variant or 'normal', {}))
    vis.update(POSE_TOGGLES.get(pose, {}))
    return {k for k, v in vis.items() if v}


def _argv(flag):
    a = sys.argv
    return a[a.index(flag) + 1] if flag in a and a.index(flag) + 1 < len(a) else None


class ChoriModel(Model):
    """Exports every bone to Java; the preview / gallery JSON hides the toggle bones the current look / pose hides.

    UV packing by FACE MASKS instead of bounding blocks: a box-UV block leaves two d x d corners that no face samples
    (the body core alone wastes 2 x 22 x 22), so smaller cubes nest into them.  The engraved tag card is a zero-thickness
    box, so only its front and back rects are real (its four side faces have zero area) and only those must be free.
    Texels are never shared: every sampled face rect owns its texels, with a 1-texel extruded gutter round it."""
    visible = None

    @staticmethod
    def _rects(c):
        w, h, d = c.size
        thin = getattr(c, 'name', '') == 'text'
        rects = {'top': (d, 0, w, d), 'bottom': (d + w, 0, w, d), 'west': (0, d, d, h),
                 'front': (d, d, w, h), 'east': (d + w, d, d, h), 'back': (2 * d + w, d, w, h)}
        keep = ('front', 'back') if thin else tuple(rects)
        return [rects[k] for k in keep if rects[k][2] > 0 and rects[k][3] > 0]

    def pack(self, pad=1):
        """Face-mask packing with a `pad`-texel gutter round every face (filled by paint(), see below)."""
        W, H = self.tex_w, self.tex_h
        used = np.zeros((H, W), bool)
        items = [c for b in self.bones() for c in b.cubes]
        items.sort(key=lambda c: (-c.uv_size()[0] * c.uv_size()[1], -c.uv_size()[1]))
        for c in items:
            bw, bh = c.uv_size()
            S = np.zeros((H + 1, W + 1), np.int32)
            S[1:, 1:] = used.cumsum(0).cumsum(1)
            V = np.arange(pad, H - bh - pad + 1)[:, None]
            U = np.arange(pad, W - bw - pad + 1)[None, :]
            ok = np.ones((V.shape[0], U.shape[1]), bool)
            for dx, dy, fw, fh in self._rects(c):
                y0, x0 = V + dy - pad, U + dx - pad
                fw2, fh2 = fw + 2 * pad, fh + 2 * pad
                ok &= (S[y0 + fh2, x0 + fw2] - S[y0, x0 + fw2] - S[y0 + fh2, x0] + S[y0, x0]) == 0
            hit = np.argwhere(ok)
            if not len(hit):
                raise RuntimeError(f'{self.name}: no room for cube {c.size} (texture {W}x{H})')
            v, u = (int(x) + pad for x in hit[0])
            c.uv = (u, v)
            for dx, dy, fw, fh in self._rects(c):
                used[v + dy:v + dy + fh, u + dx:u + dx + fw] = True
        return self

    def paint(self, default_mat, seed=1, layer='base'):
        """Paint, then extrude every face's border texels one texel into the free gutter round it, so a face edge
        seen at a grazing angle never samples a neighbouring cube's colours."""
        img = super().paint(default_mat, seed=seed, layer=layer)
        if layer != 'base':
            return img
        W, H = img.size
        own = np.zeros((H, W), bool)
        rects = []
        for b in self.bones():
            for c in b.cubes:
                for dx, dy, fw, fh in self._rects(c):
                    u0, v0 = c.uv[0] + dx, c.uv[1] + dy
                    own[v0:v0 + fh, u0:u0 + fw] = True
                    rects.append((u0, v0, fw, fh))
        px = img.load()
        for u0, v0, fw, fh in rects:
            for j in range(-1, fh + 1):
                for i in range(-1, fw + 1):
                    if 0 <= i < fw and 0 <= j < fh:
                        continue
                    x, y = u0 + i, v0 + j
                    if not (0 <= x < W and 0 <= y < H) or own[y, x] or px[x, y][3] > 0:
                        continue
                    src = px[u0 + min(max(i, 0), fw - 1), v0 + min(max(j, 0), fh - 1)]
                    if src[3] > 0:
                        px[x, y] = src
        return img

    def to_json(self):
        d = super().to_json()
        d['toggles'] = {'default': dict(TOGGLE_DEFAULT),
                        'variants': {v: dict(t) for v, t in VARIANT_TOGGLES.items()},
                        'poses': {p: dict(t) for p, t in POSE_TOGGLES.items()}}
        if self.visible is None:
            return d
        hide = set()
        for b in self.bones():
            if b.name in TOGGLE_DEFAULT and b.name not in self.visible:
                for sub in b.walk():
                    hide.add(sub.name)
        for bd in d['bones']:
            if bd['name'] in hide and bd['cubes']:
                bd['hidden_cubes'] = bd['cubes']
                bd['cubes'] = []
        return d


# ------------------------------------------------------------------ geometry constants
DZ = -0.5          # authoring z -> model z (recentres the long dog on the entity origin)
HY = 1.0           # the whole head subtree sits this much lower than authored...
HZ = -2.0          # ...and this much further forward, so a real neck (with the collar on it) shows
HEAD_BONES = {'head', 'lips', 'jaw', 'tongue', 'right_brow', 'left_brow', 'right_ear', 'left_ear', 'eyelids',
              'wrong_face'}
COLLAR_A = (0.0, 13.5, -10.0)      # collar pivot (authoring); the collar is tilted -30 deg to sit across the neck
COLLAR_TILT = -30.0
TAG_A = (0.0, 19.2, -10.8)         # the D-ring, in the collar's unrotated frame (authoring)
SCARF_A = (0.0, 16.0, -9.0)        # scarf pivot (authoring, child of neck): the roll sits on the shoulders
SCARF_TILT = -6.0


def _tag_world():
    """D-ring in model space (before DZ): the tag bone cancels the collar tilt, so tag children are world-aligned."""
    R = rot_matrix(math.radians(COLLAR_TILT), 0, 0)
    rel = np.array(TAG_A) - np.array(COLLAR_A)
    return tuple(float(v) for v in np.array(COLLAR_A) + R @ rel)


TAG_W = _tag_world()


def build(variant=None, pose=None):
    r = Rig()
    fns = {}

    def box(bone, frm, size, mat=None, inflate=0.0, decals=None, name=None, side='', knit=False):
        dy, dz = (HY, HZ) if bone in HEAD_BONES else (0.0, 0.0)
        c = r.box(bone, (frm[0], frm[1] + dy, frm[2] + DZ + dz), size, inflate=inflate, decals=decals)
        c.a0 = tuple(float(v) for v in frm)            # materials work in authoring coordinates
        c.name = name
        c.side = side
        c.fn = mat or fns[bone]
        c.knit = knit
        return c

    def bone(name, pivot, parent=None, rot=(0, 0, 0), mat=None):
        dy, dz = (HY, HZ) if name in HEAD_BONES else (0.0, 0.0)
        fns[name] = mat
        return r.bone(name, (pivot[0], pivot[1] + dy, pivot[2] + DZ + dz), parent=parent, rot=rot)

    def tag_box(wmin, size, inflate, mat, name):
        """Tag child cube placed by its RENDERED min corner in model space (before DZ); handles the deformation."""
        frm = tuple(wmin[i] + inflate - TAG_W[i] + TAG_A[i] for i in range(3))
        return box('tag', frm, size, mat=mat, inflate=inflate, name=name)

    # ---------------- body (root, pivot at the hips so sit / beg rotate around the rump)
    bone('body', (0, 16, 11), mat=body_mat)
    box('body', (-5, 12, -6), (10, 7, 22), name='core')
    box('body', (-4, 11, -4.5), (8, 9, 19), name='tall')
    box('body', (-2, 19, -6.6), (4, 2, 8), name='keel')
    box('body', (-3, 13, -7.2), (6, 6, 3), name='prow')
    box('body', (-4, 12.5, 15.5), (8, 6, 2), name='rump')
    # sweater: two shells (open belly), raised spine cable, ribbed cuff rings at the neck and the tail end
    box('body', (-5, 12, -4.5), (10, 7, 15), mat=sweater_mat, inflate=0.55, name='shell_w', knit=True)
    box('body', (-4, 11, -4.5), (8, 9, 15), mat=sweater_mat, inflate=0.55, name='shell_t', knit=True)
    box('body', (-2, 9.8, -3.5), (4, 1, 13), mat=cable_mat, name='cable', knit=True)
    box('body', (-5, 12, -5.2), (10, 7, 1), mat=sweater_mat, inflate=1.0, name='cuff', knit=True)
    box('body', (-4, 11, -5.2), (8, 9, 1), mat=sweater_mat, inflate=1.0, name='cuff', knit=True)
    box('body', (-5, 12, 10.2), (10, 7, 1), mat=sweater_mat, inflate=0.8, name='cuff', knit=True)
    box('body', (-4, 11, 10.2), (8, 9, 1), mat=sweater_mat, inflate=0.8, name='cuff', knit=True)
    # the turtleneck chest panel: brings the red (and the Nona) to the front view, between the forelegs and
    # under the chin
    box('body', (-5, 12, -8.4), (10, 7, 3), mat=sweater_mat, inflate=0.3, name='bib', knit=True)

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
        bs = f'{sd}_back_shin'
        bone(bs, (cx + 0.3 * sx, 19.5, 13), parent=bl, mat=leg_mat)
        box(bs, (cx - 1.5 + 0.3 * sx, 19.5, 11.5), (3, 3, 3), name='leg', side=sd[0])
        bp = f'{sd}_back_paw'
        bone(bp, (cx + 0.3 * sx, 22.2, 13), parent=bs, mat=leg_mat)
        box(bp, (cx - 1.5 + 0.3 * sx, 22, 10.5), (3, 2, 4), name='paw', side=sd[0])

    # ---------------- tail (raised, happy curve)
    bone('tail', (0, 12.8, 15.5), parent='body', rot=(32, 0, 0), mat=tail_mat)
    box('tail', (-1.5, 11.3, 15), (3, 3, 6), name='base')
    bone('tail_tip', (0, 12.8, 20.5), parent='tail', rot=(18, 0, 0), mat=tail_mat)
    box('tail_tip', (-1, 11.8, 20), (2, 2, 5), name='tip')

    # ---------------- neck, collar, name tag
    # The collar is a slab on its own bone, tilted 30 degrees so it sits perpendicular to the forward-leaning neck: it
    # crosses the back of the neck just behind the skull and wraps under the throat, where the tag hangs below the
    # chin.  (Children of a rotated bone are authored in that bone's unrotated frame.)
    bone('neck', (0, 13, -4.5), parent='body', mat=neck_mat)
    box('neck', (-3, 9, -13), (6, 9, 8), name='neck')
    bone('collar', COLLAR_A, parent='neck', rot=(COLLAR_TILT, 0, 0), mat=collar_mat)
    box('collar', (-3.5, 8, -11), (7, 11, 2), inflate=0.2, name='collar')
    bone('tag', TAG_A, parent='collar', rot=(-COLLAR_TILT, 0, 0), mat=tag_plate_mat)
    tx, ty, tz = TAG_W
    # split ring through the D-ring, then the backing plate and the engraved high-density card 0.05 in front of it
    tag_box((-0.75, ty - 0.1, tz - 0.25), (3, 3, 2), -0.75, tag_ring_mat, 'ring')
    tag_box((-3.9, ty + 1.15, tz - 0.4), (8, 5, 1), -0.1, tag_plate_mat, 'plate')
    tag_box((-3.5, ty + 1.55, tz - 0.45), (TXT_W, TXT_H, int(2 * TXT_K)), -TXT_K, tag_text_mat, 'text')

    # ---------------- the wrung neck (TOGGLE: hidden by default, shown in 'bipedal_180')
    bone('neck_twist', (0, 13, -4.5), parent='neck', mat=twist_mat)
    box('neck_twist', (-3, 9, -13), (6, 9, 8), inflate=0.32, name='twist')

    # ---------------- the Nona's scarf (TOGGLE: hidden by default, shown in the 'bufanda' look)
    # a fat roll on the shoulders (16 wide with the inflate: wider than the jowls, so it shows past the cheeks
    # in the front view), the knot on his left under the jaw, behind the tag, one tail hanging over the knot down
    # to the floor in front of the left foreleg, the other down his left side
    bone('scarf', SCARF_A, parent='neck', rot=(SCARF_TILT, 0, 0), mat=scarf_mat)
    box('scarf', (-7.5, 13, -12), (15, 6, 6), inflate=0.5, name='wrap')
    box('scarf', (2.8, 15.5, -12.5), (5, 5, 4), inflate=0.3, name='knot')
    bone('scarf_tail_front', (6.0, 16.5, -12.9), parent='scarf', rot=(-SCARF_TILT, 0, -3), mat=scarf_mat)
    box('scarf_tail_front', (3.5, 16.5, -13.4), (5, 8, 1), name='tail')
    bone('scarf_tail_back', (8.3, 16.5, -10.5), parent='scarf', rot=(-SCARF_TILT, 0, -8), mat=scarf_mat)
    box('scarf_tail_back', (7.8, 16.5, -13.0), (1, 7, 5), name='tail')

    # ---------------- head
    bone('head', (0, 11, -8.5), parent='neck', mat=skull_mat)
    box('head', (-6.5, 4, -16), (13, 9, 9), name='skull')
    box('head', (-5.5, 3, -15), (11, 1, 7), mat=dome_mat, name='dome')
    box('head', (-6, 11, -16.5), (12, 4, 6), mat=cheek_mat, name='cheek')
    box('head', (-2.5, 12.5, -23), (5, 2, 7), mat=muzzle_mat, name='muzzle')
    box('head', (-1.5, 11.5, -20), (3, 1, 4), mat=muzzle_mat, name='bridge')
    box('head', (-2.5, 12.3, -23.6), (5, 2, 1), mat=nose_mat, name='nose')
    box('head', (-1.5, 11.8, -23.35), (3, 1, 1), mat=nose_mat, name='bulb')
    for sd, x0 in (('r', -7.3), ('l', 1.3)):
        box('head', (x0, 5, -16.3), (6, 6, 2), mat=eye_mat, name='eye', side=sd,
            decals={'eyes:front': at(EYE_GLOW)})
    box('head', (-2.5, 14.5, -22.75), (5, 2, 0), mat=teeth_mat(["TgggT", "TtgtT"]), name='teeth')
    box('head', (-2.5, 15.5, -22.65), (1, 1, 1), mat=canine_mat, name='canine')
    box('head', (1.5, 15.5, -22.65), (1, 1, 1), mat=canine_mat, name='canine')
    box('head', (-2, 14.7, -22.4), (4, 2, 6), mat=mouth_mat, inflate=-0.1, name='mouth')

    # closed lids over both eyes (TOGGLE: hidden by default, shown in 'sleep' / 'sneeze')
    bone('eyelids', (0, 8, -16.3), parent='head', mat=lid_mat)
    for sd, x0 in (('r', -7.3), ('l', 1.3)):
        box('eyelids', (x0, 5, -16.3), (6, 6, 1), inflate=0.08, name='lid', side=sd)

    # the WRONG face (TOGGLE: hidden by default, shown in 'bipedal_180'): milk eyes with red pinpoints over the
    # eyes, and the too-wide grin on the jowls
    bone('wrong_face', (0, 8, -16.3), parent='head', mat=wrong_eye_mat)
    for sd, x0 in (('r', -7.3), ('l', 1.3)):
        box('wrong_face', (x0, 5, -16.3), (6, 6, 1), inflate=0.14, name='wrong_eye', side=sd,
            decals={'eyes:front': wrong_eye_glow(sd)})
    box('wrong_face', (-6, 11, -16.62), (12, 4, 0), mat=grin_mat, name='grin')

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

    m = ChoriModel('choripan', 128, 128, r.roots)
    m.scale = 0.5
    if pose is None and os.path.basename(sys.argv[0]) == 'preview.py':
        pose = _argv('--pose')
    if variant is None and os.path.basename(sys.argv[0]) == 'preview.py':
        variant = _argv('--variant')
    m.visible = visible_set(variant, pose)
    return m


# ------------------------------------------------------------------ FK helpers (pose maths, used to build POSES)
def _euler_zyx(R):
    """MC Euler angles (xRot, yRot, zRot) of R = Rz * Ry * Rx."""
    y = math.asin(max(-1.0, min(1.0, -R[2, 0])))
    x = math.atan2(R[2, 1], R[2, 2])
    z = math.atan2(R[1, 0], R[0, 0])
    return x, y, z


def fk(model, pose):
    """World 4x4 per bone for a pose table (bone -> (xRot, yRot, zRot, dx, dy, dz), ADDED to the rest pose), the way
    HauntModel / the preview apply it: Euler angles summed, offsets added to the pivot."""
    out = {}

    def walk(b, M):
        p = (pose or {}).get(b.name, (0, 0, 0, 0, 0, 0))
        p = tuple(p) + (0,) * (6 - len(p))
        T = np.eye(4)
        T[:3, 3] = (b.pivot[0] + p[3], b.pivot[1] + p[4], b.pivot[2] + p[5])
        R = np.eye(4)
        R[:3, :3] = rot_matrix(math.radians(b.rot[0]) + p[0], math.radians(b.rot[1]) + p[1],
                               math.radians(b.rot[2]) + p[2])
        W = M @ T @ R
        out[b.name] = W
        for c in b.children:
            walk(c, W)
    for root in model.roots:
        walk(root, np.eye(4))
    return out


def plumb(model, pose, name, swing=(0.0, 0.0)):
    """Pose entry that makes bone `name` hang straight down (gravity) while facing its parent's heading, plus a swing
    (world xRot, zRot; -xRot = lower end toward its front).  Returns (xRot, yRot, zRot) to ADD to the rest pose."""
    W = fk(model, pose)
    b = next(x for x in model.bones() if x.name == name)
    P = W[b.parent.name][:3, :3]
    fwd = P @ np.array([0.0, 0.0, -1.0])
    if math.hypot(fwd[0], fwd[2]) < 0.2:                    # parent points straight up / down: use its 'down' axis
        fwd = P @ np.array([0.0, 1.0, 0.0])
    yaw = math.atan2(-fwd[0], -fwd[2])                      # heading of -Z rotated by Ry(yaw)
    Wd = rot_matrix(0, yaw, 0) @ rot_matrix(swing[0], 0, swing[1])
    L = P.T @ Wd
    ex, ey, ez = _euler_zyx(L)
    rx, ry, rz = [math.radians(a) for a in b.rot]
    return (ex - rx, ey - ry, ez - rz)


def world_bounds(model, pose, bones=None):
    """Model-space AABB of the posed cubes (for ground / centring checks)."""
    W = fk(model, pose)
    mn = np.array([1e9] * 3)
    mx = -mn
    for b in model.bones():
        if bones and b.name not in bones:
            continue
        M = W[b.name]
        for c in b.cubes:
            x0, y0, z0 = c.origin
            w, h, d = c.size
            g = c.inflate
            for px in (x0 - g, x0 + w + g):
                for py in (y0 - g, y0 + h + g):
                    for pz in (z0 - g, z0 + d + g):
                        q = (M @ np.array([px, py, pz, 1.0]))[:3]
                        mn = np.minimum(mn, q)
                        mx = np.maximum(mx, q)
    return mn, mx


# ------------------------------------------------------------------ poses
PI = math.pi
_POSES = {
    'sit': {'body': (-0.34, 0, 0, 0, 3.06, 0),
            'right_front_leg': (0.34, 0, 0.04, 0, 1.58, 0), 'left_front_leg': (0.34, 0, -0.04, 0, 1.58, 0),
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
            'jaw': (0.16, 0, 0, 0, 0, 0), 'tongue': (0.6, 0, 0, 0, 0.6, -1.7),
            'tail': (1.45, 0.35, 0, 0, 0, 0), 'tail_tip': (-0.25, 0.3, 0, 0, 0, 0)},
    'belly_up': {'body': (0, 0, 3.02, 0, 1.35, 0),
                 'right_front_leg': (-0.5, 0, 0.25, 0, 1.2, 0), 'left_front_leg': (-0.5, 0, -0.25, 0, 1.2, 0),
                 'right_front_paw': (1.0, 0, 0, 0, 0, 0), 'left_front_paw': (1.0, 0, 0, 0, 0, 0),
                 'right_back_leg': (-0.5, 0, 0.7, 0, 1.0, 0), 'left_back_leg': (-0.5, 0, -0.7, 0, 1.0, 0),
                 'right_back_paw': (1.0, 0, 0, 0, 0, 0), 'left_back_paw': (1.0, 0, 0, 0, 0, 0),
                 'neck': (1.13, 0, 0, 0, 0, 0), 'head': (-0.4, 0, 0.15, 0, 0, 0),
                 'right_ear': (0, 0, 1.25, 0, 0, 0), 'left_ear': (0, 0, -1.25, 0, 0, 0),
                 'jaw': (0.14, 0, 0, 0, 0, 0), 'tongue': (-0.15, 0.85, 0, 1.2, 0.2, -1.0),
                 'right_brow': (0, 0, 0.12, 0, -0.3, 0), 'left_brow': (0, 0, -0.12, 0, -0.3, 0),
                 'tail': (-0.9, 0.5, 0, 0, 0, 0), 'tail_tip': (0, 0.4, 0, 0, 0, 0)},
    'tilt': {'head': (0, 0, 0.38, 0, 0, 0), 'right_ear': (0, 0, -2.3, 0, 0, 0),
             'right_brow': (0, 0, -0.2, 0, -0.4, 0), 'left_brow': (0, 0, -0.1, 0, 0, 0)},
    'growl': {'body': (0.07, 0, 0, 0, 0, 0),
              'right_front_leg': (-0.07, 0, 0, 0, -1.1, 0), 'left_front_leg': (-0.07, 0, 0, 0, -1.1, 0),
              'right_back_leg': (-0.07, 0, 0, 0, 0, 0), 'left_back_leg': (-0.07, 0, 0, 0, 0, 0),
              'neck': (0.2, 0, 0, 0, 0, 0), 'head': (-0.3, 0, 0, 0, 0, 0),
              'lips': (-0.1, 0, 0, 0, -1.4, 0), 'jaw': (0.1, 0, 0, 0, 0, 0),
              'right_brow': (0, 0, -0.45, 0, 0.3, 0), 'left_brow': (0, 0, 0.45, 0, 0.3, 0),
              'right_ear': (0.35, 0, -0.15, 0, 0, 0), 'left_ear': (0.35, 0, 0.15, 0, 0, 0),
              'tail': (-0.6, 0, 0, 0, 0, 0)},
    # THE CLIP (casa.buen_chico, 3:33).  The entity keeps facing the player; the BODY turns its back on the camera
    # (yRot pi) and stands up on the hind legs, and the neck spins the head 180 deg round the spine so the face (with
    # the collar and the tag under the chin) stares straight back at the player over the sweater's spine.
    'bipedal_180': {'body': (-1.48, PI, 0, 0, -1.5, -10.6),
                    'right_back_leg': (1.48, 0, 0.05, 0, 0, 0), 'left_back_leg': (1.48, 0, -0.05, 0, 0, 0),
                    'right_front_leg': (1.35, 0, 0.75, 0, 0, 0), 'left_front_leg': (1.35, 0, -0.75, 0, 0, 0),
                    'right_front_paw': (0.5, 0, 0.2, 0, 0, 0), 'left_front_paw': (0.5, 0, -0.2, 0, 0, 0),
                    'neck': (1.4, 0, PI, 0, 0, 0), 'head': (-0.12, 0, 0.3, 0, 0, 0),
                    'jaw': (0.14, 0, 0, 0, 0, 0), 'lips': (-0.05, 0, 0, 0, -0.6, 0),
                    'right_ear': (0, 0, -0.25, 0, 0, 0), 'left_ear': (0, 0, -0.3, 0, 0, 0),
                    'right_brow': (0, 0, -0.3, 0, 0.6, 0), 'left_brow': (0, 0, 0.3, 0, 0.6, 0),
                    'tail': (1.15, 0.4, 0, 0, 0, 0), 'tail_tip': (0.45, 0.3, 0, 0, 0, 0)},
    # B3 'stand' (perro_mira, the dog that watches the house): upright on the hind legs LIKE A PERSON, facing you (not
    # turned away like bipedal_180): the spine vertical, the front legs hanging limp at his sides with the paws
    # dangling, the head brought back level and tilted onto his left shoulder, staring.  No wag, no breathing: Java
    # keeps it perfectly still.  The tail hangs down between the hind legs.
    'stand': {'body': (-1.5, 0, 0, 0, -1.5, -10.8),
              'right_back_leg': (1.5, 0, 0.06, 0, 0, 0), 'left_back_leg': (1.5, 0, -0.06, 0, 0, 0),
              'right_back_paw': (0.0, 0.12, 0, 0, 0, 0), 'left_back_paw': (0.0, -0.12, 0, 0, 0, 0),
              'right_front_leg': (1.32, -0.46, 0, 0, 0, 0), 'left_front_leg': (1.32, 0.46, 0, 0, 0, 0),
              'right_front_paw': (0.65, 0, 0, 0, 0, 0), 'left_front_paw': (0.65, 0, 0, 0, 0, 0),
              'neck': (1.3, 0, 0, 0, 0, 0), 'head': (0.12, 0, 0.3, 0, 0, 0),
              'lips': (-0.03, 0, 0, 0, -0.3, 0),
              'right_ear': (0.15, 0, 0.1, 0, 0, 0), 'left_ear': (0.1, 0, -0.05, 0, 0, 0),
              'right_brow': (0, 0, -0.25, 0, 0.5, 0), 'left_brow': (0, 0, 0.25, 0, 0.5, 0),
              'tail': (1.7, 0.25, 0, 0, 0, 0), 'tail_tip': (0.45, 0.2, 0, 0, 0, 0)},
    'sneeze': {'body': (0.04, 0, 0, 0, 0, 0),
               'right_front_leg': (-0.22, 0, 0.06, 0, -0.3, 0), 'left_front_leg': (-0.22, 0, -0.06, 0, -0.3, 0),
               'neck': (0.22, 0, 0, 0, 0, 0), 'head': (0.12, 0, 0, 0, 0, 0),
               'lips': (-0.12, 0, 0, 0, -0.6, 0), 'jaw': (0.2, 0, 0, 0, 0, 0), 'tongue': (0.15, 0, 0, 0, 0, -0.4),
               'right_brow': (0, 0, -0.3, 0, 0.9, 0), 'left_brow': (0, 0, 0.3, 0, 0.9, 0),
               'right_ear': (-0.75, 0, -0.25, 0, 0, 0), 'left_ear': (-0.75, 0, 0.25, 0, 0, 0),
               'tail': (-0.25, 0, 0, 0, 0, 0)},
    # curled at the Nona's feet: lying on the chest, the front legs stretched out, the hind legs tucked to his left,
    # the chin on the floor beside the right paw, the head turned back toward the hip, the tail curled round the front
    'sleep': {'body': (0.04, 0.0, 0.18, 0, 3.0, 0),
              'right_front_leg': (-1.4, 0.15, 0.05, 0, 1.2, 0), 'left_front_leg': (-1.4, -0.25, -0.1, 0, 1.2, 0),
              'right_front_paw': (1.3, 0, 0, 0, 0, 0), 'left_front_paw': (1.3, 0, 0, 0, 0, 0),
              'right_back_leg': (-1.0, 0.55, 0.15, 0, 1.0, 0), 'left_back_leg': (-1.0, 0.75, -0.2, 0, 1.0, 0),
              'right_back_paw': (0.9, 0, 0, 0, 0, 0), 'left_back_paw': (0.9, 0, 0, 0, 0, 0),
              'neck': (0.42, 0.55, 0.1, 0, 0, 0), 'head': (-0.08, 0.5, -0.12, 0, 0, 0),
              'right_ear': (0.25, 0, 0.5, 0, 0, 0), 'left_ear': (-0.2, 0, -0.35, 0, 0, 0),
              'right_brow': (0, 0, 0.1, 0, 0.5, 0), 'left_brow': (0, 0, -0.1, 0, 0.5, 0),
              'tail': (-0.55, -1.5, 0, 0, 0, 0), 'tail_tip': (0.2, -1.0, 0, 0, 0, 0)},
    'sniff': {'neck': (0.52, 0, 0, 0, 0, 0), 'head': (-0.36, 0, 0, 0, 0, 0),
              'right_ear': (-0.35, 0, -0.1, 0, 0, 0), 'left_ear': (-0.35, 0, 0.1, 0, 0, 0),
              'right_brow': (0, 0, -0.15, 0, -0.3, 0), 'left_brow': (0, 0, 0.15, 0, -0.3, 0),
              'tail': (-0.35, 0.3, 0, 0, 0, 0)},
    'bark': {'body': (-0.08, 0, 0, 0, 0, 0),
             'right_front_leg': (-0.2, 0, 0.08, 0, -0.3, 0), 'left_front_leg': (-0.2, 0, -0.08, 0, -0.3, 0),
             'neck': (-0.25, 0, 0, 0, 0, 0), 'head': (-0.15, 0, 0, 0, 0, 0),
             'jaw': (0.5, 0, 0, 0, 0, 0), 'lips': (-0.06, 0, 0, 0, -0.4, 0), 'tongue': (0.1, 0, 0, 0, 0, 0),
             'right_ear': (0.5, 0, 0.15, 0, 0, 0), 'left_ear': (0.5, 0, -0.15, 0, 0, 0),
             'right_brow': (0, 0, 0.2, 0, -0.6, 0), 'left_brow': (0, 0, -0.2, 0, -0.6, 0),
             'tail': (-0.5, 0, 0, 0, 0, 0)},
}
# the tag and the scarf tails hang plumb in every pose (+ a small swing where the motion would throw them)
TAG_SWING = {'stand': (0.0, 0.0), 'beg': (-0.3, 0), 'bark': (0.2, 0), 'sneeze': (-0.35, 0), 'belly_up': (0, 0.3),
             'bipedal_180': (0.05, 0.08), 'sleep': (0, 0)}


GROUND = 24.0
HANG = ('tag', 'scarf', 'scarf_tail_front', 'scarf_tail_back')     # flexible parts: never used to ground a pose
NO_SNAP = ('belly_up',)                                             # hand-placed (rolling on the back)
HEAD_SET = ('head', 'lips', 'jaw', 'tongue', 'right_brow', 'left_brow', 'right_ear', 'left_ear', 'eyelids')
# poses whose head goes down to the floor: the dog is grounded on its legs / body first, then the head pitch is solved
# so the chin rests ON the floor (clearance 0) or just clears it
HEAD_FLOOR = {'sniff': 0.05, 'sleep': 0.05, 'sneeze': 0.8}


def _hang(m, t, name, sw):
    """Plumb + swing, and if the hanging part would sink into the floor, swing it (the smaller way) until it rests on it."""
    best = None
    for k in range(0, 31):
        for sgn in ((1,) if k == 0 else (-1, 1)):
            cand = (sw[0] + sgn * k * 0.06, sw[1])
            v = plumb(m, t, name, cand)
            t2 = dict(t)
            t2[name] = v
            if world_bounds(m, t2, [name])[1][1] <= GROUND - 0.03:
                return v
            best = best or v
    return best


def _with_plumb(poses):
    m = build(variant='bufanda', pose=None)
    body_set = [b.name for b in m.bones() if b.name not in HANG and not b.name.startswith('scarf')]
    out = {}
    for name, table in poses.items():
        t = dict(table)
        if name not in NO_SNAP:
            # ground snap: the lowest point of the dog itself sits exactly on the floor
            snap_set = [n for n in body_set if not (name in HEAD_FLOOR and n in HEAD_SET)]
            low = world_bounds(m, t, snap_set)[1][1]
            bx = tuple(t.get('body', (0, 0, 0, 0, 0, 0))) + (0,) * 6
            t['body'] = bx[:4] + (bx[4] + GROUND - low,) + bx[5:6]
        if name in HEAD_FLOOR:
            hx0 = tuple(t.get('head', (0, 0, 0, 0, 0, 0))) + (0,) * 6
            target = GROUND - HEAD_FLOOR[name]
            lo, hi = -1.2, 1.2                              # head xRot delta: + = nose down
            for _ in range(40):
                mid = (lo + hi) / 2
                t['head'] = (hx0[0] + mid,) + hx0[1:6]
                if world_bounds(m, t, list(HEAD_SET))[1][1] > target:
                    hi = mid
                else:
                    lo = mid
            t['head'] = (hx0[0] + lo,) + hx0[1:6]
        sw = TAG_SWING.get(name, (0.0, 0.0))
        t['tag'] = _hang(m, t, 'tag', sw)
        for tb, extra in (('scarf_tail_front', (0, -0.07)), ('scarf_tail_back', (0.2, -0.28))):
            t[tb] = _hang(m, t, tb, (sw[0] + extra[0], sw[1] + extra[1]))
        out[name] = {k: tuple(round(float(x), 4) for x in v) for k, v in t.items()}
    return out


POSES = _with_plumb(_POSES)

ANIM_NOTES = """Choripan (ChoripanEntity, form DOG) -- animation notes.  Units: radians, offsets in model texels (2x density
inside scale_root: 2 texels = 1 vanilla pixel, 32 texels = 1 block).  t = ageInTicks, s = walk speed 0..1.  Every pose
is ADDED to the rest pose (Euler angles summed, offsets added to the pivot, the way HauntModel applies POSES).
Blend between poses over 4-6 ticks unless a note says SNAP (1-2 ticks).  right_* is on -X; MC applies Z * Y * X;
a positive xRot swings a hanging part's lower end backwards (+Z).
He is the audience's dog: every motion is bouncy, quick and a little clumsy (squash on landings, overshoot on head
turns).  The only exception is bipedal_180, which is slow, smooth and WRONG.

Looks (VARIANT_MATS; Java picks the texture by the entity's variant index)
* 0 'normal'  -> choripan.png (+ choripan_eyes.png).  The whole case: the Nona's red Aran sweater with the cream 'C'.
* 1 'bufanda' -> choripan_bufanda.png (+ choripan_bufanda_eyes.png, same glints).  The ending (casa.desayuno, the
  base, the bed in transition 2): the demon shredded the sweater, so the sweater texels (shells, spine cable, the four
  cuffs) are TRANSPARENT in this texture and the plain coat shows; set scarf.visible = true (VARIANT_TOGGLES).  Same
  geometry, same poses.
Render: entityCutoutNoCull + the emissive layer 'eyes' (choripan_eyes.png) drawn full-bright on top: 2 warm px per
eye (the glints), so at night he sparkles instead of glowing like a hostile mob.  When eyelids is visible the lids sit
in front of the glints and the depth test hides them (optionally skip the eyes layer while asleep).

Toggles (ModelPart.visible).  Every frame: start from TOGGLE_DEFAULT, apply VARIANT_TOGGLES[look], then
POSE_TOGGLES[pose] (a pose wins over the look).  Hiding a parent hides its children.
* scarf (child of neck; + its children scarf_tail_front, scarf_tail_back)   hidden by default; visible in 'bufanda'.
  The Nona's red garter-stitch scarf: a wrap on the shoulders (it rides over the collar at the nape; the collar, the
  D-ring and the tag stay in front of it at the throat), a knot on his left under the chin, two tails with a cream
  band and a red fringe hanging down his left side.
* eyelids (child of head)   hidden by default; visible in poses 'sleep' and 'sneeze'.  Fur lid caps over both eyes
  with a curved lash line.  ALSO the blink: in every look and pose, show it for 2 ticks every 60-120 ticks (double
  blink 1 time in 4), and for 3-4 ticks on a sudden scare (he squeezes his eyes shut).

Bones
* body (root, pivot at the hips, (0, 16, 10.5)): the barrel, chest prow, keel, rump and the sweater.  Idle: breathing
  dy = sin(t * 0.09) * 0.12.  Walk (dachshund trot, short fast steps): dy = -abs(sin(walk * 2)) * 0.35, zRot =
  sin(walk) * 0.035, xRot = sin(walk * 2) * 0.02.  Happy wag: the rear end wiggles WITH the tail -- body yRot =
  -sin(wag) * 0.05 * wagAmp (a dachshund wags from the hips).  Landing / hop: squash = body dy +0.6 for 2 ticks.
* right_front_leg, left_front_leg (pivot at the elbow, under the chest): walk xRot = +-sin(walk) * 0.7 * s, diagonal
  pairs with the back legs (right front with left back).
* right_front_paw, left_front_paw (wrist): lift-off flick xRot = max(0, -frontLegXRot) * 0.8; curl in 'beg' / 'sleep'.
* right_back_leg, left_back_leg (pivot at the hip, the thigh): walk xRot = -+sin(walk) * 0.6 * s.  Scratch-behind-the-
  ear gag (optional): right_back_leg xRot -0.9 + sin(t * 1.6) * 0.25 while sitting.
* right_back_paw, left_back_paw (ankle): follow the leg, flick like the front paws.
* tail (root at the rump, rest +32 deg = carried up in a happy curve) and tail_tip (rest +18 deg): THE WAG, every
  frame in every pose (it is how the audience reads his mood, and the demon form keeps it).  tail yRot =
  sin(t * wagSpeed) * wagAmp; tail_tip yRot = sin(t * wagSpeed - 0.7) * wagAmp * 1.4 (whip, lags the root).
  Moods: idle wagSpeed 0.55 / amp 0.35; happy (player near, being petted, family calls him) 0.95 / 0.6 + the body
  wiggle; excited (choripan in hand, fetch) 1.3 / 0.75; uneasy (form UNEASY, near Ofelia) 0.25 / 0.12 with xRot +0.5
  (tail low); growl / bark: wag off, tail stiff (pose value); sleep: no wag, a tail_tip twitch every 4-8 s; sneeze
  shake-off: wag 1.3 / 0.75.  In 'bipedal_180' a SLOW wag (0.2 / 0.25) is the creepiest thing in the shot.
* neck (pivot at the chest top): 30% of the head-look yaw/pitch.  Sniff walk: neck +0.35 and head -0.25 while
  following a scent, bob dy sin(t * 1.2) * 0.3.
* collar (child of neck, rest -30 deg so it sits across the forward-leaning neck): never animated.
* tag (child of collar, pivot at the D-ring; ring + backing plate + the engraved high-density card): hangs plumb by
  gravity.  Every frame set its rotation to cancel the collar's world rotation (plumb() in this file is the reference
  maths) and ADD a damped pendulum (world xRot / zRot; impulse -k * dAngle of the head/body, k ~ 0.7, damping 0.86 per
  tick, clamp +-0.6) so it jingles when he trots, barks or shakes.  FLOOR CLAMP: the tag must never sink below y 24;
  when the throat is low (growl, sniff, sleep) swing it until its lower edge rests on the floor (the POSES values are
  pre-solved that way).  It is the identity marker shared with the demon form: keep it facing where the throat faces.
  The name reads fully whenever the head is up (sit, beg, bark, tilt, bipedal_180); at rest the long muzzle hides the
  top line from the front, as on a real dachshund -- for a cinematic close-up of the tag use 'sit' or lift the head.
* scarf (toggle; child of neck): no motion.
* scarf_tail_front, scarf_tail_back (children of scarf, pivots at the knot): pendulums exactly like the tag (plumb +
  swing, 2-4 ticks of lag behind the tag, 1.3x its amplitude), floor clamp too.  Trotting: they flap outward (zRot
  -0.15 * s).
* head (pivot at the skull base): 70% of the head-look.  Idle: the occasional curious head-tilt (blend to 'tilt' for
  40 ticks every 10-20 s), ear perks.  Head turns overshoot by 10% and settle (puppy energy).
* eyelids (toggle): see Toggles (sleep, sneeze, blinks).
* lips (upper lip, pivot at the muzzle root): lifts in 'growl' (dy -1.4) to bare the upper teeth and canines; while
  growling, tremble dy += sin(t * 2.8) * 0.15.  Small lift in 'bark' / 'sneeze' / 'bipedal_180'.
* jaw (pivot under the cheek): pant after running or in the heat of the parrilla: xRot 0.14 + sin(t * 0.8) * 0.05
  with the tongue out.  Bark: SNAP to 0.5 then close over 4 ticks.  Dialogue (choripan.buen_chico): xRot = 0.14 +
  envelope * 0.35 from DialogueLines (10 Hz envelope).
* tongue (child of jaw): pant = xRot +0.3, dz -1.0 (the tip hangs out past the lips); 'beg' and 'belly_up' already
  loll it out (pose values).  Lick after eating: dz -1.5 for 4 ticks, twice.
* right_brow, left_brow (thin planes above the eyes, rest = puppy-worried): the whole acting range.  Raised and apart
  = curious / begging ('tilt', 'beg'); inner ends down = growl / bipedal_180; pushed down onto the eyes = sneeze.
* right_ear, left_ear (huge floppy ears, pivot at the top of the skull): pendulums.  Follow the head with 3-4 ticks of
  lag and overshoot (spring k 0.25, damping 0.8), flap outward on every trot step (zRot +-0.12 * s) and on the sneeze
  shake (+-0.6).  Alert (hears something): xRot -0.25 both, 6 ticks.  'tilt' flips the right ear inside out (a pose
  value: zRot -2.3) -- keep it, it is the gag.

Poses (POSES; the 'tag' / 'scarf_tail_*' entries are their plumb + floor-clamped hang for that frozen frame, and every
pose except 'belly_up' was grounded by FK: the lowest point of the dog sits exactly on y 24)
* sit: the default "te mira fijo" (casa.buen_chico before 3:33), waiting at the table, the calm beat.  Haunches down,
  chest up, the tag hanging free in front of the chest (the best tag close-up).  Wag on the floor (amp 0.35).
* beg: sitting up on the haunches, front paws curled, tongue out (Marta's choripan, the asado).  The tag hangs in
  front of the curled paws.  Bounce: body dy sin(t * 0.5) * 0.3, paws xRot sin(t * 0.5 + 1) * 0.15.
* belly_up: the calm beat ("rascada de panza"): rolled onto his back, legs up, head upside down, tongue out, ears
  splayed on the floor.  While rubbed: back legs kick xRot sin(t * 1.4) * 0.35 (the scratch reflex), tail thumps.
  Hand-placed (no FK grounding); enter it with a 10-tick roll (body zRot 0 -> 3.02 with an overshoot).
* tilt: the curious head tilt with the inside-out right ear.  Use it for "¿qué?" moments and whenever someone says
  his name.  Additive with walk.
* growl: at a hallucination (SanityManager delays it 40 ticks; he growls at that point first, so the audience learns to
  believe him).  Head low and aimed at the target (keep the head-look on the hallucination point), lips up, brows
  down, ears back, tail stiff and low, front legs braced.  Lip tremble (see lips).  Blend in over 8 ticks.
* bark: at spectral things (Ofelia when she moves, the voluta, the Nona's chair).  Front legs braced, chest up, mouth
  wide (teeth, tongue), ears thrown back, brows up.  Each bark SNAPS into the pose in 2 ticks with choripan.bark_cute,
  then relaxes 30% over 4 ticks; 2-4 barks per burst.
* sniff: nose to the floor following the family or a scent: neck down, muzzle level along the floor (chin touching
  it), ears forward, tail up and wagging.  Walkable: add the walk cycle; bob the neck (see neck).
* sneeze: THE END of casa.parrilla (after the retract and the voluta, "un salchicha temblando estornuda y mueve la
  cola").  Sequence: (1) wind-up 8 ticks: blend toward neck -0.2 / head -0.15 / lips -0.06 / jaw 0.06 with eyelids
  visible ("ah... ah..."); (2) SNAP to 'sneeze' in 2 ticks on choripan.sneeze (head snapped down, eyes squeezed, nose
  wrinkled, mouth open, ears flung forward), hold 3 ticks; (3) shake-off 20 ticks: body zRot = sin(t * 2.2) * 0.22 *
  decay, head zRot = -sin(t * 2.2) * 0.35 * decay, ears zRot +-0.6 * decay, tag + scarf tails swinging, wag 1.3 /
  0.75; eyelids hidden when the shake ends.  Then 'tilt' for 20 ticks (dazed, proud).  Shivering before it: body
  zRot sin(t * 3.1) * 0.03.
* sleep: curled at the Nona's feet (casa.calma) and asleep on your bed with the scarf ('bufanda', the base).  Lying on
  the chest, front legs stretched forward, hind legs tucked to his left, the head turned back toward the hip with the
  chin on the floor (solved by FK), the tail curled forward round his right side, eyelids on.  Breathing: body dy
  sin(t * 0.06) * 0.2 and ribs (no extra bone: the breathing is enough); ear twitch every 5-10 s; dream paddle: front
  paws xRot sin(t * 0.9) * 0.2 for 20 ticks every 20-40 s; tail_tip twitch.  Wake-up: hide eyelids, 'tilt' for 10.
* bipedal_180: THE CLIP (casa.buen_chico, 3:33): "¿Quién es un buen chico?... YO NO."  Standing upright on the hind
  legs with his BACK to the player, the neck spun 180 deg round the spine so the face (with the collar and the gold
  'CHORIPÁN' tag under the chin, fully legible) stares straight back at the player over the sweater; Exorcist head
  roll (head zRot 0.3), chin up, lip lifted over the teeth, brows down, the limp front legs splayed behind him, the
  tail poking out of his lower back TOWARD the camera (it is what tells you he is backwards).  The entity keeps
  facing the player as usual (the pose itself turns the body away: body yRot pi, dz -10.6 recentres the feet on the
  entity origin).  Disable the head-look while in this pose (the pose aims the face).
  Staging (works with the beat's light flicker): (1) 'sit', staring.  (2) During a 3-tick blackout SNAP to
  'bipedal_180' but with neck zRot 0 instead of pi and head zRot 0: he is standing with his back to you, looking
  away.  (3) Lights on, hold 12 ticks.  (4) THE TURN: neck zRot 0 -> pi over 36 ticks, ease-in-out with two 3-tick
  hitches (at ~60 and ~120 deg; choripan.crack on each), head zRot 0 -> 0.3 in the last 10; the tag swings with it.
  (5) The line: jaw from the dialogue envelope (see jaw), a slow wag (0.2 / 0.25).  (6) "YO NO.": SNAP jaw 0.5 for
  4 ticks.  (7) Drop to all fours (blend to rest in 6 ticks, neck spin back to 0 in the same 6) and run to the patio.
  The previous 'turn' pose (a sitting head-spin that hid the face behind the skull) is superseded by this one.

Geometry notes for Java
* The engraved card is a (19, 16, 12) box with CubeDeformation -6 (renders 7 x 4 x 0): box UV ignores the
  deformation, so its front keeps all 19 x 16 texels (2.7 x 4 texels per unit; the glyphs are 6 rows tall to stay
  ~0.7 wide-to-tall).  Its four side faces have zero area and its back is transparent; it sits 0.05 in front of the
  gold backing.  The generated createBodyLayer() reproduces it exactly (texOffs + addBox + CubeDeformation).
* UV: packed by face masks with a 1-texel extruded gutter (ChoriModel.pack / paint); no texel is shared.
"""
