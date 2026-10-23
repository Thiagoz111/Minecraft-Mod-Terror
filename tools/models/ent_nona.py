"""Nona Pocha (Nelida 'Pocha' Bertolotti, 73) -- the grandmother of the Casa Morales (DEAD LINE, case 'casa').

Host #4 and the twist of the case: the girl possessed in 1961, who calls the demon back into herself to free her
granddaughter.  Authored at 2x texel density (model.scale = 0.5).  +Y down, ground y = 24, faces -Z, right_* on -X.
ANIM_NOTES (end of the file) is the animation contract; POSES / PROP_ROT are generated from POSE_TARGETS with
`python3 tools/models/ent_nona.py --write-poses [pose,pose]`.

Design
------
Read in one glance: a tiny, hunched, adorable Argentine nona -- and the same silhouette is what floats in the
rocking chair at the end.  Lovable by day (huge magnified eyes behind coke-bottle lenses, rouge, pearls, a red wool
ball in her pocket, tennis balls on the walker, a mate); terrifying possessed (cracked lenses, one glassy blue eye,
one black hole weeping black, jaw hanging to the chest with the dentures floating out, white hair drifting).

Silhouette: 1.5 blocks to the top of the bun.  A pear: narrow sloped shoulders, a dowager's hump, wide hips under a
mid-calf floral skirt, short legs in thick stockings and tartan felt slippers.  The torso leans 22 deg forward from
the waist, the neck juts forward another 30 deg, and the head tips back up so she looks at you.  The head is big
(16 x 18 face, the family style of Marta and Jorge) under a cloud of a lavender-grey perm: a curly shell with a rounded
crown, a fringe roll of fat curls over the forehead, rolled puffs over the ears that stick out past the glasses
temples, and a stepped dome of a bun under a hairnet seated on the back of the crown.  The round glasses are the
icon: two 10 x 10 round tortoiseshell discs, two texels deep, wider than her face.
Accessories are bones of the model so they move and float with her: the aluminium walker (front wheels -- one of them
squeaks and is its own bone -- cut tennis balls on the back legs, a soft granny-square bag hung by two cord loops on
the front bar with the knitting poking out) and the light-oak rocking chair (runners curving up at both ends in two
steps, four short legs -- the arm posts and the back stiles run down to the runners --, a cushion crocheted in cream
with red popcorn stitches, spindle back, a lace doily on the crest).

Face (16 x 18 hand-placed grid FACE; rows 0-13 on the skull, 14-17 on the jaw / jowls / chin):
* curls hang over a strip of powdered forehead; pencilled brows on their own bones right on top of the frames;
* the lenses carry the eyes (LENS_EYE): big magnified brown irises with a catchlight (kept top-left on both eyes)
  under an arched lash line that droops at the outer corner, the smile crease of the lower lid, a glare on the glass.
  The 'eyes' layer lights the glass, so at night the lenses glow white with two little dark eyes inside;
* a rosy bulb nose between the lens bottoms, rouge apples (cheek cubes), flat value bands on the cheeks (no dither),
  a small closed smile: one clean dark line with the corners tucked up, a coral lower lip and a light chin under it,
  a mole by her left mouth corner, jowls and a soft double chin;
* a hinged jaw with a hidden throat box: it can drop all the way to the chest (dislocated) while side flaps of
  skin stretch to the skull; toothless gums inside (her teeth are the dentures).

Looks (VARIANT_MATS): 'normal' and 'poseida' (index 1).  The possessed texture keeps the clothes but drains the skin
to a bloodless grey-lilac pulled 1-2 steps darker (sunken sockets, temples and cheek hollows), so the bleached white
hair and the glowing lens stay the only light values of the head.  The glasses break: behind the right lens (the
viewer's left) a lidless glassy blue doll's eye under a spider-web break (three dark radial cracks and one ring from
an impact high on the outer side) -- the glass still glows white, cracked; the left lens is blown out to a few shards
on a black hole ringed by a faint ember rim with a 2 x 2 ember deep inside, and ONE black tear runs from it down the
cheek, the apple, the jaw and the neck (a rhyme with Ofelia's broken eye).  A single forked vein climbs her right
temple, the mouth is a smeared black-red line, the nails are long and dark (claw planes, transparent in 'normal').
Toggle bones of the possessed look: hair_loose_0..4 (shown) and bun (hidden); the floating dentures belong to the
'scream_dentures' pose.
"""
import math
import os
import sys

import numpy as np

from mcmodel import Model, hash3, face_light, pick, rot_matrix, fbm
from rig import Rig
from paint import hx, mix, scale


def pal(*h):
    return [hx(c) for c in h]


def A(c, a=255):
    return (c[0], c[1], c[2], int(a))


# ------------------------------------------------------------------ palettes (dark -> light, hue shifted)
SKIN = pal('#40232a', '#5e3437', '#7e4a49', '#9d625d', '#b97c73', '#cf978b', '#e0b0a3', '#ecc6ba', '#f5dbd1',
           '#fbede7')


def _deathly(c):
    """Possessed skin: the ramp drained to a cold grey-lilac and pulled down a step and a half, so the white hair and
    the glowing lens stay the only light values of the head."""
    lum = 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]
    t = (lum * 0.80, lum * 0.78, lum * 0.94, 255)
    return mix(c, t, 0.9)


SKIN_P = [_deathly(mix(SKIN[max(0, i - 2)], SKIN[max(0, i - 1)], 0.5)) for i in range(len(SKIN))]
ROUGE = pal('#b5525e', '#cf6e78', '#e4949a')
LIP = pal('#6e2434', '#a03c4c', '#c4545e', '#dc747a', '#eea0a0')
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
SOLE = pal('#120c0a', '#241812', '#3a2a1e', '#56402c', '#725a40', '#8e7456', '#a88e6c')
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
GOURD = pal('#3e2012', '#5c321c', '#7c4626', '#9a5c32', '#b87a46', '#d39a5e', '#ecc08a')
YERBA = pal('#2e3a12', '#4a5a1c', '#6a7c2a', '#8ca040')
TEETH = pal('#7a7262', '#b0a890', '#d8d0b8', '#efe9d8', '#fbf8ee')
GUM = pal('#5a1424', '#86263a', '#b04456', '#d06a7a', '#e894a0')
MOUTH = pal('#040102', '#100408', '#20080e', '#360e18', '#521a26', '#6e2a36')
TONGUE = pal('#5a1a26', '#7e2a38', '#a04252', '#bc5e6c')
AID = pal('#6a5040', '#8e6e58', '#b08e74', '#cdac90')
TISSUE = pal('#8e8b98', '#aeabb8', '#c8c5d0', '#dddbe2')
SQUARES = [mix(hx(c), hx('#7c7484'), 0.5) for c in ('#e2a83a', '#2f8f8a', '#8a4a9a', '#d8603a', '#e6dcc4')]
SQ_DARK = hx('#3a3440')

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
# 2-13, jowls cols 0-1 / 14-15, chin cube cols 5-10 rows 16.5-18.5).  Front-view layout, top to bottom:
#   rows 0-1  the curl fringe (its own cube) hangs over row 1; a strip of powdered forehead shows between the curls
#   row 2     pencilled brows (own bones, cols 0-4 / 11-15) with skin between them
#   rows 3-12 the round 11 x 11 lenses (centres x -6 / +6, y -6.5): only the brow bridge (row 3 cols 4-11), the strip
#             by the nose bridge (cols 6-9) and the philtrum row 12 (cols 4-11) show between them
#   row 12    under the nose: a soft shadow; the two mouth corners tuck UP here (cols 4 / 11) = the smile
#   row 13    the mouth: one clean dark line (cols 5-10); the rouge apples (cheek cubes) cover cols 0-2 / 13-15
#   row 14    (jaw) the coral lower lip (cols 6-9); marionette creases; the mole by her left mouth corner
#   row 15    a light chin highlight under the lip; rows 16-17 chin and its shadow
# Cheeks are flat value bands (no dither): 7 upper, 6 middle, 5 jowl.  Under the lenses the sockets are painted
# anyway (seen in profile and through the shattered lens of the possessed look).
#   digits skin ramp  p powder  s nose shadow  M mouth line  L lower lip  K crease  c chin light  m mole  n mole hair
#   e/O lid / socket  H hair
GX0, GY0 = -8.0, -14.0
FACE = [
    # 0123456789012345
    "HHHHHHHHHHHHHHHH",   # r0  y-14  under the curl fringe
    "7888999pp9998887",   # r1  y-13  powdered forehead strip (the curls hang over it)
    "6778889pp9888776",   # r2  y-12  brows (own bones) over cols 0-4 / 11-15
    "6677788998877766",   # r3  y-11  lens tops; brow bridge cols 4-11
    "5566777887776655",   # r4  y-10
    "55eOOe7887eOOe55",   # r5  y-9   sockets (behind the glass)
    "5eOOOOe88eOOOOe5",   # r6  y-8
    "5eOOOOe88eOOOOe5",   # r7  y-7
    "55eOOe7887eOOe55",   # r8  y-6
    "5566e778877e6655",   # r9  y-5   nose tip in front (cols 6.5-9.5, rows 9-11)
    "556677677677665 ",   # r10 y-4
    "5566776ss6776655",   # r11 y-3
    "77777M6ss6M77777",   # r12 y-2   under the nose; the mouth corners tucked up (M) = the smile
    "777777MMMM77m777",   # r13 y-1   the mouth: one short dark line; the mole by her left corner
    "555666lLLl666555",   # r14 y0    (jaw) the coral lower lip
    "5556666cc6666555",   # r15 y1    chin highlight under the lip
    "5566666776666655",   # r16 y2    chin
    "4555555665555554",   # r17 y3    under the chin
]
FACE[10] = FACE[10].replace(' ', '5')
assert all(len(r) == 16 for r in FACE), [len(r) for r in FACE]

# possessed overrides (same grid, '.' = keep the normal char re-lit with the possessed ramp).  Her left eye (the
# viewer's right) is a black hole behind the blown-out lens (V void, X the faint ember rim); ONE black tear runs
# from its lower lid down the cheek, the apple, the jaw and the neck (T, t its wet edge); a forked vein climbs from
# the bridge of her right lens to the hairline (v); the mouth line is smeared black-red (W); the sockets and the
# hollows under the cheekbones sink 1-2 ramp steps (digits here are absolute possessed-ramp indices).
FACE_P = [
    # 0123456789012345
    "................",   # r0
    "..v.............",   # r1   vein: hairline ...
    "...v............",   # r2
    "....v...........",   # r3   ... down to the bridge of the right lens
    "..33.......XXX..",   # r4
    ".3223.....XVVVX.",   # r5   the hole: black void ringed by a faint ember rim
    "32112....XVVVVVX",   # r6
    "32112....XVVVVVX",   # r7
    ".3223....XVVVVVX",   # r8
    "..33......XVVVX.",   # r9
    ".........3.XTX..",   # r10  the tear leaves the lower lid
    "....3...3...T...",   # r11  hollows beside the nose
    "4433.W....W..T44",   # r12  sunken cheeks, smeared corners
    "......WWWW...T..",   # r13
    "33..........T.33",   # r14
    "3...........T..3",   # r15
    "............t...",   # r16
    "............t...",   # r17
]
assert all(len(r) == 16 for r in FACE_P), [len(r) for r in FACE_P]

# ---- B2 'rota' look (the hunt, Act 5): the glasses are gone and the face is bare.  Milky cataract eyes (W w, a ghost
# of the iris g) in raw red lids (R) sunk in near-black sockets (D d); blood wells under the lower lids and runs down
# both cheeks (B b, fresh r), streams from both nostrils over the lip and out of the gaping mouth (M) down the chin;
# dark veins climb the forehead (V).  '.' = the normal char re-lit with the corpse ramp SKIN_R.
FACE_R = [
    # 0123456789012345
    "................",   # r0
    "...V........V...",   # r1
    "....V......V....",   # r2
    "..ddd......ddd..",   # r3   the brow ridge overhangs dark sockets
    ".dRRRRd...dddd..",   # r4   raw upper lid (her right eye sits higher: the face is no longer level)
    "DdwwwdD..dRRRRd.",   # r5   milky cataracts, the lid's shadow over their top
    "DwWgWwD..DdwwwdD",   # r6   the drowned ghost of the iris (g)
    "DwWgWwD..DwWgWwD",   # r7
    "dRwwwRd..DwWgWwD",   # r8   raw lower lids
    ".dB.RBd..dRwwwRd",   # r9   blood wells under the eyes ...
    "..B......dB.RBd.",   # r10  ... and runs down the cheeks in thin lines
    "..B.......B.....",   # r11
    "..b....BB.b.....",   # r12  the nostrils bleed over the lip
    "..b..MMMMMM.....",   # r13  the mouth hangs open, black
    ".....bMMMMb.....",   # r14  (jaw) the lower lip, black inside, blood at the corners
    "......B...B.....",   # r15
    "......b...B.....",   # r16
    "..........b.....",   # r17
]
assert all(len(r) == 16 for r in FACE_R), [len(r) for r in FACE_R]
SKIN_R = pal('#14181e', '#1d232b', '#28303a', '#343e4a', '#424d59', '#525e69', '#646f79', '#78828a', '#8c959b',
             '#a2a9ad')
GOWN = pal('#26221e', '#38332d', '#4c463e', '#625a50', '#797064', '#90867a', '#a69c8e', '#bab1a2', '#cbc3b5')
GRIME = hx('#3a3326')
BLOOD = pal('#1e0204', '#3a0508', '#5a090d', '#7c0e13', '#a1161b', '#c42a2a')
BLOOD_DRY = pal('#2a1410', '#3e1d16', '#54281d')
CATARACT = {'W': hx('#dfe2dc'), 'w': hx('#b9bfba'), 'g': hx('#8b9799')}
VEIN_R = hx('#241c36')
ROT_TEETH = pal('#4a3f2a', '#6e6142', '#958763', '#b6a983', '#cfc4a0')


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
    if P:
        pos = {'V': VOID[0], 'X': hx('#3c0d0a'), 'T': TEAR[1], 't': TEAR[2], 'v': VEIN,
               'W': mix(LIP_P[1], TEAR[1], 0.45), 'M': MOUTH[1], 'L': LIP_P[2], 'p': S[7], 'c': S[6],
               's': S[3], 'K': S[3], 'm': MOLE[0], 'n': MOLE[0]}
        if ch in pos:
            return pos[ch]
    return {
        'H': (HAIR_P if P else HAIR)[3],
        'p': mix(S[9], hx('#ffffff'), 0.35), 's': S[5], 'K': S[5], 'c': S[8],
        'M': mix(LIP[0], MOUTH[2], 0.35), 'L': LIP[3], 'l': LIP[2],
        'm': MOLE[1], 'n': MOLE[0], 'e': S[4], 'O': S[3],
    }.get(ch, S[6])


def _near_poly(a, b, pts):
    """Distance from (a, b) to a polyline [(a0, b0), (a1, b1), ...]."""
    best = 99.0
    for (a0, b0), (a1, b1) in zip(pts, pts[1:]):
        da, db = a1 - a0, b1 - b0
        L2 = da * da + db * db
        t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((a - a0) * da + (b - b0) * db) / L2))
        best = min(best, math.hypot(a - (a0 + t * da), b - (b0 + t * db)))
    return best


