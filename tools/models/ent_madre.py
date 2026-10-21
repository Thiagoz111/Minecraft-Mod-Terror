"""La Madre Remedios Iturbe -- the static apparition of the Mother Superior (DEAD LINE, case 'convento').

Authored at 2x texel density (model.scale = 0.5).  +Y down, ground y = 24, faces -Z, right_* on -X.  Centred on
x = 0, z = 0 (only the ledger and the pen arm project forward).  Height 2.3 blocks: veil roof y = -50 -> hem y = 24
(74 texels).  63 cubes, 23 bones, 256 x 192 texture.

Design
------
Silhouette: a rigid BLACK COLUMN.  Flat-topped starched veil (crown + chamfered roof, a brim over the white band),
veil wings flaring onto a rigid capelet that makes the shoulders dead square (33 wide), almost no waist, and four
stiff skirt panels that flare a hair to a hem lying ON the floor -- she never walks, she is simply there.  On the
black: a graphic WHITE FRAME -- the starched coif boxes the face in a hard rectangle (forehead band, cheek plates,
chin wrap) and pours into a big bib with rounded bottom corners carrying a black pectoral cross; below it the red
ledger.  Head ~ 1/3 of the height so the face reads at the end of a corridor.

Face (15 x 17 window, hand-placed pixel art projected onto the layered head cubes: skull, brow ridge, cheekbones,
nose, jaw, chin): waxy yellow-grey skin in broad lit planes (forehead, nose ridge, cheekbones, chin).  ROUND WIRE
GLASSES on their own plane, lenses OPAQUE WHITE and glowing (emissive 'eyes' layer) -- you never see her eyes.  The
strict-teacher "Aja." look: her right brow furrowed down onto the frame (that lens glows as a slanted, angry
half-moon), her left brow arched up (that lens glows round and wide).  A long aquiline nose, deep nasolabial folds,
hollow cheeks, thin bloodless lips pressed into ONE dark line pulled to one side with a hooked corner, a hard chin.
A hinge jaw lets her speak ("Aja.", "Usted.", "Silencio.").

Props: an open LEDGER (libro de actas, 19 x 15 x 3) in oxblood leather with brass corner plates, a gilt title plate,
a blind-stamped cross, a banded spine with gilt lines, red-sprinkled page edges, ruled pages full of names and red
demerit ticks, a loose turnable leaf with a fresh red entry and a red ribbon -- held at the waist by the left hand
clasping its outer board, tilted towards her.  A black lacquer FOUNTAIN PEN with gold bands and a gold nib wet with
red ink in the right fist, index finger along the barrel (pen and finger point together for 'point').  A ROSARY of
pewter beads from the belt to the knee with a silver crucifix.  A ring of iron keys at the left hip.

Palette: cold blue-black wool (pleats with a cold sheen on the ridges, chalk dust on the hem), cold blue-grey
shadowed starched linen, waxy ivory/olive skin, oxblood + brass as the only warm accents.  Everything renders
translucent (habit alpha 210; veil, linen, face and ledger denser so the white frame survives fog and the face does
not ghost through the back of the head); lenses opaque and full-bright.
"""
import math

import numpy as np

from mcmodel import Model, vnoise, hash3, face_light, pick, rot_matrix
from rig import Rig
from paint import hx, mix, pixelart

# ------------------------------------------------------------------ translucency
A_HABIT = 210
A_LINEN = 234
A_SKIN = 238
A_BOOK = 230
A_METAL = 222
A_VEIL = 246


def A(c, a):
    return (c[0], c[1], c[2], int(a))


# ------------------------------------------------------------------ palettes (hand-picked, hue shifted, cold)
HABIT = [hx(c) for c in ('#020307', '#06080e', '#0b0e16', '#11151f', '#181d29', '#202736', '#2a3245',
                         '#384157', '#4a556d')]
LINEN = [hx(c) for c in ('#1b2230', '#2f3849', '#475265', '#636f82', '#818ea0', '#a0abbb', '#bcc6d2',
                         '#d4dce5', '#e7ecf1', '#f5f7f9')]
SKIN = [hx(c) for c in ('#191a19', '#272926', '#383a35', '#4c4c43', '#636050', '#7c7762', '#969077',
                        '#afa98c', '#c6c0a2', '#d9d4b8')]
BROW = [hx('#1d1e21'), hx('#3a3c40'), hx('#66686a'), hx('#97968e')]
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
    'core': ('top', 'bottom'), 'chest': ('top', 'bottom', 'front'), 'sleeve_up': ('top',),
    'sleeve_lo': ('top', 'bottom'), 'veil_back': ('front', 'top'), 'scap': ('back', 'top'),
    'panel': ('top',), 'veil_side': ('top',), 'cape': (), 'veil_nape': ('front', 'top', 'bottom'),
}
VEILS = ('crown', 'roof', 'veil_side', 'veil_back', 'veil_nape')


