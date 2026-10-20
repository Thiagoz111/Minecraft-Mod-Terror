"""Choripan, version completa -- the possessed family dachshund, stretched into a 4.5-block demon (DEAD LINE).

Authored at 2x texel density (model.scale = 0.5).  +Y down, ground y = 24, faces -Z, right_* on -X.

Design
------
Silhouette (side): a sausage dog pulled like taffy.  From the nose (z ~ -75) to the tail tip (z ~ +78)
the body is a CHAIN: the head on a raised, stretched neck, the chest (seg1, still wearing what is left of
the Nona's red sweater) on two short, bowed, perfectly normal dachshund legs, then five short fur
"links" (seg2..seg6) and the rump (hips), each link separated from the next by a band of stretched,
hairless pink-grey skin with ribs pushing through as ridges.  The back is a gentle arch.  Three pairs of
thin, far-too-long HUMAN arms grow out of the flanks of seg3, seg5 and the hips: elbows jut up above
the spine like a spider's knees, forearms come down to flat palms with long fingers on the floor.  The
tiny dachshund tail still sticks up at the end and wags.

Silhouette (front): a cute dog face (huge round eyes, split nose) on a long muzzle, two absurdly long
ears hanging almost to the ground like curtains, and the six arms fanning out behind it.

Face (the clip close-up and the jumpscare portrait):
* the eyes stay BIG and round (6x6 bulging discs, black lid ring, tan "puppy brow" dots) but are milk
  white, cataract-veined, with a tiny red pinpoint pupil each, both looking slightly inward (derp);
  emissive layer 'eyes' = the milk white (dim) + the red pinpoints (full bright);
* the muzzle splits from the nose to the throat into four flaps (jaw_upper_right/left,
  jaw_lower_right/left): the black nose is cut in half with raw red cut faces, black dog lips, a
  1-texel slit of interlocking needle teeth (zero-thickness planes) all along the lips, overbite fangs
  outside, red gums, a ridged palate, a deep red cavity inside the skull ending in a black throat;
* a long black tongue (tongue + tongue_tip) lolls out of the front like a panting dog.
Palette: red-brown coat ramp #7a3a1c -> #c06a33 (darker back stripe), stretched skin pink-grey with
purple shadows and blue veins, bone-pale rib ridges, raw red torn edges, red cable-knit sweater with a
white "C", a light-blue (celeste) collar with a brass tag.
"""
import math

import numpy as np

from mcmodel import Model, hash3, face_light, pick, rot_matrix
from rig import Rig
from paint import hx, mix


def pal(*h):
    return [hx(c) for c in h]


# ------------------------------------------------------------------ palettes (dark -> light, hue shifted)
FUR = pal('#260b07', '#3f150b', '#5c2111', '#7a3a1c', '#8f4622', '#a6552a', '#c06a33', '#d88a4c', '#ecab6c')
TAN = pal('#a8642e', '#c88446', '#dea263')
SKIN = pal('#2c1d2a', '#4a3442', '#6c5260', '#8f737c', '#ad9096', '#c7aaab', '#dcc2bd', '#ecd9d0')
VEIN = pal('#3a3463', '#544a86', '#6b4f7c')
BONE = pal('#8c7f72', '#bdb1a2', '#e2d8c8', '#f6efe2')
RAW = pal('#2e050b', '#561019', '#80202a', '#a8383e', '#c95a5a', '#e08a82')
GUM = pal('#300510', '#5a0c1c', '#8a1628', '#b52a38', '#d4484e', '#e8706c')
TEETH = pal('#5a5244', '#9a917c', '#d4ccb6', '#f2ecdc', '#fffdf4')
TONGUE = pal('#030205', '#0a080e', '#141019', '#211b28', '#332b3d', '#4f4660', '#7a7090')
THROAT = pal('#000000', '#0c0105', '#1e040a', '#3a0812', '#5c0f1b')
NOSE = pal('#050406', '#0e0c12', '#1a1820', '#2c2a36', '#4e4c5e', '#9a98b0')
LIP = pal('#08060a', '#16121a', '#2a2228')
MILK = pal('#5e6672', '#8a939c', '#b2bac0', '#cfd5d8', '#e4e8e8', '#f3f5f2', '#ffffff')
PUPIL = hx('#ff1e12')
PUPIL_D = hx('#9a0c0c')
BLOODSHOT = hx('#c4706c')
KNIT = pal('#22040a', '#3e0810', '#5e0e18', '#7e1620', '#9e2228', '#bb3432', '#d24e44', '#e47060')
KNIT_W = pal('#8f877e', '#bfb7ab', '#e3dccf', '#f6f1e6')
CELESTE = pal('#1d3a5c', '#2f5f8f', '#4f8fc4', '#75b2e2', '#a4d2f2')
BRASS = pal('#3b2a10', '#7a5a22', '#b8913e', '#e6c66a', '#fff0b0')
PAD = pal('#120c0e', '#241a1c', '#3a2c2c', '#544040')
NAIL = pal('#1a1410', '#3c3228', '#6e6250', '#a29478')
DIRT = hx('#2a1d14')


def clamp(v, a=0.0, b=1.0):
    return a if v < a else b if v > b else v


# ------------------------------------------------------------------ texel helpers
def local(ctx):
    """Texel centre in cube-local texel units (independent of bone rotation)."""
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


def A(ctx):
    """Absolute authoring coordinates (rest pose, before any bone rotation)."""
    lx, ly, lz = local(ctx)
    o = ctx.cube.a0
    return o[0] + lx, o[1] + ly, o[2] + lz


def edge(ctx):
    return min(ctx.i, ctx.j, ctx.w - 1 - ctx.i, ctx.h - 1 - ctx.j)


def tag(ctx):
    return ctx.cube.name or ''


def cseed(ctx):
    o, sz = ctx.cube.a0, ctx.cube.size
    return int(abs(o[0]) * 13.1 + abs(o[1]) * 7.3 + abs(o[2]) * 3.7 + sz[0] * 31 + sz[1] * 17 + sz[2] * 5) % 9973


def is_plane(ctx):
    return 0 in ctx.cube.size