# the possessed temple vein on the west (her right) side of the skull, in (z, y) head-local: up from the cheekbone,
# forking under the hairline
VEIN_TEMPLE = [(-6.5, -4.0), (-6.0, -6.5), (-5.0, -8.5), (-5.5, -11.0)]
VEIN_TEMPLE_B = [(-5.0, -8.5), (-3.0, -10.5)]


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
        cell = (fl(x - GX0), fl(y - GY0))
        if P:
            if n == 'skull' and cell in EMBER_PX:
                return A(mix(EMBER_PX[cell], hx('#000000'), 0.25))
            ch = face_char(x, y, FACE_P)
            if ch and ch != '.':
                return A(face_rgba(ch, True))
        if n == 'cheek':
            # the rouge apple: a powdered highlight on its top-inner corner, rosy across, a soft lower edge.
            # Possessed: a sunken grey hollow.
            i, j = fl(lx), fl(ly)
            if P:
                return A(S[5] if j == 0 else S[4])
            if j == 0 and i == (2 if ctx.cube.sx < 0 else 0):
                return A(mix(S[8], hx('#ffffff'), 0.2))
            return A(mix(S[7] if j == 0 else S[6], ROUGE[1], 0.45 if j == 0 else 0.35))
        if n == 'chin':
            i, j = fl(lx), fl(ly)
            if P:
                ch = face_char(x, y, FACE_P)
                if ch and ch != '.':
                    return A(face_rgba(ch, True))
            return A(S[7] if j == 0 and 1 <= i <= w - 2 else S[6] if j == 0 else S[5])
        ch = face_char(x, y, FACE)
        if ch:
            return A(face_rgba(ch, P))
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
            if P:
                # sunken temples, and ONE forked vein climbing her right temple (the side of the blue eye)
                if -11.5 < y < -5.5 and -7.5 < z < -2.5:
                    vv -= 0.1
                if f == 'west' and min(_near_poly(z, y, VEIN_TEMPLE), _near_poly(z, y, VEIN_TEMPLE_B)) < 0.55:
                    return A(VEIN)
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
            if P and fl(lx) == 4 and ly > 0.5:
                return A(TEAR[1] if ly < h - 1 else TEAR[2])            # the black tear drips on down the neck
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
    if n == 'claws':
        # long dark nails past the fingertips -- only in the possessed texture (transparent in 'normal')
        if not P:
            return None
        i, j = fl(lx), fl(ly)
        if i not in (0, 1, 3):
            return None
        return A((hx('#6a6470'), hx('#3a3542'), hx('#141218'))[min(j, 2)])
    if n in ('palm', 'finger', 'thumb'):
        vv = 0.6 + face_light(ctx) * 1.1
        if n == 'finger' and f in SIDE:
            if fl(ly) == 1:
                vv -= 0.07                                              # knuckle crease
            if fl(ly) == h - 1 and f == 'back':
                return A(mix(S[8], hx('#ffffff'), 0.2) if not P else hx('#4a4552'))   # fingernail
        if n == 'palm' and f in ('front', 'back') and fl(lx) == 1 and fl(ly) == 1 and not P:
            return A(mix(S[5], hx('#8a5a3a'), 0.4))                     # an age spot
        if n == 'finger' and getattr(ctx.cube, 'ring', False) and fl(ly) == 0 and f in SIDE:
            return A(GOLD[4] if f in ('front', 'west', 'top') else GOLD[2])   # wedding ring
        if P and n == 'finger' and fl(ly) == h - 1:
            vv -= 0.12                                                  # dark fingertips
        return A(pick(S, vv))
    return A(pick(S, v))


# Perm curls: jittered cellular clumps (~3.6 texels) -- each a little dome lit from the top-left with a dark crevice
# between neighbours.  Organic, high contrast, survives a thumbnail.  -> ramp index offset
CURL_S = 3.6


def curl_idx(u, v, S=CURL_S, seed=0):
    gi, gj = fl(u / S), fl(v / S)
    best = [(99.0, 0.0, 0.0), (99.0, 0.0, 0.0)]
    for di in (-1, 0, 1):
        for dj in (-1, 0, 1):
            ci, cj = gi + di, gj + dj
            cx = (ci + 0.2 + 0.6 * h2(ci, cj, 91 + seed)) * S
            cy = (cj + 0.2 + 0.6 * h2(ci, cj, 92 + seed)) * S
            dd = math.hypot(u - cx, v - cy)
            if dd < best[0][0]:
                best = [(dd, cx, cy), best[0]]
            elif dd < best[1][0]:
                best[1] = (dd, cx, cy)
    d1, cx, cy = best[0]
    if best[1][0] - d1 < 0.75:
        return -3                                                   # the crevice between curls
    t = ((u - cx) + (v - cy)) / S                                  # -: toward the top-left
    return 2 if t < -0.45 else (1 if t < 0.05 else (0 if t < 0.4 else -1))


def hpick(Hh, i):
    return Hh[max(2, min(len(Hh) - 1, i))]


def _tress_rows(ln, wd, bend, sd, wide, curve):
    """Per row: list of (left, width) runs.  Plane A (wide): a main tress (4 -> 3 -> 2 -> 1 texels) along one gentle S
    (or one soft arc), its tip drifting to one side (bend), plus a thinner tress that leaves the root with it and
    peels away toward the tip -- a clump of hair splitting.  Plane B: one thin companion lock (3 -> 2 -> 1).
    At most one texel of sideways step per row, so the edges stay clean."""
    runs_main, runs_sec = [], []
    prev = [None, None]
    for row in range(ln - 1, -1, -1):              # root first
        s = 1.0 - (row + 0.5) / ln                  # 0 at the root (the bone pivot), 1 at the tip
        if curve == 'C':
            wave = 2.6 * math.sin(math.pi * min(1.0, s * 1.15))                      # one round hook
        else:
            wave = 1.9 * math.sin(2 * math.pi * s + sd * 4.0) * min(1.0, s * 3.0)  # one gentle S
        cen = wd / 2.0 + wave + bend * 2.6 * s * s
        for k in (0, 1):
            if k == 1 and not wide:
                continue
            if k == 0:
                if wide:
                    w = 4 if s < 0.25 else (3 if s < 0.6 else (2 if s < 0.88 else 1))
                else:
                    w = 0 if s > 0.9 else (3 if s < 0.25 else (2 if s < 0.75 else 1))
                c = cen
            else:
                w = 0 if s > 0.74 else (2 if s < 0.62 else 1)
                c = cen - bend * (3.0 + 4.0 * s * s) - (1 if bend == 0 else 0) * 3.0
            out = runs_main if k == 0 else runs_sec
            if w == 0:
                out.append(None)
                continue
            left = int(round(c - w / 2.0))
            if prev[k] is not None:
                left = max(prev[k] - 1, min(prev[k] + 1 + (1 if w < 3 else 0), left))
            prev[k] = left
            out.append((left, w))
    rows = []
    for i in range(ln):
        r = []
        if runs_main[i]:
            r.append(runs_main[i])
        if wide and runs_sec[i]:
            r.append(runs_sec[i])
        rows.append(r)
    return rows[::-1]


_TRESS = {}


def strand_lock(ctx):
    """Possessed loose hair drifting as if under water: plane A one wide tress forking into two locks, plane B a
    thinner companion lock; grey at the root, white body, a shadowed edge and one wet highlight line, clean
    1-texel tips (no stray pixels).  -> rgba or None"""
    c = ctx.cube
    ln = c.size[1]
    wd = max(c.size[0], c.size[2])
    lx, ly, lz = local(ctx)
    u = lx if c.size[0] > 0 else lz
    i = fl(u)
    row = min(ln - 1, fl(ly))
    wide = c.size[0] > 0
    key = (ln, wd, c.bend, round(c.seed, 3), wide, c.curve)
    if key not in _TRESS:
        _TRESS[key] = _tress_rows(ln, wd, c.bend, c.seed, wide, c.curve)
    s = 1.0 - (row + 0.5) / ln
    H = HAIR_P
    for left, w in _TRESS[key][row]:
        p = i - left
        if not (0 <= p < w):
            continue
        if s < 0.12:
            return A(H[3] if p == 0 else H[4])                       # grey roots
        if w == 1:
            return A(H[6])                                             # the clean tip
        if p == 0:
            return A(H[4] if w >= 4 else H[5])                         # shadowed edge
        if p == (1 if w <= 3 else 2) and s < 0.82:
            return A(H[8])                                             # the wet highlight line
        if p == w - 1 and w >= 4:
            return A(H[6])
        return A(H[7])
    return None


def hair_paint(ctx, P):
    """Set grey perm with a lavender rinse: tight curls (high contrast so they survive a thumbnail) on the shell, the
    rounded crown, a scalloped fringe roll over the forehead and fat rolled puffs over the ears; a stepped bun under a
    hairnet.  Possessed: bleached white; the loose strands drift from the undone bun."""
    Hh = HAIR_P if P else HAIR
    f = ctx.face
    n = nm(ctx)
    x, y, z = bpos(ctx)
    lx, ly, lz = local(ctx)
    w_, h_, d_ = ctx.cube.size
    base = 5 if f in SIDE else (6 if f == 'top' else 3)
    if n == 'strand':
        return strand_lock(ctx)
    if n in ('hair', 'hair_top'):
        if f == 'bottom':
            return None if n == 'hair' else A(Hh[2])
        if n == 'hair':
            if f == 'front' and y > -13.0:
                return None                                             # the fringe roll covers the hairline
            if f in ('west', 'east'):
                if z < -3.0 and y > -9.0:
                    return None                                         # temple / cheek below the side puffs
                if y > -5.6 and z < 3:
                    return None
            if f == 'back' and y > -5.0 and (fl(x + 30) % 4) in (0, 3):
                return None                                             # a scalloped nape
        u = x if f in ('front', 'back', 'top') else z
        vv = z if f == 'top' else y
        idx = base + curl_idx(u + 40, vv + 40)
        if P and idx <= base - 3:
            idx -= 1                                                    # bleached: the crevices stay dark
        if f == 'top' and n == 'hair_top' and abs(x) < 0.6 and z > -2:
            idx -= 1                                                    # the parting toward the bun
        return A(hpick(Hh, idx))
    if n == 'fringe':
        # the hairline: one row of fat curls with a scalloped lower edge hanging on the forehead
        if f == 'bottom':
            return A(Hh[2])
        if f == 'front':
            a = fl(lx) % 4
            j = fl(ly)
            if j == h_ - 1 and a in (0, 3):
                return None                                             # the scallop between two curls
            idx = (6, 5, 3)[min(j, 2)] + (1 if a == 1 and j == 0 else 0) - (1 if a == 3 else 0)
            if j == h_ - 1:
                idx = 4 if a == 1 else 3
            return A(hpick(Hh, idx))
        if f == 'top':
            return A(hpick(Hh, 6 + curl_idx(lx + 40, lz + 41)))
        if f in ('west', 'east'):
            if fl(ly) == h_ - 1 and fl(lz) == 0:
                return None
            return A(hpick(Hh, 5 + (1 if fl(ly) == 0 else -1 if fl(ly) == h_ - 1 else 0)))
        return A(Hh[3])
    if n == 'wave':
        # a fat rolled puff over each ear: two horizontal sausage rolls, rounded at the ends
        if f in ('west', 'east', 'front', 'back'):
            if f in ('west', 'east'):
                uu, uw = lz, d_
            else:
                uu, uw = lx, w_
            j = fl(ly)
            roll = 0 if j < 3 else 1
            jr = j - 3 * roll
            end = uu < 1.0 or uu > uw - 1.0
            if end and jr in (0, 2) and f in ('west', 'east'):
                return None                                             # rounded roll ends
            if f in ('front', 'back') and jr in (0, 2) and (lx < 1.0 or lx > w_ - 1.0):
                return None
            idx = (6, 5, 3)[jr] + (1 if f in ('west', 'east') and jr == 0 and fl(uu + roll * 2) % 3 == 0 else 0)
            if f in ('west', 'east') and jr == 1 and fl(uu + roll * 2) % 3 == 2:
                idx -= 2                                                # the separate curls of each roll
            return A(hpick(Hh, idx))
        if f == 'top':
            return A(hpick(Hh, 6 + curl_idx(lx + 40, lz + 40)))
        return A(Hh[2])
    if n == 'bun':
        # the rodete: hair wound round and round, under a hairnet = a regular 1-texel diamond lattice in a cool
        # mid-grey with darker knots; two bobby pins in the base
        if f == 'bottom':
            return A(Hh[2])
        if f == 'top':
            u, v = lx, lz
            rr = math.hypot(lx - w_ / 2, lz - d_ / 2)
            wound = 7 if rr < 1.2 else (6 if fl(rr * 0.9) % 2 == 0 else 5)
        else:
            u, v = around(ctx), ly + ctx.cube.tier * 2
            wound = 6 + (1 if fl(ly) == 0 else 0) - (1 if ly > h_ - 1 else 0) - (1 if fl(u * 0.5 + ly) % 3 == 0 else 0)
        if ctx.cube.tier == 0 and f in ('east', 'west') and fl(ly) == 1 and 1 <= lz < 5:
            return A(PIN[2] if fl(lz) == 1 else PIN[1])                # bobby pins
        a_ = fl(u + v) % 6 == 0
        b_ = fl(u - v + 60) % 6 == 0
        if a_ and b_:
            return A(mix(Hh[3], NET[1], 0.25))                          # knot
        if a_ or b_:
            return A(mix(Hh[4], NET[1], 0.25))                          # net thread: a cool mid-grey line
        return A(hpick(Hh, wound))
    return A(pick(Hh, 0.5))


