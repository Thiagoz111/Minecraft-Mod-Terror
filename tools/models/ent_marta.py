"""Marta Morales (42) -- the mum of the Casa Morales, comic guide, NEVER possessed (DEAD LINE, case 'casa').

(design notes: see DESIGN below; the animation contract is ANIM_NOTES at the end of the file)
"""
import math
import os
import sys

import numpy as np

from mcmodel import Model, hash3, face_light, pick, rot_matrix
from rig import Rig
from paint import hx, mix


def H(*cs):
    return [hx(c) for c in cs]


def A(c, a=255):
    return (c[0], c[1], c[2], int(a))


# ------------------------------------------------------------------ palettes (dark -> light, hue shifted)
ROBE = H('#4a1640', '#6b2258', '#8d3270', '#ae4787', '#c9619c', '#de7fb0', '#ec9cc3', '#f5b9d5', '#fbd3e4',
         '#fee9f1')
TRIM = H('#2c0420', '#4e0a36', '#74124e', '#981e64', '#b82d78', '#d4468e', '#ea68a8', '#f692c2')
CURL = H('#2a0218', '#4c052c', '#740a44', '#9c0f5a', '#c41870', '#e02a84', '#f4529e', '#ff86bc', '#ffc2dc')
SKIN = H('#3b1f1a', '#5c2f26', '#7f4334', '#a05a45', '#bb7459', '#d08e6f', '#e0a787', '#ebbe9f', '#f4d4bb',
         '#fbe8d8')
HAIR = H('#140808', '#221010', '#331611', '#461d16', '#5c271c', '#743423', '#8e442e', '#a85a3c')
CREAM = H('#c9c0b2', '#dcd6cc', '#ebe7df', '#f6f7f3', '#ffffff')
NIGHTIE = H('#6c5a62', '#968088', '#bca8ac', '#d9cbc8', '#ece3dd', '#f7f1ea')
FLOWER = H('#6a4c9c', '#8a6cc0', '#b49ae0')
LEAF = H('#4f7a4c', '#6f9a6a')
GOLD = H('#4a300a', '#7a5414', '#a8791f', '#d1a334', '#ecc85a', '#fbe6a0')
CASE = H('#04232a', '#08363f', '#0f4c56', '#18646e', '#25808a', '#3a9ea6', '#5fbcc0', '#94dcd8')
DOG = H('#1e0a05', '#2e1208', '#42190b', '#57210e', '#6c2b13', '#823719', '#984421', '#ad532b', '#c06636')
FUZZ = H('#8a7660', '#b49c80', '#d6c2a4', '#ecdcc0', '#f8eedc', '#fffaf0')
SOLE = H('#4a3e32', '#6e5e4c', '#958268', '#b8a488', '#d8c8ac', '#ece2cc')
CHORI = H('#2a0a06', '#44120a', '#5e190e', '#782314', '#90301b', '#a84026', '#bc5432')
FAT = H('#d9b9a4', '#f3e2d0')
TWINE = H('#7a6644', '#b8a47a', '#e2d4ae')
BREAD = H('#4a250c', '#74401a', '#9e5f2a', '#c27e3c', '#d99c56', '#ebbd7c', '#f6daa6')
LIP = H('#6a2434', '#8e3646', '#b04e5c', '#c86a74', '#de8a90')
NAIL = H('#7a1020', '#a81c30', '#d03448', '#f0687a')
MOUTH = H('#1a0608', '#2e0c10', '#4a1820', '#6e2a34', '#9a4450')
TEETH = H('#8c8478', '#bdb5a6', '#e2dccf', '#f8f4ec')
SCLERA = hx('#f8f3ee')
SCLERA2 = hx('#d9cbc6')
IRIS = hx('#7a4a22')
IRIS2 = hx('#a8703a')
PUPIL = hx('#180a06')
LASH = hx('#1e0c0c')
GLINT = hx('#ffffff')
INK = hx('#120c0c')
BEZEL = H('#060608', '#101116', '#1c1e26')
SCREEN = {'bg': hx('#efe8dc'), 'head': hx('#167a6e'), 'in': hx('#ffffff'), 'out': hx('#bdeca6'),
          'dot': hx('#e8384a'), 'bar': hx('#d4ccbf'), 'logo': hx('#ffffff')}
LED = hx('#5dff9c')


# ------------------------------------------------------------------ geometry helpers
def local(ctx):
    """Texel centre in cube-local texel units (independent of bone rotation and face)."""
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
    """Authored (rest, unrotated) absolute position of the texel centre."""
    lx, ly, lz = local(ctx)
    c = ctx.cube
    return c.ax + lx, c.ay + ly, c.az + lz


def around(ctx):
    """Continuous horizontal coordinate wrapping round a cube (front -> east -> back -> west)."""
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    f = ctx.face
    if f == 'front':
        return lx
    if f == 'east':
        return w + lz
    if f == 'back':
        return w + d + (w - lx)
    if f == 'west':
        return 2 * w + d + (d - lz)
    return lx


def corner_dist(ctx):
    w, h, d = ctx.cube.size
    u = around(ctx)
    return min(abs(u - c) for c in (0, w, w + d, 2 * w + d, 2 * (w + d)))


def h2(a, b, s=0):
    return hash3(a, b, 0, s)


def nm(ctx):
    return ctx.cube.name


SIDE = ('front', 'back', 'west', 'east')


