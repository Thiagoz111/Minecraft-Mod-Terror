"""La Madre Remedios Iturbe -- the static apparition of the Mother Superior (DEAD LINE, case 'convento').

Authored at 2x texel density (model.scale = 0.5).  +Y down, ground y = 24, faces -Z, right_* on -X.  Centred on
x = 0, z = 0.  Height 2.3 blocks: veil crown y = -50 -> hem y = 24 (74 texels).

Design
------
Silhouette: a rigid BLACK COLUMN.  Flat-topped starched veil, square shoulders (32 wide, the arm caps sit flush with
the chest top), almost no waist, a long skirt that flares one texel to the hem and touches the floor -- she never
walks, she is simply there.  On the black: a graphic WHITE FRAME -- the starched coif boxes the face in a hard
rectangle (forehead band, cheek plates, chin wrap) and pours into a big square bib with rounded bottom corners
carrying a black pectoral cross.  Head ~ 1/3 of the height so the face reads at the end of a corridor.

Face (17 x 14 window, hand-placed pixel art projected onto the layered head cubes): waxy yellow-grey skin, heavy
grey V brows pressing down on two ROUND WIRE GLASSES whose lenses are OPAQUE WHITE and glow (emissive 'eyes'
layer) -- you never see her eyes.  A sharp 3-wide nose under the bridge, deep nasolabial folds running from the
nose wings past the mouth into marionette lines, thin lips pressed into one dark line with down-turned corners,
frown lines between the brows, crow's feet at the temples, eye bags under the frames.  A hinge jaw lets her
speak ("Ajá.", "Usted.", "Silencio.").

Props: an open LEDGER (libro de actas, 18 x 14 x 3) in oxblood leather with brass corners, tooled border, gilt title
plate and a banded spine, red-sprinkled page edges, ruled pages full of names and red demerit ticks, a turnable
page and a ribbon -- held on the left forearm at the waist, tilted towards her.  A black lacquer FOUNTAIN PEN with a
gold nib wet with red ink in the right hand, index finger along the barrel (it extends for 'point').  A ROSARY of
pewter beads from the belt to the knee with a silver crucifix.  A ring of iron keys at the left hip.

Palette: cold blue-black wool, cold blue-grey shadowed starched linen, waxy ivory/olive skin, oxblood + brass as
the only warm accents.  Everything renders translucent (alpha ~210, linen/face/book a little denser so the
white frame survives fog); the lenses are opaque and full-bright.
"""
import math

import numpy as np

from mcmodel import Model, vnoise, hash3, face_light, pick, rot_matrix
from rig import Rig
from paint import hx, mix, pixelart

# ------------------------------------------------------------------ translucency
A_HABIT = 210
A_LINEN = 226
A_SKIN = 228
A_BOOK = 230
A_METAL = 222


def A(c, a):
    return (c[0], c[1], c[2], int(a))


# ------------------------------------------------------------------ palettes (hand-picked, hue shifted, cold)
HABIT = [hx(c) for c in ('#020307', '#06080e', '#0b0e16', '#11151f', '#181d29', '#202736', '#2a3245',
                         '#384157', '#4a556d')]
LINEN = [hx(c) for c in ('#1b2230', '#2f3849', '#475265', '#636f82', '#818ea0', '#a0abbb', '#bcc6d2',
                         '#d4dce5', '#e7ecf1', '#f5f7f9')]
SKIN = [hx(c) for c in ('#191a19', '#272926', '#383a35', '#4c4c43', '#636050', '#7c7762', '#969077',
                        '#afa98c', '#c6c0a2', '#d9d4b8')]
BROW = [hx('#2f3133'), hx('#55575a'), hx('#83847f'), hx('#aeada3')]
CREASE = hx('#24231f')
CREASE_D = hx('#141412')
LIPL = hx('#20171a')
LIP = [hx('#5d4b4b'), hx('#705d5a'), hx('#857169')]
OX = [hx(c) for c in ('#140306', '#22060a', '#340a0f', '#4a1015', '#61171b', '#7a2022', '#932d2b', '#ab4239',
                      '#c25e4c')]
BRASS = [hx(c) for c in ('#241906', '#3f2d0c', '#614714', '#866521', '#ab8532', '#cba548', '#e3c46c',
                         '#f3e2a4')]
PAPER = [hx(c) for c in ('#4a463b', '#696452', '#8b846d', '#aaa388', '#c3bc9f', '#d7d0b4', '#e6e0c7',
                         '#f1edda')]
INK = hx('#151a2c')
INK2 = hx('#2b3350')
RED_INK = hx('#8c1a1c')
RED_INK2 = hx('#b8302b')
RULE = hx('#9fb0c4')
PEN = [hx(c) for c in ('#040407', '#0a0b10', '#14161d', '#20232d', '#343947', '#555c70', '#8790a6')]
SILVER = [hx(c) for c in ('#1c1f26', '#323742', '#4f5664', '#747c8a', '#9ca4b0', '#c3c9d2', '#e6eaef')]
IRON = [hx(c) for c in ('#0c0d10', '#191b20', '#2a2d34', '#41454e', '#5f646f', '#868c97')]
BELT = [hx(c) for c in ('#050507', '#0b0b0f', '#141419', '#1e1e25', '#2a2a33', '#3a3a46')]
FRAME = hx('#17181d')
FRAME_HI = hx('#6d7280')
LENS = (230, 240, 246, 255)
LENS_RIM = (178, 199, 216, 255)
LENS_GLINT = (255, 255, 255, 255)
DUST = hx('#5b5a63')
MOUTH = [hx('#070506'), hx('#140b0d'), hx('#24141a'), hx('#3a2228')]
TEETH = [hx('#5f5a49'), hx('#8b8468'), hx('#b4ad8c')]


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


