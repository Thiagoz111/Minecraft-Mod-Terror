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
BLANKET = pal('#2f2e33', '#3c3b40', '#4a494e', '#59585c', '#69676b', '#79777a', '#8a888a', '#9c9a9b')
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


def brass(p=BRASS, base=4, seed=0, tarnish=0.35, sheen=True, off=(0, 0, 0)):
    """Old brass / gilt: dark body, narrow polished highlight, tarnished patches, darker rims."""
    def t(ctx):
        P = tp(ctx, off)
        k = base
        if sheen:
            u = ctx.s if (ctx.face in ('up', 'down') or ctx.w >= ctx.h) else ctx.t
            if ctx.face in ('north', 'south', 'west', 'east') and ctx.h > ctx.w:
                u = ctx.s
            c = abs(u * 2 - 1)
            k += 2 if c < 0.16 else (1 if c < 0.42 else (-1 if c > 0.86 else 0))
        n = vn(P[0] / 3.5, P[1] / 3.5, P[2] / 3.5, seed + 80)
        if n > 1 - tarnish * 0.55:
            k -= 1
            if n > 1 - tarnish * 0.2 and ctx.face != 'up':
                return (VERDI, 1)
        if ctx.edge() == 0 and ctx.w > 2 and ctx.h > 2:
            k -= 1
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


def marble(p=MARBLE, base=6, seed=0, off=(0, 0, 0), veins=1.0, period=13.0):
    """Polished marble: soft clouds + thin meandering veins (domain-warped), no speckle."""
    def t(ctx):
        P = tp(ctx, off)
        w1 = vn(P[0] / 10.0, P[1] / 10.0, P[2] / 10.0, seed) * 9.0 + vn(P[0] / 4.0, P[1] / 4.0, P[2] / 4.0, seed + 1) * 2.0
        u = (P[0] * 0.45 + P[1] * 0.72 + P[2] * 0.36 + w1) / period
        d = abs(u - round(u)) * period
        k = base
        if d < 0.55 * veins:
            k -= 2
        elif d < 1.3 * veins:
            k -= 1
        c = vn(P[0] / 7.0, P[1] / 7.0, P[2] / 7.0, seed + 3)
        if c > 0.68:
            k += 1
        elif c < 0.24:
            k -= 1
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


def panels(inner, frame=None, rects=((3, 3, -3, -3),), faces=('north',), bevel=1, groove=True, carve=None):
    """Frame-and-panel painting. rects: (i0, j0, i1, j1) face-pixel boxes (negative = from the far edge).
    The panel gets a dark groove, a 1px bevel (lighter top/left, darker bottom/right) and may hold a carved motif:
    carve(ctx, di, dj, w, h) -> step delta or 0 (di/dj relative to the panel)."""
    frame = frame or inner

    def t(ctx):
        if ctx.face in faces:
            for (a, b, c, d) in rects:
                i0 = a if a >= 0 else ctx.w + a
                j0 = b if b >= 0 else ctx.h + b
                i1 = c if c > 0 else ctx.w + c
                j1 = d if d > 0 else ctx.h + d
                if i0 <= ctx.i < i1 and j0 <= ctx.j < j1:
                    di, dj = ctx.i - i0, ctx.j - j0
                    ei, ej = i1 - 1 - ctx.i, j1 - 1 - ctx.j
                    m = min(di, dj, ei, ej)
                    pl, k = inner(ctx)
                    if groove and m == 0:
                        return (pl, k - 2)
                    if m <= bevel:
                        k += 1 if (dj == m or di == m) else -1
                    elif carve:
                        k += carve(ctx, di, dj, i1 - i0, j1 - j0)
                    return (pl, k)
        return frame(ctx)
    return t


def outline(tone, amount=1, faces=None):
    """Darken the border texels of every face (crisp 1px definition for small parts)."""
    def t(ctx):
        r = tone(ctx)
        if r is None or type(r[0]) is not list:
            return r
        if ctx.edge() == 0 and (faces is None or ctx.face in faces):
            return (r[0], r[1] - amount)
        return r
    return t


def cross_carve(ctx, di, dj, w, h):
    """A Latin cross gouged into the centre of a panel."""
    cx = w // 2
    top = h // 5
    bar = top + (h - 2 * top) // 3
    if (abs(di - cx + 0.5) < 1 and top <= dj < h - top) or (abs(dj - bar) < 1 and abs(di - cx + 0.5) < w * 0.28):
        return -2
    if (abs(di - cx + 0.5) < 2 and top - 1 <= dj < h - top + 1) or (abs(dj - bar) < 2 and abs(di - cx + 0.5) < w * 0.28 + 1):
        return 1
    return 0


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
M_BRASS = fin(brass(seed=5, base=4), dust=0.6)
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
        # inkwell hole: x 7.5..8.5, z 2..3 units (texels 15..16, 4..5)
        if 15 <= X <= 16 and 4 <= Z <= 5:
            return (NAVY, 4) if (X, Z) == (15, 4) else (IRON, 0)
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
    mInk = fin(brass(seed=7, base=3, sheen=False, tarnish=0.6), dust=0.5)
    P.append(box((7.0, 12.0, 1.5), (9.0, 12.2, 2.0), mInk))         # inkwell pewter/brass ring
    P.append(box((7.0, 12.0, 3.0), (9.0, 12.2, 3.5), mInk))
    P.append(box((7.0, 12.0, 2.0), (7.5, 12.2, 3.0), mInk))
    P.append(box((8.5, 12.0, 2.0), (9.0, 12.2, 3.0), mInk))
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
def teacher_desk_parts(side, base_y=4.0, with_tarima=True, pal_=ROBLE, seed=61):
    """Teacher's desk (2 blocks): the teacher sits on the SOUTH side looking north. izq = drawer pedestal."""
    off = (0, 0, 0) if side == 'izq' else (16, 0, 0)
    wd = lambda sd, **kw: wood(pal_, seed=seed + sd, off=off, worn_pal=RAW, **kw)
    mP = fin(panels(wd(2, base=3, axis=1), wd(3, base=4), rects=((3, 3, -3, -3),), faces=('north', 'south', 'west', 'east')))
    mDr = fin(panels(wd(4, base=4, axis=0), rects=((1, 1, -1, -1),), faces=('south',), bevel=0))
    mDoor = fin(panels(wd(5, base=4, axis=1), wd(6, base=4, axis=1), rects=((3, 3, -3, -3),), faces=('south',)))
    mMod = fin(panels(wd(7, base=4, axis=1), wd(8, base=3, axis=0), rects=((3, 3, 13, -3), (16, 3, -3, -3)), faces=('north',)))
    mW = fin(wd(9, base=4))
    mTop = fin(wd(10, boards=(2, 9), base=4, wear=0.5))
    mLeg = fin(outline(wd(11, base=3, axis=1)))
    P = []
    if with_tarima:
        P += tarima_parts()
    y0 = base_y
    yt = y0 + 11.0  # underside of the top
    P.append(box((0.4, yt, 0.6), (16, yt + 1.0, 15.0), mTop))
    P.append(box((0.4, yt - 0.35, 0.3), (16, yt + 0.35, 0.6), mW))       # moulded front edge
    P.append(box((0.8, yt - 1.2, 1.0), (16, yt, 14.6), mW))              # apron under the top
    if side == 'izq':
        P.append(box((1.0, y0 + 0.8, 1.6), (8.0, yt - 1.2, 14.4), mP))   # pedestal carcass (panelled sides)
        P.append(box((0.7, y0, 1.3), (8.3, y0 + 0.8, 14.7), mW))         # plinth
        for n, (a, b) in enumerate(((y0 + 1.0, y0 + 4.2), (y0 + 4.4, y0 + 7.0), (y0 + 7.2, yt - 1.4))):
            P.append(box((1.5, a, 14.4), (7.5, b, 14.9), mDr))           # drawer fronts
            P.append(box((3.7, (a + b) / 2 - 0.3, 14.9), (5.3, (a + b) / 2 + 0.3, 15.3), M_BRASS))   # bail pulls
            P.append(box((4.2, (a + b) / 2 + 0.3, 14.9), (4.8, (a + b) / 2 + 0.9, 15.0), M_BRASS))
        P.append(box((8.0, y0 + 1.6, 1.6), (16, yt - 1.2, 2.2), mMod))      # modesty panel toward the pupils
        P.append(box((8.0, y0 + 1.0, 1.4), (16, y0 + 1.6, 2.4), mW))
    else:
        P.append(box((8.0, y0 + 0.8, 1.6), (15.0, yt - 1.2, 14.4), mP))   # right pedestal (cupboard)
        P.append(box((7.7, y0, 1.3), (15.3, y0 + 0.8, 14.7), mW))
        P.append(box((8.5, y0 + 1.0, 14.4), (14.5, yt - 1.6, 14.9), mDoor))   # cupboard door
        P.append(box((9.1, y0 + 5.6, 14.9), (9.7, y0 + 6.8, 15.3), M_BRASS))   # knob
        P.append(box((9.15, y0 + 4.6, 14.9), (9.65, y0 + 5.2, 14.95), fin(flat(IRON, 0))))  # keyhole
        P.append(box((0.0, yt - 3.0, 14.0), (7.7, yt - 1.2, 14.6), mDr))    # centre drawer (attendance book)
        P.append(box((3.0, yt - 2.4, 14.6), (4.8, yt - 1.8, 15.0), M_BRASS))
        P.append(box((0.0, y0 + 1.6, 1.6), (8.0, yt - 1.2, 2.2), mMod))
        P.append(box((0.0, y0 + 1.0, 1.4), (8.0, y0 + 1.6, 2.4), mW))
        # exercise books and a ruler on top
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
    sy = (H - 2) / 34.8
    sx = sy * 0.83

    def proj(lon, lat):
        return ((lon + 76.2) * sx, (-21.0 - lat) * sy + 1)
    poly = [proj(*p) for p in ARG]
    tdf = [proj(*p) for p in TDF]
    mal = [proj(*p) for p in MALV]
    img = {}
    for y in range(H):
        for x in range(W):
            px, py = x + 0.5, y + 0.5
            land = _pip(px, py, poly) or _pip(px, py, tdf)
            if land:
                lon = px / sx - 76.2
                lat = -21.0 - (py - 1) / sy
                # crude relief: Andes west, Patagonian plateau south, pampa/chaco green
                west = lon < (-68.6 if lat > -33 else (-69.6 if lat > -40 else -71.0))
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
            if x % 8 == 3 or y % 9 == 4:
                c = mix(sea, hx('#6f98ad'), 0.35)   # graticule
        if 0 <= y <= 3 and 1 <= x <= 28:
            c = hx('#7a2a22') if y in (0, 3) else (hx('#e9dcc0') if (x % 3 and y in (1, 2) and 4 <= x <= 25) else hx('#7a2a22'))
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
F('mapa_argentina', 'Mapa escolar de la Argentina', 'School map of Argentina', map_parts(), env=('wall',), collision='none',
  sound='wool')


# ============================================================================================ CHAPEL
def flame_tone(ctx):
    """Candle flame (cutout): teardrop with white-yellow core, orange rim, blue base."""
    w, h = ctx.w, ctx.h
    x = (ctx.i + 0.5) / w * 2 - 1
    y = (ctx.j + 0.5) / h            # 0 top .. 1 bottom
    width = 0.95 * math.sin(min(1.0, y * 1.15) * math.pi * 0.62) * (1.0 if y < 0.85 else (1 - (y - 0.85) * 4))
    if abs(x) > width or y < 0.04:
        return None
    if y > 0.86:
        return hx('#4d63c8') if abs(x) < width * 0.35 else T(FLAME, 1)
    c = abs(x) / max(0.01, width)
    k = 6 - int(c * 2.6) - (1 if y < 0.3 else 0) - (1 if y < 0.15 else 0)
    if c < 0.35 and 0.55 < y < 0.8:
        k = 5   # dark-ish zone above the wick
    return T(FLAME, k)


def flame_parts(cx, cz, y0, h=2.6, w=1.6):
    return [plane((cx - w / 2, y0, cz), (cx + w / 2, y0 + h, cz), flame_tone, shade=False),
            plane((cx, y0, cz - w / 2), (cx, y0 + h, cz + w / 2), flame_tone, shade=False)]


def candle_tone(seed=0, burnt=0.0):
    """Wax: smooth creamy body, vertical drips, darker melted rim at the top."""
    def t(ctx):
        P = tp(ctx)
        k = 5
        if ctx.face == 'up':
            d = max(abs(ctx.s - 0.5), abs(ctx.t - 0.5))
            return (WAX, 3 if d < 0.2 else 4)
        col = ctx.i
        dl = int(hh(col, seed, 3) * 8) if hh(col, seed) < 0.45 else 0
        if ctx.j < dl:
            k = 6 + (ctx.j == dl - 1)
        if ctx.j == 0:
            k = 4
        if ctx.i == 0 or ctx.i == ctx.w - 1:
            k -= 1
        if burnt and hh(P[0], P[1], P[2], seed) < burnt * 0.2:
            k -= 1
        return (WAX, k)
    return t


def candle(cx, cz, y0, y1, r=0.8, lit=True, seed=0):
    P = [box((cx - r, y0, cz - r), (cx + r, y1, cz + r), fin(candle_tone(seed), ao=0.5, dust=0)),
         box((cx - 0.12, y1, cz - 0.12), (cx + 0.12, y1 + 0.7, cz + 0.12), fin(flat(IRON, 0), ao=0, dust=0))]
    if lit:
        P += flame_parts(cx, cz, y1 + 0.2, h=2.4 * (r / 0.8) ** 0.4, w=1.4 * (r / 0.8) ** 0.4)
    return P


