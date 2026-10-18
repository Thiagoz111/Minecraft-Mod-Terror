"""La Llorona -- the drowned Weeping Woman of the river (DEAD LINE).

Authored at 2x texel density (model.scale = 0.5).  +Y down, ground y = 24, faces -Z.
Silhouette: hunched drowned bride, too-long neck thrust forward, lolled skull with a dislocated
wailing jaw, curtain of wet black hair, over-long arms with spider hands, flared bell skirt whose
hem is shredded into hanging strips caked in river mud and algae, torn tulle veil behind.
"""
import math

from mcmodel import Model, vnoise, hash3, face_light, pick
from rig import Rig
from paint import hx, mix, scale, pixelart

# ------------------------------------------------------------------ palettes (hand-picked, hue shifted)
SKIN = [hx('#10111a'), hx('#212535'), hx('#363e50'), hx('#515d6c'), hx('#6f7d89'),
        hx('#8e9ca4'), hx('#afbcbf'), hx('#d0dad7')]
LIVOR = hx('#4d3b62')
VEIN = hx('#2a3866')
DRESS = [hx('#1d1e24'), hx('#33353c'), hx('#4d5057'), hx('#6c6e72'), hx('#8f8f8c'),
         hx('#b2afa5'), hx('#cfcabb'), hx('#e8e3d3')]
WET = hx('#53606e')
STAIN = hx('#77653f')
MUD = [hx('#110c08'), hx('#20170e'), hx('#322416'), hx('#46341f'), hx('#5b4529')]
ALGAE = [hx('#151b10'), hx('#202a16'), hx('#2d3a1c'), hx('#3d4b22'), hx('#4f5c2a'), hx('#646f34')]
HAIR = [hx('#030305'), hx('#07080c'), hx('#0d0f15'), hx('#151922'), hx('#1f2430'), hx('#2d3445'), hx('#47526b')]
MOUTH = [hx('#020102'), hx('#0c0305'), hx('#1e070c'), hx('#3a0f16'), hx('#5c1d28'), hx('#83343f')]
TEETH = [hx('#2b2620'), hx('#4d4538'), hx('#736a57'), hx('#9a927c'), hx('#bdb6a0')]
NAIL = [hx('#09090c'), hx('#15141a'), hx('#242129'), hx('#38333d')]
LACE = [hx('#6a6c72'), hx('#929392'), hx('#b8b5ab'), hx('#d8d3c5'), hx('#f0ebdd')]
BLOSSOM = [hx('#2a2118'), hx('#4a3b2a'), hx('#7a6a50'), hx('#a89878'), hx('#cfc3a2')]


def clamp(v, a=0.0, b=1.0):
    return a if v < a else b if v > b else v


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


def is_plane(ctx):
    return 0 in ctx.cube.size


def edge(ctx):
    return min(ctx.i, ctx.j, ctx.w - 1 - ctx.i, ctx.h - 1 - ctx.j)


def tag(ctx):
    return ctx.cube.name or ''


def cseed(ctx):
    """Deterministic per-cube seed."""
    o, sz = ctx.cube.origin, ctx.cube.size
    return int(abs(o[0]) * 13.1 + abs(o[1]) * 7.3 + abs(o[2]) * 3.7 + sz[0] * 31 + sz[1] * 17 + sz[2] * 5) % 9973


# ------------------------------------------------------------------ materials
def skin_mat(ctx):
    """Drowned, bloated blue-grey skin: livor blotches, veins, bony highlights, wrinkled fingers."""
    x, y, z = ctx.pos
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    b = ctx.bone.name
    t = tag(ctx)
    v = 0.62 + face_light(ctx) * 1.15
    if edge(ctx) == 0 and ctx.face != 'top':
        v -= 0.07
    v -= (ly / max(1.0, h)) * 0.06
    m = vnoise(x * 0.21 + 11, y * 0.21, z * 0.21, 5)
    livor = m > 0.66
    if livor:
        v -= 0.08
    if t in ('knob', 'collar', 'knuckle') and ctx.face in ('front', 'top', 'west', 'east'):
        v += 0.1 if ly < max(1.0, h * 0.5) else -0.02
    if 'finger' in b or 'thumb' in b:
        v -= 0.04 + (ly / max(1.0, h)) * 0.08
        if (int(ly) % 2 == 1) and ctx.face != 'bottom':
            v -= 0.06
    if b.endswith('forearm'):
        v -= 0.02 + clamp((ly - 10) / 8) * 0.06
    c = pick(SKIN, v)
    if livor:
        c = mix(c, LIVOR, 0.3)
    if b in ('neck', 'right_forearm', 'left_forearm', 'right_hand', 'left_hand', 'chest', 'right_arm', 'left_arm'):
        vn = abs(vnoise(x * 0.38, y * 0.085, z * 0.38, 23) - 0.5)
        if vn < 0.03:
            c = mix(c, VEIN, 0.55)
    return c


