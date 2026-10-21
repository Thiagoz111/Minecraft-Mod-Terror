"""Jorge Morales (46) -- dad, 'rey del asado', host #2 of AZAMEL (DEAD LINE, case 'casa').

Authored at 2x texel density (model.scale = 0.5).  +Y down, ground y = 24, faces -Z, right_* on -X.  Centred on
x = 0, z = 0.  Height 1.9 blocks: top of the hair tuft y = -38 -> soles y = 24 (62 texels incl. the tuft, skull
top -37).  See build() for the cube / bone count; texture 256 x 256.

Design sketch
-------------
Silhouette: a PEAR on flip-flops.  Normal shoulders (22 + short sleeves), then a beer belly that is the widest and
deepest thing on him (24 wide, sticking out 7 texels in front of the chest in three rounded steps), a black apron
that rides over the belly and then FALLS STRAIGHT DOWN from it like a curtain (a hanging panel 7 texels in front of
the thighs -- the classic dad profile), khaki bermudas that only show at the sides and the hem, two thin hairy
shins, and blue ojotas with the toes out (duck stance).  A big head (16 x 17 face, a quarter of his height) with no
neck: the double chin sits on the shirt collar.  The tongs in his right fist are the only spike in the outline.

Proportions (texels at 2x): head 17 (crown -37 .. chin -20), torso 22 (shoulders -19 .. hips 3), legs 21 (hips
3 .. soles 24).  Shoulders 22 wide, belly 24, the apron front 21-23.

Face (front 16 x 17, hand-placed in the FACE grid, painted by the material so every look recolours it):
a tall forehead with two furrows and a sweaty shine (receding hairline: bald temples, one combed tuft standing
forward), two bushy brow blocks, droopy friendly eyes (4 x 2, brown 2 x 2 irises with a glint, heavy upper lids
drooping at the outer corners, bags under them), a big bulbous RED nose (own cube), ruddy cheeks, a thick walrus
MOUSTACHE (own bone: a 12-wide block with two drooping ends, bristle-tipped) that hides the upper lip, then the
lower lip and a stubbled chin on the hinged jaw, and a stubbled double chin resting on the collar.

Wardrobe: a short-sleeved button shirt with vertical light-blue / white stripes (no crest), sweat stains under the
arms and down the back; a black canvas apron: a bib with a cartoon cow, "REY" / "DEL" on the belly and "ASADO" on
the hanging panel (3 x 5 letters, off-white), grease stains, a stitched hem, neck strap and waist ties knotted in a
bow on his back; khaki bermudas with a rolled hem and cargo pockets; hairy shins; navy rubber ojotas with white
Y-straps and toes; stainless grill tongs (two hinged arms: they clack).

Palettes: warm ruddy tan skin (10 tones), dark brown-black hair greying at the sideburns, Argentine celeste +
off-white stripes, cool black apron, khaki, navy rubber, steel, kraft paper.  Comedy reads in the normal look: the
red nose, the moustache, the belly, the apron, the flip-flops and the tongs.

The possessed look ('poseido', VARIANT_MATS[1]): same clothes (plus soot), skin turned grey-green with black veins
round the eyes and temples, bruised purple nose and cheeks, BLACK sclera with white pupils, and toggle geometry:
'demon_eyes' (opaque plane over the eyes carrying the emissive white pupils -- the only 'eyes' layer pixels on the
model, so a hidden plane means no glow) and an ear-to-ear grin: 'smile' (front plane + two side planes running
back to the ears, upper teeth, gums and lips) and 'smile_jaw' (lower teeth and lip, rides the jaw).  The grin
sits under the moustache and climbs both cheeks to the ears: the friendly dad face stretched too far.

Charcoal bag ('bag', toggle): a big kraft-paper sack "CARBON" (with the accent) carried in both arms in front of the
belly, open top full of charcoal.
"""
import math
import os
import sys

from mcmodel import Model, hash3, face_light, pick
from rig import Rig
from paint import hx, mix


# ------------------------------------------------------------------ palettes (hand-picked, hue shifted)
def H(*cs):
    return [hx(c) for c in cs]


SKIN_N = H('#2a1410', '#45201a', '#642f24', '#844334', '#a35a44', '#bc7255', '#cf8a69', '#dea27f', '#eabb98',
           '#f5d3b5')
SKIN_P = H('#0f1512', '#18211b', '#233026', '#2f3e32', '#3c4d3e', '#4b5d4b', '#5c6e5a', '#6f8069', '#84937b',
           '#9aa78e')
HAIR = H('#0b0807', '#151010', '#201816', '#2c221e', '#3b2e28', '#4d3d35', '#625047')
GREY = H('#3f3b3a', '#5d5856', '#7f7a77', '#a29d99', '#c4c0bb')
CELESTE = H('#1d3a57', '#28506f', '#356789', '#467fa3', '#5a96bd', '#71abd2', '#8cc0e2', '#a9d3ee')
WHITE = H('#4f5965', '#6a7480', '#87919c', '#a4adb7', '#bfc7cf', '#d6dce2', '#e8ecf0', '#f6f8fa')
APRON = H('#040405', '#09090b', '#0f0f12', '#16161a', '#1e1e23', '#28282e', '#34343c', '#44444e')
LETTER = H('#8f8b82', '#bdb8ad', '#dcd8cd', '#efece4', '#f8f6f0')
KHAKI = H('#2a2116', '#3b2f20', '#4f402b', '#655338', '#7c6846', '#937d56', '#a99368', '#bea97e')
BELT = H('#120b07', '#1f140d', '#2f1f14', '#43301f', '#5a432c')
BRASS = H('#3a2a0c', '#6a4f15', '#9c7a24', '#c9a23c', '#e8c862')
RUBBER = H('#090d18', '#101628', '#18213b', '#22304f', '#2e4166', '#3d557f', '#506c98')
STRAP = H('#7d8794', '#a9b2bc', '#cfd5db', '#eef1f4')
STEEL = H('#16191d', '#262a30', '#3a3f47', '#525962', '#6e7680', '#8e969f', '#b0b7be', '#d1d6db', '#eff2f4')
GRIP = H('#060607', '#0e0e10', '#18181b', '#232327', '#303036')
KRAFT = H('#3a2814', '#53391d', '#6c4c28', '#865f34', '#a07442', '#b68a55', '#c9a06b', '#d9b682')
INK = H('#120d0a', '#231a14')
RED = H('#5e1210', '#851c18', '#a92a22', '#c9412f')
COAL = H('#050505', '#0c0c0d', '#151516', '#202022', '#2e2e31', '#424247', '#5c5c62')
COW_W = H('#b9b4aa', '#dedad0', '#f3f0e8')
COW_K = H('#0b0b0d', '#1e1e22')
COW_P = H('#a8505f', '#d07c8b', '#eaa3ae')
HORN = H('#a99a72', '#d8cba2')
GREASE = H('#2a1a0c', '#4a3016', '#6e4a22')
TEETH = H('#3a3226', '#6b6048', '#9d9171', '#c8bf9f', '#e6e0c8', '#f6f2e2')
GUM = H('#2a0a10', '#4a1420', '#6e2432')
LIPP = H('#120a12', '#22141f', '#33202e', '#47303f')
MOUTH_N = H('#1a0807', '#2e100d', '#4a1c16', '#6a2a20')
SOOT = hx('#141313')


# ------------------------------------------------------------------ looks
LOOKS = {
    'normal': {
        'skin': SKIN_N, 'poss': False,
        'spec': hx('#fbe6d2'), 'crease': SKIN_N[4], 'deep': SKIN_N[2],
        'lid': hx('#3a1d16'), 'sclera': hx('#efe7dc'), 'sclera2': hx('#d9cdbf'),
        'iris': hx('#5b3a20'), 'pupil': hx('#24150c'), 'glint': hx('#fff8ee'),
        'bag': hx('#a86a5e'), 'ruddy': hx('#d4705f'), 'ruddy2': hx('#b8524a'), 'ruddy3': hx('#e88d76'),
        'lip': hx('#a9584b'), 'lip2': hx('#8a4339'), 'mouth': MOUTH_N,
        'stub': hx('#6e5a5c'), 'stub2': hx('#594648'), 'nail': hx('#f0cdb8'), 'nail2': hx('#c98f78'),
        'hairline': hx('#7c4a3a'), 'vein': None, 'chest_hair': HAIR[2],
    },
    'poseido': {
        'skin': SKIN_P, 'poss': True,
        'spec': hx('#b2bda5'), 'crease': SKIN_P[3], 'deep': SKIN_P[1],
        'lid': hx('#040405'), 'sclera': hx('#050506'), 'sclera2': hx('#0b0b0d'),
        'iris': hx('#ffffff'), 'pupil': hx('#dcdcdc'), 'glint': hx('#ffffff'),
        'bag': hx('#22192a'), 'ruddy': hx('#4a3a4c'), 'ruddy2': hx('#3a2c3e'), 'ruddy3': hx('#5a4a5a'),
        'lip': hx('#2a1c2a'), 'lip2': hx('#170f17'), 'mouth': H('#030303', '#08060a', '#120c14', '#1e1420'),
        'stub': hx('#2c3830'), 'stub2': hx('#222c25'), 'nail': hx('#2f3a30'), 'nail2': hx('#1c241e'),
        'hairline': hx('#3a443a'), 'vein': hx('#0c1410'), 'chest_hair': HAIR[1],
    },
}


