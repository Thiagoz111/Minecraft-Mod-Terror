"""El Hombre Sombra -- the Hat Man (DEAD LINE).

Authored at 2x texel density (model.scale = 0.5) with rig.Rig: +Y down, ground at y = 24, the creature faces -Z,
right_* parts on -X. Cubes are authored relative to their bone pivot (bone-local, unrotated); the pivots of the
hunched upper body (neck, head, arms, collar) are placed from WORLD targets through `wbone`, which inverts the
parent transforms, so the folded rest pose stays centred on the entity origin and inside the 0.8 x 3.4 hitbox.

Design: a pure black silhouette. A wide snap-brim fedora (flat oval brim on the hat bone, a front brim that
snaps down along one straight hinge and a back brim that curls up), a low pinched crown with a violet-black band.
A deep belted trench coat whose eight panels flare out to the shins and dissolve into smoke. A C-curved hunch:
the chest leans 19 deg, three progressively rotated spine slabs roll the upper back out behind him, the neck
juts forward out of the hump and brings the face back to vertical. Impossibly long, thin, broken-looking arms
(5x5 sleeve, 4x4 forearm, bare 3x3 wrist) with an elbow that bends the wrong way, ending in spider hands.
Only deliberate dark blue / violet rim tones describe the volumes. Under the brim: two tiny ember eyes and a
too-wide grin -- a black crescent from cheek to cheek whose upper lip IS the jaw hinge, so when the jaw drops
the painted grin becomes the real maw (needle teeth hang from the upper lip, the corner cuts stay as torn slits).
"""
import math

import numpy as np

from mcmodel import Model, fbm, hash3, face_light, pick, rot_matrix
from rig import Rig
from paint import hx, mix, edge


def pal(*h):
    return [hx(c) for c in h]


# ------------------------------------------------------------------ palettes (dark -> light)
SHADE = pal('#010102', '#040409', '#08080f', '#0d0c17', '#131121', '#1a172c', '#221e3a', '#2c264a', '#3a325e')
FELT = pal('#010102', '#050508', '#0a0910', '#100e19', '#171423', '#1f1b2f', '#28223c', '#332b4c', '#41376a')
BAND = pal('#07060b', '#0c0a14', '#100e1a', '#141120', '#181527', '#1d1830')
SMOKE = pal('#07060b', '#0d0b14', '#14121d', '#1c1928', '#252134', '#2f2a41', '#3a344f')
TOOTH = pal('#15121c', '#221e2b', '#322d3d', '#443e52', '#585168', '#6e677f', '#8a8399', '#a7a0b4')
MAW = pal('#020001', '#090102', '#120204', '#1c0306', '#280509', '#36070d', '#470b12', '#5c1018')
GLOW = pal('#2a0204', '#4e0407', '#7e070a', '#b30d0e', '#e8231a', '#ff5a2a', '#ffb070', '#ffe8c0')
VOID = hx('#000000')


def fine(ramp, n):
    """Resample a palette to n tones so very dark gradients (folds, sheen) still change colour."""
    out = []
    for k in range(n):
        f = k / (n - 1) * (len(ramp) - 1)
        i = min(len(ramp) - 2, int(f))
        out.append(mix(ramp[i], ramp[i + 1], f - i))
    return out


CLOTH = fine(SHADE, 17)


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


def dpos(ctx):
    """Texel centre in authored coordinates (bone pivot + local; stable noise space)."""
    lx, ly, lz = local(ctx)
    a = ctx.bone.abs
    return a[0] + lx, a[1] + ly, a[2] + lz


def is_side(ctx):
    return ctx.face not in ('top', 'bottom')


def flat(ctx):
    return 0 in ctx.cube.size


def clamp(v, a=0.0, b=1.0):
    return a if v < a else b if v > b else v


def form(ctx, base, rim=0.07, light=1.0):
    """Value of a texel on a dark solid: baked light + violet rims on the silhouette edges."""
    v = base + face_light(ctx) * light
    if flat(ctx):
        return v
    if is_side(ctx):
        if ctx.j == 0:
            v += rim  # upper edge catches the moon
        elif ctx.j == ctx.h - 1:
            v -= 0.03
        if ctx.i == 0 or ctx.i == ctx.w - 1:
            v += rim * 0.6  # vertical silhouette rim
    elif ctx.face == 'top' and edge(ctx) == 0:
        v += rim * 0.8
    return v


def rgba(c, a):
    a = int(clamp(a) * 255)
    if a < 16:
        return None
    return (c[0], c[1], c[2], a)


# ------------------------------------------------------------------ smoke
def smoke_noise(x, y, z, seed):
    """Domain-warped noise that drifts diagonally and curls: broad blobs, not strips."""
    w = fbm(x * 0.06 + 3.1, y * 0.05, z * 0.06, 2, seed + 7)
    return fbm(x * 0.09 + y * 0.035 + w * 2.4, y * 0.065 - x * 0.02 + w * 1.2, z * 0.09 + w * 1.6, 3, seed)


def dissolve(ctx, t, start, seed):
    """Soft smoke dissolve toward the bottom of a hanging part: (alpha, k) or None."""
    if t < start - 0.15:
        return 1.0, 0.0
    x, y, z = dpos(ctx)
    k = (t - start) / max(0.05, 1.0 - start)
    n = smoke_noise(x, y, z, seed)
    s = k + (0.52 - n) * 1.1
    a = clamp(1.0 - s * 1.45)
    if a < 0.07:
        return None
    return a, clamp(k)


def smoky(c, v, a, k, ctx, lift=0.1, gain=1.5):
    """Blend a cloth colour into translucent smoke as it dissolves."""
    if k <= 0 and a >= 0.999:
        return c
    x, y, z = dpos(ctx)
    n = smoke_noise(x * 1.7, y * 1.7, z * 1.7, 5)
    s = pick(SMOKE, v + lift + k * 0.18 + (n - 0.5) * 0.35)
    c = mix(c, s, clamp(k * gain + 0.15))
    return rgba(c, a)


def smoke_plane(seed, dens=0.85, drift=1.0, top_fade=0.16):
    """Translucent smoke on a zero-thickness plane: broad soft blobs and curling wisps drifting sideways."""
    def f(ctx):
        lx, ly, lz = local(ctx)
        c = ctx.cube
        if c.size[1] == 0:
            return None
        uw = c.size[0] if c.size[0] > 0 else c.size[2]
        u = (lx - c.origin[0]) if c.size[0] > 0 else (lz - c.origin[2])
        t = (ly - c.origin[1]) / c.size[1]
        yy = ly - c.origin[1]
        uu = u + drift * (5.0 * t * t + 1.6 * math.sin(t * 5.0 + seed))
        n = smoke_noise(uu * 1.1 + seed * 3.7, yy * 1.1, seed * 1.3, seed)
        mask = clamp(t / top_fade) * (1.0 - t) ** 1.15
        side = min(u, uw - u) / max(1.0, uw * 0.18)
        mask *= clamp(side + 0.25)
        a = clamp((n - 0.36) * 2.6) * mask * dens
        if a < 0.06:
            return None
        v = 0.36 + (n - 0.5) * 0.5 - t * 0.12 + face_light(ctx) * 0.3
        return rgba(pick(SMOKE, v), a)
    return f


