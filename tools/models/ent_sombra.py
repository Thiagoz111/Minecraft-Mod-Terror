"""El Hombre Sombra -- the Hat Man (DEAD LINE).

Authored at 2x texel density (model.scale = 0.5) with rig.Rig absolute coordinates:
+Y down, ground at y = 24, the creature faces -Z, right_* parts on -X.
Every cube is authored in its bone's *unrotated* frame; bone rotations fold the figure into its hunched,
head-tilted stance. The head sits over the body (centre z ~ -7) so it stays inside the 0.8 x 3.4 hitbox.

Design: a pure black silhouette -- a wide, flat snap-brim fedora (one continuous oval brim built from a centre
slab and four angled brim bones, a low crown of inward-leaning side plates with front pinches and a teardrop
crease), a humped back with a popped collar hugging the skull, broad bevelled shoulders, a deep belted trench
coat whose eight panels flare out to the shins and dissolve into soft drifting smoke, and impossibly long
sleeved arms ending in spider fingers.
Only deliberate dark blue / violet rim tones describe the volumes. Under the brim: a scowling brow shelf, two
tiny burning ember eyes and the faint suggestion of a grin that runs ear to ear; the jaw unhinges to show rows
of needle teeth, torn cheek strands and a single ember smouldering deep in the throat.

Some long, flat slabs (side coat panels, side brims, shoulder capes, crown plates) are authored broad-side-on
and turned 90 degrees about Y by their bone: the box-UV layout wastes 2*depth^2 texels, so this keeps the
whole creature inside one 256x256 sheet.
"""
import math

from mcmodel import Model, fbm, hash3, face_light, pick
from rig import Rig
from paint import hx, mix, edge


def pal(*h):
    return [hx(c) for c in h]


# ------------------------------------------------------------------ palettes (dark -> light)
SHADE = pal('#010102', '#040409', '#08080f', '#0d0c17', '#131121', '#1a172c', '#221e3a', '#2c264a', '#3a325e')
FELT = pal('#010102', '#050508', '#0a0910', '#100e19', '#171423', '#1f1b2f', '#28223c', '#332b4c', '#41376a')
BAND = pal('#020102', '#050206', '#09040b', '#0e0610', '#140816', '#1a0b1c')
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
FELT2 = fine(FELT, 17)


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
    """Texel centre in absolute authored coordinates (before bone rotations)."""
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


def smoky(c, v, a, k, ctx):
    """Blend a cloth colour into lighter translucent smoke as it dissolves."""
    if k <= 0 and a >= 0.999:
        return c
    x, y, z = dpos(ctx)
    n = smoke_noise(x * 1.7, y * 1.7, z * 1.7, 5)
    s = pick(SMOKE, v + 0.1 + k * 0.18 + (n - 0.5) * 0.35)
    c = mix(c, s, clamp(k * 1.5 + 0.15))
    return rgba(c, a)


def smoke_plane(seed, dens=0.85, drift=1.0):
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
        # curl: wisps bend sideways the further they drift down
        uu = u + drift * (5.0 * t * t + 1.6 * math.sin(t * 5.0 + seed))
        n = smoke_noise(uu * 1.1 + seed * 3.7, yy * 1.1, seed * 1.3, seed)
        mask = clamp(t / 0.16) * (1.0 - t) ** 1.15
        side = min(u, uw - u) / max(1.0, uw * 0.18)
        mask *= clamp(side + 0.25)
        a = clamp((n - 0.36) * 2.6) * mask * dens
        if a < 0.06:
            return None
        v = 0.40 + (n - 0.5) * 0.5 - t * 0.12 + face_light(ctx) * 0.3
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
    if ctx.face in ('front', 'back'):
        col = lx
    else:
        col = lz
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
        col = mix(pick(SHADE, v), pick(SMOKE, v + 0.1), clamp(t / L * 1.2))
        return rgba(col, 1.0 - (t / L) ** 1.6)
    return f


def lining_mat(ctx):
    """Inside of the coat: a void, barely any light gets in; it fades into smoke."""
    lx, ly, lz = local(ctx)
    v = 0.10 + face_light(ctx) * 0.3
    c = pick(SHADE, v)
    t = (ly - ctx.cube.origin[1]) / ctx.cube.size[1]
    if ctx.face != 'top':
        r = dissolve(ctx, t, 0.45, 41)
        if r is None:
            return None
        return smoky(c, v, *r, ctx)
    return c


def trouser_mat(ctx):
    v = form(ctx, 0.20)
    c = pick(SHADE, v)
    if ctx.face == 'top':
        return c
    lx, ly, lz = local(ctx)
    r = dissolve(ctx, ly / 40.0, 0.42, 61)
    if r is None:
        return None
    return smoky(c, v - 0.2, *r, ctx)


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
        e = edge(ctx)
        if e == 1 and (ctx.i + ctx.j) % 2 == 0:
            v -= 0.07  # stitch line one texel in from the edge
    return pick(CLOTH, v)


def chest_mat(ctx):
    """Torso of the coat; the V between the lapels is a pure void (nothing inside the coat)."""
    v = form(ctx, 0.31)
    x, y, z = dpos(ctx)
    if ctx.face == 'front' and ctx.bone.name == 'chest':
        if abs(x) < 1.0 + (y + 46) * 0.42 and y < -36:
            return SHADE[0]  # open V of the coat: a void
        if abs(abs(x) - 6.5) < 0.5 and y > -37:
            v -= 0.07  # double-breasted seams
        f = fbm(x * 0.2, y * 0.12, 3.0, 2, 17)
        if f < 0.4:
            v -= 0.06
        elif f > 0.62:
            v += 0.05
    if ctx.face == 'back' and abs(x) < 0.5:
        v -= 0.08  # centre back seam
    if ctx.face in ('west', 'east') and abs(z - 1.5) < 0.5:
        v -= 0.06  # side seam
    v += 0.06 * clamp((-y - 30) / 14.0)  # sheen gathers on the chest
    return pick(CLOTH, v)


