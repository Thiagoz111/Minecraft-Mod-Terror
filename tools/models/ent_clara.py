"""Clara -- the freed soul of Sor Maria de la Agonia (DEAD LINE, case 'convento', ending).

Authored at 2x texel density (model.scale = 0.5).  +Y down, ground y = 24, faces -Z, right_* on -X.  Centred on
x = 0, z = 0.  Veil top y = -51, lowest light streamer y ~ 23.

Design
------
Clara Ines Bustos, 33, the nun the demon wore.  The same habit as Sor Agonia but CLEAN and whole: starched white
coif and rounded guimpe, black veil, black wool habit with wide bell sleeves, a black cincture and a plain wooden
rosary -- and the pectoral cross is upright again.  She is not scary: beautiful and sad, rising in the chapel at
dawn with her arms open.

Silhouette: a calm, slender column.  Black veil framing a white oval (coif) that pours into the white guimpe on the
shoulders, a slim black bodice, long arms in bell sleeves, and a robe that flares a little and, from the thigh down,
DISSOLVES INTO LIGHT: the wool burns away in an organic dissolve with a gold-white rim, turns into warm luminous
mist and trails off as twelve light streamers that never touch the floor.

Face (15 x 17, hand-placed pixel art projected onto layered face cubes: skull, brow ridge, nose, lips+chin):
luminous warm skin in broad soft planes, brows tilted up at the inner ends (sad), big warm-brown eyes with a
shadowed upper sclera, a dark top-lash line with a little wing and one catchlight, a small nose, rose lips with a
faint, tired smile, soft blush and ONE tear glinting on her left cheek.  The closed state is a separate bone,
`eyelids`: two zero-thickness lid planes with peaceful closed-eye lash curves that sit just in front of the open
eyes.  She starts with them visible (eyes closed) and Java opens her eyes by hiding / folding them.

Colour: violet-black wool with a warm gold rim light and gold sheen on the fold ridges; cream linen with lavender
shadows; peach-rose skin pushed toward light; gold-white light for everything that dissolves.  Translucent
(entityTranslucentEmissive), alpha baked per material (skin 242, linen 238, veil 230, habit 222, fading to 0 in the
light); faces that are never seen are cut out so nothing ghosts through.  The emissive 'eyes' layer carries the
soft glow: catchlights, the tear, the lit planes of the face and linen, the hands and the burning dissolve rim.
"""
import math

from mcmodel import Model, fbm, vnoise, hash3, face_light, pick
from rig import Rig
from paint import hx, mix, pixelart, chain

RIG = None

# ------------------------------------------------------------------ translucency (alpha baked per material)
A_SKIN = 242
A_LINEN = 238
A_VEIL = 230
A_HABIT = 222
A_WOOD = 236


def A(c, a):
    return (c[0], c[1], c[2], int(max(0, min(255, a))))


def pal(*h):
    return [hx(c) for c in h]


# ------------------------------------------------------------------ palettes (dark -> light, hue shifted)
# luminous warm skin: rose-violet shadows (light under the skin), peach mids, cream lights
SKIN = pal('#3d2230', '#5e3340', '#82494f', '#a6635d', '#c4826f', '#dba287', '#ecbea2', '#f6d6bf', '#fde9d9',
           '#fff6ee')
# starched linen: lavender shadows -> warm cream lights
LINEN = pal('#3a3150', '#574d6c', '#776d8a', '#978ea6', '#b6adbf', '#cfc6d3', '#e3dbe0', '#f1ebea', '#faf6f1',
            '#ffffff')
# habit wool: violet blacks
HABIT = pal('#060409', '#0c0812', '#140e1c', '#1d1527', '#271d33', '#332641', '#413150', '#533f62', '#6a5276')
VEILC = pal('#040307', '#09060d', '#100b16', '#181120', '#21182b', '#2c2038', '#3a2b48', '#4d3a5c')
# the light she dissolves into: gold -> cream -> white
LIGHT = pal('#5a3820', '#8a5a2e', '#b7843f', '#d9aa58', '#efc979', '#f9e0a2', '#fdefca', '#fff8e8', '#ffffff')
RIM = hx('#f3cf86')
SHEEN = hx('#a57f86')
WOOD = pal('#1e110a', '#341f12', '#4f311c', '#6c4528', '#8a5c35', '#a97746', '#c79a62')
LEATHER = pal('#060406', '#0e090c', '#181014', '#22181c', '#2f2226', '#3e2e31')
NAIL = hx('#f5c9bf')

