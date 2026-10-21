"""La Madre Remedios Iturbe -- the static apparition of the Mother Superior (DEAD LINE, case 'colegio').

Authored at 2x texel density (model.scale = 0.5).  +Y down, ground y = 24, faces -Z, right_* on -X.  Centred on
x = 0, z = 0 (only the ledger and the pen arm project forward).  Height 2.3 blocks: veil roof y = -50 -> hem y = 24
(74 texels).  68 cubes, 24 bones, 256 x 192 texture.

Design
------
Silhouette: a rigid BLACK COLUMN.  Flat-topped starched veil (crown + chamfered roof, a brim over the white band),
veil wings falling onto a rigid capelet that makes the shoulders dead square (33 wide), almost no waist, four stiff
skirt panels that flare a hair to a hem lying ON the floor -- she never walks, she is simply there.  The long back
veil hangs from the crown and lies ON the capelet and the back (no daylight anywhere in profile).  On the black: a
graphic WHITE FRAME -- the starched coif boxes the face in a hard rectangle (forehead band, cheek plates) and pours
into a big flat bib carrying a black pectoral cross; below it the open red ledger.

Face (15 x 17 window, hand-placed pixel art projected onto layered cubes: skull, nose, raised left brow, cheekbones,
jowls, a narrow hinge jaw, chin).  Pale WAXY yellow-grey skin with a 3-4 value plan: big lit planes (forehead,
cheekbones, nose ridge, chin), one cool grey-green shadow value (under the brows, along the folds, under the lip),
dark creases only where the face folds.  ROUND STEEL SPECTACLES on their own plane -- two round 7 x 7 rims drawn as a
continuous dark ring, a 3-texel bridge over the nose, temples running back to the coif -- with OPAQUE WHITE
GLOWING lenses (emissive 'eyes' layer): you never see her eyes.  The strict-teacher "Aja." look is geometric: her
right brow is a separate furrowed block (`right_brow`) that cuts diagonally across the top of the right lens, so
that lens glows as an angry crescent, while the left brow is arched high over a round, wide-open lens.  Long
aquiline nose, deep nasolabial folds cut from the nose wings round the mouth, ONE thin dark line for the pressed
lips with the corners pulled down, a hard lit chin.  The hinge jaw sits between the jowls (only the mouth and chin
move when she speaks: "Aja.", "Usted.", "Silencio.").

Props: an open LEDGER (libro de actas, 21 x 17 x 3 open) in oxblood leather with brass corner caps, a gilt title
plate, a blind-stamped cross, banded spine, red-sprinkled page edges, ruled pages full of names and bold red
demerit checks, a loose leaf with a big red X and a red ribbon -- cradled on the left forearm at the waist and
tipped towards whoever she is looking at, so the pages read from 3-5 blocks.  A big cartoon FOUNTAIN PEN (black
lacquer, gold band and clip, gold nib with a red tip) in the right fist, a chunky index finger for 'Usted.'.  A
pewter ROSARY from the belt to the knee with a silver crucifix.  A ring of three iron keys at the left hip.

Palette: cold blue-black wool (crisp organ pleats with one lit ridge texel, a pale rim on every outer veil edge and
hem so the column survives fog), cold blue-grey shadowed starched linen, waxy ivory skin, oxblood + brass + red ink
as the only warm accents.  Everything renders translucent (habit alpha 210; veil, linen, ledger denser so the white
frame survives fog; skin 252 so the face never darkens through the hollow head); lenses opaque and full-bright.
"""
import math

import numpy as np

from mcmodel import Model, hash3, face_light, pick, rot_matrix
from rig import Rig
from paint import hx, mix, pixelart

# ------------------------------------------------------------------ translucency
A_HABIT = 210
A_LINEN = 238
A_SKIN = 252
A_BOOK = 238
A_METAL = 232
A_VEIL = 246


def A(c, a):
    return (c[0], c[1], c[2], int(a))


# ------------------------------------------------------------------ palettes (hand-picked, hue shifted, cold)
HABIT = [hx(c) for c in ('#020307', '#06080e', '#0b0e16', '#11151f', '#181d29', '#202736', '#2a3245',
                         '#384157', '#4a556d')]
LINEN = [hx(c) for c in ('#1b2230', '#2f3849', '#475265', '#636f82', '#818ea0', '#a0abbb', '#bcc6d2',
                         '#d4dce5', '#e7ecf1', '#f5f7f9')]
# waxy skin: cool grey-green shadows -> sickly ivory lights
SKIN = [hx(c) for c in ('#2b2d28', '#3a3d36', '#4a4c44', '#5b5e54', '#6e7064', '#8f9080', '#aeab95',
                        '#c6c2a4', '#d9d5b9', '#e9e6d0')]
BROW = [hx('#26272b'), hx('#45474c'), hx('#6c6e70'), hx('#9a9890')]
CREASE = hx('#3d3e37')
MOUTH_LINE = hx('#1e1a1b')
OX = [hx(c) for c in ('#140306', '#22060a', '#340a0f', '#4a1015', '#61171b', '#7a2022', '#932d2b', '#ab4239',
                      '#c25e4c')]
BRASS = [hx(c) for c in ('#241906', '#3f2d0c', '#614714', '#866521', '#ab8532', '#cba548', '#e3c46c',
                         '#f3e2a4')]
PAPER = [hx(c) for c in ('#5a5546', '#7b755f', '#9c957b', '#b9b295', '#d0c9ab', '#e1dbc0', '#eee9d4',
                         '#f8f5e6')]
INK = hx('#131729')
INK2 = hx('#28304c')
RED_INK = hx('#a01c1e')
RED_INK2 = hx('#c8302a')
RULE = hx('#9fb0c4')
PEN = [hx(c) for c in ('#040407', '#0a0b10', '#14161d', '#20232d', '#343947', '#555c70', '#8790a6')]
SILVER = [hx(c) for c in ('#1c1f26', '#323742', '#4f5664', '#747c8a', '#9ca4b0', '#c3c9d2', '#e6eaef')]
IRON = [hx(c) for c in ('#0c0d10', '#191b20', '#2a2d34', '#41454e', '#5f646f', '#868c97', '#b3b8c1')]
BELT = [hx(c) for c in ('#050507', '#0b0b0f', '#141419', '#1e1e25', '#2a2a33', '#3a3a46')]
FRAME = hx('#121318')
FRAME_HI = hx('#9aa3b4')
LENS = hx('#f0f8ff')
LENS_RIM = hx('#c4daf0')
DUST = hx('#5b5a63')
MOUTH = [hx('#070506'), hx('#140b0d'), hx('#24141a'), hx('#3a2228')]
TEETH = [hx('#6a6450'), hx('#958d70'), hx('#bab194')]


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


def pleat(u, seed, period=5):
    """Crisp organ-pipe pleats of starched wool, one texel per phase: ONE lit ridge texel, body, shadow, crease."""
    ph = int(math.floor(u + seed)) % period
    if ph == 0:
        return 0.16                                         # the lit ridge
    if ph == period - 1:
        return -0.15                                        # the deep crease
    if ph == period - 2:
        return -0.05
    return 0.03


