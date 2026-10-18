"""El Hombre Sombra -- the Hat Man (DEAD LINE).

Authored at 2x texel density (model.scale = 0.5) with rig.Rig absolute coordinates:
+Y down, ground at y = 24, the creature faces -Z, right_* parts on -X.
Every cube is authored in its bone's *unrotated* frame relative to the bone pivot; bone rotations fold
the figure into its hunched, head-tilted stance.

Design: a pure black silhouette -- a huge snap-brim fedora, broad padded shoulders with a back yoke and a
popped collar, a belted trench coat whose skirt flares out in separate panels and dissolves into smoke
below the knees, and impossibly long sleeved arms ending in spider-leg fingers (three segments each).
Only deliberate dark blue / violet rim tones describe the volumes. Under the brim: two tiny burning
ember eyes and a needle-tooth grin that runs ear to ear; the jaw unhinges to show an ember-lit maw.
"""
import math

from mcmodel import Model, fbm, vnoise, hash3, face_light, pick
from rig import Rig
from paint import hx, mix, scale, edge


def pal(*h):
    return [hx(c) for c in h]


# ------------------------------------------------------------------ palettes (dark -> light)
SHADE = pal('#010102', '#040409', '#08080f', '#0d0c17', '#131121', '#1a172c', '#221e3a', '#2c264a', '#3a325e')
FELT = pal('#010102', '#050508', '#0a0910', '#100e19', '#171423', '#1f1b2f', '#28223c', '#332b4c')
BAND = pal('#050105', '#0c040b', '#140712', '#1e0b1a', '#2a1024', '#38172f')
SMOKE = pal('#08070c', '#100e17', '#191623', '#231f30', '#2e2940', '#3b3550', '#4a4362')
TOOTH = pal('#15121c', '#221e2b', '#322d3d', '#443e52', '#585168', '#6e677f', '#8a8399', '#a7a0b4')
MAW = pal('#050102', '#0e0203', '#190305', '#260509', '#36070c', '#4a0b10', '#601016')
GLOW = pal('#2a0204', '#4e0407', '#7e070a', '#b30d0e', '#e8231a', '#ff5a2a', '#ffb070', '#ffe8c0')
VOID = hx('#000000')


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
    lx, ly, lz = local(ctx)
    a = ctx.bone.abs
    return a[0] + lx, a[1] + ly, a[2] + lz


def is_side(ctx):
    return ctx.face not in ('top', 'bottom')


def flat(ctx):
    return 0 in ctx.cube.size


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


def clamp(v, a=0.0, b=1.0):
    return a if v < a else b if v > b else v


# ------------------------------------------------------------------ smoke dissolve
def fade(ctx, t, col, start, seed):
    """Ragged dissolve toward the bottom of a hanging part. Returns (alpha, k) or None (gone).

    t: 0..1 position along the hanging axis; col: integer column across it."""
    if t < start:
        return 1.0, 0.0
    strip = math.floor(col / 2)
    cut = start + (1.0 - start) * (0.45 + 0.55 * hash3(strip, 0, 0, seed))
    if hash3(strip, 1, 0, seed) < 0.18:
        cut = start + (cut - start) * 0.45  # torn-off strip
    if t >= cut:
        return None
    k = (t - start) / (cut - start)
    a = (1.0 - k) ** 0.9
    if hash3(col, math.floor(t * 40), 3, seed) < k * 0.35:
        a *= 0.55  # wispy holes
    return a, k


def smoky(c, v, a, k):
    """Blend a cloth colour into lighter translucent smoke as it dissolves."""
    s = pick(SMOKE, v + 0.18 + k * 0.12)
    c = mix(c, s, min(1.0, k * 1.6))
    alpha = int(clamp(a) * 255)
    if alpha < 18:
        return None
    return (c[0], c[1], c[2], alpha)


# ------------------------------------------------------------------ materials
def coat_value(ctx):
    v = form(ctx, 0.31)
    lx, ly, lz = local(ctx)
    fl = getattr(ctx.bone, 'flen', None)
    if fl and is_side(ctx) and not flat(ctx):
        # drape folds: meandering crease (dark) + ridge (lit) pairs that widen toward the hem
        col = lx if ctx.face in ('front', 'back') else lz
        t = ly / fl
        ph = getattr(ctx.bone, 'fseed', 0) * 0.37
        f = (col + ph) / 5.0 + 0.25 * math.sin(t * 5.0 + col * 0.4)
        period = math.floor(f)
        s = f - period
        if t > 0.06 + 0.35 * hash3(period, 0, 0, 77):
            if s < 0.2:
                v -= 0.09
            elif s < 0.4:
                v += 0.07
    return v


