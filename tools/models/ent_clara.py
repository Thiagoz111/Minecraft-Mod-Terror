"""Clara -- the freed soul of Sor Maria de la Agonia (DEAD LINE, case 'convento', ending).

Authored at 2x texel density (model.scale = 0.5).  +Y down, ground y = 24, faces -Z, right_* on -X.  Centred on
x = 0, z = 0.  Veil dome top y = -57, halo ring top ~y -61 (2.6 blocks); she floats: no feet, the robe burns away into
light and the light streamers stop ~2 texels above the floor.  COUNTS (cubes, bones, texture) are printed by the
preview and repeated at the end of ANIM_NOTES.

Design
------
Clara Ines Bustos, 33, the nun the demon wore -- freed.  The SAME habit as Sor Agonia, but clean and whole: a
starched white coif and rounded guimpe; a plum-black veil rim-lit in gold; and the black wool habit itself, dark
at the chest and the upper sleeves (so the silhouette is still the nun's), lifting through rose-grey into warm
ivory toward the hem, where it turns into light -- a cream-white burning edge, gold flakes drifting off in short
diagonal trails, and gold streamers.  She is not scary: beautiful and sad, rising in the chapel at dawn with her
arms open.

Read in a thumbnail (in this order): the warm-white HALO behind the head (thin gold ring + soft glow), the luminous
oval face framed in white, the white hands coming out of dark sleeves, and a dark habit that thins into light.
Silhouette: a slender A -- a rounded veil dome (three chamfered steps), the veil set back from the face so the
white coif, nose and chin read in profile, drapes that fall behind the shoulders, a pointed back veil (centre panel
+ two side panels angled round the back), bell sleeves in three flared tiers that hang open like wings when she
lifts her arms, eight flared robe gores.

Face (15 x 17 pixel art made oval by stepping the coif linen into the corners): smooth luminous skin in broad
planes, soft brows lifted a little at the inner ends, a small closed smile and ONE tear on her left cheek.  The
features that change live on their own planes, each sitting over a WINDOW cut out of the skull front (alpha 0 in
both layers), so the translucent per-quad sort can never put the face over them:
  * eye_right / eye_left -- the OPEN eyes (head bone, in the plane of the face, filling its windows, opaque):
    heavy, tender upper lids, a 3 x 2 deep-brown iris with a cream catchlight, sclera both sides, a lit waterline.
  * eyelids -- the CLOSED lids (two opaque planes 0.05 in front of the face, centred exactly on the same windows,
    peaceful U-shaped lash curves).  The lid is always nearer than the eye plane behind it, with the same centroid,
    so the sort is always right.  Open = hide them (see ANIM_NOTES).
  * lips -- the closed mouth (head bone, in the plane of the face, opaque) and `mouth` -- the speech frame (a
    one-row opening with lifted corners), tucked 0.2 behind the lips at rest and brought 0.05 in front of the face to
    speak.

Rendering: entityTranslucentEmissive, alpha baked per material; the 'eyes' layer carries the light (see ANIM_NOTES,
RENDERING).  Faces that can never be seen, or that would lie flat on another face, are cut out; thin plates paint a
single face (the translucent pass draws it from both sides).  Volumes nest (cloth over body) with the hidden faces
culled, so no visible faces cross in the rest pose.
"""
import math

import numpy as np

from mcmodel import Model, vnoise, hash3, face_light, pick, rot_matrix
from rig import Rig
from paint import hx, mix, pixelart, chain

RIG = None

# ------------------------------------------------------------------ translucency (alpha baked per material)
A_SKIN = 235
A_LINEN = 226
A_HEADVEIL = 228
A_VEIL = 200
A_HABIT = 196      # dark habit at the chest; it thins to ~150 toward the light at the hem
A_SLEEVE = 192
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
# the habit, top: Sor Agonia's black wool, plum-black (lighter than the veil so the folds read)
HDARK = pal('#1a1420', '#241c2b', '#2f2537', '#3b2f44', '#483a52', '#574762', '#685673', '#7b6885')
# the habit, toward the hem: rose-grey -> warm ivory (the wool turning into light)
HLIGHT = pal('#5a4650', '#715a63', '#8a7279', '#a38b8f', '#bba4a4', '#cfbab5', '#e0cec6', '#ede0d6', '#f7efe6')
# the veil: still the darkest part of her, plum-grey, rim-lit
VEILC = pal('#16111d', '#221a2b', '#2f243a', '#3d304a', '#4c3d5a', '#5c4b6a', '#6e5c7c', '#82708e')
WARM = hx('#e2c7a6')        # warm sheen on the lit ridges of the light wool
# the light she dissolves into: gold -> cream -> white
LIGHT = pal('#5a3820', '#8a5a2e', '#b7843f', '#d9aa58', '#efc979', '#f9e0a2', '#fdefca', '#fff8e8', '#ffffff')
# saturated gold for flakes and streamers (keeps its chroma at low alpha)
GOLD = pal('#9a6a1e', '#c48a2a', '#e2aa3c', '#f2c45a', '#f9d982', '#fde9b0', '#fff6dc')
SHINE = [GOLD[3], GOLD[4], GOLD[5], GOLD[6], LIGHT[7]]     # streamers: light, never brown
PALE = hx('#f1e4da')        # the habit just before it becomes light
RIMC = hx('#f4d9a2')        # gold-cream rim texel on true silhouette edges
RIM_GLOW = (150, 122, 76)
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
    """Height (texels, +Y down) of the burning hem at arc position u: a slow wave plus a few pointed tongues."""
    base = 8.0 + 2.6 * math.sin(u * 0.21 + 1.3) + 1.6 * math.sin(u * 0.53 + 0.4)
    cell = 4.6
    i = math.floor(u / cell)
    f = u / cell - i
    tongue = 0.0
    if hash3(i, 7, 0, 41) > 0.55:
        tongue = (1.0 + hash3(i, 9, 0, 43) * 3.0) * math.sin(f * math.pi) ** 2
    return base + tongue


