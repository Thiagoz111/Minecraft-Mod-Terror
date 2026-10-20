"""Ánima -- the lost soul (DEAD LINE).

Authored at 2x texel density (model.scale = 0.5) in absolute rig coordinates: +Y down, ground y = 24,
faces -Z, right_* on -X.  A ghost: it floats a couple of texels above the ground, 1.9 blocks including the tail.
Design coordinates are shifted into model space by (0, DY, DZ) so the torso sits on the entity origin.

Silhouette: a coffin-shaped, back-swept skull (narrow crown, wide brow and cheekbones, sunken temples,
occipital dome sweeping up and back) on a short vertebral neck.  The jaw is stretched DOWN into a long black
scream (a real 3-deep gullet behind it, faint cyan glow at the back of the throat) framed by bright strands of
torn cheek skin with dark outlines, so the face cuts cleanly against the chest.  Two hollow sockets (brows tilted
up at the inner corners, a thin dark nasal bridge) with burning pinpoint pupils.  Hair: six 3-segment chains,
two locks each, that rise first and then curl back like smoke under water; one lock falls forward over the left
brow.  Rib cage split open at the front (dark hollow, the soul-light glowing between the left ribs) pushed
back behind the jaw.  Over-long arms, narrow claw hands with four 1-texel jointed fingers, knuckle knobs and
black claws.  No legs: tapering shroud ribbons and a four-segment S-curved tail that frays into ribbons.

Colour: luminous teal-white core (face, jaw, cheek strands brightest at alpha 205-210), cyan toward every
silhouette edge, ribs/clavicles two steps darker and more cyan (alpha 150-175), deeper cyan toward the
extremities, darker cyan inside the eyes and the mouth.  Translucent + emissive (entityTranslucentEmissive):
alpha 110..210.  Faces that are never meant to be seen return None (cut out) so nothing ghosts in game.
"""
import math

from mcmodel import Model, hash3, face_light, pick
from rig import Rig
from paint import hx, mix

RIG = None   # set by build(); materials need absolute pivots
DY = 3.5     # design frame -> model frame vertical offset (materials work in design coordinates)
DZ = -5.0    # design frame -> model frame depth offset (centres the torso on the entity origin)

# ------------------------------------------------------------------ palettes (hand-picked, hue shifted)
# one luminous ramp: blue-black teal -> saturated cyan mids -> mint/teal-white core
GHOST = [hx(c) for c in ('#020f15', '#05232c', '#093a45', '#0e5360', '#156e7a', '#1f8b94',
                         '#35a9ad', '#62c7c3', '#98e2d9', '#c6f5ec', '#e8fffa')]
VOID = [hx(c) for c in ('#000203', '#01090c', '#031418', '#062229', '#0a333c', '#0f4853')]
HAIR = [hx(c) for c in ('#010a0e', '#03161d', '#06232c', '#0b343f', '#124855', '#1c606b', '#2b7d84',
                        '#43a0a0', '#73c6c0', '#a8e6de')]
TEETH = [hx(c) for c in ('#0f3236', '#235a5b', '#3f807c', '#6aa59c', '#9fd0c4', '#cdeee4')]
CYAN = hx('#3fe3ec')
CYAN_D = hx('#127e8c')
TEAR = hx('#011419')
SOUL = [hx('#7fe9e0'), hx('#c4fff7'), hx('#f2fffd')]
GLOW_EYE = (236, 255, 252, 255)
GLOW_EYE2 = (96, 236, 244, 255)
GLOW_RING = (14, 74, 84, 255)
GLOW_THROAT = (12, 70, 80, 255)
GLOW_THROAT2 = (26, 128, 138, 255)
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
    return p[0] + o[0] + lx, p[1] + o[1] + ly - DY, p[2] + o[2] + lz - DZ


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


def across(ctx):
    """0 at the centre line of a face, 1 at its long edges (across the strand / limb)."""
    return abs(2.0 * ctx.s - 1.0)


def glow(ctx, v, a, cyan=0.4, fk=0.45, deep=0.0):
    """Value -> luminous ramp, cyan creeping in toward the face edges and on sideways faces."""
    c = pick(GHOST, v)
    ex = across(ctx)
    c = mix(c, CYAN, cyan * ex ** 3)
    if deep:
        c = mix(c, CYAN_D, deep)
    return A(fres(c, ctx, fk), a)


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
CRACK = {(1, -35), (1, -34), (1, -33), (1, -32), (1, -31), (2, -31), (2, -30), (2, -29), (3, -29)}  # crown -> left brow
HAIRLINE = {(-4, -32), (-4, -31), (-3, -31), (-3, -30),           # forehead, right side
            (-7, -30), (-6, -30), (-6, -29), (-6, -28),            # right temple
            (5, -31), (5, -30), (6, -30),                          # left temple
            (-5, -19), (-4, -19), (-4, -18)}                       # right cheekbone
CRACK_HI = {(x + 1, y) for (x, y) in CRACK | HAIRLINE if (x + 1, y) not in CRACK | HAIRLINE}
TEARS = {-4: (-21, -6), -3: (-19, -10), 4: (-21, -8)}  # column x -> (start y, end y): black tear streaks
HIDDEN_BACK = ('forehead', 'brow', 'rim', 'bridge', 'cheekbone', 'maxilla')


def socket_d(x, y):
    """Normalised distance to the nearest eye-socket centre (< 1 inside the socket)."""
    best = 9.0
    for sx, sy in ((-2.9, -22.5), (2.9, -22.1)):
        best = min(best, ((x - sx) / 2.35) ** 2 + ((y - sy) / 3.7) ** 2)
    return best