def A(c, a=255):
    return (c[0], c[1], c[2], int(a))


# ------------------------------------------------------------------ geometry helpers
def local(ctx):
    """Texel centre in cube-local texel units (independent of bone rotation and face)."""
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


def tag(ctx):
    return ctx.cube.name or ''


def edge(ctx):
    return min(ctx.i, ctx.j, ctx.w - 1 - ctx.i, ctx.h - 1 - ctx.j)


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


def side_of(ctx):
    """-1 for the right-hand (-X) copy of a mirrored part, +1 for the left."""
    return getattr(ctx.cube, 'sx', 1)


def outer_face(ctx):
    """The face pointing away from the body for an arm / leg part (west on the right, east on the left)."""
    return 'west' if side_of(ctx) < 0 else 'east'


def inner_face(ctx):
    return 'east' if side_of(ctx) < 0 else 'west'


def h2(a, b, s=0):
    return hash3(a, b, 0, s)


# ------------------------------------------------------------------ the face (16 x 17, painted through the look)
# col c <-> x in [-8 + c, -7 + c]; row r <-> y in [-37 + r, -36 + r].  Skull rows 0..12, jaw rows 13..16.
# Covered by geometry: brows (cols 1-5 / 10-14, rows 4-5), nose (cols 6-9, rows 7-10), moustache (cols 2-13, rows
# 11-13; the drooping ends cols 1-2 / 13-14, rows 12-14).  What shows under them is painted sensibly anyway (the
# brows and the moustache move).
#   0-9 skin ramp   w specular   k soft crease   K deep crease   L lid line   W sclera   I iris   i pupil side
#   g glint   b eye bag   r R q ruddy (mid / dark / light)   l lip   m mouth   s S stubble (light / dark)
GX0, GY0 = -8.0, -37.0
FACE = [
    # 0123456789012345
    "4566777777776654",   # r0  y-37  top of the forehead (bald: the hair recedes at the temples)
    "5667kk7w87kk7665",   # r1  y-36  first furrow (two short bits) + sweaty shine
    "5678888888888765",   # r2  y-35
    "566kkk7887kkk665",   # r3  y-34  second furrow, just over the brows
    "5566777887776655",   # r4  y-33  (brows)
    "4556666776666554",   # r5  y-32  (brows) | lit nose root
    "45LLLLk77kLLLL54",   # r6  y-31  heavy upper lids
    "4bLgIW6776WgILb4",   # r7  y-30  eyes: the lids droop over the outer corners, iris 2x2 with a glint
    "4bWIiW6776WIiWb4",   # r8  y-29
    "45kbbb6776bbbk54",   # r9  y-28  bags under the eyes
    "456qrR6776Rrq654",   # r10 y-27  ruddy cheeks (nose cube over cols 6-9)
    "45rRRr5665rRRr54",   # r11 y-26  (moustache)
    "45sssss55sssss54",   # r12 y-25  (moustache)
    "4sssmmmmmmmmsss4",   # r13 y-24  jaw top: mouth line (under the moustache)
    "4sskllllllllkss4",   # r14 y-23  lower lip
    "4sssSk6776kSsss4",   # r15 y-22  chin
    "3sssss5665sssss3",   # r16 y-21
]
assert all(len(r) == 16 for r in FACE), [len(r) for r in FACE]
# possessed overlay: black veins crawling from the temples round the eyes and down the cheeks
VEINS = [
    "...........v....",
    "v.........v.....",
    ".v........v...v.",
    "..v........v.vv.",
    ".vv...........v.",
    "v..............v",
    "v..............v",
    "................",
    "................",
    "..v..........v..",
    ".v.v........v.v.",
    "v..............v",
    "................",
    "................",
    "................",
    "................",
    "................",
]
assert all(len(r) == 16 for r in VEINS)


def face_char(x, y):
    c = int(math.floor(x - GX0))
    r = int(math.floor(y - GY0))
    if 0 <= r < len(FACE) and 0 <= c < 16:
        return FACE[r][c], c, r
    return None, c, r


def face_rgba(ch, L, c, r):
    S = L['skin']
    poss = L['poss']
    if poss and VEINS[r][c] == 'v' and ch not in 'LWIigb':
        return L['vein']
    if ch.isdigit():
        return S[int(ch)]
    if ch == 'w':
        return L['spec']
    if ch == 'k':
        return L['crease']
    if ch == 'K':
        return L['deep']
    if ch == 'L':
        return L['lid']
    if ch == 'W':
        return L['sclera'] if not poss else L['sclera']
    if ch == 'I':
        return L['iris']
    if ch == 'i':
        return L['pupil']
    if ch == 'g':
        return L['glint']
    if ch == 'b':
        return L['bag']
    if ch == 'r':
        return L['ruddy']
    if ch == 'R':
        return L['ruddy2']
    if ch == 'q':
        return L['ruddy3']
    if ch == 'l':
        return L['lip']
    if ch == 'm':
        return L['mouth'][1]
    if ch in 'sS':
        base = S[5] if ch == 's' else S[4]
        hh = h2(c * 3 + 1, r * 5 + 2, 11)
        if hh > 0.55:
            return L['stub2'] if ch == 'S' else L['stub']
        if hh > 0.3:
            return mix(base, L['stub'], 0.45)
        return base
    return S[5]


# ------------------------------------------------------------------ pixel font (3 x 5, N is 4 wide)
FONT = {
    'R': ["##.", "#.#", "##.", "#.#", "#.#"],
    'E': ["###", "#..", "##.", "#..", "###"],
    'Y': ["#.#", "#.#", ".#.", ".#.", ".#."],
    'D': ["##.", "#.#", "#.#", "#.#", "##."],
    'L': ["#..", "#..", "#..", "#..", "###"],
    'A': [".#.", "#.#", "###", "#.#", "#.#"],
    'S': [".##", "#..", ".#.", "..#", "##."],
    'O': ["###", "#.#", "#.#", "#.#", "###"],
    'C': [".##", "#..", "#..", "#..", ".##"],
    'B': ["##.", "#.#", "##.", "#.#", "##."],
    'N': ["#..#", "##.#", "#.##", "#..#", "#..#"],
}


def text_mask(word):
    """-> set of (col, row) lit pixels and the width.  An 'o' with an accent is written 'Ó' (accent row -1)."""
    px = set()
    x = 0
    for ch in word:
        acc = ch == 'Ó'
        g = FONT['O' if acc else ch]
        for r, row in enumerate(g):
            for c, v in enumerate(row):
                if v == '#':
                    px.add((x + c, r))
        if acc:
            px.add((x + 2, -1))
        x += len(g[0]) + 1
    return px, x - 1


TXT_REY, W_REY = text_mask('REY')
TXT_DEL, W_DEL = text_mask('DEL')
TXT_ASADO, W_ASADO = text_mask('ASADO')
TXT_CARBON, W_CARBON = text_mask('CARBÓN')

# the cartoon cow on the bib (10 x 7): horns, ears, white head with a black patch, eyes, pink snout
COW = [
    "H........H",
    "pwwKKwwwwp",
    ".wKKKwwww.",
    ".wOwwwwOw.",
    ".PPPPPPPP.",
    ".PnPPPPnP.",
    "..PPPPPP..",
]
assert all(len(r) == 10 for r in COW)


# ------------------------------------------------------------------ materials
def skin_base(ctx, L, v):
    return L['skin'][max(0, min(9, int(v * 10)))]


