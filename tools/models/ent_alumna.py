"""Las Alumnas del Coro -- the seven mouthless choir girls of the Colegio Santa Ines, 1984 (DEAD LINE).

Authored at 2x texel density (model.scale = 0.5).  +Y down, ground y = 24, faces -Z, right_* on -X.
Centred on x = 0, z = 0.  Real height 1.35 blocks: ground y = 24, top of the skull y = -19 (hair adds 1-3).

Design
------
Silhouette: a little girl whose head is a third of her height (14 x 15 x 13 on a 4-texel neck, wider than her
narrow 12-texel chest) and whose arms are too long: thin sleeves end in pale spidery hands that hang to the knee,
below the hem.  Argentine school uniform: a starched white guardapolvo (smock-coat) with a yoke, a box-pleated
A-line skirt made of four flared panels (front panel with a button placket and two patch pockets, one blotted with
ink; back panel with an inverted box pleat under a buttoned half-belt), a white Peter Pan collar (two planes) and
the navy school bow at the throat (knot, two pinched loops, two notched tails).  Bare knees (the pale band between
hem and socks), navy ribbed knee socks with a turned-down cuff, black patent Mary-Janes with a strap and buckle.
She is a ghost: every texel is translucent (alpha ~232 on the head, ~220 at the waist, fading to ~180 at the
shoes, the shoes and socks tinted toward a cold mist blue).

Face (front of a 1-texel skin plate, 14 x 15, read at 64 px): a big pale doll forehead; faint brows whose inner
ends are raised (worried); upper-lid creases; two 4x4 sockets that are REAL holes in the plate: through them you
see the skull front one texel deeper, painted from a dark grey ring to black with a 1-px glint that glows pale
cyan (emissive 'eyes' layer); purple-grey dark circles; a lit nose bridge and a 1-px nose shadow; doll blush 2x1;
and NO MOUTH: smooth skin with a 1-px darker seam where the mouth should be, a lit ridge above it and a soft
shadow under it, as if the skin had grown shut.  The 'jaw' bone holds the round singing "O" (lips ring, black
mouth); it is parked inside the skull and only comes out (pose 'freed') when the girls get their voices back.

Hair (seven bone groups, exactly one visible per girl; Java toggles ModelPart.visible):
  hair_paloma   dark brown, centre parting, hair pulled behind the ears into two long braids that fall over the
                shoulders onto the chest, faded sky-blue ribbon bows and brush ends (the leader).
  hair_mecha    black bob with heavy blunt bangs down to the brows, hair curtains framing the cheeks.
  hair_rocio    brown, combed back to a high ponytail with a maroon scrunchie (two segments, swings).
  hair_chela    chestnut, a big cloud of tight curls (bubble-shaded shell + side and crown clumps), curly fringe.
  hair_ofelia   blue-black, long and dead straight: centre parting, curtains beside the face, two locks over the
                shoulders, a waist-long back curtain, a navy headband (one cube cut into a hoop).
  hair_anasofia dark brown, centre parting, two high pigtails with red elastics that stick out and droop.
  hair_lola     black pixie cut with a side-swept fringe and a huge white satin bow on the top-left of the head.
The rest pose of the preview / gallery JSON shows one hairstyle (env ALUMNA_HAIR, default 'paloma'); the generated
Java model contains all seven groups.
"""
import bisect
import math
import os

from mcmodel import Model, hash3, face_light, pick
from rig import Rig
from paint import hx, mix


def pal(*h):
    return [hx(c) for c in h]


# ------------------------------------------------------------------ palettes (dark -> light, hue shifted)
# starched white smock: cool blue-grey shadows -> paper white (brief: #f2f4f6 #d9dee6 #b4bdcc #8691a6)
SMOCK = pal('#2f3546', '#444c60', '#5d6779', '#727d92', '#8691a6', '#9da7b9', '#b4bdcc', '#c8cfdb', '#d9dee6',
            '#e7eaf0', '#f2f4f6', '#fbfcfd')
GRIME = pal('#4f4738', '#6e6452', '#857a65', '#9b8f7a', '#b2a791')
# school navy (#121a33 .. #2b3a66)
NAVY = pal('#05080f', '#0a0f1e', '#0f162b', '#121a33', '#18223f', '#1e2a4d', '#253359', '#2b3a66', '#3a4c80',
           '#4f6399')
# ghost-pale skin (#e8dcd6 #b9a6a2 #8a7676), extended into cold lavender shadows
SKIN = pal('#3a3140', '#54474f', '#6e5e65', '#8a7676', '#a28f8d', '#b9a6a2', '#d0c2bd', '#e8dcd6', '#f6efeb')
BLUSH = hx('#e0a2a6')
BLUSH_D = hx('#c98189')
BROW = hx('#6a5658')
LAVENDER = hx('#7a6a86')
NAIL = hx('#9aa6bd')
# hair ramps
BROWN = pal('#0b0605', '#140c08', '#1e120c', '#2a1911', '#372116', '#462a1c', '#573524', '#6a422d', '#80533a')
BROWN_L = pal('#120a06', '#1d110a', '#2b190f', '#3a2215', '#4a2c1b', '#5c3822', '#70462a', '#875636', '#a06a45')
CHESTNUT = pal('#100806', '#1b0e09', '#29150d', '#381d12', '#482618', '#59301e', '#6c3c25', '#814b2f', '#985d3c')
BLACK = pal('#030305', '#07070b', '#0c0c12', '#13131b', '#1b1b26', '#252533', '#313145', '#42425c', '#5a5c7a')
BLUEBLACK = pal('#020307', '#05070e', '#090c17', '#0f1322', '#161b30', '#1f263f', '#2a3352', '#3a4569', '#525f88')
SCALP = hx('#9c8a8a')
# accessories
CELESTE = pal('#1c3244', '#2a4a63', '#3d6a88', '#5689aa', '#74a7c6', '#98c4dc', '#c2e0ee', '#e2f2f8')
MAROON = pal('#160407', '#28080d', '#3e0e15', '#55151e', '#6e1f28', '#8a2d33', '#a5403f')
RED = pal('#220405', '#3e0808', '#5f0e0d', '#821814', '#a3241d', '#c2382b', '#d9553c')
SATIN = pal('#2f3442', '#474e60', '#646c80', '#848c9f', '#a3abbb', '#c1c7d3', '#dadee6', '#eceef3', '#fafbfc')
PATENT = pal('#010102', '#040407', '#08080e', '#0e0e16', '#161722', '#212334', '#33374f', '#535a7c', '#8e98c0',
             '#d6def5')
SOLE = pal('#121016', '#1e1b23', '#2d2933', '#3e3946', '#524c5b')
SILVER = pal('#3a3d48', '#6b7080', '#a7adbd', '#e2e6f0')
INK = pal('#0b1230', '#16225a', '#22348a', '#3149b0')
PLASTER = pal('#8a6a52', '#a8836a', '#c29e84', '#d6b79c')
# eyes and mouth
RING_D = hx('#0d090f')
RING = hx('#161118')
RING_L = hx('#241c27')
VOID = hx('#030204')
GLINT = hx('#b9d3da')
GLOW_GLINT = (196, 246, 255, 255)
LIPS = pal('#4a2a33', '#6e3c47', '#8c525b', '#a86d73', '#c48b8e')
MOUTH = pal('#020102', '#0a0407', '#170a10', '#2a1219')
FADE = hx('#a3b6cf')

HAIRS = ['paloma', 'mecha', 'rocio', 'chela', 'ofelia', 'anasofia', 'lola']
SHOW = os.environ.get('ALUMNA_HAIR', 'paloma')


def clamp(v, a=0.0, b=1.0):
    return a if v < a else b if v > b else v


# ------------------------------------------------------------------ texel helpers
def local(ctx):
    """Texel centre in cube-local texel units (independent of bone rotation)."""
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


def A(ctx):
    """Absolute authoring coordinates (rest pose, before any bone rotation)."""
    lx, ly, lz = local(ctx)
    o = ctx.cube.a0
    return o[0] + lx, o[1] + ly, o[2] + lz


def edge(ctx):
    return min(ctx.i, ctx.j, ctx.w - 1 - ctx.i, ctx.h - 1 - ctx.j)


def tag(ctx):
    return ctx.cube.name or ''


def cseed(ctx):
    o, sz = ctx.cube.a0, ctx.cube.size
    return int(abs(o[0]) * 13.1 + abs(o[1]) * 7.3 + abs(o[2]) * 3.7 + sz[0] * 31 + sz[1] * 17 + sz[2] * 5) % 9973


def is_plane(ctx):
    return 0 in ctx.cube.size


def at(points):
    """Decal painting single texels: points = [(i, j, rgba), ...] relative to the face rect."""
    def fn(img, u0, v0, w, h):
        px = img.load()
        for i, j, c in points:
            if 0 <= i < w and 0 <= j < h:
                px[u0 + i, v0 + j] = c
    return fn


def ghost(c, y):
    """Translucent spirit: alpha ~232 on the head, ~220 at the waist, ~180 at the soles; misty toward the feet."""
    if c is None:
        return None
    if y < -1.0:
        a = 232
    else:
        a = 226 - clamp((y + 1.0) / 25.0) * 46
    t = clamp((y - 13.0) / 11.0) * 0.22
    if t > 0:
        c = mix(c, FADE, t)
    return (c[0], c[1], c[2], int(a))


def G(fn):
    def f(ctx):
        c = fn(ctx)
        if c is None:
            return None
        return ghost(c, A(ctx)[1])
    f.__name__ = fn.__name__
    return f


# ------------------------------------------------------------------ skin (neck, ears, hands, knees)
def skin_v(ctx, base=0.76):
    v = base + face_light(ctx) * 1.0
    if edge(ctx) == 0 and not is_plane(ctx) and ctx.face != 'top':
        v -= 0.05
    return v


