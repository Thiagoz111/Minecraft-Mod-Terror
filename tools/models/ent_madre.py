"""La Madre Remedios Iturbe -- the static apparition of the Mother Superior (DEAD LINE, case 'colegio').

Authored at 2x texel density (model.scale = 0.5).  +Y down, ground y = 24, faces -Z, right_* on -X.  Centred on
x = 0, z = 0 (only the ledger, the arms and the back veil leave the column).  Height 2.3 blocks: veil crest
y = -50 -> hem y = 24 (74 texels).  Cube / bone counts and texture size: see build().

Design (round 3)
----------------
Silhouette: a rigid BLACK COLUMN read like a chess piece -- a HEAD, SHOULDERS and a BASE.  The starched veil has a
rounded two-step crown (25 -> 21 -> 13 wide); its wings drop straight down beside the white coif, so the head stays
a narrow 25-wide column that lands on dead-square 35-wide shoulders with a clear notch on each side.  The capelet
squares the shoulders, the skirt (four stiff panels) drops with almost no waist onto a bell step: the hem of the
habit pooled on the floor, fading out (alpha 210 -> 110 over the last 8 texels) so she rises out of the floor
instead of standing on it.  At rest the open ledger's brass corner and the raised pen hand break the front
outline.  From behind: the crown steps, the black back veil (narrower than the shoulders) hangs to the hip in a
pointed V with a pale rim and a centre seam, standing proud of the skirt.
On the black: a graphic WHITE FRAME -- the starched forehead band and coif plates box the face in a hard
rectangle, a starched fold rolls under the chin onto the big flat bib with its black pectoral cross.

Face (15 x 17 window, hand-placed pixel art over layered cubes: skull, nose, cheekbones, jowls, a narrow hinge jaw,
chin).  Waxy yellow-grey skin, flat value plan: lit planes (forehead, cheekbones, nose ridge, lower lip, chin), one
mid tone for the muzzle, dark sockets round the spectacles, single-value creases.  ROUND STEEL SPECTACLES on their
own plane: a 1-texel steel ring with one glint, a 3-texel bridge, short temples that tuck under the coif, and
OPAQUE GLOWING lenses (emissive 'eyes' layer): a hot white core inside a slightly dimmer cold ring -- light, never
eyes.  Her right brow is a separate tapered block (`right_brow`: thick inner head, thin tail, a flesh ridge under
the hairs) pressing diagonally over the right lens, which glows as a narrow angry crescent; the left brow is a thin
grey arch raised high over a wide-open lens ("Aja.").  Long aquiline nose, nasolabial folds as two clean diagonals
from the nose wings to past the mouth corners, ONE thin pressed line for the lips with the corners pulled down, a
pale lower lip and a hard lit chin.

Props: an open LEDGER (libro de actas, 21 x 17 x 3 open) in oxblood leather with brass corner caps, a gilt title
plate, a blind-stamped cross, banded spine, red-sprinkled page edges, ruled pages full of names and bold red
demerit checks, a loose leaf with a big red X and a red ribbon -- cradled on the left forearm and tipped out past
the left hip.  A big cartoon FOUNTAIN PEN (black lacquer, gold bands and clip, gold nib with a red tip) in the
right fist under a long index finger (2 x 8) that straightens for 'Usted.' while the pen turns back along the
wrist.  A pewter ROSARY from the belt to the knee with a silver crucifix.  Three iron keys fanned on an iron ring at
the left hip.

Palette: cold blue-black wool (crisp organ pleats with one lit ridge texel, a pale rim on every outer veil edge,
step and hem so the shapes survive fog), cold blue-grey shadowed starched linen, waxy ivory skin, oxblood + brass +
red ink as the only warm accents.  Translucent: habit 210 (sleeves 228) fading to 110 at the floor, veil 246 with
its pointed hem fading to ~190, linen 238, skin 252; lenses opaque and full-bright.
"""
import math

import numpy as np

