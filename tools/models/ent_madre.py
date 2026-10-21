"""La Madre Remedios Iturbe -- the static apparition of the Mother Superior (DEAD LINE, case 'colegio').

Authored at 2x texel density (model.scale = 0.5).  +Y down, ground y = 24, faces -Z, right_* on -X.  Centred on
x = 0, z = 0 (only the ledger, the arms and the back veil leave the column).  Height 2.3 blocks: crown y = -50 ->
floor y = 24 (74 texels).  See build() for the cube / bone count; texture 256 x 256.

Design (round 4)
----------------
Silhouette: a tall, looming headmistress read as ONE shape -- an arched crown, a veil that flares like a bell
onto dead-square shoulders, a long rigid column, and a habit that bells out onto the floor.  The starched crown is a
flat cap with two sloped shoulders (28 deg, own bones) so the top is an arch, not a lid; the veil wings flare 5 deg
out and fall 6 deg back behind the coif (a trapezoid from the front, the white coif showing in profile); the 35-wide
capelet rides up to the jaw (no neck: the head sits in the shoulders, the column below them is long); the back veil
is two long panels split down the middle, angled out and falling away from the back to a point at the knee; the
four skirt slabs flare 4-6 deg from the belt into a bell that pools on the floor as a thin, ragged, fading hem.  The
chest has no separate bone: the whole column leans from the floor like a statue.
On the black: a graphic WHITE FRAME -- the 3-texel starched forehead band and coif plates box the face, the linen
rounding the window's corners; a starched fold rolls under the chin onto the big flat bib with its black cross.

Face (15 x 17 window, hand-placed pixel art over skull, nose, cheekbones, flush jowls, a hinge jaw and the chin).
Waxy ivory-yellow skin with grey-green shadows in three value groups: lit planes (forehead, nose ridge, cheekbones,
chin -- one 1-texel specular each), a pale mid tone, and the darks (sockets, hollows under the cheekbones, two
nasolabial folds bracketing the mouth, the glabella crease).  ROUND STEEL SPECTACLES on their own plane with OPAQUE
GLOWING lenses (emissive 'eyes' layer): a round hot white disk with a cold crescent on its lower arc, one steel
glint on the upper-outer arc -- light, never eyes.  The scowl / raised-brow gag ("Aja."): her right brow is a heavy
2-row band of grey hair growing out of the skull at 20 deg and crushing the right lens into an angry crescent; the
left brow is a 2-row dark arch raised high over a wide-open lens.  The mouth is a prim pressed line with both
corners turned down.

Props: an open LEDGER (libro de actas, 23 x 19 boards) in oxblood leather whose boards frame the pages with a
1.5-texel border and brass corner caps, gilt title plate, blind-stamped cross, banded spine, red-sprinkled page edges,
ruled pages of handwritten names with red demerit checks, a loose leaf with a big red X and a red ribbon -- cradled on
the left forearm, four bony fingers hooked over the board edge.  A big cartoon FOUNTAIN PEN (black lacquer, gold
bands and clip, gold nib with a red tip) in the right fist (knuckles, finger splits, nails) under a long index finger
that straightens for 'Usted.'.  A pewter ROSARY to the knee with a silver crucifix.  Three iron keys on a ring.

Palette: cold blue-black wool (crisp organ pleats with one lit ridge texel, pale rims on the crown, veil and
capelet edges), cold blue-grey starched linen, waxy ivory skin, oxblood + brass + red ink as the only warm accents.
Translucent (the brief's ~210): habit 212 fading to 60 over the last 12 texels above the floor, capelet 232, veil
226, sleeves 236 (their faces buried in the body are cut so nothing ghosts through), linen 236, skin 248; lenses
opaque and full-bright.
"""
import math

import numpy as np

from mcmodel import Model, hash3, face_light, pick, rot_matrix
from rig import Rig
from paint import hx, mix, pixelart

# ------------------------------------------------------------------ translucency
A_HABIT = 212
A_CAPE = 232           # the starched capelet: the stiffest layer, so the sleeves inside it never ghost through
A_VEIL = 226
A_SLEEVE = 236
A_LINEN = 236
A_SKIN = 248
A_BOOK = 240
A_METAL = 236
A_FLOOR = 60           # the habit fades to this where it meets the floor
FADE_Y0 = 12.0         # ... starting 12 texels above the floor


def A(c, a):
    return (c[0], c[1], c[2], int(a))


def floor_fade(y, a):
    """She does not stand on the floor, she rises out of it: alpha fades over the last 12 texels of the habit."""
    t = max(0.0, min(1.0, (y - FADE_Y0) / (24.0 - FADE_Y0)))
    return int(round(a + (A_FLOOR - a) * t ** 1.3))


# ------------------------------------------------------------------ palettes (hand-picked, hue shifted, cold)
HABIT = [hx(c) for c in ('#020307', '#06080e', '#0b0e16', '#11151f', '#181d29', '#202736', '#2a3245',
                         '#384157', '#4a556d')]
LINEN = [hx(c) for c in ('#1b2230', '#2f3849', '#475265', '#636f82', '#818ea0', '#a0abbb', '#bcc6d2',
                         '#d4dce5', '#e7ecf1', '#f5f7f9')]
# waxy skin: cool grey-green shadows -> pale ivory-yellow lights (#e6e2c8) + one wet-wax specular
SKIN = [hx(c) for c in ('#1f2425', '#2f3634', '#444d49', '#5c655e', '#7a8279', '#9da293', '#bbbca9',
                        '#d2d0ba', '#dfdcc4', '#e8e4ca')]
SPEC = hx('#f7f5e8')
BROW = [hx('#24262b'), hx('#3e4147'), hx('#62656b'), hx('#8a8d92')]
CREASE = hx('#3c4440')
MOUTH_LINE = hx('#1a1517')
OX = [hx(c) for c in ('#140306', '#22060a', '#340a0f', '#4a1015', '#61171b', '#7a2022', '#932d2b', '#ab4239',
                      '#c25e4c')]
BRASS = [hx(c) for c in ('#241906', '#3f2d0c', '#614714', '#866521', '#ab8532', '#cba548', '#e3c46c',
                         '#f3e2a4')]
PAPER = [hx(c) for c in ('#5a5546', '#7b755f', '#9c957b', '#b9b295', '#d0c9ab', '#e1dbc0', '#eee9d4',
                         '#f8f5e6')]
INK = hx('#1d2238')
INK2 = hx('#46507a')
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
LENS_RIM = hx('#cfe0f3')
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


# ------------------------------------------------------------------ hidden-face culling for the arms
# Sleeve faces that stay buried inside the body (core / capelet) in the rest pose AND in every pose are cut, so the
# translucent habit never shows smoky sleeve rectangles behind it.  Boxes are (bone, min, max) in rig-absolute rest
# coordinates of that bone; POSES is read lazily (it is defined further down).
BURY = [('body', (-11.0, -26.0, -6.5), (11.0, 24.0, 6.5)),          # core
        ('body', (-17.5, -29.0, -7.5), (17.5, -19.0, 7.5))]         # capelet
_POSE_W = {}


