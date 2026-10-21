"""Sor Agonia -- the demonic nun of the Convento de Santa Ines (DEAD LINE).

Authored at 2x texel density (model.scale = 0.5).  +Y down, ground y = 24, faces -Z.  Centred on x = 0, z = 0.
Height 2.74 blocks (hood crown y -62.4 -> hem y 21.9, root lifted 3 texels).  58 bones, 164 cubes, 256 x 208.

Design (round 4)
----------------
Silhouette: an HOURGLASS in black.  A tapered hood (stepped crown, side panels flaring outward and sweeping back,
a rear drape streaming down from the crown) pours onto two shoulder drapes, so the top reads as a bell; under it
the white guimpe sits on the shoulders, the bodice pinches to an 8-texel waist cinched by a leather cincture
(negative space between the waist and the long arms on both sides), the hips widen again and a long robe of eight
torn panels flares to a shredded hem twice as wide as the shoulders.  In profile she is a hooded vulture: hunched
upper back with vertebrae tearing through the veil, the neck jutting forward and the head thrust out in front of
the chest, the veil streaming back from the crown.  Long arms end in bell sleeves (black inside) and grey bony
hands with knuckled fingers and horn claws below the knees; a brass hand-bell hangs from her left hand, a bunch of
five keys from the right of the cincture, a bone rosary with an inverted cross from the left, an inverted wooden
cross on an iron chain over the guimpe.

Face: a GREY-GREEN corpse face sunk inside a bright white coif frame (value gap ~ 60/255) with a near-black contact
shadow running all the way round the opening.  The opening is a stepped oval that WIDENS downwards (12 at the eyes,
14 at the cheekbones) and the lower face breaks out of it: a jutting muzzle and an unhinged jaw 16 texels wide, so
the lipless grin is wider than the face; its corners curl up and tear into the cheeks.  Heavy V brow over deep
sockets with AO rings and burning yellow-orange pupils at different heights (emissive 'eyes' layer), a rotted
nasal cavity, protruding cheekbones over hollow cheeks.  Two rows of crooked needle teeth top and bottom interlock
over a black gullet so the mouth reads as a band of needles even when closed; the jaw drops onto the black throat
and a dark tongue.  Deliberate grey crack networks (forehead -> left brow -> socket, right mouth corner -> right
socket, chin) with pale broken lips, black veins creeping from the temples and down the jaw from the mouth corners,
barbed wire biting into the coif band with blood running down the forehead.

Secret: a hidden plane 'face_crack' (inside the skull at rest) slides out over her left eye in the 'reveal' pose: a
vertical crack showing a strip of warm human skin, a moist brown human eye and a tear -- Clara is still in there.
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
# starched linen: cool blue-grey shadows -> warm bright off-white (the brightest thing on her)
LINEN = [hx('#15161d'), hx('#2b2e3a'), hx('#474b5a'), hx('#6c7183'), hx('#979cab'), hx('#c1c2bf'),
         hx('#dcd8ca'), hx('#eeeadc'), hx('#f8f5ea')]
DIRTY = hx('#a99467')
# corpse skin: grey-GREEN, mid-valued -- clearly darker than the linen frame
SKIN = [hx('#0b0d0c'), hx('#181c19'), hx('#272d28'), hx('#384039'), hx('#4d564c'), hx('#646e60'),
        hx('#7c8676'), hx('#959e8c'), hx('#aeb4a2')]
HANDC = [hx('#111115'), hx('#212127'), hx('#36363e'), hx('#4f4f58'), hx('#6c6b74'), hx('#8c8a92'),
         hx('#aeabb0'), hx('#cfccce')]
VEIN = hx('#12081a')
VEIN2 = hx('#3a2c44')
CRACK = hx('#0e110f')
CRACKL = hx('#b4bba5')
# claws: dark red-black root -> horn -> yellowed bright tip (reads against the black habit)
CLAW = [hx('#0e0304'), hx('#260709'), hx('#3e1211'), hx('#5e2c1e'), hx('#8a5a3a'), hx('#b89668'),
        hx('#e6d6aa')]
EMBER = [hx('#2a0300'), hx('#6e1200'), hx('#c23a00'), hx('#ff7a0a'), hx('#ffc23a'), hx('#fff3b8')]
MOUTH = [hx('#020102'), hx('#0c0305'), hx('#1e070c'), hx('#3a0f16'), hx('#5c1d28'), hx('#86343f')]
GUM = [hx('#1c0509'), hx('#3d0d15'), hx('#5e1a24'), hx('#7e2b34')]
TEETH = [hx('#2a241b'), hx('#4c4333'), hx('#7a6d54'), hx('#a89c7c'), hx('#cfc7ad'), hx('#ece6d2'),
         hx('#fbf8ee')]
WOOD = [hx('#170d07'), hx('#2a190d'), hx('#432914'), hx('#5f3d1f'), hx('#7c542c'), hx('#9a6e3c'),
        hx('#c4955c'), hx('#e0b47a')]
IRON = [hx('#0f0f12'), hx('#212126'), hx('#38383f'), hx('#55555e'), hx('#7a7a84'), hx('#a2a2ac')]
RUST = hx('#5a2a12')
BRASS = [hx('#1e1204'), hx('#3e2808'), hx('#68460f'), hx('#94691a'), hx('#c0922c'), hx('#e2bb52'),
         hx('#fbe7a0')]
LEATHER = [hx('#0a0605'), hx('#170e0b'), hx('#251812'), hx('#36241a'), hx('#4a3224'), hx('#5e4130')]
BONE = [hx('#3a3226'), hx('#5c5140'), hx('#837559'), hx('#a89878'), hx('#c9bb9a'), hx('#e2d8bd'), hx('#f4eedc')]
BLOOD = [hx('#160003'), hx('#330207'), hx('#55050c'), hx('#7a0a13'), hx('#9e141c')]
DRIED = hx('#3b120c')
DUST = hx('#4a4552')
WAX = [hx('#6e6650'), hx('#b8ae8a'), hx('#ddd3b0')]
SCORCH = [hx('#0b0503'), hx('#24110a'), hx('#4a2410'), hx('#7a3a12')]
SMOKE = [hx('#2a2830'), hx('#45434d'), hx('#68666f'), hx('#8f8d95')]
# Clara: warm living skin, a brown human eye
WARM = [hx('#3a1a14'), hx('#6e3a2c'), hx('#a8664e'), hx('#cf9474'), hx('#e8b896')]


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


def none_mat(ctx):
    return None


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
    if t == 'waist' and f in ('west', 'east'):
        v -= 0.1                                            # the pinch: sides of the waist fall into shadow
    if t == 'ribs' and f == 'front' and ctx.j >= ctx.h - 1:
        v -= 0.1
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
            if ly > h * 0.62 and s > 0.72 and f != 'top':
                c = mix(c, SCORCH[1], 0.75)                 # scorch blotches: holy fire has touched her
                if s > 0.8 and hash3(ctx.i, ctx.j, k, 22) > 0.8:
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
    if t == 'veil_lo' and f in ('front', 'back') and h > 10 and abs(lx - w / 2) < 1.0 and 1.5 < ly < 10:
        return None                                         # torn slit: the vertebrae tear through here
    if t == 'veil_tail' and f != 'top':
        if f == 'bottom':
            return None
        col = int(lx) if f in ('front', 'back') else int(lz)
        if ly > h - 0.5 - abs(lx - w / 2) * 1.6 - hash3(col, sd, 0, 62) * 2.5:
            return None                                     # torn point of the veil
    if t in ('veil_side', 'veil_hi', 'hood_side') and f != 'top':
        if f == 'bottom':
            return None
        col = int(lx) if f in ('front', 'back') else int(lz)
        if t == 'veil_side':
            cut = hem_cut(col * 2, 31 + sd % 7, h) - (col * 0.25)
        elif t == 'hood_side':
            cut = h + 1 if f in ('front', 'back') else hem_cut(col * 2, 17 + sd % 5, h) - max(0, col - 8) * 0.6
        else:
            cut = hem_cut(col, 5, h)
        if ly > cut:
            return None
    v = 0.5 + face_light(ctx) * 1.1
    if f in ('front', 'back', 'west', 'east'):
        v += fold_shade(across(ctx), ly, sd % 31, 7.0) * 0.8
    if f == 'top' and t in ('crown', 'dome'):
        ang = math.atan2(ctx.z - 0.0, ctx.x)
        ph = (ang * 7 / math.pi + vnoise(ctx.x * 0.2, ctx.z * 0.2, 3, 5) * 0.8) % 1.0
        v += 0.1 if ph < 0.2 else (-0.12 if ph > 0.8 else 0.0)   # radial folds gathered at the crown
    if t == 'hood_side' and ((f == 'east' and ctx.x < 0) or (f == 'west' and ctx.x > 0)):
        v -= 0.25                                           # inside of the hood, around the coif
    if t == 'hood_in' and f == 'front':
        v -= 0.08
    if t == 'brim' and f == 'bottom':
        v -= 0.2
    if t == 'hood_side' and f == 'front':
        v += 0.12                                           # turned-back front edge of the hood catches light
    if edge(ctx) == 0 and f != 'top' and not is_plane(ctx):
        v -= 0.07
    return pick(VEILC, v)


INNER = {'coif_r': ('east', 'bottom'), 'coif_l': ('west', 'bottom'), 'band': ('bottom',)}


def linen_mat(ctx):
    """Starched coif / wimple / guimpe: bright off-white with cool shadows; every face that looks INTO the face
    opening is in deep shadow, so the face is ringed by a dark line."""
    if is_plane(ctx) and ctx.face == 'back':
        return None
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    t = tag(ctx)
    f = ctx.face
    if t in INNER and f in INNER[t]:
        return pick(LINEN, 0.06 + (0.1 if lz > 3 else 0.0))
    if t == 'band' and (f == 'back' or (f in ('west', 'east') and lz > 6)):
        return pick(VEILC, 0.3)                             # the back of the band is under the hood
    v = 0.86 + face_light(ctx) * 0.8
    if f in ('west', 'east'):
        v -= 0.14
    elif f == 'back':
        v -= 0.3
    if t == 'gorget':
        v -= 0.22 if w > 10 else 0.32                       # under the jaw: in its shadow
    if t == 'neckl':
        v -= 0.3
    if t == 'wimple_lo' and f == 'front':
        v -= 0.05
        if abs(lx - w / 2) < 9.0:
            v = 0.1                                         # contact shadow right beside the jaw / muzzle
    if t in ('coif_r', 'coif_l') and f == 'front' and ctx.i % 3 == 1:
        v -= 0.04                                           # faint starched pleats
    if t == 'bib' and f == 'front':
        cx = abs(lx - w / 2)
        hw = w / 2 - max(0.0, ly - (h - 3.5)) ** 1.5 * 1.3
        if cx > hw:
            return None                                     # rounded guimpe bottom
        if ly < 2.0 and cx < 4.5:
            v -= 0.22                                       # shadow under the chin
    c = pick(LINEN, v)
    inner_edge = (t == 'coif_r' and f == 'front' and ctx.i == ctx.w - 1) or \
                 (t == 'coif_l' and f == 'front' and ctx.i == 0) or (t == 'band' and f == 'front' and ctx.j == ctx.h - 1)
    if edge(ctx) == 0 and f != 'top' and not inner_edge and t != 'wimple_lo':
        c = mix(c, DIRTY, 0.3)
    if t == 'bib':
        soak = (ly - (h - 3.0)) / 3.0
        if soak > 0 and f in ('front', 'west', 'east'):
            c = mix(c, BLOOD[2], min(0.85, soak * 0.9))     # blood-soaked lower edge
        if f == 'front' and 0.4 < abs(lx - w / 2) < 5.5 and hash3(int(lx), 0, 0, 41) > 0.55:
            ln = 1 + hash3(int(lx), 1, 0, 42) * 4.5
            if ly < ln:
                c = BLOOD[3] if ly < ln - 1 else BLOOD[4]   # drips running down from the mouth
    if t == 'gorget' and f == 'front' and w > 10:
        drips = {3: 3, 4: 2, 8: 1, 10: 3, 11: 1}           # three deliberate runs of blood from the jaw
        if int(lx) in drips and ly < drips[int(lx)]:
            c = BLOOD[3] if ly < drips[int(lx)] - 1 else BLOOD[4]
    if t in ('coif_r', 'coif_l') and f == 'front' and h >= 5 and ctx.i == (1 if t == 'coif_r' else ctx.w - 2):
        if ly < 2.2:
            c = BLOOD[3] if ly < 1.2 else BLOOD[2]          # a short run of blood from the barbs at the temples
    return c


# ------------------------------------------------------------------ flesh
def skin_mat(ctx):
    """Grey-green corpse skin (the front details are hand-placed decals, see FACE)."""
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    f = ctx.face
    t = tag(ctx)
    if f == 'top':
        return pick(SKIN, 0.55 if t in ('brow', 'cheek', 'muzzle') else 0.4)
    if f == 'bottom':
        if t in ('skull', 'muzzle'):
            return pick(MOUTH, 0.2 + (1 - abs(lx - w / 2) / (w / 2)) * 0.25)   # wet palate in the open mouth
        if t in ('brow', 'cheek'):
            return SKIN[1]                                  # overhang shadow
        return pick(SKIN, 0.22)
    v = 0.6 + face_light(ctx) * 0.5
    if f in ('west', 'east'):
        v -= 0.12 + (lz / max(1.0, d)) * 0.12
    elif f == 'back':
        v -= 0.4
    if edge(ctx) == 0 and f in ('west', 'east') and min(ctx.w, ctx.h) > 2:
        v -= 0.08
    c = pick(SKIN, v)
    if f in ('west', 'east') and t in ('jaw', 'chin', 'muzzle'):
        # black veins crawling back along the jaw line from the mouth corners
        zz = lz if f == 'east' else d - lz
        if abs(ly - (1.0 + zz * 0.35 + math.sin(zz * 1.3) * 0.6)) < 0.5 and zz < 6:
            c = VEIN
        elif abs(ly - (1.0 + zz * 0.35 + math.sin(zz * 1.3) * 0.6)) < 1.0 and zz < 5:
            c = mix(c, VEIN2, 0.6)
    return c


def throat_mat(ctx):
    """Pure black gullet; only the rim warms to a dark wet red."""
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    if ctx.face == 'front':
        cx = abs(lx - w / 2) / (w / 2)
        return pick(MOUTH, max(0.0, cx - 0.6) * 0.8 + max(0.0, ly - 5) * 0.06)
    return pick(MOUTH, 0.05 + (1 - lz / max(1, d)) * 0.25)


def jaw_mat(ctx):
    """Mandible: skin outside, gum rim + dark red tongue on top (seen when the jaw drops)."""
    if ctx.face == 'top':
        lx, ly, lz = local(ctx)
        w, h, d = ctx.cube.size
        cx = abs(lx - w / 2)
        if lz < 1.0:
            return pick(GUM, 0.5)
        if cx < 3.6 and lz < d - 1.5:
            return pick(MOUTH, 0.6 - cx * 0.06 + (0.08 if int(lz) % 2 else 0))    # dark red tongue
        return pick(MOUTH, 0.08)
    if ctx.face == 'back':
        return pick(MOUTH, 0.1)
    return skin_mat(ctx)


# Teeth: crooked NEEDLES.  Upper rows hang from the gum (row 0 = root), lower rows rise from the jaw (last row =
# root).  'T' front needle, 't' darker back-row needle, 'R' rotten tooth, 'F' fang.  The lower row interlocks with
# the gaps of the upper row, the back rows fill what is left, so at rest the mouth is a dense band of needles with
# only slivers of black between them; open, the rows separate into two jagged traps.
UPPER_TEETH = [            # 16 wide, x -8..8, y -45..-41 (z -9.4); row 0 = root at the gum
    ".T..T.T..T..T.T.",
    ".T..T.T..T..T.T.",
    ".T..T....T..T...",
    ".F.......F......",
]
UPPER_TEETH_2 = [          # 14 wide, x -7..7 (z -9.1): dim back row seen only through the gaps
    "..t....t..t...",
    "..t.......t...",
    "..............",
]
LOWER_TEETH = [            # 16 wide, x -8..8, y -44..-41 (z -8.8); last row = root on the jaw
    ".......F........",
    "..T....F....T...",
    "..T..T.F..T.T.T.",
]
LOWER_TEETH_2 = [          # 14 wide, x -7..7 (z -8.6)
    "..............",
    "....t.....t...",
    ".t..t..t..t..t",
]
TEETH_ROWS = {'upper_teeth': UPPER_TEETH, 'upper_teeth_2': UPPER_TEETH_2,
              'lower_teeth': LOWER_TEETH, 'lower_teeth_2': LOWER_TEETH_2}


def teeth_mat(ctx):
    """Needle teeth: near-black root sunk in the gum, ivory shaft, a bright glassy point.  Back rows dim."""
    if ctx.face != 'front':
        return None
    t = tag(ctx)
    rows = TEETH_ROWS[t]
    i, j = ctx.i, ctx.j
    ch = rows[j][i] if j < len(rows) and i < len(rows[j]) else '.'
    if ch == '.':
        return None
    up = t.startswith('upper')
    step = 1 if up else -1
    k = j if up else len(rows) - 1 - j                      # distance from the root
    jn = j + step
    tip = not (0 <= jn < len(rows)) or rows[jn][i] == '.'
    if ch == 't':
        return TEETH[3] if tip else mix(TEETH[1], GUM[0], 0.5)
    if tip:
        return TEETH[6] if (ch == 'F' or k >= 1) else TEETH[4]
    if k == 0:
        return mix(TEETH[2], GUM[1], 0.55)                  # root sunk in the dark gum
    c = TEETH[5] if ch == 'F' else TEETH[4]
    if hash3(i, j, 1 if up else 2, 33) > 0.85:
        c = TEETH[3]                                        # a yellowed one
    return c


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
    if t == 'palm' and ctx.face in ('front', 'back') and int(lx) in (2, 5) and 1 < ly < 6:
        c = mix(c, VEIN, 0.6)                               # black veins along the back of the hand
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


def brass_mat(ctx):
    """Tarnished brass hand-bell: bright specular stripe down the lit side, verdigris-dark rim."""
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    v = 0.5 + face_light(ctx) * 1.5
    if ctx.face in ('front', 'west') and ctx.i == 0:
        v += 0.32                                           # specular stripe
    if ctx.face in ('front', 'east', 'west', 'back') and ctx.j == ctx.h - 1:
        v -= 0.18
    if ctx.face == 'bottom':
        return BRASS[0]                                     # dark inside of the bell
    if hash3(ctx.i, ctx.j, cseed(ctx), 55) > 0.82:
        v -= 0.2
    return pick(BRASS, v)


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
# layered face cube by its x/y extent.  Column c <-> x in [c - 10, c - 9]; row r <-> y in [-60 + r, -59 + r].
# '.' leaves the cube's own material (linen for the coif pieces).
# Opening (skin): r6 x-5..5 | r7-r10 x-6..6 | r11-r12 x-7..7 | muzzle r13-14 and jaw r19-21 x-8..8 | chin r22
# x-5..5 | chin tip r23 x-2..2.  r15-r18 = the teeth band (own planes).
GX0, GY0 = -10, -60
FACE = [
    # 01234567890123456789
    "....................",   # r0  y-60  hood dome
    "....................",   # r1  y-59  hood crown
    "....................",   # r2  y-58
    "..z...z...z...z..z..",   # r3  y-57  coif band: barbed wire wrapped round the head, barbs up
    ".IiIIiHIiIIiHIiIIiI.",   # r4  y-56  the twisted wire
    ".B..z.B..z..dz..B...",   # r5  y-55  barbs down, blood where they bite
    ".....v676qB6c76.....",   # r6  y-54  brow ridge right under the band (protrudes): furrow, blood drip, crack
    "....kV764qb4cC6k....",   # r7  y-53  lit brow bulge; inner ends pulled down into the sockets (V frown)
    "....kKWyK64KKKKk....",   # r8  y-52  deep sockets: right pupil high
    "....qKyoK64KKWyq....",   # r9  y-51  left pupil low and outward
    "....qqKKq53qKyoq....",   # r10 y-50  rounded socket bottoms, the nose starts
    "..ckc87QqnnqQ786k...",   # r11 y-49  cheekbones (protrude) under an AO ring; the corner rip tears the linen
    "..kkc3245nn5423vk...",   # r12 y-48  hollow cheeks; the crack climbs from the mouth corner to the socket
    "..Kc567654456765vK..",   # r13 y-47  gaunt muzzle: the grin corners curl up and tear into the cheeks
    "..KKkgkkgkkgkkgkKK..",   # r14 y-46  lipless edge with gum specks
    "....................",   # r15 y-45  teeth band (planes)
    "....................",   # r16
    "....................",   # r17
    "....................",   # r18 y-42
    "..kkgkkgkkkgkkgkkk..",   # r19 y-41  lower lipless edge
    "..kv67876667c767vk..",   # r20 y-40  jaw: veins from the corners, crack to the chin
    "..k4v56655c5665v4k..",   # r21 y-39
    ".....k5677c765k.....",   # r22 y-38  chin
    "........k54k........",   # r23 y-37  pointed chin
]
assert all(len(r) == 20 for r in FACE), [len(r) for r in FACE]

FPAL = {
    '1': SKIN[1], '2': SKIN[2], '3': SKIN[3], '4': SKIN[4], '5': SKIN[5], '6': SKIN[6], '7': SKIN[7], '8': SKIN[8],
    'K': (2, 2, 3, 255), 'k': (10, 11, 12, 255), 'q': (22, 26, 23, 255), 'Q': (46, 52, 45, 255),
    'e': EMBER[1], 'r': EMBER[2], 'o': EMBER[3], 'y': EMBER[4], 'W': EMBER[5],
    'n': (3, 2, 3, 255),
    'c': CRACK, 'C': CRACKL, 'v': VEIN, 'V': VEIN2,
    'g': GUM[1], 'G': GUM[2],
    'B': BLOOD[2], 'b': BLOOD[4], 'd': DRIED,
    'i': IRON[1], 'I': IRON[3], 'H': IRON[5], 'z': IRON[2],
}
GLOWPAL = {'e': (150, 30, 0, 255), 'r': EMBER[2], 'o': EMBER[3], 'y': EMBER[4], 'W': EMBER[5],
           'h': (90, 16, 0, 255)}
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


# Clara's eye: a vertical crack over the left socket (x 0..6, y -55..-45).  Transparent outside the crack.
CRACK_ART = [
    "..kk..",   # y-55 (under the band)
    "..kCk.",   # y-54
    ".kSSk.",   # y-53
    "kRRRRk",   # y-52 upper lid
    "kwIhwk",   # y-51 sclera, brown iris with a wet highlight
    "kwPIwk",   # y-50 pupil
    "kRRtRk",   # y-49 red-rimmed lower lid, the tear wells up
    ".kStk.",   # y-48
    "..kt..",   # y-47
    "...t..",   # y-46 the tear runs out of the crack over the gum
]
CRACK_PAL = {'k': (8, 4, 4, 255), 'C': CRACKL, 'S': WARM[3], 's': WARM[4], 'R': WARM[1],
             'w': hx('#f4efe6'), 'I': hx('#7a4320'), 'P': (12, 6, 4, 255), 'h': hx('#ffffff'),
             't': hx('#bfe3f2')}

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

# five keys on an iron ring ('m' metal, 'h' highlight, 'd' dark); keys 3 and 5 are brass
KEY_PAL = {'m': IRON[3], 'h': IRON[5], 'd': IRON[1], 'r': RUST}
KEY_PAL_B = {'m': BRASS[3], 'h': BRASS[6], 'd': BRASS[1], 'r': BRASS[2]}
RING = [".hm.", "m..d", "h..d", ".dd."]
KEY_A = [".h.", "m.d", ".m.", ".m.", ".m.", ".mh", ".m.", ".md"]
KEY_B = ["hmd", "m.d", "dmd", ".m.", ".m.", ".mr", ".mm"]
KEY_C = [".m.", "h.d", ".m.", ".m.", ".m.", ".m.", ".mh", ".m.", ".hd"]
SMOKE_PAL = {'a': SMOKE[3], 'b': SMOKE[2], 'c': SMOKE[1], 'd': SMOKE[0]}
WISP_A = [
    "...a.",
    "..ab.",
    "..b..",
    ".bc..",
    ".b...",
    "..bc.",
    "...c.",
    "..cc.",
    ".cd..",
    ".d...",
]
WISP_B = [
    ".a...",
    ".ba..",
    "..b..",
    "..cb.",
    "...b.",
    "..bc.",
    ".bc..",
    ".cd..",
    "..d..",
    "..d..",
]


def art(rows, pal=None):
    return pixelart(rows, pal or FPAL, anchor='topleft')


DEFAULT_MAT = wool_mat
FOCUS = 'head'


class MonjaMeshModel(Model):
    """Model whose Java pose registry stays compilable with more than 10 poses: java.util.Map.of() has no overload
    past 10 pairs, so the POSES map is emitted with Map.ofEntries(Map.entry(...), ...) instead."""

    def pose_tables(self):
        text = super().pose_tables()
        if not self.poses or len(self.poses) <= 10:
            return text
        key = 'POSES = java.util.Map.of('
        entries = ', '.join('java.util.Map.entry("%s", POSE_%s)' % (n, n.upper()) for n in self.poses)
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if key in line:
                lines[i] = line[:line.index(key)] + 'POSES = java.util.Map.ofEntries(%s);' % entries
        return '\n'.join(lines)


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
    box('body', (-4.5, -22, -3.5), (9, 3, 7), mat=leather_mat, inflate=0.3)
    box('body', (-1, -22.5, -4.4), (2, 3, 1), mat=iron_mat)
    box('body', (-7, -19, -6), (14, 6, 12), name='hips')

    # ---------------- robe: eight flared torn panels, tops tucked inside the hips; hem floats ~1-2 texels up
    flare = [-14, -17, -13, -16, -14, -16, -13, -17]
    lens = [44, 44, 43, 44, 44, 44, 43, 44]
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
    bone('scapular_front', (0, -19, -6.6), parent='body', rot=(-13, 2, 0), mat=wool_mat)
    box('scapular_front', (-4, -19, -7.6), (8, 44, 1), name='scap')
    bone('scapular_back', (0, -19, 6.6), parent='body', rot=(14, -2, 0), mat=wool_mat)
    box('scapular_back', (-4, -19, 6.6), (8, 42, 1), name='scap')

    # ---------------- rosary of bone beads hanging to the knee from the front-left of the cincture
    bone('rosary', (3.5, -20.5, -6.8), parent='body', rot=(-17, 0, -4), mat=bone_mat)
    box('rosary', (3.5, -20.5, -6.8), (1, 20, 0), mat=string_mat)
    for i, yy in enumerate((-18.5, -15, -11.5, -8, -4.5, -1)):
        box('rosary', (3, yy, -7.8), (2, 2, 2), name='bead')
    box('rosary', (3.5, 0.5, -7.3), (1, 9, 1), mat=wood_mat, inflate=0.3)       # inverted cross, crossbar low
    box('rosary', (1.5, 5.5, -7.3), (5, 1, 1), mat=wood_mat, inflate=0.3)

    # ---------------- bunch of five keys on an iron ring, front-right of the cincture
    bone('keys', (-4.5, -20.5, -7.2), parent='body', rot=(-15, 0, 5), mat=none_mat)
    box('keys', (-6.5, -21, -7.6), (4, 4, 0), decals={'front': art(RING, KEY_PAL)})
    box('keys', (-8, -18.5, -7.8), (3, 8, 0), decals={'front': art(KEY_A, KEY_PAL)})
    box('keys', (-5.5, -18.5, -8.0), (3, 7, 0), decals={'front': art(KEY_B, KEY_PAL_B)})
    box('keys', (-6.5, -18, -8.2), (3, 9, 0), decals={'front': art(KEY_C, KEY_PAL)})
    box('keys', (-4.5, -18.5, -9.5), (0, 8, 3), decals={'west': art(KEY_A, KEY_PAL_B)})
    box('keys', (-7.5, -18.5, -9.3), (0, 7, 3), decals={'west': art(KEY_B, KEY_PAL)})

    # ---------------- chest: bodice pinched to an 8-texel waist, hunched hump with vertebrae
    bone('chest', (0, -20, 0.5), parent='body', rot=(13, 0, -4), mat=wool_mat)
    box('chest', (-4, -27, -3), (8, 7, 6), name='waist')
    box('chest', (-5, -31, -3.5), (10, 4, 7), name='ribs')
    box('chest', (-6.5, -36, -4.5), (13, 5, 9), name='ribs')
    box('chest', (-8.5, -39, -4), (17, 3, 8), name='yoke')
    box('chest', (-6.5, -40, 1.5), (13, 10, 7), name='hump')
    for yy, zz in ((-39.5, 8.0), (-36.5, 8.2), (-33.5, 7.9)):
        box('chest', (-1, yy, zz), (2, 2, 2), mat=bone_mat, name='vertebra')
    box('chest', (-4, -31, -4.6), (8, 10, 1), name='scap')
    # guimpe: rounded off-white shoulder bib (ends well above the waist), blood-soaked lower edge
    box('chest', (-9, -40, -5.5), (18, 9, 11), mat=linen_mat, name='bib')

    # ---------------- inverted wooden cross on a chain, over the guimpe and scapular
    bone('cross', (0, -38, -5.8), parent='chest', rot=(-4, 0, 3), mat=wood_mat)
    for i, yy in enumerate((-38.5, -37, -35.5)):
        box('cross', (-0.5, yy, -6.7 - (i % 2) * 0.3), (1, 2, 1), mat=iron_mat, inflate=0.12 if i % 2 else 0.0)
    box('cross', (-1.5, -34, -7.6), (3, 13, 2), decals={'front': art(CROSS_BLOOD, BAND_PAL)})
    box('cross', (-4.5, -26, -7.85), (9, 2, 2))

    # ---------------- neck: juts forward out of the hunched shoulders (hidden in the wimple)
    bone('neck', (0, -38.5, -1), parent='chest', rot=(17, 0, 0), mat=linen_mat)
    box('neck', (-4, -43, -5), (8, 6, 8), name='neckl')

    # ---------------- head: pitched back up so the face looks out from under the brow
    # layout (head frame, rest): hood dome -60, crown -59..-57, coif band -57..-54 (down to the brow), brow -54..-52,
    # sockets -52..-49, cheekbones -49..-48, muzzle -47..-45, teeth -45..-41, jaw -41..-38, chin -38..-36
    bone('head', (0, -41, -2), parent='neck', rot=(-21, 0, 7), mat=skin_mat)
    fbox('head', (-7, -55, -7), (14, 8, 12), name='skull')
    fbox('head', (-6, -54, -8), (12, 2, 1), name='brow')
    fbox('head', (-7, -49, -8), (4, 1, 1), name='cheek')
    fbox('head', (3, -49, -8), (4, 1, 1), name='cheek')
    fbox('head', (-8, -47, -9), (16, 2, 3), name='muzzle')
    box('head', (-8, -45, -9.4), (16, 4, 0), mat=teeth_mat, name='upper_teeth')
    box('head', (-7, -45, -9.1), (14, 3, 0), mat=teeth_mat, name='upper_teeth_2')
    box('head', (-7, -45, -8.3), (14, 7, 6), mat=throat_mat, name='throat')
    # coif: band over the forehead down to the brow, thin sides that step OUT under the eyes, lower wimple
    # BEHIND the jaw (it frames the jaw, never covers it)
    fbox('head', (-9, -57, -10), (18, 3, 13), mat=linen_mat, name='band')
    fbox('head', (-9, -54, -9.5), (3, 5, 7), mat=linen_mat, name='coif_r')
    fbox('head', (6, -54, -9.5), (3, 5, 7), mat=linen_mat, name='coif_l')
    fbox('head', (-9, -49, -9.5), (2, 2, 7), mat=linen_mat, name='coif_r')
    fbox('head', (7, -49, -9.5), (2, 2, 7), mat=linen_mat, name='coif_l')
    fbox('head', (-6, -54, -9.5), (1, 1, 3), mat=linen_mat, name='coif_r')
    fbox('head', (5, -54, -9.5), (1, 1, 3), mat=linen_mat, name='coif_l')
    box('head', (-9, -47, -6.5), (18, 9, 8), mat=linen_mat, name='wimple_lo')
    box('head', (-7, -38, -6.5), (14, 3, 9), mat=linen_mat, name='gorget')
    box('head', (-5, -35, -6), (10, 2, 8), mat=linen_mat, name='gorget')

    # ---------------- face_crack: hidden INSIDE the skull at rest (z -6.5); 'reveal' slides it out (dz -2.7)
    bone('face_crack', (3, -50, -6.5), parent='head', mat=none_mat)
    box('face_crack', (0, -55, -6.5), (6, 10, 0), decals={'front': art(CRACK_ART, CRACK_PAL)})

    # ---------------- smoke: hidden inside skull + wimple, rises out of the hood in the 'burn' pose (dy -15)
    bone('smoke', (0, -50, 0), parent='head', mat=none_mat)
    box('smoke', (-6, -55, -1), (5, 10, 0), decals={'front': art(WISP_A, SMOKE_PAL)})
    box('smoke', (1, -55, 0.5), (5, 10, 0), decals={'front': art(WISP_B, SMOKE_PAL)})
    box('smoke', (0, -55, -5), (0, 10, 5), decals={'west': art(WISP_B, SMOKE_PAL)})

    # ---------------- jaw: hinge deep in the skull, drops onto the black gullet
    bone('jaw', (0, -45, -1), parent='head', rot=(8, 0, -3), mat=jaw_mat)
    fbox('jaw', (-8, -41, -9), (16, 3, 8), name='jaw')
    box('jaw', (-8, -44, -8.8), (16, 3, 0), mat=teeth_mat, name='lower_teeth')
    box('jaw', (-7, -44, -8.6), (14, 3, 0), mat=teeth_mat, name='lower_teeth_2')
    fbox('jaw', (-5, -38, -8.5), (10, 1, 6), name='chin')
    fbox('jaw', (-2, -37, -8), (4, 1, 4), name='chin')

    # ---------------- hood: stepped crown, inner hood hugging the coif, brim corners rounding the white frame,
    # side drapes flaring outward AND sweeping back (the face juts out of the hood in profile)
    box('head', (-11, -58, -9.5), (2, 11, 11), mat=veil_mat, name='hood_in')
    box('head', (9, -58, -9.5), (2, 11, 11), mat=veil_mat, name='hood_in')
    box('head', (-11, -47, -6), (2, 10, 8), mat=veil_mat, name='hood_in')
    box('head', (9, -47, -6), (2, 10, 8), mat=veil_mat, name='hood_in')
    box('head', (-9, -57, -10.5), (2, 1, 2), mat=veil_mat, name='brim')
    box('head', (7, -57, -10.5), (2, 1, 2), mat=veil_mat, name='brim')
    box('head', (-9, -56, -10.5), (1, 1, 2), mat=veil_mat, name='brim')
    box('head', (8, -56, -10.5), (1, 1, 2), mat=veil_mat, name='brim')
    bone('hood_peak', (0, -57, -2), parent='head', rot=(-6, 0, 0), mat=veil_mat)
    box('hood_peak', (-10, -59, -10.5), (20, 2, 15), name='crown')
    box('hood_peak', (-7, -60, -9), (14, 1, 12), name='dome')
    box('hood_peak', (-4, -61, -7), (8, 1, 9), name='dome')
    for side, sx in (('right', -1), ('left', 1)):
        hb = f'hood_{side}'
        bone(hb, (11 * sx, -58.5, -9.5), parent='head', rot=(12, 0, -16 * sx), mat=veil_mat)
        box(hb, (11 * sx - (2 if sx < 0 else 0), -58.5, -9.5), (2, 24, 12), name='hood_side')
    bone('veil', (0, -59, 4.5), parent='head', rot=(28, 0, 0), mat=veil_mat)
    box('veil', (-9.5, -59, 4.5), (19, 24, 2), name='veil_hi')

    # ---------------- back veil: stepped V lying on the hump, narrower than the waist by the time it gets there;
    # side drapes falling from under the hood over the shoulders
    bone('veil_lower', (0, -41, 8.6), parent='chest', rot=(-9, 0, 0), mat=veil_mat)
    box('veil_lower', (-9, -41, 8.6), (18, 11, 1), name='veil_lo')
    box('veil_lower', (-6.5, -30, 8.4), (13, 9, 1), name='veil_lo')
    box('veil_lower', (-3.5, -21, 8.2), (7, 14, 1), name='veil_tail')
    for side, sx in (('right', -1), ('left', 1)):
        vb = f'veil_{side}'
        bone(vb, (9.5 * sx, -44, 0.5), parent='chest', rot=(4, 0, -30 * sx), mat=veil_mat)
        box(vb, (9.5 * sx - (3 if sx < 0 else 0), -44, -6), (3, 16, 13), name='veil_side')

    # ---------------- arms: long, hanging AWAY from the waist; bell sleeves of three flared panels
    for side, sx in (('right', -1), ('left', 1)):
        ax = 11 * sx
        ay = -35 if side == 'right' else -36
        az = 0.5
        arm, fa, hand = f'{side}_arm', f'{side}_forearm', f'{side}_hand'
        bone(arm, (ax, ay, az), parent='chest', rot=(-4, 0, (-19 if sx < 0 else -17) * sx), mat=wool_mat)
        box(arm, (ax - 3, ay - 2.5, az - 3), (6, 5, 6), name='shoulder')
        box(arm, (ax - 2.5, ay + 1.5, az - 2.5), (5, 11, 5))
        ey = ay + 12
        bone(fa, (ax, ey, az), parent=arm, rot=(-8, 0, 9 * sx), mat=wool_mat)
        box(fa, (ax - 3, ey - 1.5, az - 3), (6, 6, 6), name='core')
        box(fa, (ax - sx * 3.25 - 0.5, ey + 2, az - 3.5), (1, 10, 7), name=f'slv_i{side[0]}')
        b1 = f'sleeve_{side}_front'
        bone(b1, (ax, ey + 2, az - 3), parent=fa, rot=(-24, 0, 0), mat=wool_mat)
        box(b1, (ax - 4.5, ey + 2, az - 4), (9, 13, 1), name='slv_f')
        b2 = f'sleeve_{side}_back'
        bone(b2, (ax, ey + 2, az + 3), parent=fa, rot=(22, 0, 0), mat=wool_mat)
        box(b2, (ax - 4.5, ey + 2, az + 3), (9, 15, 1), name='slv_b')
        b3 = f'sleeve_{side}_outer'
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
            box(fb, (cx - 0.5, fy - 0.5, az - 0.8), (1, 1, 1), inflate=0.45, name='knuckle')
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
        if side == 'left':
            # brass hand-bell (3 x 4 x 3) pinched by its wooden handle between thumb and index
            bone('bell', (tx + 0.5, hy + 2, az - 3), parent=hand, rot=(0, 0, 0), mat=brass_mat)
            box('bell', (tx, hy + 1, az - 3.5), (1, 3, 1), mat=wood_mat, inflate=0.1)
            box('bell', (tx - 1, hy + 4, az - 4.5), (3, 4, 3))
            box('bell', (tx - 1, hy + 7, az - 4.5), (3, 1, 3), inflate=0.3)
            box('bell', (tx, hy + 8, az - 3.5), (1, 1, 1), mat=iron_mat)

    # lift the whole figure 3 texels (the robe is long enough to keep the hem just off the ground): 2.7 blocks
    r.bones['body'].pivot = (0.0, -23.0, 0.0)
    m = MonjaMeshModel('monja', 256, 208, r.roots)
    m.scale = 0.5
    return m


def _hands(splay, curl, thumb=0.0, sides=('right', 'left')):
    """Finger spread (z, outward) and knuckle curl of the tips for both hands."""
    out = {}
    for side, sx in (('right', -1), ('left', 1)):
        if side not in sides:
            continue
        for f in range(4):
            out[f'{side}_finger_{f + 1}'] = (0, 0, (f - 1.5) / 1.5 * splay * sx, 0, 0, 0)
            out[f'{side}_finger_{f + 1}_tip'] = (curl, 0, 0, 0, 0, 0)
        out[f'{side}_thumb'] = (0, 0, thumb * sx, 0, 0, 0)
    return out


def _robe(front, side, back, extra=0.0):
    """Additive flare for the 8 robe panels (negative = flare out): front (0,1,7), sides (2,6), back (3,4,5)."""
    vals = [front, (front + side) / 2, side, (side + back) / 2, back, (side + back) / 2, side, (front + side) / 2]
    names = ['robe_front', 'robe_front_right', 'robe_right', 'robe_back_right',
             'robe_back', 'robe_back_left', 'robe_left', 'robe_front_left']
    return {n: (v + extra, 0, 0, 0, 0, 0) for n, v in zip(names, vals)}


POSES = {
    # the jumpscare: rises and lunges, arms flung up and out so the claws frame the face, head snapped
    # sideways, jaw unhinged
    'attack': {
        'body': (0.06, 0, 0, 0, -1.5, -2.0),
        'chest': (-0.1, 0, 0, 0, 0, 0),
        'neck': (-0.05, 0, 0, 0, 0, 0),
        'head': (-0.1, 0, 0.3, 0, 0, 0),
        'jaw': (0.42, 0, 0.06, 0, 2.6, -1.5),
        'veil': (0.25, 0, 0, 0, 0, 0),
        'veil_lower': (0.2, 0, 0, 0, 0, 0),
        'veil_right': (0, 0, 0.25, 0, 0, 0),
        'veil_left': (0, 0, -0.25, 0, 0, 0),
        'right_arm': (-2.2, 0, -0.95, 0, 0, 0),
        'left_arm': (-2.05, 0, 0.85, 0, 0, 0),
        'right_forearm': (-0.75, 0, 0, 0, 0, 0),
        'left_forearm': (-0.9, 0, 0, 0, 0, 0),
        'sleeve_right_front': (-0.2, 0, 0, 0, 0, 0),
        'sleeve_left_front': (-0.2, 0, 0, 0, 0, 0),
        'sleeve_right_back': (0.35, 0, 0, 0, 0, 0),
        'sleeve_left_back': (0.35, 0, 0, 0, 0, 0),
        'right_hand': (0.5, 0, 0, 0, 0, 0),
        'left_hand': (0.5, 0, 0, 0, 0, 0),
        **_hands(0.3, 0.5, 0.3),
    },
    # head thrown back, jaw at max, arms out and back, fingers splayed: the shriek
    'scream': {
        'chest': (-0.2, 0, 0, 0, 0, 0),
        'neck': (-0.15, 0, 0, 0, 0, 0),
        'head': (-0.4, 0, 0.12, 0, 0, 0),
        'jaw': (0.6, 0, 0, 0, 2.6, -1.2),
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
    # holy light / fire: cowers, forearms crossed over the face, head ducked and turned away, smoke rising
    'burn': {
        'body': (0, 0, 0, 0, 2.0, 0),
        'chest': (0.4, 0, 0, 0, 0, 0),
        'head': (0.35, 0.35, 0, 0, 0, 0),
        'jaw': (0.45, 0, 0, 0, 0, 0),
        'smoke': (-0.35, -0.35, 0, 0, -15, 2),
        'veil': (-0.2, 0, 0, 0, 0, 0),
        'veil_right': (0, 0, -0.15, 0, 0, 0),
        'veil_left': (0, 0, 0.15, 0, 0, 0),
        'right_arm': (-1.45, 0, 0.35, 0, 0, 0),
        'left_arm': (-1.3, 0, -0.4, 0, 0, 0),
        'right_forearm': (-0.9, 0, 0.5, 0, 0, 0),
        'left_forearm': (-0.95, 0, -0.55, 0, 0, 0),
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
        'sleeve_right_back': (0.4, 0, 0, 0, 0, 0),
        'right_hand': (0.3, 0, 0, 0, 0, 0),
        **_hands(0.35, 0.35, 0.3),
    },
}



def _fist(side, curl=1.25, tip=1.35, keep=()):
    """Curl the fingers of one hand into a fist, except the fingers listed in keep (1 = outer .. 4 = index)."""
    out = {}
    for f in range(1, 5):
        if f in keep:
            continue
        out[f'{side}_finger_{f}'] = (curl, 0, 0, 0, 0, 0)
        out[f'{side}_finger_{f}_tip'] = (tip, 0, 0, 0, 0, 0)
    return out


POSES.update({
    # directs the dead girls' choir: the right INDEX finger is the baton (raised high, the other fingers in a
    # fist), the left hand holds the brass bell in front of the chest, chin up, mouth ajar as if humming
    'conduct': {
        'body': (0.0, 0.22, 0, 0, -1.0, 0),
        'chest': (-0.16, 0, 0.06, 0, 0, 0),
        'neck': (-0.12, 0, 0, 0, 0, 0),
        'head': (-0.18, -0.2, -0.3, 0, 0, 0),
        'jaw': (0.12, 0, 0, 0, 0, 0),
        'right_arm': (-1.95, 0, -0.45, 0, 0, 0),
        'right_forearm': (-0.7, 0, 0, 0, 0, 0),
        'right_hand': (-0.35, 0, 0, 0, 0, 0),
        'sleeve_right_front': (0.9, 0, 0, 0, 0, 0),
        'sleeve_right_back': (0.6, 0, 0, 0, 0, 0),
        **_fist('right', keep=(4,)),
        'right_finger_4': (-0.15, 0, -0.1, 0, 0, 0),
        'right_finger_4_tip': (-0.25, 0, 0, 0, 0, 0),
        'right_thumb': (0.5, 0, 0.5, 0, 0, 0),
        'left_arm': (-0.55, 0, 0.12, 0, 0, 0),
        'left_forearm': (-1.15, 0, 0.35, 0, 0, 0),
        'left_hand': (0.15, 0, 0, 0, 0, 0),
        'veil_lower': (0.1, 0, 0, 0, 0, 0),
    },
    # sits perfectly still (on a chair / pew edge): skirt spread over the knees, claws resting on the lap,
    # back straight, head tilted 30 degrees
    'sit': {
        'body': (0, 0, 0, 0, 10, 0),
        **_robe(-0.62, -0.3, -0.22),
        'scapular_front': (-0.6, 0, 0, 0, 0, 0),
        'scapular_back': (0.2, 0, 0, 0, 0, 0),
        'rosary': (-0.6, 0, 0, 0, 0, 0),
        'keys': (-0.55, 0, 0, 0, 0, 0),
        'chest': (-0.18, 0, 0.07, 0, 0, 0),
        'neck': (-0.1, 0, 0, 0, 0, 0),
        'head': (0.05, 0, 0.4, 0, 0, 0),
        'jaw': (-0.05, 0, 0, 0, 0, 0),
        'right_arm': (-0.45, 0, -0.3, 0, 0, 0),
        'right_forearm': (-0.75, 0, 0.2, 0, 0, 0),
        'right_hand': (0.6, 0, 0, 0, 0, 0),
        'left_arm': (-0.4, 0, 0.28, 0, 0, 0),
        'left_forearm': (-0.8, 0, -0.2, 0, 0, 0),
        'left_hand': (0.6, 0, 0, 0, 0, 0),
        **_hands(0.1, 0.35, 0.0),
    },
    # upside down on the ceiling: flipped about the waist (hem against a 3-block ceiling, the head hanging
    # just above the floor), limbs spread like a spider gripping the ceiling, the veils falling toward the floor,
    # head screwed round to look at you, jaw unhinged
    'ceiling': {
        'body': (0, 0, math.pi, 0, -4, 0),
        **_robe(-0.75, -0.75, -0.75),
        'scapular_front': (-0.7, 0, 0, 0, 0, 0),
        'scapular_back': (0.7, 0, 0, 0, 0, 0),
        'rosary': (2.6, 0, 0, 0, 0, 0),
        'keys': (2.7, 0, 0, 0, 0, 0),
        'cross': (2.9, 0, 0, 0, 0, 0),
        'chest': (-0.25, 0, 0, 0, 0, 0),
        'neck': (-0.25, 0, 0, 0, 0, 0),
        'head': (0.35, 0.55, 0.35, 0, 0, 0),
        'jaw': (0.5, 0, 0.05, 0, 2.2, -1.2),
        'veil': (2.3, 0, 0, 0, 0, 0),
        'veil_lower': (2.9, 0, 0, 0, 0, 0),
        'veil_right': (2.7, 0, 0.3, 0, 0, 0),
        'veil_left': (2.7, 0, -0.3, 0, 0, 0),
        'hood_right': (1.2, 0, 0.3, 0, 0, 0),
        'hood_left': (1.2, 0, -0.3, 0, 0, 0),
        'right_arm': (0.25, 0, 1.25, 0, 0, 0),
        'left_arm': (0.25, 0, -1.25, 0, 0, 0),
        'right_forearm': (0, 0, -1.1, 0, 0, 0),
        'left_forearm': (0, 0, 1.1, 0, 0, 0),
        'right_hand': (0, 0, -0.4, 0, 0, 0),
        'left_hand': (0, 0, 0.4, 0, 0, 0),
        **_hands(0.5, 0.9, 0.4),
    },
    # blows out a candle: neck and head thrust forward, face kept level, jaw ajar
    'blow': {
        'body': (0.1, 0, 0, 0, 0, -1.5),
        'chest': (0.12, 0, 0, 0, 0, 0),
        'neck': (0.38, 0, 0, 0, 0, -1.5),
        'head': (-0.48, 0, -0.1, 0, 0, 0),
        'jaw': (0.17, 0, 0, 0, 0.4, -0.3),
        'veil': (0.3, 0, 0, 0, 0, 0),
        'veil_lower': (0.15, 0, 0, 0, 0, 0),
        'right_arm': (-0.35, 0, -0.12, 0, 0, 0),
        'left_arm': (-0.3, 0, 0.12, 0, 0, 0),
        'right_forearm': (-0.25, 0, 0, 0, 0, 0),
        'left_forearm': (-0.25, 0, 0, 0, 0, 0),
    },
    # (comic) soaked by holy water: looks down at her dripping habit, arms held away from the body with limp
    # wrists, the hood slipped back and askew, every drape hanging flat and the robe clinging (no flare)
    'wet': {
        'body': (0, 0, 0, 0, 1.5, 0),
        **_robe(0.2, 0.22, 0.2),
        'scapular_front': (0.18, 0, 0, 0, 0, 0),
        'scapular_back': (-0.18, 0, 0, 0, 0, 0),
        'rosary': (0.2, 0, 0, 0, 0, 0),
        'keys': (0.2, 0, 0, 0, 0, 0),
        'chest': (0.25, 0, 0, 0, 0, 0),
        'neck': (0.2, 0, 0, 0, 0, 0),
        'head': (0.55, 0, -0.12, 0, 0, 0),
        'jaw': (0.22, 0, 0, 0, 0, 0),
        'hood_peak': (0.45, 0.15, 0.25, 0, 1.0, 3.0),
        'hood_right': (-0.15, 0, -0.32, 0, 2.5, 1.0),
        'hood_left': (0.1, 0, 0.36, 0, 3.0, 1.0),
        'veil': (-0.5, 0, 0.18, 0, 3.0, 0),
        'veil_right': (0, 0, -0.5, 0, 0, 0),
        'veil_left': (0, 0, 0.5, 0, 0, 0),
        'right_arm': (-0.3, 0, 0.32, 0, 0, 0),
        'right_forearm': (-1.25, 0, 0.15, 0, 0, 0),
        'right_hand': (1.1, 0, 0, 0, 0, 0),
        'left_arm': (-0.3, 0, -0.32, 0, 0, 0),
        'left_forearm': (-1.3, 0, -0.15, 0, 0, 0),
        'left_hand': (1.15, 0, 0, 0, 0, 0),
        'sleeve_right_front': (0.35, 0, 0, 0, 0, 0),
        'sleeve_left_front': (0.35, 0, 0, 0, 0, 0),
        'sleeve_right_back': (-0.35, 0, 0, 0, 0, 0),
        'sleeve_left_back': (-0.35, 0, 0, 0, 0, 0),
        'sleeve_right_outer': (0, 0, -0.35, 0, 0, 0),
        'sleeve_left_outer': (0, 0, 0.35, 0, 0, 0),
        **_hands(-0.1, 0.25, 0.0),
    },
    # kneeling, forehead pressed against the wall in front of her, limp arms hanging to the floor
    'kneel_wall': {
        'body': (0.2, 0, 0, 0, 14, -1.0),
        **_robe(-0.85, -0.6, -0.55),
        'scapular_front': (-0.9, 0, 0, 0, 0, 0),
        'scapular_back': (0.4, 0, 0, 0, 0, 0),
        'rosary': (-0.6, 0, 0, 0, 0, 0),
        'keys': (-0.6, 0, 0, 0, 0, 0),
        'chest': (0.42, 0, 0.06, 0, 0, 0),
        'neck': (0.2, 0, 0, 0, 0, 0),
        'head': (0.25, 0, -0.12, 0, 0, 0),
        'jaw': (0.06, 0, 0, 0, 0, 0),
        'veil': (-0.1, 0, 0, 0, 0, 0),
        'veil_lower': (-0.35, 0, 0, 0, 0, 0),
        'right_arm': (-0.72, 0, -0.28, 0, 0, 0),
        'left_arm': (-0.68, 0, 0.26, 0, 0, 0),
        'right_forearm': (0.05, 0, 0, 0, 0, 0),
        'left_forearm': (0.05, 0, 0, 0, 0, 0),
        **_hands(0.05, 0.15, 0.0),
    },
    # the revelation: arms opened wide like a saint, chin up, and the crack over her left eye shows Clara's
    # living brown eye and a tear (face_crack slides out of the skull)
    'reveal': {
        'body': (-0.04, 0, 0, 0, -1.0, 0),
        'chest': (-0.2, 0, 0, 0, 0, 0),
        'neck': (-0.12, 0, 0, 0, 0, 0),
        'head': (-0.08, 0, 0.05, 0, 0, 0),
        'jaw': (-0.03, 0, 0, 0, 0, 0),
        'face_crack': (0, 0, 0, 0, 0, -2.7),
        'veil_right': (0, 0, 0.2, 0, 0, 0),
        'veil_left': (0, 0, -0.2, 0, 0, 0),
        'right_arm': (-0.3, 0, 1.0, 0, 0, 0),
        'left_arm': (-0.3, 0, -1.0, 0, 0, 0),
        'right_forearm': (-0.35, 0, -0.25, 0, 0, 0),
        'left_forearm': (-0.35, 0, 0.25, 0, 0, 0),
        'right_hand': (-0.3, 0, 0, 0, 0, 0),
        'left_hand': (-0.3, 0, 0, 0, 0, 0),
        **_hands(0.45, -0.1, 0.4),
    },
})

ANIM_NOTES = """
Sor Agonia -- animation contract.  Angles in radians, ADDED to the rest pose; offsets (dx, dy, dz) in model
texels at 2x density (inside scale_root: 2 texels = 1 vanilla pixel, 32 = 1 block).  t = ageInTicks, s = glide
speed 0..1.  She never walks: no legs, the robe glides.  Everything moves slow and smooth EXCEPT the head snaps,
which are instant (1-2 ticks) -- that contrast is what makes the clips scary.
Poses: attack, scream, burn, reach (existing) + conduct, sit, ceiling, blow, wet, kneel_wall, reveal.

