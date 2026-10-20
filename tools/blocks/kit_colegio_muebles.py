"""DEAD LINE building kit - Colegio Santa Ines de la Vigilia (1984): FURNITURE + PROPS (kit 'colegio_muebles').

Every block key starts with 'colegio_'. Authoring orientation (see bkit): furniture faces NORTH (front at z=0).
Conventions used in this kit:
  * seats / desks / beds: 'facing' = the direction the user LOOKS (a pupitre facing north = the pupil looks north).
  * wall pieces (boards, crosses, frames, signs, lamps): back against the wall, front = facing.
  * left/right ('_izq'/'_der') are as seen by the user / viewer standing in front of the piece.
  * 'sobre mesa' props (phone, mate, radio, plates, pot) are modelled 4/16 lower so they sit on our 12/16 tables,
    desks and the iron stove when placed in the block ABOVE them.
  * Big wall pictures (choir photo 3x2, Madre Benigna 2x3) are ONE block whose model overflows into the neighbours:
    the photo is placed at the bottom-centre of its 3x2 area, the portrait at the middle-left of its 2x3 area.

Painting: hand-built tone ramps, structured wood grain (3D growth rings + pores + knots + board seams), painted cast
iron with rust drips, contact ambient-occlusion computed from the model itself, dust on horizontal surfaces, crisp worn
edges. No directional light is baked (Minecraft shades faces).
"""
import math

from bkit import Furniture, Door, box, plane, NORMALS
from paint import hx, mix
from mcmodel import vnoise

KIT = 'colegio_muebles'


# ============================================================================================ palettes
def pal(*cols):
    return [hx(c) for c in cols]


# woods (dark -> light, hue-shifted: shadows purple-brown, lights warm amber)
NOGAL = pal('#140b0b', '#21120f', '#2f1a13', '#3e2318', '#4f2e1d', '#623a24', '#77492c', '#8d5a36', '#a66f45')
ROBLE = pal('#1b110d', '#2a1a12', '#3b2617', '#4e331d', '#634225', '#79522e', '#8f6439', '#a67847', '#bc8e59')
PINO = pal('#2a1d14', '#3f2c1d', '#574029', '#6f5436', '#886844', '#a07d54', '#b69266', '#c9a77b', '#d9bd94')
RAW = pal('#4a3524', '#6b4f36', '#8b6a49', '#a8875f', '#c2a278', '#d6ba92')  # bare wood under worn varnish
# metals
IRON = pal('#0c0b0f', '#141319', '#1c1b22', '#25252d', '#303139', '#3c3e48', '#4c4f5b', '#61656f', '#7b8089')
RUST = pal('#24110b', '#3a1b0f', '#542612', '#6e3317', '#89421d', '#a35526', '#bb6d36', '#cf8a4f')
WPAINT = pal('#47453f', '#625f57', '#7f7b71', '#9c978b', '#b6b1a3', '#cbc6b8', '#dcd8cb', '#e9e6db', '#f3f1ea')
BRASS = pal('#22160a', '#3a280f', '#563c15', '#74531d', '#936c27', '#b08835', '#c9a44c', '#dfc274', '#f1dfa6')
VERDI = pal('#24362f', '#344d42', '#4a6858', '#628371')
NICKEL = pal('#1d1f23', '#2e3136', '#43474d', '#5c6067', '#787c83', '#959aa0', '#b3b7bb', '#cfd2d4', '#e9ebec')
# boards / chalk
SLATE = pal('#0d1612', '#121d18', '#17241d', '#1c2b22', '#213228', '#273a2e', '#2f4436', '#3a5141', '#47604e')
CHALK = hx('#e4ebe5')
CHALK_Y = hx('#e8dc9a')
CHALK_P = hx('#e6b4c0')
# textiles
LINEN = pal('#4f4b47', '#6a665f', '#86817a', '#a09b92', '#b8b2a8', '#ccc7bc', '#dcd8ce', '#e8e5dc', '#f1efe8')
BLANKET = pal('#1e1d22', '#29282e', '#35343a', '#424147', '#504f55', '#605f64', '#727176')
NAVY = pal('#080c19', '#0d1426', '#131c35', '#1a2546', '#223058', '#2c3c6a')
SMOCK = pal('#4c5361', '#626b7c', '#7a8496', '#919cad', '#a7b1c1', '#bbc4d2', '#cdd4df', '#dde2ea', '#ebeef3', '#f5f7f9')
VELVET_R = pal('#1a0406', '#2a070b', '#3d0b10', '#521017', '#69171f', '#811f28', '#992b33', '#b03c41')
VELVET_P = pal('#140a17', '#1f1024', '#2b1733', '#382042', '#462a52', '#553563', '#654274')
RUSH = pal('#3a2a14', '#57401d', '#735727', '#8e6e33', '#a88742', '#bf9e55', '#d2b46c')  # esterilla (seat weave)
# stone / ceramics
MARBLE = pal('#57544f', '#716e68', '#8c8982', '#a6a39b', '#bdbab2', '#d0cdc5', '#e0ddd6', '#ece9e3', '#f6f4ef')
PORC = pal('#555a5d', '#71777a', '#8e9496', '#aab0b0', '#c2c6c4', '#d5d8d4', '#e4e5e0', '#efefea', '#f8f7f2')
ENAMEL = pal('#47443f', '#67645d', '#8a867e', '#aba79e', '#c6c2b8', '#dbd7cd', '#eae7de', '#f4f1ea')
EBLUE = pal('#0b1124', '#121b38', '#1b284f', '#263868', '#334a82')
# paper / misc
PAPER = pal('#4f4130', '#6d5b43', '#8a7657', '#a4906d', '#bba783', '#cebb98', '#ddcdac', '#e9dcc0', '#f2e8d4')
INK = hx('#1b1a2b')
INK_BLUE = hx('#1f2f6b')
INK_RED = hx('#8e1b1b')
CORK = pal('#33200f', '#4a3018', '#624122', '#7a532d', '#916639', '#a77a48', '#bb8e5b')
BAKE = pal('#070608', '#0e0c10', '#161319', '#1f1b22', '#29242d', '#35303a', '#46404b', '#5b5461')
GOLD = pal('#2a1a07', '#45300e', '#654816', '#87621f', '#a87e2a', '#c79b3c', '#deb957', '#efd583', '#f9ecbb')
GLASSR = pal('#220103', '#3d0306', '#62060a', '#8d0c0f', '#b81716', '#dd3221', '#f45f35', '#ff9a5c', '#ffd29a')
FLAME = pal('#6e1f05', '#b2420a', '#e2701a', '#f9a332', '#ffcc5a', '#ffe796', '#fffbe6')
WAX = pal('#5f584b', '#7f7766', '#a19782', '#bfb49b', '#d4cab1', '#e3dbc6', '#efe9d9', '#f7f4ea')
GREENP = pal('#0f1712', '#17221a', '#1f2d22', '#29392c', '#344637', '#415443', '#506452', '#637764')
REDP = pal('#200707', '#360c0b', '#4f120f', '#6b1914', '#86231a', '#9f3122', '#b64630', '#c96446')
SKIN = pal('#5b3d35', '#7a5246', '#986959', '#b4826e', '#c99a84', '#dbb49e', '#e9cab6', '#f3dece')
SKIN_C = pal('#4a3a3a', '#665152', '#836a69', '#a08584', '#baa09c', '#d0b9b3', '#e2d0c9', '#efe3dd')  # ivory corpus
BLUEM = pal('#0b1124', '#121b3a', '#1a2752', '#23346b', '#2f4584', '#3f599c', '#5674b4', '#7894cb', '#a3b8de')
CELESTE = pal('#2b4560', '#3d5d7d', '#527796', '#6a92ae', '#85abc4', '#a4c4d8', '#c4dbe8')
HAIR = pal('#0c0807', '#170f0c', '#241812', '#33221a', '#452e22', '#5a3c2b')
LEATHER_G = pal('#0b130e', '#111d15', '#18271c', '#203224', '#293e2d', '#344b37')
LEATHER_B = pal('#170c08', '#24130c', '#331b11', '#442416', '#572f1d', '#6c3c26', '#824b31')
DUST = hx('#958b7c')
MIRROR = pal('#0f1317', '#161c21', '#1f272d', '#29333a', '#36424a', '#46545d', '#5b6a73', '#77878f', '#9cabb2', '#c3cfd3')


def T(p, k):
    k = int(k)
    return p[0 if k < 0 else (len(p) - 1 if k >= len(p) else k)]


# ============================================================================================ hashing / noise
def hh(*a):
    """Stable hash -> [0, 1)."""
    h = 0x811c9dc5
    for v in a:
        h = ((h ^ (int(v) & 0xffffffff)) * 0x01000193) & 0xffffffff
        h ^= h >> 15
        h = (h * 0x2c1b3c6d) & 0xffffffff
    h ^= h >> 12
    h = (h * 0x297a2d39) & 0xffffffff
    h ^= h >> 15
    return (h & 0xffffff) / 16777216.0


def vn(x, y, z=0.0, s=0):
    return vnoise(x, y, z, s)


FI = {'north': 1, 'south': 2, 'west': 3, 'east': 4, 'up': 5, 'down': 6, 'bottom': 7, 'top': 8}
BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]


def bay(x, y):
    return (BAYER[int(y) & 3][int(x) & 3] + 0.5) / 16.0


def tp(ctx, off=(0, 0, 0)):
    """Texel-space position (2 texels per model unit)."""
    p = ctx.pos
    return ((p[0] + off[0]) * 2.0, (p[1] + off[1]) * 2.0, (p[2] + off[2]) * 2.0)


def nax(ctx):
    n = ctx.n
    return 0 if n[0] else (1 if n[1] else 2)


# ============================================================================================ contact AO + dust
_OC = {}


