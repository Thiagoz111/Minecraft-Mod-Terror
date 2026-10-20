"""Choripan, version completa -- the possessed family dachshund, stretched into a 4.6-block demon (DEAD LINE).

Authored at 2x texel density (model.scale = 0.5).  +Y down, ground y = 24, faces -Z, right_* on -X.

Design
------
Silhouette (side): a sausage dog pulled like taffy and tied off into links like a string of chorizos.  From the
nose (z ~ -72) to the tail tip (z ~ +74) the body is a CHAIN of bones: the head on a raised, stretched neck, the
chest (seg1, still wearing the shreds of the Nona's red sweater) on two short, bowed, perfectly normal dachshund
legs, then five fur links (seg2..seg6) and the rump (hips).  Every link is tied to the next by a band of hairless,
stretched, see-through pink-grey skin: a rib cage of partial rib arcs and a knobbly spine ridge, then a pinched
waist where the skin is pulled thinnest.  The chain carries a hunch: it climbs from the chest to a crest at
seg3/seg4, sags at seg5 and lifts again into the rump, and the links taper (chest 14 wide -> waist 11 -> hips 13).
Three pairs of thin, far-too-long, NOT symmetrical human arms grow out of the flanks of seg3, seg5 and the hips:
spider elbows above the spine, knobbly elbows and wrists, dirty hands -- one flat, one on its knuckles, one
clawing on its fingertips, one with an extra joint and a wrist broken backwards.  The dachshund tail (now big
enough to read) still sticks up and wags.

Face (the clip close-up and the jumpscare portrait): it must still be Choripan.  The cute form's identity markers
are kept -- tan muzzle and jowls, chunky tan brows (inner ends raised: puppy eyes), big almond eyes with a 2x2
glint, one big round black nose -- but the eyes are milk-white with tiny red pinpoint pupils (2x2, one hot texel,
emissive layer 'eyes') looking slightly inward, and the tan muzzle is TORN OPEN from the nose to the throat into
four flaps (jaw_upper_right/left, jaw_lower_right/left): the nose is cut in half down a raw red seam, each flap
is lined with crooked needle teeth in two offset rows (zero-thickness planes), red gums, a ridged palate, a deep
red throat and a long black tongue (tongue + tongue_tip).
"""
import math

import numpy as np

from mcmodel import Model, hash3, face_light, pick, rot_matrix
from rig import Rig
from paint import hx, mix


def pal(*h):
    return [hx(c) for c in h]


# ------------------------------------------------------------------ palettes (dark -> light, hue shifted)
FUR = pal('#260b07', '#3f150b', '#5c2111', '#7a3a1c', '#8f4622', '#a6552a', '#c06a33', '#d88a4c', '#ecab6c')
TAN = pal('#7d4320', '#9a5728', '#b46c33', '#c98243', '#d99a57', '#e6b16d', '#f0c687', '#f8dcab')
SKIN = pal('#26141f', '#3e2232', '#583443', '#734b55', '#8e6568', '#ab8282', '#c69e99', '#d9b6ab', '#e9cdbf')
PURPLE = hx('#4a2b52')
ORGAN = pal('#2c0f22', '#4a1a2e', '#66283a', '#7e3a46')
HUMAN = pal('#271a1d', '#443034', '#654a4c', '#876866', '#a8857f', '#c3a198', '#d9bcb0', '#ead4c8')
VEIN = pal('#3b3468', '#4f4583', '#6a578f')
BONE = pal('#6e6252', '#9c907c', '#c9bea8', '#e6dcc8', '#f8f2e4')
RAW = pal('#2e050b', '#561019', '#80202a', '#a8383e', '#c95a5a', '#e08a82')
BLOOD = pal('#1c0205', '#3d0609', '#640b11', '#8c1419')
GUM = pal('#300510', '#5a0c1c', '#8a1628', '#b52a38', '#d4484e', '#e8706c')
TEETH = pal('#4e463a', '#857b66', '#b9b09a', '#ddd6c2', '#f4efe0', '#fffef8')
TONGUE = pal('#030205', '#0c0910', '#18121d', '#261d2c', '#3a2e42', '#594a66', '#8a7a9c')
THROAT = pal('#000000', '#0c0105', '#1e040a', '#3a0812', '#5c0f1b')
NOSE = pal('#050304', '#0d090b', '#191215', '#2a2125', '#43383d', '#6e6268', '#a89ca3', '#d8d0d6')
LIP = pal('#08060a', '#16121a', '#2a2228')
MILK = pal('#56606e', '#7d8894', '#a3adb6', '#c3cbd0', '#dce1e2', '#eef0ee', '#ffffff')
PUPIL = hx('#ff2a14')
PUPIL_D = hx('#a80d10')
BLOODSHOT = hx('#c4706c')
KNIT = pal('#22040a', '#3e0810', '#5e0e18', '#7e1620', '#9e2228', '#bb3432', '#d24e44', '#e47060')
KNIT_W = pal('#8f877e', '#bfb7ab', '#e3dccf', '#f6f1e6')
CELESTE = pal('#1d3a5c', '#2f5f8f', '#4f8fc4', '#75b2e2', '#a4d2f2')
BRASS = pal('#3b2a10', '#7a5a22', '#b8913e', '#e6c66a', '#fff0b0')
PAD = pal('#120c0e', '#241a1c', '#3a2c2c', '#544040')
NAIL = pal('#0e0a08', '#2a221c', '#4e4436', '#7a6c58', '#a29478')
DIRT = hx('#2a1d14')


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
    """Authoring coordinates of the texel (the bone's straightened rest frame, before bone rotations)."""
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


def art(rows, cmap, i, j, flip=False):
    row = rows[j]
    ch = row[len(row) - 1 - i] if flip else row[i]
    return cmap.get(ch)


# ------------------------------------------------------------------ fur
def strands(across, along, seed, clump=2.0, brk=3.5):
    """Directional fur: clumps `clump` texels wide, broken every ~`brk` texels along the lay."""
    col = math.floor(across / clump)
    off = hash3(col, 7, 0, seed) * brk
    k = hash3(col, math.floor((along + off) / brk), 0, seed)
    v = (k - 0.5) * 0.2
    if (along + off) % brk < 0.9:
        v -= 0.06                                   # the dark root line of each clump
    return v


def fur_val(ctx, base=0.5):
    """Body fur value: lay runs along Z on the trunk (nose -> tail); a clean dark stripe down the back."""
    x, y, z = A(ctx)
    f = ctx.face
    v = base + face_light(ctx) * 1.1
    s = cseed(ctx) % 7
    if f in ('west', 'east'):
        v += strands(y, z, 11 + s)
        v -= clamp((y - (ctx.cube.a0[1] + ctx.cube.size[1] * 0.55)) / 6.0) * 0.12   # belly side darker
    elif f in ('top', 'bottom'):
        if f == 'top' and abs(x) < 2.6:
            return v - 0.2 + strands(x, z, 21 + s) * 0.35          # the dachshund back stripe, kept clean
        v += strands(x, z, 21 + s)
    else:
        v += strands(x, y, 31 + s, 2.0, 3.0)
    if edge(ctx) == 0 and not is_plane(ctx):
        v -= 0.06
    return v


def link_fur(ctx):
    """A fur link: clean coat, 1 jagged texel of torn dark tips at each cut end, blood only on a few links."""
    c = ctx.cube
    f = ctx.face
    t = tag(ctx)
    v = fur_val(ctx, 0.53)
    if t == 'keel':
        v -= 0.07
    lx, ly, lz = local(ctx)
    w, h, d = c.size
    tf, tb = getattr(c, 'tear', (False, False))
    if f in ('front', 'back'):
        torn = tf if f == 'front' else tb
        if not torn:
            return pick(FUR, v - (0.06 if edge(ctx) == 0 else 0))
        if edge(ctx) == 0:
            return pick(FUR, v - 0.16)
        return pick(RAW, 0.38 + hash3(ctx.i, ctx.j, 3, 9) * 0.2)      # the cut meat (mostly hidden in the skin tube)
    across = lx if f in ('top', 'bottom') else ly
    for k, (torn, dist) in enumerate(((tf, lz), (tb, d - lz))):
        if not torn or dist >= 1.0:
            continue
        hh = hash3(math.floor(across), cseed(ctx), k, 13)
        if hh > 0.86 and f != 'bottom':
            return pick(RAW, 0.48)
        if hh > 0.3:
            return pick(FUR, v - 0.22)                               # ragged dark fur tips
    if getattr(c, 'drip', False) and f in ('west', 'east') and d - lz < 2.2 and lz > 0.5:
        col = math.floor(lz) + cseed(ctx)
        if hash3(col, 7, 1, 77) > 0.35 and ly < 1.5 + hash3(col, 8, 2, 78) * 5.0:
            return pick(BLOOD, 2.6 / 4 if ly > 1.0 else 3.4 / 4)
    return pick(FUR, v)


def leg_fur(ctx):
    """Dachshund legs: short shiny fur laid along the limb."""
    x, y, z = A(ctx)
    f = ctx.face
    v = 0.52 + face_light(ctx) * 1.1
    if f in ('front', 'back', 'west', 'east'):
        v += strands(x + z, y, 41 + cseed(ctx) % 5, 1.5, 3.0)
    else:
        v += strands(x, z, 47)
    if edge(ctx) == 0 and not is_plane(ctx):
        v -= 0.06
    if f == 'front' and tag(ctx) == 'shoulder':
        return mix(pick(FUR, v), pick(TAN, v), 0.35)
    return pick(FUR, v)


def tail_mat(ctx):
    """The big wagging tail: dark top stripe, paler underside, a tan tip so the wag reads from far away."""
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    x, y, z = A(ctx)
    v = 0.55 + face_light(ctx) * 1.1
    v += strands(lx + ly, z, 81, 1.5, 3.0)
    if f == 'top':
        v -= 0.14
    if edge(ctx) == 0:
        v -= 0.05
    c = pick(FUR, v)
    if tag(ctx) == 'tip':
        tt = clamp((lz - (d - 4.0)) / 3.0)                           # last ~3 texels go tan
        if f == 'back':
            tt = 1.0
        if f == 'bottom':
            tt = max(tt, 0.4)
        c = mix(c, pick(TAN, 0.55 + face_light(ctx)), tt)
    elif f == 'bottom':
        c = mix(c, pick(TAN, 0.45), 0.35)
    return c


