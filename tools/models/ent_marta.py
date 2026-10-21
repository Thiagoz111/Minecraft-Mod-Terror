"""Marta Morales (42) -- the mum of the Casa Morales, comic guide, NEVER possessed (DEAD LINE, case 'casa').

Authored at 2x texel density (model.scale = 0.5).  +Y down, ground y = 24, faces -Z, right_* on -X.  Centred on
x = 0, z = 0 (only the arms, the phone and the slipper snouts leave the column).  Height: 1.70 blocks to the crown
of the hair (y -30.5), 1.80 to the top of the middle roller (y -33.6); a 0.6 x 1.75 hitbox fits.  73 cubes,
26 bones, texture 256 x 128.  No variants (she is never possessed); two prop toggles (chorizo, bread).

Design sketch
-------------
Role: pure comedy and the player's guide in the case.  She opens the door at night in curlers, shows the family
chat on her phone, shouts '¡TIRALE ALGO!' and throws chorizo and bread through the kitchen window.  Read in one
glance: a nervous, kind mum caught mid beauty routine.  The horror read is only a gag: at night, backlit in the
doorway, the crown of rollers is a strange silhouette and the white cream on one cheek catches the flashlight.
For a split second it is a pale-faced shape at the door, and then it is just Marta.

Silhouette: a soft pink pear with a bumpy crown.  Five fuchsia rollers, all along z so their round ends face the
camera, sit in an arc over the head: three on the crown, the middle one riding higher, and one over each temple
sticking out past the ears.  A thick shawl collar rolls round the neck and closes into a V at the belt.  Below it
are a bust shelf, a cinched belt waist (the waist cube is narrower than the chest) with a knot and two hanging
tails, and a wrap skirt whose panels flare 3 deg to just under the knee.  The cream lace hem of her nightgown peeks
out underneath.  Then bare shins and two plush DACHSHUND-HEAD slippers in Choripán's caramel, a nod to the family
dog.  The phone in her left hand is the only spike in the outline.
Proportions (texels at 2x): head 16 (crown -30 .. chin -14), torso 13 (shoulders -12 .. belt -1), skirt to y 11,
legs to y 24.  The head is a third of the body height, the same chunky family style as Jorge.

Face (16 x 16, hand-placed FACE grid, rows 0-11 on the skull, 12-15 on the jaw and jowls):
* Hair pulled up into the front rollers, with one stray curl dropped on the forehead.
* Thin plucked arched brows on their own bones, at rest tilted 10 deg inner-ends-up so she is always a little
  worried.
* Wide 4 x 2 eyes: lash line flicked out at the outer corners, brown irises with a glint, a trace of mauve
  eyeshadow at the outer corners, soft bags under the eyes.
* A small nose cube, blush on the right cheek, a polite smile whose corners curl up into the cheeks, mauve lips
  with a cupid's bow.
* Face cream on ONLY her left cheek: the left cheek cube is a thick white dollop with a finger swirl, a smear
  under the eye, a drip onto the jowl and a swipe back towards the ear.
* An 8-wide hinged jaw (chin + lower lip) between two static jowls.  It opens into a round O with upper and lower
  teeth and a tongue, never a full-width box.
* Small gold drop earrings; a gold chain and medal in the V of the neckline.

Wardrobe and props:
* Bathrobe in coral-fleece pink: soft tonal patches with sparse lit and shadowed tufts, wrap folds on the skirt
  panels, a lighter facing down the wrap edge, a lit shawl collar with a shadowed outer roll, turned-back cuffs,
  patch pockets with stitched edges (a crumpled tissue pokes out of the right one), belt loops, a dropped shoulder
  seam, and a hood lying flat on her back.
* Nightgown: cream cotton with lilac flowers and a lace neckline in the V; a scalloped lace hem below the robe.
* Phone: a teal case (complementary to all the pink) with a camera bump and a daisy sticker.  The screen shows
  the family chat (teal header, white and green bubbles, a red unread dot) and is lit on the 'eyes' layer.
* Slippers: caramel plush dachshund heads with big black eyes and glints, a black nose, a pink tongue, dark
  floppy ears and cream soles.
* Toggles in the right fist: a chorizo (marbled red, fat specks, twine at both ends) and a pan francés (golden
  crust, scored top, darker baked ends).

Palette (hand-picked, hue-shifted ramps):
* Robe: bubblegum pink with purple shadows (10 tones).
* Rollers: saturated fuchsia plastic, with a lit specular band and perforations.
* Skin: warm tan (10 tones).
* Hair: dark mahogany with a warm sheen.
* Cream: mint-white.
* Nightgown: cream with lilac flowers.
* Phone: teal.
* Slippers: caramel, the same as Choripán.
* Small accents: gold jewellery and red nail polish.
"""
import math
import os
import sys

import numpy as np

from mcmodel import Model, hash3, face_light, pick, rot_matrix, fbm
from rig import Rig
from paint import hx, mix


def H(*cs):
    return [hx(c) for c in cs]


def A(c, a=255):
    return (c[0], c[1], c[2], int(a))


# ------------------------------------------------------------------ palettes (dark -> light, hue shifted)
ROBE = H('#3d1638', '#5c2050', '#7e2e66', '#a0427c', '#be5a91', '#d576a6', '#e693b9', '#f1b1cc', '#f8cddd',
         '#fde6ee')
CURL = H('#3a0624', '#620a3a', '#8e1253', '#b81d6b', '#db3184', '#f2549e', '#fb83ba', '#ffb6d6', '#ffe4f0')
SKIN = H('#3b1f1a', '#5c2f26', '#7f4334', '#a05a45', '#bb7459', '#d08e6f', '#e0a787', '#ebbe9f', '#f4d4bb',
         '#fbe8d8')
HAIR = H('#140808', '#221010', '#331611', '#461d16', '#5c271c', '#743423', '#8e442e', '#a85a3c')
CREAM = H('#a7b4ae', '#c9d4cf', '#e2eae6', '#f2f7f4', '#ffffff')
NIGHTIE = H('#6c5a62', '#968088', '#bca8ac', '#d9cbc8', '#ece3dd', '#f7f1ea')
FLOWER = H('#6a4c9c', '#8a6cc0', '#b49ae0')
LEAF = H('#4f7a4c', '#6f9a6a')
GOLD = H('#4a300a', '#7a5414', '#a8791f', '#d1a334', '#ecc85a', '#fbe6a0')
CASE = H('#04232a', '#08363f', '#0f4c56', '#18646e', '#25808a', '#3a9ea6', '#5fbcc0', '#94dcd8')
DOG = H('#2b1409', '#46200e', '#643015', '#83431e', '#a2592a', '#bd723a', '#d38e52', '#e6ab70', '#f2c896')
SOLE = H('#4a3e32', '#6e5e4c', '#958268', '#b8a488', '#d8c8ac', '#ece2cc')
CHORI = H('#2a0705', '#470d09', '#6a150e', '#8e2214', '#b0331d', '#c84a2a', '#dc6a42')
BREAD = H('#4a250c', '#74401a', '#9e5f2a', '#c27e3c', '#d99c56', '#ebbd7c', '#f6daa6')
LIP = H('#5a2030', '#7e3444', '#a24c5c', '#c06a76', '#d88a92')
NAIL = H('#7a1020', '#a81c30', '#d03448', '#f0687a')
MOUTH = H('#1a0608', '#2e0c10', '#4a1820', '#6e2a34', '#9a4450')
TEETH = H('#8c8478', '#bdb5a6', '#e2dccf', '#f6f2ea')
SCLERA = hx('#f3ece6')
SCLERA2 = hx('#cfc2bc')
IRIS = hx('#7a4e26')
IRIS2 = hx('#3e2412')
LASH = hx('#1a0c0c')
GLINT = hx('#ffffff')
BEZEL = H('#060608', '#101116', '#1c1e26')
SCREEN = {'bg': hx('#efe8dc'), 'head': hx('#167a6e'), 'head2': hx('#0f5a52'), 'in': hx('#ffffff'),
          'out': hx('#bdeca6'), 'txt': hx('#8a8a8a'), 'txt2': hx('#4f7a4c'), 'dot': hx('#e8384a'),
          'bar': hx('#d4ccbf'), 'logo': hx('#ffffff')}


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
    """Distance (texels) to the nearest vertical edge of the cube along the wrapped side faces."""
    w, h, d = ctx.cube.size
    u = around(ctx)
    return min(abs(u - c) for c in (0, w, w + d, 2 * w + d, 2 * (w + d)))


def edge(ctx):
    return min(ctx.i, ctx.j, ctx.w - 1 - ctx.i, ctx.h - 1 - ctx.j)


def h2(a, b, s=0):
    return hash3(a, b, 0, s)


def kind(ctx):
    return ctx.cube.kind


def nm(ctx):
    return ctx.cube.name