ROOT
* body -- root at the waist (pivot y -23): leather cincture + buckle, hips.  HOVER BOB: dy = -0.6 +
  sin(t*0.07)*0.8 (hem stays 1-3 texels above the ground).  Glide: xRot +0.15*s (leans in), NO step bob.

ROBE -- 8 flared torn panels, children of body, pivots inside the hips, rest flare -13..-17 deg on x, yawed 45 deg
apart; k = 0..7: robe_front, robe_front_right, robe_right, robe_back_right, robe_back, robe_back_left, robe_left,
robe_front_left.  MonjaModel ripples the whole 'robe' group (out-of-phase sway, + glide bias).
* scapular_front / scapular_back -- long scapular strips over the robe; follow robe_front / robe_back with a lag.
* rosary -- bone beads + inverted cross hanging from the front-left of the cincture: pendulum lagging the body.
* keys -- NEW: iron ring with five keys (three iron, two brass) at the front-right of the cincture.  Jingle:
  zRot sin(t*0.9)*0.06 while gliding, a sharp 0.25 flick on attack.  Plays nicely with a key-jangle sound.

TORSO
* chest -- bodice pinched to an 8-texel waist, ribs, shoulder yoke, hunched hump (rest xRot 13 deg) with three
  vertebrae tearing through the veil, scapular chest piece and the white guimpe.  Breathing xRot sin(t*0.06)*0.03.
