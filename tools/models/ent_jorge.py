"""Jorge Morales (46) -- dad, 'rey del asado', host #2 of the demon (DEAD LINE, case 2 'Casa Morales').

Authored at 2x texel density (model.scale = 0.5).  +Y down, ground y = 24, faces -Z, right_* on -X.  Centred on
x = 0, z = 0 (feet and trunk; only the belly, the apron, the tongs and the props reach forward).  Height 1.9 blocks:
skull top y = -37 -> soles y = 24 (61 texels; the combed tuft pokes to -38.5).  Texture 256 x 144 (a 1-texel
bleed gutter round every UV block, see JorgeModel).  79 cubes / 30
bones (budget 110 / 32).

Design
------
Silhouette: a PEAR on flip-flops.  Normal shoulders (22 + puffy short sleeves), then a beer belly that is the widest
and deepest thing on him: a BALL of nine stacked slabs (BELLY: a stepped ellipse 26 wide at the navel, sticking out
11 texels in front of the chest, with half-texel steps across the flat front so the print never shears), so it reads
round from the front AND really sticks out in profile.  The black apron rides over the ball (REY / DEL printed in
world space, each word on two slabs only), then leaves the belly's underside as a two-panel skirt: a 2-thick upper
panel draping back 35 deg toward the thighs and a plumb lower panel (ASADO) whose hem hangs just in front of the
bermudas.  Khaki bermudas: two 9-wide legs with a real gap and an inseam, two shins, navy ojotas, toes out.  A big
head (16 x 17 face) on a fat neck: a pear-shaped head (the cheeks and the hinged jaw are 18 wide, the forehead 16),
a small double chin resting on the bib.  The grill tongs hang tips-down along his right thigh, open in a clear V.

Hierarchy rule: 'body' is the root at the hips and owns ONLY the hips and the legs; everything above the belt hangs
from 'chest' (pivot at the belt).  Leans, bows and the walk roll go on 'chest', so the feet stay planted.

Face (front 16 x 17, hand placed in FACE, painted through the look so the possessed texture recolours it): tall
bald forehead with two furrows and a sweaty shine (receding hairline: bald temples, one combed tuft), two bushy brows
(the right one raised and arched, the left one lowered a touch at the inner end: the cocky "es la humedad, flaco"
look), 4 x 3 eyes under heavy smug half-lids (both irises centred, the glint on the same side), a big bulbous red
nose (own cube), ruddy cheeks, a thick walrus MOUSTACHE (own bone: a combed 12-wide block parted under the nose, a
strand fringe hanging over the lip at uneven lengths, two drooping ends), under it a smiling U-shaped lower lip with
dark corners peeking out from under the moustache ends, a shadow under the lip, a lit chin ball, and a little double
chin cube.  Hair: short dark clumps with a sheen band, salt-and-pepper over the ears, a ragged clumped hem at the
back that fades into the nape in 1-texel strands, a small bald spot on the crown.  Body hair on forearms / shins /
backs of the hands: fine 3-texel combed strokes (cool dark brown at ~0.3, all leaning the same way).

Wardrobe: short-sleeved shirt with vertical light-blue / white stripes (generic, no crest) and sweat stains, a gold
chain in the open collar; a black canvas apron: a cartoon cow on the bib, "REY" / "DEL" on the belly, "ASADO" on
the lower skirt panel (3 x 5 pixel letters, off-white), grease stains, stitched hem, neck strap and waist ties knotted
in a bow on his back; khaki bermudas with a belt, cargo pockets and an inseam; navy rubber ojotas with white Y straps;
stainless grill tongs (two 2 x 2 arms with a polished top edge, 4-wide scalloped heads, black rubber grips, a riveted
hinge: they clack).  Prop toggle: a 10 kg kraft paper sack of charcoal ('bag': CARBÓN in black, a red band with a
flame logo, the open top rolled over with lumps showing) that rests on the belly shelf in carry_bag.

Possessed look ('poseido', VARIANT_MATS index 1): sick corpse-grey skin (cold blue-violet shadows from the blue fire,
green only as a tint in the mid tones), bruised eye sockets, a few branching black veins off the centre line, BLACK
sclera with WHITE pupils, charred fingertips and soot creeping up the wrists (he flips chorizos on the grill with his
bare hands), sooty thumb prints on the shirt and the print, scorch marks and a singed apron hem, singed moustache
tips, the tongs blued by the blue fire.  Toggle geometry shown only in this look: 'demon_eyes' (plane over the eyes
carrying the emissive white pupils: the only 'eyes' layer pixels), 'smile' (the ear-to-ear grin, upper half: gums,
upper teeth, the corners shooting up the cheeks beside the moustache ends and two side planes running back along the
cheeks) and 'smile_jaw' (lower teeth and lower lip, riding the jaw: the grin splits open when the jaw drops).  Teeth
are hand placed per column: 2-wide teeth with dark gaps, two upper teeth a texel longer, one missing, one dead grey,
the rows interlocking, yellowing toward the corners where the gums darken.  The possessed rest also lowers the brows
into an angry V and lifts the moustache (VARIANT_POSES).  Steam at the neck is particles (Java).
"""
import math
import os
import sys

import numpy as np

from mcmodel import Model, hash3, face_light, pick, rot_matrix
from rig import Rig
from paint import hx, mix
import ent_copia_look as copia


# ------------------------------------------------------------------ palettes (hand-picked, hue shifted)
def H(*cs):
    return [hx(c) for c in cs]


SKIN_N = H('#2a1410', '#45201a', '#642f24', '#844334', '#a35a44', '#bc7255', '#cf8a69', '#dea27f', '#eabb98',
           '#f5d3b5')
# possessed: corpse grey, cold blue-violet shadows (the blue fire), only a green tint in the mid tones
SKIN_P = H('#0f0d15', '#1b1923', '#282632', '#36353f', '#45454c', '#545852', '#656a62', '#777c73', '#8b8f86',
           '#a2a59c')
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
GUM = H('#1f070c', '#3a0f19', '#5a1a28', '#7a2a38')
LIPP = H('#0c070c', '#1a0f18', '#2a1824', '#3a2432')
MOUTH_N = H('#1a0807', '#2e100d', '#4a1c16', '#6a2a20')
EMBER = H('#3a0a04', '#7a1e08', '#c8460e', '#ff8a24')
SOOT = hx('#141313')
VOID = hx('#050407')
PUPIL = hx('#f4f7ff')
PUPIL2 = hx('#d8e0f2')


# ------------------------------------------------------------------ looks
LOOKS = {
    'normal': {
        'skin': SKIN_N, 'poss': False,
        'spec': hx('#fbe6d2'), 'crease': SKIN_N[4], 'deep': SKIN_N[3],
        'lid': hx('#3e1d16'), 'lid2': hx('#c47860'), 'sclera': hx('#f4ede2'), 'sclera_sh': hx('#dccab8'),
        'iris': hx('#7a4c22'), 'iris_sh': hx('#4f2f16'), 'pupil': hx('#2e190b'), 'glint': hx('#ffffff'),
        'bag': SKIN_N[5], 'ruddy': hx('#d4705f'), 'ruddy2': hx('#bd5a4c'), 'ruddy3': hx('#e48b74'),
        'lip': hx('#b34f43'), 'lip2': hx('#7f3029'), 'liphi': hx('#cf6f5c'), 'corner': hx('#3a130f'),
        'mouth': MOUTH_N, 'chin': SKIN_N[8], 'chin2': SKIN_N[7],
        'stub': hx('#5f5058'), 'nail': hx('#f0cdb8'), 'nail2': hx('#c98f78'),
        'chest_hair': HAIR[2], 'socket': None, 'vein': None, 'tip': None,
    },
    'poseido': {
        'skin': SKIN_P, 'poss': True,
        'spec': hx('#b9bcb2'), 'crease': SKIN_P[4], 'deep': SKIN_P[1],
        'lid': hx('#060508'), 'lid2': hx('#1d1a24'), 'sclera': VOID, 'sclera_sh': VOID,
        'iris': PUPIL, 'iris_sh': VOID, 'pupil': PUPIL2, 'glint': PUPIL,
        'bag': hx('#2a2535'), 'ruddy': hx('#3b3646'), 'ruddy2': hx('#2f2b39'), 'ruddy3': hx('#4a4655'),
        'lip': hx('#2b1d2b'), 'lip2': hx('#160e16'), 'liphi': hx('#3d2b3a'), 'corner': hx('#030204'),
        'mouth': H('#030303', '#08060a', '#120c14', '#1e1420'), 'chin': SKIN_P[7], 'chin2': SKIN_P[6],
        'stub': hx('#1b1d22'), 'nail': hx('#2f3a30'), 'nail2': hx('#1c241e'),
        'chest_hair': HAIR[1], 'socket': (hx('#18141e'), hx('#262130')), 'vein': hx('#231d33'),
        'tip': True,
    },
}
# B3 'copia': the normal look drained grey (skin, lips, cheeks, nails); the copy's eyes and teeth come from COPIA_FACE
LOOKS['copia'] = dict(LOOKS['normal'], copia=True, skin=[copia.grey(c) for c in SKIN_N],
                      **{k: copia.grey(LOOKS['normal'][k]) for k in ('spec', 'crease', 'deep', 'bag', 'ruddy', 'ruddy2',
                                                                      'ruddy3', 'lip', 'lip2', 'liphi', 'corner', 'chin',
                                                                      'chin2', 'nail', 'nail2', 'lid2')})


def A(c, a=255):
    return (c[0], c[1], c[2], int(a))


# ------------------------------------------------------------------ geometry helpers
def local(ctx):
    """Texel centre in cube-local texel units (independent of bone rotation and face)."""
    w, h, d = ctx.cube.size
    s, t, f = round(ctx.s, 9), round(ctx.t, 9), ctx.face
    w, h, d = float(w), float(h), float(d)
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
    return round(c.ax0 + lx, 6), round(c.ay0 + ly, 6), round(c.az0 + lz, 6)


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


def hair_stroke(ctx, seed, p=0.5, lean=1):
    """Body hair as fine combed strokes, never blobs: on a staggered 2-wide x 4-tall grid, at most one 1-texel-wide
    stroke per cell, 3 texels long and steep (combed down the limb), the tip stepping sideways the same way on every
    face (lean).  Returns 0 (skin) or 1 / 2 / 3 (root / body / tip)."""
    i, j = ctx.i, ctx.j
    for dj in (0, 1, 2):                                      # a stroke may start up to 2 rows above this texel
        jj = j - dj
        ci = i // 2
        cj = (jj + (2 if ci % 2 else 0)) // 4                 # staggered rows: no grid look
        if h2(ci * 5 + 1, cj * 7 + 3, seed) > p:
            continue
        ri = ci * 2
        rj = cj * 4 - (2 if ci % 2 else 0) + int(h2(ci, cj, seed + 2) * 2)
        pts = ((ri, rj, 1), (ri, rj + 1, 2), (ri + lean, rj + 2, 3))
        for (pi, pj, k) in pts:
            if (i, j) == (pi, pj):
                return k
    return 0


def body_hair(L, base, hs, strength=1.0):
    """Hair stroke colour: the skin mixed toward a cool dark brown (HAIR[2]) at ~0.3, fading to the tip (reads as
    fine hair, not scratches)."""
    return mix(base, HAIR[2], {1: 0.26, 2: 0.2, 3: 0.11}.get(hs, 0.0) * strength)