from mcmodel import Model, hash3, face_light, pick, rot_matrix
from rig import Rig
from paint import hx, mix, pixelart

# ------------------------------------------------------------------ translucency
A_HABIT = 210
A_SLEEVE = 228
A_LINEN = 238
A_SKIN = 252
A_BOOK = 238
A_METAL = 232
A_VEIL = 246
A_FLOOR = 110          # the habit fades to this where it meets the floor
FADE_Y0 = 16.0         # ... starting 8 texels above the floor


def A(c, a):
    return (c[0], c[1], c[2], int(a))


def floor_fade(y, a):
    """She does not stand on the floor, she rises out of it: alpha fades over the last 8 texels of the hem."""
    t = max(0.0, min(1.0, (y - FADE_Y0) / (24.0 - FADE_Y0)))
    return int(round(a + (A_FLOOR - a) * t))


# ------------------------------------------------------------------ palettes (hand-picked, hue shifted, cold)
HABIT = [hx(c) for c in ('#020307', '#06080e', '#0b0e16', '#11151f', '#181d29', '#202736', '#2a3245',
                         '#384157', '#4a556d')]
LINEN = [hx(c) for c in ('#1b2230', '#2f3849', '#475265', '#636f82', '#818ea0', '#a0abbb', '#bcc6d2',
                         '#d4dce5', '#e7ecf1', '#f5f7f9')]
# waxy skin: cool grey-green shadows -> sickly ivory lights
SKIN = [hx(c) for c in ('#2b2d28', '#3a3d36', '#4a4c44', '#5b5e54', '#6e7064', '#8f9080', '#aeab95',
                        '#c6c2a4', '#d9d5b9', '#e9e6d0')]
BROW = [hx('#2a2b2f'), hx('#4a4c51'), hx('#6c6e70'), hx('#8f8e88')]
CREASE = hx('#45463e')
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
STEEL = hx('#56606f')
STEEL_HI = hx('#e4ebf3')
LENS = hx('#ffffff')
LENS_RIM = hx('#c4dcf2')
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
    'core': ('top', 'bottom'), 'chest': ('top', 'bottom', 'front'), 'sleeve_up': ('top', 'bottom'),
    'sleeve_lo': ('top', 'bottom'), 'cuff': ('top',), 'veil_back': ('front', 'top'), 'scap': ('back', 'top'),
    'panel': ('top', 'bottom'), 'veil_side': ('top', 'bottom'), 'cape': (),
    'veil_nape': ('front', 'top', 'bottom'), 'roof': ('bottom',), 'crest': ('bottom',), 'hem': ('bottom',),
}
VEILS = ('crown', 'roof', 'crest', 'veil_side', 'veil_back', 'veil_nape')
V_DEPTH = 9.0          # the back veil's pointed hem rises this much at its sides
FADED = ('core', 'panel', 'scap', 'hem')


