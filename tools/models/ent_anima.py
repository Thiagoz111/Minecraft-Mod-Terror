"""Ánima -- the lost soul (DEAD LINE).

Authored at 2x texel density (model.scale = 0.5) in absolute rig coordinates: +Y down, ground y = 24,
faces -Z, right_* on -X.  A ghost: it floats a few texels above the ground, 1.9 blocks including the tail.

Silhouette: a coffin-shaped, back-swept skull (narrow crown, wide brow and cheekbones, sunken temples,
occipital dome sweeping up and back) on a short vertebral neck.  The jaw is stretched DOWN into a long black
scream (twice as tall as it is wide) framed by strands of stretched cheek skin.  Real eye-socket recesses
(brow halves tilted up at the inner corners, nasal bridge, orbital rims, cheekbones) with pinprick glints
deep inside.  Hair drifts up and back like smoke under water.  Open rib cage (separate slats, dark hollow
behind them, the soul-light glowing between the left ribs), shrugged knobby shoulders, over-long arms with
jointed claw fingers.  No legs: torn shroud strips and a four-segment S-curved tail that frays into ribbons.

Colour: pale teal-white bone core (skull, face, ribs), deeper/darker cyan the further a part is from the core
(arms, hands, tail), black-teal voids (sockets, mouth, chest hollow), cyan fresnel only on sideways faces.
Translucent + emissive (entityTranslucentEmissive): alpha 210 at the face down to 110 at the tail/hair tips.
"""
import math

from mcmodel import Model, hash3, face_light, pick
from rig import Rig
from paint import hx, mix

RIG = None  # set by build(); materials need absolute pivots
DY = 2.0    # design frame -> model frame vertical offset (materials work in design coordinates)

# ------------------------------------------------------------------ palettes (hand-picked, hue shifted)
BONE = [hx(c) for c in ('#05171f', '#0c3640', '#1a5f68', '#358b8b', '#62b8b0', '#98dccf', '#c4f3e9', '#e8fffa')]
LIMB = [hx(c) for c in ('#021219', '#05242f', '#093947', '#0f4f5e', '#186a77', '#258690', '#3ba3a8', '#62c0bf')]
VOID = [hx(c) for c in ('#000304', '#010b0e', '#031a20', '#072a33', '#0c3c47')]
HAIR = [hx(c) for c in ('#010a0e', '#03161d', '#06232c', '#0b343f', '#124855', '#1c606b', '#2b7d84', '#43a0a0', '#73c6c0')]
TEETH = [hx(c) for c in ('#0f3236', '#235a5b', '#3f807c', '#5f9f98', '#80bab0')]
CYAN = hx('#3fe3ec')
TEAR = hx('#01161b')
SOUL = [hx('#7fe9e0'), hx('#c4fff7'), hx('#f2fffd')]
GLOW_EYE = (236, 255, 252, 255)
GLOW_EYE2 = (96, 236, 244, 255)
GLOW_SOUL = (120, 226, 222, 255)
GLOW_SOUL2 = (40, 150, 156, 255)


def clamp(v, a=0.0, b=1.0):
    return a if v < a else b if v > b else v


def loc(ctx):
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
    """Texel centre in authored (rest, unrotated) design coordinates."""
    p = RIG.abs_pivot[ctx.bone.name]
    o = ctx.cube.origin
    lx, ly, lz = loc(ctx)
    return p[0] + o[0] + lx, p[1] + o[1] + ly - DY, p[2] + o[2] + lz


def tag(ctx):
    return ctx.cube.name or ''


def A(c, a):
    """Every visible texel lives in the 110..210 alpha band (deliberate spirit translucency)."""
    return (c[0], c[1], c[2], int(clamp(a, 110, 210)))


def h2(a, b, seed=0):
    return hash3(a, b, seed * 7 + 3, seed)


def side_k(ctx):
    """How much a face looks sideways to the main (front) camera: those faces carry the cyan glow edge."""
    nx, ny, nz = ctx.n
    return clamp(abs(nx) * 1.0 + max(0.0, -ny) * 0.15 + max(0.0, nz) * 0.25)


def fres(c, ctx, k=0.5):
    return mix(c, CYAN, side_k(ctx) * k)


def plane_u(ctx):
    """Across-strand texel index of a zero-thickness plane (identical on both of its sides)."""
    lx, ly, lz = loc(ctx)
    w, h, d = ctx.cube.size
    return int(math.floor(lx if w > 0 else lz)), (w if w > 0 else d)


def tapered(ctx, p, lean=0):
    """Strand/tatter taper: full width at p=0, a single texel at p=1, always attached on one edge."""
    u, W = plane_u(ctx)
    if W <= 1:
        return True
    keep = max(1, math.ceil(W * (1.0 - 0.8 * p) - 1e-6))
    if lean:
        return u >= W - keep
    return u < keep


# ------------------------------------------------------------------ hand-placed skull details
# (x, y) texel cells in design space, projected onto every forward face of the head pieces.
# one deliberate branching crack from the crown down to the left brow
# one deliberate stair-step crack running down the forehead (no isolated dots anywhere on the face)
CRACK = {(2, -32), (2, -31), (2, -30), (1, -29), (3, -30)}
TEARS = {-5: (-21, -7), 4: (-21, -9)}  # column x -> (start y, end y): black tear streaks under the sockets
SUTURE = {(-3, 2), (-2, 3), (-1, 2), (0, 3), (1, 2), (2, 3), (3, 2)}


