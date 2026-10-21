"""Clara -- the freed soul of Sor Maria de la Agonia (DEAD LINE, case 'convento', ending).

Authored at 2x texel density (model.scale = 0.5).  +Y down, ground y = 24, faces -Z, right_* on -X.  Centred on
x = 0, z = 0.  Veil top y = -55, lowest light streamer y ~ 23 (she floats: no feet, the robe ends in light).
Everything above the waist is authored at its original heights and lifted by TY = -3 (a slimmer, taller figure).

Design
------
Clara Ines Bustos, 33, the nun the demon wore.  The same habit as Sor Agonia but CLEAN and whole: starched white
coif and rounded guimpe, black veil, black wool habit with wide bell sleeves, a leather cincture and a plain walnut
rosary -- and the pectoral cross is upright again.  She is not scary: beautiful and sad, rising in the chapel at
dawn with her arms open.

Silhouette: a calm, slender A-shape.  A soft rounded veil crown, the veil falling away from the white oval of the
coif onto the shoulders, the white guimpe, a slim black bodice, long arms in bell sleeves and an eight-panel robe
that flares a little and, from the thigh down, DISSOLVES INTO LIGHT: the wool burns away in pointed tatters with a
gold-white rim, embers lift off the cloth, warm mist hangs below and twelve light streamers trail off without ever
touching the floor.

Face (15 x 17, hand-placed pixel art over layered face cubes: skull, two brow pads, nose): luminous peach skin in
broad soft planes, thin brows lifted at the inner ends (sad), big warm-brown eyes (3-wide iris, amber lower half,
one catchlight), a small nose, small rose lips with corners turned up (a faint, tired smile), blush and ONE tear on
her left cheek.  The closed state is the `eyelids` bone: two zero-thickness lid planes with peaceful U-shaped lash
curves just in front of the open eyes.  She starts with them visible (eyes closed); Java opens her eyes by
folding / scaling / hiding that bone.  A `mouth` bone holds an open-mouth plane tucked behind the face for
speech (she says goodbye).

Colour: violet-black wool with a warm gold rim light and sheen; cream linen with lavender shadows; peach skin
pushed toward light; gold-white light for everything that dissolves.  Translucent (entityTranslucentEmissive), with
alpha baked per material (skin 244, linen 240, veil 244, habit 226, fading to 0 in the light); faces that are never
seen are cut out so nothing ghosts through.  The emissive 'eyes' layer carries the soft glow: the tear, the lit
planes of the face and linen, the hands, the warm rim on the silhouette edges, the burning rim of the robe, the
embers and the streamers -- never the eyes, so nothing glows through the closed lids.
"""
import math

from mcmodel import Model, vnoise, hash3, face_light, pick
from rig import Rig
from paint import hx, mix, pixelart, chain

RIG = None

# ------------------------------------------------------------------ translucency (alpha baked per material)
A_SKIN = 244
A_LINEN = 240
A_VEIL = 244
A_HABIT = 226
A_WOOD = 238


def A(c, a):
    return (c[0], c[1], c[2], int(max(0, min(255, a))))


def pal(*h):
    return [hx(c) for c in h]


# ------------------------------------------------------------------ palettes (dark -> light, hue shifted)
# luminous warm skin: rose-violet shadows (light under the skin), peach mids, cream lights
SKIN = pal('#3d2230', '#5e3340', '#82494f', '#a6635d', '#c4826f', '#dca58b', '#ecc0a5', '#f6d8c2', '#fde9db',
           '#fff6ee')
# starched linen: lavender shadows -> warm cream lights
LINEN = pal('#3a3150', '#574d6c', '#776d8a', '#978ea6', '#b6adbf', '#cfc6d3', '#e3dbe0', '#f1ebea', '#faf6f1',
            '#ffffff')
# habit wool: violet blacks (a touch lifted: she is light now, not shadow)
HABIT = pal('#0a0710', '#120d19', '#1b1424', '#251c30', '#30253d', '#3c2f4b', '#4a3b5a', '#5b4a6a', '#715d7e')
VEILC = pal('#05040a', '#0b0810', '#120c19', '#1a1222', '#23192d', '#2e2239', '#3c2d49', '#4f3d5d')
# the light she dissolves into: gold -> cream -> white
LIGHT = pal('#5a3820', '#8a5a2e', '#b7843f', '#d9aa58', '#efc979', '#f9e0a2', '#fdefca', '#fff8e8', '#ffffff')
RIM = hx('#f3cf86')
SHEEN = hx('#a8848c')
WOOD = pal('#1e110a', '#341f12', '#4f311c', '#6c4528', '#8a5c35', '#a97746', '#c79a62')
LEATHER = pal('#060406', '#0e090c', '#181014', '#22181c', '#2f2226', '#3e2e31')
NAIL = hx('#f7cfc5')

# face details
LASH = hx('#2a1712')
LASH2 = hx('#6a4436')
BROW = pal('#5a3829', '#7a5038', '#a07558')
SCLERA = hx('#f7ece4')
SCLERA_D = hx('#d6c0bb')
IRIS = pal('#2a140b', '#5a3118', '#8a5226', '#b97a3a')
CATCH = hx('#fffcf4')
LIPC = pal('#9a4d57', '#bf6668', '#d6857d', '#eaa898')
BLUSH = hx('#f0a596')
TEAR = hx('#ffffff')
TEAR2 = hx('#dcefF6')

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


def is_plane(ctx):
    return 0 in ctx.cube.size


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


def emit(ctx, col, k=1.0):
    """Record an emissive texel for the 'eyes' layer (painted by glow_decal)."""
    if k <= 0:
        return
    u0, v0, _, _ = frect(ctx.cube, ctx.face)
    GLOW[(u0 + ctx.i, v0 + ctx.j)] = (int(col[0] * k), int(col[1] * k), int(col[2] * k), 255)


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


