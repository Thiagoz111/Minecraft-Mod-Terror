"""Nona Pocha (Nelida 'Pocha' Bertolotti, 73) -- the grandmother of the Casa Morales (DEAD LINE, case 'casa').

WIP v1: geometry pass.
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
SKIN = pal('#3b2226', '#5a3434', '#7d4c48', '#a06a62', '#bf8a7f', '#d6a89b', '#e6c1b4', '#f1d6cb', '#f8e6dd',
           '#fdf3ee')
HAIR = pal('#2c2a36', '#45434f', '#615f6b', '#7f7d88', '#9d9ba6', '#bab8c3', '#d3d2db', '#e8e8ef', '#f6f6fa')
CARD = pal('#1c050b', '#2e0912', '#430e1a', '#5a1423', '#721c2e', '#8a2639', '#a33447', '#ba4858', '#cd6169')
DRESS = pal('#080b1c', '#0e1430', '#141d42', '#1c2856', '#26346a', '#33437f', '#435596')
STOCK = pal('#3a2a20', '#5a4232', '#7a5a45', '#98745a', '#b08b6e', '#c4a184', '#d5b79b')
FELT = pal('#1d1512', '#2e211b', '#433127', '#5a4334', '#735743', '#8c6c55')
PEARL = pal('#6e6a70', '#a7a2a6', '#d7d2d0', '#f2eee8', '#ffffff')
GOLD = pal('#5a3d10', '#8a6420', '#b88d35', '#e0bb5a', '#f6e39a')
FRAME = pal('#140a08', '#2a1510', '#43231a', '#5e3424', '#7a4a33', '#9a6a4a')
METAL = pal('#2a2e35', '#454b55', '#646c78', '#87909c', '#aab2bc', '#ccd2d9', '#eef1f4')
RUBBER = pal('#141417', '#1f1f23', '#2c2c32', '#3b3b42', '#4f4f57')
TENNIS = pal('#4a5a10', '#7a9418', '#a9c42a', '#cde24a', '#e6f27a')
OAK = pal('#4a3018', '#6b4624', '#8c6233', '#ab7e45', '#c69a5c', '#dbb478', '#ebcb94', '#f5dfb4')
WOOL = pal('#2a0406', '#4a080c', '#6e0e14', '#94161c', '#b82428', '#d63c3a', '#ec6658')
GOURD = pal('#2a160b', '#4a2a14', '#6e421f', '#91592b', '#b0743a')
GUM = pal('#5a1a24', '#8a2e3c', '#c2606e', '#e08896')
TEETH = pal('#8a8270', '#bdb49a', '#e2dac2', '#f6f1e2')
MOUTH = pal('#050203', '#12060a', '#240c12', '#3a141c', '#5a2230')
LENS = hx('#f4f8ff')


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


def tag(ctx):
    return ctx.cube.name or ''


def edge(ctx):
    return min(ctx.i, ctx.j, ctx.w - 1 - ctx.i, ctx.h - 1 - ctx.j)


def shade(ctx, ramp, base=0.55, light=1.0, edge_amt=0.06):
    v = base + face_light(ctx) * light
    if edge(ctx) == 0 and min(ctx.w, ctx.h) > 2:
        v -= edge_amt
    return pick(ramp, v)


# ------------------------------------------------------------------ materials (v1: flat-ish, per tag)
FLAT = {
    'skull': SKIN, 'nose': SKIN, 'cheek': SKIN, 'jowl': SKIN, 'jaw': SKIN, 'ear': SKIN, 'neck': SKIN,
    'hand': SKIN, 'thumb': SKIN, 'flap': SKIN,
    'roll': HAIR, 'puff': HAIR, 'bun': HAIR, 'bun_top': HAIR, 'strand': HAIR,
    'chest': CARD, 'hump': CARD, 'panel': CARD, 'collar': CARD, 'pelvis': CARD, 'sleeve': CARD, 'cuff': CARD,
    'skirt': DRESS, 'hem': DRESS,
    'thigh': STOCK, 'shin': STOCK, 'foot': STOCK,
    'slipper': FELT, 'sole': RUBBER,
    'tube': METAL, 'grip': RUBBER, 'wheel': RUBBER, 'tennis': TENNIS,
    'oak': OAK, 'cushion': WOOL, 'slats': OAK, 'doily': PEARL,
    'needle': METAL, 'knob': GOLD, 'knit': WOOL, 'ball': WOOL, 'yarn': WOOL,
    'gourd': GOURD, 'virola': METAL, 'bombilla': METAL,
    'denture': TEETH, 'maw': MOUTH, 'aid': STOCK, 'tissue': PEARL, 'pearls': PEARL,
    'frame': FRAME, 'temple': FRAME,
}


def make_mat(variant):
    P = variant == 'poseida'

    def mat(ctx):
        t = tag(ctx)
        if t in ('lens', 'lens_cracked'):
            return A(LENS)
        ramp = FLAT.get(t)
        if ramp is None:
            return (255, 0, 255, 255)
        if P and ramp is SKIN:
            ramp = HAIR
        return shade(ctx, ramp)
    mat.variant = variant
    return mat


# ------------------------------------------------------------------ builder
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


class Builder:
    """rig.Rig plus world-space placement (pivots / orientations given in the WORLD rest frame)."""

    def __init__(self):
        self.r = Rig()
        self.W = {}

    def bone(self, name, pivot, parent=None, rot=(0, 0, 0), world=False, wrot=None):
        if parent is None:
            Wp = np.eye(4)
            loc = np.array(pivot, float)
            absp = loc
        else:
            Wp = self.W[parent]
            pa = np.array(self.r.abs_pivot[parent])
            if world:
                loc = Wp[:3, :3].T @ (np.array(pivot, float) - Wp[:3, 3])
            else:
                loc = np.array(pivot, float) - pa
            absp = pa + loc
        if wrot is not None:
            rot = _euler(Wp[:3, :3].T @ _R(wrot))
        self.r.bone(name, tuple(float(v) for v in absp), parent=parent, rot=tuple(rot))
        T = np.eye(4)
        T[:3, 3] = loc
        Rm = np.eye(4)
        Rm[:3, :3] = _R(rot)
        self.W[name] = Wp @ T @ Rm
        return name

    def world(self, name, p):
        """World rest position of a point given relative to the bone pivot in the bone's own axes."""
        return (self.W[name] @ np.array([p[0], p[1], p[2], 1.0]))[:3]

    def lbox(self, bone, off, size, name, inflate=0.0, decals=None):
        p = self.r.abs_pivot[bone]
        c = self.r.box(bone, (p[0] + off[0], p[1] + off[1], p[2] + off[2]), size, inflate=inflate, decals=decals)
        c.name = name
        return c