def habit_mat(ctx):
    """Starched black wool: crisp organ pleats, lit square edges, seams, stitched hems, chalk dust at the floor."""
    t = tag(ctx)
    f = ctx.face
    if f in HIDDEN.get(t, ()):
        return None
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    k = cseed(ctx)
    a = A_VEIL if t in VEILS else A_HABIT
    side = f in ('front', 'back', 'west', 'east')
    v = 0.42 + face_light(ctx) * 1.15
    if t == 'core':
        return A(pick(HABIT, 0.12), a)
    if t == 'panel':
        if f == 'bottom':
            return A(pick(HABIT, 0.1), a)
        if side:
            big = max(ctx.w, ctx.h) > 4
            if big:
                v += pleat(around(ctx), k % 7, 5.0)
                v += 0.05 - ly / h * 0.12                   # a touch lighter at the waist, darker to the floor
                if f == 'back' and ctx.w > 4 and ctx.cube.size[2] == 1:
                    v -= 0.04
    elif t == 'scap':
        v += 0.07
        if f == 'front' and ctx.i in (0, ctx.w - 1):
            v += 0.12                                       # turned edges of the scapular
    elif t == 'chest' and side:
        v += pleat(around(ctx), k % 5, 6.0) * 0.6
    elif t == 'cape':
        if f == 'top':
            v += 0.02
            if ctx.i in (0, ctx.w - 1) or ctx.j in (0, ctx.h - 1):
                v += 0.12                                   # the square shoulder line catches the light
        elif side:
            u = around(ctx)
            v += pleat(u, k % 3, 8.0) * 0.45
            corner = min(abs(u - c) for c in (0, w, w + d, 2 * w + d, 2 * (w + d)))
            if corner < 1.2 and ly > h - 1.5:
                return None                                 # rounded bottom corners of the capelet
            if h - ly < 1.0:
                v += 0.1                                    # rolled edge
            elif 1.5 < h - ly < 2.5 and ctx.i % 2 == 0:
                v += 0.08                                   # stitched hem line
        elif f == 'bottom':
            v -= 0.1
    elif t in ('veil_back', 'veil_side', 'veil_nape') and side:
        v += pleat(around(ctx) + vnoise(ly * 0.08, k, 0, 3) * 2.0, k % 9, 6.0) * 0.8
        if t == 'veil_back':
            cx = abs(lx - w / 2) / (w / 2) if f in ('front', 'back') else 1.0
            if ly > h - 3.5 * cx ** 2:
                return None                                 # the veil hangs lower in the middle: rounded hem
            if h - 3.5 * cx ** 2 - ly < 1.0:
                v += 0.1
    elif t in ('sleeve_up', 'sleeve_lo', 'cuff') and side:
        v += pleat(around(ctx), k % 4, 7.0) * 0.5
        if t == 'sleeve_up' and ly > h - 3:
            v -= 0.05                                       # elbow creases
            if (ctx.i + int(ly)) % 4 == 0:
                v -= 0.08
    if t in ('crown', 'roof'):
        if f == 'top':
            v -= 0.02
            if t == 'roof':
                v += pleat(lx + abs(lz - d / 2) * 0.4, 3, 6.0) * 0.4
                if abs(lx - w / 2) < 0.6:
                    v -= 0.08                               # centre seam of the veil
            if ctx.j in (0, ctx.h - 1) or ctx.i in (0, ctx.w - 1):
                v += 0.12                                   # starched edge catches the light
        elif t == 'crown' and f == 'front' and ctx.j == ctx.h - 1:
            v += 0.1                                        # the brim edge over the white band
        elif t == 'crown' and f == 'bottom':
            v -= 0.12
    if t == 'cuff' and f == 'bottom':
        return A(HABIT[0], 255)                             # pitch black inside of the bell sleeve
    if edge(ctx) == 0 and side and min(ctx.w, ctx.h) > 2:
        v -= 0.06
    if side and t in ('panel', 'scap') and ly < 2.5:
        v -= 0.1 - ly * 0.03                                # occlusion under the belt
    if side and t not in ('core',):
        v += (vnoise(ctx.x * 0.18, ctx.y * 0.06, ctx.z * 0.18, 11) - 0.5) * 0.08   # soft sheen drifting along the folds
    c = pick(HABIT, v)
    if side and v > 0.6 and t not in ('core',):
        c = mix(c, hx('#5d6b8a'), 0.18)                     # cold sheen on the lit ridges
    if t == 'panel' and side and ctx.w > 4:
        dist = h - ly
        if dist < 1.0:
            c = mix(c, DUST, 0.42)                          # chalk dust of the corridors on the hem edge
            a = a - 40
        elif dist < 2.0:
            a = a - 20
        elif 2.5 <= dist < 3.5 and ctx.i % 2 == 0:
            c = mix(c, DUST, 0.3)                           # stitched hem line
        if f == 'front' and ctx.cube.size[2] == 1 and ctx.i % 9 == 4 and ctx.j % 3 != 2 and dist > 4:
            c = mix(c, HABIT[0], 0.55)                      # seams
    if t == 'cuff' and side and h - ly < 1.0:
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