def cseed(ctx):
    o, sz = ctx.cube.origin, ctx.cube.size
    return int(abs(o[0]) * 13.1 + abs(o[1]) * 7.3 + abs(o[2]) * 3.7 + sz[0] * 31 + sz[1] * 17 + sz[2] * 5) % 9973


def around(ctx):
    """Continuous horizontal coordinate wrapping around a cube (front -> east -> back -> west)."""
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


def pleat(u, seed, period=5.0):
    """Crisp organ-pipe pleats of starched wool: lit ridge, body, shadow, deep crease."""
    ph = ((u + seed * 0.37) % period) / period
    if ph < 0.18:
        return 0.13
    if ph < 0.55:
        return 0.04
    if ph < 0.78:
        return -0.04
    return -0.15


# ------------------------------------------------------------------ cloth
HIDDEN = {
    # tag -> faces never seen (cut out so nothing ghosts through the translucency)
    'skirt': ('top', 'bottom'), 'hem': ('top',), 'chest': ('top', 'bottom'), 'sleeve_up': ('bottom',),
    'sleeve_lo': ('top', 'bottom'), 'veil_back': ('front',), 'crown': (), 'scap': ('back',),
    'veil_side': (), 'belt': ('top', 'bottom'),
}


def habit_mat(ctx):
    """Starched black wool: crisp organ pleats, square lit shoulder edges, seams, stitched hem, chalk dust."""
    t = tag(ctx)
    f = ctx.face
    if f in HIDDEN.get(t, ()):
        return None
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    k = cseed(ctx)
    v = 0.42 + face_light(ctx) * 1.15
    if f in ('front', 'back', 'west', 'east'):
        if t in ('skirt', 'hem'):
            v += pleat(around(ctx), k % 7, 5.0)
            v += 0.06 - (ctx.y + 8) / 32 * 0.1           # a touch lighter at the waist, darker to the floor
        elif t in ('chest',):
            v += pleat(around(ctx), k % 5, 6.0) * 0.6
        elif t in ('veil_back', 'veil_side'):
            v += pleat(around(ctx) + vnoise(ly * 0.08, k, 0, 3) * 2.0, k % 9, 6.0) * 0.8
        elif t == 'scap':
            v += 0.03
            if f == 'front' and ctx.i in (0, ctx.w - 1):
                v += 0.12                                   # turned edges of the scapular
        elif t in ('sleeve_up', 'sleeve_lo', 'cuff'):
            v += pleat(around(ctx), k % 4, 7.0) * 0.5
            if t == 'sleeve_up' and ly > h - 3:
                v -= 0.05                                   # elbow creases
                if (ctx.i + int(ly)) % 4 == 0:
                    v -= 0.08
    if t == 'crown':
        if f == 'top':
            v -= 0.02
            if ctx.j in (0, ctx.h - 1) or ctx.i in (0, ctx.w - 1):
                v += 0.12                                   # starched edge catches the light
        if f == 'front':
            v += 0.08 if ctx.j == ctx.h - 1 else 0.0        # the brim edge over the white band
    if t in ('sleeve_up',) and f == 'top':
        v += 0.05
        if ctx.i in (0, ctx.w - 1) or ctx.j in (0, ctx.h - 1):
            v += 0.1                                        # square shoulder edge
    if t == 'cuff' and f == 'bottom':
        return A(HABIT[0], 255)                             # pitch black inside of the bell sleeve
    if edge(ctx) == 0 and f not in ('top', 'bottom'):
        v -= 0.06
    c = pick(HABIT, v)
    a = A_HABIT
    if t in ('skirt', 'hem') and f == 'front' and ctx.i % 11 == 3 and ctx.j % 3 != 2 and t == 'skirt':
        c = mix(c, HABIT[0], 0.6)                           # seam
    if t == 'hem' and f != 'bottom':
        dist = h - ly
        if dist < 1.0:
            c = mix(c, DUST, 0.45)                          # chalk dust of the corridors on the hem edge
        elif 2.0 <= dist < 3.0 and ctx.i % 2 == 0:
            c = mix(c, DUST, 0.35)                          # stitched hem line
        if dist < 2.0:
            a = A_HABIT - 30 + int(dist * 15)
    if t == 'hem' and f == 'bottom':
        return A(HABIT[0], 200)
    if t == 'cuff' and f in ('front', 'back', 'west', 'east') and h - ly < 1.0:
        c = mix(c, HABIT[6], 0.5)                           # rolled edge of the bell
    return A(c, a)