def _bone_world(bone, pose):
    chain = []
    b = bone
    while b is not None:
        chain.append(b)
        b = b.parent
    M = np.eye(4)
    for b in reversed(chain):
        p = list(pose.get(b.name, ())) + [0.0] * 6
        T = np.eye(4)
        T[:3, 3] = np.array(b.pivot) + np.array(p[3:6])
        R = np.eye(4)
        R[:3, :3] = rot_matrix(*[math.radians(b.rot[i]) + p[i] for i in range(3)])
        M = M @ T @ R
    return M


def _find(bone, name):
    root = bone
    while root.parent is not None:
        root = root.parent
    for b in root.walk():
        if b.name == name:
            return b
    return None


def buried(ctx, margin=0.35):
    """True when this texel sits inside the body volume in the rest pose and in every pose of POSES."""
    poses = [{}] + list(globals().get('POSES', {}).values())
    b = ctx.bone
    key = id(b)
    if key not in _POSE_W:
        mats = []
        for p in poses:
            Wb = _bone_world(b, p)
            boxes = []
            for (bn, lo, hi) in BURY:
                ob = _find(b, bn)
                Wo = _bone_world(ob, p)
                Wo_rest = _bone_world(ob, {})
                # box corners are rest-absolute; convert to that bone's local frame
                boxes.append((np.linalg.inv(Wo), Wo_rest, np.array(lo), np.array(hi)))
            mats.append((Wb, boxes))
        _POSE_W[key] = (np.linalg.inv(_bone_world(b, {})), mats)
    inv_rest, mats = _POSE_W[key]
    lp = inv_rest @ np.array([ctx.pos[0], ctx.pos[1], ctx.pos[2], 1.0])
    for Wb, boxes in mats:
        wp = Wb @ lp
        inside = False
        for inv_o, Wo_rest, lo, hi in boxes:
            q = (Wo_rest @ (inv_o @ wp))[:3]                 # back into the rest-absolute frame of the box's bone
            if np.all(q > lo + margin) and np.all(q < hi - margin):
                inside = True
                break
        if not inside:
            return False
    return True


# ------------------------------------------------------------------ cloth
HIDDEN = {
    # tag -> faces never seen (cut out so nothing ghosts through the translucency)
    'core': ('top', 'bottom'), 'panel': ('top', 'bottom'), 'scap': ('top', 'bottom', 'back'),
    'veil_back': ('top',), 'veil_side': ('bottom',), 'cape': (),
    'veil_nape': ('front', 'bottom'), 'nape_top': ('front', 'bottom', 'top'), 'crown': ('bottom',),
    'chamfer': ('bottom',), 'pool': ('bottom',),
}
VEILS = ('crown', 'chamfer', 'veil_side', 'veil_back', 'veil_nape', 'nape_top')
V_DEPTH = 8.0          # each back-veil panel's hem rises this much from its inner point to its outer edge
FADED = ('core', 'panel', 'scap', 'pool')
SKIRT_INNER = {'skirt_front': 'back', 'skirt_back': 'front', 'skirt_right': 'east', 'skirt_left': 'west'}


def habit_mat(ctx):
    """Starched black wool: crisp organ pleats, lit square edges, pale rims on the crown, veil and capelet."""
    t = tag(ctx)
    f = ctx.face
    if f in HIDDEN.get(t, ()):
        return None
    bn = ctx.bone.name
    if t in ('sleeve_up', 'sleeve_lo', 'cuff') and f in ('west', 'east', 'front', 'back', 'top') and buried(ctx):
        return None                                         # buried in the body in every pose: never seen
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    k = cseed(ctx)
    a = A_VEIL if t in VEILS else (A_SLEEVE if t in ('sleeve_up', 'sleeve_lo', 'cuff') else A_HABIT)
    if t == 'cape':
        a = A_CAPE
    side = f in ('front', 'back', 'west', 'east')
    v = 0.42 + face_light(ctx) * 1.15
    rim = False                                             # pale outer edge that keeps the shape in fog
    if t == 'core':
        return A(pick(HABIT, 0.1), floor_fade(ctx.y, a))
    if t == 'panel' and f == SKIRT_INNER.get(bn):
        return A(HABIT[1], floor_fade(ctx.y, a))            # inside of the bell: dark wool, never a hole
    if t == 'pool':                                         # the hem pooled on the floor: thin, ragged, darker
        if f == 'top':
            ex = min(lx, w - lx)
            ez = min(lz, d - lz)
            if ex < 1.0 or ez < 1.0:
                if hash3(int(lx), 0, int(lz), 91) > 0.45:
                    return None                             # ragged outline
            if (ex < 2.5 and ez < 2.5) and hash3(int(lx), 1, int(lz), 92) > 0.25:
                return None                                 # cut corners
            v = 0.3 + pleat(lx if ez < ex else lz, 2, 5) * 0.4
        elif side:
            u = around(ctx)
            if hash3(int(u), 3, 0, 93) > 0.6:
                return None
            v = 0.3 + pleat(u, 2, 5) * 0.5
        return A(pick(HABIT, v), floor_fade(ctx.y, a))
    if t == 'panel':
        if side:
            v += pleat(around(ctx), k % 7, 5)
            v += 0.05 - ly / h * 0.14                       # a touch lighter at the waist, darker to the floor
            if f == 'front' and bn == 'skirt_front' and int(lx) % 8 == 3 and ly > 2:
                v -= 0.1                                    # seams
    elif t == 'scap':
        v += 0.06
        if f == 'front' and ctx.i in (0, ctx.w - 1):
            v += 0.12                                       # turned edges of the scapular
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
    elif t == 'veil_back':                                  # two long back panels, each ending in a point
        inner_at_w = bn == 'veil_back_right'                # the right panel's inner (centre) edge is at lx = w
        di = (w - lx) if inner_at_w else lx                 # distance from the centre split
        if f in ('west', 'east'):
            di = 0.0 if ((f == 'east') == inner_at_w) else float(w)
        hem = h - V_DEPTH * (di / w) ** 1.25
        if ly > hem + 1e-6:
            return None
        to_hem = hem - ly
        if side:
            v += pleat(around(ctx), k % 9, 6) * 0.7
        if to_hem < 1.0:
            rim = True
        if f == 'back':
            if ly < 2.0:
                v -= 0.1                                    # shadow under the nape
            if di < 1.0:
                v -= 0.12                                   # the split down the middle
            if di > w - 1.0:
                rim = True                                  # outer edge
        if f in ('west', 'east') and ctx.i == ctx.w - 1:
            rim = True
        a = A_VEIL - int(max(0.0, 5.0 - to_hem) * 14)       # the veil thins out towards its point
        a = floor_fade(ctx.y, a)
    elif t in ('veil_side', 'veil_nape', 'nape_top') and side:
        v += pleat(around(ctx), k % 9, 6) * 0.8
        if t == 'veil_side':
            if f in ('front', 'back') and (ctx.i in (0, ctx.w - 1)):
                rim = True
            if h - ly < 1.0:
                rim = True                                  # lower edge lying on the capelet
            outer = (f == 'west' and ctx.x < 0) or (f == 'east' and ctx.x > 0)
            if outer and ctx.i == 0 and f == 'west' or outer and ctx.i == ctx.w - 1 and f == 'east':
                rim = True
        elif f == 'back' and ctx.i in (0, ctx.w - 1):
            rim = True
    elif t in ('sleeve_up', 'sleeve_lo') and f in ('top', 'bottom'):
        return A(HABIT[1], a)                               # sleeve ends: dark wool interior, never a hole
    elif t in ('sleeve_up', 'sleeve_lo', 'cuff') and side:
        v += pleat(around(ctx), k % 4, 7) * 0.5
        if t == 'sleeve_up' and ly > h - 3:
            v -= 0.05                                       # elbow creases
            if (ctx.i + int(ly)) % 4 == 0:
                v -= 0.08
    if t == 'veil_side' and f == 'top':
        v += 0.1
    if t in ('crown', 'chamfer'):                           # the starched crown: flat cap + sloped shoulders
        if f == 'top':
            v = 0.5
            if t == 'crown':
                v += pleat(lx, 3, 6) * 0.25                 # starched folds running front to back
                if abs(lx - w / 2) < 0.6:
                    v -= 0.08                               # centre seam of the veil
            if ctx.j == ctx.h - 1:
                v += 0.22                                   # the brim lip over the forehead catches the light
        elif f == 'front':
            v = 0.4
            if ctx.j == ctx.h - 1:
                rim = True                                  # the brim edge over the white band
            elif ctx.j == 0:
                v += 0.14
        elif side:
            if ctx.j == 0:
                rim = True
    if t == 'cuff' and f == 'bottom':
        return A(HABIT[0], 255)                             # pitch black inside of the bell sleeve
    if edge(ctx) == 0 and side and min(ctx.w, ctx.h) > 2 and not rim:
        v -= 0.06
    if side and t in ('panel', 'scap') and ly < 2.5 and bn.startswith('skirt'):
        v -= 0.1 - ly * 0.03                                # occlusion under the belt
    if rim:
        v = max(v, 0.62) + 0.2
    c = pick(HABIT, v)
    if side and v > 0.6:
        c = mix(c, hx('#5d6b8a'), 0.2)                      # cold sheen on the lit ridges and rims
    if t == 'cuff' and side and h - ly < 1.0:
        c = mix(c, HABIT[7], 0.55)                          # rolled edge of the bell
    if t in FADED:
        a = floor_fade(ctx.y, a)
    return A(c, a)