# ------------------------------------------------------------------ cloth
HIDDEN = {
    # tag -> faces never seen (cut out so nothing ghosts through the translucency)
    'core': ('top', 'bottom'), 'chest': ('top', 'bottom', 'front'), 'sleeve_up': ('top',),
    'sleeve_lo': ('top', 'bottom'), 'veil_back': ('front',), 'scap': ('back', 'top'),
    'panel': ('top',), 'veil_side': ('top',), 'cape': (), 'veil_nape': ('front', 'top', 'bottom'),
}
VEILS = ('crown', 'roof', 'veil_side', 'veil_back', 'veil_nape')


def habit_mat(ctx):
    """Starched black wool: crisp organ pleats, lit square edges, pale rims on the veil and hem, chalk dust."""
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
    rim = False                                             # pale outer edge that keeps the silhouette in fog
    if t == 'core':
        return A(pick(HABIT, 0.12), a)
    if t == 'panel':
        if f == 'bottom':
            return A(pick(HABIT, 0.1), a)
        if side:
            if max(ctx.w, ctx.h) > 4:
                v += pleat(around(ctx), k % 7, 5)
                v += 0.05 - ly / h * 0.12                   # a touch lighter at the waist, darker to the floor
            if ctx.w <= 1 or ctx.h <= 1:
                v += 0.08
    elif t == 'scap':
        v += 0.07
        if f == 'front' and ctx.i in (0, ctx.w - 1):
            v += 0.12                                       # turned edges of the scapular
    elif t == 'chest' and side:
        v += pleat(around(ctx), k % 5, 6) * 0.6
    elif t == 'cape':
        if f == 'top':
            v += 0.02
            if ctx.i in (0, ctx.w - 1) or ctx.j in (0, ctx.h - 1):
                v += 0.14                                   # the square shoulder line catches the light
        elif side:
            u = around(ctx)
            v += pleat(u, k % 3, 8) * 0.45
            corner = min(abs(u - c) for c in (0, w, w + d, 2 * w + d, 2 * (w + d)))
            if corner < 1.2 and ly > h - 1.5 and f in ('front', 'back'):
                return None                                 # rounded bottom corners of the capelet
            if h - ly < 1.0:
                rim = True                                  # rolled edge
            elif 1.5 < h - ly < 2.5 and ctx.i % 3 != 2:
                v += 0.08                                   # stitched hem line
        elif f == 'bottom':
            v -= 0.1
    elif t in ('veil_back', 'veil_side', 'veil_nape') and side:
        v += pleat(around(ctx), k % 9, 6) * 0.8
        if t == 'veil_back':
            cx = abs(lx - w / 2) / (w / 2) if f in ('front', 'back') else 1.0
            hem = h - 3.5 * cx ** 2
            if ly > hem:
                return None                                 # the veil hangs lower in the middle: rounded hem
            if hem - ly < 1.0:
                rim = True
            if f == 'back' and abs(lx - w / 2) < 0.6 and ly < hem - 2:
                v -= 0.1                                    # centre seam
            if f == 'back' and 1.0 < ly < 2.0:
                v -= 0.08                                   # shadow under the nape
            if f in ('west', 'east') or (f == 'back' and ctx.i in (0, ctx.w - 1)):
                rim = True
        elif t == 'veil_side':
            if f in ('front', 'back') and (ctx.i in (0, ctx.w - 1)):
                rim = True
            if h - ly < 1.0:
                rim = True                                  # lower edge lying on the capelet
            outer = (f == 'west' and ctx.x < 0) or (f == 'east' and ctx.x > 0)
            if outer and (ctx.i in (0, ctx.w - 1)):
                rim = True
        elif t == 'veil_nape':
            if f == 'back' and ctx.i in (0, ctx.w - 1):
                rim = True
    elif t in ('sleeve_up', 'sleeve_lo', 'cuff') and side:
        v += pleat(around(ctx), k % 4, 7) * 0.5
        if t == 'sleeve_up' and ly > h - 3:
            v -= 0.05                                       # elbow creases
            if (ctx.i + int(ly)) % 4 == 0:
                v -= 0.08
    if t in ('crown', 'roof'):
        if f == 'top':
            v -= 0.02
            if t == 'roof':
                v += pleat(lx, 3, 6) * 0.3                  # starched folds running front to back
                if abs(lx - w / 2) < 0.6:
                    v -= 0.08                               # centre seam of the veil
            if ctx.j in (0, ctx.h - 1) or ctx.i in (0, ctx.w - 1):
                v += 0.14                                   # starched edge catches the light
        elif t == 'crown' and f == 'front' and ctx.j == ctx.h - 1:
            v += 0.12                                       # the brim edge over the white band
        elif t == 'crown' and f == 'bottom':
            v -= 0.12
        elif side and ctx.j == 0:
            rim = True
    if t == 'cuff' and f == 'bottom':
        return A(HABIT[0], 255)                             # pitch black inside of the bell sleeve
    if edge(ctx) == 0 and side and min(ctx.w, ctx.h) > 2 and not rim:
        v -= 0.06
    if side and t in ('panel', 'scap') and ly < 2.5:
        v -= 0.1 - ly * 0.03                                # occlusion under the belt
    if rim:
        v = max(v, 0.62) + 0.2
    c = pick(HABIT, v)
    if side and v > 0.6:
        c = mix(c, hx('#5d6b8a'), 0.2)                      # cold sheen on the lit ridges and rims
    if t == 'panel' and side and ctx.w > 4:
        dist = h - ly
        if dist < 1.0:
            c = mix(c, DUST, 0.5)                           # chalk dust of the corridors on the hem edge
            a = a - 30
        elif dist < 2.0:
            a = a - 15
        elif 2.5 <= dist < 3.5 and ctx.i % 3 != 2:
            c = mix(c, DUST, 0.28)                          # stitched hem line
        if f == 'front' and ctx.cube.size[2] == 1 and ctx.i % 9 == 4 and dist > 4:
            c = mix(c, HABIT[0], 0.5)                       # seams
    if t == 'cuff' and side and h - ly < 1.0:
        c = mix(c, HABIT[7], 0.55)                          # rolled edge of the bell
    return A(c, a)


def belt_mat(ctx):
    if ctx.face in ('top', 'bottom'):
        return None
    v = 0.5 + face_light(ctx) * 1.1
    if ctx.j in (0, ctx.h - 1):
        v -= 0.2
    if ctx.j == ctx.h // 2 and ctx.i % 3 == 1:
        v += 0.18                                           # tooled stitch line
    return A(pick(BELT, v), A_HABIT + 12)


def bib_shape(lx, ly, w, h):
    """Half width of the bib at depth ly: straight sides, generously rounded bottom corners."""
    return w / 2 - max(0.0, ly - (h - 3.5)) ** 1.7 * 1.0