def at(points):
    """Decal painting single texels: points = [(i, j, rgba), ...] relative to the face rect."""
    def fn(img, u0, v0, w, h):
        px = img.load()
        for i, j, c in points:
            if 0 <= i < w and 0 <= j < h:
                px[u0 + i, v0 + j] = c
    return fn


# ------------------------------------------------------------------ fur
def strands(across, along, seed, clump=2.0, brk=3.5):
    """Directional fur: clumps `clump` texels wide, broken every ~`brk` texels along the lay."""
    col = math.floor(across / clump)
    off = hash3(col, 7, 0, seed) * brk
    k = hash3(col, math.floor((along + off) / brk), 0, seed)
    v = (k - 0.5) * 0.2
    if (along + off) % brk < 0.9:
        v -= 0.06                                   # the dark root line of each clump
    return v


def fur_val(ctx, base=0.5):
    """Body fur value: lay runs along Z on the trunk (nose -> tail)."""
    x, y, z = A(ctx)
    f = ctx.face
    v = base + face_light(ctx) * 1.1
    s = cseed(ctx) % 7
    if f in ('west', 'east'):
        v += strands(y, z, 11 + s)
        v -= clamp((y - (ctx.cube.a0[1] + ctx.cube.size[1] * 0.55)) / 6.0) * 0.12   # belly side darker
    elif f in ('top', 'bottom'):
        v += strands(x, z, 21 + s)
    else:
        v += strands(x, y, 31 + s, 2.0, 3.0)
    if f == 'top' and abs(x) < 2.6:
        v -= 0.14                                   # darker back stripe
    if edge(ctx) == 0 and not is_plane(ctx):
        v -= 0.06
    return v


def torn_fur(ctx, v):
    """Torn ends of a fur link: a ragged rim of dark fur tips and raw red flesh where the skin was pulled out."""
    c = ctx.cube
    lx, ly, lz = local(ctx)
    w, h, d = c.size
    f = ctx.face
    tf, tb = getattr(c, 'tear', (False, False))
    if f in ('front', 'back'):
        torn = tf if f == 'front' else tb
        if not torn:
            return pick(FUR, v)
        e = edge(ctx)
        if e == 0:
            return pick(FUR, v - 0.12)
        if e == 1 and hash3(ctx.i, ctx.j, cseed(ctx), 5) > 0.45:
            return pick(FUR, v - 0.22)
        return pick(RAW, 0.65 - e * 0.12 + hash3(ctx.i, ctx.j, 3, 9) * 0.15)
    across = lx if f in ('top', 'bottom') else ly
    for torn, dist in ((tf, lz), (tb, d - lz)):
        if not torn:
            continue
        jag = 0.5 + hash3(math.floor(across), cseed(ctx), 1 if torn is tf else 2, 13) * 1.9
        if dist < jag - 0.9:
            return pick(RAW, 0.55 + hash3(math.floor(across), 2, 3, 4) * 0.25)
        if dist < jag:
            return pick(FUR, v - 0.2)
    return pick(FUR, v)


def fur_mat(ctx):
    t = tag(ctx)
    v = fur_val(ctx, 0.52)
    if t in ('core', 'cap', 'keel', 'rump'):
        if t == 'keel':
            v -= 0.06
        return torn_fur(ctx, v)
    return pick(FUR, v)


def leg_fur(ctx):
    """Dachshund legs and tail: fur laid along the limb, darker at the back, short and shiny."""
    x, y, z = A(ctx)
    f = ctx.face
    t = tag(ctx)
    v = 0.52 + face_light(ctx) * 1.1
    if f in ('front', 'back', 'west', 'east'):
        v += strands(x + z, y, 41 + cseed(ctx) % 5, 1.5, 3.0)
    else:
        v += strands(x, z, 47)
    if edge(ctx) == 0 and not is_plane(ctx):
        v -= 0.06
    if t == 'tail':
        if f == 'top':
            v -= 0.12
        return pick(FUR, v)
    return pick(FUR, v)


def paw_mat(ctx):
    """Cute dachshund paw: rounded toes (dark grooves), black claws at the front, dark pads underneath."""
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    t = tag(ctx)
    v = 0.55 + face_light(ctx) * 1.1
    if f == 'bottom':
        return pick(PAD, 0.3 + (0.3 if (ctx.i + ctx.j) % 3 == 0 else 0))
    if t == 'toes':
        if f in ('front', 'top'):
            if ctx.i in (1, 3) if w == 5 else ctx.i == 2:
                return pick(FUR, v - 0.25)          # grooves between toes
            if f == 'front' and ctx.j == ctx.h - 1:
                return pick(PAD, 0.15 if ctx.i % 2 == 0 else 0.6)   # claw tips
        return pick(FUR, v + 0.04)
    if f == 'top' and lz < 2:
        if ctx.i in (1, 3):
            return pick(FUR, v - 0.22)
    if edge(ctx) == 0:
        v -= 0.06
    return pick(FUR, v)


# ------------------------------------------------------------------ stretched skin
def skin_core(ctx, base=0.55, along_axis='z'):
    x, y, z = A(ctx)
    f = ctx.face
    v = base + face_light(ctx) * 1.0
    if along_axis == 'z':
        across = y if f in ('west', 'east') else x
        along = z
    else:
        across = x + z
        along = y
    # stretch striations: thin darker lines running along the pull
    if math.floor(across) % 3 == 0 and hash3(math.floor(across), math.floor(along / 4), 0, 3) > 0.35:
        v -= 0.07
    # translucent: darker shapes under the skin (organs / rib shadows) on the flanks
    if f in ('west', 'east', 'bottom'):
        blob = hash3(math.floor(along / 3), math.floor(across / 3), cseed(ctx), 17)
        if blob > 0.72:
            v -= 0.1
    # wet sheen along the top
    if f == 'top' and abs(x) < 1.5:
        v += 0.12
    return v


def vein_hit(ctx, along, across, seed):
    p = 1.6 * math.sin(along * 0.55 + seed * 1.7) + 0.8 * math.sin(along * 1.3 + seed)
    c0 = (seed % 5) - 2.0
    return abs(across - c0 - p) < 0.5