def belt_mat(ctx):
    if ctx.face in ('top', 'bottom'):
        return None
    v = 0.45 + face_light(ctx) * 1.1
    if ctx.j in (0, ctx.h - 1):
        v -= 0.2
    if ctx.j == ctx.h // 2 and ctx.i % 3 == 1:
        v += 0.14                                           # tooled stitch line
    return A(pick(BELT, v), A_HABIT + 14)


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
    if t == 'bib' and f in ('back', 'bottom', 'west', 'east', 'top'):
        return None                                         # the top is under the chin fold / jaw
    if t == 'coif_side' and f in ('top', 'bottom'):
        return None
    if t == 'chinfold' and f in ('back', 'bottom'):
        return None
    if t == 'band' and f in ('top', 'back'):
        return None                                         # always under the crown / inside the veil
    v = 0.74 + face_light(ctx) * 0.9
    if f in ('west', 'east'):
        v -= 0.12
    elif f == 'back':
        v -= 0.28
    if t == 'band':
        if f == 'front':
            v += 0.06 if ctx.j == 1 else -0.02              # one ironed tuck across the forehead
            if ctx.j == ctx.h - 1:
                v -= 0.18                                   # rolls under onto the forehead
            v -= (abs(lx - w / 2) / (w / 2)) ** 2 * 0.1     # curves round the skull
        elif f == 'bottom':
            v = 0.45
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
# the furrowed right brow block (7 x 2 front face; i = 0 the tail out by the temple, i = 6 the knot by the nose):
# grey-black hair with ONE lit top-edge row, darkening into the knot; the flesh ridge is only on its underside.
BROWART = [
    "..lllbB",
    "bbbbbBB",
]
BROWPAL = {'l': BROW[2], 'b': BROW[1], 'B': BROW[0], '.': None}


def skin_mat(ctx):
    """Waxy yellow-grey skin.  The face is hand-placed pixel art (FACE decals); this paints the rest."""
    t = tag(ctx)
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    if t == 'skull' and f in ('top', 'west', 'east'):
        return None                                         # always under the coif / veil
    if t == 'skull' and f == 'back':
        return A(HABIT[1], 255)                             # opaque: the face never ghosts through the veil
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
            if lz < 0.6:
                return A(SKIN[4], A_SKIN)                   # the lip of the cheek next to the mouth corner
            return A(MOUTH[1], 255)                         # inside of the cheek, seen when the jaw drops
        if f != 'front':
            return None
    if t == 'chin' and f in ('bottom', 'back'):
        return None
    if t == 'chin' and f == 'top':
        return A(SKIN[5], A_SKIN)                           # no lit ledge under the lip
    if t == 'chin' and f in ('west', 'east'):
        return A(SKIN[5], A_SKIN)
    if t == 'cheek':
        if f == 'back' or (f == 'bottom' and lz > 0.5):
            return None
        if f == 'bottom':
            return A(SKIN[4], A_SKIN)                       # the hollow under the cheekbone
        if (f == 'west' and ctx.x < 0) or (f == 'east' and ctx.x > 0):
            return None                                     # pressed against the coif
        if f == 'top':
            return A(SKIN[6], A_SKIN)
        inner = (f == 'east' and ctx.x < 0) or (f == 'west' and ctx.x > 0)
        if inner:
            return A(SKIN[5], A_SKIN)
        if f != 'front':
            return A(SKIN[6], A_SKIN)
    if t == 'nose':
        if f == 'back':
            return None
        if f == 'bottom':
            cx = lx - w / 2
            if abs(cx) > 0.4 and lz < d - 0.6:
                return A(CREASE, A_SKIN)                    # nostrils
            return A(SKIN[4], A_SKIN)
        if f in ('west', 'east'):
            lit = (f == 'west')
            return A(SKIN[7] if lit else SKIN[5], A_SKIN)
        if f == 'top':
            return A(SKIN[7], A_SKIN)
    if t == 'brow_r':
        if f == 'back':
            return None
        ch = BROWART[min(ctx.j, 1)][min(ctx.i, 6)] if f == 'front' else None
        if f == 'front':
            return A(BROWPAL[ch], A_SKIN) if ch != '.' else None    # the tail tapers to one row
        if f == 'top':
            if lx < 2.0:
                return None                                 # over the tapered tail
            return A(BROW[1] if lz < 1.0 else BROW[0], A_SKIN)   # hair seen from above (no lit plank)
        if f == 'west':
            return A(BROW[1], A_SKIN) if ly > 1.0 else None
        if f == 'bottom':
            return A(SKIN[4] if lz < 1.2 else SKIN[3], A_SKIN)   # the flesh ridge under the hairs
        return A(BROW[0] if f == 'east' else BROW[1], A_SKIN)

    v = 0.66 + face_light(ctx) * 0.9
    if f in ('west', 'east'):
        v -= 0.12
    if f == 'back':
        v -= 0.25
    return A(pick(SKIN, v), A_SKIN)


