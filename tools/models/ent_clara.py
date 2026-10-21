"""Clara -- the freed soul of Sor Maria de la Agonia (DEAD LINE, case 'convento', ending).

Authored at 2x texel density (model.scale = 0.5).  +Y down, ground y = 24, faces -Z, right_* on -X.  Centred on
x = 0, z = 0.  Veil dome top y = -57 (2.5 blocks); the halo ring (billboarded) tops out ~y -64, its soft haze ~y -67
(2.8 blocks); she floats: no feet, the robe dissolves into light and the lowest streamer tip stops ~2 texels above
the floor.  The counts (cubes, bones, texture) are computed from build() and stated at the top of ANIM_NOTES (and
printed by the preview), so they cannot go stale.

Design
------
Clara Ines Bustos, 33, the nun the demon wore -- freed.  The SAME habit as Sor Agonia, but clean, whole and made of
light: a starched white coif and rounded guimpe; the veil, still the darkest thing about her (smoky plum-grey), its
outline rim-lit; and the habit itself, no longer black wool but a translucent warm smoky mauve-grey (alpha ~168 ->
~130, so her body visibly ghosts) with a warm inner light, stepping in five flat value bands into pearl ivory toward
the hem, where the cloth thins (its alpha fades BEFORE the edge), turns to a soft pearl band and dissolves into a
low cream haze with a few pale motes and pearl streamers.  No orange, no hard white contour: fire and smoke belong to
the demon.  She is not scary: beautiful and sad, rising in the chapel at dawn with her arms open.

Read in a thumbnail (in this order): the warm-white HALO round the head (a white-gold ring + soft haze, nothing
inside it, always a circle -- Java billboards it), the luminous oval face framed in white, the light in her palms
when she rises, and a soft grey-mauve habit that thins into light.  Silhouette: a slender A -- a rounded veil dome
(three chamfered steps, its outline rim-lit), the veil set back from the face so the white coif, nose and chin read
in profile, drapes that fall behind the shoulders, a pointed back veil (centre panel + two side panels stepped round
the back), bell sleeves -- ONE flared, open tier under a small top tier, with a rolled lit hem and a short rounded
hanging back -- that hang with gravity when she lifts her arms, eight flared robe gores with hand-placed folds.

Face (15 x 17 pixel art made oval by stepping the coif linen into the corners; one-texel linen steps in front of the
temples and the jaw and a coif band overhanging the brow give the oval depth): smooth luminous skin in broad
planes, a nose with a shaded bridge, nostril wings and a shadow under its tip, a small closed smile (a continuous
1-px curve over a soft lower lip with a highlight) and ONE tear on her left cheek (a 1 x 2 pale-blue drop with a
highlight).  The features that change live on their own planes, each sitting over a WINDOW cut out of the skull
front (alpha 0 in both layers), so the translucent per-quad sort can never put the face over them:
  * eye_right / eye_left -- the OPEN eyes with their brows (head bone, in the plane of the face, filling its 5 x 7
    windows, opaque): calm level brows, heavy tender upper lids, a 3 x 2 deep-brown iris with a cream catchlight,
    sclera both sides, a lit waterline.
  * eyelids -- the CLOSED state (two opaque 5 x 7 planes 0.05 in front of the face, centred exactly on the same
    windows): sad brows whose inner ends lift over two texels, over peaceful U-shaped lash curves (continuous 1-px
    curves).  The lid plane is always nearer than the eye plane behind it, with the same centroid, so the sort is
    always right.  Open = hide them (see ANIM_NOTES): she opens her eyes and the grief leaves her brows.
  * lips -- the closed mouth (head bone, in the plane of the face, opaque) and `mouth` -- the speech frame (the
    lower lip dropped one row under a soft one-row opening), tucked 0.2 behind the lips at rest and brought 0.05 in
    front of the face to speak.
  * backings -- a skin plane one texel larger than each window, 0.05 behind it: a rasterisation crack at a window
    edge shows skin, never the dark inside of the head.

Rendering: entityTranslucentEmissive, alpha baked per material; the 'eyes' layer carries the light (see ANIM_NOTES,
RENDERING).  Faces that can never be seen, or that would lie flat on another face, are cut out; thin plates paint a
single face (the translucent pass draws it from both sides).  Volumes nest (bodice in guimpe, forearm in the bells,
wrist in the cuff) with the hidden faces culled -- nested volumes, no visible face crossings in the rest pose; in
the poses only cloth slides over same-coloured cloth (the head's veil sides over the drapes' tops).
"""
import math

import numpy as np

from mcmodel import Model, vnoise, hash3, face_light, pick, rot_matrix
from rig import Rig
from paint import hx, mix, pixelart, chain, scale

RIG = None

# ------------------------------------------------------------------ translucency (alpha baked per material)
A_SKIN = 235
A_LINEN = 226
A_HEADVEIL = 214
A_VEIL = 184
A_HABIT = 168      # the habit ghosts: ~168 at the chest, thinning to ~130 toward the light at the hem
A_SLEEVE = 160
A_BELL = 222       # the bells are denser: through a thinner bell its box would show (a glass lantern, not cloth)
A_WOOD = 232


def A(c, a):
    return (int(c[0]), int(c[1]), int(c[2]), int(max(0, min(255, a))))


def pal(*h):
    return [hx(c) for c in h]


# ------------------------------------------------------------------ palettes (dark -> light, hue shifted)
# luminous warm skin: rose shadows (light under the skin), peach mids, cream lights
SKIN = pal('#3d2230', '#5e3340', '#82494f', '#a6635d', '#c4826f', '#dca58b', '#ecc0a5', '#f6d8c2', '#fde9db',
           '#fff6ee')
# starched linen: lavender shadows -> warm cream lights
LINEN = pal('#3a3150', '#574d6c', '#776d8a', '#978ea6', '#b6adbf', '#cfc6d3', '#e3dbe0', '#f1ebea', '#faf6f1',
            '#ffffff')
# the habit, top: the same wool as Sor Agonia's, but she is light now -- a warm smoky mauve-grey (well under the
# white coif, so the nun's silhouette survives; nothing plum-black left in her)
HDARK = pal('#3b2f3a', '#473a46', '#544652', '#62535f', '#71616c', '#80707a', '#8f7f88', '#9e8e96')
# the habit, toward the hem: rose-grey -> pearl ivory (the wool turning into light)
HLIGHT = pal('#5e4f57', '#75656c', '#8d7d82', '#a69598', '#bdaeae', '#d1c4c1', '#e2d7d2', '#efe7e1', '#f8f3ee')
# the veil: still the darkest part of her (the black veil of the brief), smoky plum-grey, rim-lit
VEILC = pal('#1d1622', '#28202f', '#352a3d', '#43374b', '#524559', '#615368', '#716378', '#837489')
WARM = hx('#eadccb')        # warm pearl sheen on the lit ridges of the light wool
# the light she dissolves into: pearl -> cream -> white, a hint of gold in the shadows only (fire is the demon's)
LIGHT = pal('#5c4f4a', '#857469', '#ac9a89', '#cbbaa5', '#e2d3bd', '#f1e6d3', '#f9f2e6', '#fffaf2', '#ffffff')
# pale champagne for motes and streamers
GOLD = pal('#a08866', '#bea27a', '#d6bc92', '#e6d0aa', '#f0e0c2', '#f8edd6', '#fff9ee')
# the halo keeps a little real gold in its ring
HGOLD = pal('#9a6a1e', '#c48a2a', '#e2aa3c', '#f2c45a', '#f9d982', '#fde9b0', '#fff6dc')
SHINE = [GOLD[3], GOLD[4], GOLD[5], GOLD[6], LIGHT[7]]     # streamers: pearl light, never brown or orange
PALE = hx('#f3ebe4')        # the habit just before it becomes light
PEARL = hx('#fbf6ef')
RIMC = hx('#fff1de')        # warm-white rim texel along the outer silhouette
RIM_GLOW = (172, 154, 128)
LINING = pal('#120c16', '#1d1423', '#2a1f31', '#3a2c42')   # inside of the bell sleeves
WOOD = pal('#1e110a', '#341f12', '#4f311c', '#6c4528', '#8a5c35', '#a97746', '#c79a62')
LEATHER = pal('#1a1114', '#271a1e', '#35252a', '#453238', '#574148', '#6b525a')
NAIL = hx('#f7cfc5')

# face details
LASH = hx('#3a2018')
LASH2 = hx('#9c7465')
BROW = pal('#6e4433', '#8e5f48', '#b08468')
SCLERA = hx('#f3e7df')
SCLERA_D = hx('#dccbc2')
IRIS = pal('#24140c', '#432617', '#613a22', '#7e5233')      # deep, low-chroma warm brown (never amber)
PUPIL = hx('#140a05')
CATCH = hx('#fff6e6')                                         # cream catchlight
LIPC = pal('#a55a60', '#c4706e', '#d98b80', '#e8a395')
BLUSH = hx('#f2a898')
WATER = hx('#fbe1d6')
TEAR = hx('#f4fbff')
TEAR2 = hx('#d8ecf4')

GLOW = {}          # (u, v) -> rgba of the emissive layer, recorded while the base texture is painted
MODEL = None
_PAINTING = [False]


# ------------------------------------------------------------------ geometry helpers
def local(ctx):
    """Texel centre in cube-local texel units (same physical point for both sides of a plane)."""
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


def clamp(v, a=0.0, b=1.0):
    return a if v < a else b if v > b else v


def frect(c, face):
    u, v = c.uv
    w, h, d = c.size
    return {
        'top': (u + d, v, w, d), 'bottom': (u + d + w, v, w, d),
        'west': (u, v + d, d, h), 'front': (u + d, v + d, w, h),
        'east': (u + d + w, v + d, d, h), 'back': (u + 2 * d + w, v + d, w, h),
    }[face]


FACE_N = {'front': (0, 0, -1), 'back': (0, 0, 1), 'west': (-1, 0, 0), 'east': (1, 0, 0), 'top': (0, -1, 0),
          'bottom': (0, 1, 0)}


def posed_matrix(b, pose=None):
    """World matrix of bone b with a POSES entry added (radians / texels), as HauntModel.apply does."""
    pose = pose or {}
    chain_ = []
    while b is not None:
        chain_.append(b)
        b = b.parent
    M = np.eye(4)
    for bb in reversed(chain_):
        p = (list(pose.get(bb.name, ())) + [0] * 6)[:6]
        T = np.eye(4)
        T[:3, 3] = (bb.pivot[0] + p[3], bb.pivot[1] + p[4], bb.pivot[2] + p[5])
        R = np.eye(4)
        R[:3, :3] = rot_matrix(math.radians(bb.rot[0]) + p[0], math.radians(bb.rot[1]) + p[1],
                               math.radians(bb.rot[2]) + p[2])
        M = M @ T @ R
    return M


def all_poses():
    return [{}] + list(POSES.values())


# ------------------------------------------------------------------ the emissive layer
def gout(c):
    """Final texel of the additive 'eyes' layer.  Additive blending ignores alpha, but non-additive consumers (the
    bestiary portrait, the gallery) blend it normally -- so near-black texels become fully transparent and dim ones
    proportionally transparent: the in-game result is unchanged and nothing paints a dark mask."""
    r, g, b = (max(0, min(255, int(v))) for v in c[:3])
    if r + g + b < 12:
        return (0, 0, 0, 0)
    m = max(r, g, b)
    a = 255 if m >= 150 else max(26, int(round(255 * (m / 150.0) ** 1.5)))
    return (r, g, b, a)


def gpal(d):
    return {k: gout(v) for k, v in d.items()}


def emit(ctx, col, k=1.0):
    """Record an emissive texel for the 'eyes' layer (painted by glow_decal)."""
    if k <= 0:
        return
    u0, v0, _, _ = frect(ctx.cube, ctx.face)
    GLOW[(u0 + ctx.i, v0 + ctx.j)] = gout((col[0] * k, col[1] * k, col[2] * k))


def glow_decal(img, u0, v0, w, h):
    if not GLOW and MODEL is not None and not _PAINTING[0]:
        _PAINTING[0] = True
        MODEL.paint(DEFAULT_MAT)
        _PAINTING[0] = False
    px = img.load()
    for j in range(h):
        for i in range(w):
            c = GLOW.get((u0 + i, v0 + j))
            if c is not None:
                px[u0 + i, v0 + j] = c


GLOW_ALL = {'eyes:' + f: glow_decal for f in ('front', 'back', 'west', 'east', 'top', 'bottom')}


def outer_face(ctx):
    """The face of a thin plate that looks away from the body (only that one is painted: the translucent pass draws
    it from both sides, and painting both large faces would double the opacity)."""
    t = tag(ctx)
    if t == 'panel':
        return 'front'
    if t in ('veil_c', 'veil_s', 'nape'):
        return 'back'
    if t in ('veil_side', 'drape'):
        return 'west' if ctx.cube.side < 0 else 'east'
    return None


def inner_face(face):
    return {'front': 'back', 'back': 'front', 'west': 'east', 'east': 'west'}[face]


