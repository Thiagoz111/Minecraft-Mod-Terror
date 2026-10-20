"""Sor Agonia -- the demonic nun of the Convento de Santa Ines (DEAD LINE).

Authored at 2x texel density (model.scale = 0.5).  +Y down, ground y = 24, faces -Z.  Centred on x = 0, z = 0.

Design (round 3)
----------------
Silhouette: a tall black A.  A small, tight head (~30 % of the height) in a white coif whose opening is a
pointed gothic arch; the black hood is chamfered into a soft dome and flows into two wide veil drapes that fall
over the shoulders and flare out to elbow level, so from the front the head pours into a black triangle with
the white guimpe (shoulder bib) in the middle.  Under it a tapered bodice (14 -> 10 -> 8) is cinched by a
leather cincture, cloth bulging over the belt, hips widen again and a long robe of eight torn panels (tops tucked
under the hips) falls to a shredded hem that floats two texels above the ground.  A scapular runs from the
chest to the hem, front and back, so the habit reads as one continuous garment.  Long arms end in bell sleeves
built from three flared cloth panels with a pitch-black inside, out of which come grey bony hands with knuckled
fingers and horn-tipped claws reaching below the knees.  Inverted wooden cross on an iron chain on the chest,
bone rosary hanging to the knee from the front-left of the cincture, barbed wire around the coif band with two
short rusted nails driven in at the temples.

Face (one pixel-art mask, FACE, projected onto the layered face cubes): corpse-white, the lit planes
(forehead, brow, cheekbones, muzzle, chin) at the top of the ramp with greys only in the creases; a near-black
shadow line separates it from the off-white linen.  Heavy V brow over two deep organic sockets with pin-point
ember pupils at different heights; a 1-px white bridge falling into two crisp black nasal slits; one continuous
black lip line that tears upward onto the cheekbones; interlocked needle teeth in two rows; a separate jaw
that unhinges onto a pure black gullet with a dark red tongue.
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
# off-white starched linen: cool grey-blue shadows -> warm off-white lights; dirt only on the edges
LINEN = [hx('#16171e'), hx('#2c2f3b'), hx('#484c5b'), hx('#6b707f'), hx('#9196a2'), hx('#b7b8b5'),
         hx('#d6d0bf'), hx('#e9e4d5')]
DIRTY = hx('#a99467')
# corpse skin: cold green-grey shadows, paper-white lights
SKIN = [hx('#16161c'), hx('#2b2c33'), hx('#45474d'), hx('#666a6b'), hx('#8d918c'), hx('#b3b6ad'),
        hx('#d3d5ca'), hx('#eeeee3')]
HANDC = [hx('#111115'), hx('#212127'), hx('#36363e'), hx('#4f4f58'), hx('#6c6b74'), hx('#8c8a92'),
         hx('#aeabb0'), hx('#cfccce')]
VEIN = hx('#1a0e1c')
VEIN2 = hx('#4a3a52')
CRACK = hx('#3a3a42')
# claws: dark red-black root -> horn -> yellowed bright tip (reads against the black habit)
CLAW = [hx('#0e0304'), hx('#260709'), hx('#3e1211'), hx('#5e2c1e'), hx('#8a5a3a'), hx('#b89668'),
        hx('#e6d6aa')]
EMBER = [hx('#2a0300'), hx('#6e1200'), hx('#c23a00'), hx('#ff7a0a'), hx('#ffc23a'), hx('#fff3b8')]
MOUTH = [hx('#020102'), hx('#0c0305'), hx('#1e070c'), hx('#3a0f16'), hx('#5c1d28'), hx('#86343f')]
LIP = [hx('#030204'), hx('#120a0f'), hx('#21161d'), hx('#33252e')]
TEETH = [hx('#2a241b'), hx('#4c4333'), hx('#76694f'), hx('#a09276'), hx('#c8bc9c'), hx('#e6dec5')]
WOOD = [hx('#170d07'), hx('#2a190d'), hx('#432914'), hx('#5f3d1f'), hx('#7c542c'), hx('#9a6e3c'),
        hx('#c4955c'), hx('#e0b47a')]
IRON = [hx('#0f0f12'), hx('#212126'), hx('#38383f'), hx('#55555e'), hx('#7a7a84'), hx('#a2a2ac')]
RUSTC = [hx('#1c0b05'), hx('#35160a'), hx('#562710'), hx('#7a3c18'), hx('#a05a2a'), hx('#d08a4e')]
RUST = hx('#5a2a12')
LEATHER = [hx('#0a0605'), hx('#170e0b'), hx('#251812'), hx('#36241a'), hx('#4a3224'), hx('#5e4130')]
BONE = [hx('#3a3226'), hx('#5c5140'), hx('#837559'), hx('#a89878'), hx('#c9bb9a'), hx('#e2d8bd'), hx('#f4eedc')]
BLOOD = [hx('#160003'), hx('#330207'), hx('#55050c'), hx('#7a0a13'), hx('#9e141c')]
DRIED = hx('#3b120c')
DUST = hx('#4a4552')
WAX = [hx('#6e6650'), hx('#b8ae8a'), hx('#ddd3b0')]
SCORCH = [hx('#0b0503'), hx('#24110a'), hx('#4a2410'), hx('#7a3a12')]


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
    """Broad folds: a lit ridge, a soft body and ONE strong crease each, wandering a little along the length."""
    ph = (u + (vnoise(u * 0.13, y * 0.05, seed, 3) - 0.5) * 3.0 + seed * 0.37) % period / period
    if ph < 0.10:
        return 0.11
    if ph < 0.50:
        return 0.04
    if ph < 0.78:
        return -0.02
    if ph < 0.88:
        return -0.08
    return -0.17


def hem_cut(col, k, h):
    """Ragged torn hem: jagged base + a few deep V rips."""
    g, ph = col // 4, col % 4
    r = hash3(g, k, 0, 11)
    rip = 0.0
    if r > 0.6:
        rip = (3 + (r - 0.6) * 24) * (1 - abs(ph - 1.5) / 2.2)
    return h - 0.4 - hash3(col, k, 0, 12) * 2.6 - rip


SLEEVE_INNER = {'slv_f': 'back', 'slv_b': 'front', 'slv_or': 'east', 'slv_ol': 'west', 'slv_ir': 'west',
                'slv_il': 'east'}
HEMMED = ('panel', 'scap', 'slv_f', 'slv_b', 'slv_or', 'slv_ol')


def wool_mat(ctx):
    """Heavy black habit wool: broad folds, seams, stitched + singed hem, scorch marks and candle-wax drips."""
    if is_plane(ctx) and ctx.face == 'back':
        return None
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    t = tag(ctx)
    f = ctx.face
    k = int(hash3(cseed(ctx), 1, 0, 2) * 50)
    if t in SLEEVE_INNER and f == SLEEVE_INNER[t]:
        return pick(WOOL, 0.02 if ly > 2 else 0.12)          # pitch-black inside of the bell sleeve
    if t == 'core' and f == 'bottom':
        return WOOL[0]
    col = int(lx) if f in ('front', 'back', 'top') else (int(lz) if f in ('west', 'east') else 0)
    cut = h + 1
    if t in HEMMED:
        if f == 'bottom':
            return None
        cut = hem_cut(col, k, h)
        if ly > cut:
            return None
    if t == 'tatter':
        if ly > h - 0.5 - hash3(int(lx), k, 0, 13) * min(6, h * 0.6):
            return None
    v = 0.5 + face_light(ctx) * 1.2
    if f in ('front', 'back', 'west', 'east'):
        v += fold_shade(across(ctx), ly, k, 10.0 if t == 'panel' else 7.0)
    if edge(ctx) == 0 and not is_plane(ctx) and f != 'top':
        v -= 0.07
    if t == 'panel':
        if f == 'back':
            v -= 0.25
        if f in ('west', 'east'):
            v -= 0.12
        v += 0.05 - ly / h * 0.12
    if t == 'scap':
        v += 0.04
        if f == 'front' and (ctx.i == 0 or ctx.i == ctx.w - 1):
            v += 0.12                                       # turned edge of the scapular catches the light
    c = pick(WOOL, v)
    if t == 'scap' and f == 'front' and ctx.i in (1, ctx.w - 2) and ctx.j % 2 == 0:
        c = mix(c, DUST, 0.45)                              # running stitch along both edges
    if t == 'panel' and f == 'front' and ctx.i == 1 + k % 3 and ctx.j % 3 != 2 and k % 2 == 0:
        c = mix(c, WOOL[0], 0.7)                            # seam
    if t in HEMMED or t == 'tatter':
        dist = cut - ly
        if dist < 1.0:
            c = mix(c, DUST, 0.55)                          # frayed threads catch the light
        elif dist < 3.5:
            c = mix(c, LEATHER[1], 0.5)                     # singed, filthy hem
        elif 4.0 <= dist < 5.0 and f in ('front', 'back') and ctx.i % 2 == 0 and t in ('panel', 'scap'):
            c = mix(c, DUST, 0.5)                           # stitched hem line
        if t in ('panel', 'slv_f', 'slv_b', 'slv_or', 'slv_ol'):
            s = vnoise(lx * 0.35, ly * 0.35, k, 21)
            if ly > h * 0.55 and s > 0.66 and f != 'top':
                c = pick(SCORCH, (s - 0.66) * 9)            # scorch blotches: holy fire has touched her
                if s > 0.76 and hash3(ctx.i, ctx.j, k, 22) > 0.7:
                    c = SCORCH[3]
        if t in ('panel', 'scap', 'slv_f') and f == 'front':
            if hash3(col, k, 0, 23) > 0.9:                  # candle-wax drips
                top = h * 0.35 + hash3(col, k, 1, 24) * h * 0.3
                ln = 2 + int(hash3(col, k, 2, 25) * 4)
                if top <= ly < top + ln:
                    c = WAX[2] if ly < top + 1 else WAX[1] if ly < top + ln - 1 else WAX[0]
        if t == 'panel' and ly > h * 0.6 and hash3(int(lx), int(ly), k, 14) > 0.985:
            return None                                     # moth holes
    return c


def veil_mat(ctx):
    """Matte black veil: long soft folds, torn trailing edges, radial folds on the crown."""
    if is_plane(ctx) and ctx.face == 'back':
        return None
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    t = tag(ctx)
    f = ctx.face
    sd = cseed(ctx)
    if t in ('veil_lo', 'veil_side', 'veil_hi') and f != 'top':
        if f == 'bottom':
            return None
        col = int(lx) if f in ('front', 'back') else int(lz)
        if t == 'veil_lo':
            cut = hem_cut(col, 77, h) - abs(lx - w / 2) * 0.9
            if abs(lx - w / 2) < 1.1 and ly < 12:
                return None                                 # torn slit: the vertebrae tear through here
        elif t == 'veil_side':
            cut = hem_cut(col * 2, 31 + sd % 7, h) - (col * 0.5)
        else:
            cut = hem_cut(col, 5, h)
        if ly > cut:
            return None
    v = 0.5 + face_light(ctx) * 1.1
    if f in ('front', 'back', 'west', 'east'):
        v += fold_shade(across(ctx), ly, sd % 31, 7.0) * 0.8
    if f == 'top' and t in ('hood', 'peak', 'chamfer'):
        ang = math.atan2(ctx.z - 0.0, ctx.x)
        ph = (ang * 7 / math.pi + vnoise(ctx.x * 0.2, ctx.z * 0.2, 3, 5) * 0.8) % 1.0
        v += 0.1 if ph < 0.2 else (-0.12 if ph > 0.8 else 0.0)   # radial folds gathered at the crown
    if edge(ctx) == 0 and f != 'top' and not is_plane(ctx):
        v -= 0.07
    return pick(VEILC, v)


def linen_mat(ctx):
    """Starched off-white coif / wimple / guimpe: cool blue-grey shade ramp, yellowed dirt only on the edges."""
    if is_plane(ctx) and ctx.face == 'back':
        return None
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    t = tag(ctx)
    f = ctx.face
    v = 0.8 + face_light(ctx) * 0.9
    if f in ('west', 'east'):
        v -= 0.13
    elif f == 'back':
        v -= 0.25
    if t == 'gorget':
        v -= 0.16                                           # in shadow under the jaw
    if t == 'neckl':
        v -= 0.3
    if t == 'wimple' and f == 'front' and ctx.i % 3 == 1 and ctx.w > 2:
        v -= 0.05                                           # faint starched pleats
    if t == 'arch' and f == 'front' and ctx.j >= ctx.h - 1:
        v = 0.3                                             # shadow line along the gothic arch opening
    if t == 'bib' and f == 'front':
        cx = abs(lx - w / 2)
        hw = w / 2 - max(0.0, ly - (h - 3.2)) ** 1.5 * 1.25
        if cx > hw:
            return None                                     # rounded guimpe bottom
    c = pick(LINEN, v)
    if edge(ctx) == 0 and f != 'top' and t not in ('arch',):
        c = mix(c, DIRTY, 0.33)
    if t == 'bib':
        soak = (ly - (h - 3.0)) / 3.0
        if soak > 0 and f in ('front', 'west', 'east'):
            c = mix(c, BLOOD[2], min(0.85, soak * 0.9))     # blood-soaked lower edge
        if f == 'front' and 0.4 < abs(lx - w / 2) < 5.5 and hash3(int(lx), 0, 0, 41) > 0.55:
            ln = 1 + hash3(int(lx), 1, 0, 42) * 4.5
            if ly < ln:
                c = BLOOD[3] if ly < ln - 1 else BLOOD[4]   # drips running down from the mouth
    if t == 'gorget' and f == 'front':
        if hash3(int(lx), 0, 0, 43) > 0.5 and ly < 1 + hash3(int(lx), 1, 0, 44) * 3:
            c = mix(c, BLOOD[2], 0.8)
    return c


# ------------------------------------------------------------------ flesh
def skin_mat(ctx):
    """Corpse-white skin with one subtle ramp; the front details are hand-placed decals (see FACE)."""
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    f = ctx.face
    t = tag(ctx)
    if f == 'top':
        return pick(SKIN, 0.38)
    if f == 'bottom':
        if t in ('skull', 'muzzle'):
            return pick(MOUTH, 0.2 + (1 - abs(lx - w / 2) / (w / 2)) * 0.25)   # wet palate in the open mouth
        return pick(SKIN, 0.3)
    v = 0.84 + face_light(ctx) * 0.5
    if f in ('west', 'east'):
        v -= 0.2 + (lz / max(1.0, d)) * 0.12
    elif f == 'back':
        v -= 0.4
    if edge(ctx) == 0 and f in ('west', 'east') and min(ctx.w, ctx.h) > 2:
        v -= 0.06
    c = pick(SKIN, v)
    if f in ('west', 'east') and hash3(ctx.i, ctx.j, cseed(ctx), 47) > 0.86:
        c = VEIN2
    return c


def throat_mat(ctx):
    """Pure black gullet; only the rim warms to a dark wet red."""
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    if ctx.face == 'front':
        cx = abs(lx - w / 2) / (w / 2)
        return pick(MOUTH, max(0.0, cx - 0.55) * 0.9)
    return pick(MOUTH, 0.05 + (1 - lz / max(1, d)) * 0.25)


def jaw_mat(ctx):
    """Mandible: skin outside, gum rim + dark red tongue on top (seen when the jaw drops)."""
    if ctx.face == 'top':
        lx, ly, lz = local(ctx)
        w, h, d = ctx.cube.size
        cx = abs(lx - w / 2)
        if lz < 1.0:
            return pick(MOUTH, 0.62)
        if cx < 3.2 and lz < d - 1:
            return pick(MOUTH, 0.55 - cx * 0.05 + (0.08 if int(lz) % 2 else 0))    # dark red tongue
        return pick(MOUTH, 0.08)
    if ctx.face == 'back':
        return pick(MOUTH, 0.1)
    return skin_mat(ctx)


# teeth: 'T' needle, 't' rotten / back-row tooth, 'g' gum.  13 wide (x -6.5..6.5), corners hidden in the wimple
UPPER_TEETH = [
    "gTgTTgTgTTgTg",
    ".T.TT.T.T..T.",
    ".T..T...T..T.",
]
UPPER_TEETH_2 = [
    "..t..t.t..t..",
    "..t....t..t..",
    ".............",
]
LOWER_TEETH = [
    ".T..T..T...T.",
    ".TT.T.TT.T.T.",
    "gTTgTgTTgTTTg",
]
LOWER_TEETH_2 = [
    ".............",
    "...t.t...t...",
    "...t.t...t...",
]
TEETH_ROWS = {'upper_teeth': UPPER_TEETH, 'upper_teeth_2': UPPER_TEETH_2,
              'lower_teeth': LOWER_TEETH, 'lower_teeth_2': LOWER_TEETH_2}


def teeth_mat(ctx):
    if ctx.face != 'front':
        return None
    t = tag(ctx)
    rows = TEETH_ROWS[t]
    ch = rows[ctx.j][ctx.i] if ctx.j < len(rows) and ctx.i < len(rows[ctx.j]) else '.'
    if ch == '.':
        return None
    if ch == 'g':
        return pick(MOUTH, 0.75)
    up = t.startswith('upper')
    tip = ctx.j / max(1, ctx.h - 1) if up else 1 - ctx.j / max(1, ctx.h - 1)
    v = 0.97 - tip * 0.28 if ch == 'T' else 0.4 - tip * 0.15
    if ch == 'T' and hash3(ctx.i, 0, 1 if up else 2, 33) > 0.84:
        v -= 0.3
    return pick(TEETH, v)


def hand_mat(ctx):
    """Long grey bony hands: tendons, lit knuckles, joint creases, tips darkening toward the claws."""
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    t = tag(ctx)
    v = 0.6 + face_light(ctx) * 1.1
    if t == 'phal':
        v -= (ly / h) * 0.16
        if ly < 0.7:
            v -= 0.12
    if t == 'knuckle':
        v += 0.14
    if t == 'palm' and ctx.face == 'front' and ly > 1.5 and int(lx) in (1, 3, 4):
        v += 0.08                                           # tendons
    if edge(ctx) == 0 and ctx.face != 'top' and min(w, h) > 2:
        v -= 0.07
    c = pick(HANDC, v)
    if t == 'palm' and ctx.face == 'front' and hash3(ctx.i, ctx.j, cseed(ctx), 48) > 0.88:
        c = VEIN2
    return c


def claw_mat(ctx):
    lx, ly, lz = local(ctx)
    h = ctx.cube.size[1]
    v = 0.1 + (ly / h) * 0.78 + face_light(ctx) * 0.8
    if ctx.face in ('front', 'west') and ctx.i == 0:
        v += 0.18                                           # pale gloss line
    return pick(CLAW, v)


def wood_mat(ctx):
    """Old cross wood: grain along the long axis, pale worn highlight on the upper-left edges."""
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    long_ = ly if h >= w else lx
    acr = lx if h >= w else ly
    v = 0.52 + face_light(ctx) * 1.3
    v += (vnoise(acr * 1.1, long_ * 0.15, cseed(ctx), 51) - 0.5) * 0.35
    if ctx.face == 'front' and (ctx.i == 0 or ctx.j == 0):
        v += 0.3
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


def nail_mat(ctx):
    """Rusted nail: rust-brown with a 1-px bright edge on the head."""
    v = 0.45 + face_light(ctx) * 1.2
    if ctx.face in ('front', 'top', 'west') and (ctx.i == 0 or ctx.j == 0):
        v += 0.42
    return pick(RUSTC, v)


def leather_mat(ctx):
    v = 0.5 + face_light(ctx) * 1.2
    if ctx.j in (0, ctx.h - 1) and ctx.face not in ('top', 'bottom'):
        v -= 0.2
    if ctx.face == 'front' and ctx.i % 4 == 1 and ctx.j == ctx.h // 2:
        v += 0.25
    return pick(LEATHER, v)


def bone_mat(ctx):
    v = 0.66 + face_light(ctx) * 1.3
    if edge(ctx) == 0 and min(ctx.w, ctx.h) > 1:
        v -= 0.16
    if ctx.face in ('front', 'west') and ctx.i == 0 and ctx.j == 0:
        v += 0.2
    return pick(BONE, v)


def string_mat(ctx):
    if ctx.face != 'front':
        return None
    return pick(LEATHER, 0.75)


# ------------------------------------------------------------------ the face mask
# One pixel-art image of the coif band + face as seen from the front (rest pose, head frame), projected onto every
# layered face cube by its x/y extent.  col c <-> texel centre x = c - 9 (19 columns, x -9..9), row r <-> y = -60 + r.
# '.' leaves the cube's own material.
GX0, GY0 = -9.5, -60
FACE = [
    # 0123456789012345678
    "..q....q...q....q..",   # r0  y-60  coif band: barbed wire (barbs)
    "iHiiHiiHiiHiiHiiHii",   # r1  y-59  twisted wire
    ".Bq....q...q....qB.",   # r2  y-58  barbs + blood from the two temple nails
    ".B.kkkkk464kkkkk.B.",   # r3  y-57  apex of the gothic arch
    ".b.kkkk478B4kkkk.b.",   # r4
    ".B.kkk5787b75kkk.d.",   # r5
    ".B.k4v78c7b87v4k...",   # r6  forehead: frown crease, blood drip, black veins at the temples
    ".bk3678875578763k..",   # r7  brow ridge (V frown, furrow at the centre)
    ".Bk2356643466532k..",   # r8  brow underside
    ".dk43qkKK5KKkq34k..",   # r9  sockets: right c4-8, 1-px bridge c9, left c10-14 (top inner corners deeper)
    "..kvqKKKK7korKq5k..",   # r10
    "..k5kKrok8qWyKkvk..",   # r11 right pupil low, left pupil high
    "..k5kKyWq74kKKk5k..",   # r12
    "..k63kKk4754kk36k..",   # r13 rounded socket bottoms
    "..k67877n8n77876k..",   # r14 cheekbones lit, nasal slits c8 / c10 around a white bridge
    "..kL6767n7n7676Lk..",   # r15 torn grin rising onto the cheekbones
    "..kBL456n6n654LBk..",   # r16 creases under the cheekbones
    "..kLLLLLLLLLLLLLk..",   # r17 y-43  one continuous black upper lip
    "...k...........k...",   # r18 y-42  teeth / gullet (own materials)
    "...k...........k...",   # r19
    "...k...........k...",   # r20
    "...LLLLLLLLLLLLL...",   # r21 y-39  lower lip (jaw)
    "...k3v6778776v3k...",   # r22 jaw
    "...k2V5667665V2k...",   # r23
    "......4566654......",   # r24 y-36  pointed chin
]
assert all(len(r) == 19 for r in FACE), [len(r) for r in FACE]

FPAL = {
    '1': SKIN[0], '2': SKIN[1], '3': SKIN[2], '4': SKIN[3], '5': SKIN[4], '6': SKIN[5], '7': SKIN[6], '8': SKIN[7],
    'K': (1, 1, 2, 255), 'k': (14, 11, 18, 255), 'q': (40, 30, 44, 255),
    'e': EMBER[1], 'r': EMBER[2], 'o': EMBER[3], 'y': EMBER[4], 'W': EMBER[5],
    'n': (1, 1, 2, 255),
    'c': CRACK, 'v': VEIN, 'V': VEIN2,
    'L': LIP[0], 'l': LIP[2],
    'B': BLOOD[2], 'b': BLOOD[4], 'd': DRIED,
    'i': IRON[1], 'H': RUSTC[4],
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


def build():
    r = Rig()

    def bone(name, pivot, parent=None, rot=(0, 0, 0), mat=None):
        return r.bone(name, pivot, parent=parent, rot=rot, mat=mat)

    def box(bone_, frm, size, mat=None, inflate=0.0, decals=None, name=None, mirror=False):
        c = r.box(bone_, frm, size, mat=mat, inflate=inflate, decals=decals, mirror=mirror)
        c.name = name
        return c

    def fbox(bone_, frm, size, mat=None, name=None, extra=None):
        """Face cube whose front is painted from the FACE mask (sliced by its rest-pose x/y extent)."""
        dec = face_decals(frm[0], frm[1], size[0], size[1])
        if extra:
            dec.update(extra)
        return box(bone_, frm, size, mat=mat, decals=dec, name=name)

    # ---------------- body (root, at the waist): cincture, hips that widen again under the wasp waist
    bone('body', (0, -20, 0), mat=wool_mat)
    box('body', (-4.5, -21, -3.5), (9, 2, 7), mat=leather_mat, inflate=0.3)
    box('body', (-1, -21.5, -4.4), (2, 3, 1), mat=iron_mat)
    box('body', (-7, -19, -6), (14, 6, 12), name='hips')

    # ---------------- robe: eight flared torn panels, tops tucked inside the hips; hem floats ~2 texels up
    flare = [-12, -15, -11, -15, -13, -15, -11, -15]
    lens = [41, 41, 40, 41, 41, 41, 40, 41]
    names = ['robe_front', 'robe_front_right', 'robe_right', 'robe_back_right',
             'robe_back', 'robe_back_left', 'robe_left', 'robe_front_left']
    for k, nm in enumerate(names):
        rr = 3.5 if k % 2 == 0 else 4.0
        yaw = k * 45 + (4 if k % 3 == 1 else -3 if k % 3 == 2 else 0)
        bone(nm, (0, -17, 0), parent='body', rot=(flare[k], yaw, 0), mat=wool_mat)
        box(nm, (-6.5, -17, -rr - 2), (13, lens[k], 2), name='panel')
        sx_ = -5 + (k * 3) % 8
        box(nm, (sx_, -17 + lens[k] - 6, -rr - 1), (2 + k % 2, 5 + k % 3, 0), name='tatter')

    # ---------------- scapular: one continuous strip chest -> hem, front and back
    bone('scapular_front', (0, -19, -6.6), parent='body', rot=(-12, 2, 0), mat=wool_mat)
    box('scapular_front', (-4, -19, -7.6), (8, 41, 1), name='scap')
    bone('scapular_back', (0, -19, 6.6), parent='body', rot=(13, -2, 0), mat=wool_mat)
    box('scapular_back', (-4, -19, 6.6), (8, 39, 1), name='scap')

    # ---------------- rosary of bone beads hanging to the knee from the front-left of the cincture
    bone('rosary', (3.5, -20.5, -6.8), parent='body', rot=(-16, 0, -4), mat=bone_mat)
    box('rosary', (3.5, -20.5, -6.8), (1, 20, 0), mat=string_mat)
    for i, yy in enumerate((-18.5, -15, -11.5, -8, -4.5, -1)):
        box('rosary', (3, yy, -7.8), (2, 2, 2), name='bead')
    box('rosary', (3.5, 0.5, -7.3), (1, 9, 1), mat=wood_mat, inflate=0.3)       # inverted cross, crossbar low
    box('rosary', (1.5, 5.5, -7.3), (5, 1, 1), mat=wood_mat, inflate=0.3)

    # ---------------- chest: tapered bodice 14 -> 10 -> 8, cloth bulging over the belt, hunched hump
    bone('chest', (0, -20, 0.5), parent='body', rot=(8, 0, -4), mat=wool_mat)
    box('chest', (-4, -26, -3), (8, 6, 6), name='waist')
    box('chest', (-4.5, -24, -3.5), (9, 3, 7), inflate=0.25, name='blouse')
    box('chest', (-5, -31, -3.5), (10, 5, 7), name='ribs')
    box('chest', (-7, -36, -4.5), (14, 5, 9), name='ribs')
    box('chest', (-8.5, -38, -4), (17, 3, 8), name='yoke')
    box('chest', (-6, -38, 2), (12, 9, 6), name='hump')
    for yy in (-37.5, -34):
        box('chest', (-1, yy, 7.8), (2, 2, 2), mat=bone_mat, name='vertebra')
    box('chest', (-4, -31, -5.0), (8, 10, 1), name='scap')
    # guimpe: rounded off-white shoulder bib, blood-soaked lower edge
    box('chest', (-9, -38, -5.6), (18, 7, 10), mat=linen_mat, name='bib')

    # ---------------- inverted wooden cross on a chain, over the guimpe and scapular
    bone('cross', (0, -37, -5.8), parent='chest', rot=(-4, 0, 3), mat=wood_mat)
    for i, yy in enumerate((-37.5, -36, -34.5)):
        box('cross', (-0.5, yy, -6.7 - (i % 2) * 0.3), (1, 2, 1), mat=iron_mat, inflate=0.12 if i % 2 else 0.0)
    box('cross', (-1.5, -33, -7.6), (3, 14, 2), decals={'front': art(CROSS_BLOOD, BAND_PAL)})
    box('cross', (-4.5, -24, -7.85), (9, 2, 2))

    # ---------------- neck (hidden in the wimple)
    bone('neck', (0, -37.5, -0.5), parent='chest', rot=(-9, 0, 0), mat=linen_mat)
    box('neck', (-4, -40, -4), (8, 5, 7), name='neckl')

    # ---------------- head: hood top -62, chin -35 (~30 % of the height)
    bone('head', (0, -38, -1), parent='neck', rot=(5, 0, 9), mat=skin_mat)
    fbox('head', (-6.5, -57, -7), (13, 15, 13), name='skull')
    fbox('head', (-5.5, -53, -9), (11, 2, 2), name='brow')
    fbox('head', (-6.5, -46, -8.75), (4, 3, 2), name='cheek')
    fbox('head', (2.5, -46, -8.75), (4, 3, 2), name='cheek')
    fbox('head', (-3.5, -45.75, -9.25), (7, 4, 4), name='muzzle')
    box('head', (-6.5, -42, -8.5), (13, 3, 0), mat=teeth_mat, name='upper_teeth')
    box('head', (-6.5, -42, -7.6), (13, 3, 0), mat=teeth_mat, name='upper_teeth_2')
    box('head', (-5.5, -41.75, -6.5), (11, 5, 7), mat=throat_mat, name='throat')
    # coif: band, wimple sides, lower wimple hiding the jaw corners, chin wrap
    fbox('head', (-9.5, -60, -9.5), (19, 3, 18), mat=linen_mat, name='band')
    fbox('head', (-9.5, -57, -9.5), (3, 15, 6), mat=linen_mat, name='wimple')
    fbox('head', (6.5, -57, -9.5), (3, 15, 6), mat=linen_mat, name='wimple')
    fbox('head', (-9.5, -42, -9.5), (4, 6, 6), mat=linen_mat, name='wimple')
    fbox('head', (5.5, -42, -9.5), (4, 6, 6), mat=linen_mat, name='wimple')
    box('head', (-8.5, -36, -8.5), (3, 2, 5), mat=linen_mat, name='wimple')
    box('head', (5.5, -36, -8.5), (3, 2, 5), mat=linen_mat, name='wimple')
    box('head', (-5.5, -36, -7.5), (11, 4, 9), mat=linen_mat, name='gorget')
    # black hood: low crown, sides, back
    box('head', (-8, -61.25, -10), (16, 2, 19), mat=veil_mat, name='hood')
    box('head', (-11, -59, -9), (2, 21, 18), mat=veil_mat, name='hood')
    box('head', (9, -59, -9), (2, 21, 18), mat=veil_mat, name='hood')
    box('head', (-9.5, -60, 7.5), (19, 22, 2), mat=veil_mat, name='hood')
    # gothic arch: two linen slabs meeting at the apex turn the opening into a pointed arch
    for side, sx in (('right', -1), ('left', 1)):
        ab = f'arch_{side}'
        bone(ab, (0, -57, -9.25), parent='head', rot=(0, 0, 34 * sx), mat=linen_mat)
        box(ab, (-8 if sx < 0 else 0, -61, -9.25), (8, 4, 2), name='arch')
        # chamfered hood corners: the white coif and the black hood lose their square corners
        hb = f'hood_{side}'
        bone(hb, (9.5 * sx, -59, 0), parent='head', rot=(0, 0, 45 * sx), mat=veil_mat)
        box(hb, (9.5 * sx - 3, -60.5, -10.25), (6, 3, 20), name='chamfer')
    bone('hood_peak', (0, -61.25, -0.5), parent='head', rot=(4, 0, -3), mat=veil_mat)
    box('hood_peak', (-5, -62.25, -7), (10, 1, 14), name='peak')
    # two short rusted nails driven in at the temples, at different angles
    for side, nx, ny, rot in (('right', -8, -58.5, (-28, 18, 22)), ('left', 8, -59, (-20, -24, -30))):
        nb = f'nail_{side}'
        bone(nb, (nx, ny, -9.5), parent='head', rot=rot, mat=nail_mat)
        box(nb, (nx - 0.5, ny - 0.5, -10.5), (1, 1, 1), mat=iron_mat)
        box(nb, (nx - 1, ny - 1, -11.5), (2, 2, 1))

    # ---------------- jaw: hinge in the wimple, drops onto a black gullet
    bone('jaw', (0, -40, -4), parent='head', rot=(5, 0, 0), mat=jaw_mat)
    fbox('jaw', (-6.5, -39, -9), (13, 3, 6), name='jaw')
    box('jaw', (-6.5, -42, -8.7), (13, 3, 0), mat=teeth_mat, name='lower_teeth')
    box('jaw', (-6.5, -42, -7.9), (13, 3, 0), mat=teeth_mat, name='lower_teeth_2')
    fbox('jaw', (-3.5, -36, -8.5), (7, 1, 4), name='chin')

    # ---------------- veil: upper drape behind the hood, long back veil, side drapes over the shoulders
    bone('veil', (0, -58, 9), parent='head', rot=(7, 0, 0), mat=veil_mat)
    box('veil', (-9, -58, 9), (18, 21, 2), name='veil_hi')
    bone('veil_lower', (0, -41, 7.5), parent='chest', rot=(-6, 0, 0), mat=veil_mat)
    box('veil_lower', (-8.5, -41, 7.5), (17, 40, 1), name='veil_lo')
    for side, sx in (('right', -1), ('left', 1)):
        vb = f'veil_{side}'
        bone(vb, (9.5 * sx, -50, 2), parent='chest', rot=(0, 0, -22 * sx), mat=veil_mat)
        box(vb, (9.5 * sx - (2 if sx > 0 else 5), -50, -1.5), (7, 31, 7), name='veil_side')

    # ---------------- arms: long, hanging slightly away from the bodice; bell sleeves of three flared panels
    for side, sx in (('right', -1), ('left', 1)):
        ax = 10 * sx
        ay = -35 if side == 'right' else -36
        az = 0.5
        arm, fa, hand = f'{side}_arm', f'{side}_forearm', f'{side}_hand'
        bone(arm, (ax, ay, az), parent='chest', rot=(-4, 0, (-8 if sx < 0 else -6) * sx), mat=wool_mat)
        box(arm, (ax - 3, ay - 2.5, az - 3), (6, 5, 6), name='shoulder')
        box(arm, (ax - 2.5, ay + 1.5, az - 2.5), (5, 11, 5))
        ey = ay + 12
        bone(fa, (ax, ey, az), parent=arm, rot=(-8, 0, -2 * sx), mat=wool_mat)
        box(fa, (ax - 3, ey - 1.5, az - 3), (6, 6, 6), name='core')
        box(fa, (ax - sx * 3.25 - 0.5, ey + 2, az - 3.5), (1, 10, 7), name=f'slv_i{side[0]}')
        b1 = f'{side}_sleeve_front'
        bone(b1, (ax, ey + 2, az - 3), parent=fa, rot=(-24, 0, 0), mat=wool_mat)
        box(b1, (ax - 4.5, ey + 2, az - 4), (9, 13, 1), name='slv_f')
        b2 = f'{side}_sleeve_back'
        bone(b2, (ax, ey + 2, az + 3), parent=fa, rot=(22, 0, 0), mat=wool_mat)
        box(b2, (ax - 4.5, ey + 2, az + 3), (9, 15, 1), name='slv_b')
        b3 = f'{side}_sleeve_outer'
        bone(b3, (ax + 3 * sx, ey + 2, az), parent=fa, rot=(0, 0, -24 * sx), mat=wool_mat)
        box(b3, (ax + 3 * sx - (1 if sx < 0 else 0), ey + 2, az - 4.5), (1, 14, 9), name='slv_o' + side[0])
        # hand emerges from the black inside of the bell
        hy = ey + 12
        hrot = (8, 10, 5) if sx < 0 else (6, -14, -6)
        bone(hand, (ax, hy, az), parent=fa, rot=hrot, mat=hand_mat)
        box(hand, (ax - 3, hy - 1, az - 1), (6, 7, 2), name='palm')
        flen = [(7, 6), (9, 7), (8, 7), (6, 5)]
        offs = [-2.4, -0.8, 0.8, 2.4]
        for f in range(4):
            fb = f'{side}_finger_{f + 1}'
            cx = ax + offs[f] * (-sx)
            fy = hy + 6
            l1, l2 = flen[f]
            bone(fb, (cx, fy, az), parent=hand, rot=(4 + f * 2, 0, (f - 1.5) * 6 * sx), mat=hand_mat)
            box(fb, (cx - 0.5, fy - 0.5, az - 0.5), (1, 1, 1), inflate=0.45, name='knuckle')
            box(fb, (cx - 0.5, fy, az - 0.5), (1, l1, 1), inflate=0.32, name='phal')
            tb = fb + '_tip'
            bone(tb, (cx, fy + l1, az), parent=fb, rot=(10 + f * 3, 0, 0), mat=hand_mat)
            box(tb, (cx - 0.5, fy + l1 - 0.5, az - 0.5), (1, 1, 1), inflate=0.38, name='knuckle')
            box(tb, (cx - 0.5, fy + l1, az - 0.5), (1, l2, 1), inflate=0.2, name='phal')
            box(tb, (cx - 0.5, fy + l1 + l2 - 0.2, az - 0.8), (1, 5, 1), mat=claw_mat, inflate=0.12)
        th = f'{side}_thumb'
        tx = ax - 2.6 * sx
        bone(th, (tx, hy + 1, az - 1), parent=hand, rot=(-28, 0, -22 * sx), mat=hand_mat)
        box(th, (tx - 0.5, hy + 0.5, az - 1.5), (1, 1, 1), inflate=0.42, name='knuckle')
        box(th, (tx - 0.5, hy + 1, az - 1.5), (1, 6, 1), inflate=0.3, name='phal')
        box(th, (tx - 0.5, hy + 6.8, az - 1.7), (1, 4, 1), mat=claw_mat, inflate=0.12)

    m = Model('monja', 256, 176, r.roots)
    m.scale = 0.5
    return m


def _hands(splay, curl, thumb=0.0):
    """Finger spread (z, outward) and knuckle curl of the tips for both hands."""
    out = {}
    for side, sx in (('right', -1), ('left', 1)):
        for f in range(4):
            out[f'{side}_finger_{f + 1}'] = (0, 0, (f - 1.5) / 1.5 * splay * sx, 0, 0, 0)
            out[f'{side}_finger_{f + 1}_tip'] = (curl, 0, 0, 0, 0, 0)
        out[f'{side}_thumb'] = (0, 0, thumb * sx, 0, 0, 0)
    return out


POSES = {
    # the jumpscare: rises and lunges, arms flung up and out so the claws frame the face, head snapped
    # sideways, jaw unhinged
    'attack': {
        'body': (0.06, 0, 0, 0, -1.5, -2.0),
        'chest': (-0.1, 0, 0, 0, 0, 0),
        'neck': (-0.05, 0, 0, 0, 0, 0),
        'head': (-0.1, 0, 0.3, 0, 0, 0),
        'jaw': (0.6, 0, 0, 0, 1.0, -0.5),
        'veil': (0.25, 0, 0, 0, 0, 0),
        'veil_lower': (0.2, 0, 0, 0, 0, 0),
        'veil_right': (0, 0, 0.25, 0, 0, 0),
        'veil_left': (0, 0, -0.25, 0, 0, 0),
        'right_arm': (-2.6, 0, 0.6, 0, 0, 0),
        'left_arm': (-2.4, 0, -0.7, 0, 0, 0),
        'right_forearm': (-0.3, 0, 0, 0, 0, 0),
        'left_forearm': (-0.5, 0, 0, 0, 0, 0),
        'right_sleeve_front': (-0.2, 0, 0, 0, 0, 0),
        'left_sleeve_front': (-0.2, 0, 0, 0, 0, 0),
        'right_sleeve_back': (0.35, 0, 0, 0, 0, 0),
        'left_sleeve_back': (0.35, 0, 0, 0, 0, 0),
        'right_hand': (0.5, 0, 0, 0, 0, 0),
        'left_hand': (0.5, 0, 0, 0, 0, 0),
        **_hands(0.3, 0.5, 0.3),
    },
    # head thrown back, jaw at max, arms out and back, fingers splayed: the shriek
    'scream': {
        'chest': (-0.2, 0, 0, 0, 0, 0),
        'neck': (-0.15, 0, 0, 0, 0, 0),
        'head': (-0.4, 0, 0.12, 0, 0, 0),
        'jaw': (0.8, 0, 0, 0, 1.0, -0.5),
        'veil': (0.3, 0, 0, 0, 0, 0),
        'veil_lower': (0.25, 0, 0, 0, 0, 0),
        'veil_right': (0, 0, 0.3, 0, 0, 0),
        'veil_left': (0, 0, -0.3, 0, 0, 0),
        'right_arm': (0.3, 0, 0.45, 0, 0, 0),
        'left_arm': (0.3, 0, -0.45, 0, 0, 0),
        'right_forearm': (0.15, 0, 0, 0, 0, 0),
        'left_forearm': (0.3, 0, 0, 0, 0, 0),
        'right_hand': (-0.6, 0, 0, 0, 0, 0),
        'left_hand': (-0.7, 0, 0, 0, 0, 0),
        **_hands(0.4, -0.2, 0.4),
    },
    # holy light / fire: cowers, forearms crossed over the face, head ducked and turned away
    'burn': {
        'body': (0, 0, 0, 0, 2.0, 0),
        'chest': (0.4, 0, 0, 0, 0, 0),
        'head': (0.35, 0.35, 0, 0, 0, 0),
        'jaw': (0.45, 0, 0, 0, 0, 0),
        'veil': (-0.2, 0, 0, 0, 0, 0),
        'veil_right': (0, 0, -0.15, 0, 0, 0),
        'veil_left': (0, 0, 0.15, 0, 0, 0),
        'right_arm': (-2.3, -0.3, -0.3, 0, 0, 0),
        'left_arm': (-2.1, 0.3, 0.3, 0, 0, 0),
        'right_forearm': (-0.9, 0, 0, 0, 0, 0),
        'left_forearm': (-0.9, 0, 0, 0, 0, 0),
        'right_hand': (-0.3, 0, 0, 0, 0, 0),
        'left_hand': (-0.4, 0, 0, 0, 0, 0),
        **_hands(0.1, 0.8, -0.2),
    },
    # chase: glides with the right arm reaching for the player, fingers spread, head pushed forward
    'reach': {
        'body': (0.12, 0, 0, 0, -1.0, 0),
        'chest': (-0.08, 0, 0, 0, 0, 0),
        'head': (0.05, 0, -0.25, 0, 0, 0),
        'jaw': (0.25, 0, 0, 0, 0, 0),
        'veil_lower': (0.35, 0, 0, 0, 0, 0),
        'right_arm': (-1.35, 0, 0.1, 0, 0, 0),
        'left_arm': (0.15, 0, 0, 0, 0, 0),
        'right_forearm': (-0.15, 0, 0, 0, 0, 0),
        'right_sleeve_back': (0.4, 0, 0, 0, 0, 0),
        'right_hand': (0.3, 0, 0, 0, 0, 0),
        **_hands(0.35, 0.35, 0.3),
    },
}

ANIM_NOTES = """
Sor Agonia -- animation contract.  Angles in radians, ADDED to the rest pose; offsets (dx, dy, dz) in model
texels at 2x density (inside scale_root: 2 texels = 1 vanilla pixel).  t = ageInTicks, s = glide speed 0..1.
She never walks: no legs, the robe glides.  Everything moves slow and smooth EXCEPT the head snaps, which are
instant (1-2 ticks) -- that contrast is what makes the clips scary.  Poses: attack, scream, burn, reach.