def solve_arm(B, chest, sx, shoulder, target, wrist_wrot, elbow_guess=-30.0):
    """Upper-arm (x, y, z) + forearm x rotations (deg) that put the wrist on `target` (world)."""
    from scipy.optimize import minimize
    Wc = B.W[chest]
    pa = np.array(B.r.abs_pivot[chest])
    loc = np.array(shoulder, float) - pa

    def wrist(p):
        ax, ay, az, fx = p
        M = Wc.copy()
        T = np.eye(4)
        T[:3, 3] = loc
        R = np.eye(4)
        R[:3, :3] = _R((ax, ay, az))
        M = M @ T @ R
        T2 = np.eye(4)
        T2[:3, 3] = (0, UPPER, 0)
        R2 = np.eye(4)
        R2[:3, :3] = _R((fx, 0, 0))
        M = M @ T2 @ R2
        return (M @ np.array([0, FORE, 0, 1.0]))[:3]

    def cost(p):
        e = wrist(p) - np.array(target)
        return e @ e + 0.0004 * (p[1] ** 2 + (p[3] - elbow_guess) ** 2)
    res = minimize(cost, [-40, 0, -5 * sx, elbow_guess], method='Nelder-Mead',
                   options={'xatol': 1e-4, 'fatol': 1e-8, 'maxiter': 4000})
    return tuple(res.x)


UPPER = 6.0      # shoulder -> elbow
FORE = 6.0       # elbow -> wrist
HUNCH = 20.0     # chest lean from the waist (deg)
NECK_TILT = 34.0 # the neck juts forward (deg, relative to the chest)
GRIP_X, GRIP_Y, GRIP_Z = 9.5, 3.0, -10.0     # walker hand grips (world, centre of the foam)


class NonaModel(Model):
    """Exports every bone to Java; the preview JSON hides the toggle bones the current variant / pose does not show."""
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