# ------------------------------------------------------------------ cloth: designed folds, not noise
def folds(i, j, w, h, n=None, converge=0.35, seed=0):
    """Long folds on a cloth face: each a lit ridge beside a shadow crease, running the full height and spreading
    from the top (where they converge toward the centre) to the hem."""
    if w < 4:
        return 0.0
    n = n or (3 if w >= 9 else 2)
    t = clamp((j + 0.5) / h)
    v = 0.0
    for k in range(n):
        xb = w * (k + 0.5 + (hash3(k, seed, 3, 17) - 0.5) * 0.35) / n
        xt = w / 2 + (xb - w / 2) * converge
        xf = xt + (xb - xt) * (t ** 0.8)
        d = i + 0.5 - xf
        if -1.2 <= d < 0.0:
            v += 0.12
        elif 0.0 <= d < 1.2:
            v -= 0.12
        elif 1.2 <= d < 2.0:
            v -= 0.04
    return v


def hem_at(u):
    """Height (texels, +Y down) of the dissolving hem at arc position u: a slow wave plus a few pointed tongues."""
    base = 8.0 + 2.6 * math.sin(u * 0.21 + 1.3) + 1.6 * math.sin(u * 0.53 + 0.4)
    cell = 4.6
    i = math.floor(u / cell)
    f = u / cell - i
    tongue = 0.0
    if hash3(i, 7, 0, 41) > 0.55:
        tongue = (1.0 + hash3(i, 9, 0, 43) * 3.0) * math.sin(f * math.pi) ** 2
    return base + tongue


def _flakes():
    """A few pale motes of light drifting down off the dissolving hem: short trails of 1x2 -> 1x1 -> 1x1 shapes
    (u, y, w, h, alpha, glow).  Fewer and paler than embers: pearl, never orange."""
    out = []
    u = -27.0
    k = 0
    while u < 27.0:
        k += 1
        if hash3(k, 3, 1, 77) < 0.42:
            sgn = 1 if hash3(k, 5, 1, 79) > 0.5 else -1
            y0 = hem_at(u) + 2.6
            shapes = ((1, 2, 170, 0.7), (1, 1, 130, 0.5), (1, 1, 96, 0.35))
            for s, (fw, fh, al, gl) in enumerate(shapes):
                fu = u + sgn * (1.2 * s + hash3(k, s, 2, 81) * 0.5)
                fy = y0 + 2.6 * s + hash3(k, s, 4, 83) * 0.8
                out.append((fu, fy, fw * 1.05, fh, al, gl))
        u += 5.5 + hash3(k, 1, 1, 85) * 3.0
    return out


FLAKES = _flakes()


def flake_at(u, y):
    for fu, fy, fw, fh, al, gl in FLAKES:
        if fu <= u < fu + fw and fy <= y < fy + fh:
            return al, gl
    return None


def robe_u(ctx):
    x, y, z = ctx.pos
    return math.atan2(x, -z) * 9.0


def robe_light(ctx, c, a):
    """Robe gores: cloth -> paler, thinner cloth (its alpha fades BEFORE the edge) -> a soft pearl band where the
    wool becomes light -> a low cream haze under it (so no dark notches show between the streamers) with a few pale
    motes drifting down.  No hard white contour, no orange: she is not burning, she is dissolving."""
    x, y, z = ctx.pos
    u = robe_u(ctx)
    hem = hem_at(u)
    dist = hem - y                                            # > 0: still cloth
    if dist > 0:
        lift = clamp(1.0 - dist / 14.0)
        c = mix(c, PALE, lift * lift * 0.85)                  # the wool turns into light: paler, thinner
        emit(ctx, (196, 178, 160), lift * lift * 0.7)
        a = a * (1.0 - 0.5 * lift ** 1.6)
        if 3.5 < dist < 6.0 and ctx.face == 'front':
            c = mix(c, HDARK[5], 0.4)                         # a darker hem band just above the light: the doubled
            #                                                   hem of the habit, so the light below it reads
        if dist < 2.5:
            k = 1.0 - dist / 2.5                              # 0 -> 1 toward the edge
            emit(ctx, (232, 222, 206), 0.5 + 0.3 * k)
            return A(mix(c, PEARL, 0.45 + 0.35 * k), a - 8 * k)
        return A(c, a)
    fl = flake_at(u, y)
    if fl:
        al, gl = fl
        emit(ctx, (236, 228, 214), gl)
        return A(PEARL if gl > 0.6 else LIGHT[6], al)
    depth = -dist
    if depth < 7.5:                                           # the cream haze the cloth dissolves into
        al = max(30.0, 96 * (1 - depth / 6.5) ** 1.2) if depth < 6.5 else 30.0
        emit(ctx, (196, 184, 166), 0.15 + al / 150)
        return A(mix(PEARL, GOLD[5], 0.3), al)
    return None


def robe_back_glow(ctx):
    """Inner face of a gore: no base texel (the outer face is drawn from both sides), but where the gore dissolves
    it carries a softer copy of the light, so the far side of the hem glows too when seen through her (from below,
    from behind) instead of showing grey."""
    dist = hem_at(robe_u(ctx)) - ctx.pos[1]
    if 0 < dist < 4.0:
        emit(ctx, (196, 184, 166), 0.45 * (1 - dist / 4.0))
    elif -6.5 < dist <= 0:
        emit(ctx, (196, 184, 166), 0.45 * (1 + dist / 6.5))
    return None


def habit_t(y):
    """0 = the smoky wool of the chest and upper sleeves .. 1 = pearl ivory at the hem (continuous)."""
    return clamp((y + 18.0) / 30.0) ** 1.2


BAYER = ((0, 8, 2, 10), (12, 4, 14, 6), (3, 11, 1, 9), (15, 7, 13, 5))
BANDS = 4          # 5 visible value bands (0, 1/4, 1/2, 3/4, 1)


def habit_band(ctx, t=None):
    """habit_t stepped into BANDS + 1 flat value bands, with a one-texel ordered-dither seam between two bands (pixel
    art, not an airbrushed gradient)."""
    t = habit_t(ctx.pos[1]) if t is None else t
    q = t * BANDS
    base = math.floor(q)
    frac = q - base
    thr = 0.5 + (BAYER[ctx.j % 4][ctx.i % 4] / 16.0 - 0.47) * 0.22
    return min(BANDS, base + (1 if frac > thr else 0)) / BANDS


def cloth_glow(ctx, k=1.0, t=None):
    """Soft inner light of the habit: a warm breath even in the wool of the chest, rising toward the hem."""
    t = habit_band(ctx) if t is None else t
    emit(ctx, (166, 148, 132), (0.3 + 0.36 * t ** 1.5) * k)


def rim(ctx, c, strength=1.0, glow=1.0):
    """A warm-white texel on the outer silhouette; it carries the backlight in the glow layer."""
    emit(ctx, RIM_GLOW, strength * glow)
    return mix(c, RIMC, 0.42 * strength)


# hand-placed folds of the eight gores (front of each gore): (x at the top, x at the hem as fractions of the width,
# 'R' = a lit ridge with its shadow side, 'C' = a crease with a lit lip); every gore also gets a darker hem band just
# above the light
PANEL_FOLDS = {
    0: ((0.20, 0.10, 'R'), (0.34, 0.26, 'R'), (0.72, 0.84, 'C')),     # front: a ridge pair, a crease
    1: ((0.40, 0.28, 'R'), (0.76, 0.88, 'C')),
    2: ((0.50, 0.45, 'R'),),
    3: ((0.30, 0.18, 'C'), (0.66, 0.78, 'R')),
    4: ((0.26, 0.14, 'C'), (0.56, 0.62, 'R'), (0.70, 0.80, 'R')),     # back: a crease, a ridge pair
    5: ((0.34, 0.22, 'R'), (0.70, 0.82, 'C')),
    6: ((0.50, 0.55, 'R'),),
    7: ((0.24, 0.12, 'C'), (0.60, 0.72, 'R')),
}
# the bodice under the guimpe: two creases gathered into the cincture and a lit ridge between them (x in texels from
# the centre at the top -> at the belt)
BODICE_FOLDS = ((-3.5, -2.0, 'C'), (0.5, 0.5, 'R'), (3.5, 2.5, 'C'), (-6.0, -5.5, 'R'), (6.0, 5.5, 'R'))


def fold_at(i, xf, kind):
    """Value change of column i for one hand-placed fold whose line is at xf (texels) in this row."""
    c = int(math.floor(xf))
    if kind == 'R':
        return 0.15 if i == c else -0.09 if i == c + 1 else 0.0
    return -0.16 if i == c else 0.05 if i == c - 1 else 0.0


HIDDEN = {
    # tag -> faces never seen (cut so nothing ghosts or doubles through the translucency)
    'bodice': ('top', 'bottom', 'back'), 'belt': ('top', 'bottom'),
    'sleeve_up': ('bottom',), 'forearm': ('top', 'bottom'), 'bell_top': (),
    'crown1': ('bottom',), 'crown2': ('bottom',), 'crown3': ('bottom',),
    'nape': ('front', 'top', 'bottom', 'west', 'east'), 'veil_side': ('top',),
    'veil_c': ('top', 'bottom', 'front'), 'veil_s': ('top', 'bottom', 'front'),
    'drape': ('top',), 'panel': ('top', 'bottom', 'back'),
}
VEIL_TAGS = ('crown1', 'crown2', 'crown3', 'nape', 'veil_side', 'drape', 'veil_c', 'veil_s')
HEADVEIL_TAGS = ('crown1', 'crown2', 'crown3', 'nape', 'veil_side')
SLEEVE_TAGS = ('sleeve_up', 'forearm', 'bell_top', 'bell', 'wing')
CROWN_NEXT = {'crown1': (8.5, 6.0, 6.0), 'crown2': (6.5, 4.5, 4.5)}    # footprint (|x|, -z, +z) of the step above


def corner_cut(ly, lz, h, r=5.0):
    """Rounded front-bottom corner of the upper veil sides (the coif edge and the chin show in profile)."""
    if ly > h - r and lz < r:
        dx, dy = r - lz, ly - (h - r)
        return dx * dx + dy * dy > r * r
    return False


def bell_half(ly, h, full):
    """Half width of the flared bell at depth ly: a little wider than the top tier (3) at the top -> `full` (half the
    box) at the hem."""
    return full - 0.6 * (full - 3.3) * (1.0 - clamp(ly / h)) ** 1.2