ROOT
* body -- root at the waist (pivot y -20): leather cincture + buckle, hips.  HOVER BOB: dy = -1.5 +
  sin(t*0.08)*1.2 (hem stays 1-3 texels above the ground).  Idle yaw drift sin(t*0.02)*0.05.  Glide/chase: xRot
  +0.12*s (leans in), side roll sin(t*0.15)*0.04, NO step bob.  Attack (0.06, 0, 0, 0, -1.5, -2): rises and
  lunges.  Scream dy -1.  Burn dy +2 (sinks, recoils) + shiver zRot sin(t*2.1)*0.03.  Reach (0.12, .., dy -1).

ROBE -- 8 flared torn panels, children of body, pivots inside the hips (y -17), rest flare -11..-15 deg on x,
yawed 45 deg apart; k = 0..7 in this order:
* robe_front, robe_front_right, robe_right, robe_back_right, robe_back, robe_back_left, robe_left,
  robe_front_left -- each sways on its own local x OUT OF PHASE: xRot += sin(t*0.09 + k*0.8)*0.07, so the hem
  ripples like cloth under water.  Glide/chase: back panels (k 3..5) trail +0.25*s, front panels (k 0,1,7)
  press back -0.12*s, side panels (k 2,6) flutter sin(t*0.4 + k)*0.1*s.  Attack: all flare out an extra -0.15.
  Scream -0.2 + tremble sin(t*1.7 + k)*0.04.  Burn: collapse inward +0.1 with twitches.
