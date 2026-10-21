"""Jorge Morales (46) -- dad, 'rey del asado', host #2 of the demon (DEAD LINE, case 2 'Casa Morales').

Authored at 2x texel density (model.scale = 0.5).  +Y down, ground y = 24, faces -Z, right_* on -X.  Centred on
x = 0, z = 0.  Height 1.9 blocks: skull top y = -37 -> soles y = 24 (61 texels; the combed tuft pokes to -38.5).
Texture 256 x 256.  Cube / bone counts: see ANIM_NOTES (and the preview printout).

Design
------
Silhouette: a PEAR on flip-flops.  Normal shoulders (22 + puffy short sleeves), then a beer belly that is the widest
and deepest thing on him: a dome built from four nested blocks (26 wide at the navel, sticking out 8.5 texels in
front of the chest), so it reads round from the front AND in profile.  The black apron rides over the dome and its
skirt swings off the bottom of the belly, angled back towards the thighs (the tent every asador's apron makes).
Khaki bermudas only show at the sides and the hem, two thin hairy shins, navy ojotas with the toes out (duck
stance).  A big head (16 x 17 face) with no neck: a double chin sits on the shirt collar.  The grill tongs in his
right fist are the only spike in the outline.

Face (front 16 x 17, hand placed in FACE, painted through the look so the possessed texture recolours it): tall
bald forehead with two furrows and a sweaty shine (receding hairline: bald temples, one combed tuft), two bushy brow
bones, droopy friendly eyes (heavy lids drooping at the outer corners, brown irises with a glint, bags), a big
bulbous red nose (own cube), ruddy cheeks, a thick walrus MOUSTACHE (own bone: a 12-wide block plus two drooping
ends) that hides the upper lip, then a smiling lower lip and a stubbled chin on the hinged jaw.

Wardrobe: short-sleeved shirt with vertical light-blue / white stripes (generic, no crest) and sweat stains, a gold
chain in the open collar; a black canvas apron: a cartoon cow on the bib, "REY" / "DEL" on the belly, "ASADO" on
the skirt (3 x 5 pixel letters, off-white), grease stains, stitched hem, neck strap and waist ties knotted in a bow
on his back; khaki bermudas with a belt and cargo pockets; navy rubber ojotas with white Y straps; stainless tongs
(two hinged arms: they clack).

Possessed look ('poseido', VARIANT_MATS index 1): grey-green skin with bruised eye sockets and a few black veins,
BLACK sclera with WHITE pupils, charred fingertips (he flips chorizos on the grill with his bare hands), soot on the
shirt, a singed apron hem.  Toggle geometry shown only in this look: 'demon_eyes' (plane over the eyes carrying
the emissive white pupils: the only 'eyes' layer pixels), 'smile' (the ear-to-ear grin: upper lip, upper teeth,
the corners climbing both cheeks and two side planes running back to the ears) and 'smile_jaw' (lower teeth and
lip, riding the jaw).  Steam at the neck is particles (Java).
"""
import math
import os
import sys

import numpy as np

from mcmodel import Model, hash3, face_light, pick, rot_matrix
from rig import Rig
from paint import hx, mix


# ------------------------------------------------------------------ palettes (hand-picked, hue shifted)
def H(*cs):
    return [hx(c) for c in cs]


SKIN_N = H('#2a1410', '#45201a', '#642f24', '#844334', '#a35a44', '#bc7255', '#cf8a69', '#dea27f', '#eabb98',
           '#f5d3b5')
SKIN_P = H('#0e1311', '#172019', '#212c24', '#2c392f', '#38473b', '#465748', '#566756', '#687865', '#7d8b77',
           '#949f8c')
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
TEETH = H('#3a3226', '#6b6048', '#9d9171', '#c8bf9f', '#e2dcc4', '#f4f0e0')
GUM = H('#2a0a10', '#4a1420', '#6e2432')
LIPP = H('#0c070c', '#1a0f18', '#2a1824', '#3a2432')
MOUTH_N = H('#1a0807', '#2e100d', '#4a1c16', '#6a2a20')
EMBER = H('#3a0a04', '#7a1e08', '#c8460e', '#ff8a24')
SOOT = hx('#141313')
VOID = hx('#050407')
PUPIL = hx('#f4f7ff')


