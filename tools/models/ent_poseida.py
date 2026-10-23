"""Lucia (8) -- the daughter of Casa Morales, host #3 of AZAMEL (DEAD LINE).  Two looks on one rig.

Authored at 2x texel density (model.scale = 0.5) with rig.Rig absolute coordinates: +Y down, ground at y = 24,
she faces -Z, right_* parts on -X.  Real height 1.5 blocks (top of the hair at y = -24).

Story: Lucia cut the 1961 stitches of the doll Ofelia, so the demon AZAMEL jumps into her (host #3, after the dog
and Jorge).  Until then she is a sweet, shy eight-year-old in her nightgown and the red sweater her Nona knitted
her; she hides under her bed and talks about Ofelia ('casa.cuarto_lucia').  Possessed she walks like a spider on
walls and ceiling and levitates ('casa.lucia'), until the Nona's slipper knocks the demon out of her and she sits
on the floor, dazed ('casa.chancleta').

Looks (VARIANT_MATS, index = the entity's variant)
* 0 'normal'  -> poseida.png.  Warm peach skin, rosy cheeks, big brown eyes with a glint, a shy closed smile,
  chestnut hair with a centre part, short bangs and two braids tied with the Nona's red yarn.  A cream nightgown
  with tiny pink rosebuds and white lace, under a baggy hand-knitted RED SWEATER with a cream heart on the chest,
  ribbed hem / cuffs / neck and sleeves so long they cover half her hands.  A darned patch on the left elbow and
  a band-aid on the left knee.  Clean bare feet.  Nothing glows.
* 1 'poseida' -> poseida_poseida.png (+ the emissive 'eyes' layer).  The original possessed design, kept: an
  oversized cracked-plaster head cocked at a broken angle inside a tangled black mane, a grin torn ear to ear
  (the jaw hinges along the cheek tears) full of yellow needle teeth, WHITE GLOWING EYES sunk in real recessed
  sockets, spider arms whose long black-nailed claws hang past the knees, the filthy ruffled nightgown with a
  shredded hem and black bile + blood vomited down the front, bruised veined knock-kneed legs and filthy bare
  pigeon-toed feet.  Plus the sweater: soot-black, the chest BURNED THROUGH where the heart was (charred curled
  lips, live embers on the rim that glow in the dark, the stained nightgown showing inside), the forearm sleeves
  burned off at the elbow so the veined spider forearms show.

Geometry that only exists in one look lives in toggle bones (see TOGGLE_DEFAULT / VARIANT_TOGGLES and the
'Toggles' section of ANIM_NOTES): braids + short child fingers (normal) vs. the mane curtain, the side locks, the
long claws and the burned lips (poseida).  Everything else is shared and only the texture changes (the burn hole,
the burned-off sleeves and the shredded hem are alpha cut-outs of the possessed texture).

Rig: base (pelvis) -> body -> neck -> head -> jaw; arms with forearm / hand -> claw (thumb + 4 finger bones) or
mitt; legs with shin / foot; the skirt hangs from base with four flared hem panels.  Every cube is authored in
its bone's unrotated frame (absolute authoring coordinates).
"""
import math
import os
import sys

import numpy as np

from mcmodel import Model, fbm, vnoise, hash3, face_light, pick, rot_matrix
from rig import Rig
from paint import hx, mix, scale


def pal(*h):
    return [hx(c) for c in h]


# ------------------------------------------------------------------ palettes (dark -> light, hue shifted)
# possessed (the original look)
SKIN = pal('#0f0c13', '#1f1a26', '#332d3b', '#4a4452', '#645e6b', '#827c86', '#a19ba2', '#beb9bb', '#d8d4d0', '#ece8e1')
GOWN = pal('#1f1b19', '#332e2a', '#4b443e', '#665e55', '#82796e', '#9f9588', '#bab1a2', '#d1c9b9', '#e4ddcd', '#f2ecdf')
LACE = pal('#4a453f', '#77716a', '#a39d92', '#cbc4b7', '#e9e3d6', '#faf6ec')
BLOOD = pal('#140103', '#280306', '#41060a', '#5e0a10', '#7c1016', '#9a1b1f')
BILE = pal('#050504', '#0c0b08', '#16140d', '#221f14', '#302c1c')
HAIR = pal('#020203', '#060508', '#0b0a0e', '#121016', '#1a171f', '#24202b', '#322d3b', '#463f52')
MOUTH = pal('#020102', '#0a0304', '#170508', '#2a090e', '#420f16', '#5d1820', '#7a242b')
TEETH = pal('#2f2718', '#4f432b', '#766540', '#9d8a58', '#bfae76', '#dacd98', '#ece4bc')
NAIL = pal('#0e0b09', '#1d1712', '#30271e', '#463a2c')
DIRT = pal('#120d09', '#211810', '#322519', '#453523', '#5a4730')
BRUISE = pal('#2a1a30', '#3e2a46', '#56405c', '#6d6250', '#7d7a62')
VEIN = hx('#170b1b')
VEIN2 = hx('#2e1a33')
# normal look
SKIN_N = pal('#3b211f', '#5f3631', '#87534a', '#ad7666', '#cc9580', '#e2b39c', '#f0cbb5', '#f9e1cf', '#fdf0e4')
GOWN_N = pal('#4a3d3d', '#6d5c5a', '#93807c', '#b5a39d', '#d0c1ba', '#e4d8d1', '#f2ebe5', '#fbf7f2')
LACE_N = pal('#8f8580', '#b3aaa4', '#d2cbc5', '#e9e4df', '#f7f4f0', '#ffffff')
HAIR_N = pal('#140a06', '#22110a', '#341a0f', '#4a2615', '#61331c', '#7a4325', '#94572f', '#b0713f')
IRIS = pal('#1c0d07', '#3e200f', '#653a1c', '#8c5a2c', '#b07a40')
SCLERA = (hx('#f7f2ed'), hx('#dccfc8'))
LASH = (hx('#1f0f0b'), hx('#4a2a20'))
BROW_N = (hx('#5a3320'), hx('#7d4c31'))
BLUSH = hx('#ec8f8c')
LIP_N = pal('#9c3f4a', '#c4606a', '#e08b8c')
SPRIG = (hx('#e48fa2'), hx('#c4677f'), hx('#9cb58f'))          # rosebud, its shadow, the tiny leaf
RIBBON_N = pal('#6a2238', '#93354f', '#bb5470', '#dc7e96', '#f2a9bb')
BANDAID = pal('#b88a62', '#d4a77c', '#e9c49a')
# the Nona's red wool (sweater, hair ties) + its cream heart; burned
KNIT = pal('#22040a', '#3d0810', '#5c0f17', '#7d1a1f', '#9c2626', '#b93630', '#d04d3d', '#e36d55', '#f09577')
CREAM = pal('#6d5d4a', '#958369', '#b9a88a', '#d7c9ab', '#ebe0c7', '#f7f0de')
CHAR = pal('#060404', '#110b09', '#1d130e', '#2c1d14', '#3f2a1c')
EMBER = pal('#4a0a04', '#8c1d08', '#d2420f', '#ff7a22', '#ffc060')
GLOW_EYE = (hx('#ffffff'), hx('#e6ecff'), hx('#b8c4e8'))

LOOKS = ('normal', 'poseida')
_LOOK = ['normal']                       # set by LuciaModel.paint from the material's .look


def poss():
    return _LOOK[0] == 'poseida'


def clamp(v, a=0.0, b=1.0):
    return a if v < a else b if v > b else v


# ------------------------------------------------------------------ texel helpers
def local(ctx):
    """Texel centre in the cube's bone frame (unrotated, relative to the bone pivot)."""
    c = ctx.cube
    x0, y0, z0 = c.origin
    w, h, d = c.size
    x1, y1, z1 = x0 + w, y0 + h, z0 + d
    s, t, f = ctx.s, ctx.t, ctx.face
    if f == 'front':
        return x0 + s * w, y0 + t * h, z0
    if f == 'back':
        return x1 - s * w, y0 + t * h, z1
    if f == 'west':
        return x0, y0 + t * h, z1 - s * d
    if f == 'east':
        return x1, y0 + t * h, z0 + s * d
    if f == 'top':
        return x0 + s * w, y0, z1 - t * d
    return x0 + s * w, y1, z1 - t * d


def face_point(frm, size, face, s, t):
    """Same mapping as local(), in absolute authoring coordinates (used by the emissive decals)."""
    x0, y0, z0 = frm
    w, h, d = size
    if face == 'front':
        return x0 + s * w, y0 + t * h, z0
    if face == 'back':
        return x0 + w - s * w, y0 + t * h, z0 + d
    if face == 'west':
        return x0, y0 + t * h, z0 + d - s * d
    if face == 'east':
        return x0 + w, y0 + t * h, z0 + s * d
    if face == 'top':
        return x0 + s * w, y0, z0 + d - t * d
    return x0 + s * w, y0 + h, z0 + d - t * d


def dpos(ctx):
    """Authoring-space position of the texel (bone abs pivot + local): ignores rest rotations."""
    lx, ly, lz = local(ctx)
    a = ctx.bone.abs
    return a[0] + lx, a[1] + ly, a[2] + lz


def edge(ctx):
    return min(ctx.i, ctx.j, ctx.w - 1 - ctx.i, ctx.h - 1 - ctx.j)


def flat(ctx):
    return 0 in ctx.cube.size


def is_side(ctx):
    return ctx.face not in ('top', 'bottom')


def tag(ctx):
    return ctx.cube.name or ''


def uv2(ctx, p):
    """2D painting coordinates on the face plane (authoring space)."""
    x, y, z = p
    if ctx.face in ('front', 'back'):
        return x, y
    if ctx.face in ('west', 'east'):
        return z, y
    return x, z


def worley(u, v, seed):
    xi, yi = math.floor(u), math.floor(v)
    d1 = d2 = 9.0
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            cx, cy = xi + dx, yi + dy
            px = cx + 0.15 + 0.7 * hash3(cx, cy, 0, seed)
            py = cy + 0.15 + 0.7 * hash3(cx, cy, 1, seed)
            d = math.hypot(px - u, py - v)
            if d < d1:
                d1, d2 = d, d1
            elif d < d2:
                d2 = d
    return d1, d2


def crack(ctx, p, cell=5.5, seed=3, width=0.1, density=0.52):
    """Plaster crack network: 1 = crack line, 2 = chipped lit lip below it, 0 none."""
    if flat(ctx):
        return 0
    u, v = uv2(ctx, p)
    if fbm(u * 0.11 + 7, v * 0.11, ord(ctx.face[0]) * 0.3, 2, seed + 40) < density:
        return 0
    d1, d2 = worley(u / cell, v / cell, seed)
    if d2 - d1 < width:
        return 1
    d1b, d2b = worley(u / cell, (v - 1) / cell, seed)
    if d2b - d1b < width:
        return 2
    return 0


def veins(ctx, p, cell=2.6, seed=11, width=0.09):
    u, v = uv2(ctx, p)
    d1, d2 = worley(u / cell, v / cell, seed)
    return d2 - d1 < width


# ------------------------------------------------------------------ skin
LIMB = ('_arm', '_forearm', '_hand', '_leg', '_shin', '_foot', '_finger', '_thumb', '_mitt')


def skin_value(ctx, p, base=0.62):
    v = base + face_light(ctx) * 1.15
    if not flat(ctx) and edge(ctx) == 0:
        v -= 0.07
    x, y, z = p
    v += (vnoise(x * 0.12, y * 0.12, z * 0.12, 5) - 0.5) * 0.12
    return v


def vein_mask(ctx, p):
    """0..1 how strongly the black spider-web veins show here."""
    n = ctx.bone.name
    x, y, z = p
    if n == 'neck':
        return 0.9
    if n.endswith('_forearm'):
        return 0.55 + 0.4 * clamp((y - 6) / 9)
    if n.endswith('_arm'):
        return 0.35
    if n.endswith('_hand'):
        return 0.6
    if n.endswith('_shin'):
        return 0.35
    if n.endswith('_leg'):
        return 0.25
    if n == 'body':
        return 0.5
    return 0.0


def bruise_at(ctx, p):
    """Hand-placed bruises: finger marks round the neck, grip marks on the arms, battered knees."""
    n = ctx.bone.name
    x, y, z = p
    if n == 'neck' and ctx.face in ('west', 'east', 'front'):
        k = (z + 2) / 1.3 if ctx.face != 'front' else (abs(x) + 1.0)
        if ctx.face == 'front':
            return 2 if abs(x) > 1 and -5 < y < -3 else 0
        if int(k) % 2 == 0 and -5.5 < y < -2.5:
            return 2 if -5 < y < -3 else 1
        return 0
    if n.endswith('_arm') and 1.5 < y < 5 and ctx.face in ('front', 'west', 'east'):
        u, _ = uv2(ctx, p)
        return 2 if int(math.floor(u * 0.9 + 5)) % 2 == 0 else 1
    if n.endswith('_shin') and y < 18 and ctx.face in ('front', 'west', 'east'):
        b = fbm(x * 0.4 + 3, y * 0.4, z * 0.4, 2, 61)
        return 2 if b > 0.6 else (1 if b > 0.53 else 0)
    if n.endswith('_leg') and ctx.face in ('front', 'west', 'east'):
        b = fbm(x * 0.35, y * 0.35 + 9, z * 0.35, 2, 63)
        return 2 if b > 0.62 else (1 if b > 0.56 else 0)
    if n.endswith('_forearm') and ctx.face == 'west' and 10 < y < 13:
        return 1
    return 0


def dirt_amount(ctx, p):
    n = ctx.bone.name
    x, y, z = p
    if n.endswith('_foot'):
        return 0.55 + 0.4 * clamp((y - 22) / 2)
    if n.endswith('_shin'):
        return clamp((y - 17) / 5) * 0.6
    if n.endswith('_hand') or '_finger' in n or '_thumb' in n:
        return 0.35
    if n.endswith('_forearm'):
        return clamp((y - 11) / 4) * 0.3
    return 0.0


def skin_n(ctx, p, base=0.6):
    """Normal look: warm healthy child skin, soft shading, rosy knees and knuckles, a band-aid on the left knee."""
    x, y, z = p
    n = ctx.bone.name
    v = base + face_light(ctx) * 1.05
    if not flat(ctx) and edge(ctx) == 0:
        v -= 0.06
    v += (vnoise(x * 0.15, y * 0.15, z * 0.15, 5) - 0.5) * 0.05
    if n.endswith(LIMB) and is_side(ctx) and not flat(ctx):
        v -= ctx.t * 0.05
    if n == 'neck':
        v -= 0.14
    c = pick(SKIN_N, v)
    if n.endswith('_shin') and ctx.face in ('front', 'west', 'east') and y < 17.0:
        c = mix(c, BLUSH, 0.22)
        if n == 'left_shin' and ctx.face == 'front' and 15.2 < y < 16.9:
            lx = x - ctx.bone.abs[0]
            if -1.6 < lx < 1.4:
                c = BANDAID[2] if 15.6 < y < 16.4 and abs(lx + 0.1) < 0.6 else BANDAID[1]
                if (ctx.i + ctx.j) % 3 == 0 and not (abs(lx + 0.1) < 0.6):
                    c = BANDAID[0]
    if n.endswith('_foot') and (ctx.face == 'bottom' or (is_side(ctx) and ctx.j >= ctx.h - 1)):
        c = mix(c, hx('#8f7368'), 0.35)                 # a little floor dust on the soles
    return c