def hand_mat(ctx):
    """Old waxy hands: lit knuckle ridge, dark finger splits, pale nails, cold veins and a few age spots."""
    t = tag(ctx)
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    v = 0.66 + face_light(ctx) * 1.0
    if t == 'fist':
        # the fist holding the pen: back of the hand on the west face, the four curled fingers on the front
        # face (knuckle row, then finger segments split by dark lines), fingertips + nails on the palm side (east)
        if f == 'top':
            return A(SKIN[6], A_SKIN)
        if f == 'bottom':
            return A(SKIN[5] if ctx.i % 2 else SKIN[7], A_SKIN)    # the curled little finger end
        if ly < 1.0:
            return A(SKIN[4], A_SKIN)                       # shadow under the cuff
        if f == 'front':
            col = int(lx)
            if ly < 2.0:
                return A(SKIN[8] if col % 2 == 0 else SKIN[6], A_SKIN)       # knuckles
            if col == 1 or col == 3:
                return A(SKIN[3], A_SKIN)                   # finger splits
            return A(SKIN[7] if ly < 4.0 else SKIN[6], A_SKIN)
        if f == 'west':
            if 1.0 <= ly < 2.0:
                return A(SPEC if ctx.i == 1 else SKIN[8], A_SKIN)              # knuckle highlight
            if ly >= 2.0 and ctx.i % 2 == 1:
                return A(SKIN[4], A_SKIN)
            c = pick(SKIN, 0.62)
            if ly < 2.0 and (ctx.i * 7 + cseed(ctx)) % 5 == 0:
                c = mix(c, hx('#5d6a78'), 0.4)              # cold veins
            return A(c, A_SKIN)
        if f == 'east':
            if lz < 1.0 and ly >= 2.0:
                return A(SKIN[9] if int(ly) % 2 == 0 else SKIN[3], A_SKIN)     # nails of the curled fingers
            return A(SKIN[5], A_SKIN)
        if f == 'back':
            return A(SKIN[5] if int(lx) % 2 else SKIN[6], A_SKIN)
    if t in ('palm',):
        if f in ('front', 'back', 'west', 'east') and ly < 1.0:
            v -= 0.15                                       # shadow under the cuff
        c = pick(SKIN, v)
        if f in ('west', 'east') and 1.5 < ly < h - 2 and (ctx.i * 7 + ctx.j * 3 + cseed(ctx)) % 11 == 0:
            c = mix(c, hx('#5d6a78'), 0.4)                  # cold veins
        if (ctx.i * 5 + ctx.j * 11 + cseed(ctx)) % 23 == 0:
            c = mix(c, hx('#6a5a3c'), 0.45)                 # age spots
        return A(c, A_SKIN)
    if t == 'lfinger':                                      # a bony fingertip lying over the page edge
        if f in ('bottom', 'east'):
            return None                                     # lies on the page / grows out of the knuckles
        if f == 'west' or (f == 'top' and lx < 1.0):
            return A(SKIN[9] if f == 'top' else SKIN[8], A_SKIN)   # pale nail at the tip
        if f == 'top':
            return A(SKIN[5] if abs(lx - 2.0) < 0.5 else SKIN[7], A_SKIN)   # knuckle crease, lit phalanx
        return A(SKIN[4], A_SKIN)                           # sides: dark splits between the fingers
    if t == 'lknuckles':                                    # the bent knuckles hooked round the board edge
        z = int(lz)
        gap = z % 2 == 1
        if f == 'top':
            return A(SKIN[3] if gap else (SPEC if lx > 1.0 and z == 2 else SKIN[8]), A_SKIN)
        if f == 'east':                                     # backs of the fingers, then the back of the hand
            if ly < 2.0:
                return A(SKIN[3] if gap else SKIN[7], A_SKIN)
            c = pick(SKIN, 0.62 - (ly - 2.0) * 0.03)
            if (z * 3 + int(ly)) % 5 == 0:
                c = mix(c, hx('#5d6a78'), 0.35)             # cold veins
            return A(c, A_SKIN)
        if f == 'west':
            return A(SKIN[3] if gap else SKIN[5], A_SKIN)
        if f == 'bottom':
            return A(SKIN[4], A_SKIN)
        return A(SKIN[5], A_SKIN)
    if t in ('finger', 'thumb'):
        if ly > h - 1.0 and f in ('front', 'west', 'east', 'back'):
            return A(SKIN[9], A_SKIN)                       # pale nail
        if f == 'bottom':
            return A(SKIN[8], A_SKIN)                       # fingertip
        if f == 'top':
            return A(SKIN[5], A_SKIN)
        if t == 'finger' and (abs(ly - 3.5) < 0.5 or abs(ly - 6.5) < 0.5):
            v -= 0.16                                       # knuckle creases
        if t == 'finger' and f == 'west' and (abs(ly - 2.5) < 0.5 or abs(ly - 5.5) < 0.5):
            v += 0.1                                        # knuckle highlights
        if f in ('west', 'east'):
            v -= 0.06
    return A(pick(SKIN, v), A_SKIN)


# ------------------------------------------------------------------ the face mask
# 15 columns (x -7.5..7.5, col c <-> x = c - 7), 17 rows (row r <-> y = -44.5 + r, y -45..-28).
# Skull rows r0..r12, jaw rows r13..r16 (jaw cols 2..12, the flush jowls hold cols 0-1 / 13-14).  The spectacles
# (own plane) hide r4..r10 except the nose strip and the rim corners (dark sockets).  The right brow is its own cube.
# Three value groups: lit 7-9 + 'w' (one specular each on forehead, nose ridge, cheekbones, chin), mid 5-6,
# darks 2-4 + 'k' creases + 'K' the pressed mouth.  'b'/'B': the raised LEFT brow, a 2-row dark arch.  'L': the
# starched linen rounding the corners of the window (the wimple wraps the jaw, so the face is not a flat screen).
GX0, GY0 = -7.5, -45
FACE = [
    # 012345678901234
    "L5555555555555L",   # r0  y-45 soft shadow where the band rolls under
    "567w7777777bbb5",   # r1  y-44 forehead (specular) | the left arch peaks high
    "5677777767bBBBb",   # r2  y-43 | the arch: lit-grey upper row, black lower row
    "456666k66bB666B",   # r3  y-42 glabella crease by the knot of the right brow | arch ends drop over an open lid
    "333332565233333",   # r4  y-41 nose root between the rims, dark sockets round them
    "333332675233333",   # r5  long nose (own cube, cols 6..8): lit west side, shadowed east
    "333332685233333",   # r6  (bridge)
    "333332785233333",   # r7
    "3333327w5233333",   # r8  aquiline bump with its specular
    "333332685233333",   # r9
    "333333674333333",   # r10
    "5w876k574k678w5",   # r11 y-34 cheekbones (own cubes, specular each) | the folds start at the nose wings
    "4555k65456k5554",   # r12 y-33 hollows under the cheekbones, shadow under the nose
    "455k6KKKKK6k554",   # r13 y-32 ONE pressed line (jaw top row), the folds bracket it
    "4555k55555k5554",   # r14 y-31 both corners turned down, the pressed lower lip in shadow: an arc of disapproval
    "L5566666666655L",   # r15 y-30 shadow under the lip; the wimple rounds the jaw
    "LL56788w88765LL",   # r16 y-29 hard lit chin with its specular
]
assert all(len(r) == 15 for r in FACE), [len(r) for r in FACE]