def skull_mat(ctx):
    """Skull cube: skin, but its underside behind the lips is the wet palate seen through the wail."""
    if ctx.face == 'bottom':
        lx, ly, lz = local(ctx)
        w = ctx.cube.size[0]
        if lz < 9 and abs(lx - w / 2) < 5:
            if lz < 1:
                return pick(MOUTH, 0.62)  # upper gum line
            return pick(MOUTH, 0.25 + (1 - abs(lx - w / 2) / 5) * 0.2 - lz * 0.02)
    return skin_mat(ctx)


def nail_tip(ctx):
    lx, ly, lz = local(ctx)
    h = ctx.cube.size[1]
    if ly > h - 1.6:
        return pick(NAIL, 0.25 + face_light(ctx) + (0.4 if ctx.face == 'front' and ly < h - 0.6 else 0))
    return skin_mat(ctx)


def throat_mat(ctx):
    """Throat: a black hole with only a hint of wet red at its rim."""
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    if ctx.face == 'front':
        cx = abs(lx - w / 2) / (w / 2)
        return pick(MOUTH, 0.02 + cx * cx * 0.3 + clamp((ly - h + 2) / 2) * 0.25)
    if ctx.face in ('west', 'east', 'top'):
        return pick(MOUTH, 0.12 + (1 - lz / max(1, d)) * 0.25)
    return pick(MOUTH, 0.05)


def tongue_mat(ctx):
    """Jaw: skin outside, wet gums/tongue on the inside (top face)."""
    if ctx.face == 'top':
        lx, ly, lz = local(ctx)
        w, h, d = ctx.cube.size
        cx = abs(lx - w / 2)
        if cx > w / 2 - 1.2:
            return skin_mat(ctx)
        if lz < 1.2:
            return pick(MOUTH, 0.7)  # lower gum line
        return pick(MOUTH, 0.22 + (1 - cx / (w / 2)) * 0.25 - lz * 0.03)
    if ctx.face == 'back':
        return pick(MOUTH, 0.08)
    return skin_mat(ctx)


def tooth_mat(ctx):
    lx, ly, lz = local(ctx)
    h = ctx.cube.size[1]
    v = 0.62 + face_light(ctx) - (ly / max(1, h)) * 0.3
    if 'rot' in tag(ctx):
        v -= 0.3
    return pick(TEETH, v)


def hair_value(ctx, col, ly):
    v = 0.3 + hash3(col, 3, 0, 71) * 0.3 + face_light(ctx) * 0.5
    k = hash3(col, 5, 0, 73)
    if k > 0.6 and ((ly + k * 23) % 12) < 2.2:
        v += 0.45
    if hash3(col, 7, 0, 75) < 0.22:
        v -= 0.2
    return v


def hair_mat(ctx):
    """Wet black hair; strands follow the cube's long (Y) axis; ragged tips cut by alpha."""
    if is_plane(ctx) and ctx.face == 'back':
        return None
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    if ctx.face in ('west', 'east'):
        col = math.floor(lz) + 50 + (0 if ctx.face == 'west' else 31)
    else:
        col = math.floor(lx)
    col += int(hash3(cseed(ctx), 0, 0, 1) * 97)
    if ctx.face in ('top', 'bottom') and h > 6:
        return pick(HAIR, 0.22 + face_light(ctx))
    if h > 6 and tag(ctx) != 'root':
        tip = h - 1 - hash3(col, 9, 0, 77) * min(9.0, h * 0.3)
        if ly > tip:
            return None
        if ly > tip - 2.5:
            return pick(HAIR, hair_value(ctx, col, ly) - 0.12)
    return pick(HAIR, hair_value(ctx, col, ly))