* scapular_front / scapular_back -- the long scapular strips over the robe (chest piece lives on chest).  Follow
  robe_front / robe_back with a 4-tick lag: xRot += sin(t*0.09 - 0.4)*0.06; chase: front -0.1*s, back +0.3*s.
* rosary -- bone beads + inverted wooden cross hanging from the front-left of the cincture to the knee.
  Pendulum lagging the body ~8 ticks: zRot = sin(t*0.07 - 0.6)*0.12, xRot = -bodyXRot*0.8 + 0.3*s.  Attack
  flicks forward -0.4 then settles.  Burn rattles zRot sin(t*2.6)*0.08.

TORSO
* chest -- tapered bodice (ribs 14 -> 10 -> waist 8), cloth bulging over the belt, sloped shoulder yoke, hump with
  two vertebrae, scapular chest piece and the off-white guimpe (shoulder bib).  Rest: hunched 8 deg, right
  shoulder dropped.  Idle breathing xRot sin(t*0.06)*0.03 and every ~8 s a crack-twist (zRot snaps +0.12 for 3
  ticks, eases back).  Glide/chase -0.08.  Attack -0.1.  Scream -0.2.  Burn +0.4 (folds over).
* cross -- inverted wooden cross on its iron chain.  Pendulum lagging the chest ~10 ticks: xRot = -chestXRot*0.7
  + sin(t*0.07 - 1.0)*0.06, zRot = sin(t*0.05)*0.08.  Chase +0.3*s.  Burn jitters zRot sin(t*3)*0.05.