def skin_mat(ctx):
    """Stretched, hairless pink-grey skin between the fur links: striated, wet, veined, see-through-ish."""
    x, y, z = A(ctx)
    f = ctx.face
    t = tag(ctx)
    if t == 'arm':
        v = skin_core(ctx, 0.56, 'y')
        lx, ly, lz = local(ctx)
        c = pick(SKIN, v)
        if f in ('front', 'west', 'east', 'back') and vein_hit(ctx, ly, ctx.i, cseed(ctx)):
            c = mix(c, VEIN[1], 0.55)
        return c
    v = skin_core(ctx, 0.55)
    c = pick(SKIN, v)
    if f in ('west', 'east', 'top'):
        across = y if f != 'top' else x
        if vein_hit(ctx, z, across - (ctx.cube.a0[1] + ctx.cube.size[1] / 2 if f != 'top' else 0), cseed(ctx)):
            c = mix(c, VEIN[1] if (cseed(ctx) % 2) else VEIN[2], 0.6)
    return c


def rib_mat(ctx):
    """A rib pushing through the stretched skin: pale ridge crest, dark creases where the skin folds."""
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    if f in ('front', 'back'):
        e = edge(ctx)
        if e == 0:
            return pick(SKIN, 0.62 + face_light(ctx))
        return pick(SKIN, 0.25)                   # crease (mostly hidden inside the tube)
    if f == 'bottom':
        return pick(SKIN, 0.35)
    v = 0.78 + face_light(ctx) * 0.8
    c = pick(SKIN, v)
    if f == 'top' and abs(lx - w / 2) < w * 0.32:
        c = mix(c, BONE[2], 0.55)                 # the bone shows through on the crest
    if f in ('west', 'east') and ly < h * 0.45:
        c = mix(c, BONE[1], 0.35)
    return c


def spike_mat(ctx):
    """A broken rib tip piercing the skin: bone, bloody at the base."""
    lx, ly, lz = local(ctx)
    h = ctx.cube.size[1]
    v = 0.6 + face_light(ctx)
    if ly > h - 1.0:
        return pick(RAW, 0.5)
    return pick(BONE, v)


# ------------------------------------------------------------------ human arms (grown out of the flanks)
def arm_mat(ctx):
    """Long human arm: hairless pink-grey skin, knobbly bone at the elbow, veins, dirty knuckles."""
    f = ctx.face
    t = tag(ctx)
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    v = 0.56 + face_light(ctx) * 0.9
    if edge(ctx) == 0 and not is_plane(ctx):
        v -= 0.05
    if t == 'elbow':
        c = pick(SKIN, v + 0.1)
        if f in ('top', 'front', 'west', 'east') and edge(ctx) > 0:
            c = mix(c, BONE[2], 0.4)                # the bone end straining the skin
        return c
    if t == 'shoulder':
        # where the arm burst out of the dog: torn fur collar around raw skin
        if ly < 1.0 or edge(ctx) == 0:
            return pick(FUR, 0.45 + face_light(ctx) + hash3(ctx.i, ctx.j, 1, 2) * 0.15)
        return pick(RAW, 0.55 + hash3(ctx.i, ctx.j, 2, 3) * 0.2)
    if t in ('upper', 'fore'):
        c = pick(SKIN, v)
        if f in ('front', 'west', 'east', 'back') and vein_hit(ctx, ly, lx + lz, cseed(ctx)):
            c = mix(c, VEIN[1], 0.5)
        if t == 'fore' and ly > h - 3:
            c = mix(c, DIRT, 0.25)                  # filthy wrists
        if t == 'upper' and ly < 2:
            c = mix(c, RAW[3], 0.35)
        return c
    if t == 'palm':
        if f == 'bottom':
            return mix(pick(SKIN, 0.3), DIRT, 0.5)
        c = pick(SKIN, v)
        if f == 'top' and ctx.j <= 1:
            c = pick(SKIN, v - 0.12)                # knuckle row
        return c
    if t in ('finger', 'thumb'):
        if f == 'bottom':
            return mix(pick(SKIN, 0.3), DIRT, 0.5)
        tip = (lz < 1.0) if t == 'finger' else (getattr(ctx.cube, 'tipx', 0) * (lx - w / 2) > 0 and abs(lx - w / 2) > w / 2 - 1)
        if tip:
            return pick(NAIL, 0.55 + face_light(ctx)) if f == 'top' else NAIL[0]   # cracked nail, black dirt
        c = pick(SKIN, v)
        if t == 'finger' and f == 'top' and int(lz) % 3 == 1:
            c = pick(SKIN, v - 0.13)                # extra knuckle creases (one too many)
        return c
    return pick(SKIN, v)


# ------------------------------------------------------------------ sweater (the Nona's red cable knit)
C_ROWS = [
    ".WWW.",
    "WW..W",
    "WW...",
    "WW...",
    "WW..W",
    ".WWW.",
]


def knit_px(i, j, v):
    v += ((0.07, -0.03), (-0.05, 0.05))[j % 2][i % 2]       # V stitches
    cab = i % 7
    if cab in (2, 3, 4):                                       # cable braid every 7 columns
        ph = (j + (cab - 2) * 2) % 6
        v += 0.1 if ph < 2 else (-0.1 if ph == 5 else 0.0)
    elif cab in (1, 5):
        v -= 0.1                                               # purl channels each side of the cable
    return v


