"""Sor Agonia -- the demonic nun of the Convento de Santa Ines (DEAD LINE).

Authored at 2x texel density (model.scale = 0.5).  +Y down, ground y = 24, faces -Z.

Design
------
Silhouette: a wrong hourglass.  Huge hooded head (black veil > white coif frame > recessed corpse face),
hunched back with vertebrae pushing through the wool, broad veiled shoulders, an 8-texel wasp waist cinched
by a leather cincture, then a heavy bell robe of eight flared, torn panels that floats just above the ground.
Head tilted on a dislocated neck.  Long bell sleeves that trail ragged cloth; grey spider hands with black
claws hanging to the knees.  Inverted wooden cross on the chest, bone rosary hanging from the belt, three
iron nails driven through the forehead band.
Face (14 x 22 visible texels inside the coif): furrowed brow ridge + glabella knot overhanging two deep black
sockets with ember eyes at different heights, two nasal slits, a protruding black-lipped maxilla with a grin
running the full width of the face, jagged 3D tooth planes above and below, a separate dropping jaw, black
ichor tears, blood from the nails.
"""
import math

from mcmodel import Model, vnoise, hash3, face_light, pick
from rig import Rig
from paint import hx, mix, scale, pixelart

# ------------------------------------------------------------------ palettes (hand-picked, hue shifted)
WOOL = [hx('#040307'), hx('#09080e'), hx('#100f17'), hx('#181722'), hx('#22202f'), hx('#2e2b3e'),
        hx('#3e3a52'), hx('#575170')]
VEILC = [hx('#030305'), hx('#07070b'), hx('#0d0d14'), hx('#15151f'), hx('#1f1f2d'), hx('#2b2b3d'),
         hx('#3b3c54'), hx('#53557a')]
LINEN = [hx('#34323a'), hx('#56535a'), hx('#7c7880'), hx('#a29e9f'), hx('#c4bfb8'), hx('#ddd7cb'),
         hx('#efe9dc'), hx('#fbf7ee')]
GRIME = hx('#8a7a55')
SKIN = [hx('#121218'), hx('#25262d'), hx('#3d3f46'), hx('#5b5e62'), hx('#7f8381'), hx('#a6a9a2'),
        hx('#c9cbc1'), hx('#e6e6da')]
HANDC = [hx('#111115'), hx('#212127'), hx('#36363e'), hx('#4f4f58'), hx('#6c6b74'), hx('#8c8a92'),
         hx('#aeabb0'), hx('#cfccce')]
VEIN = hx('#1a0e1c')
CRACK = hx('#2f2f36')
CLAW = [hx('#000000'), hx('#050507'), hx('#0d0d12'), hx('#1b1b24'), hx('#33334a'), hx('#5a5a78')]
EMBER = [hx('#2a0300'), hx('#6e1200'), hx('#c23a00'), hx('#ff7a0a'), hx('#ffc23a'), hx('#fff3b8')]
MOUTH = [hx('#020102'), hx('#0c0305'), hx('#1e070c'), hx('#3a0f16'), hx('#5c1d28'), hx('#86343f')]
LIP = [hx('#050306'), hx('#120a0f'), hx('#21161d'), hx('#33252e')]
TEETH = [hx('#2a241b'), hx('#4c4333'), hx('#76694f'), hx('#a09276'), hx('#c8bc9c'), hx('#e6dec5')]
WOOD = [hx('#170d07'), hx('#2a190d'), hx('#432914'), hx('#5f3d1f'), hx('#7c542c'), hx('#9a6e3c'),
        hx('#b98c52')]