def bib_shape(lx, ly, w, h):
    """Half width of the bib at depth ly: straight sides, generously rounded bottom corners."""
    return w / 2 - max(0.0, ly - (h - 3.5)) ** 1.7 * 1.0


def linen_mat(ctx):
    """Starched white linen: cold blue-grey shadows, ironed tucks, gathers at the neck, crisp shadow lines."""
    t = tag(ctx)
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    side = f in ('front', 'back', 'west', 'east')
    if t == 'bib' and f in ('back', 'bottom', 'west', 'east'):
        return None
    if t in ('coif_side', 'chinwrap') and f in ('top', 'bottom'):
        return None
    v = 0.74 + face_light(ctx) * 0.9
    if f in ('west', 'east'):
        v -= 0.12
    elif f == 'back':
        v -= 0.28
    if t == 'band':
        if f == 'front':
            v += (0.06, -0.02, 0.03, -0.07)[ctx.j % 4]       # ironed tucks across the forehead
            if ctx.j == ctx.h - 1:
                v -= 0.22                                   # rolls under onto the forehead
            v -= (abs(lx - w / 2) / (w / 2)) ** 2 * 0.12    # curves round the skull
        elif f == 'top':
            v -= 0.08
    elif t == 'coif_side':
        if f == 'front':
            inner = (ctx.i == ctx.w - 1) if ctx.x < 0 else (ctx.i == 0)
            outer = (ctx.i == 0) if ctx.x < 0 else (ctx.i == ctx.w - 1)
            v += -0.38 if inner else (-0.1 if outer else 0.06)
            v -= ly / h * 0.12
        elif side:
            v -= lz / max(1, d) * 0.22                      # seen in profile in front of the black veil
            if ctx.j % 5 == 2:
                v -= 0.05
    elif t == 'chinwrap':
        if f == 'front':
            v += (0.02, -0.07)[ctx.j % 2] - 0.06            # gathered under the chin
            if ctx.j == 0:
                v -= 0.3
            v -= (abs(lx - w / 2) / (w / 2)) ** 2 * 0.15
    elif t == 'bib':
        cx = abs(lx - w / 2)
        if f == 'front':
            hw = bib_shape(lx, ly, w, h)
            if cx > hw:
                return None                                 # rounded bottom corners
            if ly < 4.0:
                g = (1 - ly / 4.0)
                v += (0.05 if int(lx) % 2 == 0 else -0.08) * g   # gathers falling from the neck
                if ly < 1.0:
                    v -= 0.18                               # shadow of the chin wrap
            fold = h * 0.58
            if fold - 1.0 < ly < fold:
                v += 0.07                                   # starched bend over the chest: lit lip ...
            elif fold <= ly < fold + 1.0:
                v -= 0.07                                   # ... and its soft shadow
            if cx < 0.6 and ly > 4:
                v -= 0.05                                   # pressed centre crease
            v -= (cx / (w / 2)) ** 2 * 0.14                 # the sides turn away
            v -= ly / h * 0.06
            if cx > hw - 1.0:
                v -= 0.12                                   # turned edge
        elif f == 'top':
            v -= 0.06
            if int(lx) % 2 == 1:
                v -= 0.05
    elif t == 'undercuff':
        if f == 'bottom':
            return A(pick(LINEN, 0.2), A_LINEN)
        if side and ctx.j == ctx.h - 1:
            v -= 0.12
    c = pick(LINEN, v)
    if t == 'bib' and f == 'front':
        cx = abs(lx - w / 2)
        hw = bib_shape(lx, ly, w, h)
        if (hw - 2.0 < cx < hw - 1.0 and ly > 1.5) or (h - 2.0 < ly < h - 1.0 and cx < hw - 1.5):
            c = mix(c, LINEN[3], 0.45)                      # stitched hem a texel inside the edge
    if t == 'coif_side' and f == 'front' and ctx.j % 6 == 3 and 0 < ctx.i < ctx.w - 1:
        c = mix(c, LINEN[5], 0.3)                           # pins holding the starched plate
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
    if t in ('brow', 'cheek') and f != 'front':
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
    if t in ('fist', 'palm', 'fingers'):
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
# 15 columns (x -7.5..7.5, col c <-> x = c - 7), 17 rows (row r <-> y = -43.5 + r, y -44..-27).
# Skull rows r0..r12, jaw rows r13..r16.  Lenses (own plane) cover r4..r10.
GX0, GY0 = -7.5, -44
FACE = [
    # 012345678901234
    "556778898777655",   # r0  y-44 forehead, lit under the band
    "567777w87bhhhb5",   # r1  y-43 frown line over the right brow | the left brow arches up: "Aja."
    "bh6776w7h78876h",   # r2  y-42 right brow tip high at the temple | left brow head + tail
    "4hhhhhB65677654",   # r3  y-41 right brow slopes down to the nose | lit lid space under the arch
    "22333BB75333322",   # r4  y-40 right brow head presses down between the frames
    "222222685222222",   # r5  y-39 long nose (own cube, cols 6..8) between the opaque lenses
    "222222685222222",   # r6
    "222222695222222",   # r7  aquiline bump catches the light
    "222222685222222",   # r8
    "222222685222222",   # r9
    "333333695333333",   # r10 y-34 nose tip
    "46786k464k68764",   # r11 y-33 cheekbones lit; the deep folds start at the nose wings
    "3578k56765k8753",   # r12 y-32 folds cut down past the bloodless upper lip, lit cheek bulge outside them
    "3464kKKKKKKk643",   # r13 y-31 ONE pressed line, pulled to her left, the folds bracket it (jaw top row)
    "354kK777776k453",   # r14 y-30 right corner hooked down, lower lip catches the light, marionette lines
    "234k5444445k432",   # r15 y-29 under-lip shadow, jowl creases
    "234567898765432",   # r16 y-28 hard chin
]
assert all(len(r) == 15 for r in FACE), [len(r) for r in FACE]