def habit_mat(ctx):
    """Habit, sleeves and veil."""
    t = tag(ctx)
    f = ctx.face
    if t == 'panel' and f == 'back':
        return robe_back_glow(ctx)
    if f in HIDDEN.get(t, ()):
        return None
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    x, y, z = ctx.pos
    side = f in ('front', 'back', 'west', 'east')
    of = outer_face(ctx)
    if of and side and f == inner_face(of):
        return None                                           # thin plates: only the outer face is painted
    veil = t in VEIL_TAGS
    ht = habit_band(ctx)
    a = A_HEADVEIL if t in HEADVEIL_TAGS else A_VEIL if veil else \
        A_BELL if t in ('bell', 'bell_top') else (A_SLEEVE if t in SLEEVE_TAGS else A_HABIT) - 30 * ht
    v = 0.42 + face_light(ctx) * 0.9
    is_rim = False
    rim_k = 1.0
    rim_g = 1.0
    big = side and ctx.w >= 4 and ctx.h >= 4
    sx = getattr(ctx.cube, 'side', 0)
    outer_side = 'west' if sx < 0 else 'east'

    # ---------------- veil
    if t in ('crown1', 'crown2', 'crown3'):
        dxe, dze = min(lx, w - lx), min(lz, d - lz)
        cut = 2.5 if t == 'crown1' else 2.0
        if dxe + dze < cut:
            return None                                       # chamfered corners: an octagonal dome, not a box
        if f == 'top':
            nxt = CROWN_NEXT.get(t)
            if nxt and abs(x) < nxt[0] and -nxt[1] < z < nxt[2]:
                return None                                   # under the next step of the dome
            # one dome over all three steps: lit at the crown of the head, rolling off toward every edge
            rx = abs(x) / 9.5
            rz = abs(z) / 7.0
            v += 0.16 - (rx * rx + rz * rz) * 0.26
            v += folds(ctx.i, ctx.j, ctx.w, ctx.h, n=2, converge=0.9, seed=4) * 0.35
            if t == 'crown3' and (dxe + dze < cut + 1.0 or dxe < 1.0 or dze < 1.0):
                is_rim = True                                 # the crown of the dome, seen from above
                rim_k, rim_g = 0.5, 0.45
        elif side:
            v -= 0.04
            nxt = CROWN_NEXT.get(t)
            across = abs(x) if f in ('front', 'back') else abs(z)
            lim = None if nxt is None else (nxt[0] if f in ('front', 'back') else nxt[2])
            if t == 'crown3' or dxe + dze < cut + 1.0 or (lim is not None and across > lim and ctx.j == 0):
                is_rim = True                                 # the dome's outline: its top edge all round, and the
                rim_g = 1.0 if t == 'crown3' else 0.7         # chamfered corners / exposed shoulders of each step
    elif t == 'nape':
        v += folds(ctx.i, ctx.j, ctx.w, ctx.h, n=2, seed=3) * 0.6
        v -= ly / h * 0.08
    elif t == 'veil_side':
        if corner_cut(ly, lz, h):
            return None
        if f == of:
            v += 0.04 - (lz / d) * 0.1
            if ctx.h - 1 - ctx.j == 0 or (ly > h - 6 and corner_cut(ly + 1.0, lz - 1.0, h)):
                is_rim = True                                 # the hem and the rounded front corner
                rim_k, rim_g = 0.7, 0.45
            if lz > d - 1.0:
                is_rim = True                                 # the back edge (the head's profile)
                rim_g = 0.6
        elif f == 'front':
            v -= 0.06                                         # the dark frame round the coif (no rim: the black veil
            #                                                   framing the white coif is the nun's silhouette)
        elif f == 'bottom':
            v -= 0.12
            is_rim = True
            rim_k, rim_g = 0.6, 0.5
    elif t == 'drape':
        cut = h - 4.5 * (1.0 - lz / d) ** 1.4                  # the hem slopes: short in front, long behind
        if ly > cut:
            return None
        outer_col = (ctx.i == 0) if sx < 0 else (ctx.i == ctx.w - 1)
        if f == of:
            v += 0.03 + (ly / h) * 0.06
            if cut - ly < 1.0:
                is_rim = True                                 # the sloped hem
                rim_g = 0.6
            elif lz > d - 1.0:
                is_rim = True                                 # the back edge: soft, never a glowing 'string'
                rim_k, rim_g = 0.45, 0.3
        elif f == 'back':
            v -= 0.04
        elif f == 'front':
            v -= 0.05                                         # a dark band from the coif to the shoulder: no rim (it
            #                                                   lies behind the head, and the glow pass has no depth)
    elif t == 'veil_c':
        cx = (lx - w / 2) / (w / 2)
        cut = h - 6.0 * abs(cx) ** 1.3                         # pointed hem
        if ly > cut:
            return None
        if f == 'back':
            v += folds(ctx.i, ctx.j, ctx.w, ctx.h, n=2, converge=0.25, seed=7) * 0.8
            v += 0.08 + (ly / h) * 0.12
            if cut - ly < 1.0:
                is_rim = True
                rim_g = 0.8
        elif f in ('west', 'east'):
            v -= 0.06                                         # seams with the side panels
    elif t == 'veil_s':
        inner = (w - lx) / w if sx < 0 else lx / w             # 0 at the seam with the centre panel
        cut = h - 3.0 * inner ** 1.3
        if ly > cut:
            return None
        if f == 'back':
            v += folds(ctx.i, ctx.j, ctx.w, ctx.h, n=1, converge=0.6, seed=9) * 0.8
            v += 0.08 + (ly / h) * 0.12
            if cut - ly < 1.0:
                is_rim = True
                rim_g = 0.8
            elif inner > 1.0 - 1.0 / w:
                is_rim = True
                rim_k, rim_g = 0.6, 0.35                      # the long outer edges: soft, never glowing 'strings'
        elif f == outer_side:
            is_rim = True
            rim_k, rim_g = 0.6, 0.35
        else:
            v -= 0.06

    # ---------------- habit
    elif t == 'bodice':
        if f == 'front':
            hw = bib_half(y + 31.5, 20.0, 10.0)
            if y < -21.5 and abs(x) < hw - 0.3:
                return None                                   # behind the guimpe
        elif f in ("west", "east") and y < -21.5:
            return None
        v += 0.04 + clamp((y + 22.0) / 10.0) * 0.06
        if f == 'front':
            tt = clamp((y + 21.5) / 9.0)                      # 0 under the guimpe .. 1 at the cincture
            for xt, xb, kind in BODICE_FOLDS:
                v += fold_at(ctx.i, w / 2 + xt + (xb - xt) * tt, kind)
            if y < -19.5:
                v -= 0.12                                     # the shade the guimpe casts
    elif t == 'belt':
        if f == 'back' and abs(x) < 4.0:
            return None                                       # always under the back veil: no dark band through it
        v = 0.5 + face_light(ctx) * 1.0
        if ctx.j in (0, ctx.h - 1):
            v -= 0.14
        if ctx.j == ctx.h // 2 and ctx.i % 3 == 1:
            v += 0.14
        if f == 'front':
            emit(ctx, (40, 30, 24), 0.5)
        return A(pick(LEATHER, v), 205)
    elif t == 'sleeve_up':
        if f == ("east" if sx < 0 else "west") and y < -21.5:
            return None                                       # lies against the guimpe
        if f == 'top':
            v += 0.05
            out_edge = (lx < 1.0) if sx < 0 else (lx > w - 1.0)
            if out_edge or lz < 1.0 or lz > d - 1.0:
                is_rim = True                                 # the line of the shoulder
                rim_g = 0.7
        if big:
            v += folds(ctx.i, ctx.j, ctx.w, ctx.h, n=1, converge=0.8, seed=13) * 0.7
        # distance (texels) of this column from the arm's outer silhouette on its front / back face
        oc = None
        if f == 'front':
            oc = ctx.i if sx < 0 else ctx.w - 1 - ctx.i
        elif f == 'back':
            oc = ctx.w - 1 - ctx.i if sx < 0 else ctx.i
        if oc == 0 or (f == outer_side and (ctx.i in (0, ctx.w - 1) or ctx.j == 0)):
            is_rim = True                                     # the outer silhouette of the upper arm: a 2-texel rim,
            rim_g = 1.0                                       # bright edge ...
        elif oc == 1 or (f in ('front', 'back') and ctx.j == 0):
            is_rim = True                                     # ... and a softer second texel (and the shoulder top)
            rim_k, rim_g = 0.35, 0.4
    elif t == 'forearm':
        if -15.0 < y < -12.0 or y > -10.0:
            return None                                       # inside the top of the bell / the cuff
        if y > -12.0:
            v -= 0.18                                         # in the shade inside the bell
    elif t == 'bell_top':
        cxr, czr = abs(lx - w / 2), abs(lz - d / 2)
        if f == 'top':
            v += 0.06                                         # closed: the forearm goes into it (no open-box hole)
        elif f == 'bottom':
            if cxr < 2.0 and czr < 2.0:
                return None
            ring = max(cxr, czr)
            return A(pick(LINING, 0.2 + (3.0 - ring) * 0.25), 200)   # dark ceiling of the open bell
        else:
            v += 0.02 + (ly / h) * 0.04                        # plain cloth: no rim on its edges
    elif t == 'bell':
        # ONE flared tier: four trapezoid flaps (~4 -> 5 / ~3.6 -> 4 half width) joined to the top tier by a closed
        # shoulder; the corners step in like cloth; a rolled hem with rounded corners that catches the light
        if f == 'bottom':
            return None                                       # open below
        cxr, czr = abs(lx - w / 2), abs(lz - d / 2)
        if f == 'top':
            if cxr < 3.0 and czr < 3.0:
                return None                                   # under the top tier
            if cxr > bell_half(0, h, w / 2) or czr > bell_half(0, h, d / 2):
                return None                                   # outside the flaps' top edges
            v += 0.08                                         # the closed shoulder of the bell
        else:
            c_, full = (cxr, w / 2) if f in ('front', 'back') else (czr, d / 2)
            hw = bell_half(ly, h, full)
            if c_ > hw:
                return None                                   # the flare
            hem = h - 1.4 * (c_ / full) ** 3                  # rounded corners at the hem
            if ly > hem:
                return None
            v += 0.06 + (ly / h) * 0.12
            v += folds(ctx.i, ctx.j, ctx.w, ctx.h, n=2, converge=0.5, seed=31) * 0.6
            if c_ > hw - 1.0:
                v -= 0.06                                     # the flap's edge turns away
            if hem - ly < 1.0:
                v += 0.1
                is_rim = True                                 # the rolled hem catches the light (the only rim)
                rim_k, rim_g = 0.55, 0.5
    elif t == 'wing':
        if f != 'front':
            return None                                       # one painted face (drawn from both sides)
        cx = (lx - w / 2) / (w / 2)
        cut = h - 3.5 * abs(cx) ** 2.2                         # short, softly rounded: hanging cloth, never a blade
        if ly > cut:
            return None
        v += folds(ctx.i, ctx.j, ctx.w, ctx.h, n=2, converge=0.3, seed=37) * 0.7 + (ly / h) * 0.16
        a = A_SLEEVE - 24 - (ly / h) * 36
        if cut - ly < 1.0:
            v += 0.08                                         # a soft lighter hem, barely glowing
            is_rim = True
            rim_k, rim_g = 0.45, 0.25
    elif t == 'panel':
        k = ctx.cube.panel
        if f == 'front':
            tt = clamp((ly + 0.5) / h)
            for xt, xb, kind in PANEL_FOLDS[k]:
                v += fold_at(ctx.i, w * (xt + (xb - xt) * tt ** 0.8), kind)
        v += clamp((y + 11.5) / 16.0) * 0.26                   # brighter toward the hem
        if f in ('west', 'east'):
            v -= 0.05
        if k in (2, 6) and f == 'front' and ctx.i in (0, ctx.w - 1):
            is_rim = True                                     # the robe's flanks
            rim_k, rim_g = 0.5, 0.4
        a = A_HABIT - 30 * ht - clamp((y + 11.5) / 20.0) * 8

    if veil:
        c = pick(VEILC, v)
    else:
        if t != 'belt':
            v += clamp((y + 32.0) / 44.0) * 0.12              # the whole habit brightens from the chest to the hem
        c = mix(pick(HDARK, v), pick(HLIGHT, v), ht)          # smoky wool at the chest -> pearl ivory at the hem
        if side and v > 0.6 and ht > 0.3:
            c = mix(c, WARM, 0.16 * ht)                       # warm sheen on the lit ridges
    if is_rim:
        c = rim(ctx, c, rim_k, rim_g)
    if not veil and t != 'belt':
        cloth_glow(ctx, 0.85 if t in SLEEVE_TAGS else 1.0, ht)
    elif veil and not is_rim and f in ('front', 'west', 'east', 'top', 'bottom') and t in HEADVEIL_TAGS:
        emit(ctx, (84, 70, 80), 0.3)                          # the head veil is backlit a little through the cloth
    elif veil and not is_rim and f == outer_face(ctx):
        emit(ctx, (96, 82, 92), 0.4)                          # the back veil and drapes glow faintly through
    if t == 'panel':
        return robe_light(ctx, c, a)
    return A(c, a)


def bib_half(ly, w, h):
    """Half width of the guimpe at depth ly: straight sides, generously rounded bottom."""
    return w / 2 - max(0.0, ly - (h - 4.5)) ** 1.6 * 1.05


LINEN_GLOW = (58, 54, 48)     # ~0.2 of the linen: warm white, never blown out


def linen_mat(ctx):
    """Starched clean linen: lavender shadows, cream lights, gathers, a crisp shadow line where it meets the face.
    Glows warm white."""
    t = tag(ctx)
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    x, y, z = ctx.pos
    side = f in ('front', 'back', 'west', 'east')
    if t == 'band':
        if f in ('top', 'back'):
            return None
        if f == 'bottom' and lz > 1.5:
            return None                                       # only the overhang in front of the face shows
        if f in ('west', 'east') and z > -5.0:
            return None                                       # under the veil sides
    if t == 'step':
        if f == 'back' or (f == 'top' and y < -45) or (f == 'bottom' and y > -45):
            return None                                       # against the face / the band / the chin wrap
        if (f == 'west' and x < -7.0) or (f == 'east' and x > 7.0):
            return None                                       # against the coif side
    if t == 'coif_side':
        if f in ('top', 'back', 'bottom'):
            return None
        outer = (f == 'west' and x < 0) or (f == 'east' and x > 0)
        inner = (f == 'east' and x < 0) or (f == 'west' and x > 0)
        if inner and z > -7.0:
            return None                                       # against the skull
        if outer and y < -38.0 and z > -5.0 and not corner_cut(y + 53.0, z + 5.0, 15.0):
            return None                                       # under the veil side
    if t == 'chinwrap':
        if f in ('back', 'bottom'):
            return None
        if f == 'top' and z > -7.0:
            return None
    if t == 'guimpe':
        if f in ('back', 'bottom'):
            return None
        if f in ('west', 'east') and z > -2.0 and y > -31.0:
            return None                                       # the sleeve lies against it here
    if t == 'neckband' and f in ('top', 'bottom', 'back'):
        return None
    v = 0.8 + face_light(ctx) * 0.8
    if f in ('west', 'east'):
        v -= 0.1
    elif f == 'back':
        v -= 0.25
    gl = 1.0
    if t == 'band':
        if f == 'front':
            v += (0.06, -0.03)[ctx.j % 2]
            v -= (abs(lx - w / 2) / (w / 2)) ** 2 * 0.12
        elif f == 'bottom':
            v -= 0.16                                         # the underside of the overhang: a shade line
            gl = 0.5
    elif t == 'step':
        if f == 'front':
            v += 0.04
        else:
            v -= 0.06                                         # the coif tucked in round the jaw / temples
    elif t == 'coif_side':
        inner_strip = (f == 'east' and x < 0) or (f == 'west' and x > 0)
        if f == 'front' or inner_strip:
            v += 0.04 - ly / h * 0.06                         # one continuous white frame round the face oval
            if inner_strip:
                v += 0.1
            if f == 'front':
                v += 0.06                                     # the lit bevel of the frame
        else:
            v -= 0.18 if lz > 1.0 else 0.08                   # the cheek of the coif turns away: a soft bevel,
            gl = 0.6                                          # not a hard box corner
    elif t == 'chinwrap':
        if f == 'front':
            v += (0.04, -0.04)[ctx.i % 2]                     # gathered under the chin
            if ctx.j == 0:
                v -= 0.16
        elif f == 'top':
            v += 0.02
    elif t == 'guimpe':
        cx = abs(lx - w / 2)
        if f == 'front':
            hw = bib_half(ly, w, h)
            if cx > hw:
                return None
            if ly < 3.0:
                g = 1 - ly / 3.0
                v += (0.05 if int(lx) % 2 == 0 else -0.05) * g  # gathers falling from the neck
            v -= (cx / (w / 2)) ** 2 * 0.12
            if cx > hw - 1.0:
                v -= 0.08
        elif f in ('west', 'east'):
            zc = lz if f == 'west' else (d - lz)
            hw = bib_half(ly, d * 2, h)
            if (d - zc) > hw and ly > h - 4.5:
                return None
            v -= 0.02
            gl = 0.6
        elif f == 'top':
            v -= 0.02 + (0.04 if int(lx) % 2 else 0)
            gl = 0.0                                          # seen from behind it would glow through the back veil
    elif t == 'undercuff':
        gl = front_k(ctx)                                     # the cuffs come up to the sternum in 'bow'
        if f == 'top':
            return None
        if f == 'bottom':
            if 1.0 < lx < w - 1.0:
                return None                                   # the wrist
    elif t == 'neckband':
        v -= 0.08
    c = pick(LINEN, v)
    if t == 'guimpe' and f == 'front':
        cx = abs(lx - w / 2)
        hw = bib_half(ly, w, h)
        if hw - 2.0 < cx < hw - 1.0 and ly > 1.0:
            c = mix(c, LINEN[4], 0.45)                        # stitched hem a texel inside the edge
        cord = 3.6 - ly * 0.6
        if 0.5 < ly < 4.0 and abs(cx - max(0.0, cord)) < 0.5 and cx > 0.6:
            c = mix(c, LEATHER[3], 0.7)                       # the cross hangs on a thin cord
            gl = 0.0
    if side or f == 'top':
        lum = (c[0] + c[1] + c[2]) / 765.0
        emit(ctx, LINEN_GLOW, gl * clamp(0.2 + lum * 0.8))
    return A(c, A_LINEN)