def pool_mat(ctx):
    """Ground smoke pooling under the coat (horizontal plane)."""
    x, y, z = dpos(ctx)
    r = math.sqrt((x / 14.0) ** 2 + ((z - 1) / 11.0) ** 2)
    if r >= 1.0:
        return None
    n = smoke_noise(x * 1.4, z * 0.7, z * 1.4, 71)
    a = clamp((n - 0.3) * 2.2) * (1 - r) ** 0.8 * 0.75
    if a < 0.06:
        return None
    return rgba(pick(SMOKE, 0.35 + (n - 0.5) * 0.6), a)


# ------------------------------------------------------------------ cloth materials
def fold_value(ctx, v):
    """Gabardine drape: two or three broad folds per panel (dark crease + lit ridge) that deepen toward the hem."""
    fl = getattr(ctx.bone, 'flen', None)
    if not fl or not is_side(ctx) or flat(ctx):
        return v
    lx, ly, lz = local(ctx)
    t = ly / fl
    col = lx if ctx.face in ('front', 'back') else lz
    ph = getattr(ctx.bone, 'fseed', 0) * 1.37
    f = fbm(col * 0.16 + ph, t * 1.2 + ph * 0.3, ph, 2, 13)
    depth = 0.3 + 0.7 * clamp(t * 1.6)
    if f < 0.38:
        v -= 0.10 * depth
    elif f < 0.44:
        v -= 0.05 * depth
    elif f > 0.62:
        v += 0.10 * depth
    elif f > 0.56:
        v += 0.05 * depth
    v += 0.06 * (1.0 - t)  # soft sheen near the waist
    if ctx.face in ('west', 'east') and ctx.w <= 2:
        v += 0.06  # pressed edge of the panel
    if ctx.face in ('front', 'back') and ctx.w >= 6 and t < 0.62:
        if ctx.i in (1, ctx.w - 2) and ctx.j % 3 != 2:
            v -= 0.07  # top-stitching one texel in from the panel edge
    return v


def coat_mat(ctx):
    """Heavy black gabardine: violet rims, drape folds, dissolving into smoke toward the shins."""
    v = fold_value(ctx, form(ctx, 0.30))
    c = pick(CLOTH, v)
    fl = getattr(ctx.bone, 'flen', None)
    start = getattr(ctx.bone, 'smoke', None)
    if fl and start is not None and ctx.face != 'top':
        lx, ly, lz = local(ctx)
        r = dissolve(ctx, ly / fl, start, getattr(ctx.bone, 'fseed', 0) + 11)
        if r is None:
            return None
        return smoky(c, v, *r, ctx)
    return c


def hump_mat(ctx):
    """Rounded upper back: the moon grazes the crest of each spine slab, the flanks fall into black."""
    lx, ly, lz = local(ctx)
    c = ctx.cube
    v = 0.27 + face_light(ctx) * 0.7
    if ctx.face == 'back':
        # crest of the curve: lighter along the spine, darker toward the flanks
        v += 0.06 * (1.0 - clamp(abs(lx) / (c.size[0] * 0.5)))
        if abs(lx) < 0.5:
            v -= 0.05  # spine seam
        v += 0.05 * (1.0 - ctx.t)
    elif ctx.face == 'top':
        v += 0.04 if edge(ctx) == 0 else -0.03
    elif ctx.face in ('west', 'east'):
        v -= 0.04
    return pick(CLOTH, v)


def tatter_mat(seed):
    """Torn zero-thickness strips at the panel edges: ragged ribbons of cloth turning to smoke."""
    def f(ctx):
        lx, ly, lz = local(ctx)
        c = ctx.cube
        u = (lx - c.origin[0]) if c.size[0] > 0 else (lz - c.origin[2])
        t = (ly - c.origin[1]) / max(1, c.size[1])
        k = math.floor(u / 1.5)
        L = 0.45 + 0.55 * hash3(k, 0, 0, seed)
        wob = 0.5 * math.sin(t * 7 + k)
        if t > L or abs((u + wob) - (k + 0.5) * 1.5) > 0.75 - 0.35 * t:
            return None
        v = 0.30 + 0.06 * (1 - t) + face_light(ctx) * 0.6 + (0.06 if hash3(k, 1, 0, seed) > 0.6 else 0)
        col = mix(pick(SHADE, v), pick(SMOKE, v + 0.05), clamp(t / L * 1.2))
        return rgba(col, 1.0 - (t / L) ** 1.6)
    return f


def lining_mat(ctx):
    """Inside of the coat: a void, barely any light gets in; it fades into dark smoke."""
    lx, ly, lz = local(ctx)
    v = 0.10 + face_light(ctx) * 0.3
    c = pick(SHADE, v)
    t = (ly - ctx.cube.origin[1]) / ctx.cube.size[1]
    if ctx.face != 'top':
        r = dissolve(ctx, t, 0.45, 41)
        if r is None:
            return None
        return smoky(c, v - 0.25, *r, ctx, lift=0.0, gain=0.6)
    return c


def trouser_mat(ctx):
    """Legs hidden in the coat: near-black, dissolving into the darkest smoke so they never read as pale columns."""
    v = form(ctx, 0.16)
    c = pick(SHADE, v)
    if ctx.face == 'top':
        return c
    lx, ly, lz = local(ctx)
    r = dissolve(ctx, ly / 40.0, 0.38, 61)
    if r is None:
        return None
    a, k = r
    x, y, z = dpos(ctx)
    n = smoke_noise(x * 1.7, y * 1.7, z * 1.7, 5)
    s = pick(SMOKE[:3], 0.3 + (n - 0.5) * 0.6)
    return rgba(mix(c, s, clamp(k * 0.7)), a * (1.0 - 0.35 * k))


def belt_mat(ctx):
    v = form(ctx, 0.33, rim=0.09)
    if is_side(ctx) and ctx.h >= 3 and ctx.j in (0, ctx.h - 1) and ctx.i % 2 == 0:
        v += 0.05  # stitched edges
    return pick(SHADE, v)


def buckle_mat(ctx):
    """Dull, nearly invisible buckle: only red may glow on this figure."""
    if ctx.face == 'front' and 0 < ctx.i < ctx.w - 1 and 0 < ctx.j < ctx.h - 1:
        return SHADE[1]
    return pick(SHADE, form(ctx, 0.40, rim=0.05))