IRON = [hx('#0f0f12'), hx('#212126'), hx('#38383f'), hx('#55555e'), hx('#7a7a84'), hx('#a2a2ac')]
LEATHER = [hx('#0a0605'), hx('#170e0b'), hx('#251812'), hx('#36241a'), hx('#4a3224')]
BONE = [hx('#2e271d'), hx('#4d4333'), hx('#71654f'), hx('#988a6e'), hx('#bcae90'), hx('#d9cfb4'), hx('#efe8d6')]
BLOOD = [hx('#160003'), hx('#330207'), hx('#55050c'), hx('#7a0a13'), hx('#9e141c')]
DUST = hx('#4a4552')


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
    o, sz = ctx.cube.origin, ctx.cube.size
    return int(abs(o[0]) * 13.1 + abs(o[1]) * 7.3 + abs(o[2]) * 3.7 + sz[0] * 31 + sz[1] * 17 + sz[2] * 5) % 9973


def across(ctx):
    """Coordinate running across the face horizontally (for vertical folds)."""
    lx, ly, lz = local(ctx)
    if ctx.face in ('west', 'east'):
        return lz + (60 if ctx.face == 'east' else 30)
    return lx


# ------------------------------------------------------------------ materials
def fold_shade(u, y, seed, period=6.0):
    """Quantised vertical folds: thin lit ridge, soft body, hard dark crease."""
    ph = (u + vnoise(u * 0.21, y * 0.06, seed, 3) * 3.0 + seed * 0.37) % period / period
    if ph < 0.12:
        return 0.15      # lit ridge
    if ph < 0.32:
        return 0.06
    if ph < 0.62:
        return 0.0
    if ph < 0.8:
        return -0.07
    return -0.17         # crease


def hem_cut(col, k, h):
    """Ragged torn hem: jagged base + deep V rips."""
    g, ph = col // 4, col % 4
    r = hash3(g, k, 0, 11)
    rip = 0.0
    if r > 0.58:
        rip = (3 + (r - 0.58) * 26) * (1 - abs(ph - 1.5) / 2.2)
    return h - 0.4 - hash3(col, k, 0, 12) * 2.6 - rip


def wool_mat(ctx):
    """Heavy black habit wool: quantised folds, dark seams, frayed singed hem."""
    if is_plane(ctx) and ctx.face == 'back':
        return None
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    t = tag(ctx)
    b = ctx.bone.name
    sd = cseed(ctx)
    k = int(hash3(sd, 1, 0, 2) * 50)
    if t == 'panel':
        if ctx.face == 'bottom':
            return None
        col = int(lx) if ctx.face in ('front', 'back', 'top') else (0 if ctx.face == 'west' else w - 1)
        cut = hem_cut(col, k, h)
        if ly > cut:
            return None
    if t == 'tatter':
        cut = h - 0.5 - hash3(int(lx), k, 0, 13) * min(6, h * 0.6)
        if ly > cut:
            return None
    v = 0.5 + face_light(ctx) * 1.2
    if ctx.face in ('front', 'back', 'west', 'east'):
        v += fold_shade(across(ctx), ly, k, 6.5 if t == 'panel' else 5.0)
    if edge(ctx) == 0 and not is_plane(ctx) and ctx.face != 'top':
        v -= 0.08
    if t == 'panel':
        if ctx.face == 'back':
            v -= 0.25
        if ctx.face in ('west', 'east'):
            v -= 0.12
        v += 0.05 - ly / h * 0.12
    c = pick(WOOL, v)
    if t in ('panel', 'tatter'):
        col = int(lx) if ctx.face in ('front', 'back') else 0
        cut = hem_cut(col, k, h) if t == 'panel' else h
        dist = cut - ly
        if dist < 1.0:
            c = mix(c, DUST, 0.55)            # frayed threads catch the light
        elif dist < 3.5:
            c = mix(c, LEATHER[1], 0.5)       # singed, filthy hem
        if t == 'panel' and ly > h * 0.55 and hash3(int(lx), int(ly), k, 14) > 0.985:
            return None                        # moth holes
    return c


