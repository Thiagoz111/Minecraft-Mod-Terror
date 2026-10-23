"""La mano gris -- event 39 'bajo_cama' of Casa Morales (DEAD LINE, docs/design/casa_terror.md 5).

A grey arm far too long for a person creeps out from under a bed, lies flat on the floor, the long fingers feel along
the floorboards, dig in... and the whole thing is pulled back into the dark.  Only the hand and the forearm ever leave
the bed; the elbow and the upper arm stay under it (the entity moves along its facing, the arm trails behind).

Authored at 2x texel density (model.scale = 0.5): +Y down, ground y = 24, the fingers point -Z, right_* on -X.
It is a RIGHT hand lying palm down, so the thumb is on -X.  Lengths: fingertips z -19 .. shoulder end z +50
(2.2 blocks), 0.2 block high.  Bones: forearm (root, wrist pivot) -> upper_arm (elbow) ; forearm -> hand ->
finger_1..finger_4 (+ _tip) and thumb (+ thumb_tip).

Skin: cold dead grey with a green-blue cast, darker and bruised purple at the knuckles and the wrist, tendons on the
back of the hand, blue-black veins up the forearm, filth on the fingertips, long cracked yellow-black nails.
"""
import math

from mcmodel import Model, fbm, vnoise, hash3, face_light, pick
from rig import Rig
from paint import hx, mix


def pal(*h):
    return [hx(c) for c in h]


GREY = pal('#121416', '#1f2224', '#2f3334', '#424745', '#565b57', '#6b6f69', '#80837b', '#94968c', '#a7a89c', '#b8b8aa')
BRUISE = pal('#2a1f30', '#3e2c44', '#523c56')
VEIN = pal('#1d2836', '#2b3a4a')
DIRT = pal('#1a140e', '#2a2016', '#3a2c1e')
NAIL = pal('#0c0a08', '#211b13', '#3b3121', '#5c4d33', '#7c6b49')


def clamp(v, a=0.0, b=1.0):
    return a if v < a else b if v > b else v


def local(ctx):
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


def skin(ctx, base=0.6):
    """Grey skin lit from above: tops light, sides mid, the underside (on the floor) dark; blotchy, never flat."""
    x, y, z = ctx.pos
    v = base - 0.08 + face_light(ctx) * 1.0
    v += (fbm(x * 0.45, y * 0.45, z * 0.45, 3, 4) - 0.5) * 0.3
    v += (hash3(x * 2, y * 2, z * 2, 9) - 0.5) * 0.06
    return v


def livor(ctx, c):
    """Purple-grey livor mortis blotches pooling where the blood settled."""
    x, y, z = ctx.pos
    n = fbm(x * 0.22, y * 0.22, z * 0.22, 3, 17)
    if n > 0.58:
        return mix(c, BRUISE[1], min(0.55, (n - 0.58) * 3.0))
    return c


def arm_mat(ctx):
    x, y, z = ctx.pos
    name = ctx.cube.name
    lx, ly, lz = local(ctx)
    v = skin(ctx, 0.56 if name == 'upper' else 0.6)
    c = livor(ctx, pick(GREY, v))
    if ctx.face in ('top', 'west', 'east'):
        # blue-black veins snaking up the forearm (two long ones on top, branches down the sides)
        for k, (x0, amp, ph) in enumerate(((-1.2, 1.1, 0.0), (1.4, 0.9, 1.7))):
            vx = x0 + math.sin(z * 0.23 + ph) * amp + math.sin(z * 0.61 + ph * 2) * 0.35
            if ctx.face == 'top' and abs(x - vx) < 0.5 and z > 2:
                c = mix(c, VEIN[k % 2], 0.65)
        if ctx.face != 'top' and hash3(math.floor(z * 0.5), math.floor(y), x > 0, 13) > 0.86:
            c = mix(c, VEIN[0], 0.35)
    if name == 'wrist' or (name == 'forearm' and z < 4):
        c = mix(c, BRUISE[1], 0.28 + 0.2 * vnoise(x * 0.8, y, z * 0.8, 3))     # the bruise ring at the wrist
    if name == 'upper':
        # the part under the bed: darker, a raw graze where it drags on the floor
        c = mix(c, GREY[1], 0.3 + clamp((z - 30) / 25.0) * 0.4)
        if ctx.face == 'bottom':
            c = mix(c, hx('#4a1a1c'), 0.35)
    if ctx.face == 'bottom':
        c = mix(c, DIRT[1], 0.35)
    return c