# face details
LASH = hx('#2a1712')
LASH2 = hx('#5e3b31')
BROW = pal('#5a3829', '#7a5038', '#9c6e52')
SCLERA = hx('#f4e8e0')
SCLERA_D = hx('#c9b3b0')
IRIS = pal('#24120a', '#4a2914', '#764421', '#a8682f')
CATCH = hx('#fffaf0')
LIPC = pal('#8d4651', '#b45f63', '#cf7d78', '#e7a395')
BLUSH = hx('#eda294')
TEAR = hx('#ffffff')
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


def apos(ctx):
    """Texel centre in absolute rest (unrotated) rig coordinates."""
    p = RIG.abs_pivot[ctx.bone.name]
    o = ctx.cube.origin
    lx, ly, lz = local(ctx)
    return p[0] + o[0] + lx, p[1] + o[1] + ly, p[2] + o[2] + lz


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


def dissolve(ctx, ay, ax, az, y0=-2.0, y1=14.0):
    """Organic burn-into-light dissolve.  Returns ('cloth', k) | ('rim', k) | ('light', k, s) | None."""
    k = clamp((ay - y0) / (y1 - y0))
    if k <= 0.0:
        return ('cloth', 0.0)
    n = fbm(ax * 0.26 + 3.1, ay * 0.1, az * 0.26 - 7.0, 3, 5)
    thr = k * 1.25 - 0.18
    if n > thr + 0.075:
        return ('cloth', k)
    if n > thr:
        return ('rim', k)
    s = vnoise(ax * 0.7 + az * 0.7, ay * 0.07, 2.0, 9)
    return ('light', k, s, thr - n)


HIDDEN = {
    # tag -> faces never seen (cut out so nothing ghosts through the translucency)
    'bodice': ('top', 'bottom'), 'hips': ('top', 'bottom'),
    'sleeve_up': ('top',), 'forearm': ('top', 'bottom'),
    'crown': (), 'veil_side': ('top',), 'nape': ('front', 'top'), 'veil_back': ('top',),
}
PANELS = ('panel',)