# toggle bone -> visible by default?
TOGGLE_DEFAULT = {
    'walker': True, 'lenses': True, 'bun': True, 'right_slipper': True,
    'rocker': False, 'needle_right': False, 'needle_left': False, 'mate': False, 'chancleta': False,
    'yarn_right': False, 'yarn_left': False, 'lenses_cracked': False, 'dentures': False,
    'hair_loose_0': False, 'hair_loose_1': False, 'hair_loose_2': False, 'hair_loose_3': False,
    'hair_loose_4': False, 'hair_loose_5': False,
}
VARIANT_TOGGLES = {
    'normal': {},
    'poseida': {'lenses': False, 'bun': False, 'lenses_cracked': True, 'dentures': True,
                'hair_loose_0': True, 'hair_loose_1': True, 'hair_loose_2': True, 'hair_loose_3': True,
                'hair_loose_4': True, 'hair_loose_5': True},
}
SEATED = {'walker': False, 'rocker': True}
POSE_TOGGLES = {
    'knit_sit': dict(SEATED, needle_right=True, needle_left=True),
    'stand_walker': {},
    'stand_no_walker': {'walker': False},
    'throw_chancleta': {'walker': False, 'right_slipper': False, 'chancleta': True},
    'float_rock': dict(SEATED),
    'yarn_cast': dict(SEATED, yarn_right=True, yarn_left=True),
    'scream_dentures': dict(SEATED),
    'sew_calm': dict(SEATED),
    'offer_mate': {'mate': True},
}


def visible_set(variant=None, pose=None):
    vis = {k: v for k, v in TOGGLE_DEFAULT.items()}
    vis.update(VARIANT_TOGGLES.get(variant or 'normal', {}))
    vis.update(POSE_TOGGLES.get(pose, {}))
    return {k for k, v in vis.items() if v}


def _argv(flag):
    a = sys.argv
    return a[a.index(flag) + 1] if flag in a and a.index(flag) + 1 < len(a) else None


