"""Nona Pocha (Nelida 'Pocha' Bertolotti, 73) -- the grandmother of the Casa Morales (DEAD LINE, case 'casa').

Host #4 and the twist of the case: the girl possessed in 1961, who calls the demon back into herself to free her
granddaughter.  Authored at 2x texel density (model.scale = 0.5).  +Y down, ground y = 24, faces -Z, right_* on -X.
See the module docstring of ANIM_NOTES (bottom of the file) for the animation contract.

Design sketch
-------------
Read in one glance: a tiny, hunched, adorable Argentine nona -- and the same silhouette is what floats in the
rocking chair at the end.  Lovable by day (big magnified eyes behind coke-bottle lenses, rouge, pearls, a red wool
ball in her pocket, tennis balls on the walker); terrifying possessed (cracked lenses, one glassy blue eye, one
black hole weeping black, jaw hanging to the chest with the dentures floating in front, white hair drifting).

Silhouette: 1.5 blocks to the top of the bun.  A pear: narrow sloped shoulders, a dowager's hump, wide hips under a
mid-calf floral skirt, short legs in thick stockings and tartan felt slippers.  The torso leans 22 deg forward from
the waist, the neck juts forward another 30 deg, and the head tips back up so she looks at you.  The head is big
(16 x 18 face, the family style of Marta and Jorge) with a set grey perm, side puffs over the ears and a netted bun
on the back of the crown.  The round glasses are the icon: two thick tortoiseshell rings, 7 x 7 each, bigger than
her eye sockets.
Accessories are bones of the model so they move and float with her: the aluminium walker (front wheels -- one of them
squeaks and is its own bone -- cut tennis balls on the back legs, a granny-square knitting bag on the front bar)
and the light-oak rocking chair (curved runners, crocheted cushion, spindle back, a lace doily on the crest).

Face (16 x 18 hand-placed grid, FACE below; rows 0-13 on the skull, 14-17 on the jaw / jowls / chin):
* hair set in waves, pulled back to the bun; pencilled thin brows on their own bones (expressive: kind / furious);
* round glasses on their own bone: tortoiseshell frames (amber flecks), magnified hazel eyes with a glint and a
  heavy lid behind a pale glass with a glare streak.  'eyes' layer = the lens glass (everything but iris, pupil and
  lid line), so at night they glow white with two small dark irises inside;
* a bulbous nose, rouge apples, powder highlights, forehead lines, nasolabial folds, marionette lines, a mole with
  one hair beside the mouth, thin coral lipstick with lip lines, jowls and a soft double chin;
* a hinged jaw with a hidden throat box: it can drop all the way to the chest (dislocated) while side flaps of
  skin stretch to the skull.

Looks (VARIANT_MATS): 'normal' and 'poseida' (index 1).  The possessed texture keeps the clothes but turns the skin
bloodless grey-lilac with veins, whitens and frays the hair, cracks the glasses in a spider web: behind the right
lens (viewer's left) a glassy blue eye, the left lens shattered open on a black hole that weeps black down the
cheek, the jaw and the neck (a rhyme with Ofelia's broken eye); hairline porcelain cracks run from the hole to the
mouth corner and the lipstick is smeared.  The emissive layer of 'poseida' glows only the blue eye and the cracks.
Toggle bones for the possessed look: hair_loose_0..4 (shown) and bun (hidden); the floating dentures are a pose
toggle of 'scream_dentures'.
"""
import math
import os
import sys

import numpy as np

from mcmodel import Model, hash3, face_light, pick, rot_matrix, fbm
from rig import Rig
from paint import hx, mix


def pal(*h):
    return [hx(c) for c in h]


def A(c, a=255):
    return (c[0], c[1], c[2], int(a))


# ------------------------------------------------------------------ palettes (dark -> light, hue shifted)
SKIN = pal('#40232a', '#5e3437', '#7e4a49', '#9d625d', '#b97c73', '#cf978b', '#e0b0a3', '#ecc6ba', '#f5dbd1',
           '#fbede7')
SKIN_P = pal('#1a1824', '#2a2636', '#3d3749', '#544c5e', '#6e6577', '#887e90', '#a299a8', '#bab2bd', '#d0c9d0',
             '#e4dfe2')
ROUGE = pal('#b5525e', '#cf6e78', '#e4949a')
LIP = pal('#4e1424', '#7a2236', '#a3364c', '#c44f64', '#dc7584')
LIP_P = pal('#1a0a12', '#3a1220', '#5e1c30', '#7e2a40', '#9a4456')
MOLE = pal('#2e1a14', '#4a2c20', '#6a4430')
VEIN = hx('#4a4a78')
HAIR = pal('#2b2a38', '#424157', '#5d5c74', '#79788f', '#9695aa', '#b2b1c3', '#cbcad9', '#e0dfea', '#f1f0f6')
HAIR_P = pal('#45434e', '#62606c', '#83818c', '#a5a3ad', '#c4c3cb', '#dddce2', '#efeef2', '#f9f9fb', '#ffffff')
NET = pal('#1b1a26', '#2e2c3c')
PIN = pal('#1a1a20', '#3a3a44', '#6a6a78')
CARD = pal('#1d050c', '#310913', '#470e1c', '#5f1426', '#781c31', '#91263d', '#a9344b', '#bf465b', '#d25d6d')
DRESS = pal('#060918', '#0b1128', '#111a3a', '#18244c', '#213060', '#2c3d74', '#3a4c88')
FLOWER = {'p': hx('#ea8ea6'), 'P': hx('#b5506e'), 'w': hx('#e6e2ee'), 'W': hx('#a9a6bc'), 'y': hx('#f0cf60'),
          'g': hx('#4f9168'), 'G': hx('#2c5c44')}
LACE = pal('#8a8492', '#ada8b6', '#cfcbd6', '#e7e4ec', '#f8f6fa')
STOCK = pal('#3e2a22', '#5c4032', '#7a5844', '#957058', '#ad886d', '#c2a083', '#d4b69a', '#e2cab1')
TARTAN = pal('#0d1611', '#15221a', '#1f3125', '#2a4232', '#375540', '#466a4f')
T_RED = pal('#5e1418', '#8e2228', '#b8363a')
T_YEL = hx('#cfa84a')
T_NAVY = pal('#0c1028', '#161c3e')
SOLE = pal('#120d0b', '#1e1713', '#2c221c', '#3b2f27', '#4c3e33', '#5e4d40')
PEARL = pal('#6d6872', '#9f99a3', '#c9c3c8', '#e6e1e0', '#f7f4ef', '#ffffff')
GOLD = pal('#4a300a', '#7a5414', '#a8791f', '#d1a334', '#ecc85a', '#fbe6a0')
FRAME = pal('#120806', '#24110a', '#3a1c0f', '#552a14', '#73391a', '#94501f')
AMBER = pal('#a8621e', '#d08a34')
GLASS = pal('#8197aa', '#a8bccb', '#c8d8e3', '#e2edf3', '#f4f9fb', '#ffffff')
IRIS = pal('#24160c', '#4a301c', '#6f4c2c', '#94703e', '#b89458')
BLUE = pal('#06102a', '#0e2152', '#173c88', '#2462bd', '#468ce2', '#86c0f6', '#e8f8ff')
TEAR = pal('#010102', '#07060a', '#121018', '#24202e', '#5a5670')
VOID = pal('#000000', '#030204', '#08060a', '#100c12')
METAL = pal('#2a2e35', '#454b55', '#646c78', '#87909c', '#aab2bc', '#ccd2d9', '#eef1f4')
FOAM = pal('#0e0e12', '#18181e', '#24242c', '#33333d', '#46464f')
TENNIS = pal('#5a6a12', '#82981c', '#a9c42a', '#c8de44', '#e2f070', '#f4fbb0')
OAK = pal('#4a2e16', '#6b4422', '#8c5e30', '#ab7a42', '#c49656', '#d8b06e', '#e8c88c', '#f4dfb0')
WOOL = pal('#2a0406', '#4a080c', '#6e0e14', '#94161c', '#b82428', '#d63c3a', '#ec6658', '#f89a88')
GOURD = pal('#24110a', '#3e2012', '#5c321c', '#7c4626', '#9a5c32', '#b87a46')
YERBA = pal('#2e3a12', '#4a5a1c', '#6a7c2a', '#8ca040')
TEETH = pal('#7a7262', '#b0a890', '#d8d0b8', '#efe9d8', '#fbf8ee')
GUM = pal('#5a1424', '#86263a', '#b04456', '#d06a7a', '#e894a0')
MOUTH = pal('#040102', '#100408', '#20080e', '#360e18', '#521a26', '#6e2a36')
TONGUE = pal('#5a1a26', '#7e2a38', '#a04252', '#bc5e6c')
AID = pal('#6a5040', '#8e6e58', '#b08e74', '#cdac90')
TISSUE = pal('#a6a3b0', '#cbc8d2', '#e9e7ee', '#fbfafc')
SQUARES = [hx('#e2a83a'), hx('#2f8f8a'), hx('#8a4a9a'), hx('#d8603a'), hx('#e6dcc4')]
SQ_DARK = hx('#16131c')

_PAINT = {'variant': 'normal'}     # set by the material while painting; read by the variant-aware glow decals


# ------------------------------------------------------------------ geometry helpers
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


def bpos(ctx):
    """Authored position of the texel centre in its bone's frame (+ the cube's frame offset `ho`)."""
    lx, ly, lz = local(ctx)
    c = ctx.cube
    ho = getattr(c, 'ho', (0.0, 0.0, 0.0))
    return c.o[0] + lx + ho[0], c.o[1] + ly + ho[1], c.o[2] + lz + ho[2]


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


def corner_dist(ctx):
    w, h, d = ctx.cube.size
    u = around(ctx)
    return min(abs(u - c) for c in (0, w, w + d, 2 * w + d, 2 * (w + d)))


def edge(ctx):
    return min(ctx.i, ctx.j, ctx.w - 1 - ctx.i, ctx.h - 1 - ctx.j)


def h2(a, b, s=0):
    return hash3(a, b, 0, s)


def fl(v):
    return int(math.floor(v))


SIDE = ('front', 'back', 'west', 'east')


def kind(ctx):
    return ctx.cube.kind


def nm(ctx):
    return ctx.cube.name