def button_mat(ctx):
    if ctx.face == 'front':
        return SHADE[4] if (ctx.i, ctx.j) == (0, 0) else SHADE[3]
    return SHADE[2]


def lapel_mat(ctx):
    """Lapels / collar / flaps / cuffs: crisp pressed edges, stitched border, lit upper side."""
    v = form(ctx, 0.35, rim=0.1)
    if is_side(ctx) and not flat(ctx) and ctx.w >= 4 and ctx.h >= 4:
        if ctx.j in (1, ctx.h - 2) and 0 < ctx.i < ctx.w - 1 and ctx.i % 3 != 2:
            v -= 0.07  # dashed top-stitch one texel in from the upper and lower edges
    return pick(CLOTH, v)


def chest_mat(ctx):
    """Torso of the coat; the V between the lapels is a pure void (nothing inside the coat)."""
    v = form(ctx, 0.31)
    lx, ly, lz = local(ctx)
    if ctx.face == 'front' and ctx.bone.name == 'chest' and ctx.cube.size[1] > 10:
        if ly < -6 and abs(lx) < 1.0 + (-6 - ly) * 0.42:
            return SHADE[0]  # open V of the coat: a void
        if abs(abs(lx) - 6.5) < 0.5 and ly > -7:
            v -= 0.07  # double-breasted seams
        f = fbm(lx * 0.2, ly * 0.12, 3.0, 2, 17)
        if f < 0.4:
            v -= 0.06
        elif f > 0.62:
            v += 0.05
    if ctx.face == 'back' and abs(lx) < 0.5:
        v -= 0.08  # centre back seam
    if ctx.face in ('west', 'east') and abs(lz) < 0.5:
        v -= 0.06  # side seam
    if ctx.bone.name == 'chest':
        v += 0.06 * clamp((-ly - 4) / 12.0)  # sheen gathers on the chest
    return pick(CLOTH, v)


def sleeve_mat(ctx):
    """Thin sleeves: a single sheen stripe down the front, twisting creases under the broken elbow."""
    v = form(ctx, 0.29)
    lx, ly, lz = local(ctx)
    if is_side(ctx) and not flat(ctx):
        col = lx if ctx.face in ('front', 'back') else lz
        if getattr(ctx.bone, 'elbow', False) and ly < 6:
            ph = (col * 0.9 + ly * 0.8) % 4.0
            if ph < 0.9:
                v -= 0.08
            elif ph < 1.8:
                v += 0.06
        if abs(col) < 0.6 and ctx.face == 'back':
            v -= 0.05  # sleeve seam
        v += 0.05 * (1 - ctx.t)
    return pick(CLOTH, v)


# ------------------------------------------------------------------ hat
BRIM_RECTS = []   # hat-local footprints (x0, x1, z0, z1) of every brim slab, filled by build()


def _in_brim(x, z):
    for x0, x1, z0, z1 in BRIM_RECTS:
        if x0 <= x <= x1 and z0 <= z <= z1:
            return True
    return False


def brim_outer(ctx):
    """True when this texel of a brim slab's top/bottom face lies on the outer perimeter of the whole brim."""
    lx, ly, lz = local(ctx)
    o = ctx.bone.hat_off
    x, z = lx + o[0], lz + o[2]
    for dx, dz in ((1.0, 0), (-1.0, 0), (0, 1.0), (0, -1.0)):
        if not _in_brim(x + dx, z + dz):
            return True
    return False


def felt_mat(ctx):
    """Brim felt: violet sheen on top, a lit outer edge, and a violet ring on the underside perimeter only."""
    lx, ly, lz = local(ctx)
    o = ctx.bone.hat_off
    x, z = lx + o[0], lz + o[2]
    if ctx.face == 'bottom':
        if brim_outer(ctx):
            return FELT[5] if abs(z) > abs(x) * 0.55 else FELT[4]
        return FELT[0]
    if ctx.face == 'top':
        r = math.sqrt((x / 27.0) ** 2 + (z / 21.0) ** 2)
        v = 0.36 + 0.10 * math.exp(-((r - 0.62) / 0.22) ** 2)
        v += 0.03 * math.sin(x * 0.35 + z * 0.22)
        if brim_outer(ctx):
            v += 0.12
        return pick(FELT, v)
    # brim edge (2 texels tall): the violet rim that outlines the oval
    v = 0.66 + face_light(ctx) * 0.6
    if ctx.j == ctx.h - 1:
        v -= 0.10
    return pick(FELT, v)


def crown_mat(ctx):
    v = form(ctx, 0.34, rim=0.1)
    if ctx.face == 'bottom':
        return FELT[0]
    lx, ly, lz = local(ctx)
    if is_side(ctx) and not flat(ctx):
        v -= ctx.t * 0.08  # darker toward the band
        if ctx.face == 'front' and getattr(ctx.cube, 'pinch', False):
            # front pinch: one soft value step either side of the centre
            if 2.0 < abs(lx) < 4.5:
                v -= 0.06
    if ctx.face == 'top':
        # teardrop crease along the centre: one shaded channel, narrowing toward the back
        wid = 2.2 - (lz + 9) * 0.06
        if abs(lx) < wid:
            v -= 0.10
    return pick(FELT, v)


def band_mat(ctx):
    """Violet-black band: barely separates from the felt, one lit pixel row on top."""
    if ctx.face == 'bottom':
        return BAND[0]
    if ctx.face == 'top':
        return BAND[2]
    v = 0.30 + face_light(ctx) * 0.6
    if ctx.j == 0:
        v = 0.95
    elif ctx.j == ctx.h - 1:
        v -= 0.12
    return pick(BAND, v)


# ------------------------------------------------------------------ head: one shared face grid
# Cranium front: 18 wide (cols 0..17, x -9..9), rows 0..13. Row 14 is the first jaw row: the jaw hinge is the
# upper-lip line of the grin, so the painted mouth and the real maw are the same opening.
FACE_W, CRAN_H = 18, 14
JAW_W, JAW_H = 16, 8
SEAM = CRAN_H
EYES = ((4, 6), (12, 6))      # top-left texel of each 2x2 hot core (viewer's left eye first)
# crescent per column of the left half (mirrored): upper-lip row U, lower-lip row D (black = U..D-1)
_U = (7, 8, 9, 10, 12, 13, 14, 14, 14)
_D = (8, 10, 12, 14, 16, 17, 18, 18, 19)
# needle teeth hanging from the upper lip (on a head-bound plane): (root cols, tip col, length)
TEETH = (((5, 6), 6, 3), ((8, 9), 9, 4), ((11, 12), 11, 3))
TEETH_X0 = 5                   # first face column covered by the teeth plane


def lips(c):
    h = c if c < 9 else 17 - c
    return _U[h], _D[h], h


