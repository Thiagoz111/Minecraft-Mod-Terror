"""DEAD LINE building kit - Casa Morales, Pasaje Las Glicinas 1961 (chalet de los 50, 2026): FURNITURE + PROPS
(kit 'casa_muebles'). Every block key starts with 'casa_'.

A working-class family home in the conurbano: grandma's lustred 60s furniture next to cheap 2000s melamine, a 70s
floral sofa with crocheted doilies everywhere, a CRT TV with rabbit ears, green kitchen tiles, a brick parrilla, a
murky pelopincho, the dog's cucha. Lived-in and worn rather than ruined (dust on tops, grime where hands go, stains),
except the basement and the sealed 1961 room, which are filthy.

Authoring orientation (see bkit): furniture faces NORTH (front at z=0). Conventions used in this kit:
  * the FRONT of a piece faces 'facing'. Seats/beds/desks: the user looks toward 'facing' (a sofa facing north = the
    sitter looks north); beds: the headboard ('cabecera') sits against the wall opposite to 'facing', the foot ('pie')
    is the next block in the facing direction.
  * wall pieces (photos, shelves, cupboards, clocks, heater, breaker board, posters): back against the wall opposite
    to 'facing', front = facing.
  * '_izq' / '_der' = the block on YOUR left / right when you stand IN FRONT of the piece looking at it
    (in authoring space, viewer's left = +x). '_cabecera'/'_pie' = head / foot. '_abajo'/'_arriba' = lower/upper block.
  * 'sobre mesa' props (lata, florero, desayuno, velador...) are modelled 4/16 lower: place them in the block ABOVE a
    12/16 table. 'sobre mesada' props (mate+termo, panera, pava, escurridor) are modelled 2/16 lower: place them in
    the block ABOVE a 14/16 kitchen counter (casa_mesada*).
  * lamps / light sources come in lit / off pairs: <key> (lit) and <key>_apagado / _apagada (off).

Painting: hand-built tone ramps, structured wood grain, floral upholstery, crochet, knit, granny squares, bricks and
tiles laid out in block space so neighbours continue the pattern; contact ambient occlusion computed from the model,
dust on horizontal surfaces, crisp worn edges. No directional light is baked (Minecraft shades faces).
"""
import math

from bkit import Furniture, Door, Trapdoor, box, plane
from paint import hx, mix
from mcmodel import vnoise

KIT = 'casa_muebles'


# ============================================================================================ palettes
def pal(*cols):
    return [hx(c) for c in cols]