def sleeve_mat(ctx):
    """Sleeves: vertical sheen + twisting creases at the elbow."""
    v = form(ctx, 0.29)
    lx, ly, lz = local(ctx)
    if is_side(ctx) and not flat(ctx):
        col = lx if ctx.face in ('front', 'back') else lz
        if getattr(ctx.bone, 'elbow', False) and ly < 7:
            ph = (col * 0.9 + ly * 0.8) % 4.0
            if ph < 0.9:
                v -= 0.08
            elif ph < 1.8:
                v += 0.06
        if abs(col) < 0.6 and ctx.face == 'back':
            v -= 0.05  # sleeve seam
        v += 0.05 * (1 - ctx.t)  # sheen on the upper part of each sleeve piece
    return pick(CLOTH, v)


# ------------------------------------------------------------------ hat
def felt_mat(ctx):
    """Hat felt: soft violet sheen gradient on top, violet rim on the brim edge, pitch black underside."""
    if ctx.face == 'bottom':
        return FELT[0] if edge(ctx) > 0 else FELT[2]
    x, y, z = dpos(ctx)
    if ctx.face == 'top':
        # soft sheen: brightest on a ring around the crown where the moon catches the felt
        r = math.sqrt((x / 26.0) ** 2 + ((z + 3) / 20.0) ** 2)
        v = 0.36 + 0.10 * math.exp(-((r - 0.62) / 0.22) ** 2) - 0.05 * clamp(r - 0.85) * 4
        v += 0.03 * math.sin(x * 0.35 + z * 0.22)
        if edge(ctx) == 0:
            v += 0.08
        return pick(FELT, v)
    # brim edge (2 texels tall): the faint violet rim that outlines the oval
    v = 0.58 + face_light(ctx) * 0.6
    if ctx.j == ctx.h - 1:
        v -= 0.14
    return pick(FELT, v)


def crown_mat(ctx):
    v = form(ctx, 0.34, rim=0.1)
    if ctx.face == 'bottom':
        return FELT[0]
    lx, ly, lz = local(ctx)
    if is_side(ctx) and not flat(ctx):
        v -= ctx.t * 0.08  # darker toward the band
        if ctx.face == 'front' and ctx.bone.name == 'hat':
            # front pinches: two dents either side of the centre
            for px_ in (-4.0, 4.0):
                d = abs(lx - px_)
                if d < 0.6:
                    v -= 0.13
                elif d < 1.6 and (lx - px_) * px_ < 0:
                    v += 0.06
    if ctx.face == 'top':
        if ctx.bone.name == 'hat':
            # teardrop crease along the centre: shaded channel, narrowing toward the back
            wid = 2.4 - (lz + 9) * 0.07
            if abs(lx) < wid:
                v -= 0.16
            elif abs(lx) < wid + 1.2:
                v -= 0.06
        else:
            v += 0.05  # rounded shoulders of the crown either side of the crease
    return pick(FELT, v)


def band_mat(ctx):
    v = form(ctx, 0.40, rim=0.12)
    if ctx.face == 'bottom':
        return BAND[0]
    if is_side(ctx) and ctx.j == ctx.h - 1:
        v -= 0.1
    return pick(BAND, v)


# ------------------------------------------------------------------ head
FACE_W, FACE_H = 18, 14          # cranium front (x -9..9); its top hides inside the brim
SEAM = 14                        # face-grid row where the jaw front begins
EYES = ((4, 5), (12, 5))         # top-left texel of each 2x2 hot core (viewer's left eye first)


def skin_mat(ctx):
    """Head / neck: void skin, violet sheen only on the planes that catch the moon."""
    v = form(ctx, 0.20, rim=0.08)
    if ctx.bone.name == 'head' and ctx.cube.size[0] == FACE_W:
        if ctx.face == 'bottom':
            return palate_mat(ctx)
        if ctx.face in ('west', 'east'):
            v -= 0.08 * clamp(1.0 - ctx.t * 3)  # shadow under the hat
    return pick(SHADE, v)


def brow_mat(ctx):
    """Brow shelf: black mass, a thin violet line where the moon grazes its upper edge."""
    if ctx.face == 'bottom':
        return VOID
    v = 0.14 + face_light(ctx) * 0.5
    if is_side(ctx) and ctx.j == 0:
        v += 0.18
    return pick(SHADE, v)


def cheekbone_mat(ctx):
    v = 0.20 + face_light(ctx) * 0.8
    if ctx.face == 'front' and ctx.j == 0:
        v += 0.12
    return pick(SHADE, v)


def palate_mat(ctx):
    """Roof of the mouth: smooth black-to-dark-red gradient deepening toward the throat."""
    lx, ly, lz = local(ctx)
    zf = ctx.cube.origin[2]
    k = clamp((lz - zf - 1.0) / 13.0)
    if lz - zf < 1.0:
        return VOID
    v = 0.08 + 0.55 * k - 0.25 * clamp((abs(lx) - 5.0) / 3.0)
    return pick(MAW, v)


def throat_mat(ctx):
    """The gullet behind the jaw: its front face is the ember-lit back wall of the maw."""
    if ctx.face == 'front':
        lx, ly, lz = local(ctx)
        c = ctx.cube
        r = math.sqrt((lx / 6.0) ** 2 + ((ly - c.origin[1] - 3.5) / 4.5) ** 2)
        return pick(MAW, 0.62 - r * 0.7)
    return pick(SHADE, form(ctx, 0.18))


def jaw_mat(ctx):
    v = form(ctx, 0.20, rim=0.08)
    lx, ly, lz = local(ctx)
    if ctx.face == 'top' and ctx.cube.size[0] >= 14:
        # tongue bed: black at the lip, dark red deepening toward the throat, soft central groove
        zf = ctx.cube.origin[2]
        if lz - zf < 1.0:
            return VOID
        k = clamp((lz - zf - 1.0) / 12.0)
        vv = 0.06 + 0.42 * k ** 1.5 - 0.3 * clamp((abs(lx) - 4.5) / 3.0)
        if abs(lx) < 0.6:
            vv -= 0.12
        return pick(MAW, vv)
    if ctx.face == 'front' and ctx.cube.size[1] <= 3:
        v += 0.05  # chin catches the under-light
    return pick(SHADE, v)


