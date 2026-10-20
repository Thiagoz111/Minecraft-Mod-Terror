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
SKIN = pal('#1e1219', '#36202b', '#52343f', '#704c55', '#8e666b', '#ab8282', '#c69e99', '#dcbcb2')
HUMAN = pal('#2a1a1a', '#47302d', '#6a4a43', '#8d6a5e', '#ad8a7a', '#c8a796', '#dec1ae', '#eed8c6')
VEIN = pal('#3a3463', '#544a86', '#6b4f7c')
BONE = pal('#8c7f72', '#bdb1a2', '#e2d8c8', '#f6efe2')
RAW = pal('#2e050b', '#561019', '#80202a', '#a8383e', '#c95a5a', '#e08a82')
GUM = pal('#300510', '#5a0c1c', '#8a1628', '#b52a38', '#d4484e', '#e8706c')
TEETH = pal('#5a5244', '#9a917c', '#d4ccb6', '#f2ecdc', '#fffdf4')
TONGUE = pal('#030205', '#0c0910', '#18121d', '#261d2c', '#3a2e42', '#594a66', '#8a7a9c')
THROAT = pal('#000000', '#0c0105', '#1e040a', '#3a0812', '#5c0f1b')
NOSE = pal('#050406', '#121016', '#221f2a', '#38343f', '#625d70', '#b4b0c8')
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
    for k, (torn, dist) in enumerate(((tf, lz), (tb, d - lz))):
        if not torn:
            continue
        jag = 0.35 + hash3(math.floor(across), cseed(ctx), 1 + k, 13) * 1.35
        if dist < jag - 0.55:
            return pick(RAW, 0.55 + hash3(math.floor(across), 2, 3, 4) * 0.25)
        if dist < jag:
            return pick(FUR, v - 0.22)
        # blood trickling down the flank from the torn rim
        if f in ('west', 'east') and dist < 1.0:
            col = math.floor(lz) + 31 * k + cseed(ctx)
            if hash3(col, 7, 1, 77) > 0.55 and ly < 2.0 + hash3(col, 8, 2, 78) * 5.0:
                return pick(RAW, 0.3 if ly > 1.5 else 0.42)
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
    if math.floor(across) % 3 == 0 and hash3(math.floor(across), math.floor(along / 4), 0, 3) > 0.3:
        v -= 0.12
    elif math.floor(across) % 3 == 1 and hash3(math.floor(across), math.floor(along / 3), 1, 3) > 0.6:
        v += 0.08
    # translucent: darker shapes under the skin (organs / rib shadows) on the flanks
    if f in ('west', 'east', 'bottom'):
        blob = hash3(math.floor(along / 3), math.floor(across / 3), cseed(ctx), 17)
        if blob > 0.66:
            v -= 0.16
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
    v = skin_core(ctx, 0.5)
    c = pick(SKIN, v)
    # irritated pink where the skin is pulled out of the fur
    lx, ly, lz = local(ctx)
    d = ctx.cube.size[2]
    if f in ('west', 'east', 'top') and (lz < 4.5 or lz > d - 2.0):
        c = mix(c, RAW[4], 0.22)
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
    v = 0.62 + face_light(ctx) * 0.8
    c = pick(SKIN, v)
    if f == 'top' and abs(lx - w / 2) < w * 0.25:
        c = mix(c, BONE[1], 0.35)                 # the bone shows through on the crest
    if f in ('west', 'east') and ly < h * 0.35:
        c = mix(c, BONE[1], 0.2)
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
        c = pick(HUMAN, v + 0.1)
        if f in ('top', 'front', 'west', 'east') and edge(ctx) > 0:
            c = mix(c, BONE[2], 0.4)                # the bone end straining the skin
        return c
    if t == 'shoulder':
        # where the arm burst out of the dog: torn fur collar around raw skin
        if ly < 1.0 or edge(ctx) == 0:
            return pick(FUR, 0.45 + face_light(ctx) + hash3(ctx.i, ctx.j, 1, 2) * 0.15)
        return pick(RAW, 0.55 + hash3(ctx.i, ctx.j, 2, 3) * 0.2)
    if t in ('upper', 'fore'):
        c = pick(HUMAN, v)
        if f in ('west', 'back') and vein_hit(ctx, ly, lx + lz, cseed(ctx)):
            c = mix(c, VEIN[1], 0.3)
        if t == 'fore' and ly > h - 3:
            c = mix(c, DIRT, 0.25)                  # filthy wrists
        if t == 'upper' and ly < 2:
            c = mix(c, RAW[3], 0.35)
        return c
    if t == 'palm':
        if f == 'bottom':
            return mix(pick(HUMAN, 0.3), DIRT, 0.5)
        c = pick(HUMAN, v)
        if f == 'top' and ctx.j <= 1:
            c = pick(HUMAN, v - 0.12)                # knuckle row
        return c
    if t in ('finger', 'thumb'):
        if f == 'bottom':
            return mix(pick(HUMAN, 0.3), DIRT, 0.5)
        tip = (lz < 1.0) if t == 'finger' else (getattr(ctx.cube, 'tipx', 0) * (lx - w / 2) > 0 and abs(lx - w / 2) > w / 2 - 1)
        if tip:
            return pick(NAIL, 0.55 + face_light(ctx)) if f == 'top' else NAIL[0]   # cracked nail, black dirt
        c = pick(HUMAN, v)
        if t == 'finger' and f == 'top' and int(lz) % 3 == 1:
            c = pick(HUMAN, v - 0.13)                # extra knuckle creases (one too many)
        return c
    return pick(HUMAN, v)


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
                pts.append((i, j, (int(c[0] * 0.9), int(c[1] * 0.94), int(c[2] * 0.96), 255)))
    return at(pts)