def skin_mat(ctx):
    p = dpos(ctx)
    if not poss():
        return skin_n(ctx, p)
    x, y, z = p
    n = ctx.bone.name
    v = skin_value(ctx, p)
    limb = n.endswith(LIMB)
    if limb and is_side(ctx) and not flat(ctx):
        v -= ctx.t * 0.06
    if n == 'neck':
        v -= 0.1  # in the shadow of the huge head
    c = pick(SKIN, v)
    vm = vein_mask(ctx, p)
    if vm > 0 and not flat(ctx) and veins(ctx, p) and fbm(x * 0.2, y * 0.2, z * 0.2, 2, 13) < vm:
        c = mix(c, VEIN, 0.75)
    else:
        k = crack(ctx, p)
        if k == 1:
            c = pick(SKIN, v - 0.32)
        elif k == 2:
            c = pick(SKIN, v + 0.1)
    b = bruise_at(ctx, p)
    if b:
        c = mix(c, BRUISE[1] if b == 2 else BRUISE[3], 0.6 if b == 2 else 0.45)
    d = dirt_amount(ctx, p)
    if d > 0:
        dn = fbm(x * 0.5, y * 0.5, z * 0.5, 2, 71)
        if dn < d:
            c = mix(c, pick(DIRT, v * 0.7), 0.75)
    return c


def knob_mat(ctx):
    """Possessed: skin stretched over sharp bone (elbows, knees).  Normal: the knee is skin, the elbow is the knitted
    elbow of the sweater (the left one darned by the Nona)."""
    p = dpos(ctx)
    if not poss():
        if ctx.bone.name.endswith('_forearm'):
            return knit_core(ctx, p, rib=False, darn=ctx.bone.name.startswith('left'))
        c = skin_n(ctx, p, 0.64)
        return mix(c, BLUSH, 0.2) if is_side(ctx) else c
    v = skin_value(ctx, p, 0.66)
    if ctx.face == 'top' or (is_side(ctx) and ctx.j == 0):
        v += 0.1
    c = pick(SKIN, v)
    if is_side(ctx) and ctx.j == ctx.h - 1:
        c = mix(c, BRUISE[1], 0.5)
    d = dirt_amount(ctx, p)
    if d > 0.3:
        c = mix(c, DIRT[2], 0.4)
    return c


def finger_mat(ctx):
    """Long grey finger, dark knuckle creases, broken black nail at the tip (possessed claws)."""
    lx, ly, lz = local(ctx)
    L = ctx.cube.size[1]
    p = dpos(ctx)
    if not poss():
        return skin_n(ctx, p)
    v = skin_value(ctx, p, 0.6)
    if ly > L - 2.0:
        if ctx.face == 'bottom':
            return NAIL[0]
        return pick(NAIL, 0.4 + face_light(ctx) + (0.3 if ctx.face in ('front', 'east', 'west') and ly > L - 1 else 0))
    if int(ly) in (2, 4) and is_side(ctx):
        v -= 0.16
    v -= ly / L * 0.12
    c = pick(SKIN, v)
    if ly > L - 3.5:
        c = mix(c, DIRT[2], 0.55)
    return c


def mitt_mat(ctx):
    """Short child fingers held together (normal look): one shade per finger, pink tips, tiny nails."""
    t = tag(ctx)
    if poss():
        return skin_mat(ctx)
    lx, ly, lz = local(ctx)
    c0 = ctx.cube
    v = 0.62 + face_light(ctx) * 1.0
    depth = ly - c0.origin[1]
    if t == 'fingers':
        if ctx.face in ('west', 'east'):
            fi = int(math.floor(lz - c0.origin[2]))
            v += (0.05, -0.04, 0.03, -0.07)[fi % 4]
            if depth > c0.size[1] - 1 and fi in (1, 3):
                v -= 0.12                       # the middle fingers are longer: the others round off
        if ctx.face == 'bottom':
            v -= 0.1
        c = pick(SKIN_N, v - depth * 0.03)
        if depth > c0.size[1] - 1.0:
            c = mix(c, BLUSH, 0.3)
        if ctx.face == 'front' and depth > c0.size[1] - 1.0:
            c = mix(c, hx('#fbe7e0'), 0.6)      # nail
        return c
    # thumb
    c = pick(SKIN_N, v - 0.04)
    if depth > c0.size[1] - 1.0:
        c = mix(c, BLUSH, 0.3)
    return c


def foot_mat(ctx):
    """Bare foot: toes on the front, nails on the top row.  Possessed: grey, black soles.  Normal: clean and pink."""
    p = dpos(ctx)
    lx, ly, lz = local(ctx)
    toe_zone = (lz - ctx.cube.origin[2]) < 2.2
    if not poss():
        c = skin_n(ctx, p, 0.62)
        if ctx.face == 'bottom':
            return pick(SKIN_N, 0.42 + hash3(ctx.i, ctx.j, 0, 81) * 0.08)
        if ctx.face == 'front':
            if ctx.i % 2 == 1 and ctx.i < ctx.w - 1:
                return pick(SKIN_N, 0.4)
            if ctx.j == 0:
                return mix(c, hx('#fbe7e0'), 0.6)
            return mix(c, BLUSH, 0.25)
        if ctx.face == 'top' and toe_zone:
            if ctx.i % 2 == 1 and ctx.i < ctx.w - 1:
                return pick(SKIN_N, 0.45)
            if (lz - ctx.cube.origin[2]) < 1.0:
                return mix(c, hx('#fbe7e0'), 0.55)
        return c
    if ctx.face == 'bottom':
        return pick(DIRT, 0.2 + hash3(ctx.i, ctx.j, 0, 81) * 0.25)
    c = skin_mat(ctx)
    if ctx.face == 'front':
        if ctx.i % 2 == 1 and ctx.i < ctx.w - 1:
            return pick(DIRT, 0.3)
        if ctx.j == 0:
            return NAIL[2]
        return mix(c, DIRT[3], 0.5)
    if ctx.face == 'top' and toe_zone:
        if ctx.i % 2 == 1 and ctx.i < ctx.w - 1:
            return pick(DIRT, 0.35)
        if (lz - ctx.cube.origin[2]) < 1.0:
            return NAIL[2]
    if is_side(ctx) and ctx.j >= ctx.h - 1:
        return mix(c, DIRT[1], 0.7)
    return c


# ------------------------------------------------------------------ the face (one 18 x 18 pixel-art map per look)
# Covers the whole front of the head: col = x + 9 (x -9..9), row = y + 23 (y -23..-5).  Painted on every front face
# of the head / jaw cubes by position, so the recessed sockets, nose, cheek plate and jaw share one drawing:
#   rows 0-3 brow plate (z -9) | rows 4-7 the recessed eye band (cranium front, z -8) with temple / bridge plates
#   (cols 0, 8-9, 17) | rows 8-12 cheek plate (z -9; nose cube on cols 8-9 rows 8-9, z -10) | rows 13-17 jaw.
FPAL = {
    '0': SKIN[0], '1': SKIN[1], '2': SKIN[2], '3': SKIN[3], '4': SKIN[4], '5': SKIN[5], '6': SKIN[6],
    '7': SKIN[7], '8': SKIN[8], '9': SKIN[9],
    'K': hx('#050307'), 'k': hx('#1d1220'), 'q': hx('#3a2840'), 'Q': hx('#54405a'),
    'W': hx('#f6f4ee'), 'w': hx('#d9d6d0'), 'v': hx('#aaa6a6'), 'e': hx('#c46a6c'), 'o': hx('#0b0a0d'),
    'r': hx('#86141c'), 'R': hx('#b52a30'),
    'G': MOUTH[0], 'g': MOUTH[3], 'h': MOUTH[5],
    'T': TEETH[6], 't': TEETH[4], 'y': TEETH[2], 'Y': TEETH[1],
    'L': hx('#6f5a66'), 'l': hx('#4c3a48'), 'x': BLOOD[4], 'X': BLOOD[1], 'b': BLOOD[3], 'B': BLOOD[2],
    'V': VEIN, 'u': VEIN2,
}

FACE_BASE = [
    # 012345678901234567
    "456777777777777654",  # r0  y-23 forehead (under the fringe)
    "567777788777777765",  # r1
    "567777777777777765",  # r2
    "456666666666666654",  # r3  brow line (bottom of the forehead plate)
    "4.......76.......4",  # r4  socket band: cols 1-7 / 10-16 recessed pockets
    "4.......76.......4",  # r5
    "4.......76.......4",  # r6
    "4.......66.......4",  # r7
    "456666677766666654",  # r8  cheek plate (nose = cols 8-9, rows 8-9)
    "456677776677776654",  # r9
    "456677777777776654",  # r10
    "456666666666666654",  # r11
    "455555555555555554",  # r12
    "-45666666666666654",  # r13 jaw (cols 1-16)
    "-45667777777766654",  # r14
    "-45677788887776654",  # r15
    "-34566777777665443",  # r16
    "-23455666666554332",  # r17
]

EYE = [
    # 7 wide: cols 1-7 (right eye, viewer's left); mirrored for the left eye.  'o' = a pinprick pupil
    "KvwWwvK",  # r4 top of the white in the lid's shadow
    "kWWWWWk",  # r5
    "kWWWWWe",  # r6
    "KrWWWrK",  # r7
    "kKrRrKk",  # r8 inflamed red lower rim
    "qkkkkkq",  # r9 dark circles
    "4qqqqq4",  # r10
]

MOUTH_ART = [
    # 012345678901234567
    "ll..............ll",  # r9  corners of the grin climbing the cheeks
    "xGlLLlLLllLLlLLlGx",  # r10 cracked upper lip
    "xGGyyGyyGyyGyyGGGx",  # r11 upper teeth roots + black gums
    ".gtTGGTGGTGGTGGtg.",  # r12 upper fangs (tips)
    ".lGGTGGTGGTGGTGGl.",  # r13 lower fangs (tips)  -- jaw starts here
    "..lGyyGyyGyyGyyl..",  # r14 lower roots
    "..LlxLLlbLLlLxlL..",  # r15 cracked lower lip, blood
]

# hand-placed details: (row, col, char)
FACE_MARKS = [
    # three self-inflicted scratches across the forehead (viewer's right), scabbed at the top
    (0, 12, 'X'), (1, 11, 'x'), (2, 10, 'x'),
    (0, 14, 'X'), (1, 13, 'x'), (2, 12, 'x'), (3, 11, 'b'),
    (1, 15, 'X'), (2, 14, 'x'),
    # spider veins crawling from the sockets over the temples
    (3, 0, 'V'), (2, 1, 'u'), (4, 0, 'u'), (8, 0, 'V'), (9, 1, 'u'),
    (3, 17, 'V'), (2, 16, 'u'), (8, 17, 'V'), (9, 16, 'u'),
    # veins from the mouth corners down the jaw
    (14, 1, 'V'), (15, 2, 'u'), (16, 2, 'V'), (14, 16, 'V'), (15, 15, 'u'), (16, 15, 'V'),
    # blood running from the lower lip down the chin
    (16, 8, 'b'), (17, 8, 'B'), (16, 12, 'b'), (17, 12, 'b'), (16, 5, 'B'),
    # blood tear from the right eye
    (10, 3, 'b'), (11, 3, 'B'),
]

NOSE_FRONT = ["76", "54"]  # nose cube front (cols 8-9, rows 8-9)


def build_face():
    g = [list(r) for r in FACE_BASE]
    for j, row in enumerate(EYE):
        for i, ch in enumerate(row):
            g[4 + j][1 + i] = ch
            g[4 + j][16 - i] = ch
    for j, row in enumerate(MOUTH_ART):
        for i, ch in enumerate(row):
            if ch != '.':
                g[9 + j][i] = ch
    for r_, c_, ch in FACE_MARKS:
        g[r_][c_] = ch
    # a red vein in each white
    g[5][2] = 'e'
    g[6][14] = 'e'
    return g


FACE = build_face()

# ---- the normal face: a shy, sweet eight-year-old
NPAL = {
    '1': SKIN_N[1], '2': SKIN_N[2], '3': SKIN_N[3], '4': SKIN_N[4], '5': SKIN_N[5], '6': SKIN_N[6], '7': SKIN_N[7],
    '8': SKIN_N[8],
    'K': LASH[0], 'k': LASH[1], 'B': BROW_N[0], 'b': BROW_N[1], 'c': mix(SKIN_N[6], BROW_N[1], 0.5),
    'W': SCLERA[0], 'w': SCLERA[1], 'H': hx('#ffffff'),
    'P': IRIS[0], 'D': IRIS[1], 'I': IRIS[2], 'i': IRIS[3], 'a': IRIS[4],
    'p': mix(SKIN_N[6], BLUSH, 0.5), 'q': mix(SKIN_N[6], BLUSH, 0.25),
    'M': LIP_N[0], 'm': LIP_N[1], 'n': LIP_N[2],
}
FACE_N = [
    # 012345678901234567
    "566777777777777665",  # r0  forehead (under the bangs)
    "567777777777777765",  # r1
    "5677cc7777777cc765",  # r2  soft little brows peeking under the bangs
    "5kKKKKk6666kKKKKk5",  # r3  upper lash line on the brow plate, open at the inner corners, outer flick
    "5kWDDHW6666WDDHWk5",  # r4  big brown irises in the recessed eye band, a 2-px glint top right
    "56WIPHW6666WIPHW65",  # r5  pupil + glint
    "56WIPIW6666WIPIW65",  # r6
    "566aia6666666aia65",  # r7  warm amber lower iris, soft lower lid
    "566666677776666665",  # r8  cheek plate
    "5qppq6777777776qppq5"[:18],  # r9  rosy cheeks under the eyes
    "56qq6677777777766qq6"[:18],  # r10
    "566677777777777665",  # r11
    "566666m7777m776665",  # r12 the corners of a small closed smile...
    "-566667MMMM7666655",  # r13 ...whose line sits on the jaw seam (the jaw never opens in the normal look)
    "-56677777777766655",  # r14
    "-55667777777766555",  # r15
    "-45566777777665544",  # r16 the chin rounds off
    "-34455666666554433",  # r17
]
FACE_N = [(r + '5' * 18)[:18] for r in FACE_N]
NOSE_FRONT_N = ["77", "66"]