def tooth_cube_mat(ctx):
    """Fangs: long bone-violet needles, lighter toward the tip."""
    c = ctx.cube
    lx, ly, lz = local(ctx)
    grow = getattr(c, 'grow', 1)
    t = (ly - c.origin[1]) / c.size[1]
    t = t if grow > 0 else 1 - t
    v = 0.42 + t * 0.45 + face_light(ctx) * 0.6
    if ctx.face in ('west', 'east'):
        v -= 0.08
    return pick(TOOTH, v)


def needle_teeth(seed, grow=1, axis='x', pitch=3):
    """A row of needle teeth on a zero-thickness plane.

    Solid gum band at the root; each tooth is 2 texels wide at the root tapering to a 1-texel tip,
    3-6 texels long with irregular lengths; transparent between the teeth.
    grow=1: roots at the top (upper teeth hang down); grow=-1: roots at the bottom (lower teeth point up)."""
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
        L = 3 + int(hash3(k, 0, 0, seed) * 3.99)  # 3..6 texels
        if row > L:
            return None
        if row > (L + 1) // 2:
            tipcol = 0 if hash3(k, 1, 0, seed) < 0.5 else 1
            if m != tipcol:
                return None
        tt = row / L
        v = 0.30 + tt * 0.6 + face_light(ctx) * 0.4
        if m == 1 and row <= (L + 1) // 2:
            v -= 0.1  # shaded side of the tooth
        return pick(TOOTH, v)
    return f


def strands_mat(seed, grow=1, spacing=1.8):
    """Torn cheek strands / sinew stretched across the mouth corners (zero-thickness plane, translucent)."""
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
        v = 0.72 - t * 0.25 + face_light(ctx) * 0.3
        return rgba(pick(MAW, v), best * 0.96)
    return f


def cheek_skin_mat(seed):
    """Stretched cheek skin on the side of the jaw (YZ plane): torn vertical slits with raw red edges."""
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
            return pick(MAW, 0.35)
        v = 0.18 + face_light(ctx) * 0.6 + (0.05 if (u + t * 3) % 3 < 0.6 else 0)
        return pick(SHADE, v)
    return f


# ---------------- face pixel art (shared grid in cranium texels: cols 0..17, rows 0..13 cranium, 14.. jaw)
# closed grin: (upper lip row, lower lip row) per column of the left half; the right half mirrors it
_LIPS = {3: (8, 10), 4: (9, 12), 5: (9, 13), 6: (10, 14), 7: (10, 15), 8: (11, 16)}


def lips(c):
    return _LIPS.get(17 - c if c > 8 else c)


def grin_cells():
    """The closed grin as {(col, row): colour} on the shared face grid.

    A thin black crescent rising toward the cheekbones with a row of dark needle teeth hanging from the upper
    lip (2-wide root, 1-wide tip) and small lower points between them. Only TOOTH 1..3: it reads up close or
    when the jaw opens, never as the brightest thing on the figure."""
    cells = {}
    for c in range(3, 15):
        U, D = lips(c)
        cells[(c, U)] = VOID
        for r in range(U + 1, D):
            cells[(c, r)] = MAW[0]
        cells[(c, D)] = VOID
        cells[(c, D + 1)] = SHADE[3]   # lower lip catches a little light
    for c, r in ((2, 8), (1, 7), (15, 8), (16, 7)):
        cells[(c, r)] = VOID           # the cut keeps rising under the cheekbones
    for a, b in ((3, 4), (6, 7), (9, 10), (12, 13)):   # (root column, tip column)
        Ua, Da = lips(a)
        Ub, Db = lips(b)
        cells[(a, Ua + 1)] = TOOTH[1]
        hb = Db - Ub - 1
        n = max(2, min(hb - 1, round(hb * 0.7)))
        for k in range(n):
            cells[(b, Ub + 1 + k)] = TOOTH[1] if k == 0 else TOOTH[2] if k < n - 1 else TOOTH[3]
    U14, _ = lips(14)
    cells[(14, U14 + 1)] = TOOTH[1]
    for g in (5, 8, 11):               # lower points in the gaps
        Ug, Dg = lips(g)
        n = max(1, round((Dg - Ug - 1) * 0.45))
        for k in range(n):
            cells[(g, Dg - 1 - k)] = TOOTH[1] if k < n - 1 else TOOTH[2]
    return cells


GRIN = grin_cells()


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


def face_front_decal(img, u0, v0, w, h):
    """Cranium front: under-brim shadow, deep sockets with ember spill, cheekbone planes, the faint grin."""
    px = img.load()
    for j in range(h):
        for i in range(w):
            x, y = i + 0.5, j + 0.5
            v = 0.04 + 0.2 * clamp((y - 3.0) / 10.0)
            c = pick(SHADE, v)
            for (ex, ey), sgn in ((EYES[0], 1), (EYES[1], -1)):
                dx, dy = x - (ex + 1.0), y - (ey + 1.0)
                a = math.radians(-14 * sgn)  # sockets slant down toward the nose: a scowl
                uu = dx * math.cos(a) + dy * math.sin(a)
                vv = -dx * math.sin(a) + dy * math.cos(a)
                r = (uu / 3.0) ** 2 + (vv / 1.9) ** 2
                if r <= 1.0:
                    c = VOID
                elif r <= 1.8:
                    c = mix(SHADE[1], MAW[3], (1.8 - r) / 0.8 * 0.7)  # ember light spilling on the skin
            for cx0, sgn in ((2.5, -1), (15.5, 1)):
                if j == 9 and abs(x - (cx0 - sgn * 0.0)) < 1.6:
                    c = SHADE[0]   # hollow under the cheekbone
            px[u0 + i, v0 + j] = c
    for (i, j), c in eye_cells().items():
        if 0 <= i < w and 0 <= j < h:
            px[u0 + i, v0 + j] = c
    for (i, j), c in GRIN.items():
        if 0 <= i < w and 0 <= j < h:
            px[u0 + i, v0 + j] = c


def eyes_glow_decal(img, u0, v0, w, h):
    """Emissive pass for the cranium front: the two eyes, nothing else."""
    px = img.load()
    for (i, j), c in eye_cells(glow=True).items():
        if 0 <= i < w and 0 <= j < h:
            px[u0 + i, v0 + j] = c