SIDE = ('front', 'back', 'west', 'east')


# ------------------------------------------------------------------ fleece
def plush(ctx, k=0, amt=1.0):
    """Coral fleece: soft low-frequency tonal patches + sparse single fluff highlights / dark specks."""
    x, y, z = apos(ctx)
    s = getattr(ctx.cube, 'seed', 0) + k
    v = (fbm(x * 0.22 + s, y * 0.22, z * 0.22, 2, 5) - 0.5) * 0.11
    hh = h2(ctx.i * 3 + s * 7, ctx.j * 5 + s * 11, 42)
    if hh > 0.9:
        v += 0.07                                                 # a lit tuft
        if h2(ctx.i * 3 + s * 7, ctx.j * 5 + s * 11 + 5, 43) > 0.5:
            v += 0.03
    elif hh < 0.06:
        v -= 0.05                                                 # a shadowed tuft
    return v * amt


def robe_mat(ctx):
    f = ctx.face
    n = nm(ctx)
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    x, y, z = apos(ctx)
    side = f in SIDE
    v = 0.6 + face_light(ctx) * 1.1 + plush(ctx)
    if side and min(w, d) > 2 and n not in ('lapel',):
        cd = corner_dist(ctx)
        if cd < 1.0:
            v -= 0.06
    if n in ('torso', 'bust', 'waist') and f == 'front':
        nv = vneck(ctx, x, y)
        if nv is not None:
            return nv
    if n == 'torso' and f == 'bottom':
        return A(pick(ROBE, 0.36))
    if n == 'waist':
        if f in SIDE:
            v -= 0.06
        if f in ('front', 'back'):
            # gathered fleece above the belt: short folds converging on the waist
            ph = (x * 0.9 + (y + 5) * 0.4) % 4.0
            if ph < 0.9:
                v -= 0.07
        if f == 'back' and y < -8:
            v += 0.03
    if n == 'bust':
        if f == 'bottom':
            v -= 0.16
        elif f == 'top':
            v += 0.03
        elif f == 'front' and ly > h - 1.0:
            v -= 0.05
    if n == 'skirt':
        if f == 'bottom':
            return A(pick(ROBE, 0.28 + plush(ctx) * 0.5))      # the inside of the robe
        if f == 'top':
            return A(pick(ROBE, 0.3))
        if side:
            u = around(ctx) + ctx.cube.seed * 1.7
            fold = math.sin(u * 2 * math.pi / 6.5)
            v += fold * 0.05
            if fold < -0.8:
                v -= 0.05                                         # fold valley
            v -= ly / h * 0.07
            if ly < 1.0:
                v -= 0.08                                         # tucked under the belt
            if h - ly < 1.0:
                v += 0.1                                          # the hem roll catches light
            v += pocket(ctx, lx, ly, f)
    if n in ('sleeve_up', 'sleeve_lo'):
        if f in ('top', 'bottom'):
            return A(pick(ROBE, 0.3))
        if n == 'sleeve_up' and ly > h - 2.5:
            if (around(ctx) + ly) % 4 < 1.0:
                v -= 0.08                                         # elbow creases
        if n == 'sleeve_up' and ly < 3:
            v += 0.03
        if n == 'sleeve_up' and 1.0 <= ly < 2.0:
            v -= 0.07                                             # dropped-shoulder seam
    if n == 'cuff':
        if f == 'bottom':
            cx = abs(lx - w / 2)
            cz = abs(lz - d / 2)
            return A(ROBE[1] if max(cx, cz) < 2.5 else ROBE[3])
        if f == 'top':
            return A(pick(ROBE, 0.5))
        if side:
            v += 0.06
            if ly < 1.0:
                v += 0.1                                          # turned-back edge
            elif ly < 2.0:
                v -= 0.06                                         # seam of the turn-back
    if n == 'lapel':
        v += 0.14
        if side:
            inner = (f == 'east') if ctx.cube.sx < 0 else (f == 'west')
            if f in ('west', 'east'):
                v += 0.02 if inner else -0.14                     # the roll: lit inner edge, shadowed outer
            if f == 'front':
                outer_col = 0 if ctx.cube.sx < 0 else ctx.w - 1
                inner_col = ctx.w - 1 - outer_col
                if ctx.i == outer_col:
                    v -= 0.08
                elif ctx.i == inner_col:
                    v += 0.06
        if f == 'top':
            v += 0.05
    if n == 'collar':
        v += 0.08
        if f == 'top':
            v += 0.04
    if n == 'hood':
        # the hood lies flat on her back: rounded bottom, a centre seam, the dark opening under the collar
        if f == 'back':
            cxl = abs(lx - w / 2)
            if ly > h - 2.5 and cxl > w / 2 - (h - ly) * 1.6 - 0.4:
                return None
            if ly < 1.2:
                return A(pick(ROBE, 0.22))                        # the opening
            if abs(lx - w / 2) < 0.5 and ly > 2:
                v -= 0.08                                         # centre seam
            if ly < 2.2:
                v += 0.08                                         # the rolled rim
            elif cxl > w / 2 - 1.0:
                v += 0.06
        elif f == 'top':
            return A(pick(ROBE, 0.25))
        elif f == 'front':
            return None
        elif f in ('west', 'east'):
            if ly > h - 2.0:
                return None
            v -= 0.06
    if n == 'skirt' and f == 'front' and ctx.cube.sx > 0 and lx < 2.0:
        v += 0.1 if lx < 1.0 else 0.04                            # the facing down the wrap edge
    if n == 'skirt' and f == 'west' and ctx.cube.sx > 0 and lz < 1.6:
        v += 0.06
    if n == 'waist' and f in ('west', 'east') and 2.0 < lz < 4.0:
        v += 0.1                                                  # belt loops
    return A(pick(ROBE, v))


def pocket(ctx, lx, ly, f):
    """Patch pocket on the front of each skirt panel: stitched outline, shadowed opening.  -> value offset."""
    if f != 'front':
        return 0.0
    sx = ctx.cube.sx
    w = ctx.cube.size[0]
    px0 = 2.0 if sx < 0 else w - 7.0
    px1 = px0 + 5.0
    py0, py1 = 2.0, 7.0
    if not (px0 <= lx < px1 and py0 <= ly < py1):
        return 0.0
    if ly < py0 + 1.0:
        return -0.16                                              # the opening
    if lx < px0 + 1.0 or lx >= px1 - 1.0 or ly >= py1 - 1.0:
        return 0.06 if int(lx + ly) % 2 == 0 else -0.04           # stitched patch edge
    return 0.03


def vneck(ctx, x, y):
    """Inside the V of the robe: skin + gold chain above the nightgown's lace neckline, cream cotton below."""
    half = 5.0 * (y - (-1.0)) / (-13.0 - (-1.0))
    if abs(x) > half - 0.2:
        return None
    if y < -9.5:
        c = pick(SKIN, 0.68 + (y + 9.5) * 0.03)
        ax = abs(x)
        if abs(y - (-12.3 + ax * 0.55)) < 0.5 and ax < 3.5:
            c = GOLD[4] if x < 0 else GOLD[3]                     # chain
        if abs(x) < 0.6 and -11.0 < y < -9.5:
            c = GOLD[4] if y < -10 else GOLD[2]                   # the little medal
        return A(c)
    if y < -8.5:
        return A(NIGHTIE[5] if int(x + 20) % 2 == 0 else NIGHTIE[3])     # lace edge
    v = 0.66 - (y + 8.5) * 0.02
    c = pick(NIGHTIE, v)
    gx, gy = int(math.floor(x + 30)), int(math.floor(y + 30))
    if (gx + 2 * gy) % 5 == 0 and gy % 2 == 0:
        c = FLOWER[1]
    elif (gx + 2 * gy) % 5 == 1 and gy % 2 == 0:
        c = LEAF[1]
    return A(c)


def belt_mat(ctx):
    f = ctx.face
    n = nm(ctx)
    lx, ly, lz = local(ctx)
    v = 0.38 + face_light(ctx) * 1.0 + plush(ctx, 3, 0.5)
    if n == 'belt':
        if f in SIDE:
            if ctx.j == 0:
                v += 0.08
            elif ctx.j == ctx.h - 1:
                v -= 0.1
        if f in ('top', 'bottom'):
            return A(pick(ROBE, 0.3))
    if n == 'knot':
        if f == 'front':
            if ctx.i in (0, ctx.w - 1):
                v -= 0.1
            if ctx.j == 1 and 0 < ctx.i < ctx.w - 1:
                v -= 0.08                                         # the cinch of the knot
            if ctx.j == 0:
                v += 0.08
    if n == 'tail' and f in SIDE:
        hgt = ctx.cube.size[1]
        if hgt - ly < 1.0:
            if h2(ctx.i, 0, 9) > 0.5:
                return None                                       # frayed end
            v += 0.08
        if ctx.i == 0 and f == 'front':
            v -= 0.06
    return A(pick(ROBE, v))