def face_px(x, y):
    c = int(math.floor(x + 9))
    r = int(math.floor(y + 23))
    if 0 <= r < 18 and 0 <= c < 18:
        if poss():
            return FPAL.get(FACE[r][c])
        return NPAL.get(FACE_N[r][c])
    return None


def in_pocket(x, y):
    return -19 <= y <= -15 and (-8 <= x <= -1 or 1 <= x <= 8)


def ear_n(z, y):
    """Normal look: the little ear painted on the side of the cranium (under the cut-out of the hair cap)."""
    ez, ey = z - 0.9, y + 13.6
    if abs(ez) > 1.7 or abs(ey) > 2.4:
        return None
    if abs(ez) > 1.15 or abs(ey) > 1.85:
        return 'rim'
    if ez < 0.2 and abs(ey) < 1.2:
        return 'hole'
    return 'in'


def head_mat(ctx):
    """Cranium / face plates / jaw: the face map on the front, plaster (or warm) skin elsewhere,
    pocket walls, the ear-to-ear tear on the sides (possessed), palate + tongue inside the mouth."""
    p = dpos(ctx)
    x, y, z = p
    t = tag(ctx)
    f = ctx.face
    P = poss()
    if f == 'front':
        if t == 'nose':
            r = int(math.floor(y + 23)) - 8
            c = int(math.floor(x + 9)) - 8
            if 0 <= r < 2 and 0 <= c < 2:
                return FPAL[NOSE_FRONT[r][c]] if P else NPAL[NOSE_FRONT_N[r][c]]
        c = face_px(x, y)
        if c is not None:
            return c
        return skin_mat(ctx)
    if t == 'nose' and f == 'bottom':
        if P:
            return FPAL['K'] if ctx.j == 0 else FPAL['q']
        return SKIN_N[3] if ctx.i % 2 == 0 and ctx.j == 0 else SKIN_N[4]
    # walls of the eye pockets
    if t in ('brow', 'cheek', 'bridge', 'temple') and in_pocket(x, y) or (t == 'bridge' and f in ('west', 'east')) \
            or (t == 'temple' and f in ('west', 'east') and abs(x) < 8.6):
        if P:
            return FPAL['k'] if f != 'top' else FPAL['K']
        if t == 'brow' and f == 'bottom':
            return LASH[0] if abs(abs(x) - 4.5) < 2.6 else SKIN_N[5]     # the lash line seen from below
        return SKIN_N[6] if f != 'top' else SKIN_N[7]
    if t == 'cranium' and f == 'bottom' and z > 1.0:
        # behind the jaw: the nape under the hair
        return pick(HAIR_N, 0.25) if not P else pick(HAIR, 0.3)
    if t == 'cranium' and f == 'bottom':
        # palate: black gums at the front, raw red roof further in
        dz = z + 8
        if dz < 1.2:
            return MOUTH[1]
        return pick(MOUTH, 0.35 + face_light(ctx) + (vnoise(x * 0.6, 0, z * 0.6, 91) - 0.5) * 0.25)
    if t == 'jaw' and f == 'top':
        if abs(x) > 6.5 or z < -8:
            return MOUTH[1]
        return pick(MOUTH, 0.55 + (vnoise(x * 0.5, 1, z * 0.5, 93) - 0.5) * 0.3)
    if f in ('west', 'east'):
        if P:
            k = cheek_tear(t, y, z)
            if k:
                return k
        elif t == 'cranium':
            e = ear_n(z, y)
            if e == 'rim':
                return pick(SKIN_N, 0.62 + (0.08 if y < -13.6 else -0.04))
            if e == 'in':
                return mix(SKIN_N[4], BLUSH, 0.35)
            if e == 'hole':
                return SKIN_N[2]
    if t == 'jaw' and f == 'bottom':
        c = skin_mat(ctx)
        return scale(c, 0.75)
    if not P and t == 'jaw' and f == 'back':
        return pick(SKIN_N, 0.22 + ctx.t * 0.08)               # in the shadow of the hair, above the nape
    if not P and t == 'jaw' and f in ('west', 'east'):
        return pick(SKIN_N, 0.55 + face_light(ctx) - (y + 10) * 0.012)
    return skin_mat(ctx)


def tear_y(z):
    """Centre line of the ear-to-ear tear along the side of the head (authoring y for a given z)."""
    if z < -3:
        return -10.0
    return -10.0 - (z + 3) * 1.1


def cheek_tear(t, y, z):
    """The grin is torn back along the jaw line to below the ear (thin black slit, raw red lips)."""
    if z > -1.0:
        return None
    yc = tear_y(z)
    d = y - yc
    if t == 'jaw':
        if z > -3.5:
            return None
        if d < 0.9:
            return MOUTH[1] if z < -5 else BLOOD[3]
        if d < 1.9 and hash3(math.floor(z), 0, 0, 191) > 0.35:
            return BLOOD[4]
        return None
    if -1.0 < d <= 0.0:
        return MOUTH[1] if z < -4 else BLOOD[3]
    if -2.0 < d <= -1.0 and hash3(math.floor(z), 1, 0, 191) > 0.4:
        return BLOOD[4]
    return None


def throat_mat(ctx):
    """Back of the open mouth: only seen from the front through the dropped jaw.  Its back and sides are hidden
    (transparent) so the nape behind the jaw does not show a black block."""
    if ctx.face == 'front':
        return MOUTH[0]
    if ctx.face == 'top':
        return MOUTH[2]
    return None


def teeth_mat(grow):
    """Possessed: small yellowed needle teeth on a zero-thickness plane (revealed when the jaw drops).
    Normal: a row of small white milk teeth (the jaw stays shut in that look; painted for safety).
    grow=+1: teeth hang from the top edge; -1: teeth stand up from the bottom edge."""
    def f(ctx):
        lx, ly, lz = local(ctx)
        c = ctx.cube
        col = int(math.floor(lx - c.origin[0]))
        depth = (ly - c.origin[1]) if grow > 0 else (c.origin[1] + c.size[1] - ly)
        if not poss():
            if depth > 1.0 or abs(lx) > 4.5:
                return None
            return hx('#f4efe6') if col % 2 == 0 else hx('#d9d0c4')
        h = hash3(col, 0, 0, 97 + grow)
        L = 1.0 + h * 1.4
        if col % 2 == 1:
            return MOUTH[1] if depth < 0.8 else None
        if depth > L:
            return None
        if depth < 0.7:
            return MOUTH[2]
        return pick(TEETH, 0.85 - (depth / L) * 0.15 - (0.35 if h > 0.8 else 0))
    return f


# ------------------------------------------------------------------ emissive layer 'eyes' (possessed look only)
def glow_decal(frm, size, face, fn):
    """Decal for the 'eyes' layer: fn(x, y, z) -> rgba | None at each texel centre (authoring coordinates).
    Paints nothing in the normal look."""
    def deco(img, u0, v0, w, h):
        if not poss():
            return
        px = img.load()
        for j in range(h):
            for i in range(w):
                c = fn(*face_point(frm, size, face, (i + 0.5) / w, (j + 0.5) / h))
                if c is not None:
                    px[u0 + i, v0 + j] = c
    return deco


def eye_glow(x, y, z):
    """The white of the possessed eyes burns full-bright; red rims and the pinprick pupils stay dark."""
    if not in_pocket(x, y):
        return None
    ch = FACE[int(math.floor(y + 23))][int(math.floor(x + 9))]
    return {'W': GLOW_EYE[0], 'w': GLOW_EYE[1], 'v': GLOW_EYE[2]}.get(ch)


# 'dazed' (after the Nona's slipper): cartoon swirl eyes on two planes over the eye band (pose toggle dizzy_eyes)
SWIRL = [
    ".WKKKW.",
    "WKWWWKW",
    "KWKKWWK",
    "KWKWKWK",
    "WKWWKWW",
    ".WKKWW.",
]


def dizzy_mat(ctx):
    lx, ly, lz = local(ctx)
    c = ctx.cube
    i = int(math.floor(lx - c.origin[0]))
    j = int(math.floor(ly - c.origin[1]))
    if ctx.face != 'front' or not (0 <= j < len(SWIRL) and 0 <= i < 7):
        return None
    ch = SWIRL[j][i if c.origin[0] < 0 else 6 - i]
    if ch == 'K':
        return IRIS[1]
    if ch == 'W':
        return SCLERA[0] if j < 4 else SCLERA[1]
    return None