def jaw_front_decal(img, u0, v0, w, h):
    """Jaw front (14 wide, offset two columns from the cranium grid): lower half of the grin + chin shading."""
    px = img.load()
    for j in range(h):
        for i in range(w):
            c = GRIN.get((i + 2, j + SEAM))
            if c is None:
                v = 0.18 + 0.05 * (j / h) - (0.08 if i in (0, w - 1) else 0)
                c = pick(SHADE, v)
            px[u0 + i, v0 + j] = c


def throat_glow_decal(img, u0, v0, w, h):
    """Emissive: one soft, solid ember deep in the gullet (no dither)."""
    px = img.load()
    for j in range(h):
        for i in range(w):
            r = math.sqrt(((i + 0.5 - w / 2) / 3.2) ** 2 + ((j + 0.5 - 4.0) / 2.2) ** 2)
            if r < 0.35:
                c = GLOW[3]
            elif r < 0.65:
                c = GLOW[2]
            elif r < 0.95:
                c = GLOW[1]
            elif r < 1.3:
                c = GLOW[0]
            else:
                continue
            px[u0 + i, v0 + j] = c


def tongue_glow_decal(img, u0, v0, w, h):
    """Emissive: the ember light pooling on the back of the tongue (top face; j = 0 is the back)."""
    px = img.load()
    for j in range(h):
        for i in range(w):
            r = math.sqrt(((i + 0.5 - w / 2) / 3.0) ** 2 + (j / 2.5) ** 2)
            if r < 1.0:
                c = GLOW[0]
            else:
                continue
            px[u0 + i, v0 + j] = c


def grin_side_decal(front_high):
    """A thin cut keeps going from the grin corner around the side of the skull toward the ear."""
    def fn(img, u0, v0, w, h):
        px = img.load()
        for k in range(0, 6):
            i = (w - 1 - k) if front_high else k
            jj = int(round(7 - k * 0.4))
            if 0 <= jj < h:
                px[u0 + i, v0 + jj] = VOID if k < 4 else SHADE[1]
                if jj + 1 < h and k < 4:
                    px[u0 + i, v0 + jj + 1] = SHADE[3]
    return fn


# ------------------------------------------------------------------ hands
def hand_mat(ctx):
    """Long void fingers: violet knuckle highlights."""
    v = form(ctx, 0.26, rim=0.1)
    n = ctx.bone.name
    if is_side(ctx) and not flat(ctx):
        if ('finger' in n or 'thumb' in n) and ctx.j <= 1:
            v += 0.09  # knuckle
        if n.endswith('_hand') and ctx.face == 'front' and ctx.cube.size[1] >= 5 and ctx.i % 2 == 1:
            v += 0.06  # tendons on the back of the hand
    return pick(SHADE, v)


def nail_mat(ctx):
    """Claws: dark glossy grey-violet, a pale glint at the tip only."""
    v = 0.25 + face_light(ctx) * 1.0
    if is_side(ctx):
        v += ctx.t * 0.35
    return pick(TOOTH, v)