# ------------------------------------------------------------------ the face (head-local coordinates)
# 16 x 18: col c <-> x [-8 + c, -7 + c], row r <-> y [-14 + r, -13 + r].  Skull rows 0-13, jaw rows 14-17 (jaw cols
# 2-13, jowls cols 0-1 / 14-15, chin cube cols 5-10 rows 16-17).  The lenses cover cols 0-6 / 9-15 rows 5-11, the
# nose bridge cols 7-8 rows 6-9, the nose bulb cols 6.5-9.5 rows 10-12, the rouge cheek cubes cols 1-3 / 12-14 rows
# 12-13, the brows cols 1-5 / 10-14 row 4.
#   digits skin ramp  k crease  K deep crease  p powder  r/R rouge  u/U upper lip  l/L lower lip  c lip corner
#   s shadow  n nostril  m mole  M mole hair  e/E lid line  w eye white  i iris  o pupil  H/h hair  v vein (poseida)
GX0, GY0 = -8.0, -14.0
FACE = [
    # 0123456789012345
    "HHhHHHHhHHHHhHHH",   # r0  y-14  under the hair shell
    "HhHHhHHHHhHHhHHh",   # r1  y-13
    "6788889pp9888876",   # r2  y-12  forehead (the set waves of the shell scallop over it)
    "67kKkk8998kkKk76",   # r3  y-11  forehead lines
    "6788kk7997kk8876",   # r4  y-10  (brows)
    "5678877997788765",   # r5  y-9   lens top
    "56eEEe6886eEEe65",   # r6  y-8   heavy lids
    "5ewiiwe77ewiiwe5",   # r7  y-7
    "5wiooiw67wiooiw5",   # r8  y-6
    "5kwiiwk67kwiiwk5",   # r9  y-5
    "56kkkk6776kkkk65",   # r10 y-4   bags under the eyes
    "567k66s77s66k765",   # r11 y-3   lens bottom
    "5rRr6Kssss6KrRr5",   # r12 y-2   rouge apples | the folds start | shadow under the nose
    "4rr6K7cuUuc7Mrm4",   # r13 y-1   upper lip (thin, lip lines) | nasolabial folds | the mole + its hair
    "44K6kclLLlck6K44",   # r14 y0    lower lip (jaw from here)
    "3456k76886k76543",   # r15 y1    marionette lines
    "x3456789987654x3",   # r16 y2    chin
    "xx34567777654xxx",   # r17 y3    under the chin
]
assert all(len(r) == 16 for r in FACE), [len(r) for r in FACE]

# possessed overrides (same grid): the right eye glassy blue, the left a black hole weeping black, porcelain cracks
# from the hole to the mouth corner, smeared lipstick, veins at the temples
FACE_P = [
    # 0123456789012345
    "................",   # r0
    "................",   # r1
    "..v.........v...",   # r2
    ".v...........v..",   # r3
    "v..............v",   # r4
    "................",   # r5
    "..kKKk...kOOk...",   # r6
    ".kbBBbk.kOVVOk..",   # r7
    ".bBgBBb.OVVVVO..",   # r8
    ".kbBBbk.kOVVOk..",   # r9
    "..kkkk...kTTk...",   # r10
    "........x.TT....",   # r11
    "......x...TTx...",   # r12
    ".......cuUxTT...",   # r13
    "......lLLxlT....",   # r14
    "...........T....",   # r15
    "...........T....",   # r16
    "...........t....",   # r17
]
assert all(len(r) == 16 for r in FACE_P), [len(r) for r in FACE_P]


def face_char(x, y, grid):
    c = fl(x - GX0)
    r = fl(y - GY0)
    if 0 <= r < len(grid) and 0 <= c < 16:
        return grid[r][c]
    return None


def face_rgba(ch, P):
    S = SKIN_P if P else SKIN
    if ch.isdigit():
        return S[int(ch)]
    L = LIP_P if P else LIP
    return {
        'H': (HAIR_P if P else HAIR)[3], 'h': (HAIR_P if P else HAIR)[5],
        'k': S[4], 'K': S[3], 'p': mix(S[9], hx('#ffffff'), 0.5),
        'r': S[6] if P else mix(S[6], ROUGE[2], 0.55), 'R': S[5] if P else mix(S[6], ROUGE[1], 0.75),
        'u': L[1], 'U': L[3], 'l': L[2], 'L': L[4], 'c': L[0],
        's': S[5], 'n': S[2], 'm': MOLE[1], 'M': MOLE[0],
        'e': S[3], 'E': S[2], 'w': hx('#f2ece6'), 'i': IRIS[2], 'o': IRIS[0],
        # possessed
        'v': VEIN, 'b': BLUE[3], 'B': BLUE[4], 'g': BLUE[6], 'O': VOID[3], 'V': VOID[0],
        'T': TEAR[1], 't': TEAR[2], 'x': SKIN_P[1],
    }.get(ch, S[5])


# ------------------------------------------------------------------ materials
def skin_paint(ctx, P):
    S = SKIN_P if P else SKIN
    f = ctx.face
    n = nm(ctx)
    x, y, z = bpos(ctx)
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    v = 0.62 + face_light(ctx) * 1.0
    face_cube = n in ('skull', 'jaw', 'cheek', 'jowl', 'chin')
    if face_cube and f == 'front':
        if P:
            ch = face_char(x, y, FACE_P)
            if ch and ch != '.':
                return A(face_rgba(ch, True))
        ch = face_char(x, y, FACE)
        if ch and ch not in 'x':
            c = face_rgba(ch, P)
            if n == 'cheek':
                c = mix(c, ROUGE[2] if not P else S[7], 0.25 if fl(lx) == 1 else 0.0)
            return A(c)
        return A(pick(S, v))
    if n == 'cheek':
        if f == 'top':
            return A(S[8])
        if f == 'bottom':
            return A(S[4])
        return A(mix(pick(S, 0.66 + face_light(ctx)), ROUGE[1], 0.0 if P else 0.3))
    if n == 'chin':
        if f == 'bottom':
            return A(S[3])
        if f == 'top':
            return A(S[6])
        return A(pick(S, 0.58 + face_light(ctx)))
    if n == 'jowl':
        inner = (f == 'east') if ctx.cube.sx < 0 else (f == 'west')
        if inner:
            return A(MOUTH[3] if lz > 1.0 else (LIP_P if P else LIP)[1])   # inside of the cheek (jaw dropped)
        if f == 'top':
            return A(MOUTH[2])
        if f == 'bottom':
            return A(S[3])
        if f == 'back':
            return A(S[4])
        vv = 0.58 + face_light(ctx) - ly * 0.03
        if f in ('west', 'east') and fl(lz) == 2:
            vv -= 0.08
        return A(pick(S, vv))
    if n == 'skull':
        if f == 'bottom':
            # underside of the upper jaw: toothless gum ridge at the front (seen when the jaw drops), dark beyond
            if abs(x) < 6.0 and z < -2.0:
                if z < -7.5:
                    return A((GUM if not P else MOUTH)[3 if abs(x) < 4.5 else 2])
                if z < -6.0:
                    return A((GUM if not P else MOUTH)[1])
                return A(MOUTH[1] if z < -4 else MOUTH[0])
            return A(pick(S, 0.4))
        if f in ('west', 'east'):
            vv = 0.6 + face_light(ctx)
            if z < -5.0 and -9.0 < y < -2.0:
                vv += 0.05                                              # temple / cheekbone plane
                if z < -7.0 and fl(y) in (-7, -5) and fl(z) == -8:
                    vv -= 0.12                                          # crow's feet
            if -1 < y < 1 and z < -4:
                vv -= 0.05
            if P and -9 < y < -2 and -8 < z < -4 and ((fl(y) * 3 + fl(z)) % 5 == 0):
                return A(VEIN)
            if P and f == ('east') and -2 <= y and z < -7.5 and fl(y) % 2 == 0:
                return A(TEAR[2])
            return A(pick(S, vv))
        if f == 'back':
            return A(pick(S, 0.55 - (y + 5) * 0.01))
        return A(pick(S, v))
    if n == 'jaw':
        if f == 'top':
            # lower gum ridge (toothless) + tongue, seen when the jaw drops
            if z < -7.0:
                return A((GUM if not P else MOUTH)[2])
            if abs(x) < 3.5:
                return A(TONGUE[2] if z < -4 else TONGUE[1])
            return A(MOUTH[2])
        if f == 'bottom':
            return A(pick(S, 0.36))
        if f in ('west', 'east'):
            return A(pick(S, 0.55 + face_light(ctx) - ly * 0.03))
        return A(pick(S, v))
    if n == 'neck':
        # turkey neck: vertical cords, horizontal creases, a shadow under the jaw
        vv = 0.55 + face_light(ctx)
        if f == 'front':
            if fl(lx) in (1, 3):
                vv -= 0.07
            if fl(ly) in (1, 3):
                vv -= 0.05
            if P and fl(lx) == 3 and ly > 1:
                return A(TEAR[1])                                       # the black tear runs down the neck
        if ly < 1.0 and f in SIDE:
            vv -= 0.06
        return A(pick(S, vv))
    if n == 'wattle':
        vv = 0.58 + face_light(ctx)
        if f == 'front' and fl(ly) == 1:
            vv -= 0.08
        if f == 'bottom':
            vv -= 0.1
        return A(pick(S, vv))
    if n == 'nose':
        vv = 0.66 + face_light(ctx)
        if f == 'front':
            vv += 0.06 if fl(lx) == 0 else 0.0
        if f == 'top':
            vv += 0.08
        return A(pick(S, vv))
    if n == 'nose_tip':
        if f == 'bottom':
            cx = fl(lx)
            return A(S[1] if cx in (0, 2) else S[3])                   # nostrils
        if f == 'front':
            if fl(ly) == 0 and fl(lx) == 1:
                return A(mix(S[9], hx('#ffffff'), 0.4))                 # powdered shine on the tip
            vv = 0.7 - ly * 0.08
            if not P:
                return A(mix(pick(S, vv), ROUGE[2], 0.2))               # a rosy nose
            return A(pick(S, vv))
        return A(pick(S, 0.6 + face_light(ctx)))
    if n == 'ear':
        vv = 0.6 + face_light(ctx)
        if f in ('west', 'east'):
            if 0.6 < lz < 2.4 and 0.8 < ly < h - 0.8:
                vv -= 0.12                                              # the ear bowl
            if ly > h - 1.4:
                vv += 0.06                                              # fleshy lobe
        return A(pick(S, vv))
    if n in ('palm', 'fingers', 'thumb'):
        vv = 0.6 + face_light(ctx) * 1.1
        if n == 'fingers' and f in SIDE:
            if fl(around(ctx)) % 2 == 1 and f in ('front', 'back'):
                vv -= 0.06                                              # finger separations
            if fl(ly) == 0:
                vv -= 0.08                                              # knuckle crease
        if n == 'palm' and f in ('front', 'back') and fl(lx) == 1 and fl(ly) == 1 and not P:
            return A(mix(S[5], hx('#8a5a3a'), 0.4))                     # an age spot
        if n == 'fingers' and getattr(ctx.cube, 'ring', False) and fl(ly) == 0:
            if f in SIDE and fl(around(ctx)) in (3, 4, 9, 10):
                return A(GOLD[4] if f in ('front', 'west') else GOLD[2])   # wedding ring
        if P and n == 'fingers' and fl(ly) == ctx.cube.size[1] - 1:
            vv -= 0.12                                                  # dark fingertips
        return A(pick(S, vv))
    return A(pick(S, v))