def _flakes():
    """Floating flakes peeling off the burning hem: short diagonal trails of 2x2 -> 1x2 -> 1x1 shapes (u, y, w, h,
    alpha, glow)."""
    out = []
    u = -27.0
    k = 0
    while u < 27.0:
        k += 1
        if hash3(k, 3, 1, 77) < 0.8:
            sgn = 1 if hash3(k, 5, 1, 79) > 0.5 else -1
            y0 = hem_at(u) + 1.6
            shapes = ((2, 2, 248, 1.0), (1, 2, 232, 0.85), (2, 1, 208, 0.7), (1, 1, 180, 0.55))
            for s, (fw, fh, al, gl) in enumerate(shapes):
                fu = u + sgn * (1.7 * s + hash3(k, s, 2, 81) * 0.6)
                fy = y0 + 2.4 * s + hash3(k, s, 4, 83) * 0.8
                out.append((fu, fy, fw * 1.05, fh, al, gl))
        u += 4.3 + hash3(k, 1, 1, 85) * 2.2
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
    """Robe gores: cloth -> warmer, lighter cloth -> a thin cream-white burning edge -> floating flakes and a short
    gold afterglow (the streamers are separate planes).  Every texel past the edge is LIGHT: high value, so it reads
    as light even without the glow pass."""
    x, y, z = ctx.pos
    u = robe_u(ctx)
    hem = hem_at(u)
    dist = hem - y                                            # > 0: still cloth
    if dist > 0:
        lift = clamp(1.0 - dist / 14.0)
        c = mix(c, PALE, lift * lift * 0.85)                  # the wool turns into light: paler, warmer, thinner
        emit(ctx, (190, 160, 130), lift * lift * 0.7)
        a = a - lift * 40
        if dist < 1.0:
            emit(ctx, (255, 246, 220))
            return A(LIGHT[8], 250)                          # the thin white burning edge
        if dist < 2.0:
            emit(ctx, (240, 206, 140), 0.8)
            return A(mix(PALE, GOLD[6], 0.7), a + 50)         # a gold-cream breath just inside it
        return A(c, a)
    fl = flake_at(u, y)
    if fl:
        al, gl = fl
        emit(ctx, (255, 236, 186), gl)
        return A(LIGHT[7] if gl > 0.9 else GOLD[6] if gl > 0.6 else GOLD[5], al)
    depth = -dist
    if depth < 2.2:                                           # a short pale-gold afterglow under the edge
        al = 160 * (1 - depth / 2.2)
        if al < 28:
            return None
        emit(ctx, (230, 190, 110), al / 160)
        return A(GOLD[5], al)
    return None


def habit_t(y):
    """0 = Sor Agonia's black wool (chest, upper sleeves) .. 1 = warm ivory at the hem."""
    return clamp((y + 18.0) / 30.0) ** 1.2


def cloth_glow(ctx, k=1.0):
    """Soft inner light of the habit: none in the black wool of the chest, rising toward the hem."""
    t = habit_t(ctx.pos[1])
    emit(ctx, (150, 122, 108), (0.03 + 0.55 * t ** 1.5) * k)


def rim(ctx, c, strength=1.0, glow=1.0):
    """A single gold-cream texel on a true silhouette edge; it carries the backlight in the glow layer."""
    emit(ctx, RIM_GLOW, strength * glow)
    return mix(c, RIMC, 0.6 * strength)


HIDDEN = {
    # tag -> faces never seen (cut so nothing ghosts or doubles through the translucency)
    'bodice': ('top', 'bottom'), 'belt': ('top', 'bottom'),
    'sleeve_up': ('bottom',), 'forearm': ('top', 'bottom'), 'bell_top': (),
    'crown1': ('bottom',), 'crown2': ('bottom',), 'crown3': ('bottom',),
    'nape': ('front', 'top', 'bottom', 'west', 'east'), 'veil_side': ('top',),
    'veil_c': ('top', 'bottom', 'front'), 'veil_s': ('top', 'bottom', 'front'),
    'drape': ('top', 'front'), 'panel': ('top', 'bottom', 'back'),
}
VEIL_TAGS = ('crown1', 'crown2', 'crown3', 'nape', 'veil_side', 'drape', 'veil_c', 'veil_s')
HEADVEIL_TAGS = ('crown1', 'crown2', 'crown3', 'nape', 'veil_side')
SLEEVE_TAGS = ('sleeve_up', 'forearm', 'bell_top', 'bell', 'bell_lo', 'wing')


def corner_cut(ly, lz, h, r=5.0):
    """Rounded front-bottom corner of the upper veil sides (the coif edge and the chin show in profile)."""
    if ly > h - r and lz < r:
        dx, dy = r - lz, ly - (h - r)
        return dx * dx + dy * dy > r * r
    return False