def hairy(ctx, seed, density=0.16):
    """Short dark hairs on forearms / shins: 2-texel slanted strokes."""
    i, j = ctx.i, ctx.j
    k = h2(i * 7 + (j // 2) * 3, (j // 2) * 11 + i, seed)
    if k < density:
        return True
    k2 = h2((i - 1) * 7 + ((j - 1) // 2) * 3, ((j - 1) // 2) * 11 + (i - 1), seed)
    return k2 < density * 0.5 and j % 2 == 1


def skin_mat(ctx, L):
    t = tag(ctx)
    f = ctx.face
    S = L['skin']
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    x, y, z = ctx.pos
    v = 0.6 + face_light(ctx) * 0.9
    if f in ('west', 'east'):
        v -= 0.06
    if f == 'back':
        v -= 0.1

    # ---------------- head
    if t == 'skull':
        if f == 'front':
            ch, c, r = face_char(x, y)
            return A(face_rgba(ch, L, c, r)) if ch else A(S[5])
        if f == 'bottom':
            # roof of the mouth, seen when the jaw drops: upper teeth along the front edge, dark palate behind
            if z < -7.0:
                if abs(x) < 6.0:
                    return A(TEETH[4] if int(x + 8) % 2 == 0 else TEETH[3])
                return A(L['mouth'][2])
            if z < 4.0:
                return A(L['mouth'][0] if abs(x) < 6.5 else L['mouth'][1])
            return A(S[2])
        if f == 'top':
            v = 0.72 + (0.08 if (abs(x) < 5 and z < -2) else 0.0)
            if abs(x + 2) < 1.0 and abs(z + 4.5) < 1.0:
                return A(L['spec'])                          # shine on the bald crown
            return A(skin_base(ctx, L, v))
        if f == 'back':
            # nape under the hair line (the shell covers the rest)
            v = 0.5 - (y + 26) * 0.02
            if h2(ctx.i, ctx.j, 5) > 0.7:
                return A(HAIR[3])
            return A(skin_base(ctx, L, v))
        # sides: temple, cheek, jaw corner (the ear and the hair shell sit on top)
        fz = -z if f == 'west' else -z
        v = 0.56
        if z < -4.0:
            v += 0.06                                        # cheek turning to the front
            if y > -29 and y < -25:
                return A(L['ruddy2'] if (z < -6.5 and y > -28) else skin_base(ctx, L, 0.58))
        if y > -26.0:
            v -= 0.08
            if h2(ctx.i, ctx.j, 7) > 0.55:
                return A(L['stub'])
        if L['poss'] and ((int(z) + int(y)) % 7 == 0 and -36 < y < -29 and z < -1):
            return A(L['vein'])
        return A(skin_base(ctx, L, v))

    if t == 'jaw':
        if f == 'front':
            ch, c, r = face_char(x, y)
            return A(face_rgba(ch, L, c, r)) if ch else A(S[4])
        if f == 'top':
            # floor of the mouth: lower teeth along the front, tongue, dark throat
            if z < -7.0:
                if abs(x) < 6.0:
                    return A(TEETH[3] if int(x + 8) % 2 == 0 else TEETH[2])
                return A(L['mouth'][2])
            if abs(x) < 3.5 and z < 1.0:
                return A(L['mouth'][3] if z < -3 else L['mouth'][2])
            return A(L['mouth'][0])
        if f == 'bottom':
            return A(L['stub2'] if h2(ctx.i, ctx.j, 3) > 0.5 else S[3])
        if f == 'back':
            return A(S[2])
        # sides: the jaw line, stubbled
        v = 0.5 - (ly / h) * 0.12
        if h2(ctx.i, ctx.j, 8) > 0.5:
            return A(L['stub'] if v > 0.42 else L['stub2'])
        return A(skin_base(ctx, L, v))

    if t == 'chin2':
        if f in ('back', 'top'):
            return None
        if f == 'bottom':
            return A(S[2])
        v = 0.46 + face_light(ctx) * 0.6
        if f == 'front' and ctx.j == 0:
            return A(S[3])                                   # the fold under the chin
        if h2(ctx.i, ctx.j, 9) > 0.5:
            return A(L['stub2'])
        return A(skin_base(ctx, L, v))

    if t == 'nose':
        if f == 'back':
            return None
        if f == 'front':
            i, j = ctx.i, ctx.j
            if L['poss']:
                pal = {0: S[6], 1: S[6], 2: L['ruddy'], 3: L['ruddy2']}
                c = pal[j]
                if j == 1 and i == 1:
                    c = S[8]
                if j >= 2 and i in (0, 3):
                    c = L['ruddy2']
                return A(c)
            rows = [
                [S[6], S[7], S[7], S[6]],
                [S[6], L['spec'], S[8], L['ruddy3']],
                [L['ruddy'], L['ruddy3'], L['ruddy'], L['ruddy2']],
                [L['ruddy2'], L['ruddy'], L['ruddy'], L['ruddy2']],
            ]
            return A(rows[j][i])
        if f == 'bottom':
            if lz < 1.0 and 0.5 < lx < 1.5 or lz < 1.0 and 2.5 < lx < 3.5:
                return A(L['mouth'][1])                       # nostrils
            return A(L['ruddy2'] if not L['poss'] else S[3])
        if f == 'top':
            return A(S[7] if lz < 1.5 else S[6])
        # sides: lit west, shadowed east; the tip is ruddy
        c = S[6] if f == 'west' else S[4]
        if ly > 2.0:
            c = L['ruddy'] if f == 'west' else L['ruddy2']
        return A(c)

    if t == 'ear':
        outer = (f == 'west' and x < 0) or (f == 'east' and x > 0)
        if outer:
            # helix rim lit, concha dark, lobe at the bottom
            i, j = ctx.i, ctx.j
            if j == 0 or i == (2 if f == 'west' else 0):
                return A(S[7])
            if 1 <= j <= 3 and i == 1:
                return A(S[3])
            return A(S[6] if j < 4 else S[5])
        if f == 'front':
            return A(S[6] if ctx.j < 4 else S[5])
        if f == 'top':
            return A(S[7])
        if f == 'bottom':
            return A(S[4])
        return A(S[4])                                        # back / inner faces: shadowed

    if t == 'neck':
        if f in ('top', 'bottom'):
            return None
        if f == 'front':
            if h2(ctx.i, ctx.j, 12) > 0.6:
                return A(L['stub2'])
            return A(skin_base(ctx, L, 0.46))
        if f == 'back':
            v = 0.5
            if L['poss'] and ctx.i in (3, 6) and ctx.j < 3:
                return A(L['vein'])
            return A(skin_base(ctx, L, v))
        return A(skin_base(ctx, L, 0.44))

    # ---------------- arms
    if t == 'upper_arm':
        if f == 'top':
            return None
        v = 0.6 + face_light(ctx) * 0.9
        if ly < 1.0:
            v -= 0.16                                         # shadow under the sleeve
        if f == inner_face(ctx):
            v -= 0.08
        return A(skin_base(ctx, L, v))

    if t == 'forearm':
        if f == 'top':
            return A(S[4])
        v = 0.62 + face_light(ctx) * 0.9
        if f == inner_face(ctx):
            v -= 0.06
        if f in ('front', 'back', 'west', 'east') and ly > h - 1.0:
            v -= 0.06                                         # wrist
        if f in ('front', 'back', 'west', 'east') and hairy(ctx, 31 + int(x > 0)):
            return A(HAIR[3] if v > 0.55 else HAIR[2])
        if t == 'forearm' and getattr(ctx.cube, 'watch', False) and ly > h - 2.5 and ly < h - 0.8:
            return A(STEEL[6] if f == outer_face(ctx) else STEEL[4])
        return A(skin_base(ctx, L, v))

    if t == 'fist':
        # the right fist round the tongs grip: back of the hand outside, curled fingers underneath, nails inside
        i, j = ctx.i, ctx.j
        if f == outer_face(ctx):                              # back of the hand
            if j >= h - 1:
                return A(S[7] if i % 2 == 0 else S[5])        # knuckle row
            if hairy(ctx, 44, 0.08):
                return A(HAIR[3])
            return A(skin_base(ctx, L, 0.62))
        if f == 'bottom':                                     # four curled fingers along z
            seg = int(lz / d * 4)
            edge_z = (lz / d * 4) % 1.0
            if edge_z < 0.25 and seg > 0:
                return A(S[3])
            return A(S[6] if lx < 2.5 else S[5])
        if f == inner_face(ctx):                              # fingertips + nails pressed into the palm
            seg = (lz / d * 4) % 1.0
            if seg < 0.25:
                return A(S[3])
            if ly > 2.0:
                return A(L['nail'] if ly < 3.5 else L['nail2'])
            return A(S[5])
        if f == 'front':
            if ly < 2.0 and lx > 2.0:
                return A(S[7])
            return A(S[5] if ctx.j > 1 else S[6])
        if f == 'top':
            return A(S[4])
        return A(S[5])

    if t in ('thumb', 'thumb_l'):
        if f == 'top':
            return A(S[5])
        if f == 'bottom':
            return A(L['nail'] if t == 'thumb_l' else S[6])
        if t == 'thumb_l' and ly > h - 1.5 and f == 'front':
            return A(L['nail'])
        return A(skin_base(ctx, L, 0.62 + face_light(ctx) * 0.8))

    if t == 'palm':
        v = 0.62 + face_light(ctx) * 0.9
        if f == inner_face(ctx):                              # the palm itself: lighter, a crease
            if abs(ly - 2.5) < 0.5 and lz > 1.0:
                return A(S[5])
            return A(skin_base(ctx, L, v + 0.06))
        if f == outer_face(ctx):
            if ly > h - 1.0:
                return A(S[7] if ctx.i % 2 == 0 else S[6])    # knuckles
            if hairy(ctx, 45, 0.08):
                return A(HAIR[3])
        return A(skin_base(ctx, L, v))

    if t == 'finger':
        if f == 'top':
            return A(S[4])
        if f == 'bottom':
            return A(S[7])                                    # fingertip
        if ly > h - 1.5 and f in ('front', outer_face(ctx)):
            return A(L['nail'] if ly < h - 0.5 else L['nail2'])
        v = 0.62 + face_light(ctx) * 0.9
        if abs(ly - 2.0) < 0.5:
            v -= 0.14                                         # knuckle crease
        if f == inner_face(ctx):
            v += 0.04
        if f in ('west', 'east') and f != outer_face(ctx) and f != inner_face(ctx):
            v -= 0.05
        return A(skin_base(ctx, L, v))

    # ---------------- legs
    if t == 'shin':
        if f == 'top':
            return None
        v = 0.6 + face_light(ctx) * 0.9
        if ly < 1.5:
            v -= 0.14                                         # shadow under the bermuda hem
        if f == 'front':
            v += 0.04 if 1 <= ctx.i <= 3 else 0.0             # shin bone catches the light
        if f == 'back' and 2 < ly < 6:
            v += 0.03                                         # the calf
        if ly > h - 1.5:
            v -= 0.05                                         # ankle
        if hairy(ctx, 51 + int(x > 0), 0.2):
            return A(HAIR[2] if v < 0.6 else HAIR[3])
        return A(skin_base(ctx, L, v))

    if t == 'foot':
        sx = side_of(ctx)
        i, j = ctx.i, ctx.j
        # strap: Y from the toe post (between the big toe and the second toe) back to both sides of the foot
        big_x = (w - 2.0) if sx < 0 else 2.0                  # x of the post (big toe on the inner side)
        if f == 'top':
            u = lx
            zz = lz                                           # 0 = back of the foot (heel) .. d = toes
            toe_zone = zz > d - 2.5
            if toe_zone:
                # toes: big toe 2 wide on the inner side, four small ones, dark splits, nails
                if sx < 0:
                    big = u > w - 2.0
                    k = int((w - 2.0 - u))                    # 0.. small toes counted outward
                else:
                    big = u < 2.0
                    k = int(u - 2.0)
                split = (not big) and ((u - (2.0 if sx > 0 else 0)) % 1.25 < 0.3)
                if big and abs(u - big_x) < 0.4:
                    return A(S[3])
                if split:
                    return A(S[3])
                if zz > d - 1.2:
                    return A(L['nail'] if big or k % 2 == 0 else L['nail2'])
                return A(S[7] if big else S[6])
            # the strap
            post_z = d - 2.5
            t_ = (post_z - zz) / 4.0
            if 0.0 <= t_ <= 1.0:
                sx0 = big_x + (0 - big_x) * t_            # towards the outer edge
                sx1 = big_x + (w - big_x) * t_            # towards the inner edge
                if abs(u - sx0) < 0.7 or abs(u - sx1) < 0.7:
                    return A(STRAP[3] if abs(u - big_x) < 1.2 else STRAP[2])
            return A(skin_base(ctx, L, 0.66 - (d - zz) * 0.01))
        if f == 'front':
            # toes seen from the front
            if sx < 0:
                big = lx > w - 2.0
            else:
                big = lx < 2.0
            if j == 0:
                return A(S[7] if big else S[6])
            if not big and int(lx * 0.8) % 2 == 1:
                return A(S[4])
            return A(S[6] if big else S[5])
        if f in ('west', 'east'):
            # the strap ends anchored to the sole half-way along the foot
            if abs(lz - (d - 6.5)) < 0.8 and ctx.j >= 0:
                return A(STRAP[2])
            return A(skin_base(ctx, L, 0.52 + (0.04 if f == 'west' else 0)))
        if f == 'back':
            return A(S[4])                                    # heel
        return A(S[4])

    return A(skin_base(ctx, L, v))


def hair_mat(ctx, L):
    """Dark brown-black hair, greying at the sideburns; bushy brows; the walrus moustache."""
    t = tag(ctx)
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    x, y, z = ctx.pos
    if t == 'hair':
        ax = abs(x)
        if f in ('front', 'bottom'):
            return None
        if f == 'top':
            # receding hairline: bald temples, a central lock that comes forward to the tuft
            zf = -5.0 + 4.2 * min(1.0, max(0.0, (ax - 1.0) / 4.0)) - 1.6 * max(0.0, (ax - 5.5) / 2.5)
            if z < zf - 0.6:
                return None
            if z < zf + 0.6 and h2(ctx.i, ctx.j, 21) > 0.5:
                return None                                   # thin, broken hairline
            u = x * 0.9 + z * 0.15
            v = 0.42 + (0.12 if int(u * 1.3) % 3 == 0 else 0.0) - (z + 8) * 0.008
            if ax > 6.5:
                return A(mix(pick(HAIR, v), GREY[2], 0.35))
            return A(pick(HAIR, v))
        if f in ('west', 'east'):
            # side: hair above / behind the ear, a greying sideburn in front of it
            if z < -2.6:
                return None
            if z < -0.4:                                      # sideburn
                if y > -26.6:
                    return None
                g = 0.5 + 0.2 * h2(ctx.i, ctx.j, 22)
                return A(GREY[1] if g > 0.62 else GREY[0] if g > 0.56 else HAIR[3])
            if -1.6 < z < 1.6 and y > -31.4:
                return None                                   # the ear comes through here (hidden anyway)
            if y > -26.4:
                return None
            v = 0.36 + (0.12 if (ctx.i + ctx.j // 3) % 4 == 0 else 0.0) + (0.06 if y < -34 else 0.0)
            c = pick(HAIR, v)
            if y > -31 and z < 3.0:
                c = mix(c, GREY[2], 0.35)                     # salt and pepper over the ear
            return A(c)
        if f == 'back':
            nape = -27.0 + (0.6 if int(x + 9) % 3 == 0 else 0.0)
            if y > nape:
                return None
            v = 0.32 + (0.12 if (ctx.i // 1 + ctx.j // 2) % 4 == 0 else 0.0) + (0.08 if y < -34 else 0.0)
            return A(pick(HAIR, v))
        return None

    if t == 'tuft':
        if f == 'bottom':
            return None
        v = 0.5 + face_light(ctx) * 0.8 + (0.12 if ctx.i % 2 == 0 else 0.0)
        if f == 'front' and ctx.j == ctx.h - 1 and ctx.i == 1:
            return None                                       # the lock ends in two points
        return A(pick(HAIR, v))

    if t == 'brow':
        if f == 'back':
            return None
        if f == 'front':
            i, j = ctx.i, ctx.j
            outer = (i == 0) if x < 0 else (i == ctx.w - 1)
            if j == 0:
                if outer:
                    return None                               # tapered outer tip
                return A(HAIR[4] if (i % 2 == 0) else HAIR[3])
            return A(HAIR[2] if not outer else HAIR[1])
        if f == 'top':
            return A(HAIR[4] if ctx.i % 2 == 0 else HAIR[3])
        if f == 'bottom':
            return A(HAIR[1])
        return A(HAIR[2])

    if t in ('moustache', 'moustache_end'):
        if f == 'back':
            return None
        i, j = ctx.i, ctx.j
        if f == 'front':
            bottom = j == ctx.h - 1
            if bottom and h2(i, 3, 23 + (t == 'moustache_end')) > 0.62:
                return None                                   # bristle tips
            v = 0.4 + (0.14 if (i + (j == 1)) % 3 == 0 else 0.0)
            if j == 0:
                v -= 0.1                                      # shadow under the nose
            if t == 'moustache' and abs(x) < 0.6:
                v -= 0.12                                     # parting under the nose
            c = pick(HAIR, v)
            if h2(i, j, 24) > 0.86:
                c = GREY[2]                                   # a few grey hairs
            return A(c)
        if f == 'top':
            return A(HAIR[3])
        if f == 'bottom':
            return A(HAIR[1] if h2(i, j, 25) > 0.4 else HAIR[2])
        return A(HAIR[2] if ctx.j < ctx.h - 1 else HAIR[1])
    return A(HAIR[2])


# ---- shirt + apron (the apron is painted on the bib, the belly fronts and the skirt)
def stripe_col(u, v, poss=False):
    ph = int(math.floor(u)) % 4
    if ph < 2:
        c = pick(CELESTE, v)
    else:
        c = pick(WHITE, v + 0.08)
    return c


def apron_rgba(v, ctx=None):
    return pick(APRON, v)


def shirt_rgba(ctx, L, u, v):
    c = stripe_col(u, v)
    return c


def shirt_mat(ctx, L):
    t = tag(ctx)
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    x, y, z = ctx.pos
    side = f in ('front', 'back', 'west', 'east')
    v = 0.6 + face_light(ctx) * 1.0
    if f in ('west', 'east'):
        v -= 0.05
    u = x if f in ('front', 'back', 'top', 'bottom') else z

    if t == 'torso':
        if f == 'bottom':
            return None
        if f == 'front' and abs(x) < 7.0:
            return A(APRON[2])                                # behind the bib (never seen)
        if side and edge(ctx) == 0:
            v -= 0.06
        if f == 'top':
            # shoulders; the apron neck strap runs over them to the collar
            if 5.5 < abs(x) < 7.0 and z < -2.5:
                return A(APRON[3])
            v += 0.04
        if f in ('west', 'east'):
            # sweat stain under the arm (an oval), pull folds from the armpit to the belly
            dz, dy = z / 4.0, (y + 15.0) / 4.5
            if dz * dz + dy * dy < 1.0:
                v -= 0.16
            if (abs((z * 0.7 + y) - (-14.0)) < 0.5 or abs((z * 0.7 + y) - (-10.0)) < 0.5) and z < 2:
                v -= 0.1
            # waist ties running back round the waist
            if -7.0 <= y < -6.0:
                return A(APRON[3])
        if f == 'back':
            # a big V of sweat between the shoulder blades
            hw = 5.5 - (y + 18.0) * 0.45
            if -18.0 < y < -8.0 and abs(x) < hw:
                v -= 0.14
            if -7.0 <= y < -6.0:
                return A(APRON[3] if abs(x) > 1.0 else APRON[5])
            if 5.5 < abs(x) < 7.0 and y < -17.0:
                return A(APRON[3])                            # the neck strap ends
            if abs(x) < 0.5 and y > -16:
                v -= 0.08                                     # back seam
        c = shirt_rgba(ctx, L, u, v)
        if L['poss'] and side and h2(int(x * 2), int(y * 2), 61) > 0.93:
            c = mix(c, SOOT, 0.5)
        return A(c)

    if t == 'yoke':
        if f == 'bottom':
            return None
        if f == 'top':
            if 5.5 < abs(x) < 7.0:
                return A(APRON[4])                            # neck strap over the shoulder
            v += 0.08
        if f == 'front':
            return A(APRON[2]) if abs(x) < 7.0 else A(shirt_rgba(ctx, L, u, v))
        if f == 'back' and 5.5 < abs(x) < 7.0:
            return A(APRON[3])
        return A(shirt_rgba(ctx, L, u, v + 0.04))

    if t == 'collar':
        # stand-up shirt collar round the neck: white band, open V at the front (throat, chest hair, gold chain)
        if f == 'bottom':
            return None
        if f == 'top':
            if abs(x) < 4.6 and abs(z) < 4.0:
                return None                                   # the neck passes through
            return A(pick(WHITE, 0.82))
        if f == 'front':
            if abs(x) < 2.5:
                if ctx.j == ctx.h - 1 and abs(x) < 1.5:
                    return A(BRASS[3] if int(x + 3) % 2 else BRASS[4])     # gold chain
                if h2(ctx.i, ctx.j, 41) > 0.45:
                    return A(L['chest_hair'])
                return A(skin_base(ctx, L, 0.5))
            if abs(x) < 3.5:
                return A(pick(WHITE, 0.5))                    # collar edge in shadow
        if f in ('west', 'east', 'back') and ctx.j == ctx.h - 1:
            return A(APRON[3])                                # the apron's neck strap
        return A(pick(WHITE, v + 0.1 - (0.08 if ctx.j == ctx.h - 1 else 0.0)))

    if t == 'collar_tip':
        # a collar point lying on the chest: a triangle (zero-thickness plane)
        if f not in ('front', 'back'):
            return None
        i, j = ctx.i, ctx.j
        inner = (ctx.w - 1 - i) if x < 0 else i               # 0 next to the neck
        if f == 'back':
            inner = i if x < 0 else (ctx.w - 1 - i)
        if j > inner + 0.5:
            return None
        if j == inner or j == inner - 0 and j == ctx.h - 1:
            return A(pick(WHITE, 0.55))
        return A(pick(WHITE, 0.86 - j * 0.04))

    if t == 'sleeve':
        if f == 'top':
            return None if True else None
        if f == 'bottom':
            return A(CELESTE[0])                              # dark inside of the sleeve
        uu = around(ctx)
        v = 0.6 + face_light(ctx) * 1.0
        if ly > h - 1.5:
            v -= 0.1                                          # folded hem
            if ly > h - 0.6:
                v -= 0.08
        if f == inner_face(ctx):
            v -= 0.12
            dz, dy = (lz - d / 2) / 3.0, (ly - 1.0) / 3.5
            if dz * dz + dy * dy < 1.0:
                v -= 0.14                                     # sweat under the arm
        if ly < 1.0 and f != inner_face(ctx):
            v += 0.06                                         # shoulder seam catches light
        c = stripe_col(uu, v)
        if L['poss'] and h2(ctx.i, ctx.j, 62) > 0.94:
            c = mix(c, SOOT, 0.5)
        return A(c)

    # ---------------- belly (shirt round the sides, apron on the front)
    if t in ('belly_top', 'belly_core', 'belly_front'):
        if f == 'back':
            return None
        apron_hw = {'belly_top': 8.5, 'belly_core': 9.5, 'belly_front': 11.0}[t]
        if t == 'belly_top' and f == 'bottom':
            return None
        on_front = f in ('front', 'top') or (t == 'belly_front' and f in ('west', 'east', 'bottom'))
        if on_front and abs(x) < apron_hw:
            return A(apron_paint(ctx, L, t))
        if f == 'bottom':
            v = 0.32                                          # the underside of the belly, in shadow
        if f in ('west', 'east'):
            v -= 0.04 - (0.0 if t != 'belly_core' else 0.0)
            # shirt pulled over the belly: curved stress folds and the waist ties
            if t == 'belly_core':
                if -7.0 <= y < -6.0:
                    return A(APRON[3])
                if abs((y + 2.0) - (z + 8.0) * 0.5) < 0.5 or abs((y + 6.0) - (z + 8.0) * 0.4) < 0.5:
                    v -= 0.1
        if f == 'front' and t == 'belly_core':
            if -7.0 <= y < -6.0:
                return A(APRON[3])                            # the waist tie leaving the apron
            if abs(x) > 11.0:
                v -= 0.06
        c = shirt_rgba(ctx, L, u, v)
        if L['poss'] and h2(int(x * 2), int(y * 2) + int(z), 63) > 0.93:
            c = mix(c, SOOT, 0.5)
        return A(c)
    return A(shirt_rgba(ctx, L, u, v))


def apron_paint(ctx, L, t):
    """Black canvas: stitched hem, grease, the letters (on the flat fronts), soot when possessed."""
    f = ctx.face
    x, y, z = ctx.pos
    v = 0.42 + face_light(ctx) * 0.8
    if f in ('west', 'east'):
        v -= 0.08
    if f == 'bottom':
        v = 0.25
    if h2(ctx.i * 3 + ctx.j, ctx.j * 7, 71) > 0.9:
        v += 0.06                                             # canvas weave sparkle
    i, j = ctx.i, ctx.j
    if t == 'belly_front' and f == 'front':
        if i == 0 or i == ctx.w - 1:
            return pick(APRON, v + 0.14)                      # folded edge
        # REY (rows 1-5) and DEL (rows 7-11), centred
        ox = (ctx.w - W_REY) // 2
        if (i - ox, j - 1) in TXT_REY:
            return letter(i - ox, j - 1)
        ox = (ctx.w - W_DEL) // 2
        if (i - ox, j - 7) in TXT_DEL:
            return letter(i - ox, j - 7)
        if (i, j) in ((16, 7), (17, 7), (17, 8)):
            return GREASE[1] if (i, j) != (16, 7) else GREASE[2]
        if L['poss'] and h2(i, j, 72) > 0.9:
            return mix(pick(APRON, v), hx('#2a2a2a'), 0.5)
    if f == 'top':
        if (t == 'belly_front') or (ctx.j == ctx.h - 1):
            v += 0.08                                         # the lip of each step catches the light
    if f in ('west', 'east') and t == 'belly_front':
        v += 0.06
    if f == 'front' and t in ('belly_top', 'belly_core'):
        hw = {'belly_top': 8.5, 'belly_core': 9.5}[t]
        if abs(x) > hw - 1.0:
            v += 0.12                                         # the apron edge
    return pick(APRON, v)


def letter(c, r):
    """Off-white print, a touch darker on the bottom row and the right column (worn ink)."""
    if r == 4:
        return LETTER[2]
    if r == 0:
        return LETTER[4]
    return LETTER[3]


def apron_mat(ctx, L):
    t = tag(ctx)
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    x, y, z = ctx.pos
    i, j = ctx.i, ctx.j
    v = 0.42 + face_light(ctx) * 0.8
    if h2(i * 3 + j, j * 7 + 1, 73) > 0.9:
        v += 0.06
    if t == 'bib':
        if f == 'back':
            return None
        if f == 'front':
            if i == 0 or i == ctx.w - 1 or j == 0:
                v += 0.14                                     # folded edge
            ox = (ctx.w - 10) // 2
            ci, cj = i - ox, j
            if 0 <= ci < 10 and 0 <= cj < 7:
                ch = COW[cj][ci]
                cow = {'H': HORN[1], 'p': COW_P[1], 'w': COW_W[2], 'K': COW_K[0], 'O': COW_K[0],
                       'P': COW_P[2], 'n': COW_P[0]}.get(ch)
                if ch == 'w' and cj >= 2 and ci in (1, 8):
                    cow = COW_W[1]                            # shade down the cheeks
                if ch == 'P' and cj == 6:
                    cow = COW_P[1]
                if cow is not None:
                    return A(cow)
            return A(pick(APRON, v))
        if f in ('west', 'east'):
            return A(pick(APRON, v + 0.1))
        return A(pick(APRON, v + 0.12))
    if t == 'skirt':
        if f == 'front':
            if i == 0 or i == ctx.w - 1:
                return A(pick(APRON, v + 0.14))
            if j == ctx.h - 1:
                return A(pick(APRON, v + 0.1))               # hem
            if j == ctx.h - 2 and i % 3 != 1:
                return A(pick(APRON, v + 0.18))              # stitched hem line
            ox = (ctx.w - W_ASADO) // 2
            if (i - ox, j - 1) in TXT_ASADO:
                return A(letter(i - ox, j - 1))
            # grease stains (hand placed) and a salt smear
            stains = {(4, 6): 1, (5, 6): 2, (5, 7): 1, (17, 6): 1, (18, 7): 2, (12, 0): 1}
            if (i, j) in stains:
                return A(GREASE[stains[(i, j)]])
            if L['poss'] and j >= ctx.h - 3 and h2(i, j, 74) > 0.6:
                return A(mix(pick(APRON, v), hx('#5a2a10'), 0.4))    # singed
            return A(pick(APRON, v))
        if f == 'back':
            return A(pick(APRON, 0.18))
        if f == 'bottom':
            return A(pick(APRON, 0.3))
        return A(pick(APRON, v + 0.06))
    if t == 'bow':
        if f not in ('front', 'back'):
            return None
        return bow_paint(ctx, L)
    return A(pick(APRON, v))


# the waist ties knotted in a bow on his back (9 x 5, seen from behind; 'back' face of the plane)
BOW = [
    "XXX...XXX",
    "Xooo.oooX",
    ".XooKooX.",
    "...X.X...",
    "..X...X..",
]


def bow_paint(ctx, L):
    i, j = ctx.i, ctx.j
    if ctx.face == 'front':
        i = ctx.w - 1 - i
    ch = BOW[j][i] if j < len(BOW) and i < len(BOW[0]) else '.'
    if ch == '.':
        return None
    c = {'X': APRON[5], 'o': APRON[3], 'K': APRON[6]}[ch]
    return A(c)


def shorts_mat(ctx, L):
    t = tag(ctx)
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    x, y, z = ctx.pos
    v = 0.56 + face_light(ctx) * 1.0
    if f in ('west', 'east'):
        v -= 0.05
    side = f in ('front', 'back', 'west', 'east')
    if t == 'hips':
        if f in ('top', 'bottom'):
            return None if f == 'bottom' else A(pick(KHAKI, 0.4))
        if ly < 2.0:
            # the belt
            if f == 'front' and abs(x) < 1.5:
                return A(BRASS[3] if ly < 1.0 else BRASS[2])
            if side and (int(around(ctx)) % 9 == 4):
                return A(pick(KHAKI, v - 0.05))               # belt loop
            return A(pick(BELT, 0.5 + face_light(ctx) * 0.8 + (0.12 if ly < 1.0 else 0.0)))
        if f == 'back' and 2.5 < ly < 6.5 and (abs(abs(x) - 5.0) < 2.6):
            if ly < 3.2 or abs(abs(x) - 5.0) > 2.0:
                return A(pick(KHAKI, v - 0.12))               # back pockets
        if f == 'back' and abs(x) < 0.5:
            v -= 0.1
        return A(pick(KHAKI, v))
    if t in ('shorts', 'cuff'):
        if f == 'top':
            return None
        if f == 'bottom':
            return A(KHAKI[1])
        if t == 'cuff':
            v += 0.06 if ly < 1.0 else -0.04
            if edge(ctx) == 0 and ly > 1.0:
                v -= 0.08
            return A(pick(KHAKI, v))
        # cargo pocket on the outer side, crease lines, inseam
        if f == outer_face(ctx) and 2.0 < ly < 7.0 and 2.0 < (lz if f == 'east' else d - lz) < 8.0:
            if ly < 3.0:
                return A(pick(KHAKI, v + 0.08 if ly < 2.5 else v - 0.12))    # flap
            if abs(lz - d / 2) > 2.4 or ly > 6.4:
                return A(pick(KHAKI, v - 0.1))                # pocket seam
            return A(pick(KHAKI, v - 0.02))
        if f == inner_face(ctx):
            v -= 0.1
        if f == 'front' and int(ly) in (3, 6) and int(lx) % 4 == 1:
            v -= 0.08                                         # creases at the crotch
        if side and edge(ctx) == 0:
            v -= 0.05
        return A(pick(KHAKI, v))
    return A(pick(KHAKI, v))


def sole_mat(ctx, L):
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    if f == 'top':
        # rubber top layer round the foot, a little worn where the heel and the ball sit
        v = 0.6
        if lz < 4.0 and abs(lx - w / 2) < 2.5:
            v -= 0.12
        return A(pick(RUBBER, v))
    if f == 'bottom':
        return A(RUBBER[0] if (ctx.i + ctx.j) % 3 else RUBBER[1])
    # sides: lighter top layer, dark sole underneath
    return A(RUBBER[5] if ctx.j == 0 and ctx.h > 1 else RUBBER[3] if f != 'back' else RUBBER[2])


def steel_mat(ctx, L):
    t = tag(ctx)
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    v = 0.55 + face_light(ctx) * 1.2
    if t == 'grip':
        if f in ('top', 'west', 'east', 'bottom'):
            # ribbed black rubber
            if int(lz) % 2 == 0:
                return A(GRIP[3] if f == 'top' else GRIP[2])
            return A(GRIP[1])
        return A(GRIP[2])
    if t in ('tip', 'tip_lo'):
        # scalloped head: teeth along the front edge
        if f == 'front' and ctx.i % 2 == 1:
            return None
        if f == 'top':
            if lz < 0.7 and ctx.i % 2 == 1:
                return None
            v += 0.12
    if t == 'hinge':
        v += 0.1
    if f == 'top':
        v += 0.12
        if ctx.i == 0:
            v += 0.15                                         # polished edge
    if f == 'bottom':
        v -= 0.15
    c = pick(STEEL, v)
    if L['poss'] and h2(ctx.i, ctx.j, 81) > 0.85:
        c = mix(c, SOOT, 0.4)
    return A(c)


def bag_mat(ctx, L):
    t = tag(ctx)
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    i, j = ctx.i, ctx.j
    v = 0.56 + face_light(ctx) * 1.0
    # paper crinkle: soft vertical creases + a few hand-placed folds
    v += (0.05 if (i * 7 + j // 4) % 5 == 0 else 0.0) - (0.05 if (i * 3 + j // 3) % 7 == 0 else 0.0)
    if t == 'coal':
        if f == 'bottom':
            return None
        k = h2(i // 2 * 3 + j, i // 2 + j * 5, 91)
        if k > 0.8:
            return A(COAL[5])
        if k > 0.55:
            return A(COAL[3])
        return A(COAL[1] if (i + j) % 2 else COAL[2])
    if t == 'rim':
        if f == 'bottom':
            return None
        if f == 'top':
            if 1.0 < lx < w - 1.0 and 1.0 < lz < d - 1.0:
                return A(COAL[1])
            return A(pick(KRAFT, 0.72))
        v += 0.08 if j == 0 else -0.06
        return A(pick(KRAFT, v))
    if f == 'top':
        return A(COAL[2])
    if f == 'bottom':
        return A(pick(KRAFT, 0.2))
    if f in ('west', 'east'):
        # gusset: a vertical fold in the middle
        if abs(lz - d / 2) < 0.6:
            v -= 0.14
        return A(pick(KRAFT, v - 0.04))
    if f == 'front':
        ox = (ctx.w - W_CARBON) // 2
        if (i - ox, j - 4) in TXT_CARBON:
            return A(INK[0] if j - 4 < 4 else INK[1])
        if 11 <= j <= 13:
            c = RED[2] if j == 12 else RED[1]
            # small flame logo in the red band
            if j == 12 and abs(i - ctx.w / 2 + 0.5) < 1.0:
                return A(hx('#f2c84a'))
            return A(c)
        if j in (15,) and abs(i - ctx.w / 2 + 0.5) < 5 and i % 2 == 0:
            return A(INK[1])                                  # small print
        if (i, j) in ((3, 1), (4, 2), (20, 15), (21, 15), (22, 16)):
            return A(COAL[3])                                 # charcoal dust smudges
        return A(pick(KRAFT, v))
    return A(pick(KRAFT, v - 0.06))


def smile_mat(ctx, L):
    """The ear-to-ear grin (possessed toggle planes): lips, two rows of teeth, gums, black gaps.

    The grin's centre line rises from the mouth (y -24 at x = 0) to just in front of each ear (y -28.6 at the back of
    the side plane); its height tapers from 4.6 to 1.6 texels.  u = arc length from the centre."""
    t = tag(ctx)
    f = ctx.face
    x, y, z = ctx.pos
    if f not in ('front', 'back', 'west', 'east'):
        return None
    if t == 'smile_side':
        u = 8.0 + (z + 8.0)
    else:
        u = abs(x)
    yc = grin_center(u)
    hh = grin_half(u)
    dy = y - yc
    if abs(dy) > hh:
        return None
    # inner / outer band classification
    if dy < -hh + 1.0:
        return A(LIPP[2] if dy < -hh + 0.5 or u > 12 else LIPP[3])      # upper lip
    if dy > hh - 1.0:
        return A(LIPP[2])                                     # lower lip
    if abs(dy) < 0.5 and u > 4.0:
        return A(L['mouth'][0])                               # the black seam between the rows
    # teeth: tall narrow slats with dark gaps, a gum line at the root
    if t == 'smile_side':
        col = int(math.floor(z * 1.0))
    else:
        col = int(math.floor(x))
    gap = (col % 2 == 0) if u > 6 else (col % 3 == 0)
    upper = dy < 0
    root = (dy < -hh + 1.6) if upper else (dy > hh - 1.6)
    if gap and not root:
        return A(L['mouth'][1])
    if root:
        return A(GUM[1] if not gap else GUM[0])
    c = TEETH[4] if upper else TEETH[3]
    if (col * 7) % 5 == 0:
        c = TEETH[2]
    if u > 11:
        c = TEETH[2]
    return A(c)


def grin_center(u):
    """y of the grin's centre line at arc length u (u 0..8 on the front plane, 8..13 on the side planes)."""
    k = max(0.0, u - 3.0)
    return -24.0 - min(4.6, 0.09 * k * k)


def grin_half(u):
    return max(1.6, 2.4 - max(0.0, u - 6.0) * 0.12)


def eyes_mat(ctx, L):
    """Opaque possessed eyes (zero-thickness plane): black sclera, white pupils; transparent elsewhere."""
    if ctx.face != 'front':
        return None
    x, y, z = ctx.pos
    ch, c, r = face_char(x, y)
    if ch in ('W', 'L') and r in (7, 8):
        return A(hx('#040405'))
    if ch in ('I', 'i', 'g'):
        return A(hx('#ffffff') if ch != 'i' else hx('#e2e2e2'))
    return None


def eyes_glow(img, u0, v0, w, h):
    """'eyes' layer: the white pupils, full bright (the only emissive pixels on Jorge)."""
    px = img.load()
    for j in range(h):
        for i in range(w):
            x = DEMON_EYES_X0 + i + 0.5
            y = DEMON_EYES_Y0 + j + 0.5
            ch, c, r = face_char(x, y)
            if ch in ('I', 'g'):
                px[u0 + i, v0 + j] = (255, 255, 255, 255)
            elif ch == 'i':
                px[u0 + i, v0 + j] = (226, 232, 255, 255)


DEMON_EYES_X0, DEMON_EYES_Y0 = -7.0, -31.0

KINDS = {
    'skin': skin_mat, 'hair': hair_mat, 'shirt': shirt_mat, 'apron': apron_mat, 'shorts': shorts_mat,
    'sole': sole_mat, 'steel': steel_mat, 'bag': bag_mat, 'smile': smile_mat, 'eyes': eyes_mat,
}


def make_mat(look):
    L = LOOKS[look]

    def mat(ctx):
        kind = getattr(ctx.cube, 'kind', 'skin')
        return KINDS[kind](ctx, L)
    mat.look = look
    return mat


DEFAULT_MAT = make_mat('normal')
VARIANT_MATS = {'normal': DEFAULT_MAT, 'poseido': make_mat('poseido')}
FOCUS = 'head'

# ------------------------------------------------------------------ toggles (Java: ModelPart.visible)
TOGGLES = {
    'smile': 'poseido', 'smile_jaw': 'poseido', 'demon_eyes': 'poseido',   # shown with the possessed look
    'bag': 'carry_bag',                                                     # shown while carrying the charcoal
}


class JorgeModel(Model):
    """Exports every bone to Java; the preview / gallery JSON hides the toggle bones the current look hides."""
    show = ()

    def to_json(self):
        d = super().to_json()
        for bd in d['bones']:
            if bd['name'] in TOGGLES and bd['name'] not in self.show:
                bd['cubes'] = []
        return d


def _cli_value(flag):
    if flag in sys.argv:
        k = sys.argv.index(flag)
        if k + 1 < len(sys.argv):
            return sys.argv[k + 1]
    return None


# ------------------------------------------------------------------ rest pose (degrees)
ARM_OUT = 7.0           # arms angled out over the belly sides
ARM_FWD = -3.0
ELBOW = -12.0           # forearms a little forward
TONGS_TILT = 22.0       # tongs tips down
TONGS_OPEN = 7.0        # lower arm of the tongs sprung open
TOES_OUT = 10.0         # duck stance
BROW_DROOP = 8.0        # friendly droop of the outer brow ends


def build(variant=None):
    r = Rig()

    def bone(name, pivot, parent=None, rot=(0, 0, 0)):
        return r.bone(name, pivot, parent=parent, rot=rot)

    def box(b, frm, size, kind, name, inflate=0.0, decals=None, sx=1, **attrs):
        c = r.box(b, frm, size, inflate=inflate, decals=decals)
        c.kind = kind
        c.name = name
        c.sx = sx
        for k, v in attrs.items():
            setattr(c, k, v)
        return c

    # ---------------- body: pivot at the hips
    bone('body', (0, 3, 0))
    box('body', (-10.5, -3, -5.5), (21, 7, 11), 'shorts', 'hips')
    box('body', (-11, -19, -6), (22, 17, 12), 'shirt', 'torso')
    box('body', (-10, -20, -5), (20, 2, 11), 'shirt', 'yoke')
    box('body', (-6.5, -22, -5.5), (13, 2, 11), 'shirt', 'collar')
    box('body', (-7, -19, -7), (14, 7, 1), 'apron', 'bib')
    box('body', (-9, -20, -7.2), (4, 3, 0), 'shirt', 'collar_tip')
    box('body', (5, -20, -7.2), (4, 3, 0), 'shirt', 'collar_tip')
    box('body', (-4.5, -9, 6.15), (9, 5, 0), 'apron', 'bow')

    # ---------------- belly: three rounded steps, apron over the front
    bone('belly', (0, -10, -6), 'body')
    box('belly', (-10.5, -12, -9), (21, 3, 4), 'shirt', 'belly_top')
    box('belly', (-12, -10, -11), (24, 14, 6), 'shirt', 'belly_core')
    box('belly', (-10.5, -9, -13), (21, 12, 2), 'shirt', 'belly_front')
    bone('apron_skirt', (0, 3, -12.5), 'belly')
    box('apron_skirt', (-11.5, 3, -13), (23, 9, 1), 'apron', 'skirt')

    # ---------------- neck + head
    bone('neck', (0, -20, 0), 'body')
    box('neck', (-5, -23, -4.5), (10, 4, 9), 'skin', 'neck')
    bone('head', (0, -22, 0), 'neck')
    box('head', (-8, -37, -8), (16, 13, 16), 'skin', 'skull')
    box('head', (-8, -37, -8), (16, 11, 16), 'hair', 'hair', inflate=0.5)
    box('head', (-2, -38, -9), (3, 2, 3), 'hair', 'tuft')
    box('head', (-2, -30, -11), (4, 4, 3), 'skin', 'nose')
    box('head', (-10, -31, -1.5), (2, 5, 3), 'skin', 'ear', sx=-1)
    box('head', (8, -31, -1.5), (2, 5, 3), 'skin', 'ear', sx=1)
    bone('right_brow', (-2, -32, -8.5), 'head', rot=(0, 0, -BROW_DROOP))
    box('right_brow', (-7, -33, -9.5), (5, 2, 2), 'hair', 'brow', sx=-1)
    bone('left_brow', (2, -32, -8.5), 'head', rot=(0, 0, BROW_DROOP))
    box('left_brow', (2, -33, -9.5), (5, 2, 2), 'hair', 'brow', sx=1)
    bone('moustache', (0, -26, -8.5), 'head')
    box('moustache', (-6, -26, -10), (12, 3, 2), 'hair', 'moustache')
    box('moustache', (-7, -25, -9.5), (2, 3, 2), 'hair', 'moustache_end', sx=-1)
    box('moustache', (5, -25, -9.5), (2, 3, 2), 'hair', 'moustache_end', sx=1)
    bone('jaw', (0, -25, 2), 'head')
    box('jaw', (-8, -24, -8), (16, 4, 12), 'skin', 'jaw')
    box('jaw', (-6, -21, -7), (12, 2, 7), 'skin', 'chin2')
    # possessed toggles
    bone('smile', (0, -26, -8.2), 'head')
    box('smile', (-8, -29, -8.12), (16, 5, 0), 'smile', 'smile_front')
    box('smile', (-8.12, -30, -8), (0, 6, 5), 'smile', 'smile_side', sx=-1)
    box('smile', (8.12, -30, -8), (0, 6, 5), 'smile', 'smile_side', sx=1)
    bone('smile_jaw', (0, -25, 2), 'jaw')
    box('smile_jaw', (-8, -24, -8.12), (16, 3, 0), 'smile', 'smile_jaw')
    bone('demon_eyes', (0, -29.5, -8.25), 'head')
    box('demon_eyes', (DEMON_EYES_X0, DEMON_EYES_Y0, -8.25), (14, 3, 0), 'eyes', 'demon_eyes',
        decals={'eyes:front': eyes_glow})

    # ---------------- arms
    for side, sx in (('right', -1), ('left', 1)):
        arm, fa, hand = f'{side}_arm', f'{side}_forearm', f'{side}_hand'
        ax = 15.0 * sx
        bone(arm, (11.5 * sx, -17.5, 0), 'body', rot=(ARM_FWD, 0, -ARM_OUT * sx))
        box(arm, (ax - 4, -20, -4), (8, 8, 8), 'shirt', 'sleeve', sx=sx)
        box(arm, (ax - 3, -12, -3), (6, 5, 6), 'skin', 'upper_arm', sx=sx)
        bone(fa, (ax, -7.5, 0), arm, rot=(ELBOW, 0, 0))
        box(fa, (ax - 3, -8, -3), (6, 9, 6), 'skin', 'forearm', sx=sx, watch=(sx > 0))
        bone(hand, (ax, 1, 0), fa)
        if sx < 0:
            # the fist round the tongs grip
            box(hand, (ax - 2.5, 0.5, -3), (5, 5, 6), 'skin', 'fist', sx=sx)
            box(hand, (ax + 1.0, 0.0, -4.2), (2, 2, 3), 'skin', 'thumb', sx=sx)
            bone('tongs', (ax, 3, 0), hand, rot=(TONGS_TILT, 0, 0))
            box('tongs', (ax - 1, 2, -4), (2, 2, 9), 'steel', 'grip')
            box('tongs', (ax - 1, 2, -12), (2, 1, 8), 'steel', 'bar')
            box('tongs', (ax - 1.5, 1.5, -15), (3, 1, 3), 'steel', 'tip')
            box('tongs', (ax - 0.5, 1.5, 5), (1, 3, 1), 'steel', 'hinge')
            bone('tongs_lower', (ax, 4, 4.5), 'tongs', rot=(TONGS_OPEN, 0, 0))
            box('tongs_lower', (ax - 1, 3, -12), (2, 1, 8), 'steel', 'bar')
            box('tongs_lower', (ax - 1.5, 3.5, -15), (3, 1, 3), 'steel', 'tip_lo')
        else:
            # open hand: palm, thumb, index (own bone, for pointing), middle / ring / pinky (curl together)
            box(hand, (ax - 1.5, 0.5, -3), (3, 5, 6), 'skin', 'palm', sx=sx)
            box(hand, (ax - 2.0, 1.0, -4.6), (2, 4, 2), 'skin', 'thumb_l', sx=sx, inflate=-0.1)
            bone('left_index', (ax, 5.5, -2.4), hand, rot=(0, 0, 6))
            box('left_index', (ax - 1, 5.5, -3.4), (2, 5, 2), 'skin', 'finger', sx=sx, inflate=-0.25)
            bone('left_fingers', (ax, 5.5, 0.8), hand, rot=(0, 0, 12))
            box('left_fingers', (ax - 1, 5.5, -1.8), (2, 5, 2), 'skin', 'finger', sx=sx, inflate=-0.25)
            box('left_fingers', (ax - 1, 5.5, -0.2), (2, 5, 2), 'skin', 'finger', sx=sx, inflate=-0.25)
            box('left_fingers', (ax - 1, 5.5, 1.4), (2, 4, 2), 'skin', 'finger', sx=sx, inflate=-0.25)

    # ---------------- legs
    for side, sx in (('right', -1), ('left', 1)):
        leg, shin = f'{side}_leg', f'{side}_shin'
        lxc = 5.5 * sx
        bone(leg, (lxc, 3, 0), 'body', rot=(0, -TOES_OUT * sx, 0))
        box(leg, (lxc - 5, 3, -5), (10, 9, 10), 'shorts', 'shorts', sx=sx)
        box(leg, (lxc - 5, 10, -5), (10, 2, 10), 'shorts', 'cuff', sx=sx, inflate=0.3)
        bone(shin, (lxc, 12, 0), leg)
        box(shin, (lxc - 3, 12, -3), (6, 9, 6), 'skin', 'shin', sx=sx)
        box(shin, (lxc - 3.5, 21, -7), (7, 2, 10), 'skin', 'foot', sx=sx)
        box(shin, (lxc - 4, 23, -8), (8, 1, 12), 'sole', 'sole', sx=sx)

    # ---------------- the charcoal bag (toggle), hugged in front of the belly
    bone('bag', (0, 3, -18), 'body')
    box('bag', (-13, -14, -22), (26, 17, 9), 'bag', 'bag')
    box('bag', (-13.5, -16, -22.5), (27, 2, 10), 'bag', 'rim')
    box('bag', (-11, -17, -21), (22, 2, 7), 'bag', 'coal')

    m = JorgeModel('jorge', 256, 256, r.roots)
    m.scale = 0.5
    show = set()
    if variant == 'poseido':
        show |= {k for k, v in TOGGLES.items() if v == 'poseido'}
    if _cli_value('--pose') == 'carry_bag' or os.environ.get('JORGE_SHOW') == 'all':
        show.add('bag')
    if os.environ.get('JORGE_SHOW') == 'all':
        show |= set(TOGGLES)
    m.show = show
    return m


POSES = {}

ANIM_NOTES = """(written once the poses are final)"""