# ------------------------------------------------------------------ build
def build():
    r = Rig()

    def bone(name, pivot, parent=None, rot=(0, 0, 0), mat=None, **attrs):
        b = r.bone(name, pivot, parent, rot, mat)
        b.abs = r.abs_pivot[name]
        for k, v in attrs.items():
            setattr(b, k, v)
        return b

    def at(parent, dx, dy, dz):
        a = r.abs_pivot[parent]
        return (a[0] + dx, a[1] + dy, a[2] + dz)

    def box(b, frm, size, mat=None, inflate=0.0, decals=None):
        """frm relative to the bone pivot."""
        a = r.abs_pivot[b]
        return r.box(b, (a[0] + frm[0], a[1] + frm[1], a[2] + frm[2]), size, mat=mat, inflate=inflate, decals=decals)

    def mx(sx, frm, size):
        """Mirror a right-side (-X) box description to side sx (+1 = left)."""
        return frm if sx < 0 else (-(frm[0] + size[0]), frm[1], frm[2])

    def mbox(b, sx, frm, size, **kw):
        return box(b, mx(sx, frm, size), size, **kw)

    HIP = -16.0

    # ---------------- ground smoke pooling under him
    bone('smoke_pool', (0, 24, 1))
    box('smoke_pool', (-14, -0.4, -10), (28, 0, 22), mat=pool_mat)

    # ---------------- legs (hidden inside the coat; they dissolve into smoke before the ground)
    for side, sx in (('right', -1), ('left', 1)):
        leg = bone(f'{side}_leg', (4.5 * sx, HIP, 1.5), rot=(0, 0, -2 * sx), mat=trouser_mat)
        box(leg.name, (-3.5, 0, -3.5), (7, 22, 7))
        box(leg.name, (-3, 21, -3), (6, 19, 6))

    # ---------------- body: deep waist, belt + dull buckle, coat lining (inner skirt)
    bone('body', (0, HIP, 1.5), mat=coat_mat)
    box('body', (-9.5, -14, -8.5), (19, 15, 17), mat=chest_mat)
    box('body', (-10.5, -2, -9.5), (21, 3, 18), mat=belt_mat)
    box('body', (-2, -2.5, -10.1), (4, 4, 1), mat=buckle_mat)
    box('body', (-7.5, 1, -6), (15, 22, 12), mat=lining_mat)

    # ---------------- coat skirt: eight panels flaring out to the shins, dissolving into smoke
    FL = 38.0
    for side, sx in (('right', -1), ('left', 1)):
        dz = -0.6 if sx > 0 else 0.0
        # inner front panels hang almost straight (the coat closes over the legs)
        fp = bone(f'coat_front_{side}', at('body', 4.5 * sx, -0.5, -8.6 + dz), 'body', rot=(-9, 0, -7 * sx),
                  flen=FL, smoke=0.66, fseed=1 + sx)
        mbox(fp.name, sx, (-5, 0, -1), (10, int(FL), 2))
        mbox(fp.name, sx, (-5, FL - 13, 0), (10, 15, 0), mat=smoke_plane(11 + sx))
        mbox(fp.name, sx, (-4.5, 6, -1.6), (6, 2, 1), mat=lapel_mat)              # pocket flap
        mbox(fp.name, sx, (3.5, 0, -1.4), (1, 25, 1), mat=lapel_mat)               # front placket edge
        # front corner panels kick out: the flare of the hem seen from the front
        cp = bone(f'coat_flare_{side}', at('body', 9.0 * sx, -0.5, -6.6), 'body', rot=(-8, -32 * sx, -22 * sx),
                  flen=FL, smoke=0.64, fseed=3 + sx)
        mbox(cp.name, sx, (-4.5, 0, -1), (8, int(FL), 2))
        mbox(cp.name, sx, (-4.5, FL - 13, 0), (8, 14, 0), mat=smoke_plane(21 + sx))
        mbox(cp.name, sx, (-4.8, 3, -1.2), (0, 26, 3), mat=tatter_mat(23 + sx))
        # side panels (authored broad-side-on, turned 90 deg about Y)
        sp = bone(f'coat_side_{side}', at('body', 9.8 * sx, -0.5, 2.5), 'body', rot=(0, 90, -28 * sx),
                  flen=FL - 2, smoke=0.64, fseed=5 + sx)
        box(sp.name, (-11, 0, -1), (20, int(FL - 2), 2))
        box(sp.name, (-10.5, FL - 15, 0), (19, 16, 0), mat=smoke_plane(31 + sx))
        bp = bone(f'coat_back_{side}', at('body', 5.0 * sx, -0.5, 9.4 - dz), 'body', rot=(16, 0, -7 * sx),
                  flen=FL, smoke=0.64, fseed=7 + sx)
        mbox(bp.name, sx, (-5.5, 0, -1), (11, int(FL), 2))
        mbox(bp.name, sx, (-5.5, FL - 14, 0), (11, 16, 0), mat=smoke_plane(41 + sx))
        mbox(bp.name, sx, (-5.8, 4, -1), (0, 26, 3), mat=tatter_mat(51 + sx))
    # smoke streaming backward from the vent
    tr = bone('coat_trail', at('body', 0, 6, 10.5), 'body', rot=(34, 0, 0))
    box(tr.name, (-11, 0, 0), (22, 26, 0), mat=smoke_plane(61, dens=0.75, drift=-1.0))

    # ---------------- chest: deep, V-tapered, leaning forward over the waist
    CH = 12
    bone('chest', at('body', 0, -14, 0.5), 'body', rot=(CH, 0, 0), mat=coat_mat)
    box('chest', (-11.5, -15, -9.5), (23, 16, 18), mat=chest_mat)
    box('chest', (-14.5, -18, -9), (29, 5, 15), mat=chest_mat)      # across the shoulders
    for yy in (-12, -8, -4):
        for sx in (-1, 1):
            box('chest', (6.5 * sx - 1, yy, -10.2), (2, 2, 1), mat=button_mat)
    # hump: rounded slabs that roll the shoulders forward and taper into the neck
    hp = bone('hump', at('chest', 0, -12, 8.5), 'chest', rot=(-14, 0, 0), mat=coat_mat)
    box(hp.name, (-12, -6, -4), (24, 12, 6))
    box(hp.name, (-11, -11, -5), (22, 7, 6))
    box(hp.name, (-9, -14.5, -6), (18, 5, 5))
    # bevelled shoulder capes with epaulettes (turned 90 deg: local z runs along world x)
    for side, sx in (('right', -1), ('left', 1)):
        sh = bone(f'{side}_shoulder', at('chest', 10.0 * sx, -18.5, 0), 'chest', rot=(0, 90, 17 * sx), mat=coat_mat)
        box(sh.name, (-8.5, -1, -8 if sx < 0 else -1), (17, 4, 9))
        box(sh.name, (-1.5, -1.6, -7 if sx < 0 else 1), (4, 1, 6), mat=lapel_mat)
    for side, sx in (('right', -1), ('left', 1)):
        lp = bone(f'lapel_{side}', at('chest', 4.5 * sx, -17, -10.0), 'chest', rot=(0, 0, 22 * sx), mat=lapel_mat)
        mbox(lp.name, sx, (-4, 0, -1.2), (7, 11, 2))

    # ---------------- popped collar: stands up behind the skull and flares out beside the jaw
    cb = bone('collar_back', at('chest', 0, -18, 3.5), 'chest', rot=(-14, 0, 0), mat=lapel_mat)
    box(cb.name, (-9, -14, -1.5), (18, 14, 3))
    for side, sx in (('right', -1), ('left', 1)):
        cl = bone(f'collar_{side}', at('chest', 9.5 * sx, -18, 1.5), 'chest', rot=(-12, 48 * sx, 12 * sx),
                  mat=lapel_mat)
        mbox(cl.name, sx, (-1, -11, -9), (2, 11, 11))

    # ---------------- neck + head (long skull, brow shelf, faint grin, unhinging jaw)
    bone('neck', at('chest', 0, -16, 0.0), 'chest', rot=(-14, 0, 0), mat=skin_mat)
    box('neck', (-3.5, -12, -3.5), (7, 13, 7))
    Z0 = 2.0  # the whole skull sits 2 texels further back than the first draft (hitbox)
    bone('head', (0, -58.5, -4.5 + Z0), 'neck', rot=(-5, 0, 10), mat=skin_mat)

    def hb(b, frm, size, **kw):
        """Head-frame box: absolute coordinates shifted back by Z0."""
        return r.box(b, (frm[0], frm[1], frm[2] + Z0), size, **kw)

    hb('head', (-9, -73.9, -16), (FACE_W, FACE_H, 17), decals={
        'front': face_front_decal, 'eyes:front': eyes_glow_decal,
        'west': grin_side_decal(True), 'east': grin_side_decal(False)})
    # brow shelf: a scowling V of black mass over the eyes (sides high, centre low)
    for sx in (-1, 1):
        hb('head', mx(sx, (-9, -71.9, -17.5), (6, 2, 4)), (6, 2, 4), mat=brow_mat)
    hb('head', (-3, -70.4, -17.2), (6, 2, 4), mat=brow_mat)
    # cheekbones give the long skull structure
    for sx in (-1, 1):
        hb('head', mx(sx, (-9.3, -66.4, -16.5), (3, 1, 5)), (3, 1, 5), mat=cheekbone_mat)
    hb('head', (-7, -72, 1), (14, 9, 2))   # occiput: rounds the back of the skull
    # gullet behind the jaw: its front face is the ember-lit back wall of the maw
    hb('head', (-6, -59.9, -5), (12, 15, 5), mat=throat_mat, decals={'eyes:front': throat_glow_decal})
    # needle teeth hanging from the palate + corner fangs + torn strands (hidden inside the shut jaw)
    hb('head', (-6.5, -59.9, -15.2), (13, 6, 0), mat=needle_teeth(421, 1))
    for sx in (-1, 1):
        hb('head', (6.3 * sx, -59.9, -14.5), (0, 4, 9), mat=needle_teeth(423 + sx, 1, axis='z'))
        f = hb('head', mx(sx, (-5.9, -59.9, -15.0), (1, 6, 1)), (1, 6, 1), mat=tooth_cube_mat)
        f.grow = 1
        hb('head', mx(sx, (-6.8, -59.9, -13.6), (3, 6, 0)), (3, 6, 0), mat=strands_mat(431 + sx, 1))
        hb('head', (7.6 * sx, -59.9, -15.0), (0, 8, 11), mat=cheek_skin_mat(437 + sx))

    bone('jaw', (0, -60, -1.5 + Z0), 'head', mat=jaw_mat)
    hb('jaw', (-7, -59.97, -15.8), (14, 7, 14), decals={'front': jaw_front_decal, 'eyes:top': tongue_glow_decal})
    hb('jaw', (-5, -53, -15.6), (10, 3, 9))
    hb('jaw', (-3, -50, -15.2), (6, 2, 5))
    hb('jaw', (-1.5, -48, -14.6), (3, 1, 3))
    hb('jaw', (-6, -65.97, -15.3), (12, 6, 0), mat=needle_teeth(441, -1))
    for sx in (-1, 1):
        hb('jaw', (6.0 * sx, -63.97, -14.5), (0, 4, 9), mat=needle_teeth(443 + sx, -1, axis='z'))
        f = hb('jaw', mx(sx, (-4.8, -65.97, -14.8), (1, 6, 1)), (1, 6, 1), mat=tooth_cube_mat)
        f.grow = -1
        hb('jaw', mx(sx, (-6.6, -65.97, -13.2), (3, 6, 0)), (3, 6, 0), mat=strands_mat(451 + sx, -1))

    # ---------------- hat: wide flat snap-brim fedora, low pinched crown, teardrop crease, near-black band
    bone('hat', (0, -74, -5.5 + Z0), 'head', rot=(2, 0, -6), mat=felt_mat)
    box('hat', (-20, 0, -14), (40, 2, 14))
    box('hat', (-20, 0, 0), (40, 2, 14))
    box('hat', (-11, -3, -10), (22, 3, 20), mat=band_mat)
    box('hat', (-8, -8, -9), (16, 8, 18), mat=crown_mat)
    for side, sx in (('right', -1), ('left', 1)):
        # crown side plates lean inward (turned 90 deg: local z runs along world x)
        nm = f'hat_crown_{side}'
        bone(nm, at('hat', 9.5 * sx, 0, 0), 'hat', rot=(0, 90, -8 * sx), mat=crown_mat)
        box(nm, (-9, -9, -1.5 if sx < 0 else -0.5), (18, 9, 2))
    bone('hat_brim_front', at('hat', 0, 0, -13.5), 'hat', rot=(12, 0, 0), mat=felt_mat)
    box('hat_brim_front', (-18, 0, -3.5), (36, 2, 4))
    box('hat_brim_front', (-13, 0, -6.5), (26, 2, 3))
    bone('hat_brim_back', at('hat', 0, 0, 13.5), 'hat', rot=(9, 0, 0), mat=felt_mat)
    box('hat_brim_back', (-18, 0, -0.5), (36, 2, 4))
    box('hat_brim_back', (-13, 0, 3.5), (26, 2, 3))
    for side, sx in (('right', -1), ('left', 1)):
        # side brims turned 90 deg about Y so the long edge runs along local x; local z = world x
        nm = f'hat_brim_{side}'
        bone(nm, at('hat', 19.5 * sx, 0, 0), 'hat', rot=(0, 90, -5 * sx), mat=felt_mat)
        box(nm, (-12, 0, -5 if sx < 0 else -1), (24, 2, 6))
        box(nm, (-8, 0, -7.5 if sx < 0 else 4.5), (16, 2, 3))

    # ---------------- arms: impossibly long sleeves, flared cuffs, bony wrists, spider hands
    ARM = {
        # side: (arm rot, forearm rot, hand rot, finger fan, tip curls)
        'right': ((-CH + 2, 0, 8), (-8, 0, -6), (8, 0, 2), (-8, -1, 6, 13), (16, 20, 24, 28)),
        'left': ((-CH - 4, 0, -7), (-10, 8, 4), (14, 26, -4), (-10, 0, 7, 14), (30, 36, 40, 46)),
    }
    for side, sx in (('right', -1), ('left', 1)):
        arot, frot, hrot, fan, curls = ARM[side]
        arm = bone(f'{side}_arm', at('chest', 15.0 * sx, -15.5, 0.5), 'chest', rot=arot, mat=sleeve_mat)
        box(arm.name, (-4, -3.5, -4), (8, 8, 8))
        box(arm.name, (-3.5, 3, -3.5), (7, 10, 7))
        box(arm.name, (-3, 12, -3), (6, 9, 6))
        fa = bone(f'{side}_forearm', at(arm.name, 0, 20, 0), arm.name, rot=frot, mat=sleeve_mat, elbow=True)
        box(fa.name, (-3.5, -1.5, -3.5), (7, 3, 7))
        box(fa.name, (-3, 1, -3), (6, 8, 6))
        box(fa.name, (-2.5, 8, -2.5), (5, 8, 5))
        box(fa.name, (-3.5, 14, -3.5), (7, 5, 7), mat=lapel_mat)
        hd = bone(f'{side}_hand', at(fa.name, 0, 18.5, 0), fa.name, rot=hrot, mat=hand_mat)
        box(hd.name, (-1.5, -1.5, -1.5), (3, 4, 3))
        box(hd.name, (-3.5, 2, -1), (7, 5, 2))
        box(hd.name, (-3.5, 6, -1.5), (7, 2, 3))
        lens = ((9, 7, 3), (10, 8, 4), (10, 7, 3), (8, 6, 3))
        for k in range(4):
            xc = (3 - 2 * k) * -sx * 0.9
            p, m, c = lens[k]
            fg = bone(f'{side}_finger{k}', at(hd.name, xc, 7.5, 0), hd.name, rot=(6, 0, -fan[k] * sx), mat=hand_mat)
            box(fg.name, (-1, 0, -1), (2, p, 2))
            tp = bone(f'{side}_finger{k}_tip', at(fg.name, 0, p, 0), fg.name, rot=(curls[k], 0, 0), mat=hand_mat)
            box(tp.name, (-1, 0, -1), (2, m, 2))
            box(tp.name, (-0.5, m, -0.5), (1, c, 1), mat=nail_mat)
        th = bone(f'{side}_thumb', at(hd.name, 3.5 * -sx, 3.0, -0.5), hd.name, rot=(-14, 0, 32 * sx), mat=hand_mat)
        box(th.name, (-1, 0, -1), (2, 7, 2))
        box(th.name, (-0.5, 7, -0.5), (1, 3, 1), mat=nail_mat)

    m = Model('sombra', 256, 256, r.roots)
    m.scale = 0.5
    m.render_type = 'entityTranslucent'
    return m