def veil_mat(ctx):
    """Matte black veil: long soft folds, torn trailing edge."""
    if is_plane(ctx) and ctx.face == 'back':
        return None
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    t = tag(ctx)
    sd = cseed(ctx)
    if t == 'veil_lo':
        if ctx.face == 'bottom':
            return None
        col = int(lx) if ctx.face in ('front', 'back', 'top') else (0 if ctx.face == 'west' else w - 1)
        cut = hem_cut(col, 77, h) - abs(lx - w / 2) * 0.35
        if ly > cut:
            return None
    v = 0.5 + face_light(ctx) * 1.1
    if ctx.face in ('front', 'back', 'west', 'east'):
        v += fold_shade(across(ctx), ly, sd % 31, 7.0) * 0.8
    if edge(ctx) == 0 and ctx.face != 'top':
        v -= 0.07
    if t in ('veil_hi', 'veil_lo') and ctx.face == 'front':
        v -= 0.2   # inner side of the veil (faces the back of the nun)
    return pick(VEILC, v)


def linen_mat(ctx):
    """Starched, yellowed coif/wimple linen with blood soaking in from the mouth and the nails."""
    if is_plane(ctx) and ctx.face == 'back':
        return None
    x, y, z = ctx.pos
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    t = tag(ctx)
    v = 0.66 + face_light(ctx) * 1.1
    if edge(ctx) == 0 and ctx.face != 'top':
        v -= 0.12
    u = across(ctx)
    if t in ('wimple', 'neck') and ctx.face != 'top':
        if int(u) % 3 == 0:
            v -= 0.08
    if t == 'bib' and ctx.face == 'front':
        cx = abs(lx - w / 2)
        # rounded bottom of the guimpe
        if ly > h - 3 and cx > w / 2 - (ly - (h - 3)) * 2.2:
            return None
        if ly > h - 1.2 - max(0, cx - 4) * 0.3:
            v -= 0.12
        # pleats radiating from the throat
        if int(lx + (ly * (lx - w / 2) / 12)) % 3 == 0:
            v -= 0.07
    c = pick(LINEN, v)
    if vnoise(x * 0.3, y * 0.3, z * 0.3, 21) > 0.64:
        c = mix(c, GRIME, 0.28)
    # blood drool down the wimple and bib
    if t in ('neck', 'bib') and ctx.face == 'front':
        col = int(lx)
        ln = hash3(col, 3, 0, 31)
        if ln > 0.62:
            top = 0 if t == 'neck' else -1
            if ly < top + 2 + (ln - 0.62) * 22:
                c = mix(c, pick(BLOOD, 2.2 - ly / 9 + ln * 0.5), 0.85)
    return c


def skin_mat(ctx):
    """Corpse-white skin with grey cracks and black veins (skull, jaw, cheek pieces)."""
    x, y, z = ctx.pos
    lx, ly, lz = local(ctx)
    v = 0.66 + face_light(ctx) * 1.2
    if edge(ctx) == 0 and ctx.face != 'top':
        v -= 0.06
    m = vnoise(x * 0.25, y * 0.25, z * 0.25, 41)
    v += (m - 0.5) * 0.18
    if ctx.face == 'bottom':
        v -= 0.1
    c = pick(SKIN, v)
    cr = abs(vnoise(x * 0.35 + 3, y * 0.35, z * 0.35, 43) - 0.5)
    if cr < 0.025:
        c = mix(c, CRACK, 0.75)
    vn = abs(vnoise(x * 0.5, y * 0.16, z * 0.5, 45) - 0.5)
    if vn < 0.018:
        c = mix(c, VEIN, 0.7)
    return c


def palate_mat(ctx):
    """Under-side of the skull / maxilla: wet black-red palate seen through the open mouth."""
    if ctx.face == 'bottom':
        lx, ly, lz = local(ctx)
        w = ctx.cube.size[0]
        return pick(MOUTH, 0.18 + (1 - abs(lx - w / 2) / (w / 2)) * 0.25 - lz * 0.02)
    return skin_mat(ctx)