def habit_mat(ctx):
    """Habit, sleeves and veil."""
    t = tag(ctx)
    f = ctx.face
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
    ht = habit_t(y)
    a = A_HEADVEIL if t in HEADVEIL_TAGS else A_VEIL if veil else \
        (A_SLEEVE if t in SLEEVE_TAGS else A_HABIT) - 36 * ht
    v = 0.42 + face_light(ctx) * 0.9
    is_rim = False
    rim_k = 1.0
    rim_g = 1.0
    big = side and ctx.w >= 4 and ctx.h >= 4

    # ---------------- veil
    if t in ('crown1', 'crown2', 'crown3'):
        dxe, dze = min(lx, w - lx), min(lz, d - lz)
        if dxe + dze < (2.5 if t == 'crown1' else 2.0):
            return None                                       # chamfered corners: an octagonal dome, not a box
        if f == 'top':
            nxt = {'crown1': (8.5, 6.0, 6.0), 'crown2': (6.5, 4.5, 4.5)}.get(t)
            if nxt and abs(x) < nxt[0] and -nxt[1] < z < nxt[2]:
                return None                                   # under the next step of the dome
            # one dome over all three steps: lit at the crown of the head, rolling off toward every edge
            rx = abs(x) / 9.5
            rz = abs(z) / 7.0
            v += 0.16 - (rx * rx + rz * rz) * 0.26
            v += folds(ctx.i, ctx.j, ctx.w, ctx.h, n=2, converge=0.9, seed=4) * 0.35
        elif side:
            v -= 0.04
            if t == 'crown3' and f == 'back':
                is_rim = True                                 # the top of the dome seen from behind
                rim_g = 0.5
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
            if (lz > d - 1.0):
                is_rim = True                                 # the back edge
                rim_g = 0.4
        elif f == 'back':
            is_rim = True
            rim_g = 0.4
        elif f == 'front':
            v -= 0.06                                         # the dark frame round the coif
        elif f == 'bottom':
            v -= 0.12
    elif t == 'drape':
        cut = h - 4.5 * (1.0 - lz / d) ** 1.4                  # the hem slopes: short in front, long behind
        if ly > cut:
            return None
        if f == of:
            v += 0.03 + (ly / h) * 0.06
            if cut - ly < 1.0 or lz > d - 1.0 or lz < 1.0:
                is_rim = True
        elif f == 'back':
            is_rim = True
            rim_k = 0.6
        rim_g = 0.3                                           # the drapes sit behind the halo / shoulders
    elif t == 'veil_c':
        cx = (lx - w / 2) / (w / 2)
        cut = h - 6.0 * abs(cx) ** 1.3                         # pointed hem
        if ly > cut:
            return None
        if f == 'back':
            v += folds(ctx.i, ctx.j, ctx.w, ctx.h, n=2, converge=0.25, seed=7) * 0.8
            v += (ly / h) * 0.1
            if cut - ly < 1.0:
                is_rim = True
        elif f in ('west', 'east'):
            v -= 0.06                                         # seams with the side panels
    elif t == 'veil_s':
        inner = (w - lx) / w if ctx.cube.side < 0 else lx / w   # 0 at the seam with the centre panel
        cut = h - 3.0 * inner ** 1.3
        if ly > cut:
            return None
        if f == 'back':
            v += folds(ctx.i, ctx.j, ctx.w, ctx.h, n=1, converge=0.6, seed=9) * 0.8
            v += (ly / h) * 0.1
            if cut - ly < 1.0:
                is_rim = True
            elif inner > 1.0 - 1.0 / w:
                is_rim = True
                rim_g = 0.35                                  # the long outer edges: no glowing 'strings'
        elif (f == 'west') == (ctx.cube.side < 0):
            is_rim = True                                     # the outer edge
            rim_g = 0.35
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
        v += 0.04 + clamp((y + 22.0) / 10.0) * 0.08
        if big:
            v += folds(ctx.i, ctx.j, ctx.w, ctx.h, n=2, converge=0.15, seed=11) * 0.6
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
        return A(pick(LEATHER, v), 215)
    elif t == 'sleeve_up':
        if f == ("east" if ctx.cube.side < 0 else "west") and y < -21.5:
            return None                                       # lies against the guimpe
        if f == 'top':
            v += 0.05
        if big:
            v += folds(ctx.i, ctx.j, ctx.w, ctx.h, n=1, converge=0.8, seed=13) * 0.7
        outer_col = (f == 'front' and ((ctx.i == 0) if ctx.cube.side < 0 else (ctx.i == ctx.w - 1))) or \
                    (f == 'back' and ((ctx.i == ctx.w - 1) if ctx.cube.side < 0 else (ctx.i == 0)))
        if outer_col or (f == ('west' if ctx.cube.side < 0 else 'east') and ctx.i in (0, ctx.w - 1)):
            is_rim = True
            rim_g = 0.7
    elif t == 'forearm':
        if -15.0 < y < -12.0 or y > -10.0:
            return None                                       # inside the top of the bell / the cuff
        if y > -12.0:
            v -= 0.18                                         # in the shade inside the bell
    elif t == 'bell_top':
        cxr, czr = abs(lx - w / 2), abs(lz - d / 2)
        if f == 'top':
            if cxr < 2.0 and czr < 2.0:
                return None                                   # the forearm goes in here
            v += 0.06
        elif f == 'bottom':
            if cxr < 2.0 and czr < 2.0:
                return None
            ring = max(cxr, czr)
            return A(pick(LINING, 0.2 + (3.0 - ring) * 0.25), 215)   # dark ceiling of the open bell
        else:
            outer_col = ctx.i in (0, ctx.w - 1)
            if outer_col and f != ('east' if ctx.cube.side < 0 else 'west'):
                is_rim = True
                rim_g = 0.6
    elif t in ('bell', 'bell_lo'):
        if f == 'bottom':
            return None                                       # each tier opens into the next; the bell is open below
        if f == 'top':
            inner = 3.0 if t == 'bell' else 3.6
            if abs(lx - w / 2) < inner and abs(lz - d / 2) < inner:
                return None                                   # under the tier above
            v += 0.06
        else:
            v += 0.06 + ((ly + (4.0 if t == 'bell_lo' else 0.0)) / 9.0) * 0.14
            v += folds(ctx.i, ctx.j, ctx.w, ctx.h, n=2, converge=0.6, seed=31) * 0.7
            if t == 'bell_lo':
                across = (ctx.i + 0.5) / ctx.w
                cut = h - 1.8 * ((across - 0.5) * 2) ** 2     # the hem dips between the corners: soft cloth
                if ly > cut:
                    return None
                if cut - ly < 1.0:
                    v += 0.14
                    is_rim = True                             # the rolled hem of the bell catches the light
    elif t == 'wing':
        if f != 'front':
            return None                                       # one painted face (drawn from both sides)
        cx = (lx - w / 2) / (w / 2)
        cut = h - 6.5 * abs(cx) ** 1.4                         # a long rounded point: the sleeve's hanging back
        if ly > cut:
            return None
        v += folds(ctx.i, ctx.j, ctx.w, ctx.h, n=2, converge=0.3, seed=37) * 0.8 + (ly / h) * 0.18
        a = A_SLEEVE - 20 - (ly / h) * 30
        if cut - ly < 1.0:
            is_rim = True
    elif t == 'panel':
        k = ctx.cube.panel
        if f == 'front':
            v += folds(ctx.i, ctx.j, ctx.w, ctx.h, converge=0.3, seed=20 + k)
        v += clamp((y + 11.5) / 16.0) * 0.32                   # brighter toward the hem
        if f in ('west', 'east'):
            v -= 0.05
        if k in (2, 6) and f == 'front' and ctx.i in (0, ctx.w - 1):
            is_rim = True                                     # the robe's flanks
        a = A_HABIT - 36 * ht - clamp((y + 11.5) / 20.0) * 10

    if veil:
        c = pick(VEILC, v)
    else:
        if t != 'belt':
            v += clamp((y + 32.0) / 44.0) * 0.14              # the whole habit brightens from the chest to the hem
        c = mix(pick(HDARK, v), pick(HLIGHT, v), ht)          # black wool at the chest -> warm ivory at the hem
        if side and v > 0.6 and ht > 0.3:
            c = mix(c, WARM, 0.16 * ht)                       # warm sheen on the lit ridges
    if is_rim:
        c = rim(ctx, c, rim_k, rim_g)
    if not veil and t != 'belt':
        cloth_glow(ctx, 0.6 if t in SLEEVE_TAGS else 1.0)
    elif veil and not is_rim and f in ('front', 'west', 'east', 'top', 'bottom') and t in HEADVEIL_TAGS:
        emit(ctx, (60, 44, 52), 0.16)                         # the head veil is backlit a little through the cloth
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
        if f == 'bottom' and ctx.j != ctx.h - 1:
            return None                                       # only the strip in front of the face shows
        if f in ('west', 'east') and z > -5.0:
            return None                                       # under the veil sides
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
            v -= 0.02                                         # the strip over the forehead: no grey bezel
    elif t == 'coif_side':
        inner_strip = (f == 'east' and x < 0) or (f == 'west' and x > 0)
        if f == 'front' or inner_strip:
            v += 0.04 - ly / h * 0.06                         # one continuous white frame round the face oval
            if inner_strip:
                v += 0.1
        else:
            v -= 0.18
            gl = 0.6
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
    elif t == 'undercuff':
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
        return A(SKIN[5], A_SKIN)                             # top light is full: keep it level with the face front
    return A(pick(SKIN, v), A_SKIN)


