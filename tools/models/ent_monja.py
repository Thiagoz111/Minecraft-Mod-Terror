"""Sor Agonia -- the demonic nun of the Convento de Santa Ines (DEAD LINE).

Authored at 2x texel density (model.scale = 0.5).  +Y down, ground y = 24, faces -Z.

Design
------
Silhouette: a wrong hourglass that floats.  A tapered, slightly peaked hood (narrower than the shoulders,
with a neck notch under it), a hunched hump the black veil lies on (three vertebrae tear through it), sloped
shoulders framed by the veil's side panels, a 13-texel wasp waist cinched by a leather cincture, then a heavy
bell robe of eight flared, torn panels whose shredded hem stops ~2 texels above the ground (no feet: she
glides).  Long bell sleeves that flare from a thin upper arm into a dark open cuff with ragged drapes;
grey spider hands with two-segment hooked black claws hanging to the knees.  Inverted wooden cross on a
chain, bone rosary on the cincture, three iron nails driven through the coif band.

Face (one coherent pixel-art mask projected onto layered cubes, see FACE): the corpse-white face is the
brightest value of the whole model and is shaped like a skull/diamond inside the yellowed coif -- linen
wedges narrow the forehead, cheekbones push out past the wimple, a long pointed chin hangs below it.
Furrowed brow ridge overhanging two deep 6x6 sockets with burning ember irises at different heights,
no nose (two black slits), a protruding muzzle with black lips torn into a grin that runs past the face
onto the cheeks, double rows of needle teeth with corner fangs, a separate dropping jaw, ember glow in the
throat, hand-placed cracks / veins / blood from the nails.
"""
import math

from mcmodel import Model, vnoise, hash3, face_light, pick
from rig import Rig
from paint import hx, mix, pixelart

# ------------------------------------------------------------------ palettes (hand-picked, hue shifted)
WOOL = [hx('#040307'), hx('#09080e'), hx('#100f17'), hx('#181722'), hx('#22202f'), hx('#2e2b3e'),
        hx('#3e3a52'), hx('#575170')]
VEILC = [hx('#030305'), hx('#07070b'), hx('#0d0d14'), hx('#15151f'), hx('#1f1f2d'), hx('#2b2b3d'),
         hx('#3b3c54'), hx('#53557a')]
# yellowed, grimy linen: one full step darker than the face so the face pops inside the coif
LINEN = [hx('#24211d'), hx('#3d3830'), hx('#5a5347'), hx('#7a705f'), hx('#988c76'), hx('#b3a78d'),
         hx('#c8bda2'), hx('#d8ceb4')]
# corpse skin: cold, green-grey shadows, almost paper-white lights
SKIN = [hx('#16161c'), hx('#2b2c33'), hx('#45474d'), hx('#666a6b'), hx('#8d918c'), hx('#b3b6ad'),
        hx('#d3d5ca'), hx('#ecece0')]
HANDC = [hx('#111115'), hx('#212127'), hx('#36363e'), hx('#4f4f58'), hx('#6c6b74'), hx('#8c8a92'),
         hx('#aeabb0'), hx('#cfccce')]
VEIN = hx('#1a0e1c')
VEIN2 = hx('#4a3a52')
CRACK = hx('#3a3a42')
CLAW = [hx('#000000'), hx('#050507'), hx('#0d0d12'), hx('#1b1b24'), hx('#33334a'), hx('#5a5a78'),
        hx('#8a8aa8')]
EMBER = [hx('#2a0300'), hx('#6e1200'), hx('#c23a00'), hx('#ff7a0a'), hx('#ffc23a'), hx('#fff3b8')]
MOUTH = [hx('#020102'), hx('#0c0305'), hx('#1e070c'), hx('#3a0f16'), hx('#5c1d28'), hx('#86343f')]
LIP = [hx('#050306'), hx('#120a0f'), hx('#21161d'), hx('#33252e')]
TEETH = [hx('#2a241b'), hx('#4c4333'), hx('#76694f'), hx('#a09276'), hx('#c8bc9c'), hx('#e6dec5')]
WOOD = [hx('#170d07'), hx('#2a190d'), hx('#432914'), hx('#5f3d1f'), hx('#7c542c'), hx('#9a6e3c'),
        hx('#c4955c'), hx('#e0b47a')]
IRON = [hx('#0f0f12'), hx('#212126'), hx('#38383f'), hx('#55555e'), hx('#7a7a84'), hx('#a2a2ac')]
RUST = hx('#5a2a12')
LEATHER = [hx('#0a0605'), hx('#170e0b'), hx('#251812'), hx('#36241a'), hx('#4a3224'), hx('#5e4130')]
BONE = [hx('#2e271d'), hx('#4d4333'), hx('#71654f'), hx('#988a6e'), hx('#bcae90'), hx('#d9cfb4'), hx('#efe8d6')]
BLOOD = [hx('#160003'), hx('#330207'), hx('#55050c'), hx('#7a0a13'), hx('#9e141c')]
DRIED = hx('#3b120c')
DUST = hx('#4a4552')


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


# ------------------------------------------------------------------ cloth
def fold_shade(u, y, seed, period=10.0):
    """Two or three broad folds per panel: a lit ridge, a soft body and ONE strong crease each."""
    ph = (u + (vnoise(u * 0.13, y * 0.05, seed, 3) - 0.5) * 3.0 + seed * 0.37) % period / period
    if ph < 0.10:
        return 0.11      # lit ridge
    if ph < 0.50:
        return 0.04
    if ph < 0.78:
        return -0.02
    if ph < 0.88:
        return -0.08
    return -0.17         # the crease


def hem_cut(col, k, h):
    """Ragged torn hem: jagged base + a few deep V rips."""
    g, ph = col // 4, col % 4
    r = hash3(g, k, 0, 11)
    rip = 0.0
    if r > 0.6:
        rip = (3 + (r - 0.6) * 24) * (1 - abs(ph - 1.5) / 2.2)
    return h - 0.4 - hash3(col, k, 0, 12) * 2.6 - rip