def throat_mat(ctx):
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    if ctx.face == 'front':
        cx = abs(lx - w / 2) / (w / 2)
        return pick(MOUTH, 0.02 + cx * cx * 0.25)
    return pick(MOUTH, 0.08 + (1 - lz / max(1, d)) * 0.2)


def jaw_mat(ctx):
    """Mandible: skin outside, gums/tongue on top (seen when the jaw drops)."""
    if ctx.face == 'top':
        lx, ly, lz = local(ctx)
        w, h, d = ctx.cube.size
        cx = abs(lx - w / 2)
        if lz < 1.2:
            return pick(MOUTH, 0.75)
        return pick(MOUTH, 0.2 + (1 - cx / (w / 2)) * 0.3 - lz * 0.02)
    if ctx.face == 'back':
        return pick(MOUTH, 0.1)
    return skin_mat(ctx)


UPPER_TEETH = [
    "TTTTTTTTTTTTTT",
    "TtTTtTTTtTTtTT",
    "T.Tt.TT.tT.TT.",
    "..t...T...t...",
]
LOWER_TEETH = [
    "..t...t..t..",
    ".tT.t.Tt.Tt.",
    "tTTtTTTTtTTt",
    "TTTTTTTTTTTT",
]


def teeth_mat(ctx):
    if ctx.face != 'front':
        return None
    rows = UPPER_TEETH if tag(ctx) == 'upper_teeth' else LOWER_TEETH
    ch = rows[ctx.j][ctx.i] if ctx.j < len(rows) and ctx.i < len(rows[ctx.j]) else '.'
    if ch == '.':
        return None
    up = tag(ctx) == 'upper_teeth'
    tip = ctx.j / (ctx.h - 1) if up else 1 - ctx.j / (ctx.h - 1)
    v = 0.75 - tip * 0.25 if ch == 'T' else 0.35
    if hash3(ctx.i, 0, 1 if up else 2, 33) > 0.8:
        v -= 0.35   # rotten brown tooth
    return pick(TEETH, v)


def hand_mat(ctx):
    """Long grey bony hands: knuckle bands, dark creases, tips darkening into the claws."""
    x, y, z = ctx.pos
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    b = ctx.bone.name
    v = 0.58 + face_light(ctx) * 1.2
    if 'finger' in b or 'thumb' in b:
        if ly < 1.0:
            v += 0.12
        elif ly < 2.0 or (h > 6 and abs(ly - h * 0.55) < 0.5):
            v -= 0.14
        v -= (ly / h) * 0.12
    if tag(ctx) == 'knuckles' and ctx.face in ('front', 'top'):
        v += 0.12 if int(lx) % 2 == 0 else -0.06
    if tag(ctx) == 'palm' and ctx.face == 'front':
        # tendons fanning to the knuckles
        if int(lx) % 2 == 1 and ly > 2:
            v += 0.08
    if edge(ctx) == 0 and ctx.face != 'top' and min(w, h) > 2:
        v -= 0.07
    c = pick(HANDC, v)
    vn = abs(vnoise(x * 0.45, y * 0.12, z * 0.45, 47) - 0.5)
    if vn < 0.03:
        c = mix(c, VEIN, 0.6)
    return c


def claw_mat(ctx):
    lx, ly, lz = local(ctx)
    h = ctx.cube.size[1]
    v = 0.45 + face_light(ctx) * 1.3 - (ly / h) * 0.3
    if ctx.face in ('front', 'west') and ly < h * 0.6:
        v += 0.25   # glossy highlight
    return pick(CLAW, v)


def wood_mat(ctx):
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    long_ = ly if h >= w else lx
    acr = lx if h >= w else ly
    v = 0.5 + face_light(ctx) * 1.3
    v += (vnoise(acr * 0.9, long_ * 0.12, cseed(ctx), 51) - 0.5) * 0.5
    if edge(ctx) == 0:
        v -= 0.15
    c = pick(WOOD, v)
    if hash3(int(lx), int(ly), cseed(ctx) + ord(ctx.face[0]), 52) > 0.86:
        c = mix(c, BLOOD[2], 0.7)
    return c