# ------------------------------------------------------------------ cloth
def soft_fold(u, y, seed, period=7.0):
    """Long soft folds of clean wool: lit ridge, body, a gentle crease (no torn, dirty breaks)."""
    ph = (u + (vnoise(u * 0.1, y * 0.06, seed, 3) - 0.5) * 2.4 + seed * 0.37) % period / period
    if ph < 0.14:
        return 0.12
    if ph < 0.5:
        return 0.04
    if ph < 0.8:
        return -0.03
    return -0.11


def hem_at(u):
    """Height (texels, +Y down) where the wool ends at arc position u: a slow wave plus pointed tatters."""
    w = 3.4
    i = math.floor(u / w)
    f = u / w - i
    L = 1.5 + hash3(i, 7, 0, 41) * 7.5
    tri = 1.0 - abs(2.0 * f - 1.0)
    return 2.5 + vnoise(u * 0.16, 0.5, 0.5, 43) * 5.5 + L * tri ** 1.4


HIDDEN = {
    # tag -> faces never seen (cut out so nothing ghosts through the translucency)
    'bodice': ('top', 'bottom'), 'core': ('bottom',),
    'sleeve_up': ('top',), 'forearm': ('top', 'bottom'),
    'crown': (), 'cap': ('bottom',), 'veil_side': ('top',), 'nape': ('front', 'top'), 'veil_back': ('top',),
}
VEIL_TAGS = ('crown', 'cap', 'veil_side', 'nape', 'veil_back')


def robe_light(ctx, c, a):
    """The robe panels: wool -> warming wool -> embers -> gold-white burning rim -> warm light fading out."""
    x, y, z = ctx.pos
    u = math.atan2(x, -z) * 9.0                              # arc length around the robe (continuous)
    hem = hem_at(u + 40.0)
    dist = hem - y                                           # > 0: still cloth
    if dist > 0:
        warm = clamp((y + 6.0) / (hem + 6.0))                # the wool warms toward the hem
        c = mix(c, LIGHT[1], warm * warm * 0.35)
        if dist < 1.0:
            emit(ctx, (230, 196, 128))
            return A(LIGHT[8] if hash3(int(u * 3), int(y), 1, 5) > 0.5 else LIGHT[7], 252)
        if dist < 2.0:
            emit(ctx, (170, 120, 60))
            return A(LIGHT[5], 246)
        if dist < 4.5:
            c = mix(c, LIGHT[2], (4.5 - dist) / 2.5 * 0.55)
            a = a - (4.5 - dist) * 6
        if dist < 9.0 and hash3(int(u * 2.0), int(y * 2.0), 3, 71) > 0.975 - (9.0 - dist) * 0.002:
            emit(ctx, (220, 180, 110))
            return A(LIGHT[6], 250)                          # embers lifting off the cloth
        return A(c, a)
    depth = -dist
    s = vnoise(u * 0.55, y * 0.05, 2.0, 9)                   # vertical shafts in the mist
    lum = clamp(0.86 - depth * 0.05 + (s - 0.5) * 0.3)
    al = 215 * (1 - depth / 8.5) * (0.45 + s * 0.7)
    if al < 26:                                             # MC's translucent pipeline cuts alpha < 0.1
        return None
    emit(ctx, (150, 116, 66), clamp(al / 215))
    return A(pick(LIGHT, lum), al)


def habit_mat(ctx):
    """Clean black wool: long soft folds, warm sheen on the ridges, warm rim light on the silhouette edges, and on
    the robe panels the dissolve into light."""
    t = tag(ctx)
    f = ctx.face
    if f in HIDDEN.get(t, ()):
        return None
    if is_plane(ctx) and f == 'back':
        return None
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    k = cseed(ctx)
    side = f in ('front', 'back', 'west', 'east')
    veil = t in VEIL_TAGS
    ramp = VEILC if veil else HABIT
    a = A_VEIL if veil else A_HABIT
    if t == 'veil_back':
        a = A_VEIL - 6
    v = 0.45 + face_light(ctx) * 1.05
    if side:
        big = max(ctx.w, ctx.h) > 3 and min(ctx.w, ctx.h) > 2
        if big:
            if t in ('panel', 'veil_back', 'veil_side'):
                v += soft_fold(around(ctx), ctx.y, k % 13, 6.0)
            else:                                           # fitted parts: broad, quiet folds (no pinstripes)
                v += soft_fold(around(ctx), ctx.y, k % 13, 8.5) * 0.55
        if edge(ctx) == 0 and min(ctx.w, ctx.h) > 2:
            v -= 0.06
    if t == 'cuff':
        if f == 'bottom':
            cx = abs(lx - w / 2) / (w / 2)
            cz = abs(lz - d / 2) / (d / 2)
            if max(cx, cz) > 0.74:
                return A(pick(ramp, 0.55), a)                # rolled rim of the bell
            return A(pick(LINEN, 0.2 + (1 - max(cx, cz)) * 0.25), 250)   # white undercuff deep inside
        if side and h - ly < 1.0:
            v += 0.16                                       # rolled edge of the bell catches the light
    if t in ('crown', 'cap'):
        if f == 'top':
            # cloth over a round skull: lit in the middle, rolling off toward the edges, folds running back
            rx = abs(lx - w / 2) / (w / 2)
            rz = abs(lz - d / 2) / (d / 2)
            v += 0.08 - (rx * rx + rz * rz) * 0.16
            v += soft_fold(lx * 1.3, lz, 5, 6.0) * 0.5
            if ctx.j == ctx.h - 1:
                v += 0.1                                    # front edge catches the light
        elif t == 'crown' and f == 'front' and ctx.j == ctx.h - 1:
            v += 0.18                                       # brim edge over the white band
        elif f == 'bottom':
            v -= 0.15
    if t == 'veil_back' and side:
        cx = abs(lx - w / 2) / (w / 2) if f in ('front', 'back') else 1.0
        cut = h - 3.0 * cx ** 2
        if ly > cut:
            return None                                     # the veil hangs lower in the middle: rounded hem
        if cut - ly < 1.0:
            v += 0.12
    if t == 'veil_side' and side and h - ly < 1.0:
        v += 0.12
    c = pick(ramp, v)
    if side and v > 0.58:
        c = mix(c, SHEEN, 0.22)                             # warm sheen on the lit ridges
    # warm rim light along the silhouette edges (backlit by her own glow)
    if side:
        rim = 0.0
        if f in ('west', 'east'):
            rim = 0.16
        if ctx.i == 0 or ctx.i == ctx.w - 1:
            rim += 0.42 if f in ('front', 'back') else 0.14
        elif ctx.w > 4 and (ctx.i == 1 or ctx.i == ctx.w - 2) and f in ('front', 'back'):
            rim += 0.14
        if rim:
            c = mix(c, RIM, rim * (0.5 if veil else 0.48))
            emit(ctx, (64, 48, 26), rim)                    # the backlit edge glows a little in game
    if t == 'panel' and f != 'top':
        return robe_light(ctx, c, a)
    return A(c, a)