def hair_paint(ctx, P):
    """Set grey perm, combed back to the bun: strand columns with lit segments, scalloped hairline in front, side
    puffs, a lavender rinse.  Possessed: bleached white, frayed, uncombed."""
    Hh = HAIR_P if P else HAIR
    f = ctx.face
    n = nm(ctx)
    x, y, z = bpos(ctx)
    lx, ly, lz = local(ctx)
    if n == 'hair':
        if f == 'bottom':
            return None
        if f == 'front':
            col = fl(x + 8)
            wave = 1.2 * abs(math.sin((x + 8) * math.pi / 5.5))
            edge_y = -12.6 + wave * 0.9 + (0.6 if col in (7, 8) else 0.0)
            if P:
                edge_y += 0.8 * h2(col, 3, 41)
            if y > edge_y:
                return None
        if f in ('west', 'east'):
            if z < -3.0 and y > -9.0:
                return None                                             # cheek / temple below the side puffs
            if y > -5.6 and z < 3:
                return None
            if P and y > -7.5 and h2(fl(z * 2), fl(y), 7) > 0.6:
                return None
        if f == 'back' and y > -6.0 and h2(fl(x + 30), 3, 13) > 0.5:
            return None                                                 # wispy nape
        u = x if f in ('front', 'back', 'top') else z
        along = z if f == 'top' else y
        col = fl(u + 40)
        hs = h2(col, 0, 11)
        vv = 0.5 + face_light(ctx) * 0.8 + (hs - 0.5) * 0.16
        if fl(along * 0.8 + hs * 7) % 4 == 0:
            vv += 0.13                                                  # lit strand segment (the set wave)
        if col % 3 == 0:
            vv -= 0.09                                                  # groove between combed strands
        if f == 'top':
            vv += 0.05
            if abs(x) < 0.6:
                vv -= 0.12                                              # centre parting
        if P:
            vv += 0.06
            if h2(fl(u * 2), fl(along), 9) > 0.86:
                vv -= 0.25                                              # flyaway shadows
        return A(pick(Hh, vv))
    if n == 'wave':
        # permed puff over each ear: rolled curls (rows of C shapes)
        if f == 'bottom':
            return A(Hh[1])
        u = z if f in ('west', 'east') else x
        vv = 0.5 + face_light(ctx) * 0.8
        ph = (u * 0.9 + (y + 20) * 0.0)
        if fl(y + 20) % 3 == 0:
            vv -= 0.1
        if fl(ph + (y + 20) * 0.5) % 3 == 0:
            vv += 0.12
        if f in ('west', 'east') and edge(ctx) == 0:
            vv -= 0.08
        if P:
            vv += 0.05
        return A(pick(Hh, vv))
    if n in ('bun', 'bun_top'):
        # netted bun: wound hair + a dark diamond hairnet with knots, two bobby pins
        vv = 0.52 + face_light(ctx) * 0.9
        u = around(ctx) if f in SIDE else lx + lz
        vv += 0.1 * math.sin(u * 1.3 + ly * 0.9)
        if f in SIDE and fl(ly + u * 0.5) % 3 == 0:
            vv -= 0.08
        a = fl(u + ly) % 4
        b = fl(u - ly + 40) % 4
        if f == 'top':
            a = fl(lx + lz) % 4
            b = fl(lx - lz + 40) % 4
        if a == 0 or b == 0:
            if a == 0 and b == 0:
                return A(NET[1])                                        # net knot
            return A(NET[0] if h2(ctx.i, ctx.j, 5) > 0.25 else Hh[2])
        if n == 'bun' and f == 'east' and ctx.cube.part == 'A' and fl(ly) == 2 and 1 <= lz < 5:
            return A(PIN[2] if fl(lz) == 1 else PIN[1])                # bobby pin
        if n == 'bun' and f == 'west' and ctx.cube.part == 'B' and fl(ly) == 1 and 2 <= lz < 6:
            return A(PIN[2] if fl(lz) == 2 else PIN[1])
        return A(pick(Hh, vv))
    if n == 'strand':
        # possessed loose hair: white wet strands drifting, alpha-cut wisps, darker roots
        hgt = ctx.cube.size[1]
        u = lx if ctx.cube.size[0] > 0 else lz
        wdt = max(ctx.cube.size[0], ctx.cube.size[2])
        t = ly / hgt                                                    # 0 = tip, 1 = root
        centre = wdt / 2 + math.sin(t * 6.0 + ctx.cube.seed) * (wdt / 2 - 0.8) * (1 - t)
        half = 0.6 + 1.2 * t
        if abs(u - centre) > half:
            return None
        if t < 0.18 and h2(ctx.i, ctx.j, 3) > 0.5:
            return None
        vv = 0.55 + (0.2 if abs(u - centre) < 0.5 else 0.0) - t * 0.25
        return A(pick(HAIR_P, vv))
    return A(pick(Hh, 0.5))


def brow_paint(ctx, P):
    """Pencilled thin brows: thicker at the inner end."""
    Hh = HAIR_P if P else HAIR
    f = ctx.face
    lx, ly, lz = local(ctx)
    w = ctx.cube.size[0]
    inner = (w - 1 - lx) if ctx.cube.sx < 0 else lx
    if f == 'front':
        return A(Hh[0] if inner < 2 else Hh[1])
    if f == 'top':
        return A(Hh[2])
    if f == 'bottom':
        return A((SKIN_P if P else SKIN)[4])
    return A(Hh[1])


# ---------------- clothes
def rib(u, v):
    """Vertical knit ribbing (3-texel period: lit, mid, groove) with a faint stitch row."""
    cu = fl(u) % 3
    d = (0.05, 0.0, -0.08)[cu]
    if fl(v) % 2 == 0 and cu == 0:
        d += 0.03
    return d


def cable(u, v):
    """A 4-wide Aran cable (two strands crossing every 6 rows).  -> value offset or None outside."""
    if not (0 <= u < 4):
        return None
    ph = (v % 6) / 6.0
    cross = 2 + 1.6 * math.sin(ph * 2 * math.pi)
    d = abs(u + 0.5 - cross)
    if u < 0.5 or u > 3.5:
        return -0.12
    return 0.1 if d < 1.0 else -0.03


def card_paint(ctx, P):
    f = ctx.face
    n = nm(ctx)
    x, y, z = bpos(ctx)
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    v = 0.52 + face_light(ctx) * 1.0
    u = around(ctx) if f in SIDE else lx
    if f in SIDE:
        v += rib(u, ly)
    if n in ('torso', 'hips') and f == 'front':
        # the open cardigan: dress strip in the middle with the lace collar and the pearls
        if abs(x) < 2.0:
            if n == 'torso' and y < -7.0:
                return lace_collar(ctx, x, y)
            return dress_paint(ctx, P, override=(x, y))
    if n == 'torso' and f == 'top':
        if abs(x) < 2.0 and z < -1.5:
            return A(LACE[3])
    if n in ('cpanel', 'cpanel_lo'):
        sx = ctx.cube.sx
        inner = (w - 1 - lx) if sx < 0 else lx                          # 0 = the opening edge
        if f == 'front':
            if inner < 1.0:
                v += 0.1                                                # the ribbed button band
                if sx > 0 and fl(ly) % 3 == 1:
                    return A(PEARL[4] if fl(ly) % 2 else PEARL[3])      # pearl buttons on her left band
                if sx < 0 and fl(ly) % 3 == 1:
                    return A(CARD[1])                                   # buttonholes
            else:
                cb = cable(inner - 1.0, ly + (3 if n == 'cpanel_lo' else 0))
                if cb is not None:
                    v = 0.52 + face_light(ctx) + cb
            if n == 'cpanel_lo' and 1.0 <= ly < 4.5 and 1.5 <= inner < 6.0:
                if ly < 2.0:
                    if sx < 0 and 2.5 <= inner < 5.5:
                        return A(CARD[0])                               # pocket mouth (the yarn ball is in it)
                    v -= 0.1
                elif inner < 2.5 or inner >= 5.0 or ly >= 3.5:
                    v -= 0.06                                           # patch pocket seam
            if ly > h - 1.0:
                v -= 0.06                                               # hem rib
        elif f == 'bottom':
            v -= 0.1
    if n in ('hump', 'hump_top', 'yoke') and f == 'top':
        v += 0.04
    if n == 'hips':
        if f == 'bottom':
            return A(DRESS[1])
        if f in SIDE and y > -2.0 + 0.0 and ly > 5.0:
            return dress_paint(ctx, P)                                  # the dress shows under the cardigan
        if f in SIDE and 4.0 < ly <= 5.0:
            v -= 0.08                                                   # ribbed hem
    if n in ('sleeve', 'sleeve_lo'):
        if f == 'top':
            return A(pick(CARD, 0.45))
        if f == 'bottom':
            return A(pick(CARD, 0.3))
        if n == 'sleeve' and ly < 1.5:
            v += 0.05
        if n == 'sleeve' and ly > h - 2.0 and fl(around(ctx) + ly) % 4 == 0:
            v -= 0.08                                                   # elbow folds
    if n == 'cuff':
        if f in ('top', 'bottom'):
            cx, cz = abs(lx - w / 2), abs(lz - d / 2)
            return A(CARD[1] if max(cx, cz) < 1.5 else CARD[4])
        v += 0.04
    if P and f in SIDE and h2(fl(u * 2), fl(ly * 2), 77 + ctx.cube.seed) > 0.97:
        v -= 0.25                                                       # snags / pulled stitches
    return A(pick(CARD, v))


def lace_collar(ctx, x, y):
    """White crocheted Peter Pan collar of the dress at the neckline (scalloped lower edge)."""
    sc = -7.0 + 0.6 * abs(math.sin(x * math.pi / 1.5))
    if y > sc:
        return dress_paint(ctx, False, override=(x, y))
    vv = 0.7
    if (fl(x * 2) + fl(y * 2)) % 3 == 0:
        vv -= 0.2
    return A(pick(LACE, vv))


def dress_paint(ctx, P, override=None):
    """Navy dress with a small ditsy floral print (pink and white blossoms, yellow eyes, green leaves)."""
    f = ctx.face
    lx, ly, lz = local(ctx)
    if override:
        u, vy = override[0] + 40, override[1] + 40
    else:
        u = around(ctx) if f in SIDE else lx
        vy = ly
    v = 0.5 + face_light(ctx) * 1.0
    if f in SIDE and ctx.cube.kind == 'dress':
        w = ctx.cube.size[0]
        fold = math.sin((u + ctx.cube.seed) * 2 * math.pi / 5.0)
        v += fold * 0.05
        if fold < -0.85:
            v -= 0.05
    cu, cv = fl(u / 6.0), fl(vy / 6.0)
    ox = 1 + fl(h2(cu, cv, 21) * 4)
    oy = 1 + fl(h2(cu, cv, 22) * 4)
    fx, fy = fl(u) - cu * 6 - ox, fl(vy) - cv * 6 - oy
    kind_ = 'p' if h2(cu, cv, 23) > 0.45 else 'w'
    if f in SIDE or override:
        if (fx, fy) == (0, 0):
            return A(FLOWER['y'])
        if abs(fx) + abs(fy) == 1:
            return A(FLOWER[kind_] if (fx + fy) != 1 or fy == 0 else FLOWER[kind_.upper()])
        if (fx, fy) in ((2, 1), (-2, -1)) and h2(cu, cv, 24) > 0.4:
            return A(FLOWER['g'])
        if (fx, fy) == (2, 2) and h2(cu, cv, 24) > 0.4:
            return A(FLOWER['G'])
    if P and h2(fl(u), fl(vy), 31) > 0.985:
        v -= 0.2
    return A(pick(DRESS, v))