def hand_mat(ctx):
    x, y, z = ctx.pos
    lx, ly, lz = local(ctx)
    v = skin(ctx, 0.62)
    c = livor(ctx, pick(GREY, v))
    if ctx.face == 'top':
        # tendons fanning from the wrist to each knuckle
        for fx in (-3.0, -1.0, 1.0, 3.0):
            tx = fx * clamp((-z) / 8.0) * 0.95
            if abs(x - tx) < 0.45 and z < -1:
                c = pick(GREY, v + 0.12)
            elif abs(x - tx) < 1.0 and z < -1:
                c = pick(GREY, v - 0.05)
        if z < -6.5:
            c = mix(c, BRUISE[2], 0.45)                         # bruised purple knuckles
            if hash3(math.floor(x), 0, math.floor(z * 2), 7) > 0.6:
                c = mix(c, GREY[2], 0.5)                        # knuckle creases
    if ctx.face == 'bottom':
        c = mix(pick(GREY, 0.3), DIRT[0], 0.4)
    return c


def finger_mat(ctx):
    x, y, z = ctx.pos
    name = ctx.cube.name
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    tip = name == 'tip'
    v = skin(ctx, 0.6)
    c = livor(ctx, pick(GREY, v))
    # knuckle creases: dark rings at the joints
    if ctx.face != 'front' and ctx.face != 'back':
        along = lz
        if (not tip and along > d - 1.2) or (tip and along > d - 0.8):
            c = mix(c, BRUISE[0], 0.4)
        if not tip and abs(along - d * 0.45) < 0.5:
            c = mix(c, GREY[3], 0.5)
    if tip:
        # the long nail on the top of the last 2.5 texels and over the end; filth under it
        if ctx.face == 'top' and lz < 2.6:
            c = pick(NAIL, 0.35 + 0.5 * (lz / 2.6) + (0.15 if ctx.i == 0 else 0))
            if hash3(x * 3, z * 3, 1, 21) > 0.82:
                c = NAIL[0]                                     # a crack
        elif ctx.face == 'front':
            c = NAIL[1] if ctx.j == 0 else DIRT[2]
        elif ctx.face in ('west', 'east') and lz < 2.0:
            c = NAIL[2] if ly < 1.0 else DIRT[1]
        elif ctx.face == 'bottom' and lz < 3.0:
            c = mix(c, DIRT[0], 0.7)                            # fingertips black with filth
    if ctx.face == 'bottom':
        c = mix(c, DIRT[1], 0.3)
    return c


DEFAULT_MAT = arm_mat
FOCUS = 'hand'

FINGERS = [(-3.0, 'finger_1', 6, 5, 7.0), (-1.0, 'finger_2', 7, 5, 2.0), (1.0, 'finger_3', 7, 5, -3.0),
           (3.0, 'finger_4', 5, 4, -9.0)]