def grin_cells():
    """{(col, row): colour}: black crescent, lit lower lip, faint upper lip, shadow under the lip."""
    cells = {}
    for c in range(FACE_W):
        U, D, h = lips(c)
        cells[(c, U - 1)] = SHADE[4] if h >= 3 else SHADE[3]
        for r in range(U, D):
            cells[(c, r)] = VOID
        cells[(c, D)] = SHADE[6] if h >= 3 else SHADE[5]
        if (c, D + 1) not in cells:
            cells[(c, D + 1)] = SHADE[1]
    return cells


GRIN = grin_cells()


def teeth_cells():
    """{(col, row-from-the-hinge): colour} for the upper needles; gum pixels in the gaps."""
    cells = {}
    for c in range(TEETH_X0, FACE_W - TEETH_X0):
        cells[(c, 0)] = MAW[3]
    for (a, b), tip, L in TEETH:
        root = 2 if L >= 4 else 1
        for r in range(L):
            if r < root:
                cells[(a, r)] = TOOTH[2] if r == 0 else TOOTH[3]
                cells[(b, r)] = TOOTH[3] if r == 0 else TOOTH[4]
            else:
                cells[(tip, r)] = TOOTH[4] if r < L - 1 else TOOTH[5]
    return cells


TEETH_CELLS = teeth_cells()


def eye_cells(glow=False):
    """2x2 hot core + a 1-texel halo (no corners) per eye."""
    cells = {}
    for (ex, ey) in EYES:
        core = (GLOW[7], GLOW[6], GLOW[6], GLOW[5]) if glow else (GLOW[6], GLOW[5], GLOW[5], GLOW[4])
        for k, (di, dj) in enumerate(((0, 0), (1, 0), (0, 1), (1, 1))):
            cells[(ex + di, ey + dj)] = core[k]
        for di, dj in ((-1, 0), (-1, 1), (2, 0), (2, 1), (0, -1), (1, -1), (0, 2), (1, 2)):
            cells[(ex + di, ey + dj)] = GLOW[2] if glow else GLOW[1]
    return cells


def face_skin(i, j):
    """Base value of the face skin at grid (col, row): black under the brim, a cold violet sheen on the lower face."""
    v = 0.03 + 0.36 * clamp((j - 3.5) / 9.0)
    if i in (0, FACE_W - 1):
        v -= 0.06
    return v


def face_front_decal(img, u0, v0, w, h):
    """Cranium front: under-brim shadow, deep slanted sockets with ember spill, the rising corner cuts."""
    px = img.load()
    for j in range(h):
        for i in range(w):
            x, y = i + 0.5, j + 0.5
            c = pick(SHADE, face_skin(i, j))
            for (ex, ey), sgn in ((EYES[0], 1), (EYES[1], -1)):
                dx, dy = x - (ex + 1.0), y - (ey + 1.0)
                a = math.radians(-14 * sgn)  # sockets slant down toward the nose: a scowl
                uu = dx * math.cos(a) + dy * math.sin(a)
                vv = -dx * math.sin(a) + dy * math.cos(a)
                r = (uu / 2.7) ** 2 + (vv / 1.8) ** 2
                if r <= 1.0:
                    c = VOID
                elif r <= 1.7:
                    c = mix(SHADE[1], MAW[3], (1.7 - r) / 0.7 * 0.7)  # ember light spilling on the skin
            px[u0 + i, v0 + j] = c
    for (i, j), c in GRIN.items():
        if 0 <= i < w and 0 <= j < h:
            px[u0 + i, v0 + j] = c
    for (i, j), c in eye_cells().items():
        if 0 <= i < w and 0 <= j < h:
            px[u0 + i, v0 + j] = c


def eyes_glow_decal(img, u0, v0, w, h):
    """Emissive pass for the cranium front: the two eyes, nothing else."""
    px = img.load()
    for (i, j), c in eye_cells(glow=True).items():
        if 0 <= i < w and 0 <= j < h:
            px[u0 + i, v0 + j] = c


def jaw_front_decal(img, u0, v0, w, h):
    """Jaw front (16 wide = face cols 1..16, rows 14..21): the body of the grin, lit lower lip, long chin."""
    px = img.load()
    off = (FACE_W - w) // 2
    for j in range(h):
        for i in range(w):
            c = GRIN.get((i + off, j + SEAM))
            if c is None:
                v = face_skin(i + off, j + SEAM) - 0.04 * clamp((j - 5) / 2.0)
                if i in (0, w - 1):
                    v -= 0.06
                c = pick(SHADE, v)
            px[u0 + i, v0 + j] = c


def grin_side_decal(front_high):
    """The cut keeps going from the grin corner around the side of the skull toward the ear, lit lip below it."""
    def fn(img, u0, v0, w, h):
        px = img.load()
        U0, D0, _ = lips(0)
        for k in range(0, 7):
            i = (w - 1 - k) if front_high else k
            jj = int(round(U0 - k * 0.45))
            if 0 <= jj < h:
                px[u0 + i, v0 + jj] = VOID if k < 5 else SHADE[1]
                if jj + 1 < h and k < 5:
                    px[u0 + i, v0 + jj + 1] = SHADE[5] if k < 3 else SHADE[4]
    return fn


def skin_mat(ctx):
    """Head / neck: void skin, violet sheen only on the planes that catch the moon."""
    v = form(ctx, 0.20, rim=0.08)
    if getattr(ctx.cube, 'cranium', False):
        if ctx.face == 'bottom':
            return palate_mat(ctx)
        if ctx.face in ('west', 'east'):
            v -= 0.10 * clamp(1.0 - (ctx.t - 0.25) * 3)  # shadow under the hat
    return pick(SHADE, v)


def brow_mat(ctx):
    """Brow shelf: black mass, a thin violet line where the moon grazes its upper edge."""
    if ctx.face == 'bottom':
        return VOID
    v = 0.14 + face_light(ctx) * 0.5
    if is_side(ctx) and ctx.j == 0:
        v += 0.18
    return pick(SHADE, v)


def palate_mat(ctx):
    """Roof of the mouth: black at the lip, deepening to dark red toward the throat."""
    lx, ly, lz = local(ctx)
    zf = ctx.cube.origin[2]
    k = clamp((lz - zf - 1.0) / 13.0)
    if lz - zf < 1.0:
        return VOID
    v = 0.05 + 0.30 * k ** 1.4 - 0.2 * clamp((abs(lx) - 5.0) / 3.0)
    if abs(lx) < 0.6:
        v -= 0.08  # palate ridge
    return pick(MAW, v)


def throat_mat(ctx):
    """The gullet behind the jaw: only its top rows show through the open maw (dark red, darkest at the rim)."""
    lx, ly, lz = local(ctx)
    c = ctx.cube
    if ctx.face == 'front':
        dy = ly - c.origin[1]
        if dy < 5:
            r = math.sqrt((lx / 5.0) ** 2 + ((dy - 1.8) / 2.4) ** 2)
            return pick(MAW, 0.34 - r * 0.32)
    return pick(SHADE, form(ctx, 0.14))