def belt_mat(ctx):
    f = ctx.face
    if f in ('top', 'bottom'):
        return None
    v = 0.5 + face_light(ctx) * 1.1
    if ctx.j in (0, ctx.h - 1):
        v -= 0.18
    if ctx.j == ctx.h // 2 and ctx.i % 3 == 1:
        v += 0.16                                           # stitch line
    return A(pick(LEATHER, v), A_HABIT + 14)


def bib_half(ly, w, h):
    """Half width of the guimpe at depth ly: straight sides, generously rounded bottom."""
    return w / 2 - max(0.0, ly - (h - 4.5)) ** 1.6 * 1.05


def linen_mat(ctx):
    """Starched clean linen: lavender shadows, cream lights, ironed tucks, gathers at the neck, a crisp shadow line
    where it meets the face."""
    t = tag(ctx)
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    side = f in ('front', 'back', 'west', 'east')
    if t == 'band' and f in ('top', 'back', 'west', 'east'):
        return None
    if t == 'coif_side' and f in ('top', 'back'):
        return None
    if t == 'coif_side' and ((f == 'west' and ctx.x < 0) or (f == 'east' and ctx.x > 0)):
        return None                                         # outer side: under the veil
    if t == 'chinwrap' and f in ('back',):
        return None
    if t == 'guimpe' and f in ('back', 'bottom'):
        return None
    v = 0.78 + face_light(ctx) * 0.8
    if f in ('west', 'east'):
        v -= 0.12
    elif f == 'back':
        v -= 0.25
    if t == 'band':
        if f == 'front':
            v += (0.07, -0.01, -0.06)[ctx.j % 3] if ctx.j < ctx.h - 1 else -0.2
            v -= (abs(lx - w / 2) / (w / 2)) ** 2 * 0.14
        elif f == 'bottom':
            v -= 0.25
    elif t == 'coif_side':
        if f == 'front':
            inner = (ctx.i == ctx.w - 1) if ctx.x < 0 else (ctx.i == 0)
            v += -0.3 if inner else 0.05
            v -= ly / h * 0.1
        elif side:
            v -= 0.3                                        # inner wall toward the face: in shadow
        elif f == 'bottom':
            v -= 0.2
    elif t == 'chinwrap':
        if f == 'front':
            v += (0.03, -0.05)[ctx.i % 2] * (1 - ly / h)    # gathered under the chin
            if ctx.j == 0:
                v -= 0.24                                   # shadow under the chin
            v -= (abs(lx - w / 2) / (w / 2)) ** 2 * 0.16
        elif f == 'top':
            v -= 0.3
    elif t == 'guimpe':
        cx = abs(lx - w / 2)
        if f == 'front':
            hw = bib_half(ly, w, h)
            if cx > hw:
                return None
            if ly < 3.0:
                g = 1 - ly / 3.0
                v += (0.05 if int(lx) % 2 == 0 else -0.06) * g  # gathers falling from the neck
            fold = h * 0.55
            if fold - 1.0 < ly < fold:
                v += 0.06
            elif fold <= ly < fold + 1.0:
                v -= 0.06
            v -= (cx / (w / 2)) ** 2 * 0.16
            if cx > hw - 1.0:
                v -= 0.1
        elif f in ('west', 'east'):
            zc = lz if f == 'west' else (d - lz)
            hw = bib_half(ly, d * 2, h)
            if (d - zc) > hw + 0.0 and ly > h - 4.5:
                return None
            v -= 0.02
        elif f == 'top':
            v -= 0.04 + (0.04 if int(lx) % 2 else 0)
    elif t == 'undercuff':
        if f == 'bottom':
            return A(pick(LINEN, 0.35), A_LINEN)
    c = pick(LINEN, v)
    if t == 'guimpe' and f == 'front':
        cx = abs(lx - w / 2)
        hw = bib_half(ly, w, h)
        if hw - 2.0 < cx < hw - 1.0 and ly > 1.0:
            c = mix(c, LINEN[4], 0.5)                       # stitched hem a texel inside the edge
        # the cross hangs on a thin dark cord from the neck: two converging lines
        cord = 4.0 - ly * 0.55
        if 0.5 < ly < 4.5 and abs(cx - max(0.0, cord)) < 0.5 and cx > 0.6:
            c = mix(c, LEATHER[3], 0.75)
    if side and v > 0.78:
        emit(ctx, (46, 38, 28) if f == 'front' else (26, 21, 15))
    return A(c, A_LINEN)


# ------------------------------------------------------------------ flesh
SKIN_HIDDEN = {'skull': ('top', 'west', 'east', 'back', 'bottom'), 'nose': ('back',), 'brow': ('back',)}