def habit_mat(ctx):
    """Starched black wool: crisp organ pleats, lit square edges, pale rims on the veil, steps and hem."""
    t = tag(ctx)
    f = ctx.face
    if f in HIDDEN.get(t, ()):
        return None
    if t == 'sleeve_up' and f == 'west' and ctx.bone.name == 'left_arm':
        return None                                         # pressed against the chest, never seen
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    k = cseed(ctx)
    a = A_VEIL if t in VEILS else (A_SLEEVE if t in ('sleeve_up', 'sleeve_lo', 'cuff') else A_HABIT)
    side = f in ('front', 'back', 'west', 'east')
    v = 0.42 + face_light(ctx) * 1.15
    rim = False                                             # pale outer edge that keeps the shape in fog
    if t == 'core':
        return A(pick(HABIT, 0.12), floor_fade(ctx.y, a))
    if t == 'hem':                                          # the hem pooled on the floor: a stiff bell step
        if f == 'top':
            v = 0.47
            if edge(ctx) == 0:
                rim = True                                  # the lip of the step catches the light
            elif edge(ctx) == 1:
                v = 0.36
        elif side:
            v += pleat(around(ctx), 2, 5) * 0.7
            if ctx.j == 0:
                rim = True
    elif t == 'panel':
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
                v += 0.16                                   # the square shoulder line catches the light
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
            if ly < 1.0 and f in ('west', 'east'):
                rim = True                                  # the square shoulder seen in profile
        elif f == 'bottom':
            v -= 0.1
    elif t == 'veil_back':                                  # long back veil with a pointed hem
        cx = abs(lx - w / 2) / (w / 2) if f in ('front', 'back', 'bottom') else 1.0
        hem = h - V_DEPTH * cx ** 1.25
        if ly > hem + 1e-6:
            return None
        to_hem = hem - ly
        if side:
            v += pleat(around(ctx), k % 9, 6) * 0.7
        if to_hem < 1.0:
            rim = True
        if f == 'back':
            if abs(lx - w / 2) < 0.6 and to_hem > 1.2:
                v -= 0.14                                   # centre seam
            if ly < 1.5:
                v -= 0.08                                   # shadow under the nape
            if ctx.i in (0, ctx.w - 1):
                rim = True
        if f in ('west', 'east') and ctx.i == ctx.w - 1:
            rim = True
        a = A_VEIL - int(max(0.0, 4.0 - to_hem) * 14)       # the veil thins out towards its point
    elif t in ('veil_side', 'veil_nape') and side:
        v += pleat(around(ctx), k % 9, 6) * 0.8
        if t == 'veil_side':
            if f in ('front', 'back') and (ctx.i in (0, ctx.w - 1)):
                rim = True
            if h - ly < 1.0:
                rim = True                                  # lower edge lying on the capelet
            outer = (f == 'west' and ctx.x < 0) or (f == 'east' and ctx.x > 0)
            if outer and (ctx.i in (0, ctx.w - 1)):
                rim = True
        elif f == 'back' and ctx.i in (0, ctx.w - 1):
            rim = True
    elif t in ('sleeve_up', 'sleeve_lo', 'cuff') and side:
        v += pleat(around(ctx), k % 4, 7) * 0.5
        if t == 'sleeve_up' and ly > h - 3:
            v -= 0.05                                       # elbow creases
            if (ctx.i + int(ly)) % 4 == 0:
                v -= 0.08
    if t in ('crown', 'roof', 'crest'):                     # the two-step starched crown
        if f == 'top':
            v -= 0.02
            if t == 'crest':
                v += pleat(lx, 3, 6) * 0.3                  # starched folds running front to back
                if abs(lx - w / 2) < 0.6:
                    v -= 0.08                               # centre seam of the veil
            if ctx.j in (0, ctx.h - 1) or ctx.i in (0, ctx.w - 1):
                v += 0.18                                   # each starched step catches the light on its lip
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
        if f == 'front' and ctx.cube.size[2] == 1 and ctx.i % 9 == 4 and h - ly > 3:
            c = mix(c, HABIT[0], 0.5)                       # seams
    if t == 'hem' and side and ctx.j == ctx.h - 1:
        c = mix(c, DUST, 0.4)                               # chalk dust of the corridors on the hem edge
    if t == 'cuff' and side and h - ly < 1.0:
        c = mix(c, HABIT[7], 0.55)                          # rolled edge of the bell
    if t in FADED:
        a = floor_fade(ctx.y, a)
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
    if t == 'coif_side' and f in ('top', 'bottom'):
        return None
    if t == 'chinfold' and f in ('back', 'bottom'):
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
    elif t == 'chinfold':                                   # starched fold rolled under the chin onto the bib
        if f == 'front':
            v = 0.86 if ctx.j == 0 else 0.6                 # lit roll, shadowed underside
            if ctx.i in (0, ctx.w - 1):
                v -= 0.1
        elif f == 'top':
            v = 0.9 if ctx.j > 0 else 0.55                  # the back row tucks under the chin
        else:
            v = 0.7 if ctx.j == 0 else 0.55
    elif t == 'bib':
        cx = abs(lx - w / 2)
        if f == 'front':
            hw = bib_shape(lx, ly, w, h)
            if cx > hw:
                return None                                 # rounded bottom corners
            fold = int(h * 0.56)
            v = 0.93 if ly < fold else 0.86                 # flat starched field, a step darker under the fold
            if ly < 1.0:
                v = 0.6                                     # shadow line under the chin fold
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
# the furrowed right brow block, front face: i = 0 the thin tail (outer, up high) .. 7 the thick head (by the nose).
# s forehead skin, h / g grey hairs, H / K the dark knot of the scowl, r / q the flesh ridge pressing on the lens
BROWART = [
    "sssssgHH",
    "hhhghHHK",
    "rrrrrrqq",
]
BROWPAL = {'s': SKIN[6], 'h': BROW[1], 'g': BROW[2], 'H': BROW[0], 'K': hx('#1d1d21'), 'r': SKIN[5], 'q': SKIN[4]}


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
            return A(pick(SKIN, 0.42), A_SKIN)
        if f == 'top':
            return A(pick(SKIN, 0.7), A_SKIN)
        inner = (f == 'east' and ctx.x < 0) or (f == 'west' and ctx.x > 0)
        if inner:
            return A(pick(SKIN, 0.55), A_SKIN)
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
    if t == 'brow_r':
        if f == 'back':
            return None
        if f == 'front':
            ch = BROWART[min(ctx.j, 2)][min(ctx.i, 7)]
            return A(BROWPAL[ch], A_SKIN)
        if f == 'top':
            return A(SKIN[6], A_SKIN)                       # forehead skin, not a lit bar
        if f == 'bottom':
            return A(SKIN[3], A_SKIN)
        if f == 'east' and ctx.j < 2:
            return A(BROW[0], A_SKIN)                       # end of the thick head
        return A(SKIN[5], A_SKIN)
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
        if f in ('west', 'east') and 1.5 < ly < h - 2 and (ctx.i * 7 + ctx.j * 3 + cseed(ctx)) % 11 == 0:
            c = mix(c, hx('#5d6a78'), 0.4)                  # cold veins
        if (ctx.i * 5 + ctx.j * 11 + cseed(ctx)) % 23 == 0:
            c = mix(c, hx('#6a5a3c'), 0.45)                 # age spots
        return A(c, A_SKIN)
    if t in ('finger', 'thumb'):
        if ly > h - 1.0 and f in ('front', 'west', 'east', 'back'):
            return A(pick(SKIN, 0.9), A_SKIN)               # pale nail
        if f == 'bottom':
            return A(pick(SKIN, 0.86), A_SKIN)              # fingertip
        if f == 'top':
            return A(pick(SKIN, 0.5), A_SKIN)
        if t == 'finger' and (abs(ly - 3.5) < 0.5 or abs(ly - 6.5) < 0.5):
            v -= 0.14                                       # knuckle creases
        if f in ('west', 'east'):
            v -= 0.06
    return A(pick(SKIN, v), A_SKIN)