def sweater_mat(ctx):
    """Remnant of the sweater around the chest: torn back edge and rips (the fur shows through)."""
    f = ctx.face
    x, y, z = A(ctx)
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    if f == 'bottom':
        # only a strap under the chest between the front legs
        return pick(KNIT, 0.3) if lz < 3 else None
    if f == 'back':
        return None
    v = 0.55 + face_light(ctx) * 1.0
    if f in ('top', 'west', 'east'):
        across = lx if f == 'top' else ly
        rag = 3.5 + hash3(math.floor(across / 1.5), 4, 0, 77) * 4.5
        if d - lz < rag:
            return None                                         # ragged torn back edge
        if d - lz < rag + 1:
            return pick(KNIT, v - 0.25)                         # frayed, stretched last row
        if f == 'top' and (abs(lx - 3) < 1.2 and 3 < lz < 6):
            return None                                         # a rip on the back
        if f in ('west', 'east'):
            # the white "C" on both flanks
            ci = int(lz) - 2 if f == 'east' else int(d - lz) - 4
            cj = int(ly) - 3
            if 0 <= cj < len(C_ROWS) and 0 <= ci < 5:
                ch = C_ROWS[cj][ci if f == 'east' else 4 - ci]
                if ch == 'W':
                    return pick(KNIT_W, 0.6 + face_light(ctx) + (0.1 if cj % 2 else 0))
            if f == 'west' and 2 < ly < 5 and 7.5 < lz < 9.5:
                return None                                     # a rip on the right flank
        if f == 'top':
            v = knit_px(ctx.i, ctx.j, v)
        else:
            v = knit_px(int(lz), ctx.j, v)
        if edge(ctx) == 0 and f != 'top':
            v -= 0.05
        return pick(KNIT, v)
    if f == 'front':
        # turtleneck opening around the neck: a ribbed rim, the neck passes through the middle
        cx, cy = lx - w / 2, ly - h * 0.38
        r = max(abs(cx) / 5.0, abs(cy) / 4.6)
        if r < 1.0:
            return None
        if r < 1.35:
            return pick(KNIT, 0.62 + (0.1 if ctx.i % 2 == 0 else -0.08))   # rib knit collar
        return pick(KNIT, knit_px(ctx.i, ctx.j, v))
    return pick(KNIT, v)


def shred_mat(ctx):
    """Strips of the sweater hanging from the spine: knit, frayed bottoms, loose yarn."""
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    t = tag(ctx)
    if is_plane(ctx):
        if f not in ('west', 'front'):
            return None
        u = ctx.i
        fray = h - 1 - math.floor(hash3(u, cseed(ctx), 0, 31) * 3.2)
        if t == 'yarn':
            return pick(KNIT, 0.55 + (0.12 if ctx.j % 2 else -0.05))
        if ctx.j > fray:
            return None
        if ctx.j == fray:
            return pick(KNIT, 0.32) if u % 2 == 0 else None
        v = knit_px(ctx.i, ctx.j, 0.52 - ctx.j * 0.02)
        return pick(KNIT, v)
    if f == 'bottom':
        return pick(KNIT, 0.3)
    v = 0.55 + face_light(ctx) * 1.0
    return pick(KNIT, knit_px(ctx.i, ctx.j, v))


# ------------------------------------------------------------------ collar + tag
def collar_mat(ctx):
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    t = tag(ctx)
    if t == 'tag':
        if f != 'front':
            return None
        if (ctx.i, ctx.j) in ((0, 0), (ctx.w - 1, 0)):
            return None
        return pick(BRASS, 0.75 if (ctx.i + ctx.j) % 3 == 0 else 0.5)
    if f in ('front', 'back'):
        return None
    v = 0.55 + face_light(ctx) * 1.0
    if edge(ctx) == 0:
        v -= 0.12
    if f == 'bottom' and abs(lx - w / 2) < 1.5:
        return pick(BRASS, 0.6)                     # the ring the tag hangs from
    return pick(CELESTE, v)


# ------------------------------------------------------------------ head
def eye_rows():
    """Big round milk-white eye, 6x6.  '.' = transparent corner (the black lid shows behind)."""
    return [
        ".abba.",
        "aHwcca",
        "bwcccb",
        "bccccb",
        "accccd",
        ".dddd.",
    ]


EYE_COLS = {'a': MILK[2], 'b': MILK[3], 'c': MILK[4], 'w': MILK[5], 'H': MILK[6], 'd': MILK[3]}


def eye_px(i, j, side):
    rows = eye_rows()
    ch = rows[j][i if side == 'r' else 5 - i]
    if ch == '.':
        return None
    c = EYE_COLS[ch]
    pi = 3 if side == 'r' else 2                    # pupils both turned inward (derp)
    if (i, j) == (pi, 3):
        return PUPIL
    if abs(i - pi) + abs(j - 3) == 1:
        c = mix(c, BLOODSHOT, 0.25)                 # faint pink ring round the pinpoint
    # bloodshot threads creeping in from the outer corner
    if side == 'r' and (i, j) in ((0, 3), (1, 3), (1, 4)):
        c = mix(c, BLOODSHOT, 0.55)
    if side == 'l' and (i, j) in ((5, 2), (4, 2), (4, 3)):
        c = mix(c, BLOODSHOT, 0.55)
    return c


def eye_mat(ctx):
    side = getattr(ctx.cube, 'side', 'r')
    if ctx.face == 'front':
        return eye_px(ctx.i, ctx.j, side)
    return LIP[0]


def eye_glow(side):
    pts = []
    for j in range(6):
        for i in range(6):
            c = eye_px(i, j, side)
            if c is None:
                continue
            if c == PUPIL:
                pts.append((i, j, hx('#ff3a24')))
            else:
                pts.append((i, j, (int(c[0] * 0.62), int(c[1] * 0.66), int(c[2] * 0.7), 255)))
    return at(pts)