def wool_mat(ctx):
    """Heavy black habit wool: broad folds, dark seams, frayed singed hem."""
    if is_plane(ctx) and ctx.face == 'back':
        return None
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    t = tag(ctx)
    k = int(hash3(cseed(ctx), 1, 0, 2) * 50)
    if t == 'panel':
        if ctx.face == 'bottom':
            return None
        col = int(lx) if ctx.face in ('front', 'back', 'top') else (0 if ctx.face == 'west' else w - 1)
        if ly > hem_cut(col, k, h):
            return None
    if t == 'tatter':
        if ly > h - 0.5 - hash3(int(lx), k, 0, 13) * min(6, h * 0.6):
            return None
    v = 0.5 + face_light(ctx) * 1.2
    if ctx.face in ('front', 'back', 'west', 'east'):
        v += fold_shade(across(ctx), ly, k, 10.0 if t == 'panel' else 8.0)
    if edge(ctx) == 0 and not is_plane(ctx) and ctx.face != 'top':
        v -= 0.07
    if t == 'panel':
        if ctx.face == 'back':
            v -= 0.25
        if ctx.face in ('west', 'east'):
            v -= 0.12
        v += 0.05 - ly / h * 0.12
    if t == 'cuff' and ctx.face == 'bottom':
        rim = min(lx, w - lx, lz, d - lz)
        return pick(WOOL, 0.32) if rim < 1 else pick(WOOL, 0.0)     # dark open bell cuff
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
    """Matte black veil: long soft folds, torn trailing edges, a slit the vertebrae push through."""
    if is_plane(ctx) and ctx.face == 'back':
        return None
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    t = tag(ctx)
    sd = cseed(ctx)
    if t in ('veil_lo', 'veil_side', 'veil_hi') and ctx.face != 'top':
        if ctx.face == 'bottom':
            return None
        col = int(lx) if ctx.face in ('front', 'back') else (0 if ctx.face == 'west' else w - 1)
        if t == 'veil_lo':
            # long ragged V: centre reaches the bottom, the sides are cut away
            cut = hem_cut(col, 77, h) - abs(lx - w / 2) * 1.25
            if abs(lx - w / 2) < 1.1 and ly < 15:
                return None                    # torn slit: the vertebrae tear through here
        elif t == 'veil_side':
            cut = hem_cut(col, 31 + sd % 7, h) - (lx if sd % 2 else w - lx) * 0.9
        else:
            cut = h + 1
        if ly > cut:
            return None
    v = 0.5 + face_light(ctx) * 1.1
    if ctx.face in ('front', 'back', 'west', 'east'):
        v += fold_shade(across(ctx), ly, sd % 31, 9.0) * 0.8
    if edge(ctx) == 0 and ctx.face != 'top' and not is_plane(ctx):
        v -= 0.07
    if t == 'hood' and ctx.face == 'top':
        v += 0.04
    return pick(VEILC, v)


def linen_mat(ctx):
    """Starched, yellowed coif/wimple linen; the neck wimple and bib are grey and blood-soaked."""
    if is_plane(ctx) and ctx.face == 'back':
        return None
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    t = tag(ctx)
    v = 0.66 + face_light(ctx) * 1.0
    if edge(ctx) == 0 and ctx.face != 'top':
        v -= 0.12
    if ctx.face in ('west', 'east'):
        v -= 0.08
    if t == 'wimple' and ctx.face in ('front', 'west', 'east') and int(across(ctx)) % 3 == 0:
        v -= 0.06                              # starched pleats
    if t in ('collar', 'bib'):
        v -= 0.3                               # grey, soaked, filthy
        if ctx.face == 'front' and t == 'bib':
            cx = abs(lx - w / 2)
            if ly > h - 2 and cx > w / 2 - (ly - (h - 2)) * 2.5:
                return None                    # rounded guimpe bottom
    c = pick(LINEN, v)
    if t in ('collar', 'bib') and ctx.face != 'front':
        c = mix(c, BLOOD[1], 0.35)
    return c


# ------------------------------------------------------------------ flesh
def skin_mat(ctx):
    """Flat corpse-white skin with ONE subtle ramp; details are hand-placed decals (see FACE)."""
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    f = ctx.face
    v = 0.86 + face_light(ctx) * 0.6
    if f == 'top':
        return pick(SKIN, 0.36)                # dark shelves: no white scanlines across the face
    if f == 'bottom':
        return pick(SKIN, 0.3)
    if f in ('west', 'east'):
        v -= 0.16 + (lz / max(1.0, d)) * 0.14  # turns away into shadow
    elif f == 'back':
        v -= 0.35
    else:
        v -= (ly / max(1.0, h)) * 0.06
    if edge(ctx) == 0 and f in ('west', 'east') and min(ctx.w, ctx.h) > 2:
        v -= 0.06
    return pick(SKIN, v)


def palate_mat(ctx):
    """Maxilla: skin outside, wet black-red palate underneath (seen through the open mouth)."""
    if ctx.face == 'bottom':
        lx, ly, lz = local(ctx)
        w = ctx.cube.size[0]
        return pick(MOUTH, 0.18 + (1 - abs(lx - w / 2) / (w / 2)) * 0.3 - lz * 0.02)
    if ctx.face == 'top':
        return pick(MOUTH, 0.35)
    return skin_mat(ctx)


def throat_mat(ctx):
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    if ctx.face == 'front':
        cx = abs(lx - w / 2) / (w / 2)
        return pick(MOUTH, cx * cx * 0.22)
    return pick(MOUTH, 0.08 + (1 - lz / max(1, d)) * 0.2)


def jaw_mat(ctx):
    """Mandible: skin outside, gums/black tongue on top (seen when the jaw drops)."""
    if ctx.face == 'top':
        lx, ly, lz = local(ctx)
        w, h, d = ctx.cube.size
        cx = abs(lx - w / 2)
        if lz < 1.0:
            return pick(MOUTH, 0.5)            # gum rim behind the lower teeth
        return pick(MOUTH, 0.05 + (1 - cx / (w / 2)) * 0.22 - lz * 0.02)   # black tongue / gullet
    if ctx.face == 'back':
        return pick(MOUTH, 0.1)
    return skin_mat(ctx)


UPPER_TEETH = [            # front row: bright needles of alternating length, corner fangs, gum at the fang roots
    "TgT.T.T.TT.T.TgT",
    "T.T.t...T..t.T.T",
    "T.T..........T.T",
    "..T..........T..",
]
UPPER_TEETH_2 = [          # a few rotten teeth of the second row, behind
    "...t......t.....",
    "...t......t.....",
    "................",
    "................",
]
LOWER_TEETH = [
    "...T........T...",
    ".T.T.t.TT.t.T.T.",
    "gTgT.T.TT.T.TgTg",
]
LOWER_TEETH_2 = [
    "................",
    ".....t....t.....",
    ".....t....t.....",
]
TEETH_ROWS = {'upper_teeth': UPPER_TEETH, 'upper_teeth_2': UPPER_TEETH_2,
              'lower_teeth': LOWER_TEETH, 'lower_teeth_2': LOWER_TEETH_2}