# ------------------------------------------------------------------ the face mask
# 15 columns (x -7.5..7.5, col c <-> x = c - 7), 17 rows (row r <-> y = -43.5 + r, y -44..-27).
# Skull rows r0..r12, jaw rows r13..r16 (jaw cols 2..12, the jowls hold cols 0-1 / 13-14).  The spectacles (own
# plane) hide r4..r10 except the nose strip and the rim corners (dark sockets).  The right brow is its own cube.
# Value plan: 7-9 lit planes, 6 forehead, 5 the muzzle / jowls, 3-4 sockets and under-nose, k creases, K lips,
# h the thin grey arch of the raised LEFT brow (rises from the nose, peaks over the outer third, drops).
GX0, GY0 = -7.5, -44
FACE = [
    # 012345678901234
    "455555555555554",   # r0  y-44 soft shadow under the starched band
    "667777777777hh6",   # r1  y-43 forehead | the left arch peaks over the outer third of the lens
    "666666k677hh66h",   # r2  y-42 frown crease over the furrowed right brow | arch rising ... and dropping
    "555556k66h66666",   # r3  y-41 | the arch starts by the nose
    "333333565333333",   # r4  y-40 nose root between the rims, dark sockets round them
    "333333575333333",   # r5  long nose (own cube, cols 6..8) between the glowing lenses
    "333333585333333",   # r6  (bridge)
    "333333595333333",   # r7  aquiline bump catches the light
    "333333585333333",   # r8
    "333333474333333",   # r9
    "333333585333333",   # r10
    "67787k585k78776",   # r11 y-33 cheekbones lit (own cubes) | the folds start at the nose wings
    "6677k54445k7766",   # r12 y-32 folds run down and out, shadow under the nose
    "556k5KKKKK5k655",   # r13 y-31 ONE thin pressed line (jaw top row), folds clear of the mouth
    "55k5K66666K5k55",   # r14 y-30 corners pulled down, pale lower lip, folds pass the corners
    "55k555666555k55",   # r15 y-29 folds end past the mouth corners | chin
    "444557888755444",   # r16 y-28 hard lit chin, flat jowls
]
assert all(len(r) == 15 for r in FACE), [len(r) for r in FACE]