# woods (dark -> light; shadows purple-brown, lights warm)
CAOBA = pal('#120707', '#1e0b0a', '#2c110e', '#3c1913', '#4e2217', '#622c1c', '#773823', '#8d462c', '#a45838')  # lustred
NOGAL = pal('#140b0b', '#21120f', '#2f1a13', '#3e2318', '#4f2e1d', '#623a24', '#77492c', '#8d5a36', '#a66f45')
ROBLE = pal('#1b110d', '#2a1a12', '#3b2617', '#4e331d', '#634225', '#79522e', '#8f6439', '#a67847', '#bc8e59')
ROBLE_CL = pal('#3a2a1a', '#523c25', '#6c5032', '#87663f', '#a07c4e', '#b8925f', '#cca772', '#dcbb88', '#e9cfa2')
PINO = pal('#2a1d14', '#3f2c1d', '#574029', '#6f5436', '#886844', '#a07d54', '#b69266', '#c9a77b', '#d9bd94')
RAW = pal('#4a3524', '#6b4f36', '#8b6a49', '#a8875f', '#c2a278', '#d6ba92')
MELA_W = pal('#57544f', '#75726b', '#938f87', '#aeaaa1', '#c4c0b6', '#d5d2c8', '#e2dfd6', '#ecebe4', '#f5f4ef')
MELA_WG = pal('#1a1310', '#261b16', '#33241c', '#402d23', '#4e372b', '#5c4233', '#6b4d3b')  # wengue melamine
# metals
IRON = pal('#0c0b0f', '#141319', '#1c1b22', '#25252d', '#303139', '#3c3e48', '#4c4f5b', '#61656f', '#7b8089')
RUST = pal('#24110b', '#3a1b0f', '#542612', '#6e3317', '#89421d', '#a35526', '#bb6d36', '#cf8a4f')
BRASS = pal('#22160a', '#3a280f', '#563c15', '#74531d', '#936c27', '#b08835', '#c9a44c', '#dfc274', '#f1dfa6')
VERDI = pal('#24362f', '#344d42', '#4a6858', '#628371')
NICKEL = pal('#1d1f23', '#2e3136', '#43474d', '#5c6067', '#787c83', '#959aa0', '#b3b7bb', '#cfd2d4', '#e9ebec')
STEEL = pal('#25282c', '#373b40', '#4c5157', '#63686f', '#7c8188', '#959aa0', '#aeb2b7', '#c6c9cd', '#dcdee1')
ALU = pal('#3c4045', '#555a60', '#70757b', '#8b9096', '#a5aab0', '#bfc3c8', '#d6d9dc', '#e9ebed')
GOLD = pal('#2a1a07', '#45300e', '#654816', '#87621f', '#a87e2a', '#c79b3c', '#deb957', '#efd583', '#f9ecbb')
# textiles
FLORAL_BG = pal('#43352a', '#5f4d3c', '#7c6851', '#98846a', '#b09c80', '#c4b195', '#d4c3a8', '#e1d3bb')
ROSE = pal('#2e0e0c', '#4a1611', '#6a2116', '#8a2f1d', '#a74126', '#bf5935', '#d27a4c', '#e2a06f')
LEAF = pal('#161c0e', '#232d14', '#34421c', '#465824', '#5a6d2e', '#71833b', '#8b9a4f')
CROCHET = pal('#625a4c', '#837a69', '#a49b87', '#c1b8a3', '#d6cfbc', '#e5dfcf', '#f0ebdf', '#f8f5ee')
WOOL_R = pal('#250405', '#3c0708', '#560b0c', '#721111', '#8e1916', '#a9241e', '#c1352a', '#d6503d', '#e57460')
PINK = pal('#432630', '#653846', '#894c60', '#a96579', '#c38296', '#d7a0b1', '#e5bdca', '#f0d8e0', '#f8ecf0')
LINEN = pal('#4f4b47', '#6a665f', '#86817a', '#a09b92', '#b8b2a8', '#ccc7bc', '#dcd8ce', '#e8e5dc', '#f1efe8')
QUILT = pal('#40362b', '#5a4c3d', '#766550', '#917f66', '#a9977c', '#bdac91', '#cfbfa5', '#ddd0b9')
GRAPH = pal('#0e0f12', '#16171b', '#1e2025', '#272a30', '#31343c', '#3d414a', '#4b505a', '#5b616c')
NAVY = pal('#080c19', '#0d1426', '#131c35', '#1a2546', '#223058', '#2c3c6a', '#3a4c7e')
DENIM = pal('#0f1626', '#16203a', '#1f2c4e', '#2a3a62', '#384b76', '#4b5f8a', '#62779f')
VELVET_P = pal('#140a17', '#1f1024', '#2b1733', '#382042', '#462a52', '#553563', '#654274', '#775486')
LEATHER_B = pal('#170c08', '#24130c', '#331b11', '#442416', '#572f1d', '#6c3c26', '#824b31', '#985c3d')
RUSH = pal('#3a2a14', '#57401d', '#735727', '#8e6e33', '#a88742', '#bf9e55', '#d2b46c')
# ceramics / appliances / plastics
PORC = pal('#555a5d', '#71777a', '#8e9496', '#aab0b0', '#c2c6c4', '#d5d8d4', '#e4e5e0', '#efefea', '#f8f7f2')
ENAMEL = pal('#4a463c', '#6a6455', '#8c8571', '#aca48c', '#c6bea4', '#d8d1b8', '#e6e0c9', '#f0ebd8', '#f8f5ea')
TILE_G = pal('#0f2017', '#163024', '#1f4231', '#2a5740', '#386d50', '#4a8462', '#619b77', '#7fb48f', '#a3cbab')
GRANITO = pal('#17171a', '#222226', '#2e2e33', '#3b3b41', '#4a4a50', '#5c5c62', '#717176', '#8a8a8e')
PLAST_W = pal('#57554d', '#77746a', '#969287', '#b2aea2', '#c8c4b8', '#d9d6cb', '#e7e5dc', '#f2f1eb')
PVC_B = pal('#0b1c33', '#10294a', '#173864', '#1f4a80', '#2b5e9c', '#3c75b5', '#5690cb', '#77abdc')
BLACKP = pal('#060609', '#0c0c10', '#131318', '#1b1b21', '#24242b', '#2e2e36', '#3a3a43', '#484852')
REDP = pal('#200707', '#360c0b', '#4f120f', '#6b1914', '#86231a', '#9f3122', '#b64630', '#c96446')
CELESTE = pal('#2b4560', '#3d5d7d', '#527796', '#6a92ae', '#85abc4', '#a4c4d8', '#c4dbe8')
YELLOWP = pal('#3a2c06', '#5c460a', '#82650f', '#a88516', '#c9a320', '#e0bd33', '#efd558', '#f8e992')
GREENP = pal('#0f1712', '#17221a', '#1f2d22', '#29392c', '#344637', '#415443', '#506452', '#637764')
# masonry
BRICK = pal('#2a110b', '#43180e', '#5e2213', '#782d19', '#913b20', '#a74c29', '#ba6035', '#cb784b', '#d8956a')
MORTAR = pal('#3c3731', '#575148', '#736c60', '#8f877a', '#a89f91', '#bdb5a6', '#cfc8ba')
BAKE = pal('#070608', '#0e0c10', '#161319', '#1f1b22', '#29242d', '#35303a', '#46404b', '#5b5461')
CEMENT = pal('#2f2e2b', '#45433f', '#5c5a55', '#75726c', '#8d8a83', '#a4a199', '#b9b6ae', '#cccac3')
# nature
LEAFT = pal('#0a1307', '#11200c', '#1a2f12', '#233f18', '#2e501f', '#3a6227', '#497530', '#5a883b', '#6f9c4b')
LEMON = pal('#4a3a06', '#6e570a', '#94770f', '#b89a18', '#d4b627', '#e6cc3c', '#f1df63', '#f8ee9a')
GERAN = pal('#3a0508', '#5c080d', '#820f14', '#a8181b', '#c92a26', '#e04636', '#ef6c50', '#f99a7c')
TERRA = pal('#2e140b', '#47200f', '#622d15', '#7e3c1c', '#984c25', '#b05f31', '#c4743f', '#d48c55')
WATER_G = pal('#11170a', '#192010', '#212b15', '#2b371b', '#354422', '#3f502a', '#4c5e32', '#5d6f3d', '#738550')
BARK = pal('#1a1410', '#2a2019', '#3a2d22', '#4b3b2d', '#5d4a39', '#705b47', '#846d57')
# paper / misc
PAPER = pal('#4f4130', '#6d5b43', '#8a7657', '#a4906d', '#bba783', '#cebb98', '#ddcdac', '#e9dcc0', '#f2e8d4')
CARTON = pal('#3a2a18', '#55401f', '#6f5428', '#8a6a34', '#a28041', '#b89652', '#caab68', '#d9c084')
WAX = pal('#5f584b', '#7f7766', '#a19782', '#bfb49b', '#d4cab1', '#e3dbc6', '#efe9d9', '#f7f4ea')
FLAME = pal('#6e1f05', '#b2420a', '#e2701a', '#f9a332', '#ffcc5a', '#ffe796', '#fffbe6')
FLAME_B = pal('#06103a', '#0b2070', '#1238a8', '#2a5ad8', '#4f86f0', '#8ab6fa', '#c8e2ff')
EMBER = pal('#1a0604', '#3a0b05', '#6a1406', '#a02408', '#d0410c', '#f06a18', '#ffa040', '#ffd27a')
EMBER_B = pal('#040616', '#0a1034', '#101c5c', '#183090', '#2448c0', '#3f6ce0', '#74a0f4', '#b8d4ff')
ASH = pal('#1c1a19', '#2b2927', '#3b3936', '#4d4a46', '#625f5a', '#7a766f', '#938f87')
SKIN = pal('#5b3d35', '#7a5246', '#986959', '#b4826e', '#c99a84', '#dbb49e', '#e9cab6', '#f3dece')
PORCELAIN = pal('#6a5e5a', '#8c7f7a', '#ab9f99', '#c6bbb4', '#dad0c8', '#e9e1d9', '#f3eee8', '#fbf8f4')  # dolls
HAIR = pal('#0c0807', '#170f0c', '#241812', '#33221a', '#452e22', '#5a3c2b', '#73503a')
GLASS_J = pal('#1d241c', '#2c3628', '#3e4a38', '#536149', '#6b7a5f', '#879679', '#a8b59a')
MIRROR = pal('#0f1317', '#161c21', '#1f272d', '#29333a', '#36424a', '#46545d', '#5b6a73', '#77878f', '#9cabb2', '#c3cfd3')
OPAL = pal('#2c2a26', '#45423b', '#625d52', '#827b6c', '#a29a86', '#c0b79f', '#d9d0b6', '#ece4cc', '#fbf5e2')
OPAL_LIT = pal('#5a3c1c', '#8a6030', '#b88a48', '#dcb468', '#f2d08a', '#fbe4a8', '#fff2c8', '#fffae6')
SHADE_L = pal('#4a3c2a', '#6a573e', '#8c7654', '#ab946c', '#c6ae84', '#d9c39b', '#e7d4b0', '#f1e3c6')
SHADE_LIT = pal('#7a4a1c', '#a8682a', '#d08c3c', '#eaac52', '#f6c66e', '#fcda8e', '#ffeab0', '#fff6d8')
INK = hx('#1b1a2b')
INK_BLUE = hx('#1f2f6b')
INK_RED = hx('#8e1b1b')
DUST = hx('#958b7c')
WHITE = hx('#f4f2ec')


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