_HAND_BACK = {}


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
    v = 0.76 + face_light(ctx) * 0.7
    if t == 'palm':
        if ly < 1.0:
            v -= 0.1                                          # shade under the cuff
        if ly > h - 1.0 and f in ('west', 'east'):
            v -= 0.05
    # glow only on faces that never turn backward (they would shine through her body from behind), dimmer sides
    zb = faces_back(ctx)
    gk = 0.0 if zb > 0.3 else 1.0 if zb < 0.0 else 0.55
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
HALO_YAW = (-45, -34, -22, -11, 0, 11, 22, 34, 45)           # degrees, camera round her (relative to the body)
HALO_PITCH = (-0.25, -0.1, 0.0, 0.12, 0.24, 0.35)              # radians, + = camera below her (+Y is down)


def halo_clear(i, j):
    """Glow weight 0..1 of halo texel (i, j): 1 where it is never behind any part of her -- in the rest pose and
    every exported pose, for cameras over HALO_YAW x HALO_PITCH -- fading to 0 over 2.5 texels toward the texels
    that can be.  The glow layer has no depth, so only those texels may glow (in practice the top arc above the
    dome); the rest of the ring is full-bright in the base pass and sorts correctly behind the head."""
    if not _HALO_CLEAR:
        _halo_mask()
    return _HALO_CLEAR.get((i, j), 0.0)


def _halo_mask():
    bones = list(MODEL.bones())
    hb = next(b for b in bones if b.name == 'halo')
    hc = hb.cubes[0]
    w, h, _ = hc.size
    ij = [(i, j) for j in range(h) for i in range(w)]
    loc = np.array([[hc.origin[0] + i + 0.5, hc.origin[1] + j + 0.5, hc.origin[2], 1.0] for i, j in ij])
    dirs = []
    for yaw in HALO_YAW:
        for p in HALO_PITCH:
            a = math.radians(yaw)
            dirs.append((math.sin(a) * math.cos(p), math.sin(p), -math.cos(a) * math.cos(p)))
    dirs = np.array(dirs)
    occ = np.zeros(len(ij), bool)
    occluders = [(b, c) for b in bones if b.name != 'halo' for c in b.cubes
                 if 0 not in c.size and c.name not in ('streamer',)]
    for pose in all_poses():
        P = (posed_matrix(hb, pose) @ loc.T).T[:, :3]                     # N x 3 world
        for b, c in occluders:
            M = posed_matrix(b, pose)
            R, t = M[:3, :3], M[:3, 3]
            Pl = (P - t) @ R                                                # N x 3 bone-local
            Dl = dirs @ R                                                   # K x 3
            lo = np.array(c.origin) - c.inflate
            hi = lo + np.array(c.size) + 2 * c.inflate
            with np.errstate(divide='ignore', invalid='ignore'):
                inv = 1.0 / np.where(np.abs(Dl) < 1e-9, 1e-9, Dl)           # K x 3
                t0 = (lo[None, None, :] - Pl[:, None, :]) * inv[None, :, :]
                t1 = (hi[None, None, :] - Pl[:, None, :]) * inv[None, :, :]
            tn = np.minimum(t0, t1).max(axis=2)
            tf = np.maximum(t0, t1).min(axis=2)
            hit = (tn < tf) & (tf > 0.05)
            occ |= hit.any(axis=1)
    blocked = np.array([[i + 0.5, j + 0.5] for k, (i, j) in enumerate(ij) if occ[k]])
    for k, (i, j) in enumerate(ij):
        if occ[k]:
            _HALO_CLEAR[(i, j)] = 0.0
            continue
        d = np.min(np.hypot(blocked[:, 0] - i - 0.5, blocked[:, 1] - j - 0.5)) if len(blocked) else 99.0
        _HALO_CLEAR[(i, j)] = clamp((d - 0.5) / 2.5)


HALO_WHITE = hx('#fffaf0')
HALO_CREAM = hx('#fff3d8')


def halo_mat(ctx):
    """The nimbus: a luminous cream disc behind the head inside a white-gold ring, with a soft gold haze outside.
    Bright and fairly opaque in the base pass (it has to read as light where the glow layer may not reach)."""
    if ctx.face != 'front':
        return None
    lx, ly, lz = local(ctx)
    w, h, _ = ctx.cube.size
    r = math.hypot(lx - w / 2, ly - h / 2)
    R = w / 2
    if r > R:
        return None
    kg = halo_clear(ctx.i, ctx.j)
    rr = R - 2.6                                             # the ring
    if r < 9.5:                                              # behind the head: a faint core (seen from behind)
        return A(HALO_CREAM, 50)
    ring = abs(r - rr)
    if ring < 0.75:
        emit(ctx, (255, 240, 200), kg)
        return A(HALO_WHITE, 250)
    if ring < 1.5:
        emit(ctx, (240, 200, 120), 0.9 * kg)
        return A(GOLD[5], 225)
    if r > rr:                                               # outer haze
        k = clamp(1.0 - (r - rr - 1.5) / (R - rr - 1.5))
        al = 150 * k
        if al < 28:
            return None
        emit(ctx, (210, 168, 100), k * 0.7 * kg)
        return A(GOLD[4], al)
    k = clamp((r - 9.5) / (rr - 1.5 - 9.5))                 # inner light, strongest near the ring
    al = 70 + 120 * k * k
    emit(ctx, (200, 178, 136), (0.2 + 0.5 * k) * kg)
    return A(mix(HALO_CREAM, LIGHT[6], 0.4 * k), al)