def jaw_mat(ctx):
    v = form(ctx, 0.20, rim=0.08)
    lx, ly, lz = local(ctx)
    if ctx.face == 'top' and getattr(ctx.cube, 'tongue', False):
        # tongue bed: black at the lip, dark red deepening toward the throat, soft central groove
        zf = ctx.cube.origin[2]
        if lz - zf < 1.0:
            return VOID
        k = clamp((lz - zf - 1.0) / 11.0)
        vv = 0.03 + 0.24 * k ** 1.6 - 0.2 * clamp((abs(lx) - 4.5) / 3.0)
        if abs(lx) < 0.6:
            vv -= 0.12
        return pick(MAW, vv)
    if ctx.face == 'front' and ctx.cube.size[1] <= 3:
        v += 0.04  # chin catches the under-light
    return pick(SHADE, v)


def tooth_cube_mat(ctx):
    """Corner fangs: long bone-violet needles, lighter toward the tip."""
    c = ctx.cube
    lx, ly, lz = local(ctx)
    grow = getattr(c, 'grow', 1)
    t = (ly - c.origin[1]) / c.size[1]
    t = t if grow > 0 else 1 - t
    v = 0.40 + t * 0.42 + face_light(ctx) * 0.6
    if ctx.face in ('west', 'east'):
        v -= 0.08
    return pick(TOOTH, v)


def front_teeth_mat(ctx):
    """The upper needles of the grin (head-bound plane in front of the jaw): pixel art from TEETH_CELLS."""
    lx, ly, lz = local(ctx)
    c = ctx.cube
    col = int(math.floor(lx - c.origin[0])) + TEETH_X0
    row = int(math.floor(ly - c.origin[1]))
    return TEETH_CELLS.get((col, row))


def needle_teeth(seed, grow=1, axis='x', pitch=3):
    """A row of needle teeth on a zero-thickness plane (gum band, 2-px roots, 1-px tips, gaps between)."""
    def f(ctx):
        lx, ly, lz = local(ctx)
        c = ctx.cube
        u = (lx - c.origin[0]) if axis == 'x' else (lz - c.origin[2])
        uw = c.size[0] if axis == 'x' else c.size[2]
        depth = (ly - c.origin[1]) if grow > 0 else (c.origin[1] + c.size[1] - ly)
        row = int(math.floor(depth))
        col = int(math.floor(u))
        if row == 0:
            return MAW[3] if 0 < col < uw - 1 else MAW[1]  # gum line
        k, m = divmod(col, pitch)
        if m >= 2:
            return None
        L = 3 + int(hash3(k, 0, 0, seed) * 2.99)  # 3..5 texels
        if row > L:
            return None
        if row > (L + 1) // 2:
            tipcol = 0 if hash3(k, 1, 0, seed) < 0.5 else 1
            if m != tipcol:
                return None
        tt = row / L
        v = 0.30 + tt * 0.5 + face_light(ctx) * 0.4
        if m == 1 and row <= (L + 1) // 2:
            v -= 0.1
        return pick(TOOTH, v)
    return f


def strands_mat(seed, grow=1, spacing=1.8):
    """Torn cheek strands stretched across the mouth corners (zero-thickness plane, translucent)."""
    def f(ctx):
        lx, ly, lz = local(ctx)
        c = ctx.cube
        horiz = c.size[0] > 0
        u = (lx - c.origin[0]) if horiz else (lz - c.origin[2])
        t = (ly - c.origin[1]) / max(1, c.size[1])
        t = t if grow > 0 else 1 - t
        best = None
        for k in range(-1, 2):
            si = math.floor(u / spacing) + k
            ph = hash3(si, 0, 0, seed) * 6.28
            cx = (si + 0.5) * spacing + 0.9 * math.sin(t * 3.4 + ph)
            L = 0.55 + 0.45 * hash3(si, 1, 0, seed)
            wid = 0.75 - 0.35 * math.sin(t * math.pi) * hash3(si, 2, 0, seed)
            if t < L and abs(u - cx) < wid:
                a = 1.0 - (t / L) ** 3 * 0.6
                if best is None or a > best:
                    best = a
        if best is None:
            return None
        v = 0.62 - t * 0.25 + face_light(ctx) * 0.3
        return rgba(pick(MAW, v), best * 0.96)
    return f


def cheek_skin_mat(seed):
    """Stretched cheek skin on the side of the maw (YZ plane): torn vertical slits with raw edges."""
    def f(ctx):
        lx, ly, lz = local(ctx)
        c = ctx.cube
        u = lz - c.origin[2]
        t = (ly - c.origin[1]) / max(1, c.size[1])
        k = math.floor(u / 2.5)
        cx = (k + 0.5) * 2.5 + 0.6 * math.sin(t * 4 + k)
        tear = hash3(k, 0, 0, seed) > 0.35 and 0.2 < t < 0.85 + 0.1 * hash3(k, 1, 0, seed)
        d = abs(u - cx)
        if tear and d < 0.55 * math.sin(clamp((t - 0.2) / 0.7) * math.pi) + 0.1:
            return None
        if tear and d < 1.1:
            return MAW[1]
        v = 0.18 + face_light(ctx) * 0.6 + (0.05 if (u + t * 3) % 3 < 0.6 else 0)
        return pick(SHADE, v)
    return f


def throat_glow_decal(img, u0, v0, w, h):
    """Emissive: one small ember deep in the gullet (2x2 core, GLOW 0-1 falloff)."""
    px = img.load()
    cx = w // 2 - 1
    for (i, j), c in {(cx, 1): GLOW[1], (cx + 1, 1): GLOW[1], (cx, 2): GLOW[1], (cx + 1, 2): GLOW[0],
                      (cx - 1, 1): GLOW[0], (cx + 2, 2): GLOW[0], (cx, 3): GLOW[0], (cx + 1, 0): GLOW[0]}.items():
        if 0 <= i < w and 0 <= j < h:
            px[u0 + i, v0 + j] = c


# ------------------------------------------------------------------ hands
def hand_mat(ctx):
    """Long void fingers: violet knuckle highlights, a bony wrist."""
    v = form(ctx, 0.26, rim=0.1)
    n = ctx.bone.name
    if is_side(ctx) and not flat(ctx):
        if ('finger' in n or 'thumb' in n) and ctx.j <= 1:
            v += 0.09  # knuckle
        if n.endswith('_hand') and ctx.face == 'front' and ctx.cube.size[1] >= 5 and ctx.i % 2 == 1:
            v += 0.06  # tendons on the back of the hand
        if n.endswith('_hand') and ctx.cube.size[0] == 3 and ctx.j == ctx.h - 1:
            v += 0.08  # wrist bone knob
    return pick(SHADE, v)