def brow_paint(ctx, P):
    """Pencilled thin brows: thicker at the inner end."""
    Hh = HAIR_P if P else HAIR
    f = ctx.face
    lx, ly, lz = local(ctx)
    w = ctx.cube.size[0]
    inner = (w - 1 - lx) if ctx.cube.sx < 0 else lx
    if f == 'front':
        return A(Hh[1] if inner < 1.5 else Hh[2] if inner < w - 1.5 else Hh[3])
    if f == 'top':
        return A(Hh[3])
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
    if n == 'pocket':
        # the patch pocket on her right hip, bulging round the wool ball: ribbed welt at the mouth, seams
        if f == 'top':
            return A(CARD[0] if 0.6 < lx < w - 0.6 and lz < d - 0.6 else CARD[5])
        if f == 'bottom':
            return A(CARD[1])
        if ly < 1.0:
            v += 0.1
        elif f == 'front' and edge(ctx) == 0:
            v -= 0.08
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
    """Tan rubber sole: a darker welt round the edge, a zig-zag tread underneath with a worn heel."""
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    if f == 'bottom':
        if edge(ctx) == 0:
            return A(SOLE[2])
        if lz > d - 3.0:
            return A(SOLE[3] if (fl(lx) + fl(lz)) % 2 else SOLE[2])    # worn smooth heel
        zig = (fl(lz) + abs(fl(lx) - w // 2)) % 3
        return A((SOLE[1], SOLE[3], SOLE[2])[zig])                      # chevron tread
    if f == 'top':
        return A(SOLE[3])
    return A(SOLE[1] if fl(around(ctx)) % 2 == 0 else SOLE[2])          # the rubber edge, notched


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
        # beaded eyeglass chain (cadenita) hanging from the temple tip and looping down behind the ear to the nape
        lx_ = lz
        cy = (h - 1.2) * math.sin(min(1.0, lx_ / max(1.0, d)) * math.pi * 0.5) ** 1.6 + 0.5
        if abs(ly - cy) < 0.6:
            return A(GOLD[4] if fl(lx_ + ly) % 2 == 0 else PEARL[4])
        return None
    vv = 0.6 + face_light(ctx) * 1.2
    if ctx.face == 'front':
        vv += 0.15
    return A(pick(PEARL, vv))


LENS_N = 10         # the round lenses: 10 x 10 discs (tortoiseshell ring + 8 x 8 rounded glass)
LENS_SHAPE = [
    "...XXXX...",
    ".XXXXXXXX.",
    ".XXXXXXXX.",
    "XXXXXXXXXX",
    "XXXXXXXXXX",
    "XXXXXXXXXX",
    "XXXXXXXXXX",
    ".XXXXXXXX.",
    ".XXXXXXXX.",
    "...XXXX...",
]


def _in_disc(i, j, n=LENS_N):
    return 0 <= i < n and 0 <= j < n and LENS_SHAPE[j][i] == 'X'


def lens_mask(i, j, n=LENS_N):
    """Disc: 0 outside, 1 frame ring (4-neighbour border), 2 glass."""
    if not _in_disc(i, j, n):
        return 0
    for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        if not _in_disc(i + di, j + dj, n):
            return 1
    return 2


# Magnified granny eye behind a coke-bottle lens (front-face grid of her RIGHT lens = the viewer's left; the left lens
# mirrors the eye but keeps the glare top-left).  A heavy lid drooping at the outer corner, a big brown iris looking at
# you with a catchlight, the smile crease of the lower lid.   f frame (drawn by lens_mask)  g glass  G glare
# l lid skin  L lash line  w white  i iris  I iris light  o pupil  c catchlight  b lower lid / smile crease
LENS_EYE = [
    "...ffff...",
    ".ffGGggff.",
    ".fGLLLLgf.",
    "fgLiiiiLgf",
    "fLwicoiwgf",
    "fgwiooiwgf",
    "fgbiIIibgf",
    ".fgbbbbgf.",
    ".ffggggff.",
    "...ffff...",
]
assert all(len(r) == LENS_N for r in LENS_EYE)
GLOW_EYE = set('gGwc')      # normal look: what glows white at night (the lid, lashes, iris and pupil stay dark)

# The possessed RIGHT lens: a lidless glassy blue doll's eye staring through a spider-web break.  The glass stays
# near-white (it still glows), the eye is a big blue iris (dark limbal ring, lighter lower half, a pinprick pupil,
# one wet glint) with two burst vessels; the web is drawn over it (WEB_*).
#   g glass  b limbal ring  B iris  C lower iris  o pupil  c glint  v vessel
POS_EYE = [
    "...ffff...",
    ".ffggggff.",
    ".fggggggf.",
    "fgggbbgggf",
    "fggbcBbggf",
    "fvgbBoBbgf",
    "fggbCCbgvf",
    ".fggbbggf.",
    ".ffggggff.",
    "...ffff...",
]
assert all(len(r) == LENS_N for r in POS_EYE)
WEB_IMPACT = (1.6, 2.4)                                       # high on the outer side of the right lens
WEB_ENDS = ((8.7, 1.6), (7.6, 8.4), (1.4, 8.6))              # three clean radial cracks to the rim


def _seg_dist(px, py, a, b):
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def _web(i, j):
    """Spider-web break of the possessed right lens: 2 a dark 1-texel crack (4 rays + one ring), 0 clear glass."""
    px, py = i + 0.5, j + 0.5
    for e in WEB_ENDS:
        if _seg_dist(px, py, WEB_IMPACT, e) < 0.5:
            return 2
    r = math.hypot(px - WEB_IMPACT[0], py - WEB_IMPACT[1])
    if abs(r - 2.2) < 0.45 and px > WEB_IMPACT[0] - 0.5:
        return 2                                                  # one ring round the impact (the inner half)
    return 0


def _hole(i, j):
    """The blown-out LEFT lens (possessed): True where the glass is gone.  A jagged hole a little toward the nose,
    so the outer shards keep covering the edge of the face."""
    c = (3.6, 4.6)
    r = math.hypot(i + 0.5 - c[0], j + 0.5 - c[1])
    ang = math.atan2(j + 0.5 - c[1], i + 0.5 - c[0])
    rr = 2.7 + 0.75 * math.sin(ang * 3.0 + 0.9) + (0.5 if h2(i, j, 71) > 0.7 else 0.0)
    return r < rr and i <= 6


def lens_texel(sx, i, j, P):
    """Colour of lens texel (i, j) on the FRONT face (i to the viewer's right).  sx: -1 her right lens (viewer's
    left), +1 her left.  -> (rgba or None, glow rgba or None)."""
    m = lens_mask(i, j)
    if m == 0:
        return None, None
    if m == 1:
        # tortoiseshell ring: dark brown with amber flecks, lit on the top-left arc, darkest bottom-right
        c = (LENS_N - 1) / 2.0
        lightdir = ((c - i) + (c - j)) / LENS_N                       # +: top-left
        hh = h2(i * 3 + (sx + 1) * 17, j * 5, 61)
        if P and sx > 0 and hh > 0.55 and i < 6:
            return None, None                                            # the shattered side: chips out of the rim
        if hh > 0.72:
            return (AMBER[1] if lightdir > 0 else AMBER[0]), None
        return (FRAME[5] if lightdir > 0.35 else FRAME[4] if lightdir > 0 else FRAME[2] if lightdir > -0.35
                else FRAME[1]), None
    if not P:
        ii = i if sx < 0 else LENS_N - 1 - i                          # mirror the eye, not the glare
        ch = LENS_EYE[j][ii]
        if ch in 'co':
            ch = LENS_EYE[j][i] if LENS_EYE[j][i] in 'co' else ch      # ... nor the catchlight (top-left)
        if LENS_EYE[j][i] == 'G':
            ch = 'G'
        elif ch == 'G':
            ch = 'g'
        if ch == 'G':
            col = GLASS[5]
        elif ch == 'g':
            col = GLASS[3] if j < 4 else GLASS[2]
        else:
            col = {'l': mix(SKIN[6], GLASS[3], 0.25), 'L': mix(SKIN[1], IRIS[0], 0.5),
                   'w': mix(hx('#f6f1ea'), GLASS[3], 0.3), 'i': IRIS[2], 'I': IRIS[4], 'o': IRIS[0],
                   'c': hx('#ffffff'), 'b': mix(SKIN[5], GLASS[2], 0.3)}.get(ch, GLASS[2])
        g = None
        if ch in GLOW_EYE:
            g = (236, 242, 255, 255) if ch != 'w' else (212, 220, 236, 255)
        return col, g
    # ---- possessed
    if sx < 0:
        # her right lens: the glassy blue doll's eye staring through a spider-web break; the glass still glows white
        ch = POS_EYE[j][i]
        if ch == 'o':
            return hx('#04050a'), None                                   # pinprick pupil
        if ch == 'c':
            return hx('#ffffff'), (255, 255, 255, 255)                   # the wet glint
        if _web(i, j):
            return hx('#2a2c3a'), None                                   # a dark crack line (no glow)
        col, g = {'B': (BLUE[4], (70, 150, 250, 255)), 'C': (BLUE[5], (120, 190, 255, 255)),
                  'b': (BLUE[2], (24, 70, 170, 255)), 'v': (hx('#b0303e'), (150, 40, 50, 255)),
                  'g': (GLASS[4], (232, 240, 255, 255))}.get(ch, (GLASS[4], (232, 240, 255, 255)))
        return col, g
    # her left lens: blown out -- jagged shards cling to the rim; the black hole behind shows through
    if _hole(i, j):
        return None, None
    edge_ = any(_hole(i + di, j + dj) for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)))
    return (GLASS[1] if edge_ else GLASS[3]), ((150, 160, 185, 255) if not edge_ else None)


def lens_paint(ctx, P):
    f = ctx.face
    sx = ctx.cube.sx
    n = LENS_N
    if f in ('front', 'back'):
        i = ctx.i if f == 'front' else ctx.w - 1 - ctx.i
        c, _ = lens_texel(sx, i, ctx.j, P)
        if c is None:
            return None
        if f == 'back' and lens_mask(i, ctx.j) == 2:
            return A(GLASS[1] if not P else GLASS[0])
        return A(c)
    # rim faces: the thickness of the frame where the disc touches its bounding box
    vv = 0.48 + face_light(ctx)
    k = ctx.j if f in ('west', 'east') else ctx.i
    span = [t for t in range(n) if _in_disc(0, t, n)]
    if not (span[0] <= k <= span[-1]):
        return None
    return A(pick(FRAME, vv + (0.06 if k in (span[0], span[-1]) else 0.0)))


def make_lens_glow(sx):
    """Emissive lens decal (front face).  normal: the glass glows white (lids, iris and pupil stay dark); poseida:
    the right lens still glows white but cracked (the web stays dark) around the blue iris; the left lens keeps a
    few lit shards round its hole (the ember lives on the skull behind)."""
    def fn(img, u0, v0, w, h):
        px = img.load()
        P = _PAINT['variant'] == 'poseida'
        for j in range(h):
            for i in range(w):
                _, g = lens_texel(sx, i, j, P)
                if g is not None:
                    px[u0 + i, v0 + j] = g
    return fn


# the dying ember deep in the black hole of her left eye (skull front cells: col, row) and its faint glowing rim
EMBER_PX = {(12, 7): (255, 150, 60, 255), (13, 7): (230, 90, 24, 255), (12, 8): (210, 70, 20, 255),
            (13, 8): (160, 36, 10, 255)}
EMBER_RIM = (110, 22, 14, 255)


def socket_glow(img, u0, v0, w, h):
    """Emissive decal on the skull front: in the possessed look the 2x2 ember deep in the black hole of her left eye
    and the faint glowing rim round the hole (rhymes with Ofelia's broken eye).  Nothing in the normal look.
    'rota': the two milky cataracts glow dimly (a drowned grey-white), so she shows two pale eyes in the dark."""
    if _PAINT['variant'] == 'rota':
        px = img.load()
        for j, row in enumerate(FACE_R):
            for i, ch in enumerate(row):
                if ch in 'Wwg' and i < w and j < h:
                    px[u0 + i, v0 + j] = {'W': (178, 186, 180, 255), 'w': (120, 128, 124, 255), 'g': (70, 78, 80, 255)}[ch]
        return
    if _PAINT['variant'] != 'poseida':
        return
    px = img.load()
    # skull front: 16 wide, i = x + 8 ; j = y + 14 -- the same cells as FACE / FACE_P
    for j, row in enumerate(FACE_P):
        for i, ch in enumerate(row):
            if ch == 'X' and i < w and j < h:
                px[u0 + i, v0 + j] = EMBER_RIM
    for (i, j), c in EMBER_PX.items():
        if 0 <= i < w and 0 <= j < h:
            px[u0 + i, v0 + j] = c


def frame_paint(ctx, P):
    """Bridge and temples: tortoiseshell with amber flecks, the curled tips darker."""
    vv = 0.48 + face_light(ctx)
    if nm(ctx) == 'temple':
        lx, ly, lz = local(ctx)
        if lz > ctx.cube.size[2] - 2.5:
            vv -= 0.08
    if h2(ctx.i, ctx.j, 63 + ctx.cube.seed) > 0.8:
        return A(AMBER[0])
    return A(pick(FRAME, vv))


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
        if f == 'top':
            return A(YERBA[3] if (fl(lx) + fl(lz)) % 2 == 0 else YERBA[2])   # the yerba, green, heaped
        return A(METAL[5] if fl(lx + lz) % 3 == 0 else METAL[4])        # the silver virola
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
    """Crocheted granny-square knitting bag hanging from the walker: 4x4 squares (rings of soft, faded colour) on a
    grey-violet ground, a sagging rounded bottom, two cord handles looped over the front bar."""
    f = ctx.face
    n = nm(ctx)
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    if n == 'handles':
        i, j = fl(lx), fl(ly)
        loop = i % 4
        if (j == 0 and loop in (1, 2)) or (j >= 1 and loop in (0, 3)):
            return A(mix(SQ_DARK, hx('#9a90a2'), 0.35 if j == 0 else 0.15))
        return None
    if f == 'top':
        if n == 'bag' and 0.8 < lx < w - 0.8 and 0.5 < lz < d - 0.5:
            return A(WOOL[2])                                           # red wool inside
        return A(SQ_DARK)
    if f == 'bottom':
        return A(scale(SQ_DARK, 0.7))
    u = around(ctx) if f in SIDE else lx
    vv = ly + (5 if n == 'bag_bottom' else 0)
    a, b_ = fl(u) % 4, fl(vv) % 4
    if a == 3 or b_ == 3:
        c = SQ_DARK
    else:
        sq = fl(u / 4) * 3 + fl(vv / 4) * 5
        ring = max(abs(a - 1), abs(b_ - 1))
        c = SQUARES[(sq + ring) % len(SQUARES)]
        if ring == 0:
            c = SQUARES[(sq + 3) % len(SQUARES)]
    c = mix(c, hx('#000000'), max(0.0, -face_light(ctx)) * 1.2 + (0.18 if n == 'bag_bottom' else 0.0))
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
        # a wound ball: crossing bands of strand (one diagonal on front/back, the other on the sides), a groove
        # every third band, lit from the top-left
        if f == 'bottom':
            return A(WOOL[1])
        if f == 'top':
            band = fl(math.hypot(lx - 1.0, lz - 3.0) * 1.3)
            idx = (5, 4, 3)[band % 3] if band < 4 else 3
            return A(WOOL[idx])
        u = lx if f in ('front', 'back') else lz
        diag = (u + ly) if f in ('front', 'back') else (u - ly + 8)
        band = fl(diag * 0.75)
        idx = (4, 3, 2)[band % 3]
        if fl(ly) == 0 and f in ('front', 'west'):
            idx += 1                                                    # the light on top
        if f in ('east', 'back'):
            idx -= 1
        return A(WOOL[max(1, min(6, idx))])
    if n == 'tail':
        # the loose end draping off the ball sideways over the pocket, its tip hanging past the pocket's edge
        i, j = fl(lx), fl(ly)
        path = {(5, 0), (6, 0), (3, 1), (4, 1), (0, 2), (1, 2), (2, 2), (0, 3)}
        if (i, j) not in path:
            return None
        return A(WOOL[5] if (i + j) % 2 == 0 else WOOL[4])
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
    # the sides: cream crochet with red popcorn stitches (little bumps, staggered, lit on top, shadowed under)
    u = around(ctx)
    j = fl(ly)
    if fl(u) % 4 == (0 if j == 0 else 2):
        return A(WOOL[4] if j == 0 else WOOL[3])
    if fl(u) % 4 == 0 and j == 1:
        return A(mix(LACE[0], WOOL[1], 0.3))
    return A(mix(LACE[2] if j == 0 else LACE[1], hx('#d8b88a'), 0.3))


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
    """Mate de calabaza: a round warm-brown gourd (lit top-left, a bright highlight stripe), a pyrographed band and
    darker edges; the yerba heaps inside the silver virola."""
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    if f == 'top':
        return A(YERBA[1] if (fl(lx) + fl(lz)) % 2 == 0 else YERBA[2])
    if f == 'bottom':
        return A(GOURD[1])
    vv = 0.58 + face_light(ctx)
    u = around(ctx)
    if fl(u) in (1, 2 * w + 2 * d - 2) or (f == 'front' and fl(lx) == 1):
        vv += 0.18                                                      # the highlight stripe
    if fl(ly) == 1 and fl(u) % 2 == 0:
        vv -= 0.16                                                      # pyrographed band
    if corner_dist(ctx) < 1.0:
        vv -= 0.1
    if fl(ly) == h - 1:
        vv -= 0.1                                                       # the round bottom in shadow
    return A(pick(GOURD, vv))


def dentures_paint(ctx, P):
    """Floating dentures, 7 x 3 x 4 plates: a 1-texel band of glossy pink acrylic gum, then the teeth -- three
    front teeth and a darker molar each side, separated by dark 1-texel gaps.  The biting surfaces show the
    horseshoe (teeth round the front and the sides, pink plate in the middle)."""
    f = ctx.face
    n = nm(ctx)
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    upper = n == 'denture_up'
    i, j = fl(lx), fl(ly)
    GAP = hx('#2a1418')
    if f == 'front':
        gum = (j == 0) if upper else (j == h - 1)
        if gum:
            return A(GUM[4] if i in (1, 3, 5) else GUM[2] if i in (2, 4) else GUM[3])   # scallops over each tooth
        if i in (2, 4):
            return A(GAP)
        tip = (j == h - 1) if upper else (j == 0)
        if i in (0, w - 1):
            return A(TEETH[1] if tip else TEETH[2])                        # molars, darker
        return A(TEETH[3] if tip else TEETH[4])
    if f in ('west', 'east'):
        if (upper and j == 0) or (not upper and j == h - 1):
            return A(GUM[2])
        if fl(lz) == 2:
            return A(GAP)
        return A(TEETH[1] if lz > 2.5 else TEETH[2])
    if (f == 'top' and upper) or (f == 'bottom' and not upper):
        return A(GUM[3] if 1 <= lx < w - 1 and lz < d - 1 else GUM[2])   # the palate plate
    if f == 'back':
        return A(GUM[1])
    # biting surfaces: a horseshoe of teeth, the plate in the middle
    if lz < 1.0 or ((lx < 1.0 or lx > w - 1.0) and lz < d - 0.5):
        if lz < 1.0 and i in (2, 4):
            return A(GAP)
        return A(TEETH[3] if lz < 1.0 and 1 <= i <= w - 2 else TEETH[2])
    return A(GUM[2] if upper else GUM[1])


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
    """A crumpled paper tissue tucked in the left cuff: puffy, lit on top, one fold, a corner poking out."""
    lx, ly, lz = local(ctx)
    w, h = ctx.cube.size[0], ctx.cube.size[1]
    i, j = fl(lx), fl(ly)
    if (i, j) in ((w - 1, h - 1), (0, h - 1)):
        return None
    if j == 0:
        return A(TISSUE[1])                                             # (inside the cuff)
    if j == 1:
        return A(TISSUE[2] if i != 1 else TISSUE[1])
    return A(TISSUE[1] if i != 1 else TISSUE[0])


