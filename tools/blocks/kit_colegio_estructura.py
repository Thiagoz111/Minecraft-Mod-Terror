"""DEAD LINE building kit -- Colegio Santa Inés de la Vigilia (Córdoba, 1931-1984): STRUCTURE.

Walls (lime-washed plaster in many states, cream classroom plaster, dark wood wainscoting, exposed adobe/brick,
bathroom tiles), floors (damero, classroom boards, chapel flags, kitchen red tiles, courtyard pavers, crypt stone),
ceilings and beams, trims, doors, windows, shutters, stained glass, arches and columns of the cloister, stairs and
balustrades, the red colonial roof, the crypt (stone, niches, the 1984 bricked-up wall) and the exterior (fountain,
perimeter wall, wrought-iron gate with its arch sign).

Painting approach (32 px per block): every texture is painted with numpy as a small layered pixel-art painting, not
noise. Each material has a hand-picked hue-shifted ramp (cool shadows, warm lights, 7-9 tones). Low-frequency periodic
value noise is only used to *cluster* tones into soft blobs (posterised, never salt-and-pepper); every structural line
(joints, bevels, grain, cracks, peeling rims, nails, chips) is placed deliberately. Variants share their outer border
so they tile seamlessly with each other.
"""
import math

import numpy as np

from bkit import Cube, Slab, Stairs, Furniture, Door, box, plane, shash, FACES

KIT = 'colegio_estructura'
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
        return self.c[np.clip(np.asarray(idx).astype(int), 0, self.n - 1)]


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


# =============================================================================================== palettes
# whitewash (cal): warm off-white lights, cool lilac-grey shadows
CAL = Ramp('#3b3741', '#57525b', '#787174', '#9a928e', '#b6aea4', '#c9c2b6', '#d7d1c4', '#e2ddd1', '#ece8de')
CAL_DIRTY = Ramp('#3a332f', '#544a42', '#706355', '#8b7c6a', '#a2927c', '#b4a58e', '#c3b59f', '#cfc3ae', '#dad0bd')
CAL_STAIN = Ramp('#3b2a1c', '#563c25', '#70502f', '#87653c', '#9b7a4d', '#ad8e60', '#bca075', '#c8b089', '#d3be9b')
CREAM = Ramp('#463d33', '#625646', '#81735c', '#9e8f73', '#b4a586', '#c4b595', '#d1c3a3', '#dccfb1', '#e6dbc0')
RENDER = Ramp('#3a3633', '#4e4945', '#635c55', '#776f66', '#8a8177', '#9c9387', '#ada497', '#bbb2a5')  # grey lime render
OCHRE = Ramp('#6b5a40', '#877351', '#a08b65', '#b49f78', '#c4b089', '#d1bf99', '#dccba7')  # older faded paint layer
OLDGREEN = Ramp('#2f3a30', '#3f4d3f', '#51624f', '#647662', '#788a74', '#8c9d86')
BRICK = Ramp('#3a1a14', '#53251b', '#6b3122', '#813d2a', '#964a32', '#a8583c', '#b86849', '#c67a5a', '#d18d6e')
BRICK_OLD = Ramp('#33201a', '#4a2c22', '#5f392b', '#734536', '#855241', '#965f4c', '#a56e5a', '#b27e6a', '#bd8f7c')
MORTAR = Ramp('#4a443e', '#625b53', '#7a7268', '#91897d', '#a59d91', '#b6aea2', '#c4bdb1')
ADOBE = Ramp('#3b2a20', '#4f382a', '#644735', '#795742', '#8c6750', '#9d775e', '#ad876d', '#bb977d')
STRAW = Ramp('#6e5c3e', '#8a7550', '#a08a62', '#b39d74')
WOOD_D = Ramp('#120b08', '#1d120c', '#2a1a11', '#372216', '#452b1b', '#543522', '#64402a', '#764e34', '#8a5f40')
FLOOR = Ramp('#21140c', '#311e12', '#432918', '#55341e', '#674026', '#784c2e', '#895937', '#9a6842', '#ac7a51')
FLOOR_W = Ramp('#2c2219', '#3f3124', '#53422f', '#66533c', '#78644a', '#897459', '#998468', '#a99478')  # worn, unvarnished
TILE_W = Ramp('#57524a', '#756f64', '#938c7e', '#ada697', '#c1baa9', '#cfc8b6', '#dbd5c3', '#e6e1d0', '#efebdc')
TILE_K = Ramp('#0c0b0e', '#141317', '#1b1a1f', '#232228', '#2c2b32', '#36353c', '#424148', '#504f57', '#605f68')
GROUT = Ramp('#1b1816', '#28241f', '#37322c', '#48433b', '#5c564d', '#706a60')
CEMENT = Ramp('#2e2c2a', '#3f3c38', '#524e48', '#65605a', '#78736b', '#8a857c', '#9b968c')
DUST = Ramp('#4d463d', '#665d51', '#7f7566', '#978c7a')
BAL_R = Ramp('#3d160e', '#561e12', '#6e2717', '#83311c', '#963c22', '#a6492b', '#b45a39', '#c06c4a')
STONE = Ramp('#35312d', '#47423c', '#5b554d', '#706960', '#867e72', '#9a9185', '#ada498', '#bfb7aa', '#cfc8bc')


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


# =============================================================================================== WALLS: lime plaster
@painter('revoque')
def p_revoque(v):
    cv = Cv()
    idx = lime_idx(v)
    if v == 2:   # hairline crack, kept inside the tile
        pts = wander([(6, 4), (13, 12), (11, 21), (17, 27)], 31, amp=3)
        m = path_mask(pts)
        idx -= np.where(m, 3, 0)
        idx += np.where(nb(m, 1, 0) & ~m, 1, 0)
    if v == 3:   # two old nail holes with a faint rust bleed
        for (x, y) in ((9, 11), (22, 19)):
            idx[y, x] -= 4
            idx[y - 1, x] += 1
    cv.put(CAL, idx)
    if v == 3:
        for (x, y) in ((9, 11), (22, 19)):
            cv.tint('#7a4a26', 0.16, (cv.X == x) & (cv.Y > y) & (cv.Y < y + 4))
    return cv.out()


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


def peel(cv, idx, holes, deep, seed, ring=OCHRE, base_ramp=CAL, islands=True):
    """Peeling: whitewash gone inside `holes`; patches of an older paint layer at parts of the rim; grey render
    with its own relief; bricks (recessed, shadowed) inside `deep`."""
    H = holes
    deep = deep & erode(H, 2, False)
    if islands:   # a few whitewash flakes still clinging inside the hole
        isl = (fbm(N, N, seed + 21, cells=8, octaves=1) > 0.80) & erode(H, 2, False) & ~dilate(deep, 1, False)
        H = H & ~isl
    r = rim(H, wrap=False)
    ringm = (H & ~erode(H, 1, False)) & (fbm(N, N, seed + 5, cells=4, octaves=2) > 0.48)
    ringm |= nb(ringm, 0, 1, False) & H & (fbm(N, N, seed + 6, cells=8, octaves=1) > 0.6)
    ringm &= ~deep
    # whitewash: lit lip of the paint thickness under the hole, crisp dark edge over it
    idx = idx + np.where(r['out_below'], 2, 0) + np.where(r['out_right'], 1, 0)
    idx = idx - np.where(r['out_above'] | r['out_left'], 1, 0)
    cv.put(base_ramp, idx, ~H)
    # grey render with relief
    ridx = np.full((N, N), 4) + posterize(fbm(N, N, seed + 11, cells=4, octaves=3), [(0.66, 1), (0.36, -1)])
    ridx = relief(ridx, seed + 12, seed + 13, count=30, mind=3.5, body=-1, light=1)
    ridx -= np.where(r['in_top'], 2, 0) + np.where(r['in_left'], 1, 0)
    cv.put(RENDER, ridx, H & ~ringm & ~deep)
    oidx = np.full((N, N), 4) - np.where(r['in_top'], 2, 0) - np.where(r['in_left'], 1, 0) + np.where(r['in_bot'], 1, 0)
    cv.put(ring, oidx, ringm)
    if deep.any():
        sub = Cv()
        paint_bricks(sub, seed=seed + 3, ramp=BRICK_OLD)
        rd = rim(deep, wrap=False)
        dark = np.where(rd['in_top'], 0.55, 1.0) * np.where(rd['in_left'], 0.78, 1.0)
        dark *= np.where(nb(rd['in_top'], 1, 0, False) & deep, 0.8, 1.0)
        cv.rgb[deep] = (sub.rgb * dark[..., None])[deep]
        cv.a[deep] = 255
        cv.put(RENDER, np.full((N, N), 7), rd['out_below'] & H)   # broken render edge lit from above
        cv.put(RENDER, np.full((N, N), 6), rd['out_right'] & H & ~rd['out_below'])
    return H


@painter('revoque_descascarado')
def p_revoque_desc(v):
    cv = Cv()
    idx = lime_idx(v + 10)
    specs = [
        # flakes [(cx, cy, rx, ry)], deep [(cx, cy, rx, ry)]
        ([(19, 12, 10.5, 8.5), (6, 26, 3, 2), (28, 25, 2, 1.6)], [(19, 13, 6.5, 4.6)]),
        ([(12, 19, 10, 9.5), (25, 6, 2.6, 2)], [(11, 21, 7.5, 6.2)]),
        ([(8, 9, 5.5, 4.5), (22, 21, 7, 5.5), (26, 7, 3, 2.2), (6, 24, 2.2, 1.6)], []),
        ([(16, 15, 6.5, 13)], [(16, 17, 3.6, 8.5)]),
    ][v % 4]
    H = np.zeros((N, N), bool)
    D = np.zeros((N, N), bool)
    for k, (cx, cy, rx, ry) in enumerate(specs[0]):
        H |= flake(cx, cy, rx, ry, 400 + 13 * v + k)
    for k, (cx, cy, rx, ry) in enumerate(specs[1]):
        D |= flake(cx, cy, rx, ry, 500 + 13 * v + k, jag=0.3)
    H &= border_dist(N, N) >= 2
    D &= H
    # hairline cracks running away from the damage
    ys, xs = np.nonzero(H)
    rng = np.random.default_rng(600 + v)
    if len(xs):
        cx, cy = xs.mean(), ys.mean()
        for a in rng.uniform(0, 2 * math.pi, 2):
            x1 = cx + math.cos(a) * 14
            y1 = cy + math.sin(a) * 14
            pts = [(x, y) for x, y in wander([(cx, cy), (x1, y1)], 610 + v, amp=2.5) if 2 <= x < 30 and 2 <= y < 30]
            m = path_mask(pts) & ~dilate(H, 1, False)
            idx = idx - np.where(m, 2, 0) + np.where(nb(m, -1, 0) & ~m, 1, 0)
    peel(cv, idx, H, D, 700 + v)
    return cv.out()


@painter('revoque_humedad')
def p_revoque_humedad(v):
    """Water stain coming from the ceiling: an irregular tan stain hanging from the top edge with several darker
    tide lines, darker drip runs and a few black mould specks."""
    cv = Cv()
    idx = lime_idx(v + 20)
    cv.put(CAL, idx)
    X, Y = cv.X, cv.Y
    depth = [(14, 9, 22), (20, 12, 10), (9, 24, 15)][v % 3]
    # depth profile along x (how far the stain reaches down at each column)
    prof = vnoise(N, 1, 4, 1, 840 + v)[0] * depth[1] + depth[0] * 0.6
    prof += np.exp(-((np.arange(N) - depth[2]) / 6.0) ** 2) * 8
    f = 1 - (Y + 0.5) / prof[X] + (fbm(N, N, 810 + v, cells=4, octaves=3) - 0.5) * 0.5
    rng = np.random.default_rng(800 + v)
    runs = np.zeros((N, N), bool)
    for x in rng.choice(np.arange(3, 29), 3, replace=False):
        ln = int(prof[x] + rng.integers(3, 9))
        runs |= (X == x) & (Y < min(N - 2, ln))
        runs |= (X == x + 1) & (Y < min(N - 2, ln - 3))
    stain = (f > 0.0) | runs
    st = np.full((N, N), 7) - (f > 0.3).astype(int) - (f > 0.6).astype(int)
    st = np.where(runs & (f <= 0.0), 5, st)
    for th in (0.0, 0.3, 0.6):
        band = f > th
        st = np.where(band & ~erode(band, 1, False) & (Y > 0), 4, st)
    st += idx - 6
    cv.put(CAL_STAIN, st, stain)
    for (x, y) in poisson(830 + v, 7, 2.5, keep=lambda x, y: f[int(y), int(x)] > 0.45):
        cv.col('#3e3a2c', (X == x) & (Y == y))
    return cv.out()


@painter('revoque_salitre')
def p_revoque_salitre(v):
    """Base course of a wall: rising damp, wavy tide line with a salt fringe, small flakes and kick grime."""
    cv = Cv()
    idx = lime_idx(v + 30)
    X, Y = cv.X, cv.Y
    wave = 13 + 2.0 * np.sin((X + v * 7) / 32 * 2 * math.pi) + 1.2 * np.sin((X * 2 + v * 11) / 32 * 2 * math.pi)
    wave = wave + np.round((vnoise(N, 1, 8, 1, 900 + v)[0] - 0.5) * 3)
    wave = np.round(wave).astype(int)
    damp = Y >= wave
    cv.put(CAL, idx)
    didx = idx - 1 - ((Y > wave + 7) & (fbm(N, N, 905 + v, cells=4, octaves=2) > 0.4)).astype(int)
    cv.put(CAL_DIRTY, didx + 1, damp)
    tide = damp & ~nb(damp, 1, 0, True)
    cv.put(CAL_STAIN, np.full((N, N), 4), tide)
    cv.put(CAL_STAIN, np.full((N, N), 6), nb(tide, 1, 0, True) & ~tide)
    # salt efflorescence: crusty white clusters hugging the tide line
    salt = (Y >= wave - 3) & (Y <= wave - 1) & (fbm(N, N, 920 + v, cells=8, octaves=2) > 0.58)
    cv.put(CAL, np.full((N, N), 8), salt)
    cv.put(CAL, np.full((N, N), 5), nb(salt, 1, 0) & ~salt & ~damp)
    # flakes of paint gone in the damp band (small, a few)
    H = np.zeros((N, N), bool)
    rng = np.random.default_rng(930 + v)
    for k in range(3):
        cx, cy = int(rng.integers(4, 28)), int(rng.integers(int(wave.mean()) + 4, 26))
        H |= flake(cx, cy, rng.uniform(2, 4), rng.uniform(1.4, 2.4), 940 + v * 5 + k, jag=0.3)
    H &= border_dist(N, N) >= 2
    if H.any():
        r = rim(H, wrap=False)
        ridx = np.full((N, N), 3) + posterize(fbm(N, N, 950 + v, cells=8, octaves=2), [(0.6, 1)])
        ridx -= np.where(r['in_top'], 2, 0)
        cv.put(RENDER, ridx, H)
        cv.put(CAL_DIRTY, np.full((N, N), 8), r['out_below'])
    # kick grime near the floor: broken band, scuffs
    g = (Y >= 29) | ((Y >= 26) & (fbm(N, N, 960 + v, cells=8, octaves=2) > 0.6))
    cv.put(DUST, np.full((N, N), 2) + (Y < 29), g)
    cv.put(DUST, np.full((N, N), 1), Y == 31)
    for k in range(3):
        x, y = int(rng.integers(2, 26)), int(rng.integers(21, 27))
        ln = int(rng.integers(3, 6))
        cv.put(CAL_DIRTY, np.full((N, N), 3), (Y == y) & (X >= x) & (X < x + ln))
    return cv.out()


# --- posters, frame ghosts, scribbles
def paper_scrap(cv, x0, y0, x1, y1, seed, torn_side='bottom'):
    rng = np.random.default_rng(seed)
    X, Y = cv.X, cv.Y
    m = (X >= x0) & (X < x1) & (Y >= y0) & (Y < y1)
    edge = vnoise(N, 1, 12, 1, seed)[0]
    if torn_side == 'bottom':
        m &= Y < y0 + (y1 - y0) * (0.45 + 0.55 * edge[X])
    elif torn_side == 'right':
        m &= X < x0 + (x1 - x0) * (0.45 + 0.55 * vnoise(1, N, 1, 12, seed)[:, 0][Y])
    PAPER = Ramp('#5d5340', '#7d7055', '#9a8b69', '#b2a17c', '#c4b38d', '#d1c19b')
    pidx = np.full((N, N), 4) + posterize(fbm(N, N, seed + 1, cells=4, octaves=2), [(0.6, 1), (0.35, -1)])
    r = rim(m, wrap=False)
    pidx -= np.where(r['in_bot'] | r['in_right'], 1, 0)
    cv.put(PAPER, pidx, m)
    cv.put(CAL, np.full((N, N), 3), r['out_below'] | r['out_right'])  # tiny shadow of the paper
    return m


@painter('revoque_marcas')
def p_revoque_marcas(v):
    cv = Cv()
    idx = lime_idx(v + 40)
    X, Y = cv.X, cv.Y
    if v == 0:   # ghost of a removed picture: cleaner rectangle, dust line, nail, two picture-wire scratches
        r = (X >= 6) & (X <= 25) & (Y >= 8) & (Y <= 27)
        idx = idx + np.where(r, 1, 0) - np.where(~r, 1, 0) * (fbm(N, N, 1001, cells=4, octaves=2) > 0.5)
        rr = rim(r, wrap=False)
        idx -= np.where(rr['out_below'], 2, 0) + np.where(rr['out_left'] | rr['out_right'], 1, 0)
        idx[3, 15] -= 5
        idx[2, 15] += 1
        for (a, b) in (((15, 4), (7, 8)), ((15, 4), (24, 8))):
            for (x, y) in line_px(*a, *b)[1:-1]:
                idx[y, x] -= 1
        cv.put(CAL, idx)
    elif v == 1:  # ghost of a crucifix: a clean cross where the dust did not settle
        cross = ((X >= 14) & (X <= 17) & (Y >= 4) & (Y <= 28)) | ((X >= 8) & (X <= 23) & (Y >= 9) & (Y <= 12))
        idx = idx + np.where(cross, 1, -1)
        rr = rim(cross, wrap=False)
        idx -= np.where(rr['out_below'], 2, 0) + np.where(rr['out_right'], 1, 0)
        idx[6, 15] -= 5
        idx[6, 16] -= 3
        cv.put(CAL, idx)
        cv.tint('#6b3d22', 0.3, (X == 15) & (Y > 6) & (Y < 12))
    elif v == 2:  # torn school poster: red header band, small print, tape and glue remains
        cv.put(CAL, idx)
        m = paper_scrap(cv, 4, 3, 26, 22, 1020, 'bottom')
        hdr = (Y >= 4) & (Y <= 12) & (X >= 6) & (X <= 23) & m
        cv.put(Ramp('#5e1e1a', '#7a2a22', '#93392c'), np.full((N, N), 1) + (Y == 4), hdr)
        tm = np.zeros((N, N), bool)
        stamp(tm, text_mask('KERM'), 7, 3)
        cv.put(Ramp('#d8c9a6', '#e6d8b6'), np.full((N, N), 1), tm & hdr)
        for y in (14, 16, 18):
            cv.col('#6b604d', (Y == y) & (X >= 7) & (X < 22 - (y == 18) * 6) & m & ((X * 7 + y) % 5 != 0))
        paper_scrap(cv, 21, 24, 28, 29, 1021, 'right')
        tape = (X >= 20) & (X <= 26) & (Y >= 1) & (Y <= 2)
        cv.put(Ramp('#8a7a52', '#a8955f', '#bfac74'), np.full((N, N), 1) + (Y == 1), tape)
        glue = (X >= 8) & (X <= 14) & (Y >= 25) & (Y <= 27) & (fbm(N, N, 1022, cells=8, octaves=1) > 0.4)
        cv.put(CAL_STAIN, np.full((N, N), 6), glue)
    else:         # pencil scribbles and tally marks (days counted)
        cv.put(CAL, idx)
        PEN = Ramp('#6c6c74', '#7f7f88', '#93939b')
        rng = np.random.default_rng(1030)
        x = 4
        for g in range(4):
            for k in range(5 if g < 3 else 3):
                if k == 4:
                    pts = line_px(x - 9, 21, x - 1, 15)
                else:
                    pts = line_px(x, 14 + rng.integers(0, 2), x + rng.integers(-1, 1), 22)
                pm = path_mask(pts, wrap=False)
                cv.put(PEN, np.full((N, N), 1 + (k % 2)), pm)
                x += 2
            x += 3
        # a small heart doodle
        hm = np.zeros((N, N), bool)
        stamp(hm, np.array([[c == '#' for c in row] for row in FONT['♥']], bool), 22, 4)
        hr = rim(hm, wrap=False)
        cv.put(PEN, np.full((N, N), 1), hr['in_top'] | hr['in_bot'] | hr['in_left'] | hr['in_right'])
    return cv.out()