def teeth_mat(ctx):
    """1-px needles of alternating length, fangs at the corners, gum pixels at the roots."""
    if ctx.face != 'front':
        return None
    t = tag(ctx)
    rows = TEETH_ROWS[t]
    ch = rows[ctx.j][ctx.i] if ctx.j < len(rows) and ctx.i < len(rows[ctx.j]) else '.'
    if ch == '.':
        return None
    if ch == 'g':
        return pick(MOUTH, 0.7)
    up = t.startswith('upper')
    tip = ctx.j / max(1, ctx.h - 1) if up else 1 - ctx.j / max(1, ctx.h - 1)
    v = 0.95 - tip * 0.3 if ch == 'T' else 0.36 - tip * 0.12
    if hash3(ctx.i, 0, 1 if up else 2, 33) > 0.82:
        v -= 0.3   # rotten brown tooth
    return pick(TEETH, v)


def hand_mat(ctx):
    """Long grey bony hands: ONE crease per joint, a lit knuckle under it, tips darkening into the claws."""
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    b = ctx.bone.name
    t = tag(ctx)
    v = 0.6 + face_light(ctx) * 1.1
    if 'finger' in b or 'thumb' in b:
        if ly < 0.8:
            v -= 0.2          # joint crease
        elif ly < 1.8:
            v += 0.1          # knuckle bump
        v -= (ly / h) * 0.14
    if t == 'palm' and ctx.face == 'front' and ly > 1.5 and int(lx) in (1, 3):
        v += 0.07             # two tendons
    if t == 'knuckles' and ctx.face in ('front', 'top'):
        v += 0.08
    if edge(ctx) == 0 and ctx.face not in ('top',) and min(w, h) > 2:
        v -= 0.07
    return pick(HANDC, v)


def claw_mat(ctx):
    lx, ly, lz = local(ctx)
    h = ctx.cube.size[1]
    v = 0.4 + face_light(ctx) * 1.3 - (ly / h) * 0.25
    if ctx.face in ('front', 'west') and ctx.i == 0:
        v += 0.42   # pale gloss line
    return pick(CLAW, v)


def wood_mat(ctx):
    """Old cross wood: grain along the long axis, a pale worn highlight on the upper-left edges."""
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    long_ = ly if h >= w else lx
    acr = lx if h >= w else ly
    v = 0.5 + face_light(ctx) * 1.3
    v += (vnoise(acr * 1.1, long_ * 0.15, cseed(ctx), 51) - 0.5) * 0.35
    if ctx.face == 'front' and (ctx.i == 0 or ctx.j == 0):
        v += 0.3                               # pale worn edge (reads in the dark)
    elif edge(ctx) == 0:
        v -= 0.15
    return pick(WOOD, v)


def iron_mat(ctx):
    v = 0.45 + face_light(ctx) * 1.4 + (hash3(ctx.i, ctx.j, cseed(ctx), 53) - 0.5) * 0.2
    if edge(ctx) == 0:
        v -= 0.1
    c = pick(IRON, v)
    if hash3(ctx.i, ctx.j, cseed(ctx), 54) > 0.65:
        c = mix(c, RUST, 0.55)
    return c


def leather_mat(ctx):
    v = 0.5 + face_light(ctx) * 1.2
    if ctx.j in (0, ctx.h - 1) and ctx.face not in ('top', 'bottom'):
        v -= 0.2
    if ctx.face == 'front' and ctx.i % 4 == 1 and ctx.j == ctx.h // 2:
        v += 0.25   # stitching
    return pick(LEATHER, v)


def bone_mat(ctx):
    v = 0.6 + face_light(ctx) * 1.4
    if edge(ctx) == 0:
        v -= 0.18
    return pick(BONE, v)


def string_mat(ctx):
    if ctx.face != 'front':
        return None
    return pick(LEATHER, 0.7)


def drape_mat(ctx):
    """Trailing bell-sleeve drapes: pointed, shredded."""
    if ctx.face not in ('front', 'west', 'east'):
        return None
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    u = lx if w > 0 else lz
    span = w if w > 0 else d
    cx = abs(u - span / 2)
    if ly > h - 1 - cx * 1.5 - hash3(int(u), 5, int(span), 61) * 4:
        return None
    if ly > h * 0.45 and hash3(int(u) // 2, int(ly) // 3, int(span), 62) > 0.9:
        return None
    v = 0.4 + fold_shade(u, ly, 9, 6.0) * 0.8 - ly / h * 0.12
    return pick(WOOL, v)


def clear_mat(ctx):
    return None


# ------------------------------------------------------------------ the face mask
# One pixel-art image of the whole face as seen from the front (rest pose, head frame), projected onto
# every layered face cube by its x/y extent.  col c <-> x = GX0 + c, row r <-> y = GY0 + r.
# '.' leaves the cube's own material (linen on band/wimple/wedges).
GX0, GY0 = -10, -60
FACE = [
    # 0123456789012345 6789
    "....................",   # r0  y-60  coif band
    "....................",   # r1  y-59  (nails 1 and 3)
    ".....Bd.......dB....",   # r2  y-58  (nail 2)
    ".....B........B.....",   # r3  y-57
    ".....Bb7878787Bb....",   # r4  y-56  forehead (wedges at 3-4 / 15-16)
    ".....B78c7d778bB....",   # r5  y-55
    ".....b67754457b.....",   # r6  y-54  brow ridge (frown: inner ends dark)
    "....v6764qq4676v....",   # r7  y-53  brow underside
    "...qkKKKqkkqKKkkq...",   # r8  y-52  sockets: right 3-7, bridge 8-11, left 12-16
    "...keoeKq34qkKKKk...",   # r9  y-51
    "...KyWyKq44qKeoeK...",   # r10 y-50
    "...KeoeK3443KyWyK...",   # r11 y-49
    "...kKeKk3443KeoeK...",   # r12 y-48
    ".6787KkQ3443kKe7876.",   # r13 y-47  cheekbones (1-4 / 15-18)
    ".L433456n77n654334L.",   # r14 y-46  muzzle 4-15, nasal slits 8 / 11, torn grin rising onto the cheeks
    ".3L32345n66n54323L3.",   # r15 y-45
    ".23Ll234q55q432lL32.",   # r16 y-44
    "....LLlLLLLLLLlL....",   # r17 y-43  upper lip
    "....................",   # r18 y-42  teeth / throat (own decals)
    "....................",   # r19
    "....................",   # r20
    "....................",   # r21
    "..LLLLlLLLLLLlLLLL..",   # r22 y-38  lower lip (jaw, 16 wide)
    "..2vB3455665543bv2..",   # r23
    "..12vB34c55c43bv21..",   # r24
    "..112vb3344332vv11..",   # r25
    "......B3455432......",   # r26 y-34  chin
    "......d234c321......",   # r27
    "......12233221......",   # r28
    "........2c32........",   # r29 y-31  chin point
    "........1221........",   # r30
    "........1111........",   # r31
]
assert all(len(r) == 20 for r in FACE), [len(r) for r in FACE]

FPAL = {
    '1': SKIN[0], '2': SKIN[1], '3': SKIN[2], '4': SKIN[3], '5': SKIN[4], '6': SKIN[5], '7': SKIN[6], '8': SKIN[7],
    'K': (1, 1, 2, 255), 'k': (12, 10, 16, 255), 'q': (34, 26, 38, 255), 'Q': SKIN[2],
    'e': EMBER[1], 'r': EMBER[2], 'o': EMBER[3], 'y': EMBER[4], 'W': EMBER[5],
    'n': (2, 1, 3, 255),
    'c': CRACK, 'v': VEIN, 'V': VEIN2,
    'L': LIP[0], 'l': LIP[2], 'M': MOUTH[0], 'g': MOUTH[3],
    'B': BLOOD[2], 'b': BLOOD[4], 'd': DRIED, 'z': LINEN[2],
}
GLOWPAL = {'e': (150, 30, 0, 255), 'r': EMBER[2], 'o': EMBER[3], 'y': EMBER[4], 'W': EMBER[5],
           'h': (70, 12, 0, 255)}
EMBERS = set('eroyW')


def _glow_grid(grid):
    """Glow layer: ember pixels plus a dim red halo bleeding onto the black socket around them."""
    H, W = len(grid), len(grid[0])
    out = [['.'] * W for _ in range(H)]
    for r in range(H):
        for c in range(W):
            if grid[r][c] in EMBERS:
                out[r][c] = grid[r][c]
    for r in range(H):
        for c in range(W):
            if grid[r][c] in 'Kkq' and out[r][c] == '.':
                if any(0 <= r + dr < H and 0 <= c + dc < W and grid[r + dr][c + dc] in EMBERS
                       for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1))):
                    out[r][c] = 'h'
    return [''.join(row) for row in out]