# ------------------------------------------------------------------ the face (16 x 17, painted through the look)
# col c <-> x in [-8 + c, -7 + c]; row r <-> y in [-37 + r, -36 + r].  Skull rows 0..12 (y -37..-24), jaw rows
# 13..16 (y -24..-20; the jaw is 18 wide: its outer columns -1 / 16 are the jowls).  Covered by geometry: brows
# (right cols 1-5 rows 2-3 raised, left cols 10-14 rows 3-4), nose (cols 6-9, rows 6-9), moustache block (cols 2-13,
# rows 10-12), its fringe (cols 1-14, rows 13-14, ragged), the drooping ends (cols 1-2 / 13-14, rows 11-14).  What
# shows under them is painted sensibly anyway (the brows, the moustache and the jaw move).
#   0-9 skin ramp   w specular   k soft crease   K deep crease   L lid / lash line   V sclera in the lid's shadow
#   T iris in the lid's shadow   W sclera   g glint   I iris   i iris (dark side)   b eye bag   l lower lid
#   r R q ruddy (mid / dark / light)   M mouth corner   P lip (shade)   p lip (lit)   o lip highlight
#   c C chin (mid / lit ball)   s stubble   h hair (the lock's roots)
GX0, GY0 = -8.0, -37.0
FACE = [
    # 0123456789012345
    "556677hhh7776655",   # r0  y-37  top of the forehead (bald: the hair recedes), the central lock's roots
    "5667kk7w87kk7665",   # r1  y-36  first furrow (two short bits) + sweaty shine
    "5678888ww8888765",   # r2  y-35
    "566kkk7887kkk665",   # r3  y-34  second furrow
    "5566777887776655",   # r4  y-33
    "4kLLLL7887LLLLk4",   # r5  y-32  heavy upper lids
    "4kLTTV6776VTTLk4",   # r6  y-31  smug half-lid: its shadow over the top of the eye, the outer corner drooping
    "55WgiW6776WgiW55",   # r7  y-30  irises centred (pupil in the middle row), glint on the same side in both eyes
    "r5WIIW6776WIIW5r",   # r8  y-29
    "rqbllb6776bllbqr",   # r9  y-28  lower lids + bags (nose cube over cols 6-9), ruddy cheek edges
    "Rrq5555665555qrR",   # r10 y-27  (moustache block over cols 2-13 from here to r12)
    "Rrs5555555555srR",   # r11 y-26
    "Rss5555555555ssR",   # r12 y-25
    "4ssMpKKKKKKpMss4",   # r13 y-24  jaw top: dark corners + the lip's ends curling up beside the fringe clumps
    "4sssPpooooPPsss4",   # r14 y-23  the lit lower lip (a crescent: the smile)
    "4ssssKPPPPKssss4",   # r15 y-22  the lip's underside, the crescent's belly
    "3ssssskKKksssss3",   # r16 y-21  shadow under the lip (the double chin cube below is the lit chin)
]
assert all(len(r) == 16 for r in FACE), [len(r) for r in FACE]
# possessed: bruised sockets round the eyes (S = socket, s = soft socket) and hand-placed branching veins (v), kept
# off the face's edges and off the centre line (no mask frame)
SOCKET = [
    "................",
    "................",
    "................",
    "................",
    ".sSSSSs..sSSSSs.",
    "sS............Ss",
    ".S............S.",
    ".S............S.",
    ".s............s.",
    "..SSSS....SSSS..",
    "..ssss....ssss..",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
]
VEINS = [
    "..V.............",   # one branching vein climbing the right forehead (viewer's left), a short fork on the left
    "..Vv.........v..",   # temple, a thin one down the left jowl: connected 1-texel lines, V = core, v = fainter
    "...V.v......V...",
    "...VV........V..",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    ".............v..",
    "............V...",
    "............V...",
    "...........v....",
]
assert all(len(r) == 16 for r in SOCKET + VEINS)


# ------------------------------------------------------------------ B3: the copy (look 'copia')
COPIA_FACE = copia.check([
    "556677hhh7776655",   # r0
    "5667kk7w87kk7665",   # r1
    "5678888ww8888765",   # r2
    "566kkk7887kkk665",   # r3
    "5566777887776655",   # r4
    "4LLLL678876LLLL4",   # r5  no heavy lids any more: a thin lash line, the eyes one texel further out
    "4EEEE766667EEEE4",   # r6  white above...
    "5EEOE766667EOEE5",   # r7  ...a pinpoint turned in at you...
    "reEEE766667EEEer",   # r8  ...and white below: wide open, never blinking
    "rq555566776555qr",   # r9
    "Rrq5555665555qrR",   # r10 (moustache over cols 2-13 from here to r12)
    "Rrs5555555555srR",   # r11
    "Nss5555555555ssN",   # r12 the corners pulled up past the moustache
    "4NZGGGGGGGGGGZN4",   # r13 the lips pulled back off the gums, jowl to jowl
    "4" + copia.teeth_row(14) + "4",   # r14 upper teeth
    "4Z" + copia.teeth_row(12, 'Y') + "Z4",   # r15 lower teeth
    "3sGZZZZZZZZZZGs3",   # r16
], 16)
_FACE_ACTIVE = [FACE]


def face_char(x, y):
    c = int(math.floor(x - GX0))
    r = int(math.floor(y - GY0))
    F = _FACE_ACTIVE[0]
    if 0 <= r < len(F) and 0 <= c < 16:
        return F[r][c], c, r
    if 13 <= r < len(FACE) and c in (-1, 16):
        return 'J', c, r                                     # the jowls: the jaw is 2 texels wider than the skull
    return None, c, r


def face_rgba(ch, L, c, r):
    S = L['skin']
    if L.get('copia'):
        cc = copia.char_rgba(ch)
        if cc is not None:
            return cc
    if ch == 'J':
        # jowl front: the outermost column turns away (darker), stubbled, darkest at the jaw line
        base = S[4] if r < 16 else S[3]
        return stubble(L, base, c, r, 0.3) if r > 13 else base
    if L['poss']:
        vc = VEINS[r][c]
        if vc in 'Vv' and ch not in 'LWVTIigblMPpo':
            return L['vein'] if vc == 'V' else mix(L['vein'], S[4], 0.45)
        sk = SOCKET[r][c]
        if sk == 'S' and ch not in 'LWVTIig':
            return L['socket'][0]
        if sk == 's' and ch not in 'LWVTIig':
            return L['socket'][1]
    if ch.isdigit():
        return S[int(ch)]
    tbl = {'h': HAIR[3], 'w': L['spec'], 'k': L['crease'], 'K': L['deep'], 'L': L['lid'], 'l': L['lid2'],
           'W': L['sclera'], 'V': L['sclera_sh'], 'T': L['iris_sh'], 'I': L['iris'], 'i': L['pupil'],
           'g': L['glint'], 'b': L['bag'], 'r': L['ruddy'], 'R': L['ruddy2'], 'q': L['ruddy3'],
           'M': L['corner'], 'P': L['lip2'], 'p': L['lip'], 'o': L['liphi'], 'c': L['chin2'], 'C': L['chin']}
    if ch in tbl:
        return tbl[ch]
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

# the back of the head.  HEM_*: last hair row (0..10 of the 11-row shell, logical y = -37 + row) per column; clumps of
# 2-3 columns end in a point (the middle column one row longer), neighbouring clumps stop at different heights, so the
# hem is 2-3 rows of uneven clumps and never a flat ledge.  Back: 16 columns, c = floor(8 - x).  Sides: 16 columns
# along z, c = floor(z + 8), only behind the ear (z > 1.6) and on the sideburn.
HEM_BACK = [8, 9, 8, 9, 10, 9, 8, 9, 10, 10, 9, 8, 9, 10, 9, 8]
CLUMP_BACK = [0, 0, 0, 1, 1, 1, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5]     # clump id per column (lit edge = first column)
HEM_SIDE = [10, 10, 10, 10, 10, 10, 9, 9, 9, 10, 9, 8, 9, 10, 9, 8]
# the barber's fade under the hem: how many 1-texel strands hang below each column (staggered 0..2)
NAPE_FADE = [1, 2, 0, 1, 2, 1, 0, 2, 1, 0, 2, 1, 1, 2, 0, 1]


def back_col(x):
    return max(0, min(15, int(math.floor(8.0 - x))))


def side_col(z):
    return max(0, min(15, int(math.floor(z + 8.0))))


def hair_end_y(face, x, z):
    """World y of the bottom of the hair at this column (back or sides)."""
    if face == 'back':
        return -37.0 + HEM_BACK[back_col(x)] + 1.0
    return -37.0 + HEM_SIDE[side_col(z)] + 1.0


def nape_paint(ctx, L, face, x, y, z):
    """Skull back / side under the shell: roots above the hem, a fade of staggered 1-texel strands, then nape skin with
    stubble that thins out downward (no hard lines: the back of the head must not read as a face)."""
    S = L['skin']
    ye = hair_end_y(face, x, z)
    c = back_col(x) if face == 'back' else side_col(z)
    if y < ye:
        return A(HAIR[1] if (ctx.i + ctx.j) % 3 else HAIR[2])
    k = int(math.floor(y - ye))                               # rows below the hem
    n = NAPE_FADE[c]
    if k < n:
        strand = (c + k) % 2 == 0
        if strand:
            return A(mix(HAIR[3], S[4], 0.25 * k))
    v = 0.52 if y < -25.0 else 0.56                          # lit roll above the neck
    amt = 0.42 if k < 2 else 0.3 if k < 3 else 0.2
    return A(stubble(L, skin_base(L, v), ctx.i, ctx.j, amt))


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
            # roof of the mouth, seen when the jaw drops: upper teeth along the front edge, dark palate behind;
            # behind the neck the crease under the skull's overhang
            if z < -7.0:
                if abs(x) < 6.0:
                    return A(TEETH[4] if int(x + 8) % 2 == 0 else TEETH[3])
                return A(L['mouth'][2])
            if z < 3.0:
                return A(L['mouth'][0] if abs(x) < 6.5 else L['mouth'][1])
            return A(S[2])
        if f == 'top':
            if abs(x - 0.5) < 1.0 and abs(z - 2.5) < 1.0:
                return A(L['spec'])                          # shine on the bald spot
            if abs(x + 2) < 1.0 and abs(z + 5.5) < 1.0:
                return A(L['spec'])                          # shine on the bald forehead
            return A(skin_base(L, 0.74 + (0.06 if (abs(x) < 5 and z < -2) else 0.0)))
        if f == 'back':
            return nape_paint(ctx, L, 'back', x, y, z)
        # sides: temple, cheek, ear area; under the hair shell behind the ear and on the sideburn: roots and fade
        if z > 1.6:
            return nape_paint(ctx, L, 'side', x, y, z)
        if -2.8 < z < -0.2 and y < -27.4:
            return A(HAIR[2])
        v = 0.56 + (0.06 if z < -4.0 else 0.0)
        if poss and abs((z + 3.0) - (y + 31.0) * 0.8) < 0.5 and -35 < y < -29 and -7 < z < -2:
            return A(L['vein'])                              # a vein crawling from the eye to the temple
        if y > -27.0:
            return A(stubble(L, skin_base(L, v - 0.06), ctx.i, ctx.j))
        return A(skin_base(L, v))

    if t == 'cheek':
        # the fat cheek / jowl bevel beside the face (1 wide): ruddy at the front, stubbled lower down
        if f == 'top':
            return A(S[6])
        if f == 'front':
            r = int(math.floor(y - GY0))
            return A({9: L['ruddy2'], 10: L['ruddy2'], 11: mix(L['ruddy2'], S[3], 0.4)}.get(r, stubble(L, S[3], 0, r)))
        if f == outer_face(ctx):
            fr = (lz if f == 'east' else d - lz)            # 0 at the front edge
            if fr < 2.0 and y < -25.0:
                return A(L['ruddy'] if fr < 1.0 else mix(L['ruddy'], S[5], 0.5))
            v = 0.52 if y < -25.0 else 0.46
            return A(stubble(L, skin_base(L, v), ctx.i, ctx.j, 0.3) if y > -26.0 else skin_base(L, v))
        return A(S[4])

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
            # under the chin: the double chin's roll, a crease where it meets the neck
            if z < -6.0:
                return A(S[5])
            return A(stubble(L, S[3] if z > -2.0 else S[4], ctx.i, ctx.j, 0.25))
        if f == 'back':
            # the jowls' backs beside the fat neck: nape skin, stubbled, darker toward the bottom
            return A(stubble(L, S[5] if ly < 2.0 else S[4], ctx.i, ctx.j, 0.3))
        # sides: the jaw line, stubbled, the bottom row in shade, lighter toward the front (the cheek's roundness)
        fr = (lz if f == 'east' else d - lz)
        v = 0.54 - (ly / h) * 0.1 + (0.04 if fr < 3.0 else 0.0)
        if ly > h - 1.0:
            v -= 0.08
        return A(stubble(L, skin_base(L, v), ctx.i, ctx.j))

    if t == 'chin2':
        if f in ('back', 'top'):
            return None
        if f == 'bottom':
            return A(S[2])
        if f == 'front':
            return A(stubble(L, S[6] if abs(x) < 3.5 else S[5], ctx.i, ctx.j, 0.22))
        return A(stubble(L, S[4], ctx.i, ctx.j, 0.28))

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
            # the fat nape between the skull's overhang and the collar: one soft roll, no hard lines
            if poss and abs((x - 2.5) - (y + 23.0) * 1.0) < 0.5 and y > -24.0:
                return A(L['vein'])                          # one diagonal vein, off centre
            v = 0.5 if -23.0 < y < -22.0 else 0.45
            return A(stubble(L, skin_base(L, v) if abs(x) < 6.0 else S[4], ctx.i, ctx.j, 0.2))
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
        if side and f != inner_face(ctx) and ly < h - 1.5:
            p = 0.66 if f == outer_face(ctx) else 0.36        # denser on the outer forearm
            hs = hair_stroke(ctx, 31 + (side_of(ctx) > 0), p, lean=1)
            if hs:
                return A(body_hair(L, skin_base(L, v), hs))
        if poss and side and f != inner_face(ctx) and ly > h - 3.0 and (ctx.i + int(ly)) % 3 != 0:
            return A(mix(skin_base(L, v), SOOT, 0.25 + 0.12 * (ly - (h - 3.0))))     # soot creeping up the wrists
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
            if hs and ly < h - 1.0:
                return A(body_hair(L, skin_base(L, v), hs, 0.7))
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
        if f != inner_face(ctx) and 1.5 < ly < h - 1.5:
            # hairy calves and sides, fading out on the shin's front (the bone is bare)
            p = 0.18 if f == 'front' else 0.48
            hs = hair_stroke(ctx, 51 + (side_of(ctx) > 0), p, lean=1)
            if hs:
                return A(body_hair(L, skin_base(L, v), hs, 0.6 if f == 'front' else 0.9))
        return A(skin_base(L, v))

    if t in ('foot', 'toes'):
        return foot_paint(ctx, L, t)

    return A(skin_base(L, 0.6 + face_light(ctx) * 0.9))