def paw_mat(ctx):
    """Cute dachshund paw: rounded toes (dark grooves), black claws at the front, dark pads underneath."""
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    t = tag(ctx)
    v = 0.55 + face_light(ctx) * 1.1
    if f == 'bottom':
        return pick(PAD, 0.3 + (0.3 if (ctx.i + ctx.j) % 3 == 0 else 0))
    if t == 'toes':
        if f in ('front', 'top'):
            if (ctx.i in (1, 3)) if w == 5 else ctx.i == 2:
                return pick(FUR, v - 0.25)          # grooves between toes
            if f == 'front' and ctx.j == ctx.h - 1:
                return pick(PAD, 0.15 if ctx.i % 2 == 0 else 0.6)   # claw tips
        return mix(pick(FUR, v + 0.04), pick(TAN, v), 0.3)
    if f == 'top' and lz < 2:
        if ctx.i in (1, 3):
            return pick(FUR, v - 0.22)
    if edge(ctx) == 0:
        v -= 0.06
    return pick(FUR, v)


# ------------------------------------------------------------------ stretched skin bands
def vein_on(across, along, seed, amp=1.2, freq=0.42):
    """A connected 1-texel vein meandering along `along` (slope < 1 texel per texel, so it never breaks)."""
    c0 = (hash3(seed, 1, 2, 3) - 0.5) * 4.0
    p = c0 + amp * math.sin(along * freq + seed * 1.7) + 0.5 * amp * math.sin(along * freq * 2.3 + seed)
    return abs(math.floor(across) + 0.5 - p) < 0.5


def skin_mat(ctx):
    """Hairless skin pulled out of the fur: warm pink-grey, striated along the pull, purple underneath,
    see-through (dark organ shapes), connected blue veins, a few stretch tears."""
    x, y, z = A(ctx)
    f = ctx.face
    c_ = ctx.cube
    t = tag(ctx)
    lx, ly, lz = local(ctx)
    w, h, d = c_.size
    pinch = t == 'pinch'
    v = (0.66 if pinch else 0.6) + face_light(ctx) * 0.85
    across = y if f in ('west', 'east') else x
    k = math.floor(across)
    # stretch striations running along the pull
    if k % 2 == 0 and hash3(k, math.floor(z / (2.5 if pinch else 3.5)), 1, 3) > 0.3:
        v -= 0.11
    elif hash3(k, math.floor(z / 2), 4, 3) > 0.82:
        v += 0.07
    if edge(ctx) == 0 and f in ('west', 'east', 'top', 'bottom') and (lz < 1 or lz > d - 1):
        v -= 0.12                                               # crease where it vanishes into the fur
    c = pick(SKIN, v)
    if f == 'bottom':
        c = mix(c, PURPLE, 0.45)
    elif f in ('west', 'east', 'front', 'back') and ly > h * 0.55:
        c = mix(c, PURPLE, 0.32 * (ly - h * 0.55) / (h * 0.45))
    if f in ('west', 'east'):
        sd = cseed(ctx) + (7 if f == 'east' else 0)
        # organs seen through the skin: a soft dark oval (gut loop / lung shadow)
        oz = 1.5 + hash3(sd, 2, 0, 5) * max(0.5, d - 3.0)
        oy = h * (0.45 + hash3(sd, 3, 0, 5) * 0.25)
        r = ((lz - oz) / (2.4 if pinch else 2.8)) ** 2 + ((ly - oy) / (1.6 if pinch else 2.1)) ** 2
        if r < 1.0:
            c = mix(c, ORGAN[1 if r < 0.45 else 2], 0.55 if pinch else 0.42)
        # a stretch tear across the pull: red slit with dark lips
        tz = math.floor(1 + hash3(sd, 4, 0, 5) * max(1.0, d - 2.0))
        ty = math.floor(h * 0.2 + hash3(sd, 5, 0, 5) * h * 0.3)
        if hash3(sd, 6, 0, 5) > 0.35 and math.floor(lz) == tz and ty <= math.floor(ly) <= ty + 2:
            return RAW[2] if math.floor(ly) == ty + 1 else RAW[1]
        if vein_on(ly, z, sd, 1.0, 0.5):
            c = mix(c, VEIN[1], 0.6)
    elif f == 'top':
        if vein_on(lx + 0.5, z, cseed(ctx) + 3, 1.3, 0.38):
            c = mix(c, VEIN[2], 0.45)
    # blood around a rib spike
    for sp in SPIKES:
        if sp[0] == ctx.bone.name and f in ('west', 'east', 'top'):
            dx, dy, dz = x - sp[1], y - sp[2], z - sp[3]
            if abs(dz) < 1.6 and abs(dx) < 1.6 and -1.0 < dy < 3.5 - abs(dz):
                c = BLOOD[2] if abs(dz) < 0.7 else BLOOD[1]
    return c


def rib_mat(ctx):
    """A partial rib arc pushing out under the skin: bone-pale crest on top, fading down the flank."""
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    v = 0.62 + face_light(ctx) * 0.8
    if f == 'bottom':
        return pick(SKIN, 0.28)
    if f in ('front', 'back'):
        if edge(ctx) == 0:
            return mix(pick(SKIN, 0.4), PURPLE, 0.25)            # the fold where it meets the tube
        return pick(SKIN, 0.55)
    c = pick(SKIN, v)
    if f == 'top':
        mid = abs(lx - w / 2) / (w / 2)
        c = mix(c, BONE[3], 0.55 - mid * 0.3)
        if ctx.i in (0, ctx.w - 1):
            c = mix(c, PURPLE, 0.3)
    else:
        tt = ly / h                                               # 0 at the crest, 1 where the arc fades
        c = mix(c, BONE[2], clamp(0.5 - tt * 0.7))
        if ly > h - 1.0:
            c = mix(pick(SKIN, 0.4), PURPLE, 0.3)
    return c


def spine_mat(ctx):
    """The spine ridge on top of a band: vertebra knobs every 2 texels, dark folds between them."""
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    v = 0.6 + face_light(ctx) * 0.8
    knob = (math.floor(lz) % 2 == 0)
    if f == 'top':
        if knob:
            return mix(pick(SKIN, v), BONE[3], 0.6)
        return pick(SKIN, 0.38)
    if f in ('west', 'east'):
        if ly > h - 1.0:
            return mix(pick(SKIN, 0.35), PURPLE, 0.35)
        if ly < 1.0 and knob:
            return mix(pick(SKIN, v), BONE[2], 0.4)
        return pick(SKIN, v - (0.06 if not knob else 0))
    if f in ('front', 'back'):
        return mix(pick(SKIN, 0.5), BONE[2], 0.3)
    return pick(SKIN, 0.3)


def spike_mat(ctx):
    """A broken rib punched out through the skin: sharp pale tip, bloody shaft and base."""
    lx, ly, lz = local(ctx)
    h = ctx.cube.size[1]
    f = ctx.face
    if f == 'top':
        return BONE[4]
    if f == 'bottom':
        return BLOOD[1]
    if ly > h - 2.0:
        return BLOOD[2] if ly > h - 1.0 else RAW[2]
    if ly > h - 3.0 and (ctx.i + ctx.j) % 2 == 0:
        return RAW[3]
    v = 0.85 - ly / h * 0.4 + face_light(ctx)
    return pick(BONE, v)


# ------------------------------------------------------------------ human arms (grown out of the flanks)
def arm_mat(ctx):
    """Long human arm: sickly skin, redder where it tore out of the dog, darker and filthier toward the hand,
    knobbly elbow/wrist bones, connected veins, an ulna ridge, cracked black nails."""
    c = ctx.cube
    f = ctx.face
    t = tag(ctx)
    lx, ly, lz = local(ctx)
    w, h, d = c.size
    v = 0.56 + face_light(ctx) * 0.9
    if edge(ctx) == 0 and not is_plane(ctx):
        v -= 0.05
    s = clamp((getattr(c, 'yb', 0.0) + ly) / max(1.0, getattr(c, 'limb', 1.0)))   # 0 joint -> 1 next joint
    if t == 'collar':
        # where the arm burst out of the dog: a torn fur collar around raw meat
        if f in ('top', 'bottom'):
            return pick(RAW, 0.5 + hash3(ctx.i, ctx.j, 2, 3) * 0.25) if edge(ctx) > 0 else pick(FUR, 0.3)
        if ly < 1.5 or hash3(ctx.i, 1, cseed(ctx), 2) > 0.6 and ly < 2.5:
            return pick(FUR, 0.42 + face_light(ctx) + hash3(ctx.i, ctx.j, 1, 2) * 0.15)
        return pick(RAW, 0.5 + hash3(ctx.i, ctx.j, 2, 3) * 0.2)
    if t in ('knob', 'wknob'):
        cc = mix(pick(HUMAN, v + 0.08), BONE[2], 0.45)
        if edge(ctx) == 0:
            cc = mix(cc, HUMAN[1], 0.45)                          # dark crease round the knob
        elif (ctx.i + ctx.j) % 3 == 0:
            cc = mix(cc, BONE[3], 0.4)
        return cc
    if t in ('upper', 'bicep', 'fore', 'ulna', 'jseg'):
        lower = t in ('fore', 'ulna', 'jseg')
        if lower:
            v -= s * 0.14
        cc = pick(HUMAN, v)
        if t == 'ulna':
            cc = mix(cc, BONE[2], 0.3 if f != 'bottom' else 0.0)    # tendon / ulna ridge catching the light
        if not lower and s < 0.3:
            cc = mix(cc, RAW[3], (0.3 - s) * 1.6)                   # raw, inflamed where it burst out
        if lower:
            cc = mix(cc, DIRT, s * 0.45)                          # filthy toward the wrist
        # connected veins winding down the limb
        if f in ('west', 'east', 'front', 'back') and t != 'ulna':
            across = ctx.i
            if vein_on(across, ly + getattr(c, 'yb', 0.0), cseed(ctx) + (3 if f in ('front', 'back') else 0),
                       0.8, 0.35):
                cc = mix(cc, VEIN[1], 0.55)
        return cc
    if t in ('palm', 'knuckles'):
        if f == 'bottom':
            return mix(pick(HUMAN, 0.28), DIRT, 0.55)
        cc = mix(pick(HUMAN, v - 0.06), DIRT, 0.3)
        if t == 'knuckles' and f in ('front', 'bottom', 'top'):
            if ctx.i % 2 == 1:
                cc = mix(cc, HUMAN[1], 0.5)                     # creases between the curled fingers
            elif f == 'front':
                cc = mix(cc, BONE[2], 0.25)                     # knuckle bones
        if t == 'palm' and f == 'top' and ctx.j >= ctx.h - 2:
            cc = mix(cc, HUMAN[2], 0.35)                        # knuckle row
        return cc
    if t in ('finger', 'thumb'):
        if f == 'bottom' and getattr(c, 'tip', 'front') == 'front':
            return mix(pick(HUMAN, 0.3), DIRT, 0.55)
        tipd = getattr(c, 'tip', 'front')
        is_tip = (lz < 1.0) if tipd == 'front' else (ly > h - 1.0) if tipd == 'bottom' else (
            (lx < 1.0) if tipd == 'west' else (lx > w - 1.0))
        if is_tip:
            return pick(NAIL, 0.6 + face_light(ctx)) if f in ('top', 'front') else NAIL[0]   # cracked black nail
        cc = mix(pick(HUMAN, v - 0.04), DIRT, 0.3)
        alongv = lz if tipd == 'front' else ly if tipd == 'bottom' else lx
        if math.floor(alongv) % 3 == 1:
            cc = mix(cc, HUMAN[1], 0.4)                         # one knuckle crease too many
        return cc
    return pick(HUMAN, v)