def light_mat(ctx):
    """Light streamers below the dissolving robe: a bright cream core in a gold sheath, fading out downward."""
    if ctx.face != 'front':
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
    emit(ctx, (240, 186, 100), clamp(a / 205))
    return A(c, a)


# ------------------------------------------------------------------ the face
# 15 columns (x -7.5..7.5, col c <-> x = c - 7), 17 rows (row r <-> y = -51 + r).  '.' = a window cut out of the
# skull front (alpha 0 in both layers): the eyes (rows 4-8, cols 1-5 and 9-13) and the mouth (rows 12-15, cols 5-9)
# live on their own planes behind / in front of these windows.
GX0, GY0 = -7.5, -51
FACE = [
    # 012345678901234
    "ccc667777766ccc",   # r0  y-51 soft shade under the coif band; the coif linen rounds the corners (3-2-1)
    "cc67888988876cc",   # r1  forehead, one highlight
    "c6788h888h8876c",   # r2  the brows' inner ends, lifted one row (sad, soft)
    "6Bhbb78887bbhB6",   # r3  brows falling gently outward
    "6.....787.....6",   # r4  eye windows; the bridge of the nose between them
    "6.....787.....6",   # r5
    "6.....686.....6",   # r6  shade at the inner corners of the eyes
    "6.....787.....6",   # r7
    "6.....787.....6",   # r8  [nose cube rows 8-10, cols 6-8]
    "67rr8878788rt76",   # r9  soft blush on the cheekbones; the tear's wet trail on her left cheek
    "678887686788T76",   # r10 nostril wings, the lit tip; the drop
    "677877767778Y76",   # r11 the philtrum under the nose; the drop's shine
    "67787.....78776",   # r12 mouth window
    "c6777.....7776c",   # r13 the chin rounds: 3-2-1-1
    "c6677.....7766c",   # r14
    "cc667.....766cc",   # r15
    "ccc667787766ccc",   # r16 chin, into the coif
]
assert all(len(r) == 15 for r in FACE), [len(r) for r in FACE]

# OPEN eyes (eye_right / eye_left planes, rows 4-8): heavy tender upper lids, deep-brown 3x2 irises -- the dark top
# under the lid with a cream catchlight in the middle, the pupil below it between two warm-brown texels (she looks
# straight at you) -- sclera on both sides, a lit waterline
EYE_R = [            # her right eye (viewer's left): outer corner at the left
    "67776",
    "KKKk7",
    "vIGIw",
    "qjOjv",
    "77W77",
]
EYE_L = [            # her left eye: outer corner at the right; the tear leaves the lower lid
    "67776",
    "7kKKK",
    "wIGIv",
    "vjOjq",
    "77Wt7",
]
# CLOSED lids (eyelids bone): the same windows; peaceful U-shaped lash curves
LID_R = [
    "67776",
    "78887",
    "k888q",
    "7KKK7",
    "77777",
]
LID_L = [
    "67776",
    "78887",
    "q888k",
    "7KKK7",
    "777t7",
]
# the closed mouth (lips plane, rows 12-15, cols 5-9): lifted corners, a small closed smile, shade under the lip
LIPS = [
    "m767m",
    "7uuu7",
    "76l67",
    "77677",
]
# the speech frame (mouth bone): the same smile, the lower lip dropped one row over a one-row opening
MOUTH_OPEN = [
    "m767m",
    "7uuu7",
    "7DdD7",
    "76l67",
]
EYE_ROWS, EYE_COLS = (4, 9), {'right': 1, 'left': 9}
MOUTH_ROW, MOUTH_COL = 12, 5

FPAL = {str(i): A(SKIN[i], A_SKIN) for i in range(10)}
FPAL.update({
    '.': (0, 0, 0, 0),
    'c': A(LINEN[7], A_LINEN),
    'b': A(BROW[0], A_SKIN), 'h': A(BROW[1], A_SKIN), 'B': A(BROW[2], A_SKIN),
    'K': A(LASH, 252), 'k': A(LASH2, A_SKIN), 'q': A(mix(SKIN[6], LASH2, 0.3), A_SKIN),
    'w': A(SCLERA, A_SKIN), 'v': A(SCLERA_D, A_SKIN), 'W': A(WATER, A_SKIN),
    'I': A(IRIS[1], 252), 'i': A(IRIS[2], 252), 'j': A(IRIS[3], 252), 'O': A(PUPIL, 252), 'G': A(CATCH, 255),
    'r': A(mix(SKIN[7], BLUSH, 0.4), A_SKIN),
    'u': A(LIPC[1], A_SKIN), 'U': A(LIPC[2], A_SKIN), 'm': A(mix(SKIN[6], LIPC[0], 0.45), A_SKIN),
    'l': A(mix(SKIN[7], LIPC[2], 0.6), A_SKIN), 'L': A(mix(LIPC[2], LIPC[3], 0.6), A_SKIN),
    'D': A(hx('#6a2c36'), 250), 'd': A(hx('#86434a'), 250),
    't': A(mix(SKIN[8], TEAR2, 0.35), A_SKIN), 'T': A(hx('#dcecf4'), 245), 'Y': A(TEAR, 248),
})
# the planes over the windows are OPAQUE: whatever sits behind them (open eyes behind the lids, the speech frame
# behind the lips) must never show through
OPAQUE = {k: (v[0], v[1], v[2], 255 if v[3] else 0) for k, v in FPAL.items()}


def _g(c, k):
    return (c[0] * k, c[1] * k, c[2] * k)