# ------------------------------------------------------------------ flesh
SKIN_HIDDEN = {'skull': ('top', 'west', 'east', 'bottom'), 'nose': ('back',)}


def skin_mat(ctx):
    """Luminous skin for the sides/undersides of the face cubes (the fronts are the FACE pixel art).  The nose has NO
    glow of its own: the face glow behind it already shows through it (the glow pass has no depth), so the nose gets
    exactly one skin glow from every side."""
    t = tag(ctx)
    f = ctx.face
    if f in SKIN_HIDDEN.get(t, ()):
        return None
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    if t == 'skull' and f == 'back':
        return A(VEILC[2], 255)                               # blocks the face from ghosting through the veil
    if f == 'front':
        return A(SKIN[7], A_SKIN)                             # replaced by the face art
    v = 0.72 + face_light(ctx) * 0.7
    if f in ('west', 'east'):
        v -= 0.1
    if t == 'nose' and f == 'bottom':
        cx = lx - w / 2
        c = SKIN[5] if abs(cx) > 0.5 and lz < d - 0.4 else SKIN[6]
        return A(c, A_SKIN)
    if t == 'nose' and f == 'top':
        return A(scale(SKIN[6], 0.8), A_SKIN)                 # the top light is full: keep the bridge level with the
        #                                                       face front when she bows (no bright bar)
    return A(pick(SKIN, v), A_SKIN)


_HAND_BACK = {}


def front_k(ctx):
    """Glow weight of an arm face: 0 for any face that turns sideways or backward in some pose (the glow pass has
    no depth, so it would shine through her body -- e.g. the pressed palms and the cuffs in 'bow' seen from behind),
    rising to 1 only for faces that point clearly forward in every pose (in practice: the fingertips)."""
    return clamp((-0.02 - faces_back(ctx)) / 0.25)


def faces_back(ctx):
    """True if this face of a hand points backward (world +Z) in the rest pose or any exported pose: the glow pass
    has no depth, so such a face would shine through her body when she is seen from behind."""
    key = (ctx.bone.name, ctx.face)
    if key not in _HAND_BACK:
        n = np.array(FACE_N[ctx.face], float)
        worst = -1.0
        for p in all_poses():
            R = posed_matrix(ctx.bone, p)[:3, :3]
            worst = max(worst, (R @ n)[2])
        _HAND_BACK[key] = worst
    return _HAND_BACK[key]


def hand_mat(ctx):
    """Slender luminous hands: soft knuckle creases, rose nails, glowing fingertips."""
    t = tag(ctx)
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    if f == 'top' and t in ('palm', 'finger', 'thumb'):
        return None
    if t == 'thumb' and f == 'back':
        return None
    v = 0.8 + face_light(ctx) * 0.6                          # the hands carry their light in the base pass
    if t == 'palm':
        if ly < 1.0:
            v -= 0.1                                          # shade under the cuff
        if ly > h - 1.0 and f in ('west', 'east'):
            v -= 0.05
    # glow only on faces that never turn backward in any pose (they would shine through her body from behind): in
    # practice the fingertips, and a breath on the inner palms
    gk = front_k(ctx)
    if t in ('finger', 'thumb'):
        if ly > h - 1.0:
            c = NAIL if f not in ('bottom',) else SKIN[8]
            emit(ctx, (120, 104, 92), gk)                     # glowing fingertips
            return A(c, A_SKIN)
        if abs(ly - h * 0.45) < 0.5:
            v -= 0.06
    c = pick(SKIN, v)
    emit(ctx, (72, 60, 52), gk)
    return A(c, A_SKIN)


# finger columns of the hand (z index in the light box, from the thumb side): first texel row and length
FINGERS = {1: 4, 2: 5, 3: 4, 4: 3}


def _hand_cover(ly, lz):
    """Glow weight of a point (cube-local y, z of the light box) over the hand: palm, thumb, fingers, tips."""
    zi = int(math.floor(lz))
    if ly < 5.0:                                              # the palm (z 1..5) and the thumb (z 0..1, y 1.5..5.5)
        if zi >= 1:
            return 0.85
        return 0.8 if ly > 1.5 else 0.0
    if zi == 0:
        return 0.8 if ly < 5.5 else 0.0
    ln = FINGERS.get(zi)
    if ln is None or ly > 5.0 + ln:
        return 0.0
    return 1.0 if ly > 4.0 + ln else 0.9


def hand_light_mat(ctx):
    """The light in her palms (a glow-only shell round the hand, on its own bone so Java can hide it in 'bow', where
    the pressed palms would shine through her from behind).  No base texel: it only adds light."""
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    sx = ctx.cube.side
    if f == 'top':
        return None
    if f in ('west', 'east'):
        k = _hand_cover(ly, lz)
        inner = (f == 'east') if sx < 0 else (f == 'west')
        k *= 1.0 if inner else 0.22                           # the palm is the lit side; the back of the hand only
    elif f == 'front':                                        # catches a little of it
        k = 0.25 if ly < 9.0 else 0.0
    elif f == 'back':
        k = 0.2 if ly < 8.0 else 0.0
    else:                                                     # bottom: the tip of the middle finger
        k = 1.0 if 2.0 <= lz < 3.0 else 0.0
    if k > 0:
        tip = ly > 8.0
        emit(ctx, (200, 176, 148) if tip else (172, 150, 124), k)
    return None


def wood_mat(ctx):
    """The small wooden pectoral cross: grain, worn pale corners, a gold glint."""
    f = ctx.face
    v = 0.52 + face_light(ctx) * 1.2
    if f in ('front', 'west') and (ctx.i == 0 or ctx.j == 0):
        v += 0.22
    elif edge(ctx) == 0:
        v -= 0.1
    c = pick(WOOD, v)
    if f == 'front' and ctx.i == 0 and ctx.j == 0:
        c = LIGHT[5]
        emit(ctx, (160, 130, 70))
    return A(c, A_WOOD)


def none_mat(ctx):
    """Planes painted only by their decals."""
    return None


# ------------------------------------------------------------------ the halo
_HALO_CLEAR = {}
HALO_CAM_YAW = tuple(range(0, 360, 20))                     # degrees, camera all round her (relative to the body)
HALO_CAM_PITCH = (-0.3, -0.1, 0.1, 0.3, 0.5, 0.7)          # radians, + = camera below her (+Y is down)


def billboard_R(dcam):
    """Rotation of the billboarded halo for a camera in direction dcam (unit, model space, from the halo pivot to the
    camera): local -Z points at the camera, local -Y (up) is world up made perpendicular to it."""
    zax = -np.asarray(dcam, float)
    down = np.array([0.0, 1.0, 0.0])
    yax = down - zax * (down @ zax)
    yax /= np.linalg.norm(yax)
    xax = np.cross(yax, zax)
    return np.stack([xax, yax, zax], axis=1)


# the parts dense enough that a glowing ring must not show through them (alpha >= ~205): head, veil over the head,
# linen, cincture.  Through the translucent habit, sleeves, drapes and back veil (alpha 130-184) the ring's
# light SHOULD show -- she is a translucent soul, and the base pass shows the ring through them too
HALO_OCCLUDERS = ('skull', 'nose', 'band', 'coif_side', 'chinwrap', 'step', 'crown1', 'crown2', 'crown3', 'nape',
                  'veil_side', 'guimpe', 'neckband', 'belt')


def halo_clear(i, j):
    """Glow weight 0..1 of halo texel (i, j): 1 where no part of her is ever in front of it -- the halo billboarded to
    the camera, in the rest pose and every exported pose, for cameras all round her (HALO_CAM_YAW x HALO_CAM_PITCH)
    -- fading to 0 over 2.5 texels toward the texels that can be covered.  The glow layer has no depth, so only those
    texels may glow (in practice the top and the sides of the ring); the rest of the ring is full-bright in the base
    pass and sorts correctly behind the head."""
    if not _HALO_CLEAR:
        _halo_mask()
    return _HALO_CLEAR.get((i, j), 0.0)


def _halo_mask():
    bones = list(MODEL.bones())
    hb = next(b for b in bones if b.name == 'halo')
    hc = hb.cubes[0]
    w, h, _ = hc.size
    ij = [(i, j) for j in range(h) for i in range(w)]
    loc = np.array([[hc.origin[0] + i + 0.5, hc.origin[1] + j + 0.5, hc.origin[2]] for i, j in ij])   # N x 3
    dirs = []
    for yaw in HALO_CAM_YAW:
        for p in HALO_CAM_PITCH:
            a = math.radians(yaw)
            dirs.append((math.sin(a) * math.cos(p), math.sin(p), -math.cos(a) * math.cos(p)))
    dirs = np.array(dirs)                                                         # K x 3
    Rbb = np.stack([billboard_R(dv) for dv in dirs])                              # K x 3 x 3
    occ = np.zeros(len(ij), bool)
    occluders = [(b, c) for b in bones if b.name != 'halo' for c in b.cubes
                 if 0 not in c.size and c.name in HALO_OCCLUDERS]
    for pose in all_poses():
        piv = posed_matrix(hb, pose)[:3, 3]
        P = piv[None, None, :] + np.einsum('kab,nb->kna', Rbb, loc)               # K x N x 3 world
        for b, c in occluders:
            M = posed_matrix(b, pose)
            R, t = M[:3, :3], M[:3, 3]
            Pl = (P - t) @ R                                                      # K x N x 3 bone-local
            Dl = dirs @ R                                                         # K x 3
            lo = np.array(c.origin) - c.inflate
            hi = lo + np.array(c.size) + 2 * c.inflate
            inv = 1.0 / np.where(np.abs(Dl) < 1e-9, 1e-9, Dl)                     # K x 3
            t0 = (lo[None, None, :] - Pl) * inv[:, None, :]
            t1 = (hi[None, None, :] - Pl) * inv[:, None, :]
            tn = np.minimum(t0, t1).max(axis=2)
            tf = np.maximum(t0, t1).min(axis=2)
            hit = (tn < tf) & (tf > 0.05)
            occ |= hit.any(axis=0)
    blocked = np.array([[i + 0.5, j + 0.5] for k, (i, j) in enumerate(ij) if occ[k]])
    for k, (i, j) in enumerate(ij):
        if occ[k]:
            _HALO_CLEAR[(i, j)] = 0.0
            continue
        dd = np.min(np.hypot(blocked[:, 0] - i - 0.5, blocked[:, 1] - j - 0.5)) if len(blocked) else 99.0
        _HALO_CLEAR[(i, j)] = clamp((dd - 0.5) / 2.5)


HALO_WHITE = hx('#fffaf0')


def halo_mat(ctx):
    """The nimbus: ONLY a bright white-gold ring and a soft gold haze outside it.  Everything inside the ring is
    fully transparent -- no disc, no 'glass lid' over the veil from behind: grey alpha-blended cream never reads as
    light.  It is billboarded to the camera in Java (see ANIM_NOTES), so it is always this circle."""
    if ctx.face != 'front':
        return None
    lx, ly, lz = local(ctx)
    w, h, _ = ctx.cube.size
    r = math.hypot(lx - w / 2, ly - h / 2)
    R = w / 2
    if r > R:
        return None
    rr = R - 2.6                                             # the ring
    if r < rr - 1.5:
        return None                                          # nothing inside the ring
    kg = halo_clear(ctx.i, ctx.j)
    ring = abs(r - rr)
    if ring < 0.75:
        emit(ctx, (255, 242, 210), kg)
        return A(HALO_WHITE, 250)
    if ring < 1.5:
        emit(ctx, (240, 206, 136), 0.9 * kg)
        return A(HGOLD[5], 230 if r > rr else 200)
    k = clamp(1.0 - (r - rr - 1.5) / (R - rr - 1.5))           # outer haze
    al = 150 * k
    if al < 28:
        return None
    emit(ctx, (214, 176, 112), k * 0.7 * kg)
    return A(HGOLD[4], al)