FACE_GLOW = _glow_grid(FACE)


def _slice(grid, x0, y0, w, h):
    rows = []
    for j in range(h):
        gy = int(math.floor(y0 + j + 0.5 - GY0))
        row = ''
        for i in range(w):
            gx = int(math.floor(x0 + i + 0.5 - GX0))
            row += grid[gy][gx] if 0 <= gy < len(grid) and 0 <= gx < len(grid[gy]) else '.'
        rows.append(row)
    return rows


def face_decals(x0, y0, w, h):
    d = {'front': pixelart(_slice(FACE, x0, y0, w, h), FPAL, anchor='topleft')}
    g = _slice(FACE_GLOW, x0, y0, w, h)
    if any(ch != '.' for row in g for ch in row):
        d['eyes:front'] = pixelart(g, GLOWPAL, anchor='topleft')
    return d


THROAT_GLOW = [            # ember deep in the gullet: small, so the eyes stay the focal point
    "...............",
    "...............",
    ".......e.......",
    "......eoe......",
    ".......e.......",
    "...............",
]
THROAT_ART = [r.replace('.', 'M') for r in THROAT_GLOW]
THROAT_ART[3] = '.....heoeh.....'.replace('.', 'M')
THROAT_PAL = {'M': None, 'h': MOUTH[3], 'e': EMBER[1], 'o': EMBER[3], 'y': EMBER[4]}

# blood soaking the neck wimple and the bib: drips under the mouth corners, each ending in a droplet,
# dark/oxidised at the top
COLLAR_ART = [
    "dBB..........Bd",
    "dB...........Bd",
    "B.............B",
    "b.............b",
    "B.............b",
    "b..............",
    "B.B..........B.",
    "b.b..........b.",
    "..b..........B.",
    "..............b",
]
BIB_ART = [
    "ddBdBBBBBBdBdd",
    ".dB.bB..Bb..Bd",
    ".dB..b...b..B.",
    "..B..b...B..b.",
    "..b..B...b..b.",
    "..b..b......b.",
]
BAND_PAL = {'B': BLOOD[2], 'b': BLOOD[4], 'd': DRIED}

CROSS_BLOOD = [
    "...",
    ".B.",
    "Bb.",
    "B..",
    "...",
    "..d",
    "..B",
    "...",
]


def art(rows, pal=None):
    return pixelart(rows, pal or FPAL, anchor='topleft')


DEFAULT_MAT = wool_mat
FOCUS = 'head'


DY = 2.0   # global drop so the hood peak lands at y -62 (2.7 blocks) while the hem still floats