def _aoboxes(blk):
    bs = blk.__dict__.get('_aob')
    if bs is None:
        bs = [(p, p.frm + p.to) for p in blk.parts if not p.rot and min(p.size()) > 0.05]
        blk._aob = bs
    return bs


def occlusion(ctx, R=1.3):
    part, blk, face = ctx.part, ctx.block, ctx.face
    if not hasattr(blk, 'parts'):
        return 0.0
    key = (id(blk), id(part), face)
    cand = _OC.get(key)
    if cand is None:
        f, t = part.frm, part.to
        lo = [f[k] - R - 0.7 for k in range(3)]
        hi = [t[k] + R + 0.7 for k in range(3)]
        near = []
        for q, b in _aoboxes(blk):
            if q is part:
                continue
            if all(b[k] <= hi[k] and b[k + 3] >= lo[k] for k in range(3)):
                near.append(b)
        env = getattr(blk, 'env', ('floor',))
        if 'floor' in env:
            near.append((-99, -99, -99, 99, 0, 99))
        if 'wall' in env:
            near.append((-99, -99, 16, 99, 99, 99))
        if 'ceil' in env:
            near.append((-99, 16, -99, 99, 99, 99))
        over = [b for q, b in _aoboxes(blk) if q is not part and b[1] > f[1] + 0.3] if face != 'down' else []
        cand = (near, over)
        _OC[key] = cand
    near, over = cand
    p, n = ctx.pos, ctx.n
    sx, sy, sz = p[0] + n[0] * 0.5, p[1] + n[1] * 0.5, p[2] + n[2] * 0.5
    occ = 0.0
    RR = R * R
    for b in near:
        dx = b[0] - sx if sx < b[0] else (sx - b[3] if sx > b[3] else 0.0)
        dy = b[1] - sy if sy < b[1] else (sy - b[4] if sy > b[4] else 0.0)
        dz = b[2] - sz if sz < b[2] else (sz - b[5] if sz > b[5] else 0.0)
        d2 = dx * dx + dy * dy + dz * dz
        if d2 < RR:
            o = 1.0 - math.sqrt(d2) / R
            if o > occ:
                occ = o
    for b in over:
        if b[0] <= sx <= b[3] and b[2] <= sz <= b[5] and b[1] > sy:
            d = b[1] - sy
            o = 0.62 if d < 5 else (0.45 if d < 9 else 0.0)
            if o > occ:
                occ = o
    return occ


def dusty(ctx, c, amt):
    x, y, z = tp(ctx)
    n = vn(x / 9.0, y / 9.0 + 0.3, z / 9.0, 71) * 0.75 + vn(x / 4.0, y / 4.0, z / 4.0, 72) * 0.25
    lv = 1 + (n > 0.5) + (n > 0.66)
    if 0.48 < n < 0.52 or 0.64 < n < 0.68:
        lv += -1 if bay(x, z) > 0.5 else 0
    return mix(c, DUST, 0.07 * lv * amt)


def fin(tone, ao=1.0, dust=1.0):
    """Turn a tone function (ctx -> (palette, step) | rgba | None) into a bkit material."""
    def m(ctx):
        r = tone(ctx)
        if r is None:
            return None
        if type(r[0]) is list:
            p, k = r
            if ao:
                o = occlusion(ctx)
                if o > 0.78:
                    k -= 2 * ao
                elif o > 0.4:
                    k -= 1 * ao
            c = T(p, round(k))
        else:
            c = r
        if dust and ctx.face == 'up' and c[3] > 0:
            c = dusty(ctx, c, dust)
        return c
    return m


# ============================================================================================ tone functions
def _grain_axis(part):
    S = part.size()
    return 0 if S[0] >= S[1] and S[0] >= S[2] else (1 if S[1] >= S[2] else 2)


_KN = {}


def _knots(part, face, sd, density):
    key = (id(part), face, sd)
    k = _KN.get(key)
    if k is None:
        w, h = part.face_px(face)
        area = w * h
        k = []
        n = int(density * area / 260.0 + hh(sd, w, h, 5))
        for i in range(min(n, 3)):
            k.append((hh(sd, i, 11, w) * w, hh(sd, i, 12, h) * h, 0.9 + hh(sd, i, 13) * 1.1))
        _KN[key] = k
    return k


def wood(p=ROBLE, base=4, seed=0, axis=None, period=6.5, boards=None, off=(0, 0, 0), wear=0.45, knots=0.25,
         streak=0.07, end=-1, worn_pal=None, figure=0.5):
    """Structured wood grain: growth-ring lines (cathedral arcs), long pores, broad figure, rare knots, glued boards.
    boards=(axis, width_px) splits the piece into glued boards with dark seams."""
    def t(ctx):
        part = ctx.part
        g = axis if axis is not None else _grain_axis(part)
        P = tp(ctx, off)
        na = nax(ctx)
        sd = seed
        seam = False
        bk = 0
        if boards:
            bax, bw = boards
            bc = P[bax] / bw
            bid = math.floor(bc + 1e-6)
            sd = seed + bid * 101
            bk = 1 if hh(sd, 77) > 0.8 else (-1 if hh(sd, 77) < 0.2 else 0)
            if bax != na and (bc - bid) * bw < 0.999:
                seam = True
        a1, a2 = [k for k in range(3) if k != g]
        along = P[g]
        f, tt = part.frm, part.to
        m1 = (f[a1] + tt[a1]) + off[a1] * 2
        m2 = (f[a2] + tt[a2]) + off[a2] * 2
        c1 = m1 + (22 + hh(sd, 1) * 40) * (1 if hh(sd, 2) > 0.5 else -1)
        c2 = m2 + (hh(sd, 3) - 0.5) * 16 + (hh(sd, 4) - 0.5) * 0.22 * along
        wv = 2.2 * vn(along / 14.0, sd * 0.37, 0.5, sd) + 0.8 * vn(along / 5.0, 2.1, sd * 0.11, sd + 1)
        r = math.hypot(P[a1] - c1, P[a2] - c2) + wv
        if knots and na != g:
            for (ku, kv, ks) in _knots(part, ctx.face, sd, knots):
                gi = (g == 0 and ctx.face in ('north', 'south', 'up', 'down')) or (g == 2 and ctx.face in ('west', 'east'))
                du, dv = ctx.i + 0.5 - ku, ctx.j + 0.5 - kv
                d = math.hypot(du * (0.6 if gi else 1.0), dv * (1.0 if gi else 0.6))
                ks = 0.55 + ks * 0.35
                if d < ks:
                    return (p, base - 3)
                if d < ks + 0.9:
                    return (p, base - 2)
                if d < ks + 5.0:
                    r += (ks + 5.0 - d) * 1.1
        q = r / period
        ri = math.floor(q)
        fr = q - ri
        k = base + bk
        if fr < 0.15:
            k -= 1
        elif 0.5 < fr < 0.68 and hh(ri, sd, 7) > 0.35:
            k += 1
        if na == g:  # end grain: darker, ring arcs
            k = base + end + bk + (-1 if fr < 0.2 else 0)
        else:
            ac = P[a1] if na == a2 else P[a2]
            ai = math.floor(ac)
            seg = math.floor((along + hh(ai, sd) * 13.0) / 11.0)
            qq = hh(ai, seg, sd)
            if qq < streak:
                k -= 1
            elif qq > 1 - streak * 0.5:
                k += 1
            if figure:
                fv = vn(along / 16.0, ac / 7.0, sd * 0.3, sd + 3)
                if fv > 0.72:
                    k += 1
                elif fv < 0.22:
                    k -= 1
        if seam:
            k = base - 3
        if wear and ctx.face != 'down' and ctx.edge() == 0:
            # contiguous worn segments along edges
            e = (ctx.i if ctx.j in (0, ctx.h - 1) else ctx.j) // 4
            wv2 = hh(e, FI[ctx.face], round(P[0] * 0.25), round(P[1] * 0.25), round(P[2] * 0.25), seed)
            if wv2 < wear:
                if worn_pal is not None and wv2 < wear * 0.3:
                    return (worn_pal, 2)
                k += 1
        return (p, k)
    return t


def iron(p=IRON, base=3, seed=0, rust=0.3, off=(0, 0, 0), worn=0.3, pits=0.02, drips=True):
    """Black-painted cast iron: worn bright edges, sparse casting pits, rust patches that bleed down."""
    thr = 1.0 - rust * 0.5

    def rn(x, y, z):
        n = vn(x / 8.0, y / 8.0, z / 8.0, seed + 40) * 0.82 + vn(x / 3.5, y / 3.5, z / 3.5, seed + 41) * 0.18
        return n + 0.14 * max(0.0, 1.0 - y / 12.0)

    def t(ctx):
        P = tp(ctx, off)
        n = rn(*P)
        if n > thr:
            dpt = (n - thr) / max(0.05, 1 - thr)
            k = 2 + int(dpt * 3.5)
            if hh(P[0], P[1], P[2], seed, 1) < 0.08:
                k -= 1
            return (RUST, k)
        if n > thr - 0.03:
            return (RUST, 0)
        k = base
        if drips and ctx.face not in ('up', 'down'):
            col = math.floor(P[0] if ctx.face in ('north', 'south') else P[2])
            if hh(col, seed, 9) < 0.5:
                for d in (2.0, 4.0, 6.5):
                    if rn(P[0], P[1] + d, P[2]) > thr + 0.04:
                        return (RUST, 1 if d > 5 else 2)
        if hh(P[0], P[1], P[2], seed, 2) < pits:
            k -= 1
        if ctx.edge() == 0 and ctx.face != 'down':
            e = (ctx.i if ctx.j in (0, ctx.h - 1) else ctx.j) // 3
            if hh(e, FI[ctx.face], round(P[0] * .25), round(P[1] * .25), round(P[2] * .25), seed) < worn:
                k += 2
        return (p, k)
    return t