def linen_mat(ctx):
    """Starched white linen: flat bright fields, cold blue-grey shadows, a few crisp pressed lines."""
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
            v += 0.06 if ctx.j % 2 == 0 else -0.02         # two ironed tucks across the forehead
            if ctx.j == ctx.h - 1:
                v -= 0.2                                    # rolls under onto the forehead
            v -= (abs(lx - w / 2) / (w / 2)) ** 2 * 0.1     # curves round the skull
        elif f == 'top':
            v -= 0.08
    elif t == 'coif_side':
        if f == 'front':
            inner = (ctx.i == ctx.w - 1) if ctx.x < 0 else (ctx.i == 0)
            outer = (ctx.i == 0) if ctx.x < 0 else (ctx.i == ctx.w - 1)
            v += -0.38 if inner else (-0.1 if outer else 0.07)
            v -= ly / h * 0.1
        elif side:
            v -= lz / max(1, d) * 0.2                       # seen in profile in front of the black veil
    elif t == 'chinwrap':
        if f == 'front':
            v -= 0.06
            if ctx.j == 0:
                v -= 0.3
    elif t == 'bib':
        cx = abs(lx - w / 2)
        if f == 'front':
            hw = bib_shape(lx, ly, w, h)
            if cx > hw:
                return None                                 # rounded bottom corners
            fold = int(h * 0.56)
            v = 0.93 if ly < fold else 0.86                 # flat starched field, a step darker under the fold
            if ly < 1.0:
                v = 0.6                                     # shadow line under the chin
            elif ly < 4.0 and int(cx) in (2, 5) and int(lx) != int(w / 2):
                v = 0.74 if ly < 3.0 else 0.8               # four pressed pleats falling from the neck
            if fold <= ly < fold + 1.0:
                v = 0.76                                    # one soft fold across the chest
            if cx > hw - 1.0:
                v = 0.66                                    # turned edge
            elif (hw - 2.0 < cx < hw - 1.0 and ly > 1.5) or (h - 2.0 < ly < h - 1.0 and cx < hw - 1.5):
                if int(lx + ly) % 3 != 2:
                    v = min(v, 0.78)                        # stitched hem a texel inside the edge
        elif f == 'top':
            v = 0.8
    elif t == 'undercuff':
        if f == 'bottom':
            return A(pick(LINEN, 0.2), A_LINEN)
        if side and ctx.j == ctx.h - 1:
            v -= 0.12
    return A(pick(LINEN, v), A_LINEN)


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
        if cz < 0.1:
            return A(pick(TEETH, 0.5), A_SKIN)              # upper teeth just behind the lip
        return A(pick(MOUTH, 0.3 - cz * 0.3), 255)
    if t == 'jaw':
        if f == 'top':
            cz = lz / max(1, d)
            if cz < 0.12:
                return A(pick(TEETH, 0.35), A_SKIN)
            if abs(lx - w / 2) < 2.5 and cz < 0.7:
                return A(pick(MOUTH, 0.7), 255)             # tongue
            return A(pick(MOUTH, 0.1), 255)
        if f in ('west', 'east', 'back', 'bottom'):
            return None
    if t == 'jowl':
        inner = (f == 'east' and ctx.x < 0) or (f == 'west' and ctx.x > 0)
        if inner:
            return A(MOUTH[1], 255)                         # inside of the cheek, seen when the jaw drops
        if f != 'front':
            return None
    if t == 'cheek':
        if f == 'bottom':
            return A(pick(SKIN, 0.35), A_SKIN)
        if f == 'top':
            return A(pick(SKIN, 0.75), A_SKIN)
        inner = (f == 'east' and ctx.x < 0) or (f == 'west' and ctx.x > 0)
        if inner:
            return A(pick(SKIN, 0.45), A_SKIN)
        if f != 'front':
            return None
    if t == 'nose':
        if f == 'back':
            return None
        if f == 'bottom':
            cx = lx - w / 2
            if abs(cx) > 0.4 and lz < d - 0.6:
                return A(CREASE, A_SKIN)                    # nostrils
            return A(pick(SKIN, 0.42), A_SKIN)
        if f in ('west', 'east'):
            lit = (f == 'west')
            return A(pick(SKIN, (0.62 if lit else 0.5) - lz * 0.05), A_SKIN)
        if f == 'top':
            return A(pick(SKIN, 0.72), A_SKIN)
    if t == 'brow_l':
        if f in ('back', 'east'):
            return None                                     # the outer end tucks under the coif
        if f == 'top':
            return A(pick(SKIN, 0.82), A_SKIN)
        if f == 'bottom':
            return A(pick(SKIN, 0.35), A_SKIN)
        if f in ('west', 'east'):
            return A(pick(SKIN, 0.55), A_SKIN)
    if t == 'brow_r':                                       # the furrowed brow block over the right lens
        if f == 'back':
            return None
        if f == 'front':
            if ctx.j == 0:
                return A(BROW[2] if ctx.i < 2 else BROW[1], A_SKIN)     # grey hairs, the tail catches light
            return A(BROW[0], A_SKIN)
        if f == 'top':
            return A(BROW[2] if lz < 1 else (BROW[1] if lz < 2 else pick(SKIN, 0.72)), A_SKIN)   # bushy brow
        if f == 'bottom':
            return A(pick(SKIN, 0.22), A_SKIN)
        return A(pick(SKIN, 0.5), A_SKIN)
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
    v = 0.66 + face_light(ctx) * 1.0
    if edge(ctx) == 0 and min(ctx.w, ctx.h) > 2:
        v -= 0.07
    if t in ('fist', 'palm', 'fingers'):
        if f in ('front', 'back', 'west', 'east'):
            if ly < 1.0:
                v -= 0.15                                   # shadow under the cuff
            if t == 'fist' and ly > h - 2.0 and f in ('front', 'west', 'east'):
                v += 0.06 if int(around(ctx)) % 2 == 0 else -0.12   # curled finger segments
            if t == 'palm' and ly > h - 2.0 and f in ('front', 'back'):
                v += 0.05 if ctx.i % 2 == 0 else -0.12       # finger splits
        c = pick(SKIN, v)
        if f in ('west', 'east') and 1.5 < ly < h - 2 and hash3(ctx.i, ctx.j, cseed(ctx), 3) > 0.8:
            c = mix(c, hx('#5d6a78'), 0.4)                  # cold veins
        if hash3(ctx.i, ctx.j, cseed(ctx) + 7, 4) > 0.94:
            c = mix(c, hx('#6a5a3c'), 0.45)                 # age spots
        return A(c, A_SKIN)
    if t in ('finger', 'thumb'):
        if ly > h - 1.0 and f in ('front', 'west', 'east', 'back'):
            return A(pick(SKIN, 0.9), A_SKIN)               # pale nail
        if f == 'bottom':
            return A(pick(SKIN, 0.86), A_SKIN)              # fingertip
        if f == 'top':
            return A(pick(SKIN, 0.5), A_SKIN)
        if t == 'finger' and abs(ly - h * 0.45) < 0.5:
            v -= 0.14                                       # knuckle crease
        if f in ('west', 'east'):
            v -= 0.06
    return A(pick(SKIN, v), A_SKIN)