@painter('revoque_grafiti')
def p_revoque_grafiti(v):
    """Chalk graffiti from the girls (1984): crude nun drawing, SHHH, hearts, the rayuela code."""
    cv = Cv()
    idx = lime_idx(v + 50)
    cv.put(CAL, idx)
    X, Y = cv.X, cv.Y
    CH = Ramp('#8a8f99', '#a9aeb7', '#c9ccd2')  # wax crayon / chalk on white: grey-blue

    def chalk(mask, col_ramp=CH, density=0.78, seed=0):
        n = fbm(N, N, 1100 + seed, cells=16, octaves=1)
        cv.put(col_ramp, np.where(n > 0.55, 1, 0), mask & (n < density + 0.2))

    m = np.zeros((N, N), bool)
    RED = Ramp('#6e1f1c', '#8f2a24', '#a8382c')
    if v == 0:    # child's charcoal drawing of the nun: hatched habit, round face, X eyes
        CHAR = Ramp('#3a3a40', '#55555c', '#6e6e75')
        hab = np.zeros((N, N), bool)
        for y in range(9, 29):
            half = 3 + (y - 9) * 0.45
            hab |= (Y == y) & (np.abs(X + 0.5 - 16) <= half)
        face = (X - 15.5) ** 2 + (Y - 9.5) ** 2 <= 9.5
        veil = (Y >= 3) & (Y <= 9) & (np.abs(X + 0.5 - 16) <= 5 + (Y - 3) * 0.3)
        veil = (veil | hab) & ~face
        hatch = veil & ((X + Y) % 3 == 0)
        out = veil & ~erode(veil, 1, False)
        cv.put(CHAR, np.full((N, N), 1), hatch | out)
        fr = face & ~erode(face, 1, False)
        cv.put(CHAR, np.full((N, N), 0), fr)
        for (cx, cy) in ((14, 9), (17, 9)):
            cv.put(CHAR, np.full((N, N), 0), ((X == cx) | (X == cx + 1)) & ((Y == cy) | (Y == cy + 1)) & ((X - cx) == (Y - cy)))
            cv.put(CHAR, np.full((N, N), 0), (X == cx + 1) & (Y == cy) | (X == cx) & (Y == cy + 1))
        cv.put(CHAR, np.full((N, N), 1), (Y >= 15) & (Y <= 19) & (X == 16) | (Y == 16) & (X >= 14) & (X <= 18))
    elif v == 1:  # SHHH
        stamp(m, text_mask('SHHH'), 4, 10)
        chalk(m, seed=2)
        um = np.zeros((N, N), bool)
        stamp(um, text_mask('!'), 27, 10)
        chalk(um, seed=3)
    elif v == 2:  # red crayon heart with initials P y M (Paloma & Mecha)
        pts = []
        for t in np.linspace(0, 2 * math.pi, 90):
            hx_ = 16 * math.sin(t) ** 3
            hy_ = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
            pts.append((int(round(16 + hx_ * 0.72)), int(round(14 - hy_ * 0.72))))
        hm = np.zeros((N, N), bool)
        for a_, b_ in zip(pts, pts[1:]):
            hm |= path_mask(line_px(*a_, *b_), wrap=False)
        chalk(hm, RED, density=0.9, seed=4)
        tm = np.zeros((N, N), bool)
        stamp(tm, text_mask('P+M'), 10, 8)
        chalk(tm, RED, density=0.9, seed=5)
    else:         # the hopscotch code, scratched small: 2 1 6 8 4
        stamp(m, text_mask('21684', spacing=1), 2, 12)
        chalk(m, seed=6)
        pts = line_px(2, 22, 30, 21)
        chalk(path_mask(pts, wrap=False), seed=7)
    return cv.out()


@painter('revoque_zocalo')
def p_revoque_zocalo(v):
    """Lime wall with a dark varnished wooden baseboard (rooms without wainscoting)."""
    cv = Cv()
    idx = lime_idx(v + 60)
    cv.put(CAL, idx)
    X, Y = cv.X, cv.Y
    # dust and kick marks over the baseboard
    g = (Y >= 22) & (fbm(N, N, 1200 + v, cells=8, octaves=2) > 0.52)
    cv.put(CAL_DIRTY, idx - 1, g)
    widx = np.full((N, N), 4) + posterize(fbm(N, N, 1210 + v, cells=2, octaves=3, ax=0.25, ay=6), [(0.6, 1), (0.4, -1)])
    bb = Y >= 26
    widx += np.where(Y == 26, 3, 0) + np.where(Y == 27, 1, 0) - np.where(Y == 31, 2, 0)
    widx -= np.where((Y == 28), 1, 0) * (X % 11 == 3)
    cv.put(WOOD_D, widx, bb)
    cv.put(CAL_DIRTY, np.full((N, N), 1), Y == 25)  # crevice shadow above the baseboard
    if v == 1:  # chipped varnish
        ch = (Y >= 27) & (Y <= 29) & (X >= 18) & (X <= 21)
        cv.put(WOOD_D, np.full((N, N), 7), ch & (Y == 27))
        cv.put(WOOD_D, np.full((N, N), 6), ch & (Y > 27))
    return cv.out()


# --- cream classroom plaster
@painter('crema')
def p_crema(v):
    cv = Cv()
    idx = lime_idx(v + 70, rough=0.7)
    cv.put(CREAM, idx)
    return cv.out()


@painter('crema_marcas')
def p_crema_marcas(v):
    cv = Cv()
    idx = lime_idx(v + 80, rough=0.7)
    X, Y = cv.X, cv.Y
    if v == 0:   # map / frame ghost with dirty halo
        r = (X >= 4) & (X <= 27) & (Y >= 6) & (Y <= 24)
        idx = idx + np.where(r, 1, -1)
        rr = rim(r, wrap=False)
        idx -= np.where(rr['out_below'], 2, 0) + np.where(rr['out_right'] | rr['out_left'], 1, 0)
        idx[3, 9] -= 5
        idx[3, 22] -= 5
        cv.put(CREAM, idx)
    elif v == 1:  # crucifix ghost above the blackboard
        cross = ((X >= 14) & (X <= 17) & (Y >= 3) & (Y <= 29)) | ((X >= 7) & (X <= 24) & (Y >= 9) & (Y <= 12))
        idx = idx + np.where(cross, 1, -1)
        rr = rim(cross, wrap=False)
        idx -= np.where(rr['out_below'], 2, 0) + np.where(rr['out_right'], 1, 0)
        idx[5, 15] -= 5
        cv.put(CREAM, idx)
    else:         # chalk-dust handprints (small, a child's) and a water stain corner
        cv.put(CREAM, idx)
        HAND = ['..#.#....', '..#.#.#..', '#.#.#.#..', '#.#.#.#..', '#######..', '#######.#', '.######.#',
                '.#######.', '..#####..', '..####...', '..####...']
        hm = np.zeros((N, N), bool)
        hand = np.array([[c == '#' for c in row] for row in HAND], bool)
        stamp(hm, hand, 5, 9)
        stamp(hm, hand[:, ::-1], 17, 15)
        n = fbm(N, N, 1300 + v, cells=16, octaves=1)
        cv.put(Ramp('#cfd0cd', '#e2e2dc', '#eeeee8'), np.where(n > 0.5, 1, 0), hm & (n > 0.25))

    return cv.out()


# --- dark wood wainscoting (friso)
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


@painter('friso')
def p_friso(v):
    cv = Cv()
    X, Y = cv.X, cv.Y
    gv = wood_grain(N, N, 1400 + v, 'y')
    gh = wood_grain(N, N, 1450 + v, 'x')
    stile = ((X <= 2) | (X >= 29)) & (Y >= 5) & (Y <= 26)
    idx = np.where(stile, 4 + gv, 4 + gh)
    # chair rail: lit top, rounded nose, dark underside
    for y, t in ((0, 7), (1, 6), (2, 5), (3, 4), (4, 2)):
        idx = np.where(Y == y, t + (gh if y in (2, 3) else 0) * (y != 4), idx)
    idx = np.where(Y == 5, 2, idx)                       # shadow under the rail on the frame
    # panel
    idx = frame_opening(idx, 3, 9, 28, 22)
    idx, field, inside = raised_panel(idx, 4, 10, 27, 21, 3, 4 + gv, hi=(2, 1), lo=(-1, -1))
    # stile/rail joints (1 px seams where the rails butt into the stiles)
    idx = np.where(((X == 3) | (X == 28)) & ((Y >= 6) & (Y <= 8) | (Y >= 23) & (Y <= 26)), idx - 1, idx)
    # baseboard: bead + face + floor shadow
    idx = np.where(Y == 26, 2, idx)
    idx = np.where(Y == 27, 6, idx)
    idx = np.where(Y == 28, 5 + (gh > 0), idx)
    idx = np.where((Y >= 29) & (Y <= 30), 4 + gh, idx)
    idx = np.where(Y == 31, 2, idx)
    if v in (1, 3):   # wear: varnish rubbed on the rail nose, scuffs and kicks on the baseboard & bottom rail
        rng = np.random.default_rng(1470 + v)
        for k in range(6 if v == 1 else 3):
            x, y = int(rng.integers(1, 26)), int(rng.integers(23, 31))
            ln = int(rng.integers(2, 6))
            idx = np.where((Y == y) & (X >= x) & (X < x + ln) & (Y != 26), idx + 2, idx)
        idx = np.where((Y == 1) & (vnoise(N, N, 8, 1, 1480 + v) > 0.6), 8, idx)
    cv.put(WOOD_D, idx)
    if v == 2:   # dried split along the grain of the panel field
        pts = wander([(17, 13), (16, 16), (17, 19)], 1490, amp=0.8)
        m = path_mask(pts, wrap=False) & field
        cv.put(WOOD_D, np.full((N, N), 0), m)
        cv.put(WOOD_D, np.full((N, N), 7), nb(m, 0, 1, False) & ~m & field)
    if v == 3:   # bleached by water near the floor, tide line
        wet = (Y >= 19 + (vnoise(N, 1, 6, 1, 1495)[0][X] * 4).astype(int))
        cv.tint('#857360', 0.30, wet)
        tide = wet & ~nb(wet, 1, 0, False)
        cv.tint('#1a100a', 0.45, tide)
    return cv.out()


@painter('friso_top')
def p_friso_top(v):
    """Top/bottom face of the wainscot cube: end grain of the dark wood (only visible at cut edges)."""
    cv = Cv()
    idx = np.full((N, N), 3) + wood_grain(N, N, 1500, 'x')
    cv.put(WOOD_D, idx)
    return cv.out()


# --- exposed old brick and adobe (where the plaster is gone entirely)
@painter('ladrillo_viejo')
def p_ladrillo_viejo(v):
    """Handmade colonial brick with wide lime joints; lime render still stuck in places."""
    cv = Cv()
    lab = paint_bricks(cv, seed=1600 + v * 7)
    rest = np.zeros((N, N), bool)
    for k, (cx, cy, rx, ry) in enumerate([(7, 5, 4, 2.5), (24, 21, 5, 3)] if v == 0 else [(14, 13, 3.5, 2.2), (28, 29, 3, 2)]):
        rest |= flake(cx, cy, rx, ry, 1610 + v * 5 + k, jag=0.5)
    rest |= (lab < 0) & (fbm(N, N, 1615 + v, cells=8, octaves=1) > 0.72)
    rest &= border_dist(N, N) >= 1
    ridx = np.full((N, N), 5) + posterize(fbm(N, N, 1611 + v, cells=8, octaves=1), [(0.6, 1)])
    r = rim(rest, wrap=False)
    ridx += np.where(r['in_top'], 1, 0) - np.where(r['in_bot'], 1, 0)
    cv.put(RENDER, ridx, rest)
    cv.put(BRICK, np.full((N, N), 1), r['out_below'] & (lab >= 0))
    return cv.out()


