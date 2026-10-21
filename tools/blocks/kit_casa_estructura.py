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
  * stairs and handrails, the basement (crumbling wall, the crack, the wall the Nona breaks through, rubble) and the 1961
    room (sooty lime walls, the children's scratches LEMAZA, the old salt circle), the patio salt circle.

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
        # reflection streaks (two parallel diagonals)
        dgn = (X + Y * 1.0) % max(8, (w + h) // 2)
        st = (dgn >= 2) & (dgn <= 3) | (dgn == 6)
        st &= (X + Y) < (w + h) * 0.6
        idx = np.where(st, 7, idx)
        a = np.where(st, alpha + 70, a)
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
    """Exposed machine brick of the 1950s facade. v1: soot/rain darkening, v2: stepped crack along the joints,
    v3: an old wall plug and a rusty nail with a streak."""
    cv = Cv()
    lab, joint = paint_brick_fine(cv, v)
    X, Y = cv.X, cv.Y
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
    return lime_idx(v, base=6, seed=seed, rough=rough)


@painter('revoque_blanco')
def p_revoque_blanco(v):
    """White painted lime render of the chalet. v1 rain streaks, v2 crazing crack, v3 a patched repair."""
    cv = Cv()
    idx = render_idx(v, seed=200)
    X, Y = cv.X, cv.Y
    if v == 2:
        idx, _ = crack_line(idx, [(8, 4), (12, 11), (10, 19), (16, 27)], 6301, amp=2.5)
        idx, _ = crack_line(idx, [(12, 11), (20, 14), (25, 13)], 6302, amp=1.5, dark=2)
    if v == 3:   # rectangular-ish repair: smoother, slightly warmer, trowel edge
        pm = blob(N, N, 17, 15, 9, 7, 6310, rough=0.25, cells=2)
        idx = np.where(pm, 6 + posterize(fbm(N, N, 6311, cells=8, octaves=1), [(0.7, 1)]), idx)
        pr = rim(pm, wrap=False)
        idx = idx + np.where(pr['in_top'] | pr['in_left'], 1, 0) - np.where(pr['out_below'], 1, 0)
    cv.put(RENDER_W, idx)
    if v == 1:   # rain streaks hanging from above (grouped thin lines, broken)
        rng = np.random.default_rng(6320)
        for x in rng.choice(np.arange(3, 29), 7, replace=False):
            L = int(rng.integers(10, 28))
            y0 = int(rng.integers(0, 6))
            m = (X == x) & (Y >= y0) & (Y < y0 + L) & (fbm(N, N, 6321 + int(x), cells=8, octaves=1) > 0.25)
            cv.tint('#6a6a5a', np.where(m, 0.30, 0))
        cv.tint('#7a7866', np.where(fbm(N, N, 6330, cells=2, octaves=2, ax=4, ay=0.5) > 0.6, 0.12, 0))
    if v == 3:
        cv.tint('#cfc6b0', np.where(pm, 0.18, 0))
    return cv.out()


@painter('revoque_humedad')
def p_revoque_humedad(v):
    """Rising damp in the white render (bottom course): grey-green tide with darker lines, algae, mould specks."""
    cv = Cv()
    idx = render_idx(v + 10, seed=200)
    cv.put(RENDER_W, idx)
    X, Y = cv.X, cv.Y
    base = [17, 13, 19][v % 3]
    wave = base + np.round(3 * np.sin((X + 4 + v * 7) / 32 * 2 * math.pi) + 1.4 * np.sin((X * 2 + 13) / 32 * 2 * math.pi)).astype(int)
    f = (Y - wave) / 10.0 + (fbm(N, N, 6400 + v, cells=4, octaves=3) - 0.5) * 0.5
    damp = f > 0
    t = np.clip(0.35 + f * 0.6, 0, 0.85)
    cv.tint('#4a4c3e', np.where(damp, t, 0))
    tide = damp & ~nb(damp, 1, 0)
    cv.tint('#3a3a2c', np.where(tide, 0.55, 0))
    cv.tint('#4a4a3a', np.where(nb(tide, -2, 0) & damp, 0.25, 0))
    alg = damp & (f > 0.6) & (fbm(N, N, 6402 + v, cells=8, octaves=2) > 0.55)
    cv.tint('#3a4a24', np.where(alg, 0.45, 0))
    mould_specks(cv, 6405 + v, 3, keep=lambda x, y: 0 < f[int(y), int(x)] < 0.8)
    salt_bloom(cv, (Y < wave) & (Y > wave - 4), 6408 + v, strength=0.3, density=0.3)
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
    wave = top + 9 + np.round(1.5 * np.sin((X + 5 * v + seed) / 32 * 2 * math.pi * 2)).astype(int)
    tide = (Y == wave)
    cv.tint('#1e2018', np.where(tide, 0.35, 0))
    salt_bloom(cv, m & (Y > top + 1) & (Y < wave) & (Y > wave - 5), 6510 + seed + v, strength=0.7, density=0.45)
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


@painter('medianera')
def p_medianera(v):
    """Neighbour's party wall: coarse grey cement render, newer plaster patches, hollow brick where it fell,
    rust streak from an old bracket."""
    cv = Cv()
    X, Y = cv.X, cv.Y
    idx = np.full((N, N), 4) + posterize(cblend(fbm(N, N, 6600, cells=2, octaves=3), fbm(N, N, 6601 + v, cells=2, octaves=3)), [(0.75, 1), (0.22, -1)])
    idx = relief(idx, 6602, 6603 + v, count=46, mind=3.0, body=-1, light=1)
    cv.put(CEMENT, idx)
    if v == 1:   # two newer patches: smoother, lighter, thick edge with a shadow under it
        for k, (cx, cy, rx, ry) in enumerate(((11, 11, 7.5, 6), (23, 22, 6, 5.5))):
            pm = flake(cx, cy, rx, ry, 6610 + k, jag=0.25) & (border_dist(N, N) > 1)
            pidx = np.full((N, N), 5 + (k == 0)) + posterize(fbm(N, N, 6611 + k, cells=4, octaves=2), [(0.72, 1), (0.3, -1)])
            pr = rim(pm, wrap=False)
            pidx = pidx + pr['in_top'] - pr['in_bot'] - pr['in_right']
            cv.put(CEMENT, pidx, pm)
            cv.put(CEMENT, np.full((N, N), 1), pr['out_below'] | pr['out_right'])
            cv.tint('#d0cab8', np.where(pm, 0.08, 0))
    if v == 2:   # render fallen: ladrillo hueco (hollow clay block) with its channels
        H = flake(15, 17, 9, 6.5, 6620, jag=0.45) & (border_dist(N, N) > 2)
        HUE = Ramp('#3d1a10', '#5a2716', '#77351d', '#904426', '#a65532', '#b8673f')
        hl = (Y % 12 == 11) | ((X + (Y // 12) * 9) % 20 == 19)
        hidx = np.full((N, N), 3) + ((Y % 12) == 0) - ((Y % 12) == 10)
        holes = (((Y % 12) >= 3) & ((Y % 12) <= 4) | ((Y % 12) >= 7) & ((Y % 12) <= 8)) & ((X % 5) <= 2) & ~hl
        cv.put(HUE, hidx, H & ~hl)
        cv.put(HUE, np.full((N, N), 0), H & holes)
        cv.put(MORTAR, np.full((N, N), 3), H & hl)
        r = rim(H, wrap=False)
        cv.put(CEMENT, np.full((N, N), 1), r['in_top'] | r['in_left'])
        cv.put(CEMENT, np.full((N, N), 6), r['out_below'] | r['out_right'])
    if v == 3:   # rust streak from a bracket and a mossy foot
        cv.put(IRON, np.full((N, N), 3) + (Y == 6), rect(13, 6, 16, 7))
        st = (np.abs(X - 14.5) < 1.2 + (Y - 8) / 18) & (Y > 7)
        cv.tint('#6a3a1c', np.where(st, 0.45 * (1 - (Y - 8) / 30), 0))
        mo = (Y > 24) & (fbm(N, N, 6630, cells=8, octaves=2) > 0.5)
        cv.put(MOSS, np.full((N, N), 2), mo)
    return cv.out()


# =============================================================================================== INTERIOR: painted walls
def latex_idx(v, seed):
    """Látex over smooth plaster: softer than lime, a faint roller stipple."""
    idx = lime_idx(v, base=6, seed=seed, rough=0.35)
    st = (fbm(N, N, seed + 77, cells=16, octaves=1) > 0.82) & ((G_X + G_Y) % 3 == 0)
    idx = idx + np.where(st, 1, 0)
    return 6.0 + (idx - 6) * 0.4     # soft: clusters stay crisp but only 0.4 of a ramp step apart


def finger_drag(cv, x0, y0, seed, color='#2a2420', amount=0.22, length=14):
    """Four dirty finger trails sliding down the wall (someone feeling their way in the dark)."""
    X, Y = cv.X, cv.Y
    m = np.zeros((N, N), bool)
    for k in range(4):
        pts = wander([(x0 + k * 2, y0 + abs(k - 1.5)), (x0 + k * 2 + 3, y0 + length + (k % 2))], seed + k, amp=0.7, depth=2)
        m |= path_mask(pts, wrap=False)
    fade = np.clip(1 - (Y - y0) / (length + 2.0), 0.25, 1)
    cv.tint(color, np.where(m, amount * fade, 0))


def room_wall(ramp, v, seed, extra=None):
    """Generic room wall: v0 clean, v1 picture ghost + nail, v2 hairline crack, v3 grime + finger trails."""
    cv = Cv()
    idx = latex_idx(v, seed)
    X, Y = cv.X, cv.Y
    if v == 1:
        idx = ghost_frame(idx, 7, 10, 24, 25, k=0.6)
    if v == 2:
        idx, _ = crack_line(idx, [(22, 3), (19, 10), (21, 17), (15, 25), (16, 29)], seed + 11, amp=2.0, dark=2, lip=0.6)
    cv.put(ramp, idx)
    if v == 3:
        hm = (fbm(N, N, seed + 21, cells=4, octaves=2) > 0.55) & (Y > 8) & (Y < 26)
        cv.tint('#3a3024', np.where(hm, 0.07, 0))
        finger_drag(cv, 9, 9, seed + 30)
    if extra:
        extra(cv, v)
    return cv


def room_wall_zocalo(ramp, v, seed, wood=CEDRO):
    cv = Cv()
    idx = latex_idx(v + 40, seed)
    cv.put(ramp, idx)
    grime_band(cv, 18, 26, amount=0.18, seed=seed)
    skirting(cv, wood, top=25, seed=seed + v, chips=v, scuffs=2 + 2 * v)
    return cv


@painter('pared_living')
def p_pared_living(v):
    return room_wall(BEIGE, v, 7100).out()


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
    if v == 3:   # dog rub: Choripán's greasy brown smear along the hall, low, with hair-like streaks
        X, Y = cv.X, cv.Y
        n = fbm(N, N, 7230, cells=2, octaves=3, ax=0.25, ay=2)
        band = np.clip(1 - np.abs(Y - 25) / 4.0, 0, 1) * np.clip((n - 0.25) * 2, 0, 1)
        hair = fbm(N, N, 7231, cells=16, octaves=1, ax=0.25, ay=4) > 0.6
        cv.tint('#4a3824', band * (0.28 + 0.12 * hair))


@painter('pared_pasillo')
def p_pared_pasillo(v):
    return room_wall(AQUA, v, 7200, hall_extra).out()


@painter('pared_pasillo_zocalo')
def p_pared_pasillo_zocalo(v):
    return room_wall_zocalo(AQUA, v, 7200).out()


def kitchen_extra(cv, v):
    X, Y = cv.X, cv.Y
    rng = np.random.default_rng(7330 + v)
    if v == 1:   # grease splatter: clusters of small amber specks + a drip run
        for (cx, cy) in poisson(7331, 3, 9, keep=lambda x, y: 4 < x < 28 and 4 < y < 24):
            for k in range(14):
                x = int(round(cx + rng.normal(0, 2.4)))
                y = int(round(cy + rng.normal(0, 2.0)))
                if 1 <= x < 31 and 1 <= y < 31:
                    cv.tint('#7a5a1a', np.where((X == x) & (Y == y), 0.35 + 0.2 * rng.random(), 0))
            cv.tint('#7a5a1a', np.where((X == cx) & (Y > cy) & (Y < cy + 7), 0.22, 0))
        cv.tint('#9a8040', np.where(fbm(N, N, 7332, cells=2, octaves=2) > 0.5, 0.1, 0))
    if v == 2:   # soot cloud above the stove
        f = 1 - np.sqrt(((X - 16) / 16.0) ** 2 + ((Y - 30) / 26.0) ** 2) + (fbm(N, N, 7340, cells=4, octaves=3) - 0.5) * 0.5
        cv.tint('#2c2620', np.clip(f, 0, 1) * 0.55)


@painter('pared_cocina')
def p_pared_cocina(v):
    return room_wall(KCREAM, v, 7300, kitchen_extra).out()


def bath_extra(cv, v):
    X, Y = cv.X, cv.Y
    if v in (1, 3):   # black mould specks from the steam, thicker near the ceiling
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
def p_empapelado_nona(v):
    """Faded floral wallpaper of the Nona's room (sepia-green ground, stripes, roses in half-drop).
    v1 lifting seam (with the plaster behind), v2 water stain, v3 unfaded ghost where the crucifix hung."""
    cv = nona_paper(v)
    X, Y = cv.X, cv.Y
    if v == 1:
        seam = (X == 16)
        cv.put(NONA_BG, np.full((N, N), 1), seam & (Y < 22))
        lift = (X >= 13) & (X <= 15) & (Y >= 6) & (Y <= 14) & (X - 13 >= (Y - 6) // 4)
        cv.put(WHITEP, np.full((N, N), 4), (X >= 13) & (X <= 15) & (Y >= 6) & (Y <= 14))   # plaster behind
        cv.put(NONA_BG, np.full((N, N), 2), lift)
        cv.put(NONA_BG, np.full((N, N), 6), (X == 12) & (Y >= 6) & (Y <= 14))          # curled lip
        cv.tint('#000000', np.where((X == 11) & (Y >= 7) & (Y <= 15), 0.3, 0))
    if v == 2:
        st = blob(N, N, 15, 13, 11, 9, 7720, rough=0.4) & (border_dist(N, N) > 1)
        cv.tint('#7a5a2a', np.where(st, 0.3, 0))
        cv.tint('#4a3016', np.where(st & ~erode(st, 1, False), 0.5, 0))
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
    return cv


@painter('empapelado_matrimonial')
def p_empapelado_matrimonial(v):
    """v1 a vertical seam opening, v2 a sun-faded area and a damp corner."""
    cv = mat_paper(v)
    X, Y = cv.X, cv.Y
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
def p_cemento_lavadero(v):
    """Laundry room: sponge-floated grey cement render (fratachado). v1 damp + rising mould, v2 rust/water streak
    from a tap, v3 crack and a plug hole."""
    cv = Cv()
    X, Y = cv.X, cv.Y
    f = cblend(fbm(N, N, 7900, cells=2, octaves=3), fbm(N, N, 7901 + v, cells=2, octaves=3))
    idx = np.full((N, N), 4) + posterize(f, [(0.76, 1), (0.22, -1)])
    grain = fbm(N, N, 7902, cells=16, octaves=1)
    idx = idx + np.where(grain > 0.72, 1, 0) - np.where(grain < 0.2, 1, 0)
    # float arcs
    arc = np.abs(((np.sqrt((X - 40) ** 2 + (Y + 10) ** 2)) % 7) - 3) < 0.45
    idx = np.where(arc & (fbm(N, N, 7903, cells=4, octaves=1) > 0.55), idx + 1, idx)
    if v == 3:
        idx, _ = crack_line(idx, [(5, 8), (12, 12), (18, 11), (27, 19)], 7904, amp=2)
        idx[20, 9] -= 4
        idx[20, 10] -= 4
    cv.put(LAV, idx)
    if v == 1:
        t = np.clip((Y - 12) / 18.0, 0, 1) * (0.5 + 0.5 * fbm(N, N, 7910, cells=4, octaves=2))
        cv.tint('#22261c', t * 0.6)
        mo = (Y > 22) & (fbm(N, N, 7911, cells=8, octaves=2) > 0.55)
        cv.put(MOSS, np.full((N, N), 1), mo)
    if v == 2:
        st = (np.abs(X - 15 - np.sin(Y / 4.0)) < 1.4) & (Y > 2)
        cv.tint('#6a3a1a', np.where(st, 0.35, 0))
        cv.tint('#3a2a1a', np.where((np.abs(X - 15) < 4) & (Y > 20) & (fbm(N, N, 7920, cells=4, octaves=2) > 0.4), 0.25, 0))
    return cv.out()


# --- tiles
def tile_grid(ramp, v, seed, size=8, base=5, mottle=True, grout_base=3, grout_ramp=GROUT):
    cv = Cv()
    X, Y = cv.X, cv.Y
    grout = (X % size == 0) | (Y % size == 0)
    nt = N // size
    lab = np.where(grout, -1, (Y // size) * nt + X // size)
    rc = np.random.default_rng(seed)
    tone = rc.choice([-1, 0, 0, 0, 1], nt * nt)
    li = np.maximum(lab, 0)
    idx = base + tone[li]
    lx, ly = X % size, Y % size
    if mottle:
        mo = fbm(N, N, seed + 1, cells=8, octaves=2)
        idx = idx + np.where(mo > 0.7, 1, 0) - np.where(mo < 0.28, 1, 0)
    idx = np.where((ly == 1) | (lx == 1), idx + 1, idx)
    idx = np.where((ly == size - 1) | (lx == size - 1), idx - 1, idx)
    spec = (lx + ly == 4) & (lx >= 2) & (lx <= 3) & (tone[li] >= 0)
    idx = np.where(spec, idx + 3, idx)
    cv.put(ramp, idx, ~grout)
    gidx = np.full((N, N), grout_base) + posterize(fbm(N, N, seed + 2, cells=16, octaves=1), [(0.6, 1), (0.3, -1)])
    cv.put(grout_ramp, gidx, grout)
    return cv, lab, grout


def tile_wear(cv, lab, grout, v, ramp, seed, size=8):
    X, Y = cv.X, cv.Y
    if v == 1:   # dirty grout and splashes
        cv.put(GROUT, np.full((N, N), 1), grout & (fbm(N, N, seed + 10, cells=8, octaves=1) > 0.4))
        for k, (x, y) in enumerate(poisson(seed + 11, 8, 4, keep=lambda x, y: 2 < x < 30 and 2 < y < 30)):
            cv.tint('#5a4a1c', np.where(disc(x, y, 1.0 + (k % 2) * 0.6), 0.3, 0))
    if v == 2:   # cracked tile
        t0 = 2 * size + 1
        pts = wander([(t0 + 1, t0 - size + 2), (t0 + 3, t0 - size + 5), (t0 + size - 2, t0 - 2)], seed + 12, amp=0.8)
        cm = path_mask(pts, wrap=False) & ~grout
        cv.col('#1a1a14', cm)
        cv.tint('#ffffff', np.where(nb(cm, -1, 0, False) & ~cm & ~grout, 0.3, 0))
    if v == 3:   # missing tile: cement bed with the comb marks of the adhesive
        x0, y0 = size + 1, 2 * size + 1
        hole = rect(x0 - 1, y0 - 1, x0 + size - 1, y0 + size - 1)
        cidx = np.full((N, N), 3) + (((X + Y) % 3) == 0) - ((Y == y0 - 1) | (X == x0 - 1))
        cv.put(CEMENT, cidx, hole)
        r = rim(hole, wrap=False)
        cv.tint('#ffffff', np.where(r['out_below'], 0.2, 0))


@painter('azulejo_verde')
def p_azulejo_verde(v):
    """70s mottled avocado-green kitchen tiles, 4x4 per block. v1 grease, v2 crack, v3 a missing tile."""
    cv, lab, grout = tile_grid(AZV, v, 8000, base=5)
    tile_wear(cv, lab, grout, v, AZV, 8010)
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
    cv.put(GROUT, np.full((N, N), 3), grout & (Y <= 8))
    cv.put(GUARDA_BR, np.full((N, N), 1), (Y == 4) & (X % 8 == 0))   # the diamonds link across the joints
    return cv.out()


@painter('azulejo_celeste')
def p_azulejo_celeste(v):
    """Light-blue bathroom tiles (4x4). v1 mouldy grout, v2 crack + rust from the tap, v3 missing tile."""
    cv, lab, grout = tile_grid(AZC, v, 8100, base=5, mottle=False, grout_base=4)
    X, Y = cv.X, cv.Y
    if v == 1:
        cv.put(MOSS, np.full((N, N), 1) + (fbm(N, N, 8110, cells=16, octaves=1) > 0.6), grout & (Y > 14) & (fbm(N, N, 8111, cells=8, octaves=1) > 0.35))
        cv.put(SOOT, np.full((N, N), 2), grout & (Y > 24))
    else:
        tile_wear(cv, lab, grout, v, AZC, 8120)
    if v == 2:
        st = (np.abs(X - 22) <= 1) & (Y > 3)
        cv.tint('#7a4a22', np.where(st, 0.2 + 0.25 * (Y / 32.0), 0))
    return cv.out()


@painter('azulejo_celeste_guarda')
def p_azulejo_celeste_guarda(v):
    """Top course of the bathroom tiling: a navy listel (half-height strip tiles with a wave) over plain rows."""
    cv, lab, grout = tile_grid(AZC, v, 8130, base=5, mottle=False, grout_base=4)
    X, Y = cv.X, cv.Y
    band = (Y >= 1) & (Y <= 4) & (X % 8 != 0)
    cv.put(NAVY, np.full((N, N), 2) + (Y == 1) - (Y == 4), band)
    wave = (np.abs(Y - 2.5 - np.round(np.sin(X / 8.0 * 2 * math.pi) * 1.2)) < 0.6) & band
    cv.put(AZC, np.full((N, N), 7), wave)
    cv.put(GROUT, np.full((N, N), 4), (Y == 5) | ((Y < 5) & (X % 8 == 0)))
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
def p_parquet(v):
    """Varnished oak herringbone parquet (espina de pez), honey-brown, dulled by decades of wax."""
    cv = Cv()
    idx, lab, horiz = parquet_idx(v)
    sheen = cblend(fbm(N, N, 8220, cells=2, octaves=2), fbm(N, N, 8221 + v, cells=2, octaves=2))
    idx = idx + np.where(sheen > 0.8, 1, 0)
    cv.put(PARQ, idx)
    if v == 1:   # dark ring left by a flowerpot
        d = np.sqrt((cv.X - 15.5) ** 2 + (cv.Y - 16.5) ** 2)
        cv.tint('#1a0e06', np.where(np.abs(d - 6) < 0.8, 0.4, 0))
    if v == 2:   # scratches from dragged chairs
        for k in range(3):
            pts = line_px(4 + k * 3, 9 + k * 7, 25 + k, 11 + k * 7)
            m = path_mask(pts, wrap=False)
            cv.tint('#c8a070', np.where(m, 0.35, 0))
    return cv.out()


@painter('parquet_gastado')
def p_parquet_gastado(v):
    """Worn parquet: the varnish gone grey on the walking path, a missing strip (black bitumen), a lifted strip."""
    cv = Cv()
    idx, lab, horiz = parquet_idx(v, seed=5)
    X, Y = cv.X, cv.Y
    worn = rank(cblend(fbm(N, N, 8230, cells=2, octaves=3), fbm(N, N, 8231 + v, cells=2, octaves=3))) > 0.45
    cv.put(PARQ, idx)
    widx = np.clip(idx - 1, 0, 6)
    cv.put(PARQ_W, widx, worn & ((nb(lab, -1, 0) == lab) & (nb(lab, 0, -1) == lab)))
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
    if v == 1:   # glaze worn off in front of the sink: matte biscuit
        w = rank(fbm(N, N, 8410, cells=2, octaves=3)) > 0.62
        cv.tint('#9a8466', np.where(w & ~joint, 0.3, 0))
    if v == 2:
        pts = wander([(3, 20), (9, 22), (14, 27)], 8420, amp=0.8)
        cv.col('#2a2016', path_mask(pts, wrap=False) & ~joint)
        cv.tint('#4a3010', np.where(disc(22, 9, 3.2) & ~joint, 0.3, 0))   # spilled mate yerba stain
    return cv.out()


@painter('baldosa_patio')
def p_baldosa_patio(v):
    """Red cement patio tiles (baldosa colorada), 4x4: sun-faded unevenly, moss in the joints, a cracked one,
    v3 a tile replaced with grey cement."""
    cv = Cv()
    X, Y = cv.X, cv.Y
    joint = (X % 8 == 0) | (Y % 8 == 0)
    lab = np.where(joint, -1, (Y // 8) * 4 + X // 8)
    rc = np.random.default_rng(8500)
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
    if v == 1:
        cm = path_mask(wander([(9, 10), (12, 12), (15, 14)], 8510, amp=0.6), wrap=False) & ~joint
        cv.col('#1e0c08', cm)
    if v == 3:
        t = rect(17, 9, 23, 15)
        cv.put(CEMENT, np.full((N, N), 4) + posterize(fbm(N, N, 8520, cells=8, octaves=1), [(0.6, 1)]), t)
    return cv.out()


@painter('ladrillo_patio')
def p_ladrillo_patio(v):
    """Brick paving laid flat in basket weave (pairs alternating direction), sandy joints with moss."""
    cv = Cv()
    X, Y = cv.X, cv.Y
    cx, cy = X // 16, Y // 16
    lx, ly = X % 16, Y % 16
    horiz = (cx + cy) % 2 == 0
    sub = np.where(horiz, ly // 8, lx // 8)
    joint = np.where(horiz, (ly % 8 == 7) | (lx == 15), (lx % 8 == 7) | (ly == 15))
    lab = np.where(joint, -1, (cy * 2 + cx) * 2 + sub)
    rc = np.random.default_rng(8600)
    tone = rc.choice([-2, -1, 0, 0, 0, 1, 1], 8)
    li = np.maximum(lab, 0)
    f = cblend(fbm(N, N, 8601, cells=4, octaves=2), fbm(N, N, 8602 + v, cells=4, octaves=2))
    idx = 4 + tone[li] + posterize(f, [(0.7, 1), (0.3, -1)])
    idx = bevel(idx, lab, hi=1, lo=-1)
    for (x, y) in poisson(8603 + v, 30, 2.4):
        if lab[y, x] >= 0:
            idx[y, x] -= 1
    cv.put(BRICK, idx, ~joint)
    jn = fbm(N, N, 8604 + v, cells=16, octaves=1)
    cv.put(SAND, np.full((N, N), 2) + (jn > 0.5), joint)
    cv.put(MOSS, np.full((N, N), 2) + (jn > 0.75), joint & (jn > 0.55))
    if v == 1:   # grease / ash from the grill
        cv.tint('#1a1612', np.where(blob(N, N, 16, 15, 10, 8, 8610, rough=0.4), 0.35, 0))
    if v == 2:   # broken brick
        cm = path_mask(wander([(18, 2), (21, 5), (20, 7)], 8620, amp=0.6), wrap=False) & ~joint
        cv.col('#1a0a06', cm)
    return cv.out()


@painter('cemento_piso')
def p_cemento_piso(v):
    """Basement cement floor (alisado): trowel swirls, hairline cracks, an oil stain, damp patches."""
    cv = Cv()
    X, Y = cv.X, cv.Y
    f = cblend(fbm(N, N, 8700, cells=2, octaves=3), fbm(N, N, 8701 + v, cells=2, octaves=3))
    idx = np.full((N, N), 4) + posterize(f, [(0.74, 1), (0.24, -1)])
    sw = np.abs((np.sqrt((X - 6) ** 2 + (Y - 40) ** 2) % 6) - 3) < 0.4
    idx = np.where(sw & (fbm(N, N, 8702 + v, cells=4, octaves=1) > 0.55), idx + 1, idx)
    if v == 1:
        idx, _ = crack_line(idx, [(3, 7), (12, 10), (19, 18), (29, 21)], 8703, amp=2.5)
    cv.put(CEMENT, idx)
    if v == 2:
        st = blob(N, N, 17, 15, 8, 6, 8710, rough=0.35)
        cv.tint('#0e0c0a', np.where(st, 0.45, 0))
        cv.tint('#0e0c0a', np.where(erode(st, 2, False), 0.2, 0))
    if v == 3:
        cv.tint('#1e2218', np.where(fbm(N, N, 8720, cells=2, octaves=3) > 0.55, 0.3, 0))
        cv.put(SALT, np.full((N, N), 1), (fbm(N, N, 8721, cells=16, octaves=1) > 0.82))
    return cv.out()


@painter('arena')
def p_arena(v):
    """Packed sand floor of the 1961 room: ripples of old footsteps, grit, v1 a child's bare footprints,
    v2 drag marks, v3 old wax drips."""
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
        for k, (x, y) in enumerate(poisson(8830, 6, 5, keep=lambda x, y: 3 < x < 29 and 3 < y < 29)):
            cv.put(Ramp('#8a8070', '#b0a690', '#d4ccba'), np.full((N, N), 1 + (k % 2)), disc(x, y, 1.1 + (k % 3) * 0.4))
    return cv.out()


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
def p_asfalto(v):
    """Old asphalt of the pasaje: aggregate specks, tar-sealed cracks, v2 a pothole with water."""
    cv = Cv()
    X, Y = cv.X, cv.Y
    f = cblend(fbm(N, N, 9100, cells=2, octaves=3), fbm(N, N, 9101 + v, cells=2, octaves=3))
    idx = np.full((N, N), 3) + posterize(f, [(0.72, 1), (0.25, -1)])
    for (x, y) in poisson(9102 + v, 60, 1.8):
        idx[y, x] += 2 if (x + y) % 3 else -1
    cv.put(ASPH, idx)
    if v == 1:
        cm = path_mask(wander([(0, 12), (10, 15), (19, 11), (31, 14)], 9110, amp=2.5), wrap=False)
        cv.col('#090909', dilate(cm, 1, False) & (fbm(N, N, 9111, cells=8, octaves=1) > 0.3) | cm)
    if v == 2:
        ph = blob(N, N, 16, 17, 8, 6, 9120, rough=0.3)
        cv.put(ASPH, np.full((N, N), 1) + (fbm(N, N, 9121, cells=8, octaves=1) > 0.5), ph)
        water = erode(ph, 1, False)
        cv.put(Ramp('#0a0c10', '#141922', '#22293a', '#3a465a'), np.full((N, N), 1) + ((X - Y) % 7 == 0), water)
        r = rim(ph, wrap=False)
        cv.put(ASPH, np.full((N, N), 5), r['out_below'])
    return cv.out()


@painter('cesped_top')
def p_cesped_top(v):
    cv = Cv()
    X, Y = cv.X, cv.Y
    f = cblend(fbm(N, N, 9200, cells=4, octaves=3), fbm(N, N, 9201 + v, cells=4, octaves=3))
    idx = np.full((N, N), 4) + posterize(f, [(0.7, 1), (0.3, -1)])
    for (x, y) in poisson(9202 + v, 70, 1.6):
        idx[y, x] += 2
        idx[(y + 1) % N, x] -= 1
    cv.put(GRASS, idx)
    bare = rank(fbm(N, N, 9203 + v, cells=2, octaves=2)) > 0.86
    cv.put(EARTH, np.full((N, N), 3), bare & (fbm(N, N, 9204, cells=16, octaves=1) > 0.4))
    return cv.out()


@painter('cesped_side')
def p_cesped_side(v):
    cv = Cv()
    X, Y = cv.X, cv.Y
    f = fbm(N, N, 9210 + v, cells=4, octaves=2)
    cv.put(EARTH, np.full((N, N), 3) + posterize(f, [(0.7, 1), (0.3, -1)]))
    for (x, y) in poisson(9211, 10, 4, keep=lambda x, y: y > 8):
        cv.put(MORTAR, np.full((N, N), 3), (X == x) & (Y == y))
    edge = 3 + np.round(1.5 * np.sin(X * 1.3) + (fbm(N, N, 9212, cells=8, octaves=1)[0] - 0.5) * 4).astype(int)
    gm = Y <= edge
    cv.put(GRASS, np.full((N, N), 4) + (Y == 0) - (Y == edge), gm)
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
    """Smooth plaster ceiling (látex, yellowed). v1 hairline cracks along the slab joints, v2 fly specks and a
    cobweb thread shadow, v3 nicotine haze."""
    cv = Cv()
    idx = lime_idx(v + 90, base=6, seed=9400, rough=0.25)
    X, Y = cv.X, cv.Y
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
    cv.put(SALT, np.full((N, N), 1), (fbm(N, N, 9530 + v, cells=16, octaves=1) > 0.86) & (Y % 8 == 7))
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
    if v == 2:   # a cracked tile
        cm = path_mask(wander([(11, 3), (13, 8), (12, 13)], 9660, amp=1), wrap=False)
        cv.put(TEJA, np.full((N, N), 0), cm)
    if v == 3:   # a missing tile: the battens and the black felt
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
    """Side of the roof tiles (gable edges, stair risers): the tile ends on their mortar bed and the wooden batten."""
    cv = Cv()
    X, Y = cv.X, cv.Y
    ly = Y % 16
    lx = X % 8
    prof = np.array([0, 1, 1, 2, 2, 1, 1, 0])
    tile = ly <= 3 + (prof[lx] > 1)
    idx = np.full((N, N), 5) + np.where(ly == 0, 2, 0) - np.where(ly >= 3, 2, 0)
    cv.put(TEJA, idx, tile)
    bed = (ly > 3 + (prof[lx] > 1)) & (ly <= 10)
    cv.put(MORTAR, np.full((N, N), 3) + posterize(fbm(N, N, 9700, cells=8, octaves=1), [(0.6, 1)]) - (ly == 10), bed)
    bat = ly > 10
    cv.put(PINO, np.full((N, N), 3) + wood_grain(N, N, 9701, 'x', period=True) - (ly == 15), bat)
    cv.tint('#000000', np.where(ly == 4 + (prof[lx] > 1), 0.4, 0))
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
    if v == 1:
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
    """Render under a leaking gutter / window sill: dark grey-green streaks running down from the top."""
    cv = Cv()
    idx = render_idx(v + 14, seed=200)
    cv.put(RENDER_W, idx)
    X, Y = cv.X, cv.Y
    prof = 0.55 + 0.45 * np.sin((X + 3 + v * 11) / 32 * 2 * math.pi * 2)
    f = (prof * (22 + v * 4) - Y) / 10.0 + (fbm(N, N, 6410 + v, cells=4, octaves=3) - 0.5) * 0.6
    st = f > 0
    cv.tint('#3e4234', np.where(st, np.clip(0.25 + f * 0.25, 0, 0.6), 0))
    rng = np.random.default_rng(6411 + v)
    for x in rng.choice(np.arange(1, 31), 9, replace=False):
        L = int(prof[0, x] * (22 + v * 4) + rng.integers(2, 10))
        m = (X == x) & (Y < min(32, L)) & (fbm(N, N, 6412 + int(x), cells=8, octaves=1) > 0.2)
        cv.tint('#2e3226', np.where(m, 0.35, 0))
    if v == 1:
        mould_specks(cv, 6415, 3, keep=lambda x, y: y < 14)
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
LADRILLO = cube('ladrillo_visto', 'Ladrillo visto', 'Exposed face brick', 'ladrillo', 4, sound='stone')
cube('ladrillo_salitre', 'Ladrillo visto con salitre', 'Face brick with salt bloom', 'ladrillo_salitre', 3, sound='stone', up='ladrillo', down='ladrillo')
REVOQUE_B = cube('revoque_blanco', 'Revoque blanco', 'White render', 'revoque_blanco', 4)
cube('revoque_humedad', 'Revoque con humedad de cimientos', 'Render with rising damp', 'revoque_humedad', 3, up='revoque_blanco', down='revoque_blanco')
cube('revoque_chorreado', 'Revoque chorreado', 'Render with damp streaks from above', 'revoque_chorreado', 2, up='revoque_blanco', down='revoque_blanco')
cube('zocalo_revoque', 'Zócalo de cemento (bajo revoque)', 'Cement plinth under render', 'zocalo_revoque', 2, sound='stone', up='revoque_blanco', down='cemento_piso')
cube('zocalo_ladrillo', 'Zócalo de cemento (bajo ladrillo)', 'Cement plinth under brick', 'zocalo_ladrillo', 2, sound='stone', up='ladrillo', down='cemento_piso')
cube('medianera', 'Medianera', 'Party wall (medianera)', 'medianera', 4, sound='stone')
# --- interior walls
cube('pared_living', 'Pared del living', 'Living room wall', 'pared_living', 4)
cube('pared_living_zocalo', 'Pared del living con zócalo', 'Living room wall with skirting', 'pared_living_zocalo', 2, up='pared_living', down='pared_living')
cube('pared_living_moldura', 'Pared del living con moldura', 'Living room wall with picture rail', 'pared_living_moldura', 2, up='pared_living', down='pared_living')
cube('pared_pasillo', 'Pared del pasillo (verde agua)', 'Hall wall (pale aqua)', 'pared_pasillo', 4)
cube('pared_pasillo_zocalo', 'Pared del pasillo con zócalo', 'Hall wall with skirting', 'pared_pasillo_zocalo', 2, up='pared_pasillo', down='pared_pasillo')
cube('pared_cocina', 'Pared de la cocina', 'Kitchen wall', 'pared_cocina', 4)
cube('azulejo_verde', 'Azulejos verdes', 'Green kitchen tiles', 'azulejo_verde', 4, sound='tile')
cube('azulejo_verde_guarda', 'Azulejos verdes con guarda', 'Green tiles with decorated border', 'azulejo_verde_guarda', 1, sound='tile', up='azulejo_verde', down='azulejo_verde')
cube('pared_bano', 'Pared del baño', 'Bathroom wall', 'pared_bano', 4)
cube('azulejo_celeste', 'Azulejos celestes', 'Light-blue bathroom tiles', 'azulejo_celeste', 4, sound='tile')
cube('azulejo_celeste_guarda', 'Azulejos celestes con guarda', 'Light-blue tiles with border', 'azulejo_celeste_guarda', 1, sound='tile', up='azulejo_celeste', down='azulejo_celeste')
cube('pared_lucia', 'Pared rosa (Lucía)', "Pink wall (Lucía's room)", 'pared_lucia', 4)
cube('pared_lucia_zocalo', 'Pared rosa con zócalo', 'Pink wall with skirting', 'pared_lucia_zocalo', 2, up='pared_lucia', down='pared_lucia')
cube('pared_lucia_stickers', 'Pared rosa con stickers', 'Pink wall with stickers', 'pared_lucia_stickers', 3, up='pared_lucia', down='pared_lucia')
cube('pared_toti', 'Pared azul (Toti)', "Dark blue wall (Toti's room)", 'pared_toti', 4)
cube('pared_toti_zocalo', 'Pared azul con zócalo', 'Dark blue wall with skirting', 'pared_toti_zocalo', 2, up='pared_toti', down='pared_toti')
cube('pared_toti_poster', 'Pared azul con pósters', 'Dark blue wall with gamer posters', 'pared_toti_poster', 3, up='pared_toti', down='pared_toti')
cube('empapelado_nona', 'Empapelado floreado (Nona)', "Floral wallpaper (Nona's room)", 'empapelado_nona', 4, sound='paper')
cube('empapelado_nona_zocalo', 'Empapelado floreado con zócalo', 'Floral wallpaper with skirting', 'empapelado_nona_zocalo', 2, sound='paper', up='empapelado_nona', down='empapelado_nona')
cube('empapelado_matrimonial', 'Empapelado setentoso', '70s wallpaper (master bedroom)', 'empapelado_matrimonial', 3, sound='paper')
cube('empapelado_matrimonial_zocalo', 'Empapelado setentoso con zócalo', '70s wallpaper with skirting', 'empapelado_matrimonial_zocalo', 2, sound='paper', up='empapelado_matrimonial', down='empapelado_matrimonial')
cube('cemento_lavadero', 'Cemento del lavadero', 'Laundry cement wall', 'cemento_lavadero', 4, sound='stone')
# --- floors
cube('parquet', 'Parquet espina de pez', 'Herringbone parquet', 'parquet', 3, sound='wood')
cube('parquet_gastado', 'Parquet gastado', 'Worn parquet', 'parquet_gastado', 3, sound='wood')
cube('granitico', 'Granítico', 'Terrazzo tiles (granítico)', 'granitico', 3, sound='tile')
cube('granitico_roto', 'Granítico rajado', 'Cracked terrazzo tiles', 'granitico_roto', 3, sound='tile')
cube('ceramica_cocina', 'Cerámica de la cocina', 'Kitchen ceramic floor', 'ceramica_cocina', 3, sound='tile')
cube('baldosa_patio', 'Baldosa colorada del patio', 'Red patio tiles', 'baldosa_patio', 4, sound='stone')
cube('ladrillo_patio', 'Piso de ladrillo del patio', 'Patio brick paving', 'ladrillo_patio', 3, sound='stone', down='ladrillo')
cube('cemento_piso', 'Piso de cemento', 'Cement floor', 'cemento_piso', 4, sound='stone')
cube('arena', 'Piso de arena', 'Packed sand floor', 'arena', 4, sound='sand')
VEREDA = cube('vereda', 'Baldosa vainilla (vereda)', "'Vainilla' sidewalk tiles", 'vereda', 3, sound='stone', down='cemento_piso')
cube('vereda_rota', 'Vereda rota', 'Broken sidewalk tiles', 'vereda_rota', 3, sound='stone', up='vereda_rota', down='cemento_piso')
Cube('casa_cordon', 'Cordón de granito', 'Granite curb', faces={'up': cube_mat(PAINTERS['cordon_top']), 'side': cube_mat(PAINTERS['cordon_side']),
     'down': cube_mat(PAINTERS['cordon_side'])}, kit=KIT, sound='stone', variants=2)
cube('asfalto', 'Asfalto del pasaje', 'Old asphalt', 'asfalto', 3, sound='stone')
Cube('casa_cesped', 'Césped', 'Scruffy lawn', faces={'up': cube_mat(PAINTERS['cesped_top']), 'side': cube_mat(PAINTERS['cesped_side']),
     'down': cube_mat(PAINTERS['tierra'])}, kit=KIT, sound='grass', variants=3)
cube('tierra', 'Tierra', 'Garden earth', 'tierra', 2, sound='dirt')
# --- ceilings
cube('cielorraso', 'Cielorraso', 'Plaster ceiling', 'pared_bano', 4, down='cielorraso', up='cielorraso')
cube('cielorraso_humedad', 'Cielorraso con humedad', 'Damp-stained ceiling', 'pared_bano', 3, down='cielorraso_humedad', up='cielorraso')
cube('losa_sotano', 'Losa del sótano', 'Basement concrete slab', 'losa_sotano', 3, sound='stone')
# --- roof (two sets: ribs for slopes facing north/south, and for slopes facing east/west; stairs keep uvlock)
TEJAS = Cube('casa_tejas', 'Tejas francesas', 'French clay roof tiles', faces={'up': cube_mat(PAINTERS['tejas']),
             'side': cube_mat(PAINTERS['tejas_canto']), 'down': cube_mat(PAINTERS['machimbre'])}, kit=KIT, sound='ceramic', variants=4)
Stairs('casa_tejas_escalera', 'Techo de tejas (escalera, faldón N/S)', 'Tiled roof stairs (N/S slope)', of=TEJAS, kit=KIT, sound='ceramic')
Slab('casa_tejas_losa', 'Techo de tejas (losa)', 'Tiled roof slab', of=TEJAS, kit=KIT, sound='ceramic')
TEJAS_EO = Cube('casa_tejas_eo', 'Tejas francesas (faldón E/O)', 'French clay roof tiles (E/W slope)', faces={'up': cube_mat(PAINTERS['tejas_eo']),
                'side': cube_mat(PAINTERS['tejas_canto']), 'down': cube_mat(PAINTERS['machimbre'])}, kit=KIT, sound='ceramic', variants=4)
Stairs('casa_tejas_eo_escalera', 'Techo de tejas (escalera, faldón E/O)', 'Tiled roof stairs (E/W slope)', of=TEJAS_EO, kit=KIT, sound='ceramic')
Slab('casa_tejas_eo_losa', 'Techo de tejas (losa, E/O)', 'Tiled roof slab (E/W)', of=TEJAS_EO, kit=KIT, sound='ceramic')
cube('machimbre', 'Machimbre del alero', 'Eave soffit boards', 'machimbre', 2, sound='wood')