# ------------------------------------------------------------------ the face mask
# 15 columns (x -7.5..7.5, col c <-> x = c - 7), 17 rows (row r <-> y = -43.5 + r, y -44..-27).
# Skull rows r0..r12, jaw rows r13..r16 (jaw cols 2..12, the jowls hold cols 0-1 / 13-14).  The spectacles (own
# plane) hide r4..r10 except the nose strip and the clipped rim corners.
# Value plan: 8-9 lit planes, 6-7 half tones, 4 the ONE shadow value, k creases, K the pressed lips.
GX0, GY0 = -7.5, -44
FACE = [
    # 012345678901234
    "556666666666655",   # r0  y-44 soft shadow under the starched band
    "678889k877BBBB6",   # r1  y-43 lit forehead | frown crease | the LEFT brow arches up (own cube, cols 9-14)
    "776665k66B9998b",   # r2  y-42 forehead bunched over the furrowed right brow | arch: brow head, lit lid, tail
    "444444k65577776",   # r3  y-41 shadow under the right brow block | lit lid space under the arch
    "444444464444444",   # r4  y-40 nose root between the rims
    "444444685444444",   # r5  long nose (own cube, cols 6..8) between the opaque lenses
    "444444685444444",   # r6  (bridge)
    "444444695444444",   # r7  aquiline bump catches the light
    "444444685444444",   # r8
    "444444584444444",   # r9
    "444444685444444",   # r10
    "578874574478875",   # r11 y-33 cheekbones lit (own cubes) | nose wings | nose tip
    "4677k65456k7764",   # r12 y-32 folds cut down from the nose wings, lit cheek bulge outside, shadow under nose
    "456k6KKKKK6k654",   # r13 y-31 ONE thin pressed line (jaw top row), folds running round the mouth
    "3454k67776k4543",   # r14 y-30 corners pulled down, pale lower lip, folds into the jowls
    "345564444465543",   # r15 y-29 under-lip shadow
    "234567888765432",   # r16 y-28 hard lit chin
]
assert all(len(r) == 15 for r in FACE), [len(r) for r in FACE]

