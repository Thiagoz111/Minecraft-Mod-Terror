"""Muneca Maldita -- cursed antique porcelain doll (DEAD LINE).

Authored at 2x texel density (model.scale = 0.5).  +Y down, ground y = 24, faces -Z.

Design
------
Silhouette: a toddler-proportioned bisque doll whose head is ~45% of its height.  Big round
porcelain head (14x12 face) crowned by a dusty red bow on one side, chestnut sausage ringlets
hanging around it; a narrow burgundy bodice with huge puffed sleeves and a lace bertha collar;
a stiff flared bell skirt (8 angled panels) over a torn lace petticoat; tiny jointed porcelain
legs with ball knees and black Mary Janes.  Arms are too long (hands at knee level) and the
left forearm hangs a little lower than it should, held to the elbow only by the stringing cord.

Face (the jumpscare portrait): the face is a 2-texel porcelain "mask" slab in front of the skull,
so every break in it has real depth.  Left (viewer) side: a glossy blue glass eye set into a
socket under heavy painted lashes, rouge, and the crooked smile curling up.  Right side: a chunk
of the temple/forehead is broken away (through the hair) revealing darkness, the eye is a ragged
black hole leaking a black tear that runs down the cheek and stains the lace collar.  The mouth is
red and sewn shut with black thread; the chin is a marionette jaw (separate bone) that drops open
to reveal tiny bisque teeth and a black throat.
"""
import math

from mcmodel import Model, vnoise, hash3, face_light, pick
from rig import Rig
from paint import hx, mix, scale, pixelart

# ------------------------------------------------------------------ palettes (hand-picked, hue shifted)
PORC = [hx('#2a2530'), hx('#463f4c'), hx('#675f6c'), hx('#8c838e'), hx('#b0a7ad'),
        hx('#cfc6c6'), hx('#e6ded8'), hx('#f7f1e9')]
CHIP = hx('#fffcf6')
CRACK = hx('#3a2f33')
CRACK_D = hx('#1b1417')
GRIME = hx('#7d7069')
ROUGE = [hx('#a5626b'), hx('#bf7a80'), hx('#d39696')]
LIP = [hx('#3c060d'), hx('#650f19'), hx('#8f1c26'), hx('#b52d35')]
THREAD = hx('#0d0809')
TEAR = [hx('#030203'), hx('#0b090c'), hx('#1b1820'), hx('#3a3846')]
VOID = [hx('#000000'), hx('#040305'), hx('#08060a'), hx('#0e0b10')]
GLASS = [hx('#0a1430'), hx('#13265a'), hx('#1d3f8c'), hx('#2f62b8'), hx('#4f8ad8'), hx('#8ec0f2'), hx('#e8f6ff')]
LASH = [hx('#09060a'), hx('#1c1216'), hx('#3a2720')]
MOUTH = [hx('#030102'), hx('#12040a'), hx('#2a0a12'), hx('#4a1420'), hx('#6e2530')]
TEETH = [hx('#6d6458'), hx('#a59b8a'), hx('#d8cfbd'), hx('#f2ecdc')]

HAIR = [hx('#140905'), hx('#24100a'), hx('#3a1b0f'), hx('#532714'), hx('#6d3519'),
        hx('#89461f'), hx('#a65d2c'), hx('#c27e45')]
BOW = [hx('#220a0d'), hx('#3d1216'), hx('#5c1d20'), hx('#7a2c2b'), hx('#954038'), hx('#ad5a4c'), hx('#c27666')]
DRESS = [hx('#12060b'), hx('#230b13'), hx('#38101c'), hx('#4f1725'), hx('#681f2f'),
         hx('#822b3a'), hx('#9b3c48'), hx('#b45558')]
LACE = [hx('#3a332b'), hx('#5d5447'), hx('#857a68'), hx('#ab9f88'), hx('#cbc0a6'), hx('#e2d8bf'), hx('#f2ebd6')]
MUD = [hx('#120c08'), hx('#22170f'), hx('#352516'), hx('#4a3520')]
SHOE = [hx('#040305'), hx('#0b0a0f'), hx('#15131b'), hx('#221f2a'), hx('#3a3646'), hx('#6c6880')]
BRASS = [hx('#3b2a10'), hx('#6e5220'), hx('#a8853a'), hx('#dcc070')]
CORD = [hx('#1a120c'), hx('#33251a'), hx('#4e3a28')]


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


