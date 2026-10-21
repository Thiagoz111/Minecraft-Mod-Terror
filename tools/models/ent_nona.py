"""Nona Pocha (Nelida 'Pocha' Bertolotti, 73) -- the grandmother of the Casa Morales (DEAD LINE, case 'casa').

WIP v2: geometry + rig pass (flat shading).
"""
import math
import os
import sys

import numpy as np

from mcmodel import Model, hash3, face_light, pick, rot_matrix
from rig import Rig
from paint import hx, mix


def pal(*h):
    return [hx(c) for c in h]


def A(c, a=255):
    return (c[0], c[1], c[2], int(a))


# ------------------------------------------------------------------ palettes (dark -> light, hue shifted)
SKIN = pal('#3b2226', '#5a3434', '#7d4c48', '#a06a62', '#bf8a7f', '#d6a89b', '#e6c1b4', '#f1d6cb', '#f8e6dd')
HAIR = pal('#2c2a36', '#45434f', '#615f6b', '#7f7d88', '#9d9ba6', '#bab8c3', '#d3d2db', '#e8e8ef', '#f6f6fa')
CARD = pal('#1c050b', '#2e0912', '#430e1a', '#5a1423', '#721c2e', '#8a2639', '#a33447', '#ba4858')
DRESS = pal('#080b1c', '#0e1430', '#141d42', '#1c2856', '#26346a', '#33437f', '#435596')
STOCK = pal('#3a2a20', '#5a4232', '#7a5a45', '#98745a', '#b08b6e', '#c4a184', '#d5b79b')
FELT = pal('#232a36', '#323b4a', '#445063', '#58667c', '#6e7d93', '#8796aa')
RUBBER = pal('#141417', '#1f1f23', '#2c2c32', '#3b3b42', '#4f4f57')
PEARL = pal('#6e6a70', '#a7a2a6', '#d7d2d0', '#f2eee8', '#ffffff')
GOLD = pal('#5a3d10', '#8a6420', '#b88d35', '#e0bb5a', '#f6e39a')
FRAME = pal('#140a08', '#2a1510', '#43231a', '#5e3424', '#7a4a33', '#9a6a4a')
METAL = pal('#2a2e35', '#454b55', '#646c78', '#87909c', '#aab2bc', '#ccd2d9', '#eef1f4')
TENNIS = pal('#4a5a10', '#7a9418', '#a9c42a', '#cde24a', '#e6f27a')
OAK = pal('#4a3018', '#6b4624', '#8c6233', '#ab7e45', '#c69a5c', '#dbb478', '#ebcb94')
WOOL = pal('#2a0406', '#4a080c', '#6e0e14', '#94161c', '#b82428', '#d63c3a', '#ec6658')
GOURD = pal('#2a160b', '#4a2a14', '#6e421f', '#91592b', '#b0743a')
TEETH = pal('#8a8270', '#bdb49a', '#e2dac2', '#f6f1e2')
GUM = pal('#5a1a24', '#8a2e3c', '#c2606e', '#e08896')
MOUTH = pal('#050203', '#12060a', '#240c12', '#3a141c', '#5a2230')
LENS = hx('#f4f8ff')

DEBUG = {
    'skin': SKIN, 'hair': HAIR, 'card': CARD, 'dress': DRESS, 'stock': STOCK, 'felt': FELT, 'sole': RUBBER,
    'pearl': PEARL, 'gold': GOLD, 'frame': FRAME, 'metal': METAL, 'tennis': TENNIS, 'oak': OAK, 'wool': WOOL,
    'gourd': GOURD, 'teeth': TEETH, 'gum': GUM, 'maw': MOUTH, 'grip': RUBBER, 'cushion': WOOL, 'lace': PEARL,
    'aid': STOCK, 'tissue': PEARL, 'needle': METAL, 'bag': WOOL,
}


# ------------------------------------------------------------------ geometry helpers
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


def kind(ctx):
    return getattr(ctx.cube, 'kind', 'skin')