FPAL = {str(i): A(SKIN[i], A_SKIN) for i in range(10)}
FPAL.update({'k': A(CREASE, A_SKIN), 'K': A(MOUTH_LINE, A_SKIN), 'w': A(SPEC, A_SKIN), 'L': A(LINEN[7], A_LINEN),
             'b': A(BROW[2], A_SKIN), 'B': A(BROW[0], A_SKIN)})


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


# spectacles: two round 7 x 7 rims + a 3-texel bridge = 17 x 7 (x -8.5..8.5, y -41..-34) on a plane in front of the
# nose.  A thin 1-texel STEEL ring with one glint on its upper-outer arc; the lenses glow: a round hot white disk
# with a cold crescent along its lower arc, so they read ROUND and as light, not as eyeballs.
RING = [
    "..SSS..",
    ".SWWWS.",
    "SWWWWWS",
    "SWWWWWS",
    "SWWWWVS",
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
GLOWPAL = {'W': (255, 255, 255, 255), 'V': (196, 220, 246, 255)}


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
        if f == 'top':
            return None                                     # lies against the boards
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
    elif f == 'top' and t == 'cover':
        e = min(lx, w - lx, lz, d - lz)
        v += 0.06
        if e < 1.0:
            v += 0.12                                       # the board's rounded lip catches the light
        elif e < 1.6 and (int(lx) + int(lz)) % 2 == 0:
            v -= 0.12                                       # blind-tooled line framing the pages
    elif f == 'top':
        v += 0.04
    return A(pick(OX, v), A_BOOK)


# the big red X of the loose leaf
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
        if row % 3 == 2:
            c = mix(c, RULE, 0.4)                           # ruled baseline under each entry
        if col == margin and t != 'leaf':
            c = mix(c, RED_INK2, 0.55)
        if t == 'leaf':
            # a fresh entry with a big red X over it
            if row % 3 == 1 and 1 <= col <= w - 2 and hash3(col, row, 7, 66) > 0.4 and col % 3 != 0:
                c = INK2
            gx, gy = col - (w - 7) // 2, row - (d - 7) // 2 - 1
            if 0 <= gy < 7 and 0 <= gx < 7 and BIGX[gy][gx] == 'R':
                c = RED_INK2 if (gx + gy) % 5 else RED_INK
            return A(c, A_BOOK)
        # handwritten surnames: a dark capital (with its ascender on the row above), then thin, lighter strokes
        # broken by 1-texel gaps, varied lengths; most entries end in a red demerit tick
        n = row // 3 + (0 if right else 11)
        x0 = 0 if right else 2
        ln = 4 + int(hash3(n, 1, 0, 61) * 3)                # 4..6
        k = col - x0
        if row % 3 == 1 and 0 <= k < ln:
            if k == 0:
                c = INK
            elif (k + int(hash3(n, 5, 0, 65) * 2)) % 3 != 0 and hash3(col, row, n, 62) > 0.12:
                c = INK2 if (k + n) % 4 else mix(INK2, INK, 0.5)
        if row % 3 == 0 and k == 0 and row > 0:
            c = mix(c, INK2, 0.7)                           # the capital's ascender
        if hash3(n, 2, 0, 64) > 0.3:
            gx = col - min(x0 + ln + 1, w - 3)
            if (row % 3 == 1 and gx == 1) or (row % 3 == 2 and gx == 0):
                c = RED_INK2 if gx == 1 else RED_INK        # thin red tick
        return A(c, A_BOOK)
    if f == 'bottom':
        return None                                         # lies on the board
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
    "...oGBBo...",
    "GAA.B.B.CCg",
    "A.A.BBB.C.C",
    "AAA..b..CCC",
    ".a...b...c.",
    ".a...b...c.",
    ".a...b...c.",
    "a....bb...c",
    "a....b....c",
    "aa...bb..cc",
    "a....b.....",
    ".....b.....",
]
assert all(len(r) == 11 for r in KEYS)
KPAL = {'A': A(IRON[4], A_METAL), 'B': A(IRON[5], A_METAL), 'C': A(IRON[4], A_METAL),
        'a': A(IRON[3], A_METAL), 'b': A(IRON[4], A_METAL), 'c': A(IRON[3], A_METAL),
        'G': A(IRON[6], A_METAL), 'g': A(IRON[5], A_METAL), 'o': A(IRON[3], A_METAL)}
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
    'right': ((-28.77, 13.12, -2.49), (-109.52, -37.49, 0), (75.71, 30.76, -14.18)),
    'left': ((-11.8, 12.58, -12.63), (-32.81, 3.72, 0), (-48.71, -34.55, -17.93)),
}
CROWN_SLOPE = 28        # deg, the crown's sloped shoulders
WING_FLARE = 5          # deg, the veil wings open towards the shoulders
WING_BACK = 6           # deg, ... and fall back behind the coif in profile
SKIRT_FLARE = (4, 6)    # deg, front/back and side slabs of the bell
BACK_VEIL = (3, 4, 3)   # deg: falls away from the back, folds along the split, flares out


