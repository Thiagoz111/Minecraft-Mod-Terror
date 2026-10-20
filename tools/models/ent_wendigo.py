"""El Wendigo -- the starving deer-skull horror of the Bosque Negro (DEAD LINE).

Authored at 2x texel density (model.scale = 0.5): +Y down, ground at y = 24, the creature faces -Z,
right_* parts on -X. Bones are placed in WORLD space for the rest pose with the small `WR` helper below:
every bone gets a world pivot (its joint) and a world orientation, which are converted to MC-local pivots
and Z*Y*X Euler angles. Cubes are authored in each bone's local frame: limb segments run along local +Y
from their joint, spine / neck / antler beams along local -Y.

Silhouette: a crown of huge asymmetric antlers (right one intact with five tines, left one snapped to a
splintered stump) over a cracked deer skull with recessed black orbits and pin-prick pupils; a vulture hump
with jutting shoulder blades on a starved, rib-slatted chest; arms so long that the hooked black claws hang
at the shins; digitigrade knock-kneed legs on cloven hooves. Real size: hump 3.3 blocks, antler tips under
4.0 blocks, centred on the 1.0 x 3.3 hitbox.
"""
import math

import numpy as np

from mcmodel import Model, Bone, Cube, rot_matrix, fbm, vnoise, hash3, face_light, pick
from paint import hx, mix, scale, edge, pixelart


def pal(*h):
    return [hx(c) for c in h]


# ------------------------------------------------------------------ palettes (dark -> light)
SKIN = pal('#0e0a0a', '#1a1413', '#28201e', '#372d2a', '#483c37', '#5b4d46', '#6f5f56', '#857368', '#9c897b', '#b4a191')
FROST = pal('#09080a', '#121014', '#1b181c', '#252126', '#302b30', '#3c363b', '#494248', '#575057', '#686068')
BONE = pal('#17120f', '#2c241d', '#463b2f', '#635543', '#80715a', '#9e8f72', '#bbad8e', '#d5cbab', '#ece5cc')
ANTLER = pal('#120e0c', '#231b16', '#382d23', '#4f4132', '#685644', '#826e58', '#9f8a6f', '#bda98c', '#dacbaf')
FUR = pal('#070505', '#0f0b0a', '#191311', '#241b17', '#30251f', '#3e3028', '#4e3e34', '#615042')
FLESH = pal('#160607', '#290b0c', '#3f1213', '#581c1a', '#722823', '#8b392e', '#a44d3c')
BLOOD = pal('#120203', '#200405', '#310709', '#450b0d', '#5a1012', '#701618')     # dried, near black
FRESH = pal('#2a0306', '#4a070c', '#6c0d12', '#8e1418', '#ae1f1d', '#c93226')     # wet: mouth, chest
CLAW = pal('#030304', '#08070a', '#0f0d12', '#17141b', '#211d26', '#2d2833', '#3d3745')
GAP = pal('#040202', '#0a0505', '#120808', '#1b0d0c', '#251412')
VOID = hx('#030102')
VEIN = hx('#2a2030')
RIM = hx('#8c98b2')          # cold moonlight rim on upward faces (survives the night shot)
CLAW_HI = hx('#a6a0b6')
EYE_WH = hx('#f4f8ff')
EYE_HALO = hx('#26324c')


# ------------------------------------------------------------------ world-space rig helper
def R3(x=0.0, y=0.0, z=0.0):
    return rot_matrix(math.radians(x), math.radians(y), math.radians(z))


def euler_zyx(R):
    """Inverse of mcmodel.rot_matrix (R = Rz*Ry*Rx) -> degrees (x, y, z)."""
    sy = max(-1.0, min(1.0, -R[2, 0]))
    y = math.asin(sy)
    if abs(sy) > 0.9999:
        x, z = math.atan2(-R[1, 2], R[1, 1]), 0.0
    else:
        x, z = math.atan2(R[2, 1], R[2, 2]), math.atan2(R[1, 0], R[0, 0])
    return tuple(round(math.degrees(v), 3) for v in (x, y, z))


def aim(p, q, twist=0.0):
    """World rotation whose local +Y runs from p toward q (then twisted about it); returns (R, length)."""
    d = np.array(q, float) - np.array(p, float)
    L = float(np.linalg.norm(d))
    d /= L
    rx = math.asin(max(-1.0, min(1.0, d[2])))
    rz = math.atan2(-d[0], d[1])
    return rot_matrix(0, 0, rz) @ rot_matrix(rx, 0, 0) @ R3(0, twist, 0), L


def aim_up(p, q, twist=0.0):
    """World rotation whose local -Y runs from p toward q (beams, tines growing 'up' from their base)."""
    d = np.array(q, float) - np.array(p, float)
    L = float(np.linalg.norm(d))
    d /= L
    rx = math.asin(max(-1.0, min(1.0, -d[2])))
    rz = math.atan2(d[0], -d[1])
    return rot_matrix(0, 0, rz) @ rot_matrix(rx, 0, 0) @ R3(0, twist, 0), L


class WR:
    def __init__(self):
        self.bones, self.M, self.roots = {}, {}, []

    def bone(self, name, parent, wp, R=None, mat=None, flen=None):
        R = np.eye(3) if R is None else np.asarray(R, float)
        wp = np.array(wp, float)
        if parent:
            Mp = self.M[parent]
            rel = Mp[:3, :3].T @ (wp - Mp[:3, 3])
            ex = euler_zyx(Mp[:3, :3].T @ R)
        else:
            rel, ex = wp, euler_zyx(R)
        b = Bone(name, tuple(round(float(v), 4) for v in rel), ex, mat=mat)
        if flen:
            b.flen = flen
        M = np.eye(4)
        M[:3, 3] = b.pivot
        M[:3, :3] = rot_matrix(*[math.radians(a) for a in ex])
        if parent:
            self.bones[parent].add(b)
            M = self.M[parent] @ M
        else:
            self.roots.append(b)
        self.bones[name], self.M[name] = b, M
        return b

    def lbone(self, name, parent, lp, rot=(0, 0, 0), mat=None, flen=None):
        """Bone placed in its parent's local frame (pivot lp, extra local rotation in degrees)."""
        Mp = self.M[parent]
        return self.bone(name, parent, (Mp @ np.array([*lp, 1.0]))[:3], Mp[:3, :3] @ R3(*rot), mat, flen)

    def wp(self, name, p):
        return (self.M[name] @ np.array([*p, 1.0]))[:3]

    def lp(self, name, w):
        """World point -> local point of a bone."""
        M = self.M[name]
        return M[:3, :3].T @ (np.array(w, float) - M[:3, 3])

    def box(self, name, frm, size, mat=None, inflate=0.0, decals=None):
        c = Cube(tuple(float(v) for v in frm), size, mat=mat, inflate=inflate, decals=decals)
        self.bones[name].cubes.append(c)
        return c

    def mbox(self, name, s, frm, size, **kw):
        """Box described for the right side (-X); mirrored to +X when s > 0."""
        if s > 0:
            frm = (-(frm[0] + size[0]), frm[1], frm[2])
        return self.box(name, frm, size, **kw)


def mirror_pt(p, s):
    return (p[0] * (1 if s < 0 else -1), p[1], p[2])


# ------------------------------------------------------------------ texel helpers
def local(ctx):
    """Texel centre in the cube's bone frame (relative to the bone pivot)."""
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


def light(ctx, k=1.0):
    return face_light(ctx) * k


def is_side(ctx):
    return ctx.face not in ('top', 'bottom')


def flat(ctx):
    return 0 in ctx.cube.size


def up_facing(ctx):
    return ctx.n[1] < -0.55