FPAL = {str(i): A(SKIN[i], A_SKIN) for i in range(10)}
FPAL.update({
    'k': A(CREASE, A_SKIN), 'K': A(CREASE_D, A_SKIN), 'w': A(SKIN[4], A_SKIN),
    'B': A(BROW[0], A_SKIN), 'b': A(BROW[2], A_SKIN), 'h': A(BROW[1], A_SKIN),
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


# glasses: two 7x7 round wire rims + bridge, 15 x 7 (x -7.5..7.5, y -40..-33), on a plane in front of the nose.
# The furrowed right brow throws its shadow ('d', not emissive) across the top of the right lens, so that glow is a
# slanted, angry half-moon; under the raised left brow the lens glows round and wide -- the skeptical "Aja." look.
GLASSES = [
    "..fff.....fff..",
    ".fdddFfffFdWGf.",
    "fWddddF.FWWWWWf",
    "FWWWddF.FWWWWWF",
    "FWWWWWF.FWWWWWF",
    ".FWWVF...FWWVF.",
    "..FFF.....FFF..",
]
assert all(len(r) == 15 for r in GLASSES)
LENS_SHADE = (82, 94, 114, 255)
GPAL = {'F': FRAME, 'f': FRAME_HI, 'W': LENS, 'V': LENS_RIM, 'G': LENS_GLINT, 'd': LENS_SHADE}
GLOWPAL = {'W': (236, 246, 255, 255), 'V': (176, 210, 238, 255), 'G': (255, 255, 255, 255)}


def glasses_mat(ctx):
    """The glasses are a zero-thickness plane: only the GLASSES decal (and its 'eyes' glow) is painted."""
    return None


# ------------------------------------------------------------------ props
STAMP = [            # blind-stamped cross of the Hermanas de la Vigilia on the back board
    ".x.",
    "xxx",
    ".x.",
    ".x.",
]


def leather_mat(ctx):
    """Oxblood ledger leather: brass corner plates, blind-tooled frame, gilt title plate, banded spine, wear."""
    t = tag(ctx)
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    grain = (hash3(int(lx * 1.0), int(lz * 1.0), int(ly) + cseed(ctx), 5) - 0.5) * 0.07 + \
        (vnoise(lx * 0.35, lz * 0.35, cseed(ctx), 6) - 0.5) * 0.12
    v = 0.56 + face_light(ctx) * 0.8 + grain * 0.8
    if t == 'cover' and f == 'bottom':
        sp0, sp1 = w / 2 - 1.5, w / 2 + 1.5
        if sp0 <= lx < sp1:                                 # spine strip between the boards
            band = int(lz) % 4 == 1
            v = 0.26 + (0.2 if band else 0.0) + grain * 0.5
            c = pick(OX, v)
            if band and int(lx) == int(w / 2):
                c = BRASS[5]                                # gilt line on each raised band
            return A(c, A_BOOK)
        front = lx >= sp1
        bx = lx - sp1 if front else lx                      # board-local x (0 at the left edge of the board)
        bw = w - sp1 if front else sp0
        out_x = (bw - bx) if front else bx                  # distance from the board's OUTER edge
        in_x = bx if front else (bw - bx)                   # distance from the spine
        ez = min(lz, d - lz)
        # brass corner plates on the two outer corners of each board
        if out_x + ez < 3.2:
            k = out_x + ez
            cv = 0.75 if k < 1.0 else (0.9 if k > 2.2 else 0.55)
            if f == 'bottom' and abs(out_x - 0.8) < 0.5 and abs(ez - 0.8) < 0.5:
                cv = 0.95                                   # rivet
            return A(pick(BRASS, cv), A_BOOK)
        ex = min(out_x, in_x)
        if ex < 1.0 or ez < 1.0:
            v -= 0.16                                       # board edge
            if out_x + ez < 5.5 and hash3(int(lx), int(lz), 3, 7) > 0.5:
                v += 0.26                                   # leather rubbed pale next to the brass corners
        elif ex < 2.0 or ez < 2.0:
            v += 0.05                                       # the board rounds over: light catch
        v += (lz / d - 0.5) * -0.08                          # the far edge tilts into the light
        if front:
            cx, cz = bx - bw / 2, lz - 4.5
            if abs(cx) < 2.6 and abs(cz) < 1.6:
                if abs(cx) > 1.7 or abs(cz) > 0.7:
                    return A(BRASS[6] if (cz < -0.7 or cx < -1.7) else BRASS[3], A_BOOK)   # bevelled gilt plate
                return A(BRASS[5] if int(lx) % 2 == 0 else OX[1], A_BOOK)            # 'ACTAS' lettering
            if abs(cx) < 2.6 and abs(lz - 7.5) < 0.5:
                return A(BRASS[4], A_BOOK)                  # gilt rule under the plate
        else:
            sx, sz = int(bx - bw / 2 + 1.5), int(lz - d / 2 + 2)
            if 0 <= sz < len(STAMP) and 0 <= sx < 3 and STAMP[sz][sx] == 'x':
                v -= 0.16                                   # blind-stamped cross
        return A(pick(OX, v), A_BOOK)
    if t == 'spine':
        v = 0.32 + face_light(ctx) * 0.8 + grain * 0.5
        band = int(lz) % 4 == 1
        if f in ('bottom', 'west', 'east') and band:
            v += 0.22
        c = pick(OX, v)
        if f == 'bottom' and band and ctx.i in (1, 2):
            c = BRASS[5]
        return A(c, A_BOOK)
    if f in ('west', 'east', 'front', 'back'):
        v += 0.08                                           # board edges catch light
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
    v = 0.14 + face_light(ctx) * 0.6
    if ctx.face in ('front', 'west') and ctx.i == 0:
        v += 0.42                                           # lacquer gloss
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
    """The key ring is a zero-thickness plane: only its pixel-art decals (KEYS) are painted."""
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
    box('body', (-10.5, -8, -6.5), (21, 32, 13), name='core')
    box('body', (-11.5, -9.5, -7.5), (23, 3, 15), mat=belt_mat, name='belt')
    box('body', (12.2, -8, -4), (0, 12, 6), mat=keys_mat, name='keys',
        decals={'east': pixelart(KEYS, KPAL, anchor='topleft'), 'west': pixelart(KEYS, KPAL, anchor='topleft', flip=True)})
    # skirt: four stiff panels flaring a hair towards the floor (A-line column, hem ON the floor)
    B.bone('skirt_front', (0, -8, -6.5), parent='body', rot=(-2.5, 0, 0), mat=habit_mat)
    box('skirt_front', (-11.5, -8, -7), (23, 32, 1), name='panel')
    box('skirt_front', (-6, -6, -8), (12, 29, 1), name='scap')
    B.bone('skirt_back', (0, -8, 6.5), parent='body', rot=(3, 0, 0), mat=habit_mat)
    box('skirt_back', (-11.5, -8, 6), (23, 32, 1), name='panel')
    for side, sx in (('right', -1), ('left', 1)):
        sb = f'skirt_{side}'
        B.bone(sb, (10.5 * sx, -8, 0), parent='body', rot=(0, 0, -2.5 * sx), mat=habit_mat)
        box(sb, (10.5 * sx - (1 if sx < 0 else 0), -8, -7.5), (1, 32, 15), name='panel')

    # rosary: pewter beads from the belt to the knee, silver crucifix
    B.bone('rosary', (-7.5, -7, -9.5), parent='body', rot=(-3, 0, 2), mat=bead_mat)
    box('rosary', (-8.5, -7, -10.5), (2, 12, 2), name='beads')
    box('rosary', (-8.5, 5, -10), (2, 2, 1), mat=silver_mat, name='medal')
    box('rosary', (-8.5, 7, -10), (2, 7, 1), mat=silver_mat, name='crux')
    box('rosary', (-10.5, 8.5, -10), (6, 2, 1), mat=silver_mat, name='crux')

    # ---------------- chest: square block under a rigid capelet, big white bib, black pectoral cross
    B.bone('chest', (0, -8, 0), parent='body', mat=habit_mat)
    box('chest', (-9, -26, -6), (18, 18, 12), name='chest')
    box('chest', (-16.5, -26.5, -7.5), (33, 8, 15), name='cape')
    box('chest', (-9.5, -27, -8.5), (19, 16, 12), mat=linen_mat, name='bib')
    box('chest', (-1, -22, -9.3), (2, 8, 1), mat=ebony_mat, name='cross')
    box('chest', (-2.5, -20, -9.4), (5, 2, 1), mat=ebony_mat, name='cross')

    # back veil: long starched black panel from the crown down to the waist
    B.bone('veil', (0, -34, 9.5), parent='chest', rot=(3, 0, 0), mat=habit_mat)
    box('veil', (-12.5, -34, 9), (25, 29, 2), name='veil_back')

    # ---------------- head: roof -50, crown -49..-46, band, face window x -7.5..7.5 / y -44..-27
    B.bone('head', (0, -27, 0), parent='chest', mat=skin_mat)
    fbox('head', (-7.5, -47, -6), (15, 16, 12), name='skull')
    fbox('head', (-1.5, -39, -8), (3, 7, 2), name='nose')
    fbox('head', (-7.5, -42, -7), (15, 2, 1), name='brow')
    fbox('head', (-6.5, -33, -6.5), (3, 2, 1), name='cheek')
    fbox('head', (3.5, -33, -6.5), (3, 2, 1), name='cheek')
    box('head', (-10.5, -48, -7), (21, 4, 14), mat=linen_mat, name='band')
    box('head', (-10.5, -46, -7), (3, 21, 13), mat=linen_mat, name='coif_side')
    box('head', (7.5, -46, -7), (3, 21, 13), mat=linen_mat, name='coif_side')
    box('head', (-8.5, -27, -7), (17, 5, 12), mat=linen_mat, name='chinwrap')
    box('head', (-13.5, -49, -8.5), (27, 3, 19), mat=habit_mat, name='crown')
    box('head', (-12.5, -50, -7.5), (25, 1, 17), mat=habit_mat, name='roof')
    box('head', (-12.5, -47, 9.5), (25, 20, 2), mat=habit_mat, name='veil_nape')

    B.bone('glasses', (0, -38, -8.25), parent='head', mat=glasses_mat)
    box('glasses', (-7.5, -40, -8.25), (15, 7, 0), name='glasses',
        decals={'front': pixelart(GLASSES, GPAL, anchor='topleft'),
                'eyes:front': pixelart(GLASSES, GLOWPAL, anchor='topleft')})

    B.bone('jaw', (0, -31, 2), parent='head', mat=skin_mat)
    fbox('jaw', (-7.5, -31, -6), (15, 4, 9), name='jaw')
    fbox('jaw', (-3.5, -29, -6.75), (7, 2, 1), name='chin')

    for side, sx in (('right', -1), ('left', 1)):
        vb = f'veil_{side}'
        B.bone(vb, (10.5 * sx, -48, 2), parent='head', rot=(0, 0, -6 * sx), mat=habit_mat)
        box(vb, (10.5 * sx - (3 if sx < 0 else 0), -48, -5.5), (3, 26, 16), name='veil_side')

    # ---------------- arms (authored hanging, bent by the bone rotations); upper arms come out under the cape
    for side, sx in (('right', -1), ('left', 1)):
        arm, fa, hand = f'{side}_arm', f'{side}_forearm', f'{side}_hand'
        ax = 12.5 * sx
        B.bone(arm, (ax, -24, 0), parent='chest', rot=(-6 if sx < 0 else -3, 0, 2 * sx), mat=habit_mat)
        box(arm, (ax - 3.5, -25, -4), (7, 14, 8), name='sleeve_up')
        frot = (-55, -15, 0) if sx < 0 else (-64, 6, 0)
        B.bone(fa, (ax, -12, 0), parent=arm, rot=frot, mat=habit_mat)
        box(fa, (ax - 3, -13, -3.5), (6, 8, 7), name='sleeve_lo')
        box(fa, (ax - 4, -6, -5), (8, 7, 10), name='cuff')
        box(fa, (ax - 2.5, 0.5, -2.5), (5, 2, 5), mat=linen_mat, name='undercuff')
        B.bone(hand, (ax, 2, 0), parent=fa, rot=(0, 0, 0), mat=hand_mat)
        if sx < 0:
            box(hand, (ax - 2, 2, -2), (4, 5, 4), name='fist')
            box(hand, (ax + 1.2, 2.5, -2.6), (1, 3, 1), inflate=0.3, name='thumb')
            B.bone('right_index', (ax + 1, 6.5, -1.6), parent=hand, rot=(8, 0, 0), mat=hand_mat)
            box('right_index', (ax + 0.5, 6.5, -2.1), (1, 4, 1), inflate=0.28, name='finger')
            B.bone('pen', (ax + 0.2, 5, -2.6), parent=hand, rot=(-14, 0, -6), mat=pen_mat)
            box('pen', (ax - 0.3, -2, -3.1), (1, 9, 1), inflate=0.28, name='barrel')
            box('pen', (ax - 0.3, 7, -3.1), (1, 1, 1), inflate=0.2, name='section')
            box('pen', (ax - 0.3, 8, -3.1), (1, 2, 1), inflate=0.08, name='nib')
        else:
            box(hand, (ax - 2, 2, -1.5), (4, 5, 3), name='palm')
            box(hand, (ax - 3, 3, -1.5), (1, 4, 3), inflate=0.1, name='fingers')     # curled round the board
            box(hand, (ax - 2.3, 1.5, -2.6), (1, 3, 1), inflate=0.3, name='thumb')

    # ---------------- ledger on the left forearm, tilted towards her
    B.bone('book', (0.5, -5.5, -13.5), parent='left_forearm', world=True, wrot=(-50, 0, 3), mat=leather_mat)
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

    m = Model('madre', 256, 192, B.r.roots)
    m.scale = 0.5
    m.render_type = 'entityTranslucent'
    return m


POSES = {
    # 'Ajá.' -- head bowed over the ledger, pen nib down on the open page
    'write': {
        'chest': (0.07, 0, 0, 0, 0, 0),
        'head': (0.34, -0.14, 0.04, 0, 0, 0),
        'right_arm': (-0.3, 0.1, 0.0, 0, 0, 0),
        'right_forearm': (-0.15, -0.55, 0, 0, 0, 0),
        'right_hand': (0.45, 0, 0, 0, 0, 0),
        'pen': (0.25, 0, 0, 0, 0, 0),
        'book': (-0.08, 0, 0, 0, 0, 0),
    },
    # chin up, looking down her nose at you, the whole column leaning back from the hem
    'stare': {
        'body': (-0.035, 0, 0, 0, 0, 0),
        'chest': (-0.04, 0, 0, 0, 0, 0),
        'head': (-0.3, 0, 0, 0, 0, 0),
        'right_forearm': (0.1, 0, 0, 0, 0, 0),
    },
    # 'Usted.' -- right arm straight out at the player, index finger and pen together
    'point': {
        'chest': (0, -0.12, 0, 0, 0, 0),
        'head': (-0.12, -0.1, 0, 0, 0, 0),
        'jaw': (0.1, 0, 0, 0, 0, 0),
        'right_arm': (-1.32, 0.1, 0.0, 0, 0, 0),
        'right_forearm': (0.9, 0.26, 0, 0, 0, 0),
        'right_hand': (-0.05, 0, 0, 0, 0, 0),
        'pen': (0.24, 0, 0.1, 0, 0, 0),
        'right_index': (-0.14, 0, 0, 0, 0, 0),
    },
}

ANIM_NOTES = """
La Madre Remedios -- animation contract.  Angles in radians, ADDED to the rest pose; offsets (dx, dy, dz) in model
texels at 2x density (inside scale_root: 2 texels = 1 vanilla pixel).  t = ageInTicks.  Poses: write, stare, point.

CHARACTER: a static apparition.  She NEVER walks, bobs or floats: the hem stays on the floor and the column stays
rigid.  All motion is small, slow and deliberate (max ~0.05 rad/tick) -- EXCEPT that she is always already facing
you: while the player is not looking at her, snap body yRot to face the player in one tick (statue logic).

RENDER: entityTranslucent; alpha is baked into the texture (habit 210, veil 246, linen 234, skin 238, ledger 230,
metal 222, lenses 255).  Multiply a cold tint (0.86, 0.93, 1.0).  The 'eyes' layer (lens glow) renders
full-bright on top; pulse its alpha 0.85..1.0 with sin(t*0.05) and spike to 1.0 on every "Aja.".
APPEAR: global alpha 0 -> 1 over 8 ticks with a 2-tick flicker at 50 %; the skirt panels and veil wings flare out
(+0.06) and settle over 10 ticks as if a door had opened.  VANISH: alpha 1 -> 0 over 6 ticks, eyes layer last.

ROOT
* body -- root ON THE FLOOR (pivot 0, 24, 0): belt, black core of the column, ring of keys at the left hip.  Rest
  never moves.  Stare (-0.035 xRot): the whole rigid column tips back from the hem like a statue, looking down at
  you.  Statue snap: yRot jumps to face the player while unobserved.
* skirt_front / skirt_back / skirt_right / skirt_left -- the four stiff starched skirt panels (rest flare 2.5-3
  deg, the front one carries the scapular).  Static; draught flutter xRot/zRot += sin(t*0.03 + k)*0.01 (k = 0..3);
  appear/vanish gust +0.06 outward (front: -x, back: +x, right: +z, left: -z), ease back over 10 ticks.
* rosary -- pewter beads + silver crucifix from the belt to the knee.  Pendulum lagging the body:
  zRot = sin(t*0.06)*0.04; when the right arm snaps into 'point' give it an impulse zRot -0.15 decaying over 20
  ticks.  Clicks (sound) on the impulse.

TORSO
* chest -- square block under the rigid capelet, the big white bib and the black pectoral cross; carries arms,
  head and the long back veil.  Breathing xRot sin(t*0.05)*0.012 (barely).  Write +0.07 (leans over the ledger),
  stare -0.04, point yRot -0.12 (turns her shoulder into the gesture).
* veil -- the long starched back veil from the nape to the waist (child of chest).  Follows the chest; idle sway
  xRot sin(t*0.04)*0.015; when the head pitches down (write) add -0.25*headXRot so it does not cut into the
  nape piece; appear/vanish +0.08 then settle.

HEAD
* head -- FOCUS bone: skull + face cubes, white coif (band, cheek plates, chin wrap), black veil crown + roof + nape
  piece.  Tracks the player: yaw clamp +-0.6, pitch clamp -0.35..0.4, slow (0.04 rad/tick).  "Aja." beat: dip
  xRot +0.12 and back over 6 ticks while the pen marks the ledger.  Write (0.34, -0.14, 0.04) looks down into the
  ledger; stare (-0.3) chin up; point (-0.12, -0.1).  Roll call: between names turn yaw towards each empty desk.
* glasses -- the round wire glasses with the opaque, glowing lenses (emissive 'eyes' layer).  Static; signature
  gesture once per stare: pushed up the nose -- dy -0.6 for 8 ticks, back over 4 (sync the right hand lift).
* jaw -- lower lip + chin (hinge 0, -31, 2).  Rest closed (thin pressed line).  Voice-driven: xRot = 0.03 +
  amp*0.18 (max 0.2).  "Aja." = two short opens (0.12, then 0.08).  "Usted." = one 0.16 open.  "Silencio." =
  three; point pose holds 0.1.
* veil_right / veil_left -- the black veil wings falling over the coif onto the capelet (rest zRot -+6 deg
  outwards).  Follow the head; appear/vanish flare -+0.08 and settle; nothing in idle.

ARMS -- right_* is -X (viewer's left).
* right_arm -- pen arm, upper sleeve under the capelet (pivot at the shoulder).  Idle static.  Write (-0.3, 0.1)
  brings the pen to the page; point (-1.32, 0.1) raises it straight at the player.
* right_forearm -- forearm + bell cuff + white undercuff; rest bent -55 deg (pen poised over the ledger).
  Write (-0.15, -0.55) crosses to the book; point (+0.9, +0.26) straightens the elbow; stare +0.1.
* right_hand -- fist holding the pen.  Idle: taps the pen on the ledger every 80-140 ticks (xRot +0.2 for 3
  ticks).  Write +0.45 (wrist bends so the nib meets the page) + writing scribble (see pen).
* right_index -- index finger laid along the barrel.  Point -0.14 (straight, pointing with pen and finger).
  Running player ("En el colegio se camina."): finger wag zRot sin(t*0.9)*0.25 for 20 ticks.
* pen -- black lacquer fountain pen, gold bands, gold nib wet with red ink.  Write +0.25 and scribble:
  xRot += sin(t*1.2)*0.06, zRot += cos(t*1.2)*0.05 (2-3 strokes then a firm tick).  Point (+0.24, 0, 0.1) aligns
  the nib with the finger at the player.
* left_arm -- book arm, upper sleeve under the capelet.  Static.
* left_forearm -- forearm + cuff carrying the ledger at the waist (rest -64 deg).  Write -0.05 lifts the book a
  little towards her; roll call: same.
* left_hand -- hand clasped round the outer board of the ledger (palm, curled fingers, thumb on the pages).
  Static (it holds the book).

LEDGER
* book -- the open libro de actas (oxblood boards, brass corners, gilt title plate, banded spine, ruled pages
  full of names and red demerit ticks, red ribbon).  Rest tilted ~50 deg towards her.  Write -0.08 (tilts to the
  pen).  On "Aja." a tiny settle +0.03 after the tick.  Roll call: holds still.
* book_page -- a single loose leaf lying on the left-hand pages with a fresh red entry; pivot on the spine.  PAGE
  TURN: zRot 0 -> -3.03 over 10 ticks (ease in-out), then snap back to 0 out of sight (or on the next turn).  Turn
  one page per "Aja." and between roll-call names.

LAYERING
idle = (almost nothing) breathing + eyes pulse + occasional pen tap + statue snap.  'write' blends in over 6 ticks
and loops the pen scribble with head dips on every "Aja.".  'stare' over 10 ticks (glasses push).  'point' snaps
in over 3 ticks (fast, it is the scare) and holds while she says "Usted.", then eases out over 12.
"""