def iron_mat(ctx):
    v = 0.45 + face_light(ctx) * 1.4 + (hash3(ctx.i, ctx.j, cseed(ctx), 53) - 0.5) * 0.2
    if edge(ctx) == 0:
        v -= 0.1
    c = pick(IRON, v)
    if hash3(ctx.i, ctx.j, cseed(ctx), 54) > 0.7:
        c = mix(c, hx('#5a2a12'), 0.5)   # rust
    return c


def leather_mat(ctx):
    v = 0.5 + face_light(ctx) * 1.2
    if ctx.j in (0, ctx.h - 1) and ctx.face not in ('top', 'bottom'):
        v -= 0.2
    if ctx.face == 'front' and ctx.i % 4 == 1 and ctx.j == ctx.h // 2:
        v += 0.25   # stitching
    return pick(LEATHER, v)


def bead_mat(ctx):
    v = 0.55 + face_light(ctx) * 1.4
    if edge(ctx) == 0:
        v -= 0.18
    return pick(BONE, v)


def string_mat(ctx):
    if ctx.face != 'front':
        return None
    return pick(LEATHER, 0.6)


def cavity_mat(ctx):
    """Inside of a sleeve: pure shadow."""
    return pick(WOOL, 0.05)


def sleeve_mat(ctx):
    if ctx.face == 'bottom':
        lx, ly, lz = local(ctx)
        w, h, d = ctx.cube.size
        rim = min(lx, w - lx, lz, d - lz)
        return pick(WOOL, 0.35) if rim < 1 else pick(WOOL, 0.0)
    return wool_mat(ctx)