MATS = {
    'skin': skin_paint, 'hair': hair_paint, 'brow': brow_paint, 'card': card_paint, 'dress': skirt_paint,
    'stock': stock_paint, 'felt': felt_paint, 'sole': sole_paint, 'pearl': pearl_paint, 'gold': pearl_paint,
    'lens': lens_paint, 'frame': frame_paint, 'metal': metal_paint, 'foam': foam_paint, 'tennis': tennis_paint,
    'bag': bag_paint, 'knitting': knitting_paint, 'wool': wool_paint, 'oak': oak_paint, 'gourd': gourd_paint,
    'teeth': dentures_paint, 'maw': maw_paint, 'aid': aid_paint, 'tissue': tissue_paint,
}


# ---------------- B2: the 'rota' look (Act 5, the hunt) and its extra bones
def _lum(c):
    return (0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]) / 255.0


def _veins(x, y, z, seed=0, width=0.022):
    """Thin branching dark veins under the skin (ridged noise in bone-local texels)."""
    return abs(fbm(x * 0.42 + 11, y * 0.42 + 7, z * 0.42 + 3, 2, 90 + seed) - 0.5) < width


def rota_skin(ctx):
    """Corpse skin: the possessed colour remapped onto a cold grey-blue ramp, dark veins, the face of FACE_R."""
    n = nm(ctx)
    f = ctx.face
    x, y, z = bpos(ctx)
    base = skin_paint(ctx, True)
    if base is None:
        return None
    if n in ('skull', 'jaw', 'cheek', 'jowl', 'chin') and f == 'front':
        ch = face_char(x, y, FACE_R)
        if ch and ch != '.':
            if ch in CATARACT:
                return A(CATARACT[ch])
            return A({'D': SKIN_R[0], 'd': SKIN_R[2], 'R': mix(BLOOD[3], SKIN_R[5], 0.3), 'B': BLOOD[2], 'b': BLOOD[3],
                      'r': BLOOD[4], 'V': VEIN_R, 'M': hx('#060203')}[ch])
        base_ch = face_char(x, y, FACE)
        if base_ch and base_ch.isdigit():
            return A(SKIN_R[max(0, int(base_ch) - 1)])
    if n == 'cheek' and f == 'front':
        return A(SKIN_R[3])                                             # sunken, no rouge
    if n == 'nose_tip' and f == 'bottom':
        return A(BLOOD[1])                                              # the nostrils bleed
    if n == 'neck' and f == 'front':
        lx, ly, lz = local(ctx)
        if fl(lx) == 3 or (fl(lx) == 1 and ly < 2.5):
            return A(BLOOD[2] if fl(ly) % 3 else BLOOD[3])             # the blood keeps running down the neck
    v = _lum(base)
    idx = max(0, min(9, int(v * 12.0) - 1))
    c = SKIN_R[idx]
    if n not in ('skull',) or f != 'front':
        if _veins(x, y, z, sum(map(ord, n)) % 7):
            return A(mix(c, VEIN_R, 0.75))
    return A(c)


def rota_gown(ctx, src):
    """The cardigan and the floral dress become one filthy old cotton nightgown (camison): the print survives only as
    a faded ghost, grime in the folds, and the front is soaked with the blood that pours out of her mouth."""
    f = ctx.face
    n = nm(ctx)
    x, y, z = bpos(ctx)
    lx, ly, lz = local(ctx)
    v = _lum(src) * 0.4 + 0.52 + face_light(ctx) * 0.6
    g = fbm(x * 0.21 + 50, y * 0.21 + 9, z * 0.21, 3, 41)
    c = pick(GOWN, v - (0.12 if g > 0.68 else 0.0))
    if g > 0.64:
        c = mix(c, GRIME, (g - 0.64) * 2.0)
    if f == 'front' and n in ('torso', 'cpanel', 'hips', 'cpanel_lo', 'skirt_f', 'hem') and abs(x) < 5.0:
        # the bib: soaked under the collar, drip columns running down the front, dried brown below
        col = fl(x + 20)
        drip = -9.0 + 7.0 * h2(col, 3, 17) + (8.0 if n in ('hips', 'cpanel_lo') else 0.0)
        if n == 'torso' and y < -4.5 + 1.5 * h2(col, 1, 9):
            return A(BLOOD[2] if (fl(x) + fl(y)) % 4 else BLOOD[1])
        if n == 'torso' and h2(col, 5, 3) > 0.45 and y < drip + 6.0:
            return A(BLOOD[3] if h2(col, fl(y), 2) > 0.3 else BLOOD[2])
        if n in ('hips', 'cpanel_lo', 'skirt_f', 'hem') and h2(col, 7, 5) > 0.7 and ly < 4.0:
            return A(BLOOD_DRY[1])
    if fbm(x * 0.33 + 3, y * 0.33 + 70, z * 0.33, 2, 77) > 0.8:
        return A(mix(c, BLOOD_DRY[1], 0.6))                             # old dried stains
    if f in SIDE and n in ('skirt_f', 'skirt_b', 'hem') and ly > ctx.cube.size[1] - 2.0:
        return A(mix(c, GRIME, 0.55))                                   # the hem dragged over floors
    return A(c)


def rota_paint(ctx):
    k = kind(ctx)
    if k == 'skin':
        return rota_skin(ctx)
    if k in ('card', 'dress'):
        src = MATS[k](ctx, True)
        return None if src is None else rota_gown(ctx, src)
    if k == 'stock':
        # bare legs: corpse skin with varicose veins (the stockings are gone)
        src = stock_paint(ctx, True)
        x, y, z = bpos(ctx)
        c = SKIN_R[max(0, min(9, int(_lum(src) * 11.0)))]
        if _veins(x, y, z, 5, 0.03):
            return A(mix(c, VEIN_R, 0.8))
        return A(c)
    if k in ('hair', 'brow'):
        src = MATS[k](ctx, True)
        if src is None:
            return None
        return A(mix(src, hx('#7d7462'), 0.28))                         # greasy, yellowed white
    if k in ('felt', 'sole', 'pearl', 'gold', 'tennis', 'foam', 'bag', 'knitting', 'wool', 'oak', 'gourd', 'metal',
             'aid', 'tissue', 'lens', 'frame'):
        src = MATS[k](ctx, True)
        if src is None:
            return None
        return A(mix(src, GRIME, 0.45))
    if k == 'teeth':
        src = dentures_paint(ctx, True)
        return A(mix(src, ROT_TEETH[2], 0.4))
    if k == 'maw':
        src = maw_paint(ctx, True)
        if src is None:
            return None
        return A(mix(src, BLOOD[1], 0.35))
    fn = MATS.get(k)
    return fn(ctx, True) if fn else A(hx('#ff00ff'))


def fang_paint(ctx, P):
    """Rows of rotten teeth (zero-depth planes): long, uneven, yellow-brown with dark roots and gaps between them."""
    lx, ly, lz = local(ctx)
    w, h = ctx.cube.size[0], ctx.cube.size[1]
    i, j = fl(lx), fl(ly)
    up = getattr(ctx.cube, 'up', False)              # teeth pointing up (lower row): the root is at the bottom
    if h2(i, 0, 31 + ctx.cube.seed) < 0.22:
        return None                                  # a missing tooth
    length = 1 + fl(h2(i, 1, 33 + ctx.cube.seed) * h)
    k = (h - 1 - j) if up else j                     # distance from the root
    if k >= length:
        return None
    if k == 0:
        return A(BLOOD[2] if h2(i, 2, 35) > 0.5 else GUM[1])
    return A(ROT_TEETH[min(4, 2 + (1 if i % 2 else 0) + (1 if k == length - 1 else 0))] if h2(i, k, 37) > 0.15
             else BLOOD[3])


def jawlong_paint(ctx, P):
    """The unhinged lower jaw hanging to the chest: stretched grey skin split by tendon lines, blood sheeting down."""
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    if f == 'top':
        return A(MOUTH[1] if lz > 1.0 else BLOOD[2])                    # inside: the black gullet
    v = 0.42 + face_light(ctx) - ly * 0.012
    c = pick(SKIN_R, v)
    if f == 'front':
        col = fl(lx)
        chin = nm(ctx) == 'jawchin'
        if (not chin and col == 2) or (chin and col == 1 and ly < 2):
            return A(BLOOD[3] if fl(ly) % 4 else BLOOD[2])             # blood off the corner of the lip
        if not chin and col in (0, w - 1) and fl(ly) % 2 == 0:
            return A(SKIN_R[2])                                         # tendons straining
        if chin and ly > h - 1.5:
            return A(SKIN_R[5])                                         # the chin knob at the bottom
    if f in ('west', 'east') and fl(ly) % 3 == 0:
        return A(SKIN_R[2])
    return A(c)


def talon_paint(ctx, P):
    """Long jointed fingers (rota): grey-blue, dark knuckle rings every 3 texels, black split nails."""
    lx, ly, lz = local(ctx)
    if nm(ctx) == 'nail':
        return A((hx('#4a4552'), hx('#211d27'), hx('#0b090e'))[min(2, fl(ly))])
    if fl(ly) % 3 == 2:
        return A(SKIN_R[2])
    return A(pick(SKIN_R, 0.45 + face_light(ctx)))


def vertebra_paint(ctx, P):
    """Vertebrae and shoulder blades pushing up through the torn gown: yellow-grey bone, bloody torn edges."""
    f = ctx.face
    n = nm(ctx)
    if n == 'tear':
        lx, ly, lz = local(ctx)
        if ctx.i in (0, ctx.w - 1) or ctx.j in (0, ctx.h - 1):
            return A(BLOOD[2])
        return A(MOUTH[2])
    v = 0.55 + face_light(ctx)
    return A(pick(ROT_TEETH, v) if f != 'bottom' else BLOOD[1])


MATS.update({'fang': fang_paint, 'jawlong': jawlong_paint, 'talon': talon_paint, 'vertebra': vertebra_paint})