def painted_iron(paint=WPAINT, base=6, seed=0, chips=0.3, off=(0, 0, 0)):
    """Iron painted cream-white (dormitory beds): chips show black iron ringed with rust, yellowed patches."""
    thr = 1.0 - chips * 0.5

    def t(ctx):
        P = tp(ctx, off)
        n = vn(P[0] / 4.0, P[1] / 4.0, P[2] / 4.0, seed + 60) * 0.7 + vn(P[0] / 1.6, P[1] / 1.6, P[2] / 1.6, seed + 61) * 0.3
        if ctx.edge() == 0:
            n += 0.1
        if n > thr + 0.06:
            return (IRON, 2 + (hh(*P, seed) > 0.7))
        if n > thr:
            return (RUST, 3 + (hh(*P, seed, 2) > 0.5))
        k = base
        y = vn(P[0] / 9.0, P[1] / 9.0, P[2] / 9.0, seed + 62)
        if y > 0.62:
            k -= 1
        if y < 0.3:
            k += 1
        if ctx.edge() == 0 and ctx.face != 'down':
            k -= 1
        return (paint, k)
    return t


def brass(p=BRASS, base=5, seed=0, tarnish=0.35, sheen=True, off=(0, 0, 0)):
    def t(ctx):
        P = tp(ctx, off)
        k = base
        if sheen:
            if ctx.face in ('up', 'down'):
                u = ctx.s
            else:
                u = ctx.s if ctx.w >= ctx.h else ctx.t
            c = abs(u * 2 - 1)
            k += 1 if c < 0.3 else (0 if c < 0.75 else -1)
        n = vn(P[0] / 3.0, P[1] / 3.0, P[2] / 3.0, seed + 80)
        if n > 1 - tarnish * 0.6:
            if n > 1 - tarnish * 0.3:
                return (VERDI, 1 + (hh(*P) > 0.5))
            k -= 2
        if ctx.edge() == 0 and ctx.face != 'down':
            k += 1
        return (p, k)
    return t


def painted(p, base=4, seed=0, chips=0.0, under=None, under_k=3, grime=0.25, off=(0, 0, 0), bevel=False, wear=0.25):
    """Flat painted surface with soft mottling, optional chips revealing `under` and worn edges."""
    def t(ctx):
        P = tp(ctx, off)
        n = vn(P[0] / 5.0, P[1] / 5.0, P[2] / 5.0, seed + 90)
        k = base + (1 if n > 0.68 else (-1 if n < 0.3 else 0))
        if chips:
            c = vn(P[0] / 2.2, P[1] / 2.2, P[2] / 2.2, seed + 91) + (0.12 if ctx.edge() == 0 else 0)
            if c > 1 - chips * 0.45:
                return (under or RUST, under_k + (hh(*P) > 0.6))
        if grime and ctx.face not in ('up', 'down') and P[1] < 6:
            if hh(P[0], P[1], P[2], seed) < grime * (1 - P[1] / 6):
                k -= 1
        if bevel and ctx.face not in ('up', 'down'):
            if ctx.j == 0 or ctx.i == 0:
                k += 1
            elif ctx.j == ctx.h - 1 or ctx.i == ctx.w - 1:
                k -= 1
        elif wear and ctx.edge() == 0 and ctx.face != 'down' and hh(round(P[0] * .5), round(P[1] * .5), round(P[2] * .5), seed) < wear:
            k += 1
        return (p, k)
    return t


def flat(p, k):
    return lambda ctx: (p, k)


def cloth(p=LINEN, base=6, seed=0, fold_axis='i', folds=0.6, fold_px=5.0, weave=True, stains=0.25, hem=False,
          stain_col=hx('#a08a5a'), off=(0, 0, 0)):
    """Woven fabric: fine weave, soft folds along one face axis, water/sweat stains with darker rims."""
    def t(ctx):
        P = tp(ctx, off)
        k = base
        if folds:
            u = (ctx.i if fold_axis == 'i' else ctx.j) + 0.5
            ph = hh(seed, FI[ctx.face], 3) * 6.28
            v = math.sin(u / fold_px * 2.1 + ph + 0.8 * math.sin(u / (fold_px * 2.7) + ph))
            k += (1 if v > 0.55 else (-1 if v < -0.5 else 0)) * (1 if folds > 0.3 else 0)
            if folds > 0.8 and v < -0.85:
                k -= 1
        if weave:
            if (ctx.i % 4 == 0 and ctx.j % 2 == 0) or (ctx.j % 4 == 2 and ctx.i % 2 == 1):
                k -= 1 if hh(ctx.i, ctx.j, seed) < 0.55 else 0
        if hem and ctx.edge() == 1:
            k -= 1
        c = T(p, k)
        if stains:
            n = vn(P[0] / 5.5, P[1] / 5.5, P[2] / 5.5, seed + 30)
            th = 1 - stains * 0.5
            if n > th + 0.04:
                c = mix(c, stain_col, 0.28)
            elif n > th:
                c = mix(c, stain_col, 0.5)
        return c
    return t


def marble(p=MARBLE, base=6, seed=0, off=(0, 0, 0)):
    def t(ctx):
        P = tp(ctx, off)
        w = vn(P[0] / 6.0, P[1] / 6.0, P[2] / 6.0, seed) * 6.0
        v = abs(math.sin((P[0] * 0.35 + P[1] * 0.55 + P[2] * 0.25 + w) * 0.9))
        k = base
        if v < 0.08:
            k -= 3
        elif v < 0.22:
            k -= 1
        n = vn(P[0] / 3.0, P[1] / 3.0, P[2] / 3.0, seed + 5)
        if n > 0.7:
            k += 1
        if ctx.edge() == 0 and ctx.face != 'down':
            k += 1
        return (p, k)
    return t


def glow(p, base=5, seed=0):
    """Glass/flame-like emissive gradient: brighter centre."""
    def t(ctx):
        c = 1 - max(abs(ctx.s * 2 - 1), abs(ctx.t * 2 - 1))
        k = base - 2 + int(c * 4.5)
        if hh(ctx.i, ctx.j, seed) < 0.08:
            k += 1
        return (p, k)
    return t


def img_tone(get):
    """Tone from a precomputed per-(part,face) RGBA function get(ctx) -> rgba or (pal,k)."""
    return get


# ============================================================================================ fonts
F35 = {
    'A': ['.#.', '#.#', '###', '#.#', '#.#'], 'B': ['##.', '#.#', '##.', '#.#', '##.'], 'C': ['.##', '#..', '#..', '#..', '.##'],
    'D': ['##.', '#.#', '#.#', '#.#', '##.'], 'E': ['###', '#..', '##.', '#..', '###'], 'F': ['###', '#..', '##.', '#..', '#..'],
    'G': ['.##', '#..', '#.#', '#.#', '.##'], 'H': ['#.#', '#.#', '###', '#.#', '#.#'], 'I': ['#', '#', '#', '#', '#'],
    'J': ['..#', '..#', '..#', '#.#', '.#.'], 'K': ['#.#', '#.#', '##.', '#.#', '#.#'], 'L': ['#..', '#..', '#..', '#..', '###'],
    'M': ['#...#', '##.##', '#.#.#', '#...#', '#...#'], 'N': ['#..#', '##.#', '#.##', '#..#', '#..#'],
    'O': ['.#.', '#.#', '#.#', '#.#', '.#.'], 'P': ['##.', '#.#', '##.', '#..', '#..'], 'Q': ['.#.', '#.#', '#.#', '##.', '.##'],
    'R': ['##.', '#.#', '##.', '#.#', '#.#'], 'S': ['.##', '#..', '.#.', '..#', '##.'], 'T': ['###', '.#.', '.#.', '.#.', '.#.'],
    'U': ['#.#', '#.#', '#.#', '#.#', '###'], 'V': ['#.#', '#.#', '#.#', '#.#', '.#.'], 'W': ['#...#', '#...#', '#.#.#', '##.##', '#...#'],
    'X': ['#.#', '#.#', '.#.', '#.#', '#.#'], 'Y': ['#.#', '#.#', '.#.', '.#.', '.#.'], 'Z': ['###', '..#', '.#.', '#..', '###'],
    '0': ['###', '#.#', '#.#', '#.#', '###'], '1': ['.#', '##', '.#', '.#', '.#'], '2': ['##.', '..#', '.#.', '#..', '###'],
    '3': ['##.', '..#', '.#.', '..#', '##.'], '4': ['#.#', '#.#', '###', '..#', '..#'], '5': ['###', '#..', '##.', '..#', '##.'],
    '6': ['.##', '#..', '###', '#.#', '###'], '7': ['###', '..#', '.#.', '.#.', '.#.'], '8': ['###', '#.#', '###', '#.#', '###'],
    '9': ['###', '#.#', '###', '..#', '##.'], '.': ['.', '.', '.', '.', '#'], ',': ['.', '.', '.', '#', '#'],
    '-': ['...', '...', '###', '...', '...'], '?': ['##.', '..#', '.#.', '...', '.#.'], '¿': ['.#.', '...', '.#.', '#..', '.##'],
    '!': ['#', '#', '#', '.', '#'], ':': ['.', '#', '.', '#', '.'], "'": ['#', '#', '.', '.', '.'], ' ': ['..', '..', '..', '..', '..'],
    '/': ['..#', '..#', '.#.', '#..', '#..'], '+': ['...', '.#.', '###', '.#.', '...'], '°': ['##', '##', '..', '..', '..'],
    'N.': ['#..#', '##.#', '#.##', '#..#', '#..#'],
}
F35_ACC = {'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U', 'Ñ': 'N'}