* cross -- inverted wooden cross on its iron chain over the guimpe: pendulum lagging the chest.
* neck -- juts forward out of the hump (rest 17 deg); look() puts half the yaw/pitch here.
* head -- FOCUS bone: skull, brow ridge, cheekbones, muzzle, upper needle teeth (2 planes), black gullet, the white
  coif (band with barbed wire down to the brow, thin sides stepping out under the eyes, lower wimple + gorget
  BEHIND the jaw), inner hood + brim corners.  Rest pitched back -21 deg (the face looks out level from the
  jutting neck) and rolled 7 deg.  Snap tilts in zRot (MonjaModel) stay as before.
* jaw -- mandible 16 wide (wider than the face), lower needle teeth (2 planes), dark tongue, pointed chin; hinge
  (0, -45, -1); rest slack 8 deg so the two rows of needles separate.  attack (0.42, 0, 0.06, 0, 2.6, -1.5)
  dislocates it onto the black gullet; scream 0.6; blow 0.17 (ajar).
* face_crack -- NEW hidden plane over the LEFT eye, parked INSIDE the skull at rest (z -6.5).  'reveal' pushes it
  out with dz -2.7 (it pops through the face once the reveal weight passes ~0.6): a vertical crack showing warm
  human skin, a moist brown eye with a highlight and a tear running down over the gum.  Java can also just
  apply(pose("reveal"), w) or offset("face_crack", 0, 0, -2.7) on its own for a quick glimpse.