# ------------------------------------------------------------------ sweater (the Nona's red cable knit)
C_ROWS = [
    ".WWW.",
    "WW..W",
    "WW...",
    "WW...",
    "WW..W",
    ".WWW.",
]


def knit_px(i, j, v):
    v += ((0.07, -0.03), (-0.05, 0.05))[j % 2][i % 2]       # V stitches
    cab = i % 7
    if cab in (2, 3, 4):                                       # cable braid every 7 columns
        ph = (j + (cab - 2) * 2) % 6
        v += 0.1 if ph < 2 else (-0.1 if ph == 5 else 0.0)
    elif cab in (1, 5):
        v -= 0.1                                               # purl channels each side of the cable
    return v


def sweater_mat(ctx):
    """Remnant of the sweater around the chest: torn back edge and rips (the fur shows through)."""
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    if f == 'bottom':
        return pick(KNIT, 0.3) if lz < 3 else None             # only a strap under the chest
    if f == 'back':
        return None
    v = 0.55 + face_light(ctx) * 1.0
    if f in ('top', 'west', 'east'):
        across = lx if f == 'top' else ly
        rag = 3.0 + hash3(math.floor(across / 1.5), 4, 0, 77) * 4.5
        if d - lz < rag:
            return None                                         # ragged torn back edge
        if d - lz < rag + 1:
            return pick(KNIT, v - 0.25)                         # frayed, stretched last row
        if f == 'top' and (abs(lx - 4) < 1.2 and 3 < lz < 6):
            return None                                         # a rip on the back
        if f in ('west', 'east'):
            ci = int(lz) - 2 if f == 'east' else int(d - lz) - 3
            cj = int(ly) - 4
            if 0 <= cj < len(C_ROWS) and 0 <= ci < 5:
                ch = C_ROWS[cj][ci if f == 'east' else 4 - ci]
                if ch == 'W':
                    return pick(KNIT_W, 0.6 + face_light(ctx) + (0.1 if cj % 2 else 0))
            if f == 'west' and 2 < ly < 5 and 7.5 < lz < 9.5:
                return None                                     # a rip on the right flank
        if f == 'top':
            v = knit_px(ctx.i, ctx.j, v)
        else:
            v = knit_px(int(lz), ctx.j, v)
        if edge(ctx) == 0 and f != 'top':
            v -= 0.05
        return pick(KNIT, v)
    if f == 'front':
        # turtleneck opening around the neck: a ribbed rim, the neck passes through the middle
        cx, cy = lx - w / 2, ly - h * 0.38
        r = max(abs(cx) / 5.0, abs(cy) / 4.6)
        if r < 1.0:
            return None
        if r < 1.35:
            return pick(KNIT, 0.62 + (0.1 if ctx.i % 2 == 0 else -0.08))   # rib knit collar
        return pick(KNIT, knit_px(ctx.i, ctx.j, v))
    return pick(KNIT, v)


def shred_mat(ctx):
    """Strips of the sweater hanging from the spine: knit, frayed bottoms, a loose yarn end."""
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    if is_plane(ctx):
        if f not in ('west', 'front'):
            return None
        u = ctx.i
        if u == ctx.w - 1 and ctx.j >= h - 5 and getattr(ctx.cube, 'yarn', False):
            return pick(KNIT, 0.55 + (0.12 if ctx.j % 2 else -0.05))          # a loose yarn end
        fray = h - 1 - math.floor(hash3(u, cseed(ctx), 0, 31) * 3.2)
        if getattr(ctx.cube, 'yarn', False) and u == ctx.w - 1:
            fray = h - 6
        if ctx.j > fray:
            return None
        if ctx.j == fray:
            return pick(KNIT, 0.32) if u % 2 == 0 else None
        v = knit_px(ctx.i, ctx.j, 0.52 - ctx.j * 0.02)
        return pick(KNIT, v)
    if f == 'bottom':
        return pick(KNIT, 0.3)
    v = 0.55 + face_light(ctx) * 1.0
    return pick(KNIT, knit_px(ctx.i, ctx.j, v))


# ------------------------------------------------------------------ collar + tag
def collar_mat(ctx):
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    if tag(ctx) == 'tag':
        if f != 'front':
            return None
        if (ctx.i, ctx.j) in ((0, 0), (ctx.w - 1, 0)):
            return None
        return pick(BRASS, 0.75 if (ctx.i + ctx.j) % 3 == 0 else 0.5)
    if f in ('front', 'back'):
        return None
    v = 0.55 + face_light(ctx) * 1.0
    if edge(ctx) == 0:
        v -= 0.12
    if f == 'bottom' and abs(lx - w / 2) < 1.5:
        return pick(BRASS, 0.6)                     # the ring the tag hangs from
    return pick(CELESTE, v)


def neck_mat(ctx):
    """The stretched neck: the same see-through skin, trachea rings show as ridges."""
    if tag(ctx) == 'ring':
        return rib_mat(ctx)
    return skin_mat(ctx)


# ------------------------------------------------------------------ head
# eye: 7 x 7, the cute almond shape (cut corners, black upper lid, 2x2 glint top-left, bright lower iris),
# but the iris is milk white.  The pupil is added per side (both turned slightly inward: derp).
EYE_ART = [
    ".KKKKK.",
    "KHHaaaK",
    "KHabbbK",
    "KabbbbK",
    "KbbbbbK",
    "KbcccbK",
    ".KcccK.",
]
EYE_COLS = {'K': LIP[0], 'H': MILK[6], 'a': MILK[2], 'b': MILK[4], 'c': MILK[5]}


def eye_px(i, j, side):
    ch = EYE_ART[j][i]
    if ch == '.':
        return None
    pi = 3 if side == 'r' else 2                     # pupil columns pi, pi+1 (turned inward)
    if j in (3, 4) and i in (pi, pi + 1):
        hot = (i == (pi if side == 'r' else pi + 1)) and j == 3
        return PUPIL if hot else PUPIL_D
    c = EYE_COLS[ch]
    if ch in 'abc' and abs(i - (pi + 0.5)) <= 1.6 and 2 <= j <= 5:
        c = mix(c, BLOODSHOT, 0.28)                 # faint pink ring round the pinpoint
    # bloodshot threads creeping in from the outer corner
    if side == 'r' and (i, j) in ((1, 4), (1, 3), (2, 5)):
        c = mix(c, BLOODSHOT, 0.5)
    if side == 'l' and (i, j) in ((5, 4), (5, 3), (4, 5)):
        c = mix(c, BLOODSHOT, 0.5)
    return c


def eye_mat(ctx):
    side = getattr(ctx.cube, 'side', 'r')
    if ctx.face == 'front':
        return eye_px(ctx.i, ctx.j, side)
    if ctx.face in ('west', 'east') and ctx.j in (5, 6):
        return pick(FUR, 0.4)
    return LIP[0]


def eye_glow(side):
    pts = []
    for j in range(7):
        for i in range(7):
            c = eye_px(i, j, side)
            if c is None or c == LIP[0]:
                continue
            if c == PUPIL:
                pts.append((i, j, hx('#ff4a2a')))
            elif c == PUPIL_D:
                pts.append((i, j, hx('#d01818')))
            else:
                pts.append((i, j, (int(c[0] * 0.82), int(c[1] * 0.86), int(c[2] * 0.9), 255)))
    return at(pts)


EYE_X = (-8, 1)              # left edge of the right / left eye, head-local
EYE_Y = -14                  # top edge of the eyes, head-local