def skull_mat(ctx):
    """Head bone pieces: forehead, vault, crown, brow halves, bridge, rims, cheekbones, maxilla."""
    t = tag(ctx)
    f = ctx.face
    x, y, z = apos(ctx)
    cx, cy = int(math.floor(x)), int(math.floor(y))
    lx, ly, lz = loc(ctx)
    w, h, d = ctx.cube.size
    if t == 'midface':
        return midface_mat(ctx)
    # never-seen faces are cut out (no ghosting / coplanar shimmer under translucency)
    if f == 'back' and t in HIDDEN_BACK:
        return None
    if t == 'vault' and f == 'front' and abs(x) < 5 and y < -28:
        return None
    if t == 'vault' and f == 'bottom':
        if z > -4 and abs(x) < 6:
            return None
        return A(pick(VOID, 0.75), 208)     # roof of the sockets
    if t in ('crown', 'vault_hi') and f == 'bottom':
        return None
    if t == 'rim' and f in ('top', 'bottom'):
        return None
    if f == 'front':
        if (cx, cy) in CRACK and t in ('forehead', 'crown', 'vault', 'vault_hi', 'cheekbone'):
            return A(VOID[2], 210)
        hairline = (cx, cy) in HAIRLINE and t in ('forehead', 'crown', 'vault', 'vault_hi', 'cheekbone')
        j, H = ctx.j, ctx.h
        if t == 'forehead':
            v = 0.99 - (abs(x) / 5.0) ** 2 * 0.24
            if j == 0:
                v -= 0.07                       # curving away at the hairline
            if j == H - 1:
                v += 0.02                       # brow-ridge highlight just above the brows
            if abs(x) < 0.6 and j < 2:
                v -= 0.08                       # metopic suture
        elif t in ('vault', 'vault_hi'):
            v = 0.86 - clamp((abs(x) - 3.5) / 3.5) * 0.32   # temples fall into shadow
            if y > -28:
                v -= 0.12
        elif t == 'crown':
            v = 0.8 - (abs(x) / 3.0) ** 2 * 0.12
            if j == 0:
                v -= 0.08
        elif t == 'brow':
            v = 0.93
            if j == 0:
                v = 1.0                         # brow highlight row
            if j == H - 1:
                v = 0.5                         # dark ring over the socket
            k = ctx.i if ctx.bone.name == 'brow_left' else (w - 1 - ctx.i)  # 0 = inner corner
            if k == 0:
                v -= 0.1
        elif t == 'rim':
            v = 0.5                             # orbit rim: darker ring around the socket
        elif t == 'bridge':
            return A(pick(VOID, 0.82 - j * 0.08), 206)
        elif t == 'cheekbone':
            v = 0.92
            if j == 0:
                v = 0.5                         # lower socket rim ring
            far = abs(x) > 5.5
            if far:
                v -= 0.16
            if (cx in TEARS) and TEARS[cx][0] <= cy <= TEARS[cx][1] and j > 0:
                return A(TEAR, 210)
        elif t == 'maxilla':
            if j == H - 1:
                return A(VOID[1], 210)          # black gum line
            v = 0.8 - abs(x) / 4.0 * 0.16
        else:
            v = 0.8
        if (cx, cy) in CRACK_HI and t in ('forehead', 'crown', 'vault', 'vault_hi'):
            v += 0.06
        if hairline:
            v -= 0.34
        return glow(ctx, v, 208, cyan=0.25, fk=0.0)
    if f == 'bottom':
        if t in ('brow', 'cheekbone', 'maxilla', 'bridge'):
            return A(pick(VOID, 0.7), 210)      # undersides drop into the sockets / mouth
        return A(pick(GHOST, 0.3), 205)
    if f == 'top':
        if t == 'cheekbone':
            return A(pick(VOID, 0.9), 206)      # floor of the socket
        v = 0.8 + face_light(ctx) * 0.3
        if t in ('crown', 'vault', 'vault_hi'):
            # hair roots streaming back over the scalp (dark), sagittal + coronal sutures
            if t == 'crown' or abs(x) < 4.5:
                if h2(cx, 3, 41) > 0.45:
                    return A(HAIR[2 + int(h2(cx, 4, 42) * 3)], 200)
            if abs(x) < 0.6:
                v -= 0.2
            if abs(z - (-1.0 + (cx % 2) * 0.8)) < 0.5:
                v -= 0.18
        return glow(ctx, v, 202, cyan=0.2, fk=0.25)
    # west / east sides
    inner = (f == 'east' and x < 0) or (f == 'west' and x > 0)
    if t in ('rim', 'bridge') or (t in ('brow', 'cheekbone') and inner):
        return A(mix(pick(VOID, 0.95), CYAN_D, 0.25 + 0.2 * (1 - lz / max(1, d))), 206)  # socket walls
    v = 0.66 + face_light(ctx)
    if t in ('vault', 'vault_hi'):
        # sunken temple, hand-placed squamosal suture
        if z < -2 and y > -29:
            v -= 0.16
        if abs((y + 29.5) - abs(z + 0.5) * 0.35) < 0.5 and z > -3:
            v -= 0.22
    v -= (lz / max(1, d)) * 0.16
    return A(fres(pick(GHOST, v), ctx, 0.45), 200)


def midface_mat(ctx):
    """The deep plane behind the face frame: hollow sockets, nasal cavity; temples on its sides."""
    f = ctx.face
    x, y, z = apos(ctx)
    if f == 'front':
        if -1.6 < x < 1.6 and -21 < y < -17:
            if abs(x) < 0.5 + (y + 21) * 0.3:
                return A(VOID[0], 210)          # nasal cavity (inverted heart)
        dd = socket_d(x, y)
        if dd < 1.0:
            if dd > 0.62:
                return A(VOID[4], 210)          # darker-cyan inner wall ring
            return A(VOID[0], 210)
        if dd < 1.45:
            return A(pick(GHOST, 0.42), 208)    # rim of the hole
        v = 0.6 - clamp((y + 19.5) / 2.5) * 0.15
        return A(pick(GHOST, v), 208)           # recessed bone between and around the sockets
    if f == 'top':
        return None                             # buried under the vault
    if f == 'back':
        return A(VOID[2], 200)
    if f in ('west', 'east'):
        # sunken temples / gaunt cheek hollow: gradient into a deep hollow under the cheekbone
        v = 0.6 + face_light(ctx) - clamp((y + 23) / 5) * 0.22
        if z < -2.5:
            v -= 0.12
        return A(fres(pick(GHOST, v), ctx, 0.5), 202)
    return A(VOID[2], 205)