DEFAULT_MAT = coat_mat
FOCUS = 'head'

POSES = {
    # one arm thrown at the viewer, wrist bent back so the open spider hand faces the camera, fingers splayed
    'reach': {
        'chest': (0.06, -0.38, 0, 0, 0, 0),
        'neck': (0, 0.22, 0, 0, 0, 0),
        'head': (-0.12, 0.18, 0.22, 0, 0, 0),
        'hat': (-0.04, 0, -0.05, 0, 0, 0),
        'right_shoulder': (0, 0, 0, 0, 0, -1.5),
        'right_arm': (-1.3, 0.5, 0.1, 0, 0, -2.0),
        'right_forearm': (-0.1, 0, 0, 0, 0, 0),
        'right_hand': (-1.25, 0, 0, 0, 0, 0),
        'right_finger0': (0, 0, -0.62, 0, 0, 0),
        'right_finger1': (0, 0, -0.22, 0, 0, 0),
        'right_finger2': (0, 0, 0.24, 0, 0, 0),
        'right_finger3': (0, 0, 0.66, 0, 0, 0),
        'right_finger0_tip': (-0.3, 0, 0, 0, 0, 0),
        'right_finger1_tip': (-0.32, 0, 0, 0, 0, 0),
        'right_finger2_tip': (-0.36, 0, 0, 0, 0, 0),
        'right_finger3_tip': (-0.4, 0, 0, 0, 0, 0),
        'right_thumb': (-0.3, 0, -0.55, 0, 0, 0),
        'left_arm': (0.1, 0, -0.08, 0, 0, 0),
    },
    # lunge: torso folds forward, chin up so the eyes stay clear of the brim, jaw unhinged, both claws forward
    'attack': {
        'chest': (0.3, 0, 0, 0, 0, 0),
        'neck': (-0.05, 0, 0, 0, 0, 0),
        'head': (-0.42, 0, -0.06, 0, 0, 0),
        'jaw': (1.05, 0, 0, 0, 0, 0),
        'hat': (-0.06, 0, 0.04, 0, 0, 0),
        'right_arm': (-1.25, 0.15, 0.3, 0, 0, 0),
        'right_forearm': (-0.35, 0, 0, 0, 0, 0),
        'right_hand': (-0.3, 0, 0, 0, 0, 0),
        'left_arm': (-1.0, -0.15, -0.35, 0, 0, 0),
        'left_forearm': (-0.25, 0, 0, 0, 0, 0),
        'left_hand': (-0.2, 0, 0, 0, 0, 0),
        'right_finger0_tip': (0.25, 0, 0, 0, 0, 0),
        'right_finger1_tip': (0.25, 0, 0, 0, 0, 0),
        'right_finger2_tip': (0.25, 0, 0, 0, 0, 0),
        'right_finger3_tip': (0.25, 0, 0, 0, 0, 0),
    },
    # shoulders hunch up, forearms fold up so the claws frame the face, head thrust at the camera, jaw unhinged
    'scream': {
        'chest': (0.12, 0, 0, 0, 0, 0),
        'right_shoulder': (0, 0, 0, 0, -2.5, 0),
        'left_shoulder': (0, 0, 0, 0, -2.5, 0),
        'neck': (0.32, 0, 0, 0, 0, 0),
        'head': (-0.38, 0, -0.12, 0, 0, 0),
        'jaw': (1.25, 0, 0, 0, 0, 0),
        'hat': (-0.12, 0, 0.06, 0, 0, 0),
        'right_arm': (-0.95, 0, 0.55, 0, -1.5, 0),
        'right_forearm': (-2.4, 0.3, 0, 0, 0, 0),
        'right_hand': (0.55, 0, 0.45, 0, 0, 0),
        'left_arm': (-0.8, 0, -0.85, 0, -1.5, 0),
        'left_forearm': (-2.4, -0.6, 0, 0, 0, 0),
        'left_hand': (0.45, 0, -0.45, 0, 0, 0),
        'right_finger0_tip': (0.4, 0, 0, 0, 0, 0),
        'right_finger1_tip': (0.4, 0, 0, 0, 0, 0),
        'right_finger2_tip': (0.4, 0, 0, 0, 0, 0),
        'right_finger3_tip': (0.4, 0, 0, 0, 0, 0),
        'left_finger0_tip': (0.1, 0, 0, 0, 0, 0),
        'left_finger1_tip': (0.1, 0, 0, 0, 0, 0),
        'left_finger2_tip': (0.1, 0, 0, 0, 0, 0),
        'left_finger3_tip': (0.1, 0, 0, 0, 0, 0),
    },
}