@G
def skin_mat(ctx):
    t = tag(ctx)
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    v = skin_v(ctx)
    if t == 'neck':
        v -= 0.06
        if ly < 1.6:
            v -= 0.16                                   # shadow under the big head
        if f == 'front' and 1 <= ctx.i <= 2 and 2 <= ctx.j <= 3:
            v -= 0.05                                   # throat hollow
        return pick(SKIN, v)
    if t == 'ear':
        if f in ('west', 'east'):
            outer = (f == 'west') == (A(ctx)[0] < 0)
            if outer and ctx.i in (0, 1) and 1 <= ctx.j <= 1:
                return pick(SKIN, v - 0.3)               # ear canal shadow
            if outer and ctx.j == 0:
                v += 0.05
        return pick(SKIN, v - 0.04)
    if t == 'thigh':
        return pick(SKIN, v - 0.12 - ly / h * 0.1)
    return pick(SKIN, v)


@G
def hand_mat(ctx):
    """Long ghost-pale hands: knuckle creases, bluish nail beds, dirty fingertips."""
    t = tag(ctx)
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    v = skin_v(ctx, 0.74)
    if t == 'palm':
        if ly < 0.9 and f != 'top':
            v -= 0.12                                   # shadow under the cuff
        if f in ('west', 'east') and ly > h - 0.9:
            v -= 0.05                                   # knuckle line
        return pick(SKIN, v)
    if t in ('finger', 'index', 'thumb'):
        if f == 'top':
            return pick(SKIN, v - 0.1)
        if f == 'bottom':
            return mix(pick(SKIN, 0.5), NAIL, 0.45)
        if abs(ly - 1.5) < 0.5:
            v -= 0.08                                   # middle knuckle crease
        if t == 'finger' and f in ('west', 'east') and ctx.i == 0 and ctx.w > 1:
            v -= 0.1                                    # gap between the grouped fingers
        c = pick(SKIN, v)
        if ly > h - 1:
            c = mix(c, NAIL, 0.5)                       # cold blue fingertips / nails
        return c
    return pick(SKIN, v)


@G
def knee_mat(ctx):
    """Shin: bare pale knee band on top, navy ribbed knee sock below (a plaster on her left knee)."""
    f = ctx.face
    x, y, z = A(ctx)
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    if f == 'top':
        return pick(SKIN, 0.6)
    if f == 'bottom':
        return pick(NAVY, 0.15)
    if ly < 2.0:
        v = skin_v(ctx, 0.78)
        if ly < 0.6:
            v -= 0.1                                    # shadow under the hem
        c = pick(SKIN, v)
        if f == 'front' and x > 0 and 1 <= ctx.i <= 2:
            c = PLASTER[2] if ctx.i == 1 else PLASTER[1]    # a sticking plaster on her left knee
            if ly < 0.6:
                c = PLASTER[0]
        if f == 'front' and x < 0 and ctx.i == 2 and 0.6 < ly < 2.0:
            c = mix(c, LAVENDER, 0.35)                  # bruise on the right knee
        return c
    v = 0.5 + face_light(ctx) * 1.1
    v += 0.07 if ctx.i % 2 == 0 else -0.05              # knit ribs
    v -= clamp((ly - 3.0) / 3.0) * 0.12
    if edge(ctx) == 0 and f in ('west', 'east'):
        v -= 0.05
    return pick(NAVY, v)


@G
def cuff_mat(ctx):
    """Turned-down sock cuff: horizontal rib at the fold, fold shadow under it."""
    f = ctx.face
    if f in ('top', 'bottom'):
        return pick(NAVY, 0.35 if f == 'top' else 0.1)
    v = 0.6 + face_light(ctx) * 1.1 + (0.05 if ctx.i % 2 == 0 else -0.03)
    return pick(NAVY, v)


@G
def shoe_mat(ctx):
    """Black patent Mary-Jane: hard specular gloss on the toe, strap with a silver buckle, grey sole."""
    f = ctx.face
    x, y, z = A(ctx)
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    outer_x = x < 0 if f == 'west' else x > 0
    if f == 'bottom':
        if lz < 2.0:
            return pick(SOLE, 0.25)                     # heel block
        return pick(SOLE, 0.55 if (ctx.i + ctx.j) % 3 else 0.35)
    if f == 'top':
        # lz: 0 = heel, 7 = toe
        if lz < 2.6 and 1 <= ctx.i <= w - 2:
            return pick(PATENT, 0.08)                   # opening (shin stands here)
        if 2.6 <= lz < 3.6:
            return pick(PATENT, 0.45)                   # strap
        if 3.6 <= lz < 4.2:
            return PATENT[1]                            # gap under the strap edge
        v = 0.3 + (lz - 4.0) * 0.05
        if ctx.i == 1 and lz > 4.5:
            v = 0.8 if lz > 5.5 else 0.62               # gloss streak along the toe
        if ctx.i == 2 and lz > 6.0:
            v = 0.55
        return pick(PATENT, v)
    if ly > h - 1:
        return pick(SOLE, 0.55 if f == 'front' else 0.45)   # sole edge
    v = 0.3 + face_light(ctx) * 1.2
    if f == 'front':
        if ctx.j == 0:
            v += 0.25 if ctx.i in (1, 2) else 0.1       # glossy round toe cap
        if ctx.i == 1 and ctx.j == 0:
            return PATENT[9]
    if f in ('west', 'east'):
        # lz: strap continues down the sides; buckle on the outer side
        if 2.6 <= lz < 3.6 and ctx.j == 0:
            if outer_x:
                return SILVER[3] if ctx.j == 0 else SILVER[1]
            v += 0.12
        if ctx.j == 0 and lz > 4.0:
            v += 0.12                                   # rolled top edge catches light
        if lz > 5.5 and ctx.j == 1:
            v += 0.08
    if f == 'back':
        v -= 0.05
    return pick(PATENT, v)


# ------------------------------------------------------------------ smock (guardapolvo)
def pleat(u, period=4, off=0):
    k = (int(math.floor(u)) + off) % period
    return (0.06, 0.03, -0.05, -0.2)[k] if period == 4 else (0.05, -0.03, -0.18)[k]


@G
def smock_mat(ctx):
    t = tag(ctx)
    f = ctx.face
    x, y, z = A(ctx)
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    v = 0.78 + face_light(ctx) * 1.1
    if edge(ctx) == 0 and f != 'top' and not is_plane(ctx):
        v -= 0.05
    grime = 0.0
    if t == 'torso':
        if f == 'top':
            r = max(abs(x) / 3.0, abs(z) / 3.0)
            if r < 1.0:
                v -= 0.16                               # shadow ring at the neck
            if abs(abs(x) - 4.5) < 0.5:
                v -= 0.05                               # shoulder seams
        elif f in ('front', 'back'):
            if ctx.j == 3:
                v -= 0.1                                # yoke seam
            elif ctx.j == 4:
                v += 0.03
            if f == 'front' and ctx.j in (3, 4) and abs(x) < 5.5 - (ctx.j - 3) * 2:
                v -= 0.1                                # shadow under the collar flaps
            if ctx.j > 4:
                col = ctx.i + 1 if f == 'front' else ctx.w - ctx.i
                v += {'W': 0.08, 'w': 0.0, 'g': -0.06, 'c': -0.2, 'P': 0.06, 'p': -0.1}.get(PANEL_FRONT[0][col], 0)
        else:
            if abs(z) < 1.6 and y < 7:
                v -= 0.12                               # armpit under the sleeve
            if ctx.j == 3:
                v -= 0.06
    elif t == 'core':
        v -= 0.2
        if f == 'bottom':
            v -= 0.25
    elif t == 'panel':
        which = ctx.cube.which
        out = {'front': 'front', 'back': 'back', 'right': 'west', 'left': 'east'}[which]
        if f != out:
            v -= 0.32 if f not in ('top', 'bottom') else 0.2
            c = pick(SMOCK, v)
            return mix(c, GRIME[1], 0.55) if f == 'bottom' else c
        u, j = ctx.i, ctx.j
        rows = PANEL_FRONT if which == 'front' else PANEL_BACK if which == 'back' else PANEL_SIDE
        ch = rows[j][u if which != 'left' else ctx.w - 1 - u]
        v = PANEL_V[ch] + face_light(ctx) * 0.8
        c = pick(SMOCK, v)
        if which == 'front':
            ink = INK_BLOT.get((u, j))
            if ink is not None:
                c = mix(c, INK[ink[0]], ink[1])
        # grime soaked up from the floor: ragged top edge, darker streaks rising from the hem
        noise = hash3(u + cseed(ctx), 0, 3, 7)
        rise = 2.2 + noise * 1.6 + (1.2 if hash3(u, cseed(ctx), 5, 13) > 0.8 else 0.0)
        g = clamp((j - (h - rise)) / rise + 0.35)
        if g > 0.35:
            c = mix(c, GRIME[3] if j < h - 1 else GRIME[1], 0.25 + g * 0.45)
        return c
    elif t == 'sleeve':
        if ly < 1.0 and f != 'top':
            v -= 0.04
        if f in ('west', 'east'):
            inner = (f == 'east') == (x < 0)
            if inner:
                v -= 0.12
        if f in ('front', 'back') and ctx.i == 1:
            v += 0.03
    elif t == 'forearm':
        if ly < 1.0 and f in ('front', 'back') and ctx.i != 1:
            v -= 0.1                                    # elbow creases
        if f in ('west', 'east'):
            inner = (f == 'east') == (x < 0)
            if inner:
                v -= 0.1
        v -= ly / h * 0.05
    elif t == 'cuff':
        v += 0.03
        if f in ('front',) and ctx.i == 1:
            return pick(SMOCK, 0.99)                    # cuff button
        if f == 'bottom':
            v -= 0.25
    elif t == 'belt':
        v += 0.02
        if f == 'back' and ctx.i in (1, w - 2) and ctx.j == 0:
            return pick(SMOCK, 1.0)
        if f == 'back' and ctx.j == h - 1:
            v -= 0.08
    elif t == 'collar':
        if f != 'front':
            return None
        ch = COLLAR[ctx.j][ctx.i if ctx.cube.side == 'r' else ctx.w - 1 - ctx.i]
        if ch == '.':
            return None
        v = {'H': 1.0, 'h': 0.93, 's': 0.74, 'e': 0.52}[ch]
    c = pick(SMOCK, v)
    if grime:
        c = mix(c, GRIME[2], grime)
    return c