def build():
    _POSE_W.clear()
    B = Builder()
    box, lbox = B.box, B.lbox

    def fbox(bone_, frm, size, mat=skin_mat, name=None):
        return box(bone_, frm, size, mat=mat, name=name, decals=face_decals(frm[0], frm[1], size[0], size[1]))

    # ---------------- body: root ON THE FLOOR -- the rigid column (no separate chest bone) tilts from the hem
    B.bone('body', (0, 24, 0), mat=habit_mat)
    box('body', (-11, -26, -6.5), (22, 50, 13), name='core')
    box('body', (-12.5, -10, -8.5), (25, 3, 17), mat=belt_mat, name='belt', inflate=0.15)
    box('body', (-16.5, 23, -12.5), (33, 1, 25), name='pool')          # the hem pooled on the floor, ragged
    # square shoulders: a rigid 35-wide capelet, the big white bib and the black pectoral cross
    box('body', (-17.5, -29, -7.5), (35, 10, 15), name='cape')
    box('body', (-9.5, -28, -8.5), (19, 16, 12), mat=linen_mat, name='bib')
    box('body', (-1, -23, -9.3), (2, 8, 1), mat=ebony_mat, name='cross')
    box('body', (-2.5, -21, -9.45), (5, 2, 1), mat=ebony_mat, name='cross')

    # ---------------- the bell: four stiff slabs flaring from the belt to the floor
    ff, fs = SKIRT_FLARE
    B.bone('skirt_front', (0, -8, -6), parent='body', rot=(-ff, 0, 0), mat=habit_mat)
    box('skirt_front', (-12, -8, -8), (24, 32, 4), name='panel')
    box('skirt_front', (-6, -7, -9), (12, 31, 1), name='scap')
    B.bone('skirt_back', (0, -8, 6), parent='body', rot=(ff, 0, 0), mat=habit_mat)
    box('skirt_back', (-12, -8, 4), (24, 32, 4), name='panel')
    for side, sx in (('right', -1), ('left', 1)):
        sb = f'skirt_{side}'
        B.bone(sb, (11 * sx, -8, 0), parent='body', rot=(0, 0, -fs * sx), mat=habit_mat)
        box(sb, ((8.5 if sx > 0 else -12.5), -8, -7.5), (4, 32, 15), name='panel')
    # three iron keys fanned on an iron ring at the left hip (ride the flaring side slab)
    box('skirt_left', (12.6, -8, -3), (1, 4, 4), mat=ring_mat, name='ring')
    box('skirt_left', (12.8, -6, -6), (0, 14, 11), mat=keys_mat, name='keys',
        decals={'east': pixelart(KEYS, KPAL, anchor='topleft')})

    # rosary: a link into the belt, pewter beads down the front slab to the knee, silver crucifix
    B.bone('rosary', (-7.5, -8.5, -9.2), parent='body', rot=(-6.5, 0, 2), mat=bead_mat)
    box('rosary', (-8, -10.5, -9.2), (1, 3, 1), name='link')
    box('rosary', (-8.5, -8, -10.4), (2, 13, 2), name='beads')
    box('rosary', (-8.5, 5, -9.9), (2, 2, 1), mat=silver_mat, name='medal')
    box('rosary', (-8.5, 7, -9.9), (2, 7, 1), mat=silver_mat, name='crux')
    box('rosary', (-10.5, 8.5, -10.05), (6, 2, 1), mat=silver_mat, name='crux')

    # ---------------- back veil: two long panels split down the middle, tucked into the nape at neck height,
    # lying on the capelet, angled out and falling away to a point at the knee
    bx, by, bz = BACK_VEIL
    B.bone('veil_back_right', (0, -32, 8.3), parent='body', rot=(bx, -by, bz), mat=habit_mat)
    lbox('veil_back_right', (-11.5, 0, -1), (12, 40, 2), name='veil_back')
    B.bone('veil_back_left', (0, -32, 8.55), parent='body', rot=(bx, by, -bz), mat=habit_mat)
    lbox('veil_back_left', (-0.5, 0, -1), (12, 40, 2), name='veil_back')

    # ---------------- head: crown -50..-48, band -48..-45, face window x -7.5..7.5 / y -45..-28
    B.bone('head', (0, -28, 0), parent='body', mat=skin_mat)
    fbox('head', (-7.5, -48, -6), (15, 16, 12), name='skull')
    fbox('head', (-1.5, -40, -7.5), (3, 7, 2), name='nose')
    fbox('head', (-7.5, -34, -6.5), (4, 2, 1), name='cheek')
    fbox('head', (3.5, -34, -6.5), (4, 2, 1), name='cheek')
    fbox('head', (-7.5, -32, -6), (2, 4, 6), name='jowl')
    fbox('head', (5.5, -32, -6), (2, 4, 6), name='jowl')
    box('head', (-10.5, -48, -7), (21, 3, 14), mat=linen_mat, name='band')
    box('head', (-10.5, -45, -7), (3, 19, 13), mat=linen_mat, name='coif_side')
    box('head', (7.5, -45, -7), (3, 19, 13), mat=linen_mat, name='coif_side')
    box('head', (-8.5, -28, -9.5), (17, 2, 3), mat=linen_mat, name='chinfold')
    box('head', (-7.5, -50, -9), (15, 2, 19), mat=habit_mat, name='crown')
    box('head', (-9, -48, 6.5), (18, 3, 3), mat=habit_mat, name='nape_top')
    box('head', (-12.5, -46, 6.75), (25, 20, 3), mat=habit_mat, name='veil_nape')
    # the crown's sloped shoulders: the top of the head is an arch, not a lid
    for side, sx in (('right', -1), ('left', 1)):
        cb = f'crown_{side}'
        B.bone(cb, (7.5 * sx, -50, 0), parent='head', rot=(0, 0, CROWN_SLOPE * sx), mat=habit_mat)
        lbox(cb, ((-7 if sx < 0 else 0), 0, -8.5), (7, 3, 19), name='chamfer')

    # the furrowed right brow: a heavy band of grey hair growing out of the skull, crushing the right lens
    B.bone('right_brow', (-0.4, -38.0, -7.0), parent='head', rot=(0, 0, 20), mat=skin_mat)
    lbox('right_brow', (-7, -2, -1), (7, 2, 2), name='brow_r')

    B.bone('glasses', (0, -37.5, -7.75), parent='head', mat=glasses_mat)
    box('glasses', (-8.5, -41, -7.75), (17, 7, 0), name='glasses',
        decals={'front': pixelart(GLASSES, GPAL, anchor='topleft'),
                'eyes:front': pixelart(GLASSES, GLOWPAL, anchor='topleft')})
    for sx in (-1, 1):
        box('glasses', (8.0 * sx, -39, -7.75), (0, 1, 2), name='temple')

    B.bone('jaw', (0, -32, 2), parent='head', mat=skin_mat)
    fbox('jaw', (-5.5, -32, -6), (11, 4, 9), name='jaw')
    fbox('jaw', (-3.5, -30, -6.75), (7, 2, 1), name='chin')

    # veil wings: flare out from the crown onto the capelet -- a trapezoid falling onto the shoulders
    for side, sx in (('right', -1), ('left', 1)):
        vb = f'veil_{side}'
        B.bone(vb, (11.5 * sx, -46, 2), parent='head', rot=(WING_BACK, 0, -WING_FLARE * sx), mat=habit_mat)
        box(vb, (10.5 * sx - (2 if sx < 0 else 0), -46, -6), (2, 20, 16), name='veil_side')

    # ---------------- arms (authored hanging, bent by the bone rotations); upper arms come out under the cape
    for side, sx in (('right', -1), ('left', 1)):
        arm, fa, hand = f'{side}_arm', f'{side}_forearm', f'{side}_hand'
        ax = 12.5 * sx
        B.bone(arm, (ax, -24, 0), parent='body', rot=ARM_REST[side][0], mat=habit_mat)
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
            box(hand, (ax - 2.3, 1.5, -2.6), (1, 3, 1), inflate=0.3, name='thumb')

    # ---------------- ledger cradled on the left forearm, pages tipped towards the viewer; the boards overhang the
    # page block by 1.5 texels all round so an oxblood frame with brass corners surrounds the pages
    B.bone('book', BOOK_PIVOT, parent='left_forearm', world=True, wrot=BOOK_WROT, mat=leather_mat)
    lbox('book', (-11.5, 0, -9.5), (23, 1, 19), name='cover')
    lbox('book', (-2, 1, -9.5), (4, 1, 19), name='spine')
    lbox('book', (-10, -2, -8), (9, 2, 16), mat=page_mat, name='pages_r')
    lbox('book', (1, -2, -8), (9, 2, 16), mat=page_mat, name='pages_l')
    lbox('book', (-1, -1, -8), (2, 1, 16), mat=page_mat, name='gutter')
    for cx in (-11.5, 9.5):
        for cz in (-9.5, 7.5):
            lbox('book', (cx, 0.2, cz), (2, 1, 2), mat=brass_mat, inflate=0.3, name='corner')
    lbox('book', (-0.5, -1.0, -9.6), (1, 6, 0), mat=ribbon_mat, name='ribbon')
    lbox('book', (1.1, -2.15, -7.5), (8, 0, 15), mat=page_mat, name='leaf')
    # the left hand's four bony fingers hooked over the outer board edge onto the pages
    for fz, fl in ((-3, 3), (-1, 4), (1, 3), (3, 2)):          # index, middle, ring, little finger
        lbox('book', (10.5 - fl, -3, fz), (fl, 1, 1), mat=hand_mat, name='lfinger')
    lbox('book', (10.5, -3, -3), (2, 5, 7), mat=hand_mat, name='lknuckles')

    m = Model('madre', 256, 256, B.r.roots)
    m.scale = 0.5
    m.render_type = 'entityTranslucent'
    return m