def skull_mat(ctx):
    """Head fur.  Front: forehead with a lighter blaze, fur round the almond eyes, tan under the eyes."""
    f = ctx.face
    t = tag(ctx)
    lx, ly, lz = local(ctx)
    o = ctx.cube.a0
    hp = ctx.cube.hp                                  # head pivot (authored)
    x, y, z = o[0] + lx - hp[0], o[1] + ly - hp[1], o[2] + lz - hp[2]
    v = 0.56 + face_light(ctx) * 1.05
    if t == 'skull':
        if f == 'front':
            tx, ty = math.floor(x), math.floor(y)
            for ex0 in EYE_X:
                ii, jj = tx - ex0, ty - EYE_Y
                if 0 <= ii < 7 and 0 <= jj < 7:
                    return pick(FUR, 0.4)               # behind the eye's cut corners: lid fur
                if -1 <= ii <= 7 and jj == 7:
                    return pick(FUR, 0.3)               # soft shadow under the eye
            if ty >= EYE_Y + 7:
                return mix(pick(FUR, v), pick(TAN, v), 0.55)   # tan cheeks between eyes and muzzle
            v += 0.05 - abs(x) / 9 * 0.12
            if abs(x) < 1.5 and ty < EYE_Y + 3:
                v += 0.06                                # a lighter blaze on the forehead
            v += (hash3(math.floor(x / 2), math.floor(y / 2), 1, 61) - 0.5) * 0.1
            return pick(FUR, v)
        if f == 'bottom' and abs(x) < 4 and z < -6:
            # palate: ridged flesh, seen when the jaws open
            return pick(GUM, 0.45 + (0.18 if int(z) % 2 == 0 else -0.05) - abs(x) * 0.04)
        if f == 'top':
            if abs(x) < 2.6:
                return pick(FUR, v - 0.18 + strands(x, z, 51) * 0.4)
            v += strands(x, z, 51)
        elif f in ('west', 'east'):
            v += strands(y, z, 53)
        else:
            v += strands(x, y, 55)
        if edge(ctx) == 0:
            v -= 0.05
        return pick(FUR, v)
    if t == 'side':
        inner = (f == 'east' and x < 0) or (f == 'west' and x > 0)
        if inner:
            return pick(GUM, 0.55 - (z + 14) * 0.04 + (0.1 if int(y) % 2 == 0 else 0))
        if f == 'bottom':
            return mix(pick(FUR, v - 0.05), pick(TAN, v), 0.4)
        if f == 'front':
            # tan jowls beside the muzzle with whisker dots (the cute cheeks)
            c = pick(TAN, v + 0.02 + (hash3(ctx.i, ctx.j, 3, 3) - 0.5) * 0.08)
            if (ctx.i + ctx.j * 2) % 4 == 0 and 1 <= ctx.j <= 4:
                c = pick(TAN, 0.25)
            return c
        v += strands(y, z, 57)
        c = pick(FUR, v)
        if f in ('west', 'east'):
            c = mix(c, pick(TAN, v), clamp(-(z + 6) / 8.0) * 0.7)     # tan toward the front
        return c
    if t == 'dome':
        if abs(x) < 2.6 and f == 'top':
            return pick(FUR, v - 0.18)
        v += strands(x, z, 59)
        return pick(FUR, v)
    if t == 'gullet':
        if f == 'front' or f == 'top':
            return pick(GUM, 0.3 + (0.1 if ctx.j % 2 == 0 else 0))
        return mix(pick(FUR, v), pick(TAN, v), 0.5)
    return pick(FUR, v)


def brow_mat(ctx):
    v = 0.62 + face_light(ctx) * 0.9
    if edge(ctx) == 0 and ctx.face in ('front', 'top'):
        v -= 0.06
    return pick(TAN, v)


def throat_mat(ctx):
    """The back of the mouth: ribbed red flesh closing to a black throat."""
    f = ctx.face
    if f != 'front':
        return pick(GUM, 0.35) if f == 'top' else THROAT[1]
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    r = max(abs(lx - w / 2) / (w / 2), abs(ly - h * 0.55) / (h * 0.55))
    if r < 0.45:
        return THROAT[0]
    if r < 0.7:
        return THROAT[2 if (ctx.i + ctx.j) % 2 else 1]
    return pick(GUM, 0.2 + (r - 0.7) * 0.9 + (0.12 if ctx.j % 2 == 0 else 0))


def flap_mat(ctx):
    """The four muzzle flaps.  Outside: the cute TAN muzzle (so you see it tear), black lips, whisker dots.
    Inside: gums and raw cut faces."""
    f = ctx.face
    c = ctx.cube
    lx, ly, lz = local(ctx)
    w, h, d = c.size
    up = c.upper
    sx = c.sx                                         # -1 right flap (on -X), +1 left flap
    outer_face = 'west' if sx < 0 else 'east'
    seam_face = 'east' if sx < 0 else 'west'
    v = 0.55 + face_light(ctx) * 1.0
    deep = lz / max(1.0, d) * 0.28                   # darker toward the throat
    if f == seam_face:
        gum_edge = (ly > h - 1.0) if up else (ly < 1.0)
        if gum_edge:
            if int(lz) % 2 == 0 and lz < d - 3:
                return pick(TEETH, 0.6)
            return pick(GUM, 0.62 - deep)
        vv = 0.52 + hash3(ctx.i, ctx.j, 9, 9) * 0.12 - deep
        if int(ly) % 2 == 0:
            vv -= 0.14                               # muscle striations of the cut
        return pick(RAW, vv)
    inner_face = 'bottom' if up else 'top'
    if f == inner_face:
        seam_col = (lx > w - 1.0) if sx < 0 else (lx < 1.0)
        out_col = (lx < 1.0) if sx < 0 else (lx > w - 1.0)
        if out_col:
            return pick(GUM, (0.72 if int(lz) % 2 else 0.5) - deep)
        if seam_col:
            return pick(RAW, 0.55 - deep)
        return pick(GUM, 0.42 + (0.16 if int(lz) % 2 == 0 else 0) + (0.08 if up else -0.05) - deep)
    if f == 'back':
        return pick(RAW, 0.35)
    # outside: tan muzzle (the cute form's), black lip line on the mouth edge
    lip = (ly > h - 1.0) if up else (ly < 1.0)
    if f in (outer_face, 'front') and lip:
        return LIP[1] if (ctx.i % 3) else LIP[2]
    if f == 'front':
        if (sx < 0 and lx > w - 1.0) or (sx > 0 and lx < 1.0):
            return pick(RAW, 0.55)                   # the torn seam seen from the front
        return pick(TAN, v + 0.06 - (0.06 if not up else 0))
    if f == 'top':
        if (sx < 0 and lx > w - 1.0) or (sx > 0 and lx < 1.0):
            return pick(RAW, 0.62)                   # the split line seen from above
        cc = mix(pick(FUR, v + strands(lx, lz, 63)), pick(TAN, v), clamp(0.85 - lz / d))
        return cc
    if f in ('west', 'east'):
        cc = pick(TAN, v + strands(ly, lz, 65) * 0.6 - (0.06 if not up else 0))
        if lz > d - 5:
            cc = mix(cc, pick(FUR, v), (lz - (d - 5)) / 5 * 0.6)    # coat creeping in toward the cheeks
        if up and 1 <= ly <= 3 and 2 <= lz <= 9 and (int(lz) + int(ly)) % 3 == 0:
            return pick(TAN, 0.15)                   # whisker dots
        return cc
    if f == 'bottom':
        return pick(TAN, v - 0.04)
    return pick(TAN, v)


NOSE_ART = [               # right half; column 2 is the cut seam side.  '.' = transparent (rounded corner)
    ".sS",
    "dNk",
    ".kN",
]


def nose_mat(ctx):
    """Half of the big round black nose, cut down the middle: rounded outer corners, a nostril comma,
    a wet glint on top, a raw red cut face on the seam side."""
    f = ctx.face
    c = ctx.cube
    sx = c.sx
    seam_face = 'east' if sx < 0 else 'west'
    w, h, d = c.size
    if f == seam_face:
        return pick(RAW, 0.4 + ctx.j * 0.12)
    if f == 'front':
        i = ctx.i if sx < 0 else w - 1 - ctx.i
        ch = NOSE_ART[ctx.j][i]
        return {'.': None, 's': NOSE[5], 'S': NOSE[7], 'd': NOSE[2], 'N': NOSE[0], 'k': NOSE[1]}[ch]
    if f == 'top':
        i = ctx.i if sx < 0 else w - 1 - ctx.i
        if i == 0 and ctx.j == 0:
            return None
        if i == 2:
            return RAW[3]
        return NOSE[7] if (i == 1 and ctx.j == 1) else NOSE[4]
    if f == 'bottom':
        return NOSE[0]
    return NOSE[2]


def teeth_mat(ctx):
    """Needle teeth on zero-thickness planes: uneven, crooked, some missing, darker roots, bright points,
    longer canines at the front corner.  cube.down: hanging from the top row (upper jaw)."""
    c = ctx.cube
    f = ctx.face
    if f not in ('west', 'front'):
        return None
    i, j = ctx.i, ctx.j
    h, w = ctx.h, ctx.w
    down = c.down
    k = j if down else h - 1 - j                     # distance from the root row
    sd = cseed(ctx)
    if k == 0:
        return pick(GUM, 0.5 + (0.15 if i % 3 == 0 else 0))
    step = getattr(c, 'step', 2)
    off = getattr(c, 'off', 0)
    n = (i + off) // step
    col = (i + off) % step
    crooked = hash3(n, sd, 5, 23) > 0.75             # bent tooth: the point shifts one column
    want = 0 if not crooked else (1 if k >= 2 else 0)
    if col != want:
        return None
    if hash3(n, sd, 9, 29) > 0.86:
        return None                                  # a missing tooth
    ln = 1 + int(hash3(n, sd, 0, 21) ** 0.7 * (h - 1))
    front_i = i if f == 'front' else (w - 1 - i if getattr(c, 'front_hi', False) else i)
    if getattr(c, 'canine', False) and (n == 0 or i >= w - 2):
        ln = h - 1
    elif getattr(c, 'fang_at', None) is not None and abs(front_i - c.fang_at) <= 1:
        ln = h - 1
    if k > ln:
        return None
    if k == ln:
        return TEETH[5]                              # bright point
    if k == ln - 1:
        return TEETH[4]
    return TEETH[1] if k == 1 else TEETH[2]          # stained root


def tongue_mat(ctx):
    """Long black tongue: a centre groove and an oily purple sheen."""
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    v = 0.4 + face_light(ctx) * 0.8
    if f == 'top':
        if abs(lx - w / 2) < 0.6:
            return TONGUE[0]                         # groove
        if ctx.i == 0 or ctx.i == ctx.w - 1:
            v -= 0.1
        if (ctx.j + ctx.i) % 5 == 0:
            v += 0.3                                 # wet glints
    if f == 'bottom':
        v -= 0.12
    return pick(TONGUE, v)