# Front skirt panel 14 x 9 (x -7..7).  W lit pleat face  w cloth  g edge turning away  c pleat crease
#  P placket edge  p placket overlap shadow  B button  b button shadow  K pocket fold  k pocket seam
#  q inside the pocket  H hem fold
PANEL_FRONT = [
    "gWwcWwPpWwcWwg",
    "gWwcWwBpWwcWwg",
    "gWwcWwbpWwcWwg",
    "gKKKKwPpwKKKKg",
    "gkqqkwBpwkqqkg",
    "gkqqkwbpwkqqkg",
    "gkkkkwPpwkkkkg",
    "gWwcWwBpWwcWwg",
    "HHHHHHbHHHHHHH",
]
# Back panel: two pleats each side of an inverted box pleat (dark V) under the half-belt
PANEL_BACK = [
    "gWwcWwkkWwcWwg",
    "gWwcWwkkWwcWwg",
    "gWwcWWkkWwcWwg",
    "gWwcWWkkWwcWwg",
    "gWwcWWkkWwcWwg",
    "gWwcWwkkwWcWwg",
    "gWwcWwkkwWcWwg",
    "gWwcWwkkwWcWwg",
    "HHHHHHHHHHHHHH",
]
PANEL_SIDE = [
    "gWwcWwcWg",
    "gWwcWwcWg",
    "gWwcWwcWg",
    "gWwcWwcWg",
    "gWwcWwcWg",
    "gWwcWwcWg",
    "gWwcWwcWg",
    "gWwcWwcWg",
    "HHHHHHHHH",
]
PANEL_V = {'W': 0.93, 'w': 0.81, 'g': 0.64, 'c': 0.47, 'P': 0.93, 'p': 0.6, 'B': 1.0, 'b': 0.5, 'K': 0.99,
           'k': 0.45, 'q': 0.76, 'H': 0.5}
# ink blot on her left pocket + a drip (front panel texels u, j) -> INK index
INK_BLOT = {(10, 4): (2, 0.35), (11, 4): (1, 0.6), (10, 5): (1, 0.75), (11, 5): (0, 0.9), (12, 5): (2, 0.4),
            (11, 6): (1, 0.55), (11, 7): (2, 0.35), (9, 5): (3, 0.25)}

# Peter Pan collar flap, 6 x 4 (index 0 = outer shoulder end, 5 = centre front)
COLLAR = [
    "eHHHHHH",
    "ehhhhhh",
    "eehhhhe",
    ".eeeee.",
]


# ------------------------------------------------------------------ navy bow (moño)
BOW_LOOP = [
    # 3 x 4, index 0 = outer rounded end, 2 = pinched at the knot
    "Hh.",
    "HhM",
    "mmM",
    "dd.",
]


@G
def bow_mat(ctx):
    f = ctx.face
    t = tag(ctx)
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    v = 0.55 + face_light(ctx) * 1.0
    if t == 'knot':
        if f == 'front':
            v += 0.08 if ctx.j == 0 else (-0.12 if ctx.j == h - 1 else 0.0)
            if ctx.i == 0:
                v += 0.06
        else:
            v -= 0.12
        return pick(NAVY, v)
    if t == 'loop':
        if f in ('front', 'back'):
            i = ctx.i if f == 'front' else ctx.w - 1 - ctx.i
            ii = i if ctx.cube.side == 'r' else ctx.w - 1 - i
            ch = BOW_LOOP[ctx.j][ii]
            if ch == '.':
                return None
            v = {'H': 0.82, 'h': 0.68, 'M': 0.5, 'm': 0.45, 'd': 0.3}[ch] + face_light(ctx)
            if f == 'back':
                v -= 0.2
            return pick(NAVY, v)
        if f in ('west', 'east'):
            far = (f == 'west') == (ctx.cube.side == 'r')
            if not far:
                return None
            return pick(NAVY, 0.45 - ly / h * 0.15)
        if f == 'top':
            ii = ctx.i if ctx.cube.side == 'r' else ctx.w - 1 - ctx.i
            return None if BOW_LOOP[0][ii] == '.' else pick(NAVY, 0.7)
        ii = ctx.i if ctx.cube.side == 'r' else ctx.w - 1 - ctx.i
        return None if BOW_LOOP[3][ii] == '.' else pick(NAVY, 0.2)
    if t == 'tail':
        if f != 'front':
            return None
        if ly > h - 1 and ctx.i == (1 if ctx.cube.side == 'r' else 0):
            return None                                 # notched ribbon end
        v -= ly / h * 0.15
        if ctx.i == (0 if ctx.cube.side == 'r' else 1):
            v += 0.08
        return pick(NAVY, v)
    return pick(NAVY, v)


# ------------------------------------------------------------------ the face
# Plate front, 14 x 15 (x -7..7, y -19..-4).  Legend:
#  o skin  O highlight  s soft shade  S deep socket shade  b faint brow  u lid crease  d dark circle
#  . socket hole (the skull front shows through, one texel deeper)  N nose bridge light  n nose shadow
#  p blush  L lit ridge above the seam  M seam end  m mouth seam  l shadow under the seam
FACE = [
    # 0123456789ABCD
    "oooooooooooooo",   # r0  forehead (hairline planes cover the top rows)
    "ooooOOOOOOoooo",   # r1  domed doll forehead
    "sooooOOOOoooos",   # r2
    "soooobooboooos",   # r3  inner ends of the brows raised (worried)
    "sobbboooobbbos",   # r4  faint brows
    "souuuuoouuuuos",   # r5  upper lid creases
    "ssS..SNoS..Sss",   # r6  sockets (4x4, rounded): real holes in the plate
    "sS....No....Ss",   # r7
    "sS....oo....Ss",   # r8
    "ssS..SooS..Sss",   # r9
    "soddddonddddos",   # r10 dark circles, 1-px nose shadow
    "sppoooooooopps",   # r11 doll blush 2x1
    "soooMmmmmMooos",   # r12 NO MOUTH: only a seam where the skin grew shut
    "ssooooooooooss",   # r13
    "SssoooooooossS",   # r14 chin
]
assert all(len(r) == 14 for r in FACE) and len(FACE) == 15


def face_base(fx, fy):
    cx = (fx - 6.5) / 7.0
    v = 0.84 - cx * cx * 0.1
    if fx <= 6:
        v += 0.02                                       # key light from her right (viewer's left)
    if fy >= 13:
        v -= (fy - 12) * 0.03
    return v


def face_px(ch, fx, fy):
    b = face_base(fx, fy)
    if ch == 'O':
        return pick(SKIN, b + 0.1)
    if ch == 's':
        return pick(SKIN, b - 0.11)
    if ch == 'S':
        return mix(pick(SKIN, b - 0.3), LAVENDER, 0.3)
    if ch == 'b':
        return mix(pick(SKIN, b - 0.06), BROW, 0.4)
    if ch == 'u':
        return mix(pick(SKIN, b - 0.16), LAVENDER, 0.25)
    if ch == 'd':
        return mix(pick(SKIN, b - 0.13), LAVENDER, 0.3)
    if ch == 'N':
        return pick(SKIN, b + 0.1)
    if ch == 'n':
        return pick(SKIN, b - 0.22)
    if ch == 'p':
        return mix(pick(SKIN, b), BLUSH, 0.6)
    if ch == 'L':
        return pick(SKIN, b + 0.07)
    if ch == 'M':
        return pick(SKIN, b - 0.12)
    if ch == 'm':
        return mix(pick(SKIN, b - 0.26), LAVENDER, 0.2)
    if ch == 'l':
        return pick(SKIN, b - 0.07)
    return pick(SKIN, b)


@G
def plate_mat(ctx):
    f = ctx.face
    if f == 'back':
        return None
    if f == 'front':
        ch = FACE[ctx.j][ctx.i]
        if ch == '.':
            return None
        return face_px(ch, ctx.i, ctx.j)
    if f == 'top':
        return pick(BROWN, 0.3)
    if f == 'bottom':
        return pick(SKIN, 0.5)
    v = skin_v(ctx, 0.74)
    if ctx.j >= 13:
        v -= 0.05
    if ctx.j == 11:
        return mix(pick(SKIN, v), BLUSH, 0.35)
    return pick(SKIN, v)


def socket_px(i, j):
    for c0 in (2, 8):
        a, b = i - c0, j - 6
        if 0 <= a <= 3 and 0 <= b <= 3:
            if (a, b) == (1, 1):
                return GLINT
            if 1 <= a <= 2 and 1 <= b <= 2:
                return VOID
            if b == 0:
                return RING_D
            if b == 3:
                return RING_L
            return RING
    return None


@G
def skull_mat(ctx):
    """Skull behind the face plate: socket rings seen through the holes, skin cheeks/temples, hair elsewhere."""
    f = ctx.face
    x, y, z = A(ctx)
    if f == 'front':
        c = socket_px(ctx.i, ctx.j)
        return c if c is not None else pick(SKIN, 0.55)
    if f == 'bottom':
        if z < -1.5:
            return pick(SKIN, 0.48 - (z + 6) * 0.0)
        return pick(SKIN, 0.36)
    if f in ('west', 'east'):
        if z < -2.2 and y > -15.5 or y > -8:
            v = skin_v(ctx, 0.74)
            if -9 <= y <= -7 and z < -4:
                return mix(pick(SKIN, v), BLUSH, 0.35)
            if z > 0 and y > -8:
                v -= 0.1 + clamp((-6.0 - y) / 2.0) * 0.1   # nape in the shadow of the hair
            return pick(SKIN, v - (0.06 if y > -6 else 0.0))
    if f == 'back' and y > -7.5:
        return pick(SKIN, 0.56 - clamp((-5.5 - y) / 2.0) * 0.12)   # nape (shows under short hair)
    return pick(BROWN, 0.12 + face_light(ctx) * 0.3)