def light_mat(ctx):
    """Light streamers below the dissolving robe: a pearl-white core in a pale champagne sheath, fading out
    downward.  The base colour is on the front face only (the translucent pass draws it from both sides); the glow is
    on BOTH faces (the glow pass culls back faces), so a streamer is light from every side, never a grey ghost."""
    if ctx.face not in ('front', 'back'):
        return None
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    k = ctx.cube.seed
    cx = abs(lx - w / 2) / max(1.0, w / 2)
    tip = h - 0.5 - hash3(int(lx), k, 0, 31) * 3.0 - cx * 3.5
    if ly > tip:
        return None
    tfade = ly / max(1.0, tip)
    s = vnoise(lx * 0.8, ly * 0.12, k, 33)
    lum = clamp(0.98 - cx * 0.45 - tfade * 0.35 + (s - 0.5) * 0.2)
    c = pick(SHINE, lum)
    top_in = clamp((ly + 1.0) / 3.0)
    a = 205 * top_in * (1 - tfade) ** 1.0 * (0.8 + s * 0.3) * (1 - cx * 0.35)
    if a < 28:
        return None
    emit(ctx, (226, 208, 178), clamp(a / 205))
    return A(c, a) if ctx.face == 'front' else None


# ------------------------------------------------------------------ the face
# 15 columns (x -7.5..7.5, col c <-> x = c - 7), 17 rows (row r <-> y = -51 + r).  '.' = a window cut out of the
# skull front (alpha 0 in both layers): the eyes WITH their brows (rows 2-8, cols 1-5 and 9-13) and the mouth (rows
# 12-15, cols 5-9) live on their own planes in / in front of these windows.
GX0, GY0 = -7.5, -51
FACE = [
    # 012345678901234
    "ccc556666655ccc",   # r0  y-51 the shade line cast by the overhanging coif band; the coif linen rounds the corners
    "cc67888988876cc",   # r1  forehead, one highlight
    "c.....888.....c",   # r2  eye windows (brows and eyes); the forehead between them
    "6.....888.....6",   # r3
    "6.....787.....6",   # r4  the bridge of the nose: lit on her right (viewer's left) ...
    "6.....786.....6",   # r5  ... a soft shade down its other side
    "6.....685.....6",   # r6  shade at the inner corners of the eyes
    "6.....786.....6",   # r7
    "6.....786.....6",   # r8  [nose cube rows 8-10, cols 6-8; the tip cube rows 9-10, col 7]
    "67rr8879688rt76",   # r9  soft blush on the cheekbones; the lit tip; the tear's faint trail on her left cheek
    "678887585788Y76",   # r10 nostril wings either side of the tip; the drop's highlight
    "677877656778T76",   # r11 a one-texel shadow under the nose tip, the philtrum; the pale-blue drop
    "67787.....78776",   # r12 mouth window
    "c6777.....7776c",   # r13 the chin rounds: 3-2-1-1
    "c6677.....7766c",   # r14
    "cc667.....766cc",   # r15
    "ccc667787766ccc",   # r16 chin, into the coif
]
assert all(len(r) == 15 for r in FACE), [len(r) for r in FACE]

# OPEN eyes (eye_right / eye_left planes, rows 2-8): calm brows (the sad lift of the inner ends is gone: she is at
# peace), heavy tender upper lids, deep-brown 3x2 irises -- the dark top under the lid with a cream catchlight in
# the middle, the pupil below it between two warm-brown texels (she looks straight at you) -- sclera on both sides,
# a lit waterline
EYE_R = [            # her right eye (viewer's left): outer corner at the left
    "67888",
    "Bhbbh",
    "67776",
    "KKKk7",
    "vIGIw",
    "qjOjv",
    "77W77",
]
EYE_L = [            # her left eye: outer corner at the right; the tear leaves the lower lid
    "88876",
    "hbbhB",
    "67776",
    "7kKKK",
    "wIGIv",
    "vjOjq",
    "77Wt7",
]
# CLOSED lids (eyelids bone): the same windows; sad brows whose inner ends lift by one row over TWO texels with a
# soft step (one continuous line, no stray dot), over peaceful U-shaped lash curves: the corners are as dark as the
# lash bar and touch it diagonally (one continuous 1-px curve, no loose corner dots)
LID_R = [
    "678hb",
    "Bhby7",
    "67776",
    "78887",
    "K888k",
    "7KKK7",
    "77777",
]
LID_L = [
    "bh876",
    "7yhbB",
    "67776",
    "78887",
    "k888K",
    "7KKK7",
    "777t7",
]
# the closed mouth (lips plane, rows 12-15, cols 5-9): a small closed smile -- the parting line rises into the
# corners, which are as dark as the line and touch it diagonally (one continuous 1-px curve); a fuller lower lip
# with a 1-px highlight under it (a 2-row shape) and a soft shadow under that
LIPS = [
    "n777n",
    "7nnn7",
    "7ULU7",
    "77s77",
]
# the speech frame (mouth bone): the same smile, the lower lip dropped one row under a one-row soft opening
MOUTH_OPEN = [
    "n777n",
    "7nnn7",
    "7DdD7",
    "7ULU7",
]
EYE_ROWS, EYE_COLS = (2, 9), {'right': 1, 'left': 9}
assert all(len(g) == EYE_ROWS[1] - EYE_ROWS[0] for g in (EYE_R, EYE_L, LID_R, LID_L))
MOUTH_ROW, MOUTH_COL = 12, 5

FPAL = {str(i): A(SKIN[i], A_SKIN) for i in range(10)}
FPAL.update({
    '.': (0, 0, 0, 0),
    'c': A(LINEN[7], A_LINEN),
    'b': A(BROW[0], A_SKIN), 'h': A(BROW[1], A_SKIN), 'B': A(BROW[2], A_SKIN),
    'y': A(mix(BROW[2], SKIN[6], 0.5), A_SKIN),                  # the soft step of the lifted brow
    'K': A(LASH, 252), 'k': A(LASH2, A_SKIN), 'q': A(mix(SKIN[6], LASH2, 0.45), A_SKIN),
    'w': A(SCLERA, A_SKIN), 'v': A(SCLERA_D, A_SKIN), 'W': A(WATER, A_SKIN),
    'I': A(IRIS[1], 252), 'i': A(IRIS[2], 252), 'j': A(IRIS[3], 252), 'O': A(PUPIL, 252), 'G': A(CATCH, 255),
    'r': A(mix(SKIN[7], BLUSH, 0.4), A_SKIN),
    'n': A(LIPC[1], A_SKIN),                                      # the parting line and the lifted corners
    'a': A(mix(SKIN[6], LIPC[0], 0.42), A_SKIN),                  # the mid-tone joining a corner to the line
    'u': A(mix(SKIN[6], LIPC[1], 0.55), A_SKIN),                  # pale upper lip
    'U': A(mix(SKIN[6], LIPC[3], 0.55), A_SKIN), 'L': A(mix(SKIN[8], LIPC[3], 0.3), A_SKIN),   # lower lip: rosy,
    #                                                               skin-valued (never read as an opening), lit centre
    's': A(SKIN[5], A_SKIN),                                      # the shadow under the lower lip
    'D': A(hx('#7a3a42'), 250), 'd': A(hx('#9a5058'), 250),   # a soft, shallow opening (never a dark hole)
    't': A(mix(SKIN[8], TEAR2, 0.25), A_SKIN), 'T': A(hx('#c9e2f0'), 245), 'Y': A(hx('#f6fbff'), 248),
})
# the face front and every plane over its windows are OPAQUE: whatever sits behind a plane (open eyes behind the
# lids, the speech frame behind the lips) must never show through; only the dark inside of the head lies behind the
# face, so translucency there would only grey it; and the backings' camouflage ring (drawn twice when it sorts in
# front of the face) matches the face exactly only if both are opaque
OPAQUE = {k: (v[0], v[1], v[2], 255 if v[3] else 0) for k, v in FPAL.items()}


def _g(c, k):
    return (c[0] * k, c[1] * k, c[2] * k)


# emissive layer of the face: a warm lift of ~0.12-0.23 of each skin tone (the base pass has no lightmap: a vertical
# face facing north/south is ~0.76 lit, so face + glow lands at ~0.98 of the painted skin -- luminous, never a
# clipped white mask; the mid-tones get the most and the highlights a little less); the mid-tones that join lips,
# lashes and brows to the skin glow halfway; lashes, brows, irises and lips do not glow so the features survive
SKIN_GLOW = {3: 0.12, 4: 0.16, 5: 0.19, 6: 0.22, 7: 0.23, 8: 0.22, 9: 0.2}
GLOWPAL = {str(i): _g(SKIN[i], k) for i, k in SKIN_GLOW.items()}
GLOWPAL.update({
    'c': _g(LINEN[7], 0.24), 'W': _g(WATER, 0.2), 'r': _g(mix(SKIN[7], BLUSH, 0.4), 0.2),
    't': _g(SKIN[8], 0.2), 'T': (44, 54, 64), 'Y': (80, 86, 90),            # the tear: a soft shine, not a bar
    'y': _g(SKIN[6], 0.1), 'q': _g(SKIN[6], 0.1), 'a': _g(SKIN[6], 0.09), 'u': _g(SKIN[6], 0.11),
    's': _g(SKIN[5], 0.18), 'U': _g(mix(SKIN[6], LIPC[3], 0.55), 0.2), 'L': _g(mix(SKIN[8], LIPC[3], 0.3), 0.2),
    'n': _g(LIPC[1], 0.05),
})
# the open eyes: sclera and catchlight only, each kept at or below the lid glow over it, so the closed lids (which
# glow by the difference) add up to exactly their own glow
EYEGLOW = dict(GLOWPAL)
EYEGLOW.update({'w': (20, 19, 18), 'v': (12, 11, 10), 'G': (34, 33, 31)})
for _k in 'KkIijOD':
    EYEGLOW.pop(_k, None)


def face_glow(r, c):
    ch = FACE[r][c]
    if ch == '.':
        return None
    g = GLOWPAL.get(ch)
    return gout(g) if g else None


def cell_decal(fn, x0, y0, w, h):
    """Decal over a face-cube front: fn(row, col) -> rgba or None for the face cell under each texel."""
    def dec(img, u0, v0, fw, fh):
        px = img.load()
        for j in range(fh):
            for i in range(fw):
                r = int(math.floor(y0 + j + 0.5 - GY0))
                c = int(math.floor(x0 + i + 0.5 - GX0))
                if 0 <= r < len(FACE) and 0 <= c < 15:
                    col = fn(r, c)
                    if col is not None:
                        px[u0 + i, v0 + j] = col
    return dec


def diff_glow(rows, gpal_top, under_rows, gpal_under):
    """Glow of a plane that sits in front of another plane over the same window: its own glow minus what the plane
    behind already adds (the glow pass has no depth, so both always add up)."""
    def dec(img, u0, v0, w, h):
        px = img.load()
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                tgt = gpal_top.get(ch, (0, 0, 0))
                und = gpal_under.get(under_rows[j][i], (0, 0, 0))
                px[u0 + i, v0 + j] = gout(tuple(max(0, tgt[k] - und[k]) for k in range(3)))
    return dec


def _slice(grid, x0, y0, w, h):
    rows = []
    for j in range(h):
        gy = int(math.floor(y0 + j + 0.5 - GY0))
        row = ''
        for i in range(w):
            gx = int(math.floor(x0 + i + 0.5 - GX0))
            row += grid[gy][gx] if 0 <= gy < len(grid) and 0 <= gx < len(grid[gy]) else '/'
        rows.append(row)
    return rows


NOSE_CELLS = {(r, c) for r in (8, 9, 10) for c in (6, 7, 8)}
BACK_PAL = dict(OPAQUE)
BACK_PAL.update({'.': A(SKIN[6], 255), '_': None})


def backing_rows(x0, y0, w, h):
    """Art of a window backing: the face cells (camouflage) round a solid skin core; nothing under the nose (the
    nose cube stands in front of those cells and a backing that sorted after it must not cut into it)."""
    rows = _slice(FACE, x0, y0, w, h)
    out = []
    for j, row in enumerate(rows):
        gy = int(math.floor(y0 + j + 0.5 - GY0))
        line = ''
        for i, ch in enumerate(row):
            gx = int(math.floor(x0 + i + 0.5 - GX0))
            line += '_' if (gy, gx) in NOSE_CELLS or ch == '/' else ch
        out.append(line)
    return out


def face_decals(x0, y0, w, h, glow=True):
    d = {'front': pixelart(_slice(FACE, x0, y0, w, h), OPAQUE, anchor='topleft')}
    if glow:
        d['eyes:front'] = cell_decal(face_glow, x0, y0, w, h)
    return d


