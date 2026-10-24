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
Three pairs of far-too-long, NOT symmetrical human arms grow out of the flanks of seg3, seg5 and the hips: pallid
dead skin lit on top and livid underneath, 5 x 5 upper arms with a lean deltoid, bony elbow points, 4 x 4 forearms
tapering into 3 x 3 wrists with crease rings, bruises only at the joints, grime toward the filthy hands -- one flat,
one on its knuckles, one clawing on its fingertips, one with an extra joint and a wrist broken backwards.  The
dachshund tail (now big enough to read) still sticks up and wags.

Face (the clip close-up and the jumpscare portrait): it must still be Choripan.  The dog's identity markers are
kept -- tan muzzle and jowls, chunky tan brows (inner ends raised: puppy eyes), big almond eyes RECESSED in sockets
under brown lids with a warm wet lower lid, and THE big glossy black nose with its wet highlight -- but the eyes are
dirty, bloodshot and wet with black pinprick pupils in a red rim (only the rims glow) looking slightly inward, and the muzzle is TORN into four
flaps (jaw_upper_right/left, jaw_lower_right/left) that peel back radially, like a flower, from the corners of a
square MAW cut into the face: gum walls darkening to a black throat, two rings of needle teeth inside it.  The nose is
split down a raw red seam, each half rides its upper flap; every flap is lined with uneven needle teeth (2-3 long fangs
per row), red gums and raw cut faces; a long black tongue (tongue + tongue_tip) with a wet stripe and a rounded tip.