ANIM_NOTES = """El Hombre Sombra (the Hat Man). Render type entityTranslucent; emissive layer 'eyes' = two 2x2 ember eyes on
the cranium front + one soft ember on the gullet wall and a faint one on the back of the tongue (only visible when
the jaw opens). He never runs: he glides, stops dead, and his limbs and cloth lag behind him like smoke.

BONES
- smoke_pool: flat smoke disc on the ground under him. Never inherits body motion; slow yRot drift (~0.2 rad/s)
  and a gentle scale-like breathing via tiny dy (+-0.3). Hide it while he is airborne/teleporting.
- right_leg / left_leg: hidden inside the coat, dissolve into smoke below the knee. Small shuffle only
  (xRot +-0.15 at walk speed, opposite phase); no stride - the coat panels sell the motion.
- body: waist, belt and the coat lining. Slow breathing sway (zRot +-0.03, 0.25 Hz); glide bob dy +-0.6.
  Carries every coat panel.
- coat_front_right / coat_front_left: inner front skirt panels. Lagging secondary sway (follow body velocity with
  ~6 ticks delay, xRot up to -0.35 when moving forward), plus constant smoke flutter (sin noise, +-0.04 rad,
  1.3 Hz, different phase per panel).
- coat_flare_right / coat_flare_left: front corner panels that kick out. Same lag as the fronts but 1.4x the
  amplitude and an extra outward zRot (+-0.12) when he turns.
- coat_side_right / coat_side_left: side panels (turned 90 deg about Y at rest - only ADD to their pose, keep
  the 90 deg yRot). Flutter zRot +-0.06 (stronger than the fronts, it is the widest part of the hem).
- coat_back_right / coat_back_left: back panels; trail backward with speed (xRot up to +0.5), flutter +-0.05.
- coat_trail: wide smoke sheet streaming from the vent. xRot grows with speed (rest +0.6 rad baked in, add up to
  +0.6); constant wavy flutter (zRot +-0.08, 0.9 Hz). The hem flutter gets stronger toward the bottom: drive
  trail > back > side > flare > front.
- chest: upper torso + hunch (12 deg baked in). Breathing xRot +-0.03 at 0.25 Hz; leans forward +0.15 while
  chasing; carries arms, collar, neck.
- hump: rounded back mass; follows the chest, tiny inverse breathing (-0.5x chest) so the back seems to swell.
- right_shoulder / left_shoulder: bevelled shoulder capes with epaulettes (turned 90 deg about Y - add only).
  Rise with the arm: dy -1.5 when that arm lifts above the shoulder; static otherwise.
- lapel_right / lapel_left: static, or lag 3 ticks behind the chest breathing.
- collar_back / collar_right / collar_left: popped collar hugging the skull. Static on the chest; when the
  head turns more than 0.4 rad, rotate the collar on that side 0.25x the head yaw so it does not clip.
- neck: slow tilt (zRot +-0.06, 0.15 Hz) plus the forward thrust in attack/scream.
- head: tracks the target with yaw/pitch clamped to +-0.9 / +-0.5; slow tilt, and sudden 'head-cock' twitches:
  every 3-8 s snap zRot by +-0.35 over 2 ticks, hold 10-30 ticks, ease back over 15 ticks. While the player
  stares at him, freeze everything except the head, which turns to keep facing the camera.
- jaw: closed at rest (the grin is painted). Opens in attack (1.05) and scream (1.25); while idle, a slow
  'tasting' twitch 0.05 every few seconds. Jaw xRot is the only thing that reveals the throat ember.
- hat: locked to the head with a tiny lag (1-2 ticks, +-0.05 rad) so the brim settles after head-cocks.
- hat_crown_right / hat_crown_left: crown side plates (turned 90 deg about Y). Static.
- hat_brim_front / hat_brim_back / hat_brim_left / hat_brim_right: brim edge; static, optional +-0.03 flutter
  when he glides fast (front/back opposite phase).
- right_arm / left_arm: impossibly long sleeves. Idle: dangle and swing past the knees like pendulums (xRot +-0.12,
  0.4 Hz, opposite phase, left arm 1.3x slower); chase: arms trail behind (xRot +0.35) and swing wider.
- right_forearm / left_forearm: secondary swing lagging the upper arm by ~4 ticks (xRot +-0.1).
- right_hand / left_hand: wrist flop following the forearm (lag ~3 ticks). The left wrist is twisted at rest
  (yRot 26 deg) - keep it for asymmetry.
- right_finger0..3 / left_finger0..3 (index -> pinky): idle drumming - each finger dips xRot +0.25 in turn,
  0.12 s apart, every 2-4 s; fan (zRot) opens +-0.3 when the hand reaches.
- right_finger0_tip..3_tip / left_finger0_tip..3_tip: curl xRot follows the finger (0.6x), extra slow curling
  +-0.15 so the fingers never look still.
- right_thumb / left_thumb: curls in with the fingers (zRot toward the palm +-0.2).

POSES (added to the rest pose; ease in over 4-6 ticks, hold, ease out)
- reach: one arm thrown at the viewer: torso yaws so the right shoulder comes forward, arm horizontal, wrist bent
  back so the open spider hand (fingers fanned +-0.6 rad, tips uncurled, thumb out) faces the camera, head tilted
  the other way. Trigger: player within 4 blocks but not looking at him, or the 'stalk' state ending next to the
  player; also the thumbnail/idle-at-distance flourish.
- attack: lunge - torso folds forward, chin up so the eyes stay clear of the brim, jaw unhinged 1.05, both claws
  forward and curled. Trigger: melee swing; the jumpscare portrait uses this jaw value.
- scream: shoulders hunch up, forearms fold so the claws frame the face, head thrust at the camera, jaw fully
  unhinged 1.25, brim tilted up so it frames the eyes. Trigger: jumpscare / when hit with light, before he
  dissolves and teleports.
"""