def coat_mat(ctx):
    """Heavy black gabardine: violet rims, drape folds, dissolving into smoke at the hem."""
    v = coat_value(ctx)
    c = pick(SHADE, v)
    fl = getattr(ctx.bone, 'flen', None)
    start = getattr(ctx.bone, 'smoke', None)
    if fl and start is not None:
        lx, ly, lz = local(ctx)
        if ctx.face == 'top':
            return c
        col = math.floor(lx if ctx.face in ('front', 'back', 'bottom') else lz + 40)
        r = fade(ctx, ly / fl, col, start, getattr(ctx.bone, 'fseed', 0) + 5)
        if r is None:
            return None
        return smoky(c, v, *r)
    return c


def lining_mat(ctx):
    """Inside of the coat: a void, barely any light gets in."""
    lx, ly, lz = local(ctx)
    v = 0.12 + face_light(ctx) * 0.3
    c = pick(SHADE, v)
    t = ly / 14.0
    if t > 0.5 and ctx.face != 'top':
        a = 1.0 - (t - 0.5) / 0.5
        return smoky(c, v, a, (t - 0.5) * 2)
    return c


def trouser_mat(ctx):
    v = form(ctx, 0.24)
    lx, ly, lz = local(ctx)
    if is_side(ctx) and math.floor(lx * 3 + lz * 5) % 7 == 0:
        v -= 0.05
    c = pick(SHADE, v)
    if ctx.face == 'top':
        return c
    col = math.floor(lx if ctx.face in ('front', 'back', 'bottom') else lz + 30)
    r = fade(ctx, ly / 37.0, col, 0.42, 61)
    if r is None:
        return None
    return smoky(c, v, *r)


def belt_mat(ctx):
    v = form(ctx, 0.36, rim=0.1)
    if is_side(ctx) and ctx.h >= 3 and ctx.j == 1 and ctx.i % 3 != 2:
        v -= 0.06  # stitch line
    return pick(SHADE, v)


def buckle_mat(ctx):
    v = form(ctx, 0.5, rim=0.15)
    if is_side(ctx) and 0 < ctx.i < ctx.w - 1 and 0 < ctx.j < ctx.h - 1:
        return pick(SHADE, 0.08)  # the hole of the buckle frame
    return pick(TOOTH, v - 0.25)


def button_mat(ctx):
    if ctx.face == 'front':
        if ctx.i == 0 and ctx.j == 0:
            return TOOTH[4]  # glint
        return SHADE[5] if (ctx.i + ctx.j) % 2 == 0 else SHADE[3]
    return pick(SHADE, 0.3)


def lapel_mat(ctx):
    """Lapels / collar: crisp pressed edge on the outer border, lit upper side."""
    v = form(ctx, 0.36, rim=0.1)
    if ctx.face == 'front' and not flat(ctx):
        if ctx.i == ctx.w - 1 or ctx.i == 0:
            v += 0.06
        if ctx.i == ctx.w - 2 or ctx.i == 1:
            v -= 0.06
    return pick(SHADE, v)


def chest_mat(ctx):
    """Torso of the coat; the V between the lapels is a pure void (nothing inside the coat)."""
    v = coat_value(ctx)
    lx, ly, lz = local(ctx)
    if ctx.face == 'front' and ctx.bone.name == 'chest':
        if abs(lx) < 1.5 + (ly + 17) * 0.33 and ly < -6:
            return pick(SHADE, 0.05)
        # seam lines of the double-breasted front
        if abs(abs(lx) - 7.5) < 0.5 and ly > -10:
            v -= 0.06
    if ctx.face == 'back' and abs(lx) < 0.5 and ly > -8:
        v -= 0.08  # centre back seam
    return pick(SHADE, v)


def felt_mat(ctx):
    """Hat felt: soft violet sheen on the crown top and brim edge, pitch black underside."""
    v = form(ctx, 0.33, rim=0.1)
    if ctx.face == 'bottom':
        return pick(FELT, 0.04)
    lx, ly, lz = local(ctx)
    if ctx.face == 'top':
        v += 0.04 * math.sin(lx * 0.5 + lz * 0.3)
    c = pick(FELT, v)
    return c