def drool_mat(ctx):
    if ctx.face not in ('front', 'west'):
        return None
    if ctx.j == ctx.h - 1:
        return TONGUE[5]
    return TONGUE[2] if ctx.j % 3 else TONGUE[4]


WHISKER = [
    "k.....",
    ".kk...",
    "...kk.",
    "kk...k",
    "..kkk.",
]


def whisker_mat(ctx):
    """Three wiry dog whiskers fanning out of the muzzle (a front-facing zero-thickness plane)."""
    if ctx.face != 'front':
        return None
    sx = ctx.cube.sx
    i = ctx.i if sx > 0 else ctx.w - 1 - ctx.i
    if WHISKER[ctx.j][i] != 'k':
        return None
    return LIP[2] if i < 3 else pick(FUR, 0.18)


def ear_mat(ctx):
    """Long limp ear: wavy fur outside with a darker rim, bare pink-grey inside, a ragged lower end."""
    f = ctx.face
    c = ctx.cube
    x, y, z = A(ctx)
    lx, ly, lz = local(ctx)
    w, h, d = c.size
    sx = c.sx
    tip = c.name == 'ear_tip'
    if tip:
        dy = ly - (h - 4.5)
        if dy > 0:
            half = d / 2 * math.sqrt(max(0.0, 1 - (dy / 4.5) ** 2))
            if abs(lz - d / 2) > half + 0.35 - hash3(math.floor(lz), 5, cseed(ctx), 3) * 0.6:
                return None
        if f == 'bottom':
            return None
    inner = (f == 'east' and sx < 0) or (f == 'west' and sx > 0)
    v = 0.5 + face_light(ctx) * 1.0
    if inner:
        if lz < 1.0 or lz > d - 1.0:
            return pick(FUR, v - 0.12)
        cc = pick(SKIN, 0.55 - ly / max(1, h) * 0.15)
        if vein_on(lz, ly, cseed(ctx), 0.9, 0.4):
            cc = mix(cc, VEIN[1], 0.4)
        return cc
    if f in ('front', 'back'):
        return pick(FUR, v - 0.18)
    v += strands(lz, y, 71 + (1 if tip else 0), 2.0, 4.0)
    if int((y + lz * 0.6) / 3) % 2 == 0:
        v -= 0.05                                    # soft waves running down the leather
    if lz < 1.0 or lz > d - 1.0:
        v -= 0.12                                    # darker rim
    return pick(FUR, v)


# ------------------------------------------------------------------ kinematics helpers
def euler_zyx(R):
    """MC Euler angles (degrees) for R = Rz * Ry * Rx (mcmodel.rot_matrix order)."""
    ry = math.asin(max(-1.0, min(1.0, -R[2, 0])))
    rx = math.atan2(R[2, 1], R[2, 2])
    rz = math.atan2(R[1, 0], R[0, 0])
    return math.degrees(rx), math.degrees(ry), math.degrees(rz)


def dir_rot(d):
    """Rotation (Rz * Rx) taking the hanging direction (0, 1, 0) onto vector d."""
    d = np.asarray(d, float)
    d = d / np.linalg.norm(d)
    ax = math.asin(max(-1.0, min(1.0, d[2])))
    az = math.atan2(-d[0], d[1])
    return rot_matrix(ax, 0.0, az)


def R_deg(rx, ry, rz):
    return rot_matrix(math.radians(rx), math.radians(ry), math.radians(rz))


def wrapdeg(a):
    while a > 180:
        a -= 360
    while a <= -180:
        a += 360
    return a


def two_bone(S, W, L1, L2, pole):
    """Elbow position for a two-bone chain S -> E -> W with the elbow bent toward `pole`."""
    S = np.asarray(S, float)
    W = np.asarray(W, float)
    d = W - S
    n = float(np.linalg.norm(d))
    n = max(abs(L1 - L2) + 0.3, min(L1 + L2 - 0.3, n))
    u = d / np.linalg.norm(d)
    a = (L1 * L1 - L2 * L2 + n * n) / (2 * n)
    h = math.sqrt(max(0.0, L1 * L1 - a * a))
    pv = np.asarray(pole, float)
    pv = pv - u * float(pv @ u)
    pv = pv / max(1e-6, float(np.linalg.norm(pv)))
    return S + u * a + pv * h


# ------------------------------------------------------------------ layout
C0 = 4.0                     # chain axis height of the chest (authored)
Z1F = -34.0                  # front of the chest = seg1 pivot
SEG1_L = 15
# body links: (bone, parent, skin band length, fur length, width, height, inflate, rest pitch deg (+ = rear up),
#              blood drips)
LINKS = [
    ('seg2', 'seg1', 5, 7, 13, 12, 0.15, 13, False),
    ('seg3', 'seg2', 7, 6, 12, 12, 0.30, 10, True),
    ('seg4', 'seg3', 6, 6, 11, 11, 0.20, -13, False),
    ('seg5', 'seg4', 8, 6, 11, 11, 0.40, -24, True),
    ('seg6', 'seg5', 7, 7, 12, 11, 0.10, 6, False),
    ('hips', 'seg6', 5, 10, 13, 12, 0.25, 16, True),
]
LINK = {L[0]: L for L in LINKS}
SPIKES = []                  # (bone, x, y, z) authored base of each rib spike (filled by build, used by skin_mat)

# the six human arms.  elbow = (|x| out from the midline, world y, dz from the shoulder); wrist = (|x| out, dz);
# joint (extra elbow) likewise.  hand variants: flat, fist (on its knuckles), claw (on its fingertips),
# twist (wrist broken backwards, fingers pointing back).  fingers: lengths inner -> outer.
ARMS = {
    (1, 'right'): dict(seg='seg3', elbow=(13.0, -14.0, -5.0), wrist=(21.0, -16.0), hand='flat', yaw=34,
                       fingers=(6, 9, 8, 7)),
    (1, 'left'): dict(seg='seg3', elbow=(12.0, -8.0, -2.0), wrist=(17.0, -10.0), hand='fist', yaw=14),
    (2, 'right'): dict(seg='seg5', elbow=(17.0, -9.0, 1.0), wrist=(23.0, -1.0), hand='claw', yaw=8,
                       fingers=(4, 6, 6, 5)),
    (2, 'left'): dict(seg='seg5', elbow=(11.0, -13.0, -3.0), joint=(20.0, 1.0, 4.0), wrist=(18.0, 1.0),
                      hand='twist', yaw=158, fingers=(7, 8, 9, 6)),
    (3, 'right'): dict(seg='hips', elbow=(14.0, -6.0, 5.0), wrist=(20.0, 12.0), hand='flat', yaw=-30,
                       fingers=(8, 7, 9, 5)),
    (3, 'left'): dict(seg='hips', elbow=(16.0, -10.0, 8.0), wrist=(21.0, 16.0), hand='claw', yaw=-20,
                      fingers=(5, 6, 5, 4)),
}
HAND_DROP = {'flat': 2.0, 'twist': 2.0, 'fist': 4.0}      # wrist pivot height above the floor; claw: 1 + finger
ARM_GEOM = {}                # filled by build(): lengths + forearm frame per arm (used by the pose IK)


def arm_names(idx, side):
    return f'arm_{idx}_{side}', f'forearm_{idx}_{side}', f'joint_{idx}_{side}', f'hand_{idx}_{side}'


def hand_drop(spec):
    if spec['hand'] == 'claw':
        return 1.0 + max(spec['fingers'])
    return HAND_DROP[spec['hand']]


# ------------------------------------------------------------------ builder (world-space placement)
class Build:
    def __init__(self):
        self.r = Rig()

    def M(self, name):
        return Model('tmp', 16, 16, self.r.roots).world_matrix(self.r.bones[name])

    def bone(self, name, parent, Pw, Rw=None, mat=None):
        """Bone with WORLD rest pivot Pw and WORLD rest orientation Rw."""
        Rw = np.eye(3) if Rw is None else np.asarray(Rw, float)
        if parent is None:
            self.r.bone(name, tuple(float(v) for v in Pw), rot=euler_zyx(Rw), mat=mat)
            return
        M = self.M(parent)
        Rp, Tp = M[:3, :3], M[:3, 3]
        loc = Rp.T @ (np.asarray(Pw, float) - Tp)
        pa = self.r.abs_pivot[parent]
        self.r.bone(name, tuple(pa[i] + loc[i] for i in range(3)), parent=parent, rot=euler_zyx(Rp.T @ Rw), mat=mat)

    def lbone(self, name, parent, loc, rot=(0, 0, 0), mat=None):
        """Bone with its pivot in the PARENT's local frame and a local rotation (degrees)."""
        pa = self.r.abs_pivot[parent] if parent else (0.0, 0.0, 0.0)
        self.r.bone(name, tuple(pa[i] + loc[i] for i in range(3)), parent=parent, rot=rot, mat=mat)

    def box(self, bone, lfrm, size, mat=None, inflate=0.0, decals=None, name=None, **attrs):
        """Cube whose min corner is given in the BONE's local frame (relative to its pivot)."""
        p = self.r.abs_pivot[bone]
        frm = tuple(p[i] + lfrm[i] for i in range(3))
        c = self.r.box(bone, frm, size, mat=mat, inflate=inflate, decals=decals)
        c.a0 = frm
        c.name = name
        for k, v in attrs.items():
            setattr(c, k, v)
        return c

    def wpos(self, bone, lp=(0, 0, 0)):
        return (self.M(bone) @ np.array([*lp, 1.0]))[:3]

    def wrot(self, bone):
        return self.M(bone)[:3, :3]


# ------------------------------------------------------------------ module contract
DEFAULT_MAT = link_fur
FOCUS = 'head'
HEAD_TILT = 8.0              # rest dog head tilt (deg, zRot)
CHEST_ROLL = -5.0            # rest: the chest leans onto its right shoulder