def skin_mat(ctx):
    """Luminous warm skin for the sides/undersides of the face cubes (the fronts are the FACE pixel art)."""
    t = tag(ctx)
    f = ctx.face
    if f in SKIN_HIDDEN.get(t, ()):
        return None
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    v = 0.72 + face_light(ctx) * 0.7
    if f in ('west', 'east'):
        v -= 0.12
    if t == 'nose' and f == 'bottom':
        cx = lx - w / 2
        if abs(cx) > 0.5 and lz < d - 0.4:
            return A(SKIN[4], A_SKIN)                       # nostrils
        return A(SKIN[6], A_SKIN)
    if t == 'brow' and f == 'bottom':
        return A(SKIN[5], A_SKIN)                           # soft shadow over the lids
    if t == 'brow' and f == 'top':
        return A(SKIN[7], A_SKIN)
    return A(pick(SKIN, v), A_SKIN)


def hand_mat(ctx):
    """Slender luminous hands: soft knuckle creases, rose-pink nails, glowing fingertips."""
    t = tag(ctx)
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    v = 0.74 + face_light(ctx) * 0.8
    if f in ('west', 'east', 'front', 'back') and edge(ctx) == 0 and min(ctx.w, ctx.h) > 2:
        v -= 0.05
    if t == 'palm':
        if ly < 1.0 and f != 'bottom':
            v -= 0.12                                       # shadow under the cuff
        if ly > h - 1.0 and f in ('west', 'east'):
            v -= 0.06                                       # knuckle line
    if t in ('finger', 'thumb'):
        if f == 'top':
            v -= 0.1
        if ly > h - 1.0 and f != 'top':
            c = NAIL if f != 'bottom' else SKIN[8]
            emit(ctx, (120, 92, 66))
            return A(c, A_SKIN)
        if abs(ly - h * 0.45) < 0.5:
            v -= 0.07                                       # joint crease
    c = pick(SKIN, v)
    if v > 0.66:
        emit(ctx, (66, 50, 34))
    return A(c, A_SKIN)


def wood_mat(ctx):
    """Walnut rosary beads on a cord + plain wooden cross: grain, worn pale corners, a gold glint."""
    t = tag(ctx)
    lx, ly, lz = local(ctx)
    f = ctx.face
    if t == 'beads':
        if f in ('top', 'bottom'):
            return A(WOOD[2], A_WOOD)
        ph = int(ly) % 3
        if ph == 2:
            return A(LEATHER[4], A_WOOD) if ctx.i == ctx.w // 2 else None
        v = 0.5 + face_light(ctx) * 1.2 + (0.25 if ph == 0 and ctx.i == 0 else 0) - (0.12 if ph == 1 else 0)
        return A(pick(WOOD, v), A_WOOD)
    v = 0.5 + face_light(ctx) * 1.2
    if f in ('front', 'west') and (ctx.i == 0 or ctx.j == 0):
        v += 0.25
    elif edge(ctx) == 0:
        v -= 0.12
    c = pick(WOOD, v)
    if f == 'front' and ctx.i == 0 and ctx.j == 0:
        c = LIGHT[5]
        emit(ctx, (150, 120, 60))
    return A(c, A_WOOD)


def lid_mat(ctx):
    """Eyelid planes: only the LID pixel art is painted."""
    return None


def light_mat(ctx):
    """Light streamers below the dissolving robe: a bright core, gold edges, slow vertical shimmer, fading out."""
    if ctx.face != 'front':
        return None
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    k = cseed(ctx)
    cx = abs(lx - w / 2) / max(1.0, w / 2)
    tip = h - 0.5 - hash3(int(lx), k, 0, 31) * 3.0 - cx * 3.0
    if ly > tip:
        return None
    tfade = ly / max(1.0, tip)
    s = vnoise(lx * 0.8, ly * 0.12, k, 33)
    lum = clamp(0.95 - cx * 0.4 - tfade * 0.3 + (s - 0.5) * 0.25)
    c = pick(LIGHT, lum)
    top_in = clamp((ly + 1.0) / 4.0)
    a = 190 * top_in * (1 - tfade) ** 1.2 * (0.7 + s * 0.4) * (1 - cx * 0.35)
    if a < 26:
        return None
    emit(ctx, (150, 116, 66), clamp(a / 190))
    return A(c, a)


# ------------------------------------------------------------------ the face mask
# 15 columns (x -7.5..7.5, col c <-> x = c - 7), 17 rows (row r <-> y = -48 + r, y -48..-31: the face
# window lifted by TY = -3).
GX0, GY0 = -7.5, -48
FACE = [
    # 012345678901234
    "c4556666666554c",   # r0  y-48 soft shadow under the coif band
    "c5667777777665c",   # r1  y-47 forehead
    "5677hb777bh7765",   # r2  y-46 brows: inner ends lifted (sad)        [brow cube rows 2-3]
    "5Bhh7777777hhB5",   # r3  y-45 brow tails falling outward
    "56qq6677766qq65",   # r4  y-44 upper lids, mauve crease              [eyelids cover rows 4-7]
    "5kKKKk777kKKKk5",   # r5  y-43 upper lash line
    "5KGIiv676vGIiK5",   # r6  y-42 shaded upper sclera, catchlight, pupil, iris
    "5vjijw676wjijv5",   # r7  y-41 warm amber lower iris, bright sclera
    "565556786655565",   # r8  y-40 soft lower lids                         [nose cube rows 8-10]
    "56rr7768577rr65",   # r9  y-39 blush, nose bridge lit on her right
    "566777685777t65",   # r10 y-38 nose tip; the tear runs down her left cheek
    "566676545676T65",   # r11 y-37 shadow under the nose, the tear drop
    "56666l6q6l66665",   # r12 y-36 upper lip, corners turned up (a faint smile)
    "456666LLL666654",   # r13 y-35 mouth line
    "456666pPp666654",   # r14 y-34 lower lip with a highlight
    "c4566657566654c",   # r15 y-33 shadow under the lip, chin
    "cc45567776554cc",   # r16 y-32 chin, the coif wraps round the jaw
]
assert all(len(r) == 15 for r in FACE), [len(r) for r in FACE]
EYE_CELLS = {(r, c) for r in range(4, 8) for c in list(range(1, 6)) + list(range(9, 14))}