def crown_mat(ctx):
    v = form(ctx, 0.32, rim=0.1)
    if ctx.face == 'bottom':
        return pick(FELT, 0.04)
    lx, ly, lz = local(ctx)
    if is_side(ctx) and not flat(ctx):
        v -= ctx.t * 0.06  # darker toward the band
        if ctx.face == 'front' and ctx.i in (ctx.w // 2 - 1, ctx.w // 2):
            v -= 0.06  # front pinch
    if ctx.face == 'top' and ctx.cube.size[0] <= 7:
        # crease lobes: lit outer edge, shaded inner lip into the dent
        inner = (lx > 0 and ctx.i == 0) or (lx < 0 and ctx.i == ctx.w - 1)
        if inner:
            v -= 0.12
    return pick(FELT, v)


def band_mat(ctx):
    v = form(ctx, 0.42, rim=0.12)
    if ctx.face == 'bottom':
        return pick(BAND, 0.05)
    if is_side(ctx) and ctx.j == ctx.h - 1:
        v -= 0.1
    return pick(BAND, v)


def skin_mat(ctx):
    """Head / neck: void skin with violet sheen on cheekbones and brow (front painted by decals)."""
    v = form(ctx, 0.20, rim=0.09)
    lx, ly, lz = local(ctx)
    if ctx.face == 'bottom' and ctx.bone.name == 'head' and lz < -2:
        return maw_value(ctx, lx, lz)
    if ctx.face == 'front' and ctx.bone.name == 'head' and ctx.cube.size[2] <= 7:
        return pick(MAW, 0.1)  # throat (behind the jaw)
    return pick(SHADE, v)


def maw_value(ctx, lx, lz):
    """Palate / tongue bed: dark red ridges, black at the back."""
    v = 0.55 - (lz + 12) / 10 * 0.35
    if math.floor(lz) % 2 == 0 and abs(lx) < 6:
        v -= 0.12  # palate ridges
    if abs(lx) > 6.5:
        v -= 0.2
    return pick(MAW, v)


def jaw_mat(ctx):
    v = form(ctx, 0.20, rim=0.09)
    lx, ly, lz = local(ctx)
    if ctx.face == 'top':
        az = lz + ctx.bone.abs[2] - ctx.bone.head_z
        v = 0.5 - (az + 12) / 10 * 0.3
        if abs(lx) < 3.5:
            v += 0.12 if math.floor(az) % 3 else 0.0  # tongue
        if abs(lx) > 6.5:
            v -= 0.2
        return pick(MAW, v)
    return pick(SHADE, v)


def hand_mat(ctx):
    """Long void fingers: violet knuckle highlights, glossy grey-violet nails."""
    v = form(ctx, 0.27, rim=0.1)
    n = ctx.bone.name
    if is_side(ctx) and not flat(ctx):
        if ('finger' in n or 'thumb' in n) and ctx.j <= 1:
            v += 0.1  # knuckle
        if n.endswith('_hand') and ctx.face == 'front' and ctx.cube.size[1] >= 6 and ctx.i % 2 == 1:
            v += 0.06  # tendons on the back of the hand
    return pick(SHADE, v)


def nail_mat(ctx):
    v = 0.5 + face_light(ctx) * 1.2
    if is_side(ctx):
        v += 0.15 - ctx.t * 0.3
    return pick(TOOTH, v)


def teeth_mat(maxlen, seed, grow=1, axis='x'):
    """Needle teeth on a zero-thickness plane: 1-texel teeth with gaps, roots in dark gum.

    grow=1: roots at the plane's top (upper teeth); grow=-1: roots at the bottom (lower teeth)."""
    def f(ctx):
        lx, ly, lz = local(ctx)
        c = ctx.cube
        col = math.floor((lx if axis == 'x' else lz) * 1.0 + 0.01)
        depth = (ly - c.origin[1]) if grow > 0 else (c.origin[1] + c.size[1] - ly)
        if col % 2:
            return None if depth > 0.9 else MAW[2]
        h = hash3(col, 0, 0, seed)
        L = 1.4 + h * (maxlen - 1.4)
        if depth > L:
            return None
        if depth < 0.9:
            return MAW[3]
        tt = depth / L
        return pick(TOOTH, 0.85 - tt * 0.45 + face_light(ctx) * 0.4)
    return f


def smoke_mat(seed, start=0.0, strands=3.0):
    """Wisps of smoke on a zero-thickness plane: sinuous strands fading downward."""
    def f(ctx):
        lx, ly, lz = local(ctx)
        c = ctx.cube
        u = lx if c.size[0] > 0 else lz
        t = (ly - c.origin[1]) / max(1, c.size[1])
        best = None
        for k in range(-1, 2):
            sidx = math.floor(u / strands) + k
            phase = hash3(sidx, 0, 0, seed) * 6.28
            centre = (sidx + 0.5) * strands + 1.1 * math.sin(t * 5.5 + phase) * (0.3 + t)
            width = 0.55 + 0.5 * hash3(sidx, 1, 0, seed) * (1 - t)
            L = 0.35 + 0.65 * hash3(sidx, 2, 0, seed)
            if abs(u - centre) < width and t < L:
                a = (1 - t / L) ** 1.3 * (0.75 - start * 0.3)
                if best is None or a > best:
                    best = a
        if best is None:
            return None
        v = 0.42 - t * 0.2 + face_light(ctx) * 0.3
        col = pick(SMOKE, v)
        a = int(best * 255)
        if a < 18:
            return None
        return (col[0], col[1], col[2], a)
    return f


# ------------------------------------------------------------------ face decals
EYE_R = (4.0, 7.0)   # right eye (viewer's left) centre on the cranium front, in face texels
EYE_L = (11.0, 7.0)
SEAM = 15.0          # the head/jaw seam in combined face rows (cranium rows 0..14, jaw rows 15..)


def bite_row(i, w):
    """Row of the bite line of the grin (combined rows): a crescent rising toward both corners."""
    d = abs((i + 0.5) - w / 2) / (w / 2)
    return SEAM - 4.6 * d ** 1.8


def grin_cell(i, row, w, seed):
    """What the grin paints at combined (i, row): None / 'tooth' / 'gap' / 'lip' / 'lipl' / 'gum'."""
    b = bite_row(i, w)
    up = 1.6 + 1.2 * hash3(i, 0, 0, seed)
    lo = 1.3 + 1.0 * hash3(i, 1, 0, seed)
    y = row + 0.5
    if b - up <= y < b:
        return 'tooth' if i % 2 == 0 else 'gap'
    if b <= y < b + lo:
        return 'tooth' if i % 2 == 1 else 'gap'
    if b - up - 1 <= y < b - up:
        return 'lip'
    if b + lo <= y < b + lo + 1:
        return 'lipl'
    return None


GRIN_COL = {'tooth': TOOTH[5], 'gap': MAW[1], 'lip': VOID, 'lipl': SHADE[4]}


def face_front_decal(img, u0, v0, w, h):
    """Cranium front: shaded brow, deep sockets with ember eyes + glow spill, cheekbones, grin."""
    px = img.load()
    for j in range(h):
        for i in range(w):
            x, y = i + 0.5, j + 0.5
            c = None
            # under-brim shadow
            if j <= 4:
                c = SHADE[1]
            # brow ridges: sloping toward the centre (scowl)
            for (ex, ey), sgn in ((EYE_R, 1), (EYE_L, -1)):
                dx, dy = x - ex, y - ey
                browy = ey - 2.2 + sgn * dx * 0.28
                if abs(dx) < 3.2 and abs(y - browy) < 0.5:
                    c = SHADE[4] if abs(dx) < 2.2 else SHADE[3]
                # socket (slanted ellipse)
                a = math.radians(18 * sgn)
                uu = dx * math.cos(a) + dy * math.sin(a)
                vv = -dx * math.sin(a) + dy * math.cos(a)
                r = (uu / 2.7) ** 2 + (vv / 1.55) ** 2
                if r <= 1.0:
                    c = VOID
                elif r <= 1.9 and c is None:
                    c = mix(SHADE[2], GLOW[0], 0.55 * (1.9 - r))  # ember light spilling on the skin
            # cheekbones: lit ridge under the outer corner of each eye, sunken hollow below
            for ex, sgn in ((EYE_R[0], -1), (EYE_L[0], 1)):
                cx = ex + sgn * 1.5 - sgn * (y - 9.5) * 0.9
                if 9 <= j <= 11 and abs(x - cx) < 0.6:
                    c = SHADE[4]
                elif 9 <= j <= 12 and abs(x - (cx - sgn * 1.0)) < 0.6:
                    c = SHADE[1]
            if c is not None:
                px[u0 + i, v0 + j] = c
    # the eyes themselves (base layer: hot core so they read even without the glow pass)
    for (ex, ey) in (EYE_R, EYE_L):
        ix, iy = int(ex), int(ey)
        px[u0 + ix, v0 + iy] = GLOW[5]
        px[u0 + ix - 1, v0 + iy] = GLOW[3]
        px[u0 + ix + 1, v0 + iy] = GLOW[2]
    # the grin
    for j in range(h):
        for i in range(w):
            g = grin_cell(i, j, w, 401)
            if g:
                px[u0 + i, v0 + j] = GRIN_COL[g]


def eyes_glow_decal(img, u0, v0, w, h):
    """Emissive layer of the cranium front: ember eyes + faint red glow in the gaps of the grin."""
    px = img.load()
    for (ex, ey) in (EYE_R, EYE_L):
        ix, iy = int(ex), int(ey)
        px[u0 + ix, v0 + iy] = GLOW[7]
        px[u0 + ix - 1, v0 + iy] = GLOW[5]
        px[u0 + ix + 1, v0 + iy] = GLOW[4]
        for di, dj, k in ((-2, 0, 2), (2, 0, 2), (0, -1, 3), (0, 1, 3), (-1, -1, 1), (1, -1, 1), (-1, 1, 1), (1, 1, 1)):
            px[u0 + ix + di, v0 + iy + dj] = GLOW[k]
    for j in range(h):
        for i in range(w):
            if grin_cell(i, j, w, 401) == 'gap':
                px[u0 + i, v0 + j] = GLOW[0]


def jaw_front_decal(img, u0, v0, w, h):
    px = img.load()
    for j in range(h):
        for i in range(w):
            g = grin_cell(i, j + SEAM, w, 403)
            if g:
                px[u0 + i, v0 + j] = GRIN_COL[g]
            elif j >= 3 and (i in (w // 2 - 4, w // 2 + 3)) and j <= 4:
                px[u0 + i, v0 + j] = SHADE[1]  # chin creases


def jaw_glow_decal(img, u0, v0, w, h):
    px = img.load()
    for j in range(h):
        for i in range(w):
            if grin_cell(i, j + SEAM, w, 403) == 'gap':
                px[u0 + i, v0 + j] = GLOW[0]


def grin_side_decal(front_high):
    """Continue the grin around the side of the head toward the ear (a Glasgow smile)."""
    def fn(img, u0, v0, w, h):
        px = img.load()
        b0 = SEAM - 4.6
        for k in range(0, 8):
            i = (w - 1 - k) if front_high else k
            b = b0 - k * 0.55
            jj = int(b)
            if 0 <= jj < h:
                px[u0 + i, v0 + jj] = MAW[1] if k < 6 else SHADE[1]
                if k < 4:
                    if jj - 1 >= 0:
                        px[u0 + i, v0 + jj - 1] = TOOTH[4] if k % 2 == 0 else MAW[1]
                    if jj + 1 < h:
                        px[u0 + i, v0 + jj + 1] = TOOTH[3] if k % 2 == 1 else MAW[1]
                if jj - 2 >= 0 and k < 6:
                    px[u0 + i, v0 + jj - 2] = VOID
    return fn


def palate_glow_decal(img, u0, v0, w, h):
    """Emissive: embers smouldering deep in the palate (bottom face, front edge at high j)."""
    px = img.load()
    for j in range(h):
        for i in range(w):
            if j < h - 12 or i < 2 or i > w - 3:
                continue
            n = hash3(i // 2, j // 2, 0, 911)
            if n > 0.55 and (i + j) % 2 == 0:
                px[u0 + i, v0 + j] = GLOW[0] if n < 0.8 else GLOW[1]


def tongue_glow_decal(img, u0, v0, w, h):
    """Emissive: the throat end of the tongue bed glows (top face, front edge at low... high j)."""
    px = img.load()
    for j in range(h):
        for i in range(w):
            if i < 3 or i > w - 4:
                continue
            n = hash3(i // 2, j // 2, 1, 913)
            if n > 0.6 and (i + j) % 2 == 1:
                px[u0 + i, v0 + j] = GLOW[0] if n < 0.85 else GLOW[1]


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

    def box(b, frm, size, mat=None, inflate=0.0, decals=None, ref=None):
        a = r.abs_pivot[ref or b]
        return r.box(b, (a[0] + frm[0], a[1] + frm[1], a[2] + frm[2]), size, mat=mat, inflate=inflate, decals=decals)

    def mx(sx, frm, size):
        """Mirror a right-side (-X) box description to side sx (+1 = left)."""
        return frm if sx < 0 else (-(frm[0] + size[0]), frm[1], frm[2])

    def mbox(b, sx, frm, size, **kw):
        return box(b, mx(sx, frm, size), size, **kw)

    WAIST = -14.0

    # ---------------- legs (mostly hidden; dissolve into smoke)
    for side, sx in (('right', -1), ('left', 1)):
        leg = bone(f'{side}_leg', (5.0 * sx, WAIST, 1.0), rot=(0, 0, -2 * sx), mat=trouser_mat)
        box(leg.name, (-3.5, 0, -3.5), (7, 20, 7))
        box(leg.name, (-3, 19, -3), (6, 18, 6))

    # ---------------- body: waist, belt, coat lining
    bone('body', (0, WAIST, 1.0), mat=coat_mat)
    box('body', (-10.5, -16, -6.5), (21, 16, 13), mat=chest_mat)
    box('body', (-12, -2, -8.5), (24, 3, 17), mat=belt_mat)
    box('body', (-6.5, -3, -9.2), (5, 5, 1), mat=buckle_mat)
    box('body', (-9.5, 1, -5.5), (19, 14, 11), mat=lining_mat)

    # ---------------- coat skirt: five flaring panels dissolving into smoke
    FL = 34.0
    fr = bone('coat_front_right', at('body', -5.75, 0, -6.5), 'body', rot=(-7, 0, 7), flen=FL, smoke=0.5, fseed=1)
    box(fr.name, (-5.75, 0, -1), (12, int(FL), 2))
    box(fr.name, (-5.75, FL - 8, 0), (12, 14, 0), mat=smoke_mat(501))
    box(fr.name, (-4.5, 6, -1.6), (4, 2, 1), mat=lapel_mat)  # pocket flap
    fl = bone('coat_front_left', at('body', 5.75, 0, -7.1), 'body', rot=(-7, 0, -7), flen=FL, smoke=0.5, fseed=2)
    box(fl.name, (-6.25, 0, -1), (12, int(FL), 2))
    box(fl.name, (-6.25, FL - 8, 0), (12, 14, 0), mat=smoke_mat(503))
    box(fl.name, (0.5, 6, -1.6), (4, 2, 1), mat=lapel_mat)
    box(fl.name, (-5.5, 1, -1.5), (3, 10, 0), mat=coat_mat)  # hanging belt tail
    for side, sx in (('right', -1), ('left', 1)):
        sd = bone(f'coat_side_{side}', at('body', 10.3 * sx, 0, 0.5), 'body', rot=(0, 0, -12 * sx), flen=FL - 3,
                  smoke=0.45, fseed=3 + sx)
        mbox(sd.name, sx, (-1, 0, -6.5), (2, int(FL - 3), 13))
        mbox(sd.name, sx, (0, FL - 10, -6), (0, 14, 12), mat=smoke_mat(505 + sx))
    bk = bone('coat_back', at('body', 0, 0, 6.5), 'body', rot=(13, 0, 0), flen=FL + 4, smoke=0.5, fseed=6)
    box(bk.name, (-11.5, 0, -1), (23, int(FL + 4), 2))
    box(bk.name, (-11.5, FL - 4, 0), (23, 16, 0), mat=smoke_mat(509))

    # ---------------- chest: hunched, broad padded shoulders, yoke, lapels, popped collar
    CH = 14
    bone('chest', at('body', 0, -15, 0.5), 'body', rot=(CH, 0, 0), mat=coat_mat)
    box('chest', (-12, -17, -7), (24, 17, 13), mat=chest_mat)
    box('chest', (-15, -18, -7.5), (30, 5, 14))
    box('chest', (-14, -18.5, 1), (28, 11, 6))
    for k, yy in enumerate((-9, -5, -1)):
        for sx in (-1, 1):
            box('chest', (4.5 * sx - 1, yy, -8), (2, 2, 1), mat=button_mat)
    for side, sx in (('right', -1), ('left', 1)):
        lp = bone(f'lapel_{side}', at('chest', 5.5 * sx, -16.5, -7), 'chest', rot=(0, 0, 18 * sx), mat=lapel_mat)
        mbox(lp.name, sx, (-3, 0, -1.5), (5, 12, 2))
        cl = bone(f'collar_{side}', at('chest', 6.5 * sx, -17.5, -1.5), 'chest', rot=(-6, 0, 14 * sx), mat=lapel_mat)
        mbox(cl.name, sx, (-1, -11, -6), (2, 11, 11))
    cb = bone('collar_back', at('chest', 0, -17.5, 4), 'chest', rot=(-16, 0, 0), mat=lapel_mat)
    box(cb.name, (-7.5, -12, -1), (15, 12, 2))

    # ---------------- neck + head
    bone('neck', at('chest', 0, -17, -1), 'chest', rot=(24, 0, 0), mat=skin_mat)
    box('neck', (-3, -11, -3), (6, 12, 6))
    bone('head', at('neck', 0, -10, 0), 'neck', rot=(-34, 0, 16), mat=skin_mat)
    box('head', (-8, -20, -12), (16, 15, 16), decals={
        'front': face_front_decal, 'eyes:front': eyes_glow_decal,
        'west': grin_side_decal(True), 'east': grin_side_decal(False),
        'eyes:bottom': palate_glow_decal})
    box('head', (-6, -6, -3), (12, 7, 6))
    # upper needle teeth hanging from the palate (hidden inside the jaw while it is shut)
    box('head', (-7.5, -5, -11.6), (15, 3, 0), mat=teeth_mat(3.0, 421, 1))
    for sx in (-1, 1):
        box('head', (7.6 * sx, -5, -11), (0, 2, 9), mat=teeth_mat(2.0, 423 + sx, 1, axis='z'))

    hz = r.abs_pivot['head'][2]
    bone('jaw', at('head', 0, -5.5, -1), 'head', rot=(0, 0, 0), mat=jaw_mat, head_z=hz)
    box('jaw', (-8.5, -5, -12.5), (17, 6, 11), ref='head', decals={
        'front': jaw_front_decal, 'eyes:front': jaw_glow_decal, 'eyes:top': tongue_glow_decal})
    box('jaw', (-3.5, 1, -12), (7, 3, 6), ref='head')
    box('jaw', (-2, 4, -11), (4, 2, 4), ref='head')
    box('jaw', (-7.5, -8, -11.9), (15, 3, 0), mat=teeth_mat(3.0, 431, -1), ref='head')
    for sx in (-1, 1):
        box('jaw', (7.9 * sx, -7, -11.5), (0, 2, 9), mat=teeth_mat(2.0, 433 + sx, -1, axis='z'), ref='head')

    # ---------------- hat: wide snap brim, pinched crown, plum band
    bone('hat', at('head', 0, -17, -4), 'head', rot=(5, 0, -4), mat=felt_mat)
    box('hat', (-20, -1, -11), (40, 2, 22))
    box('hat', (-9, -12, -9), (18, 11, 18), mat=crown_mat)
    box('hat', (-8, -15, -8), (16, 3, 16), mat=crown_mat)
    box('hat', (-8, -17, -7), (6, 2, 14), mat=crown_mat)
    box('hat', (2, -17, -7), (6, 2, 14), mat=crown_mat)
    box('hat', (-9.5, -4, -9.5), (19, 3, 19), mat=band_mat)
    bone('hat_brim_front', at('hat', 0, 0, -11), 'hat', rot=(12, 0, 0), mat=felt_mat)
    box('hat_brim_front', (-17, -1, -5), (34, 2, 5))
    box('hat_brim_front', (-12, -1, -8), (24, 2, 3))
    bone('hat_brim_back', at('hat', 0, 0, 11), 'hat', rot=(16, 0, 0), mat=felt_mat)
    box('hat_brim_back', (-17, -1, 0), (34, 2, 5))
    box('hat_brim_back', (-12, -1, 5), (24, 2, 3))

    # ---------------- arms: impossibly long sleeves, spider hands
    ARM = {
        # side: (arm rot, forearm rot, hand rot, curl per finger)
        'right': ((-CH - 4, 0, 5), (7, 0, -2), (6, 0, 0), (12, 16, 20, 24)),
        'left': ((-CH - 12, 0, -4), (-24, 0, 3), (14, 0, 4), (34, 40, 44, 48)),
    }
    for side, sx in (('right', -1), ('left', 1)):
        arot, frot, hrot, curls = ARM[side]
        arm = bone(f'{side}_arm', at('chest', 15 * sx, -15, 0), 'chest', rot=arot, mat=coat_mat, flen=None)
        box(arm.name, (-4.5, -3.5, -4.5), (9, 7, 9))
        box(arm.name, (-3, 3, -3), (6, 20, 6))
        fa = bone(f'{side}_forearm', at(arm.name, 0, 22, 0), arm.name, rot=frot, mat=coat_mat)
        box(fa.name, (-2.5, -1, -2.5), (5, 16, 5))
        box(fa.name, (-3, 14, -3), (6, 5, 6), mat=lapel_mat)
        hd = bone(f'{side}_hand', at(fa.name, 0, 18, 0), fa.name, rot=hrot, mat=hand_mat)
        box(hd.name, (-1.5, -1, -1.5), (3, 3, 3))
        box(hd.name, (-4, 1, -1), (8, 6, 2))
        box(hd.name, (-4, 6, -1.5), (8, 2, 3))
        # fingers from the thumb side (inner, -sx) to the pinky (outer, +... sx)
        lens = ((7, 6, 3), (8, 7, 4), (8, 6, 3), (6, 5, 3))
        fan = (-6, 1, 6, 12)
        for k in range(4):
            xc = (3 - 2 * k) * -sx  # index at the inner side
            p, m, c = lens[k]
            fg = bone(f'{side}_finger{k}', at(hd.name, xc, 7.5, 0), hd.name, rot=(4, 0, -fan[k] * sx), mat=hand_mat)
            box(fg.name, (-1, 0, -1), (2, p, 2))
            tp = bone(f'{side}_finger{k}_tip', at(fg.name, 0, p, 0), fg.name, rot=(curls[k], 0, 0), mat=hand_mat)
            box(tp.name, (-1, 0, -1), (2, m, 2))
            box(tp.name, (-0.5, m, -0.5), (1, c, 1), mat=nail_mat)
        th = bone(f'{side}_thumb', at(hd.name, 4.0 * -sx, 2.5, -0.5), hd.name, rot=(-10, 0, 28 * sx), mat=hand_mat)
        box(th.name, (-1, 0, -1), (2, 6, 2))
        box(th.name, (-0.5, 6, -0.5), (1, 3, 1), mat=nail_mat)

    m = Model('sombra', 256, 256, r.roots)
    m.scale = 0.5
    m.render_type = 'entityTranslucent'
    return m


DEFAULT_MAT = coat_mat
FOCUS = 'head'

POSES = {
    # one arm thrown toward the viewer, fingers splayed, head cocked further
    'reach': {
        'chest': (0.12, 0, 0, 0, 0, 0),
        'head': (0, 0, 0.25, 0, 0, 0),
        'right_arm': (-1.35, 0.0, -0.1, 0, 0, 0),
        'right_forearm': (-0.05, 0, 0, 0, 0, 0),
        'right_hand': (-0.9, 0, 0, 0, 0, 0),
        'right_finger0': (0, 0, 0.3, 0, 0, 0),
        'right_finger1': (0, 0, 0.1, 0, 0, 0),
        'right_finger2': (0, 0, -0.1, 0, 0, 0),
        'right_finger3': (0, 0, -0.3, 0, 0, 0),
    },
    'attack': {
        'chest': (0.3, 0, 0, 0, 0, 0),
        'neck': (0.2, 0, 0, 0, 0, 0),
        'head': (-0.3, 0, 0, 0, 0, 0),
        'jaw': (0.95, 0, 0, 0, 0, 0),
        'right_arm': (-1.3, 0, 0.3, 0, 0, 0),
        'left_arm': (-1.1, 0, -0.3, 0, 0, 0),
        'left_forearm': (0.3, 0, 0, 0, 0, 0),
    },
    'scream': {
        'chest': (-0.15, 0, 0, 0, 0, 0),
        'neck': (-0.3, 0, 0, 0, 0, 0),
        'head': (-0.5, 0, -0.25, 0, 0, 0),
        'jaw': (1.2, 0, 0, 0, 0, 0),
        'right_arm': (-0.3, 0, 1.0, 0, 0, 0),
        'left_arm': (-0.1, 0, -1.0, 0, 0, 0),
        'left_forearm': (0.3, 0, 0, 0, 0, 0),
    },
}

ANIM_NOTES = """placeholder"""