FPAL = {str(i): A(SKIN[i], A_SKIN) for i in range(10)}
FPAL.update({'k': A(CREASE, A_SKIN), 'K': A(MOUTH_LINE, A_SKIN), 'h': A(BROW[1], A_SKIN)})


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
# nose.  The rims are a thin 1-texel STEEL ring with a single glint on the upper-outer arc; the lenses glow: a hot
# white core inside a slightly dimmer cold ring, so they read as light, not as eyeballs.
RING = [
    "..SSS..",
    ".SVVVS.",
    "SVWWWVS",
    "SVWWWVS",
    "SVWWWVS",
    ".SVVVS.",
    "..SSS..",
]


def _glasses():
    rows = []
    for j in range(7):
        r = list(RING[j])
        l = list(RING[j])
        if j == 1:
            r[1] = 'g'                                      # steel glint, upper-outer arc of each rim
            l[5] = 'g'
        mid = 'SSS' if j == 2 else '...'
        rows.append(''.join(r) + mid + ''.join(l))
    return rows


GLASSES = _glasses()
assert all(len(r) == 17 for r in GLASSES)
GPAL = {'S': STEEL, 'g': STEEL_HI, 'W': LENS, 'V': LENS_RIM}
GLOWPAL = {'W': (255, 255, 255, 255), 'V': (176, 206, 238, 255)}


def glasses_mat(ctx):
    """The spectacles are zero-thickness planes: only the GLASSES decal (and its 'eyes' glow) is painted; the
    temples are steel wire painted on both sides, tucking under the coif."""
    if tag(ctx) == 'temple':
        lx, ly, lz = local(ctx)
        return A(STEEL_HI if lz < 0.6 else STEEL, 255)      # hinge glint where it leaves the rim
    return None


# ------------------------------------------------------------------ props
STAMP = [            # blind-stamped cross of the Hermanas de la Vigilia on the back board
    ".x.",
    "xxx",
    ".x.",
    ".x.",
]
# hand-placed wear on the outer boards (cover-local lx, lz): pale scuffs and dark ink / thumb stains
SCUFFS = {(3, 4): 0.14, (4, 4): 0.1, (4, 5): 0.08, (15, 11): 0.14, (16, 12): 0.12, (17, 3): 0.12,
          (6, 13): 0.1, (13, 14): 0.08, (18, 9): 0.1}
STAINS = {(5, 9): -0.12, (6, 9): -0.1, (6, 10): -0.08, (14, 6): -0.1, (15, 6): -0.08}