# closed lids (eyelids bone): one 5 x 4 plane per eye over face rows 4-7 (y -44..-40), cols 1..5 and 9..13.
LID_R = [            # her right eye (viewer's left): outer corner at the left
    "6qq66",
    "67776",
    "k677k",
    "kKKK6",
]
LID_L = [            # her left eye: outer corner at the right
    "66qq6",
    "67776",
    "k776k",
    "6KKKk",
]

# open mouth for speech (mouth bone): one 5 x 3 plane over face rows 12-14, cols 5..9
MOUTH_OPEN = [
    "luUul",
    "LDdDL",
    "6pPp6",
]

FPAL = {str(i): A(SKIN[i], A_SKIN) for i in range(10)}
FPAL.update({
    'D': A(hx('#4a1f2a'), 252), 'd': A(hx('#7a3a42'), 250),
    'c': A(LINEN[4], A_LINEN), 'C': A(LINEN[6], A_LINEN),
    'b': A(BROW[0], A_SKIN), 'B': A(BROW[2], A_SKIN), 'h': A(BROW[1], A_SKIN),
    'K': A(LASH, 252), 'k': A(LASH2, A_SKIN),
    'w': A(SCLERA, A_SKIN), 'v': A(SCLERA_D, A_SKIN),
    'I': A(IRIS[0], 252), 'i': A(IRIS[2], 252), 'j': A(IRIS[3], 252), 'G': A(CATCH, 255),
    'q': A(mix(SKIN[5], LIPC[0], 0.22), A_SKIN), 'r': A(mix(SKIN[6], BLUSH, 0.5), A_SKIN),
    'n': A(SKIN[4], A_SKIN),
    'u': A(LIPC[1], A_SKIN), 'U': A(LIPC[2], A_SKIN), 'L': A(LIPC[0], A_SKIN),
    'l': A(mix(SKIN[5], LIPC[0], 0.55), A_SKIN),
    'p': A(LIPC[2], A_SKIN), 'P': A(LIPC[3], A_SKIN),
    'T': A(TEAR, 252), 't': A(TEAR2, 248),
})
# lids use the face palette (same alpha, so the lid planes do not read as lighter patches)
LIDPAL = dict(FPAL)
# emissive layer of the face: a soft glow on the lit planes and the tear -- never on the eyes, so nothing glows
# through the closed lids
GLOWPAL = {
    'T': (170, 182, 190, 255), 't': (90, 104, 112, 255),
    '9': (46, 36, 26, 255), '8': (38, 29, 20, 255), '7': (26, 19, 13, 255), '6': (14, 10, 7, 255),
    'c': (20, 17, 14, 255),
}
FACE_GLOW = [''.join(ch if (r, c) not in EYE_CELLS else '.' for c, ch in enumerate(row)) for r, row in enumerate(FACE)]


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
    return {'front': pixelart(_slice(FACE, x0, y0, w, h), FPAL, anchor='topleft'),
            'eyes:front': pixelart(_slice(FACE_GLOW, x0, y0, w, h), GLOWPAL, anchor='topleft')}


DEFAULT_MAT = habit_mat
FOCUS = 'head'

# robe hull at the hips (y -9): octagon vertices (x, z), front edge first, going round toward her left (+X)
HULL = [(-4.5, -4.5), (4.5, -4.5), (7.0, -2.0), (7.0, 2.0), (4.5, 4.5), (-4.5, 4.5), (-7.0, 2.0), (-7.0, -2.0)]
PANEL_NAMES = ['skirt_front', 'skirt_front_left', 'skirt_left', 'skirt_back_left', 'skirt_back', 'skirt_back_right',
               'skirt_right', 'skirt_front_right']
# streamers per panel: (offset along the panel from its centre, width, top y, height)
STREAMERS = {
    'skirt_front': ((-3.5, 3, 10, 13), (1.0, 4, 12, 12)),
    'skirt_front_left': ((0.0, 3, 11, 11),),
    'skirt_left': ((-1.0, 3, 9, 13),),
    'skirt_back_left': ((0.5, 3, 11, 11),),
    'skirt_back': ((-3.0, 4, 11, 12), (2.5, 3, 10, 12)),
    'skirt_back_right': ((-0.5, 3, 10, 12),),
    'skirt_right': ((1.0, 3, 11, 12),),
    'skirt_front_right': ((0.0, 3, 9, 14),),
}
TY = -3.0          # torso extension: everything above the waist is lifted by 3 texels (slimmer, taller figure)
ROBE_H = 26        # robe panels hang from y -9 to y 17