# ------------------------------------------------------------------ hair
def hair_v(ctx, col, ly_frac, seed=0):
    strand = hash3(col // 2, seed, 0, 101)
    v = 0.28 + strand * 0.34 + face_light(ctx) * 0.9
    if col % 3 == 0:
        v -= 0.12
    v -= ly_frac * 0.1
    return v


def hair_color(ctx, p, v, col):
    x, y, z = p
    if not poss():
        return pick(HAIR_N, v + 0.12)
    # matted with dried blood in clumps
    if fbm(x * 0.25, y * 0.18, z * 0.25, 2, 107) > 0.66 and col % 4 != 0:
        return pick(BLOOD, v * 0.6 + 0.1)
    return pick(HAIR, v)


def hair_cap_n(ctx, p):
    """Normal: chestnut hair with a centre part, combed down the sides behind the ears to the two braids."""
    x, y, z = p
    f = ctx.face
    if f in ('bottom', 'front'):
        return None
    if f in ('west', 'east'):
        if z < 0.2 and y > -15.5:                       # cheek below the temple and the ear stay bare
            return None
        if ear_n(z, y) is not None:
            return None
        if z < -6.0 and y > -19.5:
            return None
        # strands sweep down-and-back toward the braid root behind the ear
        col = int(math.floor(z * 0.9 - (y + 23) * 0.45)) + 40
        v = 0.42 + hash3(col, 0, 0, 113) * 0.22 + face_light(ctx) * 0.8 - (0.1 if col % 3 == 0 else 0)
        if y > -14 and z > 0:
            v -= 0.08
        return pick(HAIR_N, v)
    if f == 'top':
        if abs(x) < 0.5:
            return mix(SKIN_N[5], HAIR_N[3], 0.35)      # the centre part
        col = int(math.floor(z * 0.8 + abs(x) * 0.25)) + (0 if x < 0 else 20)
        v = 0.52 + hash3(col, 1, 0, 113) * 0.22 + face_light(ctx) * 0.8 - (0.1 if col % 3 == 0 else 0)
        v += 0.06 if abs(x) < 3 else 0                  # sheen along the crown
        return pick(HAIR_N, v)
    # back: the part runs down to the nape, each half combed to its braid
    if abs(x) < 0.5:
        return mix(SKIN_N[4], HAIR_N[3], 0.45)
    col = int(math.floor(abs(x) * 0.8 + (y + 23) * 0.4)) + (0 if x < 0 else 30)
    v = 0.4 + hash3(col, 2, 0, 113) * 0.22 + face_light(ctx) * 0.8 - (0.1 if col % 3 == 0 else 0)
    return pick(HAIR_N, v)


def hair_cap_mat(ctx):
    """Shell over the cranium: open over the face, sideburn cut-outs to show the cheek tears."""
    p = dpos(ctx)
    if not poss():
        return hair_cap_n(ctx, p)
    x, y, z = p
    f = ctx.face
    if f in ('bottom', 'front'):
        return None
    if f in ('west', 'east'):
        lim = -16.5 + hash3(math.floor(z), 0, 0, 111) * 3.0
        if z < -3.5 and y > lim:
            return None
        if z < -6.5 and y > -20:
            return None
        col = int(math.floor(z * 1.0)) + 40
    elif f == 'top':
        col = int(math.floor(x)) + 20
    else:
        col = int(math.floor(x)) + 60
    v = hair_v(ctx, col, 0, 3)
    return hair_color(ctx, p, v, col)


def hang_mat(seed, ragged=0.45, axis='x'):
    """Hanging hair curtain / lock: per-strand values, ragged free ends toward +y (possessed mane)."""
    def f(ctx):
        c = ctx.cube
        lx, ly, lz = local(ctx)
        if ctx.face == 'bottom':
            return None
        if ctx.face == 'top':
            col = ctx.i + 30
            frac = 0.0
        else:
            col = int(math.floor(lx if ctx.face in ('front', 'back') else lz)) + (0 if ctx.face in ('front', 'back') else 50)
            frac = (ly - c.origin[1]) / c.size[1]
            lim = 1.0 - ragged * hash3(col, 0, 0, seed)
            if frac > lim:
                return None
            if frac > lim - 0.08:
                return pick(HAIR, 0.55) if poss() else pick(HAIR_N, 0.7)  # split ends catch the light
        v = hair_v(ctx, col, frac, seed)
        if ctx.face == 'front' and ctx.bone.name == 'hair_back':
            v -= 0.18  # underside of the curtain, against the back
        return hair_color(ctx, dpos(ctx), v, col)
    return f


# fringe: per-column strand length (rows from y=-24), x = -10 + col.
# possessed: long side curtains frame the face; ragged bangs; one long wet strand falls across the right eye.
FRINGE_L = [19, 18, 9, 5, 4, 14, 4, 3, 5, 3, 2, 4, 3, 5, 3, 4, 6, 10, 18, 19]
# normal: neat short bangs that stop just above the brows, two soft wisps framing the face in front of the ears
FRINGE_N = [11, 9, 4, 4, 3, 3, 3, 4, 4, 5, 4, 4, 4, 3, 3, 3, 4, 4, 9, 11]


def fringe_mat(ctx):
    lx, ly, lz = local(ctx)
    c = ctx.cube
    col = int(math.floor(lx - c.origin[0]))
    j = int(math.floor(ly - c.origin[1]))
    if not poss():
        L = FRINGE_N[col] if 0 <= col < len(FRINGE_N) else 0
        if j >= L:
            return None
        if L > 6 and j >= L - 2 and col in (1, 18):
            return None
        v = 0.5 + hash3(col, 0, 0, 177) * 0.2 + (0.16 if j == 1 else 0) - (0.1 if col % 3 == 0 else 0)
        if j >= L - 1:
            v -= 0.14                                    # the tips curl under, in shadow
        return pick(HAIR_N, v)
    L = FRINGE_L[col] if 0 <= col < len(FRINGE_L) else 0
    if j >= L:
        return None
    if j >= L - 2 and col % 2 == 1 and L > 4:
        return None  # tapered strand ends
    v = 0.30 + hash3(col, 0, 0, 175) * 0.3 + (0.18 if j == 2 else 0) - (0.1 if col % 3 == 0 else 0)
    if L > 8 and j > 6:
        v -= 0.08
    if col == 5 and j > 9:
        return pick(BLOOD, 0.45)  # blood-matted strand tip
    return pick(HAIR, v)


def braid_mat(ctx):
    """A three-strand plait: alternating diagonal lobes, a dark seam between them, sheen on the lobe tops."""
    lx, ly, lz = local(ctx)
    c = ctx.cube
    f = ctx.face
    if f in ('top', 'bottom'):
        return pick(HAIR_N, 0.32 if f == 'bottom' else 0.5)
    i = ctx.i
    j = int(math.floor(ly - c.origin[1] + (0.0 if tag(ctx) == 'braid' else 0.5)))
    seg = j // 2
    k = j % 2
    flip = (seg + (1 if f in ('west', 'back') else 0)) % 2
    w = ctx.w
    lobe = i if flip == 0 else (w - 1 - i)
    v = 0.5 + face_light(ctx) * 0.9
    if k == 0:
        v += (0.18, 0.06, -0.12)[min(lobe, 2)]
    else:
        v += (0.02, -0.08, -0.22)[min(lobe, 2)]
    return pick(HAIR_N, v)


def tuft_mat(ctx):
    """The brushy end of the braid under the yarn tie: splayed strands with ragged tips."""
    lx, ly, lz = local(ctx)
    c = ctx.cube
    f = ctx.face
    if f == 'top':
        return pick(HAIR_N, 0.4)
    depth = (ly - c.origin[1]) / c.size[1]
    if f == 'bottom':
        return None if (ctx.i + ctx.j) % 2 else pick(HAIR_N, 0.3)
    lim = 0.55 + 0.45 * hash3(ctx.i, ord(f[0]), 0, 197)
    if depth > lim:
        return None
    v = 0.48 + face_light(ctx) * 0.9 + (0.12 if ctx.i % 2 == 0 else -0.06) - depth * 0.15
    return pick(HAIR_N, v)


def yarn_mat(ctx):
    """The Nona's red yarn: hair ties (normal) -- wound turns."""
    v = 0.55 + face_light(ctx) * 1.0 + (0.1 if ctx.j % 2 == 0 else -0.05) + (0.06 if ctx.i % 2 == 0 else 0)
    return pick(KNIT, v)


# ------------------------------------------------------------------ the nightgown
def gown_value(ctx, p, base=0.66):
    x, y, z = p
    v = base + face_light(ctx) * 1.1
    if not flat(ctx) and edge(ctx) == 0:
        v -= 0.06
    return v


STAIN_W = [3.6, 3.4, 3.0, 2.6, 2.6, 2.2, 2.0, 1.8, 1.6, 1.6, 1.4, 1.2, 1.0]


def stain(ctx, p):
    """Black bile + blood vomited down the front (an organic flow with drips)."""
    x, y, z = p
    if ctx.face != 'front':
        return None
    row = math.floor(y + 4)
    col = math.floor(x)
    xc = 0.3 + math.sin(y * 0.33) * 1.1
    if 0 <= row < len(STAIN_W):
        w = STAIN_W[row] + (hash3(row, 0, 0, 121) - 0.5) * 1.1
        dx = abs(x - xc)
        if dx < w:
            if dx < w * 0.5:
                return BILE[1] if hash3(col, row, 0, 123) > 0.15 else BILE[3]
            return BLOOD[2] if dx < w - 0.9 else BLOOD[4]
    # drips: thin runs of different length from the bottom of the flow and the collar
    if y > -2:
        L = hash3(col, 0, 0, 125)
        start = 7 if abs(x - xc) < 3 else -2
        if abs(x - 0.5) < 5.5 and L > 0.5 and y < start + (L - 0.5) * 26:
            if abs(x - 0.5) > 3.5 and L < 0.75:
                return None
            tip = y > start + (L - 0.5) * 26 - 1.5
            return BLOOD[4] if tip else (BLOOD[2] if hash3(col, 1, 0, 125) > 0.45 else BILE[2])
    # a few splatter dots on the skirt
    if y > 9 and hash3(col, math.floor(y), 0, 127) > 0.965:
        return BLOOD[3]
    return None


def handprint(x, y, cx, cy):
    """A small bloody handprint (5 x 6) on the skirt, palm + four fingers."""
    i, j = int(math.floor(x - cx)), int(math.floor(y - cy))
    art = [
        "x.x.x",
        "x.x.x.",
        "xxxxx",
        "xxxx.",
        ".xxx.",
    ]
    if 0 <= j < len(art) and 0 <= i < len(art[j]):
        return art[j][i] == 'x'
    return False


def sprig(u, v):
    """Normal look: tiny pink rosebuds on the cream flannel, a sparse staggered 5 x 5 grid."""
    iu, iv = int(math.floor(u + 100)), int(math.floor(v + 100))
    su = iu + (2 if (iv // 5) % 2 else 0)
    a, b = su % 5, iv % 5
    if b == 1 and a == 1:
        return SPRIG[0]
    if b == 1 and a == 2:
        return SPRIG[1]
    if b == 2 and a == 1:
        return SPRIG[2]
    return None


def gown_mat(ctx):
    p = dpos(ctx)
    x, y, z = p
    t = tag(ctx)
    f = ctx.face
    v = gown_value(ctx, p)
    if is_side(ctx):
        u = x if f in ('front', 'back') else z
        k = math.floor(u) % 3
        v += (-0.07, 0.05, 0.0)[k]
    if not poss():
        c = pick(GOWN_N, v + 0.04)
        if is_side(ctx):
            s = sprig(*uv2(ctx, p))
            if s is not None:
                c = s
        return c
    c = pick(GOWN, v)
    g = fbm(x * 0.3, y * 0.3, z * 0.3, 2, 131)
    if g > 0.62:
        c = mix(c, hx('#6b5b41'), 0.45)
    if t == 'bodice' and f == 'front':
        # seen only through the hole burned in the sweater: grimy flannel, pin-tucks, pearl buttons, singed edge
        if abs(x - 0.5) < 0.6 and math.floor(y) % 2 == 0:
            c = LACE[4]
        bc = burn_class(x, y)
        dd = math.hypot(x - BURN_C[0], (y - BURN_C[1]) * 1.12) - burn_r(math.atan2((y - BURN_C[1]) * 1.12, x - BURN_C[0]))
        if dd > -1.2:
            c = mix(c, hx('#3a2216'), 0.55 if dd > -0.6 else 0.3)
        if bc is None and dd < -1.2 and hash3(math.floor(x * 2), math.floor(y * 2), 0, 135) > 0.9:
            c = BLOOD[3]
        return c
    s = stain(ctx, p)
    if s is not None:
        c = s
    return c


def skirt_mat(ctx):
    """Ruffled tier of the bell skirt.  Possessed: shredded hem (alpha), grime, blood, bile and a handprint.
    Normal: clean cream flannel with rosebuds, a lace edge on every tier and a scalloped lace hem."""
    p = dpos(ctx)
    x, y, z = p
    f = ctx.face
    c_ = ctx.cube
    P = poss()
    torn = tag(ctx) == 'hem'
    if f == 'bottom':
        if torn:
            return LACE_N[2] if not P else None
        return pick(GOWN_N, 0.12) if not P else pick(GOWN, 0.08)      # the shadowed petticoat inside the tier
    if f == 'top':
        # the ruffle shelf of a lower tier: lace frill
        v = 0.72 + ((ctx.i + ctx.j) % 2) * 0.08
        return pick(LACE, v) if P else pick(LACE_N, v)
    u = x if f in ('front', 'back') else z
    col = math.floor(u)
    lx, ly, lz = local(ctx)
    depth = (ly - c_.origin[1])
    hgt = c_.size[1]
    if not P:
        v = gown_value(ctx, p, 0.66) + (-0.08, 0.04, 0.06, 0.0)[col % 4] - (depth / hgt) * 0.08
        if f == 'back' or (torn and ctx.face in ('back',)):
            v -= 0.03
        c = pick(GOWN_N, v)
        s = sprig(u, y)
        if s is not None:
            c = s
        if not torn and depth > hgt - 1.0:
            c = pick(LACE_N, 0.55 + (col % 2) * 0.3)
        if torn:
            if depth > hgt - 2.0:
                # scalloped broderie lace: little arches with eyelets
                k = col % 3
                if depth > hgt - 1.0 and k == 1:
                    return None
                c = pick(LACE_N, 0.62 + (0.25 if k == 0 else 0.0))
                if depth < hgt - 1.0 and k == 2:
                    c = LACE_N[1]
            elif depth > hgt - 3.0:
                c = mix(c, RIBBON_N[3], 0.7) if col % 2 == 0 else c   # a pink satin band above the lace
        return c
    if torn:
        lim = hgt * (0.45 + 0.55 * hash3(col // 1, 0, ord(f[0]), 141))
        if hash3(col, 1, 0, 143) > 0.82:
            lim = hgt * 0.25  # a deep rip showing the legs
        if depth > lim:
            return None
    v = gown_value(ctx, p, 0.64)
    k = col % 4
    v += (-0.1, 0.04, 0.07, 0.0)[k]
    v -= (depth / hgt) * 0.1
    if f == 'back':
        v -= 0.04
    c = pick(GOWN, v)
    if not torn and depth > hgt - 1.0:
        c = pick(LACE, 0.5 + (col % 2) * 0.3)
    g = fbm(x * 0.28, y * 0.2, z * 0.28, 2, 147) + (y - 8) * 0.03
    if g > 0.68:
        c = mix(c, hx('#5c4b33'), 0.5)
    if torn and depth > lim - 1.0:
        c = mix(c, DIRT[2], 0.6)
    s = stain(ctx, p)
    if s is not None:
        c = s
    if f == 'front' and handprint(x, y, -6, 13):
        c = BLOOD[3]
    return c


def lace_mat(ctx):
    """High lace collar of the nightgown peeking out of the sweater: scalloped top edge with holes."""
    f = ctx.face
    if f in ('bottom', 'top'):
        return None if f == 'top' else (LACE[1] if poss() else LACE_N[1])
    j, i = ctx.j, ctx.i
    if j == 0 and i % 2 == 1:
        return None
    if j == 1 and i % 4 == 2:
        return None
    p = dpos(ctx)
    v = 0.62 + face_light(ctx) + (0.12 if (i + j) % 2 == 0 else 0)
    if not poss():
        return pick(LACE_N, v + 0.06)
    c = pick(LACE, v)
    if f == 'front' and abs(p[0] - 0.3) < 2.2 and j >= 1 and hash3(i, j, 0, 161) > 0.3:
        c = BILE[1] if abs(p[0] - 0.3) < 1 else BLOOD[3]
    return c


def petticoat_mat(ctx):
    return pick(GOWN, 0.18 + face_light(ctx) * 0.5) if poss() else pick(GOWN_N, 0.3 + face_light(ctx) * 0.5)


# ------------------------------------------------------------------ the Nona's red sweater
BURN_C = (0.0, 1.4)                         # centre of the heart / of the burn on the sweater front (authoring x, y)
HEART = [
    ".XX.XX.",
    "XXXXXXX",
    "XXXXXXX",
    ".XXXXX.",
    "..XXX..",
    "...X...",
]


def burn_r(a):
    return 2.7 + 0.75 * math.sin(3 * a + 0.7) + 0.45 * math.sin(5 * a + 2.1) + 0.25 * math.sin(8 * a + 0.3)


def burn_class(x, y):
    """Possessed: the hole burned through the chest of the sweater, where the heart was."""
    dx, dy = x - BURN_C[0], (y - BURN_C[1]) * 1.12
    d = math.hypot(dx, dy)
    r = burn_r(math.atan2(dy, dx))
    h = hash3(math.floor(x * 2), math.floor(y * 2), 0, 211)
    if d < r:
        return 'hole'
    if d < r + 0.55:
        return 'ember' if h > 0.58 else 'char'
    if d < r + 1.5:
        return 'char' if h > 0.12 else 'scorch'
    if d < r + 3.8 and hash3(math.floor(x * 2), math.floor(y * 2), 1, 211) > (d - r - 1.5) / 2.3:
        return 'scorch'
    return None


def heart_at(x, y):
    i = int(math.floor(x - BURN_C[0] + 3.5))
    j = int(math.floor(y - BURN_C[1] + 3.0))
    return 0 <= j < len(HEART) and 0 <= i < 7 and HEART[j][i] == 'X'


def knit_core(ctx, p, rib=False, darn=False):
    """Hand-knitted red wool: stockinette 'V' columns (2 texels per stitch) or vertical ribs; baked light."""
    x, y, z = p
    f = ctx.face
    u = x if f in ('front', 'back', 'top', 'bottom') else z
    vv = y if f not in ('top', 'bottom') else z
    iu, jy = math.floor(u + 100), math.floor(vv + 100)
    v = 0.56 + face_light(ctx) * 1.0
    if rib:
        v += 0.08 if iu % 2 == 0 else -0.1
    else:
        v += 0.07 if (iu % 2) == (jy % 2) else -0.05
        if not flat(ctx) and edge(ctx) == 0:
            v -= 0.05
    c = pick(KNIT, v)
    if darn and f in ('back', 'west', 'east', 'bottom'):
        # the Nona's darn on the elbow: a woven patch of cream-red wool
        c = pick(CREAM, 0.35 + face_light(ctx) + (0.12 if (iu + jy) % 2 == 0 else 0)) if (iu + jy) % 3 else c
    return c


def knit_mat(ctx):
    """Sweater body / waistband / neck rib.  Normal: clean wool with the cream heart.  Possessed: soot, stretched
    stitches, bile running down from the hole burned through the heart (alpha: the nightgown shows inside)."""
    p = dpos(ctx)
    x, y, z = p
    f = ctx.face
    t = tag(ctx)
    P = poss()
    if t == 'neckrib' and f == 'top':
        lx, ly, lz = local(ctx)
        c0 = ctx.cube
        if c0.origin[0] + 1 < lx < c0.origin[0] + c0.size[0] - 1 and c0.origin[2] + 1 < lz < c0.origin[2] + c0.size[2] - 1:
            return None                              # the neck hole
    if f == 'bottom' and t == 'sweater':
        return KNIT[1] if not P else CHAR[2]
    rib = t in ('waistband', 'neckrib', 'cuff')
    c = knit_core(ctx, p, rib)
    if t == 'sweater' and f == 'front':
        if P:
            b = burn_class(x, y)
            if b == 'hole':
                return None
            if b == 'ember':
                return EMBER[2] if hash3(math.floor(x * 2), math.floor(y * 2), 2, 211) > 0.5 else EMBER[1]
            if b == 'char':
                return pick(CHAR, 0.1 + hash3(math.floor(x * 2), math.floor(y * 2), 3, 211) * 0.55)
            if b == 'scorch':
                c = mix(c, hx('#2a1710'), 0.62)
            elif heart_at(x, y):
                c = mix(pick(CREAM, 0.4 + face_light(ctx) + (0.1 if (math.floor(x + 100) % 2) == (math.floor(y + 100) % 2) else -0.06)), CHAR[3], 0.45)
        elif heart_at(x, y):
            c = pick(CREAM, 0.55 + face_light(ctx) + (0.1 if (math.floor(x + 100) % 2) == (math.floor(y + 100) % 2) else -0.06))
    if not P:
        return c
    # filth: the whole sweater sooted and greyed, darker blotches, pulled threads, bile running down from the hole
    g = fbm(x * 0.32, y * 0.32, z * 0.32, 2, 221)
    c = mix(c, hx('#2b1a1a'), 0.32 + (0.3 if g > 0.58 else 0.0))
    if f == 'front':
        s = stain(ctx, (x * 0.85, y, z))                 # the bile + blood she vomited runs down over the wool
        if s is not None and (t != 'sweater' or burn_class(x, y) in (None, 'scorch')):
            c = s
    if is_side(ctx) and hash3(math.floor(x * 3), math.floor(y), math.floor(z * 3), 223) > 0.97:
        c = CHAR[1]
    return c


def sweater_glow(x, y, z):
    if burn_class(x, y) == 'ember':
        return EMBER[3] if hash3(math.floor(x * 2), math.floor(y * 2), 2, 211) > 0.5 else EMBER[2]
    return None


def sleeve_mat(ctx):
    """Upper sweater sleeve.  Possessed: sooty, two moth-eaten / burned holes showing the grey arm."""
    p = dpos(ctx)
    x, y, z = p
    c = knit_core(ctx, p, rib=False)
    if not poss():
        return c
    if is_side(ctx) and fbm(x * 0.55 + 3, y * 0.55, z * 0.55, 2, 231) > 0.68:
        return None
    g = fbm(x * 0.3, y * 0.3, z * 0.3, 2, 233)
    return mix(c, hx('#2b1a1a'), 0.32 + (0.3 if g > 0.56 else 0.0))


def fsleeve_cut(face, x, y, z, top):
    """Possessed: how far the forearm sleeve survives below the elbow -> 'gone' | 'ember' | 'char' | None.
    Absolute authoring coordinates; top = y of the top of the sleeve cube."""
    depth = y - top
    u = x if face in ('front', 'back') else z
    k = math.floor(u * 1.5 + 50)
    lim = 2.2 + 1.6 * hash3(k, ord(face[0]), 0, 241)
    if depth > lim:
        return 'gone'
    if depth > lim - 0.7:
        return 'ember' if hash3(k, 1, ord(face[0]), 241) > 0.55 else 'char'
    if depth > lim - 1.6:
        return 'char'
    return None


def fsleeve_mat(ctx):
    """Forearm sleeve + cuff.  Normal: too long, the ribbed cuff covers half her hand.  Possessed: burned off at
    the elbow (alpha), a charred ragged edge with embers; the cuff is gone."""
    p = dpos(ctx)
    t = tag(ctx)
    P = poss()
    if t == 'cuff':
        if P:
            return None
        if ctx.face in ('top', 'bottom'):
            lx, ly, lz = local(ctx)
            c0 = ctx.cube
            inner = c0.origin[0] + 0.6 < lx < c0.origin[0] + c0.size[0] - 0.6 and c0.origin[2] + 0.6 < lz < c0.origin[2] + c0.size[2] - 0.6
            if inner:
                return KNIT[0] if ctx.face == 'bottom' else None
        return knit_core(ctx, p, rib=True)
    if ctx.face == 'bottom':
        return None if P else KNIT[1]
    if P:
        if ctx.face == 'top':
            return mix(knit_core(ctx, p), CHAR[2], 0.5)
        k = fsleeve_cut(ctx.face, *p, ctx.bone.abs[1] + ctx.cube.origin[1])
        if k == 'gone':
            return None
        if k == 'ember':
            return EMBER[3]
        if k == 'char':
            return pick(CHAR, 0.3 + hash3(ctx.i, ctx.j, 0, 243) * 0.6)
        return mix(knit_core(ctx, p), hx('#2b1a1a'), 0.5)
    return knit_core(ctx, p)


def fsleeve_glow(face, top):
    def fn(x, y, z):
        return EMBER[4] if fsleeve_cut(face, x, y, z, top) == 'ember' else None
    return fn


def burn_mat(ctx):
    """Charred, curled lips of the burn hole (toggle 'sweater_burn', possessed): black wool with live embers."""
    p = dpos(ctx)
    x, y, z = p
    if ctx.face == 'back':
        return CHAR[0]
    h = hash3(math.floor(x * 2), math.floor(y * 2), math.floor(z * 2), 251)
    if h > 0.78:
        return EMBER[3] if h > 0.9 else EMBER[2]
    v = 0.35 + face_light(ctx) * 1.2 + (h - 0.5) * 0.4
    return pick(CHAR, v)


def burn_glow(x, y, z):
    h = hash3(math.floor(x * 2), math.floor(y * 2), math.floor(z * 2), 251)
    if h > 0.78:
        return EMBER[4] if h > 0.9 else EMBER[3]
    return None


# ------------------------------------------------------------------ module contract
class LuciaModel(Model):
    """Exports every bone to Java; the preview / gallery JSON hides the toggle bones the current look hides.
    paint() tells the look-aware materials and the emissive decals which look ('normal' / 'poseida') is painted."""
    visible = None

    def paint(self, default_mat, seed=1, layer='base'):
        _LOOK[0] = getattr(default_mat, 'look', 'normal')
        try:
            return super().paint(default_mat, seed, layer)
        finally:
            _LOOK[0] = 'normal'

    def to_json(self):
        d = super().to_json()
        d['toggles'] = {'default': dict(TOGGLE_DEFAULT),
                        'variants': {k: dict(v) for k, v in VARIANT_TOGGLES.items()},
                        'poses': {k: dict(v) for k, v in POSE_TOGGLES.items()}}
        if self.visible is None:
            return d
        hide = set()
        for b in self.bones():
            if b.name in TOGGLE_DEFAULT and b.name not in self.visible:
                for sub in b.walk():
                    hide.add(sub.name)
        for bd in d['bones']:
            if bd['name'] in hide and bd['cubes']:
                bd['hidden_cubes'] = bd['cubes']                       # a toggle-aware viewer can still show them
                bd['cubes'] = []
        return d


def make_mat(look):
    """Fallback material of look `look`; LuciaModel.paint reads .look and every material follows it."""
    def mat(ctx):
        return skin_mat(ctx)
    mat.look = look
    return mat


DEFAULT_MAT = make_mat('normal')
VARIANT_MATS = {'normal': DEFAULT_MAT, 'poseida': make_mat('poseida')}
FOCUS = 'head'

# ------------------------------------------------------------------ toggles (Java: ModelPart.visible)
# bone -> visible in the default look 'normal'.  Hiding a parent hides its children.
TOGGLE_DEFAULT = {
    'braid_right': True, 'braid_left': True, 'right_mitt': True, 'left_mitt': True,
    'hair_back': False, 'hair_right': False, 'hair_left': False, 'right_claw': False, 'left_claw': False,
    'sweater_burn': False, 'dizzy_eyes': False,
}
VARIANT_TOGGLES = {
    'normal': {},
    'poseida': {'braid_right': False, 'braid_left': False, 'right_mitt': False, 'left_mitt': False,
                'hair_back': True, 'hair_right': True, 'hair_left': True, 'right_claw': True, 'left_claw': True,
                'sweater_burn': True},
}
POSE_TOGGLES = {'dazed': {'dizzy_eyes': True}}
JAW_LOCKED_VARIANTS = ('normal',)          # Java never opens the torn jaw in the normal look


def visible_set(variant=None, pose=None):
    vis = dict(TOGGLE_DEFAULT)
    vis.update(VARIANT_TOGGLES.get(variant or 'normal', {}))
    vis.update(POSE_TOGGLES.get(pose, {}))
    show = os.environ.get('POSEIDA_SHOW', '')           # preview helper: 'all' or 'bone,-bone' (- hides)
    items = show.split(',') if show else []
    for k in vis:
        if show == 'all' or k in items:
            vis[k] = True
        if '-' + k in items:
            vis[k] = False
    return {k for k, v in vis.items() if v}


def _argv(flag):
    a = sys.argv
    return a[a.index(flag) + 1] if flag in a and a.index(flag) + 1 < len(a) else None


# ------------------------------------------------------------------ rest rotations shared by build() and the gravity maths
CHAIN_REST = {'base': (0, 0, 0), 'body': (7, 0, 0), 'neck': (-4, 0, 0), 'head': (4, 0, -16)}
PARENT = {'body': 'base', 'neck': 'body', 'head': 'neck', 'hair_back': 'head', 'hair_right': 'head', 'hair_left': 'head',
          'braid_right': 'head', 'braid_left': 'head', 'braid_right_tip': 'braid_right', 'braid_left_tip': 'braid_left',
          'skirt': 'base', 'hem_front': 'skirt', 'hem_back': 'skirt', 'hem_right': 'skirt', 'hem_left': 'skirt'}


# ------------------------------------------------------------------ build
REST_DEG = {}                               # bone -> rest rotation (degrees), filled by build()
ABS_PIVOT = {}


def build(variant=None, pose=None):
    r = Rig()

    def bone(name, pivot, parent=None, rot=(0, 0, 0), mat=None):
        b = r.bone(name, pivot, parent, rot, mat)
        b.abs = r.abs_pivot[name]
        REST_DEG[name] = tuple(float(v) for v in rot)
        ABS_PIVOT[name] = b.abs
        return b

    def box(b, frm, size, mat=None, inflate=0.0, decals=None, name=None, glow=None):
        if glow is not None:
            decals = dict(decals or {})
            for face, fn in glow.items():
                decals['eyes:' + face] = glow_decal(frm, size, face, fn)
        c = r.box(b, frm, size, mat=mat, inflate=inflate, decals=decals)
        c.name = name
        return c

    # ---------------- base (pelvis) + legs
    bone('base', (0, 8, 0))
    box('base', (-5.5, 4, -3), (11, 6, 6), mat=petticoat_mat)
    for side, sx in (('right', -1), ('left', 1)):
        leg = bone(f'{side}_leg', (3 * sx, 8, 0), 'base', rot=(-3 if sx < 0 else 4, 0, 5 * sx), mat=skin_mat)
        box(leg.name, (3 * sx - 2.5, 7, -2.5), (5, 8, 5))
        shin = bone(f'{side}_shin', (3 * sx, 15, 0), leg.name, rot=(4 if sx < 0 else -2, 0, -9 * sx), mat=skin_mat)
        box(shin.name, (3 * sx - 2, 14.2, -3.4), (4, 2, 2), mat=knob_mat)
        box(shin.name, (3 * sx - 2, 15, -2), (4, 7, 4))
        foot = bone(f'{side}_foot', (3 * sx, 22, 0), shin.name, rot=(0, -18 if sx < 0 else 6, 0), mat=foot_mat)
        box(foot.name, (3 * sx - 2, 22, -6), (4, 2, 8))

    # ---------------- skirt: two ruffled tiers + a flared hem in four panels (shredded / lace)
    bone('skirt', (0, 4, 0), 'base', mat=skirt_mat)
    box('skirt', (-7, 4, -4.5), (14, 5, 9), name='tier')
    box('skirt', (-8, 9, -5.5), (16, 4, 11), name='tier')
    fl = HANG_REST['hem_back'][0]
    bone('hem_front', (0, 12.5, -5), 'skirt', rot=(-fl, 0, 0), mat=skirt_mat)
    box('hem_front', (-9, 12.5, -5.5), (18, 7, 1), name='hem')
    bone('hem_back', (0, 12.5, 5), 'skirt', rot=(fl, 0, 0), mat=skirt_mat)
    box('hem_back', (-9, 12.5, 4.5), (18, 7, 1), name='hem')
    bone('hem_right', (-7.5, 12.5, 0), 'skirt', rot=(0, 0, fl), mat=skirt_mat)
    box('hem_right', (-8.5, 12.5, -6.5), (1, 7, 13), name='hem')
    bone('hem_left', (7.5, 12.5, 0), 'skirt', rot=(0, 0, -fl), mat=skirt_mat)
    box('hem_left', (7.5, 12.5, -6.5), (1, 7, 13), name='hem')

    # ---------------- torso: nightgown bodice + lace collar under the Nona's sweater
    bone('body', (0, 7, 0), 'base', rot=CHAIN_REST['body'], mat=gown_mat)
    box('body', (-6, -3, -3.5), (12, 11, 7), name='bodice')
    box('body', (-3.5, -5.5, -3), (7, 3, 6), mat=lace_mat, inflate=0.3)
    sw_frm, sw_size = (-6.5, -3, -4), (13, 10, 8)
    box('body', sw_frm, sw_size, mat=knit_mat, inflate=0.5, name='sweater', glow={'front': sweater_glow})
    box('body', (-6, 7, -3.5), (12, 3, 7), mat=knit_mat, inflate=0.6, name='waistband')
    box('body', (-4.5, -4, -3.5), (9, 1, 7), mat=knit_mat, inflate=0.5, name='neckrib')
    # charred curled lips round the hole (possessed only)
    bone('sweater_burn', (BURN_C[0], BURN_C[1], -4.6), 'body', mat=burn_mat)
    lips = [((-1.4, -2.4, -5.0), (3, 1, 1)), ((-3.0, 0.2, -5.0), (1, 3, 1)), ((1.4, 3.0, -5.0), (2, 1, 1))]
    for frm, size in lips:
        box('sweater_burn', frm, size, inflate=-0.1, name='lip', glow={'front': burn_glow})
    box('sweater_burn', (-2.4, 3.2, -4.9), (1, 3, 0), name='strand')       # a melted strand hanging off

    # ---------------- neck + head
    bone('neck', (0, -2, 0.5), 'body', rot=CHAIN_REST['neck'], mat=skin_mat)
    box('neck', (-2.5, -7, -2), (5, 7, 5))
    bone('head', (0, -7, 1), 'neck', rot=CHAIN_REST['head'], mat=head_mat)
    cr_frm, cr_size = (-9, -23, -8), (18, 13, 15)
    box('head', cr_frm, cr_size, name='cranium', glow={'front': eye_glow})
    box('head', (-9, -23, -9), (18, 4, 1), name='brow')
    box('head', (-9, -15, -9), (18, 5, 1), name='cheek')
    box('head', (-9, -19, -9), (1, 4, 1), name='temple')
    box('head', (8, -19, -9), (1, 4, 1), name='temple')
    box('head', (-1, -19, -9), (2, 4, 1), name='bridge')
    box('head', (-1, -15, -10), (2, 2, 1), name='nose')
    box('head', (-6, -10, -1), (12, 4, 3), mat=throat_mat)
    box('head', (-8, -10, -8.5), (16, 2, 0), mat=teeth_mat(1))
    # hair cap (shell) + fringe strands over the forehead (and, possessed, over the right eye)
    box('head', cr_frm, cr_size, mat=hair_cap_mat, inflate=1.0)
    box('head', (-10, -24, -9.5), (20, 19, 0), mat=fringe_mat)

    bone('jaw', (0, -10, 1), 'head', mat=head_mat)
    box('jaw', (-8, -10, -9), (16, 5, 10), name='jaw')
    box('jaw', (-7, -12, -8.5), (14, 2, 0), mat=teeth_mat(-1))
    # 'dazed' only: swirl eyes floating just in front of the face plates
    bone('dizzy_eyes', (0, -17, -9.1), 'head', mat=dizzy_mat)
    box('dizzy_eyes', (-8, -20, -9.15), (7, 6, 0), name='swirl')
    box('dizzy_eyes', (1, -20, -9.15), (7, 6, 0), name='swirl')

    # possessed: long tangled hair -- back curtain + two side locks hanging over the shoulders
    bone('hair_back', (0, -17, 7.5), 'head', rot=HANG_REST['hair_back'], mat=hang_mat(181, 0.5))
    box('hair_back', (-10, -17, 6.5), (20, 24, 3))
    for side, sx in (('right', -1), ('left', 1)):
        hl = bone(f'hair_{side}', (9.5 * sx, -16, -1), 'head', rot=HANG_REST[f'hair_{side}'], mat=hang_mat(185 + sx, 0.4))
        box(hl.name, (9.5 * sx - 2, -16, -4), (4, 20, 5))

    # normal: two braids from behind the ears, draped forward over the shoulders, tied with red yarn
    for side, sx in (('right', -1), ('left', 1)):
        bx = 10.3 * sx
        bone(f'braid_{side}', (bx, -12.5, 3.0), 'head', rot=HANG_REST[f'braid_{side}'], mat=braid_mat)
        box(f'braid_{side}', (bx - 1.5, -12.5, 1.5), (3, 8, 3), name='braid')
        bone(f'braid_{side}_tip', (bx, -4.5, 3.0), f'braid_{side}', rot=HANG_REST[f'braid_{side}_tip'], mat=braid_mat)
        box(f'braid_{side}_tip', (bx - 1.5, -4.5, 1.5), (3, 5, 3), inflate=-0.15, name='braid2')
        box(f'braid_{side}_tip', (bx - 2, 0.5, 1.0), (4, 1, 4), mat=yarn_mat, inflate=-0.1, name='tie')
        box(f'braid_{side}_tip', (bx - 2, 1.5, 1.0), (4, 3, 4), mat=tuft_mat, inflate=-0.25, name='tuft')

    # ---------------- arms: sweater sleeves, sharp elbows, spider claws (possessed) or small hands (normal)
    for side, sx in (('right', -1), ('left', 1)):
        sh_y = -1 if sx > 0 else 0  # right shoulder dropped
        ax = 6.8 * sx
        arm = bone(f'{side}_arm', (ax, sh_y, 0.5), 'body', rot=(-10, 0, -16 * sx), mat=skin_mat)
        box(arm.name, (ax - 2, sh_y - 1, -1.5), (4, 8, 4))
        box(arm.name, (ax - 2.5, sh_y - 2.5, -2), (5, 9, 5), mat=sleeve_mat, inflate=0.2, name='sleeve')
        fa = bone(f'{side}_forearm', (ax, sh_y + 7, 0.5), arm.name, rot=(-16 if sx < 0 else 14, 0, 2 * sx), mat=skin_mat)
        box(fa.name, (ax - 1.5, sh_y + 7, -1), (3, 9, 3))
        box(fa.name, (ax - 1.5, sh_y + 6, 1.5), (3, 2, 2), mat=knob_mat)
        fs_frm, fs_size = (ax - 2, sh_y + 6.5, -1.5), (4, 8, 4)
        box(fa.name, fs_frm, fs_size, mat=fsleeve_mat, inflate=0.25, name='fsleeve',
            glow={f: fsleeve_glow(f, fs_frm[1]) for f in ('front', 'back', 'west', 'east')})
        box(fa.name, (ax - 2, sh_y + 14, -1.5), (4, 3, 4), mat=fsleeve_mat, inflate=0.5, name='cuff')
        hy = sh_y + 16
        hd = bone(f'{side}_hand', (ax, hy, 0.5), fa.name, rot=(6, 0, 0), mat=skin_mat)
        box(hd.name, (ax - 1, hy, -1.5), (2, 4, 4))
        # possessed claws
        claw = bone(f'{side}_claw', (ax, hy, 0.5), hd.name, rot=(-8.6, 0, -11.5 * sx), mat=finger_mat)  # splayed, clear of the floor
        th = bone(f'{side}_thumb', (ax, hy + 1, -1.5), claw.name, rot=(-25, 0, -20 * sx), mat=finger_mat)
        box(th.name, (ax - 0.5, hy + 1, -2), (1, 4, 1))
        for k, zc in enumerate((-1.0, 0.0, 1.0, 2.0)):
            L = (7, 8, 7, 6)[k]
            fg = bone(f'{side}_finger{k + 1}', (ax, hy + 4, zc + 0.5), claw.name,
                      rot=((k - 1.5) * 7, 0, -26 * sx), mat=finger_mat)
            box(fg.name, (ax - 0.5, hy + 4, zc), (1, L, 1))
        # normal: short child fingers held together + thumb
        mitt = bone(f'{side}_mitt', (ax, hy + 4, 0.5), hd.name, mat=mitt_mat)
        box(mitt.name, (ax - 1, hy + 4, -1.5), (2, 3, 4), inflate=-0.05, name='fingers')
        box(mitt.name, (ax - 0.5 - 0.5 * sx, hy + 1, -2.5), (1, 3, 1), name='thumb')

    m = LuciaModel('poseida', 256, 256, r.roots)
    m.scale = 0.5
    if os.path.basename(sys.argv[0]) == 'preview.py':
        variant = variant or _argv('--variant')
        pose = pose or _argv('--pose')
    m.visible = visible_set(variant, pose)
    return m


# ------------------------------------------------------------------ gravity: braids and mane hang plumb
# Same idea as Ofelia's threads: a hanging part gets the pose entry that gives it a chosen WORLD orientation
# (inverse of its parent's world rotation), so braids and mane keep hanging under gravity whatever the body does.
# Java does the same every frame (parent world rotation inverted + a damped swing); these are frozen frames.
HANG_REST = {'hair_back': (-6, 0, 14), 'hair_right': (0, 0, 6), 'hair_left': (0, 0, 22),
             'skirt': (0, 0, 0), 'hem_front': (-11, 0, 0), 'hem_back': (11, 0, 0), 'hem_right': (0, 0, 11),
             'hem_left': (0, 0, -11)}


def _rad(t):
    return tuple(math.radians(v) for v in t)


def _euler(R):
    """MC ZYX angles (radians) of R = Rz * Ry * Rx."""
    y = math.asin(max(-1.0, min(1.0, -R[2, 0])))
    return math.atan2(R[2, 1], R[2, 2]), y, math.atan2(R[1, 0], R[0, 0])


def _wrap(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


def _rest(name):
    return CHAIN_REST[name] if name in CHAIN_REST else HANG_REST[name]


def _world_rot(name, pose):
    chain = []
    n = name
    while n is not None:
        chain.append(n)
        n = PARENT.get(n)
    R = np.eye(3)
    for n in reversed(chain):
        r = _rad(_rest(n))
        p = pose.get(n, (0, 0, 0))
        R = R @ rot_matrix(r[0] + p[0], r[1] + p[1], r[2] + p[2])
    return R


def _dir_rot(d):
    """World rotation whose local +Y (down the strand) points along d; local Z stays as close to world Z as it can."""
    y = np.array(d, float)
    y /= np.linalg.norm(y)
    x = np.cross(y, np.array((0.0, 0.0, 1.0)))
    if np.linalg.norm(x) < 1e-6:
        x = np.array((1.0, 0.0, 0.0))
    x /= np.linalg.norm(x)
    return np.column_stack((x, y, np.cross(x, y)))


def _entry(name, pose, R_target):
    """Additive pose entry (radians) that gives bone `name` the world rotation R_target under `pose`."""
    loc = _euler(_world_rot(PARENT[name], pose).T @ R_target)
    r = _rad(_rest(name))
    return tuple(_wrap(loc[i] - r[i]) for i in range(3)) + (0.0, 0.0, 0.0)


# ------------------------------------------------------------------ poses (radians / texels, ADDED to the rest pose)
# Look each pose is played in: the normal girl ('normal') or the host ('poseida').  Hanging parts follow that look.
POSE_LOOK = {'stand_normal': 'normal', 'hide_under_bed': 'normal', 'dazed': 'normal'}

_POSES = {
    # NORMAL idle: shy, hands held together in front of the skirt, head down and tilted (cancels most of the
    # possessed rest roll), pigeon-toed.  The normal look never shows the raw rest pose: this IS her idle.
    'stand_normal': {
        'head': (0.14, 0.12, 0.2, 0, 0, 0), 'body': (-0.03, 0, 0, 0, 0, 0),
        'right_arm': (-0.3104, -0.0656, 0.0498, 0, 0, 0), 'right_forearm': (-0.246, -0.2228, -1.1263, 0, 0, 0),
        'right_hand': (0.5818, -0.0927, 0.9825, 0, 0, 0), 'left_arm': (-0.2946, -0.1661, 0.1183, 0, 0, 0),
        'left_forearm': (-0.4603, 0.1402, 1.1236, 0, 0, 0), 'left_hand': (0.3855, 0.1633, -0.9244, 0, 0, 0),
    },
    # NORMAL 'casa.cuarto_lucia': lying prone under the bed, only the head and the forearms peek out past its edge;
    # chin up looking at the player, forearms flat on the floor, pointed feet behind.  Belly on y = 24.
    'hide_under_bed': {
        'base': (1.5708, 0, 0, 0, 10.4, 6), 'body': (-0.12, 0, 0, 0, 0, 0), 'neck': (0.5, 0, 0, 0, 0, 0),
        'right_foot': (1.4, 0, 0.1, 0, 0, 0), 'left_foot': (1.4, 0, -0.1, 0, 0, 0),
        'hem_back': (-0.95, 0, 0, 0, 0, 0), 'hem_front': (0.3, 0, 0, 0, 0, 0), 'hem_right': (0, 0, -0.8, 0, 0, 0),
        'hem_left': (0, 0, 0.8, 0, 0, 0), 'head': (-2.3891, 0.1023, 0.1207, 0, 0, 0), 'right_arm': (-0.9942, 0.8197, 1.2798, 0, 0, 0),
        'right_forearm': (-0.543, 0.3302, 0.6399, 0, 0, 0), 'right_hand': (0.035, -0.1146, 0.0282, 0, 0, 0),
        'left_arm': (-0.9055, -0.6675, -1.3317, 0, 0, 0), 'left_forearm': (-1.0614, -0.4358, -0.8424, 0, 0, 0),
        'left_hand': (0.0834, 0.0627, 0.0177, 0, 0, 0),
    },
    # NORMAL after the slipper ('casa.chancleta'): sat down hard on the floor, legs out in a V, skirt pooled round
    # her, hands propping behind, head lolling onto her left shoulder (Java circles it).  Shows dizzy_eyes.
    'dazed': {
        'base': (-0.12, 0, 0.05, 0, 13.6, 0), 'body': (-0.1, 0.1, 0.08, 0, 0, 0),
        'head': (0.25, -0.15, 0.62, 0, 0, 0), 'neck': (0.05, 0, 0.05, 0, 0, 0), 'skirt': (0, 0, 0, 0, -3, 0),
        'hem_front': (-1.1, 0, 0, 0, 0, 0), 'hem_back': (1.36, 0, 0, 0, 0, 0), 'hem_right': (0, 0, 1.18, 0, 0, 0),
        'hem_left': (0, 0, -1.3, 0, 0, 0), 'right_leg': (-1.2631, 0.1289, 0.5309, 0, 0, 0),
        'right_shin': (-0.0806, 0, 0, 0, 0, 0), 'right_foot': (-1.341, 0.987, -0.3389, 0, 0, 0),
        'left_leg': (-1.7245, -0.2181, 0.5009, 0, 0, 0), 'left_shin': (0.0399, 0, 0, 0, 0, 0),
        'left_foot': (-1.0765, 0.3115, 0.306, 0, 0, 0), 'right_arm': (0.3719, 0.627, -0.6638, 0, 0, 0),
        'right_forearm': (-0.4945, 0.6436, 1.1018, 0, 0, 0), 'right_hand': (0.829, -0.5658, 0.3594, 0, 0, 0),
        'left_arm': (-0.4952, -0.1747, 0.1787, 0, 0, 0), 'left_forearm': (1.0682, 0.4837, -1.0168, 0, 0, 0),
        'left_hand': (0.1723, -0.3687, -0.3475, 0, 0, 0),
    },
    # POSSESSED lunge (Java weight = sin(attackAnim * PI)): body pitched and slid forward, the head tipped up so the
    # torn grin faces the player, jaw dropped, right claw raised beside the face (never in front of it), left claw
    # thrust low at the player, fingers splayed
    'attack': {
        'body': (0.42, 0, 0, 0, 0, -1.5), 'head': (-0.5, 0.05, 0.32, 0, 0, 0), 'jaw': (0.85, 0, 0, 0, 0, 0),
        'right_leg': (-0.42, 0, 0, 0, 0, 0), 'right_shin': (0.32, 0, 0, 0, 0, 0), 'left_leg': (0.22, 0, 0, 0, 0, 0),
        'left_shin': (0.12, 0, 0, 0, 0, 0), 'right_arm': (0.2304, 0.4961, 1.7161, 0, 0, 0),
        'right_forearm': (-0.6428, 0.752, 0.2932, 0, 0, 0), 'left_arm': (-1.694, -0.7552, 0.1701, 0, 0, 0),
        'left_forearm': (-0.0436, -1.1403, 0.59, 0, 0, 0), 'right_finger1': (0, 0, 0.35, 0, 0, 0),
        'right_finger4': (0, 0, -0.35, 0, 0, 0), 'right_thumb': (0, 0, 0.3, 0, 0, 0),
        'left_finger1': (0, 0, -0.35, 0, 0, 0), 'left_finger4': (0, 0, 0.35, 0, 0, 0),
        'left_thumb': (0, 0, -0.3, 0, 0, 0), 'hem_front': (0.25, 0, 0, 0, 0, 0), 'hem_back': (0.15, 0, 0, 0, 0, 0),
        'right_hand': (-0.5741, 1.9509, -0.4658, 0, 0, 0), 'left_hand': (-0.5996, -0.6824, 0.4267, 0, 0, 0),
    },
    # POSSESSED: head thrown back, jaw at full drop, arms flung back and out, claws splayed
    'scream': {
        'body': (-0.15, 0, 0, 0, 0, 0), 'neck': (-0.15, 0, 0, 0, 0, 0), 'head': (-0.45, 0, 0.3, 0, 0, 0),
        'jaw': (1, 0, 0, 0, 0, 0), 'right_arm': (0.35, 0, 0.6, 0, 0, 0), 'left_arm': (0.35, 0, -0.6, 0, 0, 0),
        'right_forearm': (-0.35, 0, 0.2, 0, 0, 0), 'left_forearm': (-0.35, 0, -0.2, 0, 0, 0),
        'right_finger1': (0, 0, 0.4, 0, 0, 0), 'right_finger4': (0, 0, -0.4, 0, 0, 0),
        'left_finger1': (0, 0, -0.4, 0, 0, 0), 'left_finger4': (0, 0, 0.4, 0, 0, 0),
    },
    # POSSESSED on the ceiling: belly to the ceiling, back to the floor, hands and feet planted on y = -24 (the top
    # of her 1.5-block box), elbows and knees out like a spider, the head hanging UPSIDE DOWN below the neck with
    # the face forward and the jaw ajar, the mane and the hem falling toward the player
    'crawl_ceiling': {
        'base': (1.5708, 0, 3.1416, 0, -21, 6), 'body': (0.08, 0, 0, 0, 0, 0), 'jaw': (0.35, 0, 0, 0, 0, 0),
        'neck': (-0.9282, 0, 0, 0, 0, 0), 'head': (-0.9719, 0.2083, 0.4968, 0, 0, 0),
        'right_arm': (0.2312, 0.1852, 1.6873, 0, 0, 0), 'right_forearm': (-0.8114, 0.6239, 0.6242, 0, 0, 0),
        'left_arm': (0.2378, 0.158, -1.5376, 0, 0, 0), 'left_forearm': (-0.7633, -0.4624, -1.407, 0, 0, 0),
        'right_leg': (-0.4514, -0.8538, 1.4823, 0, 0, 0), 'right_shin': (-1.0196, 0, 0, 0, 0, 0),
        'right_foot': (0.4636, -1.2607, 0.5363, 0, 0, 0), 'left_leg': (-0.5734, 0.8537, -1.4821, 0, 0, 0),
        'left_shin': (-0.9149, 0, 0, 0, 0, 0), 'left_foot': (1.409, -0.0835, 0.4056, 0, 0, 0),
        'right_finger1': (0.9, 0, 0, 0, 0, 0), 'right_finger2': (0.9, 0, 0, 0, 0, 0),
        'right_finger3': (0.9, 0, 0, 0, 0, 0), 'right_finger4': (0.9, 0, 0, 0, 0, 0),
        'left_finger1': (0.9, 0, 0, 0, 0, 0), 'left_finger2': (0.9, 0, 0, 0, 0, 0),
        'left_finger3': (0.9, 0, 0, 0, 0, 0), 'left_finger4': (0.9, 0, 0, 0, 0, 0),
    },
    # POSSESSED floor crab walk (Java 'spider', crawl / climbing): head first, belly up, shoulders high, arms bent
    # back down to the floor beside the head (claws planted), knees up behind, head hanging upside down, face forward
    'spider': {
        'base': (2.1365, 0, 3.1416, 0, 2.9966, 5), 'jaw': (0.45, 0, 0, 0, 0, 0), 'body': (0.45, 0, 0, 0, 0, 0),
        'neck': (-1.1921, 0, 0, 0, 0, 0), 'head': (-1.1135, -0.2183, 0.2516, 0, 0, 0),
        'right_arm': (1.1882, -0.282, 0.7533, 0, 0, 0), 'right_forearm': (0.4576, 0.5335, -0.4679, 0, 0, 0),
        'left_arm': (1.3546, 0.4798, -0.1529, 0, 0, 0), 'left_forearm': (-0.4133, 0.7124, 0.3575, 0, 0, 0),
        'right_leg': (-0.2331, 0.5809, 0.4774, 0, 0, 0), 'right_shin': (0.6935, 0, 0, 0, 0, 0),
        'right_foot': (2.1288, 0.0061, 0.9169, 0, 0, 0), 'left_leg': (-0.3552, -0.5806, -0.4774, 0, 0, 0),
        'left_shin': (0.7983, 0, 0, 0, 0, 0), 'left_foot': (2.1458, 0.2569, -0.8655, 0, 0, 0),
        'right_hand': (-0.2229, 0.3213, -0.7488, 0, 0, 0), 'left_hand': (0.409, 0.8963, 0.4734, 0, 0, 0),
    },
    # POSSESSED exorcism hover: lifted half a block (base dy -16), arched back, head thrown back and rolled, jaw
    # ajar, arms spread wide and limp from the elbow, legs together with the toes pointing down, hem flared, the
    # mane floating up and back as if under water
    'levitate': {
        'base': (0.05, 0, 0, 0, -16, 0), 'body': (-0.22, 0, 0, 0, 0, 0), 'neck': (-0.25, 0, 0, 0, 0, 0),
        'head': (-0.35, 0.12, 0.35, 0, 0, 0), 'jaw': (0.3, 0, 0, 0, 0, 0), 'right_leg': (0.12, 0, 0.06, 0, 0, 0),
        'left_leg': (0.04, 0, -0.1, 0, 0, 0), 'right_shin': (0.3, 0, 0.1, 0, 0, 0),
        'left_shin': (0.4, 0, -0.08, 0, 0, 0), 'right_foot': (0.75, 0.25, 0, 0, 0, 0),
        'left_foot': (0.8, -0.1, 0, 0, 0, 0), 'hem_front': (-0.3, 0, 0, 0, 0, 0), 'hem_back': (0.3, 0, 0, 0, 0, 0),
        'hem_right': (0, 0, 0.32, 0, 0, 0), 'hem_left': (0, 0, -0.32, 0, 0, 0),
        'right_arm': (-0.4078, 0.7384, 0.5331, 0, 0, 0), 'right_forearm': (0.8037, 0.4649, -0.0039, 0, 0, 0),
        'right_hand': (0.4741, 0.4715, 0.2181, 0, 0, 0), 'left_arm': (-0.2569, 0.0803, -0.9991, 0, 0, 0),
        'left_forearm': (-0.2121, 0.5499, 0.4925, 0, 0, 0), 'left_hand': (-0.3944, 0.6781, 0.3308, 0, 0, 0),
        'right_finger1': (0.25, 0, 0.2, 0, 0, 0), 'right_finger4': (-0.25, 0, -0.15, 0, 0, 0),
        'left_finger1': (0.2, 0, -0.25, 0, 0, 0), 'left_finger4': (-0.3, 0, 0.15, 0, 0, 0),
    },
    # legacy name used by PoseidaModel.java for the exorcism: = levitate WITHOUT the lift (Java adds its own -6 bob)
    'float': {
        'base': (0.05, 0, 0, 0, 0, 0), 'body': (-0.22, 0, 0, 0, 0, 0), 'neck': (-0.25, 0, 0, 0, 0, 0),
        'head': (-0.35, 0.12, 0.35, 0, 0, 0), 'jaw': (0.3, 0, 0, 0, 0, 0), 'right_leg': (0.12, 0, 0.06, 0, 0, 0),
        'left_leg': (0.04, 0, -0.1, 0, 0, 0), 'right_shin': (0.3, 0, 0.1, 0, 0, 0),
        'left_shin': (0.4, 0, -0.08, 0, 0, 0), 'right_foot': (0.75, 0.25, 0, 0, 0, 0),
        'left_foot': (0.8, -0.1, 0, 0, 0, 0), 'hem_front': (-0.3, 0, 0, 0, 0, 0), 'hem_back': (0.3, 0, 0, 0, 0, 0),
        'hem_right': (0, 0, 0.32, 0, 0, 0), 'hem_left': (0, 0, -0.32, 0, 0, 0),
        'right_arm': (-0.4078, 0.7384, 0.5331, 0, 0, 0), 'right_forearm': (0.8037, 0.4649, -0.0039, 0, 0, 0),
        'right_hand': (0.4741, 0.4715, 0.2181, 0, 0, 0), 'left_arm': (-0.2569, 0.0803, -0.9991, 0, 0, 0),
        'left_forearm': (-0.2121, 0.5499, 0.4925, 0, 0, 0), 'left_hand': (-0.3944, 0.6781, 0.3308, 0, 0, 0),
        'right_finger1': (0.25, 0, 0.2, 0, 0, 0), 'right_finger4': (-0.25, 0, -0.15, 0, 0, 0),
        'left_finger1': (0.2, 0, -0.25, 0, 0, 0), 'left_finger4': (-0.3, 0, 0.15, 0, 0, 0),
    },
    # legacy PoseidaModel.java 'headturn' (ACT_HEADSPIN): the head turns all the way round; blend the weight 0 -> 1
    'headturn': {
        'head': (0, math.pi, 0, 0, 0, 0),
    },
}

# braids in the normal idle: the upper plait drapes forward-and-out over the front of the shoulder, the tip hangs
BRAID_DROP = {'right': (-0.2, 1.0, -0.62), 'left': (0.2, 1.0, -0.62)}
TIP_DROP = (0.0, 1.0, -0.06)
# pose -> side -> (upper, tip) world directions when they differ from the idle drape
BRAID_DIR = {
    # lying prone: the plaits fall to the floor beside her face and lie forward along it
    'hide_under_bed': {'right': ((-0.5, 1.0, -0.45), (-0.3, -0.03, -1.0)), 'left': ((0.5, 1.0, -0.45), (0.3, -0.03, -1.0))},
}
# pose -> mane bone -> (xRot, yRot, zRot) world-space swing added to its rest orientation
HAIR_SWING = {
    'levitate': {'hair_back': (0.75, 0, 0), 'hair_right': (0.25, 0, 0.55), 'hair_left': (0.3, 0, -0.6)},   # floats up
    'float': {'hair_back': (0.75, 0, 0), 'hair_right': (0.25, 0, 0.55), 'hair_left': (0.3, 0, -0.6)},
    'attack': {'hair_back': (0.35, 0, 0), 'hair_right': (0.2, 0, 0.12), 'hair_left': (0.2, 0, -0.12)},   # lags the lunge
    'scream': {'hair_back': (0.25, 0, 0), 'hair_right': (0.1, 0, 0.3), 'hair_left': (0.1, 0, -0.3)},
    # crab walk: the mane hangs from the upside-down head and drags forward along the floor ahead of her face
    'spider': {'hair_back': (-1.3, 0, 0), 'hair_right': (-1.35, 0, 0.3), 'hair_left': (-1.5, 0, -0.3)},
}
# pose -> hem panel -> world rotation: in the inverted poses the hem falls with gravity (back + sides hang plumb, the
# front panel, now on top, folds down over the hips)
_DOWN = np.eye(3)
HEM_HANG = {p: {'hem_back': _DOWN, 'hem_right': rot_matrix(0, 0, 0.12), 'hem_left': rot_matrix(0, 0, -0.12)}
            for p in ('crawl_ceiling', 'spider')}


def _solve_braid_rest():
    Wp = _world_rot('head', _POSES['stand_normal'])
    for side in ('right', 'left'):
        Rr = _dir_rot(BRAID_DROP[side])
        HANG_REST[f'braid_{side}'] = tuple(round(math.degrees(a), 2) for a in _euler(Wp.T @ Rr))
        HANG_REST[f'braid_{side}_tip'] = tuple(round(math.degrees(a), 2) for a in _euler(Rr.T @ _dir_rot(TIP_DROP)))


_solve_braid_rest()


def hang_entries(pname, pose):
    out = {}
    if POSE_LOOK.get(pname, 'poseida') == 'normal':
        for side in ('right', 'left'):
            up, tip = BRAID_DIR.get(pname, {}).get(side, (BRAID_DROP[side], TIP_DROP))
            Rr = _dir_rot(up)
            out[f'braid_{side}'] = _entry(f'braid_{side}', pose, Rr)
            out[f'braid_{side}_tip'] = _entry(f'braid_{side}_tip', dict(pose, **{f'braid_{side}': out[f'braid_{side}']}),
                                              _dir_rot(tip))
    else:
        for h in ('hair_back', 'hair_right', 'hair_left'):
            R0 = _world_rot(h, {})
            sw = HAIR_SWING.get(pname, {}).get(h)
            if sw:
                R0 = rot_matrix(*sw) @ R0
            out[h] = _entry(h, pose, R0)
    for h, R in HEM_HANG.get(pname, {}).items():        # upside down: the nightgown hem falls toward the floor
        out[h] = _entry(h, pose, R)
    return {k: v for k, v in out.items() if max(abs(a) for a in v) > 1e-3}


def _round(t):
    return tuple(round(float(v), 4) for v in t)


# ------------------------------------------------------------------ B3: 'ceiling_crawl' and 'sit_chair'
def _model_fk(pose):
    """World 4x4 per bone of the built model under an additive pose table (Euler sums, offsets on the pivot)."""
    m = build(variant='poseida')
    out = {}

    def walk(b, M):
        p = tuple(pose.get(b.name, (0, 0, 0, 0, 0, 0))) + (0,) * 6
        T = np.eye(4)
        T[:3, 3] = (b.pivot[0] + p[3], b.pivot[1] + p[4], b.pivot[2] + p[5])
        R = np.eye(4)
        R[:3, :3] = rot_matrix(math.radians(b.rot[0]) + p[0], math.radians(b.rot[1]) + p[1], math.radians(b.rot[2]) + p[2])
        W = M @ T @ R
        out[b.name] = (W, b)
        for c in b.children:
            walk(c, W)
    for root in m.roots:
        walk(root, np.eye(4))
    return out


def _local_entry(fk, name, R_world):
    """Additive entry giving bone `name` the world rotation R_world (its parent as in `fk`)."""
    W, b = fk[name]
    P = fk[b.parent.name][0][:3, :3] if b.parent is not None else np.eye(3)
    loc = _euler(P.T @ R_world)
    r = [math.radians(a) for a in b.rot]
    return tuple(_wrap(loc[i] - r[i]) for i in range(3)) + (0.0, 0.0, 0.0)


def _axis_rot(axis, ang):
    a = np.array(axis, float)
    a /= np.linalg.norm(a)
    K = np.array([[0, -a[2], a[1]], [a[2], 0, -a[0]], [-a[1], a[0], 0]])
    return np.eye(3) + math.sin(ang) * K + (1 - math.cos(ang)) * (K @ K)


def _bent_wrong(base, flip=2.3):
    """crawl_ceiling with every elbow and knee swung round the shoulder->wrist / hip->ankle line by `flip` radians
    (hands and feet stay planted on the plaster, the joints now point the wrong way) and the face turned DOWN to the
    floor (the top of the skull forward, the chin back toward her chest), tipped onto one side."""
    pose = {k: tuple(v) + (0,) * (6 - len(v)) for k, v in base.items()}
    for root, mid, end, sgn in (('right_arm', 'right_forearm', 'right_hand', 1), ('left_arm', 'left_forearm', 'left_hand', -1),
                                ('right_leg', 'right_shin', 'right_foot', -1), ('left_leg', 'left_shin', 'left_foot', 1)):
        fk = _model_fk(pose)
        S = fk[root][0][:3, 3]
        E = fk[end][0][:3, 3]
        keep_end = fk[end][0][:3, :3]
        Q = _axis_rot(E - S, flip * sgn)
        pose[root] = _local_entry(fk, root, Q @ fk[root][0][:3, :3])
        fk = _model_fk(pose)
        pose[end] = _local_entry(fk, end, keep_end)
    fk = _model_fk(pose)
    face_down = rot_matrix(math.pi / 2, 0, 0) @ rot_matrix(0, 0, 0.42)
    pose['head'] = _local_entry(fk, 'head', face_down)
    pose['jaw'] = (0.55, 0, 0, 0, 0, 0)
    return pose


_POSES['ceiling_crawl'] = _bent_wrong(_POSES['crawl_ceiling'])
HEM_HANG['ceiling_crawl'] = HEM_HANG['crawl_ceiling']
# the face looks DOWN: the mane must not curtain it, so it is swept back along the plaster and out to the sides
HAIR_SWING['ceiling_crawl'] = {'hair_back': (1.45, 0, 0), 'hair_right': (0.9, 0, 1.1), 'hair_left': (0.9, 0, -1.1)}

# NORMAL at the dinner table (Act 2-3, silla_4): sitting on a chair seat at the height of her hips (0.5 block: the
# entity stands on the chair's block, Java lifts nothing), thighs level, shins straight down with the feet dangling
# (she is small), hands in her lap, head bowed: she does not look at you.
_POSES['sit_chair'] = {
    'base': (0, 0, 0, 0, 0.5, 0), 'body': (0.06, 0, 0, 0, 0, 0), 'head': (0.32, 0.1, 0.22, 0, 0, 0),
    'right_leg': (-1.5708, 0.06, 0, 0, 0, 0), 'left_leg': (-1.5708, -0.06, 0, 0, 0, 0),
    'right_shin': (1.5708, 0, 0, 0, 0, 0), 'left_shin': (1.5708, 0, 0, 0, 0, 0),
    'hem_front': (-1.2, 0, 0, 0, 0, 0), 'hem_back': (0.2, 0, 0, 0, 0, 0),
    'right_arm': (-0.62, -0.08, 0.06, 0, 0, 0), 'right_forearm': (-0.55, -0.1, -0.6, 0, 0, 0),
    'right_hand': (0.4, 0, 0.6, 0, 0, 0), 'left_arm': (-0.62, 0.08, -0.06, 0, 0, 0),
    'left_forearm': (-0.55, 0.1, 0.6, 0, 0, 0), 'left_hand': (0.4, 0, -0.6, 0, 0, 0),
}
POSE_LOOK['sit_chair'] = 'normal'


POSES = {k: {b: _round(v) for b, v in dict(p, **hang_entries(k, p)).items()} for k, p in _POSES.items()}

ANIM_NOTES = """Lucia (PoseidaEntity, and the normal Lucia NPC on the same model) -- animation notes.  Units: radians, offsets in
model texels (2x density inside scale_root: 2 texels = 1 vanilla pixel, 32 texels = 1 block).  t = ageInTicks,
s = walk speed 0..1.  Every pose is ADDED to the rest pose.  The REST pose is the possessed stance: hunched 7 deg, head
rolled 16 deg onto her right shoulder, right shoulder dropped, spider claws hanging past the knees.

Looks (VARIANT_MATS; Java picks the texture by the entity's variant index = FamilyEntity.LOOK_NORMAL / LOOK_POSSESSED)
* 0 'normal'  -> poseida.png.  The sweet eight-year-old: brown eyes, rosy cheeks, shy closed smile, chestnut braids
  with red yarn ties, cream rosebud nightgown under the Nona's red sweater (cream heart, sleeves over her hands).
  poseida_eyes.png is EMPTY in this look (nothing glows): skip the glow layer for variant 0.
* 1 'poseida' -> poseida_poseida.png + poseida_poseida_eyes.png.  The host: plaster skin, torn grin, glowing white
  eyes, black mane, claws, the sweater sooted and BURNED THROUGH on the chest (where the heart was), forearm sleeves
  burned off at the elbows.  Emissive: the eye whites, the embers on the burn rim / burned lips / sleeve edges.
  The swap normal <-> poseida happens behind ActorSwap's flash + smoke (texture + toggles change on the same frame).

Toggles (ModelPart.visible).  Every frame: start from TOGGLE_DEFAULT, apply VARIANT_TOGGLES[look], then
POSE_TOGGLES[pose].  Hiding a parent hides its children.
* braid_right (+ braid_right_tip), braid_left (+ braid_left_tip): the two plaits with red yarn ties.  'normal' only.
* right_mitt, left_mitt: short child fingers held together + thumb, peeking out of the sweater cuffs.  'normal' only.
* hair_back, hair_right, hair_left: the tangled black mane (back curtain + two side locks).  'poseida' only.
* right_claw, left_claw: holders of right/left_thumb + right/left_finger1..4, the long black-nailed claws.  'poseida'
  only.
* sweater_burn: charred, curled lips of the hole burned in the chest + one melted strand hanging off.  'poseida' only.
* dizzy_eyes: two '@ @' swirl planes floating over the eyes.  Only in pose 'dazed' (normal look); hide them again
  when she comes round.
Differences that need NO toggle (alpha in the possessed texture): the hole through the sweater (the stained nightgown
shows inside), the forearm sleeves and cuffs burned away, the shredded hem, the long fringe strand over her right eye.
JAW_LOCKED_VARIANTS = ('normal',): in the normal look NEVER move the jaw (the smile is painted across the seam):
drop the jaw values of every pose and the idle chatter for variant 0; she "talks" with tiny head bobs (head xRot
+0.04 on each syllable).

Bones
* base (root, pelvis, pivot y 8): carries everything.  PoseidaModel already lifts it for the exorcism
  (offset dy -6 * w + bob).  The contact-solved poses rotate and move it (prone, seated, inverted, hover).
* right_leg / left_leg (hips; knock-kneed rest), right_shin / left_shin (knees, with the bony knee cap), right_foot /
  left_foot (ankles; pigeon-toed rest, the right turned in 18 deg).  Normal walk: small shy steps,
  walk(..., 0.45 * s, 0.15 * s), feet keep their toe-in.  Possessed walk: the existing stiff walk (0.6).
* skirt: the two ruffled tiers (static on the pelvis).  Walk: counter-yaw yRot = -sin(walk) * 0.04 * s.
* hem_front, hem_back, hem_right, hem_left: the flared hem panels hinged under tier 2 (lace in 'normal', shredded in
  'poseida').  Cloth: ripple("hem_", t, 0.09, 1.2, 0.04, 0.03, -0.03 * s); flare out more on the attack lunge and
  in the hover.  The inverted poses carry them hanging with gravity; 'dazed' spreads them flat on the floor;
  'hide_under_bed' folds them in over her legs.
* body (torso: nightgown bodice + lace collar + sweater body, ribbed waistband and neck): breathing.  Normal: xRot
  += sin(t * 0.08) * 0.015.  Possessed: ragged, xRot += sin(t * 0.3) * 0.02 plus a 0.06 jerk every 3-6 s.
* sweater_burn (child of body, toggle): no motion.  Optional: flicker the ember alpha of the glow layer.
* neck: look(s, 0.4) (already in PoseidaModel).
* head: rest roll -16 deg.  Possessed idle: slow zRot drift sin(t * 0.04) * 0.25 (existing) + a 2-tick SNAP of
  +-0.3 every 4-8 s.  Normal idle: 'stand_normal' already straightens it to a shy tilt; add curious tilts zRot
  +-0.08 over 2-3 s.  'dazed': circle it, rot(head, sin(t * 0.25) * 0.12, 0, cos(t * 0.25) * 0.15), fading over 3 s.
* jaw (possessed only): hinges down along the ear-to-ear tears (xRot).  Idle chatter (sin(t * 0.07) * 0.5 + 0.5) *
  0.08 (existing).  The double-voice lines ("El te llamo. El tiene muchas voces."): open 0.45 on the stressed
  syllables with a 1-tick 0.05 jitter (two mouths at once).  attack 0.85, scream 1.0.  Locked in 'normal'.
* dizzy_eyes (child of head, toggle): no motion; optional slow spin zRot += t * 0.3 on the whole bone reads as
  swirling eyes.
* hair_back, hair_right, hair_left (children of head, possessed): GRAVITY.  Every frame set each root to the inverse
  of its parent's world rotation times its rest world rotation (= hang_entries() in this file; the poses carry
  the frozen result), then add the swing: ripple("hair", t, 0.08, 1.0, 0.04, 0.03, 0) (existing) + a damped
  pendulum kicked by head snaps (lag 3 ticks).  They float up in 'levitate' / 'float' (HAIR_SWING) and drag
  forward along the floor in 'spider'.
* braid_right, braid_left (children of head, normal) and braid_right_tip, braid_left_tip: the plaits.  Their rest
  rotations are solved so that, in 'stand_normal', the upper plait drapes forward over the front of the shoulder
  and the tip hangs plumb (pose entries are then 0).  Same gravity rule as the mane (hang_entries) + a pendulum:
  root follows the head with 2-tick lag, tip with 4-tick lag and 1.5x amplitude; walking bounces them
  xRot +-0.06 per step.
* right_arm / left_arm (shoulders; the right one dropped 1 texel, the left 1 higher): walk swing 0.25 (existing).
* right_forearm / left_forearm (elbows): carry the forearm sleeve and the ribbed cuff (the left elbow has the Nona's
  darn in 'normal').
* right_hand / left_hand (wrists): palm cube.  Idle tremor zRot sin(t * 0.9) * 0.02 in 'poseida'.
* right_claw / left_claw (toggle holders, pivot at the wrist): no motion of their own; optional xScale/yScale
  1 -> 1.15 over 3 ticks on the attack ("the claws grow").
* right_thumb, right_finger1..4 / left_thumb, left_finger1..4: the spider claws.  Idle twitch
  ripple("right_finger" / "left_finger", ...) (existing); splayed in attack / scream / levitate; laid flat along
  the plaster in 'crawl_ceiling'.
* right_mitt / left_mitt (toggle, normal): short fingers + thumb; static.

Poses (POSES; hanging parts already carry their gravity entries)
* stand_normal ('normal'): her IDLE in the normal look -- apply it at weight 1 whenever variant 0 is not in another
  state (never show the raw possessed rest pose with the normal texture).  Shy: head down and tilted (cancels most
  of the rest roll), hands held together in front of the skirt (heart on the sweater stays visible), pigeon-toed.
  Walking: keep it at weight 1 and add the small walk on top (her hands stay together).
* hide_under_bed ('normal', 'casa.cuarto_lucia'): lying prone, belly on the floor (y 24), chin up looking at the
  player, forearms flat on the floor in front of her face, pointed feet behind, plaits lying forward along the
  floor.  Footprint from the origin (= the pelvis): head and hands 0.69 block forward (-Z), feet 0.82 block back,
  body 0.35 block high, head 0.79.  Spawn at the casa marker 'lucia_bajo_cama' facing out from under the bed (her
  body under the bed may clip into it; only head and forearms need to show).  No physics, no walk.  While she
  speaks: head bob only.
* dazed ('normal', after the slipper, 'casa.chancleta'): sat down hard on the floor (bottom on y 24), legs out in a
  V, the hem spread flat round her, hands propping behind, head lolling to her left; shows dizzy_eyes; Java circles
  the head (see head).  Footprint: legs 0.5 block forward.  Freed line ("Ofelia tenia miedo...") from this pose;
  then blend to stand_normal over 20 ticks and hide dizzy_eyes.
* attack ('poseida'): weight = sin(attackAnim * PI) (existing).  Body pitched 0.42 and slid 1.5 forward, legs in a
  lunge stride, the head tipped up so the torn grin and glowing eyes face the player, jaw dropped 0.85, right claw
  raised high beside the face, left claw low and forward, all claws splayed, the mane lagging behind.  Reaches
  1 block forward.
* scream ('poseida'): head thrown back, jaw at full drop (1.0), arms flung back and out, claws splayed.
* crawl_ceiling ('poseida', 'casa.lucia': "en el techo, caminando como arana"): INVERTED.  Base rolled upside down
  (belly to the ceiling, back to the floor), hands and feet planted on y = -24 = the TOP of her 1.5-block box,
  elbows and knees out like a spider, claws flat on the plaster, the head hanging UPSIDE DOWN below the neck with the
  face forward and the jaw ajar, the mane and the hem falling toward the player (the hair reaches the bottom of the
  box).  Java: give the entity noGravity and keep its box top against the ceiling (y = ceilingY - 1.5); move it
  along the ceiling with the spider scuttle on top: hands/feet in diagonal pairs, rot(right_arm, a) / rot(left_leg,
  a) and rot(left_arm, -a) / rot(right_leg, -a) with a = cos(walk * 1.4) * 0.35 * s (same as 'spider'), plus the
  head twitch yRot sin(t * 0.9) * 0.12.  Enter/leave it behind a flash, or blend over 10 ticks (the base rolls
  through 180 deg: reads as her flipping up onto the ceiling).
* spider ('poseida', legacy name used by PoseidaModel for ACT_CRAWL and wall climbing): the Exorcist crab walk on
  the floor -- head first, belly up, shoulders high and hips low, arms bent back down to the floor beside the head
  (claws planted), knees up behind, the head hanging upside down between the arms with the face forward, the mane
  dragging forward along the floor.  Reaches ~1 block forward.  The existing diagonal scuttle applies on top.
* levitate ('poseida', the hover): lifted half a block (base dy -16: the toes 0.39 block above the floor), arched
  back, head thrown back and rolled, jaw ajar, arms spread wide and limp from the elbows, legs together with the
  toes pointing down, hem flared, the mane floating up and back as if under water.  Add a slow bob dy
  sin(t * 0.1) * 1.5 and a body roll sin(t * 0.05) * 0.04.
* float ('poseida', legacy name used by PoseidaModel for the exorcism, ACT_EXORCISM): = levitate WITHOUT the lift
  (PoseidaModel adds its own -6 bob and the convulsions).
* headturn ('poseida', legacy ACT_HEADSPIN): head yRot + PI; blend the weight 0 -> 1 so the head turns all the way
  round (the mane follows the back of the head and ends up hanging in front of her chest).

Jumpscare portrait: FOCUS 'head', look 'poseida', pose 'attack' (grin + glowing eyes full frame) or 'crawl_ceiling'
(the upside-down face).  Thumbnail of the normal look: pose 'stand_normal' or 'hide_under_bed'.

Java checklist for PoseidaModel / renderer
1. Texture + glow by variant: 0 -> poseida.png (no glow), 1 -> poseida_poseida.png + poseida_poseida_eyes.png.
2. Toggles every frame (TOGGLE_DEFAULT -> VARIANT_TOGGLES -> POSE_TOGGLES).  Without this every look's geometry
   shows at once (braids + mane + mitts + claws + burned lips + swirl eyes).
3. Variant 0: base state = stand_normal at weight 1; jaw locked; no spider/headturn/attack.
4. The poses spider / headturn / float / attack used by the current PoseidaModel now exist; add crawl_ceiling,
   levitate, scream, hide_under_bed, dazed for the scripted beats.
"""