def skirt_paint(ctx, P):
    f = ctx.face
    n = nm(ctx)
    lx, ly, lz = local(ctx)
    h = ctx.cube.size[1]
    if f == 'bottom':
        return A(DRESS[0] if n != 'hem' else DRESS[1])                  # the dark inside of the skirt
    if f == 'top':
        return A(DRESS[1])
    c = dress_paint(ctx, P)
    if n == 'hem' and f in SIDE and ly > h - 1.0:
        return A(DRESS[1])                                              # stitched hem band
    if n == 'hem' and f in SIDE and ly < 1.0:
        return A(mix(c, DRESS[1], 0.4))
    return c


def stock_paint(ctx, P):
    """Thick opaque stockings: a back seam, the shin's sheen, sagging wrinkles at the ankle."""
    f = ctx.face
    n = nm(ctx)
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    v = 0.56 + face_light(ctx) * 1.0
    if f in SIDE:
        cd = corner_dist(ctx)
        if cd < 1.0:
            v -= 0.05
        if f == 'front' and abs(lx - w / 2) < 1.0:
            v += 0.06                                                   # shin highlight
        if f == 'back' and abs(lx - w / 2) < 0.5:
            v -= 0.1                                                    # seam
        if n == 'shin' and ly > h - 3.0 and fl(ly * 1.5 + around(ctx) * 0.3) % 2 == 0:
            v -= 0.08                                                   # sagging folds at the ankle
    if n == 'foot' and f == 'front':
        v += 0.04
    if P:
        v -= 0.04
    return A(pick(STOCK, v))


def tartan(u, v):
    """Escocesa felt: green blocks, navy band, thin red and yellow lines."""
    a, b = fl(u) % 8, fl(v) % 8
    if a == 3 or b == 3:
        return T_RED[1]
    if a == 6 and b % 2 == 0:
        return T_YEL
    base = 2 + (1 if a < 3 else 0) + (1 if b < 3 else 0)
    if 4 <= a <= 5 and 4 <= b <= 5:
        return T_NAVY[1]
    return TARTAN[base]


def felt_paint(ctx, P):
    f = ctx.face
    n = nm(ctx)
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    if n == 'pompom':
        vv = 0.55 + face_light(ctx) + (h2(ctx.i, ctx.j, 4) - 0.5) * 0.2
        return A(pick(WOOL, vv))
    if f == 'top':
        # the opening where the stocking foot goes in (back half), toe cap in front
        if lz > d - 4.5 and 1.0 <= lx < w - 1.0:
            return A(STOCK[3] if n != 'chancleta' else T_NAVY[0])
        c = tartan(lx * 1.0, lz * 1.0)
        return A(mix(c, hx('#ffffff'), 0.06))
    if f == 'bottom':
        return A(SOLE[1])
    c = tartan(around(ctx), ly + 2)
    if ly > h - 1.0:
        c = mix(c, hx('#000000'), 0.35)                                 # stitched edge to the sole
    if ly < 0.9:
        c = mix(c, hx('#ffffff'), 0.08)
    return A(c)


def sole_paint(ctx, P):
    f = ctx.face
    lx, ly, lz = local(ctx)
    v = 0.4 + face_light(ctx)
    if f == 'bottom':
        v = 0.25 + (0.08 if fl(lz) % 2 == 0 else 0.0)
    if f == 'top':
        v = 0.55
    return A(pick(SOLE, v))


# ---------------- jewellery, glasses
def pearl_paint(ctx, P):
    """Pearls: a necklace plane (beads with a lit pip), earrings and buttons."""
    n = nm(ctx)
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    if n == 'pearls':
        # a two-strand necklace hanging in a U on the chest
        for k, (sag, r0) in enumerate(((4.2, 0.0), (5.6, 1.0))):
            cx = lx - w / 2
            cy = r0 + sag * (1 - (cx / (w / 2)) ** 2) * 0.8 + 0.3
            if abs(ly - cy) < 0.6 and abs(cx) < w / 2 - 0.2:
                bead = fl(lx + k) % 2
                return A(PEARL[5] if bead == 0 and ly < cy else (PEARL[3] if bead == 0 else PEARL[1]))
        return None
    if n == 'chain':
        # beaded eyeglass chain (cadenita) hanging from the temple tips
        lx_ = lz if ctx.cube.size[0] == 0 else lx
        wd = max(d, w)
        cy = 0.5 + 6.0 * math.sin(min(1.0, lx_ / max(1.0, wd)) * math.pi * 0.5)
        if abs(ly - cy) < 0.55:
            return A(GOLD[4] if fl(lx_ * 2) % 2 == 0 else PEARL[4])
        return None
    vv = 0.6 + face_light(ctx) * 1.2
    if ctx.face == 'front':
        vv += 0.15
    return A(pick(PEARL, vv))


def lens_mask(i, j, n=7):
    """7x7 disc: 0 outside, 1 frame ring, 2 glass."""
    c = (n - 1) / 2.0
    r = math.hypot(i - c, j - c)
    if r > c + 0.6:
        return 0
    if r > c - 0.55:
        return 1
    return 2


# magnified eye inside a 7x7 lens (glass texels only): row, col -> char (relative to the lens grid)
LENS_EYE = [
    "..   ..",
    ". gg  .",
    " eEEEe ",
    " wiIiw ",
    " wiOiw ",
    ". w w .",
    "..   ..",
]


def crack_dist(i, j, cx, cy, rays):
    """Distance to the nearest ray (spider-web crack) from (cx, cy) + concentric rings."""
    dx, dy = i - cx, j - cy
    r = math.hypot(dx, dy)
    best = 9.0
    for a in rays:
        px, py = math.cos(a), math.sin(a)
        t = dx * px + dy * py
        if t > 0:
            best = min(best, abs(dx * py - dy * px))
    return r, best


def lens_texel(sx, i, j, P, front=True):
    """Colour of lens texel (i, j) (front-face grid, i to the viewer's right).  sx: -1 her right lens (viewer's
    left), +1 her left.  -> rgba or None (transparent)."""
    m = lens_mask(i, j)
    if m == 0:
        return None
    if m == 1:
        # tortoiseshell ring: dark brown with amber flecks, lit on the top-left arc
        hh = h2(i * 3 + (sx + 1) * 17, j * 5, 61)
        if hh > 0.78:
            return AMBER[0] if j > 3 else AMBER[1]
        return FRAME[4] if (j < 3 and i < 4) else (FRAME[2] if j > 3 else FRAME[3])
    if not P:
        ch = LENS_EYE[j][i]
        glare = (i - j) in (-2, -3) and j < 4                           # diagonal glare streak
        if ch == 'e':
            return mix(SKIN[4], GLASS[3], 0.3)
        if ch == 'E':
            return mix(SKIN[2], GLASS[2], 0.2)                           # the heavy upper lid
        if ch == 'i':
            return mix(IRIS[2], GLASS[3], 0.15)
        if ch == 'I':
            return IRIS[3]
        if ch == 'O':
            return IRIS[0]
        if ch == 'g':
            return GLASS[5]
        if ch == 'w':
            return mix(hx('#f4efe8'), GLASS[3], 0.4)
        if glare:
            return GLASS[5]
        return GLASS[3] if j < 3 else GLASS[2]
    # ---- possessed
    if sx < 0:
        # spider-web cracks over a glassy blue eye
        r, dc = crack_dist(i, j, 2.2, 2.6, (0.3, 1.5, 2.6, 3.6, 4.6, 5.6))
        ring = abs(r - 1.6) < 0.35 or abs(r - 3.0) < 0.3
        if dc < 0.42 or ring:
            return hx('#ffffff') if (i + j) % 2 == 0 else GLASS[4]
        if dc < 0.9:
            return GLASS[0]
        eye = math.hypot(i - 3.0, j - 3.2)
        if eye < 1.0:
            return BLUE[0] if eye < 0.5 else BLUE[2]                    # dilated pupil
        if eye < 2.2:
            return BLUE[4] if (i + j) % 2 else BLUE[3]                  # milky blue iris
        return mix(GLASS[1], BLUE[5], 0.25)
    # left lens: shattered open on the black hole -- jagged shards left on the rim
    r = math.hypot(i - 3.0, j - 3.0)
    ang = math.atan2(j - 3.0, i - 3.0)
    shard = 1.4 + 0.9 * (0.5 + 0.5 * math.sin(ang * 3.0 + 1.0)) + (0.6 if h2(i, j, 71) > 0.6 else 0.0)
    if r < shard:
        return None                                                     # the hole: see the socket behind
    return GLASS[4] if (i * 2 + j) % 3 == 0 else GLASS[1]


def lens_paint(ctx, P):
    f = ctx.face
    sx = ctx.cube.sx
    if f in ('front', 'back'):
        i = ctx.i if f == 'front' else ctx.w - 1 - ctx.i
        c = lens_texel(sx, i, ctx.j, P, f == 'front')
        if c is None:
            return None
        if f == 'back':
            if lens_mask(i, ctx.j) == 2:
                return A(GLASS[1] if not P else GLASS[0])
        return A(c)
    # rim faces: the thickness of the frame
    vv = 0.5 + face_light(ctx)
    if f in ('west', 'east'):
        if ctx.j < 2 or ctx.j > 4:
            return None                                                 # round: only the middle of the side
        return A(pick(FRAME, vv))
    if ctx.i < 2 or ctx.i > 4:
        return None
    return A(pick(FRAME, vv))


def frame_paint(ctx, P):
    vv = 0.48 + face_light(ctx)
    if nm(ctx) == 'temple':
        lx, ly, lz = local(ctx)
        if lz > ctx.cube.size[2] - 2.5:
            vv -= 0.08                                                  # the curled tip
        if h2(ctx.i, ctx.j, 63) > 0.8:
            return A(AMBER[0])
    return A(pick(FRAME, vv))


def lens_glow(img, u0, v0, w, h):
    """Emissive lens decal (front face).  normal: the glass glows white (iris, pupil and lid stay dark); poseida:
    only the cracks of the right lens and its blue eye glow; the left one is a hole."""
    px = img.load()
    P = _PAINT['variant'] == 'poseida'
    sx = lens_glow.sx_map.get((u0, v0), -1)
    for j in range(h):
        for i in range(w):
            if lens_mask(i, j) != 2:
                continue
            c = lens_texel(sx, i, j, P)
            if c is None:
                continue
            if not P:
                ch = LENS_EYE[j][i]
                if ch in 'iIOeE':
                    continue
                px[u0 + i, v0 + j] = (236, 244, 255, 255) if ch != 'w' else (200, 210, 225, 255)
            else:
                if sx > 0:
                    continue
                if c in (hx('#ffffff'), GLASS[4]):
                    px[u0 + i, v0 + j] = (220, 230, 255, 255)
                elif c in (BLUE[4], BLUE[3]):
                    px[u0 + i, v0 + j] = (60, 140, 255, 255)
                elif c == BLUE[2]:
                    px[u0 + i, v0 + j] = (30, 80, 200, 255)