def build():
    global RIG, MODEL
    GLOW.clear()
    r = Rig()
    RIG = r

    def bone(name, pivot, parent=None, rot=(0, 0, 0), mat=None):
        return r.bone(name, pivot, parent=parent, rot=rot, mat=mat)

    def box(bone_, frm, size, mat=None, name=None, inflate=0.0, decals=None, glow=True):
        dec = dict(decals or {})
        if glow:
            for kk, fn in GLOW_ALL.items():
                dec[kk] = chain(dec[kk], fn) if kk in dec else fn
        c = r.box(bone_, frm, size, mat=mat, inflate=inflate, decals=dec)
        c.name = name
        return c

    # upper body (everything above the waist) is authored at the original heights and lifted by TY
    def ubone(name, pivot, parent=None, rot=(0, 0, 0), mat=None):
        return bone(name, (pivot[0], pivot[1] + TY, pivot[2]), parent, rot, mat)

    def ubox(bone_, frm, size, **kw):
        return box(bone_, (frm[0], frm[1] + TY, frm[2]), size, **kw)

    def fbox(bone_, frm, size, name, mat=skin_mat):
        f = (frm[0], frm[1] + TY, frm[2])
        return box(bone_, f, size, mat=mat, name=name, decals=face_decals(f[0], f[1], size[0], size[1]))

    # ---------------- body: root at the waist; cincture + a hidden core inside the robe
    bone('body', (0, -10, 0), mat=habit_mat)
    box('body', (-7.5, -11, -4.75), (15, 2, 9), mat=belt_mat, inflate=0.25, name='belt')
    box('body', (-5, -9, -3.5), (10, 5, 7), name='core')

    # rosary from the left hip (her left = +X): walnut beads, upright wooden cross
    bone('rosary', (4.5, -10, -5.6), parent='body', rot=(-7, 0, -3), mat=wood_mat)
    box('rosary', (4.0, -10, -6.1), (1, 13, 1), name='beads', glow=True)
    box('rosary', (4.0, 3, -6.3), (1, 5, 1), name='cross', glow=True)
    box('rosary', (3.0, 4, -6.3), (3, 1, 1), name='cross', glow=True)

    # ---------------- robe: eight flared panels round an octagonal hull, each dissolving into light, with light
    # streamers trailing below.  Each panel is authored facing -Z at its pivot and yawed into place.
    for k, name in enumerate(PANEL_NAMES):
        (x0, z0), (x1, z1) = HULL[k], HULL[(k + 1) % 8]
        ln = math.hypot(x1 - x0, z1 - z0)
        tx, tz = (x1 - x0) / ln, (z1 - z0) / ln
        nx, nz = tz, -tx                                    # outward normal (hull runs clockwise seen from above)
        cxm, czm = (x0 + x1) / 2 + nx * 0.5, (z0 + z1) / 2 + nz * 0.5
        yaw = math.degrees(math.atan2(-nx, -nz))            # local -Z -> (nx, nz)
        flare = -7.0 if k % 2 == 0 else -9.0
        bone(name, (cxm, -9, czm), parent='body', rot=(flare, yaw, 0), mat=habit_mat)
        wd = int(round(ln)) + 2
        box(name, (cxm - wd / 2, -9, czm - 0.5), (wd, ROBE_H, 1), name='panel', glow=True)
        for off, sw, sy, sh in STREAMERS[name]:
            box(name, (cxm + off - sw / 2, sy, czm - 0.62), (sw, sh, 0), mat=light_mat, name='streamer', glow=True)

    # ---------------- chest: slim bodice under a rounded white guimpe, upright wooden cross
    bone('chest', (0, -10, 0), parent='body', mat=habit_mat)
    ubox('chest', (-6.5, -26, -4), (13, 16 - int(TY), 8), name='bodice')
    ubox('chest', (-10.5, -27, -6), (21, 10, 12), mat=linen_mat, name='guimpe', glow=True)
    ubox('chest', (-0.5, -22.5, -6.8), (1, 5, 1), mat=wood_mat, name='cross', glow=True)
    ubox('chest', (-1.5, -21.5, -6.8), (3, 1, 1), mat=wood_mat, name='cross', glow=True)

    # long back veil from the nape to the hips (angled in so it rests on the back)
    ubone('veil', (0, -31, 9), parent='chest', rot=(-8, 0, 0), mat=habit_mat)
    ubox('veil', (-10.5, -31, 8.5), (21, 27 - int(TY), 1), name='veil_back')

    # ---------------- neck (inside the wimple)
    ubone('neck', (0, -27, 0), parent='chest', mat=skin_mat)
    ubox('neck', (-3, -30, -3), (6, 4, 6), mat=linen_mat, name='chinwrap')

    # ---------------- head: face window x -7.5..7.5 / y (-45..-28) + TY
    ubone('head', (0, -28, 0), parent='neck', mat=skin_mat)
    fbox('head', (-7.5, -45, -7), (15, 17, 13), 'skull')
    fbox('head', (-6.5, -43, -7.5), (5, 2, 1), 'brow')                     # brow pads over each eye
    fbox('head', (1.5, -43, -7.5), (5, 2, 1), 'brow')
    fbox('head', (-1.5, -37, -7.75), (3, 3, 1), 'nose')
    ubox('head', (-9.5, -48, -8), (19, 3, 14), mat=linen_mat, name='band', glow=True)
    ubox('head', (-9.5, -45, -8), (2, 17, 13), mat=linen_mat, name='coif_side', glow=True)
    ubox('head', (7.5, -45, -8), (2, 17, 13), mat=linen_mat, name='coif_side', glow=True)
    ubox('head', (-7.5, -28, -7.5), (15, 4, 12), mat=linen_mat, name='chinwrap', glow=True)
    ubox('head', (-10.5, -51, -8.75), (21, 3, 18), mat=habit_mat, name='crown')
    ubox('head', (-8.5, -52, -6.5), (17, 1, 15), mat=habit_mat, name='cap')
    ubox('head', (-9.5, -48, 7.25), (19, 20, 2), mat=habit_mat, name='nape')

    ubone('eyelids', (0, -41, -7.2), parent='head', mat=lid_mat)
    ubox('eyelids', (-6.5, -41, -7.2), (5, 4, 0), name='lid',
         decals={'front': pixelart(LID_R, LIDPAL, anchor='topleft')})
    ubox('eyelids', (1.5, -41, -7.2), (5, 4, 0), name='lid',
         decals={'front': pixelart(LID_L, LIDPAL, anchor='topleft')})

    # speech: an open-mouth plane tucked 0.2 behind the face plane (hidden); Java slides it forward to talk
    ubone('mouth', (0, -33, -6.8), parent='head', mat=lid_mat)
    ubox('mouth', (-2.5, -33, -6.8), (5, 3, 0), name='mouth_open',
         decals={'front': pixelart(MOUTH_OPEN, FPAL, anchor='topleft')})

    for side, sx in (('right', -1), ('left', 1)):
        vb = f'veil_{side}'
        ubone(vb, (10.0 * sx, -50, 0), parent='head', rot=(0, 0, -7 * sx), mat=habit_mat)
        ubox(vb, (10.0 * sx - 1, -50, -7.75), (2, 27, 17), name='veil_side')

    # ---------------- arms: bell sleeves, slender hands
    for side, sx in (('right', -1), ('left', 1)):
        arm, fa, sl, hand, fing = (f'{side}_arm', f'{side}_forearm', f'{side}_sleeve', f'{side}_hand',
                                   f'{side}_fingers')
        ax = 12.5 * sx
        ubone(arm, (ax, -24, 0), parent='chest', rot=(-4, 0, -6 * sx), mat=habit_mat)
        ubox(arm, (ax - 3, -26, -3), (6, 12, 6), name='sleeve_up')
        ubone(fa, (ax, -14.5, 0), parent=arm, rot=(-14, 0, 3 * sx), mat=habit_mat)
        ubox(fa, (ax - 2, -15.5, -2), (4, 10, 4), name='forearm')       # inner sleeve (shows when the bell droops)
        ubox(fa, (ax - 2, -5.5, -2), (4, 1, 4), mat=linen_mat, name='undercuff', inflate=0.3)
        ubone(sl, (ax, -11, 0), parent=fa, mat=habit_mat)
        ubox(sl, (ax - 4, -11, -4), (8, 8, 8), name='cuff')
        ubone(hand, (ax, -4, 0), parent=fa, rot=(0, -30 * sx, 0), mat=hand_mat)   # palms turned a little forward
        ubox(hand, (ax - 1, -4, -2), (2, 5, 4), name='palm', glow=True)
        ubox(hand, (ax - 0.5, -3, -3), (1, 4, 1), name='thumb', glow=True)
        ubone(fing, (ax, 1, 0), parent=hand, rot=(-8, 0, 0), mat=hand_mat)      # fingers softly curled
        for zz, ln in ((-2, 4), (-1, 5), (0, 4), (1, 3)):
            ubox(fing, (ax - 0.5, 1, zz + 0.1), (1, ln, 1), inflate=-0.1, name='finger', glow=True)

    # zero-thickness planes with transparent edges get their own gutter-separated strip at the bottom of the sheet,
    # so no neighbouring texel of the packed atlas can bleed into them as a hairline
    u, v, row_h = 0, 200, 0
    for b in r.bones.values():
        for c in b.cubes:
            if 0 in c.size:
                w, h = c.uv_size()
                if u + w > 256:
                    u, v, row_h = 0, v + row_h + 1, 0
                c.uv = (u, v)
                u += w + 1
                row_h = max(row_h, h)

    m = Model('clara', 256, 256, r.roots)
    m.scale = 0.5
    m.render_type = 'entityTranslucentEmissive'
    MODEL = m
    return m