* neck -- short neck hidden in the linen wimple.  Idle creak yRot sin(t*0.03)*0.08.  Attack -0.05, scream -0.15.
  'Owl turn': when the player looks away, neck yRot may go to +-1.4 over 40 ticks.
* head -- skull + face cubes, coif (band with barbed wire, wimple, chin wrap / gorget), black hood; FOCUS bone
  and jumpscare portrait (its cubes reach y -32 so the dropped jaw stays in frame).  Follows look yaw/pitch
  (clamp yaw +-0.9, neck adds the rest).  SIGNATURE: snap tilts -- every 60-120 ticks zRot jumps +-0.6..1.57 in
  1-2 ticks, holds 20-40, drifts back over 30.  Idle micro-twitch zRot += 0.15 for 1 tick (3 %/tick).  Attack
  (-0.1, 0, 0.3) snapped instantly.  Scream (-0.4, 0, 0.12).  Burn (0.35, 0.35, 0).  Reach (0.05, 0, -0.25).
* jaw -- mandible with the black lower lip, lower needle teeth (two rows), dark red tongue on top and the
  pointed chin; hinge at (0, -40, -4) inside the wimple.  Idle: slack tremble xRot = 0.05 + sin(t*0.9)*0.02,
  slowly opening to 0.35 while she stares at the player.  Glide 0.15.  Attack (0.6, 0, 0, 0, +1, -0.5): unhinges
  down onto the black gullet.  Scream (0.8, 0, 0, 0, +1, -0.5) + shiver sin(t*2.5)*0.04.  Burn 0.45 (gasping).