def uv2(ctx, off=(0, 0, 0)):
    """2D texel coords on a face in block space (u across, v down), so patterns continue across parts/blocks."""
    x, y, z = tp(ctx, off)
    f = ctx.face
    if f in ('north', 'south'):
        return (x if f == 'south' else -x), -y
    if f in ('west', 'east'):
        return (z if f == 'west' else -z), -y
    return x, (z if f == 'up' else -z)


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
            if ao and len(c) == 4 and c[3] > 0:
                o = occlusion(ctx)
                if o > 0.4:
                    c = mix(c, (10, 8, 12, c[3]), (0.32 if o > 0.78 else 0.16) * ao)
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
    """Structured wood grain: growth-ring lines, long pores, broad figure, rare knots, glued boards.
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
        if na == g:
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
            e = (ctx.i if ctx.j in (0, ctx.h - 1) else ctx.j) // 4
            wv2 = hh(e, FI[ctx.face], round(P[0] * 0.25), round(P[1] * 0.25), round(P[2] * 0.25), seed)
            if wv2 < wear:
                if worn_pal is not None and wv2 < wear * 0.3:
                    return (worn_pal, 2)
                k += 1
        return (p, k)
    return t


def lustre(p=CAOBA, base=4, seed=0, **kw):
    """Lustred (French-polished) old furniture: wood grain + a soft gloss band on vertical faces."""
    w = wood(p, base=base, seed=seed, **kw)

    def t(ctx):
        pl, k = w(ctx)
        if ctx.face in ('north', 'south', 'west', 'east') and ctx.h > 6:
            g = (ctx.t + ctx.s * 0.35) % 1.0
            if 0.18 < g < 0.24:
                k += 1
        elif ctx.face == 'up':
            g = (ctx.s * 0.7 + ctx.t * 0.3)
            if 0.40 < g < 0.47:
                k += 1
        return (pl, k)
    return t


def iron(p=IRON, base=3, seed=0, rust=0.3, off=(0, 0, 0), worn=0.3, pits=0.02, drips=True):
    """Black-painted iron: worn bright edges, sparse pits, rust patches that bleed down."""
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


def painted_iron(paint=ENAMEL, base=6, seed=0, chips=0.3, off=(0, 0, 0)):
    """Iron painted a light colour: chips show black iron ringed with rust, yellowed patches."""
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
    """Old brass / chrome: dark body, narrow polished highlight, tarnished patches, darker rims."""
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
            if p is BRASS and n > 1 - tarnish * 0.2 and ctx.face != 'up':
                return (VERDI, 1)
        if ctx.edge() == 0 and ctx.w > 2 and ctx.h > 2:
            k -= 1
        return (p, k)
    return t


def painted(p, base=4, seed=0, chips=0.0, under=None, under_k=3, grime=0.25, off=(0, 0, 0), bevel=False, wear=0.25):
    """Flat painted / enamelled surface: soft mottling, optional chips revealing `under`, worn edges, grime low."""
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


def smooth(p, base=5, seed=0, grime=0.15, edge=1, mottle=0.25):
    """Smooth plastic / enamel / porcelain: gentle broad mottling, darker rims, grime in the low parts."""
    def t(ctx):
        P = tp(ctx)
        n = vn(P[0] / 7.0, P[1] / 7.0, P[2] / 7.0, seed + 93)
        k = base + (1 if n > 1 - mottle else (-1 if n < mottle * 0.9 else 0))
        if edge and ctx.edge() == 0 and ctx.w > 2 and ctx.h > 2:
            k -= edge
        if grime and ctx.face not in ('up', 'down') and P[1] < 5 and hh(P[0], P[1], P[2], seed) < grime * (1 - P[1] / 5):
            k -= 1
        return (p, k)
    return t


def flat(p, k):
    return lambda ctx: (p, k)


def cloth(p=LINEN, base=6, seed=0, fold_axis='i', folds=0.6, fold_px=5.0, weave=True, stains=0.25, hem=False,
          stain_col=hx('#a08a5a'), off=(0, 0, 0)):
    """Woven fabric: fine weave, soft folds along one face axis, stains with darker rims. Returns rgba."""
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
        o = occlusion(ctx)
        if o > 0.78:
            k -= 2
        elif o > 0.4:
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


def glow(p, base=5, seed=0):
    """Emissive gradient: brighter centre."""
    def t(ctx):
        c = 1 - max(abs(ctx.s * 2 - 1), abs(ctx.t * 2 - 1))
        k = base - 2 + int(c * 4.5)
        if hh(ctx.i, ctx.j, seed) < 0.08:
            k += 1
        return (p, k)
    return t


def panels(inner, frame=None, rects=((3, 3, -3, -3),), faces=('north',), bevel=1, groove=True, carve=None):
    """Frame-and-panel painting. rects: (i0, j0, i1, j1) face-pixel boxes (negative = from the far edge)."""
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


def only(face_tones, default):
    """Per-face tone dispatch: {'north': tone, ...}; others use default."""
    def t(ctx):
        return face_tones.get(ctx.face, default)(ctx)
    return t


# ------------------------------------------------------------------------------------------------ textile patterns
def _rose(lu, lv, r=3.6):
    """Rose motif at local (lu, lv) from its centre -> ROSE step or None."""
    d = math.hypot(lu, lv)
    if d > r:
        return None
    a = math.atan2(lv, lu)
    spiral = (d * 1.25 + a / (2 * math.pi) * 2.2) % 1.0
    if d < 0.9:
        return 1
    k = 4 if spiral > 0.38 else 2
    if d > r - 0.8:
        k = 3 if spiral > 0.3 else 2
    if lv < -0.6 and lu < 0.4 and spiral > 0.5:
        k += 2                                            # light from the top-left on the petals
    return k


def floral(seed=0, off=(0, 0, 0), fade=0.0):
    """70s floral upholstery: beige ground with a woven texture, half-drop rust roses with olive leaves and small
    cream blossoms; 16 px repeat continuous across blocks (pass off = block offset). fade: worn/faded areas."""
    def t(ctx):
        u, v = uv2(ctx, off)
        k = 4
        if (int(u) + int(v) * 3) % 4 == 0:
            k -= 1                                         # weave
        if (int(u) * 3 + int(v)) % 7 == 0:
            k += 1
        res = (FLORAL_BG, k)
        cu, cv = math.floor(u / 16.0), math.floor(v / 16.0)
        lu, lv = u - cu * 16.0, v - cv * 16.0
        # main rose at (5, 5); a second, smaller one on the half-drop at (13, 13)
        for (rx, ry, rr, big) in ((5.0, 5.0, 3.7, True), (13.0, 13.0, 2.5, False)):
            du, dv = lu - rx, lv - ry
            du -= round(du / 16.0) * 16.0
            dv -= round(dv / 16.0) * 16.0
            rk = _rose(du, dv, rr)
            if rk is not None:
                res = (ROSE, rk + (0 if big else 1))
                break
            # leaves: two ellipses hugging the rose
            for (lx, ly, ang) in ((rr + 1.4, -1.6, -0.6), (-rr - 0.6, 2.0, 0.9)):
                if not big:
                    lx, ly = lx * 0.8, ly * 0.8
                ex, ey = du - lx, dv - ly
                ca, sa = math.cos(ang), math.sin(ang)
                qx, qy = ex * ca + ey * sa, -ex * sa + ey * ca
                ln = 2.4 if big else 1.8
                if (qx / ln) ** 2 + (qy / 1.05) ** 2 <= 1.0:
                    res = (LEAF, 3 if abs(qy) < 0.45 else (5 if qy < 0 else 4))
                    break
        else:
            # cream blossoms (5 dots) at (12, 4) and (4, 12)
            for (bx, by) in ((12.0, 4.0), (4.0, 12.5)):
                du, dv = lu - bx, lv - by
                d = math.hypot(du, dv)
                if d < 0.75:
                    res = (ROSE, 6)
                elif d < 1.9 and (math.atan2(dv, du) * 5 / (2 * math.pi)) % 1.0 < 0.62:
                    res = (CROCHET, 5)
        pl, kk = res
        if fade:
            fv = vn(u / 6.0, v / 6.0, seed * 0.3, seed + 7)
            if fv > 1 - fade * 0.5:
                kk += 1
                if pl is ROSE and kk < 6:
                    pl, kk = (ROSE, kk + 1)
        return (pl, kk)
    return t


def crochet_disc(ctx, cx, cy, R, seed=0):
    """Doily lace (cutout): rosette centre, ring of petals, net of holes, scalloped picot rim. Returns rgba or None."""
    x, y = ctx.i + 0.5 - cx, ctx.j + 0.5 - cy
    d = math.hypot(x, y)
    a = math.atan2(y, x)
    if d > R:
        return None
    ang = (a / (2 * math.pi)) % 1.0
    if d > R - 1.3:                                            # scallops
        sc = abs(((ang * 18) % 1.0) - 0.5)
        if d > R - 1.3 + (0.5 - sc) * 2.4 * 0.5 + 0.55:
            return None
        return T(CROCHET, 5 if sc < 0.3 else 4)
    rel = d / R
    if rel < 0.18:
        return T(CROCHET, 6 if (ctx.i + ctx.j) % 2 else 5)
    if rel < 0.42:
        pet = abs(((ang * 8) % 1.0) - 0.5)
        if pet > 0.36 and rel > 0.26:
            return None
        return T(CROCHET, 6 if pet < 0.18 else 5)
    if rel < 0.72:                                             # net
        q = (ang * 16 + (1 if int(d) % 2 else 0) * 0.5) % 1.0
        if abs(q - 0.5) < 0.24 and int(d * 1.2) % 2 == 0:
            return None
        return T(CROCHET, 5)
    pet = abs(((ang * 12 + 0.5) % 1.0) - 0.5)
    if pet > 0.34 and rel < 0.85:
        return None
    return T(CROCHET, 6 if pet < 0.2 else 4)


def doily_tone(shape='disc', seed=0):
    """Material for a crocheted doily plane. shape 'disc' (flat on a table), 'drape' (front half hanging over an
    edge: top half of a disc seen on the face), 'oval' (stretched)."""
    def t(ctx):
        w, h = ctx.w, ctx.h
        if shape == 'disc':
            R = min(w, h) / 2.0
            c = crochet_disc(ctx, w / 2.0, h / 2.0, R, seed)
        elif shape == 'oval':
            class _C:
                pass
            sx = w / max(1.0, h)
            q = _C()
            q.i, q.j = (ctx.i + 0.5) / sx - 0.5, ctx.j
            c = crochet_disc(q, h / 2.0, h / 2.0, h / 2.0, seed)
        else:                                                   # drape: disc centred at the top edge
            R = w / 2.0
            c = crochet_disc(ctx, w / 2.0, -R * 0.35, R, seed)
        if c is None:
            return None
        if hh(ctx.i, ctx.j, seed) < 0.05:
            c = mix(c, hx('#a08a5a'), 0.35)                    # yellowed spots
        return c
    return t


def knit(p=WOOL_R, base=5, seed=0, off=(0, 0, 0), cable=False):
    """Knitted wool (stockinette): columns of little V stitches, 2 px wide x 2 px tall, slight unevenness."""
    def t(ctx):
        u, v = uv2(ctx, off)
        iu, iv = int(math.floor(u)), int(math.floor(v))
        col, row = iu // 2, iv // 2
        su, sv = iu % 2, iv % 2
        k = base
        if sv == 0:
            k += 1 if su == (col % 2) else 0
        else:
            k -= 1 if su != (col % 2) else 0
        if su == 0 and sv == 1:
            k -= 1                                              # gap between the legs of the V
        if cable and col % 6 in (0, 5):
            k -= 1
        if hh(col, row, seed) < 0.06:
            k += 1
        if ctx.edge() == 0:
            k -= 1
        return (p, k)
    return t


GRANNY_COLS = [WOOL_R, YELLOWP, CELESTE, PINK, VELVET_P, LEAF, CROCHET]


def granny(seed=0, off=(0, 0, 0), size=10):
    """Granny-square crochet blanket: squares of 3 concentric coloured rings with see-through-ish dark joins."""
    def t(ctx):
        u, v = uv2(ctx, off)
        cu, cv = math.floor(u / size), math.floor(v / size)
        lu, lv = u - cu * size, v - cv * size
        m = min(lu, lv, size - lu, size - lv)
        if m < 0.9:
            return (BAKE, 3)                                    # black joining round
        ring = int((m - 0.9) / ((size / 2 - 0.9) / 3))
        cols = [GRANNY_COLS[int(hh(cu, cv, seed, r) * len(GRANNY_COLS))] for r in range(3)]
        p = cols[min(2, ring)]
        k = 5
        # clusters: gaps every 3 px along the ring direction
        along = lu if abs(lu - size / 2) < abs(lv - size / 2) else lv
        if int(along) % 3 == 0:
            k -= 1
        if (int(lu) + int(lv)) % 2 == 0:
            k += 0 if hh(int(u), int(v), seed) > 0.3 else -1
        return (p, k)
    return t


def bricks(seed=0, off=(0, 0, 0), soot=0.0, mortar=MORTAR, blen=8, course=3):
    """Common brick (ladrillo comun) in running bond: 8 px long, 2 px high + 1 px mortar joints; per-brick tone,
    chipped corners, soot rising from below (soot>0, parrilla)."""
    def t(ctx):
        u, v = uv2(ctx, off)
        x, y, z = tp(ctx, off)
        if ctx.face in ('up', 'down'):
            u, v = x, z
        row = math.floor(v / course)
        sh = (blen // 2) * (row % 2)
        col = math.floor((u + sh) / blen)
        lu = (u + sh) - col * blen
        lv = v - row * course
        if lv < 1.0 or lu < 1.0:
            res = (mortar, 3 + (hh(int(u), int(v), seed) > 0.6))
        else:
            b = hh(col, row, seed)
            k = 4 + (1 if b > 0.66 else (-1 if b < 0.25 else 0))
            if b > 0.93:
                k = 2                                           # an over-fired dark brick
            if (lu < 2 or lu > blen - 1) and hh(col, row, int(lu), seed) < 0.2:
                k -= 1
            if hh(int(u), int(v), seed, 3) < 0.05:
                k += 1
            res = (BRICK, k)
        if soot:
            sv = vn(x / 6.0, y / 9.0, z / 6.0, seed + 5) * 0.6 + max(0.0, (y / 32.0)) * 0.6
            if sv > 1 - soot * 0.6:
                pl, k = res
                return (BAKE, 3 + (pl is BRICK) + (sv < 1 - soot * 0.45))
        return res
    return t


def tiles(p=TILE_G, base=5, size=8, seed=0, off=(0, 0, 0), grout=None, decor=0.0):
    """Glazed square tiles with grout lines; per-tile tone, glaze highlight at the top-left, grimy grout,
    occasional decal tile (decor = probability) with a 4-petal flower."""
    grout = grout or (CEMENT, 4)

    def t(ctx):
        u, v = uv2(ctx, off)
        if ctx.face in ('up', 'down'):
            x, y, z = tp(ctx, off)
            u, v = x, z
        cu, cv = math.floor(u / size), math.floor(v / size)
        lu, lv = u - cu * size, v - cv * size
        if lu < 1.0 or lv < 1.0:
            g = grout
            if hh(int(u), int(v), seed) < 0.3:
                return (g[0], g[1] - 1)
            return g
        b = hh(cu, cv, seed)
        k = base + (1 if b > 0.8 else (-1 if b < 0.12 else 0))
        if lu < 2.0 and lv < 3.0 or lv < 2.0 and lu < 3.0:
            k += 1
        if lu > size - 1 or lv > size - 1:
            k -= 1
        if decor and hh(cu, cv, seed, 5) < decor:
            du, dv = lu - (size + 1) / 2.0, lv - (size + 1) / 2.0
            if abs(du) + abs(dv) < 1.2:
                return (YELLOWP, 5)
            if (abs(du) < 0.7 and abs(dv) < 2.6) or (abs(dv) < 0.7 and abs(du) < 2.6):
                return (CROCHET, 6)
        return (p, k)
    return t


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
    '♥': ['#.#', '###', '###', '.#.', '...'], '%': ['#.#', '..#', '.#.', '#..', '#.#'],
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
    '+': ['.....', '..#..', '..#..', '#####', '..#..', '..#..', '.....'], '/': ['....#', '...#.', '...#.', '..#..', '.#...', '.#...', '#....'],
    "'": ['#', '#', '.', '.', '.', '.', '.'], '♥': ['.....', '.#.#.', '#####', '#####', '.###.', '..#..', '.....'],
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
        return acc_rows + rows, -len(acc_rows)
    up = ch.upper()
    if up in font:
        return font[up], 0
    return font.get('?', [['#']]), 0


def text_width(font, s, sp=1):
    return sum(len(glyph(font, c)[0][0]) + sp for c in s) - sp if s else 0


def draw_text(font, s, x, y, sp=1, italic=0.0, jitter=0.0, seed=0, scale=1):
    """Rasterise text; returns list of (x, y). italic = px shift per row (handwriting slant)."""
    out = []
    cx = x
    for n, ch in enumerate(s):
        rows, top = glyph(font, ch)
        jy = 0
        if jitter:
            jy = int(round((hh(seed, n, 1) - 0.5) * 2 * jitter))
        for j, row in enumerate(rows):
            for i, c in enumerate(row):
                if c == '#':
                    sh = int(round((len(rows) + top - j) * italic)) if italic else 0
                    for a in range(scale):
                        for b in range(scale):
                            out.append((cx + i * scale + a + sh, y + (top + j) * scale + b + jy))
        cx += (len(rows[0]) + sp) * scale
    return out


# ============================================================================================ small helpers
def mirror_parts(parts):
    """Mirror a list of parts across x=8 (left half -> right half). Decals are dropped (they are not mirrored)."""
    out = []
    for p in parts:
        f, t = p.frm, p.to
        rot = p.rot
        if rot:
            ax, ang, org = rot
            rot = (ax, -ang if ax in ('y', 'z') else ang, (16 - org[0], org[1], org[2]))
        faces = tuple({'west': 'east', 'east': 'west'}.get(fc, fc) for fc in p.faces)
        q = type(p)((16 - t[0], f[1], f[2]), (16 - f[0], t[1], t[2]), p.mat, faces=faces, rot=rot, decals=p.decals,
                    shade=p.shade, name=p.name, cull=p.cull)
        out.append(q)
    return out


def shift(parts, dx=0, dy=0, dz=0):
    for p in parts:
        p.frm = (p.frm[0] + dx, p.frm[1] + dy, p.frm[2] + dz)
        p.to = (p.to[0] + dx, p.to[1] + dy, p.to[2] + dz)
        if p.rot:
            ax, ang, o = p.rot
            p.rot = (ax, ang, (o[0] + dx, o[1] + dy, o[2] + dz))
    return parts


def F(key, es, en, parts, env=('floor',), sound='wood', light=0, render='cutout', collision='auto', directional=True,
      breakable=False, mat=None):
    b = Furniture('casa_' + key, es, en, parts, kit=KIT, sound=sound, light=light, render=render, collision=collision,
                  directional=directional, breakable=breakable, mat=mat)
    b.env = env
    return b


class _Q:
    """Fake ctx for sampling a tone at arbitrary i/j."""
    __slots__ = ('i', 'j')


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


class Canvas:
    """Tiny raster painter for pictures (photos, screens, drawings): rgba rows, painter's algorithm."""

    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = [[bg] * w for _ in range(h)]

    def get(self, x, y):
        if 0 <= x < self.w and 0 <= y < self.h:
            return self.px[y][x]
        return None

    def set(self, x, y, c):
        x, y = int(x), int(y)
        if c is not None and 0 <= x < self.w and 0 <= y < self.h:
            if callable(c):
                c = c(self.px[y][x])
            self.px[y][x] = c

    def rect(self, x0, y0, x1, y1, c):
        for y in range(int(y0), int(y1)):
            for x in range(int(x0), int(x1)):
                self.set(x, y, c)

    def ellipse(self, cx, cy, rx, ry, c):
        for y in range(int(cy - ry - 1), int(cy + ry + 2)):
            for x in range(int(cx - rx - 1), int(cx + rx + 2)):
                if ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 <= 1.0:
                    self.set(x, y, c)

    def poly(self, pts, c):
        ys = [p[1] for p in pts]
        for y in range(int(min(ys)), int(max(ys)) + 1):
            for x in range(0, self.w):
                if _pip(x + 0.5, y + 0.5, pts):
                    self.set(x, y, c)

    def line(self, x0, y0, x1, y1, c, w=1):
        n = int(max(abs(x1 - x0), abs(y1 - y0)) * 2) + 1
        for i in range(n + 1):
            x = x0 + (x1 - x0) * i / n
            y = y0 + (y1 - y0) * i / n
            for a in range(w):
                for b in range(w):
                    self.set(int(x) + a, int(y) + b, c)

    def ascii(self, x0, y0, rows, pal_):
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                if ch in pal_:
                    self.set(x0 + i, y0 + j, pal_[ch])

    def text(self, font, s, x, y, c, **kw):
        for (px_, py_) in draw_text(font, s, x, y, **kw):
            self.set(px_, py_, c)