def skull_mat(ctx):
    """Head bone pieces: forehead, vault, crown, brow halves, bridge, rims, cheekbones, maxilla."""
    t = tag(ctx)
    f = ctx.face
    x, y, z = apos(ctx)
    cx, cy = int(math.floor(x)), int(math.floor(y))
    lx, ly, lz = loc(ctx)
    w, h, d = ctx.cube.size
    # hidden inner/back faces: neutral dark so nothing ghosts through the translucent skull
    if f == 'back' and t in ('forehead', 'brow', 'bridge', 'rim', 'cheekbone', 'maxilla'):
        return A(VOID[3], 200)
    if t == 'midface':
        return midface_mat(ctx)
    base = {'forehead': 0.86, 'crown': 0.74, 'vault': 0.78, 'brow': 0.93, 'bridge': 0.84, 'rim': 0.74,
            'cheekbone': 0.92, 'maxilla': 0.6}.get(t, 0.75)
    if f == 'front':
        v = base - (abs(x) / 8.0) ** 2 * 0.18
        if ctx.j == 0 and t != 'forehead':
            v += 0.06
        if ctx.j == ctx.h - 1:
            v -= 0.14  # crease where the piece meets the one below
        if t == 'maxilla':
            # upper lip skin over the gum; bottom row = black gum line
            if ctx.j == ctx.h - 1:
                return A(VOID[1], 210)
            v = 0.62 - abs(x) / 4.0 * 0.12
        if t == 'rim':
            v -= 0.1
        if t == 'brow' and ctx.j == ctx.h - 1:
            v -= 0.08  # brow shadow ring over the socket
        if t == 'cheekbone':
            far = abs(x) > 5.5
            if far:
                v -= 0.12
            if (cx in TEARS) and TEARS[cx][0] <= cy <= TEARS[cx][1]:
                return A(TEAR, 210)
        if (cx, cy) in CRACK and t in ('forehead', 'crown', 'vault'):
            return A(VOID[1], 210)
        if t == 'crown' and ctx.j == 0 and cx in (-3, 0, 2):
            return A(HAIR[5], 205)  # a few roots creeping over the top edge
        if t == 'bridge':
            v = 0.66 - ctx.j * 0.06  # thin nasal bone, recessed: mid tone so the sockets dominate
        if t in ('vault', 'crown'):
            v -= 0.08 if abs(x) > 5 else 0.0          # temples fall into shadow
            v -= clamp((-30.5 - y) / 4.5) * 0.3       # dome curves away from the light
        return A(pick(BONE, v), 208)
    if f == 'bottom':
        # undersides cast shadow into the sockets / mouth
        v = 0.18 if t in ('brow', 'cheekbone', 'maxilla') else 0.3
        if t == 'maxilla':
            return A(VOID[1], 210)
        return A(pick(BONE, v), 205)
    if f == 'top':
        v = base - 0.08 + face_light(ctx) * 0.4
        if t == 'cheekbone':
            v = 0.38  # floor of the socket
        if t in ('crown', 'vault'):
            # hair roots streaming back over the scalp (dark), sagittal suture
            if t == 'crown' or abs(x) < 4.5:
                col = cx
                if h2(col, 3, 41) > 0.35:
                    return A(HAIR[2 + int(h2(col, 4, 42) * 3)], 200)
            if abs(x) < 0.6:
                v -= 0.18
        return A(fres(pick(BONE, v), ctx, 0.25), 202)
    # west / east sides
    inner = (f == 'east' and x < 0 and t != 'vault') or (f == 'west' and x > 0 and t != 'vault')
    if t in ('rim', 'bridge') or (t == 'brow' and inner):
        return A(pick(BONE, 0.3 - (lz / max(1, d)) * 0.1), 205)  # socket walls: dark, deeper = darker
    v = base - 0.14 + face_light(ctx)
    if t == 'vault':
        # sunken temple, sutures hand-placed
        if z < -2 and y > -29:
            v -= 0.14
        if (int(z), int(y + 30)) in SUTURE:
            v -= 0.2
    v -= (lz / max(1, d)) * 0.16
    return A(fres(pick(BONE, v), ctx, 0.45), 200)


def midface_mat(ctx):
    """The deep plane behind the face frame: hollow sockets, nasal cavity; temples on its sides."""
    f = ctx.face
    x, y, z = apos(ctx)
    if f == 'front':
        best = 9.0
        for sx, sy in ((-3.0, -22.6), (3.0, -22.2)):
            dd = ((x - sx) / 2.4) ** 2 + ((y - sy) / 3.2) ** 2
            best = min(best, dd)
        if -1.2 < x < 1.2 and -21 < y < -17.5:
            return A(VOID[0], 210)  # nasal cavity
        if best < 1.0:
            return A(pick(VOID, best * 0.55), 210)
        return A(pick(VOID, 0.55 + min(1.0, best - 1.0) * 0.4), 208)
    if f in ('west', 'east'):
        # sunken temples / gaunt cheek hollow
        v = 0.36 + face_light(ctx) - clamp((y + 22) / 6) * 0.1
        if z < -2.5:
            v -= 0.1
        return A(fres(pick(BONE, v), ctx, 0.5), 200)
    if f == 'bottom':
        return A(VOID[2], 205)
    return A(VOID[3], 200)