POSES = {
    # 'Aja.' -- head bowed over the ledger, book tipped back towards her, nib ON the right-hand page
    'write': {
        'head': (0.26, -0.1, 0.03, 0, 0, 0),
        'veil_right': (-0.221, 0, 0, 0, 0, 0),
        'veil_left': (-0.221, 0, 0, 0, 0, 0),
        'veil_back_right': (0, 0, 0, 0, 0, -0.52),
        'veil_back_left': (0, 0, 0, 0, 0, -0.52),
        'left_forearm': (-0.1, 0, 0, 0, 0, 0),
        'book': (-0.36, 0, 0, 0, 0, 0),
        'right_arm': (0.169, 0.066, -0.063, 0, 0, 0),
        'right_forearm': (0.025, 0.067, 0, 0, 0, 0),
        'right_hand': (0.003, 0.138, 0.030, 0, 0, 0),
    },
    # chin up, looking down her nose at you: the rigid column rocks back on the back edge of its hem, the head
    # tips further back, the spectacles are pushed up the nose (the pen stays poised over the ledger)
    'stare': {
        'body': (-0.06, 0, 0, 0, -0.75, 0),
        'head': (-0.3, 0, 0.05, 0, 0, 0),
        'veil_right': (0.255, 0, 0, 0, 0, 0),
        'veil_left': (0.255, 0, 0, 0, 0, 0),
        'glasses': (0, 0, 0, 0, -0.8, 0),
        'right_brow': (0, 0, 0.06, 0, 0, 0),
    },
    # 'Usted.' -- right shoulder forward, arm raised to shoulder height, elbow almost straight, the long index finger
    # aimed straight at the player's eyes (world dir ~ (0.10, -0.10, -0.99)); the pen turned back along the inside
    # of the wrist so the finger is the only spike; she leans into it with the mouth open on the word
    'point': {
        'body': (0, -0.12, 0, 0, 0, 0),
        'head': (0.05, 0.12, 0, 0, 0, 0),
        'veil_right': (-0.0425, 0, 0, 0, 0, 0),
        'veil_left': (-0.0425, 0, 0, 0, 0, 0),
        'veil_back_right': (0, 0, 0, 0, 0, -0.1),
        'veil_back_left': (0, 0, 0, 0, 0, -0.1),
        'jaw': (0.14, 0, 0, 0, 0, 0),
        'right_brow': (0, 0, 0.06, 0, 0, 0),
        'left_arm': (-0.08, 0, 0, 0, 0, 0),
        'right_arm': (-0.833, -0.199, 0.045, 0, 0, 0),
        'right_forearm': (1.695, 0.641, 0, 0, 0, 0),
        'right_hand': (-1.440, -0.522, 0.240, 0, 0, 0),
        'right_index': (-0.5236, 0, 0, 0, 0, 0),
        'pen': (2.736, -0.001, 0.007, 1.74, -4.472, -0.595),
    },
}

