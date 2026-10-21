"""DEAD LINE building kit -- Casa Morales (Pasaje Las Glicinas 1961, Villa Esperanza, conurbano sur): STRUCTURE.

A 1950s working-class chalet, lived-in, at night. Every key starts with 'casa_' and every block has kit='casa_estructura'.

Contents
  * exterior: exposed machine brick (ladrillo visto) with raked joints, white lime render with damp streaks, the cement
    salt plinth, the neighbour's party wall (medianera) with plaster patches, French clay roof tiles (cube/stairs/slab),
    ridge, eave with fascia, gutter + downpipe, front fence (low brick wall, iron railing, pedestrian gate, car gate),
    'baldosa vainilla' sidewalk, granite curb, asphalt, lawn, the flickering street lamp, dog sign, meter boxes,
    the house number.
  * interior walls per room (living beige with picture rail, hall 'verde agua', 70s green kitchen tiles with a decorated
    border, light-blue bathroom tiles, Lucía pink with stickers, Toti dark blue with posters, Nona's floral wallpaper,
    master bedroom 70s wallpaper, laundry cement), skirting/cornice trims, ceilings, floors (herringbone parquet,
    granítico, kitchen ceramic, red patio tiles, brick paving, cement, sand), the upstairs carpet runner.
  * doors (real opening doors) and in-wall windows with security bars and roll-up blinds (open/closed).
  * stairs and handrails, the basement (crumbling plaster over old brick, damp foot, the CRACK as three stacked cubes
    leaking sand, the wall the Nona breaks through as six in-wall 'boquete' pieces + rubble, the ventiluz, the two-faced
    'pared_divisoria' between basement and sealed room) and the 1961 room (grey lime wash, candle-soot plume cubes,
    scratched decals: LEMAZA big/small, the drawing 'MI AMIGO', day tallies, the priest's Latin and its glowing
    variant for beat 15, sooty handprints), the old salt circle and the Nona's patio salt (quarter pieces).
  * 'Es la humedad': a 2x2 rising-damp stain decal for the living room and its variant with a face.
  * Toti's four poster decals (casa_poster_toti_1..4), the marble door threshold (casa_umbral_marmol: lay it under
    every interior door), street signage legible at arm's length (number 1961, doorbell, street plate + numbering
    strip, dog sign with the Nona's marker scribble in a wall version and a 32 px railing version).

VARIANTS (round 1 of the art review): plain wall/floor cubes have VAR = 10 random variants - mostly clean re-seeds of
the base mottling, each light defect (a hairline crack, a grease drop, a cracked tile...) in ONE variant only, so
nothing repeats louder than 1 block in 10. Loud, story-like defects are separate hand-placed cubes: *_marco (ghost
of a picture), pared_pasillo_rayada (finger trails), pared_cocina_hollin, azulejo_*_falta / azulejo_*_sucio (missing
tile / dirty grout - use _sucio only on the course by the floor, bath, tap or stove), medianera_parche / _hueco,
parquet_mancha, arena_pisadas / _arrastre, asfalto_bache, empapelado_nona_cruz, cemento_lavadero_zocalo (grimy
foot course). Rising damp: casa_zocalo_revoque_humedad goes UNDER casa_revoque_humedad (its wet zone continues down
to the plinth); the six revoque_humedad variants all meet their neighbours at the same front height on the seams.
Inner-corner trims: *_esquina_der (side wall on your right as you face the corner) and *_esquina_izq (on your left).
Every element model goes through fix_coplanar(): no same-direction coplanar faces (no z-fighting).

ORIENTATION CONVENTIONS (authoring = facing north, front at z=0):
  * wall pieces (trims, decals, signs, meter boxes): they sit against the wall BEHIND them (the z=16 side); place them in
    the air block in front of the wall with 'facing' = the direction you look at them from... i.e. facing points away
    from the wall, towards the viewer.
  * in-wall pieces (windows, the broken wall): they REPLACE a wall block. 'facing' = the EXTERIOR / the side the bars and
    blinds are on (windows) or the basement side (broken wall). Interior = the z=16 side.
  * '_izq' / '_der' = left / right as seen by someone standing in FRONT (on the 'facing' side) looking at the piece.
    For a window facing the street, izq is the left half seen from the sidewalk (it is on the right seen from inside).
  * multi-block decals (the damp stain 2x2, the LEMAZA scratches 3x1) are ONE block whose model overflows into the
    neighbours: place it at the bottom-centre (3 wide) or bottom-left-of-centre (2 wide: the block covers x -8..24).
  * salt circles (r = 3 blocks, centred on a block CORNER): 5 pieces per quarter, see SAL_LAYOUT below.

Painting approach (shared with the Colegio kit): every texture is a small layered pixel-art painting made with numpy:
hand-picked hue-shifted ramps, low-frequency periodic value noise only to cluster tones, deliberate structural lines
(joints, bevels, grain, cracks, chips), variants that share their outer border so they tile seamlessly.
"""
import math

import numpy as np

from bkit import Cube, Slab, Stairs, Furniture, Door, box, plane, shash, FACES

KIT = 'casa_estructura'
N = 32  # texels per block


# =============================================================================================== colour & canvas
def C(h):
    h = h.lstrip('#')
    return np.array([int(h[k:k + 2], 16) for k in (0, 2, 4)], float)


class Ramp:
    """Hand-picked ramp, dark -> light. ramp[idx_array] -> (..., 3) float colours (indices are clamped)."""

    def __init__(self, *hexes):
        self.c = np.array([C(h) for h in hexes])
        self.n = len(hexes)

    def __getitem__(self, idx):
        idx = np.asarray(idx)
        if idx.dtype.kind == 'f' and np.any(idx != np.floor(idx)):
            return self.lerp(idx)
        return self.c[np.clip(idx.astype(int), 0, self.n - 1)]

    def lerp(self, idx):
        """Fractional index (soft, low-contrast fields such as latex paint): blends neighbouring ramp entries."""
        f = np.clip(np.asarray(idx, float), 0, self.n - 1)
        i0 = np.floor(f).astype(int)
        i1 = np.minimum(i0 + 1, self.n - 1)
        t = (f - i0)[..., None]
        return self.c[i0] * (1 - t) + self.c[i1] * t


class Cv:
    """RGBA float canvas. Painting is done through ramps + index maps so every colour comes from a palette."""

    def __init__(self, w=N, h=N):
        self.w, self.h = w, h
        self.rgb = np.zeros((h, w, 3))
        self.a = np.zeros((h, w))
        self.Y, self.X = np.mgrid[0:h, 0:w]

    def put(self, ramp, idx, mask=None, a=255):
        cols = ramp[np.broadcast_to(np.asarray(idx), (self.h, self.w))]
        m = np.ones((self.h, self.w), bool) if mask is None else mask
        self.rgb[m] = cols[m]
        if np.ndim(a):
            self.a[m] = np.broadcast_to(a, (self.h, self.w))[m]
        else:
            self.a[m] = a

    def col(self, color, mask, a=255):
        self.rgb[mask] = C(color) if isinstance(color, str) else color
        self.a[mask] = a

    def tint(self, color, t, mask=None):
        c = C(color) if isinstance(color, str) else np.asarray(color, float)
        t = np.broadcast_to(np.asarray(t, float), (self.h, self.w))
        if mask is not None:
            t = np.where(mask, t, 0.0)
        self.rgb = self.rgb * (1 - t[..., None]) + c * t[..., None]

    def mul(self, f, mask=None):
        f = np.broadcast_to(np.asarray(f, float), (self.h, self.w))
        if mask is not None:
            f = np.where(mask, f, 1.0)
        self.rgb = self.rgb * f[..., None]

    def dot(self, x, y, color, a=255):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.rgb[y, x] = C(color) if isinstance(color, str) else color
            self.a[y, x] = a

    def out(self):
        return np.dstack([np.clip(self.rgb, 0, 255), np.clip(self.a, 0, 255)]).round().astype(np.uint8)


# =============================================================================================== noise & masks
def vnoise(w, h, cx, cy, seed):
    """Periodic value noise (period = the canvas), smoothstep interpolated."""
    rng = np.random.default_rng(seed & 0xffffffff)
    g = rng.random((cy, cx))
    fx = (np.arange(w) + 0.5) / w * cx
    fy = (np.arange(h) + 0.5) / h * cy
    x0 = np.floor(fx).astype(int)
    y0 = np.floor(fy).astype(int)
    tx = fx - x0
    ty = fy - y0
    tx = tx * tx * (3 - 2 * tx)
    ty = ty * ty * (3 - 2 * ty)
    x1, y1 = (x0 + 1) % cx, (y0 + 1) % cy
    x0, y0 = x0 % cx, y0 % cy
    a, b = g[np.ix_(y0, x0)], g[np.ix_(y0, x1)]
    c, d = g[np.ix_(y1, x0)], g[np.ix_(y1, x1)]
    top = a + (b - a) * tx[None, :]
    bot = c + (d - c) * tx[None, :]
    return top + (bot - top) * ty[:, None]


def fbm(w, h, seed, cells=2, octaves=3, ax=1.0, ay=1.0, gain=0.5):
    tot, amp, s = 0.0, 1.0, 0.0
    for o in range(octaves):
        cx = max(1, int(round(cells * ax * 2 ** o)))
        cy = max(1, int(round(cells * ay * 2 ** o)))
        tot = tot + vnoise(w, h, cx, cy, seed + 101 * o) * amp
        s += amp
        amp *= gain
    return tot / s


def border_dist(w, h):
    Y, X = np.mgrid[0:h, 0:w]
    return np.minimum(np.minimum(X, w - 1 - X), np.minimum(Y, h - 1 - Y))


def eblend(common, var, inset=6):
    """Edge-consistent variants: the outer band is shared by all variants so any two tile together."""
    h, w = common.shape
    t = np.clip((border_dist(w, h) - 1) / inset, 0, 1)
    return common * (1 - t) + var * t


def roll(m, dy, dx):
    return np.roll(np.roll(m, dy, 0), dx, 1)


def nb(m, dy, dx, wrap=True, fill=False):
    """Neighbour lookup: result[j, i] = m[j - dy, i - dx] (dy=1 -> value of the pixel ABOVE)."""
    if wrap:
        return roll(m, dy, dx)
    out = np.full_like(m, fill)
    h, w = m.shape
    ys = slice(max(dy, 0), h + min(dy, 0))
    yd = slice(max(-dy, 0), h + min(-dy, 0))
    xs = slice(max(dx, 0), w + min(dx, 0))
    xd = slice(max(-dx, 0), w + min(-dx, 0))
    out[ys, xs] = m[yd, xd]
    return out


def dilate(m, r=1, wrap=True):
    out = m.copy()
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx * dx + dy * dy <= r * r + r * 0.5:
                out |= nb(m, dy, dx, wrap)
    return out


def erode(m, r=1, wrap=True):
    return ~dilate(~m, r, wrap)


def blob(w, h, cx, cy, rx, ry, seed, rough=0.35, cells=3):
    """Organic blob: an ellipse whose edge is displaced by noise (not periodic: keep it inside the face)."""
    Y, X = np.mgrid[0:h, 0:w]
    d = np.sqrt(((X + 0.5 - cx) / rx) ** 2 + ((Y + 0.5 - cy) / ry) ** 2)
    n = fbm(w, h, seed, cells=cells, octaves=3)
    return d + (n - 0.5) * rough * 2 < 1


def line_px(x0, y0, x1, y1):
    """Bresenham."""
    pts = []
    x0, y0, x1, y1 = int(round(x0)), int(round(y0)), int(round(x1)), int(round(y1))
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
    err = dx + dy
    while True:
        pts.append((x0, y0))
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy
    return pts


def wander(pts, seed, amp=2.0, depth=3):
    """Midpoint-displaced polyline through control points (organic cracks), returns pixel list (connected)."""
    rng = np.random.default_rng(seed)
    P = [tuple(map(float, p)) for p in pts]
    for _ in range(depth):
        Q = [P[0]]
        for a, b in zip(P, P[1:]):
            mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
            L = math.hypot(b[0] - a[0], b[1] - a[1]) + 1e-6
            nx, ny = -(b[1] - a[1]) / L, (b[0] - a[0]) / L
            off = (rng.random() - 0.5) * 2 * amp * min(1.0, L / 8)
            Q += [(mx + nx * off, my + ny * off), b]
        P = Q
        amp *= 0.55
    out = []
    for a, b in zip(P, P[1:]):
        seg = line_px(a[0], a[1], b[0], b[1])
        out += seg if not out else seg[1:]
    return out


def path_mask(pts, w=N, h=N, wrap=True):
    m = np.zeros((h, w), bool)
    for x, y in pts:
        if wrap:
            m[y % h, x % w] = True
        elif 0 <= x < w and 0 <= y < h:
            m[y, x] = True
    return m


def rim(mask, wrap=True):
    """Edge sets of a region (for bevels): returns dict of boolean maps."""
    return {
        'in_top': mask & ~nb(mask, 1, 0, wrap),     # inside, pixel above is outside
        'in_left': mask & ~nb(mask, 0, 1, wrap),
        'in_bot': mask & ~nb(mask, -1, 0, wrap),
        'in_right': mask & ~nb(mask, 0, -1, wrap),
        'out_below': ~mask & nb(mask, 1, 0, wrap),  # outside, pixel above is inside
        'out_above': ~mask & nb(mask, -1, 0, wrap),
        'out_right': ~mask & nb(mask, 0, 1, wrap),
        'out_left': ~mask & nb(mask, 0, -1, wrap),
    }


def bevel(idx, labels, hi=1, lo=-1, wrap=True, hi2=0, lo2=0):
    """Per-region bevel from a label map (each brick/tile/plank its own label, -1 = joint)."""
    up = nb(labels, 1, 0, wrap, -9)
    lf = nb(labels, 0, 1, wrap, -9)
    dn = nb(labels, -1, 0, wrap, -9)
    rt = nb(labels, 0, -1, wrap, -9)
    on = labels >= 0
    idx = idx + np.where(on & ((up != labels) | (lf != labels)), hi, 0)
    idx = idx + np.where(on & ((dn != labels) | (rt != labels)), lo, 0)
    if hi2 or lo2:
        up2 = nb(labels, 2, 0, wrap, -9)
        dn2 = nb(labels, -2, 0, wrap, -9)
        idx = idx + np.where(on & (up2 != labels) & (up == labels), hi2, 0)
        idx = idx + np.where(on & (dn2 != labels) & (dn == labels), lo2, 0)
    return idx


def posterize(n, cuts, base=0):
    """Map a 0..1 field to integer offsets: cuts = [(threshold, delta), ...] (delta applied where n > t if delta>0,
    where n < t if delta<0)."""
    out = np.zeros(n.shape, int) + base
    for t, d in cuts:
        out += np.where(n > t, d, 0) if d > 0 else np.where(n < t, d, 0)
    return out


def _hash01(gi, gj, seed):
    """Per-texel white noise in 0..1 (stable, vectorised): grains, specks."""
    v = np.sin(gi * 12.9898 + gj * 78.233 + seed * 0.123) * 43758.5453
    return v - np.floor(v)


# ===== palettes defined below
# =============================================================================================== palettes
# Casa Morales: 1950s conurbano chalet. Warm orange machine brick, cool white render going grey-green with damp,
# 70s interior colours faded by 50 years of mate, smoke and humidity. Shadows lean violet/blue, lights lean warm.
BRICK = Ramp('#36150f', '#4f1e15', '#682819', '#80331f', '#953f25', '#a74c2d', '#b65a37', '#c46b45', '#d07f58')
BRICK_D = Ramp('#2a100c', '#3d1711', '#521f15', '#65281a', '#76321f', '#863d26', '#95492f')       # overfired / clinker
MORTAR = Ramp('#2f2e2c', '#43413e', '#58554f', '#6c6861', '#7f7a72', '#928c83', '#a39d93', '#b3ada3')
RENDER_W = Ramp('#47484b', '#5f6063', '#78787a', '#929190', '#aaa9a5', '#bfbdb7', '#cfcdc6', '#dcdad3', '#e7e5df')
DAMP = Ramp('#262823', '#33362e', '#43463a', '#545647', '#666756', '#797866', '#8c8b78')           # grey-green damp
SOOT = Ramp('#1a1918', '#262422', '#33302d', '#423e39')
MOSS = Ramp('#1f2716', '#2b351c', '#394624', '#4a582d', '#5d6b37')
SALT = Ramp('#9a978e', '#b8b5ac', '#d2d0c8', '#e6e4dd', '#f2f1ec')
CEMENT = Ramp('#2c2b29', '#3c3a37', '#4e4b47', '#615d57', '#736f68', '#86817a', '#98938b', '#a9a49b')
RUSTST = Ramp('#3b2414', '#56331b', '#714424', '#8a5630')                                           # rust stains
# interior paints
BEIGE = Ramp('#4b4032', '#665844', '#837259', '#9d8a6c', '#b19d7d', '#c1ad8b', '#cdba98', '#d7c6a5', '#e0d1b3')
AQUA = Ramp('#2e423d', '#425a53', '#57726a', '#6c8a80', '#819f95', '#93b0a6', '#a2beb4', '#afc9c0', '#bcd3ca')
KCREAM = Ramp('#4a4130', '#665b43', '#837557', '#9d8e69', '#b2a27a', '#c2b289', '#cfc097', '#d9cca5')
PINK = Ramp('#56363d', '#744953', '#925f6a', '#ab7580', '#bd8892', '#cb9aa3', '#d6aab2', '#dfb8bf', '#e8c6cc')
TOTI = Ramp('#161b26', '#1e2432', '#272e3f', '#31394c', '#3b4459', '#465066', '#525d74', '#5f6b82')
WHITEP = Ramp('#4e504f', '#686a68', '#838481', '#9d9d99', '#b3b2ad', '#c5c3bd', '#d3d1ca', '#dedcd5', '#e7e6e0')
LAV = Ramp('#2a2b2b', '#393a3a', '#4b4c4b', '#5d5e5c', '#6f706d', '#81817e', '#92928e', '#a2a19d')   # laundry cement
# wallpapers
NONA_BG = Ramp('#4e4a3b', '#6a654f', '#857f63', '#9c9676', '#afa886', '#bdb693', '#c9c2a0')
NONA_ROSE = Ramp('#4a2a2a', '#6a3a38', '#88504a', '#a0665c', '#b47d70')
NONA_LEAF = Ramp('#2c3324', '#3d4630', '#4f5a3d', '#626d4b')
MAT_BG = Ramp('#4a3d26', '#66532f', '#83693a', '#9d7f46', '#b19352', '#c0a464', '#ccb478')       # 70s mustard
MAT_BR = Ramp('#22140c', '#331f12', '#462b19', '#5a3920', '#6d4627')
MAT_OR = Ramp('#5c2a14', '#7c3a1b', '#9a4b22', '#b35d2b', '#c3713a')
# tiles
AZV = Ramp('#18230f', '#223016', '#2e3f1d', '#3a4e24', '#475e2c', '#556e35', '#64803f', '#76924d', '#8ba35f', '#a2b677')
AZC = Ramp('#33505d', '#456876', '#5a808e', '#6f97a4', '#84abb7', '#97bbc6', '#a9cad3', '#b9d6de', '#c9e2e8')
GROUT = Ramp('#1c1a18', '#2a2723', '#3a362f', '#4c473f', '#615b51', '#777065', '#8b8478')
GUARDA_BR = Ramp('#2a170b', '#3e2310', '#553117', '#6b3f1e')
GUARDA_OR = Ramp('#7a3a12', '#9c4f18', '#b9661f', '#cf7e2c', '#de9a46')
GUARDA_CR = Ramp('#a99c7c', '#c4b893', '#d8cda9', '#e6ddbe', '#f0e9cf')
NAVY = Ramp('#0e1626', '#152036', '#1c2b47', '#263a5c', '#334b70')
# floors
PARQ = Ramp('#22140b', '#321e10', '#442916', '#57351c', '#6a4222', '#7d502a', '#905f33', '#a26f3e', '#b5814b', '#c5945c')
PARQ_W = Ramp('#3a2c1f', '#4f3d2b', '#665038', '#7c6346', '#907555', '#a28764', '#b29874')         # unvarnished, worn
GRAN = Ramp('#3b3833', '#4d4943', '#615c55', '#756f67', '#888279', '#9a948a', '#aba59a', '#bab4a9', '#c7c2b7')
CERAM = Ramp('#4c3a26', '#6a5236', '#886b47', '#a38459', '#b9996b', '#c9ab7d', '#d6bb8f', '#e0c9a0')
CERAM_P = Ramp('#3c1f10', '#5a2d17', '#77401f', '#93552a')
PATIO_R = Ramp('#3a1610', '#521f15', '#6a2a1b', '#7f3621', '#924229', '#a24f31', '#b05d3c', '#bc6c4a')
VAINILLA = Ramp('#4c473b', '#625c4d', '#797261', '#8e8774', '#a19a85', '#b1aa94', '#beb7a1', '#c9c3ad', '#d3cdb8')
GRANITE = Ramp('#2f2f31', '#424244', '#555557', '#68686a', '#7b7a7b', '#8e8c8c', '#a09e9c', '#b1afac')
ASPH = Ramp('#141516', '#1c1d1f', '#252628', '#2f3032', '#3a3b3c', '#464646', '#535351')
GRASS = Ramp('#1b2412', '#25321a', '#304222', '#3c532b', '#496435', '#577540', '#66864b', '#789858')
EARTH = Ramp('#1f1710', '#2c2117', '#3b2c1f', '#4b3828', '#5c4632', '#6e553d')
SAND = Ramp('#4a3f2e', '#5f523c', '#76674c', '#8c7b5d', '#a08e6c', '#b19f7c', '#c0ae8b', '#ccbc99')
# roof
TEJA = Ramp('#3a170c', '#562212', '#732e17', '#8e3b1d', '#a54824', '#b8562c', '#c76636', '#d47843', '#de8c55', '#e7a26c')
LICHEN = Ramp('#56562f', '#6f6d3b', '#8a8649', '#a7a05c', '#c0b36a')
# wood, metal, glass
WOOD_D = Ramp('#120b08', '#1d120c', '#2a1a11', '#372216', '#452b1b', '#543522', '#64402a', '#764e34', '#8a5f40')
CEDRO = Ramp('#1c0d08', '#2b150c', '#3b1d10', '#4c2615', '#5e301b', '#713b21', '#854728', '#985532', '#aa653e')
PINO = Ramp('#2a1d14', '#3f2c1d', '#574029', '#6f5436', '#886844', '#a07d54', '#b69266', '#c9a77b', '#d9bd94')
ENAMEL_W = Ramp('#58564f', '#75736a', '#929086', '#aeab9f', '#c3c0b3', '#d3d0c3', '#dfdcd0', '#e8e6db')  # yellowed white enamel
IRON = Ramp('#0d0d10', '#151418', '#1e1c20', '#28252a', '#343034', '#423d3e', '#544e4c', '#6a625d')
RUST = Ramp('#2e170f', '#462114', '#5e2d18', '#77391d', '#8f4824', '#a85b2e', '#bd7039')
GREEN = Ramp('#0f1a13', '#16241b', '#1e3124', '#273f2e', '#314f39', '#3c6045', '#4a7354', '#5d8866', '#76a07c')
REJA_V = Ramp('#0b120e', '#111b15', '#17251c', '#1e3024', '#273c2d', '#314a37', '#3e5a44')          # dark green rejas
WEATHER = Ramp('#2f2b26', '#433d36', '#58514a', '#6e665d', '#857c71', '#9b9285', '#b0a799')
GLASS = Ramp('#141c1f', '#222d31', '#334247', '#46585d', '#5c7074', '#788b8d', '#9cadad', '#c3d0ce', '#e4ece8')
BRASS = Ramp('#2b1d0b', '#47310f', '#664a17', '#866424', '#a37f35', '#bf9b4b', '#d6b768', '#ead290')
CHROME = Ramp('#1f2124', '#33363a', '#4b4f54', '#666a70', '#83878c', '#a2a5a9', '#c2c4c6', '#e0e1e2')
ENAMEL = Ramp('#3d4148', '#6f747b', '#a3a8ad', '#c9cdd0', '#e2e4e4', '#f1f2ef')
GALV = Ramp('#2a2c2e', '#3b3e41', '#4f5256', '#64676b', '#7a7d80', '#8f9294', '#a4a6a7', '#b8b9b9')    # galvanised sheet
CAL = RENDER_W  # alias used by copied helpers
STONE = GRANITE

# =============================================================================================== material adapters
_VMAP = {}


def cube_mat(painter):
    """painter(v) -> (32, 32, 4) uint8 for variant v. Returns a bkit material picking the variant from ctx.seed."""
    cache = {}

    def mat(ctx):
        key = ctx.block.key
        vm = _VMAP.get(key)
        if vm is None:
            vm = {}
            for v in range(max(1, ctx.block.variants)):
                for f in FACES:
                    vm.setdefault(shash(key, v, f), v)
            _VMAP[key] = vm
        v = vm.get(ctx.seed, 0)
        a = cache.get(v)
        if a is None:
            a = cache[v] = painter(v)
        p = a[ctx.j % a.shape[0], ctx.i % a.shape[1]]
        return (int(p[0]), int(p[1]), int(p[2]), int(p[3]))
    return mat


def face_mat(painter):
    """painter(face, w, h, part) -> (h, w, 4) uint8 (alpha 0 = transparent). One cached image per part face."""
    cache = {}

    def mat(ctx):
        k = (ctx.block.key, id(ctx.part), ctx.face)
        a = cache.get(k)
        if a is None:
            a = cache[k] = painter(ctx.face, ctx.w, ctx.h, ctx.part)
        p = a[ctx.j, ctx.i]
        if p[3] == 0:
            return None
        return (int(p[0]), int(p[1]), int(p[2]), int(p[3]))
    return mat


def face_coords(part, face, w, h):
    """Block-space (x, y, z) arrays of every texel centre of a part face."""
    s = (np.arange(w) + 0.5) / w
    t = (np.arange(h) + 0.5) / h
    S, T = np.meshgrid(s, t)
    (x1, y1, z1), (x2, y2, z2) = part.frm, part.to
    W, H, D = x2 - x1, y2 - y1, z2 - z1
    if face == 'north':
        return x2 - S * W, y2 - T * H, np.full_like(S, z1)
    if face == 'south':
        return x1 + S * W, y2 - T * H, np.full_like(S, z2)
    if face == 'west':
        return np.full_like(S, x1), y2 - T * H, z1 + S * D
    if face == 'east':
        return np.full_like(S, x2), y2 - T * H, z2 - S * D
    if face == 'up':
        return x1 + S * W, np.full_like(S, y2), z1 + T * D
    return x1 + S * W, np.full_like(S, y1), z2 - T * D


def aligned_uv(part, face, w, h):
    """Texel coords (i, j) in a 32 px block texture that a full cube face at the same place would use."""
    x, y, z = face_coords(part, face, w, h)
    if face == 'north':
        u, v = (16 - x) * 2, (16 - y) * 2
    elif face == 'south':
        u, v = x * 2, (16 - y) * 2
    elif face == 'west':
        u, v = z * 2, (16 - y) * 2
    elif face == 'east':
        u, v = (16 - z) * 2, (16 - y) * 2
    elif face == 'up':
        u, v = x * 2, z * 2
    else:
        u, v = x * 2, (16 - z) * 2
    return np.floor(u).astype(int) % N, np.floor(v).astype(int) % N


def aligned(tex):
    """Face painter sampling a 32 px block texture in block space (so trims/arches continue the walls)."""
    def p(face, w, h, part):
        i, j = aligned_uv(part, face, w, h)
        return tex[j, i]
    return p


_TEX = {}


def T(name, v=0):
    """Memoised texture lookup by painter name (used by furniture that reuses wall/floor textures)."""
    k = (name, v)
    if k not in _TEX:
        _TEX[k] = PAINTERS[name](v)
    return _TEX[k]


PAINTERS = {}


def painter(name):
    def deco(fn):
        PAINTERS[name] = fn
        return fn
    return deco

# =============================================================================================== pixel font
FONT = {
    'A': ['.###.', '#...#', '#...#', '#####', '#...#', '#...#', '#...#'],
    'B': ['####.', '#...#', '#...#', '####.', '#...#', '#...#', '####.'],
    'C': ['.###.', '#...#', '#....', '#....', '#....', '#...#', '.###.'],
    'D': ['####.', '#...#', '#...#', '#...#', '#...#', '#...#', '####.'],
    'E': ['#####', '#....', '#....', '####.', '#....', '#....', '#####'],
    'F': ['#####', '#....', '#....', '####.', '#....', '#....', '#....'],
    'G': ['.###.', '#...#', '#....', '#.###', '#...#', '#...#', '.####'],
    'H': ['#...#', '#...#', '#...#', '#####', '#...#', '#...#', '#...#'],
    'I': ['###', '.#.', '.#.', '.#.', '.#.', '.#.', '###'],
    'J': ['..###', '...#.', '...#.', '...#.', '#..#.', '#..#.', '.##..'],
    'K': ['#...#', '#..#.', '#.#..', '##...', '#.#..', '#..#.', '#...#'],
    'L': ['#....', '#....', '#....', '#....', '#....', '#....', '#####'],
    'M': ['#...#', '##.##', '#.#.#', '#.#.#', '#...#', '#...#', '#...#'],
    'N': ['#...#', '##..#', '#.#.#', '#..##', '#...#', '#...#', '#...#'],
    'O': ['.###.', '#...#', '#...#', '#...#', '#...#', '#...#', '.###.'],
    'P': ['####.', '#...#', '#...#', '####.', '#....', '#....', '#....'],
    'Q': ['.###.', '#...#', '#...#', '#...#', '#.#.#', '#..#.', '.##.#'],
    'R': ['####.', '#...#', '#...#', '####.', '#.#..', '#..#.', '#...#'],
    'S': ['.####', '#....', '#....', '.###.', '....#', '....#', '####.'],
    'T': ['#####', '..#..', '..#..', '..#..', '..#..', '..#..', '..#..'],
    'U': ['#...#', '#...#', '#...#', '#...#', '#...#', '#...#', '.###.'],
    'V': ['#...#', '#...#', '#...#', '#...#', '#...#', '.#.#.', '..#..'],
    'W': ['#...#', '#...#', '#...#', '#.#.#', '#.#.#', '##.##', '#...#'],
    'X': ['#...#', '#...#', '.#.#.', '..#..', '.#.#.', '#...#', '#...#'],
    'Y': ['#...#', '#...#', '.#.#.', '..#..', '..#..', '..#..', '..#..'],
    'Z': ['#####', '....#', '...#.', '..#..', '.#...', '#....', '#####'],
    '0': ['.###.', '#...#', '#..##', '#.#.#', '##..#', '#...#', '.###.'],
    '1': ['.#.', '##.', '.#.', '.#.', '.#.', '.#.', '###'],
    '2': ['.###.', '#...#', '....#', '...#.', '..#..', '.#...', '#####'],
    '3': ['####.', '....#', '....#', '.###.', '....#', '....#', '####.'],
    '4': ['...#.', '..##.', '.#.#.', '#..#.', '#####', '...#.', '...#.'],
    '5': ['#####', '#....', '####.', '....#', '....#', '#...#', '.###.'],
    '6': ['.###.', '#....', '#....', '####.', '#...#', '#...#', '.###.'],
    '7': ['#####', '....#', '...#.', '..#..', '.#...', '.#...', '.#...'],
    '8': ['.###.', '#...#', '#...#', '.###.', '#...#', '#...#', '.###.'],
    '9': ['.###.', '#...#', '#...#', '.####', '....#', '....#', '.###.'],
    ' ': ['...', '...', '...', '...', '...', '...', '...'],
    '.': ['.', '.', '.', '.', '.', '.', '#'],
    ',': ['..', '..', '..', '..', '..', '.#', '#.'],
    '-': ['....', '....', '....', '####', '....', '....', '....'],
    '+': ['.....', '..#..', '..#..', '#####', '..#..', '..#..', '.....'],
    '=': ['....', '....', '####', '....', '####', '....', '....'],
    '·': ['.', '.', '.', '#', '.', '.', '.'],
    '°': ['.#.', '#.#', '.#.', '...', '...', '...', '...'],
    '!': ['#', '#', '#', '#', '#', '.', '#'],
    '?': ['.###.', '#...#', '....#', '...#.', '..#..', '.....', '..#..'],
    "'": ['#', '#', '.', '.', '.', '.', '.'],
    '/': ['....#', '...#.', '...#.', '..#..', '.#...', '.#...', '#....'],
    '♥': ['.#.#.', '#####', '#####', '#####', '.###.', '..#..', '.....'],
}
ACCENT = {'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U'}


def glyph(ch):
    """Glyph rows for ch; accented capitals get a 2-row accent on top (returned glyph is 9 rows tall)."""
    if ch in ACCENT:
        g = FONT[ACCENT[ch]]
        w = len(g[0])
        acc = ['.' * (w // 2 + 1) + '#' + '.' * (w - w // 2 - 2), '.' * (w // 2) + '#' + '.' * (w - w // 2 - 1)]
        acc = [a[:w] for a in acc]
        return acc + g
    if ch == 'Ñ':
        g = FONT['N']
        return ['.#.#.', '#.#..'] + g
    g = FONT.get(ch, FONT['?'])
    return ['.' * len(g[0])] * 2 + g


def text_mask(text, spacing=1, scale_x=1, scale_y=1):
    """Render text with the pixel font: returns a bool array (9*scale_y rows: 2 accent rows + 7 cap rows)."""
    cols = []
    for k, ch in enumerate(text):
        g = glyph(ch)
        arr = np.array([[c == '#' for c in row] for row in g], bool)
        arr = np.repeat(np.repeat(arr, scale_y, 0), scale_x, 1)
        cols.append(arr)
        if k < len(text) - 1:
            cols.append(np.zeros((arr.shape[0], spacing), bool))
    return np.concatenate(cols, 1)


def stamp(dst, m, x, y):
    """OR a small mask into a bigger one at (x, y) (clipped)."""
    h, w = m.shape
    H, W = dst.shape
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + w), min(H, y + h)
    if x1 > x0 and y1 > y0:
        dst[y0:y1, x0:x1] |= m[y0 - y:y1 - y, x0 - x:x1 - x]
    return dst


# =============================================================================================== base painters
def cweight(w=N, h=N, p=0.6):
    """0 on the border, 1 in the middle, rounded iso-lines (variant blending without square artefacts)."""
    Y, X = np.mgrid[0:h, 0:w]
    return (np.sin(math.pi * (X + 0.5) / w) * np.sin(math.pi * (Y + 0.5) / h)) ** p


def rank(n):
    """Histogram-equalise a field to 0..1 (thresholds then mean area fractions)."""
    r = n.ravel().argsort().argsort().reshape(n.shape)
    return r / max(1, n.size - 1)


def cblend(common, var, p=0.6):
    t = cweight(common.shape[1], common.shape[0], p)
    return rank(common) * (1 - t) + rank(var) * t


def poisson(seed, count, mind, w=N, h=N, keep=None, wrap=True):
    """Blue-noise points (periodic distance). keep(x, y) -> bool filters candidate positions."""
    rng = np.random.default_rng(seed)
    pts = []
    tries = 0
    while len(pts) < count and tries < count * 60:
        tries += 1
        x, y = rng.uniform(0, w), rng.uniform(0, h)
        if keep is not None and not keep(x, y):
            continue
        ok = True
        for (px, py) in pts:
            dx, dy = abs(px - x), abs(py - y)
            if wrap:
                dx, dy = min(dx, w - dx), min(dy, h - dy)
            if dx * dx + dy * dy < mind * mind:
                ok = False
                break
        if ok:
            pts.append((x, y))
    return [(int(x), int(y)) for x, y in pts]


# little hand-drawn relief clumps for render/plaster (body pixels '#'; the light catches the pixel above each column)
CLUMPS = [['##'], ['###'], ['.##', '##.'], ['##.', '.##'], ['##', '#.'], ['#'], ['###', '.#.'], ['.#', '##'], ['##']]


def relief(idx, seed_common, seed_var, count=26, mind=5.0, body=-1, light=1, shade=0, edge=4, w=N, h=N):
    """Scatter hand-drawn clumps: darker body, lit top rim (and optional shaded bottom). Border clumps are shared by
    every variant (same seed) so variants tile together."""
    bd = border_dist(w, h)
    near = poisson(seed_common, int(count * 0.55), mind, w, h, keep=lambda x, y: bd[int(y), int(x)] < edge)
    far = poisson(seed_var, int(count * 0.6), mind, w, h, keep=lambda x, y: bd[int(y), int(x)] >= edge + 2)
    rng = np.random.default_rng(seed_var + 3)
    rngc = np.random.default_rng(seed_common + 3)
    out = idx.copy()
    for pts, r in ((near, rngc), (far, rng)):
        for (x, y) in pts:
            st = CLUMPS[r.integers(0, len(CLUMPS))]
            for j, row in enumerate(st):
                for i, ch in enumerate(row):
                    if ch == '#':
                        X, Y = (x + i) % w, (y + j) % h
                        out[Y, X] += body
                        above = st[j - 1][i] if j > 0 and i < len(st[j - 1]) else '.'
                        if above != '#':
                            out[(Y - 1) % h, X] += light - body if False else light
                        below = st[j + 1][i] if j + 1 < len(st) and i < len(st[j + 1]) else '.'
                        if shade and below != '#':
                            out[(Y + 1) % h, X] += shade
    return out


def lime_idx(v, base=6, seed=0, rough=1.0, big=1):
    """Whitewashed lime plaster: very soft large tonal shapes, a stucco relief of small clumps, pits."""
    common = fbm(N, N, 7001 + seed, cells=2, octaves=3)
    var = fbm(N, N, 7100 + seed + 37 * v, cells=2, octaves=3)
    n = cblend(common, var)
    idx = posterize(n, [(0.80, big), (0.14, -big)], base)
    # mid-scale mottling (3-6 px organic clusters), one step only
    m2 = cblend(fbm(N, N, 7003 + seed, cells=4, octaves=3), fbm(N, N, 7300 + seed + 37 * v, cells=4, octaves=3))
    idx += np.where((m2 > 0.84) & (idx <= base), 1, 0) - np.where((m2 < 0.06) & (idx >= base), 1, 0)
    if rough:
        idx = relief(idx, 7400 + seed, 7500 + seed + 37 * v, count=int(18 * rough), mind=5.5, body=-1, light=1)
        pits = poisson(7600 + seed + 37 * v, int(5 * rough), 8, keep=lambda x, y: border_dist(N, N)[int(y), int(x)] >= 3)
        for (x, y) in pits:
            idx[y, x] -= 2
            idx[(y + 1) % N, x] += 1
    return idx


def brick_layout(course=8, mortar=2, lengths=(15, 17), offset=8, seed=1, w=N, h=N):
    """Colonial handmade brick bond: returns (labels, mortar_mask). Periodic in 32."""
    lab = -np.ones((h, w), int)
    rng = np.random.default_rng(seed)
    n = 0
    for r in range(h // course):
        y0 = r * course
        x = (r * offset) % w
        # bricks along the row until we wrap (lengths alternate so the row closes exactly at 32)
        L = list(lengths) if sum(lengths) == w else [w // 2, w - w // 2]
        for k, ln in enumerate(L):
            for yy in range(y0, y0 + course - mortar):
                for xx in range(x, x + ln - mortar):
                    lab[yy % h, xx % w] = n
            x += ln
            n += 1
    return lab, lab < 0


def paint_bricks(cv, mask=None, seed=3, ramp=BRICK, mramp=MORTAR, base=4, course=8, mortar=2, lengths=(15, 17),
                 offset=8):
    lab, mor = brick_layout(course, mortar, lengths, offset, seed)
    rng = np.random.default_rng(seed)
    nbk = lab.max() + 1
    tone = rng.choice([-2, -1, -1, 0, 0, 0, 1, 1], nbk)
    idx = np.where(lab >= 0, base + tone[np.maximum(lab, 0)], 0)
    n = fbm(N, N, seed + 50, cells=4, octaves=3, ax=1.6)
    idx += posterize(n, [(0.66, 1), (0.34, -1)])
    idx = bevel(idx, lab, hi=1, lo=-1)
    # pitted, sandy faces: small dark specks with a light grain above
    sp = poisson(seed + 77, 22, 3.2)
    for (x, y) in sp:
        if lab[y, x] >= 0 and lab[(y + 1) % N, x] == lab[y, x]:
            idx[y, x] -= 1
            idx[(y + 1) % N, x] -= 1 if (x + y) % 3 == 0 else 0
    # chipped arrises on some bricks (corner bites showing the mortar colour)
    m = np.ones((N, N), bool) if mask is None else mask
    cv.put(ramp, idx, m & (lab >= 0))
    # mortar: recessed (darker right under each brick), crumbly
    midx = np.full((N, N), 3) + posterize(fbm(N, N, seed + 9, cells=8, octaves=2), [(0.62, 1), (0.34, -1)])
    midx -= (nb(lab, 1, 0) >= 0).astype(int)  # shadow under the brick above
    midx += ((nb(lab, -1, 0) >= 0) & (nb(lab, 1, 0) < 0)).astype(int)  # lit ledge on top of the brick below
    cv.put(mramp, midx, m & mor)
    return lab

def flake(cx, cy, rx, ry, seed, jag=0.45):
    """Jagged flake outline: an ellipse displaced by coarse + fine noise."""
    Y, X = np.mgrid[0:N, 0:N]
    d = np.sqrt(((X + 0.5 - cx) / rx) ** 2 + ((Y + 0.5 - cy) / ry) ** 2)
    n1 = fbm(N, N, seed, cells=3, octaves=2)
    n2 = fbm(N, N, seed + 1, cells=8, octaves=2)
    m = d + (n1 - 0.5) * 0.8 + (n2 - 0.5) * jag * 2 < 1
    # clean single-pixel spurs
    cnt = sum(nb(m, dy, dx, False).astype(int) for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)))
    return (m & (cnt >= 2)) | (~m & (cnt >= 4))


def grain_profile(n, seed, tones=(-1, 0, 0, 0, 1), runs=(1, 4)):
    """1-D tone profile across the grain: runs of 1-4 px, never two equal tones in a row."""
    rng = np.random.default_rng(seed)
    out = np.zeros(n, int)
    i, last = 0, None
    while i < n:
        t = tones[rng.integers(0, len(tones))]
        if t == last:
            continue
        L = int(rng.integers(runs[0], runs[1] + 1))
        out[i:i + L] = t
        i += L
        last = t
    return out


def wood_grain(w, h, seed, along='y', warp=1.6, pores=0.04, tones=(-1, 0, 0, 0, 1), period=True):
    """Long wavy streaks (tone offsets) + short dark pores. along='y': grain runs vertically."""
    if along == 'x':
        return wood_grain(h, w, seed, 'y', warp, pores, tones, period).T
    prof = grain_profile(w * 2, seed, tones)
    if period:
        prof = prof[:w]
    wv = vnoise(1, h, 1, max(1, h // 10), seed + 1)[:, 0] - 0.5
    wv2 = vnoise(1, h, 1, max(1, h // 4), seed + 2)[:, 0] - 0.5
    Y, X = np.mgrid[0:h, 0:w]
    sway = vnoise(w, 1, max(1, w // 8), 1, seed + 3)[0]  # different columns sway differently
    u = X + np.round((wv[Y] * 2 * warp + wv2[Y] * 0.8) * (0.5 + sway[X])).astype(int)
    g = prof[u % len(prof)]
    rng = np.random.default_rng(seed + 4)
    pm = np.zeros((h, w), bool)
    for _ in range(int(w * h * pores / 3)):
        x, y = int(rng.integers(0, w)), int(rng.integers(0, h))
        for k in range(int(rng.integers(2, 4))):
            pm[(y + k) % h, x] = True
    return g - pm.astype(int)


def raised_panel(idx, x0, y0, x1, y1, bev, field_idx, hi=(2, 1), lo=(-2, -1)):
    """Raised panel inside the opening [x0..x1]x[y0..y1]: mitred bevels of width bev (top, left lit; bottom,
    right shaded), the flat field painted with field_idx."""
    h, w = idx.shape
    Y, X = np.mgrid[0:h, 0:w]
    inside = (X >= x0) & (X <= x1) & (Y >= y0) & (Y <= y1)
    dt, db, dl, dr = Y - y0, y1 - Y, X - x0, x1 - X
    field = inside & (dt >= bev) & (db >= bev) & (dl >= bev) & (dr >= bev)
    m = np.minimum(np.minimum(dt, db), np.minimum(dl, dr))
    top = inside & ~field & (dt == m)
    bot = inside & ~field & (db == m) & ~top
    left = inside & ~field & (dl == m) & ~top & ~bot
    right = inside & ~field & ~top & ~bot & ~left
    out = np.where(field, field_idx, idx)
    out = np.where(top, field_idx + hi[0], out)
    out = np.where(left, field_idx + hi[1], out)
    out = np.where(bot, field_idx + lo[0], out)
    out = np.where(right, field_idx + lo[1], out)
    # crisp field edge (arris) catches the light at the top, sinks at the bottom
    fr = rim(field, wrap=False)
    out = np.where(fr['in_top'], out + 1, out)
    out = np.where(fr['in_bot'], out - 1, out)
    return out, field, inside


def frame_opening(idx, x0, y0, x1, y1):
    """Sticking moulding round a frame opening: the frame casts a shadow on top/left, lit lip bottom/right."""
    h, w = idx.shape
    Y, X = np.mgrid[0:h, 0:w]
    out = idx.copy()
    out = np.where((Y == y0) & (X >= x0) & (X <= x1), 1, out)
    out = np.where((X == x0) & (Y >= y0) & (Y <= y1), np.minimum(out, 2), out)
    out = np.where((Y == y1) & (X >= x0) & (X <= x1), out + 1, out)
    out = np.where((X == x1) & (Y > y0) & (Y <= y1), out + 1, out)
    return out


def fkey(part, face):
    return shash(part.frm, part.to, face) % 9973


def face_axis(face, w, h, along=None):
    if along:
        return along
    return 'x' if w >= h else 'y'


def border_px(w, h):
    Y, X = np.mgrid[0:h, 0:w]
    return np.minimum(np.minimum(X, w - 1 - X), np.minimum(Y, h - 1 - Y)), X, Y


def pp_plaster(name='revoque_blanco', v=0):
    """Plaster continuing the walls (texture sampled in block space)."""
    return aligned(T(name, v))


def pp_wood(ramp=WOOD_D, base=4, seed=0, along=None, out=-1, top=1, grain_on=True, dark_ends=True):
    """Solid wood: grain along the long axis, 1 px darker outline (crisp edges), lit top arris on vertical faces."""
    def p(face, w, h, part):
        al = face_axis(face, w, h, along)
        idx = np.full((h, w), base)
        if grain_on and max(w, h) > 2:
            idx = idx + wood_grain(w, h, seed + fkey(part, face), al, period=False, pores=0.03)
        bd, X, Y = border_px(w, h)
        if out and min(w, h) > 2:
            idx = np.where(bd == 0, idx + out, idx)
        if top and face not in ('up', 'down') and h > 2:
            idx = np.where((Y == 0) & (X > 0) & (X < w - 1), idx + top + 1, idx)
        if dark_ends and face in ('up', 'down') and min(w, h) <= 3:
            idx = idx + 1
        cv = Cv(w, h)
        cv.put(ramp, idx)
        return cv.out()
    return p


def pp_paint(ramp=GREEN, base=4, seed=0, chip=0.22, louvers=False, along=None, out=-1):
    """Old oil-painted wood (shutters): flat paint with brush streaks, chips showing grey bare wood."""
    def p(face, w, h, part):
        al = face_axis(face, w, h, along)
        k = seed + fkey(part, face)
        g = wood_grain(w, h, k, al, period=False, pores=0.0, tones=(0, 0, 0, 1, -1))
        idx = base + np.where(np.abs(g) > 0, np.sign(g), 0) * (np.arange(w)[None, :] % 3 == 0 if al == 'y' else np.arange(h)[:, None] % 3 == 0)
        bd, X, Y = border_px(w, h)
        if louvers and face in ('north', 'south') and h > 4:
            ph = Y % 3
            idx = np.where(ph == 0, base + 2, np.where(ph == 2, base - 2, base))
            idx = np.where(bd == 0, base - 1, idx)
        if out and min(w, h) > 2:
            idx = np.where(bd == 0, idx + out, idx)
        cv = Cv(w, h)
        cv.put(ramp, idx)
        if chip and min(w, h) > 2:
            n = fbm(w, h, k + 7, cells=max(1, w // 6), octaves=2) if w >= 6 and h >= 6 else np.zeros((h, w))
            ch = n > 1 - chip * 0.6
            ch |= (bd == 0) & (fbm(w, h, k + 9, cells=max(1, w // 3), octaves=1) > 1 - chip) if w >= 3 and h >= 3 else False
            widx = 3 + wood_grain(w, h, k + 11, al, period=False)
            cv.put(WEATHER, widx, ch)
            r = rim(ch, wrap=False)
            cv.put(ramp, np.full((h, w), base + 2), r['out_below'] & ~ch)
        return cv.out()
    return p


def pp_iron(base=3, seed=0, rust=0.25, out=-1, top=2):
    def p(face, w, h, part):
        k = seed + fkey(part, face)
        idx = np.full((h, w), base)
        bd, X, Y = border_px(w, h)
        if min(w, h) > 2:
            idx = idx + posterize(fbm(w, h, k, cells=max(1, w // 4), octaves=2) if w >= 4 and h >= 4 else np.full((h, w), 0.5), [(0.7, 1), (0.3, -1)])
            idx = np.where(bd == 0, idx + out, idx)
        if face not in ('up', 'down'):
            idx = np.where(Y == 0, idx + top, idx)
        else:
            idx = idx + 1
        cv = Cv(w, h)
        cv.put(IRON, idx)
        if rust and w * h >= 4:
            n = vnoise(w, h, max(2, w // 2), max(2, h // 2), k + 5)
            rm = n > 1 - rust * 0.45
            ridx = 2 + (n > 1 - rust * 0.2).astype(int)
            cv.put(RUST, ridx, rm)
        return cv.out()
    return p


def pp_glass(seed=0, alpha=96, clip=None, dirt=0.6, crack=None, frosted=False):
    """Old window glass: blue-grey tint, a couple of diagonal reflection streaks, grime gathering at the bottom and
    in the corners. clip(x, y, z) -> bool mask of texels to keep. crack: (cx, cy) impact point in face pixels."""
    def p(face, w, h, part):
        x, y, z = face_coords(part, face, w, h)
        cv = Cv(w, h)
        bd, X, Y = border_px(w, h)
        k = seed + fkey(part, face)
        idx = np.full((h, w), 4 if not frosted else 6)
        a = np.full((h, w), float(alpha if not frosted else 215))
        # one soft diagonal glint per pane, drawn in block space so the front and back faces coincide (no X), its
        # position and slope varied per pane, low contrast
        pk = shash(part.frm, part.to, seed) % 997
        u = z if face in ('west', 'east') else x
        sl = 0.8 + 0.5 * ((pk % 7) / 6.0)
        t0 = 0.3 + 0.4 * ((pk % 101) / 100.0)
        c0 = u.min() + sl * y.min() + t0 * ((u.max() - u.min()) + sl * (y.max() - y.min()))
        g = np.clip(1 - np.abs(u + sl * y - c0) / 1.1, 0, 1)
        idx = idx + g * 1.6
        a = a + g * 22
        # grime: bottom band + corners
        g = (1 - (y - y.min()) / max(1e-3, (y.max() - y.min()))) if h > 1 else np.zeros((h, w))
        n = fbm(w, h, k, cells=max(1, w // 6), octaves=2) if w >= 6 and h >= 6 else np.full((h, w), 0.5)
        gr = (g * dirt + (bd < 2) * 0.35 + (n - 0.5) * 0.4) > 0.55
        cv.put(GLASS, idx, None, a)
        cv.tint('#4a4232', np.where(gr, 0.55, 0.0))
        cv.a = np.where(gr, np.maximum(cv.a, 185), cv.a)
        if crack is not None:
            cx, cy = crack
            rng = np.random.default_rng(k)
            cm = np.zeros((h, w), bool)
            for ang in rng.uniform(0, 2 * math.pi, 6):
                L = rng.uniform(4, max(w, h))
                pts = wander([(cx, cy), (cx + math.cos(ang) * L, cy + math.sin(ang) * L)], k + int(ang * 100), amp=1.0)
                cm |= path_mask(pts, w, h, wrap=False)
            cv.put(GLASS, np.full((h, w), 8), cm, 235)
            hole = (X - cx) ** 2 + (Y - cy) ** 2 < 5
            cv.a = np.where(hole, 0, cv.a)
        if clip is not None:
            cv.a = np.where(clip(x, y, z), cv.a, 0)
        return cv.out()
    return p


def pp_fn(fn):
    """Painter from fn(face, w, h, part, cv) that paints into a fresh canvas."""
    def p(face, w, h, part):
        cv = Cv(w, h)
        fn(face, w, h, part, cv)
        return cv.out()
    return p


def P(frm, to, painter, **kw):
    return box(frm, to, face_mat(painter), **kw)


def PL(frm, to, painter, **kw):
    return plane(frm, to, face_mat(painter), **kw)


# =============================================================================================== DOORS
TINY = {  # 5-row condensed font for small plates (variable width)
    'A': ['.#.', '#.#', '###', '#.#', '#.#'], 'B': ['##.', '#.#', '##.', '#.#', '##.'], 'C': ['##', '#.', '#.', '#.', '##'],
    'D': ['##.', '#.#', '#.#', '#.#', '##.'], 'E': ['##', '#.', '##', '#.', '##'], 'I': ['#', '#', '#', '#', '#'],
    'N': ['#..#', '##.#', '#.##', '#..#', '#..#'], 'O': ['###', '#.#', '#.#', '#.#', '###'], 'R': ['##.', '#.#', '##.', '#.#', '#.#'],
    'S': ['##', '#.', '##', '.#', '##'], 'T': ['###', '.#.', '.#.', '.#.', '.#.'], 'L': ['#.', '#.', '#.', '#.', '##'],
    'Ó': ['###', '#.#', '#.#', '#.#', '###'], 'U': ['#.#', '#.#', '#.#', '#.#', '###'], 'M': ['#.#', '###', '###', '#.#', '#.#'],
    'P': ['##.', '#.#', '##.', '#..', '#..'], 'G': ['##.', '#..', '#.#', '#.#', '###'], 'V': ['#.#', '#.#', '#.#', '#.#', '.#.'],
    ' ': ['.', '.', '.', '.', '.'], '°': ['#', '.', '.', '.', '.'],
    '0': ['###', '#.#', '#.#', '#.#', '###'], '1': ['#', '#', '#', '#', '#'], '2': ['##', '.#', '##', '#.', '##'],
    '3': ['##', '.#', '##', '.#', '##'], '4': ['#.#', '#.#', '###', '..#', '..#'], '5': ['##', '#.', '##', '.#', '##'],
    '6': ['##', '#.', '##', '##', '##'], '7': ['##', '.#', '.#', '.#', '.#'], '8': ['###', '#.#', '###', '#.#', '###'],
    '9': ['###', '#.#', '###', '..#', '..#'], '-': ['..', '..', '##', '..', '..'], '.': ['.', '.', '.', '.', '#'],
    'Ñ': ['#..#', '##.#', '#.##', '#..#', '#..#'],
    'F': ['##', '#.', '##', '#.', '#.'], 'H': ['#.#', '#.#', '###', '#.#', '#.#'], 'J': ['.#', '.#', '.#', '.#', '##'],
    'K': ['#.#', '##.', '#..', '##.', '#.#'], 'Q': ['###', '#.#', '#.#', '###', '..#'], 'W': ['#...#', '#...#', '#.#.#', '#.#.#', '.#.#.'],
    'X': ['#.#', '#.#', '.#.', '#.#', '#.#'], 'Y': ['#.#', '#.#', '.#.', '.#.', '.#.'], 'Z': ['###', '..#', '.#.', '#..', '###'],
    'Á': ['.#.', '#.#', '###', '#.#', '#.#'], 'É': ['##', '#.', '##', '#.', '##'], 'Í': ['#', '#', '#', '#', '#'],
    'Ú': ['#.#', '#.#', '#.#', '#.#', '###'], '·': ['.', '.', '#', '.', '.'], '+': ['...', '.#.', '###', '.#.', '...'],
    '/': ['..#', '..#', '.#.', '#..', '#..'], ',': ['.', '.', '.', '#', '#'],
}


def tiny_mask(text):
    """Returns (mask 6 rows: 1 accent row + 5, width)."""
    cols = []
    for k, ch in enumerate(text):
        g = TINY.get(ch, TINY[' '])
        arr = np.array([[c == '#' for c in row] for row in g], bool)
        acc = np.zeros((1, arr.shape[1]), bool)
        if ch in ('Ó', 'Á', 'É', 'Í', 'Ú'):
            acc[0, min(arr.shape[1] - 1, arr.shape[1] // 2 + (arr.shape[1] > 2))] = True
        if ch == 'Ñ':
            acc[0, :] = True
        cols.append(np.vstack([acc, arr]))
        if k < len(text) - 1:
            cols.append(np.zeros((6, 1), bool))
    return np.concatenate(cols, 1)


def door_mat(painter):
    cache = {}

    def mat(ctx):
        if 'img' not in cache:
            cache['img'] = painter()
        a = cache['img']
        j = ctx.j + (0 if ctx.face == 'top' else 32)
        p = a[j % 64, ctx.i % 32]
        if p[3] == 0:
            return None
        return (int(p[0]), int(p[1]), int(p[2]), int(p[3]))
    return mat


def door_base(ramp=WOOD_D, seed=0, base=4):
    """Canvas, grain maps, coordinates for a 32x64 door (row 0 = top of the upper half)."""
    cv = Cv(32, 64)
    gv = wood_grain(32, 64, seed + 1, 'y')
    gh = wood_grain(32, 64, seed + 2, 'x')
    return cv, cv.X, cv.Y, gv, gh


def door_glass(cv, m, seed, alpha=105):
    X, Y = cv.X, cv.Y
    idx = np.full(m.shape, 4)
    dg = (X + Y) % 13
    st = ((dg == 3) | (dg == 4) | (dg == 7)) & ((X + Y) % 26 < 13)
    idx = np.where(st, 7, idx)
    a = np.where(st, alpha + 70, alpha)
    cv.put(GLASS, idx, m, a)
    ys = Y[m]
    if ys.size:
        y0, y1 = ys.min(), ys.max()
        t = (Y - y0) / max(1, y1 - y0)
        n = fbm(32, 64, seed, cells=4, octaves=2)
        gr = m & ((t * 0.9 + (n - 0.5) * 0.5) > 0.72)
        cv.tint('#4a4232', np.where(gr, 0.55, 0))
        cv.a = np.where(gr, 190, cv.a)


def enamel_plate(cv, x0, y0, w, h, text_mask_, ink='#1f2b4c', base=ENAMEL, screws=True, chip=None):
    X, Y = cv.X, cv.Y
    m = (X >= x0) & (X < x0 + w) & (Y >= y0) & (Y < y0 + h)
    r = rim(m, wrap=False)
    idx = np.full(m.shape, 4) + (Y == y0 + 1) - ((Y == y0 + h - 2) & m)
    idx = np.where(r['in_top'] | r['in_left'] | r['in_bot'] | r['in_right'], 1, idx)
    cv.put(base, idx, m)
    tm = np.zeros(m.shape, bool)
    th, tw = text_mask_.shape
    stamp(tm, text_mask_, x0 + (w - tw) // 2, y0 + (h - th) // 2)
    cv.col(ink, tm & m)
    if screws:
        for (sx, sy) in ((x0 + 1, y0 + 1), (x0 + w - 2, y0 + h - 2)):
            cv.put(BRASS, np.full(m.shape, 5), (X == sx) & (Y == sy))
    if chip:
        cx, cy = chip
        cv.put(IRON, np.full(m.shape, 2), (np.abs(X - cx) + np.abs(Y - cy) <= 1) & m & ~tm)
    cv.put(WOOD_D, np.full(m.shape, 1), r['out_below'] | r['out_right'])  # shadow of the plate


def lever_handle(cv, x, y, keyhole=True):
    X, Y = cv.X, cv.Y
    rose = (X - x) ** 2 + (Y - y) ** 2 <= 2.3
    cv.put(BRASS, np.full(X.shape, 4) + ((Y < y) & rose) - ((Y > y) & rose), rose)
    lev = (Y >= y - 0) & (Y <= y + 1) & (X >= x - 5) & (X <= x)
    cv.put(BRASS, np.full(X.shape, 5) + (Y == y) * 2 - (Y == y + 1), lev)
    cv.put(WOOD_D, np.full(X.shape, 1), (Y == y + 2) & (X >= x - 5) & (X <= x - 1))
    if keyhole:
        esc = (X >= x - 1) & (X <= x + 1) & (Y >= y + 4) & (Y <= y + 7)
        cv.put(BRASS, np.full(X.shape, 4) + (Y == y + 4), esc)
        cv.col('#0b0807', (X == x) & (Y >= y + 5) & (Y <= y + 6))


def scroll_mask(w, h, cx, cy, r0, turns=1.6, thick=0.7, flip=False):
    """A spiral C-scroll (iron) centred at cx, cy."""
    Y, X = np.mgrid[0:h, 0:w]
    dx, dy = X + 0.5 - cx, Y + 0.5 - cy
    if flip:
        dx = -dx
    r = np.sqrt(dx * dx + dy * dy)
    th = (np.arctan2(dy, dx) + 2 * np.pi) % (2 * np.pi)
    m = np.zeros((h, w), bool)
    for k in range(int(turns) + 1):
        rr = r0 * (1 - (th + 2 * np.pi * k) / (2 * np.pi * (turns + 0.6)))
        m |= (np.abs(r - rr) < thick) & (rr > 0.6) & ((th + 2 * np.pi * k) < 2 * np.pi * turns)
    return m


def iron_comp(mask, seed=0):
    """Colour a cut-out iron composition: highlight on top edges, rust specks; alpha 0 elsewhere."""
    h, w = mask.shape
    out = np.zeros((h, w, 4))
    idx = np.full((h, w), 2) + (nb(mask, 1, 0, False) == False) * 3 - (nb(mask, -1, 0, False) == False) * 1
    col = IRON[idx]
    rs = (vnoise(w, h, max(2, w // 3), max(2, h // 3), seed) > 0.8) & mask
    col[rs] = RUST[np.full((h, w), 2)][rs]
    out[..., :3] = col
    out[..., 3] = np.where(mask, 255, 0)
    return out


_IRON = {}


def comp_plane(name, builder, xoff_px=0, rows=None, cols_total=None, px_w=32, y_top_units=16):
    """Painter mapping a composition onto a plane: column from x (left = high x, as seen from the front), row from y."""
    def p(face, w, h, part):
        if name not in _IRON:
            _IRON[name] = builder()
        img = _IRON[name]
        x, y, z = face_coords(part, face, w, h)
        H_, W_ = img.shape[:2]
        col = np.clip(xoff_px + np.floor((16 - x) * 2).astype(int), 0, W_ - 1)
        row = np.clip(np.floor((y_top_units - y) * 2).astype(int), 0, H_ - 1)
        return np.clip(img[row, col], 0, 255).round().astype(np.uint8)
    return p


def spray(text_lines, color, scale=(2, 2), drips=True, halo=True, seed=0, width_px=96, height_px=48, scratch=False,
          heart=False):
    W, H = width_px, height_px
    rng = np.random.default_rng(seed)
    m = np.zeros((H, W), bool)
    y = 2
    for ln in text_lines:
        t = text_mask(ln, spacing=1, scale_x=scale[0], scale_y=scale[1])
        th, tw = t.shape
        x0 = (W - tw) // 2 + int(rng.integers(-2, 3))
        # hand-sprayed: every glyph column band jitters a pixel up/down
        tt = np.zeros_like(t)
        step = 6 * scale[0]
        for c0 in range(0, tw, step):
            dy = int(rng.integers(-1, 2))
            seg = t[:, c0:c0 + step]
            if dy > 0:
                tt[dy:, c0:c0 + step] = seg[:-dy]
            elif dy < 0:
                tt[:dy, c0:c0 + step] = seg[-dy:]
            else:
                tt[:, c0:c0 + step] = seg
        stamp(m, tt, x0, y)
        y += th + 2
    if heart:
        pts = []
        for tt_ in np.linspace(0, 2 * math.pi, 80):
            hx_ = 16 * math.sin(tt_) ** 3
            hy_ = 13 * math.cos(tt_) - 5 * math.cos(2 * tt_) - 2 * math.cos(3 * tt_) - math.cos(4 * tt_)
            pts.append((int(round(W - 12 + hx_ * 0.45)), int(round(H - 12 - hy_ * 0.45))))
        for a_, b_ in zip(pts, pts[1:]):
            m |= path_mask(line_px(*a_, *b_), W, H, wrap=False)
    out = np.zeros((H, W, 4))
    c = C(color)
    Y, X = np.mgrid[0:H, 0:W]
    n = vnoise(W, H, W // 3, H // 3, seed + 1)
    if scratch:   # scratched into the plaster: pale lines with a dark lower edge
        out[m, :3] = C('#e4dfd2')
        out[m, 3] = 230
        lo = nb(m, 1, 0, False) & ~m
        out[lo, :3] = C('#6e6760')
        out[lo, 3] = 200
        return out
    if halo:
        hm = dilate(m, 1, False) & ~m
        out[hm, :3] = c
        out[hm, 3] = 70 + 40 * (n[hm] > 0.5)
    out[m, :3] = c * (0.9 + 0.2 * n[m][:, None])
    out[m, 3] = 235
    if drips:
        bottoms = m & ~nb(m, -1, 0, False)
        for (yy, xx) in zip(*np.nonzero(bottoms)):
            if rng.random() < 0.12:
                L = int(rng.integers(2, 7))
                for k in range(1, L):
                    if yy + k < H:
                        out[yy + k, xx, :3] = c * 0.85
                        out[yy + k, xx, 3] = 220 - k * 15
    return out


def decal_parts(name, builder, w_blocks=3, h_units=24, y0=0):
    """Wall decal on the face of the wall block behind (z = 16 side), centred on this block."""
    x0 = 8 - w_blocks * 8
    def p(face, w, h, part):
        if name not in _IRON:
            _IRON[name] = builder()
        img = _IRON[name]
        x, y, z = face_coords(part, face, w, h)
        H_, W_ = img.shape[:2]
        col = np.clip(np.floor((x0 + w_blocks * 16 - x) * 2).astype(int), 0, W_ - 1)
        row = np.clip(np.floor((y0 + h_units - y) * 2).astype(int), 0, H_ - 1)
        a = np.clip(img[row, col], 0, 255).round().astype(np.uint8)
        if face != 'north':
            a[..., 3] = 0
        return a
    return [PL((x0, y0, 15.92), (x0 + w_blocks * 16, y0 + h_units, 15.92), p, name='decal')]




# =============================================================================================== casa helpers
G_Y, G_X = np.mgrid[0:N, 0:N]


def rect(x0, y0, x1, y1, X=G_X, Y=G_Y):
    """Inclusive pixel rectangle mask."""
    return (X >= x0) & (X <= x1) & (Y >= y0) & (Y <= y1)


def disc(cx, cy, r, X=G_X, Y=G_Y):
    return (X + 0.5 - cx) ** 2 + (Y + 0.5 - cy) ** 2 <= r * r


def ascii_mask(rows, ch='#'):
    return np.array([[c in ch for c in row] for row in rows], bool)


def stamp_ascii(cv, rows, x0, y0, colors):
    """colors: {char: (ramp, idx) | '#hex'}; '.' / ' ' transparent."""
    for j, row in enumerate(rows):
        for i, c in enumerate(row):
            if c in colors:
                x, y = x0 + i, y0 + j
                if 0 <= x < cv.w and 0 <= y < cv.h:
                    col = colors[c]
                    if isinstance(col, str):
                        cv.rgb[y, x] = C(col)
                    else:
                        cv.rgb[y, x] = col[0][np.array(col[1])]
                    cv.a[y, x] = 255


def crack_line(idx, pts, seed, amp=2.5, depth=3, dark=3, lip=1.0):
    """Hairline crack (inside the tile, so variants still tile): darker line, lit lip under it."""
    m = path_mask(wander(pts, seed, amp=amp, depth=depth), wrap=False)
    idx = idx - np.where(m, dark, 0)
    idx = idx + np.where(nb(m, -1, 0, False) & ~m, lip, 0)
    return idx, m


def ghost_frame(idx, x0, y0, x1, y1, nail=True, k=1.0):
    """Ghost of a removed picture: the paint stayed cleaner under the frame, dust line under it, nail above."""
    r = rect(x0, y0, x1, y1)
    idx = idx + np.where(r, 1.0 * k, 0)
    rr = rim(r, wrap=False)
    idx = idx - np.where(rr['out_below'], 2.0 * k, 0) - np.where(rr['out_left'] | rr['out_right'], 1.0 * k, 0)
    if nail:
        cx = (x0 + x1) // 2
        idx[y0 - 4, cx] -= 5
        idx[y0 - 5, cx] += 1
        idx[y0 - 3, cx] -= 1
    return idx


def skirting(cv, ramp=CEDRO, top=26, seed=0, chips=0, scuffs=0):
    """Varnished wooden skirting baked into the bottom of a wall course: crevice shadow, moulded top, grain face,
    dark floor contact, dust on the moulding."""
    X, Y = cv.X, cv.Y
    g = wood_grain(N, N, 5100 + seed, 'x', warp=0.8, pores=0.02)
    idx = np.full((N, N), 4) + g
    idx = np.where(Y == top + 1, 7, idx)
    idx = np.where(Y == top + 2, 5 + (g > 0), idx)
    idx = np.where(Y == top + 3, 3, idx)
    idx = np.where(Y == N - 1, 1, idx)
    rng = np.random.default_rng(5110 + seed)
    for k in range(scuffs):
        x, y = int(rng.integers(2, 26)), int(rng.integers(top + 4, N - 1))
        idx = np.where((Y == y) & (X >= x) & (X < x + int(rng.integers(2, 5))), idx + 2, idx)
    m = Y > top
    cv.put(ramp, idx, m)
    cv.col(cv.rgb[top] * 0.62, Y == top) if False else None
    cv.rgb[top] = cv.rgb[top] * 0.66   # crevice shadow on the wall over the board
    cv.rgb[top - 1] = cv.rgb[top - 1] * 0.9
    if chips:
        for k in range(chips):
            x = int(rng.integers(3, 27))
            ch = (Y >= top + 1) & (Y <= top + 2) & (X >= x) & (X <= x + 1)
            cv.put(PINO, np.full((N, N), 5), ch)
    # dust on the top of the moulding
    du = (Y == top + 1) & (fbm(N, N, 5120 + seed, cells=8, octaves=1) > 0.5)
    cv.tint('#8a826f', np.where(du, 0.35, 0))


def picture_rail(cv, ramp=CEDRO, y=7, seed=0, above=None):
    """Picture rail moulding across the wall at row y; the band above painted with `above` (ramp, idx)."""
    X, Y = cv.X, cv.Y
    if above is not None:
        cv.put(above[0], above[1], Y < y - 1)
    g = wood_grain(N, N, 5200 + seed, 'x', warp=0.6, pores=0.02)
    idx = np.full((N, N), 4) + g
    idx = np.where(Y == y - 1, 6, idx)
    idx = np.where(Y == y, 5 + (g > 0), idx)
    idx = np.where(Y == y + 1, 3, idx)
    cv.put(ramp, idx, (Y >= y - 1) & (Y <= y + 1))
    cv.rgb[y + 2] = cv.rgb[y + 2] * 0.72
    cv.rgb[y + 3] = cv.rgb[y + 3] * 0.92
    # a hook still hanging from the rail
    if seed % 2:
        cv.put(BRASS, np.full((N, N), 4), (X == 21) & (Y >= y + 1) & (Y <= y + 4))
        cv.put(BRASS, np.full((N, N), 6), (X == 22) & (Y == y + 4))


def grime_band(cv, y0, y1, color='#3a3128', amount=0.25, seed=0):
    Y = cv.Y
    t = np.clip((Y - y0) / max(1, y1 - y0), 0, 1) * amount
    n = fbm(N, N, 5300 + seed, cells=4, octaves=2)
    cv.tint(color, np.where(Y >= y0, t * (0.6 + 0.8 * n), 0))


# =============================================================================================== EXTERIOR: brick
def brick_fine_layout():
    """Machine brick (ladrillo visto), 8 courses per block: bricks 15x3 px with 1 px raked joints, half bond."""
    X, Y = G_X, G_Y
    course = Y // 4
    off = (course % 2) * 8
    joint = (Y % 4 == 3) | ((X + off) % 16 == 15)
    lab = np.where(joint, -1, course * 2 + ((X + off) % 32) // 16)
    return lab, joint


def paint_brick_fine(cv, v, seed=0, salt=0.0, soot=0.0):
    X, Y = cv.X, cv.Y
    lab, joint = brick_fine_layout()
    nl = lab.max() + 1
    rc = np.random.default_rng(6000 + seed)            # common: same brick tones in every variant
    tone = rc.choice([-1, 0, 0, 0, 1, 1], nl)
    clink = rc.random(nl) < 0.10
    rv = np.random.default_rng(6010 + seed + 17 * v)   # per variant: a couple more dark/odd bricks inside
    inner = [k for k in range(nl) if not ((lab == k) & (border_dist(N, N) < 1)).any()]
    for k in rv.choice(inner, 2, replace=False):
        tone[k] = rv.choice([-2, 2])
    ly = Y % 4
    li = np.maximum(lab, 0)
    idx = 4 + tone[li]
    f = fbm(N, N, 6020 + seed, cells=4, octaves=2, ax=2.0)
    idx = idx + posterize(cblend(f, fbm(N, N, 6030 + seed + v, cells=4, octaves=2, ax=2.0)), [(0.78, 1), (0.2, -1)])
    idx = np.where(ly == 0, idx + 1, idx)               # top arris catches light
    idx = np.where(ly == 2, idx - 1, idx)               # lower arris
    # sand specks and small pits
    for (x, y) in poisson(6040 + seed + v, 26, 2.6):
        if lab[y, x] >= 0:
            idx[y, x] += -2 if (x * 3 + y) % 4 == 0 else 1
    cv.put(BRICK, idx, ~joint & ~clink[li])
    cv.put(BRICK_D, idx - 1, ~joint & clink[li])
    # raked mortar joints: deep, darker under the brick above, grains
    midx = np.full((N, N), 2) + posterize(fbm(N, N, 6050 + seed, cells=16, octaves=1), [(0.6, 1), (0.25, -1)])
    midx = np.where((X + Y * 3) % 7 == 0, midx + 1, midx)
    cv.put(MORTAR, midx, joint)
    # vertical joints shadowed at the top
    return lab, joint


@painter('ladrillo')
def p_ladrillo(v):
    """Exposed machine brick of the 1950s facade. VAR variants: v0-6 clean (a couple of odd bricks move), v7 soot/rain
    darkening, v8 a stepped crack along the joints, v9 an old wall plug and a rusty nail with a streak."""
    cv = Cv()
    lab, joint = paint_brick_fine(cv, v)
    X, Y = cv.X, cv.Y
    v = {7: 1, 8: 2, 9: 3}.get(v, 0)
    if v == 1:
        n = fbm(N, N, 6100, cells=2, octaves=3)
        t = np.clip((n - 0.42) * 2.4, 0, 1) * cweight(p=0.9)
        cv.tint('#24190f', t * 0.42)
    if v == 2:   # stepped crack through the joints, broken arrises beside it
        path = [(6, 3), (6, 7), (14, 7), (14, 11), (22, 11), (22, 15), (14, 15), (14, 19), (22, 19), (22, 23), (12, 23)]
        cm = np.zeros((N, N), bool)
        for a, b in zip(path, path[1:]):
            cm |= path_mask(line_px(*a, *b), wrap=False)
        cm &= joint
        cm &= fbm(N, N, 6110, cells=8, octaves=1) > 0.22
        cv.col('#22180f', cm)
        side = (nb(cm, 1, 0, False) | nb(cm, 0, 1, False)) & ~cm & ~joint
        cv.tint('#1a100a', np.where(side, 0.35, 0))
        chip = (nb(cm, -1, 0, False) & ~cm & ~joint) & (fbm(N, N, 6111, cells=16, octaves=1) > 0.5)
        cv.put(BRICK, np.full((N, N), 7), chip)
    if v == 3:
        cv.put(PINO, np.full((N, N), 4) + (Y == 13), rect(16, 13, 18, 14))   # wooden plug in a joint
        cv.col('#2a1a10', (X == 17) & (Y == 13))
        cv.put(IRON, np.full((N, N), 5), (X == 9) & (Y == 20))
        cv.put(RUSTST, np.full((N, N), 1) + (Y < 24), (X == 9) & (Y > 20) & (Y < 28))
    return cv.out()


@painter('ladrillo_salitre')
def p_ladrillo_salitre(v):
    """Brick course near the ground: rising damp darkens the lower bricks, salt blooms out of the joints above the
    tide line, earth splashed at the foot."""
    cv = Cv()
    lab, joint = paint_brick_fine(cv, v, seed=3)
    X, Y = cv.X, cv.Y
    wave = 15 + np.round(2.2 * np.sin((X + v * 9) / 32 * 2 * math.pi) + 1.0 * np.sin((X * 2 + 5) / 32 * 2 * math.pi)).astype(int)
    t = np.clip((Y - wave + 2) / 10.0, 0, 1)
    cv.tint('#1e1c16', t * 0.42)
    zone = (Y >= wave - 7) & (Y <= wave + 2)
    salt_bloom(cv, zone & joint, 6200 + v, strength=0.85, density=0.75)
    salt_bloom(cv, zone & ~joint & (np.abs(Y - wave + 1) <= 2), 6205 + v, strength=0.55, density=0.4)
    salt_bloom(cv, (Y < wave - 7) & (Y > wave - 12) & joint, 6207 + v, strength=0.4, density=0.35)
    sp = (Y >= 28) & (fbm(N, N, 6220 + v, cells=16, octaves=1) > 0.5)
    cv.put(EARTH, np.full((N, N), 3), sp)
    return cv.out()


# =============================================================================================== EXTERIOR: white render
def render_idx(v, seed=0, rough=1.0):
    """Painted lime render: the tonal clusters and stucco clumps of lime_idx at 0.6 contrast (soft at facade scale)."""
    return 6.0 + (lime_idx(v, base=6, seed=seed, rough=rough) - 6) * 0.6


@painter('revoque_blanco')
def p_revoque_blanco(v):
    """White painted lime render of the chalet. VAR variants: v0-6 clean, v7 rain streaks, v8 a crazing crack,
    v9 a patched repair."""
    cv = Cv()
    idx = render_idx(v, seed=200)
    X, Y = cv.X, cv.Y
    v = {7: 1, 8: 2, 9: 3}.get(v, 0)
    if v == 2:
        idx, _ = crack_line(idx, [(8, 4), (12, 11), (10, 19), (16, 27)], 6301, amp=2.5)
        idx, _ = crack_line(idx, [(12, 11), (20, 14), (25, 13)], 6302, amp=1.5, dark=2)
    if v == 3:   # rectangular-ish repair: smoother, slightly warmer, trowel edge
        pm = blob(N, N, 17, 15, 9, 7, 6310, rough=0.25, cells=2) & (border_dist(N, N) > 2)
        idx = np.where(pm, 6.2 + posterize(fbm(N, N, 6311, cells=8, octaves=1), [(0.7, 1)]) * 0.4, idx)
        pr = rim(pm, wrap=False)
        idx = idx + np.where(pr['in_top'] | pr['in_left'], 0.5, 0) - np.where(pr['out_below'] | pr['out_right'], 0.6, 0)
    cv.put(RENDER_W, idx)
    if v == 1:   # rain streaks hanging from above (grouped thin lines, broken)
        rng = np.random.default_rng(6320)
        for x in rng.choice(np.arange(4, 28), 4, replace=False):
            L = int(rng.integers(8, 20))
            y0 = int(rng.integers(2, 8))
            m = (X == x) & (Y >= y0) & (Y < y0 + L) & (fbm(N, N, 6321 + int(x), cells=8, octaves=1) > 0.25)
            cv.tint('#6a6a5a', np.where(m, 0.16 * np.clip(1 - (Y - y0) / max(1, L), 0.3, 1), 0))
        cv.tint('#7a7866', np.where(fbm(N, N, 6330, cells=2, octaves=2, ax=4, ay=0.5) > 0.6, 0.12, 0))
    if v == 3:
        cv.tint('#cfc6b0', np.where(pm, 0.18, 0))
    return cv.out()


DAMP_EDGE = 15          # row of the damp front at the block seams (x = 0 / 31): every variant tiles with every other
DAMP_SHAPES = [         # per variant: bumps (centre x, rise in px, half width) of the front (+ climbs, - sags), so the
    [(9.0, 6.0, 5.0), (22.0, -3.0, 5.0)],                               # seams fall on rises, dips and level parts alike
    [(16.0, -6.0, 8.0)],                                                # v1 the front sags in the middle
    [(7.0, 4.0, 3.5), (19.0, 6.0, 4.0), (13.0, -2.0, 3.0)],             # v2 two tongues of different height
    [(12.0, 1.5, 7.0), (24.0, -1.5, 5.0)],                              # v3 almost level
    [(22.0, 7.0, 5.0), (8.0, -4.0, 5.0)],                               # v4 one high tongue on the right, a dip left
    [(5.0, -3.0, 4.0), (16.0, 2.5, 8.0), (27.0, 3.0, 3.5)],             # v5 a wide low rise
]


def damp_front(v):
    X = np.arange(N)
    hw_ = np.sin(np.pi * (X + 0.5) / N) ** 0.7
    bumps = sum(r * np.exp(-((X - c) / w) ** 2) for (c, r, w) in DAMP_SHAPES[v % len(DAMP_SHAPES)])
    jit = (vnoise(N, 1, 8, 1, 6411 + v)[0] - 0.5) * 4.0 + (vnoise(N, 1, 16, 1, 6412 + v)[0] - 0.5) * 2.4 \
        + (vnoise(N, 1, 32, 1, 6413 + v)[0] - 0.5) * 1.6                 # ragged at every scale, like a coastline
    return np.clip(DAMP_EDGE - hw_ * (bumps * 0.85 + jit), 6, 23)


def damp_tint(cv, wet_rows, base=0.12, gain=0.33, ramp_px=14.0, mask=None):
    """Darken the render below the front. wet_rows: (32, 32) rows below the front (<0 = dry). The tint grows over
    14 px under the front and in any case reaches base+gain at the bottom row, so the bottom of every variant
    matches the course below (zocalo_revoque_humedad starts at that value)."""
    X, Y = cv.X, cv.Y
    blot = fbm(N, N, 6450, cells=4, octaves=3)          # one periodic field shared by the two courses
    wet = wet_rows > 0
    g = np.maximum(np.clip(wet_rows / ramp_px, 0, 1), np.clip((Y - 17) / 14.0, 0, 1))
    t = base + gain * g + (blot - 0.5) * 0.12
    if mask is not None:
        wet &= mask
    cv.tint('#4c4c3e', np.where(wet, t, 0))
    alg = wet & (wet_rows > 8) & (Y > 20) & (fbm(N, N, 6452, cells=8, octaves=2) > 0.62)
    cv.tint('#3a4a24', np.where(alg, 0.18, 0))
    return wet


@painter('revoque_humedad')
def p_revoque_humedad(v):
    """Rising damp in the white render (the course above the plinth): the front climbs in tongues whose shape
    changes per variant (all four meet the neighbours at the same height on the block edges), a soft brownish tide
    line where the salts dry out, the wet render darker and greener towards the ground, blistered paint, mould.
    Place casa_zocalo_revoque_humedad under it: the wet zone continues down to the plinth."""
    cv = Cv()
    idx = render_idx(v + 10, seed=200)
    cv.put(RENDER_W, idx)
    X, Y = cv.X, cv.Y
    front = damp_front(v)[None, :] + (fbm(N, N, 6400 + v, cells=8, octaves=3) - 0.5) * 5.0 * np.sin(np.pi * (X + 0.5) / N) ** 0.5
    rows = Y - front
    wet = damp_tint(cv, rows)
    # tide line: 2 px of brownish salt stain at the front (broken), fading softly into the dry paint above it
    brk = fbm(N, N, 6404 + v, cells=8, octaves=2) > 0.33
    cv.tint('#5e5442', np.where((rows > -0.5) & (rows <= 1.5) & brk, 0.26, 0))
    cv.tint('#5e5442', np.where((rows > -1.5) & (rows <= -0.5), 0.14, 0))
    cv.tint('#5e5442', np.where((rows > -2.5) & (rows <= -1.5), 0.06, 0))
    cv.tint('#4a4636', np.where((rows > 4.5) & (rows <= 5.5) & (fbm(N, N, 6403 + v, cells=8, octaves=1) > 0.45), 0.10, 0))
    # a few salt crystals right on the tide line, blistered paint and mould inside the wet zone
    salt_bloom(cv, (rows > -1.5) & (rows < 1.0), 6408 + v, strength=0.25, density=0.2)
    for (cx, cy) in poisson(6420 + v, 2, 9, keep=lambda x, y: 3 < rows[int(y), int(x)] < 10 and 3 < x < 28):
        b = disc(cx, cy, 1.3)
        cv.tint('#d8d6cc', np.where(b & (Y < cy), 0.1, 0))
        cv.tint('#26261e', np.where(rim(b, wrap=False)['out_below'], 0.2, 0))
    return cv.out()


@painter('zocalo_revoque_humedad')
def p_zocalo_revoque_humedad(v):
    """Bottom course under casa_revoque_humedad: the render above the plinth fully wet (the tint picks up exactly
    where the course above ends and keeps darkening), flaking paint, green algae, then the cement plinth, damp too.
    v7: a flake of the plinth gone."""
    cv = Cv()
    cv.put(RENDER_W, render_idx(v + 24, seed=200))
    X, Y = cv.X, cv.Y
    damp_tint(cv, Y + 40.0, base=0.45, gain=0.0)
    cv.tint('#4a4c3e', np.where(Y < 11, np.clip(Y / 10.0, 0, 1) * 0.08, 0))
    alg = (Y > 3) & (Y < 11) & (fbm(N, N, 6460 + v, cells=8, octaves=3) > 0.58)
    cv.tint('#3a4a24', np.where(alg, 0.16, 0))
    salt_bloom(cv, (Y > 5) & (Y < 10) & (fbm(N, N, 6461 + v, cells=4, octaves=2) > 0.6), 6462 + v, strength=0.22, density=0.3)
    plinth(cv, 1 if v == 7 else (0 if v == 1 else v), 'render')
    cv.tint('#24261c', np.where(Y > 11, 0.12, 0))
    return cv.out()


def plinth(cv, v, above, seed=0, top=11):
    """Cement plinth (zócalo de cemento) under a facade: drip groove, salt crust, rising damp, splash dirt."""
    X, Y = cv.X, cv.Y
    idx = np.full((N, N), 4) + posterize(cblend(fbm(N, N, 6500 + seed, cells=8, octaves=2), fbm(N, N, 6501 + seed + v, cells=8, octaves=2)), [(0.7, 1), (0.28, -1)])
    idx = relief(idx, 6502 + seed, 6503 + seed + v, count=34, mind=3.2, body=-1, light=1)
    m = Y >= top
    cv.put(CEMENT, idx, m)
    cv.put(CEMENT, np.full((N, N), 1), Y == top)        # drip groove (buña) under the facade
    cv.put(CEMENT, np.full((N, N), 6), Y == top + 1)    # lit lip of the plinth
    cv.rgb[top - 1] = cv.rgb[top - 1] * 0.8
    # damp darkening towards the ground + splash
    t = np.clip((Y - (top + 6)) / 14.0, 0, 1)
    cv.tint('#24261c', np.where(m, t * 0.5, 0))
    hw_ = np.sin(np.pi * (X + 0.5) / N)
    wave = top + 9 + np.round(1.0 * np.sin((X + seed) / 32 * 2 * math.pi) + 4 * hw_ * (vnoise(N, N, 5, 1, 6512 + seed + v) - 0.5)).astype(int)
    tide = (Y == wave) & (fbm(N, N, 6513 + seed + v, cells=8, octaves=1) > 0.3)
    cv.tint('#1e2018', np.where(tide, 0.3, 0))
    patch = cblend(fbm(N, N, 6514 + seed, cells=4, octaves=2), fbm(N, N, 6515 + seed + v, cells=4, octaves=2)) > 0.5
    salt_bloom(cv, m & (Y > top + 1) & (Y < wave) & (Y > wave - 5) & patch, 6510 + seed + v, strength=0.55, density=0.4)
    sp = (Y >= 28) & (fbm(N, N, 6520 + seed + v, cells=16, octaves=1) > 0.5)
    cv.put(EARTH, np.full((N, N), 2), sp)
    if v == 1:   # a flake of the plinth gone: brick under it
        H = flake(20, 23, 4.5, 3.0, 6530 + seed, jag=0.35) & m & (Y > top + 3) & (border_dist(N, N) > 1)
        sub = Cv()
        paint_brick_fine(sub, 0, seed=9)
        r = rim(H, wrap=False)
        dk = np.where(r['in_top'], 0.55, 1.0) * np.where(r['in_left'], 0.8, 1.0)
        cv.rgb[H] = (sub.rgb * dk[..., None])[H]
        cv.put(CEMENT, np.full((N, N), 6), r['out_below'])


@painter('zocalo_revoque')
def p_zocalo_revoque(v):
    cv = Cv()
    cv.put(RENDER_W, render_idx(v + 20, seed=200))
    cv.tint('#6a6656', np.where(cv.Y > 6, 0.12, 0))
    plinth(cv, v, 'render')
    return cv.out()


@painter('zocalo_ladrillo')
def p_zocalo_ladrillo(v):
    cv = Cv()
    paint_brick_fine(cv, v, seed=5)
    plinth(cv, v, 'brick', seed=40, top=12)
    return cv.out()


def cement_sweeps(seed, v, count=3, radius=(18.0, 30.0), length=(12.0, 20.0), tilt=0.5, inset=3):
    """Tool marks in a cement finish: a few long, shallow trowel strokes running roughly along the wall (or across
    the floor), each a lit ridge with the dull groove of the blade's edge just under it, fading out at both ends and
    broken where the tool skipped. Kept inside the block so every variant still tiles. Returns a float field
    (+1 ridge, -1 groove, fractional where it fades)."""
    X, Y = G_X + 0.5, G_Y + 0.5
    rng = np.random.default_rng(seed + 7 * v)
    out = np.zeros((N, N))
    for k in range(count):
        a0 = (math.pi / 2 if rng.random() < 0.5 else -math.pi / 2) + rng.uniform(-tilt, tilt)
        R = rng.uniform(*radius)
        L = rng.uniform(*length)
        px, py = rng.uniform(9, 23), rng.uniform(6 + 7 * (k % 3), 9 + 7 * (k % 3))
        cx, cy = px - math.cos(a0) * R, py - math.sin(a0) * R
        sp = L / R
        d = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2)
        dth = (np.arctan2(Y - cy, X - cx) - a0 + math.pi) % (2 * math.pi) - math.pi
        win = np.clip(np.cos(np.clip(dth / (sp / 2), -1, 1) * math.pi / 2), 0, 1) ** 0.6
        side = 1.0 if math.sin(a0) < 0 else -1.0        # the groove sits on the lower side of the stroke
        ridge = np.abs(d - R) < 0.55
        groove = np.abs(d - (R - side)) < 0.55
        out = out + np.where(ridge, win, 0) - np.where(groove & ~ridge, win * 0.8, 0)
    keep = (border_dist(N, N) >= inset) & (fbm(N, N, seed + 3 + v, cells=8, octaves=1) > 0.28)
    return np.clip(out, -1, 1) * keep


def cement_idx(v, seed, contrast=0.45, sweeps=None, pits=4, speck=(0.965, 0.975), tool=0.45):
    """Structured cement finish (no per-pixel mush): soft large tonal patches, a mid-scale cloudiness, the tool
    strokes, a few pits with a lit lip, and only a sparse sprinkle of 1 px grains."""
    X, Y = G_X, G_Y
    f = cblend(fbm(N, N, seed, cells=2, octaves=3), fbm(N, N, seed + 1 + v, cells=2, octaves=3))
    idx = np.full((N, N), 4.0) + posterize(f, [(0.74, 1), (0.24, -1)]) * contrast
    m2 = cblend(fbm(N, N, seed + 2, cells=4, octaves=2), fbm(N, N, seed + 3 + v, cells=4, octaves=2))
    idx = idx + np.where(m2 > 0.8, 0.3, 0) - np.where(m2 < 0.18, 0.3, 0)
    idx = idx + np.where(_hash01(X, Y, seed + 4 + v) > speck[0], 0.6, 0) - np.where(_hash01(X, Y, seed + 5 + v) > speck[1], 0.6, 0)
    idx = idx + cement_sweeps(seed + 10, v, **(sweeps or {})) * tool
    bd = border_dist(N, N)
    for (x, y) in poisson(seed + 20 + v, pits, 6, keep=lambda x, y: bd[int(y), int(x)] >= 2):
        idx[y, x] -= 1.6
        idx[(y + 1) % N, x] += 0.6
    return idx


def cement_patch(idx, cx, cy, rx, ry, seed):
    """An old repair: a flatter, slightly lighter patch with a thin raised edge (lit top/left, shadow bottom/right)."""
    pm = flake(cx, cy, rx, ry, seed, jag=0.25) & (border_dist(N, N) > 2)
    pr = rim(pm, wrap=False)
    idx = np.where(pm, 4.3 + (fbm(N, N, seed + 1, cells=8, octaves=1) > 0.6) * 0.3, idx)
    idx = idx + (pr['in_top'] | pr['in_left']) * 0.6 - (pr['out_below'] | pr['out_right']) * 0.9
    return idx, pm


def efflorescence(cv, x, y0, length, seed, strength=0.16):
    """A pale salt streak washing down the cement from a crack or a joint (1-2 px, fraying downwards)."""
    X, Y = cv.X, cv.Y
    wob = np.round(np.sin((Y + seed) / 5.0) * 0.6).astype(int)
    m = (np.abs(X - x - wob) <= (Y < y0 + length // 2)) & (Y >= y0) & (Y < y0 + length)
    m &= fbm(N, N, seed, cells=8, octaves=1) > 0.25
    t = np.clip(1 - (Y - y0) / max(1, length), 0, 1)
    cv.tint('#dedbd2', np.where(m, strength * (0.4 + 0.6 * t), 0))


@painter('medianera')
def p_medianera(v, kind=None):
    """Neighbour's party wall: coarse grey cement render (revoque grueso fratachado) with wide float sweeps and
    sparse stucco clumps. VAR variants: v0-7 clean (v4 the faint horizontal joint where one day's render met the
    next), v8 a small newer patch, v9 a short rust run from an old bracket.
    Hand-placed: kind='parche' (two newer plaster patches), kind='hueco' (render fallen: the hollow clay block)."""
    cv = Cv()
    X, Y = cv.X, cv.Y
    idx = cement_idx(v, 6600, contrast=0.5, sweeps=dict(count=2, radius=(22.0, 40.0), length=(14.0, 24.0)), pits=5, tool=0.35)
    idx = idx + relief(np.zeros((N, N)), 6602, 6603 + v, count=14, mind=4.5, body=-1, light=1) * 0.6
    if kind is None and v == 4:
        seam = (Y == 19 + np.round(np.sin(X / 9.0)).astype(int)) & (border_dist(N, N) >= 0)
        idx = idx + np.where(seam, 0.8, 0) - np.where(nb(seam, 1, 0), 0.6, 0)
    if kind is None and v == 8:
        idx, _ = cement_patch(idx, 20, 12, 5.5, 4.5, 6612)
    cv.put(CEMENT, idx)
    if kind == 'parche':   # two newer patches: smoother, lighter, thick edge with a shadow under it
        for k, (cx, cy, rx, ry) in enumerate(((11, 11, 7.5, 6), (23, 22, 6, 5.5)) if v % 2 == 0 else ((19, 9, 8, 5.5), (9, 23, 6.5, 5))):
            pm = flake(cx, cy, rx, ry, 6610 + k + 2 * v, jag=0.25) & (border_dist(N, N) > 1)
            pidx = np.full((N, N), 4.6 + 0.4 * (k == 0)) + posterize(fbm(N, N, 6611 + k, cells=4, octaves=2), [(0.72, 1), (0.3, -1)]) * 0.4
            pr = rim(pm, wrap=False)
            pidx = pidx + pr['in_top'] * 0.6 - pr['in_bot'] * 0.4
            cv.put(CEMENT, pidx, pm)
            cv.tint('#1c1b19', np.where(pr['out_below'] | pr['out_right'], 0.3, 0))
            cv.tint('#d0cab8', np.where(pm, 0.05, 0))
    if kind == 'hueco':   # render fallen: ladrillo hueco (hollow clay block) with its channels
        H = flake(15, 17, 9, 6.5, 6620 + v, jag=0.45) & (border_dist(N, N) > 2)
        # the grooved face of the hollow clay blocks (ladrillo hueco), 12 px courses with thick grey joints, the
        # scratch-coat grooves running along, one block corner broken open showing its dark cells
        HUE = Ramp('#3d1a10', '#5a2716', '#77351d', '#904426', '#a65532', '#b8673f')
        hl = (Y % 12 == 11) | (Y % 12 == 10) & False | ((X + (Y // 12) * 9) % 20 == 19)
        ly = Y % 12
        hidx = np.full((N, N), 3.0) + np.where(ly % 2 == 0, 0.6, -0.4) + (ly == 0) * 0.6 - (ly == 9) * 0.8
        hidx = hidx + posterize(fbm(N, N, 6621, cells=4, octaves=2), [(0.7, 1), (0.3, -1)]) * 0.5
        cv.put(HUE, hidx, H & ~hl)
        brk = H & ~hl & (np.abs(X - 19) <= 2) & (ly >= 3) & (ly <= 6) & (Y < 24)
        cv.put(HUE, np.full((N, N), 0), brk & ((X - 19) % 2 != 0))
        cv.put(MORTAR, np.full((N, N), 3) - (ly == 10), H & hl)
        r = rim(H, wrap=False)
        cv.put(CEMENT, np.full((N, N), 1), r['in_top'] | r['in_left'])
        cv.put(CEMENT, np.full((N, N), 6), r['out_below'] | r['out_right'])
    if kind is None and v == 9:   # rust run from a bracket
        cv.put(IRON, np.full((N, N), 3) + (Y == 6), rect(13, 6, 15, 7))
        st = (np.abs(X - 14.0) < 0.9 + (Y - 8) / 22) & (Y > 7) & (Y < 22)
        cv.tint('#6a3a1c', np.where(st, 0.35 * (1 - (Y - 8) / 16), 0))
    if kind is None and v in (2, 6):
        efflorescence(cv, [9, 22][v == 6], [6, 11][v == 6], 12, 6640 + v, strength=0.12)
    return cv.out()


PAINTERS['medianera_parche'] = lambda v: p_medianera(v + 20, 'parche')
PAINTERS['medianera_hueco'] = lambda v: p_medianera(v + 30, 'hueco')


# =============================================================================================== INTERIOR: painted walls
def latex_idx(v, seed):
    """Látex over smooth plaster: softer than lime, a faint roller stipple."""
    idx = lime_idx(v, base=6, seed=seed, rough=0.35)
    st = (fbm(N, N, seed + 77, cells=16, octaves=1) > 0.82) & ((G_X + G_Y) % 3 == 0)
    idx = idx + np.where(st, 1, 0)
    return 6.0 + (idx - 6) * 0.4     # soft: clusters stay crisp but only 0.4 of a ramp step apart


def finger_drag(cv, x0, y0, seed, color='#2a2420', amount=0.18, length=17):
    """Four dirty finger trails sliding down the wall (someone feeling their way in the dark)."""
    X, Y = cv.X, cv.Y
    m = np.zeros((N, N), bool)
    for k in range(4):
        pts = wander([(x0 + k * 2, y0 + abs(k - 1.5)), (x0 + k * 2 + 1, y0 + length + (k % 2) - abs(k - 1.5))], seed + k, amp=0.3, depth=2)
        m |= path_mask(pts, wrap=False)
    fade = np.clip(1 - (Y - y0) / (length + 2.0), 0.25, 1)
    cv.tint(color, np.where(m, amount * fade, 0))


# Variant plan of the plain wall/floor cubes (Minecraft picks a variant per placed block with equal weight): VAR
# variants, the first ones are clean re-seeds of the base mottling, each defect appears in ONE variant only (10 %),
# and loud story-like defects (picture ghosts, finger drags, missing tiles, stains) are separate hand-placed cubes.
VAR = 10
ROOM_CRACKS = [[(22, 3), (19, 10), (21, 17), (15, 25), (16, 29)],
               [(7, 2), (10, 9), (8, 15), (12, 22), (11, 27)],
               [(26, 6), (21, 12), (23, 19), (18, 26)],
               [(13, 3), (16, 9), (14, 16), (19, 24)]]


def room_wall(ramp, v, seed, extra=None, kind=None):
    """Generic room wall, VAR variants: v0-7 clean re-seeds of the latex mottling, v8 a hairline crack (its path
    depends on the room), v9 the room's own light wear (extra) or a faint hand-height smudge.
    Hand-placed kinds: 'marco' = ghost of a removed picture with its nail (v0 landscape, v1 portrait),
    'rayada' = grime and four dirty finger trails sliding down (someone feeling their way in the dark)."""
    cv = Cv()
    idx = latex_idx(v + (20 if kind else 0), seed)
    X, Y = cv.X, cv.Y
    if kind == 'marco':
        idx = ghost_frame(idx, *((7, 10, 24, 25) if v % 2 == 0 else (10, 8, 21, 27)), k=0.6)
    if kind is None and v == 8:
        idx, _ = crack_line(idx, ROOM_CRACKS[(seed // 100) % len(ROOM_CRACKS)], seed + 11, amp=2.0, dark=2, lip=0.6)
    cv.put(ramp, idx)
    if kind == 'rayada':
        hm = (fbm(N, N, seed + 21, cells=4, octaves=2) > 0.55) & (Y > 8) & (Y < 26)
        cv.tint('#3a3024', np.where(hm, 0.07, 0))
        finger_drag(cv, 9 if v % 2 == 0 else 13, 9 if v % 2 == 0 else 6, seed + 30 + v)
    if kind is None and v == 9:
        if extra:
            extra(cv, v)
        else:   # faint smudge at hand height (light switch level), nothing that reads as a pattern
            hm = (fbm(N, N, seed + 21, cells=4, octaves=2) > 0.6) & (Y > 10) & (Y < 24) & (border_dist(N, N) > 3)
            cv.tint('#3a3024', np.where(hm, 0.05, 0))
    return cv


def room_wall_zocalo(ramp, v, seed, wood=CEDRO):
    cv = Cv()
    idx = latex_idx(v + 40, seed)
    cv.put(ramp, idx)
    grime_band(cv, 18, 26, amount=0.18, seed=seed)
    skirting(cv, wood, top=25, seed=seed + v, chips=int(v == 3), scuffs=2 + v)
    return cv


@painter('pared_living')
def p_pared_living(v):
    return room_wall(BEIGE, v, 7100).out()


@painter('pared_living_marco')
def p_pared_living_marco(v):
    """Hand-placed: the clean ghost of a picture taken down (the family photo moved), its nail still in."""
    return room_wall(BEIGE, v, 7100, kind='marco').out()


@painter('pared_living_zocalo')
def p_pared_living_zocalo(v):
    return room_wall_zocalo(BEIGE, v, 7100).out()


@painter('pared_living_moldura')
def p_pared_living_moldura(v):
    """Top course of the living: picture rail with a paler frieze band above it (painted like the ceiling)."""
    cv = Cv()
    idx = latex_idx(v + 60, 7100)
    cv.put(BEIGE, idx)
    picture_rail(cv, CEDRO, y=8, seed=v, above=(WHITEP, latex_idx(v + 61, 7150) - 1))
    if v == 1:   # yellowed smoke shadow over the rail (the stove / cigarettes of 50 years)
        cv.tint('#7a6436', np.where((cv.Y < 7) & (fbm(N, N, 7160, cells=2, octaves=2) > 0.4), 0.22, 0))
    return cv.out()


def hall_extra(cv, v):
    if v == 9:   # dog rub: Choripán's greasy brown smear along the hall, low, with hair-like streaks
        X, Y = cv.X, cv.Y
        n = fbm(N, N, 7230, cells=2, octaves=3, ax=0.25, ay=2)
        band = np.clip(1 - np.abs(Y - 25) / 4.0, 0, 1) * np.clip((n - 0.25) * 2, 0, 1)
        hair = fbm(N, N, 7231, cells=16, octaves=1, ax=0.25, ay=4) > 0.6
        cv.tint('#4a3824', band * (0.28 + 0.12 * hair))


@painter('pared_pasillo')
def p_pared_pasillo(v):
    return room_wall(AQUA, v, 7200, hall_extra).out()


@painter('pared_pasillo_marco')
def p_pared_pasillo_marco(v):
    """Hand-placed: where the family photos hung along the hall (v0 landscape, v1 portrait)."""
    return room_wall(AQUA, v, 7200, kind='marco').out()


@painter('pared_pasillo_rayada')
def p_pared_pasillo_rayada(v):
    """Hand-placed: dirty finger trails sliding down the wall at shoulder height (chapter 6, the dark hall)."""
    return room_wall(AQUA, v, 7200, kind='rayada').out()


@painter('pared_pasillo_zocalo')
def p_pared_pasillo_zocalo(v):
    return room_wall_zocalo(AQUA, v, 7200).out()


def kitchen_extra(cv, v):
    X, Y = cv.X, cv.Y
    rng = np.random.default_rng(7330 + v)
    if v == 9:   # grease splatter: clusters of small amber specks + a drip run
        for (cx, cy) in poisson(7331, 3, 9, keep=lambda x, y: 4 < x < 28 and 4 < y < 24):
            for k in range(14):
                x = int(round(cx + rng.normal(0, 2.4)))
                y = int(round(cy + rng.normal(0, 2.0)))
                if 1 <= x < 31 and 1 <= y < 31:
                    cv.tint('#7a5a1a', np.where((X == x) & (Y == y), 0.35 + 0.2 * rng.random(), 0))
            cv.tint('#7a5a1a', np.where((X == cx) & (Y > cy) & (Y < cy + 7), 0.22, 0))
        cv.tint('#9a8040', np.where(fbm(N, N, 7332, cells=2, octaves=2) > 0.5, 0.1, 0))


@painter('pared_cocina')
def p_pared_cocina(v):
    return room_wall(KCREAM, v, 7300, kitchen_extra).out()


@painter('pared_cocina_hollin')
def p_pared_cocina_hollin(v):
    """Hand-placed: the soot cloud above the stove (the wall course right over the burners), fading up and out."""
    cv = room_wall(KCREAM, v + 3, 7300)
    X, Y = cv.X, cv.Y
    f = 1 - np.sqrt(((X - 16) / 16.0) ** 2 + ((Y - 30) / 26.0) ** 2) + (fbm(N, N, 7340 + v, cells=4, octaves=3) - 0.5) * 0.5
    cv.tint('#2c2620', np.clip(f, 0, 1) * 0.55)
    return cv.out()


def bath_extra(cv, v):
    X, Y = cv.X, cv.Y
    if v == 9:   # black mould specks from the steam, thicker near the ceiling
        for k, (x, y) in enumerate(poisson(7430 + v, 22, 2.2, keep=lambda x, y: y < 18 + (x % 7))):
            cv.put(SOOT, np.full((N, N), 1 + (k % 3)), (X == x) & (Y == y) | ((k % 4 == 0) & (X == x + 1) & (Y == y)))
        cv.tint('#4a4a3a', np.where((Y < 10) & (fbm(N, N, 7440, cells=4, octaves=2) > 0.5), 0.2, 0))


@painter('pared_bano')
def p_pared_bano(v):
    return room_wall(WHITEP, v, 7400, bath_extra).out()


@painter('pared_lucia')
def p_pared_lucia(v):
    return room_wall(PINK, v, 7500).out()


@painter('pared_lucia_zocalo')
def p_pared_lucia_zocalo(v):
    return room_wall_zocalo(PINK, v, 7500, wood=ENAMEL_W).out()


STAR = ['..#..', '.###.', '#####', '.###.', '.#.#.']
HEART = ['.#.#.', '#####', '#####', '.###.', '..#..']
BUTTER = ['#...#', '##.##', '.###.', '##.##', '#...#']
RAINBOW = ['..rrrr..', '.roooor.', 'royyyyor', 'oy....yo', 'y......y']
MOON = ['.##.', '#...', '#...', '#...', '.##.']


@painter('pared_lucia_stickers')
def p_pared_lucia_stickers(v):
    """Pink wall with a girl's stickers: glossy stars, hearts, a rainbow, a butterfly; one half peeled off with the
    glue ghost of another."""
    cv = room_wall(PINK, v % 2, 7500)
    X, Y = cv.X, cv.Y

    def sticker(rows, x0, y0, col, outline='#f4eee6', peeled=False):
        m = np.zeros((N, N), bool)
        stamp(m, ascii_mask(rows), x0, y0)
        o = dilate(m, 1, False) & ~m
        cv.col(outline, o)
        cv.col(col, m)
        cv.col('#ffffff', m & ~nb(m, 1, 0, False) & ~nb(m, 0, 1, False))
        if peeled:   # lower half curling off: the paper back shows
            pm = m & (Y >= y0 + 3)
            cv.col('#d9d2c4', pm)
            cv.col('#9a8e80', nb(pm, -1, 0, False) & ~m & o)
    if v == 0:
        sticker(STAR, 5, 5, '#e8c23a')
        sticker(HEART, 20, 9, '#d8486a')
        sticker(STAR, 13, 20, '#7ac0e6')
        sticker(MOON, 25, 22, '#e8d36a')
    elif v == 1:
        rb = np.zeros((N, N), bool)
        stamp(rb, ascii_mask(RAINBOW, 'roy'), 10, 8)
        cv.col('#f4eee6', dilate(rb, 1, False) & ~rb)
        for ch, col in (('r', '#d8485a'), ('o', '#e89a3a'), ('y', '#e8d84a')):
            mm = np.zeros((N, N), bool)
            stamp(mm, ascii_mask(RAINBOW, ch), 10, 8)
            cv.col(col, mm)
        sticker(BUTTER, 5, 20, '#9a6ad8')
        sticker(HEART, 23, 21, '#d8486a', peeled=True)
    elif v == 2:
        sticker(STAR, 6, 7, '#e8c23a', peeled=True)
        sticker(STAR, 19, 5, '#e8c23a')
        sticker(HEART, 12, 18, '#e86a9a')
        g = rect(22, 20, 26, 24)
        cv.tint('#8a6a5a', np.where(g & (fbm(N, N, 7560, cells=16, octaves=1) > 0.4), 0.3, 0))   # glue ghost
    return cv.out()


@painter('pared_toti')
def p_pared_toti(v):
    return room_wall(TOTI, v, 7600).out()


@painter('pared_toti_zocalo')
def p_pared_toti_zocalo(v):
    return room_wall_zocalo(TOTI, v, 7600, wood=WOOD_D).out()


def poster_frame(cv, x0, y0, x1, y1, seed):
    """Paper poster: slight curl shadow on the right/bottom, tape corners, a torn corner."""
    X, Y = cv.X, cv.Y
    m = rect(x0, y0, x1, y1)
    r = rim(m, wrap=False)
    cv.tint('#000000', np.where(r['out_below'] | r['out_right'], 0.45, 0))
    return m


def tape(cv, x, y):
    cv.put(Ramp('#8a8166', '#b5ac8c', '#d2caa8'), np.full((N, N), 1) + (cv.Y == y), rect(x, y, x + 2, y + 1))


@painter('pared_toti_poster')
def p_pared_toti_poster(v):
    """Toti's gamer posters (invented games, no brands): v0 'RANKED' neon helmet, v1 pixel dragon 'DRAGON 7',
    v2 'GG' with a controller."""
    cv = room_wall(TOTI, v % 2, 7600)
    X, Y = cv.X, cv.Y
    if v == 0:
        m = poster_frame(cv, 6, 3, 25, 29, 7610)
        g = np.clip((Y - 3) / 26.0, 0, 1)
        bg = Ramp('#120a24', '#1e0f3a', '#2c1452', '#3c1a68')
        cv.put(bg, np.full((N, N), 3) - (g * 3).astype(int), m)
        helm = ascii_mask(['...####...', '..######..', '.########.', '.#VVVVVV#.', '.#VVVVVV#.', '.########.',
                           '..######..', '..##..##..', '.###..###.', '####..####'], '#')
        visor = ascii_mask(['...####...', '..######..', '.########.', '.#VVVVVV#.', '.#VVVVVV#.', '.########.',
                            '..######..', '..##..##..', '.###..###.', '####..####'], 'V')
        hm, vm = np.zeros((N, N), bool), np.zeros((N, N), bool)
        stamp(hm, helm, 11, 7)
        stamp(vm, visor, 11, 7)
        cv.col('#2a2a36', hm)
        cv.col('#4a4a5a', hm & ~nb(hm, 1, 0, False))
        cv.col('#2ee8e0', vm)
        cv.col('#c8fffb', vm & (Y == 10))
        cv.col('#2ee8e0', (dilate(hm | vm, 1, False) & ~(hm | vm)) & m & (fbm(N, N, 7611, cells=16, octaves=1) > 0.5))
        tm = np.zeros((N, N), bool)
        stamp(tm, tiny_mask('RANKED')[1:], 8, 21)
        cv.col('#ff3aa8', tm)
        cv.col('#ffd0ec', tm & ~nb(tm, 1, 0, False))
        cv.col('#2ee8e0', (Y == 27) & (X >= 9) & (X <= 22) & m)
        tape(cv, 6, 3)
        tape(cv, 23, 3)
    elif v == 1:
        m = poster_frame(cv, 4, 4, 27, 27, 7620)
        cv.put(Ramp('#3a1a0a', '#6a2a10', '#a4441a', '#d8762a', '#f0a84a'), np.clip(4 - ((Y - 4) // 6), 0, 4), m)
        drag = ['......##..', '.....####.', '##..##.#..', '.######...', '..#######.', '.##.##..##', '##..#...#.', '#...#.....']
        dm = np.zeros((N, N), bool)
        stamp(dm, ascii_mask(drag), 10, 9)
        cv.col('#1a0a0a', dm)
        cv.col('#ff5a2a', (X == 17) & (Y == 10))
        tm = np.zeros((N, N), bool)
        stamp(tm, tiny_mask('DRAGON')[1:], 7, 20)
        seven = np.zeros((N, N), bool)
        stamp(seven, text_mask('7')[2:], 22, 6)
        cv.col('#ffe27a', seven)
        cv.col('#f8e8b0', tm)
        cv.col('#5a1a0a', nb(tm, -1, 0, False) & ~tm & m)
        torn = (X >= 24) & (Y >= 24) & (X + Y >= 50)
        cv.put(TOTI, latex_idx(v, 7600), torn & m)
        tape(cv, 4, 4)
    else:
        m = poster_frame(cv, 7, 5, 24, 26, 7630)
        cv.put(Ramp('#0a1a12', '#0e2a1c', '#123a26'), np.full((N, N), 1) + ((X + Y) % 4 == 0), m)
        tm = np.zeros((N, N), bool)
        stamp(tm, text_mask('GG', spacing=2, scale_x=2, scale_y=2)[4:], 9, 8)
        cv.col('#5aff7a', tm)
        cv.col('#d8ffe0', tm & ~nb(tm, 1, 0, False))
        pad = ascii_mask(['.##########.', '############', '##.#####.###', '############', '###......###', '.##......##.'])
        pm = np.zeros((N, N), bool)
        stamp(pm, pad, 10, 18)
        cv.col('#dcdcdc', pm)
        cv.col('#ff3a3a', (X == 18) & (Y == 20))
        cv.col('#3a7aff', (X == 19) & (Y == 21))
        tape(cv, 22, 5)
    return cv.out()


# --- wallpapers
ROSE = ['..dRd..', '.dRhRd.', '.RhdhR.', '.dRhRd.', 'l.dRd.l', 'll.s.ll', '.l.s.l.', '...s...']
BUD = ['.d.', 'dRd', '.s.', 'ls.', '.s.']


def nona_paper(v, faded=True):
    cv = Cv()
    X, Y = cv.X, cv.Y
    f = cblend(fbm(N, N, 7700, cells=2, octaves=3), fbm(N, N, 7701 + v, cells=2, octaves=3))
    idx = np.full((N, N), 4) + posterize(f, [(0.78, 1), (0.2, -1)])
    stripe = (X % 8 == 0)
    dots = (X % 8 == 4) & (Y % 4 == 1)
    idx = np.where(stripe, idx + 1, idx)
    idx = np.where(dots, idx - 1, idx)
    cv.put(NONA_BG, idx)
    cols = {'d': (NONA_ROSE, 1), 'R': (NONA_ROSE, 2), 'h': (NONA_ROSE, 4), 'l': (NONA_LEAF, 2), 's': (NONA_LEAF, 1)}
    for (x0, y0) in ((5, 3), (21, 19)):
        for dx in (0, -32):
            for dy in (0, -32):
                stamp_ascii(cv, ROSE, x0 + dx, y0 + dy, cols)
    for (x0, y0) in ((22, 6), (6, 22)):
        stamp_ascii(cv, BUD, x0, y0, cols)
    # paper texture: soft fading towards light-struck areas
    cv.tint('#cfc6a4', np.where(fbm(N, N, 7710 + v, cells=2, octaves=2) > 0.55, 0.12 if faded else 0, 0))
    return cv


@painter('empapelado_nona')
def p_empapelado_nona(v, kind=None):
    """Faded floral wallpaper of the Nona's room (sepia-green ground, stripes, roses in half-drop), VAR variants:
    v0-7 clean (the fading moves), v8 lifting seam (with the plaster behind), v9 a small water stain.
    kind='cruz' (hand-placed): the unfaded ghost where the crucifix hung, its nail still there."""
    cv = nona_paper(v)
    X, Y = cv.X, cv.Y
    if kind == 'cruz':
        v = 3
    elif v in (8, 9):
        v = {8: 1, 9: 2}[v]
    else:
        v = 0
    if v == 1:
        seam = (X == 16)
        cv.put(NONA_BG, np.full((N, N), 1), seam & (Y < 22))
        lift = (X >= 13) & (X <= 15) & (Y >= 6) & (Y <= 14) & (X - 13 >= (Y - 6) // 4)
        cv.put(WHITEP, np.full((N, N), 4), (X >= 13) & (X <= 15) & (Y >= 6) & (Y <= 14))   # plaster behind
        cv.put(NONA_BG, np.full((N, N), 2), lift)
        cv.put(NONA_BG, np.full((N, N), 6), (X == 12) & (Y >= 6) & (Y <= 14))          # curled lip
        cv.tint('#000000', np.where((X == 11) & (Y >= 7) & (Y <= 15), 0.3, 0))
    if v == 2:
        st = blob(N, N, 19, 9, 8, 6.5, 7720, rough=0.4) & (border_dist(N, N) > 1)
        cv.tint('#7a5a2a', np.where(st, 0.14, 0))
        cv.tint('#4a3016', np.where(st & ~erode(st, 1, False) & (fbm(N, N, 7722, cells=8, octaves=1) > 0.35), 0.16, 0))
        inner = erode(st, 3, False) & (fbm(N, N, 7721, cells=4, octaves=2) > 0.5)
        cv.tint('#4a3016', np.where(inner & ~erode(inner, 1, False), 0.35, 0))
    if v == 3:
        cross = rect(14, 4, 17, 27) | rect(9, 9, 22, 12)
        cv.rgb = np.where(cross[..., None], np.clip(cv.rgb * 1.05 + np.array([6, -4, -6]) * 0 + 0, 0, 255), cv.rgb)
        un = nona_paper(9, faded=False)
        cv.rgb[cross] = np.clip(un.rgb[cross] * 1.08, 0, 255)
        rr = rim(cross, wrap=False)
        cv.tint('#3a3020', np.where(rr['out_below'], 0.35, 0))
        cv.put(IRON, np.full((N, N), 2), (X == 15) & (Y == 2))
    return cv.out()


PAINTERS['empapelado_nona_cruz'] = lambda v: p_empapelado_nona(v + 30, 'cruz')


@painter('empapelado_nona_zocalo')
def p_empapelado_nona_zocalo(v):
    cv = nona_paper(v + 20)
    grime_band(cv, 16, 26, amount=0.2, seed=7730)
    skirting(cv, CEDRO, top=25, seed=7730 + v, chips=v, scuffs=3)
    return cv.out()


def mat_paper(v):
    """70s geometric wallpaper (mustard ground, brown and orange rings) for the master bedroom."""
    cv = Cv()
    X, Y = cv.X, cv.Y
    lx, ly = X % 16, Y % 16
    cell = (X // 16 + Y // 16) % 2
    d = np.sqrt((lx - 7.5) ** 2 + (ly - 7.5) ** 2)
    f = cblend(fbm(N, N, 7800, cells=2, octaves=2), fbm(N, N, 7801 + v, cells=2, octaves=2))
    base = posterize(f, [(0.8, 1), (0.2, -1)])
    cv.put(MAT_BG, np.full((N, N), 4) + base)
    ring1 = (d >= 5.6) & (d < 7.4)
    ring2 = (d >= 3.2) & (d < 4.6)
    core = d < 1.8
    a, b = (MAT_BR, MAT_OR)
    cv.put(MAT_BR, np.full((N, N), 3) + base + (ly < 7), ring1 & (cell == 0))
    cv.put(MAT_OR, np.full((N, N), 2) + base + (ly < 7), ring1 & (cell == 1))
    cv.put(MAT_OR, np.full((N, N), 3) + base, ring2 & (cell == 0))
    cv.put(MAT_BR, np.full((N, N), 2) + base, ring2 & (cell == 1))
    cv.put(MAT_BR, np.full((N, N), 1), core)
    # small diamonds between the circles
    dm = (np.abs(lx - 0) + np.abs(ly - 0) <= 1) | (np.abs(lx - 16) + np.abs(ly - 0) <= 1) | (np.abs(lx) + np.abs(ly - 16) <= 1)
    dm |= (np.abs(X % 16 - 15.5) + np.abs(Y % 16 - 15.5) <= 1.5)
    cv.put(MAT_BR, np.full((N, N), 2), dm & (d > 7.4))
    cv.tint('#b8a882', 0.16 + 0.06 * (f > 0.6))          # fifty years of light, smoke and mate: faded, yellowed
    return cv


@painter('empapelado_matrimonial')
def p_empapelado_matrimonial(v):
    """VAR variants: v0-7 clean, v8 a vertical seam opening, v9 a sun-faded area and a damp corner."""
    cv = mat_paper(v)
    X, Y = cv.X, cv.Y
    v = {8: 1, 9: 2}.get(v, 0)
    if v == 1:
        cv.put(WHITEP, np.full((N, N), 3), (X == 16) & (Y > 3) & (Y < 26))
        cv.tint('#000000', np.where((X == 17) & (Y > 3) & (Y < 26), 0.25, 0))
    if v == 2:
        cv.tint('#d8caa0', np.where(fbm(N, N, 7820, cells=2, octaves=2) > 0.45, 0.2, 0))
        st = blob(N, N, 25, 6, 9, 7, 7821, rough=0.4) & (border_dist(N, N) > 1)
        cv.tint('#4a3016', np.where(st, 0.22, 0))
        cv.tint('#3a2410', np.where(st & ~erode(st, 1, False), 0.45, 0))
    return cv.out()


@painter('empapelado_matrimonial_zocalo')
def p_empapelado_matrimonial_zocalo(v):
    cv = mat_paper(v + 10)
    grime_band(cv, 16, 26, amount=0.16, seed=7830)
    skirting(cv, CEDRO, top=25, seed=7830 + v, chips=v, scuffs=2)
    return cv.out()


@painter('cemento_lavadero')
def p_cemento_lavadero(v, foot=False):
    """Laundry room: sponge-floated grey cement render (fratachado): overlapping swirls of the float, a few pits.
    VAR variants: v0-7 clean (v3/v6 a pale salt streak), v8 a crack and an old plug hole, v9 a short rust run.
    foot=True (casa_cemento_lavadero_zocalo): the bottom course, a dark grime band from mops, splashes and damp."""
    cv = Cv()
    X, Y = cv.X, cv.Y
    idx = cement_idx(v + (40 if foot else 0), 7900, contrast=0.45, sweeps=dict(count=3, radius=(10.0, 18.0), length=(10.0, 16.0), tilt=0.7),
                     pits=3, tool=0.6)
    if not foot and v == 8:
        idx, _ = crack_line(idx, [(5, 8), (12, 12), (18, 11), (27, 19)], 7904, amp=2, dark=2, lip=0.6)
        idx[20, 9] -= 2.5                                                    # an old plug hole
        idx[21, 9] += 0.8
    cv.put(LAV, idx)
    if not foot and v == 9:
        st = (np.abs(X - 15 - np.sin(Y / 4.0)) < 1.1) & (Y > 2) & (Y < 20)
        cv.tint('#6a3a1a', np.where(st, 0.28 * (1 - Y / 24.0), 0))
    if not foot and v in (3, 6):
        efflorescence(cv, [8, 23][v == 6], [4, 9][v == 6], 14, 7930 + v)
    if foot:
        hw_ = np.sin(np.pi * (X + 0.5) / N)
        top = 19 + np.round(1.0 * np.sin((X + 5) / 32 * 2 * math.pi) + 4 * hw_ * (vnoise(N, N, 5, 1, 7940 + v) - 0.5)).astype(int)
        t = np.clip((Y - top) / 10.0, 0, 1)
        cv.tint('#22251c', np.where(Y >= top, 0.18 + 0.32 * t, 0))
        cv.tint('#1a1c14', np.where((Y == top) & (fbm(N, N, 7941 + v, cells=8, octaves=1) > 0.3), 0.25, 0))
        salt_bloom(cv, (Y < top) & (Y > top - 3) & (fbm(N, N, 7942, cells=4, octaves=2) > 0.5), 7943 + v, strength=0.4, density=0.35)
        for (x, y) in poisson(7944 + v, 6, 4, keep=lambda x, y: y > 24):
            cv.tint('#3a3224', np.where(disc(x, y, 1.2), 0.25, 0))
        cv.tint('#141410', np.where(Y >= 30, 0.3, 0))
    return cv.out()


PAINTERS['cemento_lavadero_zocalo'] = lambda v: p_cemento_lavadero(v, foot=True)


# --- tiles
GROUT_L = Ramp('#56534d', '#6c6963', '#827f78', '#97948c', '#a9a69e', '#bab7af', '#c8c5bd')   # clean cement grout


def tile_grid(ramp, v, seed, size=8, base=5, mottle=True, grout_base=4, grout_ramp=GROUT_L, tone_amp=0.5):
    """Glazed wall tiles, 15x15 cm (8 px with the joint): 1 px light-mid grey cement grout, a 1 px lit bevel along
    the top/left of every glazed face, a faint shade on its bottom/right, one specular glint per tile."""
    cv = Cv()
    X, Y = cv.X, cv.Y
    grout = (X % size == 0) | (Y % size == 0)
    nt = N // size
    lab = np.where(grout, -1, (Y // size) * nt + X // size)
    rc = np.random.default_rng(seed + 977 * v)          # each tile is its own piece: the tones reshuffle per variant
    tone = rc.choice([-1, 0, 0, 0, 1], nt * nt) * tone_amp
    li = np.maximum(lab, 0)
    idx = base + tone[li]
    lx, ly = X % size, Y % size
    if mottle:   # glazed tiles: the mottling is in the glaze, soft
        mo = cblend(fbm(N, N, seed + 1, cells=8, octaves=2), fbm(N, N, seed + 3 + 31 * v, cells=8, octaves=2))
        idx = idx + np.where(mo > 0.7, 0.5, 0) - np.where(mo < 0.28, 0.5, 0)
    idx = np.where(((ly == 1) | (lx == 1)) & ~grout, idx + 0.8, idx)
    idx = np.where(((ly == size - 1) | (lx == size - 1)) & ~grout, idx - 0.3, idx)
    spec = (lx + ly == 4) & (lx == 2) & (tone[li] >= 0)
    idx = np.where(spec, idx + 2.0, idx)
    cv.put(ramp, idx, ~grout)
    gidx = np.full((N, N), grout_base) + posterize(fbm(N, N, seed + 2, cells=16, octaves=1), [(0.7, 1), (0.25, -1)])
    cv.put(grout_ramp, gidx, grout)
    return cv, lab, grout


TILE_CRACKS = [(2, 1), (1, 2), (3, 0), (0, 3)]   # which tile (column, row) cracks in the crack variant


def tile_crack(cv, grout, seed, t, size=8):
    tx, ty = t
    x0, y0 = tx * size + 1, ty * size + 1
    pts = wander([(x0 + 1, y0 + 1), (x0 + 3, y0 + 4), (x0 + size - 2, y0 + size - 3)], seed + 12, amp=0.8)
    cm = path_mask(pts, wrap=False) & ~grout
    cv.col('#1a1a14', cm)
    cv.tint('#ffffff', np.where(nb(cm, -1, 0, False) & ~cm & ~grout, 0.3, 0))


def tile_hole(cv, t, size=8):
    """A missing tile: the cement bed with the comb marks of the adhesive, the neighbours' raw edges."""
    X, Y = cv.X, cv.Y
    x0, y0 = t[0] * size + 1, t[1] * size + 1
    hole = rect(x0 - 1, y0 - 1, x0 + size - 1, y0 + size - 1)
    cidx = np.full((N, N), 3) + (((X + Y) % 3) == 0) - ((Y == y0 - 1) | (X == x0 - 1))
    cv.put(CEMENT, cidx, hole)
    r = rim(hole, wrap=False)
    cv.tint('#ffffff', np.where(r['out_below'], 0.2, 0))


def tile_dirty(cv, grout, seed, moss=False):
    """Dark, dirty grout (near the floor, the tap, the bath): soot-grey joints, splashes, mould for the bathroom."""
    X, Y = cv.X, cv.Y
    gd = cblend(fbm(N, N, seed + 10, cells=8, octaves=1), fbm(N, N, seed + 13, cells=8, octaves=1))
    cv.put(GROUT, np.full((N, N), 4.0) - np.clip((Y - 8) / 16.0, 0, 1) * 1.6 + (gd > 0.6) * 0.6 - (gd < 0.25) * 0.6, grout)
    if moss:
        cv.put(MOSS, np.full((N, N), 1) + (fbm(N, N, seed + 14, cells=16, octaves=1) > 0.6), grout & (Y > 14) & (fbm(N, N, seed + 15, cells=8, octaves=1) > 0.4))
        cv.put(SOOT, np.full((N, N), 2), grout & (Y > 24))
    for k, (x, y) in enumerate(poisson(seed + 11, 8, 4, keep=lambda x, y: 2 < x < 30 and 2 < y < 30)):
        cv.tint('#5a4a1c', np.where(disc(x, y, 1.0 + (k % 2) * 0.6) & ~grout, 0.22, 0))


@painter('azulejo_verde')
def p_azulejo_verde(v, kind=None):
    """70s mottled avocado-green kitchen tiles, 4x4 per block. VAR variants: v0-7 clean, v8 one cracked tile,
    v9 a few grease drops. Hand-placed: 'falta' (a tile gone: v0/v1 different tiles), 'sucio' (dark greasy grout,
    for the course behind the stove and the sink)."""
    cv, lab, grout = tile_grid(AZV, v, 8000, base=5)
    if kind == 'falta':
        tile_hole(cv, [(1, 2), (2, 1)][v % 2])
    elif kind == 'sucio':
        tile_dirty(cv, grout, 8010 + v)
    elif v == 8:
        tile_crack(cv, grout, 8010, TILE_CRACKS[0])
    elif v == 9:
        for k, (x, y) in enumerate(poisson(8011, 4, 6, keep=lambda x, y: 3 < x < 29 and 3 < y < 29)):
            cv.tint('#5a4a1c', np.where(disc(x, y, 0.8 + (k % 2) * 0.5) & ~grout, 0.25, 0))
    return cv.out()


GUARDA = ['...b...', '..bOb..', '.bOyOb.', 'bOyhyOb', '.bOyOb.', '..bOb..', '...b...']


@painter('azulejo_verde_guarda')
def p_azulejo_verde_guarda(v):
    """Top course of the kitchen tiling: plain green rows and, as the top row, the decorated 70s border
    (a chain of orange diamonds outlined in brown on cream, linked across the grout)."""
    cv, lab, grout = tile_grid(AZV, v, 8020, base=5)
    X, Y = cv.X, cv.Y
    band = (Y >= 1) & (Y <= 7) & ~grout
    lx, ly = X % 8, Y % 8
    cv.put(GUARDA_CR, np.full((N, N), 3) - (ly == 7) + (ly == 1), band)
    corner = band & ((np.minimum(lx - 1, 7 - lx) + np.minimum(ly - 1, 7 - ly)) <= 1)
    cv.put(GUARDA_OR, np.full((N, N), 1), corner)
    for t in range(4):
        stamp_ascii(cv, GUARDA, t * 8 + 1, 1, {'b': (GUARDA_BR, 1), 'O': (GUARDA_OR, 2), 'y': (GUARDA_OR, 4), 'h': (GUARDA_CR, 4)})
    cv.put(GROUT_L, np.full((N, N), 3), grout & (Y <= 8))
    cv.put(GUARDA_BR, np.full((N, N), 1), (Y == 4) & (X % 8 == 0))   # the diamonds link across the joints
    return cv.out()


@painter('azulejo_celeste')
def p_azulejo_celeste(v, kind=None):
    """Light-blue bathroom tiles (4x4). VAR variants: v0-7 clean, v8 one cracked tile, v9 a rust run from above.
    Hand-placed: 'falta' (missing tile), 'sucio' (dark mouldy grout for the course by the floor, bath and tap)."""
    cv, lab, grout = tile_grid(AZC, v, 8100, base=5, mottle=False, grout_base=5, tone_amp=0.3)
    X, Y = cv.X, cv.Y
    if kind == 'falta':
        tile_hole(cv, [(2, 2), (1, 1)][v % 2])
    elif kind == 'sucio':
        tile_dirty(cv, grout, 8110 + v, moss=True)
    elif v == 8:
        tile_crack(cv, grout, 8120, TILE_CRACKS[1])
    elif v == 9:
        st = (np.abs(X - 22 - np.round(np.sin(Y / 5.0) * 0.5)) <= 0.5) & (Y > 3) & ~grout
        cv.tint('#8a5428', np.where(st, 0.08 + 0.14 * (Y / 32.0), 0))
    return cv.out()


for _nm, _fn in (('azulejo_verde', p_azulejo_verde), ('azulejo_celeste', p_azulejo_celeste)):
    for _kd in ('falta', 'sucio'):
        PAINTERS[f'{_nm}_{_kd}'] = (lambda fn, kd: (lambda v: fn(v, kd)))(_fn, _kd)


@painter('azulejo_celeste_guarda')
def p_azulejo_celeste_guarda(v):
    """Top course of the bathroom tiling: a navy listel (half-height strip tiles with a wave) over plain rows."""
    cv, lab, grout = tile_grid(AZC, v, 8130, base=5, mottle=False, grout_base=5, tone_amp=0.3)
    X, Y = cv.X, cv.Y
    band = (Y >= 1) & (Y <= 4) & (X % 8 != 0)
    cv.put(NAVY, np.full((N, N), 2) + (Y == 1) - (Y == 4), band)
    wave = (np.abs(Y - 2.5 - np.round(np.sin(X / 8.0 * 2 * math.pi) * 1.2)) < 0.6) & band
    cv.put(AZC, np.full((N, N), 7), wave)
    cv.put(GROUT_L, np.full((N, N), 5), (Y == 5) | ((Y < 5) & (X % 8 == 0)))
    cv.put(AZC, np.full((N, N), 5), (Y >= 6) & (Y <= 7) & (X % 8 != 0))
    return cv.out()


# =============================================================================================== FLOORS
def herringbone():
    """Labels of the herringbone parquet: 16 strips of 4x16 px (8 horizontal, 8 vertical), exact 32 px period."""
    lab = -np.ones((N, N), int)
    horiz = np.zeros((N, N), bool)
    w, L = 4, 16
    seen = {}
    for a in range(-20, 21):
        for b in range(-8, 9):
            ox, oy = a * w + b * L, a * w - b * L
            for typ in 'HV':
                key = (typ, ox % N, oy % N)
                if key in seen:
                    continue
                seen[key] = len(seen)
                if typ == 'H':
                    xs, ys = range(ox, ox + L), range(oy, oy + w)
                else:
                    xs, ys = range(ox, ox + w), range(oy + w, oy + w + L)
                for x in xs:
                    for y in ys:
                        lab[y % N, x % N] = seen[key]
                        horiz[y % N, x % N] = typ == 'H'
    return lab, horiz


_HB = herringbone()


def parquet_idx(v, seed=0):
    lab, horiz = _HB
    X, Y = G_X, G_Y
    rc = np.random.default_rng(8200 + seed)
    tone = rc.choice([-1, -1, 0, 0, 0, 0, 1, 1, 2], lab.max() + 1)
    if v:   # strips that stay inside the block take new tones in every variant (seamless: border strips are shared)
        rv = np.random.default_rng(8205 + seed + 13 * v)
        bd = border_dist(N, N)
        for k in range(lab.max() + 1):
            if not ((lab == k) & (bd < 1)).any():
                tone[k] = rv.choice([-1, -1, 0, 0, 0, 0, 1, 1, 2])
    gh = wood_grain(N, N, 8210 + seed, 'x', warp=0.7, pores=0.03, tones=(-1, 0, 0, 1))
    gv = wood_grain(N, N, 8211 + seed, 'y', warp=0.7, pores=0.03, tones=(-1, 0, 0, 1))
    idx = 5 + tone[lab] + np.where(horiz, gh, gv)
    up = nb(lab, 1, 0)
    lf = nb(lab, 0, 1)
    dn = nb(lab, -1, 0)
    rt = nb(lab, 0, -1)
    idx = np.where((dn != lab) | (rt != lab), idx - 2, idx)
    idx = np.where(((up != lab) | (lf != lab)) & (dn == lab) & (rt == lab), idx + 1, idx)
    return idx, lab, horiz


@painter('parquet')
def p_parquet(v, kind=None):
    """Varnished oak herringbone parquet (espina de pez), honey-brown, dulled by decades of wax. VAR variants:
    v0-8 clean (the strips' tones and the wax sheen reshuffle), v9 faint scratches from dragged chairs.
    kind='mancha' (hand-placed): the dark ring of a flowerpot and a dull water mark beside it."""
    cv = Cv()
    idx, lab, horiz = parquet_idx(v)
    sheen = cblend(fbm(N, N, 8220, cells=2, octaves=2), fbm(N, N, 8221 + v, cells=2, octaves=2))
    idx = idx + np.where(sheen > 0.8, 1, 0)
    cv.put(PARQ, idx)
    if kind == 'mancha':
        cx, cy = (15.5, 16.5) if v % 2 == 0 else (12.5, 13.5)
        d = np.sqrt((cv.X - cx) ** 2 + (cv.Y - cy) ** 2)
        cv.tint('#1a0e06', np.where(np.abs(d - 6) < 0.8, 0.4, 0))
        cv.tint('#1a0e06', np.where(d < 5.2, 0.12, 0))
        wm = blob(N, N, cx + 9, cy + 7, 4, 3, 8225 + v, rough=0.4) & (border_dist(N, N) > 1)
        cv.tint('#b8a080', np.where(wm, 0.18, 0))
    elif v == 9:   # scratches from dragged chairs
        for k in range(3):
            pts = line_px(4 + k * 3, 9 + k * 7, 25 + k, 11 + k * 7)
            m = path_mask(pts, wrap=False)
            cv.tint('#c8a070', np.where(m, 0.22, 0))
    return cv.out()


PAINTERS['parquet_mancha'] = lambda v: p_parquet(v, 'mancha')


@painter('parquet_gastado')
def p_parquet_gastado(v):
    """Worn parquet: the varnish gone grey on the walking path. VAR variants: v0-7 worn only, v8 a missing strip
    (black bitumen), v9 a lifted strip."""
    cv = Cv()
    idx, lab, horiz = parquet_idx(v, seed=5)
    X, Y = cv.X, cv.Y
    worn = rank(cblend(fbm(N, N, 8230, cells=2, octaves=3), fbm(N, N, 8231 + v, cells=2, octaves=3))) > 0.45
    cv.put(PARQ, idx)
    inner = worn & ((nb(lab, -1, 0) == lab) & (nb(lab, 0, -1) == lab))
    cv.tint('#8a7458', np.where(inner, 0.38, 0))      # varnish gone: greyer, flatter, a bit lighter
    cv.tint('#2a1c10', np.where(inner & (rank(fbm(N, N, 8232 + v, cells=8, octaves=1)) > 0.8), 0.25, 0))
    v = {8: 1, 9: 2}.get(v, 0)
    if v == 1:   # missing strip
        k = lab[13, 18]
        hole = lab == k
        cv.put(Ramp('#0c0a08', '#15110d', '#1e1913'), np.full((N, N), 1) + ((X * 2 + Y) % 5 == 0), hole)
        r = rim(hole, wrap=True)
        cv.put(PARQ, np.full((N, N), 1), r['out_below'] | r['out_right'])
    if v == 2:   # lifted strip (cupped): bright ridge and a shadow line along it
        k = lab[20, 8]
        st = lab == k
        r = rim(st, wrap=True)
        cv.put(PARQ, np.full((N, N), 8), st & ~r['in_bot'] & ~r['in_right'] & (nb(st, 1, 0) | nb(st, 0, 1)) & ~(nb(st, -1, 0) & nb(st, 0, -1)))
        cv.put(PARQ, np.full((N, N), 0), r['out_below'] | r['out_right'])
    return cv.out()


def gran_tile(cv, x0, y0, s, seed, wear=0, crack=None, stain=None):
    """One granítico tile: warm grey cement matrix, fine chips (dark, pale, terracotta), polished but dull."""
    X, Y = cv.X, cv.Y
    m = rect(x0, y0, x0 + s - 1, y0 + s - 1)
    f = fbm(N, N, seed, cells=4, octaves=2)
    idx = np.full((N, N), 5) + posterize(f, [(0.72, 1), (0.3, -1)])
    cv.put(GRAN, idx, m)
    rng = np.random.default_rng(seed)
    cols = [('#4a4540', 0.38), ('#d2cbbd', 0.30), ('#8a5a48', 0.17), ('#a89070', 0.15)]
    pts = poisson(seed + 1, 22, 2.4, keep=lambda x, y: x0 <= x < x0 + s and y0 <= y < y0 + s, wrap=False)
    for k, (x, y) in enumerate(pts):
        c = cols[int(rng.choice(4, p=[c[1] for c in cols]))][0]
        cv.tint(c, np.where((X == x) & (Y == y), 0.75, 0))
        if k % 4 == 0 and x + 1 < x0 + s:
            cv.tint(c, np.where((X == x + 1) & (Y == y), 0.6, 0))
    for (x, y) in poisson(seed + 2, 30, 1.6, keep=lambda x, y: x0 <= x < x0 + s and y0 <= y < y0 + s, wrap=False):
        cv.tint('#2e2a26', np.where((X == x) & (Y == y), 0.3, 0))
    r = rim(m, wrap=False)
    cv.tint('#ffffff', np.where(r['in_top'] | r['in_left'], 0.10, 0))
    cv.tint('#000000', np.where(r['in_bot'] | r['in_right'], 0.12, 0))
    if crack is not None:
        cm = path_mask(wander(crack, seed + 3, amp=0.8), wrap=False) & m
        cv.col('#24201c', cm)
        cv.tint('#ffffff', np.where(nb(cm, -1, 0, False) & m & ~cm, 0.12, 0))
    return m


@painter('granitico')
def p_granitico(v, kind='clean'):
    """Granítico (terrazzo tiles), 2x2 per block: warm grey with black/white/red chips. Hall and kitchen."""
    cv = Cv()
    X, Y = cv.X, cv.Y
    joint = (X % 16 == 0) | (Y % 16 == 0)
    cv.put(GROUT, np.full((N, N), 2), joint)
    for ty in range(2):
        for tx in range(2):
            crack = None
            if kind == 'roto' and (tx, ty) in (((v + 1) % 2, v % 2), (1, 1)):
                crack = [(tx * 16 + 2, ty * 16 + 3 + v * 3), (tx * 16 + 8, ty * 16 + 9), (tx * 16 + 15, ty * 16 + 7 + v * 2)]
            gran_tile(cv, tx * 16 + 1, ty * 16 + 1, 15, 8300 + v * 4 + ty * 2 + tx + (40 if kind == 'roto' else 0), crack=crack)
    if kind == 'roto' and v == 2:   # a chipped corner and a dark tide from mopping
        cv.put(CEMENT, np.full((N, N), 3), (np.abs(X - 17) + np.abs(Y - 17) <= 2) & ~joint)
    if kind == 'roto':
        cv.tint('#3a3020', np.where(fbm(N, N, 8340 + v, cells=2, octaves=2) > 0.6, 0.15, 0))
    return cv.out()


PAINTERS['granitico_roto'] = lambda v: p_granitico(v, 'roto')

PETAL = ['pp...pp', 'p.....p', '.......', '.......', '.......', 'p.....p', 'pp...pp']


MARMOL = Ramp('#5e5d5a', '#7a7976', '#959490', '#aeada8', '#c2c1bc', '#d2d1cc', '#dedcd7', '#e8e7e2')


@painter('umbral_marmol')
def p_umbral_marmol(v):
    """Door threshold (umbral): one slab of worn grey-veined marble filling the block under a door, a 1 px joint all
    round (direction-free, so it fits doors in either wall), the polish walked off in the middle, grime in the joint."""
    cv = Cv()
    X, Y = cv.X, cv.Y
    f = fbm(N, N, 8450 + v, cells=2, octaves=3)
    idx = np.full((N, N), 5.0) + posterize(f, [(0.72, 1), (0.25, -1)]) * 0.5
    vm = np.zeros((N, N), bool)
    for k, pts in enumerate(([(2, 6 + v * 3), (11, 9), (19, 7), (30, 12)], [(4, 27), (13, 21 - v * 2), (22, 23), (29, 18)])):
        vm |= path_mask(wander(pts, 8455 + k + 3 * v, amp=2.2), wrap=False)
    vm &= fbm(N, N, 8457 + v, cells=8, octaves=1) > 0.22                     # veins fade in and out
    idx = idx - np.where(vm, 1.1, 0) - np.where(dilate(vm, 1, False) & ~vm & (fbm(N, N, 8458 + v, cells=8, octaves=1) > 0.5), 0.35, 0)
    worn = (np.abs(X - 15.5) < 9) & (np.abs(Y - 15.5) < 12)
    idx = np.where(worn, idx - 0.35, idx)
    joint = (X == 0) | (Y == 0)
    idx = np.where((X == 1) | (Y == 1), idx + 0.6, idx)
    idx = np.where((X == 31) | (Y == 31), idx - 0.5, idx)
    cv.put(MARMOL, idx, ~joint)
    cv.put(GROUT, np.full((N, N), 2), joint)
    cv.tint('#5a4a30', np.where(worn & (fbm(N, N, 8459 + v, cells=4, octaves=2) > 0.6), 0.1, 0))
    return cv.out()


@painter('ceramica_cocina')
def p_ceramica_cocina(v):
    """Kitchen floor ceramic (cream glaze, a brown four-petal print at every corner meeting -> a lattice of flowers)."""
    cv = Cv()
    X, Y = cv.X, cv.Y
    joint = (X % 16 == 0) | (Y % 16 == 0)
    lx, ly = X % 16, Y % 16
    f = cblend(fbm(N, N, 8400, cells=4, octaves=2), fbm(N, N, 8401 + v, cells=4, octaves=2))
    idx = np.full((N, N), 5) + posterize(f, [(0.75, 1), (0.25, -1)])
    idx = np.where((lx == 1) | (ly == 1), idx + 1, idx)
    idx = np.where((lx == 15) | (ly == 15), idx - 1, idx)
    cv.put(CERAM, idx, ~joint)
    # quarter flowers in each corner (form a flower over each joint crossing) + centre diamond
    dc = np.minimum(lx, 16 - lx) ** 2 + np.minimum(ly, 16 - ly) ** 2
    petal = ~joint & (dc <= 20) & (dc >= 6) & ((np.minimum(lx, 16 - lx) <= 2) | (np.minimum(ly, 16 - ly) <= 2))
    cv.put(CERAM_P, np.full((N, N), 2), petal)
    cv.put(CERAM_P, np.full((N, N), 1), ~joint & (dc <= 4))
    dia = (np.abs(lx - 8) + np.abs(ly - 8) <= 2) & ~joint
    cv.put(CERAM_P, np.full((N, N), 3) - (np.abs(lx - 8) + np.abs(ly - 8) <= 0), dia)
    cv.put(GROUT, np.full((N, N), 3), joint)
    if v == 8:   # glaze worn off on one tile (in front of the sink): matte biscuit
        w = (rank(fbm(N, N, 8410, cells=2, octaves=3)) > 0.5) & (G_X > 16) & (G_Y > 16)
        cv.tint('#9a8466', np.where(w & ~joint, 0.3, 0))
    if v == 9:   # one cracked tile and a faint yerba stain on another
        pts = wander([(3, 20), (9, 22), (14, 27)], 8420, amp=0.8)
        cv.col('#2a2016', path_mask(pts, wrap=False) & ~joint)
        cv.tint('#4a3010', np.where(disc(22, 9, 2.6) & ~joint, 0.18, 0))
    return cv.out()


@painter('baldosa_patio')
def p_baldosa_patio(v):
    """Red cement patio tiles (baldosa colorada), 4x4: sun-faded unevenly, moss in the joints. VAR variants: v0-7
    clean (the tiles' tones reshuffle), v8 a cracked tile, v9 a tile replaced with grey cement."""
    cv = Cv()
    X, Y = cv.X, cv.Y
    joint = (X % 8 == 0) | (Y % 8 == 0)
    lab = np.where(joint, -1, (Y // 8) * 4 + X // 8)
    rc = np.random.default_rng(8500 + 31 * v)
    tone = rc.choice([-1, 0, 0, 1, 1], 16)
    li = np.maximum(lab, 0)
    f = cblend(fbm(N, N, 8501, cells=4, octaves=2), fbm(N, N, 8502 + v, cells=4, octaves=2))
    idx = 4 + tone[li] + posterize(f, [(0.72, 1), (0.28, -1)])
    lx, ly = X % 8, Y % 8
    idx = np.where((lx == 1) | (ly == 1), idx + 1, idx)
    idx = np.where((lx == 7) | (ly == 7), idx - 1, idx)
    cv.put(PATIO_R, idx, ~joint)
    cv.tint('#c8a080', np.where(rank(fbm(N, N, 8503 + v, cells=2, octaves=2)) > 0.7, 0.18, 0) * ~joint)
    jn = fbm(N, N, 8504 + v, cells=16, octaves=1)
    cv.put(EARTH, np.full((N, N), 2), joint)
    cv.put(MOSS, np.full((N, N), 2) + (jn > 0.7), joint & (jn > 0.45))
    if v == 8:
        cm = path_mask(wander([(9, 10), (12, 12), (15, 14)], 8510, amp=0.6), wrap=False) & ~joint
        cv.col('#1e0c08', cm)
    if v == 9:
        t = rect(1, 17, 7, 23)
        cv.put(CEMENT, np.full((N, N), 4) + posterize(fbm(N, N, 8520, cells=8, octaves=1), [(0.6, 1)]), t)
    return cv.out()


@painter('ladrillo_patio')
def p_ladrillo_patio(v):
    """Patio paving of common brick laid flat in basket weave at real size (25 x 12 cm: 8 x 4 px with the joint),
    sun-faded and dusty, sandy joints with moss. VAR variants: v0-6 clean, v7 grease and ash from the grill, v8 a
    cracked brick, v9 a sunken pair holding a film of dirt."""
    cv = Cv()
    X, Y = cv.X, cv.Y
    cx, cy = X // 8, Y // 8
    lx, ly = X % 8, Y % 8
    horiz = (cx + cy) % 2 == 0
    sub = np.where(horiz, ly // 4, lx // 4)
    joint = np.where(horiz, (ly % 4 == 3) | (lx == 7), (lx % 4 == 3) | (ly == 7))
    lab = np.where(joint, -1, (cy * 4 + cx) * 2 + sub)
    rc = np.random.default_rng(8600)
    tone = rc.choice([-2, -1, -1, 0, 0, 0, 1, 1, 2], 32)
    rv = np.random.default_rng(8605 + v)
    inner = [k for k in range(32) if not ((lab == k) & (border_dist(N, N) < 1)).any()]
    for k in rv.choice(inner, 3, replace=False):
        tone[k] = rv.choice([-2, 2])
    li = np.maximum(lab, 0)
    f = cblend(fbm(N, N, 8601, cells=2, octaves=2), fbm(N, N, 8602 + v, cells=2, octaves=2))
    idx = 4.0 + tone[li] * 0.8 + posterize(f, [(0.72, 1), (0.28, -1)]) * 0.5
    lit = np.where(horiz, (ly % 4 == 0), (lx % 4 == 0)) & ~joint
    sh = np.where(horiz, (ly % 4 == 2), (lx % 4 == 2)) & ~joint
    idx = idx + lit * 0.9 - sh * 0.7
    for (x, y) in poisson(8603 + v, 26, 2.2):
        if lab[y, x] >= 0:
            idx[y, x] -= 1.2
    cv.put(BRICK, idx, ~joint)
    cv.tint('#8a7a66', np.where(~joint, 0.16 + 0.1 * (f > 0.6), 0))
    jn = fbm(N, N, 8604 + v, cells=16, octaves=1)
    cv.put(SAND, np.full((N, N), 2) + (jn > 0.5), joint)
    cv.put(MOSS, np.full((N, N), 1) + (jn > 0.85), joint & (jn > 0.72))
    if v == 7:
        cv.tint('#1a1612', np.where(blob(N, N, 16, 15, 9, 7, 8610, rough=0.4), 0.22, 0))
    if v == 8:
        cm = path_mask(wander([(17, 9), (19, 11), (18, 14)], 8620, amp=0.6), wrap=False) & ~joint
        cv.col('#2a120a', cm)
    if v == 9:
        pit = ((cx == 1) & (cy == 2))
        cv.tint('#3a3024', np.where(pit, 0.3, 0))
    return cv.out()


@painter('cemento_piso')
def p_cemento_piso(v):
    """Basement / laundry cement floor (alisado): wide steel-trowel sweeps, pits, a sparse grain. VAR variants:
    v0-6 clean (v2 and v5 an old repair patch, each in its own place), v7 a hairline crack, v8 a damp patch with
    salt, v9 a small oil stain."""
    cv = Cv()
    X, Y = cv.X, cv.Y
    idx = cement_idx(v, 8700, contrast=0.45, sweeps=dict(count=3, radius=(16.0, 30.0), length=(14.0, 22.0), tilt=1.2), pits=5, tool=0.6)
    if v == 2:
        idx, _ = cement_patch(idx, 11, 20, 6, 4.5, 8706)
    if v == 5:
        idx, _ = cement_patch(idx, 21, 10, 5, 5.5, 8707)
    if v == 7:
        idx, _ = crack_line(idx, [(4, 8), (12, 10), (19, 17), (27, 20)], 8703, amp=2.5)
    cv.put(CEMENT, idx)
    if v == 8:
        dd = np.sqrt(((G_X - 16) / 10.0) ** 2 + ((G_Y - 16) / 8.0) ** 2) + (fbm(N, N, 8720, cells=4, octaves=3) - 0.5) * 0.6
        cv.tint('#1e2218', np.clip((1.0 - dd) / 0.35, 0, 1) * 0.22 * (border_dist(N, N) > 1))         # a soft damp patch
        cv.tint('#1e2218', np.where((np.abs(dd - 0.95) < 0.05) & (border_dist(N, N) > 1), 0.12, 0))
    if v == 9:
        st = blob(N, N, 18, 14, 5, 4, 8710, rough=0.35) & (border_dist(N, N) > 2)
        cv.tint('#0e0c0a', np.where(st, 0.26, 0))
        cv.tint('#0e0c0a', np.where(erode(st, 1, False), 0.12, 0))
    return cv.out()


@painter('arena')
def p_arena(v, kind=None):
    """Packed sand floor of the 1961 room: ripples of old footsteps, grit. VAR variants: v0-8 clean, v9 a few old
    wax drips. Hand-placed: kind='pisadas' (a child's bare footprints), kind='arrastre' (drag marks)."""
    cv = Cv()
    X, Y = cv.X, cv.Y
    f = cblend(fbm(N, N, 8800, cells=4, octaves=3), fbm(N, N, 8801 + v, cells=4, octaves=3))
    idx = np.full((N, N), 4) + posterize(f, [(0.72, 1), (0.28, -1)])
    g = fbm(N, N, 8802, cells=16, octaves=1)
    idx = idx + np.where(g > 0.78, 1, 0) - np.where(g < 0.18, 1, 0)
    for (x, y) in poisson(8803 + v, 14, 4):
        idx[y, x] -= 2
        idx[(y - 1) % N, x] += 1
    cv.put(SAND, idx)
    v = {'pisadas': 1, 'arrastre': 2}.get(kind, 3 if v == 9 else 0)
    if v == 1:
        FOOT = ['.#.#.', '#.#..', '.###.', '.###.', '.###.', '..##.', '.###.', '.##..']
        fm = np.zeros((N, N), bool)
        stamp(fm, ascii_mask(FOOT), 7, 4)
        stamp(fm, ascii_mask(FOOT)[:, ::-1], 17, 17)
        cv.put(SAND, np.full((N, N), 1), fm)
        cv.put(SAND, np.full((N, N), 6), nb(fm, -1, 0, False) & ~fm)
    if v == 2:
        for x in (9, 10, 14, 15):
            m = (X == x) & (Y > 2) & (Y < 30)
            cv.put(SAND, np.full((N, N), 2), m)
        cv.put(SAND, np.full((N, N), 6), ((X == 11) | (X == 16)) & (Y > 2) & (Y < 30))
    if v == 3:
        for k, (x, y) in enumerate(poisson(8830, 4, 6, keep=lambda x, y: 3 < x < 29 and 3 < y < 29)):
            cv.put(Ramp('#8a8070', '#b0a690', '#d4ccba'), np.full((N, N), 1 + (k % 2)), disc(x, y, 1.0 + (k % 3) * 0.3))
    return cv.out()


PAINTERS['arena_pisadas'] = lambda v: p_arena(v + 20, 'pisadas')
PAINTERS['arena_arrastre'] = lambda v: p_arena(v + 30, 'arrastre')


def vainilla_tile(cv, x0, y0, horiz, seed):
    """One 15x15 'vainilla' sidewalk tile: three long rounded bars separated by grooves."""
    X, Y = cv.X, cv.Y
    lx, ly = X - x0, Y - y0
    m = (lx >= 0) & (lx < 15) & (ly >= 0) & (ly < 15)
    a, b = (lx, ly) if horiz else (ly, lx)       # a: along the bars, b: across
    bar = b // 5
    bb = b % 5
    groove = (bb == 4) | (a == 0) | (a == 14)
    idx = np.full((N, N), 5) + posterize(fbm(N, N, seed, cells=4, octaves=2), [(0.7, 1), (0.3, -1)])
    idx = np.where(bb == 0, idx + 1, idx)
    idx = np.where(bb == 3, idx - 1, idx)
    idx = np.where((a == 1) | (a == 13), idx - 1, idx)
    idx = np.where(groove, 2, idx)
    cv.put(VAINILLA, idx, m)
    return m


@painter('vereda')
def p_vereda(v, kind='clean'):
    """'Baldosa vainilla' sidewalk (2x2 tiles, bars alternating direction): yellow-grey cement, dirt in the grooves.
    'rota': cracks, a sunk tile, a missing one with earth and a weed, gum spots."""
    cv = Cv()
    X, Y = cv.X, cv.Y
    joint = (X % 16 == 15) | (Y % 16 == 15)
    cv.put(GROUT, np.full((N, N), 2), joint)
    for ty in range(2):
        for tx in range(2):
            vainilla_tile(cv, tx * 16, ty * 16, (tx + ty) % 2 == 0, 8900 + ty * 2 + tx + v * 4)
    cv.tint('#3a3426', np.where(fbm(N, N, 8910 + v, cells=2, octaves=2) > 0.6, 0.12, 0))
    if kind == 'rota':
        if v == 0:
            cm = path_mask(wander([(2, 4), (8, 9), (13, 8), (21, 17), (30, 20)], 8920, amp=1.2), wrap=False)
            cv.col('#1a1812', cm)
            cv.tint('#ffffff', np.where(nb(cm, -1, 0, False) & ~cm, 0.15, 0))
        if v == 1:   # missing tile: earth and a weed
            hole = rect(16, 0, 31, 14) & (border_dist(N, N) > 0)
            cv.put(EARTH, np.full((N, N), 2) + posterize(fbm(N, N, 8930, cells=8, octaves=2), [(0.6, 1), (0.3, -1)]), hole)
            r = rim(hole, wrap=False)
            cv.put(EARTH, np.full((N, N), 0), r['in_top'] | r['in_left'])
            weed = ascii_mask(['..#.#..', '#.#.#.#', '.#####.', '..###..', '...#...'])
            wm = np.zeros((N, N), bool)
            stamp(wm, weed, 21, 6)
            cv.put(GRASS, np.full((N, N), 4) + (cv.Y < 9), wm)
        if v == 2:   # sunk / lifted tile: dark rim on one side, bright on the other
            t = rect(0, 16, 14, 30)
            cv.mul(np.where(t, 0.85, 1.0))
            cv.put(VAINILLA, np.full((N, N), 7), (Y == 16) & (X < 15))
            cv.put(GROUT, np.full((N, N), 0), (X == 15) & (Y > 15))
        for k, (x, y) in enumerate(poisson(8940 + v, 4, 6)):
            cv.put(Ramp('#3a3a38', '#555552', '#6a6a66'), np.full((N, N), 1 + (k % 2)), disc(x, y, 1.0))
    return cv.out()


PAINTERS['vereda_rota'] = lambda v: p_vereda(v, 'rota')
PAINTERS['asfalto_bache'] = lambda v: p_asfalto(v + 20, 'bache')


@painter('cordon_top')
def p_cordon_top(v):
    """Granite curb top: calm grey granite with fine black/white grains, worn edge towards the street (north)."""
    cv = Cv()
    X, Y = cv.X, cv.Y
    f = fbm(N, N, 9000 + v, cells=2, octaves=2)
    idx = np.full((N, N), 4) + posterize(f, [(0.72, 1), (0.28, -1)])
    cv.put(GRANITE, idx)
    for k, (x, y) in enumerate(poisson(9001 + v, 60, 1.7)):
        cv.put(GRANITE, np.full((N, N), [1, 7, 2, 6][k % 4]), (X == x) & (Y == y))
    cv.put(GRANITE, np.full((N, N), 6), Y == 0)
    cv.put(GRANITE, np.full((N, N), 5), Y == 1)
    cv.put(GROUT, np.full((N, N), 2), X == 0)
    return cv.out()


@painter('cordon_side')
def p_cordon_side(v):
    cv = Cv()
    X, Y = cv.X, cv.Y
    f = fbm(N, N, 9010 + v, cells=2, octaves=2)
    idx = np.full((N, N), 3) + posterize(f, [(0.72, 1), (0.28, -1)])
    idx = np.where((Y % 3 == 0) & ((X * 5 + Y) % 7 < 3), idx - 1, idx)    # chisel tooling
    cv.put(GRANITE, idx)
    for k, (x, y) in enumerate(poisson(9011 + v, 50, 1.7)):
        cv.put(GRANITE, np.full((N, N), [1, 6, 2, 5][k % 4]), (X == x) & (Y == y))
    cv.put(GRANITE, np.full((N, N), 6), Y == 0)
    cv.put(GROUT, np.full((N, N), 2), X == 0)
    cv.tint('#2a2418', np.where(Y > 18, (Y - 18) / 26.0, 0))
    return cv.out()


@painter('asfalto')
def p_asfalto(v, kind=None):
    """Old asphalt of the pasaje: aggregate specks. VAR variants: v0-7 clean, v8 a tar-sealed crack, v9 a shorter
    one. kind='bache' (hand-placed): a pothole holding water."""
    cv = Cv()
    X, Y = cv.X, cv.Y
    f = cblend(fbm(N, N, 9100, cells=2, octaves=3), fbm(N, N, 9101 + v, cells=2, octaves=3))
    idx = np.full((N, N), 3) + posterize(f, [(0.72, 1), (0.25, -1)])
    for (x, y) in poisson(9102 + v, 60, 1.8):
        idx[y, x] += 2 if (x + y) % 3 else -1
    cv.put(ASPH, idx)
    if v in (8, 9) and kind is None:
        pts = [(2, 12), (10, 15), (19, 11), (29, 14)] if v == 8 else [(8, 25), (14, 21), (22, 22)]
        cm = path_mask(wander(pts, 9110 + v, amp=2.5), wrap=False)
        cv.col('#090909', dilate(cm, 1, False) & (fbm(N, N, 9111, cells=8, octaves=1) > 0.3) | cm)
    if kind == 'bache':
        ph = blob(N, N, 16, 17, 8, 6, 9120, rough=0.3)
        cv.put(ASPH, np.full((N, N), 1) + (fbm(N, N, 9121, cells=8, octaves=1) > 0.5), ph)
        water = erode(ph, 1, False)
        cv.put(Ramp('#0a0c10', '#141922', '#22293a', '#3a465a'), np.full((N, N), 1) + ((X - Y) % 7 == 0), water)
        r = rim(ph, wrap=False)
        cv.put(ASPH, np.full((N, N), 5), r['out_below'])
    return cv.out()


@painter('cesped_top')
def p_cesped_top(v):
    """Scruffy conurbano lawn seen from above: dense blades (lit tip, dark shadow beside), clover clumps, dry
    straw-coloured patches, a few specks of earth. Variants differ inside, share the border."""
    cv = Cv()
    X, Y = cv.X, cv.Y
    f = cblend(fbm(N, N, 9200, cells=4, octaves=3), fbm(N, N, 9201 + v, cells=4, octaves=3))
    idx = np.full((N, N), 3) + posterize(f, [(0.72, 1), (0.3, -1)])
    rng = np.random.default_rng(9205 + v)
    bd = border_dist(N, N)
    pts = poisson(9202, 60, 1.9, keep=lambda x, y: bd[int(y), int(x)] < 3) + \
          poisson(9206 + v, 110, 1.9, keep=lambda x, y: bd[int(y), int(x)] >= 3)
    for k, (x, y) in enumerate(pts):
        L = 2 + (k % 3 == 0)
        lean = (k % 4) - 1.5
        for j in range(L):
            xx = int(round(x + lean * j * 0.4)) % N
            yy = (y - j) % N
            idx[yy, xx] = 6 if j == L - 1 else 5
        idx[y % N, (x + 1) % N] = min(idx[y % N, (x + 1) % N], 1)
    cv.put(GRASS, idx)
    dry = rank(cblend(fbm(N, N, 9210, cells=2, octaves=2), fbm(N, N, 9211 + v, cells=2, octaves=2))) > 0.72
    cv.tint('#8a8648', np.where(dry, 0.30, 0) * (idx >= 4))
    cv.tint('#4a4a2a', np.where(dry, 0.15, 0) * (idx < 4))
    for (x, y) in poisson(9212 + v, 3, 9, keep=lambda x, y: bd[int(y), int(x)] >= 4):
        clov = ((X - x) ** 2 + (Y - y) ** 2 <= 4.5) & ((X + Y) % 2 == 0)
        cv.put(GRASS, np.full((N, N), 2), clov)
        cv.put(GRASS, np.full((N, N), 4), clov & (Y < y))
    for (x, y) in poisson(9213 + v, 5, 6, keep=lambda x, y: bd[int(y), int(x)] >= 2):
        cv.put(EARTH, np.full((N, N), 3), (X == x) & (Y == y))
    return cv.out()


@painter('cesped_side')
def p_cesped_side(v):
    """Side of the lawn block: a ragged turf edge (blade tips of uneven height, light and dark, never a smooth drip
    line), a dark humus mat full of pale roots, then the soil with pebbles."""
    cv = Cv()
    X, Y = cv.X, cv.Y
    f = fbm(N, N, 9210 + v, cells=4, octaves=2)
    cv.put(EARTH, np.full((N, N), 3) + posterize(f, [(0.7, 1), (0.3, -1)]))
    for (x, y) in poisson(9211 + v, 9, 4, keep=lambda x, y: y > 12):
        cv.put(MORTAR, np.full((N, N), 3 + (x % 2)), (X == x) & (Y == y))
        cv.put(MORTAR, np.full((N, N), 1), (X == x) & (Y == y + 1))
    rng = np.random.default_rng(9212 + v)
    turf = np.array([int(rng.choice([2, 3, 3, 4, 4, 5, 6])) for _ in range(N)])     # how deep the green reaches
    turf[0], turf[-1] = 4, 4
    humus = Y < turf[None, :] + 4
    cv.put(EARTH, np.full((N, N), 1) + (f > 0.6), humus)
    for k in range(7):                                                              # roots: thin pale threads
        x0 = int(rng.integers(1, 31))
        pts = wander([(x0, 4), (x0 + int(rng.integers(-3, 4)), 9 + int(rng.integers(0, 6)))], 9213 + v * 11 + k, amp=1.2, depth=2)
        rm = path_mask(pts, wrap=False)
        cv.put(Ramp('#5a4a32', '#7a6644', '#9a8458'), np.full((N, N), 1 + (k % 2)), rm & (Y > 3))
    green = Y < turf[None, :]
    gidx = np.full((N, N), 4) + ((X * 7 + Y * 3) % 5 == 0) - ((X * 3 + Y) % 4 == 0)
    gidx = np.where(Y == 0, 6, gidx)
    cv.put(GRASS, gidx, green)
    for x in range(N):                                                              # blade tips catching light
        if rng.random() < 0.45:
            cv.put(GRASS, np.full((N, N), 6 + (rng.random() < 0.3)), (X == x) & (Y <= int(rng.integers(1, 3))))
        if rng.random() < 0.25:
            cv.put(GRASS, np.full((N, N), 1), (X == x) & (Y == turf[x] - 1))
    cv.tint('#8a8648', np.where(green & (vnoise(N, N, 6, 2, 9214 + v) > 0.65), 0.25, 0))   # dry straw blades
    return cv.out()


@painter('tierra')
def p_tierra(v):
    cv = Cv()
    X, Y = cv.X, cv.Y
    f = cblend(fbm(N, N, 9300, cells=4, octaves=3), fbm(N, N, 9301 + v, cells=4, octaves=3))
    idx = np.full((N, N), 3) + posterize(f, [(0.7, 1), (0.3, -1)])
    for (x, y) in poisson(9302 + v, 30, 2.5):
        idx[y, x] -= 1
    cv.put(EARTH, idx)
    for k, (x, y) in enumerate(poisson(9303 + v, 7, 6)):
        cv.put(MORTAR, np.full((N, N), 4 + (k % 2)), (X == x) & (Y == y))
        cv.put(MORTAR, np.full((N, N), 2), (X == x) & (Y == (y + 1) % N))
    return cv.out()


# =============================================================================================== CEILINGS
@painter('cielorraso')
def p_cielorraso(v):
    """Smooth plaster ceiling (látex, yellowed). VAR variants: v0-7 clean, v8 a hairline crack along the slab joint,
    v9 fly specks."""
    cv = Cv()
    idx = lime_idx(v + 90, base=6, seed=9400, rough=0.25)
    idx = 6.0 + (idx - 6) * 0.42           # látex over smooth plaster: the clusters stay, the contrast goes
    X, Y = cv.X, cv.Y
    v = {8: 1, 9: 2}.get(v, 0)
    if v == 1:
        idx, _ = crack_line(idx, [(2, 15), (11, 16), (20, 14), (30, 16)], 9401, amp=1.5, dark=2)
    cv.put(WHITEP, idx)
    if v == 2:
        for (x, y) in poisson(9410, 14, 3, keep=lambda x, y: border_dist(N, N)[int(y), int(x)] > 2):
            cv.put(SOOT, np.full((N, N), 2), (X == x) & (Y == y))
    if v == 3:
        cv.tint('#9a8456', np.where(fbm(N, N, 9420, cells=2, octaves=2) > 0.4, 0.14, 0.06))
    return cv.out()


@painter('cielorraso_humedad')
def p_cielorraso_humedad(v):
    """Ceiling damp from the roof: soft brown bloom with two faint tide lines, darker core, mould dots, a blister."""
    cv = Cv()
    idx = lime_idx(v + 95, base=6, seed=9400, rough=0.25)
    cv.put(WHITEP, 6.0 + (idx - 6) * 0.5)
    X, Y = cv.X, cv.Y
    cx, cy = [(15, 14), (18, 18), (13, 17)][v % 3]
    f = fbm(N, N, 9430 + v, cells=3, octaves=3)
    d = np.sqrt(((X - cx) / 1.15) ** 2 + (Y - cy) ** 2) + (f - 0.5) * 12
    st = d < 13
    t = np.clip((13 - d) / 13.0, 0, 1)
    cv.tint('#8a6a3a', np.where(st, 0.12 + 0.3 * t, 0))
    for rr, a in ((13, 0.38), (9.5, 0.22)):
        ring = (np.abs(d - rr) < 0.6)
        cv.tint('#5a4020', np.where(ring, a, 0))
    cv.tint('#3a2a14', np.where(d < 4, 0.18, 0))
    if v == 1:   # paint blister / peel in the centre
        H = flake(cx, cy, 3.6, 2.8, 9440, jag=0.4)
        r = rim(H, wrap=False)
        cv.put(CEMENT, np.full((N, N), 5) - r['in_top'], H)
        cv.put(WHITEP, np.full((N, N), 8), r['out_below'])
    if v == 2:
        mould_specks(cv, 9450, 2, keep=lambda x, y: d[int(y), int(x)] < 8, spread=1.8)
    return cv.out()


@painter('losa_sotano')
def p_losa_sotano(v):
    """Raw concrete slab of the basement: board-form imprints, rust bleeding from rebar, a spalled patch (v2)."""
    cv = Cv()
    X, Y = cv.X, cv.Y
    board = Y // 8
    rc = np.random.default_rng(9500)
    tone = rc.choice([-1, 0, 0, 1], 4)
    gr = wood_grain(N, N, 9501, 'x', warp=1.0, pores=0.02, tones=(0, 0, 0, 1, -1))
    idx = 4 + tone[board] + gr * (fbm(N, N, 9502, cells=4, octaves=1) > 0.45)
    idx = np.where(Y % 8 == 0, idx - 1, idx)
    idx = np.where(Y % 8 == 1, idx + 1, idx)
    idx = idx + posterize(cblend(fbm(N, N, 9503, cells=2, octaves=2), fbm(N, N, 9504 + v, cells=2, octaves=2)), [(0.75, 1), (0.25, -1)])
    cv.put(CEMENT, idx)
    sv = v
    v = {8: 1, 9: 2}.get(v, 0)
    if v == 1:
        st = (np.abs(X - 11) < 1.5) | (np.abs(X - 23) < 1.0)
        cv.tint('#6a3a1a', np.where(st & (fbm(N, N, 9510, cells=8, octaves=2) > 0.35), 0.35, 0))
    if v == 2:
        H = flake(16, 15, 6, 4, 9520, jag=0.4) & (border_dist(N, N) > 2)
        r = rim(H, wrap=False)
        cv.put(CEMENT, np.full((N, N), 2) - r['in_top'] + (fbm(N, N, 9521, cells=16, octaves=1) > 0.6), H)
        bar = H & (np.abs(Y - 15) < 1)
        cv.put(RUST, np.full((N, N), 3) + (Y == 14), bar)
        cv.tint('#6a3a1a', np.where(nb(H, -2, 0, False) & ~H & (np.abs(X - 16) < 4), 0.4, 0))
    cv.put(SALT, np.full((N, N), 1), (fbm(N, N, 9530 + sv, cells=16, octaves=1) > 0.86) & (Y % 8 == 7))
    return cv.out()


# =============================================================================================== ROOF: French tiles
def teja_tex(v, along='z'):
    """Marseille (French) clay tiles: 4 tiles across x 2 rows per block. Each tile: a dark interlock groove, the
    side roll, a flat channel with one raised central rib; darker under the head (covered by the row above), a lit
    lip at the bottom and the hard shadow it throws. Ribs run along the image's vertical axis (slopes facing N/S)."""
    cv = Cv()
    X, Y = cv.X, cv.Y
    rc = np.random.default_rng(9600)
    tone = rc.choice([-2, -1, 0, 0, 0, 1, 1], 8)
    col = X // 8
    row = Y // 16
    lab = col * 2 + row
    lx, ly = X % 8, Y % 16
    prof = np.array([-3, 1, 0, 0, 2, 1, 0, -1])
    idx = 5 + tone[lab] + prof[lx]
    idx = np.where(ly <= 2, idx - (3 - ly), idx)          # head under the overlap
    idx = np.where(ly == 13, idx + 1, idx)
    idx = np.where(ly == 14, 7 + (tone[lab] > 0), idx)    # lip
    idx = np.where(ly == 15, 1, idx)                      # shadow of the lip
    f = fbm(N, N, 9610 + v, cells=4, octaves=3)
    idx = idx + np.where(f > 0.76, 1, 0) - np.where(f < 0.22, 1, 0)
    cv.put(TEJA, idx)
    # dirt in the grooves, pale bloom and grey-yellow lichen rosettes
    ch = (lx == 0) & (ly > 2) & (ly < 14) & (fbm(N, N, 9620 + v, cells=8, octaves=2) > 0.6)
    cv.tint('#1e140c', np.where(ch, 0.4, 0))
    rng = np.random.default_rng(9630 + v)
    for k, (x, y) in enumerate(poisson(9630 + v, 3, 9, keep=lambda x, y: 3 <= int(y) % 16 <= 11)):
        for j in range(7):
            px_, py_ = int(round(x + rng.normal(0, 1.0))), int(round(y + rng.normal(0, 0.8)))
            cv.put(LICHEN, np.full((N, N), 1 + (j % 3)), (X == px_ % N) & (Y == py_ % N))
    cv.tint('#7a6a58', np.where(fbm(N, N, 9650 + v, cells=2, octaves=2) > 0.64, 0.16, 0))
    if v == 9:   # a cracked tile (VAR variants: v0-8 clean, the lichen and dirt move)
        cm = path_mask(wander([(11, 3), (13, 8), (12, 13)], 9660, amp=1), wrap=False)
        cv.put(TEJA, np.full((N, N), 0), cm)
    if v == -1:   # (unused) a missing tile: the battens and the black felt -- see casa_techo_roto
        hole = (col == 2) & (row == 0) & (ly < 15)
        felt = Ramp('#0d0c0b', '#171513', '#211e1a')
        cv.put(felt, np.full((N, N), 1) + ((X + Y) % 5 == 0), hole)
        cv.put(PINO, np.full((N, N), 3) + (ly == 5), hole & ((ly == 5) | (ly == 6)))
    out = cv.out()
    if along == 'x':
        out = np.ascontiguousarray(np.transpose(out, (1, 0, 2))[::-1])
    return out


PAINTERS['tejas'] = lambda v: teja_tex(v)
PAINTERS['tejas_eo'] = lambda v: teja_tex(v, 'x')


@painter('tejas_canto')
def p_tejas_canto(v):
    """Side of the tile cubes (stair risers, slab edges, gable ends of a cube roof): the overlapping rows of tiles
    seen edge-on, two rows per block: the lit lip with the roll humps, the tile body under it, the black gap and
    the next tile's head."""
    cv = Cv()
    X, Y = cv.X, cv.Y
    ly = Y % 16
    lx = X % 8
    hump = (lx == 1) | (lx == 2) | (lx == 3)
    rc = np.random.default_rng(9700)
    tone = rc.choice([-1, 0, 0, 1], 8)[(X // 8) + 4 * (Y // 16)]
    idx = np.full((N, N), 4) + tone
    idx = np.where(ly == 0, 7 + hump, idx)                       # lip
    idx = np.where(ly == 1, 6 + hump, idx)
    idx = np.where((ly >= 2) & (ly <= 9), 4 + tone - (ly >= 7) + np.where(hump, 1, 0) - (lx == 0) * 2, idx)
    idx = np.where((ly >= 10) & (ly <= 12), np.where(hump & (ly == 10), 3, 1), idx)   # the dark gap under the row
    idx = np.where(ly >= 13, 0, idx)
    idx = np.where((ly == 15) & ~hump, 2, idx)                   # the head of the tile below catches a little light
    cv.put(TEJA, idx)
    mo = (ly >= 9) & (ly <= 12) & (fbm(N, N, 9701 + v, cells=8, octaves=1) > 0.62)
    cv.put(MOSS, np.full((N, N), 1), mo)
    cv.put(MORTAR, np.full((N, N), 3), (ly >= 11) & (ly <= 13) & (fbm(N, N, 9702 + v, cells=16, octaves=1) > 0.72))
    return cv.out()


@painter('machimbre')
def p_machimbre(v):
    """Eave soffit / underside of the roof: tongue-and-groove pine boards, dark varnish, damp stains."""
    cv = Cv()
    X, Y = cv.X, cv.Y
    lab = X // 8
    rc = np.random.default_rng(9800)
    tone = rc.integers(-1, 2, 4)
    g = wood_grain(N, N, 9801 + v, 'y', warp=1.2, pores=0.03)
    idx = 4 + tone[lab] + g
    idx = np.where(X % 8 == 0, 0, idx)
    idx = np.where(X % 8 == 1, idx + 1, idx)
    idx = np.where(X % 8 == 7, idx - 1, idx)
    cv.put(PINO, idx - 1)
    if v == 7:   # (8 variants) one damp stain
        st = blob(N, N, 12, 16, 9, 7, 9810, rough=0.4)
        cv.tint('#2a1a0a', np.where(st, 0.3, 0))
        cv.tint('#120a04', np.where(st & ~erode(st, 1, False), 0.45, 0))
    return cv.out()


def salt_bloom(cv, mask, seed, strength=0.75, density=0.5):
    """Efflorescence: crystalline white bloom, tinted (not opaque) with a few bright crystals."""
    n = fbm(N, N, seed, cells=16, octaves=1)
    n2 = fbm(N, N, seed + 1, cells=8, octaves=2)
    m = mask & (n2 > 1 - density)
    cv.tint('#e9e7e0', np.where(m, strength * (0.55 + 0.45 * n), 0))
    cr = m & (n > 0.72)
    cv.tint('#ffffff', np.where(cr, 0.6, 0))
    return m


def mould_specks(cv, seed, count, keep=None, spread=2.2):
    """Clusters of black mould: tiny 1 px specks around a few centres (never big discs)."""
    X, Y = cv.X, cv.Y
    rng = np.random.default_rng(seed)
    centres = poisson(seed, count, 6.0, keep=keep)
    for (cx, cy) in centres:
        for k in range(int(rng.integers(5, 12))):
            x = int(round(cx + rng.normal(0, spread)))
            y = int(round(cy + rng.normal(0, spread * 0.8)))
            if 1 <= x < N - 1 and 1 <= y < N - 1:
                cv.put(SOOT, np.full((N, N), int(rng.integers(0, 3))), (X == x) & (Y == y))
                if rng.random() < 0.3:
                    cv.put(SOOT, np.full((N, N), 3), (X == x + 1) & (Y == y))


@painter('revoque_chorreado')
def p_revoque_chorreado(v):
    """Render under a leaking gutter / window sill: soft grey-green run-off stains hanging from the top edge, each a
    bundle of narrow vertical streaks that fade and fray downwards, a darker damp band right under the eave."""
    cv = Cv()
    idx = render_idx(v + 14, seed=200)
    cv.put(RENDER_W, idx)
    X, Y = cv.X, cv.Y
    n = fbm(N, N, 6410 + v, cells=2, octaves=3, ax=6, ay=0.35)          # vertically stretched, periodic in x
    reach = 8 + 22 * np.clip((n - 0.25) * 1.8, 0, 1)                      # how far each column's stain runs down
    fray = fbm(N, N, 6420 + v, cells=4, octaves=2, ax=4, ay=1)
    t = np.clip((reach - Y) / reach, 0, 1) ** 1.3
    t = t * (0.55 + 0.45 * fray)
    cv.tint('#4a4e40', t * 0.55)
    edge = (np.abs(Y - reach) < 1.0) & (Y > 4)
    cv.tint('#3a3e30', np.where(edge, 0.18, 0))
    cv.tint('#3e4234', np.clip((6 - Y) / 6.0, 0, 1) * 0.35)
    if v == 1:
        mould_specks(cv, 6415, 3, keep=lambda x, y: y < 12)
    return cv.out()


# =============================================================================================== BLOCKS (batch 1)
def cube(key, es, en, painter_name, variants=1, sound='plaster', up=None, down=None, **kw):
    mats = {}

    def m(name):
        if name not in mats:
            mats[name] = cube_mat(PAINTERS[name])
        return mats[name]
    up = up or painter_name
    down = down or up
    faces = {'side': m(painter_name), 'up': m(up), 'down': m(down)}
    return Cube('casa_' + key, es, en, faces=faces, kit=KIT, sound=sound, variants=variants, **kw)


# --- exterior walls
LADRILLO = cube('ladrillo_visto', 'Ladrillo visto', 'Exposed face brick', 'ladrillo', VAR, sound='stone')
cube('ladrillo_salitre', 'Ladrillo visto con salitre', 'Face brick with salt bloom', 'ladrillo_salitre', 4, sound='stone', up='ladrillo', down='ladrillo')
REVOQUE_B = cube('revoque_blanco', 'Revoque blanco', 'White render', 'revoque_blanco', VAR)
cube('revoque_humedad', 'Revoque con humedad de cimientos', 'Render with rising damp', 'revoque_humedad', len(DAMP_SHAPES), up='revoque_blanco', down='revoque_blanco')
cube('zocalo_revoque_humedad', 'Zócalo de cemento con humedad (bajo revoque húmedo)', 'Cement plinth under damp render', 'zocalo_revoque_humedad', 8,
     sound='stone', up='revoque_blanco', down='cemento_piso')
cube('revoque_chorreado', 'Revoque chorreado', 'Render with damp streaks from above', 'revoque_chorreado', 2, up='revoque_blanco', down='revoque_blanco')
cube('zocalo_revoque', 'Zócalo de cemento (bajo revoque)', 'Cement plinth under render', 'zocalo_revoque', 2, sound='stone', up='revoque_blanco', down='cemento_piso')
cube('zocalo_ladrillo', 'Zócalo de cemento (bajo ladrillo)', 'Cement plinth under brick', 'zocalo_ladrillo', 2, sound='stone', up='ladrillo', down='cemento_piso')
cube('medianera', 'Medianera', 'Party wall (medianera)', 'medianera', VAR, sound='stone')
cube('medianera_parche', 'Medianera con parches', 'Party wall with plaster patches', 'medianera_parche', 2, sound='stone', up='medianera', down='medianera')
cube('medianera_hueco', 'Medianera sin revoque (ladrillo hueco)', 'Party wall with the render fallen (hollow block)', 'medianera_hueco', 2,
     sound='stone', up='medianera', down='medianera')
# --- interior walls (VAR variants: clean re-seeds + one light defect each; the loud ones are their own blocks)
cube('pared_living', 'Pared del living', 'Living room wall', 'pared_living', VAR)
cube('pared_living_marco', 'Pared del living (marca de cuadro)', 'Living room wall (ghost of a picture)', 'pared_living_marco', 2, up='pared_living', down='pared_living')
cube('pared_living_zocalo', 'Pared del living con zócalo', 'Living room wall with skirting', 'pared_living_zocalo', 4, up='pared_living', down='pared_living')
cube('pared_living_moldura', 'Pared del living con moldura', 'Living room wall with picture rail', 'pared_living_moldura', 2, up='pared_living', down='pared_living')
cube('pared_pasillo', 'Pared del pasillo (verde agua)', 'Hall wall (pale aqua)', 'pared_pasillo', VAR)
cube('pared_pasillo_marco', 'Pared del pasillo (marca de cuadro)', 'Hall wall (ghost of a picture)', 'pared_pasillo_marco', 2, up='pared_pasillo', down='pared_pasillo')
cube('pared_pasillo_rayada', 'Pared del pasillo (dedos sucios)', 'Hall wall (dirty finger trails)', 'pared_pasillo_rayada', 2, up='pared_pasillo', down='pared_pasillo')
cube('pared_pasillo_zocalo', 'Pared del pasillo con zócalo', 'Hall wall with skirting', 'pared_pasillo_zocalo', 4, up='pared_pasillo', down='pared_pasillo')
cube('pared_cocina', 'Pared de la cocina', 'Kitchen wall', 'pared_cocina', VAR)
cube('pared_cocina_hollin', 'Pared de la cocina (tizne de la hornalla)', 'Kitchen wall (soot over the stove)', 'pared_cocina_hollin', 2, up='pared_cocina', down='pared_cocina')
cube('azulejo_verde', 'Azulejos verdes', 'Green kitchen tiles', 'azulejo_verde', VAR, sound='tile')
cube('azulejo_verde_falta', 'Azulejos verdes (falta uno)', 'Green tiles (one missing)', 'azulejo_verde_falta', 2, sound='tile', up='azulejo_verde', down='azulejo_verde')
cube('azulejo_verde_sucio', 'Azulejos verdes (juntas sucias)', 'Green tiles (greasy grout)', 'azulejo_verde_sucio', 2, sound='tile', up='azulejo_verde', down='azulejo_verde')
cube('azulejo_verde_guarda', 'Azulejos verdes con guarda', 'Green tiles with decorated border', 'azulejo_verde_guarda', 1, sound='tile', up='azulejo_verde', down='azulejo_verde')
cube('pared_bano', 'Pared del baño', 'Bathroom wall', 'pared_bano', VAR)
cube('azulejo_celeste', 'Azulejos celestes', 'Light-blue bathroom tiles', 'azulejo_celeste', VAR, sound='tile')
cube('azulejo_celeste_falta', 'Azulejos celestes (falta uno)', 'Light-blue tiles (one missing)', 'azulejo_celeste_falta', 2, sound='tile', up='azulejo_celeste', down='azulejo_celeste')
cube('azulejo_celeste_sucio', 'Azulejos celestes (juntas con hongos)', 'Light-blue tiles (mouldy grout)', 'azulejo_celeste_sucio', 2, sound='tile', up='azulejo_celeste', down='azulejo_celeste')
cube('azulejo_celeste_guarda', 'Azulejos celestes con guarda', 'Light-blue tiles with border', 'azulejo_celeste_guarda', 1, sound='tile', up='azulejo_celeste', down='azulejo_celeste')
cube('pared_lucia', 'Pared rosa (Lucía)', "Pink wall (Lucía's room)", 'pared_lucia', VAR)
cube('pared_lucia_zocalo', 'Pared rosa con zócalo', 'Pink wall with skirting', 'pared_lucia_zocalo', 4, up='pared_lucia', down='pared_lucia')
cube('pared_lucia_stickers', 'Pared rosa con stickers', 'Pink wall with stickers', 'pared_lucia_stickers', 3, up='pared_lucia', down='pared_lucia')
cube('pared_toti', 'Pared azul (Toti)', "Dark blue wall (Toti's room)", 'pared_toti', VAR)
cube('pared_toti_zocalo', 'Pared azul con zócalo', 'Dark blue wall with skirting', 'pared_toti_zocalo', 4, up='pared_toti', down='pared_toti')
cube('pared_toti_poster', 'Pared azul con pósters', 'Dark blue wall with gamer posters', 'pared_toti_poster', 3, up='pared_toti', down='pared_toti')
cube('empapelado_nona', 'Empapelado floreado (Nona)', "Floral wallpaper (Nona's room)", 'empapelado_nona', VAR, sound='paper')
cube('empapelado_nona_cruz', 'Empapelado floreado (marca del crucifijo)', 'Floral wallpaper (ghost of the crucifix)', 'empapelado_nona_cruz', 1, sound='paper',
     up='empapelado_nona', down='empapelado_nona')
cube('empapelado_nona_zocalo', 'Empapelado floreado con zócalo', 'Floral wallpaper with skirting', 'empapelado_nona_zocalo', 2, sound='paper', up='empapelado_nona', down='empapelado_nona')
cube('empapelado_matrimonial', 'Empapelado setentoso', '70s wallpaper (master bedroom)', 'empapelado_matrimonial', VAR, sound='paper')
cube('empapelado_matrimonial_zocalo', 'Empapelado setentoso con zócalo', '70s wallpaper with skirting', 'empapelado_matrimonial_zocalo', 2, sound='paper', up='empapelado_matrimonial', down='empapelado_matrimonial')
cube('cemento_lavadero', 'Cemento del lavadero', 'Laundry cement wall', 'cemento_lavadero', VAR, sound='stone')
cube('cemento_lavadero_zocalo', 'Cemento del lavadero (pie sucio)', 'Laundry cement wall (grimy foot)', 'cemento_lavadero_zocalo', 4, sound='stone',
     up='cemento_lavadero', down='cemento_lavadero')
# --- floors
cube('parquet', 'Parquet espina de pez', 'Herringbone parquet', 'parquet', VAR, sound='wood', down='cielorraso')
cube('parquet_mancha', 'Parquet con mancha de maceta', 'Herringbone parquet (flowerpot ring)', 'parquet', 2, sound='wood', up='parquet_mancha', down='cielorraso')
cube('parquet_gastado', 'Parquet gastado', 'Worn parquet', 'parquet_gastado', VAR, sound='wood', down='cielorraso')
cube('granitico', 'Granítico', 'Terrazzo tiles (granítico)', 'granitico', 6, sound='tile', down='cielorraso')
cube('granitico_roto', 'Granítico rajado', 'Cracked terrazzo tiles', 'granitico_roto', 3, sound='tile', down='cielorraso')
cube('umbral_marmol', 'Umbral de mármol', 'Marble door threshold', 'umbral_marmol', 2, sound='stone', down='cielorraso')
cube('ceramica_cocina', 'Cerámica de la cocina', 'Kitchen ceramic floor', 'ceramica_cocina', VAR, sound='tile', down='cielorraso')
cube('baldosa_patio', 'Baldosa colorada del patio', 'Red patio tiles', 'baldosa_patio', VAR, sound='stone')
cube('ladrillo_patio', 'Piso de ladrillo del patio', 'Patio brick paving', 'ladrillo_patio', VAR, sound='stone', down='ladrillo')
cube('cemento_piso', 'Piso de cemento', 'Cement floor', 'cemento_piso', VAR, sound='stone')
cube('arena', 'Piso de arena', 'Packed sand floor', 'arena', VAR, sound='sand')
cube('arena_pisadas', 'Piso de arena con pisadas', 'Packed sand with bare footprints', 'arena', 1, sound='sand', up='arena_pisadas', down='arena')
cube('arena_arrastre', 'Piso de arena con marcas de arrastre', 'Packed sand with drag marks', 'arena', 1, sound='sand', up='arena_arrastre', down='arena')
VEREDA = cube('vereda', 'Baldosa vainilla (vereda)', "'Vainilla' sidewalk tiles", 'vereda', 3, sound='stone', down='cemento_piso')
cube('vereda_rota', 'Vereda rota', 'Broken sidewalk tiles', 'vereda_rota', 3, sound='stone', up='vereda_rota', down='cemento_piso')
Cube('casa_cordon', 'Cordón de granito', 'Granite curb', faces={'up': cube_mat(PAINTERS['cordon_top']), 'side': cube_mat(PAINTERS['cordon_side']),
     'down': cube_mat(PAINTERS['cordon_side'])}, kit=KIT, sound='stone', variants=2)
cube('asfalto', 'Asfalto del pasaje', 'Old asphalt', 'asfalto', VAR, sound='stone')
cube('asfalto_bache', 'Asfalto con bache', 'Asphalt with a pothole', 'asfalto', 1, sound='stone', up='asfalto_bache', down='asfalto')
Cube('casa_cesped', 'Césped', 'Scruffy lawn', faces={'up': cube_mat(PAINTERS['cesped_top']), 'side': cube_mat(PAINTERS['cesped_side']),
     'down': cube_mat(PAINTERS['tierra'])}, kit=KIT, sound='grass', variants=3)
cube('tierra', 'Tierra', 'Garden earth', 'tierra', 2, sound='dirt')
# --- ceilings
cube('cielorraso', 'Cielorraso', 'Plaster ceiling', 'pared_bano', VAR, down='cielorraso', up='cielorraso')
cube('cielorraso_humedad', 'Cielorraso con humedad', 'Damp-stained ceiling', 'pared_bano', 3, down='cielorraso_humedad', up='cielorraso')
cube('losa_sotano', 'Losa del sótano', 'Basement concrete slab', 'losa_sotano', VAR, sound='stone')
# --- roof (two sets: ribs for slopes facing north/south, and for slopes facing east/west; stairs keep uvlock)
TEJAS = Cube('casa_tejas', 'Tejas francesas', 'French clay roof tiles', faces={'up': cube_mat(PAINTERS['tejas']),
             'side': cube_mat(PAINTERS['tejas_canto']), 'down': cube_mat(PAINTERS['machimbre'])}, kit=KIT, sound='ceramic', variants=VAR)
Stairs('casa_tejas_escalera', 'Techo de tejas (escalera, faldón N/S)', 'Tiled roof stairs (N/S slope)', of=TEJAS, kit=KIT, sound='ceramic')
Slab('casa_tejas_losa', 'Techo de tejas (losa)', 'Tiled roof slab', of=TEJAS, kit=KIT, sound='ceramic')
TEJAS_EO = Cube('casa_tejas_eo', 'Tejas francesas (faldón E/O)', 'French clay roof tiles (E/W slope)', faces={'up': cube_mat(PAINTERS['tejas_eo']),
                'side': cube_mat(PAINTERS['tejas_canto']), 'down': cube_mat(PAINTERS['machimbre'])}, kit=KIT, sound='ceramic', variants=VAR)
Stairs('casa_tejas_eo_escalera', 'Techo de tejas (escalera, faldón E/O)', 'Tiled roof stairs (E/W slope)', of=TEJAS_EO, kit=KIT, sound='ceramic')
Slab('casa_tejas_eo_losa', 'Techo de tejas (losa, E/O)', 'Tiled roof slab (E/W)', of=TEJAS_EO, kit=KIT, sound='ceramic')
cube('machimbre', 'Machimbre del alero', 'Eave soffit boards', 'machimbre', 8, sound='wood')


# =============================================================================================== FURNITURE HELPER
def mirror_x(parts):
    """Mirror unrotated parts left/right (x -> 16 - x): the '_izq' twin of a '_der' piece."""
    out = []
    for q in parts:
        assert not q.rot, 'mirror_x: rotated parts are not supported'
        (x1, y1, z1), (x2, y2, z2) = q.frm, q.to
        out.append(box((16 - x2, y1, z1), (16 - x1, y2, z2), q.mat, faces=q.faces, decals=q.decals, shade=q.shade, name=q.name, cull=q.cull))
    return out


_AXF = {'north': (2, 0), 'south': (2, 1), 'west': (0, 0), 'east': (0, 1), 'down': (1, 0), 'up': (1, 1)}


def fix_coplanar(parts, eps=0.01):
    """No z-fighting: where two parts (same rotation) emit faces in the same direction on the same plane and those
    faces overlap, the later part gives way by eps - a box pulls that face 0.01 into itself, a thin plane/decal
    steps 0.01 OUT so it stays on top. Repeats until nothing coplanar is left."""
    for _ in range(6):
        changed = False
        for j in range(len(parts)):
            for i in range(j):
                a, b = parts[i], parts[j]
                if a.rot != b.rot:
                    continue
                for f in set(a.faces) & set(b.faces):
                    ax, side = _AXF[f]
                    pa = a.to[ax] if side else a.frm[ax]
                    pb = b.to[ax] if side else b.frm[ax]
                    if abs(pa - pb) > 1e-4:
                        continue
                    ov = 1.0
                    for k in range(3):
                        if k != ax:
                            ov *= max(0.0, min(a.to[k], b.to[k]) - max(a.frm[k], b.frm[k]))
                    if ov <= 1e-4:
                        continue
                    frm, to = list(b.frm), list(b.to)
                    if to[ax] - frm[ax] > 3 * eps:
                        if side:
                            to[ax] -= eps
                        else:
                            frm[ax] += eps
                    else:
                        d = eps if side else -eps
                        frm[ax] += d
                        to[ax] += d
                    b.frm, b.to = tuple(round(v, 4) for v in frm), tuple(round(v, 4) for v in to)
                    changed = True
        if not changed:
            break
    return parts


def F(key, es, en, parts, **kw):
    """Register an element-model piece of this kit (key gets the 'casa_' prefix); coplanar faces are separated."""
    kw.setdefault('kit', KIT)
    kw.setdefault('sound', 'wood')
    return Furniture('casa_' + key, es, en, parts=fix_coplanar(list(parts)), **kw)


# =============================================================================================== ROOF SYSTEM
# Smooth 45-degree roof made of rotated tile slabs (Minecraft allows +-45 degree element rotations), so the chalet
# gets a real pitched roof instead of vanilla stair steps. All pieces face NORTH = the downhill side; the slope rises
# towards +z (the back). One block of slope = 16 up + 16 back. The tile surface passes through the block's lower
# front corner (z=0, y=0) and its upper back corner (z=16, y=16), so pieces placed diagonally (one up, one back)
# continue each other. The roof's EAVE piece sits directly ON TOP of the facade's top wall block (its slope starts at
# the outer top edge of the wall and overhangs 4/16 with fascia, soffit and the gutter). A 15-deep house gets its
# ridge piece (peak in the middle of the block) at the 8th row. Gable ends: '_izq'/'_der' pieces fill the wall
# triangle under the slope (wall material sampled in block space so it continues the gable's cubes) and add the
# verge overhang on the OUTER side: _izq = the gable is on the LEFT of a viewer standing downhill looking at the
# roof (authoring +x), _der = on the right.
R2 = math.sqrt(2.0)
ROOF_T = 2.0                  # tile layer thickness (perpendicular to the slope)
TILE_ROWS = 45                # texel rows of tile field per block along the slope (16*sqrt2 units)
_TMAP = {}


def teja_map(kind='normal'):
    """The tile field of one block of slope: (45 rows along the slope, 32 cols) RGBA. Row 0 = eave side.
    Marseille tiles in straight columns (8 px wide), 3 rows per block (15 px): lip highlight at the bottom of each
    tile with the roll humps, interlock groove, two channels and a rib, the dark crevice under the row above."""
    if kind in _TMAP:
        return _TMAP[kind]
    W_, H_ = 32, TILE_ROWS
    Y, X = np.mgrid[0:H_, 0:W_]
    row, lu = Y // 15, Y % 15
    col, lx = X // 8, X % 8
    rc = np.random.default_rng(9900 + len(kind))
    tone = rc.choice([-2, -1, -1, 0, 0, 0, 1, 1], 12)
    t = tone[(row % 3) * 4 + col]
    prof = np.array([-3, 2, 1, -1, -1, 1, 0, -1])
    idx = 5 + t + prof[lx]
    mott = vnoise(W_, H_, 4, 6, 9910) * 0.6 + vnoise(W_, H_, 8, 9, 9911) * 0.4
    idx = idx + np.where(mott > 0.68, 1, 0) - np.where(mott < 0.3, 1, 0)
    idx = np.where(lu == 0, 7 + (t > 0) + (lx == 1), idx)            # the lip catching light
    idx = np.where(lu == 1, idx + 1, idx)
    idx = np.where((lu >= 10) & (lu <= 11), idx - 1, idx)
    idx = np.where(lu == 12, idx - 2, idx)
    crev = lu >= 13
    idx = np.where(crev, np.where(lu == 13, 1, 0), idx)
    hump = (lu == 14) & ((lx == 1) | (lx == 2))                       # the roll of the row above dips into the gap
    idx = np.where(hump, 5, idx)
    cv = Cv(W_, H_)
    cv.put(TEJA, idx)
    # grime in the interlock grooves, rain streaks running down the slope (towards row 0)
    cv.tint('#1e140c', np.where((lx == 0) & ~crev & (vnoise(W_, H_, 8, 15, 9912) > 0.45), 0.35, 0))
    streak = (vnoise(W_, H_, 16, 3, 9913) > 0.72) & ~crev
    cv.tint('#3a2a20', np.where(streak, 0.18, 0))
    # pale efflorescence bloom on some tiles + grey-yellow lichen rosettes on the flat parts
    cv.tint('#9a8a78', np.where((vnoise(W_, H_, 4, 3, 9914) > 0.66) & ~crev, 0.16, 0))
    nlich = {'normal': 4, 'musgo': 12, 'roto': 5}[kind]
    rng = np.random.default_rng(9920 + nlich)
    for k in range(nlich):
        cx_, cy_ = int(rng.integers(0, W_)), int(rng.integers(0, H_))
        if cy_ % 15 >= 12:
            continue
        for j in range(int(rng.integers(4, 9))):
            px_, py_ = int(round(cx_ + rng.normal(0, 1.1))), int(round(cy_ + rng.normal(0, 0.8)))
            if 0 <= py_ < H_ and py_ % 15 < 13:
                cv.put(LICHEN, np.full((H_, W_), 1 + (j % 3)), (X == px_ % W_) & (Y == py_))
    if kind == 'musgo':   # moss cushions in the crevices and grooves, black streaks
        mo = (crev | (lx == 0)) & (vnoise(W_, H_, 8, 9, 9930) > 0.42)
        cv.put(MOSS, np.full((H_, W_), 2) + (vnoise(W_, H_, 16, 15, 9931) > 0.6) + (lu == 14), mo)
        cv.put(MOSS, np.full((H_, W_), 3), (lu == 0) & (vnoise(W_, H_, 8, 3, 9932) > 0.6))
        cv.tint('#16120e', np.where((vnoise(W_, H_, 16, 2, 9933) > 0.7) & ~crev, 0.3, 0))
    if kind == 'roto':
        # a missing tile (col 2, row 1): black felt and the pine batten, the head of the tile below
        hole = (col == 2) & (row == 1) & (lu <= 13)
        felt = Ramp('#0b0a09', '#141210', '#1d1a17', '#26221e')
        cv.put(felt, np.full((H_, W_), 1) + ((X + Y) % 4 == 0) - (lu == 0), hole)
        cv.put(PINO, np.full((H_, W_), 3) + (lu == 6) - (lu == 8), hole & (lu >= 6) & (lu <= 8))
        cv.put(TEJA, np.full((H_, W_), 3), hole & (lu <= 2) & (lx >= 1) & (lx <= 6))     # head of the tile below
        # a cracked tile next to it and a shard lying in the gap
        cm = path_mask(wander([(4, 17), (6, 22), (5, 26)], 9940, amp=0.8), W_, H_, wrap=False)
        cv.put(TEJA, np.full((H_, W_), 1), cm)
        cv.put(TEJA, np.full((H_, W_), 6), (X == 19) & (Y >= 21) & (Y <= 22))
    _TMAP[kind] = cv.out()
    return _TMAP[kind]


def slope_box(za, ya, zb, yb, x0=0.0, x1=16.0, dy0=0.0, dy1=ROOF_T, kind='normal', mat='tile', mirror=False, name=None):
    """A slab along the 45-degree line from (za, ya) to (zb, yb) (za < zb), occupying depths dy0..dy1 below the line.
    mat 'tile' = the roof (tile field on top), 'render' = plastered verge band, 'wood' = barge board."""
    rising = yb > ya
    zm, ym = (za + zb) / 2.0, (ya + yb) / 2.0
    L = R2 * (zb - za)
    ang = -45 if rising else 45
    z1 = zm - L / 2
    if rising:
        u_z1, sgn = (za + ya) / R2, 1.0
    else:
        u_z1, sgn = ((16 - za) + ya) / R2, -1.0
    tm = teja_map(kind)

    def along(z):
        return u_z1 + sgn * (z - z1)

    def p(face, w, h, part):
        x, y, z = face_coords(part, face, w, h)
        xx = (16 - x) if mirror else x
        cx = np.floor(xx * 2).astype(int) % 32
        cv = Cv(w, h)
        if mat == 'tile' and face == 'up':
            r = np.floor(along(z) * TILE_ROWS / (16 * R2)).astype(int) % TILE_ROWS
            return tm[r, cx]
        if mat == 'tile' and face in ('west', 'east'):
            r = np.floor(along(z) * TILE_ROWS / (16 * R2)).astype(int) % TILE_ROWS
            dep = np.floor((ym - dy0 - y) * 2).astype(int)
            lu = r % 15
            idx = np.where(dep <= 0, 6, np.where(dep >= 3, 1, 3)) + 0
            idx = np.where(lu >= 13, np.minimum(idx, 1), idx)
            idx = np.where(lu == 0, idx + 1, idx)
            cv.put(TEJA, idx)
            return cv.out()
        if mat == 'tile' and face == 'down':
            g = wood_grain(w, h, 9950, 'y', period=False, pores=0.02)
            idx = 3 + g
            idx = np.where(cx % 8 == 0, 0, idx)
            idx = np.where(cx % 8 == 1, idx + 1, idx)
            cv.put(PINO, idx - 1)
            cv.tint('#120c08', np.where(vnoise(w, h, max(1, w // 8), max(1, h // 8), 9951) > 0.6, 0.35, 0.1))
            return cv.out()
        if mat == 'tile':   # the lip / end faces: tile noses with the roll humps
            dep = np.floor((ym - dy0 - y) * 2).astype(int) if face in ('north', 'south') else np.zeros((h, w), int)
            lx = cx % 8
            idx = np.where(dep <= 0, 7, np.where(dep == 1, 6, np.where(dep == 2, 4, 1)))
            idx = idx + np.where((lx == 1) | (lx == 2), 1, 0) - np.where(lx == 0, 3, 0)
            cv.put(TEJA, idx)
            return cv.out()
        if mat == 'render':
            idx = render_idx(0, seed=200)
            i, j = aligned_uv(part, face, w, h)
            cv.put(RENDER_W, idx[j, i] - (face == 'down'))
            if face in ('west', 'east', 'north', 'south'):
                dep = (ym - y)
                cv.tint('#24261c', np.where(dep > dy1 - 0.8, 0.25, 0))
            return cv.out()
        return pp_paint(WOOD_D, 3, seed=9960, chip=0.15)(face, w, h, part)

    frm = (x0, ym - dy1, zm - L / 2)
    to = (x1, ym - dy0, zm + L / 2)
    return P(frm, to, p, rot=('x', ang, (8.0, ym, zm)), name=name or 'slope')


def gable_fill(profile, wall='ladrillo', x0=0.0, x1=16.0):
    """Wall triangle under the slope: one 1-unit column per z step, top = profile(k) (block space texture)."""
    tex = T(wall, 0)
    parts = []
    for k in range(16):
        top = profile(k)
        if top <= 0.05:
            continue
        parts.append(P((x0, 0, k), (x1, top, k + 1), aligned(tex), faces=('west', 'east'), name='gable'))
    return parts


def gutter_parts(x0=0.0, x1=16.0, cap_l=False, cap_r=False):
    """Half-round galvanised gutter hung on the fascia, in front of the eave (block-local coordinates of the eave
    piece: the gutter hangs in the air block in front of the wall's top block). Its bottom is at y=-10.2, its axis at
    z=-6.7 (local z 9.3 of that front block: the downpipe's swan neck starts there)."""
    gz = pp_fn(gutter_paint)
    parts = [
        P((x0, -10.2, -8.8), (x1, -9.4, -4.8), gz, name='g_bottom'),
        P((x0, -9.6, -9.4), (x1, -7.2, -8.8), gz, name='g_front'),
        P((x0, -7.4, -9.7), (x1, -6.6, -8.7), gz, name='g_bead'),
        P((x0, -9.6, -4.8), (x1, -6.2, -4.2), gz, name='g_back'),
        PL((x0, -9.35, -8.8), (x1, -9.35, -4.8), pp_fn(gutter_muck), name='g_muck'),
    ]
    it = pp_iron(seed=9970, rust=0.45)
    for xs in (3.0, 11.0):
        if x0 <= xs < x1:
            parts += [P((xs, -10.5, -9.0), (xs + 0.7, -10.2, -4.4), it, name='strap_b'),
                      P((xs, -10.2, -9.9), (xs + 0.7, -6.6, -9.4), it, name='strap_f'),
                      P((xs, -6.6, -9.9), (xs + 0.7, -6.2, -8.6), it, name='strap_hook')]
    for on, xc in ((cap_l, x1 - 0.5), (cap_r, x0)):
        if on:
            parts.append(P((xc, -10.2, -9.4), (xc + 0.5, -6.6, -4.2), gz, name='g_cap'))
    return parts


def gutter_paint(face, w, h, part, cv):
    """Old galvanised sheet: spangle mottle, dull grey, rust along seams and the bottom, a moss tuft on the bead."""
    x, y, z = face_coords(part, face, w, h)
    k = fkey(part, face)
    n = vnoise(w, h, max(1, w // 4), max(1, h // 2), k) if w > 1 and h > 1 else np.full((h, w), 0.5)
    idx = np.full((h, w), 4) + np.where(n > 0.65, 1, 0) - np.where(n < 0.3, 1, 0)
    if face in ('north', 'south') and h > 2:
        idx = np.where(np.arange(h)[:, None] == 0, idx + 2, idx)
    if face == 'down':
        idx = idx - 1
    cv.put(GALV, idx)
    seam = (np.floor(x * 2).astype(int) % 32 == 0) & (w > 2)
    rs = seam | ((face == 'down') & (vnoise(w, h, max(1, w // 3), max(1, h // 2), k + 1) > 0.62))
    rs |= (vnoise(w, h, max(1, w // 4), max(1, h), k + 2) > 0.88)
    cv.put(RUST, np.full((h, w), 2) + (vnoise(w, h, max(1, w // 2), max(1, h), k + 3) > 0.6), rs)
    if face == 'down':   # rust drips hanging under the seams
        cv.put(RUST, np.full((h, w), 1), seam)


def gutter_muck(face, w, h, part, cv):
    """What sits in a gutter nobody cleaned in years: black silt, dead leaves, a tennis ball's worth of moss."""
    x, y, z = face_coords(part, face, w, h)
    n = vnoise(w, h, max(1, w // 3), max(1, h // 2), 9975)
    cv.put(EARTH, np.full((h, w), 1) + (n > 0.5))
    lv = vnoise(w, h, max(1, w // 2), max(1, h), 9976) > 0.62
    cv.put(Ramp('#3a2410', '#5a3a18', '#7a5426'), np.full((h, w), 1) + (n > 0.7), lv)
    cv.put(MOSS, np.full((h, w), 2), vnoise(w, h, max(1, w // 4), max(1, h // 2), 9977) > 0.74)


def fascia_soffit(x0=0.0, x1=16.0):
    wood = pp_paint(WOOD_D, 3, seed=9980, chip=0.18, along='x')
    sof = pp_fn(lambda face, w, h, part, cv: cv.put(PINO, (3 + wood_grain(w, h, 9981, 'y', period=False) -
                                                          (np.floor(face_coords(part, face, w, h)[0] * 2).astype(int) % 8 == 0) * 3)
                                                         if face == 'down' else np.full((h, w), 2)))
    return [P((x0, -7.6, -4.6), (x1, -3.4, -3.6), wood, name='fascia'),
            P((x0, -7.4, -3.6), (x1, -6.8, 0.0), sof, name='soffit')]


def roof_parts(kind='normal'):
    return [slope_box(0, 0, 16, 16, kind=kind)]


def eave_parts(kind='normal', x0=0.0, x1=16.0):
    return [slope_box(-4, -4, 16, 16, x0=x0, x1=x1, kind=kind, name='slope_eave')] + fascia_soffit(x0, x1) + gutter_parts(x0, x1)


def ridge_cap_parts(y0, x0=0.0, x1=16.0, end=None):
    """Half-round ridge tiles on a mortar bed, with the overlapping socket every 8 units. y0 = the peak line."""
    cap = pp_fn(ridge_paint)
    mort = pp_fn(lambda face, w, h, part, cv: cv.put(MORTAR, np.full((h, w), 4) + (vnoise(w, h, max(1, w // 2), max(1, h // 2), 9990) > 0.55)
                                                    - (vnoise(w, h, max(1, w // 3), max(1, h), 9991) > 0.75) * 2))
    parts = [P((x0, y0 - 3.2, 5.2), (x1, y0 + 0.4, 10.8), mort, name='mortar'),
             P((x0, y0 - 0.4, 4.6), (x1, y0 + 1.6, 11.4), cap, name='cap_lo'),
             P((x0, y0 + 1.6, 5.4), (x1, y0 + 2.8, 10.6), cap, name='cap_mid'),
             P((x0, y0 + 2.8, 6.6), (x1, y0 + 3.4, 9.4), cap, name='cap_top')]
    if end is not None:   # the open end of the last ridge tile, filled with mortar
        parts.append(P((end - 0.3, y0 - 0.2, 5.0), (end + 0.3, y0 + 2.6, 11.0), mort, name='cap_end'))
    return parts


def ridge_paint(face, w, h, part, cv):
    x, y, z = face_coords(part, face, w, h)
    xi = np.floor(x * 2).astype(int) % 16
    idx = np.full((h, w), 5) + np.where(xi < 2, 2, 0) - np.where(xi == 15, 3, 0) - np.where(xi == 14, 1, 0)
    n = vnoise(w, h, max(1, w // 4), max(1, h // 2) if h > 1 else 1, fkey(part, face))
    idx = idx + np.where(n > 0.66, 1, 0) - np.where(n < 0.3, 1, 0)
    if face == 'up':
        idx = idx + 1
    if face == 'down':
        idx = idx - 2
    cv.put(TEJA, idx)
    cv.put(LICHEN, np.full((h, w), 2), (vnoise(w, h, max(1, w // 2), max(1, h // 2) if h > 1 else 1, 9995) > 0.8))


def ridge_parts(kind='normal'):
    return [slope_box(0, 0, 8, 8, kind=kind, name='slope_f'), slope_box(8, 8, 16, 0, kind=kind, mirror=True, name='slope_b')] + ridge_cap_parts(8.0)


def gable_side(side, wall):
    """x-range of the verge overhang + the outer cap position for an izq/der gable piece."""
    if side == 'izq':
        return (0.0, 17.5), 17.5
    return (-1.5, 16.0), -1.5


def verge_band(za, ya, zb, yb, xr, side):
    """Plastered verge (bargeboard of render) under the overhanging tiles at a gable."""
    x0, x1 = (16.0, 17.3) if side == 'izq' else (-1.3, 0.0)
    return slope_box(za, ya, zb, yb, x0=x0, x1=x1, dy0=ROOF_T, dy1=ROOF_T + 2.6, mat='render', name='verge')


def hastial_parts(side, wall, piece):
    (vx0, vx1), cap = gable_side(side, wall)
    if piece == 'techo':
        parts = [slope_box(0, 0, 16, 16, x0=vx0, x1=vx1), verge_band(0, 0, 16, 16, None, side)]
        parts += gable_fill(lambda k: k - 0.5, wall)
    elif piece == 'alero':
        parts = [slope_box(-4, -4, 16, 16, x0=vx0, x1=vx1, name='slope_eave'), verge_band(-4, -4, 16, 16, None, side)]
        parts += fascia_soffit()
        parts += gutter_parts(cap_l=(side == 'izq'), cap_r=(side == 'der'))
        parts += gable_fill(lambda k: k - 0.5, wall)
    else:
        parts = [slope_box(0, 0, 8, 8, x0=vx0, x1=vx1, name='slope_f'),
                 slope_box(8, 8, 16, 0, x0=vx0, x1=vx1, mirror=True, name='slope_b'),
                 verge_band(0, 0, 8, 8, None, side), verge_band(8, 8, 16, 0, None, side)]
        parts += ridge_cap_parts(8.0, x0=vx0, x1=vx1, end=cap)
        parts += gable_fill(lambda k: min(k, 15 - k) - 0.5, wall)
    return parts


def downpipe_ring(y, rust=True):
    it = pp_iron(seed=9996, rust=0.5 if rust else 0.1)
    return [P((6.1, y, 11.7), (9.9, y + 0.8, 15.3), it, name='ring'), P((7.6, y, 15.3), (8.4, y + 0.8, 16.0), it, name='tab')]


def pipe_seg(y0, y1, cz=13.5, r=1.5):
    gz = pp_fn(gutter_paint)
    return [P((8 - r * 0.8, y0, cz - r), (8 + r * 0.8, y1, cz + r), gz, name='pipe_a'),
            P((8 - r, y0, cz - r * 0.8), (8 + r, y1, cz + r * 0.8), gz, name='pipe_b')]


def downpipe_parts(piece):
    """Galvanised downpipe hugging the wall behind (z=16), axis at z=13.5. 'codo' = the swan neck that sits under
    the gutter (in the air block in front of the wall's top block, i.e. directly below the eave's overhang) and
    brings the outlet (axis z=9.3) back to the wall; 'pie' = the shoe at the bottom that kicks the water out onto
    a small cement splash block."""
    gz = pp_fn(gutter_paint)
    if piece == 'recta':
        return pipe_seg(0, 16) + downpipe_ring(9.0) + [P((6.3, 15.0, 11.9), (9.7, 16.0, 15.1), gz, name='socket')]
    if piece == 'codo':
        L = 4.2 * R2 + 2.4
        return ([P((6.6, 4.4, 7.9), (9.4, 6.0, 10.7), gz, name='outlet'),
                 P((6.2, 5.8, 7.5), (9.8, 6.3, 11.1), gz, name='funnel'),
                 P((6.8, 2.5 - 1.2, 11.4 - L / 2), (9.2, 2.5 + 1.2, 11.4 + L / 2), gz, rot=('x', 45, (8.0, 2.5, 11.4)), name='neck_a'),
                 P((6.5, 2.5 - 0.9, 11.4 - L / 2 + 0.3), (9.5, 2.5 + 0.9, 11.4 + L / 2 - 0.3), gz, rot=('x', 45, (8.0, 2.5, 11.4)), name='neck_b')]
                + pipe_seg(0, 1.2) + downpipe_ring(0.2))
    # pie
    L = 5.0
    return (pipe_seg(4.0, 16) + downpipe_ring(11.0) +
            [P((6.8, 2.2 - 1.2, 11.0 - L / 2), (9.2, 2.2 + 1.2, 11.0 + L / 2), gz, rot=('x', -45, (8.0, 2.2, 11.0)), name='shoe_a'),
             P((6.5, 2.2 - 0.9, 11.0 - L / 2 + 0.2), (9.5, 2.2 + 0.9, 11.0 + L / 2 - 0.2), gz, rot=('x', -45, (8.0, 2.2, 11.0)), name='shoe_b'),
             P((4.5, 0, 2.5), (11.5, 0.9, 13.0), pp_fn(splash_paint), name='splash')])


def splash_paint(face, w, h, part, cv):
    x, y, z = face_coords(part, face, w, h)
    idx = np.full((h, w), 4) + (vnoise(w, h, max(1, w // 3), max(1, h // 3), 9997) > 0.6) - (face != 'up')
    cv.put(CEMENT, idx)
    if face == 'up':   # the dark wet tongue where the water lands, moss at the edge
        wet = ((x - 8) ** 2 / 9.0 + (z - 7.5) ** 2 / 20.0) < 1
        cv.tint('#141612', np.where(wet, 0.45, 0))
        cv.put(MOSS, np.full((h, w), 2), wet & ~erode(wet, 1, False) & (vnoise(w, h, max(1, w // 2), max(1, h // 2), 9998) > 0.4))


F('techo', 'Techo de tejas (faldón)', 'Tiled roof slope', roof_parts(), collision='full', sound='ceramic', render='solid')
F('techo_musgo', 'Techo de tejas con musgo', 'Mossy tiled roof slope', roof_parts('musgo'), collision='full', sound='ceramic', render='solid')
F('techo_roto', 'Techo de tejas (teja faltante)', 'Tiled roof slope with a missing tile', roof_parts('roto'), collision='full', sound='ceramic', render='solid')
F('techo_alero', 'Alero con canaleta', 'Roof eave with gutter', eave_parts(), collision='full', sound='ceramic')
F('techo_alero_musgo', 'Alero con canaleta (musgo)', 'Mossy roof eave with gutter', eave_parts('musgo'), collision='full', sound='ceramic')
F('techo_cumbrera', 'Cumbrera del techo', 'Roof ridge', ridge_parts(), collision='full', sound='ceramic')
F('cumbrera', 'Cumbrera (sobre bloque)', 'Ridge cap (on top of a block)', ridge_cap_parts(0.0), sound='ceramic', collision='none')
for _w, _wn, _we in (('revoque_blanco', '', ''), ('ladrillo', '_ladrillo', ' (brick)')):
    for _s, _sn in (('izq', 'izquierdo'), ('der', 'derecho')):
        F(f'hastial{_wn}_{_s}', f'Hastial{" de ladrillo" if _wn else ""} bajo el techo ({_sn})', f'Gable under the roof slope{_we} ({_s})',
          hastial_parts(_s, _w, 'techo'), collision='full', sound='ceramic')
        F(f'hastial{_wn}_alero_{_s}', f'Hastial{" de ladrillo" if _wn else ""} con alero ({_sn})', f'Gable eave corner{_we} ({_s})',
          hastial_parts(_s, _w, 'alero'), collision='full', sound='ceramic')
        F(f'hastial{_wn}_cumbrera_{_s}', f'Hastial{" de ladrillo" if _wn else ""} en la cumbrera ({_sn})', f'Gable peak{_we} ({_s})',
          hastial_parts(_s, _w, 'cumbrera'), collision='full', sound='ceramic')
F('bajada', 'Caño de bajada', 'Downpipe', downpipe_parts('recta'), sound='metal')
F('bajada_codo', 'Caño de bajada (cuello bajo la canaleta)', 'Downpipe swan neck (under the gutter)', downpipe_parts('codo'), sound='metal')
F('bajada_pie', 'Caño de bajada (pie con desagüe)', 'Downpipe shoe with splash block', downpipe_parts('pie'), sound='metal')


# =============================================================================================== DOORS
# Real opening doors (vanilla door logic, 32 x 64 px: row 0 = top of the upper half). The handle side is drawn on the
# RIGHT (x ~ 26); Minecraft mirrors the texture for left/right hinges.
CEDRILLO = Ramp('#2a170c', '#3d2212', '#523019', '#683e21', '#7e4d2a', '#935d34', '#a66e40', '#b7804e', '#c6925f')
PINK_FOAM = ['#e86a9a', '#f0a43a', '#6ac0e8', '#9a6ad8', '#e8d84a']
GLASS_FROST = Ramp('#3a4446', '#566264', '#738082', '#8f9b9b', '#a7b1af', '#bcc4c1', '#ced5d1', '#dfe4e0')
CREAM_EN = Ramp('#4e4836', '#6c654e', '#8a8268', '#a69e82', '#bdb59a', '#cfc8ae', '#ddd7bf', '#e8e3ce')    # ivory enamel
DGREEN = Ramp('#0c140f', '#122019', '#182b21', '#1f372a', '#284434', '#32523f', '#3e624b')                # gate paint


def drect(cv, x0, y0, x1, y1):
    return (cv.X >= x0) & (cv.X <= x1) & (cv.Y >= y0) & (cv.Y <= y1)


def door_frame_idx(X, Y, gv, gh, stile=4, top=4, bottom=9, base=4):
    st = (X < stile) | (X >= 32 - stile)
    idx = np.where(st, base + gv, base + gh)
    idx = np.where((X == 0) | (X == 31) | (Y == 0) | (Y == 63), idx - 2, idx)
    idx = np.where((X == 1) & (Y > 0) & (Y < 63), idx + 1, idx)
    idx = np.where((Y == 1) & (X > 0) & (X < 31), idx + 1, idx)
    return idx


def knob(cv, x, y, ramp=BRASS):
    """Round knob (pomo) on its rose, lit from the top-left, with the shadow it throws."""
    X, Y = cv.X, cv.Y
    rose = (X - x) ** 2 + (Y - y) ** 2 <= 5.0
    cv.tint('#000000', np.where((Y == y + 3) & (np.abs(X - x) <= 1), 0.4, 0))
    cv.put(ramp, np.full(X.shape, 2), rose)
    k = (X - x) ** 2 + (Y - y) ** 2 <= 2.1
    cv.put(ramp, np.full(X.shape, 5) + ((X <= x) & (Y <= y)) * 1 - ((X > x) & (Y > y)) * 2, k)
    cv.put(ramp, np.full(X.shape, 7), (X == x - 1) & (Y == y - 1))


def lever_plate(cv, x, y, ramp=CHROME, keyhole=True):
    """Long rectangular escutcheon (bocallave) with a lever: the picaporte of every Argentine interior door."""
    X, Y = cv.X, cv.Y
    plate = drect(cv, x - 1, y - 4, x + 1, y + 9)
    cv.tint('#000000', np.where(drect(cv, x + 2, y - 3, x + 2, y + 10) | drect(cv, x - 1, y + 10, x + 2, y + 10), 0.35, 0))
    cv.put(ramp, np.full(X.shape, 4) + (X == x - 1) - (X == x + 1) + (Y == y - 4), plate)
    lev = drect(cv, x - 6, y - 1, x, y)
    cv.put(ramp, np.full(X.shape, 6) - (Y == y) * 2, lev)
    cv.put(ramp, np.full(X.shape, 7), (X == x - 6) & (Y == y - 1))
    cv.tint('#000000', np.where(drect(cv, x - 6, y + 1, x - 1, y + 1), 0.4, 0))
    if keyhole:
        cv.col('#0a0908', (X == x) & (Y >= y + 5) & (Y <= y + 6))
        cv.col('#0a0908', (X == x) & (Y == y + 7) | False)


def hand_grime(cv, x, y, r=5, amount=0.22, seed=0):
    X, Y = cv.X, cv.Y
    d = np.sqrt((X - x) ** 2 + ((Y - y) / 1.4) ** 2)
    n = fbm(32, 64, 5900 + seed, cells=8, octaves=2)
    cv.tint('#2a1e14', np.clip((r - d) / r, 0, 1) * amount * (0.6 + 0.8 * n))


def kick_scuffs(cv, seed, y0=54, y1=62, n=7, color='#d8cbb4', amount=0.35):
    rng = np.random.default_rng(seed)
    X, Y = cv.X, cv.Y
    for k in range(n):
        x, y = int(rng.integers(3, 27)), int(rng.integers(y0, y1))
        L = int(rng.integers(2, 6))
        cv.tint(color, np.where((Y == y) & (X >= x) & (X < x + L), amount, 0))


def veneer_idx(cv, seed, base=5):
    """Rotary/flat-cut veneer: vertical grain with cathedral arches (nested parabolas) centred on the leaf."""
    X, Y = cv.X, cv.Y
    rng = np.random.default_rng(seed)
    cx = 15.5 + rng.uniform(-2, 2)
    w = (X - cx) / 16.0
    f = (Y + 70 * w * w * (1 + 0.3 * np.sin(Y / 9.0))) / 5.5 + vnoise(32, 64, 4, 8, seed) * 2.2
    band = np.floor(f).astype(int) % 4
    g = np.where(band == 0, -1, np.where(band == 2, 1, 0))
    fine = vnoise(32, 64, 16, 4, seed + 1)
    g = g + np.where(fine > 0.78, 1, 0) - np.where(fine < 0.18, 1, 0)
    return base + g


def hammered_glass(cv, m, alpha=210, seed=0, ramp=GLASS_FROST):
    """'Vidrio martillado': frosted glass with a dense pattern of round dimples (lit top-left, shaded bottom-right)."""
    X, Y = cv.X, cv.Y
    gx = (X + (Y // 3 % 2) * 1.5) % 3.0
    gy = Y % 3.0
    dx, dy = gx - 1.5, gy - 1.5
    idx = np.full(X.shape, 4) + np.where((dx < -0.4) & (dy < -0.4), 1, 0) - np.where((dx > 0.4) & (dy > 0.4), 1, 0)
    n = vnoise(32, 64, 4, 8, seed)
    idx = idx + np.where(n > 0.7, 1, 0)
    cv.put(ramp, idx, m, alpha)
    ys = Y[m]
    if ys.size:   # grime gathers at the bottom of the pane and in the corners
        t = (Y - ys.min()) / max(1, ys.max() - ys.min())
        gr = m & ((t * 0.8 + (vnoise(32, 64, 6, 10, seed + 1) - 0.5) * 0.5) > 0.7)
        cv.tint('#4a4232', np.where(gr, 0.35, 0))


def wired_glass(cv, m, alpha=200, seed=0):
    """'Vidrio armado': greenish frosted glass with the square wire mesh."""
    X, Y = cv.X, cv.Y
    cv.put(GLASS_FROST, np.full(X.shape, 4) + (vnoise(32, 64, 4, 8, seed) > 0.6), m, alpha)
    wire = m & ((X % 4 == 1) | (Y % 4 == 1))
    cv.put(IRON, np.full(X.shape, 5), wire, 235)
    cv.tint('#5a6a52', np.where(m, 0.12, 0))


def paint_chips(cv, seed, under, under_idx=3, density=0.2, region=None):
    """Chipped enamel: small flakes showing the wood (or primer) underneath, with a lit lower rim."""
    X, Y = cv.X, cv.Y
    n = vnoise(32, 64, 10, 20, seed)
    n2 = vnoise(32, 64, 16, 32, seed + 1)
    ch = (n > 1 - density) & (n2 > 0.45)
    if region is not None:
        ch &= region
    cv.put(under, np.full(X.shape, under_idx) + (n2 > 0.75), ch)
    r = rim(ch, wrap=False)
    cv.tint('#ffffff', np.where(r['out_below'], 0.18, 0))
    cv.tint('#000000', np.where(r['out_above'], 0.2, 0))


def tape_px(cv, x, y, w=3, h=2):
    cv.put(Ramp('#8a8166', '#b5ac8c', '#d2caa8'), np.full(cv.X.shape, 1) + (cv.Y == y), drect(cv, x, y, x + w - 1, y + h - 1))


@painter('door_entrada')
def p_door_entrada(v):
    """Front door of the chalet: varnished cedar, a tall pane of hammered glass behind a wrought-iron grille
    (bars, a pair of C-scrolls and a sunburst head), a lower raised panel with a diamond, brass knob and lock,
    the bottom rail bleached and cracked by fifty summers of afternoon sun."""
    cv = Cv(32, 64)
    X, Y = cv.X, cv.Y
    gv = wood_grain(32, 64, 4001, 'y', warp=1.4)
    gh = wood_grain(32, 64, 4002, 'x', warp=1.4)
    idx = door_frame_idx(X, Y, gv, gh, stile=5, top=5)
    idx = np.where((Y >= 36) & (Y <= 40) & (X >= 5) & (X <= 26), 4 + gh, idx)          # lock rail
    idx = frame_opening(idx, 5, 4, 26, 35)
    gl = drect(cv, 6, 5, 25, 34)
    idx = frame_opening(idx, 5, 41, 26, 58)
    idx, field, ins = raised_panel(idx, 6, 42, 25, 57, 3, 4 + gv, hi=(2, 1), lo=(-2, -1))
    dia = (np.abs(X - 15.5) / 7.0 + np.abs(Y - 49.5) / 4.0) <= 1.0
    dia_e = dia & ~(np.abs(X - 15.5) / 6.0 + np.abs(Y - 49.5) / 3.0 <= 1.0)
    idx = np.where(dia_e & (Y < 49.5), idx + 2, np.where(dia_e, idx - 2, idx))
    cv.put(CEDRO, idx)
    hammered_glass(cv, gl, alpha=225, seed=4003)
    # wrought-iron grille in front of the glass
    m = np.zeros((64, 32), bool)
    m |= gl & ((X == 6) | (X == 25) | (Y == 5) | (Y == 34))
    for xb in (10, 15, 16, 21):
        m |= gl & (X == xb) & (Y >= 13)
    m |= gl & (Y == 13)
    m |= gl & (Y == 27)
    for cx_, fl in ((11.5, False), (19.5, True)):
        m |= scroll_mask(32, 64, cx_, 20.5, 4.0, turns=1.25, thick=0.55, flip=fl) & gl & (Y > 13) & (Y < 27)
    r_ = np.sqrt((X + 0.5 - 16) ** 2 + (Y + 0.5 - 13) ** 2)
    ang = np.degrees(np.arctan2(13 - (Y + 0.5), X + 0.5 - 16))
    sun = gl & (Y < 13) & (((np.abs(r_ - 6.5) < 0.55)) | ((r_ < 6.5) & (r_ > 2) & (np.min([np.abs(ang - a) for a in (30, 60, 90, 120, 150)], 0) < 7)))
    m |= sun | (gl & (r_ < 2.0) & (Y < 13))
    lit = m & ~nb(m, 1, 0, False)
    cv.put(IRON, np.full((64, 32), 3) + lit * 2, m)
    cv.put(RUST, np.full((64, 32), 2), m & (vnoise(32, 64, 8, 16, 4004) > 0.78))
    cv.tint('#000000', np.where(gl & ~m & nb(m, 1, 1, False), 0.35, 0))   # the grille's shadow on the glass
    # sun damage on the lower rail and panel: bleached, crazed varnish
    sunb = (Y > 52) & (vnoise(32, 64, 6, 12, 4005) > 0.35)
    cv.tint('#b89a74', np.where(sunb, 0.25 * np.clip((Y - 52) / 10.0, 0, 1), 0))
    craz = (Y > 56) & (((X * 3 + Y * 5) % 11 == 0) | ((X * 7 + Y) % 13 == 0)) & (X > 1) & (X < 30)
    cv.tint('#24160c', np.where(craz, 0.4, 0))
    hand_grime(cv, 26, 38, r=5, amount=0.3, seed=1)
    knob(cv, 26, 38)
    cv.put(BRASS, np.full((64, 32), 4) + (Y == 42), drect(cv, 25, 42, 27, 45))      # lock escutcheon
    cv.col('#0a0806', (X == 26) & (Y >= 43) & (Y <= 44))
    cv.put(BRASS, np.full((64, 32), 6), (X == 16) & (Y == 2) | (X == 15) & (Y == 2))  # the peephole
    cv.col('#0a0806', (X == 15) & (Y == 2))
    return cv.out()


def flush_door(seed, white=False):
    """Hollow-core flush door ('puerta placa'): cedar-look veneer, or white enamel over it."""
    cv = Cv(32, 64)
    X, Y = cv.X, cv.Y
    if white:
        idx = np.full((64, 32), 5) + np.where((X % 5 == 2) & (vnoise(32, 64, 6, 4, seed) > 0.55), 1, 0)
        idx = idx - np.where(vnoise(32, 64, 4, 8, seed + 1) < 0.2, 1, 0)
        idx = np.where((X == 0) | (X == 31) | (Y == 0) | (Y == 63), idx - 2, idx)
        idx = np.where((X == 1) | (Y == 1), idx + 1, idx)
        cv.put(ENAMEL_W, idx)
        cv.tint('#a08a54', np.where(vnoise(32, 64, 2, 4, seed + 2) > 0.5, 0.12, 0.05))       # nicotine yellowing
        # paint runs that dried decades ago
        for x in (7, 19):
            cv.tint('#ffffff', np.where((X == x) & (Y >= 20) & (Y <= 25 + x % 4), 0.12, 0))
            cv.tint('#000000', np.where((X == x) & (Y == 26 + x % 4), 0.12, 0))
        paint_chips(cv, seed + 3, CEDRILLO, 4, density=0.07, region=(Y > 55) | (X > 28) | (X < 2))
    else:
        idx = veneer_idx(cv, seed)
        idx = np.where((X == 0) | (X == 31) | (Y == 0) | (Y == 63), idx - 2, idx)
        idx = np.where((X == 1) | (Y == 1), idx + 1, idx)
        cv.put(CEDRILLO, idx)
        sheen = (np.abs((X - Y * 0.35) % 22 - 4) < 1.5)
        cv.tint('#e8c898', np.where(sheen, 0.06, 0))
    kick_scuffs(cv, seed + 4, color='#3a2a1c' if white else '#d8b88a', amount=0.3)
    return cv


@painter('door_placa')
def p_door_placa(v):
    """Interior hollow-core door with cedar-look veneer, chrome picaporte, hand grime, a crushed dent at kick
    height where the cheap skin cracked."""
    cv = flush_door(4100)
    X, Y = cv.X, cv.Y
    hand_grime(cv, 25, 37, r=6, amount=0.25, seed=2)
    dent = ((X - 9) ** 2 / 6.0 + (Y - 52) ** 2 / 3.0) <= 1
    cv.tint('#140c06', np.where(dent, 0.35, 0))
    cv.put(CEDRILLO, np.full((64, 32), 7), dent & ~nb(dent, 1, 0, False))
    crk = path_mask(line_px(6, 51, 12, 53), 32, 64, wrap=False)
    cv.col('#1a0f08', crk)
    lever_plate(cv, 26, 37)
    return cv.out()


@painter('door_placa_blanca')
def p_door_placa_blanca(v):
    """Interior flush door painted white enamel, yellowed, chipped along the lock edge, brass knob."""
    cv = flush_door(4200, white=True)
    hand_grime(cv, 26, 37, r=6, amount=0.3, seed=3)
    knob(cv, 26, 37)
    cv.col('#0a0908', (cv.X == 26) & (cv.Y >= 41) & (cv.Y <= 42))
    cv.put(BRASS, np.full((64, 32), 3), drect(cv, 25, 40, 27, 40))
    return cv.out()


@painter('door_lucia')
def p_door_lucia(v):
    """Lucía's door: white flush door, foam letters L-U-C-I-A in five colours, stickers, and a child's crayon
    drawing taped at her eye level: the family, Choripán... and a doll drawn bigger than everyone, with a red
    stitched mouth. In the corner someone scribbled a tall black figure."""
    cv = flush_door(4300, white=True)
    X, Y = cv.X, cv.Y
    word = 'LUCIA'
    x = 3
    for k, ch in enumerate(word):
        g = text_mask(ch)[2:]
        m = np.zeros((64, 32), bool)
        dy = (-1, 1, 0, -1, 1)[k]
        stamp(m, g, x, 4 + dy)
        side = nb(m, 0, 1, False) & ~m                      # foam thickness on the right
        cv.tint('#000000', np.where(nb(m | side, 1, 1, False) & ~(m | side), 0.35, 0))
        cv.col(PINK_FOAM[k], side)
        cv.mul(np.where(side, 0.62, 1.0))
        cv.col(PINK_FOAM[k], m)
        cv.tint('#ffffff', np.where(m & ~nb(m, 1, 0, False), 0.45, 0))
        x += g.shape[1] + 1
    # crayon drawing on a sheet of paper (A5-ish), slightly tilted by the tape
    paper = drect(cv, 6, 17, 25, 33)
    cv.tint('#000000', np.where(drect(cv, 7, 34, 26, 34) | drect(cv, 26, 18, 26, 34), 0.3, 0))
    cv.put(Ramp('#b8b2a2', '#d6d1c3', '#ebe7dc', '#f4f1ea'), np.full((64, 32), 3) - (X == 6) - (Y == 33) + 0 * Y, paper)
    def crayon(pts_rows, x0, y0, color):
        mm = np.zeros((64, 32), bool)
        stamp(mm, ascii_mask(pts_rows), x0, y0)
        cv.col(color, mm & paper)
    cv.col('#6aa0d8', paper & (Y == 18))                                # sky line
    cv.col('#5a9a3a', paper & (Y == 32))                                # grass
    cv.col('#e8b830', paper & ((X - 23) ** 2 + (Y - 20) ** 2 <= 2))      # sun
    for k, (xx, tall, col) in enumerate(((8, 9, '#d84a7a'), (11, 10, '#3a5ad8'), (14, 6, '#e86a9a'), (17, 7, '#8a5ad8'))):
        crayon(['.#.', '###', '.#.', '.#.', '#.#'][:2] + ['.#.'] * (tall - 5) + ['.#.', '#.#'], xx, 31 - tall, col)
    crayon(['#..##', '#####', '.#.#.'], 19, 29, '#7a4a2a')              # Choripán, a sausage with legs
    crayon(['.###.', '#####', '#.#.#', '#####', '.###.', '..#..', '.###.', '#.#.#', '..#..', '.#.#.'], 20, 21, '#e8d0b8')
    cv.col('#c81818', paper & (Y == 24) & (X >= 21) & (X <= 23))         # the doll's red mouth, stitched
    cv.col('#c81818', paper & ((X == 21) | (X == 23)) & (Y == 23))
    cv.col('#1a1414', paper & (X == 21) & (Y == 22) | paper & (X == 23) & (Y == 22))
    crayon(['.#', '##', '.#', '.#', '.#', '.#', '#.', '#.', '.#', '.#', '.#', '#.'], 23, 19, '#151212')   # tall black scribble
    tape_px(cv, 5, 16)
    tape_px(cv, 24, 16)
    # stickers: a heart, a star, a peeled unicorn-ish horse
    for rows, (sx, sy), col in ((HEART, (4, 40), '#d8486a'), (STAR, (11, 47), '#e8c23a'), (BUTTER, (18, 55), '#9a6ad8')):
        mm = np.zeros((64, 32), bool)
        stamp(mm, ascii_mask(rows), sx, sy)
        cv.col('#f4eee6', dilate(mm, 1, False) & ~mm)
        cv.col(col, mm)
    hand_grime(cv, 26, 37, r=5, amount=0.25, seed=4)
    knob(cv, 26, 37)
    return cv.out()


@painter('door_toti')
def p_door_toti(v):
    """Toti's door: veneer, a printed 'NO PASAR' sign, a skull sticker, and the cardboard hanger on the handle:
    'EN RANKED' / 'NO MOLESTAR'."""
    cv = flush_door(4400)
    X, Y = cv.X, cv.Y
    sign = drect(cv, 5, 6, 26, 16)
    cv.tint('#000000', np.where(drect(cv, 6, 17, 27, 17) | drect(cv, 27, 7, 27, 17), 0.35, 0))
    cv.put(Ramp('#8a1a14', '#b8261c', '#d63a2a'), np.full((64, 32), 1) + (Y == 6), sign)
    cv.col('#f2ece0', sign & ((X == 5) | (X == 26) | (Y == 6) | (Y == 16)))
    t1 = tiny_mask('NO PASAR')[1:]
    tm = np.zeros((64, 32), bool)
    stamp(tm, t1, 16 - t1.shape[1] // 2, 9)
    cv.col('#f8f2e8', tm)
    tape_px(cv, 4, 5, 2, 2)
    tape_px(cv, 25, 5, 2, 2)
    skull = ['.###.', '#####', '#.#.#', '#####', '.#.#.']
    mm = np.zeros((64, 32), bool)
    stamp(mm, ascii_mask(skull), 8, 22)
    cv.col('#101010', dilate(mm, 1, False) & ~mm)
    cv.col('#e8e8e0', mm)
    bolt = ['..##', '.##.', '####', '.##.', '##..']
    mm = np.zeros((64, 32), bool)
    stamp(mm, ascii_mask(bolt), 15, 24)
    cv.col('#1a1a1a', dilate(mm, 1, False) & ~mm)
    cv.col('#f0e030', mm)
    hand_grime(cv, 25, 37, r=6, amount=0.3, seed=5)
    lever_plate(cv, 26, 37)
    # door hanger hanging from the lever (cardboard, black with neon letters)
    hang = drect(cv, 16, 39, 29, 60)
    hole = (X - 22.5) ** 2 + (Y - 41) ** 2 <= 1.6
    cv.tint('#000000', np.where(drect(cv, 17, 61, 30, 61) | drect(cv, 30, 40, 30, 61), 0.4, 0))
    cv.put(Ramp('#0c0c12', '#16161f', '#22222e'), np.full((64, 32), 1) + (X == 16), hang & ~hole)
    for tt, yy, col in (('EN', 43, '#5aff7a'), ('RAN', 49, '#ff3aa8'), ('KED', 55, '#ff3aa8')):
        t_ = tiny_mask(tt)[1:]
        mm = np.zeros((64, 32), bool)
        stamp(mm, t_, 23 - t_.shape[1] // 2, yy)
        cv.col(col, mm & hang)
    return cv.out()


@painter('door_bano')
def p_door_bano(v):
    """Bathroom door: white flush door with a small hand-painted ceramic oval 'BAÑO' (blue letters, two flowers),
    the key left in the lock, damp swelling at the bottom (paint blistered)."""
    cv = flush_door(4500, white=True)
    X, Y = cv.X, cv.Y
    ov = ((X - 15.5) / 14.0) ** 2 + ((Y - 12.0) / 7.0) ** 2 <= 1
    cv.tint('#000000', np.where((((X - 16.5) / 14.0) ** 2 + ((Y - 13.0) / 7.0) ** 2 <= 1) & ~ov, 0.35, 0))
    cv.put(Ramp('#8a8a84', '#c4c2ba', '#e4e2da', '#f4f2ec'), np.full((64, 32), 3) - (~erode(ov, 1, False) & ov) * 2, ov)
    tm = np.zeros((64, 32), bool)
    t = text_mask('BAÑO')
    stamp(tm, t, 16 - t.shape[1] // 2, 5)
    cv.col('#2a4a9a', tm & ov)
    for fx in (6, 25):
        cv.col('#d85a3a', (X == fx) & (Y == 11) | (X == fx - 1) & (Y == 12) | (X == fx + 1) & (Y == 12) | (X == fx) & (Y == 13))
        cv.col('#e8c040', (X == fx) & (Y == 12))
        cv.col('#4a8a3a', (X == fx) & (Y == 14))
    knob(cv, 26, 37, ramp=CHROME)
    cv.put(CHROME, np.full((64, 32), 5) + (Y == 41), drect(cv, 25, 41, 27, 42) | drect(cv, 26, 43, 26, 45))   # the key
    bl = (Y > 56) & (vnoise(32, 64, 8, 16, 4501) > 0.55)
    cv.tint('#6a5a3a', np.where(bl, 0.3, 0))
    cv.tint('#ffffff', np.where(bl & ~nb(bl, 1, 0, False), 0.25, 0))
    return cv.out()


@painter('door_nona')
def p_door_nona(v):
    """The Nona's door, the original 1950s one: dark cedar with six raised panels, an old brass lever, a holy card
    taped on the top panel and a dried olive sprig from Palm Sunday tucked behind it."""
    cv = Cv(32, 64)
    X, Y = cv.X, cv.Y
    gv = wood_grain(32, 64, 4601, 'y', warp=1.8)
    gh = wood_grain(32, 64, 4602, 'x', warp=1.8)
    idx = door_frame_idx(X, Y, gv, gh, stile=4, base=3)
    idx = np.where((X >= 15) & (X <= 16) & (Y > 3) & (Y < 60), 3 + gv, idx)
    for (y0, y1) in ((4, 18), (22, 38), (42, 59)):
        for (x0, x1) in ((4, 14), (17, 27)):
            idx = frame_opening(idx, x0, y0, x1, y1)
            idx, field, ins = raised_panel(idx, x0 + 1, y0 + 1, x1 - 1, y1 - 1, 2, 3 + gv, hi=(2, 1), lo=(-2, -1))
    cv.put(CEDRO, idx)
    cv.tint('#0a0604', np.where(vnoise(32, 64, 4, 8, 4603) > 0.6, 0.15, 0))
    # holy card on the upper right panel: gold border, blue mantle, halo, pink face
    card = drect(cv, 19, 6, 25, 15)
    cv.tint('#000000', np.where(drect(cv, 20, 16, 26, 16) | drect(cv, 26, 7, 26, 16), 0.35, 0))
    cv.put(Ramp('#7a6020', '#b08a30', '#d8b44a'), np.full((64, 32), 2), card)
    inner = drect(cv, 20, 7, 24, 14)
    cv.col('#d8d0b8', inner)
    cv.col('#2a4a8a', inner & (Y >= 10) & ((X - 22) ** 2 / 6.0 + (Y - 14) ** 2 / 20.0 <= 1))
    cv.col('#e8c040', inner & ((X - 22) ** 2 + (Y - 8.5) ** 2 <= 2.2))
    cv.col('#d8a890', inner & (X == 22) & (Y == 9))
    tape_px(cv, 21, 5, 3, 1)
    # dried olive sprig (grey-green leaves) poking from behind the card
    for (lx_, ly_) in ((18, 5), (17, 4), (16, 3), (18, 3), (17, 2), (19, 4)):
        cv.col('#6a7454' if (lx_ + ly_) % 2 else '#4a5438', (X == lx_) & (Y == ly_))
    cv.col('#3a2a1a', (X == 18) & (Y == 6))
    hand_grime(cv, 25, 37, r=5, amount=0.25, seed=6)
    lever_handle(cv, 27, 37)
    return cv.out()


@painter('door_cocina')
def p_door_cocina(v):
    """Kitchen door to the patio: ivory enamel over wood, six glazed lights with a red gingham half-curtain on the
    lower two, two lower panels, chipped and sun-faded at the bottom, aluminium knob."""
    cv = Cv(32, 64)
    X, Y = cv.X, cv.Y
    gv = wood_grain(32, 64, 4701, 'y', warp=1.0)
    gh = wood_grain(32, 64, 4702, 'x', warp=1.0)
    idx = door_frame_idx(X, Y, np.sign(gv) * 0, np.sign(gh) * 0, stile=4, base=5)
    idx = frame_opening(idx, 4, 4, 27, 33)
    gl = drect(cv, 5, 5, 26, 32)
    mun = gl & (((X >= 15) & (X <= 16)) | (Y == 14) | (Y == 23))
    idx = np.where(mun, 5 + (Y == 14) + (Y == 23), idx)
    for (x0, x1) in ((4, 14), (17, 27)):
        idx = frame_opening(idx, x0, 38, x1, 58)
        idx, field, ins = raised_panel(idx, x0 + 1, 39, x1 - 1, 57, 2, np.full((64, 32), 5), hi=(1, 1), lo=(-2, -1))
    cv.put(CREAM_EN, idx)
    pane = gl & ~mun
    door_glass(cv, pane, 4703, alpha=110)
    cur = pane & (Y >= 24)
    ging = ((X // 2 + Y // 2) % 2 == 0)
    cv.put(Ramp('#7a1a14', '#a8281e', '#c83a2a', '#e8d8c8'), np.where(((X // 2) % 2 == 0) & ((Y // 2) % 2 == 0), 1, np.where(ging, 3, 2)), cur, 240)
    cv.put(Ramp('#7a1a14', '#a8281e', '#c83a2a', '#e8d8c8'), np.full((64, 32), 0), cur & (Y == 24) & (X % 2 == 0), 240)
    cv.put(CHROME, np.full((64, 32), 6), (Y == 24) & pane)       # the curtain wire
    paint_chips(cv, 4704, PINO, 4, density=0.16, region=(Y > 46) | (X > 28))
    cv.tint('#c8b890', np.where((Y > 50) & (vnoise(32, 64, 4, 8, 4705) > 0.4), 0.15, 0))
    hand_grime(cv, 26, 36, r=6, amount=0.3, seed=7)
    knob(cv, 26, 36, ramp=CHROME)
    return cv.out()


@painter('door_lavadero')
def p_door_lavadero(v):
    """Laundry door, 'puerta de chapa': pressed steel painted grey-green, wired glass in the top, two embossed
    panels, a louvred vent at the bottom (the gas regulations), paint peeling to primer and rust at the foot."""
    cv = Cv(32, 64)
    X, Y = cv.X, cv.Y
    LAVG = Ramp('#1a2220', '#26302d', '#323e3a', '#3f4c47', '#4d5b55', '#5c6a63', '#6c7a72', '#7e8b83')
    idx = np.full((64, 32), 4) + (vnoise(32, 64, 4, 8, 4801) > 0.65) - (vnoise(32, 64, 4, 8, 4802) < 0.25)
    idx = np.where((X <= 1) | (X >= 30) | (Y <= 1) | (Y >= 62), idx - 1, idx)
    idx = np.where((X == 0) | (Y == 0), idx + 2, idx)
    for (y0, y1) in ((30, 41), (44, 52)):
        emb = drect(cv, 5, y0, 26, y1)
        r_ = rim(emb, wrap=False)
        idx = np.where(r_['in_top'] | r_['in_left'], idx + 2, idx)
        idx = np.where(r_['in_bot'] | r_['in_right'], idx - 2, idx)
    cv.put(LAVG, idx)
    gl = drect(cv, 5, 5, 26, 25)
    cv.put(LAVG, np.full((64, 32), 6), drect(cv, 4, 4, 27, 4) | drect(cv, 4, 4, 4, 26))
    cv.put(LAVG, np.full((64, 32), 1), drect(cv, 4, 26, 27, 26) | drect(cv, 27, 4, 27, 26))
    wired_glass(cv, gl, seed=4803)
    # louvred vent: slots that are really open (see-through)
    for k in range(3):
        y = 55 + k * 2
        slot = drect(cv, 9, y, 22, y)
        cv.a = np.where(slot, 0, cv.a)
        cv.put(LAVG, np.full((64, 32), 6), drect(cv, 9, y - 1, 22, y - 1))
    paint_chips(cv, 4804, Ramp('#5a4a3a', '#7a6a52', '#9a8a6a', '#b0a080'), 2, density=0.22, region=(Y > 40) | (X < 3) | (X > 28))
    rs = (Y > 57) & (vnoise(32, 64, 8, 8, 4805) > 0.35) | (vnoise(32, 64, 6, 12, 4806) > 0.9)
    cv.put(RUST, np.full((64, 32), 2) + (vnoise(32, 64, 16, 16, 4807) > 0.6), rs & (cv.a > 0))
    for (x, y) in ((12, 41), (20, 52), (7, 26)):
        cv.put(RUST, np.full((64, 32), 1), (X == x) & (Y > y) & (Y < y + 5) & (cv.a > 0))
    hand_grime(cv, 26, 35, r=5, amount=0.3, seed=8)
    lever_plate(cv, 26, 35, ramp=IRON)
    return cv.out()


@painter('door_sotano')
def p_door_sotano(v):
    """Basement door: five old pine boards gone grey, real gaps between them (you see the dark through), a
    Z-brace, hand-forged strap hinges, an open hasp with a padlock hanging, rusty nails, the foot rotted ragged."""
    cv = Cv(32, 64)
    X, Y = cv.X, cv.Y
    board = X // 6.4
    bx = (X % 6.4)
    gap = (bx < 1.0) & (X > 0)
    rc = np.random.default_rng(4901)
    tone = rc.choice([-1, 0, 0, 1], 6)[board.astype(int)]
    gvv = wood_grain(32, 64, 4902, 'y', warp=2.2, pores=0.06)
    idx = 3 + tone + gvv
    idx = np.where(bx < 1.8, idx - 1, idx)
    idx = np.where((bx >= 5.4), idx + 1, idx)
    for (y0, y1) in ((6, 10), (52, 56)):          # ledges
        led = drect(cv, 1, y0, 30, y1)
        idx = np.where(led, 4 + wood_grain(32, 64, 4903 + y0, 'x', warp=1.0), idx)
        idx = np.where(led & (Y == y0), idx + 2, idx)
        idx = np.where(led & (Y == y1), idx - 2, idx)
        idx = np.where(drect(cv, 1, y1 + 1, 30, y1 + 1), idx - 2, idx)
    dd = (X - 2) * (41.0 / 27.0) - (51 - Y)
    brace = (np.abs(dd) < 2.4) & (Y > 10) & (Y < 52) & (X > 1) & (X < 30)
    gb = wood_grain(32, 64, 4907, 'x', warp=0.6)
    idx = np.where(brace, 5 + gb, idx)
    idx = np.where(brace & (dd < -1.4), idx + 1, idx)
    idx = np.where(brace & (dd > 1.4), idx - 2, idx)
    idx = np.where(~brace & (dd > 2.4) & (dd < 3.6) & (Y > 10) & (Y < 52), idx - 2, idx)
    cv.put(WEATHER, idx)
    cv.a = np.where(gap & ~brace & ~(drect(cv, 1, 6, 30, 10) | drect(cv, 1, 52, 30, 56)), 0, cv.a)
    # rotten foot
    foot = (Y >= 61 - np.round(2 * vnoise(32, 1, 8, 1, 4904)[0] * 2).astype(int)[None, :].repeat(64, 0) * 0) & (Y >= 60)
    ragged = (Y >= 60) & (vnoise(32, 64, 16, 8, 4905) > 0.55)
    cv.a = np.where(ragged | (Y == 63) & (X % 3 != 1), 0, cv.a)
    cv.tint('#1a1612', np.where((Y > 54) & (cv.a > 0), 0.35, 0))
    # strap hinges (on the left, the hinge side is mirrored by Minecraft as needed)
    for yc in (8, 54):
        st = drect(cv, 0, yc - 1, 14, yc + 1) & ~((X > 10) & (np.abs(Y - yc) == 1))
        cv.put(IRON, np.full((64, 32), 3) + (Y == yc - 1) * 2, st)
        cv.put(RUST, np.full((64, 32), 3), st & (vnoise(32, 64, 16, 32, 4906) > 0.6))
        for nx in (3, 8, 13):
            cv.put(IRON, np.full((64, 32), 6), (X == nx) & (Y == yc))
    for (nx, ny) in ((5, 8), (11, 8), (17, 8), (23, 8), (29, 8), (5, 54), (17, 54), (23, 54), (29, 54)):
        cv.put(IRON, np.full((64, 32), 5), (X == nx) & (Y == ny))
        cv.put(RUST, np.full((64, 32), 1), (X == nx) & (Y > ny) & (Y < ny + 4))
    # hasp and padlock, open
    cv.put(IRON, np.full((64, 32), 4) + (Y == 30), drect(cv, 24, 30, 30, 32))
    lock = drect(cv, 25, 35, 28, 39)
    cv.put(BRASS, np.full((64, 32), 3) + (Y == 35) - (Y == 39), lock)
    cv.put(IRON, np.full((64, 32), 5), ((X == 25) & (Y >= 32) & (Y <= 34)) | ((X == 26) & (Y == 31)))
    cv.col('#0a0806', (X == 26) & (Y == 37))
    return cv.out()


@painter('door_placard')
def p_door_placard(v):
    """Louvred wardrobe door (placard) in varnished pine: two louvre fields with see-through slits between the
    slats (whatever hides inside glows through), a small brass knob. Place casa_placard_maletero above it."""
    cv = Cv(32, 64)
    X, Y = cv.X, cv.Y
    gv = wood_grain(32, 64, 5001, 'y', warp=1.2)
    gh = wood_grain(32, 64, 5002, 'x', warp=1.2)
    idx = door_frame_idx(X, Y, gv, gh, stile=4, base=5)
    idx = np.where((Y >= 30) & (Y <= 34), 5 + gh, idx)
    open_ = np.zeros((64, 32), bool)
    for (y0, y1) in ((4, 29), (35, 59)):
        f = drect(cv, 4, y0, 27, y1)
        ly = (Y - y0) % 3
        idx = np.where(f, np.where(ly == 0, 7, np.where(ly == 1, 5, 2)) + np.sign(gh), idx)
        idx = np.where(f & ((X == 4) | (X == 27)), 1, idx)
        open_ |= f & (ly == 2) & (X > 4) & (X < 27)
        idx = frame_opening(idx, 3, y0 - 1, 28, y1 + 1)
    cv.put(PINO, idx)
    cv.put(PINO, np.full((64, 32), 0), open_)                       # slits: binary alpha (the door renders 'cutout'):
    cv.a = np.where(open_ & ((X % 5) != 2), 0, cv.a)                # see-through gaps, every 5th texel a dark slat edge
    hand_grime(cv, 26, 32, r=4, amount=0.3, seed=9)
    knob(cv, 26, 32)
    return cv.out()


def gate_iron(cv, m, seed, ramp=DGREEN):
    """Painted iron: lit top rim, dark bottom rim, rust where paint is gone."""
    lit = m & ~nb(m, 1, 0, False)
    dark = m & ~nb(m, -1, 0, False)
    cv.put(ramp, np.full((64, 32), 4) + lit * 2 - dark * 2, m)
    rs = m & (vnoise(32, 64, 8, 16, seed) > 0.72)
    cv.put(RUST, np.full((64, 32), 2) + (vnoise(32, 64, 16, 32, seed + 1) > 0.6), rs)


@painter('door_reja')
def p_door_reja(v):
    """Pedestrian gate of the front fence: dark-green iron frame, bars with a row of C-scrolls and little spear
    finials, a sheet-metal lower half with a stamped diamond and the mailbox slot, the latch box."""
    cv = Cv(32, 64)
    X, Y = cv.X, cv.Y
    m = np.zeros((64, 32), bool)
    m |= (X <= 1) | (X >= 30) | (Y >= 62) | ((Y >= 4) & (Y <= 5)) | ((Y >= 34) & (Y <= 35))
    for xb in range(5, 29, 4):
        m |= (X == xb) & (Y >= 2) & (Y <= 34)
        m |= (Y <= 2) & (np.abs(X - xb) <= (Y)) & (Y >= 0) & (np.abs(X - xb) <= 1) & ~((Y == 0) & (X != xb))
    for cx_ in range(7, 29, 4):          # the welded rings between the bars, so typical of 1950s rejas
        rr_ = np.sqrt((X + 0.5 - cx_) ** 2 + (Y + 0.5 - 10.5) ** 2)
        m |= (np.abs(rr_ - 1.9) < 0.55) & (X > 1) & (X < 30)
    m |= ((Y >= 14) & (Y <= 15)) & (X > 1) & (X < 30)
    sheet = drect(cv, 2, 36, 29, 61)
    cv.a = np.where(m | sheet, 255, 0)
    gate_iron(cv, m & ~sheet, 5101)
    sidx = np.full((64, 32), 4) + (vnoise(32, 64, 4, 8, 5102) > 0.6)
    dia = (np.abs(X - 15.5) / 11.0 + np.abs(Y - 48.5) / 10.0) <= 1.0
    de = dia & ~(np.abs(X - 15.5) / 9.5 + np.abs(Y - 48.5) / 8.5 <= 1.0)
    sidx = np.where(de & (Y < 48.5), sidx + 2, np.where(de, sidx - 2, sidx))
    cv.put(DGREEN, sidx, sheet)
    slot = drect(cv, 10, 40, 21, 41)
    cv.put(DGREEN, np.full((64, 32), 6), drect(cv, 9, 39, 22, 39))
    cv.col('#060806', slot)
    t = tiny_mask('CARTAS')[1:]
    tm = np.zeros((64, 32), bool)
    stamp(tm, t, 16 - t.shape[1] // 2, 43)
    cv.col('#b8b090', tm & ~dia | tm & dia)
    rs = sheet & ((Y > 56) & (vnoise(32, 64, 8, 8, 5103) > 0.35) | (vnoise(32, 64, 8, 16, 5104) > 0.86))
    cv.put(RUST, np.full((64, 32), 2) + (vnoise(32, 64, 16, 16, 5105) > 0.6), rs)
    lb = drect(cv, 24, 30, 29, 38)
    cv.put(IRON, np.full((64, 32), 3) + (Y == 30) * 2 - (Y == 38), lb)
    cv.a = np.where(lb, 255, cv.a)
    cv.put(CHROME, np.full((64, 32), 5) - (Y == 33), drect(cv, 19, 32, 24, 33))
    cv.a = np.where(drect(cv, 19, 32, 24, 33), 255, cv.a)
    cv.col('#0a0806', (X == 27) & (Y >= 35) & (Y <= 36))
    return cv.out()


@painter('door_porton')
def p_door_porton(v):
    """Car gate leaf (portón): pressed sheet steel with vertical ribs, painted dark green, a band of bars with
    arrow tips on top, a dent, rust running down from every rib and the bottom eaten through."""
    cv = Cv(32, 64)
    X, Y = cv.X, cv.Y
    m = np.zeros((64, 32), bool)
    m |= (X <= 1) | (X >= 30) | ((Y >= 10) & (Y <= 11))
    for xb in range(4, 30, 4):
        m |= (X == xb) & (Y >= 2) & (Y <= 10)
        m |= (Y < 2) & (np.abs(X - xb) <= Y) & (np.abs(X - xb) <= 1)
    sheet = (Y >= 12) & (X >= 2) & (X <= 29)
    cv.a = np.where(m | sheet, 255, 0)
    gate_iron(cv, m & ~sheet, 5201)
    rib = (X % 4 == 1)
    sidx = np.full((64, 32), 4) + rib * 2 - (X % 4 == 2) * 1 + (vnoise(32, 64, 4, 8, 5202) > 0.6)
    sidx = np.where((Y == 12) | (Y == 36), sidx + 2, sidx)
    sidx = np.where((Y == 13) | (Y == 37), sidx - 2, sidx)
    dent = ((X - 9) ** 2 / 10.0 + (Y - 46) ** 2 / 6.0) <= 1
    sidx = np.where(dent & (Y < 46), sidx - 1, np.where(dent, sidx + 1, sidx))
    cv.put(DGREEN, sidx, sheet)
    for xb in range(1, 30, 4):
        L = 6 + (xb * 7) % 9
        cv.put(RUST, np.full((64, 32), 1), sheet & (X == xb) & (Y > 37) & (Y < 37 + L))
    rs = sheet & ((Y > 54) & (vnoise(32, 64, 8, 8, 5203) > 0.3) | (vnoise(32, 64, 6, 16, 5204) > 0.88))
    cv.put(RUST, np.full((64, 32), 2) + (vnoise(32, 64, 16, 16, 5205) > 0.6), rs)
    holes = (Y >= 61) & (vnoise(32, 64, 16, 8, 5206) > 0.6)
    cv.a = np.where(holes & sheet, 0, cv.a)
    cv.put(IRON, np.full((64, 32), 4) + (Y == 30) * 2, drect(cv, 27, 30, 29, 36))   # latch
    return cv.out()


DOORS = [
    ('puerta_entrada', 'Puerta de entrada', 'Front door', 'entrada', 'translucent', 'wood'),
    ('puerta_placa', 'Puerta placa', 'Flush interior door', 'placa', 'cutout', 'wood'),
    ('puerta_placa_blanca', 'Puerta placa blanca', 'White flush door', 'placa_blanca', 'cutout', 'wood'),
    ('puerta_lucia', 'Puerta del cuarto de Lucía', "Lucía's door", 'lucia', 'cutout', 'wood'),
    ('puerta_toti', 'Puerta del cuarto de Toti', "Toti's door", 'toti', 'cutout', 'wood'),
    ('puerta_bano', 'Puerta del baño', 'Bathroom door', 'bano', 'cutout', 'wood'),
    ('puerta_nona', 'Puerta del cuarto de la Nona', "The Nona's door", 'nona', 'cutout', 'wood'),
    ('puerta_cocina', 'Puerta de la cocina (al patio)', 'Kitchen door (to the patio)', 'cocina', 'translucent', 'wood'),
    ('puerta_lavadero', 'Puerta de chapa del lavadero', 'Steel laundry door', 'lavadero', 'translucent', 'metal'),
    ('puerta_sotano', 'Puerta del sótano', 'Basement plank door', 'sotano', 'cutout', 'wood'),
    ('puerta_placard', 'Puerta de placard', 'Louvred wardrobe door', 'placard', 'cutout', 'wood'),
    ('puerta_reja', 'Puerta de reja (vereda)', 'Front fence gate', 'reja', 'cutout', 'metal'),
    ('porton', 'Portón de chapa', 'Sheet-steel car gate leaf', 'porton', 'cutout', 'metal'),
]
for _k, _es, _en, _p, _r, _snd in DOORS:
    Door('casa_' + _k, _es, _en, door_mat((lambda name: (lambda: PAINTERS['door_' + name](0)))(_p)), kit=KIT, render=_r, sound=_snd)


def trim_wood(seed, ramp=CEDRO, base=4):
    def p(face, w, h, part):
        x, y, z = face_coords(part, face, w, h)
        along = 'x' if (part.size()[0] >= part.size()[2] and face in ('north', 'south', 'up', 'down')) else ('y' if part.size()[1] > 4 else 'x')
        idx = np.full((h, w), base) + wood_grain(w, h, seed + fkey(part, face), along, period=False, pores=0.02)
        if face == 'up':
            idx = idx + 1
        if face == 'down':
            idx = idx - 2
        cv = Cv(w, h)
        cv.put(ramp, idx)
        if face == 'up':   # dust on every horizontal ledge
            cv.tint('#8a826f', np.where(vnoise(w, h, max(1, w // 3), max(1, h // 2), seed + 7) > 0.45, 0.32, 0.12))
        return cv.out()
    return p


# =============================================================================================== WINDOWS
# In-wall pieces: each REPLACES a wall block. 'facing' = the EXTERIOR (bars and roller blind outside, the casements
# in the middle of the wall, the interior sill and the blind-box cover inside). Jambs, sill and lintel are white
# lime render on the outside (a render surround that also reads well inside a brick facade) and white latex inside.
# 2x2 window: inf (lower) / sup (upper) x izq / der, where izq/der = left/right of a viewer OUTSIDE looking at the
# window (izq = authoring +x: its jamb is at x 14..16; der has its jamb at x 0..2). '_cerrada' = roller blind down.
# Half-closed blind = sup_cerrada pieces over open inf pieces.
WIN_FRAME_Z = (6.0, 8.5)


def wall_face_painter(ext='revoque_blanco', inn='pared_bano', split=None, lining=None):
    """Faces of a wall chunk: north (exterior) = facade render, south (interior) = latex, reveal faces split at the
    window frame (dark contact line where the frame sits). lining: a painter for the inner half of the reveal (the
    painted wooden box frame of the 2x2 windows, so the window looks right on any room's wall colour)."""
    split = split or WIN_FRAME_Z
    pe, pi = aligned(T(ext)), aligned(T(inn))

    def p(face, w, h, part):
        if face == 'north':
            return pe(face, w, h, part)
        if face == 'south':
            return pi(face, w, h, part)
        x, y, z = face_coords(part, face, w, h)
        a, b = pe(face, w, h, part), (lining or pi)(face, w, h, part)
        out = np.where((z < (split[0] + split[1]) / 2)[..., None], a, b).astype(float)
        near = (np.abs(z - split[0]) < 0.6) | (np.abs(z - split[1]) < 0.6)
        out[..., :3] *= np.where(near, 0.62, 1.0)[..., None]
        edge = (z < 0.6)                                              # the arris at the facade catches light
        out[..., :3] = np.where(edge[..., None], np.minimum(out[..., :3] * 1.08, 255), out[..., :3])
        return out.round().astype(np.uint8)
    return p


def sill_paint(face, w, h, part, cv):
    """Cement window sill: smooth, dirtier on top, drip groove under the nose, a crack, black run-off."""
    x, y, z = face_coords(part, face, w, h)
    idx = np.full((h, w), 5) + (vnoise(w, h, max(1, w // 4), max(1, h // 4), 8810) > 0.62) - (vnoise(w, h, max(1, w // 6), max(1, h // 3), 8811) < 0.25)
    if face == 'up':
        idx = idx - (z > 3)
    if face == 'down':
        idx = idx - 2
    cv.put(CEMENT, idx + 1)
    if face == 'up':
        cv.tint('#3a3426', np.where(vnoise(w, h, max(1, w // 3), max(1, h // 2), 8812) > 0.5, 0.25, 0.08))
    if face == 'north':
        cv.tint('#1c1e16', np.where(vnoise(w, h, max(1, w // 2), 1, 8813) > 0.55, 0.3, 0))


PERSIANA = Ramp('#1e150e', '#2e2116', '#43301f', '#5a4129', '#6f5134', '#836141', '#97734f', '#a9845e')   # sun-beaten varnish


def persiana_painter(side='ext'):
    """Wooden roller-blind slats (2 units each), weathered grey outside, honey pine inside; tiny light slits at the
    joints (the house light leaks out through them at night). Rows aligned in block space across inf/sup."""
    def p(face, w, h, part):
        x, y, z = face_coords(part, face, w, h)
        v = np.floor((16 - y) * 2).astype(int)
        u = np.floor(x * 2).astype(int)
        r = v % 4
        slat = v // 4
        tone = ((slat * 7) % 5 == 0) * -1 + ((slat * 3) % 7 == 0) * 1
        idx = np.where(r == 0, 5, np.where(r == 3, 1, 3)) + tone
        g = np.where((u * 5 + slat * 3) % 11 == 0, -1, 0) + np.where((u * 3 + slat) % 13 == 0, 1, 0)
        idx = idx + np.where(r < 3, g, 0)
        cv = Cv(w, h)
        cv.put(PERSIANA if (side == 'ext' and face == 'north') else PINO, idx + (0 if face == 'north' else 1))
        if face == 'north':
            cv.tint('#2a2620', np.where(vnoise(w, h, max(1, w // 6), max(1, h // 8), 8820) > 0.62, 0.2, 0))
        slit = (r == 3) & ((u + slat * 5) % 9 == 0)
        cv.a = np.where(slit, 0, cv.a)
        return cv.out()
    return p


def window_wood(seed):
    return pp_paint(CREAM_EN, 5, seed=seed, chip=0.18)


def reja_rings_painter(xw0):
    """Cut-out band of welded rings between the bars (window-space x: xw = local x + xw0)."""
    def p(face, w, h, part):
        x, y, z = face_coords(part, face, w, h)
        xw = x + xw0
        cxr = np.floor(xw / 3.5) * 3.5 + 1.75
        d = np.sqrt((xw - cxr) ** 2 + (y - 7.0) ** 2)
        m = np.abs(d - 1.15) < 0.32
        cv = Cv(w, h)
        idx = np.full((h, w), 3) + (y > 7.0) * 2
        cv.put(REJA_V, idx, m)
        cv.put(RUST, np.full((h, w), 2), m & (vnoise(w, h, max(1, w // 3), max(1, h // 2), 8830) > 0.75))
        return cv.out()
    return p


def window2_parts(piece, side, closed=False):
    """2x2 casement window with reja and roller blind. piece 'inf'/'sup', side 'izq'/'der'."""
    izq = side == 'izq'
    xw0 = 14.0 if izq else -2.0                 # window-space x = local x + xw0 (0..28 between the jambs)
    ox0, ox1 = (0.0, 14.0) if izq else (2.0, 16.0)       # the opening inside this block
    lining = pp_paint(CREAM_EN, 5, seed=8845, chip=0.08, along='y')     # 'marco cajón': painted wood lines the reveal
    wallp = wall_face_painter(lining=lining)
    parts = []
    jx = (14.0, 16.0) if izq else (0.0, 2.0)
    parts.append(P((jx[0], 0, 0), (jx[1], 16, 16), wallp, name='jamb'))
    wood = window_wood(8840 + (piece == 'sup') + 2 * izq)
    it = pp_iron(seed=8850, rust=0.35)
    rej = lambda frm, to, nm: P(frm, to, pp_fn(lambda face, w, h, part, cv: cv.put(REJA_V, np.full((h, w), 3) + (face == 'up') * 2 - (face == 'down') * 2
                                                                                      + (vnoise(w, h, max(1, w // 2), max(1, h // 2), fkey(part, face)) > 0.7))), name=nm)
    fz0, fz1 = WIN_FRAME_Z
    # frame (marco) against the jamb and the leaves
    fr_x = (12.6, 14.0) if izq else (2.0, 3.4)
    ms_x = (0.0, 1.2) if izq else (14.8, 16.0)          # meeting stile at the centre seam
    os_x = (11.4, 12.6) if izq else (3.4, 4.6)          # leaf outer stile
    gx = (1.2, 11.4) if izq else (4.6, 14.8)
    if piece == 'inf':
        y0, y1 = 1.6, 16.0
        parts += [P((ox0 - (0 if izq else 0), 0, -1.6), (ox1 + (1.5 if izq else 0) if izq else ox1, 1.6, 0.0), pp_fn(sill_paint), name='sill_nose'),
                  P((ox0, 0, 0.0), (ox1, 1.6, fz0), pp_fn(sill_paint), name='sill'),
                  P((ox0, 0, fz1), (ox1, 1.2, 16.6), pp_wood(CEDRO, 5, seed=8860, along='x'), name='sill_in'),
                  P((ox0, 1.2, fz0), (ox1, 3.4, fz1), wood, name='rail_b'),
                  P((ms_x[0], 3.4, 6.4), (ms_x[1], 16, 8.1), wood, name='meet'),
                  P((os_x[0], 3.4, 6.4), (os_x[1], 16, 8.1), wood, name='stile'),
                  P((gx[0], 9.6, 7.0), (gx[1], 10.4, 7.6), wood, name='bar')]
        if not izq:   # the der sill nose also covers the left ear
            parts[1] = P((-1.5, 0, -1.6), (16.0, 1.6, 0.0), pp_fn(sill_paint), name='sill_nose')
        else:
            parts[1] = P((0.0, 0, -1.6), (17.5, 1.6, 0.0), pp_fn(sill_paint), name='sill_nose')
        gy = (3.4, 16.0)
    else:
        y0, y1 = 0.0, 11.4
        parts += [P((ox0, 11.4, 0), (ox1, 16, 16), wall_face_painter(lining=lining), name='lintel'),
                  P((ox0, 10.0, fz0), (ox1, 11.4, fz1), wood, name='head'),
                  P((ox0, 8.6, 6.4), (ox1, 10.0, 8.1), wood, name='rail_t'),
                  P((ms_x[0], 0, 6.4), (ms_x[1], 8.6, 8.1), wood, name='meet'),
                  P((os_x[0], 0, 6.4), (os_x[1], 8.6, 8.1), wood, name='stile'),
                  P((gx[0], 1.2, 7.0), (gx[1], 2.0, 7.6), wood, name='bar'),
                  # blind-box cover inside (tapa del cajón de persiana): a painted board with a screwed lid
                  P((ox0, 11.4, 16.0), (ox1, 16.0, 16.4), pp_paint(ENAMEL_W, 5, seed=8870, chip=0.1, along='x'), name='box_cover')]
        gy = (0.0, 8.6)
    parts.append(P((fr_x[0], y0, fz0), (fr_x[1], y1 if piece == 'inf' else 10.0, fz1), wood, name='frame'))
    parts.append(PL((gx[0], gy[0], 7.3), (gx[1], gy[1], 7.3), pp_glass(seed=8880 + (piece == 'sup') + 2 * izq, alpha=88), name='glass'))
    # roller blind: guides on the jamb, slats when closed, the bottom bar peeking out of the box when open
    gdx = (13.2, 14.0) if izq else (2.0, 2.8)
    parts.append(P((gdx[0], y0, 2.0), (gdx[1], y1, 4.4), pp_iron(seed=8890, rust=0.3), name='guide'))
    sx0, sx1 = (0.0, 13.2) if izq else (2.8, 16.0)
    if closed:
        parts.append(P((sx0, y0, 2.6), (sx1, y1, 3.8), persiana_painter(), name='slats'))
    elif piece == 'sup':
        parts.append(P((sx0, 9.2, 2.4), (sx1, 11.4, 4.0), persiana_painter(), name='slat_bar'))
    # reja: frame flat bars, vertical bars every 3.5 (window space), ring band in the upper piece
    rz = (0.3, 1.3)
    parts.append(rej(((13.0, y0, rz[0]) if izq else (2.0, y0, rz[0])), ((14.0, y1, rz[1]) if izq else (3.0, y1, rz[1])), 'reja_side'))
    if piece == 'inf':
        parts.append(rej((ox0, 1.6, rz[0]), (ox1, 2.6, rz[1]), 'reja_bottom'))
    else:
        parts.append(rej((ox0, 10.4, rz[0]), (ox1, 11.4, rz[1]), 'reja_top'))
        parts.append(rej((ox0, 4.6, rz[0]), (ox1, 5.4, rz[1]), 'reja_r1'))
        parts.append(rej((ox0, 8.6, rz[0]), (ox1, 9.4, rz[1]), 'reja_r2'))
        parts.append(PL((ox0, 5.4, 0.8), (ox1, 8.6, 0.8), reja_rings_painter(xw0), name='rings'))
    for k in range(1, 8):
        xw = 3.5 * k
        xl = xw - xw0
        if ox0 - 0.01 <= xl <= ox1 + 0.01 and not (izq and abs(xw - 14.0) < 0.01):
            parts.append(P((xl - 0.45, y0, 0.35), (xl + 0.45, y1, 1.25), it, name='bar_v'))
    # interior casing (contramarco) over the jamb's room face: varnished cedar like the doors, so no latex shows
    cx0, cx1 = (13.4, 16.0) if izq else (0.0, 2.6)
    parts.append(P((cx0, 1.2 if piece == 'inf' else 0.0, 16.0), (cx1, 16.0 if piece == 'inf' else 11.4, 16.6), trim_wood(7125, CEDRO, 4), name='casing'))
    if piece == 'sup':
        parts.append(P((cx0, 11.4, 16.0), (cx1, 16.0, 16.6), trim_wood(7126, CEDRO, 4), name='casing_top'))
    if izq:   # the strap of the roller blind and its winder, on the interior face of the jamb
        if piece == 'inf':
            parts.append(P((14.0, 6.0, 16.6), (15.8, 10.6, 16.95), pp_paint(ENAMEL_W, 5, seed=8895, chip=0.0), name='winder'))
            parts.append(PL((14.7, 10.6, 16.7), (15.1, 16.0, 16.7), pp_fn(strap_paint), name='strap'))
        else:
            parts.append(PL((14.7, 0.0, 16.7), (15.1, 11.4, 16.7), pp_fn(strap_paint), name='strap'))
    return parts


def strap_paint(face, w, h, part, cv):
    x, y, z = face_coords(part, face, w, h)
    cv.put(Ramp('#3a3226', '#5a4e3a', '#7a6c52', '#948668'), np.full((h, w), 2) + (np.floor(y * 2).astype(int) % 3 == 0))


def kitchen_window_parts(side, open_=False):
    """Kitchen window over the counter (2 wide x 1 high, sill at the bottom of the block, lintel on top): a cream
    painted IRON casement with 2x2 small panes per leaf, reja outside, no blind. '_abierta' = this leaf swung open
    into the kitchen (Marta throws the chorizo through it)."""
    izq = side == 'izq'
    xw0 = 14.0 if izq else -2.0
    ox0, ox1 = (0.0, 14.0) if izq else (2.0, 16.0)
    jx = (14.0, 16.0) if izq else (0.0, 2.0)
    wallp = wall_face_painter(inn='pared_cocina')
    ironf = pp_paint(CREAM_EN, 5, seed=8900 + izq, chip=0.25)
    parts = [P((jx[0], 0, 0), (jx[1], 16, 16), wallp, name='jamb'),
             P((0.0 if izq else -1.5, 0, -1.6), (17.5 if izq else 16.0, 1.6, 0.0), pp_fn(sill_paint), name='sill_nose'),
             P((ox0, 0, 0), (ox1, 1.6, 16.0), pp_fn(sill_paint), name='sill'),
             P((ox0, 12.4, 0), (ox1, 16, 16), wall_face_painter(inn='pared_cocina'), name='lintel'),
             P((ox0, 1.6, 6.0), (ox1, 2.4, 7.4), ironf, name='frame_b'),
             P((ox0, 11.6, 6.0), (ox1, 12.4, 7.4), ironf, name='frame_t'),
             P(((13.2, 1.6, 6.0) if izq else (2.0, 1.6, 6.0)), ((14.0, 12.4, 7.4) if izq else (2.8, 12.4, 7.4)), ironf, name='frame_s')]
    # leaf (2x2 panes): x within the opening; hinge at the jamb side
    lx0, lx1 = (0.0, 13.2) if izq else (2.8, 16.0)
    leaf = [((lx0, 2.4), (lx1, 3.0)), ((lx0, 11.0), (lx1, 11.6)), ((lx0, 6.7), (lx1, 7.3))]
    if not open_:
        for (a, b) in leaf:
            parts.append(P((a[0], a[1], 6.3), (b[0], b[1], 7.1), ironf, name='leaf_h'))
        for xs in ((lx0, lx0 + 0.6), (lx1 - 0.6, lx1), ((lx0 + lx1) / 2 - 0.3, (lx0 + lx1) / 2 + 0.3)):
            parts.append(P((xs[0], 3.0, 6.3), (xs[1], 11.0, 7.1), ironf, name='leaf_v'))
        parts.append(PL((lx0, 2.4, 6.7), (lx1, 11.6, 6.7), pp_glass(seed=8910 + izq, alpha=90), name='glass'))
    else:
        hx = lx1 if izq else lx0          # hinge on the jamb side; the leaf points into the kitchen (+z)
        sgn = -1 if izq else 1
        L = lx1 - lx0
        xa, xb = (hx - 0.8, hx) if izq else (hx, hx + 0.8)
        for (a, b) in leaf:
            parts.append(P((xa, a[1], 7.1), (xb, b[1], 7.1 + L), ironf, name='leaf_h'))
        for zs in ((7.1, 7.7), (7.1 + L - 0.6, 7.1 + L), (7.1 + L / 2 - 0.3, 7.1 + L / 2 + 0.3)):
            parts.append(P((xa, 3.0, zs[0]), (xb, 11.0, zs[1]), ironf, name='leaf_v'))
        parts.append(PL(((xa + xb) / 2, 2.4, 7.1), ((xa + xb) / 2, 11.6, 7.1 + L), pp_glass(seed=8912 + izq, alpha=90), name='glass'))
    it = pp_iron(seed=8920, rust=0.35)
    rej = pp_fn(lambda face, w, h, part, cv: cv.put(REJA_V, np.full((h, w), 3) + (face == 'up') * 2 - (face == 'down') * 2))
    parts += [P((ox0, 1.6, 0.3), (ox1, 2.4, 1.3), rej, name='reja_b'), P((ox0, 11.6, 0.3), (ox1, 12.4, 1.3), rej, name='reja_t'),
              P(((13.0, 1.6, 0.3) if izq else (2.0, 1.6, 0.3)), ((14.0, 12.4, 1.3) if izq else (3.0, 12.4, 1.3)), rej, name='reja_s')]
    for k in range(1, 8):
        xw = 3.5 * k
        xl = xw - xw0
        if ox0 - 0.01 <= xl <= ox1 + 0.01 and not (izq and abs(xw - 14.0) < 0.01):
            parts.append(P((xl - 0.45, 1.6, 0.35), (xl + 0.45, 12.4, 1.25), it, name='bar_v'))
    return parts


def bath_window_parts():
    """Small high bathroom window (1 block): frosted tilting sash (banderola) open a crack, three bars outside."""
    wallp = wall_face_painter(inn='pared_bano')
    wood = window_wood(8930)
    parts = [P((0, 0, 0), (3, 16, 16), wallp, name='jamb_r'), P((13, 0, 0), (16, 16, 16), wallp, name='jamb_l'),
             P((3, 0, 0), (13, 4, 16), wallp, name='under'), P((3, 14, 0), (13, 16, 16), wallp, name='lintel'),
             P((2.0, 2.8, -1.4), (14.0, 4.0, 0.0), pp_fn(sill_paint), name='sill_nose'),
             P((3, 4, 6.0), (13, 4.8, 8.5), wood, name='frame_b'), P((3, 13.2, 6.0), (13, 14, 8.5), wood, name='frame_t'),
             P((3, 4.8, 6.0), (3.8, 13.2, 8.5), wood, name='frame_l'), P((12.2, 4.8, 6.0), (13, 13.2, 8.5), wood, name='frame_r')]
    rot = ('x', 22.5, (8.0, 4.8, 7.6))
    sash = [P((3.9, 4.8, 7.0), (12.1, 5.6, 8.2), wood, rot=rot, name='sash_b'), P((3.9, 12.4, 7.0), (12.1, 13.1, 8.2), wood, rot=rot, name='sash_t'),
            P((3.9, 5.6, 7.0), (4.6, 12.4, 8.2), wood, rot=rot, name='sash_l'), P((11.4, 5.6, 7.0), (12.1, 12.4, 8.2), wood, rot=rot, name='sash_r'),
            PL((4.6, 5.6, 7.6), (11.4, 12.4, 7.6), pp_glass(seed=8935, frosted=True), rot=rot, name='glass')]
    parts += sash
    it = pp_iron(seed=8940, rust=0.4)
    for x in (5.5, 8.0, 10.5):
        parts.append(P((x - 0.45, 4.0, 0.4), (x + 0.45, 14.0, 1.3), it, name='bar'))
    parts.append(P((3.0, 8.6, 0.3), (13.0, 9.4, 1.4), it, name='bar_h'))
    return parts


for _side in ('izq', 'der'):
    for _pc, _pes in (('inf', 'abajo'), ('sup', 'arriba')):
        F(f'ventana_{_pc}_{_side}', f'Ventana con reja y persiana ({_pes}, {_side})', f'Window with bars and roller blind ({_pc}, {_side})',
          window2_parts(_pc, _side), render='translucent', sound='glass')
        F(f'ventana_{_pc}_{_side}_cerrada', f'Ventana con persiana bajada ({_pes}, {_side})', f'Window with the blind down ({_pc}, {_side})',
          window2_parts(_pc, _side, closed=True), render='translucent', sound='glass')
    F(f'ventana_cocina_{_side}', f'Ventana de la cocina ({_side})', f'Kitchen window over the counter ({_side})',
      kitchen_window_parts(_side), render='translucent', sound='glass')
    F(f'ventana_cocina_{_side}_abierta', f'Ventana de la cocina abierta ({_side})', f'Kitchen window, leaf open ({_side})',
      kitchen_window_parts(_side, open_=True), render='translucent', sound='glass')
F('ventana_bano', 'Ventanita del baño (banderola)', 'Small bathroom tilt window', bath_window_parts(), render='translucent', sound='glass')


# =============================================================================================== FRONT FENCE & STREET
# Fence line along the sidewalk: casa_murito (low brick wall, 13.5/16 with its cement coping) carries casa_reja in
# the block above (the railing reaches down onto the coping); casa_pilar / casa_pilar_remate are the brick piers
# (corners, both sides of the gates); casa_pilar_luz is the electricity pier with the meter box facing the street.
# The gates are the Door blocks casa_puerta_reja (pedestrian) and casa_porton (car gate leaves, place two or more).
# Wall-mounted pieces (signs, meters, number, bell) sit against the wall behind them (z=16), front = facing.
_IMG = {}


def img_once(name, builder):
    if name not in _IMG:
        _IMG[name] = builder()
    return _IMG[name]


def plate_box(name, builder, x0, x1, y0, y1, z0, z1, back=GALV, back_idx=3):
    """A thin plate whose front (north) face shows a composition image; back and edges are painted sheet metal.
    Transparent image pixels are cut out on every face."""
    def p(face, w, h, part):
        img = img_once(name, builder)
        H_, W_ = img.shape[:2]
        x, y, z = face_coords(part, face, w, h)
        col = np.clip(np.floor((x1 - x) / (x1 - x0) * W_).astype(int), 0, W_ - 1)
        row = np.clip(np.floor((y1 - y) / (y1 - y0) * H_).astype(int), 0, H_ - 1)
        a = img[row, col].astype(float)
        if face == 'north':
            return np.clip(a, 0, 255).round().astype(np.uint8)
        cv = Cv(w, h)
        cv.put(back, np.full((h, w), back_idx) + (vnoise(w, h, max(1, w // 3), max(1, h // 3), fkey(part, face)) > 0.6))
        cv.put(RUST, np.full((h, w), 2), vnoise(w, h, max(1, w // 3), max(1, h // 3), fkey(part, face) + 1) > 0.7)
        cv.a = np.where(a[..., 3] > 0, cv.a, 0)
        return cv.out()
    return P((x0, y0, z0), (x1, y1, z1), p, name=name)


def brick_wall_painter(dirty_foot=True):
    tex = T('ladrillo', 0)
    base = aligned(tex)

    def p(face, w, h, part):
        a = base(face, w, h, part).astype(float)
        x, y, z = face_coords(part, face, w, h)
        if dirty_foot and face not in ('up', 'down'):
            t = np.clip((4.5 - y) / 4.5, 0, 1) * 0.5
            a[..., :3] = a[..., :3] * (1 - t[..., None]) + C('#2a2418') * t[..., None]
            sp = (y < 2.0) & (vnoise(w, h, max(1, w // 2), max(1, h // 2), fkey(part, face)) > 0.55)
            a[..., :3] = np.where(sp[..., None], EARTH[np.full((h, w), 3)], a[..., :3])
        return np.clip(a, 0, 255).round().astype(np.uint8)
    return p


def coping_paint(face, w, h, part, cv):
    x, y, z = face_coords(part, face, w, h)
    k = fkey(part, face)
    idx = np.full((h, w), 5) + (vnoise(w, h, max(1, w // 4), max(1, h // 4), k) > 0.62) - (vnoise(w, h, max(1, w // 6), max(1, h // 3), k + 1) < 0.25)
    if face == 'down':
        idx = idx - 2
    if face in ('north', 'south', 'east', 'west') and h > 2:
        idx = np.where(np.arange(h)[:, None] == 0, idx + 1, idx)
    cv.put(CEMENT, idx)
    cv.put(LICHEN, np.full((h, w), 1) + (vnoise(w, h, max(1, w // 2), max(1, h // 2), k + 2) > 0.8),
           vnoise(w, h, max(1, w // 3), max(1, h // 3), k + 3) > 0.78)
    if face == 'up':
        cv.put(MOSS, np.full((h, w), 2), (vnoise(w, h, max(1, w // 2), max(1, h // 2), k + 4) > 0.8))
        cm = path_mask(wander([(int(w * 0.6), 0), (int(w * 0.55), h // 2), (int(w * 0.62), h - 1)], k, amp=1.0), w, h, wrap=False)
        cv.put(CEMENT, np.full((h, w), 1), cm)


def murito_parts():
    return [P((0, 0, 4), (16, 12, 12), brick_wall_painter(), name='wall'),
            P((0, 12, 3), (16, 13.5, 13), pp_fn(coping_paint), name='coping')]


def pilar_parts(top=False):
    bw = brick_wall_painter()
    if not top:
        return [P((1, 0, 1), (15, 16, 15), bw, name='pier')]
    cp = pp_fn(coping_paint)
    return [P((1, 0, 1), (15, 10, 15), brick_wall_painter(False), name='pier'),
            P((0, 10, 0), (16, 11.8, 16), cp, name='cap'),
            P((1.5, 11.8, 1.5), (14.5, 12.8, 14.5), cp, name='step'),
            P((4, 12.8, 4), (12, 14.0, 12), cp, name='pyr1'),
            P((6, 14.0, 6), (10, 14.8, 10), cp, name='pyr2')]


def reja_parts(sign=None):
    """Railing on top of the low wall: square bars every 8/3 with spear tips, two rails, a band of welded rings,
    the posts reach down onto the coping (y -2.5)."""
    rp = pp_fn(lambda face, w, h, part, cv: (cv.put(REJA_V, np.full((h, w), 3) + (face == 'up') * 2 - (face == 'down') * 2
                                                    + (vnoise(w, h, max(1, w // 2), max(1, h // 2), fkey(part, face)) > 0.7)),
                                             cv.put(RUST, np.full((h, w), 2), vnoise(w, h, max(1, w // 2), max(1, h // 2), fkey(part, face) + 9) > 0.8)))
    parts = [P((0, -2.5, 7.4), (16, -1.5, 8.6), rp, name='rail_b'), P((0, 11.0, 7.4), (16, 12.0, 8.6), rp, name='rail_t'),
             P((0, 7.0, 7.4), (16, 7.8, 8.6), rp, name='rail_m'),
             PL((0, 7.8, 8.0), (16, 11.0, 8.0), reja_band_painter(), name='rings')]
    for k in range(6):
        x = 1.333 + k * 2.667
        parts.append(P((x - 0.5, -1.5, 7.5), (x + 0.5, 14.0, 8.5), rp, name='bar'))
        parts.append(P((x - 0.85, 13.6, 7.65), (x + 0.85, 15.3, 8.35), rp, name='tip', rot=('z', 45, (x, 14.45, 8.0))))
    if sign:   # 32 px wide (stays inside the block, clear of the piers); the nona plate hangs down to the coping
        y0 = -2.3 if 'nona' in sign else 0.5
        parts.append(plate_box('reja_' + sign, SIGNS['reja_' + sign], 0.0, 16.0, y0, y0 + (19.0 if 'nona' in sign else 12.0), 6.4, 6.9))
        parts.append(P((2.0, 10.6, 6.9), (2.6, 11.4, 7.6), pp_iron(seed=7001, rust=0.6), name='wire_l'))
        parts.append(P((13.4, 10.6, 6.9), (14.0, 11.4, 7.6), pp_iron(seed=7002, rust=0.6), name='wire_r'))
    return parts


def reja_band_painter():
    def p(face, w, h, part):
        x, y, z = face_coords(part, face, w, h)
        cxr = np.floor(x / 2.667) * 2.667 + 1.333 + 1.333
        cxr = np.where(cxr > 16, cxr - 2.667, cxr)
        d = np.sqrt((x - (np.floor((x - 1.333) / 2.667) * 2.667 + 2.667)) ** 2 + (y - 9.4) ** 2)
        m = np.abs(d - 1.05) < 0.32
        cv = Cv(w, h)
        cv.put(REJA_V, np.full((h, w), 3) + (y > 9.4) * 2, m)
        return cv.out()
    return p


DOG = ['.#..#........', '.##.##.......', '.#####.......', '#######......', '##o#######...', '###########..',
       '#######...##.', '######.v.v...', '#######......', '.######......', '..#####......']
DOG_S = ['.#..#....', '.##.##...', '.#####...', '##o####..', '#########', '#####.v.v', '######...', '.####....', '..###....']
MARKER = '#1c2440'          # blue-black felt marker (hand-added, not the sign's print)
MARKER_GLYPHS = {           # hand-drawn capitals, 1 px strokes, 5 rows (italicised and jittered when written)
    'Y': ['#...#', '.#.#.', '..#..', '..#..', '.#...'], 'C': ['.###', '#...', '#...', '#...', '.###'],
    'O': ['.##.', '#..#', '#..#', '#..#', '.##.'], 'N': ['#..#', '##.#', '#.##', '#..#', '#..#'],
    'L': ['#...', '#...', '#...', '#...', '.###'], 'A': ['.##.', '#..#', '####', '#..#', '#..#'],
    '!': ['#', '#', '#', '.', '#'], '.': ['.', '.', '.', '.', '#'],
}
MARKER_NARROW = {'O': ['.#.', '#.#', '#.#', '#.#', '.#.'], 'A': ['.#.', '#.#', '###', '#.#', '#.#']}


def marker_line(m, text, x, y, seed, narrow=False, slant=0.3, rise=1.0, jitter=(0, 0, 0, -1, 1)):
    """Felt-marker handwriting into mask m: hand-drawn 1 px capitals, italicised (rows shifted right towards the
    top), every glyph nudged a pixel up or down, the line climbing `rise` px to the right, as people write on a
    sign wired to a fence. Returns the x where the line ends."""
    rng = np.random.default_rng(seed)
    cx = x
    n = max(1, len(text) - 1)
    for k, ch in enumerate(text):
        if ch == ' ':
            cx += 1 if narrow else 2
            continue
        rows = (MARKER_NARROW.get(ch) if narrow else None) or MARKER_GLYPHS[ch]
        dy = int(round(-rise * k / n)) + int(rng.choice(jitter))
        for r, row in enumerate(rows):
            sh = int(round((len(rows) - 1 - r) * slant))
            for c, px in enumerate(row):
                if px == '#':
                    xx, yy = cx + c + sh, y + r + dy
                    if 0 <= yy < m.shape[0] and 0 <= xx < m.shape[1]:
                        m[yy, xx] = True
        cx += len(rows[0]) + 1
    return cx - 1


def dog_sign(nona=False, W_=40, small=False):
    """'CUIDADO CON EL PERRO' tin sign: red band, a snarling dog head, black stencil letters on yellow. The Nona
    variant is taller: under the print somebody added '...Y CON / LA NONA!' in blue-black felt marker, slanted,
    climbing to the right and underlined twice. small=True: the 32 px wide plate wired to the railing."""
    H_ = (38 if small else 40) if nona else 24
    cv = Cv(W_, H_)
    X, Y = cv.X, cv.Y
    YEL = Ramp('#5a4410', '#8a6a18', '#b8901e', '#d8ac28', '#e8c040', '#f0d468')
    cv.put(YEL, np.full((H_, W_), 4) - (vnoise(W_, H_, 6, 6, 7010) > 0.7) + (vnoise(W_, H_, 6, 6, 7011) > 0.75))
    cv.put(Ramp('#5a0c0a', '#8a1612', '#b0201a'), np.full((H_, W_), 1) + (Y == 2), (Y >= 2) & (Y <= 8) & (X >= 2) & (X <= W_ - 3))
    t = tiny_mask('CUIDADO')[1:]
    m = np.zeros((H_, W_), bool)
    stamp(m, t, (W_ - t.shape[1]) // 2, 3)
    cv.col('#f4ece0', m)
    dog, dx = (DOG_S, 2) if small else (DOG, 2)
    for ch, col in (('#v', '#141210'), ('o', '#e8c040'), ('v', '#f4ece0')):
        dm = np.zeros((H_, W_), bool)
        stamp(dm, ascii_mask(dog, ch), dx, 11)
        cv.col(col, dm)
    x0 = 12 if small else 16
    print_m = np.zeros((H_, W_), bool)
    for txt, yy in (('CON EL', 11), ('PERRO', 17)):
        if small:   # tight word gap so 'CON EL' fits beside the dog
            t = np.concatenate([tiny_mask('CON')[1:], np.zeros((5, 2), bool), tiny_mask('EL')[1:]], 1) if txt == 'CON EL' else tiny_mask(txt)[1:]
        else:
            t = tiny_mask(txt)[1:]
        stamp(print_m, t, x0 + (W_ - 2 - x0 - t.shape[1]) // 2, yy)
    cv.col('#141210', print_m)
    mm = np.zeros((H_, W_), bool)
    if nona:
        y1, y2 = (23, 29) if small else (24, 30)
        marker_line(mm, '...Y CON', 3 if small else 5, y1, 7016, narrow=small, jitter=(0, 0, 0, 1))      # never up into the print
        e2 = marker_line(mm, 'LA NONA!', 1 if small else 4, y2, 7017, narrow=small, jitter=(0, 0, 0, -1))  # never down onto the line
        ul = y2 + 6
        sline(mm, (2 if small else 4, ul), (min(W_ - 3, e2), ul - 1))           # underlined (twice on the big one)
        if not small:
            sline(mm, (7, ul + 1), (min(W_ - 4, e2 - 3), ul))
        mm &= (X >= 1) & (X <= W_ - 2) & (Y >= 2) & (Y <= H_ - 2)
        cv.col(MARKER, mm)
    # border, rusty bent corner, two wire holes (rust kept off the letters)
    bd = (X == 0) | (X == W_ - 1) | (Y == 0) | (Y == H_ - 1)
    cv.col('#1a1612', bd)
    edge = (X <= 1) | (X >= W_ - 2) | (Y <= 1) | (Y >= H_ - 2)
    rs = (edge & (vnoise(W_, H_, 8, 8, 7012) > 0.5)) | ((X > W_ - 6) & (Y > H_ - 6) & (vnoise(W_, H_, 10, 10, 7013) > 0.4))
    rs |= (X <= 3) & (Y >= 9) & (vnoise(W_, H_, 10, 10, 7015) > 0.6)
    rs &= ~dilate(print_m | mm, 1, False) & ~bd
    cv.put(RUST, np.full((H_, W_), 2) + (vnoise(W_, H_, 16, 16, 7014) > 0.6), rs)
    cv.a = np.where((X >= W_ - 2) & (Y >= H_ - 2), 0, cv.a)
    for hx_ in (8, W_ - 9):
        cv.col('#0a0806', (X == hx_) & (Y == 1))
    return cv.out()


SIGNS = {'cartel_perro': lambda: dog_sign(False), 'cartel_perro_nona': lambda: dog_sign(True),
         'reja_cartel_perro': lambda: dog_sign(False, 32, small=True), 'reja_cartel_perro_nona': lambda: dog_sign(True, 32, small=True)}


def wall_sign_parts(sign):
    top = 17.0 if 'nona' in sign else 12.5
    return [plate_box(sign, SIGNS[sign], -2.0, 18.0, top - (20.0 if 'nona' in sign else 12.0), top, 15.3, 15.8, back=GALV),
            P((5.0, top - 2.0, 15.8), (6.0, top - 1.0, 16.0), pp_iron(seed=7003), name='screw_l'),
            P((10.0, top - 2.0, 15.8), (11.0, top - 1.0, 16.0), pp_iron(seed=7004), name='screw_r')]


# --- meters
def meter_luz_img():
    """Electricity meter box door: grey steel, a window onto the meter (dial, the spinning disc's slot, numbers),
    'LUZ' stencil, a lead seal on a wire, a rusty hinge, a sticker of a phone number for a locksmith."""
    W_, H_ = 20, 24
    cv = Cv(W_, H_)
    X, Y = cv.X, cv.Y
    G = Ramp('#22262a', '#30353a', '#40464c', '#525960', '#656d74', '#7a838a', '#9099a0')
    cv.put(G, np.full((H_, W_), 4) + (vnoise(W_, H_, 4, 4, 7020) > 0.65) - (vnoise(W_, H_, 6, 6, 7021) < 0.25))
    win = (X >= 4) & (X <= 15) & (Y >= 3) & (Y <= 13)
    cv.put(GLASS, np.full((H_, W_), 3), win)
    face = (X >= 5) & (X <= 14) & (Y >= 4) & (Y <= 12)
    cv.put(ENAMEL, np.full((H_, W_), 3), face)
    cv.col('#1a1a1a', face & (Y == 6) & (X >= 6) & (X <= 13) & (X % 2 == 0))      # the counter digits
    cv.col('#c81818', face & (Y == 6) & (X == 13))
    cv.col('#2a2a2a', face & (Y == 10) & (X >= 6) & (X <= 13))                  # disc slot
    cv.col('#c81818', face & (Y == 10) & (X == 9))                              # the red mark on the disc
    cv.tint('#ffffff', np.where(win & ((X + Y) % 9 == 0), 0.35, 0))
    cv.put(G, np.full((H_, W_), 6), (Y == 2) & (X >= 3) & (X <= 16) | (X == 3) & (Y >= 2) & (Y <= 14))
    cv.put(G, np.full((H_, W_), 1), (Y == 14) & (X >= 3) & (X <= 16) | (X == 16) & (Y >= 2) & (Y <= 14))
    t = tiny_mask('LUZ')[1:]
    m = np.zeros((H_, W_), bool)
    stamp(m, t, (W_ - t.shape[1]) // 2, 16)
    cv.col('#d8d0b0', m)
    cv.put(Ramp('#3a3a3a', '#6a6a6a', '#9a9a9a'), np.full((H_, W_), 2), (X == 17) & (Y >= 18) & (Y <= 19))   # lead seal
    cv.col('#8a8a80', (X == 16) & (Y == 17))
    cv.put(RUST, np.full((H_, W_), 2), (X <= 1) & ((Y == 4) | (Y == 5) | (Y == 18) | (Y == 19)))
    cv.put(RUST, np.full((H_, W_), 1), (vnoise(W_, H_, 6, 6, 7022) > 0.8) | (Y >= H_ - 2) & (vnoise(W_, H_, 10, 4, 7023) > 0.4))
    sticker = (X >= 4) & (X <= 11) & (Y >= 19) & (Y <= 21)
    cv.col('#e8e0c8', sticker)
    cv.col('#2a4a9a', sticker & (Y == 20) & (X % 2 == 1))
    cv.col('#141414', (X == 0) | (X == W_ - 1) | (Y == 0) | (Y == H_ - 1))
    return cv.out()


def meter_gas_img():
    """Gas meter cabinet door: yellow paint gone ochre, a grid of punched vent holes, 'GAS' stencil, padlock eye."""
    W_, H_ = 24, 20
    cv = Cv(W_, H_)
    X, Y = cv.X, cv.Y
    YEL = Ramp('#4a3a10', '#6a5418', '#8a6e20', '#a8882a', '#c09c36', '#d0b048')
    cv.put(YEL, np.full((H_, W_), 4) + (vnoise(W_, H_, 4, 4, 7030) > 0.65) - (vnoise(W_, H_, 6, 6, 7031) < 0.3))
    holes = (X >= 4) & (X <= 19) & (Y >= 3) & (Y <= 9) & (X % 3 == 1) & (Y % 3 == 0)
    cv.col('#0e0c08', holes)
    cv.put(YEL, np.full((H_, W_), 5), np.roll(holes, 1, 0))
    t = tiny_mask('GAS')[1:]
    m = np.zeros((H_, W_), bool)
    stamp(m, t, (W_ - t.shape[1]) // 2, 12)
    cv.col('#1a1610', m)
    cv.put(IRON, np.full((H_, W_), 4), (X == 21) & (Y >= 9) & (Y <= 11))
    cv.put(RUST, np.full((H_, W_), 2) + (vnoise(W_, H_, 8, 8, 7032) > 0.6),
           (vnoise(W_, H_, 6, 6, 7033) > 0.78) | (Y >= H_ - 3) & (vnoise(W_, H_, 10, 4, 7034) > 0.3))
    cv.col('#141414', (X == 0) | (X == W_ - 1) | (Y == 0) | (Y == H_ - 1))
    return cv.out()


_IMGB = {'medidor_luz': meter_luz_img, 'medidor_gas': meter_gas_img}


def meter_box(name, x0, x1, y0, y1, z0, z1):
    body = pp_fn(lambda face, w, h, part, cv: cv.put(Ramp('#22262a', '#30353a', '#40464c', '#525960', '#656d74'),
                                                     np.full((h, w), 3) - (face == 'down') + (face == 'up')))
    return [P((x0, y0, z0 + 0.4), (x1, y1, z1), body, name='body'),
            plate_box(name, _IMGB[name], x0 - 0.2, x1 + 0.2, y0 - 0.2, y1 + 0.2, z0, z0 + 0.4, back=GALV)]


def medidor_luz_parts():
    """Wall-mounted electricity meter box with a conduit going up the wall."""
    return meter_box('medidor_luz', 3, 13, 2, 14, 12.6, 16) + [P((7.2, 14, 13.8), (8.8, 16, 15.4), pp_fn(gutter_paint), name='conduit')]


def medidor_gas_parts():
    """Wall-mounted gas meter cabinet with the yellow supply pipe coming out of the floor."""
    yp = pp_paint(Ramp('#4a3a10', '#6a5418', '#8a6e20', '#a8882a', '#c09c36', '#d0b048'), 4, seed=7035, chip=0.2)
    return meter_box('medidor_gas', 2, 14, 3, 13, 12.0, 16) + [P((10.5, 0, 13.2), (12.0, 3, 14.7), yp, name='pipe'),
                                                                P((10.2, 0, 12.9), (12.3, 0.6, 15.0), yp, name='flange')]


def pilar_luz_parts():
    """Electricity pier ('pilar de luz'): brick pier with the meter box set in its street face and the galvanised
    mast with the cable inlet sticking up above (reaches into the block above)."""
    bw = brick_wall_painter()
    gz = pp_fn(gutter_paint)
    return ([P((1, 0, 1), (15, 16, 15), bw, name='pier')] + meter_box('medidor_luz', 3, 13, 2, 14, 0.4, 1.0)
            + [P((7.0, 16, 7.0), (9.0, 30, 9.0), gz, name='mast'), P((6.4, 29.0, 6.4), (9.6, 30.6, 9.6), gz, name='inlet'),
               P((7.6, 30.6, 5.0), (8.4, 31.2, 9.0), gz, name='hook'), P((6.6, 16, 6.6), (9.4, 16.8, 9.4), gz, name='collar')])


# --- street lamp
def concrete_paint(face, w, h, part, cv):
    """Precast concrete pole: grey with aggregate pits, the mould seam, rust from the rebar ties, grime at the foot."""
    x, y, z = face_coords(part, face, w, h)
    k = fkey(part, face)
    idx = np.full((h, w), 4) + (vnoise(w, h, max(1, w // 3), max(1, h // 6), k) > 0.62) - (vnoise(w, h, max(1, w // 3), max(1, h // 4), k + 1) < 0.28)
    cv.put(CEMENT, idx)
    for (px_, py_) in poisson(k, max(1, w * h // 30), 2.0, w, h, wrap=False):
        cv.put(CEMENT, np.full((h, w), 2), (cv.X == px_) & (cv.Y == py_))
    if face in ('north', 'south', 'east', 'west'):
        cv.put(CEMENT, np.full((h, w), 6), cv.X == w // 2)
        tie = (np.floor(y * 2).astype(int) % 24 == 5)
        cv.tint('#6a3a1a', np.where(tie & (vnoise(w, h, max(1, w // 2), 1, k + 2) > 0.3), 0.4, 0))
        cv.tint('#6a3a1a', np.where((np.floor(y * 2).astype(int) % 24 > 5) & (np.floor(y * 2).astype(int) % 24 < 12) & (cv.X == 1), 0.25, 0))


def poste_parts(foot=False, flyers=False):
    cp = pp_fn(concrete_paint)
    parts = [P((5.5, 0, 6.0), (10.5, 16, 10.0), cp, name='pole_a'), P((6.0, 0, 5.5), (10.0, 16, 10.5), cp, name='pole_b')]
    if foot:
        parts.append(P((4.5, 0, 4.5), (11.5, 1.2, 11.5), pp_fn(coping_paint), name='collar'))
        parts.append(PL((5.49, 1.2, 6.0), (5.49, 5.0, 10.0), pp_fn(pee_stain), name='stain'))
    if flyers:
        parts.append(plate_box('afiche_vidente', flyer_vidente, 4.6, 11.4, 8.5, 15.5, 5.2, 5.5, back=Ramp('#c8c0a8', '#d8d0b8', '#e8e0c8'), back_idx=1))
        parts.append(plate_box('afiche_fletes', flyer_fletes, 5.4, 10.6, 2.0, 8.0, 5.2, 5.45, back=Ramp('#c8c0a8', '#d8d0b8', '#e8e0c8'), back_idx=1))
    return parts


def pee_stain(face, w, h, part, cv):
    x, y, z = face_coords(part, face, w, h)
    t = np.clip((5.0 - y) / 4.0, 0, 1)
    m = (vnoise(w, h, max(1, w // 2), max(1, h // 3), 7040) * t) > 0.25
    cv.col('#2a2a1a', m, a=120)


def flyer_vidente():
    """Photocopied flyer: 'VIDENTE · TAROT · AMARRES' with a crude eye, and tear-off phone tabs (two torn off)."""
    W_, H_ = 14, 14
    cv = Cv(W_, H_)
    X, Y = cv.X, cv.Y
    cv.put(Ramp('#b8b098', '#d0c8b0', '#e4dcc8', '#eee8d8'), np.full((H_, W_), 2) + (vnoise(W_, H_, 4, 4, 7050) > 0.6))
    for txt, yy in (('TAROT', 1),):
        t = tiny_mask(txt)[1:]
        m = np.zeros((H_, W_), bool)
        stamp(m, t, (W_ - t.shape[1]) // 2, yy)
        cv.col('#7a1a5a', m)
    eye = ((X - 6.5) ** 2 / 9.0 + (Y - 8.5) ** 2 / 2.2) <= 1
    cv.col('#1a1a1a', eye & ~(((X - 6.5) ** 2 / 6.0 + (Y - 8.5) ** 2 / 1.0) <= 1))
    cv.col('#1a1a1a', (X >= 6) & (X <= 7) & (Y >= 8) & (Y <= 9))
    tabs = (Y >= 11) & (X % 2 == 0)
    cv.col('#2a2a2a', tabs & (Y == 12))
    cv.a = np.where((Y >= 11) & ((X // 2) % 3 == 1), 0, cv.a)
    return cv.out()


def flyer_fletes():
    W_, H_ = 10, 12
    cv = Cv(W_, H_)
    X, Y = cv.X, cv.Y
    cv.put(Ramp('#a8b0c0', '#c0c8d8', '#d8e0ee'), np.full((H_, W_), 1) + (vnoise(W_, H_, 4, 4, 7051) > 0.6))
    cv.col('#1a2a7a', (Y >= 1) & (Y <= 3) & (X >= 1) & (X <= 8))
    truck = ascii_mask(['.....', '####.', '#####', '.#.#.'])
    m = np.zeros((H_, W_), bool)
    stamp(m, truck, 2, 5)
    cv.col('#1a1a1a', m)
    cv.col('#2a2a2a', (Y == 10) & (X % 2 == 1))
    cv.tint('#6a5a3a', np.where(vnoise(W_, H_, 3, 3, 7052) > 0.6, 0.3, 0))
    return cv.out()


def farol_parts(lit=True):
    """Street lamp head on the concrete pole: pole top, a curved iron arm reaching ~1 block over the street (towards
    'facing'), a cobra-head luminaire with a refractor underneath (sodium orange when lit). The game flickers it by
    swapping casa_farol / casa_farol_apagado."""
    cp = pp_fn(concrete_paint)
    it = pp_iron(seed=7060, rust=0.4)
    shell = pp_fn(lambda face, w, h, part, cv: cv.put(Ramp('#2a2c2e', '#3c4044', '#52575c', '#6a7076', '#868c92'),
                                                      np.full((h, w), 2) + (face == 'up') * 2 - (face == 'down')
                                                      + (vnoise(w, h, max(1, w // 3), max(1, h // 3), fkey(part, face)) > 0.6)))

    def lens(face, w, h, part, cv):
        x, y, z = face_coords(part, face, w, h)
        if lit:
            cv.put(Ramp('#a85a14', '#d8801e', '#f0a83a', '#ffd070', '#fff0b8'), np.full((h, w), 2) + ((cv.X + cv.Y) % 3 == 0) + (np.abs(x - 8) < 1.5) * 2)
        else:
            cv.put(Ramp('#2a2a26', '#3a3a34', '#4e4c44', '#66625a'), np.full((h, w), 1) + ((cv.X + cv.Y) % 3 == 0))
            cv.tint('#1a1408', np.where(vnoise(w, h, max(1, w // 2), max(1, h // 2), 7061) > 0.5, 0.4, 0))
    parts = [P((5.5, 0, 6.0), (10.5, 11, 10.0), cp, name='pole_a'), P((6.0, 0, 5.5), (10.0, 11, 10.5), cp, name='pole_b'),
             P((5.2, 11, 5.2), (10.8, 12.0, 10.8), cp, name='cap'),
             P((7.2, 9.0, 4.0), (8.8, 13.0, 6.0), it, name='clamp'),
             P((7.3, 12.0, 5.6), (8.7, 13.4, 9.0), it, name='arm_root'),
             P((7.35, 11.2, -12.0), (8.65, 12.5, 6.0), it, rot=('x', 22.5, (8.0, 11.85, -3.0)), name='arm'),
             P((5.0, 13.0, -15.8), (11.0, 15.4, -8.6), shell, name='shell'),
             P((5.8, 15.4, -15.0), (10.2, 16.4, -9.6), shell, name='shell_top'),
             P((7.4, 14.4, -8.8), (8.6, 15.4, -7.4), it, name='socket'),
             P((5.6, 12.1, -15.2), (10.4, 13.0, -9.0), pp_fn(lens), shade=not lit, name='lens')]
    return parts


# --- house number, bell, street name
def numero_img():
    """Hand-painted azulejo with the house number 1961 in cobalt (2-3 px clear of the cobalt filete on every side)
    and a sprig of wisteria (glicinas) in the two free corners."""
    W_, H_ = 30, 16
    cv = Cv(W_, H_)
    X, Y = cv.X, cv.Y
    cv.put(Ramp('#9a978a', '#c8c4b4', '#e2ddcc', '#f0ece0'), np.full((H_, W_), 3) - (vnoise(W_, H_, 4, 4, 7070) > 0.75))
    cv.put(Ramp('#1a2a6a', '#2a3e8a'), np.full((H_, W_), 1), (X == 1) | (X == W_ - 2) | (Y == 1) | (Y == H_ - 2))
    t = text_mask('1961')[2:]
    m = np.zeros((H_, W_), bool)
    stamp(m, t, (W_ - t.shape[1]) // 2, 4)
    cv.col('#1e3080', m)
    cv.col('#3a50a8', m & ~nb(m, 0, 1, False) & ~nb(m, 1, 0, False))      # brush loading on the strokes
    for (lx_, ly_, c_) in ((3, 4, '#8a6ab8'), (2, 5, '#6a4a98'), (3, 6, '#8a6ab8'), (2, 7, '#a88ad0'), (3, 8, '#6a4a98'),
                           (2, 9, '#8a6ab8'), (2, 11, '#6a4a98')):     # a wisteria raceme hanging down the left
        cv.col(c_, (X == lx_) & (Y == ly_))
    cv.col('#4a7a3a', (X == 3) & (Y == 2) | (X == 2) & (Y == 3) | (X == 26) & (Y == 13) | (X == 27) & (Y == 12) | (X == 25) & (Y == 13))
    cv.tint('#6a5a3a', np.where((vnoise(W_, H_, 4, 4, 7071) > 0.7) & ~m, 0.2, 0))
    cv.col('#2a2826', (X == 0) | (X == W_ - 1) | (Y == 0) | (Y == H_ - 1))
    cv.a = np.where((X == W_ - 1) & (Y <= 2), 0, cv.a)        # a chipped corner
    return cv.out()


CONDENSED = {   # 4 px wide capitals, 7 rows: the street-name plate
    'P': ['###.', '#..#', '#..#', '###.', '#...', '#...', '#...'], 'J': ['..##', '...#', '...#', '...#', '...#', '#..#', '.##.'],
    'E': ['####', '#...', '#...', '###.', '#...', '#...', '####'], 'L': ['#...', '#...', '#...', '#...', '#...', '#...', '####'],
    'A': ['.##.', '#..#', '#..#', '####', '#..#', '#..#', '#..#'], 'S': ['.###', '#...', '#...', '.##.', '...#', '...#', '###.'],
    'G': ['.##.', '#..#', '#...', '#.##', '#..#', '#..#', '.###'], 'I': ['###', '.#.', '.#.', '.#.', '.#.', '.#.', '###'],
    'C': ['.##.', '#..#', '#...', '#...', '#...', '#..#', '.##.'], 'N': ['#..#', '##.#', '##.#', '#.##', '#.##', '#..#', '#..#'],
    'F': ['####', '#...', '#...', '###.', '#...', '#...', '#...'], 'R': ['###.', '#..#', '#..#', '###.', '#.#.', '#..#', '#..#'],
    ' ': ['..', '..', '..', '..', '..', '..', '..'],
}


def condensed_mask(text):
    cols = []
    for k, ch in enumerate(text):
        cols.append(ascii_mask(CONDENSED[ch]))
        if k < len(text) - 1:
            cols.append(np.zeros((7, 1), bool))
    return np.concatenate(cols, 1)


def enamel_rust(cv, W_, H_, seed, keep_off):
    """Rust bursts on enamel, mostly at the edges and the screw holes, never over the letters."""
    X, Y = cv.X, cv.Y
    edge = np.minimum(np.minimum(X, W_ - 1 - X), np.minimum(Y, H_ - 1 - Y))
    ys, xs = np.nonzero(keep_off & (edge > 1))
    box_ = rect(xs.min() - 2, ys.min() - 1, xs.max() + 2, ys.max() + 1, X, Y) if len(xs) else np.zeros_like(edge, bool)
    rs = ((vnoise(W_, H_, 10, 4, seed) > 0.8) & ~box_) | ((edge <= 2) & (vnoise(W_, H_, 20, 8, seed + 1) > 0.6))
    rs &= ~dilate(keep_off, 1, False)
    cv.put(RUST, np.full((H_, W_), 2) + (vnoise(W_, H_, 20, 8, seed + 2) > 0.6), rs)
    cv.col('#1a1a1a', rs & (vnoise(W_, H_, 20, 8, seed + 3) > 0.72))


def calle_img():
    """Blue enamel street-name plate (80 x 16 px): 'PJE LAS GLICINAS' in condensed white capitals, white filete,
    rust bursts at the edges and the screw holes (kept off the letters)."""
    W_, H_ = 80, 16
    cv = Cv(W_, H_)
    X, Y = cv.X, cv.Y
    cv.put(Ramp('#0e1a3a', '#16285a', '#1e3678', '#2a4690'), np.full((H_, W_), 2) + (vnoise(W_, H_, 8, 4, 7080) > 0.65))
    cv.col('#e8e4d8', (X == 1) | (X == W_ - 2) | (Y == 1) | (Y == H_ - 2))
    t = condensed_mask('PJE LAS GLICINAS')
    m = np.zeros((H_, W_), bool)
    stamp(m, t, (W_ - t.shape[1]) // 2, 4)
    cv.col('#f0ece0', m)
    enamel_rust(cv, W_, H_, 7081, m | (Y == 1) | (Y == H_ - 2) | (X == 1) | (X == W_ - 2))
    for hx_ in (4, W_ - 5):
        cv.col('#0a0a0a', (X == hx_) & (Y == H_ // 2))
    cv.col('#141414', (X == 0) | (X == W_ - 1) | (Y == 0) | (Y == H_ - 1))
    return cv.out()


def calle_num_img():
    """The small numbering strip under the street plate: '1900-2000' (the block the house is on)."""
    W_, H_ = 40, 11
    cv = Cv(W_, H_)
    X, Y = cv.X, cv.Y
    cv.put(Ramp('#0e1a3a', '#16285a', '#1e3678', '#2a4690'), np.full((H_, W_), 2) + (vnoise(W_, H_, 6, 3, 7084) > 0.65))
    cv.col('#d8d4c8', (X == 1) | (X == W_ - 2) | (Y == 1) | (Y == H_ - 2))
    t = tiny_mask('1900-2000')[1:]
    m = np.zeros((H_, W_), bool)
    stamp(m, t, (W_ - t.shape[1]) // 2, 3)
    cv.col('#e0dccf', m)
    enamel_rust(cv, W_, H_, 7085, m | (Y == 1) | (Y == H_ - 2) | (X == 1) | (X == W_ - 2))
    cv.col('#141414', (X == 0) | (X == W_ - 1) | (Y == 0) | (Y == H_ - 1))
    return cv.out()


M5 = ['#...#', '##.##', '#.#.#', '#...#', '#...#']


def timbre_parts():
    """Doorbell plate on the pier (bakelite, 16 wide): the push button in a brass bezel over a name card,
    'MORALES' typed in blue ink, 2 px clear of the card's edges."""
    pl = pp_fn(lambda face, w, h, part, cv: cv.put(Ramp('#3a3226', '#5a4e3c', '#7a6c56', '#9a8c74', '#b8aa90'),
                                                   np.full((h, w), 3) + (face == 'up') - (face == 'down')))

    def card(face, w, h, part, cv):
        cv.put(Ramp('#b8b098', '#d8d0bc', '#ebe5d4'), np.full((h, w), 2) - (vnoise(w, h, max(1, w // 4), 2, 7095) > 0.7))
        if face != 'north':
            return
        X, Y = cv.X, cv.Y
        cols = []
        for k, ch in enumerate('MORALES'):
            g = ascii_mask(M5) if ch == 'M' else tiny_mask(ch)[1:]
            cols += [g, np.zeros((5, 1), bool)]
        t = np.concatenate(cols[:-1], 1)
        m = np.zeros((h, w), bool)
        stamp(m, t, (w - t.shape[1]) // 2, (h - 5) // 2)
        cv.col('#1a2a6a', m)
        cv.tint('#5a4a30', np.where((vnoise(w, h, max(1, w // 3), 2, 7096) > 0.6) & ~m, 0.18, 0))
        cv.tint('#000000', np.where(Y == 0, 0.3, 0))           # the plate's lip shades the top of the card
    btn = pp_fn(lambda face, w, h, part, cv: cv.put(ENAMEL, np.full((h, w), 4) + (face == 'north')))
    return [P((0.0, 7.0, 15.3), (16.0, 15.0, 16.0), pl, name='plate'),
            P((6.6, 12.6, 14.9), (9.4, 14.2, 15.3), pp_fn(lambda face, w, h, part, cv: cv.put(BRASS, np.full((h, w), 4) + (face == 'up'))), name='bezel'),
            P((7.2, 13.0, 14.6), (8.8, 13.8, 14.9), btn, name='button'),
            P((0.5, 7.5, 15.2), (15.5, 12.0, 15.3), pp_fn(card), name='card')]


F('murito', 'Murito de ladrillo', 'Low brick front wall', murito_parts(), sound='stone')
F('pilar', 'Pilar de ladrillo', 'Brick pier', pilar_parts(), sound='stone', collision='full')
F('pilar_remate', 'Remate de pilar', 'Brick pier top with cap', pilar_parts(True), sound='stone')
F('pilar_luz', 'Pilar de luz (con medidor)', 'Electricity pier with meter box', pilar_luz_parts(), sound='stone')
F('reja', 'Reja del frente', 'Front railing (on the low wall)', reja_parts(), sound='metal')
F('reja_cartel_perro', "Reja con cartel 'Cuidado con el perro'", "Railing with 'Beware of the dog' sign", reja_parts('cartel_perro'), sound='metal')
F('reja_cartel_perro_nona', "Reja con cartel '...y con la nona'", "Railing with the dog sign ('...and the nona')", reja_parts('cartel_perro_nona'), sound='metal')
F('cartel_perro', "Cartel 'Cuidado con el perro'", "'Beware of the dog' sign", wall_sign_parts('cartel_perro'), sound='metal', collision='none')
F('cartel_perro_nona', "Cartel 'Cuidado con el perro... y con la nona'", "Dog sign with the marker scribble", wall_sign_parts('cartel_perro_nona'), sound='metal', collision='none')
F('medidor_luz', 'Medidor de luz', 'Electricity meter box', medidor_luz_parts(), sound='metal')
F('medidor_gas', 'Gabinete del medidor de gas', 'Gas meter cabinet', medidor_gas_parts(), sound='metal')
F('poste', 'Columna de hormigón', 'Concrete lamp post', poste_parts(), sound='stone')
F('poste_pie', 'Pie de columna de hormigón', 'Concrete lamp post foot', poste_parts(foot=True), sound='stone')
F('poste_afiches', 'Columna con afiches', 'Concrete post with flyers', poste_parts(flyers=True), sound='stone')
F('farol', 'Farol de la calle (encendido)', 'Street lamp (lit)', farol_parts(True), sound='metal', light=15)
F('farol_apagado', 'Farol de la calle (apagado)', 'Street lamp (off)', farol_parts(False), sound='metal')
F('poste_cartel_calle', "Columna con cartel 'Pje. Las Glicinas'", 'Concrete post with the street-name plate', poste_parts() +
  [plate_box('cartel_calle', calle_img, -12.0, 28.0, 9.5, 17.5, 4.6, 5.0, back=Ramp('#0e1a3a', '#16285a', '#1e3678'), back_idx=1),
   plate_box('cartel_calle_num', calle_num_img, -2.0, 18.0, 3.0, 8.5, 4.6, 5.0, back=Ramp('#0e1a3a', '#16285a', '#1e3678'), back_idx=1),
   P((5.2, 11.0, 5.0), (10.8, 11.8, 11.2), pp_iron(seed=7090), name='strap1'), P((5.2, 15.0, 5.0), (10.8, 15.8, 11.2), pp_iron(seed=7091), name='strap2'),
   P((5.2, 5.4, 5.0), (10.8, 6.2, 11.2), pp_iron(seed=7092), name='strap3')],
  sound='stone')
F('numero_1961', 'Número de la casa (1961)', 'House number tile (1961)', [plate_box('numero', numero_img, 0.5, 15.5, 5.5, 13.5, 15.4, 16.0, back=CEMENT)],
  sound='ceramic', collision='none')
F('timbre', 'Timbre (Morales)', "Doorbell ('Morales')", timbre_parts(), sound='stone', collision='none')


# =============================================================================================== INTERIOR TRIMS & FITTINGS
# Wall pieces: back against the wall behind (z=16), front = facing (towards the room). Inner-corner pieces: place
# them with the same facing as the straight run along the wall BEHIND them; '_esquina_der' when the side wall is on
# your RIGHT as you look at the corner from the room, '_esquina_izq' when it is on your LEFT. (In a rectangular room
# seen from inside: NW corner = _der facing east or _izq facing south, NE = _der south / _izq west, SE = _der west /
# _izq north, SW = _der north / _izq east.)
# Door casings ('contramarco'): _izq goes in front of the wall block on the LEFT of the door's UPPER half (seen from
# the room) and reaches down to the floor (so a carpet or skirting can share the floor-level block), _der likewise
# on the right, _dintel in front of the wall block above the door (its mitred ears reach the side strips).
def zocalo_parts(corner=False):
    tw = trim_wood(7100)
    parts = [P((0, 0, 15.0), (16, 3.2, 16), tw, name='board'), P((0, 3.2, 15.4), (16, 3.8, 16), tw, name='bead')]
    if corner:
        parts += [P((0, 0, 0), (1.0, 3.2, 15.0), tw, name='board_s'), P((0, 3.2, 0), (0.6, 3.8, 15.4), tw, name='bead_s')]
    return parts


def plaster_trim(seed):
    def p(face, w, h, part):
        cv = Cv(w, h)
        idx = np.full((h, w), 6) + (vnoise(w, h, max(1, w // 4), max(1, h // 2), seed + fkey(part, face)) > 0.65) - (face == 'down') * 2
        cv.put(WHITEP, idx)
        cv.tint('#7a6a46', np.where(vnoise(w, h, max(1, w // 3), max(1, h // 2), seed + 3) > 0.55, 0.14, 0.05))
        return cv.out()
    return p


def cornisa_parts(corner=False):
    pt = plaster_trim(7110)
    parts = [P((0, 14.4, 12.6), (16, 16, 16), pt, name='c0'), P((0, 12.8, 14.6), (16, 14.4, 16), pt, name='c1'),
             P((0, 12.2, 15.4), (16, 12.8, 16), pt, name='bead'), P((0, 15.2, 11.6), (16, 16, 12.6), pt, name='lip')]
    if corner:
        parts += [P((0, 14.4, 0), (3.4, 16, 12.6), pt, name='c0s'), P((0, 12.8, 0), (1.4, 14.4, 14.6), pt, name='c1s'),
                  P((0, 12.2, 0), (0.6, 12.8, 15.4), pt, name='beads'), P((3.4, 15.2, 0), (4.4, 16, 11.6), pt, name='lips')]
    return parts


def roseton_parts():
    """Plaster ceiling rose: three stepped rings with a ring of leaves, the cable hole in the boss."""
    def rose(face, w, h, part):
        x, y, z = face_coords(part, face, w, h)
        cv = Cv(w, h)
        r = np.sqrt((x - 8) ** 2 + (z - 8) ** 2)
        ang = np.arctan2(z - 8, x - 8)
        idx = np.full((h, w), 6)
        if face == 'down':
            leaf = (np.cos(ang * 12) > 0.2) & (r > 3.8) & (r < 6.4)
            idx = np.where(leaf, 7, 5) - (np.abs(r - 6.6) < 0.4) * 2 - (np.abs(r - 3.6) < 0.4) * 2
            idx = np.where(r < 0.9, 1, idx)
        cv.put(WHITEP, idx)
        cv.tint('#6a5a3a', np.where(r < 2.5, 0.2, 0.06))
        return cv.out()
    pr = pp_fn(lambda face, w, h, part, cv: cv.put(WHITEP, np.full((h, w), 5)))
    parts = []
    for (r_, y0) in ((7.0, 15.4), (4.2, 14.8), (1.8, 14.0)):
        parts.append(P((8 - r_, y0, 8 - r_ * 0.42), (8 + r_, 16 if y0 == 15.4 else (15.4 if y0 == 14.8 else 14.8), 8 + r_ * 0.42), rose, name='ring_a'))
        parts.append(P((8 - r_ * 0.42, y0, 8 - r_), (8 + r_ * 0.42, 16 if y0 == 15.4 else (15.4 if y0 == 14.8 else 14.8), 8 + r_), rose, name='ring_b'))
        parts.append(P((8 - r_ * 0.78, y0 - 0.01, 8 - r_ * 0.78), (8 + r_ * 0.78, (16 if y0 == 15.4 else (15.4 if y0 == 14.8 else 14.8)) - 0.01, 8 + r_ * 0.78), rose, name='ring_c'))
    return parts


def contramarco_parts(kind):
    tw = trim_wood(7120, CEDRO, 4)
    if kind == 'izq':
        return [P((0, -12.0, 15.0), (1.6, 16, 16), tw, name='strip'), P((1.6, -16.0, 15.5), (2.0, 16, 16), tw, name='step'),
                P((0, -16.0, 14.6), (2.0, -12.0, 16), tw, name='plinth')]
    if kind == 'der':
        return [P((14.4, -12.0, 15.0), (16, 16, 16), tw, name='strip'), P((14.0, -16.0, 15.5), (14.4, 16, 16), tw, name='step'),
                P((14.0, -16.0, 14.6), (16, -12.0, 16), tw, name='plinth')]
    return [P((-1.6, 0, 15.0), (17.6, 1.6, 16), tw, name='head'), P((-1.6, 1.6, 15.2), (17.6, 2.0, 16), tw, name='cap'),
            P((0, -0.01, 15.5), (16, 0.4, 16), tw, name='step')]


def switch_parts(kind):
    """'llave' = bakelite light switch (two toggles, the plate greyed by fingers); 'enchufe' = outlet with the
    three flat V pins of the Argentine plug; 'rejilla' = louvred ventilation grille (gas safety vent)."""
    bak = Ramp('#3a3226', '#5c5040', '#7e705a', '#a09078', '#bfb096', '#d4c6aa')
    if kind == 'llave':
        def plate(face, w, h, part, cv):
            cv.put(bak, np.full((h, w), 4) + (face == 'up') - (face == 'down'))
            if face == 'north':
                X, Y = cv.X, cv.Y
                for tx in (w // 3, 2 * w // 3):
                    cv.put(bak, np.full((h, w), 1), (X == tx) & (Y >= h // 2 - 2) & (Y <= h // 2 + 1))
                    cv.put(bak, np.full((h, w), 5), (X == tx) & (Y == h // 2 - 2))
                cv.tint('#2a2014', np.clip(1 - np.sqrt((X - w / 2) ** 2 + (Y - h / 2) ** 2) / (w * 0.6), 0, 1) * 0.35)
        return [P((5.8, 3.0, 15.4), (10.2, 9.0, 16), pp_fn(plate), name='plate')]
    if kind == 'enchufe':
        def plate(face, w, h, part, cv):
            cv.put(bak, np.full((h, w), 4) + (face == 'up') - (face == 'down'))
            if face == 'north':
                X, Y = cv.X, cv.Y
                cv.col('#1a1610', ((X == w // 2 - 2) & (Y == h // 2 - 1)) | ((X == w // 2 - 1) & (Y == h // 2)))
                cv.col('#1a1610', ((X == w // 2 + 2) & (Y == h // 2 - 1)) | ((X == w // 2 + 1) & (Y == h // 2)))
                cv.col('#1a1610', (X == w // 2) & (Y >= h // 2 + 2) & (Y <= h // 2 + 3))
                cv.tint('#1a1410', np.where(Y < 2, 0.3, 0))      # scorch over the outlet
        return [P((5.8, 3.0, 15.4), (10.2, 8.4, 16), pp_fn(plate), name='plate')]

    def grille(face, w, h, part, cv):
        x, y, z = face_coords(part, face, w, h)
        cv.put(Ramp('#3a3c3e', '#5a5d60', '#7c8084', '#a0a4a8', '#bfc2c4'), np.full((h, w), 3) + (face == 'up') - (face == 'down'))
        if face == 'north':
            X, Y = cv.X, cv.Y
            sl = (Y % 3 == 1) & (X > 1) & (X < w - 2) & (Y > 1) & (Y < h - 2)
            cv.col('#0c0c0c', sl)
            cv.put(Ramp('#3a3c3e', '#5a5d60', '#7c8084', '#a0a4a8', '#bfc2c4'), np.full((h, w), 4), np.roll(sl, -1, 0) & ~sl & (Y > 1))
            cv.tint('#1a1410', np.where(vnoise(w, h, max(1, w // 3), max(1, h // 3), 7130) > 0.55, 0.3, 0))
    return [P((3.5, 4.0, 15.3), (12.5, 13.0, 16), pp_fn(grille), name='grille'),
            PL((5.0, 0.5, 15.99), (11.0, 4.0, 15.99), pp_fn(lambda face, w, h, part, cv: cv.col('#3a2a1a', vnoise(w, h, max(1, w // 2), max(1, h // 2), 7131) * (face_coords(part, face, w, h)[1] / 4.0) > 0.3, a=110)), name='streak')]


@painter('piso_bano')
def p_piso_bano(v):
    """Bathroom floor: white octagon tiles with little black square 'tacos' at the corners (the classic 1950s
    pattern), 4 octagons per block side. VAR variants: v0-6 clean, v7 dirty grout + rust ring from a can, v8 a
    cracked octagon, v9 a missing taco and a chipped edge."""
    cv = Cv()
    v0, v = v, {7: 1, 8: 2, 9: 3}.get(v, 0)
    X, Y = cv.X, cv.Y
    lx, ly = X % 8, Y % 8
    cut = np.minimum(lx, 7 - lx) + np.minimum(ly, 7 - ly)
    taco = cut <= 1
    joint = (lx == 0) | (ly == 0)
    oct_ = ~taco & ~joint
    idx = np.full((N, N), 6) + (vnoise(N, N, 4, 4, 8950 + v0) > 0.7) - (vnoise(N, N, 8, 8, 8951) < 0.2)
    idx = np.where(oct_ & ((lx == 1) | (ly == 1)) & (cut > 2), idx + 1, idx)
    idx = np.where(oct_ & ((lx == 7) | (ly == 7)), idx - 1, idx)
    cv.put(WHITEP, idx, oct_)
    cv.put(Ramp('#0a0a0c', '#16161a', '#24242a', '#34343c'), np.full((N, N), 2) + ((lx + ly) % 7 == 2), taco & ~joint)
    cv.put(GROUT_L, np.full((N, N), 4) - (v == 1) * 2, joint)
    if v == 1:
        d = np.sqrt((X - 20.5) ** 2 + (Y - 12.5) ** 2)
        cv.tint('#6a3a1a', np.where(np.abs(d - 4.5) < 0.8, 0.45, 0))
    if v == 2:
        cm = path_mask(wander([(9, 9), (12, 12), (14, 14)], 8952, amp=0.7), wrap=False) & oct_
        cv.col('#2a2826', cm)
    if v == 3:
        cv.put(CEMENT, np.full((N, N), 3), taco & (X >= 15) & (X <= 17) & (Y >= 15) & (Y <= 17))
        cv.put(CEMENT, np.full((N, N), 4), oct_ & (X >= 24) & (X <= 26) & (Y >= 1) & (Y <= 2))
    return cv.out()


@painter('madera_escalera')
def p_madera_escalera(v):
    """Pinotea stair/landing boards: narrow dense boards along x (4 px with a fine joint), long resin-streaked grain,
    rare staggered board ends, varnish worn pale where the feet go (the middle)."""
    cv = Cv()
    X, Y = cv.X, cv.Y
    lab = Y // 4
    g = wood_grain(N, N, 8960 + v, 'x', warp=1.0, pores=0.02, tones=(-1, 0, 0, 1, 1))
    rc = np.random.default_rng(8961)
    tone = rc.choice([-1, 0, 0, 1], 8)
    idx = 5.0 + tone[lab] * 0.6 + g * 0.8
    joint = (Y % 4 == 3)
    idx = np.where(joint, 2.6, idx)
    idx = np.where(Y % 4 == 0, idx + 0.6, idx)
    ends = (X == (5 + lab * 13) % 32) & ~joint & ((lab % 3) == 0)
    idx = np.where(ends, 2.4, idx)
    cv.put(CEDRO, idx)
    worn = (np.abs(X - 16) < 9) & (vnoise(N, N, 4, 2, 8962 + v) > 0.35)
    cv.tint('#a08a68', np.where(worn & ~joint, 0.2, 0))
    return cv.out()


def step_parts(material='madera'):
    """A furniture stair block (two 8/16 steps), front = facing = the LOW side; you walk up away from 'facing'.
    Wood: pinotea treads with a rounded nosing overhang and cream painted risers scuffed by shoes. Cement: the
    basement steps, edges worn round, damp at the foot."""
    if material == 'madera':
        tread = pp_fn(lambda face, w, h, part, cv: cv.put(CEDRO, (np.full((h, w), 5) + wood_grain(w, h, 8970 + fkey(part, face), 'x', period=False)
                                                                  - (face == 'down') * 2 + ((face == 'north') & (np.arange(h)[:, None] == 0)) * 2)) or
                      (face == 'up' and cv.tint('#a08a68', np.where(np.abs(face_coords(part, face, w, h)[0] - 8) < 4.5, 0.22, 0))))

        def riser(face, w, h, part, cv):
            cv.put(CREAM_EN, np.full((h, w), 5.0) + (vnoise(w, h, max(1, w // 4), max(1, h // 2), 8971) > 0.7) * 0.4)
            if face == 'north':
                X, Y = cv.X, cv.Y
                cv.tint('#000000', np.where(Y == 0, 0.45, np.where(Y == 1, 0.2, 0)))
                rng = np.random.default_rng(8972 + fkey(part, face))
                for k in range(6):
                    x_, y_ = int(rng.integers(2, max(3, w - 4))), int(rng.integers(h // 2, max(h // 2 + 1, h - 1)))
                    cv.tint('#2a2420', np.where((Y == y_) & (X >= x_) & (X < x_ + 3), 0.4, 0))
            else:
                cv.put(CEDRO, np.full((h, w), 3) + wood_grain(w, h, 8973, 'x', period=False))
        rp = pp_fn(riser)
        return [P((0, 0, 0.4), (16, 7, 16), rp, name='riser_lo'), P((0, 7, -0.8), (16, 8, 16), tread, name='tread_lo'),
                P((0, 8, 8.4), (16, 15, 16), rp, name='riser_hi'), P((0, 15, 7.2), (16, 16, 16), tread, name='tread_hi')]

    floor_tex = aligned(T('cemento_piso', 3))

    def cem(face, w, h, part, cv):
        """Cast cement steps: the treads are the basement floor finish (sampled in block space) worn pale and smooth
        in the middle with dirt in the back corner; risers show the formwork boards (seams every 4 units, a tone per
        board), a chipped nosing, damp darkening at the foot."""
        x, y, z = face_coords(part, face, w, h)
        X, Y = cv.X, cv.Y
        if face == 'up':
            a = floor_tex(face, w, h, part)
            cv.rgb = a[..., :3].astype(float)
            cv.a = np.full((h, w), 255.0)
            cv.tint('#b8b2a6', np.clip(1 - np.abs(x - 8) / 5.5, 0, 1) ** 1.5 * 0.16)   # walked smooth and pale
            back = z > part.to[2] - 2.0
            cv.tint('#2a261e', np.where(back & (vnoise(w, h, max(1, w // 3), 2, 8983) > 0.4), 0.3, 0))
            nose = z < part.frm[2] + 0.6
            cv.tint('#cfc9bd', np.where(nose, 0.22, 0))
            return
        board = np.floor(y / 4.0).astype(int)
        tone = np.array([0.0, 0.3, -0.25, 0.15, -0.1])[board % 5]
        idx = 4.0 + tone + (_hash01(X, Y, 8984 + fkey(part, face)) > 0.97) * 0.6 - (_hash01(X, Y, 8985 + fkey(part, face)) > 0.975) * 0.6
        seam = (np.abs(y - np.round(y / 4.0) * 4.0) < 0.26) & (y > part.frm[1] + 0.3) & (y < part.to[1] - 0.3)
        idx = idx - seam * 0.8 + np.roll(seam, 1, 0) * 0.35
        cv.put(CEMENT, idx)
        if face == 'north':
            top = Y == 0
            cv.put(CEMENT, np.full((h, w), 6.0) - (vnoise(w, h, max(1, w // 2), 1, 8982) > 0.6) * 2.5, top)
            cv.tint('#1e2218', np.clip((part.frm[1] + 3.0 - y) * 0.12, 0, 0.35))


    cp = pp_fn(cem)
    return [P((0, 0, 0), (16, 8, 16), cp, name='step_lo'), P((0, 8, 8), (16, 16, 16), cp, name='step_hi')]


def baranda_iron():
    return pp_fn(lambda face, w, h, part, cv: (cv.put(IRON, np.full((h, w), 3) + (face == 'up') * 2 - (face == 'down') + (cv.X == 0) * 1),
                                               cv.put(RUST, np.full((h, w), 2), vnoise(w, h, max(1, w // 2), max(1, h // 2), fkey(part, face)) > 0.82)))


def baranda_parts(kind='recta', side='izq'):
    """Simple 1950s balustrade: square black iron balusters, a flat bar at the foot, a cedar handrail. 'recta' for a
    landing/upper-hall edge; 'escalera' goes in the block ABOVE a stair block (balusters reach down onto both
    treads; side izq = on the viewer's left when looking up the stair from the bottom, x 14; der = x 2);
    'poste' = the newel post."""
    it = baranda_iron()
    rail = trim_wood(7140, CEDRO, 5)
    if kind == 'recta':
        parts = [P((0, 0, 7.4), (16, 0.8, 8.6), it, name='foot'), P((0, 14.2, 6.6), (16, 15.6, 9.4), rail, name='rail'),
                 P((0, 13.6, 7.3), (16, 14.2, 8.7), it, name='rail_bar')]
        for x in (2, 6, 10, 14):
            parts.append(P((x - 0.5, 0.8, 7.5), (x + 0.5, 13.6, 8.5), it, name='baluster'))
        return parts
    if kind == 'poste':
        return [P((5, 0, 5), (11, 15, 11), trim_wood(7141, CEDRO, 4), name='post'), P((4.4, 15, 4.4), (11.6, 16.4, 11.6), rail, name='cap'),
                P((6, 16.4, 6), (10, 17.4, 10), rail, name='knob')]
    x = 14.0 if side == 'izq' else 2.0
    parts = []
    for z, tread in ((2.5, -8.0), (6.0, -8.0), (10.5, 0.0), (14.0, 0.0)):
        top = z + 4.2
        parts.append(P((x - 0.5, tread, z - 0.5), (x + 0.5, top, z + 0.5), it, name='baluster'))
    L = 16 * R2 + 1.0
    parts.append(P((x - 1.4, 5.0 + 8 - 0.7, 8 - L / 2), (x + 1.4, 5.0 + 8 + 0.7, 8 + L / 2), rail, rot=('x', -45, (x, 13.0, 8.0)), name='rail'))
    parts.append(P((x - 0.7, 5.0 + 8 - 1.3, 8 - L / 2), (x + 0.7, 5.0 + 8 - 0.7, 8 + L / 2), it, rot=('x', -45, (x, 13.0, 8.0)), name='rail_bar'))
    return parts


def pasamanos_parts(side):
    """Galvanised pipe handrail fixed to the side wall of the basement stair on iron brackets. Placed in the block
    ABOVE a stair block, rising away from 'facing'. izq: the wall is on the viewer's left (x=16), der: right (x=0)."""
    gz = pp_fn(gutter_paint)
    xw = 16.0 if side == 'izq' else 0.0
    xr = 13.2 if side == 'izq' else 2.8
    L = 16 * R2 + 0.5
    parts = [P((xr - 0.8, 12.2, 8 - L / 2), (xr + 0.8, 13.8, 8 + L / 2), gz, rot=('x', -45, (xr, 13.0, 8.0)), name='pipe')]
    bx0, bx1 = (xr, xw) if side == 'izq' else (xw, xr)
    for zc in (3.0, 13.0):
        yc = 13.0 + (zc - 8.0) - 1.2
        parts.append(P((bx0, yc - 0.4, zc - 0.4), (bx1, yc + 0.4, zc + 0.4), pp_iron(seed=7150, rust=0.5), name='bracket'))
    return parts


# --- carpet runner for the upstairs hall
RUN_RED = Ramp('#1e0606', '#2e0a0a', '#420f0e', '#561613', '#6a1e18', '#7e281e', '#923426')
RUN_NAVY = Ramp('#0a0e1a', '#121a2c', '#1a263e', '#243450')
RUN_CREAM = Ramp('#6a5e46', '#8a7c5e', '#a89a78', '#c2b490', '#d6c9a6')
RUN_OCHRE = Ramp('#4a3010', '#6a4618', '#8a5e22', '#a8782e')


def runner_img(width_units=13.0, xw0=0.0, total=13.0, stain=False):
    """The runner pattern as a function painter: window-space x (0..total units across the runner), z along."""
    def p(face, w, h, part):
        x, y, z = face_coords(part, face, w, h)
        cv = Cv(w, h)
        if face != 'up':
            cv.put(RUN_RED, np.full((h, w), 1))
            if face in ('north', 'south'):
                cv.put(RUN_CREAM, np.full((h, w), 1), np.zeros((h, w), bool))
            return cv.out()
        xw = x + xw0
        d_edge = np.minimum(xw, total - xw)
        zz = z % 16
        idx = np.full((h, w), 4) + (vnoise(w, h, max(1, w // 4), max(1, h // 4), 7160) > 0.65)
        cv.put(RUN_RED, idx)
        border = d_edge < 2.2
        cv.put(RUN_NAVY, np.full((h, w), 2) + ((np.floor(z * 2).astype(int) % 4) == 0), border)
        cv.put(RUN_CREAM, np.full((h, w), 3), (np.abs(d_edge - 0.6) < 0.35) | (np.abs(d_edge - 2.4) < 0.3))
        # zigzag in the border band
        zig = border & (np.abs(d_edge - (1.0 + 0.6 * np.abs(((z * 2) % 4) - 2) / 2)) < 0.3)
        cv.put(RUN_OCHRE, np.full((h, w), 3), zig)
        # central medallion each block: a stepped diamond in ochre/navy with a cream heart
        cx = total / 2
        dd = np.abs(xw - cx) / 4.6 + np.abs(zz - 8) / 6.0
        cv.put(RUN_OCHRE, np.full((h, w), 2), (dd <= 1.0) & (dd > 0.78))
        cv.put(RUN_NAVY, np.full((h, w), 3), (dd <= 0.78) & (dd > 0.5))
        cv.put(RUN_CREAM, np.full((h, w), 2), (dd <= 0.5) & (dd > 0.3))
        cv.put(RUN_RED, np.full((h, w), 6), dd <= 0.3)
        # little crosses between medallions
        cr = ((np.abs(xw - cx) < 0.35) & (np.abs(zz) < 1.3)) | ((np.abs(zz) < 0.35) & (np.abs(xw - cx) < 1.3))
        cv.put(RUN_CREAM, np.full((h, w), 2), cr & ~border)
        # pile texture + the walking path worn flat and grey in the middle
        cv.mul(np.where((cv.X + cv.Y * 2) % 5 == 0, 0.9, 1.0))
        worn = (np.abs(xw - cx) < total * 0.22) & (vnoise(w, h, max(1, w // 6), max(1, h // 4), 7161) > 0.35)
        cv.tint('#6a5a50', np.where(worn, 0.2, 0))
        if stain:   # something dark soaked into the pile and dried: red-brown, soft edge, a darker tide ring
            nn = vnoise(w, h, max(1, w // 3), max(1, h // 3), 7170)
            d = np.sqrt((xw - total * 0.55) ** 2 / 16.0 + (z - 7.5) ** 2 / 10.0) + (nn - 0.5) * 0.7
            t = np.clip((1.0 - d) / 0.45, 0, 1)
            cv.tint('#2e0c08', 0.62 * t ** 0.8)
            cv.tint('#1e0604', np.where((np.abs(d - 0.97) < 0.07) & (nn > 0.3), 0.35, 0))
            cv.tint('#4a1a10', np.where((d < 0.45) & (nn > 0.6), 0.15, 0))
        return cv.out()
    return p


def fringe_paint(face, w, h, part, cv):
    x, y, z = face_coords(part, face, w, h)
    cv.put(RUN_CREAM, np.full((h, w), 3) - (np.floor(x * 2).astype(int) % 2))
    cv.a = np.where((np.floor(x * 2).astype(int) % 2 == 1) & (face == 'up'), 0, cv.a)


def alfombra_parts(kind='1', end=False, stain=False):
    """Runner pieces, long axis along z (lay them along the corridor). kind '1' = one block wide (x 1.5..14.5);
    'izq'/'der' = the two halves of a runner covering a 2-wide corridor (x 4..28 of the pair; izq = viewer's left
    looking along 'facing'... i.e. authoring +x half). '_punta' pieces end with the fringe at the FRONT (z=0)."""
    if kind == '1':
        x0, x1, xw0, total = 1.5, 14.5, -1.5, 13.0
    elif kind == 'der':
        x0, x1, xw0, total = 4.0, 16.0, -4.0, 24.0
    else:
        x0, x1, xw0, total = 0.0, 12.0, 12.0, 24.0
    z0 = 2.0 if end else 0.0
    parts = [P((x0, 0, z0), (x1, 0.5, 16), runner_img(total=total, xw0=xw0, stain=stain), name='runner')]
    if end:
        parts.append(P((x0 + (0.4 if kind != 'izq' else 0), 0, 0.2), (x1 - (0.4 if kind != 'der' else 0), 0.25, 2.0), pp_fn(fringe_paint), name='fringe'))
    return parts


def maletero_parts():
    """Top cupboard over the placard (the wardrobe is 3 blocks tall: door + this). Place with the SAME facing as the
    placard door below: like the door, its doors sit at z 13..16 and face +z (the room the door was placed from)."""
    gv = trim_wood(7180, PINO, 5)

    def lou(face, w, h, part, cv):
        x, y, z = face_coords(part, face, w, h)
        cv.put(PINO, np.full((h, w), 5) + wood_grain(w, h, 7181, 'x', period=False) * 0)
        if face == 'south':
            v = np.floor((16 - y) * 2).astype(int) % 3
            xi = np.floor(x * 2).astype(int)
            inner = (xi % 16 > 2) & (xi % 16 < 13) & (y > 2.5) & (y < 14)
            cv.put(PINO, np.where(v == 0, 7, np.where(v == 1, 5, 2)), inner)
            cv.put(PINO, np.full((h, w), 3), (xi % 16 == 15) | (xi % 16 == 0))
            cv.put(BRASS, np.full((h, w), 5), ((xi == 13) | (xi == 18)) & (np.abs(y - 4) < 0.6))
    return [P((0, 0, 13), (16, 16, 16), pp_fn(lou), name='doors'), P((0, 15, 12.6), (16, 16, 16), gv, name='top')]


F('zocalo', 'Zócalo de madera', 'Wooden skirting board', zocalo_parts(), collision='none')
F('zocalo_esquina_der', 'Zócalo de madera (rincón, pared a la derecha)', 'Wooden skirting (inner corner, wall on the right)', zocalo_parts(True), collision='none')
F('zocalo_esquina_izq', 'Zócalo de madera (rincón, pared a la izquierda)', 'Wooden skirting (inner corner, wall on the left)', mirror_x(zocalo_parts(True)),
  collision='none')
F('cornisa', 'Cornisa de yeso', 'Plaster cornice', cornisa_parts(), collision='none', sound='plaster')
F('cornisa_esquina_der', 'Cornisa de yeso (rincón, pared a la derecha)', 'Plaster cornice (inner corner, wall on the right)', cornisa_parts(True),
  collision='none', sound='plaster')
F('cornisa_esquina_izq', 'Cornisa de yeso (rincón, pared a la izquierda)', 'Plaster cornice (inner corner, wall on the left)', mirror_x(cornisa_parts(True)),
  collision='none', sound='plaster')
F('roseton', 'Rosetón de yeso del techo', 'Plaster ceiling rose', roseton_parts(), directional=False, collision='none', sound='plaster')
for _k in ('izq', 'der', 'dintel'):
    F(f'contramarco_{_k}', f'Contramarco de puerta ({_k})', f'Door casing ({_k})', contramarco_parts(_k), collision='none')
F('llave_luz', 'Llave de luz de baquelita', 'Bakelite light switch', switch_parts('llave'), collision='none', sound='stone')
F('enchufe', 'Tomacorriente', 'Wall outlet', switch_parts('enchufe'), collision='none', sound='stone')
F('rejilla', 'Rejilla de ventilación', 'Ventilation grille', switch_parts('rejilla'), collision='none', sound='metal')
F('escalon_madera', 'Escalón de madera', 'Wooden stair step (furniture)', step_parts('madera'))
F('escalon_cemento', 'Escalón de cemento (sótano)', 'Cement basement step', step_parts('cemento'), sound='stone')
F('baranda', 'Baranda', 'Balustrade', baranda_parts('recta'), sound='metal')
F('baranda_poste', 'Poste de baranda', 'Newel post', baranda_parts('poste'))
F('baranda_escalera_izq', 'Baranda de escalera (izquierda)', 'Stair balustrade (left)', baranda_parts('escalera', 'izq'), sound='metal', collision='none')
F('baranda_escalera_der', 'Baranda de escalera (derecha)', 'Stair balustrade (right)', baranda_parts('escalera', 'der'), sound='metal', collision='none')
F('pasamanos_izq', 'Pasamanos de caño (pared a la izquierda)', 'Pipe handrail (wall on the left)', pasamanos_parts('izq'), sound='metal', collision='none')
F('pasamanos_der', 'Pasamanos de caño (pared a la derecha)', 'Pipe handrail (wall on the right)', pasamanos_parts('der'), sound='metal', collision='none')
for _k, _es in (('1', ''), ('izq', ' (mitad izquierda)'), ('der', ' (mitad derecha)')):
    _sfx = '' if _k == '1' else '_' + _k
    F(f'alfombra{_sfx}', f'Alfombra de pasillo{_es}', f'Hall runner{_es}', alfombra_parts(_k), collision='none', sound='cloth')
    F(f'alfombra_punta{_sfx}', f'Alfombra de pasillo, punta con flecos{_es}', f'Hall runner end with fringe{_es}', alfombra_parts(_k, end=True), collision='none', sound='cloth')
F('alfombra_mancha', 'Alfombra de pasillo con mancha', 'Hall runner with a stain', alfombra_parts('1', stain=True), collision='none', sound='cloth')
F('placard_maletero', 'Maletero del placard', 'Wardrobe top cupboard', maletero_parts())
PISO_BANO = cube('piso_bano', 'Piso del baño (octógonos)', 'Bathroom octagon floor tiles', 'piso_bano', VAR, sound='tile', down='cielorraso')
MADERA_ESC = cube('madera_escalera', 'Madera de pinotea (escalera)', 'Pitch-pine stair boards', 'madera_escalera', 2, sound='wood')
Stairs('casa_escalera_madera', 'Escalera de pinotea', 'Pitch-pine stairs', of=MADERA_ESC, kit=KIT, sound='wood')
Slab('casa_escalera_madera_losa', 'Losa de pinotea (descanso)', 'Pitch-pine slab (landing)', of=MADERA_ESC, kit=KIT, sound='wood')
import bkit as _bkit  # noqa: E402  (the registry, to reuse the cement floor cube for the basement stairs)
_CEM = next(b for b in _bkit.REGISTRY if b.key == 'casa_cemento_piso')
Stairs('casa_escalera_cemento', 'Escalera de cemento (sótano)', 'Cement stairs (basement)', of=_CEM, kit=KIT, sound='stone')
Slab('casa_escalera_cemento_losa', 'Losa de cemento', 'Cement slab', of=_CEM, kit=KIT, sound='stone')


# =============================================================================================== BASEMENT (sótano)
# Old common brick (ladrillo común: softer, pinker, blotchier than the facade brick, same 4 px course layout so the
# broken wall's brick faces line up with the cubes) under a grey-ochre lime plaster gone damp. The wall towards the
# sealed 1961 room CRACKS (three stacked cubes: the crack leaves/enters every block at the centre of its top/bottom
# edge, so arriba / medio / abajo connect) and is later BROKEN THROUGH by the Nona (in-wall pieces, see BOQUETE).
OLDBRICK = Ramp('#3a1a10', '#52251a', '#6b3222', '#843f2a', '#994d33', '#aa5c3d', '#b96c4a', '#c67e5a')
LIME_OLD = Ramp('#35322b', '#48443a', '#5c5749', '#716b5a', '#867f6b', '#99927c', '#aaa38c', '#b8b19a', '#c4bea8')
LIME61 = Ramp('#212224', '#2f3032', '#3f4042', '#515254', '#646566', '#777877', '#8a8a87', '#9c9b96', '#acaaa4', '#bab8b1')
SALT_OLD = Ramp('#5c5850', '#7c776a', '#9d978a', '#bab4a6', '#d0cbbe', '#e0dcd2')
WAX = Ramp('#6a6048', '#8f8566', '#b3a985', '#cfc6a2', '#e2dbbd')


def paint_old_brick(cv, v, seed=0, mask=None):
    """Old common brick: tone per brick, blotches, pits, crumbled arrises, recessed pale lime mortar."""
    X, Y = cv.X, cv.Y
    lab, joint = brick_fine_layout()
    nl = lab.max() + 1
    rc = np.random.default_rng(9600 + seed)
    tone = rc.choice([-2, -1, -1, 0, 0, 0, 1, 1, 2], nl)
    rv = np.random.default_rng(9610 + seed + 17 * v)
    inner = [k for k in range(nl) if not ((lab == k) & (border_dist(N, N) < 1)).any()]
    for k in rv.choice(inner, 3, replace=False):
        tone[k] = rv.choice([-3, -2, 2])
    li = np.maximum(lab, 0)
    idx = 4 + tone[li]
    f = cblend(fbm(N, N, 9620 + seed, cells=4, octaves=2, ax=2.0), fbm(N, N, 9630 + seed + v, cells=4, octaves=2, ax=2.0))
    idx = idx + posterize(f, [(0.76, 1), (0.22, -1)])
    ly = Y % 4
    idx = np.where(ly == 0, idx + 1, idx)
    idx = np.where(ly == 2, idx - 1, idx)
    for (x, y) in poisson(9640 + seed + v, 30, 2.4):
        if lab[y, x] >= 0:
            idx[y, x] += -2 if (x + 2 * y) % 3 == 0 else 1
    edge = ~joint & (nb(joint, 1, 0) | nb(joint, -1, 0) | nb(joint, 0, 1) | nb(joint, 0, -1))
    er = edge & (cblend(fbm(N, N, 9650 + seed, cells=16, octaves=1), fbm(N, N, 9651 + seed + v, cells=16, octaves=1)) > 0.72)
    j2 = joint | er
    m = np.ones((N, N), bool) if mask is None else mask
    cv.put(OLDBRICK, idx, m & ~j2)
    midx = np.full((N, N), 4) + posterize(fbm(N, N, 9660 + seed, cells=16, octaves=1), [(0.62, 1), (0.3, -1)])
    midx = midx - 2 * (nb(lab, 1, 0) >= 0) - er.astype(int)
    cv.put(LIME_OLD, midx, m & j2)
    return lab, j2


def sotano_base(cv, v, seed=0):
    """Basement lime plaster: lime relief at 0.85 contrast, cold damp clouds with a tide line at their edge."""
    idx = lime_idx(v + 60, base=5, seed=9700 + seed, rough=0.8)
    cv.put(LIME_OLD, 5.0 + (idx - 5) * 0.55)
    d = cblend(fbm(N, N, 9710 + seed, cells=2, octaves=3), fbm(N, N, 9711 + seed + v, cells=2, octaves=3))
    cv.tint('#2a3022', np.clip((d - 0.5) * 0.6, 0, 0.16))
    return d


def plaster_hole(cv, H, under, seed=0):
    """Plaster fallen off inside mask H: the canvas `under` shows through, shadowed under the plaster's top edge,
    the broken lime lip below catching the light."""
    r = rim(H, wrap=False)
    dk = np.where(r['in_top'], 0.45, 1.0) * np.where(r['in_left'], 0.72, 1.0) * np.where(nb(r['in_top'], 1, 0, False) & H, 0.82, 1.0)
    cv.rgb[H] = (under.rgb * dk[..., None])[H]
    cv.put(LIME_OLD, np.full((N, N), 7), r['out_below'])
    cv.put(LIME_OLD, np.full((N, N), 6), r['out_right'] & ~r['out_below'])
    cv.put(LIME_OLD, np.full((N, N), 2), r['out_above'] | r['out_left'])


@painter('pared_sotano')
def p_pared_sotano(v):
    """Basement wall: grey-ochre lime plaster over old brick, cold damp clouds with tide lines. VAR variants: v0-6
    clean, v7 salt bloom and black mould, v8 hairline cracks and an old nail with its rust run, v9 plaster fallen off
    showing the brick (for big falls use casa_pared_sotano_ladrillo)."""
    cv = Cv()
    X, Y = cv.X, cv.Y
    sotano_base(cv, v)
    v = {9: 1, 7: 2, 8: 3}.get(v, 0)
    if v == 1:
        H = flake(17, 12, 5.0, 3.2, 9720, jag=0.8) & (border_dist(N, N) > 3)
        sub = Cv()
        paint_old_brick(sub, 0, seed=1)
        sub.tint('#3a3428', 0.4)
        plaster_hole(cv, H, sub)
    if v == 2:
        sm = (fbm(N, N, 9730, cells=4, octaves=2) > 0.5) & (border_dist(N, N) > 2)
        salt_bloom(cv, sm, 9731, strength=0.28, density=0.35)
        mould_specks(cv, 9732, 3, keep=lambda x, y: border_dist(N, N)[int(y), int(x)] > 3)
    if v == 3:
        cm = path_mask(wander([(5, 3), (11, 12), (9, 20), (13, 29)], 9740, amp=2.5), wrap=False)
        cm |= path_mask(wander([(11, 12), (19, 15), (26, 13)], 9741, amp=1.5), wrap=False)
        cv.tint('#15130f', np.where(cm, 0.7, 0))
        cv.tint('#ffffff', np.where(nb(cm, 1, 0, False) & ~cm, 0.12, 0))
        cv.put(IRON, np.full((N, N), 4), (X == 22) & (Y == 8))            # an old nail head, rust bleeding down
        cv.put(IRON, np.full((N, N), 1), (X == 22) & (Y == 9))
        st = (np.abs(X - 22) < 1) & (Y > 9) & (Y < 22)
        cv.tint('#6a3a1c', np.where(st, 0.35 * (1 - (Y - 9) / 14.0), 0))
    return cv.out()


@painter('pared_sotano_zocalo')
def p_pared_sotano_zocalo(v):
    """Bottom course of the basement wall: rising damp (dark, green-black) with a tide line and patches of salt
    crust, the plaster rotted away along the floor showing wet brick, sand and dust against the foot."""
    cv = Cv()
    X, Y = cv.X, cv.Y
    sotano_base(cv, v + 4)
    hw_ = np.sin(np.pi * (X + 0.5) / N)
    wave = 12 + np.round(1.2 * np.sin((X + 4) / 32 * 2 * math.pi) + 5 * hw_ * (vnoise(N, N, 5, 1, 9753 + v) - 0.5)).astype(int)
    f = (Y - wave) / 12.0 + (fbm(N, N, 9750 + v, cells=4, octaves=3) - 0.5) * 0.5 * hw_
    damp = f > 0
    blot = cblend(fbm(N, N, 9757, cells=4, octaves=2), fbm(N, N, 9758 + v, cells=4, octaves=2))
    cv.tint('#1e2219', np.where(damp, np.clip(0.16 + f * 0.45 + (blot - 0.5) * 0.2, 0, 0.6), 0))
    tide = damp & ~nb(damp, 1, 0)
    cv.tint('#15170f', np.where(tide & (blot > 0.25), 0.4, 0.0))
    patch = cblend(fbm(N, N, 9759, cells=4, octaves=2), fbm(N, N, 9760 + v, cells=4, octaves=2)) > 0.55
    salt_bloom(cv, (Y < wave + 1) & (Y > wave - 5) & patch, 9751 + v, strength=0.55, density=0.45)
    mould_specks(cv, 9752 + v, 3, keep=lambda x, y: 0 < f[int(y), int(x)] < 0.7 and 2 < x < 29)
    top = 25 + np.round(0.8 * np.sin((X + 3) / 32 * 2 * math.pi) + 5 * hw_ * (vnoise(N, N, 7, 1, 9754 + v) - 0.5)).astype(int)
    rot = (Y > top) & ((fbm(N, N, 9761 + v, cells=8, octaves=1) > 0.3) | (Y > top + 2))
    sub = Cv()
    paint_old_brick(sub, v, seed=2)
    sub.tint('#15170f', 0.4)
    plaster_hole(cv, rot, sub)
    sand = (Y >= 29) & (fbm(N, N, 9755 + v, cells=16, octaves=1) > 0.45 - (Y - 29) * 0.12)
    cv.put(SAND, np.full((N, N), 3) + (fbm(N, N, 9756, cells=16, octaves=1) > 0.6), sand)
    return cv.out()


@painter('sotano_ladrillo')
def p_sotano_ladrillo(v):
    """Old common brick where the basement plaster is long gone: v1 islands of plaster still stuck on, v2 rising
    damp with salt in the joints."""
    cv = Cv()
    lab, j2 = paint_old_brick(cv, v)
    X, Y = cv.X, cv.Y
    if v == 1:
        for k, (cx, cy, rx, ry) in enumerate(((9, 9, 5.5, 4), (23, 22, 6, 4.5))):
            H = flake(cx, cy, rx, ry, 9770 + k, jag=0.5) & (border_dist(N, N) > 1)
            pidx = np.full((N, N), 5) + posterize(fbm(N, N, 9772 + k, cells=8, octaves=1), [(0.65, 1), (0.3, -1)])
            r = rim(H, wrap=False)
            pidx = pidx + r['in_top'] - 2 * r['in_bot']
            cv.put(LIME_OLD, pidx, H)
            cv.tint('#000000', np.where(r['out_below'] | r['out_right'], 0.35, 0))
    if v == 2:
        t = np.clip((Y - 12) / 20.0, 0, 1)
        cv.tint('#1a1c14', t * 0.45)
        salt_bloom(cv, j2 & (Y > 8) & (Y < 22), 9780, strength=0.85, density=0.7)
    return cv.out()


def grieta_painter(piece):
    """The crack in the wall of the sealed room. The gap shows the void behind (pure black), plaster lips lit below /
    shadowed above, hairline branches, plaster fallen beside it, and SAND from the 1961 room trickling out of it."""
    def p(v):
        cv = Cv()
        X, Y = cv.X, cv.Y
        sotano_base(cv, 0)
        sub = Cv()
        paint_old_brick(sub, 0, seed=3)
        if piece == 'arriba':
            ctrl, wy, seed = [(22, 3), (19, 10), (21, 17), (17, 25), (16, 31)], (lambda y: 1 + (y > 13) + (y > 24)), 9810
            flakes = [(20, 22, 3.5, 2.5)]
            branches = [((21, 6), (27, 2)), ((19, 12), (12, 9))]
        elif piece == 'medio':
            ctrl, wy, seed = [(16, 0), (12, 7), (15, 13), (20, 19), (18, 25), (16, 31)], (lambda y: 3 + (6 < y < 25)), 9820
            flakes = [(9, 9, 4.5, 3.5), (23, 21, 4, 3.5)]
            branches = [((12, 7), (4, 4)), ((15, 13), (7, 17)), ((20, 19), (28, 15)), ((18, 25), (26, 29))]
        else:
            ctrl, wy, seed = [(16, 0), (14, 8), (17, 15), (13, 23), (11, 31)], (lambda y: 3 if y < 20 else 2), 9830
            flakes = [(20, 10, 4, 3)]
            branches = [((14, 8), (6, 6)), ((17, 15), (25, 19)), ((13, 23), (22, 31))]
        for (cx, cy, rx, ry) in flakes:
            H = flake(cx, cy, rx, ry, seed + cx, jag=0.45) & (border_dist(N, N) > 1)
            plaster_hole(cv, H, sub)
        hm = np.zeros((N, N), bool)
        for a, b in branches:
            hm |= path_mask(wander([a, b], seed + a[0] * 7 + b[1], amp=1.6), wrap=False)
        cv.tint('#100e0b', np.where(hm, 0.65, 0))
        cv.tint('#ffffff', np.where(nb(hm, 1, 0, False) & ~hm, 0.1, 0))
        gap = np.zeros((N, N), bool)
        for (x, y) in wander(ctrl, seed, amp=1.4, depth=3):
            w = wy(y)
            x0 = x - w // 2
            gap[y, max(0, x0):min(N, x0 + w)] = True
        r = rim(gap, wrap=False)
        cv.col('#070605', gap)
        cv.col('#1b1712', gap & (r['in_left'] | r['in_right']) & (wy(16) > 2))
        cv.put(LIME_OLD, np.full((N, N), 1), r['out_left'] | r['out_above'])
        cv.put(LIME_OLD, np.full((N, N), 8), r['out_right'] & ~r['out_left'])
        if piece in ('medio', 'abajo'):   # sand settled in the bottom of the gap, and the trickle down the wall
            sg = gap & (fbm(N, N, seed + 5, cells=16, octaves=1) > 0.55) & (Y > 18)
            cv.put(SAND, np.full((N, N), 4), sg)
            y_from = 20 if piece == 'medio' else 0
            tr = (np.abs(X - 19.5) < 1.0) & (Y >= y_from) & ~gap
            cv.tint('#b8a47c', np.where(tr, 0.38 + 0.12 * (fbm(N, N, seed + 6, cells=1, octaves=1, ay=16) > 0.5), 0))
            if piece == 'medio':
                cv.put(SAND, np.full((N, N), 5), (X == 19) & (Y == 20))
        if piece == 'abajo':   # a fan of sand and crumbs at the foot of the wall
            fan = (Y > 23) & (np.abs(X - 17) < (Y - 23) * 1.4 + 1) & (fbm(N, N, 9835, cells=8, octaves=2) > 0.3 - (Y - 23) * 0.05)
            cv.put(SAND, np.full((N, N), 4) + (fbm(N, N, 9836, cells=16, octaves=1) > 0.6) - (Y == 31), fan)
            for (x, y) in poisson(9837, 6, 2.5, keep=lambda x, y: 25 < y < 31 and 8 < x < 26):
                cv.put(OLDBRICK, np.full((N, N), 4), rect(x, y, x + 1, y))
                cv.put(OLDBRICK, np.full((N, N), 2), rect(x, y + 1, x + 1, y + 1))
        return cv.out()
    return p


PAINTERS['grieta_arriba'] = grieta_painter('arriba')
PAINTERS['grieta'] = grieta_painter('medio')
PAINTERS['grieta_abajo'] = grieta_painter('abajo')


# =============================================================================================== THE 1961 ROOM walls
@painter('pared_61')
def p_pared_61(v):
    """The sealed 1961 room: rough brick under a lime wash once tinted with bluing (cal con añil), gone grey with
    dust and candle soot. Chalky uneven coverage: the brick courses ghost through only where the wash is thin.
    VAR variants: v0-6 clean, v7 a flake of wash gone (brick showing), v8 pale calcite runs, v9 three fingernail
    scratches."""
    cv = Cv()
    X, Y = cv.X, cv.Y
    idx = lime_idx(v + 70, base=7, seed=9900, rough=1.0)
    idx = 7.0 + (idx - 7) * 0.6
    st = cblend(fbm(N, N, 9901, cells=2, octaves=2, ax=1.0, ay=3), fbm(N, N, 9902 + v, cells=2, octaves=2, ax=1.0, ay=3))
    idx = idx + np.where(st > 0.8, 0.25, 0) - np.where(st < 0.18, 0.25, 0)
    thin = cblend(fbm(N, N, 9905, cells=2, octaves=3), fbm(N, N, 9906 + v, cells=2, octaves=3)) > 0.62
    lab, joint = brick_fine_layout()
    idx = idx - (joint & thin) * 1.1 - (joint & ~thin) * 0.25
    cv.put(LIME61, idx)
    cv.tint('#3e5466', 0.07)
    cv.tint('#7a4a36', np.where(thin & ~joint, 0.1, 0))
    cv.tint('#2a241c', np.clip((cblend(fbm(N, N, 9903, cells=2, octaves=3), fbm(N, N, 9904 + v, cells=2, octaves=3)) - 0.6) * 0.5, 0, 0.12))
    v = {7: 1, 8: 2, 9: 3}.get(v, 0)
    if v == 1:
        H = flake(16, 16, 7, 3.5, 9910, jag=0.8) & (border_dist(N, N) > 2)
        sub = Cv()
        paint_old_brick(sub, 1, seed=4)
        sub.tint('#5a5a56', 0.5)
        r = rim(H, wrap=False)
        cv.rgb[H] = (sub.rgb * np.where(r['in_top'], 0.6, 1.0)[..., None])[H]
        cv.put(LIME61, np.full((N, N), 9), r['out_below'])
    if v == 2:
        for k, x in enumerate((6, 18, 25)):
            L = 12 + (k * 7) % 12
            m = (X == x) & (Y > 1) & (Y < 1 + L) & (fbm(N, N, 9920 + k, cells=8, octaves=1) > 0.3)
            cv.tint('#e4e2da', np.where(m, 0.3, 0))
            cv.tint('#2c2a24', np.where(nb(m, 0, 1, False) & ~m, 0.18, 0))
            cv.tint('#e4e2da', np.where((X == x) & (Y == L) | (X == x) & (Y == L + 1), 0.4, 0))
    if v == 3:
        sm = np.zeros((N, N), bool)
        for k in range(3):
            sm |= path_mask(wander([(12 + k * 3, 10 + k), (14 + k * 3, 20 + k)], 9930 + k, amp=0.6, depth=2), wrap=False)
        cv.tint('#e8e4da', np.where(sm, 0.32, 0))
        cv.tint('#000000', np.where(nb(sm, -1, 0, False) & ~sm, 0.22, 0))
    return cv.out()


@painter('pared_61_zocalo')
def p_pared_61_zocalo(v):
    """Foot of the 1961 room wall: damp tide, sand kicked against it, scuffs of small shoes."""
    cv = Cv()
    base = PAINTERS['pared_61'](v)
    cv.rgb = base[..., :3].astype(float)
    cv.a = base[..., 3].astype(float)
    X, Y = cv.X, cv.Y
    hw_ = np.sin(np.pi * (X + 0.5) / N)
    wave = 17 + np.round(2 * np.sin((X + 9) / 32 * 2 * math.pi) + 4 * hw_ * (vnoise(N, N, 5, 1, 9940 + v) - 0.5)).astype(int)
    damp = Y > wave
    cv.tint('#1a1c18', np.where(damp, np.clip(0.1 + (Y - wave) * 0.025, 0, 0.4), 0))
    cv.tint('#121410', np.where(damp & ~nb(damp, 1, 0) & (fbm(N, N, 9947 + v, cells=8, octaves=1) > 0.3), 0.25, 0))
    salt_bloom(cv, (Y <= wave) & (Y > wave - 3), 9941 + v, strength=0.5, density=0.4)
    rng = np.random.default_rng(9942 + v)
    for k in range(4):
        x, y = int(rng.integers(3, 26)), int(rng.integers(22, 28))
        cv.tint('#0e0c0a', np.where((Y == y) & (X >= x) & (X < x + int(rng.integers(2, 5))), 0.45, 0))
    drift = 28 + np.round(1.5 * np.sin((X + 5) / 32 * 2 * math.pi) + 3 * hw_ * (vnoise(N, N, 6, 1, 9943 + v) - 0.5)).astype(int)
    sand = Y >= drift
    cv.put(SAND, np.full((N, N), 4) + (_hash01(X, Y, 9944) > 0.7) - (_hash01(X, Y, 9945) < 0.15), sand)
    cv.put(SAND, np.full((N, N), 6), sand & ~nb(sand, 1, 0, False))
    for (x, y) in poisson(9946 + v, 7, 2.5, keep=lambda x, y: drift[int(y), int(x)] - 4 < y < drift[int(y), int(x)]):
        cv.put(SAND, np.full((N, N), 3), (X == x) & (Y == y))
    return cv.out()


def soot_plume(cv, x0=16.0, y_base=34.0, top=False, seed=0):
    """Candle soot: a narrow dark tongue right above the flame widening into a diffuse fan that blackens the top."""
    X, Y = cv.X, cv.Y
    h = y_base - Y                                                   # px above the flame
    wob = (vnoise(N, N, 1, 4, seed) - 0.5) * 4
    half = 1.5 + np.maximum(h, 0) * 0.42 + (wob if not top else 0)
    if top:
        half = half + 14
    dx = np.abs(X + 0.5 - x0 - wob * 0.5)
    t = np.clip(1 - dx / half, 0, 1) ** 0.8
    a = t * np.clip(0.75 - np.maximum(h, 0) * 0.008, 0.2, 0.75)
    n = fbm(N, N, seed + 1, cells=2, octaves=3)
    a = a * (0.85 + 0.3 * n)
    cv.tint('#0d0a08', np.clip(a, 0, 0.85))


@painter('pared_61_hollin')
def p_pared_61_hollin(v):
    """The wall right above where the candles stood (place it over a candle on the floor): the soot tongue."""
    cv = Cv()
    base = PAINTERS['pared_61'](0)
    cv.rgb = base[..., :3].astype(float)
    cv.a = base[..., 3].astype(float)
    soot_plume(cv, 16.0, 34.0, seed=9950)
    return cv.out()


@painter('pared_61_hollin_alto')
def p_pared_61_hollin_alto(v):
    """The block(s) above the soot tongue: the fan of soot spreading and blackening towards the ceiling."""
    cv = Cv()
    base = PAINTERS['pared_61'](2)
    cv.rgb = base[..., :3].astype(float)
    cv.a = base[..., 3].astype(float)
    soot_plume(cv, 16.0, 66.0, seed=9950)
    cv.tint('#0d0a08', np.clip((12 - cv.Y) / 12.0, 0, 1) * 0.35 * cweight(p=0.5))
    return cv.out()


# =============================================================================================== BOQUETE: the broken wall
# The Nona breaks the wall of the sealed room (beat 14, 'wall.break'): swap the cracked cubes for these six in-wall
# pieces around a 2-wide x 2-high hole (its top bites ~0.5 block into the lintel row):
#        [pared_sotano]       [boquete_dintel_izq] [boquete_dintel_der]   [pared_sotano]
#        [boquete_izq_arriba]        (air)                (air)           [boquete_der_arriba]
#        [boquete_izq_abajo]         (air + escombros)    (air)           [boquete_der_abajo]
# 'facing' = the BASEMENT side (grey-ochre plaster); the z=16 side is the 1961 room (old grey lime wash).
# izq / der = left / right seen from the basement (izq = authoring +x). The jambs are built course by course (2/16
# per brick course) with the plaster spalled back from the broken brick edge; a few courses jut into the hole columns.
STROKES = None   # (defined below with the scratch font)
_BQ = {}


def bq_shape():
    """Hole outline in 'hole space': u 0..64 across [jamb izq | hole | hole | jamb der] seen from the basement
    (u = col*16 + 16 - x), y 0..48 (3 rows). Rows 0-1: per course k (2 units) the hole spans [L_k, R_k). Row 2: per
    2-unit column the hole reaches up to T (>= 32). Plaster setbacks per course/column (front = basement, back = 61)."""
    if _BQ:
        return _BQ
    rng = np.random.default_rng(9810)

    def q(val, k):
        off = 4.0 if k % 2 else 0.0
        qv = round((val - off) / 4.0) * 4.0 + off
        if rng.random() < 0.55:
            qv += float(rng.choice([-2.0, -1.5, -1.0, 1.0, 1.5, 2.0]))
        return qv
    L, R = [], []
    pl, pr = 12.0, 52.0
    for k in range(16):
        yc = 2 * k + 1
        hw = 19.5 if yc < 17 else 19.5 * math.sqrt(max(0.0, 1 - ((yc - 17) / 23.0) ** 2))
        lv = q(32 - hw + rng.normal(0, 1.6) + (2.5 if k == 0 else 0), k)
        rv = q(32 + hw + rng.normal(0, 1.6) - (2.0 if k == 0 else 0), k)
        lv = float(np.clip(lv, pl - 5, pl + 5))
        rv = float(np.clip(rv, pr - 5, pr + 5))
        lv, rv = float(np.clip(lv, 5.0, 19.0)), float(np.clip(rv, 45.0, 59.0))
        L.append(lv)
        R.append(rv)
        pl, pr = lv, rv
    T = []
    for c in range(16):
        uc = 16 + 2 * c + 1
        t = 32 + 8.0 * math.sqrt(max(0.0, 1 - ((uc - 32) / 16.6) ** 2)) + rng.normal(0, 1.3)
        T.append(max(32.0, 2 * round(t / 2)))

    def walk(n, mu, sd, lo, hi):
        s, out = mu, []
        for _ in range(n):
            s = float(np.clip(s + rng.normal(0, sd), lo, hi))
            out.append(round(s * 2) / 2)
        return out
    _BQ.update(L=L, R=R, T=T, sLf=walk(16, 2.0, 1.1, 0.5, 5.0), sRf=walk(16, 2.0, 1.1, 0.5, 5.0),
               sLb=walk(16, 1.0, 0.7, 0.0, 3.0), sRb=walk(16, 1.0, 0.7, 0.0, 3.0),
               sTf=walk(16, 2.0, 1.0, 0.0, 4.0), sTb=walk(16, 1.0, 0.6, 0.0, 2.0))
    return _BQ


def bq_core_painter():
    """Broken brick: brick faces where the plaster spalled (sampled like the old-brick cubes), the broken section
    (orange body, mortar beds, head joints through the wall thickness), crusty mortar beds on top/bottom."""
    brick = aligned(T('sotano_ladrillo', 0))

    def p(face, w, h, part):
        if face in ('north', 'south'):
            return brick(face, w, h, part)
        x, y, z = face_coords(part, face, w, h)
        cv = Cv(w, h)
        k = fkey(part, face)
        n = vnoise(w, h, max(1, w // 3), max(1, h // 2), k)
        n2 = vnoise(w, h, max(1, w // 2), max(1, h // 2), k + 1)
        if face in ('west', 'east'):
            py = np.floor((16 - y) * 2).astype(int)
            course = py // 4
            r = py % 4
            zz = np.floor(z * 2).astype(int)
            vj = ((zz + course * 5) % 9 == 0)
            idx = 3 + (n > 0.6) - (n < 0.3) + (r == 0) - (r == 2)
            idx = idx - (((zz * 7 + py * 3) % 11) == 0) * 2
            body = (r != 3) & ~vj
            cv.put(OLDBRICK, idx, body)
            cv.put(LIME_OLD, np.full((h, w), 3) + (n2 > 0.55) - (r == 3) * (zz % 5 == 0) * 2, ~body)
        else:
            idx = 4 + (n > 0.62) - (n < 0.3) - (face == 'down') * 2
            cv.put(LIME_OLD, idx)
            cv.put(OLDBRICK, np.full((h, w), 3), (n2 > 0.72))
            if face == 'up':
                cv.tint('#8a7a5c', np.where(n2 < 0.35, 0.25, 0.08))
        return cv.out()
    return p


def bq_plaster_painter(side):
    tex = aligned(T('pared_sotano', 0)) if side == 'front' else aligned(T('pared_61', 0))
    ramp = LIME_OLD if side == 'front' else LIME61
    skin = 2

    def p(face, w, h, part):
        if face in ('north', 'south'):
            return tex(face, w, h, part)
        x, y, z = face_coords(part, face, w, h)
        cv = Cv(w, h)
        outer = (z < 0.5) if side == 'front' else (z > 15.5)
        n = vnoise(w, h, max(1, w // 2), max(1, h // 2), fkey(part, face))
        idx = np.where(outer, skin, 6 + (n > 0.6)) + (face == 'up') - 2 * (face == 'down')
        cv.put(ramp, idx)
        return cv.out()
    return p


def _clip_iv(ivs, lo, hi):
    out = []
    for a, b in ivs:
        a, b = max(a, lo), min(b, hi)
        if b - a > 0.05:
            out.append((a, b))
    return out


def boquete_parts(piece):
    S = bq_shape()
    col = {'izq_abajo': 0, 'izq_arriba': 0, 'dintel_izq': 1, 'dintel_der': 2, 'der_arriba': 3, 'der_abajo': 3}[piece]
    row = 2 if piece.startswith('dintel') else (1 if piece.endswith('arriba') else 0)
    lo, hi = {0: (0.0, 20.0), 1: (16.0, 32.0), 2: (32.0, 48.0), 3: (44.0, 64.0)}[col]
    painters = {'core': bq_core_painter(), 'front': bq_plaster_painter('front'), 'back': bq_plaster_painter('back')}
    zr = {'core': (1.0, 15.0), 'front': (0.0, 1.0), 'back': (15.0, 16.0)}
    fc = {'core': FACES, 'front': ('north', 'west', 'east', 'up', 'down'), 'back': ('south', 'west', 'east', 'up', 'down')}
    boxes = {}   # (layer, xa, xb) -> list of courses
    for kl in range(8):
        k = row * 8 + kl
        for layer in ('core', 'front', 'back'):
            if row < 2:
                sl = {'core': 0.0, 'front': S['sLf'][k], 'back': S['sLb'][k]}[layer]
                sr = {'core': 0.0, 'front': S['sRf'][k], 'back': S['sRb'][k]}[layer]
                ivs = [(0.0, S['L'][k] - sl), (S['R'][k] + sr, 64.0)]
            else:
                yb = 32.0 + 2 * kl
                ivs, run = [(0.0, 16.0)], None
                for c in range(16):
                    st = {'core': 0.0, 'front': S['sTf'][c], 'back': S['sTb'][c]}[layer]
                    solid = S['T'][c] + st <= yb + 0.01
                    u0 = 16.0 + 2 * c
                    if solid and run is None:
                        run = u0
                    if not solid and run is not None:
                        ivs.append((run, u0))
                        run = None
                if run is not None:
                    ivs.append((run, 48.0))
                ivs.append((48.0, 64.0))
            for a, b in _clip_iv(ivs, lo, hi):
                xa, xb = col * 16 + 16 - b, col * 16 + 16 - a
                boxes.setdefault((layer, round(xa, 3), round(xb, 3)), []).append(kl)
    parts = []
    for (layer, xa, xb), ks in sorted(boxes.items(), key=lambda t: (t[0][0], t[1][0])):
        ks = sorted(ks)
        runs, s0, prev = [], ks[0], ks[0]
        for kk in ks[1:]:
            if kk != prev + 1:
                runs.append((s0, prev))
                s0 = kk
            prev = kk
        runs.append((s0, prev))
        for a, b in runs:
            z0, z1 = zr[layer]
            parts.append(P((xa, 2.0 * a, z0), (xb, 2.0 * b + 2.0, z1), painters[layer], faces=fc[layer], name=f'{layer}'))
    return parts


# --- rubble
def rubble_paint(face, w, h, part, cv):
    """Mixed rubble: broken brick bits, lumps of lime plaster, dust; sand where kind='arena'."""
    x, y, z = face_coords(part, face, w, h)
    k = fkey(part, face)
    n = vnoise(w, h, max(1, w // 2), max(1, h // 2), k)
    n2 = vnoise(w, h, max(1, w // 3), max(1, h // 3), k + 3)
    cv.put(LIME_OLD, np.full((h, w), 4) + (n > 0.6) - (n < 0.25) - (face == 'down') * 2)
    br = n2 > 0.55
    cv.put(OLDBRICK, np.full((h, w), 4) + (n > 0.5) - (face != 'up'), br)
    cv.put(LIME_OLD, np.full((h, w), 1), rim(br, wrap=False)['out_below'])
    if face == 'up':
        cv.tint('#9a8e74', np.where(n < 0.4, 0.3, 0.1))


def sand_paint(face, w, h, part, cv):
    x, y, z = face_coords(part, face, w, h)
    n = vnoise(w, h, max(1, w // 2), max(1, h // 2), fkey(part, face))
    cv.put(SAND, np.full((h, w), 4) + (n > 0.62) - (n < 0.28) - (face == 'down') * 2 + (face == 'up'))
    gr = ((np.floor(x * 2).astype(int) * 7 + np.floor(z * 2).astype(int) * 13 + np.floor(y * 2).astype(int) * 5) % 9) == 0
    cv.put(SAND, np.full((h, w), 2), gr)


def brickbat_paint(face, w, h, part, cv):
    n = vnoise(w, h, max(1, w // 2), max(1, h // 2), fkey(part, face))
    idx = 4 + (n > 0.6) - (n < 0.3) + (face == 'up') - (face == 'down') * 2
    cv.put(OLDBRICK, idx)
    bd, X, Y = border_px(w, h)
    if face in ('west', 'east', 'north', 'south') and min(w, h) > 2:
        cv.put(OLDBRICK, np.full((h, w), 2), (Y == h - 1))
    if face == 'north' and w > 3:
        cv.put(LIME_OLD, np.full((h, w), 5), X < 2)   # plaster still stuck on one end


def escombros_parts(arena=False):
    """Rubble pile on the floor where the wall came down (low mound, brickbats and plaster flakes; walk over it).
    arena=True: the sand of the 1961 room spilled out over the rubble (the hole side)."""
    rb, bb = pp_fn(rubble_paint), pp_fn(brickbat_paint)
    pl = pp_fn(lambda face, w, h, part, cv: cv.put(LIME_OLD, np.full((h, w), 6) + (face == 'up') - 3 * (face == 'down')
                                                    - (border_px(w, h)[0] == 0)))
    parts = [P((1.0, 0, 2.0), (15.0, 1.6, 14.5), rb, name='mound0'), P((3.0, 1.6, 3.5), (12.5, 3.0, 12.0), rb, name='mound1'),
             P((5.5, 3.0, 5.0), (10.5, 4.0, 9.5), rb, name='mound2')]
    for (x0, z0, ang, y0) in ((2.0, 1.0, 22.5, 1.6), (10.0, 3.0, -22.5, 3.0), (6.0, 10.5, 45, 1.6), (11.5, 11.0, 0, 1.6),
                              (4.5, 6.0, -45, 3.0), (12.5, 6.5, 22.5, 0.0)):
        parts.append(P((x0, y0, z0), (x0 + 3.8, y0 + 1.6, z0 + 1.9), bb, rot=('y', ang, (x0 + 1.9, y0, z0 + 1.0)), name='brickbat'))
    for (x0, z0, ang) in ((8.0, 0.4, 22.5), (13.0, 9.0, -22.5), (0.6, 9.0, 45)):
        parts.append(P((x0, 0.0, z0), (x0 + 2.6, 0.5, z0 + 2.0), pl, rot=('y', ang, (x0 + 1.3, 0, z0 + 1.0)), name='plaster_flake'))
    if arena:
        sp = pp_fn(sand_paint)
        parts += [P((0.0, 0, 8.0), (16.0, 1.0, 16.0), sp, name='sand0'), P((2.0, 1.0, 10.0), (14.0, 2.2, 16.0), sp, name='sand1'),
                  P((4.5, 2.2, 12.5), (11.5, 3.0, 16.0), sp, name='sand2')]
    return parts


# =============================================================================================== SCRATCHED WRITING
# A stroke font (glyph grid 0..w x 0..6, y down) drawn with Bresenham lines and per-point jitter: a hand scratching
# with a nail or a knife, not a typeface. Children's version: wobbling baseline, letters growing, a mirrored Z.
STROKES = {
    'A': (4, [[(0, 6), (2, 0), (4, 6)], [(0.9, 3.9), (3.1, 3.9)]]),
    'B': (4, [[(0, 6), (0, 0), (3, 0), (4, 1), (4, 2), (3, 3), (0, 3)], [(3, 3), (4, 4), (4, 5), (3, 6), (0, 6)]]),
    'C': (4, [[(4, 1), (3, 0), (1, 0), (0, 1.5), (0, 4.5), (1, 6), (3, 6), (4, 5)]]),
    'D': (4, [[(0, 0), (0, 6), (2.5, 6), (4, 4.5), (4, 1.5), (2.5, 0), (0, 0)]]),
    'E': (4, [[(4, 0), (0, 0), (0, 6), (4, 6)], [(0, 3), (3, 3)]]),
    'F': (4, [[(4, 0), (0, 0), (0, 6)], [(0, 3), (3, 3)]]),
    'G': (4, [[(4, 1), (3, 0), (1, 0), (0, 1.5), (0, 4.5), (1, 6), (3, 6), (4, 5), (4, 3.5), (2.5, 3.5)]]),
    'H': (4, [[(0, 0), (0, 6)], [(4, 0), (4, 6)], [(0, 3), (4, 3)]]),
    'I': (2, [[(1, 0), (1, 6)]]),
    'L': (3.5, [[(0, 0), (0, 6), (3.5, 6)]]),
    'M': (4.5, [[(0, 6), (0, 0), (2.25, 3.5), (4.5, 0), (4.5, 6)]]),
    'N': (4, [[(0, 6), (0, 0), (4, 6), (4, 0)]]),
    'O': (4, [[(1, 0), (3, 0), (4, 1.5), (4, 4.5), (3, 6), (1, 6), (0, 4.5), (0, 1.5), (1, 0)]]),
    'P': (4, [[(0, 6), (0, 0), (3, 0), (4, 1), (4, 2), (3, 3), (0, 3)]]),
    'R': (4, [[(0, 6), (0, 0), (3, 0), (4, 1), (4, 2), (3, 3), (0, 3)], [(1.8, 3), (4, 6)]]),
    'S': (4, [[(4, 0.8), (3, 0), (1, 0), (0, 1), (0, 2), (1, 3), (3, 3), (4, 4), (4, 5), (3, 6), (1, 6), (0, 5.2)]]),
    'T': (4, [[(0, 0), (4, 0)], [(2, 0), (2, 6)]]),
    'U': (4, [[(0, 0), (0, 5), (1, 6), (3, 6), (4, 5), (4, 0)]]),
    'V': (4, [[(0, 0), (2, 6), (4, 0)]]),
    'X': (4, [[(0, 0), (4, 6)], [(4, 0), (0, 6)]]),
    'Z': (4, [[(0, 0), (4, 0), (0, 6), (4, 6)]]),
    '+': (3, [[(1.5, -0.5), (1.5, 6)], [(0, 1.6), (3, 1.6)]]),
    'Y': (4, [[(0, 0), (2, 3), (4, 0)], [(2, 3), (2, 6)]]),
    '.': (0.6, [[(0.3, 5.5), (0.3, 6)]]),
    '!': (0.8, [[(0.4, 0), (0.4, 4.0)], [(0.4, 5.6), (0.4, 6)]]),
}


def sline(m, a, b):
    H, W = m.shape
    for (x, y) in line_px(a[0], a[1], b[0], b[1]):
        if 0 <= x < W and 0 <= y < H:
            m[y, x] = True


def scratch_text(m, text, x, y, size, rng, jit=0.5, slant=0.0, mirror=(), wobble=1, grow=0.0, twice=()):
    """Scratch `text` into mask m: cap height `size` px, top-left (x, y). mirror: indices of letters drawn backwards
    (children); twice: indices gone over twice (a doubled, sloppier line). Returns the x where the text ends."""
    sc0 = size / 6.0
    cx = float(x)
    for n, ch in enumerate(text):
        if ch == ' ':
            cx += sc0 * 3.2
            continue
        gw, strokes = STROKES[ch]
        sc = sc0 * (1 + rng.uniform(-0.12, 0.12) + grow * n)
        dy = int(rng.integers(-wobble, wobble + 1)) if wobble else 0
        for rep in range(2 if n in twice else 1):
            for s in strokes:
                pts = []
                for (gx, gy) in s:
                    if n in mirror:
                        gx = gw - gx
                    pts.append((cx + gx * sc + (6 - gy) * sc * slant + rng.normal(0, jit + rep * 0.5),
                                y + size + dy - (6 - gy) * sc + rng.normal(0, jit + rep * 0.5)))
                for a, b in zip(pts, pts[1:]):
                    sline(m, a, b)
        cx += (gw + 1.7) * sc
    return int(round(cx))


def scratch_rgba(m, glow=False):
    """Scratched into the sooty lime: pale fresh lime in the groove, its upper wall a dark shadow line. glow=True:
    the same marks burning (ember core, orange and red halo) for the climax."""
    H, W = m.shape
    out = np.zeros((H, W, 4))
    if glow:
        h2 = dilate(m, 2, False) & ~m
        h1 = dilate(m, 1, False) & ~m
        out[h2, :3] = C('#7a1e0e')
        out[h2, 3] = 95
        out[h1, :3] = C('#e0662a')
        out[h1, 3] = 200
        out[m, :3] = C('#ffe0a0')
        out[m, 3] = 255
        return out
    above = nb(m, -1, 0, False) & ~m
    left = nb(m, 0, -1, False) & ~m & ~above
    out[above, :3] = C('#1c1915')
    out[above, 3] = 200
    out[left, :3] = C('#2a2621')
    out[left, 3] = 110
    n = vnoise(W, H, max(1, W // 6), max(1, H // 6), 9961)
    Y, X = np.mgrid[0:H, 0:W]
    skip = m & (_hash01(X, Y, 9962) < 0.1)            # the nail skipped: broken, scratchy strokes
    core = m & ~skip
    out[core, :3] = C('#c4bdae') * (0.86 + 0.18 * n[core])[:, None]
    out[core, 3] = 215
    out[skip, :3] = C('#6e685e')
    out[skip, 3] = 120
    return out


def stick_girl(m, x, y, rng, s=1.0):
    """Child's drawing of a girl (pigtails, triangle dress), feet at y. Returns the hand position."""
    j = lambda p: (p[0] + rng.normal(0, 0.3), p[1] + rng.normal(0, 0.3))
    hy = y - 14 * s
    for a in np.linspace(0, 2 * math.pi, 9)[:-1]:
        b = a + 2 * math.pi / 8
        sline(m, j((x + 2.2 * s * math.cos(a), hy + 2.2 * s * math.sin(a))), j((x + 2.2 * s * math.cos(b), hy + 2.2 * s * math.sin(b))))
    sline(m, (x - 2.5 * s, hy - 1), (x - 4.5 * s, hy + 1.5 * s))
    sline(m, (x + 2.5 * s, hy - 1), (x + 4.5 * s, hy + 1.5 * s))
    sline(m, (x, hy + 2.2 * s), (x - 4 * s, y - 4 * s))
    sline(m, (x, hy + 2.2 * s), (x + 4 * s, y - 4 * s))
    sline(m, (x - 4 * s, y - 4 * s), (x + 4 * s, y - 4 * s))
    sline(m, (x - 1.5 * s, y - 4 * s), (x - 1.8 * s, y))
    sline(m, (x + 1.5 * s, y - 4 * s), (x + 1.8 * s, y))
    sline(m, (x - 1, hy + 4 * s), (x - 5 * s, hy + 6.5 * s))
    sline(m, (x + 1, hy + 4 * s), (x + 5 * s, hy + 6.5 * s))
    return (x + 5 * s, hy + 6.5 * s), (x - 5 * s, hy + 6.5 * s)


def tall_friend(m, x, y, rng, hand=None, h=26):
    """'Mi amigo': a figure twice as tall as the girl, scribbled-black head, very long arms with long fingers."""
    hy = y - h
    for k in range(9):   # the head: a scribble, gone over and over
        sline(m, (x - 2.5 + rng.normal(0, 0.5), hy - 2 + k * 0.5), (x + 2.5 + rng.normal(0, 0.5), hy - 2.5 + k * 0.55))
    sline(m, (x, hy + 2.5), (x, y - 9))
    sline(m, (x, y - 9), (x - 2.5, y))
    sline(m, (x, y - 9), (x + 2.5, y))
    sh = (x, hy + 5)
    end = hand if hand else (x - 11, y - 6)
    sline(m, sh, ((sh[0] + end[0]) / 2, sh[1] + 3))
    sline(m, ((sh[0] + end[0]) / 2, sh[1] + 3), end)
    other = (x + 10, y - 4)
    sline(m, sh, (x + 6, hy + 10))
    sline(m, (x + 6, hy + 10), other)
    for d in (-2, 0, 2):
        sline(m, other, (other[0] + 1.5 + d * 0.3, other[1] + 3))


def tally(m, x, y, n, rng, h=7):
    """Day counting marks: groups of four bars and a strike."""
    for g in range(0, n, 5):
        k = min(5, n - g)
        gx = x + (g // 5) * 10
        for b in range(min(4, k)):
            sline(m, (gx + b * 2 + rng.normal(0, 0.3), y), (gx + b * 2 + rng.normal(0, 0.4), y + h))
        if k == 5:
            sline(m, (gx - 1, y + h), (gx + 7, y))


def img_lemaza():
    """3 blocks wide x 1.5 tall (96 x 48 px): LEMAZA scratched over and over at a child's height, the Z backwards,
    the last line dragging into four fingernail marks; day tallies; the girl holding hands with her tall friend."""
    m = np.zeros((48, 96), bool)
    rng = np.random.default_rng(9960)
    scratch_text(m, 'LEMAZA', 5, 3, 12, rng, jit=0.55, slant=0.12, twice={0, 2})
    scratch_text(m, 'LEMAZA LEMAZA', 3, 22, 6, rng, jit=0.45, slant=0.06, mirror={11}, grow=0.012)
    x = scratch_text(m, 'LEMAZA', 4, 34, 6, rng, jit=0.5, slant=-0.04)
    for k in range(4):
        m |= path_mask(wander([(x + 1 + k * 2.2, 33 + k * 0.6), (x + 7 + k * 2.6, 47)], 9961 + k, amp=0.8, depth=2), 96, 48, wrap=False)
    hand_r, hand_l = stick_girl(m, 62, 46, rng, s=0.95)
    tall_friend(m, 84, 47, rng, hand=(hand_r[0] + 1, hand_r[1]), h=30)
    return scratch_rgba(m)


def img_lemaza_chico():
    """One block (32 x 32 px): three cramped lines of LEMAZA, the last one trailing off."""
    m = np.zeros((32, 32), bool)
    rng = np.random.default_rng(9970)
    scratch_text(m, 'LEMAZA', 2, 3, 5, rng, jit=0.35, slant=0.08)
    scratch_text(m, 'LEMAZA', 3, 12, 5, rng, jit=0.4, slant=0.1)
    x = scratch_text(m, 'LEMA', 2, 21, 5, rng, jit=0.45, slant=0.12)
    m |= path_mask(wander([(x, 24), (30, 29)], 9971, amp=1.2), 32, 32, wrap=False)
    return scratch_rgba(m)


def img_dibujo():
    """Two blocks wide (64 x 32 px): 'MI AMIGO' over the drawing: the girl, the doll with the stitched mouth in her
    other hand, the tall friend holding her hand, a sun with a face."""
    m = np.zeros((32, 64), bool)
    rng = np.random.default_rng(9980)
    scratch_text(m, 'MI AMIGO', 4, 2, 6, rng, jit=0.4, slant=0.05, grow=0.02)
    hr, hl = stick_girl(m, 24, 31, rng, s=0.95)
    tall_friend(m, 38, 31, rng, hand=(hr[0] + 1, hr[1] + 0.5), h=22)
    cx, cy = hl[0] - 2, hl[1] + 3
    for a in np.linspace(0, 2 * math.pi, 7)[:-1]:
        b = a + 2 * math.pi / 6
        sline(m, (cx + 1.8 * math.cos(a), cy + 1.8 * math.sin(a)), (cx + 1.8 * math.cos(b), cy + 1.8 * math.sin(b)))
    sline(m, (cx - 1, cy + 0.5), (cx + 1, cy + 0.5))
    m[int(cy) + 1, int(cx)] = True
    sx, sy = 55, 7
    for a in np.linspace(0, 2 * math.pi, 9)[:-1]:
        b = a + 2 * math.pi / 8
        sline(m, (sx + 3.2 * math.cos(a), sy + 3.2 * math.sin(a)), (sx + 3.2 * math.cos(b), sy + 3.2 * math.sin(b)))
        sline(m, (sx + 4.6 * math.cos(a), sy + 4.6 * math.sin(a)), (sx + 6.6 * math.cos(a), sy + 6.6 * math.sin(a)))
    m[sy - 1, sx - 1] = m[sy - 1, sx + 1] = True
    sline(m, (sx - 1, sy + 1.5), (sx + 1, sy + 1.5))
    sline(m, (2, 31), (62, 30))
    return scratch_rgba(m)


def img_palitos():
    """One block: weeks of days counted on the wall in rows of tallies, the last group unfinished."""
    m = np.zeros((32, 32), bool)
    rng = np.random.default_rng(9990)
    for r, n in enumerate((15, 15, 15, 8)):
        tally(m, 1 + r % 2, 1 + r * 8, n, rng, h=5)
    return scratch_rgba(m)


def img_latin(glow=False):
    """Three blocks wide (96 x 48 px): the priest's knife-cut Latin, crosses on both sides: VADE RETRO / SATANA /
    EXI AB EA ('leave her'). glow=True: the same marks burning for beat 15."""
    m = np.zeros((48, 96), bool)
    rng = np.random.default_rng(9995)
    scratch_text(m, 'VADE RETRO', 13, 3, 8, rng, jit=0.25, wobble=0)
    scratch_text(m, 'SATANA', 17, 16, 11, rng, jit=0.25, wobble=0, twice={0})
    scratch_text(m, 'EXI AB EA', 27, 34, 6, rng, jit=0.25, wobble=0)
    for cx in (5, 90):
        sline(m, (cx, 6), (cx, 30))
        sline(m, (cx - 4, 12), (cx + 4, 12))
        sline(m, (cx + 1, 6), (cx + 1, 30))
    return scratch_rgba(m, glow=glow)


def img_manos():
    """One block: three small soot handprints at a child's height, the last one dragged down the wall."""
    W = H = 32
    out = np.zeros((H, W, 4))
    Y, X = np.mgrid[0:H, 0:W]
    rng = np.random.default_rng(9998)
    HAND = ['.#.#.#..', '.#.#.#.#', '.#.#.#.#', '######.#', '#######.', '.######.', '..#####.', '..####..', '...##...']
    hm = ascii_mask(HAND)
    for (x0, y0, drag, flip) in ((3, 4, 0, False), (14, 2, 0, True), (21, 12, 15, False)):
        m = np.zeros((H, W), bool)
        stamp(m, hm[:, ::-1] if flip else hm, x0, y0)
        if drag:
            for fx in (x0 + 1, x0 + 3, x0 + 5, x0 + 7):
                for yy in range(y0 + 3, min(H, y0 + 3 + drag - (fx % 3) * 2)):
                    if 0 <= fx < W:
                        m[yy, fx] = True
        a = np.where(m, 150 + 70 * vnoise(W, H, 8, 8, 9999 + x0), 0)
        a = np.where(m & (Y > y0 + 9), a * np.clip(1 - (Y - y0 - 9) / 18.0, 0.25, 1), a)
        out[m, :3] = C('#120e0b')
        out[..., 3] = np.maximum(out[..., 3], a)
    return out


def wall_decal(name, builder, w_units, h_units, y0=0.0, x0=None, shade=True, z=15.92):
    """A flat decal on the face of the wall block behind (z = 16 side) at 2 px per unit, centred on this block
    (x0 = 8 - w/2) unless x0 is given. It overflows into the neighbouring blocks (see the module docstring)."""
    if x0 is None:
        x0 = 8 - w_units / 2.0

    def p(face, w, h, part):
        if name not in _IRON:
            _IRON[name] = builder()
        img = _IRON[name]
        x, y, z_ = face_coords(part, face, w, h)
        H_, W_ = img.shape[:2]
        col = np.clip(np.floor((x0 + w_units - x) * 2).astype(int), 0, W_ - 1)
        row = np.clip(np.floor((y0 + h_units - y) * 2).astype(int), 0, H_ - 1)
        return np.clip(img[row, col], 0, 255).round().astype(np.uint8)
    return [PL((x0, y0, z), (x0 + w_units, y0 + h_units, z), p, faces=('north',), shade=shade, name='decal')]


# =============================================================================================== DAMP STAIN ('Es la humedad')
def img_humedad(face=False):
    """2 x 2 blocks (64 x 64 px), translucent: Jorge's 'humedad' rising from the floor up the living-room wall. It
    DARKENS the paint like water soaking in (a warm ochre-brown wet zone over the beige, alpha growing towards the
    floor), the front climbs in irregular tongues, a 2-3 px tide line where the salts dry out fades softly into the
    dry paint above, an older fainter tide inside, mould dots and paint blisters only inside the wet zone.
    face=True: the wettest patches settle into two eyes and a long open mouth with runs - wetter, darker zones of
    the same stain, not black holes."""
    W = H = 64
    Y, X = np.mgrid[0:H, 0:W]
    out = np.zeros((H, W, 4))
    n = fbm(W, H, 9950, cells=3, octaves=4)
    n2 = fbm(W, H, 9951, cells=8, octaves=2)
    col = np.arange(W)
    front = 27 + 5 * (vnoise(W, 1, 4, 1, 9956)[0] - 0.5) * 2 + 3.5 * (vnoise(W, 1, 11, 1, 9957)[0] - 0.5) * 2 \
        + 1.5 * (vnoise(W, 1, 23, 1, 9959)[0] - 0.5) * 2
    if face:
        front = np.minimum(front, 21 + np.abs(col - 32) * 0.35)
    side = np.minimum(col, W - 1 - col)
    front = front + (np.clip(14 - side, 0, 14) / 14.0) ** 2 * 18 * (0.7 + 0.6 * vnoise(W, 1, 6, 1, 9960)[0])
    sdist = Y - front[None, :] + (n - 0.5) * 3.0
    fade = np.clip((side[None, :] - 1 + (n - 0.5) * 6) / 9.0, 0, 1) * np.ones((H, 1))   # dies out before the edges

    def over(mask, color, a):
        a = np.clip(np.where(mask, a * fade, 0), 0, 255) / 255.0
        c = C(color)
        base_a = out[..., 3] / 255.0
        na = a + base_a * (1 - a)
        out[..., :3] = np.where(na[..., None] > 0, (c * a[..., None] + out[..., :3] * (base_a * (1 - a))[..., None]) / np.maximum(na, 1e-6)[..., None], out[..., :3])
        out[..., 3] = na * 255
    inside = sdist > 0
    wet = np.clip(sdist / 30.0, 0, 1)
    soak = np.clip(sdist / 9.0, 0, 1) ** 0.8
    # the wet zone: warm ochre-brown darkening (multiply-like over the beige: same hue family, darker), soaking in
    # gradually under the front and darkest towards the floor, mottled
    over(inside, '#7a5c36', 26 + 64 * soak + 50 * wet + 20 * (n2 - 0.5))
    over(inside & (wet > 0.45), '#4e4a32', 70 * (wet - 0.45) + 10 * (n2 > 0.6))       # greyer, greener near the floor
    # tide line: 2-3 px at the front, broken, soft gradient into the dry paint above
    over((sdist > -0.5) & (sdist < 2.5) & (n2 > 0.3), '#5a4224', 40 + 30 * (n2 > 0.55) - 14 * np.abs(sdist - 1.0))
    over((sdist <= -0.5) & (sdist > -1.5), '#7a5c36', 22)
    over((sdist <= -1.5) & (sdist > -2.5), '#7a5c36', 10)
    # an older, fainter tide inside, broken
    over((np.abs(sdist - 9.0) < 0.9) & (n2 > 0.42), '#5a4426', 36)
    # a few salt crystals right on the tide line (inside the stain)
    over((sdist > 0.5) & (sdist < 2.0) & (_hash01(X, Y, 9958) > 0.93), '#d8ccb0', 70)
    rng = np.random.default_rng(9952)
    for (cx, cy) in poisson(9953, 8, 6.0, W, H, keep=lambda x, y: sdist[int(y), int(x)] > 10, wrap=False):
        for k in range(int(rng.integers(6, 14))):
            x, y = int(round(cx + rng.normal(0, 2.0))), int(round(cy + rng.normal(0, 1.6)))
            if 0 <= x < W and 0 <= y < H and sdist[y, x] > 6:
                over((X == x) & (Y == y), '#24221a', 90 + 50 * rng.random())
    for (cx, cy) in poisson(9954, 7, 5.0, W, H, keep=lambda x, y: 4 < sdist[int(y), int(x)] < 14, wrap=False):
        r = 1.2 + rng.random() * 1.1
        b = (X + 0.5 - cx) ** 2 + (Y + 0.5 - cy) ** 2 < r * r
        over(b & (Y < cy), '#c8b490', 50)                                   # blister: the lifted paint catches light
        over(rim(b, wrap=False)['out_below'], '#3a2a14', 90)
    for (cx, cy) in ((14, 59), (47, 60)):                                  # small flakes off at the foot
        fl = flake(cx % 32 + 0.0, cy % 32 + 0.0, 2.0, 1.3, 9955 + cx, jag=0.4)
        fm = np.zeros((H, W), bool)
        fm[(cy // 32) * 32:(cy // 32) * 32 + 32, (cx // 32) * 32:(cx // 32) * 32 + 32] = fl
        over(fm, '#b8aa8c', 110)
        over(rim(fm, wrap=False)['out_below'], '#3a2e1e', 120)
    if face:
        for (cx, cy, rx, ry) in ((24.0, 33, 3.8, 5.0), (40.0, 32, 4.0, 4.8)):
            e = ((X + 0.5 - cx) / rx) ** 2 + ((Y + 0.5 - cy) / ry) ** 2 + (n - 0.5) * 0.5
            over(e < 1.0, '#5a4224', 70)
            over(e < 0.55, '#3e2e18', 70)
            over(np.abs(e - 1.0) < 0.18, '#4a3820', 50)                    # its own little tide ring
            for k, tx in enumerate((cx - 1, cx + 1.5)):
                run = (np.abs(X + 0.5 - tx) < 0.6) & (Y > cy + ry - 1) & (Y < cy + ry + 6 + k * 4)
                over(run, '#4a3820', 70)
        mo = ((X + 0.5 - 32.5) / 4.6) ** 2 + ((Y + 0.5 - 47) / 8.0) ** 2 + (n - 0.5) * 0.45
        over(mo < 1.0, '#5a4224', 70)
        over(mo < 0.5, '#3a2a16', 80)
        over(np.abs(mo - 1.0) < 0.15, '#4a3820', 50)
    return out


# =============================================================================================== TOTI'S POSTERS (decals)
# Four invented posters (no real brands) as wall decals, so they can be placed one by one and never wrap around an
# outside corner: 1 shooter 'FRAG', 2 anime heroine, 3 the neighbourhood football club C.A.V.E., 4 the streamer
# 'PIBE GG'. 22 x 30 px of paper (11 x 15 units) + 1 px curl shadow, taped at the corners.
def poster_canvas():
    W_, H_ = 23, 31
    cv = Cv(W_, H_)
    return cv, cv.X, cv.Y, (cv.X < 22) & (cv.Y < 30)


def poster_finish(cv, X, Y, m, seed, tapes=((0, 0), (19, 0)), torn=None):
    """Paper edge, curl shadow (right/bottom), sun-faded top, tape pieces, a torn corner."""
    if torn is not None:
        tx, ty = torn
        m = m & ~((X >= tx) & (Y >= ty) & (X - tx + Y - ty >= 3))
    sh = (~m) & (nb(m, 1, 1, False) | nb(m, 0, 1, False) | nb(m, 1, 0, False)) & (X >= 1) & (Y >= 1)
    cv.a = np.where(m, 255, 0)
    cv.col('#000000', sh, a=90)
    cv.tint('#e8e0d0', np.where(m & (Y < 6), 0.08 * (6 - Y) / 6.0, 0))
    cv.tint('#5a4a30', np.where(m & (vnoise(23, 31, 4, 5, seed) > 0.7), 0.1, 0))
    for (x, y) in tapes:
        cv.put(Ramp('#8a8166', '#b5ac8c', '#d2caa8'), np.full((31, 23), 1) + (Y == y), rect(x, y, x + 2, y + 1, X, Y) & m, a=220)
    return cv.out()


def poster_frag():
    """Shooter: dusk sky, a helmeted soldier aiming, a muzzle flash, 'FRAG' in big letters with a red drop shadow."""
    cv, X, Y, m = poster_canvas()
    sky = Ramp('#0e1e26', '#163038', '#24464a', '#5a4a3a', '#b0602a', '#e08a3a')
    cv.put(sky, np.clip(5 - (Y - 8) // 4, 0, 5), m)
    cv.col('#141414', m & (Y >= 26 - (np.abs(X - 11) < 6)))                       # rubble skyline
    SOLD = ['....###.......', '...#####......', '...#.o.#......', '....###.......', '..######......', '.#############',
            '########=.....', '.######.......', '..#####.......', '..##..##......', '.##....##.....', '.##.....##....']
    sm = np.zeros((31, 23), bool)
    stamp(sm, ascii_mask(SOLD, '#=o'), 3, 13)
    cv.col('#0a0a0c', sm & m)
    gm = np.zeros((31, 23), bool)
    stamp(gm, ascii_mask(SOLD, 'o'), 3, 13)
    cv.col('#3affd8', gm)                                                          # night-vision goggle glint
    fl = ((X - 18) ** 2 + (Y - 18) ** 2 <= 3) & m
    cv.col('#ffd060', fl)
    cv.col('#fff4c0', (X == 18) & (Y == 18))
    t = condensed_mask('FRAG')
    tm = np.zeros((31, 23), bool)
    stamp(tm, t, (22 - t.shape[1]) // 2, 2)
    cv.col('#b01818', nb(tm, 1, 1, False) & ~tm & m)
    cv.col('#f4f0e6', tm)
    cv.col('#f4f0e6', m & (Y == 28) & (X >= 3) & (X <= 18) & (X % 2 == 0))         # small print
    return poster_finish(cv, X, Y, m, 7650)


def poster_anime():
    """Anime: pastel pink field with speed lines, a heroine with spiky blue hair and huge teal eyes, vertical title."""
    cv, X, Y, m = poster_canvas()
    cv.put(Ramp('#d86a9a', '#e88ab0', '#f2aac6', '#f8c8da'), np.full((31, 23), 2) + ((X * 3 + Y) % 11 == 0) - ((X - Y) % 13 == 0), m)
    FACE = ['...#.##.#.....', '..##########..', '.############.', '###ssssssss###', '##ssssssssss##', '#sEEssssssEEs#',
            '#sEWssssssEWs#', '.sEEssssssEEs.', '.sssssssssss..', '..sssssmssss..', '...ssssssss...', '....ssssss....', '.....ssss.....']
    cols = {'#': '#22306a', 's': '#f4d8c4', 'E': '#1aa8a0', 'W': '#ffffff', 'm': '#c04060'}
    for ch, c_ in cols.items():
        fm = np.zeros((31, 23), bool)
        stamp(fm, ascii_mask(FACE, ch), 2, 7)
        cv.col(c_, fm & m)
    cv.col('#3a4a9a', m & (Y == 7) & (X >= 4) & (X <= 13) & (X % 3 == 0))         # hair highlights
    for k in range(4):                                                             # vertical title, invented glyphs
        y = 3 + k * 6
        cv.col('#1a1020', m & (X >= 18) & (X <= 20) & ((Y == y) | (Y == y + 3)))
        cv.col('#1a1020', m & (X == 19 + (k % 2) - (k == 3)) & (Y >= y) & (Y <= y + 4))
    cv.col('#ffffff', m & (Y == 27) & (X >= 3) & (X <= 15))
    return poster_finish(cv, X, Y, m, 7660, tapes=((0, 0), (19, 0), (0, 27)))


def poster_club():
    """The neighbourhood football club (invented): Club Atletico Villa Esperanza, 'C.A.V.E.', orange and black
    stripes on the shield, a star for the one title, the date of the promotion they still talk about."""
    cv, X, Y, m = poster_canvas()
    cv.put(Ramp('#c8c0a8', '#dcd4bc', '#ece6d2'), np.full((31, 23), 1) + (vnoise(23, 31, 5, 6, 7671) > 0.6), m)
    sh = (np.abs(X - 10.5) <= 7.5 - np.clip(Y - 19, 0, 9) * 0.8) & (Y >= 6) & (Y <= 27)
    cv.col('#141414', sh & m)
    inner = erode(sh, 1, False)
    cv.col('#e0701e', inner & ((X // 2) % 2 == 0))
    cv.col('#1a1a1a', inner & ((X // 2) % 2 == 1))
    band = inner & (Y >= 11) & (Y <= 17)
    cv.col('#f4ece0', band)
    t = tiny_mask('CAVE')[1:]
    tm = np.zeros((31, 23), bool)
    stamp(tm, t, 11 - t.shape[1] // 2, 12)
    cv.col('#141414', tm)
    STAR = ['..#..', '.###.', '#####', '.#.#.']
    st = np.zeros((31, 23), bool)
    stamp(st, ascii_mask(STAR), 9, 1)
    cv.col('#d8a828', st & m)
    cv.col('#141414', m & (Y == 28) & (X >= 4) & (X <= 17) & (X % 3 != 2))
    return poster_finish(cv, X, Y, m, 7670, torn=(19, 26))


def poster_pibe():
    """Streamer merch: black, a neon green wolf head with headphones, 'PIBE' 'GG' in magenta, a red LIVE tag."""
    cv, X, Y, m = poster_canvas()
    cv.put(Ramp('#06060a', '#0c0c14', '#14141e'), np.full((31, 23), 1) + ((X + Y) % 5 == 0), m)
    WOLF = ['#.........#', '##.......##', '###.....###', '.#########.', 'h##o###o##h', 'h#########h', '.#########.',
            '..#######..', '...#####...', '....###....']
    for ch, c_ in (('#', '#2aff6a'), ('o', '#06060a'), ('h', '#b0b0c0')):
        wm = np.zeros((31, 23), bool)
        stamp(wm, ascii_mask(WOLF, ch), 6, 4)
        cv.col(c_, wm & m)
    cv.col('#0e8a3a', m & (Y == 13) & (X >= 9) & (X <= 13))
    for txt, yy in (('PIBE', 16), ('GG', 22)):
        t = tiny_mask(txt)[1:]
        t = np.repeat(t, 1, 0)
        tm = np.zeros((31, 23), bool)
        stamp(tm, t, (22 - t.shape[1]) // 2, yy)
        cv.col('#7a1a5a', nb(tm, 1, 1, False) & ~tm & m)
        cv.col('#ff3ab8', tm)
    cv.col('#e01818', m & rect(15, 26, 20, 28, X, Y))
    cv.col('#ffffff', m & (Y == 27) & (X >= 16) & (X <= 19) & (X % 2 == 0))
    return poster_finish(cv, X, Y, m, 7680, tapes=((0, 0), (19, 0), (19, 27)))


# =============================================================================================== SALT CIRCLES
# Floor decals, radius ~2.8 blocks around a block CORNER, built from 6 pieces per quarter that you rotate with
# 'facing'. For a circle centred on the corner shared by blocks (cx-1..cx) x (cz-1..cz) (i.e. at world x = cx,
# z = cz), place piece p = (i, j) of SAL_PIECES four times:
#     facing north at (cx + i, cz + j)      facing east at (cx - 1 - j, cz + i)
#     facing south at (cx - 1 - i, cz - 1 - j)   facing west at (cx + j, cz - 1 - i)
# (all at the y of the air block above the floor). Old 1961 circle: outer ring, inner ring, four radial crosses at
# the cardinal points, ticks between the rings, candle wax at the diagonals. Patio: the Nona's thick poured line.
SAL_PIECES = {'a': (0, 2), 'b': (1, 2), 'c': (2, 2), 'd': (2, 1), 'e': (2, 0), 'f': (1, 1)}


def sal_painter(kind, i, j, broken=False):
    def p(face, w, h, part):
        x, y, z = face_coords(part, face, w, h)
        qx, qz = 16.0 * i + x, 16.0 * j + z
        r = np.sqrt(qx * qx + qz * qz)
        th = np.arctan2(qz, qx)
        gi, gj = np.floor(qx * 2), np.floor(qz * 2)
        g = _hash01(gi, gj, 7 if kind == 'patio' else 3)
        g2 = _hash01(gi + 31, gj - 17, 11)
        cv = Cv(w, h)
        if kind == 'patio':
            R = 44.0 + 0.8 * np.sin(8 * th + 0.5) + 0.5 * np.sin(20 * th + 2.0)
            hw = 2.1 + 0.6 * np.sin(12 * th + 1.1) + 0.35 * np.sin(28 * th)
            heap = np.clip((np.sin(12 * th + 0.3) - 0.86) / 0.14, 0, 1)
            hw = hw + heap * 1.2
            dr = r - R
            core = np.abs(dr) < hw
            edge = (np.abs(dr) >= hw) & (np.abs(dr) < hw + 1.5) & (g < 0.45)
            scat = (np.abs(dr) >= hw + 1.5) & (np.abs(dr) < hw + 6) & (g < 0.05)
            idx = 3 + (g > 0.72) - (g < 0.14) + heap * (np.abs(dr) < hw * 0.5) - ((dr > hw * 0.4) & (heap > 0.2))
            cv.put(SALT, idx, core)
            cv.put(SALT, np.full((h, w), 2) + (g2 > 0.5), edge | scat)
            wet = (np.sin(4 * th * 5 + 2.2) * 0.5 + np.sin(4 * th * 9) * 0.5) > 0.72
            cv.a = np.where(core & wet, 175, cv.a)
            cv.tint('#7a7462', np.where(core & wet, 0.3, 0))
            return cv.out()
        # old 1961 circle: compacted, yellowed, mixed with sand, broken in places
        R = 44.0 + 0.4 * np.sin(8 * th + 1.0)
        hw = 1.85 + 0.35 * np.sin(16 * th + 0.4)
        gap = (0.6 * np.sin(12 * th + 1.3) + 0.4 * np.sin(28 * th + 0.4)) > 0.8
        outer = (np.abs(r - R) < hw) & ~(gap & (g < 0.75))
        inner = (np.abs(r - 37.0) < 0.95) & ~(gap & (g < 0.5)) & (g2 > 0.12)
        ticks = np.zeros((h, w), bool)
        for kk in range(1, 6):
            a = math.radians(15 * kk)
            ticks |= (np.abs(r * np.sin(th - a)) < 0.5) & (r > 38.6) & (r < 42.6)
        cross = np.zeros((h, w), bool)
        for (rho, tau) in ((qx - 40.5, qz), (qz - 40.5, -qx)):
            cross |= ((np.abs(tau) < 0.55) & (rho > -3.2) & (rho < 2.2)) | ((np.abs(rho - 0.9) < 0.55) & (np.abs(tau) < 1.8))
        dg = math.radians(45)
        wx, wz = 40.5 * math.cos(dg), 40.5 * math.sin(dg)
        dw = np.sqrt((qx - wx) ** 2 + (qz - wz) ** 2) + (_hash01(gi, gj, 5) - 0.5) * 0.5
        wax = dw < 1.9
        drips = (dw < 3.2) & (np.abs(np.sin(np.arctan2(qz - wz, qx - wx) * 5)) > 0.9) & ~wax
        salt = outer | inner | ticks | cross
        if broken:
            cut = np.abs(th - math.radians(75)) < math.radians(3.5)
            drag = (np.abs(th - math.radians(76)) < math.radians(2.5)) & (r > 30) & (r < 56) & (g < 0.18)
            salt = (salt & ~cut) | drag
        idx = 3 + (g > 0.7) - (g < 0.2) - (g2 > 0.8) * 2
        cv.put(SALT_OLD, idx, salt)
        cv.put(SALT_OLD, np.full((h, w), 1), (np.abs(r - R) < hw + 1.2) & ~salt & (g < 0.18))
        cv.put(WAX, np.full((h, w), 3) + (dw < 1.0) - (dw > 1.5), wax)
        cv.col('#1a1410', dw < 0.35)
        cv.put(WAX, np.full((h, w), 2), drips)
        return cv.out()
    return p


def sal_parts(kind, piece, broken=False):
    i, j = SAL_PIECES[piece]
    return [PL((0, 0.06, 0), (16, 0.06, 16), sal_painter(kind, i, j, broken), faces=('up',), name='salt')]


# =============================================================================================== BASEMENT WINDOW
def cobweb_paint(face, w, h, part, cv):
    x, y, z = face_coords(part, face, w, h)
    cx, cy = part.to[0], part.to[1]          # anchored in the upper corner (+x, top)
    dx, dy = cx - x, cy - y
    r = np.sqrt(dx * dx + dy * dy)
    ang = np.arctan2(dy, dx)
    radial = np.abs(np.sin(ang * 7)) < 0.12
    spiral = np.abs(((r + ang * 0.35) % 1.1) - 0.55) < 0.09
    m = (radial | spiral) & (r < 4.2)
    cv.col('#c8c4ba', m, a=150)
    cv.a = np.where(m, cv.a, 0)


def ventana_sotano_parts():
    """Basement window (ventiluz) at the top of a basement wall, at patio level outside: a slot with three iron bars,
    a dirty wired-glass pane with a broken corner, dead leaves on the outer sill, a cobweb inside. Replaces the top
    wall block; facing = the patio (exterior)."""
    wp = wall_face_painter(ext='revoque_humedad', inn='pared_sotano', split=(7.0, 9.0))
    it = pp_iron(seed=9700, rust=0.55)
    parts = [P((0, 0, 0), (3, 16, 16), wp, name='jamb_l'), P((13, 0, 0), (16, 16, 16), wp, name='jamb_r'),
             P((3, 0, 0), (13, 4, 16), wp, name='sill'), P((3, 11, 0), (13, 16, 16), wp, name='lintel'),
             P((3, 4, 7), (13, 5, 9), it, name='frame_b'), P((3, 10, 7), (13, 11, 9), it, name='frame_t'),
             P((3, 5, 7), (4, 10, 9), it, name='frame_l'), P((12, 5, 7), (13, 10, 9), it, name='frame_r'),
             P((7.6, 5, 7.4), (8.4, 10, 8.6), it, name='mullion'),
             PL((4, 5, 8), (12, 10, 8), pp_glass(seed=9701, alpha=170, dirt=1.1, crack=(3, 3)), name='glass')]
    for xb in (5.6, 8.0, 10.4):
        parts.append(P((xb - 0.45, 4, 1.2), (xb + 0.45, 11, 2.1), it, name='bar'))
    leaf = pp_fn(lambda face, w, h, part, cv: cv.put(Ramp('#2a1a0e', '#3e2814', '#58381a', '#6e4a22'), np.full((h, w), 2)
                                                     + (vnoise(w, h, max(1, w // 2), max(1, h // 2), fkey(part, face)) > 0.55)))
    for (lx, lz, ang) in ((4.0, 0.6, 22.5), (8.5, 2.6, -22.5), (10.6, 0.4, 45)):
        parts.append(P((lx, 4.0, lz), (lx + 2.2, 4.25, lz + 1.4), leaf, rot=('y', ang, (lx + 1.1, 4.0, lz + 0.7)), name='leaf'))
    parts.append(PL((8.6, 6.0, 12.0), (12.9, 10.9, 12.0), pp_fn(cobweb_paint), faces=('north', 'south'), name='web'))
    return parts


# =============================================================================================== REGISTRATION (batch F)
cube('pared_sotano', 'Pared del sótano', 'Basement wall', 'pared_sotano', VAR)
cube('pared_sotano_zocalo', 'Pared del sótano (pie húmedo)', 'Basement wall (damp foot)', 'pared_sotano_zocalo', 2, up='pared_sotano', down='pared_sotano')
cube('pared_sotano_ladrillo', 'Ladrillo viejo del sótano', 'Old basement brick', 'sotano_ladrillo', 3, sound='stone')
cube('pared_sotano_grieta_arriba', 'Pared rajada (arriba)', 'Cracked wall (top)', 'grieta_arriba', 1, up='pared_sotano', down='pared_sotano')
cube('pared_sotano_grieta', 'Pared rajada (medio)', 'Cracked wall (middle)', 'grieta', 1, up='pared_sotano', down='pared_sotano')
cube('pared_sotano_grieta_abajo', 'Pared rajada (abajo, con arena)', 'Cracked wall (bottom, sand spilling)', 'grieta_abajo', 1, up='pared_sotano', down='pared_sotano')
for _k, _es, _en in (('izq_abajo', 'jamba izquierda, abajo', 'left jamb, bottom'), ('izq_arriba', 'jamba izquierda, arriba', 'left jamb, top'),
                     ('dintel_izq', 'dintel izquierdo', 'left lintel'), ('dintel_der', 'dintel derecho', 'right lintel'),
                     ('der_arriba', 'jamba derecha, arriba', 'right jamb, top'), ('der_abajo', 'jamba derecha, abajo', 'right jamb, bottom')):
    F(f'boquete_{_k}', f'Pared rota por la Nona ({_es})', f'Broken-through wall ({_en})', boquete_parts(_k), sound='stone')
F('escombros', 'Escombros', 'Rubble', escombros_parts(), collision='none', sound='stone')
F('escombros_arena', 'Escombros con arena', 'Rubble with spilled sand', escombros_parts(arena=True), collision='none', sound='sand')
F('ventana_sotano', 'Ventiluz del sótano', 'Basement window', ventana_sotano_parts(), render='translucent', sound='glass')
cube('pared_61', 'Pared del cuarto del 61', 'Wall of the 1961 room', 'pared_61', VAR)
cube('pared_61_zocalo', 'Pared del cuarto del 61 (pie)', 'Wall of the 1961 room (foot)', 'pared_61_zocalo', 2, up='pared_61', down='pared_61')
cube('pared_61_hollin', 'Pared del 61 con hollín de vela', 'Wall of the 1961 room with candle soot', 'pared_61_hollin', 1, up='pared_61', down='pared_61')
cube('pared_61_hollin_alto', 'Pared del 61 con hollín (arriba)', 'Wall of the 1961 room with soot (upper)', 'pared_61_hollin_alto', 1, up='pared_61', down='pared_61')
_DEC = dict(collision='none', sound='plaster', render='translucent')
F('rayones_lemaza', 'Rayones "LEMAZA" (3 bloques)', "Scratches 'LEMAZA' (3 blocks wide)", wall_decal('rayones_lemaza', img_lemaza, 48, 24, y0=2.0), **_DEC)
F('rayones_lemaza_chico', 'Rayones "LEMAZA" (chico)', "Scratches 'LEMAZA' (small)", wall_decal('rayones_lemaza_chico', img_lemaza_chico, 16, 16, y0=3.0), **_DEC)
F('rayones_dibujo', 'Rayones: dibujo "MI AMIGO" (2 bloques)', "Scratched drawing 'MI AMIGO' (2 blocks)", wall_decal('rayones_dibujo', img_dibujo, 32, 16, y0=2.0), **_DEC)
F('rayones_palitos', 'Rayones: días contados', 'Scratched tally of days', wall_decal('rayones_palitos', img_palitos, 16, 16, y0=4.0), **_DEC)
F('rayones_latin', 'Rayones en latín (3 bloques)', 'Latin scratched by the priest (3 blocks)', wall_decal('rayones_latin', img_latin, 48, 24, y0=4.0), **_DEC)
F('rayones_latin_brillo', 'Rayones en latín, encendidos', 'Latin scratches, glowing', wall_decal('rayones_latin_brillo', lambda: img_latin(True), 48, 24, y0=4.0, shade=False),
  light=7, **_DEC)
F('manos_hollin', 'Manitos de hollín', 'Small sooty handprints', wall_decal('manos_hollin', img_manos, 16, 16, y0=4.0), **_DEC)
F('mancha_humedad', 'Mancha de humedad (2x2)', 'Damp stain (2x2)', wall_decal('mancha_humedad', img_humedad, 32, 32, x0=-8.0, y0=0.0), **_DEC)
F('mancha_humedad_cara', 'Mancha de humedad con cara (2x2)', 'Damp stain with a face (2x2)', wall_decal('mancha_humedad_cara', lambda: img_humedad(True), 32, 32, x0=-8.0, y0=0.0),
  **_DEC)
for _k, (_fn, _es, _en) in enumerate(((poster_frag, 'shooter FRAG', "shooter 'FRAG'"), (poster_anime, 'anime', 'anime heroine'),
                                       (poster_club, 'del club C.A.V.E.', 'the local football club'), (poster_pibe, "del streamer 'Pibe GG'", "streamer 'Pibe GG'")), 1):
    F(f'poster_toti_{_k}', f'Póster de Toti ({_es})', f"Toti's poster ({_en})", wall_decal(f'poster_toti_{_k}', _fn, 11.5, 15.5, y0=0.5),
      collision='none', sound='paper', render='cutout')
for _kind, _es, _en in (('61', 'Círculo de sal viejo', 'Old salt circle'), ('patio', 'Círculo de sal de la Nona', "Nona's salt circle")):
    for _p in SAL_PIECES:
        F(f'sal_{_kind}_{_p}', f'{_es} (pieza {_p})', f'{_en} (piece {_p})', sal_parts(_kind, _p), collision='none', sound='sand', render='translucent')
F('sal_61_a_rota', 'Círculo de sal viejo (pieza a, cortada)', 'Old salt circle (piece a, broken)', sal_parts('61', 'a', broken=True),
  collision='none', sound='sand', render='translucent')


def divisoria_parts(front='pared_sotano', back='pared_61', vf=0, vb=0):
    """The wall between the basement and the sealed room is one block thick, so its plain blocks need two faces:
    an in-wall full block with the basement plaster on the 'facing' side and the 1961 lime wash on the other."""
    pf, pb = aligned(T(front, vf)), aligned(T(back, vb))

    def p(face, w, h, part):
        return pb(face, w, h, part) if face == 'south' else pf(face, w, h, part)
    return [P((0, 0, 0), (16, 16, 16), p, name='wall')]


F('pared_divisoria', 'Pared sótano / cuarto del 61', 'Basement / 1961 room dividing wall', divisoria_parts(), collision='full', sound='stone')
F('pared_divisoria_b', 'Pared sótano / cuarto del 61 (rajada)', 'Basement / 1961 room dividing wall (hairline cracks)', divisoria_parts(vf=8, vb=8),
  collision='full', sound='stone')
F('pared_divisoria_zocalo', 'Pared sótano / cuarto del 61 (pie)', 'Basement / 1961 room dividing wall (foot)',
  divisoria_parts('pared_sotano_zocalo', 'pared_61_zocalo'), collision='full', sound='stone')