def build():
    r = Rig()
    r.bone('forearm', (0, 21.5, 0), mat=arm_mat)
    c = r.box('forearm', (-3, 19, 1), (6, 5, 25))
    c.name = 'forearm'
    c = r.box('forearm', (-3.5, 20, -1), (7, 4, 2))
    c.name = 'wrist'
    r.bone('upper_arm', (0, 21.5, 26), parent='forearm', mat=arm_mat)
    c = r.box('upper_arm', (-3.5, 18.5, 25), (7, 6, 25))
    c.name = 'upper'
    r.bone('hand', (0, 22, 0), parent='forearm', mat=hand_mat)
    c = r.box('hand', (-4, 21, -8), (8, 3, 8))
    c.name = 'palm'
    for cx, name, l1, l2, yaw in FINGERS:
        r.bone(name, (cx, 23, -8), parent='hand', rot=(0, yaw, 0), mat=finger_mat)
        c = r.box(name, (cx - 1, 22, -8 - l1), (2, 2, l1))
        c.name = 'prox'
        r.bone(name + '_tip', (cx, 23, -8 - l1), parent=name, rot=(0, 0, 0), mat=finger_mat)
        c = r.box(name + '_tip', (cx - 1, 22, -8 - l1 - l2), (2, 2, l2))
        c.name = 'tip'
    r.bone('thumb', (-4, 23, -3), parent='hand', rot=(0, 38, 0), mat=finger_mat)
    c = r.box('thumb', (-5.5, 22, -8), (2, 2, 5))
    c.name = 'prox'
    r.bone('thumb_tip', (-4.5, 23, -8), parent='thumb', rot=(0, 10, 0), mat=finger_mat)
    c = r.box('thumb_tip', (-5.5, 22, -12), (2, 2, 4))
    c.name = 'tip'
    m = Model('mano', 128, 64, r.roots)
    m.scale = 0.5
    return m


# poses (radians / texels, ADDED to the rest pose)
POSES = {
    # the fingers dig into the floorboards: curled down at both joints, the hand arched up off the floor
    'grip': {'hand': (-0.18, 0, 0, 0, -0.4, 0),
             'finger_1': (0.55, 0, 0, 0, 0, 0), 'finger_1_tip': (0.75, 0, 0, 0, 0, 0),
             'finger_2': (0.6, 0, 0, 0, 0, 0), 'finger_2_tip': (0.8, 0, 0, 0, 0, 0),
             'finger_3': (0.6, 0, 0, 0, 0, 0), 'finger_3_tip': (0.8, 0, 0, 0, 0, 0),
             'finger_4': (0.5, 0, 0, 0, 0, 0), 'finger_4_tip': (0.7, 0, 0, 0, 0, 0),
             'thumb': (0.3, -0.2, 0, 0, 0, 0), 'thumb_tip': (0.4, 0, 0, 0, 0, 0)},
    # reaching: the fingers spread and lifted, the hand raised at the wrist toward you
    'reach': {'hand': (-0.35, 0, 0, 0, -0.6, 0),
              'finger_1': (-0.25, 0.12, 0, 0, 0, 0), 'finger_1_tip': (0.2, 0, 0, 0, 0, 0),
              'finger_2': (-0.2, 0.05, 0, 0, 0, 0), 'finger_2_tip': (0.25, 0, 0, 0, 0, 0),
              'finger_3': (-0.2, -0.05, 0, 0, 0, 0), 'finger_3_tip': (0.25, 0, 0, 0, 0, 0),
              'finger_4': (-0.15, -0.15, 0, 0, 0, 0), 'finger_4_tip': (0.3, 0, 0, 0, 0, 0),
              'thumb': (-0.1, 0.25, 0, 0, 0, 0)},
}

ANIM_NOTES = """La mano gris (ManoEntity) -- animation notes.  Radians; offsets in texels at 2x density.  t = ageInTicks.
The entity is the HAND: it slides along its facing (the server moves it out from under the bed and back); the forearm
and the upper arm trail behind it under the bed.  action 0 = CREEP (coming out), 1 = GRIP (holding the floor),
2 = RETRACT (yanked back).
* CREEP: the fingers 'walk' -- finger_k xRot = max(0, sin(t * 0.55 + k * 1.3)) * 0.45 (lift and plant in a wave from
  the little finger to the index), tips follow at 0.6x; the hand rises a little with each step (dy -0.3).  Blend
  'reach' at 0.35 so it reads as feeling for something.
* GRIP: blend 'grip' in over 4 ticks; then a scratching tremor finger_k xRot += sin(t * 2.2 + k) * 0.05.
* RETRACT: the fingers splay and drag: blend 'reach' at 1.0 in 2 ticks, tips trail (tip xRot -0.2).
* The elbow (upper_arm) bends a little as the arm slides: yRot sin(t * 0.08) * 0.12.
"""