# rosary looped from the belt on the front gore: walnut beads, a small cross above the dissolving hem.  It is painted
# on a plane the size of the gore (mostly transparent), so its centroid matches the gore's and it always sorts in
# front of it.
ROSARY = [
    "o.o",
    ",.,",
    "o.o",
    ".o.",
    ".,.",
    ".o.",
    ".+.",
    "+X+",
    ".+.",
    ".+.",
]
ROS_PAL = {'o': A(WOOD[5], A_WOOD), ',': A(LEATHER[3], 200), '+': A(WOOD[5], A_WOOD), 'X': A(LIGHT[5], 245)}
ROS_GLOW = gpal({'o': (30, 24, 18), '+': (52, 42, 32), 'X': (170, 150, 120)})

DEFAULT_MAT = habit_mat
FOCUS = 'head'

# robe hull at the hips (y -11.5): octagon vertices (x, z), front edge first, going round toward her left (+X)
HULL = [(-4.5, -5.0), (4.5, -5.0), (7.0, -2.0), (7.0, 2.0), (4.5, 5.0), (-4.5, 5.0), (-7.0, 2.0), (-7.0, -2.0)]
PANEL_NAMES = ['skirt_front', 'skirt_front_left', 'skirt_left', 'skirt_back_left', 'skirt_back', 'skirt_back_right',
               'skirt_right', 'skirt_front_right']
# streamers per panel: (offset along the panel from its centre, width, top y, height)
STREAMERS = {
    'skirt_front': ((-2.5, 3, 10, 12), (2.0, 3, 12, 10)),
    'skirt_front_left': ((0.0, 3, 11, 10),),
    'skirt_left': ((0.0, 3, 9, 12),),
    'skirt_back_left': ((0.0, 3, 11, 10),),
    'skirt_back': ((-2.5, 3, 11, 11), (2.0, 3, 9, 12)),
    'skirt_back_right': ((0.0, 3, 10, 11),),
    'skirt_right': ((0.0, 3, 11, 11),),
    'skirt_front_right': ((0.0, 3, 9, 12),),
}
ROBE_TOP = -11.4
ROBE_H = 29        # robe gores hang from y -11.4 to y 17.6
HALO_R = 17                    # ring plane radius (the ring itself at R - 2.6, its haze to R)
HALO_PIVOT = (0.0, -45.0, 0.0)  # the centre of the head (veil included)
HALO_UP, HALO_D = 5.0, 9.5      # ring centre 5 above the pivot, the plane 9.5 behind it (the nape ends at z 7)
EYE_Z = -7.0       # open eyes / closed lips: IN the plane of the face front (z -7), filling its windows
LID_Z = -7.05      # closed lids / speech frame when speaking: 0.05 in front of it
MOUTH_REST_DZ = 0.25   # the speech frame rests at LID_Z + 0.25 = -6.8, 0.2 behind the opaque lips
BACK_Z = -6.95     # skin backings behind the windows (in front of the hidden states at -6.8)


def build():
    global RIG, MODEL
    GLOW.clear()
    _HALO_CLEAR.clear()
    _HAND_BACK.clear()
    r = Rig()
    RIG = r

    def bone(name, pivot, parent=None, rot=(0, 0, 0), mat=None):
        return r.bone(name, pivot, parent=parent, rot=rot, mat=mat)

    def box(bone_, frm, size, mat=None, name=None, inflate=0.0, decals=None, glow=True, **attrs):
        dec = dict(decals or {})
        if glow:
            for kk, fn in GLOW_ALL.items():
                dec[kk] = chain(dec[kk], fn) if kk in dec else fn
        c = r.box(bone_, frm, size, mat=mat, inflate=inflate, decals=dec)
        c.name = name
        c.side = attrs.get('side', 0)
        c.panel = attrs.get('panel', -1)
        c.seed = attrs.get('seed', 0)
        return c

    def fbox(bone_, frm, size, name, glow=True):
        return box(bone_, frm, size, mat=skin_mat, name=name,
                   decals=face_decals(frm[0], frm[1], size[0], size[1], glow))

    def plane(bone_, frm, size, name, rows, base_pal, glow_dec):
        dec = {'front': pixelart(rows, base_pal, anchor='topleft')}
        if glow_dec is not None:
            dec['eyes:front'] = glow_dec
        return box(bone_, frm, size, mat=none_mat, name=name, glow=False, decals=dec)

    # ---------------- body: root at the waist; leather cincture
    bone('body', (0, -12, 0), mat=habit_mat)
    box('body', (-8, -13.5, -5), (16, 2, 10), name='belt')

    # ---------------- robe: eight flared gores round an octagonal hull, each dissolving into light, with light
    # streamers trailing below.  Each gore is authored facing -Z at its pivot and yawed into place.
    for k, name in enumerate(PANEL_NAMES):
        (x0, z0), (x1, z1) = HULL[k], HULL[(k + 1) % 8]
        ln = math.hypot(x1 - x0, z1 - z0)
        tx, tz = (x1 - x0) / ln, (z1 - z0) / ln
        nx, nz = tz, -tx                                    # outward normal (hull runs clockwise seen from above)
        off = 0.5 if k % 2 == 0 else 1.3                    # the diagonal gores lie over the edges of the others
        cxm, czm = (x0 + x1) / 2 + nx * off, (z0 + z1) / 2 + nz * off
        yaw = math.degrees(math.atan2(-nx, -nz))            # local -Z -> (nx, nz)
        flare = -7.0 if k % 2 == 0 else -9.0
        bone(name, (cxm, ROBE_TOP, czm), parent='body', rot=(flare, yaw, 0), mat=habit_mat)
        wd = int(round(ln)) if k % 2 == 0 else int(math.ceil(ln)) + 2
        box(name, (cxm - wd / 2, ROBE_TOP, czm - 0.5), (wd, ROBE_H, 1), name='panel', panel=k)
        for si, (off, sw, sy, sh) in enumerate(STREAMERS[name]):
            box(name, (cxm + off - sw / 2, sy, czm - 0.6), (sw, sh, 0), mat=light_mat, name='streamer',
                seed=k * 7 + si)
        if name == 'skirt_front':
            dx = int(round(1.5 - (cxm - wd / 2)))
            box(name, (cxm - wd / 2, ROBE_TOP, czm - 0.75), (wd, ROBE_H, 0), mat=none_mat, name='rosary', glow=False,
                decals={'front': pixelart(ROSARY, ROS_PAL, anchor='topleft', dx=dx, dy=1),
                        'eyes:front': pixelart(ROSARY, ROS_GLOW, anchor='topleft', dx=dx, dy=1)})

    # ---------------- chest: slim bodice under the rounded white guimpe, the small wooden cross on its cord
    bone('chest', (0, -12, 0), parent='body', mat=habit_mat)
    box('chest', (-7, -31.5, -4), (14, 20, 8), name='bodice')
    box('chest', (-10, -31.5, -6), (20, 10, 9), mat=linen_mat, name='guimpe')
    box('chest', (-0.5, -29, -7), (1, 5, 1), mat=wood_mat, name='cross')
    box('chest', (-1.5, -28, -7), (1, 1, 1), mat=wood_mat, name='cross')
    box('chest', (0.5, -28, -7), (1, 1, 1), mat=wood_mat, name='cross')

    # back veil: a centre panel with a pointed hem and two side panels stepped 0.7 forward round the back (one bone:
    # the side panels' own sway was too small to be worth two bones)
    bone('veil', (0, -33, 4.9), parent='chest', rot=(4, 0, 0), mat=habit_mat)
    box('veil', (-4, -33, 4.9), (8, 27, 1), name='veil_c')
    for side, sx in (('right', -1), ('left', 1)):
        box('veil', (4 if sx > 0 else -9, -33, 4.2), (5, 21, 1), name='veil_s', side=sx)

    # ---------------- neck (inside the wimple)
    bone('neck', (0, -32, 0), parent='chest', mat=linen_mat)
    box('neck', (-4, -33, -4), (8, 2, 7), mat=linen_mat, name='neckband')

    # ---------------- head: face window x -7.5..7.5 / y -51..-34
    bone('head', (0, -33, 1.5), parent='neck', mat=skin_mat)
    fbox('head', (-7.5, -51, -7), (15, 17, 12), 'skull')
    fbox('head', (-1.5, -43, -8), (3, 3, 1), 'nose', glow=False)
    fbox('head', (-0.5, -42, -9), (1, 2, 1), 'nose', glow=False)
    box('head', (-8.5, -53, -8.5), (17, 2, 14), mat=linen_mat, name='band')     # overhangs the brow by a texel
    box('head', (-8.5, -51, -7.5), (1, 17, 12), mat=linen_mat, name='coif_side', side=-1)
    box('head', (7.5, -51, -7.5), (1, 17, 12), mat=linen_mat, name='coif_side', side=1)
    box('head', (-8.5, -34, -7.5), (17, 2, 10), mat=linen_mat, name='chinwrap')
    # the coif tucked in round the oval: one-texel steps in front of the face's linen corners (temples and jaw), so
    # the oval has depth and still reads in 3/4 and from below
    for sx in (-1, 1):
        box('head', (-7.5 if sx < 0 else 4.5, -51, -7.5), (3, 1, 1), mat=linen_mat, name='step')
        box('head', (-7.5 if sx < 0 else 5.5, -36, -7.5), (2, 2, 1), mat=linen_mat, name='step')
    # the veil over the head: a dome in three steps (19 -> 17 -> 13 wide) and the nape
    box('head', (-9.5, -55, -7), (19, 2, 14), mat=habit_mat, name='crown1')
    box('head', (-8.5, -56, -6), (17, 1, 12), mat=habit_mat, name='crown2')
    box('head', (-6.5, -57, -4.5), (13, 1, 9), mat=habit_mat, name='crown3')
    box('head', (-8.5, -53, 6), (17, 20, 1), mat=habit_mat, name='nape')

    # the open eyes and the closed lips: opaque planes filling the windows of the skull front (same plane)
    ex = {s: GX0 + c for s, c in EYE_COLS.items()}
    ey = GY0 + EYE_ROWS[0]
    eyes = {'right': EYE_R, 'left': EYE_L}
    lids = {'right': LID_R, 'left': LID_L}
    for s in ('right', 'left'):
        plane('head', (ex[s], ey, EYE_Z), (5, len(EYE_R), 0), 'eye_' + s, eyes[s], OPAQUE,
              pixelart(eyes[s], gpal(EYEGLOW), anchor='topleft'))
    mx, my = GX0 + MOUTH_COL, GY0 + MOUTH_ROW
    plane('head', (mx, my, EYE_Z), (5, 4, 0), 'lips', LIPS, OPAQUE, pixelart(LIPS, gpal(GLOWPAL), anchor='topleft'))

    # backings: one texel larger than each window all round, 0.05 behind it, same centre (so always sorted behind the
    # planes in the window).  Any rasterisation crack where a window edge meets its plane shows skin, never the dark
    # inside of the head; the ring outside the window repeats the face texels under it, so when it sorts in front of
    # the face it is invisible.  No glow.
    for wx, wy, ww, wh in ((ex['right'], ey, 5, len(EYE_R)), (ex['left'], ey, 5, len(EYE_R)), (mx, my, 5, 4)):
        plane('head', (wx - 1, wy - 1, BACK_Z), (ww + 2, wh + 2, 0), 'backing', backing_rows(wx - 1, wy - 1, ww + 2, wh + 2),
              BACK_PAL, None)

    # the closed lids: opaque planes just in front of the same windows (same centroids as the eye planes)
    bone('eyelids', (0, ey, LID_Z), parent='head', mat=none_mat)
    for s in ('right', 'left'):
        plane('eyelids', (ex[s], ey, LID_Z), (5, len(LID_R), 0), 'lid', lids[s], OPAQUE,
              diff_glow(lids[s], GLOWPAL, eyes[s], EYEGLOW))

    # speech frame: tucked 0.2 behind the opaque lips at rest; 'speak' brings it 0.05 in front of the face
    mz = LID_Z + MOUTH_REST_DZ
    bone('mouth', (0, my, mz), parent='head', mat=none_mat)
    plane('mouth', (mx, my, mz), (5, 4, 0), 'mouth_open', MOUTH_OPEN, OPAQUE,
          diff_glow(MOUTH_OPEN, GLOWPAL, LIPS, GLOWPAL))

    # the halo: a ring plane on a pivot at the CENTRE of the head, HALO_D behind it and HALO_UP above it.  Java
    # billboards the bone to the camera every frame, so the ring is always a circle and always behind the head as
    # seen from the camera (see ANIM_NOTES)
    px, py, pz = HALO_PIVOT
    bone('halo', HALO_PIVOT, parent='head', mat=halo_mat)
    box('halo', (px - HALO_R, py - HALO_UP - HALO_R, pz + HALO_D), (2 * HALO_R, 2 * HALO_R, 0), name='halo')

    # veil sides: an upper plate hugging the coif (child of head) and a lower drape resting on the back of the
    # shoulder (child of chest: it does not lever with the head)
    for side, sx in (('right', -1), ('left', 1)):
        vs, dr = f'veil_{side}', f'veil_drape_{side}'
        bone(vs, (9.0 * sx, -53, 0.5), parent='head', mat=habit_mat)
        box(vs, (9.0 * sx - 0.5, -53, -5), (1, 15, 12), name='veil_side', side=sx)
        bone(dr, (9.5 * sx, -38, 6.5), parent='chest', rot=(0, 0, -12 * sx), mat=habit_mat)
        box(dr, (9.5 * sx - 1.0, -38, 3.0), (2, 15, 5), name='drape', side=sx)       # ends 0.5 before the halo

    # ---------------- arms: upper sleeve, forearm, open bell sleeve, slender luminous hands
    for side, sx in (('right', -1), ('left', 1)):
        arm, fa, sl, hand = f'{side}_arm', f'{side}_forearm', f'{side}_sleeve', f'{side}_hand'
        ax = 12.5 * sx
        bone(arm, (ax, -30, 0.5), parent='chest', rot=(-3, 0, -7 * sx), mat=habit_mat)
        box(arm, (ax - 2.5 + 0.25 * sx, -31, -2), (5, 12, 5), name='sleeve_up', side=sx)
        bone(fa, (ax, -19.5, 0.5), parent=arm, rot=(-8, 0, 0), mat=habit_mat)
        box(fa, (ax - 2, -19.5, -1.5), (4, 11, 4), name='forearm', side=sx)
        box(fa, (ax - 2, -9.75, -1.5), (4, 1, 4), mat=linen_mat, name='undercuff', inflate=0.25)
        bone(sl, (ax, -15, 0.5), parent=fa, mat=habit_mat)
        box(sl, (ax - 3, -15, -2.5), (6, 3, 6), name='bell_top', side=sx)
        box(sl, (ax - 5, -12, -3.5), (10, 9, 8), name='bell', side=sx)            # one flared tier
        box(sl, (ax - 4.5, -9, 5.8), (9, 12, 0), name='wing', side=sx)          # the hanging back of the sleeve
        bone(hand, (ax, -8.5, 0.5), parent=fa, rot=(0, -30 * sx, 0), mat=hand_mat)
        box(hand, (ax - 1, -8.5, -1.5), (2, 5, 4), name='palm')
        box(hand, (ax - 0.5 * sx - 0.5, -7, -2.5), (1, 4, 1), name='thumb')
        for zz, ln in ((-1.5, 4), (-0.5, 5), (0.5, 4), (1.5, 3)):
            box(hand, (ax - 0.5, -3.5, zz), (1, ln, 1), inflate=-0.1, name='finger')
        # the light in her palm: a glow-only shell round the hand, on its own bone (hidden in 'bow')
        hl = f'{side}_hand_light'
        bone(hl, (ax, -8.5, 0.5), parent=hand, mat=hand_light_mat)
        box(hl, (ax - 1, -8.5, -2.5), (2, 10, 5), inflate=0.3, name='hand_light', side=sx)

    # zero-thickness planes with transparent edges get their own gutter-separated strip at the bottom of the sheet,
    # so no neighbouring texel of the packed atlas can bleed into them as a hairline
    planes = [c for b in r.bones.values() for c in b.cubes if 0 in c.size]
    planes.sort(key=lambda c: -c.uv_size()[1])
    rows = []
    for c in planes:
        w, h = c.uv_size()
        if not rows or rows[-1][0] + w > 256:
            rows.append([0, h, []])
        rows[-1][2].append((c, rows[-1][0]))
        rows[-1][0] += w + 1
    strip = sum(rh + 1 for _, rh, _ in rows)
    for tex_h in range(128, 257, 16):
        v = tex_h - strip
        for _, rh, items in rows:
            for c, uu in items:
                c.uv = (uu, v)
            v += rh + 1
        m = Model('clara', 256, tex_h, r.roots)
        try:
            m.pack()
        except RuntimeError:
            for b in m.bones():
                for c in b.cubes:
                    if 0 not in c.size:
                        c.uv = None
            continue
        break
    m.scale = 0.5
    m.render_type = 'entityTranslucentEmissive'
    MODEL = m
    return m