@painter('adobe')
def p_adobe(v):
    """Sun-dried mud bricks (2 courses), mud joints of the same earth, eroded corners, straw fibres, pebbles."""
    cv = Cv()
    X, Y = cv.X, cv.Y
    lab = -np.ones((N, N), int)
    n = 0
    for r in range(2):
        y0 = r * 16
        off = 0 if r == 0 else 16
        for k in range(2):
            x0 = off + k * 16 + 1
            blk = np.zeros((N, N), bool)
            yy, xx = np.mgrid[0:13, 0:14]
            corner = ((yy < 2) & (xx < 2 - yy)) | ((yy < 2) & (xx > 11 + yy)) | ((yy > 10) & (xx < yy - 10)) | ((yy > 10) & (xx > 23 - yy))
            for j in range(13):
                for i in range(14):
                    if not corner[j, i]:
                        lab[(y0 + 1 + j) % N, (x0 + i) % N] = n
            n += 1
    rng = np.random.default_rng(1700 + v)
    tone = rng.choice([-1, 0, 0, 1], n)
    f = fbm(N, N, 1710 + v, cells=4, octaves=3)
    idx = np.where(lab >= 0, 4 + tone[np.maximum(lab, 0)], 3) + posterize(f, [(0.68, 1), (0.32, -1)])
    idx = bevel(idx, lab, hi=0, lo=-1)
    idx = relief(idx, 1720, 1721 + v, count=30, mind=3.6, body=-1, light=1)
    # mud joint: same earth, rougher, a shadow line under each block
    joint = lab < 0
    idx = np.where(joint & (nb(lab, 1, 0) >= 0), 2, idx)
    cv.put(ADOBE, idx)
    # straw fibres: short pale strokes lying in many directions
    dirs = [(1, 0), (1, 0), (2, 1), (1, 1), (2, -1), (0, 1)]
    for k, (x, y) in enumerate(poisson(1730 + v, 13, 5.0)):
        dx, dy = dirs[int(rng.integers(0, len(dirs)))]
        L = int(rng.integers(2, 4))
        pts = line_px(x, y, x + dx * L // max(1, abs(dx) if dx else 1), y + dy * (L // 2 if dx else L))
        for (px, py) in pts:
            px, py = px % N, py % N
            cv.put(STRAW, np.full((N, N), 1 + (k % 3)), (X == px) & (Y == py) & (lab >= 0))
    # pebbles in the joints
    for (x, y) in poisson(1740 + v, 8, 6):
        if joint[y, x]:
            cv.put(MORTAR, np.full((N, N), 4), (X == x) & (Y == y))
            cv.put(MORTAR, np.full((N, N), 2), (X == x) & (Y == (y + 1) % N))
    return cv.out()


# --- bathroom tiles
AZ = Ramp('#555b60', '#767c80', '#999ea0', '#b8bcbb', '#cdd0cc', '#dcdfda', '#e7e9e3', '#f0f1ec', '#f8f8f4')


@painter('azulejo')
def p_azulejo(v):
    """White glazed 15 cm tiles (4 x 4 per block), grout lines, crazing, rust and a missing tile in variant 2."""
    cv = Cv()
    X, Y = cv.X, cv.Y
    grout = (X % 8 == 0) | (Y % 8 == 0)
    lab = np.where(grout, -1, (Y // 8) * 4 + X // 8)
    rng = np.random.default_rng(1800 + v)
    tone = rng.integers(0, 2, 16)
    idx = np.where(lab >= 0, 5 + tone[np.maximum(lab, 0)], 0)
    # glaze: soft cloudy highlight and a crisp specular stroke on some tiles
    f = fbm(N, N, 1810 + v, cells=4, octaves=2)
    idx += posterize(f, [(0.66, 1), (0.34, -1)]) * (lab >= 0)
    lx, ly = X % 8, Y % 8
    idx = np.where((lab >= 0) & ((ly == 1) | (lx == 1)), idx + 1, idx)
    idx = np.where((lab >= 0) & ((ly == 7) | (lx == 7)), idx - 1, idx)
    spec = (lab >= 0) & (lx + ly == 5) & (lx >= 2) & (lx <= 3) & (tone[np.maximum(lab, 0)] == 1)
    idx = np.where(spec, 8, idx)
    cv.put(AZ, idx)
    gidx = np.full((N, N), 3) + posterize(fbm(N, N, 1820 + v, cells=8, octaves=1), [(0.55, -1), (0.3, -1)])
    cv.put(GROUT, gidx, grout)
    if v == 1:   # crazed glaze: fine crack network on two tiles
        for k, (a, b) in enumerate((((9, 9), (15, 14)), ((17, 18), (22, 23)))):
            pts = wander([a, b], 1830 + k, amp=1.5)
            cv.put(AZ, np.full((N, N), 2), path_mask(pts, wrap=False) & (lab >= 0))
        rust = (X >= 24) & (X <= 26) & (Y >= 10) & (fbm(N, N, 1840, cells=8, octaves=2) > 0.35)
        cv.tint('#7a4a22', np.where(rust, 0.25 + 0.25 * (Y > 18), 0))
    if v == 2:   # a missing tile: cement bed with trowel ridges
        hole = (X >= 17) & (X <= 23) & (Y >= 9) & (Y <= 15)
        cidx = np.full((N, N), 2) + ((X + Y) % 3 == 0) - (Y == 9) - (X == 17)
        cv.put(CEMENT, cidx, hole)
        hr = rim(hole, wrap=False)
        cv.put(AZ, np.full((N, N), 8), hr['out_below'])
        chip = (X >= 9) & (X <= 11) & (Y >= 25) & (Y <= 26)
        cv.put(CEMENT, np.full((N, N), 4), chip)
    if v == 3:   # grime: dark grout and a brown streak from a dripping tap
        cv.put(GROUT, np.full((N, N), 0), grout & (Y > 16))
        st = (np.abs(X - 12) <= 1 + (Y > 22)) & (Y > 4)
        cv.tint('#6b4a2a', np.where(st, 0.22 + 0.3 * (Y / 32), 0))
    return cv.out()


@painter('azulejo_guarda')
def p_azulejo_guarda(v):
    """Tile course with the black-and-green border band (guarda) at 3/4 height."""
    cv = Cv()
    cv.rgb[:] = 0
    base = T('azulejo', 0)
    cv.rgb = base[..., :3].astype(float)
    cv.a[:] = 255
    X, Y = cv.X, cv.Y
    GR = Ramp('#0f1f17', '#173024', '#214332', '#2c5740', '#3a6c50', '#4c8263')
    band = (Y >= 9) & (Y <= 15)
    gidx = np.full((N, N), 2) + (Y == 10) - (Y == 15)
    # diamond motif in the band
    d = np.abs((X % 8) - 3.5) + np.abs(Y - 12)
    gidx = np.where(d <= 2.5, 4 + (d <= 1), gidx)
    cv.put(GR, gidx, band)
    cv.put(GROUT, np.full((N, N), 2), (Y == 8) | (Y == 16) | (band & (X % 8 == 0)))
    return cv.out()


# =============================================================================================== FLOORS
def damero_tile(cv, x0, y0, black, seed, wear=0, chip_corners=(), crack=None):
    """One 15x15 mosaic tile of the damero at (x0, y0)."""
    X, Y = cv.X, cv.Y
    m = (X >= x0) & (X < x0 + 15) & (Y >= y0) & (Y < y0 + 15)
    lx, ly = X - x0, Y - y0
    f = fbm(N, N, seed, cells=4, octaves=3)
    rng = np.random.default_rng(seed)
    if black:
        ramp, base = TILE_K, 3
        idx = np.full((N, N), base) + posterize(f, [(0.64, 1), (0.36, -1)])
        # dull scuffed polish: lighter cloudy zone
        sc = fbm(N, N, seed + 3, cells=2, octaves=2) > (0.58 - 0.05 * wear)
        idx += sc.astype(int)
        # fine light scratches
        for k in range(2 + wear):
            sx, sy = x0 + rng.integers(2, 12), y0 + rng.integers(2, 12)
            ang = rng.uniform(0, math.pi)
            L = rng.integers(3, 7)
            pts = line_px(sx, sy, sx + math.cos(ang) * L, sy + math.sin(ang) * L)
            sm = path_mask(pts, wrap=False) & m
            idx = np.where(sm, 5 + (k % 2), idx)
        # calcareous flecks
        fl = (fbm(N, N, seed + 9, cells=16, octaves=1) > 0.83) & m
        idx = np.where(fl, idx + 2, idx)
    else:
        ramp, base = TILE_W, 5
        idx = np.full((N, N), base) + posterize(f, [(0.66, 1), (0.40, -1)])
        # yellowed, dirtier towards the grout
        idx -= ((lx == 0) | (ly == 0) | (lx == 14) | (ly == 14)).astype(int) * (f > 0.4)
        # faint grey veins
        vp = wander([(x0 + rng.integers(0, 6), y0 + rng.integers(0, 15)), (x0 + 14, y0 + rng.integers(0, 15))],
                    seed + 5, amp=2.5)
        vm = path_mask(vp, wrap=False) & m & (fbm(N, N, seed + 6, cells=8, octaves=1) > 0.4)
        idx = np.where(vm, idx - 2, idx)
        if wear:
            dirt = fbm(N, N, seed + 7, cells=4, octaves=2) > 0.62
            idx = np.where(dirt, idx - 1, idx)
    # bevel: top/left edge catches light, bottom/right edge shaded
    idx = np.where(m & ((ly == 0) | (lx == 0)), idx + 1, idx)
    idx = np.where(m & ((ly == 14) | (lx == 14)), idx - 1, idx)
    cv.put(ramp, idx, m)
    # chipped corners -> grout/cement shows
    for (cx, cy) in chip_corners:
        ch = m & (np.abs(lx - cx) + np.abs(ly - cy) <= 2)
        cv.put(CEMENT, np.full((N, N), 3), ch)
        cv.put(CEMENT, np.full((N, N), 1), ch & ((np.abs(lx - cx) + np.abs(ly - cy)) == 2))
    if crack is not None:
        pts = wander(crack, seed + 11, amp=0.7, depth=3)
        cm = path_mask(pts, wrap=False) & m
        # a short branch off the middle
        mid = pts[len(pts) // 2]
        br = wander([mid, (mid[0] + rng.integers(-4, 5), mid[1] + rng.choice([-5, 5]))], seed + 12, amp=1.0)
        cm |= path_mask(br, wrap=False) & m
        cv.put(GROUT, np.full((N, N), 0), cm)
        lip = nb(cm, -1, 0, False) & m & ~cm
        cv.put(ramp, np.full((N, N), base + 1), lip)
    return m


@painter('damero')
def p_damero(v, kind='clean'):
    cv = Cv()
    X, Y = cv.X, cv.Y
    grout = (X % 16 == 0) | (Y % 16 == 0)
    gidx = np.full((N, N), 2) + posterize(fbm(N, N, 1900 + v, cells=8, octaves=1), [(0.6, 1), (0.3, -1)])
    cv.put(GROUT, gidx, grout)
    rng = np.random.default_rng(1910 + v + (100 if kind != 'clean' else 0))
    for ty in range(2):
        for tx in range(2):
            black = (tx + ty) % 2 == 1
            chips = []
            crack = None
            if kind == 'cracked':
                if (tx, ty) == ((v + 1) % 2, v % 2) or v == 2:
                    y0 = int(rng.integers(2, 13))
                    crack = [(tx * 16 + 1, ty * 16 + 1 + y0), (tx * 16 + 5, ty * 16 + 1 + y0 + rng.integers(-2, 3)),
                             (tx * 16 + 10, ty * 16 + 1 + int(rng.integers(3, 12))), (tx * 16 + 15, ty * 16 + 1 + int(rng.integers(2, 13)))]
                if rng.random() < 0.6:
                    chips.append([(0, 0), (14, 0), (0, 14), (14, 14)][rng.integers(0, 4)])
            damero_tile(cv, tx * 16 + 1, ty * 16 + 1, black, 1920 + v * 4 + ty * 2 + tx + (50 if kind != 'clean' else 0),
                        wear=1 if kind != 'clean' else (v % 2), chip_corners=chips, crack=crack)
    if kind == 'missing':
        # one tile gone: recessed cement bed (shadowed rim), trowel ridges, grit and two broken shards
        tx, ty = [(0, 0), (1, 1), (1, 0)][v % 3]
        hole = (X >= tx * 16 + 1) & (X <= tx * 16 + 15) & (Y >= ty * 16 + 1) & (Y <= ty * 16 + 15)
        cidx = np.full((N, N), 1) + posterize(fbm(N, N, 1991 + v, cells=8, octaves=2), [(0.66, 1), (0.30, -1)])
        cidx += (((X - Y) % 4) == 0).astype(int)                 # trowel combing ridges
        r = rim(hole, wrap=False)
        cidx = np.where(r['in_top'], 0, cidx)
        cidx = np.where(r['in_left'] & ~r['in_top'], 1, cidx)
        cidx = np.where(nb(r['in_top'], 1, 0, False) & hole, cidx - 1, cidx)
        cv.put(CEMENT, cidx, hole)
        cv.put(GROUT, np.full((N, N), 1), r['out_below'] | r['out_right'] | r['out_above'] | r['out_left'])
        for k, (sx, sy) in enumerate(poisson(1995 + v, 3, 4, keep=lambda x, y: hole[int(y), int(x)] and not r['in_top'][int(y), int(x)])):
            shard = (X >= sx) & (X <= sx + 2) & (Y == sy) | (X >= sx) & (X <= sx + 1) & (Y == sy + 1)
            shard &= hole
            rr, b0 = (TILE_K, 4) if k % 2 else (TILE_W, 3)
            cv.put(rr, np.full((N, N), b0), shard)
            cv.put(rr, np.full((N, N), b0 + 2), shard & (Y == sy))
            cv.put(CEMENT, np.full((N, N), 0), nb(shard, 1, 0, False) & hole & ~shard)
    return cv.out()


PAINTERS['damero_roto'] = lambda v: p_damero(v, 'cracked')
PAINTERS['damero_faltante'] = lambda v: p_damero(v, 'missing')


@painter('damero_huellas')
def p_damero_huellas(v):
    """Damero with small muddy shoe prints of a girl (guillerminas) walking across."""
    base = T('damero', v % 2)
    cv = Cv()
    cv.rgb = base[..., :3].astype(float)
    cv.a[:] = 255
    X, Y = cv.X, cv.Y
    SHOE = ['.###.', '#####', '#####', '#####', '#####', '.###.', '.....', '.###.', '.###.']
    sm = np.array([[c == '#' for c in row] for row in SHOE], bool)
    m = np.zeros((N, N), bool)
    if v == 0:   # walking north (up the texture)
        stamp(m, sm, 7, 4)
        stamp(m, sm, 13, 19)
    else:        # walking east
        sm = sm.T[:, ::-1]
        stamp(m, sm, 4, 7)
        stamp(m, sm, 19, 13)
    n = fbm(N, N, 2000 + v, cells=16, octaves=1)
    m &= n > 0.18
    cv.tint('#5b4936', np.where(m, 0.62 + 0.2 * (n > 0.6), 0))
    # tread: lighter dried crumbs inside the print
    cv.tint('#7a6a54', np.where(m & ((X + 2 * Y) % 5 == 0), 0.6, 0))
    return cv.out()


# --- classroom floorboards
def boards(v, worn=False, seed=0, joints=None):
    cv = Cv()
    X, Y = cv.X, cv.Y
    rng = np.random.default_rng(2100 + v + seed)
    row = Y // 8
    jy = Y % 8
    if joints is None:
        joints = [[(5 + 9 * v) % 32], [], [(21 + 5 * v) % 32], [(13 + 11 * v) % 32] if v % 2 else []]
    lab = row * 4
    for r, js in enumerate(joints):
        for jx in js:
            lab = np.where((row == r) & (X >= jx), lab + 1, lab)
    tone = rng.choice([-1, 0, 0, 1], 20)
    g = np.zeros((N, N), int)
    for r in range(4):
        gr = wood_grain(N, N, 2110 + v * 7 + seed + r * 13, 'x', warp=1.2, pores=0.02, tones=(-1, 0, 0, 0, 0, 1))
        g = np.where(row == r, gr, g)
    big = fbm(N, N, 2120 + v + seed, cells=2, octaves=2, ax=0.5, ay=4)
    idx = 4 + tone[lab % 20] + g + np.where(big > 0.75, 1, 0) - np.where(big < 0.22, 1, 0)
    # board edges: gap at top row, bevel below, darker bottom row
    idx = np.where(jy == 0, 0, idx)
    idx = np.where(jy == 1, idx + 1, idx)
    idx = np.where(jy == 7, idx - 1, idx)
    # butt joints + nail pairs
    for r, js in enumerate(joints):
        for jx in js:
            jm = (row == r) & (X == jx) & (jy > 0)
            idx = np.where(jm, 1, idx)
            idx = np.where((row == r) & (X == (jx + 1) % 32) & (jy > 0), idx + 1, idx)
            for ny in (2, 5):
                nx = (jx + 2) % 32
                idx[r * 8 + ny, nx] = 1
    # knots on some boards
    for k in range(1 if v == 1 else 0):
        r = rng.integers(0, 4)
        kx = rng.integers(3, 29)
        ky = r * 8 + 4
        d = ((X - kx) / 1.6) ** 2 + ((Y - ky) / 1.0) ** 2
        ring = (d >= 1) & (d < 3.2) & (row == r) & (jy > 1) & (jy < 7)
        idx = np.where(ring & (Y < ky), idx + 1, idx)
        idx = np.where(ring & (Y >= ky), idx - 1, idx)
        idx = np.where((d < 1) & (row == r), 1, idx)
    return cv, idx, lab


@painter('tablas')
def p_tablas(v):
    cv, idx, lab = boards(v)
    cv.put(FLOOR, idx)
    return cv.out()


@painter('tablas_gastadas')
def p_tablas_gastadas(v):
    """Worn path + arcs of scratches left by the desks dragged across the floor."""
    cv, idx, lab = boards(v, seed=40)
    X, Y = cv.X, cv.Y
    wear = rank(fbm(N, N, 2200 + v, cells=2, octaves=3)) > 0.62
    wear &= (Y % 8 != 0)
    cv.put(FLOOR, idx + wear.astype(int))
    cv.tint('#8a7a66', np.where(wear, 0.18, 0))
    rng = np.random.default_rng(2210 + v)
    for k in range(3):
        cx, cy, R = rng.uniform(-10, 40), rng.uniform(40, 60), rng.uniform(26, 40)
        a0 = rng.uniform(-2.2, -1.0)
        pts = []
        for t in np.linspace(a0, a0 + 0.55, 30):
            pts.append((int(cx + math.cos(t) * R), int(cy + math.sin(t) * R)))
        m = np.zeros((N, N), bool)
        for a, b in zip(pts, pts[1:]):
            m |= path_mask(line_px(*a, *b), wrap=False)
        m &= (Y % 8 != 0)
        cv.put(FLOOR, np.full((N, N), 7 - (k % 2)), m)
        cv.put(FLOOR, np.full((N, N), 2), nb(m, -1, 0, False) & ~m & (Y % 8 != 0))
    return cv.out()


@painter('tabla_floja')
def p_tabla_floja(v):
    """A loose, creaking board: darker, warped, a popped nail and a crack along the grain."""
    cv, idx, lab = boards(v, seed=80, joints=[[7], [], [23], []])
    X, Y = cv.X, cv.Y
    loose = (Y // 8 == 1)
    idx = np.where(loose, idx - 2, idx)
    idx = np.where(loose & (Y % 8 == 1), idx + 3, idx)
    idx = np.where((Y == 16) | (Y == 8), 0, idx)
    cv.put(FLOOR, idx)
    pts = wander([(3, 12), (17, 13), (29, 12)], 2300, amp=0.8)
    cm = path_mask(pts, wrap=False) & loose
    cv.put(FLOOR, np.full((N, N), 0), cm)
    # popped nails: raised, shiny heads
    for nx in (5, 26):
        cv.put(Ramp('#3a3a3e', '#6a6a70', '#9a9aa0'), np.full((N, N), 2), (X == nx) & (Y == 10))
        cv.put(Ramp('#3a3a3e', '#6a6a70', '#9a9aa0'), np.full((N, N), 0), (X == nx) & (Y == 11))
    return cv.out()


# --- ceilings
@painter('cielorraso')
def p_cielorraso(v):
    """Lime ceiling: greyer, sagging cracks along the reed lath, brown water rings, a fallen patch in v3."""
    cv = Cv()
    idx = lime_idx(v + 90) - 1
    X, Y = cv.X, cv.Y
    cv.put(CAL, idx)
    if v in (1, 3):
        for k, pts in enumerate(([(0, 9), (11, 11), (22, 8), (32, 9)], [(14, 0), (16, 13), (13, 22)])):
            p = wander(pts, 2400 + v * 3 + k, amp=2)
            m = path_mask(p, wrap=False)
            cv.put(CAL, idx - 3, m)
            cv.put(CAL, idx + 1, nb(m, -1, 0, False) & ~m)
    if v == 2:   # water rings
        f = fbm(N, N, 2410, cells=4, octaves=2)
        d = np.sqrt((X - 16) ** 2 + (Y - 15) ** 2) + (f - 0.5) * 8
        st = d < 12
        cv.put(CAL_STAIN, idx - 1 - (d < 7), st)
        for rr in (12, 7):
            ring = (np.abs(d - rr) < 0.8)
            cv.put(CAL_STAIN, np.full((N, N), 2), ring)
    if v == 3:   # plaster fallen: the cañizo (reed lath) shows
        hole = blob(N, N, 20, 20, 7.5, 6, 2420, rough=0.4)
        REED = Ramp('#2e2316', '#46351f', '#5e4a2b', '#776039', '#8f7749')
        ridx = np.where(X % 3 == 0, 1, 3 + (Y % 7 == 0))
        ridx += posterize(fbm(N, N, 2421, cells=8, octaves=1), [(0.6, 1)])
        r = rim(hole, wrap=False)
        ridx -= np.where(r['in_top'] | r['in_left'], 2, 0)
        cv.put(REED, ridx, hole)
        cv.put(RENDER, np.full((N, N), 5), r['out_below'] | r['out_right'])
        cv.put(RENDER, np.full((N, N), 3), (r['out_above'] | r['out_left']))
    return cv.out()


@painter('cielorraso_tablas')
def p_cielorraso_tablas(v):
    """Tongue-and-groove board ceiling (machimbre), boards 6.4 px... 5 per block, aged dark varnish."""
    cv = Cv()
    X, Y = cv.X, cv.Y
    lab = X // 8
    g = fbm(N, N, 2500 + v, cells=2, octaves=3, ax=6, ay=0.25)
    rng = np.random.default_rng(2510 + v)
    tone = rng.integers(-1, 2, 4)
    idx = 4 + tone[lab] + posterize(g, [(0.62, 1), (0.4, -1)])
    idx = np.where(X % 8 == 0, 0, idx)
    idx = np.where(X % 8 == 1, idx + 1, idx)
    idx = np.where(X % 8 == 7, idx - 1, idx)
    cv.put(WOOD_D, idx + 1)
    if v == 1:
        st = blob(N, N, 10, 18, 9, 6, 2520, rough=0.4)
        cv.tint('#6e5a40', np.where(st, 0.3, 0))
        tide = st & ~erode(st, 1, False)
        cv.tint('#1a100a', np.where(tide, 0.5, 0))
    return cv.out()


# --- courtyard paving
@painter('patio_lajas')
def p_patio_lajas(v):
    """Courtyard flagstones: rectangular limestone slabs in random bond (rows of 10/12/10 px, slab lengths 9-20 px),
    worn rounded arrises, chipped corners, dark earthy joints with grass and moss."""
    cv = Cv()
    X, Y = cv.X, cv.Y
    rng = np.random.default_rng(2900 + v)
    rows = [(0, 10), (10, 12), (22, 10)]
    lab = -np.ones((N, N), int)
    n = 0
    common = np.random.default_rng(2899)
    for r, (y0, hh) in enumerate(rows):
        # slab boundaries along the row (periodic); first cut shared by all variants keeps the edges consistent
        x = int(common.integers(0, 8)) + r * 5
        cuts = [x]
        while True:
            L = int(rng.integers(9, 21))
            if cuts[-1] + L >= x + N - 6:
                break
            cuts.append(cuts[-1] + L)
        for a, b in zip(cuts, cuts[1:] + [x + N]):
            for xx in range(a + 1, b):
                for yy in range(y0 + 1, y0 + hh):
                    lab[yy % N, xx % N] = n
            n += 1
    joint = lab < 0
    tone = rng.choice([-1, 0, 0, 0, 1], n)
    f = fbm(N, N, 2910 + v, cells=4, octaves=3)
    idx = 4 + tone[np.maximum(lab, 0)] + posterize(f, [(0.72, 1), (0.26, -1)])
    idx = relief(idx, 2920, 2921 + v, count=16, mind=4.5, body=-1, light=1)
    idx = bevel(idx, lab, hi=1, lo=-1)
    # chipped corners: knock a 2-3 px bite out of some slab corners (becomes joint)
    for k in range(n):
        ys, xs = np.nonzero(lab == k)
        if len(xs) == 0 or rng.random() < 0.5:
            continue
        cx, cy = (xs.min(), ys.min()) if rng.random() < 0.5 else (xs.max(), ys.max())
        bite = (np.abs(X - cx) + np.abs(Y - cy) <= 1) & (lab == k)
        joint |= bite
        lab = np.where(bite, -1, lab)
    cv.put(STONE, idx)
    jidx = np.full((N, N), 1) + posterize(fbm(N, N, 2930 + v, cells=8, octaves=1), [(0.6, 1)])
    cv.put(Ramp('#231d16', '#33291f', '#463829'), jidx, joint)
    gr = joint & (fbm(N, N, 2940 + v, cells=8, octaves=2) > 0.58)
    GRASS = Ramp('#2b3a1c', '#3d5226', '#516a30', '#68833d')
    cv.put(GRASS, np.full((N, N), 1) + posterize(fbm(N, N, 2941 + v, cells=16, octaves=1), [(0.5, 1), (0.75, 1)]), gr)
    blade = nb(gr, -1, 0) & ~joint & (fbm(N, N, 2942 + v, cells=16, octaves=1) > 0.6)
    cv.put(GRASS, np.full((N, N), 3), blade)
    # rain-darkened patches (where water stands)
    wet = rank(fbm(N, N, 2950 + v, cells=2, octaves=2)) > 0.85
    cv.mul(np.where(wet & ~joint, 0.88, 1.0))
    return cv.out()


# =============================================================================================== CHAPEL & CRYPT stone
SILLAR = Ramp('#2f2c2a', '#433f3b', '#58534c', '#6d675e', '#827b70', '#968e82', '#a9a194', '#bab3a6', '#c9c3b7')
CRIPTA = Ramp('#121412', '#1b1e1b', '#252924', '#30352e', '#3c4239', '#4a5045', '#595f52', '#6a6f60')
MOSS = Ramp('#1c2414', '#283419', '#36451f', '#465827')
LADRILLO_N = Ramp('#3b170f', '#561f14', '#712a18', '#8a361d', '#a04424', '#b1532d', '#bf6439', '#cb7849')
CEMENTO = Ramp('#3a3936', '#4d4b47', '#605e59', '#74716b', '#88857e', '#9b9891')


def ashlar_layout(v, course=8, lengths=((16, 16), (12, 20), (20, 12), (16, 16)), offset=(0, 8, 4, 12)):
    lab = -np.ones((N, N), int)
    n = 0
    for r in range(N // course):
        y0 = r * course
        x = offset[r % len(offset)]
        for L in lengths[r % len(lengths)]:
            for yy in range(y0 + 1, y0 + course):
                for xx in range(x + 1, x + L):
                    lab[yy % N, xx % N] = n
            x += L
            n += 1
    return lab


@painter('sillar')
def p_sillar(v):
    """Chapel ashlar: dressed limestone blocks, fine joints, diagonal tooling marks, soot and damp variants."""
    cv = Cv()
    X, Y = cv.X, cv.Y
    lab = ashlar_layout(v)
    rng = np.random.default_rng(3000 + v)
    tone = rng.choice([-1, 0, 0, 0, 1], lab.max() + 1)
    f = fbm(N, N, 3010 + v, cells=4, octaves=3)
    idx = 5 + tone[np.maximum(lab, 0)] + posterize(f, [(0.72, 1), (0.28, -1)])
    # tooling: faint diagonal chisel strokes, different direction per block
    dirn = rng.choice([1, -1], lab.max() + 1)
    tool = (((X + Y * dirn[np.maximum(lab, 0)]) % 5) == 0) & (fbm(N, N, 3015 + v, cells=8, octaves=2) > 0.66)
    idx = np.where(tool & (lab >= 0), idx - 1, idx)
    idx = bevel(idx, lab, hi=1, lo=-1)
    cv.put(SILLAR, idx)
    cv.put(SILLAR, np.full((N, N), 2) + (nb(lab, -1, 0) < 0), lab < 0)
    if v == 1:   # candle soot rising from below
        sm = (Y > 10) & (fbm(N, N, 3020, cells=4, octaves=3) * (Y / 32.0) > 0.38)
        cv.tint('#1d1915', np.where(sm, 0.35, 0))
    if v == 2:   # damp: darker lower blocks with salt tide
        dm = (Y > 18 + 2 * np.sin(X / 5.0 * math.pi / 3.2) + (fbm(N, N, 3021, cells=4, octaves=2) - 0.5) * 4)
        cv.mul(np.where(dm, 0.86, 1.0))
        tide = dm & ~nb(dm, 1, 0)
        cv.tint('#d8d2c4', np.where(tide, 0.4, 0))
    if v == 3:   # one cracked block
        pts = wander([(5, 9), (10, 12), (14, 15)], 3030, amp=1.2)
        m = path_mask(pts) & (lab >= 0)
        cv.put(SILLAR, np.full((N, N), 1), m)
        cv.put(SILLAR, np.full((N, N), 7), nb(m, -1, 0) & ~m & (lab >= 0))
    return cv.out()


@painter('sillar_tallado')
def p_sillar_tallado(v):
    """Carved band: a blind gothic arcade of two pointed lancets with an oculus between their heads."""
    cv = Cv()
    X, Y = cv.X, cv.Y
    f = fbm(N, N, 3100, cells=4, octaves=3)
    idx = np.full((N, N), 5) + posterize(f, [(0.72, 1), (0.28, -1)])
    rec = np.zeros((N, N), bool)
    spring, hw = 13.0, 4.5
    for cx in (8.0, 24.0):
        body = (np.abs(X + 0.5 - cx) <= hw) & (Y >= spring) & (Y <= 27)
        h = spring - (Y + 0.5)
        half = np.sqrt(np.clip((2 * hw) ** 2 - h ** 2, 0, None)) - hw
        head = (Y < spring) & (np.abs(X + 0.5 - cx) <= half)
        rec |= body | head
    ring = np.abs(np.sqrt((X + 0.5 - 16) ** 2 + (Y + 0.5 - 6.5) ** 2) - 2.6) < 0.9
    rec |= ring
    rec |= ((X + 0.5 - 16) ** 2 + (Y + 0.5 - 6.5) ** 2 < 0.8)
    r = rim(rec, wrap=False)
    idx = np.where(rec, 3, idx)
    idx = np.where(r['in_top'] | r['in_left'], 1, idx)
    idx = np.where(r['in_bot'] | r['in_right'], 5, idx)
    idx = np.where(r['out_above'] | r['out_left'], idx + 1, idx)
    idx = np.where(r['out_below'] | r['out_right'], idx - 1, idx)
    # sill moulding under the arcade, joints top and bottom
    idx = np.where(Y == 28, 7, np.where(Y == 29, 5, np.where(Y == 30, 2, idx)))
    idx = np.where((Y == 0) | (Y == 31), 2, idx)
    cv.put(SILLAR, idx)
    if v == 1:
        cv.tint('#1d1915', np.where((Y > 14) & (fbm(N, N, 3110, cells=4, octaves=2) > 0.5), 0.3, 0))
    return cv.out()


@painter('sillar_moldura')
def p_sillar_moldura(v):
    """String course: a roll moulding with a hollow under it and a row of ballflowers."""
    cv = Cv()
    X, Y = cv.X, cv.Y
    idx = np.full((N, N), 5) + posterize(fbm(N, N, 3200, cells=4, octaves=3), [(0.72, 1), (0.28, -1)])
    prof = {9: 3, 10: 6, 11: 7, 12: 7, 13: 6, 14: 5, 15: 4, 16: 3, 17: 1, 18: 2, 19: 3, 20: 4, 21: 6, 22: 5}
    for y, t in prof.items():
        idx = np.where(Y == y, t, idx)
    for cx in (8, 24):
        d = (X - cx) ** 2 + (Y - 19.5) ** 2
        ball = d <= 5
        idx = np.where(ball, 5, idx)
        idx = np.where(ball & (Y < 19), 7, idx)
        idx = np.where(ball & (Y > 20), 3, idx)
        idx = np.where(((X - cx) ** 2 + (Y - 19.5) ** 2 <= 1.2), 2, idx)
    idx = np.where((Y == 0) | (Y == 31) | ((X % 16 == 4) & ((Y < 9) | (Y > 22))), 2, idx)
    cv.put(SILLAR, idx)
    return cv.out()


@painter('piso_capilla')
def p_piso_capilla(v):
    """Chapel floor: big square limestone flags (2 x 2 per block) of two slightly different stones, worn smooth."""
    cv = Cv()
    X, Y = cv.X, cv.Y
    lab = np.where((X % 16 == 0) | (Y % 16 == 0), -1, (Y // 16) * 2 + X // 16)
    rng = np.random.default_rng(3300 + v)
    tone = np.array([0, -1, -1, 0]) + rng.choice([0, 0, 1], 4) * (v > 0)
    f = fbm(N, N, 3310 + v, cells=4, octaves=3)
    idx = 5 + tone[np.maximum(lab, 0)] + posterize(f, [(0.7, 1), (0.3, -1)])
    idx = relief(idx, 3320, 3321 + v, count=10, mind=6, body=-1, light=1)
    worn = (fbm(N, N, 3330 + v, cells=2, octaves=2) > 0.55) & (lab >= 0)
    idx = np.where(worn, idx + 1, idx)
    idx = bevel(idx, lab, hi=1, lo=-1)
    cv.put(SILLAR, idx)
    cv.put(GROUT, np.full((N, N), 2), lab < 0)
    if v == 2:   # wax drips from candles
        WAX = Ramp('#b9af8e', '#cfc5a2', '#e2d9b8')
        for k, (x, y) in enumerate(poisson(3340, 3, 8, keep=lambda x, y: lab[int(y), int(x)] >= 0)):
            drop = blob(N, N, x, y, 1.6 + (k % 2), 1.2, 3341 + k, rough=0.3)
            cv.put(WAX, np.full((N, N), 1), drop)
            cv.put(WAX, np.full((N, N), 2), drop & ~nb(drop, 1, 0, False))
            cv.put(SILLAR, np.full((N, N), 3), nb(drop, 1, 0, False) & ~drop)
    return cv.out()


@painter('lapida_piso')
def p_lapida_piso(v):
    """Floor tomb slab: a single dark stone with a border, an engraved cross and worn lettering."""
    cv = Cv()
    X, Y = cv.X, cv.Y
    f = fbm(N, N, 3400, cells=4, octaves=3)
    idx = np.full((N, N), 4) + posterize(f, [(0.7, 1), (0.3, -1)])
    idx = relief(idx, 3410, 3411, count=10, mind=6, body=-1, light=1)
    border = (border_dist(N, N) == 2)
    idx = np.where(border, 2, idx)
    idx = np.where(border_dist(N, N) == 3, idx + 1, idx)
    cross = ((np.abs(X - 15.5) <= 1) & (Y >= 5) & (Y <= 17)) | ((np.abs(Y - 9.5) <= 1) & (X >= 11) & (X <= 20))
    r = rim(cross, wrap=False)
    idx = np.where(cross, 2, idx)
    idx = np.where(r['in_top'] | r['in_left'], 1, idx)
    idx = np.where(r['out_below'] | r['out_right'], idx + 1, idx)
    tm = np.zeros((N, N), bool)
    stamp(tm, tiny_mask('R.I.P.'.replace('.', '.')), 9, 19)
    stamp(tm, tiny_mask('1890'), 10, 25)
    idx = np.where(tm, 2, idx)
    idx = np.where(nb(tm, 1, 0) & ~tm, idx + 1, idx)
    idx = np.where(border_dist(N, N) == 0, 1, idx)
    cv.put(SILLAR, idx - 1)
    # worn: footsteps polished the middle, letters half gone
    cv.mul(np.where((fbm(N, N, 3420, cells=4, octaves=2) > 0.6) & tm, 1.25, 1.0))
    return cv.out()


def rubble(v, seed, ramp, mramp, nsites=9, mind=8.0, jitter=1.6, mortar_w=1.6, wrap=True):
    """Irregular rubble masonry (Voronoi stones with rounded outlines, thick mortar)."""
    cv = Cv()
    X, Y = cv.X, cv.Y
    sites = poisson(seed, nsites, mind)
    warp = (fbm(N, N, seed + 1, cells=4, octaves=2) - 0.5) * jitter * 2
    best = np.full((N, N), 1e9)
    second = np.full((N, N), 1e9)
    lab = np.zeros((N, N), int)
    for k, (sx, sy) in enumerate(sites):
        for ox in (-N, 0, N):
            for oy in (-N, 0, N):
                d = np.sqrt(((X + warp) - sx - ox) ** 2 * 1.0 + ((Y - warp) - sy - oy) ** 2 * 1.35)
                upd = d < best
                second = np.where(upd, best, np.minimum(second, d))
                lab = np.where(upd, k, lab)
                best = np.where(upd, d, best)
    mortar = (second - best) < mortar_w
    lab = np.where(mortar, -1, lab)
    rng = np.random.default_rng(seed + 2)
    tone = rng.choice([-1, 0, 0, 1], len(sites))
    f = fbm(N, N, seed + 3, cells=4, octaves=3)
    idx = 4 + tone[np.maximum(lab, 0)] + posterize(f, [(0.7, 1), (0.3, -1)])
    # each stone domed: lit towards its upper-left, shaded at lower-right
    idx = bevel(idx, lab, hi=1, lo=-1, hi2=1, lo2=-1)
    cv.put(ramp, idx)
    midx = np.full((N, N), 2) + posterize(fbm(N, N, seed + 4, cells=8, octaves=1), [(0.6, 1)])
    midx -= (nb(lab, 1, 0) >= 0).astype(int)
    cv.put(mramp, midx, mortar)
    return cv, lab, mortar


@painter('cripta_piedra')
def p_cripta_piedra(v):
    cv, lab, mortar = rubble(v, 3500 + v * 11, CRIPTA, MORTAR, nsites=9)
    X, Y = cv.X, cv.Y
    cv.mul(np.where(mortar, 0.62, 1.0))   # mortar darkened by damp
    # mould and moss creeping in the joints, salt bloom on some stones
    mo = mortar & (fbm(N, N, 3510 + v, cells=8, octaves=2) > 0.55)
    cv.put(MOSS, np.full((N, N), 1) + (fbm(N, N, 3511 + v, cells=16, octaves=1) > 0.6), mo)
    if v == 1:
        sb = (lab >= 0) & (fbm(N, N, 3520, cells=4, octaves=3) > 0.66)
        cv.tint('#9a9a8a', np.where(sb, 0.3, 0))
    if v == 2:  # water seeping: dark wet streak with a glossy edge
        wx = 12 + 2 * np.sin(Y / 6.0) + (fbm(N, N, 3530, cells=2, octaves=2) - 0.5) * 4
        wet = np.abs(X - wx) < 2.5 + Y / 16.0
        cv.mul(np.where(wet, 0.72, 1.0))
        cv.tint('#7d8a80', np.where(wet & (np.abs(X - wx) < 0.5) & (Y % 3 != 0), 0.3, 0))
    return cv.out()


@painter('cripta_piso')
def p_cripta_piso(v):
    """Crypt floor: uneven dark flags, mud in the joints, a puddle sheen in v2."""
    cv, lab, mortar = rubble(v, 3600 + v * 7, CRIPTA, Ramp('#15120e', '#211c16', '#2e271f', '#3b3329'), nsites=5, mind=12, mortar_w=1.2)
    X, Y = cv.X, cv.Y
    cv.mul(1.12)
    if v == 2:   # mud and grit washed in over the stones
        mud = (fbm(N, N, 3610, cells=4, octaves=3) > 0.58)
        cv.put(Ramp('#1e1912', '#2a231a', '#373024'), np.full((N, N), 1) + (fbm(N, N, 3611, cells=16, octaves=1) > 0.6), mud)
    return cv.out()


def brick_new(cv, seed, crack=None, mortar_bulge=True):
    """1984 bricked-up wall: rough common bricks, sloppy grey cement squeezing out of the joints."""
    X, Y = cv.X, cv.Y
    lab, mor = brick_layout(8, 2, (16, 16), 8, seed)
    rng = np.random.default_rng(seed)
    nbk = lab.max() + 1
    tone = rng.choice([-1, 0, 0, 1], nbk)
    # bricks laid crooked: each brick shifted up/down by a pixel
    idx = np.where(lab >= 0, 4 + tone[np.maximum(lab, 0)], 0)
    f = fbm(N, N, seed + 5, cells=8, octaves=2)
    idx += posterize(f, [(0.68, 1), (0.3, -1)])
    idx = bevel(idx, lab, hi=1, lo=-1)
    cv.put(LADRILLO_N, idx, lab >= 0)
    midx = np.full((N, N), 3) + posterize(fbm(N, N, seed + 6, cells=8, octaves=2), [(0.6, 1), (0.35, -1)])
    cv.put(CEMENTO, midx, mor)
    if mortar_bulge:   # cement squeezed out over the brick edges, smeared
        sq = (dilate(mor, 1) & ~mor) & (fbm(N, N, seed + 7, cells=8, octaves=2) > 0.55)
        cv.put(CEMENTO, np.full((N, N), 4), sq)
        cv.put(CEMENTO, np.full((N, N), 1), nb(sq, -1, 0) & ~sq & ~mor)
        sm = (lab >= 0) & (fbm(N, N, seed + 8, cells=4, octaves=2) > 0.74)
        cv.tint('#8a867c', np.where(sm, 0.45, 0))
    return lab, mor


@painter('muro_ladrillo')
def p_muro_ladrillo(v):
    cv = Cv()
    brick_new(cv, 3700 + v * 13)
    return cv.out()


@painter('muro_ladrillo_grieta')
def p_muro_ladrillo_grieta(v):
    """The bricked wall with a crack stepping along the joints, entering top-centre and leaving bottom-centre so
    stacked blocks make one long crack; black void behind, cement crumbs."""
    cv = Cv()
    X, Y = cv.X, cv.Y
    lab, mor = brick_new(cv, 3800 + v * 13)
    pts = [(16, 0)]
    xs = [16, 13, 19, 14, 17] if v == 0 else [16, 20, 15, 18, 16]
    for r in range(4):
        y0 = r * 8
        x = xs[r]
        pts += [(x, y0), (x, y0 + 6), (xs[r + 1], y0 + 6), (xs[r + 1], y0 + 8)]
    pts.append((16, 31))
    m = np.zeros((N, N), bool)
    for a, b in zip(pts, pts[1:]):
        m |= path_mask(line_px(*a, *b), wrap=False)
    wide = m | (nb(m, 0, 1, False) & (Y > 8) & (Y < 26))
    cv.col('#020203', wide)
    cv.put(CEMENTO, np.full((N, N), 5), nb(wide, -1, 0, False) & ~wide)
    cv.put(LADRILLO_N, np.full((N, N), 1), nb(wide, 0, -1, False) & ~wide & (lab >= 0))
    return cv.out()


@painter('mosaico_bano')
def p_mosaico_bano(v):
    """Bathroom floor: small white hexagon-like octagon tiles with black dots (venecita), grimy grout."""
    cv = Cv()
    X, Y = cv.X, cv.Y
    lx, ly = X % 8, Y % 8
    oct_ = (np.abs(lx - 3.5) + np.abs(ly - 3.5) <= 5.5) & (lx > 0) & (ly > 0)
    dot = ((X % 8 == 0) & (Y % 8 == 0)) | ((X % 8 == 0) & (Y % 8 == 1)) | ((X % 8 == 1) & (Y % 8 == 0))
    dotm = (np.abs(((X + 0) % 8) - 0) <= 0) & False
    corner = ~oct_
    idx = np.full((N, N), 5) + posterize(fbm(N, N, 3900 + v, cells=8, octaves=2), [(0.7, 1), (0.3, -1)])
    idx = np.where(oct_ & ((ly == 1) | (lx == 1)), idx + 1, idx)
    idx = np.where(oct_ & ((ly == 7) | (lx == 7)), idx - 1, idx)
    cv.put(AZ, idx)
    k = (np.abs(lx - 0) + np.abs(ly - 0) <= 1) | (np.abs(lx - 8) + np.abs(ly - 0) <= 1)
    cv.put(TILE_K, np.full((N, N), 3) + ((lx == 0) & (ly == 0)), corner)
    cv.put(GROUT, np.full((N, N), 4), oct_ & ((lx == 0) | (ly == 0)))
    if v == 1:
        cv.tint('#5a4a32', np.where(fbm(N, N, 3910, cells=4, octaves=2) > 0.6, 0.3, 0))
    return cv.out()


@painter('baldosa_colorada')
def p_baldosa_colorada(v):
    """Kitchen floor: red cement tiles (baldosa colorada), 20 cm, waxed and worn grey in the walking lanes."""
    cv = Cv()
    X, Y = cv.X, cv.Y
    lab = np.where((X % 8 == 0) | (Y % 8 == 0), -1, (Y // 8) * 4 + X // 8)
    rng = np.random.default_rng(3950 + v)
    tone = rng.choice([-1, 0, 0, 1], 16)
    idx = 4 + tone[np.maximum(lab, 0)] + posterize(fbm(N, N, 3951 + v, cells=8, octaves=2), [(0.7, 1), (0.3, -1)])
    idx = bevel(idx, lab, hi=1, lo=-1)
    cv.put(BAL_R, idx)
    cv.put(GROUT, np.full((N, N), 2), lab < 0)
    wear = (fbm(N, N, 3952 + v, cells=2, octaves=3) > 0.55) & (lab >= 0)
    cv.tint('#7d6f62', np.where(wear, 0.3, 0))
    if v == 1:   # grease stain near the stove
        st = blob(N, N, 12, 20, 9, 6, 3953, rough=0.4)
        cv.mul(np.where(st, 0.72, 1.0))
    return cv.out()


# =============================================================================================== FURNITURE PAINTERS
IRON = Ramp('#0d0d10', '#151418', '#1e1c20', '#28252a', '#343034', '#423d3e', '#544e4c', '#6a625d')
RUST = Ramp('#2e170f', '#462114', '#5e2d18', '#77391d', '#8f4824', '#a85b2e', '#bd7039')
GREEN = Ramp('#0f1a13', '#16241b', '#1e3124', '#273f2e', '#314f39', '#3c6045', '#4a7354', '#5d8866', '#76a07c')
WEATHER = Ramp('#2f2b26', '#433d36', '#58514a', '#6e665d', '#857c71', '#9b9285', '#b0a799')  # grey bare wood
GLASS = Ramp('#141c1f', '#222d31', '#334247', '#46585d', '#5c7074', '#788b8d', '#9cadad', '#c3d0ce', '#e4ece8')
BRASS = Ramp('#2b1d0b', '#47310f', '#664a17', '#866424', '#a37f35', '#bf9b4b', '#d6b768', '#ead290')
ENAMEL = Ramp('#3d4148', '#6f747b', '#a3a8ad', '#c9cdd0', '#e2e4e4', '#f1f2ef')
OAK = Ramp('#1a120c', '#271a11', '#362417', '#462f1e', '#573a25', '#68472e', '#7a5538', '#8d6443', '#a0754f')


def fkey(part, face):
    return shash(part.frm, part.to, face) % 9973


def face_axis(face, w, h, along=None):
    if along:
        return along
    return 'x' if w >= h else 'y'


def border_px(w, h):
    Y, X = np.mgrid[0:h, 0:w]
    return np.minimum(np.minimum(X, w - 1 - X), np.minimum(Y, h - 1 - Y)), X, Y


def pp_plaster(name='revoque', v=0):
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


def F(key, es, en, parts, **kw):
    kw.setdefault('kit', KIT)
    kw.setdefault('sound', 'wood')
    return Furniture('colegio_' + key, es, en, parts=parts, **kw)


# =============================================================================================== WINDOWS
WIN_R = 6.0          # arch radius of the window head (opening 12 wide)
WIN_C = (8.0, 10.0)  # arch centre in the upper block


def arch_y(x, cx=WIN_C[0], cy=WIN_C[1], r=WIN_R):
    d = r * r - (x - cx) ** 2
    return cy + math.sqrt(d) if d > 0 else cy


def jambs(name='revoque'):
    pl = pp_plaster(name)
    return [P((0, 0, 0), (2, 16, 16), pl, name='jamb_l'), P((14, 0, 0), (16, 16, 16), pl, name='jamb_r')]


def reja_bars(y0, y1, top_clip=None, z0=0.6, z1=1.8):
    """Wrought-iron bars of a window grille (exterior side)."""
    parts = []
    it = pp_iron(seed=3, rust=0.3)
    for xc in (3.6, 6.2, 8.8 + 0.0, 11.4):
        x0, x1 = xc - 0.6, xc + 0.6
        top = y1 if top_clip is None else min(y1, top_clip((x0 + x1) / 2) - 0.2)
        if top > y0:
            parts.append(P((x0, y0, z0), (x1, top, z1), it))
    return parts


def window_parts(part='inf', glass=True, shutters=False, broken=False, wall='revoque'):
    """Tall colonial window in a 1-block-thick wall: plaster reveals, wooden frame and glazing bars in the middle of
    the wall, iron grille on the exterior side (north/front), arched head on the 'sup' piece."""
    parts = jambs(wall)
    wood = pp_wood(WOOD_D, 4, seed=11)
    sill = pp_wood(WOOD_D, 5, seed=12)
    stone = pp_plaster('revoque', 1)
    it = pp_iron(seed=5, rust=0.35)
    zf0, zf1 = 7.0, 9.0
    clip = None
    if part == 'inf':
        parts += [
            P((1, 0, -1.5), (15, 1.5, 6.5), stone, name='sill_out'),              # exterior plaster sill
            P((2, 0, 9.0), (14, 1.0, 16.4), sill, name='sill_in'),                # interior wooden sill board
            P((2, 1.0, zf0), (14, 2.5, zf1), wood, name='rail_b'),
            P((2, 2.5, zf0), (3.5, 16, zf1), wood, name='stile_l'),
            P((12.5, 2.5, zf0), (14, 16, zf1), wood, name='stile_r'),
            P((7.4, 2.5, 7.6), (8.6, 16, 8.4), wood, name='mull'),
            P((3.5, 9.0, 7.6), (12.5, 10.0, 8.4), wood, name='bar'),
            P((2, 1.5, 0.6), (14, 2.7, 1.8), it, name='reja_b'),
            P((2, 14.4, 0.6), (14, 15.6, 1.8), it, name='reja_m'),
        ]
        parts += reja_bars(1.5, 16)
        gy0 = 2.5
    elif part == 'med':
        parts += [
            P((2, 0, zf0), (3.5, 16, zf1), wood, name='stile_l'),
            P((12.5, 0, zf0), (14, 16, zf1), wood, name='stile_r'),
            P((2, 14.5, zf0), (14, 16, zf1), wood, name='meeting'),
            P((7.4, 0, 7.6), (8.6, 14.5, 8.4), wood, name='mull'),
            P((3.5, 7.0, 7.6), (12.5, 8.0, 8.4), wood, name='bar'),
            P((2, 7.4, 0.6), (14, 8.6, 1.8), it, name='reja_m'),
        ]
        parts += reja_bars(0, 16)
        gy0 = 0
    else:  # sup: arched head
        # plaster fill above the arch (stepped 1-unit columns) and the wooden arched frame under it
        pl = pp_plaster(wall)
        for xi in range(2, 14):
            xm = xi + 0.5
            ya = arch_y(xm)
            if ya < 16:
                parts.append(P((xi, ya, 0), (xi + 1, 16, 16), pl, name='arch_fill'))
            fa = arch_y(xm, r=WIN_R - 1.5)
            parts.append(P((xi, max(fa, 0), zf0), (xi + 1, ya, zf1), wood, name='arch_frame'))
        parts += [
            P((2, 0, zf0), (3.5, 10.0, zf1), wood, name='stile_l'),
            P((12.5, 0, zf0), (14, 10.0, zf1), wood, name='stile_r'),
            P((7.4, 0, 7.6), (8.6, 14.2, 8.4), wood, name='mull'),
            P((3.5, 6.0, 7.6), (12.5, 7.0, 8.4), wood, name='bar'),
            P((2, 6.4, 0.6), (14, 7.6, 1.8), it, name='reja_m'),
        ]
        parts += reja_bars(0, 16, top_clip=lambda x: arch_y(x))
        # fan of the grille: radial iron bars in the arch
        for ang in (35, 65, 115, 145):
            a = math.radians(ang)
            cx, cy = WIN_C
            x0, y0 = cx + math.cos(a) * 1.2, cy + math.sin(a) * 1.2
        parts.append(PL((2.2, 6.0, 1.2), (13.8, 16, 1.2), pp_fn(reja_fan), name='fan'))
        gy0 = 0
        clip = lambda x, y, z: (x - WIN_C[0]) ** 2 + (y - WIN_C[1]) ** 2 <= (WIN_R - 0.1) ** 2 if True else None
        clip = (lambda x, y, z: (y <= WIN_C[1]) | ((x - WIN_C[0]) ** 2 + (y - WIN_C[1]) ** 2 <= (WIN_R - 0.2) ** 2))
    if shutters:
        # closed green louvered shutters right behind the grille
        sh = pp_paint(GREEN, 4, seed=21, chip=0.3, louvers=True)
        shf = pp_paint(GREEN, 4, seed=22, chip=0.2)
        top = 16 if part != 'sup' else 10.0
        y0 = 2.5 if part == 'inf' else 0
        parts += [P((2.2, y0, 2.6), (7.9, top, 3.8), sh, name='leaf_l'), P((8.1, y0, 2.6), (13.8, top, 3.8), sh, name='leaf_r')]
        if part == 'sup':
            for xi in range(2, 14):
                ya = arch_y(xi + 0.5)
                parts.append(P((xi + 0.2 if xi == 2 else xi, 10.0, 2.6), (xi + 1 if xi < 13 else 13.8, ya, 3.8), shf, name='leaf_arch'))
    if glass:
        g = pp_glass(seed=31 + (part == 'sup'), clip=clip, crack=(9, 12) if broken else None)
        parts.append(PL((3.5, gy0, 8.0), (12.5, 16 if part != 'sup' else 16, 8.0), g, name='glass'))
    return parts


def reja_fan(face, w, h, part, cv):
    """Iron sunburst of the arched grille head (cut-out pixels on a plane)."""
    x, y, z = face_coords(part, face, w, h)
    cx, cy = WIN_C
    dx, dy = x - cx, y - cy
    r = np.sqrt(dx * dx + dy * dy)
    ang = np.degrees(np.arctan2(dy, dx))
    m = np.zeros((h, w), bool)
    m |= (np.abs(r - (WIN_R - 0.9)) < 0.55) & (dy >= -0.2)             # outer arc
    m |= (np.abs(r - 2.2) < 0.5) & (dy >= -0.2)                       # inner semicircle
    for a0 in (30, 60, 90, 120, 150):
        m |= (np.abs(ang - a0) < 3.2 * 2.2 / np.maximum(r, 0.6)) & (r > 2.2) & (r < WIN_R - 0.9) & (dy > 0)
    m |= (np.abs(dy) < 0.5) & (np.abs(dx) <= WIN_R - 0.6)               # spring bar
    idx = np.full((h, w), 3) + (np.roll(m, 1, 0) == False).astype(int)
    cv.put(IRON, idx, m)
    rr = m & (vnoise(w, h, max(1, w // 3), max(1, h // 3), 77) > 0.72)
    cv.put(RUST, np.full((h, w), 3), rr)


# =============================================================================================== TRANSOM, CORNICE, BEAM
def banderola_parts():
    """Transom over a door: plaster reveals, a wooden frame with a tilting glazed sash and diagonal glazing bars."""
    pl = pp_plaster('revoque')
    wood = pp_wood(WOOD_D, 4, seed=41)
    parts = [P((0, 12.5, 0), (16, 16, 16), pl, name='soffit'),
             P((0, 0, 0), (16, 12.5, 1.5), pl, name='face_out') if False else None]
    parts = [p for p in parts if p]
    parts += [
        P((0, 0, 12.5), (16, 1.5, 16), wood, name='lintel'),
        P((0, 1.5, 13.0), (1.5, 12.5, 15.5), wood, name='st_l'),
        P((14.5, 1.5, 13.0), (16, 12.5, 15.5), wood, name='st_r'),
        P((0, 11.0, 13.0), (16, 12.5, 15.5), wood, name='top'),
        P((1.5, 1.5, 13.6), (14.5, 2.6, 14.9), wood, name='sash_b'),
        P((1.5, 9.9, 13.6), (14.5, 11.0, 14.9), wood, name='sash_t'),
        P((7.5, 2.6, 13.9), (8.5, 9.9, 14.6), wood, name='sash_m'),
        PL((1.5, 2.6, 14.25), (14.5, 9.9, 14.25), pp_glass(seed=43, alpha=110), name='glass'),
    ]
    return parts


def cornisa_profile(along_x=True, plaster=None):
    """Crown moulding against the wall behind (z=16 side), at the top of the block (meets the ceiling)."""
    pl = plaster or pp_fn(cornisa_paint)
    if along_x:
        return [P((0, 13.0, 15.0), (16, 16, 16), pl, name='c0'),
                P((0, 14.0, 13.6), (16, 16, 15.0), pl, name='c1'),
                P((0, 14.8, 12.0), (16, 16, 13.6), pl, name='c2'),
                P((0, 12.2, 15.3), (16, 13.0, 16), pl, name='bead')]
    return [P((15.0, 13.0, 0), (16, 16, 16), pl, name='d0'),
            P((13.6, 14.0, 0), (15.0, 16, 16), pl, name='d1'),
            P((12.0, 14.8, 0), (13.6, 16, 16), pl, name='d2'),
            P((15.3, 12.2, 0), (16, 13.0, 16), pl, name='dbead')]


def cornisa_paint(face, w, h, part, cv):
    i, j = aligned_uv(part, face, w, h)
    tex = T('revoque', 0)
    base = tex[j, i][..., :3].astype(float)
    cv.rgb = base
    cv.a[:] = 255
    # soot/dust darkening at the underside and deep crevices
    if face == 'down':
        cv.mul(0.86)
    bd, X, Y = border_px(w, h)
    if face not in ('up', 'down') and h > 1:
        cv.mul(np.where(Y == h - 1, 0.9, 1.0))
        cv.mul(np.where(Y == 0, 1.06, 1.0))


def viga_parts(end=False):
    """Squared dark beam (adzed), running north-south under the ceiling."""
    wood = pp_fn(viga_paint)
    parts = [P((5, 9, 0), (11, 16, 16), wood, name='beam')]
    return parts


def viga_paint(face, w, h, part, cv):
    al = 'y' if face in ('up', 'down') else ('x' if face in ('north', 'south') else 'x')
    if face in ('west', 'east'):
        al = 'x'
    if face in ('north', 'south'):   # end grain
        idx = np.full((h, w), 3)
        Y, X = np.mgrid[0:h, 0:w]
        r = np.sqrt((X - w / 2 + 0.5) ** 2 + (Y - h / 2 + 0.5) ** 2)
        idx = idx + ((r.astype(int) % 3) == 0).astype(int) - (r < 1.5)
        idx = np.where(border_px(w, h)[0] == 0, idx - 1, idx)
        cv.put(WOOD_D, idx)
        return
    k = fkey(part, face)
    g = wood_grain(w, h, k + 3, al, period=False, warp=2.2, pores=0.05)
    idx = 4 + g
    # adze marks: shallow scallops across the grain every ~5 px
    Y, X = np.mgrid[0:h, 0:w]
    along = X if al == 'x' else Y
    across = Y if al == 'x' else X
    sc = ((along + (across // 4) * 3) % 9 == 0) & (fbm(w, h, k + 9, cells=2, octaves=1) > 0.4) if min(w, h) > 4 else np.zeros((h, w), bool)
    idx = np.where(sc, idx + 1, idx)
    bd = border_px(w, h)[0]
    idx = np.where(bd == 0, idx - 1, idx)
    # long drying check (crack) along the beam on the sides
    if face in ('west', 'east'):
        yy = h // 2 + (k % 3) - 1
        idx = np.where((Y == yy) & (X > 3) & (X < w - 5), 1, idx)
        idx = np.where((Y == yy + 1) & (X > 3) & (X < w - 5), idx + 1, idx)
    cv.put(WOOD_D, idx)


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


def wood_door_frame(cv, X, Y, gv, gh, ramp=WOOD_D, base=4, stile=4, top=4, bottom=8, rails=()):
    """Stiles, rails and the outer arris of a framed door; returns idx (openings filled later)."""
    st = (X < stile) | (X >= 32 - stile)
    idx = np.where(st, base + gv, base + gh)
    idx = np.where((X == 0) | (X == 31) | (Y == 0) | (Y == 63), idx - 2, idx)
    idx = np.where((X == 1) & (Y > 0) & (Y < 63), idx + 1, idx)
    idx = np.where((Y == 1) & (X > 0) & (X < 31), idx + 1, idx)
    return idx


@painter('door_aula')
def p_door_aula(num):
    cv, X, Y, gv, gh = door_base(WOOD_D, 3000 + num)
    idx = wood_door_frame(cv, X, Y, gv, gh)
    cst = (X >= 15) & (X <= 16) & (Y > 38) & (Y < 56)
    idx = np.where(cst, 4 + gv, idx)
    # glazed upper half
    idx = frame_opening(idx, 4, 4, 27, 29)
    gl = (X >= 5) & (X <= 26) & (Y >= 5) & (Y <= 28)
    mun = gl & (((X >= 15) & (X <= 16)) | ((Y >= 16) & (Y <= 17)))
    idx = np.where(mun, 5 + (X == 15) * 0 + (Y == 16), idx)
    # lower raised panels
    for (a, b) in ((4, 14), (17, 27)):
        idx = frame_opening(idx, a, 39, b, 55)
        idx, field, ins = raised_panel(idx, a + 1, 40, b - 1, 54, 2, 4 + gv, hi=(2, 1), lo=(-1, -1))
    # kick wear on the bottom rail, hand grime near the handle
    rng = np.random.default_rng(3100 + num)
    for k in range(6):
        x, y = int(rng.integers(2, 28)), int(rng.integers(57, 62))
        idx = np.where((Y == y) & (X >= x) & (X < x + int(rng.integers(2, 5))), idx + 2, idx)
    cv.put(WOOD_D, idx)
    door_glass(cv, gl & ~mun, 3200 + num)
    cv.tint('#1a120c', np.where((X >= 21) & (X <= 29) & (Y >= 36) & (Y <= 46) & (fbm(32, 64, 3300, cells=8, octaves=1) > 0.5), 0.25, 0))
    label = text_mask(f'{num}°')
    enamel_plate(cv, 9, 30, 14, 11, label[2:, :], chip=(20, 39) if num == 6 else None)
    lever_handle(cv, 27, 47)
    return cv.out()


@painter('door_direccion')
def p_door_direccion(v):
    cv, X, Y, gv, gh = door_base(WOOD_D, 3400)
    idx = wood_door_frame(cv, X, Y, gv, gh, base=4)
    cst = (X >= 15) & (X <= 16)
    idx = np.where(cst, 4 + gv, idx)
    for (a, b) in ((4, 14), (17, 27)):
        for (c, d) in ((4, 26), (38, 57)):
            idx = frame_opening(idx, a, c, b, d)
            idx, field, ins = raised_panel(idx, a + 1, c + 1, b - 1, d - 1, 2, 4 + gv, hi=(2, 1), lo=(-1, -1))
    cv.put(WOOD_D, idx)
    cv.tint('#4a1e10', 0.12)   # cedro: a warmer, redder wood than the classroom doors
    tm = tiny_mask('DIRECCIÓN')
    enamel_plate(cv, 0, 27, 32, 9, tm, ink='#2a1a08', base=BRASS, screws=False)
    lever_handle(cv, 27, 45)
    return cv.out()


@painter('door_celda')
def p_door_celda(v):
    """Plain plank door of the nuns' cells: four boards, two battens with clinched nails, iron latch."""
    cv = Cv(32, 64)
    X, Y = cv.X, cv.Y
    board = X // 8
    g = np.zeros((64, 32), int)
    for b in range(4):
        g = np.where(board == b, wood_grain(32, 64, 3500 + b * 7, 'y'), g)
    rng = np.random.default_rng(3510)
    tone = rng.choice([-1, 0, 0, 1], 4)
    idx = 4 + g + tone[board]
    idx = np.where(X % 8 == 0, 1, idx)
    idx = np.where(X % 8 == 1, idx + 1, idx)
    for (y0, y1) in ((7, 12), (51, 56)):
        bt = (Y >= y0) & (Y <= y1)
        bidx = 4 + wood_grain(32, 64, 3520 + y0, 'x')
        bidx = np.where(Y == y0, 6, np.where(Y == y1, 2, bidx))
        idx = np.where(bt, bidx, idx)
        idx = np.where((Y == y1 + 1), 1, idx)
        for x in (3, 11, 19, 27):
            idx = np.where((X == x) & ((Y == y0 + 2) | (Y == y1 - 2)), 1, idx)
    idx = np.where((X == 0) | (X == 31) | (Y == 0) | (Y == 63), idx - 1, idx)
    cv.put(OAK, idx)
    # iron thumb latch and keyhole plate
    cv.put(IRON, np.full((64, 32), 4) + (Y == 30), (X >= 21) & (X <= 28) & (Y >= 30) & (Y <= 31))
    cv.put(IRON, np.full((64, 32), 3), (X >= 25) & (X <= 27) & (Y >= 33) & (Y <= 37))
    cv.col('#060505', (X == 26) & (Y >= 34) & (Y <= 35))
    cv.put(RUST, np.full((64, 32), 3), (X >= 25) & (X <= 27) & (Y == 38))
    return cv.out()


def studs(cv, pts, big=False):
    X, Y = cv.X, cv.Y
    for (x, y) in pts:
        cv.put(IRON, np.full(X.shape, 2), (X == x) & (Y == y + 1) | (X == x + 1) & (Y == y + 1) | (X == x + 1) & (Y == y))
        cv.put(IRON, np.full(X.shape, 6), (X == x) & (Y == y))
        cv.put(WOOD_D, np.full(X.shape, 0), (X == x + 1) & (Y == y + 2) | (X == x + 2) & (Y == y + 1))


@painter('door_capilla')
def p_door_capilla(v):
    """Chapel door: heavy oak planks with deep V-joints, studded battens, forged strap hinges, ring knocker."""
    cv = Cv(32, 64)
    X, Y = cv.X, cv.Y
    board = X // 6 if True else 0
    g = np.zeros((64, 32), int)
    for b in range(6):
        g = np.where(board == b, wood_grain(32, 64, 3600 + b * 5, 'y', warp=2.2), g)
    tone = np.random.default_rng(3601).choice([-1, 0, 0, 1], 6)
    idx = 4 + g + tone[np.minimum(board, 5)]
    idx = np.where((X % 6 == 0) & (X > 0), 1, idx)
    idx = np.where((X % 6 == 1) & (X > 1), idx + 1, idx)
    idx = np.where((X == 0) | (X == 31) | (Y == 0) | (Y == 63), 1, idx)
    # weathering: bottom 10 px greyed and split
    cv.put(OAK, idx)
    low = Y > 52
    cv.tint('#6a6050', np.where(low & (fbm(32, 64, 3602, cells=8, octaves=2) > 0.45), 0.35, 0))
    # forged strap hinges (from the hinge side, x=0) with spear ends
    for yc in (9, 54):
        strap = (Y >= yc - 1) & (Y <= yc + 1) & (X <= 21)
        strap |= (X >= 22) & (X <= 24) & (np.abs(Y - yc) <= (24 - X))
        strap |= (X >= 19) & (X <= 21) & (np.abs(Y - yc) <= 2)
        cv.put(IRON, np.full((64, 32), 3) + (Y == yc - 1) * 2 - (Y == yc + 1), strap)
        cv.put(WOOD_D, np.full((64, 32), 0), nb(strap, 1, 0, False) & ~strap)
        for x in (3, 9, 15):
            cv.put(IRON, np.full((64, 32), 6), (X == x) & (Y == yc))
        cv.put(RUST, np.full((64, 32), 3), strap & (fbm(32, 64, 3603 + yc, cells=8, octaves=1) > 0.7))
    # rows of studs on the battens
    studs(cv, [(x, y) for y in (20, 43) for x in (3, 9, 15, 21, 27)])
    # ring knocker + lock plate
    ring = (np.abs(np.sqrt((X - 22.5) ** 2 + (Y - 33.5) ** 2) - 3.2) < 0.75)
    cv.put(IRON, np.full((64, 32), 3) + (Y < 33), ring)
    cv.put(IRON, np.full((64, 32), 5), (X >= 21) & (X <= 24) & (Y >= 28) & (Y <= 29))
    cv.put(WOOD_D, np.full((64, 32), 0), nb(ring, -1, 1, False) & ~ring & (Y > 33))
    cv.put(IRON, np.full((64, 32), 3), (X >= 26) & (X <= 29) & (Y >= 38) & (Y <= 44))
    cv.col('#050404', (X == 27) & (Y >= 40) & (Y <= 42))
    return cv.out()


@painter('door_porton')
def p_door_porton(v):
    """Main entrance leaf: colonial cuarterones (square raised panels with a pyramid boss), iron studs, knocker."""
    cv = Cv(32, 64)
    X, Y = cv.X, cv.Y
    gv = wood_grain(32, 64, 3700, 'y', warp=2.0)
    gh = wood_grain(32, 64, 3701, 'x', warp=2.0)
    idx = np.where((X < 3) | (X > 28) | ((X >= 15) & (X <= 16)), 4 + gv, 4 + gh)
    idx = np.where((X == 0) | (X == 31) | (Y == 0) | (Y == 63), 1, idx)
    rows = [(3, 15), (18, 30), (33, 45), (48, 60)]
    for (y0, y1) in rows:
        for (x0, x1) in ((3, 14), (17, 28)):
            idx = frame_opening(idx, x0, y0, x1, y1)
            idx, field, ins = raised_panel(idx, x0 + 1, y0 + 1, x1 - 1, y1 - 1, 3, 4 + gv, hi=(2, 1), lo=(-2, -1))
            # pyramid boss in the field
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            d = np.maximum(np.abs(X - cx), np.abs(Y - cy))
            boss = d <= 2.0
            tri_t = boss & ((Y - cy) < -(np.abs(X - cx)) + 0.5)
            tri_b = boss & ((Y - cy) > (np.abs(X - cx)) - 0.5)
            idx = np.where(boss, 4, idx)
            idx = np.where(tri_t, 6, idx)
            idx = np.where(tri_b, 2, idx)
    cv.put(OAK, idx)
    studs(cv, [(x, y) for y in (1, 16, 31, 46, 61) for x in (1, 15, 29) if y < 62])
    # knocker on the upper half
    ring = (np.abs(np.sqrt((X - 22.5) ** 2 + (Y - 26.5) ** 2) - 3.0) < 0.75) & (Y >= 24)
    cv.put(IRON, np.full((64, 32), 4), ring)
    cv.put(IRON, np.full((64, 32), 5), (X >= 21) & (X <= 24) & (Y >= 21) & (Y <= 23))
    cv.tint('#6a6050', np.where((Y > 55) & (fbm(32, 64, 3702, cells=8, octaves=2) > 0.5), 0.3, 0))
    return cv.out()


def iron_sheet(cv, seed, base=3):
    X, Y = cv.X, cv.Y
    n = fbm(32, 64, seed, cells=4, octaves=3)
    idx = base + posterize(n, [(0.66, 1), (0.34, -1)])
    cv.put(IRON, idx)
    # rust: blooms + streaks running down
    rs = rank(fbm(32, 64, seed + 1, cells=8, octaves=2)) > 0.9
    rs |= (Y > 55) & (fbm(32, 64, seed + 2, cells=8, octaves=2) > 0.55)
    rs |= (Y > 60) & (fbm(32, 64, seed + 4, cells=16, octaves=1) > 0.4)
    cv.put(RUST, np.full((64, 32), 2) + posterize(fbm(32, 64, seed + 3, cells=8, octaves=1), [(0.65, 1), (0.3, -1)]), rs)
    # rust streaks running down from a few points
    for (x, y) in poisson(seed + 5, 6, 6, 32, 64):
        L = 3 + (x * 7 + y) % 6
        cv.put(RUST, np.full((64, 32), 1), (X == x) & (Y >= y) & (Y < y + L))


def rivet_row(cv, pts, rust=True):
    X, Y = cv.X, cv.Y
    for (x, y) in pts:
        cv.put(IRON, np.full(X.shape, 6), (X == x) & (Y == y))
        cv.put(IRON, np.full(X.shape, 1), (X == x) & (Y == y + 1))
        if rust and (x * 7 + y * 3) % 3 == 0:
            cv.put(RUST, np.full(X.shape, 2), (X == x) & (Y >= y + 2) & (Y <= y + 4))


@painter('door_cripta')
def p_door_cripta(v):
    """Iron crypt door: riveted plates, angle-iron frame, three straps, heavy lock box, barred spy-hole."""
    cv = Cv(32, 64)
    X, Y = cv.X, cv.Y
    iron_sheet(cv, 3800)
    fr = (X <= 2) | (X >= 29) | (Y <= 2) | (Y >= 61)
    cv.put(IRON, np.full((64, 32), 4) + (X == 0) * -2 + (Y == 0) * 2 + ((X == 2) | (Y == 2)) * -1, fr)
    for yc in (17, 33, 49):
        st = (Y >= yc - 1) & (Y <= yc + 1) & ~fr
        cv.put(IRON, np.full((64, 32), 4) + (Y == yc - 1) * 2 - (Y == yc + 1) * 2, st)
        rivet_row(cv, [(x, yc) for x in range(5, 28, 5)])
    rivet_row(cv, [(1, y) for y in range(4, 62, 6)] + [(30, y) for y in range(4, 62, 6)], rust=False)
    # seam between the two plates
    cv.put(IRON, np.full((64, 32), 1), (X == 16) & ~fr & (np.abs(Y - 17) > 1) & (np.abs(Y - 33) > 1) & (np.abs(Y - 49) > 1))
    # spy-hole with bars (see-through)
    hole = (X >= 10) & (X <= 21) & (Y >= 6) & (Y <= 12)
    cv.a = np.where(hole, 0, cv.a)
    bars = hole & ((X == 12) | (X == 15) | (X == 18) | (X == 21) & False)
    cv.put(IRON, np.full((64, 32), 4) + (Y == 6), bars)
    hr = rim(hole, wrap=False)
    cv.put(IRON, np.full((64, 32), 6), hr['out_below'])
    cv.put(IRON, np.full((64, 32), 0), hr['out_above'])
    # lock box + keyhole
    lb = (X >= 21) & (X <= 28) & (Y >= 37) & (Y <= 45)
    cv.put(IRON, np.full((64, 32), 4) + (Y == 37) * 2 - (Y == 45) * 2, lb)
    cv.col('#030303', (X == 24) & (Y >= 39) & (Y <= 42) | (X == 25) & (Y == 40))
    cv.put(RUST, np.full((64, 32), 4), (X >= 23) & (X <= 26) & (Y >= 46) & (Y <= 50) & ((X + Y) % 2 == 0))
    return cv.out()


@painter('door_silencio')
def p_door_silencio(v):
    """'Cuarto del Silencio': low iron door with a barred slit and a sliding cover, scratched tallies near the floor."""
    cv = Cv(32, 64)
    X, Y = cv.X, cv.Y
    iron_sheet(cv, 3900, base=3)
    fr = (X <= 1) | (X >= 30) | (Y <= 1) | (Y >= 62)
    cv.put(IRON, np.full((64, 32), 4) + (Y == 0) * 2 - (X == 31), fr)
    slit = (X >= 8) & (X <= 23) & (Y >= 19) & (Y <= 21)
    cv.a = np.where(slit, 0, cv.a)
    cv.put(IRON, np.full((64, 32), 5), slit & (X % 3 == 1))
    cover = (X >= 7) & (X <= 24) & (Y >= 15) & (Y <= 17)
    cv.put(IRON, np.full((64, 32), 4) + (Y == 15) * 2 - (Y == 17), cover)
    cv.put(IRON, np.full((64, 32), 6), (X == 16) & (Y == 14))
    sr = rim(slit, wrap=False)
    cv.put(IRON, np.full((64, 32), 6), sr['out_below'])
    # scratched tally marks (bright bare metal)
    for k in range(9):
        x = 6 + k * 2 + (k >= 5)
        if k == 4 or k == 9:
            pts = line_px(4, 54, 13, 49)
        else:
            pts = line_px(x, 48, x, 54)
        cv.put(IRON, np.full((64, 32), 7), path_mask(pts, 32, 64, wrap=False))
    cv.put(IRON, np.full((64, 32), 7), path_mask(line_px(4, 54, 13, 49), 32, 64, wrap=False))
    # hasp and padlock
    cv.put(IRON, np.full((64, 32), 4), (X >= 25) & (X <= 29) & (Y >= 34) & (Y <= 35))
    pad = (X >= 25) & (X <= 28) & (Y >= 37) & (Y <= 41)
    cv.put(BRASS, np.full((64, 32), 3) + (Y == 37), pad)
    cv.put(IRON, np.full((64, 32), 2), ((X == 25) | (X == 28)) & (Y == 36))
    return cv.out()


# =============================================================================================== CLOISTER: arches & columns
ARCH_R = 24.0   # semicircular arch over a 3-block opening, springing from the capitals


def arch_pieces(bx, by):
    """Boxes of one arch block: bx in (0, 1, 2) = left/centre/right of the opening, by in (0, 1) = lower/upper row.
    Each 1-unit column is solid above the intrados; returns list of (x0, x1, y0) in block units."""
    cx = 24.0 - bx * 16          # arch centre relative to this block
    out = []
    for i in range(16):
        dx = i + 0.5 - cx
        d = ARCH_R * ARCH_R - dx * dx
        yc = math.sqrt(d) if d > 0 else 0.0
        y0 = yc - by * 16
        if y0 >= 16:
            continue
        out.append((i, i + 1, max(0.0, y0)))
    # merge equal neighbours
    merged = []
    for (a, b, y) in out:
        if merged and abs(merged[-1][2] - y) < 1e-6 and merged[-1][1] == a:
            merged[-1] = (merged[-1][0], b, y)
        else:
            merged.append((a, b, y))
    return merged, cx, by


def arch_paint(bx, by, wall='revoque'):
    """Plaster of the arch with a painted archivolt band (lime-washed ochre ring, dark arris) on the faces and a
    darker soffit."""
    cx = 24.0 - bx * 16
    cy = -by * 16.0

    def fn(face, w, h, part, cv):
        i, j = aligned_uv(part, face, w, h)
        tex = T(wall, (bx + by) % 4)
        cv.rgb = tex[j, i][..., :3].astype(float)
        cv.a[:] = 255
        x, y, z = face_coords(part, face, w, h)
        r = np.sqrt((x - cx) ** 2 + (y - cy) ** 2)
        if face in ('north', 'south'):
            band = (r >= ARCH_R) & (r < ARCH_R + 3.0)
            cv.tint('#c9b48c', np.where(band, 0.32, 0))
            cv.mul(np.where(band & (r >= ARCH_R + 2.5), 0.78, 1.0))
            cv.mul(np.where((r >= ARCH_R) & (r < ARCH_R + 0.5), 1.08, 1.0))
            # keystone outline at the crown
            ks = (np.abs(x - cx) < 1.6) & (r >= ARCH_R) & (r < ARCH_R + 3.6)
            cv.tint('#d8c7a0', np.where(ks, 0.35, 0))
        if face == 'down':
            cv.mul(0.9)
            cv.tint('#6e6250', 0.08)
    return pp_fn(fn)


def arch_block(bx, by):
    pieces, cx, _ = arch_pieces(bx, by)
    pt = arch_paint(bx, by)
    return [P((a, y0, 0), (b, 16, 16), pt, name='arch') for (a, b, y0) in pieces]


def octo(x0, x1, y0, y1, painter, cx=8.0, cz=8.0):
    """Octagonal prism from an axis-aligned box and the same box turned 45 degrees."""
    hw = (x1 - x0) / 2
    s2 = hw / math.sqrt(2) * 2 * 0.83
    return [P((cx - hw, y0, cz - hw), (cx + hw, y1, cz + hw), painter),
            P((cx - hw * 0.83, y0, cz - hw * 0.83), (cx + hw * 0.83, y1, cz + hw * 0.83), painter,
              rot=('y', 45, (cx, (y0 + y1) / 2, cz)))]


def column_parts(piece):
    pl = pp_plaster('revoque', 0)
    plw = pp_plaster('revoque_descascarado', 3)
    if piece == 'base':
        return [P((1.5, 0, 1.5), (14.5, 3, 14.5), pl, name='plinth'),
                P((2.5, 3, 2.5), (13.5, 4, 13.5), pl, name='torus')] + octo(3.4, 12.6, 4, 5.2, pl) + octo(4.4, 11.6, 5.2, 16, plw)
    if piece == 'fuste':
        return octo(4.4, 11.6, 0, 16, pl)
    # capital
    return octo(4.4, 11.6, 0, 9, pl) + octo(3.8, 12.2, 9, 10.2, pl) + octo(3.0, 13.0, 10.2, 12.5, pl) + [
        P((1.0, 12.5, 1.0), (15.0, 16, 15.0), pl, name='abacus')]


# =============================================================================================== STAIRS & BALUSTRADES
@painter('madera_oscura')
def p_madera_oscura(v):
    """Polished dark tread boards (hall staircase, choir loft floor): 4 boards, wax wear in the middle."""
    cv, idx, lab = boards(v, seed=300, joints=[[11], [27], [3], [19]])
    X, Y = cv.X, cv.Y
    cv.put(WOOD_D, idx + 1)
    wear = (np.abs(Y - 16) < 9) & (fbm(N, N, 2600 + v, cells=2, octaves=2) > 0.45) & (Y % 8 != 0)
    cv.put(WOOD_D, idx + 2, wear)
    return cv.out()


@painter('piedra_escalon')
def p_piedra_escalon(v):
    """Worn grey-ochre limestone (steps, landings): big slabs, the middle polished by 90 years of feet."""
    cv = Cv()
    X, Y = cv.X, cv.Y
    lab = np.where(Y < 16, 0, 1) if v % 2 == 0 else np.where(X < 20, 0, 1)
    joint = (Y == 0) | ((Y == 16) if v % 2 == 0 else (X == 20)) | (X == 0)
    lab = np.where(joint, -1, lab)
    n = fbm(N, N, 2700 + v, cells=4, octaves=3)
    idx = np.full((N, N), 4) + posterize(n, [(0.68, 1), (0.30, -1)])
    idx = relief(idx, 2710, 2711 + v, count=14, mind=5, body=-1, light=1)
    idx = bevel(idx, lab, hi=1, lo=-1)
    worn = (np.abs(X - 16) < 10) & (np.abs(Y - 16) < 12) & (fbm(N, N, 2720 + v, cells=2, octaves=2) > 0.42)
    idx = np.where(worn & (lab >= 0), idx + 1, idx)
    cv.put(STONE, idx)
    cv.put(GROUT, np.full((N, N), 2), joint)
    # fossil shell / dark inclusion specks typical of Córdoba limestone
    for (x, y) in poisson(2730 + v, 4, 8, keep=lambda x, y: lab[int(y), int(x)] >= 0):
        cv.put(STONE, np.full((N, N), 1), (X == x) & (Y == y) | (X == x + 1) & (Y == y))
        cv.put(STONE, np.full((N, N), 6), (X == x) & (Y == y - 1))
    return cv.out()


def baluster(x, z, y0, y1, pt, w=1.0):
    """Turned baluster between y0 and y1 (square base, bulb, neck, top block)."""
    H = y1 - y0
    k = H / 12.5
    c = (x, z)
    def bx(r, a, b):
        return P((c[0] - r, y0 + a * k, c[1] - r), (c[0] + r, y0 + b * k, c[1] + r), pt)
    return [bx(1.1 * w, 0, 2.0), bx(1.5 * w, 2.0, 6.0), bx(1.15 * w, 6.0, 7.0), bx(0.7 * w, 7.0, 10.5), bx(1.1 * w, 10.5, 12.5)]


def baranda_parts():
    wood = pp_wood(WOOD_D, 4, seed=51)
    rail = pp_wood(WOOD_D, 5, seed=52)
    parts = [P((0, 0, 6.2), (16, 1.5, 9.8), wood, name='shoe'),
             P((0, 13.5, 5.6), (16, 15.0, 10.4), rail, name='rail'),
             P((0, 15.0, 6.4), (16, 15.8, 9.6), rail, name='rail_top')]
    for x in (2, 6, 10, 14):
        parts += baluster(x, 8, 1.5, 13.5, wood)
    return parts


def baranda_poste_parts():
    wood = pp_wood(WOOD_D, 4, seed=53)
    cap = pp_wood(WOOD_D, 5, seed=54)
    return [P((5, 0, 5), (11, 13, 11), wood, name='post'),
            P((4.4, 2, 4.4), (11.6, 3, 11.6), cap, name='ring'),
            P((4.2, 13, 4.2), (11.8, 15, 11.8), cap, name='cap'),
            P((5.6, 15, 5.6), (10.4, 16, 10.4), wood, name='neck'),
            P((6.0, 16, 6.0), (10.0, 18.8, 10.0), cap, name='ball'),
            P((6.6, 18.8, 6.6), (9.4, 19.6, 9.4), cap, name='ball_top')]


def baranda_escalera_parts(side='izq'):
    """Raking balustrade for a straight stair that rises towards the north (front). It is placed in the block ABOVE
    the stair; the balusters reach down onto the treads. side izq = on the west edge, der = east edge."""
    wood = pp_wood(WOOD_D, 4, seed=55)
    rail = pp_wood(WOOD_D, 5, seed=56, along='y')
    x = 2.0 if side == 'izq' else 14.0
    parts = []
    for z in (3.0, 7.0, 11.0, 15.0):
        tread = 0.0 if z < 8 else -8.0
        top = 22 - z
        parts += baluster(x, z, tread, top - 1.0, wood, w=0.8)
    # handrail: a box along z rotated 45 degrees about x (rises to the north)
    L = 16 * math.sqrt(2) + 2
    cz, cy = 8.0, 14.0 + 0.0
    parts.append(P((x - 1.8, cy - 0.9, cz - L / 2), (x + 1.8, cy + 0.9, cz + L / 2), rail, rot=('x', 45, (x, cy, cz)), name='rail'))
    return parts


# =============================================================================================== ROOF
TEJA = Ramp('#3a1710', '#542015', '#6e2b1a', '#86361f', '#9c4326', '#ae522f', '#bd623b', '#c97549', '#d48a5d')
LICHEN = Ramp('#56562f', '#6f6d3b', '#8a8649', '#a7a05c', '#c0b36a')
LICHEN_O = Ramp('#7a4a1c', '#a0662a', '#c58a3d')


@painter('tejas')
def p_tejas(v):
    """Spanish barrel tiles (tejas coloniales), 4 courses across, 2 rows per block: convex covers (cobijas) over
    concave channels (canales), rounded lips with shadow, colour variation per tile, lichen and moss."""
    cv = Cv()
    X, Y = cv.X, cv.Y
    rng = np.random.default_rng(2800 + v)
    col = X // 8
    lx = X % 8
    row = Y // 16
    ly = Y % 16
    lab = col * 2 + row
    tone = rng.choice([-2, -1, 0, 0, 0, 1, 1], 8)
    # channel (canal) between covers: x 6..7 of each course, deep and dark; cover (cobija) x 0..5 convex
    cover = lx <= 5
    prof = np.array([-1, 1, 2, 2, 1, -1, 0, 0])   # convex shading across a cover (lit crest)
    idx = 4 + tone[lab] + np.where(cover, prof[lx], -2)
    idx = np.where(~cover & (lx == 6), idx - 1, idx)
    # tile lips: each cover's lower end (ly 13..15) overlaps the next: bright rim then hard shadow underneath
    idx = np.where(cover & (ly == 13), idx + 1, idx)
    idx = np.where(cover & (ly == 14), idx + 2, idx)
    idx = np.where(cover & (ly == 15), 0, idx)
    idx = np.where(cover & (ly == 0), idx - 1, idx)
    # firing variation: darker burnt patches, clay grain
    n = fbm(N, N, 2810 + v, cells=4, octaves=3)
    idx += np.where(n > 0.72, 1, 0) - np.where(n < 0.25, 1, 0)
    cv.put(TEJA, idx)
    # dirt and moss gathered in the channels
    mo = ~cover & (fbm(N, N, 2820 + v, cells=8, octaves=2) > 0.5)
    cv.put(Ramp('#22261a', '#2f3522', '#3e472b'), np.full((N, N), 1) + (lx == 7), mo)
    # lichen rosettes on the covers (yellow-green and orange)
    for k, (x, y) in enumerate(poisson(2830 + v, 2 + v % 2, 9, keep=lambda x, y: (int(x) % 8) <= 5 and (int(y) % 16) < 12)):
        d = (X - x) ** 2 + (Y - y) ** 2
        lm = (d <= 2 + (k % 2) * 2) & cover & (fbm(N, N, 2840 + k, cells=8, octaves=1) > 0.45)
        rr = LICHEN if k % 3 else LICHEN_O
        cv.put(rr, np.full((N, N), 1) + (d <= 1), lm)
    cv.tint('#6a6040', np.where(cover & (fbm(N, N, 2845 + v, cells=4, octaves=2) > 0.7), 0.25, 0))  # weathered bloom
    if v == 2:   # a cracked cover tile
        pts = wander([(10, 2), (12, 7), (11, 12)], 2850, amp=1)
        cm = path_mask(pts) & cover
        cv.put(TEJA, np.full((N, N), 0), cm)
    if v == 3:   # a missing cover: the mud bed and the channel tiles show
        hole = (col == 2) & (row == 0) & cover & (ly < 13)
        cv.put(ADOBE, np.full((N, N), 2) + posterize(fbm(N, N, 2860, cells=8, octaves=1), [(0.6, 1)]), hole)
        cv.put(ADOBE, np.full((N, N), 0), hole & (ly == 0))
    return cv.out()


def alero_parts():
    """Eave: tile overhang with the round tile ends and carved rafter tails (canecillos) underneath.
    Placed against the wall top (wall behind = south/back side), overhanging towards the front."""
    tile = pp_fn(alero_tile_paint)
    wood = pp_wood(WOOD_D, 4, seed=61, along='y')
    parts = [P((0, 11, 0), (16, 14, 16), tile, name='tiles')]
    for x in (1.5, 7.0, 12.5):
        parts += [P((x, 8.2, 1.0), (x + 2.2, 11, 16), wood, name='rafter'),
                  P((x, 7.0, 1.0), (x + 2.2, 8.2, 3.6), wood, name='rafter_tip')]
    parts.append(P((0, 10, 13), (16, 11, 16), pp_wood(WOOD_D, 3, seed=62), name='wallplate'))
    return parts


def alero_tile_paint(face, w, h, part, cv):
    tex = T('tejas', 0)
    if face in ('up', 'down'):
        i, j = aligned_uv(part, face, w, h)
        cv.rgb = tex[j, i][..., :3].astype(float)
        cv.a[:] = 255
        if face == 'down':  # underside: the mud bed and the cane lath under the tiles
            cv.put(ADOBE, np.full((h, w), 2) + ((np.arange(w)[None, :] % 3) == 0), np.ones((h, w), bool))
        return
    # front/side faces: tile ends (half-round covers above, channel arcs below)
    Y, X = np.mgrid[0:h, 0:w]
    lx = X % 8
    idx = np.full((h, w), 3)
    dome = ((lx - 2.5) ** 2 / 9.0 + (Y - h + 0.5) ** 2 / ((h - 0.5) ** 2) <= 1.0) & (lx <= 5)
    idx = np.where(dome, 5 + (Y < h // 2) - (lx == 0) - (lx == 5), 1)
    idx = np.where(dome & (Y == 0), 7, idx)
    cv.put(TEJA, idx)
    cv.col('#140906', ~dome & (Y >= h // 2))


# =============================================================================================== STAINED GLASS
GL = {   # stained glass colour ramps (dark -> light)
    'blue': Ramp('#0c1640', '#132260', '#1c3285', '#2a46a6', '#3c5fc2', '#5a7fd6'),
    'blue2': Ramp('#10204a', '#183068', '#22438a', '#3159a8', '#4672c0'),
    'red': Ramp('#3e0a10', '#5e0f16', '#83171c', '#a52423', '#c23a2e', '#d65a44'),
    'gold': Ramp('#5a3a06', '#86590c', '#b07c14', '#d09f22', '#e7c046', '#f3dc7e'),
    'green': Ramp('#0f2a16', '#17401f', '#215a2a', '#2f7536', '#468f47'),
    'white': Ramp('#8d9488', '#a8ae9f', '#c0c4b2', '#d6d7c3', '#e8e6d2'),
    'flesh': Ramp('#8a5c40', '#a8765a', '#c49376', '#d9ae90', '#e8c6a8'),
    'purple': Ramp('#24102e', '#371845', '#4c235e', '#633279'),
    'brown': Ramp('#2a170c', '#3e2312', '#55321b'),
    'pale': Ramp('#7f8f86', '#98a69c', '#b2bdb2', '#c8d0c4', '#dbe0d3'),
}
LEAD = np.array(C('#141216'))
STONE_T = np.array(C('#8a8276'))


def glass_compose(labels, colors, paint=None, seed=0, bars=(), alpha=205):
    """labels: int map; colors: {label: ramp name}; paint: list of (mask, rgb, alpha) drawn on top (grisaille).
    Returns float rgba (h, w, 4). Leads = 1 px between different labels. Each connected piece gets its own tone."""
    h, w = labels.shape
    out = np.zeros((h, w, 4))
    streak = fbm(w, h, seed, cells=2, octaves=3, ax=2.5, ay=0.5)
    piece_t = fbm(w, h, seed + 1, cells=3, octaves=1)
    for lab, name in colors.items():
        m = labels == lab
        if not m.any():
            continue
        if name == 'stone':
            out[m, :3] = STONE_T
            out[m, 3] = 255
            continue
        ramp = GL[name]
        base = ramp.n // 2
        idx = base + posterize(streak, [(0.66, 1), (0.34, -1)]) + np.where(piece_t > 0.6, 1, 0) - np.where(piece_t < 0.3, 1, 0)
        out[m, :3] = ramp[idx][m]
        out[m, 3] = alpha if name not in ('white', 'pale') else alpha - 25
    Y, X = np.mgrid[0:h, 0:w]
    lead = (nb(labels, 1, 0, False, -1) != labels) | (nb(labels, 0, 1, False, -1) != labels)
    lead &= (X > 0) & (Y > 0)
    lead &= ~((labels < 0) & (nb(labels, 1, 0, False, -1) < 0) & (nb(labels, 0, 1, False, -1) < 0))
    out[lead, :3] = LEAD
    out[lead, 3] = 255
    for yb in bars:
        out[Y == yb, :3] = C('#0a0a0c')
        out[Y == yb, 3] = 255
    if paint:
        for (m, rgb, a) in paint:
            out[m, :3] = C(rgb)
            out[m, 3] = np.maximum(out[m, 3], a)
    out[labels < 0] = 0
    return out


def lancet_head_mask(w, h, top_off=0):
    """Pointed (equilateral) arch head of a 24 px wide lancet: True inside the opening. Rows of the sup piece."""
    Y, X = np.mgrid[0:h, 0:w]
    xu = 2 + (X + 0.5) / 2.0          # block units across the opening (2..14)
    yu = 16 - (Y + 0.5) / 2.0
    ys = 4.0
    inside = yu <= ys
    left = ((xu - 14) ** 2 + (yu - ys) ** 2 <= 144) & (xu <= 8)
    right = ((xu - 2) ** 2 + (yu - ys) ** 2 <= 144) & (xu > 8)
    return inside | left | right


def vitral_ines():
    """Santa Inés with the lamb and the palm, under a gold canopy; blue diaper ground; red/gold border."""
    W, H = 24, 96
    Y, X = np.mgrid[0:H, 0:W]
    lab = np.full((H, W), 1)           # 1 = blue ground
    opening = np.ones((H, W), bool)
    opening[0:32] = lancet_head_mask(W, 32)
    # border: 2 px, alternating red / gold every 3 px
    edge = (X < 2) | (X >= W - 2)
    head_edge = ~lancet_head_mask(W, 32) if False else None
    om = opening.copy()
    inner = om & nb(om, 2, 0, False) & nb(om, -2, 0, False) & nb(om, 0, 2, False) & nb(om, 0, -2, False)
    border = om & ~inner
    lab = np.where(border, np.where(((X + Y) // 3) % 2 == 0, 2, 3), lab)
    # canopy (gold architecture) rows 8..20 in the head
    can = inner & (Y >= 9) & (Y <= 15) & (np.abs(X - 11.5) <= 7)
    can |= inner & (Y >= 4) & (Y < 9) & (np.abs(X - 11.5) <= (Y - 3) * 0.9)
    lab = np.where(can, 4, lab)
    lab = np.where(can & (Y == 15), 5, lab)
    # halo + head + hair
    halo = ((X - 11.5) ** 2 + (Y - 24) ** 2 <= 22) & inner
    lab = np.where(halo, 4, lab)
    head = ((X - 11.5) ** 2 / 6.0 + (Y - 25) ** 2 / 9.0 <= 1)
    hair = ((X - 11.5) ** 2 / 10.0 + (Y - 25.5) ** 2 / 12.0 <= 1) | ((np.abs(X - 11.5) <= 4) & (Y >= 25) & (Y <= 33))
    lab = np.where(hair, 8, lab)
    lab = np.where(head, 6, lab)
    # body: red dress (central), green mantle on both sides falling to the feet
    yb0, yb1 = 31, 80
    t = np.clip((Y - yb0) / (yb1 - yb0), 0, 1)
    halfw = 3.2 + t * 4.2
    body = (np.abs(X - 11.5) <= halfw) & (Y >= yb0) & (Y <= yb1)
    dress = body & (np.abs(X - 11.5) <= 1.6 + t * 2.0)
    lab = np.where(body, 7, lab)
    lab = np.where(dress, 9, lab)
    # hands holding the palm (diagonal green frond from the right hand up to the left shoulder)
    hand = ((X - 15.0) ** 2 + (Y - 46) ** 2 <= 2.2)
    lab = np.where(hand, 6, lab)
    palm = (np.abs((X - 15) + (Y - 46) * 0.42) <= 0.8) & (Y >= 33) & (Y <= 46)
    palm |= ((np.abs((X - 15) + (Y - 46) * 0.42) <= 2.4) & (Y >= 33) & (Y <= 40) & ((Y % 2) == 0))
    lab = np.where(palm & inner, 10, lab)
    # lamb in her left arm / at her feet (inf piece)
    lamb = ((X - 7.5) ** 2 / 14.0 + (Y - 70) ** 2 / 9.0 <= 1)
    lamb_head = ((X - 3.5) ** 2 + (Y - 67) ** 2 <= 3.2)
    lab = np.where(lamb, 11, lab)
    lab = np.where(lamb_head & inner, 12, lab)
    legs = ((X == 6) | (X == 9)) & (Y >= 72) & (Y <= 75)
    lab = np.where(legs, 12, lab)
    # ground + inscription
    ground = inner & (Y >= 80) & (Y <= 83)
    lab = np.where(ground, 10, lab)
    plaque = inner & (Y >= 84) & (Y <= 92)
    lab = np.where(plaque, 13, lab)
    lab = np.where(~opening, -1, lab)
    colors = {1: 'blue', 2: 'red', 3: 'gold', 4: 'gold', 5: 'white', 6: 'flesh', 7: 'green', 8: 'brown', 9: 'red',
              10: 'green', 11: 'white', 12: 'brown', 13: 'purple'}
    # grisaille paint: diaper lattice on the ground, face, drapery folds, letters, lamb fleece
    paint = []
    diaper = (lab == 1) & (((X + Y) % 6 == 0) | ((X - Y) % 6 == 0))
    paint.append((diaper, '#0b1336', 230))
    paint.append(((Y == 24) & ((X == 10) | (X == 13)), '#3a2014', 255))
    paint.append(((Y == 27) & (X >= 11) & (X <= 12), '#7a4632', 255))
    folds = ((lab == 7) | (lab == 9)) & ((X + (Y // 7)) % 4 == 0) & (Y > 36)
    paint.append((folds, '#1a0a0a', 235))
    fleece = (lab == 11) & (((X * 3 + Y * 5) % 7) == 0)
    paint.append((fleece, '#8d9488', 230))
    tm = np.zeros((H, W), bool)
    stamp(tm, tiny_mask('S.INÉS'), 2, 85)
    paint.append((tm & (lab == 13), '#e7c046', 255))
    return glass_compose(lab, colors, paint, seed=4000, bars=(48, 64))


def vitral_geo():
    """Repeating window: pale grisaille quarries with a red/blue border and a medallion with a gold cross."""
    W, H = 24, 96
    Y, X = np.mgrid[0:H, 0:W]
    opening = np.ones((H, W), bool)
    opening[0:32] = lancet_head_mask(W, 32)
    om = opening
    inner = om & nb(om, 2, 0, False) & nb(om, -2, 0, False) & nb(om, 0, 2, False) & nb(om, 0, -2, False)
    border = om & ~inner
    # quarries: diamond lattice, each diamond its own label so leads appear
    q = ((X + Y) // 6) * 100 + ((X - Y + 96) // 6)
    lab = np.where(inner, 1000 + q, -1)
    lab = np.where(border, np.where((Y // 4) % 2 == 0, 2, 3), lab)
    # medallion (circle) in the med piece, quatrefoil in the head, small roundel in the inf
    def roundel(cx, cy, r, ring_lab, fill_lab, cross_lab=None):
        nonlocal lab
        d = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2)
        lab = np.where(inner & (d <= r), ring_lab, lab)
        lab = np.where(inner & (d <= r - 2), fill_lab, lab)
        if cross_lab is not None:
            cr = inner & (d <= r - 3) & ((np.abs(X - cx) <= 1) | (np.abs(Y - cy) <= 1))
            lab = np.where(cr, cross_lab, lab)
    roundel(11.5, 47.5, 8.5, 4, 5, 6)
    roundel(11.5, 18, 5.5, 4, 7)
    roundel(11.5, 76, 5.5, 4, 7)
    colors = {2: 'red', 3: 'blue2', 4: 'gold', 5: 'blue', 6: 'gold', 7: 'red'}
    for v in np.unique(lab):
        if v >= 1000:
            colors[int(v)] = 'pale'
    paint = []
    # grisaille vine on the quarries: small painted dots/strokes
    vine = (lab >= 1000) & (((X * 2 + Y * 3) % 11) == 0)
    paint.append((vine, '#4f5a52', 220))
    return glass_compose(lab, colors, paint, seed=4100, bars=(48, 64))


_VIT = {}


def vit_img(name):
    if name not in _VIT:
        _VIT[name] = {'ines': vitral_ines, 'geo': vitral_geo}[name]()
    return _VIT[name]


def vitral_glass(name, piece):
    off = {'sup': 0, 'med': 32, 'inf': 64}[piece]

    def p(face, w, h, part):
        x, y, z = face_coords(part, face, w, h)
        img = vit_img(name)
        col = np.clip(np.floor((14 - x) * 2).astype(int), 0, 23)
        row = np.clip(off + np.floor((16 - y) * 2).astype(int), 0, 95)
        if face == 'south':
            col = 23 - col   # seen from outside the design is mirrored, as in real glass
        a = img[row, col]
        return np.clip(a, 0, 255).round().astype(np.uint8)
    return p


def vitral_parts(name, piece):
    pl = pp_plaster('sillar')
    parts = [P((0, 0, 0), (2, 16, 16), pl, name='jamb_l'), P((14, 0, 0), (16, 16, 16), pl, name='jamb_r')]
    if piece == 'inf':
        parts.append(P((1, 0, 0), (15, 1.5, 16), pl, name='sill'))
    if piece == 'sup':
        for xi in range(2, 14):
            xm = xi + 0.5
            ys = 4.0
            ya = ys + (math.sqrt(max(0, 144 - (xm - 14) ** 2)) if xm <= 8 else math.sqrt(max(0, 144 - (xm - 2) ** 2)))
            if ya < 16:
                parts.append(P((xi, ya, 0), (xi + 1, 16, 16), pl, name='head_fill'))
    it = pp_iron(seed=71, rust=0.15)
    for yb in ((8.0,) if piece != 'sup' else ()):
        parts.append(P((2, yb - 0.5, 7.4), (14, yb + 0.5, 8.6), it, name='saddle'))
    parts.append(PL((2, 0 if piece != 'inf' else 1.5, 8.0), (14, 16, 8.0), vitral_glass(name, piece), name='glass'))
    return parts


def roseton():
    """Rose window composition, 64 x 64 px over 2 x 2 blocks: 8 petals, oculus with IHS, stone tracery."""
    W = 64
    Y, X = np.mgrid[0:W, 0:W]
    cx = cy = 31.5
    d = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2)
    ang = (np.degrees(np.arctan2(Y - cy, X - cx)) + 360) % 360
    lab = np.full((W, W), -1)
    R = 29.0
    lab = np.where(d <= R, 1, lab)                          # blue ground
    sector = (ang // 45).astype(int)
    # petals: circles of radius 8 centred at r=18 on each 45 deg axis
    for k in range(8):
        a = math.radians(k * 45 + 22.5)
        px, py = cx + math.cos(a) * 18.5, cy + math.sin(a) * 18.5
        pd = np.sqrt((X - px) ** 2 + (Y - py) ** 2)
        lab = np.where(pd <= 7.5, 10 + k, lab)
        lab = np.where(pd <= 4.0, 20 + k, lab)
    # oculus
    lab = np.where(d <= 9.5, 30, lab)
    lab = np.where(d <= 7.0, 31, lab)
    # stone tracery: outer ring, ring around the oculus, spokes between petals
    stone = (d > R) & (d <= R + 2.5)
    stone |= (np.abs(d - 10.5) < 1.2)
    for k in range(8):
        a = k * 45.0
        diff = np.abs(((ang - a) + 180) % 360 - 180)
        stone |= (diff * np.pi / 180 * d < 1.3) & (d > 10.5) & (d < R)
    lab = np.where(stone, 99, lab)
    lab = np.where(d > R + 2.5, -2, lab)
    colors = {1: 'blue', 30: 'gold', 31: 'red', 99: 'stone'}
    for k in range(8):
        colors[10 + k] = 'red' if k % 2 == 0 else 'gold'
        colors[20 + k] = 'blue2' if k % 2 == 0 else 'green'
    tm = np.zeros((W, W), bool)
    stamp(tm, tiny_mask('IHS'), 27, 28)
    paint = [(tm & (lab == 31), '#f3dc7e', 255),
             ((lab == 1) & (((X + Y) % 5 == 0)), '#0b1336', 220)]
    img = glass_compose(lab, colors, paint, seed=4200)
    img[lab == -2] = 0
    # stone tracery shading
    st = lab == 99
    img[st & (nb(st, 1, 0, False) == False), :3] = C('#b4ab9c')
    img[st & (nb(st, -1, 0, False) == False), :3] = C('#5f594f')
    return img


def roseton_glass(gx, gy):
    """gx: 0 = left piece (as seen from the front), gy: 0 = top piece."""
    def p(face, w, h, part):
        x, y, z = face_coords(part, face, w, h)
        img = vit_img('rose') if 'rose' in _VIT else _VIT.setdefault('rose', roseton())
        col = np.clip(gx * 32 + np.floor((16 - x) * 2).astype(int), 0, 63)
        row = np.clip(gy * 32 + np.floor((16 - y) * 2).astype(int), 0, 63)
        if face == 'south':
            col = 63 - col
        return np.clip(img[row, col], 0, 255).round().astype(np.uint8)
    return p


def roseton_parts(gx, gy):
    pl = pp_plaster('sillar')
    parts = []
    # stone fill outside the circle (stepped 1-unit columns), circle centre at the shared corner of the 4 pieces
    ccx = 0.0 if gx == 0 else 16.0      # centre x in this block's units (left piece: centre on its x=0 side)
    ccy = 0.0 if gy == 0 else 16.0      # top piece: centre at its bottom
    Rr = 15.25
    for xi in range(16):
        xm = xi + 0.5
        dx = xm - ccx
        if abs(dx) >= Rr:
            parts.append(P((xi, 0, 0), (xi + 1, 16, 16), pl, name='fill'))
            continue
        dy = math.sqrt(Rr * Rr - dx * dx)
        if gy == 0:      # circle occupies y < dy (from the bottom of the top piece)
            if dy < 16:
                parts.append(P((xi, dy, 0), (xi + 1, 16, 16), pl, name='fill'))
        else:            # bottom piece: circle occupies y > 16 - dy
            if dy < 16:
                parts.append(P((xi, 0, 0), (xi + 1, 16 - dy, 16), pl, name='fill'))
    parts.append(PL((0, 0, 8.0), (16, 16, 8.0), roseton_glass(gx, gy), name='glass'))
    return parts


# =============================================================================================== CRYPT NICHES, HOLE, PLATES
MARBLE = Ramp('#6e6a64', '#8e8a83', '#aaa69e', '#c0bcb3', '#d2cec5', '#e0ddd5', '#ebe9e2')


def plaque_paint(lines, base_ramp=MARBLE, ink='#2a2724', broken=False, seed=0):
    def fn(face, w, h, part, cv):
        X, Y = cv.X, cv.Y
        if face not in ('north',):
            cv.put(base_ramp, np.full((h, w), 2))
            return
        f = fbm(w, h, 4300 + seed, cells=max(1, w // 8), octaves=3)
        idx = np.full((h, w), 4) + posterize(f, [(0.7, 1), (0.3, -1)])
        vein = path_mask(wander([(0, h * 0.3), (w * 0.5, h * 0.6), (w - 1, h * 0.4)], 4310 + seed, amp=3), w, h, wrap=False)
        idx = np.where(vein, idx - 2, idx)
        bd = border_px(w, h)[0]
        idx = np.where(bd == 0, 2, np.where(bd == 1, idx + 1, idx))
        cv.put(base_ramp, idx)
        y = 3
        for ln in lines:
            tm = tiny_mask(ln)
            th, tw = tm.shape
            m = np.zeros((h, w), bool)
            stamp(m, tm, (w - tw) // 2, y)
            cv.col(ink, m)
            cv.put(base_ramp, np.full((h, w), 6), nb(m, -1, 0, False) & ~m)
            y += th + 2
        if broken:
            pts = wander([(w * 0.62, 0), (w * 0.55, h * 0.5), (w * 0.7, h - 1)], 4320 + seed, amp=2)
            cm = path_mask(pts, w, h, wrap=False)
            cv.col('#141210', cm)
        # grime from the damp crypt
        cv.tint('#3b3a2c', np.where((Y > h * 0.7) & (fbm(w, h, 4330 + seed, cells=4, octaves=2) > 0.5), 0.3, 0))
    return pp_fn(fn)


def nicho_parts(lines=None, open_=False, seed=0, broken=False):
    """A niche set in the crypt wall (the block replaces a wall block). Named plaque spans 2 blocks (x -8..24) so the
    names fit; for the open niche the plaque hangs below the opening."""
    st = pp_plaster('cripta_piedra')
    frame = pp_plaster('sillar', 2)
    parts = [P((1, 13.5, -1.0), (15, 15.5, 1.0), frame, name='lintel'),
             P((1, 0.5, -1.4), (15, 2.0, 1.0), frame, name='sill'),
             P((1, 2.0, -1.0), (2.5, 13.5, 1.0), frame, name='jl'),
             P((13.5, 2.0, -1.0), (15, 13.5, 1.0), frame, name='jr'),
             P((0, 15.5, 0), (16, 16, 16), st), P((0, 0, 0), (16, 0.5, 16), st),
             P((0, 0.5, 0), (1, 15.5, 16), st), P((15, 0.5, 0), (16, 15.5, 16), st)]
    if open_:
        dark = pp_fn(lambda face, w, h, part, cv: cv.put(CRIPTA, np.full((h, w), 1) + (border_px(w, h)[0] == 0) * -1))
        parts += [P((2.5, 2.0, 14), (13.5, 13.5, 16), dark, name='back'),
                  P((2.5, 2.0, 1.0), (13.5, 2.2, 14), dark, name='floor')]
        if lines:
            parts.append(P((-8, -7.5, -0.6), (24, 0.2, 0), plaque_paint(lines, seed=seed), name='plaque'))
    else:
        parts.append(P((2.5, 2.0, -0.2), (13.5, 13.5, 1.0), pp_plaster('cripta_piedra', 1), name='seal'))
        if lines:
            parts.append(P((-8, 2.5, -0.9), (24, 13.0, -0.3), plaque_paint(lines, seed=seed, broken=broken), name='plaque'))
    return parts


def ladrillo_hueco_parts():
    """The 1984 wall with bricks knocked out: a real hole you can see (and shine a torch) through."""
    tex = pp_plaster('muro_ladrillo')
    inner = pp_fn(lambda face, w, h, part, cv: cv.put(CEMENTO, np.full((h, w), 2) + ((np.arange(w)[None, :] + np.arange(h)[:, None]) % 3 == 0)))
    courses = [(0, 4, None), (4, 8, (6, 12)), (8, 12, (4, 13)), (12, 16, (7, 11))]
    parts = []
    for (y0, y1, hole) in courses:
        if hole is None:
            parts.append(P((0, y0, 0), (16, y1, 16), tex))
        else:
            parts.append(P((0, y0, 0), (hole[0], y1, 16), tex))
            parts.append(P((hole[1], y0, 0), (16, y1, 16), tex))
    return parts


def wall_plate_parts(text_lines, w_units=10, h_units=7, big=False, ramp=ENAMEL, ink='#1f2b4c', y0=6):
    """Enamel plate screwed to the wall behind (z=16)."""
    def fn(face, w, h, part, cv):
        X, Y = cv.X, cv.Y
        idx = np.full((h, w), 4)
        bd = border_px(w, h)[0]
        idx = np.where(bd == 0, 1, np.where(bd == 1, 3, idx))
        idx = np.where((bd == 2) & (Y < h // 2), 5, idx)
        cv.put(ramp, idx)
        if face == 'north':
            yy = 3
            for ln, f in text_lines:
                tm = text_mask(ln)[2:, :] if f == 'big' else tiny_mask(ln)
                th, tw = tm.shape
                m = np.zeros((h, w), bool)
                stamp(m, tm, (w - tw) // 2, yy)
                cv.col(ink, m)
                yy += th + 2
            cv.put(BRASS, np.full((h, w), 5), ((X == 1) | (X == w - 2)) & ((Y == 1) | (Y == h - 2)))
            chip = (X >= w - 4) & (Y >= h - 3) & (bd <= 1)
            cv.put(IRON, np.full((h, w), 2), chip)
    x0 = 8 - w_units / 2
    return [P((x0, y0, 15.4), (x0 + w_units, y0 + h_units, 16), pp_fn(fn), name='plate')]


def tablones_parts():
    """Boards nailed across a door (Sor María's cell). Placed in front of the door, lower block; reaches up the
    whole doorway."""
    parts = []
    specs = [(3, 2.4, 0), (11, 2.6, 22.5), (19, 2.4, -22.5), (26, 2.6, 0)]
    for k, (y, hh, ang) in enumerate(specs):
        pt = pp_paint(WEATHER, 4, seed=81 + k, chip=0.0, along='x', out=-1)
        if ang:
            parts.append(P((-1, y, 14.4), (17, y + hh, 15.6), pt, rot=('z', ang, (8, y + hh / 2, 15)), name='board'))
        else:
            parts.append(P((-1, y, 14.4), (17, y + hh, 15.6), pt, name='board'))
    nail = pp_iron(base=5, seed=89, rust=0.4)
    for (x, y) in ((0.5, 4), (15, 4), (0.5, 27.2), (15, 27.2)):
        parts.append(P((x, y, 14.0), (x + 0.6, y + 0.6, 14.4), nail, name='nail'))
    return parts


# =============================================================================================== BLOCKS
def cube(key, es, en, painter_name, variants=1, sound='plaster', up=None, down=None, **kw):
    mats = {}

    def m(name):
        if name not in mats:
            mats[name] = cube_mat(PAINTERS[name])
        return mats[name]
    up = up or painter_name
    down = down or up
    faces = {'side': m(painter_name), 'up': m(up), 'down': m(down)}
    return Cube('colegio_' + key, es, en, faces=faces, kit=KIT, sound=sound, variants=variants, **kw)


# walls
REVOQUE = cube('revoque', 'Revoque a la cal', 'Lime plaster wall', 'revoque', 4)
cube('revoque_descascarado', 'Revoque descascarado', 'Peeling plaster wall', 'revoque_descascarado', 4, up='revoque', down='revoque')
cube('revoque_humedad', 'Revoque con humedad', 'Water-stained plaster', 'revoque_humedad', 3, up='revoque', down='revoque')
cube('revoque_salitre', 'Revoque con salitre', 'Plaster with rising damp', 'revoque_salitre', 3, up='revoque', down='revoque')
cube('revoque_marcas', 'Revoque con marcas', 'Plaster with old marks', 'revoque_marcas', 4, up='revoque', down='revoque')
cube('revoque_grafiti', 'Revoque con dibujos de tiza', 'Plaster with chalk drawings', 'revoque_grafiti', 4, up='revoque', down='revoque')
cube('revoque_zocalo', 'Revoque con zócalo', 'Plaster with baseboard', 'revoque_zocalo', 2, up='revoque', down='revoque')
cube('crema', 'Revoque crema', 'Cream plaster wall', 'crema', 3)
cube('crema_marcas', 'Revoque crema con marcas', 'Cream plaster with marks', 'crema_marcas', 3, up='crema', down='crema')
cube('friso', 'Friso de madera oscura', 'Dark wood wainscoting', 'friso', 4, sound='wood', up='friso_top')
cube('ladrillo_viejo', 'Ladrillo colonial', 'Old colonial brick', 'ladrillo_viejo', 2, sound='stone')
cube('adobe', 'Adobe', 'Adobe wall', 'adobe', 2, sound='dirt')
cube('azulejo', 'Azulejo blanco', 'White bathroom tiles', 'azulejo', 4, sound='tile')
cube('azulejo_guarda', 'Azulejo con guarda', 'Bathroom tiles with border', 'azulejo_guarda', 1, sound='tile', up='azulejo', down='azulejo')
# floors
cube('damero', 'Damero', 'Checkerboard tiles', 'damero', 3, sound='tile')
cube('damero_roto', 'Damero rajado', 'Cracked checkerboard tiles', 'damero_roto', 3, sound='tile')
cube('damero_faltante', 'Damero con baldosa faltante', 'Checkerboard with missing tile', 'damero_faltante', 3, sound='tile')
cube('damero_huellas', 'Damero con huellas', 'Checkerboard with small footprints', 'damero_huellas', 2, sound='tile')
cube('tablas', 'Piso de tablas', 'Classroom floorboards', 'tablas', 3, sound='wood')
cube('tablas_gastadas', 'Tablas gastadas', 'Worn floorboards', 'tablas_gastadas', 2, sound='wood')
cube('tabla_floja', 'Tabla floja', 'Loose creaking board', 'tabla_floja', 1, sound='wood')
# ceilings
cube('cielorraso', 'Cielorraso', 'Plaster ceiling', 'revoque', 4, up='revoque', down='cielorraso')
cube('cielorraso_tablas', 'Cielorraso de machimbre', 'Board ceiling', 'cielorraso_tablas', 2, sound='wood')

# --- windows, transom, trims
F('ventana_inf', 'Ventana colonial (abajo)', 'Colonial window (bottom)', window_parts('inf'), render='translucent', sound='glass')
F('ventana_med', 'Ventana colonial (medio)', 'Colonial window (middle)', window_parts('med'), render='translucent', sound='glass')
F('ventana_sup', 'Ventana colonial (arco)', 'Colonial window (arched top)', window_parts('sup'), render='translucent', sound='glass')
F('ventana_rota_inf', 'Ventana con vidrio roto', 'Window with broken glass', window_parts('inf', broken=True), render='translucent', sound='glass')
F('postigo_inf', 'Ventana con postigos (abajo)', 'Shuttered window (bottom)', window_parts('inf', glass=False, shutters=True), render='cutout')
F('postigo_med', 'Ventana con postigos (medio)', 'Shuttered window (middle)', window_parts('med', glass=False, shutters=True), render='cutout')
F('postigo_sup', 'Ventana con postigos (arco)', 'Shuttered window (arched top)', window_parts('sup', glass=False, shutters=True), render='cutout')
F('banderola', 'Banderola', 'Door transom', banderola_parts(), render='translucent', sound='glass')
F('cornisa', 'Cornisa', 'Crown moulding', cornisa_profile(True), sound='plaster', collision='none')
F('cornisa_esquina', 'Cornisa (rincón)', 'Crown moulding (inner corner)', cornisa_profile(True) + cornisa_profile(False), sound='plaster', collision='none')
F('viga', 'Viga', 'Ceiling beam', viga_parts(), collision='none')

# --- doors (two blocks tall, open by hand)
Door('colegio_puerta_aula_6', 'Puerta del aula de 6°', '6th grade classroom door', door_mat(lambda: p_door_aula(6)), kit=KIT, render='translucent')
Door('colegio_puerta_aula_4', 'Puerta del aula de 4°', '4th grade classroom door', door_mat(lambda: p_door_aula(4)), kit=KIT, render='translucent')
Door('colegio_puerta_direccion', 'Puerta de Dirección', "Headmistress's office door", door_mat(lambda: p_door_direccion(0)), kit=KIT)
Door('colegio_puerta_celda', 'Puerta de celda', 'Cell door', door_mat(lambda: p_door_celda(0)), kit=KIT)
Door('colegio_puerta_capilla', 'Puerta de la capilla', 'Chapel door', door_mat(lambda: p_door_capilla(0)), kit=KIT)
Door('colegio_porton', 'Portón de entrada', 'Main entrance door', door_mat(lambda: p_door_porton(0)), kit=KIT)
Door('colegio_puerta_cripta', 'Puerta de hierro de la cripta', 'Iron crypt door', door_mat(lambda: p_door_cripta(0)), kit=KIT, sound='metal')
Door('colegio_puerta_silencio', 'Puerta del Cuarto del Silencio', 'Silence Room door', door_mat(lambda: p_door_silencio(0)), kit=KIT, sound='metal')

cube('patio_lajas', 'Lajas del patio', 'Courtyard flagstones', 'patio_lajas', 3, sound='stone')
# --- cloister: columns and arches
F('columna_base', 'Columna (base)', 'Column (base)', column_parts('base'), sound='plaster')
F('columna_fuste', 'Columna (fuste)', 'Column (shaft)', column_parts('fuste'), sound='plaster')
F('columna_capitel', 'Columna (capitel)', 'Column (capital)', column_parts('capitel'), sound='plaster')
for (bx, by, k, es, en) in ((0, 0, 'arco_bajo_izq', 'Arco (arranque izq.)', 'Arch (left springer)'),
                            (2, 0, 'arco_bajo_der', 'Arco (arranque der.)', 'Arch (right springer)'),
                            (0, 1, 'arco_alto_izq', 'Arco (izquierda)', 'Arch (upper left)'),
                            (1, 1, 'arco_alto_centro', 'Arco (clave)', 'Arch (keystone)'),
                            (2, 1, 'arco_alto_der', 'Arco (derecha)', 'Arch (upper right)')):
    F(k, es, en, arch_block(bx, by), sound='plaster')

# --- stairs and balustrades
MADERA = cube('madera_oscura', 'Madera oscura', 'Dark wood boards', 'madera_oscura', 2, sound='wood')
Stairs('colegio_escalera_madera', 'Escalera de madera', 'Dark wood stairs', of=MADERA, kit=KIT, sound='wood')
Slab('colegio_losa_madera', 'Losa de madera', 'Dark wood slab', of=MADERA, kit=KIT, sound='wood')
PIEDRA = cube('piedra_escalon', 'Piedra gastada', 'Worn limestone', 'piedra_escalon', 2, sound='stone')
Stairs('colegio_escalera_piedra', 'Escalera de piedra', 'Stone stairs', of=PIEDRA, kit=KIT, sound='stone')
Slab('colegio_losa_piedra', 'Losa de piedra', 'Stone slab', of=PIEDRA, kit=KIT, sound='stone')
F('baranda', 'Baranda', 'Balustrade', baranda_parts())
F('baranda_poste', 'Poste de baranda', 'Newel post', baranda_poste_parts())
F('baranda_escalera_izq', 'Baranda de escalera (izq.)', 'Stair balustrade (left)', baranda_escalera_parts('izq'))
F('baranda_escalera_der', 'Baranda de escalera (der.)', 'Stair balustrade (right)', baranda_escalera_parts('der'))

# --- roof
TEJAS = cube('tejas', 'Tejas coloniales', 'Colonial roof tiles', 'tejas', 4, sound='ceramic')
Stairs('colegio_tejas_escalera', 'Tejado (escalera)', 'Roof tiles (stairs)', of=TEJAS, kit=KIT, sound='ceramic')
Slab('colegio_tejas_losa', 'Tejado (losa)', 'Roof tiles (slab)', of=TEJAS, kit=KIT, sound='ceramic')
F('alero', 'Alero con canecillos', 'Eave with rafter tails', alero_parts(), sound='ceramic')

# --- chapel
cube('sillar', 'Sillar de piedra', 'Chapel ashlar', 'sillar', 4, sound='stone')
cube('sillar_tallado', 'Sillar tallado (arquería ciega)', 'Carved ashlar (blind arcade)', 'sillar_tallado', 2, sound='stone', up='sillar', down='sillar')
cube('sillar_moldura', 'Sillar con moldura', 'Ashlar string course', 'sillar_moldura', 1, sound='stone', up='sillar', down='sillar')
cube('piso_capilla', 'Piso de la capilla', 'Chapel stone floor', 'piso_capilla', 3, sound='stone')
cube('lapida_piso', 'Lápida en el piso', 'Floor tomb slab', 'lapida_piso', 1, sound='stone', up='lapida_piso', down='sillar')
# --- crypt
CRIPTA_B = cube('cripta_piedra', 'Piedra de la cripta', 'Crypt rubble stone', 'cripta_piedra', 3, sound='stone')
Stairs('colegio_cripta_escalera', 'Bóveda de piedra (escalera)', 'Crypt stone stairs (vault)', of=CRIPTA_B, kit=KIT, sound='stone')
Slab('colegio_cripta_losa', 'Losa de piedra de la cripta', 'Crypt stone slab', of=CRIPTA_B, kit=KIT, sound='stone')
cube('cripta_piso', 'Piso de la cripta', 'Crypt floor', 'cripta_piso', 3, sound='stone')
cube('muro_ladrillo', 'Muro de ladrillo (1984)', 'Bricked-up wall (1984)', 'muro_ladrillo', 2, sound='stone')
cube('muro_ladrillo_grieta', 'Muro de ladrillo rajado', 'Bricked-up wall with crack', 'muro_ladrillo_grieta', 2, sound='stone', up='muro_ladrillo', down='muro_ladrillo')
# --- service floors
cube('mosaico_bano', 'Mosaico del baño', 'Bathroom mosaic floor', 'mosaico_bano', 2, sound='tile')
cube('baldosa_colorada', 'Baldosa colorada', 'Red kitchen tiles', 'baldosa_colorada', 2, sound='tile')

# --- stained glass, rose window
for nm, es_n, en_n in (('ines', 'Santa Inés', 'Saint Agnes'), ('geo', 'geométrico', 'geometric')):
    for pc, es_p, en_p in (('inf', 'abajo', 'bottom'), ('med', 'medio', 'middle'), ('sup', 'ojiva', 'pointed top')):
        F(f'vitral_{nm}_{pc}', f'Vitral {es_n} ({es_p})', f'Stained glass {en_n} ({en_p})', vitral_parts(nm, pc),
          render='translucent', sound='glass', light=0)
for gx, gy, k, es_p, en_p in ((0, 0, 'sup_izq', 'arriba izq.', 'top left'), (1, 0, 'sup_der', 'arriba der.', 'top right'),
                              (0, 1, 'inf_izq', 'abajo izq.', 'bottom left'), (1, 1, 'inf_der', 'abajo der.', 'bottom right')):
    F(f'roseton_{k}', f'Rosetón ({es_p})', f'Rose window ({en_p})', roseton_parts(gx, gy), render='translucent', sound='glass')

# --- crypt niches and the broken wall
F('nicho_garay', 'Nicho de Sor Purificación', 'Niche of Sister Purificación', nicho_parts(['SOR PURIFICACIÓN', 'GARAY', '1902 - 1971'], seed=1), sound='stone', collision='full')
F('nicho_roldan', 'Nicho de Sor Inmaculada', 'Niche of Sister Inmaculada', nicho_parts(['SOR INMACULADA', 'ROLDÁN', '1915 - 1980'], seed=2), sound='stone', collision='full')
F('nicho_iturbe', 'Nicho de la Madre Remedios', 'Niche of Mother Remedios', nicho_parts(['MADRE REMEDIOS', 'ITURBE', '1920 - 1991'], seed=3), sound='stone', collision='full')
F('nicho_agonia', 'Nicho vacío de Sor María', "Sister María's empty niche", nicho_parts(['SOR MARÍA DE LA', 'AGONÍA  1951 -'], open_=True, seed=4), sound='stone', collision='full')
F('nicho_sellado', 'Nicho sellado', 'Sealed niche', nicho_parts(None, seed=5), sound='stone', collision='full')
F('nicho_roto', 'Nicho con lápida rota', 'Niche with broken plaque', nicho_parts(['R.I.P.', 'HNA. ESPERANZA', '1899 - 1962'], seed=6, broken=True), sound='stone', collision='full')
F('muro_ladrillo_hueco', 'Muro de ladrillo con hueco', 'Bricked wall with a hole', ladrillo_hueco_parts(), sound='stone')

# --- plates, boards
F('cartel_aula_6', 'Cartel "6° GRADO"', '"6th grade" plate', wall_plate_parts([('6°', 'big'), ('GRADO', 't')], 10, 9, y0=4), sound='metal', collision='none')
F('cartel_aula_4', 'Cartel "4° GRADO"', '"4th grade" plate', wall_plate_parts([('4°', 'big'), ('GRADO', 't')], 10, 9, y0=4), sound='metal', collision='none')
F('cartel_direccion', 'Cartel "DIRECCIÓN"', '"Office" plate', wall_plate_parts([('DIRECCIÓN', 't')], 16, 5.5, y0=6, ramp=BRASS, ink='#2a1a08'), sound='metal', collision='none')
F('tablones_clavados', 'Tablones clavados', 'Boards nailed across a door', tablones_parts(), breakable=True)