def skull_mat(ctx):
    """Head fur.  Front: forehead, black lid rings, tan puppy-brow dots; the inside of the mouth cavity is flesh."""
    f = ctx.face
    t = tag(ctx)
    x, y, z = A(ctx)
    lx, ly, lz = local(ctx)
    v = 0.56 + face_light(ctx) * 1.05
    if t == 'skull':
        if f == 'front':
            # eye footprints (x -7..-1 and 1..7, y -12..-6) + 1 texel ring = black lids
            for ex0 in (-7, 1):
                if ex0 - 1 <= x <= ex0 + 7 and -13 <= y <= -6:
                    inner = ex0 <= x <= ex0 + 6 and -12 <= y
                    corner = (x < ex0 or x > ex0 + 6) and (y < -12)
                    if not corner:
                        return LIP[0] if inner else LIP[1]
            # tan puppy brows, raised at the inner ends (sad, cute)
            if (x, y) and -14 <= y < -13 and (-5 <= x < -2 or 2 <= x < 5):
                return TAN[1]
            if -15 <= y < -14 and (-3 <= x < -2 or 2 <= x < 3):
                return TAN[0]
            v += 0.04 - abs(x) / 8 * 0.1
            v += (hash3(math.floor(x / 2), math.floor(y / 2), 1, 61) - 0.5) * 0.12
            return pick(FUR, v)
        if f == 'bottom' and abs(x) < 4 and z < -52:
            # palate: ridged flesh, seen when the jaws open
            return pick(GUM, 0.45 + (0.18 if int(z) % 2 == 0 else -0.05) - abs(x) * 0.04)
        if f == 'top':
            v += strands(x, z, 51)
            if abs(x) < 2.6:
                v -= 0.12
        elif f in ('west', 'east'):
            v += strands(y, z, 53)
        else:
            v += strands(x, y, 55)
        if edge(ctx) == 0:
            v -= 0.05
        return pick(FUR, v)
    if t == 'side':
        inner = (f == 'east' and x < 0) or (f == 'west' and x > 0)
        if inner:
            # cavity wall: red flesh with ridges, darker toward the throat
            return pick(GUM, 0.55 - (z + 60) * 0.04 + (0.1 if int(y) % 2 == 0 else 0))
        if f == 'bottom':
            return pick(FUR, v - 0.05)
        if f == 'front':
            # cheeks beside the muzzle: whisker spots
            c = pick(FUR, v + 0.03 + (hash3(ctx.i, ctx.j, 3, 3) - 0.5) * 0.1)
            if (ctx.i + ctx.j * 2) % 4 == 0 and 1 <= ctx.j <= 4:
                c = pick(FUR, 0.18)
            return c
        v += strands(y, z, 57)
        return pick(FUR, v)
    if t == 'dome':
        v += strands(x, z, 59)
        if abs(x) < 2.6 and f == 'top':
            v -= 0.12
        return pick(FUR, v)
    return pick(FUR, v)


def throat_mat(ctx):
    """The back of the mouth: ribbed red flesh closing to a black throat."""
    f = ctx.face
    if f != 'front':
        return pick(GUM, 0.35) if f == 'top' else THROAT[1]
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    r = max(abs(lx - w / 2) / (w / 2), abs(ly - h * 0.55) / (h * 0.55))
    if r < 0.45:
        return THROAT[0]
    if r < 0.7:
        return THROAT[2 if (ctx.i + ctx.j) % 2 else 1]
    return pick(GUM, 0.2 + (r - 0.7) * 0.9 + (0.12 if ctx.j % 2 == 0 else 0))


def flap_mat(ctx):
    """The four muzzle flaps.  Outside: dog muzzle fur, black lips, whisker spots.  Inside: gums and raw cut faces."""
    f = ctx.face
    c = ctx.cube
    lx, ly, lz = local(ctx)
    w, h, d = c.size
    up = c.upper
    sx = c.sx                                         # -1 right flap (on -X), +1 left flap
    outer_face = 'west' if sx < 0 else 'east'
    seam_face = 'east' if sx < 0 else 'west'
    v = 0.5 + face_light(ctx) * 1.05
    if f == seam_face:
        # the cut: raw flesh with a gum line toward the mouth
        gum_edge = (ly > h - 1.0) if up else (ly < 1.0)
        if gum_edge:
            return pick(GUM, 0.62)
        return pick(RAW, 0.5 + hash3(ctx.i, ctx.j, 9, 9) * 0.25 - (0.12 if (lz < 1 and up) else 0))
    inner_face = 'bottom' if up else 'top'
    if f == inner_face:
        # gums/palate (upper) or the floor of the mouth (lower); teeth sockets on the outer row
        seam_col = (lx > w - 1.0) if sx < 0 else (lx < 1.0)
        out_col = (lx < 1.0) if sx < 0 else (lx > w - 1.0)
        if out_col:
            return pick(GUM, 0.72 if int(lz) % 2 else 0.5)
        if seam_col:
            return pick(RAW, 0.55)
        return pick(GUM, 0.4 + (0.16 if int(lz) % 2 == 0 else 0) + (0.08 if up else -0.05))
    if f == 'back':
        return pick(RAW, 0.35)
    # outside: muzzle fur (darker toward the nose), black lip line on the mouth edge
    lip = (ly > h - 1.0) if up else (ly < 1.0)
    if f in (outer_face, 'front') and lip:
        return LIP[1] if (ctx.i % 3) else LIP[2]
    near_nose = clamp(1.0 - lz / 5.0) if f != 'front' else 1.0
    v -= near_nose * 0.12
    if not up:
        v += 0.04                                    # chin a touch paler
    if f == 'top':
        v += strands(lx, lz, 63)
        if (sx < 0 and lx > w - 1.0) or (sx > 0 and lx < 1.0):
            return pick(RAW, 0.62)                   # the split line seen from above
    elif f in ('west', 'east'):
        v += strands(ly, lz, 65)
        if up and 1 <= ly <= 3 and 2 <= lz <= 9 and (int(lz) + int(ly)) % 3 == 0:
            return pick(FUR, 0.15)                   # whisker spots
    elif f == 'bottom':
        v -= 0.04
    if f == 'front':
        if (sx < 0 and lx > w - 1.0) or (sx > 0 and lx < 1.0):
            return pick(RAW, 0.55)
    if edge(ctx) == 0:
        v -= 0.05
    return pick(FUR, v)


def nose_mat(ctx):
    """Half of the black nose, cut down the middle (raw red cut face on the seam side)."""
    f = ctx.face
    c = ctx.cube
    sx = c.sx
    seam_face = 'east' if sx < 0 else 'west'
    lx, ly, lz = local(ctx)
    w, h, d = c.size
    if f == seam_face:
        return pick(RAW, 0.45 + ctx.j * 0.1)
    if f == 'front':
        nost = (ctx.i == (1 if sx < 0 else w - 2)) and ctx.j == 1
        seam = (ctx.i == w - 1) if sx < 0 else (ctx.i == 0)
        if nost:
            return NOSE[0]
        if seam:
            return pick(RAW, 0.55)
        if ctx.j == 0:
            return NOSE[4] if ctx.i == (0 if sx < 0 else w - 1) else NOSE[3]
        return NOSE[2] if ctx.j == 1 else NOSE[1]
    if f == 'top':
        return NOSE[5] if (ctx.i == 1 and ctx.j == 1) else NOSE[3]
    if f == 'bottom':
        return NOSE[0]
    return NOSE[2]