def wcol(ctx):
    """Horizontal texel coordinate that wraps continuously around a cube's four sides."""
    w, h, d = ctx.cube.size
    f = ctx.face
    if f == 'front':
        return ctx.i
    if f == 'east':
        return w + ctx.i
    if f == 'back':
        return w + d + ctx.i
    if f == 'west':
        return 2 * w + d + ctx.i
    return ctx.i


def bands(n, lo=0.4, hi=0.6, amt=0.07):
    return amt if n > hi else (-amt if n < lo else 0.0)


def drip_len(col, seed, lo, length):
    h = hash3(col, 0, 0, seed)
    if h < lo:
        return -1.0
    return 1.0 + (h - lo) / (1 - lo) * length


def sub(ramp, a, b, v):
    """Pick from ramp[a..b] with v in 0..1."""
    return pick(ramp[a:b + 1], v)


def rim(ctx, c, k=1.0):
    """Cold grey-blue moonlight: a bright 1-px lip on upward faces, a faint wash inside them, and the
    top row of side faces."""
    if up_facing(ctx):
        return mix(c, RIM, (0.1 + (0.24 if edge(ctx) == 0 else 0.0)) * k)
    if is_side(ctx) and not flat(ctx) and ctx.j == 0 and ctx.n[1] < 0.3:
        return mix(c, RIM, 0.16 * k)
    return c


def dried(v):
    return sub(BLOOD, 1, 4, v)


# ------------------------------------------------------------------ hide (skin)
EXTREMITY = {'_arm': (0.0, 0.08), '_forearm': (0.1, 0.45), '_hand': (0.5, 0.7), '_leg': (0.0, 0.05),
             '_shin': (0.05, 0.35), '_foot': (0.35, 0.6)}
CREASES = {'_arm': (-6, -3), '_leg': (-7, -4), '_shin': (-6,), '_forearm': (-6,)}


def frost(ctx):
    """0..1: frostbitten / necrotic darkening toward the hands and hooves (along the bone axis)."""
    n = ctx.bone.name
    for suf, (a, b) in EXTREMITY.items():
        if n.endswith(suf):
            ln = getattr(ctx.bone, 'flen', 20.0)
            t = max(0.0, min(1.0, local(ctx)[1] / ln))
            return a + (b - a) * t
    return 0.0


def crease(ctx, v):
    """Curved dark wrinkle lines with a lit lip under them (above elbows, knees, hocks)."""
    if not is_side(ctx) or flat(ctx) or ctx.h < 6:
        return v
    n = ctx.bone.name
    rows = None
    for suf, rr in CREASES.items():
        if n.endswith(suf):
            rows = rr
    if rows is None:
        return v
    ln = getattr(ctx.bone, 'flen', 0.0)
    ly = math.floor(local(ctx)[1])
    col = wcol(ctx)
    for k, r in enumerate(rows):
        yc = math.floor(ln + r + 1.3 * math.sin(col * 0.42 + k * 2.3))
        if ly == yc and hash3(col, k, 0, 77) > 0.15:
            return v - 0.16
        if ly == yc + 1:
            v += 0.06
    return v


def hide_value(ctx, base=0.57):
    x, y, z = ctx.pos
    v = base + light(ctx, 1.0)
    if not flat(ctx) and edge(ctx) == 0:
        v -= 0.06
    n = fbm(x * 0.075 + 3, y * 0.075, z * 0.075, 2, 11)       # broad value groups, not static
    v += 0.07 if n > 0.6 else (-0.06 if n < 0.38 else 0.0)
    m = fbm(x * 0.22, y * 0.22, z * 0.22, 2, 12)              # mottled, uneven hide
    v += 0.05 if m > 0.63 else (-0.08 if m < 0.35 else 0.0)
    return v


ROT = hx('#2b2430')        # bruised, rotting patches
PALE = hx('#a89a8c')       # hide stretched thin and pale over bone


def hide_color(ctx, v):
    x, y, z = ctx.pos
    fr = frost(ctx)
    c = pick(SKIN, v)
    if fr > 0:
        c = mix(c, pick(FROST, v + 0.05), fr)
    q = fbm(x * 0.12 + 7, y * 0.12, z * 0.12, 2, 14)
    if q < 0.33:
        c = mix(c, ROT, 0.35)
    elif q > 0.7 and fr < 0.3:
        c = mix(c, PALE, 0.18)
    return c


def hide_mat(ctx):
    """Grey-brown leathery hide stretched over bone."""
    v = hide_value(ctx)
    name = ctx.bone.name
    side = is_side(ctx)
    if side and not flat(ctx):
        v -= ctx.t * 0.05                      # occlusion toward the far end of the segment
    v = crease(ctx, v)
    if ctx.face in ('front', 'back') and name.endswith(('_shin', '_forearm')) and ctx.w >= 5 and ctx.h >= 8:
        c0 = ctx.w // 2 - 1                    # tibia / ulna pressing through, off-centre
        if ctx.i == c0:
            v += 0.1
        elif ctx.i == c0 + 1:
            v -= 0.07
    c = hide_color(ctx, v)
    if name.endswith(('_arm', '_forearm', '_shin', '_leg')) and side and ctx.h >= 10 and ctx.face in ('front', 'east', 'west'):
        seed = int(hash3(ctx.cube.size[1], ctx.w, ord(ctx.face[0]), 9) * 100)
        vc = int(ctx.w * 0.3 + 1.4 * math.sin(ctx.j * 0.33 + seed))
        if ctx.i == vc and 0.12 < ctx.t < 0.8 and hash3(seed, 0, 0, 1) > 0.4:
            c = mix(c, VEIN, 0.5)
    if name.endswith('_forearm') and side and ctx.cube.origin[1] > 10:
        col = wcol(ctx) + int(hash3(*ctx.cube.size, 3) * 50)
        L = drip_len(col, 13, 0.62, 4)        # a few dried drips running up from the wrist
        if L > 0 and ctx.h - 1 - ctx.j < L:
            c = dried(0.5)
    return rim(ctx, c)


def knob_mat(ctx, boost=0.0):
    """Knotted joint in the hide colour: lit top only, a pale bone glint at the apex."""
    v = hide_value(ctx, 0.56 + boost)
    top = up_facing(ctx) or (is_side(ctx) and ctx.j == 0)
    if top:
        v += 0.08
    c = hide_color(ctx, v)
    if up_facing(ctx) and abs(ctx.s - 0.5) < 0.3 and abs(ctx.t - 0.5) < 0.35:
        c = mix(c, BONE[6], 0.55)
    elif is_side(ctx) and ctx.j == 0 and abs(ctx.s - 0.5) < 0.25:
        c = mix(c, BONE[6], 0.4)
    return rim(ctx, c, 0.7)


def knob(boost):
    return lambda ctx: knob_mat(ctx, boost)


def vert_mat(ctx):
    """Spinous process pushing through the hide: pale bone cap, hide-toned sides."""
    v = hide_value(ctx, 0.6)
    if up_facing(ctx) or ctx.face == 'back':
        return sub(BONE, 4, 7, 0.5 + light(ctx, 0.6) + (0.15 if edge(ctx) else -0.1))
    if is_side(ctx) and ctx.j == 0:
        v += 0.1
    return rim(ctx, mix(pick(SKIN, v), pick(BONE, v - 0.05), 0.45))


def cage_mat(ctx):
    """Ribcage core: dark hide sunk between the rib slats; rib ridges show through on the flanks."""
    x, y, z = ctx.pos
    if ctx.face == 'front':
        v = 0.30 + light(ctx, 0.5) + bands(fbm(x * 0.3, y * 0.3, z * 0.3, 2, 3), 0.4, 0.6, 0.06)
        return pick(SKIN, v)
    c = hide_mat(ctx)
    if ctx.face in ('east', 'west'):
        lx, ly, lz = local(ctx)
        r = (ly + 0.45 * (lz + 7)) % 4.0         # rib ridges sloping back and down
        if r < 1.0:
            return scale(c, 0.62)
        if r < 2.0:
            return rim(ctx, scale(c, 1.2))
    return c