EYE_GLOW = [(3, 7, GLOW_GLINT), (9, 7, GLOW_GLINT)]


# ------------------------------------------------------------------ the O mouth (jaw, freed only)
O_MOUTH = [
    ".LL.",
    "LKKL",
    "LKkL",
    ".ll.",
]


@G
def jaw_mat(ctx):
    f = ctx.face
    if f == 'front':
        ch = O_MOUTH[ctx.j][ctx.i]
        if ch == '.':
            return None
        return {'L': LIPS[3], 'l': LIPS[2], 'K': MOUTH[0], 'k': MOUTH[2]}[ch]
    if f == 'back':
        return MOUTH[0]
    return LIPS[1]


# ------------------------------------------------------------------ hair
_PART = {}


def _partition(seed):
    """Deterministic split of integer columns into strand clumps 2-4 texels wide."""
    if seed not in _PART:
        starts, widths = [], []
        x, k = -80, 0
        while x < 80:
            w = 2 + int(hash3(k, seed, 0, 41) * 2.999)
            starts.append(x)
            widths.append(w)
            x += w
            k += 1
        _PART[seed] = (starts, widths)
    return _PART[seed]


def clump_of(ui, seed):
    starts, widths = _partition(seed)
    k = bisect.bisect_right(starts, ui) - 1
    return k, ui - starts[k], widths[k]


def strands(u, along, ctx, seed, clump=2.5, sheen=None, light=0.9, soft=1.0):
    """Painted hair: clumps of 2-4 texels (lit edge, dark 1-px gap), one broken sheen band."""
    ui = int(math.floor(u * 2.5 / clump))
    k, pos, w = clump_of(ui, seed)
    r = hash3(k, seed, 0, 71)
    v = 0.47 + (r - 0.5) * 0.12 * soft + face_light(ctx) * light
    if pos == 0:
        v -= (0.13 if w > 2 else 0.08) * soft
    elif pos == w - 1:
        v += 0.05 * soft
    if sheen is not None:
        b = math.floor(sheen + (r - 0.5) * 2.2)
        a = math.floor(along)
        if a == b:
            v += 0.22 if pos != 0 else 0.1
        elif a == b - 1 or a == b + 1:
            v += 0.08
    return v


def curls(ctx, a, b, seed):
    """Tight ringlets: 3-texel columns, each a stack of round turns (lit crest, mid, dark groove) whose phase is
    offset per column, with a dark gap between columns; reads as springy curls, not as a knit."""
    col = math.floor(a / 3.0)
    la = a - col * 3.0
    hc = hash3(col, seed, 0, 17)
    phase = (b + hc * 3.0 + (la - 1.0) * 0.35) % 3.0
    v = 0.5 + face_light(ctx) * 0.8 + (hc - 0.5) * 0.1
    if phase < 1.0:
        v += 0.15 if 0.6 < la < 2.2 else 0.06           # round crest of the turn
    elif phase < 2.0:
        v += 0.0
    else:
        v -= 0.15                                       # groove under the turn
    if la < 0.6:
        v -= 0.12                                       # gap between ringlets
    return v


def pulled(style):
    return style in ('paloma', 'rocio', 'anasofia', 'lola')


def side_hair(style, y, z):
    """Hair mask on the sides of the shell (x = +-8)."""
    if -1.0 <= z <= 1.0 and -11.0 <= y <= -8.0 and pulled(style):
        return False                                     # the ear shows
    if not pulled(style):
        return True
    if style == 'lola':
        if y < -16.0:
            return True
        if y < -9.0:
            return z > -4.6 + max(0.0, y + 12.0) * 0.4   # short sideburn
        return z > 1.2 + (y + 9.0) * 0.3
    if y < -15.5:
        return True
    if y < -11.0:
        return z > -5.0 + (y + 15.5) * 0.65
    return z > 1.2


def back_bottom(style, x):
    """Lowest hair texel row on the back of the shell (nape line)."""
    return {'paloma': -6.0, 'rocio': -7.5, 'anasofia': -7.5, 'lola': -8.0}.get(style, 99)


@G
def shell_mat(ctx):
    c = ctx.cube
    st = c.style
    P = c.pal
    f = ctx.face
    x, y, z = A(ctx)
    lx, ly, lz = local(ctx)
    w, h, d = c.size
    if f == 'front':
        return None
    if f == 'bottom':
        if z < -7.0 or (-7.0 < x < 7.0 and z < 6.0):
            return None
        if abs(x) > 7.0 and not side_hair(st, y - 0.5, z):
            return None
        return pick(P, 0.16)
    if f in ('west', 'east') and not side_hair(st, y, z):
        return None
    if f == 'back' and pulled(st):
        nb = back_bottom(st, x)
        tip = hash3(int(x * 2), 3, cseed(ctx), 9) * 1.2
        if y > nb + tip:
            return None
    seed = HAIRS.index(st) * 7 + {'top': 0, 'west': 1, 'east': 2, 'back': 3}[f]
    if st == 'chela':
        if f == 'top':
            v = curls(ctx, x, z, seed)
        elif f in ('west', 'east'):
            v = curls(ctx, z, y, seed)
        else:
            v = curls(ctx, x, y, seed)
        v -= clamp((y + 8.0) / 6.0) * 0.16
        if f != 'top' and y < -19.0:
            v += 0.05
        if edge(ctx) == 0:
            v -= 0.08
        return pick(P, v)
    if f == 'top':
        part = st in ('paloma', 'ofelia', 'anasofia')
        if part and abs(x) < 0.5 and z < 1.5:
            return mix(pick(P, 0.6), SCALP, 0.5)        # centre parting
        if st == 'lola' and abs(x - 3.5) < 0.5 and z < 0.5:
            return mix(pick(P, 0.6), SCALP, 0.45)       # side parting
        if part:
            v = strands(z, abs(x), ctx, seed, sheen=5.5, light=0.5, soft=0.55)
        elif st == 'rocio':
            v = strands(x, z, ctx, seed, sheen=-1.0, light=0.5, soft=0.6)
        else:
            ang = math.atan2(x, z - 2.0) * 6.0
            v = strands(ang, math.hypot(x, z - 2.0), ctx, seed, sheen=5.0, light=0.5, soft=0.6)
        rr = max(abs(x) / 8.0, abs(z + 0.5) / 7.5)
        v -= clamp((rr - 0.75) / 0.25) * 0.08            # the crown rounds off toward the edges
        return pick(P, v + 0.06)
    if f in ('west', 'east'):
        if st in ('rocio', 'anasofia'):
            u = z + (y + 16.0) * 0.9                    # combed up and back
        elif st == 'paloma':
            u = z - (y + 16.0) * 0.45                   # combed back and down to the braids
        else:
            u = z
        v = strands(u + (40 if f == 'east' else 0), y, ctx, seed, sheen=-16.5)
        if not pulled(st):
            v -= clamp((y + 9.0) / 6.0) * 0.14          # ends in shadow
        if pulled(st) and not side_hair(st, y + 0.9, z - 0.9):
            v += 0.08                                   # lit hairline edge
        return pick(P, v)
    # back
    if st in ('paloma', 'anasofia') and abs(x) < 0.5:
        return mix(pick(P, 0.42), SCALP, 0.25)          # parting runs down to the nape
    if st == 'rocio':
        u = x * (1.0 + clamp((y + 15.0) / 8.0) * 0.5)    # gathered up into the ponytail
    elif st == 'paloma':
        u = x + (math.copysign(1.0, x) * clamp((y + 12.0) / 6.0) * 2.0)   # pulled out to the braids
    else:
        u = x
    v = strands(u, y, ctx, seed, sheen=-16.0, soft=0.85)
    v -= clamp((y + 10.0) / 8.0) * 0.14
    if st in ('paloma', 'anasofia') and abs(x) < 1.5:
        v -= 0.06
    return pick(P, v)


# hairline planes in front of the forehead: per style a bottom profile (hair rows per column) + shading
FRONT_PROFILE = {
    # 16 columns: x -8..8
    'paloma': [7, 6, 5, 4, 3, 3, 2, 1, 1, 2, 3, 3, 4, 5, 6, 7],
    'rocio': [5, 4, 3, 2, 2, 1, 1, 2, 2, 1, 1, 2, 2, 3, 4, 5],
    'anasofia': [5, 4, 3, 2, 2, 2, 2, 1, 1, 2, 2, 2, 2, 3, 4, 5],
    'lola': [8, 7, 7, 6, 6, 6, 5, 5, 4, 4, 3, 3, 2, 2, 3, 6],
    # 18 columns: x -9..9 (bob with curtains framing the cheeks)
    'mecha': [15, 15, 12, 7, 7, 8, 7, 7, 7, 8, 7, 7, 7, 8, 7, 12, 15, 15],
    # 17 columns: x -8.5..8.5 (long straight, centre parting, curtains beside the face)
    'ofelia': [17, 17, 13, 6, 4, 3, 2, 2, 1, 2, 2, 3, 4, 6, 13, 17, 17],
    # 20 columns: x -10..10 (curly fringe + side masses)
    'chela': [18, 18, 18, 14, 7, 6, 6, 5, 6, 5, 5, 6, 5, 6, 6, 7, 14, 18, 18, 18],
}