def canvas_tone(cv, face='north', other=None, flip=False):
    """Material that shows canvas pixels on one face (scaled to the face size); other faces use `other`."""
    def t(ctx):
        if ctx.face != face:
            return other(ctx) if other else (PAPER, 5)
        x = int(ctx.s * cv.w)
        y = int(ctx.t * cv.h)
        if flip:
            x = cv.w - 1 - x
        c = cv.get(x, y)
        return c if c is not None else (PAPER, 6)
    return t


# ------------------------------------------------------------------------------------------------ candles, flames
def flame_tone(p=FLAME, core=hx('#4d63c8')):
    """Candle/gas flame (cutout): teardrop with bright core, coloured rim, blue base."""
    def t(ctx):
        w, h = ctx.w, ctx.h
        x = (ctx.i + 0.5) / w * 2 - 1
        y = (ctx.j + 0.5) / h
        width = 0.95 * math.sin(min(1.0, y * 1.15) * math.pi * 0.62) * (1.0 if y < 0.85 else (1 - (y - 0.85) * 4))
        if abs(x) > width or y < 0.04:
            return None
        if y > 0.86:
            return core if abs(x) < width * 0.35 else T(p, 1)
        c = abs(x) / max(0.01, width)
        k = 6 - int(c * 2.6) - (1 if y < 0.3 else 0) - (1 if y < 0.15 else 0)
        if c < 0.35 and 0.55 < y < 0.8:
            k = 5
        return T(p, k)
    return t