def build():
    r = Rig()

    def bone(name, pivot, parent=None, rot=(0, 0, 0), mat=None):
        return r.bone(name, (pivot[0], pivot[1] + DY, pivot[2]), parent=parent, rot=rot, mat=mat)

    def box(bone_, frm, size, mat=None, inflate=0.0, decals=None, name=None, mirror=False):
        c = r.box(bone_, (frm[0], frm[1] + DY, frm[2]), size, mat=mat, inflate=inflate, decals=decals, mirror=mirror)
        c.name = name
        return c

    def fbox(bone_, frm, size, mat=None, name=None, extra=None):
        """Face cube whose front is painted from the FACE mask (sliced by its rest-pose x/y extent)."""
        dec = face_decals(frm[0], frm[1], size[0], size[1])
        if extra:
            dec.update(extra)
        return box(bone_, frm, size, mat=mat, decals=dec, name=name)

    # ---------------- body (root): floats.  13-texel wasp waist, cincture, small hip yoke
    bone('body', (0, -12, 0), mat=wool_mat)
    box('body', (-3, -24, -3), (6, 17, 6), name='waist')
    box('body', (-3.5, -14, -3.5), (7, 2, 7), mat=leather_mat, inflate=0.3)
    box('body', (-1, -14.5, -4.2), (2, 3, 1), mat=iron_mat)
    box('body', (-5.5, -8, -4.5), (11, 5, 9), name='hips')

    # ---------------- robe: eight flared torn panels; hem stops ~2 texels above the ground (she glides)
    flare = [-14, -16, -13, -16, -14, -15, -13, -16]
    lens = [26, 27, 25, 27, 26, 27, 25, 27]
    names = ['robe_front', 'robe_front_right', 'robe_right', 'robe_back_right',
             'robe_back', 'robe_back_left', 'robe_left', 'robe_front_left']
    for k, nm in enumerate(names):
        rr = 4.5 if k % 2 == 0 else 5.5
        yaw = k * 45 + (4 if k % 3 == 1 else -3 if k % 3 == 2 else 0)
        bone(nm, (0, -6, 0), parent='body', rot=(flare[k], yaw, 0), mat=wool_mat)
        box(nm, (-7.5, -6, -rr - 2), (15, lens[k], 2), name='panel')
        for s_ in range(2):
            sx = -6 + s_ * 7 + (k % 3)
            ln = 6 + int(hash3(k, s_, 0, 7) * 4)
            box(nm, (sx, -6 + lens[k] - 7, -rr - 1), (2 + (s_ + k) % 2, ln, 0), name='tatter')

    # ---------------- rosary of bone beads hanging from the cincture
    bone('rosary', (-3.5, -12.5, -3.8), parent='body', rot=(-12, 0, 8), mat=bone_mat)
    box('rosary', (-4, -12.5, -4.2), (1, 18, 0), mat=string_mat)
    for yy in (-10.5, -7.5, -4.5, -1.5, 1.5):
        box('rosary', (-4.5, yy, -5.2), (2, 2, 2))
    box('rosary', (-4, 4.5, -4.7), (1, 6, 1), mat=wood_mat, inflate=0.25)
    box('rosary', (-5.5, 6.5, -4.7), (4, 1, 1), mat=wood_mat, inflate=0.25)

    # ---------------- chest: hunched, right shoulder dropped, hump with vertebrae through the veil
    bone('chest', (0, -21, 0), parent='body', rot=(14, 0, -6), mat=wool_mat)
    box('chest', (-4.5, -27, -3.5), (9, 6, 7))
    box('chest', (-7, -33, -5), (14, 6, 10))
    box('chest', (-8, -36, -4.5), (16, 3, 9))
    box('chest', (-6, -38, 1), (12, 10, 7), name='hump')
    box('chest', (-4, -40, 2), (8, 2, 5), name='hump')
    for yy in (-39, -35.5, -32):
        box('chest', (-1, yy, 7.5), (2, 2, 3), mat=bone_mat, name='vertebra')
    box('chest', (-7, -36, -6.2), (14, 6, 1), mat=linen_mat, name='bib', decals={'front': art(BIB_ART, BAND_PAL)})

    # ---------------- inverted wooden cross on a chain from the neck, resting on the chest above the cincture
    bone('cross', (0, -37, -6.0), parent='chest', rot=(-3, 0, 3), mat=wood_mat)
    for i, yy in enumerate((-37, -35.5, -34, -32.5)):
        box('cross', (-0.5, yy, -6.9 - (i % 2) * 0.3), (1, 2, 1), mat=iron_mat, inflate=0.12 if i % 2 else 0.0)
    box('cross', (-1.5, -31, -7.8), (3, 16, 2), decals={'front': art(CROSS_BLOOD, BAND_PAL)})
    box('cross', (-5, -19, -8.2), (10, 2, 2))

    # ---------------- neck: grey stretched sinew with a dislocated vertebra
    bone('neck', (0, -36, -0.5), parent='chest', rot=(-18, 0, 0), mat=skin_mat)
    box('neck', (-3, -42, -3), (6, 7, 6), name='neckcore')
    box('neck', (-1, -41, 2.6), (2, 2, 2), mat=bone_mat, name='vertebra')

    # ---------------- head
    bone('head', (0, -41, -1), parent='neck', rot=(8, 0, 15), mat=skin_mat)
    # recessed skull: the sockets live on its front (z -6), 2.5 texels behind the brow
    fbox('head', (-8, -58, -6), (16, 16, 13), name='skull')
    fbox('head', (-7, -56, -7.5), (14, 2, 2), name='forehead')
    fbox('head', (-7, -54, -8.5), (14, 2, 3), name='brow')
    # cheekbones push out past the wimple line
    fbox('head', (-9, -47, -9), (4, 4, 3), name='cheek')
    fbox('head', (5, -47, -9), (4, 4, 3), name='cheek')
    # protruding muzzle (in front of the coif), two nasal slits, black upper lip
    fbox('head', (-6, -46, -10.5), (12, 4, 5), mat=palate_mat, name='maxilla')
    box('head', (-8, -42, -10.0), (16, 4, 0), mat=teeth_mat, name='upper_teeth')
    box('head', (-8, -42, -9.0), (16, 4, 0), mat=teeth_mat, name='upper_teeth_2')
    box('head', (-7.5, -42, -8.5), (15, 6, 7), mat=throat_mat, name='throat',
        decals={'front': art(THROAT_ART, THROAT_PAL), 'eyes:front': art(THROAT_GLOW, GLOWPAL)})
    # coif: band + wimple sides + wedges that turn the opening into a pointed arch
    fbox('head', (-9.5, -60, -9.5), (19, 4, 17), mat=linen_mat, name='band')
    fbox('head', (-9, -56, -8.5), (2, 12, 14), mat=linen_mat, name='wimple')
    fbox('head', (7, -56, -8.5), (2, 12, 14), mat=linen_mat, name='wimple')
    fbox('head', (-7, -56, -9), (2, 3, 1), mat=linen_mat, name='wedge')
    fbox('head', (5, -56, -9), (2, 3, 1), mat=linen_mat, name='wedge')
    fbox('head', (-7, -53, -9), (1, 2, 1), mat=linen_mat, name='wedge')
    fbox('head', (6, -53, -9), (1, 2, 1), mat=linen_mat, name='wedge')
    # blood-soaked grey wimple around the neck (stops the white mass at the chin)
    box('head', (-7, -42, -2.5), (14, 10, 9), mat=linen_mat, name='collar',
        decals={'front': art(COLLAR_ART, BAND_PAL)})
    # veil hood: rounded in three steps to a low peak; sides widen slightly as they fall
    box('head', (-9.5, -61, -8.5), (19, 2, 18), mat=veil_mat, name='hood')
    box('head', (-7.5, -63, -7.5), (15, 2, 16), mat=veil_mat, name='hood')
    box('head', (-4, -64, -6), (8, 1, 13), mat=veil_mat, name='hood')
    box('head', (-10.5, -59, -8), (2, 9, 17), mat=veil_mat, name='hood_side')
    box('head', (8.5, -59, -8), (2, 9, 17), mat=veil_mat, name='hood_side')
    box('head', (-11, -50, -7.5), (2, 8, 16), mat=veil_mat, name='hood_side')
    box('head', (9, -50, -7.5), (2, 8, 16), mat=veil_mat, name='hood_side')
    box('head', (-9, -59, 7), (18, 17, 2), mat=veil_mat, name='hood')
    # iron nails driven through the band (different lengths, 2x2 heads)
    for nx, ny, ln in ((-5, -59, 5), (0, -58, 4), (4, -59, 6)):
        box('head', (nx, ny, -9.5 - ln), (1, 1, ln), mat=iron_mat)
        box('head', (nx - 0.5, ny - 0.5, -10.5 - ln), (2, 2, 1), mat=iron_mat)

    # ---------------- jaw (hinge level with the mouth line so it drops instead of sliding into the neck)
    bone('jaw', (0, -38, -1.5), parent='head', rot=(12, 0, 0), mat=jaw_mat)
    fbox('jaw', (-8, -38, -9.5), (16, 4, 8), name='jaw')
    box('jaw', (-8, -41, -9.2), (16, 3, 0), mat=teeth_mat, name='lower_teeth')
    box('jaw', (-8, -41, -8.4), (16, 3, 0), mat=teeth_mat, name='lower_teeth_2')
    fbox('jaw', (-4, -34, -9), (8, 3, 6), name='chin')
    fbox('jaw', (-2, -31, -8.5), (4, 3, 4), name='chin_point')

    # ---------------- veil: upper drape follows the head down to the nape, lower part lies on the hump
    bone('veil', (0, -57, 8.5), parent='head', rot=(6, 0, 0), mat=veil_mat)
    box('veil', (-8.5, -57, 8.5), (17, 18, 3), name='veil_hi')
    bone('veil_lower', (0, -41, 8.5), parent='chest', rot=(-8, 0, 0), mat=veil_mat)
    box('veil_lower', (-11, -41, 8.5), (22, 38, 1), name='veil_lo')
    for side, sx in (('right', -1), ('left', 1)):
        vb = f'veil_{side}'
        bone(vb, (8.5 * sx, -39, 5), parent='chest', rot=(-9, 0, -16 * sx), mat=veil_mat)
        box(vb, (8.5 * sx - (7 if sx < 0 else 0), -39, 5), (7, 26, 1), name='veil_side')

    # ---------------- arms: thin upper arm, bell sleeve flaring 7 -> 10 -> 13, ragged drapes, spider hands
    for side, sx in (('right', -1), ('left', 1)):
        ax = 9.5 * sx
        ay = -33 if side == 'right' else -36       # right shoulder dropped
        az = 2.5
        arm, fa = f'{side}_arm', f'{side}_forearm'
        bone(arm, (ax, ay, az), parent='chest', rot=(-4, 0, -10 * sx), mat=wool_mat)
        box(arm, (ax - 3.5, ay - 3, az - 3.5), (7, 6, 7), name='shoulder')
        box(arm, (ax - 2.5, ay + 2, az - 2.5), (5, 13, 5))
        ey = ay + 15
        bone(fa, (ax, ey, az), parent=arm, rot=(-60 if sx < 0 else -72, 0, 6 * sx), mat=wool_mat)
        box(fa, (ax - 3.5, ey - 1, az - 3.5), (7, 7, 7))
        box(fa, (ax - 5, ey + 5, az - 5), (10, 6, 10))
        box(fa, (ax - 6.5, ey + 10, az - 6.5), (13, 6, 13), name='cuff')
        sl = f'{side}_sleeve'
        bone(sl, (ax, ey + 10, az), parent=fa, rot=(6, 0, 0), mat=drape_mat)
        box(sl, (ax - 6.5, ey + 10, az + 6.7), (13, 18, 0))                       # back drape (longest)
        box(sl, (ax + 6.7 * sx, ey + 10, az - 6.5), (0, 15, 13))                  # outer side drape
        box(sl, (ax + (3.5 if sx > 0 else -6.5), ey + 10, az - 6.7), (3, 11, 0))  # front-outer tatter
        # hand emerges from the dark cuff
        hy = ey + 14
        hand = f'{side}_hand'
        hrot = (52, 16, 6) if sx < 0 else (64, -22, -8)
        bone(hand, (ax, hy, az), parent=fa, rot=hrot, mat=hand_mat)
        box(hand, (ax - 3, hy - 2, az - 1.5), (6, 9, 3), name='palm')
        box(hand, (ax - 3.5, hy + 6, az - 1.5), (7, 2, 3), name='knuckles')
        flen = [(8, 6), (10, 7), (9, 7), (7, 5)]
        offs = [-3.0, -1.0, 1.0, 3.0]
        for f in range(4):
            fb = f'{side}_finger_{f + 1}'
            cx = ax + offs[f] * (-sx)
            fz = az - 0.6 + f * 0.2
            by = hy + 7.5
            l1, l2 = flen[f]
            bone(fb, (cx, by, fz + 0.5), parent=hand, rot=(6 + f * 3, 0, (f - 1.5) * 10 * sx), mat=hand_mat)
            box(fb, (cx - 0.5, by, fz), (1, l1, 1), inflate=0.3)
            tb = fb + '_tip'
            bone(tb, (cx, by + l1, fz + 0.5), parent=fb, rot=(14 + f * 4, 0, 0), mat=hand_mat)
            box(tb, (cx - 0.5, by + l1, fz), (1, l2, 1), inflate=0.24)
            box(tb, (cx - 0.5, by + l1 + l2 - 0.3, fz), (1, 5, 1), mat=claw_mat, inflate=0.16)
            cb = f'{side}_claw_{f + 1}'
            cy = by + l1 + l2 + 4.6
            bone(cb, (cx, cy, fz + 0.5), parent=tb, rot=(35, 0, 0), mat=claw_mat)
            box(cb, (cx - 0.5, cy, fz), (1, 4, 1), mat=claw_mat, inflate=0.03)
        th = f'{side}_thumb'
        tx = ax + 3.2 * sx
        bone(th, (tx, hy + 1, az - 1), parent=hand, rot=(-24, 0, 26 * sx), mat=hand_mat)
        box(th, (tx - 0.5, hy + 1, az - 1.5), (1, 7, 1), inflate=0.28)
        box(th, (tx - 0.5, hy + 7.7, az - 1.5), (1, 4, 1), mat=claw_mat, inflate=0.14)

    m = Model('monja', 256, 256, r.roots)
    m.scale = 0.5
    return m