lens_glow.sx_map = {}


def make_lens_glow(sx):
    def fn(img, u0, v0, w, h):
        lens_glow.sx_map[(u0, v0)] = sx
        lens_glow(img, u0, v0, w, h)
    return fn


# ---------------- props
def metal_paint(ctx, P):
    """Brushed aluminium tubes: a lit band along the top/front, dark underside, rivets at the joints."""
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    vv = 0.55 + face_light(ctx) * 1.2
    if f in ('front', 'west') and min(w, h, d) <= 1:
        vv += 0.12
    long_ = max(w, h, d)
    t = (lx if w == long_ else (ly if h == long_ else lz))
    if fl(t) % 7 == 3 and long_ > 8:
        vv -= 0.06
    if nm(ctx) in ('needle',):
        if t > long_ - 1.5:
            return A(GOLD[3] if f != 'bottom' else GOLD[1])            # knob at the end
        vv += 0.05
    if nm(ctx) == 'bombilla':
        vv += 0.1
        if ly < 1.0:
            return A(GOLD[3])
    if nm(ctx) == 'virola':
        return A(pick(METAL, 0.62 + face_light(ctx) + (0.1 if fl(lx + ly) % 2 == 0 else -0.05)))
    if P:
        vv -= 0.05
    return A(pick(METAL, vv))


def foam_paint(ctx, P):
    f = ctx.face
    n = nm(ctx)
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    if n == 'wheel':
        # grey hub + black tyre on the side faces, tread on the rest
        if f in ('west', 'east'):
            r = math.hypot(lz - d / 2, ly - h / 2)
            if r < 1.0:
                return A(METAL[4])
            if r < 1.6:
                return A(METAL[2])
            if r > min(d, h) / 2 + 0.2:
                return None
            return A(FOAM[2] if ly < h / 2 else FOAM[1])
        if f in ('front', 'back', 'top', 'bottom'):
            if (f in ('front', 'back') and (ly < 0.8 or ly > h - 0.8)):
                return None
            return A(FOAM[1] if fl(lz + ly) % 2 else FOAM[2])
    vv = 0.45 + face_light(ctx) + (h2(ctx.i, ctx.j, 8) - 0.5) * 0.12
    if fl(max(lx, lz)) % 2 == 0 and f in SIDE:
        vv += 0.05
    return A(pick(FOAM, vv))


def tennis_paint(ctx, P):
    """Cut tennis balls on the back legs of the walker: fuzzy yellow-green with the white seam curve."""
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    if f == 'top':
        cx, cz = lx - w / 2, lz - d / 2
        if abs(cx) < 0.6 and abs(cz) < 0.6:
            return A(METAL[2])                                          # the tube goes in
        return A(TENNIS[1])                                             # the cut edge
    u = around(ctx)
    seam = 1.5 + 1.0 * math.sin(u * 2 * math.pi / (2 * (w + d)) * 2)
    if abs(ly - seam) < 0.45:
        return A(hx('#f4f4ec'))
    vv = 0.58 + face_light(ctx) + (h2(ctx.i, ctx.j, 12) - 0.5) * 0.18
    if P:
        vv -= 0.15
    return A(pick(TENNIS, vv))


def bag_paint(ctx, P):
    """Crocheted granny-square knitting bag hanging from the walker: 4x4 squares (rings of colour) on black."""
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    if f == 'top':
        if 0.8 < lx < w - 0.8 and 0.5 < lz < d - 0.5:
            return A(WOOL[2])                                           # red wool inside
        return A(SQ_DARK)
    u = around(ctx) if f in SIDE else lx
    a, b = fl(u) % 4, fl(ly) % 4
    if a == 3 or b == 3:
        return A(SQ_DARK)
    sq = fl(u / 4) * 3 + fl(ly / 4) * 5
    ring = max(abs(a - 1), abs(b - 1))
    c = SQUARES[(sq + ring) % len(SQUARES)]
    if ring == 0:
        c = SQUARES[(sq + 3) % len(SQUARES)]
    c = mix(c, hx('#000000'), max(0.0, -face_light(ctx)) * 1.2)
    return A(c)


def knitting_paint(ctx, P):
    """Plane above the bag: two needles and a tuft of red wool poking out."""
    lx, ly, lz = local(ctx)
    w, h = ctx.cube.size[0], ctx.cube.size[1]
    i = fl(lx)
    j = fl(ly)
    # needle 1 leaning right, needle 2 leaning left
    for k, (x0, slope) in enumerate(((2.0, 0.35), (6.5, -0.3))):
        xx = x0 + (h - ly) * slope
        if abs(lx - xx) < 0.55 and ly > 0.5:
            if ly < 1.5:
                return A(GOLD[3])
            return A(METAL[5] if k == 0 else METAL[4])
    if ly > h - 3.0 and 1 <= i <= w - 2:
        if h2(i, j, 81) > 0.35 or ly > h - 1.8:
            return A(WOOL[4] if (i + j) % 2 else WOOL[3])
    return None


def wool_paint(ctx, P):
    """Red wool: ball (wound strands), knitted swatch, shooting yarn."""
    f = ctx.face
    n = nm(ctx)
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    vv = 0.55 + face_light(ctx) * 1.0
    if n == 'ball':
        u = around(ctx) if f in SIDE else lx + lz
        ph = (u * 0.8 + ly * 1.2) if (fl(u / 2) + fl(ly / 2)) % 2 == 0 else (u * 0.8 - ly * 1.2)
        vv += 0.12 * math.sin(ph * 2.2)
        if h2(ctx.i, ctx.j, 15 + ctx.cube.seed) > 0.9:
            vv += 0.15
        return A(pick(WOOL, vv))
    if n == 'tail':
        if abs(lx - (w / 2 + 0.7 * math.sin(ly * 0.8))) > 0.6:
            return None
        return A(WOOL[4] if fl(ly) % 2 else WOOL[3])
    if n == 'knit':
        # a knitted swatch (the scarf in progress): V stitches, cast-on row on the needle, ragged bottom
        if ly > h - 1.0 and h2(ctx.i, 0, 91) > 0.5:
            return None
        a = fl(lx) % 2
        b = fl(ly) % 2
        vv = 0.6 + (0.1 if a == b else -0.06)
        if fl(ly) == 0:
            vv += 0.1
        return A(pick(WOOL, vv))
    if n == 'yarn':
        # twisted 2-ply strand, lit and dark plies alternating
        u = around(ctx) if f in SIDE else lx
        ph = fl(ly + u) % 3
        return A(WOOL[(5, 4, 2)[ph]])
    if n == 'cushion':
        return cushion_paint(ctx, P)
    return A(pick(WOOL, vv))


def cushion_paint(ctx, P):
    """Crocheted cushion: red granny pattern with a cream picot border."""
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    if f == 'top':
        cx, cz = lx - w / 2, lz - d / 2
        ring = fl(max(abs(cx) / (w / 2), abs(cz) / (d / 2)) * 5)
        if ring >= 5 or (lx < 1 or lx > w - 1 or lz < 1 or lz > d - 1):
            return A(LACE[3] if (fl(lx) + fl(lz)) % 2 == 0 else LACE[2])
        c = (WOOL[4], WOOL[3], LACE[3], WOOL[5], WOOL[2])[ring % 5]
        if (fl(lx) + fl(lz)) % 2 == 0:
            c = mix(c, hx('#000000'), 0.15)
        return A(c)
    if f == 'bottom':
        return A(WOOL[1])
    if fl(around(ctx)) % 2 == 0:
        return A(LACE[3])
    return A(WOOL[3])


def oak_paint(ctx, P):
    """Light oak: grain along the long axis of each piece, darker edges, varnish highlights."""
    f = ctx.face
    n = nm(ctx)
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    if n == 'spindles':
        # the back: 5 turned spindles between the stiles (alpha between them)
        if f not in ('front', 'back') and w > 0:
            pass
        sp = (lx + 0.5) % 3.4
        if sp > 1.6:
            return None
        bead = fl(ly) % 6 in (0, 3)
        vv = 0.6 + (0.1 if sp < 0.7 else -0.05) + (0.08 if bead else 0.0)
        return A(pick(OAK, vv))
    if n == 'doily':
        # round crocheted lace doily over the crest rail (alpha holes)
        cx, cy = lx - w / 2, ly - h / 2
        r = math.hypot(cx / (w / 2), cy / (h / 2))
        if r > 1.0:
            return None
        ang = math.atan2(cy, cx)
        petal = 0.85 + 0.15 * math.cos(ang * 8)
        if r > petal:
            return None
        if 0.45 < r < 0.62 or (r > 0.25 and fl((ang + 4) * 8 / math.pi) % 2 == 0 and r < 0.4):
            return None
        return A(LACE[4] if r < 0.3 else LACE[3])
    long_ = max(w, h, d)
    if long_ == h:
        g_u, g_t = (lx if f in ('front', 'back') else lz), ly
    elif long_ == d:
        g_u, g_t = (ly if f in ('west', 'east') else lx), lz
    else:
        g_u, g_t = (ly if f in ('front', 'back') else lz), lx
    vv = 0.58 + face_light(ctx) * 1.1
    vv += (fbm(g_u * 1.7 + ctx.cube.seed, g_t * 0.18, 0, 2, 3) - 0.5) * 0.28
    if fl(g_u * 1.0 + 0.3 * math.sin(g_t * 0.4)) % 3 == 0:
        vv -= 0.05
    if edge(ctx) == 0 and min(ctx.w, ctx.h) > 1:
        vv -= 0.07
    if f == 'top':
        vv += 0.06
    if P:
        vv -= 0.08
    return A(pick(OAK, vv))


def gourd_paint(ctx, P):
    """Mate de calabaza: burnt brown gourd with a pyrographed band, yerba on top."""
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    if f == 'top':
        if (fl(lx) + fl(lz)) % 2 == 0:
            return A(YERBA[2])
        return A(YERBA[1] if h2(ctx.i, ctx.j, 5) > 0.5 else YERBA[3])
    vv = 0.5 + face_light(ctx) + (h2(ctx.i, ctx.j, 19) - 0.5) * 0.1
    if f in SIDE and fl(ly) == 1 and fl(around(ctx)) % 2 == 0:
        vv -= 0.2                                                       # pyrographed band
    if f in SIDE and corner_dist(ctx) < 1.0:
        vv -= 0.08
    return A(pick(GOURD, vv))