def foot_paint(ctx, L, t):
    """Bare feet in ojotas.  'foot' = instep (z -4..3, 2 tall) with the white Y strap running from the toe post
    between the big toe and the second toe back to both sides of the sole; 'toes' = the lower toe row in front
    (z -7..-4, 1 tall): a fat big toe on the inner side, four small toes, pale nails on the front row."""
    S = L['skin']
    f = ctx.face
    sx = side_of(ctx)
    x, y, z = rest_pos(ctx)
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    cx = ctx.cube.ax0 + w / 2.0                               # foot centre line
    inner = (x - cx) * (-sx)                                  # +3.5 = inner (big toe) edge, -3.5 = outer edge
    post_x = cx - sx * 1.5                                    # the toe post, between the big toe and the second toe
    if t == 'toes':
        big = inner > 1.5
        col = int(math.floor(3.5 - inner)) if not big else -1    # small toes: 0..3 from the post outward
        if f == 'top':
            if z < -6.0:                                      # the front row: nails
                if L['poss']:
                    return A(L['nail2'])
                return A(L['nail'] if big or col % 2 == 0 else L['nail2'])
            if abs(x - post_x) < 0.5 and z > -5.0:
                return A(STRAP[3])                            # the toe post
            if big:
                return A(S[7] if z < -5.0 else S[6])
            return A(S[6] if col % 2 == 0 else S[5])          # alternating toes read as separate
        if f == 'front':
            if big:
                return A(S[7])
            return A(S[6] if col % 2 == 0 else S[4])
        if f in ('west', 'east'):
            return A(S[5])
        return A(S[4])
    # instep
    if f == 'top':
        tt = (z + 4.0) / 4.5                                  # 0 at the toe post .. 1 where the strap meets the sole
        if 0.0 <= tt <= 1.0:
            e0 = post_x + (cx + sx * 3.5 - post_x) * tt       # strap toward the outer edge
            e1 = post_x + (cx - sx * 3.5 - post_x) * tt       # strap toward the inner edge
            if abs(x - e0) < 0.6 or abs(x - e1) < 0.6:
                return A(STRAP[3] if tt < 0.3 else STRAP[2])
        v = 0.66 - max(0.0, z) * 0.02
        if L['poss']:
            v -= 0.04
        return A(skin_base(L, v))
    if f in ('west', 'east'):
        if abs(z - 0.5) < 0.6:
            return A(STRAP[2])                                # the strap ends anchored in the sole
        if z > 1.5 and ly > 1.0:
            return A(S[4])                                    # heel shadow
        return A(skin_base(L, 0.52 + (0.04 if f == 'west' else 0)))
    if f == 'front':
        return A(S[5])                                        # behind the toes: the ball of the foot
    if f == 'back':
        return A(S[4] if ly < 1.0 else S[3])                  # heel
    return A(S[4])


def hair_clumps(u, y, seed):
    """Short combed-back hair seen from the side / back: 3-texel clumps (lit edge, body, shadowed edge), a sheen band
    where the skull turns to the light, darker toward the nape."""
    cl = int(math.floor(u / 3.0))
    p = int(math.floor(u)) - cl * 3
    v = 0.4 + (0.1 if p == 0 else -0.08 if p == 2 else 0.0)
    if -35.6 < y < -33.4:
        v += 0.1                                              # sheen
    if y > -31.0:
        v -= (y + 31.0) * 0.035
    return pick(HAIR, v)


def hem_cut(j, col, hem, n):
    """Ragged hem of the hair shell: -> None (cut), 'tip' (the clump's last texel) or 'hair'."""
    last = hem[max(0, min(n - 1, col))]
    if j > last:
        return None
    return 'tip' if j == last else 'hair'


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
            # the bald spot on the crown (the skull's shiny top shows through), a ragged rim of thin hair
            bs = ((x - 0.5) / 2.3) ** 2 + ((z - 2.5) / 2.0) ** 2
            if bs < 1.0:
                return None
            if bs < 1.6 and h2(i, j, 29) > 0.55:
                return None
            u = x * 0.9 + z * 0.15
            v = 0.42 + (0.12 if int(u * 1.3) % 3 == 0 else 0.0) - (z + 8) * 0.008
            if bs < 2.2:
                v -= 0.08                                     # thinning round the spot
            if ax > 6.5:
                return A(mix(pick(HAIR, v), GREY[2], 0.35))
            return A(pick(HAIR, v))
        if f in ('west', 'east'):
            if z < -2.6:
                return None                                   # bald temple
            if z < -0.4:                                      # sideburn, greying, ends in a point
                if y > -27.6 - (0.0 if z > -1.5 else 1.0):
                    return None
                g = h2(i, j, 22)
                return A(GREY[1] if g > 0.6 else GREY[0] if g > 0.35 else HAIR[3])
            if -1.6 < z < 1.6 and y > -31.4:
                return None                                   # the ear comes through here
            ye = hair_end_y('side', x, z)
            if y > ye:
                return None
            c = hair_clumps(z * (1 if f == 'east' else -1), y, 23)
            if y > -32 and z < 3.5:
                c = mix(c, GREY[2], 0.3 if (i + j) % 3 else 0.5)    # salt and pepper over the ear
            elif h2(i, j, 24) > 0.9:
                c = GREY[1]
            if y > ye - 1.0:
                c = HAIR[2]                                   # the clump's tip
            return A(c)
        if f == 'back':
            ye = hair_end_y('back', x, z)
            if y > ye:
                return None
            col = back_col(x)
            cl = CLUMP_BACK[col]
            first = col == 0 or CLUMP_BACK[col - 1] != cl
            last = col == 15 or CLUMP_BACK[col + 1] != cl
            v = 0.42 - max(0.0, y + 33.0) * 0.022             # darker toward the nape
            if y < -35.0:
                v += 0.08                                     # the crown turning to the light
            elif y < -32.5 and (col + int(y)) % 2 == 0:
                v += 0.12                                     # sheen band
            if first:
                v += 0.1                                      # each clump's lit edge
            elif last:
                v -= 0.12                                     # and its shadowed edge: the clumps separate
            if abs(x) > 6.5:
                v -= 0.06                                     # the head turning away at the sides
            c = pick(HAIR, v)
            if h2(i, j, 26) > 0.9:
                c = GREY[1]
            if y > ye - 1.0:
                c = HAIR[2] if not first else HAIR[3]          # the clump's tip
            return A(c)
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
            # bushy: lit strands combed outward along the top, a dark underside; the outer tip thins (painted)
            if j == 0:
                if outer:
                    return A(HAIR[2])
                return A(HAIR[6] if ((i + (0 if x < 0 else 1)) % 2 == 0) else HAIR[5])
            return A(HAIR[1] if outer else HAIR[3] if i % 2 else HAIR[2])
        if f == 'top':
            return A(HAIR[6] if i % 2 == 0 else HAIR[5])
        if f == 'bottom':
            return A(HAIR[1])
        return A(HAIR[2])

    if t == 'moustache':
        if f == 'back':
            return None
        if f == 'front':
            # combed strands fanning outward from a parting notch under the nose: a lit top band, the strand
            # direction set by the half (left half leans left, right half leans right), only the tips dark
            col = int(math.floor(x + 6.0))                    # 0..11
            if j == 0 and col in (5, 6):
                return A(HAIR[2])                             # the parting notch
            left = col < 6
            k = (col + j) % 3 if left else (col - j) % 3
            # top band lifted (HAIR 5-6), body HAIR 3-4, bottom row the dark tips
            c = [[HAIR[6], HAIR[5], HAIR[5]], [HAIR[4], HAIR[4], HAIR[3]], [HAIR[3], HAIR[2], HAIR[2]]][j][k]
            if (col, j) in ((3, 0), (8, 1), (10, 0)):
                c = GREY[1]                                   # a few grey strands
            if j == 2 and h2(col, 9, 26) > 0.6:
                c = HAIR[1]                                   # darker tips
            if L['poss'] and j == 2 and h2(col, j, 25) > 0.6:
                c = EMBER[0]                                  # singed tips
            return A(c)
        if f == 'top':
            return A(HAIR[5] if h2(i, j, 27) > 0.5 else HAIR[4])
        if f == 'bottom':
            return A(HAIR[2])
        return A(HAIR[3] if j == 0 else HAIR[2])

    if t == 'fringe':
        # zero-thickness strand plane hanging off the block's bottom edge over the lip: uneven 1-texel strands
        col = int(math.floor(x + 7.0))                        # 0..13
        n = FRINGE_LEN[col]
        if j >= n:
            return None
        c = HAIR[3] if j == 0 else HAIR[1]
        if j == 0 and col in (3, 9):
            c = HAIR[4]                                       # the lit root of a clump
        if L['poss'] and j == n - 1 and h2(col, 4, 33) > 0.5:
            c = EMBER[0]
        return A(c)

    if t == 'moustache_end':
        if f == 'back':
            return None
        outer = (i == 0) if x < 0 else (i == ctx.w - 1)
        if f == 'front':
            if j == ctx.h - 1:
                if not outer:
                    return None                               # ragged: the inner strand is shorter
                return A(EMBER[0] if L['poss'] else HAIR[1])
            return A([HAIR[4], HAIR[3], HAIR[2]][min(j, 2)] if not (outer and j == 0) else HAIR[5])
        if f == 'bottom':
            return A(HAIR[1])
        if f == 'top':
            return A(HAIR[4])
        if j == ctx.h - 1 and f != outer_face(ctx):
            return None
        return A(HAIR[3] if j < 2 else HAIR[2])
    return A(HAIR[2])


FRINGE_LEN = [2, 2, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 2, 2]     # clumps: long under the droopy ends, parted in the middle


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
        return 9.0
    return 10.0


# possessed: sooty thumb prints (thumb-shaped, a soft edge texel), world (x, y) of each print's top-left corner and
# whether it is mirrored
THUMB = [
    ".ee.",
    "eCCe",
    "eCCe",
    ".eCe",
    "..e.",
]
SMUDGES = [(-12.0, -11.0, False), (11.0, -6.0, True), (-7.0, -17.0, False), (8.0, -18.0, True), (2.0, -1.0, False)]