# ------------------------------------------------------------------ looks
LOOKS = {
    'normal': {
        'skin': SKIN_N, 'poss': False,
        'spec': hx('#fbe6d2'), 'crease': SKIN_N[4], 'deep': SKIN_N[3],
        'lid': hx('#4a241b'), 'lid2': SKIN_N[4], 'sclera': hx('#efe7dc'),
        'iris': hx('#6b4424'), 'pupil': hx('#2a170c'), 'glint': hx('#fff8ee'),
        'bag': SKIN_N[5], 'ruddy': hx('#d4705f'), 'ruddy2': hx('#bd5a4c'), 'ruddy3': hx('#e48b74'),
        'lip': hx('#a24c40'), 'lip2': hx('#7a3429'), 'mouth': MOUTH_N,
        'stub': hx('#5f5058'), 'nail': hx('#f0cdb8'), 'nail2': hx('#c98f78'),
        'chest_hair': HAIR[2], 'socket': None, 'vein': None, 'tip': None,
    },
    'poseido': {
        'skin': SKIN_P, 'poss': True,
        'spec': hx('#a9b59e'), 'crease': SKIN_P[3], 'deep': SKIN_P[2],
        'lid': hx('#0a070b'), 'lid2': hx('#1b141d'), 'sclera': VOID,
        'iris': PUPIL, 'pupil': hx('#dfe6f4'), 'glint': PUPIL,
        'bag': hx('#2b2230'), 'ruddy': hx('#3e3a44'), 'ruddy2': hx('#332d38'), 'ruddy3': hx('#4a4750'),
        'lip': hx('#2a1c2a'), 'lip2': hx('#170f17'), 'mouth': H('#030303', '#08060a', '#120c14', '#1e1420'),
        'stub': hx('#1f2a23'), 'nail': hx('#2f3a30'), 'nail2': hx('#1c241e'),
        'chest_hair': HAIR[1], 'socket': (hx('#1c1620'), hx('#2b2330')), 'vein': hx('#0b120e'),
        'tip': True,
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


def rest_pos(ctx):
    """Texel centre in REST model space (the cube's own rest position, whatever the bone rotation)."""
    c = ctx.cube
    lx, ly, lz = local(ctx)
    return c.ax0 + lx, c.ay0 + ly, c.az0 + lz


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


def skin_base(L, v):
    return L['skin'][max(0, min(9, int(v * 10)))]


def stubble(L, base, i, j, amt=0.32):
    """5 o'clock shadow: two close tones on an ordered pattern (no salt-and-pepper noise)."""
    k = h2(i, j, 13)
    t = amt if ((i + 2 * j) % 3 == 0 or k > 0.72) else amt * 0.55
    return mix(base, L['stub'], t)


def hair_stroke(ctx, seed, p=0.5, cell=3):
    """Body hair: at most one short 2-texel slanted stroke per 3x3 cell (never clumps into blotches).

    Returns 0 (skin), 1 (stroke root, darker) or 2 (stroke tip, softer)."""
    i, j = ctx.i, ctx.j
    for (ci, cj) in ((i // cell, j // cell), ((i - 1) // cell, (j - 1) // cell)):
        if h2(ci * 5 + 1, cj * 7 + 3, seed) > p:
            continue
        oi = int(h2(ci, cj, seed + 1) * (cell - 1))
        oj = int(h2(cj, ci, seed + 2) * (cell - 1))
        ri, rj = ci * cell + oi, cj * cell + oj
        if (i, j) == (ri, rj):
            return 1
        if (i, j) == (ri + 1, rj + 1):
            return 2
    return 0


# ------------------------------------------------------------------ the face (16 x 17, painted through the look)
# col c <-> x in [-8 + c, -7 + c]; row r <-> y in [-37 + r, -36 + r].  Skull rows 0..11 (y -37..-25), jaw rows
# 12..16 (y -25..-20).  Covered by geometry: brows (cols 1-6 / 9-14, rows 4-5), nose (cols 6-9, rows 6-9),
# moustache (cols 2-13, rows 10-12; the drooping ends cols 0-2 / 13-15, rows 11-14).  What shows under them is
# painted sensibly anyway (the brows, the moustache and the jaw move).
#   0-9 skin ramp   w specular   k soft crease   K deep crease   L lid line   W sclera   I iris   i pupil side
#   g glint   b eye bag   l lower lid   r R q ruddy (mid / dark / light)   p P lower lip (lit / corner)
#   m mouth   s stubble   h hair at the temple corners
GX0, GY0 = -8.0, -37.0
FACE = [
    # 0123456789012345
    "h566777777776 5h".replace(' ', '6'),   # r0  y-37  top of the forehead (bald: the hair recedes)
    "5667kk7w87kk7665",   # r1  y-36  first furrow (two short bits) + sweaty shine
    "5678888ww8888765",   # r2  y-35
    "566kkk7887kkk665",   # r3  y-34  second furrow
    "5566777887776655",   # r4  y-33  (brows)
    "4455566776655544",   # r5  y-32  (brows)
    "44LLLL6776LLLL44",   # r6  y-31  heavy upper lids
    "4kLgIW6776WgILk4",   # r7  y-30  eyes: lids droop over the outer corners, 2x2 iris with a glint
    "45WIiW6776WiIW54",   # r8  y-29
    "45lbbl6776lbbl54",   # r9  y-28  lower lid + bags (nose cube over cols 6-9)
    "45qrrR5665Rrrq54",   # r10 y-27  ruddy cheeks (moustache from here down)
    "4sRRr555555rRRs4",   # r11 y-26
    "4ssmmmmmmmmmmss4",   # r12 y-25  jaw top: mouth line (under the moustache)
    "4ssPppppppppPss4",   # r13 y-24  lower lip, smiling (corners shaded)
    "4sss55k66k55sss4",   # r14 y-23  under the lip
    "4sss55666655sss4",   # r15 y-22  chin
    "3sssss5555sssss3",   # r16 y-21
]
assert all(len(r) == 16 for r in FACE), [len(r) for r in FACE]
# possessed: bruised sockets round the eyes (S = socket, s = soft socket) and hand-placed black veins (v)
SOCKET = [
    "................",
    "................",
    "................",
    "................",
    "................",
    ".ssSSSs..sSSSss.",
    ".S..............",
    ".S............S.",
    ".S............S.",
    ".sS....  ....Ss.".replace(' ', '.'),
    "..sSSs....sSSs..",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
]
VEINS = [
    "v..............v",
    ".v............v.",
    ".v............v.",
    "..v..........v..",
    "................",
    "................",
    "................",
    "v..............v",
    "v..............v",
    "................",
    "v..............v",
    ".v............v.",
    "................",
    "................",
    "................",
    "v..............v",
    "v..............v",
]
assert all(len(r) == 16 for r in SOCKET + VEINS)


def face_char(x, y):
    c = int(math.floor(x - GX0))
    r = int(math.floor(y - GY0))
    if 0 <= r < len(FACE) and 0 <= c < 16:
        return FACE[r][c], c, r
    return None, c, r


def face_rgba(ch, L, c, r):
    S = L['skin']
    if L['poss']:
        if VEINS[r][c] == 'v' and ch not in 'LWIigb':
            return L['vein']
        sk = SOCKET[r][c]
        if sk == 'S' and ch not in 'LWIig':
            return L['socket'][0]
        if sk == 's' and ch not in 'LWIig':
            return L['socket'][1]
        if ch in 'pP':
            return L['lip'] if ch == 'p' else L['lip2']
    if ch.isdigit():
        return S[int(ch)]
    if ch == 'h':
        return HAIR[3]
    if ch == 'w':
        return L['spec']
    if ch == 'k':
        return L['crease']
    if ch == 'K':
        return L['deep']
    if ch == 'L':
        return L['lid']
    if ch == 'l':
        return L['lid2']
    if ch == 'W':
        return L['sclera']
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
    if ch == 'p':
        return L['lip']
    if ch == 'P':
        return L['lip2']
    if ch == 'm':
        return L['mouth'][1]
    if ch == 's':
        return stubble(L, S[5], c, r)
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
    'O': [".#.", "#.#", "#.#", "#.#", ".#."],
    'C': [".##", "#..", "#..", "#..", ".##"],
    'B': ["##.", "#.#", "##.", "#.#", "##."],
    'N': ["#..#", "##.#", "#.##", "#..#", "#..#"],
}


def text_mask(word):
    """-> set of (col, row) lit pixels and the width.  An 'O' with an accent is written 'Ó' (accent on row -1)."""
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

# the cartoon cow on the bib (12 x 7): horns, pink ears, white head with a black patch, eyes, big pink snout
COW = [
    ".H........H.",
    "EHwwwKKwwwHE",
    ".EwwKKKwwwE.",
    "..wOwwwwOw..",
    "..PPPPPPPP..",
    "..PnPPPPnP..",
    "...PPPPPP...",
]
assert all(len(r) == 12 for r in COW)


# ------------------------------------------------------------------ skin, head, limbs
def skin_mat(ctx, L):
    t = tag(ctx)
    f = ctx.face
    S = L['skin']
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    x, y, z = rest_pos(ctx)
    poss = L['poss']

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
            if z < 3.0:
                return A(L['mouth'][0] if abs(x) < 6.5 else L['mouth'][1])
            return A(S[2])
        if f == 'top':
            if abs(x + 2) < 1.0 and abs(z + 4.5) < 1.0:
                return A(L['spec'])                          # shine on the bald crown
            return A(skin_base(L, 0.74 + (0.06 if (abs(x) < 5 and z < -2) else 0.0)))
        if f == 'back':
            return A(skin_base(L, 0.44))                     # nape under the hair line (the shell covers the rest)
        # sides: temple, cheek, jaw corner (the ear and the hair shell sit on top)
        v = 0.56 + (0.06 if z < -4.0 else 0.0)
        if z < -5.5 and -29 < y < -26:
            return A(L['ruddy2'] if not poss else S[3])      # the cheek turning to the front
        if y > -27.0:
            return A(stubble(L, skin_base(L, v - 0.06), ctx.i, ctx.j))
        if poss and abs((z + 3.0) - (y + 31.0) * 0.8) < 0.5 and -35 < y < -29 and z < -1:
            return A(L['vein'])                              # a vein crawling from the eye to the temple
        return A(skin_base(L, v))

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
            return A(stubble(L, S[3], ctx.i, ctx.j, 0.25))
        if f == 'back':
            return A(S[2])
        v = 0.52 - (ly / h) * 0.12                           # sides: the jaw line, stubbled
        return A(stubble(L, skin_base(L, v), ctx.i, ctx.j))

    if t == 'chin2':
        if f in ('back', 'top'):
            return None
        if f == 'bottom':
            return A(S[2])
        if f == 'front' and ctx.j == 0:
            return A(S[3])                                   # the fold under the chin
        v = 0.46 + face_light(ctx) * 0.6
        return A(stubble(L, skin_base(L, v), ctx.i, ctx.j, 0.28))

    if t == 'nose':
        if f == 'back':
            return None
        i, j = ctx.i, ctx.j
        if f == 'front':
            if poss:
                rows = [
                    [S[5], S[6], S[6], S[5]],
                    [S[5], S[7], S[6], L['ruddy3']],
                    [L['ruddy'], L['ruddy3'], L['ruddy'], L['ruddy2']],
                    [L['ruddy2'], L['ruddy'], L['ruddy'], L['ruddy2']],
                ]
            else:
                rows = [
                    [S[6], S[7], S[7], S[6]],
                    [S[6], L['spec'], S[8], L['ruddy3']],
                    [L['ruddy'], L['ruddy3'], L['ruddy'], L['ruddy2']],
                    [L['ruddy2'], L['ruddy'], L['ruddy'], L['ruddy2']],
                ]
            return A(rows[j][i])
        if f == 'bottom':
            if lz < 1.0 and (0.5 < lx < 1.5 or 2.5 < lx < 3.5):
                return A(L['mouth'][1])                       # nostrils
            return A(L['ruddy2'] if not poss else S[3])
        if f == 'top':
            return A(S[7] if lz < 1.5 else S[6])
        c = S[6] if f == 'west' else S[5]                     # sides: lit west, shadowed east; ruddy tip
        if ly > 2.0:
            c = L['ruddy'] if f == 'west' else L['ruddy2']
        return A(c)

    if t == 'ear':
        outer = (f == 'west' and x < 0) or (f == 'east' and x > 0)
        if outer:
            i, j = ctx.i, ctx.j                               # helix rim lit, concha dark, lobe at the bottom
            if j == 0 or i == (2 if f == 'west' else 0):
                return A(S[7])
            if 1 <= j <= 3 and i == 1:
                return A(S[3])
            return A(S[6] if j < 4 else S[5])
        if f == 'front':
            return A(S[6] if ctx.j < 4 else S[5])
        if f == 'top':
            return A(S[7])
        return A(S[4])

    if t == 'neck':
        if f in ('top', 'bottom'):
            return None
        if f == 'back':
            if poss and ctx.i in (3, 7) and ctx.j < 4:
                return A(L['vein'])
            if ctx.j < 2 and h2(ctx.i, ctx.j, 5) > 0.6:
                return A(HAIR[3])                             # the nape hairline
            return A(skin_base(L, 0.48))
        return A(stubble(L, skin_base(L, 0.44), ctx.i, ctx.j, 0.25))

    # ---------------- arms
    if t == 'upper_arm':
        if f == 'top':
            return None
        v = 0.6 + face_light(ctx) * 0.9
        if ly < 1.0:
            v -= 0.18                                         # shadow under the sleeve
        if f == inner_face(ctx):
            v -= 0.08
        return A(skin_base(L, v))

    if t == 'forearm':
        if f == 'top':
            return A(S[4])
        v = 0.62 + face_light(ctx) * 0.9
        if f == inner_face(ctx):
            v -= 0.06
        side = f in ('front', 'back', 'west', 'east')
        if side and ly > h - 1.0:
            v -= 0.05                                         # wrist
        if getattr(ctx.cube, 'watch', False) and side and h - 2.6 < ly < h - 0.8:
            if f == outer_face(ctx):                          # the watch: steel case + face on the outer wrist
                return A(STEEL[7] if 2.0 < lz < 4.0 and ly < h - 1.6 else STEEL[5])
            return A(STEEL[4] if ly < h - 1.7 else STEEL[3])
        if side and f != inner_face(ctx):
            hs = hair_stroke(ctx, 31 + (side_of(ctx) > 0), 0.45 if f == outer_face(ctx) else 0.25)
            if hs:
                return A(mix(skin_base(L, v), HAIR[2], 0.42 if hs == 1 else 0.24))
        if poss and side and h2(ctx.i, ctx.j // 2, 33) > 0.9:
            return A(mix(skin_base(L, v), SOOT, 0.5))
        return A(skin_base(L, v))

    if t == 'palm':
        v = 0.62 + face_light(ctx) * 0.9
        if f == inner_face(ctx):                              # the palm: lighter, a crease; burned when possessed
            if poss:
                if h2(ctx.i, ctx.j, 34) > 0.55:
                    return A(COAL[3])
                return A(mix(skin_base(L, v), EMBER[0], 0.45))
            if abs(ly - 2.5) < 0.5 and lz > 1.0:
                return A(S[5])
            return A(skin_base(L, v + 0.06))
        if f == outer_face(ctx):
            if ly > h - 1.0:
                return A(S[7] if ctx.i % 2 == 0 else S[6])    # knuckles
            hs = hair_stroke(ctx, 45, 0.35)
            if hs == 1:
                return A(mix(skin_base(L, v), HAIR[2], 0.35))
        if f == 'bottom':
            return A(S[5])
        return A(skin_base(L, v))

    if t == 'thumb':
        if f == 'top':
            return A(S[5])
        if f == 'bottom':
            return A(COAL[2] if poss else S[7])
        if poss and ly > h - 1.5:
            return A(COAL[3] if ctx.i % 2 else EMBER[1])
        if f == 'front' and ly > h - 1.5:
            return A(L['nail'])
        return A(skin_base(L, 0.62 + face_light(ctx) * 0.8))

    if t == 'finger':
        if f == 'top':
            return A(S[4])
        if f == 'bottom':
            return A(COAL[2] if poss else S[7])               # fingertip
        if poss and ly > h - 1.6:
            # charred fingertips: black with an ember crack (he flips the chorizos with his bare hands)
            return A(EMBER[2] if (ctx.i + ctx.j) % 3 == 0 and f != 'back' else COAL[2])
        if ly > h - 1.4 and f == outer_face(ctx):
            return A(L['nail'] if ly < h - 0.5 else L['nail2'])
        v = 0.62 + face_light(ctx) * 0.9
        if abs(ly - 2.0) < 0.5:
            v -= 0.14                                         # knuckle crease
        if f == inner_face(ctx):
            v += 0.04
        if f in ('front', 'back'):
            v -= 0.08                                         # the gaps between the fingers
        return A(skin_base(L, v))

    # ---------------- legs
    if t == 'shin':
        if f == 'top':
            return None
        v = 0.6 + face_light(ctx) * 0.9
        if ly < 1.5:
            v -= 0.16                                         # shadow under the bermuda hem
        if f == 'front':
            v += 0.05 if 2 <= ctx.i <= 3 else 0.0             # shin bone catches the light
        if f == 'back' and 2 < ly < 6:
            v += 0.03                                         # the calf
        if ly > h - 1.5:
            v -= 0.05                                         # ankle
        if f != inner_face(ctx) and ly > 1.5:
            hs = hair_stroke(ctx, 51 + (side_of(ctx) > 0), 0.5)
            if hs:
                return A(mix(skin_base(L, v), HAIR[2], 0.4 if hs == 1 else 0.22))
        return A(skin_base(L, v))

    if t == 'foot':
        sx = side_of(ctx)
        i, j = ctx.i, ctx.j
        big_x = (w - 2.0) if sx < 0 else 2.0                  # x of the toe post (big toe on the inner side)
        if f == 'top':
            u = lx
            zz = lz                                           # 0 = heel .. d = toes
            if zz > d - 2.5:
                big = (u > w - 2.0) if sx < 0 else (u < 2.0)
                k = int(w - 2.0 - u) if sx < 0 else int(u - 2.0)
                split = (not big) and ((u - (2.0 if sx > 0 else 0)) % 1.25 < 0.3)
                if (big and abs(u - big_x) < 0.4) or split:
                    return A(S[3])
                if zz > d - 1.2:
                    if poss:
                        return A(L['nail2'])
                    return A(L['nail'] if big or k % 2 == 0 else L['nail2'])
                return A(S[7] if big else S[6])
            post_z = d - 2.5                                  # the Y strap from the toe post back to both sides
            t_ = (post_z - zz) / 4.0
            if 0.0 <= t_ <= 1.0:
                sx0 = big_x + (0 - big_x) * t_
                sx1 = big_x + (w - big_x) * t_
                if abs(u - sx0) < 0.7 or abs(u - sx1) < 0.7:
                    return A(STRAP[3] if abs(u - big_x) < 1.2 else STRAP[2])
            return A(skin_base(L, 0.66 - (d - zz) * 0.01))
        if f == 'front':
            big = (lx > w - 2.0) if sx < 0 else (lx < 2.0)
            if j == 0:
                return A(S[7] if big else S[6])
            if not big and int(lx * 0.8) % 2 == 1:
                return A(S[4])
            return A(S[6] if big else S[5])
        if f in ('west', 'east'):
            if abs(lz - (d - 6.5)) < 0.8:
                return A(STRAP[2])                            # the strap ends anchored to the sole
            return A(skin_base(L, 0.52 + (0.04 if f == 'west' else 0)))
        return A(S[4])

    return A(skin_base(L, 0.6 + face_light(ctx) * 0.9))


def hair_mat(ctx, L):
    """Dark brown-black hair greying at the sideburns; bushy brows; the walrus moustache."""
    t = tag(ctx)
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    x, y, z = rest_pos(ctx)
    i, j = ctx.i, ctx.j
    if t == 'hair':
        ax = abs(x)
        if f in ('front', 'bottom'):
            return None
        if f == 'top':
            # receding hairline: bald temples, a central lock that comes forward to the tuft
            zf = -5.0 + 4.2 * min(1.0, max(0.0, (ax - 1.0) / 4.0)) - 1.6 * max(0.0, (ax - 5.5) / 2.5)
            if z < zf - 0.6:
                return None
            if z < zf + 0.6 and h2(i, j, 21) > 0.5:
                return None                                   # thin, broken hairline
            u = x * 0.9 + z * 0.15
            v = 0.42 + (0.12 if int(u * 1.3) % 3 == 0 else 0.0) - (z + 8) * 0.008
            if ax > 6.5:
                return A(mix(pick(HAIR, v), GREY[2], 0.35))
            return A(pick(HAIR, v))
        if f in ('west', 'east'):
            if z < -2.6:
                return None                                   # bald temple
            if z < -0.4:                                      # sideburn, greying
                if y > -27.6:
                    return None
                g = 0.5 + 0.2 * h2(i, j, 22)
                return A(GREY[1] if g > 0.62 else GREY[0] if g > 0.56 else HAIR[3])
            if -1.6 < z < 1.6 and y > -31.4:
                return None                                   # the ear comes through here
            if y > -27.4:
                return None
            v = 0.36 + (0.12 if (i + j // 3) % 4 == 0 else 0.0) + (0.06 if y < -34 else 0.0)
            c = pick(HAIR, v)
            if y > -32 and z < 3.0:
                c = mix(c, GREY[2], 0.35)                     # salt and pepper over the ear
            return A(c)
        if f == 'back':
            nape = -27.0 + (0.6 if int(x + 9) % 3 == 0 else 0.0)
            if y > nape:
                return None
            v = 0.32 + (0.12 if (i + j // 2) % 4 == 0 else 0.0) + (0.08 if y < -34 else 0.0)
            return A(pick(HAIR, v))
        return None

    if t == 'tuft':
        if f == 'bottom':
            return None
        v = 0.5 + face_light(ctx) * 0.8 + (0.12 if i % 2 == 0 else 0.0)
        if f == 'front' and j == ctx.h - 1 and i == 1:
            return None                                       # the lock ends in two points
        return A(pick(HAIR, v))

    if t == 'brow':
        if f == 'back':
            return None
        outer = (i == 0) if x < 0 else (i == ctx.w - 1)
        if f == 'front':
            if j == 0:
                if outer:
                    return None                               # tapered outer tip
                return A(HAIR[4] if (i % 2 == 0) else HAIR[3])
            return A(HAIR[2] if not outer else HAIR[1])
        if f == 'top':
            return A(HAIR[4] if i % 2 == 0 else HAIR[3])
        if f == 'bottom':
            return A(HAIR[1])
        return A(HAIR[2])

    if t in ('moustache', 'moustache_end'):
        if f == 'back':
            return None
        if f == 'front':
            # combed strands: irregular 1-texel strands, lit along the top, darker ragged tips; never even bands
            k = h2(i + (40 if t == 'moustache_end' else 0) + (20 if x > 0 else 0), 1, 23)
            v = 0.36 + k * 0.16
            if j == 0:
                v += 0.12                                     # the light catches the top
            elif j >= ctx.h - 1:
                v -= 0.1 + 0.08 * h2(i, 9, 26)                # tips
            if t == 'moustache' and abs(x) < 0.6:
                v -= 0.12                                     # the parting under the nose
            c = pick(HAIR, v)
            if j == 1 and h2(i, j, 24) > 0.88:
                c = GREY[1]                                   # a couple of grey hairs
            if L['poss'] and j >= ctx.h - 1 and h2(i, j, 25) > 0.6:
                c = EMBER[0]                                  # singed tips
            return A(c)
        if f == 'top':
            return A(HAIR[4] if h2(i, j, 27) > 0.5 else HAIR[3])
        if f == 'bottom':
            return A(HAIR[1])
        k = h2(j, i, 28)
        return A(HAIR[3] if j == 0 else HAIR[2] if k > 0.4 else HAIR[1])
    return A(HAIR[2])


# ------------------------------------------------------------------ shirt + apron
def stripe_col(u, v):
    if int(math.floor(u)) % 4 < 2:
        return pick(CELESTE, v)
    return pick(WHITE, v + 0.08)


def apron_hw(y):
    """Half width of the apron on front / top faces: the bib, then wider over the belly."""
    if y < -12.0:
        return 7.0
    if y < -11.0:
        return 8.0
    if y < -10.0:
        return 8.5
    if y < -9.0:
        return 9.5
    return 10.0


def soot(ctx, L, c, x, y, seed):
    """Possessed: a few deliberate charcoal smudges (thumb-sized, not noise)."""
    if not L['poss']:
        return c
    for (sx_, sy_, rad) in SMUDGES:
        if (x - sx_) ** 2 + (y - sy_) ** 2 < rad * rad:
            return mix(c, SOOT, 0.55 if h2(ctx.i, ctx.j, seed) > 0.3 else 0.35)
    return c


SMUDGES = [(-11.5, -9.0, 1.6), (12.2, -4.0, 1.4), (-6.0, -15.5, 1.2), (8.0, -17.0, 1.0), (3.0, -6.0, 1.5)]


def shirt_mat(ctx, L):
    t = tag(ctx)
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    x, y, z = rest_pos(ctx)
    side = f in ('front', 'back', 'west', 'east')
    v = 0.6 + face_light(ctx) * 1.0
    if f in ('west', 'east'):
        v -= 0.05
    u = x if f in ('front', 'back', 'top', 'bottom') else z

    if t == 'torso':
        if f == 'bottom':
            return None
        if f == 'front' and abs(x) < apron_hw(y):
            return A(APRON[2])                                # behind the bib (never seen)
        if side and edge(ctx) == 0:
            v -= 0.06
        if f == 'top':
            if 5.5 < abs(x) < 7.0 and z < -2.5:
                return A(APRON[3])                            # the apron neck strap over the shoulders
            v += 0.04
        if f in ('west', 'east'):
            dz, dy = z / 4.0, (y + 15.5) / 4.0
            if dz * dz + dy * dy < 1.0:
                v -= 0.12                                     # sweat stain under the arm
            if -5.0 <= y < -4.0:
                return A(APRON[3])                            # the waist ties running round to the back
        if f == 'back':
            hw = 5.5 - (y + 18.0) * 0.45
            if -18.0 < y < -9.0 and abs(x) < hw:
                v -= 0.1                                      # a V of sweat between the shoulder blades
            if -5.0 <= y < -4.0:
                return A(APRON[3])
            if 5.5 < abs(x) < 7.0 and y < -17.0:
                return A(APRON[3])                            # the neck strap ends
            if abs(x) < 0.5 and y > -16:
                v -= 0.08                                     # back seam
            if y > -3.0:
                v -= 0.06                                     # the tail of the shirt over the belt
        c = stripe_col(u, v)
        return A(soot(ctx, L, c, x, y, 61))

    if t == 'yoke':
        if f == 'bottom':
            return None
        if f == 'top':
            if 5.5 < abs(x) < 7.0:
                return A(APRON[4])                            # neck strap over the shoulder
            v += 0.08
        if f == 'front' and abs(x) < 7.0:
            return A(APRON[2])
        if f == 'back' and 5.5 < abs(x) < 7.0:
            return A(APRON[3])
        return A(stripe_col(u, v + 0.04))

    if t == 'collar':
        # stand-up collar round the neck: white band, open V at the front (throat, chest hair, gold chain)
        if f == 'bottom':
            return None
        if f == 'top':
            if abs(x) < 4.6 and abs(z) < 4.0:
                return None
            return A(pick(WHITE, 0.82))
        if f == 'front':
            if abs(x) < 2.5:
                if ctx.j == ctx.h - 1 and abs(x) < 1.5:
                    return A(BRASS[3] if int(x + 3) % 2 else BRASS[4])     # gold chain
                if h2(ctx.i, ctx.j, 41) > 0.5:
                    return A(L['chest_hair'])
                return A(skin_base(L, 0.5))
            if abs(x) < 3.5:
                return A(pick(WHITE, 0.5))
        if f in ('west', 'east', 'back') and ctx.j == ctx.h - 1:
            return A(APRON[3])                                # the apron's neck strap
        return A(pick(WHITE, v + 0.1 - (0.08 if ctx.j == ctx.h - 1 else 0.0)))

    if t == 'collar_tip':
        # a collar point lying on the chest beside the bib: a triangle (zero-thickness plane)
        if f not in ('front', 'back'):
            return None
        i, j = ctx.i, ctx.j
        inner = (ctx.w - 1 - i) if x < 0 else i               # 0 next to the bib
        if f == 'back':
            inner = i if x < 0 else (ctx.w - 1 - i)
        if j > inner + 0.5:
            return None
        if j == inner:
            return A(pick(WHITE, 0.55))
        return A(pick(WHITE, 0.86 - j * 0.04))

    if t == 'sleeve':
        if f == 'top':
            return None
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
                v -= 0.1                                      # sweat under the arm
        if ly < 1.0 and f != inner_face(ctx):
            v += 0.06                                         # shoulder seam catches light
        c = stripe_col(uu, v)
        if L['poss'] and ly > h - 1.5 and h2(ctx.i, 0, 62) > 0.6:
            c = mix(c, EMBER[0], 0.45)                        # singed hem
        return A(c)

    # ---------------- belly: shirt round the sides, apron over the front of the dome
    if t.startswith('belly'):
        if f == 'back':
            return None
        if t == 'belly_cap' or t.startswith('belly_round'):
            if f == 'bottom':
                return A(pick(APRON, 0.22))
            if f in ('west', 'east'):
                if lz < 1.0:
                    return A(pick(APRON, 0.5))                # the apron wraps one texel round the dome
                c = stripe_col(z, v - 0.02 - (0.06 if y > 0.5 else 0.0))
                return A(soot(ctx, L, c, x, y, 64))
            return A(apron_paint(ctx, L, t, x, y))
        if f in ('front', 'top') and abs(x) < apron_hw(y):
            return A(apron_paint(ctx, L, t, x, y))
        if f == 'bottom':
            v = 0.3                                           # under the belly, in shadow
        if f in ('west', 'east'):
            v -= 0.02
            # the shirt pulled tight over the belly: curved stress folds
            if abs((y + 2.0) - (z + 9.0) * 0.6) < 0.5 or abs((y + 8.0) - (z + 9.0) * 0.5) < 0.5:
                v -= 0.09
        if f in ('front', 'west', 'east') and -5.0 <= y < -4.0:
            return A(APRON[3])                                # the waist tie leaving the apron
        if f == 'front' and abs(x) > 11.5:
            v -= 0.05
        c = stripe_col(u, v)
        return A(soot(ctx, L, c, x, y, 63))
    return A(stripe_col(u, v))


def apron_paint(ctx, L, t, x, y):
    """Black canvas on the belly: stitched / folded edges, grease, REY / DEL on the dome's front."""
    f = ctx.face
    i, j = ctx.i, ctx.j
    v = 0.42 + face_light(ctx) * 0.8
    if f in ('west', 'east'):
        v -= 0.06
    if h2(i * 3 + j, j * 7, 71) > 0.9:
        v += 0.05                                             # canvas weave sparkle
    if t == 'belly_cap' and f == 'front':
        if i == 0 or i == ctx.w - 1:
            return pick(APRON, v + 0.14)                      # folded edge
        if j == ctx.h - 1:
            v -= 0.06                                         # the dome turns under
        ox = (ctx.w - W_REY) // 2
        if (i - ox, j) in TXT_REY:
            return letter(i - ox, j)
        ox = (ctx.w - W_DEL) // 2
        if (i - ox, j - 6) in TXT_DEL:
            return letter(i - ox, j - 6)
        if (i, j) in ((16, 6), (17, 6), (17, 7), (2, 2)):
            return GREASE[2] if (i, j) == (16, 6) else GREASE[1]
        if L['poss'] and (i, j) in ((3, 8), (4, 8), (4, 9), (15, 2)):
            return mix(pick(APRON, v), hx('#3a2a20'), 0.5)
        return pick(APRON, v)
    if f == 'top':
        v += 0.1                                              # the lip of each step catches the light
        if t == 'belly_cap' and ctx.j == ctx.h - 1:
            v += 0.06
    if f == 'front' and abs(x) > apron_hw(y) - 1.0:
        v += 0.12                                             # the apron edge
    return pick(APRON, v)


def letter(c, r):
    """Off-white print, a touch brighter on top, worn on the bottom row."""
    if r == 4:
        return LETTER[2]
    if r == 0:
        return LETTER[4]
    return LETTER[3]


def apron_mat(ctx, L):
    t = tag(ctx)
    f = ctx.face
    i, j = ctx.i, ctx.j
    v = 0.42 + face_light(ctx) * 0.8
    if h2(i * 3 + j, j * 7 + 1, 73) > 0.9:
        v += 0.05
    if t == 'bib':
        if f == 'back':
            return None
        if f == 'front':
            if i == 0 or i == ctx.w - 1:
                v += 0.14                                     # folded edge
            ox = (ctx.w - 12) // 2
            ci, cj = i - ox, j - 1
            if 0 <= ci < 12 and 0 <= cj < 7:
                ch = COW[cj][ci]
                cow = {'H': HORN[1], 'E': COW_P[1], 'w': COW_W[2], 'K': COW_K[0], 'O': COW_K[0],
                       'P': COW_P[2], 'n': COW_P[0]}.get(ch)
                if ch == 'w' and cj >= 2 and ci in (2, 9):
                    cow = COW_W[1]                            # shade down the cheeks
                if ch == 'P' and cj == 6:
                    cow = COW_P[1]
                if ch == 'H' and cj == 1:
                    cow = HORN[0]
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
                if L['poss'] and h2(i, j, 74) > 0.35:
                    return A(EMBER[1] if h2(i, j, 75) > 0.6 else hx('#4a2a14'))     # singed hem
                return A(pick(APRON, v + 0.1))                # hem
            if j == ctx.h - 2 and i % 3 != 1:
                return A(pick(APRON, v + 0.2))                # stitched hem line
            ox = (ctx.w - W_ASADO) // 2
            if (i - ox, j - 1) in TXT_ASADO:
                return A(letter(i - ox, j - 1))
            stains = {(3, 6): 1, (4, 6): 2, (17, 0): 1, (18, 1): 2}
            if (i, j) in stains:
                return A(GREASE[stains[(i, j)]])
            if j == 0:
                v -= 0.08                                     # shadow under the belly
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
    return A({'X': APRON[5], 'o': APRON[3], 'K': APRON[6]}[ch])


def shorts_mat(ctx, L):
    t = tag(ctx)
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    x, y, z = rest_pos(ctx)
    v = 0.56 + face_light(ctx) * 1.0
    if f in ('west', 'east'):
        v -= 0.05
    side = f in ('front', 'back', 'west', 'east')
    if t == 'hips':
        if f == 'bottom':
            return None
        if f == 'top':
            return A(pick(KHAKI, 0.4))
        if 3.0 < ly < 5.0:
            # the belt under the belly
            if side and (int(around(ctx)) % 9 == 4):
                return A(pick(KHAKI, v - 0.05))               # belt loop
            return A(pick(BELT, 0.5 + face_light(ctx) * 0.8 + (0.12 if ly < 4.0 else 0.0)))
        if ly < 3.0:
            return A(stripe_col(around(ctx), v - 0.08))       # shirt tucked in (seen at the back)
        if f == 'back' and 5.0 < ly and abs(abs(x) - 5.0) < 2.6:
            return A(pick(KHAKI, v - 0.12))                   # back pocket tops
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
            v -= 0.08                                         # creases
        if side and edge(ctx) == 0:
            v -= 0.05
        return A(pick(KHAKI, v))
    return A(pick(KHAKI, v))


def sole_mat(ctx, L):
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    if f == 'top':
        v = 0.6
        if lz < 4.0 and abs(lx - w / 2) < 2.5:
            v -= 0.12                                         # worn where the heel sits
        return A(pick(RUBBER, v))
    if f == 'bottom':
        return A(RUBBER[0] if (ctx.i + ctx.j) % 3 else RUBBER[1])
    return A(RUBBER[5] if ctx.j == 0 and ctx.h > 1 else RUBBER[3] if f != 'back' else RUBBER[2])


def steel_mat(ctx, L):
    t = tag(ctx)
    f = ctx.face
    lx, ly, lz = local(ctx)
    v = 0.55 + face_light(ctx) * 1.2
    if t == 'grip':
        if f in ('top', 'west', 'east', 'bottom'):
            return A(GRIP[3] if int(lz) % 2 == 0 and f == 'top' else GRIP[2] if int(lz) % 2 == 0 else GRIP[1])
        return A(GRIP[2])
    if t in ('tip', 'tip_lo'):
        if f == 'front' and ctx.i % 2 == 1:
            return None                                       # scalloped head
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
    if L['poss'] and t in ('tip', 'tip_lo', 'bar'):
        c = mix(c, hx('#2a3a8a'), 0.25)                       # blued by the blue fire
    return A(c)


def bag_mat(ctx, L):
    t = tag(ctx)
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    i, j = ctx.i, ctx.j
    v = 0.56 + face_light(ctx) * 1.0
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
        if abs(lz - d / 2) < 0.6:
            v -= 0.14                                         # gusset fold
        return A(pick(KRAFT, v - 0.04))
    if f == 'front':
        ox = (ctx.w - W_CARBON) // 2
        if (i - ox, j - 4) in TXT_CARBON:
            return A(INK[0] if j - 4 < 4 else INK[1])
        if 11 <= j <= 13:
            if j == 12 and abs(i - ctx.w / 2 + 0.5) < 1.0:
                return A(hx('#f2c84a'))                       # small flame logo in the red band
            return A(RED[2] if j == 12 else RED[1])
        if j == 15 and abs(i - ctx.w / 2 + 0.5) < 5 and i % 2 == 0:
            return A(INK[1])                                  # small print
        if (i, j) in ((3, 1), (4, 2), (19, 15), (20, 15), (21, 16)):
            return A(COAL[3])                                 # charcoal dust smudges
        return A(pick(KRAFT, v))
    return A(pick(KRAFT, v - 0.06))


# ------------------------------------------------------------------ possessed toggles: the grin + the eyes
def grin_center(u):
    """y of the grin's centre line at arc length u from the middle (front plane u = |x| 0..8, sides 8..15)."""
    if u <= 4.0:
        return -23.0
    if u <= 8.0:
        k = (u - 4.0) / 4.0
        return -23.0 - 2.6 * k * k
    return -25.6 - (u - 8.0) * 0.42


def grin_half(u):
    return max(0.95, 1.65 - max(0.0, u - 6.0) * 0.09)


def grin_rgba(L, u, y, col, upper_only=False, lower_only=False):
    """Colour of the grin at arc length u / height y, or None outside it.  col = tooth column index."""
    yc = grin_center(u)
    hh = grin_half(u)
    dy = y - yc
    if upper_only and dy > 0:
        return None
    if lower_only and dy < 0:
        return None
    if abs(dy) > hh + 0.55:
        return None
    if abs(dy) > hh:
        return LIPP[2]                                        # the stretched lip edge
    if abs(dy) > hh - 0.55:
        return LIPP[0] if u > 11 else LIPP[1]                 # lips: thin, black-purple, cracked
    upper = dy < 0
    if (col + (0 if upper else 1)) % 2 == 0:                  # interlocking teeth: dark gaps offset per row
        return GUM[0] if u > 10 else L['mouth'][1]
    c = TEETH[5] if upper else TEETH[4]
    if u > 9.5:
        c = TEETH[3]
    if u > 12.5:
        c = TEETH[2]
    if (col * 7) % 5 == 0:
        c = TEETH[3]
    return c


def smile_mat(ctx, L):
    t = tag(ctx)
    f = ctx.face
    x, y, z = rest_pos(ctx)
    if t == 'smile_side':
        if f != outer_face(ctx):
            return None
        u = 8.0 + (z + 8.0)
        col = int(math.floor(z + 8.0)) + 8
        c = grin_rgba(L, u, y, col)
    elif t == 'smile_jaw':
        if f != 'front':
            return None
        u = abs(x)
        col = int(math.floor(x + 8.0))
        c = grin_rgba(L, u, y, col, lower_only=True)
    else:
        if f != 'front':
            return None
        u = abs(x)
        col = int(math.floor(x + 8.0))
        c = grin_rgba(L, u, y, col, upper_only=u < 6.0)
    return None if c is None else A(c)


def eyes_mat(ctx, L):
    """Opaque possessed eyes (zero-thickness plane): black sclera, white pupils; transparent elsewhere."""
    if ctx.face != 'front':
        return None
    x, y, z = rest_pos(ctx)
    ch, c, r = face_char(x, y)
    if ch in ('W', 'L') and r in (7, 8):
        return A(VOID)
    if ch in ('I', 'i', 'g'):
        return A(PUPIL if ch != 'i' else hx('#dfe6f4'))
    return None


def eyes_glow(img, u0, v0, w, h):
    """'eyes' layer: the white pupils, full bright (the only emissive pixels on Jorge)."""
    px = img.load()
    for j in range(h):
        for i in range(w):
            ch, c, r = face_char(DEMON_EYES_X0 + i + 0.5, DEMON_EYES_Y0 + j + 0.5)
            if ch in ('I', 'g'):
                px[u0 + i, v0 + j] = (255, 255, 255, 255)
            elif ch == 'i':
                px[u0 + i, v0 + j] = (226, 232, 255, 255)


DEMON_EYES_X0, DEMON_EYES_Y0 = -7.0, -30.0

KINDS = {
    'skin': skin_mat, 'hair': hair_mat, 'shirt': shirt_mat, 'apron': apron_mat, 'shorts': shorts_mat,
    'sole': sole_mat, 'steel': steel_mat, 'bag': bag_mat, 'smile': smile_mat, 'eyes': eyes_mat,
}


def make_mat(look):
    L = LOOKS[look]

    def mat(ctx):
        return KINDS[getattr(ctx.cube, 'kind', 'skin')](ctx, L)
    mat.look = look
    return mat


DEFAULT_MAT = make_mat('normal')
VARIANT_MATS = {'normal': DEFAULT_MAT, 'poseido': make_mat('poseido')}
FOCUS = 'head'


# ------------------------------------------------------------------ toggles (Java: ModelPart.visible)
TOGGLE_DEFAULT = {'smile': False, 'smile_jaw': False, 'demon_eyes': False, 'bag': False, 'tongs': True}
VARIANT_TOGGLES = {'normal': {}, 'poseido': {'smile': True, 'smile_jaw': True, 'demon_eyes': True}}
POSE_TOGGLES = {'carry_bag': {'bag': True, 'tongs': False}, 'grill_flip': {'tongs': False}}


def visible_set(variant=None, pose=None):
    vis = dict(TOGGLE_DEFAULT)
    vis.update(VARIANT_TOGGLES.get(variant or 'normal', {}))
    vis.update(POSE_TOGGLES.get(pose, {}))
    return {k for k, v in vis.items() if v}


class JorgeModel(Model):
    """Exports every bone to Java; the preview / gallery JSON hides the toggle bones the current look / pose hides."""
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


# ------------------------------------------------------------------ rest pose (degrees)
ARM_OUT = 9.0           # arms angled out round the belly
ARM_FWD = -3.0
ELBOW = -12.0           # forearms a little forward
TONGS_TILT = 24.0       # tongs tips down
TONGS_OPEN = 7.0        # lower arm of the tongs sprung open
TOES_OUT = 10.0         # duck stance
BROW_DROOP = 8.0        # friendly droop of the outer brow ends
SKIRT_TILT = 9.0        # apron skirt, tucked under the dome, swings back towards the thighs
FIST = -80.0            # right fingers curled round the tongs grip
FINGERS_L = 14.0        # left fingers relaxed
INDEX_L = 6.0


def build(variant=None, pose=None):
    r = Rig()

    def bone(name, pivot, parent=None, rot=(0, 0, 0)):
        return r.bone(name, pivot, parent=parent, rot=rot)

    def box(b, frm, size, kind, name, inflate=0.0, decals=None, sx=1, **attrs):
        c = r.box(b, frm, size, inflate=inflate, decals=decals)
        c.kind = kind
        c.name = name
        c.sx = sx
        c.ax0, c.ay0, c.az0 = frm
        for k, v in attrs.items():
            setattr(c, k, v)
        return c

    # ---------------- body: pivot at the hips
    bone('body', (0, 3, 0))
    box('body', (-10.5, -3, -5.5), (21, 7, 11), 'shorts', 'hips')
    box('body', (-11, -19, -6), (22, 17, 12), 'shirt', 'torso')
    box('body', (-10, -20, -5.5), (20, 1, 11), 'shirt', 'yoke')
    box('body', (-6, -22, -5), (12, 2, 10), 'shirt', 'collar')
    box('body', (-7, -20, -7), (14, 8, 1), 'apron', 'bib')
    box('body', (-10, -20, -6.1), (3, 3, 0), 'shirt', 'collar_tip')
    box('body', (7, -20, -6.1), (3, 3, 0), 'shirt', 'collar_tip')
    box('body', (-4.5, -7, 6.15), (9, 5, 0), 'apron', 'bow')

    # ---------------- belly: a dome of four nested blocks, the apron over the front
    bone('belly', (0, -4, -6), 'body')
    box('belly', (-11, -12, -10), (22, 15, 4), 'shirt', 'belly_a')
    box('belly', (-12, -10, -12), (24, 12, 3), 'shirt', 'belly_b')
    box('belly', (-13, -7, -11), (26, 7, 6), 'shirt', 'belly_c')
    box('belly', (-8.5, -11, -12.5), (17, 1, 3), 'shirt', 'belly_round_1')
    box('belly', (-9.5, -10, -13.5), (19, 1, 3), 'shirt', 'belly_round_2')
    box('belly', (-10, -9, -14.5), (20, 11, 3), 'shirt', 'belly_cap')
    box('belly', (-9.5, 2, -13.5), (19, 1, 3), 'shirt', 'belly_round_3')
    bone('apron_skirt', (0, 3, -11.5), 'belly', rot=(SKIRT_TILT, 0, 0))
    box('apron_skirt', (-10.5, 3, -12), (21, 8, 1), 'apron', 'skirt')

    # ---------------- neck + head
    bone('neck', (0, -20, 0), 'body')
    box('neck', (-5.5, -26, -4), (11, 6, 9), 'skin', 'neck')
    bone('head', (0, -23, 0), 'neck')
    box('head', (-8, -37, -8), (16, 12, 16), 'skin', 'skull')
    box('head', (-8, -37, -8), (16, 11, 16), 'hair', 'hair', inflate=0.5)
    box('head', (-2, -38.5, -8.5), (3, 2, 4), 'hair', 'tuft')
    box('head', (-2, -31, -11), (4, 4, 3), 'skin', 'nose')
    box('head', (-10, -31, -1.5), (2, 5, 3), 'skin', 'ear', sx=-1)
    box('head', (8, -31, -1.5), (2, 5, 3), 'skin', 'ear', sx=1)
    bone('right_brow', (-4.5, -32, -8.5), 'head', rot=(0, 0, -BROW_DROOP))
    box('right_brow', (-7, -33, -9.5), (5, 2, 2), 'hair', 'brow', sx=-1)
    bone('left_brow', (4.5, -32, -8.5), 'head', rot=(0, 0, BROW_DROOP))
    box('left_brow', (2, -33, -9.5), (5, 2, 2), 'hair', 'brow', sx=1)
    bone('moustache', (0, -26, -9), 'head')
    box('moustache', (-6, -27, -10), (12, 3, 2), 'hair', 'moustache')
    box('moustache', (-7.5, -26, -9.6), (2, 4, 2), 'hair', 'moustache_end', sx=-1, inflate=-0.1)
    box('moustache', (5.5, -26, -9.6), (2, 4, 2), 'hair', 'moustache_end', sx=1, inflate=-0.1)
    bone('jaw', (0, -25.5, 1), 'head')
    box('jaw', (-8, -25, -8), (16, 5, 12), 'skin', 'jaw')
    box('jaw', (-5, -20.5, -7.5), (10, 2, 7), 'skin', 'chin2')
    # possessed toggles
    bone('smile', (0, -25.5, -8.1), 'head')
    box('smile', (-8, -29, -8.1), (16, 6, 0), 'smile', 'smile_front')
    box('smile', (-8.1, -31, -8), (0, 8, 7), 'smile', 'smile_side', sx=-1)
    box('smile', (8.1, -31, -8), (0, 8, 7), 'smile', 'smile_side', sx=1)
    bone('smile_jaw', (0, -25.5, 1), 'jaw')
    box('smile_jaw', (-8, -23, -8.1), (16, 3, 0), 'smile', 'smile_jaw')
    bone('demon_eyes', (0, -29, -8.15), 'head')
    box('demon_eyes', (DEMON_EYES_X0, DEMON_EYES_Y0, -8.15), (14, 2, 0), 'eyes', 'demon_eyes',
        decals={'eyes:front': eyes_glow})

    # ---------------- arms
    for side, sx in (('right', -1), ('left', 1)):
        arm, fa, hand = f'{side}_arm', f'{side}_forearm', f'{side}_hand'
        ax = 15.0 * sx
        bone(arm, (11.5 * sx, -18, 0), 'body', rot=(ARM_FWD, 0, -ARM_OUT * sx))
        box(arm, (ax - 4, -20.5, -4), (8, 8, 8), 'shirt', 'sleeve', sx=sx)
        box(arm, (ax - 3, -13, -3), (6, 6, 6), 'skin', 'upper_arm', sx=sx)
        bone(fa, (ax, -7.5, 0), arm, rot=(ELBOW, 0, 0))
        box(fa, (ax - 3, -8, -3), (6, 9, 6), 'skin', 'forearm', sx=sx, watch=(sx > 0))
        bone(hand, (ax, 1, 0), fa)
        box(hand, (ax - 1.5, 0.5, -3), (3, 5, 6), 'skin', 'palm', sx=sx)
        tx = ax - 0.5 if sx < 0 else ax - 1.5                 # thumb on the front edge, palm side
        box(hand, (tx, 1.0, -4.4), (2, 4, 2), 'skin', 'thumb', sx=sx, inflate=-0.15)
        if sx < 0:
            # four fingers in one bone, curled round the tongs grip at rest
            bone('right_fingers', (ax, 5.5, 0), hand, rot=(0, 0, FIST))
            for fz, fl in ((-3.25, 4), (-1.75, 5), (-0.25, 4), (1.25, 3)):
                box('right_fingers', (ax - 1, 5.5, fz), (2, fl, 2), 'skin', 'finger', sx=sx, inflate=-0.25)
            bone('tongs', (ax + 0.5, 6.5, 0), hand, rot=(TONGS_TILT, 0, 0))
            box('tongs', (ax - 0.5, 5.5, -4), (2, 2, 9), 'steel', 'grip')
            box('tongs', (ax - 0.5, 5.5, -13), (2, 1, 9), 'steel', 'bar')
            box('tongs', (ax - 1, 5.5, -16), (3, 1, 3), 'steel', 'tip')
            box('tongs', (ax, 5, 5), (1, 3, 1), 'steel', 'hinge')
            bone('tongs_lower', (ax + 0.5, 7, 5), 'tongs', rot=(TONGS_OPEN, 0, 0))
            box('tongs_lower', (ax - 0.5, 6.5, -13), (2, 1, 9), 'steel', 'bar')
            box('tongs_lower', (ax - 1, 6.5, -16), (3, 1, 3), 'steel', 'tip_lo')
        else:
            # index on its own bone (pointing), middle / ring / pinky curl together
            bone('left_index', (ax, 5.5, -2.25), hand, rot=(0, 0, INDEX_L))
            box('left_index', (ax - 1, 5.5, -3.25), (2, 4, 2), 'skin', 'finger', sx=sx, inflate=-0.25)
            bone('left_fingers', (ax, 5.5, 0.75), hand, rot=(0, 0, FINGERS_L))
            for fz, fl in ((-1.75, 5), (-0.25, 4), (1.25, 3)):
                box('left_fingers', (ax - 1, 5.5, fz), (2, fl, 2), 'skin', 'finger', sx=sx, inflate=-0.25)

    # ---------------- legs
    for side, sx in (('right', -1), ('left', 1)):
        leg, shin = f'{side}_leg', f'{side}_shin'
        lxc = 5.5 * sx
        bone(leg, (lxc, 4, 0), 'body', rot=(0, -TOES_OUT * sx, 0))
        box(leg, (lxc - 5, 3, -5), (10, 9, 10), 'shorts', 'shorts', sx=sx)
        box(leg, (lxc - 5, 10, -5), (10, 2, 10), 'shorts', 'cuff', sx=sx, inflate=0.3)
        bone(shin, (lxc, 12, 0), leg)
        box(shin, (lxc - 3, 12, -3), (6, 9, 6), 'skin', 'shin', sx=sx)
        box(shin, (lxc - 3.5, 21, -7), (7, 2, 10), 'skin', 'foot', sx=sx)
        box(shin, (lxc - 4, 23, -8), (8, 1, 12), 'sole', 'sole', sx=sx)

    # ---------------- the charcoal bag (toggle), hugged in front of the belly
    bone('bag', (0, -8, -20), 'body')
    box('bag', (-11, -17, -25), (22, 17, 9), 'bag', 'sack')
    box('bag', (-11.5, -19, -25.5), (23, 2, 10), 'bag', 'rim')
    box('bag', (-10, -20, -24), (20, 2, 7), 'bag', 'coal')

    m = JorgeModel('jorge', 256, 256, r.roots)
    m.scale = 0.5
    if pose is None and os.path.basename(sys.argv[0]) == 'preview.py':
        pose = _argv('--pose')
    m.visible = visible_set(variant, pose)
    return m


# ------------------------------------------------------------------ FK (pose checks: python3 ent_jorge.py --fk)
def fk(roots, pose):
    out = {}

    def rec(b, M):
        p = pose.get(b.name, (0, 0, 0, 0, 0, 0))
        T = np.eye(4)
        T[:3, 3] = [b.pivot[0] + p[3], b.pivot[1] + p[4], b.pivot[2] + p[5]]
        R = np.eye(4)
        R[:3, :3] = rot_matrix(math.radians(b.rot[0]) + p[0], math.radians(b.rot[1]) + p[1],
                               math.radians(b.rot[2]) + p[2])
        W = M @ T @ R
        out[b.name] = W
        for c in b.children:
            rec(c, W)
    for rb in roots:
        rec(rb, np.eye(4))
    return out


POSES = {}

ANIM_NOTES = """(written once the poses are final)"""