def leather_mat(ctx):
    """Oxblood ledger leather: blind-tooled frame, gilt title plate, banded spine, worn dark edges, a few
    hand-placed scuffs and stains (no noise)."""
    t = tag(ctx)
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    v = 0.56 + face_light(ctx) * 0.8
    if t == 'cover' and f == 'bottom':
        sp0, sp1 = w / 2 - 1.5, w / 2 + 1.5
        if sp0 <= lx < sp1:                                 # spine strip between the boards
            band = int(lz) % 4 == 1
            v = 0.26 + (0.2 if band else 0.0)
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
            v -= 0.24                                       # dark worn edge of the board
            if out_x < 1.0 and ez < 3.5:
                v += 0.3                                    # leather rubbed pale next to the brass corners
        elif ex < 2.0 or ez < 2.0:
            v += 0.06                                       # the board rounds over: light catch
            if (ex < 2.0 and int(lz) % 2 == 0) or (ez < 2.0 and int(lx) % 2 == 0):
                v -= 0.1                                    # blind-tooled frame
        v += SCUFFS.get((int(lx), int(lz)), 0.0) + STAINS.get((int(lx), int(lz)), 0.0)
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
        v = 0.32 + face_light(ctx) * 0.8
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
    """The keys are a zero-thickness plane: only their pixel-art decal (KEYS) is painted."""
    return None


# three iron keys fanned from the ring (east face, column 0 = front of the hip, row 0 = y -6): round bows, long
# shafts, toothed bits; dark iron with one glint per bow so they read as keys, not as white pixels
KEYS = [
    "...........",
    "...........",
    "....GBB....",
    ".GAAB.BCCg.",
    ".A.ABBBC.C.",
    ".AAA.b.CCC.",
    "..a..b..c..",
    "..a..b..c..",
    ".a...b...c.",
    ".a...bb..c.",
    "a....b...cc",
    "aa...bb...c",
    "a....b.....",
    ".....b.....",
]
assert all(len(r) == 11 for r in KEYS)
KPAL = {'A': A(IRON[4], A_METAL), 'B': A(IRON[4], A_METAL), 'C': A(IRON[4], A_METAL),
        'a': A(IRON[3], A_METAL), 'b': A(IRON[3], A_METAL), 'c': A(IRON[3], A_METAL),
        'G': A(IRON[6], A_METAL), 'g': A(IRON[5], A_METAL)}
RING_ART = [".OO.", "O..O", "O..O", ".OO."]


def ring_mat(ctx):
    """The iron key ring hanging from the belt: a 1-texel ring with a real hole."""
    f = ctx.face
    if f in ('west', 'east'):
        if RING_ART[min(ctx.j, 3)][min(ctx.i, 3)] == '.':
            return None
        return A(pick(IRON, 0.62 if ctx.j == 0 else 0.48), A_METAL)
    return A(pick(IRON, 0.45 + face_light(ctx)), A_METAL)


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