def soot(ctx, L, c, x, y, seed):
    """Possessed: a few deliberate charcoal thumb prints (not noise, not filled discs)."""
    if not L['poss']:
        return c
    for (sx_, sy_, flip) in SMUDGES:
        ci = int(math.floor(x - sx_))
        cj = int(math.floor(y - sy_))
        if 0 <= ci < 4 and 0 <= cj < 5:
            ch = THUMB[cj][3 - ci if flip else ci]
            if ch == 'C':
                return mix(c, SOOT, 0.6)
            if ch == 'e':
                return mix(c, SOOT, 0.3)
    return c


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
        # stand-up collar round the fat neck: white band, the apron's neck strap running round it
        if f == 'bottom':
            return None
        if f == 'top':
            if abs(x) < 7.3 and -4.3 < z < 5.3:
                return None                                   # only inside the neck's footprint (no see-through slit)
            if z > 5.0 or z < -4.0 or abs(x) > 7.0:
                return A(pick(WHITE, 0.82) if abs(x) > 5.5 or z > 0 else APRON[3])
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

    return A(stripe_col(u, v))


# ------------------------------------------------------------------ the belly (stacked slabs) + the apron over it
# (y0, y1, front z, half width): a stepped ellipse 26 wide, sticking out 11 texels in front of the chest.  The text
# rows sit on the flat front (half-texel steps): REY on slabs 3-4, DEL on slabs 4-5 (no shear in 3/4 views).
BELLY = [
    (-13, -12, -10.0, 9),
    (-12, -11, -13.0, 10),
    (-11, -10, -15.0, 12),
    (-10, -8, -16.5, 13),
    (-8, -2, -17.0, 13),
    (-2, 1, -16.5, 13),
    (1, 2, -15.0, 12),
    (2, 3, -13.0, 11),
    (3, 4, -10.0, 10),
]
REY_Y0, DEL_Y0, TXT_X0 = -10, -4, -6                    # print rows / first column on the belly (world texels)
STAINS = {(5, -6): 2, (5, -5): 1, (6, -5): 1, (-8, -9): 1, (-3, 2): 1}
STAINS_P = {(-7, -1): 0, (-6, -1): 1, (-6, 0): 0, (8, -10): 0}


def belly_side_v(y):
    """Shirt value on the ball's sides at height y (lit upper half, falling on the lower half)."""
    v = 0.62 + (0.03 if y < -8 else 0.0)
    if y >= -2.0:
        v -= 0.08 + max(0.0, y) * 0.02
    return v


def belly_mat(ctx, L):
    f = ctx.face
    k = ctx.cube.slab
    y0, y1, zf, hw = BELLY[k]
    x, y, z = rest_pos(ctx)
    ahw = apron_hw(y)
    lower = y >= -2.0                                         # the half of the ball that turns away from the light
    if f == 'front':
        if abs(x) < ahw:
            return A(apron_belly(ctx, L, x, y, ahw))
        v = belly_side_v(y) + 0.04 - (abs(x) - ahw) * 0.05
        if -5.0 <= y < -4.0:
            return A(APRON[3])                                # the waist tie leaving the apron
        return A(soot(ctx, L, stripe_col(x, v), x, y, 63))
    if f in ('west', 'east'):
        if hw <= ahw + 0.01:
            return A(pick(APRON, 0.5 - (0.1 if lower else 0.0)))     # narrow slabs: the apron wraps round
        if z < zf + 1.0 and hw - ahw < 1.6:
            return A(pick(APRON, 0.52 if not lower else 0.4))        # its folded edge seen from the side
        v = belly_side_v(y)
        # the shirt pulled tight over the ball: two curved stress folds running to the navel
        if abs((y + 1.5) - (z + 10.0) * 0.55) < 0.5 or abs((y + 7.5) - (z + 10.0) * 0.45) < 0.5:
            v -= 0.1
        if -5.0 <= y < -4.0:
            return A(APRON[3])                                # the waist tie running round to the back
        return A(soot(ctx, L, stripe_col(z, v), x, y, 64))
    if f in ('top', 'bottom'):
        # the steps' treads: the same value as the side at this height, so the stack never reads as plates
        if abs(x) < ahw:
            av = apron_value(x, y - (0.5 if f == 'top' else -0.5), ahw)
            return A(pick(APRON, av + (0.03 if f == 'top' else -0.04)))
        return A(stripe_col(x, belly_side_v(y) + (0.02 if f == 'top' else -0.03)))
    # back: only the wide slabs show behind the arms
    return A(stripe_col(x, 0.5))


def apron_value(x, y, ahw):
    """Black canvas over the ball: a sheen across the top of the dome, darker as it turns under, folded edges."""
    row = int(math.floor(y))
    v = 0.4
    if row <= -10:
        v += 0.1                                              # the top of the dome faces the sky
    elif row <= -8 and abs(x) < 7.0:
        v += 0.06                                             # sheen
    if row >= 0:
        v -= 0.08 + 0.04 * row                                # turning under, into the shadow
    ax = abs(x)
    if ax > ahw - 1.0:
        v += 0.1                                              # the hemmed edge
    elif ax > ahw - 3.0:
        v -= 0.07                                             # the canvas wrapping round the ball, away from us
    elif ax < 4.0 and -10 <= row <= -6:
        v += 0.04                                             # the crown of the belly
    return v