def habit_mat(ctx):
    """Clean black wool: long soft folds, warm gold sheen on the ridges, warm rim light on the silhouette edges, and
    from the thigh down an organic dissolve into light."""
    t = tag(ctx)
    f = ctx.face
    if f in HIDDEN.get(t, ()):
        return None
    if is_plane(ctx) and f == 'back':
        return None
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    ax, ay, az = apos(ctx)
    k = cseed(ctx)
    side = f in ('front', 'back', 'west', 'east')
    veil = t in ('crown', 'veil_side', 'nape', 'veil_back')
    ramp = VEILC if veil else HABIT
    a = A_VEIL if veil else A_HABIT
    v = 0.45 + face_light(ctx) * 1.05
    if side:
        big = max(ctx.w, ctx.h) > 3
        if big and t not in ('belt',):
            v += soft_fold(around(ctx), ay, k % 13, 6.0 if t in ('panel', 'veil_back') else 5.0)
        if edge(ctx) == 0 and min(ctx.w, ctx.h) > 2:
            v -= 0.06
    if t == 'cuff':
        if f == 'bottom':
            cx = abs(lx - w / 2) / (w / 2)
            cz = abs(lz - d / 2) / (d / 2)
            if max(cx, cz) > 0.72:
                return A(pick(ramp, 0.5), a)                # rolled rim of the bell
            return A(pick(LINEN, 0.22 + (1 - max(cx, cz)) * 0.2), 250)   # white undercuff deep inside
        if side and h - ly < 1.0:
            v += 0.14                                       # rolled edge of the bell catches the light
    if t == 'crown':
        if f == 'top':
            v -= 0.04
            if ctx.j in (0, ctx.h - 1) or ctx.i in (0, ctx.w - 1):
                v += 0.12
        elif f == 'front' and ctx.j == ctx.h - 1:
            v += 0.16                                       # brim edge over the white band
        elif f == 'bottom':
            v -= 0.15
    if t == 'veil_side' and f in ('west', 'east') and side:
        pass
    if t == 'veil_back' and side:
        cx = abs(lx - w / 2) / (w / 2) if f in ('front', 'back') else 1.0
        cut = h - 3.0 * cx ** 2
        if ly > cut:
            return None                                     # the veil hangs lower in the middle: rounded hem
        if cut - ly < 1.0:
            v += 0.12
    c = pick(ramp, v)
    if side and v > 0.58:
        c = mix(c, SHEEN, 0.22)                             # warm sheen on the lit ridges
    # warm rim light along the silhouette edges (backlit by her own glow)
    if side and t not in ('belt',):
        rim = 0.0
        if f in ('west', 'east'):
            rim = 0.18
        if ctx.i == 0 or ctx.i == ctx.w - 1:
            rim += 0.32 if f in ('front', 'back') else 0.15
        if rim:
            c = mix(c, RIM, rim * (0.55 if veil else 0.45))
    # dissolve into light (robe panels, and a little at the bottom of the bell sleeves never)
    if t in PANELS and f != 'top':
        r = dissolve(ctx, ay, ax, az)
        if r[0] == 'cloth':
            kk = r[1]
            if kk > 0:
                c = mix(c, LIGHT[2], kk * 0.45)             # the wool already warms and thins toward the rim
                a = a - kk * 40
                if hash3(int(ax * 2), int(ay * 2), int(az * 2), 71) > 0.985:
                    c = LIGHT[7]                            # sparks lifting off the cloth
                    emit(ctx, (220, 190, 130))
        elif r[0] == 'rim':
            c = LIGHT[7] if r[1] < 0.75 else LIGHT[6]
            a = 250
            emit(ctx, (210, 170, 100))
        else:
            kk, s, depth = r[1], r[2], r[3]
            if kk > 0.97 or depth > 0.55:
                return None
            lum = clamp(0.62 + s * 0.35 - depth * 0.6)
            c = pick(LIGHT, lum)
            a = (205 - kk * 150) * (1 - depth * 1.4) * (0.65 + s * 0.45)
            if a < 26:
                return None
            emit(ctx, (120, 92, 52), clamp(a / 210))
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
    return A(pick(LEATHER, v), A_HABIT + 12)


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
    v = 0.76 + face_light(ctx) * 0.8
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
        cord = 4.0 - (ly - 0.0) * 0.55
        if 0.5 < ly < 4.5 and abs(cx - max(0.0, cord)) < 0.5 and cx > 0.6:
            c = mix(c, LEATHER[3], 0.75)
    if side and v > 0.8 and f == 'front':
        emit(ctx, (34, 28, 22))
    return A(c, A_LINEN)


# ------------------------------------------------------------------ flesh
SKIN_HIDDEN = {'skull': ('top', 'west', 'east', 'back', 'bottom'), 'muzzle': ('back', 'top'),
               'nose': ('back',), 'brow': ('back',)}


def skin_mat(ctx):
    """Luminous warm skin for the sides/undersides of the face cubes (the fronts are the FACE pixel art)."""
    t = tag(ctx)
    f = ctx.face
    if f in SKIN_HIDDEN.get(t, ()):
        return None
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    v = 0.7 + face_light(ctx) * 0.7
    if f in ('west', 'east'):
        v -= 0.14
    if t == 'nose' and f == 'bottom':
        cx = lx - w / 2
        if abs(cx) > 0.5 and lz < d - 0.4:
            return A(SKIN[3], A_SKIN)                       # nostrils
        return A(SKIN[5], A_SKIN)
    if t == 'brow' and f == 'bottom':
        return A(SKIN[4], A_SKIN)                           # brow ridge shadow over the lids
    if t == 'muzzle' and f == 'bottom':
        return A(SKIN[4], A_SKIN)
    return A(pick(SKIN, v), A_SKIN)