HY, HZ = 2.0, -46.0          # authored head pivot (the neck joint under the back of the skull)
EYE_X = (-8, 2)              # left edge of the right / left eye disc, head-relative
EYE_Y = -12                  # top edge of the eye discs, head-relative


def in_disc(i, j):
    """Texel (i, j) inside the 6x6 eye disc (corners cut)."""
    if not (0 <= i < 6 and 0 <= j < 6):
        return False
    return (i, j) not in ((0, 0), (5, 0), (0, 5), (5, 5))


def skull_mat(ctx):
    """Head fur.  Front: forehead, black lid rings, tan puppy-brow dots; the inside of the mouth cavity is flesh."""
    f = ctx.face
    t = tag(ctx)
    x, y, z = A(ctx)
    lx, ly, lz = local(ctx)
    v = 0.56 + face_light(ctx) * 1.05
    y -= HY
    z -= HZ
    if t == 'skull':
        if f == 'front':
            tx, ty = math.floor(x), math.floor(y)
            # black lid ring hugging the round eye discs (4-neighbours of the disc), fur bridge between
            for ex0 in EYE_X:
                if in_disc(tx - ex0, ty - EYE_Y):
                    return LIP[0]
                if any(in_disc(tx + dx - ex0, ty + dy - EYE_Y) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    return LIP[1] if ty > EYE_Y + 3 else LIP[0]
            # tan puppy brows, raised at the inner ends (sad, cute)
            if ty == EYE_Y - 2 and (-6 <= tx <= -4 or 3 <= tx <= 5):
                return TAN[1] if (tx in (-4, 3)) else TAN[0]
            v += 0.04 - abs(x) / 9 * 0.1
            v += (hash3(math.floor(x / 2), math.floor(y / 2), 1, 61) - 0.5) * 0.12
            return pick(FUR, v)
        if f == 'bottom' and abs(x) < 4 and z < -6:
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
            return pick(GUM, 0.55 - (z + 14) * 0.04 + (0.1 if int(y) % 2 == 0 else 0))
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
    deep = lz / max(1.0, d) * 0.28                   # darker toward the throat
    if f == seam_face:
        # the cut: striated raw flesh, a gum line with a row of small inner teeth toward the mouth
        gum_edge = (ly > h - 1.0) if up else (ly < 1.0)
        if gum_edge:
            if int(lz) % 2 == 0 and lz < d - 3:
                return pick(TEETH, 0.6)
            return pick(GUM, 0.62 - deep)
        vv = 0.52 + hash3(ctx.i, ctx.j, 9, 9) * 0.12 - deep
        if int(ly) % 2 == 0:
            vv -= 0.14                               # muscle striations
        return pick(RAW, vv)
    inner_face = 'bottom' if up else 'top'
    if f == inner_face:
        # gums/palate (upper) or the floor of the mouth (lower); teeth sockets on the outer row
        seam_col = (lx > w - 1.0) if sx < 0 else (lx < 1.0)
        out_col = (lx < 1.0) if sx < 0 else (lx > w - 1.0)
        if out_col:
            return pick(GUM, (0.72 if int(lz) % 2 else 0.5) - deep)
        if seam_col:
            return pick(RAW, 0.55 - deep)
        return pick(GUM, 0.42 + (0.16 if int(lz) % 2 == 0 else 0) + (0.08 if up else -0.05) - deep)
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
        rows = ["hHhr", "mOOr", "llOr"]
        ch = rows[ctx.j][ctx.i if sx < 0 else w - 1 - ctx.i]
        return {'h': NOSE[4], 'H': NOSE[5], 'm': NOSE[2], 'O': NOSE[0], 'l': NOSE[1], 'r': RAW[3]}[ch]
    if f == 'top':
        seam = (ctx.i == w - 1) if sx < 0 else (ctx.i == 0)
        if seam:
            return RAW[3]
        return NOSE[5] if (ctx.j == 1 and ctx.i == (1 if sx < 0 else w - 2)) else NOSE[3]
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


WHISKER = [
    "k.....",
    ".kk...",
    "...kk.",
    "kk...k",
    "..kkk.",
]


def whisker_mat(ctx):
    """Three wiry dog whiskers fanning out of the muzzle (a front-facing zero-thickness plane)."""
    if ctx.face != 'front':
        return None
    sx = ctx.cube.sx
    i = ctx.i if sx > 0 else ctx.w - 1 - ctx.i
    if WHISKER[ctx.j][i] != 'k':
        return None
    return LIP[2] if i < 3 else pick(FUR, 0.18)


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
        # rounded, slightly ragged lower end
        dy = ly - (h - 4.5)
        if dy > 0:
            half = d / 2 * math.sqrt(max(0.0, 1 - (dy / 4.5) ** 2))
            if abs(lz - d / 2) > half + 0.35 - hash3(math.floor(lz), 5, cseed(ctx), 3) * 0.6:
                return None
        if f == 'bottom':
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
    (1, 'seg3', 3.0, (16.0, -9.0, -6.0), (20.0, -17.0), 35),
    (2, 'seg5', 31.0, (17.0, -10.0, 2.0), (21.0, -4.0), 12),
    (3, 'hips', 61.0, (16.0, -8.0, 8.0), (20.0, 14.0), -25),
]