def edge(ctx):
    return min(ctx.i, ctx.j, ctx.w - 1 - ctx.i, ctx.h - 1 - ctx.j)


def make_mat(variant):
    P = variant == 'poseida'

    def mat(ctx):
        k = kind(ctx)
        if k in ('lens', 'lens_cracked'):
            return A(LENS)
        ramp = DEBUG.get(k, [hx('#ff00ff')])
        v = 0.55 + face_light(ctx)
        if edge(ctx) == 0 and min(ctx.w, ctx.h) > 2:
            v -= 0.06
        return pick(ramp, v)
    mat.variant = variant
    return mat


# ------------------------------------------------------------------ rig helpers
def _R(rot):
    return rot_matrix(*[math.radians(a) for a in rot])


def _euler(R):
    """Inverse of mcmodel.rot_matrix (Rz Ry Rx) -> (x, y, z) degrees."""
    sb = max(-1.0, min(1.0, -R[2, 0]))
    b = math.asin(sb)
    if abs(math.cos(b)) > 1e-6:
        a = math.atan2(R[2, 1], R[2, 2])
        c = math.atan2(R[1, 0], R[0, 0])
    else:
        a = math.atan2(-R[1, 2], R[1, 1])
        c = 0.0
    return (math.degrees(a), math.degrees(b), math.degrees(c))


def _T(p):
    M = np.eye(4)
    M[:3, 3] = p
    return M


def _RM(rot_deg):
    M = np.eye(4)
    M[:3, :3] = _R(rot_deg)
    return M


class Builder:
    """rig.Rig with bone-local authoring.  bone(at=...) is the pivot offset from the parent's pivot in the parent's
    own axes (absolute for a root); world=True takes a world rest position instead; wrot = desired world rotation."""

    def __init__(self):
        self.r = Rig()
        self.W = {}

    def bone(self, name, parent=None, at=(0, 0, 0), rot=(0, 0, 0), world=False, wrot=None):
        if parent is None:
            Wp = np.eye(4)
            loc = np.array(at, float)
            absp = loc
        else:
            Wp = self.W[parent]
            pa = np.array(self.r.abs_pivot[parent])
            loc = Wp[:3, :3].T @ (np.array(at, float) - Wp[:3, 3]) if world else np.array(at, float)
            absp = pa + loc
        if wrot is not None:
            rot = _euler(Wp[:3, :3].T @ _R(wrot))
        self.r.bone(name, tuple(float(v) for v in absp), parent=parent, rot=tuple(float(v) for v in rot))
        self.W[name] = Wp @ _T(loc) @ _RM(rot)
        return name

    def world(self, name, p):
        return (self.W[name] @ np.array([p[0], p[1], p[2], 1.0]))[:3]

    def box(self, bone, off, size, kind, name=None, inflate=0.0, decals=None, **attrs):
        p = self.r.abs_pivot[bone]
        c = self.r.box(bone, (p[0] + off[0], p[1] + off[1], p[2] + off[2]), size, inflate=inflate, decals=decals)
        c.kind = kind
        c.name = name or kind
        for k, v in attrs.items():
            setattr(c, k, v)
        return c


def fk(roots, pose=None):
    """World matrices of every bone with a pose table (radians / texels, added to the rest pose)."""
    pose = pose or {}
    W = {}

    def rec(b, M):
        d = (list(pose.get(b.name, ())) + [0.0] * 6)[:6]
        Mb = M @ _T(np.array(b.pivot) + np.array(d[3:6])) @ np.vstack([
            np.hstack([rot_matrix(math.radians(b.rot[0]) + d[0], math.radians(b.rot[1]) + d[1],
                                  math.radians(b.rot[2]) + d[2]), np.zeros((3, 1))]), [0, 0, 0, 1]])
        W[b.name] = Mb
        for c in b.children:
            rec(c, Mb)
    for r in roots:
        rec(r, np.eye(4))
    return W


