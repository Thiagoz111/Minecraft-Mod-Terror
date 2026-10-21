"""Las Alumnas del Coro -- the seven mouthless choir girls of the Colegio Santa Ines, 1984 (DEAD LINE).

Authored at 2x texel density (model.scale = 0.5).  +Y down, ground y = 24, faces -Z, right_* on -X.
Centred on x = 0, z = 0.  Real height 1.35 blocks: ground y = 24, top of the skull y = -19 (hair adds 1-3).

Design
------
Silhouette: a little girl whose head is a third of her height (14 x 15 x 13 on a 4-texel neck, wider than her
narrow 12-texel chest) and whose arms are too long: thin sleeves angled a little out and forward, ending in cold
lavender-grey spidery hands (palm + thumb + three splayed 1x5 fingers with 1-texel gaps, palms turned back) whose
dirty fingertips hang 3-4 texels below the hem, down to the sock cuffs.  Argentine school uniform: a starched white
guardapolvo (smock-coat) with a yoke and 6.5 texels of chest above the waist seam, an A-line box-pleated skirt of
four flared 16 x 10 panels (front panel with a button placket and two patch pockets, one blotted with ink; back
panel with an inverted box pleat under a buttoned half-belt; the top corners of the front/back panels are cut so
the waist is 14 wide and the hem 16), a white Peter Pan collar (two planes) and the navy school bow at the throat
(knot, two pinched loops, two notched tails).  A pale knee band (with a plaster / bruise) between hem and the navy
ribbed knee socks with a turned-down cuff; black patent Mary-Janes with one clear strap across the instep, the
silver buckle on the outer side, a single specular texel on the toe and a dark sole edge.
She is a ghost: every texel is translucent (alpha ~228 on the head, ~214 at the waist, dissolving from the hem down
into a cold mist: ~200 at the knee, ~158 at the soles, tinted toward mist blue) and the vertical silhouette edges of
the smock, sleeves and hair carry a 1-texel cold cyan rim.  Faces that are always buried (torso below the waist
seam, every face of the waist band except its dark underside, the skull top, the shin tops) are left transparent so
nothing ghosts through in entityTranslucent (no face sorting inside a model).

Face (front of a 1-texel skin plate, 14 x 15, read at 64 px): a big pale doll forehead; faint brows whose inner
ends are raised (worried); upper-lid creases; two 4x4 sockets that are REAL holes in the plate: through them you
see the skull front one texel deeper, painted from a dark grey ring to black with a 1-px glint that glows pale
cyan (emissive 'eyes' layer); purple-grey dark circles; a lit nose bridge and a 1-px nose shadow; doll blush 2x1;
and NO MOUTH: a faint philtrum (two 1-px soft shades) runs down from the nose into nothing, then one 6-px healed-over
seam (SKIN[4]-ish, its ends dissolving - never dark end points) with a 1-px lit lip of fused skin under it: it reads
as skin that grew shut, not as lips, from the 64-px full body down to the 512-px portrait.  In profile the skull
side carries a lit cheekbone, a temple hollow and a mandible edge with shadow under it.  The 'jaw' bone holds the
round singing "O" (a 4x4 zero-thickness plane: lips ring, black mouth); it is parked inside the skull and pose
'freed' slides it onto the face at z = -7.1 (0.1 in front of the plate: never z-fights) when they get their voices
back.

Head from behind (the choir-loft and crypt angle, the thumbnail before the 180 turn): every hair shell is two stepped
boxes - the back block 0.5 narrower each side (so it is never flush with the skull's sides, x = +-7) and 1 lower -
and the step, the back face, the back block's top and a ragged-tips plane are all painted by one function with one
seed, so strands and the sheen arc run on unbroken: no ledges, no outlines, no slab - one rounded hair mass whose
lower edge breaks into uneven 1-3 texel strand tips (short nape wisps on the pulled-back styles, around a narrow
4-6 px bare nape patch).  The shared skull is skin wherever any pulled-back style leaves its side bare (grown 1 texel
for the recess under the shell), and a mid hair value where every style covers it: no black slit between cheek and
hair from any angle.  Every hairstyle has zero coplanar painted faces in the rest pose (checked face by face).

Hair (seven bone groups, exactly one visible per girl; Java toggles ModelPart.visible):
  hair_paloma   dark brown, centre parting, hair pulled behind the ears into two braid roots (visible from behind)
                and two long braids that fall over the shoulders onto the chest, faded sky-blue ribbon bows and brush
                ends (the leader).
  hair_mecha    black bob with heavy blunt bangs down to the brows, hair curtains framing the cheeks.
  hair_rocio    brown, combed back (every strand converging on the scrunchie) into a ponytail gathered at the back of
                the crown by a maroon scrunchie; the tail leaves it at ~36 deg and falls in one tapered lock (4 -> 3 ->
                2 wide, ragged tip) close behind the head; two loose strands at the temples.
  hair_chela    chestnut, a big cloud of corkscrew ringlets (6-texel S/Z ringlet glyph: 2-px bright crest, dark core,
                four values only - reads as spirals, not static, at full-body distance; round coil heads on top),
                ringlet clumps on the sides/crown/back and four ringlet tubes turned 45 deg on the vertical corners so
                the outline is bumpy and round; an even curly fringe (no forehead peeking through).
  hair_ofelia   blue-black, long and dead straight: centre parting, curtains beside the face, two locks over the
                shoulders, a waist-long back curtain, and a deep maroon velvet Alice band across the crown 2 texels
                behind the hairline (never wider than the head), its ends running down behind the ears.
  hair_anasofia dark brown, centre parting, two high pigtails with red elastics that stick out and droop.
  hair_lola     black pixie cut with a side-swept fringe and a huge crimson satin bow on the top-left of the head
                (two wings tilted up ~15 deg toward their ends, 1-px lit rim, a dark pinched fold running into a
                darker knot - reads as a bow at 64 px); its two ribbon tails lie flat along the left side of the head.
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
FADE = hx('#93a9c6')
RIM = hx('#bfe6f2')
# cold ghost hands: lavender-grey shadows, dirty grey fingertips
HAND = pal('#2c2735', '#3e3747', '#544b5a', '#6b606c', '#837679', '#9a8b8b', '#ae9f9d', '#c2b4b0')
DIRT = hx('#5d5a58')
# Lola's huge bow: deep crimson satin (reads against her black hair and the pale face at 64 px)
BOWRED = pal('#160205', '#2c050a', '#470910', '#680f17', '#8a1720', '#aa2229', '#c83a37', '#e06450', '#f39a80')
# Ofelia's Alice band: deep maroon velvet (soft sheen, no bright edges)
BAND = pal('#120308', '#20060d', '#320a15', '#46101d', '#5c1726', '#742232', '#8c3343')

KNEE = 3.0          # pale knee band height on the shin (above the navy knee sock)
WAIST = 6.5         # skirt hinge line (y)

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


def ghost(c, y, rim=0.0, fade=1.0):
    """Translucent spirit: alpha ~228 on the head, ~214 at the waist, dissolving into a cold mist from the hem down
    (~200 at the knees, ~158 at the soles, tinted toward mist blue); `rim` adds the cold edge glow; `fade` scales the
    mist tint (soles and sole edges keep their black so a kicked-back shoe never reads as a pale slab)."""
    if c is None:
        return None
    if y < -1.0:
        a = 228
    elif y < 15.0:
        a = 222 - (y + 1.0) / 16.0 * 14.0
    else:
        a = 208 - clamp((y - 15.0) / 9.0) * 50
    t = clamp((y - 14.0) / 10.0) * 0.38 * fade
    if t > 0:
        c = mix(c, FADE, t)
    if rim > 0:
        c = mix(c, RIM, rim)
    return (c[0], c[1], c[2], int(a))


_RIM = [0.0]
_FADE = [1.0]
_SOLID = [False]


def G(fn):
    def f(ctx):
        _RIM[0] = 0.0
        _FADE[0] = 1.0
        _SOLID[0] = False
        c = fn(ctx)
        if c is None:
            return None
        g = ghost(c, A(ctx)[1], _RIM[0], _FADE[0])
        if _SOLID[0]:
            g = (g[0], g[1], g[2], 255)                 # always-covered occluder: nothing behind may ghost through
        return g
    f.__name__ = fn.__name__
    return f


def rim_edge(ctx, amt):
    """Mark a texel on the vertical silhouette edge of a cloth / hair box for the cold ghost rim (see ghost())."""
    if ctx.face in ('top', 'bottom') or is_plane(ctx):
        return
    if ctx.i == 0 or ctx.i == ctx.w - 1:
        _RIM[0] = amt


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
        if f in ('top', 'bottom'):
            return None                                 # buried in the skull / the torso
        v -= 0.06
        if ly < 1.6:
            v -= 0.16                                   # shadow under the big head
        if f == 'front' and 1 <= ctx.i <= 2 and 2 <= ctx.j <= 3:
            v -= 0.05                                   # throat hollow
        return pick(SKIN, v)
    if t == 'ear':
        if f in ('west', 'east'):
            outer = (f == 'west') == (A(ctx)[0] < 0)
            if not outer:
                return None                             # flat against the skull side (no z-fight)
            if outer and ctx.i in (0, 1) and 1 <= ctx.j <= 1:
                return pick(SKIN, v - 0.3)               # ear canal shadow
            if outer and ctx.j == 0:
                v += 0.05
        return pick(SKIN, v - 0.04)
    if t == 'thigh':
        if f == 'top':
            return None                                 # flush with the waist band's underside (no z-fight)
        return pick(SKIN, v - 0.12 - ly / h * 0.1)
    return pick(SKIN, v)


@G
def hand_mat(ctx):
    """Long ghost-pale hands: knuckle creases, bluish nail beds, dirty fingertips."""
    t = tag(ctx)
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    v = 0.66 + face_light(ctx) * 1.0
    if edge(ctx) == 0 and f not in ('top', 'bottom'):
        v -= 0.05
    if t == 'palm':
        if f == 'top':
            return pick(HAND, 0.12)                     # inside the cuff
        if ly < 1.0:
            v -= 0.26                                   # deep shadow under the cuff
        elif ly < 2.0:
            v -= 0.08
        if f in ('west', 'east') and ly > h - 0.9:
            v -= 0.1                                    # knuckle line
        if f in ('west', 'east') and 1.0 <= ly < h - 1 and ctx.i == ctx.w // 2:
            v -= 0.06                                   # a tendon / vein down the back of the hand
        return pick(HAND, v)
    if t in ('finger', 'index', 'thumb'):
        if f == 'top':
            return pick(HAND, v - 0.2)
        if f == 'bottom':
            return mix(DIRT, NAIL, 0.3)
        if abs(ly - 1.5) < 0.5 or (h >= 5 and abs(ly - 3.5) < 0.5):
            v -= 0.12                                   # knuckle creases
        c = pick(HAND, v - ly / h * 0.08)
        if ly > h - 1:
            c = mix(c, DIRT, 0.55)                      # dirty grey fingertips
            if f == 'front' or f == 'back':
                c = mix(c, NAIL, 0.35)                  # cold nails
        return c
    return pick(HAND, v)


@G
def knee_mat(ctx):
    """Shin: bare pale knee band on top, navy ribbed knee sock below (a plaster on her left knee)."""
    f = ctx.face
    x, y, z = A(ctx)
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    if f == 'top':
        return None                                     # buried in the thigh
    if f == 'bottom':
        return pick(NAVY, 0.15)
    if ly < KNEE:
        v = skin_v(ctx, 0.78)
        if ly < 1.2:
            v -= 0.12                                   # shadow under the hem
        c = pick(SKIN, v)
        if f == 'front' and x > 0 and 1 <= ctx.i <= 2 and ly >= 1.0:
            c = PLASTER[2] if ctx.i == 1 else PLASTER[1]    # a sticking plaster on her left knee
            if ly < 2.0:
                c = PLASTER[0] if ctx.i == 2 else PLASTER[1]
        if f == 'front' and x < 0 and ctx.i == 2 and 1.0 < ly < KNEE:
            c = mix(c, LAVENDER, 0.35)                  # bruise on the right knee
        return c
    v = 0.5 + face_light(ctx) * 1.1
    v += 0.07 if ctx.i % 2 == 0 else -0.05              # knit ribs
    v -= clamp((ly - 4.0) / 2.0) * 0.12
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
    """Black patent Mary-Jane: one clear strap across the instep (silver buckle on the outer side), a single
    specular texel on the toe cap, a dark sole edge (no grey plinth)."""
    f = ctx.face
    x, y, z = A(ctx)
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    outer_x = x < 0 if f == 'west' else x > 0
    zi = int(math.floor(z + 0.001))                     # texel row along the foot: -5 toe tip .. 1 heel
    _FADE[0] = 0.35                                     # patent black survives the mist
    if f == 'bottom':
        _FADE[0] = 0.08                                 # the sole stays a dark shoe sole from behind ('run')
        if zi >= 0:
            return pick(SOLE, 0.05)                     # heel block
        return pick(SOLE, 0.18 if (ctx.i + ctx.j) % 3 else 0.08)
    if f == 'top':
        if zi >= -2 and 1 <= ctx.i <= w - 2:
            return None                                 # opening: the shin stands here
        if zi == -3:
            return pick(PATENT, 0.74 if ctx.i % 2 else 0.68)   # the strap across the instep: one clear band
        if zi >= -2:
            v = 0.3                                     # collar of the shoe beside the ankle
            if outer_x:
                v += 0.05
            return pick(PATENT, v)
        v = 0.24 + (-3 - zi) * 0.04
        if ctx.i == 1 and zi == -4:
            v = 0.5                                     # gloss streak along the toe
        if ctx.i == 1 and zi == -5:
            return PATENT[9]                            # one deliberate specular texel on the toe cap
        return pick(PATENT, v)
    if ly > h - 1:
        _FADE[0] = 0.1
        return pick(SOLE, 0.16 if f == 'front' else 0.1)    # sole edge (dark: no grey plinth)
    v = 0.26 + face_light(ctx) * 1.2
    if f == 'front':
        if ctx.j == 0:
            v += 0.14 if ctx.i in (1, 2) else 0.05      # rounded toe cap
        if ctx.i == 1 and ctx.j == 0:
            return PATENT[7]
        return pick(PATENT, v)
    if f in ('west', 'east'):
        if zi == -3:
            if outer_x and ctx.j == 0:
                return SILVER[3]                        # buckle on the outer side
            if outer_x and ctx.j == 1:
                return SILVER[1]
            return pick(PATENT, 0.66 - ctx.j * 0.08)    # strap down to the sole
        if zi in (-4, -2) and ctx.j <= 1:
            v -= 0.06
        if ctx.j == 0 and zi <= -4:
            v += 0.12                                   # rolled top edge catches light
    if f == 'back':
        v -= 0.05
    return pick(PATENT, v)


# ------------------------------------------------------------------ smock (guardapolvo)
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
        if f == 'bottom' or (f != 'top' and y > WAIST + 0.05):
            return None                                 # buried in the waist band
        if f in ('west', 'east'):
            rim_edge(ctx, 0.26)
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
                col = ctx.i + 2 if f == 'front' else ctx.w + 1 - ctx.i
                v += {'W': 0.08, 'w': 0.0, 'g': -0.06, 'c': -0.2, 'C': -0.12, 'P': 0.06, 'p': -0.1}.get(PANEL_FRONT[0][col], 0)
                if f == 'front' and ctx.i + 2 == 7 and ctx.j == 6:
                    return pick(SMOCK, 1.0)             # top button of the placket
        else:
            if abs(z) < 1.6 and y < 7:
                v -= 0.12                               # armpit under the sleeve
            if ctx.j == 3:
                v -= 0.06
    elif t == 'core':
        if f != 'bottom':
            return None                                 # buried: torso above, skirt panels around it
        v = 0.3 - max(abs(x) / 6.5, abs(z) / 4.0) * -0.1   # the dark underside of the bell
    elif t == 'panel':
        which = ctx.cube.which
        out = {'front': 'front', 'back': 'back', 'right': 'west', 'left': 'east'}[which]
        if which in ('front', 'back') and ly < 4.0 and (lx < 1.0 or lx > w - 1.0):
            return None                                 # A-line: the waist is 14 wide, the hem 16
        if f == 'top':
            return pick(SMOCK, 0.36)                    # the fold at the waist seam (no bright ledge)
        if f != out:
            v -= 0.32 if f not in ('top', 'bottom') else 0.2
            c = pick(SMOCK, v)
            return mix(c, GRIME[1], 0.55) if f == 'bottom' else c
        u, j = ctx.i, ctx.j
        rim_edge(ctx, 0.34)
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
        rim_edge(ctx, 0.26)
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
            return pick(SMOCK, 0.18)                    # dark mouth of the cuff around the wrist
        if ctx.j == ctx.h - 1:
            v -= 0.12
    elif t == 'belt':
        if f == 'front':
            return None                                 # lies on the back panel (no z-fight)
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


# Front skirt panel 16 x 10 (x -8..8).  W lit pleat face  w cloth  g edge turning away  C soft pleat crease (front
#  panel only: low contrast so it never builds glyphs at distance)  P placket edge  p placket overlap shadow
#  B button  b button shadow  K the pocket's lit top fold  s soft shadow under the fold  q flat pocket patch (no
#  outline: the pleats simply stop)  H hem fold
PANEL_FRONT = [
    "gWwCWwCPpWwCWwCg",
    "gWwCWwCBpWwCWwCg",
    "gWwCWwCbpWwCWwCg",
    "gWKKKKCPpWKKKKCg",
    "gWssssCwpWssssCg",
    "gWqqqqCBpWqqqqCg",
    "gWqqqqCbpWqqqqCg",
    "gWwCWwCPpWwCWwCg",
    "gWwCWwCBpWwCWwCg",
    "HHHHHHHHbHHHHHHH",
]
# Back panel: pleats each side of an inverted box pleat (dark V) under the half-belt
PANEL_BACK = [
    "gWwcWwcWkkWwcWwg",
    "gWwcWwcWkkWwcWwg",
    "gWwcWwcWkkWwcWwg",
    "gWwcWwcWkkWwcWwg",
    "gWwcWwcWkkWwcWwg",
    "gWwcWwcWkkWwcWwg",
    "gWwcWwcWkkWwcWwg",
    "gWwcWwcWkkWwcWwg",
    "gWwcWwcWkkWwcWwg",
    "HHHHHHHHHHHHHHHH",
]
PANEL_SIDE = [
    "gWwcWwcWwg",
    "gWwcWwcWwg",
    "gWwcWwcWwg",
    "gWwcWwcWwg",
    "gWwcWwcWwg",
    "gWwcWwcWwg",
    "gWwcWwcWwg",
    "gWwcWwcWwg",
    "gWwcWwcWwg",
    "HHHHHHHHHH",
]
assert all(len(r) == 16 for r in PANEL_FRONT + PANEL_BACK) and all(len(r) == 10 for r in PANEL_SIDE)
PANEL_V = {'W': 0.93, 'w': 0.81, 'g': 0.64, 'c': 0.47, 'C': 0.66, 'P': 0.9, 'p': 0.7, 'B': 1.0, 'b': 0.64,
           'K': 0.99, 's': 0.7, 'q': 0.86, 'k': 0.45, 'H': 0.5}
# ink blot on her left pocket + a drip (front panel texels u, j) -> INK index
INK_BLOT = {(11, 4): (2, 0.35), (12, 4): (1, 0.6), (11, 5): (1, 0.75), (12, 5): (0, 0.9), (13, 5): (2, 0.4),
            (12, 6): (1, 0.55), (12, 7): (2, 0.35), (12, 8): (3, 0.25), (10, 5): (3, 0.25)}

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
#  p blush  f/g philtrum: two 1-px soft shades under the nose that run down into nothing
#  m the seam: a short (3 + 2 dissolving ends 'e') healed-over line (SKIN[4]-ish) where the lips grew together
#  X two 1-px pinches across it (skin grown shut, like old stitch scars), x the skin they pull just under it
#  (no lit lip row: a lit row under the seam read as a lower lip)  L / l / c lip / faint seam / crease (variants)
#  (No dark line with corners: every variant with a dark core + end dimples read as a closed mouth.)
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
    "sppooofofoopps",   # r11 doll blush 2x1; the philtrum starts under the nose ...
    "sooooogogoooos",   # r12 ... and runs down into the two pinches
    "sooooeXmXeooos",   # r13 NO MOUTH: a short healed-over seam, pinched shut at two points (soft ends)
    "SssoooxoxoossS",   # r14 the pinches pull the plain skin under it (no lip)
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
    base = pick(SKIN, b)
    # the sealed mouth: low-contrast blends of the local skin tone (no hard line that could read as lips)
    if ch == 'L':
        return mix(base, SKIN[8], 0.45)
    if ch == 'c':
        return mix(base, SKIN[5], 0.22)
    if ch == 'l':
        return mix(mix(base, SKIN[5], 0.34), LAVENDER, 0.06)
    if ch == 'f':
        return mix(base, SKIN[5], 0.42)                 # philtrum: soft shade under the nose ...
    if ch == 'g':
        return mix(base, SKIN[5], 0.2)                  # ... running down into nothing
    if ch == 'm':
        return mix(mix(base, SKIN[4], 0.78), LAVENDER, 0.05)   # the healed-over seam
    if ch == 'X':
        return mix(mix(base, SKIN[3], 0.62), LAVENDER, 0.08)   # a pinch where the skin grew shut across it
    if ch == 'x':
        return mix(base, SKIN[4], 0.42)                 # the pinch pulls the skin just under the seam
    if ch == 'e':
        return mix(base, SKIN[5], 0.3)                  # seam ends dissolve (never dark end points)
    return base


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
        v -= 0.07 + (ctx.j - 13) * 0.04                 # jawline turns under (continues on the skull side)
    if 3 <= ctx.j <= 6:
        v -= 0.03                                       # temple
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
    """Skull behind the face plate: socket rings seen through the holes, skin cheeks/temples, a narrow nape patch at
    the centre back; everything a hair shell covers is deep hair shadow (no pale slab under the hair)."""
    f = ctx.face
    x, y, z = A(ctx)
    if f == 'front':
        c = socket_px(ctx.i, ctx.j)
        return c if c is not None else pick(SKIN, 0.55)
    if f == 'top':
        return None                                     # buried under every hair shell
    if f == 'bottom':
        _SOLID[0] = True                                # opaque: the socket rings on the skull front never ghost through
        if z < -3.0:
            return pick(SKIN, 0.4 + (z + 6.0) * -0.03)   # under the chin
        if z < -2.0:
            return pick(SKIN, 0.24)
        # behind the jaw every hair shell's own underside covers this 1 texel lower; only the pulled-back styles'
        # nape notch (a skin strip from the nape down to the neck) shows it: shadowed nape skin, never a black band
        return pick(SKIN, 0.3 + clamp((z - 2.0) / 4.0) * 0.1)
    if f in ('west', 'east'):
        # one skull serves all seven hairstyles: skin wherever any pulled-back style leaves the side bare, grown by
        # 1 texel for the recess under the shell (seen past the hair edge at 3/4 angles), so no dark slit ever opens
        # between cheek and hair; a mid hair value (not black) where every style covers it
        if not side_skin(y, z):
            return pick(BROWN, 0.35)
        v = skin_v(ctx, 0.74)
        if -16.5 < y < -12.5 and -5.5 < z < -1.5:
            v -= 0.07                                   # temple hollow
        if -10.0 < y < -8.0 and z < -3.0:
            v += 0.04                                   # cheekbone catches the light
        jaw = -5.0 - clamp((z + 6.0) / 6.0) * 2.1       # the mandible's lower edge rises toward the ear
        if y > jaw:
            v -= 0.12 + (y - jaw) * 0.02                # under the jaw: the side of the face turns under
        elif y > jaw - 1.0:
            v += 0.03                                   # lit edge of the jaw
        if z > -1.0 and y > -8:
            v -= 0.1 + clamp((-6.0 - y) / 2.0) * 0.1   # jaw hinge in the shadow of the hair
        if not side_exposed(y, z):
            v -= 0.1                                    # soft shadow just under the hair edge
        if -9 <= y <= -7 and z < -4:
            return mix(pick(SKIN, v), BLUSH, 0.35)
        return pick(SKIN, v)
    if f == 'back':
        # a narrow nape (4-6 px) at the centre with ragged hair tips; hair shadow everywhere else (opaque: always
        # behind a hair shell or seen through the nape window, so the face never ghosts through the back of the head)
        _SOLID[0] = True
        ax = abs(x)
        top = -7.0 + ax * 0.9 + hash3(int(math.floor(x)), 7, 3, 11) * 1.3
        if ax < 3.0 and y > top:
            return pick(SKIN, 0.5 - clamp((top + 1.5 - y) / 1.5) * 0.1 - (0.06 if ax > 2.0 else 0.0))
        return pick(BROWN, 0.1 + face_light(ctx) * 0.3)
    return pick(BROWN, 0.12 + face_light(ctx) * 0.3)


EYE_GLOW = [(3, 7, GLOW_GLINT), (9, 7, GLOW_GLINT)]


def side_exposed(y, z):
    """Skull-side texel left bare by at least one pulled-back hairstyle (paloma / rocio / anasofia share a mask)."""
    return not side_hair('paloma', y, z) or not side_hair('lola', y, z)


def side_skin(y, z):
    return any(side_exposed(y + dy, z + dz) for dy in (0.0, -1.0, 1.0) for dz in (0.0, 1.0, -1.0))


# ------------------------------------------------------------------ the O mouth (jaw, freed only)
# a 4x4 zero-thickness plane parked inside the skull; pose 'freed' slides it onto the face (z = -7.1)
O_MOUTH = [
    ".LL.",
    "LKKL",
    "LKkL",
    ".ll.",
]


@G
def jaw_mat(ctx):
    if ctx.face != 'front':
        return None
    ch = O_MOUTH[ctx.j][ctx.i]
    if ch == '.':
        return None
    return {'L': LIPS[3], 'l': LIPS[2], 'K': MOUTH[0], 'k': MOUTH[2]}[ch]


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


def curls(ctx, a, b, top=False):
    """Corkscrew ringlets, drawn on an 8-texel period so each coil still reads at a 300-px close-up: every ringlet is
    a 7-texel tube of diagonal turns (a 3-px bright crest, a 1-px black shadow tucked right under it, a 4-px dark
    core; the tube's two edge columns stay dark so it reads round) beside a 1-px dark gap.  Each ringlet starts its
    turns at its own height (random phase, never mirrored into a herringbone), so the cloud reads as separate springy
    spirals, not orange-brown blotches or knitting.  Seen from above (top=True) the ringlets are round coil heads on a
    staggered grid.  Three values only (no mid tone).  Returns a ramp value."""
    ai = int(math.floor(a + 1000.0)) - 1000
    col = ai // 8
    i = ai - col * 8
    if top:
        bi = int(math.floor(b + (col % 2) * 4 + 1000.0)) - 1000
        return CURL_V[CURL_TOP[bi % 8][i]] + face_light(ctx) * 0.6
    bi = int(math.floor(b + hash3(col, 3, 5, 47) * 8.0 + 1000.0)) - 1000
    return CURL_V[CURL_G[bi % 8][i]] + face_light(ctx) * 0.6


def _curl_glyph():
    rows = []
    for j in range(8):
        r = ''
        for i in range(8):
            if i == 7:
                r += 'k'                                # the gap between two ringlets
                continue
            ph = (j - i * 0.6) % 8.0
            ch = 'H' if ph < 3.6 else 'k' if ph < 4.6 else 'd'
            if i in (0, 6):
                ch = 'd' if ch == 'H' else 'k' if ch == 'k' else 'd'   # the tube turns away at its edges
            r += ch
        rows.append(r)
    return rows


CURL_G = _curl_glyph()
CURL_TOP = [
    "kddHHddk",
    "dHHHHHdk",
    "dHHHHHdk",
    "HHHHHddk",
    "dHHHddkk",
    "kdddddkk",
    "kkddkkkk",
    "kkkkkkkk",
]
CURL_V = {'k': 0.15, 'd': 0.3, 'M': 0.47, 'H': 0.7}


def pulled(style):
    return style in ('paloma', 'rocio', 'anasofia', 'lola')


TIPS = ('paloma', 'mecha', 'rocio', 'anasofia', 'lola')     # styles whose back edge ends in a ragged tips plane
# Chela's cloud (the two stepped shell blocks): clump faces flush against or inside it are left transparent
CHELA_SHELL = [(-10.0, -22.0, -9.0, 10.0, -3.0, 4.0), (-9.5, -21.0, 4.0, 9.5, -3.0, 9.0)]
NORMAL = {'front': (0, 0, -1), 'back': (0, 0, 1), 'west': (-1, 0, 0), 'east': (1, 0, 0), 'top': (0, -1, 0),
          'bottom': (0, 1, 0)}


def buried(x, y, z, face, boxes, eps=0.05):
    """True if the texel looks straight into one of the boxes (face flush against it or inside it)."""
    n = NORMAL[face]
    px, py, pz = x + n[0] * eps, y + n[1] * eps, z + n[2] * eps
    return any(b[0] - 1e-3 <= px <= b[3] + 1e-3 and b[1] - 1e-3 <= py <= b[4] + 1e-3 and b[2] - 1e-3 <= pz <= b[5] + 1e-3
               for b in boxes)


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
        return z > 1.2 + (y + 9.0) * 0.55                # tapered pixie nape
    if y < -15.5:
        return True
    if y < -11.0:
        return z > -5.0 + (y + 15.5) * 0.65
    if y < -8.0:
        return z > 1.2
    return z > 1.6 + (y + 8.0) * 0.7                     # hairline behind the ear runs down to the back corner


def nape_top(x):
    """Upper edge of the bare nape patch at the centre back (shared by the skull paint and the shell cut-out)."""
    ax = abs(x)
    return -7.0 + ax * 0.9 + hash3(int(math.floor(x)), 7, 3, 11) * 1.3


def back_v(st, x, y, ctx, seed, light=0.9):
    """Value of the back-of-head hair.  The shell's back face, the step of the front block, the back block's top and
    the ragged tips plane all call it with the same seed, so strands and sheen run on unbroken across them (no
    ledges, no outlines: the back of the head reads as one rounded hair mass, not a crate)."""
    if st == 'rocio':
        u = x / (0.3 + 0.7 * clamp((y + 18.5) / 13.0))   # every strand converges on the scrunchie
    elif st == 'paloma':
        u = x + (math.copysign(1.0, x) * clamp((y + 12.0) / 6.0) * 2.0)   # pulled out to the braids
    else:
        u = x
    # sheen: an arc across the back of the skull (higher in the middle, dropping at the sides) = a round head
    v = strands(u, y - (x / 8.0) ** 2 * 3.0, ctx, seed, sheen=-15.5, soft=0.7, light=light)
    v -= clamp((y + 10.0) / 8.0) * 0.12
    v -= clamp((abs(x) - 5.0) / 3.0) ** 1.5 * 0.1       # turns away toward the sides (soft, no outline)
    if y < -18.0:
        v += 0.04                                       # the top-back edge turns up toward the light
    if st in ('paloma', 'anasofia') and abs(x) < 1.5:
        v -= 0.05
    return v


def back_seed(st):
    return HAIRS.index(st) * 7 + 3


def crown_field(st, x, z):
    """Strand field on the crown (the top faces of both shell blocks, seen from above): (u, a) = the across-strand
    coordinate (texels at the parting / whorl) and the along-strand coordinate.  The level lines of u ARE the strands:
    they leave the parting sideways and turn toward the front / the back as they near those edges (a fan, never
    parallel planks); paloma's sweep back to the braid roots, rocio's converge on the scrunchie, anasofia's on the
    pigtail roots, mecha's radiate from a whorl on the crown, lola's sweep across from a side parting."""
    if st in ('paloma', 'ofelia', 'anasofia'):
        ax = abs(x + 0.25)                              # the parting: x -0.5 (16 wide) / 0 (odd widths)
        if st in ('paloma', 'anasofia'):
            # converging on the braid roots behind the ears / the pigtail roots on the sides
            rx, rz, R = (9.5, 4.5, 9.0) if st == 'paloma' else (8.8, 1.0, 8.5)
            u = math.atan2(z - rz, rx - ax) * R
            ax = rx - math.hypot(rx - ax, z - rz)       # along: from the parting toward the root
        else:
            u = (z + 0.5) / (1.0 + 0.3 * ax)            # dead straight: falls sideways, fanning out
        return u + (0.0 if x > -0.25 else 23.0), ax     # each side of the parting has its own strands
    if st == 'rocio':
        return x / (0.42 + 0.58 * clamp((7.5 - z) / 15.5)), z    # combed back onto the scrunchie
    if st == 'lola':
        dx = x - 3.5                                    # side parting
        if dx < 0:
            return (z + 1.0 + 0.4 * -dx) / (1.0 + 0.22 * -dx) + 23.0, -dx   # swept forward across to her right
        return (z - 0.2 * dx) / (1.0 + 0.2 * dx), dx
    dz = z - 2.5                                        # mecha: the bob falls every way from a whorl on the crown
    return math.atan2(x, dz) * 4.2, math.hypot(x, dz)


CROWN_C = {'rocio': 3.0, 'mecha': 2.5}                  # crown point (z) the sheen arc curves round


_LINES = {}


def strand_lines(seed):
    """Positions (in u) of the strand borders on the crown: irregular spacing 2-3.5 texels."""
    if seed not in _LINES:
        pos, u, k = [], -60.0, 0
        while u < 60.0:
            pos.append(u)
            u += 2.0 + hash3(k, seed, 0, 97) * 1.5
            k += 1
        _LINES[seed] = pos
    return _LINES[seed]


def crown_v(st, x, z, ctx, seed, lower=False):
    """Hair seen from above.  The strand borders are drawn as clean 1-px dark lines along the level lines of the crown
    field (each pixel tests its distance to the nearest border in pixels, so a curved line never breaks into
    stair-step noise); every line is broken into 3-6 texel runs with offset gaps, so neighbouring borders never line
    up into plank lines.  Between two borders the strand is shaded like a tube (lit just past the border, darker
    toward the next).  One broken sheen arc runs round the crown point following the curve of the skull, and the
    value falls off toward all four edges so the box corners round off.  The back block's top (lower=True, 1 texel
    lower) runs on in the same field, a touch darker, with no lit edge."""
    u, a = crown_field(st, x, z)
    gx = (crown_field(st, x + 0.25, z)[0] - crown_field(st, x - 0.25, z)[0]) * 2.0
    gz = (crown_field(st, x, z + 0.25)[0] - crown_field(st, x, z - 0.25)[0]) * 2.0
    g = max(0.35, math.hypot(gx, gz))                   # u per pixel across the strands
    L = strand_lines(seed)
    k = bisect.bisect_right(L, u) - 1
    u0, u1 = L[k], L[k + 1]
    if (u1 - u0) / g < 1.9:                             # strands converging: every other border merges away
        k -= k % 2
        u0, u1 = L[k], L[k + 2]
    elif (u1 - u0) / g > 3.6 + hash3(k, seed, 5, 67) * 1.6:
        um = (u0 + u1) * 0.5 + (hash3(k, seed, 6, 59) - 0.5) * 0.4 * (u1 - u0)
        k = k * 2 + 200                                 # fanning out: a new strand surfaces between the two
        if u < um:
            u1 = um
        else:
            u0, k = um, k + 1
    p = (u - u0) / (u1 - u0)                            # 0..1 across this strand
    v = 0.52 + (hash3(k, seed, 0, 71) - 0.5) * 0.04
    if (u - u0) / g < 1.0:
        v += 0.08                                       # the lit side of the strand, just past the border
    v -= p * 0.06                                       # rolling into shadow toward the next border
    for kk, uu in ((k, u0), (k + 1, u1)):
        if abs(u - uu) / g < 0.5:
            run = 3.0 + hash3(kk, seed, 1, 73) * 3.0
            seg = int(math.floor((a + hash3(kk, seed, 4, 61) * 6.0) / run))
            if hash3(kk, seg, seed, 79) < 0.78:
                v = 0.52 - 0.17 + (hash3(kk, seg, seed, 81) - 0.5) * 0.04   # the dark border (broken)
    cz = CROWN_C.get(st, 1.0)
    q = math.hypot(x / 7.6, (z - cz) / 7.2) * 7.0      # ~texels out from the crown point
    q0 = 3.9 + (hash3(k, seed, 2, 83) - 0.5) * 1.3
    if z < cz + 0.5 and hash3(k, seed, 3, 89) < 0.8:
        dq = abs(q - q0)
        if dq < 0.6:
            v += 0.17                                   # the broken sheen arc
        elif dq < 1.5:
            v += 0.06
    e = ((x / 8.0) ** 4 + ((z + 0.5) / 7.5) ** 4) ** 0.25
    v -= clamp((e - 0.66) / 0.34) ** 1.3 * 0.18         # rounds off toward every edge
    if lower:
        v -= 0.04
    return v


def under_v(st, x, z, c, ctx):
    """Underside of the hair: every shell ends 1 texel below the skull (y -3), and whenever the head bows (face_wall,
    cover_ears) this face turns toward a viewer behind her.  It continues the back face's strands (same columns, same
    seed) rolling under toward the neck, ~0.1 darker, with no baked face light (the renderer darkens a bottom face)."""
    yy = -3.0 + max(0.0, c.zb - z) * 0.6
    if st == 'chela':
        v = curls(ctx, x, yy + 3.0) - 0.12
    else:
        v = back_v(st, x, yy, ctx, back_seed(st), light=0.0) - 0.1
        if pulled(st) and abs(x) < 4.2:
            v -= 0.05                                   # the short wisps framing the nape notch
    dn = max(abs(x) - 2.0, abs(z) - 2.0)
    v -= clamp((3.0 - dn) / 3.0) * 0.06                 # occlusion beside the neck
    return v


@G
def shell_mat(ctx):
    c = ctx.cube
    st = c.style
    P = c.pal
    f = ctx.face
    x, y, z = A(ctx)
    lx, ly, lz = local(ctx)
    w, h, d = c.size
    bottom = c.a0[1] + h                                # lowest y of this shell
    if f == 'front':
        # behind the fringe plane: only the top row and the hair-covered outer columns are painted, so no light
        # sliver can show between the plane and the shell when the head bows (the face stays open)
        if getattr(c, 'part', '') != 'front' or st == 'chela':
            return None                                 # (chela's fringe plane paints every texel it covers itself)
        prof = FRONT_PROFILE[st]
        jr = int(math.floor(y - c.a0[1]))
        if jr == 0 or (ctx.i in (0, w - 1) and jr < prof[ctx.i] - 1):
            return pick(P, 0.22)
        return None
    if f == 'bottom':
        # the underside of the hair, 1 texel below the skull's own underside (never its plane): hair, then the nape
        # notch, then the neck when the head bows and you stand behind her
        if z < -7.0:
            return None
        if abs(x) > 7.0:
            if not side_hair(st, y - 0.5, z):
                return None
            return pick(P, under_v(st, x, z, c, ctx))   # under the side hair
        if z < -2.5:
            return None                                 # under the face: the skull's chin underside shows
        if abs(x) < 2.1 and abs(z) < 2.1:
            return None                                 # the neck stands here
        if pulled(st) and z > 2.0 and abs(x) < 3.2 and bottom - 0.5 > nape_top(x) + 0.5:
            return None                                 # nape notch: the bare nape runs on under the head to the neck
        return pick(P, under_v(st, x, z, c, ctx))
    if f in ('west', 'east') and not side_hair(st, y, z):
        return None
    if f == 'back' and getattr(c, 'part', '') == 'front':
        # the 1-texel step where the back block (0.5 narrower each side, 1 lower) meets the front block: painted
        # with the back block's own strands so it reads as the head rounding off, never as a dark ledge
        if abs(x) < c.a0[0] + w - 1.0 - 0.01 and y > c.a0[1] + 1.0:
            return None                                 # buried behind the narrower back block
        if pulled(st) and y > -9.0 and abs(x) > 7.0 and not side_hair(st, y, z + 0.5):
            return None
        if st == 'chela':
            return pick(P, curls(ctx, x, y) - clamp((y + 8.0) / 6.0) * 0.14)
        return pick(P, back_v(st, x, y, ctx, back_seed(st)))
    if f == 'back':
        if pulled(st) and abs(x) < 3.2 and y > nape_top(x) + 0.5:
            return None                                 # bare nape patch (the skull's skin shows 1 texel deeper)
        # (TIPS styles keep their last row painted: it sits 0.12 behind the tips plane and closes the gap, so the
        #  nape skin never glints through between them)
        if st not in TIPS and y > bottom - 1.0 and hash3(int(math.floor(x)), 5, HAIRS.index(st), 19) > 0.5:
            return None                                 # ragged hair tips along the lower edge
    if f in ('west', 'east') and y > bottom - 1.0 and hash3(int(math.floor(z)), 6, HAIRS.index(st), 29) > 0.6 \
            and z > 0.0 and st != 'chela':
        return None                                     # ragged ends along the lower back corners too
    seed = HAIRS.index(st) * 7 + {'top': 0, 'west': 1, 'east': 2, 'back': 3}[f]
    if st == 'ofelia' and f in ('west', 'east') and -6.0 <= z < -3.0 and y < -13.0 + (z + 6.0) * 0.4:
        return band_px(ctx, -0.08 if y > -14.5 else 0.0)   # the velvet band's ends run down behind the ears
    if st == 'ofelia' and f in ('west', 'east') and -6.0 <= z < -3.0 and y < -12.0 + (z + 6.0) * 0.4:
        return pick(P, 0.14)                            # where the band slips under the hair
    if st == 'chela':
        if f == 'top':
            v = curls(ctx, x, z, top=True)
        elif f in ('west', 'east'):
            v = curls(ctx, z + (37 if f == 'east' else 0), y)
        else:
            v = curls(ctx, x, y)
        v -= clamp((y + 8.0) / 6.0) * 0.14
        return pick(P, v)
    if f == 'top':
        # the crown (front block top + the back block's top 1 lower, one field): strands radiating from the parting
        part = st in ('paloma', 'ofelia', 'anasofia')
        if part and abs(x + 0.25) < 0.5 and z < 6.5:
            return mix(pick(P, 0.4), SCALP, 0.32 - clamp((z - 1.0) / 5.0) * 0.16)   # centre parting
        if st == 'lola' and abs(x - 3.5) < 0.5 and z < 0.5:
            return mix(pick(P, 0.55), SCALP, 0.45)      # side parting
        v = crown_v(st, x, z, ctx, HAIRS.index(st) * 7, lower=getattr(c, 'part', '') == 'back')
        if part and abs(x + 0.25) < 1.5:
            v -= 0.05                                   # the hair each side of the parting
        if st == 'lola' and abs(x - 3.5) < 1.5 and z < 0.5:
            v -= 0.05
        return pick(P, v)
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
        else:
            v -= clamp((y + 9.0) / 5.0) * 0.12
        if pulled(st) and not side_hair(st, y + 0.9, z - 0.9):
            v += 0.08                                   # lit hairline edge
        return pick(P, v)
    # back
    if st in ('paloma', 'anasofia') and abs(x) < 0.5 and y < -8.0:
        return mix(pick(P, 0.42), SCALP, 0.25)          # parting runs down to the nape
    v = back_v(st, x, y, ctx, seed)
    if pulled(st) and abs(x) < 4.2 and y > nape_top(x) - 0.5:
        v -= 0.08                                       # short dark wisps framing the nape
    return pick(P, v)


def band_px(ctx, dv=0.0):
    """Ofelia's Alice band ends on the sides of the shell: maroon velvet, soft sheen along the middle."""
    x, y, z = A(ctx)
    v = 0.56 + face_light(ctx) * 0.6 + dv
    if -5.0 <= z < -4.0:
        v += 0.06
    return pick(BAND, v)