F57 = {
    'A': ['.###.', '#...#', '#...#', '#####', '#...#', '#...#', '#...#'], 'B': ['####.', '#...#', '#...#', '####.', '#...#', '#...#', '####.'],
    'C': ['.###.', '#...#', '#....', '#....', '#....', '#...#', '.###.'], 'D': ['####.', '#...#', '#...#', '#...#', '#...#', '#...#', '####.'],
    'E': ['#####', '#....', '#....', '####.', '#....', '#....', '#####'], 'F': ['#####', '#....', '#....', '####.', '#....', '#....', '#....'],
    'G': ['.###.', '#...#', '#....', '#.###', '#...#', '#...#', '.####'], 'H': ['#...#', '#...#', '#...#', '#####', '#...#', '#...#', '#...#'],
    'I': ['###', '.#.', '.#.', '.#.', '.#.', '.#.', '###'], 'J': ['..###', '...#.', '...#.', '...#.', '...#.', '#..#.', '.##..'],
    'K': ['#...#', '#..#.', '#.#..', '##...', '#.#..', '#..#.', '#...#'], 'L': ['#....', '#....', '#....', '#....', '#....', '#....', '#####'],
    'M': ['#...#', '##.##', '#.#.#', '#.#.#', '#...#', '#...#', '#...#'], 'N': ['#...#', '#...#', '##..#', '#.#.#', '#..##', '#...#', '#...#'],
    'O': ['.###.', '#...#', '#...#', '#...#', '#...#', '#...#', '.###.'], 'P': ['####.', '#...#', '#...#', '####.', '#....', '#....', '#....'],
    'Q': ['.###.', '#...#', '#...#', '#...#', '#.#.#', '#..#.', '.##.#'], 'R': ['####.', '#...#', '#...#', '####.', '#.#..', '#..#.', '#...#'],
    'S': ['.####', '#....', '#....', '.###.', '....#', '....#', '####.'], 'T': ['#####', '..#..', '..#..', '..#..', '..#..', '..#..', '..#..'],
    'U': ['#...#', '#...#', '#...#', '#...#', '#...#', '#...#', '.###.'], 'V': ['#...#', '#...#', '#...#', '#...#', '#...#', '.#.#.', '..#..'],
    'W': ['#...#', '#...#', '#...#', '#.#.#', '#.#.#', '#.#.#', '.#.#.'], 'X': ['#...#', '#...#', '.#.#.', '..#..', '.#.#.', '#...#', '#...#'],
    'Y': ['#...#', '#...#', '.#.#.', '..#..', '..#..', '..#..', '..#..'], 'Z': ['#####', '....#', '...#.', '..#..', '.#...', '#....', '#####'],
    'a': ['....', '....', '.##.', '...#', '.###', '#..#', '.###'], 'b': ['#...', '#...', '###.', '#..#', '#..#', '#..#', '###.'],
    'c': ['....', '....', '.##.', '#..#', '#...', '#..#', '.##.'], 'd': ['...#', '...#', '.###', '#..#', '#..#', '#..#', '.###'],
    'e': ['....', '....', '.##.', '#..#', '####', '#...', '.##.'], 'f': ['..#.', '.#.#', '.#..', '###.', '.#..', '.#..', '.#..'],
    'g': ['....', '....', '.###', '#..#', '#..#', '.###', '...#', '#..#', '.##.'], 'h': ['#...', '#...', '###.', '#..#', '#..#', '#..#', '#..#'],
    'i': ['.#.', '...', '##.', '.#.', '.#.', '.#.', '###'], 'j': ['..#', '...', '.##', '..#', '..#', '..#', '..#', '#.#', '.#.'],
    'k': ['#...', '#...', '#..#', '#.#.', '##..', '#.#.', '#..#'], 'l': ['##.', '.#.', '.#.', '.#.', '.#.', '.#.', '###'],
    'm': ['.....', '.....', '##.#.', '#.#.#', '#.#.#', '#.#.#', '#.#.#'], 'n': ['....', '....', '###.', '#..#', '#..#', '#..#', '#..#'],
    'o': ['....', '....', '.##.', '#..#', '#..#', '#..#', '.##.'], 'p': ['....', '....', '###.', '#..#', '#..#', '#..#', '###.', '#...', '#...'],
    'q': ['....', '....', '.###', '#..#', '#..#', '#..#', '.###', '...#', '...#'], 'r': ['....', '....', '#.##', '##..', '#...', '#...', '#...'],
    's': ['....', '....', '.###', '#...', '.##.', '...#', '###.'], 't': ['.#..', '.#..', '###.', '.#..', '.#..', '.#.#', '..#.'],
    'u': ['....', '....', '#..#', '#..#', '#..#', '#..#', '.###'], 'v': ['.....', '.....', '#...#', '#...#', '.#.#.', '.#.#.', '..#..'],
    'w': ['.....', '.....', '#...#', '#...#', '#.#.#', '#.#.#', '.#.#.'], 'x': ['....', '....', '#..#', '#..#', '.##.', '#..#', '#..#'],
    'y': ['....', '....', '#..#', '#..#', '#..#', '.###', '...#', '#..#', '.##.'], 'z': ['....', '....', '####', '..#.', '.#..', '#...', '####'],
    'á': ['..#.', '.#..', '.##.', '...#', '.###', '#..#', '.###'], 'é': ['..#.', '.#..', '.##.', '#..#', '####', '#...', '.##.'],
    'í': ['..#', '.#.', '##.', '.#.', '.#.', '.#.', '###'], 'ó': ['..#.', '.#..', '.##.', '#..#', '#..#', '#..#', '.##.'],
    'ú': ['..#.', '.#..', '#..#', '#..#', '#..#', '#..#', '.###'], 'ñ': ['.#.#', '#.#.', '###.', '#..#', '#..#', '#..#', '#..#'],
    '0': ['.##.', '#..#', '#..#', '#..#', '#..#', '#..#', '.##.'], '1': ['.#.', '##.', '.#.', '.#.', '.#.', '.#.', '###'],
    '2': ['.##.', '#..#', '...#', '..#.', '.#..', '#...', '####'], '3': ['###.', '...#', '...#', '.##.', '...#', '...#', '###.'],
    '4': ['#..#', '#..#', '#..#', '####', '...#', '...#', '...#'], '5': ['####', '#...', '###.', '...#', '...#', '#..#', '.##.'],
    '6': ['.##.', '#...', '#...', '###.', '#..#', '#..#', '.##.'], '7': ['####', '...#', '..#.', '..#.', '.#..', '.#..', '.#..'],
    '8': ['.##.', '#..#', '#..#', '.##.', '#..#', '#..#', '.##.'], '9': ['.##.', '#..#', '#..#', '.###', '...#', '...#', '.##.'],
    '.': ['.', '.', '.', '.', '.', '.', '#'], ',': ['.', '.', '.', '.', '.', '#', '#', '#'], '-': ['...', '...', '...', '###', '...', '...', '...'],
    '?': ['.##.', '#..#', '...#', '..#.', '.#..', '....', '.#..'], '¿': ['..#.', '....', '..#.', '.#..', '#...', '#..#', '.##.'],
    '!': ['#', '#', '#', '#', '#', '.', '#'], ':': ['.', '.', '#', '.', '.', '#', '.'], ' ': ['...'] * 7,
    '+': ['.....', '..#..', '..#..', '#####', '..#..', '..#..', '.....'], '♪': ['..#.', '..##', '..#.', '..#.', '.##.', '###.', '.#..'],
    '/': ['....#', '...#.', '...#.', '..#..', '.#...', '.#...', '#....'], "'": ['#', '#', '.', '.', '.', '.', '.'],
    '_': ['....', '....', '....', '....', '....', '....', '####'], '<': ['...', '..#', '.#.', '#..', '.#.', '..#', '...'],
    '♥': ['.....', '.#.#.', '#####', '#####', '.###.', '..#..', '.....'],
}
F57_ACC = {'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U', 'Ñ': 'N'}