# ------------------------------------------------------------------ proportions
HUNCH = 20.0       # chest lean from the waist (deg)
NECK_TILT = 30.0   # the neck juts forward (deg, relative to the chest)
HEAD_LOOK = -4.0   # world pitch of the head at rest (chin up a little: she looks at you over the glasses)
UPPER = 6.0        # shoulder -> elbow
FORE = 5.5         # elbow -> wrist
SHOULDER = (8.5, -8.5, 0.0)   # chest-local, x mirrored
TOES_OUT = 8.0
GRIP_X, GRIP_Y, GRIP_Z = 10.5, 2.5, -8.5      # walker grips (world, centre of the foam)
SIT_DY = 6.0       # seated: the hips drop onto the cushion


def arm_ik(Wc, sh, target, hint=None, w_hint=0.02, guess=(-40, 0, 0, -30), fa_y=0.0):
    """(arm x, y, z, forearm x) in degrees putting the wrist on `target` (world).  Wc = world matrix of the arm's
    parent, sh = arm pivot in the parent's frame, hint = world point the elbow should lean towards."""
    from scipy.optimize import minimize
    target = np.array(target, float)

    def chain(p):
        ax, ay, az, fx = p
        M = Wc @ _T(sh) @ _RM((ax, ay, az))
        elbow = (M @ np.array([0, UPPER, 0, 1.0]))[:3]
        M2 = M @ _T((0, UPPER, 0)) @ _RM((fx, fa_y, 0))
        wrist = (M2 @ np.array([0, FORE, 0, 1.0]))[:3]
        return elbow, wrist

    def cost(p):
        e, w = chain(p)
        c = float(np.sum((w - target) ** 2))
        if hint is not None:
            c += w_hint * float(np.sum((e - np.array(hint, float)) ** 2))
        c += 1e-5 * (p[1] ** 2) + (0.002 * (p[3] - 5) ** 2 if p[3] > 5 else 0.0)   # no hyper-extended elbow
        return c
    best = None
    for g in (guess, (guess[0] - 30, guess[1], guess[2], guess[3]), (guess[0] + 30, guess[1] + 20, guess[2], guess[3] - 30)):
        res = minimize(cost, list(g), method='Nelder-Mead', options={'xatol': 1e-5, 'fatol': 1e-10, 'maxiter': 8000})
        if best is None or res.fun < best.fun:
            best = res
    return tuple(best.x)


# ------------------------------------------------------------------ toggles (Java: ModelPart.visible)
# bone -> visible in the default look / rest pose
TOGGLE_DEFAULT = {
    'walker': True, 'lenses': True, 'bun': True, 'right_slipper': True,
    'rocker': False, 'needle_right': False, 'needle_left': False, 'mate': False, 'chancleta': False,
    'yarn_right': False, 'yarn_left': False, 'lenses_cracked': False, 'dentures': False,
    'hair_loose_0': False, 'hair_loose_1': False, 'hair_loose_2': False, 'hair_loose_3': False,
}
LOOSE = ('hair_loose_0', 'hair_loose_1', 'hair_loose_2', 'hair_loose_3')
VARIANT_TOGGLES = {
    'normal': {},
    'poseida': dict({'lenses': False, 'bun': False, 'lenses_cracked': True}, **{h: True for h in LOOSE}),
}
SEATED = {'walker': False, 'rocker': True}
POSE_TOGGLES = {
    'knit_sit': dict(SEATED, needle_right=True, needle_left=True),
    'stand_walker': {},
    'stand_no_walker': {'walker': False},
    'throw_chancleta': {'walker': False, 'right_slipper': False, 'chancleta': True},
    'float_rock': dict(SEATED),
    'yarn_cast': dict(SEATED, yarn_right=True, yarn_left=True),
    'scream_dentures': dict(SEATED, dentures=True),
    'sew_calm': dict(SEATED),
    'offer_mate': {'mate': True},
}


def visible_set(variant=None, pose=None):
    vis = dict(TOGGLE_DEFAULT)
    vis.update(VARIANT_TOGGLES.get(variant or 'normal', {}))
    vis.update(POSE_TOGGLES.get(pose, {}))
    return {k for k, v in vis.items() if v}