# hairline planes in front of the forehead: per style a bottom profile (hair rows per column) + shading
FRONT_PROFILE = {
    # 16 columns: x -8..8
    'paloma': [7, 6, 5, 4, 3, 3, 2, 1, 1, 2, 3, 3, 4, 5, 6, 7],
    'rocio': [5, 10, 4, 3, 2, 1, 1, 2, 2, 1, 1, 2, 3, 4, 11, 5],
    'anasofia': [5, 4, 3, 2, 2, 2, 2, 1, 1, 2, 2, 2, 2, 3, 4, 5],
    'lola': [8, 7, 7, 6, 6, 6, 5, 5, 4, 4, 3, 3, 2, 2, 3, 6],
    # 18 columns: x -9..9 (bob with curtains framing the cheeks)
    'mecha': [15, 15, 12, 7, 7, 8, 7, 7, 7, 8, 7, 7, 7, 8, 7, 12, 15, 15],
    # 17 columns: x -8.5..8.5 (long straight, centre parting, curtains beside the face)
    'ofelia': [17, 17, 13, 7, 6, 5, 4, 4, 3, 4, 4, 5, 6, 7, 13, 17, 17],
    # 20 columns: x -10..10 (curly fringe + side masses)
    'chela': [18, 18, 18, 14, 8, 7, 7, 6, 6, 6, 6, 6, 6, 7, 7, 8, 14, 18, 18, 18],
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
        x, y, z = A(ctx)
        v = curls(ctx, x, y) + 0.03
        if tip and prof[k] < 18:
            v -= 0.08
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
        if abs(k - mid) < 0.6 and j < 4:
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
    if t in ('clump', 'tube'):
        x, y, z = A(ctx)
        if t == 'clump' and buried(x, y, z, f, CHELA_SHELL):
            return None                                 # flush against / inside the cloud: never z-fights
        if f == 'bottom':
            return pick(P, 0.16)
        if f == 'top':
            a, b = x, z
        elif f in ('front', 'back'):
            a, b = x, y
        else:
            a, b = z + (37 if f == 'east' else 0), y
        if t == 'tube':
            a, b = (lx if f in ('front', 'back', 'top') else lz) + cseed(ctx) % 4, ly + (lz if f == 'top' else 0)
        v = curls(ctx, a, b, top=(f == 'top' and t == 'clump')) - clamp((y + 8.0) / 6.0) * 0.12
        return pick(P, v)
    if t == 'tips':
        # zero-thickness plane just behind the shell's back face: carries its last row and lets uneven 1-3 texel
        # strand tips hang below it, so the bottom of the head is never a ruler-straight box edge
        if f != 'back':
            return None
        x, y, z = A(ctx)
        top = c.a0[1]                                   # = the shell's last row
        if pulled(st) and abs(x) < 3.2 and y > nape_top(x) + 0.5:
            return None                                 # bare nape (hair pulled up)
        xi = int(math.floor(x))
        r = hash3(xi, 3, HAIRS.index(st), 23)
        if pulled(st):
            ln = (0, 1, 1, 2)[int(r * 3.999)] if abs(x) > 3.6 else 0     # short nape wisps at the corners
        else:
            ln = 1 + int(r * 2.999)                     # bob: ragged ends 1-3 texels long
            if abs(x) > 6.0:
                ln = max(1, ln - 1)
        row = y - top - 1.0                             # 0.. below the shell's bottom edge
        if row > ln:
            return None
        v = back_v(st, x, y, ctx, back_seed(st))
        if row > 0:
            v -= 0.04 + row * 0.05                      # the ends thin out into shadow
        return pick(P, v)
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
    """Ribbons, scrunchie, elastics and Lola's satin bow."""
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
        if f in ('west', 'east') and (f == 'east') == (A(ctx)[0] < 0):
            return None                                 # inner face: buried in the shell, flush with the skull
        return pick(P, v + (0.08 if ctx.j == 0 else -0.04))
    if t == 'ribbon_bow':
        if f != 'front':
            return None
        ch = RIBBON_BOW[ctx.j][ctx.i]
        if ch == '.':
            return None
        return pick(P, {'H': 0.86, 'h': 0.7, 'm': 0.52, 'd': 0.32, 'k': 0.2}[ch])
    if t == 'big_loop':
        if f in ('front', 'back'):
            i = ctx.i if f == 'front' else ctx.w - 1 - ctx.i
            ii = i if c.side == 'r' else ctx.w - 1 - i
            ch = BIG_LOOP[ctx.j][ii]
            if ch == '.':
                return None
            v = BIG_V[ch]
            if f == 'back':
                v -= 0.18
            return pick(P, v)
        if f in ('west', 'east'):
            far = (f == 'west') == (c.side == 'r')
            if not far:
                return None
            return pick(P, 0.5 - ly / h * 0.2)
        # top / bottom: only over the columns whose first / last row is filled (as bow_mat does for the navy bow),
        # so no lit lid floats above the cut upper-inner corner of the wing
        ii = ctx.i if c.side == 'r' else ctx.w - 1 - ctx.i
        if (BIG_LOOP[0] if f == 'top' else BIG_LOOP[-1])[ii] == '.':
            return None
        return pick(P, 0.82 if f == 'top' else 0.2)
    if t == 'big_knot':
        if f == 'front':
            v = 0.42 + (0.1 if ctx.j == 0 else -0.14 if ctx.j == h - 1 else 0.0)
            if ctx.i in (0, w - 1):
                v -= 0.12                               # the ribbon pinched into the knot
        else:
            v = 0.26 + face_light(ctx) * 0.6
        return pick(P, v)
    if t == 'big_tail':
        # ribbon tails lying flat along the side of the head (planes facing +-X)
        if f not in ('west', 'east'):
            return None
        out = (f == 'east') == (A(ctx)[0] > 0)
        if not out:
            return None                                 # zero-thickness plane: only the face away from the head
        if ly > h - 1 and ctx.i == 1:
            return None                                 # notched ribbon end
        v = 0.66 - ly / h * 0.22 + face_light(ctx)
        if ctx.i == 0 or ly < 1.0:
            v -= 0.2                                    # folded edge in shadow
        return pick(P, v)
    if t == 'band':
        # Ofelia's Alice band: deep maroon velvet lying across the crown 2 texels behind the hairline (its side
        # faces are flush with the shell: the shell paints the ends running down behind the ears instead)
        if f in ('west', 'east', 'bottom'):
            return None
        if f == 'top':
            v = 0.62 + face_light(ctx) * 0.4
            v += 0.06 if ctx.j == 1 else -0.06          # soft velvet sheen down the middle, rounded edges
            return pick(P, v)
        if f == 'front':
            return pick(P, 0.5)
        return pick(P, 0.3)                             # back edge
    return pick(P, v)


RIBBON_BOW = [
    # 6 x 3, a small sky-blue bow tied round the braid end
    "Hh..hH",
    "hmkkmh",
    "dk..kd",
]

BIG_LOOP = [
    # 6 x 6 wing of the bow, index 0 = outer end (tilted up ~15 deg), 5 = pinched at the knot.
    # H 1-px lit satin rim  h lit satin  m mid  f the dark pinched centre fold running into the knot  d shadow side
    # D darkest under-edge
    "HH....",
    "hhHH..",
    "hfhhHH",
    "mmffhm",
    "dmmmfd",
    ".dDDd.",
]
BIG_V = {'H': 0.93, 'h': 0.76, 'm': 0.6, 'f': 0.28, 'd': 0.4, 'D': 0.2}


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


ARM_OUT = 15.0      # rest: sleeves angled out from the shoulders (deg)
ARM_FWD = -4.0      # rest: arms hang a little forward of the smock
HAND_TWIST = 35.0   # rest: palms turned back so the splayed fingers read from the front


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
    W = WAIST

    # ---------------- body (root at the hips): smock chest down to the waist, waist band closing the skirt bell
    bone('body', (0, 9.0, 0), mat=smock_mat)
    box('body', (-6, 0, -3.5), (12, 8, 7), name='torso')
    box('body', (-7, W, -4), (14, 3, 8), name='core')

    # ---------------- skirt: four flared, box-pleated panels 16 x 10 (front placket + pockets, back pleat + belt)
    # (the panels start 0.5 above the hinge: their top tucks under the smock and the hem clears 2+ texels of pale knee)
    PT = W - 0.5
    bone('skirt_front', (0, W, -3.7), parent='body', rot=(-13, 0, 0), mat=smock_mat)
    box('skirt_front', (-8, PT, -4.7), (16, 10, 1), name='panel', which='front')
    bone('skirt_back', (0, W, 3.7), parent='body', rot=(13, 0, 0), mat=smock_mat)
    box('skirt_back', (-8, PT, 3.7), (16, 10, 1), name='panel', which='back')
    box('skirt_back', (-4, W + 0.2, 4.75), (8, 2, 1), name='belt')
    bone('skirt_right', (-6.5, W, 0), parent='body', rot=(0, 0, 13), mat=smock_mat)
    box('skirt_right', (-7, PT, -5), (1, 10, 10), name='panel', which='right')
    bone('skirt_left', (6.5, W, 0), parent='body', rot=(0, 0, -13), mat=smock_mat)
    box('skirt_left', (6, PT, -5), (1, 10, 10), name='panel', which='left')

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

    # ---------------- legs: thigh (under the skirt), pale knee band + navy knee sock, cuff, Mary-Jane
    for side, sx in (('right', -1), ('left', 1)):
        lb, sb, fb = f'{side}_leg', f'{side}_shin', f'{side}_shoe'
        cx = 2.4 * sx
        bone(lb, (cx, 9.5, 0), parent='body', mat=skin_mat)
        box(lb, (cx - 2, 9.5, -2), (4, 6, 4), name='thigh', inflate=0.1)   # never shares a plane with the shin
        bone(sb, (cx, 15.5, 0), parent=lb, mat=knee_mat)
        box(sb, (cx - 2, 15.5, -2), (4, 6, 4), name='shin')
        box(sb, (cx - 2, 15.5 + KNEE, -2), (4, 1, 4), mat=cuff_mat, name='cuff', inflate=0.2)
        bone(fb, (cx, 21.0, 0), parent=sb, mat=shoe_mat)
        # 0.2 outward / 0.1 back: the two shoes never share a plane and the heel clears the shin's back face
        box(fb, (cx - 2.5 + 0.2 * sx, 21.0, -4.9), (5, 3, 7), name='shoe')

    # ---------------- arms: thin sleeves, cuffs, long cold hands (palm, thumb, three splayed 1x5 fingers)
    for side, sx in (('right', -1), ('left', 1)):
        ab, fb, hb = f'{side}_arm', f'{side}_forearm', f'{side}_hand'
        ax = 7.5 * sx
        bone(ab, (ax, 1.5, 0), parent='body', rot=(ARM_FWD, 0, -ARM_OUT * sx), mat=smock_mat)
        box(ab, (ax - 1.5, 0, -1.5), (3, 7, 3), name='sleeve', inflate=0.3)
        bone(fb, (ax, 6.5, 0), parent=ab, rot=(-6, 0, 4 * sx), mat=smock_mat)
        box(fb, (ax - 1.5, 6.5, -1.5), (3, 5, 3), name='forearm', inflate=0.15)
        box(fb, (ax - 1.5, 10.6, -1.5), (3, 1, 3), name='cuff', inflate=0.4)
        bone(hb, (ax, 11.5, 0), parent=fb, rot=(0, HAND_TWIST * sx, 0), mat=hand_mat)
        box(hb, (ax - 1, 11.5, -1.5), (2, 3, 3), name='palm')
        box(hb, (ax - 0.5 - 0.5 * sx, 12.2, -2.4), (1, 2, 1), name='thumb')
        bone(f'{side}_fingers', (ax, 14.5, 0.5), parent=hb, rot=(7, 0, 0), mat=hand_mat)
        box(f'{side}_fingers', (ax - 0.5, 14.3, -0.5), (1, 5, 1), name='finger')
        box(f'{side}_fingers', (ax - 0.5, 14.1, 1.5), (1, 5, 1), name='finger')
        bone(f'{side}_index', (ax, 14.5, -2.0), parent=hb, rot=(-7, 0, 0), mat=hand_mat)
        box(f'{side}_index', (ax - 0.5, 14.3, -2.5), (1, 5, 1), name='index')

    # ---------------- neck + head: skin plate with real socket holes over the skull, ears
    bone('neck', (0, 0.0, 0), parent='body', mat=skin_mat)
    box('neck', (-2, -4.5, -2), (4, 5, 4), name='neck')
    bone('head', (0, -4.0, 0), parent='neck', rot=(4, 0, -6), mat=skull_mat)
    box('head', (-7, -19, -7), (14, 15, 1), mat=plate_mat, name='plate')
    box('head', (-7, -19, -6), (14, 15, 12), mat=skull_mat, name='skull', decals={'eyes:front': at(EYE_GLOW)})
    box('head', (-8, -11, -1), (1, 3, 2), mat=skin_mat, name='ear')
    box('head', (7, -11, -1), (1, 3, 2), mat=skin_mat, name='ear')

    # the round singing "O": a plane parked inside the skull, slid flush onto the face by pose 'freed'
    bone('jaw', (0, -7.0, -5.5), parent='head', mat=jaw_mat)
    box('jaw', (-2, -9, -5.5), (4, 4, 0), name='mouth')

    # ---------------- hair groups (exactly one visible per girl)
    HC = (0, -12.0, 0)

    def shell(style, P, frm, size, split=3.0):
        # two stepped boxes: the back block is 0.5 narrower each side and 1 lower than the front block -> the head
        # rounds off; 0.5 (not 1) keeps every back-block side face clear of the skull's side faces (x = +-7)
        x0, y0, z0 = frm
        w, h, d = size
        box('hair_' + style, frm, (w, h, int(split - z0)), mat=shell_mat, name='shell', style=style, pal=P,
            part='front', zb=z0 + d)
        box('hair_' + style, (x0 + 0.5, y0 + 1, split), (w - 1, h - 1, int(z0 + d - split)), mat=shell_mat,
            name='shell', style=style, pal=P, part='back', zb=z0 + d)
        if style in TIPS:
            # ragged strand tips: a zero-thickness plane 0.12 behind the back face, from its last row down 3
            box('hair_' + style, (x0 + 0.5, y0 + h - 1, z0 + d + 0.12), (w - 1, 4, 0), mat=hairbit_mat,
                name='tips', style=style, pal=P)

    def front(style, P, frm, size):
        # inflated a hair so the fringe plane overlaps the shell's side faces (no light seam at the corners)
        box('hair_' + style, frm, size, mat=front_mat, name='front', style=style, pal=P, inflate=0.07)

    # Paloma: centre parting, two long plaits over the shoulders with sky-blue bows
    P = BROWN
    bone('hair_paloma', HC, parent='head', mat=shell_mat)
    shell('paloma', P, (-8, -20, -8), (16, 17, 15))
    front('paloma', P, (-8, -20, -8.05), (16, 7, 0))
    for side, sx in (('right', -1), ('left', 1)):
        b1, b2 = f'paloma_braid_{side}', f'paloma_braid_{side}_tip'
        px = 6.8 * sx
        box('hair_paloma', (px - 1.5, -10.5, 3.2), (3, 4, 3), mat=hairbit_mat, name='braid', style='paloma', pal=P)
        bone(b1, (px, -7.0, 3.0), parent='hair_paloma', rot=(-58, 0, 4 * sx), mat=hairbit_mat)
        box(b1, (px - 1.5, -7.5, 1.5), (3, 9, 3), name='braid', style='paloma', pal=P)
        bone(b2, (px, 1.5, 3.0), parent=b1, rot=(52, 0, -2 * sx), mat=hairbit_mat)
        box(b2, (px - 1.5, 1.3, 1.5), (3, 6, 3), name='braid', style='paloma', pal=P)
        box(b2, (px - 1.5, 6.8, 1.5), (3, 1, 3), mat=ribbon_mat, name='wrap', inflate=0.35, style='paloma',
            pal=CELESTE)
        box(b2, (px - 3, 6.2, 1.0), (6, 3, 0), mat=ribbon_mat, name='ribbon_bow', style='paloma', pal=CELESTE)
        box(b2, (px - 1, 7.6, 2.0), (2, 3, 2), name='tuft', style='paloma', pal=P)

    # Mecha: black bob, blunt bangs, curtains framing the cheeks
    P = BLACK
    bone('hair_mecha', HC, parent='head', mat=shell_mat)
    shell('mecha', P, (-9, -20, -8), (18, 17, 16))
    front('mecha', P, (-9, -20, -8.05), (18, 15, 0))

    # Rocio: combed back into a ponytail gathered at the back of the crown by a maroon scrunchie; the tail leaves it
    # at ~35 deg and falls in one tapered lock (4 -> 3 -> 2 wide, ragged tip) close to the back of the head
    P = BROWN_L
    bone('hair_rocio', HC, parent='head', mat=shell_mat)
    shell('rocio', P, (-8, -20, -8), (16, 17, 15))
    front('rocio', P, (-8, -20, -8.05), (16, 11, 0))
    box('hair_rocio', (-2, -19.6, 6.0), (4, 3, 2), mat=ribbon_mat, name='scrunchie', inflate=0.35, style='rocio',
        pal=MAROON)
    bone('rocio_tail', (0, -18.6, 7.4), parent='hair_rocio', rot=(36, 0, 0), mat=hairbit_mat)
    box('rocio_tail', (-2, -18.8, 6.0), (4, 4, 3), name='tail', style='rocio', pal=P)
    bone('rocio_tail_tip', (0, -14.8, 7.4), parent='rocio_tail', rot=(-36, 0, 0), mat=hairbit_mat)
    box('rocio_tail_tip', (-1.5, -15.0, 6.12), (3, 8, 3), name='tail', style='rocio', pal=P)
    box('rocio_tail_tip', (-1.0, -7.2, 6.4), (2, 4, 2), name='tail_tip', style='rocio', pal=P)

    # Chela: a big cloud of tight ringlets
    P = CHESTNUT
    bone('hair_chela', HC, parent='head', mat=shell_mat)
    shell('chela', P, (-10, -22, -9), (20, 19, 18), split=4.0)
    front('chela', P, (-10, -22, -9.05), (20, 18, 0))
    # (clump faces flush against the cloud are left transparent by hairbit_mat; the fractional offsets keep any two
    #  clumps from sharing a plane)
    for (fx, fy, fz), (sw, sh, sd) in (((-12, -18, -5), (2, 5, 6)), ((10, -17, -4), (2, 6, 6)),
                                       ((-12, -10, -2), (2, 5, 6)), ((10, -9, -1), (2, 5, 6)),
                                       ((-5, -24, -4), (8, 2, 7)), ((-6, -14, 9), (12, 7, 1)),
                                       ((-11, -3.85, -3), (3, 4, 5)), ((8, -3.85, -2), (3, 4, 5)),
                                       ((-9, -23, 2), (5, 2, 5)), ((4, -23, -6), (5, 2, 5)),
                                       ((-12.15, -9.15, 3.15), (3, 6, 5)), ((9.15, -9.15, 3.15), (3, 6, 5))):
        box('hair_chela', (fx, fy, fz), (sw, sh, sd), mat=hairbit_mat, name='clump', style='chela', pal=P)
    # ringlet tubes turned 45 deg round the four vertical corners of the cloud: a bumpy, rounded outline
    bone('chela_curls', (0, -12.0, 0), parent='hair_chela', rot=(0, 45, 0), mat=hairbit_mat)
    cs = math.sqrt(0.5)
    for (qx, qz), (ty, th) in (((-9.6, 8.6), (-19.0, 13)), ((9.6, 8.6), (-20.0, 14)),
                               ((-9.8, -8.0), (-21.0, 9)), ((9.8, -8.0), (-20.0, 8))):
        # place the 3x3 tube so that, after the bone's 45 deg yaw, its centre lands on (qx, qz)
        lx_ = qx * cs - qz * cs
        lz_ = qx * cs + qz * cs
        box('chela_curls', (lx_ - 1.5, ty, lz_ - 1.5), (3, th, 3), name='tube', style='chela', pal=P)

    # Ofelia: long dead-straight blue-black hair, Alice band, locks over the shoulders, back curtain
    P = BLUEBLACK
    bone('hair_ofelia', HC, parent='head', mat=shell_mat)
    shell('ofelia', P, (-8.5, -20, -8), (17, 17, 15))
    front('ofelia', P, (-8.5, -20, -8.05), (17, 17, 0))
    # Alice band: maroon velvet across the crown, set 2 texels back from the hairline (no inflate: never wider than
    # the head); its ends are painted on the shell running down behind the ears
    box('hair_ofelia', (-8.5, -20.9, -6.0), (17, 1, 3), mat=ribbon_mat, name='band', style='ofelia', pal=BAND)
    box('hair_ofelia', (-8.6, -6, -6.5), (3, 13, 2), mat=hairbit_mat, name='lock', style='ofelia', pal=P)
    box('hair_ofelia', (5.6, -6, -6.5), (3, 13, 2), mat=hairbit_mat, name='lock', style='ofelia', pal=P)
    bone('ofelia_curtain', (0, -6.0, 6.0), parent='hair_ofelia', rot=(8, 0, 0), mat=hairbit_mat)
    box('ofelia_curtain', (-7.5, -6.0, 5.0), (15, 17, 2), name='curtain', style='ofelia', pal=P)

    # Ana Sofia: centre parting, two high pigtails with red elastics
    P = BROWN
    bone('hair_anasofia', HC, parent='head', mat=shell_mat)
    shell('anasofia', P, (-8, -20, -8), (16, 17, 15))
    front('anasofia', P, (-8, -20, -8.05), (16, 5, 0))
    for side, sx in (('right', -1), ('left', 1)):
        t1, t2 = f'anasofia_tail_{side}', f'anasofia_tail_{side}_tip'
        px = 8.2 * sx
        box('hair_anasofia', (px - 1, -18.0, -0.5), (2, 3, 3), mat=ribbon_mat, name='elastic', inflate=0.2,
            style='anasofia', pal=RED)
        bone(t1, (px, -16.5, 1.0), parent='hair_anasofia', rot=(0, 0, -100 * sx), mat=hairbit_mat)
        box(t1, (px - 1.5, -16.5, -0.5), (3, 6, 3), name='pigtail', style='anasofia', pal=P)
        bone(t2, (px, -11.0, 1.0), parent=t1, rot=(0, 0, 58 * sx), mat=hairbit_mat)
        box(t2, (px - 1.5, -11.3, -0.38), (3, 7, 3), name='pigtail_tip', style='anasofia', pal=P)

    # Lola: black pixie cut, side-swept fringe, huge crimson satin bow on the top-left of the head
    P = BLACK
    bone('hair_lola', HC, parent='head', mat=shell_mat)
    shell('lola', P, (-8, -20, -8), (16, 17, 15))
    front('lola', P, (-8, -20, -8.05), (16, 9, 0))
    bone('lola_bow', (4.5, -20.5, -8.0), parent='hair_lola', rot=(-6, 0, -10), mat=ribbon_mat)
    box('lola_bow', (3.0, -22.0, -9.6), (3, 3, 3), name='big_knot', style='lola', pal=BOWRED)
    box('lola_bow', (-3.0, -23.5, -9.0), (6, 6, 2), name='big_loop', side='r', style='lola', pal=BOWRED)
    box('lola_bow', (6.0, -23.5, -9.0), (6, 6, 2), name='big_loop', side='l', style='lola', pal=BOWRED)
    # the two ribbon tails lie flat along the left side of the head (never over the forehead)
    box('hair_lola', (8.12, -19.0, -7.2), (0, 7, 2), mat=ribbon_mat, name='big_tail', side='r', style='lola',
        pal=BOWRED)
    box('hair_lola', (8.16, -18.5, -4.6), (0, 6, 2), mat=ribbon_mat, name='big_tail', side='l', style='lola',
        pal=BOWRED)

    m = AlumnaModel('alumna', 256, 256, r.roots)
    m.scale = 0.5
    m.render_type = 'entityTranslucent'
    if show is not None:
        m.show = show
    return m


POSES = {
    # hands joined in front of the skirt, head lowered a little: the obedient pupil
    'stand': {'head': (0.12, 0, 0.04, 0, 0, 0), 'right_arm': (-0.302, 0.251, -0.263, 0, 0, 0),
             'right_forearm': (-0.169, 0, -0.901, 0, 0, 0), 'right_hand': (0.301, 0.557, 0.364, 0, 0, 0),
             'left_arm': (-0.297, -0.215, 0.248, 0, 0, 0), 'left_forearm': (-0.202, 0, 0.894, 0, 0, 0),
             'left_hand': (0.309, -0.578, -0.363, 0, 0, 0)},
    # choir: chin up, prayer hands at the chest
    'sing': {'neck': (-0.08, 0, 0, 0, 0, 0), 'head': (-0.28, 0, 0.06, 0, 0, 0),
            'right_arm': (-0.386, 0.293, -0.733, 0, 0, 0), 'right_forearm': (-0.482, 0, -1.158, 0, 0, 0),
            'right_hand': (0.343, 1.327, -0.614, 0, 0, 0), 'left_arm': (-0.386, -0.294, 0.733, 0, 0, 0),
            'left_forearm': (-0.481, 0, 1.158, 0, 0, 0), 'left_hand': (0.343, -1.327, 0.614, 0, 0, 0)},
    # at the desk: knees at 90 degrees, skirt draped on the lap, hands folded on the desk top, head tilted
    'sit_desk': {'body': (0, 0, 0, 0, 6, 0), 'right_leg': (-1.57, 0.08, 0, 0, 0, 0),
                'right_shin': (1.57, 0, 0, 0, 0, 0), 'left_leg': (-1.57, -0.08, 0, 0, 0, 0),
                'left_shin': (1.57, 0, 0, 0, 0, 0), 'skirt_front': (-1.22, 0, 0, 0, 0.0, 4.5),
                'skirt_back': (-1.38, 0, 0, 0, 0, 0), 'skirt_right': (0, 0.14, -0.04, 0.35, -5.0, -1.5),
                'skirt_left': (0, -0.14, 0.04, -0.35, -5.0, -1.5), 'right_arm': (-0.363, 0.32, -0.311, 0, 0, 0),
                'right_forearm': (-0.531, 0, -1.156, 0, 0, 0), 'right_hand': (0.563, 0.412, -0.257, 0, 0, 0),
                'left_arm': (-0.351, -0.228, 0.268, 0, 0, 0), 'left_forearm': (-0.626, 0, 1.128, 0, 0, 0),
                'left_hand': (0.552, -0.456, 0.254, 0, 0, 0), 'head': (0.05, 0, 0.18, 0, 0, 0)},
    # punished: forehead against the wall, shoulders dropped, arms hanging dead
    'face_wall': {'body': (0.1, 0, 0, 0, 0, -0.5), 'neck': (0.2, 0, 0, 0, 0, 0), 'head': (0.42, 0, 0.08, 0, 0, 0),
                 'right_leg': (-0.1, 0, 0, 0, 0, 0), 'left_leg': (-0.1, 0, 0, 0, 0, 0),
                 'right_arm': (0.296, 0.183, 0.01, 0, 1, 0), 'left_arm': (0.293, -0.031, 0.026, 0, 1, 0),
                 'right_forearm': (-0.567, 0, -0.531, 0, 0, 0), 'left_forearm': (-0.65, 0, 0.412, 0, 0, 0),
                 'right_hand': (0.307, 0.163, 0.262, 0, 0, 0), 'left_hand': (0.356, -0.334, -0.243, 0, 0, 0),
                 'rocio_tail_tip': (-0.12, 0, 0, 0, 0, 0), 'ofelia_curtain': (-0.6, 0, 0, 0, 0, 0)},
    # the right arm straight at the player, index out, the other fingers curled
    'point': {'head': (0.05, 0, 0.3, 0, 0, 0), 'right_arm': (-1.5, 0.05, -0.26, 0, 0, 0),
              'right_forearm': (0.1, 0, 0.07, 0, 0, 0), 'right_hand': (0, 0.611, 0, 0, 0, 0),
              'right_fingers': (0, 0, -1.4, 0, 0, 0), 'paloma_braid_right': (0.3, 0, -0.12, 0, 0, 0)},
    # crouched and cowering, shoulders hunched up 1.6, elbows forward and down, both palms pressed flat on the OUTSIDE
    # of the hair over the ears (16-wide styles: palms at x = +-9..10), the long fingers wrapping back over the sides of
    # the head (never above the crown).  Wider hair: use 'cover_ears_mecha' / '_ofelia' / '_chela' (same body).
    'cover_ears': {'body': (0.25, 0, 0, 0, 2.09, 0), 'right_leg': (-0.7, 0, 0, 0, 0, 0),
                  'left_leg': (-0.7, 0, 0, 0, 0, 0), 'right_shin': (1.2, 0, 0, 0, 0, 0),
                  'left_shin': (1.2, 0, 0, 0, 0, 0), 'right_shoe': (-0.75, 0, 0, 0, 0, 0),
                  'left_shoe': (-0.75, 0, 0, 0, 0, 0), 'neck': (0.12, 0, 0, 0, 0, 0), 'head': (0.3, 0, 0, 0, 0, 0),
                  'right_arm': (-1.885, 0.322, -0.284, 0.3, -1.6, 0), 'right_forearm': (-1.122, 0.325, -0.218, 0, 0, 0),
                  'right_hand': (-0.598, 0.594, -0.141, 0, 0, 0), 'left_arm': (-1.885, -0.322, 0.284, -0.3, -1.6, 0),
                  'left_forearm': (-1.122, -0.325, 0.218, 0, 0, 0), 'left_hand': (-0.598, -0.594, 0.141, 0, 0, 0),
                  'rocio_tail_tip': (-0.1, 0, 0, 0, 0, 0), 'ofelia_curtain': (-0.45, 0, 0, 0, 0, 0)},
    # the thumbnail shot: neck + head yaw sum to pi
    'head_180': {'neck': (0, 0.5, 0, 0, 0, 0), 'head': (0, 2.64, 0.12, 0, 0, 0)},
    # Hora Muerta: running ahead lighting candles (contact frame)
    'run': {'body': (0.2, 0, 0, 0, 1.53, 0), 'head': (-0.15, 0, 0, 0, 0, 0), 'right_leg': (-0.9, 0, 0, 0, 0, 0),
           'right_shin': (0.9, 0, 0, 0, 0, 0), 'right_shoe': (-0.2, 0, 0, 0, 0, 0), 'left_leg': (0.6, 0, 0, 0, 0, 0),
           'left_shin': (1.2, 0, 0, 0, 0, 0), 'left_shoe': (0.35, 0, 0, 0, 0, 0),
           'right_arm': (1.109, 0.065, 0.131, 0, 0, 0), 'right_forearm': (-0.948, 0, -0.376, 0, 0, 0),
           'left_arm': (-0.619, -0.095, 0.081, 0, 0, 0), 'left_forearm': (-1.094, 0, 0.376, 0, 0, 0),
           'skirt_back': (0.25, 0, 0, 0, 0, 0), 'skirt_front': (-0.1, 0, 0, 0, 0, 0),
           'paloma_braid_right': (0.5, 0, 0, 0, 0, 0), 'paloma_braid_left': (0.6, 0, 0, 0, 0, 0),
           'rocio_tail': (0.45, 0, 0, 0, 0, 0), 'rocio_tail_tip': (0.36, 0, 0, 0, 0, 0),
           'ofelia_curtain': (0.35, 0, 0, 0, 0, 0),
           'right_hand': (0.155, 0.215, 0.019, 0, 0, 0), 'left_hand': (0.11, -0.224, -0.011, 0, 0, 0)},
    # leaning out sideways TOWARD the doorframe on her left (+X: in MC a positive body zRot tips the top toward +X =
    # her left), the left hand gripping the frame edge outside her silhouette at chest height (palm centre x 13.4,
    # y 5.2, z -4.5, palm facing -X onto the jamb, fingers pointing forward and curled -X around its front edge,
    # stacked index-on-top); the right arm hangs plumb; the head tilts on out past the edge
    'peek': {'body': (0, 0, 0.42, 0, 0.9, 0), 'right_leg': (0, 0, -0.36, 0, 0, 0),
            'left_leg': (-0.56, 0, -0.48, 0, 0, 0), 'left_shin': (1.12, 0, 0, 0, 0, 0),
            'left_shoe': (-0.56, 0, 0, 0, 0, 0), 'neck': (0, 0, 0.05, 0, 0, 0), 'head': (0.05, 0, 0.12, 0, 0, 0),
            'left_arm': (-1.055, -1.761, -0.163, 0, 0, 0), 'left_forearm': (-0.332, 0.266, 2.038, 0, 0, 0),
            'left_hand': (0.61, -0.322, -0.199, 0, 0, 0), 'left_fingers': (0, 0, 1.3, 0, 0, 0),
            'left_index': (0, 0, 1.1, 0, 0, 0), 'right_arm': (0.2, 0.1, -0.33, 0, 0, 0),
            'right_forearm': (-0.35, 0, -0.3, 0, 0, 0), 'right_hand': (0.15, 0.15, 0.1, 0, 0, 0)},
    # arms out to the sides to hold hands in the ring
    'ronda': {'right_arm': (0.182, 0.121, 1.095, 0, 0, 0), 'left_arm': (0.183, -0.243, -1.11, 0, 0, 0),
             'right_forearm': (-0.519, 0, -0.567, 0, 0, 0), 'right_hand': (0.238, 0.266, 0.209, 0, 0, 0),
             'left_forearm': (-0.441, 0, 0.632, 0, 0, 0), 'left_hand': (0.21, -0.154, -0.221, 0, 0, 0)},
    # rayuela hop: one leg up behind, arms out for balance
    'hop': {'body': (0, 0, 0, 0, -1.5, 0), 'left_leg': (-0.5, 0, 0, 0, 0, 0), 'left_shin': (1.6, 0, 0, 0, 0, 0),
           'right_arm': (0.376, 0.042, 0.804, 0, 0, 0), 'left_arm': (0.379, -0.161, -0.844, 0, 0, 0),
           'right_forearm': (-0.538, 0, -0.547, 0, 0, 0), 'right_hand': (0.245, 0.302, 0.208, 0, 0, 0),
           'left_forearm': (-0.459, 0, 0.618, 0, 0, 0), 'left_hand': (0.216, -0.184, -0.22, 0, 0, 0)},
    # the right arm raised beside the head (Laudes goodbye)
    'wave': {'right_arm': (-0.495, 1.139, 1.515, 0, 0, 0), 'right_forearm': (-0.668, 0, 0.497, 0, 0, 0),
            'right_hand': (0.397, 0.417, -0.122, 0, 0, 0), 'head': (0, 0, -0.15, 0, 0, 0)},
    # the "O" mouth slid flush onto the face + chin up (only after the final chorus)
    'freed': {'head': (-0.1, 0, 0, 0, 0, 0), 'jaw': (0, 0, 0, 0, 0, -1.6)},
}

# cover_ears for the wider hairstyles: same crouch, the arms re-solved so the palms land flat on the outside of that
# hair at ear height (mecha bob +-9, ofelia +-8.5, chela's curl clumps +-12).  Java: POSES.get("cover_ears_" + hair),
# falling back to "cover_ears" for paloma / rocio / anasofia / lola.
COVER_EARS_ARMS = {
    'mecha': {'right_arm': (-1.963, 0.337, -0.456, 0.3, -1.6, 0), 'right_forearm': (-1.023, 0.321, -0.245, 0, 0, 0),
              'right_hand': (-0.613, 0.566, -0.257, 0, 0, 0)},
    'ofelia': {'right_arm': (-1.973, 0.246, -0.554, 0.3, -1.6, 0), 'right_forearm': (-1.041, 0.194, -0.352, 0, 0, 0),
               'right_hand': (-0.576, 0.441, -0.202, 0, 0, 0)},
    'chela': {'right_arm': (-2.298, 0.601, -0.714, 0.3, -1.6, 0), 'right_forearm': (-0.514, 0.727, -0.338, 0, 0, 0),
              'right_hand': (-0.719, 0.329, -0.488, 0, 0, 0)},
}
for _hair, _arms in COVER_EARS_ARMS.items():
    _p = dict(POSES['cover_ears'])
    for _b, _v in _arms.items():
        _p[_b] = _v
        _p[_b.replace('right_', 'left_')] = (_v[0], -_v[1], -_v[2], -_v[3], _v[4], _v[5])   # mirrored
    POSES['cover_ears_' + _hair] = _p

ANIM_NOTES = """Las Alumnas del Coro -- animation notes.  Units: radians, offsets in model texels (2x density inside
scale_root: 2 texels = 1 vanilla pixel).  t = ageInTicks, s = walk speed 0..1.  Every POSES entry is ADDED to the rest
pose; blend between poses over 4-6 ticks unless a note says SNAP (1-2 ticks).

Variants and toggles (synced data: variant 0..6, freed, pose)
* Exactly one hair group is visible: variant 0 hair_paloma, 1 hair_mecha, 2 hair_rocio, 3 hair_chela, 4 hair_ofelia,
  5 hair_anasofia, 6 hair_lola.  Every frame: for each part in group("hair_") set visible = (name == HAIRS[variant])
  (hiding a group hides its child bones too).  The order is the same as the HAIRS list in ent_alumna.py.
* Pose variants by hairstyle: for 'cover_ears' use POSES "cover_ears_" + hair when it exists (mecha, ofelia, chela:
  the same crouch with the arms re-solved so the palms land on the outside of their wider hair), else "cover_ears".
* jaw.visible = freed.  When freed, also apply POSE 'freed' (it slides the flat "O" mouth plane 1.6 texels forward to
  z -7.1, 0.1 in front of the face plate so it never z-fights; it is a zero-thickness plane, so it can never read as a
  box).  Never show the jaw before Laudes; the mouthless face IS
  the character.
* Render type entityTranslucent (texture alpha ~158-228: misty from the hem down, cold rim on the cloth/hair edges).
  Buried faces are already transparent in the texture; keep the model part order as exported (head cubes before the
  hair groups) so the dark skull acts as an occluder behind the hair.  Camera flash: render with alpha forced to 255 for the flash
  frames (they look solid) and set freed = true for that frame only (in the photo they have mouths).
* Emissive layer 'eyes': only the two 1-px socket glints (pale cyan).  Flicker their alpha 0.6-1.0 while a girl is
  singing backwards; switch them off for 3 ticks right before a head_180 snap.

Movement style: they are dead children, not zombies.  Idle is perfectly still except breathing-free, tiny "settle"
twitches; anything uncanny happens in SNAPS (1-2 ticks) while the player is not looking, then freezes.  Walking is a
light, too-even glide: the legs walk but the body has no bob at all (dy = 0), the arms do not swing.

Bones
* body (root, pivot at the waist): whole girl.  Idle: still; every 6-10 s a single 0.03 zRot settle.  Walk: no bob, no
  sway (that evenness is the creepy part).  Run: pose 'run' with a 0.08 xRot bounce on each footfall.
* body also carries the waist band ('core': only its dark underside is painted - it closes the bell of the skirt).
* skirt_front, skirt_back, skirt_right, skirt_left: the four 16 x 10 box-pleated panels of the guardapolvo, hinged at
  the waist seam (y 6.5; each panel starts 0.5 above the hinge so 2+ texels of pale knee show under the hem).  Idle:
  ripple("skirt_", t, 0.05, 1.4, 0.015, 0.01, 0).  Walk/run: the panel on the side of the forward leg opens -0.12 * s,
  skirt_back flares +0.25 in 'run'.  skirt_back carries the buttoned half-belt.  sit_desk: front laid on the lap (short
  overhang past the knees), back tucked under onto the seat (xRot -1.38), and the side panels (a 10 x 10 square cannot
  fold into the 5 texels between waist and seat) are lifted 5 (dy -5), yawed +-0.14 and slid forward 1.5 so they
  drape the hips from the waist to the seat line: nothing reaches below the seat, and from behind their back edges
  hide behind the smock.
* collar: the two Peter Pan collar planes (static, rest xRot -12 deg so they stand off the chest).  No animation.
* bow: the navy school bow at the throat (child of collar).  Secondary: zRot spring-lagged from body/head motion
  (+-0.08), xRot -0.15 in 'run'.
* right_leg / left_leg: thighs (hip joint).  Walk: xRot = +-sin(walk) * 0.5 * s.  Sit/crouch/hop: pose values.
* right_shin / left_shin: knee joint (pale knee band 3 texels + navy knee sock + turned-down cuff).  Walk: xRot = max(0, sin(walk + 1.2))
  * 0.6 * s (bend on the back-swing only).  sit_desk +1.57.
* right_shoe / left_shoe: ankle (black patent Mary-Janes).  Keep the sole flat: xRot = -(leg + shin) * 0.4 while
  walking; cover_ears -0.75 (soles flat in the crouch).
* right_arm / left_arm: shoulders (thin white sleeves, rest angled 15 deg out and 4 deg forward so the long hands
  hang clear of the skirt).  Idle: hanging dead still; no swing when walking.  Run: +-0.8 counter to the legs.
* right_forearm / left_forearm: elbows (forearm sleeve + cuff, 5 long).  Follow pose values only.
* right_hand / left_hand: wrists (cold palm + thumb; rest yRot 35 deg so the palms turn back and the splayed
  fingers read from the front).  Idle: a 0.04 zRot tremor on one hand every few seconds.
* right_fingers / left_fingers: the middle and ring fingers (two 1x5 cubes with a 1-texel gap).  zRot curls them
  toward the palm (right -1.4, left +1.4; the palm is the hand's +-X face, so zRot is the curl axis whatever the arm
  does): fist for 'point'; in 'peek' the hand points forward with the finger row stacked vertically, so the same zRot
  (+1.3 / index +1.1) wraps the fingers horizontally around the vertical frame edge.  Idle: slow 0.1 curl/uncurl,
  never both hands together.
* right_index / left_index: the 1x5 index finger (splayed 1 texel in front of the others), separate so 'point' can
  keep it straight while the others curl.
  In 'point' add a slow beckoning curl xRot 0..-0.5 on the right index after the pose has held 2 s.
* neck: takes 30% of the head look (yaw/pitch) and 0.5 of the yaw in 'head_180'.
* head: 70% of the head look; rest pose already tilted 6 deg toward her right shoulder and nodded 4 deg.
  Idle: hold, then every 5-12 s SNAP a +-0.25 zRot tilt in 2 ticks and hold it.  When the player comes within 3 blocks:
  SNAP 'head_180' (neck + head yaw = pi in 2 ticks, overshoot 0.1 and settle), giggle, then dissolve.
* jaw: the round singing "O" (a flat 4x4 plane: lips ring + black mouth).  Hidden (visible = false) unless freed;
  pose 'freed' slides it onto the face with dz -1.6 (z -7.1).  While freed and singing: dy oscillation 0..0.4 on the
  beat, never open wider.
* hair_paloma: centre-parted brown hair + the two braid roots behind the ears (rigid) + braids.  paloma_braid_right / paloma_braid_left: the upper plaits (hinged
  behind the ears, swung forward over the shoulders); paloma_braid_right_tip / paloma_braid_left_tip: lower plaits
  with the sky-blue ribbon bows and brush ends.  Pendulums: xRot/zRot spring-lag the head and body by 3-4 ticks
  (amplitude 0.1 idle, 0.5 back in 'run'); the tips lag the uppers by 2 more ticks.
* hair_mecha: black bob with bangs (stepped shell + bangs plane + ragged tips plane).  Rigid; no bones to animate.
  Every hair group is built the same way: two stepped shell boxes (the back one 0.5 narrower each side, 1 lower), a
  fringe plane and - except Chela and Ofelia - a zero-thickness 'tips' plane that breaks the lower back edge into
  uneven 1-3 texel strand ends.  All rigid with their group.
* hair_rocio: combed-back hair + the scrunchie at the back of the crown.  rocio_tail (the root: leaves the scrunchie
  at 36 deg) and rocio_tail_tip (the tapered fall, 3 then 2 wide with a ragged tip, hanging ~1 texel behind the back
  of the head): pendulum chain, 'run' +0.45 / +0.36 (streams back in one line), bounce 0.15 on each footfall, side
  swing zRot +-0.2 when the head snaps.  Gravity: the tail rests ON the back of the head, so when the head bows do
  NOT counter-rotate the root (that pushes it into the skull); only let the tip hang a little (rocio_tail_tip about
  -0.15 x the summed body + neck + head pitch: baked into 'face_wall' -0.12 and 'cover_ears' -0.1).
* hair_chela: the curly cloud (shell, fringe, ringlet clumps).  Rigid; on footfalls a 0.3 texel dy squash is enough.
  chela_curls: the four ringlet tubes on the corners of the cloud (bone yawed 45 deg to round the outline).  Static
  (never animate it on its own; it moves with hair_chela).
* hair_ofelia: long straight blue-black hair, the maroon velvet Alice band (a thin cube across the crown, 2 texels
  behind the hairline, its ends painted on the shell down behind the ears; no bone of its own) and
  the two locks over the shoulders (rigid with the head).  ofelia_curtain: the waist-long back curtain; lags the head (xRot spring) and lifts
  +0.35 in 'run'.  When the head bows it keeps hanging vertical: counter-rotate like rocio_tail ('face_wall' -0.6,
  'cover_ears' -0.45).
* hair_anasofia: centre parting + red elastics.  anasofia_tail_right / anasofia_tail_left: the high pigtails (stick
  out sideways); anasofia_tail_right_tip / anasofia_tail_left_tip: drooping ends.  Bounce zRot +-0.25 on every hop
  in 'hop' and on footfalls, opposite phase left/right.
* hair_lola: black pixie cut with a side-swept fringe; the two ribbon tails lie flat on the left side of the head
  (rigid with hair_lola).  lola_bow: the huge crimson satin bow (two up-tilted wings + dark knot); small spring wobble
  (zRot +-0.06) after head snaps.

Poses
* stand: hands joined in front of the skirt, head a little down.  Default pose in classrooms, refectory, locutorio.
* sing: chin up, prayer hands at the chest.  Choir (Completas, Maitines).  Combine with 'freed' at Laudes.
* sit_desk: knees at 90 deg, hands folded on the desk, head tilted.  body dy +6 puts the soles on the floor of the
  same block (seat 0.2 blocks above the floor); raise the entity 0.2 blocks for the classroom benches.  The front
  skirt panel lies on the thighs (1-2 texels past the knees), the back panel is tucked under her onto the seat, the
  side panels drape the hips down to the seat line (nothing goes below the seat, front or back view).
* face_wall: punished pupil: forehead on the wall, neck and head bowed, shoulders dropped 1 texel, arms hanging
  dead.  Place her 0.25 blocks from the wall.  Cripta at the Hora Muerta (before the 180 + "CORRE").
* point: the right arm straight at the player, index out, other fingers curled, head tilted.  Ronda beat ("...con
  esta SI") - all girls SNAP into it on the same tick.  (Paloma's right braid swings back 0.3 so the raised sleeve
  does not cut through it.)
* cover_ears: crouched (soles flat on the floor: shoes -0.75 cancel body + leg + shin pitch, body dy +2.09), head
  bowed (neck 0.12, head 0.3), shoulders hunched up 1.6 (arm dy -1.6, dx 0.3 inward), elbows forward and down in front
  of the chest, both palms pressed flat on the OUTSIDE of the hair over the ears (16-wide styles: palm centres at
  head-local x +-9.5, y -10) and turned ~12 deg so the backs of the hands show from the front, the long fingers
  wrapping back over the sides of the head (never above the crown).  Per hairstyle: paloma / rocio / anasofia / lola
  'cover_ears'; mecha (bob +-9) 'cover_ears_mecha'; ofelia (+-8.5) 'cover_ears_ofelia'; chela (curl clumps +-12)
  'cover_ears_chela' - same body/legs/head values, only the six arm bones differ (if a renderer prefers one pose plus
  an offset: add about -0.08 (right) / +0.08 (left) arm zRot per texel of extra hair width).  Warning when Sor Agonia
  hunts within 16 blocks ("shh, viene"), then dissolve.
* head_180: the thumbnail shot.  neck + head yaw sum to pi; SNAP all girls on the same tick when the flashlight hits
  the choir loft.  Works from any base pose (stand, sing, face_wall); body stays still.
* run: Hora Muerta, running ahead lighting candles; braids/ponytail/curtain fly back.  Contact frame: the front
  (right) sole is flat on the floor (body dy +1.53), the back foot kicked up toe-down.
* peek: leaning sideways TOWARD the doorframe on her left (body zRot +0.42: in MC a positive zRot tips the top toward
  +X, which is her left; legs counter-rotated -0.36 / -0.48 so the feet stay apart, body dy +0.9 and the left knee
  bent forward so both soles stay on the floor), neck/head tilting on out past the edge (0.05 / 0.12).  The left hand
  grips the frame edge OUTSIDE her silhouette at chest height (palm centre about x 13.4, y 5.2, z -4.5; palm facing
  -X onto the jamb, fingers pointing forward and curled around its front edge, stacked index-on-top; it never
  overlaps the face or neck from the front); the right arm hangs plumb.  Place her so the frame edge is at her left
  hand: her body behind the wall, half the face past the edge.  Corridors.
* ronda: arms out to the sides to hold hands in the ring (claustro).  Rotate the ring, not the girls.
* hop: rayuela hop (Paloma): one leg up behind, arms out for balance, body dy -1.5 at the top of the hop.
* wave: the right arm raised beside the head (Laudes goodbye); drive right_forearm zRot +-0.35 at 0.25 rad/tick.
* freed: the "O" mouth slid flush onto the face + chin up.  Only after the final chorus.
"""