def drape_mat(ctx):
    """Trailing bell-sleeve drape: pointed, shredded."""
    if ctx.face != 'front':
        return None
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    cx = abs(lx - w / 2)
    if ly > h - 1 - cx * 1.6 - hash3(int(lx), 5, 0, 61) * 4:
        return None
    if ly > h * 0.4 and hash3(int(lx) // 2, int(ly) // 3, 0, 62) > 0.9:
        return None
    v = 0.42 + fold_shade(lx, ly, 9, 4.0) - ly / h * 0.1
    c = pick(WOOL, v)
    return c


# ------------------------------------------------------------------ face pixel art
FPAL = {
    '1': SKIN[0], '2': SKIN[1], '3': SKIN[2], '4': SKIN[3], '5': SKIN[4], '6': SKIN[5], '7': SKIN[6], '8': SKIN[7],
    'K': (1, 1, 2, 255), 'k': (12, 10, 16, 255), 'q': (40, 30, 44, 255),
    'e': EMBER[1], 'o': EMBER[3], 'y': EMBER[4], 'W': EMBER[5],
    'n': (2, 1, 3, 255), 'N': SKIN[1],
    'x': (6, 4, 9, 255), 'X': (34, 34, 52, 255),
    'c': CRACK, 'v': VEIN,
    'L': LIP[0], 'l': LIP[2], 'M': MOUTH[0], 'g': MOUTH[3],
    'B': BLOOD[2], 'b': BLOOD[4],
}
GLOW = {'e': (150, 30, 0, 255), 'o': EMBER[3], 'y': EMBER[4], 'W': EMBER[5]}

#        0123456789012345   (col 0 = x -8 = viewer's left, hidden under the wimple)
SKULL = [
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    ".qkKKk....23332.",
    ".kKKKK....kKKkq.",
    ".KoyoK3553KKKKk.",
    ".KeoeKn44nKoyoK.",
    ".qKKKqn45nKeoeK.",
    ".34x43N33NqKxKk.",
    "................",
    "................",
    "................",
    "................",
]
BROW = [
    "45566676666554",
    "345c5565565c43",
    "22333222233322",
]
GLABELLA = [
    "4664",
    "c55c",
    "2442",
]
MAXILLA = [
    "L4x44555544x4L",
    "lLx34433443xLl",
    "LLLlLLLLLLlLLL",
    "gMgMgggMggMgMg",
]
JAW = [
    "LLlLLLLLLLLlLL",
    "B3x3445544x33B",
    "B3x4c55554x43b",
    "b2x3455543x32b",
    "12x2334332x221",
]
CHIN = [
    "34555543",
    "23c44c32",
    "12233221",
]
BAND = [
    "....................",
    ".....b....b...b.....",
    ".....B....b...B.....",
    ".....B.........B....",
]


def art(rows, glow=False):
    return pixelart(rows, GLOW if glow else FPAL, anchor='topleft')


DEFAULT_MAT = wool_mat
FOCUS = 'head'


def build():
    r = Rig()

    def box(bone, frm, size, mat=None, inflate=0.0, decals=None, name=None, mirror=False):
        c = r.box(bone, frm, size, mat=mat, inflate=inflate, decals=decals, mirror=mirror)
        c.name = name
        return c

    bone = r.bone

    # ---------------- body: wasp waist, cincture, hip yoke (root, floats)
    bone('body', (0, -12, 0), mat=wool_mat)
    box('body', (-4, -18, -3.5), (8, 10, 7))
    box('body', (-4.5, -14, -4), (9, 2, 8), mat=leather_mat, inflate=0.25)
    box('body', (-1.5, -14.5, -4.8), (3, 3, 1), mat=iron_mat)
    box('body', (-7, -10, -6), (14, 6, 12))

    # ---------------- robe: eight flared torn panels around the hips
    flare = [-19, -22, -18, -23, -20, -21, -18, -22]
    lens = [33, 34, 32, 35, 33, 34, 32, 35]
    names = ['robe_front', 'robe_front_right', 'robe_right', 'robe_back_right',
             'robe_back', 'robe_back_left', 'robe_left', 'robe_front_left']
    for k, nm in enumerate(names):
        rr = 5.5 if k % 2 == 0 else 7.0
        yaw = k * 45 + (4 if k % 3 == 1 else -3 if k % 3 == 2 else 0)
        bone(nm, (0, -9, 0), parent='body', rot=(flare[k], yaw, 0), mat=wool_mat)
        box(nm, (-7.5, -9, -rr - 2), (15, lens[k], 2), name='panel')
        for s in range(2):
            sx = -6 + s * 7 + (k % 3)
            ln = 7 + int(hash3(k, s, 0, 7) * 6)
            box(nm, (sx, -9 + lens[k] - 6, -rr - 1), (2 + (s + k) % 2, ln, 0), name='tatter')

    # ---------------- rosary of bone beads hanging from the cincture
    bone('rosary', (-4.5, -12.5, -4.8), parent='body', rot=(-30, 0, 6), mat=bead_mat)
    box('rosary', (-5, -12.5, -5), (1, 20, 0), mat=string_mat)
    for i, yy in enumerate((-11, -8, -5, -2, 1, 4)):
        box('rosary', (-5.5, yy, -5.8), (2, 2, 2))
    box('rosary', (-5, 7, -5.3), (1, 7, 1), mat=wood_mat, inflate=0.3)
    box('rosary', (-6.5, 11, -5.3), (4, 1, 1), mat=wood_mat, inflate=0.3)

    # ---------------- chest: hunched, one shoulder dropped, hump with vertebrae through the wool
    bone('chest', (0, -16, 0), parent='body', rot=(12, 0, -4), mat=wool_mat)
    box('chest', (-5, -22, -4.5), (10, 6, 9))
    box('chest', (-8, -32, -5.5), (16, 10, 11))
    box('chest', (-12, -37, -6), (24, 6, 12))
    box('chest', (-6, -36, 4), (12, 10, 5))
    for yy in (-36, -33, -30):
        box('chest', (-1, yy, 8.2), (2, 2, 2), mat=bead_mat, name='vertebra')
    box('chest', (-8, -37, -7.2), (16, 9, 2), mat=linen_mat, name='bib')

    # ---------------- inverted wooden cross on a chain
    bone('cross', (0, -29, -8), parent='chest', rot=(-12, 0, 4), mat=wood_mat)
    box('cross', (-0.5, -30, -8.0), (1, 3, 0), mat=iron_mat)
    box('cross', (-1, -28, -9), (2, 16, 2))
    box('cross', (-4, -18, -9), (8, 2, 2))

    # ---------------- neck: white wimple wrapped around a twisted neck
    bone('neck', (0, -36, 0), parent='chest', rot=(-14, 0, 0), mat=linen_mat)
    box('neck', (-9, -42, -6.5), (18, 8, 13), name='neck')

    # ---------------- head: coif frame, veil hood, recessed corpse face
    bone('head', (0, -41, 1), parent='neck', rot=(4, 0, 13), mat=skin_mat)
    box('head', (-8, -58, -7), (16, 16, 14), mat=palate_mat,
        decals={'front': art(SKULL), 'eyes:front': art(SKULL, True)})
    box('head', (-7, -55, -8.5), (14, 3, 2), decals={'front': art(BROW)})
    box('head', (-2, -53, -8.8), (4, 3, 2), decals={'front': art(GLABELLA)})
    box('head', (-7, -46, -8), (14, 4, 3), mat=palate_mat, decals={'front': art(MAXILLA)})
    box('head', (-7, -43, -7.6), (14, 4, 0), mat=teeth_mat, name='upper_teeth')
    box('head', (-6, -44, -6), (12, 6, 8), mat=throat_mat)
    # coif: forehead band + wimple sides framing the face
    box('head', (-10, -59, -9), (20, 4, 17), mat=linen_mat, name='band', decals={'front': art(BAND)})
    box('head', (-10, -55, -8.5), (3, 18, 14), mat=linen_mat, name='wimple')
    box('head', (7, -55, -8.5), (3, 18, 14), mat=linen_mat, name='wimple')
    # veil hood
    box('head', (-12, -62, -8), (24, 4, 20), mat=veil_mat)
    box('head', (-10, -63, -6), (20, 1, 16), mat=veil_mat)
    box('head', (-12, -58, -6), (2, 21, 18), mat=veil_mat)
    box('head', (10, -58, -6), (2, 21, 18), mat=veil_mat)
    box('head', (-10, -58, 7), (20, 18, 5), mat=veil_mat)
    # iron nails driven through the forehead band
    for nx in (-5, 0, 4):
        box('head', (nx, -58, -11.5), (1, 1, 3), mat=iron_mat, inflate=0.2)

    # ---------------- jaw (drops)
    bone('jaw', (0, -43, 1), parent='head', rot=(14, 0, 0), mat=jaw_mat)
    box('jaw', (-7, -42, -7.5), (14, 5, 10), decals={'front': art(JAW)})
    box('jaw', (-4, -37, -7), (8, 3, 7), decals={'front': art(CHIN)})
    box('jaw', (-6, -45, -7.0), (12, 4, 0), mat=teeth_mat, name='lower_teeth')

    # ---------------- veil falling down the back
    bone('veil', (0, -60, 11.5), parent='head', rot=(14, 0, -13), mat=veil_mat)
    box('veil', (-12, -60, 11.2), (24, 32, 1), name='veil_hi')
    bone('veil_lower', (0, -29, 12), parent='veil', rot=(-8, 0, 0), mat=veil_mat)
    box('veil_lower', (-13, -29, 11.4), (26, 24, 1), name='veil_lo')

    # ---------------- arms: bell sleeves, trailing drapes, spider hands
    for side, sx in (('right', -1), ('left', 1)):
        ax = 12 * sx
        bone(f'{side}_arm', (ax, -35, 0), parent='chest', rot=(-8, 0, -9 * sx), mat=wool_mat)
        box(f'{side}_arm', (ax - 4, -38, -4.5), (8, 6, 9))
        box(f'{side}_arm', (ax - 3.5, -35, -3.5), (7, 16, 7))
        bone(f'{side}_forearm', (ax, -20, 0), parent=f'{side}_arm', rot=(-28, 0, 4 * sx), mat=sleeve_mat)
        box(f'{side}_forearm', (ax - 4, -21, -4), (8, 7, 8))
        box(f'{side}_forearm', (ax - 5.5, -14, -5.5), (11, 9, 11))
        bone(f'{side}_sleeve', (ax, -14, 5.5), parent=f'{side}_forearm', rot=(30, 0, 0), mat=drape_mat)
        box(f'{side}_sleeve', (ax - 5.5, -14, 5.5), (11, 26, 0))
        hrot = (10, 18, 4) if sx < 0 else (2, -24, -6)
        bone(f'{side}_hand', (ax, -7, 0), parent=f'{side}_forearm', rot=hrot, mat=hand_mat)
        box(f'{side}_hand', (ax - 3, -8, -1.5), (6, 8, 3), name='palm')
        box(f'{side}_hand', (ax - 3.5, -1, -2), (7, 2, 3), name='knuckles')
        flen = [(8, 6), (10, 7), (9, 7), (7, 5)]
        for f in range(4):
            fb = f'{side}_finger_{f + 1}'
            cx = ax + (-2.25 + f * 1.5) * (-sx)
            bone(fb, (cx, 0, 0), parent=f'{side}_hand', rot=(8 + f * 2, 0, (f - 1.5) * 6 * sx), mat=hand_mat)
            box(fb, (cx - 0.5, 0, -0.5), (1, flen[f][0], 1), inflate=0.4)
            tb = fb + '_tip'
            bone(tb, (cx, flen[f][0], 0), parent=fb, rot=(18 + f * 4, 0, 0), mat=hand_mat)
            box(tb, (cx - 0.5, flen[f][0], -0.5), (1, flen[f][1], 1), inflate=0.33)
            box(tb, (cx - 0.5, flen[f][0] + flen[f][1] - 0.4, -0.8), (1, 5, 1), mat=claw_mat, inflate=0.2)
        th = f'{side}_thumb'
        tx = ax + 3.2 * sx
        bone(th, (tx, -4, -0.5), parent=f'{side}_hand', rot=(-20, 0, 30 * sx), mat=hand_mat)
        box(th, (tx - 0.5, -4, -1), (1, 7, 1), inflate=0.4)
        box(th, (tx - 0.5, 2.6, -1.3), (1, 4, 1), mat=claw_mat, inflate=0.2)

    m = Model('monja', 256, 256, r.roots)
    m.scale = 0.5
    return m


POSES = {
    'attack': {
        'chest': (0.15, 0, 0, 0, 0, 0),
        'head': (-0.3, 0, 0.2, 0, 0, 0),
        'jaw': (0.85, 0, 0, 0, 0, 0),
        'right_arm': (-2.3, 0, 0.5, 0, 0, 0),
        'left_arm': (-2.3, 0, -0.5, 0, 0, 0),
        'right_forearm': (0.3, 0, 0, 0, 0, 0),
        'left_forearm': (0.3, 0, 0, 0, 0, 0),
    },
    'burn': {
        'chest': (0.35, 0, 0, 0, 0, 0),
        'head': (0.35, 0, 0, 0, 0, 0),
        'right_arm': (-1.9, 0.6, 0, 0, 0, 0),
        'left_arm': (-1.9, -0.6, 0, 0, 0, 0),
        'right_forearm': (-1.2, 0, 0, 0, 0, 0),
        'left_forearm': (-1.2, 0, 0, 0, 0, 0),
    },
}

ANIM_NOTES = "todo"