def arm_rig(idx, side, E=None, W=None, hand_world=None, seg_R=None, seg_T=None):
    """Rest (or re-targeted) kinematics of one human arm.

    Returns shoulder S, lengths L1/L2 (fixed by the rest pose) and MC Euler angles (degrees) of the
    arm, forearm and hand bones.  For a pose pass world targets: elbow E, wrist W (the wrist lands on
    the line from E toward W at the fixed forearm length), hand_world (3x3) and the parent segment's
    world rotation/translation (seg_R, seg_T) if the segment itself moves in that pose."""
    a = {k[0]: k for k in ARMS}[idx]
    _, seg, zs, (eo, ey, edz), (wo, wdz), yaw = a
    sx = -1 if side == 'right' else 1
    c = SEG_C[seg]
    S = np.array([5.0 * sx, c + 2.0, zs])
    E0 = np.array([eo * sx, ey, zs + edz])
    W0 = np.array([wo * sx, 22.0, zs + wdz])
    L1 = int(round(np.linalg.norm(E0 - S)))
    R1w = dir_rot(E0 - S)
    L2 = int(round(np.linalg.norm(W0 - (S + R1w @ np.array([0, L1, 0])))))
    Hw = R_deg(0, -yaw * sx, 0)
    if E is not None:
        segR = np.eye(3) if seg_R is None else seg_R
        segT = np.zeros(3) if seg_T is None else np.asarray(seg_T, float)
        Sw = segR @ S + segT                      # shoulder in the world for this pose
        R1w = dir_rot(np.asarray(E, float) - Sw)
        Ew = Sw + R1w @ np.array([0, L1, 0])
        R2w = dir_rot(np.asarray(W, float) - Ew)
        Hw = hand_world if hand_world is not None else Hw
        R1 = segR.T @ R1w
    else:
        R1 = R1w
        R2w = dir_rot(W0 - (S + R1w @ np.array([0, L1, 0])))
        segR = np.eye(3)
    R1world = segR @ R1
    R2 = R1world.T @ R2w
    Rh = R2w.T @ Hw
    return {'S': S, 'L1': L1, 'L2': L2, 'a1': euler_zyx(R1), 'a2': euler_zyx(R2), 'ah': euler_zyx(Rh)}


def _wrap(d):
    d = math.radians(d)
    while d > math.pi:
        d -= 2 * math.pi
    while d <= -math.pi:
        d += 2 * math.pi
    return d


def arm_pose(idx, side, E, W, hand_world=None, seg_R=None, seg_T=None):
    """Pose deltas (radians, added to rest) for the arm, forearm and hand bones of one arm."""
    r0 = arm_rig(idx, side)
    r1 = arm_rig(idx, side, E, W, hand_world, seg_R, seg_T)
    out = {}
    for key, bn in (('a1', f'arm_{idx}_{side}'), ('a2', f'forearm_{idx}_{side}'), ('ah', f'hand_{idx}_{side}')):
        out[bn] = tuple(_wrap(r1[key][k] - r0[key][k]) for k in range(3)) + (0.0, 0.0, 0.0)
    return out


def arm_ik(idx, side, W, pole, hand_world=None, seg_R=None, seg_T=None):
    """Two-bone IK: wrist on W (world), elbow bent toward `pole`; returns pose deltas."""
    g = arm_rig(idx, side)
    L1, L2 = g['L1'], g['L2']
    segR = np.eye(3) if seg_R is None else seg_R
    segT = np.zeros(3) if seg_T is None else np.asarray(seg_T, float)
    S = segR @ g['S'] + segT
    W = np.asarray(W, float)
    d = W - S
    n = float(np.linalg.norm(d))
    n = max(abs(L1 - L2) + 0.5, min(L1 + L2 - 0.5, n))
    u = d / np.linalg.norm(d)
    a = (L1 * L1 - L2 * L2 + n * n) / (2 * n)
    h = math.sqrt(max(0.0, L1 * L1 - a * a))
    pv = np.asarray(pole, float)
    pv = pv - u * float(pv @ u)
    pv = pv / max(1e-6, float(np.linalg.norm(pv)))
    E = S + u * a + pv * h
    return arm_pose(idx, side, E, S + u * n, hand_world, seg_R, seg_T)


def rad(*deg):
    return tuple(math.radians(v) for v in deg)