@G
def front_mat(ctx):
    c = ctx.cube
    st = c.style
    P = c.pal
    if ctx.face != 'front':
        return None
    prof = FRONT_PROFILE[st]
    k, j = ctx.i, ctx.j
    if j >= prof[k]:
        return None
    W = ctx.w
    mid = (W - 1) / 2.0
    seed = HAIRS.index(st) * 11 + 5
    tip = j == prof[k] - 1
    if st == 'chela':
        v = curls(ctx, k + 0.5, j + 0.3, seed) + 0.04
        if tip:
            v -= 0.06
        return pick(P, v)
    if st == 'mecha':
        u = k
        v = strands(u, j, ctx, seed, clump=2.0, sheen=2.0)
        if tip:
            v -= 0.1
        if k in (0, 1, W - 2, W - 1) and j > 6:
            v -= 0.06 + (j - 6) * 0.01
        return pick(P, v)
    if st == 'lola':
        u = k + j * 0.9                                 # swept toward her right
        v = strands(u, j, ctx, seed, clump=2.2, sheen=1.5)
        if tip:
            v -= 0.1
        return pick(P, v)
    if st == 'ofelia':
        if abs(k - mid) < 0.6 and j < 2:
            return mix(pick(P, 0.6), SCALP, 0.4)
        u = k + (j * 0.6 if k < mid else -j * 0.6)
        if k in (0, 1, 2, W - 3, W - 2, W - 1) and j > 5:
            u = k * 1.0
        v = strands(u, j, ctx, seed, clump=2.0, sheen=2.0)
        if tip:
            v -= 0.08
        return pick(P, v)
    # centre-parted / pulled-back hairlines
    if abs(k - mid) < 0.6 and j < 1 and st in ('paloma', 'anasofia'):
        return mix(pick(P, 0.6), SCALP, 0.45)
    u = k + (j * 0.9 if k < mid else -j * 0.9)
    v = strands(u, j, ctx, seed, clump=2.0, sheen=0.5)
    if tip:
        v -= 0.08
    return pick(P, v)


def braid_v(ctx, lx, ly, w):
    """Three-strand plait: lobes alternate left/right every 2 rows, lit top row, dark seam between lobes."""
    lobe = int(math.floor(ly / 2.0))
    in_lobe = ly - lobe * 2.0
    a = lx / max(1.0, w)
    left = lobe % 2 == 0
    v = 0.5 + face_light(ctx) * 0.8
    if (left and a > 0.66) or (not left and a < 0.34):
        v -= 0.14                                       # the crossing strand underneath
    if in_lobe < 1.0:
        v += 0.12
    else:
        v -= 0.03
    return v


@G
def hairbit_mat(ctx):
    """Braids, ponytails, pigtails, curl clumps, locks and the back curtain."""
    c = ctx.cube
    st = c.style
    P = c.pal
    t = tag(ctx)
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = c.size
    seed = HAIRS.index(st) * 13 + cseed(ctx) % 7
    if t == 'braid':
        if f in ('top', 'bottom'):
            return pick(P, 0.3)
        u = lx if f in ('front', 'back') else lz
        return pick(P, braid_v(ctx, u, ly, w if f in ('front', 'back') else d))
    if t == 'tuft':
        if f == 'top':
            return pick(P, 0.3)
        if f == 'bottom':
            return pick(P, 0.2)
        if ly > h - 1 and hash3(ctx.i, cseed(ctx), 0, 3) > 0.5:
            return None
        u = lx if f in ('front', 'back') else lz
        return pick(P, strands(u * 2, ly, ctx, seed, clump=1.5) - ly / h * 0.1)
    if t == 'clump':
        if f == 'bottom':
            return pick(P, 0.3)
        a = lx if f in ('front', 'back') else lz
        b = ly if f not in ('top', 'bottom') else lz
        return pick(P, curls(ctx, a + cseed(ctx) % 3, b + 0.7, seed))
    if t in ('tail', 'tail_tip', 'pigtail', 'pigtail_tip'):
        if f == 'top' and t in ('tail', 'pigtail'):
            return pick(P, 0.35)
        if f == 'bottom':
            if t.endswith('tip'):
                return pick(P, 0.18)
            return pick(P, 0.3)
        u = lx if f in ('front', 'back') else lz
        v = strands(u * 1.4 + (17 if f in ('west', 'east') else 0), ly, ctx, seed, clump=1.8, sheen=1.5)
        if t.endswith('tip'):
            if ly > h - 1 and hash3(ctx.i, cseed(ctx), 2, 3) > 0.45:
                return None                             # ragged ends
            v -= ly / h * 0.12
        return pick(P, v)
    if t in ('curtain', 'lock'):
        if f == 'top':
            return pick(P, 0.35)
        if f == 'bottom':
            return pick(P, 0.15)
        if ly > h - 1 and hash3(ctx.i, cseed(ctx), 2, 5) > 0.5:
            return None
        u = lx if f in ('front', 'back') else lz + 30
        v = strands(u, ly, ctx, seed, clump=2.2, sheen=3.0 if t == 'curtain' else 2.0)
        v -= clamp(ly / h) * 0.14
        if f == 'front' and t == 'curtain':
            v -= 0.18                                   # inner side (against her back)
        return pick(P, v)
    return pick(P, 0.4)


@G
def ribbon_mat(ctx):
    """Ribbons, scrunchie, elastics, headband and Lola's satin bow."""
    c = ctx.cube
    P = c.pal
    t = tag(ctx)
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = c.size
    v = 0.55 + face_light(ctx) * 1.0
    if t == 'wrap':
        v += 0.05 if ctx.j == 0 else -0.06
        return pick(P, v)
    if t == 'scrunchie':
        v += 0.1 if (ctx.i + ctx.j) % 2 == 0 else -0.08   # gathered fabric
        return pick(P, v)
    if t == 'elastic':
        return pick(P, v + (0.08 if ctx.j == 0 else -0.04))
    if t == 'ribbon_bow':
        if f != 'front':
            return None
        ch = RIBBON_BOW[ctx.j][ctx.i]
        if ch == '.':
            return None
        return pick(P, {'H': 0.86, 'h': 0.7, 'm': 0.52, 'd': 0.32, 'k': 0.2}[ch])
    if t == 'band':
        # Ofelia's headband: one cube cut into a hoop over the head
        if f == 'bottom':
            return None
        if f in ('front', 'back'):
            if not (ctx.j == 0 or ctx.i == 0 or ctx.i == ctx.w - 1):
                return None
            v -= 0.06 if f == 'back' else 0.0
        if f == 'top':
            v += 0.06 if ctx.j == 0 else 0.0
        if f in ('west', 'east') and ctx.i == 0:
            v += 0.06
        return pick(P, v)
    if t == 'big_loop':
        if f in ('front', 'back'):
            i = ctx.i if f == 'front' else ctx.w - 1 - ctx.i
            ii = i if c.side == 'r' else ctx.w - 1 - i
            ch = BIG_LOOP[ctx.j][ii]
            if ch == '.':
                return None
            v = {'H': 0.95, 'h': 0.84, 'M': 0.7, 'm': 0.66, 'd': 0.5, 'k': 0.36}[ch] + face_light(ctx) * 0.6
            if f == 'back':
                v -= 0.18
            return pick(P, v)
        if f in ('west', 'east'):
            far = (f == 'west') == (c.side == 'r')
            if not far:
                return None
            return pick(P, 0.55 - ly / h * 0.2)
        ii = ctx.i if c.side == 'r' else ctx.w - 1 - ctx.i
        rowc = BIG_LOOP[0] if f == 'top' else BIG_LOOP[-1]
        if rowc[ii] == '.':
            return None
        return pick(P, 0.72 if f == 'top' else 0.3)
    if t == 'big_knot':
        if f == 'front':
            v += 0.06 if ctx.j == 0 else (-0.14 if ctx.j == h - 1 else 0.0)
            if ctx.i == 1 and ctx.j == 1:
                v -= 0.08
        else:
            v -= 0.1
        return pick(P, v)
    if t == 'big_tail':
        if f != 'front':
            return None
        if ly > h - 1 and ctx.i == (1 if c.side == 'r' else 0):
            return None
        v += 0.2 - ly / h * 0.18
        if ctx.i == 0:
            v += 0.06
        return pick(P, v)
    return pick(P, v)


RIBBON_BOW = [
    # 6 x 3, a small sky-blue bow tied round the braid end
    "Hh.hH.",
    "hmdmhH",
    "dk.kdm",
]
RIBBON_BOW = [
    "Hh..hH",
    "hmkkmh",
    "dk..kd",
]

BIG_LOOP = [
    # 6 x 6, index 0 = outer rounded end, 5 = pinched at the knot
    ".HHHh.",
    "HHhhhh",
    "Hhhmhm",
    "hhmmmd",
    "hmmdd.",
    ".mdd..",
]


# ------------------------------------------------------------------ module contract
DEFAULT_MAT = smock_mat
FOCUS = 'head'


class AlumnaModel(Model):
    """Exports every hair group to Java; the preview / gallery JSON shows only the selected hairstyle."""
    show = SHOW

    def to_json(self):
        d = super().to_json()
        if self.show == 'all':
            return d
        hidden = set()
        for b in self.bones():
            if b.name.startswith('hair_') and b.name != 'hair_' + self.show:
                for sub in b.walk():
                    hidden.add(sub.name)
        for bd in d['bones']:
            if bd['name'] in hidden:
                bd['cubes'] = []
        return d