# ------------------------------------------------------------------------------------------------ corpus painting
def corpus_tone(kind, small=False):
    """Painted plaster/wood corpus: ivory skin with ochre shadows, ribs, wounds, dark hair & beard."""
    skin = SKIN_C if small else SKIN

    def t(ctx):
        i, j, w, h = ctx.i, ctx.j, ctx.w, ctx.h
        f = ctx.face
        if kind == 'head':
            if f == 'up':
                return (HAIR, 3 + (hh(i, j) > 0.6))
            if f == 'south':
                return (HAIR, 2 + (j % 3 == 0))
            if f in ('west', 'east'):
                if i < w * 0.6 or j > h * 0.6:
                    return (HAIR, 3 + (hh(i, j, 1) > 0.6))
                return (skin, 4)
            # front face
            if small:
                return (HAIR, 3) if j == 0 else (skin, 4)
            if j < 1 or i == 0 or i == w - 1:
                return (HAIR, 3)
            if j >= h - 2 and 0 < i < w - 1:
                return (HAIR, 2 if j == h - 1 else 3)           # beard
            if j == 2 and i in (1, w - 2):
                return (HAIR, 2)                                 # closed eyes (lid lines)
            if j == 2:
                return (skin, 3)
            if j == 1 and i in (2,):
                return (REDP, 4)                                 # blood from the thorns
            return (skin, 5 if i in (2, 3) else 4)
        if kind == 'torso':
            if f == 'north' and not small:
                k = 5
                if j in (3, 5, 7) and 0 < i < w - 1:
                    k = 4                                        # ribs
                if i in (0, w - 1):
                    k = 3
                if i == w // 2 and j > 8:
                    k = 4                                        # abdomen line
                if j in (6, 7) and i == w - 2:
                    return (REDP, 4 if j == 6 else 3)            # side wound
                return (skin, k)
            return (skin, 3 if f in ('west', 'east', 'down') else 4)
        if kind == 'arm':
            if f == 'down':
                return (skin, 3)
            if (i < 2 or i >= w - 2) and f in ('north', 'up'):
                if not small and (i in (0, w - 1)):
                    return (skin, 3)
                if not small and i in (1, w - 2) and f == 'north':
                    return (REDP, 3)                             # nail wound in the palm
            return (skin, 4 if f != 'up' else 5)
        if kind == 'legs':
            if f == 'north' and i == w // 2:
                return (skin, 3)                                 # gap between the legs
            if f == 'north' and not small and j == h - 2 and i in (1, w - 2):
                return (REDP, 3)
            return (skin, 4 if f in ('north', 'up') else 3)
        if kind == 'cloth':
            k = 6 + (1 if (i // 2) % 3 == 0 else 0) - (1 if (i // 2) % 3 == 2 else 0)
            if j == h - 1:
                k -= 1
            return (LINEN, k)
        if kind == 'thorns':
            if (i + j * 2) % 3 == 0 or hh(i, j, 7) < 0.25:
                return (HAIR, 3 + (hh(i, j) > 0.5)) if hh(i, j, 2) > 0.2 else None
            return None
        return (skin, 4)
    return t


def crucifix_small_parts():
    mW = fin(outline(wood(NOGAL, seed=81, base=4, wear=0.3)), dust=0.4)
    mB = fin(brass(seed=84, sheen=False, base=4))
    ct = lambda k: fin(corpus_tone(k, small=True), dust=0.2, ao=0.6)
    P = [
        box((7.0, 2.0, 15.0), (9.0, 15.0, 16), mW),                  # upright
        box((3.6, 10.2, 15.1), (7.0, 12.0, 16), mW),                 # arms (split: no coplanar overlap)
        box((9.0, 10.2, 15.1), (12.4, 12.0, 16), mW),
        box((7.3, 13.4, 14.7), (8.7, 14.4, 15.0), mB),               # INRI plaque
        box((7.45, 11.2, 14.3), (8.55, 12.4, 15.0), ct('head')),
        box((7.35, 7.9, 14.4), (8.65, 11.2, 15.0), ct('torso')),
        box((4.2, 10.7, 14.6), (7.35, 11.4, 15.0), ct('arm')),
        box((8.65, 10.7, 14.6), (11.8, 11.4, 15.0), ct('arm')),
        box((7.25, 7.2, 14.3), (8.75, 8.3, 15.0), ct('cloth')),
        box((7.55, 3.6, 14.5), (8.45, 7.2, 15.0), ct('legs')),
    ]
    # dried olive sprig tucked behind the cross (Domingo de Ramos)
    leaf = {'#': hx('#6e6a3a'), '+': hx('#8f8a52'), '=': hx('#48452a'), 's': hx('#5a4630')}

    def sprig(ctx):
        rows = ['.....+#..', '...+#=.+.', '..#+s=+#.', '.+#.s.=..', '#+=.s+#=.', '.=.s.=...', '..s+#....', '.s=......', 's........']
        ch = rows[ctx.j * 9 // ctx.h][ctx.i * 9 // ctx.w]
        return leaf.get(ch)
    P.append(plane((8.6, 11.5, 15.6), (13.0, 16.0, 15.6), sprig))
    return P


def crucifix_big_parts():
    """Chapel crucifix: 2 blocks tall (place it 1 block above the floor), gilded finials, painted corpus."""
    mW = fin(outline(wood(NOGAL, seed=101, base=3, wear=0.25)), dust=0.5)
    mG = fin(brass(GOLD, seed=102, base=5, tarnish=0.2), dust=0.4)
    ct = lambda k: fin(corpus_tone(k), dust=0.35, ao=0.7)

    def inri(ctx):
        if ctx.face != 'north':
            return (GOLD, 4)
        pts = set(draw_text(F35, 'INRI', 1, 1))
        return (PAPER, 1) if (ctx.i, ctx.j) in pts else (PAPER, 6 - (ctx.edge() == 0) * 2)
    P = [
        box((6.6, 0.0, 14.4), (9.4, 30.4, 16.0), mW),                # upright
        box((-2.2, 21.2, 14.6), (6.6, 24.0, 16.0), mW),              # crossbar halves
        box((9.4, 21.2, 14.6), (18.2, 24.0, 16.0), mW),
        box((6.2, 30.4, 14.2), (9.8, 32.0, 16.0), mG),               # finials
        box((-3.4, 20.8, 14.2), (-2.2, 24.4, 16.0), mG),
        box((18.2, 20.8, 14.2), (19.4, 24.4, 16.0), mG),
        box((6.0, 0.0, 14.2), (10.0, 1.2, 16.0), mG),
        box((5.0, 26.2, 14.0), (11.0, 29.4, 14.4), fin(inri, dust=0.3)),   # INRI
        box((6.6, 1.2, 12.4), (9.4, 1.8, 14.4), mW),                 # suppedaneum
        box((7.0, 22.6, 12.4), (9.0, 25.4, 14.2), ct('head'), rot=('z', 22.5, (8.0, 22.6, 13.3))),
        box((6.6, 24.0, 12.1), (9.4, 24.8, 14.5), ct('thorns'), faces=('north', 'south', 'west', 'east'),
            rot=('z', 22.5, (8.0, 22.6, 13.3))),
        box((7.5, 21.6, 12.9), (8.5, 22.8, 13.9), ct('torso')),      # neck
        box((6.7, 15.6, 12.6), (9.3, 21.8, 14.4), ct('torso')),      # chest
        box((6.95, 13.8, 12.8), (9.05, 15.6, 14.3), ct('torso')),    # belly
        box((9.0, 20.7, 13.0), (17.0, 21.9, 14.2), ct('arm'), rot=('z', 22.5, (9.0, 21.3, 13.6))),
        box((-1.0, 20.7, 13.0), (7.0, 21.9, 14.2), ct('arm'), rot=('z', -22.5, (7.0, 21.3, 13.6))),
        box((6.5, 11.6, 12.4), (9.5, 14.4, 14.6), ct('cloth')),      # perizonium
        box((9.2, 10.0, 12.7), (10.0, 12.6, 14.2), ct('cloth')),     # knot flap
        box((7.0, 7.4, 12.7), (9.0, 11.8, 14.2), ct('legs')),        # thighs
        box((7.2, 3.0, 12.3), (8.8, 7.6, 13.7), ct('legs')),         # shins, knees forward
        box((7.1, 1.8, 12.5), (8.9, 3.0, 14.1), ct('legs')),         # crossed feet
        box((7.8, 2.2, 12.2), (8.2, 2.6, 12.5), fin(flat(IRON, 2))), # nail
    ]
    return P


# ------------------------------------------------------------------------------------------------ statues
def virgin_tone(kind):
    """Virgen de Luján style: celeste mantle with gold border and white stars, white gown, golden rays."""
    def t(ctx):
        i, j, w, h, f = ctx.i, ctx.j, ctx.w, ctx.h, ctx.face
        P = tp(ctx)
        if kind == 'gown':
            # front: white gown strip in the middle of the mantle cone, with gold embroidery
            if f == 'north':
                mid = abs(i + 0.5 - w / 2)
                strip = w * (0.16 + 0.22 * (j / h))
                if mid < strip:
                    if mid > strip - 1:
                        return (GOLD, 5)
                    k = 7 if (i + j) % 6 else 5
                    if j % 7 == 3 and abs(i + 0.5 - w / 2) < 1.5:
                        return (GOLD, 6)
                    return (LINEN, k)
                if mid < strip + 1.0:
                    return (GOLD, 4)
            if ctx.edge() == 0 and f != 'up' and j == h - 1:
                return (GOLD, 4)
            k = 5
            if (i * 7 + j * 3) % 11 == 0 and ctx.edge() > 0:
                return (LINEN, 8)                                # white stars
            u = (i if f in ('north', 'south') else i) + 0.5
            if math.sin(u * 0.9 + j * 0.05) > 0.6:
                k += 1
            if math.sin(u * 0.9 + 2.2) < -0.75:
                k -= 1
            return (CELESTE, k)
        if kind == 'face':
            if f == 'north':
                if j <= 0 or i == 0 or i == w - 1:
                    return (HAIR, 3)
                if j == 2 and i in (1, w - 2):
                    return (HAIR, 1)                             # lowered eyes
                if j == 4 and i in (2, 3) and w >= 6:
                    return (REDP, 5)                             # lips
                return (SKIN, 6 if 1 < i < w - 2 else 5)
            return (HAIR, 3 + (hh(i, j) > 0.7)) if f != 'down' else (SKIN, 4)
        if kind == 'hands':
            if f == 'north':
                if i == w // 2 - 1 + (w % 2) and j > 0:
                    return (SKIN, 3)                         # the two palms pressed together
                return (SKIN, 6 if j == 0 else 5)
            return (SKIN, 4)
        if kind == 'base':
            if j == 0 or j == h - 1:
                return (GOLD, 5)
            k = 4 + ((i // 3 + j // 3) % 2) if f == 'north' else 4
            return (NOGAL, k)
        return (GOLD, 5)
    return t


def rays_tone(ctx):
    """Silver-gilt resplendor behind the Virgin: rays radiating from the head, alternating straight / wavy."""
    w, h = ctx.w, ctx.h
    cx, cy = w / 2, h * 0.17
    x, y = ctx.i + 0.5 - cx, ctx.j + 0.5 - cy
    r = math.hypot(x, y * 1.05)
    a = math.atan2(y, x)
    n = 26
    ang = (a / (2 * math.pi) * n) % 1.0
    ray = abs(ang - 0.5)
    wavy = int(a / (2 * math.pi) * n) % 2
    reach = (h * 0.98 if wavy else h * 0.86)
    if r < 3.5 or r > reach - abs(math.sin(a)) * 4:
        return None
    width = 0.22 - r / reach * 0.12 + (0.06 * math.sin(r * 0.9) if wavy else 0)
    if ray < width:
        k = 6 - int(r / reach * 3) + (1 if ray < width * 0.4 else 0)
        return T(GOLD, k)
    if r < 6.5:
        return T(GOLD, 4)
    return None


def virgin_parts():
    vt = lambda k: fin(virgin_tone(k), dust=0.6, ao=0.8)
    P = [
        box((2.5, 0.0, 3.0), (13.5, 2.8, 13.0), vt('base')),         # gilded wooden pedestal
        box((3.0, 2.8, 3.5), (13.0, 3.4, 12.5), fin(brass(GOLD, base=4, seed=111))),
    ]
    tiers = [(2.0, 3.4, 7.0), (2.6, 7.0, 10.5), (3.3, 10.5, 14.0), (4.0, 14.0, 17.0), (4.7, 17.0, 20.0), (5.4, 20.0, 22.4)]
    for (inset, y0, y1) in tiers:
        P.append(box((inset + 0.8, y0, 5.0 + inset * 0.3), (16 - inset - 0.8, y1, 11.0 - inset * 0.3), vt('gown')))
    P += [
        box((7.3, 17.4, 4.5), (8.7, 19.6, 6.4), vt('hands')),        # joined hands
        box((6.8, 16.6, 4.9), (9.2, 17.6, 6.6), fin(brass(GOLD, base=5, seed=116))),   # gold cuffs
        box((6.5, 22.2, 6.2), (9.5, 25.4, 9.2), vt('face')),         # head
        box((6.1, 21.0, 7.6), (9.9, 25.6, 10.0), fin(virgin_tone('gown'), dust=0.3)),   # veil/mantle over the head
        box((6.3, 25.4, 6.0), (9.7, 26.4, 9.6), fin(brass(GOLD, base=6, seed=112))),    # crown band
        box((6.6, 26.4, 6.3), (9.4, 27.6, 9.3), fin(brass(GOLD, base=5, seed=113))),
        box((7.6, 27.6, 7.5), (8.4, 29.0, 8.3), fin(brass(GOLD, base=6, seed=114))),    # cross on the crown
        plane((-3.0, 4.0, 11.4), (19.0, 31.8, 11.4), rays_tone, faces=('north', 'south')),
        box((4.4, 3.4, 3.4), (11.6, 4.2, 4.4), fin(brass(NICKEL, base=6, seed=115))),  # silver crescent moon
    ]
    return P


def ines_tone(kind):
    def t(ctx):
        i, j, w, h, f = ctx.i, ctx.j, ctx.w, ctx.h, ctx.face
        if kind == 'tunic':
            k = 6 + (1 if (i // 2) % 3 == 0 else 0) - (1 if (i // 2) % 3 == 2 else 0)
            if j >= h - 1:
                return (GOLD, 4)
            return (LINEN, k)
        if kind == 'mantle':
            k = 4 + (1 if math.sin((i + j * 0.4) * 0.8) > 0.5 else 0) - (1 if math.sin((i + j * 0.4) * 0.8) < -0.7 else 0)
            if ctx.edge() == 0 and f != 'up':
                return (GOLD, 5)
            return (VELVET_R, k + 1)
        if kind == 'face':
            if f == 'north':
                if j <= 1:
                    return (HAIR, 4 if j == 1 else 3)            # fringe
                if i == 0 or i == w - 1:
                    return (HAIR, 4)
                if j == 3 and i in (1, w - 2):
                    return (BAKE, 2)                             # eyes
                if j == 3 and i in (2, w - 3):
                    return (SKIN, 7)
                if j == 5 and w // 2 - 1 <= i <= w // 2:
                    return (REDP, 5)
                if j == 4 and i in (1, w - 2):
                    return (REDP, 7)                             # cheeks
                return (SKIN, 6)
            return (HAIR, 4 + (hh(i, j) > 0.6)) if f != 'down' else (SKIN, 5)
        if kind == 'hair':
            k = 4 + (1 if (i + j // 3) % 4 == 0 else 0) - (1 if (i * 3 + j) % 7 == 0 else 0)
            return (HAIR, k)
        if kind == 'skin':
            return (SKIN, 6 if f in ('north', 'up') else 5)
        if kind == 'lamb':
            if f == 'north' and ctx.part.name == 'lambhead':
                if j == 2 and i in (1, w - 2):
                    return (BAKE, 2)
                if j >= h - 2 and w // 2 - 1 <= i <= w // 2:
                    return (SKIN, 4)
            k = 6 + (1 if (i + (j % 2)) % 3 == 0 else 0) - (1 if (i * 2 + j) % 5 == 0 else 0)
            return (WAX, k)
        if kind == 'base':
            if j == 0:
                return (GOLD, 5)
            return (MARBLE, 5 + ((i + j) % 9 == 0))
        if kind == 'halo':
            return None
        return (LINEN, 6)
    return t


def halo_tone(ctx):
    x = (ctx.i + 0.5) / ctx.w * 2 - 1
    y = (ctx.j + 0.5) / ctx.h * 2 - 1
    r = math.hypot(x, y)
    if 0.8 < r < 1.0:
        return T(GOLD, 6 if y < 0 else 5)
    if r < 0.8 and int((math.atan2(y, x) + 3.2) * 4) % 2 == 0 and r > 0.55:
        return T(GOLD, 4)
    return None


def palm_tone(ctx):
    """Martyr's palm frond (cutout): central rib with leaflets angled upward."""
    w, h = ctx.w, ctx.h
    x = ctx.i + 0.5 - w / 2
    y = ctx.j + 0.5
    if abs(x) < 0.6:
        return T(PINO, 5)
    if y > h * 0.88:
        return None
    side = abs(x)
    reach = (w / 2) * (0.35 + 0.65 * math.sin(min(1, y / (h * 0.85)) * math.pi * 0.95))
    if side < reach and ((int(y) - int(side * 0.9)) % 3 == 0):
        return T(GOLD, 3 + (side < reach * 0.5)) if hh(ctx.i, ctx.j) > 0.1 else T(VERDI, 2)
    return None


def ines_parts(body=True, head=True, head_only=False):
    it = lambda k: fin(ines_tone(k), dust=0.6, ao=0.8)
    P = []
    hy = 0.0
    if head_only:
        hy = -14.0     # head centred low in its own block, for the turning display entity
    if body:
        P += [
            box((3.0, 0.0, 3.5), (13.0, 2.6, 12.5), it('base')),
            box((4.2, 2.6, 5.4), (11.8, 9.0, 10.6), it('tunic')),
            box((4.8, 9.0, 5.8), (11.2, 15.0, 10.2), it('tunic')),
            box((5.3, 15.0, 6.3), (10.7, 20.4, 9.7), it('tunic')),
            box((4.0, 4.0, 8.6), (12.0, 16.0, 11.0), it('mantle')),      # red mantle at the back
            box((4.6, 16.0, 8.4), (11.4, 20.2, 10.4), it('mantle')),
            box((3.9, 9.5, 5.0), (12.1, 12.0, 8.0), it('mantle'), rot=('z', -22.5, (8, 10.7, 6.5))),  # drape across
            box((4.0, 13.0, 6.8), (5.4, 19.6, 8.4), it('mantle')),       # right arm (down, holding the palm)
            box((3.8, 12.2, 6.4), (5.4, 13.4, 8.2), it('skin')),         # hand
            box((10.4, 15.0, 5.0), (11.8, 19.8, 8.2), it('mantle')),     # left arm cradling the lamb
            box((8.6, 14.6, 3.6), (12.4, 17.4, 7.2), it('lamb'), name='lamb'),
            box((11.4, 16.6, 2.8), (13.0, 18.6, 4.6), it('lamb'), name='lambhead'),
            box((11.0, 18.0, 3.6), (11.6, 18.6, 4.2), it('lamb')),       # ear
            box((12.8, 18.0, 3.6), (13.4, 18.6, 4.2), it('lamb')),
            box((9.0, 14.0, 4.0), (9.8, 14.6, 4.8), it('lamb')),         # folded legs
            box((11.2, 14.0, 4.0), (12.0, 14.6, 4.8), it('lamb')),
            plane((2.6, 12.0, 7.3), (5.6, 26.0, 7.3), palm_tone, faces=('north', 'south')),
        ]
    if head or head_only:
        H = [
            box((6.3, 20.2, 6.1), (9.7, 23.8, 9.3), it('face')),
            box((5.9, 15.5, 8.2), (10.1, 24.2, 10.0), it('hair')),        # long hair down the back
            box((5.9, 20.4, 6.6), (6.3, 24.0, 8.2), it('hair')),
            box((9.7, 20.4, 6.6), (10.1, 24.0, 8.2), it('hair')),
            box((6.1, 23.8, 6.4), (9.9, 24.4, 8.4), it('hair')),
            plane((4.6, 19.8, 10.3), (11.4, 26.6, 10.3), halo_tone, faces=('north', 'south')),
        ]
        if head_only:
            H = [p for p in H]
            for p in H:
                if p.frm[1] < 18:
                    p.frm = (p.frm[0], 18.0, p.frm[2])
            shift(H, dy=hy)
        P += H
    return P


# ------------------------------------------------------------------------------------------------ pews
def pew_parts(side):
    """Church pew piece, the sitter looks north. side: 'izq' (end panel on the west), 'centro', 'der'."""
    mS = fin(wood(NOGAL, seed=121, boards=(2, 8), axis=0, worn_pal=RAW, wear=0.55))
    mB = fin(wood(NOGAL, seed=123, axis=0, base=4))
    mE = fin(panels(wood(NOGAL, seed=125, axis=1, base=3), wood(NOGAL, seed=126, axis=1, base=4),
                    rects=((3, 4, -3, -7),), faces=('west', 'east'), carve=cross_carve))
    mK = fin(cloth(LEATHER_B, base=4, seed=127, folds=0.0, weave=False, stains=0.2))
    P = [
        box((0, 6.8, 4.0), (16, 7.8, 12.0), mS),                     # seat
        box((0, 6.3, 3.6), (16, 7.4, 4.2), mB),                      # rounded seat nose
        box((0, 5.4, 4.3), (16, 6.8, 5.0), mB),                      # apron
        box((0, 7.8, 11.4), (16, 9.0, 12.2), mB),                    # back bottom rail
        box((0, 9.0, 11.7), (16, 14.6, 12.4), mS),                   # back boards
        box((0, 14.6, 11.3), (16, 15.6, 12.9), mB),                  # top rail (hand rail for the row behind)
        box((0, 10.2, 12.4), (16, 10.7, 14.0), mB),                  # hymn-book shelf behind
        box((0, 10.7, 13.6), (16, 11.7, 14.0), mB),
        box((0, 1.6, 12.9), (16, 2.4, 15.6), mB),                    # kneeler (for the row behind)
        box((0.0, 2.4, 13.1), (16, 3.0, 15.4), mK),                  # worn leather pad
    ]
    if side in ('izq', 'der'):
        x0, x1 = (0.0, 1.3) if side == 'izq' else (14.7, 16.0)
        P += [
            box((x0, 0, 3.2), (x1, 14.6, 13.0), mE),                 # carved end panel
            box((x0 - 0.15, 14.6, 8.6), (x1 + 0.15, 16.4, 13.4), mB),   # scrolled top
            box((x0 - 0.15, 8.6, 2.8), (x1 + 0.15, 9.8, 5.6), mB),   # arm scroll
            box((x0 - 0.1, 0, 2.9), (x1 + 0.1, 0.8, 13.3), fin(painted(NOGAL, base=2, seed=128, grime=0.8))),
            box((x0, 0, 13.0), (x1, 3.0, 15.8), mB),                 # kneeler bracket
        ]
    else:
        P += [box((7.4, 0, 5.0), (8.6, 6.8, 11.6), mB), box((7.5, 0, 11.6), (8.5, 1.6, 15.2), mB)]
    return P


# ------------------------------------------------------------------------------------------------ altar
def lace_tone(ctx):
    """Bobbin-lace edging (cutout): solid band, a row of pin holes, then rounded scallops."""
    i, j, h = ctx.i, ctx.j, ctx.h
    if j == 0:
        return T(LINEN, 7)
    if j == 1:
        return None if i % 2 == 0 else T(LINEN, 8)
    u = (i % 8) - 3.5
    reach = 3.6 - (j - 2) * 1.25
    if abs(u) < reach:
        if j == 2 and abs(u) < 1:
            return None
        return T(LINEN, 8 if (i + j) % 2 else 6)
    return None


def altar_tone(kind, emblem=False, off=(0, 0, 0)):
    cl = cloth(LINEN, base=7, seed=131, fold_axis='i', folds=0.7, fold_px=2.6, stains=0.22, off=off)
    wd = wood(NOGAL, seed=133, off=off, base=4, axis=1)
    fr = wood(NOGAL, seed=134, off=off, base=3, axis=0)

    def t(ctx):
        if kind == 'cloth':
            c = cl(ctx)
            if ctx.face == 'north' and emblem:
                cx = ctx.w // 2
                pts = draw_text(F35, 'IHS', cx - 6, 4)
                if (ctx.i, ctx.j) in set(pts):
                    return T(GOLD, 6)
                if ctx.i == cx and 0 <= ctx.j <= 2:
                    return T(GOLD, 6)
                if ctx.j == 1 and abs(ctx.i - cx) <= 1:
                    return T(GOLD, 6)
            if ctx.face == 'north' and ctx.j >= ctx.h - 2:
                return T(GOLD, 5 if ctx.j == ctx.h - 2 else 3)          # gold braid above the lace
            return c
        if kind == 'base':
            if ctx.face == 'north':
                i, j, w, h = ctx.i, ctx.j, ctx.w, ctx.h
                u = (i % 32) - 15.5 if w >= 32 else i - w / 2 + 0.5
                top = 13 + int(abs(u) ** 2 / 14)
                if abs(u) < 11 and top <= j < h - 3:
                    if abs(u) >= 10 or j == top:
                        return (GOLD, 4 + (j == top))
                    pl, k = wd(ctx)
                    return (pl, k - 1 - (j < top + 2) - (abs(u) > 8.5))
                if j >= h - 3:
                    return fr(ctx)
            return fr(ctx)
        return fr(ctx)
    return t


def altar_parts(side):
    # front-facing piece: the viewer's left is +x in authoring space, so 'izq' has its open end at x=16
    off = {'izq': (32, 0, 0), 'centro': (16, 0, 0), 'der': (0, 0, 0)}[side]
    side = {'izq': 'der', 'der': 'izq'}.get(side, side)
    emb = side == 'centro'
    mBase = fin(altar_tone('base', off=off), dust=0.4)
    mTop = fin(wood(NOGAL, seed=135, off=off, base=4, axis=0))
    mCl = fin(altar_tone('cloth', emblem=emb, off=off), dust=0.5)
    mPl = fin(marble(seed=137, base=5, off=off))
    x0 = 0.0 if side != 'izq' else 1.0
    x1 = 16.0 if side != 'der' else 15.0
    c0 = 0.0 if side != 'izq' else 0.2
    c1 = 16.0 if side != 'der' else 15.8
    P = [
        box((0, 0, 2.4), (16, 1.2, 15.0), mPl),                                 # marble step
        box((x0, 1.2, 3.6), (x1, 14.6, 14.0), mBase),
        box((x0 - 0.4, 1.2, 3.2), (x1 + (0.4 if side == 'der' else 0), 2.2, 14.4), mTop),   # base moulding
        box((c0 + 0.2, 14.6, 2.6), (c1 - 0.2, 15.6, 14.8), mTop),               # mensa
        box((c0, 15.6, 2.3), (c1, 15.9, 15.0), mCl),                            # cloth on top
        box((c0, 10.6, 2.0), (c1, 15.9, 2.3), mCl, faces=('north', 'down', 'west', 'east')),   # front drop
        plane((c0, 8.8, 1.95), (c1, 10.6, 1.95), lace_tone, faces=('north', 'south')),
    ]
    if side in ('izq', 'der'):
        x = c0 if side == 'izq' else c1
        x2 = x - 0.3 if side == 'izq' else x + 0.3
        P.append(box((min(x, x2), 8.4, 2.0), (max(x, x2), 15.9, 15.0), mCl, faces=('west', 'east', 'down', 'north', 'south')))
    return P


# ------------------------------------------------------------------------------------------------ candlesticks
def candelabro_parts(lit):
    mB = fin(brass(seed=141, base=5), dust=0.5)
    mD = fin(brass(seed=142, base=4, sheen=False), dust=0.5)
    P = [
        box((5.0, 0.0, 5.0), (11.0, 1.0, 11.0), mD),
        box((4.4, 0.0, 4.4), (6.0, 1.4, 6.0), mB), box((10.0, 0.0, 4.4), (11.6, 1.4, 6.0), mB),   # claw feet
        box((4.4, 0.0, 10.0), (6.0, 1.4, 11.6), mB), box((10.0, 0.0, 10.0), (11.6, 1.4, 11.6), mB),
        box((5.8, 1.0, 5.8), (10.2, 2.4, 10.2), mB),
        box((6.8, 2.4, 6.8), (9.2, 3.4, 9.2), mD),
        box((7.3, 3.4, 7.3), (8.7, 22.0, 8.7), mB),                  # stem
        box((6.7, 7.6, 6.7), (9.3, 9.0, 9.3), mB),                   # knops
        box((6.9, 14.4, 6.9), (9.1, 15.6, 9.1), mB),
        box((7.0, 19.6, 7.0), (9.0, 20.6, 9.0), mD),
        box((5.6, 22.0, 5.6), (10.4, 22.6, 10.4), mB),               # drip pan
        box((5.4, 22.6, 5.4), (10.6, 23.0, 5.8), mD), box((5.4, 22.6, 10.2), (10.6, 23.0, 10.6), mD),
        box((5.4, 22.6, 5.8), (5.8, 23.0, 10.2), mD), box((10.2, 22.6, 5.8), (10.6, 23.0, 10.2), mD),
        box((7.0, 22.6, 7.0), (9.0, 23.6, 9.0), mB),                 # socket
    ]
    P += candle(8.0, 8.0, 23.6, 29.6, r=0.85, lit=lit, seed=143)
    # a wax drip running over the pan
    P.append(box((8.85, 22.4, 7.6), (9.25, 23.6, 8.2), fin(flat(WAX, 6), ao=0, dust=0)))
    return P


def candelero_altar_parts(lit):
    mB = fin(brass(seed=151, base=5), dust=0.4)
    P = [
        box((5.4, 0.0, 5.4), (10.6, 0.8, 10.6), mB),
        box((6.2, 0.8, 6.2), (9.8, 1.6, 9.8), mB),
        box((7.3, 1.6, 7.3), (8.7, 6.4, 8.7), mB),
        box((6.8, 3.2, 6.8), (9.2, 4.2, 9.2), mB),
        box((6.0, 6.4, 6.0), (10.0, 7.0, 10.0), mB),
        box((7.0, 7.0, 7.0), (9.0, 7.8, 9.0), mB),
    ]
    P += candle(8.0, 8.0, 7.8, 13.4, r=0.75, lit=lit, seed=152)
    return P


def puddle_tone(centres, seed=0):
    """Irregular wax puddle (cutout): union of blobs around the candles, creamy with darker dirty rim."""
    def t(ctx):
        if ctx.face != 'up':
            return None
        x, z = ctx.pos[0], ctx.pos[2]
        best = 9.0
        for (cx, cz, r) in centres:
            d = math.hypot(x - cx, z - cz) - r - (vn(x / 1.7, z / 1.7, 0.5, seed) - 0.5) * 1.6
            best = min(best, d)
        if best > 0:
            return None
        k = 5 if best < -0.6 else 3
        if hh(ctx.i, ctx.j, seed) < 0.06:
            k -= 1
        return (WAX, k)
    return t


def velas_piso_parts(lit):
    cands = ((6.0, 7.0, 7.5, 1.1), (9.6, 6.2, 5.0, 0.9), (8.4, 10.0, 9.0, 1.0), (4.8, 10.4, 3.6, 0.8), (11.0, 9.4, 2.4, 1.2))
    P = [box((1.0, 0.0, 1.5), (15.0, 0.3, 15.0), fin(puddle_tone([(x, z, r + 1.6) for (x, z, _, r) in cands], 161), ao=0, dust=0.5),
             faces=('up',))]
    for n, (x, z, hgt, r) in enumerate(cands):
        P += candle(x, z, 0.3, 0.3 + hgt, r=r, lit=lit and n != 3, seed=162 + n)
    return P


# ------------------------------------------------------------------------------------------------ confessional
def grille_tone(base_pal=NOGAL, holes=True):
    """Pierced wooden grille: diamond lattice with see-through holes (cutout)."""
    def t(ctx):
        if ctx.face not in ('west', 'east', 'north', 'south'):
            return T(base_pal, 3)
        i, j = ctx.i, ctx.j
        if ctx.edge() == 0:
            return T(base_pal, 3)
        a, b = (i + j) % 4, (i - j) % 4
        if holes and a and b:
            return None
        return T(base_pal, 4 if (a == 0) else 3)
    return t


def confessional_parts(col, row):
    """col: 'izq' | 'centro' | 'der' (viewer's left/right), row 0 = bottom, 1 = top. Front faces north."""
    off = {'izq': (32, 0, 0), 'centro': (16, 0, 0), 'der': (0, 0, 0)}[col]
    off = (off[0], row * 16, 0)
    wd = lambda sd, **kw: wood(NOGAL, seed=171 + sd, off=off, worn_pal=RAW, **kw)
    mFrame = fin(wd(0, base=4))
    mPanel = fin(panels(wd(1, base=3, axis=1), wd(2, base=4, axis=1), rects=((3, 3, -3, -3),),
                        faces=('north', 'south', 'west', 'east')))
    mDoor = fin(panels(wd(3, base=4, axis=1), wd(4, base=4, axis=1),
                       rects=((3, 4, -3, 14), (3, 18, -3, -4)) if row == 0 else ((3, 3, -3, 12),), faces=('north',)))
    mCurt = fin(cloth(VELVET_P, base=4, seed=181, fold_axis='i', folds=0.9, fold_px=2.2, weave=False, stains=0.15,
                      stain_col=hx('#2a1a20')), ao=0.5, dust=0.3)
    mGr = fin(grille_tone(), ao=0, dust=0)
    mPad = fin(cloth(LEATHER_B, base=3, seed=183, folds=0, weave=False, stains=0.2))
    P = []
    outer_x = {'izq': (14.6, 16.0), 'der': (0.0, 1.4)}
    if row == 0:
        P.append(box((0, 0, 0.6), (16, 1.0, 16), fin(wd(5, base=3, axis=0))))          # raised floor / plinth
        P.append(box((0, 0, 0.2), (16, 0.6, 0.6), fin(painted(NOGAL, base=2, seed=185, grime=0.8))))
    P.append(box((0, 0 if row else 1.0, 15.0), (16, 16, 16), mPanel))                    # back wall
    if col == 'centro':
        for (x0, x1) in ((0.0, 1.2), (14.8, 16.0)):
            if row == 0:
                P.append(box((x0, 1.0, 0.6), (x1, 9.0, 15.0), mPanel))
                P.append(box((x0, 9.0, 1.0), (x1, 16.0, 4.0), mFrame))
                P.append(box((x0, 9.0, 10.0), (x1, 16.0, 15.0), mFrame))
                P.append(box((x0 + 0.3, 9.0, 4.0), (x1 - 0.3, 16.0, 10.0), mGr, faces=('west', 'east')))   # grille
                P.append(box((x0, 15.2, 4.0), (x1, 16.0, 10.0), mFrame))
            else:
                P.append(box((x0, 0.0, 0.6), (x1, 2.0, 15.0), mFrame))
                P.append(box((x0, 2.0, 0.6), (x1, 16.0, 15.0), mPanel))
        if row == 0:
            P.append(box((1.2, 1.0, 0.8), (14.8, 16.0, 1.6), mDoor))                     # priest's door
            P.append(box((12.4, 8.0, 0.2), (13.4, 9.2, 0.8), M_BRASS))                    # knob
            P.append(box((2.0, 1.0, 9.0), (14.0, 8.0, 14.6), fin(panels(wd(6, base=4), faces=('north',)))))  # priest's seat
        else:
            P.append(box((1.2, 0.0, 0.8), (14.8, 7.0, 1.6), mDoor))
            P.append(box((1.2, 7.0, 1.0), (14.8, 13.0, 1.4), mCurt, faces=('north', 'south')))   # little curtain window
            P.append(box((1.2, 13.0, 0.8), (14.8, 16.0, 1.6), mFrame))
            P.append(box((1.2, 6.8, 0.4), (14.8, 7.4, 1.0), mFrame))
    else:
        x0, x1 = outer_x[col]
        P.append(box((x0, 0 if row else 1.0, 0.6), (x1, 16, 15.0), mPanel))             # outer side wall
        if row == 0:
            ix = (1.2, 7.0) if col == 'der' else (9.0, 14.8)
            kx = (10.0, 15.2) if col == 'der' else (0.8, 6.0)
            P.append(box((kx[0], 1.0, 2.0), (kx[1], 3.6, 13.0), fin(wd(7, base=4))))      # kneeler next to the grille
            P.append(box((kx[0] + 0.3, 3.6, 2.3), (kx[1] - 0.3, 4.2, 12.7), mPad))
            P.append(box((kx[0], 10.0, 3.0), (kx[1], 10.8, 11.0), fin(wd(8, base=4))))     # elbow rest under the grille
        # velvet curtain on the open front (pulled to the outer side)
        cx0, cx1 = (8.0, 14.6) if col == 'izq' else (1.4, 8.0)
        P.append(box((cx0, 0.0 if row else 1.4, 0.9), (cx1, 16 if row == 0 else 13.6, 1.6), mCurt, faces=('north', 'south', 'west', 'east', 'down')))
        if row == 1:
            P.append(box((0, 13.6, 1.0), (16, 14.2, 1.4), M_BRASS))                        # curtain rod
    if row == 1:
        P.append(box((0, 14.2, 0.2), (16, 16.0, 16), fin(wd(9, base=4, axis=0))))          # roof / cornice
        P.append(box((0, 15.2, -0.4), (16, 16.4, 0.4), fin(wd(10, base=5, axis=0))))
        if col == 'centro':
            mG = fin(brass(GOLD, seed=187, base=5))
            P += [box((5.0, 16.4, 1.0), (11.0, 17.6, 4.0), fin(wd(11, base=4))),           # crest + cross
                  box((7.4, 17.6, 2.0), (8.6, 23.0, 3.0), mG), box((5.8, 20.4, 2.0), (10.2, 21.4, 3.0), mG)]
    return P


# ------------------------------------------------------------------------------------------------ fonts of water
def water_tone(ctx):
    i, j = ctx.i, ctx.j
    k = 3
    if (i * 3 + j * 5) % 13 == 0:
        k = 5
    if (i + j * 2) % 17 == 0:
        k = 4
    return (pal('#0f1b1e', '#162a2e', '#1e383c', '#2a4a4c', '#3e6262', '#6a8e8a'), k)


def font_parts():
    mM = fin(marble(seed=191, base=6))
    mM2 = fin(marble(seed=192, base=5))
    P = [
        box((3.0, 0.0, 3.0), (13.0, 1.4, 13.0), mM2),
        box((4.2, 1.4, 4.2), (11.8, 2.4, 11.8), mM),
        box((5.8, 2.4, 5.8), (10.2, 8.0, 10.2), mM),                 # stem
        box((5.2, 5.0, 5.2), (10.8, 5.8, 10.8), mM2),                # carved ring
        box((4.6, 8.0, 4.6), (11.4, 9.2, 11.4), mM2),                # bowl foot
        box((2.4, 9.2, 2.4), (13.6, 10.4, 13.6), mM),                # bowl bottom
        box((2.0, 10.4, 2.0), (14.0, 14.0, 3.2), mM), box((2.0, 10.4, 12.8), (14.0, 14.0, 14.0), mM),   # bowl walls
        box((2.0, 10.4, 3.2), (3.2, 14.0, 12.8), mM), box((12.8, 10.4, 3.2), (14.0, 14.0, 12.8), mM),
        box((3.2, 10.4, 3.2), (12.8, 12.8, 12.8), fin(water_tone, ao=0.0, dust=0), faces=('up',)),
        box((1.7, 13.4, 1.7), (14.3, 14.2, 14.3), mM2, faces=('north', 'south', 'west', 'east', 'down')),  # lip
    ]
    return P


def stoup_parts():
    """Pila de agua bendita: marble shell basin on the wall near the door."""
    mM = fin(marble(seed=195, base=6), dust=0.3)
    return [
        box((5.0, 6.0, 15.0), (11.0, 14.0, 16.0), fin(marble(seed=196, base=5))),   # back plate
        box((5.4, 6.5, 11.6), (10.6, 7.6, 15.0), mM),                               # basin bottom
        box((5.0, 7.6, 11.2), (11.0, 9.6, 12.0), mM),                               # basin walls
        box((5.0, 7.6, 12.0), (5.8, 9.6, 15.0), mM), box((10.2, 7.6, 12.0), (11.0, 9.6, 15.0), mM),
        box((5.8, 7.6, 12.0), (10.2, 8.8, 15.0), fin(water_tone, ao=0, dust=0), faces=('up',)),
        box((7.6, 4.8, 13.0), (8.4, 6.5, 14.0), mM),                                # drop
        box((7.5, 14.0, 15.2), (8.5, 15.6, 15.8), fin(brass(GOLD, base=5, seed=197))),  # little cross
        box((7.0, 14.6, 15.2), (9.0, 15.0, 15.8), fin(brass(GOLD, base=5, seed=198))),
    ]


# ------------------------------------------------------------------------------------------------ sanctuary lamp, chains
def chain_tone(ctx):
    """Chain links (cutout): an open ring seen flat, then a link seen edge-on, like vanilla chains."""
    i, j, w = ctx.i, ctx.j, ctx.w
    y = j % 7
    c = (w - 1) / 2.0
    d = abs(i - c)
    if y < 4:
        ring = ['.#.', '#.#', '#.#', '.#.'][y]
        ix = int(round(i - c + 1))
        if 0 <= ix < 3 and ring[ix] == '#':
            return T(IRON, 6 if (y == 0 or ix == 0) else 4)
        return None
    if d < 0.6:
        return T(IRON, 5 if y == 5 else 3)
    return None


def chain_parts(x=8.0, z=8.0, y0=0.0, y1=16.0, w=1.5):
    return [plane((x - w / 2, y0, z), (x + w / 2, y1, z), chain_tone, faces=('north', 'south')),
            plane((x, y0, z - w / 2), (x, y1, z + w / 2), chain_tone, faces=('west', 'east'))]


def lamp_glass_tone(lit):
    def t(ctx):
        i, j, w, h = ctx.i, ctx.j, ctx.w, ctx.h
        c = 1 - abs((i + 0.5) / w * 2 - 1)
        if ctx.face == 'up':
            d = math.hypot((i + 0.5) / w - 0.5, (j + 0.5) / h - 0.5)
            if lit and d < 0.18:
                return T(FLAME, 5)
            return T(GLASSR, 5 if lit else 2)
        k = (3 + int(c * 3.5) + (1 if j > h * 0.5 else 0)) if lit else (1 + int(c * 2))
        if i == 1 or (j == 1 and i % 3 == 0):
            k += 2                                               # glass highlights / moulded ribs
        return T(GLASSR, k)
    return t


def sanctuary_lamp_parts(lit):
    mB = fin(brass(seed=201, base=5, tarnish=0.4), dust=0.3, ao=0.6)
    mGl = fin(lamp_glass_tone(lit), ao=0, dust=0)
    P = [
        box((7.6, 0.6, 7.6), (8.4, 1.6, 8.4), mB),                   # drop finial
        box((7.0, 1.6, 7.0), (9.0, 2.6, 9.0), mB),
        box((5.6, 2.6, 5.6), (10.4, 3.8, 10.4), mB),                 # cup
        box((6.0, 3.8, 6.0), (10.0, 8.6, 10.0), mGl, shade=not lit), # red glass
        box((5.6, 8.6, 5.6), (10.4, 9.4, 10.4), mB, faces=('north', 'south', 'west', 'east', 'down')),  # rim
        box((5.6, 8.6, 5.6), (10.4, 9.4, 6.0), mB, faces=('up',)), box((5.6, 8.6, 10.0), (10.4, 9.4, 10.4), mB, faces=('up',)),
        box((5.6, 8.6, 6.0), (6.0, 9.4, 10.0), mB, faces=('up',)), box((10.0, 8.6, 6.0), (10.4, 9.4, 10.0), mB, faces=('up',)),
        box((5.7, 4.6, 5.7), (10.3, 5.2, 10.3), mB, faces=('north', 'south', 'west', 'east')),   # band
    ]
    for (x, z) in ((5.8, 5.8), (9.8, 5.8), (5.8, 9.8), (9.8, 9.8)):
        P.append(box((x, 9.4, z), (x + 0.4, 12.0, z + 0.4), mB))     # straps up to the crown
    P.append(box((5.6, 12.0, 5.6), (10.4, 12.6, 10.4), mB))          # crown
    P.append(box((7.0, 12.6, 7.0), (9.0, 13.4, 9.0), mB))
    P += chain_parts(8.0, 8.0, 13.4, 16.0, 1.4)
    return P


# ------------------------------------------------------------------------------------------------ harmonium
def keys_tone(ctx):
    """Keyboard top: yellowed ivory naturals with black sharps (2+3 pattern), worn middle keys."""
    if ctx.face != 'up':
        return (WAX, 4) if ctx.face != 'south' else (WAX, 5)
    i, j, w, h = ctx.i, ctx.j, ctx.w, ctx.h
    X = int(ctx.pos[0] * 2 + (16 if ctx.block.key.endswith('_der') else 0) * 2)
    nat = X // 2                         # 2 px per natural key
    sub = X % 2
    oct_ = nat % 7
    if j < h * 0.55 and (sub == 1 and oct_ in (0, 1, 3, 4, 5) or sub == 0 and oct_ in (1, 2, 4, 5, 6)):
        if (sub == 1 and oct_ in (0, 1, 3, 4, 5)) or (sub == 0 and oct_ in (1, 2, 4, 5, 6)):
            return (BAKE, 3 if j > 0 else 5)
    if sub == 1 and j >= h * 0.55:
        return (WAX, 3)                  # gaps between naturals
    k = 6 - (1 if hh(nat, 3) < 0.3 else 0) - (1 if j == h - 1 else 0)
    if 10 < nat < 22 and hh(nat, j, 5) < 0.25:
        k -= 1                           # yellowed from use
    return (WAX, k)


def harmonium_parts(side):
    """Reed organ (2 blocks wide); the organist sits on the SOUTH side looking north."""
    off = (0, 0, 0) if side == 'izq' else (16, 0, 0)
    wd = lambda sd, **kw: wood(NOGAL, seed=211 + sd, off=off, worn_pal=RAW, **kw)
    mCase = fin(panels(wd(0, base=3, axis=1), wd(1, base=4, axis=1), rects=((3, 3, -3, -3),), faces=('south', 'west', 'east', 'north')))
    mW = fin(wd(2, base=4))
    mFret = fin(panels(wd(3, base=4, axis=0), rects=((2, 2, -2, -2),), faces=('south', 'north'),
                       carve=lambda c, di, dj, w, h: -3 if ((di + dj) % 4 == 0 or (di - dj) % 4 == 0) and 1 < dj < h - 2 else 0))
    mCloth = fin(cloth(VELVET_R, base=3, seed=219, folds=0, weave=True, stains=0.25))
    mKeys = fin(keys_tone, ao=0.6, dust=0.6)
    mIv = fin(flat(WAX, 6), ao=0, dust=0.3)
    edge0, edge1 = (0.6, 16.0) if side == 'izq' else (0.0, 15.4)
    P = [
        box((edge0, 0.0, 2.6), (edge1, 1.2, 13.2), fin(painted(NOGAL, base=2, seed=221, grime=0.8))),   # plinth
        box((edge0 + 0.4, 1.2, 3.0), (edge1 - (0.4 if side == 'der' else 0), 10.4, 12.6), mCase),        # lower case
        box((edge0, 10.4, 2.8), (edge1, 11.2, 13.4), mW),                                               # key bed
        box((edge0 + (2.0 if side == 'izq' else 0), 11.2, 9.8), (edge1 - (2.0 if side == 'der' else 0), 11.9, 14.2), mKeys),  # keys
        box((edge0 + (2.0 if side == 'izq' else 0), 11.2, 14.2), (edge1 - (2.0 if side == 'der' else 0), 11.9, 14.6), mW),
        box((edge0, 11.2, 3.0), (edge1, 15.0, 9.8), mW),                                                # stop rail block
        box((edge0, 15.0, 3.0), (edge1, 24.0, 8.6), mFret),                                             # upper case (fretwork)
        box((edge0, 16.0, 8.6), (edge1, 16.7, 11.0), mW),                                               # music rest ledge
        box((edge0 - 0.2, 24.0, 2.6), (edge1 + 0.2 if side == 'der' else edge1, 25.0, 9.2), fin(wd(4, base=5, axis=0))),   # cornice
        box((edge0, 4.4, 12.6), (edge1 - (0.4 if side == 'der' else 0), 6.4, 13.0), mW),                 # knee board
    ]
    if side == 'izq':
        P += [box((0.6, 11.2, 9.8), (2.6, 13.4, 14.6), mW),                                         # key cheek
              box((0.2, 25.0, 3.0), (2.0, 27.0, 5.0), fin(wd(5, base=5))),                          # finial
              box((-1.2, 13.0, 9.0), (0.6, 13.6, 11.0), M_BRASS),                                   # candle bracket
              box((-1.0, 13.6, 9.2), (0.4, 14.2, 10.8), M_BRASS)]
        P += candle(-0.3, 10.0, 14.2, 17.4, r=0.6, lit=False, seed=223)
        P += [box((3.0, 1.2, 12.2), (7.4, 2.6, 16.6), mCloth, rot=('x', -22.5, (5.2, 1.2, 12.2)))]   # bellows pedal
    else:
        P += [box((13.4, 11.2, 9.8), (15.4, 13.4, 14.6), mW),
              box((14.0, 25.0, 3.0), (15.8, 27.0, 5.0), fin(wd(6, base=5)))]
        P += [box((8.6, 1.2, 12.2), (13.0, 2.6, 16.6), mCloth, rot=('x', -22.5, (10.8, 1.2, 12.2)))]
        # open hymn book on the music rest
        mPg = fin(cloth(PAPER, base=7, seed=225, folds=0, weave=False, stains=0.3), ao=0.3, dust=0.4)
        P += [box((-6.0, 16.7, 8.2), (0.0, 22.5, 8.6), mPg, rot=('y', 22.5, (0.0, 16.7, 8.4))),
              box((0.0, 16.7, 8.2), (6.0, 22.5, 8.6), mPg, rot=('y', -22.5, (0.0, 16.7, 8.4)))]
    # ivory stop knobs
    xs = (3.5, 6.5, 9.5, 12.5) if side == 'izq' else (3.0, 6.0, 9.0, 12.0)
    for x in xs:
        P.append(box((x - 0.4, 13.2, 9.8), (x + 0.4, 14.0, 10.4), mIv))
        P.append(box((x - 0.6, 12.4, 9.79), (x + 0.6, 12.8, 9.8), fin(flat(PAPER, 6), ao=0, dust=0), faces=('south',)))
    return P


# ------------------------------------------------------------------------------------------------ choir lecterns
def lectern_label_tone(name):
    pts = set(draw_text(F35, name, 1, 1)) if name else set()

    def t(ctx):
        if ctx.face != 'up':
            return (PAPER, 4)
        if (ctx.i, ctx.j) in pts:
            return INK
        k = 7 - (ctx.edge() == 0)
        return (PAPER, k)
    return t


def score_tone(ctx):
    """Sheet music: staves with notes."""
    if ctx.face != 'up':
        return (PAPER, 5)
    i, j = ctx.i, ctx.j
    if ctx.edge() == 0:
        return (PAPER, 5)
    y = j % 7
    if y in (1, 2, 3, 4, 5) and 1 < i < ctx.w - 2:
        if hh(i // 3, j // 7, 3) < 0.3 and y in (2, 3) and i % 3 == 1:
            return INK
        if hh(i // 3, j // 7, 4) < 0.3 and i % 3 == 2 and y in (1, 2, 3):
            return INK
        if y in (1, 3, 5):
            return mix(T(PAPER, 6), INK, 0.45)
    return (PAPER, 7)


def atril_parts(kind):
    """Choir lectern: the singer stands on the SOUTH side looking north. kind: 'vacio' | 'partitura' | 'albornoz'."""
    mW = fin(outline(wood(NOGAL, seed=231, base=4, wear=0.5)))
    mD = fin(wood(NOGAL, seed=233, axis=0, base=4, boards=(2, 12), worn_pal=RAW))
    rot = ('x', 22.5, (8.0, 15.0, 9.0))
    P = [
        box((3.0, 0.0, 7.2), (13.0, 1.2, 8.8), mW), box((7.2, 0.0, 3.0), (8.8, 1.2, 13.0), mW),   # cross base
        box((7.4, 1.2, 7.4), (8.6, 14.6, 8.6), mW),                   # column
        box((7.0, 1.2, 7.0), (9.0, 2.6, 9.0), mW), box((7.1, 7.0, 7.1), (8.9, 8.0, 8.9), mW),
        box((6.8, 13.8, 6.8), (9.2, 15.0, 9.2), mW),                  # head
        box((-2.0, 15.0, 3.0), (18.0, 15.8, 15.0), mD, rot=rot),      # slanted desk
        box((-2.0, 15.8, 14.2), (18.0, 16.8, 15.0), mW, rot=rot),     # ledge
    ]
    if kind in ('partitura', 'albornoz'):
        mS = fin(score_tone, ao=0.4, dust=0.5)
        P.append(box((0.5, 15.8, 4.0), (8.0, 15.9, 14.0), mS, rot=rot))
        P.append(box((8.0, 15.8, 4.0), (15.5, 15.9, 14.0), mS, rot=rot))
    if kind == 'albornoz':
        P.append(box((-1.0, 15.9, 3.4), (17.0, 16.0, 6.4), fin(lectern_label_tone('T.ALBORNOZ'), ao=0, dust=0.3), rot=rot))
    else:
        P.append(box((-1.0, 15.9, 3.4), (17.0, 16.0, 6.4), fin(lectern_label_tone(''), ao=0, dust=0.3), rot=rot))
    return P


def reclinatorio_parts():
    """Prie-dieu: the user kneels on the SOUTH side looking north."""
    mW = fin(outline(wood(NOGAL, seed=241, base=4, wear=0.5)))
    mF = fin(panels(wood(NOGAL, seed=243, axis=1, base=3), wood(NOGAL, seed=244, axis=1, base=4),
                    rects=((3, 3, -3, -3),), faces=('south', 'north'), carve=cross_carve))
    mPad = fin(cloth(VELVET_R, base=3, seed=245, folds=0, weave=True, stains=0.3))
    return [
        box((2.0, 0.0, 3.0), (3.4, 14.0, 5.0), mW), box((12.6, 0.0, 3.0), (14.0, 14.0, 5.0), mW),   # uprights
        box((3.4, 2.0, 3.4), (12.6, 13.0, 4.4), mF),                  # front panel
        box((1.6, 13.0, 2.4), (14.4, 14.0, 8.6), mW),                 # arm rest shelf
        box((1.8, 14.0, 7.6), (14.2, 14.6, 8.6), mW),                 # lip
        box((2.0, 0.0, 5.0), (3.4, 1.2, 14.6), mW), box((12.6, 0.0, 5.0), (14.0, 1.2, 14.6), mW),   # runners
        box((2.0, 1.2, 9.0), (14.0, 2.4, 14.6), mW),                  # kneeler
        box((2.3, 2.4, 9.3), (13.7, 3.4, 14.3), mPad),
    ]


# ============================================================================================ register: chapel
F('crucifijo_chico', 'Crucifijo de pared', 'Small wall crucifix', crucifix_small_parts(), env=('wall',), collision='none')
F('crucifijo_grande', 'Crucifijo grande de la capilla', 'Large chapel crucifix', crucifix_big_parts(), env=('wall',),
  collision='none')
F('virgen', 'Virgen de Luján', 'Our Lady of Luján statue', virgin_parts(), sound='stone')
F('santa_ines', 'Santa Inés con el cordero', 'Saint Agnes with the lamb', ines_parts(), sound='stone')
F('santa_ines_cuerpo', 'Santa Inés (sin cabeza)', 'Saint Agnes (headless body)', ines_parts(head=False), sound='stone')
F('santa_ines_cabeza', 'Cabeza de Santa Inés', 'Saint Agnes head (for the turning display)', ines_parts(body=False, head_only=True),
  sound='stone', collision='none')
for _s, _es in (('izq', 'izquierda'), ('centro', 'centro'), ('der', 'derecha')):
    F(f'banco_iglesia_{_s}', f'Banco de capilla ({_es})', f'Chapel pew ({_es})', pew_parts(_s))
    F(f'altar_{_s}', f'Altar con mantel ({_es})', f'Altar with cloth ({_es})', altar_parts(_s), sound='stone')
F('candelabro', 'Candelabro alto encendido', 'Tall candlestick (lit)', candelabro_parts(True), light=13, sound='metal')
F('candelabro_apagado', 'Candelabro alto apagado', 'Tall candlestick (unlit)', candelabro_parts(False), sound='metal')
F('candelero', 'Candelero de altar encendido', 'Altar candlestick (lit)', candelero_altar_parts(True), light=12, sound='metal')
F('candelero_apagado', 'Candelero de altar apagado', 'Altar candlestick (unlit)', candelero_altar_parts(False), sound='metal')
F('velas', 'Velas en el piso encendidas', 'Floor candles (lit)', velas_piso_parts(True), light=11, sound='candle',
  collision='none')
F('velas_apagadas', 'Velas en el piso apagadas', 'Floor candles (unlit)', velas_piso_parts(False), sound='candle',
  collision='none')
for _c, _ce in (('izq', 'izquierda'), ('centro', 'centro'), ('der', 'derecha')):
    for _r, _re in ((0, 'abajo'), (1, 'arriba')):
        F(f'confesionario_{_c}_{_re}', f'Confesionario ({_ce}, {_re})', f'Confessional ({_ce}, {_re})',
          confessional_parts(_c, _r), env=('floor',) if _r == 0 else ())
F('pila_bautismal', 'Pila bautismal', 'Baptismal font', font_parts(), sound='stone')
F('pila_agua_bendita', 'Pila de agua bendita', 'Holy water stoup', stoup_parts(), env=('wall',), sound='stone')
F('lampara_santisimo', 'Lámpara del Santísimo', 'Sanctuary lamp (lit)', sanctuary_lamp_parts(True), env=('ceil',), light=10,
  sound='glass', collision='none')
F('lampara_santisimo_apagada', 'Lámpara del Santísimo apagada', 'Sanctuary lamp (out)', sanctuary_lamp_parts(False),
  env=('ceil',), sound='glass', collision='none')
F('cadena', 'Cadena colgante', 'Hanging chain', chain_parts(), env=(), sound='metal', collision='none', directional=False)
F('armonio_izq', 'Armonio (izquierda)', 'Harmonium (left)', harmonium_parts('izq'))
F('armonio_der', 'Armonio (derecha)', 'Harmonium (right)', harmonium_parts('der'))
F('atril_coro', 'Atril del coro', 'Choir lectern', atril_parts('vacio'))
F('atril_coro_partitura', 'Atril del coro con partitura', 'Choir lectern with score', atril_parts('partitura'))
F('atril_albornoz', 'Atril 8 "T. ALBORNOZ"', 'Choir lectern 8 "T. ALBORNOZ"', atril_parts('albornoz'))
F('reclinatorio', 'Reclinatorio', 'Prie-dieu', reclinatorio_parts())


# ============================================================================================ DORMITORY
TICKING = pal('#1b2338', '#2a3550', '#a9ad9f', '#c9cbbd', '#dddccf')


def ticking_tone(ctx):
    """Old wool mattress cover: blue-grey stripes on off-white."""
    P = tp(ctx)
    u = P[0] if ctx.face in ('north', 'south', 'up', 'down') else P[2]
    if ctx.face in ('north', 'south'):
        u = P[0]
    st = int(u) % 6
    k = 1 if st == 0 else (2 if st == 3 else 3 + (hh(int(u), int(P[1])) > 0.7))
    if ctx.face == 'up':
        k = 3
    return (TICKING, k)


def sheet(seed=0, base=6, axis='i', folds=0.6, px=3.0, stains=0.25):
    return fin(cloth(LINEN, base=base, seed=seed, fold_axis=axis, folds=folds, fold_px=px, stains=stains), ao=0.6, dust=0.5)


def blanket_tone(seed=0):
    """Grey institutional wool blanket with two navy stripes near the edge and a soft nap."""
    def t(ctx):
        P = tp(ctx)
        z = P[2]
        k = 4
        if ctx.face != 'down':
            if (int(P[0]) + int(P[1]) * 2 + int(z)) % 3 == 0:
                k -= 1
            if hh(int(P[0] / 2), int(z / 2), int(P[1] / 2), seed) < 0.12:
                k += 1
        c = T(BLANKET, k)
        zz = (ctx.pos[2] + (16 if ctx.block.key.endswith('_pie') else 0)) * 2
        if 50 <= zz % 64 <= 51 or 54 <= zz % 64 <= 55:
            c = T(NAVY, 3 + (k > 4))
        return c
    return t


def bed_frame(head=True, finial_y=None):
    mP = fin(painted_iron(seed=301, chips=0.32), dust=0.5)
    mPs = fin(painted_iron(seed=303, chips=0.25, base=6), dust=0.4)
    mBr = fin(brass(seed=305, base=5, tarnish=0.5), dust=0.5)
    P = []
    zb = (0.4, 1.6) if head else (14.4, 15.6)
    top = 22.0 if head else 15.0
    for x0 in (0.6, 14.2):
        P.append(box((x0, 0.8, zb[0]), (x0 + 1.2, top, zb[1]), mP))                          # posts
        P.append(box((x0 - 0.15, top, zb[0] - 0.15), (x0 + 1.35, top + 0.5, zb[1] + 0.15), mBr))  # collar
        P.append(box((x0 + 0.05, top + 0.5, zb[0] + 0.05), (x0 + 1.15, top + 1.6, zb[1] - 0.05), mBr))  # ball
        P.append(box((x0 + 0.1, 0.0, zb[0] + 0.1), (x0 + 1.1, 0.8, zb[1] - 0.1), fin(flat(IRON, 2))))   # caster
        P.append(box((x0 + 0.2, 6.0, 0.0 if not head else zb[1]), (x0 + 1.0, 7.2, 16.0 if head else zb[0]), mP))  # side rails
    r1, r2 = (9.4, 10.4), ((top - 1.6), (top - 0.6))
    P.append(box((1.8, r1[0], zb[0] + 0.3), (14.2, r1[1], zb[1] - 0.3), mP))
    P.append(box((1.8, r2[0], zb[0] + 0.3), (14.2, r2[1], zb[1] - 0.3), mP))
    n = 7
    for k in range(n):
        x = 2.6 + k * (10.8 / (n - 1))
        P.append(box((x - 0.3, r1[1], zb[0] + 0.5), (x + 0.3, r2[0], zb[1] - 0.5), mPs))     # spindles
    if head:
        P.append(box((6.0, 17.2, zb[0] + 0.4), (10.0, 18.0, zb[1] - 0.4), mP))                 # decorative arch
        P.append(box((5.4, 16.0, zb[0] + 0.4), (6.2, 18.0, zb[1] - 0.4), mP))
        P.append(box((9.8, 16.0, zb[0] + 0.4), (10.6, 18.0, zb[1] - 0.4), mP))
    return P


def bed_parts(piece, state):
    """piece: 'cabecera' (headboard at the front/z=0) | 'pie'. state: 'hecha' | 'bulto' | 'deshecha'."""
    head = piece == 'cabecera'
    P = bed_frame(head)
    mT = fin(ticking_tone, ao=0.8, dust=0)
    z0, z1 = (1.6, 16.0) if head else (0.0, 14.4)
    P.append(box((1.6, 7.2, z0), (14.4, 9.4, z1), mT))                                          # mattress
    sh = sheet(seed=311 if head else 312)
    shv = sheet(seed=313 if head else 314, axis='i', folds=0.9, px=2.0)
    mBl = fin(blanket_tone(315), ao=0.7, dust=0.6)
    if state == 'hecha':
        P.append(box((1.4, 9.4, z0), (14.6, 9.7, z1), sh))                                      # bottom sheet
        if head:
            P.append(box((2.6, 9.7, 2.2), (13.4, 11.8, 6.4), sheet(seed=316, base=7, folds=0.4, px=4.0)))  # pillow
            P.append(box((1.2, 9.7, 7.0), (14.8, 10.3, 16.0), mBl))                             # blanket
            P.append(box((1.2, 10.3, 7.0), (14.8, 10.6, 9.2), sheet(seed=317, base=7)))           # sheet turned down
            P.append(box((1.0, 5.6, 7.0), (1.2, 10.6, 16.0), mBl, faces=('west', 'east', 'down', 'north')))
            P.append(box((14.8, 5.6, 7.0), (15.0, 10.6, 16.0), mBl, faces=('west', 'east', 'down', 'north')))
        else:
            P.append(box((1.2, 9.7, 0.0), (14.8, 10.3, 14.6), mBl))
            P.append(box((1.0, 5.6, 0.0), (1.2, 10.3, 14.6), mBl, faces=('west', 'east', 'down')))
            P.append(box((14.8, 5.6, 0.0), (15.0, 10.3, 14.6), mBl, faces=('west', 'east', 'down')))
    elif state == 'bulto':
        P.append(box((1.4, 9.4, z0), (14.6, 9.7, z1), sh))
        if head:
            P += [box((2.6, 9.7, 2.2), (13.4, 11.2, 6.4), sheet(seed=316, base=7, folds=0.4, px=4.0)),   # pillow
                  box((5.0, 11.2, 2.4), (11.0, 13.0, 7.0), shv),                                     # the covered head
                  box((5.6, 13.0, 2.8), (10.4, 14.2, 6.6), shv),
                  box((6.4, 14.2, 3.4), (9.6, 14.8, 6.0), shv),
                  box((5.8, 9.7, 6.8), (10.2, 11.6, 8.0), shv),                                      # neck
                  box((2.6, 9.7, 7.8), (13.4, 11.6, 16.0), shv),                                     # shoulders / back
                  box((3.2, 11.6, 8.4), (12.8, 12.8, 16.0), shv),
                  box((4.4, 12.8, 9.4), (11.6, 13.4, 16.0), shv),
                  box((1.0, 6.2, 5.8), (1.4, 11.2, 16.0), shv, faces=('west', 'east', 'down', 'north')),
                  box((14.6, 6.2, 5.8), (15.0, 11.2, 16.0), shv, faces=('west', 'east', 'down', 'north'))]
        else:
            P += [box((2.8, 9.7, 0.0), (13.2, 11.8, 5.0), shv),                                      # hips
                  box((3.6, 11.8, 0.0), (12.4, 12.8, 4.4), shv),
                  box((3.6, 9.7, 5.0), (12.4, 11.2, 11.0), shv),                                     # legs
                  box((4.2, 11.2, 5.0), (7.6, 12.0, 11.0), shv), box((8.4, 11.2, 5.0), (11.8, 12.0, 11.0), shv),
                  box((4.2, 9.7, 11.0), (11.8, 12.6, 12.4), shv),                                    # feet tenting the sheet
                  box((4.6, 12.6, 11.2), (7.2, 13.4, 12.2), shv), box((8.8, 12.6, 11.2), (11.4, 13.4, 12.2), shv),
                  box((4.0, 9.7, 12.4), (12.0, 11.0, 13.4), shv),
                  box((1.2, 9.7, 13.2), (14.8, 11.0, 14.6), mBl),                                    # blanket folded at the foot
                  box((1.0, 6.2, 0.0), (1.4, 11.2, 13.2), shv, faces=('west', 'east', 'down', 'south')),
                  box((14.6, 6.2, 0.0), (15.0, 11.2, 13.2), shv, faces=('west', 'east', 'down', 'south'))]
    else:  # deshecha: sheet rumpled, blanket dragged to the floor
        P.append(box((1.4, 9.4, z0), (14.6, 9.7, z1), sh))
        if head:
            P.append(box((3.0, 9.7, 2.4), (12.0, 11.4, 6.6), sheet(seed=318, base=7, folds=0.5), rot=('y', 22.5, (7.5, 9.7, 4.5))))
            P.append(box((2.0, 9.7, 9.0), (10.0, 11.0, 15.0), shv))                               # rumpled sheet
            P.append(box((4.0, 11.0, 10.0), (8.0, 11.6, 13.0), shv))
        else:
            P.append(box((1.2, 9.7, 0.0), (9.0, 10.4, 8.0), mBl))
            P.append(box((14.8, 0.0, 0.0), (15.4, 10.4, 12.0), mBl, faces=('west', 'east', 'north', 'south')))   # hanging
            P.append(box((15.2, 0.0, 0.0), (19.0, 0.6, 12.0), mBl))                                # pooled on the floor
            mSh = fin(painted(BAKE, base=3, seed=319, wear=0.5))
            P += [box((4.0, 0.0, 15.2), (5.6, 1.4, 18.8), mSh), box((6.2, 0.0, 15.0), (7.8, 1.4, 18.6), mSh),   # guillerminas
                  box((4.0, 1.0, 15.6), (5.6, 1.2, 16.0), mSh), box((6.2, 1.0, 15.4), (7.8, 1.2, 15.8), mSh)]
    return P


def baul_parts():
    """Pupil's trunk at the foot of the bed: planked pine body, iron bands and corners, brass lock, leather handles."""
    mW = fin(panels(wood(PINO, seed=321, base=3, axis=0, boards=(1, 5)), rects=((2, 2, -2, -2),), faces=('north', 'south'),
                    groove=False, bevel=0))
    mL = fin(wood(PINO, seed=323, base=3, axis=0, boards=(2, 6)))
    mI = fin(iron(seed=325, rust=0.45))
    mLe = fin(painted(LEATHER_B, base=3, seed=327, wear=0.4))
    P = [
        box((1.2, 0.8, 3.6), (14.8, 7.2, 12.4), mW),                 # body
        box((1.0, 7.2, 3.4), (15.0, 9.0, 12.6), mL),                 # lid
        box((1.4, 9.0, 4.2), (14.6, 9.6, 11.8), mL),                 # lid dome
        box((1.0, 0.0, 3.4), (2.6, 0.8, 5.0), mI), box((13.4, 0.0, 3.4), (15.0, 0.8, 5.0), mI),   # feet
        box((1.0, 0.0, 11.0), (2.6, 0.8, 12.6), mI), box((13.4, 0.0, 11.0), (15.0, 0.8, 12.6), mI),
        box((6.9, 4.4, 3.2), (9.1, 7.6, 3.6), M_BRASS),              # lock plate
        box((7.8, 5.2, 3.1), (8.2, 6.0, 3.2), fin(flat(IRON, 0), ao=0)),
        box((-0.2, 4.8, 6.6), (1.2, 5.6, 9.4), mLe), box((14.8, 4.8, 6.6), (16.2, 5.6, 9.4), mLe),   # handles
    ]
    for x in (3.4, 12.0):  # iron bands wrapping body and lid
        P.append(box((x, 0.8, 3.4), (x + 0.6, 7.2, 3.6), mI))
        P.append(box((x, 0.8, 12.4), (x + 0.6, 7.2, 12.6), mI))
        P.append(box((x, 7.2, 3.2), (x + 0.6, 9.0, 3.4), mI))
        P.append(box((x, 9.0, 4.0), (x + 0.6, 9.8, 12.0), mI))
    for (x, z) in ((1.0, 3.4), (14.4, 3.4), (1.0, 12.0), (14.4, 12.0)):   # corner brackets
        P.append(box((x, 6.0, z), (x + 0.6, 9.2, z + 0.6), mI))
    return P


def mesita_parts(bell=False):
    mW = fin(outline(wood(PINO, seed=331, base=4, worn_pal=RAW, wear=0.5)))
    mF = fin(panels(wood(PINO, seed=333, base=4, axis=1), rects=((2, 2, -2, -2),), faces=('north',)))
    mD = fin(panels(wood(PINO, seed=334, base=4, axis=0), rects=((1, 1, -1, -1),), faces=('north',), bevel=0))
    P = []
    for (x, z) in ((3.0, 3.0), (11.8, 3.0), (3.0, 11.8), (11.8, 11.8)):
        P.append(box((x, 0.0, z), (x + 1.2, 3.0, z + 1.2), mW))
        P.append(box((x + 0.2, 1.2, z + 0.2), (x + 1.0, 1.8, z + 1.0), mW))
    P += [
        box((3.0, 3.0, 3.0), (13.0, 11.0, 13.0), mF),                # carcass (door on the front)
        box((3.4, 8.4, 2.6), (12.6, 10.6, 3.0), mD),                 # drawer
        box((7.4, 9.2, 2.2), (8.6, 9.8, 2.6), M_BRASS),
        box((10.6, 5.2, 2.6), (11.2, 6.4, 3.0), M_BRASS),            # door knob
        box((2.6, 11.0, 2.6), (13.4, 12.0, 13.4), fin(wood(PINO, seed=335, base=4, boards=(2, 10)))),
    ]
    if bell:
        mB = fin(brass(seed=337, base=4), dust=0.4)
        mH = fin(painted(BAKE, base=4, seed=338, wear=0.4))
        P += [
            box((8.2, 12.0, 7.4), (11.8, 12.5, 11.0), mB),            # bell rim
            box((8.6, 12.5, 7.8), (11.4, 13.8, 10.6), mB),
            box((9.1, 13.8, 8.3), (10.9, 14.4, 10.1), mB),
            box((9.6, 14.4, 8.8), (10.4, 16.6, 9.6), mH),             # wooden handle
            box((9.4, 16.6, 8.6), (10.6, 17.4, 9.8), mH),
        ]
        P += [box((3.8, 12.0, 4.0), (7.0, 12.4, 7.2), fin(flat(ENAMEL, 5)))]     # saucer
        P += candle(5.4, 5.6, 12.4, 14.6, r=0.6, lit=False, seed=339)
        # a rosary coiled on the top
        mR = fin(flat(BAKE, 4), ao=0, dust=0.2)
        for k in range(9):
            a = k / 9 * 6.28
            P.append(box((4.6 + math.cos(a) * 1.6, 12.0, 9.6 + math.sin(a) * 1.4), (5.1 + math.cos(a) * 1.6, 12.4, 10.1 + math.sin(a) * 1.4), mR))
        P.append(box((6.2, 12.0, 11.0), (6.6, 12.3, 12.6), fin(flat(NICKEL, 5), ao=0)))
    return P


def curtain_tone(ctx):
    """White cotton curtain: translucent-ish with deep vertical folds, dirty hem, a few holes."""
    i, j, w, h = ctx.i, ctx.j, ctx.w, ctx.h
    P = tp(ctx)
    u = P[0] + 0.5
    v = math.sin(u / 2.4 * 2.1 + 0.6 * math.sin(u / 7.0))
    k = 6 + (1 if v > 0.5 else (-1 if v < -0.4 else 0)) - (1 if v < -0.85 else 0)
    c = T(LINEN, k)
    if j > h - 6:
        c = mix(c, hx('#7a6c58'), 0.12 * (j - (h - 6)))
    if hh(i // 2, j // 3, 9) < 0.006:
        return None
    n = vn(P[0] / 6.0, P[1] / 6.0, 0.4, 341)
    if n > 0.74:
        c = mix(c, hx('#a8946a'), 0.25)
    return (c[0], c[1], c[2], 224)


def cortina_parts():
    mR = fin(iron(seed=343, rust=0.3), dust=0.5)
    P = [box((0.0, 1.0, 7.7), (16.0, 30.0, 8.3), curtain_tone, faces=('north', 'south', 'down')),
         box((-0.2, 30.6, 7.6), (16.2, 31.2, 8.4), mR)]
    for x in (1.0, 5.0, 9.0, 13.0):
        P.append(box((x, 29.6, 7.5), (x + 1.2, 31.6, 8.5), mR, faces=('north', 'south', 'west', 'east')))
    return P


def rush_tone(ctx):
    """Esterilla (woven rush seat): diagonal over-under weave converging to the centre."""
    if ctx.face != 'up':
        return (RUSH, 3)
    i, j, w, h = ctx.i, ctx.j, ctx.w, ctx.h
    x, y = i - w / 2 + 0.5, j - h / 2 + 0.5
    quad = abs(x) > abs(y)
    a = (int(abs(y) if quad else abs(x)) + (i + j)) % 4
    k = 4 + (1 if a < 2 else -1)
    if abs(abs(x) - abs(y)) < 0.8:
        k = 2
    if ctx.edge() == 0:
        k = 3
    return (RUSH, k)


def silla_monja_parts(raise_=0.0):
    """The celadora's chair: tall spindle back with a cut cross, rush seat, turned legs (sitter looks north)."""
    mW = fin(outline(wood(NOGAL, seed=351, base=4, worn_pal=RAW, wear=0.5)))
    mT = fin(wood(NOGAL, seed=353, base=5))
    P = []
    for (x, z, top) in ((2.6, 2.6, 7.6), (12.2, 2.6, 7.6), (2.6, 12.2, 27.0), (12.2, 12.2, 27.0)):
        P.append(box((x, 0.0, z), (x + 1.2, top, z + 1.2), mW))
        for y in (2.0, 5.0):
            P.append(box((x - 0.2, y, z - 0.2), (x + 1.4, y + 0.8, z + 1.4), mT))     # turned rings
        if top > 20:
            P.append(box((x - 0.1, top, z - 0.1), (x + 1.3, top + 1.2, z + 1.3), mT))  # finial
    P += [
        box((3.8, 2.8, 3.0), (12.2, 3.4, 3.8), mW), box((3.8, 2.8, 12.4), (12.2, 3.4, 13.2), mW),   # stretchers
        box((3.0, 3.4, 3.8), (3.6, 4.0, 12.2), mW), box((12.4, 3.4, 3.8), (13.0, 4.0, 12.2), mW),
        box((2.4, 7.0, 2.4), (13.6, 7.6, 13.6), mW),                 # seat frame
        box((3.0, 7.6, 3.0), (13.0, 8.2, 13.0), fin(rush_tone, ao=0.8, dust=0.7)),   # rush seat
        box((3.8, 12.0, 12.4), (12.2, 13.0, 13.2), mW),              # back rails
        box((3.8, 22.2, 12.2), (12.2, 25.4, 13.4), fin(panels(wood(NOGAL, seed=355, base=4, axis=0), rects=((1, 1, -1, -1),),
            faces=('north', 'south'), bevel=0, carve=lambda c, di, dj, w, h: -4 if (abs(di - w / 2 + 0.5) < 1 and 1 <= dj <= h - 2)
            or (dj == 2 and abs(di - w / 2 + 0.5) < 3) else 0))),   # crest rail with a cut cross
    ]
    for x in (5.4, 7.6, 9.8):
        P.append(box((x, 13.0, 12.5), (x + 0.8, 22.2, 13.1), mW))   # spindles
    if raise_:
        shift(P, dy=raise_)
    return P


def mirror_tone(cracked=False, seed=0):
    """Old mirror: dark cool reflection, diagonal sheen streaks, black silvering loss at the edges."""
    def t(ctx):
        i, j, w, h = ctx.i, ctx.j, ctx.w, ctx.h
        if ctx.face not in ('north',):
            return (NICKEL, 3)
        u = (i + j * 0.6)
        k = 3 + (1 if j < h * 0.4 else 0)
        if 6 < (u % 23) < 9:
            k += 2
        elif 9 <= (u % 23) < 10:
            k += 1
        e = min(i, j, w - 1 - i, h - 1 - j)
        n = vn(i / 3.0, j / 3.0, seed * 0.1, seed + 361)
        if e < 3 and n > 0.45 + e * 0.12:
            return (MIRROR, 0 if hh(i, j) < 0.6 else 1)            # desilvering
        if hh(i // 2, j // 2, seed) < 0.015:
            return (MIRROR, 1)
        c = T(MIRROR, k)
        if cracked:
            cx, cy = w * 0.55, h * 0.42
            dx, dy = i + 0.5 - cx, j + 0.5 - cy
            a = math.atan2(dy, dx)
            r = math.hypot(dx, dy)
            spokes = (a / (2 * math.pi) * 9 + 0.5) % 1.0
            wob = vn(r / 3.0, a * 2, 0.0, seed + 5) * 0.12
            if r < 1.5 or (abs(spokes - 0.5 + wob) < 0.06 and r < max(w, h) * 0.8) or (abs(r - 4.5) < 0.5 and spokes < 0.7) \
                    or (abs(r - 9) < 0.5 and 0.2 < spokes < 0.6):
                return T(MIRROR, 9) if hh(i, j, 3) < 0.5 else T(MIRROR, 0)
        return c
    return t


def ropero_parts(half):
    """Wardrobe 2 blocks tall (inf/sup): two doors (left with a mirror), drawer below, cornice. Front faces north."""
    yo = 0 if half == 'inf' else 16
    off = (0, yo, 0)
    wd = lambda sd, **kw: wood(NOGAL, seed=371 + sd, off=off, worn_pal=RAW, **kw)
    mC = fin(panels(wd(0, base=3, axis=1), wd(1, base=4, axis=1), rects=((3, 3, -3, -3),), faces=('west', 'east')))
    mW = fin(wd(2, base=4))

    def door_tone(mirror):
        inner = wd(3 if mirror else 4, base=4, axis=1)
        fr = wd(5, base=4, axis=1)

        def t(ctx):
            if ctx.face != 'north':
                return fr(ctx)
            Y = int((ctx.pos[1] + yo - 5.6) * 2)       # door-local row from the bottom (door y 5.6 .. 30.4 overall)
            Hd = int((30.4 - 5.6) * 2)
            j = Hd - 1 - Y
            i, w = ctx.i, ctx.w
            # upper panel (mirror or wood) rows 3..28, lower panel rows 32..Hd-4
            for (a, b) in ((3, 29), (32, Hd - 3)):
                if 2 <= i < w - 2 and a <= j < b:
                    di, dj, ei, ej = i - 2, j - a, w - 3 - i, b - 1 - j
                    m = min(di, dj, ei, ej)
                    if m == 0:
                        return (NOGAL, 1)
                    if mirror and a == 3:
                        return None   # the mirror plate is a separate part
                    pl, k = inner(ctx)
                    if m == 1:
                        k += 1 if (dj == m or di == m) else -1
                    return (pl, k)
            return fr(ctx)
        return t
    P = []
    if half == 'inf':
        P += [
            box((0.6, 0.0, 2.2), (2.2, 2.0, 3.8), mW), box((13.8, 0.0, 2.2), (15.4, 2.0, 3.8), mW),   # bun feet
            box((0.6, 0.0, 13.0), (2.2, 2.0, 14.6), mW), box((13.8, 0.0, 13.0), (15.4, 2.0, 14.6), mW),
            box((0.4, 2.0, 2.0), (15.6, 3.0, 15.0), mW),                                          # plinth
            box((0.8, 3.0, 2.6), (15.2, 16.0, 14.8), mC),                                         # carcass
            box((1.2, 3.2, 2.2), (14.8, 5.4, 2.6), fin(panels(wd(6, base=4, axis=0), rects=((1, 1, -1, -1),), faces=('north',), bevel=0))),   # drawer
            box((4.4, 4.0, 1.8), (5.6, 4.6, 2.2), M_BRASS), box((10.4, 4.0, 1.8), (11.6, 4.6, 2.2), M_BRASS),
        ]
    else:
        P += [
            box((0.8, 0.0, 2.6), (15.2, 14.4, 14.8), mC),
            box((0.2, 14.4, 1.8), (15.8, 15.2, 15.2), mW),                                       # cornice
            box((-0.2, 15.2, 1.2), (16.2, 16.0, 15.4), fin(wd(7, base=5, axis=0))),
        ]
    y0, y1 = (5.6, 16.0) if half == 'inf' else (0.0, 14.4)
    P.append(box((1.2, y0, 2.2), (8.0, y1, 2.6), fin(door_tone(True))))
    P.append(box((8.0, y0, 2.2), (14.8, y1, 2.6), fin(door_tone(False))))
    if half == 'inf':
        P.append(box((7.2, 11.0, 1.8), (7.7, 12.6, 2.2), M_BRASS))      # door handles + keyhole
        P.append(box((8.3, 11.0, 1.8), (8.8, 12.6, 2.2), M_BRASS))
        P.append(box((8.4, 10.0, 2.15), (8.7, 10.6, 2.2), fin(flat(IRON, 0), ao=0)))
        P.append(box((2.2, 7.6, 2.4), (7.0, 16.0, 2.4), fin(mirror_tone(seed=1), ao=0, dust=0), faces=('north',)))
    else:
        P.append(box((2.2, 0.0, 2.4), (7.0, 13.0, 2.4), fin(mirror_tone(seed=2), ao=0, dust=0), faces=('north',)))
    return P


# ============================================================================================ register: dormitory
for _st, _es, _en in (('', 'Cama de hierro', 'Iron bed'), ('_bulto', 'Cama con bulto bajo la sábana', 'Iron bed with a shape under the sheet'),
                      ('_deshecha', 'Cama de hierro deshecha', 'Unmade iron bed')):
    _state = {'': 'hecha', '_bulto': 'bulto', '_deshecha': 'deshecha'}[_st]
    F(f'cama{_st}_cabecera', f'{_es} (cabecera)', f'{_en} (head)', bed_parts('cabecera', _state), sound='metal')
    F(f'cama{_st}_pie', f'{_es} (pie)', f'{_en} (foot)', bed_parts('pie', _state), sound='metal')
F('baul', 'Baúl', 'Wooden trunk', baul_parts())
F('mesita_luz', 'Mesita de luz', 'Nightstand', mesita_parts())
F('mesita_luz_campanita', 'Mesita de luz con campanita', 'Nightstand with hand bell', mesita_parts(True))
F('cortina_blanca', 'Cortina blanca', 'White curtain', cortina_parts(), render='translucent', collision='none', sound='cloth')
F('silla_monja', 'Silla de la celadora', "Nun's chair", silla_monja_parts())
F('ropero_abajo', 'Ropero con espejo (abajo)', 'Wardrobe with mirror (bottom)', ropero_parts('inf'))
F('ropero_arriba', 'Ropero con espejo (arriba)', 'Wardrobe with mirror (top)', ropero_parts('sup'), env=())


# ============================================================================================ REFECTORY
def table_top_tone(seed, off):
    """Scrubbed pine refectory top: worn pale centre, knife cuts, soup/wine rings."""
    base = wood(PINO, seed=seed, base=5, axis=0, boards=(2, 7), off=off, wear=0.6, knots=0.3)
    rings = [(hh(seed, n, 1) * 32 + off[0] * 2, hh(seed, n, 2) * 26 + 3, 2.2 + hh(seed, n, 3) * 1.6) for n in range(2)]

    def t(ctx):
        r = base(ctx)
        if ctx.face != 'up':
            return r
        X, Z = ctx.pos[0] * 2 + off[0] * 2, ctx.pos[2] * 2
        for (cx, cz, rr) in rings:
            d = math.hypot(X - cx, Z - cz)
            if abs(d - rr) < 0.5 and hh(int(X), int(Z)) < 0.8:
                return (PINO, r[1] - 2)
        if hh(int(X) // 3, int(Z), seed, 5) < 0.02:
            return (PINO, r[1] + 2)                  # knife cuts
        return r
    return t


def mesa_larga_parts(kind):
    """Long refectory table segment (long axis = x). kind: 'extremo' (legs at x=0 end), 'centro', 'puesta'."""
    off = (0, 0, 0) if kind == 'extremo' else (16, 0, 0)
    mTop = fin(table_top_tone(401, off))
    mW = fin(wood(PINO, seed=403, base=4, off=off, wear=0.4))
    mL = fin(outline(wood(PINO, seed=405, base=3, axis=1)))
    x0 = 0.4 if kind == 'extremo' else 0.0
    P = [
        box((x0, 11.0, 0.8), (16, 12.0, 15.2), mTop),
        box((x0 + 0.8, 9.4, 1.6), (16, 11.0, 2.2), mW), box((x0 + 0.8, 9.4, 13.8), (16, 11.0, 14.4), mW),   # aprons
        box((x0 + 0.8, 2.2, 7.4), (16, 3.0, 8.6), mW),                                                    # long stretcher
    ]
    if kind == 'extremo':
        P.append(box((1.2, 9.4, 2.2), (1.8, 11.0, 13.8), mW))
        for z in (1.8, 12.8):
            P += [box((1.3, 0.0, z), (2.7, 9.4, z + 1.4), mL),
                  box((1.1, 6.0, z - 0.2), (2.9, 7.0, z + 1.6), mL), box((1.1, 2.6, z - 0.2), (2.9, 3.4, z + 1.6), mL),
                  box((1.0, 0.0, z - 0.3), (3.0, 0.6, z + 1.7), mL)]
        P.append(box((1.6, 2.2, 3.2), (2.4, 3.0, 12.8), mW))
    if kind == 'puesta':
        P += place_setting(3.5, 1.4, north=True) + place_setting(9.0, 9.0, north=False)
    return P


def enamel_tone(rim_rows=1, inside=False, seed=0, soot=False):
    """White enamel with a navy rim, black chips showing iron, soot at the bottom."""
    def t(ctx):
        P = tp(ctx)
        if ctx.face == 'up' and inside:
            d = max(abs(ctx.s - 0.5), abs(ctx.t - 0.5)) * 2
            if d > 0.82:
                return (EBLUE, 3)
            return (ENAMEL, 3 if d > 0.55 else 2)
        if ctx.face not in ('up', 'down') and ctx.j < rim_rows:
            return (EBLUE, 3 - (hh(ctx.i, seed) < 0.15))
        if vn(P[0] / 2.0, P[1] / 2.0, P[2] / 2.0, seed + 411) > 0.8:
            return (IRON, 1)
        k = 5 + (1 if 0.3 < ctx.s < 0.5 else 0)
        if soot and ctx.face not in ('up',) and ctx.j > ctx.h - 3:
            return (BAKE, 3 + (hh(ctx.i, ctx.j) > 0.5))
        return (ENAMEL, k)
    return t


def plate_tone(seed=0):
    def t(ctx):
        if ctx.face != 'up':
            return (ENAMEL, 4) if ctx.face != 'down' else (EBLUE, 2)
        d = max(abs(ctx.s - 0.5), abs(ctx.t - 0.5)) * 2
        if d > 0.86:
            return (EBLUE, 3)
        if hh(ctx.i, ctx.j, seed) < 0.03:
            return (IRON, 1)
        return (ENAMEL, 5 if d > 0.6 else 6)
    return t


def place_setting(x, z, north=True, y=12.0):
    """Enamel plate + bowl, spoon, fork and a tin mug, laid toward the sitter (north or south side)."""
    mPl = fin(plate_tone(x), ao=0.3, dust=0.6)
    mBo = fin(enamel_tone(1, inside=True, seed=int(x * 7)), ao=0.4, dust=0.5)
    mNi = fin(brass(NICKEL, base=5, seed=int(x)), ao=0.2, dust=0.4)
    mMug = fin(enamel_tone(1, inside=True, seed=int(x * 3) + 1), ao=0.4, dust=0.5)
    P = [box((x, y, z), (x + 5.0, y + 0.4, z + 5.0), mPl),
         box((x + 1.2, y + 0.4, z + 1.2), (x + 3.8, y + 1.8, z + 3.8), mBo),
         box((x + 5.6, y, z + 0.8), (x + 6.0, y + 0.15, z + 4.0), mNi), box((x + 5.45, y, z + 0.3), (x + 6.15, y + 0.2, z + 1.2), mNi),
         box((x - 1.0, y, z + 0.8), (x - 0.6, y + 0.15, z + 4.0), mNi), box((x - 1.15, y, z + 0.3), (x - 0.45, y + 0.2, z + 1.0), mNi)]
    mz = z + (0.4 if north else 3.0)
    P += [box((x + 6.6, y, mz), (x + 8.4, y + 2.2, mz + 1.8), mMug),
          box((x + 8.4, y + 0.6, mz + 0.6), (x + 8.9, y + 1.8, mz + 1.2), fin(enamel_tone(0, seed=3), ao=0))]
    return P


def banco_largo_parts(kind):
    """Long bench segment; the sitter looks north (toward the table). kind: 'extremo' | 'centro'."""
    off = (0, 0, 0) if kind == 'extremo' else (16, 0, 0)
    mS = fin(wood(PINO, seed=421, base=4, axis=0, off=off, worn_pal=RAW, wear=0.6, boards=(2, 7)))
    mW = fin(outline(wood(PINO, seed=423, base=3)))
    x0 = 0.4 if kind == 'extremo' else 0.0
    P = [box((x0, 7.0, 1.6), (16, 8.0, 8.6), mS),
         box((x0 + 1.0, 6.0, 2.2), (16, 7.0, 2.8), mW), box((x0 + 1.0, 6.0, 7.4), (16, 7.0, 8.0), mW),
         box((x0 + 1.6, 2.6, 4.6), (16, 3.4, 5.6), mW)]
    if kind == 'extremo':
        P += [box((1.2, 3.8, 2.0), (2.4, 7.0, 8.2), mW),
              box((1.2, 0.0, 2.0), (2.4, 3.8, 3.6), mW), box((1.2, 0.0, 6.6), (2.4, 3.8, 8.2), mW)]
    return P


def candelero_mesa_parts(lit):
    P = candelero_altar_parts(lit)
    return shift(P, dy=-4.0)


def stack_plates_parts():
    P = []
    mPl = fin(plate_tone(5), ao=0.5, dust=0.7)
    for n in range(6):
        P.append(box((3.0 + (n % 2) * 0.2, -4.0 + n * 0.45, 3.0), (8.0 + (n % 2) * 0.2, -3.6 + n * 0.45, 8.0), mPl))
    mBo = fin(enamel_tone(1, inside=True, seed=9), ao=0.5, dust=0.7)
    for n in range(3):
        P.append(box((9.0, -4.0 + n * 1.0, 6.0), (12.4, -2.9 + n * 1.0, 9.4), mBo))
    mNi = fin(brass(NICKEL, base=5, seed=11), ao=0.3, dust=0.5)
    for n in range(4):
        P.append(box((4.0 + n * 0.8, -4.0, 10.0), (4.4 + n * 0.8, -3.85, 14.0), mNi))
    return P


def libro_parts(y, rot):
    """Big open book (Vidas de Santas) for the reading lectern."""
    mPg = fin(score_book_tone, ao=0.4, dust=0.6)
    mC = fin(painted(LEATHER_B, base=3, seed=431, wear=0.5))
    return [box((0.6, y, 4.0), (15.4, y + 0.5, 14.0), mC, rot=rot),
            box((1.2, y + 0.5, 4.4), (8.0, y + 1.3, 13.6), mPg, rot=rot),
            box((8.0, y + 0.5, 4.4), (14.8, y + 1.3, 13.6), mPg, rot=rot),
            box((7.6, y + 1.3, 8.0), (8.2, y + 1.35, 14.6), fin(flat(VELVET_R, 5), ao=0), rot=rot)]   # ribbon


def score_book_tone(ctx):
    if ctx.face != 'up':
        return (PAPER, 5 if ctx.j % 2 else 6)
    i, j, w = ctx.i, ctx.j, ctx.w
    if j in (2, 3) and 2 <= i < w - 2:
        return INK_RED if (i // 2) % 2 == 0 else (PAPER, 6)       # rubric heading
    if j > 4 and j % 2 == 1 and 1 < i < w - 2 and hh(i // 3, j, 7) > 0.18:
        return mix(T(PAPER, 6), INK, 0.6)
    return (PAPER, 7 - (ctx.edge() == 0))


def atril_lectura_parts():
    P = [p for p in atril_parts('vacio') if p.size()[0] < 19]
    P += libro_parts(15.8, ('x', 22.5, (8.0, 15.0, 9.0)))
    return P


# ============================================================================================ KITCHEN
def stove_top_tone(ctx):
    """Cast-iron hob: concentric removable rings, soot and rust bloom."""
    if ctx.face != 'up':
        return None
    X = ctx.pos[0] * 2 + (32 if ctx.block.key.endswith('_der') else 0)
    Z = ctx.pos[2] * 2
    k = 2
    for (cx, cz, r) in ((16, 15, 8.5), (40, 13, 7.0)):
        d = math.hypot(X - cx, Z - cz)
        if d < r:
            if abs(d - r + 0.5) < 0.6 or abs(d - r * 0.6) < 0.5 or abs(d - r * 0.25) < 0.5:
                return (IRON, 0)
            k = 3 if d < r * 0.25 else 2
    if hh(int(X), int(Z), 5) < 0.04:
        return (RUST, 2)
    return (IRON, k)


def stove_parts(side):
    """Cocina económica (cast-iron wood stove, 2 blocks). Front faces north; top at 12/16."""
    mI = fin(iron(seed=441, rust=0.3, base=2))
    mIt = fin(lambda c: stove_top_tone(c) or iron(seed=442, base=2)(c), ao=0.4, dust=0.8)
    mN = fin(brass(NICKEL, base=5, seed=443), dust=0.5)
    mDoor = fin(panels(iron(seed=444, base=3, rust=0.2), rects=((2, 2, -2, -2),), faces=('north',)))
    x0, x1 = (0.4, 16.0) if side == 'izq' else (0.0, 15.6)
    P = [
        box((x0 + 0.4, 1.6, 2.0), (x1 - (0.4 if side == 'der' else 0), 11.2, 15.0), mI),    # body
        box((x0, 11.2, 1.4), (x1, 12.0, 15.6), mIt),                                         # hob
        box((x0, 10.6, 1.4), (x1, 11.2, 2.0), mN),                                           # nickel trim band
        box((x0, 9.4, 0.2), (x1, 9.9, 0.7), mN),                                             # towel rail
    ]
    lx = 1.4 if side == 'izq' else 14.0
    P += [box((lx, 0.0, 2.4), (lx + 1.4, 1.6, 3.8), mI), box((lx, 0.0, 13.0), (lx + 1.4, 1.6, 14.4), mI),
          box((lx + 0.4, 9.4, 0.7), (lx + 1.0, 9.9, 2.0), mN)]
    if side == 'izq':
        P += [box((2.4, 5.6, 1.6), (8.6, 10.0, 2.0), mDoor),                                 # firebox door
              box((3.4, 7.6, 1.2), (7.6, 8.2, 1.6), mN),                                     # draught slider
              box((2.4, 2.2, 1.6), (8.6, 5.0, 2.0), mDoor),                                  # ash drawer
              box((4.6, 3.4, 1.2), (6.4, 3.9, 1.6), mN),
              box((9.4, 2.2, 1.6), (15.6, 10.0, 2.0), mDoor),                                # warming oven
              box((10.0, 6.0, 1.2), (11.0, 6.6, 1.6), mN),
              box((5.0, 12.0, 10.6), (9.0, 32.0, 14.6), fin(iron(seed=446, rust=0.4, base=2))),   # flue pipe
              box((4.6, 22.0, 10.2), (9.4, 22.8, 15.0), mI),                                 # pipe collar
              box((9.0, 24.6, 12.3), (10.6, 25.2, 12.9), mN)]                                # damper key
        # dented aluminium kettle (pava) on the hob
        mA = fin(brass(NICKEL, base=4, seed=447, tarnish=0.5))
        P += [box((10.0, 12.0, 5.0), (14.4, 15.2, 9.4), mA), box((10.6, 15.2, 5.6), (13.8, 15.8, 8.8), mA),
              box((11.6, 15.8, 6.6), (12.8, 16.4, 7.8), fin(painted(BAKE, base=3, seed=448))),
              box((8.0, 13.2, 6.8), (10.0, 14.0, 7.6), mA, rot=('z', 45, (10.0, 13.6, 7.2))),          # spout
              box((11.9, 15.8, 4.8), (12.5, 17.8, 9.6), fin(painted(BAKE, base=2, seed=449)))]         # handle
    else:
        P += [box((1.0, 2.2, 1.6), (13.0, 10.0, 2.0), mDoor),                                # oven door
              box((3.0, 8.6, 1.0), (11.0, 9.1, 1.6), mN),                                    # handle bar
              box((6.3, 5.0, 1.2), (7.7, 6.4, 1.6), fin(flat(ENAMEL, 6), ao=0)),             # thermometer dial
              box((6.9, 5.6, 1.15), (7.1, 6.3, 1.2), fin(flat(INK and BAKE, 2), ao=0))]
    return P


def olla_parts(y=-4.0, big=False):
    mE = fin(enamel_tone(1, seed=451, soot=True), ao=0.5, dust=0.6)
    mL = fin(enamel_tone(0, seed=452), ao=0.4, dust=0.8)
    mK = fin(painted(BAKE, base=3, seed=453))
    s = 1.0 if not big else 1.3
    a, b = 8 - 4.5 * s, 8 + 4.5 * s
    P = [box((a, y, a), (b, y + 6.0 * s, b), mE),
         box((a - 0.3, y + 6.0 * s, a - 0.3), (b + 0.3, y + 6.5 * s, b + 0.3), fin(flat(EBLUE, 3))),
         box((a + 0.3, y + 6.5 * s, a + 0.3), (b - 0.3, y + 6.9 * s, b - 0.3), mL),
         box((7.3, y + 6.9 * s, 7.3), (8.7, y + 7.8 * s, 8.7), mK),
         box((a - 1.3, y + 4.4 * s, 7.2), (a, y + 5.0 * s, 8.8), mK), box((b, y + 4.4 * s, 7.2), (b + 1.3, y + 5.0 * s, 8.8), mK)]
    return P


def ollas_piso_parts():
    mA = fin(brass(NICKEL, base=4, seed=461, tarnish=0.6), dust=0.8)
    P = [box((1.6, 0.0, 2.4), (10.4, 8.0, 11.2), mA),                # big aluminium stock pot
         box((1.3, 8.0, 2.1), (10.7, 8.6, 11.5), mA),
         box((0.4, 6.0, 6.0), (1.6, 6.6, 7.6), mA), box((10.4, 6.0, 6.0), (11.6, 6.6, 7.6), mA)]
    P += shift(olla_parts(0.0), dx=4.0, dz=4.0)[:0]
    P += shift(olla_parts(8.6), dx=-2.0, dz=-1.2)                     # smaller pot stacked on top
    mLa = fin(brass(NICKEL, base=5, seed=463))
    P += [box((11.8, 0.0, 10.0), (15.2, 1.6, 13.4), fin(enamel_tone(1, inside=True, seed=7), ao=0.4)),   # basin
          box((12.4, 1.6, 11.4), (12.9, 9.5, 11.9), mLa, rot=('z', -22.5, (12.6, 1.6, 11.6)))]           # ladle
    return P


def key_shape(kind):
    """Pixel art of hanging keys (cutout). kind: 'hierro' | 'bronce' | 'etiqueta'."""
    rows = {
        'hierro': ['.###.', '#...#', '#...#', '.###.', '..#..', '..#..', '..#..', '..#..', '..###', '..#..', '..##.'],
        'bronce': ['.###.', '#.#.#', '.###.', '..#..', '..#..', '..#..', '..##.', '..#..', '..##.'],
    }[kind if kind != 'etiqueta' else 'hierro']
    return rows


def key_tone(kind, tag=None):
    rows = key_shape(kind)
    p = IRON if kind != 'bronce' else BRASS

    def t(ctx):
        i, j = ctx.i, ctx.j
        if tag and j >= 11:
            jj = j - 11
            if 0 <= jj < 6 and 0 <= i < ctx.w:
                if (jj, i) in ((2, 1), (2, 2), (2, 3), (3, 1), (3, 3)):
                    return INK if tag != 'red' else INK_RED
                return T(PAPER, 6 - (jj == 5)) if tag != 'red' else T(VELVET_R, 6)
        if j < len(rows) and i < len(rows[0]) and rows[j][i] == '#':
            return T(p, 6 if (i + j) % 3 == 0 else 4)
        if tag and j == 10 and i == 2:
            return T(PAPER, 3)
        return None
    return t


def tablero_llaves_parts(missing=False):
    mB = fin(panels(wood(PINO, seed=471, base=4, axis=0, boards=(1, 7)), rects=((1, 1, -1, -1),), faces=('north',), bevel=0))
    mT = fin(wood(PINO, seed=473, base=5, axis=0))
    mH = fin(brass(seed=475, base=4, sheen=False))
    P = [box((1.0, 2.0, 15.0), (15.0, 14.0, 16.0), mB),
         box((0.6, 14.0, 14.2), (15.4, 15.0, 16.0), mT),             # little roof
         box((7.4, 15.0, 15.4), (8.6, 15.8, 16.0), M_IRON)]
    n = 0
    for r, y in enumerate((12.0, 8.4, 4.8)):
        for c, x in enumerate((3.0, 6.4, 9.8, 13.0)):
            P.append(box((x - 0.3, y, 14.2), (x + 0.3, y + 0.5, 15.0), mH))            # hook
            P.append(box((x - 0.3, y + 0.5, 14.2), (x + 0.3, y + 0.9, 14.6), mH))
            lab = fin(lambda ctx, n=n: (PAPER, 6) if ctx.edge() else (PAPER, 4), ao=0)
            P.append(box((x - 0.9, y - 3.4, 14.95), (x + 0.9, y - 2.8, 15.0), lab, faces=('north',)))  # paper labels
            key_ = (r, c)
            if key_ == (0, 2):         # the office key: brass with a red tag
                if not missing:
                    P.append(plane((x - 1.25, y - 8.4, 14.5), (x + 1.25, y + 0.4, 14.5), key_tone('bronce', 'red')))
                n += 1
                continue
            if hh(r, c, 3) < 0.25:
                n += 1
                continue
            kind = 'hierro' if hh(r, c) < 0.6 else 'bronce'
            tag = 'paper' if hh(r, c, 5) < 0.5 else None
            P.append(plane((x - 1.25, y - (8.4 if tag else 5.2), 14.5), (x + 1.25, y + 0.4, 14.5), key_tone(kind, tag)))
            n += 1
    return P


def castigos_tone():
    """Punishment list pinned to the kitchen wall: CASTIGOS header, date, handwritten lines, Albornoz in red."""
    head = set(draw_text(F35, 'CASTIGOS', 0, 2))
    hw = max(x for x, y in head) + 1
    date = set(draw_text(F35, '18/6/84', 0, 9))
    dw = max(x for x, y in date) + 1
    alb = set(draw_text(F35, 'ALBORNOZ', 0, 0))

    def t(ctx):
        i, j, w, h = ctx.i, ctx.j, ctx.w, ctx.h
        if ctx.face != 'north':
            return T(PAPER, 5)
        base = cloth(PAPER, base=7, seed=481, folds=0, weave=False, stains=0.4, stain_col=hx('#8a6a3a'))(ctx)
        if ctx.edge() == 0:
            base = mix(base, hx('#6a5a40'), 0.35)
        if j == h // 3 and hh(i, 3) < 0.7:
            base = mix(base, hx('#7a6a50'), 0.25)                 # fold line
        ox = (w - hw) // 2
        if (i - ox, j) in head:
            return INK
        if (i - (w - dw - 2), j) in date:
            return mix(INK, base, 0.25)
        # handwritten lines
        lines = (16, 21, 26, 31, 36)
        for n, ly in enumerate(lines):
            if n == 3:
                if (i - 2, j - ly + 4) in alb:
                    return INK_RED
                if j == ly + 1 and 2 <= i < 33:
                    return INK_RED                                # underlined twice
                continue
            if ly - 2 <= j <= ly and 2 <= i < w - 3:
                seg = hh(i // 3, n, 9)
                if j == ly and seg > 0.22 and (i + n) % 5 != 0:
                    return mix(INK_BLUE, base, 0.15)
                if j == ly - 1 and hh(i, n, 2) < 0.35 and seg > 0.22:
                    return mix(INK_BLUE, base, 0.25)
                if j == ly - 2 and hh(i, n, 4) < 0.12:
                    return mix(INK_BLUE, base, 0.3)
        if j == h - 4 and w // 2 <= i < w - 3 and hh(i, 7) < 0.75:
            return INK                                            # signature
        if j == h - 5 and w // 2 + 2 <= i < w - 4 and hh(i, 8) < 0.4:
            return INK
        return base
    return t


def lista_castigos_parts():
    return [box((0.6, -4.0, 15.55), (15.4, 15.0, 15.65), fin(castigos_tone(), ao=0, dust=0), faces=('north', 'south')),
            box((7.6, 13.6, 15.0), (8.4, 14.4, 15.55), fin(flat(NICKEL, 6), ao=0)),          # pin
            box((12.6, -4.0, 15.2), (15.4, -2.6, 15.55), fin(flat(PAPER, 5), ao=0), rot=('y', 22.5, (14.0, -3.3, 15.4)))]  # curled corner


def cano_parts():
    mI = fin(iron(seed=491, rust=0.45, base=2))
    return [box((5.0, 0.0, 10.6), (9.0, 16.0, 14.6), mI), box((4.6, 7.0, 10.2), (9.4, 7.8, 15.0), mI)]


# ============================================================================================ register: refectory + kitchen
F('mesa_larga_extremo', 'Mesa larga del refectorio (punta)', 'Long refectory table (end)', mesa_larga_parts('extremo'))
F('mesa_larga_centro', 'Mesa larga del refectorio (tramo)', 'Long refectory table (middle)', mesa_larga_parts('centro'))
F('mesa_larga_puesta', 'Mesa larga del refectorio puesta', 'Long refectory table (set)', mesa_larga_parts('puesta'))
F('banco_largo_extremo', 'Banco largo (punta)', 'Long bench (end)', banco_largo_parts('extremo'))
F('banco_largo_centro', 'Banco largo (tramo)', 'Long bench (middle)', banco_largo_parts('centro'))
F('cubiertos_mesa', 'Plato, tazón y cubiertos (sobre mesa)', 'Place setting (on a table)', place_setting(5.0, 8.4, y=-4.0),
  collision='none', sound='ceramic')
F('pila_platos', 'Pila de platos (sobre mesa)', 'Stack of plates (on a table)', stack_plates_parts(), collision='none',
  sound='ceramic')
F('candelero_mesa', 'Candelero encendido (sobre mesa)', 'Table candlestick, lit (on a table)', candelero_mesa_parts(True),
  light=12, collision='none', sound='metal')
F('candelero_mesa_apagado', 'Candelero apagado (sobre mesa)', 'Table candlestick, unlit (on a table)',
  candelero_mesa_parts(False), collision='none', sound='metal')
F('atril_lectura', 'Atril con "Vidas de Santas"', 'Reading lectern with "Lives of the Saints"', atril_lectura_parts())
F('cocina_hierro_izq', 'Cocina económica de hierro (izquierda)', 'Cast-iron wood stove (left)', stove_parts('izq'), sound='metal')
F('cocina_hierro_der', 'Cocina económica de hierro (derecha)', 'Cast-iron wood stove (right)', stove_parts('der'), sound='metal')
F('cano_estufa', 'Caño de la cocina', 'Stove pipe', cano_parts(), env=(), sound='metal')
F('olla', 'Olla enlozada (sobre mesa o cocina)', 'Enamel pot (on a table or the stove)', olla_parts(), collision='none',
  sound='metal')
F('ollas_piso', 'Ollas en el piso', 'Pots on the floor', ollas_piso_parts(), sound='metal')
F('tablero_llaves', 'Tablero de llaves', 'Key board', tablero_llaves_parts(), env=('wall',), collision='none')
F('tablero_llaves_falta', 'Tablero de llaves (falta la del despacho)', 'Key board (office key taken)',
  tablero_llaves_parts(True), env=('wall',), collision='none')
F('lista_castigos', 'Lista de castigos', 'Punishment list', lista_castigos_parts(), env=('wall',), collision='none',
  sound='paper')