def dentures_paint(ctx, P):
    """Floating dentures: pink acrylic gums + a row of slightly yellowed teeth; the palate plate on the top/bottom."""
    f = ctx.face
    n = nm(ctx)
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    upper = n == 'denture_up'
    if f == 'front':
        gum_row = (ly < 1.0) if upper else (ly >= h - 1.0)
        if gum_row:
            return A(GUM[3] if fl(lx) % 2 else GUM[2])
        if fl(lx) in (0, w - 1):
            return A(TEETH[1])                                          # molars in shadow
        if fl(lx) % 2 == 1 and (ly > 1.3 if upper else ly < h - 1.3) and (ly < h - 0.4 if upper else ly > 0.4):
            return A(TEETH[2])
        return A(TEETH[4] if fl(lx) in (3, 4) else TEETH[3])
    if f in ('west', 'east'):
        if (upper and ly < 1.0) or (not upper and ly >= h - 1.0):
            return A(GUM[2])
        return A(TEETH[2])
    if (f == 'top' and upper) or (f == 'bottom' and not upper):
        return A(GUM[3] if lz < d - 1.0 else GUM[1])                   # the palate plate
    # biting surfaces
    if 0.6 < lx < w - 0.6 and lz < d - 1.0:
        return A(TEETH[3] if fl(lx + lz) % 2 else TEETH[2])
    return A(GUM[1])


def maw_paint(ctx, P):
    """Throat box revealed when the jaw drops: dark gullet, uvula, tongue root; flaps = stretched cheek skin."""
    f = ctx.face
    n = nm(ctx)
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    S = SKIN_P if P else SKIN
    if n == 'flap':
        # zero-thickness stretched skin between the skull and the dropped jaw: tendon strings + dark gaps
        u = lz
        if fl(u) % 2 == 0 and h2(fl(u), fl(ly), 51) > 0.25:
            return A(S[4] if fl(ly) % 3 else S[3])
        if ly > h - 3:
            return A(S[3])
        return None
    if f == 'front':
        cx = abs(lx - w / 2)
        if ly > h - 2.5:
            return A(TONGUE[2] if cx < 2.5 else MOUTH[3])               # tongue root rising from the jaw
        if cx < 0.8 and h - 6 < ly < h - 3.5:
            return A(GUM[1] if ly > h - 4.5 else MOUTH[4])              # uvula
        vv = 0.1 + (ly / h) * 0.35 - cx * 0.03
        return A(pick(MOUTH, vv))
    if f in ('west', 'east'):
        return A(MOUTH[3] if ly > h - 3 else MOUTH[1])
    return A(MOUTH[0])


def aid_paint(ctx, P):
    vv = 0.55 + face_light(ctx)
    lx, ly, lz = local(ctx)
    if ly < 1.0 and ctx.face in SIDE:
        return A(METAL[3])                                              # the little tube over the ear
    return A(pick(AID, vv))


def tissue_paint(ctx, P):
    lx, ly, lz = local(ctx)
    w, h = ctx.cube.size[0], ctx.cube.size[1]
    if (lx < 0.6 and ly > h - 0.8) or (lx > w - 0.6 and ly < 0.7):
        return None
    vv = 0.6 + (0.15 if (fl(lx) + fl(ly)) % 2 == 0 else -0.05)
    return A(pick(TISSUE, vv))


MATS = {
    'skin': skin_paint, 'hair': hair_paint, 'brow': brow_paint, 'card': card_paint, 'dress': skirt_paint,
    'stock': stock_paint, 'felt': felt_paint, 'sole': sole_paint, 'pearl': pearl_paint, 'gold': pearl_paint,
    'lens': lens_paint, 'frame': frame_paint, 'metal': metal_paint, 'foam': foam_paint, 'tennis': tennis_paint,
    'bag': bag_paint, 'knitting': knitting_paint, 'wool': wool_paint, 'oak': oak_paint, 'gourd': gourd_paint,
    'teeth': dentures_paint, 'maw': maw_paint, 'aid': aid_paint, 'tissue': tissue_paint,
}


def make_mat(variant):
    P = variant == 'poseida'

    def mat(ctx):
        _PAINT['variant'] = variant
        fn = MATS.get(kind(ctx))
        if fn is None:
            return A(hx('#ff00ff'))
        return fn(ctx, P)
    mat.variant = variant
    return mat


# ------------------------------------------------------------------ rig helpers
def _R(rot):
    return rot_matrix(*[math.radians(a) for a in rot])


def _euler(R):
    """Inverse of mcmodel.rot_matrix (Rz Ry Rx) -> (x, y, z) degrees."""
    sb = max(-1.0, min(1.0, -R[2, 0]))
    b = math.asin(sb)
    if abs(math.cos(b)) > 1e-6:
        a = math.atan2(R[2, 1], R[2, 2])
        c = math.atan2(R[1, 0], R[0, 0])
    else:
        a = math.atan2(-R[1, 2], R[1, 1])
        c = 0.0
    return (math.degrees(a), math.degrees(b), math.degrees(c))


def _T(p):
    M = np.eye(4)
    M[:3, 3] = p
    return M


def _RM(rot_deg):
    M = np.eye(4)
    M[:3, :3] = _R(rot_deg)
    return M


class Builder:
    """rig.Rig with bone-local authoring.  bone(at=...) is the pivot offset from the parent's pivot in the parent's
    own axes (absolute for a root); world=True takes a world rest position instead; wrot = desired world rotation.
    box(off=...) is the cube's min corner relative to the bone pivot, in the bone's own axes."""

    def __init__(self):
        self.r = Rig()
        self.W = {}

    def bone(self, name, parent=None, at=(0, 0, 0), rot=(0, 0, 0), world=False, wrot=None):
        if parent is None:
            Wp = np.eye(4)
            loc = np.array(at, float)
            absp = loc
        else:
            Wp = self.W[parent]
            pa = np.array(self.r.abs_pivot[parent])
            loc = Wp[:3, :3].T @ (np.array(at, float) - Wp[:3, 3]) if world else np.array(at, float)
            absp = pa + loc
        if wrot is not None:
            rot = _euler(Wp[:3, :3].T @ _R(wrot))
        self.r.bone(name, tuple(float(v) for v in absp), parent=parent, rot=tuple(float(v) for v in rot))
        self.W[name] = Wp @ _T(loc) @ _RM(rot)
        return name

    def world(self, name, p):
        return (self.W[name] @ np.array([p[0], p[1], p[2], 1.0]))[:3]

    def box(self, bone, off, size, kind, name=None, inflate=0.0, decals=None, sx=0, **attrs):
        p = self.r.abs_pivot[bone]
        c = self.r.box(bone, (p[0] + off[0], p[1] + off[1], p[2] + off[2]), size, inflate=inflate, decals=decals)
        c.kind = kind
        c.name = name or kind
        c.o = tuple(float(v) for v in off)
        c.sx = sx
        c.seed = int(abs(off[0]) * 7 + abs(off[1]) * 3 + abs(off[2]) * 5 + size[0] * 11) % 97
        for k, v in attrs.items():
            setattr(c, k, v)
        return c


def fk(roots, pose=None):
    """World matrices of every bone with a pose table (radians / texels, added to the rest pose)."""
    pose = pose or {}
    W = {}

    def rec(b, M):
        d = (list(pose.get(b.name, ())) + [0.0] * 6)[:6]
        R = rot_matrix(math.radians(b.rot[0]) + d[0], math.radians(b.rot[1]) + d[1], math.radians(b.rot[2]) + d[2])
        Mb = M @ _T(np.array(b.pivot) + np.array(d[3:6]))
        Mb[:3, :3] = Mb[:3, :3] @ R
        W[b.name] = Mb
        for c in b.children:
            rec(c, Mb)
    for r in roots:
        rec(r, np.eye(4))
    return W


# ------------------------------------------------------------------ proportions (texels at 2x)
HIP_Y = 9.0         # hip joints (world, standing)
HUNCH = 22.0        # chest lean from the waist (deg)
NECK_TILT = 30.0    # the neck juts forward (deg, relative to the chest)
HEAD_LOOK = -6.0    # world pitch of the head at rest (chin up a little: she looks at you)
UPPER = 6.0         # shoulder -> elbow
FORE = 5.0          # elbow -> wrist
SHOULDER = (7.5, -7.5, 0.5)   # chest-local, x mirrored
TOES_OUT = 9.0
GRIP_X, GRIP_Y, GRIP_Z = 10.5, 4.5, -9.5     # walker grips (world, centre of the foam)
SIT_DY = 5.0        # seated: the hips drop onto the cushion
BROW_KIND = 8.0     # rest tilt of the brows (inner ends up: sweet)


def arm_ik(Wc, sh, target, hint=None, w_hint=0.02, guess=(-40, 0, 0, -30), fa_y=0.0):
    """(arm x, y, z, forearm x) in degrees putting the wrist on `target` (world).  Wc = world matrix of the arm's
    parent, sh = arm pivot in the parent's frame, hint = world point the elbow should lean towards."""
    from scipy.optimize import minimize
    target = np.array(target, float)

    def chain(p):
        ax, ay, az, fx = p
        M = Wc @ _T(sh) @ _RM((ax, ay, az))
        elbow = (M @ np.array([0, UPPER, 0, 1.0]))[:3]
        M2 = M @ _T((0, UPPER, 0)) @ _RM((fx, fa_y, 0))
        wrist = (M2 @ np.array([0, FORE, 0, 1.0]))[:3]
        return elbow, wrist

    def cost(p):
        e, w = chain(p)
        c = float(np.sum((w - target) ** 2))
        if hint is not None:
            c += w_hint * float(np.sum((e - np.array(hint, float)) ** 2))
        c += 1e-5 * (p[1] ** 2) + (0.002 * (p[3] - 5) ** 2 if p[3] > 5 else 0.0)   # no hyper-extended elbow
        return c
    best = None
    for g in (guess, (guess[0] - 30, guess[1], guess[2], guess[3]), (guess[0] + 30, guess[1] + 20, guess[2], guess[3] - 30)):
        res = minimize(cost, list(g), method='Nelder-Mead', options={'xatol': 1e-5, 'fatol': 1e-10, 'maxiter': 8000})
        if best is None or res.fun < best.fun:
            best = res
    return tuple(best.x)


# ------------------------------------------------------------------ toggles (Java: ModelPart.visible)
LOOSE = tuple(f'hair_loose_{k}' for k in range(5))
# bone -> visible in the default look ('normal') at rest ('stand_walker')
TOGGLE_DEFAULT = dict({
    'walker': True, 'bun': True, 'right_slipper': True,
    'rocker': False, 'needle_right': False, 'needle_left': False, 'mate': False, 'chancleta': False,
    'yarn_right': False, 'yarn_left': False, 'dentures': False,
}, **{h: False for h in LOOSE})
VARIANT_TOGGLES = {
    'normal': {},
    'poseida': dict({'bun': False}, **{h: True for h in LOOSE}),
}
SEATED = {'walker': False, 'rocker': True}
POSE_TOGGLES = {
    'knit_sit': dict(SEATED, needle_right=True, needle_left=True),
    'stand_walker': {},
    'stand_no_walker': {'walker': False},
    'throw_chancleta': {'walker': False, 'right_slipper': False, 'chancleta': True},
    'float_rock': dict(SEATED),
    'yarn_cast': dict(SEATED, yarn_right=True, yarn_left=True),
    'scream_dentures': dict(SEATED, dentures=True),
    'sew_calm': dict(SEATED),
    'offer_mate': {'mate': True},
}