def build(show=None):
    r = Rig()

    def box(bone_, frm, size, mat=None, inflate=0.0, decals=None, name=None, side='', **attrs):
        c = r.box(bone_, frm, size, mat=mat, inflate=inflate, decals=decals)
        c.a0 = tuple(float(v) for v in frm)
        c.name = name
        c.side = side
        for k, v in attrs.items():
            setattr(c, k, v)
        return c

    bone = r.bone

    # ---------------- body (root at the waist): smock chest, skirt core
    bone('body', (0, 9.0, 0), mat=smock_mat)
    box('body', (-6, 0, -3.5), (12, 12, 7), name='torso')
    box('body', (-6.5, 5.5, -4), (13, 8, 8), name='core')

    # ---------------- skirt: four flared, box-pleated panels (front placket + pockets, back pleat + half-belt)
    bone('skirt_front', (0, 5.5, -3.7), parent='body', rot=(-13, 0, 0), mat=smock_mat)
    box('skirt_front', (-7, 5.5, -4.7), (14, 9, 1), name='panel', which='front')
    bone('skirt_back', (0, 5.5, 3.7), parent='body', rot=(13, 0, 0), mat=smock_mat)
    box('skirt_back', (-7, 5.5, 3.7), (14, 9, 1), name='panel', which='back')
    box('skirt_back', (-4, 6.2, 4.7), (8, 2, 1), name='belt')
    bone('skirt_right', (-6.7, 5.5, 0), parent='body', rot=(0, 0, 12), mat=smock_mat)
    box('skirt_right', (-7.2, 5.5, -4.5), (1, 9, 9), name='panel', which='right')
    bone('skirt_left', (6.7, 5.5, 0), parent='body', rot=(0, 0, -12), mat=smock_mat)
    box('skirt_left', (6.2, 5.5, -4.5), (1, 9, 9), name='panel', which='left')

    # ---------------- collar (two planes) + navy bow
    bone('collar', (0, -0.2, -3.6), parent='body', rot=(-12, 0, 0), mat=smock_mat)
    box('collar', (-7, -0.2, -3.7), (7, 4, 0), name='collar', side='r')
    box('collar', (0, -0.2, -3.75), (7, 4, 0), name='collar', side='l')
    bone('bow', (0, 1.4, -4.0), parent='collar', mat=bow_mat)
    box('bow', (-1, 0.4, -4.4), (2, 2, 1), name='knot')
    box('bow', (-4, -0.6, -4.15), (3, 4, 1), name='loop', side='r')
    box('bow', (1, -0.6, -4.15), (3, 4, 1), name='loop', side='l')
    box('bow', (-2.0, 2.2, -4.0), (2, 4, 0), name='tail', side='r')
    box('bow', (0.0, 2.2, -4.05), (2, 4, 0), name='tail', side='l')

    # ---------------- legs: thigh (under the skirt), knee band + navy knee sock, cuff, Mary-Jane
    for side, sx in (('right', -1), ('left', 1)):
        lb, sb, fb = f'{side}_leg', f'{side}_shin', f'{side}_shoe'
        cx = 2.4 * sx
        bone(lb, (cx, 9.5, 0), parent='body', mat=skin_mat)
        box(lb, (cx - 2, 9.5, -2), (4, 6, 4), name='thigh')
        bone(sb, (cx, 15.5, 0), parent=lb, mat=knee_mat)
        box(sb, (cx - 2, 15.5, -2), (4, 6, 4), name='shin')
        box(sb, (cx - 2, 17.5, -2), (4, 1, 4), mat=cuff_mat, name='cuff', inflate=0.3)
        bone(fb, (cx, 21.0, 0), parent=sb, mat=shoe_mat)
        box(fb, (cx - 2.5, 21.0, -4.5), (5, 3, 7), name='shoe')

    # ---------------- arms: thin sleeves, cuffs, long pale hands (palm, thumb, grouped fingers, index)
    for side, sx in (('right', -1), ('left', 1)):
        ab, fb, hb = f'{side}_arm', f'{side}_forearm', f'{side}_hand'
        ax = 7.5 * sx
        bone(ab, (ax, 1.5, 0), parent='body', rot=(0, 0, -14 * sx), mat=smock_mat)
        box(ab, (ax - 1.5, 0, -1.5), (3, 7, 3), name='sleeve', inflate=0.3)
        bone(fb, (ax, 6.5, 0), parent=ab, rot=(-6, 0, 4 * sx), mat=smock_mat)
        box(fb, (ax - 1.5, 6.5, -1.5), (3, 4, 3), name='forearm', inflate=0.15)
        box(fb, (ax - 1.5, 9.6, -1.5), (3, 1, 3), name='cuff', inflate=0.4)
        bone(hb, (ax, 10.5, 0), parent=fb, rot=(0, 0, 0), mat=hand_mat)
        box(hb, (ax - 1, 10.5, -1.5), (2, 3, 3), name='palm')
        box(hb, (ax - 0.5 - 0.5 * sx, 11.2, -2.4), (1, 2, 1), name='thumb')
        bone(f'{side}_fingers', (ax, 13.5, 0.5), parent=hb, rot=(6, 0, 0), mat=hand_mat)
        box(f'{side}_fingers', (ax - 0.5, 13.5, -0.5), (1, 4, 2), name='finger')
        bone(f'{side}_index', (ax, 13.5, -1.0), parent=hb, rot=(-4, 0, 0), mat=hand_mat)
        box(f'{side}_index', (ax - 0.5, 13.5, -1.5), (1, 4, 1), name='index')

    # ---------------- neck + head: skin plate with real socket holes over the skull, ears
    bone('neck', (0, 0.0, 0), parent='body', mat=skin_mat)
    box('neck', (-2, -4.5, -2), (4, 5, 4), name='neck')
    bone('head', (0, -4.0, 0), parent='neck', rot=(4, 0, -6), mat=skull_mat)
    box('head', (-7, -19, -7), (14, 15, 1), mat=plate_mat, name='plate')
    box('head', (-7, -19, -6), (14, 15, 12), mat=skull_mat, name='skull', decals={'eyes:front': at(EYE_GLOW)})
    box('head', (-8, -11, -1), (1, 3, 2), mat=skin_mat, name='ear')
    box('head', (7, -11, -1), (1, 3, 2), mat=skin_mat, name='ear')

    # the round singing "O": parked inside the skull, pushed out by pose 'freed'
    bone('jaw', (0, -6.0, -5.0), parent='head', mat=jaw_mat)
    box('jaw', (-2, -8, -5.4), (4, 4, 1), name='mouth')

    # ---------------- hair groups (exactly one visible per girl)
    HC = (0, -12.0, 0)

    def shell(style, P, frm, size):
        box('hair_' + style, frm, size, mat=shell_mat, name='shell', style=style, pal=P)

    def front(style, P, frm, size):
        box('hair_' + style, frm, size, mat=front_mat, name='front', style=style, pal=P)

    # Paloma: centre parting, two long plaits over the shoulders with sky-blue bows
    P = BROWN
    bone('hair_paloma', HC, parent='head', mat=shell_mat)
    shell('paloma', P, (-8, -20, -8), (16, 14, 15))
    front('paloma', P, (-8, -20, -8.05), (16, 7, 0))
    for side, sx in (('right', -1), ('left', 1)):
        b1, b2 = f'paloma_braid_{side}', f'paloma_braid_{side}_tip'
        px = 6.8 * sx
        bone(b1, (px, -7.0, 3.0), parent='hair_paloma', rot=(-58, 0, 4 * sx), mat=hairbit_mat)
        box(b1, (px - 1.5, -7.5, 1.5), (3, 9, 3), name='braid', style='paloma', pal=P)
        bone(b2, (px, 1.5, 3.0), parent=b1, rot=(52, 0, -2 * sx), mat=hairbit_mat)
        box(b2, (px - 1.5, 1.3, 1.5), (3, 6, 3), name='braid', style='paloma', pal=P)
        box(b2, (px - 1.5, 6.8, 1.5), (3, 1, 3), mat=ribbon_mat, name='wrap', inflate=0.35, style='paloma',
            pal=CELESTE)
        box(b2, (px - 3, 6.2, 1.1), (6, 3, 0), mat=ribbon_mat, name='ribbon_bow', style='paloma', pal=CELESTE)
        box(b2, (px - 1, 7.6, 2.0), (2, 3, 2), name='tuft', style='paloma', pal=P)

    # Mecha: black bob, blunt bangs, curtains framing the cheeks
    P = BLACK
    bone('hair_mecha', HC, parent='head', mat=shell_mat)
    shell('mecha', P, (-9, -20, -8), (18, 15, 16))
    front('mecha', P, (-9, -20, -8.05), (18, 15, 0))

    # Rocio: combed back into a high ponytail with a maroon scrunchie
    P = BROWN_L
    bone('hair_rocio', HC, parent='head', mat=shell_mat)
    shell('rocio', P, (-8, -20, -8), (16, 13, 15))
    front('rocio', P, (-8, -20, -8.05), (16, 5, 0))
    box('hair_rocio', (-2, -17.5, 6.6), (4, 3, 2), mat=ribbon_mat, name='scrunchie', inflate=0.3, style='rocio',
        pal=MAROON)
    bone('rocio_tail', (0, -16.0, 8.0), parent='hair_rocio', rot=(62, 0, 0), mat=hairbit_mat)
    box('rocio_tail', (-2, -16.0, 6.5), (4, 7, 3), name='tail', style='rocio', pal=P)
    bone('rocio_tail_tip', (0, -9.2, 8.0), parent='rocio_tail', rot=(-52, 0, 0), mat=hairbit_mat)
    box('rocio_tail_tip', (-1.5, -9.5, 6.8), (3, 10, 3), name='tail_tip', style='rocio', pal=P)

    # Chela: a big cloud of tight curls
    P = CHESTNUT
    bone('hair_chela', HC, parent='head', mat=shell_mat)
    shell('chela', P, (-10, -22, -9), (20, 19, 18))
    front('chela', P, (-10, -22, -9.05), (20, 18, 0))
    for (fx, fy, fz), (sw, sh, sd) in (((-12, -18, -5), (2, 5, 6)), ((10, -17, -4), (2, 6, 6)),
                                       ((-12, -10, -2), (2, 5, 6)), ((10, -9, -1), (2, 5, 6)),
                                       ((-5, -24, -4), (8, 2, 7)), ((-6, -14, 9), (12, 7, 1)),
                                       ((-11, -4, -3), (3, 4, 5)), ((8, -4, -2), (3, 4, 5)),
                                       ((-9, -23, 2), (5, 2, 5)), ((4, -23, -6), (5, 2, 5))):
        box('hair_chela', (fx, fy, fz), (sw, sh, sd), mat=hairbit_mat, name='clump', style='chela', pal=P)

    # Ofelia: long dead-straight blue-black hair, headband, locks over the shoulders, back curtain
    P = BLUEBLACK
    bone('hair_ofelia', HC, parent='head', mat=shell_mat)
    shell('ofelia', P, (-8.5, -20, -8), (17, 17, 15))
    front('ofelia', P, (-8.5, -20, -8.05), (17, 17, 0))
    box('hair_ofelia', (-9, -21, -6.0), (18, 7, 2), mat=ribbon_mat, name='band', style='ofelia', pal=SATIN)
    box('hair_ofelia', (-8.5, -6, -6.5), (3, 13, 2), mat=hairbit_mat, name='lock', style='ofelia', pal=P)
    box('hair_ofelia', (5.5, -6, -6.5), (3, 13, 2), mat=hairbit_mat, name='lock', style='ofelia', pal=P)
    bone('ofelia_curtain', (0, -6.0, 6.0), parent='hair_ofelia', rot=(8, 0, 0), mat=hairbit_mat)
    box('ofelia_curtain', (-7.5, -6.0, 5.0), (15, 17, 2), name='curtain', style='ofelia', pal=P)

    # Ana Sofia: centre parting, two high pigtails with red elastics
    P = BROWN
    bone('hair_anasofia', HC, parent='head', mat=shell_mat)
    shell('anasofia', P, (-8, -20, -8), (16, 13, 15))
    front('anasofia', P, (-8, -20, -8.05), (16, 5, 0))
    for side, sx in (('right', -1), ('left', 1)):
        t1, t2 = f'anasofia_tail_{side}', f'anasofia_tail_{side}_tip'
        px = 8.2 * sx
        box('hair_anasofia', (px - 1, -18.0, -0.5), (2, 3, 3), mat=ribbon_mat, name='elastic', inflate=0.2,
            style='anasofia', pal=RED)
        bone(t1, (px, -16.5, 1.0), parent='hair_anasofia', rot=(0, 0, -100 * sx), mat=hairbit_mat)
        box(t1, (px - 1.5, -16.5, -0.5), (3, 6, 3), name='pigtail', style='anasofia', pal=P)
        bone(t2, (px, -11.0, 1.0), parent=t1, rot=(0, 0, 58 * sx), mat=hairbit_mat)
        box(t2, (px - 1.5, -11.3, -0.5), (3, 7, 3), name='pigtail_tip', style='anasofia', pal=P)

    # Lola: black pixie cut, side-swept fringe, huge white satin bow on the top-left
    P = BLACK
    bone('hair_lola', HC, parent='head', mat=shell_mat)
    shell('lola', P, (-8, -20, -8), (16, 12, 15))
    front('lola', P, (-8, -20, -8.05), (16, 9, 0))
    bone('lola_bow', (4.5, -20.5, -8.0), parent='hair_lola', rot=(-6, 0, -14), mat=ribbon_mat)
    box('lola_bow', (3.0, -22.0, -9.6), (3, 3, 3), name='big_knot', style='lola', pal=SATIN)
    box('lola_bow', (-3.0, -23.5, -9.0), (6, 6, 2), name='big_loop', side='r', style='lola', pal=SATIN)
    box('lola_bow', (6.0, -23.5, -9.0), (6, 6, 2), name='big_loop', side='l', style='lola', pal=SATIN)
    box('lola_bow', (2.4, -19.4, -9.3), (2, 4, 0), name='big_tail', side='r', style='lola', pal=SATIN)
    box('lola_bow', (4.6, -19.4, -9.4), (2, 5, 0), name='big_tail', side='l', style='lola', pal=SATIN)

    m = AlumnaModel('alumna', 256, 128, r.roots)
    m.scale = 0.5
    m.render_type = 'entityTranslucent'
    if show is not None:
        m.show = show
    return m