def flame_parts(cx, cz, y0, h=2.6, w=1.6, p=FLAME):
    ft = flame_tone(p)
    return [plane((cx - w / 2, y0, cz), (cx + w / 2, y0 + h, cz), ft, shade=False),
            plane((cx, y0, cz - w / 2), (cx, y0 + h, cz + w / 2), ft, shade=False)]


def candle_tone(seed=0, p=WAX, melted=0.0):
    """Wax: smooth body, vertical drips from the rim, darker melted crater on top."""
    def t(ctx):
        k = 5
        if ctx.face == 'up':
            d = max(abs(ctx.s - 0.5), abs(ctx.t - 0.5))
            return (p, 3 if d < 0.2 else 4)
        col = ctx.i
        dl = int(hh(col, seed, 3) * (8 + melted * 10)) if hh(col, seed) < 0.45 + melted * 0.3 else 0
        if ctx.j < dl:
            k = 6 + (ctx.j == dl - 1)
        if ctx.j == 0:
            k = 4
        if ctx.i == 0 or ctx.i == ctx.w - 1:
            k -= 1
        return (p, k)
    return t


def candle(cx, cz, y0, y1, r=0.8, lit=True, seed=0, p=WAX, melted=0.0):
    P = [box((cx - r, y0, cz - r), (cx + r, y1, cz + r), fin(candle_tone(seed, p, melted), ao=0.5, dust=0)),
         box((cx - 0.12, y1, cz - 0.12), (cx + 0.12, y1 + 0.7, cz + 0.12), fin(flat(IRON, 0), ao=0, dust=0))]
    if lit:
        P += flame_parts(cx, cz, y1 + 0.2, h=2.4 * (r / 0.8) ** 0.4, w=1.4 * (r / 0.8) ** 0.4)
    return P