def _mirror(right):
    """Pose entries for both arms from the right-arm values (mirror across x = 0: yRot and zRot flip)."""
    out = {}
    for name, (x, y, z, dx, dy, dz) in right.items():
        out['right_' + name] = (x, y, z, dx, dy, dz)
        out['left_' + name] = (x, -y, -z, -dx, dy, dz)
    return out


POSES = {
    # ascension: she rises, arms open wide and low, palms turned forward and up, head lifted, eyes OPEN (the lids
    # fold back into the head)
    'rise': {
        'body': (-0.04, 0, 0, 0, -3.0, 0),
        'chest': (-0.06, 0, 0, 0, 0, 0),
        'neck': (-0.05, 0, 0, 0, 0, 0),
        'head': (-0.22, 0, 0, 0, 0, 0),
        'eyelids': (1.5708, 0, 0, 0, 0, 0),
        'veil': (0.12, 0, 0, 0, 0, 0),
        **_mirror({
            'arm': (-0.379, 0.431, 0.377, 0, 0, 0),
            'forearm': (-0.138, 0.287, 0.135, 0, 0, 0),
            'sleeve': (1.0, 0, 0.05, 0, 0, 0),          # the bell sleeves hang from the open arms like wings
            'hand': (-0.35, 0.25, 0.014, 0, 0, 0),
        }),
    },
    # 'Gracias por venir': eyes open, head a little lifted, mouth open (the speech frame Java flaps)
    'speak': {
        'head': (-0.08, 0, 0.05, 0, 0, 0),
        'eyelids': (1.5708, 0, 0, 0, 0, 0),
        'mouth': (0, 0, 0, 0, 0, -0.45),
    },
    # gratitude: a gentle bow of the head over hands joined in prayer at the chest, eyes closed
    'bow': {
        'chest': (0.08, 0, 0, 0, 0, 0),
        'neck': (0.08, 0, 0, 0, 0, 0),
        'head': (0.28, 0, 0, 0, 0, 0),
        **_mirror({
            'arm': (-0.462, -0.48, -0.217, 0, 0, 0),
            'forearm': (-0.832, -0.448, 0.111, 0, 0, 0),
            'hand': (-0.874, -0.347, 0.685, 0, 0, 0),
        }),
    },
}