def visible_set(variant=None, pose=None):
    vis = dict(TOGGLE_DEFAULT)
    vis.update(VARIANT_TOGGLES.get(variant or 'normal', {}))
    vis.update(POSE_TOGGLES.get(pose, {}))
    show = os.environ.get('NONA_SHOW', '')
    if show:                                                            # preview helper: 'all' or 'bone,bone'
        for k in vis:
            if show == 'all' or k in show.split(','):
                vis[k] = True
    return {k for k, v in vis.items() if v}


class NonaModel(Model):
    """Exports every bone to Java; the preview JSON hides the toggle bones the current look / pose does not show."""
    visible = None

    def to_json(self):
        d = super().to_json()
        if self.visible is None:
            return d
        hide = set()
        for b in self.bones():
            if b.name in TOGGLE_DEFAULT and b.name not in self.visible:
                for sub in b.walk():
                    hide.add(sub.name)
        for bd in d['bones']:
            if bd['name'] in hide:
                bd['cubes'] = []
        return d


def _argv(flag):
    a = sys.argv
    return a[a.index(flag) + 1] if flag in a and a.index(flag) + 1 < len(a) else None


# ------------------------------------------------------------------ build
def build(variant=None, pose=None):
    B = Builder()
    bone, box = B.bone, B.box

    # ---------------- floor anchor: body, walker and rocker hang from it (float = dy, rock = xRot)
    bone('base', None, (0, 24, 0))

    # ---------------- hips: pivot at the hip joints; cardigan over the dress, pocket panels
    bone('body', 'base', (0, HIP_Y - 24, 0.5))
    box('body', (-8, -7, -5.5), (16, 7, 11), 'card', 'hips')
    box('body', (-8.5, -7, -6.5), (7, 5, 1), 'card', 'cpanel_lo', sx=-1)
    box('body', (1.5, -7, -6.5), (7, 5, 1), 'card', 'cpanel_lo', sx=1)

    # ---------------- the floral skirt: front slab with a hinged hem (it folds over the knees), back slab
    bone('skirt_front', 'body', (0, -3, 0), rot=(-5, 0, 0))
    box('skirt_front', (-9, 0, -7), (18, 8, 8), 'dress', 'skirt_f')
    bone('skirt_hem', 'skirt_front', (0, 8, 0), rot=(-2, 0, 0))
    box('skirt_hem', (-9.5, 0, -7.5), (19, 3, 9), 'dress', 'hem')
    bone('skirt_back', 'body', (0, -3, 0), rot=(5, 0, 0))
    box('skirt_back', (-9, 0, -1), (18, 11, 7), 'dress', 'skirt_b')

    # ---------------- legs: thick stockings, tartan felt slippers (the right one comes off: chancleta)
    for side, sx in (('right', -1), ('left', 1)):
        leg, shin = f'{side}_leg', f'{side}_shin'
        bone(leg, 'body', (3.5 * sx, 0, 0), rot=(0, -TOES_OUT * sx, 0))
        box(leg, (-3, 0, -3), (6, 6, 6), 'stock', 'thigh', sx=sx)
        bone(shin, leg, (0, 6, 0))
        box(shin, (-2.5, 0, -2.5), (5, 6, 5), 'stock', 'shin', sx=sx)
        if sx < 0:
            box(shin, (-2, 6, -5.5), (4, 3, 7), 'stock', 'foot', sx=sx)
            bone('right_slipper', shin, (0, 6, 0))
            sb, o = 'right_slipper', 0
        else:
            sb, o = shin, 6
        box(sb, (-3, o, -6.5), (6, 2, 9), 'felt', 'slipper', sx=sx)
        box(sb, (-3.5, o + 2, -7), (7, 1, 10), 'sole', 'sole', sx=sx)
        box(sb, (-1.5, o - 1, -7.2), (3, 2, 2), 'felt', 'pompom', sx=sx)

    # ---------------- chest: hunched from the waist, dowager's hump, open cardigan over the dress, pearls
    bone('chest', 'body', (0, -7, 0), rot=(HUNCH, 0, 0))
    box('chest', (-6.5, -9, -4.5), (13, 9, 9), 'card', 'torso')
    box('chest', (-6, -9, 2.5), (12, 6, 4), 'card', 'hump')
    box('chest', (-5, -10, 0.5), (10, 2, 5), 'card', 'hump_top')
    box('chest', (-5.5, -10, -3.5), (11, 1, 4), 'card', 'yoke')
    box('chest', (-7, -9, -5.5), (5, 9, 1), 'card', 'cpanel', sx=-1)
    box('chest', (2, -9, -5.5), (5, 9, 1), 'card', 'cpanel', sx=1)
    box('chest', (-4, -8.6, -5.65), (8, 7, 0), 'pearl', 'pearls')

    # ---------------- neck + head (the head juts forward and looks up at you)
    bone('neck', 'chest', (0, -8.5, -1), rot=(NECK_TILT, 0, 0))
    box('neck', (-2.5, -4, -2.5), (5, 5, 5), 'skin', 'neck')
    box('neck', (-2, -3, -3.5), (4, 3, 1), 'skin', 'wattle')
    bone('head', 'neck', B.world('neck', (0, -3.5, -0.5)), world=True, wrot=(HEAD_LOOK, 0, 0))
    H = 'head'
    box(H, (-8, -14, -9), (16, 14, 13), 'skin', 'skull')
    box(H, (-8, -14, -9), (16, 9, 13), 'hair', 'hair', inflate=0.6)
    box(H, (-10.6, -13, -6), (2, 5, 9), 'hair', 'wave', sx=-1)
    box(H, (8.6, -13, -6), (2, 5, 9), 'hair', 'wave', sx=1)
    box(H, (-1, -8, -10), (2, 4, 1), 'skin', 'nose')
    box(H, (-1.5, -4, -11), (3, 3, 2), 'skin', 'nose_tip')
    box(H, (-7, -2, -10), (3, 2, 1), 'skin', 'cheek', sx=-1)
    box(H, (4, -2, -10), (3, 2, 1), 'skin', 'cheek', sx=1)
    box(H, (-8, 0, -9), (2, 4, 7), 'skin', 'jowl', sx=-1)
    box(H, (6, 0, -9), (2, 4, 7), 'skin', 'jowl', sx=1)
    box(H, (-9, -8, -2), (1, 5, 3), 'skin', 'ear', sx=-1)
    box(H, (8, -8, -2), (1, 5, 3), 'skin', 'ear', sx=1)
    box(H, (-9.4, -3.4, -1.2), (1, 1, 1), 'pearl', 'earring', sx=-1)
    box(H, (8.4, -3.4, -1.2), (1, 1, 1), 'pearl', 'earring', sx=1)
    box(H, (-9.8, -8.5, 0.8), (1, 4, 1), 'aid', 'aid', sx=-1)

    # brows (pencilled, expressive)
    bone('right_brow', H, (-4.5, -9.5, -9.2), rot=(0, 0, -BROW_KIND))
    box('right_brow', (-2.5, -0.5, -0.4), (5, 1, 1), 'brow', 'brow', sx=-1)
    bone('left_brow', H, (4.5, -9.5, -9.2), rot=(0, 0, BROW_KIND))
    box('left_brow', (-2.5, -0.5, -0.4), (5, 1, 1), 'brow', 'brow', sx=1)

    # jaw: chin + lower lip between the jowls; the hidden throat box and the cheek flaps travel with it
    JO = (0, 0, -1)
    bone('jaw', H, JO)
    box('jaw', (-6, 0, -8), (12, 3, 8), 'skin', 'jaw', ho=JO)
    box('jaw', (-3.5, 2, -8.8), (7, 2, 1), 'skin', 'chin', ho=JO)
    box('jaw', (-5, -8, -6), (10, 8, 5), 'maw', 'maw', ho=JO)
    box('jaw', (-5.9, -8, -7.5), (0, 8, 5), 'maw', 'flap', sx=-1, ho=JO)
    box('jaw', (5.9, -8, -7.5), (0, 8, 5), 'maw', 'flap', sx=1, ho=JO)

    # bun with a hairnet on the back of the crown (two crossed cubes = an octagon, a domed top)
    bone('bun', H, (0, -13.5, 3.5), rot=(-40, 0, 0))
    box('bun', (-4, -5, -3), (8, 5, 6), 'hair', 'bun', part='A')
    box('bun', (-3, -5, -4), (6, 5, 8), 'hair', 'bun', part='B')
    box('bun', (-3, -6, -3), (6, 1, 6), 'hair', 'bun_top')

    # glasses: two thick round tortoiseshell lenses (7 x 7 rings), the bridge, temples, the beaded chain
    bone('glasses', H, (0, -5.5, -9.9))
    for sx in (-1, 1):
        x0 = -8.3 if sx < 0 else 1.3
        box('glasses', (x0, -3.5, -0.5), (7, 7, 1), 'lens', 'lens', sx=sx, decals={'eyes:front': make_lens_glow(sx)})
        box('glasses', ((-9.3 if sx < 0 else 8.3), -2.5, -0.3), (1, 1, 9), 'frame', 'temple', sx=sx)
        box('glasses', ((-9.6 if sx < 0 else 9.6), -2.0, 3.0), (0, 8, 6), 'pearl', 'chain', sx=sx)
    box('glasses', (-1.5, -1.5, -1.0), (3, 1, 1), 'frame', 'bridge')

    # floating dentures (toggle) in front of the mouth; the lower plate clacks on its own bone
    bone('dentures', H, (0, 2.0, -16.0))
    box('dentures', (-3.5, -2.5, -2), (7, 2, 4), 'teeth', 'denture_up')
    bone('dentures_lower', 'dentures', (0, 0, 1.5))
    box('dentures_lower', (-3.5, 0.0, -3.5), (7, 2, 4), 'teeth', 'denture_lo')

    # possessed: the bun undone into white strands drifting up as if underwater (toggles)
    loose = [((0, -13.5, 3.5), (-30, 0, 0)), ((-6, -13, 0), (-15, 0, -40)), ((6, -13, 0), (-15, 0, 40)),
             ((-3, -11, 5), (-70, 0, -15)), ((3, -11, 5), (-70, 0, 15))]
    for k, (p, r) in enumerate(loose):
        bn = f'hair_loose_{k}'
        bone(bn, H, p, rot=r)
        ln = 16 if k else 18
        box(bn, (-2, -ln, 0), (4, ln, 0), 'hair', 'strand', seed=k * 1.7)
        box(bn, (0, -ln + 2, -2), (0, ln - 2, 4), 'hair', 'strand', seed=k * 2.3 + 1)

    # ---------------- arms: round shoulders, hands on the walker grips (solved)
    for side, sx in (('right', -1), ('left', 1)):
        arm, fa, hand = f'{side}_arm', f'{side}_forearm', f'{side}_hand'
        sh = (SHOULDER[0] * sx, SHOULDER[1], SHOULDER[2])
        target = (GRIP_X * sx, GRIP_Y - 2.4, GRIP_Z + 0.6)
        ax, ay, az, fx = arm_ik(B.W['chest'], sh, target, hint=(12 * sx, -2, 0), guess=(-40, 0, 0, -30))
        bone(arm, 'chest', sh, rot=(ax, ay, az))
        box(arm, (-2.5, -1.5, -2.5), (5, 8, 5), 'card', 'sleeve', sx=sx)
        bone(fa, arm, (0, UPPER, 0), rot=(fx, 0, 0))
        box(fa, (-2, 0, -2), (4, 4, 4), 'card', 'sleeve_lo', sx=sx)
        box(fa, (-2, 3, -2), (4, 2, 4), 'card', 'cuff', sx=sx, inflate=0.3)
        bone(hand, fa, B.world(fa, (0, FORE, 0)), world=True, wrot=(-10, 0, 0))
        box(hand, (-2, 0, -1.5), (4, 3, 3), 'skin', 'palm', sx=sx)
        box(hand, (-2, 3, -1.5), (4, 2, 3), 'skin', 'fingers', sx=sx, inflate=-0.1, ring=(sx > 0))
        box(hand, ((-2.6 if sx < 0 else 1.6), 0.5, -2.2), (1, 3, 1), 'skin', 'thumb', sx=sx)
        if sx > 0:
            box(fa, (-1.2, 2.6, -2.45), (3, 2, 0), 'tissue', 'tissue')    # tissue tucked in the cuff

    # held props (toggles)
    bone('mate', 'right_hand', (0, 2.5, -2.5))
    box('mate', (-2, -3.5, -2), (4, 4, 4), 'gourd', 'gourd')
    box('mate', (-2, -4.5, -2), (4, 1, 4), 'metal', 'virola', inflate=0.15)
    box('mate', (0.3, -8.5, -0.5), (1, 5, 1), 'metal', 'bombilla')
    bone('chancleta', 'right_hand', (0, 2.5, 0))
    box('chancleta', (-3, -1, -4.5), (6, 2, 9), 'felt', 'chancleta')
    box('chancleta', (-3.5, 1, -5), (7, 1, 10), 'sole', 'sole')
    bone('needle_right', 'right_hand', (0, 2, 0))
    box('needle_right', (-0.5, -0.5, -10), (1, 1, 12), 'metal', 'needle')
    bone('needle_left', 'left_hand', (0, 2, 0))
    box('needle_left', (-0.5, -0.5, -10), (1, 1, 12), 'metal', 'needle')
    box('needle_left', (-3, 0.5, -9), (6, 8, 0), 'wool', 'knit')
    bone('yarn_right', 'right_hand', (0, 4, 0))
    box('yarn_right', (-1, 0, -1), (2, 30, 2), 'wool', 'yarn')
    bone('yarn_left', 'left_hand', (0, 4, 0))
    box('yarn_left', (-1, 0, -1), (2, 30, 2), 'wool', 'yarn')

    # red wool ball in the cardigan pocket (her right hip) with a loose tail
    bone('yarn_ball', 'body', (-5, -5.5, -7.5))
    box('yarn_ball', (-2, -2, -2), (4, 4, 4), 'wool', 'ball')
    box('yarn_ball', (-1, 2, -1.6), (3, 6, 0), 'wool', 'tail')

    # ---------------- walker (andador): aluminium U frame, front wheels, cut tennis balls on the back legs
    bone('walker', 'base', (0, 0, 0))
    gy = GRIP_Y - 24
    for sx in (-1, 1):
        x = GRIP_X * sx
        box('walker', (x - 0.5, gy - 0.5, -17.5), (1, -gy - 4.5, 1), 'metal', 'tube')     # front leg (to the wheel fork)
        box('walker', (x - 0.5, gy - 0.5, -3.5), (1, -gy - 2.5, 1), 'metal', 'tube')      # back leg (to the tennis ball)
        box('walker', (x - 0.5, gy - 0.5, -17.5), (1, 1, 14), 'metal', 'tube')             # side rail
        box('walker', (x - 1, gy - 1, GRIP_Z - 2.5), (2, 2, 5), 'foam', 'grip')            # foam grip
        box('walker', (x - 1.5, -3, -4.5), (3, 3, 3), 'tennis', 'tennis')
    box('walker', (-GRIP_X, gy - 0.5, -17.5), (int(2 * GRIP_X), 1, 1), 'metal', 'tube')    # front top bar
    box('walker', (-GRIP_X, gy + 8, -17.5), (int(2 * GRIP_X), 1, 1), 'metal', 'tube')      # front low bar
    box('walker', (GRIP_X - 0.5, -5, -19.5), (1, 5, 5), 'foam', 'wheel')
    box('walker', (-5, gy + 0.5, -18.6), (9, 7, 2), 'bag', 'bag')
    box('walker', (-5, gy - 4.5, -17.9), (9, 5, 0), 'knitting', 'knitting')
    bone('walker_wheel', 'walker', (-GRIP_X, -2.5, -17.0))
    box('walker_wheel', (-0.5, -2.5, -2.5), (1, 5, 5), 'foam', 'wheel')

    # ---------------- rocking chair (light oak, crocheted cushion, spindle back, doily over the crest)
    bone('rocker', 'base', (0, 0, 0))
    seat = HIP_Y - 24 + SIT_DY + 3            # cushion top (local y): the thighs rest on it
    box('rocker', (-9.5, seat, -8), (19, 2, 15), 'wool', 'cushion')
    box('rocker', (-10.5, seat + 2, -9), (21, 2, 17), 'oak', 'seat')
    for sx in (-1, 1):
        x0 = -10.5 if sx < 0 else 8.5
        box('rocker', (x0, seat + 4, -8.5), (2, int(-seat - 7), 2), 'oak', 'leg')
        box('rocker', (x0, seat + 4, 5), (2, int(-seat - 7), 2), 'oak', 'leg')
        box('rocker', (x0, -3, -9), (2, 3, 17), 'oak', 'runner')
        box('rocker', (x0, -4, -14), (2, 2, 5), 'oak', 'runner')
        box('rocker', (x0, -5, 8), (2, 2, 6), 'oak', 'runner')
        box('rocker', (x0 - 0.5 * sx, seat - 9, -9), (2, 2, 15), 'oak', 'armrest')
        box('rocker', (x0, seat - 7, -8.5), (2, 7, 2), 'oak', 'post')
    bone('rocker_back', 'rocker', (0, seat + 2, 7), rot=(-12, 0, 0))
    for sx in (-1, 1):
        x0 = -10.5 if sx < 0 else 8.5
        box('rocker_back', (x0, -34, -1), (2, 34, 2), 'oak', 'stile')
    box('rocker_back', (-11.5, -38, -1.5), (23, 5, 3), 'oak', 'crest')
    box('rocker_back', (-8.5, -33, 0), (17, 29, 0), 'oak', 'spindles')
    box('rocker_back', (-6, -36, -1.7), (12, 8, 0), 'oak', 'doily')

    m = NonaModel('nona', 256, 256, B.r.roots)
    m.scale = 0.5
    if pose is None and os.path.basename(sys.argv[0]) == 'preview.py':
        pose = _argv('--pose')
    if variant is None and os.path.basename(sys.argv[0]) == 'preview.py':
        variant = _argv('--variant')
    m.visible = visible_set(variant, pose)
    m.builder = B
    return m