# emissive layer of the face: the skin glows in proportion to its own tone (~0.03 in the shadows .. 0.17 at the
# lights: the base pass is already full-bright, so this only lifts the face a little), the tear shines; lashes,
# brows, irises and lips do not glow so the features survive
SKIN_GLOW = {3: 0.03, 4: 0.05, 5: 0.07, 6: 0.10, 7: 0.13, 8: 0.15, 9: 0.17}
GLOWPAL = {str(i): _g(SKIN[i], k) for i, k in SKIN_GLOW.items()}
GLOWPAL.update({
    'c': _g(LINEN[7], 0.2), 'W': _g(WATER, 0.12), 'r': _g(mix(SKIN[7], BLUSH, 0.4), 0.10),
    't': (40, 50, 56), 'T': (100, 116, 126), 'Y': (160, 176, 188),
    'm': _g(SKIN[6], 0.05), 'q': (12, 10, 9),
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


def face_decals(x0, y0, w, h, glow=True):
    d = {'front': pixelart(_slice(FACE, x0, y0, w, h), FPAL, anchor='topleft')}
    if glow:
        d['eyes:front'] = cell_decal(face_glow, x0, y0, w, h)
    return d


# rosary looped from the belt on the front gore: walnut beads, a small cross above the burning hem.  It is painted
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
ROS_GLOW = gpal({'o': (40, 28, 16), '+': (90, 66, 34), 'X': (220, 184, 110)})

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
HALO_R, HALO_Y, HALO_Z = 17, -50.0, 8.5   # disc radius, centre height, plane depth (the nape ends at z 7)
EYE_Z = -7.0       # open eyes / closed lips: IN the plane of the face front (z -7), filling its windows
LID_Z = -7.05      # closed lids / speech frame when speaking: 0.05 in front of it
MOUTH_REST_DZ = 0.25   # the speech frame rests at LID_Z + 0.25 = -6.8, 0.2 behind the opaque lips


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

    # ---------------- robe: eight flared gores round an octagonal hull, each burning away into light, with light
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

    # back veil: a centre panel with a pointed hem and two side panels angled forward round the back
    bone('veil', (0, -33, 4.9), parent='chest', rot=(4, 0, 0), mat=habit_mat)
    box('veil', (-4, -33, 4.9), (8, 27, 1), name='veil_c')
    for side, sx in (('right', -1), ('left', 1)):
        vb = f'veil_back_{side}'
        bone(vb, (4 * sx, -33, 4.9), parent='veil', rot=(0, 18 * sx, 0), mat=habit_mat)
        box(vb, (4 * sx if sx > 0 else -9, -33, 4.9), (5, 21, 1), name='veil_s', side=sx)

    # ---------------- neck (inside the wimple)
    bone('neck', (0, -32, 0), parent='chest', mat=linen_mat)
    box('neck', (-4, -33, -4), (8, 2, 7), mat=linen_mat, name='neckband')

    # ---------------- head: face window x -7.5..7.5 / y -51..-34
    bone('head', (0, -33, 1.5), parent='neck', mat=skin_mat)
    fbox('head', (-7.5, -51, -7), (15, 17, 12), 'skull')
    fbox('head', (-1.5, -43, -8), (3, 3, 1), 'nose', glow=False)
    fbox('head', (-0.5, -42, -9), (1, 2, 1), 'nose', glow=False)
    box('head', (-8.5, -53, -7.5), (17, 2, 13), mat=linen_mat, name='band')
    box('head', (-8.5, -51, -7.5), (1, 17, 12), mat=linen_mat, name='coif_side', side=-1)
    box('head', (7.5, -51, -7.5), (1, 17, 12), mat=linen_mat, name='coif_side', side=1)
    box('head', (-8.5, -34, -7.5), (17, 2, 10), mat=linen_mat, name='chinwrap')
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
        plane('head', (ex[s], ey, EYE_Z), (5, 5, 0), 'eye_' + s, eyes[s], OPAQUE,
              pixelart(eyes[s], gpal(EYEGLOW), anchor='topleft'))
    mx, my = GX0 + MOUTH_COL, GY0 + MOUTH_ROW
    plane('head', (mx, my, EYE_Z), (5, 4, 0), 'lips', LIPS, OPAQUE, pixelart(LIPS, gpal(GLOWPAL), anchor='topleft'))

    # the closed lids: opaque planes just in front of the same windows (same centroids as the eye planes)
    bone('eyelids', (0, ey, LID_Z), parent='head', mat=none_mat)
    for s in ('right', 'left'):
        plane('eyelids', (ex[s], ey, LID_Z), (5, 5, 0), 'lid', lids[s], OPAQUE,
              diff_glow(lids[s], GLOWPAL, eyes[s], EYEGLOW))

    # speech frame: tucked 0.2 behind the opaque lips at rest; 'speak' brings it 0.05 in front of the face
    mz = LID_Z + MOUTH_REST_DZ
    bone('mouth', (0, my, mz), parent='head', mat=none_mat)
    plane('mouth', (mx, my, mz), (5, 4, 0), 'mouth_open', MOUTH_OPEN, OPAQUE,
          diff_glow(MOUTH_OPEN, GLOWPAL, LIPS, GLOWPAL))

    # the halo: a nimbus disc just behind the veil, centred a little above the middle of the head
    bone('halo', (0, HALO_Y, HALO_Z), parent='head', mat=halo_mat)
    box('halo', (-HALO_R, HALO_Y - HALO_R, HALO_Z), (2 * HALO_R, 2 * HALO_R, 0), name='halo')

    # veil sides: an upper plate hugging the coif (child of head) and a lower drape over the back of the shoulder
    for side, sx in (('right', -1), ('left', 1)):
        vs, dr = f'veil_{side}', f'veil_drape_{side}'
        bone(vs, (9.0 * sx, -53, 0.5), parent='head', mat=habit_mat)
        box(vs, (9.0 * sx - 0.5, -53, -5), (1, 15, 12), name='veil_side', side=sx)
        bone(dr, (9.5 * sx, -38, 6.5), parent=vs, rot=(0, 0, -12 * sx), mat=habit_mat)
        box(dr, (9.5 * sx - 0.5, -38, 3.5), (1, 15, 6), name='drape', side=sx)

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
        box(sl, (ax - 4, -12, -3.5), (8, 4, 8), name='bell', side=sx)
        box(sl, (ax - 4.5, -8, -4), (9, 5, 9), name='bell_lo', side=sx)
        box(sl, (ax - 4.5, -9, 5.3), (9, 15, 0), name='wing', side=sx)          # the long back of the sleeve
        bone(hand, (ax, -8.5, 0.5), parent=fa, rot=(0, -30 * sx, 0), mat=hand_mat)
        box(hand, (ax - 1, -8.5, -1.5), (2, 5, 4), name='palm')
        box(hand, (ax - 0.5 * sx - 0.5, -7, -2.5), (1, 4, 1), name='thumb')
        for zz, ln in ((-1.5, 4), (-0.5, 5), (0.5, 4), (1.5, 3)):
            box(hand, (ax - 0.5, -3.5, zz), (1, ln, 1), inflate=-0.1, name='finger')

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
    # light, chest arched, face lifted to the light, eyes OPEN; the bells hang from the arms like wings, the veil
    # streams back, the drapes fold at the shoulders instead of levering with the head, the hem trails below
    'rise': {
        'body': (-0.04, 0, 0, 0, -3.0, 0),
        'chest': (-0.1, 0, 0, 0, 0, 0),
        'neck': (-0.08, 0, 0, 0, 0, 0),
        'head': (-0.3, 0, 0, 0, 0, 0),
        'eyelids': EYES_OPEN,
        'halo': (0.416, 0, 0, 0, -8.94, -1.6),
        'veil': (0.14, 0, 0, 0, 1.5, 0),
        **_skirts(-0.08, -0.05, 0.12),
        **_mirror({
            'veil_*': (0, 0, 0.08),
            'veil_drape_*': (0.62, 0, -0.02),
            'veil_back_*': (0, 0.1, 0),
            '*_arm': (0.206, 0.11, 1.867),
            '*_forearm': (-0.287, 1.003, -0.063),
            '*_sleeve': (1.076, 0, -0.592, 0, -3.0, 0),
            '*_hand': (-0.194, 0.431, -0.287),
        }),
    },
    # 'Gracias por venir': eyes open, head a little lifted and tilted, the speech frame in front of the lips
    'speak': {
        'head': (-0.08, 0, 0.06, 0, 0, 0),
        'halo': (0.08, 0, -0.06, 0, -0.59, 0.36),
        'eyelids': EYES_OPEN,
        'mouth': MOUTH_SPEAK,
        **_mirror({'veil_drape_*': (0.08, 0, 0)}),
    },
    # gratitude: a gentle bow of the head, tilted with tenderness, over hands joined in prayer at the sternum (in
    # front of the guimpe and the cross), eyes closed; the bells slide back toward the elbows and hang
    'bow': {
        'chest': (0.08, 0, 0, 0, 0, 0),
        'neck': (0.07, 0, 0, 0, 0, 0),
        'head': (0.24, 0, 0.1, 0, -1.0, -0.5),
        'halo': (-0.39, 0, -0.1, 0, 4.96, 5.07),
        **_skirts(0.03, 0.03, 0.03),
        **_mirror({
            'veil_drape_*': (-0.05, 0, 0.06),
            '*_arm': (-0.938, -0.135, -0.051),
            '*_forearm': (0.197, -1.123, -1.211),
            '*_sleeve': (1.255, 0, -1.002, 0, -0.06, 0),
            '*_hand': (-0.837, -0.145, 1.522),
        }),
    },
}


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

RENDERING.  Base: RenderType.entityTranslucentEmissive(texture) -- full-bright, alpha baked per material (skin 235,
linen 226, head veil 228, back veil and drapes 200, habit 196 at the chest -> ~150 toward the light, sleeves 192,
halo / light / flakes / streamers fading to 0; nothing below alpha 28 is painted, MC discards < 0.1).  Glow: the
'eyes' layer (clara_eyes.png) through GlowLayer / RenderType.eyes (additive): face and lids (a gentle lift, ~0.15 of
the skin), linen, hands (fingertips brightest), a 1-texel gold rim on the true silhouette edges, the soft inner light
of the habit rising toward the hem, the burning hem, flakes, streamers and the parts of the halo that are never
behind her.  Near-black glow texels are alpha 0 and dim ones partly transparent (additive blending ignores alpha;
the portrait / gallery compositing does not).
IMPORTANT: neither pass writes depth.  The translucent base pass is sorted PER QUAD by centroid, and the glow pass
adds every texel of every VISIBLE part, even one hidden behind another.  Hence the rules (keep them when editing):
  * Features that change sit on planes over WINDOWS cut out of the skull front, centred exactly on them: open eyes
    and closed lips in the plane of the face (z {EYE_Z}), closed lids (and the speech frame while speaking) just in
    front of it (z {LID_Z}); hidden states sit 0.2 behind (z {LID_Z + MOUTH_REST_DZ:.2f}).
  * Never hide a part by folding it into the body (a folded plane shows through the translucent face).  Hide it
    with ModelPart.visible = false -- that also removes its glow, which a pose offset alone does not.
  * Glowing faces never point backward in any pose (hands), and the halo glows only where it is never behind her.
Fade her in / out with the vertex alpha (0 -> 1 over 40 ticks) and scale the glow layer's colour with the same
factor.  She is NOT scary: every motion is slow, soft and continuous (sine eases, no snaps, no twitches).  She never
walks: the robe ends in light.  Poses: rise, speak, bow.

ENDING BEAT (suggested): appear in 'bow' with alpha 0 -> 1 and body dy +6 -> 0 (40 ticks)  ->  lift the head out of
the bow (30 ticks)  ->  OPEN THE EYES (eyelids, ~10 ticks, see below)  ->  'speak' while clara.voz plays ("Gracias
por venir.  Digale a Teresita que no fue su culpa.")  ->  blend to 'rise' over 60 ticks while she floats up 2-3
blocks  ->  white flash, alpha -> 0.

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
* chest -- slim bodice (black wool) under the rounded white guimpe, the small wooden cross on its cord.  Breathing
  (she breathes even as a soul; it reads as alive): xRot sin(t*0.05)*0.015.  Rise {_pv('rise', 'chest')}, bow
  {_pv('bow', 'chest')}.
* veil -- the back veil's centre panel (nape to hips, pointed hem), child of chest, rest +4 deg so it clears the
  gores.  Hangs with gravity: xRot = -chestXRot*0.6 + sin(t*0.05 - 1.2)*0.03.  Rise {_pv('rise', 'veil')} (streams
  back), bow 0.
* veil_back_right / veil_back_left -- the two side panels of the back veil, children of veil, hinged on the centre
  panel's edges and yawed 18 deg forward round the back.  Sway yRot += sin(t*0.05 + side)*0.03.  Rise
  {_pv('rise', 'veil_back_right')} (right; left mirrored) as the veil streams back.
* neck -- inside the wimple (a linen band fills the gap when the head lifts).  Follows the head softly: 30 % of the
  look pitch.  Rise {_pv('rise', 'neck')}, bow {_pv('bow', 'neck')}.
* head -- face cube with the 15 x 17 face (made oval by the coif linen; windows for the eyes and the mouth), the
  nose, the white coif band / sides / chin wrap, the veil dome (three chamfered steps), the nape, and the static
  planes eye_right / eye_left (open eyes) and lips (closed mouth) behind the windows.  FOCUS bone.  Looks at the
  player with gentle easing (yaw clamp +-0.6, pitch +-0.3, lerp 0.08 per tick).  Idle: a slow tilt
  zRot sin(t*0.03)*0.05.  Rise {_pv('rise', 'head')} (her face lifts to the light).  Speak {_pv('speak', 'head')}.
  Bow {_pv('bow', 'head')}: a gentle bow tilted with tenderness.
* eyelids -- the two CLOSED-lid planes (peaceful U-shaped lash curves), opaque, 0.05 in front of the face, centred
  on the eye windows; pivot on the top edge of the lids (y {GY0 + EYE_ROWS[0]}).  REST = EYES CLOSED.  To OPEN: a
  real lid lift -- yScale 1 -> 0 over ~10 ticks (ease-out), then visible = false.  To close / blink: visible = true
  and yScale 0 -> 1 (a blink = 2-3 ticks closed every 80-140 ticks while open).  Never fold them into the head.
  The pose tables encode 'open' as {_pv('rise', 'eyelids')} (the lids slide behind the opaque eye planes) for tools
  that cannot hide parts; in game ALSO set visible = false whenever that weight is > 0.5, or the hidden lids still
  add their glow over the open eyes.  Closed in 'bow'; open in 'speak' and 'rise'.
* mouth -- the speech frame (the same lips, the lower lip dropped one row over a one-row opening, corners lifted: a
  soft smile while she speaks), opaque, tucked 0.2 behind the opaque lips plane at rest.  REST: visible = false
  (it is also hidden behind the lips, and its own glow is zero, so nothing leaks either way).  Talking: visible =
  true and dz {_n(MOUTH_SPEAK[5])} (the 'speak' table: {_pv('speak', 'mouth')}) brings it 0.05 in front of the face; flap
  it with the voice (dz {_n(MOUTH_SPEAK[5])} for 2-3 ticks per syllable, or while the clara.voz amplitude is above a threshold) and
  set it back (dz 0, visible = false) when silent.
* halo -- the nimbus disc behind the head (thin gold ring + soft warm glow), child of head.  Breathe it: scale
  1 + sin(t*0.08)*0.03 if the renderer allows (else leave static); fade its glow with the ending.  RULE for every
  head pitch: counter-rotate the halo by about the summed pitch of chest + neck + head so it stays upright behind
  her (rise {_pv('rise', 'halo')}: tipped back with her face but lifted clear of the dome; bow {_pv('bow', 'halo')}:
  fully upright).  Its glow is masked wherever any part of her can stand in front of it.
* veil_right / veil_left -- the upper veil sides hugging the coif from the crown to the jaw (child of head; front
  edge set back so the white coif, nose and chin read in profile; rounded front-bottom corner).  Sway
  zRot += sin(t*0.05 + side)*0.02; rise {_pv('rise', 'veil_right')} (right; left mirrored): open outward.
* veil_drape_right / veil_drape_left -- the lower veil drapes, child of the upper sides, hanging behind the
  shoulders (outside the guimpe and the sleeves) with a 12 deg outward flare and a sloped hem.  They FOLD at the
  shoulder instead of levering with the head: counter-rotate part of the head pitch -- rise
  {_pv('rise', 'veil_drape_right')}, bow {_pv('bow', 'veil_drape_right')} (small: they stay tucked behind the
  shoulders), speak {_pv('speak', 'veil_drape_right')}; add sin(t*0.05 + 0.6)*0.03 sway.

ARMS (right_* on -X; left mirrors yRot / zRot / dx)
* right_arm / left_arm -- upper sleeve (black wool), shoulder pivot beside the guimpe (rest 7 deg out, 3 deg
  forward).  Idle: xRot sin(t*0.05)*0.03.  Rise {_pv('rise', 'right_arm')}: arms open and lifted above the
  horizontal, swept a little back (orans / ascension).  Bow {_pv('bow', 'right_arm')}.
* right_forearm / left_forearm -- inner sleeve ending in the white undercuff at the wrist; elbow pivot (rest bent
  8 deg).  Rise {_pv('rise', 'right_forearm')}: soft elbows.  Bow {_pv('bow', 'right_forearm')}: forearms up to the
  sternum.
* right_sleeve / left_sleeve -- the open bell of the sleeve, three flared tiers (6 -> 8 -> 9 wide, open below,
  dark lining at the top, curved rolled hem, a long hanging back 'wing'), child of the forearm, pivot at the top of
  the bell.  It should HANG: whenever the forearm lifts, rotate it back toward gravity, lagging 6-10 ticks behind
  the arm, plus sin(t*0.06)*0.04 sway.  Rise {_pv('rise', 'right_sleeve')}: the top tier stays on the forearm, the
  wing hangs.  Bow {_pv('bow', 'right_sleeve')}: with the forearms raised the bell hangs from the elbow.
* right_hand / left_hand -- palm, thumb and four slender fingers with rose nails and glowing tips; wrist pivot,
  rest yaw 30 deg (palms turned a little forward).  Rise {_pv('rise', 'right_hand')}: palms up and out, receiving
  the light; fingers breathe xRot sin(t*0.07)*0.04.  Bow {_pv('bow', 'right_hand')}: palms pressed together at the
  sternum, fingers up, in front of the guimpe and the cross.
"""