def nail_mat(ctx):
    """Claws: dark glossy grey-violet, a pale glint at the tip only."""
    v = 0.25 + face_light(ctx) * 1.0
    if is_side(ctx):
        v += ctx.t * 0.35
    return pick(TOOTH, v)


# ------------------------------------------------------------------ build helpers
def wmat(b):
    """World matrix of a Bone at rest (walks the parent chain)."""
    chain = []
    while b is not None:
        chain.append(b)
        b = b.parent
    M = np.eye(4)
    for bb in reversed(chain):
        T = np.eye(4)
        T[:3, 3] = bb.pivot
        R = np.eye(4)
        R[:3, :3] = rot_matrix(*[math.radians(a) for a in bb.rot])
        M = M @ T @ R
    return M


def build():
    r = Rig()
    BRIM_RECTS.clear()

    def bone(name, pivot, parent=None, rot=(0, 0, 0), mat=None, **attrs):
        b = r.bone(name, pivot, parent, rot, mat)
        b.abs = r.abs_pivot[name]
        for k, v in attrs.items():
            setattr(b, k, v)
        return b

    def at(parent, dx, dy, dz):
        """Pivot given in the parent's local (unrotated) frame."""
        a = r.abs_pivot[parent]
        return (a[0] + dx, a[1] + dy, a[2] + dz)

    def wbone(name, world, parent, rot=(0, 0, 0), mat=None, **attrs):
        """Bone whose pivot lands on a WORLD position at rest (parent transforms inverted)."""
        Mp = wmat(r.bones[parent])
        loc = np.linalg.inv(Mp) @ np.array([world[0], world[1], world[2], 1.0])
        return bone(name, at(parent, loc[0], loc[1], loc[2]), parent, rot, mat, **attrs)

    def box(b, frm, size, mat=None, inflate=0.0, decals=None, **attrs):
        """frm relative to the bone pivot."""
        a = r.abs_pivot[b]
        c = r.box(b, (a[0] + frm[0], a[1] + frm[1], a[2] + frm[2]), size, mat=mat, inflate=inflate, decals=decals)
        for k, v in attrs.items():
            setattr(c, k, v)
        return c

    def mx(sx, frm, size):
        """Mirror a right-side (-X) box description to side sx (+1 = left)."""
        return frm if sx < 0 else (-(frm[0] + size[0]), frm[1], frm[2])

    def mbox(b, sx, frm, size, **kw):
        return box(b, mx(sx, frm, size), size, **kw)

    HIP = -16.0

    # ---------------- ground smoke pooling under him
    bone('smoke_pool', (0, 24, 1))
    box('smoke_pool', (-14, -0.4, -10), (28, 0, 22), mat=pool_mat)

    # ---------------- legs (hidden inside the coat; they dissolve into dark smoke before the ground)
    for side, sx in (('right', -1), ('left', 1)):
        leg = bone(f'{side}_leg', (4.5 * sx, HIP, 1.5), rot=(0, 0, -2 * sx), mat=trouser_mat)
        box(leg.name, (-3.5, 0, -3.5), (7, 22, 7))
        box(leg.name, (-3, 21, -3), (6, 19, 6))

    # ---------------- body: deep waist, belt + dull buckle, coat lining (inner skirt)
    bone('body', (0, HIP, 1.5), mat=coat_mat)
    box('body', (-9.5, -14, -8.5), (19, 14, 17), mat=chest_mat)
    box('body', (-10.5, -2, -9.5), (21, 3, 19), mat=belt_mat)
    box('body', (-2, -2.5, -10.1), (4, 4, 1), mat=buckle_mat)
    box('body', (-7.5, 0.4, -6), (15, 22, 12), mat=lining_mat)

    # ---------------- coat skirt: eight panels flaring out to the shins, dissolving into smoke
    FL = 38.0
    for side, sx in (('right', -1), ('left', 1)):
        dz = -0.6 if sx > 0 else 0.0
        fp = bone(f'coat_front_{side}', at('body', 4.5 * sx, -0.5, -8.6 + dz), 'body', rot=(-9, 0, -7 * sx),
                  flen=FL, smoke=0.66, fseed=1 + sx)
        mbox(fp.name, sx, (-5, 0, -1), (10, int(FL), 2))
        mbox(fp.name, sx, (-4.5, 6, -1.6), (6, 2, 1), mat=lapel_mat)              # pocket flap
        mbox(fp.name, sx, (3.5, 0, -1.4), (1, 25, 1), mat=lapel_mat)               # front placket edge
        cp = bone(f'coat_flare_{side}', at('body', 9.0 * sx, -0.5, -6.6), 'body', rot=(-8, -32 * sx, -22 * sx),
                  flen=FL, smoke=0.64, fseed=3 + sx)
        mbox(cp.name, sx, (-4.5, 0, -1), (8, int(FL), 2))
        mbox(cp.name, sx, (-4.8, 3, -1.2), (0, 26, 3), mat=tatter_mat(23 + sx))
        sp = bone(f'coat_side_{side}', at('body', 9.8 * sx, -0.5, 2.5), 'body', rot=(0, 90, -28 * sx),
                  flen=FL - 2, smoke=0.64, fseed=5 + sx)
        box(sp.name, (-11, 0, -1), (20, int(FL - 2), 2))
        bp = bone(f'coat_back_{side}', at('body', 5.0 * sx, -0.5, 9.4 - dz), 'body', rot=(16, 0, -7 * sx),
                  flen=FL, smoke=0.64, fseed=7 + sx)
        mbox(bp.name, sx, (-5.5, 0, -1), (11, int(FL), 2))
        mbox(bp.name, sx, (-5.8, 4, -1), (0, 26, 3), mat=tatter_mat(51 + sx))
    tr = bone('coat_trail', at('body', 0, 6, 10.5), 'body', rot=(34, 0, 0))
    box(tr.name, (-11, 0, 0), (22, 26, 0), mat=smoke_plane(61, dens=0.75, drift=-1.0))

    # ---------------- chest: leans 19 deg over the waist; the hunch is pushed BACK (+Z), not the head forward
    CH = 19
    bone('chest', at('body', 0, -14, 2.0), 'body', rot=(CH, 0, 0), mat=coat_mat)
    box('chest', (-11, -16, -9), (22, 17, 17), mat=chest_mat)
    box('chest', (-14.5, -19, -8), (29, 4, 14), mat=chest_mat)      # across the shoulders
    for yy in (-12, -8, -4):
        for sx in (-1, 1):
            box('chest', (6.5 * sx - 1, yy, -9.7), (2, 2, 1), mat=button_mat)
    # curved spine: three progressively rotated slabs (chest 19 -> 29 -> 41 -> 55 deg) rolling the upper back
    # out behind him and over into the collar; each slab carries a narrower outer slab that bevels its flanks
    bone('hump_low', at('chest', 0, -2, 7.0), 'chest', rot=(10, 0, 0), mat=hump_mat)
    box('hump_low', (-11, -12, -1), (22, 12, 4))
    box('hump_low', (-8, -11, 2.6), (16, 10, 2))
    bone('hump_mid', at('hump_low', 0, -12, 1.0), 'hump_low', rot=(12, 0, 0), mat=hump_mat)
    box('hump_mid', (-9.5, -7, -2), (19, 8, 5))
    box('hump_mid', (-6.5, -6, 2.6), (13, 6, 2))
    bone('hump', at('hump_mid', 0, -7, 0.0), 'hump_mid', rot=(14, 0, 0), mat=hump_mat)
    box('hump', (-7.5, -6, -3), (15, 7, 5))
    box('hump', (-4.5, -5, 1.6), (9, 4, 2))
    # bevelled shoulder capes with epaulettes (turned 90 deg: local z runs along world x)
    for side, sx in (('right', -1), ('left', 1)):
        sh = bone(f'{side}_shoulder', at('chest', 10.0 * sx, -19.5, -0.5), 'chest', rot=(0, 90, 17 * sx), mat=coat_mat)
        box(sh.name, (-8.5, -1, -8 if sx < 0 else -1), (17, 4, 9))
        box(sh.name, (-1.5, -1.6, -7 if sx < 0 else 1), (4, 1, 6), mat=lapel_mat)
    for side, sx in (('right', -1), ('left', 1)):
        lp = bone(f'lapel_{side}', at('chest', 4.5 * sx, -17, -10.0 - (0.1 if sx > 0 else 0)), 'chest',
                  rot=(0, 0, 22 * sx), mat=lapel_mat)
        mbox(lp.name, sx, (-4, 0, -1.2), (7, 11, 2))

    # ---------------- neck + head (world targets: the neck juts forward out of the hump, the face is vertical)
    NECK_W = (0, -48.4, 4.6)
    HEAD_W = (0, -58.5, -1.0)
    NECK_ANG = 29.0
    wbone('neck', NECK_W, 'chest', rot=(NECK_ANG - CH, 0, 0), mat=skin_mat)
    box('neck', (-3, -12.5, -3), (6, 13, 6))
    HEAD_X = -4.0
    wbone('head', HEAD_W, 'neck', rot=(HEAD_X - NECK_ANG, 0, 9), mat=skin_mat)

    ZF = -11.5        # cranium front (head-local z)
    YS = -3.8         # the seam = jaw hinge = upper-lip line (head-local y)
    YT = YS - CRAN_H  # cranium top (hidden in the crown)
    box('head', (-9, YT, ZF), (FACE_W, CRAN_H, 16), cranium=True, decals={
        'front': face_front_decal, 'eyes:front': eyes_glow_decal,
        'west': grin_side_decal(True), 'east': grin_side_decal(False)})
    # brow shelf: a scowling V of black mass over the eyes (sides high, centre low)
    for sx in (-1, 1):
        box('head', mx(sx, (-9.1, YT + 4.0, ZF - 1.5), (6, 2, 4)), (6, 2, 4), mat=brow_mat)
    box('head', (-3, YT + 5.4, ZF - 1.2), (6, 2, 4), mat=brow_mat)
    box('head', (-7, YT + 2, ZF + 16), (14, 9, 2))   # occiput: rounds the back of the skull
    # gullet behind the jaw: only its upper rows show through the open maw; it also frames the jumpscare portrait
    box('head', (-5, YS, -1.0), (10, 14, 3), mat=throat_mat, decals={'eyes:front': throat_glow_decal})
    # upper needles of the grin: head-bound, just in front of the jaw -> the grin's teeth when shut, the upper
    # fangs when the jaw drops
    box('head', (TEETH_X0 - 9, YS, ZF + 0.15), (FACE_W - 2 * TEETH_X0, 5, 0), mat=front_teeth_mat)
    for sx in (-1, 1):
        box('head', (5.6 * sx, YS, ZF + 2.0), (0, 4, 9), mat=needle_teeth(423 + sx, 1, axis='z'))
        f = box('head', mx(sx, (-6.3, YS, ZF + 0.9), (1, 5, 1)), (1, 5, 1), mat=tooth_cube_mat)
        f.grow = 1
        box('head', mx(sx, (-7.2, YS, ZF + 2.2), (3, 6, 0)), (3, 6, 0), mat=strands_mat(431 + sx, 1))
        box('head', (7.3 * sx, YS, ZF + 1.5), (0, 8, 11), mat=cheek_skin_mat(437 + sx))

    bone('jaw', at('head', 0, YS, 1.0), 'head', mat=jaw_mat)
    JZ = ZF + 0.3     # jaw front, a hair behind the cranium (upper lip overhangs)
    box('jaw', (-8, 0.03, JZ - 1.0), (JAW_W, JAW_H, 12), tongue=True, decals={'front': jaw_front_decal})
    box('jaw', (-5, JAW_H, JZ - 0.6), (10, 2, 7))                  # tapered chin
    box('jaw', (-4, JAW_H + 2, JZ - 0.2), (8, 1, 5))
    box('jaw', (-5, -4.97, JZ - 0.4), (10, 5, 0), mat=needle_teeth(441, -1))
    for sx in (-1, 1):
        box('jaw', (5.4 * sx, -3.97, JZ - 0.5), (0, 4, 8), mat=needle_teeth(443 + sx, -1, axis='z'))
        f = box('jaw', mx(sx, (-6.0, -5.97, JZ - 0.6), (1, 6, 1)), (1, 6, 1), mat=tooth_cube_mat)
        f.grow = -1
        box('jaw', mx(sx, (-7.0, -5.97, JZ + 1.5), (3, 6, 0)), (3, 6, 0), mat=strands_mat(451 + sx, -1))

    # ---------------- hat: wide snap-brim fedora, low pinched crown, teardrop crease, violet-black band
    bone('hat', at('head', 0, YT + 3.0, -3.5), 'head', rot=(2, 0, -6), mat=felt_mat)
    hat0 = r.abs_pivot['hat']
    r.bones['hat'].hat_off = (0.0, 0.0, 0.0)

    def brim(bname, frm, size):
        b = r.bones[bname]
        o = b.hat_off
        BRIM_RECTS.append((frm[0] + o[0], frm[0] + size[0] + o[0], frm[2] + o[2], frm[2] + size[2] + o[2]))
        return box(bname, frm, size)

    brim('hat', (-22, 0, -12), (44, 2, 12))
    brim('hat', (-22, 0, 0), (44, 2, 12))
    for sx in (-1, 1):
        brim('hat', mx(sx, (-26, 0, -8), (4, 2, 8)), (4, 2, 8))
        brim('hat', mx(sx, (-26, 0, 0), (4, 2, 8)), (4, 2, 8))
        brim('hat', mx(sx, (-28, 0, -4), (2, 2, 8)), (2, 2, 8))
    box('hat', (-10.5, -3, -10.5), (21, 3, 21), mat=band_mat)
    # crown: a taller, wider back and a narrower, lower pinched front, each with a 1-texel inset cap
    box('hat', (-9.5, -9, -3.5), (19, 9, 13), mat=crown_mat)
    box('hat', (-8.5, -10, -2.5), (17, 1, 11), mat=crown_mat)
    box('hat', (-8.5, -7.6, -9.5), (17, 8, 6), mat=crown_mat, pinch=True)
    box('hat', (-7.5, -8.6, -8.5), (15, 1, 5), mat=crown_mat)
    fb = bone('hat_brim_front', at('hat', 0, 1, -12), 'hat', rot=(12, 0, 0), mat=felt_mat)
    fb.hat_off = (0.0, 1.0, -12.0)
    for wdt, z0, dep in ((44, -3, 3), (38, -6, 3), (28, -8, 2), (16, -9, 1)):
        brim('hat_brim_front', (-wdt / 2, -1, z0), (wdt, 2, dep))
    bb = bone('hat_brim_back', at('hat', 0, 1, 12), 'hat', rot=(8, 0, 0), mat=felt_mat)
    bb.hat_off = (0.0, 1.0, 12.0)
    for wdt, z0, dep in ((44, 0, 3), (38, 3, 3), (28, 6, 2), (16, 8, 1)):
        brim('hat_brim_back', (-wdt / 2, -1, z0), (wdt, 2, dep))

    # ---------------- collar: popped, stands up behind the skull and flares out beside the jaw
    wbone('collar_back', (0, -49.5, 7.5), 'chest', rot=(-12 - CH, 0, 0), mat=lapel_mat)
    box('collar_back', (-9, -13, -1.5), (18, 13, 3))
    for side, sx in (('right', -1), ('left', 1)):
        wbone(f'collar_{side}', (9.5 * sx, -48.5, 1.0), 'chest', rot=(-14 - CH, 48 * sx, 12 * sx), mat=lapel_mat)
        mbox(f'collar_{side}', sx, (-1, -11, -9), (2, 11, 11))

    # ---------------- arms: impossibly long thin sleeves, a wrong-way elbow break, bare bony wrists, spider hands
    ARM = {
        # side: (arm rot, forearm rot, hand rot, finger fan, tip curls)
        'right': ((-CH + 3, 0, 5), (-12, 8, 7), (8, 24, -6), (-9, -2, 5, 12), (18, 22, 26, 30)),
        'left': ((-CH + 1, 0, -6), (-14, -10, -8), (12, -30, 8), (-10, -1, 6, 14), (30, 34, 40, 44)),
    }
    for side, sx in (('right', -1), ('left', 1)):
        arot, frot, hrot, fan, curls = ARM[side]
        arm = wbone(f'{side}_arm', (14.5 * sx, -44.5, -1.5), 'chest', rot=arot, mat=sleeve_mat)
        box(arm.name, (-2.5, -2.5, -2.5), (5, 19, 5))
        fa = bone(f'{side}_forearm', at(arm.name, 0, 16, 0), arm.name, rot=frot, mat=sleeve_mat, elbow=True)
        box(fa.name, (-2, -1, -2), (4, 20, 4))
        box(fa.name, (-2.5, 17, -2.5), (5, 3, 5), mat=lapel_mat)          # small cuff
        hd = bone(f'{side}_hand', at(fa.name, 0, 20, 0), fa.name, rot=hrot, mat=hand_mat)
        box(hd.name, (-1.5, -0.5, -1.5), (3, 4, 3))                         # bare bony wrist
        box(hd.name, (-3, 3, -1), (6, 5, 2))                                # palm
        box(hd.name, (-3, 7, -1.5), (6, 2, 3), inflate=0.05)                # knuckle ridge
        lens = ((9, 7, 3), (10, 8, 4), (10, 7, 3), (8, 6, 3))
        for k in range(4):
            xc = (1.5 - k) * 1.6 * -sx
            p, m, c = lens[k]
            fg = bone(f'{side}_finger{k}', at(hd.name, xc, 8.5, 0), hd.name, rot=(6, 0, -fan[k] * sx), mat=hand_mat)
            box(fg.name, (-1, 0, -1), (2, p, 2))
            tp = bone(f'{side}_finger{k}_tip', at(fg.name, 0, p, 0), fg.name, rot=(curls[k], 0, 0), mat=hand_mat)
            box(tp.name, (-1, 0, -1), (2, m, 2))
            box(tp.name, (-0.5, m, -0.5), (1, c, 1), mat=nail_mat)
        th = bone(f'{side}_thumb', at(hd.name, 2.6 * -sx, 3.5, -0.5), hd.name, rot=(-14, 0, 30 * sx), mat=hand_mat)
        box(th.name, (-1, 0, -1), (2, 7, 2))
        box(th.name, (-0.5, 7, -0.5), (1, 3, 1), mat=nail_mat)

    # ---------------- hem smoke: every translucent smoke sheet of the coat in ONE bone, authored last
    hs = bone('smoke_hem', at('body', 0, 20, 0), 'body')
    for (x0, z0, w, d, y0, hgt, seed) in ((-13, -12.5, 26, 0, -14, 22, 11), (-14, 17.5, 28, 0, -14, 22, 41),
                                          (-21, -8, 0, 22, -15, 21, 31), (21, -8, 0, 22, -15, 21, 32),
                                          (-24, -6, 11, 0, -13, 19, 21), (13, -6, 11, 0, -13, 19, 22)):
        box(hs.name, (x0, y0, z0 - 1.5), (w, hgt, d), mat=smoke_plane(seed, dens=0.8, top_fade=0.3))

    m = Model('sombra', 256, 256, r.roots)
    m.scale = 0.5
    m.render_type = 'entityTranslucent'
    return m


DEFAULT_MAT = coat_mat
FOCUS = 'head'

POSES = {
    'reach': {},
    'attack': {
        'chest': (0.3, 0, 0, 0, 0, 0),
        'head': (-0.42, 0, -0.06, 0, 0, 0),
        'jaw': (1.05, 0, 0, 0, 0, 0),
        'right_arm': (-1.25, 0.15, 0.3, 0, 0, 0),
        'left_arm': (-1.0, -0.15, -0.35, 0, 0, 0),
    },
    'scream': {
        'jaw': (1.25, 0, 0, 0, 0, 0),
    },
}

ANIM_NOTES = """(rewritten below once the poses are final)"""