def make_mat(variant):
    P = variant == 'poseida'

    def mat(ctx):
        _PAINT['variant'] = variant
        if variant == 'rota':
            return rota_paint(ctx)
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
BROW_KIND = 12.0     # rest tilt of the brows (inner ends up: sweet)
# possessed loose hair (head-local): (root pivot, direction root -> tip, the way plane A faces, length, width)
LOOSE_SPEC = [
    ((2.0, -15.5, 0.0), (0.78, -0.62, -0.18), (0, 0, -1), 15, 11, 1),   # up off the crown, hooking over to her left
    ((-9.0, -12.0, -1.0), (-0.72, 0.68, 0.06), (0, 0, -1), 22, 12, 1),  # her right: out and down past the shoulder,
    ((9.0, -12.5, -1.0), (0.74, 0.64, 0.08), (0, 0, -1), 21, 12, -1),   # the tips lifting; her left
    ((-5.0, -10.0, 3.5), (-0.55, 0.83, 0.1), (0, 0, -1), 18, 10, -1),   # drooping down the back, right
    ((5.0, -9.0, 3.5), (0.5, 0.85, 0.12), (0, 0, -1), 17, 10, 1),       # drooping down the back, left
]


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
# B2 'rota' bones (glasses become a toggle too: she loses them in the hunt)
ROTA_BONES = ('jaw_long', 'teeth_upper', 'right_talons', 'left_talons', 'spine')
TOGGLE_DEFAULT = dict({
    'walker': True, 'bun': True, 'right_slipper': True, 'glasses': True,
    'rocker': False, 'needle_right': False, 'needle_left': False, 'mate': False, 'chancleta': False,
    'yarn_right': False, 'yarn_left': False, 'dentures': False,
}, **{h: False for h in LOOSE}, **{b: False for b in ROTA_BONES})
VARIANT_TOGGLES = {
    'normal': {},
    'poseida': dict({'bun': False}, **{h: True for h in LOOSE}),
    'rota': dict({'bun': False, 'glasses': False, 'walker': False}, **{h: True for h in LOOSE},
                 **{b: True for b in ROTA_BONES}),
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
    # B2 hunt poses (shown with the 'rota' look; no walker, no rocker)
    'crawl_spider': {'walker': False},
    'stand_tall': {'walker': False},
    'neck_twist': {'walker': False},
    'listen': {'walker': False},
    'ceiling_hang': {'walker': False},
    'jumpscare': {'walker': False},
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
    """Exports every bone to Java; the preview JSON hides the toggle bones the current look / pose does not show.
    paint() tells the variant-aware emissive decals which look is being painted (decals never see the material)."""
    visible = None

    def paint(self, default_mat, seed=1, layer='base'):
        _PAINT['variant'] = getattr(default_mat, 'variant', 'normal')
        return super().paint(default_mat, seed, layer)

    def to_json(self):
        d = super().to_json()
        d['toggles'] = {'default': dict(TOGGLE_DEFAULT), 'variants': {k: dict(v) for k, v in VARIANT_TOGGLES.items()},
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
                bd['hidden_cubes'] = bd['cubes']          # a toggle-aware viewer can still show them
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
    # B2 'rota' (toggle): the spine and the shoulder blades push up through a tear in the back of the gown
    bone('spine', 'chest', (0, -6, 6.5))
    box('spine', (-2.5, -5, 0.05), (5, 10, 0), 'vertebra', 'tear')
    for k in range(5):
        box('spine', (-1, -4.5 + 2.2 * k, -0.6), (2, 2, 2), 'vertebra', 'vertebra')
    box('spine', (-6.0, -4.0, -0.3), (3, 5, 1), 'vertebra', 'blade')
    box('spine', (3.0, -4.0, -0.3), (3, 5, 1), 'vertebra', 'blade')

    # ---------------- neck + head (the head juts forward and looks up at you)
    bone('neck', 'chest', (0, -8.5, -1), rot=(NECK_TILT, 0, 0))
    box('neck', (-2.5, -4, -2.5), (5, 5, 5), 'skin', 'neck')
    box('neck', (-2, -3, -3.5), (4, 3, 1), 'skin', 'wattle')
    bone('head', 'neck', B.world('neck', (0, -3.5, -0.5)), world=True, wrot=(HEAD_LOOK, 0, 0))
    H = 'head'
    box(H, (-8, -14, -9), (16, 14, 13), 'skin', 'skull', decals={'eyes:front': socket_glow})
    # the perm: a curly shell, a rounded crown on top, a fringe roll of fat curls over the forehead, rolled puffs
    # over the ears that stick out past the glasses temples
    box(H, (-8, -14, -9), (16, 9, 13), 'hair', 'hair', inflate=0.6)
    box(H, (-6.5, -16, -7.5), (13, 2, 11), 'hair', 'hair_top', inflate=0.2)
    box(H, (-8, -15, -11), (16, 3, 2), 'hair', 'fringe')
    box(H, (-13, -13, -6), (5, 6, 10), 'hair', 'wave', sx=-1)
    box(H, (8, -13, -6), (5, 6, 10), 'hair', 'wave', sx=1)
    box(H, (-1, -8, -10), (2, 5, 1), 'skin', 'nose')
    box(H, (-1.5, -5, -11), (3, 3, 2), 'skin', 'nose_tip')
    box(H, (-8, -1, -9.5), (3, 2, 1), 'skin', 'cheek', sx=-1)
    box(H, (5, -1, -9.5), (3, 2, 1), 'skin', 'cheek', sx=1)
    box(H, (-8, 0, -9), (2, 4, 7), 'skin', 'jowl', sx=-1)
    box(H, (6, 0, -9), (2, 4, 7), 'skin', 'jowl', sx=1)
    box(H, (-9, -8, -2), (1, 5, 3), 'skin', 'ear', sx=-1)
    box(H, (8, -8, -2), (1, 5, 3), 'skin', 'ear', sx=1)
    box(H, (-9.4, -3.4, -1.2), (1, 1, 1), 'pearl', 'earring', sx=-1)
    box(H, (8.4, -3.4, -1.2), (1, 1, 1), 'pearl', 'earring', sx=1)
    box(H, (-9.8, -7.0, 0.8), (1, 3, 1), 'aid', 'aid', sx=-1)

    # brows (pencilled, expressive) right on top of the frames, under the fringe
    bone('right_brow', H, (-6.0, -11.5, -9.6), rot=(0, 0, -BROW_KIND))
    box('right_brow', (-2.5, -0.5, -0.45), (5, 1, 1), 'brow', 'brow', sx=-1)
    bone('left_brow', H, (6.0, -11.5, -9.6), rot=(0, 0, BROW_KIND))
    box('left_brow', (-2.5, -0.5, -0.45), (5, 1, 1), 'brow', 'brow', sx=1)

    # jaw: chin + lower lip between the jowls; the hidden throat box and the cheek flaps travel with it
    JO = (0, 0, -1)
    bone('jaw', H, JO)
    box('jaw', (-6, 0, -8), (12, 3, 8), 'skin', 'jaw', ho=JO)
    box('jaw', (-3, 2.5, -8.5), (6, 2, 1), 'skin', 'chin', ho=JO)
    box('jaw', (-5, -8, -6), (10, 8, 5), 'maw', 'maw', ho=JO)
    box('jaw', (-5.9, -8, -7.5), (0, 8, 5), 'maw', 'flap', sx=-1, ho=JO)
    box('jaw', (5.9, -8, -7.5), (0, 8, 5), 'maw', 'flap', sx=1, ho=JO)

    # the rodete: a stepped dome seated on the crown (its base buried 2 texels in the curls), under a hairnet
    bone('bun', H, (0, -15.0, 2.5), rot=(-20, 0, 0))
    box('bun', (-4.5, -1, -4.5), (9, 3, 9), 'hair', 'bun', tier=0)
    box('bun', (-3.5, -3, -3.5), (7, 2, 7), 'hair', 'bun', tier=1)
    box('bun', (-2.5, -4, -2.5), (5, 1, 5), 'hair', 'bun', tier=2)

    # glasses: two thick round tortoiseshell lenses (10 x 10 discs, 2 deep), wider than the face; the bridge, the
    # temples into the ear puffs and the beaded chain (cadenita) looping from the temple tips
    bone('glasses', H, (0, -6.0, -9.9))
    for sx in (-1, 1):
        x0 = -11.0 if sx < 0 else 1.0
        box('glasses', (x0, -5.0, -0.7), (LENS_N, LENS_N, 2), 'lens', 'lens', sx=sx,
            decals={'eyes:front': make_lens_glow(sx)})
        box('glasses', ((-12.0 if sx < 0 else 11.0), -2.5, 0.5), (1, 1, 9), 'frame', 'temple', sx=sx)
        box('glasses', ((-12.2 if sx < 0 else 12.2), -1.5, 4.0), (0, 8, 6), 'pearl', 'chain', sx=sx)
    box('glasses', (-1, -2.0, -0.5), (2, 1, 1), 'frame', 'bridge')

    # floating dentures (toggle): parked at nose height 8 texels in front of the face, tilted so both rows of
    # teeth face you; the lower plate is hinged at the back of the upper one and clacks on its own bone
    bone('dentures', H, (0, -2.5, -17.5), rot=(-12, 0, 0))
    box('dentures', (-3.5, -3, -1.5), (7, 2, 3), 'teeth', 'denture_up')
    bone('dentures_lower', 'dentures', (0, -1, 1.5), rot=(36, 0, 0))
    box('dentures_lower', (-3.5, 0, -3), (7, 2, 3), 'teeth', 'denture_lo')

    # B2 'rota' (toggles): a row of rotten upper teeth behind the lip (hidden inside the closed jaw) and the unhinged
    # lower jaw: a long slab of stretched skin hanging off the jaw down to the chest, its own row of teeth on top
    bone('teeth_upper', H, (0, 0, 0))
    box('teeth_upper', (-4.5, -0.2, -8.7), (9, 2, 0), 'fang', 'fang_up')
    bone('jaw_long', 'jaw', (0, 0, 0))
    box('jaw_long', (-4, 2.5, -7.2), (8, 6, 4), 'jawlong', 'jawlong')
    box('jaw_long', (-3, 8.5, -6.8), (6, 3, 3), 'jawlong', 'jawchin')
    box('jaw_long', (-4.5, -2.2, -7.9), (9, 2, 0), 'fang', 'fang_lo', up=True)

    # possessed: the bun undone into long white locks drifting as if under water (toggles).  Radial: one up from
    # the crown, two out to the sides and down past the shoulders, two drooping down the back -- none reaches
    # back into the rocker.  Each bone holds two crossed planes of two S-curved locks; Java ripples 'hair_loose_'.
    for k, (p, dirv, face, ln, wd, bend) in enumerate(LOOSE_SPEC):
        bn = f'hair_loose_{k}'
        R = frame((0, -1, 0), dirv, (0, 0, -1), face)
        bone(bn, H, p, rot=_euler(R))
        curve = 'C' if k == 0 else 'S'
        box(bn, (-wd / 2, -ln, 0), (wd, ln, 0), 'hair', 'strand', seed=0.4 * k, bend=bend, curve=curve)
        box(bn, (0, -ln + 4, -wd / 2 + 1), (0, ln - 4, wd - 2), 'hair', 'strand', seed=0.4 * k + 0.8, bend=-bend,
            curve=curve)

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
        for fi, fx0 in enumerate((-2.0, -0.5, 1.0)):                     # three separate fingers
            box(hand, (fx0, 3, -1.2), (1, 3, 2), 'skin', 'finger', sx=sx, ring=(sx > 0 and fi == 0))
        box(hand, ((-2.6 if sx < 0 else 1.6), 0.5, -2.2), (1, 3, 1), 'skin', 'thumb', sx=sx)
        box(hand, (-2, 5, -0.2), (4, 3, 0), 'skin', 'claws', sx=sx)       # long nails: possessed texture only
        # B2 'rota' (toggle): the fingers keep growing -- three long jointed talons with split black nails
        tal = bone(f'{side}_talons', hand, (0, 0, 0))
        for fx0 in (-2.0, -0.5, 1.0):
            box(tal, (fx0, 5.5, -1.0), (1, 9, 1), 'talon', 'talon', sx=sx)
            box(tal, (fx0, 14.5, -1.0), (1, 3, 0), 'talon', 'nail', sx=sx)
        if sx > 0:
            box(fa, (-1.2, 4.3, -2.2), (3, 3, 0), 'tissue', 'tissue')     # tissue tucked into the cuff

    # held props (toggles); their rest rotations are solved so each one sits right in the pose that shows it
    # (PROP_ROT, generated with the poses)
    def prop(name, parent, at):
        return bone(name, parent, at, rot=PROP_ROT.get(name, (0.0, 0.0, 0.0)))
    prop('mate', 'right_hand', (0, 2.5, -2.6))
    box('mate', (-2, -3.0, -2), (4, 4, 4), 'gourd', 'gourd')
    box('mate', (-1.5, -4.0, -1.5), (3, 1, 3), 'metal', 'virola', inflate=0.3)
    box('mate', (0.3, -8.5, -0.5), (1, 5, 1), 'metal', 'bombilla')
    prop('chancleta', 'right_hand', (0, 3.0, -0.5))
    box('chancleta', (-3, -1, -8.5), (6, 2, 9), 'felt', 'chancleta')
    box('chancleta', (-3.5, 1, -9), (7, 1, 10), 'sole', 'sole')
    box('chancleta', (-1.5, -2, -8.7), (3, 2, 2), 'felt', 'pompom')
    prop('needle_right', 'right_hand', (0, 2, -0.5))
    box('needle_right', (-0.5, -0.5, -11), (1, 1, 13), 'metal', 'needle')
    prop('needle_left', 'left_hand', (0, 2, -0.5))
    box('needle_left', (-0.5, -0.5, -11), (1, 1, 13), 'metal', 'needle')
    box('needle_left', (0, 0.5, -9.5), (0, 7, 7), 'wool', 'knit')
    prop('yarn_right', 'right_hand', (0, 4, 0))
    box('yarn_right', (-1, 0, -1), (2, 30, 2), 'wool', 'yarn')
    prop('yarn_left', 'left_hand', (0, 4, 0))
    box('yarn_left', (-1, 0, -1), (2, 30, 2), 'wool', 'yarn')

    # red wool ball in the cardigan pocket (her right hip) with a loose tail
    bone('yarn_ball', 'body', (-5, -6.0, -6.5))
    box('yarn_ball', (-2, -2, -2), (4, 4, 4), 'wool', 'ball')
    box('body', (-7.5, -5.5, -9.5), (5, 4, 3), 'card', 'pocket', sx=-1)      # the patch pocket, bulging
    box('yarn_ball', (-4, 0.5, -3.1), (7, 4, 0), 'wool', 'tail')            # the loose end drapes off sideways

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
    box('walker', (-4, gy + 0.8, -18.6), (8, 5, 2), 'bag', 'bag')
    box('walker', (-3.5, gy + 5.8, -18.4), (7, 1, 2), 'bag', 'bag_bottom')
    box('walker', (-4, gy - 2.5, -17.0), (8, 4, 0), 'bag', 'handles')
    box('walker', (-4.5, gy - 4.5, -17.9), (8, 5, 0), 'knitting', 'knitting')
    bone('walker_wheel', 'walker', (-GRIP_X, -2.5, -17.0))
    box('walker_wheel', (-0.5, -2.5, -2.5), (1, 5, 5), 'foam', 'wheel')

    # ---------------- rocking chair (light oak, crocheted cushion, spindle back, doily over the crest)
    bone('rocker', 'base', (0, 0, 0))
    seat = HIP_Y - 24 + SIT_DY + 3            # cushion top (local y): the thighs rest on it
    box('rocker', (-9.5, seat, -8), (19, 2, 15), 'wool', 'cushion')
    box('rocker', (-10.5, seat + 2, -9), (21, 1, 17), 'oak', 'seat')
    for sx in (-1, 1):
        x0 = -10.5 if sx < 0 else 8.5
        # curved runner in three steps each way: the ends sweep up
        box('rocker', (x0, -2, -8), (2, 2, 15), 'oak', 'runner')
        box('rocker', (x0, -3, -11), (2, 2, 3), 'oak', 'runner')
        box('rocker', (x0, -4.5, -13), (2, 2, 2), 'oak', 'runner')
        box('rocker', (x0, -3, 7), (2, 2, 3), 'oak', 'runner')
        box('rocker', (x0, -4.5, 10), (2, 2, 3), 'oak', 'runner')
        box('rocker', (x0 - 0.5 * sx, seat - 9, -9), (2, 2, 15), 'oak', 'armrest')
        box('rocker', (x0, seat - 7, -8.5), (2, 12, 2), 'oak', 'post')          # arm post = front leg to the runner
    bone('rocker_back', 'rocker', (0, seat + 2, 7), rot=(-12, 0, 0))
    for sx in (-1, 1):
        x0 = -10.5 if sx < 0 else 8.5
        box('rocker_back', (x0, -34, -1), (2, 37, 2), 'oak', 'stile')           # stile = back leg to the runner
    box('rocker_back', (-11.5, -38, -1.5), (23, 5, 3), 'oak', 'crest')
    box('rocker_back', (-8.5, -33, 0), (17, 29, 0), 'oak', 'spindles')
    box('rocker_back', (-6, -36, -1.7), (12, 8, 0), 'oak', 'doily')

    m = NonaModel('nona', 256, 160, B.r.roots)   # 160: room for the B2 'rota' bones
    m.scale = 0.5
    if pose is None and os.path.basename(sys.argv[0]) == 'preview.py':
        pose = _argv('--pose')
    if variant is None and os.path.basename(sys.argv[0]) == 'preview.py':
        variant = _argv('--variant')
    m.visible = visible_set(variant, pose)
    m.builder = B
    return m


DEFAULT_MAT = make_mat('normal')
VARIANT_MATS = {'normal': DEFAULT_MAT, 'poseida': make_mat('poseida'), 'rota': make_mat('rota')}
FOCUS = 'head'


# ------------------------------------------------------------------ poses
# Authored as targets and solved (python3 tools/models/ent_nona.py --write-poses rewrites the generated POSES block
# at the end of this file; edit POSE_TARGETS, not that block).  Per pose:
#   'add': bone -> degrees added to the rest rotation       'off': bone -> (dx, dy, dz) texels (parent frame)
#   'ik':  (side, wrist, palm, fingers, elbow_hint)  wrist / elbow_hint = (ref_bone, point in that bone's frame)
#          evaluated in the posed rig; palm = world direction the palm faces, fingers = world direction they point.
# Hand frame: fingers along local +Y, palm normal local -Z, thumb on the outer side.
# Every solved Euler component stays within LIMIT degrees of rest (the linear blend of HauntModel.apply() then never
# corkscrews an arm); pose_report() prints the largest delta of each pose.
LIMIT = 105.0
# seated: thighs forward, shins down; the skirt front lies over the lap with the hem folded at the knees; the back
# of the skirt lies flat on the cushion under her (it ends ON the cushion top, y 17 seated)
SIT_ADD = {'right_leg': (-90, 0, 0), 'left_leg': (-90, 0, 0), 'right_shin': (90, 0, 0), 'left_shin': (90, 0, 0),
           'skirt_front': (-85, 0, 0), 'skirt_hem': (86, 0, 0), 'skirt_back': (-95, 0, 0)}
SIT_OFF = {'body': (0, SIT_DY, 0), 'skirt_front': (0, 2.5, 0.5), 'skirt_hem': (0, -6.0, 0.0),
           'skirt_back': (0, 0.0, 5.0)}
FLOAT_DY = -14.0     # the rocker floats 14 texels (7 px) off the floor in the 1961 room


def _merge(*ds):
    out = {}
    for d in ds:
        for k, v in d.items():
            if k in out:
                out[k] = tuple(out[k][i] + v[i] for i in range(3))
            else:
                out[k] = tuple(v)
    return out


def seated(add=None, off=None, ik=None, float_=False, tilt=0.0):
    a = _merge(SIT_ADD, add or {})
    o = _merge(SIT_OFF, off or {})
    if float_:
        o = _merge(o, {'base': (0, FLOAT_DY, 0)})
    if tilt:
        a = _merge(a, {'base': (tilt, 0, 0)})
    return {'add': a, 'off': o, 'ik': ik or []}


ARMREST = {s: ('rocker', (9.0 * sx, -17.2, -6.5)) for s, sx in (('right', -1), ('left', 1))}
# scream_dentures: the claws frame the face out in front of it (body frame, seated): x +-16, brow level, z -14
SCREAM_WRIST = ((-13.5, -21.0, -13.5), (13.5, -21.0, -13.5))
SCREAM_ELBOW = ((-18.0, -14.0, -6.0), (18.0, -14.0, -6.0))
POSE_TARGETS = {
    # the default with the walker (rest = hands on the grips): head cocked, sweet brows
    'stand_walker': {'add': {'head': (0, 0, 7), 'right_brow': (0, 0, -4), 'left_brow': (0, 0, 4)}},
    # 'Queres un mate, nene?': the right hand holds the gourd out over the walker, palm up; the left stays on its grip
    'offer_mate': {
        'add': {'chest': (-6, -10, 0), 'neck': (0, -6, 0), 'head': (8, 6, 9), 'jaw': (7, 0, 0),
                'right_brow': (0, 0, -7), 'left_brow': (0, 0, 7)},
        'ik': [('right', ('body', (-6.0, -10.0, -14.5)), (0.1, -1.0, 0.1), (0.25, 0.1, -1.0), ('body', (-12, -9, -8)))],
    },
    # straight, furious, fists on her hips ('jarras'), chin up
    'stand_no_walker': {
        'add': {'chest': (-17, 0, 0), 'neck': (-10, 0, 0), 'head': (16, 0, 0), 'jaw': (12, 0, 0),
                'right_brow': (0, 0, 28), 'left_brow': (0, 0, -28)},
        'off': {'right_brow': (0, 0.5, 0), 'left_brow': (0, 0.5, 0)},
        'off': {'right_brow': (0, 0.5, 0), 'left_brow': (0, 0.5, 0), 'right_arm': (0, -1.0, 0), 'left_arm': (0, -1.0, 0)},
        'ik': [('right', ('body', (-9.0, -8.0, -3.0)), (1, 0, 0.3), (0.2, 0.6, 0.75), ('body', (-18, -11, 1))),
               ('left', ('body', (9.0, -8.0, -3.0)), (-1, 0, 0.3), (-0.2, 0.6, 0.75), ('body', (18, -11, 1)))],
    },
    # 'SALI DE MI NIETA, ATORRANTE!': overhand wind-up, the chancleta cocked behind her head, the left arm aiming
    'throw_chancleta': {
        'add': {'body': (0, 22, 0), 'right_leg': (0, -22, 0), 'left_leg': (0, -22, 0), 'chest': (-14, 0, 6),
                'neck': (-6, -10, 0), 'head': (10, -16, -6), 'jaw': (24, 0, 0),
                'right_brow': (0, 0, 28), 'left_brow': (0, 0, -28)},
        'off': {'right_brow': (0, 0.5, 0), 'left_brow': (0, 0.5, 0)},
        'ik': [('right', ('body', (-15.5, -20.5, -5.0)), (0.3, 0.2, -0.95), (-0.25, -1.0, 0.15), ('body', (-15.0, -13.0, 0.0))),
               ('left', ('body', (8.0, -15.0, -14.0)), (-0.2, 0.9, -0.2), (0.1, -0.2, -1.0), ('body', (12, -11, -7)))],
    },
    # in the rocker, knitting: the needles cross over the lap, head bowed over the work
    'knit_sit': seated(
        add={'neck': (2, 0, 0), 'head': (7, 0, 7), 'right_brow': (0, 0, -4), 'left_brow': (0, 0, 4)},
        ik=[('right', ('body', (-4.0, -7.5, -12.0)), (0.55, 0.8, 0.1), (0.55, -0.05, -0.85), ('body', (-11, -7, -6))),
            ('left', ('body', (4.0, -7.5, -12.0)), (-0.55, 0.8, 0.1), (-0.55, -0.05, -0.85), ('body', (11, -7, -6)))]),
    # 'Damelo, nene. Esta vez lo cierro yo.': hands together over Ofelia on her lap, tender
    'sew_calm': seated(
        add={'neck': (8, 0, 0), 'head': (16, 0, 10), 'right_brow': (0, 0, -8), 'left_brow': (0, 0, 8)},
        ik=[('right', ('body', (-1.6, -6.5, -10.5)), (0.25, 0.95, -0.1), (0.5, 0.2, -0.85), ('body', (-11, -6, -6))),
            ('left', ('body', (1.9, -6.0, -9.5)), (-0.3, 0.95, -0.1), (-0.6, 0.25, -0.75), ('body', (11, -6, -5)))]),
    # the finale: floating in the rocker, hands over the armrest ends, head cocked, staring (Ofelia on the lap)
    'float_rock': seated(
        add={'neck': (4, 0, 0), 'head': (4, 0, 15), 'jaw': (5, 0, 0), 'right_brow': (0, 0, -6), 'left_brow': (0, 0, 6)},
        ik=[('right', ARMREST['right'], (0, 1, 0), (0, 0.45, -0.9), ('rocker', (-12.5, -21, -1))),
            ('left', ARMREST['left'], (0, 1, 0), (0, 0.45, -0.9), ('rocker', (12.5, -21, -1)))],
        float_=True, tilt=-5),
    # red yarn shooting from both hands across the room: arms flung out wide, head thrown back, mouth open
    'yarn_cast': seated(
        add={'chest': (-12, 0, 0), 'neck': (-8, 0, 0), 'head': (-10, 0, 0), 'jaw': (22, 0, 0),
             'right_brow': (0, 0, -10), 'left_brow': (0, 0, 10)},
        off={'right_brow': (0, -1.0, 0), 'left_brow': (0, -1.0, 0)},
        ik=[('right', ('body', (-16.5, -15.5, -6.0)), (-0.2, 0.0, -1.0), (-0.9, -0.4, -0.1), ('body', (-12, -18, 1))),
            ('left', ('body', (16.5, -15.5, -6.0)), (0.2, 0.0, -1.0), (0.9, -0.4, -0.1), ('body', (12, -18, 1)))],
        float_=True),
    # the jaw dislocated down to the chest, the dentures floating out in front, clawed hands raised
    'scream_dentures': seated(
        add={'chest': (-6, 0, 0), 'neck': (2, 0, 0), 'head': (-14, 0, 0), 'jaw': (30, 0, 0), 'dentures': (4, -8, 6),
             'dentures_lower': (8, 0, 0),
             'right_brow': (0, 0, -14), 'left_brow': (0, 0, 14)},
        off={'jaw': (0, 7.0, -1.0), 'right_brow': (0, -1.5, 0), 'left_brow': (0, -1.5, 0), 'dentures': (0, 4.5, 0),
             'right_arm': (0, -3.0, -2.5), 'left_arm': (0, -3.0, -2.5)},
        ik=[('right', ('body', SCREAM_WRIST[0]), (0.45, 0.0, -1.0), (0.3, -1.0, -0.35), ('body', SCREAM_ELBOW[0])),
            ('left', ('body', SCREAM_WRIST[1]), (-0.45, 0.0, -1.0), (-0.3, -1.0, -0.35), ('body', SCREAM_ELBOW[1]))],
        float_=True),
    # ---- B2 hunt poses (the 'rota' look, Act 5).  Java (NonaRotaModel) adds the stretch scales and the gait cycles.
    # listen: frozen mid-step, head cocked hard to one side, chin up, sniffing; the talons hang in front of her
    'listen': {
        'add': {'chest': (-10, 8, 0), 'neck': (-14, 22, 0), 'head': (18, 28, 34), 'jaw': (16, 0, 0),
                'right_brow': (0, 0, -10), 'left_brow': (0, 0, 10)},
        'ik': [('right', ('body', (-8.0, -3.0, -11.0)), (0.2, 1.0, -0.2), (-0.2, 0.7, -0.7), ('body', (-12, -8, -4))),
               ('left', ('body', (9.0, -6.0, -10.0)), (-0.2, 1.0, -0.3), (0.3, 0.5, -0.8), ('body', (13, -10, -4)))],
    },
    # stand_tall: the hunch straightened out, the head level, the arms hanging straight to the knees (Java scales
    # legs / spine / neck / arms up to ~2.4 blocks on top of this)
    'stand_tall': {
        'add': {'chest': (-24, 0, 0), 'neck': (-30, 0, 0), 'head': (60, 0, 0), 'jaw': (10, 0, 0)},
        'ik': [('right', ('chest', (-8.5, 3.5, 1.0)), (1, 0, 0), (0, 1, 0), ('chest', (-9, -2, 3))),
               ('left', ('chest', (8.5, 3.5, 1.0)), (-1, 0, 0), (0, 1, 0), ('chest', (9, -2, 3)))],
    },
    # neck_twist: ONLY the twist (add it on top of any body pose): the head turned 180 deg round over the shoulder
    'neck_twist': {'add': {'neck': (0, 70, 0), 'head': (0, 110, 12), 'jaw': (12, 0, 0)}},
    # crawl_spider: the Exorcist bridge -- belly up, hands and feet on the floor, the head upside down at the front
    # facing where she goes, hips the highest point (~0.45 blocks)
    'crawl_spider': {
        'add': {'base': (-90, 180, 0), 'chest': (-25, 0, 0), 'neck': (-40, 0, 0), 'head': (-10, 0, 8), 'jaw': (26, 0, 0),
                'right_leg': (55, 0, 28), 'left_leg': (55, 0, -28), 'right_shin': (38, 0, 0), 'left_shin': (38, 0, 0),
                'skirt_front': (-30, 0, 0), 'skirt_back': (40, 0, 0)},
        'off': {'base': (0, -15, 21), 'jaw': (0, 3.0, 0)},
        'ik': [('right', (14.0, 19.0, -14.0), (0, 1, 0), (0.3, 0.35, -0.9), (12.0, 6.0, -6.0)),
               ('left', (-14.0, 19.0, -14.0), (0, 1, 0), (-0.3, 0.35, -0.9), (-12.0, 6.0, -6.0))],
    },
    # ceiling_hang: upside down from the ceiling like a spider, the feet on it, the head hanging, looking down at you,
    # the talons reaching down (the model hangs inside her box: base raised 46 = the ceiling 1.44 blocks over her)
    'ceiling_hang': {
        'add': {'base': (0, 0, 180), 'head': (-55, 0, 14), 'neck': (-10, 0, 0), 'jaw': (30, 0, 0),
                'right_leg': (0, 0, -22), 'left_leg': (0, 0, 22)},
        'off': {'base': (0, -46, 0), 'jaw': (0, 4.0, 0)},
        'ik': [('right', (13.0, 16.5, -9.0), (0, 0.2, -1), (0.3, 1.0, -0.3), (15.0, 10.0, -2.0)),
               ('left', (-13.0, 16.5, -9.0), (0, 0.2, -1), (-0.3, 1.0, -0.3), (-15.0, 10.0, -2.0))],
    },
    # jumpscare: lunging at you, the jaw unhinged to the chest, the talons framing the face
    'jumpscare': {
        'add': {'chest': (6, 0, 0), 'neck': (8, 0, 0), 'head': (-22, 0, -6), 'jaw': (38, 0, 0),
                'right_brow': (0, 0, 24), 'left_brow': (0, 0, -24)},
        'off': {'jaw': (0, 8.0, -1.0)},
        'ik': [('right', ('body', (-12.0, -21.0, -15.0)), (0.3, 0.0, -1.0), (0.3, -1.0, -0.3), ('body', (-17.0, -13.0, -6.0))),
               ('left', ('body', (12.0, -21.0, -15.0)), (-0.3, 0.0, -1.0), (-0.3, -1.0, -0.3), ('body', (17.0, -13.0, -6.0)))],
    },
}
# prop -> (pose that shows it, local axis a, world direction a, local axis b, world direction b)
PROP_AIM = {
    'mate': ('offer_mate', (0, -1, 0), (0.0, -0.88, -0.48), (0, 0, -1), (0.15, 0.0, -1.0)),
    'chancleta': ('throw_chancleta', (0, 0, -1), (-0.62, -0.78, 0.05), (0, 1, 0), (0.45, -0.2, 0.85)),
    'needle_right': ('knit_sit', (0, 0, -1), (0.6, -0.42, -0.68), (0, 1, 0), (0, 1, 0)),
    'needle_left': ('knit_sit', (0, 0, -1), (-0.6, -0.42, -0.68), (0, 1, 0), (0, 1, 0)),
    'yarn_right': ('yarn_cast', (0, 1, 0), (-0.86, -0.32, -0.4), (0, 0, -1), (0, -1, 0)),
    'yarn_left': ('yarn_cast', (0, 1, 0), (0.86, -0.32, -0.4), (0, 0, -1), (0, -1, 0)),
}
POSE_ORDER = ['stand_walker', 'knit_sit', 'stand_no_walker', 'throw_chancleta', 'float_rock', 'yarn_cast',
              'scream_dentures', 'sew_calm', 'offer_mate',
              'listen', 'stand_tall', 'neck_twist', 'crawl_spider', 'ceiling_hang', 'jumpscare']


def _wrap_near(a, ref):
    return ref + ((a - ref + 180.0) % 360.0) - 180.0


def euler_near(R, ref):
    """Of the two Euler triples of R, the one closest to ref (each angle wrapped next to ref)."""
    x, y, z = _euler(R)
    best = None
    for c in ((x, y, z), (x + 180.0, 180.0 - y, z + 180.0)):
        cc = tuple(_wrap_near(c[i], ref[i]) for i in range(3))
        cost = max(abs(cc[i] - ref[i]) for i in range(3))
        if best is None or cost < best[0]:
            best = (cost, cc)
    return best[1]


def fk_rots(roots, rots, offs=None):
    """World matrices; rots = {bone: (x, y, z) degrees} overrides the rest rotation, offs = {bone: (dx, dy, dz)}."""
    offs = offs or {}
    W = {}

    def rec(b, M):
        Mb = M @ _T(np.array(b.pivot) + np.array(offs.get(b.name, (0.0, 0.0, 0.0)))) @ _RM(rots.get(b.name, b.rot))
        W[b.name] = Mb
        for c in b.children:
            rec(c, Mb)
    for r in roots:
        rec(r, np.eye(4))
    return W


def frame(dir_a, vec_a, dir_b, vec_b):
    """Rotation mapping local unit dir_a -> world vec_a exactly and local dir_b -> as close as possible to vec_b."""
    va = np.array(vec_a, float)
    va /= np.linalg.norm(va)
    vb = np.array(vec_b, float)
    vb = vb - va * np.dot(va, vb)
    vb /= np.linalg.norm(vb)
    vc = np.cross(va, vb)
    la = np.array(dir_a, float)
    lb = np.array(dir_b, float)
    lc = np.cross(la, lb)
    return np.stack([va, vb, vc], 1) @ np.stack([la, lb, lc], 1).T


def _pt(W, spec):
    if spec is None:
        return None
    if isinstance(spec[0], str):
        bn, p = spec
        return (W[bn] @ np.array([p[0], p[1], p[2], 1.0]))[:3]
    return np.array(spec, float)


def solve_arm(roots, side, wrist, hand_R, elbow_hint, rots, offs, rest, limit):
    """Arm (x, y, z) + forearm (x bend, y twist) degrees putting the wrist on `wrist` (world); the hand takes the
    rotation that makes its world orientation hand_R (the Euler triple nearest its rest).  Every delta from rest is
    kept under `limit`.  Returns {bone: rot}."""
    from scipy.optimize import minimize
    arm, fa, hand = f'{side}_arm', f'{side}_forearm', f'{side}_hand'
    r_arm, r_fa, r_hand = rest[arm], rest[fa], rest[hand]
    target = np.array(wrist, float)

    def chain(p):
        rr = dict(rots)
        rr[arm] = (p[0], p[1], p[2])
        rr[fa] = (p[3], p[4], 0.0)
        rr[hand] = r_hand
        return fk_rots(roots, rr, offs)

    def over(d, lim):
        return max(0.0, abs(d) - lim) ** 2

    def cost(p):
        W = chain(p)
        c = float(np.sum((W[hand][:3, 3] - target) ** 2))
        if elbow_hint is not None:
            c += 0.03 * float(np.sum((W[fa][:3, 3] - elbow_hint) ** 2))
        ds = [p[i] - r_arm[i] for i in range(3)] + [p[3] - r_fa[0]]
        c += sum(2e-2 * over(d, limit) + 1e-5 * d * d for d in ds)
        c += 2e-2 * over(p[4] - r_fa[1], 70) + 5e-5 * (p[4] - r_fa[1]) ** 2
        c += 0.05 * max(0.0, p[3]) ** 2 + 0.05 * max(0.0, -p[3] - 150) ** 2   # the elbow bends one way only
        e = euler_near(W[fa][:3, :3].T @ hand_R, r_hand)
        c += sum(2e-2 * over(e[i] - r_hand[i], limit) + 2e-5 * (e[i] - r_hand[i]) ** 2 for i in range(3))
        return c
    best = None
    g0 = list(r_arm) + [r_fa[0], r_fa[1]]
    starts = [g0]
    for dx, dy, dz, dfx, dt in ((-40, 0, 30, -40, 0), (-70, 30, 40, -60, 30), (-60, -30, -20, -30, -30),
                                (30, 0, 0, -50, 0), (-50, 20, -40, -40, 45), (-30, -20, 20, 20, -45),
                                (-100, 0, 0, -20, 0), (40, 30, -30, -80, 20)):
        starts.append([g0[0] + dx, g0[1] + dy, g0[2] + dz, g0[3] + dfx, g0[4] + dt])
    for g in starts:
        res = minimize(cost, g, method='Nelder-Mead', options={'xatol': 1e-4, 'fatol': 1e-10, 'maxiter': 10000})
        res = minimize(cost, res.x, method='Nelder-Mead', options={'xatol': 1e-5, 'fatol': 1e-12, 'maxiter': 10000})
        if best is None or res.fun < best.fun:
            best = res
    p = best.x
    W = chain(p)
    err = float(np.linalg.norm(W[hand][:3, 3] - target))
    if err > 0.6:
        print(f'  ! {side} wrist misses its target by {err:.2f} texels', SOLVING[0])
    return {arm: tuple(_wrap_near(p[i], r_arm[i]) for i in range(3)),
            fa: (_wrap_near(p[3], r_fa[0]), _wrap_near(p[4], r_fa[1]), 0.0),
            hand: euler_near(W[fa][:3, :3].T @ hand_R, r_hand)}


def pose_rig(name):
    """(roots, rots, offs) of the solved pose `name` (rest rotations + POSES deltas)."""
    m = build(pose=name)
    rest = {b.name: tuple(b.rot) for b in m.bones()}
    rots, offs = dict(rest), {}
    for b, t in POSES.get(name, {}).items():
        rots[b] = tuple(rest[b][i] + math.degrees(t[i]) for i in range(3))
        offs[b] = tuple(t[3:6])
    return m, rots, offs


SOLVING = ['']


def solve_poses(names=None):
    """POSE_TARGETS -> {pose: {bone: (xRot, yRot, zRot, dx, dy, dz)}} (radians / texels, added to rest)."""
    m = build(pose='__none__')
    rest = {b.name: tuple(b.rot) for b in m.bones()}
    out = {}
    for name in names or POSE_ORDER:
        SOLVING[0] = name
        spec = POSE_TARGETS[name]
        rots = dict(rest)
        for b, r in spec.get('add', {}).items():
            rots[b] = tuple(rest[b][i] + r[i] for i in range(3))
        offs = {b: tuple(o) for b, o in spec.get('off', {}).items()}
        for side, wrist, palm, fing, hint in spec.get('ik', []):
            W = fk_rots(m.roots, rots, offs)
            R = frame((0, 0, -1), palm, (0, 1, 0), fing)
            rots.update(solve_arm(m.roots, side, _pt(W, wrist), R, _pt(W, hint), rots, offs, rest, LIMIT))
        table = {}
        for b in rots:
            d = [math.radians(rots[b][i] - rest[b][i]) for i in range(3)]
            off = offs.get(b, (0, 0, 0))
            if any(abs(v) > 1e-4 for v in d) or any(abs(v) > 1e-4 for v in off):
                table[b] = tuple(round(v, 4) for v in d) + tuple(float(v) for v in off)
        for b, off in offs.items():
            table.setdefault(b, (0.0, 0.0, 0.0) + tuple(float(v) for v in off))
        out[name] = table
    return out


def solve_props(P):
    """Rest rotation (degrees) of every held prop so it points where PROP_AIM says in the pose that shows it."""
    m = build(pose='__none__')
    rest = {b.name: tuple(b.rot) for b in m.bones()}
    out = {}
    for prop_, (pose, la, wa, lb, wb) in PROP_AIM.items():
        rots, offs = dict(rest), {}
        for b, t in P[pose].items():
            rots[b] = tuple(rest[b][i] + math.degrees(t[i]) for i in range(3))
            offs[b] = tuple(t[3:6])
        rots[prop_] = (0.0, 0.0, 0.0)
        W = fk_rots(m.roots, rots, offs)
        Rp = W[prop_][:3, :3]
        out[prop_] = tuple(round(v, 2) for v in euler_near(Rp.T @ frame(la, wa, lb, wb), (0.0, 0.0, 0.0)))
    return out


def pose_report(poses):
    for name, table in poses.items():
        big = max(((abs(v), b) for b, t in table.items() for v in t[:3]), default=(0, None))
        print('%-16s max |delta| %6.1f deg (%s)' % (name, math.degrees(big[0]), big[1]))


MARK_A = '# >>> ' + 'POSES'
MARK_B = '# <<< ' + 'POSES'


def write_poses(P, props):
    lines = ['PROP_ROT = {']
    for k, v in props.items():
        lines.append("    '%s': (%s)," % (k, ', '.join('%.2f' % x for x in v)))
    lines.append('}')
    lines.append('POSES = {')
    for k, v in P.items():
        lines.append("    '%s': {" % k)
        for b, t in v.items():
            lines.append("        '%s': (%s)," % (b, ', '.join(('%.4f' % x).rstrip('0').rstrip('.') if x else '0' for x in t)))
        lines.append('    },')
    lines.append('}')
    path = os.path.abspath(__file__)
    src = open(path).read()
    a = src.index(MARK_A)
    a = src.index('\n', a) + 1
    b = src.index(MARK_B)
    open(path, 'w').write(src[:a] + '\n'.join(lines) + '\n' + src[b:])


ANIM_NOTES = """Nona Pocha (Nelida 'Pocha' Bertolotti, 73) -- grandmother, host #4 and the twist of Casa Morales.
42 bones, 144 cubes, 256x144, scale 0.5 (authored at 2x), entityCutoutNoCull.  1.5 blocks to the top of the bun, hunched.
Textures: nona.png (+ nona_eyes.png) = look 0 'normal'; nona_poseida.png (+ nona_poseida_eyes.png) = look 1 'poseida'.
Emissive layer 'eyes': normal = the glass of both round lenses glows white (lids, lashes, irises and pupils stay dark:
at night two white discs with little dark eyes -- beat casa.calma "los anteojos brillan blancos"); poseida = her right
lens still glows white but CRACKED (the three radial cracks and the ring stay dark) round a glowing blue iris and a
white glint; the left lens keeps a few dim shards round its hole, and behind it (painted on the skull) the black hole
glows with a faint ember rim and a 2x2 ember deep inside.  Emissive layers cast no light; add a dim light if needed.

BONES (pivots at the joints; right_* is on -X = the viewer's left)
  base            floor anchor (y 24) of EVERYTHING: body, walker and rocker hang from it.  Float = base dy (negative is
                  up), rock = base xRot about the floor contact.  Finale: base dy FLOAT_DY (-14) is already in the
                  floating poses; add a bob dy +-0.8 sin(t 0.06) and the rock xRot 0.09 sin(t 0.08) on top.
  body            hips (pivot at the hip joints): cardigan hem, pocket panels and the bulging patch pocket on her right
                  hip.  Walk: tiny zRot sway +-0.03.
  skirt_front > skirt_hem   front of the floral dress and its hinged hem.  Walk: skirt_front xRot 0.25 x the forward leg
                  swing; skirt_hem follows at 0.5 x skirt_front (secondary).  Seated poses lay skirt_front over the lap
                  and fold skirt_hem down at the knees (in the tables).
  skirt_back      back of the dress.  Walk: xRot 0.2 x |swing|.  Seated poses lay it flat ON the cushion under her (it
                  ends on the cushion top, never through the seat).
  right_leg > right_shin > right_slipper, left_leg > left_shin   thick stockings and tartan felt slippers (red
                  pompoms).  Toes out 9 deg.  Walk: HauntModel.walk(s, "left_leg", "right_leg", null arms, 0.35, 0):
                  she shuffles (small amplitude, slow).  right_slipper is the chancleta she pulls off (toggle).
  chest           hunched 22 deg from the waist, dowager's hump, open cardigan, lace collar, pearl necklace.
                  Idle: breathe xRot +-0.025 sin(t 0.08).
  neck / head     the head juts forward and tips up to look at you: HauntModel.look(s, 0.35).  Idle: slow zRot
                  tilt +-0.06 sin(t 0.035) (the deaf "que?" tilt); every 4-6 s a quick yRot glance +-0.2 over 6 ticks.
                  The head carries the perm (shell, rounded crown, fringe roll, ear puffs), the nose, rouge apples,
                  jowls, ears with pearl earrings and the hearing aid on her right ear.
  jaw             mouth hinge (toothless gums inside: her teeth are the dentures).  Talk: xRot 0.04..0.22 driven by
                  the voice amplitude.  The hidden throat box + two stretched skin flaps travel with it, so the jaw can
                  drop by dy +7 (dislocated, scream_dentures) without opening a hole.
  right_brow / left_brow   pencilled brows on top of the frames, rest tilt 12 deg inner-up (sweet).  zRot adds
                  expression (right_brow +0.45 / left_brow -0.45 = furious, the opposite = worried); dy -1..-1.5 lifts.
  glasses         the two round 10x10 tortoiseshell lenses (2 deep, wider than her face), bridge, temples into the ear
                  puffs and the beaded chain (cadenita).  Fixed to the head; a 0.05 zRot jiggle on footsteps sells the
                  weight.
  bun             the grey stepped-dome bun under a hairnet on the back of the crown (two bobby pins).  Toggle (hidden
                  in 'poseida').
  dentures > dentures_lower   floating dentures: 7x2x3 plates (pink gum band, three front teeth and dark molars with
                  dark gaps), parked at nose height 8 texels in front of the face, tilted so both rows face you; the
                  lower plate is hinged at the back of the upper one.  Toggle.  Animate a clack: dentures_lower xRot
                  +0.35 abs(sin(t 0.45)); a drift dy +-0.6 sin(t 0.1), yRot +-0.15 sin(t 0.07).
  hair_loose_0..4 possessed only: the bun undone into long white tresses drifting as if under water -- 0 rises off the
                  crown and curls over to her left, 1 / 2 drift out sideways and down past the shoulders, 3 / 4 droop
                  down the back.  Each bone = two crossed planes of one S-curved tapering tress (grey root, white body,
                  one wet highlight).  None reaches back into the rocker in any seated pose.  Always animate SLOW and
                  LARGE, out of phase per bone k: xRot += 0.10 sin(t 0.05 + 1.3k), zRot += 0.14 sin(t 0.037 + 0.9k),
                  yRot += 0.06 sin(t 0.03 + 2.1k) (ripple("hair_loose_", t, 0.05, 1.3, 0.14, 0.10, 0) is equivalent).
  right_arm > right_forearm > right_hand   holds the props: mate, chancleta, needle_right, yarn_right.
  left_arm > left_forearm > left_hand      holds needle_left (+ the knitted swatch) and yarn_left; a grey tissue is
                  tucked into the left cuff.  Each hand = palm, three separate fingers (wedding ring on the left), thumb
                  and a claw plane of long dark nails that only the 'poseida' texture paints (transparent in 'normal').
                  Rest = both hands on the walker grips.  With the walker: arms swing 0 (they push the walker);
                  without it: walk arms amplitude 0.2.
  mate            the gourd (warm brown, highlight, pyrographed band), silver virola heaped with green yerba, the
                  bombilla.  Held in the right hand, tilted toward you.  Toggle.
  chancleta       the tartan slipper with its red pompom and dark treaded rubber sole, held in the right hand.  Toggle.
  needle_right / needle_left   knitting needles (the left one carries the red swatch).  Toggles.
  yarn_right / yarn_left   30-texel strands of red yarn shooting from the hands.  Toggles.
  yarn_ball       the red wound wool ball half sunk in her right cardigan pocket, its loose end draping off sideways
                  over the pocket.  Fixed (can bob 0.03 with steps).
  walker > walker_wheel   aluminium walker: U frame, front wheels, cut tennis balls on the back legs, a soft
                  granny-square bag (sagging bottom, two cord loops over the front bar) with the knitting poking out.
                  The walker moves with her (part of the model).  walker_wheel is THE squeaky wheel (her right front
                  wheel): spin xRot += distance moved / 2.5 per tick and play andador.squeak every half turn.  Toggle.
  rocker > rocker_back    light-oak rocking chair: runners curving up at both ends, short legs (arm posts and back
                  stiles run down to the runners), thin seat, cushion crocheted cream with red popcorn stitches, arm
                  rests, spindle back, lace doily on the crest.  Toggle.  It rocks with base xRot (see base), never on
                  its own.

TOGGLES (ModelPart.visible).  Default look 'normal' at rest: walker, bun, right_slipper visible; everything else hidden.
  walker          visible by default; hidden in stand_no_walker, throw_chancleta and every seated pose.
  rocker          hidden by default; visible in the seated poses knit_sit, float_rock, yarn_cast, scream_dentures,
                  sew_calm.
  bun             visible in 'normal'; hidden in 'poseida' (look 1).
  hair_loose_0..4 hidden in 'normal'; visible in 'poseida' (look 1).
  dentures (+ dentures_lower)   hidden; visible only in scream_dentures (normally with 'poseida').
  right_slipper   visible; hidden in throw_chancleta (the stocking foot shows) -- the chancleta is now in her hand.
  chancleta       hidden; visible in throw_chancleta.  On release hide it and spawn the slipper projectile at the
                  right_hand world position.
  mate            hidden; visible in offer_mate.
  needle_right, needle_left (+ the knitted swatch)   hidden; visible in knit_sit.
  yarn_right, yarn_left   hidden; visible in yarn_cast.  Scale them with yScale 0..1 over 4 ticks when the pose starts
                  (the yarn shoots out), then the BlockDisplay web takes over (section 3.6 of the bible).
  (claws are not a toggle: the claw planes are always there, painted only in the 'poseida' texture.)
  Prop rest rotations (PROP_ROT) are pre-solved for the pose that shows each prop -- just show it.
  The preview / gallery JSON carries 'toggles' {default, variants, poses}; cubes of hidden toggle bones are kept
  under 'hidden_cubes'.  preview.py shows the toggles of --variant / --pose; NONA_SHOW=all|bone,bone forces them on.

POSES (additive tables POSE_<NAME>; radians / texels on top of the rest pose).  They are mutually exclusive: cross-fade
between them (weights sum to 1, 5-8 ticks; 3 ticks for the throw and the scream).  Seated poses already contain the
sit (hips drop 5, thighs forward, skirt over the lap, back skirt on the cushion) and the finale ones the float
(base dy -14).  Arm and hand deltas stay within 105 deg of rest (solved with that limit), so the linear blend never
corkscrews; the only bigger single-axis deltas are the seated skirt folds (skirt_back -95 deg about X).
  stand_walker    default with the walker: hands on the grips, head cocked, sweet brows.  Walk with it (walker_wheel
                  spins and squeaks).  Beats casa.llegada / casa.calma.
  offer_mate      "Queres un mate, nene?": the right hand holds the gourd out over the walker, tilted so you see the
                  yerba; the left stays on its grip; head tilted, jaw open a little.  Show 'mate'.  Bob the mate dy
                  +-0.3 while she talks.
  knit_sit        in the rocker (rocker visible, walker hidden), knitting: needles crossed over the lap, swatch hanging,
                  head bowed over the work.  Add the knitting loop: right_hand xRot +-0.18 sin(t 0.5), left_hand xRot
                  +-0.12 sin(t 0.5 + 1.6); slow rock (base xRot 0.06 sin(t 0.07)).
  stand_no_walker straight and furious, fists on her hips ('jarras': wrists on the front of the waist, elbows out, a
                  slight shoulder lift -- the angry teapot), chin up, brows down, mouth open.  Beat casa.chancleta (she
                  arrives WITHOUT the walker).  Add a scolding head shake yRot +-0.12 sin(t 0.6).
  throw_chancleta "SALI DE MI NIETA, ATORRANTE!": overhand wind-up, the chancleta cocked up beside her head (outside the
                  hair puff, tartan upper and pompom toward you), left arm aiming, body twisted back.  Release: blend
                  out in 3 ticks while adding right_arm xRot -1.6 / right_forearm xRot +0.8 for 2 ticks (the snap),
                  hide 'chancleta', spawn the projectile.
  float_rock      finale (casa.nona): floating sitting in the rocker in the 1961 room, hands over the arm-rest ends,
                  head cocked, staring; Ofelia sits on her lap (the doll entity, seated on the lap at ~(0, -3, -4) in
                  the body bone's frame).  Add the bob and the rock (see base) and the hair ripple.  Look: 'poseida'.
  yarn_cast       the red yarn shoots across the room: arms flung out, head thrown back, mouth open, yarn_* shown.
                  Hold while the yarn web spawns; tremble the hands zRot +-0.05 sin(t 1.7).
  scream_dentures the jaw dislocated down to the chest (jaw dy +7, xRot +0.52), the head thrown back, the dentures shown
                  floating between the nose and the black throat, the clawed hands raised in front of the face edges
                  (shoulders shrugged up 3).  Fast blend in (3 ticks) + jumpscare; add the dentures clack (see above).
  sew_calm        "Damelo, nene. Esta vez lo cierro yo." / the last stitch: seated, hands together over Ofelia on her
                  lap, head bowed tenderly.  Used for the calm ending ("Sesenta y cinco anos esperando...") in either
                  look; lower the float to base dy 0 over 60 ticks while she comes down.

LOOKS (VARIANT_MATS, Java picks by the entity's variant index)
  0 normal   powdered pink skin, rouge apples, a small closed smile with a coral lower lip, a mole by her left mouth
             corner, lavender-grey curly perm and netted bun, sweet magnified brown eyes behind glowing white lenses.
  1 poseida  bloodless grey-lilac skin a step darker (sunken sockets, temples and cheeks, one forked temple vein),
             bleached white hair (bun hidden, hair_loose shown), long dark nails; the right lens cracked in a spider web
             over a glassy blue doll's eye (still glowing), the left blown out on a black hole with an ember, weeping one
             black tear down the cheek, the jaw and the neck (rhymes with Ofelia's broken eye).
"""


# >>> POSES (generated: python3 tools/models/ent_nona.py --write-poses; edit POSE_TARGETS, not this block)
PROP_ROT = {
    'mate': (123.13, 11.08, 7.09),
    'chancleta': (117.19, -32.77, -42.61),
    'needle_right': (85.01, 150.63, 15.97),
    'needle_left': (85.01, -150.63, -15.97),
    'yarn_right': (-108.64, 53.75, -114.87),
    'yarn_left': (-108.64, -53.75, 114.87),
}
POSES = {
    'stand_walker': {
        'head': (0, 0, 0.1222, 0, 0, 0),
        'right_brow': (0, 0, -0.0698, 0, 0, 0),
        'left_brow': (0, 0, 0.0698, 0, 0, 0),
    },
    'knit_sit': {
        'body': (0, 0, 0, 0, 5, 0),
        'skirt_front': (-1.4835, 0, 0, 0, 2.5, 0.5),
        'skirt_hem': (1.501, 0, 0, 0, -6, 0),
        'skirt_back': (-1.6581, 0, 0, 0, 0, 5),
        'right_leg': (-1.5708, 0, 0, 0, 0, 0),
        'right_shin': (1.5708, 0, 0, 0, 0, 0),
        'left_leg': (-1.5708, 0, 0, 0, 0, 0),
        'left_shin': (1.5708, 0, 0, 0, 0, 0),
        'neck': (0.0349, 0, 0, 0, 0, 0),
        'head': (0.1222, 0, 0.1222, 0, 0, 0),
        'right_brow': (0, 0, -0.0698, 0, 0, 0),
        'left_brow': (0, 0, 0.0698, 0, 0, 0),
        'right_arm': (-1.1189, 0.2738, 1.7491, 0, 0, 0),
        'right_forearm': (0.6626, -0.3212, 0, 0, 0, 0),
        'right_hand': (-0.1469, -0.8364, 0.5255, 0, 0, 0),
        'left_arm': (-1.1189, -0.2738, -1.7491, 0, 0, 0),
        'left_forearm': (0.6626, 0.3212, 0, 0, 0, 0),
        'left_hand': (-0.1469, 0.8364, -0.5255, 0, 0, 0),
    },
    'stand_no_walker': {
        'chest': (-0.2967, 0, 0, 0, 0, 0),
        'neck': (-0.1745, 0, 0, 0, 0, 0),
        'head': (0.2793, 0, 0, 0, 0, 0),
        'right_brow': (0, 0, 0.4887, 0, 0.5, 0),
        'left_brow': (0, 0, -0.4887, 0, 0.5, 0),
        'jaw': (0.2094, 0, 0, 0, 0, 0),
        'right_arm': (0.5507, -0.781, 0.1571, 0, -1, 0),
        'right_forearm': (-0.8441, -0.1314, 0, 0, 0, 0),
        'right_hand': (-0.1926, -0.5289, -1.2709, 0, 0, 0),
        'left_arm': (0.5507, 0.781, -0.1571, 0, -1, 0),
        'left_forearm': (-0.8441, 0.1314, 0, 0, 0, 0),
        'left_hand': (-0.1926, 0.5289, 1.2709, 0, 0, 0),
    },
    'throw_chancleta': {
        'body': (0, 0.384, 0, 0, 0, 0),
        'right_leg': (0, -0.384, 0, 0, 0, 0),
        'left_leg': (0, -0.384, 0, 0, 0, 0),
        'chest': (-0.2443, 0, 0.1047, 0, 0, 0),
        'neck': (-0.1047, -0.1745, 0, 0, 0, 0),
        'head': (0.1745, -0.2793, -0.1047, 0, 0, 0),
        'right_brow': (0, 0, 0.4887, 0, 0.5, 0),
        'left_brow': (0, 0, -0.4887, 0, 0.5, 0),
        'jaw': (0.4189, 0, 0, 0, 0, 0),
        'right_arm': (0.5154, 0.7502, 0.8947, 0, 0, 0),
        'right_forearm': (0.2815, 0.0674, 0, 0, 0, 0),
        'right_hand': (-1.2054, -1.0967, 0.8743, 0, 0, 0),
        'left_arm': (-0.612, -0.2803, -1.6652, 0, 0, 0),
        'left_forearm': (0.6616, 0.3033, 0, 0, 0, 0),
        'left_hand': (-0.5093, 1.0672, 0.4426, 0, 0, 0),
    },
    'float_rock': {
        'base': (-0.0873, 0, 0, 0, -14, 0),
        'body': (0, 0, 0, 0, 5, 0),
        'skirt_front': (-1.4835, 0, 0, 0, 2.5, 0.5),
        'skirt_hem': (1.501, 0, 0, 0, -6, 0),
        'skirt_back': (-1.6581, 0, 0, 0, 0, 5),
        'right_leg': (-1.5708, 0, 0, 0, 0, 0),
        'right_shin': (1.5708, 0, 0, 0, 0, 0),
        'left_leg': (-1.5708, 0, 0, 0, 0, 0),
        'left_shin': (1.5708, 0, 0, 0, 0, 0),
        'neck': (0.0698, 0, 0, 0, 0, 0),
        'head': (0.0698, 0, 0.2618, 0, 0, 0),
        'right_brow': (0, 0, -0.1047, 0, 0, 0),
        'left_brow': (0, 0, 0.1047, 0, 0, 0),
        'jaw': (0.0873, 0, 0, 0, 0, 0),
        'right_arm': (0.0202, -0.3731, 0.6807, 0, 0, 0),
        'right_forearm': (-0.7514, -0.1596, 0, 0, 0, 0),
        'right_hand': (1.5335, -1.8379, -1.3772, 0, 0, 0),
        'left_arm': (0.0202, 0.3731, -0.6807, 0, 0, 0),
        'left_forearm': (-0.7514, 0.1596, 0, 0, 0, 0),
        'left_hand': (1.5335, 1.8379, 1.3772, 0, 0, 0),
    },
    'yarn_cast': {
        'base': (0, 0, 0, 0, -14, 0),
        'body': (0, 0, 0, 0, 5, 0),
        'skirt_front': (-1.4835, 0, 0, 0, 2.5, 0.5),
        'skirt_hem': (1.501, 0, 0, 0, -6, 0),
        'skirt_back': (-1.6581, 0, 0, 0, 0, 5),
        'right_leg': (-1.5708, 0, 0, 0, 0, 0),
        'right_shin': (1.5708, 0, 0, 0, 0, 0),
        'left_leg': (-1.5708, 0, 0, 0, 0, 0),
        'left_shin': (1.5708, 0, 0, 0, 0, 0),
        'chest': (-0.2094, 0, 0, 0, 0, 0),
        'neck': (-0.1396, 0, 0, 0, 0, 0),
        'head': (-0.1745, 0, 0, 0, 0, 0),
        'right_brow': (0, 0, -0.1745, 0, -1, 0),
        'left_brow': (0, 0, 0.1745, 0, -1, 0),
        'jaw': (0.384, 0, 0, 0, 0, 0),
        'right_arm': (0.5859, -0.1719, 1.1017, 0, 0, 0),
        'right_forearm': (-0.0561, -0.0715, 0, 0, 0, 0),
        'right_hand': (0.4069, -0.6204, 0.3932, 0, 0, 0),
        'left_arm': (0.5859, 0.1719, -1.1017, 0, 0, 0),
        'left_forearm': (-0.0561, 0.0715, 0, 0, 0, 0),
        'left_hand': (0.4069, 0.6204, -0.3932, 0, 0, 0),
    },
    'scream_dentures': {
        'base': (0, 0, 0, 0, -14, 0),
        'body': (0, 0, 0, 0, 5, 0),
        'skirt_front': (-1.4835, 0, 0, 0, 2.5, 0.5),
        'skirt_hem': (1.501, 0, 0, 0, -6, 0),
        'skirt_back': (-1.6581, 0, 0, 0, 0, 5),
        'right_leg': (-1.5708, 0, 0, 0, 0, 0),
        'right_shin': (1.5708, 0, 0, 0, 0, 0),
        'left_leg': (-1.5708, 0, 0, 0, 0, 0),
        'left_shin': (1.5708, 0, 0, 0, 0, 0),
        'chest': (-0.1047, 0, 0, 0, 0, 0),
        'neck': (0.0349, 0, 0, 0, 0, 0),
        'head': (-0.2443, 0, 0, 0, 0, 0),
        'right_brow': (0, 0, -0.2443, 0, -1.5, 0),
        'left_brow': (0, 0, 0.2443, 0, -1.5, 0),
        'jaw': (0.5236, 0, 0, 0, 7, -1),
        'dentures': (0.0698, -0.1396, 0.1047, 0, 4.5, 0),
        'dentures_lower': (0.1396, 0, 0, 0, 0, 0),
        'right_arm': (0.0732, 0.75, 0.9322, 0, -3, -2.5),
        'right_forearm': (0.33, -0.0422, 0, 0, 0, 0),
        'right_hand': (-0.833, -1.5825, 1.3208, 0, 0, 0),
        'left_arm': (0.0732, -0.75, -0.9322, 0, -3, -2.5),
        'left_forearm': (0.33, 0.0422, 0, 0, 0, 0),
        'left_hand': (-0.833, 1.5825, -1.3208, 0, 0, 0),
    },
    'sew_calm': {
        'body': (0, 0, 0, 0, 5, 0),
        'skirt_front': (-1.4835, 0, 0, 0, 2.5, 0.5),
        'skirt_hem': (1.501, 0, 0, 0, -6, 0),
        'skirt_back': (-1.6581, 0, 0, 0, 0, 5),
        'right_leg': (-1.5708, 0, 0, 0, 0, 0),
        'right_shin': (1.5708, 0, 0, 0, 0, 0),
        'left_leg': (-1.5708, 0, 0, 0, 0, 0),
        'left_shin': (1.5708, 0, 0, 0, 0, 0),
        'neck': (0.1396, 0, 0, 0, 0, 0),
        'head': (0.2793, 0, 0.1745, 0, 0, 0),
        'right_brow': (0, 0, -0.1396, 0, 0, 0),
        'left_brow': (0, 0, 0.1396, 0, 0, 0),
        'right_arm': (-0.193, 0.1315, -1.8327, 0, 0, 0),
        'right_forearm': (0.6638, 0.3419, 0, 0, 0, 0),
        'right_hand': (-0.0038, 0.8589, -0.0449, 0, 0, 0),
        'left_arm': (-0.1394, -0.0821, 1.6519, 0, 0, 0),
        'left_forearm': (0.6631, -0.2723, 0, 0, 0, 0),
        'left_hand': (-0.1089, -1.0415, 0.2814, 0, 0, 0),
    },
    'offer_mate': {
        'chest': (-0.1047, -0.1745, 0, 0, 0, 0),
        'neck': (0, -0.1047, 0, 0, 0, 0),
        'head': (0.1396, 0.1047, 0.1571, 0, 0, 0),
        'right_brow': (0, 0, -0.1222, 0, 0, 0),
        'left_brow': (0, 0, 0.1222, 0, 0, 0),
        'jaw': (0.1222, 0, 0, 0, 0, 0),
        'right_arm': (-0.6119, 0.113, 0.0415, 0, 0, 0),
        'right_forearm': (0.521, -0.0061, 0, 0, 0, 0),
        'right_hand': (-1.2668, -0.1021, -0.0578, 0, 0, 0),
    },
    'listen': {
        'chest': (-0.1745, 0.1396, 0, 0, 0, 0),
        'neck': (-0.2443, 0.384, 0, 0, 0, 0),
        'head': (0.3142, 0.4887, 0.5934, 0, 0, 0),
        'right_brow': (0, 0, -0.1745, 0, 0, 0),
        'left_brow': (0, 0, 0.1745, 0, 0, 0),
        'jaw': (0.2793, 0, 0, 0, 0, 0),
        'right_arm': (-1.2287, -0.2912, 1.4421, 0, 0, 0),
        'right_forearm': (0.6506, -0.3602, 0, 0, 0, 0),
        'right_hand': (0.1778, -0.9395, -0.1045, 0, 0, 0),
        'left_arm': (-0.5237, 0.4997, -0.7781, 0, 0, 0),
        'left_forearm': (0.5123, 0.2852, 0, 0, 0, 0),
        'left_hand': (0.2722, 1.3833, 0.003, 0, 0, 0),
    },
    'stand_tall': {
        'chest': (-0.4189, 0, 0, 0, 0, 0),
        'neck': (-0.5236, 0, 0, 0, 0, 0),
        'head': (1.0472, 0, 0, 0, 0, 0),
        'jaw': (0.1745, 0, 0, 0, 0, 0),
        'right_arm': (0.0222, -1.4943, 0.0647, 0, 0, 0),
        'right_forearm': (0.4645, -0.1038, 0, 0, 0, 0),
        'right_hand': (-0.7932, -0.748, 0.0534, 0, 0, 0),
        'left_arm': (0.0222, 1.4943, -0.0647, 0, 0, 0),
        'left_forearm': (0.4645, 0.1038, 0, 0, 0, 0),
        'left_hand': (-0.7932, 0.748, -0.0534, 0, 0, 0),
    },
    'neck_twist': {
        'neck': (0, 1.2217, 0, 0, 0, 0),
        'head': (0, 1.9199, 0.2094, 0, 0, 0),
        'jaw': (0.2094, 0, 0, 0, 0, 0),
    },
    'crawl_spider': {
        'base': (-1.5708, 3.1416, 0, 0, -15, 21),
        'skirt_front': (-0.5236, 0, 0, 0, 0, 0),
        'skirt_back': (0.6981, 0, 0, 0, 0, 0),
        'right_leg': (0.9599, 0, 0.4887, 0, 0, 0),
        'right_shin': (0.6632, 0, 0, 0, 0, 0),
        'left_leg': (0.9599, 0, -0.4887, 0, 0, 0),
        'left_shin': (0.6632, 0, 0, 0, 0, 0),
        'chest': (-0.4363, 0, 0, 0, 0, 0),
        'neck': (-0.6981, 0, 0, 0, 0, 0),
        'head': (-0.1745, 0, 0.1396, 0, 0, 0),
        'jaw': (0.4538, 0, 0, 0, 3, 0),
        'right_arm': (1.6531, 0.5683, 1.833, 0, 0, 0),
        'right_forearm': (0.547, 0.6438, 0, 0, 0, 0),
        'right_hand': (0.3902, 1.4377, 0.5266, 0, 0, 0),
        'left_arm': (1.6531, -0.5683, -1.833, 0, 0, 0),
        'left_forearm': (0.547, -0.6438, 0, 0, 0, 0),
        'left_hand': (0.3902, -1.4377, -0.5266, 0, 0, 0),
    },
    'ceiling_hang': {
        'base': (0, 0, 3.1416, 0, -46, 0),
        'right_leg': (0, 0, -0.384, 0, 0, 0),
        'left_leg': (0, 0, 0.384, 0, 0, 0),
        'neck': (-0.1745, 0, 0, 0, 0, 0),
        'head': (-0.9599, 0, 0.2443, 0, 0, 0),
        'jaw': (0.5236, 0, 0, 0, 4, 0),
        'right_arm': (0.5456, 0.0328, 1.8334, 0, 0, 0),
        'right_forearm': (0.6497, -0.1491, 0, 0, 0, 0),
        'right_hand': (0.049, -0.5205, 0.2697, 0, 0, 0),
        'left_arm': (0.5456, -0.0328, -1.8334, 0, 0, 0),
        'left_forearm': (0.6497, 0.1491, 0, 0, 0, 0),
        'left_hand': (0.049, 0.5205, -0.2697, 0, 0, 0),
    },
    'jumpscare': {
        'chest': (0.1047, 0, 0, 0, 0, 0),
        'neck': (0.1396, 0, 0, 0, 0, 0),
        'head': (-0.384, 0, -0.1047, 0, 0, 0),
        'right_brow': (0, 0, 0.4189, 0, 0, 0),
        'left_brow': (0, 0, -0.4189, 0, 0, 0),
        'jaw': (0.6632, 0, 0, 0, 8, -1),
        'right_arm': (0.2642, 0.2373, 1.8332, 0, 0, 0),
        'right_forearm': (0.6622, -0.2598, 0, 0, 0, 0),
        'right_hand': (0.2108, -0.9485, 0.7, 0, 0, 0),
        'left_arm': (0.2642, -0.2373, -1.8332, 0, 0, 0),
        'left_forearm': (0.6622, 0.2598, 0, 0, 0, 0),
        'left_hand': (0.2108, 0.9485, -0.7, 0, 0, 0),
    },
}
# <<< POSES


if __name__ == '__main__':
    if '--write-poses' in sys.argv:
        only = _argv('--write-poses')
        if only and not only.startswith('-'):
            P = dict(POSES)
            P.update(solve_poses(only.split(',')))
            P = {k: P[k] for k in POSE_ORDER}
        else:
            P = solve_poses()
        pose_report(P)
        props = solve_props(P)
        print(props)
        write_poses(P, props)
        print('POSES written')