def P(rx=0.0, ry=0.0, rz=0.0, dx=0.0, dy=0.0, dz=0.0):
    """Pose entry from degrees + texel offsets."""
    return rad(rx, ry, rz) + (dx, dy, dz)



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
    bone('neck', (0, HY, -36), parent='seg1', rot=(-35, 0, 0), mat=skin_mat)
    box('neck', (-4.5, HY - 5, -48), (9, 9, 15), name='tube')
    for k, z in enumerate((-41.0, -38.0)):
        box('neck', (-5.5, HY - 6, z), (11, 9, 1), mat=rib_mat, name='ring')
    box('neck', (-5.5, HY - 6, -45.5), (11, 11, 2), mat=collar_mat, name='collar')
    box('neck', (-1, HY + 5, -44.5), (2, 3, 0), mat=collar_mat, name='tag')

    # ---------------- head (pivot at the neck joint, under the back of the skull)
    def H(x, y, z):
        return (x, HY + y, HZ + z)

    bone('head', (0, HY, HZ), parent='neck', rot=(35, 0, 0), mat=skull_mat)
    box('head', H(-9, -14, -14), (18, 8, 14), name='skull')
    box('head', H(-7, -15, -12), (14, 1, 10), name='dome')
    box('head', H(-9, -6, -14), (5, 6, 14), name='side')
    box('head', H(4, -6, -14), (5, 6, 14), name='side')
    box('head', H(-4, -6, -6), (8, 6, 6), mat=throat_mat, name='throat')
    box('head', H(EYE_X[0], EYE_Y, -15), (6, 6, 1), mat=eye_mat, name='eye', side='r',
        decals={'eyes:front': eye_glow('r')})
    box('head', H(EYE_X[1], EYE_Y, -15), (6, 6, 1), mat=eye_mat, name='eye', side='l',
        decals={'eyes:front': eye_glow('l')})

    # the four muzzle flaps
    for side, sx in (('right', -1), ('left', 1)):
        ub, lb = f'jaw_upper_{side}', f'jaw_lower_{side}'
        bone(ub, H(0.5 * sx, -1, -13), parent='head', rot=(-3, 3 * -sx, 0), mat=flap_mat)
        x0 = -5.5 if sx < 0 else 0.5
        box(ub, H(x0, -6, -27), (5, 5, 14), name='flap', upper=True, sx=sx)
        nx0 = -4.5 if sx < 0 else 0.5
        box(ub, H(nx0, -6.5, -29), (4, 3, 2), mat=nose_mat, name='nose', sx=sx)
        lipx = -5.2 if sx < 0 else 5.2
        box(ub, H(lipx, -1, -26), (0, 3, 12), mat=teeth_mat, name='teeth', down=True)
        box(ub, H(-1.8 if sx < 0 else 1.8, -1, -25), (0, 2, 11), mat=teeth_mat, name='teeth', down=True)
        box(ub, H(-5.2 if sx < 0 else 1.2, -1, -26.6), (4, 3, 0), mat=teeth_mat, name='teeth', down=True,
            canine=True)
        box(ub, H(-11.5 if sx < 0 else 5.5, -5, -21), (6, 5, 0), mat=whisker_mat, name='whisker', sx=sx)

        bone(lb, H(0.5 * sx, 0, -6), parent='head', rot=(4, 3 * -sx, 0), mat=flap_mat)
        lx0 = -4.5 if sx < 0 else 0.5
        box(lb, H(lx0, 0, -26), (4, 4, 20), name='flap', upper=False, sx=sx)
        box(lb, H(-4.1 if sx < 0 else 4.1, -3, -25), (0, 3, 11), mat=teeth_mat, name='teeth', down=False)
        box(lb, H(-4.1 if sx < 0 else 1.1, -3, -25.6), (3, 3, 0), mat=teeth_mat, name='teeth', down=False,
            canine=True)
        box(lb, H(-1.4 if sx < 0 else 1.4, -2, -24), (0, 2, 12), mat=teeth_mat, name='teeth', down=False)
        # a string of black drool from the corner of the mouth
        box(lb, H(-4.6 if sx < 0 else 4.6, 4, -18 if sx < 0 else -15), (0, 4 if sx < 0 else 6, 1),
            mat=drool_mat, name='drool')

    # black tongue lolling out of the front
    bone('tongue', H(0, -0.5, -8), parent='head', mat=tongue_mat)
    box('tongue', H(-2.5, -1, -28), (5, 1, 20), name='tongue')
    bone('tongue_tip', H(0, -0.5, -28), parent='tongue', rot=(52, 6, 0), mat=tongue_mat)
    box('tongue_tip', H(-2.5, -1, -37), (5, 1, 9), name='tongue')
    box('tongue_tip', H(-1.5, -1, -40), (3, 1, 3), name='tongue')

    # ears: limp and far too long, nearly touching the ground; turned a little toward the front
    for side, sx in (('right', -1), ('left', 1)):
        eb, tb = f'{side}_ear', f'{side}_ear_tip'
        ex = 10.0 * sx
        bone(eb, H(ex, -11, -4), parent='head', rot=(8, -24 * sx, -10 * sx), mat=ear_mat)
        box(eb, H(ex - 1, -12, -6), (2, 17, 5), name='ear', sx=sx)
        box(eb, H(ex - 1, -1, -7.5), (2, 6, 7), name='ear', sx=sx)
        bone(tb, H(ex, 5, -4), parent=eb, rot=(-7, 0, 6 * sx), mat=ear_mat)
        box(tb, H(ex - 1, 5, -8), (2, 21, 8), name='ear_tip', sx=sx)

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
    shreds = [('shred_1', 'seg2', -11.0, 12, 8), ('shred_2', 'seg3', 3.0, 9, 14),
              ('shred_3', 'seg4', 17.0, 14, 7), ('shred_4', 'seg5', 30.5, 7, 12)]
    for name, parent, zc, lr, ll in shreds:
        c = SEG_C[parent]
        bone(name, (0, c - 6, zc), parent=parent, mat=shred_mat)
        box(name, (-6.3, c - 6.4, zc - 1.5), (12, 1, 3), name='band', inflate=0.15)
        box(name, (-6.5, c - 5.6, zc - 2.0), (0, lr, 4), name='strip')
        box(name, (6.5, c - 5.6, zc - 1.5), (0, ll, 3), name='strip')
        box(name, (-6.6, c - 5.6 + lr - 1, zc + 0.5), (0, 5, 1), name='yarn')

    # ---------------- three pairs of human arms (spider elbows above the spine, flat palms, long fingers)
    for idx, seg, zs, (eo, ey, edz), (wo, wdz), yaw in ARMS:
        c = SEG_C[seg]
        for side, sx in (('right', -1), ('left', 1)):
            ab, fb, hb = f'arm_{idx}_{side}', f'forearm_{idx}_{side}', f'hand_{idx}_{side}'
            g = arm_rig(idx, side)
            S, L1, L2 = g['S'], g['L1'], g['L2']
            a1, a2, ah = g['a1'], g['a2'], g['ah']
            Sx, Sy, Sz = S
            bone(ab, (Sx, Sy, Sz), parent=seg, rot=a1, mat=arm_mat)
            box(ab, (Sx - 2.5, Sy - 1.5, Sz - 2.5), (5, 4, 5), name='shoulder')
            box(ab, (Sx - 1.5, Sy, Sz - 1.5), (3, L1, 3), name='upper', inflate=0.3)
            box(ab, (Sx - 2, Sy + 3, Sz - 2), (4, 6, 4), name='upper')
            bone(fb, (Sx, Sy + L1, Sz), parent=ab, rot=a2, mat=arm_mat)
            box(fb, (Sx - 2, Sy + L1 - 2, Sz - 2), (4, 4, 4), name='elbow')
            box(fb, (Sx - 1, Sy + L1, Sz - 1), (2, L2, 2), name='fore', inflate=0.3)
            box(fb, (Sx - 1.5, Sy + L1 + 2, Sz - 1.5), (3, 8, 3), name='fore')
            hy = Sy + L1 + L2
            bone(hb, (Sx, hy, Sz), parent=fb, rot=ah, mat=arm_mat)
            box(hb, (Sx - 3.5, hy, Sz - 5), (7, 2, 6), name='palm')
            for k, fx in enumerate((-3.0, -1.0, 1.0, 3.0)):
                ln = (7, 9, 8, 6)[k if sx < 0 else 3 - k]
                box(hb, (Sx + fx - 0.5, hy + 1, Sz - 5 - ln), (1, 1, ln), name='finger')
            tx = Sx + 3.5 if sx < 0 else Sx - 3.5 - 4
            box(hb, (tx, hy + 1, Sz - 4), (4, 1, 1), name='thumb', tipx=1 if sx < 0 else -1)

    m = Model('choripan_demonio', 256, 224, r.roots)
    m.scale = 0.5
    return m