def hand_mat(ctx):
    """Slender luminous hands: soft knuckle creases, finger splits, rose-pink nails, glowing fingertips."""
    t = tag(ctx)
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    v = 0.7 + face_light(ctx) * 0.8
    if f in ('west', 'east', 'front', 'back') and edge(ctx) == 0 and min(ctx.w, ctx.h) > 2:
        v -= 0.06
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
            emit(ctx, (110, 84, 60))
            return A(c, A_SKIN)
        if abs(ly - h * 0.45) < 0.5:
            v -= 0.08                                       # joint crease
    c = pick(SKIN, v)
    if v > 0.72:
        emit(ctx, (48, 36, 26))
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
    if ctx.face != 'front' and ctx.face != 'west':
        return None
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    k = cseed(ctx)
    across = lx if w > 0 else lz
    width = w if w > 0 else d
    cx = abs(across + 0.5 - width / 2 - 0.5) / max(1.0, width / 2)
    tip = h - 0.5 - hash3(int(across), k, 0, 31) * 3.5
    if ly > tip:
        return None
    tfade = ly / max(1.0, tip)
    s = vnoise(across * 0.8, ly * 0.12, k, 33)
    lum = clamp(0.92 - cx * 0.35 - tfade * 0.25 + (s - 0.5) * 0.25)
    c = pick(LIGHT, lum)
    top_in = clamp(ly / 4.0)
    a = 200 * top_in * (1 - tfade) ** 1.1 * (0.75 + s * 0.35)
    if a < 18:
        return None
    emit(ctx, (140, 110, 64), clamp(a / 200))
    return A(c, a)


# ------------------------------------------------------------------ the face mask
# 15 columns (x -7.5..7.5, col c <-> x = c - 7), 17 rows (row r <-> y = -45 + r, y -45..-28).
GX0, GY0 = -7.5, -45
FACE = [
    # 012345678901234
    "c3445555554443c",   # r0  y-45 shadow under the coif band
    "c4566777766654c",   # r1  y-44 forehead
    "4567bb787bb7654",   # r2  y-43 brows: inner ends lifted (sad)
    "4Bbb6677766bbB4",   # r3  y-42 brow tails
    "45qqq56755qqq54",   # r4  y-41 lid crease (under the brow ridge)
    "5kKKKK675KKKKk5",   # r5  y-40 upper lash line with a little wing
    "56vGIv674vGIv65",   # r6  y-39 shadowed upper sclera, catchlight, pupil
    "56wjiw674wjiw65",   # r7  y-38 warm amber lower iris
    "566qq67846qq665",   # r8  y-37 soft lower lid
    "56rr7768477rr65",   # r9  y-36 blush, nose
    "56777659467T765",   # r10 y-35 nose tip; the tear starts on her left cheek
    "566666n5n566t65",   # r11 y-34 nostrils
    "456665uUu5666T4",   # r12 y-33 upper lip
    "45665lLLLl56654",   # r13 y-32 mouth line, corners soft
    "456665pPp566654",   # r14 y-31 lower lip
    "c4566665666654c",   # r15 y-30 chin
    "cc45567765544cc",   # r16 y-29 chin underside, the coif wraps round
]
assert all(len(r) == 15 for r in FACE), [len(r) for r in FACE]

# closed lids (eyelids bone): one 5 x 4 plane per eye, rows y -41..-37, cols 1..5 and 9..13.
LID_R = [
    "56665",
    "67776",
    "k6776",
    "5KKKk",
]
LID_L = [
    "56665",
    "67776",
    "6776k",
    "kKKK5",
]