class NonaModel(Model):
    """Exports every bone to Java; the preview JSON hides the toggle bones the current look / pose does not show."""
    visible = None

    def to_json(self):
        d = super().to_json()
        if self.visible is None:
            return d
        hide = set()
        for b in self.bones():
            if b.name in TOGGLE_DEFAULT and b.name not in self.visible:
                for sub in b.walk():
                    hide.add(sub.name)
        for bd in d['bones']:
            if bd['name'] in hide:
                bd['cubes'] = []
        return d


def _argv(flag):
    a = sys.argv
    return a[a.index(flag) + 1] if flag in a and a.index(flag) + 1 < len(a) else None


# ------------------------------------------------------------------ build
def build(variant=None, pose=None):
    B = Builder()
    bone, box = B.bone, B.box

    # ---------------- floor anchor: body, walker and rocker hang from it (float = dy, rock = xRot)
    bone('base', None, (0, 24, 0))

    # ---------------- hips: pivot at the hip joints; the cardigan's lower half over the dress
    bone('body', 'base', (0, -17, 0.5))                                 # world (0, 7, 0.5)
    box('body', (-8, -8, -5.5), (16, 8, 11), 'card', 'hips')
    box('body', (-8.5, -8, -6.5), (7, 6, 1), 'card', 'cpanel_lo', sx=-1)
    box('body', (1.5, -8, -6.5), (7, 6, 1), 'card', 'cpanel_lo', sx=1)

    # ---------------- the floral skirt: front slab with a hinged hem (it folds over the knees), back slab
    bone('skirt_front', 'body', (0, -3, 0), rot=(-5, 0, 0))
    box('skirt_front', (-9, 0, -7), (18, 9, 7), 'dress', 'skirt_f')
    bone('skirt_hem', 'skirt_front', (0, 9, 0), rot=(-2, 0, 0))
    box('skirt_hem', (-9.5, 0, -7.5), (19, 3, 8), 'dress', 'hem')
    bone('skirt_back', 'body', (0, -3, 0), rot=(5, 0, 0))
    box('skirt_back', (-9, 0, 0), (18, 12, 6), 'dress', 'skirt_b')

    # ---------------- legs: thick stockings, felt slippers (the right one comes off: chancleta)
    for side, sx in (('right', -1), ('left', 1)):
        leg, shin = f'{side}_leg', f'{side}_shin'
        bone(leg, 'body', (3.5 * sx, 0, 0), rot=(0, -TOES_OUT * sx, 0))
        box(leg, (-3, 0, -3), (6, 7, 6), 'stock', 'thigh', sx=sx)
        bone(shin, leg, (0, 7, 0))
        box(shin, (-2.5, 0, -2.5), (5, 7, 5), 'stock', 'shin', sx=sx)
        if sx < 0:
            box(shin, (-2, 7, -5.5), (4, 3, 7), 'stock', 'foot', sx=sx)
            bone('right_slipper', shin, (0, 7, 0))
            sb = 'right_slipper'
            o = 0
        else:
            sb = shin
            o = 7
        box(sb, (-3, o, -6.5), (6, 2, 9), 'felt', 'slipper', sx=sx)
        box(sb, (-3.5, o + 2, -7), (7, 1, 10), 'sole', 'sole', sx=sx)
        box(sb, (-1.5, o - 1, -7), (3, 2, 2), 'wool', 'pompom', sx=sx)

    # ---------------- chest: hunched from the waist, dowager's hump, open cardigan over the dress, pearls
    bone('chest', 'body', (0, -8, 0), rot=(HUNCH, 0, 0))
    box('chest', (-6.5, -10, -4.5), (13, 10, 9), 'card', 'torso')
    box('chest', (-6, -10, 2.5), (12, 7, 4), 'card', 'hump')
    box('chest', (-5, -11, 0.5), (10, 2, 5), 'card', 'hump_top')
    box('chest', (-5.5, -11, -3.5), (11, 1, 4), 'card', 'yoke')
    box('chest', (-7, -10, -5.5), (5, 10, 1), 'card', 'cpanel', sx=-1)
    box('chest', (2, -10, -5.5), (5, 10, 1), 'card', 'cpanel', sx=1)
    box('chest', (-4, -10, -5.6), (8, 6, 0), 'pearl', 'pearls')

    # ---------------- neck + head (the head juts forward and looks up at you over the glasses)
    bone('neck', 'chest', (0, -9.5, -1), rot=(NECK_TILT, 0, 0))
    box('neck', (-2.5, -4, -2.5), (5, 5, 5), 'skin', 'neck')
    box('neck', (-2, -3, -3.5), (4, 3, 1), 'skin', 'wattle')
    bone('head', 'neck', B.world('neck', (0, -3.5, -0.5)), world=True, wrot=(HEAD_LOOK, 0, 0))
    H = 'head'
    box(H, (-8, -15, -9), (16, 12, 13), 'skin', 'skull')
    box(H, (-8, -15, -9), (16, 7, 13), 'hair', 'hair', inflate=0.6)
    box(H, (-9.6, -14, -7), (2, 6, 9), 'hair', 'wave', sx=-1)
    box(H, (7.6, -14, -7), (2, 6, 9), 'hair', 'wave', sx=1)
    box(H, (-1.5, -7, -11), (3, 4, 2), 'skin', 'nose')
    box(H, (-2, -5, -11.5), (4, 2, 1), 'skin', 'nose_tip')
    box(H, (-7, -6, -10), (4, 3, 1), 'skin', 'cheek', sx=-1)
    box(H, (3, -6, -10), (4, 3, 1), 'skin', 'cheek', sx=1)
    box(H, (-8, -5, -8.5), (2, 5, 7), 'skin', 'jowl', sx=-1)
    box(H, (6, -5, -8.5), (2, 5, 7), 'skin', 'jowl', sx=1)
    box(H, (-9, -10, -2), (1, 5, 2), 'skin', 'ear', sx=-1)
    box(H, (8, -10, -2), (1, 5, 2), 'skin', 'ear', sx=1)
    box(H, (-9.4, -5, -1.5), (1, 1, 1), 'pearl', 'earring', sx=-1)
    box(H, (8.4, -5, -1.5), (1, 1, 1), 'pearl', 'earring', sx=1)
    box(H, (-9.6, -11, -0.5), (1, 3, 1), 'aid', 'aid', sx=-1)

    bone('jaw', H, (0, -3, -1))
    box('jaw', (-6.5, 0, -8), (13, 3, 8), 'skin', 'jaw')
    box('jaw', (-3.5, 2, -8.4), (7, 2, 2), 'skin', 'chin')
    box('jaw', (-5, -10, -7), (10, 10, 6), 'maw', 'maw')
    box('jaw', (-6.2, -10, -8), (0, 10, 5), 'skin', 'flap', sx=-1)
    box('jaw', (6.2, -10, -8), (0, 10, 5), 'skin', 'flap', sx=1)

    bone('bun', H, (0, -15, 2), rot=(-25, 0, 0))
    box('bun', (-4, -5, -4), (8, 5, 8), 'hair', 'bun')
    box('bun', (-3, -6, -3), (6, 1, 6), 'hair', 'bun_top')

    bone('glasses', H, (0, -7.5, -10.4))
    box('glasses', (-9, -3.5, 0), (18, 7, 0), 'frame', 'frame')
    box('glasses', (-10, -1.5, 0), (1, 1, 9), 'frame', 'temple', sx=-1)
    box('glasses', (9, -1.5, 0), (1, 1, 9), 'frame', 'temple', sx=1)
    box('glasses', (-10.1, -1, 7), (0, 8, 6), 'pearl', 'chain', sx=-1)
    box('glasses', (10.1, -1, 7), (0, 8, 6), 'pearl', 'chain', sx=1)
    bone('lenses', 'glasses', (0, 0, 0.15))
    box('lenses', (-9, -3.5, 0), (18, 7, 0), 'lens', 'lens')
    bone('lenses_cracked', 'glasses', (0, 0, 0.1))
    box('lenses_cracked', (-9, -3.5, 0), (18, 7, 0), 'lens_cracked', 'lens_cracked')

    bone('dentures', H, (0, -2, -14))
    box('dentures', (-3, -2, -2), (6, 2, 4), 'teeth', 'denture_up')
    box('dentures', (-3, 1, -2), (6, 2, 4), 'teeth', 'denture_lo')

    loose = [((0, -15, 2), (-35, 0, 0)), ((-6, -14, -2), (-10, 0, -40)), ((6, -14, -2), (-10, 0, 40)),
             ((0, -12, 4), (-70, 0, 0))]
    for k, (p, r) in enumerate(loose):
        bn = f'hair_loose_{k}'
        bone(bn, H, p, rot=r)
        box(bn, (-2, -18, 0), (4, 18, 0), 'hair', 'strand')
        box(bn, (0, -15, -2), (0, 15, 4), 'hair', 'strand')

    # ---------------- arms: round shoulders, hands on the walker grips (solved)
    for side, sx in (('right', -1), ('left', 1)):
        arm, fa, hand = f'{side}_arm', f'{side}_forearm', f'{side}_hand'
        sh = (SHOULDER[0] * sx, SHOULDER[1], SHOULDER[2])
        target = (GRIP_X * sx, GRIP_Y - 2.4, GRIP_Z + 0.3)
        ax, ay, az, fx = arm_ik(B.W['chest'], sh, target, hint=(12 * sx, -2, 0), guess=(-40, 0, 0, -30))
        bone(arm, 'chest', sh, rot=(ax, ay, az))
        box(arm, (-2.5, -1.5, -2.5), (5, 8, 5), 'card', 'sleeve', sx=sx)
        bone(fa, arm, (0, UPPER, 0), rot=(fx, 0, 0))
        box(fa, (-2, 0, -2), (4, 4, 4), 'card', 'sleeve_lo', sx=sx)
        box(fa, (-2, 3.5, -2), (4, 2, 4), 'card', 'cuff', sx=sx, inflate=0.3)
        bone(hand, fa, B.world(fa, (0, FORE, 0)), world=True, wrot=(-10, 0, 0))
        box(hand, (-2, 0, -1.5), (4, 3, 3), 'skin', 'palm', sx=sx)
        box(hand, (-2, 3, -1.5), (4, 2, 3), 'skin', 'fingers', sx=sx, inflate=-0.1)
        box(hand, ((-2.6 if sx < 0 else 1.6), 0.5, -2.2), (1, 3, 1), 'skin', 'thumb', sx=sx)
        if sx > 0:
            box(fa, (-1, 3.6, -2.6), (2, 2, 0), 'tissue', 'tissue')

    # held props (toggles)
    bone('mate', 'right_hand', (0, 2, -2.5))
    box('mate', (-1.5, -4, -1.5), (3, 4, 3), 'gourd', 'gourd')
    box('mate', (-1.5, -4.5, -1.5), (3, 1, 3), 'metal', 'virola', inflate=0.15)
    box('mate', (0.3, -8, -0.5), (1, 4, 1), 'metal', 'bombilla')
    bone('chancleta', 'right_hand', (0, 2.5, 0))
    box('chancleta', (-3, -1, -4.5), (6, 2, 9), 'felt', 'slipper')
    box('chancleta', (-3.5, 1, -5), (7, 1, 10), 'sole', 'sole')
    bone('needle_right', 'right_hand', (0, 2, 0))
    box('needle_right', (-0.5, -0.5, -10), (1, 1, 12), 'needle', 'needle')
    bone('needle_left', 'left_hand', (0, 2, 0))
    box('needle_left', (-0.5, -0.5, -10), (1, 1, 12), 'needle', 'needle')
    box('needle_left', (-3, 0.5, -9), (6, 8, 0), 'wool', 'knit')
    bone('yarn_right', 'right_hand', (0, 4, 0))
    box('yarn_right', (-1, 0, 0), (2, 30, 0), 'wool', 'yarn')
    bone('yarn_left', 'left_hand', (0, 4, 0))
    box('yarn_left', (-1, 0, 0), (2, 30, 0), 'wool', 'yarn')

    # red wool ball in the cardigan pocket (her right hip)
    bone('yarn_ball', 'body', (-5, -3.5, -7))
    box('yarn_ball', (-2, -2, -2), (4, 4, 4), 'wool', 'ball')

    # ---------------- walker (andador): aluminium U frame, front wheels, cut tennis balls on the back legs
    bone('walker', 'base', (0, 0, 0))
    gy = GRIP_Y - 24
    for sx in (-1, 1):
        x = GRIP_X * sx
        box('walker', (x - 0.5, gy - 0.5, -17), (1, 19, 1), 'metal', 'tube')       # front leg (to the wheel)
        box('walker', (x - 0.5, gy - 0.5, -4), (1, 21, 1), 'metal', 'tube')        # back leg (to the tennis ball)
        box('walker', (x - 0.5, gy - 0.5, -17), (1, 1, 14), 'metal', 'tube')       # side rail
        box('walker', (x - 1, gy - 1, GRIP_Z - 2.5), (2, 2, 5), 'grip', 'grip')    # foam grip
        box('walker', (x - 1.5, -3, -5), (3, 3, 3), 'tennis', 'tennis')
    box('walker', (-GRIP_X, gy - 0.5, -17), (int(2 * GRIP_X), 1, 1), 'metal', 'tube')   # front top bar
    box('walker', (-GRIP_X, gy + 9, -17), (int(2 * GRIP_X), 1, 1), 'metal', 'tube')     # front low bar
    box('walker', (GRIP_X - 0.5, -5, -19), (1, 5, 5), 'grip', 'wheel')
    box('walker', (-6, gy + 0.5, -18), (8, 7, 2), 'bag', 'bag')
    bone('walker_wheel', 'walker', (-GRIP_X, -2.5, -16.5))
    box('walker_wheel', (-0.5, -2.5, -2.5), (1, 5, 5), 'grip', 'wheel')

    # ---------------- rocking chair (light oak, crocheted cushion, doily over the crest)
    bone('rocker', 'base', (0, 0, 0))
    seat = -24 + 7 + SIT_DY + 3            # cushion top (local y): thighs rest on it
    box('rocker', (-9.5, seat, -8), (19, 2, 15), 'cushion', 'cushion')
    box('rocker', (-10.5, seat + 2, -9), (21, 2, 17), 'oak', 'seat')
    for sx in (-1, 1):
        x0 = -10.5 if sx < 0 else 8.5
        box('rocker', (x0, seat + 4, -8.5), (2, -seat - 7, 2), 'oak', 'leg')
        box('rocker', (x0, seat + 4, 5), (2, -seat - 7, 2), 'oak', 'leg')
        box('rocker', (x0, -3, -9), (2, 3, 17), 'oak', 'runner')
        box('rocker', (x0, -4, -14), (2, 2, 5), 'oak', 'runner')
        box('rocker', (x0, -5, 8), (2, 2, 6), 'oak', 'runner')
        box('rocker', (x0 - 0.5 * sx, seat - 9, -9), (2, 2, 15), 'oak', 'armrest')
        box('rocker', (x0, seat - 7, -8.5), (2, 7, 2), 'oak', 'post')
    bone('rocker_back', 'rocker', (0, seat + 2, 7), rot=(-12, 0, 0))
    for sx in (-1, 1):
        x0 = -10.5 if sx < 0 else 8.5
        box('rocker_back', (x0, -36, -1), (2, 36, 2), 'oak', 'stile')
    box('rocker_back', (-11.5, -40, -1.5), (23, 5, 3), 'oak', 'crest')
    box('rocker_back', (-8.5, -35, 0), (17, 31, 0), 'oak', 'spindles')
    box('rocker_back', (-6, -38, -1.7), (12, 8, 0), 'lace', 'doily')

    m = NonaModel('nona', 256, 256, B.r.roots)
    m.scale = 0.5
    if pose is None and os.path.basename(sys.argv[0]) == 'preview.py':
        pose = _argv('--pose')
    m.visible = visible_set(variant, pose)
    m.builder = B
    return m