# ------------------------------------------------------------------ porcelain
def porc_value(ctx, base=0.74):
    x, y, z = A(ctx)
    v = base + face_light(ctx) * 1.1
    if edge(ctx) == 0 and ctx.face != 'top':
        v -= 0.06
    g = vnoise(x * 0.22 + 4, y * 0.22, z * 0.22, 3)
    v -= max(0.0, g - 0.58) * 0.55            # soft grime blotches
    cz = vnoise(x * 0.8 + 3, y * 0.8, z * 0.8, 9)
    if abs(cz - 0.5) < 0.022:
        v -= 0.13                              # crazing (hairline glaze cracks)
    return v


def porcelain(ctx):
    return pick(PORC, porc_value(ctx))


def limb_mat(ctx):
    """Porcelain limbs: ball joints shaded round, seams, grime in the joints, a few cracks."""
    x, y, z = A(ctx)
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    t = tag(ctx)
    v = porc_value(ctx, 0.72)
    if t == 'ball':
        # spherical read: darker rim, bright cap
        if ctx.face != 'top':
            v += 0.08 - abs(ly / max(1, h) - 0.4) * 0.35
            if ctx.face in ('front', 'back'):
                v -= abs(lx / max(1, w) - 0.5) * 0.3
            else:
                v -= abs(lz / max(1, d) - 0.5) * 0.3
    if t in ('forearm', 'shin', 'upper'):
        if ly < 0.9 and ctx.face != 'top':
            v -= 0.16                          # socket shadow under the joint
    if t == 'hand' or t == 'finger':
        if ctx.face == 'bottom':
            v -= 0.1
    c = pick(PORC, v)
    if t in ('forearm', 'shin', 'ball', 'upper'):
        cr = vnoise(x * 0.9, y * 0.35, z * 0.9, 17)
        if abs(cr - 0.5) < 0.03 and hash3(int(x * 2), int(y), int(z * 2), 5) > 0.3:
            c = CRACK
    if t == 'finger' and ly > h - 0.9 and ctx.face != 'top':
        c = mix(c, GRIME, 0.6)                  # dirty fingertips
    return c


# ------------------------------------------------------------------ the face
# 14 x 12 front face of the porcelain mask ('.' = broken away / socket, seen through to what is behind)
FACE = [
    # 0123456789ABCD
    "ooooooooocCh..",   # r0  under the fringe; broken temple on the right
    "oooooooocooh..",   # r1
    "wWWWWWoocohh.h",   # r2  heavy painted upper lid + lashes
    "W....Wooch..ho",   # r3  glass eye opening (cols 1-4) | ragged eye hole (cols 9-12)
    "o....eoco....o",   # r4
    "o....oocoh...h",   # r5
    "ruuuurnohk..co",   # r6  lower lid | hole lower rim leaking
    "rRRRRrNNcktrRr",   # r7  rouge, nostrils, crack, tear
    "rRLSlSlSlLktRr",   # r8  sewn upper lip (crooked: rises on the left)
    "orLm......mkro",   # r9  marionette slits either side of the chin
    "ooom......mkoo",   # r10
    "ggom......mtgg",   # r11
]


def face_px(ctx, ch):
    x, y, z = A(ctx)
    i, j = ctx.i, ctx.j
    # roundness: the mask darkens toward its outline, brightest on the cheeks / brow
    cx = (i - 6.5) / 7.0
    cy = (j - 6.0) / 6.0
    base = 0.86 - cx * cx * 0.16 - max(0.0, cy) * cy * 0.12
    if ch == 'o':
        v = base
        g = vnoise(x * 0.3 + 7, y * 0.3, 1, 3)
        v -= max(0.0, g - 0.62) * 0.5
        return pick(PORC, v)
    if ch == 'g':
        return pick(PORC, base - 0.18)
    if ch == 'c':
        return CRACK
    if ch == 'C':
        return CRACK_D
    if ch == 'h':
        return CHIP
    if ch == 'w':
        return LASH[1]
    if ch == 'W':
        return LASH[0]
    if ch == 'e':
        return LASH[2]
    if ch == 'u':
        return mix(pick(PORC, base - 0.06), ROUGE[0], 0.25)
    if ch == 'r':
        return mix(pick(PORC, base), ROUGE[2], 0.55)
    if ch == 'R':
        return ROUGE[1]
    if ch == 'n':
        return pick(PORC, base - 0.12)
    if ch == 'N':
        return mix(ROUGE[0], CRACK, 0.35)
    if ch == 'L':
        return LIP[1]
    if ch == 'l':
        return LIP[3]
    if ch == 'S':
        return THREAD
    if ch == 'm':
        return CRACK_D
    if ch == 'k':
        return TEAR[0]
    if ch == 't':
        return TEAR[2]
    return pick(PORC, base)