# ledger placement (WORLD, rest): cradled on the left forearm, pages tipped towards the viewer and rolled out past
# the left hip so its brass corner breaks the front outline
BOOK_PIVOT = (3.0, -5.0, -16.5)
BOOK_WROT = (24, 0, 10)
PEN_TILT = 30
# rest rotations (deg) of arm / forearm / hand.  Right: elbow at the side, forearm raised, the pen poised over the
# right-hand page (solved numerically).  Left: cradles the ledger (solved so the cuff stays under the boards).
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
    box('body', (-10.5, -8, -6.5), (21, 30, 13), name='core')
    box('body', (-11.5, -9.5, -7.5), (23, 3, 15), mat=belt_mat, name='belt', inflate=0.15)
    box('body', (-14.5, 22, -10.5), (29, 2, 21), name='hem')            # the bell step she rises out of
    # three iron keys fanned on an iron ring hanging from the belt at the left hip
    box('body', (11.65, -8, -3), (1, 4, 4), mat=ring_mat, name='ring')
    box('body', (12.4, -6, -6), (0, 14, 11), mat=keys_mat, name='keys',
        decals={'east': pixelart(KEYS, KPAL, anchor='topleft')})
    # skirt: four stiff panels flaring a hair onto the hem step (A-line column)
    B.bone('skirt_front', (0, -8, -6.5), parent='body', rot=(-2.5, 0, 0), mat=habit_mat)
    box('skirt_front', (-11.5, -8, -7), (23, 30, 1), name='panel')
    box('skirt_front', (-6, -6, -8), (12, 28, 1), name='scap')
    B.bone('skirt_back', (0, -8, 6.5), parent='body', rot=(3, 0, 0), mat=habit_mat)
    box('skirt_back', (-11.5, -8, 6), (23, 30, 1), name='panel')
    for side, sx in (('right', -1), ('left', 1)):
        sb = f'skirt_{side}'
        B.bone(sb, (10.5 * sx, -8, 0), parent='body', rot=(0, 0, -2.5 * sx), mat=habit_mat)
        box(sb, (10.35 * sx - (1 if sx < 0 else 0), -8, -7.5), (1, 30, 15), name='panel')   # inset: no z-fight

    # rosary: a link into the belt, pewter beads to the knee, silver crucifix
    B.bone('rosary', (-7.5, -7.5, -8.6), parent='body', rot=(-3, 0, 2), mat=bead_mat)
    box('rosary', (-8, -9.5, -8.4), (1, 3, 1), name='link')
    box('rosary', (-8.5, -7, -9.6), (2, 12, 2), name='beads')
    box('rosary', (-8.5, 5, -9.1), (2, 2, 1), mat=silver_mat, name='medal')
    box('rosary', (-8.5, 7, -9.1), (2, 7, 1), mat=silver_mat, name='crux')
    box('rosary', (-10.5, 8.5, -9.25), (6, 2, 1), mat=silver_mat, name='crux')

    # ---------------- chest: square block under a rigid capelet (35 wide), big white bib, black pectoral cross
    B.bone('chest', (0, -8, 0), parent='body', mat=habit_mat)
    box('chest', (-9, -26, -6), (18, 18, 12), name='chest')
    box('chest', (-17.5, -26.5, -7.5), (35, 8, 15), name='cape')
    box('chest', (-9.5, -27, -8.5), (19, 16, 12), mat=linen_mat, name='bib')
    box('chest', (-1, -22, -9.3), (2, 8, 1), mat=ebony_mat, name='cross')
    box('chest', (-2.5, -20, -9.45), (5, 2, 1), mat=ebony_mat, name='cross')

    # back veil: narrower than the shoulders, from under the head veil down to the hip in a pointed V, lying on the
    # capelet (pivot at the point of the hem: when the head bows, the top follows the head veil, the point stays)
    B.bone('veil', (0, 2, 9.1), parent='chest', mat=habit_mat)
    box('veil', (-10.5, -31, 7.6), (21, 33, 3), name='veil_back')

    # ---------------- head: crest -50, roof -49, crown -48..-46, band, face window x -7.5..7.5 / y -44..-27
    B.bone('head', (0, -27, 0), parent='chest', mat=skin_mat)
    fbox('head', (-7.5, -47, -6), (15, 16, 12), name='skull')
    fbox('head', (-1.5, -39, -8), (3, 7, 2), name='nose')
    fbox('head', (-7.5, -33.05, -6.5), (4, 2, 1), name='cheek')
    fbox('head', (3.5, -33.05, -6.5), (4, 2, 1), name='cheek')
    fbox('head', (-7.5, -31, -6.25), (2, 4, 6), name='jowl')
    fbox('head', (5.5, -31, -6.25), (2, 4, 6), name='jowl')
    box('head', (-10.5, -48, -7), (21, 4, 14), mat=linen_mat, name='band')
    box('head', (-10.5, -44, -7), (3, 18, 13), mat=linen_mat, name='coif_side')
    box('head', (7.5, -44, -7), (3, 18, 13), mat=linen_mat, name='coif_side')
    box('head', (-8.5, -26, -9.5), (17, 2, 3), mat=linen_mat, name='chinfold')
    box('head', (-12.5, -48, -8.5), (25, 2, 20), mat=habit_mat, name='crown')
    box('head', (-10.5, -49, -7.5), (21, 1, 18), mat=habit_mat, name='roof')
    box('head', (-6.5, -50, -5.5), (13, 1, 14), mat=habit_mat, name='crest')
    box('head', (-12.5, -47, 9.5), (25, 20, 2), mat=habit_mat, name='veil_nape', inflate=0.12)

    # the furrowed right brow: a tapered block pressing diagonally over the right lens
    B.bone('right_brow', (-1.5, -36.8, -7.6), parent='head', rot=(0, 0, 27), mat=skin_mat)
    lbox('right_brow', (-7.5, -2, -0.95), (8, 3, 1), name='brow_r')

    B.bone('glasses', (0, -36.5, -8.25), parent='head', mat=glasses_mat)
    box('glasses', (-8.5, -40, -8.25), (17, 7, 0), name='glasses',
        decals={'front': pixelart(GLASSES, GPAL, anchor='topleft'),
                'eyes:front': pixelart(GLASSES, GLOWPAL, anchor='topleft')})
    for sx in (-1, 1):
        box('glasses', (8.0 * sx, -38, -8.25), (0, 1, 2), name='temple')

    B.bone('jaw', (0, -31, 2), parent='head', mat=skin_mat)
    fbox('jaw', (-5.5, -31, -6), (11, 4, 9), name='jaw')
    fbox('jaw', (-3.5, -29, -6.75), (7, 2, 1), name='chin')

    # veil wings: drop straight down beside the coif and stop on the capelet (the head stays narrower than the
    # shoulders, with a notch on each side)
    for side, sx in (('right', -1), ('left', 1)):
        vb = f'veil_{side}'
        B.bone(vb, (11.55 * sx, -46, 2), parent='head', mat=habit_mat)
        box(vb, (10.55 * sx - (2 if sx < 0 else 0), -46, -6), (2, 20, 16), name='veil_side')

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
            # long index finger: lies along the top of the pen, straightens for 'Usted.'
            B.bone('right_index', (ax, 6.5, -2.1), parent=hand, rot=(PEN_TILT, 0, 0), mat=hand_mat)
            box('right_index', (ax - 1, 6.5, -3.1), (2, 8, 2), name='finger')
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
    'write': {
        'chest': (0.06, 0, 0, 0, 0, 0),
        'head': (0.24, -0.1, 0.03, 0, 0, 0),
        'veil': (0.09, 0, 0, 0, 0, 0),
        'veil_right': (-0.1, 0, 0, 0, 0, 0),
        'veil_left': (-0.1, 0, 0, 0, 0, 0),
        'left_forearm': (-0.1, 0, 0, 0, 0, 0),
        'book': (-0.36, 0, 0, 0, 0, 0),
    },
    'stare': {
        'body': (-0.04, 0, 0, 0, 0, 0),
        'chest': (-0.06, 0, 0, 0, 0, 0),
        'head': (-0.2, 0, 0.05, 0, 0, 0),
        'glasses': (0, 0, 0, 0, -0.6, 0),
        'right_brow': (0, 0, 0.06, 0, 0, 0),
    },
    'point': {
        'chest': (0, -0.12, 0, 0, 0, 0),
        'head': (0.05, 0.12, 0, 0, 0, 0),
        'jaw': (0.14, 0, 0, 0, 0, 0),
        'right_brow': (0, 0, 0.06, 0, 0, 0),
    },
}

ANIM_NOTES = """(placeholder)"""