FPAL = {str(i): A(SKIN[i], A_SKIN) for i in range(10)}
FPAL.update({
    'c': A(LINEN[4], A_LINEN), 'C': A(LINEN[6], A_LINEN),
    'b': A(BROW[0], A_SKIN), 'B': A(BROW[2], A_SKIN), 'h': A(BROW[1], A_SKIN),
    'K': A(LASH, 250), 'k': A(LASH2, A_SKIN),
    'w': A(SCLERA, A_SKIN), 'v': A(SCLERA_D, A_SKIN),
    'I': A(IRIS[0], 250), 'i': A(IRIS[1], 250), 'j': A(IRIS[3], 250), 'G': A(CATCH, 255),
    'q': A(mix(SKIN[5], LIPC[0], 0.25), A_SKIN), 'r': A(mix(SKIN[6], BLUSH, 0.55), A_SKIN),
    'n': A(SKIN[3], A_SKIN),
    'u': A(LIPC[1], A_SKIN), 'U': A(LIPC[2], A_SKIN), 'L': A(LIPC[0], A_SKIN), 'l': A(mix(SKIN[5], LIPC[0], 0.5), A_SKIN),
    'p': A(LIPC[2], A_SKIN), 'P': A(LIPC[3], A_SKIN),
    'T': A(TEAR, 250), 't': A(TEAR2, 248),
})
GLOWPAL = {
    'G': (255, 240, 210, 255), 'j': (70, 40, 16, 255), 'T': (170, 180, 186, 255), 't': (90, 104, 112, 255),
    '8': (26, 20, 14, 255), '9': (34, 26, 18, 255), '7': (16, 12, 8, 255),
}


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
    rows = _slice(FACE, x0, y0, w, h)
    return {'front': pixelart(rows, FPAL, anchor='topleft'),
            'eyes:front': pixelart(rows, GLOWPAL, anchor='topleft')}


DEFAULT_MAT = habit_mat
FOCUS = 'head'