def belt_mat(ctx):
    v = 0.5 + face_light(ctx) * 1.1
    if ctx.j in (0, ctx.h - 1):
        v -= 0.2
    if ctx.face in ('front', 'back', 'west', 'east') and ctx.j == ctx.h // 2 and ctx.i % 3 == 1:
        v += 0.18                                           # tooled stitch line
    if ctx.face in ('top', 'bottom'):
        return None
    return A(pick(BELT, v), A_HABIT + 10)


def linen_mat(ctx):
    """Starched white linen: cold blue-grey shadows, ironed tucks, crisp shadow lines where it folds under."""
    t = tag(ctx)
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    if t == 'bib' and f in ('back', 'bottom', 'west', 'east'):
        return None
    if t == 'coif_side' and f in ('top', 'bottom'):
        return None
    v = 0.78 + face_light(ctx) * 0.9
    if f in ('west', 'east'):
        v -= 0.14
    elif f == 'back':
        v -= 0.28
    if t == 'band' and f == 'front':
        v += [0.06, -0.02, 0.04, -0.06, 0.02, -0.04][ctx.j % 6]   # ironed tucks across the forehead band
        if ctx.j == ctx.h - 1:
            v -= 0.18                                       # it rolls under onto the forehead
    if t == 'coif_side' and f == 'front':
        if (ctx.i == ctx.w - 1 and ctx.x < 0) or (ctx.i == 0 and ctx.x > 0):
            v -= 0.34                                       # shadow line along the face opening
        elif (ctx.i == 0 and ctx.x < 0) or (ctx.i == ctx.w - 1 and ctx.x > 0):
            v -= 0.12
        v -= ly / h * 0.08
    if t == 'chinwrap':
        if f == 'front':
            v += [0.03, -0.05][ctx.j % 2] - 0.04
            if ctx.j == 0:
                v -= 0.3                                    # deep shadow under the chin
            cx = abs(lx - w / 2) / (w / 2)
            v -= cx * 0.12
    if t == 'bib':
        if f == 'front':
            cx = abs(lx - w / 2)
            hw = w / 2 - max(0.0, ly - (h - 3.0)) ** 1.6 * 1.1
            if cx > hw:
                return None                                 # rounded bottom corners
            if ly < 2:
                v -= 0.2 - ly * 0.07                        # shadow of the chin wrap
            if cx > hw - 1.0:
                v -= 0.1                                    # the edge turns away
            if abs(lx - w / 2) < 0.6 and ly > 3:
                v -= 0.06                                   # pressed centre crease
            v -= ly / h * 0.08
        if f == 'top':
            v -= 0.05
    if t == 'undercuff':
        v -= 0.05
        if f == 'bottom':
            return A(pick(LINEN, 0.2), A_LINEN)
    c = pick(LINEN, v)
    if t == 'bib' and f == 'front':
        cx = abs(lx - w / 2)
        hw = w / 2 - max(0.0, ly - (h - 3.0)) ** 1.6 * 1.1
        if hw - 2.0 < cx < hw - 1.0 and ctx.j % 2 == 0 and ly > 1:
            c = mix(c, LINEN[4], 0.6)                       # hand-stitched border
    return A(c, A_LINEN)


# ------------------------------------------------------------------ flesh
def skin_mat(ctx):
    """Waxy yellow-grey skin.  The face is hand-placed pixel art (FACE decals); this paints the rest."""
    t = tag(ctx)
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    if t == 'skull' and f in ('top', 'west', 'east', 'back'):
        return None                                         # always under the coif / veil
    if t == 'skull' and f == 'bottom':
        cz = lz / max(1, d)
        if cz < 0.12:
            return A(pick(TEETH, 0.5), A_SKIN)              # upper teeth just behind the lip
        return A(pick(MOUTH, 0.3 - cz * 0.3), 255)
    if t == 'jaw':
        if f == 'top':
            cz = lz / max(1, d)
            if cz < 0.12:
                return A(pick(TEETH, 0.35), A_SKIN)
            if abs(lx - w / 2) < 3 and cz < 0.7:
                return A(pick(MOUTH, 0.7), 255)             # tongue
            return A(pick(MOUTH, 0.1), 255)
        if f in ('west', 'east', 'back', 'bottom'):
            return None
    if t == 'nose':
        if f == 'bottom':
            cx = lx - w / 2
            if abs(cx) > 0.4 and lz < d - 0.6:
                return A(CREASE_D, A_SKIN)                  # nostrils
            return A(pick(SKIN, 0.32), A_SKIN)
        if f in ('west', 'east'):
            return A(pick(SKIN, 0.48 - lz * 0.05), A_SKIN)
        if f == 'top':
            return A(pick(SKIN, 0.6), A_SKIN)
    if t == 'brow' and f != 'front':
        return A(pick(BROW, 0.3), A_SKIN) if f == 'top' else A(pick(SKIN, 0.3), A_SKIN)
    v = 0.66 + face_light(ctx) * 0.9
    if f in ('west', 'east'):
        v -= 0.12
    if f == 'back':
        v -= 0.25
    return A(pick(SKIN, v), A_SKIN)