def _hands(splay, curl, claw, thumb=0.0):
    """Finger spread (z, outward), knuckle curl of the tips and hook of the claws for both hands."""
    out = {}
    for side, sx in (('right', -1), ('left', 1)):
        for f in range(4):
            out[f'{side}_finger_{f + 1}'] = (0, 0, (f - 1.5) / 1.5 * splay * sx, 0, 0, 0)
            out[f'{side}_finger_{f + 1}_tip'] = (curl, 0, 0, 0, 0, 0)
            out[f'{side}_claw_{f + 1}'] = (claw, 0, 0, 0, 0, 0)
        out[f'{side}_thumb'] = (0, 0, thumb * sx, 0, 0, 0)
    return out


POSES = {
    # the jumpscare: rises and lunges, arms flung up and OUT so the claws frame the face (never cross it),
    # head snapped sideways, jaw unhinged
    'attack': {
        'body': (0.06, 0, 0, 0, -1.5, -2.0),
        'chest': (-0.1, 0, 0, 0, 0, 0),
        'neck': (-0.1, 0, 0, 0, 0, 0),
        'head': (-0.15, 0, 0.35, 0, 0, 0),
        'jaw': (0.75, 0, 0, 0, 3.0, -1.5),
        'veil': (0.25, 0, 0, 0, 0, 0),
        'veil_lower': (0.2, 0, 0, 0, 0, 0),
        'right_arm': (-2.8, 0, -0.45, 0, 0, 0),
        'left_arm': (-2.4, 0, 0.75, 0, 0, 0),
        'right_forearm': (0.9, 0, 0, 0, 0, 0),
        'left_forearm': (0.3, 0, 0, 0, 0, 0),
        'right_hand': (-0.25, 0, 0, 0, 0, 0),
        'left_hand': (-0.3, 0, 0, 0, 0, 0),
        'right_sleeve': (0.5, 0, 0, 0, 0, 0),
        'left_sleeve': (0.5, 0, 0, 0, 0, 0),
        **_hands(0.25, 0.5, 0.3, 0.3),
    },
    # head thrown back, jaw at max, arms out and back, fingers splayed: the shriek
    'scream': {
        'chest': (-0.2, 0, 0, 0, 0, 0),
        'neck': (-0.15, 0, 0, 0, 0, 0),
        'head': (-0.45, 0, 0.15, 0, 0, 0),
        'jaw': (1.1, 0, 0, 0, 1.0, -0.5),
        'veil': (0.3, 0, 0, 0, 0, 0),
        'veil_lower': (0.25, 0, 0, 0, 0, 0),
        'veil_right': (0, 0, 0.2, 0, 0, 0),
        'veil_left': (0, 0, -0.2, 0, 0, 0),
        'right_arm': (0.3, 0, 0.5, 0, 0, 0),
        'left_arm': (0.3, 0, -0.5, 0, 0, 0),
        'right_forearm': (0.5, 0, 0, 0, 0, 0),
        'left_forearm': (0.6, 0, 0, 0, 0, 0),
        'right_hand': (-0.6, 0, 0, 0, 0, 0),
        'left_hand': (-0.7, 0, 0, 0, 0, 0),
        **_hands(0.35, -0.2, 0.0, 0.4),
    },
    # holy light / fire: cowers, forearms crossed over the face, head ducked and turned away
    'burn': {
        'body': (0, 0, 0, 0, 1.5, 0),
        'chest': (0.45, 0, 0, 0, 0, 0),
        'head': (0.4, 0.35, 0, 0, 0, 0),
        'jaw': (0.5, 0, 0, 0, 0, 0),
        'veil': (-0.2, 0, 0, 0, 0, 0),
        'right_arm': (-2.1, -0.3, 0, 0, 0, 0),
        'left_arm': (-2.1, 0.6, 0, 0, 0, 0),
        'right_forearm': (0.5, 0, 0, 0, 0, 0),
        'left_forearm': (1.0, 0, 0, 0, 0, 0),
        'right_hand': (-0.5, 0, 0, 0, 0, 0),
        'left_hand': (-0.6, 0, 0, 0, 0, 0),
        'right_sleeve': (-0.3, 0, 0, 0, 0, 0),
        'left_sleeve': (-0.3, 0, 0, 0, 0, 0),
        **_hands(0.1, 0.7, 0.4, -0.2),
    },
}