ANIM_NOTES = """
La Madre Remedios -- animation contract.  Angles in radians, ADDED to the rest pose; offsets (dx, dy, dz) in model
texels at 2x density (inside scale_root: 2 texels = 1 vanilla pixel), in the PARENT bone's space.  t = ageInTicks.
Poses (exported as POSE_WRITE / POSE_STARE / POSE_POINT): write, stare, point -- every value quoted below is the one
in the POSES table.  25 bones; there is NO chest bone: the whole rigid column (capelet, bib, arms, head, back veil)
hangs from `body`, which stands on the floor.

CHARACTER: a static apparition.  She NEVER walks, bobs or floats: the hem stays on the floor and the column stays
rigid.  All motion is small, slow and deliberate (max ~0.05 rad/tick) -- EXCEPT that she is always already facing
you: while the player is not looking at her, snap body yRot to face the player in one tick (statue logic).

RENDER: entityTranslucent; alpha is baked into the texture (habit 212, capelet 232, veil 226, sleeves 236 with every
face that stays buried in the body cut away, linen 236, skin 248, ledger 240, metal 236; pen, lenses, mouth and the
back of the skull 255).  The habit FADES to alpha 60 over the last 12 texels above the floor (core, skirt slabs,
scapular, the ragged hem pool, the tips of the back veil): she rises out of the floor instead of standing on it --
do not add a shadow under her.  Multiply a cold tint (0.86, 0.93, 1.0).  The 'eyes' layer (the two lenses: a round
hot white disk with a cold crescent along its lower arc) renders full-bright on top; pulse its alpha 0.85..1.0 with
sin(t*0.05) and spike to 1.0 on every "Aja.".  The right_brow block sits in front of the right lens, so that lens
always glows as an angry crescent.
APPEAR: global alpha 0 -> 1 over 8 ticks with a 2-tick flicker at 50 %; the skirt slabs and veil wings flare out
(+0.06) and settle over 10 ticks as if a door had opened.  VANISH: alpha 1 -> 0 over 6 ticks, eyes layer last.

VEIL RULE (applies to every head pitch, posed or tracked).  h = the head's own xRot offset (pose + tracking; the
body's pitch does not count -- the back veil and the head both hang from the body).  Add
    veil_right xRot = veil_left xRot = -0.85 * h
    veil_back_right dz = veil_back_left dz = -2.0 * max(h, 0)        (a translation, in texels)
The pose tables follow this rule: write (h = 0.26) -> wings -0.221, back veil dz -0.52; stare (h = -0.3) -> wings
+0.255, back veil 0; point (h = 0.05) -> wings -0.0425, back veil dz -0.1.  Measured on the model over h = -0.3..+0.35:
the wings' lower edge never lifts off the capelet (0.06 texel at worst) and the top of the back veil, tucked 6 texels
up inside the nape at neck height, never sticks out behind it (0.04 texel at worst).  Head yaw needs no veil follow
(the back veil top stays hidden behind the nape up to the +-0.6 tracking clamp).

ROOT
* body -- root ON THE FLOOR (pivot 0, 24, 0): the black core of the column, the belt, the ragged hem pool fading on the
  floor, the rigid 35-wide capelet (square shoulders), the big white bib and the black pectoral cross.  Carries every
  other bone.  Rest never moves.  Breathing: xRot sin(t*0.05)*0.006 (barely).  Stare (-0.06 xRot, dy -0.75): the whole
  rigid column rocks back on the back edge of its hem like a statue (the dy keeps that edge exactly on the floor).
  Point (yRot -0.12): turns the right shoulder into the accusation.  Statue snap: yRot jumps to face the player while
  unobserved.
* skirt_front / skirt_back / skirt_right / skirt_left -- the four stiff slabs of the bell, pivots at the belt, rest
  flare 4 deg (front/back) and 6 deg (sides) so the hem is wider than the shoulders' column; the front slab carries
  the scapular, the left slab the iron key ring and the three fanned keys (they ride its flare).  Static; draught
  flutter xRot/zRot += sin(t*0.03 + k)*0.008 (k = 0..3); appear/vanish gust +0.06 further outward (front: -x, back:
  +x, right: +z, left: -z), ease back over 10 ticks.  Keys: a single clink when she appears.
* rosary -- link into the belt, pewter beads down the front slab to the knee, silver crucifix (rest xRot -6.5 deg so
  it lies on the flared slab).  Pendulum lagging the body: zRot = sin(t*0.06)*0.04; when the right arm snaps into
  'point' give it an impulse zRot -0.15 decaying over 20 ticks (bead clicks on the impulse).  Keep xRot >= 0 offset
  (a negative xRot would push the beads into the slab).
* veil_back_right / veil_back_left -- the long back veil, two panels split down the middle, pivots at the top (0,
  -32, ~8.4) tucked inside the nape at neck height; rest (3, -+4, +-3) deg: falling away from the back, folded along
  the split, flaring out.  Each ends in a point at the knee (y 8) with a pale rim.  Idle sway xRot sin(t*0.04 +
  0/1.3)*0.01 (out of phase).  VEIL RULE dz.  Appear/vanish: zRot +-0.05 further out, settle over 10 ticks.

HEAD
* head -- FOCUS bone (pivot 0, -28, 0): skull + face cubes (nose, cheekbones, flush jowls), white coif (3-texel
  forehead band, cheek plates, the starched fold under the chin), the flat crown cap, the nape.  Tracks the player:
  yaw clamp +-0.6, pitch clamp -0.3..0.35, slow (0.04 rad/tick), always with the VEIL RULE.  "Aja." beat: dip xRot +0.1
  and back over 6 ticks while the pen ticks the ledger.  Write (0.26, -0.1, 0.03) looks down into the ledger; stare
  (-0.3, 0, 0.05) chin up, looking down her nose at you with a disdainful tilt; point (0.05, 0.12, 0) leans into the
  accusation and cancels the body's yaw so the face stays on the player.  Roll call: between names turn yaw towards
  each empty desk.
* crown_right / crown_left -- the sloped shoulders of the starched crown (rest zRot -+28 deg); they make the top of
  the head an arch.  Static (never animate: they cover the band's top corners).
* right_brow -- the furrowed right brow: a 7 x 2 band of grey hair growing out of the skull (z -8..-6), rest zRot 20
  deg, knot by the nose, crushing the right lens into a crescent.  Idle: nothing.  On every "Aja." and in stare / point:
  zRot +0.06 (deeper scowl, the crescent narrows).  Surprise (player answers "presente"): zRot -0.15 for 10 ticks.
  (The LEFT brow is painted: a 2-row dark arch raised high over a wide-open lens -- the gag is the asymmetry.)
* glasses -- round steel spectacles: 1-texel steel rims with one glint, bridge, short temples tucking under the coif,
  opaque glowing lenses (emissive 'eyes' layer).  Static; signature gesture in stare: pushed up the nose, dy -0.8
  (table value) -- animate it 6 ticks up, hold, back over 4 (with a glint spike on the eyes layer).
* jaw -- the hinge jaw between the jowls: the pressed mouth line with its turned-down corners, the chin (hinge 0, -32,
  2).  Rest closed.  Voice-driven: xRot = amp*0.18 (max 0.2).  "Aja." = two short opens (0.1, then 0.06).  "Usted." =
  one 0.14 open; point holds 0.14.  "Silencio." = three.
* veil_right / veil_left -- the black veil wings: from the crown they flare 5 deg out towards the shoulders and fall 6
  deg back behind the coif (rest (6, 0, +-5) deg), landing on the capelet.  VEIL RULE (write -0.221, stare +0.255,
  point -0.0425); appear/vanish flare zRot -+0.08 and settle.

ARMS -- right_* is -X (viewer's left).  Rest: the right elbow out at the side, the fist raised to the chest holding
the pen, nib over the right-hand page; the left forearm cradles the ledger, the left hand grips its outer edge (four
fingers hooked over the board, modelled on the book bone).
* right_arm -- pen arm, upper sleeve under the capelet (pivot at the shoulder).  Idle static.  Write (0.169, 0.066,
  -0.063); point (-0.833, -0.199, 0.045) raises it to shoulder height, aimed at the player.  Stare: rest (the pen
  stays poised; the gesture is the chin and the spectacles).
* right_forearm -- forearm + bell cuff + white undercuff.  Write (0.025, 0.067) brings the nib down; point (1.695,
  0.641) straightens the elbow (the forearm lines up with the upper arm).
* right_hand -- fist holding the pen (knuckle row, finger splits, nails on the palm side, thumb).  Idle: taps the
  nib towards the ledger every 80-140 ticks (xRot +0.12 for 3 ticks).  Write (0.003, 0.138, 0.03): the nib's lowest
  edge rests ON the right-hand page; point (-1.44, -0.522, 0.24): knuckles up, thumb in, the finger dead ahead --
  world direction (0.10, -0.10, -0.99), 6 deg up towards the player's eyes, tip 39 texels in front of her at shoulder
  height.  Blend in body-relative order (arm, forearm, hand) over the pose's blend time.
* right_index -- long index finger (2 x 8) lying along the top of the pen at rest (xRot PEN_TILT 30 deg).  Point
  -0.5236 (dead straight).  Running player ("En el colegio se camina."): finger wag zRot sin(t*0.9)*0.25 for 20 ticks
  on top of point.
* pen -- big black-lacquer fountain pen, gold bands and clip, gold nib with a red tip.  Write: scribble on top of the
  pose -- xRot += sin(t*1.2)*0.05, zRot += cos(t*1.2)*0.04 (2-3 strokes, then a firm tick: xRot +0.08 for 2 ticks).
  Point (2.736, -0.001, 0.007, 1.74, -4.472, -0.595): flipped back along the inside of the wrist and laid down the
  forearm, 0.26 texel inside the sleeve (no coplanar faces), cap in the fist -- so the finger is the only spike.  When
  snapping into point, flip the pen in the first 2 ticks (a pen twirl).
* left_arm -- book arm, upper sleeve under the capelet.  Static.  Point -0.08 (keeps the ledger off the belt while
  the body turns).
* left_forearm -- forearm + cuff under the ledger (the cuff stays under the boards).  Write -0.1 lifts the book
  towards her; roll call: same.
* left_hand -- palm and thumb under the outer edge of the ledger (the fingers are on the book bone, hooked over the
  board).  Static.

LEDGER
* book -- the open libro de actas: oxblood boards (23 x 19) overhanging the page block by 1.5 texels with a tooled
  frame and brass corner caps, banded spine, ruled pages of handwritten names with red demerit ticks, a loose leaf
  with a big red X, a red ribbon, and the left hand's four fingers hooked over the outer board edge.  Rest tipped ~24
  deg TOWARDS the viewer and rolled 10 deg out past the left hip, so both pages read from 3-5 blocks.  Write -0.36
  (tipped back flat for writing).  On "Aja." a tiny settle +0.03 after the tick.

LAYERING
idle = (almost nothing) breathing + eyes pulse + occasional pen tap + statue snap.  'write' blends in over 6 ticks
and loops the pen scribble with head dips on every "Aja.".  'stare' over 10 ticks (the column rocks back, the
spectacles are pushed up).  'point' snaps in over 3 ticks (fast, it is the scare) and holds while she says
"Usted.", then eases out over 12.
"""