* smoke -- NEW: three grey wisps parked inside the skull; 'burn' lifts them dy -15 out of the crown (counter-
  rotated so they rise straight).  Add the existing DEMON_SMOKE particles on top.
* hood_peak -- stepped crown (dome 3 steps) with a brim overhanging the white band.  Static except 'wet' (slips
  back and askew).  hood_right / hood_left -- side drapes pivoting at the brim's front-top corners, flaring 16 deg
  outward and swept back 12 deg so the face juts out of the hood in profile.  Chase: xRot +0.2*s (trail).
* veil -- rear drape streaming back from the crown (rest 28 deg).  MonjaModel: rot sin(t*0.08)*0.05 + glide*0.35.

VEIL ON THE BODY
* veil_lower -- stepped V of black veil lying on the hump down to the hips (never wider than the waist from the
  front, so the pinch stays readable); slit for the vertebrae.  Trails +0.35*s.
* veil_right / veil_left -- shoulder drapes flaring 30 deg: with the hood they make the bell-shaped top of the
  hourglass.  Flutter zRot sin(t*0.07 + side)*0.05.

ARMS -- right_* is -X (viewer's left).  Rest: long arms splayed away from the waist (negative space both sides).
* right_arm / left_arm, right_forearm / left_forearm, right_hand / left_hand -- as before.
* sleeve_right_front/back/outer, sleeve_left_front/back/outer -- RENAMED from right_sleeve_* so that MonjaModel's
  ripple("sleeve", ...) now actually drives the bell-sleeve panels (it matched nothing before).
* right_finger_1..4 (+ _tip) / left_finger_1..4 (+ _tip) -- 1 = outer, 4 = INDEX (next to the thumb).
* right_thumb / left_thumb.
* bell -- NEW: brass hand-bell (3x4x3 body, wooden handle, flared rim, iron clapper) pinched between the left
  thumb and index.  Ring it: zRot sin(t*1.6)*0.35 for ~20 ticks before a teleport ("tilin-tilin").

POSES (blend with apply(pose(name), w); offsets are model texels)
* conduct -- directs the choir: right arm raised forward, INDEX finger straight up as the baton (fingers 1-3 in a
  fist), left hand holds the bell in front of the chest, chin up, mouth ajar.  Beat time with right_forearm xRot
  sin(t*0.5)*0.15 and right_hand sin(t*0.5 - 0.6)*0.1 on top of the pose.
* sit -- sits perfectly still: body dy +10, skirt spread over the knees (hem may dip under the floor: hidden by
  it), claws resting on the lap, back straight, head tilted 30 deg.  Do not add idle motion in this pose.
* ceiling -- upside down: body flipped (zRot pi about the waist, dy -4) so the hem touches a 3-block ceiling and
  the head hangs ~0.3 blocks above the floor; arms and fingers spread like a spider, robe flared against the
  ceiling, every veil falling toward the floor, head screwed round, jaw unhinged.  For other ceiling heights
  translate the PoseStack by (ceilingHeight - 3 blocks).
* blow -- neck thrust forward (dz -1.5), face kept level, jaw ajar: blowing out a candle.  Pair with a breath
  particle from the mouth.
* wet -- (comic) looks down at her soaked habit: robe and drapes hang flat (flare removed), hood slipped back and
  askew showing the white coif, arms held away with limp wrists, mouth open in dismay.
* kneel_wall -- kneels (body dy +14) bent forward, forehead against the wall in front of her, arms hanging limp to
  the floor, skirt pooled around her.
* reveal -- arms opened wide like a saint, chin up, mouth shut, face_crack out over the left eye (Clara's eye).
* burn -- (kept) cowers with the forearms crossed over the face, head ducked away, jaw gasping; smoke wisps rise.
* attack / scream / reach -- (kept) the lunge with the jaw dislocated, the shriek, the chase reach.

LAYERING
idle = hover bob + breathing + robe/sleeve ripple + veil sway + random head snaps + finger taps + jaw tremble.
glide/chase = idle + lean + trailing cloth * speed; blend toward POSE_REACH within 6 blocks.  attack = blend 4
ticks into POSE_ATTACK, hold 6, release over 10.  scream = POSE_SCREAM.  burn = POSE_BURN while in light.
Scripted beats: conduct (coro alto), sit (aula), ceiling (dormitorio), blow (refectorio candles), wet (holy water
gag), kneel_wall (capilla), reveal (Maitines).
"""