def hair_shell(ctx):
    """Hair plastered over the skull: centre part, open over the face."""
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    if ctx.face == 'bottom':
        return None
    if ctx.face == 'front':
        cx = abs(lx - w / 2)
        if cx < 1.0:
            return None if ly > 0.5 else pick(SKIN, 0.4)
        if ly > 0.6 + (cx - 1) * 0.6:
            return None
        return pick(HAIR, 0.3 + face_light(ctx) + (0.3 if int(lx) % 4 == 1 else 0))
    if ctx.face == 'top':
        if abs(lx - w / 2) < 0.6 and lz < d * 0.6:
            return pick(SKIN, 0.42)
        col = math.floor(lx * 1.0) + math.floor(lz / 4) * 7
        sheen = 0.35 if (hash3(col, 2, 0, 82) > 0.7 and int(lz) % 5 == 2) else 0
        return pick(HAIR, 0.36 + hash3(col, 1, 0, 81) * 0.25 + sheen)
    if ctx.face in ('west', 'east'):
        col = math.floor(lz) + (0 if ctx.face == 'west' else 40)
    else:
        col = math.floor(lx) + 90
    return pick(HAIR, hair_value(ctx, col, ly))


def veil_mat(ctx):
    """Sheer tulle gathered at the crown, scalloped embroidered border, torn and muddy at the bottom."""
    if ctx.face == 'back':
        return None
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    if tag(ctx) == 'veil_lo':
        ly, h = ly + 22, h + 22
        lx -= 2
        w -= 4
    ix, iy = int(lx), int(ly)
    cx = abs(lx - w / 2)
    hw = 4.5 + ly * 0.45 if tag(ctx) == 'veil_hi' else 14
    if cx > hw:
        return None
    tear = h - 1 - hash3(ix // 2, 1, 0, 91) * 14 - (9 if hash3(ix // 3, 2, 0, 92) > 0.7 else 0)
    if ly > tear:
        return None
    if vnoise(lx * 0.25, ly * 0.1, 0, 93) > 0.71 and ly > 10:
        return None
    rim = hw - cx
    fold = (ix // 2) % 3
    if rim < 1.6 or (iy >= tear - 2):
        if (iy + ix) % 3 == 0:
            return None
        v, a = 0.78 - (ly / h) * 0.35, 205
    else:
        # floral sprigs scattered in the tulle
        sx, sy = (ix + (iy // 11) * 4) % 9, iy % 11
        if (sx - 4) ** 2 + (sy - 5) ** 2 <= 1:
            v, a = 0.8 - (ly / h) * 0.3, 175
        else:
            v, a = 0.6 - (ly / h) * 0.3 + fold * 0.06, 52 + fold * 16
    c = pick(LACE, v)
    if ly > h * 0.45 and vnoise(lx * 0.35, ly * 0.18, 3, 94) > 0.56:
        c = mix(c, MUD[3], 0.6)
        a = min(255, a + 50)
    return (c[0], c[1], c[2], a)


def blossom_mat(ctx):
    """Dead orange-blossom wreath."""
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    v = 0.62 + face_light(ctx) * 1.2
    if edge(ctx) == 0 and ctx.face != 'top':
        v -= 0.22
    if hash3(ctx.i + cseed(ctx), ctx.j, ord(ctx.face[0]), 61) > 0.72:
        v -= 0.3  # browned, rotting petal
    return pick(BLOSSOM, v)


def dress_mat(ctx):
    """Rotten wedding satin: folds, wet cling, tidelines, river mud and algae from the hem."""
    x, y, z = ctx.pos
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    b = ctx.bone.name
    t = tag(ctx)
    ang = math.atan2(x, -z)
    plane = is_plane(ctx)
    if plane and ctx.face == 'back':
        return None
    skirt = b.startswith('skirt') or t == 'tatter'

    if t == 'panel':
        hw = 0.414 * (5.5 + ly * 0.27) + 1.4
        if abs(lx - w / 2) > hw:
            return None
        col = int(lx // 2)
        cut = h - 1 - hash3(col, int(b[-1]), 0, 41) * 6
        if ly > cut:
            return None
    if t == 'tatter':
        col = int(lx)
        cut = h - hash3(col, int(abs(x) * 7 + abs(z) * 3), 0, 43) * min(5, h * 0.4)
        if ly > cut:
            return None
        if 0.5 < lx < w - 0.5 and hash3(col, int(ly), 1, 44) > 0.9:
            return None
    if t == 'sleeve':
        if ctx.face in ('bottom', 'top'):
            return None
        if ly > h - 1 - hash3(int(lx + lz * 3), 0, 0, 46) * 5:
            return None
        if (int(lx + lz) + int(ly)) % 3 == 0 or vnoise(lx * 0.7, ly * 0.5, lz * 0.7, 45) > 0.66:
            return None
        c = pick(LACE, 0.62 + face_light(ctx) - ly / h * 0.3)
        return (c[0], c[1], c[2], 190)
    if t == 'puff':
        if ctx.face == 'bottom':
            return None
        if ctx.face != 'top' and ly > h - 1 - hash3(int(lx + lz * 2), 0, 0, 47) * 3.5:
            return None

    v = 0.66
    if not plane:
        v += face_light(ctx) * 1.1
    if edge(ctx) == 0 and not plane and ctx.face != 'top':
        v -= 0.05
    if skirt or b == 'body':
        u = ang * 5.2 + vnoise(ang * 2.2, y * 0.05, 0, 47) * 2.2
    else:
        u = x * 0.55 + vnoise(x * 0.3, y * 0.1, z * 0.3, 48) * 1.6
    fold = math.sin(u * 2.0)
    v += fold * 0.09
    if fold < -0.82:
        v -= 0.12
    if skirt and ctx.face == 'back':
        v -= 0.26
    wetness = clamp((y + 10) / 32)
    v -= wetness * 0.14
    c = pick(DRESS, v)
    cling = vnoise(x * 0.15 + 5, y * 0.09, z * 0.15, 49)
    if cling > 0.6:
        c = mix(c, WET, 0.35 + (cling - 0.6))
    tl = y + vnoise(ang * 2.0, 0, 0, 50) * 6
    if y > -10 and (tl % 9.0) < 0.8:
        c = mix(c, STAIN, 0.38)
    drip = hash3(int((ang + 4) * 13), 0, 0, 51)
    mud_top = 12 - vnoise(ang * 2.5, 0, 0, 52) * 6 - (drip * 10 if drip > 0.72 else 0)
    if y > mud_top:
        mv = 0.55 + (0 if plane else face_light(ctx)) - clamp((y - mud_top) / 9) * 0.3
        if (int(y) + int(ang * 30)) % 5 == 0:
            mv += 0.12
        c = pick(MUD, mv)
    elif y > mud_top - 6:
        a = vnoise(ang * 6, y * 0.25, 0, 53)
        if a > 0.48:
            c = mix(c, pick(ALGAE, 0.3 + (a - 0.48) * 2.0 + (y - mud_top + 6) / 12), 0.85)
    if skirt and ctx.face == 'back':
        c = scale(c, 0.8)
    return c


def bodice_mat(ctx):
    """Soaked bodice; low neckline showing the bony sternum; wet fabric clinging to the ribs."""
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    if ctx.face in ('front', 'top') and tag(ctx) != 'blade':
        cx = abs(lx - w / 2)
        if ctx.face == 'top':
            if lz < d * 0.55 and cx < 6:
                return skin_mat(ctx)
        elif ly < 3.4 - cx * 0.2 or ly < 5.2 - cx * 1.0:
            return skin_mat(ctx)
    c = dress_mat(ctx)
    if ctx.face == 'front' and tag(ctx) != 'blade':
        cx = abs(lx - w / 2)
        top = max(3.4 - cx * 0.2, 5.2 - cx * 1.0)
        if top <= ly < top + 1.0:
            c = pick(LACE, 0.72 if int(lx) % 2 else 0.5)
        elif ly > top + 1.0:
            c = mix(c, WET, 0.45)  # soaked through: grey, skin showing
    return c


def rib_mat(ctx):
    """Ribs pressing through the soaked fabric: wet grey, lit top edge, dark groove under."""
    c = mix(dress_mat(ctx), WET, 0.4)
    if ctx.face == 'top':
        return mix(c, pick(SKIN, 0.75), 0.4)
    if ctx.face == 'bottom':
        return scale(c, 0.45)
    return c


def sash_mat(ctx):
    lx, ly, lz = local(ctx)
    v = 0.5 + face_light(ctx) + (0.12 if int(ly) == 1 else 0) - (0.15 if edge(ctx) == 0 else 0)
    return mix(pick(DRESS, v), WET, 0.3)


# ------------------------------------------------------------------ face pixel art
FPAL = {
    '1': SKIN[0], '2': SKIN[1], '3': SKIN[2], '4': SKIN[3], '5': SKIN[4], '6': SKIN[5], '7': SKIN[6], '8': SKIN[7],
    'K': (2, 2, 5, 255), 'k': (16, 14, 26, 255), 'W': (248, 252, 255, 255), 'w': (104, 122, 150, 255),
    'T': (4, 4, 8, 255), 't': (30, 32, 46, 255),
    'L': (60, 46, 78, 255), 'l': (118, 104, 132, 255), 'r': (110, 44, 58, 255), 'p': (58, 44, 80, 255),
    'M': MOUTH[0], 'm': MOUTH[2], 'R': MOUTH[4],
    'h': HAIR[1], 'H': HAIR[4],
}

#            0123456789012345   (col 0 = x -8 = viewer's left)
SKULL_FACE = [
    "hhhhhhh44hhhhhhh",
    "hhhhh3455543hhhh",
    "hhh3455665t43hhh",
    "h2345t66556t432h",
    "2344556666554432",
    "2334455555544332",
    "1223334444333221",
    "2pkKKKk33kKKKkp2",
    "2kKKKKK33KKWKKk2",
    "pKKKKKK33KKwKKKp",
    "pKKKWKK33KKKKKKp",
    "2prKwkr33rkKKrp2",
    "334T44333334T433",
    "334T432KK234T433",
    "333TlLLLLLLlT333",
    "23TlLmMMMMmLlT32",
]

BROW = [
    "33445652566443",
    "2t3455t2554t32",
    "12233344332221",
]
BROW_BOTTOM = ["11111111111111", "22222222222222"]

#          0123456789
JAW_FRONT = [
    "lLmMMMMmLl",
    "TlLLmmLLlT",
    "T3llLLll3T",
    "t44llll44t",
    "4T455554T4",
    "4t456654t4",
    "34t5665t43",
    "3345665433",
    "1223443221",
]

CHIN = [
    "t45665t",
    "3456654",
    "3345543",
    "1223321",
]
CHEEKBONE = ["677", "456"]
NOSE = ["34", "45", "56", "56", "67", "34"]
NOSE_BOTTOM = ["KK", "2K"]


def eyes_glow(img, u0, v0, w, h):
    """Emissive layer: only the two pin pupils (+ a dim under-glow)."""
    px = img.load()
    for (i, j) in ((4, 10), (11, 8)):
        px[u0 + i, v0 + j] = (240, 248, 255, 255)
    for (i, j) in ((4, 11), (11, 9)):
        px[u0 + i, v0 + j] = (70, 96, 140, 255)


DEFAULT_MAT = dress_mat
FOCUS = 'head'

UP = 4  # everything above the waist is shifted this many texels down (keeps the height at 2.7 blocks)


def build():
    r = Rig()

    def box(bone, frm, size, mat=None, inflate=0.0, decals=None, name=None):
        c = r.box(bone, (frm[0], frm[1] + up[0], frm[2]), size, mat=mat, inflate=inflate, decals=decals)
        c.name = name
        return c

    def bone(name, pivot, parent=None, rot=(0, 0, 0), mat=None):
        return r.bone(name, (pivot[0], pivot[1] + up[0], pivot[2]), parent=parent, rot=rot, mat=mat)

    up = [0]
    # ---------------- body: waist sash + petticoat core (the floating anchor)
    bone('body', (0, -12, 0), mat=dress_mat)
    box('body', (-6, -16, -4.5), (12, 4, 9), mat=sash_mat)
    box('body', (-5.5, -12, -5), (11, 10, 10), name='core')
    box('body', (-6, -2, -6), (12, 12, 12), name='core')
    box('body', (-7, 10, -7), (14, 8, 14), name='core')

    # ---------------- skirt gores (8 flared panels around the hips) with hanging shreds
    flare = [-14, -17, -12, -18, -13, -16, -11, -17]
    lens = [31, 29, 32, 28, 31, 30, 33, 29]
    for k in range(8):
        name = f'skirt_{k}'
        bone(name, (0, -14, 0), parent='body', rot=(flare[k], k * 45 + (3 if k % 2 else -2), 0), mat=dress_mat)
        rr = 5.5 + (0.5 if k % 2 else 0)
        box(name, (-6, -14, -rr - 1), (12, lens[k], 1), name='panel')
        for s in range(3):
            sx = -5 + s * 4 + (k % 3) - 1
            ln = 4 + int(hash3(k, s, 0, 7) * 4)
            box(name, (sx, -14 + lens[k] - 3, -rr - 0.6 - s * 0.15), (2 + (s + k) % 2, ln, 0), name='tatter')

    up[0] = UP
    # ---------------- chest (hunched forward, one shoulder dropped)
    bone('chest', (0, -17, 0), parent='body', rot=(15, -3, 3), mat=dress_mat)
    box('chest', (-5, -26, -4), (10, 9, 8))
    box('chest', (-7.5, -38, -5.5), (15, 12, 11), mat=bodice_mat)
    box('chest', (-7, -37, -6.2), (6, 1, 1), mat=skin_mat, name='collar')
    box('chest', (1, -37, -6.2), (6, 1, 1), mat=skin_mat, name='collar')
    for yy in (-32, -30, -28):
        for sgn in (-1, 1):
            box('chest', (1 if sgn > 0 else -4, yy, -6.1), (3, 1, 1), mat=rib_mat)
            box('chest', (4 if sgn > 0 else -7, yy + 1, -6.0), (3, 1, 1), mat=rib_mat)
    box('chest', (-7, -38, 3), (6, 7, 3), mat=bodice_mat, name='blade')
    box('chest', (1, -38, 3), (6, 7, 3), mat=bodice_mat, name='blade')
    for yy in (-39, -36, -33, -30):
        box('chest', (-1, yy, 4.6), (2, 2, 2 if yy < -34 else 1), mat=skin_mat, name='knob')

    # ---------------- neck (too long, thrust forward)
    bone('neck', (0, -37, 0.5), parent='chest', rot=(28, 0, 2), mat=skin_mat)
    box('neck', (-3, -52, -2.5), (6, 15, 6))
    box('neck', (-3.2, -50, -3.0), (1, 12, 1), name='knob')
    box('neck', (2.2, -50, -3.0), (1, 12, 1), name='knob')

    # ---------------- head (big skull, lolled sideways)
    bone('head', (0, -51, 0.5), parent='neck', rot=(-40, 5, 10), mat=skin_mat)
    box('head', (-8, -67, -7.5), (16, 16, 15), mat=skull_mat,
        decals={'front': pixelart(SKULL_FACE, FPAL, anchor='topleft'), 'eyes:front': eyes_glow})
    box('head', (-8, -67, -7.5), (16, 16, 15), mat=hair_shell, inflate=0.6)
    box('head', (-7, -63, -9.5), (14, 3, 2), decals={'front': pixelart(BROW, FPAL, anchor='topleft'),
                                                    'bottom': pixelart(BROW_BOTTOM, FPAL, anchor='topleft')})
    box('head', (-1, -60, -9.5), (2, 6, 2), decals={'front': pixelart(NOSE, FPAL, anchor='topleft'),
                                                   'bottom': pixelart(NOSE_BOTTOM, FPAL, anchor='topleft')})
    box('head', (-8, -55, -8.5), (3, 2, 1), decals={'front': pixelart(CHEEKBONE, FPAL, anchor='topleft')})
    box('head', (5, -55, -8.5), (3, 2, 1), decals={'front': pixelart(CHEEKBONE, FPAL, anchor='topleft', flip=True)})
    box('head', (-4, -52, -4.5), (8, 8, 6), mat=throat_mat)
    for tx, th, rot in ((-3, 2, ''), (2, 1, 'rot')):
        box('head', (tx, -52, -7.2), (1, th, 1), mat=tooth_mat, name=rot)
    # wet hair hanging from the nape, covering the back of the long neck
    box('head', (-7.5, -58, 3.5), (15, 18, 3), mat=hair_mat)
    # wet hair hanging beside the face: separate strands on their own bones (kept hanging by the animator)
    for side, sx, lens in (('right', -1, (26, 21, 17)), ('left', 1, (29, 23, 15))):
        hb = f'hair_side_{side}'
        bone(hb, (9.0 * sx, -64, -3), parent='head', rot=(-4, 0, -9), mat=hair_mat)
        for k, (ln, z0) in enumerate(zip(lens, (-6.8, -4.4, -2.0))):
            x0 = (8.1 + (0.3 if k == 1 else 0)) if sx > 0 else -(8.1 + (0.3 if k == 1 else 0)) - 2
            box(hb, (x0, -65.2 + k * 0.4, z0), (2, ln, 2))
    # crown of dead orange blossoms where the veil is pinned
    for bx, by, bz, bs in ((-7.2, -68.0, 1.5, 2), (-4.2, -68.6, 4.0, 3), (1.6, -68.7, 4.6, 2), (5.0, -68.2, 1.0, 3)):
        box('head', (bx, by, bz), (bs, 2, bs - 1), mat=blossom_mat)

    # ---------------- jaw (dislocated, hanging open in an eternal wail)
    bone('jaw', (0, -51, 0.5), parent='head', rot=(30, 0, 5), mat=tongue_mat)
    box('jaw', (-5, -51, -7.5), (10, 6, 8), decals={'front': pixelart(JAW_FRONT[:6], FPAL, anchor='topleft')})
    box('jaw', (-3.5, -45, -7.2), (7, 4, 6), decals={'front': pixelart(CHIN, FPAL, anchor='topleft')})
    for tx, th, rot in ((-3, 1, 'rot'), (2, 2, '')):
        box('jaw', (tx, -51 - th, -7.0), (1, th, 1), mat=tooth_mat, name=rot)

    # ---------------- hair strands over the face (separate, rotated, with gaps)
    strands = [(-8.6, 3, 34, (-6, 0, -8)), (-3.6, 1, 15, (-9, 0, -6)), (3.6, 2, 22, (-8, 0, -12)),
               (6.0, 3, 36, (-5, 0, -12)), (0.4, 1, 10, (-12, 0, -6))]
    for i, (sx, sw, ln, rot) in enumerate(strands):
        name = f'hair_front_{i + 1}'
        bone(name, (sx + sw / 2, -67, -8.6), parent='head', rot=rot, mat=hair_mat)
        box(name, (sx, -67.3, -9.6), (sw, ln, 1))

    # ---------------- long hair down the back
    bone('hair_back', (0, -63, 7.5), parent='head', rot=(34, 0, -9), mat=hair_mat)
    box('hair_back', (-8, -64, 7.8), (16, 22, 0), name='root')
    for sx, dz in ((-8.5, 8.2), (-5, 8.8), (-1.5, 9.2), (2, 8.8), (5.5, 8.2)):
        box('hair_back', (sx, -64, dz), (3, 22, 2), name='root')
    bone('hair_back_lower', (0, -43, 8.8), parent='hair_back', rot=(-30, 0, 3), mat=hair_mat)
    box('hair_back_lower', (-8, -43, 7.8), (16, 40, 0))
    for sx, ln, dz in ((-9, 44, 8.2), (-6, 36, 9.0), (-3, 48, 9.6), (0, 40, 9.2), (3, 47, 9.6), (6, 39, 8.6)):
        box('hair_back_lower', (sx, -43.5, dz), (3, ln, 2))

    # ---------------- torn tulle veil
    # veil pinned at the crown, lying over the hair and following it down the back
    bone('veil', (0, -65, 11.6), parent='hair_back', rot=(-3, 0, 0), mat=veil_mat)
    box('veil', (-10, -65.5, 11.6), (20, 22, 0), name='veil_hi')
    bone('veil_lower', (0, -43.5, 11.8), parent='hair_back_lower', rot=(4, 0, 0), mat=veil_mat)
    box('veil_lower', (-12, -43.5, 11.8), (24, 40, 0), name='veil_lo')

    # ---------------- arms: much too long, bony, wrists bent, spider fingers
    for side, sx in (('right', -1), ('left', 1)):
        ax = 9.5 * sx
        bone(f'{side}_arm', (ax, -36, 0), parent='chest', rot=(-8, 0, -10 * sx), mat=skin_mat)
        box(f'{side}_arm', (ax - 3, -39, -3), (6, 5, 6), mat=dress_mat, name='puff')
        box(f'{side}_arm', (ax - 2, -36, -2), (4, 16, 4))
        box(f'{side}_arm', (ax - 2, -36, -2), (4, 9, 4), mat=dress_mat, inflate=0.5, name='sleeve')
        box(f'{side}_arm', (ax - 2.5, -22, -1.5), (5, 3, 5), name='knob')
        bone(f'{side}_forearm', (ax, -20, 0.5), parent=f'{side}_arm', rot=(-22, 0, 5 * sx), mat=skin_mat)
        box(f'{side}_forearm', (ax - 1.5, -20, -1), (3, 17, 3))
        box(f'{side}_forearm', (ax - 2, -5, -1.5), (4, 2, 4), name='knob')
        hrot = (-34, 30, 8) if sx < 0 else (-16, -48, -6)
        bone(f'{side}_hand', (ax, -3, 0.5), parent=f'{side}_forearm', rot=hrot, mat=skin_mat)
        box(f'{side}_hand', (ax - 2.5, -3, -0.5), (5, 7, 2))
        box(f'{side}_hand', (ax - 2.5, 3, -1.0), (5, 1, 3), name='knuckle')
        fx = [-2.3, -0.9, 0.5, 1.8]
        flen = [(7, 6), (9, 7), (8, 7), (6, 5)]
        for f in range(4):
            fb = f'{side}_finger_{f + 1}'
            px = ax + fx[f] * (-sx) - 0.5
            bone(fb, (px + 0.5, 4, 0.5), parent=f'{side}_hand', rot=(-14 - f * 4, 0, (f - 1.5) * 5 * sx), mat=skin_mat)
            box(fb, (px, 4, 0), (1, flen[f][0], 1), inflate=0.3)
            curl = (-44 + f * 4) if sx < 0 else (-30 - f * 5)
            bone(fb + '_tip', (px + 0.5, 4 + flen[f][0], 0.5), parent=fb, rot=(curl, 0, 0), mat=nail_tip)
            box(fb + '_tip', (px, 4 + flen[f][0], 0), (1, flen[f][1], 1), inflate=0.12)
        tb = f'{side}_thumb'
        tx = ax + 2.6 * sx
        bone(tb, (tx, 1, 0.0), parent=f'{side}_hand', rot=(-45, 0, 22 * sx), mat=nail_tip)
        box(tb, (tx - 0.5, 1, -0.5), (1, 6, 1), inflate=0.25)

    m = Model('llorona', 256, 256, r.roots)
    m.scale = 0.5
    m.render_type = 'entityTranslucent'
    return m


POSES = {
    # lunge: arms reaching forward wide, fingers splayed and hooked, jaw dropped, head thrust at the victim
    'attack': {
        'chest': (0.18, 0, 0, 0, 0, 0),
        'neck': (0.12, 0, 0, 0, 0, 0),
        'head': (-0.28, 0, -0.12, 0, 0, -2.0),
        'jaw': (0.95, 0, 0, 0, 0, 0),
        'hair_front_1': (0.25, 0, 0, 0, 0, 0), 'hair_front_2': (0.25, 0, 0, 0, 0, 0),
        'hair_front_3': (0.25, 0, 0, 0, 0, 0), 'hair_front_4': (0.25, 0, 0, 0, 0, 0),
        'hair_side_right': (0.25, 0, 0, 0, 0, 0), 'hair_side_left': (0.25, 0, 0, 0, 0, 0),
        'right_arm': (-1.3, 0.5, 0.4, 0, 0, 0),
        'left_arm': (-1.4, -0.4, -0.4, 0, 0, 0),
        'right_forearm': (-0.15, 0, -0.1, 0, 0, 0),
        'left_forearm': (-0.15, 0, 0.1, 0, 0, 0),
        'right_hand': (0.75, -0.55, 0, 0, 0, 0),
        'left_hand': (0.75, 0.55, 0, 0, 0, 0),
        'right_finger_1': (0, 0, 0.35, 0, 0, 0), 'right_finger_2': (0, 0, 0.12, 0, 0, 0),
        'right_finger_3': (0, 0, -0.12, 0, 0, 0), 'right_finger_4': (0, 0, -0.35, 0, 0, 0),
        'left_finger_1': (0, 0, -0.35, 0, 0, 0), 'left_finger_2': (0, 0, -0.12, 0, 0, 0),
        'left_finger_3': (0, 0, 0.12, 0, 0, 0), 'left_finger_4': (0, 0, 0.35, 0, 0, 0),
        'right_thumb': (0, 0, 0.4, 0, 0, 0), 'left_thumb': (0, 0, -0.4, 0, 0, 0),
    },
    # banshee wail: spine arched back, head thrown back, jaw unhinged, arms flung down and back
    'scream': {
        'chest': (-0.22, 0, 0, 0, 0, 0),
        'neck': (-0.4, 0, 0, 0, 0, 0),
        'head': (-0.55, 0, -0.15, 0, 0, 0),
        'jaw': (1.05, 0, 0, 0, 0, 0),
        'hair_front_1': (1.0, 0, 0.1, 0, 0, 0), 'hair_front_2': (1.0, 0, 0, 0, 0, 0),
        'hair_front_3': (1.0, 0, 0, 0, 0, 0), 'hair_front_4': (1.0, 0, 0.1, 0, 0, 0),
        'hair_front_5': (1.0, 0, 0, 0, 0, 0),
        'hair_side_right': (1.05, 0, 0.1, 0, 0, 0), 'hair_side_left': (1.05, 0, 0.1, 0, 0, 0),
        'hair_back': (0.75, 0, 0, 0, 0, 0),
        'hair_back_lower': (0.35, 0, 0, 0, 0, 0),
        'right_arm': (0.4, 0, 0.3, 0, 0, 0),
        'left_arm': (0.4, 0, -0.3, 0, 0, 0),
        'right_forearm': (0.25, 0, 0, 0, 0, 0),
        'left_forearm': (0.25, 0, 0, 0, 0, 0),
        'right_hand': (0.4, 0, 0, 0, 0, 0),
        'left_hand': (0.4, 0, 0, 0, 0, 0),
    },
}

ANIM_NOTES = "todo"