# ------------------------------------------------------------------ poses
def _merge(*ds):
    out = {}
    for d in ds:
        out.update(d)
    return out


def _sit_up(A):
    """seg1 (root) pitched up by A degrees around its back end so seg2.. stay planted (seg2 counter-rotates)."""
    c1 = SEG_C['seg1']
    v = np.array([0.0, SEGMENTS[0][3] - c1, SEGMENTS[0][2] + 36.0])     # seg2 pivot relative to seg1's
    R = R_deg(-A, 0, 0)
    off = v - R @ v
    return {'seg1': P(-A, 0, 0, 0, off[1], off[2]), 'seg2': P(A)}


def _praying_hands():
    out = {}
    for side, sx in (('right', -1), ('left', 1)):
        Hw = np.array([[0, -sx, 0], [0, 0, 1], [-sx, 0, 0]], float)
        out.update(arm_ik(1, side, (2.0 * sx, 3.0, -39.0), (sx * 1.0, -0.6, 0.5), Hw))
    return out


def _folded_arms(seg_dz):
    """Arms folded back over the flanks like a resting spider (for the transformation)."""
    out = {}
    for idx, seg, *_ in ARMS:
        T = np.array([0.0, 0.0, seg_dz[seg]])
        for side, sx in (('right', -1), ('left', 1)):
            S = arm_rig(idx, side)['S'] + T
            W = S + np.array([sx * 6.0, -3.0, 18.0])
            out.update(arm_ik(idx, side, W, (sx * 0.6, -1.0, -0.2), R_deg(0, 180, 0), seg_T=T))
    return out


SEGMENT_Z = {'seg1': -36.0, **{n[0]: float(n[2]) for n in SEGMENTS}}


def _world(pose):
    """World matrices of every bone with `pose` (radians / texels) added to the rest pose."""
    m = build()
    for bn in m.bones():
        if bn.name in pose:
            q = pose[bn.name]
            bn.rot = tuple(bn.rot[k] + math.degrees(q[k]) for k in range(3))
            bn.pivot = (bn.pivot[0] + q[3], bn.pivot[1] + q[4], bn.pivot[2] + q[5])
    return {bn.name: m.world_matrix(bn) for bn in m.bones()}