def back_mat(ctx):
    """Hump and back: hide with the spine groove and rib ridges fanning out from it."""
    c = hide_mat(ctx)
    lx, ly, lz = local(ctx)
    ax = abs(lx)
    if ctx.face == 'back':
        if ax < 1.0:
            return scale(c, 0.6)
        if ax < 2.0:
            return scale(c, 1.12)
    if ctx.face in ('back', 'east', 'west') and ax > 3.5:
        r = (ly + 0.4 * ax + 0.25 * lz) % 4.5
        if r < 1.0:
            return scale(c, 0.64)
        if r < 2.2:
            return scale(c, 1.14)
    return c


def rib_mat(ctx):
    """A rib slat: hide shrink-wrapped over bone, pale lit top edge, shadowed underside."""
    x, y, z = ctx.pos
    if ctx.face == 'bottom':
        return SKIN[1]
    if ctx.face == 'top':
        c = mix(pick(SKIN, 0.75 + light(ctx, 0.3)), BONE[6], 0.45)
        return rim(ctx, c, 0.6)
    if ctx.face == 'front':
        if ctx.j == 0:
            c = mix(SKIN[7], BONE[6], 0.5 + bands(hash3(x // 2, y, z // 2, 8), 0.4, 0.6, 0.3))
        elif ctx.j == ctx.h - 1:
            c = SKIN[2]
        else:
            c = pick(SKIN, 0.55 + light(ctx, 0.6))
        if abs(x) < 4.5:                       # blood from the mouth has run down the breastbone
            L = drip_len(math.floor(x), 401, 0.3, 4)
            if L > 0 and hash3(math.floor(x), math.floor(y), 0, 402) > 0.3:
                c = sub(FRESH, 1, 4, 0.35 + ctx.j * 0.2)
        return c
    return SKIN[3]


def sternum_mat(ctx):
    x, y, z = ctx.pos
    v = 0.62 + light(ctx, 0.9)
    if is_side(ctx) and edge(ctx) == 0:
        v -= 0.08
    c = mix(pick(SKIN, v), pick(BONE, v - 0.08), 0.5)
    if ctx.face == 'front' and hash3(math.floor(x), 0, 0, 403) > 0.2:
        c = sub(FRESH, 1, 4, 0.6 - ctx.t * 0.45)       # fresh blood down the breastbone
    return c


def neck_mat(ctx):
    """Neck: hide with cords of tendon on the sides."""
    c = hide_mat(ctx)
    if ctx.face in ('west', 'east') and ctx.i % 3 == 1:
        return scale(c, 0.8)
    return c


def finger_mat(ctx):
    """Frostbitten grey-black fingers: dark knuckle bands, a few dried drips at the tips."""
    lx, ly, lz = local(ctx)
    v = 0.5 + light(ctx, 1.0)
    if is_side(ctx) and not flat(ctx) and edge(ctx) == 0:
        v -= 0.06
    c = pick(FROST, v)
    if ctx.cube.size[0] == 3:                  # knuckle knot
        c = pick(FROST, v + 0.12) if (up_facing(ctx) or ctx.j == 0) else pick(FROST, v - 0.18)
    elif is_side(ctx) and int(ly) in (4, 11):
        c = pick(FROST, v - 0.25)              # dark wrinkle band
    elif is_side(ctx) and ly > 12.5 and hash3(wcol(ctx), ctx.cube.size[1], 1, 45) > 0.55:
        c = dried(0.5)
    return rim(ctx, c, 0.6)


# ------------------------------------------------------------------ bone, skull, mouth
def bone_value(ctx, p, base=0.62):
    x, y, z = p
    v = base + light(ctx, 1.0)
    if not flat(ctx) and edge(ctx) == 0:
        v -= 0.09
    v += bands(fbm(x * 0.13, y * 0.13, z * 0.13, 2, 21), 0.36, 0.66, 0.05)
    return v


def skull_mat(ctx):
    p = ctx.pos
    x, y, z = p
    v = bone_value(ctx, p)
    if ctx.face == 'bottom':
        v -= 0.15
    if is_side(ctx):
        v -= ctx.t * 0.06
    c = pick(BONE, v)
    if hash3(x, y, z, 23) > 0.975:
        c = pick(BONE, v - 0.28)                 # pits
    if fbm(x * 0.17, y * 0.17, z * 0.17, 2, 24) > 0.68:
        c = mix(c, hx('#4b3122'), 0.3)           # tannin stains
    return c


# eye sockets: slanted ellipses on the cranium front (head-local x, y) that wrap round onto the skull sides
SOCK_C = ((-7.4, -9.4, -1), (7.4, -9.4, 1))
SOCK_R = (3.9, 4.7)
SOCK_TILT = 0.30           # the outer corner droops: hollow, starving, not an angry frown
PUPILS = ((-6.5, -8.5), (7.5, -9.5))   # tiny, low-inner, slightly asymmetric (one looks past you)
CRANIUM_FRONT_Z = -15.0
RIM_FRONT_Z = -18.5


def sock_d(x, y):
    """Normalised distance to the nearest socket centre (< 1 inside the orbit)."""
    best = 9.0
    for cx, cy, s in SOCK_C:
        dx, dy = (x - cx) * -s, y - cy          # dx > 0 = toward the nose
        u = dx * math.cos(SOCK_TILT) + dy * math.sin(SOCK_TILT)
        v = -dx * math.sin(SOCK_TILT) + dy * math.cos(SOCK_TILT)
        best = min(best, math.hypot(u / SOCK_R[0], v / SOCK_R[1]))
    return best


def socket_color(d, base):
    if d < 0.62:
        return VOID
    if d < 0.8:
        return GAP[0]
    if d < 0.93:
        return BONE[1]
    if d < 1.06:
        return BONE[2]
    if d < 1.2:
        return mix(base, BONE[3], 0.6)
    return base


def orbit_mat(ctx):
    """Brow ridges, cheekbones, nasal bridge: lit lips, cavity walls fading to black inside the orbit."""
    p = local(ctx)
    c = skull_mat(ctx)
    if ctx.face != 'front' and sock_d(p[0], p[1]) < 1.15:
        depth = (p[2] - RIM_FRONT_Z) / (CRANIUM_FRONT_Z - RIM_FRONT_Z)
        return sub(BONE, 0, 3, 0.8 - depth * 0.9)
    if up_facing(ctx) or (ctx.face == 'front' and ctx.j == 0):
        c = mix(c, BONE[7], 0.5)
    elif ctx.face == 'front' and ctx.j == ctx.h - 1:
        c = mix(c, BONE[2], 0.5)
    return c


def cranium_mat(ctx):
    p = local(ctx)
    c = skull_mat(ctx)
    if ctx.face == 'front':
        return socket_color(sock_d(p[0], p[1]), c)
    if ctx.face in ('west', 'east'):
        sx = -1 if ctx.face == 'west' else 1
        x_eff = sx * (11.0 + max(0.0, p[2] - CRANIUM_FRONT_Z) * 1.1)     # the orbit wraps round the corner
        return socket_color(sock_d(x_eff, p[1]), c)
    if up_facing(ctx):
        c = mix(c, BONE[7], 0.25)
    return c


def muzzle_mat(ctx):
    """Snout: bone outside, raw gums on the underside (seen when the jaw drops), blood at the lips."""
    p = ctx.pos
    if ctx.face == 'bottom':
        if ctx.i in (0, ctx.w - 1):
            return sub(FRESH, 0, 2, 0.5)
        lz = local(ctx)[2]
        if int(lz) % 3 == 0:
            return FLESH[1]                      # palatal ridges
        return pick(FLESH, 0.45 + bands(fbm(p[0] * 0.4, 0, p[2] * 0.4, 2, 51), 0.4, 0.6, 0.15))
    c = skull_mat(ctx)
    if up_facing(ctx):
        c = mix(c, BONE[7], 0.3)
    if is_side(ctx) and ctx.j >= ctx.h - 2:
        col = math.floor(p[2] if ctx.face in ('west', 'east') else p[0])
        if hash3(col, 0, 0, 57) > 0.35:
            c = sub(FRESH, 1, 3, 0.5)            # lips of blood along the tooth row
    return c


def jaw_mat(ctx):
    """Mandible ramus: bone sides, a row of molars on top (faces the camera when the jaw drops),
    fresh blood only toward the chin."""
    p = ctx.pos
    lz = local(ctx)[2]
    if ctx.face == 'top':
        k = ctx.j % 3
        if k == 2:
            return GAP[0]
        return BONE[7] if k == 0 else (BONE[5] if hash3(ctx.i, ctx.j, 0, 53) > 0.25 else FRESH[1])
    c = skull_mat(ctx)
    if is_side(ctx) and lz < -13:
        col = math.floor(p[2] * 2) if ctx.face in ('west', 'east') else math.floor(p[0]) + 40
        L = drip_len(col, 59, 0.45, 3)
        if L > 0 and ctx.j < L:
            c = sub(FRESH, 1, 4, 0.6 - ctx.j * 0.15)
        elif L > 0 and ctx.j < L + 1 and hash3(col, 1, 0, 59) > 0.5:
            c = FRESH[3]
    return c


def chin_mat(ctx):
    if ctx.face == 'top':
        return sub(FLESH, 2, 5, 0.5 + bands(hash3(ctx.i, 0, 0, 62), 0.3, 0.7, 0.3))
    c = skull_mat(ctx)
    col = wcol(ctx)
    if is_side(ctx):
        L = 1.5 + hash3(col, 0, 0, 61) * 3.2
        if ctx.j < L or (ctx.face == 'front' and hash3(col, 1, 0, 61) > 0.6):
            c = sub(FRESH, 1, 4, 0.75 - ctx.j * 0.18)   # chin soaked, drips ending in droplets
        elif ctx.j < L + 1.2 and hash3(col, 2, 0, 61) > 0.5:
            c = FRESH[3]
    return c


def mouth_mat(ctx):
    """Floor of the mouth (faces the camera when the jaw drops): lower teeth at the chin, a lolling
    tongue and a black gullet."""
    if ctx.face != 'top':
        return jaw_mat(ctx) if ctx.face != 'bottom' else skull_mat(ctx)
    i, j, w, h = ctx.i, ctx.j, ctx.w, ctx.h
    front = h - 1 - j                          # 0 = the chin end
    if front < 4:                              # lower teeth growing toward the gullet (up when open)
        L = 2 + int(hash3(i, 0, 0, 71) * 2.6) if i % 2 == 0 else 1
        if front < L and not (front == 0 and i % 2):
            return BONE[7] if front < L - 1 else BONE[5]
        return VOID if front > 1 else FRESH[1]
    ci = abs(i - (w - 1) / 2)
    t = (front - 4) / max(1, h - 4)
    if ci < 2.0 and t < 0.75:                   # tongue
        if ci > 1.2 and t > 0.45:
            return GAP[1]
        return sub(FLESH, 1, 4, 0.65 - t * 0.7 + (0.12 if ci < 0.6 else 0))
    if t < 0.25 and hash3(i, j, 0, 73) > 0.55:
        return FRESH[0]
    return VOID if hash3(i, j, 1, 73) > 0.12 else GAP[1]


def tooth_mat(ctx):
    """Cube teeth: yellowed enamel with a bleeding root."""
    lx, ly, lz = local(ctx)
    v = 0.78 + light(ctx, 0.4)
    c = pick(BONE, v - ctx.t * 0.15)
    if ctx.face in ('top', 'bottom'):
        return BONE[7]
    if hash3(*ctx.cube.origin, 5) > 0.6 and ctx.t < 0.3:
        c = sub(FRESH, 1, 3, 0.5)
    return c


def teeth_mat(root_y, maxlen, axis, seed, canines=(), grow=1):
    """Jagged teeth on a zero-thickness plane; gum line at local y=root_y, teeth grow along +y (grow=1)."""
    def f(ctx):
        lx, ly, lz = local(ctx)
        col = math.floor(lx if axis == 'x' else lz)
        h = hash3(col, 0, 0, seed)
        if col in canines:
            L = maxlen
        elif h < 0.2:
            L = 0.8                                   # missing tooth
        else:
            L = 1.5 + ((h - 0.2) / 0.8) ** 1.3 * (maxlen - 2.3)
        depth = (ly - root_y) * grow
        if depth < 0 or depth > L:
            return None
        if depth < 1.0:
            return sub(FRESH, 0, 2, h)                # bleeding gum line
        t = depth / max(1.0, L)
        if hash3(col, 3, 0, seed) > 0.72 and depth < 1.0 + hash3(col, 4, 0, seed) * L * 0.6:
            return sub(FRESH, 1, 3, 0.4 + t * 0.3)   # blood caked from the roots down
        v = 0.92 - t * 0.25 + light(ctx, 0.3) - (0.22 if hash3(col, 5, 0, seed) > 0.8 else 0)
        if col % 2 == 0 and t > 0.3:
            v -= 0.12                                 # gap shading between teeth
        return pick(BONE, v)
    return f


def string_mat(seed):
    """Strings of bloody drool (zero-thickness, ragged, mostly transparent)."""
    def f(ctx):
        lx, ly, lz = local(ctx)
        c = ctx.cube
        col = math.floor(lx)
        h = hash3(col, 0, 0, seed)
        if h < 0.45 or col % 2:
            return None
        depth = ly - c.origin[1]
        L = c.size[1] * (0.35 + 0.65 * (h - 0.45) / 0.55)
        if depth > L:
            return None
        if depth > L - 1:
            return FRESH[3]                           # droplet
        return sub(FRESH, 0, 3, 0.7 - depth / c.size[1] * 0.5)
    return f


# ------------------------------------------------------------------ antlers, claws, hooves
def antler_mat(ctx):
    x, y, z = ctx.pos
    n = ctx.bone.name
    v = 0.52 + light(ctx, 1.1)
    if 'tine' in n:
        v += (1 - ctx.t) * 0.08 if is_side(ctx) else 0.08
    if not flat(ctx) and edge(ctx) == 0:
        v -= 0.08
    if is_side(ctx) and ctx.w >= 3 and hash3(ctx.i, ctx.cube.size[1], ctx.cube.size[0], 61) > 0.62:
        v -= 0.1                                  # longitudinal grooves
    v += bands(vnoise(x * 0.5, y * 0.5, z * 0.5, 62), 0.35, 0.65, 0.05)
    c = pick(ANTLER, v)
    if is_side(ctx) and ctx.j <= 0:
        c = mix(c, ANTLER[8], 0.35)
    return rim(ctx, c, 1.2)


def antler_tip_mat(ctx):
    """Polished tine points: pale, lit (survive the night shot)."""
    v = 0.55 + light(ctx, 0.8) + (0.3 if (is_side(ctx) and ctx.j == 0) or ctx.face == 'top' else 0)
    return sub(ANTLER, 6, 8, v)


def burr_mat(ctx):
    p = ctx.pos
    v = 0.36 + light(ctx, 1.0) + bands(hash3(p[0], p[1], p[2], 63), 0.35, 0.65, 0.12)
    return pick(ANTLER, v)


def broken_mat(ctx):
    """Antler snapped off: pale splintered core on the top, jagged rim."""
    if ctx.face == 'top':
        e = edge(ctx)
        if e >= 1:
            return BONE[7] if hash3(ctx.i, ctx.j, 0, 64) > 0.3 else BONE[5]
        return BONE[4] if hash3(ctx.i, ctx.j, 1, 64) > 0.4 else None
    if is_side(ctx) and ctx.j <= 1:
        if ctx.j == 0 and hash3(ctx.i, 0, ord(ctx.face[0]), 65) < 0.45:
            return None
        return BONE[6]
    return antler_mat(ctx)


def splinter_mat(ctx):
    """A snapped rib punching out through the hide: blood ring at the root, pale splintered tip."""
    lx = local(ctx)[0]
    v = bone_value(ctx, ctx.pos, 0.66)
    if lx < 1.5:
        return sub(FRESH, 1, 3, 0.5 + light(ctx, 0.5))
    if lx < 2.5:
        return dried(0.5)
    return BONE[8] if ctx.face == 'east' else pick(BONE, v)


def claw_mat(ctx):
    """Glossy black hooked claw: 1-px specular line on the outer curve, bright tip, blood at the root."""
    lx, ly, lz = local(ctx)
    v = 0.42 + light(ctx, 1.0)
    c = pick(CLAW, v)
    size = ctx.cube.size
    if size[0] == 2 and ly < 2.5 and is_side(ctx):
        return dried(0.35 + ctx.t * 0.2) if ctx.t < 0.7 else c     # blood caked at the root
    if ctx.face == 'front' and ctx.i == 0:
        c = CLAW_HI                                 # glossy outer curve
    elif ctx.face in ('west', 'east') and ctx.i == ctx.w - 1 and size[0] == 2:
        c = pick(CLAW, 0.85)
    if size[0] == 1 and ctx.t > 0.75 and is_side(ctx):
        c = CLAW_HI                                 # specular point
    return c


def hoof_mat(ctx):
    p = ctx.pos
    v = 0.4 + light(ctx, 1.1) + bands(hash3(p[0], p[1] // 2, p[2], 72), 0.3, 0.7, 0.06)
    if is_side(ctx) and ctx.j == 0:
        v += 0.25
    if ctx.face == 'bottom':
        return pick(CLAW, 0.1)
    return rim(ctx, pick(CLAW, v), 0.8)


# ------------------------------------------------------------------ fur / flaps
def clump_mat(seed, ragged=0.6):
    """A matted tuft of fur: solid on top, strands of random length hanging toward local +y."""
    def f(ctx):
        if ctx.face == 'bottom':
            return None
        c = ctx.cube
        lx, ly, lz = local(ctx)
        depth = (ly - c.origin[1]) / c.size[1]
        if ctx.face == 'top':
            col, depth = ctx.i + 40, 0.0
        else:
            col = math.floor(lx) if ctx.face in ('front', 'back') else math.floor(lz) + 20
        lim = 1.0 - ragged * hash3(col, 0, 0, seed)
        if depth > lim:
            return None
        v = 0.36 + hash3(col // 2, 1, 0, seed) * 0.3 + depth * 0.2 + light(ctx, 0.9)
        if col % 3 == 0:
            v -= 0.12
        if depth > lim - 0.12:
            v += 0.1
        return rim(ctx, pick(FUR, v), 0.3)
    return f


def fur_plane(seed, solid=0.25):
    """Rotten matted fur hanging off bone (zero-thickness plane): strands with ragged ends."""
    def f(ctx):
        lx, ly, lz = local(ctx)
        c = ctx.cube
        col = math.floor(lx)
        depth = (ly - c.origin[1]) / c.size[1]
        h = hash3(col, 0, 0, seed)
        lim = solid + (1 - solid) * h
        if depth > lim or (col % 4 == 3 and depth > solid * 0.6):
            return None
        v = 0.4 + hash3(col // 2, 1, 0, seed) * 0.28 - depth * 0.15 + light(ctx, 0.4)
        if col % 3 == 0:
            v -= 0.12
        if depth > lim - 0.08:
            v += 0.12
        return pick(FUR, v)
    return f


def flap_mat(seed=97, kind='skin'):
    """Hanging torn hide (zero-thickness plane): ragged hem, raw red edge, dark creases."""
    def f(ctx):
        lx, ly, lz = local(ctx)
        c = ctx.cube
        depth = ly - c.origin[1]
        col = math.floor(lx)
        h = hash3(col, 0, 0, seed)
        lim = c.size[1] * (0.45 + 0.55 * h)
        if depth > lim or (hash3(col, 1, 0, seed) < 0.12 and depth > 2):
            return None
        v = 0.5 + light(ctx, 0.5) - depth / c.size[1] * 0.18
        if kind == 'velvet':
            if depth > lim - 1.2:
                return sub(FLESH, 2, 4, 0.5)
            return pick(FUR, v + 0.1 + (col % 2) * 0.1)
        if depth > lim - 1.6:
            return sub(FLESH, 2, 5, v + 0.1)          # raw torn hem
        if (col + int(depth * 0.5)) % 4 == 0:
            v -= 0.12
        return pick(SKIN, v)
    return f


# ------------------------------------------------------------------ pixel-art decals
SOCK_PAL = {'K': VOID, '1': BONE[1], '2': BONE[2], '3': BONE[3], '4': BONE[4], '7': BONE[7], 'r': BLOOD[2],
            'R': FRESH[2]}
# head-local pupil centres (x, y) on the cranium front face; slightly asymmetric
PUPILS = ((-7.5, -8.5), (7.5, -9.5))


def cranium_front_decal(img, u0, v0, w, h):
    """Cranium front: pin-prick pupils deep in the sockets, a crack from the left orbit to the crown."""
    px = img.load()
    for x, y in PUPILS:
        px[u0 + int(x + w / 2), v0 + int(y + h)] = EYE_WH
    for i, j in ((15, 0), (15, 1), (16, 2), (16, 3)):
        if 0 <= i < w and 0 <= j < h:
            px[u0 + i, v0 + j] = BONE[1]


def eyes_decal(img, u0, v0, w, h):
    """Emissive layer: 1x1 white core with a dim cold halo on two sides only (asymmetric glints)."""
    px = img.load()
    for k, (x, y) in enumerate(PUPILS):
        i, j = int(x + w / 2), int(y + h)
        px[u0 + i, v0 + j] = EYE_WH
        for di, dj in (((-1, 0), (0, 1)), ((1, 0), (0, -1)))[k]:
            px[u0 + i + di, v0 + j + dj] = EYE_HALO


def nasal_decal(img, u0, v0, w, h):
    """Snout tip front: a big black nasal aperture (inverted pear) with a snapped septum."""
    rows = [
        "2KKKK2",
        "1KKKK1",
        "1K1KK1",
        "21KK12",
        ".2K12.",
        "..22..",
    ]
    pixelart(rows, SOCK_PAL, anchor='topleft', dx=(w - 6) // 2, dy=0)(img, u0, v0, w, h)


def bridge_decal(img, u0, v0, w, h):
    """Nasal bridge front: a crack and the frontal suture."""
    px = img.load()
    path = [(w // 2 + 1, 0), (w // 2 + 1, 1), (w // 2, 2), (w // 2, 3), (w // 2 + 1, 4), (w // 2 + 2, 5),
            (w // 2 + 2, 6), (w // 2 + 1, 7)]
    for i, j in path:
        if 0 <= i < w and 0 <= j < h:
            px[u0 + i, v0 + j] = BONE[1]
    for i, j in ((w // 2 + 2, 2), (w // 2 - 1, 5)):
        px[u0 + i, v0 + j] = BONE[3]


def muzzle_top_decal(img, u0, v0, w, h):
    """Nasal bones from above: centre seam and a hairline crack (top face: high j = front)."""
    px = img.load()
    for j in range(h):
        if j % 5 != 4:
            px[u0 + w // 2, v0 + j] = BONE[3]
    for i, j in ((w // 2 + 1, 3), (w // 2 + 2, 4), (w // 2 + 2, 5), (w // 2 + 3, 6)):
        if i < w:
            px[u0 + i, v0 + j] = BONE[1]


def crown_decal(img, u0, v0, w, h):
    """Crack continuing over the crown (top face: high j = front)."""
    px = img.load()
    path = [(w - 6, h - 1), (w - 6, h - 2), (w - 7, h - 3), (w - 7, h - 4), (w - 8, h - 5), (w - 8, h - 6),
            (w - 9, h - 7), (w - 9, h - 8)]
    for i, j in path:
        if 0 <= i < w and 0 <= j < h:
            px[u0 + i, v0 + j] = BONE[1]


def gash_decal(img, u0, v0, w, h):
    rows = [
        "..ffff..",
        ".fGGGGf.",
        "fGGGGGGf",
        ".fhffff.",
    ]
    p = {'f': FLESH[3], 'G': GAP[0], 'h': FLESH[6]}
    pixelart(rows, p, anchor='topleft', dx=1, dy=4)(img, u0, v0, w, h)


def bite_decal(img, u0, v0, w, h):
    rows = [
        ".K.K.K.",
        "KfffffK",
        ".fFFFf.",
        "KfFGFfK",
        ".fFFFf.",
        "KfffffK",
        ".K.K.K.",
    ]
    p = {'K': GAP[0], 'f': FLESH[2], 'F': FLESH[4], 'G': GAP[1]}
    pixelart(rows, p, anchor='center')(img, u0, v0, w, h)


def tear_decal(img, u0, v0, w, h):
    """Flank: torn hide around the splintered rib's exit wound."""
    rows = [
        "..fff...",
        ".fFFFf..",
        "fFGGGFf.",
        "fGGGGGFf",
        "fFGGGFf.",
        ".fFFf...",
        "..r.r...",
        "..r.....",
    ]
    p = {'f': FLESH[2], 'F': FLESH[4], 'G': GAP[0], 'r': BLOOD[3]}
    pixelart(rows, p, anchor='center', dx=1, dy=-3)(img, u0, v0, w, h)


# ------------------------------------------------------------------ build
ZOFF = 12.0         # global depth shift that centres the hunched body on the hitbox

LEGS = {   # hip, knee, hock, fetlock (world, before ZOFF): knees out, hocks back, toes in
    'right': ((-7.0, -32.0, 10.0), (-13.0, -13.0, -4.0), (-8.0, 5.5, 5.0), (-5.5, 17.5, -1.5)),
    'left': ((7.0, -32.0, 10.0), (12.5, -12.0, -0.5), (7.5, 6.5, 8.5), (5.5, 17.5, 2.5)),
}
ARMS = {   # elbow offset from the shoulder, wrist offset from the elbow (world, right side = -X)
    'right': ((-6.0, 25.0, 1.0), (4.0, 25.0, -5.0)),
    'left': ((8.0, 23.5, 3.0), (-5.0, 23.0, -6.0)),
}
# antler joints in head-local space: right beam (intact) and its tines, left snapped stump and its tine
RIGHT_BEAM = [(-6.5, -14, -8), (-16, -20, -4), (-27, -23, -1), (-36, -27, -5), (-41, -33, -12)]
RIGHT_TINES = [   # (name, beam segment index, base, tip)
    ('right_tine0', 0, (-10.5, -17, -7), (-13, -21, -20)),
    ('right_tine1', 1, (-16, -20, -4), (-15, -32, -5)),
    ('right_tine2', 1, (-21.5, -21.5, -2.5), (-24, -31, 7)),
    ('right_tine3', 2, (-27, -23, -1), (-29, -34, -2)),
    ('right_tine4', 3, (-36, -27, -5), (-41, -36, 0)),
]
LEFT_STUMP = [(6.5, -14, -8), (16, -24, -4)]
LEFT_TINE = ((10, -17.5, -7), (13, -24, -20))


def build():
    r = WR()

    def P(x, y, z):
        return np.array([x, y, z + ZOFF], float)

    # ---------------- legs (separate roots: the Java walk swings them; the body bob slides over the overlap)
    for side, s in (('right', -1), ('left', 1)):
        H, K, A, F = [P(*q) for q in LEGS[side]]
        R1, L1 = aim(H, K)
        leg = r.bone(f'{side}_leg', None, H, R1, mat=hide_mat, flen=L1)
        r.box(leg.name, (-5, -7, -5.5), (10, 16, 11), decals={'front': gash_decal} if s < 0 else None)
        r.box(leg.name, (-4, 8, -3.5), (8, int(L1) - 8, 8))
        R2, L2 = aim(K, A)
        shin = r.bone(f'{side}_shin', leg.name, K, R2, mat=hide_mat, flen=L2)
        r.box(shin.name, (-4.5, -4, -5.5), (9, 7, 8), mat=knob(0.04))                    # knee knot
        r.box(shin.name, (-3.5, 2, -3), (7, int(L2) - 5, 7))
        r.box(shin.name, (-4, L2 - 4, -2.5), (8, 6, 8), mat=knob(0.0))                   # hock + heel spur
        R3_, L3 = aim(A, F)
        foot = r.bone(f'{side}_foot', shin.name, A, R3_, mat=hide_mat, flen=L3)
        r.box(foot.name, (-3, 1, -3), (6, int(L3) - 1, 6))
        r.box(foot.name, (-3.5, L3 - 3, -3.5), (7, 5, 7), mat=knob(-0.04))               # fetlock
        hoof = r.bone(f'{side}_hoof', foot.name, F, R3(0, 12 * s, 0), mat=hoof_mat)     # toes turned in
        hy = 24.0 - F[1]                                                                   # touches y = 24
        r.box(hoof.name, (-3.7, hy - 6, -6.5), (3, 6, 8))
        r.box(hoof.name, (0.7, hy - 6, -6.5), (3, 6, 8))
        r.box(hoof.name, (-2, hy - 8.5, 1), (4, 3, 2))                                     # dewclaws

    # ---------------- pelvis + sunken abdomen
    r.bone('body', None, P(0, -32, 10), R3(14), mat=hide_mat)
    r.box('body', (-6, -5, -6), (12, 10, 12))
    for s in (-1, 1):
        r.mbox('body', s, (-8.5, -9, -5), (4, 5, 5), mat=knob(0.06))                      # iliac points
        r.mbox('body', s, (-11.5, -4, -3), (3, 7, 6), mat=clump_mat(321 + s, 0.75))       # ragged hip tufts
    r.box('body', (-2.5, -7, 4.5), (5, 7, 3), mat=vert_mat)                                # sacrum
    r.box('body', (-5, -21, -3), (10, 18, 8))                                               # waist
    for yy in (-20, -14.5, -9):
        r.box('body', (-1.5, yy, 4.5), (3, 3, 3), mat=vert_mat)
    r.lbone('tail', 'body', (0, -1, 5), rot=(100, 0, 0), mat=clump_mat(131, 0.5))
    r.box('tail', (-2, -1, -1), (4, 7, 2))

    # ---------------- chest: ribcage, tapered vulture hump, spine, rib slats
    r.lbone('chest', 'body', (0, -19, 0.5), rot=(26, 0, 0), mat=hide_mat)
    r.box('chest', (-9, -26, -7), (18, 26, 12), mat=cage_mat, decals={'east': tear_decal})
    r.box('chest', (-11, -29, 0), (22, 15, 10), mat=back_mat)                              # hump base
    r.box('chest', (-8.5, -33, 2), (17, 8, 9), mat=back_mat)                               # hump
    r.box('chest', (-5, -35, 4), (10, 5, 6), mat=back_mat)                                 # hump crest
    r.box('chest', (-12.5, -28, -6), (25, 8, 8))                                            # shoulder girdle
    r.box('chest', (-1.5, -24, -8.5), (3, 20, 2), mat=sternum_mat)
    for yy, zb in ((-37, 5), (-31, 10), (-26, 10), (-21, 9), (-16, 9), (-10, 4), (-4, 4)):
        r.box('chest', (-2, yy, zb), (4, 3, 4), mat=vert_mat)
    for side, s in (('right', -1), ('left', 1)):
        rb = r.lbone(f'{side}_ribs', 'chest', (0, -14, -7), rot=(0, 0, -18 * s), mat=rib_mat)
        for k, yy in enumerate((-10, -6, -2, 2, 6)):
            wd = 8 if k in (1, 2) else 7
            if side == 'left' and k == 3:
                wd = 4                                                                     # broken rib
            r.mbox(rb.name, s, (-(2.5 + wd), yy, -2), (wd, 2, 3))
    r.lbone('rib_splinter', 'chest', (8.5, -12, -3), rot=(0, 28, -14), mat=splinter_mat)
    r.box('rib_splinter', (0, -1, -1), (7, 2, 2))
    r.box('rib_splinter', (7, -0.5, -0.5), (3, 1, 1))
    # scapulae: blades yawed outward so their outer edges stand proud of the hump
    for side, s in (('right', -1), ('left', 1)):
        sc = r.lbone(f'{side}_scapula', 'chest', (3 * s, -28.5, 11), rot=(-8, -30 * s, 0), mat=knob(0.02))
        r.mbox(sc.name, s, (-10, 0, -2), (10, 12, 3))
        r.mbox(sc.name, s, (-9, 2, 0.5), (8, 2, 2.5), mat=knob(0.1))                     # scapular spine
        r.mbox(sc.name, s, (-12, -1, -4), (7, 9, 7), mat=clump_mat(331 + s, 0.65))     # matted shoulder tuft

    # ---------------- neck, skull
    n0 = r.wp('chest', (0, -28, -4))
    HD = P(0, -57, -15)
    u = (HD - n0) / np.linalg.norm(HD - n0)
    NL = float(np.linalg.norm(HD - n0))
    r.bone('neck', 'chest', n0, R3(math.degrees(math.atan2(-u[2], -u[1]))), mat=neck_mat, flen=NL)
    r.box('neck', (-4, -NL - 1, -4), (8, int(NL) + 5, 8), decals={'west': bite_decal})
    for yy in (-NL * 0.35, -NL * 0.7):
        r.box('neck', (-1.5, yy, 3), (3, 3, 3.5), mat=vert_mat)
    r.bone('skull_mount', 'neck', HD, np.eye(3))
    HP, ROLL = 10.0, 5.0
    r.lbone('head', 'skull_mount', (0, 0, 0), rot=(HP, 0, ROLL), mat=skull_mat)
    r.box('head', (-11, -16, -15), (22, 16, 15), mat=cranium_mat,
          decals={'front': cranium_front_decal, 'eyes:front': eyes_decal, 'top': crown_decal})
    for s in (-1, 1):
        r.mbox('head', s, (-6.5, -17, -18.5), (4, 4, 4), mat=orbit_mat)                  # inner brow ridge
        r.mbox('head', s, (-12, -15.5, -18), (6, 3, 4), mat=orbit_mat)                   # drooping outer brow
        r.mbox('head', s, (-12.5, -6, -18), (6, 3, 4), mat=orbit_mat)                    # cheekbone
    r.box('head', (-3.5, -14.5, -17), (7, 9, 3), mat=orbit_mat, decals={'front': bridge_decal})
    r.box('head', (-9, -17.5, -11), (7, 3, 9), mat=clump_mat(161, 0.5))                  # rotten fur on the crown
    r.box('head', (3, -17, -6), (6, 2, 7), mat=clump_mat(163, 0.5))
    r.box('head', (-5, -12, 2.6), (10, 18, 0), mat=flap_mat(181))                        # torn hide off the nape
    r.box('head', (-14, -6, -12), (5, 26, 0), mat=fur_plane(171, 0.15))                 # fur hanging off the cheeks
    r.box('head', (9, -4, -10.5), (5, 22, 0), mat=fur_plane(173, 0.2))
    r.box('head', (6.5, -3, -18.3), (5, 9, 0), mat=flap_mat(183))                        # skin peeling off the cheek

    # snout: dropped, tapering muzzle; the nasal aperture faces the camera
    SP = 18.0
    r.lbone('snout', 'head', (0, -6.5, -16), rot=(SP, 0, 0), mat=muzzle_mat)
    r.box('snout', (-4, -3, -8), (8, 8, 10), decals={'top': muzzle_top_decal})            # root
    r.box('snout', (-3, -2.5, -15), (6, 7, 8), decals={'front': nasal_decal})              # tip
    r.box('snout', (-3.5, 3.5, -14.5), (7, 3, 11))                                          # tooth row
    for s in (-1, 1):
        r.mbox('snout', s, (-3.8, 5.5, -13.8), (2, 7, 2), mat=tooth_mat)                 # upper sabre fangs
        r.mbox('snout', s, (-3.75, 6.5, -12), (0, 4, 9), mat=teeth_mat(6.5, 4, 'z', 207 + s, canines=(-4,)))
    # front row of upper teeth, authored on the head so it hangs vertically for the jumpscare
    tl = r.lp('head', r.wp('snout', (0, 6.5, -14.5)))
    r.box('head', (-3.5, tl[1] - 0.8, tl[2] + 0.4), (7, 7, 0), mat=teeth_mat(tl[1] - 0.2, 6.5, 'x', 201, canines=(-3, 2)))
    r.box('head', (-2, tl[1] + 1.0, tl[2] + 1.2), (4, 12, 0), mat=string_mat(191))      # bloody drool

    # mandible: rami wider than the snout so the dropped jaw frames the face
    r.bone('jaw', 'head', r.wp('snout', (0, 6.2, 6.4)), r.M['snout'][:3, :3], mat=jaw_mat)
    for s in (-1, 1):
        r.mbox('jaw', s, (-7.5, 0.3, -21), (2, 3, 21))                                    # ramus, molars on top
        r.mbox('jaw', s, (-7.8, -5, -3), (2, 6, 4), mat=skull_mat)                        # ascending ramus
        r.mbox('jaw', s, (-6.2, -3.5, -22.5), (2, 4, 2), mat=tooth_mat)                   # lower fangs
    r.box('jaw', (-6, -0.5, -24.5), (12, 5, 4), mat=chin_mat)
    r.box('jaw', (-5, 0.8, -21), (10, 2, 13), mat=mouth_mat)
    r.box('jaw', (-3, 4.2, -16), (6, 8, 0), mat=flap_mat(185))                            # hide hanging under the jaw

    # ---------------- antlers (asymmetric crown; the left one is snapped)
    par = 'head'
    seg = []
    for k, w in enumerate((7, 6, 5, 4)):
        a, b = r.wp('head', RIGHT_BEAM[k]), r.wp('head', RIGHT_BEAM[k + 1])
        Rb, L = aim_up(a, b)
        nm = 'right_antler' if k == 0 else 'right_antler_' + 'bcd'[k - 1]
        r.bone(nm, par, a, Rb, mat=antler_mat)
        r.box(nm, (-w / 2, -L - 0.5, -w / 2), (w, int(round(L)) + 1, w))
        seg.append((nm, L))
        par = nm
    r.box('right_antler', (-4.5, -1.5, -4.5), (9, 2, 9), mat=burr_mat)
    nm, L = seg[-1]
    r.box(nm, (-1.5, -L - 5, -1.5), (3, 5, 3), mat=antler_tip_mat)
    for nm, k, a, b in RIGHT_TINES:
        pa, pb = r.wp('head', a), r.wp('head', b)
        Rb, L = aim_up(pa, pb)
        r.bone(nm, seg[k][0], pa, Rb, mat=antler_mat)
        r.box(nm, (-1.5, -L + 2.5, -1.5), (3, int(round(L)) - 2, 3))
        r.box(nm, (-1, -L - 0.5, -1), (2, 4, 2), mat=antler_tip_mat)

    pa, pb = r.wp('head', LEFT_STUMP[0]), r.wp('head', LEFT_STUMP[1])
    Rb, L = aim_up(pa, pb)
    r.bone('left_antler', 'head', pa, Rb, mat=antler_mat)
    r.box('left_antler', (-4.5, -1.5, -4.5), (9, 2, 9), mat=burr_mat)
    r.box('left_antler', (-3.5, -L - 1, -3.5), (7, int(round(L)) + 1, 7))
    r.box('left_antler', (-3, -L - 4, -3), (6, 4, 6), mat=broken_mat)                    # splintered stump top
    r.box('left_antler', (0.5, -L - 8, -2), (2, 5, 2), mat=broken_mat)                    # surviving splinter
    r.box('left_antler', (-2.5, -L - 1, -3.8), (4, 12, 0), mat=flap_mat(187, 'velvet'))   # velvet strips
    r.box('left_antler', (-1, -L + 1, 3.8), (3, 10, 0), mat=flap_mat(189, 'velvet'))
    pa, pb = r.wp('head', LEFT_TINE[0]), r.wp('head', LEFT_TINE[1])
    Rb, L = aim_up(pa, pb)
    r.bone('left_tine0', 'left_antler', pa, Rb, mat=antler_mat)
    r.box('left_tine0', (-1.5, -L + 2.5, -1.5), (3, int(round(L)) - 2, 3))
    r.box('left_tine0', (-1, -L - 0.5, -1), (2, 4, 2), mat=antler_tip_mat)

    # ---------------- arms: grotesquely long, zig-zag elbows, twisted wrists, 4 hooked claws
    for side, s in (('right', -1), ('left', 1)):
        S = r.wp('chest', (12.5 * s, -22, -4))
        eo, wo = ARMS[side]
        E = S + np.array(eo)
        Wr = E + np.array(wo)
        Ra, La = aim(S, E)
        arm = r.bone(f'{side}_arm', 'chest', S, Ra, mat=hide_mat, flen=La)
        r.box(arm.name, (-4.5, -4.5, -4.5), (9, 9, 9), mat=knob(0.02))                    # shoulder ball
        r.box(arm.name, (-4, 3, -4), (8, 13, 8))
        r.box(arm.name, (-3.5, 15, -3.5), (7, int(La) - 15, 7))
        Rf, Lf = aim(E, Wr)
        fa = r.bone(f'{side}_forearm', arm.name, E, Rf, mat=hide_mat, flen=Lf)
        r.box(fa.name, (-4, -4, -2.5), (8, 7, 8), mat=knob(0.04))                         # knobby elbow
        r.box(fa.name, (-3.5, 2, -3.5), (7, 12, 7))
        r.box(fa.name, (-3, 13, -3), (6, int(Lf) - 15, 6))
        r.box(fa.name, (-3.5, Lf - 3, -3.5), (7, 5, 7), mat=knob(0.0))                    # wrist knot
        Rh, _ = aim(Wr, Wr + np.array([0.5 * s, 1.0, -0.25]), twist=-40 * s)
        hd = r.bone(f'{side}_hand', fa.name, Wr, Rh, mat=hide_mat, flen=11)
        r.box(hd.name, (-5, 0, -2), (10, 11, 4))                                           # palm
        r.box(hd.name, (-5.5, 8.5, -2.5), (11, 3, 5), mat=finger_mat)                     # knuckles
        for k, xk in enumerate((-3.75, -1.25, 1.25, 3.75)):
            fg = r.lbone(f'{side}_finger{k}', hd.name, (xk, 11, 0), rot=(10 + (k % 2) * 6, 0, (k - 1.5) * 6), mat=finger_mat)
            r.box(fg.name, (-1, -0.5, -1), (2, 14, 2))
            r.box(fg.name, (-1.5, 5, -1.5), (3, 3, 3))
            cl = r.lbone(f'{side}_claw{k}', fg.name, (0, 13.5, 0), rot=(24, 0, 0), mat=claw_mat)
            r.box(cl.name, (-1, -0.5, -1), (2, 5, 2))
            r.box(cl.name, (-0.9, 4, -0.3), (2, 4, 2))
            r.box(cl.name, (-0.5, 7.5, 0.9), (1, 5, 1))

    m = Model('wendigo', 256, 256, r.roots)
    m.scale = 0.5
    return m


DEFAULT_MAT = hide_mat
FOCUS = 'head'

POSES = {
    # the lunge: torso pitches in, skull thrust forward and up at the victim, jaw unhinged, claws raised
    'attack': {
        'body': (0.12, 0, 0, 0, 0, 0),
        'chest': (0.12, 0, 0, 0, 0, 0),
        'neck': (-0.3, 0, 0, 0, 0, 0),
        'head': (-0.35, 0, 0, 0, 0, 0),
        'jaw': (1.0, 0, 0, 0, 0, 0),
        'right_arm': (-1.1, 0, -0.7, 0, 0, 0),
        'left_arm': (-1.0, 0, 0.6, 0, 0, 0),
        'right_forearm': (-1.2, 0, 0, 0, 0, 0),
        'left_forearm': (-1.1, 0, 0, 0, 0, 0),
        'right_hand': (0.3, 0, 0, 0, 0, 0),
        'left_hand': (0.3, 0, 0, 0, 0, 0),
        'right_finger0': (0, 0, 0.2, 0, 0, 0), 'right_finger3': (0, 0, -0.2, 0, 0, 0),
        'left_finger0': (0, 0, 0.2, 0, 0, 0), 'left_finger3': (0, 0, -0.2, 0, 0, 0),
    },
    # rearing back, skull thrown back to the sky (one socket still on the camera), jaw at max, arms spread
    'scream': {
        'body': (-0.1, 0, 0, 0, 0, 0),
        'chest': (-0.25, 0, 0, 0, 0, 0),
        'neck': (-0.45, 0, 0, 0, 0, 0),
        'head': (-0.7, 0, 0.12, 0, 0, 0),
        'jaw': (1.15, 0, 0, 0, 0, 0),
        'right_arm': (-0.35, 0, -1.0, 0, 0, 0),
        'left_arm': (-0.35, 0, 1.0, 0, 0, 0),
        'right_forearm': (-0.5, 0, 0, 0, 0, 0),
        'left_forearm': (-0.5, 0, 0, 0, 0, 0),
        'right_hand': (0.3, 0, 0, 0, 0, 0),
        'left_hand': (0.3, 0, 0, 0, 0, 0),
    },
    # creeping on all fours: chest dropped, claws planted on the ground, skull kept level on the player
    'stalk': {
        'body': (0.3, 0, 0, 0, 0, 0),
        'chest': (0.35, 0, 0, 0, 0, 0),
        'neck': (-0.2, 0, 0, 0, 0, 0),
        'head': (-0.55, 0, 0, 0, 0, 0),
        'jaw': (0.12, 0, 0, 0, 0, 0),
        'right_arm': (-0.55, 0, 0, 0, 0, 0),
        'left_arm': (-0.75, 0, 0, 0, 0, 0),
        'right_forearm': (-0.3, 0, 0, 0, 0, 0),
        'left_forearm': (0.0, 0, 0, 0, 0, 0),
        'right_hand': (-0.6, 0, 0, 0, 0, 0),
        'left_hand': (-0.6, 0, 0, 0, 0, 0),
    },
    # uncanny curious tilt
    'head_tilt': {
        'neck': (0, 0, -0.12, 0, 0, 0),
        'head': (0, 0, -0.42, 0, 0, 0),
        'jaw': (0.15, 0, 0, 0, 0, 0),
    },
}

ANIM_NOTES = """todo"""