def teeth_mat(ctx):
    """Needle teeth on zero-thickness planes.  cube.down: teeth hang from the top row (upper jaw) or stand on the bottom row."""
    c = ctx.cube
    f = ctx.face
    if f not in ('west', 'front'):
        return None
    i, j = ctx.i, ctx.j
    h = ctx.h
    down = c.down
    k = j if down else h - 1 - j                     # distance from the root row
    if k == 0:
        return pick(GUM, 0.55)
    if i % 2 == 1:
        return None
    n = i // 2
    ln = 1 + int(hash3(n, cseed(ctx), 0, 21) * (h - 0.5))
    if getattr(c, 'canine', False) and (n == 0 or i >= ctx.w - 2):
        ln = h - 1
    if k > ln:
        return None
    return pick(TEETH, 0.95 - (ln - k) * 0.18) if k == ln else pick(TEETH, 0.55 + k * 0.1)


def tongue_mat(ctx):
    """Long black tongue: a centre groove and an oily purple sheen."""
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    v = 0.4 + face_light(ctx) * 0.8
    if f == 'top':
        if abs(lx - w / 2) < 0.6:
            return TONGUE[0]                         # groove
        if ctx.i == 0 or ctx.i == ctx.w - 1:
            v -= 0.1
        if (ctx.j + ctx.i) % 5 == 0:
            v += 0.3                                 # wet glints
    if f == 'bottom':
        v -= 0.12
    return pick(TONGUE, v)


def drool_mat(ctx):
    if ctx.face not in ('front', 'west'):
        return None
    if ctx.j == ctx.h - 1:
        return TONGUE[5]
    return TONGUE[2] if ctx.j % 3 else TONGUE[4]


def ear_mat(ctx):
    """Long limp ear: wavy fur outside with a darker rim, bare pink-grey inside, a ragged lower end."""
    f = ctx.face
    c = ctx.cube
    x, y, z = A(ctx)
    lx, ly, lz = local(ctx)
    w, h, d = c.size
    sx = c.sx
    tip = c.name == 'ear_tip'
    if tip:
        # ragged end: per z column, the bottom few texels are gone
        cut = h - (1 + hash3(math.floor(lz), 5, cseed(ctx), 3) * 3.2)
        if ly > cut and f not in ('top',):
            return None
    inner = (f == 'east' and sx < 0) or (f == 'west' and sx > 0)
    v = 0.5 + face_light(ctx) * 1.0
    if inner:
        cc = pick(SKIN, 0.5 - ly / max(1, h) * 0.15)
        if lz < 1.0 or lz > d - 1.0:
            return pick(FUR, v - 0.12)
        return cc
    if f in ('front', 'back'):
        return pick(FUR, v - 0.18)
    v += strands(lz, y, 71 + (1 if tip else 0), 2.0, 4.0)
    # soft waves running down the leather
    if int((y + lz * 0.6) / 3) % 2 == 0:
        v -= 0.05
    if lz < 1.0 or lz > d - 1.0:
        v -= 0.12                                    # darker rim
    return pick(FUR, v)


# ------------------------------------------------------------------ kinematics helpers
def euler_zyx(R):
    """MC Euler angles (degrees) for R = Rz * Ry * Rx (mcmodel.rot_matrix order)."""
    ry = math.asin(max(-1.0, min(1.0, -R[2, 0])))
    rx = math.atan2(R[2, 1], R[2, 2])
    rz = math.atan2(R[1, 0], R[0, 0])
    return math.degrees(rx), math.degrees(ry), math.degrees(rz)


def dir_rot(d):
    """Rotation (Rz * Rx) taking the hanging direction (0, 1, 0) onto unit vector d."""
    d = np.asarray(d, float)
    d = d / np.linalg.norm(d)
    ax = math.asin(max(-1.0, min(1.0, d[2])))
    az = math.atan2(-d[0], d[1])
    return rot_matrix(ax, 0.0, az)


def R_deg(rx, ry, rz):
    return rot_matrix(math.radians(rx), math.radians(ry), math.radians(rz))


# ------------------------------------------------------------------ module contract
DEFAULT_MAT = fur_mat
FOCUS = 'head'

# body chain: (bone, parent, pivot z, centre y, width, height, fur length, gap)
SEGMENTS = [
    ('seg2', 'seg1', -21, 2.5, 12, 12, 8, 6),
    ('seg3', 'seg2', -7, 1.0, 12, 12, 8, 6),
    ('seg4', 'seg3', 7, 0.0, 12, 12, 8, 6),
    ('seg5', 'seg4', 21, 1.0, 12, 12, 8, 6),
    ('seg6', 'seg5', 35, 2.0, 12, 12, 8, 6),
    ('hips', 'seg6', 49, 3.0, 13, 12, 12, 6),
]
SEG_C = {'seg1': 4.0, **{s[0]: s[3] for s in SEGMENTS}}

# human arm pairs: (index, parent segment, shoulder z, elbow (out, y, dz), wrist (out, dz), hand yaw)
ARMS = [
    (1, 'seg3', 3.0, (13.0, -14.0, -3.0), (22.0, -9.0), 30),
    (2, 'seg5', 31.0, (14.0, -15.0, 0.0), (24.0, 1.0), 10),
    (3, 'hips', 61.0, (13.0, -12.0, 3.0), (22.0, 9.0), -15),
]