FPAL = {str(i): A(SKIN[i], A_SKIN) for i in range(10)}
FPAL.update({
    'k': A(CREASE, A_SKIN), 'K': A(MOUTH_LINE, A_SKIN),
    'B': A(BROW[0], A_SKIN), 'b': A(BROW[1], A_SKIN), 'h': A(BROW[1], A_SKIN),
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


# spectacles: two round 7 x 7 rims + a 3-texel bridge = 17 x 7 (x -8.5..8.5, y -40..-33) on a plane in front of the
# nose.  The rims are ONE continuous dark ring (top included) with a single steel glint on the upper-outer arc; the
# lenses are pure glowing white with a cold blue crescent on the lower inner arc.
RING = [
    "..FFF..",
    ".FWWWF.",
    "FWWWWWF",
    "FWWWWWF",
    "FVWWWVF",
    ".FVVVF.",
    "..FFF..",
]


def _glasses():
    rows = []
    for j in range(7):
        r = list(RING[j])
        l = list(RING[j])
        if j == 1:
            r[1] = 'f'                                      # steel glint, upper-outer arc of each rim
            l[5] = 'f'
        mid = 'FFF' if j == 2 else '...'
        rows.append(''.join(r) + mid + ''.join(l))
    return rows


GLASSES = _glasses()
assert all(len(r) == 17 for r in GLASSES)
GPAL = {'F': FRAME, 'f': FRAME_HI, 'W': LENS, 'V': LENS_RIM}
GLOWPAL = {'W': (240, 248, 255, 255), 'V': (186, 214, 242, 255)}


def glasses_mat(ctx):
    """The spectacles are zero-thickness planes: only the GLASSES decal (and its 'eyes' glow) is painted; the
    temples are plain dark wire."""
    if tag(ctx) == 'temple':
        return A(FRAME, 255) if ctx.face == 'east' else None
    return None


# ------------------------------------------------------------------ props
STAMP = [            # blind-stamped cross of the Hermanas de la Vigilia on the back board
    ".x.",
    "xxx",
    ".x.",
    ".x.",
]


def leather_mat(ctx):
    """Oxblood ledger leather: blind-tooled frame, gilt title plate, banded spine, rubbed edges."""
    t = tag(ctx)
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    grain = (hash3(int(lx), int(lz), int(ly) + cseed(ctx), 5) - 0.5) * 0.08
    v = 0.56 + face_light(ctx) * 0.8 + grain
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
        ex = min(out_x, in_x)
        if ex < 1.0 or ez < 1.0:
            v -= 0.16                                       # board edge
            if out_x + ez < 6 and hash3(int(lx), int(lz), 3, 7) > 0.5:
                v += 0.26                                   # leather rubbed pale next to the brass corners
        elif ex < 2.0 or ez < 2.0:
            v += 0.06                                       # the board rounds over: light catch
            if (ex < 2.0 and int(lz) % 2 == 0) or (ez < 2.0 and int(lx) % 2 == 0):
                v -= 0.1                                    # blind-tooled frame
        if front:
            cx, cz = bx - bw / 2, lz - d / 2 + 2
            if abs(cx) < 3.1 and abs(cz) < 1.6:
                if abs(cx) > 2.2 or abs(cz) > 0.7:
                    return A(BRASS[6] if (cz < -0.7 or cx < -2.2) else BRASS[3], A_BOOK)   # bevelled gilt plate
                return A(BRASS[5] if int(lx) % 2 == 0 else OX[1], A_BOOK)            # 'ACTAS' lettering
            if abs(cx) < 3.1 and abs(cz - 3) < 0.5:
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
        v += 0.1                                            # board edges catch light
        if ctx.j == 0:
            v += 0.08
    elif f == 'top':
        v += 0.04
    return A(pick(OX, v), A_BOOK)


# red demerit check mark (2 texels thick) and the big X of the loose leaf
CHECK = [
    "....rr",
    "...rr.",
    "rr.rr.",
    ".rrr..",
    "..r...",
]
BIGX = [
    "R.....R",
    "RR...RR",
    ".RR.RR.",
    "..RRR..",
    ".RR.RR.",
    "RR...RR",
    "R.....R",
]


def page_mat(ctx):
    """Ledger pages: ruled lines, a red margin, bold names in blue-black ink and red demerit checks."""
    t = tag(ctx)
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    if t == 'leaf' and f != 'top':
        return None                                         # zero-thickness: one face only (no z-fight)
    if f == 'top':
        col, row = int(lx), int(lz)
        v = 0.86
        if (t == 'pages_r' and col == w - 1) or (t == 'pages_l' and col == 0):
            v -= 0.22                                       # gutter shadow
        if t == 'leaf':
            v = 0.92
        c = pick(PAPER, v)
        if row < 1 or row > d - 2:
            return A(pick(PAPER, v - 0.08), A_BOOK)         # blank head / foot of the page
        right = t == 'pages_r'
        margin = w - 2 if right else 1                      # red margin rule next to the gutter
        if row % 3 == 0:
            c = mix(c, RULE, 0.45)                          # ruled line
        if col == margin and t != 'leaf':
            c = mix(c, RED_INK2, 0.6)
        if t == 'leaf':
            # a fresh entry with a big red X over it
            if row % 3 == 1 and 1 <= col <= w - 2 and hash3(col, row, 7, 66) > 0.25:
                c = INK2
            gx, gy = col - (w - 7) // 2, row - (d - 7) // 2 - 1
            if 0 <= gy < 7 and 0 <= gx < 7 and BIGX[gy][gx] == 'R':
                c = RED_INK2 if (gx + gy) % 5 else RED_INK
            return A(c, A_BOOK)
        if row % 3 in (1, 2):
            n = row // 3 + (0 if right else 11)
            ln = 3 + int(hash3(n, 1, 0, 61) * 3)
            start = 1 if right else 3
            if row % 3 == 1 and start <= col < start + ln and hash3(col, row, n, 62) > 0.15:
                c = INK if hash3(col, row, n, 63) > 0.35 else INK2       # surname in ink
            # bold 2-texel red demerit check at the end of most lines
            if hash3(n, 2, 0, 64) > 0.35:
                cx0 = (w - 4) if not right else (w - 5)
                gx, gy = col - cx0, row % 3 - 1
                if 0 <= gx < 3 and ((gy == 0 and gx == 2) or (gy == 1 and gx in (0, 1))):
                    c = RED_INK2 if gx != 1 else RED_INK
        return A(c, A_BOOK)
    if f == 'bottom':
        return A(pick(PAPER, 0.3), A_BOOK)
    # page edges: thin stacked leaves, red-sprinkled like an old accounting ledger
    v = 0.7 + face_light(ctx) * 0.5 - (0.12 if ctx.j % 2 else 0.0)
    c = pick(PAPER, v)
    if hash3(ctx.i, ctx.j, cseed(ctx), 67) > 0.8:
        c = mix(c, hx('#8a4a40'), 0.45)                     # dusty red sprinkle
    return A(c, A_BOOK)


def brass_mat(ctx):
    v = 0.55 + face_light(ctx) * 1.3
    if ctx.face in ('top', 'front', 'west') and (ctx.i == 0 or ctx.j == 0):
        v += 0.25
    if edge(ctx) == 0 and ctx.face in ('bottom', 'back', 'east'):
        v -= 0.2
    return A(pick(BRASS, v), A_BOOK)


def ribbon_mat(ctx):
    if ctx.face != 'front':
        return None
    lx, ly, lz = local(ctx)
    h = ctx.cube.size[1]
    if ly > h - 1 and ctx.i == 0:
        return None                                         # forked end
    v = 0.55 - ly / h * 0.25
    return A(pick([hx('#1d0306'), hx('#3a070c'), hx('#5c0c14'), hx('#801520'), hx('#a12230')], v), A_BOOK)


def pen_mat(ctx):
    """Big cartoon fountain pen: black lacquer with a cool gloss streak, gold band + clip, gold nib, red tip."""
    t = tag(ctx)
    f = ctx.face
    lx, ly, lz = local(ctx)
    h = ctx.cube.size[1]
    if t == 'nib':
        if ly > h - 1.0:
            return A(RED_INK2 if f != 'bottom' else RED_INK, 255)   # red ink on the tip
        v = 0.62 + face_light(ctx) * 1.2 + (0.2 if ctx.i == 0 else 0)
        c = pick(BRASS, v)
        if f in ('front', 'back') and ctx.i == ctx.w // 2 and ly > 0.8:
            c = BRASS[1]                                    # slit
        return A(c, 255)
    if f in ('top', 'bottom'):
        return A(pick(PEN, 0.4 if f == 'top' else 0.15), 255)
    v = 0.18 + face_light(ctx) * 0.6
    if ctx.i == 0 and f in ('front', 'west'):
        v += 0.5                                            # lacquer gloss
    c = pick(PEN, v)
    if 2.0 <= ly < 3.0 or h - 3.0 <= ly < h - 2.0:
        c = pick(BRASS, 0.7 + face_light(ctx) + (0.15 if ctx.i == 0 else 0))     # gold bands
    if f == 'back' and 3.0 <= ly < 7.0:
        c = BRASS[6] if ctx.i == 0 else BRASS[4]            # clip
    if ly < 1.0:
        c = pick(PEN, 0.45)                                 # domed cap end
    return A(c, 255)


def bead_mat(ctx):
    """Rosary strand: pewter beads (2 tall) on a dark link (1 tall)."""
    lx, ly, lz = local(ctx)
    f = ctx.face
    if tag(ctx) == 'link':
        return A(IRON[3] if ctx.i == 0 else IRON[2], A_METAL)
    if f in ('top', 'bottom'):
        return A(pick(SILVER, 0.4), A_METAL)
    ph = int(ly) % 3
    if ph == 2:
        cx = lx if f in ('front', 'back') else lz
        if abs(cx - 1.0) > 0.6:
            return None
        return A(IRON[2], A_METAL)                          # link
    v = 0.58 + face_light(ctx) * 1.2
    if ph == 0 and ctx.i == 0:
        v += 0.3                                            # specular dot
    if ph == 1:
        v -= 0.15
    return A(pick(SILVER, v), A_METAL)


def silver_mat(ctx):
    v = 0.6 + face_light(ctx) * 1.3
    if ctx.face in ('front', 'west', 'top') and (ctx.i == 0 or ctx.j == 0):
        v += 0.2
    elif edge(ctx) == 0:
        v -= 0.15
    return A(pick(SILVER, v), A_METAL)


def ebony_mat(ctx):
    """Pectoral cross: polished ebony, reads black on the white bib."""
    v = 0.3 + face_light(ctx) * 1.0
    if ctx.face == 'front' and ctx.i == 0:
        v += 0.25
    return A(pick(PEN, v), 244)


def keys_mat(ctx):
    """The key ring is a zero-thickness plane: only its pixel-art decals (KEYS) are painted."""
    return None


# ring of three iron keys: round bows with holes, shafts, toothed bits (front of the hip is column 0)
KEYS = [
    "...ooo...",
    "..o...o..",
    "..o...o..",
    "..i...o..",
    "AAAoooCCC",
    "A.AiBBC.C",
    "AAAB.BCCC",
    ".a.BBB.c.",
    ".a..b..c.",
    ".a..b..cc",
    ".a..bb.c.",
    ".aa.b..cc",
    ".a..bb...",
    ".aa......",
    ".a.......",
]
KPAL = {'o': A(IRON[4], A_METAL), 'i': A(IRON[6], A_METAL),
        'A': A(IRON[5], A_METAL), 'B': A(IRON[4], A_METAL), 'C': A(IRON[5], A_METAL),
        'a': A(IRON[3], A_METAL), 'b': A(IRON[2], A_METAL), 'c': A(IRON[3], A_METAL)}


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


DEFAULT_MAT = habit_mat
FOCUS = 'head'

# ledger placement (WORLD, rest): cradled on the left forearm at the waist, pages tipped towards the viewer
BOOK_PIVOT = (0.5, -5.0, -16.5)
BOOK_WROT = (24, 0, 3)
PEN_TILT = 30
# rest rotations (deg) of arm / forearm / hand.  Right: elbow at the side, forearm raised, the pen poised over the
# right-hand page (solved numerically so the nib hovers 1.5 texels above the page).  Left: cradles the ledger.
ARM_REST = {
    'right': ((8.95, 13.24, -5.55), (-114.53, -29.61, 0), (49.5, -22.69, -41.54)),
    'left': ((-3, 0, 2), (-64, 6, 0), (0, 0, 0)),
}


def build():
    B = Builder()
    box, lbox = B.box, B.lbox

    def fbox(bone_, frm, size, mat=skin_mat, name=None):
        return box(bone_, frm, size, mat=mat, name=name, decals=face_decals(frm[0], frm[1], size[0], size[1]))

    # ---------------- body: root on the floor -- the rigid column tilts from the hem like a statue
    B.bone('body', (0, 24, 0), mat=habit_mat)
    box('body', (-10.5, -8, -6.5), (21, 32, 13), name='core')
    box('body', (-11.5, -9.5, -7.5), (23, 3, 15), mat=belt_mat, name='belt', inflate=0.15)
    box('body', (12.25, -8.5, -4.5), (0, 15, 9), mat=keys_mat, name='keys',
        decals={'east': pixelart(KEYS, KPAL, anchor='topleft')})
    # skirt: four stiff panels flaring a hair towards the floor (A-line column, hem ON the floor)
    B.bone('skirt_front', (0, -8, -6.5), parent='body', rot=(-2.5, 0, 0), mat=habit_mat)
    box('skirt_front', (-11.5, -8, -7), (23, 32, 1), name='panel')
    box('skirt_front', (-6, -6, -8), (12, 29, 1), name='scap')
    B.bone('skirt_back', (0, -8, 6.5), parent='body', rot=(3, 0, 0), mat=habit_mat)
    box('skirt_back', (-11.5, -8, 6), (23, 32, 1), name='panel')
    for side, sx in (('right', -1), ('left', 1)):
        sb = f'skirt_{side}'
        B.bone(sb, (10.5 * sx, -8, 0), parent='body', rot=(0, 0, -2.5 * sx), mat=habit_mat)
        box(sb, (10.35 * sx - (1 if sx < 0 else 0), -8, -7.5), (1, 32, 15), name='panel')   # inset: no z-fight

    # rosary: a link into the belt, pewter beads to the knee, silver crucifix
    B.bone('rosary', (-7.5, -7.5, -8.6), parent='body', rot=(-3, 0, 2), mat=bead_mat)
    box('rosary', (-8, -9.5, -8.4), (1, 3, 1), name='link')
    box('rosary', (-8.5, -7, -9.6), (2, 12, 2), name='beads')
    box('rosary', (-8.5, 5, -9.1), (2, 2, 1), mat=silver_mat, name='medal')
    box('rosary', (-8.5, 7, -9.1), (2, 7, 1), mat=silver_mat, name='crux')
    box('rosary', (-10.5, 8.5, -9.25), (6, 2, 1), mat=silver_mat, name='crux')

    # ---------------- chest: square block under a rigid capelet, big white bib, black pectoral cross
    B.bone('chest', (0, -8, 0), parent='body', mat=habit_mat)
    box('chest', (-9, -26, -6), (18, 18, 12), name='chest')
    box('chest', (-16.5, -26.5, -7.5), (33, 8, 15), name='cape')
    box('chest', (-9.5, -27, -8.5), (19, 16, 12), mat=linen_mat, name='bib')
    box('chest', (-1, -22, -9.3), (2, 8, 1), mat=ebony_mat, name='cross')
    box('chest', (-2.5, -20, -9.45), (5, 2, 1), mat=ebony_mat, name='cross')

    # back veil: starched black panel from under the head veil, lying on the capelet and the back down to the waist
    # (pivot at the hem on the back: when the head bows, the top follows the head veil and the hem stays put)
    B.bone('veil', (0, -5, 5.8), parent='chest', rot=(-6, 0, 0), mat=habit_mat)
    box('veil', (-12.5, -36, 3.8), (25, 31, 4), name='veil_back')

    # ---------------- head: roof -50, crown -49..-46, band, face window x -7.5..7.5 / y -44..-27
    B.bone('head', (0, -27, 0), parent='chest', mat=skin_mat)
    fbox('head', (-7.5, -47, -6), (15, 16, 12), name='skull')
    fbox('head', (-1.5, -39, -8), (3, 7, 2), name='nose')
    fbox('head', (1.5, -43, -7), (6, 2, 1), name='brow_l')
    fbox('head', (-7.5, -33.05, -6.5), (4, 2, 1), name='cheek')
    fbox('head', (3.5, -33.05, -6.5), (4, 2, 1), name='cheek')
    fbox('head', (-7.5, -31, -6.25), (2, 4, 6), name='jowl')
    fbox('head', (5.5, -31, -6.25), (2, 4, 6), name='jowl')
    box('head', (-10.5, -48, -7), (21, 4, 14), mat=linen_mat, name='band')
    box('head', (-10.5, -44, -7), (3, 18, 13), mat=linen_mat, name='coif_side')
    box('head', (7.5, -44, -7), (3, 18, 13), mat=linen_mat, name='coif_side')
    box('head', (-7.5, -27, -7), (15, 5, 12), mat=linen_mat, name='chinwrap')
    box('head', (-13.5, -49, -8.5), (27, 3, 19), mat=habit_mat, name='crown')
    box('head', (-12.5, -50, -7.5), (25, 1, 17), mat=habit_mat, name='roof')
    box('head', (-12.5, -47, 9.5), (25, 20, 2), mat=habit_mat, name='veil_nape', inflate=0.12)

    # the furrowed right brow: a block cutting diagonally across the top of the right lens
    B.bone('right_brow', (-1.5, -36.8, -7.6), parent='head', rot=(0, 0, 27), mat=skin_mat)
    lbox('right_brow', (-7.5, -1, -1.1), (8, 2, 3), name='brow_r')

    B.bone('glasses', (0, -36.5, -8.25), parent='head', mat=glasses_mat)
    box('glasses', (-8.5, -40, -8.25), (17, 7, 0), name='glasses',
        decals={'front': pixelart(GLASSES, GPAL, anchor='topleft'),
                'eyes:front': pixelart(GLASSES, GLOWPAL, anchor='topleft')})
    for sx in (-1, 1):
        box('glasses', (7.2 * sx, -38, -8.25), (0, 1, 6), name='temple')

    B.bone('jaw', (0, -31, 2), parent='head', mat=skin_mat)
    fbox('jaw', (-5.5, -31, -6), (11, 4, 9), name='jaw')
    fbox('jaw', (-3.5, -29, -6.75), (7, 2, 1), name='chin')

    for side, sx in (('right', -1), ('left', 1)):
        vb = f'veil_{side}'
        B.bone(vb, (10.5 * sx, -48, 2), parent='head', rot=(0, 0, -6 * sx), mat=habit_mat)
        box(vb, (10.5 * sx - (3 if sx < 0 else 0), -48, -5.7), (3, 26, 16), name='veil_side')

    # ---------------- arms (authored hanging, bent by the bone rotations); upper arms come out under the cape
    for side, sx in (('right', -1), ('left', 1)):
        arm, fa, hand = f'{side}_arm', f'{side}_forearm', f'{side}_hand'
        ax = 12.5 * sx
        B.bone(arm, (ax, -24, 0), parent='chest', rot=ARM_REST[side][0], mat=habit_mat)
        box(arm, (ax - 3.5, -25, -4), (7, 14, 8), name='sleeve_up')
        B.bone(fa, (ax, -12, 0), parent=arm, rot=ARM_REST[side][1], mat=habit_mat)
        box(fa, (ax - 3, -13, -3.5), (6, 8, 7), name='sleeve_lo')
        box(fa, (ax - 4, -6, -5), (8, 7, 10), name='cuff')
        box(fa, (ax - 2.5, 0.5, -2.5), (5, 2, 5), mat=linen_mat, name='undercuff')
        B.bone(hand, (ax, 2, 0), parent=fa, rot=ARM_REST[side][2], mat=hand_mat)
        if sx < 0:
            box(hand, (ax - 2, 2, -2), (4, 5, 4), name='fist')
            box(hand, (ax + 1.6, 2.5, -2.4), (1, 3, 1), inflate=0.3, name='thumb')
            # chunky index finger: lies along the top of the pen, straightens for 'Usted.'
            B.bone('right_index', (ax, 6.5, -2.1), parent=hand, rot=(PEN_TILT, 0, 0), mat=hand_mat)
            box('right_index', (ax - 1, 6.5, -3.1), (2, 6, 2), name='finger')
            # big cartoon fountain pen through the fist (cap end behind the knuckles, nib 10 texels out)
            B.bone('pen', (ax, 5, 0), parent=hand, rot=(PEN_TILT, 0, 0), mat=pen_mat)
            box('pen', (ax - 1, 0, -1), (2, 12, 2), name='barrel')
            box('pen', (ax - 1, 12, -1), (2, 3, 2), inflate=-0.2, name='nib')
        else:
            box(hand, (ax - 2, 2, -1.5), (4, 5, 3), name='palm')
            box(hand, (ax - 3, 3, -1.5), (1, 4, 3), inflate=0.1, name='fingers')     # curled round the board
            box(hand, (ax - 2.3, 1.5, -2.6), (1, 3, 1), inflate=0.3, name='thumb')

    # ---------------- ledger cradled on the left forearm, pages tipped towards the viewer
    B.bone('book', BOOK_PIVOT, parent='left_forearm', world=True, wrot=BOOK_WROT, mat=leather_mat)
    lbox('book', (-10.5, 0, -8.5), (21, 1, 17), name='cover')
    lbox('book', (-2, 1, -8.5), (4, 1, 17), name='spine')
    lbox('book', (-10, -2, -8), (9, 2, 16), mat=page_mat, name='pages_r')
    lbox('book', (1, -2, -8), (9, 2, 16), mat=page_mat, name='pages_l')
    lbox('book', (-1, -1, -8), (2, 1, 16), mat=page_mat, name='gutter')
    for cx in (-10.5, 8.5):
        for cz in (-8.5, 6.5):
            lbox('book', (cx, 0.2, cz), (2, 1, 2), mat=brass_mat, inflate=0.3, name='corner')
    lbox('book', (-0.5, -1.0, -8.6), (1, 6, 0), mat=ribbon_mat, name='ribbon')
    B.bone('book_page', B.r.abs_pivot['book'], parent='book', rot=(0, 0, -5), mat=page_mat)
    lbox('book_page', (1.1, -2.15, -7.5), (8, 0, 15), name='leaf')

    m = Model('madre', 256, 192, B.r.roots)
    m.scale = 0.5
    m.render_type = 'entityTranslucent'
    return m


POSES = {
    # 'Aja.' -- leans over the ledger, head bowed, book tipped back towards her, nib ON the right-hand page
    'write': {
        'chest': (0.06, 0, 0, 0, 0, 0),
        'head': (0.24, -0.1, 0.03, 0, 0, 0),
        'veil': (0.09, 0, 0, 0, 0, 0),
        'veil_right': (-0.1, 0, 0, 0, 0, 0),
        'veil_left': (-0.1, 0, 0, 0, 0, 0),
        'left_forearm': (-0.1, 0, 0, 0, 0, 0),
        'book': (-0.36, 0, 0, 0, 0, 0),
        'right_arm': (0.05, 0.046, -0.01, 0, 0, 0),
        'right_forearm': (-0.199, 0.122, 0, 0, 0, 0),
        'right_hand': (-0.03, 0.437, -0.114, 0, 0, 0),
    },
    # chin up, looking down her nose at you; the rigid column leans back from the hem; pushes up her glasses
    'stare': {
        'body': (-0.04, 0, 0, 0, 0, 0),
        'chest': (-0.06, 0, 0, 0, 0, 0),
        'head': (-0.2, 0, 0.05, 0, 0, 0),
        'veil': (-0.07, 0, 0, 0, 0, 0),
        'veil_right': (0.08, 0, 0, 0, 0, 0),
        'veil_left': (0.08, 0, 0, 0, 0, 0),
        'glasses': (0, 0, 0, 0, -0.6, 0),
        'right_brow': (0, 0, 0.06, 0, 0, 0),
        'right_forearm': (0.12, 0, 0, 0, 0, 0),
    },
    # 'Usted.' -- right shoulder forward, arm out at the player, chunky index finger straight, the pen sticking out
    # of the bottom of the fist like a dagger; mouth open on the word
    'point': {
        'chest': (0, -0.12, 0, 0, 0, 0),
        'left_arm': (-0.08, 0, 0, 0, 0, 0),
        'head': (-0.12, -0.08, 0, 0, 0, 0),
        'veil': (-0.04, 0, 0, 0, 0, 0),
        'veil_right': (0.04, 0, 0, 0, 0, 0),
        'veil_left': (0.04, 0, 0, 0, 0, 0),
        'jaw': (0.12, 0, 0, 0, 0, 0),
        'right_brow': (0, 0, 0.06, 0, 0, 0),
        'right_arm': (-1.291, 0.013, 0.097, 0, 0, 0),
        'right_forearm': (1.859, 0.517, 0, 0, 0, 0),
        'right_hand': (-0.602, 0.396, 1.039, 0, 0, 0),
        'right_index': (-0.524, 0, 0, 0, 0, 0),
        'pen': (1.222, 0, 0, 0, 0, 0),
    },
}

ANIM_NOTES = """
La Madre Remedios -- animation contract.  Angles in radians, ADDED to the rest pose; offsets (dx, dy, dz) in model
texels at 2x density (inside scale_root: 2 texels = 1 vanilla pixel), in the PARENT bone's space.  t = ageInTicks.
Poses (exported as POSE_WRITE / POSE_STARE / POSE_POINT): write, stare, point -- every value quoted below is the one
in the POSES table.

CHARACTER: a static apparition.  She NEVER walks, bobs or floats: the hem stays on the floor and the column stays
rigid.  All motion is small, slow and deliberate (max ~0.05 rad/tick) -- EXCEPT that she is always already facing
you: while the player is not looking at her, snap body yRot to face the player in one tick (statue logic).

RENDER: entityTranslucent; alpha is baked into the texture (habit 210, veil 246, linen 238, skin 252, ledger 238,
metal 232, pen / lenses / mouth 255).  Multiply a cold tint (0.86, 0.93, 1.0).  The 'eyes' layer (the two lenses)
renders full-bright on top; pulse its alpha 0.85..1.0 with sin(t*0.05) and spike to 1.0 on every "Aja.".  The
right_brow block sits in front of the right lens, so that lens always glows as an angry crescent.
APPEAR: global alpha 0 -> 1 over 8 ticks with a 2-tick flicker at 50 %; the skirt panels and veil wings flare out
(+0.06) and settle over 10 ticks as if a door had opened.  VANISH: alpha 1 -> 0 over 6 ticks, eyes layer last.

VEIL RULE (applies to every head pitch, posed or tracked): the head veil (crown, roof, nape, wings) is head-owned
and the long back veil is chest-owned, pivoted at its hem.  Whenever head xRot changes by h (total, incl. chest
pitch), add  veil xRot = -0.35*h  and  veil_right / veil_left xRot = -0.35*h  so the back veil follows the nape and the
wings stay on the capelet (no daylight between head veil and back veil).  The pose tables already contain this.

ROOT
* body -- root ON THE FLOOR (pivot 0, 24, 0): black core of the column, belt, ring of three iron keys on the left
  hip.  Rest never moves.  Stare -0.04 xRot: the whole rigid column tips back from the hem like a statue.  Statue
  snap: yRot jumps to face the player while unobserved.
* skirt_front / skirt_back / skirt_right / skirt_left -- the four stiff starched skirt panels (rest flare 2.5-3
  deg; the front one carries the scapular).  Static; draught flutter xRot/zRot += sin(t*0.03 + k)*0.01 (k = 0..3);
  appear/vanish gust +0.06 outward (front: -x, back: +x, right: +z, left: -z), ease back over 10 ticks.
* rosary -- link into the belt, pewter beads to the knee, silver crucifix.  Pendulum lagging the body:
  zRot = sin(t*0.06)*0.04; when the right arm snaps into 'point' give it an impulse zRot -0.15 decaying over 20
  ticks (bead clicks on the impulse).

TORSO
* chest -- square block under the rigid capelet, the big white bib and the black pectoral cross; carries arms,
  head and the back veil.  Breathing xRot sin(t*0.05)*0.012 (barely).  Write +0.06 (leans over the ledger), stare
  -0.06 (leans back), point yRot -0.12 (brings the right shoulder into the gesture).
* veil -- the long starched back veil lying on the capelet and the back, pivot at its hem (0, -5, 5.8) so its top
  follows the head veil.  Idle sway xRot sin(t*0.04)*0.01.  Write +0.09 (top forward with the bowed head), stare
  -0.07, point -0.04 (VEIL RULE); appear/vanish +0.05 then settle.

HEAD
* head -- FOCUS bone: skull + face cubes (nose, raised left brow, cheekbones, jowls), white coif (band, cheek
  plates, chin wrap), black veil crown + roof + nape.  Tracks the player: yaw clamp +-0.6, pitch clamp -0.3..0.35,
  slow (0.04 rad/tick), always with the VEIL RULE.  "Aja." beat: dip xRot +0.1 and back over 6 ticks while the pen
  ticks the ledger.  Write (0.24, -0.1, 0.03) looks down into the ledger; stare (-0.2, 0, 0.05) chin up with a
  disdainful tilt; point (-0.12, -0.08, 0).  Roll call: between names turn yaw towards each empty desk.
* right_brow -- the furrowed right brow block in front of the right lens (rest zRot 27 deg).  Idle: nothing.  On
  every "Aja." and in stare / point: zRot +0.06 (deeper scowl, the lens crescent narrows).  Surprise (player
  answers "presente"): zRot -0.15 for 10 ticks.
* glasses -- round steel spectacles with temples and the opaque glowing lenses (emissive 'eyes' layer).  Static;
  signature gesture in stare: pushed up the nose, dy -0.6 (table value) -- animate it 8 ticks up, hold, back over 4
  (sync a small right_hand lift).
* jaw -- the narrow hinge jaw between the jowls: lower lip + chin (hinge 0, -31, 2).  Rest closed (one thin pressed
  line).  Voice-driven: xRot = amp*0.18 (max 0.2).  "Aja." = two short opens (0.1, then 0.06).  "Usted." = one 0.14
  open; point holds 0.12.  "Silencio." = three.
* veil_right / veil_left -- the black veil wings falling over the coif onto the capelet (rest zRot -+6 deg
  outwards, pivots at the crown).  Follow the head with the VEIL RULE (write -0.1, stare +0.08, point +0.04);
  appear/vanish flare zRot -+0.08 and settle.

ARMS -- right_* is -X (viewer's left).  Rest: the right forearm is raised with the pen poised 1.5 texels over the
right-hand page; the left forearm cradles the ledger.
* right_arm -- pen arm, upper sleeve under the capelet (pivot at the shoulder).  Idle static.  Write (0.05, 0.046,
  -0.01); point (-1.291, 0.013, 0.097) raises it out towards the player.
* right_forearm -- forearm + bell cuff + white undercuff.  Write (-0.199, 0.122) brings the nib down onto the page;
  point (1.859, 0.517) straightens the elbow; stare +0.12 lowers the pen a little.
* right_hand -- fist holding the pen.  Idle: taps the nib on the ledger every 80-140 ticks (xRot +0.12 for 3 ticks).
  Write (-0.03, 0.437, -0.114): the nib's lowest edge rests ON the right-hand page (checked numerically, < 0.1
  texel); point (-0.602, 0.396, 1.039) bends the wrist so the finger shows from the front.
* right_index -- chunky index finger lying along the top of the pen.  Point -0.524 (dead straight, out of the fist).
  Running player ("En el colegio se camina."): finger wag zRot sin(t*0.9)*0.25 for 20 ticks on top of point.
* pen -- big black-lacquer fountain pen, gold bands and clip, gold nib with a red tip.  Write: scribble on top of
  the pose -- xRot += sin(t*1.2)*0.05, zRot += cos(t*1.2)*0.04 (2-3 strokes, then a firm tick: xRot +0.08 for 2
  ticks).  Point +1.222: swung down out of the bottom of the fist like a dagger so the finger is the longest thing.
* left_arm -- book arm, upper sleeve under the capelet.  Static.  Point -0.08 (keeps the ledger off the belt while
  the chest turns).
* left_forearm -- forearm + cuff carrying the ledger at the waist.  Write -0.1 lifts the book towards her; roll
  call: same.
* left_hand -- hand clasped round the outer board of the ledger (palm, curled fingers, thumb).  Static.

LEDGER
* book -- the open libro de actas (oxblood boards, brass corner caps, gilt title plate, banded spine, ruled pages
  of names with bold red checks, red ribbon).  Rest tipped ~24 deg TOWARDS the viewer so both pages read from 3-5
  blocks.  Write -0.36 (tipped back flat for writing).  On "Aja." a tiny settle +0.03 after the tick.
* book_page -- a loose leaf with a big red X lying on the left-hand pages; pivot on the spine.  PAGE TURN: zRot
  0 -> -3.03 over 10 ticks (ease in-out), then snap back to 0 out of sight (or on the next turn).  Turn one page per
  "Aja." and between roll-call names.

LAYERING
idle = (almost nothing) breathing + eyes pulse + occasional pen tap + statue snap.  'write' blends in over 6 ticks
and loops the pen scribble with head dips on every "Aja.".  'stare' over 10 ticks (glasses push).  'point' snaps in
over 3 ticks (fast, it is the scare) and holds while she says "Usted.", then eases out over 12.
"""