# ------------------------------------------------------------------ hair + rollers
def hair_mat(ctx):
    """Dark mahogany hair combed UP into the rollers: strand columns with 2-texel lit segments, dark partings,
    a warm sheen band round the crown, occlusion under the rollers, wispy ends at the nape."""
    f = ctx.face
    n = nm(ctx)
    if n == 'brow':
        return brow_paint(ctx)
    x, y, z = apos(ctx)
    if f == 'bottom':
        return None
    if f == 'front':
        col_ = int(math.floor(x + 8))
        edge_y = -29.0 if col_ in (6, 7) else (-29.6 if col_ in (1, 2, 3, 12, 13, 14) else -29.25)
        if y > edge_y:
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
    if f in SIDE and y < -29.2:
        v -= 0.07                                                 # occlusion under the rollers
    if f == 'back' and y > -21.0:
        v -= 0.06
    if f == 'top':
        if abs(abs(x) - 2.75) < 0.6 or abs(x) > 7.6:
            v -= 0.12                                             # partings between the rollers
    return A(pick(HAIR, v))


# right brow (front face, col 0 = the outer tail out by the temple, col 5 = the inner end): a thin plucked arch,
# thick at the inner end, tapering to a one-row tail
BROW_ART = [
    ".bBBBb",
    "b....B",
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
        return A(HAIR[2] if f == 'top' else SKIN[4])
    # end faces
    inner = (f == 'east') if sx < 0 else (f == 'west')
    if inner:
        return A(HAIR[1])
    return A(HAIR[2]) if ctx.j == 1 else None


def curler_mat(ctx):
    """Pink plastic rollers (two crossed cubes per roller = an octagon), axis z.  End caps: a pink rim with one
    lit arc and a dark hollow core; barrel shaded as a cylinder from each texel's angle round the axis, with rows of
    perforations and the white pick through it."""
    f = ctx.face
    cx, cy, cz = ctx.cube.ctr
    x, y, z = apos(ctx)
    a, b = y - cy, x - cx
    if f in ('front', 'back'):
        r = math.hypot(a, b)
        if r < 0.75:
            return A(CURL[0])                                     # the hollow core
        if r < 1.3:
            return A(CURL[2])                                     # inside of the tube
        lit = (-a - b * 0.5) / max(r, 1e-6)
        v = 0.55 + lit * 0.22 + (0.0 if f == 'front' else -0.1)
        if ctx.cube.part == 'B':
            v -= 0.06
        return A(pick(CURL, v))
    if f == 'top':
        a = -2.6 if ctx.cube.part == 'A' else -1.6
    elif f == 'bottom':
        a = 2.6 if ctx.cube.part == 'A' else 1.6
    elif f == 'west':
        b = -2.6 if ctx.cube.part == 'B' else -1.6
    elif f == 'east':
        b = 2.6 if ctx.cube.part == 'B' else 1.6
    nrm = math.hypot(a, b) or 1.0
    ny, nx = a / nrm, b / nrm
    lam = max(0.0, -ny * 0.85 - nx * 0.35)
    v = 0.28 + lam * 0.62
    if f == 'bottom':
        return A(pick(HAIR, 0.3))                                 # sits on the hair
    along = z - cz
    if -0.98 < ny < -0.55:
        v += 0.1                                                  # specular band along the top
    ang = math.atan2(a, b)
    if int(math.floor(along + 20)) % 2 == 0 and int(math.floor((ang + 4) * 1.6)) % 2 == 0:
        v -= 0.17                                                 # perforations
    if abs(along - ctx.cube.pick_at) < 0.5:
        return A(mix(hx('#f4eef2'), hx('#b9a8b4'), 0.0 if ny < -0.2 else 0.6))   # the white pick
    return A(pick(CURL, v))


# ------------------------------------------------------------------ the face
# 16 x 16: col c <-> x [-8 + c, -7 + c], row r <-> y [-30 + r, -29 + r].  Jaw rows 12..15 exist only for
# cols 1..14 (the jaw is 14 wide).  Brow cubes sit over rows 3-4, the nose over cols 7-8 rows 6-8, the cheek cubes
# over rows 9-11 (cols 1-4 / 11-14; the left one is the dollop of face cream).
#   digits skin ramp  w specular  k crease  L lashes  V/W sclera  I/i iris  g glint  b eye bag  r/R blush
#   c mouth corner  u upper lip  l/q lower lip  s shadow  n nostril  H/h hair  M/m/N face cream
GX0, GY0 = -8.0, -30.0
FACE = [
    # 0123456789012345
    "HHHHHHHHHHHHHHHH",   # r0  y-30  hairline: the hair pulled up into the front roller
    "5678887hh8887765",   # r1  y-29  forehead | the stray curl
    "56788888h8w87765",   # r2  y-28  forehead specular
    "5678888888888765",   # r3  y-27  (brows)
    "5667777887777665",   # r4  y-26  (brows)
    "56ekk76776kke655",   # r5  y-25  lid creases, a trace of yesterday's mauve eyeshadow at the outer corners
    "4LLLLK6776KLLLL4",   # r6  y-24  upper lashes, flicked out at the outer corners, thinner by the nose
    "45WgIW6776WgIW54",   # r7  y-23  eyes
    "45WIiW6776WIiW54",   # r8  y-22
    "45bkkb6nn6bkkb54",   # r9  y-21  lower lids | nostrils  (cheek cubes over cols 1-3 / 12-14, rows 9-11)
    "4wrRc677776cRrw4",   # r10 y-20  cheekbones + blush | the corners of the smile curl up
    "45rr5cuUUuc5rr54",   # r11 y-19  upper lip (cupid's bow), the corners curl up
    "x45556lqql65mN4x",   # r12 y-18  lower lip (jaw cols 4-11) | jowls cols 1-3 / 12-14 | cream drip
    "x45566ssss665m4x",   # r13 y-17
    "x345667ww766543x",   # r14 y-16  chin
    "xxxx45666654xxxx",   # r15 y-15  the chin (jaw only)
]
assert all(len(r) == 16 for r in FACE), [len(r) for r in FACE]


def face_rgba(ch):
    if ch.isdigit():
        return SKIN[int(ch)]
    return {
        'H': HAIR[2], 'h': HAIR[4], 'w': SKIN[9], 'k': SKIN[4], 'L': LASH,
        'W': SCLERA, 'V': SCLERA2, 'I': IRIS, 'i': IRIS2, 'g': GLINT, 'b': mix(SKIN[5], hx('#8a6a8a'), 0.25),
        'r': mix(SKIN[6], hx('#e0707a'), 0.4), 'R': mix(SKIN[6], hx('#e0707a'), 0.6), 'c': LIP[0],
        'u': LIP[1], 'U': LIP[2], 'l': LIP[3], 'q': LIP[4], 'e': mix(SKIN[6], hx('#8a5a9a'), 0.3), 'K': mix(LASH, SKIN[4], 0.45), 's': SKIN[4], 'n': SKIN[2],
        'M': CREAM[4], 'm': CREAM[2], 'N': CREAM[1],
    }.get(ch, SKIN[5])


def face_char(x, y):
    c = int(math.floor(x - GX0))
    r = int(math.floor(y - GY0))
    if 0 <= r < len(FACE) and 0 <= c < 16:
        return FACE[r][c]
    return None


def skin_mat(ctx):
    f = ctx.face
    n = nm(ctx)
    x, y, z = apos(ctx)
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    v = 0.62 + face_light(ctx) * 1.0
    if n == 'cheek' and ctx.cube.sx > 0:
        return cream_paint(ctx)
    if n in ('skull', 'jaw', 'cheek', 'jowl') and f == 'front':
        ch = face_char(x, y)
        if ch and ch not in '.x ':
            return A(face_rgba(ch))
    if n == 'cheek':
        if f == 'top':
            return A(SKIN[8])
        return A(pick(SKIN, 0.66 + face_light(ctx)))
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
            if f == 'east' and -21.0 < y < -18.0 and z < -4.0:
                if abs((y + 19.6) - (z + 8.0) * 0.35) < 0.6 or (z < -6.0 and y < -19.0):
                    return A(CREAM[2] if z < -6 else CREAM[1])    # the finger swipe runs back to the ear
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
    if n == 'leg':
        if f in SIDE:
            cd = corner_dist(ctx)
            if cd < 1.0:
                v -= 0.06                                         # round the shin off
            elif f == 'front' and abs(lx - w / 2) < 1.0:
                v += 0.05                                         # lit shin bone
            if f == 'back' and 13.0 < y < 17.0:
                v += 0.03                                         # calf
            if y > 16.5:
                v -= 0.04                                         # ankle into the slipper
        if y < 13:
            v -= 0.15                                             # under the robe and the nightgown
    if n == 'ear':
        v -= 0.04
    return A(pick(SKIN, v))


# the dollop of night cream on her LEFT cheek (front of the left cheek cube, 4 x 3; col 0 = by the nose):
# a thick swirl that catches the light, fading to a thin smear at the edges where the skin shows through
CREAM_ART = [
    "MWm",
    "WMM",
    "NMm",
]


def cream_paint(ctx):
    f = ctx.face
    if f == 'front':
        ch = CREAM_ART[min(ctx.j, 2)][min(ctx.i, 2)]
        return A({'M': CREAM[3], 'W': CREAM[4], 'm': CREAM[2], 'N': CREAM[1], 's': SKIN[6]}.get(ch, SKIN[6]))
    if f == 'top':
        return A(CREAM[4] if ctx.i < 2 else CREAM[3])
    if f == 'west':
        return A(CREAM[2])
    if f == 'east':
        return A(CREAM[1] if ctx.j < 2 else SKIN[5])
    if f == 'bottom':
        return A(CREAM[1] if ctx.i < 2 else SKIN[5])
    return A(pick(SKIN, 0.6 + face_light(ctx)))


# ------------------------------------------------------------------ slippers: two plush dachshund heads
def slipper_mat(ctx):
    f = ctx.face
    n = nm(ctx)
    x, y, z = apos(ctx)
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    v = 0.56 + face_light(ctx) * 1.0 + plush(ctx, 5, 0.6)
    if n == 'ear':
        v -= 0.2
        if f in SIDE and h - ly < 1.0:
            v -= 0.06
        return A(pick(DOG, v))
    if n == 'head':
        if f == 'front':
            # two big black eyes with glints, above the snout
            ci = ctx.i
            if ctx.j in (0, 1) and ci in (1, w - 2):
                if ctx.j == 0 and ci == 1:
                    return A(GLINT)
                if ctx.j == 0 and ci == w - 2:
                    return A(GLINT)
                return A(hx('#120c0c'))
            if ctx.j == 0 and ci in (0, w - 1):
                v -= 0.1
        if f == 'top':
            # the opening round the ankle
            cxl = lx - w / 2
            if abs(cxl) < 3.2 and lz > 2.0 and lz < d - 0.4:
                return A(DOG[1] if abs(cxl) > 2.4 or lz < 2.8 else DOG[0])
            if lz < 1.2 and ctx.i in (1, w - 2):
                return A(DOG[3])                                  # brow fur over the eyes
    if n == 'snout':
        if f == 'front':
            if ctx.j == 0 and 1 <= ctx.i <= w - 2:
                return A(hx('#120c0c') if ctx.i != 1 else hx('#5a4a4a'))    # nose
            if ctx.j == 1 and ctx.i == w // 2:
                return A(hx('#3a1a10'))
            if ctx.j == 2 and 1 <= ctx.i <= w - 2:
                return A(hx('#d86a7a') if ctx.i == w // 2 else pick(DOG, 0.75))   # tongue + muzzle
            v += 0.15
        if f == 'top':
            v += 0.08
            if ctx.j == 0:
                return A(hx('#120c0c'))                           # nose seen from above
    return A(pick(DOG, v))


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
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    v = 0.5 + face_light(ctx) * 1.0
    if f == 'west':
        return A(screen_px(ctx.i, ctx.j, ctx.w, ctx.h) or BEZEL[0])
    if f == 'east':
        # the case back: teal, a camera bump in the top corner, a little daisy sticker
        i, j = ctx.i, ctx.j
        cam = j >= h - 3 and i >= ctx.w - 3
        if cam:
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
    if r == 0:
        return BEZEL[1]
    if r == 1:
        return SCREEN['head'] if c != 1 else SCREEN['logo']
    if r == h - 1:
        return BEZEL[1]
    if r == h - 2:
        return SCREEN['bar']
    rr = r - 2
    if rr in (0, 1) and c <= w - 3:
        return SCREEN['in']
    if rr in (2, 3) and c >= 2:
        return SCREEN['out']
    if rr in (5,) and c <= w - 2:
        return SCREEN['in']
    if rr == 6 and c == w - 1:
        return SCREEN['dot']
    return SCREEN['bg']


def gold_mat(ctx):
    f = ctx.face
    if f in ('west', 'east'):
        return A(GOLD[4] if ctx.j == 0 else GOLD[3])
    return None


def chori_mat(ctx):
    f = ctx.face
    lx, ly, lz = local(ctx)
    d = ctx.cube.size[2]
    v = 0.5 + face_light(ctx) * 1.0
    if f in SIDE + ('top', 'bottom') and f not in ('front', 'back'):
        if lz < 1.0 or d - lz < 1.0:
            return A(hx('#d8c8a0'))                               # twine at both ends
        hh = h2(ctx.i, ctx.j, 21)
        if hh > 0.8:
            return A(hx('#e9c2a6'))                               # fat specks
        if hh < 0.12:
            v -= 0.15
    return A(pick(CHORI, v))


def bread_mat(ctx):
    """Pan francés: a golden crust, darker baked ends, pale scored cuts along the top."""
    f = ctx.face
    lx, ly, lz = local(ctx)
    d = ctx.cube.size[2]
    v = 0.58 + face_light(ctx) * 1.0
    if f in ('front', 'back'):
        return A(pick(BREAD, 0.3 if edge(ctx) == 0 else 0.42))
    end = min(lz, d - lz)
    if end < 2.0:
        v -= 0.16 - end * 0.05
    if f == 'top':
        if int(lz) % 4 == 1 and 0 < lx < ctx.cube.size[0] - 1 and end > 2:
            v += 0.24                                             # scored cuts
    elif f in ('west', 'east') and ctx.j == 0 and int(lz) % 4 == 1 and end > 2:
        v += 0.12
    if f == 'bottom':
        v -= 0.1
    return A(pick(BREAD, v))


def nightie_mat(ctx):
    """Cream cotton nightgown: only the hem shows under the robe -- a scalloped lace edge, tiny lilac flowers."""
    f = ctx.face
    if f in ('top',):
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
    v = 0.62 + face_light(ctx) * 0.8
    c = pick(NIGHTIE, v)
    if (int(u) + 2 * int(ly)) % 5 == 0 and int(ly) % 2 == 0:
        c = FLOWER[1]
    return A(c)


def tissue_mat(ctx):
    if ctx.face not in ('front', 'back'):
        return None
    if ctx.j == 0 and ctx.i in (0, 2):
        return None
    return A(NIGHTIE[5] if (ctx.i + ctx.j) % 2 else NIGHTIE[4])


MATS = {
    'robe': robe_mat, 'belt': belt_mat, 'hair': hair_mat, 'curler': curler_mat, 'skin': skin_mat,
    'slipper': slipper_mat, 'sole': sole_mat, 'phone': phone_mat, 'gold': gold_mat, 'chori': chori_mat,
    'bread': bread_mat, 'tissue': tissue_mat, 'brow': hair_mat, 'nightie': nightie_mat,
}


def marta_mat(ctx):
    return MATS[kind(ctx)](ctx)


def phone_glow(img, u0, v0, w, h):
    px = img.load()
    for j in range(h):
        for i in range(w):
            c = screen_px(i, j, w, h)
            if c is not None and c not in BEZEL:
                px[u0 + i, v0 + j] = c


DEFAULT_MAT = marta_mat
FOCUS = 'head'

# ------------------------------------------------------------------ toggles (Java: ModelPart.visible)
TOGGLE_DEFAULT = {'chorizo': False, 'bread': False}
POSE_TOGGLES = {'throw': {'chorizo': True}}


class MartaModel(Model):
    """Exports every bone to Java; the preview JSON hides the toggle bones the current pose does not show."""
    visible = None

    def to_json(self):
        d = super().to_json()
        if self.visible is None:
            return d
        for bd in d['bones']:
            if bd['name'] in TOGGLE_DEFAULT and bd['name'] not in self.visible:
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


def solve_arm(roots, side, wrist, hand_R=None, elbow_hint=None, rots=None, guess=(-30, 0, 0, -60)):
    """Arm (x, y, z) + forearm x (degrees) putting the hand pivot on `wrist` (world); then the hand rotation so
    the hand's world orientation is hand_R.  Returns {bone: rot}."""
    from scipy.optimize import minimize
    rots = dict(rots or {})
    arm, fa, hand = f'{side}_arm', f'{side}_forearm', f'{side}_hand'
    target = np.array(wrist, float)

    def chain(p):
        rr = dict(rots)
        rr[arm] = (p[0], p[1], p[2])
        rr[fa] = (p[3], 0, 0)
        W = fk(roots, rr)
        return W, W[hand][:3, 3], W[fa][:3, 3]

    def cost(p):
        W, w, e = chain(p)
        c = float(np.sum((w - target) ** 2))
        if elbow_hint is not None:
            c += 0.02 * float(np.sum((e - np.array(elbow_hint, float)) ** 2))
        c += 1e-5 * (p[1] ** 2 + p[2] ** 2) + (0.01 * p[3] ** 2 if p[3] > 0 else 0.0)
        return c
    best = None
    for g in (guess, (guess[0] - 30, guess[1], guess[2] + 20, guess[3] + 20), (guess[0] + 20, guess[1] - 20, guess[2], guess[3] - 30)):
        res = minimize(cost, list(g), method='Nelder-Mead', options={'xatol': 1e-4, 'fatol': 1e-9, 'maxiter': 6000})
        if best is None or res.fun < best.fun:
            best = res
    p = best.x
    out = {arm: (p[0], p[1], p[2]), fa: (p[3], 0, 0)}
    if hand_R is not None:
        rr = dict(rots)
        rr.update(out)
        W = fk(roots, rr)
        out[hand] = _euler(W[fa][:3, :3].T @ hand_R)
    return out


# ------------------------------------------------------------------ rest pose (degrees)
# Right arm hangs relaxed, a little out and forward.  Left arm: the hand in front of the chest, palm towards her,
# fingers up, holding the phone screen-to-her so the teal case faces out -- solved with solve_arm() for the wrist
# (6, -1, -12.5), palm facing (0.15, -0.25, 1), fingers along (-0.35, -1, -0.15), elbow out by (16, -2, -2).
ARM_REST = {
    'right_arm': (-4.0, 0.0, 7.0), 'right_forearm': (-14.0, 0.0, 0.0), 'right_hand': (0.0, 10.0, 0.0),
    'left_arm': (-30.24, 37.39, -13.01), 'left_forearm': (-52.51, 0.0, 0.0), 'left_hand': (-88.67, -5.09, 64.52),
}
LAPEL_ROT = 22          # deg, the shawl collar's lapels close into a V at the belt
SKIRT_FLARE = 3         # deg, the wrap skirt panels open out to the hem
TOES_OUT = 8            # deg, duck stance in the dog slippers
BROW_WORRY = 10         # deg, inner ends of the brows raised at rest (she is always a little worried)


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
        for kk, vv in attrs.items():
            setattr(c, kk, vv)
        return c

    # ---------------- body (pivot at the hips)
    bone('body', (0, 2, 0))
    box('body', (-10, -12, -6), (20, 7, 12), 'robe', 'torso')
    box('body', (-9, -5, -5.5), (18, 4, 11), 'robe', 'waist')
    box('body', (-8, -9.5, -8), (16, 6, 2), 'robe', 'bust')
    box('body', (-9.5, -3, -7.5), (19, 2, 13), 'belt', 'belt', inflate=0.25)
    box('body', (-0.5, -3.7, -10.7), (5, 3, 2), 'belt', 'knot')
    box('body', (-7, -16, 2.5), (14, 5, 4), 'robe', 'collar')
    box('body', (-6.5, -12.5, 6), (13, 9, 2), 'robe', 'hood')
    box('body', (-8.5, -14, -5), (3, 3, 8), 'robe', 'collar')
    box('body', (5.5, -14, -5), (3, 3, 8), 'robe', 'collar')

    for side, sx in (('right', -1), ('left', 1)):
        lb = f'lapel_{side}'
        bone(lb, (6.5 * sx, -13, -6.5), 'body', rot=(-8, 0, LAPEL_ROT * sx))
        box(lb, (6.5 * sx - 1.5, -13, -8), (3, 13, 3), 'robe', 'lapel', sx=sx)

    bone('skirt_right', (-5.5, -1, 0), 'body', rot=(-2, 0, SKIRT_FLARE))
    box('skirt_right', (-11, -1, -7), (11, 12, 10), 'robe', 'skirt', sx=-1)
    box('skirt_right', (-8.5, -0.5, -7.25), (3, 3, 0), 'tissue', 'tissue')
    bone('skirt_left', (5.5, -1, 0), 'body', rot=(-2, 0, -SKIRT_FLARE))
    box('skirt_left', (-2, -1, -8), (13, 12, 10), 'robe', 'skirt', sx=1)
    bone('skirt_back', (0, -1, 3), 'body', rot=(5, 0, 0))
    box('skirt_back', (-11, -1, 2.5), (22, 12, 4), 'robe', 'skirt', sx=0)

    # the nightgown's lace hem peeks out under the robe
    box('body', (-9.5, 7, -6), (19, 6, 11), 'nightie', 'nightie')

    bone('belt_tails', (2, -1, -10), 'body', rot=(-4, 0, 0))
    box('belt_tails', (0.2, -1.4, -10.4), (2, 10, 1), 'belt', 'tail')
    box('belt_tails', (2.6, -1.4, -10.2), (2, 8, 1), 'belt', 'tail')

    # ---------------- neck + head (face 16 x 16: skull 12 rows + jaw 4)
    bone('neck', (0, -11, 0), 'body')
    box('neck', (-3.5, -17.5, -3), (7, 7, 6), 'skin', 'neck')
    bone('head', (0, -17, 0), 'neck')
    box('head', (-8, -30, -8), (16, 12, 16), 'skin', 'skull')
    box('head', (-8, -30, -8), (16, 12, 16), 'hair', 'hair', inflate=0.5)
    box('head', (-1, -24, -10), (2, 3, 2), 'skin', 'nose')
    box('head', (-7, -21, -9), (3, 3, 1), 'skin', 'cheek', sx=-1)
    box('head', (4, -21, -9), (3, 3, 1), 'skin', 'cheek', sx=1)
    box('head', (-9, -23, -1), (1, 4, 3), 'skin', 'ear')
    box('head', (8, -23, -1), (1, 4, 3), 'skin', 'ear')
    box('head', (-9.4, -19.5, -0.5), (0, 3, 2), 'gold', 'earring')
    box('head', (9.4, -19.5, -0.5), (0, 3, 2), 'gold', 'earring')
    box('head', (-7, -18, -8), (3, 3, 9), 'skin', 'jowl', sx=-1)
    box('head', (4, -18, -8), (3, 3, 9), 'skin', 'jowl', sx=1)
    bone('jaw', (0, -18, 2), 'head')
    box('jaw', (-4, -18, -8), (8, 4, 10), 'skin', 'jaw')
    bone('right_brow', (-4, -26, -8.5), 'head', rot=(0, 0, -BROW_WORRY))
    box('right_brow', (-7, -27, -9), (6, 2, 1), 'brow', 'brow', sx=-1)
    bone('left_brow', (4, -26, -8.5), 'head', rot=(0, 0, BROW_WORRY))
    box('left_brow', (1, -27, -9), (6, 2, 1), 'brow', 'brow', sx=1)

    # five rollers, all along z so their round ends face the camera: three over the crown (the middle one rides
    # higher), one over each temple
    bone('curlers', (0, -30, 0), 'head')
    ROLLERS = ((-5.5, -30.2, -2.5, 9), (0.0, -31.1, -2.5, 10), (5.5, -30.2, -2.5, 9),
               (-9.0, -26.5, -0.5, 8), (9.0, -26.5, -0.5, 8))
    for k, (cx, cy, cz, ln) in enumerate(ROLLERS):
        box('curlers', (cx - 1.5, cy - 2.5, cz - ln / 2), (3, 5, ln), 'curler', 'curler', axis='z', part='A',
            ctr=(cx, cy, cz), pick_at=(1.5 if k % 2 else -1.5), ln=ln)
        box('curlers', (cx - 2.5, cy - 1.5, cz - ln / 2 + 0.5), (5, 3, ln - 1), 'curler', 'curler', axis='z',
            part='B', ctr=(cx, cy, cz), pick_at=(1.5 if k % 2 else -1.5), ln=ln)

    # ---------------- arms (authored hanging; bent by the bone rotations)
    for side, sx in (('right', -1), ('left', 1)):
        arm, fa, hand = f'{side}_arm', f'{side}_forearm', f'{side}_hand'
        ax = 13.0 * sx
        bone(arm, (10.5 * sx, -10, 0), 'body', rot=ARM_REST[arm])
        box(arm, (ax - 3.5, -13, -3.5), (7, 11, 7), 'robe', 'sleeve_up')
        bone(fa, (ax, -2.5, 0), arm, rot=ARM_REST[fa])
        box(fa, (ax - 3, -3, -3), (6, 7, 6), 'robe', 'sleeve_lo')
        box(fa, (ax - 4, 2.5, -4), (8, 4, 8), 'robe', 'cuff')
        box(fa, (ax - 1.5, 5, -1.5), (3, 3, 3), 'skin', 'wrist')
        bone(hand, (ax, 7.5, 0), fa, rot=ARM_REST[hand])
        box(hand, (ax - 1.5, 7, -2.5), (3, 4, 5), 'skin', 'palm')
        box(hand, (ax - 1 - 0.6 * sx, 7.6, -3.9), (2, 3, 2), 'skin', 'thumb')
        if sx < 0:
            bone('right_index', (ax, 11, -1.5), hand)
            box('right_index', (ax - 1, 11, -2.5), (2, 6, 2), 'skin', 'finger')
            bone('right_fingers', (ax, 11, 1), hand)
            box('right_fingers', (ax - 1, 11, -0.5), (2, 4, 3), 'skin', 'fingers')
            bone('chorizo', (ax, 10, 0), hand)
            box('chorizo', (ax - 1.5, 8.5, -7), (3, 3, 12), 'chori', 'chorizo')
            bone('bread', (ax, 10, 0), hand)
            box('bread', (ax - 2, 8, -8), (4, 4, 15), 'bread', 'bread')
        else:
            box(hand, (ax - 1, 11, -2.5), (2, 4, 5), 'skin', 'fingers')
            bone('phone', (ax - 2, 12, 0), hand)
            box('phone', (ax - 2.5, 9, -3), (1, 10, 6), 'phone', 'phone',
                decals={'eyes:west': phone_glow})

    # ---------------- legs (duck stance) + plush dachshund slippers
    for side, sx in (('right', -1), ('left', 1)):
        leg = f'{side}_leg'
        lxc = 4.5 * sx
        bone(leg, (lxc, 2, 0), 'body', rot=(0, -TOES_OUT * sx, 0))
        box(leg, (lxc - 2.5, 2, -2.5), (5, 19, 5), 'skin', 'leg')
        box(leg, (lxc - 3, 18, -4), (6, 5, 7), 'slipper', 'head')
        box(leg, (lxc - 2, 20, -9), (4, 3, 5), 'slipper', 'snout')
        box(leg, (lxc - 4, 18.5, -3), (1, 5, 3), 'slipper', 'ear')
        box(leg, (lxc + 3, 18.5, -3), (1, 5, 3), 'slipper', 'ear')
        box(leg, (lxc - 3.5, 23, -9.5), (7, 1, 13), 'sole', 'sole')

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
# Authored as world-space targets (texels, rest frame) and solved with solve_arm(); the table below is the solver's
# output (python3 tools/models/ent_marta.py --solve re-solves and prints it).  Per pose:
#   'add': bone -> degrees added to the rest rotation, 'off': bone -> (dx, dy, dz) texels,
#   'ik':  (side, wrist target, world direction the palm faces, world direction the fingers point, elbow hint,
#           solver guess (arm x, y, z, forearm x)).
POSE_TARGETS = {
    # hands wringing: the left hand clutches the phone to her belly, the right hand covers it and rubs
    'idle_nervous': {
        'add': {'head': (4, 0, 6), 'right_brow': (0, 0, -6), 'left_brow': (0, 0, 6)},
        'ik': [
            ('left', (4.0, -1.5, -11.5), (0.05, -0.3, 1.0), (-1.0, -0.6, 0.0), (15, -3, -3), (-30, 20, -10, -60)),
            ('right', (-4.5, -2.5, -14.0), (0.1, -0.2, 1.0), (1.0, -0.5, 0.0), (-15, -3, -3), (-30, -20, 10, -60)),
        ],
    },
    # hands up to her face (palms on the cheeks, fingers up), mouth open, brows up, leaning back
    'scared': {
        'add': {'head': (-8, 0, 0), 'jaw': (24, 0, 0), 'right_brow': (0, 0, -8), 'left_brow': (0, 0, 8),
                'body': (-4, 0, 0), 'right_leg': (4, 0, 0), 'left_leg': (4, 0, 0)},
        'off': {'right_brow': (0, -1.5, 0), 'left_brow': (0, -1.5, 0), 'curlers': (0, -0.6, 0)},
        'ik': [
            ('right', (-9.5, -12.5, -5.0), (1.0, 0.0, -0.15), (0.1, -1.0, -0.2), (-16, -2, -6), (-40, 0, 20, -120)),
            ('left', (9.5, -12.5, -5.0), (-1.0, 0.0, -0.15), (-0.1, -1.0, -0.2), (16, -2, -6), (-40, 0, -20, -120)),
        ],
    },
    # pointing out (at the window / the doll): right arm out, index straight, the others curled
    'point': {
        'add': {'head': (-2, -14, 0), 'neck': (0, -8, 0), 'jaw': (8, 0, 0), 'right_brow': (0, 0, 10),
                'left_brow': (0, 0, -2), 'right_fingers': (0, 0, -110), 'body': (0, -6, 0)},
        'off': {'left_brow': (0, -0.8, 0)},
        'ik': [
            ('right', (-21.0, -15.0, -11.0), (0.15, 1.0, 0.25), (-0.75, -0.25, -0.62), (-17, -12, -5), (-70, 0, 50, -10)),
        ],
    },
    # holding the phone out to the player, screen to camera; the right index taps the screen
    'show_phone': {
        'add': {'head': (4, 0, 7), 'jaw': (6, 0, 0), 'left_brow': (0, 0, 4), 'right_fingers': (0, 0, -80)},
        'off': {'left_brow': (0, -1.2, 0)},
        'ik': [
            ('left', (9.0, -4.0, -17.0), (-0.25, 0.1, -1.0), (-0.1, -1.0, 0.0), (16, -3, -6), (-60, 0, -10, -40)),
            ('right', (-1.5, -8.0, -11.5), (-0.1, 1.0, 0.3), (0.75, -0.05, -0.65), (-15, -4, -5), (-60, 0, 0, -70)),
        ],
    },
    # overhand throw, wind-up: chorizo cocked behind her head, left arm out front, body twisted back
    'throw': {
        'add': {'body': (-5, 22, 0), 'right_leg': (5, -22, 0), 'left_leg': (5, -22, 0), 'head': (2, -18, 0),
                'neck': (0, -6, 0), 'jaw': (14, 0, 0), 'right_brow': (0, 0, 14), 'left_brow': (0, 0, -14),
                'right_fingers': (0, 0, -95), 'right_index': (0, 0, -85)},
        'ik': [
            ('right', (-15.0, -22.0, 6.5), (0.1, 0.1, -1.0), (0.15, -1.0, 0.45), (-20, -13, 0), (-120, 0, 40, -90)),
            ('left', (14.0, -12.0, -14.5), (-0.4, 0.9, -0.2), (0.25, -0.35, -1.0), (17, -9, -5), (-70, 0, -10, -10)),
        ],
    },
}
POSE_TARGETS['shout'] = {
    'add': {'body': (6, 0, 0), 'right_leg': (-6, 0, 0), 'left_leg': (-6, 0, 0), 'neck': (6, 0, 0),
            'head': (-10, 8, 0), 'jaw': (27, 0, 0), 'right_brow': (0, 0, -6), 'left_brow': (0, 0, 6),
            'right_fingers': (0, 0, -25), 'right_index': (0, 0, -15)},
    'off': {'right_brow': (0, -1.2, 0), 'left_brow': (0, -1.2, 0)},
    'ik': [
        ('right', (-8.5, -13.0, -10.0), (0.9, 0.0, 0.45), (0.1, -0.85, -0.5), (-16, -5, -8), (-90, 0, 20, -90)),
    ],
}


def solve_poses(names=None):
    """Re-solve POSE_TARGETS -> {pose: {bone: (xRot, yRot, zRot, dx, dy, dz)}} (radians / texels, added to rest)."""
    m = build()
    rest = {b.name: tuple(b.rot) for b in m.bones()}
    out = {}
    for name in names or POSE_TARGETS:
        spec = POSE_TARGETS[name]
        rots = dict(rest)
        for b, r in spec.get('add', {}).items():
            rots[b] = tuple(rest[b][i] + r[i] for i in range(3))
        for side, wrist, palm, fing, hint, guess in spec.get('ik', []):
            R = frame((1, 0, 0) if side == 'right' else (-1, 0, 0), palm, (0, 1, 0), fing)
            rots.update(solve_arm(m.roots, side, wrist, R, elbow_hint=hint, rots=rots, guess=guess))
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


POSES = {
    'idle_nervous': {
        'head': (0.0698, 0, 0.1047, 0, 0, 0),
        'right_brow': (0, 0, -0.1047, 0, 0, 0),
        'left_brow': (0, 0, 0.1047, 0, 0, 0),
        'right_arm': (-0.7366, -0.6305, 0.0392, 0, 0, 0),
        'right_forearm': (-0.3971, 0, 0, 0, 0, 0),
        'right_hand': (-0.6856, -0.0595, -0.8867, 0, 0, 0),
        'left_arm': (-0.0751, 0.1801, -0.1079, 0, 0, 0),
        'left_forearm': (-0.0799, 0, 0, 0, 0, 0),
        'left_hand': (0.687, -0.1913, -0.2482, 0, 0, 0),
    },
    'scared': {
        'body': (-0.0698, 0, 0, 0, 0, 0),
        'head': (-0.1396, 0, 0, 0, 0, 0),
        'jaw': (0.4189, 0, 0, 0, 0, 0),
        'right_brow': (0, 0, -0.1396, 0, -1.5, 0),
        'left_brow': (0, 0, 0.1396, 0, -1.5, 0),
        'curlers': (0, 0, 0, 0, -0.6, 0),
        'right_arm': (-0.2505, -0.4473, 0.2728, 0, 0, 0),
        'right_forearm': (-2.2607, 0, 0, 0, 0, 0),
        'right_hand': (-0.2493, -0.5733, 0.5962, 0, 0, 0),
        'left_arm': (0.2075, -0.2053, -0.1679, 0, 0, 0),
        'left_forearm': (-1.5885, 0, 0, 0, 0, 0),
        'left_hand': (1.2982, 0.4876, -1.7223, 0, 0, 0),
        'right_leg': (0.0698, 0, 0, 0, 0, 0),
        'left_leg': (0.0698, 0, 0, 0, 0, 0),
    },
    'point': {
        'body': (0, -0.1047, 0, 0, 0, 0),
        'neck': (0, -0.1396, 0, 0, 0, 0),
        'head': (-0.0349, -0.2443, 0, 0, 0, 0),
        'jaw': (0.1396, 0, 0, 0, 0, 0),
        'right_brow': (0, 0, 0.1745, 0, 0, 0),
        'left_brow': (0, 0, -0.0349, 0, -0.8, 0),
        'right_arm': (-0.3614, 0.6616, 0.9407, 0, 0, 0),
        'right_forearm': (-0.8112, 0, 0, 0, 0, 0),
        'right_hand': (1.0662, -0.5654, -0.8801, 0, 0, 0),
        'right_fingers': (0, 0, -1.9199, 0, 0, 0),
    },
    'show_phone': {
        'head': (0.0698, 0, 0.1222, 0, 0, 0),
        'jaw': (0.1047, 0, 0, 0, 0, 0),
        'left_brow': (0, 0, 0.0698, 0, -1.2, 0),
        'right_arm': (-1.1046, -0.789, 0.6074, 0, 0, 0),
        'right_forearm': (-0.9733, 0, 0, 0, 0, 0),
        'right_hand': (0.6949, -0.9131, -0.6226, 0, 0, 0),
        'right_fingers': (0, 0, -1.3963, 0, 0, 0),
        'left_arm': (-0.6358, -0.5483, 0.5926, 0, 0, 0),
        'left_forearm': (0.8178, 0, 0, 0, 0, 0),
        'left_hand': (-0.508, -0.0411, -2.6066, 0, 0, 0),
    },
    'throw': {
        'body': (-0.0873, 0.384, 0, 0, 0, 0),
        'neck': (0, -0.1047, 0, 0, 0, 0),
        'head': (0.0349, -0.3142, 0, 0, 0, 0),
        'jaw': (0.2443, 0, 0, 0, 0, 0),
        'right_brow': (0, 0, 0.2443, 0, 0, 0),
        'left_brow': (0, 0, -0.2443, 0, 0, 0),
        'right_arm': (-2.0044, 0.3522, -0.3276, 0, 0, 0),
        'right_forearm': (-1.2172, 0, 0, 0, 0, 0),
        'right_hand': (0.3376, -0.719, -0.6296, 0, 0, 0),
        'right_index': (0, 0, -1.4835, 0, 0, 0),
        'right_fingers': (0, 0, -1.6581, 0, 0, 0),
        'left_arm': (0.502, -0.8678, -0.8845, 0, 0, 0),
        'left_forearm': (-0.7237, 0, 0, 0, 0, 0),
        'left_hand': (2.0861, 0.2373, -1.1568, 0, 0, 0),
        'right_leg': (0.0873, -0.384, 0, 0, 0, 0),
        'left_leg': (0.0873, -0.384, 0, 0, 0, 0),
    },
    'shout': {
        'body': (0.1047, 0, 0, 0, 0, 0),
        'neck': (0.1047, 0, 0, 0, 0, 0),
        'head': (-0.1745, 0.1396, 0, 0, 0, 0),
        'jaw': (0.4712, 0, 0, 0, 0, 0),
        'right_brow': (0, 0, -0.1047, 0, -1.2, 0),
        'left_brow': (0, 0, 0.1047, 0, -1.2, 0),
        'right_arm': (-0.7225, -0.2046, 0.5292, 0, 0, 0),
        'right_forearm': (-1.8318, 0, 0, 0, 0, 0),
        'right_hand': (0.0337, 0.2489, 0.4658, 0, 0, 0),
        'right_index': (0, 0, -0.2618, 0, 0, 0),
        'right_fingers': (0, 0, -0.4363, 0, 0, 0),
        'right_leg': (-0.1047, 0, 0, 0, 0, 0),
        'left_leg': (-0.1047, 0, 0, 0, 0, 0),
    },
}

ANIM_NOTES = """
Marta Morales -- animation contract.  Angles in radians, ADDED to the rest pose; offsets (dx, dy, dz) in model
texels at 2x density (inside scale_root: 2 texels = 1 vanilla pixel), in the PARENT bone's space.  t = ageInTicks,
s = walk speed 0..1.  26 bones.  Render type entityCutoutNoCull; one emissive layer 'eyes' (marta_eyes.png) that
holds ONLY the phone screen.  No variants (she is never possessed: one texture, marta.png).

CHARACTER: pure comedy, nervous and caring.  She is never still: small, quick, fidgety motions (hands wringing,
weight shifts, brows popping up), never slow or creepy.  Every reaction is a little too big.

Poses (exported as POSE_IDLE_NERVOUS / POSE_SCARED / POSE_POINT / POSE_SHOW_PHONE / POSE_THROW / POSE_SHOUT):
idle_nervous, scared, point, show_phone, throw, and shout (bonus, for '¡TIRALE ALGO!').  The arm values were solved
with IK from world-space targets (POSE_TARGETS in ent_marta.py; python3 tools/models/ent_marta.py --solve).  Blend
whole tables in and out with ONE weight per pose (lerp every component from 0 to the table value), never bone by
bone, or the hands drift off their targets.  The legs are children of body: every pose that pitches or yaws the body
already counter-rotates right_leg / left_leg so the slippers stay planted.  Keep that pairing in any procedural
lean you add (leg xRot -= body xRot, leg yRot -= body yRot).

Toggles (ModelPart.visible; both hidden by default)
* chorizo -- the chorizo in her right fist.  Visible during 'throw' from the start of the wind-up until the release
  frame (the arm's forward snap), then hidden in the same tick the thrown chorizo item/projectile spawns from the
  right hand.  Used in casa.parrilla ('¡Lo único que lo calma es un choripán! ¡Tomá!').
* bread -- a pan francés in the same fist, for the SECOND throw of that beat (chorizo first, then bread).  Same
  rule: visible through the wind-up, hidden on release.  Never show both at once.
* The phone is not a toggle: it stays in her left hand in every pose (it is part of her).

ROOT
* body -- root at the hips (pivot 0, 2, 0).  It carries the robe torso, the narrower waist, the bust shelf, the belt
  and its knot, the shawl collar ring (back roll + side rolls), the hood lying flat on her back, and the nightgown's
  lace hem under the robe.  Every other bone hangs from it.  Idle: weight shift zRot = sin(t*0.06)*0.025, with the
  legs counter-rotating (leg zRot -= the same).  Walk: bob dy = -abs(sin(walk))*0.6*s, a slight waddle
  zRot = sin(walk)*0.04*s.  Poses: scared xRot -0.0698 (recoils back), point yRot -0.1047 (turns her right shoulder
  in), throw (-0.0873, 0.384) (leans back and twists the throwing shoulder away), shout xRot 0.1047 (leans in).
* lapel_right / lapel_left -- the two sides of the shawl collar.  Rest (-8, 0, -+22) deg makes them roll down from
  the neck to the belt in a V over the nightgown.  Static.  Run: flutter xRot -sin(t*0.9)*0.05*s.
* skirt_right / skirt_left / skirt_back -- the wrap skirt panels, hinged at the belt.  Rest: the fronts tilt
  -2 deg and flare 3 deg out; the back tilts +5 deg.  skirt_left carries the overlap (it wraps over skirt_right,
  with a lighter facing down its edge); skirt_right carries the patch pocket with the tissue.  Walk: the panel
  over the forward leg opens -0.15*s (xRot) and skirt_back swings +0.1*s; idle ripple xRot sin(t*0.08 + k)*0.01
  (k = 0, 1, 2).  scared: skirt_back +0.06 (she jumps).  A body lean does not need skirt compensation.
* belt_tails -- the two hanging ends of the bathrobe belt under the knot (rest xRot -4 deg).  A pendulum that lags
  the body by about 3 ticks: xRot = -0.07 - lag(body pitch + walk bob)*0.6, zRot = lag(body zRot)*0.8.  It swings
  hard on the throw release and on every scared jump.

HEAD
* neck -- takes 30% of head look yaw/pitch.  point yRot -0.1396 and throw yRot -0.1047 (looking where she points or
  throws); shout xRot 0.1047 (neck pushed forward).
* head -- FOCUS bone (pivot 0, -17, 0): the 16 x 16 face, hair shell, nose, the two cheek cubes (the LEFT one is the
  dollop of face cream), ears, gold drop earrings, and the two static jowls beside the jaw.  It tracks the player with 70% of
  the look, yaw clamp +-0.7, pitch -0.35..0.3, and tracks quickly (0.15 rad/tick): she is jumpy.  Idle: a nervous
  tilt zRot sin(t*0.11)*0.04, and every 60-120 ticks a quick double glance (yaw +-0.3 for 6 ticks, back).
  idle_nervous (0.0698, 0, 0.1047): head a little down and tilted.  scared -0.1396 (head jerks back).  point
  (-0.0349, -0.2443, 0) and throw (0.0349, -0.3142, 0) look where the hand goes (the throw yaw cancels the body
  twist).  show_phone (0.0698, 0, 0.1222): a coy 'mirá' tilt.  shout (-0.1745, 0.1396, 0): chin up, projecting.
* jaw -- the chin and lower lip (8 wide) hinged at (0, -18, 2), between the jowls.  Rest closed (polite smile).
  Voice-driven: xRot = amp*0.3, max 0.3.  She talks fast: let the envelope be choppy.  Pose values: scared 0.4189
  (scream, a round O with upper/lower teeth and a tongue), shout 0.4712 (widest), throw 0.2443 ('¡TOMÁ!'), point
  0.1396 ('¡Ahí!'), show_phone 0.1047 ('mire, mire').  Never above 0.5: the lower teeth would leave the jowls.
* right_brow / left_brow -- expressive thin arched brows (6 x 2 bars, pivots at their centres), rest zRot -+10 deg
  (inner ends up: worried).  Sign rule: zRot NEGATIVE on right_brow and POSITIVE on left_brow raise the inner ends
  (worry/fear); the opposite lowers them (anger/determination); dy < 0 lifts the whole brow (surprise).  Values:
  idle_nervous -+0.1047 (more worried); scared -+0.1396 with dy -1.5 (both shoot up); point right +0.1745 / left
  (-0.0349, dy -0.8) (one down, one up: urgent); show_phone left (0.0698, dy -1.2) (one brow raised: 'mirá esto');
  throw +-0.2443 (both inner ends down: determined); shout -+0.1047 with dy -1.2.  Talking: on stressed syllables
  pop both brows dy -0.6 for 3 ticks.  The FACE grid draws no eyebrows of its own: these bones are her eyebrows.
* curlers -- the five pink rollers (three over the crown, one over each temple; each is two crossed cubes, an
  octagon).  Secondary motion only: spring-lag the head's pitch/yaw by 2 ticks (xRot/zRot up to +-0.05, a quick
  jiggle, critically damped).  scared dy -0.6 (they jump with her), then they wobble back.  Never animate them on
  their own.

ARMS -- right_* is -X (viewer's left).  Rest: the right arm hangs relaxed (a little out and forward); the left hand
holds the phone in front of her chest, screen towards her, so the teal case faces out.
* right_arm / right_forearm / right_hand -- the free hand: it wrings, points, throws, cups the mouth, and holds the
  chorizo / bread toggles.  Walk: right_arm xRot = -sin(walk)*0.6*s.  Idle (layered on idle_nervous): wringing,
  right_hand zRot += sin(t*0.45)*0.25 and right_forearm xRot += sin(t*0.45 + 1)*0.06.  The pose values are
  solved, so blend them as whole tables.
* right_index -- the straight index finger (2 x 6, own bone so 'point' keeps it straight while the others curl).
  throw -1.4835 (curled round the chorizo), shout -0.2618 (cupped).  In 'point', add a jab: xRot -0.15 then back
  over 4 ticks on each '¡Ahí!'.
* right_fingers -- middle, ring and little finger (2 x 4 x 3).  zRot NEGATIVE curls them into the palm.  point
  -1.9199 (fist behind the index), show_phone -1.3963 (fist, index points at the screen), throw -1.6581 (grip),
  shout -0.4363 (cupped hand).
* left_arm / left_forearm / left_hand -- the phone hand.  Walk: half swing, left_arm xRot = sin(walk)*0.3*s (she
  does not let go of the phone).  idle_nervous pulls the phone against her belly with the right hand over it;
  scared presses the phone to her left cheek as both hands fly to her face (the classic 'Ay, Dios mío' with a call
  on); show_phone holds it out at chest height with the screen to the player; throw swings it forward for balance.
* phone -- the smartphone in the left hand (teal case, camera bump, daisy sticker; the screen is the cube's west
  face).  Static on the hand.  'eyes' layer = the lit screen: always on, full-bright.  casa.ya_llego: when the
  message from the unknown number arrives, flash the eyes layer to alpha 1.0 with a 2-tick white-out, then
  hold.  If Java dims emissives, keep the screen at least 0.8 at night: it lights her face from below in
  show_phone, which is the shot.

LEGS
* right_leg / left_leg -- bare shins and the dachshund-head slippers (eyes, nose, tongue, floppy ears, cream sole);
  duck stance (rest yRot right +8 deg, left -8 deg: toes out).  Walk: xRot = +-sin(walk)*0.55*s (short, quick steps, a slipper shuffle: no knee
  bone).  Pose values only counter-rotate the body lean (scared +0.0698, throw (0.0873, -0.384), shout -0.1047).
  Idle: every 80-160 ticks tap one slipper (leg xRot -0.12 for 3 ticks, back): impatience.

POSES -- what each one is for, and how it moves.
* idle_nervous -- the default idle (blend weight 1 whenever she has nothing else to do).  Hands wringing at her belly
  round the phone, head down and tilted, brows extra worried.  Layer the wringing, the weight shift, the head
  glances and the slipper taps on top.  casa.llegada: 'Ay, gracias a Dios... pase, pase... y límpiese los pies.'
* show_phone -- casa.ya_llego: holds the family chat out to the player, one brow up, the right index pointing at
  the screen.  Blend in over 8 ticks and hold while the chat screen is open; small 'look' nods (head xRot
  +0.05 every 30 ticks).  When she says '...Lucía no tiene celular.', blend 40% of 'scared' on top for the rest of
  the line (the brows shoot up, the jaw drops a little, she pulls the phone back).
* point -- '¡Esas sillas eran de mi suegra!' (casa.cocina), '¡Te dije que no comas tanto chorizo!' (casa.jorge), and
  pointing the player at the window / the doghouse.  Snap in over 3 ticks, hold, and jab the index on each stress.
  To aim it, add yaw to body (and counter-yaw the legs) rather than editing the arm values.
* scared -- every scare she witnesses (the flying plate, the chair tower, Choripán's demon form, the cumbia
  stopping).  SNAP in 2 ticks with a jump: body dy -1.0 at tick 1 back to 0 by tick 4, curlers dy -0.6 with a
  wobble.  Hold with a tremble (body zRot sin(t*1.7)*0.02, jaw += sin(t*2.1)*0.03), and ease out over 12 ticks.
* throw -- casa.parrilla: the wind-up of an overhand throw through the kitchen window (chorizo cocked behind her
  head, the phone arm out front, body twisted back).  Animate: 0 -> table over 8 ticks (wind-up, chorizo visible),
  hold 4, then RELEASE over 3 ticks: right_arm xRot table -> table + 1.1 (the arm whips forward and down into the
  follow-through), right_forearm -> 0 (straightens), body yRot table -> table - 0.6 (the shoulders unwind), and to
  keep the slippers planted and her eyes on the window, both legs yRot += 0.6 and head yRot += 0.6.  The arm passes
  the release point at about table + 0.6.  On that tick hide the chorizo and spawn the projectile at the right
  hand's world position (verified render: the follow-through ends with the fist by her right hip).  Ease back to
  idle over 10 ticks.  Repeat with the bread.
* shout -- casa.trae: '¡TIRALE ALGO!' from another room: leaning in, right hand cupped at the mouth, chin up, jaw
  wide.  Blend in over 4 ticks, hold for the line, out over 8.

LAYERING
idle = idle_nervous + wringing + weight shift + glances + slipper taps.  Talking adds the jaw and brow pops on top
of any pose.  Walking adds the leg / arm swing and the skirt / belt-tail secondary motion; while walking, blend
idle_nervous down to 0.5 so the right arm can swing.
"""


if __name__ == '__main__':
    if '--solve' in sys.argv:
        for k, v in solve_poses().items():
            print(k, v)