def build():
    b = Build()
    box = b.box
    SPIKES.clear()

    # ---------------- seg1: the chest (root) with the sweater remnant
    b.bone('seg1', None, (0.0, C0, Z1F), R_deg(0, 0, CHEST_ROLL), mat=link_fur)
    box('seg1', (-7, -5.5, 0), (14, 11, SEG1_L), name='core', tear=(False, True))
    box('seg1', (-5, -6.5, 0.5), (10, 1, SEG1_L - 1), name='cap', tear=(False, True))
    box('seg1', (-5, 5.5, 1), (10, 1, SEG1_L - 2), name='keel', tear=(False, True))
    box('seg1', (-7, -6.5, 0), (14, 13, 12), mat=sweater_mat, name='sweater', inflate=0.45)

    # ---------------- body links: skin band (rib cage + pinched waist + spine ridge) then a fur link
    parent, pz = 'seg1', float(SEG1_L)
    for k, (name, par, Lb, Lf, W, Hh, infl, pitch, drip) in enumerate(LINKS):
        roll = -CHEST_ROLL if par == 'seg1' else 0.0
        b.lbone(name, par, (0.0, 0.0, pz), rot=(pitch, 0, roll), mat=link_fur)
        ti = 0.04 * k                                       # tiny per-link growth: nested bands never share planes
        box(name, (-4.5, -4.5, -3), (9, 9, max(3, Lb // 2 + 3)), mat=skin_mat, name='tube', inflate=ti)
        box(name, (-3.5, -3.5, Lb // 2 - 1), (7, 7, Lb - Lb // 2 + 3), mat=skin_mat, name='pinch', inflate=ti)
        nrib = 2 if Lb >= 7 else 1
        for q in range(nrib):
            rz = 0.3 + q * 2.0 if nrib == 2 else 0.8
            box(name, (-5.5, -5.5, rz), (11, 5, 1), mat=rib_mat, name='rib', inflate=ti * 0.5)
        box(name, (-1, -6, -1), (2, 3, Lb + 2), mat=spine_mat, name='spine', inflate=ti * 0.5)
        last = name == 'hips'
        z0 = float(Lb)
        box(name, (-W / 2, -Hh / 2 + 1, z0), (W, Hh - 2, Lf), name='core', inflate=infl, tear=(True, not last), drip=drip)
        box(name, (-W / 2 + 2, -Hh / 2, z0 + 0.5), (W - 4, 1, Lf - 1), name='cap', inflate=infl, tear=(True, not last))
        box(name, (-W / 2 + 2, Hh / 2 - 1, z0 + 0.5), (W - 4, 1, Lf - 1), name='keel', inflate=infl, tear=(True, not last))
        if last:
            box(name, (-W / 2 + 2, -Hh / 2 + 2, z0 + Lf), (W - 4, Hh - 4, 1), name='rump', inflate=infl)
        pz = float(Lb + Lf)

    # broken ribs piercing the skin (seg3 band right flank, seg5 band left top)
    for bn, lp in (('seg3', (-4.0, -4.0, 1.0)), ('seg5', (3.0, -4.0, 4.0))):
        box(bn, (lp[0], lp[1] - 6.0, lp[2]), (1, 6, 1), mat=spike_mat, name='spike')
        p = b.r.abs_pivot[bn]
        SPIKES.append((bn, p[0] + lp[0] + 0.5, p[1] - 4.6, p[2] + lp[2] + 0.5))

    # ---------------- the two real dachshund front legs (planted, bowed in, paws turned out)
    for side, sx in (('right', -1), ('left', 1)):
        lb, pb = f'front_{side}_leg', f'front_{side}_paw'
        Sw = b.wpos('seg1', (4.5 * sx, 3.0, 6.0))
        Rl = R_deg(0, 0, 5 * sx)
        b.bone(lb, 'seg1', Sw, Rl, mat=leg_fur)
        Lleg = (21.0 - Sw[1]) / math.cos(math.radians(5))
        box(lb, (-2.5, -1, -2.5), (5, 6, 5), name='shoulder')
        box(lb, (-2, 4, -2), (4, int(math.ceil(Lleg - 3)), 4), name='leg')
        Pw = Sw + Rl @ np.array([0.0, Lleg, 0.0])
        Pw[1] = 21.0
        b.bone(pb, lb, Pw, R_deg(0, -16 * sx, 0), mat=paw_mat)
        box(pb, (-2.5, 0, -4), (5, 3, 6), name='paw')
        box(pb, (-2, 1, -5), (4, 2, 1), name='toes')

    # ---------------- neck: stretched skin with trachea rings, the celeste collar and its brass tag
    b.lbone('neck', 'seg1', (0.0, -2.0, 0.0), rot=(-35, 0, -CHEST_ROLL * 0.6), mat=neck_mat)
    box('neck', (-4.5, -5, -13), (9, 9, 16), name='tube')
    for z in (-7.0, -4.0):
        box('neck', (-5.5, -6, z), (11, 6, 1), name='ring')
    box('neck', (-5.5, -6, -11.5), (11, 11, 2), mat=collar_mat, name='collar')
    box('neck', (-1, 5, -10.5), (2, 3, 0), mat=collar_mat, name='tag')

    # ---------------- head (pivot at the neck joint, under the back of the skull); level, with a dog tilt
    Hp = b.wpos('neck', (0.0, 0.0, -11.0))
    b.bone('head', 'neck', Hp, R_deg(0, 0, HEAD_TILT), mat=skull_mat)
    hp = b.r.abs_pivot['head']
    box('head', (-9, -16, -14), (18, 10, 14), name='skull', hp=hp)
    box('head', (-7, -17, -12), (14, 1, 10), name='dome', hp=hp)
    box('head', (-9, -6, -14), (5, 6, 14), name='side', hp=hp)
    box('head', (4, -6, -14), (5, 6, 14), name='side', hp=hp)
    box('head', (-4, -6, -6), (8, 6, 6), mat=throat_mat, name='throat')
    box('head', (-4, 0.5, -7), (8, 4, 7), name='gullet', hp=hp)
    box('head', (EYE_X[0], EYE_Y, -15), (7, 7, 1), mat=eye_mat, name='eye', side='r',
        decals={'eyes:front': eye_glow('r')})
    box('head', (EYE_X[1], EYE_Y, -15), (7, 7, 1), mat=eye_mat, name='eye', side='l',
        decals={'eyes:front': eye_glow('l')})

    # chunky tan brows, inner ends raised (the cute puppy-eyes look), as bones so they can furrow
    for side, sx in (('right', -1), ('left', 1)):
        bb = f'{side}_brow'
        b.lbone(bb, 'head', (4.5 * sx, -15.6, -14.6), rot=(0, 0, 13 * -sx), mat=brow_mat)
        box(bb, (-2.5, -1, -1), (5, 2, 2), name='brow')

    # the four muzzle flaps
    for side, sx in (('right', -1), ('left', 1)):
        ub, lb = f'jaw_upper_{side}', f'jaw_lower_{side}'
        b.lbone(ub, 'head', (0.5 * sx, -1, -13), rot=(-3, 3 * -sx, 0), mat=flap_mat)
        x0 = -6.0 if sx < 0 else 0.0
        box(ub, (x0, -5, -14), (5, 5, 14), name='flap', upper=True, sx=sx)
        box(ub, (-3.0 if sx < 0 else 0.0, -5.5, -16), (3, 3, 2), mat=nose_mat, name='nose', sx=sx)
        box(ub, (-5.7 if sx < 0 else 4.7, 0, -13), (0, 3, 12), mat=teeth_mat, name='teeth', down=True,
            fang_at=11, step=2, off=0)
        box(ub, (-2.3 if sx < 0 else 1.3, 0, -12.5), (0, 2, 11), mat=teeth_mat, name='teeth', down=True,
            step=2, off=1)
        box(ub, (-5.7 if sx < 0 else 0.7, 0, -13.6), (5, 4, 0), mat=teeth_mat, name='teeth', down=True,
            canine=True, step=2, off=0)
        box(ub, (-12.0 if sx < 0 else 5.0, -4, -8), (6, 5, 0), mat=whisker_mat, name='whisker', sx=sx)

        b.lbone(lb, 'head', (0.5 * sx, 0, -6), rot=(4, 3 * -sx, 0), mat=flap_mat)
        lx0 = -5.0 if sx < 0 else 0.0
        box(lb, (lx0, 0, -20), (4, 4, 20), name='flap', upper=False, sx=sx)
        box(lb, (-4.6 if sx < 0 else 3.6, -3, -19), (0, 3, 11), mat=teeth_mat, name='teeth', down=False,
            step=2, off=1)
        box(lb, (-4.6 if sx < 0 else 0.6, -3, -19.6), (4, 3, 0), mat=teeth_mat, name='teeth', down=False,
            canine=True, step=2, off=1)
        box(lb, (-1.9 if sx < 0 else 0.9, -2, -18), (0, 2, 12), mat=teeth_mat, name='teeth', down=False,
            step=2, off=0)
        if sx < 0:
            box(lb, (-5.1, 4, -12), (0, 5, 1), mat=drool_mat, name='drool')

    # black tongue lolling out of the front
    b.lbone('tongue', 'head', (0, -0.5, -8), mat=tongue_mat)
    box('tongue', (-2.5, -0.5, -20), (5, 1, 20), name='tongue')
    b.lbone('tongue_tip', 'tongue', (0, 0, -20), rot=(52, 6, 0), mat=tongue_mat)
    box('tongue_tip', (-2.5, -0.5, -9), (5, 1, 9), name='tongue')
    box('tongue_tip', (-1.5, -0.5, -12), (3, 1, 3), name='tongue')

    # ears: limp and far too long, hanging nearly to the ground (world-hanging, whatever the head tilt)
    for side, sx in (('right', -1), ('left', 1)):
        eb, tb = f'{side}_ear', f'{side}_ear_tip'
        Pw = b.wpos('head', (10.0 * sx, -13.0, -4.0))
        b.bone(eb, 'head', Pw, EAR_WORLD(sx), mat=ear_mat)
        box(eb, (-1, -1, -2), (2, 17, 5), name='ear', sx=sx)
        box(eb, (-1.5, 9.5, -3.5), (3, 6, 7), name='ear', sx=sx)
        b.lbone(tb, eb, (0, 16, 0), rot=(-7, 0, 6 * sx), mat=ear_mat)
        box(tb, (-1, 0, -4), (2, 21, 8), name='ear_tip', sx=sx)

    # ---------------- tail: big enough to read, carried high and curved up, tan tip -- it still wags
    Lb, Lf = LINK['hips'][2], LINK['hips'][3]
    b.lbone('tail', 'hips', (0, -3.5, Lb + Lf - 1.0), rot=(48, 0, 0), mat=tail_mat)
    box('tail', (-2, -2, 0), (4, 4, 12), name='base')
    b.lbone('tail_tip', 'tail', (0, 0, 11.5), rot=(26, 0, 0), mat=tail_mat)
    box('tail_tip', (-1.5, -1.5, 0), (3, 3, 10), name='tip')

    # ---------------- sweater shreds hanging off the spine (band + two strips, one with a loose yarn end)
    shreds = [('shred_1', 'seg2', 9.0, 11, 7), ('shred_2', 'seg3', 10.0, 8, 13),
              ('shred_3', 'seg4', 9.0, 13, 6), ('shred_4', 'seg5', 11.0, 6, 11)]
    for k, (name, par, zc, lr, ll) in enumerate(shreds):
        W, Hh, infl = LINK[par][4], LINK[par][5], LINK[par][6]
        top = -Hh / 2 - infl
        b.lbone(name, par, (0, top, zc), mat=shred_mat)
        box(name, (-W / 2 - 0.6, -0.6, -1.5), (W + 1, 1, 3), name='band', inflate=0.1)
        box(name, (-W / 2 - 0.7, 0.2, -2.0), (0, lr, 4), name='strip', yarn=(k % 2 == 0))
        box(name, (W / 2 + 0.7, 0.2, -1.5), (0, ll, 3), name='strip', yarn=(k % 2 == 1))

    # ---------------- three pairs of human arms
    ARM_GEOM.clear()
    for (idx, side), spec in ARMS.items():
        sx = -1 if side == 'right' else 1
        seg = spec['seg']
        _, Lb, Lf, W, Hh, infl, *_ = LINK[seg][1:]
        ab, fb, jb, hb = arm_names(idx, side)
        S = b.wpos(seg, (sx * (W / 2 - 1.0), 1.5, Lb + Lf / 2.0))
        eo, ey, edz = spec['elbow']
        E = np.array([sx * eo, ey, S[2] + edz])
        wo, wdz = spec['wrist']
        Wt = np.array([sx * wo, 24.0 - hand_drop(spec), S[2] + wdz])
        Hw = R_deg(0, -spec['yaw'] * sx, 0)
        L1 = int(round(float(np.linalg.norm(E - S))))
        if 'joint' in spec:
            jo, jy, jdz = spec['joint']
            J = np.array([sx * jo, jy, S[2] + jdz])
            E = S + (E - S) / np.linalg.norm(E - S) * L1
            L2 = int(round(float(np.linalg.norm(J - E))))
            L3 = int(round(float(np.linalg.norm(Wt - J))))
            J = two_bone(E, Wt, L2, L3, J - (E + Wt) / 2)
            R1w, R2w, R3w = dir_rot(E - S), dir_rot(J - E), dir_rot(Wt - J)
        else:
            L2 = int(round(float(np.linalg.norm(Wt - E))))
            E = two_bone(S, Wt, L1, L2, E - (S + Wt) / 2)
            R1w, R2w = dir_rot(E - S), dir_rot(Wt - E)
            L3, J, R3w = 0, None, None
        # upper arm
        b.bone(ab, seg, S, R1w, mat=arm_mat)
        box(ab, (-2.5, -1.5, -2.5), (5, 4, 5), name='collar')
        box(ab, (-1.5, 0, -1.5), (3, L1 + 1, 3), name='upper', inflate=0.2, yb=0.0, limb=L1)
        box(ab, (-2, 2, -2.2 if sx < 0 else -1.8), (4, 7, 4), name='bicep', yb=2.0, limb=L1)
        # forearm (elbow knob on the outside of the bend, ulna ridge down the back, knobbly wrist)
        b.bone(fb, ab, E, R2w, mat=arm_mat)
        out = -((S - E) / np.linalg.norm(S - E) + ((J if J is not None else Wt) - E) /
                np.linalg.norm((J if J is not None else Wt) - E))
        ol = R2w.T @ out
        ol[1] = 0.0
        ol = ol / max(1e-6, float(np.linalg.norm(ol)))
        box(fb, (ol[0] * 1.2 - 1.5, -2.5, ol[2] * 1.2 - 1.5), (3, 4, 3), name='knob')
        box(fb, (-1, 0, -1), (2, L2, 2), name='fore', inflate=0.25, yb=0.0, limb=L2 + L3)
        box(fb, (ol[0] * 1.15 - 0.5, 2.5, ol[2] * 1.15 - 0.5), (1, max(3, L2 - 6), 1), name='ulna',
            yb=2.5, limb=L2 + L3)
        last = fb
        if J is not None:
            b.bone(jb, fb, J, R3w, mat=arm_mat)
            box(jb, (-1.5, -1.5, -1.5), (3, 3, 3), name='knob')
            box(jb, (-1, 0, -1), (2, L3, 2), name='jseg', inflate=0.22, yb=float(L2), limb=L2 + L3)
            last = jb
        Ll = L3 if J is not None else L2
        box(last, (-1.5, Ll - 2.5, -1.5), (3, 2, 3), name='wknob')
        # hand
        b.bone(hb, last, Wt, Hw, mat=arm_mat)
        hv = spec['hand']
        inner = -sx                                          # +x for the right hand: thumb on the inner side
        if hv in ('flat', 'twist'):
            box(hb, (-3.5, 0, -5), (7, 2, 6), name='palm')
            fl = spec['fingers']
            for q, fx in enumerate((-3.0, -1.0, 1.0, 3.0)):
                ln = fl[3 - q] if inner > 0 else fl[q]
                box(hb, (fx - 0.5, 1, -5 - ln), (1, 1, ln), name='finger', tip='front')
            box(hb, (3.5 if inner > 0 else -7.5, 1, -3), (4, 1, 1), name='thumb', tip='east' if inner > 0 else 'west')
        elif hv == 'claw':
            box(hb, (-3.5, 0, -5), (7, 2, 6), name='palm')
            fl = spec['fingers']
            for q, fx in enumerate((-2.8, -0.9, 0.9, 2.8)):
                ln = fl[3 - q] if inner > 0 else fl[q]
                box(hb, (fx - 0.5, 1, -5.6 + (q % 2) * 0.3), (1, ln, 1), name='finger', tip='bottom')
            box(hb, (3.6 if inner > 0 else -4.6, 1, -2), (1, 4, 1), name='thumb', tip='bottom')
        else:  # fist: on its knuckles
            box(hb, (-3.5, 0, -4.5), (7, 2, 5), name='palm')
            box(hb, (-3.5, 1, -7), (7, 3, 3), name='knuckles', inflate=0.2)
            box(hb, (3.6 if inner > 0 else -5.6, 1, -4), (2, 2, 3), name='thumb', tip='front')
        ARM_GEOM[(idx, side)] = dict(L1=L1, L2=L2, L3=L3, jointed=J is not None)

    m = Model('choripan_demonio', 256, 256, b.r.roots)
    m.scale = 0.5
    return m


def EAR_WORLD(sx):
    """Rest world orientation of an ear: hanging straight down, the leather turned toward the front."""
    return R_deg(4, -22 * sx, -6 * sx)


# ------------------------------------------------------------------ pose kit (world-space posing)
class Kit:
    def __init__(self):
        self.m = build()
        self.b = {bn.name: bn for bn in self.m.bones()}
        self.rest = {n: (bn.rot, bn.pivot) for n, bn in self.b.items()}
        self.d = {}

    def _apply(self, n):
        bn = self.b[n]
        r0, p0 = self.rest[n]
        d = self.d.get(n, [0.0] * 6)
        bn.rot = tuple(r0[k] + d[k] for k in range(3))
        bn.pivot = tuple(p0[k] + d[3 + k] for k in range(3))

    def set(self, n, rx=0.0, ry=0.0, rz=0.0, dx=0.0, dy=0.0, dz=0.0):
        self.d[n] = [rx, ry, rz, dx, dy, dz]
        self._apply(n)

    def add(self, n, rx=0.0, ry=0.0, rz=0.0, dx=0.0, dy=0.0, dz=0.0):
        d = self.d.get(n, [0.0] * 6)
        self.d[n] = [d[0] + rx, d[1] + ry, d[2] + rz, d[3] + dx, d[4] + dy, d[5] + dz]
        self._apply(n)

    def M(self, n):
        return self.m.world_matrix(self.b[n])

    def R(self, n):
        return self.M(n)[:3, :3]

    def wpos(self, n, lp=(0, 0, 0)):
        return (self.M(n) @ np.array([*lp, 1.0]))[:3]

    def parentR(self, n):
        p = self.b[n].parent
        return self.R(p.name) if p is not None else np.eye(3)

    def set_world_rot(self, n, Rw):
        e = euler_zyx(self.parentR(n).T @ Rw)
        r0 = self.rest[n][0]
        d = self.d.get(n, [0.0] * 6)
        d[:3] = [wrapdeg(e[k] - r0[k]) for k in range(3)]
        self.d[n] = d
        self._apply(n)

    def set_world_pos(self, n, Pw):
        p = self.b[n].parent
        if p is None:
            loc = np.asarray(Pw, float)
        else:
            M = self.M(p.name)
            loc = M[:3, :3].T @ (np.asarray(Pw, float) - M[:3, 3])
        p0 = self.rest[n][1]
        d = self.d.get(n, [0.0] * 6)
        d[3:] = [float(loc[k] - p0[k]) for k in range(3)]
        self.d[n] = d
        self._apply(n)

    def lowest(self, names):
        y = -1e9
        for n in names:
            M = self.M(n)
            for c in self.b[n].cubes:
                g = c.inflate
                for px in (c.origin[0] - g, c.origin[0] + c.size[0] + g):
                    for py in (c.origin[1] - g, c.origin[1] + c.size[1] + g):
                        for pz in (c.origin[2] - g, c.origin[2] + c.size[2] + g):
                            y = max(y, float((M @ np.array([px, py, pz, 1.0]))[1]))
        return y

    def table(self):
        out = {}
        for n, d in self.d.items():
            if any(abs(v) > 1e-6 for v in d):
                out[n] = tuple(math.radians(v) for v in d[:3]) + tuple(float(v) for v in d[3:])
        return out

    # ---- limbs
    def arm(self, idx, side, W, pole, Hw):
        """IK: wrist pivot of arm (idx, side) onto world point W, elbow bent toward `pole`, hand world rot Hw."""
        g = ARM_GEOM[(idx, side)]
        ab, fb, jb, hb = arm_names(idx, side)
        S = self.wpos(ab)
        W = np.asarray(W, float)
        if g['jointed']:
            self.set_world_rot(fb, self.R(fb))              # keep the zig-zag; solve on the effective link
            v = self.R(fb).T @ (self.wpos(hb) - self.wpos(fb))
            L2 = float(np.linalg.norm(v))
            Q = dir_rot(v)
        else:
            L2, Q = float(g['L2']), np.eye(3)
        E = two_bone(S, W, g['L1'], L2, pole)
        self.set_world_rot(ab, dir_rot(E - S))
        self.set_world_rot(fb, dir_rot(W - E) @ Q.T)
        self.set_world_rot(hb, Hw)

    def plant_arm(self, idx, side, xz, pole, yaw_deg, extra=None):
        spec = ARMS[(idx, side)]
        W = np.array([xz[0], 24.0 - hand_drop(spec), xz[1]])
        Hw = R_deg(0, yaw_deg, 0) if extra is None else extra
        self.arm(idx, side, W, pole, Hw)

    def plant_leg(self, side, reach_deg, paw_yaw=None, bow=5.0):
        """Front leg: swing it `reach_deg` (negative = forward) and lengthen nothing -- solve the swing so the
        paw lands flat on the floor, keeping the requested direction as a hint."""
        sx = -1 if side == 'right' else 1
        lb, pb = f'front_{side}_leg', f'front_{side}_paw'
        S = self.wpos(lb)
        lp = self.b[pb].pivot                             # paw pivot in leg-local (rest geometry)
        L = float(np.linalg.norm(lp))
        drop = 21.0 - S[1]
        sgn = -1.0 if reach_deg < 0 else 1.0
        if abs(drop) >= L:
            ang = 0.0
        else:
            ang = math.degrees(math.acos(max(-1.0, min(1.0, drop / L)))) * sgn
        yaw = float(np.degrees(np.arctan2(self.R('seg1')[0, 2], self.R('seg1')[2, 2])))
        self.set_world_rot(lb, R_deg(0, yaw, 0) @ R_deg(ang, 0, 0) @ R_deg(0, 0, bow * sx))
        py = -16 * sx if paw_yaw is None else paw_yaw
        self.set_world_rot(pb, R_deg(0, yaw + py, 0))
        # residual (bow + rounding): nudge the paw pivot so it sits exactly on the floor
        P = self.wpos(pb)
        if abs(P[1] - 21.0) > 0.05:
            self.set_world_pos(pb, (P[0], 21.0, P[2]))

    def hang_ears(self, swing=0.0, clamp_y=23.4, splay=0.0):
        Rh = self.R('head')
        f = Rh @ np.array([0.0, 0.0, -1.0])
        yaw = math.degrees(math.atan2(-f[0], -f[2]))
        for side, sx in (('right', -1), ('left', 1)):
            eb, tb = f'{side}_ear', f'{side}_ear_tip'
            for k in range(40):
                out = splay + k * 3.0
                self.set_world_rot(eb, R_deg(0, yaw, 0) @ R_deg(swing, 0, out * -sx) @ EAR_WORLD(sx))
                if self.lowest([eb, tb]) <= clamp_y:
                    break


def make_poses():
    poses = {}

    # ------------------------------------------------ lunge
    k = Kit()
    k.set('jaw_upper_right', -28, 34, -12)
    k.set('jaw_upper_left', -28, -34, 12)
    k.set('jaw_lower_right', 34, 28, 14)
    k.set('jaw_lower_left', 34, -28, -14)
    k.set('right_brow', 0, 0, -22, 0, 0.6, 0)
    k.set('left_brow', 0, 0, 22, 0, 0.6, 0)
    k.set('neck', 27, 0, 0)
    k.set('head', -14, 0, -HEAD_TILT, 0, 0, -3)
    k.set('tongue', -8)
    k.set('tongue_tip', -34)
    k.set('right_ear_tip', 25)
    k.set('left_ear_tip', 25)
    k.set('seg1', 0, 0, 0, 0, 2.5, 0)
    k.set('seg2', -6)
    k.set('seg3', -2)
    k.set('seg4', 5)
    k.set('seg5', 4)
    k.set('tail', 10, 26, 0)
    k.set('tail_tip', 0, 20, 0)
    k.plant_leg('right', -30)
    k.plant_leg('left', -22)
    reach = {(1, 'right'): (-24, -12, 40), (1, 'left'): (20, -10, -18), (2, 'right'): (-25, 5, 10),
             (2, 'left'): (19, 9, -160), (3, 'right'): (-21, 26, 24), (3, 'left'): (22, 30, -20)}
    for (idx, side), (x, dz, yaw) in reach.items():
        sx = -1 if side == 'right' else 1
        S = k.wpos(arm_names(idx, side)[0])
        k.plant_arm(idx, side, (x, S[2] + dz), (sx * 0.6, -1.0, 0.0), yaw)
    k.hang_ears(50)
    poses['lunge'] = k.table()

    # ------------------------------------------------ coil
    k = Kit()
    yaw = [('seg2', 40), ('seg3', 32), ('seg4', 40), ('seg5', 32), ('seg6', 40), ('hips', 30)]
    for q, (n, a) in enumerate(yaw):
        k.set(n, -4 if q % 2 else 3, a, 0)
    k.set('seg1', 0, 30, 0)
    k.set('neck', -30, -55, 0)
    k.set('head', 55, -20, 8 - HEAD_TILT)
    k.set('jaw_upper_right', -16, 14, 0)
    k.set('jaw_upper_left', -16, -14, 0)
    k.set('jaw_lower_right', 20, 14, 0)
    k.set('jaw_lower_left', 20, -14, 0)
    k.set('right_brow', 0, 0, -16, 0, 0.5, 0)
    k.set('left_brow', 0, 0, 16, 0, 0.5, 0)
    k.set('tail', 0, 40, 0)
    k.set('tail_tip', 0, 30, 0)
    k.set('tongue_tip', -10)
    k.plant_leg('right', -8)
    k.plant_leg('left', 8)
    piv = [k.wpos(n) for n in ('seg1', 'seg2', 'seg3', 'seg4', 'seg5', 'seg6', 'hips')]
    cen = np.mean(np.array(piv), axis=0)
    for (idx, side), spec in ARMS.items():
        ab = arm_names(idx, side)[0]
        S = k.wpos(ab)
        dirc = cen - S
        dirc[1] = 0.0
        dirc = dirc / np.linalg.norm(dirc)
        bang = math.degrees(math.atan2(-dirc[0], -dirc[2]))
        if side == 'left':
            # inner arms reach in and grab the victim at chest height
            Wt = cen - dirc * 9.0
            Wt[1] = -6.0 - idx * 5.0
            k.arm(idx, side, Wt, (0.0, -1.0, 0.0), R_deg(0, bang, 0))
        else:
            # outer arms brace on the floor, pushing away from the ring
            Wt = S - dirc * 13.0
            k.plant_arm(idx, side, (Wt[0], Wt[2]), (0.0, -1.0, 0.0), bang + 180 - 25)
    k.hang_ears(0)
    poses['coil'] = k.table()

    # ------------------------------------------------ vomit
    k = Kit()
    k.set('jaw_upper_right', -30, 26, 10)
    k.set('jaw_upper_left', -30, -26, -10)
    k.set('jaw_lower_right', 34, 26, -8)
    k.set('jaw_lower_left', 34, -26, 8)
    k.set('right_brow', 0, 0, 14, 0, -0.5, 0)
    k.set('left_brow', 0, 0, -14, 0, -0.5, 0)
    k.set('neck', -24, 0, 0)
    k.set('head', -30, 0, -HEAD_TILT)
    k.set('tongue', 6)
    k.set('tongue_tip', 20)
    k.set('seg1', 0, 0, 0, 0, -1.5, 0)
    k.set('seg2', 6)
    k.set('seg3', 6)
    k.set('seg4', -2)
    k.set('seg5', -4)
    k.set('tail', -20, 0, 0)
    k.plant_leg('right', -12)
    k.plant_leg('left', -12)
    brace = {(1, 'right'): (-24, -6, 40), (1, 'left'): (22, -4, -30), (2, 'right'): (-25, 2, 20),
             (2, 'left'): (23, 4, -150), (3, 'right'): (-23, 8, -20), (3, 'left'): (24, 10, 25)}
    for (idx, side), (x, dz, yw) in brace.items():
        sx = -1 if side == 'right' else 1
        S = k.wpos(arm_names(idx, side)[0])
        k.plant_arm(idx, side, (x, S[2] + dz), (sx * 0.4, -1.0, 0.0), yw)
    k.hang_ears(10)
    poses['vomit'] = k.table()

    # ------------------------------------------------ beg (filled below)
    poses['beg'] = make_beg()

    # ------------------------------------------------ stretch
    poses['stretch'] = make_stretch()
    return poses


def make_beg():
    k = Kit()
    return k.table()


def make_stretch():
    k = Kit()
    return k.table()


POSES = make_poses()

ANIM_NOTES = """(rewritten below)"""