def _mirror(right):
    """Pose entries for both sides from the right-side values (mirror across x = 0: yRot, zRot and dx flip)."""
    out = {}
    for name, v in right.items():
        x, y, z, dx, dy, dz = (list(v) + [0, 0, 0, 0, 0, 0])[:6]
        out[name.replace('*', 'right')] = (x, y, z, dx, dy, dz)
        out[name.replace('*', 'left')] = (x, -y, -z, -dx, dy, dz)
    return out


def _skirts(front, side, back, diag_front=None, diag_back=None):
    df = front if diag_front is None else diag_front
    db = back if diag_back is None else diag_back
    vals = (front, df, side, db, back, db, side, df)
    return {n: (v, 0, 0, 0, 0, 0) for n, v in zip(PANEL_NAMES, vals)}


# eyes OPEN in a pose table: the lids slide 0.25 back, behind the opaque eye planes (hidden in the base pass).  In
# game also set eyelids.visible = false (see ANIM_NOTES): hidden planes still add their glow.
EYES_OPEN = (0, 0, 0, 0, 0, 0.25)
MOUTH_SPEAK = (0, 0, 0, 0, 0, -MOUTH_REST_DZ)

POSES = {
    # ascension, the money shot: she rises, arms open wide and lifted, elbows soft, palms up and out receiving the
    # light, the face only SLIGHTLY lifted (chest 0 + neck -0.04 + head -0.1 = -0.14 rad, ~8 deg: from below, the face
    # that has just opened its eyes stays in view), eyes OPEN; the bells hang straight down from the forearms with
    # gravity, their hanging backs facing forward; the veil streams back (the drapes with it), the hem trails below
    'rise': {
        'body': (0, 0, 0, 0, -3.0, 0),
        'neck': (-0.04, 0, 0, 0, 0, 0),
        'head': (-0.1, 0, 0, 0, 0, 0),
        'eyelids': EYES_OPEN,
        'veil': (0.14, 0, 0, 0, 1.5, 0),
        **_skirts(-0.08, -0.05, 0.12),
        **_mirror({
            'veil_*': (0, 0, 0.08),
            'veil_drape_*': (0.1, 0, 0),
            '*_arm': (0.206, 0.11, 1.867),
            '*_forearm': (-0.287, 1.003, -0.063),
        }),
    },
    # 'Gracias por venir': eyes open, head a little lifted and tilted, the speech frame in front of the lips
    'speak': {
        'head': (-0.08, 0, 0.06, 0, 0, 0),
        'eyelids': EYES_OPEN,
        'mouth': MOUTH_SPEAK,
    },
    # gratitude: a gentle bow of the head, tilted with tenderness, over hands joined in prayer at the sternum (in
    # front of the guimpe and the cross), eyes closed; the bells slide back toward the elbows and hang
    'bow': {
        'chest': (0.08, 0, 0, 0, 0, 0),
        'neck': (0.07, 0, 0, 0, 0, 0),
        'head': (0.24, 0, 0.1, 0, -1.0, -0.5),
        **_skirts(0.03, 0.03, 0.03),
        **_mirror({
            '*_arm': (-0.938, -0.135, -0.051),
            '*_forearm': (0.197, -1.123, -1.211),
            '*_sleeve': (1.255, 0, -1.002, 0, -0.06, 0),
            '*_hand': (-0.837, -0.145, 1.522),
        }),
    },
}
# 'rise': each bell hangs from its raised forearm with gravity -- its world rotation is a pure roll in the frontal plane
# (no yaw, no pitch), swinging this far (radians) outward from straight down -- so from the front it is a flared
# trapezoid of cloth hanging under the arm, and its hanging back faces the viewer (never edge-on to a low camera)
RISE_SLEEVE_ROLL = 0.18
# 'rise': the palms (their inner face) turn to face forward and a little down and out -- toward the people below her,
# never in toward her own head (the palm light has no depth and would shine through it in a side view).  Right hand;
# the left mirrors x.  The fingers keep the authored direction (up and out along the arm).
RISE_PALM = (-0.085, 0.37, -0.92)


def _euler_zyx(R):
    """(xRot, yRot, zRot) with mcmodel.rot_matrix(x, y, z) == R (MC's Z*Y*X order)."""
    y = math.asin(max(-1.0, min(1.0, -R[2, 0])))
    return math.atan2(R[2, 1], R[2, 2]), y, math.atan2(R[1, 0], R[0, 0])


def _solve_poses():
    """Pose entries that are derived, not authored: (1) every pose's 'halo' entry cancels the summed rotation of
    body -> chest -> neck -> head, so in the tables (and any tool that cannot billboard) the ring stands upright and
    faces straight forward -- the billboard solution for a camera in front of her; in game Java overwrites it every
    frame with the real camera (ANIM_NOTES); (2) the 'rise' bells hang straight down, facing forward."""
    m = build()
    bones = {b.name: b for b in m.bones()}
    for name, pose in POSES.items():
        R = posed_matrix(bones['head'], pose)[:3, :3]
        pose['halo'] = tuple(round(v, 4) for v in _euler_zyx(R.T)) + (0, 0, 0)
    rise = POSES['rise']
    for side, sx in (('right', -1), ('left', 1)):
        R = posed_matrix(bones[f'{side}_forearm'], rise)[:3, :3]
        Rt = rot_matrix(0.0, 0.0, -sx * RISE_SLEEVE_ROLL)
        rise[f'{side}_sleeve'] = tuple(round(v, 4) for v in _euler_zyx(R.T @ Rt)) + (0, 0, 0)
        hb = bones[f'{side}_hand']
        Rw = posed_matrix(hb, rise)[:3, :3]
        fy = Rw @ np.array([0.0, 1.0, 0.0])                                   # the fingers' direction, kept
        n = np.array(RISE_PALM) * np.array([-sx, 1.0, 1.0])                  # mirrored for the left hand
        n = n - fy * (n @ fy)
        n /= np.linalg.norm(n)
        px = n if sx < 0 else -n                                              # palm = east face (right) / west (left)
        Rnew = np.stack([px, fy, np.cross(px, fy)], axis=1)
        Rp = posed_matrix(hb.parent, rise)[:3, :3]
        tot = _euler_zyx(Rp.T @ Rnew)
        rest = [math.radians(a) for a in hb.rot]
        rise[f'{side}_hand'] = tuple(round(tot[i] - rest[i], 4) for i in range(3)) + (0, 0, 0)


_solve_poses()


def _n(x):
    s = ('%.3f' % x).rstrip('0').rstrip('.')
    return '0' if s in ('-0', '') else s


def _pv(pose, bone):
    """A POSES entry formatted for the notes: (xRot, yRot, zRot) or (xRot, yRot, zRot, dx, dy, dz)."""
    v = POSES[pose].get(bone)
    if v is None:
        return '0'
    v = (list(v) + [0] * 6)[:6]
    s = ', '.join(_n(x) for x in v[:3])
    if any(abs(x) > 1e-9 for x in v[3:]):
        s += ', ' + ', '.join(_n(x) for x in v[3:])
    return '(' + s + ')'


def _counts():
    m = build()
    return sum(len(b.cubes) for b in m.bones()), sum(1 for _ in m.bones()), m.tex_w, m.tex_h


_C = _counts()