# ------------------------------------------------------------------ fleece
def nub(ctx, amt=0.1):
    """Coral-fleece micro pattern: every 2 x 2 nub on a brick grid has a lit top-left texel and a shaded
    bottom-right one.  Returns -1, 0 or +1 (the caller blends HALF a ramp step that way: soft and regular)."""
    i, j = ctx.i, ctx.j
    ii = (i + 2 * ((j // 2) % 2)) % 4
    jj = j % 2
    if ii == 0 and jj == 0:
        return 1
    if ii == 1 and jj == 1:
        return -1
    return 0


def tone(ramp, v, k=0, amt=0.45):
    """Ramp colour for value v, blended part of the way to the neighbouring tone for a fleece nub (k = +-1)."""
    v = max(0.0, min(0.999, v))
    n = len(ramp)
    i = int(v * n)
    c = ramp[i]
    if k:
        c = mix(c, ramp[max(0, min(n - 1, i + k))], amt if k > 0 else amt * 0.7)
    return A(c)


LAPEL_ROT = 22          # deg, the shawl collar's lapels close into a V at the belt
SKIRT_FLARE = 3         # deg, the wrap skirt panels open out to the hem
TOES_OUT = 8            # deg, duck stance in the dog slippers
BROW_WORRY = 16         # deg, inner ends of the brows raised at rest (she is always worried)
_SA, _CA = math.sin(math.radians(LAPEL_ROT)), math.cos(math.radians(LAPEL_ROT))


def lapel_edge(y, dx):
    """|x| of a lapel's long edge at height y (dx = +1.5 outer edge, -1.5 inner edge)."""
    dy = (y + 13.0 - dx * _SA) / _CA
    return 6.5 + dx * _CA - dy * _SA


def hood_bottom(x):
    """y of the hood's rounded point at column x (the hood hangs to y -2 at the centre)."""
    return -2.0 - max(0.0, (abs(x) - 0.5) / 1.6)


def robe_mat(ctx):
    f = ctx.face
    n = nm(ctx)
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    x, y, z = apos(ctx)
    side = f in SIDE
    v = 0.62 + face_light(ctx)
    k = nub(ctx) if (side or f == 'top') else 0
    if side and min(w, d) > 2 and n not in ('lapel', 'hood') and corner_dist(ctx) < 1.0:
        v -= 0.05                                                 # soft rounding at the box corners
    if n == 'torso':
        if f == 'front':
            nv = vneck(ctx, x, y)
            if nv is not None:
                return nv
            if y < -11.0:
                v -= 0.14                                         # under the shawl collar's shoulder rolls
            xo = lapel_edge(y, 1.5)
            if 0.0 <= abs(x) - xo < 1.3:
                v -= 0.14                                         # cast shadow of the collar roll
        elif f in ('west', 'east'):
            if abs(z) < 4.0 and y > -11.0:
                v -= 0.14                                         # armpit: the sleeve hangs right here
            if abs(z + 4.5) < 0.5 or abs(z - 4.5) < 0.5:
                v -= 0.1                                          # side drape folds
            elif abs(z + 3.5) < 0.5 or abs(z - 5.5) < 0.5:
                v += 0.04
        elif f == 'back':
            if abs(x) < 7.5 and abs(x) > 6.4:
                v -= 0.14                                         # shadow beside the hood
            for fx in (-8.5, 8.5):
                if abs(x - fx) < 0.5:
                    v -= 0.1                                      # drape folds
                elif abs(x - fx - 1.0) < 0.5:
                    v += 0.05
            if y < -11.0:
                v -= 0.08
        elif f == 'bottom':
            return A(pick(ROBE, 0.3))
    if n == 'bust':
        if f == 'front':
            nv = vneck(ctx, x, y)
            if nv is not None:
                return nv
            xo = lapel_edge(y, 1.5)
            if 0.0 <= abs(x) - xo < 1.3:
                v -= 0.14
            if ly < 1.0:
                v += 0.06
            elif ly > h - 1.0:
                v -= 0.08                                         # the bust curves under
        elif f == 'bottom':
            return A(pick(ROBE, 0.22))                            # deep shadow under the bust shelf
        elif f == 'top':
            v += 0.04
        elif f in ('west', 'east'):
            v -= 0.06
    if n == 'waist':
        if f == 'front':
            nv = vneck(ctx, x, y)
            if nv is not None:
                return nv
            v -= 0.16                                             # under the bust shelf
        elif side:
            v -= 0.05
            ph = (around(ctx) * 0.9 + ly * 0.5) % 4.0
            if ph < 0.9:
                v -= 0.08                                         # gathered fleece above the belt
            if f == 'back' and y < hood_bottom(x) + 1.6 and abs(x) < 6.6:
                v -= 0.16                                         # shadow under the hood's point
    if n == 'skirt':
        if f == 'bottom':
            return A(pick(ROBE, 0.24))                            # the inside of the robe
        if f == 'top':
            return A(pick(ROBE, 0.3))
        if side:
            v += skirt_folds(ctx)
            if ly < 1.5:
                v -= 0.15                                         # the belt's shadow
            elif ly < 2.5:
                v -= 0.06
            v -= ly / h * 0.05
            v += pocket(ctx, lx, ly, f)
            sx = ctx.cube.sx
            if sx > 0 and f == 'front' and lx < 2.0:
                v += 0.1 if lx < 1.0 else 0.05                    # the wrap's facing (left panel over the right)
            if sx < 0 and f == 'front' and lx > w - 3.0:
                v -= 0.15                                         # shadow under the overlapping panel
    if n in ('sleeve_up', 'sleeve_lo'):
        if f in ('top', 'bottom'):
            return A(pick(ROBE, 0.32))
        sx = ctx.cube.sx
        inner = (f == 'east') if sx < 0 else (f == 'west')
        if inner:
            v -= 0.12                                             # the side against the body
        if n == 'sleeve_up':
            if ly < 1.0:
                v += 0.05
            elif ly < 2.0:
                v -= 0.08                                         # dropped-shoulder seam
            if ly > h - 3.0 and f == 'front':
                c = abs(lx - w / 2)
                if abs(c - (h - ly) * 0.9 - 0.4) < 0.5:
                    v -= 0.12                                     # elbow crease, a soft V
        else:
            if 3.5 < ly < 4.5 and (int(around(ctx)) % 5) != 2:
                v -= 0.1                                          # wrist fold above the cuff
            if 2.5 < ly < 3.5 and (int(around(ctx)) % 5) in (0, 1):
                v += 0.04
    if n == 'cuff':
        if f == 'bottom':
            cx, cz = abs(lx - w / 2), abs(lz - d / 2)
            return A(ROBE[1] if max(cx, cz) < 2.6 else ROBE[4])
        if f == 'top':
            return A(pick(ROBE, 0.72))
        if side:
            v += 0.06
            if ly < 1.0:
                return A(pick(TRIM, 0.62 + face_light(ctx)))       # raspberry piping on the turn-back
            elif ly < 2.0:
                v -= 0.1                                          # under the turn-back roll
    if n == 'lapel':
        v += 0.12
        sx = ctx.cube.sx
        if f in ('west', 'east'):
            inner = (f == 'east') if sx < 0 else (f == 'west')
            if not inner:
                return A(pick(TRIM, 0.55 + face_light(ctx)))       # raspberry piping on the outer edge
            v += 0.02
        if f == 'front':
            outer_col = 0 if sx < 0 else ctx.w - 1
            inner_col = ctx.w - 1 - outer_col
            if ctx.i == outer_col:
                return A(pick(TRIM, 0.62))
            if ctx.i == inner_col:
                v += 0.08
        if f == 'top':
            v += 0.05
    if n in ('collar_back', 'collar_side'):
        v += 0.08
        if f == 'top':
            v += 0.04
        elif side and ctx.j == ctx.h - 1:
            v -= 0.12
        elif side and ctx.j == 0:
            v += 0.04
    if n == 'hood':
        cut = y > hood_bottom(x) + 0.5
        if f in ('front', 'back'):
            if cut:
                return None
            if f == 'front':
                return A(pick(ROBE, 0.3))
            if y < -10.0:
                return A(pick(ROBE, 0.28))                        # the crease under the collar roll
            if y < -9.0:
                v += 0.06                                         # the rolled rim of the hood
            if abs(x) < 0.5 and y > -8.0:
                v -= 0.1                                          # centre seam
            if y > hood_bottom(x) - 0.5:
                v += 0.08                                         # the lit rolled edge
            elif abs(x) > 5.5:
                v += 0.04
        elif f in ('west', 'east'):
            if cut:
                return None
            v -= 0.06
        else:
            return A(pick(ROBE, 0.3))
    return tone(ROBE, v, k)


SKIRT_FOLD_U = {'R': (13.5, 17.5, 22.0), 'L': (9.5, 16.0, 22.5), 'B': (4.0, 10.5, 17.0, 31.0, 38.0)}


def skirt_folds(ctx):
    """Two to five deliberate vertical folds per panel (valley + lit ridge), fading out under the belt."""
    lx, ly, lz = local(ctx)
    sx = ctx.cube.sx
    key = 'R' if sx < 0 else ('L' if sx > 0 else 'B')
    u = around(ctx)
    out = 0.0
    if ly < 2.0:
        return 0.0
    k = min(1.0, (ly - 2.0) / 3.0)
    for uf in SKIRT_FOLD_U[key]:
        du = u - uf
        if 0.0 <= du < 1.0:
            out -= 0.11 * k
        elif -1.0 <= du < 0.0:
            out += 0.05 * k
    return out


def pocket(ctx, lx, ly, f):
    """Patch pocket on the front of each front panel: dark opening, lit hem, seam outline.  -> value offset."""
    if f != 'front':
        return 0.0
    sx = ctx.cube.sx
    w = ctx.cube.size[0]
    px0 = 2.0 if sx < 0 else w - 7.0
    px1 = px0 + 5.0
    py0, py1 = 3.0, 8.0
    if not (px0 - 1.0 <= lx < px1 + 1.0 and py0 <= ly < py1 + 1.0):
        return 0.0
    if not (px0 <= lx < px1 and ly < py1):
        return -0.06                                              # the pocket's shadow on the panel
    if ly < py0 + 1.0:
        return -0.2                                               # the opening
    if ly < py0 + 2.0:
        return 0.08                                               # turned-down pocket hem
    if lx < px0 + 1.0 or lx >= px1 - 1.0:
        return -0.03
    return 0.03


def vneck(ctx, x, y):
    """Inside the V of the robe: skin + gold chain above the nightgown's lace neckline, cream cotton below."""
    half = lapel_edge(y, -1.5)
    if abs(x) > half - 0.2:
        return None
    if y < -9.5:
        c = pick(SKIN, 0.68 + (y + 9.5) * 0.03)
        ax = abs(x)
        if abs(y - (-12.3 + ax * 0.55)) < 0.5 and ax < 3.5:
            c = GOLD[4] if x < 0 else GOLD[3]                     # chain
        if abs(x) < 0.6 and -11.0 < y < -9.5:
            c = GOLD[4] if y < -10 else GOLD[2]                   # the little medal
        if abs(x) > half - 1.2:
            c = mix(c, SKIN[3], 0.35)                             # the collar's shadow on the skin
        return A(c)
    if y < -8.5:
        return A(NIGHTIE[5] if int(x + 20) % 2 == 0 else NIGHTIE[3])     # lace edge
    v = 0.66 - (y + 8.5) * 0.02
    if abs(x) > half - 1.2:
        v -= 0.15
    c = pick(NIGHTIE, v)
    gx, gy = int(math.floor(x + 30)), int(math.floor(y + 30))
    if (gx + 2 * gy) % 5 == 0 and gy % 2 == 0:
        c = FLOWER[1]
    elif (gx + 2 * gy) % 5 == 1 and gy % 2 == 0:
        c = LEAF[1]
    return A(c)


def fluff_mat(ctx):
    """Fringe shells round the cuffs, the collar and the hem: 1-2 rows of irregular fleece tufts with cut-out
    gaps, so the outline of the robe is soft instead of a box edge."""
    f = ctx.face
    if f not in SIDE:
        return None
    c = ctx.cube
    rows = c.size[1]
    k = ctx.j if c.grow == 'down' else rows - 1 - ctx.j          # 0 = the row attached to the robe
    u = int(math.floor(around(ctx))) + c.seed * 5
    hh = h2(u, k, 77)
    if rows == 1 or k == rows - 1:
        # the tips: runs of 1-2 tufts, then a gap
        if u % 3 == 2 or (u % 3 == 0 and hh < 0.3):
            return None
    elif hh < 0.12:
        return None
    base = c.tone if hasattr(c, 'tone') else 0.7
    v = base + face_light(ctx) * 0.6
    if k == rows - 1 and rows > 1:
        v += 0.04
    return tone(ROBE, v, 1 if (u + k) % 2 == 0 else 0)


def belt_mat(ctx):
    """The belt, the knot and its tails in a deeper raspberry than the robe: the waist reads from 10 blocks."""
    f = ctx.face
    n = nm(ctx)
    lx, ly, lz = local(ctx)
    v = 0.52 + face_light(ctx) * 1.0
    if n == 'belt':
        if f in SIDE:
            if ctx.j == 0:
                v += 0.14
            elif ctx.j == ctx.h - 1:
                v -= 0.12
            if f in ('west', 'east') and 2.0 < lz < 3.5:
                v += 0.12                                         # belt loop
        else:
            return A(pick(TRIM, 0.3))
    if n == 'knot':
        if f == 'front':
            if ctx.i in (0, ctx.w - 1):
                v -= 0.12
            if ctx.j == 1 and 0 < ctx.i < ctx.w - 1:
                v -= 0.14                                         # the cinch of the knot
            if ctx.j == 0:
                v += 0.12
        elif f == 'top':
            v += 0.06
    if n == 'tail' and f in SIDE:
        hgt = ctx.cube.size[1]
        if hgt - ly < 1.0:
            if h2(ctx.i, 0, 9) > 0.55:
                return None                                       # frayed fleece end
            v += 0.1
        if ctx.i == 0 and f == 'front':
            v += 0.08
        if ly < 1.0:
            v -= 0.1                                              # shadow under the knot
    return A(pick(TRIM, v))


# ------------------------------------------------------------------ hair + rollers
def hair_mat(ctx):
    """Dark mahogany hair combed UP into the rollers: strand columns with 2-texel lit segments, dark partings,
    a warm sheen band, deep occlusion under the rollers, wispy ends at the nape, a fringe framing the temples."""
    f = ctx.face
    n = nm(ctx)
    if n == 'brow':
        return brow_paint(ctx)
    if n == 'curl':
        return curl_paint(ctx)
    x, y, z = apos(ctx)
    if f == 'bottom':
        return None
    if f == 'front':
        if abs(x) < 7.4:
            if y > -29.3:
                return None
        elif y > -26.0 + (0.6 if abs(x) > 8.0 else 0.0):
            return None
    if f in ('west', 'east'):
        if y > -23.6 and z < 3.0:
            return None                                           # the face / ear show below the temples
        if y > -19.0:
            return None
    if f == 'back':
        if y > -18.5:
            return None
        if y > -20.0 and h2(int(math.floor(x + 30)), 3, 13) > 0.55:
            return None                                           # wispy nape hairs
    u = x if f in ('front', 'back', 'top') else z
    along = z if f == 'top' else y
    col = int(math.floor(u + 40))
    hs = h2(col, 0, 11)
    v = 0.42 + face_light(ctx) * 0.8 + (hs - 0.5) * 0.16
    if int(math.floor(along + hs * 7)) % 5 == 0:
        v += 0.12                                                 # lit strand segment
    if col % 4 == 0:
        v -= 0.08                                                 # dark parting between strand groups
    if f in SIDE and -28.0 < y < -25.5:
        v += 0.07                                                 # sheen band
    if f in SIDE and y < -29.4:
        v -= 0.16                                                 # occlusion under the rollers
    if f == 'back' and y > -21.0:
        v -= 0.06
    if f == 'top':
        v -= 0.12
    return A(pick(HAIR, v))


# right brow (front face, col 0 = the outer tail out by the temple, col 5 = the inner end): the inner end is the
# high, thick point; the tail drops toward the temple -- worried by construction, not only by the bone tilt
BROW_ART = [
    "..bBBB",
    "bBb...",
]


def brow_paint(ctx):
    f = ctx.face
    if f == 'back':
        return None
    sx = ctx.cube.sx
    w = ctx.cube.size[0]
    if f == 'front':
        i = ctx.i if sx < 0 else w - 1 - ctx.i
        ch = BROW_ART[min(ctx.j, 1)][min(i, 5)]
        if ch == '.':
            return None
        return A(HAIR[1] if ch == 'B' else HAIR[3])
    if f in ('top', 'bottom'):
        i = ctx.i if sx < 0 else w - 1 - ctx.i
        row = 0 if f == 'top' else 1
        if BROW_ART[row][min(i, 5)] == '.':
            return None
        return A(HAIR[3] if f == 'top' else HAIR[0])
    inner = (f == 'east') if sx < 0 else (f == 'west')
    if inner:
        return A(HAIR[1]) if ctx.j == 0 else None
    return A(HAIR[2]) if ctx.j == 1 else None


# the stray curl that escaped the front roller: a C with a lit inner edge, over her right brow
CURL_ART = [
    ".hH",
    "h..",
    "H..",
    ".hh",
]


def curl_paint(ctx):
    if ctx.face not in ('front', 'back'):
        return None
    i = ctx.i if ctx.face == 'front' else ctx.w - 1 - ctx.i
    ch = CURL_ART[min(ctx.j, 3)][min(i, 2)]
    if ch == '.':
        return None
    return A(HAIR[6] if ch == 'H' else HAIR[2])


def curler_mat(ctx):
    """Hot-fuchsia plastic rollers (two crossed cubes per roller = an octagonal tube).  The barrel is shaded as a
    cylinder from each texel's angle round the axis, with a grid of perforations, a white pick ring, and a band
    of dark hair wound on near each end; the end caps are lighter flanges round a dark hollow core."""
    c = ctx.cube
    f = ctx.face
    x, y, z = apos(ctx)
    cx, cy, cz = c.ctr
    if c.axis == 'x':
        along, p, q = x - cx, y - cy, z - cz           # p = down, q = back
        caps = ('west', 'east')
        lp, lq = -0.78, -0.62                          # light from above and in front
    else:
        along, p, q = y - cy, x - cx, z - cz           # p = toward +x (her left), q = back
        caps = ('top', 'bottom')
        lp, lq = -0.45, -0.89                          # light from the front, a little from her right
    r = math.hypot(p, q) or 1e-6
    if f in caps:
        if r < 0.9:
            return A(CURL[0])                          # hollow core
        if r < 1.6:
            return A(CURL[2])                          # inside of the tube
        lam = (p * lp + q * lq) / r
        return A(pick(CURL, 0.66 + lam * 0.2))         # the flange: lighter than the barrel
    lam = max(0.0, (p * lp + q * lq) / r)
    v = 0.3 + lam * 0.5
    half = c.ln / 2.0
    if abs(along) > half - 1.0:
        return A(pick(CURL, v + 0.12))                 # the flange rim
    if abs(along) > half - 2.0:
        return A(pick(HAIR, 0.28 + lam * 0.35))        # the hair wound onto the roller
    if abs(along - c.pick_at) < 0.5:
        return A(mix(hx('#fbf7fa'), hx('#a898a4'), 0.0 if lam > 0.35 else 0.55))   # the white pick
    ang = math.atan2(q, p)
    ia = int(math.floor(along + half))
    ib = int(math.floor((ang + math.pi) / (2 * math.pi) * 14))
    if ia % 2 == 1 and ib % 2 == 0:
        v -= 0.2                                       # perforations
    if 0.62 < lam < 0.9:
        v += 0.08                                      # specular band
    if c.axis == 'x' and p > 0.6 * r:
        v -= 0.1                                       # the underside sits in the hair
    return A(pick(CURL, v))


# ------------------------------------------------------------------ the face
# 16 x 16: col c <-> x [-8 + c, -7 + c], row r <-> y [-30 + r, -29 + r].  Rows 0-11 on the skull, 12-15 on the
# jaw (cols 4-11) and the jowls (cols 1-3 / 12-14).  The brow cubes sit over rows 2-3, the nose cube over cols 7-8
# rows 6-8.
#   digits skin ramp  w specular  k crease  e eyeshadow  L/F lashes  K thin inner lash  W/V sclera  I/J iris
#   P pupil  b eye bag  r/R blush  u/U upper lip  o/O lower lip  T/t teeth  m soft mouth corner  n nostril
#   s shadow  H hair  x no geometry
GX0, GY0 = -8.0, -30.0
FACE = [
    # 0123456789012345
    "HHHHHHHHHHHHHHHH",   # r0  y-30  hairline (under the front roller)
    "5678888888887765",   # r1  y-29  forehead
    "5678888888w88765",   # r2  y-28  (brows)
    "5678888888888765",   # r3  y-27  (brows)
    "56eek777777keee5",   # r4  y-26  lids, a trace of mauve shadow at the outer corners
    "5FLLLK6776KLLLF5",   # r5  y-25  lash line: flicked out at the outer corners, thin at the inner corners
    "56WWWW6776WWWW65",   # r6  y-24  white ABOVE the iris: wide, jumpy eyes
    "56WgPW6776WgPW65",   # r7  y-23  glint + a 1-texel pupil
    "56VJJV6776VJJV65",   # r8  y-22  iris (lit lower half), shadowed corners
    "45b66b6nn6b66b54",   # r9  y-21  soft lower lids + bags | nostrils
    "4rRRrqUUUU655554",   # r10 y-20  blush | a one-row upper lip, her RIGHT corner pulled up (crooked)
    "45rr5uTTTuq65554",   # r11 y-19  the mouth line, a few teeth on the lifted side (away from the cream)
    "x45556oOOo65554x",   # r12 y-18  a short lower lip on the jaw | jowls
    "x45566s66s66554x",   # r13 y-17
    "x345667ww766543x",   # r14 y-16  chin
    "xxxx45666654xxxx",   # r15 y-15
]
assert all(len(r) == 16 for r in FACE), [len(r) for r in FACE]

# night cream on ONLY her left cheek (viewer's right): an organic smear under the eye, across the cheekbone and
# down onto the jowl, a finger-drag trail and loose dots.  C bright, c cream, d warm shadow edge.
CREAM_MAP = [
    "................",   # r0
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "...............c",   # r8   a loose dot by the eye's corner
    "...........dccd.",   # r9   under the eye
    "..........dcCCCc",   # r10  across the cheekbone
    "...........cCCCd",   # r11
    "............cCd.",   # r12  down onto the jowl
    "............dc..",   # r13  the finger-drag trail
    "..............d.",   # r14  a dot
    "................",
]
assert all(len(r) == 16 for r in CREAM_MAP)


def face_rgba(ch):
    if ch.isdigit():
        return SKIN[int(ch)]
    return {
        'H': HAIR[2], 'w': SKIN[9], 'k': SKIN[4], 'L': LASH, 'F': LASH, 'K': mix(LASH, SKIN[5], 0.5),
        'W': SCLERA, 'V': SCLERA2, 'I': IRIS, 'J': IRIS2, 'P': PUPIL, 'g': GLINT,
        'b': mix(SKIN[6], hx('#9a7a9a'), 0.22), 'e': mix(SKIN[6], hx('#9a6aaa'), 0.3),
        'r': mix(SKIN[6], hx('#e8707a'), 0.38), 'R': mix(SKIN[6], hx('#e8707a'), 0.58),
        'u': LIP[0], 'q': mix(LIP[0], SKIN[3], 0.35), 'U': mix(SKIN[5], LIP[2], 0.6),
        'o': mix(SKIN[6], LIP[3], 0.55), 'O': mix(SKIN[7], LIP[4], 0.45), 'T': TEETH[3], 't': TEETH[1], 'm': SKIN[3],
        's': SKIN[4], 'n': SKIN[2],
    }.get(ch, SKIN[5])


def cream_rgba(ch):
    return {'C': CREAM[4], 'c': CREAM[3], 'd': CREAM[1]}.get(ch)


def grid_char(grid, x, y):
    c = int(math.floor(x - GX0))
    r = int(math.floor(y - GY0))
    if 0 <= r < len(grid) and 0 <= c < 16:
        return grid[r][c]
    return None


def skin_mat(ctx):
    f = ctx.face
    n = nm(ctx)
    x, y, z = apos(ctx)
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    v = 0.62 + face_light(ctx) * 1.0
    if n == 'dollop':
        return dollop_paint(ctx)
    if n in ('skull', 'jaw', 'jowl') and f == 'front':
        cc = cream_rgba(grid_char(CREAM_MAP, x, y) or '.')
        if cc is not None:
            return A(cc)
        ch = grid_char(FACE, x, y)
        if ch and ch not in '.x ':
            return A(face_rgba(ch))
    if n == 'jowl':
        inner = (f == 'east') if ctx.cube.sx < 0 else (f == 'west')
        if inner:
            return A(MOUTH[2] if lz > 0.6 else LIP[1])             # inside of the cheek, seen when the jaw drops
        if f == 'top':
            return A(MOUTH[1])
        if f == 'bottom':
            return A(pick(SKIN, 0.42))
        if f == 'back':
            return None
        if f == 'east' and ctx.cube.sx > 0 and lz < 2.0 and ly < 1.5:
            return A(CREAM[2])                                    # the smear wraps round the jowl
        return A(pick(SKIN, 0.6 + face_light(ctx)))
    if n == 'skull':
        if f == 'bottom':
            if abs(x) < 4.0:
                if z < -7.0:
                    if abs(x) > 3.0:
                        return A(MOUTH[1])
                    return A(TEETH[3] if int(math.floor(x + 8)) % 2 else TEETH[1])   # upper teeth
                return A(MOUTH[1] if z < -3 else MOUTH[0])
            return A(pick(SKIN, 0.4))
        if f in ('west', 'east'):
            v -= 0.02
            if y > -21 and z < -2:
                v += 0.04                                         # cheek plane catches light
            if f == 'east':
                # the finger swipe: a thin white streak back toward the ear, and one dot
                if -20.0 < y < -19.0 and z < -4.5:
                    return A(CREAM[3] if z < -6.0 else CREAM[1])
                if -21.0 < y < -20.0 and -3.5 < z < -2.5:
                    return A(CREAM[2])
    if n == 'jaw':
        if f == 'top':
            if z < -7.0:
                if abs(x) > 2.5:
                    return A(MOUTH[1])
                return A(TEETH[2] if int(math.floor(x + 8)) % 2 else TEETH[0])   # lower teeth, gapped
            if abs(x) < 2.5 and z < -1.0:
                return A(MOUTH[4] if z < -4 else MOUTH[3])        # tongue
            return A(MOUTH[1])
        if f in ('west', 'east'):
            v -= 0.1
        if f == 'bottom':
            v = 0.45
    if n == 'nose':
        if f == 'bottom':
            return A(SKIN[3])
        if f == 'top':
            return A(SKIN[8])
        if f == 'front':
            return A(SKIN[8] if ctx.j == 0 else (SKIN[9] if ctx.j == 1 and ctx.i == 0 else SKIN[7]))
        return A(SKIN[7] if f == 'west' else SKIN[5])
    if n == 'neck':
        if y < -16:
            v -= 0.14                                             # under the chin
    if n in ('finger', 'fingers', 'thumb'):
        tip = h - ly < 1.0 if f in SIDE else f == 'bottom'
        if tip and f in ('bottom', 'front', 'west', 'east', 'back'):
            return A(NAIL[2] if (f != 'bottom' and ctx.i % 2 == 0) else NAIL[1])
        if n == 'fingers' and f in ('west', 'east') and ctx.i % 2 == 1:
            v -= 0.08                                             # finger splits (one finger per texel column)
    if n in ('palm', 'wrist', 'thumb', 'finger', 'fingers') and f == 'top':
        v -= 0.05
    if n == 'palm' and f in ('west', 'east'):
        palm_side = (f == 'east') if ctx.cube.sx < 0 else (f == 'west')
        if palm_side:
            v -= 0.04
        elif ly < 1.5:
            v += 0.04                                             # knuckles on the back of the hand
    if n == 'leg':
        if f in SIDE:
            cd = corner_dist(ctx)
            if cd < 1.0:
                v -= 0.06                                         # round the shin off
            elif f == 'front' and abs(lx - w / 2) < 1.0:
                v += 0.05                                         # lit shin bone
            if y > 17.0:
                v -= 0.05                                         # ankle into the slipper
        if y < 15:
            v -= 0.15                                             # under the robe and the nightgown
    if n == 'ear':
        v -= 0.04
    return A(pick(SKIN, v))


def dollop_paint(ctx):
    """The thick blob of cream at the thickest point of the smear: bright, a warm shadowed underside."""
    f = ctx.face
    if f == 'front':
        return A(CREAM[4] if (ctx.i, ctx.j) != (1, 1) else CREAM[3])
    if f == 'top':
        return A(CREAM[4])
    if f == 'bottom':
        return A(CREAM[1])
    if f in ('west', 'east'):
        return A(CREAM[2] if ctx.j == 0 else CREAM[1])
    return None


# ------------------------------------------------------------------ slippers: two plush dachshund heads
def slipper_mat(ctx):
    f = ctx.face
    n = nm(ctx)
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    v = 0.55 + face_light(ctx) * 1.0
    kk = nub(ctx) if (f in SIDE or f == 'top') else 0
    if n == 'dog_ear':
        sx = ctx.cube.sx
        if f in SIDE and ly > h - 1.0 and ctx.i in (0, ctx.w - 1):
            return None                                           # rounded lobe
        outer = (f == 'west') if sx < 0 else (f == 'east')
        if f == 'top':
            return A(pick(DOG, 0.32))
        if outer or f in ('front', 'back'):
            return A(pick(DOG, 0.18 + face_light(ctx) + (0.06 if ly < 1.0 else 0.0)))
        return A(pick(DOG, 0.12))
    if n == 'dog_head':
        if f == 'front':
            ci, cj = ctx.i, ctx.j
            if cj < 2 and ci in (1, 2, 4, 5):
                return A(GLINT if (cj == 0 and ci in (1, 4)) else INK)   # two big shiny button eyes (2 x 2)
            if cj == 0:
                v += 0.08
        if f == 'top':
            return A(pick(DOG, 0.62))
        if f in ('west', 'east', 'back') and ly < 1.0:
            v += 0.08
    if n == 'dog_snout':
        w2 = ctx.w
        if f == 'front':
            if ctx.j == 0 and ctx.i in (1, 2):
                return A(INK if ctx.i == 2 else hx('#4a3a3a'))     # the nose, with a glint
            if ctx.j == 1 and ctx.i == 2:
                return A(hx('#e0707e'))                           # tongue
            return A(pick(FUZZ, 0.5))                             # pale muzzle
        if f == 'top':
            if ctx.j == ctx.h - 1 and ctx.i in (1, 2):
                return A(INK)                                     # nose seen from above
            return A(pick(FUZZ, 0.62))
        if f in ('west', 'east'):
            return A(pick(FUZZ, 0.36 if ctx.j else 0.46))
    if n == 'fuzz':
        if f == 'top':
            cx, cz = abs(lx - w / 2), abs(lz - d / 2)
            return A(FUZZ[1] if max(cx, cz) < 2.6 else FUZZ[4])
        if f == 'bottom':
            return None
        if ly < 1.0:
            u = int(math.floor(around(ctx)))
            if u % 3 == 2:
                return None                                       # tufted top edge
            return A(pick(FUZZ, 0.86))
        return tone(FUZZ, 0.62 + face_light(ctx), nub(ctx), 0.6)
    return tone(DOG, v, kk)


def sole_mat(ctx):
    f = ctx.face
    v = 0.6 + face_light(ctx) * 0.8
    if f == 'top':
        return A(SOLE[2])
    if f in SIDE and ctx.j == 0:
        v += 0.1
    return A(pick(SOLE, v))


# ------------------------------------------------------------------ props
def phone_mat(ctx):
    f = ctx.face
    h = ctx.cube.size[1]
    v = 0.5 + face_light(ctx) * 1.0
    if f == 'west':
        return A(screen_px(ctx.i, ctx.j, ctx.w, ctx.h) or BEZEL[0])
    if f == 'east':
        # the case back: teal, a camera bump in the top corner, a little daisy sticker
        i, j = ctx.i, ctx.j
        if j >= h - 3 and i >= ctx.w - 3:
            return A(BEZEL[1] if (i + j) % 2 else BEZEL[2])
        v = 0.55 + (0.06 if i == 0 else 0.0) - (0.06 if i == ctx.w - 1 else 0.0)
        if (i, j) in ((1, 3), (3, 3), (2, 2), (2, 4)):
            return A(hx('#fbf6ee'))
        if (i, j) == (2, 3):
            return A(GOLD[4])
        return A(pick(CASE, v))
    return A(pick(CASE, v + 0.05))


def screen_px(i, j, w, h):
    """Family chat on the screen (row 0 = the phone's bottom end, since the phone is held fingers-up)."""
    r = h - 1 - j            # 0 = top of the screen
    c = i
    if r == 0 or r == h - 1:
        return BEZEL[1]
    if r == 1:
        return SCREEN['head'] if c != 1 else SCREEN['logo']
    if r == h - 2:
        return SCREEN['bar']
    rr = r - 2
    if rr in (0, 1) and c <= w - 3:
        return SCREEN['in']
    if rr in (2, 3) and c >= 2:
        return SCREEN['out']
    if rr == 4 and c <= w - 2:
        return SCREEN['in']
    if rr == 5 and c == w - 1:
        return SCREEN['dot']
    return SCREEN['bg']


def gold_mat(ctx):
    f = ctx.face
    if f in ('west', 'east'):
        return A(GOLD[4] if ctx.j == 0 else GOLD[3])
    return None


def chori_mat(ctx):
    """One link of chorizo: browner red with placed white fat flecks, a darker wrinkled casing at the tied ends."""
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    if nm(ctx) == 'twine':
        return A(TWINE[2] if (ctx.i + ctx.j) % 2 == 0 else TWINE[1])
    v = 0.56 + face_light(ctx) * 1.0
    if f in ('front', 'back'):
        # the tied end: a puckered dark casing
        if (ctx.i, ctx.j) == (1, 1):
            return A(TWINE[1])
        return A(pick(CHORI, 0.22 if (ctx.i + ctx.j) % 2 else 0.3))
    end = min(lz, d - lz)
    if end < 1.0:
        v -= 0.2                                                  # wrinkled casing at the tie
        if (ctx.i + int(lz * 3)) % 2 == 0:
            v -= 0.08
    else:
        k = (int(lz) * 3 + ctx.i * 5 + {'top': 0, 'bottom': 1, 'west': 2, 'east': 3}[f]) % 7
        if k == 0:
            return A(FAT[1])                                      # fat fleck
        if k == 4 and f != 'bottom':
            return A(FAT[0])
        if ctx.j == 0 and f in ('west', 'east'):
            v += 0.08                                             # sheen
    return A(pick(CHORI, v))


def bread_mat(ctx):
    """Pan francés: a golden crust, darker baked ends, pale scored cuts along the top."""
    f = ctx.face
    lx, ly, lz = local(ctx)
    d = ctx.cube.size[2]
    v = 0.58 + face_light(ctx) * 1.0
    if f in ('front', 'back'):
        return A(pick(BREAD, 0.3 if min(ctx.i, ctx.j, ctx.w - 1 - ctx.i, ctx.h - 1 - ctx.j) == 0 else 0.42))
    end = min(lz, d - lz)
    if end < 2.0:
        v -= 0.16 - end * 0.05
    if f == 'top':
        if (int(lz) + ctx.i) % 4 == 1 and 0 < lx < ctx.cube.size[0] - 1 and end > 2:
            v += 0.26                                             # diagonal scored cuts
    elif f in ('west', 'east') and ctx.j == 0 and int(lz) % 4 == 1 and end > 2:
        v += 0.12
    if f == 'bottom':
        v -= 0.12
    return A(pick(BREAD, v))


def nightie_mat(ctx):
    """Cream cotton nightgown: only the hem shows under the robe -- a scalloped lace edge, tiny lilac flowers."""
    f = ctx.face
    if f == 'top':
        return None
    lx, ly, lz = local(ctx)
    h = ctx.cube.size[1]
    if f == 'bottom':
        return A(NIGHTIE[2])
    u = around(ctx)
    if h - ly < 1.0:
        if int(u) % 2 == 1:
            return None                                       # scallops
        return A(NIGHTIE[5])
    if h - ly < 2.0:
        return A(NIGHTIE[4] if int(u) % 2 == 0 else NIGHTIE[3])       # lace band
    v = 0.6 + face_light(ctx) * 0.8 - (0.12 if ly < 4.0 else 0.0)    # in the robe's shadow up top
    c = pick(NIGHTIE, v)
    if (int(u) + 2 * int(ly)) % 5 == 0 and int(ly) % 2 == 0:
        c = FLOWER[1]
    return A(c)


MATS = {
    'robe': robe_mat, 'belt': belt_mat, 'hair': hair_mat, 'curler': curler_mat, 'skin': skin_mat,
    'slipper': slipper_mat, 'sole': sole_mat, 'phone': phone_mat, 'gold': gold_mat, 'chori': chori_mat,
    'bread': bread_mat, 'nightie': nightie_mat, 'fluff': fluff_mat,
}


def marta_mat(ctx):
    return MATS[ctx.cube.kind](ctx)


def phone_glow(img, u0, v0, w, h):
    """'eyes' layer: the lit screen (everything but the bezel)."""
    px = img.load()
    for j in range(h):
        for i in range(w):
            c = screen_px(i, j, w, h)
            if c is not None and c not in BEZEL:
                px[u0 + i, v0 + j] = c


def phone_led(img, u0, v0, w, h):
    """'eyes' layer on the case back: the notification LED next to the camera, so the phone glows from behind."""
    px = img.load()
    px[u0 + w - 1, v0 + h - 4] = LED
    px[u0 + w - 2, v0 + h - 4] = LED


DEFAULT_MAT = marta_mat
FOCUS = 'head'

# ------------------------------------------------------------------ toggles (Java: ModelPart.visible)
TOGGLE_DEFAULT = {'chorizo': False, 'bread': False}
POSE_TOGGLES = {'throw': {'chorizo': True}}


class MartaModel(Model):
    """Exports every bone to Java.  The preview / gallery JSON carries a 'toggles' map (default visibility + per-pose
    overrides); bones the current pose hides keep their cubes under 'hidden_cubes' so a toggle-aware viewer can show
    them (e.g. the chorizo in 'throw')."""
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


# ------------------------------------------------------------------ kinematics
def _R(rot_deg):
    return rot_matrix(*[math.radians(a) for a in rot_deg])


def _T(p):
    M = np.eye(4)
    M[:3, 3] = p
    return M


def _RM(rot_deg):
    M = np.eye(4)
    M[:3, :3] = _R(rot_deg)
    return M


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


def _wrap_near(a, ref):
    return ref + ((a - ref + 180.0) % 360.0) - 180.0


def euler_near(R, ref):
    """Of the two Euler triples of R, the one closest to ref (each angle wrapped next to ref): keeps pose deltas
    small so a linear blend of the table does not corkscrew."""
    x, y, z = _euler(R)
    best = None
    for c in ((x, y, z), (x + 180.0, 180.0 - y, z + 180.0)):
        cc = tuple(_wrap_near(c[i], ref[i]) for i in range(3))
        cost = max(abs(cc[i] - ref[i]) for i in range(3))
        if best is None or cost < best[0]:
            best = (cost, cc)
    return best[1]


def fk(roots, rots=None):
    """World matrices of every bone; rots = {bone: (x, y, z) degrees} overrides the bone's rest rotation."""
    rots = rots or {}
    W = {}

    def rec(b, M):
        Mb = M @ _T(np.array(b.pivot)) @ _RM(rots.get(b.name, b.rot))
        W[b.name] = Mb
        for c in b.children:
            rec(c, Mb)
    for r in roots:
        rec(r, np.eye(4))
    return W


def frame(dir_a, vec_a, dir_b, vec_b):
    """Rotation matrix mapping local unit dir_a -> world vec_a exactly and local dir_b -> as close as possible to
    world vec_b."""
    va = np.array(vec_a, float)
    va /= np.linalg.norm(va)
    vb = np.array(vec_b, float)
    vb = vb - va * np.dot(va, vb)
    vb /= np.linalg.norm(vb)
    vc = np.cross(va, vb)
    la = np.array(dir_a, float)
    lb = np.array(dir_b, float)
    lc = np.cross(la, lb)
    Lm = np.stack([la, lb, lc], 1)
    Wm = np.stack([va, vb, vc], 1)
    return Wm @ Lm.T


def solve_arm(roots, side, wrist, hand_R=None, elbow_hint=None, rots=None, rest=None, limit=80.0,
              palm_weight=4.0):
    """Arm (x, y, z) + forearm x (degrees) putting the hand pivot on `wrist` (world), with every angle kept within
    `limit` degrees of `rest` where possible; then the hand rotation (the Euler triple nearest its rest) so the
    hand's world orientation is hand_R.  Returns {bone: rot}."""
    from scipy.optimize import minimize
    rots = dict(rots or {})
    rest = rest or {}
    arm, fa, hand = f'{side}_arm', f'{side}_forearm', f'{side}_hand'
    r_arm = rest.get(arm, (0.0, 0.0, 0.0))
    r_fa = rest.get(fa, (0.0, 0.0, 0.0))[0]
    target = np.array(wrist, float)

    loc_palm = np.array((1.0, 0.0, 0.0) if side == 'right' else (-1.0, 0.0, 0.0))
    loc_fing = np.array((0.0, 1.0, 0.0))
    if hand_R is not None:
        t_palm, t_fing = hand_R @ loc_palm, hand_R @ loc_fing

    def chain(p):
        rr = dict(rots)
        rr[arm] = (p[0], p[1], p[2])
        rr[fa] = (p[3], 0, 0)
        rr[hand] = rest.get(hand, (0.0, 0.0, 0.0))
        W = fk(roots, rr)
        return W[hand][:3, 3], W[fa][:3, 3], W[hand][:3, :3]

    def cost(p):
        w, e, Rh = chain(p)
        c = float(np.sum((w - target) ** 2))
        if hand_R is not None:
            # prefer an arm twist that already turns the palm the right way: the hand's own delta stays small
            c += palm_weight * (float(np.sum((Rh @ loc_palm - t_palm) ** 2)) + 0.5 * float(np.sum((Rh @ loc_fing - t_fing) ** 2)))
        if elbow_hint is not None:
            c += 0.02 * float(np.sum((e - np.array(elbow_hint, float)) ** 2))
        for i in range(3):
            c += 2e-3 * max(0.0, abs(p[i] - r_arm[i]) - limit) ** 2
        c += 2e-3 * max(0.0, abs(p[3] - r_fa) - limit) ** 2
        c += 0.02 * max(0.0, p[3]) ** 2                         # elbows only bend one way
        return c
    best = None
    g0 = list(r_arm) + [r_fa]
    for g in (g0, [g0[0] - 40, g0[1], g0[2] + 30, g0[3] - 40], [g0[0] - 70, g0[1] + 30, g0[2] + 40, g0[3] - 60],
              [g0[0] - 60, g0[1] - 30, g0[2] - 20, g0[3] - 30], [g0[0] + 20, g0[1], g0[2], g0[3] - 50]):
        res = minimize(cost, g, method='Nelder-Mead', options={'xatol': 1e-4, 'fatol': 1e-10, 'maxiter': 8000})
        if best is None or res.fun < best.fun:
            best = res
    p = best.x
    out = {arm: tuple(_wrap_near(p[i], r_arm[i]) for i in range(3)), fa: (_wrap_near(p[3], r_fa), 0, 0)}
    if hand_R is not None:
        rr = dict(rots)
        rr.update(out)
        W = fk(roots, rr)
        out[hand] = euler_near(W[fa][:3, :3].T @ hand_R, rest.get(hand, (0.0, 0.0, 0.0)))
    return out


# ------------------------------------------------------------------ rest pose (degrees)
# Right arm hangs relaxed, a little out and forward, the back of the hand turned to the front and the fingers
# loosely curled.  Left arm: the phone held in front of her ribs, screen tilted up and toward the viewer (she was
# just reading the family chat) -- solved with solve_arm() from REST_IK (python3 tools/models/ent_marta.py --rest).
ARM_REST = {
    'right_arm': (-4.0, 0.0, 7.0), 'right_forearm': (-16.0, 0.0, 0.0), 'right_hand': (0.0, -40.0, 0.0),
    'left_arm': (-31.5, -3.0, 62.6), 'left_forearm': (-52.8, 0.0, 0.0), 'left_hand': (62.1, -26.1, -28.2),
}
FINGER_REST = {'right_index': (0.0, 0.0, -18.0), 'right_fingers': (0.0, 0.0, -38.0)}
REST_IK = ('left', (5.5, -4.0, -13.5), (0.35, -0.75, -0.55), (-0.75, -0.1, -0.65), (15, -3, -5))


def build(pose=None):
    pose = pose or _argv('--pose')
    r = Rig()

    def bone(name, pivot, parent=None, rot=(0, 0, 0)):
        r.bone(name, pivot, parent=parent, rot=rot)

    def box(b, frm, size, k, name=None, inflate=0.0, decals=None, **attrs):
        c = r.box(b, frm, size, inflate=inflate, decals=decals)
        c.kind = k
        c.name = name or k
        c.ax, c.ay, c.az = frm
        c.seed = int(abs(frm[0]) * 7 + abs(frm[1]) * 3 + abs(frm[2]) * 5) % 97
        c.sx = 0
        for kk, vv in attrs.items():
            setattr(c, kk, vv)
        return c

    # ---------------- body (pivot at the hips)
    bone('body', (0, 2, 0))
    box('body', (-10, -12, -6), (20, 7, 12), 'robe', 'torso')
    box('body', (-9, -5, -5.5), (18, 4, 11), 'robe', 'waist')
    box('body', (-8, -9.5, -8), (16, 6, 2), 'robe', 'bust')
    box('body', (-9.5, -3, -7.5), (19, 2, 13), 'belt', 'belt', inflate=0.25)
    box('body', (-0.5, -3.7, -9.7), (5, 3, 2), 'belt', 'knot')            # back face touches the belt (z -7.75)
    box('body', (-7, -16, 2.5), (14, 5, 4), 'robe', 'collar_back')
    box('body', (-8, -17, 2), (16, 1, 5), 'fluff', 'fluff', grow='up', tone=0.76)
    box('body', (-8.5, -14, -5), (3, 3, 8), 'robe', 'collar_side', sx=-1)
    box('body', (5.5, -14, -5), (3, 3, 8), 'robe', 'collar_side', sx=1)
    box('body', (-9, -15, -5.5), (4, 1, 9), 'fluff', 'fluff', grow='up', tone=0.76)
    box('body', (5, -15, -5.5), (4, 1, 9), 'fluff', 'fluff', grow='up', tone=0.76)
    box('body', (-6.5, -11, 6), (13, 9, 1), 'robe', 'hood')
    box('body', (-9.5, 7, -6), (19, 7, 11), 'nightie', 'nightie')          # the lace hem peeks out to y 14

    for side, sx in (('right', -1), ('left', 1)):
        lb = f'lapel_{side}'
        bone(lb, (6.5 * sx, -13, -6.5), 'body', rot=(-8, 0, LAPEL_ROT * sx))
        box(lb, (6.5 * sx - 1.5, -13, -8), (3, 13, 3), 'robe', 'lapel', sx=sx)

    # wrap skirt: the side panels run back to z 5 and skirt_back starts at z 0.5, so they overlap by 3+ texels at
    # every flare / walk-swing angle (no slit down the sides)
    bone('skirt_right', (-5.5, -1, 0), 'body', rot=(-2, 0, SKIRT_FLARE))
    box('skirt_right', (-11, -1, -7), (11, 12, 12), 'robe', 'skirt', sx=-1)
    box('skirt_right', (-11.5, 10, -7.5), (12, 2, 13), 'fluff', 'fluff', grow='down', tone=0.68)
    bone('skirt_left', (5.5, -1, 0), 'body', rot=(-2, 0, -SKIRT_FLARE))
    box('skirt_left', (-2, -1, -8), (13, 12, 13), 'robe', 'skirt', sx=1)
    box('skirt_left', (-2.5, 10, -8.5), (14, 2, 14), 'fluff', 'fluff', grow='down', tone=0.68)
    bone('skirt_back', (0, -1, 3), 'body', rot=(5, 0, 0))
    box('skirt_back', (-11, -1, 0.5), (22, 12, 6), 'robe', 'skirt', sx=0)
    box('skirt_back', (-11.5, 10, 0), (23, 2, 7), 'fluff', 'fluff', grow='down', tone=0.64)

    bone('belt_tails', (2, -1, -9), 'body', rot=(-4, 0, 0))
    box('belt_tails', (0.2, -1.4, -9.4), (2, 10, 1), 'belt', 'tail')
    box('belt_tails', (2.6, -1.4, -9.2), (2, 8, 1), 'belt', 'tail')

    # ---------------- neck + head (face 16 x 16: skull 12 rows + jaw 4)
    bone('neck', (0, -11, 0), 'body')
    box('neck', (-3.5, -17.5, -3), (7, 7, 6), 'skin', 'neck')
    bone('head', (0, -17, 0), 'neck')
    box('head', (-8, -30, -8), (16, 12, 16), 'skin', 'skull')
    box('head', (-8, -30, -8), (16, 12, 16), 'hair', 'hair', inflate=0.5)
    box('head', (-1, -24, -10), (2, 3, 2), 'skin', 'nose')
    box('head', (4, -20, -9), (2, 2, 1), 'skin', 'dollop')                 # the thick blob of cream
    box('head', (-5, -31, -8.7), (3, 4, 0), 'hair', 'curl')                # the stray curl
    box('head', (-9, -23, -1), (1, 4, 3), 'skin', 'ear')
    box('head', (8, -23, -1), (1, 4, 3), 'skin', 'ear')
    box('head', (-9.4, -19.5, -0.5), (0, 3, 2), 'gold', 'earring')
    box('head', (9.4, -19.5, -0.5), (0, 3, 2), 'gold', 'earring')
    box('head', (-7, -18, -8), (3, 3, 9), 'skin', 'jowl', sx=-1)
    box('head', (4, -18, -8), (3, 3, 9), 'skin', 'jowl', sx=1)
    bone('jaw', (0, -18, 2), 'head')
    box('jaw', (-4, -18, -8), (8, 4, 10), 'skin', 'jaw')
    bone('right_brow', (-4, -27, -8.5), 'head', rot=(0, 0, -BROW_WORRY))
    box('right_brow', (-7, -28, -9), (6, 2, 1), 'hair', 'brow', sx=-1)
    bone('left_brow', (4, -27, -8.5), 'head', rot=(0, 0, BROW_WORRY))
    box('left_brow', (1, -28, -9), (6, 2, 1), 'hair', 'brow', sx=1)

    # five rollers.  Crown: three along X, stacked front -> middle -> back like hair rolled back from the hairline,
    # so the perforated barrels and the white picks face the camera; the middle one rides highest.  Temples: one
    # standing (along Y) over each ear.
    bone('curlers', (0, -30, 0), 'head')
    CROWN = ((-32.5, -5.0, 6, 12, 2.0), (-34.5, 0.0, 7, 11, -2.0), (-32.5, 5.0, 6, 12, 1.0))
    for cy, cz, D, L, pk in CROWN:
        box('curlers', (-L / 2, cy - D / 2, cz - (D - 2) / 2), (L, D, D - 2), 'curler', 'curler', axis='x',
            ctr=(0.0, cy, cz), ln=L, pick_at=pk)
        box('curlers', (-L / 2 + 0.5, cy - (D - 2) / 2, cz - D / 2), (L - 1, D - 2, D), 'curler', 'curler',
            axis='x', ctr=(0.0, cy, cz), ln=L, pick_at=pk)
    box('curlers', (-5, -32, -2), (10, 3, 4), 'hair', 'hair_bun')          # hair wound up under the middle one
    for sx in (-1, 1):
        cx, cz, L, D = 10.5 * sx, -2.0, 8, 5
        box('curlers', (cx - D / 2, -31, cz - (D - 2) / 2), (D, L, D - 2), 'curler', 'curler', axis='y',
            ctr=(cx, -27.0, cz), ln=L, pick_at=-1.5 * sx)
        box('curlers', (cx - (D - 2) / 2, -30.5, cz - D / 2), (D - 2, L - 1, D), 'curler', 'curler', axis='y',
            ctr=(cx, -27.0, cz), ln=L, pick_at=-1.5 * sx)

    # ---------------- arms (authored hanging; bent by the bone rotations)
    for side, sx in (('right', -1), ('left', 1)):
        arm, fa, hand = f'{side}_arm', f'{side}_forearm', f'{side}_hand'
        ax = 13.0 * sx
        bone(arm, (10.5 * sx, -10, 0), 'body', rot=ARM_REST[arm])
        box(arm, (ax - 3.5, -13, -3.5), (7, 11, 7), 'robe', 'sleeve_up', sx=sx)
        bone(fa, (ax, -2.5, 0), arm, rot=ARM_REST[fa])
        box(fa, (ax - 3, -3, -3), (6, 7, 6), 'robe', 'sleeve_lo', sx=sx)
        box(fa, (ax - 4, 2.5, -4), (8, 4, 8), 'robe', 'cuff', sx=sx)
        box(fa, (ax - 5, 1.5, -5), (10, 1, 10), 'fluff', 'fluff', grow='up', tone=0.74)
        box(fa, (ax - 5, 6.5, -5), (10, 1, 10), 'fluff', 'fluff', grow='down', tone=0.7)
        box(fa, (ax - 1.5, 5, -1.5), (3, 3, 3), 'skin', 'wrist')
        bone(hand, (ax, 7.5, 0), fa, rot=ARM_REST[hand])
        box(hand, (ax - 1.5, 7, -2.5), (3, 4, 5), 'skin', 'palm', sx=sx)
        box(hand, (ax - 1 - 0.6 * sx, 7.6, -3.9), (2, 3, 2), 'skin', 'thumb')
        if sx < 0:
            bone('right_index', (ax, 11, -1.5), hand, rot=FINGER_REST['right_index'])
            box('right_index', (ax - 1, 11, -2.5), (2, 5, 2), 'skin', 'finger')
            bone('right_fingers', (ax, 11, 1), hand, rot=FINGER_REST['right_fingers'])
            box('right_fingers', (ax - 1, 11, -0.5), (2, 4, 3), 'skin', 'fingers')
            # toggles in the fist: two chorizo links held by the twine between them, and a pan francés
            bone('chorizo', (ax, 10, 0), hand)
            box('chorizo', (ax - 1.5, 8.5, -6.5), (3, 3, 6), 'chori', 'chorizo')
            box('chorizo', (ax - 1, 9, -0.5), (2, 2, 1), 'chori', 'twine')
            bone('chorizo_link', (ax, 10, 0.5), 'chorizo', rot=(32, 0, 8))
            box('chorizo_link', (ax - 1.5, 8.5, 0.5), (3, 3, 6), 'chori', 'chorizo')
            bone('bread', (ax, 10, 0), hand)
            box('bread', (ax - 2, 8, -6.5), (4, 4, 13), 'bread', 'bread')
        else:
            box(hand, (ax - 1, 11, -2.5), (2, 4, 5), 'skin', 'fingers')
            bone('phone', (ax - 2, 12, 0), hand)
            box('phone', (ax - 2.5, 9, -3), (1, 9, 6), 'phone', 'phone',
                decals={'eyes:west': phone_glow, 'eyes:east': phone_led})

    # ---------------- legs (duck stance) + plush dachshund-head slippers
    for side, sx in (('right', -1), ('left', 1)):
        leg = f'{side}_leg'
        lxc = 4.5 * sx
        bone(leg, (lxc, 2, 0), 'body', rot=(0, -TOES_OUT * sx, 0))
        box(leg, (lxc - 2.5, 2, -2.5), (5, 18, 5), 'skin', 'leg')
        box(leg, (lxc - 3.5, 19, -4.5), (7, 4, 8), 'slipper', 'dog_head')
        box(leg, (lxc - 2, 21, -8.5), (4, 2, 4), 'slipper', 'dog_snout')
        box(leg, (lxc - 4.5, 18.5, -4), (2, 4, 3), 'slipper', 'dog_ear', sx=-1)
        box(leg, (lxc + 2.5, 18.5, -4), (2, 4, 3), 'slipper', 'dog_ear', sx=1)
        box(leg, (lxc - 3.5, 18, -3.5), (7, 2, 7), 'slipper', 'fuzz', inflate=0.2)
        box(leg, (lxc - 4, 23, -9.5), (8, 1, 13), 'sole', 'sole')

    m = MartaModel('marta', 256, 128, r.roots)
    m.scale = 0.5
    vis = dict(TOGGLE_DEFAULT)
    vis.update(POSE_TOGGLES.get(pose, {}))
    show = os.environ.get('MARTA_SHOW', '')
    if show:                                                      # preview helper: 'all' or 'chorizo,bread'
        vis = {k: (show == 'all' or k in show.split(',')) for k in vis}
    m.visible = {k for k, v in vis.items() if v}
    return m


# ------------------------------------------------------------------ poses
# Authored as world-space targets (texels, rest frame) and solved with solve_arm(); POSES below is the solver's
# output (python3 tools/models/ent_marta.py --solve re-solves and prints it).  Per pose:
#   'add': bone -> degrees added to the rest rotation, 'off': bone -> (dx, dy, dz) texels,
#   'ik':  (side, wrist target, world direction the palm faces, world direction the fingers point, elbow hint).
# Every solved angle stays within LIMIT degrees of its rest value, so Java's linear blend of a whole table never
# corkscrews a hand.
LIMIT = 85.0
POSE_TARGETS = {
    # hands wringing at her belly round the phone (screen up), the right hand rubbing over the left
    'idle_nervous': {
        'add': {'head': (4, 0, 6), 'right_brow': (0, 0, -5), 'left_brow': (0, 0, 5), 'right_fingers': (0, 0, -20),
                'right_index': (0, 0, -15)},
        'ik': [
            ('left', (3.5, -1.0, -12.5), (0.25, -0.8, -0.55), (-0.8, 0.0, -0.5), (15, -3, -5)),
            ('right', (-2.0, -2.5, -13.5), (0.75, 0.5, 0.4), (0.6, -0.2, -0.75), (-15, -3, -5)),
        ],
    },
    # 'Ay, Dios mio': the free hand flies to her RIGHT cheek (the cream cheek stays visible), the phone hand clutches
    # up by the left collarbone with the lit screen out; jaw drops, brows shoot up, she recoils
    'scared': {
        'add': {'head': (-8, 0, -4), 'jaw': (24, 0, 0), 'right_brow': (0, 0, -8), 'left_brow': (0, 0, 8),
                'body': (-4, 0, 0), 'right_leg': (4, 0, 0), 'left_leg': (4, 0, 0), 'right_fingers': (0, 0, 20),
                'right_index': (0, 0, 14)},
        'off': {'right_brow': (0, -1.5, 0), 'left_brow': (0, -1.5, 0), 'curlers': (0, -0.6, 0)},
        'ik': [
            ('right', (-9.0, -14.0, -11.5), (0.45, 0.1, 0.9), (0.15, -1.0, -0.1), (-17, -6, -6)),
            ('left', (9.5, -6.5, -12.0), (-0.3, 0.1, -0.95), (-0.35, -0.95, -0.05), (17, -2, -4)),
        ],
    },
    # pointing out (at the window / the doll): right arm out, index straight, the others curled
    'point': {
        'add': {'head': (-2, -14, 0), 'neck': (0, -8, 0), 'jaw': (8, 0, 0), 'right_brow': (0, 0, 12),
                'left_brow': (0, 0, -2), 'right_fingers': (0, 0, -72), 'right_index': (0, 0, 18), 'body': (0, -6, 0),
                'right_leg': (0, 6, 0), 'left_leg': (0, 6, 0)},
        'off': {'left_brow': (0, -0.8, 0)},
        'ik': [
            ('right', (-21.0, -15.0, -11.0), (0.15, 1.0, 0.25), (-0.75, -0.25, -0.62), (-17, -12, -5)),
        ],
    },
    # holding the phone out to the player, screen to camera; the right index points at the screen
    'show_phone': {
        'add': {'head': (4, 0, 7), 'jaw': (6, 0, 0), 'left_brow': (0, 0, 4), 'right_fingers': (0, 0, -70),
                'right_index': (0, 0, 18)},
        'off': {'left_brow': (0, -1.2, 0)},
        'ik': [
            ('left', (7.5, -6.0, -16.5), (-0.15, 0.05, -1.0), (-0.1, -1.0, -0.05), (16, -6, -8)),
            ('right', (-1.0, -6.5, -14.5), (-0.1, 1.0, 0.25), (0.8, -0.1, -0.6), (-15, -4, -6)),
        ],
    },
    # overhand throw, wind-up: chorizo cocked behind her head, phone arm out front, body twisted back
    'throw': {
        'add': {'body': (-5, 22, 0), 'right_leg': (5, -22, 0), 'left_leg': (5, -22, 0), 'head': (2, -18, 0),
                'neck': (0, -6, 0), 'jaw': (14, 0, 0), 'right_brow': (0, 0, 14), 'left_brow': (0, 0, -14),
                'right_fingers': (0, 0, -55), 'right_index': (0, 0, -60)},
        'ik': [
            ('right', (-15.0, -22.0, 6.0), (0.3, 0.0, -0.95), (0.1, -0.9, 0.4), (-20, -13, 0)),
            ('left', (14.0, -11.0, -14.0), (-0.3, 0.9, -0.3), (0.25, -0.35, -1.0), (17, -9, -5)),
        ],
    },
    # '¡TIRALE ALGO!': leaning in, chin up, the right hand cupped two texels in front of the mouth corner
    'shout': {
        'add': {'body': (6, 0, 0), 'right_leg': (-6, 0, 0), 'left_leg': (-6, 0, 0), 'neck': (6, 0, 0),
                'head': (-10, 8, 0), 'jaw': (27, 0, 0), 'right_brow': (0, 0, -6), 'left_brow': (0, 0, 6),
                'right_fingers': (0, 0, -55), 'right_index': (0, 0, -35)},
        'off': {'right_brow': (0, -1.2, 0), 'left_brow': (0, -1.2, 0)},
        'ik': [
            ('right', (-7.5, -12.5, -13.0), (0.85, 0.0, -0.5), (0.1, -0.95, -0.3), (-16, -6, -9)),
        ],
    },
}


def rest_rots(m):
    return {b.name: tuple(b.rot) for b in m.bones()}


def solve_rest():
    m = build()
    rest = rest_rots(m)
    side, wrist, palm, fing, hint = REST_IK
    R = frame((1, 0, 0) if side == 'right' else (-1, 0, 0), palm, (0, 1, 0), fing)
    return solve_arm(m.roots, side, wrist, R, elbow_hint=hint, rots=rest, rest=rest, limit=170.0)


def solve_poses(names=None):
    """Re-solve POSE_TARGETS -> {pose: {bone: (xRot, yRot, zRot, dx, dy, dz)}} (radians / texels, added to rest)."""
    m = build()
    rest = rest_rots(m)
    out = {}
    for name in names or POSE_TARGETS:
        spec = POSE_TARGETS[name]
        rots = dict(rest)
        for b, r in spec.get('add', {}).items():
            rots[b] = tuple(rest[b][i] + r[i] for i in range(3))
        for side, wrist, palm, fing, hint in spec.get('ik', []):
            R = frame((1, 0, 0) if side == 'right' else (-1, 0, 0), palm, (0, 1, 0), fing)
            rots.update(solve_arm(m.roots, side, wrist, R, elbow_hint=hint, rots=rots, rest=rest, limit=LIMIT))
        table = {}
        for b in rots:
            d = [math.radians(rots[b][i] - rest[b][i]) for i in range(3)]
            off = spec.get('off', {}).get(b, (0, 0, 0))
            if any(abs(a) > 1e-4 for a in d) or any(abs(o) > 1e-4 for o in off):
                table[b] = tuple(round(a, 4) for a in d) + tuple(float(o) for o in off)
        for b, off in spec.get('off', {}).items():
            table.setdefault(b, (0.0, 0.0, 0.0) + tuple(float(o) for o in off))
        out[name] = table
    return out


def pose_report(poses):
    """Largest |delta| per pose (degrees) and where each IK wrist actually landed."""
    for name, table in poses.items():
        big = max(((abs(v), b) for b, t in table.items() for v in t[:3]), default=(0, None))
        print('%-13s max |delta| %6.1f deg (%s)' % (name, math.degrees(big[0]), big[1]))


POSES = {}
ANIM_NOTES = """(rewritten below)"""


if __name__ == '__main__':
    if '--rest' in sys.argv:
        for k, v in solve_rest().items():
            print(k, tuple(round(a, 2) for a in v))
    if '--solve' in sys.argv:
        P = solve_poses()
        for k, v in P.items():
            print("    '%s': {" % k)
            for b, t in v.items():
                print("        '%s': (%s)," % (b, ', '.join(('%.4f' % a).rstrip('0').rstrip('.') if a else '0' for a in t)))
            print('    },')
        pose_report(P)