ANIM_NOTES = """
Clara (the freed soul of Sor Maria) -- animation contract.  Angles in radians, ADDED to the rest pose; offsets
(dx, dy, dz) in model texels at 2x density (inside scale 0.5: 2 texels = 1 vanilla pixel).  t = ageInTicks.
Render the base with RenderType.entityTranslucentEmissive(texture) (alpha is baked: skin 244, linen 240, veil 244,
habit 226, light fading to 0) and the 'eyes' layer as an additive emissive overlay (RenderType.eyes) -- it carries
the warm glow of the face, linen, hands, robe rim, embers and streamers, and never the eyes themselves.  Fade her in
and out with the vertex alpha (0 -> 1 over 40 ticks).  She is NOT scary: every motion is slow, soft and continuous
(sine eases, no snaps, no twitches).  She never walks: the robe ends in light.  Poses: rise, speak, bow.

ENDING BEAT (suggested): appear in 'bow' with alpha 0 -> 1 and body dy +6 -> 0 (40 ticks)  ->  lift the head out
of the bow (30 ticks)  ->  OPEN THE EYES (eyelids, 20 ticks)  ->  'speak' while clara.voz plays ("Gracias por
venir. Digale a Teresita que no fue su culpa.")  ->  blend to 'rise' over 60 ticks while she floats up 2-3 blocks
->  white flash, alpha -> 0.

ROOT
* body -- root at the waist (pivot y -10): leather cincture + hidden core.  HOVER: dy = -1.0 + sin(t*0.06)*1.0
  (the light streamers stay 1-3 texels above the floor), xRot sin(t*0.045)*0.02, yRot sin(t*0.02)*0.04.
  Rise: (-0.04, 0, 0, 0, -3, 0) then keep adding dy for the ascension.  Bow: 0.
* rosary -- walnut beads + upright wooden cross hanging from her left hip.  Lagging pendulum:
  xRot = -bodyXRot*0.8 + sin(t*0.06 - 0.8)*0.05, zRot = sin(t*0.05 - 0.5)*0.06.  Rise: trails +0.12.

ROBE -- eight panels round an octagonal hull, children of body, pivots at the hips (y -9), rest flare -7/-9 deg,
k = 0..7 in this order: skirt_front, skirt_front_left, skirt_left, skirt_back_left, skirt_back, skirt_back_right,
skirt_right, skirt_front_right.  Each panel carries its light streamers (zero-thickness planes) so they sway with
it; the dissolve into light is painted, so no bone is needed for it.
* skirt_* -- slow underwater ripple, out of phase: xRot += sin(t*0.07 + k*0.785)*0.05 (local x = outward
  flare: negative opens the panel).  Rise: front panels (k 0,1,7) -0.08, back panels (k 3,4,5) +0.12 (the hem
  trails below her as she lifts), sides (k 2,6) -0.05.  Bow: all +0.03 (the robe settles).  Never let a panel
  go past -0.35 or the streamers lift into view above the hem.

TORSO
* chest -- slim bodice, rounded white guimpe with the upright wooden cross on its cord.  Breathing (she breathes
  even as a soul, it reads as alive): xRot sin(t*0.05)*0.015.  Rise -0.06 (opens), bow +0.08.
* veil -- the long back veil (nape to hips).  Hangs with gravity: xRot = -chestXRot*0.6 + sin(t*0.05 - 1.2)*0.03.
  Rise +0.12 (streams back).  Bow -0.03.
* neck -- inside the wimple.  Follows the head softly: 30 % of the look pitch.  Rise -0.05, bow +0.08.
* head -- skull with the 15 x 17 face (brow pads, nose), coif band, coif sides, chin wrap, veil crown + cap and
  nape.  FOCUS bone.  Looks at the player with gentle easing (yaw clamp +-0.6, pitch +-0.3, lerp 0.08 per
  tick).  Idle: a slow tilt zRot sin(t*0.03)*0.05.  Rise (-0.22): lifts her face to the light.  Speak
  (-0.08, 0, 0.05).  Bow 0.28 (with neck + chest: a 25 deg bow).
* eyelids -- two zero-thickness closed-lid planes (peaceful U-shaped lash curves) 0.2 texels in front of the open
  eyes, pivot at the top of the lids (y -44).  REST = EYES CLOSED.  To open: xRot 0 -> +1.5708 over ~20 ticks
  (the lids fold back into the head), or yScale 1 -> 0 (lids retract upward from the pivot), or visible = false.
  Blink while open (2 ticks closed every 80-140 ticks).  Keep closed in 'bow'.
* mouth -- the speech frame: a zero-thickness open-mouth plane tucked 0.2 texels BEHIND the face plane (hidden
  at rest; the face shows a closed, faintly smiling mouth).  Talking: dz -0.45 brings it in front of the face
  ('speak' pose); flap it with the voice (open 2-3 ticks per syllable, or whenever the clara.voz amplitude is
  above a threshold); return dz 0 when silent.
* veil_right / veil_left -- the black veil falling from the crown onto the shoulders (rest flare 7 deg).  Sway
  zRot += sin(t*0.05 + side)*0.03; rise: open outward 0.08 (right +, left -).

ARMS (right_* on -X; left mirrors yRot / zRot)
* right_arm / left_arm -- upper sleeve, shoulder pivot inside the guimpe.  Idle: xRot sin(t*0.05)*0.03, a
  slow forward drift.  Rise (-0.379, +-0.431, +-0.377): arms open wide and low.  Bow (-0.462, -+0.48, -+0.217).
* right_forearm / left_forearm -- inner sleeve (black) ending in the white undercuff at the wrist; elbow pivot.
  Rise (-0.138, +-0.287, +-0.135).  Bow (-0.832, -+0.448, +-0.111): forearms come together at the chest.
* right_sleeve / left_sleeve -- the bell of the sleeve (8 x 8 x 8, white undercuff visible inside the opening),
  child of the forearm, pivot at the top of the bell.  It should always HANG: whenever the forearm lifts, rotate
  it back toward gravity (rise: (1.0, 0, +-0.05) -- they hang from the open arms like wings; lag 6-10 ticks
  behind the arm, plus sin(t*0.06)*0.04 sway).  Bow: 0 (the bells meet in front like a muff).
* right_hand / left_hand -- palm + thumb, wrist pivot; rest yaw 30 deg (palms turned slightly forward).
  Rise (-0.35, +-0.25, +-0.014): palms open forward and up, receiving the light.  Bow (-0.874, -+0.347,
  +-0.685): palms pressed together in prayer, fingers up.
* right_fingers / left_fingers -- four slender fingers with rose nails and glowing tips; rest curl -8 deg.
  Rise: uncurl +0.1 and breathe xRot sin(t*0.07)*0.04.  Bow: 0.
"""