DEFAULT_MAT = make_mat('normal')
VARIANT_MATS = {'normal': DEFAULT_MAT, 'poseida': make_mat('poseida')}
FOCUS = 'head'


# ------------------------------------------------------------------ poses (solved against the rest rig)
def _bones(m):
    return {b.name: b for b in m.bones()}


def pose_arm(m, pose, side, target, hint=None, hand_wrot=None, w_hint=0.02, guess=(-40, 0, 0, -30)):
    """Adds <side>_arm / _forearm (/ _hand) deltas to `pose` so the wrist lands on `target` (world, posed body)."""
    bn = _bones(m)
    arm, fa, hand = bn[f'{side}_arm'], bn[f'{side}_forearm'], bn[f'{side}_hand']
    W = fk(m.roots, pose)
    Wc = W[arm.parent.name]
    ax, ay, az, fx = arm_ik(Wc, np.array(arm.pivot), target, hint, w_hint, guess, fa_y=fa.rot[1])
    r = math.radians
    pose[arm.name] = (r(ax - arm.rot[0]), r(ay - arm.rot[1]), r(az - arm.rot[2]), 0, 0, 0)
    pose[fa.name] = (r(fx - fa.rot[0]), 0, 0, 0, 0, 0)
    if hand_wrot is not None:
        W = fk(m.roots, pose)
        Wf = W[fa.name]
        loc = _euler(Wf[:3, :3].T @ _R(hand_wrot))
        pose[hand.name] = (r(loc[0] - hand.rot[0]), r(loc[1] - hand.rot[1]), r(loc[2] - hand.rot[2]), 0, 0, 0)
    return pose


def _sit(extra=None):
    """Seated in the rocker: hips drop onto the cushion, thighs forward, shins hang, the skirt drapes the lap."""
    p = {
        'body': (0, 0, 0, 0, SIT_DY, 0),
        'right_leg': (-1.5708, 0, 0, 0, 0, 0), 'left_leg': (-1.5708, 0, 0, 0, 0, 0),
        'right_shin': (1.5708, 0, 0, 0, 0, 0), 'left_shin': (1.5708, 0, 0, 0, 0, 0),
        'skirt_front': (-1.48, 0, 0, 0, 2.5, 0.5), 'skirt_hem': (1.5, 0, 0, 0, 0, 0),
        'skirt_back': (-1.2, 0, 0, 0, 3.0, 1.0),
    }
    if extra:
        p.update(extra)
    return p


def make_poses():
    m = build(pose='__none__')
    P = {}
    P['stand_walker'] = {'head': (0, 0, 0.1, 0, 0, 0)}
    P['stand_no_walker'] = {'chest': (-0.22, 0, 0, 0, 0, 0), 'neck': (-0.1, 0, 0, 0, 0, 0)}
    pose_arm(m, P['stand_no_walker'], 'right', (-8.5, 3.5, 1.0), hint=(-14, -1, 2))
    pose_arm(m, P['stand_no_walker'], 'left', (8.5, 3.5, 1.0), hint=(14, -1, 2))
    P['knit_sit'] = _sit()
    pose_arm(m, P['knit_sit'], 'right', (-3, 0, -10), hint=(-11, 2, -4))
    pose_arm(m, P['knit_sit'], 'left', (3, 0, -10), hint=(11, 2, -4))
    return P


POSES = make_poses()

ANIM_NOTES = """WIP"""