def build(variant=None, pose=None):
    B = Builder()
    bone, lbox = B.bone, B.lbox

    # ---------------- floor anchor: body, walker and rocker hang from it (float = dy, rock = xRot)
    bone('base', (0, 24, 0))

    # ---------------- hips (cardigan lower half) + the floral skirt in three hinged pieces
    bone('body', (0, 6, 0.5), parent='base')
    lbox('body', (-8, -5, -5), (16, 5, 10), 'pelvis')
    lbox('body', (-8.5, -5, -5.5), (6, 5, 1), 'panel_lo')
    lbox('body', (2.5, -5, -5.5), (6, 5, 1), 'panel_lo')
    bone('skirt_front', (0, 6, 0.5), parent='body', rot=(-4, 0, 0))
    lbox('skirt_front', (-8.5, 0, -6), (17, 7, 6), 'skirt')
    bone('skirt_hem', (0, 13, 0.5), parent='skirt_front', rot=(-4, 0, 0))
    lbox('skirt_hem', (-9, 0, -6.5), (18, 3, 7), 'hem')
    bone('skirt_back', (0, 6, 0.5), parent='body', rot=(5, 0, 0))
    lbox('skirt_back', (-8.5, 0, 0), (17, 10, 6), 'skirt')

    # ---------------- legs: thick tan stockings, felt slippers (the right one comes off: chancleta)
    for side, sx in (('right', -1), ('left', 1)):
        leg, shin, foot = f'{side}_leg', f'{side}_shin', f'{side}_foot'
        x = 3.5 * sx
        bone(leg, (x, 6, 0.5), parent='body')
        lbox(leg, (-2.5, 0, -2.5), (5, 7, 5), 'thigh')
        bone(shin, (x, 13, 0.5), parent=leg)
        lbox(shin, (-2.5, 0, -2.5), (5, 8, 5), 'shin')
        bone(foot, (x, 21, 0.5), parent=shin)
        if sx < 0:
            lbox(foot, (-2, 0.5, -4), (4, 2, 6), 'foot')
            bone('right_slipper', (x, 21, 0.5), parent=foot)
            sb = 'right_slipper'
        else:
            sb = foot
        lbox(sb, (-2.5, 0, -5), (5, 2, 7), 'slipper')
        lbox(sb, (-3, 2, -5.5), (6, 1, 8), 'sole')

    # ---------------- chest: hunched from the waist, dowager's hump, open cardigan over the dress, pearls
    bone('chest', (0, 1, 1), parent='body', rot=(HUNCH, 0, 0))
    lbox('chest', (-7, -10, -4.5), (14, 10, 9), 'chest')
    lbox('chest', (-6, -11, -3.5), (12, 1, 7), 'yoke')
    lbox('chest', (-6, -11, 1.5), (12, 7, 5), 'hump')
    lbox('chest', (-7.5, -10, -5.5), (5, 10, 1), 'panel')
    lbox('chest', (2.5, -10, -5.5), (5, 10, 1), 'panel')
    lbox('chest', (-3, -10, -5.0), (6, 4, 0), 'pearls')

    # ---------------- neck + head (the head juts forward and looks up at you over the glasses)
    bone('neck', (0, -9.5, 0), parent='chest', rot=(NECK_TILT, 0, 0))
    lbox('neck', (-2.5, -4, -2.5), (5, 5, 5), 'neck')
    top = B.world('neck', (0, -3, -0.5))
    bone('head', tuple(top), parent='neck', world=True, wrot=(-6, 0, 0))
    H = 'head'
    lbox(H, (-8, -12, -10), (16, 12, 14), 'skull')
    lbox(H, (-8.5, -13, -10.5), (17, 5, 15), 'cap')
    lbox(H, (-9.5, -10, -7), (2, 6, 10), 'puff')
    lbox(H, (7.5, -10, -7), (2, 6, 10), 'puff')
    lbox(H, (-8.5, -5, -2), (1, 3, 2), 'ear')
    lbox(H, (7.5, -5, -2), (1, 3, 2), 'ear')
    lbox(H, (-9, -6, 0.5), (1, 3, 2), 'aid')
    lbox(H, (-1.5, -6, -11.5), (3, 3, 2), 'nose')
    lbox(H, (-7, -4, -10.5), (4, 3, 1), 'cheek')
    lbox(H, (3, -4, -10.5), (4, 3, 1), 'cheek')
    lbox(H, (-8, 0, -9), (2, 2, 7), 'jowl')
    lbox(H, (6, 0, -9), (2, 2, 7), 'jowl')

    hp = np.array(B.r.abs_pivot[H])
    bone('jaw', tuple(hp + (0, -1, -1)), parent=H)
    lbox('jaw', (-6, 0, -8.6), (12, 5, 10), 'jaw')
    lbox('jaw', (-4, -6, -8), (8, 6, 4), 'maw')
    lbox('jaw', (-6, -6, -8.3), (2, 7, 0), 'flap')
    lbox('jaw', (4, -6, -8.3), (2, 7, 0), 'flap')

    bone('bun', tuple(hp + (0, -13, 1.5)), parent=H, rot=(-22, 0, 0))
    lbox('bun', (-3.5, -4, -3.5), (7, 4, 7), 'bun')
    lbox('bun', (-2.5, -5, -2.5), (5, 1, 5), 'bun_top')

    bone('glasses', tuple(hp + (0, -6.5, -11.2)), parent=H)
    lbox('glasses', (-9, -4, 0), (18, 8, 0), 'frame')
    lbox('glasses', (-10, -1.5, 0.2), (1, 1, 10), 'temple')
    lbox('glasses', (9, -1.5, 0.2), (1, 1, 10), 'temple')
    bone('lenses', tuple(hp + (0, -6.5, -11.0)), parent='glasses')
    lbox('lenses', (-9, -4, 0), (18, 8, 0), 'lens')
    bone('lenses_cracked', tuple(hp + (0, -6.5, -11.0)), parent='glasses')
    lbox('lenses_cracked', (-9, -4, 0), (18, 8, 0), 'lens_cracked')

    bone('dentures', tuple(hp + (0, 1.5, -13.5)), parent=H)
    lbox('dentures', (-3.5, -2, -2), (7, 2, 4), 'denture')
    lbox('dentures', (-3, 0.5, -1.5), (6, 2, 4), 'denture')

    loose = [((-4, -12.5, -2), (-15, 0, 30)), ((4, -12.5, -2), (-15, 0, -30)), ((0, -13, 1), (-35, 0, 4)),
             ((-7, -10, 2), (-10, 0, 70)), ((7, -10, 2), (-10, 0, -70)), ((0, -10, 4), (-75, 0, 0))]
    for k, (p, r) in enumerate(loose):
        bn = f'hair_loose_{k}'
        bone(bn, tuple(hp + p), parent=H, rot=r)
        lbox(bn, (-1.5, -12, 0), (3, 12, 0), 'strand')

    # ---------------- arms: round shoulders, hands on the walker grips (solved)
    for side, sx in (('right', -1), ('left', 1)):
        arm, fa, hand = f'{side}_arm', f'{side}_forearm', f'{side}_hand'
        sh = (7.5 * sx, -8.5, 1)
        target = (GRIP_X * sx, GRIP_Y - 2.2, GRIP_Z + 0.4)
        ax, ay, az, fx = solve_arm(B, 'chest', sx, sh, target, (0, 0, 0))
        bone(arm, sh, parent='chest', rot=(ax, ay, az))
        lbox(arm, (-2, -1, -2), (4, 7, 4), 'sleeve')
        bone(fa, (sh[0], sh[1] + UPPER, sh[2]), parent=arm, rot=(fx, 0, 0))
        lbox(fa, (-1.5, 0, -1.5), (3, 5, 3), 'sleeve')
        lbox(fa, (-2, 4, -2), (4, 2, 4), 'cuff')
        wp = B.world(fa, (0, FORE, 0))
        bone(hand, tuple(wp), parent=fa, world=True, wrot=(-12, 0, 0))
        lbox(hand, (-1.5, 0, -1.5), (3, 3, 3), 'hand')
        lbox(hand, (-1.0 if sx < 0 else 0.0, 0.5, -2.2), (1, 2, 1), 'thumb')
        if sx > 0:
            lbox(fa, (-0.5, 5.5, -2.4), (2, 2, 0), 'tissue')

    # held props (toggles)
    bone('mate', tuple(B.world('right_hand', (0, 2, -2.5))), parent='right_hand', world=True, wrot=(0, 0, 0))
    lbox('mate', (-1.5, -4, -1.5), (3, 4, 3), 'gourd')
    lbox('mate', (-1.5, -4.5, -1.5), (3, 1, 3), 'virola', inflate=0.15)
    lbox('mate', (0.3, -8, -0.5), (1, 4, 1), 'bombilla')
    bone('chancleta', tuple(B.world('right_hand', (0, 2.5, 0))), parent='right_hand', world=True)
    lbox('chancleta', (-2.5, -1, -3.5), (5, 2, 7), 'slipper')
    lbox('chancleta', (-3, 1, -4), (6, 1, 8), 'sole')
    bone('needle_right', tuple(B.world('right_hand', (0, 1.5, 0))), parent='right_hand', world=True)
    lbox('needle_right', (-0.5, -0.5, -9), (1, 1, 11), 'needle')
    lbox('needle_right', (-1, -1, 2), (2, 2, 1), 'knob')
    bone('needle_left', tuple(B.world('left_hand', (0, 1.5, 0))), parent='left_hand', world=True)
    lbox('needle_left', (-0.5, -0.5, -9), (1, 1, 11), 'needle')
    lbox('needle_left', (-1, -1, 2), (2, 2, 1), 'knob')
    lbox('needle_left', (-3, 0.5, -8), (6, 7, 1), 'knit')
    bone('yarn_right', tuple(B.world('right_hand', (0, 3, 0))), parent='right_hand', world=True)
    lbox('yarn_right', (-1, 0, 0), (2, 30, 0), 'yarn')
    bone('yarn_left', tuple(B.world('left_hand', (0, 3, 0))), parent='left_hand', world=True)
    lbox('yarn_left', (-1, 0, 0), (2, 30, 0), 'yarn')

    # red wool ball in the cardigan pocket (her left hip)
    bone('yarn_ball', (5, 3.5, -6), parent='body')
    lbox('yarn_ball', (-2, -2, -2), (4, 4, 4), 'ball')

    # ---------------- walker (andador): aluminium U frame, front wheels, cut tennis balls on the back legs
    bone('walker', (0, 24, 0), parent='base')
    gy = GRIP_Y - 24
    for sx in (-1, 1):
        x = GRIP_X * sx
        lbox('walker', (x - 0.5, gy - 0.5, -16), (1, 19.5, 1), 'tube')       # front leg (to the wheel)
        lbox('walker', (x - 0.5, gy - 0.5, -5), (1, 21.5, 1), 'tube')        # back leg (to the tennis ball)
        lbox('walker', (x - 0.5, gy - 0.5, -16), (1, 1, 12), 'tube')         # side rail
        lbox('walker', (x - 1, gy - 1, GRIP_Z - 3), (2, 2, 6), 'grip')      # foam grip
        lbox('walker', (x - 1.5, -3, -6), (3, 3, 3), 'tennis')
    lbox('walker', (-GRIP_X, gy - 0.5, -16), (2 * GRIP_X, 1, 1), 'tube')    # front top bar
    lbox('walker', (-GRIP_X, gy + 9, -16), (2 * GRIP_X, 1, 1), 'tube')      # front low bar
    lbox('walker', (GRIP_X - 0.5, -5, -18), (1, 5, 5), 'wheel')
    bone('walker_wheel', (-GRIP_X, 21.5, -15.5), parent='walker')
    lbox('walker_wheel', (-0.5, -2.5, -2.5), (1, 5, 5), 'wheel')

    # ---------------- rocking chair (light oak, crocheted cushion, doily over the crest)
    bone('rocker', (0, 24, 0), parent='base')
    lbox('rocker', (-9.5, -7.5, -9), (19, 2, 17), 'oak')                   # seat board y 16.5..18.5
    lbox('rocker', (-8.5, -8.5, -8.5), (17, 1, 14), 'cushion')            # y 15.5..16.5
    for sx in (-1, 1):
        x0 = -9.5 if sx < 0 else 8.0
        lbox('rocker', (x0, -5.5, -8.5), (2, 4, 2), 'oak')      # front leg
        lbox('rocker', (x0, -5.5, 5), (2, 4, 2), 'oak')                           # back leg
        lbox('rocker', (x0, -2, -7), (2, 2, 13), 'oak')                           # runner (floor)
        lbox('rocker', (x0, -3, -13), (2, 2, 6), 'oak')                           # runner front tip
        lbox('rocker', (x0, -3, 6), (2, 2, 6), 'oak')                             # runner back
        lbox('rocker', (x0, -4, 12), (2, 2, 3), 'oak')                            # runner back tip
        lbox('rocker', (x0 - (0.5 if sx < 0 else -0.5), -16, -8.5), (2, 1, 14), 'oak')   # arm rest
        lbox('rocker', (x0, -15, -8), (2, 7, 1), 'oak')        # arm post
    bone('rocker_back', (0, 16.5, 6.5), parent='rocker', rot=(-10, 0, 0))
    for sx in (-1, 1):
        x0 = -9.5 if sx < 0 else 8.0
        lbox('rocker_back', (x0, -30, 0), (2, 30, 2), 'oak')
    lbox('rocker_back', (-10.5, -33, -0.5), (21, 4, 3), 'oak')
    lbox('rocker_back', (-7.5, -28, 1), (15, 25, 0), 'slats')

    m = NonaModel('nona', 256, 256, B.r.roots)
    m.scale = 0.5
    if pose is None and os.path.basename(sys.argv[0]) == 'preview.py':
        pose = _argv('--pose')
    m.visible = visible_set(variant, pose)
    return m


DEFAULT_MAT = make_mat('normal')
VARIANT_MATS = {'normal': DEFAULT_MAT, 'poseida': make_mat('poseida')}
FOCUS = 'head'

S = (0, 0, 0, 0, 7, 0)   # seated: hips drop onto the seat
POSES = {
    'stand_walker': {'head': (0, 0, 0.12, 0, 0, 0)},
    'knit_sit': {'body': S, 'right_leg': (-1.57, 0, 0, 0, 0, 0), 'left_leg': (-1.57, 0, 0, 0, 0, 0),
                 'right_shin': (1.57, 0, 0, 0, 0, 0), 'left_shin': (1.57, 0, 0, 0, 0, 0),
                 'skirt_front': (-1.52, 0, 0, 0, 0, 0), 'skirt_hem': (1.57, 0, 0, 0, 0, 0),
                 'skirt_back': (-1.6, 0, 0, 0, 0, 0)},
}

ANIM_NOTES = """WIP"""