EAR_REST = {'right_ear': (8.0, 24.0, 10.0), 'left_ear': (8.0, -24.0, -10.0)}


def _hang_ears(pose, swing=0.0):
    """Add ear deltas to `pose` so both ears hang under gravity wherever the head ends up
    (`swing` = extra backward fling in degrees, e.g. a lunge)."""
    wm = _world(pose)
    Rh = wm['head'][:3, :3]
    f = Rh @ np.array([0.0, 0.0, -1.0])
    yaw = math.atan2(-f[0], -f[2])
    for ear, rest in EAR_REST.items():
        Rrest = R_deg(*rest)
        Rt = rot_matrix(0.0, yaw, 0.0) @ R_deg(swing, 0, 0) @ Rrest
        loc = euler_zyx(Rh.T @ Rt)
        pose[ear] = tuple(_wrap(loc[k] - rest[k]) for k in range(3)) + (0.0, 0.0, 0.0)
    return pose


def make_poses():
    poses = {}
    jaws70 = {'jaw_upper_right': P(-26, 34, -12), 'jaw_upper_left': P(-26, -34, 12),
              'jaw_lower_right': P(32, 28, 14), 'jaw_lower_left': P(32, -28, -14)}
    # lunge: neck thrown forward, jaws open 70 deg into a 4-petal maw, ears flung back, front legs reaching
    poses['lunge'] = _merge(jaws70, {
        'neck': P(27, 0, 0), 'head': P(-14, 0, 0, 0, 0, -3),
        'tongue': P(-8, 0, 0), 'tongue_tip': P(-34, 0, 0),
        'right_ear_tip': P(25), 'left_ear_tip': P(25),
        'seg1': P(0, 0, 0, 0, 2.5, 0), 'seg2': P(-4), 'seg3': P(-3), 'seg4': P(4), 'seg5': P(3),
        'front_right_leg': P(-48, 0, 0), 'front_left_leg': P(-40, 0, 0),
        'front_right_paw': P(30), 'front_left_paw': P(25),
        'tail': P(10, 26, 0), 'tail_tip': P(0, 20, 0),
    }, arm_ik(1, 'right', (-17.0, 21.0, -26.0), (-1.0, -1.0, 0.0)),
        arm_ik(1, 'left', (17.0, 21.0, -22.0), (1.0, -1.0, 0.0)))
    _hang_ears(poses['lunge'], 50)
    # coil ("long hug"): every link yawed the same way, alternating strong/soft, with a slight rise and
    # fall, so the body spirals ~3/4 of a turn round the victim on its LEFT (+X); the head rears up and
    # turns in to look down at them; the inner human arms reach in and grab at chest height
    yaw = [('seg2', 40), ('seg3', 32), ('seg4', 40), ('seg5', 32), ('seg6', 40), ('hips', 30)]
    coil = {n: P(-4 if k % 2 else 3, a, 0) for k, (n, a) in enumerate(yaw)}
    coil.update({'seg1': P(0, 30, 0), 'neck': P(-30, -55, 0), 'head': P(55, -20, 8),
                 'jaw_upper_right': P(-16, 14, 0), 'jaw_upper_left': P(-16, -14, 0),
                 'jaw_lower_right': P(20, 14, 0), 'jaw_lower_left': P(20, -14, 0),
                 'tail': P(0, 40, 0), 'tail_tip': P(0, 30, 0), 'tongue_tip': P(-10)})
    wm = _world(coil)
    piv = [wm[n][:3, 3] for n in ('seg1', 'seg2', 'seg3', 'seg4', 'seg5', 'seg6', 'hips')]
    cen = np.mean(np.array(piv), axis=0)
    for idx, seg, *_ in ARMS:
        M = wm[seg]
        segR = M[:3, :3]
        segT = M[:3, 3] - segR @ np.array([0.0, SEG_C[seg], SEGMENT_Z[seg]])
        S = segR @ arm_rig(idx, 'left')['S'] + segT
        dirc = cen - S
        dirc[1] = 0.0
        dirc = dirc / np.linalg.norm(dirc)
        Wt = cen - dirc * 9.0
        Wt[1] = -6.0 - idx * 5.0
        b = math.atan2(-dirc[0], -dirc[2])
        coil.update(arm_ik(idx, 'left', Wt, (0.0, -1.0, 0.0), rot_matrix(0.0, b, 0.0), segR, segT))
    _hang_ears(coil)
    poses['coil'] = coil
    # vomit: neck arched up, snout to the sky, all four flaps peeled open, tongue out, legs braced
    poses['vomit'] = _merge({
        'jaw_upper_right': P(-30, 26, 10), 'jaw_upper_left': P(-30, -26, -10),
        'jaw_lower_right': P(34, 26, -8), 'jaw_lower_left': P(34, -26, 8),
        'neck': P(-24, 0, 0), 'head': P(-30, 0, 0), 'tongue': P(6), 'tongue_tip': P(20),
        'seg1': P(0, 0, 0, 0, -1.5, 0), 'seg2': P(4), 'seg3': P(4), 'seg4': P(-3), 'seg5': P(-3),
        'front_right_leg': P(-22, 0, 8), 'front_left_leg': P(-22, 0, -8),
        'front_right_paw': P(18), 'front_left_paw': P(18), 'tail': P(-20, 0, 0)})
    _hang_ears(poses['vomit'], 10)
    # beg: the funniest one.  The chest sits up straight on the planted body, the stubby front paws beg,
    # the head does the dog tilt, the first pair of human hands are pressed together, the tail wags
    beg = _sit_up(72)
    beg.update({'neck': P(62, 0, 0), 'head': P(6, 6, 22),
                'front_right_leg': P(-6, 0, 4), 'front_left_leg': P(-9, 0, -4),
                'front_right_paw': P(140), 'front_left_paw': P(146),
                'tail': P(-8, 34, 0), 'tail_tip': P(0, 22, 0), 'tongue_tip': P(10, -32, 0)})
    beg.update(_praying_hands())
    _hang_ears(beg)
    poses['beg'] = beg
    # stretch: half length.  Every link slides 10.5 texels into the one in front (the skin bands and part
    # of each fur link disappear), the neck telescopes in, the human arms fold over the back
    dz = -10.5
    st = {n: P(0, 0, 0, 0, 0, dz) for n, *_ in SEGMENTS}
    st['head'] = P(0, 0, 0, 0, 0, 7.0)
    acc, seg_dz = 0.0, {}
    for n, *_ in SEGMENTS:
        acc += dz
        seg_dz[n] = acc
    st.update(_folded_arms(seg_dz))
    st.update({'right_ear': P(0, 0, -4), 'left_ear': P(0, 0, 4), 'tail': P(0, 20, 0)})
    poses['stretch'] = st
    return poses