def hand_mat(ctx):
    """Old waxy hands: lit knuckle ridge, finger splits, pale nails, cold veins and a few age spots."""
    t = tag(ctx)
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    v = 0.6 + face_light(ctx) * 1.0
    if edge(ctx) == 0 and min(ctx.w, ctx.h) > 2:
        v -= 0.07
    if t in ('fist', 'palm'):
        if f in ('front', 'back', 'west', 'east'):
            if ly < 1.0:
                v -= 0.15                                   # shadow under the cuff
            if t == 'fist' and ly > h - 2.0 and f in ('front', 'west', 'east'):
                v += 0.08 if int(around(ctx)) % 2 == 0 else -0.12   # curled finger segments
            if t == 'palm' and ly > h - 2.0 and f in ('front', 'back'):
                v += 0.06 if ctx.i % 2 == 0 else -0.14       # finger splits
        c = pick(SKIN, v)
        if f in ('west', 'east') and 1.5 < ly < h - 2 and hash3(ctx.i, ctx.j, cseed(ctx), 3) > 0.8:
            c = mix(c, hx('#5d6a78'), 0.45)                 # cold veins
        if hash3(ctx.i, ctx.j, cseed(ctx) + 7, 4) > 0.94:
            c = mix(c, hx('#6a5a3c'), 0.5)                  # age spots
        return A(c, A_SKIN)
    if t in ('finger', 'thumb'):
        if ly > h - 1.0 and f in ('front', 'west', 'east', 'back'):
            return A(pick(SKIN, 0.86), A_SKIN)              # pale nail
        if f == 'bottom':
            return A(pick(SKIN, 0.75), A_SKIN)
        if abs(ly - h * 0.5) < 0.5:
            v -= 0.12                                       # joint crease
    return A(pick(SKIN, v), A_SKIN)


# ------------------------------------------------------------------ the face mask
# 17 columns (x -8.5..8.5, col c <-> x = c - 8), 14 rows (row r <-> y = -42.5 + r, y -43..-29).
GX0, GY0 = -8.5, -43
FACE = [
    # 01234567890123456
    "34556676k6766554 3".replace(' ', ''),   # r0  y-43 forehead under the band, two frown lines
    "3hBBBb67k76bBBBh3",   # r1  y-42 heavy brows, outer ends high
    "23344BBBkBBB44332",   # r2  y-41 inner ends pressed down onto the frames (the V)
    "32222223632222223",   # r3  y-40 lens tops (hidden behind the opaque lenses)
    "F222222373222222F",   # r4  y-39 temple arms of the glasses + nose bridge
    "42222225852222224",   # r5  y-38 nose (own cube, cols 7..9)
    "w222222585222222w",   # r6  y-37 crow's feet
    "42222225852222224",   # r7
    "34222225952222243",   # r8  y-35 nose tip
    "355433k474k334553",   # r9  y-34 nose wings, folds start, eye bags under the frames
    "3564k8ll4llk84653",   # r10 y-33 cheeks lit above the folds; thin upper lip
    "3467kLLLLLLLk7643",   # r11 y-32 the pressed lip line (jaw top row)
    "346kL5mmmmm5Lk643",   # r12 y-31 corners turned down, marionette lines
    "2345k6788876k5432",   # r13 y-30 hard chin
]
assert all(len(r) == 17 for r in FACE), [len(r) for r in FACE]

FPAL = {str(i): A(SKIN[i], A_SKIN) for i in range(10)}
FPAL.update({
    'k': A(CREASE, A_SKIN), 'K': A(CREASE_D, A_SKIN), 'w': A(SKIN[3], A_SKIN),
    'B': A(BROW[1], A_SKIN), 'b': A(BROW[3], A_SKIN), 'h': A(BROW[2], A_SKIN),
    'L': A(LIPL, A_SKIN), 'l': A(LIP[0], A_SKIN), 'm': A(LIP[1], A_SKIN),
    'F': A(FRAME, 255),
})


def _slice(grid, x0, y0, w, h):
    rows = []
    for j in range(h):
        gy = int(math.floor(y0 + j + 0.5 - GY0))
        row = ''
        for i in range(w):
            gx = int(math.floor(x0 + i + 0.5 - GX0))
            row += grid[gy][gx] if 0 <= gy < len(grid) and 0 <= gx < len(grid[gy]) else '.'
        rows.append(row)
    return rows


def face_decals(x0, y0, w, h):
    return {'front': pixelart(_slice(FACE, x0, y0, w, h), FPAL, anchor='topleft')}


# glasses: two 7x7 round wire rims + keyhole bridge, 15 x 7 (x -7.5..7.5, y -40..-33)
GLASSES = [
    "..fff.....fff..",
    ".fGWWFFFFFGWWF.",
    "fGWWWWF.fGWWWWF",
    "FWWWWVF.FWWWWVF",
    "FWWWVVF.FWWWVVF",
    ".FVVVF...FVVVF.",
    "..FFF.....FFF..",
]
assert all(len(r) == 15 for r in GLASSES)
GPAL = {'F': FRAME, 'f': FRAME_HI, 'W': LENS, 'V': LENS_RIM, 'G': LENS_GLINT}
GLOWPAL = {'W': (236, 246, 255, 255), 'V': (170, 205, 235, 255), 'G': (255, 255, 255, 255)}