def apron_belly(ctx, L, x, y, ahw):
    """The apron's front over the ball: canvas value, grease, REY / DEL printed on it (world coordinates)."""
    col = int(math.floor(x)) - TXT_X0
    row = int(math.floor(y))
    v = apron_value(x, y, ahw)
    if h2(int(x * 3) + row, row * 7, 71) > 0.92:
        v += 0.05                                             # canvas weave sparkle
    for (y_0, txt) in ((REY_Y0, TXT_REY), (DEL_Y0, TXT_DEL)):
        if (col, row - y_0) in txt:
            c = letter(col, row - y_0)
            if row >= 0:
                c = LETTER[1]                                  # the print in the shadow of the dome
            if L['poss'] and h2(col, row, 79) > 0.8:
                c = mix(c, SOOT, 0.6)                          # sooty thumb prints over the letters
            return c
    p = (int(math.floor(x)), row)
    if p in STAINS:
        return GREASE[STAINS[p]]
    if L['poss'] and p in STAINS_P:
        return mix(pick(APRON, v), EMBER[STAINS_P[p]], 0.6)    # scorch marks from the blue fire
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
    if t in ('skirt', 'hem'):
        lower = t == 'hem'
        if f == 'front':
            if i == 0 or i == ctx.w - 1:
                return A(pick(APRON, v + 0.16))               # the hemmed side edges
            if lower:
                if j == ctx.h - 1:
                    if L['poss'] and h2(i, j, 74) > 0.35:
                        return A(EMBER[1] if h2(i, j, 75) > 0.6 else hx('#4a2a14'))     # singed hem
                    return A(pick(APRON, v + 0.14))           # hem
                if j == ctx.h - 2 and i % 3 != 1:
                    return A(pick(APRON, v + 0.2))            # stitched hem line
                ox = (ctx.w - W_ASADO) // 2
                if (i - ox, j) in TXT_ASADO:
                    return A(letter(i - ox, j))
                stains = {(3, 5): 1, (4, 5): 2, (17, 0): 1, (18, 1): 2}
                if (i, j) in stains:
                    return A(GREASE[stains[(i, j)]])
                if j == 0:
                    v -= 0.06                                 # the fold where the two panels meet
                return A(pick(APRON, v))
            # upper panel: in the belly's shadow at the top, two soft vertical folds
            if j == 0:
                v -= 0.1
            if i in (6, 14):
                v += 0.06
            elif i in (7, 15):
                v -= 0.05
            return A(pick(APRON, v))
        if f == 'back':
            return A(pick(APRON, 0.2))
        # side and bottom faces: the lit hem tone (the 2-texel canvas edge reads as cloth, not a board)
        return A(APRON[7] if (f != 'bottom' and ctx.j % 3 != 2) else APRON[6])
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
            return A(stripe_col(x, 0.48))                    # the shirt's tail (shows if a lean lifts the torso)
        if 0.0 < y < 2.0:
            # the belt under the belly
            if side and (int(around(ctx)) % 9 == 4):
                return A(pick(KHAKI, v - 0.05))               # belt loop
            return A(pick(BELT, 0.5 + face_light(ctx) * 0.8 + (0.12 if y < 1.0 else 0.0)))
        if y < 0.0:
            return A(stripe_col(around(ctx), v - 0.08))       # shirt tucked in (seen at the back / under a lean)
        if f in ('back', 'front') and abs(x) < 0.5:
            return A(pick(KHAKI, v - 0.2))                    # the centre seam running down into the crotch
        if f in ('back', 'front') and abs(x) < 1.5 and y > 3.0:
            return A(pick(KHAKI, v - 0.12))                   # the crotch crease
        if f == 'back' and 2.0 < y and abs(abs(x) - 5.5) < 2.6:
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
            if f in ('front', 'back') and abs(x) < 2.25:
                v -= 0.1
            return A(pick(KHAKI, v))
        # cargo pocket on the outer side, crease lines, inseam
        if f == outer_face(ctx) and 2.0 < ly < 7.0 and 2.0 < (lz if f == 'east' else d - lz) < 8.0:
            if ly < 3.0:
                return A(pick(KHAKI, v + 0.08 if ly < 2.5 else v - 0.12))    # flap
            if abs(lz - d / 2) > 2.4 or ly > 6.4:
                return A(pick(KHAKI, v - 0.1))                # pocket seam
            return A(pick(KHAKI, v - 0.02))
        if f == inner_face(ctx):
            v -= 0.12
        if f in ('front', 'back') and abs(x) < 3.25:
            # the two inner columns: the inseam (dark line) and the cloth folding into the crotch
            v -= 0.2 if abs(x) < 2.25 else 0.1
            if ly < 2.0:
                v -= 0.06
        if f == 'front' and int(ly) in (3, 6) and int(lx) % 4 == 1:
            v -= 0.08                                         # creases
        if f == 'back' and int(ly) in (2, 5) and 3.0 < abs(x) < 6.0:
            v -= 0.07                                         # creases behind the knee / under the seat
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
    """Stainless grill tongs.  Bars run along the tongs' local -Z: polished top edge, mid sides, dark underside, a
    black ribbed rubber grip near the hinge; scalloped spoon heads; a riveted hinge.  Blued when possessed."""
    t = tag(ctx)
    f = ctx.face
    lx, ly, lz = local(ctx)
    x, y, z = rest_pos(ctx)
    w, h, d = ctx.cube.size
    if t in ('bar', 'bar_lo'):
        if z > -2.0 and f != 'back':
            # black rubber grip, ribbed every texel
            rib = int(math.floor(z)) % 2 == 0
            return A(GRIP[4] if (rib and f == 'top') else GRIP[2] if rib else GRIP[1])
        if f == 'top':
            c = STEEL[8] if ctx.i == 0 else STEEL[5]          # one polished highlight texel along the top edge
        elif f == 'bottom':
            c = STEEL[2]
        elif f in ('west', 'east'):
            c = STEEL[6] if ctx.j == 0 else STEEL[3]          # the edge highlight wraps one texel down the side
        elif f == 'front':
            c = STEEL[4]
        else:
            c = STEEL[3]
    elif t in ('head', 'head_lo'):
        # the scalloped spoon (4 wide across the opening): the tip cut into scallops, a lit rim, a dished inner face
        inner = (f == 'west') if t == 'head' else (f == 'east')
        if f == 'front':
            if ctx.j % 2 == 1:
                return None
            c = STEEL[7]
        elif f in ('west', 'east'):
            if lz < 0.7 and ctx.j % 2 == 1:
                return None                                   # the scallops seen from the side
            rim = ctx.j in (0, ctx.h - 1) or lz < 1.0
            c = (STEEL[4] if rim else STEEL[2]) if inner else (STEEL[8] if rim else STEEL[6])
        elif f == 'top':
            c = STEEL[8]
        elif f == 'bottom':
            c = STEEL[3]
        else:
            c = STEEL[5]
    elif t == 'hinge':
        c = STEEL[6]
        if f in ('west', 'east') and ctx.i == ctx.w // 2 and ctx.j == ctx.h // 2:
            c = STEEL[8]                                      # the rivet
        elif f == 'bottom':
            c = STEEL[3]
        elif f == 'top':
            c = STEEL[7]
    else:
        c = pick(STEEL, 0.55 + face_light(ctx) * 1.2)
    if L['poss'] and t != 'hinge':
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
        # lumps: 2-3 texel chunks with lit facets; the top row of the sides is bitten out so the heap is ragged
        ck = h2(i // 2 * 3 + (j // 2) * 11, i // 3 + j * 5, 91)
        if f != 'top' and j == 0 and h2(i // 2, 3, 92) > 0.5:
            return None
        if ck > 0.78:
            return A(COAL[5] if (i + j) % 2 == 0 else COAL[4])
        if ck > 0.5:
            return A(COAL[3])
        return A(COAL[1] if (i + j) % 3 else COAL[2])
    if t == 'rim':
        if f == 'bottom':
            return None
        if f == 'top':
            if 1.0 < lx < w - 1.0 and 1.0 < lz < d - 1.0:
                return A(COAL[1])
            return A(pick(KRAFT, 0.8))
        # the rolled-over paper: a lit fold on top, a crease, ragged torn bottom edge shadow
        v += 0.12 if j == 0 else -0.08
        if j == 1 and h2(i, 7, 93) > 0.75:
            v -= 0.1
        return A(pick(KRAFT, v))
    if f == 'top':
        return A(COAL[2])
    if f == 'bottom':
        return A(pick(KRAFT, 0.2))
    if f in ('west', 'east'):
        if abs(lz - d / 2) < 0.6:
            v -= 0.14                                         # gusset fold
        if j == ctx.h - 1:
            v -= 0.1
        return A(pick(KRAFT, v - 0.04))
    if f == 'front':
        ox = (ctx.w - W_CARBON) // 2
        if (i - ox, j - 1) in TXT_CARBON:
            return A(INK[0] if j - 1 < 4 else INK[1])
        if j == ctx.h - 2:
            if abs(i - ctx.w / 2 + 0.5) < 1.0:
                return A(hx('#f2c84a'))                       # small flame logo in the red band
            return A(RED[2] if (i + 1) % 6 else RED[1])
        if j == ctx.h - 1:
            return A(RED[0] if 1 <= i < ctx.w - 1 else pick(KRAFT, v - 0.15))
        if (i, j) in ((1, 6), (2, 6), (23, 6), (24, 6), (25, 5)):
            return A(COAL[4])                                 # charcoal dust smudges (clear of the lettering)
        if i in (7, 18) and j != 8:
            v += 0.1 if j % 3 else -0.06                      # two vertical paper creases
        elif i in (8, 19):
            v -= 0.06
        if j == 0:
            v -= 0.08                                         # shadow under the rolled rim
        return A(pick(KRAFT, v))
    return A(pick(KRAFT, v - 0.06))


# ------------------------------------------------------------------ possessed toggles: the grin + the eyes
# The grin, hand placed per 1-texel column.  Front: k = |column| from the middle (0 = the two centre columns, 8 = the
# jowl / cheek column).  (bite y, upper teeth rows, lower teeth rows): the gum one row above the upper teeth, the
# lower lip one row under the lower teeth.  The centre sits on the jaw under the moustache fringe, columns 5-6 hide
# behind the moustache ends, columns 7-8 shoot up the cheeks beside them: the corners climb.
GRIN_FRONT = {0: (-22, 2, 1), 1: (-22, 2, 1), 2: (-22, 2, 1), 3: (-22, 2, 1), 4: (-22, 2, 1), 5: (-23, 2, 1),
              6: (-23, 2, 1), 7: (-24, 3, 1), 8: (-25, 2, 1)}
# Sides (zero-thickness planes on the cheek cubes): column s = texels back from the cheek's front (z = -7.5 + s);
# the slit climbs toward the ear and thins to a black line.
GRIN_SIDE = {0: (-25, 1, 1), 1: (-26, 1, 0), 2: (-26, 0, 0), 3: (-27, 0, 0), 4: (-27, 0, 0), 5: (-27, 0, 0)}
# irregular teeth (tooth id = (column + 30 [+1 lower]) // 3): two longer upper teeth, one missing, two dead grey
LONG_UP = {9, 11}
MISSING_UP = {12}
DEAD = {('u', 7), ('l', 10)}


def grin_px(L, spec, row, col, k, side=False):
    """-> (colour, is_upper_half) for the grin pixel at integer row y = row, or (None, None)."""
    bite, nu, nl = spec
    top_lip = bite - nu - 1
    bot_lip = bite + nl
    if row < top_lip - (1 if k >= 6 or side else 0) or row > bot_lip:
        return None, None
    upper = row < bite
    corner = side or k >= 5
    if row == top_lip - 1:
        return LIPP[2], True                                  # the cheek folding over the corner (stretched)
    if row == top_lip:
        if nu == 0 and nl == 0:
            return LIPP[0], True                              # the slit's upper edge
        # the gums above the upper teeth: darkening toward the corners
        return (GUM[2] if k < 3 and not side else GUM[1] if k < 6 and not side else GUM[0]), True
    if row == bot_lip:
        return (LIPP[1] if not corner else LIPP[0]), False
    tid_u = (col + 30) // 3
    tid_l = (col + 31) // 3
    if not side and not upper and row == bite and tid_u in LONG_UP and (col + 30) % 3 != 2:
        c = TEETH[3]                                          # a long upper tooth reaching over the lower row
        return (TEETH[max(1, TEETH.index(c) - 2)] if corner else c), True
    p = (col + (0 if upper else 1) + 30) % 3
    if p == 2:
        return (L['mouth'][1] if not corner else GUM[0]), upper     # the gap between two teeth
    if upper and not side and tid_u in MISSING_UP:
        return L['mouth'][0], True                            # a missing tooth: black
    if upper:
        c = TEETH[5] if row < bite - 1 or nu == 1 else TEETH[4]              # upper teeth: bright, the tips shaded
    else:
        c = TEETH[4] if row == bite else TEETH[3]                           # lower teeth: in the lip's shade
    if p == 1:
        c = TEETH[TEETH.index(c) - 1]                         # each tooth: lit left half, shaded right half
    if (('u', tid_u) in DEAD and upper) or (('l', tid_l) in DEAD and not upper):
        c = TEETH[1]                                          # a dead grey tooth
    if corner:
        c = TEETH[max(1, TEETH.index(c) - 2)]                 # yellower and darker toward the corners
    return c, upper


def smile_mat(ctx, L):
    t = tag(ctx)
    f = ctx.face
    x, y, z = rest_pos(ctx)
    row = int(math.floor(y))
    if t == 'smile_side':
        if f != outer_face(ctx):
            return None
        s = int(math.floor(z + 7.5))
        if s not in GRIN_SIDE:
            return None
        c, up = grin_px(L, GRIN_SIDE[s], row, s, s, side=True)
        return None if c is None else A(c)
    if f != 'front':
        return None
    col = int(math.floor(x))
    k = int(abs(col + 0.5))
    if k not in GRIN_FRONT:
        return None
    c, up = grin_px(L, GRIN_FRONT[k], row, col if col >= 0 else -col - 1, k)
    if c is None:
        return None
    on_head = up or row < -24
    if (t == 'smile_front') != on_head:
        return None
    return A(c)


def eyes_mat(ctx, L):
    """Opaque possessed eyes (zero-thickness plane): the whole 4 x 3 eye black (the demon opens them wide), white
    2 x 2 pupils; transparent elsewhere."""
    if ctx.face != 'front':
        return None
    x, y, z = rest_pos(ctx)
    ch, c, r = face_char(x, y)
    if ch in ('I', 'i', 'g'):
        return A(PUPIL if ch != 'i' else PUPIL2)
    if ch in ('W', 'V', 'T', 'L') and 6 <= r <= 8:
        return A(VOID)
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


DEMON_EYES_X0, DEMON_EYES_Y0 = -6.0, -31.0

KINDS = {
    'skin': skin_mat, 'hair': hair_mat, 'shirt': shirt_mat, 'belly': belly_mat, 'apron': apron_mat, 'shorts': shorts_mat,
    'sole': sole_mat, 'steel': steel_mat, 'bag': bag_mat, 'smile': smile_mat, 'eyes': eyes_mat,
}


def make_mat(look):
    L = LOOKS[look]

    def mat(ctx):
        return KINDS[getattr(ctx.cube, 'kind', 'skin')](ctx, L)
    mat.look = look
    return mat


DEFAULT_MAT = make_mat('normal')


def _copia_mat():
    """B3 look 'copia' (casa_terror.md 2 Act 5, event 41): Jorge's own face with grey skin, the eyes one texel further
    apart and wide open round a pinpoint (unblinking), and under the moustache a grin from jowl to jowl showing every
    tooth and the gums.  Java index 2 (FamilyEntity.LOOK_COPIA) -> jorge_copia.png; no toggles (the possessed grin and
    eyes stay hidden)."""
    base = make_mat('copia')

    def mat(ctx):
        _FACE_ACTIVE[0] = COPIA_FACE
        try:
            return base(ctx)
        finally:
            _FACE_ACTIVE[0] = FACE
    mat.look = 'copia'
    return mat


VARIANT_MATS = {'normal': DEFAULT_MAT, 'poseido': make_mat('poseido'), 'copia': _copia_mat()}
FOCUS = 'head'


# ------------------------------------------------------------------ toggles (Java: ModelPart.visible)
TOGGLE_DEFAULT = {'smile': False, 'smile_jaw': False, 'demon_eyes': False, 'bag': False, 'tongs': True}
VARIANT_TOGGLES = {'normal': {}, 'poseido': {'smile': True, 'smile_jaw': True, 'demon_eyes': True}}
POSE_TOGGLES = {'carry_bag': {'bag': True, 'tongs': False}, 'grill_flip': {'tongs': False},
                'limp_fall': {'tongs': False}}
# per-look rest offsets (bone -> (xRot, yRot, zRot, dx, dy, dz), radians / texels), ADDED under every pose while that
# look is active: the possessed face scowls (brows in an angry V) and the grin shoves the moustache up
VARIANT_POSES = {
    'normal': {},
    'poseido': {
        'right_brow': (0, 0, 0.42, 0, 1.4, 0),
        'left_brow': (0, 0, -0.34, 0, 0.5, 0),
        'moustache': (-0.08, 0, 0, 0, -0.8, 0),
    },
}


def visible_set(variant=None, pose=None):
    vis = dict(TOGGLE_DEFAULT)
    vis.update(VARIANT_TOGGLES.get(variant or 'normal', {}))
    vis.update(POSE_TOGGLES.get(pose, {}))
    return {k for k, v in vis.items() if v}


class JorgeModel(Model):
    """Exports every bone to Java; the preview / gallery JSON hides the toggle bones the current look / pose hides.

    Texture seams: the atlas is packed with a 1-texel gutter round every cube's UV block and each face's border texels
    are extruded into that gutter, so a face edge seen at a grazing angle never samples a neighbouring cube's colours
    (the white collar-tip line that showed at the nape in the 180 deg view).  That gutter is why the sheet is 256 x 144
    (135 rows used) and not 256 x 128."""
    visible = None

    def pack(self, pad=1):
        return super().pack(pad=pad)

    def paint(self, default_mat, seed=1, layer='base'):
        img = super().paint(default_mat, seed=seed, layer=layer)
        if layer != 'base':
            return img
        W, Hh = img.size
        own = np.zeros((Hh, W), bool)
        rects = []
        for b in self.bones():
            for c in b.cubes:
                for f in ('top', 'bottom', 'west', 'front', 'east', 'back'):
                    u0, v0, fw, fh = self.face_rect(c, f)
                    if fw > 0 and fh > 0:
                        own[v0:v0 + fh, u0:u0 + fw] = True
                        rects.append((u0, v0, fw, fh))
        px = img.load()
        for (u0, v0, fw, fh) in rects:
            for j in range(-1, fh + 1):
                for i in range(-1, fw + 1):
                    if 0 <= i < fw and 0 <= j < fh:
                        continue
                    x, y = u0 + i, v0 + j
                    if not (0 <= x < W and 0 <= y < Hh) or own[y, x] or px[x, y][3] > 0:
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
        d['variant_poses'] = VARIANT_POSES
        if self.visible is None:
            return d
        hide = set()
        for b in self.bones():
            if b.name in TOGGLE_DEFAULT and b.name not in self.visible:
                for sub in b.walk():
                    hide.add(sub.name)
        for bd in d['bones']:
            if bd['name'] in hide and bd['cubes']:
                bd['hidden_cubes'] = bd['cubes']             # a toggle-aware viewer can still show them
                bd['cubes'] = []
        return d


def _argv(flag):
    a = sys.argv
    return a[a.index(flag) + 1] if flag in a and a.index(flag) + 1 < len(a) else None


# ------------------------------------------------------------------ rest pose (degrees)
ARM_OUT = 9.0           # arms angled out round the belly
ARM_FWD = -3.0
ELBOW = -12.0           # forearms a little forward
TONGS_TILT = 76.0       # tongs hang tips-down along the thigh
TONGS_OUT = -2.0        # ... their tips toward the thigh line
TONGS_OPEN = 15.0       # outer arm of the tongs sprung open: a clear V
TOES_OUT = 6.0          # duck stance (kept small so the crotch gap stays open)
BROW_ARCH = 6.0         # right brow: raised, the outer end arched down
BROW_SMUG = 5.0         # left brow: the inner end a touch lower (knowing look)
SKIRT_TILT = 35.0       # upper apron panel drapes back from the belly's underside toward the thighs
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

    # ---------------- body: the root at the hips, owns only the hips + the legs
    bone('body', (0, 3, 0))
    box('body', (-10.5, -4, -5.5), (21, 8, 11), 'shorts', 'hips')

    # ---------------- chest: everything above the belt (leans / rolls go here, never on body)
    bone('chest', (0, 2, 0), 'body')
    box('chest', (-11, -19, -6), (22, 17, 12), 'shirt', 'torso')
    box('chest', (-10, -20, -5), (20, 1, 10), 'shirt', 'yoke')
    box('chest', (-8, -21.5, -6), (16, 2, 12), 'shirt', 'collar')
    box('chest', (-7, -20.5, -7), (14, 8, 1), 'apron', 'bib')
    box('chest', (-10, -20, -6.6), (3, 3, 0), 'shirt', 'collar_tip')
    box('chest', (7, -20, -6.6), (3, 3, 0), 'shirt', 'collar_tip')
    box('chest', (-4.5, -7, 6.15), (9, 5, 0), 'apron', 'bow')

    # ---------------- belly: a ball of stacked slabs (stepped ellipse in profile AND from the front), the apron over
    # its front, the shirt pulled tight round its sides
    bone('belly', (0, -4, -6), 'chest')
    for k, (y0, y1, zf, hw) in enumerate(BELLY):
        dep = int(math.floor(-5.0 - zf + 1e-6))               # backs just inside the torso front (z -5 .. -5.5)
        c = box('belly', (-hw, y0, zf), (int(round(2 * hw)), y1 - y0, dep), 'belly', 'belly_%d' % k)
        c.slab = k
    # the apron skirt: an upper panel draping back from the belly's underside, a plumb lower panel (ASADO)
    bone('apron_skirt', (0, 3, -10), 'belly', rot=(SKIRT_TILT, 0, 0))
    box('apron_skirt', (-10.5, 3, -11), (21, 6, 2), 'apron', 'skirt')
    bone('apron_hem', (0, 9, -10), 'apron_skirt', rot=(-SKIRT_TILT, 0, 0))
    box('apron_hem', (-11, 9, -11), (22, 7, 2), 'apron', 'hem')

    # ---------------- neck + head
    bone('neck', (0, -21, 0), 'chest')
    box('neck', (-7.5, -27, -4.5), (15, 6, 10), 'skin', 'neck')
    bone('head', (0, -24, 0), 'neck')
    box('head', (-8, -37, -8), (16, 13, 16), 'skin', 'skull')
    box('head', (-8, -37, -8), (16, 11, 16), 'hair', 'hair', inflate=0.5)
    box('head', (-2, -38.5, -8.5), (3, 2, 4), 'hair', 'tuft')
    box('head', (-2, -31, -11), (4, 4, 3), 'skin', 'nose')
    box('head', (-10, -31, -1.5), (2, 5, 3), 'skin', 'ear', sx=-1)
    box('head', (8, -31, -1.5), (2, 5, 3), 'skin', 'ear', sx=1)
    box('head', (-9, -28, -7.5), (1, 4, 6), 'skin', 'cheek', sx=-1)
    box('head', (8, -28, -7.5), (1, 4, 6), 'skin', 'cheek', sx=1)
    bone('right_brow', (-4.5, -34, -8.5), 'head', rot=(0, 0, -BROW_ARCH))
    box('right_brow', (-7, -35, -9.5), (5, 2, 2), 'hair', 'brow', sx=-1)
    bone('left_brow', (4.5, -33, -8.5), 'head', rot=(0, 0, -BROW_SMUG))
    box('left_brow', (2, -34, -9.5), (5, 2, 2), 'hair', 'brow', sx=1)
    bone('moustache', (0, -25.5, -9), 'head')
    box('moustache', (-6, -27, -10), (12, 3, 2), 'hair', 'moustache')
    box('moustache', (-7, -24, -8.6), (14, 2, 0), 'hair', 'fringe')
    box('moustache', (-7, -26, -9.6), (2, 4, 2), 'hair', 'moustache_end', sx=-1, inflate=-0.1)
    box('moustache', (5, -26, -9.6), (2, 4, 2), 'hair', 'moustache_end', sx=1, inflate=-0.1)
    bone('jaw', (0, -24, 1), 'head')
    box('jaw', (-9, -24, -8), (18, 4, 11), 'skin', 'jaw')            # jowly: 2 wider than the skull
    box('jaw', (-4.5, -20, -7.5), (9, 1, 3), 'skin', 'chin2')        # the double chin resting on the bib
    # possessed toggles: the grin.  Gums + upper teeth + the corners climbing the cheeks ride the head, lower teeth +
    # lower lip ride the jaw, so the grin splits open when the jaw drops.
    bone('smile', (0, -24, -8.2), 'head')
    box('smile', (-9, -29, -8.15), (18, 7, 0), 'smile', 'smile_front')
    box('smile', (-9.12, -28, -7.5), (0, 4, 6), 'smile', 'smile_side', sx=-1)
    box('smile', (9.12, -28, -7.5), (0, 4, 6), 'smile', 'smile_side', sx=1)
    bone('smile_jaw', (0, -24, 1), 'jaw')
    box('smile_jaw', (-9, -24, -8.1), (18, 4, 0), 'smile', 'smile_jaw')
    bone('demon_eyes', (0, -29.5, -8.2), 'head')
    box('demon_eyes', (DEMON_EYES_X0, DEMON_EYES_Y0, -8.2), (12, 3, 0), 'eyes', 'demon_eyes',
        decals={'eyes:front': eyes_glow})

    # ---------------- arms
    for side, sx in (('right', -1), ('left', 1)):
        arm, fa, hand = f'{side}_arm', f'{side}_forearm', f'{side}_hand'
        ax = 15.0 * sx
        bone(arm, (11.5 * sx, -18, 0), 'chest', rot=(ARM_FWD, 0, -ARM_OUT * sx))
        box(arm, (ax - 4, -20.5, -4), (8, 8, 8), 'shirt', 'sleeve', sx=sx)
        box(arm, (ax - 3, -13, -3), (6, 6, 6), 'skin', 'upper_arm', sx=sx)
        bone(fa, (ax, -7.5, 0), arm, rot=(ELBOW, 0, 0))
        box(fa, (ax - 3, -8, -3), (6, 9, 6), 'skin', 'forearm', sx=sx, inflate=-0.1, watch=(sx > 0))
        bone(hand, (ax, 1, 0), fa)
        box(hand, (ax - 1.5, 0.5, -3), (3, 5, 6), 'skin', 'palm', sx=sx)
        tx = ax - 0.5 if sx < 0 else ax - 1.5                 # thumb on the front edge, palm side
        box(hand, (tx, 1.0, -4.4), (2, 4, 2), 'skin', 'thumb', sx=sx, inflate=-0.15)
        if sx < 0:
            # four fingers in one bone, curled round the tongs grip at rest
            bone('right_fingers', (ax, 5.5, 0), hand, rot=(0, 0, FIST))
            for fz, fl in ((-3.1, 4), (-1.6, 5), (-0.1, 4), (1.4, 3)):
                box('right_fingers', (ax - 1, 5.5, fz), (2, fl, 2), 'skin', 'finger', sx=sx, inflate=-0.25)
            # the tongs: riveted hinge in the fist, two 2 x 2 arms side by side (the fixed one on the inner side),
            # scalloped spoon heads 4 wide across the opening; the outer arm ('tongs_arm') swings out about its local
            # Y, so the V opens sideways: it reads from the front and in 3/4, hanging tips-down along the thigh
            px = ax + 0.5
            bone('tongs', (px, 6.5, 0), hand, rot=(TONGS_TILT, 0, TONGS_OUT))
            box('tongs', (px - 2, 5, 3), (4, 3, 2), 'steel', 'hinge')
            box('tongs', (px, 5.5, -7), (2, 2, 10), 'steel', 'bar')
            box('tongs', (px, 4.5, -10), (2, 4, 3), 'steel', 'head')
            bone('tongs_arm', (px, 6.5, 4), 'tongs', rot=(0, TONGS_OPEN, 0))
            box('tongs_arm', (px - 2, 5.5, -7), (2, 2, 10), 'steel', 'bar_lo')
            box('tongs_arm', (px - 2, 4.5, -10), (2, 4, 3), 'steel', 'head_lo')
        else:
            # index on its own bone (pointing), middle / ring / pinky curl together
            bone('left_index', (ax, 5.5, -2.1), hand, rot=(0, 0, INDEX_L))
            box('left_index', (ax - 1, 5.5, -3.1), (2, 4, 2), 'skin', 'finger', sx=sx, inflate=-0.25)
            bone('left_fingers', (ax, 5.5, 0.9), hand, rot=(0, 0, FINGERS_L))
            for fz, fl in ((-1.6, 5), (-0.1, 4), (1.4, 3)):
                box('left_fingers', (ax - 1, 5.5, fz), (2, fl, 2), 'skin', 'finger', sx=sx, inflate=-0.25)

    # ---------------- legs (children of body: they never inherit a lean)
    for side, sx in (('right', -1), ('left', 1)):
        leg, shin = f'{side}_leg', f'{side}_shin'
        lxc = 5.75 * sx
        bone(leg, (lxc, 4, 0), 'body', rot=(0, -TOES_OUT * sx, 0))
        box(leg, (lxc - 4.5, 3, -5), (9, 9, 10), 'shorts', 'shorts', sx=sx)
        box(leg, (lxc - 4.5, 10, -5), (9, 2, 10), 'shorts', 'cuff', sx=sx, inflate=0.15)
        bone(shin, (lxc, 12, 0), leg)
        box(shin, (lxc - 3, 12, -3), (6, 9, 6), 'skin', 'shin', sx=sx)
        box(shin, (lxc - 3.5, 21, -4), (7, 2, 7), 'skin', 'foot', sx=sx)
        box(shin, (lxc - 3.5, 22, -7), (7, 1, 3), 'skin', 'toes', sx=sx)
        box(shin, (lxc - 4, 23, -8), (8, 1, 12), 'sole', 'sole', sx=sx)

    # ---------------- the charcoal bag (toggle): a 10 kg kraft sack lying across the top of the belly (the belly is the
    # shelf), hugged at both ends; open top rolled over, lumps of charcoal showing
    bone('bag', (0, -13, -14), 'chest')
    box('bag', (-13.5, -17.5, -18), (27, 9, 7), 'bag', 'sack')
    box('bag', (-14, -19.5, -18.5), (28, 2, 8), 'bag', 'rim')
    box('bag', (-11.5, -20.5, -17), (23, 2, 5), 'bag', 'coal')

    # the look's rest offsets (VARIANT_POSES; Java adds the same table while that look is active)
    vp = VARIANT_POSES.get(variant or 'normal', {})
    for name, (rx, ry, rz, dx, dy, dz) in vp.items():
        b = r.bones[name]
        b.rot = (b.rot[0] + math.degrees(rx), b.rot[1] + math.degrees(ry), b.rot[2] + math.degrees(rz))
        b.pivot = (b.pivot[0] + dx, b.pivot[1] + dy, b.pivot[2] + dz)

    m = JorgeModel('jorge', 256, 144, r.roots)
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


# ------------------------------------------------------------------ poses
# bone -> (xRot, yRot, zRot, dx, dy, dz) in radians / texels, ADDED to the rest pose.
POSES = {
    'idle': {
        'chest': (-0.04, 0, 0, 0, 0, 0),
        'head': (0.02, -0.1, 0.07, 0, 0, 0),
        'left_arm': (-0.453, 0.715, -0.951, 0, 0, 0),
        'left_forearm': (-2.16, 0, 0, 0, 0, 0),
        'left_hand': (1.528, 0.291, 0.358, 0, 0, 0),
        'left_fingers': (0, 0, -0.15, 0, 0, 0),
        'left_index': (0, 0, -0.1, 0, 0, 0),
        'right_forearm': (-0.3, 0, 0, 0, 0, 0),
    },
    'grill_flip': {
        'chest': (0.55, 0, 0, 0, 0, 0),
        'apron_skirt': (-0.55, 0, 0, 0, 0, 0),
        'neck': (-0.18, 0, 0, 0, 0, 0),
        'head': (-0.32, 0.12, 0.26, 0, 0, 0),
        'jaw': (0.2, 0, 0, 0, 0, 0),
        'right_arm': (-1.085, -0.133, 0.869, 0, 0, 0),
        'right_forearm': (-1.235, 0, 0, 0, 0, 0),
        'right_hand': (-0.247, 1.865, 0.623, 0, 0, 0),
        'right_fingers': (0, 0, 1.15, 0, 0, 0),
        'left_arm': (-1.064, 0.239, -0.737, 0, 0, 0),
        'left_forearm': (-1.123, 0, 0, 0, 0, 0),
        'left_hand': (0.99, 0.557, 0.475, 0, 0, 0),
        'left_fingers': (0, 0, 0.9, 0, 0, 0),
        'left_index': (0, 0, 0.7, 0, 0, 0),
    },
    'knife_conduct': {
        'chest': (-0.1, 0, 0, 0, 0, 0),
        'neck': (-0.08, 0, 0, 0, 0, 0),
        'head': (-0.28, 0.12, -0.16, 0, 0, 0),
        'jaw': (0.38, 0, 0, 0, 0, 0),
        'right_arm': (-2.45, 0.35, -0.55, 0, 0, 0),
        'right_forearm': (-0.45, 0, 0, 0, 0, 0),
        'right_hand': (-0.335, -1.251, 0.413, 0, 0, 0),
        'left_arm': (-2.7, -0.15, 0.68, 0, 0, 0),
        'left_forearm': (-0.35, 0, 0, 0, 0, 0),
        'left_hand': (-0.309, 1.458, -0.484, 0, 0, 0),
        'left_fingers': (0, 0, -0.35, 0, 0, 0),
        'left_index': (0, 0, -0.45, 0, 0, 0),
        'tongs': (0.188, -0.035, -0.607, 0, 0, 0),
        'tongs_arm': (0, 0.12, 0, 0, 0, 0),
        'right_brow': (0, 0, 0.1, 0, -0.6, 0),
        'left_brow': (0, 0, -0.1, 0, -0.6, 0),
    },
    'limp_fall': {
        'body': (-1.571, 0, 0, 0, 9.245, -12.96),
        'neck': (0.1, 0, 0, 0, 0, 0),
        'head': (-0.15, 0.55, 0.1, 0, 0, 0),
        'jaw': (0.45, 0, 0, 0, 0, 0),
        'right_arm': (0.06, 0, 1.3, 0, 0, 0),
        'right_forearm': (-0.25, 0, 0, 0, 0, 0),
        'right_fingers': (0, 0, 0.9, 0, 0, 0),
        'left_arm': (0.06, 0, -1.0, 0, 0, 0),
        'left_forearm': (-0.6, 0, 0, 0, 0, 0),
        'left_fingers': (0, 0, 0.2, 0, 0, 0),
        'right_leg': (-1.25, 0, 0.3, 0, 0, 0),
        'left_leg': (-1.25, 0, -0.3, 0, 0, 0),
        'right_shin': (0.6, 0, 0, 0, 0, 0),
        'left_shin': (0.65, 0, 0, 0, 0, 0),
        'apron_skirt': (-0.5, 0, 0, 0, 0, 0),
        'right_brow': (0, 0, 0, 0, 0.5, 0),
        'left_brow': (0, 0, 0, 0, 0.5, 0),
    },
    'point': {
        'head': (0, 0, -0.08, 0, 0, 0),
        'jaw': (0.12, 0, 0, 0, 0, 0),
        'left_arm': (-1.42, -0.05, 0.12, 0, 0, 0),
        'left_forearm': (0.12, 0, 0, 0, 0, 0),
        'left_index': (0, 0, -0.1, 0, 0, 0),
        'left_fingers': (0, 0, 1.25, 0, 0, 0),
        'right_arm': (-0.255, 0.021, 0.253, 0, 0, 0),
        'right_forearm': (-0.894, 0, 0, 0, 0, 0),
        'tongs': (0.1, 0, -0.15, 0, 0, 0),
        'right_brow': (0, 0, 0, 0, -0.5, 0),
        'left_brow': (0, 0, 0, 0, -1, 0),
    },
    'carry_bag': {
        'chest': (-0.05, 0, 0, 0, 0, 0),
        'right_arm': (-0.44, -0.207, 0.37, 0, 0, 0),
        'right_forearm': (-1.125, 0, 0, 0, 0, 0),
        'right_hand': (0.67, 0.298, 0.237, 0, 0, 0),
        'left_arm': (-0.44, 0.207, -0.37, 0, 0, 0),
        'left_forearm': (-1.125, 0, 0, 0, 0, 0),
        'left_hand': (0.67, -0.298, -0.237, 0, 0, 0),
        'right_fingers': (0, 0, 0.6, 0, 0, 0),
        'left_fingers': (0, 0, 0.4, 0, 0, 0),
        'left_index': (0, 0, 0.5, 0, 0, 0),
    },
    # C (set pieces): seated on a chair / his armchair (added to 'idle'): hips down 3.5 and 2 back, thighs level, shins
    # down, the apron laid over the knees
    'sit_chair': {
        'body': (0, 0, 0, 0, 3.5, 2.0),
        'right_leg': (-1.48, 0, 0, 0, 0, 0),
        'left_leg': (-1.48, 0, 0, 0, 0, 0),
        'right_shin': (1.48, 0, 0, 0, 0, 0),
        'left_shin': (1.48, 0, 0, 0, 0, 0),
        'apron_skirt': (-0.9, 0, 0, 0, 0, 0),
        'apron_hem': (0.6, 0, 0, 0, 0, 0),
    },
}

ANIM_NOTES = """Jorge Morales -- animation notes.  Units: radians for POSES and for the values below (rest rotations quoted in
DEGREES where marked "deg"), offsets in model texels (2x density inside scale_root: 2 texels = 1 vanilla pixel,
32 texels = 1 block).  t = ageInTicks, s = walk speed 0..1.  Every POSES entry is ADDED to the rest pose; blend
between poses over 4-6 ticks unless a note says SNAP (1-2 ticks).  (xRot, yRot, zRot[, dx, dy, dz]); right_* is on
-X; MC applies Z * Y * X.  A positive xRot swings a hanging part's lower end backwards (+Z).

RULES (read first)
* LEAN RULE: 'body' is the root at the hips and owns ONLY the hips and the two legs.  Every lean, bow, sway or roll of
  the upper body goes on 'chest' (pivot at the belt (0, 2, 0)), never on 'body', so the feet never tip or slide.  'body'
  only ever gets dy (the walk bob) and the whole-body fall of limp_fall.  If some code must rotate 'body' anyway, add
  right_leg / left_leg xRot = -(body xRot) and zRot = -(body zRot) on top of any leg rotation.  Every standing pose
  ends with the soles exactly on y = 24.
* APRON RULE: the skirt hangs by gravity.  Whenever chest leans by xRot = L, add apron_skirt xRot = -L (grill_flip does
  this).  Walking: apron_hem xRot = -max(0, -leg xRot) * 0.6 (the thigh pushes the hem forward), lagging 2 ticks.
* TONGS: the tongs' rest is (76 deg, 0, -2 deg) inside the right fist (tips down along the thigh).  Poses aim them by
  ADDING to that rest (see point / knife_conduct).  tongs_arm opens/closes about its local Y.

Looks (VARIANT_MATS, picked by the entity's variant index)
* 0 'normal'  -> jorge.png (+ jorge_eyes.png, empty unless demon_eyes is visible).  The dad: ruddy skin, brown eyes.
* 1 'poseido' -> jorge_poseido.png (+ jorge_poseido_eyes.png).  Corpse-grey skin (cold blue-violet shadows, green only
  as a tint), bruised sockets, branching veins, black sclera / white pupils, charred fingertips, soot thumb prints,
  scorched apron hem, blued tongs.  Both looks share the geometry; the possessed one also turns the toggles below on
  and adds VARIANT_POSES['poseido'].
Render: entityCutoutNoCull + the emissive layer 'eyes' drawn full-bright on top.  The 'eyes' layer only has pixels
on the demon_eyes plane (the two 2 x 2 white pupils), so it glows only while demon_eyes is visible.

VARIANT_POSES (per-look rest offsets, ADDED every frame under any pose while that look is active)
* 'poseido': right_brow (0, 0, 0.42, 0, 1.4, 0) + left_brow (0, 0, -0.34, 0, 0.5, 0) = the brows drop into an angry V
  (the cocky raised right brow is gone); moustache (-0.08, 0, 0, 0, -0.8, 0) = the grin shoves the moustache up so
  the teeth show.  Blend them in over the possession SNAP (2 ticks).

Toggles (ModelPart.visible).  Every frame: start from TOGGLE_DEFAULT, apply VARIANT_TOGGLES[look], then
POSE_TOGGLES[pose] (a pose wins over the look):
* smile        (child of head)  hidden by default; visible in 'poseido'.  The grin's upper half: gums (darkening toward
                                the corners), upper teeth (two longer, one missing, one dead grey), the corners shooting
                                up both cheeks + two side planes back along the cheek cubes.
* smile_jaw    (child of jaw)   hidden by default; visible in 'poseido'.  Lower teeth + lower lip (they drop with the
                                jaw, so every jaw open splits the grin).
* demon_eyes   (child of head)  hidden by default; visible in 'poseido'.  Opaque plane over both 4 x 3 eyes: all black
                                (the demon opens them wide), white 2 x 2 pupils that carry the emissive 'eyes' pixels.
* bag          (child of chest) hidden by default; visible only in pose 'carry_bag' (either look).  The CARBON sack.
* tongs        (child of right_hand, + child tongs_arm)  VISIBLE by default; hidden in 'carry_bag' (he comes back from
                                the shop), 'grill_flip' (bare hands) and 'limp_fall' (dropped them: spawn a tongs
                                ItemDisplay falling from the right hand if wanted).
Possession (beat casa.jorge): the voluta reaches his mouth -> jaw 0.5 for 6 ticks (the wisp goes in), SNAP to look
'poseido' (texture + toggles + VARIANT_POSES), the bag toggle goes off (spawn a falling bag prop), blue fire on the
grill.  Steam (particles, not geometry): white puffs from the collar every 3-5 ticks while possessed, spawned at model
(+-4, -21, -2) = 0.12 block either side of centre, 1.4 blocks up, drifting up 0.03 / tick.

Rest pose (deg; every pose starts from it)
* right_arm = (-3, 0, 9), left_arm = (-3, 0, -9): hanging, angled out round the belly.
* right_forearm = left_forearm = (-12, 0, 0): a little forward.
* right_fingers = (0, 0, -80): curled round the tongs grip.  left_fingers = (0, 0, 14), left_index = (0, 0, 6).
* tongs = (76, 0, -2): tips down along the thigh.  tongs_arm = (0, 15, 0): the outer arm sprung open, a clear V.
* right_leg = (0, 6, 0), left_leg = (0, -6, 0): toes a little out (duck stance; the crotch gap stays open).
* right_brow = (0, 0, -6) and 1 texel higher: raised and arched; left_brow = (0, 0, -5): inner end a touch lower.
  Together with the smug half-lids that is the cocky "es la humedad, flaco" look.
* apron_skirt = (35, 0, 0): the upper panel drapes back from the belly's underside; apron_hem = (-35, 0, 0): the lower
  panel hangs plumb, its hem just in front of the bermudas.

Bones (pivots in model space)
* body (root, pivot hips (0, 3, 0)): ONLY the hips block (belt, tucked shirt tail, back pockets, crotch seam) and the
  legs.  Walk: dy = |sin(walk)| * 0.8 * s (the bob).  Nothing else (lean rule).
* chest (child of body, pivot at the belt (0, 2, 0)): shirt torso (stripes, sweat stains), yoke, collar (chest hair +
  gold chain), apron bib with the cow, the two collar points, the apron bow on his back.  Owns belly, neck, arms, bag.
  Idle breathing: xRot -0.01..0.01 on a 3.5 s sine.  Walk (a waddle): zRot = sin(walk) * 0.06 * s (rolls over each
  stance leg), yRot = sin(walk) * 0.05 * s.  Leans: idle -0.04, grill_flip +0.55, knife_conduct -0.1, carry_bag -0.05.
* belly (child of chest, pivot (0, -4, -6)): the ball (nine slabs) with the apron over it.  Breathing: dz 0 .. -0.4
  (pushes OUT) on a 3.5 s sine.  Walk jiggle: dy = sin(2 * walk - 0.6) * 0.5 * s (lags the step).  Salt hit / laugh:
  SNAP dz +0.8 then a damped wobble (dz 0.8 * cos(t * 1.6) * e^(-t / 6)) - it is a jelly.
* apron_skirt (child of belly, pivot at the belly's underside (0, 3, -10)): the 2-thick upper skirt panel.  Gravity
  (apron rule), flaps -0.25 on a salt hit, secondary +-0.08 following the belly with a 2-tick lag.
* apron_hem (child of apron_skirt, pivot (0, 9, -10)): the plumb lower panel with ASADO.  Walk: lifted by the thighs
  (apron rule).
* neck (child of chest, pivot (0, -21, 0)): the fat nape.  Takes 30 % of the head look (yaw / pitch).
* head (pivot (0, -24, 0)): skull, hair shell (bald spot on the crown, ragged clumped hem), tuft, nose, ears, the two
  cheek bevels.  70 % of the head look.  Talking: tiny nods (xRot +-0.05 per phrase).
* right_brow / left_brow (children of head, pivots (-4.5, -34, -8.5) / (4.5, -33, -8.5)): bushy brows.  Raised =
  dy -1 (never above -1.2: the furrows); worried = right (0, 0, 0.2), left (0, 0, -0.2); angry V = right (0, 0, 0.4,
  0, 1.4, 0), left (0, 0, -0.35, 0, 0.5, 0) (that is the possessed rest).
* moustache (child of head, pivot (0, -25.5, -9)): the combed walrus block, its strand fringe over the lip and the two
  drooping ends.  Bobs with speech: dy +0.3 on each syllable with the jaw; a "pfff" on "es la humedad": xRot -0.12
  for 3 ticks.
* jaw (child of head, pivot (0, -24, 1)): jowls (18 wide), the smiling lower lip, chin, the double chin cube.  Talk:
  xRot 0 .. 0.22 per syllable.  Shout ("ES LA HUMEDAD", "LE FALTA SAL"): 0.45.  Max 0.5 (the double chin enters the
  bib).  Possessed idle: chatter 0 .. 0.06 at 5 Hz (the grin's halves tick against each other).
* smile / smile_jaw / demon_eyes: toggles (above).  Never animate them; they ride head / jaw.
* right_arm / left_arm (shoulders (-11.5, -18, 0) / (11.5, -18, 0), children of chest): sleeves + upper arms.  Walk:
  xRot = +-sin(walk) * 0.35 * s (opposite to the legs).
* right_forearm / left_forearm (elbows): forearms (the left one wears the watch).  Pose values only.
* right_hand / left_hand (wrists (-17.9, -0.1, -2.7) / (17.9, -0.1, -2.7) at rest): palms (knuckles, palm crease,
  charred palms when possessed) + thumbs.
* right_fingers (child of right_hand): the four right fingers in one bone, a fist round the tongs grip at rest; zRot
  +1.15 opens them (grill_flip, limp_fall).
* left_index (child of left_hand): the pointing finger; left_fingers (child of left_hand): middle / ring / pinky.
  Fist = left_fingers zRot +1.25 (point).  Spread = left_fingers -0.35 + left_index -0.45 (knife_conduct).
* tongs (child of right_hand, pivot in the fist): hinge, the fixed inner arm (black ribbed grip, polished edge,
  scalloped spoon head).  The baton in knife_conduct.  tongs_arm (child of tongs, pivot at the hinge): the outer arm.
  CLACK: tongs_arm yRot -0.26 (closed) for 2 ticks, back over 2, twice ("clack clack"); idle every 5-9 s, and on
  every "jugoso o a punto?".
* right_leg / left_leg (hips (-5.75, 4, 0) / (5.75, 4, 0), children of body): 9-wide bermuda legs with an inseam.
  Walk: xRot = +-sin(walk) * 0.45 * s (short steps).  right_shin / left_shin (knees (+-5.75, 12, 0)): shins + insteps
  + toe rows + ojotas (one bone, no ankle).  Walk: xRot = max(0, sin(walk + 1.2)) * 0.4 * s.
* bag (child of chest, pivot (0, -13, -14)): toggle; static (it lies on the belly shelf, the hands hold its ends).

Poses (wrist = hand pivot in model space, for placing held props / checking contacts)
* idle: the "es la humedad, flaco" stance: chest -0.04 (belly out), head cocked (0.02, -0.1, 0.07); the LEFT hand lies
  flat on top of the belly, elbow out (left_arm (-0.453, 0.715, -0.951), left_forearm -2.16, left_hand (1.528, 0.291,
  0.358) palm down, fingers flat: left_fingers -0.15, left_index -0.1; wrist (11.4, -15.9, -7.1)); the tongs hand a
  little forward (right_forearm -0.3, wrist (-17.7, -1.3, -5)).  On top: breathing, a belly pat every 4-8 s (left_hand
  xRot +0.15 for 3 ticks, twice), the tongs clack, look-at.  Also the sofa pose (legs handled by any sitting code).
* point: "es la humedad" at a wall stain / at the player: left arm straight out (left_arm (-1.42, -0.05, 0.12),
  left_forearm +0.12, wrist (16, -17.1, -18.8)), index straight (left_index -0.1), fist (left_fingers +1.25); the
  tongs aimed forward too: right_arm (-0.255, 0.021, 0.253), right_forearm -0.894, tongs (0.1, 0, -0.15) (their tips
  point straight ahead), wrist (-19.5, -9.1, -11.5); brows raised (right dy -0.5, left dy -1), jaw 0.12, head cocked
  (zRot -0.08).  Talk on top (jaw / moustache).  Hold 30-40 ticks.
* carry_bag: beat casa.jorge, entering through the gate ("Llegue. No habia carbon en lo de Ruben..."): the sack lies
  across the top of the belly, low enough that his mouth shows; both hands on its ends, palms in, fingers forward:
  right_arm (-0.44, -0.207, 0.37), right_forearm -1.125, right_hand (0.67, 0.298, 0.237), left mirrored (left_arm
  (-0.44, 0.207, -0.37), left_forearm -1.125, left_hand (0.67, -0.298, -0.237)); wrists (+-15.7, -12.9, -12.9);
  fingers curled round the corners (right_fingers +0.6, left_fingers +0.4, left_index +0.5); chest leans back -0.05
  (counter-weight).  Toggles: bag on, tongs off.  Walk with this pose: legs only, NO arm swing, plus a sideways sway
  (chest zRot sin(walk) * 0.05).  When the wisp hits: release (blend back to rest in 3 ticks, bag toggle off, drop a
  sack prop).
* grill_flip: possessed at the grill ("Jugoso o a punto, pibe?").  Bent over the grill at the belt (chest 0.55, the
  legs stay planted; apron_skirt -0.55 keeps the skirt hanging), neck -0.18 + head (-0.32, 0.12, 0.26) look up at the
  player, jaw 0.2 (grin half open).  Elbows out, both hands well in front of and ~8 texels above the leaned belly,
  over the grill: RIGHT hand palm up, wrist flicked back mid-flip (right_arm (-1.085, -0.133, 0.869), right_forearm
  -1.235, right_hand (-0.247, 1.865, 0.623), fingers open (right_fingers +1.15), wrist (-10, -9.9, -24.2)); LEFT hand
  pressing a chorizo, palm down, claw (left_arm (-1.064, 0.239, -0.737), left_forearm -1.123, left_hand (0.99, 0.557,
  0.475), left_fingers +0.9, left_index +0.7, wrist (9.9, -8, -24.1)); no finger touches the belly.  Tongs hidden
  (bare hands).  Loop on top, 16-tick cycle: the FLIP = right_forearm -0.35 and right_hand xRot -0.6 over 3 ticks
  (spawn the chorizo hop / sparks there), back over 5; the left hand presses dy +0.6 on the off-beat; head zRot
  0.26 +- 0.1 on a slow 2 s sine; jaw chatter.  Place him so the grill top is at model y ~ -4 and starts ~22 texels
  in front of him (under his hands).
* knife_conduct: possessed conductor at the climax (the 6 knives rise and orbit): chest -0.1, neck -0.08, head
  (-0.28, 0.12, -0.16) thrown back, jaw 0.38 (grin split open), both arms up and out in a V: right_arm (-2.45, 0.35,
  -0.55), right_forearm -0.45, right_hand (-0.335, -1.251, 0.413) with the tongs as the baton pointing up and out
  (tongs (0.188, -0.035, -0.607), tongs_arm +0.12); left_arm (-2.7, -0.15, 0.68), left_forearm -0.35, left_hand
  (-0.309, 1.458, -0.484), fingers spread (left_fingers -0.35, left_index -0.45); brows up (right (0, 0, 0.1, 0, -0.6,
  0), left (0, 0, -0.1, 0, -0.6, 0)) on top of the possessed V.  Wrists ~(-22.9, -31.9, -1.1) and (23.9, -31.8, 1.4).
  Beat on top: 4/4 at 2 beats / s - right_arm xRot +0.25 on each downbeat (2 ticks down, 8 back), left_arm +-0.1 on
  the off-beats, body dy +0.3 on the downbeat; launch one knife per downbeat (6 beats).  The knives are ItemDisplays
  orbiting at radius 1.2 blocks at the height of his raised hands (model y ~ -32 = 1.75 blocks up), tips outward.
* limp_fall: three salt hits -> he falls backwards like a sack into the pelopincho.  END state: on his back, belly to
  the sky (the belly island), feet in the air: body (-1.571, 0, 0, 0, 9.245, -12.96) (the dy / dz put his head and
  back on y = 24 and centre the lying body on the entity origin), hips flexed so the legs rise (right_leg (-1.25, 0,
  0.3), left_leg (-1.25, 0, -0.3): splayed), knees bent (right_shin +0.6, left_shin +0.65), the head lolled to one
  side (neck +0.1, head (-0.15, 0.55, 0.1)), jaw 0.45 (KO), arms flopped wide (right_arm (0.06, 0, 1.3), left_arm
  (0.06, 0, -1.0), forearms -0.25 / -0.6, hands open: right_fingers +0.9, left_fingers +0.2), the apron skirt flopped
  over his lap (apron_skirt -0.5), brows slack (dy +0.5).  Tongs hidden.  Blend 0 -> 1 over 8 ticks with an ease-IN
  (w = t^2: stiff at first, then he drops), the legs lagging 2 ticks behind the body (they swing up as he lands), with
  a 2-tick SNAP of the last 10 % (the thud).  Java moves the entity into the pool; afloat: body dy +-0.3 on a 1.5 s
  sine, belly dz -0.4 (the island), the feet paddle (shins +-0.1 out of phase).  The salt hits before it: additive
  flinch for 6 ticks = chest xRot -0.15, head -0.3, jaw 0.5, belly SNAP wobble, apron_skirt -0.25.
"""


if __name__ == '__main__' and '--fk' in sys.argv:
    # pose checks: wrist / head positions per pose (model texels)
    _m = build(pose='__none__')
    for _name, _pose in POSES.items():
        _W = fk(_m.roots, _pose)
        print(_name, {k: tuple(round(float(v), 1) for v in _W[k][:3, 3]) for k in ('right_hand', 'left_hand', 'head')})