def glyph(font, ch):
    """Return (rows, top_offset) for a character; accented capitals get their accent drawn above."""
    acc = F35_ACC if font is F35 else F57_ACC
    if ch in font:
        return font[ch], 0
    if ch in acc:
        rows = font[acc[ch]]
        w = len(rows[0])
        if ch == 'Ñ':
            top = ['.' * w]
            top[0] = ('#' * (w // 2)).rjust(w - 1, '.') + '.'
            return top + rows, -2 if font is F57 else -1
        mid = w // 2 + (1 if w > 3 else 0)
        acc_rows = ['.' * mid + '#' + '.' * (w - mid - 1)] if font is F35 else \
            ['.' * min(w - 1, mid + 1) + '#' + '.' * (w - min(w - 1, mid + 1) - 1), '.' * mid + '#' + '.' * (w - mid - 1)]
        acc_rows = [r[:w] for r in acc_rows]
        return acc_rows + rows, -len(acc_rows) - (0 if font is F35 else 0)
    up = ch.upper()
    if up in font:
        return font[up], 0
    return font.get('?', [['#']]), 0


def text_width(font, s, sp=1):
    return sum(len(glyph(font, c)[0][0]) + sp for c in s) - sp if s else 0


def draw_text(font, s, x, y, sp=1, italic=0.0, jitter=0.0, seed=0, plot=None):
    """Rasterise text; returns list of (x, y). italic = px shift per row (handwriting slant)."""
    out = []
    cx = x
    for n, ch in enumerate(s):
        rows, top = glyph(font, ch)
        jy = 0
        if jitter:
            jy = int(round((hh(seed, n, 1) - 0.5) * 2 * jitter))
        for j, row in enumerate(rows):
            yy = y + top + j + jy
            sh = int(round((len(rows) + top - j) * italic)) if italic else 0
            for i, c in enumerate(row):
                if c == '#':
                    out.append((cx + i + sh, yy))
        cx += len(rows[0]) + sp
    return out


# ============================================================================================ small helpers
def mirror_parts(parts):
    """Mirror a list of parts across x=8 (left half -> right half)."""
    out = []
    for p in parts:
        f, t = p.frm, p.to
        rot = p.rot
        if rot:
            ax, ang, org = rot
            rot = (ax, -ang if ax in ('y', 'z') else ang, (16 - org[0], org[1], org[2]))
        q = type(p)((16 - t[0], f[1], f[2]), (16 - f[0], t[1], t[2]), p.mat, faces=p.faces, rot=rot, decals=p.decals,
                    shade=p.shade, name=p.name, cull=p.cull)
        out.append(q)
    return out


def F(key, es, en, parts, env=('floor',), sound='wood', light=0, render='cutout', collision='auto', directional=True,
      breakable=False, mat=None):
    b = Furniture('colegio_' + key, es, en, parts, kit=KIT, sound=sound, light=light, render=render, collision=collision,
                  directional=directional, breakable=breakable, mat=mat)
    b.env = env
    return b


def shift(parts, dx=0, dy=0, dz=0):
    for p in parts:
        p.frm = (p.frm[0] + dx, p.frm[1] + dy, p.frm[2] + dz)
        p.to = (p.to[0] + dx, p.to[1] + dy, p.to[2] + dz)
        if p.rot:
            ax, ang, o = p.rot
            p.rot = (ax, ang, (o[0] + dx, o[1] + dy, o[2] + dz))
    return parts


# ============================================================================================ shared materials
M_ROBLE_TOP = None  # built per piece (carvings)
M_IRON = fin(iron(seed=3))
M_IRON2 = fin(iron(seed=17, rust=0.38))
M_BRASS = fin(brass(seed=5), dust=0.6)
M_ROBLE = fin(wood(ROBLE, seed=21, worn_pal=RAW))
M_NOGAL = fin(wood(NOGAL, seed=31, worn_pal=RAW, wear=0.35))
M_PINO = fin(wood(PINO, seed=41, base=4, wear=0.5))


# ============================================================================================ CLASSROOM
def desk_top_tone(seed, off, side):
    """Pupitre top: oak boards + pencil groove, inkwell hole, carved graffiti and wear where arms rest."""
    base = wood(ROBLE, seed=seed, boards=(2, 8), off=off, worn_pal=RAW, knots=0.3)
    # carvings in desk-top texel coords (x 0..31 across the half, z 0..15 depth)
    carve = set()
    if side == 'izq':
        for (x, z) in [(6, 10), (7, 9), (8, 10), (9, 9), (10, 10), (7, 11), (8, 12), (9, 11), (8, 11)]:  # heart
            carve.add((x, z))
        for i in range(7):  # seven tally marks...
            for d in range(4):
                carve.add((15 + i * 2, 9 + d))
        for d in range(9):
            carve.add((14 + d * 2 - (d // 3), 10 + (d % 2)))
    else:
        for (x, z) in draw_text(F35, 'PF', 4, 9) + draw_text(F35, '84', 14, 9):
            carve.add((x, z))
        for d in range(10):
            carve.add((19 + d, 13 - d // 4))

    def t(ctx):
        r = base(ctx)
        if ctx.face != 'up':
            return r
        X = int(ctx.pos[0] * 2)
        Z = int(ctx.pos[2] * 2)
        if side == 'der':
            X = int(ctx.pos[0] * 2)
        # pencil groove along x at z = 3.6..4.2 units (texel 7..8)
        if Z == 7:
            return (ROBLE, 1)
        if Z == 8:
            return (ROBLE, 3)
        # inkwell hole: x 7..9, z 1.5..3.5 units (texels 14..17, 3..6)
        if 14 <= X <= 17 and 3 <= Z <= 6:
            if (X, Z) == (15, 4):
                return (NAVY, 4)
            return (IRON, 0 if 15 <= X <= 16 and 4 <= Z <= 5 else 1)
        if (X, Z) in carve:
            return (RAW, 1 if (X + Z) % 3 else 2)
        if (X, Z - 1) in carve:
            return (ROBLE, 2)
        # elbows wore the varnish near the pupil's edge
        if Z > 12 and hh(X, Z, seed) < 0.10 * (Z - 12):
            return (RAW, 1)
        return r
    return t


def pupitre_parts(side, bench=True):
    """Double desk half (cast-iron side frame on the outer side). Built as the LEFT half then mirrored."""
    off = (0, 0, 0) if side == 'izq' else (16, 0, 0)
    mI = M_IRON
    mW = fin(wood(ROBLE, seed=23, off=off, worn_pal=RAW))
    mTop = fin(desk_top_tone(25 if side == 'izq' else 26, off, side))
    P = []
    # ---- cast iron side frame (outer side, x 0.5..2)
    if bench:
        P.append(box((0.6, 0, 0.8), (1.9, 1.0, 15.2), mI))           # floor runner (patin)
        P.append(box((0.35, 0, 0.5), (2.15, 0.5, 2.0), mI))          # foot pad front
        P.append(box((0.35, 0, 14.0), (2.15, 0.5, 15.5), mI))        # foot pad back
    else:
        P.append(box((0.6, 0, 0.8), (1.9, 1.0, 8.0), mI))
        P.append(box((0.35, 0, 0.5), (2.15, 0.5, 2.0), mI))
        P.append(box((0.35, 0, 6.8), (2.15, 0.5, 8.3), mI))
        P.append(box((0.7, 1.0, 6.6), (1.8, 10.0, 7.6), mI))          # rear leg
    P.append(box((0.6, 1.0, 2.5), (1.9, 2.4, 5.1), mI))              # post foot flare
    P.append(box((0.7, 2.4, 3.2), (1.8, 10.0, 4.4), mI))             # desk post
    P.append(box((0.75, 1.0, 1.0), (1.75, 7.4, 2.0), mI, rot=('x', 22.5, (1.25, 1.0, 1.5))))  # front brace
    P.append(box((0.7, 10.0, 0.8), (1.8, 11.0, 8.2), mI))            # bracket under the top
    P.append(box((0.7, 8.6, 5.0), (1.8, 10.0, 6.2), mI))             # scroll
    P.append(box((0.7, 7.8, 6.2), (1.8, 8.8, 7.4), mI))
    P.append(box((0.3, 7.2, 3.4), (0.7, 7.9, 4.2), mI))              # bolt heads
    P.append(box((0.3, 10.15, 6.6), (0.7, 10.85, 7.4), mI))
    if bench:
        P.append(box((0.7, 1.0, 11.4), (1.8, 5.6, 12.6), mI))        # bench post
        P.append(box((0.7, 5.6, 9.6), (1.8, 6.5, 15.2), mI))         # seat bracket
        P.append(box((0.7, 6.5, 14.5), (1.8, 15.4, 15.5), mI))       # back post
        P.append(box((0.7, 2.6, 12.6), (1.8, 3.6, 14.0), mI))        # scrolls under the seat
        P.append(box((0.7, 3.6, 13.4), (1.8, 5.6, 14.4), mI))
        P.append(box((0.3, 5.75, 11.8), (0.7, 6.35, 12.6), mI))
        P.append(box((0.3, 12.6, 14.7), (0.7, 13.3, 15.3), mI))
        P.append(box((1.8, 2.2, 5.6), (16, 3.0, 6.4), M_IRON2))      # foot rest bar
    else:
        P.append(box((1.8, 2.2, 6.8), (16, 3.0, 7.6), M_IRON2))
    # ---- oak
    P.append(box((0.5, 11.0, 0.5), (16, 12.0, 8.5), mTop))           # desk top
    P.append(box((0.6, 8.4, 0.6), (16, 11.0, 1.4), mW))              # front apron
    P.append(box((1.9, 8.4, 1.4), (16, 8.9, 7.2), mW))               # book shelf
    P.append(box((6.6, 12.0, 1.1), (9.4, 12.3, 1.5), M_BRASS))      # inkwell brass ring
    P.append(box((6.6, 12.0, 3.5), (9.4, 12.3, 3.9), M_BRASS))
    P.append(box((6.6, 12.0, 1.5), (7.0, 12.3, 3.5), M_BRASS))
    P.append(box((9.0, 12.0, 1.5), (9.4, 12.3, 3.5), M_BRASS))
    if bench:
        mS = fin(wood(ROBLE, seed=27, off=off, worn_pal=RAW, wear=0.6))
        P.append(box((0.5, 6.5, 9.6), (16, 7.4, 11.2), mS))          # seat slats
        P.append(box((0.5, 6.5, 11.45), (16, 7.4, 13.05), mS))
        P.append(box((0.5, 6.5, 13.3), (16, 7.4, 14.5), mS))
        P.append(box((0.5, 9.4, 14.55), (16, 11.0, 15.35), mS))      # back slats
        P.append(box((0.5, 12.4, 14.55), (16, 14.6, 15.35), mS))
    if side == 'der':
        P = mirror_parts(P)
        # the mirror moved the inkwell: put the hole/rim back over the carved-out hole of the right half
    return P


def chair_parts(seat_y=7.0, mat_w=None, raise_=0.0):
    mI = M_IRON
    mW = mat_w or fin(wood(ROBLE, seed=29, worn_pal=RAW, wear=0.6))
    P = []
    y = seat_y
    for x0 in (3.2, 11.6):
        P.append(box((x0, 0, 2.8), (x0 + 1.2, y - 0.6, 4.0), mI))            # front legs
        P.append(box((x0, 0, 12.0), (x0 + 1.2, y + 9.4, 13.2), mI))          # back legs / uprights
        P.append(box((x0 + 0.1, 2.4, 4.0), (x0 + 1.1, 3.1, 12.0), M_IRON2))  # side stretcher
        P.append(box((x0, y - 1.4, 2.8), (x0 + 1.2, y - 0.6, 12.0), mI))     # seat rail
        P.append(box((x0 - 0.2, 0, 2.6), (x0 + 1.4, 0.4, 4.2), mI))          # feet
        P.append(box((x0 - 0.2, 0, 11.8), (x0 + 1.4, 0.4, 13.4), mI))
    P.append(box((4.4, y - 1.3, 3.0), (11.6, y - 0.7, 3.8), mI))             # front rail
    P.append(box((2.8, y - 0.6, 2.4), (13.2, y + 0.4, 13.4), mW))            # seat
    P.append(box((2.8, y + 3.6, 13.25), (13.2, y + 5.4, 14.05), mW))         # back slats
    P.append(box((2.8, y + 6.4, 13.25), (13.2, y + 8.8, 14.05), mW))
    if raise_:
        shift(P, dy=raise_)
    return P


# ------------------------------------------------------------------------------------------------ tarima
def tarima_tone(seed=51):
    plank = wood(ROBLE, seed=seed, base=4, boards=(2, 7), axis=0, worn_pal=RAW, wear=0.5, knots=0.25)

    def t(ctx):
        if ctx.face == 'up':
            r = plank(ctx)
            X = int(ctx.pos[0] * 2)
            Z = int(ctx.pos[2] * 2)
            # board butt joints (staggered) + nail heads
            row = int(Z // 7)
            j0 = (row * 11 + 5) % 32
            if X == j0:
                return (ROBLE, 1)
            if (X == (j0 + 2) % 32 or X == (j0 - 3) % 32) and Z % 7 in (2, 5):
                return (IRON, 3)
            # scuffed path where teachers walked
            n = vn(X / 7.0, Z / 7.0, 0.3, 9)
            if n > 0.7 and hh(X, Z) < 0.4:
                return (RAW, 2)
            return r
        return plank(ctx)
    return t


def tarima_parts(edges=()):
    """4/16 high platform. edges: subset of ('n', 'w') -> nosing on the front (north) and/or left (west) side."""
    mT = fin(tarima_tone())
    mS = fin(wood(ROBLE, seed=53, axis=0, base=3, wear=0.3))
    mK = fin(painted(ROBLE, base=2, seed=55, grime=0.6, wear=0.1))
    P = []
    z0 = 0.8 if 'n' in edges else 0.0
    x0 = 0.8 if 'w' in edges else 0.0
    P.append(box((x0, 0, z0), (16, 3.6, 16), mS))
    P.append(box((0, 3.6, 0), (16, 4.0, 16), mT, faces=('up', 'north', 'west', 'east', 'south')))
    if 'n' in edges:
        P.append(box((x0, 2.9, 0.25), (16, 3.6, 0.8), mS))           # quarter-round under the nosing
        P.append(box((x0, 0, 0.75), (16, 1.0, 0.8), mK, faces=('north',)))  # scuffed kick strip (thin)
    if 'w' in edges:
        P.append(box((0.25, 2.9, z0), (0.8, 3.6, 16), mS))
    return P


# ------------------------------------------------------------------------------------------------ teacher desk
def teacher_desk_parts(side, base_y=4.0, with_tarima=True):
    """Teacher's desk (2 blocks): user (the teacher) sits on the SOUTH side looking north. izq = drawers pedestal."""
    off = (0, 0, 0) if side == 'izq' else (16, 0, 0)
    mW = fin(wood(ROBLE, seed=61, off=off, worn_pal=RAW, base=4))
    mP = fin(wood(ROBLE, seed=63, off=off, base=3, wear=0.25))
    mTop = fin(wood(ROBLE, seed=65, off=off, boards=(2, 9), base=4, worn_pal=RAW, wear=0.5))
    P = []
    if with_tarima:
        P += tarima_parts()
    y0 = base_y
    yt = y0 + 11.0  # underside of the top
    # top with an overhang + moulded edge
    P.append(box((0.4, yt, 0.6), (16, yt + 1.0, 15.0), mTop))
    P.append(box((0.8, yt - 0.6, 1.0), (16, yt, 14.6), mP))           # top frame (apron) under the top
    if side == 'izq':
        # pedestal with 3 drawers, opening to the south (teacher side)
        P.append(box((1.0, y0, 1.6), (8.0, yt - 0.6, 14.4), mP))
        P.append(box((0.8, y0, 1.4), (8.2, y0 + 0.8, 14.6), mW))        # plinth
        for n, (a, b) in enumerate(((y0 + 0.9, y0 + 4.3), (y0 + 4.5, y0 + 7.4), (y0 + 7.6, yt - 0.8))):
            P.append(box((1.5, a, 14.4), (7.5, b, 14.9), mW))          # drawer fronts
            P.append(box((3.6, (a + b) / 2 - 0.35, 14.9), (5.4, (a + b) / 2 + 0.35, 15.4), M_BRASS))  # pulls
        # modesty panel toward the pupils (north) with a raised field
        P.append(box((8.0, y0 + 2.0, 1.6), (16, yt - 0.6, 2.2), mP))
        P.append(box((9.0, y0 + 3.0, 1.2), (16, yt - 1.6, 1.6), mW))
    else:
        P.append(box((8.0, y0, 1.6), (15.0, yt - 0.6, 14.4), mP))       # right pedestal (cupboard)
        P.append(box((7.8, y0, 1.4), (15.2, y0 + 0.8, 14.6), mW))
        P.append(box((8.6, y0 + 1.0, 14.4), (14.4, yt - 0.8, 14.9), mW))  # cupboard door
        P.append(box((9.2, y0 + 6.0, 14.9), (9.8, y0 + 7.4, 15.3), M_BRASS))  # knob
        P.append(box((0.0, yt - 2.6, 14.0), (7.8, yt - 0.6, 14.6), mW))  # centre drawer (attendance book)
        P.append(box((3.0, yt - 1.95, 14.6), (4.8, yt - 1.25, 15.1), M_BRASS))
        P.append(box((0.0, y0 + 2.0, 1.6), (8.0, yt - 0.6, 2.2), mP))   # modesty panel
        P.append(box((0.0, y0 + 3.0, 1.2), (7.0, yt - 1.6, 1.6), mW))
        # a few exercise books and the wooden ruler on top
        mB1 = fin(painted(NAVY, base=3, seed=67, wear=0.3))
        mB2 = fin(painted(REDP, base=3, seed=68, wear=0.3))
        mPg = fin(flat(PAPER, 6))
        P.append(box((9.0, yt + 1.0, 6.0), (14.0, yt + 1.5, 12.5), mB1))
        P.append(box((9.2, yt + 1.5, 6.4), (13.8, yt + 1.8, 12.2), mPg, faces=('north', 'south', 'west', 'east')))
        P.append(box((9.4, yt + 1.8, 6.1), (14.2, yt + 2.3, 12.3), mB2))
        P.append(box((2.0, yt + 1.0, 9.0), (13.0, yt + 1.3, 9.9), fin(wood(NOGAL, seed=69, axis=0))))  # ruler
    return P


# ------------------------------------------------------------------------------------------------ chalkboard
BOARD_W, BOARD_H = 160, 64   # 5 x 2 blocks


def _swirls(seed, n, W=BOARD_W, H=BOARD_H):
    arcs = []
    for i in range(n):
        arcs.append((hh(seed, i, 1) * W, hh(seed, i, 2) * H * 1.2 + 8, 9 + hh(seed, i, 3) * 22, 1.8 + hh(seed, i, 4) * 1.6,
                     hh(seed, i, 5) * 6.28, 1.2 + hh(seed, i, 6) * 2.4))
    return arcs


def board_layers(variant):
    """Returns (residue[y][x] 0..2, chalk dict {(x,y): (strength, colour)}) for the whole 160x64 board."""
    W, H = BOARD_W, BOARD_H
    res = [[0] * W for _ in range(H)]
    sd = {'blank': 3, 'fecha': 5, 'nodebo': 7, 'cantas': 9, 'gracias': 11}[variant]
    for (cx, cy, R, wdt, a0, span) in _swirls(sd, 9):
        for y in range(H):
            for x in range(W):
                dx, dy = x - cx, (y - cy) * 1.25
                d = math.hypot(dx, dy)
                if abs(d - R) < wdt:
                    ang = math.atan2(dy, dx) - a0
                    ang = (ang + math.pi) % (2 * math.pi) - math.pi
                    if abs(ang) < span / 2:
                        core = abs(d - R) < wdt * 0.45
                        res[y][x] = max(res[y][x], 2 if core and hh(x, y, sd) < 0.5 else 1)
    # horizontal wipe bands
    for b in range(4):
        y0 = int(hh(sd, b, 9) * (H - 6))
        x0 = int(hh(sd, b, 10) * W * 0.6)
        ln = int(30 + hh(sd, b, 11) * 60)
        for y in range(y0, y0 + 5):
            for x in range(x0, min(W, x0 + ln)):
                if hh(x // 3, y, b, sd) < 0.55:
                    res[y][x] = max(res[y][x], 1)
    # chalk dust settling at the bottom of the board
    for y in range(H - 6, H):
        for x in range(W):
            pr = (y - (H - 6)) / 6.0
            if hh(x, y, sd, 3) < pr * 0.9:
                res[y][x] = max(res[y][x], 1 + (hh(x, y, 4) < pr * 0.5))
    ink = {}

    def put(pts, s=1.0, col=CHALK, rough=0.2, halo=0.3, seed=0):
        for (x, y) in pts:
            if 0 <= x < W and 0 <= y < H:
                st = s * (0.55 if hh(x, y, seed, 1) < rough else 1.0)
                ink[(x, y)] = (max(st, ink.get((x, y), (0, col))[0]), col)
        if halo:
            for (x, y) in pts:
                for (dx, dy) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    q = (x + dx, y + dy)
                    if q not in ink and 0 <= q[0] < W and 0 <= q[1] < H and hh(q[0], q[1], seed, 2) < halo:
                        ink[q] = (0.22 * s, col)

    # ghost writing of old lessons (very faint)
    ghost = {'blank': ['DICTADO', 'SUMAS'], 'fecha': ['TAREA'], 'nodebo': [], 'cantas': ['AVE MARIA'], 'gracias': []}[variant]
    for gi, g in enumerate(ghost):
        pts = draw_text(F35, g, 18 + gi * 52, 18 + gi * 17)
        put(pts, 0.14, CHALK, rough=0.4, halo=0, seed=gi)

    if variant == 'fecha':
        put(draw_text(F57, 'Lunes 21 de junio de 1984', 10, 6, italic=0.25, jitter=0.4, seed=1), 1.0, seed=1)
        title = 'Los ríos de la Argentina'
        tw = text_width(F57, title)
        put(draw_text(F57, title, (W - tw) // 2, 19, italic=0.25, jitter=0.4, seed=2), 1.0, seed=2)
        for x in range((W - tw) // 2 - 2, (W + tw) // 2 + 3):          # underline
            put([(x, 28 + (x // 23) % 2)], 0.9, seed=3, halo=0.15)
        rivers = ['1. Paraná', '2. Uruguay', '3. Paraguay', '4. Pilcomayo', '5. Bermejo', '6. Salado', '7. Colorado', '8. Negro']
        for n, rv in enumerate(rivers):
            cx = 14 + (n // 4) * 74
            cy = 34 + (n % 4) * 7 - 2
            if n >= 7:
                put(draw_text(F57, rv[:5], cx, cy, italic=0.25, seed=n + 9), 0.9, CHALK_Y, seed=n)   # unfinished...
            else:
                put(draw_text(F57, rv, cx, cy, italic=0.25, jitter=0.3, seed=n + 9), 0.95, seed=n)
        # a little river drawing in yellow chalk
        for x in range(128, 156):
            y = int(40 + 6 * math.sin(x / 4.0) + (x - 128) * 0.35)
            put([(x, y), (x, y + 1)], 0.8, CHALK_Y, seed=x)
    elif variant == 'nodebo':
        line = 'NO DEBO HABLAR EN CLASE'
        for n in range(7):
            y = 5 + n * 8 + (1 if n > 3 else 0)
            mess = n / 6.0
            x = 6 + int(hh(n, 3) * 4) - n // 3
            put(draw_text(F57, line, x, y, italic=0.18 + mess * 0.35, jitter=0.4 + mess * 1.8, seed=n * 7),
                1.0 - mess * 0.15, rough=0.18 + mess * 0.25, seed=n)
        # broken chalk scrape at the end of the last line
        for k in range(14):
            put([(139 + k, 58 + k // 5)], 0.9, seed=k + 50)
    elif variant == 'cantas':
        a, b = '¿POR QUÉ', 'NO CANTÁS?'
        for (s, y, sd2) in ((a, 10, 1), (b, 36, 2)):
            pts = draw_text(F57, s, 0, 0, sp=1, italic=0.15, jitter=0.0, seed=sd2)
            big = []
            for (x, yy) in pts:  # 2x scale, wobbly
                for dx in (0, 1):
                    for dy in (0, 1):
                        big.append((x * 2 + dx, yy * 2 + dy))
            tw = max(p[0] for p in big) + 1
            ox = (W - tw) // 2 + (3 if sd2 == 2 else -6)
            put([(x + ox + int(1.2 * math.sin((yy + y) / 3.0 + sd2)), yy + y) for (x, yy) in big], 1.0, rough=0.3, seed=sd2)
        # little crooked music notes drawn by a child
        for (nx, ny) in ((8, 50), (142, 8), (150, 46), (20, 6)):
            put(draw_text(F57, '♪', nx, ny, seed=nx), 0.75, CHALK_P, seed=nx)
    elif variant == 'gracias':
        s = 'GRACIAS'
        pts = draw_text(F57, s, 0, 0, sp=2, italic=0.12, seed=4)
        big = [(x * 2 + dx, y * 2 + dy) for (x, y) in pts for dx in (0, 1) for dy in (0, 1)]
        tw = max(p[0] for p in big) + 1
        put([(x + (W - tw) // 2, y + 8) for (x, y) in big], 1.0, rough=0.15, seed=4)
        names = ['Paloma', 'Mecha', 'Rocío', 'Chela', 'Ofelia', 'Ana Sofía', 'Lola']
        for n, nm in enumerate(names):
            x = 6 + (n % 4) * 39 + (n // 4) * 18
            y = 36 + (n // 4) * 11
            put(draw_text(F57, nm, x, y, italic=0.3, jitter=0.6, seed=n + 20), 0.9, (CHALK, CHALK_P, CHALK_Y)[n % 3], seed=n)
        put(draw_text(F57, '♥', 146, 50, seed=3), 0.9, CHALK_P, seed=3)
    return res, ink


_BOARD = {}


def board_tone(variant, col, row):
    if variant not in _BOARD:
        _BOARD[variant] = board_layers(variant)
    res, ink = _BOARD[variant]
    frame = wood(NOGAL, seed=71, base=3)

    def t(ctx):
        if ctx.face != 'north':
            fp, fk = frame(ctx)
            return T(fp, fk)
        X = col * 32 + ctx.i
        Y = row * 32 + ctx.j
        k = 3
        if hh(Y, X // 9, 5) < 0.12:
            k += 1                      # long faint wipe streaks
        if hh(X, Y, 6) < 0.035:
            k -= 1                      # pits in the slate paint
        k += res[Y][X]
        o = occlusion(ctx)
        if o > 0.78:
            k -= 2
        elif o > 0.4:
            k -= 1
        c = T(SLATE, k)
        if (X, Y) in ink:
            s, col_ = ink[(X, Y)]
            c = mix(c, col_, min(0.95, s * 0.9))
        return c
    return t


def chalkboard_parts(variant, col, row, cols=5):
    """col 0..cols-1 from the viewer's left, row 0 = top. Authoring: viewer at north looking south."""
    mF = fin(wood(NOGAL, seed=73, axis=None, base=4, wear=0.45), dust=0.6)
    mFace = board_tone(variant, col, row)
    left = col == 0
    right = col == cols - 1
    top = row == 0
    bottom = row == 1
    P = [box((0, 0, 15.0), (16, 16, 16), mFace, faces=('north', 'west', 'east', 'up', 'down'))]
    # frame - viewer's left is +x in authoring space
    y_lo = 1.8 if bottom else 0.0
    y_hi = 14.2 if top else 16.0
    if left:
        P.append(box((14.2, y_lo, 14.2), (16, y_hi, 15.0), mF))
    if right:
        P.append(box((0, y_lo, 14.2), (1.8, y_hi, 15.0), mF))
    if top:
        P.append(box((0, 14.2, 14.2), (16, 16, 15.0), mF))
        P.append(box((0, 15.3, 13.7), (16, 16, 14.2), mF))
    if bottom:
        P.append(box((0, 0, 14.2), (16, 1.8, 15.0), mF))
        mTray = fin(wood(NOGAL, seed=75, axis=0, base=4, wear=0.5), dust=2.2)
        P.append(box((0, 0.0, 11.6), (16, 0.7, 14.2), mTray))
        P.append(box((0, 0.7, 11.6), (16, 1.3, 12.1), mTray))
        if col in (1, 3) and variant != 'gracias':
            mC = fin(flat([CHALK], 0), ao=0, dust=0)
            mCY = fin(flat([CHALK_Y], 0), ao=0, dust=0)
            P.append(box((3, 0.7, 12.6), (6.5, 1.3, 13.2), mC))                    # chalk sticks
            P.append(box((7.5, 0.7, 12.8), (9.4, 1.3, 13.4), mCY))
            if col == 1:
                P.append(box((10.5, 0.7, 12.3), (14.5, 1.6, 13.9), fin(wood(NOGAL, seed=77, base=5))))  # eraser
                P.append(box((10.5, 1.6, 12.3), (14.5, 2.3, 13.9), fin(cloth(BLANKET, base=4, seed=78, folds=0))))
    return P


# ------------------------------------------------------------------------------------------------ crucifix (small)
def crucifix_small_parts():
    mW = fin(wood(NOGAL, seed=81, base=4, wear=0.3), dust=0.4)
    mC = fin(painted(SKIN_C, base=5, seed=82, wear=0.0, grime=0), dust=0.3)
    mL = fin(painted(LINEN, base=6, seed=83, wear=0.0, grime=0), dust=0.2)
    mB = fin(brass(seed=84, sheen=False))
    P = [
        box((7.0, 2.0, 15.0), (9.0, 15.0, 16), mW),                  # upright
        box((3.6, 10.2, 15.1), (7.0, 12.0, 16), mW),                 # arms (split: no coplanar overlap)
        box((9.0, 10.2, 15.1), (12.4, 12.0, 16), mW),
        box((7.3, 13.4, 14.7), (8.7, 14.4, 15.0), mB),               # INRI plaque
        box((7.45, 11.2, 14.3), (8.55, 12.4, 15.0), mC),             # head
        box((7.35, 7.9, 14.4), (8.65, 11.2, 15.0), mC),              # torso
        box((4.2, 10.7, 14.6), (7.4, 11.4, 15.0), mC),               # arms
        box((8.6, 10.7, 14.6), (11.8, 11.4, 15.0), mC),
        box((7.25, 7.2, 14.3), (8.75, 8.3, 15.0), mL),               # loincloth
        box((7.55, 3.6, 14.5), (8.45, 7.2, 15.0), mC),               # legs
    ]
    # dried olive sprig tucked behind the cross (Domingo de Ramos)
    leaf = {'#': hx('#5b5a33'), '+': hx('#7a7444'), '=': hx('#3c3a22')}

    def sprig(ctx):
        rows = ['......+#.', '....+##=.', '...#+#=..', '.+##=#...', '#+=.#=...', '.=.#=....', '..#=.....', '.#=......', '#=.......']
        j = ctx.j * 9 // ctx.h
        i = ctx.i * 9 // ctx.w
        ch = rows[j][i]
        return leaf.get(ch)
    P.append(plane((8.6, 11.5, 15.6), (13.0, 16.0, 15.6), sprig))
    return P


# ------------------------------------------------------------------------------------------------ map of Argentina
ARG = [(-66.2, -21.8), (-64.3, -22.4), (-62.6, -22.3), (-61.0, -23.7), (-58.6, -25.2), (-57.6, -25.3), (-55.9, -27.3), (-54.6, -25.6),
       (-53.6, -26.2), (-53.9, -27.1), (-55.6, -28.0), (-57.6, -30.2), (-58.2, -32.4), (-58.4, -33.9), (-57.2, -35.2),
       (-56.7, -36.3), (-57.5, -38.1), (-60.0, -38.9), (-62.2, -38.8), (-62.3, -40.6), (-65.0, -40.8), (-64.3, -42.2),
       (-63.6, -42.6), (-65.0, -43.3), (-65.7, -45.0), (-67.6, -46.0), (-65.9, -47.8), (-67.7, -49.3), (-69.2, -51.6),
       (-68.4, -52.4), (-71.0, -52.0), (-72.3, -51.3), (-73.3, -49.5), (-72.4, -47.6), (-71.7, -45.0), (-71.6, -43.0),
       (-71.9, -40.0), (-71.0, -37.5), (-70.4, -35.0), (-69.9, -33.0), (-70.3, -30.0), (-69.5, -28.0), (-68.4, -26.5),
       (-67.2, -24.0), (-66.6, -22.7)]
TDF = [(-68.6, -52.6), (-68.6, -54.9), (-66.5, -55.0), (-65.2, -54.7), (-66.8, -53.6), (-68.0, -53.0)]
MALV = [(-61.3, -51.3), (-59.9, -51.2), (-57.8, -51.5), (-58.4, -52.2), (-60.5, -52.1)]
RIVERS = [[(-54.6, -25.7), (-56.7, -27.4), (-58.6, -27.3), (-59.6, -29.5), (-60.6, -31.6), (-60.7, -32.9), (-59.0, -33.8), (-58.4, -34.0)],
          [(-53.8, -27.0), (-55.8, -28.6), (-57.6, -30.4), (-58.1, -32.5), (-58.4, -33.9)],
          [(-70.2, -36.4), (-67.0, -37.6), (-64.0, -38.9), (-62.1, -39.8)],
          [(-68.5, -38.9), (-66.3, -39.3), (-64.5, -40.3), (-62.8, -41.0)],
          [(-65.3, -24.7), (-63.5, -27.5), (-61.8, -29.8), (-60.7, -31.6)],
          [(-64.6, -22.6), (-62.5, -24.0), (-60.0, -26.0), (-58.6, -27.3)]]


def _pip(x, y, poly):
    inside = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y):
            xi = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if x < xi:
                inside = not inside
    return inside


def map_image(W=30, H=52):
    """Pixel map of Argentina (with Malvinas) on aged paper: ocean, Andes, pampas, Patagonia, rivers."""
    def proj(lon, lat):
        return ((lon + 74.5) / 21.5 * W, (-21.0 - lat) / 34.8 * (H - 2) + 1)
    poly = [proj(*p) for p in ARG]
    tdf = [proj(*p) for p in TDF]
    mal = [proj(*p) for p in MALV]
    img = {}
    for y in range(H):
        for x in range(W):
            px, py = x + 0.5, y + 0.5
            land = _pip(px, py, poly) or _pip(px, py, tdf)
            if land:
                lon = px / W * 21.5 - 74.5
                lat = -21.0 - (py - 1) / (H - 2) * 34.8
                # crude relief: Andes west, Patagonian plateau south, pampa/chaco green
                west = lon < -68.8 + (0.0 if lat > -38 else 1.2) and lat > -50
                if west:
                    c = hx('#9a6b43') if hh(x, y) < 0.7 else hx('#7d5534')
                elif lat < -39.5:
                    c = hx('#c8ad6a') if hh(x, y, 2) < 0.8 else hx('#b39556')
                elif lat > -27.5 and lon > -63.5:
                    c = hx('#6e9050')
                else:
                    c = hx('#8eaa5e') if hh(x, y, 3) < 0.85 else hx('#7d9a52')
                img[(x, y)] = c
            elif _pip(px, py, mal):
                img[(x, y)] = hx('#8eaa5e')
    # coast line darker
    out = {}
    for (x, y), c in img.items():
        edge = any((x + dx, y + dy) not in img for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        out[(x, y)] = mix(c, hx('#3f3a2a'), 0.45) if edge else c
    for rv in RIVERS:
        for a, b in zip(rv, rv[1:]):
            (x1, y1), (x2, y2) = proj(*a), proj(*b)
            n = int(max(abs(x2 - x1), abs(y2 - y1)) * 2) + 1
            for i in range(n + 1):
                x = int(x1 + (x2 - x1) * i / n)
                y = int(y1 + (y2 - y1) * i / n)
                if (x, y) in img:
                    out[(x, y)] = hx('#3f6f9a')
    return out


def map_tone():
    m = map_image()
    paper = cloth(PAPER, base=6, seed=91, folds=0, weave=False, stains=0.35)

    def t(ctx):
        if ctx.face not in ('north',):
            return paper(ctx)
        x, y = ctx.i - 1, ctx.j - 1
        base = paper(ctx)
        if ctx.edge() == 0:
            return mix(base, hx('#5a4a35'), 0.45)
        sea = mix(base, hx('#8fb6c9'), 0.55)
        if (x, y) in m:
            c = mix(m[(x, y)], base, 0.18)
        else:
            c = sea
            if (x + y) % 7 == 0 and hh(x, y) < 0.3:
                c = mix(sea, hx('#6f98ad'), 0.4)
        # compass rose / scale bar, bottom right
        if 21 <= x <= 25 and 40 <= y <= 44 and (x == 23 or y == 42):
            c = hx('#7a2a22')
        if 3 <= x <= 12 and y == 49:
            c = hx('#2a2622') if (x // 2) % 2 else hx('#d8ccb0')
        # tear and fold
        if y == 26 and hh(x, 5) < 0.6:
            c = mix(c, hx('#5a4a35'), 0.3)
        return c
    return t


def map_parts():
    mR = fin(wood(NOGAL, seed=93, axis=0, base=4), dust=0.7)
    mP = fin(map_tone(), ao=0, dust=0)
    mCord = fin(flat(PAPER, 2), ao=0, dust=0)
    P = [
        box((-0.6, 14.6, 14.9), (16.6, 15.6, 15.9), mR),             # top rod
        box((-0.6, -12.6, 14.9), (16.6, -11.6, 15.9), mR),           # bottom rod
        box((0.5, -12.0, 15.25), (15.5, 15.0, 15.35), mP, faces=('north', 'south')),
        box((0.2, 15.0, 15.2), (0.7, 21.0, 15.6), mCord, rot=('z', -45, (0.45, 15.0, 15.4))),
        box((15.3, 15.0, 15.2), (15.8, 21.0, 15.6), mCord, rot=('z', 45, (15.55, 15.0, 15.4))),
        box((7.6, 19.0, 15.2), (8.4, 19.8, 16.0), M_IRON),           # nail
    ]
    return P


# ============================================================================================ register: classroom
F('pupitre_doble_izq', 'Pupitre doble (izquierda)', 'Double school desk (left)', pupitre_parts('izq'), sound='wood')
F('pupitre_doble_der', 'Pupitre doble (derecha)', 'Double school desk (right)', pupitre_parts('der'), sound='wood')
F('pupitre_mesa_izq', 'Mesa de pupitre (izquierda)', 'School desk without bench (left)', pupitre_parts('izq', bench=False))
F('pupitre_mesa_der', 'Mesa de pupitre (derecha)', 'School desk without bench (right)', pupitre_parts('der', bench=False))
F('silla_escolar', 'Silla escolar', 'School chair', chair_parts())
F('tarima', 'Tarima', 'Teacher platform', tarima_parts(), collision='auto')
F('tarima_borde', 'Tarima (borde)', 'Teacher platform (edge)', tarima_parts(('n',)))
F('tarima_esquina', 'Tarima (esquina)', 'Teacher platform (corner)', tarima_parts(('n', 'w')))
F('escritorio_maestra_izq', 'Escritorio de la maestra sobre tarima (izquierda)', 'Teacher desk on platform (left)',
  teacher_desk_parts('izq'))
F('escritorio_maestra_der', 'Escritorio de la maestra sobre tarima (derecha)', 'Teacher desk on platform (right)',
  teacher_desk_parts('der'))
F('silla_maestra', 'Silla de la maestra sobre tarima', 'Teacher chair on platform',
  tarima_parts() + chair_parts(raise_=4.0, mat_w=fin(wood(NOGAL, seed=95, worn_pal=RAW, wear=0.5))))
for _row, _rn in ((0, 'arriba'), (1, 'abajo')):
    for _col, _cn in ((0, 'izq'), (1, 'centro'), (4, 'der')):
        F(f'pizarron_{_rn}_{_cn}', f'Pizarrón ({_rn}, {_cn})', f'Chalkboard ({_rn}, {_cn})',
          chalkboard_parts('blank', _col, _row), env=('wall',), sound='stone', collision='auto')
for _var, _es in (('fecha', 'Lunes 21 de junio'), ('nodebo', 'No debo hablar en clase'), ('cantas', '¿Por qué no cantás?'),
                  ('gracias', 'Gracias')):
    for _row in range(2):
        for _col in range(5):
            F(f'pizarron_{_var}_{_col + 1}_{_row + 1}', f'Pizarrón "{_es}" ({_col + 1}/5, fila {_row + 1})',
              f'Chalkboard "{_es}" ({_col + 1}/5, row {_row + 1})', chalkboard_parts(_var, _col, _row), env=('wall',),
              sound='stone')
F('crucifijo_chico', 'Crucifijo de pared', 'Small wall crucifix', crucifix_small_parts(), env=('wall',), collision='none')
F('mapa_argentina', 'Mapa escolar de la Argentina', 'School map of Argentina', map_parts(), env=('wall',), collision='none',
  sound='wool')