Export for Java (ChoripanRenderer draws the body as a chain that follows the head's position history): every body
link is its own TOP-LEVEL bone, link_0 (head + neck) .. link_7 (hips), pivot at the link's front joint; arms, front
legs, shreds and the tail ride on their link.  Toggles (hidden by default): `vomit` (the black column) and `choripan`
(the blessed choripan caught in the air); `mouth_item` is a cubeless locator for the fetched ItemStack.  Poses:
unspool, run, fetch_drop, beg, lunge, catch, vomit, retract, stretch, coil + the gait keys walk_1..walk_4 (the six
arms' tripod walk, looped in trail mode); POSE_ANCHOR says how each pose is placed on the trail.  ANIM_NOTES at the end
of the file is the animation contract (chain table, trail algorithm, anchors, every bone, toggle and pose) and is
generated from the built model, so its numbers never go stale.
"""
import math
import os
import sys

import numpy as np

from mcmodel import Model, fbm, hash3, face_light, pick, rot_matrix
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
HUMAN = pal('#241815', '#3f2b25', '#5e4537', '#7e6049', '#9c7c60', '#b69a7a', '#cbb393', '#dccbad')
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
        r = max(abs(lx - w / 2), abs(ly - h / 2))
        if r < 4.0:
            return mix(pick(SKIN, 0.42), PURPLE, 0.3)               # where the skin tube dives in
        if r < 5.0 + hash3(ctx.i, ctx.j, 3, 9) * 0.9:
            return pick(RAW, 0.42 + hash3(ctx.i, ctx.j, 3, 9) * 0.2)  # thin raw ring
        return pick(FUR, v - 0.2)                                    # fur folding in over the cut
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
# pallid dead human skin: grey-pink, cool shadows, a warm sickly light side
DEAD = pal('#2e1f22', '#4b3236', '#6c4d50', '#8d6a6a', '#a98783', '#c0a29b', '#d4bab1', '#e4cfc5', '#f0e2d8')
BRUISE = (hx('#3e2c48'), hx('#5c4462'), hx('#6e6a40'))      # deep purple, purple, old yellow-green
GRIME = hx('#2b2219')


def arm_light(ctx):
    """Light from above in WORLD space (the rest pose): the top of every limb segment is clearly lit, the underside
    dark, whatever direction the bone points."""
    return -float(ctx.n[1]) * 0.2 - float(ctx.n[0]) * 0.03


def bruise_at(ctx, amount):
    """Soft bruise blotch (purple, an old yellow-green edge) -- only called near the joints."""
    hsh = hash3(math.floor(ctx.i / 2), math.floor(ctx.j / 2), cseed(ctx), 181)
    if hsh > 1.0 - amount:
        return BRUISE[0] if hsh > 1.0 - amount * 0.45 else BRUISE[1]
    if hsh > 1.0 - amount * 1.35:
        return BRUISE[2]
    return None


def arm_mat(ctx):
    """Long human arm, pallid dead skin: lit top / dark underside, a soft roll-off toward the edges of each face,
    crease rings at the elbow and the wrist, bruises only at the joints, raw where it burst out of the dog, grime
    building up toward the hands, cracked black nails."""
    c = ctx.cube
    f = ctx.face
    t = tag(ctx)
    lx, ly, lz = local(ctx)
    w, h, d = c.size
    v = 0.6 + arm_light(ctx)
    long_face = f in ('west', 'east', 'front', 'back')
    if long_face and not is_plane(ctx):
        across = ctx.i / max(1, ctx.w - 1)
        v -= abs(across - 0.45) * 0.1                   # rounded: the middle of each face catches more light
    yb = getattr(c, 'yb', 0.0)
    limb = max(1.0, getattr(c, 'limb', 1.0))
    s = clamp((yb + ly) / limb)                          # 0 at the joint above -> 1 at the joint below
    if t == 'collar':
        # where the arm burst out of the dog: a torn fur collar around raw meat
        if f in ('top', 'bottom'):
            return pick(RAW, 0.5 + hash3(ctx.i, ctx.j, 2, 3) * 0.25) if edge(ctx) > 0 else pick(FUR, 0.3)
        if ly < 1.5 or hash3(ctx.i, 1, cseed(ctx), 2) > 0.6 and ly < 2.5:
            return pick(FUR, 0.42 + face_light(ctx) + hash3(ctx.i, ctx.j, 1, 2) * 0.15)
        return pick(RAW, 0.5 + hash3(ctx.i, ctx.j, 2, 3) * 0.2)
    if t in ('knob', 'wknob'):
        cc = mix(pick(DEAD, v + 0.12), BONE[2], 0.3)      # bone pushing at the skin
        if edge(ctx) == 0:
            cc = mix(cc, DEAD[1], 0.5)                     # the crease round the knob
        else:
            b = bruise_at(ctx, 0.5)
            if b is not None:
                cc = mix(cc, b, 0.55)
        return cc
    if t in ('upper', 'bicep', 'fore', 'wrist', 'jseg'):
        lower = t in ('fore', 'wrist', 'jseg')
        if lower:
            v -= s * 0.1
        x, y, z = A(ctx)
        v += (fbm(x * 0.22, y * 0.22, z * 0.22, 2, 191) - 0.5) * 0.14       # soft mottling (no strands)
        cc = pick(DEAD, v)
        if float(ctx.n[1]) > 0.35 or (f == 'bottom' and float(ctx.n[1]) > -0.2):
            cc = mix(cc, BRUISE[1], 0.22)                    # livor: blood pooled on the underside
        if not lower and s < 0.22:
            cc = mix(cc, RAW[3], (0.22 - s) * 2.2)          # raw, inflamed where it burst out
        if lower:
            cc = mix(cc, GRIME, s * 0.42)                   # filthier toward the hand
        if long_face:
            # crease rings: two folds of skin under the elbow, two at the wrist
            ring = (t == 'fore' and ly in (1.5, 3.5)) or (t in ('wrist', 'jseg') and h - ly in (1.5, 3.5)) \
                or (t == 'upper' and h - ly in (2.5,))
            ring = ring or (t == 'fore' and math.floor(ly) in (1, 3)) or (t in ('wrist', 'jseg') and math.floor(h - ly) in (1, 3))
            if ring:
                cc = mix(cc, DEAD[1], 0.55)
            elif (t == 'fore' and math.floor(ly) in (0, 2)) or (t in ('wrist', 'jseg') and math.floor(h - ly) in (2,)):
                cc = mix(cc, DEAD[7], 0.25)                   # the lit lip of each fold
            # bruises only at the joints
            near = (t == 'fore' and ly < 4.5) or (t == 'upper' and h - ly < 4.0) or (t in ('wrist', 'jseg') and h - ly < 3.0)
            if near:
                b = bruise_at(ctx, 0.32)
                if b is not None:
                    cc = mix(cc, b, 0.5)
        if f == 'bottom':
            cc = mix(cc, DEAD[1], 0.4)
        return cc
    if t in ('palm', 'knuckles'):
        if f == 'bottom':
            return mix(pick(DEAD, 0.3), GRIME, 0.6)
        cc = mix(pick(DEAD, v - 0.06), GRIME, 0.38)
        if t == 'knuckles' and f in ('front', 'bottom', 'top'):
            if ctx.i % 2 == 1:
                cc = mix(cc, DEAD[1], 0.5)                     # creases between the curled fingers
            elif f == 'front':
                cc = mix(cc, BONE[2], 0.25)                    # knuckle bones
        if t == 'palm' and f == 'top' and ctx.j >= ctx.h - 2:
            cc = mix(cc, DEAD[2], 0.35)                        # knuckle row
        return cc
    if t in ('finger', 'thumb'):
        if f == 'bottom' and getattr(c, 'tip', 'front') == 'front':
            return mix(pick(DEAD, 0.3), GRIME, 0.6)
        tipd = getattr(c, 'tip', 'front')
        is_tip = (lz < 1.0) if tipd == 'front' else (ly > h - 1.0) if tipd == 'bottom' else (
            (lx < 1.0) if tipd == 'west' else (lx > w - 1.0))
        if is_tip:
            return pick(NAIL, 0.6 + face_light(ctx)) if f in ('top', 'front') else NAIL[0]   # cracked black nail
        cc = mix(pick(DEAD, v - 0.04), GRIME, 0.42)
        alongv = lz if tipd == 'front' else ly if tipd == 'bottom' else lx
        if math.floor(alongv) % 3 == 1:
            cc = mix(cc, DEAD[1], 0.45)                        # one knuckle crease too many
        return cc
    return pick(DEAD, v)


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
# Head-local layout (pivot = the head joint under the back of the skull; the face plane is z = FACE_Z):
#   skull block behind the face (front at SKULL_Z), the eyes RECESSED in sockets framed by the brow ridge, the blaze,
#   the temples and the cheek band (front at FACE_Z); below them the maw: a square hole HOLE (x0, x1, y0, y1) cut into
#   the face between the tan jowls, 8 texels deep to the throat (black core in a gum ring), two rings of needle teeth
#   inside it; the four muzzle flaps close over it and peel back from its four outer corners.
FACE_Z = -14.0
SKULL_Z = -12.0
EYE_X = (-8, 1)              # left edge of the right / left eye, head-local
EYE_Y = -15                  # top edge of the eyes (7 x 8, front at z = -13: one texel deep in a two-texel socket)
EYE_W, EYE_H = 7, 8
HOLE = (-5.0, 5.0, -6.0, 3.0)
THROAT_Z = -6.0
# eye: 7 x 8, the dog's almond eye (brown upper lid over the top two rows, brown ring, a raw wet lower lid).  B3 pass:
# no more milk-white googly eyes -- a dirty, yellowed, wet eyeball choked with burst veins, a pinprick pupil (ONE black
# texel) inside a thin rim of dark blood-red iris, turned slightly inward; the lower rim raw and red.  Only the
# pinprick's rim and one wet glint glow (emissive), so at night it is two tiny red points, not two headlights.
EYE_ART = [
    "cLLLLLc",
    "LlllllL",
    "lssabsl",
    "rabbbar",
    "abbbbba",
    "rabbbar",
    "rRRRRRr",
    "cwwwwwc",
]
LID = pal('#1e0c06', '#3a1a0c', '#5a2c14', '#7a4220')
WET = pal('#5a2a24', '#8a4a3e', '#b0705c')
SCL = pal('#2e2422', '#5e5046', '#8e806c', '#b0a48c', '#cfc6b0')      # dirty, yellowed sclera (dark -> light)
VEIN_R = (hx('#5e0c0e'), hx('#8a1a18'), hx('#a8342c'))
IRIS_R = (hx('#2a0606'), hx('#4a0c0a'), hx('#6a1612'))
PIN = hx('#030102')
EYE_COLS = {'c': FUR[1], 'L': LID[2], 'l': LID[0], 'r': LID[1], 's': SCL[1], 'a': SCL[2], 'b': SCL[3],
            'R': VEIN_R[0], 'w': WET[1]}
PUPIL_ROW = 4
# burst veins, (i, j) per side, crawling in from both corners toward the pupil ('r' = the right eye, on -X)
VEINS = {'r': {(0, 4): 1, (1, 4): 2, (1, 5): 0, (2, 3): 2, (6, 4): 2},
         'l': {(6, 4): 1, (5, 4): 2, (5, 5): 0, (4, 3): 2, (0, 4): 2}}


def _pin(side):
    return (4, PUPIL_ROW) if side == 'r' else (2, PUPIL_ROW)       # turned slightly inward


def eye_px(i, j, side):
    ch = EYE_ART[j][i]
    pi, pj = _pin(side)
    if (i, j) == (pi, pj):
        return PIN
    if j == pj and abs(i - pi) == 1:
        return IRIS_R[1]                                             # the thin blood-red iris rim
    if i == pi and j == pj - 1:
        return IRIS_R[0]
    c = EYE_COLS[ch]
    if ch in 'sab':
        v = VEINS[side].get((i, j))
        if v is not None:
            return VEIN_R[v]
    if ch == 'L' and i in (2, 3):
        c = LID[3]                                   # a soft sheen on the lid
    if ch == 'w' and i in (1, 5):
        c = WET[0]
    if ch == 'w' and i == 3:
        c = WET[2]                                   # the wet line catches the light
    if ch == 'R' and i in (2, 4):
        c = VEIN_R[1]
    if (i, j) == ((1, 2) if side == 'r' else (5, 2)):
        c = SCL[4]                                   # one wet glint under the lid
    return c


def eye_mat(ctx):
    side = getattr(ctx.cube, 'side', 'r')
    if ctx.face == 'front':
        return eye_px(ctx.i, ctx.j, side)
    return pick(FUR, 0.12)                           # (hidden in the socket)


def eye_glow(side):
    """Emissive: only the pinprick's red rim (dim) and the single wet glint -- two small red points in the dark."""
    pi, pj = _pin(side)
    pts = [(pi - 1, pj, hx('#8a1210')), (pi + 1, pj, hx('#8a1210')), (pi, pj - 1, hx('#5e0a0a'))]
    g = (1, 2) if side == 'r' else (5, 2)
    pts.append((g[0], g[1], hx('#8c8478')))
    return at(pts)


def hloc(ctx):
    """Head-local texel centre (cubes on the head carry the head pivot as cube.hp)."""
    lx, ly, lz = local(ctx)
    o = ctx.cube.a0
    hp = ctx.cube.hp
    return o[0] + lx - hp[0], o[1] + ly - hp[1], o[2] + lz - hp[2]


def in_eye_cols(x):
    return any(ex <= x < ex + EYE_W for ex in EYE_X)


def maw_wall(z, ridge, dark=0.0):
    """Inside of the maw: wet red gum at the rim fading through dark red to black at the throat (z = THROAT_Z)."""
    t = clamp((z - FACE_Z) / (THROAT_Z - FACE_Z))
    if t > 0.72:
        return THROAT[1] if ridge else THROAT[0]
    v = 0.62 - t * 0.75 - dark + (0.1 if ridge else 0.0)
    return pick(GUM, v) if v > 0.12 else THROAT[2]


def face_mat(ctx):
    """The eye sockets' rim (brow ridge, blaze, temples, cheek band): fur round the eyes, a lighter blaze between
    them, tan cheeks under them, dark socket walls inside."""
    f = ctx.face
    t = tag(ctx)
    x, y, z = hloc(ctx)
    v = 0.56 + face_light(ctx) * 1.05
    wall = ((t == 'ridge' and f == 'bottom' and in_eye_cols(x)) or (t == 'cheekband' and f == 'top' and in_eye_cols(x))
            or (t == 'blaze' and f in ('west', 'east')) or (t == 'temple' and ((f == 'east') == (x < 0))))
    if wall:
        return pick(FUR, 0.1 + (0.06 if z < FACE_Z + 0.6 else 0.0))       # inside the socket
    if f == 'front':
        if t == 'cheekband':
            if in_eye_cols(x):
                return mix(pick(FUR, 0.42), pick(TAN, 0.5), 0.45)        # warm fold under the lower lid
            return mix(pick(FUR, v), pick(TAN, v), 0.55)
        if t == 'blaze':
            return mix(pick(FUR, v + 0.08), pick(TAN, v), 0.25 + (0.15 if y > -11 else 0.0))
        if t == 'ridge':
            return pick(FUR, v - (0.1 if in_eye_cols(x) else 0.0))       # shadow of the brow over the lids
        return pick(FUR, v - 0.04)
    if f == 'bottom' and abs(x) < HOLE[1]:
        return pick(GUM, 0.48 + (0.15 if int(z) % 2 == 0 else -0.05))      # front of the palate
    if f == 'top' and abs(x) < 2.6:
        return pick(FUR, v - 0.18)
    v += strands(y if f in ('west', 'east') else x, z, 51)
    return pick(FUR, v)


def skull_mat(ctx):
    """Head fur: back stripe on top, the palate under the skull (seen through the open flower)."""
    f = ctx.face
    t = tag(ctx)
    x, y, z = hloc(ctx)
    lx, ly, lz = local(ctx)
    v = 0.56 + face_light(ctx) * 1.05
    if t == 'skull':
        if f == 'front':
            return pick(FUR, 0.12)                       # (behind the eyes and the socket rim)
        if f == 'bottom' and abs(x) < HOLE[1] and z < THROAT_Z:
            return maw_wall(z, int(z) % 2 == 0)                    # palate: ridged, darkening into the throat
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
            # the maw's side wall: ridged gum, darkening to black toward the throat
            return maw_wall(z, int(y) % 2 == 0)
        if f == 'bottom':
            return mix(pick(FUR, v - 0.05), pick(TAN, v), 0.4)
        if f == 'front':
            if abs(x) < HOLE[1] + 1.0 and y < HOLE[3]:
                return pick(RAW, 0.38 + (0.12 if int(y) % 2 else 0.0))        # torn rim of the maw
            # tan jowls beside the muzzle with whisker dots (the cute cheeks)
            c = pick(TAN, v + 0.02 + (hash3(ctx.i, ctx.j, 3, 3) - 0.5) * 0.08)
            if (ctx.i + ctx.j * 2) % 4 == 0 and 2 <= ctx.j <= 6 and abs(x) > 6:
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
    if t == 'chin':
        if f == 'top':
            return maw_wall(z, int(z) % 2 == 0, 0.08)               # floor of the maw
        if f == 'front':
            if y < HOLE[3] + 1.0:
                return pick(RAW, 0.36 + (0.1 if ctx.i % 2 else 0.0))          # lower rim of the maw
            if y < HOLE[3] + 2.0:
                return pick(GUM, 0.28)
            c = mix(pick(FUR, v + strands(x, y, 61) * 0.5), pick(TAN, v), 0.7)
            return c
        if f == 'bottom':
            return mix(pick(TAN, v + 0.05), pick(SKIN, 0.5), 0.35)          # bald, stretched underneath
        cc = mix(pick(FUR, v + strands(lz, y, 61) * 0.6), pick(TAN, v), 0.45 + clamp(-(z + 4) / 10.0) * 0.3)
        return cc
    return pick(FUR, v)


def brow_mat(ctx):
    v = 0.62 + face_light(ctx) * 0.9
    if edge(ctx) == 0 and ctx.face in ('front', 'top'):
        v -= 0.06
    return pick(TAN, v)


def throat_mat(ctx):
    """The back of the maw, facing the camera when the flower opens: a thin rim of ribbed dark-red flesh round a
    big black throat (the gum-lined walls of the maw do the red)."""
    f = ctx.face
    if f != 'front':
        return pick(GUM, 0.3) if f == 'top' else THROAT[1]
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    r = max(abs(lx - w / 2) / (w / 2), abs(ly - h / 2) / (h / 2))
    if r < 0.62:
        return THROAT[0]
    if r < 0.82:
        return THROAT[2] if (ctx.i * 3 + ctx.j) % 4 else THROAT[3]
    return GUM[1] if (ctx.i + ctx.j) % 2 else THROAT[3]


def ring_mat(ctx):
    """A ring of needle teeth lining the maw (a front-facing plane): a gum band round the edge, uneven needles pointing
    in, the centre open.  cube.deep: the inner ring (in shadow, darker)."""
    if ctx.face != 'front':
        return None
    i, j, w, h = ctx.i, ctx.j, ctx.w, ctx.h
    deep = getattr(ctx.cube, 'deep', False)
    ds = (i, j, w - 1 - i, h - 1 - j)                 # distance to the left, top, right, bottom edge
    e = min(ds)
    if e == 0:
        return GUM[1] if deep else (GUM[2] if (i + j) % 3 else GUM[1])
    side = ds.index(e)
    along = j if side in (0, 2) else i
    sd = 7 if deep else 3
    if hash3(along, side, sd, 131) < (0.62 if deep else 0.42):
        return None
    ln = 1 + int(hash3(along, side, sd, 137) * (2.2 if deep else 3.2))
    if (along in (1, w - 2)) and e <= 2:
        return None                                  # leave the corners open
    if e > ln:
        return None
    if e == ln:
        return TEETH[2] if deep else TEETH[4]
    return mix(TEETH[1 if deep else 3], hx('#a89a5a'), 0.35 if e == 1 else 0.1)   # yellowed roots


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


# THE dog nose, at the dog's proportions (8 x 3 + a 6 x 1 leather bulb across the two upper flaps), cut in half down
# a raw red seam: each half rides its flap when the flower opens.  Full front, viewer's left = the right half:
NOSE_FRONT = [
    ".kmSskk.",
    "kkskkkkk",
    "kNNkkNNk",
]
NOSE_BULB = "kSSmkk"           # the leather bulb on top: the crisp 2-texel wet highlight (light from the upper left)
NOSE_COLS = {'k': NOSE[2], 'm': NOSE[5], 'S': NOSE[7], 's': NOSE[4], 'N': NOSE[0]}


def nose_mat(ctx):
    """Half of the big glossy black nose.  cube.sx: -1 right half (columns 0-3 of NOSE_FRONT), +1 left half."""
    f = ctx.face
    c = ctx.cube
    sx = c.sx
    seam_face = 'east' if sx < 0 else 'west'
    bulb = tag(ctx) == 'bulb'
    if f == seam_face:
        return pick(RAW, 0.35 + ctx.j * 0.12)
    if f == 'front':
        if bulb:
            col = ctx.i if sx < 0 else ctx.i + 3
            return NOSE_COLS[NOSE_BULB[col]]
        col = ctx.i if sx < 0 else ctx.i + 4
        ch = NOSE_FRONT[ctx.j][col]
        if ch == '.':
            return None
        if (sx < 0 and ctx.i == ctx.w - 1) and ctx.j > 0:
            return RAW[1]                                # the split seam down the middle
        return NOSE_COLS[ch]
    if f == 'top':
        col = ctx.i if sx < 0 else ctx.i + (3 if bulb else 4)
        if bulb:
            return NOSE[6] if col in (1, 2) and ctx.j == ctx.h - 1 else NOSE[3]
        if (sx < 0 and ctx.i == ctx.w - 1) or (sx > 0 and ctx.i == 0):
            return RAW[2]
        return NOSE[5] if ctx.j == ctx.h - 1 and col in (1, 2, 5) else NOSE[3]
    if f == 'bottom':
        return NOSE[0]
    return NOSE[3] if ctx.j == 0 else NOSE[1]


def tooth_layout(w, h, sd, fangs=2):
    """Uneven needle teeth along a plane: [(column, length, slant)], gaps of 0-2 columns, lengths 2-4 (capped by the
    plane), `fangs` long ones running the full height (past the flap edge)."""
    out, i = [], int(hash3(sd, 1, 2, 151) * 2)
    while i < w:
        ln = 2 + int(hash3(i, sd, 3, 153) * 2.99)
        sl = (-1, 0, 0, 1)[int(hash3(i, sd, 5, 155) * 3.99)]
        out.append([i, min(ln, h - 1), sl])
        i += 2 + int(hash3(i, sd, 7, 157) ** 2 * 2.5)
    if out and fangs:
        picks = sorted(range(len(out)), key=lambda q: hash3(q, sd, 9, 159))[:fangs]
        for q in picks:
            out[q][1] = h - 1
            out[q][2] = 0
    return out


def teeth_mat(ctx):
    """Needle teeth on zero-thickness planes: irregular spacing, lengths 2-4 with a slight slant, two or three long
    fangs per row, stained yellow roots, bright points, dark gum between the roots.  cube.down: hanging from the top
    row (upper jaw)."""
    c = ctx.cube
    f = ctx.face
    if f not in ('west', 'front'):
        return None
    i, j, w, h = ctx.i, ctx.j, ctx.w, ctx.h
    k = j if c.down else h - 1 - j                   # distance from the root row
    teeth = tooth_layout(w, h, cseed(ctx) + getattr(c, 'salt', 0), getattr(c, 'fangs', 2))
    if k == 0:
        rooted = any(t[0] == i for t in teeth)
        return GUM[3] if rooted else GUM[1]
    for col, ln, sl in teeth:
        cc = col + (sl if k * 2 > ln else 0)
        if i != cc or k > ln:
            continue
        if k == ln:
            return TEETH[5]                          # bright point
        if k == 1:
            return mix(TEETH[2], hx('#9c8a4a'), 0.45)   # yellowed root
        return TEETH[4] if k == ln - 1 else TEETH[3]
    return None


def tongue_mat(ctx):
    """Long black tongue: a wet mid-value stripe down the middle with glints, an oily purple sheen on the edges, a
    rounded tip (cube.tip: the last cube, its two front corners cut)."""
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    v = 0.36 + face_light(ctx) * 0.8
    if getattr(ctx.cube, 'tip', False) and f in ('top', 'bottom') and lz < 1.0 and ctx.i in (0, ctx.w - 1):
        return None                                  # rounded end
    if f == 'top':
        mid = abs(lx - w / 2)
        if mid < 0.6:
            return TONGUE[5] if (ctx.j % 4 == 1) else TONGUE[4]       # the wet stripe down the centre
        if mid < 1.6:
            v += 0.12 + (0.2 if hash3(ctx.i, ctx.j, 3, 171) > 0.8 else 0.0)
        else:
            v -= 0.08                                # dark oily edges
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
        return mix(pick(FUR, v + 0.06), pick(TAN, 0.42), 0.35)          # the thin leather edge catches the light
    v += strands(lz, y, 71 + (1 if tip else 0), 2.0, 4.0)
    if int((y + lz * 0.6) / 3) % 2 == 0:
        v -= 0.05                                    # soft waves running down the leather
    if lz < 1.0 or lz > d - 1.0:
        return mix(pick(FUR, v + 0.1), pick(TAN, 0.45), 0.3)           # lighter leather rim
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


# ------------------------------------------------------------------ the 'CHORIPAN' name tag (gold, engraved)
# 3x5 pixel font (N is 4 wide: a 3-wide N reads as H).  Two lines, "CHORI" / "PAN" with the acute accent over the A.
FONT = {
    'C': [".##", "#..", "#..", "#..", ".##"],
    'H': ["#.#", "#.#", "###", "#.#", "#.#"],
    'O': [".#.", "#.#", "#.#", "#.#", ".#."],
    'R': ["##.", "#.#", "##.", "#.#", "#.#"],
    'I': ["#", "#", "#", "#", "#"],
    'P': ["##.", "#.#", "##.", "#..", "#.."],
    'A': [".#.", "#.#", "###", "#.#", "#.#"],
    'N': ["#..#", "##.#", "#.##", "#..#", "#..#"],
}
TAG_W, TAG_H = 17, 13
# aged brass, one ramp step darker than new: the milk eyes stay the brightest thing on the creature
GOLD = pal('#1c0f05', '#3e2a0c', '#62481a', '#87692c', '#a6863e', '#bfa052', '#d6bc74')
ENGRAVE = hx('#160b04')
TAG_CUT = {(0, 0), (1, 0), (0, 1), (TAG_W - 1, 0), (TAG_W - 2, 0), (0, TAG_H - 1), (1, TAG_H - 1), (0, TAG_H - 2),
           (TAG_W - 1, TAG_H - 1), (TAG_W - 2, TAG_H - 1), (TAG_W - 1, TAG_H - 2)}


def _tag_text():
    rows = [[0] * TAG_W for _ in range(TAG_H)]

    def put(word, x0, y0):
        x = x0
        for ch in word:
            g = FONT[ch]
            for j, r in enumerate(g):
                for i, c in enumerate(r):
                    if c == '#':
                        rows[y0 + j][x + i] = 1
            x += len(g[0]) + 1

    put('CHORI', 0, 1)
    w2 = sum(len(FONT[c][0]) for c in 'PAN') + 2
    x2 = (TAG_W - w2) // 2
    put('PAN', x2, 7)
    rows[6][x2 + len(FONT['P'][0]) + 1 + 2] = 1          # the acute accent: up-right of the A's apex
    return rows


TAG_TXT = _tag_text()


def tag_mat(ctx):
    """The brass name tag (a rounded, notched plate): the name engraved edge to edge in dark cuts on worn brass, a
    lit top bevel, a shaded bottom bevel, a plain scratched back; a ring on top."""
    f = ctx.face
    i, j, w, h = ctx.i, ctx.j, ctx.w, ctx.h
    if tag(ctx) == 'ring':
        if f in ('front', 'back') and 0 < i < w - 1 and 0 < j < h - 1:
            return None
        return GOLD[4] if (i + j) % 2 == 0 else GOLD[2]
    if f in ('front', 'back'):
        if (i, j) in TAG_CUT:
            return None                                          # rounded, notched corners
        if f == 'back':
            if edge(ctx) == 0:
                return GOLD[1]
            v = 0.4 + (0.1 if (i - j) % 7 == 0 else 0) - (0.12 if hash3(i, j, 4, 41) > 0.93 else 0)
            return pick(GOLD, v)
        if TAG_TXT[j][i]:
            return ENGRAVE
        if j == 0 or (i, j - 1) in TAG_CUT:
            return GOLD[5]                                       # lit top bevel
        if j == h - 1 or (i, j + 1) in TAG_CUT:
            return GOLD[1]                                       # shaded bottom bevel
        v = 0.58 - j * 0.012 + (0.1 if (i + j) % 13 == 0 else 0) - (0.08 if hash3(i, j, 2, 43) > 0.9 else 0)
        return pick(GOLD, v)
    if f == 'top':
        return GOLD[4]
    return GOLD[1]


# ------------------------------------------------------------------ the black vomit column (toggle)
TAR = pal('#010002', '#050308', '#0b070f', '#140d19', '#211726', '#342639', '#524160')
SHEEN = hx('#7a6a9e')                       # cool wet specular on the bile (reads under moonlight / a flashlight)
EMBER = (hx('#ff6a1e'), hx('#ffb648'), hx('#d81c10'))
EMBER_GLOW = (hx('#ff7a2a'), hx('#ffc060'), hx('#ff2a18'))
RIM_GLOW = (hx('#7a1a0c'), hx('#8a3410'))   # dim (~50 %) emissive rim of the splash
CORE_GLOW = (hx('#5a0608'), hx('#8a0c0c'))  # the deep red core at the mouth end


def _face_seed(cube_tag, face, size):
    return (sum(map(ord, face)) * 7 + sum(map(ord, cube_tag)) * 3 + int(size[0] * 13 + size[1] * 3 + size[2])) % 997


def _ember(i, j, sd, rate, cw=2, ch=2):
    """Embers come in clusters (cw x ch cells, one or two texels of each cell missing)."""
    ci, cj = i // cw, j // ch
    if hash3(ci, cj, sd, 91) >= rate:
        return None
    if hash3(i, j, sd, 93) < 0.22:
        return None
    k = hash3(i, j, sd, 95)
    return 1 if k > 0.7 else (0 if k > 0.25 else 2)          # index into EMBER / EMBER_GLOW


def vomit_px(t, f, size, i, j, w, h):
    """(base colour, glow colour or None) of one texel of the bile column.  Shared by the material and the emissive
    decal so the glowing texels are exactly the painted embers."""
    sd = _face_seed(t, f, size)
    if t == 'puddle':
        if f != 'top':
            return None, None
        cx, cy = (w - 1) / 2, (h - 1) / 2
        dx, dy = (i - cx) / (w / 2), (j - cy) / (h / 2)
        r = math.hypot(dx, dy)
        ang = math.atan2(dy, dx)
        lim = 0.72 + 0.16 * math.sin(ang * 5 + 1.3) + 0.1 * math.sin(ang * 3 - 0.4)
        if r > lim:
            if hash3(i, j, 7, 93) > 0.9 and r < lim + 0.25:
                return TAR[3], (RIM_GLOW[0] if hash3(i, j, 8, 94) > 0.5 else None)      # flung drops
            return None, None
        if r > lim - 0.12:
            return mix(TAR[5], RIM_GLOW[1], 0.6), RIM_GLOW[1 if (i + j) % 3 == 0 else 0]   # the glowing crown rim
        e = _ember(i, j, sd, 0.1)
        if e is not None and r < 0.55:
            return EMBER[e], EMBER_GLOW[e]
        if abs(r - 0.3) < 0.07 and hash3(i, 1, 2, 95) > 0.3:
            return mix(TAR[4], SHEEN, 0.5), None                                 # a slow ripple ring
        if hash3(i, j, 3, 97) > 0.93:
            return SHEEN, None                                                   # bubble glints
        return pick(TAR, 0.32 - r * 0.15 + (0.12 if (i - j) % 9 == 0 else 0)), None
    if t == 'splash':
        if f not in ('front', 'west'):
            return None, None
        col_h = 1 + int(hash3(i, 0, sd, 99) ** 1.6 * (h - 1))
        k = h - 1 - j
        if k < col_h:
            if (i % 2 == 1 and k > 0) or hash3(i, k, sd, 101) > 0.85:
                return None, None
            if k == col_h - 1:
                return mix(TAR[5], SHEEN, 0.6), (RIM_GLOW[1] if hash3(i, 5, sd, 102) > 0.45 else None)
            e = _ember(i, k, sd, 0.18, 2, 1)
            if e is not None:
                return EMBER[e], EMBER_GLOW[e]
            return TAR[2], None
        if k == col_h + 1 and hash3(i, 3, sd, 103) > 0.6:
            return TAR[3], RIM_GLOW[0]                                           # a detached drop
        return None, None
    if f in ('top', 'bottom'):
        if t == 'gush' and f == 'top':
            return TAR[1], CORE_GLOW[0]
        return TAR[1], None
    # the stream / gush (side faces, j = 0 at the mouth end)
    if t == 'gush':
        if j < 3 and 1 <= i < w - 1:
            g = CORE_GLOW[1] if (j == 0 and 2 <= i < w - 2) else CORE_GLOW[0]
            return mix(TAR[3], BLOOD[2], 0.6), g                                 # deep red core at the mouth end
        e = _ember(i, j, sd, 0.32)
    else:
        e = _ember(i, j, sd, 0.085, 2, 1) if j < h - 1 else None
    if e is not None:
        return EMBER[e], EMBER_GLOW[e]
    band = hash3(i, math.floor((j + i * 2) / 3), sd, 107)
    v = 0.3 + (band - 0.5) * 0.18                                                # falling streaks
    if i in (1, w - 2) and hash3(i, math.floor(j / 4), sd, 109) > 0.22:
        return (mix(TAR[6], SHEEN, 0.75) if (j + i) % 5 else SHEEN), None       # wet specular down both sides
    if i in (0, w - 1):
        v -= 0.12
    if t == 'gush' and hash3(i, j, sd, 111) > 0.8:
        v += 0.18                                                                # foam
    return pick(TAR, v), None


def vomit_mat(ctx):
    """Thick, glossy black bile: falling streaks, a cool wet sheen down both sides of the stream, clusters of red
    embers caught in it (also on the emissive layer), a deep red core at the mouth end, a puddle with bubbles and a
    dimly glowing crown rim; the splash planes are ragged crowns of drops."""
    c, _ = vomit_px(tag(ctx), ctx.face, ctx.cube.size, ctx.i, ctx.j, ctx.w, ctx.h)
    return c


def vomit_glow(cube_tag, size):
    """Emissive layer: the embers, the red core and the crown rim -- the same texels vomit_mat paints."""
    def make(face):
        def fn(img, u0, v0, w, h):
            px = img.load()
            for jj in range(h):
                for ii in range(w):
                    _, g = vomit_px(cube_tag, face, size, ii, jj, w, h)
                    if g is not None:
                        px[u0 + ii, v0 + jj] = g
        return fn
    return {f'eyes:{face}': make(face) for face in ('front', 'back', 'west', 'east', 'top')}


# ------------------------------------------------------------------ the blessed choripan (toggle: caught in the air)
BREAD = pal('#4a2208', '#7a3e14', '#a85e24', '#cc8438', '#e6a956', '#f4cb82', '#fde6b8')
CRUMB = pal('#a88a5a', '#ccb282', '#e6d3a4', '#f8ecc8')
SAUSAGE = pal('#1e0604', '#3a0e08', '#5c1a0e', '#7e2a16', '#a03e20', '#c45a30', '#de7c48')
CHIMI = (hx('#2e5a14'), hx('#5a8c22'), hx('#9cc04a'))
HOLY = hx('#d8f6ff')


def chori_mat(ctx):
    """A fat cartoon choripan: crusty pan de campo split open along the top with the crumb showing, the grilled
    chorizo poking out of both ends (diagonal grill marks, a fat glint), chimichurri flecks."""
    f = ctx.face
    t = tag(ctx)
    i, j, w, h = ctx.i, ctx.j, ctx.w, ctx.h
    v = 0.55 + face_light(ctx) * 1.0
    if t == 'bun':
        if f == 'top':
            if 1 <= j <= h - 2:
                return pick(CRUMB, 0.55 + (0.2 if (i + j) % 3 == 0 else 0) - (0.25 if j in (1, h - 2) else 0))
            return pick(BREAD, v + 0.1)
        if f in ('west', 'east'):
            if i in (0, w - 1) and j == 0:
                return None
            return pick(CRUMB, 0.45 + (0.15 if (i + j) % 2 else 0)) if j == 0 else pick(BREAD, v - 0.05)
        if f == 'bottom':
            return pick(BREAD, 0.3 + (0.1 if (i * 3 + j) % 5 == 0 else 0))
        # crust: flour dust and darker blisters
        if (i in (0, w - 1)) and j in (0, h - 1):
            return None
        c = pick(BREAD, v + (0.12 if hash3(i, j, 5, 111) > 0.8 else 0) - (0.2 if hash3(i, j, 6, 113) > 0.88 else 0))
        if j == 0:
            c = pick(BREAD, v + 0.18)
        return c
    # sausage
    if f in ('west', 'east'):
        if (i in (0, w - 1)) and (j in (0, h - 1)):
            return None                                          # rounded end
        return pick(SAUSAGE, 0.45 + (0.15 if (i, j) == (1, 1) else 0))
    if f == 'top':
        if (i + j * 2) % 5 == 0:
            return SAUSAGE[0]                                    # grill marks
        if hash3(i, j, 8, 115) > 0.82:
            return CHIMI[1] if hash3(i, j, 9, 117) > 0.5 else CHIMI[0]
        return pick(SAUSAGE, v + (0.25 if j == 1 and i % 4 == 2 else 0))
    if (i + j * 2) % 5 == 0 and f in ('front', 'back'):
        return SAUSAGE[1]
    return pick(SAUSAGE, v - 0.05)


def chori_glow():
    """'Bendito': a few holy-water sparkles on the crust (emissive)."""
    pts = [(2, 0), (5, 1), (9, 0), (12, 1), (7, 2)]
    return {'eyes:front': at([(i, j, HOLY) for i, j in pts]),
            'eyes:top': at([(1, 0, HOLY), (13, 0, HOLY), (6, 4, HOLY)])}


# ------------------------------------------------------------------ layout
C0 = 4.0                     # chain axis height of the chest (authored)
Z1F = -34.0                  # front of the chest = link_1 pivot
SEG1_L = 15
HEAD_TILT = 8.0              # rest dog head tilt (deg, zRot)
CHEST_ROLL = -5.0            # rest: the chest leans onto its right shoulder
NECK_SOCKET = (0.0, -2.0, 0.0)          # where the neck leaves the chest (link_1-local)
NECK_LEN = 11.0                          # socket -> head joint
NECK_REST = (-35.0, 0.0, -CHEST_ROLL * 0.6)   # neck rest rotation relative to the chest (deg)
COLLAR_Z = 3.5                           # collar position along the neck (neck-local, from the head joint back)
TONGUE_YAW = -36.0                       # rest yaw of the tongue (deg): out of the side of the mouth
TONGUE_POSE_YAW = -13.0                  # the centred yaw the posed tongue values are relative to
MOUTH = (0.0, -1.5, -22.0)               # head-local: a fetched item held between the front teeth (fetch_drop)
CUP = (0.0, -2.0, -15.5)                 # head-local: the caught choripan, clamped in the open flower's cup (catch)
TONGUE_ROOT = (0.0, -1.5, -8.0)          # head-local: tongue pivot, in the maw at the height of the mouth line
FLAP_HINGE = {('upper', -1): (-6.0, -6.0, -14.0), ('upper', 1): (6.0, -6.0, -14.0),     # head-local: the outer back
              ('lower', -1): (-5.0, 3.0, -14.0), ('lower', 1): (5.0, 3.0, -14.0)}       # corner of each flap


def BROW_PIVOT(sx):
    return (4.5 * sx, -16.0, -14.2)       # on the top-front edge of the brow ridge
# body links after the chest: (bone, link in front, skin band length, fur length, width, height, inflate,
#                              rest pitch deg (+ = rear up), blood drips)
LINKS = [
    ('link_2', 'link_1', 5, 7, 13, 12, 0.15, 13, False),
    ('link_3', 'link_2', 7, 6, 12, 12, 0.30, 10, True),
    ('link_4', 'link_3', 6, 6, 11, 11, 0.20, -13, False),
    ('link_5', 'link_4', 8, 6, 11, 11, 0.40, -24, True),
    ('link_6', 'link_5', 7, 7, 12, 11, 0.10, 6, False),
    ('link_7', 'link_6', 5, 10, 13, 12, 0.25, 16, True),
]
LINK = {L[0]: L for L in LINKS}
BODY = ['link_1'] + [L[0] for L in LINKS]
CHAIN = ['link_0'] + BODY
LINK_LEN = dict({'link_1': float(SEG1_L)}, **{L[0]: float(L[2] + L[3]) for L in LINKS})   # pivot -> next pivot (+Z)
SPIKES = []                  # (bone, x, y, z) authored base of each rib spike (filled by build, used by skin_mat)
VOMIT_LEN = 30               # column length; re-solved by make_vomit() so the puddle lands on the floor

# the six human arms.  elbow = (|x| out from the midline, world y, dz from the shoulder); wrist = (|x| out, dz);
# joint (extra elbow) likewise.  hand variants: flat, fist (on its knuckles), claw (on its fingertips),
# twist (wrist broken backwards, fingers pointing back).  fingers: lengths inner -> outer.
ARMS = {
    (1, 'right'): dict(seg='link_3', elbow=(13.0, -14.0, -5.0), wrist=(21.0, -16.0), hand='flat', yaw=34,
                       fingers=(6, 9, 8, 7)),
    (1, 'left'): dict(seg='link_3', elbow=(12.0, -8.0, -2.0), wrist=(17.0, -10.0), hand='fist', yaw=14),
    (2, 'right'): dict(seg='link_5', elbow=(17.0, -9.0, 1.0), wrist=(23.0, -1.0), hand='claw', yaw=8,
                       fingers=(4, 6, 6, 5)),
    (2, 'left'): dict(seg='link_5', elbow=(11.0, -13.0, -3.0), joint=(20.0, 1.0, 4.0), wrist=(18.0, 1.0),
                      hand='twist', yaw=158, fingers=(7, 8, 9, 6)),
    (3, 'right'): dict(seg='link_7', elbow=(14.0, -6.0, 5.0), wrist=(20.0, 12.0), hand='flat', yaw=-30,
                       fingers=(8, 7, 9, 5)),
    (3, 'left'): dict(seg='link_7', elbow=(16.0, -10.0, 8.0), wrist=(21.0, 16.0), hand='claw', yaw=-20,
                      fingers=(5, 6, 5, 4)),
}
HAND_DROP = {'flat': 2.0, 'twist': 2.0, 'fist': 4.2}      # wrist pivot height above the floor; claw: 1 + finger
ARM_GEOM = {}                # filled by build(): lengths + forearm frame per arm (used by the pose IK)


def arm_names(idx, side):
    return f'arm_{idx}_{side}', f'forearm_{idx}_{side}', f'joint_{idx}_{side}', f'hand_{idx}_{side}'


def hand_drop(spec):
    if spec['hand'] == 'claw':
        return 1.0 + max(spec['fingers'])
    return HAND_DROP[spec['hand']]


def body_fk(rel=None, root_rot=(0.0, 0.0, 0.0), root_pos=(0.0, 0.0, 0.0), slide=None):
    """World frames {link: (R, P)} of link_1..link_7 composed like a hierarchy: each link's rotation relative to the
    link in front = its rest hunch (pitch, 0, roll) + rel[link] (deg, Euler added); its pivot sits at the end of the
    link in front, + slide[link] (a local (dx, dy, dz) in the front link's frame).  rel = {} gives the rest pose."""
    rel = rel or {}
    slide = slide or {}
    R = R_deg(*(np.array([0.0, 0.0, CHEST_ROLL]) + np.array(root_rot, float)))
    P = np.array([0.0, C0, Z1F]) + np.array(root_pos, float)
    out = {'link_1': (R, P)}
    L = float(SEG1_L)
    for (name, par, Lb, Lf, W, Hh, infl, pitch, drip) in LINKS:
        roll = -CHEST_ROLL if par == 'link_1' else 0.0
        P = P + R @ (np.array([0.0, 0.0, L]) + np.array(slide.get(name, (0.0, 0.0, 0.0)), float))
        R = R @ R_deg(*(np.array([pitch, 0.0, roll]) + np.array(rel.get(name, (0.0, 0.0, 0.0)), float)))
        out[name] = (R, P)
        L = float(Lb + Lf)
    return out


def neck_fk(R1, P1, neck_rel=(0.0, 0.0, 0.0), head_rel=(0.0, 0.0, 0.0), head_slide=(0.0, 0.0, 0.0)):
    """(neck world rot, head joint, head world rot) for a chest frame, like the neck/head hierarchy hanging off the
    chest socket (rel = Euler deltas on the rest local rotations, head_slide = offset of the head joint along the
    neck frame)."""
    Rn = R1 @ R_deg(*(np.array(NECK_REST) + np.array(neck_rel, float)))
    S = P1 + R1 @ np.array(NECK_SOCKET)
    Hj = S + Rn @ (np.array([0.0, 0.0, -NECK_LEN]) + np.array(head_slide, float))
    Rh = Rn @ R_deg(*(np.array(HEAD_LOCAL_REST) + np.array(head_rel, float)))
    return Rn, Hj, Rh


def _head_local_rest():
    R1 = R_deg(0, 0, CHEST_ROLL)
    Rn = R1 @ R_deg(*NECK_REST)
    return euler_zyx(Rn.T @ R_deg(0, 0, HEAD_TILT))


HEAD_LOCAL_REST = _head_local_rest()


def wdir(pitch, yaw, roll=0.0):
    """World rotation of a link from WORLD angles: pitch + = rear end up, yaw + = rear end toward +X."""
    return R_deg(0, yaw, 0) @ R_deg(pitch, 0, 0) @ R_deg(0, 0, roll)


def body_world(P1, ang, slide=None):
    """World frames for link_1..link_7 from world angles ang[link] = (pitch, yaw[, roll]); each pivot sits at the end
    of the link in front, minus slide[link] texels (telescoped into it)."""
    slide = slide or {}
    out = {}
    P = np.asarray(P1, float)
    prev = None
    for n in BODY:
        if prev is not None:
            Rp, Pp = out[prev]
            P = Pp + Rp @ np.array([0.0, 0.0, LINK_LEN[prev] - slide.get(n, 0.0)])
        a = ang[n]
        out[n] = (wdir(*a), P)
        prev = n
    return out


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


# ------------------------------------------------------------------ toggles (Java: ModelPart.visible)
TOGGLE_DEFAULT = {'vomit': False, 'choripan': False}
POSE_TOGGLES = {'vomit': {'vomit': True}, 'catch': {'choripan': True}}


def visible_set(pose=None):
    vis = dict(TOGGLE_DEFAULT)
    vis.update(POSE_TOGGLES.get(pose, {}))
    show = os.environ.get('CHORI_SHOW', '')
    if show:                                                    # preview helper: 'all' or 'bone,bone'
        for k in vis:
            if show == 'all' or k in show.split(','):
                vis[k] = True
    return {k for k, v in vis.items() if v}


class ChoriModel(Model):
    """Exports every bone to Java; the preview JSON hides the toggle bones the current pose does not show."""
    visible = None

    def to_json(self):
        d = super().to_json()
        d['toggles'] = {'default': dict(TOGGLE_DEFAULT), 'poses': {p: dict(t) for p, t in POSE_TOGGLES.items()}}
        if self.visible is None:
            return d
        hide = set()
        for b in self.bones():
            if b.name in TOGGLE_DEFAULT and b.name not in self.visible:
                for sub in b.walk():
                    hide.add(sub.name)
        for bd in d['bones']:
            if bd['name'] in hide and bd['cubes']:
                bd['hidden_cubes'] = bd['cubes']
                bd['cubes'] = []
        return d


def _argv(flag):
    a = sys.argv
    return a[a.index(flag) + 1] if flag in a and a.index(flag) + 1 < len(a) else None


# ------------------------------------------------------------------ module contract
DEFAULT_MAT = link_fur
FOCUS = 'head'


def build():
    b = Build()
    box = b.box
    SPIKES.clear()
    F = body_fk()

    # ---------------- link_1: the chest with the sweater remnant
    R1, P1 = F['link_1']
    b.bone('link_1', None, P1, R1, mat=link_fur)
    box('link_1', (-7, -5.5, 0), (14, 11, SEG1_L), name='core', tear=(False, True))
    box('link_1', (-5, -6.5, 0.5), (10, 1, SEG1_L - 1), name='cap', tear=(False, True))
    box('link_1', (-5, 5.5, 1), (10, 1, SEG1_L - 2), name='keel', tear=(False, True))
    box('link_1', (-7, -6.5, 0), (14, 13, 12), mat=sweater_mat, name='sweater', inflate=0.45)

    # ---------------- link_2..link_7 (top-level): skin band (rib cage + pinched waist + spine ridge) + a fur link
    for k, (name, par, Lb, Lf, W, Hh, infl, pitch, drip) in enumerate(LINKS):
        R, P = F[name]
        b.bone(name, None, P, R, mat=link_fur)
        ti = 0.3 + 0.07 * k                                 # per-link growth: nested / telescoped bands never share planes
        box(name, (-4.5, -4.5, -3), (9, 9, max(3, Lb // 2 + 3)), mat=skin_mat, name='tube', inflate=ti)
        box(name, (-3.5, -3.5, Lb // 2 - 1), (7, 7, Lb - Lb // 2 + 3), mat=skin_mat, name='pinch', inflate=ti)
        nrib = 2 if Lb >= 7 else 1
        for q in range(nrib):
            rz = 0.3 + q * 1.8 if nrib == 2 else 0.8
            box(name, (-5.5, -5.5, rz), (11, 5, 1), mat=rib_mat, name='rib', inflate=ti * 0.5)
        box(name, (-1, -6, -1), (2, 3, Lb + 2), mat=spine_mat, name='spine', inflate=0.45 + 0.03 * k)
        last = name == 'link_7'
        z0 = float(Lb)
        box(name, (-W / 2, -Hh / 2 + 1, z0), (W, Hh - 2, Lf), name='core', inflate=infl, tear=(True, not last), drip=drip)
        box(name, (-W / 2 + 2, -Hh / 2, z0 + 0.5), (W - 4, 1, Lf - 1), name='cap', inflate=infl, tear=(True, not last))
        box(name, (-W / 2 + 2, Hh / 2 - 1, z0 + 0.5), (W - 4, 1, Lf - 1), name='keel', inflate=infl, tear=(True, not last))
        if last:
            box(name, (-W / 2 + 2, -Hh / 2 + 2, z0 + Lf), (W - 4, Hh - 4, 1), name='rump', inflate=infl)

    # broken ribs piercing the skin (link_3 band right flank, link_5 band left top)
    for bn, lp in (('link_3', (-4.0, -4.0, 1.0)), ('link_5', (3.0, -4.0, 4.0))):
        box(bn, (lp[0], lp[1] - 6.0, lp[2]), (1, 6, 1), mat=spike_mat, name='spike')
        p = b.r.abs_pivot[bn]
        SPIKES.append((bn, p[0] + lp[0] + 0.5, p[1] - 4.6, p[2] + lp[2] + 0.5))

    # ---------------- the two real dachshund front legs (planted, bowed in, paws turned out)
    for side, sx in (('right', -1), ('left', 1)):
        lb, pb = f'front_{side}_leg', f'front_{side}_paw'
        Sw = b.wpos('link_1', (4.5 * sx, 3.0, 6.0))
        Rl = R_deg(0, 0, 5 * sx)
        b.bone(lb, 'link_1', Sw, Rl, mat=leg_fur)
        Lleg = (21.0 - Sw[1]) / math.cos(math.radians(5))
        box(lb, (-2.5, -1, -2.5), (5, 6, 5), name='shoulder', inflate=0.18)
        box(lb, (-2, 4, -2), (4, int(math.ceil(Lleg - 3)), 4), name='leg')
        Pw = Sw + Rl @ np.array([0.0, Lleg, 0.0])
        Pw[1] = 21.0
        b.bone(pb, lb, Pw, R_deg(0, -16 * sx, 0), mat=paw_mat)
        box(pb, (-2.5, 0, -4), (5, 3, 6), name='paw')
        box(pb, (-2, 1, -5), (4, 2, 1), name='toes')

    # ---------------- link_0 (top-level, pivot at the head joint): the neck runs back from it to the chest socket
    Rn, Hj, Rh = neck_fk(R1, P1)
    b.bone('link_0', None, Hj, np.eye(3))
    b.bone('neck', 'link_0', Hj, Rn, mat=neck_mat)
    box('neck', (-4.5, -5, -2), (9, 9, 16), name='tube', inflate=-0.12)
    for z in (8.0, 11.0):
        box('neck', (-5.5, -6, z), (11, 6, 1), name='ring')
    box('neck', (-5.5, -6, COLLAR_Z), (11, 11, 2), mat=collar_mat, name='collar')
    # the big brass 'CHORIPAN' tag hanging from the collar ring (its own bone: it swings)
    Tw = b.wpos('neck', (0.0, 5.6, COLLAR_Z + 1.0))
    b.bone('tag', 'neck', Tw, np.eye(3), mat=tag_mat)
    box('tag', (-1, -0.5, -0.4), (2, 2, 1), name='ring')
    box('tag', (-TAG_W / 2, 1.2, -0.5), (TAG_W, TAG_H, 1), name='plate')

    # ---------------- head (pivot = link_0 pivot, under the back of the skull); level, with a dog tilt
    b.bone('head', 'link_0', Hj, Rh, mat=skull_mat)
    hp = b.r.abs_pivot['head']
    fz = FACE_Z
    box('head', (-9, -16, SKULL_Z), (18, 10, -SKULL_Z), name='skull', hp=hp)
    box('head', (-7, -17, -12), (14, 1, 10), name='dome', hp=hp)
    # the eye sockets: rim pieces 2 texels proud of the skull, the eyes recessed one texel inside
    box('head', (-9, EYE_Y - 1, fz), (18, 1, 2), mat=face_mat, name='ridge', hp=hp)
    box('head', (-1, EYE_Y, fz), (2, EYE_H, 2), mat=face_mat, name='blaze', hp=hp)
    box('head', (-9, EYE_Y, fz), (1, EYE_H, 2), mat=face_mat, name='temple', hp=hp)
    box('head', (8, EYE_Y, fz), (1, EYE_H, 2), mat=face_mat, name='temple', hp=hp)
    box('head', (-9, EYE_Y + EYE_H, fz), (18, 1, 2), mat=face_mat, name='cheekband', hp=hp)
    for k, sd in ((0, 'r'), (1, 'l')):
        box('head', (EYE_X[k], EYE_Y, fz + 1), (EYE_W, EYE_H, 1), mat=eye_mat, name='eye', side=sd, hp=hp,
            decals={'eyes:front': eye_glow(sd)})
    # the maw: jowls either side, the chin under it, the throat at the back, two rings of needles inside
    hx0, hx1, hy0, hy1 = HOLE
    hw, hh = int(hx1 - hx0), int(hy1 - hy0)
    box('head', (-9, hy0, fz), (int(hx0 + 9), hh, 14), name='side', hp=hp)
    box('head', (hx1, hy0, fz), (int(9 - hx1), hh, 14), name='side', hp=hp)
    box('head', (hx0, hy1, fz), (hw, 5, 13), name='chin', hp=hp)
    box('head', (hx0, hy0, THROAT_Z), (hw, hh, -int(THROAT_Z)), mat=throat_mat, name='throat')
    box('head', (hx0, hy0, fz + 0.6), (hw, hh, 0), mat=ring_mat, name='ring')
    box('head', (hx0, hy0, fz + 4.4), (hw, hh, 0), mat=ring_mat, name='ring', deep=True)

    # chunky tan brows on the brow ridge, inner ends raised (the cute puppy-eyes look), bones so they can furrow
    for side, sx in (('right', -1), ('left', 1)):
        bb = f'{side}_brow'
        b.lbone(bb, 'head', BROW_PIVOT(sx), rot=(0, 0, 13 * -sx), mat=brow_mat)
        box(bb, (-2.5, -1.4, -1.6), (5, 2, 2), name='brow')

    # the four muzzle flaps, each hinged at the OUTER back corner of its quarter of the muzzle (the corner of the maw):
    # they peel back radially, NE / NW / SE / SW, round the open hole (Kit.flower)
    def hbox(bone, frm, size, **kw):
        piv = b.r.abs_pivot[bone]
        loc = tuple(frm[q] - (piv[q] - hp[q]) for q in range(3))
        return box(bone, loc, size, **kw)

    for side, sx in (('right', -1), ('left', 1)):
        ub, lb = f'jaw_upper_{side}', f'jaw_lower_{side}'
        b.lbone(ub, 'head', FLAP_HINGE[('upper', sx)], mat=flap_mat)
        hbox(ub, (-6.0 if sx < 0 else 0.0, -6, -26), (6, 4, 12), name='flap', upper=True, sx=sx)
        hbox(ub, (-4.15 if sx < 0 else 0.15, -7, -27), (4, 3, 3), mat=nose_mat, name='nose', sx=sx)
        hbox(ub, (-3.15 if sx < 0 else 0.15, -8, -26.6), (3, 1, 2), mat=nose_mat, name='bulb', sx=sx)
        hbox(ub, (5.5 * sx, -2, -25.5), (0, 5, 11), mat=teeth_mat, name='teeth',
             down=True, fangs=3, salt=11 + sx)
        hbox(ub, (2.4 * sx, -2, -25), (0, 3, 10), mat=teeth_mat, name='teeth', down=True, fangs=0, salt=13 + sx)
        hbox(ub, (-6.0 if sx < 0 else 0.0, -2, -25.6), (6, 4, 0), mat=teeth_mat, name='teeth', down=True,
             fangs=2, salt=17 + sx)
        hbox(ub, (-12.0 if sx < 0 else 6.0, -5, -20), (6, 5, 0), mat=whisker_mat, name='whisker', sx=sx)

        b.lbone(lb, 'head', FLAP_HINGE[('lower', sx)], mat=flap_mat)
        hbox(lb, (-5.0 if sx < 0 else 0.0, -1, -25), (5, 4, 11), name='flap', upper=False, sx=sx)
        hbox(lb, (4.4 * sx, -5, -24.5), (0, 4, 10), mat=teeth_mat, name='teeth', down=False, fangs=2, salt=19 + sx)
        hbox(lb, (1.5 * sx, -4, -24), (0, 3, 10), mat=teeth_mat, name='teeth', down=False, fangs=0, salt=23 + sx)
        hbox(lb, (-5.0 if sx < 0 else 0.0, -4, -24.6), (5, 3, 0), mat=teeth_mat, name='teeth', down=False,
             fangs=2, salt=29 + sx)
        if sx < 0:
            hbox(lb, (-5.1, 3, -19), (0, 5, 1), mat=drool_mat, name='drool')

    # black tongue (rest: lolling out of the LEFT side of the mouth like a panting dog, so the tag stays readable)
    b.lbone('tongue', 'head', TONGUE_ROOT, rot=(0, TONGUE_YAW, 0), mat=tongue_mat)
    box('tongue', (-2.5, -0.5, -18), (5, 1, 18), name='tongue', inflate=-0.1)
    b.lbone('tongue_tip', 'tongue', (0, 0, -18), rot=(62, -10, 18), mat=tongue_mat)
    box('tongue_tip', (-2.5, -0.5, -8), (5, 1, 8), name='tongue', inflate=-0.1)
    box('tongue_tip', (-1.5, -0.5, -12), (3, 1, 4), name='tongue', inflate=-0.1, tip=True)

    # ears: limp and far too long, hanging nearly to the ground (world-hanging, whatever the head tilt)
    for side, sx in (('right', -1), ('left', 1)):
        eb, tb = f'{side}_ear', f'{side}_ear_tip'
        Pw = b.wpos('head', (10.0 * sx, -13.0, -4.0))
        b.bone(eb, 'head', Pw, EAR_WORLD(sx), mat=ear_mat)
        box(eb, (-1, -1, -2), (2, 17, 5), name='ear', sx=sx)
        box(eb, (-1.5, 9.5, -3.5), (3, 6, 7), name='ear', sx=sx)
        b.lbone(tb, eb, (0, 16, 0), rot=(-7, 0, 6 * sx), mat=ear_mat)
        box(tb, (-1, 0, -4), (2, 21, 8), name='ear_tip', sx=sx)

    # ---------------- toggles on the head: the black vomit column and the caught choripan
    b.lbone('vomit', 'head', (0.0, (HOLE[2] + HOLE[3]) / 2, FACE_Z + 2.0), rot=(-90, 0, 0), mat=vomit_mat)
    vl = int(VOMIT_LEN)
    box('vomit', (-3.5, -3, -3.5), (7, 8, 7), name='gush', decals=vomit_glow('gush', (7, 8, 7)))
    box('vomit', (-2.5, 4, -2.5), (5, vl - 4, 5), name='stream', inflate=0.2, decals=vomit_glow('stream', (5, vl - 4, 5)))
    box('vomit', (-9, vl - 1.0, -9), (18, 1, 18), name='puddle')
    box('vomit', (-6, vl - 6.5, 0.3), (12, 6, 0), name='splash')
    box('vomit', (0.3, vl - 6.5, -6), (0, 6, 12), name='splash')
    # cubeless locator between the front teeth: Java renders the fetched ItemStack here (fetch_drop) and drops it
    b.lbone('mouth_item', 'head', MOUTH, rot=(0, 0, 0))
    b.lbone('choripan', 'head', CUP, rot=(0, 0, 0), mat=chori_mat)
    box('choripan', (-7, -1.5, -2.5), (14, 4, 5), name='bun', decals=chori_glow())
    box('choripan', (-8.5, -2.6, -1.5), (17, 3, 3), name='sausage')

    # ---------------- tail: big enough to read, carried high and curved up, tan tip -- it still wags
    Lb, Lf = LINK['link_7'][2], LINK['link_7'][3]
    b.lbone('tail', 'link_7', (0, -3.5, Lb + Lf - 1.0), rot=(48, 0, 0), mat=tail_mat)
    box('tail', (-2, -2, 0), (4, 4, 12), name='base')
    b.lbone('tail_tip', 'tail', (0, 0, 11.5), rot=(26, 0, 0), mat=tail_mat)
    box('tail_tip', (-1.5, -1.5, 0), (3, 3, 10), name='tip')

    # ---------------- sweater shreds hanging off the spine (band + two strips, one with a loose yarn end)
    shreds = [('shred_1', 'link_2', 9.0, 11, 7), ('shred_2', 'link_3', 10.0, 8, 13),
              ('shred_3', 'link_4', 9.6, 13, 6), ('shred_4', 'link_5', 11.0, 6, 11)]
    for k, (name, par, zc, lr, ll) in enumerate(shreds):
        W, Hh, infl = LINK[par][4], LINK[par][5], LINK[par][6]
        top = -Hh / 2 - infl
        b.lbone(name, par, (0, top, zc), mat=shred_mat)
        box(name, (-W / 2 - 0.6, -0.84, -1.0), (W + 1, 1, 2), name='band', inflate=0.12)
        box(name, (-W / 2 - 0.9, 0.2, -1.5), (0, lr, 3), name='strip', yarn=(k % 2 == 0))
        box(name, (W / 2 + 0.9, 0.2, -1.0), (0, ll, 2), name='strip', yarn=(k % 2 == 1))

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
        # upper arm: a 5 x 5 shaft out of a torn fur collar, a lean deltoid bulge near the shoulder
        b.bone(ab, seg, S, R1w, mat=arm_mat)
        box(ab, (-3.5, -1.5, -3.5), (7, 4, 7), name='collar')
        box(ab, (-2.5, 0, -2.5), (5, L1 + 1, 5), name='upper', inflate=0.1, yb=0.0, limb=L1)
        box(ab, (-3, 2, -3.2 if sx < 0 else -2.8), (6, max(5, L1 // 3), 6), name='bicep', yb=2.0, limb=L1)
        # forearm: a bony elbow knob on the outside of the bend, a 4 x 4 forearm tapering into a 3 x 3 wrist
        b.bone(fb, ab, E, R2w, mat=arm_mat)
        out = -((S - E) / np.linalg.norm(S - E) + ((J if J is not None else Wt) - E) /
                np.linalg.norm((J if J is not None else Wt) - E))
        ol = R2w.T @ out
        ol[1] = 0.0
        ol = ol / max(1e-6, float(np.linalg.norm(ol)))
        box(fb, (ol[0] * 1.6 - 2.5, -2.5, ol[2] * 1.6 - 2.5), (5, 4, 5), name='knob', inflate=0.25)   # elbow point
        lf1 = max(4, int(round(L2 * 0.58)))
        box(fb, (-2, 0, -2), (4, lf1, 4), name='fore', inflate=0.05, yb=0.0, limb=L2 + L3)
        box(fb, (-1.5, lf1 - 1, -1.5), (3, L2 - lf1 + 1, 3), name='wrist', inflate=0.1, yb=float(lf1 - 1),
            limb=L2 + L3)
        last = fb
        if J is not None:
            b.bone(jb, fb, J, R3w, mat=arm_mat)
            box(jb, (-2.5, -2.5, -2.5), (5, 5, 5), name='knob')
            box(jb, (-1.5, 0, -1.5), (3, L3, 3), name='jseg', inflate=0.12, yb=float(L2), limb=L2 + L3)
            last = jb
        Ll = L3 if J is not None else L2
        box(last, (-2, Ll - 2.5, -2), (4, 2, 4), name='wknob')
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

    m = ChoriModel('choripan_demonio', 256, 256, b.r.roots)
    m.scale = 0.5
    m.visible = visible_set(_argv('--pose'))
    return m


def EAR_WORLD(sx):
    """Rest world orientation of an ear: hanging straight down, the leather turned toward the front."""
    return R_deg(4, -22 * sx, -6 * sx)


# ------------------------------------------------------------------ pose kit (world-space posing)
def look_rot(f, up=(0.0, -1.0, 0.0)):
    """World rotation whose local +Z points along f and whose local -Y (the back) is as close as possible to `up`."""
    z = np.asarray(f, float)
    z = z / np.linalg.norm(z)
    u = np.asarray(up, float)
    u = u - z * float(u @ z)
    u = u / max(1e-9, float(np.linalg.norm(u)))
    y = -u
    x = np.cross(y, z)
    return np.column_stack([x, y, z])


def yaw_of(R):
    """Heading (deg) of a frame's -Z axis, as a yRot about the world Y axis."""
    f = R @ np.array([0.0, 0.0, -1.0])
    return math.degrees(math.atan2(-f[0], -f[2]))


FLOWER_ELEV = (34.0, 60.0)                 # peel directions (deg from horizontal) of the upper / lower petals
FLAPS = {('upper', -1): 'jaw_upper_right', ('upper', 1): 'jaw_upper_left',
         ('lower', -1): 'jaw_lower_right', ('lower', 1): 'jaw_lower_left'}
FLAP_JITTER = {('upper', -1): 0.6, ('upper', 1): -0.3, ('lower', -1): -0.8, ('lower', 1): 1.0}


def axis_rot(axis, deg):
    a = np.asarray(axis, float)
    a = a / np.linalg.norm(a)
    t = math.radians(deg)
    K = np.array([[0, -a[2], a[1]], [a[2], 0, -a[0]], [-a[1], a[0], 0]])
    return np.eye(3) + math.sin(t) * K + (1 - math.cos(t)) * (K @ K)


def petal_rot(sx, sy, elev, theta, curl=0.0):
    """Head-local rotation of one flap opened by theta (deg): about the tangent axis through its hinge, so the tip
    (-Z) swings toward the radial direction u = (sx cos elev, sy sin elev, 0) (sy -1 = up); curl rolls the petal
    about its own length so the toothed inner face turns to the camera."""
    e = math.radians(elev)
    u = np.array([sx * math.cos(e), sy * math.sin(e), 0.0])
    R = axis_rot((u[1], -u[0], 0.0), theta)
    if curl:
        R = R @ axis_rot((0.0, 0.0, -1.0), curl * sx * -sy)
    return R


class Kit:
    def __init__(self):
        self.m = build()
        self.b = {bn.name: bn for bn in self.m.bones()}
        self.rest = {n: (bn.rot, bn.pivot) for n, bn in self.b.items()}
        # posed tongue values are written against the centred yaw; table() re-bases them on the real rest
        self.rest['tongue'] = ((0.0, TONGUE_POSE_YAW, 0.0), self.rest['tongue'][1])
        self.d = {}
        # effective forearm length (elbow -> wrist, through the extra joint of the broken arm)
        self.l2eff = {key: float(np.linalg.norm(self.wpos(arm_names(*key)[3]) - self.wpos(arm_names(*key)[1])))
                      for key in ARMS}

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
        if 'tongue' in self.d:
            # pose tongue values were authored against the old centred rest yaw: keep each pose's look exactly
            self.d['tongue'][1] += TONGUE_POSE_YAW - TONGUE_YAW
        for n, d in self.d.items():
            if any(abs(v) > 1e-6 for v in d):
                out[n] = tuple(math.radians(v) for v in d[:3]) + tuple(float(v) for v in d[3:])
        return out

    # ---- the chain
    def body(self, F):
        """Place link_1..link_7 at world frames {link: (R, P)}."""
        for n in BODY:
            R, P = F[n]
            self.set_world_rot(n, R)
            self.set_world_pos(n, P)

    def shift(self, dv):
        """Move the whole creature (every top-level bone) by a world offset."""
        for n in CHAIN:
            P = self.wpos(n)
            self.set_world_pos(n, P + np.asarray(dv, float))

    def neck_head(self, F, Rn, Rh, slide=0.0):
        """Neck leaving the chest socket with world rotation Rn (its -Z toward the head), head joint at
        NECK_LEN + slide along it (link_0 moves there; its own rotation stays at rest), head world rot Rh."""
        R1, P1 = F['link_1']
        S = P1 + R1 @ np.array(NECK_SOCKET)
        Hj = S + Rn @ np.array([0.0, 0.0, -(NECK_LEN + slide)])
        self.set_world_pos('link_0', Hj)
        self.set_world_rot('neck', Rn)
        self.set_world_rot('head', Rh)
        return Hj

    def legacy_neck(self, F, neck_rel=(0, 0, 0), head_rel=(0, 0, 0), head_slide=(0, 0, 0)):
        Rn, Hj, Rh = neck_fk(*F['link_1'], neck_rel, head_rel, head_slide)
        self.set_world_pos('link_0', Hj)
        self.set_world_rot('neck', Rn)
        self.set_world_rot('head', Rh)

    def face_yaw(self):
        """Heading of the face: the head's -Z, or its chin direction when the head points straight up / down."""
        Rh = self.R('head')
        f = Rh @ np.array([0.0, 0.0, -1.0])
        if math.hypot(f[0], f[2]) < 0.45:
            f = Rh @ np.array([0.0, 1.0, 0.0]) * (1.0 if f[1] < 0 else -1.0)
        return math.degrees(math.atan2(-f[0], -f[2]))

    def hang_tag(self, swing=0.0, floor=23.6):
        """The name tag hangs plumb from the collar ring, facing where the face faces (swing: xRot, + = lower edge
        back).  If the ring is too low for it to hang free, it swings forward until it rests above the floor."""
        yaw = self.face_yaw()
        for k in range(40):
            self.set_world_rot('tag', R_deg(0, yaw, 0) @ R_deg(swing - k * 4.0, 0, 0))
            if self.lowest(['tag']) <= floor:
                break

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

    def fit_target(self, idx, side, W):
        """Slide a wrist target horizontally (toward / away from the shoulder) until the arm can reach it without
        locking straight or folding flat."""
        g = ARM_GEOM[(idx, side)]
        L2 = self.l2eff[(idx, side)]
        lo, hi = abs(g['L1'] - L2) + 2.0, g['L1'] + L2 - 1.0
        S = self.wpos(arm_names(idx, side)[0])
        W = np.asarray(W, float).copy()
        h = W - S
        h[1] = 0.0
        if np.linalg.norm(h) < 1e-6:
            h = np.array([-1.0 if side == 'right' else 1.0, 0.0, 0.0])
        h /= np.linalg.norm(h)
        for _ in range(120):
            dist = float(np.linalg.norm(W - S))
            if dist < lo:
                W += h * 0.5
            elif dist > hi:
                W -= h * 0.5
            else:
                break
        return W

    def plant_arm(self, idx, side, xz, pole, yaw_deg, extra=None, lift=0.0):
        spec = ARMS[(idx, side)]
        W = np.array([xz[0], 24.0 - hand_drop(spec) - lift, xz[1]])
        W = self.fit_target(idx, side, W)
        Hw = R_deg(0, yaw_deg, 0) if extra is None else extra
        self.arm(idx, side, W, pole, Hw)
        self.unfloor_arm(idx, side, W, pole, Hw)

    def unfloor_arm(self, idx, side, W, pole, Hw, floor=24.0):
        """Nothing of the arm may sink into the floor: lift the wrist target (and the elbow pole) until it clears."""
        ab, fb, jb, hb = arm_names(idx, side)
        parts = [n for n in (ab, fb, jb, hb) if n in self.b]
        W = np.asarray(W, float).copy()
        pole = np.asarray(pole, float).copy()
        for it in range(20):
            over = self.lowest(parts) - floor
            if over <= 0.05:
                break
            if self.lowest([hb]) - floor > 0.05:
                W[1] -= over
            else:
                pole[1] -= 0.6                                 # an elbow / extra joint dipping: bend it up more
                if it >= 6:
                    W[1] -= 1.0                                # ...and if that is not enough, lift the hand too
            self.arm(idx, side, W, pole, Hw)

    def plant_leg(self, side, reach_deg, paw_yaw=None, bow=5.0):
        """Front leg: solve the swing so the paw lands flat on the floor; reach_deg only picks the direction
        (negative = forward)."""
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
        yaw = float(np.degrees(np.arctan2(self.R('link_1')[0, 2], self.R('link_1')[2, 2])))
        self.set_world_rot(lb, R_deg(0, yaw, 0) @ R_deg(ang, 0, 0) @ R_deg(0, 0, bow * sx))
        py = -16 * sx if paw_yaw is None else paw_yaw
        self.set_world_rot(pb, R_deg(0, yaw + py, 0))
        P = self.wpos(pb)
        if abs(P[1] - 21.0) > 0.05:
            self.set_world_pos(pb, (P[0], 21.0, P[2]))

    def hang_ears(self, swing=0.0, clamp_y=23.4, splay=0.0):
        """Ears hang plumb (whatever the head does), swung by `swing` (xRot, + = lower ends back).  Where the floor is
        in the way the leather first folds at the knee and the tip lies forward on the ground, and only then does the
        whole ear splay out sideways."""
        yaw = self.face_yaw()
        for side, sx in (('right', -1), ('left', 1)):
            eb, tb = f'{side}_ear', f'{side}_ear_tip'
            tip0 = list(self.d.get(tb, [0.0] * 6))
            Ry = R_deg(0, yaw, 0)
            done = False
            for k in range(40):
                out = splay + k * 3.0
                self.set(tb, *tip0)
                self.set_world_rot(eb, Ry @ R_deg(swing, 0, out * -sx) @ EAR_WORLD(sx))
                Rt0 = self.R(tb)
                for q in range(24):
                    if self.lowest([eb, tb]) <= clamp_y:
                        done = True
                        break
                    if self.lowest([eb]) > clamp_y:
                        break
                    # fold the tip straight forward (about the face's own left-right axis) onto the floor
                    self.set_world_rot(tb, Ry @ R_deg(-4.0 * (q + 1), 0, 0) @ Ry.T @ Rt0)
                if done:
                    break

    def unfloor(self, n, axis=0, step=-4.0, floor=23.8, tries=30):
        """Rotate bone n about one local axis (deg steps) until it (with its children) clears the floor."""
        names = [b.name for b in self.b[n].walk()]
        for _ in range(tries):
            if self.lowest(names) <= floor:
                return
            d = self.d.get(n, [0.0] * 6)
            d[axis] += step
            self.set(n, *d)

    def flower(self, up, lo=None, elev_up=FLOWER_ELEV[0], elev_lo=FLOWER_ELEV[1], jitter=0.0, curl=0.0):
        """Peel the four muzzle flaps open round the maw: each flap turns `up` / `lo` degrees about the tangent axis
        through its hinge (the outer back corner), so its tip swings radially outward -- the upper pair toward
        NW / NE at `elev_up` deg above horizontal, the lower pair toward SW / SE at `elev_lo` deg below.  jitter:
        +- deg per flap so the four never open in lockstep; curl: roll of each petal about its own length (deg,
        + turns its inner, toothed face toward the camera)."""
        for (which, sx), name in FLAPS.items():
            th = (up if which == 'upper' else (up if lo is None else lo))
            th += jitter * FLAP_JITTER[(which, sx)]
            self.set(name, *euler_zyx(petal_rot(sx, -1 if which == 'upper' else 1,
                                                 elev_up if which == 'upper' else elev_lo, th, curl)))

    def brows(self, rz, dy=0.0):
        """rz > 0: inner ends up (sad / pleading); rz < 0: inner ends down (furious).  dy is clamped to -0.3 (a lift
        any bigger opens a gap between the brow and the brow ridge)."""
        dy = max(-0.3, dy)
        self.set('right_brow', 0, 0, rz, 0, dy, 0)
        self.set('left_brow', 0, 0, -rz, 0, dy, 0)

    def ground(self, names=None, floor=23.7):
        """Shift the creature so the lowest point of `names` (default every link) rests on the floor."""
        low = self.lowest(names or BODY)
        self.shift((0.0, floor - low, 0.0))


def gait(k, phase, stride=9.0, spread=17.0, lift=7.0, skip=()):
    """Arms walking: each arm's hand target swings fore/aft along its link's heading by stride*cos(phase) and lifts
    off the floor by lift*max(0, sin(phase)) (the hand in the air is mid-step)."""
    for (idx, side), spec in ARMS.items():
        if (idx, side) in skip:
            continue
        sx = -1 if side == 'right' else 1
        ab = arm_names(idx, side)[0]
        seg = spec['seg']
        S = k.wpos(ab)
        fwd = k.R(seg) @ np.array([0.0, 0.0, -1.0])
        fwd[1] = 0.0
        fwd /= np.linalg.norm(fwd)
        outv = np.array([-fwd[2], 0.0, fwd[0]]) * -sx       # perpendicular, toward the arm's side
        if float(outv @ (S - k.wpos(seg))) < 0:
            outv = -outv
        ph = math.radians(phase[(idx, side)])
        W = S + outv * spread + fwd * (stride * math.cos(ph))
        up = lift * max(0.0, math.sin(ph))
        yaw = math.degrees(math.atan2(-fwd[0], -fwd[2])) + sx * -spec['yaw'] * 0.5
        k.plant_arm(idx, side, (W[0], W[2]), (sx * 0.5, -1.0, 0.0), yaw, lift=up)


def make_poses():
    poses = {}
    poses['unspool'] = make_unspool()
    poses['run'] = make_run()
    poses['fetch_drop'] = make_fetch_drop()
    poses['beg'] = make_beg()
    poses['lunge'] = make_lunge()
    poses['catch'] = make_catch()
    poses['vomit'] = make_vomit()
    poses['retract'] = make_retract()
    poses['stretch'] = make_stretch()
    poses['coil'] = make_coil()
    for q in range(4):
        poses[f'walk_{q + 1}'] = make_walk(q)
    return poses


# ------------------------------------------------------------------ walk_1..walk_4: the arms' gait keys (trail mode)
GAIT_A = ((1, 'right'), (2, 'left'), (3, 'right'))           # tripod gait: these three move together...
GAIT_STRIDE, GAIT_LIFT = 7.0, 7.0                              # ...the other three half a cycle later


def make_walk(q):
    """Gait key q (0..3) of the six-arm walk, on the REST body (Java places the links on the trail and loops these
    keys for the arms): phase ph = q * 90 deg for tripod A, ph + 180 for tripod B.  ph 0: hand planted forward
    (contact), 90: planted under the shoulder (stance), 180: planted back (push-off), 270: in the air swinging forward,
    fingers dangling.  Planted hands sit exactly on the floor; the two stubby front legs trot in the same rhythm."""
    k = Kit()
    for (idx, side), spec in ARMS.items():
        sx = -1 if side == 'right' else 1
        ab, fb, jb, hb = arm_names(idx, side)
        ph = math.radians(q * 90.0 + (0.0 if (idx, side) in GAIT_A else 180.0))
        W0 = k.wpos(hb)
        fwd = k.R(spec['seg']) @ np.array([0.0, 0.0, -1.0])
        fwd[1] = 0.0
        fwd /= np.linalg.norm(fwd)
        W = W0 + fwd * (GAIT_STRIDE * math.cos(ph))
        up = GAIT_LIFT * max(0.0, -math.sin(ph))
        up = up if up > 0.01 else 0.0
        yaw = -spec['yaw'] * sx
        Hw = R_deg(0, yaw, 0) @ R_deg(38.0 * up / GAIT_LIFT, 0, 0)      # a lifted hand hangs limp from the wrist
        k.plant_arm(idx, side, (W[0], W[2]), (sx * 0.5, -1.0, 0.0), yaw, extra=Hw, lift=up)
        # a swinging hand clears the floor by ~4 texels even with its long fingers dangling
        extra_up = 0.0
        while up > 0.0 and k.lowest([hb]) > 24.0 - 4.0 * up / GAIT_LIFT and extra_up < 12.0:
            extra_up += 1.0
            k.plant_arm(idx, side, (W[0], W[2]), (sx * 0.5, -1.0, 0.0), yaw, extra=Hw, lift=up + extra_up)
    for side, sx in (('right', -1), ('left', 1)):
        ph = math.radians(q * 90.0 + (180.0 if side == 'right' else 0.0))
        lift = max(0.0, -math.sin(ph))
        k.set(f'front_{side}_leg', -12.0 * math.cos(ph) - 34.0 * lift)
        k.set(f'front_{side}_paw', 12.0 * math.cos(ph) + 30.0 * lift)
        k.unfloor(f'front_{side}_paw', 0, -4.0, 24.05)
    return k.table()                                           # (the tail wag is procedural: ANIM_NOTES)


# ------------------------------------------------------------------ lunge (ported)
def make_lunge():
    k = Kit()
    F = body_fk(rel={'link_2': (-6, 0, 0), 'link_3': (-2, 0, 0), 'link_4': (5, 0, 0), 'link_5': (4, 0, 0)},
                root_pos=(0, 2.5, 0))
    k.body(F)
    k.legacy_neck(F, neck_rel=(27, 0, 0), head_rel=(-14, 0, -HEAD_TILT), head_slide=(0, 0, -3))
    k.flower(76, 80, jitter=4.0, curl=10.0)
    k.brows(-22, 0.3)
    # the tongue lies along the floor of the maw and out over the lower-left petal (the maw stays clear)
    k.set('tongue', 0, 0, 0, 0, 4.0, 0.0)
    pd = k.R('jaw_lower_left') @ np.array([0.0, 0.0, -1.0])
    fwd = k.R('head') @ np.array([0.0, 0.0, -1.0])
    k.set_world_rot('tongue', look_rot(-(pd * 0.7 + fwd * 0.3), k.R('head') @ np.array([0.0, -1.0, 0.0])))
    k.set('tongue_tip', 30, 0, 0)
    k.set('right_ear_tip', 25)
    k.set('left_ear_tip', 25)
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
    k.hang_tag(30)
    return k.table()


# ------------------------------------------------------------------ coil (ported)
def make_coil():
    k = Kit()
    yaw = [('link_2', 40), ('link_3', 32), ('link_4', 40), ('link_5', 32), ('link_6', 40), ('link_7', 30)]
    rel = {n: (-4 if q % 2 else 3, a, 0) for q, (n, a) in enumerate(yaw)}
    F = body_fk(rel=rel, root_rot=(0, 30, 0))
    k.body(F)
    k.legacy_neck(F, neck_rel=(-30, -55, 0), head_rel=(55, -20, 8 - HEAD_TILT))
    k.flower(40, 44, jitter=4.0)
    k.brows(-16, 0.5)
    k.set('tail', 0, 40, 0)
    k.set('tail_tip', 0, 30, 0)
    k.set('tongue_tip', -10)
    k.plant_leg('right', -8)
    k.plant_leg('left', 8)
    piv = [k.wpos(n) for n in BODY]
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
            # outer arms brace on the floor, pushing away from the ring (far enough for the arm to reach)
            g = ARM_GEOM[(idx, side)]
            need = abs(g['L1'] - g['L2']) + 2.0
            for dist in np.arange(13.0, 40.0, 1.0):
                Wt = S - dirc * dist
                Wt[1] = 24.0 - hand_drop(spec)
                if np.linalg.norm(Wt - S) >= need:
                    break
            k.plant_arm(idx, side, (Wt[0], Wt[2]), (0.0, -1.0, 0.0), bang + 180 - 25)
    k.hang_ears(0)
    k.hang_tag()
    return k.table()


# ------------------------------------------------------------------ stretch (ported)
def make_stretch():
    """The transformation, w = 1 = compressed: every link telescopes into the one in front (only ~4 texels of
    each fur link still show), the compressed body slopes from the chest down to the rump sitting on the floor
    (a sitting dachshund), the neck telescopes in and the six arms are folded tight along the flanks."""
    k = Kit()
    vis = 4.0
    rel = {n: (-LINK[n][7], (3.0, -6.0)[min(q, 1)] * (-1) ** max(0, q - 1), (3.0, -6.0)[min(q, 1)] * (-1) ** max(0, q - 1))
           for q, (n, *_) in enumerate(LINKS)}                       # zig-zag yaw / roll: telescoped coats never coplanar
    slide = {n: ((0.4, -0.45, 0.25, -0.3, 0.5, -0.2)[q], 0, vis + 0.45 * q - LINK[n][2] - LINK[n][3])
             for q, (n, *_) in enumerate(LINKS)}
    lo, hi = -40.0, 0.0
    for _ in range(30):
        mid = (lo + hi) / 2
        rel['link_2'] = (-LINK['link_2'][7] + mid, 3.0, 3.0)
        k.body(body_fk(rel=rel, slide=slide))
        if k.lowest(['link_7']) > 23.6:
            lo = mid
        else:
            hi = mid
    F = body_fk(rel=rel, slide=slide)
    k.body(F)
    k.legacy_neck(F, head_slide=(0, 0, 7.0))
    k.set('tail', -30, 0, 0)
    for (idx, side), spec in ARMS.items():
        sx = -1 if side == 'right' else 1
        ab = arm_names(idx, side)[0]
        S = k.wpos(ab)
        fwd = k.R(spec['seg']) @ np.array([0.0, 0.0, 1.0])
        fwd[1] = 0
        fwd /= np.linalg.norm(fwd)
        g = ARM_GEOM[(idx, side)]
        W = S + np.array([sx * 9.0, 0.0, 0.0]) + fwd * (4.0 + idx * 2.0)
        W[1] = 24.0 - hand_drop(spec)
        if np.linalg.norm(W - S) < abs(g['L1'] - g['L2']) + 1.5:
            W = S + (W - S) / np.linalg.norm(W - S) * (abs(g['L1'] - g['L2']) + 1.5)
            W[1] = 24.0 - hand_drop(spec)
        yaw = math.degrees(math.atan2(-fwd[0], -fwd[2])) + 180 + sx * 20
        k.plant_arm(idx, side, (W[0], W[2]), (sx * 0.3, -1.0, 0.0), yaw)
    k.hang_ears(0)
    k.hang_tag()
    return k.table()


# ------------------------------------------------------------------ run
def make_run():
    """Full chase gallop: the chain low and long, snaking in an S behind the head, the neck thrust forward, ears
    streaming back, the tongue flapping out of the side of the mouth, the six arms caught mid-stride in a centipede
    wave (two hands in the air), one stubby front paw tucked up."""
    k = Kit()
    ang = {'link_1': (-4, -8), 'link_2': (5, 8), 'link_3': (6, 20), 'link_4': (-5, 10), 'link_5': (-10, -10),
           'link_6': (2, -20), 'link_7': (9, -8)}
    F = body_world((0.0, 5.5, -38.0), ang)
    k.body(F)
    k.neck_head(F, wdir(-14, -8), R_deg(0, -10, 0) @ R_deg(-4, 0, 0))
    k.flower(14, 20, jitter=3.0)
    k.brows(-14, 0.4)
    k.set('tongue', 12, 50, 0)                                 # flapping out of the side of the mouth...
    k.set('tongue_tip', 40, 0, 0)                              # ...the tip drooping, not a stick
    k.set('tail', -6, -26, 0)
    k.set('tail_tip', 6, -24, 0)
    k.plant_leg('left', 20)
    lb, pb = 'front_right_leg', 'front_right_paw'
    yaw = yaw_of(k.R('link_1'))
    k.set_world_rot(lb, R_deg(0, yaw, 0) @ R_deg(-55, 0, 0) @ R_deg(0, 0, -6))
    k.set_world_rot(pb, R_deg(0, yaw, 0) @ R_deg(50, 0, 0))
    phase = {(1, 'right'): 0, (1, 'left'): 180, (2, 'right'): 230, (2, 'left'): 50,
             (3, 'right'): 100, (3, 'left'): 280}
    gait(k, phase, stride=12.0, spread=17.0, lift=9.0)
    k.hang_ears(62)
    for eb in ('right_ear_tip', 'left_ear_tip'):
        k.add(eb, -24, 0, 0)                                   # the streaming leather droops at the tip
    k.hang_tag(55)
    return k.table()


# ------------------------------------------------------------------ fetch_drop
def make_fetch_drop():
    """'Te lo trae y te lo deja en los pies': a play bow.  The chest drops low on its forelegs (planted far forward),
    the rump stays up with the tail high and swept to one side (wagging), the neck reaches forward and down and the
    head hangs a hand above the floor, tilted, looking up at you from under puppy brows, the lower flaps just parted
    so the fetched item falls out at the player's feet (MOUTH point), the ears flopped on the floor."""
    k = Kit()
    ang = {'link_1': (14, 0), 'link_2': (20, 4), 'link_3': (12, 6), 'link_4': (2, 4), 'link_5': (-10, 0),
           'link_6': (-4, -4), 'link_7': (8, -6)}
    F = body_world((0.0, 9.5, -32.0), ang)
    k.body(F)
    k.neck_head(F, wdir(-2, 0), R_deg(0, 0, -16) @ R_deg(16, 0, 0))
    k.flower(2, 9, jitter=1.0)
    k.brows(16, -0.7)
    k.set('tongue', 24, 30, 0)                                 # out of the side, clear of the item in the teeth
    k.set('tongue_tip', 40, 0, 0)
    k.unfloor('tongue_tip', 0, -5.0)
    k.set('tail', -16, 34, 0)
    k.set('tail_tip', 10, 26, 0)
    k.plant_leg('right', -60, paw_yaw=8)
    k.plant_leg('left', -60, paw_yaw=-8)
    reach = {(1, 'right'): (-23, -8, 30), (1, 'left'): (22, -6, -24), (2, 'right'): (-24, 2, 10),
             (2, 'left'): (22, 6, -160), (3, 'right'): (-20, 8, 20), (3, 'left'): (21, 10, -20)}
    for (idx, side), (x, dz, yw) in reach.items():
        sx = -1 if side == 'right' else 1
        S = k.wpos(arm_names(idx, side)[0])
        k.plant_arm(idx, side, (x, S[2] + dz), (sx * 0.6, -1.0, 0.0), yw)
    k.hang_ears(0)
    k.hang_tag(-20)
    return k.table()


# ------------------------------------------------------------------ beg
def make_beg():
    """THE gag: 'pide sentado sobre los seis brazos'.  The rump sits on the floor, tail out behind it wagging, and the
    whole sausage body stands straight up out of it like a meerkat -- a 3.5-block begging tower -- with the chest on
    top, the stubby dachshund paws held up and bent at the wrist (the dachshund 'sit pretty'), the head tilted down
    at you with sad puppy brows.  The middle pair of human hands is pressed together 'por favor' in front of the
    chest; the lower two pairs are planted round the base like the legs of a stool: it is sitting on its arms."""
    k = Kit()
    ang = {'link_1': (-84, 0), 'link_2': (-87, 1.5), 'link_3': (-88, -1.5), 'link_4': (-84, 1.5), 'link_5': (-70, -1.0),
           'link_6': (-38, 0), 'link_7': (-2, 0)}
    F = body_world((0.0, -40.0, -14.0), ang)
    k.body(F)
    k.ground(['link_7', 'link_6'], 23.8)
    F = {n: (k.R(n), k.wpos(n)) for n in BODY}
    # the base: center the tower over the origin
    k.shift((0.0, 0.0, -float(F['link_5'][1][2]) - 6.0))
    F = {n: (k.R(n), k.wpos(n)) for n in BODY}
    # the neck stands up out of the chest so the head sits ON TOP of the tower, looking down at you with the dog
    # head tilt; nothing of the begging below it (paws, tag, praying hands) hides behind the skull
    k.neck_head(F, wdir(-86, 0), R_deg(0, 4, 0) @ R_deg(0, 0, 18) @ R_deg(-6, 0, 0), slide=6.0)
    k.flower(3, 8, jitter=1.0)
    k.brows(15, -0.7)
    k.set('tongue', 10, 34, 0)                                 # lolling out of the side of the mouth
    k.set('tongue_tip', 30, 10, 0)
    # stubby front paws held up high beside the name tag, folded down at the wrist: the dachshund 'sit pretty'
    for side, sx in (('right', -1), ('left', 1)):
        lb, pb = f'front_{side}_leg', f'front_{side}_paw'
        k.set_world_rot(lb, R_deg(0, -40 * sx, 0) @ R_deg(-128, 0, 0) @ R_deg(0, 0, 16 * sx))
        k.set_world_rot(pb, R_deg(0, -22 * sx, 0) @ R_deg(84, 0, 0))
    k.hang_tag(-32)                                          # resting on the bulge of the belly
    # pair 1: two human hands held out side by side under the tag, palms up and tipped toward you, cupped:
    # 'una monedita'.  Elbows jut out like a mantis (the forearms are far too long to fold any closer)
    tag_lo = k.lowest(['tag'])
    front = min(float(k.wpos('link_1', (0.0, 6.5, z))[2]) for z in (0.0, 7.0, 14.0))
    for side, sx in (('right', -1), ('left', 1)):
        W = np.array([sx * 5.5, tag_lo + 4.5, front - 9.0])
        k.arm(1, side, W, (sx * 1.0, -0.4, 0.3), bowl_rot(sx, lift=-24.0, cup=20.0, yaw=-8.0 * sx))
    # pairs 2 and 3: planted round the base, elbows out: it sits on its arms
    base = k.wpos('link_6')
    spots = {(2, 'right'): (-22, -14, 34), (2, 'left'): (22, -12, -150), (3, 'right'): (-24, 10, -20),
             (3, 'left'): (25, 14, 25)}
    for (idx, side), (x, dz, yw) in spots.items():
        sx = -1 if side == 'right' else 1
        k.plant_arm(idx, side, (x, base[2] + dz), (sx * 1.0, -0.8, 0.0), yw)
    k.set('tail', -40, 30, 0)
    k.set('tail_tip', 20, 20, 0)
    k.hang_ears(0)
    return k.table()


def bowl_rot(sx, lift=24.0, cup=16.0, yaw=0.0):
    """World rotation of a begging hand: palm up (rolled 180 about the fingers), fingers forward and tipped up by
    `lift`, its pinky edge raised by `cup` so the two hands held side by side make a bowl."""
    return R_deg(0, yaw, 0) @ R_deg(0, 0, cup * sx) @ R_deg(-lift, 0, 0) @ R_deg(0, 0, 180)


def prayer_rot(sx, tilt=0.0):
    """World rotation of a hand pressed palm-to-palm with its twin: fingers up, palm facing the midline."""
    Rp = np.array([[0.0, -sx, 0.0], [0.0, 0.0, 1.0], [-sx, 0.0, 0.0]])
    return R_deg(tilt, 0, 0) @ Rp


# ------------------------------------------------------------------ catch
def make_catch():
    """It catches the blessed choripan in the air: the chest rears up off its stubby forelegs, the neck goes straight
    up and the head points at the sky with the four flaps peeled wide open like a flower, the choripan (toggle) just
    dropping in between the needle teeth, the black tongue lolling out over the lower flaps, every hand braced for
    the jump, tail wagging."""
    k = Kit()
    ang = {'link_1': (-34, 0), 'link_2': (-14, 2), 'link_3': (4, 4), 'link_4': (-6, 2), 'link_5': (-12, 0),
           'link_6': (4, -2), 'link_7': (12, -4)}
    F = body_world((0.0, -2.0, -34.0), ang)
    k.body(F)
    # the head tipped back ~62 deg (not straight up): the open bloom faces the thrower at 3/4 from below
    k.neck_head(F, wdir(-62, 0), R_deg(0, 0, -6) @ R_deg(-62, 0, 0))
    k.flower(80, 84, jitter=3.0, curl=10.0)
    k.brows(12, -0.3)
    # the tongue lies along the floor of the maw and out over the lower-right petal, its tip curling off the end
    k.set('tongue', 0, 0, 0, 0, 4.0, 0.0)
    pd = k.R('jaw_lower_right') @ np.array([0.0, 0.0, -1.0])            # the petal's length, root -> tip
    fwd = k.R('head') @ np.array([0.0, 0.0, -1.0])
    k.set_world_rot('tongue', look_rot(-(pd * 0.75 + fwd * 0.25), k.R('head') @ np.array([0.0, -1.0, 0.0])))
    k.set('tongue_tip', 34, 0, 0)
    # the choripan clamped crosswise in the cup, between the rings of needles, its split top out of the mouth
    k.set('choripan', 90, 0, 7)
    # forelegs dangling forward off the ground (it jumped)
    for side, sx in (('right', -1), ('left', 1)):
        lb, pb = f'front_{side}_leg', f'front_{side}_paw'
        k.set_world_rot(lb, R_deg(0, 0, 10 * sx) @ R_deg(-40, 0, 0))
        k.set_world_rot(pb, R_deg(30, 0, 0))
    reach = {(1, 'right'): (-25, -12, 40), (1, 'left'): (23, -10, -24), (2, 'right'): (-26, 0, 14),
             (2, 'left'): (22, 4, -156), (3, 'right'): (-22, 10, 22), (3, 'left'): (23, 12, -22)}
    for (idx, side), (x, dz, yw) in reach.items():
        sx = -1 if side == 'right' else 1
        S = k.wpos(arm_names(idx, side)[0])
        k.plant_arm(idx, side, (x, S[2] + dz), (sx * 0.7, -1.0, 0.0), yw)
    k.set('tail', -10, 32, 0)
    k.set('tail_tip', 10, 26, 0)
    k.hang_ears(0)
    k.hang_tag(-14)                                          # swung forward off the reared chest
    return k.table()


# ------------------------------------------------------------------ vomit
def make_vomit():
    """Retching: the back arches up into a hump like a sick cat, every arm locks out stiff and wide, the neck juts
    forward and the head hangs nose-down with the four flaps peeled open toward the floor and the tongue hanging out,
    and the black column (toggle 'vomit') pours straight down out of the mouth into a splashing puddle."""
    global VOMIT_LEN
    k = Kit()
    ang = {'link_1': (8, 0), 'link_2': (24, 0), 'link_3': (14, 0), 'link_4': (-6, 0), 'link_5': (-22, 0),
           'link_6': (-12, 0), 'link_7': (6, 0)}
    F = body_world((0.0, 4.5, -32.0), ang)
    k.body(F)
    k.neck_head(F, wdir(-40, 0), R_deg(0, 0, 6) @ R_deg(44, 0, 0))
    k.flower(62, 66, jitter=4.0, curl=8.0)
    k.brows(14, -0.5)
    k.set('tongue', 30, 26, 0, 0, 4.0, 0.0)                    # along the floor of the maw, hanging out of one side
    k.set('tongue_tip', 20, 0, 0)
    k.unfloor('tongue_tip', 0, -6.0)
    k.set('tail', -26, 0, 0)
    k.set('tail_tip', -10, 0, 0)
    k.plant_leg('right', -14)
    k.plant_leg('left', -14)
    brace = {(1, 'right'): (-26, -8, 40), (1, 'left'): (24, -6, -30), (2, 'right'): (-27, 2, 20),
             (2, 'left'): (25, 4, -150), (3, 'right'): (-25, 8, -20), (3, 'left'): (26, 10, 25)}
    for (idx, side), (x, dz, yw) in brace.items():
        sx = -1 if side == 'right' else 1
        S = k.wpos(arm_names(idx, side)[0])
        k.plant_arm(idx, side, (x, S[2] + dz), (sx * 0.4, -1.0, 0.0), yw)
    # the column hangs plumb from inside the mouth; its length lands the puddle on the floor
    k.set_world_rot('vomit', R_deg(0, k.face_yaw(), 0))
    top = k.wpos('vomit')
    VOMIT_LEN = int(math.floor(24.0 - float(top[1])))
    # drop the column (< 1 texel, the gush stays inside the mouth) so the puddle lies exactly on the floor
    k.set_world_pos('vomit', top + np.array([0.0, 23.95 - (float(top[1]) + VOMIT_LEN), 0.0]))
    k.hang_ears(0)
    k.hang_tag(0)
    return k.table()


# ------------------------------------------------------------------ retract
def make_retract():
    """'Se enrolla como un metro': the tape measure snapping home.  Every link telescopes back into the one behind
    it toward the rump (only ~3 texels of fur per link still show), the compressed body sits low, the head is yanked
    back onto the chest (neck telescoped), ears flung forward by the whiplash, flaps snapped shut, brows shot up,
    tongue sucked in, the six arms folding in tight against the flanks with the elbows jutting above the back, tail
    straight up (boing)."""
    k = Kit()
    vis = 3.0
    slide = {n: LINK_LEN[p] - vis for n, p in zip(BODY[1:], BODY[:-1])}
    ang = {'link_1': (-10, 0), 'link_2': (-6, 2.5, 1.5), 'link_3': (-3, -2.0, -2.0), 'link_4': (0, 3.5, 2.5),
           'link_5': (2, -3.0, -1.5), 'link_6': (4.5, 1.5, 3.0), 'link_7': (4, -1.0, -2.5)}   # alternating yaw / roll:
    # the telescoped coats never share a plane
    F = body_world((0.0, 0.0, 0.0), ang, slide)
    # pin the rump where it is at rest (the housing of the tape measure) and sit it on the floor
    rest7 = body_fk()['link_7'][1]
    off = rest7 - F['link_7'][1]
    F = {n: (R, P + off) for n, (R, P) in F.items()}
    k.body(F)
    k.ground(BODY, 23.6)
    F = {n: (k.R(n), k.wpos(n)) for n in BODY}
    k.neck_head(F, wdir(-60, 0), R_deg(-16, 0, 0), slide=-7.0)
    k.flower(0, 0)
    k.brows(16, -0.3)                                          # shot up (rotation only: they stay on the ridge)
    k.set('tongue', -6, 13, 0, 0, 0, 12.0)
    k.set('tongue_tip', -62, 10, -18)
    k.set('tail', -48, 0, 0)
    k.set('tail_tip', -26, 0, 0)
    k.plant_leg('right', -10)
    k.plant_leg('left', -10)
    for (idx, side), spec in ARMS.items():
        sx = -1 if side == 'right' else 1
        ab = arm_names(idx, side)[0]
        S = k.wpos(ab)
        g = ARM_GEOM[(idx, side)]
        fwd = k.R(spec['seg']) @ np.array([0.0, 0.0, -1.0])
        fwd[1] = 0.0
        fwd /= np.linalg.norm(fwd)
        W = S + np.array([sx * 6.0, 0.0, 0.0]) + fwd * ((idx - 2) * 3.0 + sx * 1.5)
        W[1] = 24.0 - hand_drop(spec)
        need = abs(g['L1'] - g['L2']) + 1.0
        if np.linalg.norm(W - S) < need:
            W = S + (W - S) / np.linalg.norm(W - S) * need
            W[1] = 24.0 - hand_drop(spec)
        yaw = math.degrees(math.atan2(-fwd[0], -fwd[2])) + sx * (70 + idx * 6)
        # elbows up above the back but splayed outward, so the left and right arms never meet over the spine;
        # each hand a hair higher than the last (folded hands never share a plane)
        k.plant_arm(idx, side, (W[0], W[2]), (sx * 0.7, -1.0, 0.0), yaw, lift=0.3 * idx + (0.15 if sx > 0 else 0.0))
    k.hang_ears(-50, splay=18.0)                               # flung forward, but outside the jowls
    k.hang_tag(-35)
    return k.table()


# ------------------------------------------------------------------ unspool
DOOR_Z = 8.0                 # unspool: model z of the doghouse door plane (the cucha lies at z > DOOR_Z)
CUCHA_FLOOR = 21.6           # the doghouse's raised floor (y), 1.2 vanilla px above the ground
CUCHA_DEPTH = 25.6           # inside depth behind the door plane (texels)
INSIDE_STEP = 3.0            # trail rule 6: links still inside the cucha sit 3 texels apart along the door axis
FIRST_INSIDE = 'link_3'


def inside_frames(z_door, first=FIRST_INSIDE):
    """World frames of the links still inside the cucha (trail rule 6): telescoped INSIDE_STEP apart along +Z from the
    door plane, each sitting on the doghouse floor; the last one (the hips) tilted rear-up 25 deg so the rump clears
    the back wall; tiny alternating rolls so the nested coats never share a plane."""
    out = {}
    names = BODY[BODY.index(first):]
    for q, n in enumerate(names):
        W, Hh, infl = LINK[n][4], LINK[n][5], LINK[n][6]
        pitch = 25.0 if n == 'link_7' else (8.0 if n == 'link_6' else 0.0)
        R = wdir(pitch, (-1.5, 1.6, -2.4, 2.2, -0.8)[q % 5], (2.0, -2.2, 1.0, -1.2, 3.0)[q % 5])
        P = np.array([0.37 * q - 0.6,
                      CUCHA_FLOOR - Hh / 2.0 - infl - 0.3 - (0.0, 0.43, 0.71, 0.27, 0.58)[q % 5], z_door + INSIDE_STEP * q])
        out[n] = (R, P)
    return out


def make_unspool():
    """casa.cucha, the reveal: it never finishes coming out.  Only the head, the neck, the chest and one link are out
    of the doghouse: the chest has crawled out flat on its belly (stubby paws stretched forward), the first fur link
    wriggles over the threshold, the neck rises and the head looks up at you with the flower open.  Everything from
    link_3 back is still INSIDE the cucha, telescoped 3 texels apart along the door axis exactly as trail rule 6 keeps
    it (so blending into the chase never moves a link backwards), its arms folded flat, and the tail lies forward
    along the compressed body with its tip in the top of the doorway, wagging."""
    k = Kit()
    inside = inside_frames(DOOR_Z)
    P3 = inside[FIRST_INSIDE][1]
    # link_2 wriggles over the threshold (yawed one way, the chest the other: an S coming out of the door)
    R2 = wdir(-6.0, 26.0)
    P2 = P3 - R2 @ np.array([0.0, 0.0, LINK_LEN['link_2']])
    R1 = wdir(-1.0, -16.0, -4.0)
    chest_axis = 24.0 - 6.5 - 0.6                               # flat on its belly: the keel on the floor
    P2[1] = chest_axis + R1[1, 2] * 0.0
    P1 = P2 - R1 @ np.array([0.0, 0.0, LINK_LEN['link_1']])
    P1[1] = chest_axis
    F = {'link_1': (R1, P1), 'link_2': (look_rot(P3 - P2), P2)}
    F.update(inside)
    k.body(F)
    k.neck_head(F, wdir(-52, 10), R_deg(0, 6, 0) @ R_deg(0, 0, 12) @ R_deg(-14, 0, 0))
    k.flower(70, 74, jitter=4.0, curl=10.0)
    k.brows(-8, 0.25)
    # the tongue lies along the floor of the maw and out over the lower-left petal (the maw stays clear)
    k.set('tongue', 0, 0, 0, 0, 4.0, 0.0)
    pd = k.R('jaw_lower_left') @ np.array([0.0, 0.0, -1.0])
    fwd = k.R('head') @ np.array([0.0, 0.0, -1.0])
    k.set_world_rot('tongue', look_rot(-(pd * 0.7 + fwd * 0.3), k.R('head') @ np.array([0.0, -1.0, 0.0])))
    k.set('tongue_tip', 30, 0, 0)
    k.plant_leg('right', -80, paw_yaw=10)
    k.plant_leg('left', -80, paw_yaw=-10)
    # arms of the links still inside: folded flat, like a grasshopper's legs -- the upper arm pressed down the flank,
    # the forearm laid back along the floor beside the body, the hand palm-down at its end (trail rule 6: Java hides
    # the arms of a link while it is behind the door plane, so they never poke through the cucha's walls)
    for (idx, side), spec in ARMS.items():
        sx = -1 if side == 'right' else 1
        ab = arm_names(idx, side)[0]
        S = k.wpos(ab)
        g = ARM_GEOM[(idx, side)]
        L2 = k.l2eff[(idx, side)]
        W = S + np.array([sx * (3.5 + idx * 0.8), 0.0, 0.0])
        W[1] = CUCHA_FLOOR - hand_drop(spec) - 0.35 * idx
        reach = math.sqrt(max(1.0, (g['L1'] + L2 - 2.5) ** 2 - (W[1] - S[1]) ** 2 - 12.0)) * (1.0, 0.86, 0.72)[idx - 1]
        W[2] = S[2] + reach
        k.arm(idx, side, W, (sx * 0.5, 1.0, -0.4), R_deg(0, 180.0, 0))
    # the tail lies forward along the telescoped body, its tip curling up in the top of the doorway (wagging)
    tb = k.wpos('tail')
    tip_target = np.array([0.0, CUCHA_FLOOR - 15.0, DOOR_Z + 2.5])
    k.set_world_rot('tail', look_rot(tip_target - tb, np.array([0.0, -1.0, 0.0])))
    k.set('tail_tip', -34, 0, 0)
    k.hang_ears(0)
    k.hang_tag(-10)
    return k.table()


POSES = make_poses()


# ------------------------------------------------------------------ ANIM_NOTES (the Java contract; numbers computed)
def _posed_model(name=None):
    m = build()                                            # (no UV packing: only transforms are read)
    if name:
        for bn in m.bones():
            p = POSES[name].get(bn.name)
            if p:
                bn.rot = tuple(bn.rot[k] + math.degrees(p[k]) for k in range(3))
                bn.pivot = tuple(bn.pivot[k] + p[3 + k] for k in range(3))
    return m


def _wp(m, name, lp=(0.0, 0.0, 0.0)):
    bn = next(b for b in m.bones() if b.name == name)
    return (m.world_matrix(bn) @ np.array([*lp, 1.0]))[:3]


def _f(v, n=1):
    return ('%.*f' % (n, v)).replace('-0.0', '0.0') if abs(v) >= 0.05 or n > 1 else '0'


def _chain_table():
    m = _posed_model()
    B = {b.name: b for b in m.bones()}
    rows, prev, arc = [], None, 0.0
    what = {'link_0': 'head + stretched neck (pivot = head joint under the back of the skull)',
            'link_1': 'chest in the sweater remnant + the two stubby dachshund front legs',
            'link_2': 'fur link 1 (skin band in front of it, sweater shred_1)',
            'link_3': 'fur link 2 + arm pair 1 (broken rib spike on its band)',
            'link_4': 'fur link 3 (crest of the hunch)',
            'link_5': 'fur link 4 + arm pair 2 (rib spike)',
            'link_6': 'fur link 5',
            'link_7': 'hips / rump + arm pair 3 + the wagging tail'}
    for n in CHAIN:
        P = m.world_matrix(B[n])[:3, 3]
        d = 0.0 if prev is None else math.hypot(P[0] - prev[0], P[2] - prev[2])
        arc += d
        r = B[n].rot
        ln = NECK_LEN if n == 'link_0' else LINK_LEN[n]
        rows.append(f'  {n:7s} pivot ({_f(P[0])}, {_f(P[1])}, {_f(P[2])})   java offset ({_f(P[0])}F, {_f(P[1] - 24)}F, '
                    f'{_f(P[2])}F)   rest rot deg ({_f(r[0])}, {_f(r[1])}, {_f(r[2])})\n'
                    f'          length {ln:g}, spacing {_f(d)}, arc {_f(arc)} -- {what[n]}')
        prev = P
    return '\n'.join(rows)


def _rest_arcs():
    """Horizontal running arc of every chain pivot from the head joint at rest (the trail spacing, rule 3)."""
    m = _posed_model()
    out, prev, arc = {}, None, 0.0
    for n in CHAIN:
        P = _wp(m, n)
        if prev is not None:
            arc += math.hypot(P[0] - prev[0], P[2] - prev[2])
        out[n] = arc
        prev = P
    return out


TRAIL_HEAD_Z = 10.0          # trail rule 2: link_0 sits 10 texels behind the entity origin


def _pose_anchors():
    """POSE_ANCHOR = {pose: (anchor, (tx, ty, tz))}: before blending a pose in, Java translates the whole posed model
    (every top-level bone link_0..link_7) by T so that its anchor lands where the trail has it.  The values here are
    for a STRAIGHT trail (anchor at (0, *, TRAIL_HEAD_Z + arc)); on a curved trail use T = trailPivot(anchor) -
    posedPivot(anchor) (x and z only; y is never translated: every pose is authored standing on y = 24).  'door':
    the pose is authored with the doghouse door plane at model z = DOOR_Z: spawn the entity there (T = 0)."""
    arcs = _rest_arcs()
    out = {}
    for name in POSES:
        if name.startswith('walk'):
            continue
        if name == 'unspool':
            out[name] = ('door', (0.0, 0.0, 0.0))
            continue
        bone = 'link_7' if name in ('retract', 'stretch') else 'link_0'
        P = _wp(_posed_model(name), bone)
        out[name] = (bone, (round(-float(P[0]), 2), 0.0, round(TRAIL_HEAD_Z + arcs[bone] - float(P[2]), 2)))
    return out


POSE_ANCHOR = _pose_anchors()


def _landmarks():
    out = {}
    for name in [p for p in POSES if not p.startswith('walk')]:
        m = _posed_model(name)
        T = np.array(POSE_ANCHOR[name][1])
        zs = [float(_wp(m, b.name, (c.origin[0] + c.size[0] * i, c.origin[1] + c.size[1] * j,
                                     c.origin[2] + c.size[2] * q))[2])
              for b in m.bones() if b.name not in TOGGLE_DEFAULT for c in b.cubes
              for i in (0, 1) for j in (0, 1) for q in (0, 1)]
        out[name] = {'head': _wp(m, 'head'), 'mouth': _wp(m, 'mouth_item'), 'cup': _wp(m, 'choripan'),
                     'link_7': _wp(m, 'link_7'), 'T': T,
                     'top': min(float(_wp(m, b.name, c.origin)[1]) for b in m.bones() for c in b.cubes
                                if b.name not in TOGGLE_DEFAULT),
                     'center': np.mean([_wp(m, n) for n in BODY], axis=0), 'zmin': min(zs), 'zmax': max(zs)}
        if name == 'unspool':
            out[name]['inside'] = {n: _wp(m, n) for n in BODY[BODY.index(FIRST_INSIDE):]}
            out[name]['link_2'] = _wp(m, 'link_2')
    return out


def _v(p):
    return '(%s, %s, %s)' % (_f(p[0]), _f(p[1]), _f(p[2]))


def _anchor_table():
    rows = []
    for name, (bone, T) in POSE_ANCHOR.items():
        rows.append(f'          {name:10s} anchor {bone:6s}  T = ({_f(T[0], 2)}, 0, {_f(T[2], 2)})')
    return '\n'.join(rows)


def _flap_table(pose):
    t = POSES[pose]
    return '; '.join(f'{n} ({t[n][0]:.3f}, {t[n][1]:.3f}, {t[n][2]:.3f})' for n in FLAPS.values() if n in t)


def _anim_notes():
    m = _posed_model()
    nb = sum(1 for _ in m.bones())
    nc = sum(len(b.cubes) for b in m.bones())
    L = _landmarks()
    arcs = _rest_arcs()
    beg_top = (24.0 - float(L['beg']['top'])) / 32.0
    U = L['unspool']
    head_out = DOOR_Z - float(U['head'][2])
    ins = ', '.join(f"{n} z {_f(float(P[2]) - DOOR_Z)}" for n, P in U['inside'].items())
    cup = L['catch']['cup'] + L['catch']['T']
    return f"""Choripan, version completa (ChoripanEntity, form BEAST) -- animation contract.
{nb} bones, {nc} cubes, texture {m.tex_w}x{m.tex_h} (choripan_demonio.png), scale 0.5, RenderTypes::entityCutoutNoCull.
Units: radians for POSES and for every value quoted 'rad'; 'deg' values are degrees; offsets (dx, dy, dz) in model \
texels at 2x density (inside scale_root: 2 texels = 1 vanilla pixel, 32 texels = 1 block), in the PARENT bone's space \
(top-level bones: model space, +Y down, ground y = 24, the creature faces -Z, its right side is -X).  Every POSES value \
is ADDED to the rest pose.  t = ageInTicks.  One look only (no VARIANT_MATS): the DOG form is the separate model \
`choripan`.  Emissive layer 'eyes' (choripan_demonio_eyes.png): the red rims of the two black pinprick pupils (+ one wet glint each), \
the ember clusters, the deep red core and the dim crown rim of the vomit column and the holy-water sparkles on the \
blessed choripan; a hidden toggle bone must not draw its glow either (render the eyes pass through the same model with \
the same visibility).
Its rule: "Sigue siendo un perro" -- every scare ends in a dog behaviour (wag, fetch, beg, catch).  The TAIL NEVER \
STOPS WAGGING, in every pose and state, even while the rest of the body is frozen or still inside the doghouse.

======================================================================================================== THE CHAIN
The body is a chain of top-level bones link_0 (head) .. link_7 (hips) (rest values in Java: part.getInitialPose()).  Each has its own pivot at its FRONT joint \
and its own rest rotation; its body runs from the pivot toward +Z (the tail) for `length` texels, where the next link's \
pivot sits at rest (link_0: the neck runs back from the head joint to the chest socket, see neck).  Skin bands overlap \
3 texels into the link in front, so neighbours may bend up to ~35 deg (yaw) / ~25 deg (pitch) against each other \
without opening a gap.  Rest layout (authored model space; 'java offset' = the PartPose offset under scale_root, \
y - 24; 'spacing' = horizontal distance from the previous pivot; 'arc' = running sum from the head joint):
{_chain_table()}

TRAIL MODE (BEAST chasing, walking, fetching; the server hitbox 0.8 x 0.8 is the HEAD only):
 1. Client, per entity: a ring buffer of the head's interpolated world positions, one sample every 1/8 block moved
    (plus one per tick while standing), at least 6 blocks of history; prepend the current lerped position each frame.
 2. link_0 sits on the entity: pivot (0, rest y, +{TRAIL_HEAD_Z:g}) -- {TRAIL_HEAD_Z:g} texels behind the origin, so skull + muzzle are centred on
    the hitbox -- yRot 0 (the renderer's body yaw = the head's heading; netHeadYaw / headPitch go to `head`).
 3. link_k (k = 1..7): walk back along the history from the current position by s_k = {TRAIL_HEAD_Z:g} + arc_k texels (/32 ->
    blocks) to the point Q_k.  Convert to model space with the entity's yaw b: d = Q_k - E (blocks), forward
    f = (-sin b, 0, cos b), right r = (-cos b, 0, -sin b); x = -32 * (d . r), z = -32 * (d . f),
    y = rest_y_k - 32 * d.y.  Set link_k.x/y/z (java: y - 24).
 4. Heading: v = (pivot of link_k+1) - (pivot of link_k) in model space (for link_7 use link_6 -> link_7);
    link_k.yRot = atan2(v.x, v.z); link_k.xRot = atan2(-v.y, hypot(v.x, v.z)) (this reproduces the rest hunch on a
    straight flat trail); link_k.zRot = rest zRot (only link_1 has one: the chest leans 5 deg onto its right shoulder).
    Clamp each link's yaw to +-35 deg of the link in front (sharp corners are cut, never folded).
 5. neck (child of link_0): aim it at the chest socket = link_1 pivot + R(link_1) * (0, -2, 0): with v that vector in
    link_0 space, neck.yRot = atan2(v.x, v.z), neck.xRot = atan2(-v.y, hypot(v.x, v.z)), zRot rest.  The neck tube is
    16 texels long (2 in front of the head joint, socket at 11): never let |v| exceed 13 or a gap shows.
 6. Not enough history yet (just spawned, or coming out of the doghouse): seed / continue the path in a straight
    line back to the trailAnchor (the doghouse door, marker `cucha` facing) and on INTO the doghouse along the door
    axis.  A link whose s_k lies past the door plane is INSIDE: every inside link sits {INSIDE_STEP:g} texels behind the one in
    front of it along the door axis (the first inside link exactly on the door plane), on the doghouse floor (y =
    {CUCHA_FLOOR:g} - half the link's height), yaw 0 against the door axis; link_6 tilted 8 deg and link_7 25 deg rear-up
    so the rump clears the back wall ({CUCHA_DEPTH:g} texels deep); alternate +-2 deg roll / +-1.5 deg yaw between
    neighbours (the nested coats never share a plane).  The ARMS of an inside link are hidden (ModelPart.visible =
    false on arm_* / forearm_* / joint_* / hand_* of that link: 30-38-texel forearms do not fit in a 25-texel
    cucha) and keep the 'unspool' folded values; the frame a link crosses the door plane, show them and blend them
    to the gait in 6 ticks.  The body never finishes coming out while the head is already chasing you, and the tail
    (link_7, at the 'cucha_cola' marker) keeps wagging inside.  Every 0.4 block the head gains, the next link pops out
    of the door (choripan.crack).
 7. Arms and front legs are children of their links: in trail mode loop the gait keys walk_1 -> walk_2 -> walk_3 ->
    walk_4 -> walk_1 (they only hold arm and front-leg entries), p = walkAnimation.position * 0.55 (one key per
    0.5 block at full speed), key = floor(p) mod 4, smoothstep(fract(p)) between consecutive keys.  Head, neck,
    flaps, ears, tongue and brows take the 'run' values (weight 1 while chasing, 0.4 while walking).
 8. Culling: setNoCulling-style -- extend the render bounding box to cover the whole history used (s_7 + 1 block)
    plus 1.2 blocks sideways for the arms, or the chain pops out of view at corners.
 9. Poses and trail mix: every pose table is authored on the REST skeleton (its own frame, head joint near z -43).
    Before blending a pose in, translate the posed model by its anchor vector T (POSE_ANCHOR below): add T.x / T.z
    to the pose offsets of all eight top-level bones link_0..link_7 (children follow), never T.y.  Then lerp every
    link from its trail transform to rest + pose + T over 6 ticks (8 for retract); when the pose ends, lerp back to
    the trail.  Anchors: the poses that play while you can hit it (run, fetch_drop, lunge, beg, catch, vomit, coil)
    keep the HEAD JOINT where the trail has it, so nothing slides off the head hitbox; retract and stretch keep the
    HIPS (link_7) where the trail has them (the body compresses toward the rump, the swap to the DOG happens there);
    unspool is authored on the door (spawn rule below).  Straight-trail values (curved trail: T = trailPivot(anchor) -
    posedPivot(anchor), x / z only):
{_anchor_table()}
 10. The SERVER HITBOX never follows a pose: with these anchors the posed head stays inside the 0.8 x 0.8 column
    in x / z, so crucifix and holy-water hits, salt blocking, the catch timing and the lunge contact are computed on the
    visible head.  Heights differ: the head joint is {_f((24 - float(L['fetch_drop']['head'][1])) / 32, 2)} block up in fetch_drop, {_f((24 - float(L['lunge']['head'][1])) / 32, 2)} in lunge,
    {_f((24 - float(L['catch']['head'][1])) / 32, 2)} in catch, {_f((24 - float(L['vomit']['head'][1])) / 32, 2)} in vomit and {_f((24 - float(L['beg']['head'][1])) / 32, 2)} in beg: while BegGoal / CatchBlessedGoal run, refreshDimensions()
    to 0.8 x {_f(beg_top + 0.2, 1)} so the raised head is still hittable; retract and stretch are uninterruptible (no hits).

======================================================================================================== BONES
link_0 .. link_7 -- the chain above.  Breathing on the fur links: scale nothing; dy = sin(t * 0.12 + k * 0.7) * 0.4
  on link_2..link_7 (a slow peristaltic ripple running toward the tail).  Footfalls: link_3 / link_5 / link_7 dip
  +0.6 dy when their arm pair plants.
neck (child of link_0, pivot = head joint): the stretched see-through neck with two trachea rings, the celeste collar
  around it.  Rest rot (-35, 0, -2) deg relative to link_0: it climbs back down to the chest socket.  Trail rule 5.
  Idle: xRot += sin(t * 0.08) * 0.03.
tag (child of neck, pivot = the collar ring): the brass 'CHORIPAN' name tag ({TAG_W} x {TAG_H}, aged brass, rounded and notched
  corners, the name engraved in two lines with the accent over the A); it must stay readable.  Physics: it hangs
  plumb, facing where the face faces -- every frame give it the world rotation yRot(face heading) only (tag local
  rotation = inverse(neck world rotation) * that; hang_tag() in this file is the reference), then add a damped
  pendulum xRot / zRot kicked by the neck's angular velocity (k 0.6, damping 0.9 per tick, clamp +-0.6).  Poses carry
  the frozen value of that plumb hang plus the swing each pose names.
head (child of link_0, pivot = head joint): FOCUS bone.  The dachshund face kept: the bloodshot, yellowed almond eyes (black pinprick pupils in a red rim) RECESSED
  one texel deep in sockets (brow ridge, blaze, temples, cheek band), brown upper lids over the top two rows, a warm
  wet lower lid, tiny red pin pupils (emissive) looking slightly inward; tan jowls; THE dog nose (8 x 3 + a 6 x 1
  leather bulb with the 2-texel wet highlight) split down a red seam across the two upper flaps; under the eyes the
  MAW: a {_f(HOLE[1] - HOLE[0])} x {_f(HOLE[3] - HOLE[2])} hole between the jowls, {_f(THROAT_Z - FACE_Z)} texels deep, gum walls darkening to a black throat, two rings of
  needle teeth inside it.  Rest: level with a dog head tilt (zRot 8 deg).  Look at the player: yaw clamp +-0.7, pitch
  -0.5..0.6, fast (0.15 rad/tick) -- it locks on.  The DOG tilt: every 3-6 s while idle / watching, zRot +-0.35 in 4
  ticks, hold 20 ticks, back (the curious-dog head tilt is the creepiest thing it does).
right_brow / left_brow (children of head, pivot on the top-front edge of the brow ridge): chunky tan brows, inner
  ends raised at rest (puppy eyes).  zRot (right +, left -) up to +0.3 = sad / pleading (beg, fetch_drop, catch),
  down to -0.4 = furious (lunge, run, coil); dy only between -0.3 (lifted) and +0.6 (pressed onto the lids) or the brow
  leaves the ridge.  Snap in 3 ticks.
jaw_upper_right / jaw_upper_left / jaw_lower_right / jaw_lower_left (children of head): THE FLOWER.  The tan muzzle is
  four flaps (6 x 4 x 12 upper, 5 x 4 x 11 lower), each lined with uneven needle teeth (two rows along its mouth edge
  + a row of fangs across its tip, 2-3 long fangs per row), red gums, raw cut faces; the nose halves ride the upper
  pair.  Each flap is hinged at the OUTER BACK CORNER of its quarter of the muzzle, at the corner of the maw (pivots,
  head-local: upper ({_f(FLAP_HINGE[('upper', -1)][0])}/+{_f(FLAP_HINGE[('upper', 1)][0])}, {_f(FLAP_HINGE[('upper', 1)][1])}, {_f(FLAP_HINGE[('upper', 1)][2])}), lower ({_f(FLAP_HINGE[('lower', -1)][0])}/+{_f(FLAP_HINGE[('lower', 1)][0])}, {_f(FLAP_HINGE[('lower', 1)][1])}, {_f(FLAP_HINGE[('lower', 1)][2])}); rest rotation 0 =
  closed).  Opening turns each flap about the tangent axis through its hinge, so the tips peel RADIALLY outward round
  the open hole: upper pair toward NW / NE ({FLOWER_ELEV[0]:g} deg above horizontal), lower pair toward SW / SE ({FLOWER_ELEV[1]:g} deg below);
  they never cross the centre line, the throat stays in view.  The pose values are the Euler triples of those
  rotations: animate the flower by lerping each flap's (xRot, yRot, zRot) from 0 to the target pose's values.  "Se
  abre en flor": open from closed to the 'lunge' values in 5 ticks with an overshoot of 15 % and a 2-tick settle, the
  four flaps 1 tick apart (upper right, lower left, upper left, lower right) -- never all together.  lunge (rad):
  {_flap_table('lunge')}.  Idle in BEAST: they breathe open to 8 % of those values
  (sin(t * 0.2)) and quiver (+-0.03 random each tick).  Chomp (catch -> chewing): close fully and reopen to 50 % 3 times,
  5 ticks each.
tongue / tongue_tip (tongue child of head, pivot head-local {_v(TONGUE_ROOT)} in the maw at the mouth line; tongue_tip at
  its end): the long black tongue (a wet mid-value stripe down the middle, rounded tapering tip).  Rest: lolling out
  of the LEFT side of the mouth like a panting dog (rest yRot {TONGUE_YAW:g} deg; keeps the name tag clear from the
  front), the tip curling down.  With the flower open it lies on the FLOOR of the maw (dy +4) and hangs out over a
  lower petal (lunge, unspool, catch, vomit) -- never across the hole.  Chase: flapping, tongue.yRot += sin(t * 0.7) *
  0.3, tongue_tip.xRot += sin(t * 0.7 - 1) * 0.4 on top of the drooping 'run' curl.  Retract: tongue dz +12 (sucked
  back in).
right_ear / left_ear + right_ear_tip / left_ear_tip (children of head): long limp ears, almost to the ground, a lighter
  leather edge.  They hang plumb: every frame give each ear the world rotation yRot(face heading) * EAR_WORLD
  (EAR_WORLD = (4, -+22, -+6) deg, right / left: the leather turned to the front), i.e. cancel the head's pitch and
  tilt (hang_ears() in this file is the reference), plus a pendulum with 3-4 ticks of lag and 1.5x amplitude on the
  tip.  Running: swing back 0.9 rad (streaming) with the tip drooping (-0.4 xRot).  Flung forward (retract): splay
  them out 0.3 rad so they pass outside the jowls.  Never let them pass through the floor: when the head is low
  (fetch_drop, vomit) fold the tip forward along the ground (the pose values do that).
vomit (child of head, pivot in the maw; TOGGLE, hidden by default): the black bile column, {VOMIT_LEN} texels from the
  throat to the floor -- a gush in the mouth with a deep red glowing core, the stream (falling streaks, a cool violet
  wet sheen down both sides, clusters of red embers on the 'eyes' layer) and a splashing puddle with a dimly glowing
  crown rim and a crown of drops (it reads at night).  Its length is solved for the 'vomit' pose (the puddle lies
  exactly on the floor there); only show it in that pose.  Pulse: xScale = zScale = 1 + sin(t * 1.3) * 0.08 on the
  stream; the puddle grows from scale 0.3 to 1 over the first 10 ticks.
mouth_item (child of head, no cubes; head-local {_v(MOUTH)}): locator between the front teeth.  Render the fetched
  ItemStack there (ItemDisplayContext.GROUND, scaled x2 to undo the model's 0.5, rotated 90 deg about Y so it lies
  across the jaws); at the end of 'fetch_drop' spawn / release the ItemEntity at this point's world position (it falls
  0.3 block onto the player's feet).
choripan (child of head, head-local {_v(CUP)} = in the cup of the open flower, between the rings of needles; TOGGLE,
  hidden by default): the blessed choripan -- pan de campo split open, the grilled chorizo poking out of both ends,
  chimichurri, holy-water sparkles (emissive).  Shown only from the catch frame until the 3rd chomp.
front_right_leg / front_left_leg + front_right_paw / front_left_paw (children of link_1): the two short, bowed, normal
  dachshund front legs and their cute paws -- the only dog legs left.  Rest: planted, paws turned out.  They trot in
  the gait keys; in 'beg' they are held up high beside the tag, folded down at the wrist; in 'catch' they dangle (it
  jumped).
shred_1, shred_2, shred_3, shred_4 (children of link_2, link_3, link_4, link_5; pivot on the spine): strips of the Nona's red sweater hanging off the
  back (a band + two strips, loose yarn ends).  Secondary only: zRot = sin(t * 0.15 + k) * 0.06; chase: +0.25 xRot
  (blown back); never driven by poses.
tail / tail_tip (children of link_7): the big dachshund tail carried high, tan tip.  ALWAYS WAGGING, added on top of
  every pose, trail and freeze: tail.yRot += sin(t * 1.1) * 0.55, tail_tip.yRot += sin(t * 1.1 - 0.9) * 0.45; faster
  and wider when it 'is a good dog' (fetch_drop, beg, catch: t * 1.6, amplitude 0.75); slower while unspooling
  inside the doghouse (t * 0.7) -- that is the gag of the reveal.
arm_1_right / arm_1_left (on link_3), arm_2_right / arm_2_left (on link_5), arm_3_right / arm_3_left (on link_7):
  three pairs of far-too-long, NOT symmetric human arms bursting out of the flanks (torn fur collar, raw base) --
  pallid dead skin, lit on top, livid underneath, bruised only at the joints.  Upper arms 5 x 5 with a lean deltoid
  bulge, spider elbows above the spine.  forearm_1_right, forearm_1_left, forearm_2_right, forearm_2_left,
  forearm_3_right, forearm_3_left (children of the upper arms, pivot at the elbow): a bony elbow knob, a 4 x 4 forearm
  tapering into a 3 x 3 wrist, crease rings under the elbow and at the wrist, a knobbly wrist bone.  joint_2_left
  (child of forearm_2_left): the extra joint of the broken arm 2-left (a second elbow; its wrist is broken backwards).
  hand_1_right, hand_1_left, hand_2_right, hand_2_left, hand_3_right, hand_3_left (children of the forearms / of
  joint_2_left, pivot at the wrist): filthy hands, cracked black nails -- hand_1_right flat, hand_1_left on its
  knuckles (fist), hand_2_right clawing on its fingertips, hand_2_left twisted backwards, hand_3_right flat,
  hand_3_left clawing.  Animated only by POSES (all arm values are IK-solved so planted hands sit exactly on the
  floor): gait keys in trail mode, the pose tables otherwise.  Idle: finger twitch = one random hand xRot -0.15 for 3
  ticks every 1-3 s.

======================================================================================================== TOGGLES
ModelPart.visible.  Default (TOGGLE_DEFAULT): vomit = false, choripan = false.  Hiding a bone hides its children and \
its glow.
* vomit -- visible only during the 'vomit' pose (casa.parrilla, after the catch).  Show it on the first frame the
  pose reaches weight 1; hide it when the wisp (DemonWisp) leaves the mouth, before 'retract'.
* choripan -- visible only in 'catch': show it on the frame the thrown ChoripanBenditoEntity reaches the mouth
  (discard that entity the same tick), keep it through the 3 chomps, hide it on the last one (swallowed).
* the arms of links still inside the cucha (trail rule 6) are hidden the same way until their link crosses the door.
* mouth_item is not a toggle: it has no cubes; Java draws the fetched ItemStack there only while it carries one.

======================================================================================================== POSES
(all tables are IK-solved snapshots on the rest skeleton; the arms' planted hands touch y = 24 exactly; translate
by POSE_ANCHOR before blending, trail rule 9)
* unspool -- casa.cucha, the reveal, [CLIP][JUMPSCARE] and the thumbnail: it never finishes coming out.  Only the
  head, the neck, the chest and link_2 are out of the doghouse: the chest has crawled out flat on its belly (stubby
  paws stretched forward), link_2 wriggles over the threshold, the neck rises and the head looks up at you with the
  flower open (the maw clear, the tongue on its floor).  Authored on the door: the door plane is model z = {_f(DOOR_Z)}
  ({_f(DOOR_Z / 32, 2)} block behind the entity origin), the head joint is {_f(head_out / 32, 2)} block out in front of it, link_2's pivot
  {_f((DOOR_Z - float(U['link_2'][2])) / 32, 2)} block.  link_3 .. link_7 are INSIDE, exactly as trail rule 6 keeps them ({ins}, relative to
  the door), their arms folded flat and hidden, the tail lying forward along the telescoped body with its tip
  wagging in the top of the doorway.  Spawn: put the BEAST {_f(DOOR_Z / 32, 2)} block in front of the cucha's door plane
  (the `cucha` marker's facing), facing away from it (T = 0).  Hold 20 ticks (choripan.crack x6, one per link, 3
  ticks apart: kick each link_k +0.15 xRot for 2 ticks), open the flower (5 ticks), then start the chase: blend (8
  ticks) into trail mode seeded straight back to the door -- the inside links already sit where rule 6 wants them,
  so nothing moves backwards; each link pops out (and shows its arms) as the head gains distance.
* run -- the chase body attitude: the chain low and long, snaking in an S behind the head, the neck thrust forward,
  ears streaming back with the tips drooping, the tongue flapping out of the side with its tip curled down, the
  flower just parted (the four quarters of the muzzle split), furious brows, the six arms caught mid-stride in a
  centipede wave (two hands in the air), one stubby front paw tucked up.  In trail mode use only its head / neck /
  flaps / brows / tongue / ears / tag values (the chain comes from the trail, the arms from walk_*); use the whole
  table when chasing without a trail (debug, or a cut where the body must stay in frame).
* walk_1 .. walk_4 -- the gait keys (arms + front legs only, on the rest chain; no anchor): a tripod gait, tripod A =
  hand_1_right, hand_2_left, hand_3_right, tripod B = the other three, half a cycle apart.  walk_1: A planted
  forward / B planted back; walk_2: A under the shoulders / B in the air swinging forward, fingers dangling; walk_3: A
  back / B forward; walk_4: A in the air / B under the shoulders.  Loop 1-2-3-4-1 (trail rule 7); the front legs trot
  in the same rhythm.
* fetch_drop -- casa.trae, 'te lo trae y te lo deja en los pies': a play bow.  The chest drops low on its forelegs,
  the rump stays up with the tail high and swept to one side (WAGGING FAST), the neck reaches forward and down, the
  head hangs a hand above the floor, tilted, looking up at you from under sad puppy brows, the muzzle just parted,
  the tongue out of the side with its tip curled; mouth_item at {_v(L['fetch_drop']['mouth'] + L['fetch_drop']['T'])} after the anchor =
  {_f((24 - float(L['fetch_drop']['mouth'][1])) / 32, 2)} block above the floor, {_f(-float(L['fetch_drop']['mouth'][2] + L['fetch_drop']['T'][2]) / 32, 2)} block in front of the origin: stop the entity so that
  point is over the player's feet.  Play: blend in 8 ticks carrying the item, release it on tick 10, then hold 60
  ticks of silence (only the tail and the eye glow move; no breathing), then LUNGE.  Also the base for
  SaltBlockedGoal (whining against the salt line: hold it with the flower closed (flaps 0), the head pushing forward
  2 texels and back every 10 ticks, brows sad).
* beg -- casa.parrilla, 'pide sentado sobre los seis brazos' (BegGoal: the player holds a chorizo / choripan).  The
  rump sits on the floor, the tail out behind it wagging, the whole sausage body stands straight up out of it like a
  meerkat -- a {beg_top:.1f}-block begging tower -- the chest on top with the stubby paws held up high beside the readable name
  tag and folded down at the wrist, the head on top tilted at you with sad puppy brows and the tongue lolling out of
  the side; arm pair 1 reaches all the way up and holds out two human hands side by side just under the tag, 4
  texels apart, palms up and tipped toward you, cupped ('una monedita'), elbows jutting out like a mantis; pairs 2 and
  3 are planted round the base like the legs of a stool.  Anchored on the head (the tower stands under the hitbox).
  Blend in over 14 ticks (it unfolds upward), then idle: the tower sways zRot sin(t * 0.1) * 0.03 on link_1..link_4,
  the cupped hands bob dy sin(t * 0.3) * 0.6, the head tilts.
* lunge -- LungeGoal / the attack and the JUMPSCARE PORTRAIT: the chain bunches and the head drops low with the
  flower fully open round the black maw (these are the flower values), the tongue lying on the floor of the maw and
  hanging out over the lower-left petal, furious brows, the ears flung, every hand gripping the floor.  Blend in 3
  ticks, hold 4, hit: Fx.jumpscare(p, "choripan_demonio") (4 damage) -- the open flower fills the camera
  until the crucifix is raised.
* catch -- casa.parrilla, CatchBlessedGoal: it catches the blessed choripan in the air.  The chest rears up off its
  stubby forelegs (paws dangling: it jumped), the neck goes up and the head tips back ~62 deg -- JAWS POINTING UP but
  the open bloom still facing the thrower at 3/4 from below -- the four flaps peeled wide round the maw, the choripan
  toggle clamped crosswise in the cup between the needles (its centre at {_v(cup)} after the anchor, =
  {_f((24 - float(cup[1])) / 32, 2)} block up: aim the throw there), the tongue draped down over the lower-right petal, every hand
  braced, tail wagging.  Blend in 4 ticks timed so weight 1 lands on the frame the thrown item reaches the mouth (FOV
  punch), hold 6, then 3 chomps (flaps), then freeze 30 ticks (it realises: brows snap to sad, eyes keep glowing),
  then 'vomit'.
* vomit -- the bile: the back arches up into a hump like a sick cat, every arm locks out stiff and wide, the neck juts
  forward, the head hangs nose-down with the four flaps peeled open toward the floor and the tongue out of one side,
  and the black column (toggle vomit) pours straight down out of the maw into the puddle.  Blend in 8 ticks (retch:
  link_2 .. link_5 xRot pulses +0.12 at 6-tick intervals, 3 times), show the toggle, 40 ticks of pouring while the
  DemonWisp rises out of the column, hide it, then 'retract'.
* retract -- 'se enrolla como un metro': the tape measure snapping home.  Every link telescopes back into the one
  behind it toward the rump (~3 texels of fur per link still show), the compressed body sits low around the hips
  (anchored on link_7: the rump stays where the trail had it), the head yanked back onto the chest (neck telescoped),
  ears flung forward by the whiplash (splayed outside the jowls), the flower snapped shut, brows shot up (rotation
  only), tongue sucked in, arms folded tight against the flanks with the elbows jutting above the back, tail straight
  up -- 'boing'.  Play it FAST: 8 ticks with an ease-in (the links reach their slots one after another from the head
  back, 1 tick apart), a 4-tick overshoot on the tail; then swap to the DOG model at the rump's position (ActorSwap /
  form REVERTING) with the sneeze.
* stretch -- the transformation (form TRANSFORMING, DOG -> BEAST in view): w = 1 is this pose, the body compressed
  like a sitting dachshund (each link telescoped into the one in front, the rump on the floor, the neck in, the arms
  folded tight along the flanks), anchored on link_7 (the dog's rump); animate the weight 1 -> 0 over 40 ticks so the
  chain stretches out link by link (stagger: link_k starts 4 * k ticks late, choripan.crack on each), the arms
  unfolding last.
* coil -- the grab: the chain wrapped round a victim standing at {_v(L['coil']['center'] + L['coil']['T'])} (model space after the anchor,
  the ring's centre), the head swung round to face it at mouth height, flower open, the inner (left) arms reaching in
  at chest height, the outer arms bracing on the floor.  Used for the jumpscare close-up / a caught player; position
  the entity so that point is on the player.

Beat order (casa): unspool (cucha) -> trail chase (walk_* + run head) / lunge -> fetch_drop (casa.trae) -> lunge -> \
beg (parrilla, while the choripan cooks; it circles the salt ring in trail mode between begs) -> catch -> chomps -> \
vomit -> retract -> DOG.
Jumpscare portrait: FOCUS 'head', pose 'lunge' (the open flower round the black maw, bloodshot pinprick eyes, needle teeth).
"""


def _reflow(raw, width=118):
    """Re-wrap the notes: a line starting at column 0 (or ' N. ') opens a paragraph, an indented line continues it;
    table rows ('  link_...' and their description lines) and '=' rules are kept as they are."""
    import textwrap
    out, para = [], None

    def flush():
        if para:
            first, sub, words = para
            out.extend(textwrap.wrap(' '.join(words), width, initial_indent=first, subsequent_indent=sub,
                                     break_on_hyphens=False, break_long_words=False))
    for line in raw.splitlines():
        verbatim = (not line.strip() or line.startswith('=') or line.startswith('  link_')
                    or line.startswith('          '))
        if verbatim:
            flush()
            para = None
            out.append(line)
            continue
        numbered = line[:1] == ' ' and line[1:2].isdigit()
        if para is not None and line.startswith('  ') and not numbered:
            para[2].append(line.strip())
            continue
        flush()
        lead = line[:len(line) - len(line.lstrip())]
        sub = '    ' if numbered else '  '
        para = (lead, sub, [line.strip()])
    flush()
    return '\n'.join(out) + '\n'


ANIM_NOTES = _reflow(_anim_notes())