def build():
    global RIG, MODEL
    GLOW.clear()
    r = Rig()
    RIG = r

    def bone(name, pivot, parent=None, rot=(0, 0, 0), mat=None):
        return r.bone(name, pivot, parent=parent, rot=rot, mat=mat)

    def box(bone_, frm, size, mat=None, name=None, inflate=0.0, decals=None, glow=False):
        dec = dict(decals or {})
        if glow:
            for kk, fn in GLOW_ALL.items():
                dec[kk] = chain(dec[kk], fn) if kk in dec else fn
        c = r.box(bone_, frm, size, mat=mat, inflate=inflate, decals=dec)
        c.name = name
        return c

    def fbox(bone_, frm, size, name, mat=skin_mat):
        return box(bone_, frm, size, mat=mat, name=name, decals=face_decals(frm[0], frm[1], size[0], size[1]))

    # ---------------- body: root at the waist; cincture + hips
    bone('body', (0, -10, 0), mat=habit_mat)
    box('body', (-8, -11, -5), (16, 2, 10), mat=belt_mat, inflate=0.25, name='belt')
    box('body', (-7.5, -9, -4.5), (15, 6, 9), name='hips')

    # rosary from the left hip (her left = +X): walnut beads, upright wooden cross
    bone('rosary', (5.5, -10, -5.4), parent='body', rot=(-4, 0, -3), mat=wood_mat)
    box('rosary', (5, -10, -5.9), (1, 11, 1), name='beads', glow=True)
    box('rosary', (5, 1, -6.1), (1, 5, 1), name='cross', glow=True)
    box('rosary', (4, 2, -6.1), (3, 1, 1), name='cross', glow=True)

    # ---------------- robe: four flared panels dissolving into light, light streamers below each
    bone('skirt_front', (0, -9, -4.5), parent='body', rot=(-5, 0, 0), mat=habit_mat)
    box('skirt_front', (-9, -9, -5.5), (18, 23, 1), name='panel', glow=True)
    bone('skirt_back', (0, -9, 4.5), parent='body', rot=(6, 0, 0), mat=habit_mat)
    box('skirt_back', (-9, -9, 4.5), (18, 23, 1), name='panel', glow=True)
    bone('skirt_right', (-7.5, -9, 0), parent='body', rot=(0, 0, 6), mat=habit_mat)
    box('skirt_right', (-8.5, -9, -5), (1, 23, 10), name='panel', glow=True)
    bone('skirt_left', (7.5, -9, 0), parent='body', rot=(0, 0, -6), mat=habit_mat)
    box('skirt_left', (7.5, -9, -5), (1, 23, 10), name='panel', glow=True)

    bone('light_front', (0, 6, -5.4), parent='skirt_front', mat=light_mat)
    for x0, y0, ww, hh in ((-7.5, 5, 3, 14), (-2, 6, 4, 17), (3.5, 4, 3, 13)):
        box('light_front', (x0, y0, -5.3), (ww, hh, 0), name='streamer', glow=True)
    bone('light_back', (0, 6, 5.4), parent='skirt_back', mat=light_mat)
    for x0, y0, ww, hh in ((-6.5, 5, 3, 15), (-1, 6, 3, 16), (4, 5, 3, 12)):
        box('light_back', (x0, y0, 5.3), (ww, hh, 0), name='streamer', glow=True)
    bone('light_right', (-8.3, 6, 0), parent='skirt_right', mat=light_mat)
    for z0, y0, dd, hh in ((-4, 5, 3, 13), (1, 6, 3, 15)):
        box('light_right', (-8.2, y0, z0), (0, hh, dd), name='streamer', glow=True)
    bone('light_left', (8.3, 6, 0), parent='skirt_left', mat=light_mat)
    for z0, y0, dd, hh in ((-3.5, 6, 3, 15), (1.5, 5, 3, 12)):
        box('light_left', (8.2, y0, z0), (0, hh, dd), name='streamer', glow=True)

    # ---------------- chest: slim bodice under a rounded white guimpe, upright wooden cross
    bone('chest', (0, -10, 0), parent='body', mat=habit_mat)
    box('chest', (-7, -26, -4), (14, 16, 8), name='bodice')
    box('chest', (-10.5, -27, -6), (21, 10, 12), mat=linen_mat, name='guimpe', glow=True)
    box('chest', (-0.5, -22.5, -6.8), (1, 5, 1), mat=wood_mat, name='cross', glow=True)
    box('chest', (-1.5, -21.5, -6.8), (3, 1, 1), mat=wood_mat, name='cross', glow=True)

    # long back veil from the nape to the hips (angled in so it rests on the back)
    bone('veil', (0, -31, 9), parent='chest', rot=(-8, 0, 0), mat=habit_mat)
    box('veil', (-10.5, -31, 8.5), (21, 27, 1), name='veil_back')

    # ---------------- neck (inside the wimple)
    bone('neck', (0, -27, 0), parent='chest', mat=skin_mat)
    box('neck', (-3, -30, -3), (6, 4, 6), mat=linen_mat, name='chinwrap')

    # ---------------- head: veil top -51, face window x -7.5..7.5 / y -45..-28
    bone('head', (0, -28, 0), parent='neck', mat=skin_mat)
    fbox('head', (-7.5, -45, -7), (15, 17, 13), 'skull')
    fbox('head', (-6.5, -43, -7.75), (13, 2, 1), 'brow')
    fbox('head', (-1.5, -37, -7.75), (3, 3, 1), 'nose')
    fbox('head', (-2.5, -33, -7.5), (5, 5, 1), 'muzzle')
    box('head', (-9.5, -48, -8), (19, 3, 14), mat=linen_mat, name='band', glow=True)
    box('head', (-9.5, -45, -8), (2, 17, 13), mat=linen_mat, name='coif_side', glow=True)
    box('head', (7.5, -45, -8), (2, 17, 13), mat=linen_mat, name='coif_side', glow=True)
    box('head', (-7.5, -28, -7.5), (15, 4, 12), mat=linen_mat, name='chinwrap', glow=True)
    box('head', (-11.5, -51, -9), (23, 3, 18), mat=habit_mat, name='crown')
    box('head', (-9.5, -48, 7), (19, 20, 2), mat=habit_mat, name='nape')

    bone('eyelids', (0, -41, -7.25), parent='head', mat=lid_mat)
    box('eyelids', (-6.5, -41, -7.25), (5, 4, 0), name='lid',
        decals={'front': pixelart(LID_R, FPAL, anchor='topleft')})
    box('eyelids', (1.5, -41, -7.25), (5, 4, 0), name='lid',
        decals={'front': pixelart(LID_L, FPAL, anchor='topleft')})

    for side, sx in (('right', -1), ('left', 1)):
        vb = f'veil_{side}'
        bone(vb, (10.5 * sx, -49, 0), parent='head', rot=(0, 0, -3 * sx), mat=habit_mat)
        box(vb, (10.5 * sx - 1, -49, -7.5), (2, 25, 16), name='veil_side')

    # ---------------- arms: bell sleeves, slender hands
    for side, sx in (('right', -1), ('left', 1)):
        arm, fa, sl, hand, fing = (f'{side}_arm', f'{side}_forearm', f'{side}_sleeve', f'{side}_hand',
                                   f'{side}_fingers')
        ax = 12.5 * sx
        bone(arm, (ax, -24, 0), parent='chest', rot=(-4, 0, -5 * sx), mat=habit_mat)
        box(arm, (ax - 3, -26, -3), (6, 12, 6), name='sleeve_up')
        bone(fa, (ax, -14.5, 0), parent=arm, rot=(-16, 0, 3 * sx), mat=habit_mat)
        box(fa, (ax - 2.5, -15.5, -2.5), (5, 6, 5), name='forearm')
        box(fa, (ax - 2, -5, -2), (4, 1, 4), mat=linen_mat, name='undercuff')
        bone(sl, (ax, -10, 0), parent=fa, mat=habit_mat)
        box(sl, (ax - 3.5, -10, -3.5), (7, 7, 7), name='cuff')
        bone(hand, (ax, -4, 0), parent=fa, rot=(0, 0, 0), mat=hand_mat)
        box(hand, (ax - 1, -4, -2), (2, 5, 4), name='palm', glow=True)
        box(hand, (ax - 0.5, -3, -3), (1, 4, 1), name='thumb', glow=True)
        bone(fing, (ax, 1, 0), parent=hand, rot=(0, 0, 0), mat=hand_mat)
        for zz, ln in ((-2, 4), (-1, 5), (0, 4), (1, 3)):
            box(fing, (ax - 0.5, 1, zz + 0.1), (1, ln, 1), inflate=-0.1, name='finger', glow=True)

    m = Model('clara', 256, 256, r.roots)
    m.scale = 0.5
    m.render_type = 'entityTranslucentEmissive'
    MODEL = m
    return m