ANIM_NOTES = """
Sor Agonia -- animation contract.  Angles in radians, ADDED to the rest pose; offsets (dx, dy, dz) in model
texels at 2x density (inside scale_root: 2 texels = 1 vanilla pixel).  t = ageInTicks, s = glide speed 0..1.
She never walks: no legs, the robe glides.  Everything moves slow and smooth EXCEPT the head snaps, which are
instant (1-2 ticks) -- that contrast is what makes the clips scary.

ROOT
* body -- root at the waist: 13-texel wasp waist, leather cincture, hip yoke.  HOVER BOB: dy = -1.5 +
  sin(t*0.08)*1.2 (the hem stays 1-3 texels above the ground, never touches it).  Idle: slow yaw drift
  sin(t*0.02)*0.05.  Glide/chase: xRot +0.12*s (leans into the motion), side roll sin(t*0.15)*0.04, NO step
  bob.  Attack: (0.06, 0, 0, 0, -1.5, -2) rises and lunges.  Scream: dy -1 (lifts).  Burn: dy +1.5 (sinks,
  recoils) + shiver zRot sin(t*2.1)*0.03.

ROBE -- 8 flared torn habit panels, children of body, pivots at the hips (rest flare -13..-16 deg on x,
yawed 45 deg apart; k = 0..7 in this order):
* robe_front, robe_front_right, robe_right, robe_back_right, robe_back, robe_back_left, robe_left,
  robe_front_left -- each sways on its own local x OUT OF PHASE: xRot += sin(t*0.09 + k*0.8)*0.07 (+-4 deg),
  so the hem ripples like cloth under water.  Glide/chase: back panels (k 3..5) trail +0.25*s, front panels
  (k 0,1,7) press back -0.12*s, side panels (k 2,6) flutter sin(t*0.4 + k)*0.1*s.  Attack: all flare out an
  extra -0.15 (a gust).  Scream: -0.2 plus tremble sin(t*1.7 + k)*0.04.  Burn: collapse inward +0.1 with
  twitches.
* rosary -- bone beads + small wooden cross hanging from the cincture (right hip).  Pendulum that LAGS the
  body ~8 ticks: zRot = sin(t*0.07 - 0.6)*0.12, xRot = -bodyXRot*0.8 + 0.3*s (swings back when gliding).
  Attack: flicks forward -0.4 then settles.  Burn: rattles zRot sin(t*2.6)*0.08.

TORSO
* chest -- ribcage, hunched hump, sloped shoulder yoke, vertebrae through the veil, bloody bib.  Rest is
  hunched 14 deg with the right shoulder dropped.  Idle: breathing xRot sin(t*0.06)*0.03 and every ~8 s a
  crack-twist (zRot snaps +0.12 for 3 ticks, eases back).  Glide/chase -0.08 (head pushed forward).  Attack
  -0.1.  Scream -0.2 (throws itself back).  Burn +0.45 (folds over).
* cross -- inverted wooden cross on its iron chain from the neck.  Pendulum lagging the chest ~10 ticks:
  xRot = -chestXRot*0.7 + sin(t*0.07 - 1.0)*0.06, zRot = sin(t*0.05)*0.08.  Chase: swings back +0.3*s.
  Burn: jitters zRot sin(t*3)*0.05 (it burns her).
* neck -- stretched grey neck with a dislocated vertebra.  Idle: creak yRot sin(t*0.03)*0.08.  Attack -0.1,
  scream -0.15.  'Owl turn': when the player looks away, neck yRot may go to +-1.4 over 40 ticks.
* head -- hood, coif, corpse face, nails; FOCUS bone and jumpscare portrait.  Follows look yaw/pitch (clamp
  yaw +-0.9, neck adds the rest).  SIGNATURE: snap tilts -- every 60-120 ticks zRot jumps +-0.6..1.57 (up to
  a 90 deg tilt) in 1-2 ticks, holds 20-40 ticks, drifts back over 30.  Idle micro-twitch zRot += 0.15 for
  1 tick (3% chance per tick).  Attack (-0.15, 0, 0.35) snapped instantly.  Scream (-0.45, 0, 0.15).  Burn
  (0.4, 0.35, 0): ducks and turns away from the light.
* jaw -- mandible with the lower needle teeth and the long pointed chin; hinge at the mouth line.  Idle:
  hangs slack with a tremble xRot = 0.05 + sin(t*0.9)*0.02 and slowly opens to 0.4 while she stares at the
  player.  Glide 0.15.  Attack (0.75, 0, 0, 0, +3, -1.5): the jaw UNHINGES downward.  Scream (1.1, 0, 0, 0,
  +1, -0.5) + shiver sin(t*2.5)*0.04.  Burn 0.5 (gasping).

VEIL
* veil -- upper veil block falling from the back of the hood to the nape (child of head).  Trails opposite
  to the head: xRot = -headXRot*0.4 + 0.25*s; idle sway sin(t*0.05)*0.04.  Attack +0.25, scream +0.3 (blown
  back), burn -0.2.
* veil_lower -- long black veil lying on the hump (child of chest), torn V bottom and the slit the vertebrae
  push through.  Idle xRot sin(t*0.05 - 0.5)*0.05.  Glide/chase: trails +0.35*s with ripple sin(t*0.3)*0.05*s.
  Attack +0.2, scream +0.25.
* veil_right / veil_left -- side panels behind the shoulders that frame them from the front.  Flutter out of
  phase: zRot += sin(t*0.07 + side)*0.06; chase xRot +0.3*s (trail); scream opens them out (+0.2 / -0.2).

ARMS -- right_* is -X (viewer's left).  Rest = 'ghost hands': forearms raised forward 60/72 deg, hands
drooping limp from the wrists, fingers dangling.
* right_arm / left_arm -- shoulder cap + thin upper sleeve; pivots at the shoulders (right one lower).  Idle
  sway xRot sin(t*0.05 + side)*0.04.  Glide: drift back +0.15*s (no walking swing).  Chase: reach forward
  -0.6*s.  Attack right (-2.8, 0, -0.45) / left (-2.4, 0, 0.75): flung UP and OUT so the claws frame the face,
  never crossing it.  Scream (0.3, 0, +-0.5) out and back.  Burn right (-2.1, -0.3, 0) / left (-2.1, 0.6, 0).
* right_forearm / left_forearm -- bell sleeve flaring 7 -> 10 -> 13 with the dark open cuff.  Idle bob
  sin(t*0.06 + side)*0.05.  Attack +0.9 / +0.3 (unfold), scream +0.5 / +0.6, burn +0.5 / +1.0 (wrists cross
  in front of the eyes).
* right_sleeve / left_sleeve -- ragged drapes hanging from the cuff (long back drape, outer side drape, front
  tatter).  Pure secondary motion: xRot lags its forearm ~6 ticks + flutter sin(t*0.2 + side)*0.08; chase
  +0.35*s (trails back).  Attack +0.5, burn -0.3.
* right_hand / left_hand -- long grey bony hand (palm + knuckles), droops limp at rest.  Idle slow curl
  sin(t*0.04)*0.06.  Attack -0.25 / -0.3 (wrist lifts so the hooked claws face the victim), scream -0.6 /
  -0.7, burn -0.5 / -0.6.
* {side}_finger_1..4 (1 = outer, 4 = inner) -- first phalanx, splayed on z.  Idle: ONE finger at a time
  twitches (every 25-40 ticks pick one, xRot +0.35 for 2 ticks, ease back -- spider tapping).  Attack splay
  zRot +-0.25 outward, scream +-0.35, burn +-0.1.
* {side}_finger_1..4_tip -- second phalanx; follows its finger with a 3-tick lag.  Attack +0.5 (curl),
  scream -0.2 (straighten), burn +0.7 (clench).
* {side}_claw_1..4 -- hooked black claw (35 deg hook).  Attack +0.3 (rake), burn +0.4, idle +0.05 tick
  whenever its finger twitches.
* right_thumb / left_thumb -- thumb with its claw, curled inward.  Attack opens zRot +-0.3, scream +-0.4,
  burn -+0.2 (clenches).

LAYERING
idle = hover bob + breathing + robe ripple + veil sway + random head snaps + finger taps + jaw tremble.
glide/chase = idle + lean + trailing cloth (back robe panels, veil, veil_lower, veil sides, sleeves) * speed.
attack = blend 4 ticks into POSE_ATTACK, hold 6, release over 10.  scream = POSE_SCREAM during the shriek.
burn = POSE_BURN while in light / holy water, with jitter on chest, hands and cross.
"""