* arch_right / arch_left -- linen slabs (rest zRot -+34 deg) that cut the coif opening into a gothic pointed
  arch.  STATIC (never animate; they are part of the coif).
* hood_right / hood_left -- black chamfer slabs (rest zRot -+45 deg) rounding the hood and coif corners.
  Static; in scream they may lift zRot -+0.08 with the veil.
* hood_peak -- the soft gathered fold on the crown.  Static; tiny flutter sin(t*0.05)*0.03 in chase.
* nail_right / nail_left -- two short rusted nails driven into the coif at the temples (blood runs from them
  down the wimple).  Static.  Burn: jitter yRot sin(t*3.3)*0.06 as if they glow.

VEIL
* veil -- upper veil block falling from the back of the hood to the nape (child of head).  Trails opposite the
  head: xRot = -headXRot*0.4 + 0.25*s; idle sway sin(t*0.05)*0.04.  Attack +0.25, scream +0.3, burn -0.2.
* veil_lower -- long black back veil from the nape to the knee (child of chest), torn V bottom and a slit the
  vertebrae push through.  Idle xRot sin(t*0.05 - 0.5)*0.05.  Chase trails +0.35*s with ripple
  sin(t*0.3)*0.05*s.  Attack +0.2, scream +0.25, reach +0.35.