def occ_mat(ctx):
    """Back-swept occipital dome: pale bone, hand-placed lambdoid suture and two cracks, hair roots on top."""
    f = ctx.face
    x, y, z = apos(ctx)
    lx, ly, lz = loc(ctx)
    w, h, d = ctx.cube.size
    if f == 'front':
        return None                              # buried inside the vault
    v = 0.74 + face_light(ctx) * 0.9
    if f == 'top':
        col = int(math.floor(x))
        if h2(col, int(lz) // 3, 51) > 0.35:
            return A(HAIR[1 + int(h2(col, 5, 52) * 4)], 196)
    if f == 'back':
        i, j = ctx.i, ctx.j
        zz = abs(i - (w - 1) / 2.0) * 0.55 + (i % 2) * 0.8
        if abs(j - (1.2 + zz)) < 0.55:
            v -= 0.26
        if (i, j) in ((2, 3), (2, 4), (3, 5), (w - 3, 2), (w - 4, 3)):
            v -= 0.32
        v -= j / max(1, h) * 0.14
    if f in ('west', 'east'):
        v -= lz / max(1, d) * 0.12
        if ctx.j == ctx.h - 1:
            v -= 0.12
    return A(fres(pick(GHOST, v), ctx, 0.5), 198)


def tooth_mat(ctx):
    lx, ly, lz = loc(ctx)
    h = ctx.cube.size[1]
    up = ctx.bone.name == 'head'
    tip = ly / max(1.0, h) if up else 1 - ly / max(1.0, h)  # 0 at the gum, 1 at the tip
    if ctx.face == 'back' or (ctx.face == 'top' and up) or (ctx.face == 'bottom' and not up):
        return None
    v = 0.62 + tip * 0.32 + face_light(ctx) * 0.5
    if ctx.face in ('west', 'east'):
        v -= 0.25
    if tip < 0.2:
        v = 0.12  # stained root at the gum line
    return A(pick(TEETH, v), 206)


def throat_mat(ctx):
    """Mouth void: black core, darker cyan toward the cheeks (head throat + the jaw's 3-deep gullet)."""
    x, y, z = apos(ctx)
    f = ctx.face
    if f in ('front', 'top'):
        dd = abs(x) / 3.0
        c = mix(VOID[0], VOID[4], clamp(dd * dd * 1.2 - 0.15))
        return A(c, 210)
    return A(VOID[1], 210)


def strand_mat(ctx):
    """Stretched cheek skin: one sheet per side from the cheekbone down past the jaw corner.  Its outer
    edge slants in toward the chin (coffin-shaped lower face) with a dark outline column; the inner edge is
    the lip of the scream."""
    lx, ly, lz = loc(ctx)
    w, h, d = ctx.cube.size
    p = ly / max(1, h)
    right = ctx.bone.name == 'cheek_right'
    u = int(math.floor(lx))
    k = u if right else (w - 1 - u)  # 0 = outer edge, w-1 = inner (mouth) edge
    lost = int(p * 3.4)
    if k < lost:
        return None
    if p > 0.88 and (k + int(ly)) % 2 == 0 and k != w - 1:
        return None
    x, y, z = apos(ctx)
    if k == lost:
        return A(VOID[2], 208)          # dark outline: the lower face cuts against the chest
    if k == 2 and 0.4 < p < 0.6:
        return A(VOID[1], 206)          # torn slit in the skin
    if int(math.floor(x)) in TEARS and TEARS[int(math.floor(x))][0] <= y <= TEARS[int(math.floor(x))][1] + 2:
        return A(TEAR, 208)
    v = 0.98 - p * 0.3
    if k == w - 1:
        v -= 0.16                       # lip edge folds into the mouth
    if k == lost + 1:
        v -= 0.05
    c = pick(GHOST, v)
    if p > 0.72:
        c = mix(c, CYAN, (p - 0.72) * 0.8)
    return A(c, 210 - p * 40)


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
        return None
    if t in ('ramus', 'corner'):
        inner = (f == 'east' and x < 0) or (f == 'west' and x > 0)
        if inner:
            return A(pick(VOID, 0.5 + ly / h * 0.4), 210)    # wet dark inside of the cheek
        outer = (f == 'west' and x < 0) or (f == 'east' and x > 0)
        if f == 'front':
            # outer column = dark outline, inner column = bright bone
            k = ctx.i if x > 0 else (w - 1 - ctx.i)  # 0 inner .. w-1 outer
            if w > 1 and k == w - 1:
                return A(VOID[2], 210)
            v = 0.97 - ly / h * 0.12
            if ctx.j % 5 == 4:
                v -= 0.08
            return A(pick(GHOST, v), 208)
        if f == 'top':
            return A(pick(GHOST, 0.6), 204)
        if f == 'bottom':
            return A(pick(VOID, 0.6), 206)
        if outer:
            return A(mix(pick(VOID, 0.75), CYAN_D, 0.3), 206)  # outline seen in 3/4
        return A(pick(VOID, 0.6), 206)
    # chin + chin point
    if f == 'top':
        if t == 'chin':
            return A(pick(VOID, 0.5 if ctx.edge() == 0 else 0.15), 210)  # floor of the mouth
        return None
    if f == 'front':
        if t == 'chin' and ctx.j == 0:
            return A(VOID[2], 210)  # lower gum line
        if ctx.i == 0 or ctx.i == ctx.w - 1:
            return A(VOID[3], 210)  # outline
        v = 0.98 - abs(x) / 2.5 * 0.14 - (0.06 if t == 'chinpt' else 0.0)
        if ctx.j == ctx.h - 1:
            v -= 0.2
        if t == 'chin' and (int(math.floor(x)), ctx.j) in ((-1, 1), (1, 2)):
            v -= 0.3  # chipped bone
        return A(pick(GHOST, v), 208)
    if f == 'bottom':
        return A(pick(GHOST, 0.42), 204)
    v = 0.62 + face_light(ctx)
    return A(fres(pick(GHOST, v), ctx, 0.5), 202)


def bone_mat(ctx):
    """Ribs, clavicles, shoulders, vertebrae, scapulae: they sit BEHIND the face, so they stay two steps
    darker and more cyan than the skull (and more transparent) to keep the figure-ground of the scream."""
    t = tag(ctx)
    f = ctx.face
    x, y, z = apos(ctx)
    lx, ly, lz = loc(ctx)
    w, h, d = ctx.cube.size
    j, H = ctx.j, ctx.h
    lit = face_light(ctx) * 0.9
    if t in ('ribf', 'ribs'):
        if f == 'back':
            return None if t == 'ribf' else A(pick(GHOST, 0.3), 150)
        v = 0.56 + lit
        if f in ('front', 'west', 'east'):
            if j == 0:
                v += 0.1                        # top edge catches the light
            elif j == H - 1:
                v -= 0.18
        if t == 'ribs':
            v -= 0.08 + clamp(lz / max(1, d)) * 0.24  # curving away toward the spine
            a = 156
        else:
            a = 172
            ex = abs(x) - 5.0
            if f == 'front' and ex < 1.0:
                v += 0.04                       # broken inner end, a touch paler
            if f == 'front' and abs(x) > 9:
                v -= 0.08
        c = mix(pick(GHOST, v), CYAN, 0.16)
        return A(fres(c, ctx, 0.35), a)
    if t == 'clav':
        v = 0.56 + lit
        if j == H - 1:
            v -= 0.14
        return A(fres(mix(pick(GHOST, v), CYAN, 0.16), ctx, 0.35), 168)
    if t in ('vert', 'spine'):
        v = 0.66 + lit
        if j == H - 1:
            v -= 0.22
        if j == 0:
            v += 0.06
        return A(fres(pick(GHOST, v), ctx, 0.45), 186 if t == 'vert' else 176)
    if t == 'shoulder':
        v = 0.64 + lit
        if f == 'top' and ctx.edge() > 0:
            v += 0.08
        if f in ('front', 'back', 'west', 'east') and j == H - 1:
            v -= 0.14
        return A(fres(pick(GHOST, v), ctx, 0.45), 182)
    if t == 'tendon':
        v = 0.55 + lit
        return A(fres(pick(GHOST, v), ctx, 0.5), 176)
    if t == 'scap':
        v = 0.7 - j / max(1, H) * 0.3 + lit
        if j == 0:
            v += 0.08
        if f == 'back' and (ctx.i == 0 or ctx.i == ctx.w - 1):
            v -= 0.14
        return A(fres(pick(GHOST, v), ctx, 0.4), 178)
    if t == 'yoke':
        v = 0.52 + lit
        if f == 'front':
            return None                         # hidden against the backplate
        return A(fres(pick(GHOST, v), ctx, 0.45), 178)
    v = 0.6 + lit
    return A(fres(pick(GHOST, v), ctx, 0.45), 180)


def backplate_mat(ctx):
    """Front: the dark hollow of the open chest lit by the soul.  Back: skin drawn over spine and ribs."""
    f = ctx.face
    x, y, z = apos(ctx)
    if f == 'front':
        dd = math.sqrt((x - 5.5) ** 2 + ((y + 8) * 0.8) ** 2) / 7.0
        return A(pick(VOID, 0.92 - dd * 0.8), 188)
    v = 0.5 + face_light(ctx)
    if f == 'back':
        # ribs arching out from the spine under the skin, spine groove, waist narrowing into shadow
        ry = (y + 100 + abs(x) * 0.35) % 3.1
        if ry < 1.0:
            v -= 0.12
        elif ry < 2.0:
            v += 0.06
        if abs(x) < 1.5:
            v -= 0.14
        if abs(x) > 5.5:
            v -= 0.1
        v -= clamp((y + 5) / 5) * 0.15
        return glow(ctx, v, 184, cyan=0.5, fk=0.4)
    return glow(ctx, v - 0.05, 180, cyan=0.3, fk=0.5)


def soul_mat(ctx):
    e = ctx.edge()
    c = SOUL[2] if e > 0 else SOUL[1]
    if ctx.face in ('bottom', 'back'):
        c = SOUL[0]
    return A(c, 205)


def waist_mat(ctx):
    x, y, z = apos(ctx)
    f = ctx.face
    if f == 'top':
        return None
    v = 0.56 + face_light(ctx)
    if f in ('front', 'back'):
        ex = across(ctx)
        v += 0.22 * (1 - ex * ex) - 0.06   # lumbar core glow
        if abs(x) < 0.6 and int(y + 100) % 2 == 0:
            v -= 0.14                      # vertebrae pressing through
    return glow(ctx, v, 184, cyan=0.6, fk=0.45)


ARM_ALPHA = {'upper': 182, 'knob': 186, 'fore': 176, 'wrist': 178, 'palm': 172, 'knuckle': 180,
             'finger': 166}


def arm_mat(ctx):
    """Emaciated limbs: bright bone ridges down the middle, cyan toward the edges, deeper cyan toward the
    claws; elbow/knuckle highlights, wrist creases, faint dark-cyan veins, black claws."""
    n = ctx.bone.name
    t = tag(ctx)
    f = ctx.face
    x, y, z = apos(ctx)
    lx, ly, lz = loc(ctx)
    w, h, d = ctx.cube.size
    if t == 'drape':
        return ecto_mat(ctx)
    if t == 'claw':
        if f == 'top':
            return None
        p = ly / max(1, h)
        c = mix(VOID[1], CYAN, 0.06 + (0.22 if (f == 'front' and p < 0.4) else 0.0))
        return A(c, 204)
    j, H, i, W = ctx.j, ctx.h, ctx.i, ctx.w
    a = ARM_ALPHA.get(t, 170)
    lit = face_light(ctx)
    p = ly / max(1, h)
    side = 1 if x > 0 else -1
    deep = 0.0
    if t == 'upper':
        v = 0.66 - p * 0.1 + lit
        if f in ('front', 'back'):
            v += 0.16 * (1 - across(ctx) ** 2)   # humerus ridge
            # meandering vein down the arm
            vc = 1 + int(round(math.sin(ly * 0.55 + side * 1.3)))
            if i == vc and 2 < ly < h - 2 and f == 'front':
                v -= 0.2
        if j == 0 and f != 'top':
            v -= 0.08
    elif t == 'knob':                           # elbow
        v = 0.8 + lit
        if j == 0:
            v += 0.08
        if j == H - 1:
            v -= 0.34
    elif t == 'fore':
        v = 0.6 - p * 0.08 + lit
        if f in ('front', 'back'):
            if i == 0 or i == W - 1:
                v += 0.14                       # ulna / radius ridges
            else:
                v -= 0.12                       # groove between them
            if i == 1 and (j + 2) % 5 == 0:
                v -= 0.1                        # vein crossing
        deep = 0.08
    elif t == 'wrist':
        v = 0.66 + lit
        if j == H - 1:
            v -= 0.3                            # wrist crease
        deep = 0.1
    elif t == 'palm':
        v = 0.58 + lit
        if f == 'front':
            if i % 2 == 0:
                v += 0.12                       # metacarpal ridges
            else:
                v -= 0.08
            if j == H - 1:
                v += 0.1                        # knuckle line highlight
            if j == 0:
                v -= 0.14                       # wrist crease
        if f == 'back' and j in (1, 3) and 0 < i < W - 1:
            v -= 0.16                           # palm creases
        deep = 0.14
    elif t == 'knuckle':
        if f == 'back':
            return None
        v = 0.84 + lit * 0.5
        if f == 'bottom':
            v -= 0.3
        deep = 0.05
    else:                                       # finger / thumb segments
        if f == 'top' and 'tip' in n:
            return None
        tipseg = 'tip' in n
        v = 0.68 - p * 0.14 - (0.08 if tipseg else 0.0) + lit
        if j == 0 and f in ('front', 'west', 'east'):
            v += 0.12                           # joint highlight
        if j == H - 1 and f != 'bottom':
            v -= 0.14                           # knuckle crease
        deep = 0.16 if not tipseg else 0.24
        a = 166 if not tipseg else 156
    if f in ('front', 'back') and t in ('upper', 'fore', 'palm'):
        pass
    c = pick(GHOST, v)
    c = mix(c, CYAN, 0.35 * across(ctx) ** 3)
    if deep:
        c = mix(c, CYAN_D, deep)
    return A(fres(c, ctx, 0.45), a)


def ecto_mat(ctx):
    """Ectoplasm: tail, shroud ribbons, sleeve drapes.  A luminous near-white core streak runs down the
    middle of each part, fading to cyan edges and then to a transparent fray (columns end at their own
    length, no random holes)."""
    n = ctx.bone.name
    t = tag(ctx)
    f = ctx.face
    x, y, z = apos(ctx)
    lx, ly, lz = loc(ctx)
    w, h, d = ctx.cube.size
    if t in ('tatter', 'drape', 'ribbon'):
        p = ly / max(1, h)
        u, W = plane_u(ctx)
        seed = int(abs(ctx.cube.origin[0]) * 3 + abs(ctx.cube.origin[2]) * 5) + len(n)
        end = 0.66 + 0.34 * h2(u, seed, 61)
        if t != 'drape' and W > 1 and u in (0, W - 1):
            end = min(end, 0.8)
        if p > end:
            return None
        if t == 'ribbon' and not tapered(ctx, p, lean=ctx.cube.origin[0] > 0):
            return None
        uc = abs((u + 0.5) / W * 2 - 1)        # 0 centre .. 1 edge
        v = 0.86 - p * 0.36 - uc * 0.26 + (h2(u, seed, 62) - 0.5) * 0.1
        if W > 2 and (u == 0 or u == W - 1):
            v -= 0.06
        c = pick(GHOST, v)
        c = mix(c, CYAN, clamp(uc * 0.5 + p * 0.3))
        a0 = {'tatter': 176, 'drape': 160, 'ribbon': 168}[t]
        return A(fres(c, ctx, 0.3), a0 - p * 58)
    # tail segments: core streak, thinner and deeper with distance from the body
    k = int(n[-1]) if n[-1].isdigit() else 1
    p = ly / max(1, h)
    if f == 'top' and k > 1:
        return None
    ex = across(ctx) if f in ('front', 'back', 'top', 'bottom') else across(ctx) * 0.6 + 0.4
    v = 0.92 - k * 0.05 - ex * ex * 0.42 - p * 0.05 + face_light(ctx) * 0.7
    col = int(math.floor(lx if f in ('front', 'back', 'top', 'bottom') else lz))
    if f in ('front', 'back') and (col + k) % 3 == 0 and ex > 0.3:
        v -= 0.06                              # flow lines
    c = pick(GHOST, v)
    c = mix(c, CYAN, clamp(ex ** 2 * 0.6 + k * 0.04))
    a = {1: 186, 2: 172, 3: 156, 4: 140}[k] - p * 10 - ex * 14
    return A(fres(c, ctx, 0.4), a)


HAIR_SEG = {'': 0, 'mid': 1, 'tip': 2}


def hair_mat(ctx):
    """Locks drifting up and back: dark teal roots framing the skull, light catching along the strand,
    pale glowing cyan tips that taper and fade."""
    n = ctx.bone.name
    t = tag(ctx)
    lx, ly, lz = loc(ctx)
    w, h, d = ctx.cube.size
    suffix = n.split('_')[-1]
    seg = HAIR_SEG.get(suffix if not suffix.isdigit() else '', 0)
    p0 = 1 - ly / max(1, h)        # 0 at the root end of this segment, 1 at its far end
    p = (seg + p0) / 3.0
    sib = t == 'lock2'
    if not tapered(ctx, p0 * 0.55 + seg * 0.15, lean=(len(n) + int(ctx.cube.origin[0] * 2) + sib) % 2):
        return None
    u, W = plane_u(ctx)
    s = h2(u, len(n) + int(ctx.cube.origin[2] * 3) + sib * 5, 81)
    v = 0.3 + p * 0.68 + (s - 0.5) * 0.16 - (0.08 if sib else 0.0)
    if u == 0 and W > 1:
        v -= 0.08
    c = pick(HAIR, v)
    if p > 0.62:
        c = mix(c, CYAN, (p - 0.62) * 1.1)
    if seg == 2 and p0 > 0.75:
        c = mix(c, hx('#d8fff8'), (p0 - 0.75) * 1.6)
    return A(c, 200 - p * 88)


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
    """Midface front (x -6..6, y -26..-17): a faint darker-cyan ring on the socket walls and a burning 2x2
    pupil with a 1-texel halo deep in each socket, staring slightly inward (at the viewer); the left one a
    texel lower -- asymmetric and wrong."""
    px = img.load()
    for j in range(h):
        for i in range(w):
            x, y = -6 + i + 0.5, -26 + j + 0.5
            dd = socket_d(x, y)
            if 0.62 < dd < 1.0:
                px[u0 + i, v0 + j] = GLOW_RING
    for (ci, cj) in ((2, 3), (8, 4)):
        for (i, j) in ((ci - 1, cj), (ci - 1, cj + 1), (ci + 2, cj), (ci + 2, cj + 1),
                       (ci, cj - 1), (ci + 1, cj - 1), (ci, cj + 2), (ci + 1, cj + 2)):
            if 0 <= i < w and 0 <= j < h:
                px[u0 + i, v0 + j] = GLOW_EYE2
        for (i, j) in ((ci, cj), (ci + 1, cj), (ci, cj + 1), (ci + 1, cj + 1)):
            if 0 <= i < w and 0 <= j < h:
                px[u0 + i, v0 + j] = GLOW_EYE


def eyes_wall(img, u0, v0, w, h):
    """Inner socket walls (rims, bridge sides): a dim darker-cyan glow so the sockets read in fog."""
    px = img.load()
    for j in range(h):
        for i in range(w):
            px[u0 + i, v0 + j] = GLOW_RING


def eyes_throat(img, u0, v0, w, h):
    """Back of the gullet: a dim cyan glow deep in the throat, brightest low in the middle."""
    px = img.load()
    for j in range(h):
        for i in range(w):
            dx = ((i + 0.5) / w - 0.5) / 0.42
            dy = ((j + 0.5) / h - 0.6) / 0.42
            r = dx * dx + dy * dy
            if r < 0.35:
                px[u0 + i, v0 + j] = GLOW_THROAT2
            elif r < 1.0:
                px[u0 + i, v0 + j] = GLOW_THROAT


def eyes_soul(img, u0, v0, w, h):
    px = img.load()
    for j in range(h):
        for i in range(w):
            e = min(i, j, w - 1 - i, h - 1 - j)
            px[u0 + i, v0 + j] = GLOW_SOUL if e > 0 else GLOW_SOUL2


# ------------------------------------------------------------------ build
# hair chains: root (x, y, z), segments [(length, back deg, out deg, width)], sibling lock (dx, dz, dlen, w)
HAIR_CHAINS = [
    ((-6.2, -30.5, -3.0), [(6, 8, 30, 4), (5, 30, 24, 3), (8, 40, 14, 2)], (-1.0, 1.6, 1, 2)),   # right temple
    ((6.2, -30.0, -2.5), [(6, 10, 32, 4), (6, 22, 20, 3), (8, 44, 12, 2)], (1.0, 1.6, -1, 2)),   # left temple
    ((-3.0, -34.0, -1.0), [(5, 36, 10, 3), (6, 38, 10, 2), (8, 36, 6, 2)], (-1.2, 1.8, 1, 2)),   # right crown
    ((2.6, -34.2, 0.0), [(5, 40, 8, 3), (6, 34, 14, 2), (8, 40, 8, 2)], (1.2, 1.8, 1, 2)),       # left crown
    ((0.0, -33.5, 2.5), [(5, 52, -4, 3), (7, 30, 8, 2), (9, 26, -8, 2)], (1.4, 1.6, -1, 2)),     # back centre
    ((4.6, -33.0, -4.4), [(4, -26, 34, 3), (5, -122, 8, 2), (8, -26, -6, 2)], (-1.0, 0.8, -1, 1)),  # falls forward
]


def build():
    global RIG
    r = Rig()
    RIG = r

    def bone(name, pivot, parent=None, rot=(0, 0, 0)):
        return r.bone(name, (pivot[0], pivot[1] + DY, pivot[2] + DZ), parent=parent, rot=rot)

    def B(bn, frm, size, name, **kw):
        c = r.box(bn, (frm[0], frm[1] + DY, frm[2] + DZ), size, **kw)
        c.name = name
        return c

    # ---------------- body (root): waist pivot, leaning into the drift.  The rib cage is split open at the
    # front and pushed back (ribs front at z=0) so the hanging jaw always reads in front of a dark hollow.
    bone('body', (0, 0, 4), rot=(8, 0, 0))
    B('body', (-7, -17, 7), (14, 9, 2), 'backplate')
    B('body', (-5, -8, 7), (10, 7, 2), 'backplate')
    B('body', (4, -10, 3), (3, 4, 3), 'soul',
      decals={'eyes:front': eyes_soul, 'eyes:west': eyes_soul, 'eyes:east': eyes_soul, 'eyes:top': eyes_soul})
    B('body', (-3, -3, 2.5), (6, 5, 4), 'waist')
    B('body', (-12.5, -19.5, 2.5), (3, 3, 4), 'shoulder')
    B('body', (9.5, -19.5, 2.5), (3, 3, 4), 'shoulder')
    B('body', (-9, -18, 7.1), (18, 2, 2), 'yoke')            # behind the backplate top, out of the maw
    B('body', (-10.5, -18.2, 1), (6, 1, 2), 'clav')            # clavicles end at the shoulders
    B('body', (4.5, -18.2, 1), (6, 1, 2), 'clav')
    for y in (-17, -14, -11, -8, -5, -2):
        B('body', (-1, y, 9), (2, 2, 2), 'spine')
    B('body', (-7, -16, 9), (4, 6, 1), 'scap')
    B('body', (3, -16, 9), (4, 6, 1), 'scap')

    # ---------------- rib cage: separate slats sloping down and out from a broken-open front
    bone('ribs_right', (-5, -16, 0.5), parent='body', rot=(0, 0, -12))
    bone('ribs_left', (5, -16, 0.5), parent='body', rot=(0, 0, 12))
    for k, w in enumerate((4, 5, 6, 5, 4)):
        y = -15.5 + 3.1 * k
        B('ribs_right', (-5 - w, y, 0), (w, 2, 2), 'ribf')
        B('ribs_right', (-5 - w, y, 2), (2, 2, 6), 'ribs')
        B('ribs_left', (5, y, 0), (w, 2, 2), 'ribf')
        B('ribs_left', (3 + w, y, 2), (2, 2, 6), 'ribs')

    # ---------------- neck: visible vertebrae between the skull base and the shoulders
    bone('neck', (0, -17, 5), parent='body', rot=(-10, 0, 0))
    B('neck', (-1.5, -25, 1), (3, 2, 3), 'vert')
    B('neck', (-1.5, -22.5, 2), (3, 2, 3), 'vert')
    B('neck', (-1.5, -20, 3), (3, 2, 3), 'vert')
    B('neck', (-2.5, -24, 1.5), (1, 7, 1), 'tendon')
    B('neck', (1.5, -24, 1.5), (1, 7, 1), 'tendon')

    # ---------------- head: coffin skull, recessed face frame (two hollow sockets 4.5 x 6.5, 2-4 deep)
    bone('head', (0, -25, 2), parent='neck', rot=(-6, 0, 5))
    wall = {'eyes:east': eyes_wall, 'eyes:west': eyes_wall}
    B('head', (-7, -31, -6), (14, 5, 10), 'vault')
    B('head', (-5, -33, -5), (10, 2, 9), 'vault_hi')
    B('head', (-3, -35, -3.5), (6, 2, 7), 'crown')
    B('head', (-5, -32, -7), (10, 4, 1), 'forehead')
    B('head', (-6, -26, -4), (12, 9, 5), 'midface', decals={'eyes:front': eyes_sockets})
    B('head', (-6, -25, -6), (1, 6, 2), 'rim', decals={'eyes:east': eyes_wall})
    B('head', (5, -25, -6), (1, 6, 2), 'rim', decals={'eyes:west': eyes_wall})
    B('head', (-0.5, -26, -6.5), (1, 5, 2), 'bridge', decals=dict(wall))
    B('head', (-4, -17.5, -7.5), (8, 2, 3), 'maxilla')
    B('head', (-3, -17, -4.4), (6, 18, 3), 'throat')    # the upper gullet: 3 deep, ends at the rest chin
    for tx, ty, th in ((-3, -15.5, 2), (-1.8, -15.5, 4), (-0.5, -15.5, 1), (1.2, -15.5, 3), (2.2, -15.5, 1)):
        B('head', (tx, ty, -7), (1, th, 1), 'tooth')

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

    # cheekbones (angled, outer ends drooping) + stretched cheek skin converging toward the chin
    bone('cheek_right', (-2.5, -19, -7), parent='head', rot=(0, 16, -9))
    B('cheek_right', (-8, -19.5, -7), (6, 2, 3), 'cheekbone')
    B('cheek_right', (-7, -17.5, -8.1), (4, 15, 0), 'strand')
    bone('cheek_left', (2.5, -19, -7), parent='head', rot=(0, -16, 9))
    B('cheek_left', (2, -19.5, -7), (6, 2, 3), 'cheekbone')
    B('cheek_left', (3, -17.5, -8.1), (4, 15, 0), 'strand')

    # ---------------- jaw: long, hanging open; 2-wide rami with dark outer outlines; a real 3-deep gullet
    bone('jaw', (0, -17, -4.5), parent='head')
    B('jaw', (-5, -16, -7.5), (2, 12, 3), 'ramus')
    B('jaw', (3, -16, -7.5), (2, 12, 3), 'ramus')
    B('jaw', (-2, -4, -8.5), (4, 3, 4), 'chin')
    B('jaw', (-1, -1, -8), (2, 2, 3), 'chinpt')
    B('jaw', (-4, -6, -7.5), (2, 3, 3), 'corner')   # the mouth narrows to a point at the bottom
    B('jaw', (2, -6, -7.5), (2, 3, 3), 'corner')
    B('jaw', (-3, -14, -5.4), (6, 12, 3), 'throat', decals={'eyes:front': eyes_throat})
    for tx, th in ((-1.8, 5), (-0.6, 2), (1.0, 4)):
        B('jaw', (tx, -4 - th, -7.6), (1, th, 1), 'tooth')

    # ---------------- hair: 3-segment chains (two locks each) that rise first, then curl back
    bone('hair', (0, -34, 0), parent='head')
    for k, ((hx_, hy, hz), segs, (sdx, sdz, sdl, sw)) in enumerate(HAIR_CHAINS):
        sgn = 1 if hx_ > 0 else -1
        parent = 'hair'
        y0 = hy
        for s, (ln, back, out, wd) in enumerate(segs):
            nm = 'hair_%d' % (k + 1) + ('', '_mid', '_tip')[s]
            bone(nm, (hx_, y0, hz), parent=parent, rot=(-back, 0, out * sgn))
            B(nm, (hx_ - wd / 2.0, y0 - ln, hz), (wd, ln, 0), 'lock')
            if s < 2:
                B(nm, (hx_, y0 - ln + 1, hz - 1), (0, ln - 1, 2), 'lock')
            ls = max(2, ln + sdl)
            B(nm, (hx_ + sdx - sw / 2.0, y0 - ls, hz + sdz), (sw, ls, 0), 'lock2')
            parent = nm
            y0 -= ln

    # ---------------- arms (authored hanging, posed reaching forward and out)
    AZ = 2.0  # arm depth offset (shoulder joint at z = 3.5)

    def arm(side, sx, rot_arm, rot_fore, rot_hand, curls):
        def X(x0, w):
            return x0 if sx > 0 else -(x0 + w)
        an, fn_, hn = side + '_arm', side + '_forearm', side + '_hand'
        bone(an, (11 * sx, -18, 1.5 + AZ), parent='body', rot=(rot_arm[0], -rot_arm[1] * sx, -rot_arm[2] * sx))
        B(an, (X(9.5, 3), -18, 0 + AZ), (3, 12, 3), 'upper')
        B(an, (X(9, 4), -7, -0.5 + AZ), (4, 3, 4), 'knob')
        bone(fn_, (11 * sx, -5.5, 1.5 + AZ), parent=an, rot=(rot_fore, 0, 0))
        B(fn_, (X(9.5, 3), -5.5, 0 + AZ), (3, 11, 3), 'fore')
        B(fn_, (X(9.5, 3), 5, -0.5 + AZ), (3, 2, 4), 'wrist')
        B(fn_, (X(11, 0), -4, 3 + AZ), (0, 11, 6), 'drape')
        bone(hn, (11 * sx, 7, 1.5 + AZ), parent=fn_, rot=(rot_hand, 0, 0))
        B(hn, (X(8.5, 5), 7, 0.5 + AZ), (5, 5, 2), 'palm')
        B(hn, (X(7.3, 1), 8, 1.0 + AZ), (1, 6, 1), 'finger')     # thumb, tucked along the inner edge
        B(hn, (X(7.3, 1), 14, 1.05 + AZ), (1, 3, 1), 'claw')
        # fingers medial -> lateral: x0, root y, splay, proximal, distal, claw  (1 wide, ~1-texel gaps)
        fingers = [(8.0, 11, -22, 8, 7, 3), (9.7, 12, -8, 9, 8, 4), (11.3, 12, 8, 9, 7, 4), (13.0, 11, 24, 8, 6, 3)]
        for k, (fx, fy, splay, lp, ld, lc) in enumerate(fingers):
            fnm = '%s_finger_%d' % (side, k + 1)
            tnm = fnm + '_tip'
            bone(fnm, ((fx + 0.5) * sx, fy, 1.5 + AZ), parent=hn, rot=(curls[k][0], 0, -splay * sx))
            B(fnm, (X(fx, 1), fy, 1.0 + AZ), (1, lp, 1), 'finger')
            B(fnm, (X(fx, 1), fy + 0.2, 0.4 + AZ), (1, 1, 1), 'knuckle', inflate=0.2)
            bone(tnm, ((fx + 0.5) * sx, fy + lp, 1.5 + AZ), parent=fnm, rot=(curls[k][1], 0, 0))
            B(tnm, (X(fx, 1), fy + lp, 1.0 + AZ), (1, ld, 1), 'finger')
            B(tnm, (X(fx, 1), fy + lp + ld, 1.05 + AZ), (1, lc, 1), 'claw')

    # (xRot forward<0, yRot, zRot outward>0), forearm bend, wrist droop, finger curls (proximal, distal)
    arm('right', -1, (-56, 10, 10), -26, 30, ((14, 22), (24, 34), (32, 42), (42, 54)))
    arm('left', 1, (-48, 6, 13), -32, 32, ((18, 26), (30, 38), (26, 34), (38, 50)))

    # ---------------- shroud: long tapering ribbons that continue the body's taper below the waist
    bone('shroud_front', (0, 1, 1.6), parent='body', rot=(-6, 0, 0))
    B('shroud_front', (-4.5, 1, 1.4), (3, 15, 0), 'ribbon')
    B('shroud_front', (-1.6, 1, 1.7), (2, 18, 0), 'ribbon')
    B('shroud_front', (0.4, 1, 1.5), (2, 14, 0), 'ribbon')
    B('shroud_front', (2.2, 1, 1.3), (3, 16, 0), 'ribbon')
    bone('shroud_back', (0, 0, 7.5), parent='body', rot=(14, 0, 0))
    B('shroud_back', (-4, 0, 7.6), (3, 15, 0), 'tatter')
    B('shroud_back', (-0.5, 0, 7.75), (2, 19, 0), 'tatter')
    B('shroud_back', (2.2, 0, 7.6), (3, 13, 0), 'tatter')
    bone('shroud_right', (-3.6, 0, 4.5), parent='body', rot=(0, -35, 10))
    B('shroud_right', (-3.6, 0, 2.5), (0, 14, 4), 'tatter')
    bone('shroud_left', (3.6, 0, 4.5), parent='body', rot=(0, 35, -10))
    B('shroud_left', (3.6, 0, 2.5), (0, 12, 4), 'tatter')

    # ---------------- tail: no legs, the soul trails off in a sideways S and frays into ribbons
    bone('tail1', (0, 2, 4.5), parent='body', rot=(8, 0, 0))
    B('tail1', (-4, 1.5, 1.5), (8, 7, 6), 'tail')
    bone('tail2', (0, 8, 4.5), parent='tail1', rot=(14, 0, -24))
    B('tail2', (-3, 7.5, 2.5), (6, 6, 4), 'tail')
    bone('tail3', (0, 13, 4.5), parent='tail2', rot=(14, 0, 42))
    B('tail3', (-2, 12.5, 3), (4, 6, 3), 'tail')
    bone('tail4', (0, 18, 4.5), parent='tail3', rot=(12, 0, 30))
    B('tail4', (-1, 17.5, 3.5), (2, 5, 2), 'tail')
    B('tail4', (-2, 19, 4.5), (2, 10, 0), 'ribbon')
    B('tail4', (0.4, 19, 4.4), (2, 8, 0), 'ribbon')
    B('tail4', (0, 19.5, 3), (0, 9, 3), 'ribbon')

    m = Model('anima', 256, 128, r.roots)
    m.scale = 0.5
    m.render_type = 'entityTranslucentEmissive'
    return m


FOCUS = 'head'

POSES = {
    # the signature: jaw dislocated to the chest, head thrown back, arms flung wide with the elbows bent UP,
    # wrists bent back and every finger splayed, cheeks torn wider
    'scream': {
        'body': (-0.14, 0, 0, 0, 0, 0),
        'neck': (-0.18, 0, 0, 0, 0, 0),
        'head': (-0.34, 0, -0.06, 0, 0, 0),
        'jaw': (-0.1, 0, 0, 0, 6.5, -1.0),
        'cheek_right': (0, 0, 0.12, 0, 1.0, 0),
        'cheek_left': (0, 0, -0.12, 0, 1.0, 0),
        'brow_right': (0, 0, -0.1, 0, -0.5, 0),
        'brow_left': (0, 0, 0.1, 0, -0.5, 0),
        'right_arm': (0.1, 0.2, 0.95, 0, 0, 0),
        'left_arm': (0.0, -0.2, -0.95, 0, 0, 0),
        'right_forearm': (0.3, 0, 0.45, 0, 0, 0),
        'left_forearm': (0.3, 0, -0.45, 0, 0, 0),
        'right_hand': (-0.7, 0, 0.3, 0, 0, 0),
        'left_hand': (-0.7, 0, -0.3, 0, 0, 0),
        'right_finger_1': (-0.3, 0, -0.25, 0, 0, 0), 'right_finger_4': (-0.4, 0, 0.3, 0, 0, 0),
        'left_finger_1': (-0.3, 0, 0.25, 0, 0, 0), 'left_finger_4': (-0.4, 0, -0.3, 0, 0, 0),
        'right_finger_2': (-0.35, 0, -0.1, 0, 0, 0), 'right_finger_3': (-0.4, 0, 0.1, 0, 0, 0),
        'left_finger_2': (-0.35, 0, 0.1, 0, 0, 0), 'left_finger_3': (-0.4, 0, -0.1, 0, 0, 0),
        'hair': (-0.2, 0, 0, 0, 0, 0),
        'tail1': (0.1, 0, 0, 0, 0, 0),
        'tail2': (0.15, 0, 0.1, 0, 0, 0),
        'tail3': (0.15, 0, -0.15, 0, 0, 0),
    },
    # lunge at the victim: body pitches in, jaw gapes WIDER than the scream (this jaw is the jumpscare
    # portrait's), both claws come up beside the face and curl
    'attack': {
        'body': (0.28, 0, 0, 0, -3.0, -3.0),
        'head': (0.06, 0, -0.08, 0, 0, 0),
        'jaw': (-0.14, 0, 0, 0, 7.5, -1.5),
        'cheek_right': (0, 0, 0.1, 0, 1.0, 0),
        'cheek_left': (0, 0, -0.1, 0, 1.0, 0),
        'right_arm': (-0.95, -0.25, 0.42, 0, 0, 0),
        'left_arm': (-1.05, 0.25, -0.42, 0, 0, 0),
        'right_forearm': (-0.2, 0, 0, 0, 0, 0),
        'left_forearm': (-0.15, 0, 0, 0, 0, 0),
        'right_hand': (-0.1, 0, 0, 0, 0, 0),
        'left_hand': (-0.1, 0, 0, 0, 0, 0),
        'right_finger_1': (0.3, 0, 0, 0, 0, 0), 'right_finger_2': (0.35, 0, 0, 0, 0, 0),
        'right_finger_3': (0.35, 0, 0, 0, 0, 0), 'right_finger_4': (0.3, 0, 0, 0, 0, 0),
        'left_finger_1': (0.3, 0, 0, 0, 0, 0), 'left_finger_2': (0.35, 0, 0, 0, 0, 0),
        'left_finger_3': (0.35, 0, 0, 0, 0, 0), 'left_finger_4': (0.3, 0, 0, 0, 0, 0),
        'tail1': (-0.1, 0, 0, 0, 0, 0),
        'tail2': (-0.15, 0, 0, 0, 0, 0),
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
        'right_finger_1': (-0.3, 0, -0.25, 0, 0, 0), 'right_finger_4': (-0.4, 0, 0.3, 0, 0, 0),
        'left_finger_1': (-0.3, 0, 0.25, 0, 0, 0), 'left_finger_4': (-0.4, 0, -0.3, 0, 0, 0),
        'right_finger_2': (-0.35, 0, -0.1, 0, 0, 0), 'right_finger_3': (-0.4, 0, 0.1, 0, 0, 0),
        'left_finger_2': (-0.35, 0, 0.1, 0, 0, 0), 'left_finger_3': (-0.4, 0, -0.1, 0, 0, 0),
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
TODO
"""
