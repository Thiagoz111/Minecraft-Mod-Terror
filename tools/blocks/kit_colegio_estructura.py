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
    idx += np.where((m2 > 0.84) & (idx <= base), 1, 0) - np.where((m2 < 0.12) & (idx >= base), 1, 0)
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