POSES = {
    # ascension: rises, arms open wide, palms up and forward, head lifted, eyes OPEN (lids folded away)
    'rise': {
        'body': (-0.04, 0, 0, 0, -3.0, 0),
        'chest': (-0.08, 0, 0, 0, 0, 0),
        'neck': (-0.06, 0, 0, 0, 0, 0),
        'head': (-0.26, 0, 0, 0, 0, 0),
        'eyelids': (1.5708, 0, 0, 0, 0, 0),
        'right_arm': (-0.4, 0, 1.1, 0, 0, 0),
        'left_arm': (-0.4, 0, -1.1, 0, 0, 0),
        'right_forearm': (-0.3, 0, 0.15, 0, 0, 0),
        'left_forearm': (-0.3, 0, -0.15, 0, 0, 0),
        'right_sleeve': (0, 0, -0.7, 0, 0, 0),
        'left_sleeve': (0, 0, 0.7, 0, 0, 0),
        'right_hand': (0, 1.2, 0, 0, 0, 0),
        'left_hand': (0, -1.2, 0, 0, 0, 0),
        'veil': (0.12, 0, 0, 0, 0, 0),
        'veil_right': (0, 0, 0.1, 0, 0, 0),
        'veil_left': (0, 0, -0.1, 0, 0, 0),
        'skirt_front': (-0.1, 0, 0, 0, 0, 0),
        'skirt_back': (0.14, 0, 0, 0, 0, 0),
        'skirt_right': (0, 0, 0.1, 0, 0, 0),
        'skirt_left': (0, 0, -0.1, 0, 0, 0),
    },
    # gratitude: gentle bow of the head, hands together in prayer at the chest, eyes closed
    'bow': {
        'chest': (0.1, 0, 0, 0, 0, 0),
        'neck': (0.1, 0, 0, 0, 0, 0),
        'head': (0.38, 0, 0, 0, 0, 0),
        'right_arm': (-0.75, 0, -0.42, 0, 0, 0),
        'left_arm': (-0.75, 0, 0.42, 0, 0, 0),
        'right_forearm': (-1.3, 0, 0, 0, 0, 0),
        'left_forearm': (-1.3, 0, 0, 0, 0, 0),
        'veil': (-0.06, 0, 0, 0, 0, 0),
    },
}

ANIM_NOTES = """
TODO
"""