def glasses_mat(ctx):
    return None


# ------------------------------------------------------------------ props
def leather_mat(ctx):
    """Oxblood ledger leather: tooled double rule, brass corner plates, gilt title plate, banded spine."""
    t = tag(ctx)
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    v = 0.5 + face_light(ctx) * 0.9
    v += (vnoise(lx * 0.6, lz * 0.6, ly * 0.6 + cseed(ctx), 5) - 0.5) * 0.12
    if t == 'cover' and f == 'bottom':
        # outer covers seen from the front: two boards either side of the spine (x 8..11)
        sp0, sp1 = w / 2 - 1.5, w / 2 + 1.5
        if sp0 <= lx < sp1:
            v = 0.3 + (0.18 if int(lz) % 4 == 1 else 0.0)  # raised bands on the spine
            c = pick(OX, v)
            if int(lz) % 4 == 1 and int(lx) == int(w / 2):
                c = BRASS[5]                                # gilt lines on the bands
            return A(c, A_BOOK)
        bx = lx if lx < sp0 else lx - sp1                   # board-local coords
        bw = sp0
        ex = min(bx, bw - bx)
        ez = min(lz, d - lz)
        outer = (lx < sp0 and bx < 3.0) or (lx >= sp1 and bw - bx < 3.0)
        if ez < 3.0 and outer and (ex if not outer else min(ex, 3.0)) + ez < 4.2 and \
                ((lx < sp0 and bx < 3) or (lx >= sp1 and bw - bx < 3)):
            cv = 0.55 + (0.3 if (ex + ez) < 1.8 else 0.0) - (0.25 if (ex + ez) > 3.3 else 0.0)
            return A(pick(BRASS, cv + face_light(ctx) * 0.3), A_BOOK)   # brass corner plate
        if ex < 0.9 or ez < 0.9:
            v -= 0.12                                       # board edge
        if abs(ex - 2.0) < 0.5 or abs(ez - 2.0) < 0.5:
            if ex > 1.5 and ez > 1.5:
                v -= 0.2                                    # blind-tooled frame
        if 2.6 < ex < 3.4 and ez > 2.5 or 2.6 < ez < 3.4 and ex > 2.5:
            v += 0.12                                       # highlight under the rule
        if lx >= sp1:
            cx, cz = bx - bw / 2, lz - d * 0.38
            if abs(cx) < 2.5 and abs(cz) < 1.5:
                if abs(cx) > 1.6 or abs(cz) > 0.6:
                    return A(BRASS[5] if cz < 0 else BRASS[3], A_BOOK)  # gilt title plate rim
                return A(OX[1], A_BOOK)
        c = pick(OX, v)
        if hash3(int(lx * 3), int(lz * 3), 7, 9) > 0.93:
            c = mix(c, OX[7], 0.4)                          # scuffs
        return A(c, A_BOOK)
    if t == 'spine':
        v = 0.38 + face_light(ctx) * 0.8
        if f in ('bottom', 'west', 'east') and int(lz) % 4 == 1:
            v += 0.2
        c = pick(OX, v)
        if f == 'bottom' and int(lz) % 4 == 1 and ctx.i in (1, 2):
            c = BRASS[4]
        return A(c, A_BOOK)
    if edge(ctx) == 0:
        v -= 0.08
    return A(pick(OX, v), A_BOOK)