POSES = make_poses()

ANIM_NOTES = """Choripan, version completa -- animation notes.  Units: radians, offsets in model texels (2x density
inside scale_root: 2 texels = 1 vanilla pixel).  t = ageInTicks, s = walk speed 0..1.  Every pose value is ADDED to the
rest pose (apply(POSE_X, w)).  Golden rule: it is a monster that is still a dog -- the TAIL WAGS IN EVERY STATE (even
while biting, coiling or vomiting) and the ears/tongue flop with dog physics.  Entity length ~4.7 blocks (nose z -75,
tail tip z +78), height ~1.35 blocks; the origin sits under seg3/seg4.

Bones (parent in brackets)
* seg1 (ROOT, pivot at the front of the chest): chest + sweater remnant + the two real dachshund legs.  Follows the
  entity body yaw.  Idle: breathing dy = sin(t*0.08)*0.4.  Chase: dy bob = -abs(sin(walk))*0.8*s, small roll
  zRot = sin(walk)*0.05.
* seg2, seg3, seg4, seg5, seg6, hips [each the child of the previous link; pivot at the FRONT of the link, inside the
  stretched skin band]: the snake chain.  Drive yRot from a position-history buffer: each link's yaw = (heading of the
  path point N ticks behind the previous link) - (previous link heading), N ~ 3 ticks per link at full speed, clamped
  to +-0.9 per joint.  Add a travelling undulation while moving: yRot += sin(t*0.45 - k*0.9)*0.12*s (k = link index),
  xRot += sin(t*0.3 - k*0.8)*0.04 (a lazy vertical wave).  The pink skin band + 2 rib ridges (rest pose authored 6 texels
  long, overlapping 3 texels into the link in front) opens on the OUTSIDE of every bend -- that's the money shot.
* neck [seg1, pivot inside the chest top, rest pitched 35 deg up]: takes 40% of look(); chase: xRot +0.2 (head lower,
  forward).  Can stretch: offsets on 'head' along its z (pose 'lunge' uses dz -3).
* head [neck, pivot at the neck joint under the back of the skull, rest +35 to level it]: 60% of look().  The DOG HEAD
  TILT (zRot +-0.4 snapped in 3 ticks, held 20 ticks) whenever it hears the player's voice / a thrown item lands.
* jaw_upper_right, jaw_upper_left [head, hinge at the back-inner edge of each upper muzzle half, by the eyes]:
  the upper half of the split muzzle, each carrying half of the black nose, overbite needle teeth and whiskers.
  Open = xRot negative (front rises) + yRot outward (right +, left -) + zRot outward.  Rest is ajar (3 deg) so the
  needle slit always shows.  Idle: a twitch every 3-6 s: both upper flaps yRot +-0.08 for 4 ticks (the nose "unzips").
* jaw_lower_right, jaw_lower_left [head, hinge at the throat under the skull]: the two lower halves, nose-to-throat.
  Open = xRot positive + yRot outward.  Chase: the four flaps breathe open/closed: w = 0.15 + 0.15*sin(t*0.5),
  apply(POSE_LUNGE jaws only, w).  Attack (lunge bite): snap to the full 'lunge' jaw values in 3 ticks, CLAMP shut
  (back to rest) in 2 ticks on hit, chomp sound.  Always move the 4 flaps together, upper/lower mirrored.
* tongue [head, root on the floor of the mouth]: black tongue, lies in the lip slit.  Pant while idle/chasing:
  xRot = sin(t*0.6)*0.05, dz = -abs(sin(t*0.6))*1.0.
* tongue_tip [tongue, hangs out of the front, rest 52 deg down]: dog-lolling pendulum, lagged 3 ticks behind the head
  (xRot/yRot +-0.25, zRot from head roll).  'lunge' shoots it forward (xRot -0.6).
* right_ear, left_ear [head, attached low on the back of the skull, turned 24 deg toward the front]: limp pendulums.
  Counter-rotate against head pitch/roll so they keep hanging (the poses already include this), lag 4 ticks,
  amplitude up to 0.5; fling back (xRot +0.9) on the lunge.  right_ear_tip, left_ear_tip [ear]: second pendulum stage,
  2 ticks more lag, half amplitude -- the floppiest thing on the model; they nearly sweep the floor.
* front_right_leg, front_left_leg [seg1]: the original short, bowed dachshund legs.  Normal quadruped trot,
  xRot = +-cos(walk*1.4)*0.9*s (fast, tiny steps -- comic next to the long arms).  front_right_paw, front_left_paw
  [leg]: turned-out feet; flex xRot +0.4 on the back swing; 'beg' curls them down 140 deg (the begging wrists).
* arm_1_right/left [seg3], arm_2_right/left [seg5], arm_3_right/left [hips]: the human upper arms bursting from the
  flanks (torn fur collar at the shoulder).  forearm_K_side [arm]: elbow knob + too-long forearm.  hand_K_side
  [forearm]: flat palm, 4 over-long fingers with black nails, splayed thumb.  Rest stance: elbows above the spine like a
  spider, palms flat on the floor.  Walk as a wave from front to back: pair K lifts when sin(walk*0.9 - K*1.6) > 0:
  arm zRot += 0.35*lift*(right +, left -) (raises the elbow), forearm zRot -= 0.5*lift (folds), hand xRot -0.3*lift
  (palm peels off the floor, fingers last).  Left/right of a pair alternate (phase + PI).  Idle: one random finger
  hand tap every 2-4 s (hand xRot -0.15 for 2 ticks) -- drumming fingers.  Pose tables re-target them by IK (coil:
  the left arms grab inward; beg: pair 1 presses its palms together; stretch: all folded over the back).
* tail [hips], tail_tip [tail]: the tiny dachshund tail, carried up.  WAG ALWAYS: tail yRot = sin(t*1.6)*0.6,
  tail_tip yRot = sin(t*1.6 - 0.8)*0.5; faster (t*2.4) when it sees food/a thrown item, slow (t*0.8) when hurt.
* shred_1 [seg2], shred_2 [seg3], shred_3 [seg4], shred_4 [seg5]: strips of the Nona's red sweater hanging off the
  spine (band + side strips + loose yarn, zero-thickness planes).  Flutter: zRot = sin(t*0.35 + k)*0.08, xRot = -0.25*s
  (streaming back in the chase).
* Emissive layer 'eyes': the milk-white eye discs (dim glow) + the red pinpoint pupils.  Optional: shrink the pupils'
  apparent glow (alpha pulse 0.7..1.0) when it begs, full bright when it lunges.

Poses
* lunge: neck thrown forward and the head pushed 3 texels along it, chest dips, the muzzle peels open ~70 deg in four
  petals (eyes stay visible above the maw), tongue shoots out, ears flung back, front paws and the first pair of arms
  reach forward.  Ease in 3 ticks, hold 6, snap shut.
* coil: the "long hug".  Every link yaws the same way (alternating ~0.7 / 0.55 rad, slight alternating pitch) so the
  body rings ~3/4 of a turn round a victim on its LEFT; the neck rears up and the head looks down into the ring, jaws
  half open; the three left arms reach in and grab at chest height.  In game, feed the real coil from the path buffer
  (the victim's position) and use this table as the target shape; spiral 1.5 turns by adding dy per link.
* vomit: neck arched up, snout to the sky, all four flaps peeled wide, tongue lolling, front legs braced, back
  humped.  Spawn the black ectoplasm column at the head pivot + 18 texels along the snout direction.  Hold while the
  'choripan.vomit' sound plays, add a shudder (seg2..seg6 yRot +-0.05 at t*3).
* beg: THE gag.  seg1 is pitched up 72 deg around the chest's back end (offset already in the table) and seg2 counter-
  rotates so the rest of the 8-legged body stays planted; the stubby paws hang curled in front of the chest, the head
  does the dog tilt, the first pair of human hands press together "por favor" between the paws, tongue out, tail
  wagging hard (keep the wag running on top).  Blend in over 10 ticks when the player holds a chorizo/choripan.
* stretch: the transformation.  w = 1 is HALF length: every link slides 10.5 texels into the one in front (the skin
  bands and ribs vanish inside the fur), the neck telescopes in (head dz +7), and all six human arms are folded over
  the back like a resting spider's legs.  Script: start at w = 1 (also scale the arm/forearm/hand bones from 0 to 1
  over the first 40% of the effect so they "sprout"), then ease w 1 -> 0 one link at a time from the FRONT
  (seg2 first, hips last, 8 ticks apart) with a 'choripan.crack' per link -- the slinky going down the stairs.
  Reverse it (0 -> 1, then scale everything down) for the post-choripan "boing" retraction.
"""