def puddle_tone(centres, seed=0, p=WAX):
    """Irregular wax puddle (cutout): union of blobs around the candles, creamy with a darker dirty rim."""
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
        return (p, k)
    return t


# ------------------------------------------------------------------------------------------------ chains, cords, mirrors
def chain_tone(ctx):
    """Chain links (cutout): an open ring seen flat, then a link seen edge-on."""
    i, j, w = ctx.i, ctx.j, ctx.w
    y = j % 7
    c = (w - 1) / 2.0
    d = abs(i - c)
    if y < 4:
        ring = ['.#.', '#.#', '#.#', '.#.'][y]
        ix = int(round(i - c + 1))
        if 0 <= ix < 3 and ring[ix] == '#':
            return T(BRASS, 6 if (y == 0 or ix == 0) else 4)
        return None
    if d < 0.6:
        return T(BRASS, 5 if y == 5 else 3)
    return None


def chain_parts(x=8.0, z=8.0, y0=0.0, y1=16.0, w=1.5):
    return [plane((x - w / 2, y0, z), (x + w / 2, y1, z), chain_tone, faces=('north', 'south')),
            plane((x, y0, z - w / 2), (x, y1, z + w / 2), chain_tone, faces=('west', 'east'))]


def cord_parts(x=8.0, z=8.0, y0=0.0, y1=16.0, col=BLACKP, k=3):
    m = fin(flat(col, k), ao=0, dust=0.3)
    return [box((x - 0.25, y0, z - 0.25), (x + 0.25, y1, z + 0.25), m)]