def occ_mat(ctx):
    """Back-swept occipital dome: pale bone, hand-placed lambdoid suture and two cracks, hair roots on top."""
    f = ctx.face
    x, y, z = apos(ctx)
    lx, ly, lz = loc(ctx)
    w, h, d = ctx.cube.size
    if f == 'front':
        return A(VOID[3], 200)  # buried inside the vault
    v = 0.66 + face_light(ctx) * 0.9
    if f == 'top':
        col = int(math.floor(x))
        if h2(col, int(lz) // 3, 51) > 0.3:
            return A(HAIR[1 + int(h2(col, 5, 52) * 4)], 196)
    if f == 'back':
        i, j = ctx.i, ctx.j
        # lambdoid suture: a zig-zag "^" across the back
        zz = abs(i - (w - 1) / 2.0) * 0.55 + (i % 2) * 0.8
        if abs(j - (1.2 + zz)) < 0.55:
            v -= 0.24
        if (i, j) in ((2, 3), (2, 4), (3, 5), (w - 3, 2), (w - 4, 3)):
            v -= 0.3
        v -= j / max(1, h) * 0.12
    if f in ('west', 'east'):
        v -= lz / max(1, d) * 0.1
        if ctx.j == ctx.h - 1:
            v -= 0.1
    return A(fres(pick(BONE, v), ctx, 0.5), 198)


def tooth_mat(ctx):
    lx, ly, lz = loc(ctx)
    h = ctx.cube.size[1]
    up = ctx.bone.name == 'head'
    tip = ly / max(1.0, h) if up else 1 - ly / max(1.0, h)  # 0 at the gum, 1 at the tip
    v = 0.55 + tip * 0.3 + face_light(ctx) * 0.5
    if ctx.face in ('west', 'east', 'back'):
        v -= 0.25
    if tip < 0.2:
        v = 0.1  # stained root at the gum line
    return A(pick(TEETH, v), 200)


def throat_mat(ctx):
    """Mouth void: black core, darker cyan toward the cheeks.  The head-bone plane is only painted down to
    the rest chin (its lower part frames the dropped scream jaw in the close-up / jumpscare portrait)."""
    x, y, z = apos(ctx)
    if ctx.bone.name == 'head' and y > 1.0:
        return None
    d = abs(x) / 3.0
    c = mix(VOID[0], VOID[3], clamp(d * d * 1.1 - 0.1))
    return A(c, 210)


def strand_mat(ctx):
    """Stretched cheek skin: one sheet per side from the cheekbone down past the jaw corner.  Its outer
    edge slants in toward the chin (coffin-shaped lower face), the inner edge is the lip of the scream."""
    lx, ly, lz = loc(ctx)
    w, h, d = ctx.cube.size
    p = ly / max(1, h)
    right = ctx.bone.name == 'cheek_right'
    u = int(math.floor(lx))
    k = u if right else (w - 1 - u)  # 0 = outer edge, w-1 = inner (mouth) edge
    # outer edge eaten away progressively toward the bottom; the last rows are ragged single strands
    lost = int(p * 3.4)
    if k < lost:
        return None
    if p > 0.86 and (k + int(ly)) % 2 == 0 and k != w - 1:
        return None
    # a torn slit in the stretched skin
    if k == 1 and 0.42 < p < 0.62:
        return None
    x, y, z = apos(ctx)
    if int(math.floor(x)) in TEARS and k >= 2 and p < 0.55:
        return A(TEAR, 206)
    v = 0.84 - p * 0.42
    if k == w - 1:
        v -= 0.12  # lip edge folds into the mouth
    if k == 2:
        v += 0.04
    if k == lost:
        v -= 0.1   # torn edge
    c = pick(BONE, v)
    if p > 0.7:
        c = mix(c, CYAN, (p - 0.7) * 0.6)
    return A(c, 208 - p * 70)


def jaw_mat(ctx):
    t = tag(ctx)
    f = ctx.face
    x, y, z = apos(ctx)
    lx, ly, lz = loc(ctx)
    w, h, d = ctx.cube.size
    if t == 'tooth':
        return tooth_mat(ctx)
    if t == 'throat':
        return throat_mat(ctx)
    if f == 'back':
        return A(VOID[2], 205)
    if t in ('ramus', 'corner'):
        inner = (f == 'east' and x < 0) or (f == 'west' and x > 0)
        if inner:
            return A(pick(VOID, 0.45 + ly / h * 0.4), 210)  # wet dark inside of the cheek
        if f == 'front':
            v = 0.8 - ly / h * 0.2
            if ctx.j % 4 == 3:
                v -= 0.1
            return A(pick(BONE, v), 206)
        if f == 'top':
            return A(pick(BONE, 0.4), 200)
        v = 0.58 + face_light(ctx) - ly / h * 0.15
        return A(fres(pick(BONE, v), ctx, 0.5), 202)
    # chin + chin point
    if f == 'top':
        if t == 'chin':
            return A(pick(VOID, 0.5 if ctx.edge() == 0 else 0.15), 210)  # floor of the mouth
        return A(pick(BONE, 0.5), 200)
    if f == 'front':
        if t == 'chin' and ctx.j == 0:
            return A(VOID[2], 210)  # lower gum line
        v = 0.82 - abs(x) / 2.5 * 0.18 - (0.1 if t == 'chinpt' else 0.0)
        if ctx.j == ctx.h - 1:
            v -= 0.12
        if t == 'chin' and (int(math.floor(x)), ctx.j) in ((-2, 1), (1, 2)):
            v -= 0.25  # chipped bone
        return A(pick(BONE, v), 208)
    if f == 'bottom':
        return A(pick(BONE, 0.3), 202)
    v = 0.6 + face_light(ctx)
    return A(fres(pick(BONE, v), ctx, 0.5), 202)


def bone_mat(ctx):
    """Ribs, sternum, clavicles, shoulders, vertebrae, scapulae: pale bone under a thin glowing skin."""
    t = tag(ctx)
    f = ctx.face
    x, y, z = apos(ctx)
    lx, ly, lz = loc(ctx)
    w, h, d = ctx.cube.size
    a = 196
    v = 0.74 + face_light(ctx) * 1.1
    if t in ('ribf', 'ribs'):
        v -= 0.2
        if f in ('front', 'west', 'east', 'back'):
            if ctx.j == 0:
                v += 0.1
            elif ctx.j == ctx.h - 1:
                v -= 0.24
        if t == 'ribs':
            v -= 0.2 + clamp(lz / max(1, d)) * 0.3  # curving away toward the spine
        if f == 'front' and t == 'ribf':
            far = abs(x) > 6.5
            v -= 0.1 if far else 0.0
        if f == 'back':
            v = 0.3
    elif t == 'sternum':
        if ctx.j % 3 == 2:
            v -= 0.18
    elif t == 'clav':
        if ctx.j == ctx.h - 1:
            v -= 0.16
    elif t in ('vert', 'spine'):
        a = 190
        if ctx.j == ctx.h - 1:
            v -= 0.22
    elif t == 'shoulder':
        v -= 0.06
        if f == 'top' and ctx.edge() > 0:
            v += 0.06
        a = 192
    elif t == 'tendon':
        v = 0.55 + face_light(ctx)
        a = 180
    elif t == 'scap':
        # shoulder blade: bright ridge along the top, fading down into the back
        v = 0.66 - ctx.j / max(1, ctx.h) * 0.3 + face_light(ctx)
        if ctx.j == 0:
            v += 0.08
        if f == 'back' and (ctx.i == 0 or ctx.i == ctx.w - 1):
            v -= 0.14
        a = 180
    elif t == 'yoke':
        v = 0.5 + face_light(ctx)
        a = 186
    if t in ('ribf', 'ribs', 'shoulder', 'clav', 'yoke'):
        return A(mix(fres(pick(BONE, v), ctx, 0.45), CYAN, 0.12), a)
    return A(fres(pick(BONE, v), ctx, 0.45), a)


def backplate_mat(ctx):
    """Front: the dark hollow of the chest lit by the soul.  Back: skin drawn over spine and ribs."""
    f = ctx.face
    x, y, z = apos(ctx)
    if f == 'front':
        dd = math.sqrt((x - 4.5) ** 2 + ((y + 8) * 0.8) ** 2) / 7.0
        return A(pick(VOID, 0.85 - dd * 0.75), 196)
    v = 0.5 + face_light(ctx)
    if f == 'back':
        # ribs arching out from the spine under the skin, spine groove, waist narrowing into shadow
        ry = (y + 100 + abs(x) * 0.35) % 3.1
        if ry < 1.0:
            v -= 0.14
        elif ry < 2.0:
            v += 0.05
        if abs(x) < 1.5:
            v -= 0.16
        if abs(x) > 5.5:
            v -= 0.1
        v -= clamp((y + 5) / 5) * 0.15
        return A(pick(LIMB, v + 0.2), 186)
    return A(fres(pick(LIMB, v + 0.1), ctx, 0.5), 186)


def soul_mat(ctx):
    e = ctx.edge()
    c = SOUL[2] if e > 0 else SOUL[1]
    if ctx.face in ('bottom', 'back'):
        c = SOUL[0]
    return A(c, 205)


def waist_mat(ctx):
    x, y, z = apos(ctx)
    f = ctx.face
    v = 0.52 + face_light(ctx)
    if f == 'front':
        if abs(x) < 1:
            v += 0.08  # lumbar spine pressing through the belly
        if int(y + 100) % 2 == 0 and abs(x) < 1.2:
            v -= 0.12
        v -= abs(x) / 3.5 * 0.16
    return A(fres(pick(LIMB, v + 0.12), ctx, 0.45), 182)


ARM_ALPHA = {'arm': 172, 'forearm': 164, 'hand': 156}


def arm_mat(ctx):
    """Emaciated limbs in deeper cyan: knotted joints, tendon split, knuckle creases, black claws."""
    n = ctx.bone.name
    t = tag(ctx)
    f = ctx.face
    x, y, z = apos(ctx)
    lx, ly, lz = loc(ctx)
    w, h, d = ctx.cube.size
    if t == 'drape':
        return ecto_mat(ctx)
    part = n.split('_', 1)[1] if '_' in n else n
    a = ARM_ALPHA.get(part, 148)
    v = 0.6 + face_light(ctx) * 1.1
    if f in ('front', 'back'):
        v += 0.06 - abs(lx / max(1, w) - 0.5) * 0.25
    if t == 'knob':
        v += 0.14  # bone of the joint shows through, paler
        if ctx.j == ctx.h - 1:
            v -= 0.2
    if t == 'fore' and f in ('front', 'back') and ctx.i == 1:
        v -= 0.14  # radius / ulna split
    if t in ('upper', 'fore'):
        v -= (ly / max(1, h)) * 0.12
    if t == 'palm':
        a = 156
        if f == 'back' and ctx.j in (1, 3) and 0 < ctx.i < ctx.w - 1:
            v -= 0.16  # palm creases
        if f == 'front' and ctx.i % 2 == 1:
            v -= 0.1  # metacarpal ridges
    if t == 'finger':
        a = 148 if 'tip' not in n else 138
        if int(ly) == h - 1 and f != 'bottom':
            v -= 0.14  # knuckle crease
    if t == 'claw':
        c = mix(VOID[1], CYAN, 0.18 if f in ('front', 'west') else 0.04)
        return A(c, 196)
    return A(fres(pick(LIMB, v), ctx, 0.45), a)


def ecto_mat(ctx):
    """Ectoplasm: tail, shroud strips, sleeve drapes.  Flow lines run the whole length; hems fray by column
    and fade out (no random holes)."""
    n = ctx.bone.name
    t = tag(ctx)
    f = ctx.face
    x, y, z = apos(ctx)
    lx, ly, lz = loc(ctx)
    w, h, d = ctx.cube.size
    if t in ('tatter', 'drape', 'ribbon'):
        p = ly / max(1, h)
        u, W = plane_u(ctx)
        # column-based fray: each column ends at its own length
        seed = int(abs(ctx.cube.origin[0]) * 3 + abs(ctx.cube.origin[2]) * 5) + len(n)
        end = 0.62 + 0.38 * h2(u, seed, 61)
        if p > end:
            return None
        if t == 'ribbon' and not tapered(ctx, p):
            return None
        v = 0.62 - p * 0.35 + (h2(u, seed, 62) - 0.5) * 0.16
        if u == 0 or u == W - 1:
            v -= 0.06
        a0 = {'tatter': 160, 'drape': 150, 'ribbon': 140}[t]
        return A(fres(pick(LIMB, v), ctx, 0.3), a0 - p * 45)
    # tail segments: darker and thinner with distance from the body
    k = int(n[-1]) if n[-1].isdigit() else 1
    col = int(math.floor(lx if f in ('front', 'back', 'top', 'bottom') else lz))
    s = h2(col, k, 71)
    p = ly / max(1, h)
    v = 0.62 - k * 0.07 + face_light(ctx) + (s - 0.5) * 0.12 - p * 0.06
    if f in ('front', 'back') and col % 3 == 1:
        v -= 0.05
    a = {1: 168, 2: 152, 3: 136, 4: 122}[k] - p * 10
    if f == 'bottom':
        v -= 0.1
    return A(fres(pick(LIMB, v), ctx, 0.5), a)


def hair_mat(ctx):
    """Strands drifting up and back: dark roots, light catching toward the tips, tips taper + fade."""
    n = ctx.bone.name
    lx, ly, lz = loc(ctx)
    w, h, d = ctx.cube.size
    seg = 1 if n.endswith('_tip') else 0
    p0 = 1 - ly / max(1, h)  # 0 at the root end of this segment, 1 at its far end
    p = p0 * 0.5 + seg * 0.5
    if not tapered(ctx, p, lean=(len(n) + int(ctx.cube.origin[0] * 2)) % 2):
        return None
    u, W = plane_u(ctx)
    s = h2(u, len(n) + int(ctx.cube.origin[2] * 3), 81)
    v = 0.42 + p * 0.5 + (s - 0.5) * 0.18
    if u == 0:
        v -= 0.08
    c = pick(HAIR, v)
    if p > 0.8:
        c = mix(c, CYAN, (p - 0.8) * 1.2)
    return A(c, 192 - p * 82)


def anima_mat(ctx):
    n = ctx.bone.name
    t = tag(ctx)
    if t == 'tooth':
        return tooth_mat(ctx)
    if t == 'throat':
        return throat_mat(ctx)
    if t == 'strand':
        return strand_mat(ctx)
    if n in ('head', 'brow_right', 'brow_left', 'cheek_right', 'cheek_left'):
        return skull_mat(ctx)
    if n == 'skull_back':
        return occ_mat(ctx)
    if n == 'jaw':
        return jaw_mat(ctx)
    if n.startswith('hair'):
        return hair_mat(ctx)
    if n.startswith('tail') or n.startswith('shroud'):
        return ecto_mat(ctx)
    if t == 'backplate':
        return backplate_mat(ctx)
    if t == 'soul':
        return soul_mat(ctx)
    if t == 'waist':
        return waist_mat(ctx)
    if n in ('body', 'ribs_right', 'ribs_left', 'neck'):
        return bone_mat(ctx)
    return arm_mat(ctx)


DEFAULT_MAT = anima_mat


# ------------------------------------------------------------------ emissive decals (layer 'eyes')
def eyes_sockets(img, u0, v0, w, h):
    """Midface front (x -6..6, y -26..-17): one pinprick glint deep in each socket, staring slightly inward
    (at the viewer), the left one a texel lower -- asymmetric and wrong."""
    px = img.load()
    for (i, j, c) in ((3, 3, GLOW_EYE), (3, 4, GLOW_EYE2), (8, 4, GLOW_EYE), (8, 5, GLOW_EYE2)):
        if i < w and j < h:
            px[u0 + i, v0 + j] = c


def eyes_soul(img, u0, v0, w, h):
    px = img.load()
    for j in range(h):
        for i in range(w):
            e = min(i, j, w - 1 - i, h - 1 - j)
            px[u0 + i, v0 + j] = GLOW_SOUL if e > 0 else GLOW_SOUL2


# ------------------------------------------------------------------ build
def build():
    global RIG
    r = Rig()
    RIG = r

    def bone(name, pivot, parent=None, rot=(0, 0, 0)):
        return r.bone(name, (pivot[0], pivot[1] + DY, pivot[2]), parent=parent, rot=rot)

    def B(bn, frm, size, name, **kw):
        c = r.box(bn, (frm[0], frm[1] + DY, frm[2]), size, **kw)
        c.name = name
        return c

    # ---------------- body (root): waist pivot, leaning into the drift.  The torso sits BEHIND the face
    # (ribs front at z=-2) so the hanging jaw always stays in front of the rib cage.
    bone('body', (0, 0, 4), rot=(8, 0, 0))
    B('body', (-7, -17, 6), (14, 9, 2), 'backplate')
    B('body', (-5, -8, 6), (10, 7, 2), 'backplate')
    B('body', (3, -10, 0.5), (3, 4, 3), 'soul',
      decals={'eyes:front': eyes_soul, 'eyes:west': eyes_soul, 'eyes:east': eyes_soul, 'eyes:top': eyes_soul})
    B('body', (-3.5, -3, 2), (7, 5, 5), 'waist')
    B('body', (-12.5, -19.5, 2), (3, 3, 4), 'shoulder')
    B('body', (9.5, -19.5, 2), (3, 3, 4), 'shoulder')
    B('body', (-9, -18, 4), (18, 2, 4), 'yoke')
    B('body', (-9, -18.5, -1), (8, 1, 2), 'clav')
    B('body', (1, -18.5, -1), (8, 1, 2), 'clav')
    B('body', (-1, -17, -2.5), (2, 9, 2), 'sternum')
    for y in (-17, -14, -11, -8, -5, -2):
        B('body', (-1, y, 8), (2, 2, 2), 'spine')
    B('body', (-7, -16, 8), (4, 6, 1), 'scap')
    B('body', (3, -16, 8), (4, 6, 1), 'scap')

    # ---------------- rib cage: separate slats sloping down from the sternum, real gaps between them
    bone('ribs_right', (-1, -16, -1.5), parent='body', rot=(0, 0, -12))
    bone('ribs_left', (1, -16, -1.5), parent='body', rot=(0, 0, 12))
    for k, w in enumerate((7, 8, 9, 8, 6)):
        y = -15.5 + 3.1 * k
        B('ribs_right', (-1 - w, y, -2), (w, 2, 2), 'ribf')
        B('ribs_right', (-1 - w, y, 0), (2, 2, 6), 'ribs')
        B('ribs_left', (1, y, -2), (w, 2, 2), 'ribf')
        B('ribs_left', (w - 1, y, 0), (2, 2, 6), 'ribs')

    # ---------------- neck: visible vertebrae between the skull base and the shoulders
    bone('neck', (0, -17, 5), parent='body', rot=(-10, 0, 0))
    B('neck', (-1.5, -25, 1), (3, 2, 3), 'vert')
    B('neck', (-1.5, -22.5, 2), (3, 2, 3), 'vert')
    B('neck', (-1.5, -20, 3), (3, 2, 3), 'vert')
    B('neck', (-2.5, -24, 1.5), (1, 7, 1), 'tendon')
    B('neck', (1.5, -24, 1.5), (1, 7, 1), 'tendon')

    # ---------------- head: coffin skull, recessed face frame (sockets 4.5 x 6, 3-4 texels deep)
    bone('head', (0, -25, 2), parent='neck', rot=(-6, 0, 5))
    B('head', (-7, -31, -6), (14, 5, 10), 'vault')
    B('head', (-5, -33, -5), (10, 2, 9), 'vault')
    B('head', (-3, -35, -3.5), (6, 2, 7), 'crown')
    B('head', (-5, -32, -7), (10, 4, 1), 'forehead')
    B('head', (-6, -26, -4), (12, 9, 5), 'midface', decals={'eyes:front': eyes_sockets})
    B('head', (-6, -25, -6), (1, 6, 2), 'rim')
    B('head', (5, -25, -6), (1, 6, 2), 'rim')
    B('head', (-1, -26, -7.5), (2, 5, 3), 'bridge')
    B('head', (-4, -17.5, -7.5), (8, 2, 3), 'maxilla')
    B('head', (-3, -17, -4.5), (6, 25, 1), 'throat')   # 1 deep: two black layers
    for tx, th in ((-3, 2), (-1.8, 4), (-0.5, 1), (1.3, 3), (2.2, 1)):
        B('head', (tx, -15.5, -7), (1, th, 1), 'tooth')

    # brow halves: inner corners raised (anguish), they overhang the sockets
    bone('brow_right', (-4.5, -27, -7), parent='head', rot=(0, 0, -22))
    B('brow_right', (-7.8, -28, -8.5), (6, 2, 3), 'brow')
    bone('brow_left', (4.5, -27, -7), parent='head', rot=(0, 0, 22))
    B('brow_left', (1.8, -28, -8.5), (6, 2, 3), 'brow')

    # occipital dome sweeping up and back (elongated side silhouette)
    bone('skull_back', (0, -29, 1), parent='head', rot=(22, 0, 0))
    B('skull_back', (-6, -33, 0), (12, 8, 7), 'occ')
    B('skull_back', (-4.5, -32, 6), (9, 6, 4), 'occ')
    B('skull_back', (-3, -31, 9), (6, 4, 3), 'occ')

    # stretched cheek skin: strands from the cheekbones down past the jaw corners
    # cheekbones (angled, outer ends drooping) + stretched cheek skin converging toward the chin
    bone('cheek_right', (-2.5, -19, -7), parent='head', rot=(0, 16, -9))
    B('cheek_right', (-8, -19.5, -7), (6, 2, 3), 'cheekbone')
    B('cheek_right', (-7, -17.5, -8.1), (4, 15, 0), 'strand')
    bone('cheek_left', (2.5, -19, -7), parent='head', rot=(0, -16, 9))
    B('cheek_left', (2, -19.5, -7), (6, 2, 3), 'cheekbone')
    B('cheek_left', (3, -17.5, -8.1), (4, 15, 0), 'strand')

    # ---------------- jaw: long, narrow, hanging open; tapered chin; few broken teeth
    bone('jaw', (0, -17, -4.5), parent='head')
    B('jaw', (-4, -16, -7.5), (1, 12, 3), 'ramus')
    B('jaw', (3, -16, -7.5), (1, 12, 3), 'ramus')
    B('jaw', (-2, -4, -8.5), (4, 3, 4), 'chin')
    B('jaw', (-1, -1, -8), (2, 2, 3), 'chinpt')
    B('jaw', (-3, -7, -7.5), (1, 4, 3), 'corner')   # the mouth narrows to a point at the bottom
    B('jaw', (2, -7, -7.5), (1, 4, 3), 'corner')
    B('jaw', (-3, -13, -5.4), (6, 9, 0), 'throat')
    for tx, th in ((-1.8, 5), (-0.6, 2), (1.0, 4)):
        B('jaw', (tx, -4 - th, -7.6), (1, th, 1), 'tooth')

    # ---------------- hair: locks of 2-segment chains drifting up and back, tapering to 1-texel tips
    bone('hair', (0, -34, 0), parent='head')
    locks = [  # root x, y, z, back-sweep A, out A, len A, back extra B, out extra B, len B, widths
        (-4.0, -33.0, -2.5, 60, 56, 9, 16, 18, 12, (3, 1)),
        (2.5, -34.0, -2.0, 68, 26, 9, 14, 14, 13, (2, 1)),
        (-1.0, -34.5, 0.5, 74, 8, 10, 10, -8, 17, (3, 2)),
        (4.5, -32.5, 1.5, 62, 60, 9, 14, 20, 12, (2, 1)),
        (-5.0, -31.5, 3.0, 72, 46, 10, 12, 16, 14, (2, 1)),
        (1.0, -31.0, 5.0, 82, 10, 12, 4, 6, 18, (3, 2)),
    ]
    for k, (hx_, hy, hz, back, out, la, back2, out2, lb, (wa, wb)) in enumerate(locks):
        sgn = 1 if hx_ > 0 else -1
        na = 'hair_%d' % (k + 1)
        nb = na + '_tip'
        bone(na, (hx_, hy, hz), parent='hair', rot=(-back, 0, out * sgn))
        B(na, (hx_ - wa / 2.0, hy - la, hz), (wa, la, 0), 'lock')
        B(na, (hx_, hy - la, hz - 1), (0, la, 2), 'lock')
        B(na, (hx_ + sgn * 1.0, hy - la + 2, hz + 0.6), (1, la - 2, 0), 'lock')
        bone(nb, (hx_, hy - la + 0.5, hz), parent=na, rot=(-back2, 0, out2 * sgn))
        B(nb, (hx_ - wb / 2.0, hy - la - lb + 0.5, hz), (wb, lb, 0), 'lock')
        B(nb, (hx_, hy - la - lb + 2.5, hz - 0.5), (0, lb - 2, 1), 'lock')

    # ---------------- arms (authored hanging, posed reaching forward and out)
    AZ = 2.0  # arm depth offset (shoulder joint at z = 3.5)

    def arm(side, sx, rot_arm, rot_fore, rot_hand, curl, thumb_rot):
        def X(x0, w):
            return x0 if sx > 0 else -(x0 + w)
        an, fn_, hn = side + '_arm', side + '_forearm', side + '_hand'
        bone(an, (11 * sx, -18, 1.5 + AZ), parent='body', rot=(rot_arm[0], -rot_arm[1] * sx, -rot_arm[2] * sx))
        B(an, (X(9.5, 3), -18, 0 + AZ), (3, 12, 3), 'upper')
        B(an, (X(9, 4), -7, -0.5 + AZ), (4, 3, 4), 'knob')
        bone(fn_, (11 * sx, -5.5, 1.5 + AZ), parent=an, rot=(rot_fore, 0, 0))
        B(fn_, (X(9.5, 3), -5.5, 0 + AZ), (3, 12, 3), 'fore')
        B(fn_, (X(9.5, 3), 5, -0.5 + AZ), (3, 2, 4), 'knob')
        B(fn_, (X(11, 0), -4, 3 + AZ), (0, 11, 6), 'drape')
        bone(hn, (11 * sx, 7, 1.5 + AZ), parent=fn_, rot=(rot_hand, 0, 0))
        B(hn, (X(7.5, 7), 7, 0.5 + AZ), (7, 5, 2), 'palm')
        # fingers medial -> lateral: x0, splay, proximal, distal
        fingers = [(7.5, -10, 6, 5), (9.4, -3, 7, 6), (11.2, 4, 7, 5), (13, 12, 5, 4)]
        for k, (fx, splay, lp, ld) in enumerate(fingers):
            fnm = '%s_finger_%d' % (side, k + 1)
            tnm = fnm + '_tip'
            bone(fnm, ((fx + 1) * sx, 12, 1.5 + AZ), parent=hn, rot=(curl[0] + k * 2, 0, -splay * sx))
            B(fnm, (X(fx, 2), 12, 0.5 + AZ), (2, lp, 2), 'finger')
            bone(tnm, ((fx + 1) * sx, 12 + lp, 1.5 + AZ), parent=fnm, rot=(curl[1], 0, 0))
            B(tnm, (X(fx, 2), 12 + lp - 0.2, 0.55 + AZ), (2, ld, 2), 'finger')
            B(tnm, (X(fx + 0.5, 1), 12 + lp + ld - 0.4, 1.0 + AZ), (1, 3, 1), 'claw')
        th = side + '_thumb'
        bone(th, (7.5 * sx, 9, 1.5 + AZ), parent=hn, rot=(thumb_rot[0], 0, -thumb_rot[1] * sx))
        B(th, (X(6.5, 2), 9, 0.5 + AZ), (2, 7, 2), 'finger')
        B(th, (X(7, 1), 15.6, 1.0 + AZ), (1, 3, 1), 'claw')

    # (xRot forward<0, yRot, zRot outward>0), forearm bend, wrist droop, finger curl, thumb (x, z)
    arm('right', -1, (-40, 10, 9), -34, 28, (22, 30), (14, 34))
    arm('left', 1, (-32, 6, 12), -38, 30, (26, 34), (18, 38))

    # ---------------- shroud strips around the waist (narrow, tattered, the torso still reads)
    bone('shroud_front', (0, 1, 1.6), parent='body', rot=(-6, 0, 0))
    B('shroud_front', (-4, 1, 1.4), (2, 12, 0), 'tatter')
    B('shroud_front', (-0.5, 1, 1.6), (1, 6, 0), 'tatter')
    B('shroud_front', (2.2, 1, 1.4), (2, 14, 0), 'tatter')
    bone('shroud_back', (0, 0, 7.5), parent='body', rot=(14, 0, 0))
    B('shroud_back', (-4, 0, 7.6), (3, 14, 0), 'tatter')
    B('shroud_back', (-0.5, 0, 7.7), (2, 18, 0), 'tatter')
    B('shroud_back', (2.2, 0, 7.6), (3, 12, 0), 'tatter')
    bone('shroud_right', (-3.6, 0, 4.5), parent='body', rot=(0, -35, 10))
    B('shroud_right', (-3.6, 0, 2.5), (0, 13, 4), 'tatter')
    bone('shroud_left', (3.6, 0, 4.5), parent='body', rot=(0, 35, -10))
    B('shroud_left', (3.6, 0, 2.5), (0, 11, 4), 'tatter')

    # ---------------- tail: no legs, the soul trails off in an S-curve and frays into ribbons
    bone('tail1', (0, 2, 4.5), parent='body', rot=(8, 0, 0))
    B('tail1', (-4, 1.5, 1.5), (8, 7, 6), 'tail')
    bone('tail2', (0, 8, 4.5), parent='tail1', rot=(16, 0, 10))
    B('tail2', (-3, 7.5, 2.5), (6, 6, 4), 'tail')
    bone('tail3', (0, 13, 4.5), parent='tail2', rot=(18, 0, -20))
    B('tail3', (-2, 12.5, 3), (4, 6, 3), 'tail')
    bone('tail4', (0, 18, 4.5), parent='tail3', rot=(16, 0, 16))
    B('tail4', (-1, 17.5, 3.5), (2, 5, 2), 'tail')
    B('tail4', (-2, 19, 4.5), (2, 10, 0), 'ribbon')
    B('tail4', (0.4, 19, 4.4), (2, 8, 0), 'ribbon')
    B('tail4', (0, 19.5, 3), (0, 9, 3), 'ribbon')

    m = Model('anima', 256, 64, r.roots)
    m.scale = 0.5
    m.render_type = 'entityTranslucentEmissive'
    return m


FOCUS = 'head'

POSES = {
    # the signature: jaw dislocated to the chest, head thrown back, arms flung wide, cheeks torn wider
    'scream': {
        'body': (-0.14, 0, 0, 0, 0, 0),
        'neck': (-0.18, 0, 0, 0, 0, 0),
        'head': (-0.34, 0, -0.06, 0, 0, 0),
        'jaw': (-0.1, 0, 0, 0, 6.5, -1.0),
        'cheek_right': (0, 0, 0.12, 0, 1.0, 0),
        'cheek_left': (0, 0, -0.12, 0, 1.0, 0),
        'brow_right': (0, 0, -0.1, 0, -0.5, 0),
        'brow_left': (0, 0, 0.1, 0, -0.5, 0),
        'right_arm': (-0.2, 0.25, 0.55, 0, 0, 0),
        'left_arm': (-0.3, -0.25, -0.5, 0, 0, 0),
        'right_forearm': (-0.35, 0, 0, 0, 0, 0),
        'left_forearm': (-0.3, 0, 0, 0, 0, 0),
        'right_hand': (-0.6, 0, 0, 0, 0, 0),
        'left_hand': (-0.6, 0, 0, 0, 0, 0),
        'hair': (-0.2, 0, 0, 0, 0, 0),
        'tail1': (0.1, 0, 0, 0, 0, 0),
        'tail2': (0.15, 0, 0.1, 0, 0, 0),
        'tail3': (0.15, 0, -0.15, 0, 0, 0),
    },
    # lunge at the victim: body pitches in, jaw gapes WIDER than the scream (this jaw is the jumpscare
    # portrait's), both claws snap forward and curl
    'attack': {
        'body': (0.28, 0, 0, 0, 0, -3.0),
        'head': (0.06, 0, -0.08, 0, 0, 0),
        'jaw': (-0.14, 0, 0, 0, 7.5, -1.5),
        'cheek_right': (0, 0, 0.1, 0, 1.0, 0),
        'cheek_left': (0, 0, -0.1, 0, 1.0, 0),
        'right_arm': (-0.55, -0.15, -0.1, 0, 0, 0),
        'left_arm': (-0.7, 0.1, 0.05, 0, 0, 0),
        'right_forearm': (0.25, 0, 0, 0, 0, 0),
        'left_forearm': (0.3, 0, 0, 0, 0, 0),
        'right_hand': (-0.2, 0, 0, 0, 0, 0),
        'left_hand': (-0.2, 0, 0, 0, 0, 0),
        'tail1': (-0.25, 0, 0, 0, 0, 0),
        'tail2': (-0.2, 0, 0, 0, 0, 0),
        'tail3': (-0.15, 0, 0, 0, 0, 0),
    },
    # idle float: arms trail low and back, head hangs, tail streams out behind
    'drift': {
        'body': (0.12, 0, 0, 0, 0, 0),
        'neck': (0.2, 0, 0, 0, 0, 0),
        'head': (0.25, 0, 0.12, 0, 0, 0),
        'jaw': (0.05, 0, 0, 0, 1.0, 0),
        'right_arm': (0.85, 0, -0.1, 0, 0, 0),
        'left_arm': (0.8, 0, -0.15, 0, 0, 0),
        'right_forearm': (0.2, 0, 0, 0, 0, 0),
        'left_forearm': (0.25, 0, 0, 0, 0, 0),
        'right_hand': (0.2, 0, 0, 0, 0, 0),
        'left_hand': (0.2, 0, 0, 0, 0, 0),
        'hair': (-0.15, 0, 0, 0, 0, 0),
        'tail1': (0.2, 0, 0, 0, 0, 0),
        'tail2': (0.2, 0, -0.1, 0, 0, 0),
        'tail3': (0.2, 0, 0.15, 0, 0, 0),
        'tail4': (0.2, 0, -0.1, 0, 0, 0),
    },
    # the clip money shot: both arms straight at the camera, fingers splayed wide, face pushed forward
    'reach': {
        'body': (0.12, 0, 0, 0, 0, -1.5),
        'head': (0.05, 0, 0, 0, 0, 0),
        'jaw': (-0.08, 0, 0, 0, 4.0, -0.5),
        'right_arm': (-0.85, -0.12, -0.05, 0, 0, 0),
        'left_arm': (-1.0, 0.06, 0.05, 0, 0, 0),
        'right_forearm': (0.42, 0, 0, 0, 0, 0),
        'left_forearm': (0.5, 0, 0, 0, 0, 0),
        'right_hand': (-0.75, 0, 0, 0, 0, 0),
        'left_hand': (-0.8, 0, 0, 0, 0, 0),
        'right_finger_1': (-0.3, 0, -0.25, 0, 0, 0), 'right_finger_4': (-0.3, 0, 0.3, 0, 0, 0),
        'left_finger_1': (-0.3, 0, 0.25, 0, 0, 0), 'left_finger_4': (-0.3, 0, -0.3, 0, 0, 0),
        'right_finger_2': (-0.3, 0, -0.1, 0, 0, 0), 'right_finger_3': (-0.3, 0, 0.1, 0, 0, 0),
        'left_finger_2': (-0.3, 0, 0.1, 0, 0, 0), 'left_finger_3': (-0.3, 0, -0.1, 0, 0, 0),
        'tail1': (0.15, 0, 0, 0, 0, 0),
    },
    # reveal(): caught by the flash / UV light -- arms thrown up to shield, head twisted away, tail whips
    'revealed': {
        'body': (-0.22, 0.2, 0, 0, 0, 1.5),
        'neck': (0.05, 0.2, 0, 0, 0, 0),
        'head': (0.18, 0.38, 0.22, 0, 0, 0),
        'jaw': (-0.05, 0, 0, 0, 4.5, -0.5),
        'right_arm': (-1.05, -0.55, -0.15, 0, 0, 0),
        'left_arm': (-1.15, 0.6, 0.1, 0, 0, 0),
        'right_forearm': (-0.75, 0.3, 0, 0, 0, 0),
        'left_forearm': (-0.7, -0.3, 0, 0, 0, 0),
        'right_hand': (-0.3, 0, 0, 0, 0, 0),
        'left_hand': (-0.2, 0, 0, 0, 0, 0),
        'tail1': (-0.15, 0, 0.3, 0, 0, 0),
        'tail2': (0.2, 0, 0.45, 0, 0, 0),
        'tail3': (0.2, 0, -0.5, 0, 0, 0),
        'tail4': (0.2, 0, 0.5, 0, 0, 0),
        'hair': (0.1, 0.2, 0, 0, 0, 0),
    },
    # moan (ANIMA_MOAN sound): jaw half open, head rolled to one side, brows lifted
    'moan': {
        'neck': (0.05, 0, 0.12, 0, 0, 0),
        'head': (-0.12, 0.1, 0.3, 0, 0, 0),
        'jaw': (-0.05, 0, 0.05, 0, 3.0, -0.5),
        'brow_right': (0, 0, -0.12, 0, -0.3, 0),
        'brow_left': (0, 0, 0.12, 0, -0.3, 0),
        'cheek_right': (0, 0, 0.06, 0, 0.5, 0),
        'cheek_left': (0, 0, -0.06, 0, 0.5, 0),
        'right_arm': (0.25, 0, 0, 0, 0, 0),
        'left_arm': (0.3, 0, 0, 0, 0, 0),
    },
}

ANIM_NOTES = """
Ánima -- translucent screaming lost soul.  render_type entityTranslucentEmissive (base texture alpha 110-210,
face 205-210, torso 180-196, arms 150-172, fingers/tail/hair tips fading to 110); the 'eyes' layer holds the two
pinprick pupils deep in the sockets and the soul-light between the left ribs.  No legs: it never walks --
drive everything from tickCount / ageInTicks, not walkAnimationPos.  POSES are offsets ADDED to the rest pose
(radians / texels); blend them in over ~4-6 ticks and out over ~8.

BONES
- body (root, pivot at the waist): idle bob +-1.5 texels (sin(age*0.08)) and a slow forward/back lean of
  +-0.05 rad; leans into the drift direction while moving (xRot up to +0.15).
- ribs_right / ribs_left: breathing flex -- zRot +-0.04 rad (mirrored) on a 60-tick cycle, faster (20 ticks)
  while chasing.
- neck: follows head pitch at 40%; small 0.03 rad wobble out of phase with body.
- head: look-at target (yaw clamp +-0.6, pitch clamp +-0.4) plus a random twitch every 40-120 ticks
  (snap +-0.15 rad roll for 2 ticks, ease back).  Thrown back in 'scream', rolled in 'moan', wrenched aside in
  'revealed'.
- brow_right / brow_left: anguish -- inner corners lift further (zRot -/+0.1, dy -0.5) whenever the jaw opens
  past half; tiny tremble at rest.
- skull_back: rigid with the head (no animation; separate only for its back-swept rotation).
- cheek_right / cheek_left: stretched cheek skin + cheekbones -- splay outward (zRot +/-0.1..0.12, dy +1) as the
  jaw drops, so the face looks torn wider; slight lag (2 ticks) behind the jaw.
- jaw: ALWAYS ajar at rest (the long scream is the silhouette).  Idle: slow sag 0..+1 texel dy.  Drops +3 dy
  on 'moan' (ANIMA_MOAN sound), +6.5 on 'scream', +7.5 on 'attack' (the jumpscare portrait uses the attack
  jaw), with a small negative xRot so the chin stays in front of the ribs.  Add a 1-tick 0.5-texel shiver at
  the peak.
- hair: whole-mass drift, xRot -0.1..-0.2 (lifts) in scream / attack.
- hair_1..hair_6 (root segments) and hair_N_tip (second segments): continuous upward/backward drift like hair
  under water -- xRot and zRot sines (amplitude 0.12 root, 0.2 tip), each lock phase-offset by N*0.9 rad and
  the tip lagging its root by ~0.6 rad.  Never synchronised.
- right_arm / left_arm (shoulder): idle sway +-0.08 rad out of phase L/R; reach toward the target while
  chasing (blend toward 'reach').
- right_forearm / left_forearm (elbow): follow the arm with 0.1 rad lag; snap straight in attack.
- right_hand / left_hand (wrist): slow claw droop; flick up (-0.3) on attack.
- right_finger_1..4 / left_finger_1..4 (+ _tip): claw curl -- proximal xRot +0.1..+0.4, tip +0.2..+0.6 on
  attack (grab), splayed (zRot fan) in 'reach'; random single-finger twitches at rest.
- right_thumb / left_thumb: curl with the fingers (xRot +0.3 on grab); keep them turned away from the face.
- shroud_front / shroud_back / shroud_right / shroud_left: tattered strips flutter -- xRot (front/back) and
  zRot (sides) sines, 0.1-0.15 rad, each with its own phase; trail opposite to the movement direction.
- tail1..tail4: sinuous wave -- zRot = A*sin(age*0.12 - k*0.7) and xRot = 0.5*A*sin(age*0.09 - k*0.6) with
  A = 0.06, 0.1, 0.16, 0.24 for k = 1..4 (amplitude grows toward the frayed end); streams back (+xRot) with
  speed.

POSES
- 'drift': default idle float -- arms trail low and back, head hung, hair rising, tail streaming.
- 'reach': chase / the clip money shot -- both claws straight at the camera, fingers splayed, jaw half open.
- 'attack': lunge -- body pitches in (dz -3), jaw wider than the scream, claws forward and curling.
- 'scream': signature shriek (played with the scream sound and before vanishing) -- jaw dislocated to the
  chest, head thrown back, arms raised in a claw spread, cheeks torn wider.
- 'revealed': reveal() (camera flash / UV light, becomeWeakened) -- recoils: arms flung up, head wrenched aside,
  tail whipped into an S.  Hold while isRevealed() and the reveal timer is high, then ease back to 'drift'.
- 'moan': with the ANIMA_MOAN sound -- jaw half open, head rolled to one side, brows lifted.
"""