def chunk_hit(x, y, z):
    """The broken-away chunk of the right temple, as a 3D region (shared by mask, hair, bow)."""
    if z > -3.6:
        return False
    jag = (hash3(int(math.floor(x)), int(math.floor(y)), 0, 211) - 0.5) * 1.2
    return ((x - 7.6) / 5.0) ** 2 + ((y + 2.6) / 3.9) ** 2 < 1.0 + jag * 0.25


def plate_mat(ctx):
    """The porcelain face mask (front 2 texels of the head)."""
    f = ctx.face
    if f == 'back':
        return None
    if f == 'front':
        ch = FACE[ctx.j][ctx.i]
        if ch == '.':
            return None
        return face_px(ctx, ch)
    x, y, z = A(ctx)
    if chunk_hit(x, y, z):
        return None
    if f == 'bottom':
        if -3 <= x <= 3:
            return None                          # marionette chin slot
        if 4.0 <= x <= 5.0:
            return TEAR[1]                       # black tear dripping off the jaw line
    v = porc_value(ctx, 0.72)
    c = pick(PORC, v)
    if f in ('west', 'east') and 5 <= y <= 9:
        c = mix(c, ROUGE[1], 0.28)
    # chipped rim around the break
    if f in ('top', 'east'):
        dx = 0.4
        if chunk_hit(x + dx, y + dx, z) or chunk_hit(x - dx, y - dx, z) or chunk_hit(x, y + 0.9, z) or chunk_hit(x - 0.9, y, z):
            c = CHIP
    return c


def skull_mat(ctx):
    """Skull behind the mask: black inside (seen through the breaks), porcelain under the jaw line."""
    f = ctx.face
    if f == 'front':
        return pick(VOID, 0.2)
    return porcelain(ctx)


def void_mat(ctx):
    """Darkness inside the broken head; one dying ember of a pupil deep in the hole."""
    return pick(VOID, 0.1 + hash3(ctx.i, ctx.j, ord(ctx.face[0]), 3) * 0.25)


EYEBALL = [
    "nnnn",
    "bKgb",
    "lbbl",
]


def eyeball_mat(ctx):
    if ctx.face != 'front':
        return pick(GLASS, 0.05)
    ch = EYEBALL[ctx.j][ctx.i]
    return {'n': GLASS[1], 'b': GLASS[3], 'K': VOID[0], 'g': GLASS[6], 'l': GLASS[4]}[ch]


EYE_GLOW = pixelart(["    ",
                     " .g ",
                     "l  l"], {'g': hx('#e8f6ff'), 'l': hx('#5f9ae6'), '.': None}, anchor='topleft')

JAW = [
    "SlSlSL",     # lower lip, sewn
    "LoNooo",     # needle punctures under the lip
    "oocooo",
    "gooogg",
]


def jaw_mat(ctx):
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    if f == 'front':
        ch = JAW[ctx.j][ctx.i]
        if ch == 'N':
            return LIP[0]
        return face_px_jaw(ctx, ch)
    if f == 'top':
        # inside of the mouth: gum + a row of tiny bisque teeth at the lip
        if lz < 0.9:
            return pick(TEETH, 0.7) if ctx.i % 2 == 0 else pick(MOUTH, 0.2)
        return pick(MOUTH, 0.55 - lz * 0.12)
    if f == 'back':
        return pick(MOUTH, 0.1)
    c = pick(PORC, porc_value(ctx, 0.7))
    return c


def face_px_jaw(ctx, ch):
    if ch == 'o':
        return pick(PORC, 0.8 - ctx.j * 0.05)
    if ch == 'g':
        return pick(PORC, 0.62)
    if ch == 'c':
        return CRACK
    if ch == 'L':
        return LIP[1]
    if ch == 'l':
        return LIP[3]
    if ch == 'S':
        return THREAD
    return pick(PORC, 0.75)