def build():
    r = Rig()

    def box(bone, frm, size, mat=None, inflate=0.0, decals=None, name=None, **attrs):
        c = r.box(bone, frm, size, mat=mat, inflate=inflate, decals=decals)
        c.a0 = tuple(float(v) for v in frm)
        c.name = name
        for k, v in attrs.items():
            setattr(c, k, v)
        return c

    bone = r.bone

    # ---------------- seg1: the chest (root) with the sweater remnant and the two real dachshund legs
    c1 = SEG_C['seg1']
    bone('seg1', (0, c1, -36), mat=fur_mat)
    box('seg1', (-7, c1 - 6, -37), (14, 12, 16), name='core', tear=(False, True))
    box('seg1', (-5, c1 - 7, -37), (10, 1, 16), name='cap', tear=(False, True))
    box('seg1', (-5, c1 + 6, -35), (10, 1, 13), name='keel', tear=(False, True))
    box('seg1', (-7, c1 - 6, -37), (14, 12, 13), mat=sweater_mat, name='sweater', inflate=0.6)

    for side, sx in (('right', -1), ('left', 1)):
        lb, pb = f'front_{side}_leg', f'front_{side}_paw'
        lx = 4.5 * sx
        bone(lb, (lx, c1 + 4, -30), parent='seg1', rot=(0, 0, 5 * sx), mat=leg_fur)
        box(lb, (lx - 2.5, c1 + 3, -32.5), (5, 6, 5), name='shoulder')
        box(lb, (lx - 2, c1 + 9, -32), (4, 8, 4), name='leg')
        bone(pb, (lx, 21, -30), parent=lb, rot=(0, -16 * sx, -5 * sx), mat=paw_mat)
        box(pb, (lx - 2.5, 21, -34), (5, 3, 6), name='paw')
        box(pb, (lx - 2, 22, -35), (4, 2, 1), name='toes')

    # ---------------- neck: stretched skin with trachea rings, the celeste collar and its brass tag
    bone('neck', (0, 0, -36), parent='seg1', rot=(-25, 0, 0), mat=skin_mat)
    box('neck', (-4.5, -5, -48), (9, 9, 15), name='tube')
    for k, z in enumerate((-41.0, -38.0)):
        box('neck', (-5.5, -6, z), (11, 9, 1), mat=rib_mat, name='ring')
    box('neck', (-5.5, -6, -45.5), (11, 11, 2), mat=collar_mat, name='collar')
    box('neck', (-1, 5, -44.5), (2, 3, 0), mat=collar_mat, name='tag')

    # ---------------- head (pivot at the neck joint, under the back of the skull)
    HZ = -46.0

    def H(x, y, z):
        return (x, y, HZ + z)

    bone('head', (0, 0, HZ), parent='neck', rot=(25, 0, 0), mat=skull_mat)
    box('head', H(-8, -14, -14), (16, 8, 14), name='skull')
    box('head', H(-6, -15, -12), (12, 1, 10), name='dome')
    box('head', H(-8, -6, -14), (4, 6, 14), name='side')
    box('head', H(4, -6, -14), (4, 6, 14), name='side')
    box('head', H(-4, -6, -6), (8, 6, 6), mat=throat_mat, name='throat')
    box('head', H(-7, -12, -15), (6, 6, 1), mat=eye_mat, name='eye', side='r',
        decals={'eyes:front': eye_glow('r')})
    box('head', H(1, -12, -15), (6, 6, 1), mat=eye_mat, name='eye', side='l',
        decals={'eyes:front': eye_glow('l')})

    # the four muzzle flaps
    for side, sx in (('right', -1), ('left', 1)):
        ub, lb = f'jaw_upper_{side}', f'jaw_lower_{side}'
        bone(ub, H(0.5 * sx, -1, -13), parent='head', rot=(-3, 3 * -sx, 0), mat=flap_mat)
        x0 = -5.5 if sx < 0 else 0.5
        box(ub, H(x0, -6, -27), (5, 5, 14), name='flap', upper=True, sx=sx)
        nx0 = -3.5 if sx < 0 else 0.5
        box(ub, H(nx0, -6, -29), (3, 3, 2), mat=nose_mat, name='nose', sx=sx)
        lipx = -5.2 if sx < 0 else 5.2
        box(ub, H(lipx, -1, -26), (0, 3, 12), mat=teeth_mat, name='teeth', down=True)
        box(ub, H(-1.8 if sx < 0 else 1.8, -1, -25), (0, 2, 11), mat=teeth_mat, name='teeth', down=True)
        box(ub, H(-5.2 if sx < 0 else 1.2, -1, -26.6), (4, 3, 0), mat=teeth_mat, name='teeth', down=True,
            canine=True)

        bone(lb, H(0.5 * sx, 0, -6), parent='head', rot=(4, 3 * -sx, 0), mat=flap_mat)
        lx0 = -4.5 if sx < 0 else 0.5
        box(lb, H(lx0, 0, -26), (4, 4, 20), name='flap', upper=False, sx=sx)
        box(lb, H(-4.1 if sx < 0 else 4.1, -3, -25), (0, 3, 11), mat=teeth_mat, name='teeth', down=False)
        box(lb, H(-4.1 if sx < 0 else 1.1, -3, -25.6), (3, 3, 0), mat=teeth_mat, name='teeth', down=False,
            canine=True)
        # a string of black drool from the corner of the mouth
        box(lb, H(-4.6 if sx < 0 else 4.6, 4, -18 if sx < 0 else -15), (0, 4 if sx < 0 else 6, 1),
            mat=drool_mat, name='drool')

    # black tongue lolling out of the front
    bone('tongue', H(0, -0.5, -8), parent='head', mat=tongue_mat)
    box('tongue', H(-2, -1, -27), (4, 1, 19), name='tongue')
    bone('tongue_tip', H(0, -0.5, -27), parent='tongue', rot=(62, 0, 0), mat=tongue_mat)
    box('tongue_tip', H(-2, -1, -36), (4, 1, 9), name='tongue')
    box('tongue_tip', H(-1, -1, -39), (2, 1, 3), name='tongue')

    # ears: limp and far too long, nearly touching the ground
    for side, sx in (('right', -1), ('left', 1)):
        eb, tb = f'{side}_ear', f'{side}_ear_tip'
        ex = 9.0 * sx
        bone(eb, H(ex, -13, -5), parent='head', rot=(4, 0, -7 * sx), mat=ear_mat)
        box(eb, H(ex - 1, -14, -9), (2, 19, 8), name='ear', sx=sx)
        bone(tb, H(ex, 5, -5), parent=eb, rot=(-3, 0, 4 * sx), mat=ear_mat)
        box(tb, H(ex - 1, 5, -8.5), (2, 20, 7), name='ear_tip', sx=sx)

    # ---------------- body links seg2..seg6 + hips: stretched skin band (ribs) then a fur link
    for name, parent, pz, c, W, Hh, L, gap in SEGMENTS:
        bone(name, (0, c, pz), parent=parent, mat=fur_mat)
        box(name, (-4.5, c - 4.5, pz - 3), (9, 9, gap + 4), mat=skin_mat, name='tube')
        for rz in (pz + 1.5, pz + 3.5):
            box(name, (-5.5, c - 5.5, rz), (11, 9, 1), mat=rib_mat, name='rib')
        z0 = pz + gap
        last = name == 'hips'
        box(name, (-W / 2, c - Hh / 2 + 1, z0), (W, Hh - 2, L), name='core', tear=(True, not last))
        box(name, (-W / 2 + 2, c - Hh / 2, z0), (W - 4, 1, L), name='cap', tear=(True, not last))
        box(name, (-W / 2 + 2, c + Hh / 2 - 1, z0), (W - 4, 1, L), name='keel', tear=(True, not last))
        if last:
            box(name, (-W / 2 + 2, c - Hh / 2 + 2, z0 + L), (W - 4, Hh - 4, 1), name='rump')

    # a broken rib piercing the skin on the right flank of the seg3 gap
    box('seg3', (-6.5, -4.0, -5.0), (1, 3, 1), mat=spike_mat, name='spike')
    box('seg5', (5.5, -3.0, 22.5), (1, 2, 1), mat=spike_mat, name='spike')

    # ---------------- tail: a normal little dachshund tail, still wagging
    ch = SEG_C['hips']
    bone('tail', (0, ch - 4, 66), parent='hips', rot=(38, 0, 0), mat=leg_fur)
    box('tail', (-1.5, ch - 5.5, 66), (3, 3, 9), name='tail')
    bone('tail_tip', (0, ch - 4, 75), parent='tail', rot=(14, 0, 0), mat=leg_fur)
    box('tail_tip', (-1, ch - 5, 74.5), (2, 2, 8), name='tail')

    # ---------------- sweater shreds hanging off the spine
    shreds = [('shred_1', 'seg2', -11.0, 9, 6), ('shred_2', 'seg3', 3.0, 7, 11),
              ('shred_3', 'seg4', 17.0, 12, 5), ('shred_4', 'seg5', 30.5, 5, 9)]
    for name, parent, zc, lr, ll in shreds:
        c = SEG_C[parent]
        bone(name, (0, c - 6, zc), parent=parent, mat=shred_mat)
        box(name, (-6.3, c - 6.4, zc - 1.5), (12, 1, 3), name='band', inflate=0.15)
        box(name, (-6.5, c - 5.6, zc - 1.5), (0, lr, 3), name='strip')
        box(name, (6.5, c - 5.6, zc - 1.0), (0, ll, 2), name='strip')
        box(name, (-6.6, c - 5.6 + lr - 1, zc + 0.5), (0, 5, 1), name='yarn')

    # ---------------- three pairs of human arms (spider elbows above the spine, flat palms, long fingers)
    for idx, seg, zs, (eo, ey, edz), (wo, wdz), yaw in ARMS:
        c = SEG_C[seg]
        for side, sx in (('right', -1), ('left', 1)):
            ab, fb, hb = f'arm_{idx}_{side}', f'forearm_{idx}_{side}', f'hand_{idx}_{side}'
            S = np.array([5.0 * sx, c + 2.0, zs])
            E = np.array([eo * sx, ey, zs + edz])
            W = np.array([wo * sx, 22.0, zs + wdz])
            d1 = E - S
            L1 = int(round(np.linalg.norm(d1)))
            R1 = dir_rot(d1)
            d2 = W - (S + R1 @ np.array([0, L1, 0]))
            L2 = int(round(np.linalg.norm(d2)))
            R2w = dir_rot(d2)
            R2 = R1.T @ R2w
            Rh = R2w.T @ R_deg(0, -yaw * sx, 0)
            a1 = euler_zyx(R1)
            a2 = euler_zyx(R2)
            ah = euler_zyx(Rh)
            Sx, Sy, Sz = S
            bone(ab, (Sx, Sy, Sz), parent=seg, rot=a1, mat=arm_mat)
            box(ab, (Sx - 2, Sy - 1.5, Sz - 2), (4, 3, 4), name='shoulder')
            box(ab, (Sx - 1.5, Sy, Sz - 1.5), (3, L1, 3), name='upper')
            bone(fb, (Sx, Sy + L1, Sz), parent=ab, rot=a2, mat=arm_mat)
            box(fb, (Sx - 2, Sy + L1 - 2, Sz - 2), (4, 4, 4), name='elbow')
            box(fb, (Sx - 1, Sy + L1, Sz - 1), (2, L2, 2), name='fore', inflate=0.25)
            hy = Sy + L1 + L2
            bone(hb, (Sx, hy, Sz), parent=fb, rot=ah, mat=arm_mat)
            box(hb, (Sx - 3.5, hy, Sz - 5), (7, 2, 6), name='palm')
            for k, fx in enumerate((-3.0, -1.0, 1.0, 3.0)):
                ln = (7, 9, 8, 6)[k if sx < 0 else 3 - k]
                box(hb, (Sx + fx - 0.5, hy + 1, Sz - 5 - ln), (1, 1, ln), name='finger')
            tx = Sx + 3.5 if sx < 0 else Sx - 3.5 - 4
            box(hb, (tx, hy + 1, Sz - 4), (4, 1, 1), name='thumb', tipx=1 if sx < 0 else -1)

    m = Model('choripan_demonio', 256, 256, r.roots)
    m.scale = 0.5
    return m


POSES = {}

ANIM_NOTES = """(written once the rig is final)"""