* veil_right / veil_left -- the wide side drapes falling from the hood over the shoulders and flaring 22 deg to
  elbow level: they make the black A silhouette.  Flutter out of phase: zRot += sin(t*0.07 + side)*0.05; chase
  xRot +0.3*s (trail).  Attack opens them +0.25 / -0.25 (a gust), scream +0.3 / -0.3, burn closes them
  -0.15 / +0.15 around her.

ARMS -- right_* is -X (viewer's left).  Rest: long arms hanging slightly away from the bodice inside the veil
drapes, right shoulder lower, hands dangling beside the robe below the knees.
* right_arm / left_arm -- shoulder cap + upper sleeve; pivots at the shoulders.  Idle sway xRot
  sin(t*0.05 + side)*0.04.  Glide drift back +0.15*s.  Chase: reach forward -1.35*s (see 'reach').  Attack
  right (-2.6, 0, 0.6) / left (-2.4, 0, -0.7): flung up and out so the claws frame the face.  Scream
  (0.3, 0, +-0.45).  Burn right (-2.3, -0.3, -0.3) / left (-2.1, 0.3, 0.3) so the forearms cross over the face.
* right_forearm / left_forearm -- elbow: sleeve core, inner side plate, carries the bell panels and the hand.
  Idle bob sin(t*0.06 + side)*0.05.  Attack -0.3 / -0.5, burn -0.9 (forearms fold across the face).
* {side}_sleeve_front / _sleeve_back / _sleeve_outer -- the three flared cloth panels of the bell sleeve (rest
  flare -24 / +22 / 24 deg outward), pitch black inside.  Pure secondary motion: lag the forearm ~6 ticks +
  flutter sin(t*0.2 + panel)*0.08; chase: back panel +0.35*s, front -0.1*s.  Attack: back panel +0.35 (blown
  open), front -0.2.
* right_hand / left_hand -- long grey palm emerging from the black cuff.  Idle limp curl sin(t*0.04)*0.06.
  Attack +0.5 (wrists bend so the claws rake forward), scream -0.6 / -0.7, burn -0.3 / -0.4 (palms over the
  face), reach +0.3.
* {side}_finger_1..4 (1 = outer, 4 = inner) -- knuckle + first phalanx, splayed on z.  Idle: ONE finger at a
  time twitches (every 25-40 ticks, xRot +0.35 for 2 ticks, ease back: spider tapping).  Attack splay zRot
  +-0.3, scream +-0.4, reach +-0.35, burn +-0.1.
* {side}_finger_1..4_tip -- joint knuckle + second phalanx + horn-tipped claw; follows its finger with a 3-tick
  lag.  Attack +0.5 (hook), scream -0.2, burn +0.8 (clench), reach +0.35.
* right_thumb / left_thumb -- thumb with knuckle and claw, curled inward.  Attack opens zRot +-0.3, scream
  +-0.4, burn -+0.2.

LAYERING
idle = hover bob + breathing + robe ripple + veil sway + random head snaps + finger taps + jaw tremble.
glide/chase = idle + lean + trailing cloth (back robe panels, scapular_back, veils, sleeve panels) * speed; blend
toward POSE_REACH while the player is within 6 blocks.  attack = blend 4 ticks into POSE_ATTACK, hold 6,
release over 10.  scream = POSE_SCREAM during the shriek.  burn = POSE_BURN while in light / holy water, with
jitter on chest, hands, nails and cross.
"""