POSES = {
    # hands joined in front of the skirt, head lowered a little: the obedient pupil
    'stand': {'head': (0.12, 0, 0.04, 0, 0, 0),
              'right_arm': (-0.52, -0.27, -0.25, 0, 0, 0), 'right_forearm': (-0.25, 0, -0.3, 0, 0, 0),
              'right_hand': (0.35, 0.5, 0.17, 0, 0, 0),
              'left_arm': (-0.52, 0.27, 0.25, 0, 0, 0), 'left_forearm': (-0.25, 0, 0.3, 0, 0, 0),
              'left_hand': (0.35, -0.5, -0.17, 0, 0, 0)},
    # choir: chin up, prayer hands at the chest
    'sing': {'neck': (-0.08, 0, 0, 0, 0, 0), 'head': (-0.28, 0, 0.06, 0, 0, 0),
             'right_arm': (-0.6, -0.05, -0.69, 0, 0, 0), 'right_forearm': (-0.62, 0, -0.66, 0, 0, 0),
             'right_hand': (-0.21, 0.98, -1.13, 0, 0, 0),
             'left_arm': (-0.6, 0.05, 0.69, 0, 0, 0), 'left_forearm': (-0.62, 0, 0.66, 0, 0, 0),
             'left_hand': (-0.21, -0.98, 1.13, 0, 0, 0)},
    # at the desk: knees at 90 degrees, hands folded on the desk top, head tilted, staring
    'sit_desk': {'body': (0, 0, 0, 0, 6.0, 0),
                 'right_leg': (-1.57, 0.08, 0, 0, 0, 0), 'right_shin': (1.57, 0, 0, 0, 0, 0),
                 'left_leg': (-1.57, -0.08, 0, 0, 0, 0), 'left_shin': (1.57, 0, 0, 0, 0, 0),
                 'skirt_front': (-1.4, 0, 0, 0, 0.3, 2.6), 'skirt_back': (0.3, 0, 0, 0, 0, 0),
                 'skirt_right': (0, 0, 0.25, 0, 0, 0), 'skirt_left': (0, 0, -0.25, 0, 0, 0),
                 'right_arm': (-0.59, 0.15, -0.38, 0, 0, 0), 'right_forearm': (-0.52, 0, -0.76, 0, 0, 0),
                 'right_hand': (0.45, 0.06, -0.34, 0, 0, 0),
                 'left_arm': (-0.59, -0.15, 0.38, 0, 0, 0), 'left_forearm': (-0.52, 0, 0.76, 0, 0, 0),
                 'left_hand': (0.45, -0.06, 0.34, 0, 0, 0),
                 'head': (0.05, 0, 0.18, 0, 0, 0)},
    # punished: forehead against the wall, shoulders dropped, arms hanging dead
    'face_wall': {'body': (0.1, 0, 0, 0, 0, -0.5), 'neck': (0.2, 0, 0, 0, 0, 0), 'head': (0.42, 0, 0.08, 0, 0, 0),
                  'right_leg': (-0.1, 0, 0, 0, 0, 0), 'left_leg': (-0.1, 0, 0, 0, 0, 0),
                  'right_arm': (-0.1, 0, -0.16, 0, 1.0, 0), 'left_arm': (-0.1, 0, 0.16, 0, 1.0, 0),
                  'right_forearm': (-0.05, 0, 0, 0, 0, 0), 'left_forearm': (-0.05, 0, 0, 0, 0, 0),
                  'right_hand': (0.1, 0, 0.1, 0, 0, 0), 'left_hand': (0.1, 0, -0.1, 0, 0, 0)},
    'point': {'head': (0.05, 0, 0.3, 0, 0, 0),
              'right_arm': (-1.6, 0, -0.2, 0, 0, 0), 'right_forearm': (0.05, 0, 0, 0, 0, 0),
              'right_fingers': (0, 0, -1.4, 0, 0, 0)},
    'cover_ears': {'body': (0.25, 0, 0, 0, 2.5, 0), 'right_leg': (-0.7, 0, 0, 0, 0, 0), 'left_leg': (-0.7, 0, 0, 0, 0, 0),
                   'right_shin': (1.2, 0, 0, 0, 0, 0), 'left_shin': (1.2, 0, 0, 0, 0, 0),
                   'right_shoe': (-0.25, 0, 0, 0, 0, 0), 'left_shoe': (-0.25, 0, 0, 0, 0, 0),
                   'neck': (0.1, 0, 0, 0, 0, 0), 'head': (0.2, 0, 0, 0, 0, 0),
                   'right_arm': (-0.38, -0.23, 2.58, 0, 0, 0), 'right_forearm': (0.71, 0, 0.61, 0, 0, 0),
                   'right_hand': (0.18, -0.39, -0.35, 0, 0, 0),
                   'left_arm': (-0.38, 0.23, -2.58, 0, 0, 0), 'left_forearm': (0.71, 0, -0.61, 0, 0, 0),
                   'left_hand': (0.18, 0.39, 0.35, 0, 0, 0)},
    'head_180': {'neck': (0, 0.5, 0, 0, 0, 0), 'head': (0, 2.64, 0.12, 0, 0, 0)},
    'run': {'body': (0.2, 0, 0, 0, -0.5, 0), 'head': (-0.15, 0, 0, 0, 0, 0),
            'right_leg': (-0.9, 0, 0, 0, 0, 0), 'right_shin': (0.9, 0, 0, 0, 0, 0),
            'left_leg': (0.6, 0, 0, 0, 0, 0), 'left_shin': (1.2, 0, 0, 0, 0, 0),
            'right_arm': (0.8, 0, 0, 0, 0, 0), 'right_forearm': (-0.6, 0, 0, 0, 0, 0),
            'left_arm': (-0.9, 0, 0, 0, 0, 0), 'left_forearm': (-0.8, 0, 0, 0, 0, 0),
            'skirt_back': (0.25, 0, 0, 0, 0, 0), 'skirt_front': (-0.1, 0, 0, 0, 0, 0),
            'paloma_braid_right': (0.5, 0, 0, 0, 0, 0), 'paloma_braid_left': (0.6, 0, 0, 0, 0, 0),
            'rocio_tail': (0.4, 0, 0, 0, 0, 0), 'ofelia_curtain': (0.35, 0, 0, 0, 0, 0)},
    # leaning out sideways from behind a doorframe (frame edge on her left, in front of her chest)
    'peek': {'body': (0, 0, 0.38, 0, 0, 0), 'right_leg': (0, 0, -0.38, 0, 0, 0), 'left_leg': (0, 0, -0.38, 0, 0, 0),
             'head': (0.05, 0, 0.32, 0, 0, 0),
             'left_arm': (-1.15, 0.4, 0.82, 0, 0, 0), 'left_forearm': (-0.56, 0, 1.14, 0, 0, 0),
             'left_hand': (0.29, 0, -0.43, 0, 0, 0), 'left_fingers': (0, 0, 0.9, 0, 0, 0),
             'left_index': (0, 0, 0.7, 0, 0, 0),
             'right_arm': (0.05, 0, -0.2, 0, 0, 0)},
    'ronda': {'right_arm': (-0.2, 0, 0.9, 0, 0, 0), 'left_arm': (-0.2, 0, -0.9, 0, 0, 0)},
    'hop': {'body': (0, 0, 0, 0, -1.5, 0), 'left_leg': (-0.5, 0, 0, 0, 0, 0), 'left_shin': (1.6, 0, 0, 0, 0, 0),
            'right_arm': (0, 0, 0.6, 0, 0, 0), 'left_arm': (0, 0, -0.6, 0, 0, 0)},
    'wave': {'right_arm': (-0.76, 1.28, 1.69, 0, 0, 0), 'right_forearm': (-0.02, 0, 0.11, 0, 0, 0),
             'right_hand': (0.05, -0.44, 0.15, 0, 0, 0), 'head': (0, 0, -0.15, 0, 0, 0)},
    'freed': {'head': (-0.1, 0, 0, 0, 0, 0), 'jaw': (0, 0, 0, 0, 0, -2.0)},
}