def page_mat(ctx):
    """Ledger pages: ruled lines, a red margin, names in blue-black ink and red demerit ticks; sprinkled edges."""
    t = tag(ctx)
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    if t == 'leaf':
        if f == 'bottom':
            return A(pick(PAPER, 0.6), A_BOOK)
        if f != 'top':
            return None
    if f == 'top':
        v = 0.8 + (vnoise(lx * 0.4, lz * 0.4, cseed(ctx), 2) - 0.5) * 0.1
        if t == 'pages_r' and lx > w - 1.0 or t == 'pages_l' and lx < 1.0:
            v -= 0.18                                       # gutter shadow
        c = pick(PAPER, v)
        row = int(lz)
        col = int(lx)
        if lz < 1.0:
            return A(pick(PAPER, v - 0.05), A_BOOK)
        side = 0 if t == 'pages_l' else 1
        margin = 1 if side == 0 else w - 2                  # red margin rule next to the gutter
        if row % 2 == 0:
            c = mix(c, RULE, 0.35)
        if col == margin:
            c = mix(c, RED_INK2, 0.55)
        if row % 2 == 1 and 2 <= row <= d - 2:
            n = (row // 2) * 3 + side * 17
            ln = 2 + int(hash3(n, 1, 0, 61) * 3)
            start = 3 if side == 0 else 1
            if start <= col < start + ln and hash3(col, row, n, 62) > 0.18:
                c = INK if hash3(col, row, n, 63) > 0.4 else INK2
            if hash3(n, 2, 0, 64) > 0.45 and col == (w - 2 if side == 0 else w - 3):
                c = RED_INK                                 # demerit tick
            if hash3(n, 3, 0, 65) > 0.75 and col == (w - 3 if side == 0 else w - 4):
                c = RED_INK
        if t == 'leaf':
            c = pick(PAPER, v + 0.04)
            if row % 2 == 0:
                c = mix(c, RULE, 0.3)
            if row % 2 == 1 and 2 <= row <= d - 3 and 1 <= col < 2 + int(hash3(row, 4, 0, 66) * 4):
                c = INK
            if row == d - 3 and col in (2, 3, 4):
                c = RED_INK2                                # fresh entry, still wet
        return A(c, A_BOOK)
    if f == 'bottom':
        return A(pick(PAPER, 0.3), A_BOOK)
    # page edges: thin stacked leaves, red-sprinkled like an old accounting ledger
    v = 0.66 + face_light(ctx) * 0.5 - (0.1 if ctx.j % 2 else 0.0)
    c = pick(PAPER, v)
    if hash3(ctx.i, ctx.j, cseed(ctx), 67) > 0.72:
        c = mix(c, RED_INK, 0.65)
    return A(c, A_BOOK)


def brass_mat(ctx):
    v = 0.55 + face_light(ctx) * 1.3
    if ctx.face in ('top', 'front', 'west') and (ctx.i == 0 or ctx.j == 0):
        v += 0.25
    if edge(ctx) == 0 and ctx.face in ('bottom', 'back', 'east'):
        v -= 0.2
    return A(pick(BRASS, v), A_BOOK)


def ribbon_mat(ctx):
    if ctx.face not in ('front', 'back', 'top', 'bottom'):
        return None
    lx, ly, lz = local(ctx)
    v = 0.35 + (0.15 if ctx.i == 0 else 0.0) - ly * 0.0
    return A(pick([hx('#1d0306'), hx('#3a070c'), hx('#5c0c14'), hx('#801520'), hx('#a12230')], v), A_BOOK)


def pen_mat(ctx):
    """Black lacquer fountain pen: cool specular streak, gold band and clip, gold nib wet with red ink."""
    t = tag(ctx)
    lx, ly, lz = local(ctx)
    h = ctx.cube.size[1]
    if t == 'nib':
        if ly > h - 0.8:
            return A(RED_INK2, 255)                         # red ink on the tip
        v = 0.6 + face_light(ctx) * 1.2 + (0.2 if ctx.i == 0 else 0)
        c = pick(BRASS, v)
        if ctx.face in ('front', 'back') and ly > 0.5:
            c = BRASS[1]                                    # slit
        return A(c, 255)
    v = 0.35 + face_light(ctx) * 1.0
    if ctx.face in ('front', 'west') and ctx.i == 0:
        v += 0.35                                           # lacquer gloss
    c = pick(PEN, v)
    if t == 'barrel' and (abs(ly - (h - 2.5)) < 0.5 or abs(ly - 2.5) < 0.5):
        c = pick(BRASS, 0.65 + face_light(ctx))             # gold bands
    if t == 'barrel' and ctx.face == 'front' and 0.5 < ly < 3.0:
        c = BRASS[6] if ctx.i == 0 else BRASS[4]            # clip
    return A(c, 255)


def bead_mat(ctx):
    """Rosary strand: pewter beads (2 tall) on a dark link (1 tall)."""
    lx, ly, lz = local(ctx)
    f = ctx.face
    if f in ('top', 'bottom'):
        return A(pick(SILVER, 0.4), A_METAL)
    ph = int(ly) % 3
    if ph == 2:
        cx = lx if f in ('front', 'back') else lz
        if abs(cx - 1.0) > 0.6:
            return None
        return A(IRON[2], A_METAL)                          # link
    v = 0.55 + face_light(ctx) * 1.2
    if ph == 0 and ctx.i == 0:
        v += 0.3                                            # specular dot
    if ph == 1:
        v -= 0.15
    return A(pick(SILVER, v), A_METAL)


def silver_mat(ctx):
    v = 0.58 + face_light(ctx) * 1.3
    if ctx.face in ('front', 'west', 'top') and (ctx.i == 0 or ctx.j == 0):
        v += 0.2
    elif edge(ctx) == 0:
        v -= 0.15
    return A(pick(SILVER, v), A_METAL)


def ebony_mat(ctx):
    """Pectoral cross: polished ebony with a pewter corpus line, reads black on the white bib."""
    v = 0.3 + face_light(ctx) * 1.0
    if ctx.face == 'front' and ctx.i == 0:
        v += 0.25
    c = pick(PEN, v)
    return A(c, 240)


def keys_mat(ctx):
    if ctx.face not in ('west', 'east'):
        return None
    return None


KEYS = [
    ".ooo..",
    "o...o.",
    "o...o.",
    ".oIo..",
    "..I.I.",
    "..I.I.",
    "..IIIi",
    "..I.I.",
    "..Ii.I",
    "..I..I",
    "..i..I",
    ".....i",
]
KPAL = {'o': A(IRON[4], A_METAL), 'I': A(IRON[3], A_METAL), 'i': A(IRON[5], A_METAL)}


# ------------------------------------------------------------------ builder
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


class Builder:
    """rig.Rig plus world-space placement for props held in rotated hands."""

    def __init__(self):
        self.r = Rig()
        self.W = {}

    def bone(self, name, pivot, parent=None, rot=(0, 0, 0), mat=None, world=False, wrot=None):
        """pivot: rig-absolute (unrotated) point, or a WORLD rest point when world=True.
        wrot: desired WORLD orientation (deg); converted to the local rotation."""
        if parent is None:
            Wp = np.eye(4)
            loc = np.array(pivot, float)
            absp = loc
        else:
            Wp = self.W[parent]
            pa = np.array(self.r.abs_pivot[parent])
            if world:
                loc = Wp[:3, :3].T @ (np.array(pivot, float) - Wp[:3, 3])
            else:
                loc = np.array(pivot, float) - pa
            absp = pa + loc
        if wrot is not None:
            rot = _euler(Wp[:3, :3].T @ _R(wrot))
        self.r.bone(name, tuple(float(v) for v in absp), parent=parent, rot=tuple(rot), mat=mat)
        T = np.eye(4)
        T[:3, 3] = loc
        Rm = np.eye(4)
        Rm[:3, :3] = _R(rot)
        self.W[name] = Wp @ T @ Rm
        return name

    def box(self, bone, frm, size, mat=None, name=None, inflate=0.0, decals=None, mirror=False):
        c = self.r.box(bone, frm, size, mat=mat, inflate=inflate, decals=decals, mirror=mirror)
        c.name = name
        return c

    def lbox(self, bone, off, size, **kw):
        """Box given relative to the bone pivot, in the bone's own axes."""
        p = self.r.abs_pivot[bone]
        return self.box(bone, (p[0] + off[0], p[1] + off[1], p[2] + off[2]), size, **kw)

    def world(self, bone):
        return self.W[bone][:3, 3]


DEFAULT_MAT = habit_mat
FOCUS = 'head'


def build():
    B = Builder()
    box, lbox = B.box, B.lbox

    def fbox(bone_, frm, size, mat=skin_mat, name=None):
        return box(bone_, frm, size, mat=mat, name=name, decals=face_decals(frm[0], frm[1], size[0], size[1]))

    # ---------------- body: root on the floor -- the rigid column tilts from the hem like a statue
    B.bone('body', (0, 24, 0), mat=habit_mat)
    box('body', (-12, 18, -8), (24, 6, 16), name='hem')
    box('body', (-11, -8, -7), (22, 26, 14), name='skirt')
    box('body', (-6, -6, -8.2), (12, 24, 1), name='scap')                       # scapular over the skirt
    box('body', (-6, -6, 7.2), (12, 24, 1), name='scap')
    box('body', (-11.5, -9.5, -7.5), (23, 3, 15), mat=belt_mat, name='belt')
    # ring of keys at the left hip (plane facing +X)
    box('body', (11.7, -8, -4), (0, 12, 6), mat=keys_mat, name='keys',
        decals={'east': pixelart(KEYS, KPAL, anchor='topleft'), 'west': pixelart(KEYS, KPAL, anchor='topleft', flip=True)})

    # rosary: pewter beads from the belt to the knee, silver crucifix
    B.bone('rosary', (-7.5, -7, -8.6), parent='body', rot=(-4, 0, 2), mat=bead_mat)
    box('rosary', (-8.5, -7, -9.6), (2, 12, 2), name='beads')
    box('rosary', (-8.5, 5, -9.1), (2, 2, 1), mat=silver_mat, name='medal')
    box('rosary', (-8.5, 7, -9.1), (2, 7, 1), mat=silver_mat, name='crux')
    box('rosary', (-10.5, 8.5, -9.1), (6, 2, 1), mat=silver_mat, name='crux')

    # ---------------- chest: square block, big white bib, black pectoral cross
    B.bone('chest', (0, -8, 0), parent='body', mat=habit_mat)
    box('chest', (-9, -27, -6), (18, 19, 12), name='chest')
    box('chest', (-6, -14, -6.6), (12, 6, 1), name='scap')
    box('chest', (-8.5, -27.5, -7), (17, 14, 12), mat=linen_mat, name='bib')
    box('chest', (-1, -23, -7.8), (2, 7, 1), mat=ebony_mat, name='cross')
    box('chest', (-2.5, -21.5, -7.9), (5, 2, 1), mat=ebony_mat, name='cross')

    # back veil: long starched black panel from the crown to the waist
    B.bone('veil', (0, -47, 8), parent='chest', mat=habit_mat)
    box('veil', (-12, -47, 7), (24, 41, 2), name='veil_back')

    # ---------------- head: veil crown -50, coif band, face window x -8.5..8.5 / y -43..-29
    B.bone('head', (0, -29, 0), parent='chest', mat=skin_mat)
    fbox('head', (-8.5, -46, -6), (17, 14, 12), name='skull')
    fbox('head', (-1.5, -38, -8), (3, 5, 2), name='nose')
    fbox('head', (-7.5, -42, -7), (15, 2, 1), name='brow')
    box('head', (-10.5, -48, -7), (21, 5, 14), mat=linen_mat, name='band')
    box('head', (-11.5, -46, -7), (3, 19, 13), mat=linen_mat, name='coif_side')
    box('head', (8.5, -46, -7), (3, 19, 13), mat=linen_mat, name='coif_side')
    box('head', (-9.5, -29, -7), (19, 4, 12), mat=linen_mat, name='chinwrap')
    box('head', (-12.5, -50, -8), (25, 3, 18), mat=habit_mat, name='crown')

    B.bone('glasses', (0, -39, -8.25), parent='head', mat=glasses_mat)
    box('glasses', (-7.5, -40, -8.25), (15, 7, 0), name='glasses',
        decals={'front': pixelart(GLASSES, GPAL, anchor='topleft'),
                'eyes:front': pixelart(GLASSES, GLOWPAL, anchor='topleft')})

    B.bone('jaw', (0, -32, 2), parent='head', mat=skin_mat)
    fbox('jaw', (-8.5, -32, -6), (17, 3, 10), name='jaw')

    for side, sx in (('right', -1), ('left', 1)):
        vb = f'veil_{side}'
        B.bone(vb, (12.5 * sx, -48, 0), parent='head', rot=(0, 0, 4 * sx), mat=habit_mat)
        box(vb, (11.5 * sx - (2 if sx < 0 else 0), -48, -7.5), (2, 24, 16), name='veil_side')

    # ---------------- arms (authored hanging, bent by the bone rotations)
    for side, sx in (('right', -1), ('left', 1)):
        arm, fa, hand = f'{side}_arm', f'{side}_forearm', f'{side}_hand'
        ax = 12.5 * sx
        B.bone(arm, (ax, -25, 0), parent='chest', rot=(-8 if sx < 0 else -4, 0, 3 * sx), mat=habit_mat)
        box(arm, (ax - 3.5, -27, -4), (7, 15, 8), name='sleeve_up')
        frot = (-52, -14, 0) if sx < 0 else (-72, 30, 0)
        B.bone(fa, (ax, -13, 0), parent=arm, rot=frot, mat=habit_mat)
        box(fa, (ax - 3, -14, -3.5), (6, 9, 7), name='sleeve_lo')
        box(fa, (ax - 4, -7, -5), (8, 7, 10), name='cuff')
        box(fa, (ax - 2.5, -0.5, -2.5), (5, 2, 5), mat=linen_mat, name='undercuff')
        B.bone(hand, (ax, 1, 0), parent=fa, rot=(0, 0, 0), mat=hand_mat)
        if sx < 0:
            box(hand, (ax - 2, 1, -2), (4, 5, 4), name='fist')
            box(hand, (ax + 1.2, 1.5, -2.6), (1, 3, 1), inflate=0.3, name='thumb')
            B.bone('right_index', (ax + 1, 5.5, -1.6), parent=hand, rot=(8, 0, 0), mat=hand_mat)
            box('right_index', (ax + 0.5, 5.5, -2.1), (1, 4, 1), inflate=0.28, name='finger')
            B.bone('pen', (ax + 0.2, 4, -2.6), parent=hand, rot=(-14, 0, -6), mat=pen_mat)
            box('pen', (ax - 0.3, -3, -3.1), (1, 9, 1), inflate=0.28, name='barrel')
            box('pen', (ax - 0.3, 6, -3.1), (1, 1, 1), inflate=0.2, name='section')
            box('pen', (ax - 0.3, 7, -3.1), (1, 2, 1), inflate=0.08, name='nib')
        else:
            box(hand, (ax - 2, 1, -1.5), (4, 5, 3), name='palm')
            box(hand, (ax - 2.3, 1.5, -2.6), (1, 3, 1), inflate=0.3, name='thumb')

    # ---------------- ledger on the left forearm, tilted towards her
    B.bone('book', (3.5, -7.5, -13.5), parent='left_forearm', world=True, wrot=(-50, -8, 0), mat=leather_mat)
    lbox('book', (-9.5, 0, -7.5), (19, 1, 15), name='cover')
    lbox('book', (-2, 1, -7.5), (4, 1, 15), name='spine')
    lbox('book', (-9, -2, -7), (8, 2, 14), mat=page_mat, name='pages_r')
    lbox('book', (1, -2, -7), (8, 2, 14), mat=page_mat, name='pages_l')
    lbox('book', (-1, -1, -7), (2, 1, 14), mat=page_mat, name='gutter')
    for cx in (-9.75, 7.75):
        for cz in (-7.75, 5.75):
            lbox('book', (cx, -0.25, cz), (2, 1, 2), mat=brass_mat, inflate=0.2, name='corner')
    lbox('book', (-0.5, -1.1, 6.5), (1, 0, 5), mat=ribbon_mat, name='ribbon')
    B.bone('book_page', B.r.abs_pivot['book'], parent='book', rot=(0, 0, -6), mat=page_mat)
    lbox('book_page', (0.6, -2.15, -6.8), (8, 0, 13), name='leaf')

    m = Model('madre', 256, 256, B.r.roots)
    m.scale = 0.5
    m.render_type = 'entityTranslucent'
    return m


POSES = {}

ANIM_NOTES = """
draft
"""