DEFAULT_MAT = make_mat('normal')
VARIANT_MATS = {'normal': DEFAULT_MAT, 'poseida': make_mat('poseida')}
FOCUS = 'head'


# ------------------------------------------------------------------ poses (solved against the rest rig)
def _bones(m):
    return {b.name: b for b in m.bones()}


def pose_arm(m, pose, side, target, hint=None, hand_wrot=None, w_hint=0.02, guess=(-40, 0, 0, -30)):
    """Adds <side>_arm / _forearm (/ _hand) deltas to `pose` so the wrist lands on `target` (world, posed body)."""
    bn = _bones(m)
    arm, fa, hand = bn[f'{side}_arm'], bn[f'{side}_forearm'], bn[f'{side}_hand']
    W = fk(m.roots, pose)
    Wc = W[arm.parent.name]
    ax, ay, az, fx = arm_ik(Wc, np.array(arm.pivot), target, hint, w_hint, guess, fa_y=fa.rot[1])
    r = math.radians
    pose[arm.name] = (r(ax - arm.rot[0]), r(ay - arm.rot[1]), r(az - arm.rot[2]), 0, 0, 0)
    pose[fa.name] = (r(fx - fa.rot[0]), 0, 0, 0, 0, 0)
    if hand_wrot is not None:
        W = fk(m.roots, pose)
        Wf = W[fa.name]
        loc = _euler(Wf[:3, :3].T @ _R(hand_wrot))
        pose[hand.name] = (r(loc[0] - hand.rot[0]), r(loc[1] - hand.rot[1]), r(loc[2] - hand.rot[2]), 0, 0, 0)
    return pose