ANIM_NOTES = """Las Alumnas del Coro -- animation notes.  Units: radians, offsets in model texels (2x density inside
scale_root: 2 texels = 1 vanilla pixel).  t = ageInTicks, s = walk speed 0..1.  Every POSES entry is ADDED to the rest
pose; blend between poses over 4-6 ticks unless a note says SNAP (1-2 ticks).

Variants and toggles (synced data: variant 0..6, freed, pose)
* Exactly one hair group is visible: variant 0 hair_paloma, 1 hair_mecha, 2 hair_rocio, 3 hair_chela, 4 hair_ofelia,
  5 hair_anasofia, 6 hair_lola.  Every frame: for each part in group("hair_") set visible = (name == HAIRS[variant])
  (hiding a group hides its child bones too).  The order is the same as the HAIRS list in ent_alumna.py.
* jaw.visible = freed.  When freed, also apply POSE 'freed' (it pushes the "O" mouth 2 texels forward out of the
  skull).  Never show the jaw before Laudes; the mouthless face IS the character.
* Render type entityTranslucent (texture alpha 180-232).  Camera flash: render with alpha forced to 255 for the flash
  frames (they look solid) and set freed = true for that frame only (in the photo they have mouths).
* Emissive layer 'eyes': only the two 1-px socket glints (pale cyan).  Flicker their alpha 0.6-1.0 while a girl is
  singing backwards; switch them off for 3 ticks right before a head_180 snap.

Movement style: they are dead children, not zombies.  Idle is perfectly still except breathing-free, tiny "settle"
twitches; anything uncanny happens in SNAPS (1-2 ticks) while the player is not looking, then freezes.  Walking is a
light, too-even glide: the legs walk but the body has no bob at all (dy = 0), the arms do not swing.

Bones
* body (root, pivot at the waist): whole girl.  Idle: still; every 6-10 s a single 0.03 zRot settle.  Walk: no bob, no
  sway (that evenness is the creepy part).  Run: pose 'run' with a 0.08 xRot bounce on each footfall.
* skirt_front, skirt_back, skirt_right, skirt_left: the four box-pleated panels of the guardapolvo, hinged at the waist.
  Idle: ripple("skirt_", t, 0.05, 1.4, 0.015, 0.01, 0).  Walk/run: the panel on the side of the forward leg opens
  -0.12 * s, skirt_back flares +0.25 in 'run'.  skirt_back carries the buttoned half-belt.
* collar: the two Peter Pan collar planes (static, rest xRot -12 deg so they stand off the chest).  No animation.
* bow: the navy school bow at the throat (child of collar).  Secondary: zRot spring-lagged from body/head motion
  (+-0.08), xRot -0.15 in 'run'.
* right_leg / left_leg: thighs (hip joint).  Walk: xRot = +-sin(walk) * 0.5 * s.  Sit/crouch/hop: pose values.
* right_shin / left_shin: knee joint (pale knee band + navy knee sock + cuff).  Walk: xRot = max(0, sin(walk + 1.2))
  * 0.6 * s (bend on the back-swing only).  sit_desk +1.57.
* right_shoe / left_shoe: ankle (black patent Mary-Janes).  Keep the sole flat: xRot = -(leg + shin) * 0.4 while
  walking; cover_ears -0.25.
* right_arm / left_arm: shoulders (thin white sleeves, rest angled 14 deg out over the skirt).  Idle: hanging dead
  still; no swing when walking.  Run: +-0.8 counter to the legs.
* right_forearm / left_forearm: elbows (sleeve + cuff).  Follow pose values only.
* right_hand / left_hand: wrists (long pale palm + thumb).  Idle: a 0.04 zRot tremor on one hand every few seconds.
* right_fingers / left_fingers: the three grouped long fingers.  zRot curls them into the palm (right -1.4, left
  +1.4): fist for 'point', grip on the frame for 'peek'.  Idle: slow 0.1 curl/uncurl, never both hands together.
* right_index / left_index: the index finger, separate so 'point' can keep it straight while the others curl.
  In 'point' add a slow beckoning curl xRot 0..-0.5 on the right index after the pose has held 2 s.
* neck: takes 30% of the head look (yaw/pitch) and 0.5 of the yaw in 'head_180'.
* head: 70% of the head look; rest pose already tilted 6 deg toward her right shoulder and nodded 4 deg.
  Idle: hold, then every 5-12 s SNAP a +-0.25 zRot tilt in 2 ticks and hold it.  When the player comes within 3 blocks:
  SNAP 'head_180' (neck + head yaw = pi in 2 ticks, overshoot 0.1 and settle), giggle, then dissolve.
* jaw: the round singing "O" (lips ring + black mouth).  Hidden (visible = false) unless freed; pose 'freed' pushes it
  out with dz -2.  While freed and singing: dy oscillation 0..0.4 on the beat, never open wider.
* hair_paloma: centre-parted brown hair + braids.  paloma_braid_right / paloma_braid_left: the upper plaits (hinged
  behind the ears, swung forward over the shoulders); paloma_braid_right_tip / paloma_braid_left_tip: lower plaits
  with the sky-blue ribbon bows and brush ends.  Pendulums: xRot/zRot spring-lag the head and body by 3-4 ticks
  (amplitude 0.1 idle, 0.5 back in 'run'); the tips lag the uppers by 2 more ticks.
* hair_mecha: black bob with bangs (shell + bangs plane).  Rigid; no bones to animate.
* hair_rocio: combed-back hair + scrunchie.  rocio_tail (upper ponytail, sticks out behind) and rocio_tail_tip
  (hanging end): pendulum chain, +0.4 xRot in 'run', bounce 0.15 on each footfall, side swing zRot +-0.2 when the
  head snaps.
* hair_chela: the curly cloud (shell, fringe, ringlet clumps).  Rigid; on footfalls a 0.3 texel dy squash is enough.
* hair_ofelia: long straight blue-black hair, white headband and the two locks over the shoulders (rigid with the
  head).  ofelia_curtain: the waist-long back curtain; lags the head (xRot spring) and lifts +0.35 in 'run'.  In
  'face_wall' it hangs (counter-rotate -0.3 so it falls vertical instead of following the bowed head).
* hair_anasofia: centre parting + red elastics.  anasofia_tail_right / anasofia_tail_left: the high pigtails (stick
  out sideways); anasofia_tail_right_tip / anasofia_tail_left_tip: drooping ends.  Bounce zRot +-0.25 on every hop
  in 'hop' and on footfalls, opposite phase left/right.
* hair_lola: black pixie cut with a side-swept fringe.  lola_bow: the huge white satin bow; small spring wobble
  (zRot +-0.06) after head snaps.

Poses
* stand: hands joined in front of the skirt, head a little down.  Default pose in classrooms, refectory, locutorio.
* sing: chin up, prayer hands at the chest.  Choir (Completas, Maitines).  Combine with 'freed' at Laudes.
* sit_desk: knees at 90 deg, hands folded on the desk, head tilted.  body dy +6 puts the soles on the floor of the
  same block (stool height ~0.3 blocks); raise the entity 0.2 blocks for the classroom benches.  The front skirt
  panel is laid over the thighs.
* face_wall: punished pupil: forehead on the wall, neck and head bowed, shoulders dropped 1 texel, arms hanging
  dead.  Place her 0.25 blocks from the wall.  Cripta at the Hora Muerta (before the 180 + "CORRE").
* point: the right arm straight at the player, index out, other fingers curled, head tilted.  Ronda beat ("...con
  esta SI") - all girls SNAP into it on the same tick.
* cover_ears: crouched, both hands flat over the ears, head down.  Warning when Sor Agonia hunts within 16 blocks
  ("shh, viene"), then dissolve.
* head_180: the thumbnail shot.  neck + head yaw sum to pi; SNAP all girls on the same tick when the flashlight hits
  the choir loft.  Works from any base pose (stand, sing, face_wall); body stays still.
* run: Hora Muerta, running ahead lighting candles; braids/ponytail/curtain fly back.
* peek: leaning sideways (body zRot +0.38, legs counter-rotated so the feet stay planted) from behind a doorframe on
  her left, left hand gripping the frame at chest height, head tilted further.  Corridors.
* ronda: arms out to the sides to hold hands in the ring (claustro).  Rotate the ring, not the girls.
* hop: rayuela hop (Paloma): one leg up behind, arms out for balance, body dy -1.5 at the top of the hop.
* wave: the right arm raised beside the head (Laudes goodbye); drive right_forearm zRot +-0.35 at 0.25 rad/tick.
* freed: the "O" mouth pushed out of the skull + chin up.  Only after the final chorus.
"""