def mirror_tone(cracked=False, seed=0, fog=0.0):
    """Old mirror: dark cool reflection, diagonal sheen streaks, black silvering loss at the edges."""
    def t(ctx):
        i, j, w, h = ctx.i, ctx.j, ctx.w, ctx.h
        u = (i + j * 0.6)
        k = 3 + (1 if j < h * 0.4 else 0)
        if 6 < (u % 23) < 9:
            k += 2
        elif 9 <= (u % 23) < 10:
            k += 1
        e = min(i, j, w - 1 - i, h - 1 - j)
        n = vn(i / 3.0, j / 3.0, seed * 0.1, seed + 361)
        if e < 3 and n > 0.45 + e * 0.12:
            return T(MIRROR, 0 if hh(i, j) < 0.6 else 1)
        if hh(i // 2, j // 2, seed) < 0.015:
            return T(MIRROR, 1)
        c = T(MIRROR, k)
        if fog and vn(i / 4.0, j / 4.0, 0.3, seed + 5) > 1 - fog:
            c = mix(c, hx('#c8ccc6'), 0.25)
        if cracked:
            cx, cy = w * 0.55, h * 0.42
            dx, dy = i + 0.5 - cx, j + 0.5 - cy
            a = math.atan2(dy, dx)
            r = math.hypot(dx, dy)
            spokes = (a / (2 * math.pi) * 9 + 0.5) % 1.0
            wob = vn(r / 3.0, a * 2, 0.0, seed + 5) * 0.12
            if r < 1.5 or (abs(spokes - 0.5 + wob) < 0.06 and r < max(w, h) * 0.8) or (abs(r - 4.5) < 0.5 and spokes < 0.7):
                return T(MIRROR, 9) if hh(i, j, 3) < 0.5 else T(MIRROR, 0)
        return c
    return t


# ------------------------------------------------------------------------------------------------ shared materials
M_IRON = fin(iron(seed=3))
M_BRASS = fin(brass(seed=5, base=4), dust=0.6)
M_CHROME = fin(brass(NICKEL, seed=7, base=5, tarnish=0.2), dust=0.5)
M_CAOBA = fin(lustre(CAOBA, seed=11, worn_pal=RAW, wear=0.35))
M_DARK = fin(flat(BAKE, 1), ao=0, dust=0)