def _sit(extra=None):
    """Seated in the rocker: hips drop onto the cushion, thighs forward, shins hang, the skirt drapes the lap."""
    p = {
        'body': (0, 0, 0, 0, SIT_DY, 0),
        'right_leg': (-1.5708, 0, 0, 0, 0, 0), 'left_leg': (-1.5708, 0, 0, 0, 0, 0),
        'right_shin': (1.5708, 0, 0, 0, 0, 0), 'left_shin': (1.5708, 0, 0, 0, 0, 0),
        'skirt_front': (-1.48, 0, 0, 0, 2.5, 0.5), 'skirt_hem': (1.5, 0, 0, 0, 0, 0),
        'skirt_back': (-1.2, 0, 0, 0, 3.0, 1.0),
    }
    if extra:
        p.update(extra)
    return p


def make_poses():
    m = build(pose='__none__')
    P = {}
    P['stand_walker'] = {'head': (0, 0, 0.1, 0, 0, 0)}
    P['stand_no_walker'] = {'chest': (-0.22, 0, 0, 0, 0, 0), 'neck': (-0.1, 0, 0, 0, 0, 0)}
    pose_arm(m, P['stand_no_walker'], 'right', (-8.5, 1.5, 1.0), hint=(-14, -3, 2))
    pose_arm(m, P['stand_no_walker'], 'left', (8.5, 1.5, 1.0), hint=(14, -3, 2))
    P['knit_sit'] = _sit()
    pose_arm(m, P['knit_sit'], 'right', (-3, -2, -10), hint=(-11, 0, -4))
    pose_arm(m, P['knit_sit'], 'left', (3, -2, -10), hint=(11, 0, -4))
    return P


POSES = make_poses()

ANIM_NOTES = """WIP"""