ANIM_NOTES = f"""
Clara (the freed soul of Sor Maria) -- animation contract.  Angles in radians, ADDED to the rest pose; offsets
(dx, dy, dz) in model texels at 2x density (inside scale 0.5: 2 texels = 1 vanilla pixel).  t = ageInTicks.
{_C[0]} cubes, {_C[1]} bones, texture {_C[2]} x {_C[3]}.

POSES ARE DATA: the exact values live in the generated POSE_RISE / POSE_SPEAK / POSE_BOW tables (apply them with
HauntModel.apply(pose, weight) and blend the weights).  The numbers quoted below are copied from those tables when
this file is built; if they ever disagree, the tables win.  Mirrored pairs: the left side negates yRot, zRot, dx.
Some entries are DERIVED when the file is built (never hand-edit them): every pose's 'halo' entry (the billboard
solution for a camera straight in front), and the 'rise' sleeve and hand entries (bells hanging with gravity, palms
turned to the people below).

RENDERING.  Base: RenderType.entityTranslucentEmissive(texture) -- no lightmap, alpha baked per material (the face
front and its feature planes 255, other skin 235, linen 226, bells {A_BELL}, head veil {A_HEADVEIL}, back veil and drapes
{A_VEIL}, habit {A_HABIT} at the chest -> ~130 toward the light, sleeves {A_SLEEVE}: her body visibly ghosts; halo haze / hem
haze / motes / streamers fading to 0; nothing below alpha 28 is painted, MC discards < 0.1).  Glow: the 'eyes' layer
(clara_eyes.png) through GlowLayer / RenderType.eyes (additive, back faces culled): the face and lids (~0.12-0.23 of
each skin tone), the linen (~0.24), a warm inner light in the whole habit (~0.3 of a warm grey at the chest rising to
~0.66 at the hem), a warm-white 1-texel rim along the outer silhouette (the veil dome's outline, the line of the
shoulders and the upper sleeves, the drapes' sloped hem and back edge, the back veil's hem), the pearl band where the
robe dissolves and the cream haze under it (also on the gores' inner faces, softer), the motes, the streamers (both
faces), the upper half of the halo ring, and the palm lights in 'rise'.  Near-black glow texels are alpha 0 and dim
ones partly transparent (additive blending ignores alpha; the portrait / gallery compositing does not).
IMPORTANT: neither pass writes depth.  The translucent base pass is sorted PER QUAD by centroid, and the glow pass
adds every texel of every VISIBLE part, even one hidden behind another.  Hence the rules (keep them when editing):
  * Features that change sit on planes over WINDOWS cut out of the skull front, centred exactly on them: open eyes
    and closed lips in the plane of the face (z {EYE_Z}), closed lids (and the speech frame while speaking) just in
    front of it (z {LID_Z}); hidden states sit 0.2 behind (z {LID_Z + MOUTH_REST_DZ:.2f}).  A skin 'backing' plane
    0.05 behind each window (z {BACK_Z}, one texel larger, same centre) closes any rasterisation crack.
  * Never hide a part by folding it into the body (a folded plane shows through the translucent face).  Hide it
    with ModelPart.visible = false -- that also removes its glow, which a pose offset alone does not.
  * Rims sit only on faces that nothing dense can stand in front of (no rim on the drapes' fronts or the veil sides'
    face edges -- they lie behind the head); the halo ring glows only where no dense part of her (head, veil over
    the head, linen, cincture) can cover it from ANY camera direction; the palm lights exist only in 'rise'.
The base pass keeps MC's two fixed cardinal lights (only the lightmap is skipped), so a vertical face is ~0.75
bright when she faces north / south and ~0.5 facing east / west: place her (and turn the ending camera) so she faces
along the Z axis.  The face glow (~0.2 of the skin) brings the face to ~0.98 of its painted colour when she faces the
camera -- luminous, not clipped; in 'bow' the face is in its own shadow (~0.55) and brightens as she lifts it --
open the eyes right after the lift and the light seems to come into her face.
Fade her in / out with the vertex alpha (0 -> 1 over 40 ticks) and scale the glow layer's colour with the same
factor.  She is NOT scary: every motion is slow, soft and continuous (sine eases, no snaps, no twitches).  She never
walks: the robe ends in light.  Poses: rise, speak, bow.

ENDING BEAT (suggested): appear in 'bow' with alpha 0 -> 1 and body dy +6 -> 0 (40 ticks)  ->  lift the head out of
the bow (30 ticks)  ->  OPEN THE EYES (eyelids, ~8 ticks, see below)  ->  'speak' while clara.voz plays ("Gracias
por venir.  Digale a Teresita que no fue su culpa.")  ->  blend to 'rise' over 60 ticks while she floats up 2-3
blocks (show the palm lights when the 'rise' weight passes 0.5)  ->  white flash, alpha -> 0.

ROOT
* body -- root at the waist (pivot y -12): the leather cincture.  HOVER: dy = -1.0 + sin(t*0.06)*1.0 (the streamers
  stay 1-3 texels above the floor), xRot sin(t*0.045)*0.02, yRot sin(t*0.02)*0.04.  Rise {_pv('rise', 'body')},
  then keep adding dy for the ascension.  Bow / speak: 0.

ROBE -- eight gores round an octagonal hull, children of body, pivots at the hips (y -11.4); rest flare -7 deg
(front, sides, back) / -9 deg (the four diagonal gores, which lie over the others' edges).  k = 0..7: skirt_front,
skirt_front_left, skirt_left, skirt_back_left, skirt_back, skirt_back_right, skirt_right, skirt_front_right.  Each
gore carries its light streamers (planes) so they sway with it; skirt_front also carries the looped rosary with its
small cross (a gore-sized plane, mostly transparent).  The dissolve is painted, no bone needed.
* skirt_* -- slow underwater ripple, out of phase: xRot += sin(t*0.07 + k*0.785)*0.05 (local x = outward flare:
  negative opens the gore), zRot += cos(t*0.058 + k)*0.015.  Rise: front {_pv('rise', 'skirt_front')}, sides
  {_pv('rise', 'skirt_left')}, back {_pv('rise', 'skirt_back')} (the hem trails below her as she lifts).  Bow: all
  {_pv('bow', 'skirt_front')} (the robe settles).  Keep every gore between -0.3 and +0.25 so the diagonal gores stay
  outside the others.

TORSO
* chest -- slim bodice (smoky wool, hand-placed folds gathered into the cincture) under the rounded white guimpe,
  the small wooden cross on its cord.  Breathing (she breathes even as a soul; it reads as alive): xRot
  sin(t*0.05)*0.015.  Rise {_pv('rise', 'chest')} (upright: no arch, so the face stays toward a camera below her),
  bow {_pv('bow', 'chest')}.
* veil -- the back veil: a centre panel (nape to hips, pointed hem) and two side panels stepped 0.7 forward round
  the back (static cubes of this bone), child of chest, rest +4 deg so it clears the gores.  Hangs with gravity:
  xRot = -chestXRot*0.6 + sin(t*0.05 - 1.2)*0.03.  Rise {_pv('rise', 'veil')} (streams back), bow 0.
* neck -- inside the wimple (a linen band fills the gap when the head lifts).  Follows the head softly: 30 % of the
  look pitch.  Rise {_pv('rise', 'neck')}, bow {_pv('bow', 'neck')}.
* head -- face cube with the 15 x 17 face (made oval by the coif linen and its one-texel steps; windows for the eyes
  and the mouth), the nose, the white coif band (overhanging the brow by a texel) / sides / chin wrap, the veil dome
  (three chamfered steps, rim-lit outline), the nape, and the static planes eye_right / eye_left (open eyes with
  calm brows) and lips (closed mouth) in the windows, with their skin backings.  FOCUS bone.  Looks at the player
  with gentle easing (yaw clamp +-0.6, pitch +-0.35, lerp 0.08 per tick).  Idle: a slow tilt zRot sin(t*0.03)*0.05.
  Speak {_pv('speak', 'head')}.  Bow {_pv('bow', 'head')}: a gentle bow tilted with tenderness.
  Rise {_pv('rise', 'head')}: only SLIGHTLY lifted (with the neck, -0.14 rad, ~8 deg).  DURING THE ASCENSION THE
  LOOK-AT PITCH OVERRIDES THE POSE: as she rises above the player, ease the head pitch from the pose's lift to the
  look-at pitch (positive xRot = she looks DOWN at the player, up to +0.35; neck takes 30 % of it), so the face that
  has just opened its warm brown eyes stays turned to the player below instead of disappearing behind the chin.
* eyelids -- the two CLOSED-state planes (sad brows, inner ends lifted, over peaceful U-shaped lash curves), opaque,
  0.05 in front of the face, centred on the 5 x 7 eye windows (brows included); pivot on their top edge
  (y {GY0 + EYE_ROWS[0]}).  REST = EYES CLOSED.  To OPEN: yScale 1 -> 0 over ~8 ticks (ease-out; the lids and the
  sad brows lift away and the calm open eyes show through), then visible = false.  To close / blink: visible = true
  and yScale 0 -> 1 (a blink = 2-3 ticks closed every 80-140 ticks while open; the brows soften again on reopening,
  which reads as a gentle sigh).  Never fold them into the head.
  The pose tables encode 'open' as {_pv('rise', 'eyelids')} (the lids slide behind the opaque eye planes) for tools
  that cannot hide parts; in game ALSO set visible = false whenever that weight is > 0.5, or the hidden lids still
  add their glow over the open eyes.  Closed in 'bow'; open in 'speak' and 'rise'.
* mouth -- the speech frame (the same smile, the lower lip dropped one row under a soft one-row opening), opaque,
  tucked 0.2 behind the opaque lips plane at rest.  REST: visible = false (it is also hidden behind the lips).
  Talking: visible = true and dz {_n(MOUTH_SPEAK[5])} (the 'speak' table: {_pv('speak', 'mouth')}) brings it 0.05 in front of
  the face; flap it with the voice (dz {_n(MOUTH_SPEAK[5])} for 2-3 ticks per syllable, or while the clara.voz amplitude is above a
  threshold) and set it back (dz 0, visible = false) when silent.
* halo -- the nimbus: ONE plane, only a white-gold ring and a soft haze outside it (everything inside the ring is
  transparent).  Child of head; its pivot is the CENTRE of the head ({HALO_PIVOT[0]:g}, {HALO_PIVOT[1]:g}, {HALO_PIVOT[2]:g} in model space at rest),
  the plane {HALO_D:g} texels behind the pivot (local +Z) and the ring centre {HALO_UP:g} above it.
  BILLBOARD IT EVERY FRAME (in the renderer, where the camera is known), so it is always a full circle and always
  behind the head as seen from the camera -- from the front, the side, behind and below:
    1. c = (camera position - halo pivot) expressed in MODEL space (undo the renderer's transform: body yaw, the
       (-1, -1, 1) flip, the 1.501 translate and scale 0.5; model space is +Y down, the face looks along -Z);
       normalise.
    2. The wanted model-space rotation M has columns X', Y', Z': Z' = -c (local -Z points at the camera),
       Y' = normalise((0, 1, 0) - (Z' . (0, 1, 0)) Z') (local +Y stays 'down'), X' = Y' x Z'.
    3. halo local rotation = inverse(R_body * R_chest * R_neck * R_head) * M, where each R is that part's CURRENT
       rotationZYX(zRot, yRot, xRot); write it back with Quaternionf.getEulerAnglesZYX -> halo.xRot / yRot / zRot.
  (Equivalent: draw the halo part on its own after the body -- translate to the pivot through the body -> head
  chain, then mulPose(cameraOrientation()) as a name tag does, plus the 180 deg Y turn so its -Z faces the camera,
  and render it with zero rotation.)  Because the plane sits {HALO_D:g} behind its pivot along the camera axis it always
  lands on the far side of the head.  The pose tables' halo entries (rise {_pv('rise', 'halo')},
  bow {_pv('bow', 'halo')}) are only the solution for a camera straight in front, for tools that cannot billboard;
  Java overwrites them.  Breathe: scale 1 + sin(t*0.08)*0.03 about the ring centre; fade its glow with the ending.
  Its glow is masked where the head, the veil over the head, the linen or the cincture can cover it from any camera
  direction (in practice the upper half glows); through the translucent cloth its light may show.
* veil_right / veil_left -- the upper veil sides hugging the coif from the crown to the jaw (child of head; front
  edge set back so the white coif, nose and chin read in profile; rounded front-bottom corner).  Sway
  zRot += sin(t*0.05 + side)*0.02; rise {_pv('rise', 'veil_right')} (right; left mirrored): open outward.
* veil_drape_right / veil_drape_left -- the lower veil drapes (2 texels thick: from the front a dark band framing the
  guimpe, never a thin 'string'), children of CHEST, hanging behind the shoulders from just under the upper veil
  sides (outside the guimpe and the sleeves) with a 12 deg outward flare and a sloped, rim-lit hem.  They do not
  follow the head (a real veil rests on the shoulders), so no counter-rotation is needed for bow / speak (0).  Rise
  {_pv('rise', 'veil_drape_right')}: they stream back a little with the veil.  Idle: xRot sin(t*0.05 + 0.6)*0.03,
  and yRot = 30 % of the head's look yaw (the veil follows the head a little).

ARMS (right_* on -X; left mirrors yRot / zRot / dx)
* right_arm / left_arm -- upper sleeve (rim-lit shoulder line and outer edge), shoulder pivot beside the guimpe
  (rest 7 deg out, 3 deg forward).  Idle: xRot sin(t*0.05)*0.03.  Rise {_pv('rise', 'right_arm')}: arms open and
  lifted above the horizontal, swept a little back (orans / ascension).  Bow {_pv('bow', 'right_arm')}.
* right_forearm / left_forearm -- inner sleeve ending in the white undercuff at the wrist; elbow pivot (rest bent
  8 deg).  Rise {_pv('rise', 'right_forearm')}: soft elbows.  Bow {_pv('bow', 'right_forearm')}: forearms up to the
  sternum.
* right_sleeve / left_sleeve -- the open bell: a small top tier and ONE flared tier (four trapezoid flaps, ~8 -> 10
  wide, corners stepping in like cloth, open below, dark lining under the top tier, a rolled hem with rounded corners -- the
  only rim), and a short rounded hanging back ('wing', a plane behind the bell).  Child of the forearm, pivot at the
  top of the bell.  It HANGS: whenever the forearm lifts, rotate it back toward gravity, lagging 6-10 ticks behind
  the arm, plus sin(t*0.06)*0.04 sway.  Rise {_pv('rise', 'right_sleeve')} (derived: the bell's world rotation is
  straight down rolled {RISE_SLEEVE_ROLL:g} rad outward -- a flared trapezoid of cloth under each raised arm, its hanging back
  facing the viewer, never edge-on).  Bow {_pv('bow', 'right_sleeve')}: with the forearms raised the bell hangs from
  the elbow.
* right_hand / left_hand -- palm, thumb and four slender fingers with rose nails; wrist pivot, rest yaw 30 deg
  (palms turned a little forward).  Rise {_pv('rise', 'right_hand')} (derived: palms face forward and a little down
  and out -- toward the people below her, never in toward her own head; the fingers point up along the arm);
  fingers breathe xRot sin(t*0.07)*0.04.  Bow {_pv('bow', 'right_hand')}: palms pressed together at the sternum,
  fingers up, in front of the guimpe and the cross.
* right_hand_light / left_hand_light -- the light in her palms: a glow-only shell round each hand (no base texels;
  it only adds light: the palm face bright, the fingertips brightest, the back of the hand a breath).  Child of the
  hand, same pivot, never animated.  visible = true ONLY while the 'rise' weight is > 0.5 (switch it on as the arms
  open; if the glow colour can be scaled, fade it in over ~10 ticks).  Hidden in 'bow' (the pressed palms would shine
  through her from behind -- the glow pass has no depth) and at rest / speak (the hands hang half inside the bells,
  which would turn into lanterns).
"""