def mouth_mat(ctx):
    """Throat behind the marionette chin: upper bisque teeth hanging from the lip, then black."""
    if ctx.face == 'front':
        if ctx.j == 0:
            return pick(TEETH, 0.8 - (ctx.i % 2) * 0.35) if ctx.i not in (0, ctx.w - 1) else pick(MOUTH, 0.4)
        return pick(MOUTH, 0.25 - ctx.j * 0.1)
    return pick(MOUTH, 0.05)


# ------------------------------------------------------------------ hair
def hair_v(col, ly, ctx):
    v = 0.42 + hash3(col, 3, 0, 71) * 0.22 + face_light(ctx) * 0.8
    k = hash3(col, 5, 0, 73)
    if k > 0.55 and ((ly + k * 17) % 9) < 1.6:
        v += 0.25                                   # sheen
    if hash3(col, 7, 0, 75) < 0.2:
        v -= 0.18                                   # dark strand gap
    return v


def hair_shell(ctx):
    """Hair cap over the skull: centre parting on top, open over the face and cheeks."""
    f = ctx.face
    x, y, z = A(ctx)
    if f in ('front', 'bottom'):
        return None
    if chunk_hit(x, y, z):
        return None
    if f in ('west', 'east') and z < -3.2 and y > 0.5 - (z + 3.2) * 0.4:
        return None                                  # cheek / temple left bare
    if f == 'top':
        if abs(x + 1.0) < 0.6 and z > -5:
            return pick(PORC, 0.55)                  # parting line
        col = int(math.floor((x + 1) * 1.0)) * 3 + int(z // 3)
        return pick(HAIR, hair_v(col, z, ctx) + 0.05)
    if f in ('west', 'east'):
        col = int(math.floor(z)) + (0 if f == 'west' else 41)
    else:
        col = int(math.floor(x)) + 90
    v = hair_v(col, y, ctx) - clamp((y - 4) / 8) * 0.15
    return pick(HAIR, v)


BANGS = [
    # 9 wide x 3 tall, front of the fringe (row 0 stands above the skull)
    "aBbBaBbBa",
    "bBaBbBaBb",
    "B.bB.Bb.c",
]


def bangs_mat(ctx):
    f = ctx.face
    if f == 'front':
        ch = BANGS[ctx.j][ctx.i]
        if ch == '.':
            return None
        v = {'a': 0.62, 'B': 0.45, 'b': 0.55, 'c': 0.3}[ch] + (0.15 if ctx.j == 0 else 0)
        if ctx.j == 2:
            v -= 0.12
        return pick(HAIR, v)
    if f == 'bottom':
        return pick(HAIR, 0.2)
    if f == 'top':
        return pick(HAIR, 0.68 + (0.1 if ctx.i % 3 == 0 else 0))
    return pick(HAIR, 0.42 + face_light(ctx))


def curl_mat(ctx):
    """Sausage ringlet: diagonal bands wrap around the tube so it reads as a spiral."""
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    if f == 'top':
        return pick(HAIR, 0.45)
    if f == 'bottom':
        return pick(HAIR, 0.22)
    # perimeter coordinate around the tube
    if f == 'front':
        u = lx
    elif f == 'east':
        u = w + lz
    elif f == 'back':
        u = w + d + (w - lx)
    else:
        u = 2 * w + d + (d - lz)
    per = 2 * (w + d)
    phase = (ly * 1.0 + u / per * 3.0 + cseed(ctx) * 0.37) % 3.0
    v = 0.3 + face_light(ctx) * 0.9
    if phase < 1.0:
        v += 0.32                                   # lit crest of the coil
    elif phase < 1.6:
        v += 0.14
    elif phase > 2.4:
        v -= 0.1                                    # shadowed groove
    if f in ('back',):
        v -= 0.06
    v -= clamp(ly / h) * 0.08
    if tag(ctx) == 'tip' and ly > h - 1 and ctx.face != 'bottom':
        v -= 0.1
    return pick(HAIR, v)


def bow_mat(ctx):
    """Dusty faded satin bow: pinched folds at the knot, sun-faded crests, dust in the creases."""
    f = ctx.face
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    t = tag(ctx)
    if is_plane(ctx) and f == 'back':
        return None
    v = 0.55 + face_light(ctx) * 1.1
    if t == 'knot':
        v -= 0.08
        if f == 'front' and ctx.i == 1:
            v -= 0.1
    elif t == 'loop':
        # folds radiate from the knot: darker toward the pinched end
        u = lx / max(1, w)
        if tag2(ctx) == 'r':
            u = 1 - u
        v -= (1 - u) * 0.22
        if f in ('front', 'back', 'top') and abs(ly - h / 2) < 0.6 and u < 0.8:
            v -= 0.12                                # centre crease
        if u > 0.75 and f != 'bottom':
            v += 0.1
    elif t == 'tail':
        if ly > h - 1.2 and ctx.i % 2 == 0:
            return None                              # notched ribbon end
        v -= ly / max(1, h) * 0.15
    if edge(ctx) == 0 and not is_plane(ctx):
        v -= 0.05
    c = pick(BOW, v)
    if vnoise(lx * 0.6 + cseed(ctx), ly * 0.6, lz * 0.6, 33) > 0.66:
        c = mix(c, LACE[2], 0.25)                    # dust
    return c


def tag2(ctx):
    return getattr(ctx.cube, 'side', '')


# ------------------------------------------------------------------ dress
def dress_mat(ctx):
    """Victorian burgundy wool-silk: pleats, wear on edges, grime and mud rising from the hem."""
    x, y, z = A(ctx)
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    t = tag(ctx)
    f = ctx.face
    if is_plane(ctx) and f == 'back':
        return None
    v = 0.56 + face_light(ctx) * 1.1
    if edge(ctx) == 0 and f != 'top' and not is_plane(ctx):
        v -= 0.06
    if t == 'panel':
        if f == 'back':
            return pick(DRESS, 0.12)
        col = ctx.i
        # torn, uneven hem
        cut = h - 1 - (hash3(col // 2, cseed(ctx), 0, 41) > 0.62) * (1 + hash3(col, 1, cseed(ctx), 42) * 1.5)
        if f in ('front', 'west', 'east') and ly > cut + 1:
            return None
        if f == 'front':
            pl = col % 3
            v += (0.1, 0.0, -0.1)[pl]
            if ly > h - 1.6:
                v -= 0.1
            v -= clamp((ly - 1) / h) * 0.12
        if f == 'bottom':
            v -= 0.2
    if t == 'puff':
        # gathered puff: vertical gathers that pinch at top and bottom
        if f in ('front', 'back', 'west', 'east'):
            v += 0.08 * math.sin((ctx.i) * 2.1)
            v -= abs(ly / max(1, h) - 0.45) * 0.35
    if t == 'bodice':
        if f == 'front' and abs(x) < 0.6:
            yy = y - 11.5
            if yy > 0 and int(yy) % 2 == 0:
                return pick(LACE, 0.85)                # pearl buttons
            v -= 0.12
    c = pick(DRESS, v)
    # grime: mud splashed up from the hem, stains
    if t in ('panel', 'core'):
        m = clamp((y - 17.0) / 3.0)
        n = vnoise(x * 0.5, y * 0.4, z * 0.5, 61)
        if n < m * 0.85:
            c = mix(c, MUD[2], 0.55)
    st = vnoise(x * 0.33 + 9, y * 0.33, z * 0.33, 63)
    if st > 0.72:
        c = mix(c, MUD[1], 0.45)
    return c


def lace_mat(ctx):
    """Yellowed lace: scalloped edge, open-work holes, dirt."""
    x, y, z = A(ctx)
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    f = ctx.face
    t = tag(ctx)
    v = 0.66 + face_light(ctx) * 1.0
    if f == 'bottom':
        return None if t in ('collar', 'cuff', 'sock') else pick(LACE, 0.3)
    if f != 'top':
        # scalloped lower edge with eyelet holes
        if ly > h - 1:
            u = ctx.i
            if u % 3 == 2:
                return None
            v -= 0.06
        elif ly > h - 2 and ctx.i % 3 == 1:
            return pick(LACE, 0.25)                    # eyelet (dark)
        if ctx.j == 0:
            v += 0.06
    else:
        if t == 'collar':
            # flat collar seen from above: rings of lace pattern
            r = max(abs(x) / 6.0, abs(z) / 3.5)
            if int(r * 7) % 2 == 0:
                v -= 0.08
    c = pick(LACE, v)
    if vnoise(x * 0.4 + 2, y * 0.4, z * 0.4, 81) > 0.64:
        c = mix(c, MUD[3], 0.35)
    # the black tear stains the collar under the right cheek
    if t == 'collar' and f in ('top', 'front') and 3.0 < x < 5.6 and z < -1.5:
        c = mix(c, TEAR[1], 0.85 if f == 'top' or ly < 1 else 0.5)
    return c


def shoe_mat(ctx):
    """Black patent Mary Jane: glossy highlight, strap, tiny tarnished buckle."""
    x, y, z = A(ctx)
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    f = ctx.face
    v = 0.3 + face_light(ctx) * 1.2
    if f == 'top':
        if lz > d - 3.0:
            # opening of the shoe (the shin stands here)
            v = 0.12
        if 1.2 < (d - lz) < 2.2:
            v = 0.45                                    # strap
    if f in ('front', 'west', 'east') and ly < 0.9:
        v += 0.25                                       # patent gloss
    if f == 'bottom':
        v = 0.05
    c = pick(SHOE, v)
    if f in ('west', 'east') and 1.0 < lz < 2.0 and ly < 1.0 and tag(ctx) == 'shoe':
        c = BRASS[2] if (f == 'east') == (x > 0) else c
    return c


def cord_mat(ctx):
    lx, ly, lz = local(ctx)
    return pick(CORD, 0.4 + face_light(ctx) + (0.3 if int(ly) % 2 == 0 else 0))


# ------------------------------------------------------------------ module contract
DEFAULT_MAT = dress_mat
FOCUS = 'head'


def build():
    r = Rig()

    def box(bone, frm, size, mat=None, inflate=0.0, decals=None, name=None, side=''):
        c = r.box(bone, frm, size, mat=mat, inflate=inflate, decals=decals)
        c.a0 = tuple(float(v) for v in frm)
        c.name = name
        c.side = side
        return c

    bone = r.bone

    # ---------------- body (root): bodice, sash, collar
    bone('body', (0, 15, 0), mat=dress_mat)
    box('body', (-4, 10.5, -2.5), (8, 5, 5), name='bodice')
    box('body', (-4.5, 14.2, -3), (9, 2, 6), name='sash')
    box('body', (-6, 9.8, -3.5), (12, 2, 7), mat=lace_mat, name='collar')
    # sash bow at the back
    box('body', (-4.2, 13.2, 3.0), (3, 3, 2), mat=bow_mat, name='loop', side='l')
    box('body', (1.2, 13.2, 3.0), (3, 3, 2), mat=bow_mat, name='loop', side='r')
    box('body', (-1.0, 13.7, 3.2), (2, 2, 2), mat=bow_mat, name='knot')
    box('body', (-2.5, 15.5, 4.2), (2, 5, 0), mat=bow_mat, name='tail')
    box('body', (0.6, 15.5, 4.0), (2, 6, 0), mat=bow_mat, name='tail')

    # ---------------- skirt: 8 flared panels over a core, petticoat underneath
    bone('skirt', (0, 15.2, 0), parent='body', mat=dress_mat)
    box('skirt', (-4, 15.2, -3), (8, 4, 6), name='core')
    box('skirt', (-5.5, 18.8, -3.5), (11, 2, 7), mat=lace_mat, name='petticoat')
    box('skirt', (-3.5, 18.8, -5.5), (7, 2, 11), mat=lace_mat, name='petticoat')
    panels = [('skirt_front', 0, 3.2), ('skirt_front_right', 45, 3.6), ('skirt_right', 90, 4.0),
              ('skirt_back_right', 135, 3.6), ('skirt_back', 180, 3.2), ('skirt_back_left', -135, 3.6),
              ('skirt_left', -90, 4.0), ('skirt_front_left', -45, 3.6)]
    for k, (name, yaw, rad) in enumerate(panels):
        flare = 27 + (k % 2) * 2
        bone(name, (0, 15.2, 0), parent='skirt', rot=(-flare, yaw, 0), mat=dress_mat)
        box(name, (-3, 15.2, -rad - 1), (6, 5, 1), name='panel')

    # ---------------- legs: hidden thigh, ball knee, short shin, Mary Jane
    for side, sx, yaw in (('right', -1, 8), ('left', 1, -14)):
        lb = f'{side}_leg'
        cx = 2.2 * sx
        bone(lb, (cx, 18, 0), parent='body', rot=(0, yaw, 0), mat=limb_mat)
        box(lb, (cx - 1.5, 17.5, -1.5), (3, 3, 3), name='upper')
        box(lb, (cx - 2, 20, -2), (4, 2, 4), name='ball', inflate=0.1)
        box(lb, (cx - 1.5, 21.6, -1.5), (3, 2, 3), name='shin')
        box(lb, (cx - 1.5, 21.4, -1.5), (3, 1, 3), mat=lace_mat, name='sock', inflate=0.35)
        box(lb, (cx - 2, 22, -3.5), (4, 2, 6), mat=shoe_mat, name='shoe')

    # ---------------- arms: puffed sleeve, lace cuff, ball elbow, long porcelain forearm, spidery hand
    for side, sx in (('right', -1), ('left', 1)):
        ab, fb = f'{side}_arm', f'{side}_forearm'
        ax = 5.0 * sx
        bone(ab, (ax, 11.6, 0), parent='body', rot=(4 if sx < 0 else -3, 0, 13 * -sx), mat=limb_mat)
        box(ab, (ax - 2 + 0.6 * sx, 10.2, -2), (4, 4, 4), mat=dress_mat, name='puff', inflate=0.3)
        box(ab, (ax - 2 + 0.6 * sx, 13.9, -2), (4, 1, 4), mat=lace_mat, name='cuff', inflate=0.25)
        box(ab, (ax - 1.5 + 0.6 * sx, 14.2, -1.5), (3, 2, 3), name='upper')
        box(ab, (ax - 1.5 + 0.6 * sx, 15.8, -1.5), (3, 2, 3), name='ball', inflate=0.2)
        ex = ax + 0.6 * sx
        broken = sx > 0
        fy = 17.0 + (1.3 if broken else 0)
        bone(fb, (ex, fy, 0), parent=ab, rot=((6, 0, -5) if broken else (-6, 0, 2)), mat=limb_mat)
        if broken:
            box(fb, (ex - 0.5, fy - 1.6, -0.5), (1, 2, 1), mat=cord_mat, name='cord')
        box(fb, (ex - 1.5, fy, -1.5), (3, 3, 3), name='forearm')
        box(fb, (ex - 1.3, fy + 2.8, -1.3), (3, 2, 3), name='ball', inflate=-0.2)
        box(fb, (ex - 1.5, fy + 4.4, -1.5), (3, 2, 2), name='hand')
        for k, fx in enumerate((-1.5, -0.5, 0.5)):
            ln = 2 + (1 if k == 1 else 0)
            box(fb, (ex + fx, fy + 6.2, -1.4), (1, ln, 1), name='finger')
        box(fb, (ex - 1.5 if sx > 0 else ex + 0.5, fy + 5.4, -2.2), (1, 2, 1), name='finger')

    # ---------------- head: porcelain mask + skull + hair, bow, marionette jaw
    bone('head', (0, 10, 0.5), parent='body', rot=(0, 0, -7), mat=porcelain)
    box('head', (-7, -2, -6), (14, 12, 2), mat=plate_mat, name='plate')
    box('head', (-7, -2, -4), (14, 12, 10), mat=skull_mat, name='skull')
    box('head', (1.5, -1.5, -5.5), (5, 7, 2), mat=void_mat, name='void',
        decals={'eyes:front': pixelart(["     ", "     ", "     ", "     ", "  e  "],
                                       {'e': hx('#8a1a14')}, anchor='topleft')})
    box('head', (-6, 1, -5.4), (4, 3, 2), mat=eyeball_mat, name='eyeball', decals={'eyes:front': EYE_GLOW})
    box('head', (-3, 6.8, -4.6), (6, 3, 1), mat=mouth_mat, name='throat')
    box('head', (-7, -2, -6), (14, 12, 12), mat=hair_shell, inflate=0.6, name='shell')
    box('head', (-7, -3, -7), (9, 3, 1), mat=bangs_mat, name='bangs')

    bone('jaw', (0, 7, -4), parent='head', mat=jaw_mat)
    box('jaw', (-3, 7, -6), (6, 4, 2), name='chin')

    # bow on the doll's right temple
    bone('bow', (-4.5, -2.5, -1.0), parent='head', rot=(-8, 18, -26), mat=bow_mat)
    box('bow', (-5.5, -4.0, -2.0), (2, 3, 2), name='knot')
    box('bow', (-10.0, -5.0, -2.0), (4, 4, 2), name='loop', side='l')
    box('bow', (-3.5, -5.0, -2.0), (4, 4, 2), name='loop', side='r')
    box('bow', (-6.0, -1.5, -1.8), (2, 5, 0), name='tail')
    box('bow', (-4.0, -1.5, -1.4), (2, 4, 0), name='tail')

    # ringlets: 3 on the right, 2 on the (broken) left, 4 down the back
    curls = [('curl_r1', (-8.2, 1.0, -2.2), 9, (0, 0, 8)), ('curl_r2', (-8.0, 1.5, 0.8), 11, (6, 0, 6)),
             ('curl_r3', (-7.6, 1.0, 3.6), 10, (10, 0, 4)),
             ('curl_l1', (8.2, 2.0, 0.6), 8, (4, 0, -8)), ('curl_l2', (7.8, 1.0, 3.6), 11, (10, 0, -5)),
             ('curl_b1', (-4.5, 3.0, 7.0), 12, (14, 0, 4)), ('curl_b2', (-1.5, 3.5, 7.4), 13, (12, 0, 1)),
             ('curl_b3', (1.5, 3.0, 7.4), 12, (13, 0, -2)), ('curl_b4', (4.5, 3.5, 7.0), 10, (15, 0, -5))]
    for name, (px, py, pz), ln, rot in curls:
        bone(name, (px, py, pz), parent='head', rot=rot, mat=curl_mat)
        box(name, (px - 1.5, py - 1, pz - 1.5), (3, ln, 3), name='coil')
        box(name, (px - 1, py - 1 + ln, pz - 1), (2, 2, 2), name='tip')

    m = Model('muneca', 128, 128, r.roots)
    m.scale = 0.5
    return m


POSES = {
    # head tilted ~40 deg, the intact right arm raised toward the viewer, fingers reaching
    'creep': {'head': (0.05, 0.15, 0.7, 0, 0, 0), 'right_arm': (-1.75, 0.15, -0.15, 0, 0, 0),
              'right_forearm': (-0.25, 0, 0, 0, 0, 0), 'left_arm': (0.1, 0, -0.1, 0, 0, 0),
              'jaw': (0.15, 0, 0, 0, 0, 0)},
    'attack': {'body': (0.35, 0, 0, 0, 0.5, -1), 'head': (-0.45, 0, 0.25, 0, 0, 0), 'jaw': (0.85, 0, 0, 0, 0, 0),
               'right_arm': (-2.1, 0, 0.35, 0, 0, 0), 'left_arm': (-2.0, 0, -0.35, 0, 0, 0),
               'right_forearm': (-0.3, 0, 0, 0, 0, 0), 'left_forearm': (-0.3, 0, 0, 0, 0, 0),
               'right_leg': (-0.45, 0, 0, 0, 0, 0), 'left_leg': (0.4, 0, 0, 0, 0, 0)},
    'scream': {'head': (-0.35, 0, -0.1, 0, 0, 0), 'jaw': (1.0, 0, 0, 0, 0, 0),
               'right_arm': (0, 0, 0.9, 0, 0, 0), 'left_arm': (0, 0, -0.9, 0, 0, 0),
               'right_forearm': (0, 0, 0.3, 0, 0, 0), 'left_forearm': (0, 0, -0.3, 0, 0, 0)},
    'sit': {'body': (0, 0, 0, 0, 4.5, 0), 'right_leg': (-1.5, 0.2, 0, 0, 0, 0), 'left_leg': (-1.5, -0.25, 0, 0, 0, 0),
            'head': (0.2, 0, 0.35, 0, 0, 0), 'right_arm': (0, 0, -0.1, 0, 0, 0), 'left_arm': (0, 0, 0.1, 0, 0, 0)},
}

ANIM_NOTES = "todo"
