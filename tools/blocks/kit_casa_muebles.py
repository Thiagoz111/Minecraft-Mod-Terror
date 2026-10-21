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
def _rose(du, dv, r):
    """Cabbage-rose motif (du, dv from its centre) -> ROSE step or None: dark rim, spiral petal edges, lit top-left."""
    d = math.hypot(du, dv)
    if d > r:
        return None
    if d > r - 0.85:
        return 1
    a = math.atan2(dv, du)
    q = (d / r * 2.6 + (a / (2 * math.pi))) % 1.0
    light = -(du + dv) / (r * 1.414)
    k = 3 + (1 if light > 0.15 else 0) + (1 if q > 0.55 else 0)
    if q < 0.17:
        k = 2 if d > r * 0.4 else 1
    if d < r * 0.22:
        k = 2
    if light > 0.55 and q > 0.55:
        k = 6
    return k


def _leaf(du, dv, ang, ln, wd):
    """Pointed leaf from its base: -> LEAF step or None."""
    ca, sa = math.cos(ang), math.sin(ang)
    x, y = du * ca + dv * sa, -du * sa + dv * ca
    if x < 0 or x > ln:
        return None
    w = wd * math.sin(math.pi * x / ln) ** 0.8
    if abs(y) > w:
        return None
    if abs(y) > w - 0.7:
        return 1
    if abs(y) < 0.45:
        return 2
    return 5 if y < 0 else 4


ROSES = ((9.0, 10.0, 6.4), (25.0, 25.5, 4.4), (25.5, 6.0, 2.4), (5.0, 26.5, 2.2))
LEAVES = ((9.0, 10.0, -0.35, 11.5, 2.3), (9.0, 10.0, 2.55, 10.5, 2.1), (9.0, 10.0, 1.2, 9.5, 1.9),
          (25.0, 25.5, 3.6, 8.0, 1.8), (25.0, 25.5, 0.6, 7.5, 1.7), (25.5, 6.0, 1.9, 5.0, 1.2), (5.0, 26.5, -1.0, 5.0, 1.2))


def floral(seed=0, off=(0, 0, 0), fade=0.0):
    """70s floral upholstery: cream-beige twill ground, big rust cabbage roses with olive pointed leaves, buds and
    tiny cream sprigs; 32 px repeat laid out in block space (pass off = block offset so sofas continue the print)."""
    def t(ctx):
        u, v = uv2(ctx, off)
        iu, iv = int(math.floor(u)), int(math.floor(v))
        k = 5
        if (iu + iv) % 3 == 0:
            k -= 1                                         # twill diagonal
        res = (FLORAL_BG, k)
        lu, lv = u % 32.0, v % 32.0
        hit = False
        for (rx, ry, rr) in ROSES:
            du, dv = lu - rx, lv - ry
            du -= round(du / 32.0) * 32.0
            dv -= round(dv / 32.0) * 32.0
            rk = _rose(du, dv, rr)
            if rk is not None:
                res = (ROSE, rk + (1 if rr < 3 else 0))
                hit = True
                break
        if not hit:
            for (rx, ry, ang, ln, wd) in LEAVES:
                du, dv = lu - rx, lv - ry
                du -= round(du / 32.0) * 32.0
                dv -= round(dv / 32.0) * 32.0
                lk = _leaf(du, dv, ang, ln, wd)
                if lk is not None:
                    res = (LEAF, lk + 1)
                    hit = True
                    break
        if not hit:
            for (bx, by) in ((18.0, 14.5), (15.5, 29.0), (30.5, 16.0)):
                du, dv = lu - bx, lv - by
                d = math.hypot(du, dv)
                if d < 0.7:
                    res = (YELLOWP, 5)
                elif d < 1.8 and (math.atan2(dv, du) * 5 / (2 * math.pi)) % 1.0 < 0.6:
                    res = (CROCHET, 6)
        pl, kk = res
        if fade:
            fv = vn(u / 7.0, v / 7.0, seed * 0.3, seed + 7)
            if fv > 1 - fade * 0.5:
                kk += 1
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
        elif shape == 'drape_top':                              # far half of the disc, squashed onto a top face
            R = w / 2.0
            q = _Q()
            q.i, q.j = ctx.i, (h - 1 - ctx.j) * R / max(1.0, h) * 0.9
            c = crochet_disc(q, w / 2.0, -0.5, R, seed)
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


# ============================================================================================ LIVING
def seat_wear(tone, cx=8.0, cz=7.0, rx=5.0, rz=4.0, seed=0):
    """Wrap an upholstery tone: the place where someone always sits is darker and shinier on the top face."""
    def t(ctx):
        r = tone(ctx)
        if r is None or ctx.face != 'up' or type(r[0]) is not list:
            return r
        d = ((ctx.pos[0] - cx) / rx) ** 2 + ((ctx.pos[2] - cz) / rz) ** 2
        if d < 1.0 and hh(ctx.i, ctx.j, seed) < 0.75 - d * 0.5:
            return (r[0], r[1] - 1)
        return r
    return t


def doily_drape(x0, x1, ytop, z, depth=2.4, hang=3.0, seed=0, top=True):
    """Crocheted doily laid over the top of a backrest (top plane) and hanging down its front (drape plane at z)."""
    P = [plane((x0, ytop - hang, z - 0.05), (x1, ytop + 0.05, z - 0.05), fin(doily_tone('drape', seed), ao=0, dust=0.3),
               faces=('north', 'south'))]
    if top:
        P.append(plane((x0, ytop + 0.05, z - 0.05), (x1, ytop + 0.05, z + depth),
                       fin(doily_tone('drape_top', seed), ao=0, dust=0.4), faces=('up', 'down')))
    return P


def sofa_parts(arms, off, doily=True, seed=0):
    """Floral 70s sofa segment. arms: subset of ('w', 'e') = armrest at x=0 / x=16 side. Sitter looks north."""
    up = lambda sd, fade=0.0: fin(outline(floral(seed + sd, off, fade)))
    mBase = up(1)
    mSeat = fin(outline(seat_wear(floral(seed + 2, off, 0.5), cx=8.0, cz=6.0, seed=seed + 3)))
    mBack = up(4, 0.2)
    mArm = up(5, 0.8)
    mFoot = fin(outline(lustre(CAOBA, base=3, seed=seed + 7, axis=1)))
    xa = 2.8 if 'w' in arms else 0.0
    xb = 13.2 if 'e' in arms else 16.0
    ga = 0.15 if 'w' not in arms else 0.0      # tiny gap at block seams so the cushions read separately
    gb = 0.15 if 'e' not in arms else 0.0
    P = [
        box((0 if 'w' not in arms else 0.4, 1.6, 1.4), (16 if 'e' not in arms else 15.6, 5.2, 15.6), mBase),   # base / skirt
        box((xa + ga, 5.2, 1.6), (xb - gb, 8.0, 12.4), mSeat),                                                # seat cushion
        box((xa + ga, 5.5, 1.0), (xb - gb, 7.7, 1.6), mSeat),                                                 # rounded front
        box((0 if 'w' not in arms else 0.4, 5.2, 13.0), (16 if 'e' not in arms else 15.6, 13.4, 15.6), mBack),  # back frame
        box((xa + ga, 8.0, 10.6), (xb - gb, 13.6, 13.0), mBack),                                              # back cushion
        box((xa + ga + 0.3, 13.6, 11.0), (xb - gb - 0.3, 14.2, 12.8), mBack),                                 # cushion top roll
    ]
    for side in arms:
        x0 = 0.0 if side == 'w' else 13.2
        P += [box((x0 + 0.2, 1.6, 1.0), (x0 + 2.6, 10.2, 15.6), mArm),                                       # armrest
              box((x0 - 0.1 if side == 'w' else x0 + 0.1, 10.2, 0.8), (x0 + 2.7 if side == 'w' else x0 + 2.9, 11.8, 15.6), mArm),  # roll
              box((x0 + 0.5, 0.0, 1.8), (x0 + 1.9, 1.6, 3.2), mFoot), box((x0 + 0.5, 0.0, 13.6), (x0 + 1.9, 1.6, 15.0), mFoot)]
    if doily:
        P += doily_drape(4.0, 12.0, 14.2, 11.0, depth=1.8, hang=3.6, seed=seed + 9)
    return P


def armchair_parts(seed=31, doilies=True):
    P = sofa_parts(('w', 'e'), (48, 0, 0), doily=doilies, seed=seed)
    if doilies:
        for x0 in (0.0, 13.2):
            P.append(plane((x0 - 0.05, 11.85, 1.2), (x0 + 2.85, 11.85, 5.2), fin(doily_tone('oval', seed + int(x0)), ao=0, dust=0.3),
                           faces=('up', 'down')))
            P.append(plane((x0 - 0.05, 9.4, 0.75), (x0 + 2.85, 11.8, 0.75), fin(doily_tone('drape', seed + 3 + int(x0)), ao=0, dust=0),
                           faces=('north', 'south')))
    return P


def magazine_tone(col, seed=0):
    """Magazine / book stack sides: page edges; covers with a title band and a photo block."""
    def t(ctx):
        if ctx.face in ('north', 'south', 'west', 'east'):
            return (PAPER, 6 if ctx.j % 2 else 5)
        i, j, w, h = ctx.i, ctx.j, ctx.w, ctx.h
        if j < 2:
            return (col, 2) if i % 4 else (PAPER, 7)
        if 2 < j < h - 2 and 1 < i < w - 2:
            return (SKIN, 4) if (i + j) % 5 else (HAIR, 3)
        return (col, 4)
    return t


def mesa_ratona_parts():
    """70s coffee table in lustred wood: tapered legs, magazine shelf, doily with a glass candy dish and the remote."""
    mTop = fin(lustre(CAOBA, base=4, seed=101, boards=(2, 12), worn_pal=RAW, wear=0.3))
    mW = fin(lustre(CAOBA, base=4, seed=103))
    mL = fin(outline(lustre(CAOBA, base=3, seed=105, axis=1)))
    P = [box((0.8, 7.0, 2.6), (15.2, 8.0, 13.4), mTop),
         box((1.6, 6.0, 3.4), (14.4, 7.0, 4.0), mW), box((1.6, 6.0, 12.0), (14.4, 7.0, 12.6), mW),
         box((1.6, 6.0, 4.0), (2.2, 7.0, 12.0), mW), box((13.8, 6.0, 4.0), (14.4, 7.0, 12.0), mW),
         box((2.2, 1.8, 3.6), (13.8, 2.4, 12.4), mW)]                                                  # shelf
    for (x, z) in ((1.6, 3.4), (13.2, 3.4), (1.6, 11.4), (13.2, 11.4)):
        P += [box((x, 2.4, z), (x + 1.2, 6.0, z + 1.2), mL), box((x + 0.15, 0.0, z + 0.15), (x + 1.05, 2.4, z + 1.05), mL)]
    for n, col in enumerate((REDP, CELESTE, YELLOWP)):                                                 # magazines
        P.append(box((3.0 + n * 0.5, 2.4 + n * 0.3, 4.6 + n * 0.3), (9.0 + n * 0.4, 2.7 + n * 0.3, 11.0 - n * 0.2),
                     fin(magazine_tone(col, n), ao=0.6, dust=0.6)))
    P.append(plane((3.6, 8.03, 4.2), (12.4, 8.03, 11.8), fin(doily_tone('disc', 107), ao=0, dust=0.4), faces=('up',)))
    mGl = fin(lambda c: (GLASS_J, 5 if c.face == 'up' else (6 if c.i == 1 else 4)), ao=0.2, dust=0.3)
    P += [box((6.0, 8.05, 6.2), (10.0, 8.6, 10.2), mGl), box((5.4, 8.6, 5.6), (10.6, 9.6, 10.8), mGl),    # candy dish
          box((6.2, 9.0, 6.6), (7.8, 9.8, 7.8), fin(flat(REDP, 6), ao=0)), box((8.2, 9.0, 8.4), (9.6, 9.8, 9.6), fin(flat(YELLOWP, 5), ao=0)),
          box((7.2, 9.0, 8.0), (8.4, 9.9, 9.0), fin(flat(CELESTE, 4), ao=0))]
    mR = fin(lambda c: (BLACKP, 3) if c.face != 'up' else ((REDP, 5) if (c.j == 1 and c.i == 1) else
                                                            ((GRAPH, 6) if (c.j % 2 == 1 and c.i % 2 == 1) else (BLACKP, 4))), ao=0.4)
    P.append(box((11.6, 8.0, 9.0), (13.0, 8.6, 13.2), mR, rot=('y', 22.5, (12.3, 8.0, 11.1))))       # remote
    return P


# ------------------------------------------------------------------------------------------------ CRT TV
def tv_novela():
    """22x19 telenovela frame: a woman with big hair confronting a mustached man, warm drawing-room light."""
    cv = Canvas(22, 19, hx('#5a3424'))
    for y in range(19):
        for x in range(22):
            c = mix(hx('#7a4a2c'), hx('#2c1812'), y / 19.0 * 0.6 + abs(x - 6) / 22.0 * 0.5)
            if 13 <= x <= 20 and 1 <= y <= 9:
                c = mix(hx('#d8a868'), hx('#8a5a34'), (y - 1) / 8.0)        # lamp-lit curtain behind him
            cv.set(x, y, c)
    sk, skd = hx('#e0a888'), hx('#a8705a')
    # her: big dark hair, red lips, gold earring (left)
    cv.ellipse(6.0, 7.5, 5.2, 6.2, hx('#1c0f0c'))
    cv.ellipse(6.6, 9.2, 3.0, 4.2, sk)
    cv.rect(4, 13, 10, 19, hx('#9a1e2a'))              # red dress
    cv.rect(5, 12, 9, 14, sk)
    cv.set(5, 8, hx('#1a1010'))
    cv.set(8, 8, hx('#1a1010'))
    cv.set(5, 7, hx('#3a2018'))
    cv.set(8, 7, hx('#3a2018'))
    cv.rect(6, 11, 8, 12, hx('#c0202c'))               # lips
    cv.set(3, 10, hx('#e8c050'))                       # earring
    cv.set(7, 10, skd)
    # him: profile on the right, mustache, slicked hair, dark suit
    cv.ellipse(16.2, 8.5, 2.8, 3.6, sk)
    cv.ellipse(16.8, 6.0, 3.0, 2.0, hx('#120a08'))
    cv.rect(14, 10, 16, 11, hx('#2a1810'))             # mustache
    cv.set(14, 8, hx('#1a1010'))
    cv.rect(12, 13, 22, 19, hx('#1a1a22'))             # suit
    cv.rect(15, 12, 18, 14, hx('#e8e4dc'))             # shirt collar
    cv.set(16, 14, hx('#7a1a1a'))
    cv.text(F35, '9', 19, 1, hx('#f0f0f0'))           # channel bug
    for y in range(19):
        for x in range(22):
            c = cv.px[y][x]
            if y % 2:
                c = mix(c, hx('#000000'), 0.18)        # scanlines
            v = ((x - 10.5) / 11.0) ** 2 + ((y - 9) / 9.5) ** 2
            c = mix(c, hx('#000000'), max(0.0, v - 0.55) * 0.6)
            if x + y < 7 and (x + y) % 2 == 0:
                c = mix(c, hx('#ffffff'), 0.22)        # glass glare
            cv.px[y][x] = c
    return cv


def tv_static(seed=3):
    """Snow: random grey per pixel, rolling bright band, a face that is almost there."""
    cv = Canvas(22, 19, hx('#808080'))
    for y in range(19):
        band = 0.25 if 7 <= y <= 9 else 0.0
        for x in range(22):
            v = hh(x, y, seed)
            v = v * 0.85 + band + (hh(y, seed, 5) - 0.5) * 0.15
            # the faint face of a porcelain doll: two dark eyes and a stitched mouth
            fx, fy = (x - 11) / 4.5, (y - 9.5) / 5.5
            if fx * fx + fy * fy < 1.0:
                v = v * 0.75 + 0.22
            if (x in (9, 13) and y == 8) or (y == 12 and 9 <= x <= 13 and x % 2):
                v *= 0.35
            g = int(max(0, min(1, v)) * 235 + 10)
            c = (g, g, int(g * 1.04) if g < 245 else g, 255)
            if y % 2:
                c = mix(c, hx('#000000'), 0.15)
            cv.px[y][x] = c
    return cv


def tv_off():
    cv = Canvas(22, 19, hx('#1c211f'))
    for y in range(19):
        for x in range(22):
            v = ((x - 10.5) / 11.0) ** 2 + ((y - 9) / 9.5) ** 2
            c = mix(hx('#2c3532'), hx('#0e1110'), min(1.0, v * 0.9))
            if 2 <= x + y * 0.5 <= 4 and y < 9:
                c = mix(c, hx('#7c8a86'), 0.45)        # window reflection on the curved glass
            if hh(x, y, 9) < 0.05:
                c = mix(c, hx('#8a8478'), 0.4)         # dust
            cv.px[y][x] = c
    return cv


def tv_parts(state):
    """CRT 21" with rabbit-ear antenna and a doily + porcelain poodle on top, on a lustred low cabinet with a
    cable box. state: 'novela' | 'estatica' | 'apagada'. The screen is emissive when on."""
    mCab = fin(panels(lustre(CAOBA, base=4, seed=121, axis=1), lustre(CAOBA, base=4, seed=122), rects=((2, 2, -2, -2),),
                      faces=('north',)))
    mTop = fin(lustre(CAOBA, base=4, seed=123, boards=(2, 14)), dust=0.8)
    mW = fin(lustre(CAOBA, base=3, seed=124))
    mP = fin(smooth(GRAPH, base=3, seed=125, grime=0.0), dust=1.2)

    def bezel(ctx):
        if ctx.face == 'north' and ctx.j >= ctx.h - 4:
            i = ctx.i
            if ctx.j in (ctx.h - 3, ctx.h - 2) and i > ctx.w - 8 and i % 2 == 0:
                return (NICKEL, 5)                                  # buttons
            if ctx.j == ctx.h - 3 and i == ctx.w - 10:
                return hx('#40e060') if state != 'apagada' else hx('#a02020')   # power LED
            if ctx.j in (ctx.h - 3, ctx.h - 2) and 3 <= i < 13 and i % 2:
                return (BLACKP, 1)                                  # speaker slots
            return (GRAPH, 4)
        if ctx.face in ('west', 'east') and ctx.j % 3 == 0 and 3 < ctx.i < ctx.w - 3 and ctx.j < ctx.h * 0.6:
            return (BLACKP, 2)                                      # vents
        return smooth(GRAPH, base=3, seed=126, grime=0.0)(ctx)
    mBz = fin(bezel, dust=1.2)
    cv = {'novela': tv_novela, 'estatica': tv_static, 'apagada': tv_off}[state]()
    on = state != 'apagada'
    mScr = fin(canvas_tone(cv, other=lambda c: (BLACKP, 2)), ao=0, dust=0 if on else 0.6)
    P = [
        box((0.4, 0.0, 2.4), (15.6, 1.0, 15.2), mW),                                    # plinth
        box((0.6, 1.0, 2.0), (15.4, 8.4, 15.4), mCab),                                  # cabinet carcass
        box((0.2, 8.4, 1.6), (15.8, 9.2, 15.6), mTop),                                  # top board
        box((1.0, 1.4, 1.6), (5.6, 8.0, 2.0), mCab), box((10.4, 1.4, 1.6), (15.0, 8.0, 2.0), mCab),   # doors
        box((5.6, 1.4, 2.0), (10.4, 8.0, 2.05), M_DARK, faces=('north',)),             # open middle bay (dark)
        box((5.9, 4.6, 2.2), (10.1, 5.6, 7.0), fin(lambda c: (BLACKP, 3) if not (c.face == 'north' and c.j == 1 and c.i in (2, 3))
                                                   else hx('#4cff70'), ao=0.5)),           # cable box with a green LED
        box((6.0, 1.4, 2.4), (10.0, 4.4, 6.0), fin(magazine_tone(DENIM, 2), ao=0.6)),   # DVDs / VHS
        box((4.8, 4.4, 1.3), (5.2, 5.6, 1.6), M_BRASS), box((10.8, 4.4, 1.3), (11.2, 5.6, 1.6), M_BRASS),   # knobs
        # the set
        box((1.6, 9.2, 3.2), (14.4, 21.2, 12.0), mBz),                                  # cabinet of the CRT
        box((3.4, 10.0, 12.0), (12.6, 19.6, 14.0), mP), box((5.0, 11.4, 14.0), (11.0, 18.0, 15.2), mP),   # tube neck
        box((2.6, 11.4, 2.9), (13.4, 20.4, 3.2), mScr, faces=('north',), shade=not on),  # screen
        box((1.6, 20.4, 2.8), (14.4, 21.2, 3.2), mBz), box((1.6, 9.2, 2.8), (14.4, 11.4, 3.2), mBz),     # bezel
        box((1.6, 11.4, 2.8), (2.6, 20.4, 3.2), mBz), box((13.4, 11.4, 2.8), (14.4, 20.4, 3.2), mBz),
        plane((2.8, 21.24, 4.0), (11.2, 21.24, 11.4), fin(doily_tone('disc', 127), ao=0, dust=0.5), faces=('up',)),
        # rabbit ears
        box((5.6, 21.2, 6.4), (9.0, 22.2, 9.4), fin(smooth(BLACKP, base=3, seed=128), dust=1.0)),
        box((7.05, 22.2, 7.65), (7.55, 31.4, 8.15), M_CHROME, rot=('z', 22.5, (7.3, 22.2, 7.9))),
        box((7.05, 22.2, 7.65), (7.55, 30.2, 8.15), M_CHROME, rot=('z', -45, (7.3, 22.2, 7.9))),
    ]
    # porcelain poodle on the doily
    mPo = fin(lambda c: (PORCELAIN, 6 if c.face == 'up' else 5), ao=0.5, dust=0.6)
    P += [box((10.2, 21.2, 7.0), (12.6, 22.4, 8.2), mPo), box((10.4, 22.4, 7.2), (11.4, 23.8, 8.0), mPo),
          box((10.0, 23.6, 6.9), (11.6, 24.8, 8.3), mPo), box((12.2, 22.4, 7.3), (12.8, 23.4, 7.9), mPo),
          box((10.4, 21.2, 7.0), (10.9, 21.2, 8.2), mPo, faces=('up',)),
          box((10.1, 24.0, 6.85), (10.4, 24.4, 7.1), fin(flat(BAKE, 1), ao=0)), box((11.2, 24.0, 6.85), (11.5, 24.4, 7.1), fin(flat(BAKE, 1), ao=0))]
    return P


# ------------------------------------------------------------------------------------------------ standing lamp
def shade_tone(lit, seed=0, p_off=SHADE_L, p_on=SHADE_LIT):
    """Pleated fabric lampshade: vertical pleats, a darker band at the rims, scorch spot; lit = warm glow."""
    def t(ctx):
        if ctx.face in ('up', 'down'):
            return (p_on, 2) if lit else (p_off, 2)
        pl = ctx.i % 3
        k = (5 if lit else 5) + (1 if pl == 0 else (-1 if pl == 2 else 0))
        if ctx.j <= 0 or ctx.j >= ctx.h - 1:
            k -= 2
        if lit:
            k += 1 if ctx.t > 0.55 else 0
        if not lit and vn(ctx.i / 3.0, ctx.j / 3.0, FI[ctx.face], seed) > 0.72:
            k -= 1                                              # yellowed / scorched patches
        return (p_on if lit else p_off, k)
    return t


def lamp_shade(x0, x1, z0, z1, y0, y1, lit, seed=0, taper=1.0, th=0.35):
    """Open lampshade: four thin walls in two tiers (tapering) so the bulb is seen from below."""
    m = fin(shade_tone(lit, seed), ao=0, dust=0 if lit else 0.8)
    P = []
    ym = (y0 + y1) / 2
    for n, (a, b, ins) in enumerate(((y0, ym, 0.0), (ym, y1, taper))):
        xa, xb, za, zb = x0 + ins, x1 - ins, z0 + ins, z1 - ins
        P += [box((xa, a, za), (xb, b, za + th), m, shade=not lit), box((xa, a, zb - th), (xb, b, zb), m, shade=not lit),
              box((xa, a, za + th), (xa + th, b, zb - th), m, shade=not lit), box((xb - th, a, za + th), (xb, b, zb - th), m, shade=not lit)]
    return P


def bulb_parts(x, y, z, lit, r=1.0, h=2.2):
    mB = fin(lambda c: (OPAL_LIT, 6 + (c.edge() > 0)) if lit else (OPAL, 5 + (c.edge() > 0)), ao=0, dust=0 if lit else 0.5)
    mS = fin(brass(NICKEL, base=4, seed=17), ao=0)
    return [box((x - r, y, z - r), (x + r, y + h, z + r), mB, shade=not lit),
            box((x - r * 0.6, y + h, z - r * 0.6), (x + r * 0.6, y + h + 1.0, z + r * 0.6), mS)]


def lampara_pie_parts(lit):
    mB = fin(brass(seed=131, base=4, tarnish=0.5), dust=0.6)
    P = [box((4.6, 0.0, 4.6), (11.4, 0.6, 11.4), mB), box((5.8, 0.6, 5.8), (10.2, 1.4, 10.2), mB),
         box((7.4, 1.4, 7.4), (8.6, 22.6, 8.6), mB), box((7.0, 11.0, 7.0), (9.0, 12.4, 9.0), mB),       # pole + knop
         box((7.0, 22.6, 7.0), (9.0, 23.4, 9.0), mB)]
    P += bulb_parts(8.0, 23.4, 8.0, lit, r=1.1, h=2.4)
    P += lamp_shade(2.6, 13.4, 2.6, 13.4, 21.6, 30.4, lit, seed=133, taper=1.4)
    P += [box((8.8, 21.0, 7.8), (9.1, 23.4, 8.1), M_BRASS), box((8.6, 20.4, 7.6), (9.3, 21.0, 8.3), M_BRASS)]   # pull chain
    return P


# ------------------------------------------------------------------------------------------------ Nona's rocking chair
def mecedora_parts():
    """The Nona's rocking chair: light oak, curved rockers, spindle back reclined 22.5 deg, knitted red cushion and a
    granny-square blanket folded over the left arm. The sitter looks north."""
    mW = fin(outline(wood(ROBLE_CL, seed=141, base=4, worn_pal=RAW, wear=0.6)))
    mT = fin(wood(ROBLE_CL, seed=143, base=5))
    mK = fin(knit(WOOL_R, base=5, seed=145), dust=0.3)
    mG = fin(granny(147, size=6), dust=0.4)
    P = []
    for x in (2.2, 12.6):
        P += [box((x, 0.0, 2.6), (x + 1.2, 1.2, 13.4), mT),                                              # rocker
              box((x, 0.0, -2.0), (x + 1.2, 1.2, 2.8), mT, rot=('x', 22.5, (x + 0.6, 0.6, 2.8))),
              box((x, 0.0, 13.2), (x + 1.2, 1.2, 17.6), mT, rot=('x', -22.5, (x + 0.6, 0.6, 13.2))),
              box((x + 0.1, 1.2, 3.2), (x + 1.1, 15.6, 4.4), mW),                                         # front post up to the arm
              box((x + 0.1, 1.2, 11.8), (x + 1.1, 9.0, 13.0), mW),                                        # back leg
              box((x - 0.5, 15.0, 1.8), (x + 1.7, 16.0, 13.4), mT),                                       # arm
              box((x + 0.2, 3.0, 4.4), (x + 1.0, 3.8, 11.8), mW)]                                         # side stretcher
    P += [box((3.4, 8.4, 2.8), (12.6, 9.4, 13.0), mW),                                                    # seat
          box((3.6, 9.4, 3.2), (12.4, 10.8, 12.4), mK),                                                   # knitted cushion
          box((4.2, 10.8, 3.8), (11.8, 11.2, 11.8), mK),
          box((3.4, 3.0, 3.6), (12.6, 3.8, 4.2), mW)]                                                     # front stretcher
    org = (8.0, 9.4, 12.4)
    rot = ('x', 22.5, org)
    P += [box((2.3, 9.4, 11.8), (3.5, 26.4, 13.0), mW, rot=rot), box((12.5, 9.4, 11.8), (13.7, 26.4, 13.0), mW, rot=rot),
          box((2.0, 26.4, 11.6), (3.8, 27.4, 13.2), mT, rot=rot), box((12.2, 26.4, 11.6), (14.0, 27.4, 13.2), mT, rot=rot),
          box((3.5, 22.4, 11.9), (12.5, 25.6, 12.9), fin(panels(wood(ROBLE_CL, seed=149, base=4, axis=0), rects=((1, 1, -1, -1),),
                                                                faces=('north', 'south'), bevel=0)), rot=rot),   # crest rail
          box((3.5, 12.6, 11.9), (12.5, 13.6, 12.9), mW, rot=rot),
          box((4.2, 13.6, 11.0), (11.8, 20.0, 11.9), mK, rot=rot)]                                        # knitted back pad
    for x in (5.0, 7.6, 10.2):
        P.append(box((x, 13.6, 12.05), (x + 0.8, 22.4, 12.75), mW, rot=rot))                             # spindles
    # granny blanket folded over the (sitter's) left arm = x small side
    P += [box((1.5, 16.0, 4.2), (3.9, 16.4, 10.8), mG), box((1.1, 8.8, 4.2), (1.5, 16.4, 10.8), mG),
          box((3.9, 13.2, 4.2), (4.3, 16.4, 10.8), mG), box((1.1, 8.2, 4.6), (1.5, 8.8, 10.4), mG)]
    return P


# ------------------------------------------------------------------------------------------------ doilies, vase (sobre mesa)
def carpetita_parts(florero=False):
    P = [plane((2.6, -3.96, 2.6), (13.4, -3.96, 13.4), fin(doily_tone('disc', 151), ao=0, dust=0.4), faces=('up',))]
    if florero:
        mGl = fin(lambda c: (GLASS_J, 4 + (c.i % 3 == 1) + (c.face == 'up')), ao=0, dust=0.4)
        P += [box((6.6, -4.0, 6.6), (9.4, -3.5, 9.4), mGl), box((7.0, -3.5, 7.0), (9.0, 0.2, 9.0), mGl),
              box((6.7, 0.2, 6.7), (9.3, 0.7, 9.3), mGl)]
        mSt = fin(flat(LEAF, 3), ao=0)
        for n, (dx, dz, ht, col) in enumerate(((-1.4, 0.4, 3.6, GERAN), (1.2, -0.6, 4.6, PINK), (0.2, 1.2, 3.0, YELLOWP),
                                               (-0.4, -1.2, 5.2, ROSE))):
            x, z = 8.0 + dx, 8.0 + dz
            P += [box((x - 0.12, 0.7, z - 0.12), (x + 0.12, 0.7 + ht, z + 0.12), mSt),
                  box((x - 0.7, 0.7 + ht - 0.2, z - 0.7), (x + 0.7, 0.7 + ht + 0.9, z + 0.7),
                      fin(lambda c, col=col: (col, 4 + ((c.i + c.j) % 2) + (c.face == 'up')), ao=0, dust=0.2))]
        P += [box((7.9, 1.6, 7.0), (10.0, 1.8, 7.5), fin(flat(LEAF, 4), ao=0), rot=('z', 22.5, (7.9, 1.6, 7.3))),
              box((6.0, 2.2, 8.6), (7.9, 2.4, 9.1), fin(flat(LEAF, 5), ao=0), rot=('z', -22.5, (7.9, 2.2, 8.8)))]
    return P


# ------------------------------------------------------------------------------------------------ family photos
PH_SKIN = [hx('#8a5a4a'), hx('#b98470'), hx('#d8a891'), hx('#ebc6b0')]


FAM = {
    'jorge': (['..hhh..', '.hssss.', '.sesse.', '.smmms.', '..sss..', 'kKkKkKk', 'kKkKkKk', 'KkKkKkK', 'KkKkKkK', '.kKkKk.',
               '.ppppp.', '.pp.pp.', '.pp.pp.', '.pp.pp.', '.ff.ff.'],
              {'h': hx('#2a1a14'), 's': PH_SKIN[2], 'e': hx('#1a1010'), 'm': hx('#2a1a14'), 'k': hx('#8ab8dc'), 'K': hx('#eef2f4'),
               'p': hx('#3a3a48'), 'f': hx('#1a1414')}),
    'marta': (['.rhrh.', 'rhhhhr', '.sess.', '.ssss.', '..ll..', '.BBBB.', 'BBBBBB', 'BBwwBB', 'BBBBBB', '.BBBB.', '.BBBB.',
               '..ss..', '..pp..'],
              {'r': hx('#f080a8'), 'h': hx('#5a3020'), 's': PH_SKIN[2], 'e': hx('#1a1010'), 'l': hx('#b04050'), 'B': hx('#e8a0b8'),
               'w': hx('#c87890'), 'p': hx('#f0c0d0')}),
    'nona': (['..oo..', '.hhhh.', '.gsgs.', '.ssss.', '..ss..', '.CCCC.', 'CvvvvC', 'CvvvvC', '.vvvv.', '.vvvv.', '..ss..',
              '..dd..'],
             {'o': hx('#b8b4ae'), 'h': hx('#a8a49e'), 'g': hx('#ffffff'), 's': PH_SKIN[3], 'C': hx('#6a1424'),
              'v': hx('#7a8a5a'), 'd': hx('#5a4a40')}),
    'lucia': (['.hhh.', 'hssh.', 'hesh.'[:5], '.ss..', 'RRRR.', 'RRRR.', 'RRRR.', '.ss..', '.pp..'],
              {'h': hx('#5a3a22'), 's': PH_SKIN[2], 'e': hx('#1a1010'), 'R': hx('#c42a2a'), 'p': hx('#e0a0c0')}),
    'toti': (['.hhhh.', 'hhhhhh', '.sess.', '.ssss.', '.g..n.', 'HHHHHH', 'HHHHHH', 'HHHHHH', 'HHHHHH', '.jjjj.', '.jj.jj',
              '.jj.jj', '.jj.jj', '.ww.ww'],
             {'h': hx('#1a1210'), 's': PH_SKIN[1], 'e': hx('#1a1010'), 'g': hx('#30ff80'), 'n': hx('#ff30c0'), 'H': hx('#202024'),
              'j': hx('#34466a'), 'w': hx('#f0f0f0')}),
}


def draw_chori(cv, x, y, stare=True):
    """Choripan, the dachshund: long and low, red sweater with a white C, ears, two catch-light eyes AT THE CAMERA."""
    rows = ['..ee......',
            '.eHHe.....',
            'oHwHwo....',
            '.HnnHSSSSSS.',
            '..HHSCSSSSSt',
            '...SSSSSSS.t',
            '...l.l..l.l.']
    pal_ = {'e': hx('#4a2414'), 'H': hx('#8a4a24'), 'o': hx('#4a2414'), 'w': hx('#f8f8f0') if stare else hx('#3a2010'),
            'n': hx('#140a08'), 'S': hx('#c42a2a'), 'C': hx('#f0f0f0'), 't': hx('#8a4a24'), 'l': hx('#6a3418')}
    cv.ascii(x, y, rows, pal_)


def draw_ofelia(cv, x, y):
    rows = ['.hhh.', 'hppph', 'hepeh', '.prp.', 'WWWWW', 'WWWWW', '.WWW.', '.p.p.']
    cv.ascii(x, y, rows, {'h': hx('#120c0a'), 'p': hx('#f0e6dc'), 'e': hx('#2a2a40'), 'r': hx('#c01818'), 'W': hx('#ece6da')})


def photo_grade(c, kind='color'):
    r, g, b = c[0], c[1], c[2]
    if kind == 'sepia':
        l = (r * 0.3 + g * 0.55 + b * 0.15)
        return (min(255, int(l * 0.95 + 38)), min(255, int(l * 0.82 + 26)), min(255, int(l * 0.6 + 14)), 255)
    if kind == 'bw':
        l = int(r * 0.3 + g * 0.55 + b * 0.15)
        return (min(255, int(l * 0.9 + 18)), min(255, int(l * 0.9 + 18)), min(255, int(l * 0.88 + 20)), 255)
    if kind == 'faded':
        return (min(255, int(r * 0.8 + 50)), min(255, int(g * 0.76 + 40)), min(255, int(b * 0.7 + 42)), 255)
    return (min(255, int(r * 0.95 + 8)), min(255, int(g * 0.95 + 6)), min(255, int(b * 0.92 + 8)), 255)


def finish_photo(cv, kind='color', seed=0, border=0):
    for y in range(cv.h):
        for x in range(cv.w):
            if border and (x < border or y < border or x >= cv.w - border or y >= cv.h - border):
                continue
            c = photo_grade(cv.px[y][x], kind)
            v = ((x - cv.w / 2) / (cv.w / 2)) ** 2 + ((y - cv.h / 2) / (cv.h / 2)) ** 2
            if v > 0.7:
                c = mix(c, hx('#3a2a20'), (v - 0.7) * 0.3)
            if hh(x, y, seed) < 0.008:
                c = mix(c, hx('#ffffff'), 0.4)
            cv.px[y][x] = c
    return cv


def photo_canvas(kind):
    if kind in ('familia', 'familia_ofelia'):
        cv = Canvas(40, 24, hx('#c8b898'))
        for y in range(24):
            for x in range(40):
                c = hx('#d6c8a6') if y < 15 else hx('#7a6a54')
                if y < 15 and (x // 5 + y // 5) % 2 == 0:
                    c = mix(c, hx('#c4b490'), 0.5)                 # living-room wallpaper behind them
                if 26 <= x <= 37 and 2 <= y <= 11:
                    c = hx('#8aa8c0') if (x + y) % 7 else hx('#9ab8cc')   # window
                cv.set(x, y, c)
        for x in range(2, 38):
            for y in range(13, 17):
                cv.set(x, y, mix(hx('#a85a3a'), hx('#c0784a'), ((x // 3 + y) % 3) / 3.0))   # the floral sofa
        order = [('toti', 2, 2), ('jorge', 9, 3), ('nona', 17, 9), ('marta', 24, 6), ('lucia', 31, 11)]
        for name, x, y in order:
            rows, pl = FAM[name]
            cv.ascii(x, y, rows, pl)
        draw_chori(cv, 14, 17)
        if kind == 'familia_ofelia':
            draw_ofelia(cv, 26, 15)                               # she sits next to the next host
        cv.text(F35, '2025', 23, 18, hx('#f0a040'))               # camera date stamp
        return finish_photo(cv, 'color', 11)
    if kind == 'cumple':
        cv = Canvas(28, 22, hx('#e0c8a0'))
        for y in range(22):
            for x in range(28):
                cv.set(x, y, hx('#e8d4a8') if y < 11 else hx('#d8d0c0'))
        for (x, y, c) in ((3, 2, hx('#f04060')), (9, 1, hx('#40a0f0')), (19, 2, hx('#f0d040')), (24, 1, hx('#60d060'))):
            cv.ellipse(x, y + 1.5, 1.6, 2.0, c)                   # balloons
            cv.line(x, y + 3, x, y + 7, hx('#a0a0a0'))
        cv.rect(4, 12, 24, 16, hx('#f0f0f0'))                     # table cloth
        cv.rect(10, 9, 18, 12, hx('#f4e0e8'))                     # cake
        cv.rect(10, 9, 18, 10, hx('#e070a0'))
        for x in (11, 13, 15, 17):
            cv.set(x, 8, hx('#f0f0f0'))
            cv.set(x, 7, hx('#ffc040'))
        cv.text(F35, '8', 13, 9, hx('#c02060'))
        # family seen from behind / side, all looking at the cake
        backs = [(1, 5, hx('#2a1a14'), hx('#eef2f4')), (6, 4, hx('#5a3020'), hx('#e8a0b8')), (19, 5, hx('#1a1210'), hx('#202024')),
                 (23, 6, hx('#a8a49e'), hx('#6a1424'))]
        for (x, y, hc, bc) in backs:
            cv.rect(x, y, x + 4, y + 3, hc)
            cv.rect(x - 1, y + 3, x + 5, y + 9, bc)
        cv.rect(12, 4, 16, 7, hx('#5a3a22'))                      # Lucia behind the cake, eyes closed blowing
        cv.rect(12, 6, 16, 8, PH_SKIN[2])
        cv.set(13, 6, hx('#3a2020'))
        cv.set(15, 6, hx('#3a2020'))
        draw_chori(cv, 2, 14)                                     # the dog looks at YOU
        return finish_photo(cv, 'color', 12)
    if kind == 'choripan':
        cv = Canvas(18, 22, hx('#7a9a5a'))
        for y in range(22):
            for x in range(18):
                cv.set(x, y, mix(hx('#86a868'), hx('#4a6a3a'), y / 22.0) if (x * 3 + y) % 5 else hx('#5a7a44'))
        rows = ['....ee..ee....',
                '...eeHHHHee...',
                '..eeHHHHHHee..',
                '..eHHwHHwHHe..',
                '..eHHHHHHHHe..',
                '...eHHnnHHe...',
                '....HHHHHH....',
                '....HmmmmH....',
                '...SSScSSSS...',
                '..SSSCCCSSSS..',
                '..SSSSCSSSSS..',
                '..SSSSSSSSSS..',
                '..SSSSSSSSSS..',
                '...HH....HH...']
        cv.ascii(2, 4, rows, {'e': hx('#4a2414'), 'H': hx('#8a4a24'), 'w': hx('#ffffff'), 'n': hx('#140a08'),
                              'm': hx('#c06070'), 'S': hx('#c42a2a'), 'C': hx('#f0f0f0'), 'c': hx('#80c8e8')})
        cv.set(7, 7, hx('#140a08'))
        cv.set(10, 7, hx('#140a08'))
        return finish_photo(cv, 'color', 13)
    if kind == 'casamiento':
        cv = Canvas(20, 26, hx('#c8c0b0'))
        for y in range(26):
            for x in range(20):
                cv.set(x, y, mix(hx('#d8d0c0'), hx('#9a9080'), abs(x - 10) / 12.0))
        cv.ascii(3, 3, ['.hhh.', 'hssh.', '.ses.', '.ss..', 'DDDD.', 'DwDD.', 'DDDD.', 'DDDD.', 'DDDD.', '.DD..', '.DD..', '.DD..',
                        '.DD..', '.ff..'],
                 {'h': hx('#2a1a14'), 's': PH_SKIN[2], 'e': hx('#1a1010'), 'D': hx('#202028'), 'w': hx('#f0f0f0'), 'f': hx('#101010')})
        cv.ascii(10, 4, ['.hhhh.', 'hssssh', 'hesesh', '.ssss.', 'hh..hh', 'WWWWWW', 'WWWWWW', 'WWrWWW', 'WWWWWWW', 'WWWWWWWW',
                         'WWWWWWWW', 'WWWWWWWWW', 'WWWWWWWWW', 'WWWWWWWWW', 'WWWWWWWWWW'],
                 {'h': hx('#5a3020'), 's': PH_SKIN[2], 'e': hx('#1a1010'), 'W': hx('#f4f2ee'), 'r': hx('#e07090')})
        for y in range(26):
            for x in range(20):
                if hh(x, y, 4) < 0.02:
                    cv.set(x, y, hx('#ffffff'))
        return finish_photo(cv, 'faded', 14)
    if kind == 'nona_joven':
        cv = Canvas(18, 24, hx('#a8a8a0'))
        for y in range(24):
            for x in range(18):
                cv.set(x, y, mix(hx('#c0c0b8'), hx('#686860'), ((x - 9) ** 2 + (y - 10) ** 2) / 200.0))
        cv.ascii(5, 3, ['..hhh..', '.hhhhh.', 'hhsssh.', 'hseses.'[:7], '.sssss.', '..sms..', '..sss..', '.DDDDD.', 'DDDDDDD',
                        'DDDpDDD', 'DDDDDDD', 'DDDDDDD', '.DDDDD.', '.DDDDD.'],
                 {'h': hx('#201814'), 's': hx('#e0c8b0'), 'e': hx('#201010'), 'm': hx('#7a3030'), 'D': hx('#3a3a44'), 'p': hx('#e8e8e0')})
        return finish_photo(cv, 'bw', 15)
    if kind == 'nelida':
        # 1960: a little girl in a white dress holding the doll Ofelia (mouth sewn with red thread), sepia print with
        # a fountain-pen caption on the white border (cursive "Nelida y Ofelia" + a legible 1960).
        cv = Canvas(20, 30, hx('#efe6d2'))
        img = Canvas(16, 18, hx('#b8a888'))
        for y in range(18):
            for x in range(16):
                img.set(x, y, hx('#c8b898') if y < 12 else hx('#8a7a60'))
                if y < 12 and x % 4 == 0:
                    img.set(x, y, hx('#b4a484'))
        img.ascii(3, 1, ['..hhhh..', '.hhhhhh.', 'hhsssshh', 'h.esse.h', '..ssss..', '...ss...', '.WWWWWW.', 'WWWWWWWW',
                         'WsWWWWsW', 'WWOOOOWW', 'WWOooOWW', '.WOooOW.', '.WWOOWW.', '.WWWWWW.', '..s..s..', '..b..b..'],
                  {'h': hx('#2a1c14'), 's': hx('#e8d0b8'), 'e': hx('#201010'), 'W': hx('#f4f0e8'), 'O': hx('#1a1210'),
                   'o': hx('#f4ece4'), 'b': hx('#201010')})
        img.set(7, 11, hx('#a01818'))
        img.set(8, 11, hx('#a01818'))
        finish_photo(img, 'sepia', 16)
        for y in range(18):
            for x in range(16):
                cv.set(x + 2, y + 2, img.px[y][x])
        ink = hx('#2a2a6a')
        for x in range(2, 18):                                            # cursive "Nelida y Ofelia"
            y = 22 + int(round(math.sin(x * 1.9) * 1.0 + (0.6 if x % 5 == 0 else 0)))
            cv.set(x, y, ink)
            if x % 4 == 1:
                cv.set(x, y - 1, ink)
        cv.text(F35, '1960', 3, 24, ink)
        for y in range(30):
            for x in range(20):
                if x + y < 5 or hh(x, y, 9) < 0.01:
                    cv.set(x, y, lambda c: mix(c, hx('#b89a60'), 0.35))
        return cv
    raise ValueError(kind)


PHOTO_FRAMES = {   # kind -> (centre x, bottom y of the print, frame width, frame style); print size = canvas px / 2
    'familia': (8.0, 4.0, 1.0, 'dorado'),
    'familia_ofelia': (8.0, 4.0, 1.0, 'dorado'),
    'cumple': (8.0, 5.0, 0.8, 'blanco'),
    'choripan': (8.0, 3.0, 0.8, 'madera'),
    'casamiento': (8.0, 2.0, 1.0, 'plata'),
    'nona_joven': (8.0, 3.0, 1.1, 'oscuro'),
    'nelida': (8.0, 1.0, 0.9, 'oscuro'),
}


def photo_parts(kind):
    """Framed photo hanging on the wall (back of the frame against the wall opposite to facing)."""
    cx, y0, fw, style = PHOTO_FRAMES[kind]
    cv = photo_canvas(kind)
    x0, x1 = cx - cv.w / 4.0, cx + cv.w / 4.0
    y1 = y0 + cv.h / 2.0
    mFr = {'dorado': fin(brass(GOLD, base=4, seed=161, tarnish=0.4), dust=0.6),
           'blanco': fin(smooth(PLAST_W, base=6, seed=162), dust=0.6),
           'madera': fin(outline(wood(ROBLE, seed=163, base=4)), dust=0.6),
           'plata': fin(brass(NICKEL, base=5, seed=164, tarnish=0.5), dust=0.6),
           'oscuro': fin(outline(lustre(CAOBA, seed=165, base=3)), dust=0.6)}[style]
    mPh = fin(canvas_tone(cv, other=lambda c: (PAPER, 6)), ao=0, dust=0.15)
    zb = 15.0
    return [box((x0, y0, 15.45), (x1, y1, 15.55), mPh, faces=('north',)),
            box((x0 - fw, y0 - fw, zb), (x1 + fw, y0, 16.0), mFr), box((x0 - fw, y1, zb), (x1 + fw, y1 + fw, 16.0), mFr),
            box((x0 - fw, y0, zb), (x0, y1, 16.0), mFr), box((x1, y0, zb), (x1 + fw, y1, 16.0), mFr),
            box((x0, y0, 15.55), (x1, y1, 16.0), fin(flat(CARTON, 3), ao=0), faces=('south',))]


# ------------------------------------------------------------------------------------------------ gas wall heater
def heater_front_tone(lit):
    def t(ctx):
        i, j, w, h = ctx.i, ctx.j, ctx.w, ctx.h
        if ctx.face == 'up':
            if j % 2 == 0 and 2 <= i < w - 2 and j < h - 3:
                return (BAKE, 3)                                   # top grille slots
            return (ENAMEL, 5)
        if ctx.face != 'north':
            return smooth(ENAMEL, base=5, seed=171)(ctx)
        if j < 6 and 2 <= i < w - 2:
            if j % 2 == 1:
                return (BAKE, 2 + (j == 1))                        # louvres
            return (ENAMEL, 6 if hh(i, j) > 0.1 else 3)
        cx = w / 2
        if abs(i + 0.5 - cx) < 4.5 and h - 11 <= j < h - 4:     # mirilla (window) with the burner behind
            ii, jj = i + 0.5 - cx, j - (h - 11)
            if abs(ii) > 3.6 or jj in (0, 6):
                return (NICKEL, 5)
            if lit:
                if jj >= 4:
                    return T(FLAME_B, 4 + (abs(ii) < 1.5))
                if hh(i, j, 3) < 0.7:
                    return T(EMBER, 5 + (jj > 2) + (abs(ii) < 1.4))
                return T(EMBER, 4)
            if jj >= 4 and abs(ii) < 0.8:
                return T(FLAME_B, 5)                              # pilot only
            return (BAKE, 2)
        if j == h - 2 and i in (3, 4):
            return (BLACKP, 2)
        if 6 <= j <= 7 and w - 8 <= i < w - 3:
            return (NICKEL, 6) if j == 6 else (NICKEL, 4)         # name plate
        k = 5
        if j > h - 3:
            k -= 1
        if hh(i, j, 172) < 0.03:
            k -= 1
        return (ENAMEL, k)
    return t


def soot_stain_tone(seed=0, strength=1.0):
    """Dithered dark stain (cutout) rising from a heater/parrilla onto the wall."""
    def t(ctx):
        u = ctx.s * 2 - 1
        v = 1 - ctx.t
        d = abs(u) * 1.2 + v * 0.9 - 0.15 + (vn(ctx.i / 3.0, ctx.j / 3.0, 0.5, seed) - 0.5) * 0.5
        a = (1 - d) * strength
        if a <= 0 or bay(ctx.i, ctx.j) > a:
            return None
        return mix(hx('#2a2420'), hx('#4a4038'), 0.5 - a * 0.4)
    return t


def estufa_parts(lit):
    mB = fin(heater_front_tone(lit), ao=0.6, dust=0.8)
    mS = fin(smooth(ENAMEL, base=5, seed=173), dust=0.8)
    P = [box((2.0, 1.2, 10.4), (14.0, 13.6, 15.8), mB),
         box((2.6, 0.0, 11.0), (4.0, 1.2, 15.0), M_CHROME), box((12.0, 0.0, 11.0), (13.4, 1.2, 15.0), M_CHROME),
         box((12.0, 13.6, 13.0), (13.4, 14.4, 14.4), fin(smooth(BLACKP, base=3, seed=174))),          # knob
         box((10.0, 13.6, 13.4), (11.0, 14.0, 14.2), fin(flat(REDP, 5), ao=0)),                     # piezo button
         box((4.0, 13.6, 15.0), (6.0, 14.6, 16.0), mS),                                              # gas pipe to the wall
         plane((1.0, 13.6, 15.95), (15.0, 26.0, 15.95), fin(soot_stain_tone(175, 0.8), ao=0, dust=0), faces=('north',))]
    return P


# ============================================================================================ register: living
F('sillon_der', 'Sillón floreado (derecha)', 'Floral sofa (right end)', sofa_parts(('w',), (0, 0, 0), seed=11), sound='wool')
F('sillon_centro', 'Sillón floreado (centro)', 'Floral sofa (middle)', sofa_parts((), (16, 0, 0), seed=13), sound='wool')
F('sillon_izq', 'Sillón floreado (izquierda)', 'Floral sofa (left end)', sofa_parts(('e',), (32, 0, 0), seed=15), sound='wool')
F('sillon_individual', 'Sillón individual floreado', 'Floral armchair', armchair_parts(), sound='wool')
F('mesa_ratona', 'Mesa ratona con carpetita', 'Coffee table with a doily', mesa_ratona_parts())
F('tele_vieja', 'Tele vieja (telenovela)', 'Old CRT TV (soap opera)', tv_parts('novela'), light=6, sound='metal')
F('tele_vieja_estatica', 'Tele vieja (estática)', 'Old CRT TV (static)', tv_parts('estatica'), light=6, sound='metal')
F('tele_vieja_apagada', 'Tele vieja (apagada)', 'Old CRT TV (off)', tv_parts('apagada'), sound='metal')
F('lampara_pie', 'Lámpara de pie (encendida)', 'Standing lamp (lit)', lampara_pie_parts(True), light=12, directional=False)
F('lampara_pie_apagada', 'Lámpara de pie (apagada)', 'Standing lamp (off)', lampara_pie_parts(False), directional=False)
F('mecedora', 'Mecedora de la Nona', "Nona's rocking chair", mecedora_parts())
F('carpetita', 'Carpetita tejida (sobre mesa)', 'Crocheted doily (on a table)', carpetita_parts(), collision='none', sound='wool')
F('carpetita_florero', 'Carpetita con florero (sobre mesa)', 'Doily with a vase of plastic flowers (on a table)',
  carpetita_parts(True), collision='none', sound='glass')
for _k, _es, _en in (('familia', 'Foto de la familia Morales', 'Morales family photo'),
                     ('familia_ofelia', 'Foto de la familia (con Ofelia)', 'Family photo (Ofelia in it)'),
                     ('cumple', 'Foto del cumple de Lucía', "Photo of Lucia's birthday"),
                     ('choripan', 'Foto de Choripán', 'Photo of Choripan'),
                     ('casamiento', 'Foto del casamiento de Marta y Jorge', "Marta and Jorge's wedding photo"),
                     ('nona_joven', 'Foto de la Nona de joven', 'Photo of young Nona'),
                     ('nelida', 'Foto "Nélida y Ofelia, 1960"', 'Photo "Nelida and Ofelia, 1960"')):
    F(f'foto_{_k}', _es, _en, photo_parts(_k), env=('wall',), collision='none', sound='paper')
F('estufa', 'Estufa de tiro balanceado (prendida)', 'Balanced-flue gas heater (on)', estufa_parts(True), env=('wall',),
  light=6, sound='metal')
F('estufa_apagada', 'Estufa de tiro balanceado (piloto)', 'Balanced-flue gas heater (pilot only)', estufa_parts(False),
  env=('wall',), sound='metal')


# ============================================================================================ DINING
def turned_leg(x, z, y0, y1, m, w=1.4, rings=(0.25, 0.62)):
    """Square leg with turned rings (lathe beads) at fractions of its height."""
    P = [box((x, y0, z), (x + w, y1, z + w), m)]
    for f in rings:
        y = y0 + (y1 - y0) * f
        P.append(box((x - 0.2, y, z - 0.2), (x + w + 0.2, y + 0.8, z + w + 0.2), m))
    return P


def runner_tone(seed=0):
    """Crocheted table runner (cutout): open filet mesh with solid diamonds and a scalloped long edge."""
    def t(ctx):
        i, j, w, h = ctx.i, ctx.j, ctx.w, ctx.h
        if j < 1 or j >= h - 1:
            return T(CROCHET, 5) if i % 3 != 2 else None
        cx = (i % 10) - 4.5
        cy = j - h / 2 + 0.5
        dia = abs(cx) + abs(cy) * 1.4 < 4.0
        if dia:
            return T(CROCHET, 6 if (i + j) % 2 else 5)
        if (i % 2 == 0) or (j % 2 == 0):
            return T(CROCHET, 5)
        return None
    return t


def mesa_comedor_parts(kind):
    """Long lustred dining table (long axis = x, top at 12/16). kind 'extremo' (turned legs at the x=0 end) | 'centro'
    (with the crocheted runner). Three blocks: extremo + centro + extremo turned 180."""
    off = (0, 0, 0) if kind == 'extremo' else (16, 0, 0)
    mTop = fin(lustre(CAOBA, base=4, seed=201, axis=0, boards=(2, 10), off=off, worn_pal=RAW, wear=0.3))
    mW = fin(lustre(CAOBA, base=3, seed=203, off=off))
    mL = fin(outline(lustre(CAOBA, base=3, seed=205, axis=1)))
    x0 = 0.4 if kind == 'extremo' else 0.0
    P = [box((x0, 11.0, 0.6), (16, 12.0, 15.4), mTop),
         box((x0 + 1.0, 9.0, 1.6), (16, 11.0, 2.2), mW), box((x0 + 1.0, 9.0, 13.8), (16, 11.0, 14.4), mW)]
    if kind == 'extremo':
        P.append(box((1.4, 9.0, 2.2), (2.0, 11.0, 13.8), mW))
        for z in (1.4, 13.2):
            P += turned_leg(1.4, z, 0.0, 11.0, mL)
        P.append(box((1.8, 2.2, 2.8), (2.4, 2.9, 13.2), mW))                                  # H stretcher
        P.append(box((2.4, 2.2, 7.6), (16.0, 2.9, 8.4), mW))
    else:
        P.append(box((0.0, 2.2, 7.6), (16.0, 2.9, 8.4), mW))
        P.append(plane((0.0, 12.04, 5.6), (16.0, 12.04, 10.4), fin(runner_tone(207), ao=0, dust=0.3), faces=('up',)))
        P += [box((6.6, 12.0, 6.6), (9.4, 12.5, 9.4), fin(lambda c: (PORC, 6), ao=0.3)),       # fruit bowl
              box((6.0, 12.5, 6.0), (10.0, 13.6, 10.0), fin(lambda c: (PORC, 6 if c.face != 'up' else 3), ao=0.3))]
        for n, (dx, dz, col) in enumerate(((-0.8, -0.6, LEMON), (0.9, 0.2, REDP), (-0.2, 1.0, LEMON), (0.4, -1.0, GERAN))):
            P.append(box((8 + dx - 0.9, 13.0, 8 + dz - 0.9), (8 + dx + 0.9, 14.6, 8 + dz + 0.9),
                         fin(lambda c, col=col: (col, 5 + (c.face == 'up') - (c.edge() == 0)), ao=0.4)))
    return P


def leatherette(p=REDP, base=4, seed=0, buttons=False):
    """Cuerina (vinyl) upholstery: smooth with a fine pebble grain, cracked and paler where it is worn."""
    def t(ctx):
        P = tp(ctx)
        k = base + (1 if hh(int(P[0]), int(P[1]), int(P[2]), seed) < 0.12 else 0)
        n = vn(P[0] / 4.0, P[1] / 4.0, P[2] / 4.0, seed + 5)
        if ctx.face == 'up' and n > 0.68:
            k += 1
            if hh(ctx.i, ctx.j, seed) < 0.25:
                return (CROCHET, 3)                                 # cracks showing the fabric backing
        if ctx.edge() == 0:
            k -= 1
        if buttons and ctx.face == 'up' and (ctx.i % 8, ctx.j % 8) == (4, 4):
            k -= 2
        return (p, k)
    return t


def silla_comedor_parts():
    """Dining chair matching the table: lustred frame, turned front legs, bordo cuerina seat, carved back splat.
    The sitter looks north (front = north)."""
    mW = fin(outline(lustre(CAOBA, base=4, seed=211, worn_pal=RAW, wear=0.45)))
    mS = fin(leatherette(REDP, base=4, seed=213))
    P = []
    for x in (3.0, 11.6):
        P += turned_leg(x, 3.0, 0.0, 7.0, mW, w=1.3, rings=(0.3,))
        P.append(box((x, 0.0, 12.0), (x + 1.3, 22.0, 13.3), mW))                             # back legs / stiles
        P.append(box((x + 0.2, 2.4, 4.3), (x + 1.1, 3.0, 12.0), mW))
    P += [box((2.8, 6.0, 2.8), (13.2, 7.0, 13.4), mW),                                        # seat frame
          box((3.0, 7.0, 2.6), (13.0, 8.4, 12.6), mS),                                        # upholstered seat
          box((4.3, 19.4, 12.2), (11.6, 21.6, 13.1), fin(panels(lustre(CAOBA, base=4, seed=215, axis=0), rects=((1, 1, -1, -1),),
                                                                faces=('north', 'south'), bevel=0))),   # top rail
          box((6.6, 9.0, 12.4), (9.4, 19.4, 12.9), fin(panels(lustre(CAOBA, base=4, seed=217, axis=1), rects=((1, 2, -1, -2),),
                                                              faces=('north', 'south'), bevel=1))),     # splat
          box((4.3, 9.0, 12.3), (11.6, 9.8, 13.0), mW)]
    return P


def tip_back(parts, pivot_z=14.0, lift=-4.0):
    """Turn axis-aligned parts 90 deg about the x axis so the piece lies on its back (its back toward +z)."""
    out = []
    for p in parts:
        (x1, y1, z1), (x2, y2, z2) = p.frm, p.to
        ny1, ny2 = pivot_z - z2, pivot_z - z1
        nz1, nz2 = y1 + lift, y2 + lift
        fmap = {'up': 'south', 'south': 'down', 'down': 'north', 'north': 'up', 'west': 'west', 'east': 'east'}
        q = type(p)((x1, ny1, nz1), (x2, ny2, nz2), p.mat, faces=tuple(fmap[f] for f in p.faces), shade=p.shade,
                    name=p.name, cull=p.cull)
        out.append(q)
    return out


def aparador_parts(side):
    """Sideboard 2 blocks wide (viewer's left = '_izq' = +x half): drawers over panelled doors, a back hutch with a
    plate rail of standing decorative plates, a doily, a sugar bowl and (der) a bottle and the house keys."""
    off = (0, 0, 0) if side == 'der' else (16, 0, 0)
    wd = lambda sd, **kw: lustre(CAOBA, seed=221 + sd, off=off, **kw)
    mC = fin(wd(0, base=3, axis=1))
    mDr = fin(panels(wd(1, base=4, axis=0), rects=((1, 1, -1, -1),), faces=('north',), bevel=0))
    mDo = fin(panels(wd(2, base=4, axis=1), wd(3, base=4, axis=1), rects=((2, 2, -2, -2),), faces=('north',)))
    mTop = fin(wd(4, base=4, axis=0, boards=(2, 10), worn_pal=RAW, wear=0.3), dust=1.2)
    mBk = fin(panels(wd(5, base=3, axis=0), rects=((2, 2, -2, -2),), faces=('north',), bevel=1))
    xe = 0.4 if side == 'der' else 0.0
    xf = 16.0 if side == 'der' else 15.6
    P = [box((xe + 0.4, 0.0, 3.4), (xf - 0.4, 1.2, 15.0), mC),
         box((xe + 0.2, 1.2, 3.0), (xf - 0.2, 12.6, 15.6), mC),
         box((xe, 12.6, 2.4), (xf, 13.6, 15.8), mTop)]
    xa, xb = xe + 0.8, xf - 0.8
    xm = (xa + xb) / 2
    P += [box((xa, 9.8, 2.6), (xb, 12.2, 3.0), mDr),
          box((xa, 1.6, 2.6), (xm - 0.1, 9.4, 3.0), mDo), box((xm + 0.1, 1.6, 2.6), (xb, 9.4, 3.0), mDo),
          box((xm - 1.0, 10.7, 2.2), (xm + 1.0, 11.3, 2.6), M_BRASS),
          box((xm - 0.9, 5.0, 2.2), (xm - 0.4, 6.4, 2.6), M_BRASS), box((xm + 0.4, 5.0, 2.2), (xm + 0.9, 6.4, 2.6), M_BRASS)]
    # hutch back with plate rail
    P += [box((xe, 13.6, 14.6), (xf, 27.0, 15.8), mBk),
          box((xe, 27.0, 14.0), (xf, 28.0, 16.0), mTop),
          box((xe, 20.0, 12.6), (xf, 20.6, 14.6), mTop),                                       # shelf
          box((xe, 21.4, 12.6), (xf, 21.8, 12.9), mC)]                                         # plate rail
    mPl = lambda sd: fin(plate_face_tone(sd), ao=0.3, dust=0.5)
    for n, x in enumerate((2.8, 9.0) if side == 'der' else (1.4, 7.6)):
        P.append(box((x, 20.6, 13.0), (x + 5.2, 25.8, 13.5), mPl(n + (0 if side == 'der' else 2)), rot=('x', 22.5, (x, 20.6, 13.0))))
    P.append(plane((xe + 0.6, 13.64, 4.0), (xf - 0.6, 13.64, 12.0), fin(runner_tone(229 + (side == 'izq')), ao=0, dust=0.5),
                   faces=('up',)))
    if side == 'izq':
        mSu = fin(lambda c: (PORC, 6 - (c.edge() == 0)) if c.j > 1 or c.face == 'up' else (CELESTE, 3), ao=0.4)
        P += [box((9.0, 13.6, 7.0), (12.0, 16.0, 10.0), mSu), box((9.6, 16.0, 7.6), (11.4, 16.6, 9.4), mSu),
              box((10.2, 16.6, 8.2), (10.8, 17.2, 8.8), mSu)]                                   # sugar bowl
    else:
        mBo = fin(lambda c: (BLACKP, 3 + (c.i == 1)) if c.j > 2 else (BLACKP, 2), ao=0.3)
        mLb = fin(lambda c: (CROCHET, 6) if c.face in ('north', 'west', 'east', 'south') and 2 < c.j < 7 else (BLACKP, 3), ao=0.3)
        P += [box((3.0, 13.6, 7.6), (5.0, 20.0, 9.6), mLb), box((3.5, 20.0, 8.1), (4.5, 22.6, 9.1), mBo),
              box((3.4, 22.6, 8.0), (4.6, 23.2, 9.2), fin(flat(GOLD, 5), ao=0))]                # bottle
        P += [box((9.0, 13.6, 5.0), (11.6, 13.9, 6.0), fin(brass(BRASS, base=5, seed=231), ao=0)),   # keys on a ring
              box((10.4, 13.6, 5.8), (11.0, 13.9, 7.8), fin(brass(NICKEL, base=5, seed=232), ao=0))]
    return P


def plate_face_tone(seed=0, faces=('north', 'south')):
    """Decorative plate seen from the front (cutout disc): white porcelain, blue rim band, a painted flower."""
    def t(ctx):
        if ctx.face not in faces:
            return (PORC, 5)
        w, h = ctx.w, ctx.h
        x, y = (ctx.i + 0.5) / w * 2 - 1, (ctx.j + 0.5) / h * 2 - 1
        r = math.hypot(x, y)
        if r > 1.0:
            return None
        if ctx.face == faces[1]:
            return (PORC, 4)
        if r > 0.86:
            return (PORC, 5)
        if r > 0.7:
            return (CELESTE, 2 + (int((math.atan2(y, x) + 4) * 6) % 2)) if seed % 2 else (GOLD, 5)
        if r < 0.32:
            a = (math.atan2(y, x) / (2 * math.pi) * 5) % 1.0
            return (ROSE, 5) if a < 0.6 else (LEAF, 4)
        return (PORC, 7 if hh(ctx.i, ctx.j, seed) > 0.05 else 5)
    return t


def lampara_comedor_parts(lit):
    """70s brass three-arm ceiling lamp with frosted amber tulips (hangs from the ceiling above the table)."""
    mB = fin(brass(seed=241, base=4, tarnish=0.5), dust=0.6)

    def tulip(lit_):
        def t(ctx):
            if ctx.face == 'down':
                return (OPAL_LIT, 6) if lit_ else (OPAL, 4)
            k = 3 + int((1 - ctx.t) * 3) + (ctx.i % 3 == 1)
            return (OPAL_LIT, k + 1) if lit_ else (OPAL, k - 1 if ctx.j > ctx.h - 2 else k)
        return t
    mT = fin(tulip(lit), ao=0, dust=0 if lit else 0.5)
    P = [box((7.2, 3.4, 7.2), (8.8, 9.6, 8.8), mB), box((6.4, 3.0, 6.4), (9.6, 4.2, 9.6), mB),
         box((7.4, 9.6, 7.4), (8.6, 15.0, 8.6), mB), box((6.0, 15.0, 6.0), (10.0, 16.0, 10.0), mB)]   # stem + canopy
    for (dx, dz) in ((5.2, 0.0), (-2.6, 4.5), (-2.6, -4.5)):
        x, z = 8 + dx, 8 + dz
        P += [box((min(8, x) - 0.3 if dx < 0 else 8.0, 4.0, z - 0.3) if dz == 0 else (min(8.0, x), 4.0, min(8.0, z)),
                  (max(8.0, x) + 0.3, 4.6, z + 0.3) if dz == 0 else (max(8.0, x), 4.6, max(8.0, z)), mB),
              box((x - 0.4, 4.6, z - 0.4), (x + 0.4, 6.0, z + 0.4), mB),
              box((x - 1.6, 1.2, z - 1.6), (x + 1.6, 4.0, z + 1.6), mT, shade=not lit),          # tulip (opening down)
              box((x - 1.2, 0.4, z - 1.2), (x + 1.2, 1.2, z + 1.2), mT, shade=not lit),
              box((x - 1.0, 4.0, z - 1.0), (x + 1.0, 4.6, z + 1.0), mB)]
    return P


# ============================================================================================ KITCHEN
def cream_door(seed=0, knob=True):
    """Painted kitchen cabinet door: cream enamel paint, a routed rectangle, grime around the handle, chips."""
    base = smooth(ENAMEL, base=6, seed=seed, grime=0.3, edge=0, mottle=0.12)

    def t(ctx):
        P = tp(ctx)
        if ctx.edge() == 0 and vn(P[0] / 1.5, P[1] / 1.5, P[2] / 1.5, seed + 3) > 0.72:
            return (PINO, 4)                                        # chipped paint on the edges
        pl, k = base(ctx)
        if ctx.face == 'north' and 0.1 < ctx.t < 0.5 and hh(ctx.i // 2, ctx.j // 2, seed) < 0.06:
            k -= 1                                                  # finger marks near the handle
        return (pl, k)
    return panels(t, rects=((2, 2, -2, -2),), faces=('north',), bevel=1, groove=True)


def granite_tone(seed=0):
    """Polished 'granito gris mara' counter top: black/grey/white speckle, slight sheen band."""
    def t(ctx):
        P = tp(ctx)
        hv = hh(int(P[0]), int(P[1]), int(P[2]), seed)
        k = 5 + (1 if vn(P[0] / 5.0, P[1] / 5.0, P[2] / 5.0, seed) > 0.6 else 0)
        if hv < 0.10:
            k = 2
        elif hv < 0.2:
            k = 3
        elif hv > 0.94:
            k = 7
        if ctx.face == 'up' and 0.45 < (ctx.s * 0.6 + ctx.t * 0.4) < 0.5:
            k += 1
        return (GRANITO, k)
    return t


def mesada_parts(kind='lisa'):
    """Kitchen counter (top at 14/16): cream painted base cabinet, granite top with a front lip, a strip of green 70s
    tiles on the back. kind: 'lisa' (two doors) | 'cajones' (three drawers) | 'pileta' (stainless sink, tap, sponge,
    detergent, dish cloth) | 'esquina' (corner, fronts on north and east)."""
    mBody = fin(painted(ENAMEL, base=5, seed=301, grime=0.4))
    mPl = fin(flat(BAKE, 2), ao=0.4)
    mTop = fin(granite_tone(303), dust=0.4)
    mTile = fin(tiles(TILE_G, base=5, size=8, seed=305), dust=0.3)
    P = [box((0.0, 1.2, 1.6), (16.0, 13.2, 16.0), mBody, faces=('north', 'south', 'west', 'east', 'down') if kind == 'pileta'
             else None),
         box((0.0, 0.0, 2.6), (16.0, 1.2, 16.0), mPl)]                                      # recessed plinth
    if kind == 'esquina':
        P[0] = box((0.0, 1.2, 1.6), (14.4, 13.2, 16.0), mBody)
        P[1] = box((0.0, 0.0, 2.6), (13.4, 1.2, 16.0), mPl)
    if kind == 'pileta':
        P += [box((0.0, 13.2, 1.0), (2.2, 14.2, 15.4), mTop), box((13.8, 13.2, 1.0), (16.0, 14.2, 15.4), mTop),
              box((2.2, 13.2, 1.0), (13.8, 14.2, 2.4), mTop), box((2.2, 13.2, 12.6), (13.8, 14.2, 15.4), mTop)]
        mSt = fin(brass(STEEL, base=5, seed=307, sheen=False, tarnish=0.1), dust=0)
        P += [box((2.2, 8.6, 2.4), (13.8, 13.2, 2.8), mSt), box((2.2, 8.6, 12.2), (13.8, 13.2, 12.6), mSt),
              box((2.2, 8.6, 2.8), (2.6, 13.2, 12.2), mSt), box((13.4, 8.6, 2.8), (13.8, 13.2, 12.2), mSt),
              box((2.6, 8.6, 2.8), (13.4, 9.0, 12.2), fin(lambda c: (STEEL, 2) if (abs(c.s - 0.5) < 0.08 and abs(c.t - 0.5) < 0.1)
                                                          else (STEEL, 4 + (hh(c.i, c.j) > 0.85)), ao=0.8, dust=0))]   # basin
        mCh = fin(brass(NICKEL, base=6, seed=309, tarnish=0.25), dust=0)
        P += [box((7.4, 14.2, 13.2), (8.6, 17.2, 14.4), mCh), box((7.6, 16.4, 9.6), (8.4, 17.2, 13.2), mCh),
              box((7.5, 15.4, 9.4), (8.5, 16.6, 10.2), mCh)]                                  # tap
        for x in (5.2, 10.0):
            P += [box((x, 14.2, 13.4), (x + 0.8, 15.2, 14.2), mCh), box((x - 0.6, 15.2, 13.6), (x + 1.4, 15.6, 14.0), mCh),
                  box((x + 0.2, 15.2, 13.0), (x + 0.6, 15.6, 14.6), mCh)]
        P += [box((2.6, 14.2, 13.0), (4.4, 18.6, 14.6), fin(lambda c: (YELLOWP, 5 + (c.i == 1)) if c.j > 3 else (GREENP, 5), ao=0.4)),
              box((3.1, 18.6, 13.5), (3.9, 19.4, 14.1), fin(flat(GREENP, 6), ao=0)),          # detergent bottle
              box((11.4, 14.2, 13.2), (13.4, 15.2, 14.6), fin(lambda c: (GREENP, 5) if c.j < 2 else (YELLOWP, 6), ao=0.4))]   # sponge
        # rejilla (dish cloth) over the cabinet door
        P.append(box((6.0, 6.4, 1.2), (10.0, 12.8, 1.6), fin(cloth(LINEN, base=5, seed=311, folds=0.4, stains=0.5,
                                                                    stain_col=hx('#7a6a40')), ao=0.4)))
        P.append(box((6.0, 12.8, 1.2), (10.0, 13.2, 3.0), fin(cloth(LINEN, base=5, seed=312, folds=0.2, stains=0.4), ao=0.4)))
    else:
        P += [box((0.0, 13.2, 1.0), (16.0, 14.2, 16.0), mTop)]
    P.append(box((0.0, 14.2, 15.4), (16.0, 17.4, 16.0), mTile, faces=('north', 'up', 'west', 'east')))  # tile upstand
    if kind in ('lisa', 'pileta'):
        P += [box((0.6, 1.6, 1.2), (7.9, 12.8, 1.6), fin(cream_door(313))), box((8.1, 1.6, 1.2), (15.4, 12.8, 1.6), fin(cream_door(314)))]
        P += [box((6.6, 9.6, 0.6), (7.2, 11.6, 1.2), M_CHROME), box((8.8, 9.6, 0.6), (9.4, 11.6, 1.2), M_CHROME)]
    elif kind == 'cajones':
        for n, (a, b) in enumerate(((1.6, 5.2), (5.4, 9.0), (9.2, 12.8))):
            P += [box((0.6, a, 1.2), (15.4, b, 1.6), fin(cream_door(315 + n))),
                  box((6.4, (a + b) / 2 - 0.3, 0.6), (9.6, (a + b) / 2 + 0.3, 1.2), M_CHROME)]
    elif kind == 'esquina':
        P += [box((0.6, 1.6, 1.2), (13.8, 12.8, 1.6), fin(cream_door(318))),
              box((11.4, 9.6, 0.6), (12.0, 11.6, 1.2), M_CHROME),
              box((14.4, 1.6, 1.6), (14.8, 12.8, 16.0), fin(lambda c: (ENAMEL, 5), ao=0.5), faces=('east',))]
        P[-1] = box((14.4, 1.2, 1.6), (14.8, 13.2, 16.0), mBody)
    return P


def stove_top_tone(ctx):
    """Enamel hob: four burners (black grate rings + caps), drip stains and burnt rings around them."""
    if ctx.face != 'up':
        return (ENAMEL, 5)
    x, z = ctx.pos[0], ctx.pos[2]
    for (cx, cz, r) in ((4.5, 5.0, 2.6), (11.5, 5.0, 2.2), (4.5, 11.0, 2.2), (11.5, 11.0, 2.6)):
        d = math.hypot(x - cx, z - cz)
        if d < r * 0.45:
            return (BAKE, 2)
        if d < r:
            return (BAKE, 4)
        if d < r + 0.9 and hh(ctx.i, ctx.j, 3) < 0.6:
            return (ENAMEL, 2)                                      # scorched halo
    if hh(ctx.i // 2, ctx.j // 2, 5) < 0.04:
        return (CARTON, 4)                                          # old drips
    return (ENAMEL, 6)


def oven_door_tone(ctx):
    if ctx.face != 'north':
        return (ENAMEL, 5)
    i, j, w, h = ctx.i, ctx.j, ctx.w, ctx.h
    if 4 <= i < w - 4 and 5 <= j < h - 4:
        if i in (4, w - 5) or j in (5, h - 5):
            return (NICKEL, 4)
        return (BAKE, 2 if (i + j) % 7 else 4)                       # dark oven window
    if j < 3:
        return (ENAMEL, 6)
    return (ENAMEL, 6 if hh(i, j, 7) > 0.04 else 4)


def cocina_gas_parts(pava=False):
    mE = fin(smooth(ENAMEL, base=6, seed=321, grime=0.3), dust=0.4)
    mTop = fin(stove_top_tone, ao=0.3, dust=0.3)
    mDoor = fin(oven_door_tone, ao=0.4)
    mG = fin(iron(seed=323, rust=0.15), dust=0)
    P = [box((0.6, 1.2, 1.8), (15.4, 13.0, 15.2), mE),
         box((1.0, 0.0, 2.4), (2.4, 1.2, 3.8), M_CHROME), box((13.6, 0.0, 2.4), (15.0, 1.2, 3.8), M_CHROME),
         box((1.0, 0.0, 13.0), (2.4, 1.2, 14.4), M_CHROME), box((13.6, 0.0, 13.0), (15.0, 1.2, 14.4), M_CHROME),
         box((0.6, 13.0, 1.6), (15.4, 13.6, 15.2), mTop),
         box((0.6, 13.6, 14.4), (15.4, 18.0, 15.4), mE),                                          # back guard
         box((1.4, 2.2, 1.4), (14.6, 9.4, 1.8), mDoor),
         box((3.0, 8.4, 0.6), (13.0, 9.0, 1.4), M_CHROME), box((3.0, 8.4, 1.0), (3.6, 9.0, 1.4), M_CHROME),
         box((0.6, 9.8, 1.4), (15.4, 12.6, 1.8), fin(lambda c: (NICKEL, 5 if c.j else 6), ao=0.3))]   # control strip
    for n, x in enumerate((2.4, 5.0, 7.6, 10.2, 12.8)):
        P += [box((x - 0.7, 10.4, 0.8), (x + 0.7, 11.8, 1.4), fin(smooth(BAKE, base=4, seed=325 + n), ao=0)),
              box((x - 0.15, 11.2, 0.6), (x + 0.15, 11.8, 0.8), fin(flat(ENAMEL, 7), ao=0))]
    for (cx, cz, r) in ((4.5, 5.0, 2.6), (11.5, 5.0, 2.2), (4.5, 11.0, 2.2), (11.5, 11.0, 2.6)):   # grates
        P += [box((cx - r, 13.6, cz - 0.25), (cx + r, 14.2, cz + 0.25), mG), box((cx - 0.25, 13.6, cz - r), (cx + 0.25, 14.2, cz + r), mG)]
    if pava:
        P += flame_parts(4.5, 11.0 - 1.0, 13.7, h=0.9, w=1.2, p=FLAME_B) + flame_parts(4.5, 12.0, 13.7, h=0.9, w=1.2, p=FLAME_B)
        P += shift(pava_parts(), dx=-3.5, dy=16.2 - 2.0, dz=3.0)
    return P


def pava_parts():
    """Aluminium kettle (pava) with a black bakelite handle, dented and blackened at the bottom ('sobre mesada')."""
    y = -2.0
    mA = fin(brass(ALU, base=4, seed=331, tarnish=0.4), dust=0.3)
    mS = fin(lambda c: (BAKE, 3) if c.j > c.h - 3 else brass(ALU, base=4, seed=332, tarnish=0.4)(c), dust=0.2)
    mH = fin(smooth(BLACKP, base=3, seed=333))
    return [box((5.0, y, 5.0), (11.0, y + 3.6, 11.0), mS), box((5.6, y + 3.6, 5.6), (10.4, y + 4.4, 10.4), mA),
            box((6.8, y + 4.4, 6.8), (9.2, y + 4.8, 9.2), mA), box((7.6, y + 4.8, 7.6), (8.4, y + 5.4, 8.4), mH),
            box((10.8, y + 1.0, 7.4), (12.4, y + 2.0, 8.6), mA, rot=('z', 45, (10.8, y + 1.0, 8.0))),     # spout
            box((7.6, y + 4.4, 5.6), (8.4, y + 7.4, 6.4), mH), box((7.6, y + 4.4, 9.6), (8.4, y + 7.4, 10.4), mH),
            box((7.6, y + 7.4, 5.6), (8.4, y + 8.2, 10.4), mH)]


def heladera_tone(ctx, yoff=0.0):
    """Rounded 60s fridge: cream enamel, rust blooming at the bottom edge of the cabinet."""
    P = tp(ctx, (0, yoff, 0))
    k = 6
    n = vn(P[0] / 6.0, P[1] / 6.0, P[2] / 6.0, 341)
    if n > 0.7:
        k -= 1
    if ctx.face != 'up' and P[1] < 4 and vn(P[0] / 2.0, P[1] / 2.0, P[2] / 2.0, 342) > 0.6 - (4 - P[1]) * 0.08:
        return (RUST, 3 + (hh(*P) > 0.6))
    if ctx.edge() == 0 and ctx.w > 3 and ctx.h > 3:
        k -= 1
    return (ENAMEL, k)


def fridge_drawing_canvas():
    """Lucia's crayon drawing held by magnets: the family holding hands, the dog, and a tall black figure."""
    cv = Canvas(14, 12, hx('#f4f2ea'))
    crayon = {'r': hx('#d02a2a'), 'b': hx('#2a4ad0'), 'y': hx('#e8c020'), 'g': hx('#30a040'), 'k': hx('#141414'),
              'p': hx('#e070b0'), 'n': hx('#8a4a24')}
    cv.ascii(0, 0, ['y.............', '.y............', '..............', '..r..b..p.k...', '.rrr.b..p.kk..',
                    '..r.bbb.p.k...', '.r.r.b.ppp.k..', '.r.r.b.p.p.k..', '.............', 'nnnn......k...',
                    'n..n......kk..', 'gggggggggggggg'], crayon)
    cv.ascii(9, 0, ['..k..', '.kkk.', 'k.k.k'], crayon)
    return cv


def heladera_parts(half):
    """Old rounded fridge, 2 blocks tall ('abajo' / 'arriba'): cream enamel, chrome lever handle and script plate
    'AURORA', kick grille, Lucia's drawing and a pizzeria magnet on the door."""
    yo = 0.0 if half == 'abajo' else 16.0
    mB = fin(lambda c: heladera_tone(c, yo), dust=0.6)
    mD = mB
    P = []
    if half == 'abajo':
        P += [box((1.0, 0.0, 2.0), (15.0, 2.0, 15.4), fin(lambda c: (BAKE, 2) if (c.face == 'north' and c.j % 2 == 0 and 1 < c.i < c.w - 2)
                                                          else (NICKEL, 4), ao=0.4)),
              box((1.0, 2.0, 2.0), (15.0, 16.0, 15.4), mB),
              box((1.4, 2.4, 1.4), (14.6, 16.0, 2.0), mD),
              box((1.0, 2.0, 1.6), (15.0, 2.4, 2.0), fin(flat(GRAPH, 3), ao=0))]
        cv = fridge_drawing_canvas()
        P += [box((4.0, 8.0, 1.3), (11.0, 14.0, 1.4), fin(canvas_tone(cv), ao=0, dust=0), faces=('north',)),
              box((4.4, 13.4, 1.0), (5.6, 14.4, 1.3), fin(flat(REDP, 5), ao=0)),
              box((9.4, 13.4, 1.0), (10.6, 14.4, 1.3), fin(flat(CELESTE, 4), ao=0)),
              box((10.6, 4.6, 1.0), (13.0, 6.4, 1.3), fin(lambda c: (YELLOWP, 6) if c.j < 2 else (REDP, 4), ao=0))]   # pizza magnet
    else:
        P += [box((1.0, 0.0, 2.0), (15.0, 8.6, 15.4), mB),
              box((1.6, 8.6, 2.6), (14.4, 9.6, 15.0), mB),                                       # rounded top
              box((2.6, 9.6, 3.6), (13.4, 10.0, 14.0), mB),
              box((1.4, 0.0, 1.4), (14.6, 8.2, 2.0), mD),
              box((2.0, 8.2, 1.8), (14.0, 8.8, 2.4), mD)]
        mCh = fin(brass(NICKEL, base=6, seed=345, tarnish=0.3), dust=0.3)
        P += [box((12.0, 0.0, 0.6), (13.2, 5.2, 1.4), mCh), box((12.2, 4.4, 1.0), (13.0, 5.0, 1.4), mCh),
              box((12.2, 0.0, 1.0), (13.0, 0.6, 1.4), mCh)]                                      # lever handle
        def plate(c):
            if c.face != 'north':
                return (NICKEL, 5)
            pts = set(draw_text(F35, 'AURORA', 1, 1, sp=1))
            return (BAKE, 3) if (c.i, c.j) in pts else (NICKEL, 6 if c.edge() else 4)
        P.append(box((4.6, 4.6, 1.2), (11.4, 6.2, 1.4), fin(plate, ao=0, dust=0.2)))
        P.append(box((3.0, 10.0, 6.0), (9.0, 10.6, 11.0), fin(lambda c: (CARTON, 5) if c.face == 'up' else (CARTON, 3), ao=0.5)))  # box on top
    return P


def alacena_parts(kind):
    """Wall cupboard, cream painted. Place it TWO blocks above the floor (over the counter's prop block): the model
    hangs 8/16 below its block so it spans 1.5 m .. 2.5 m. kind: 'cerrada' (two doors) | 'abierta' (doors swung
    open: plates, cups and the yerba/azucar/cafe canisters inside) | 'cuerpo' (no doors, for the trapdoor door)."""
    mBody = fin(painted(ENAMEL, base=5, seed=351, grime=0.0))
    mIn = fin(painted(ENAMEL, base=3, seed=352, grime=0.0), dust=0.8)
    P = [box((0.4, 1.0, 10.6), (15.6, 1.8, 16.0), mBody), box((0.4, 14.6, 10.6), (15.6, 15.4, 16.0), mBody),
         box((0.4, 1.8, 10.6), (1.2, 14.6, 16.0), mBody), box((14.8, 1.8, 10.6), (15.6, 14.6, 16.0), mBody),
         box((1.2, 1.8, 15.4), (14.8, 14.6, 16.0), mIn), box((1.2, 7.8, 10.8), (14.8, 8.4, 15.4), mIn)]
    if kind == 'cerrada':
        P += [box((0.6, 1.2, 10.2), (7.9, 15.2, 10.6), fin(cream_door(353))),
              box((8.1, 1.2, 10.2), (15.4, 15.2, 10.6), fin(cream_door(354))),
              box((6.8, 2.2, 9.6), (7.4, 4.2, 10.2), M_CHROME), box((8.6, 2.2, 9.6), (9.2, 4.2, 10.2), M_CHROME)]
        return shift(P, dy=-8.0)
    if kind == 'abierta':
        P += [box((0.6, 1.2, 2.8), (1.0, 15.2, 10.2), fin(cream_door(355))),
              box((15.0, 1.2, 2.8), (15.4, 15.2, 10.2), fin(cream_door(356))),
              box((1.0, 2.2, 3.2), (1.6, 4.2, 3.8), M_CHROME), box((14.4, 2.2, 3.2), (15.0, 4.2, 3.8), M_CHROME)]
    # contents: plates stacked, cups, the yerbera set
    mPl = fin(lambda c: (PORC, 6 - (c.j % 2)) if c.face != 'up' else (PORC, 7), ao=0.6, dust=0.5)
    P += [box((2.0, 1.8, 11.4), (6.6, 4.6, 15.2), mPl)]
    for n, x in enumerate((8.0, 10.4, 12.8)):
        col = (REDP, CELESTE, YELLOWP)[n]
        P += [box((x - 0.9, 1.8, 12.2), (x + 0.9, 3.8, 14.0), fin(lambda c, col=col: (col, 5 if c.face != 'up' else 2), ao=0.5)),
              box((x + 0.9, 2.4, 12.8), (x + 1.3, 3.4, 13.4), fin(flat(col, 4), ao=0))]
    for n, (x, word, col) in enumerate(((2.0, 'YERBA', REDP), (6.4, 'AZUCAR', REDP), (10.8, 'CAFE', REDP))):
        def lab(c, word=word, col=col):
            if c.face == 'north':
                pts = set(draw_text(F35, word[:3], 1, 2))
                return (col, 3) if (c.i, c.j) in pts else (ENAMEL, 6)
            return (ENAMEL, 5 if c.face != 'up' else 3)
        P.append(box((x, 8.4, 11.6), (x + 3.4, 13.0, 14.6), fin(lab, ao=0.5, dust=0.6)))
    return shift(P, dy=-8.0)


def alacena_puerta_tone(ctx):
    """32x32 trapdoor face: cream painted cupboard door with a routed panel and a chrome knob."""
    i, j = ctx.i, ctx.j
    if i in (0, 31) or j in (0, 31):
        return (ENAMEL, 3)
    if 13 <= i <= 18 and 25 <= j <= 27:
        return (NICKEL, 6 if j == 25 else 4)
    if (i in (4, 27) and 4 <= j <= 27) or (j in (4, 27) and 4 <= i <= 27):
        return (ENAMEL, 4)
    if (i == 5 and 5 <= j <= 26) or (j == 5 and 5 <= i <= 26):
        return (ENAMEL, 7)
    k = 6 - (1 if hh(i // 2, j // 2, 411) < 0.05 else 0)
    if 20 <= j and 10 <= i <= 21 and hh(i, j, 412) < 0.12:
        k -= 1
    return (ENAMEL, k)


def panera_parts():
    """Tin bread box with a roll-top ('sobre mesada'): cream enamel, red PAN lettering, half a baguette poking out."""
    y = -2.0
    def front(c):
        if c.face == 'north':
            pts = set((x, yy) for (x, yy) in draw_text(F57, 'PAN', 3, 2, sp=1))
            return (REDP, 4) if (c.i, c.j) in pts else (ENAMEL, 6 - (c.edge() == 0))
        return (ENAMEL, 5)
    mB = fin(front, dust=0.6)
    mR = fin(lambda c: (ENAMEL, 5 + (c.j % 2)), dust=0.6)
    mBread = fin(lambda c: (CARTON, 6 if c.face == 'up' else 5) if hh(c.i, c.j) > 0.15 else (CARTON, 7), ao=0.4)
    return [box((2.4, y, 4.0), (13.6, y + 5.6, 12.8), mB),
            box((2.6, y + 5.6, 5.0), (13.4, y + 6.6, 12.8), mR),
            box((2.6, y + 6.6, 7.0), (13.4, y + 7.2, 12.4), mR),
            box((5.4, y + 4.0, 3.0), (6.4, y + 4.6, 4.0), M_CHROME), box((9.6, y + 4.0, 3.0), (10.6, y + 4.6, 4.0), M_CHROME),
            box((13.6, y + 1.2, 6.0), (16.4, y + 3.0, 7.8), mBread)]


def mate_parts(y=-2.0):
    """Mate (calabaza with an alpaca rim and the bombilla), red thermos with chrome cup, yerba package."""
    mG = fin(painted(pal('#2a1a0e', '#3e2814', '#56381c', '#6e4a26', '#8a5e32'), base=2, seed=361, wear=0.3), dust=0.4)
    mN = fin(brass(NICKEL, base=5, seed=363), dust=0.3)
    mY = fin(lambda c: (pal('#2e3a14', '#46561e', '#5e7028', '#7a8a38'), 1 + (hh(c.i, c.j) > 0.5)), ao=0, dust=0)
    mT = fin(painted(pal('#3a0a0a', '#5a1010', '#7a1a16', '#9a2a20', '#b84030'), base=3, seed=365, wear=0.3), dust=0.5)
    P = [box((3.2, y, 6.2), (6.8, y + 2.6, 9.8), mG),
         box((2.8, y + 0.6, 6.6), (7.2, y + 2.2, 9.4), mG), box((3.6, y + 0.6, 5.8), (6.4, y + 2.2, 10.2), mG),
         box((3.5, y + 2.6, 6.5), (6.5, y + 3.2, 9.5), mN),
         box((3.9, y + 3.0, 6.9), (6.1, y + 3.1, 9.1), mY, faces=('up',)),
         box((5.0, y + 2.6, 7.8), (5.4, y + 6.4, 8.2), mN, rot=('z', -22.5, (5.2, y + 2.6, 8.0))),
         box((9.2, y, 7.4), (12.0, y + 6.6, 10.2), mT),
         box((9.0, y + 6.6, 7.2), (12.2, y + 8.6, 10.4), mN),
         box((9.4, y + 8.6, 7.6), (11.8, y + 9.0, 10.0), mN),
         box((12.0, y + 2.0, 8.4), (12.6, y + 5.0, 9.2), mT),
         box((9.2, y + 3.0, 7.3), (12.0, y + 3.4, 7.4), mN, faces=('north',)),
         box((7.4, y, 11.2), (10.6, y + 4.2, 13.2), fin(lambda c: (PAPER, 6) if c.j < 3 or c.face == 'up' else
                                                       ((GREENP, 6) if (c.i + c.j) % 7 else (YELLOWP, 5)), dust=0.6))]
    return P


def escurridor_parts():
    """Chrome-wire dish rack ('sobre mesada') with plates, two glasses and a cup."""
    y = -2.0
    mW = fin(brass(NICKEL, base=5, seed=371, tarnish=0.4), dust=0)
    P = [box((1.6, y, 3.6), (14.4, y + 0.4, 12.4), fin(lambda c: (NICKEL, 4) if (c.i % 3 == 0 or c.face != 'up') else None, ao=0))]
    for x in (1.6, 14.0):
        P.append(box((x, y + 0.4, 3.6), (x + 0.4, y + 3.0, 12.4), fin(lambda c: (NICKEL, 5) if c.j % 3 == 0 or c.i % 4 == 0 else None, ao=0)))
    for n in range(5):
        x = 3.0 + n * 1.4
        P.append(box((x, y + 0.4, 4.4), (x + 0.3, y + 6.4, 11.6), fin(plate_face_tone(n, ('west', 'east')), ao=0.2),
                     rot=('z', -22.5, (x, y + 0.4, 8.0)), faces=('west', 'east')))
    mGl = fin(lambda c: (GLASS_J, 6 if c.i == 1 else 5), ao=0)
    P += [box((10.4, y + 0.4, 4.6), (12.0, y + 3.4, 6.2), mGl), box((10.4, y + 0.4, 9.0), (12.0, y + 3.0, 10.6), mGl),
          box((10.2, y + 0.4, 6.8), (12.4, y + 2.4, 8.6), fin(lambda c: (CELESTE, 5) if c.face != 'up' else (CELESTE, 1), ao=0.3))]
    return P


def clock_face(hour, minute, red=True):
    def t(ctx):
        w, h = ctx.w, ctx.h
        x, y = (ctx.i + 0.5) / w * 2 - 1, (ctx.j + 0.5) / h * 2 - 1
        r = math.hypot(x, y)
        if ctx.face != 'north':
            return (REDP, 4) if red else (NICKEL, 4)
        if r > 1.0:
            return None
        if r > 0.84:
            return (REDP, 4 + (y < 0)) if red else (NICKEL, 5)
        a = math.atan2(x, -y)                                   # 0 at 12, clockwise
        ah = (hour % 12 + minute / 60.0) / 12.0 * 2 * math.pi
        am = minute / 60.0 * 2 * math.pi
        def on_hand(ang, ln, wd):
            hx_, hy_ = math.sin(ang), -math.cos(ang)
            proj = x * hx_ + y * hy_
            perp = abs(x * hy_ - y * hx_)
            return -0.08 < proj < ln and perp < wd
        if on_hand(am, 0.74, 0.07):
            return T(BAKE, 1)
        if on_hand(ah, 0.48, 0.1):
            return T(BAKE, 1)
        if r < 0.1:
            return T(REDP, 4)
        tick = (a / (2 * math.pi) * 12) % 1.0
        if r > 0.68 and (tick < 0.09 or tick > 0.91):
            return T(BAKE, 2)
        return T(CROCHET, 7)
    return t


def reloj_parts(hour, minute):
    m = fin(clock_face(hour, minute), ao=0, dust=0.2)
    return [box((3.0, 4.0, 14.6), (13.0, 14.0, 15.6), m),
            box((7.6, 13.6, 15.6), (8.4, 14.6, 16.0), M_IRON)]


def tubo_parts(lit):
    """Kitchen fluorescent fixture on the ceiling: white steel tray, one tube, yellowed end caps, dead flies."""
    mT = fin(smooth(PLAST_W, base=6, seed=381, grime=0.0), dust=0.4)
    mTube = fin(lambda c: (OPAL_LIT, 7) if lit else ((OPAL, 4) if (c.i > 3 and c.i < c.w - 4) else (OPAL, 2)), ao=0, dust=0 if lit else 0.3)
    return [box((0.6, 14.4, 6.4), (15.4, 16.0, 9.6), mT),
            box((1.0, 13.4, 7.2), (15.0, 14.4, 8.8), mTube, shade=not lit),
            box((0.6, 13.2, 6.8), (1.6, 14.4, 9.2), fin(flat(PLAST_W, 3), ao=0)),
            box((14.4, 13.2, 6.8), (15.4, 14.4, 9.2), fin(flat(PLAST_W, 3), ao=0))]


def hule_tone(seed=0):
    """Oilcloth (hule) on the kitchen table: red-and-white gingham with little cherries, shiny, a burn mark."""
    def t(ctx):
        u, v = uv2(ctx)
        if ctx.face in ('up', 'down'):
            x, y, z = tp(ctx)
            u, v = x, z
        a = int(math.floor(u / 3.0)) % 2
        b = int(math.floor(v / 3.0)) % 2
        if a and b:
            c = (REDP, 5)
        elif a or b:
            c = (REDP, 7)
        else:
            c = (CROCHET, 7)
        if ctx.face == 'up' and math.hypot(u - 20, v - 12) < 1.6:
            return (BAKE, 3)                                     # cigarette burn
        return c
    return t


def mesa_cocina_parts():
    """Kitchen table: oilcloth (red gingham) over a formica top, chrome tube legs."""
    mH = fin(hule_tone(391), dust=0.2)
    mCh = fin(brass(NICKEL, base=5, seed=393, tarnish=0.3), dust=0.3)
    P = [box((0.6, 11.2, 0.6), (15.4, 12.0, 15.4), mH),
         box((0.4, 9.6, 0.4), (15.6, 11.2, 0.8), mH), box((0.4, 9.6, 15.2), (15.6, 11.2, 15.6), mH),
         box((0.4, 9.6, 0.8), (0.8, 11.2, 15.2), mH), box((15.2, 9.6, 0.8), (15.6, 11.2, 15.2), mH)]
    for (x, z) in ((2.0, 2.0), (13.0, 2.0), (2.0, 13.0), (13.0, 13.0)):
        P += [box((x, 0.6, z), (x + 1.0, 11.2, z + 1.0), mCh), box((x - 0.2, 0.0, z - 0.2), (x + 1.2, 0.6, z + 1.2), fin(flat(BLACKP, 3)))]
    return P


def silla_cocina_parts():
    """Chrome tube kitchen chair with a red vinyl seat and backrest (sitter looks north)."""
    mCh = fin(brass(NICKEL, base=5, seed=395, tarnish=0.3), dust=0.3)
    mV = fin(leatherette(REDP, base=5, seed=397))
    P = []
    for x in (3.2, 12.0):
        P += [box((x, 0.0, 3.2), (x + 0.8, 7.0, 4.0), mCh), box((x, 0.0, 12.0), (x + 0.8, 18.0, 12.8), mCh),
              box((x, 0.0, 4.0), (x + 0.8, 0.6, 12.0), mCh)]
    P += [box((2.8, 7.0, 2.8), (13.2, 8.6, 13.0), mV), box((3.4, 12.0, 12.6), (12.6, 17.2, 13.6), mV),
          box((4.0, 6.4, 3.4), (12.0, 7.0, 4.0), mCh)]
    return P


def desayuno_parts():
    """Breakfast ('sobre mesa'): plate of medialunas, two cups of cafe con leche, sugar bowl and a spoon."""
    y = -4.0
    mPl = fin(lambda c: (PORC, 7 if c.face == 'up' else 5), ao=0.3, dust=0)
    mM = fin(lambda c: (CARTON, 7 if (c.i + c.j) % 3 else 6) if c.face == 'up' else (CARTON, 5), ao=0.4, dust=0)
    P = [box((2.0, y, 2.4), (9.0, y + 0.4, 9.4), mPl)]
    for (x, z, rot) in ((2.8, 3.4, 22.5), (4.6, 6.0, -22.5), (5.4, 3.0, 0)):
        P += [box((x, y + 0.4, z), (x + 3.4, y + 1.6, z + 1.4), mM, rot=('y', rot, (x + 1.7, y, z + 0.7)) if rot else None)]
    for (x, z) in ((10.4, 3.0), (10.0, 10.0)):
        P += [box((x - 1.4, y, z - 1.4), (x + 2.4, y + 0.3, z + 2.4), mPl),
              box((x - 0.6, y + 0.3, z - 0.6), (x + 1.6, y + 2.6, z + 1.6),
                  fin(lambda c: (CARTON, 6) if c.face == 'up' else (PORC, 6), ao=0.3, dust=0)),
              box((x + 1.6, y + 1.0, z + 0.2), (x + 2.2, y + 2.0, z + 0.8), fin(flat(PORC, 6), ao=0))]
    P += [box((3.6, y, 11.0), (6.4, y + 2.2, 13.8), fin(lambda c: (PORC, 6) if c.face != 'up' else (PORC, 4), ao=0.3, dust=0))]
    return P


def tacho_parts():
    """Pedal bin: cream enamel body, chrome lid, black pedal; a plastic bag hem showing under the lid."""
    m = fin(smooth(ENAMEL, base=5, seed=401, grime=0.5), dust=0.6)
    return [box((4.0, 0.4, 4.0), (12.0, 10.4, 12.0), m), box((3.8, 10.4, 3.8), (12.2, 11.4, 12.2), M_CHROME),
            box((3.6, 10.2, 3.6), (12.4, 10.6, 12.4), fin(flat(GRAPH, 4), ao=0)),
            box((6.4, 0.0, 2.4), (9.6, 0.8, 4.0), fin(flat(BLACKP, 3))), box((4.2, 0.0, 4.2), (11.8, 0.4, 11.8), fin(flat(BLACKP, 2)))]


# ============================================================================================ register: dining + kitchen
F('mesa_comedor_extremo', 'Mesa del comedor (extremo)', 'Dining table (end)', mesa_comedor_parts('extremo'))
F('mesa_comedor_centro', 'Mesa del comedor (centro, con camino tejido)', 'Dining table (middle, crocheted runner)',
  mesa_comedor_parts('centro'))
F('silla_comedor', 'Silla del comedor', 'Dining chair', silla_comedor_parts())
F('silla_comedor_volcada', 'Silla del comedor tirada', 'Dining chair knocked over', tip_back(silla_comedor_parts()))
F('aparador_izq', 'Aparador con platos (izquierda)', 'Sideboard with plates (left)', aparador_parts('izq'))
F('aparador_der', 'Aparador con platos (derecha)', 'Sideboard with plates (right)', aparador_parts('der'))
F('lampara_comedor', 'Lámpara del comedor (encendida)', 'Dining room ceiling lamp (lit)', lampara_comedor_parts(True),
  env=('ceil',), light=13, collision='none', directional=False, sound='metal')
F('lampara_comedor_apagada', 'Lámpara del comedor (apagada)', 'Dining room ceiling lamp (off)', lampara_comedor_parts(False),
  env=('ceil',), collision='none', directional=False, sound='metal')
F('mesada', 'Mesada con bajo mesada', 'Kitchen counter', mesada_parts('lisa'), sound='stone')
F('mesada_cajones', 'Mesada con cajones', 'Kitchen counter with drawers', mesada_parts('cajones'), sound='stone')
F('mesada_pileta', 'Mesada con pileta de cocina', 'Kitchen counter with sink', mesada_parts('pileta'), sound='stone')
F('mesada_esquina', 'Mesada (esquina)', 'Kitchen counter (corner)', mesada_parts('esquina'), sound='stone')
F('cocina_gas', 'Cocina a gas con horno', 'Gas stove with oven', cocina_gas_parts(), sound='metal')
F('cocina_gas_pava', 'Cocina a gas con la pava en el fuego', 'Gas stove with the kettle on', cocina_gas_parts(True), light=3,
  sound='metal')
F('heladera_abajo', 'Heladera vieja (abajo)', 'Old rounded fridge (bottom)', heladera_parts('abajo'), sound='metal')
F('heladera_arriba', 'Heladera vieja (arriba)', 'Old rounded fridge (top)', heladera_parts('arriba'), sound='metal', env=())
F('alacena', 'Alacena cerrada', 'Wall cupboard (closed)', alacena_parts('cerrada'), env=('wall',))
F('alacena_abierta', 'Alacena abierta', 'Wall cupboard (doors open)', alacena_parts('abierta'), env=('wall',))
F('alacena_cuerpo', 'Alacena sin puertas (para la puerta trampilla)', 'Wall cupboard body (for the hatch door)',
  alacena_parts('cuerpo'), env=('wall',))
Trapdoor('casa_alacena_puerta', 'Puerta de alacena', 'Cupboard door (opens)', fin(alacena_puerta_tone, ao=0, dust=0), kit=KIT,
         sound='wood')
F('panera', 'Panera (sobre mesada)', 'Bread box (on the counter)', panera_parts(), collision='none', sound='metal')
F('mate_termo', 'Mate y termo (sobre mesada)', 'Mate and thermos (on the counter)', mate_parts(-2.0), collision='none')
F('mate_termo_mesa', 'Mate y termo (sobre mesa)', 'Mate and thermos (on a table)', mate_parts(-4.0), collision='none')
F('pava', 'Pava (sobre mesada)', 'Kettle (on the counter)', pava_parts(), collision='none', sound='metal')
F('escurridor', 'Escurridor de platos (sobre mesada)', 'Dish rack (on the counter)', escurridor_parts(), collision='none',
  sound='metal')
F('reloj_cocina', 'Reloj de cocina', 'Kitchen wall clock', reloj_parts(10, 10), env=('wall',), collision='none')
F('reloj_cocina_333', 'Reloj de cocina (3:33)', 'Kitchen wall clock (3:33)', reloj_parts(3, 33), env=('wall',), collision='none')
F('tubo', 'Tubo fluorescente (encendido)', 'Fluorescent tube (lit)', tubo_parts(True), env=('ceil',), light=14, collision='none',
  sound='glass')
F('tubo_apagado', 'Tubo fluorescente (apagado)', 'Fluorescent tube (off)', tubo_parts(False), env=('ceil',), collision='none',
  sound='glass')
F('mesa_cocina', 'Mesa de cocina con hule', 'Kitchen table with oilcloth', mesa_cocina_parts())
F('silla_cocina', 'Silla de cocina cromada', 'Chrome kitchen chair', silla_cocina_parts(), sound='metal')
F('desayuno', 'Desayuno con medialunas (sobre mesa)', 'Breakfast with croissants (on a table)', desayuno_parts(), collision='none',
  sound='stone')
F('tacho_basura', 'Tacho de basura a pedal', 'Pedal bin', tacho_parts(), sound='metal')


# ============================================================================================ shared helpers (batch 2)
HUESO = pal('#4f4a40', '#6e675a', '#8f8775', '#aca38e', '#c3baa4', '#d5cdb8', '#e3dccb', '#eee9dc', '#f7f4eb')   # sanitary
ROSA_CH = pal('#5a2a3a', '#7e3a52', '#a04c6a', '#bc6482', '#d07e98', '#e09cb0', '#ecbccb', '#f6d9e2', '#fcecf1')         # chenille
CORTINA = pal('#3d5a5c', '#557a7a', '#6f9a98', '#8cb6b2', '#aacfca', '#c6e2dd', '#e0f1ee', '#f2fbf9')
TENNIS = pal('#3a4410', '#5a6a18', '#7e9222', '#a2b82e', '#c2d63e', '#dcec62', '#eef79a')
TIN_B = pal('#060e24', '#0c1a3c', '#132858', '#1c3874', '#284c90', '#3a62a8', '#5680c0')
WATER_T = pal('#141c1c', '#1c2a2a', '#26393a', '#32494a', '#40595a', '#516b6a')
TOWEL_C = pal('#1a3440', '#24485a', '#305e74', '#3e768e', '#5290a8', '#6eaac0', '#94c4d4')


def rbox(frm, to, m, r=0.4, **kw):
    """Box with bevelled vertical edges: two crossed boxes; the second is 0.02 shorter at both ends so the caps never
    z-fight."""
    (x0, y0, z0), (x1, y1, z1) = frm, to
    return [box((x0 + r, y0, z0), (x1 - r, y1, z1), m, **kw),
            box((x0, y0 + 0.02, z0 + r), (x1, y1 - 0.02, z1 - r), m, **kw)]


def porcelain(p=HUESO, base=6, seed=0, grime=0.3, streak=True):
    """Vitreous china / enamel: glossy streak on tall faces, darker rims, limescale and grime creeping up from the floor."""
    def t(ctx):
        P = tp(ctx)
        k = base
        n = vn(P[0] / 6.0, P[1] / 6.0, P[2] / 6.0, seed + 11)
        if n > 0.74:
            k -= 1
        if streak and ctx.face in ('north', 'south', 'west', 'east') and ctx.h > 5:
            g = (ctx.s * 0.35 + ctx.t) % 1.0
            if 0.18 < g < 0.23:
                k += 1
        if ctx.edge() == 0 and ctx.w > 2 and ctx.h > 2:
            k -= 1
        if grime and ctx.face not in ('up', 'down') and P[1] < 3.0 and hh(int(P[0]), int(P[1]), int(P[2]), seed) < grime * (1 - P[1] / 3.0):
            return (CARTON, 3)
        return (p, k)
    return t


def fuzz(p=ROSA_CH, base=5, seed=0, border=0):
    """Chenille / terry pile: tufts of light and dark texels, matted darker centre, optional darker border band."""
    def t(ctx):
        P = tp(ctx)
        k = base
        v = hh(int(P[0]), int(P[1]), int(P[2]), seed)
        if v < 0.22:
            k -= 1
        elif v > 0.86:
            k += 1
        if (int(P[0]) + int(P[2]) * 2 + int(P[1])) % 5 == 0:
            k -= 1
        if border and ctx.face == 'up' and ctx.edge() < border:
            k -= 1
        if ctx.face == 'down':
            k -= 2
        return (p, k)
    return t


def ellipse_up(cx, cz, rx, rz, inside, outside, ring=None):
    """Top-face painter in block space: inside / outside tones of an ellipse (ring=(dr, tone) paints a rim band)."""
    def t(ctx):
        d = ((ctx.pos[0] - cx) / rx) ** 2 + ((ctx.pos[2] - cz) / rz) ** 2
        if ring and 1.0 <= d < (1 + ring[0]) ** 2:
            return ring[1](ctx) if callable(ring[1]) else ring[1]
        if d < 1.0:
            return inside(ctx) if callable(inside) else inside
        return outside(ctx) if callable(outside) else outside
    return t


def card_canvas(kind, seed=0):
    """Estampita (holy card) 6x9 px: gilt or white border, a saint on a coloured ground."""
    cv = Canvas(6, 9, hx('#f2ead8'))
    bg = {'virgen': (hx('#4a78b8'), hx('#a8c8e8')), 'corazon': (hx('#8a1a1a'), hx('#e0a060')),
          'cayetano': (hx('#6a4a24'), hx('#e8c870')), 'expedito': (hx('#2a5a3a'), hx('#c8b070')),
          'gauchito': (hx('#a01010'), hx('#f04030')), 'pompeya': (hx('#3a3a6a'), hx('#d8c8a0')),
          'lujan': (hx('#3a6ab0'), hx('#f0e0a0'))}[kind]
    gold = kind not in ('gauchito',)
    for y in range(9):
        for x in range(6):
            if x in (0, 5) or y in (0, 8):
                cv.set(x, y, hx('#c8a040') if gold and (x + y) % 2 else hx('#efe6d2'))
            else:
                cv.set(x, y, mix(bg[1], bg[0], y / 8.0))
    robe = {'virgen': hx('#e8eef8'), 'corazon': hx('#c42a2a'), 'cayetano': hx('#2a1a14'), 'expedito': hx('#8a1a1a'),
            'gauchito': hx('#1a1a1a'), 'pompeya': hx('#2a4a8a'), 'lujan': hx('#4a8ad0')}[kind]
    cv.set(2, 1, hx('#f0d070'))
    cv.set(3, 1, hx('#f0d070'))                                   # halo
    cv.set(2, 2, hx('#e0b090'))
    cv.set(3, 2, hx('#e0b090'))                                   # face
    for y in range(3, 8):
        w = 1 if y < 5 else 2
        for x in range(3 - w, 3 + w):
            cv.set(x, y, robe)
    if kind == 'corazon':
        cv.set(2, 4, hx('#ffd040'))
    if kind == 'cayetano':
        cv.set(4, 4, hx('#e8c040'))
        cv.set(4, 5, hx('#e8c040'))                              # ears of wheat
    if kind == 'gauchito':
        cv.set(1, 3, hx('#e02020'))
        cv.set(4, 3, hx('#e02020'))                              # red poncho/flag
    if kind == 'lujan':
        for y in range(3, 8):
            cv.set(1, y, hx('#f0e0a0'))
            cv.set(4, y, hx('#f0e0a0'))                          # the rays of the Lujan virgin
    return cv


def card_parts(x, y, z, kind, seed=0, rot=0.0, scale=1.0):
    """A holy card stuck to the wall plane z (face north)."""
    cv = card_canvas(kind, seed)
    w, h = 3.0 * scale, 4.5 * scale
    kw = {'rot': ('z', rot, (x + w / 2, y + h / 2, z))} if rot else {}
    return [box((x, y, z - 0.08), (x + w, y + h, z), fin(canvas_tone(cv, other=lambda c: (PAPER, 6)), ao=0, dust=0.1),
                faces=('north',), **kw)]


# ============================================================================================ BATHROOM
def inodoro_parts():
    """50s low-cistern toilet in bone china, lid up showing the pink chenille lid cover, a matching U-shaped mat round
    the foot, a spare roll on the cistern. Front (bowl) faces 'facing', cistern against the wall behind."""
    mP = fin(porcelain(seed=501), dust=0.3)
    mPc = fin(porcelain(seed=502, grime=0.0), dust=0.6)
    mCh = fin(fuzz(ROSA_CH, base=5, seed=503), dust=0.2)
    mM = fin(fuzz(ROSA_CH, base=4, seed=504, border=2), dust=0.0)

    def bowl_top(ctx):
        if ctx.face != 'up':
            return porcelain(seed=505)(ctx)
        d = ((ctx.pos[0] - 8.0) / 3.0) ** 2 + ((ctx.pos[2] - 6.2) / 3.6) ** 2
        if d < 0.35:
            return (WATER_T, 2 + (hh(ctx.i, ctx.j) > 0.8))
        if d < 1.0:
            k = 3 + int((d - 0.35) * 4)
            if abs(ctx.pos[0] - 8.0) < 0.6 and ctx.pos[2] > 7.5:
                return (CARTON, 3)                                    # limescale streak under the flush
            return (HUESO, k)
        return (HUESO, 6)

    def seat(ctx):
        d = ((ctx.pos[0] - 8.0) / 2.9) ** 2 + ((ctx.pos[2] - 6.2) / 3.5) ** 2
        if ctx.face in ('up', 'down') and d < 1.0:
            return None
        return (PLAST_W, 6 if ctx.face == 'up' else 4)
    P = [box((5.6, 0.0, 5.2), (10.4, 1.0, 12.0), mP),
         box((6.0, 1.0, 4.4), (10.0, 4.0, 12.2), mP)]
    P += rbox((4.2, 4.0, 1.6), (11.8, 6.6, 11.6), fin(bowl_top, dust=0.2), r=1.4)
    P += rbox((4.0, 6.62, 1.4), (12.0, 7.1, 11.8), fin(seat, ao=0.3, dust=0.2), r=1.4)
    P += rbox((2.6, 6.2, 12.6), (13.4, 13.4, 15.8), mPc, r=0.6)                          # cistern
    P += [box((2.4, 13.4, 12.4), (13.6, 14.2, 16.0), mPc),
          box((7.2, 14.2, 13.8), (8.8, 14.5, 15.0), M_CHROME),                             # push button
          box((7.4, 1.6, 12.2), (8.6, 2.8, 16.0), mP)]                                     # outlet to the wall
    P += rbox((4.1, 7.1, 11.8), (11.9, 15.0, 12.5), fin(lambda c: (PLAST_W, 5), ao=0.3), r=1.2)   # lid (up)
    P += rbox((4.4, 7.4, 11.3), (11.6, 14.8, 11.8), mCh, r=1.2)                            # chenille lid cover
    P += [box((2.8, 0.0, 0.6), (13.2, 0.5, 4.6), mM), box((2.8, 0.0, 4.6), (5.0, 0.5, 15.4), mM),
          box((11.0, 0.0, 4.6), (13.2, 0.5, 15.4), mM)]                                    # U-shaped mat
    P += rbox((9.6, 14.2, 13.0), (12.6, 17.0, 15.8), fin(lambda c: ((CARTON, 3) if math.hypot(c.pos[0] - 11.1, c.pos[2] - 14.4) < 0.6 else (LINEN, 7))
                                                                     if c.face == 'up' else (LINEN, 6), ao=0.3, dust=0.3), r=0.5)
    return P


def bidet_parts():
    """Bidet matching the toilet: low bowl, chrome mixer with two cross handles at the back, a folded hand towel."""
    mP = fin(porcelain(seed=511), dust=0.3)

    def top(ctx):
        if ctx.face != 'up':
            return porcelain(seed=512)(ctx)
        d = ((ctx.pos[0] - 8.0) / 3.0) ** 2 + ((ctx.pos[2] - 7.4) / 4.4) ** 2
        if d < 0.08:
            return (IRON, 1)
        if d < 1.0:
            return (HUESO, 3 + int(d * 3))
        return (HUESO, 6)
    P = [box((5.4, 0.0, 5.0), (10.6, 1.0, 13.0), mP), box((5.8, 1.0, 4.0), (10.2, 3.6, 13.6), mP)]
    P += rbox((4.0, 3.6, 2.0), (12.0, 6.2, 14.6), fin(top, dust=0.2), r=1.6)
    mC = fin(brass(NICKEL, base=6, seed=513, tarnish=0.25), dust=0.2)
    P += [box((7.4, 6.2, 12.6), (8.6, 7.6, 13.8), mC), box((7.6, 7.0, 11.4), (8.4, 7.6, 12.6), mC)]
    for x in (5.6, 9.6):
        P += [box((x, 6.2, 12.8), (x + 0.8, 7.2, 13.6), mC), box((x - 0.5, 7.2, 13.0), (x + 1.3, 7.6, 13.4), mC),
              box((x + 0.2, 7.2, 12.5), (x + 0.6, 7.6, 13.9), mC)]
    mT = fin(cloth(TOWEL_C, base=4, seed=514, folds=0.3, stains=0.1), ao=0.4, dust=0.1)
    P += [box((3.6, 6.2, 9.6), (5.4, 6.8, 13.2), mT), box((3.2, 2.6, 9.6), (3.6, 6.8, 13.2), mT, faces=('west', 'east', 'north', 'south', 'down'))]
    return P


def lavatorio_parts():
    """Pedestal washbasin (back to the wall): bone china, chrome taps, soap, a glass with the family's four toothbrushes."""
    mP = fin(porcelain(seed=521), dust=0.3)

    def basin(ctx):
        if ctx.face != 'up':
            return porcelain(seed=522)(ctx)
        d = ((ctx.pos[0] - 8.0) / 4.6) ** 2 + ((ctx.pos[2] - 8.0) / 3.8) ** 2
        if d < 0.04:
            return (IRON, 1)
        if d < 1.0:
            if abs(ctx.pos[0] - 8.0) < 0.5 and ctx.pos[2] > 8.6:
                return (RUST, 4 + (hh(ctx.i, ctx.j) > 0.5))                 # rust streak under the tap
            return (HUESO, 3 + int(d * 3))
        return (HUESO, 6 if hh(ctx.i, ctx.j, 5) > 0.05 else 4)
    mC = fin(brass(NICKEL, base=6, seed=523, tarnish=0.3), dust=0.2)
    P = [box((6.0, 0.0, 8.0), (10.0, 1.0, 12.0), mP), box((6.6, 1.0, 8.6), (9.4, 9.6, 11.4), mP),
         box((5.6, 9.6, 7.6), (10.4, 10.6, 12.4), mP)]
    P += rbox((1.8, 10.6, 3.2), (14.2, 13.4, 15.4), fin(basin, dust=0.2), r=1.4)
    P += [box((1.8, 13.4, 14.6), (14.2, 15.8, 16.0), mP),
          box((7.4, 13.4, 13.0), (8.6, 15.0, 14.4), mC), box((7.6, 14.2, 10.6), (8.4, 14.8, 13.0), mC),
          box((7.6, 13.6, 10.6), (8.4, 14.2, 11.2), mC)]
    for x in (4.6, 10.6):
        P += [box((x, 13.4, 13.2), (x + 0.8, 14.6, 14.0), mC), box((x - 0.6, 14.6, 13.4), (x + 1.4, 15.0, 13.8), mC),
              box((x + 0.2, 14.6, 12.8), (x + 0.6, 15.0, 14.4), mC)]
    P.append(box((2.6, 13.4, 11.6), (5.0, 14.2, 13.0), fin(lambda c: (ROSA_CH, 6 if c.face == 'up' else 5), ao=0.3)))   # soap
    mGl = fin(lambda c: (GLASS_J, 6 if c.i == 1 else 4) if c.face != 'up' else (GLASS_J, 2), ao=0.2, dust=0)
    P.append(box((11.2, 13.4, 11.4), (12.8, 15.6, 13.0), mGl))
    for n, (dx, dz, col) in enumerate(((0.3, 0.3, REDP), (0.9, 0.5, CELESTE), (0.4, 1.0, YELLOWP), (1.0, 1.1, PINK))):
        P.append(box((11.2 + dx, 15.0, 11.4 + dz), (11.6 + dx, 18.4 - n * 0.3, 11.8 + dz), fin(flat(col, 4), ao=0),
                     rot=('z', 22.5 if n % 2 else -22.5, (11.4 + dx, 15.0, 11.6 + dz))))
    return P


def botiquin_parts(cracked=False):
    """Medicine cabinet with a mirror door over the basin (place it in the block above the basin): chrome frame, a
    glass shelf underneath with Marta's face cream and a perfume bottle."""
    mF = fin(smooth(PLAST_W, base=6, seed=531, grime=0.0), dust=0.6)
    mM = fin(mirror_tone(cracked=cracked, seed=533 if cracked else 532, fog=0.3), ao=0, dust=0)
    P = [box((2.6, 2.6, 12.6), (13.4, 13.6, 16.0), mF),
         box((2.4, 2.4, 12.2), (13.6, 2.8, 16.0), M_CHROME), box((2.4, 13.4, 12.2), (13.6, 13.8, 16.0), M_CHROME),
         box((2.4, 2.8, 12.2), (2.8, 13.4, 16.0), M_CHROME), box((13.2, 2.8, 12.2), (13.6, 13.4, 16.0), M_CHROME),
         box((2.8, 2.8, 12.5), (13.2, 13.4, 12.5), mM, faces=('north',)),
         box((12.4, 7.0, 12.0), (12.8, 9.0, 12.2), M_CHROME),                                       # finger pull
         box((1.6, 0.4, 11.6), (14.4, 0.8, 16.0), fin(lambda c: (GLASS_J, 5 if c.face == 'up' else 6), ao=0, dust=0.6)),   # glass shelf
         box((2.0, 0.8, 15.0), (2.6, 2.4, 16.0), M_CHROME), box((13.4, 0.8, 15.0), (14.0, 2.4, 16.0), M_CHROME)]
    P += rbox((3.4, 0.8, 12.6), (6.2, 2.4, 15.2), fin(lambda c: (PORC, 7) if c.face != 'up' else (PINK, 6), ao=0.3), r=0.5)   # cream jar
    P += [box((10.0, 0.8, 13.0), (11.6, 3.0, 14.4), fin(lambda c: (GOLD, 6 if c.i == 1 else 4) if c.face != 'up' else (GOLD, 3), ao=0.2)),
          box((10.4, 3.0, 13.4), (11.2, 3.8, 14.0), fin(flat(BLACKP, 4), ao=0))]                                        # perfume
    P.append(box((7.0, 0.8, 13.8), (9.0, 1.2, 14.6), fin(flat(CELESTE, 4), ao=0)))                    # disposable razor
    return P


def aplique_parts(lit, glass='opal'):
    """Wall light: chrome plate, short arm and a frosted globe (bathroom / patio)."""
    mG = fin(lambda c: (OPAL_LIT, 6 + (c.edge() > 0) - (c.j > c.h - 2)) if lit else (OPAL, 4 + (c.edge() > 0) - (hh(c.i, c.j) < 0.08)),
             ao=0, dust=0 if lit else 0.6)
    P = [box((6.6, 9.0, 15.2), (9.4, 13.0, 16.0), M_CHROME), box((7.5, 10.4, 13.0), (8.5, 11.4, 15.2), M_CHROME),
         box((6.6, 11.0, 11.4), (9.4, 11.8, 14.2), M_CHROME)]
    P += rbox((5.4, 4.6, 9.6), (10.6, 11.0, 14.8), mG, r=1.2, shade=not lit)
    P += [box((6.8, 3.8, 11.0), (9.2, 4.6, 13.4), mG, shade=not lit)]
    return P


def banadera_parts(side):
    """Built-in enamelled iron bathtub, 2 blocks along x: front apron of celeste tiles faces 'facing', back against the
    wall. '_izq' = viewer's left block with the taps and the drain; '_der' = the other end (rubber duck)."""
    izq = side == 'izq'
    off = (0, 0, 0) if izq else (16, 0, 0)

    def inner(ctx):
        P = tp(ctx)
        if ctx.face == 'up' and ctx.pos[1] > 9.0:
            return porcelain(ENAMEL, base=7, seed=543)(ctx)
        if 5.2 < P[1] < 6.4 and ctx.face not in ('up', 'down'):
            return (CARTON, 4 + (hh(int(P[0]), int(P[2])) > 0.6))             # the old bathtub ring
        return porcelain(ENAMEL, base=6, seed=544, grime=0.0)(ctx)
    mI = fin(inner, dust=0.2)
    mApron = fin(only({'north': lambda c: tiles(CELESTE, base=4, size=8, seed=541, off=off, grout=(CROCHET, 5))(c)},
                      inner), dust=0.2)
    xa, xb = (0.0, 14.2) if izq else (1.8, 16.0)
    P = [box((0.0, 0.0, 0.8), (16.0, 8.6, 2.6), mApron),                                     # apron + front wall
         box((0.0, 8.6, 0.6), (16.0, 9.4, 2.8), mI),                                          # front rim (rolled)
         box((0.0, 0.0, 14.0), (16.0, 9.4, 16.0), mI)]                                        # back wall
    if izq:
        P.append(box((14.2, 0.0, 2.6), (16.0, 9.4, 14.0), mI))                                # tap end
    else:
        P.append(box((0.0, 0.0, 2.6), (1.8, 9.4, 14.0), mI))                                  # foot end

    def floor_(ctx):
        if ctx.face == 'up' and izq:
            d = math.hypot(ctx.pos[0] - 12.4, ctx.pos[2] - 8.2)
            if d < 0.7:
                return (IRON, 1)
            if d < 1.0:
                return (NICKEL, 4)
            if d < 3.4 and hh(ctx.i, ctx.j, 3) < 0.5:
                return (WATER_T, 4)                                                           # standing water near the drain
            if abs(ctx.pos[2] - 8.2) < 0.6 and ctx.pos[0] > 12.4:
                return (RUST, 4)
        return inner(ctx)
    P.append(box((xa, 0.0, 2.6), (xb, 1.6, 14.0), fin(floor_, dust=0.0)))
    if izq:
        mC = fin(brass(NICKEL, base=6, seed=545, tarnish=0.3), dust=0.2)
        P += [box((14.6, 11.6, 7.6), (16.0, 12.6, 8.6), mC), box((12.6, 11.6, 7.7), (14.6, 12.4, 8.5), mC),
              box((12.6, 11.0, 7.8), (13.2, 11.6, 8.4), mC)]                                  # spout
        for z in (5.0, 11.0):
            P += [box((15.0, 12.6, z - 0.4), (16.0, 13.4, z + 0.4), mC), box((14.6, 13.4, z - 1.0), (15.4, 13.8, z + 1.0), mC),
                  box((14.6, 13.4, z - 0.2), (15.4, 14.2, z + 0.2), mC)]
            P.append(box((14.4, 12.6, z - 0.15), (14.6, 12.8, z + 0.15), fin(flat(REDP if z < 8 else CELESTE, 5), ao=0)))
        P += chain_parts(13.4, 9.8, 1.6, 11.6, w=0.8)[:1]
        P += [box((12.0, 9.4, 14.2), (13.6, 13.4, 15.6), fin(lambda c: (YELLOWP, 6) if c.j < 3 else (GREENP, 5), ao=0.3)),   # shampoo
              box((10.2, 9.4, 14.4), (11.6, 12.0, 15.8), fin(lambda c: (PINK, 6) if c.face != 'up' else (PLAST_W, 6), ao=0.3))]
    else:
        mD = fin(lambda c: (YELLOWP, 6) if c.face == 'up' else (YELLOWP, 5), ao=0.3, dust=0.3)
        P += [box((5.0, 9.4, 1.0), (7.8, 10.8, 2.6), mD), box((6.0, 10.8, 1.2), (7.8, 12.2, 2.4), mD),                     # rubber duck
              box((5.4, 11.2, 1.2), (6.0, 11.8, 2.4), fin(flat(GERAN, 5), ao=0)),
              box((6.1, 11.6, 1.15), (6.5, 12.0, 1.2), fin(flat(BAKE, 1), ao=0)), box((6.1, 11.6, 2.4), (6.5, 12.0, 2.45), fin(flat(BAKE, 1), ao=0))]
    return P


def curtain_print(kind):
    """Shower curtain (translucent plastic): pleats, a print of little fish and bubbles, black mildew at the hem.
    kind 'silueta': a small dark figure standing behind it."""
    def t(ctx):
        P = tp(ctx)
        u = P[0] if ctx.face in ('north', 'south') else P[2]
        v = 32 - P[1]
        pl = math.sin(u / 2.0 * 2.2 + 0.7 * math.sin(u / 6.0))
        k = 5 + (1 if pl > 0.55 else (-1 if pl < -0.5 else 0))
        c = T(CORTINA, k)
        a = 170
        lu, lv = u % 12.0, (P[1] + (int(u // 12) % 2) * 6) % 12.0
        if 3 <= lu < 7 and 4 <= lv < 6:
            c = T(YELLOWP, 5) if lu < 6 else T(ROSE, 5)                     # a little fish
            a = 230
            if lu >= 6:
                c = T(YELLOWP, 4)
        elif abs(lu - 9.0) < 0.7 and abs(lv - 9.0) < 0.7:
            c = T(CORTINA, 7)                                                 # bubble
        hem = P[1] + 12.8
        if hem < 4.0 and vn(u / 2.0, P[1] / 1.5, 0.3, 547) > 0.35 + hem * 0.12:
            c = mix(c, hx('#141a14'), 0.75)                                   # mildew
            a = 230
        if kind == 'silueta':
            fx, fy = u - 18.0, P[1] + 4.0
            body = (abs(fx) < 3.4 - max(0.0, (fy - 8) * 0.5) and -12 < fy < 9) or math.hypot(fx, (fy - 11.0) * 0.9) < 2.6
            if body:
                edge_ = abs(fx) > 3.4 - max(0.0, (fy - 8) * 0.5) - 1.0 and math.hypot(fx, (fy - 11.0) * 0.9) > 1.6
                c = mix(c, hx('#070909'), 0.6 if edge_ else 0.8)
                a = 235
        if hh(ctx.i, ctx.j, 548) < 0.004:
            return None
        return (c[0], c[1], c[2], a)
    return t


def cortina_ducha_parts(kind):
    """Shower curtain on a chrome rod; place it in the block ABOVE the bathtub (it hangs down to the rim).
    kind: 'cerrada' | 'silueta' (a small figure behind it) | 'corrida' (bunched at the viewer's right end)."""
    mR = fin(brass(NICKEL, base=5, seed=549, tarnish=0.4), dust=0.4)
    z = 1.6
    P = [box((0.0, 14.6, z - 0.3), (16.0, 15.2, z + 0.3), mR)]
    ct = curtain_print('silueta' if kind == 'silueta' else 'cerrada')
    if kind == 'corrida':
        for n in range(5):
            x = 0.4 + n * 0.8
            P.append(box((x, -6.4, z - 0.9 + (n % 2) * 0.6), (x + 0.8, 14.4, z - 0.3 + (n % 2) * 0.6), ct,
                         faces=('north', 'south', 'west', 'east')))
        for x in (0.6, 1.4, 2.2, 3.0, 3.8):
            P.append(box((x, 14.2, z - 0.5), (x + 0.5, 15.6, z + 0.5), mR, faces=('north', 'south', 'west', 'east')))
    else:
        P.append(box((0.0, -6.4, z), (16.0, 14.4, z), ct, faces=('north', 'south')))
        for x in (1.0, 5.0, 9.0, 13.0):
            P.append(box((x, 14.2, z - 0.5), (x + 0.5, 15.6, z + 0.5), mR, faces=('north', 'south', 'west', 'east')))
    return P


def ducha_parts():
    """Shower arm and rose coming out of the wall (place it on the wall above the tap end of the tub)."""
    mC = fin(brass(NICKEL, base=6, seed=551, tarnish=0.35), dust=0.4)

    def rose(ctx):
        if ctx.face == 'down':
            return (NICKEL, 2) if (ctx.i % 2 == 0 and ctx.j % 2 == 0 and 0 < ctx.i < ctx.w - 1 and 0 < ctx.j < ctx.h - 1) else (NICKEL, 5)
        return brass(NICKEL, base=6, seed=552)(ctx)
    P = [box((7.4, 14.0, 14.8), (8.6, 15.2, 16.0), mC), box((7.5, 14.2, 10.6), (8.5, 15.0, 14.8), mC),
         box((7.0, 12.6, 8.4), (9.0, 14.2, 11.6), mC),
         box((7.5, 0.0, 15.0), (8.5, 14.0, 16.0), mC)]                                  # riser pipe from the taps
    P += rbox((5.6, 12.0, 7.6), (10.4, 12.6, 12.4), fin(rose, dust=0), r=1.0)
    P += [box((7.6, 11.98, 9.6), (8.4, 12.0, 10.4), fin(flat(RUST, 4), ao=0), faces=('down',))]
    return P


def toallero_parts():
    """Chrome towel rail with a faded blue bath towel and a small pink one (wall, place at chest height)."""
    mC = fin(brass(NICKEL, base=6, seed=561, tarnish=0.35), dust=0.4)
    P = [box((1.0, 3.4, 13.0), (15.0, 4.2, 13.8), mC),
         box((1.4, 3.0, 13.4), (2.4, 4.6, 16.0), mC), box((13.6, 3.0, 13.4), (14.6, 4.6, 16.0), mC)]

    def terry(p, sd):
        def t(ctx):
            pl, k = fuzz(p, base=4, seed=sd)(ctx)
            Y = ctx.pos[1]
            if -7.0 < Y < -5.8 or -5.2 < Y < -4.6:
                k += 2                                                        # woven band near the hem
            return (pl, k)
        return t
    mB = fin(terry(TOWEL_C, 562), ao=0.4, dust=0.0)
    mPk = fin(terry(ROSA_CH, 563), ao=0.4, dust=0.0)
    P += [box((2.6, -8.6, 12.4), (8.8, 4.2, 13.0), mB), box((2.6, -6.0, 13.8), (8.8, 4.2, 14.4), mB),
          box((2.6, 4.2, 12.4), (8.8, 4.8, 14.4), mB),
          box((9.4, -4.0, 12.5), (13.4, 4.2, 13.0), mPk), box((9.4, -2.4, 13.8), (13.4, 4.2, 14.3), mPk),
          box((9.4, 4.2, 12.5), (13.4, 4.7, 14.3), mPk)]
    return P


def portarrollo_parts():
    mC = fin(brass(NICKEL, base=6, seed=571, tarnish=0.35), dust=0.4)

    def roll(ctx):
        if ctx.face in ('west', 'east'):
            d = math.hypot(ctx.s - 0.5, ctx.t - 0.5)
            return (CARTON, 4) if d < 0.18 else (LINEN, 7 if (int(d * 14) % 2) else 6)
        return (LINEN, 7 if ctx.i % 4 else 6)
    P = [box((4.0, 8.6, 15.0), (12.0, 10.6, 16.0), mC), box((4.0, 9.2, 12.6), (5.0, 10.0, 15.0), mC),
         box((11.0, 9.2, 12.6), (12.0, 10.0, 15.0), mC)]
    P += rbox((5.0, 7.6, 11.0), (11.0, 12.0, 15.2), fin(roll, ao=0.3, dust=0.3), r=0.8)
    P.append(box((5.4, 4.4, 10.95), (10.6, 9.0, 11.0), fin(lambda c: (LINEN, 7 if c.j % 5 else 5), ao=0, dust=0), faces=('north', 'south')))
    return P


def alfombra_bano_parts():
    m = fin(fuzz(ROSA_CH, base=4, seed=581, border=2), dust=0.0)
    return rbox((1.6, 0.0, 3.6), (14.4, 0.6, 12.4), m, r=1.4)


# ============================================================================================ NONA'S ROOM
def lace_edge_tone(seed=0, flip=False):
    """Crocheted lace border hanging off a sheet / altar cloth (cutout): picot scallops at the bottom (top if flip),
    filet holes."""
    def t(ctx):
        i, j, w, h = ctx.i, ctx.j, ctx.w, ctx.h
        if flip:
            j = h - 1 - j
        sc = abs(((i / 4.0) % 1.0) - 0.5)
        if j > h - 1 - (0.5 - sc) * 4:
            return None
        if j < 1:
            return T(CROCHET, 6)
        if (i % 2 == 0 and j % 2 == 0):
            return None
        return T(CROCHET, 6 if (i + j) % 4 else 5)
    return t


def bed_frame_wood(head, seed=0, pal_=CAOBA, h_head=21.0, h_foot=12.0):
    """Lustred single bed frame. head=True: headboard at the back (z=16), side rails toward the front.
    head=False: footboard at the front (z=0)."""
    wd = lambda sd, **kw: lustre(pal_, seed=seed + sd, worn_pal=RAW, **kw)
    mP = fin(outline(wd(1, base=3, axis=1)))
    mR = fin(wd(2, base=4, axis=2))
    zb = (14.4, 16.0) if head else (0.0, 1.6)
    top = h_head if head else h_foot

    def board(ctx):
        pl, k = wd(3, base=4, axis=0)(ctx)
        if ctx.face in ('north', 'south'):
            Y = ctx.pos[1]
            if abs(Y - (top - 3.0)) < 0.35 or abs(Y - 10.4) < 0.35:
                k -= 2                                                         # routed lines
            if top - 2.6 < Y < top - 1.2 and abs(ctx.pos[0] - 8) < 2.2:
                k += 1                                                         # carved rosette band
        return (pl, k)
    mB = fin(board)
    P = []
    for x0 in (0.4, 14.2):
        P.append(box((x0, 0.0, zb[0]), (x0 + 1.4, top + 0.6, zb[1]), mP))
        P.append(box((x0 - 0.1, top + 0.6, zb[0] - 0.1), (x0 + 1.5, top + 1.4, zb[1] + 0.1), mR))
        P.append(box((x0 + 0.2, 3.6, 0.0 if head else zb[1]), (x0 + 1.2, 5.6, zb[0] if head else 16.0), mR))   # side rails
    P.append(box((1.8, 4.0, zb[0] + 0.3), (14.2, top, zb[1] - 0.3), mB))
    if head:
        P.append(box((4.2, top, zb[0] + 0.3), (11.8, top + 1.6, zb[1] - 0.3), mB))      # arched crest (stepped)
        P.append(box((6.0, top + 1.6, zb[0] + 0.3), (10.0, top + 2.6, zb[1] - 0.3), mB))
    return P


def cama_nona_parts(piece):
    """Nona Pocha's single bed: lustred wood, granny-square crocheted blanket, lace-edged sheet, a knitted red cushion
    on the pillow. 'cabecera' (headboard against the wall opposite to facing) + 'pie' (the next block toward facing)."""
    head = piece == 'cabecera'
    P = bed_frame_wood(head, seed=601)
    mT = fin(lambda c: (LINEN, 5 if (int(tp(c)[0]) % 6) else 4), ao=0.8, dust=0)
    mG = fin(granny(603, size=8), ao=0.6, dust=0.3)
    z0, z1 = (0.0, 14.4) if head else (1.6, 16.0)
    P.append(box((1.6, 5.2, z0), (14.4, 8.4, z1), mT))                                    # mattress
    if head:
        P += [box((0.3, 8.4, 0.0), (15.7, 9.0, 9.6), mG),                                   # blanket on top
              box((0.3, 4.4, 0.0), (0.6, 8.4, 9.6), mG), box((15.4, 4.4, 0.0), (15.7, 8.4, 9.6), mG),   # hanging sides
              box((0.3, 9.0, 8.0), (15.7, 9.4, 10.4), fin(cloth(LINEN, base=7, seed=605, folds=0.3, stains=0.2), ao=0.4)),   # sheet fold
              box((1.6, 8.4, 9.6), (14.4, 9.0, 14.4), fin(cloth(LINEN, base=6, seed=606, folds=0.4, stains=0.3), ao=0.6)),
              plane((0.4, 9.03, 6.6), (15.6, 9.03, 8.0), fin(lace_edge_tone(607, flip=True), ao=0, dust=0), faces=('up',))]
        P += rbox((2.4, 8.4, 10.6), (13.6, 11.0, 14.2), fin(cloth(LINEN, base=7, seed=608, folds=0.5, fold_px=3.0, stains=0.2), ao=0.6), r=0.8)
        P += [box((5.0, 9.6, 10.2), (11.0, 14.0, 11.2), fin(knit(WOOL_R, base=5, seed=609)), rot=('x', -22.5, (8.0, 9.6, 10.7)))]
    else:
        P += [box((0.3, 8.4, 1.6), (15.7, 9.0, 16.0), mG),
              box((0.3, 4.4, 1.6), (0.6, 8.4, 16.0), mG), box((15.4, 4.4, 1.6), (15.7, 8.4, 16.0), mG),
              box((2.0, 9.0, 2.0), (14.0, 9.8, 6.0), fin(knit(CROCHET, base=5, seed=611)))]     # a folded shawl
    return P


def virgen_mini_parts(x, z, y0, s=0.5):
    """A small plaster Virgen de Lujan (triangular celeste mantle, white gown, gilt rays, crown); s = height scale
    (s=0.5 -> about 9.5/16 tall with the rays)."""
    def gown(ctx):
        if ctx.face == 'north':
            mid = abs(ctx.s - 0.5)
            if mid < 0.12 + 0.12 * ctx.t:
                return (LINEN, 7) if mid < 0.08 + 0.12 * ctx.t else (GOLD, 5)
        if (ctx.i * 5 + ctx.j * 3) % 9 == 0:
            return (LINEN, 8)
        return (CELESTE, 4 + (ctx.i % 3 == 0))
    mG = fin(gown, ao=0.5, dust=0.6)
    mGold = fin(brass(GOLD, base=5, seed=621), ao=0, dust=0.4)
    P = []
    for n, (hw, a, b) in enumerate(((4.6, 0.0, 4.0), (3.9, 4.0, 8.0), (3.1, 8.0, 11.0), (2.3, 11.0, 13.0))):
        P.append(box((x - hw * s, y0 + a * s, z - 2.6 * s + n * 0.02), (x + hw * s, y0 + b * s, z + 2.6 * s - n * 0.02), mG))
    P += [box((x - 2.0 * s, y0 + 13.0 * s, z - 2.0 * s), (x + 2.0 * s, y0 + 15.6 * s, z + 2.0 * s),
              fin(lambda c: (SKIN, 6) if c.face == 'north' and c.j > 0 else (CELESTE, 4), ao=0.3)),
          box((x - 2.1 * s, y0 + 15.6 * s, z - 2.1 * s), (x + 2.1 * s, y0 + 17.0 * s, z + 2.1 * s), mGold),
          plane((x - 7.2 * s, y0 + 6.0 * s, z + 3.0 * s), (x + 7.2 * s, y0 + 19.0 * s, z + 3.0 * s), fin(rays_mini_tone, ao=0, dust=0.2),
                faces=('north', 'south'))]
    return P


def rays_mini_tone(ctx):
    w, h = ctx.w, ctx.h
    cx, cy = w / 2, h * 0.22
    x, y = ctx.i + 0.5 - cx, ctx.j + 0.5 - cy
    r = math.hypot(x, y)
    a = math.atan2(y, x)
    if r < 2.0 or r > h * 0.55 - abs(math.sin(a)) * 2:
        return None
    if (a / (2 * math.pi) * 16) % 1.0 < 0.35:
        return T(GOLD, 6 - int(r / h * 4))
    return None


def novena_candle(x, z, y0, h, lit, col, seed=0):
    """Tall glass novena candle with a printed saint label and coloured wax; flame on top when lit."""
    def t(ctx):
        if ctx.face == 'up':
            d = max(abs(ctx.s - 0.5), abs(ctx.t - 0.5))
            return (col, 3) if d < 0.3 else (GLASS_J, 5)
        if 0.3 < ctx.t < 0.75:
            if 0.25 < ctx.s < 0.75 and 0.38 < ctx.t < 0.68:
                return (GOLD, 6) if ctx.t < 0.45 else (CELESTE, 5)          # saint picture on the label
            return (PAPER, 7)
        return (col, 5 if ctx.i != 1 else 6)
    P = [box((x - 0.9, y0, z - 0.9), (x + 0.9, y0 + h, z + 0.9), fin(t, ao=0.3, dust=0.3))]
    if lit:
        P += flame_parts(x, z, y0 + h - 0.4, h=2.0, w=1.2)
    return P


def altar_parts(lit):
    """The Nona's home altar on a small lustred table against the wall: lace cloth, a little Virgen de Lujan, two novena
    candles and two tea lights, plastic flowers, a rosary hanging over the edge, holy cards leaning on the statue.
    Lit = the safe light of the house (12)."""
    wd = lambda sd, **kw: lustre(CAOBA, seed=631 + sd, worn_pal=RAW, **kw)
    mL = fin(outline(wd(0, base=3, axis=1)))
    mTop = fin(wd(1, base=4, axis=0, boards=(2, 10)))
    P = []
    for (x, z) in ((2.0, 6.4), (12.8, 6.4), (2.0, 14.0), (12.8, 14.0)):
        P += turned_leg(x, z, 0.0, 11.2, mL, w=1.2, rings=(0.3, 0.7))
    P += [box((1.4, 11.2, 5.8), (14.6, 12.0, 15.8), mTop),
          box((2.4, 9.6, 6.6), (13.6, 11.2, 7.2), fin(wd(2, base=3, axis=0))),
          plane((1.6, 12.04, 6.0), (14.4, 12.04, 15.6), fin(runner_tone(633), ao=0, dust=0.2), faces=('up',)),
          plane((1.6, 8.0, 5.75), (14.4, 12.04, 5.75), fin(lace_edge_tone(634), ao=0, dust=0), faces=('north', 'south'))]
    P += virgen_mini_parts(8.0, 12.8, 12.04, s=0.62)
    P += novena_candle(3.6, 9.6, 12.04, 5.2, lit, REDP, 1) + novena_candle(12.4, 9.6, 12.04, 4.4, lit, YELLOWP, 2)
    for (x, z) in ((5.6, 7.6), (10.4, 7.6)):
        P += [box((x - 0.9, 12.04, z - 0.9), (x + 0.9, 12.7, z + 0.9), M_CHROME),
              box((x - 0.7, 12.7, z - 0.7), (x + 0.7, 12.75, z + 0.7), fin(flat(WAX, 6), ao=0))]
        if lit:
            P += flame_parts(x, z, 12.8, h=1.6, w=1.0)
    P += card_parts(5.2, 12.1, 10.6, 'cayetano', rot=22.5, scale=0.7) + card_parts(9.6, 12.1, 10.6, 'gauchito', rot=-22.5, scale=0.7)
    mBead = fin(flat(BAKE, 4), ao=0, dust=0.2)
    for k in range(7):
        P.append(box((6.4 + k * 0.5, 11.0 - math.sin(k / 6 * math.pi) * 1.6, 5.6), (6.8 + k * 0.5, 11.4 - math.sin(k / 6 * math.pi) * 1.6, 5.7), mBead))
    P.append(box((7.8, 8.6, 5.6), (8.2, 9.6, 5.7), mBead))
    P.append(box((7.5, 9.0, 5.6), (8.5, 9.3, 5.7), mBead))
    mGl = fin(lambda c: (GLASS_J, 4 + (c.i % 3 == 1) + (c.face == 'up')), ao=0, dust=0.4)
    P += [box((12.0, 12.04, 13.0), (13.6, 15.0, 14.6), mGl)]
    for (dx, dz, ht, col) in ((-0.4, 0.2, 3.0, GERAN), (0.4, -0.2, 3.8, PINK), (0.0, 0.5, 2.6, LINEN)):
        xx, zz = 12.8 + dx, 13.8 + dz
        P += [box((xx - 0.1, 15.0, zz - 0.1), (xx + 0.1, 15.0 + ht, zz + 0.1), fin(flat(LEAF, 3), ao=0)),
              box((xx - 0.6, 14.8 + ht, zz - 0.6), (xx + 0.6, 15.6 + ht, zz + 0.6), fin(lambda c, col=col: (col, 4 + ((c.i + c.j) % 2)), ao=0))]
    return P


def palm_tone(ctx):
    """Dried palm frond (Domingo de Ramos) braided into a cross: straw stripes."""
    return (RUSH, 4 + (ctx.i % 2) - (ctx.edge() == 0))


def estampitas_parts():
    """The wall above the altar: holy cards stuck in a cluster, a wooden crucifix with a dried palm, a framed Sagrado
    Corazon print and a red ribbon (Gauchito Gil). Wall piece: place it in the block above casa_altar."""
    P = []
    kinds = ['virgen', 'corazon', 'cayetano', 'expedito', 'gauchito', 'pompeya', 'lujan']
    spots = [(1.0, 1.2, 0), (4.4, 0.6, 22.5), (11.4, 0.8, -22.5), (12.8, 5.6, 0), (0.6, 6.4, -22.5), (5.6, 11.6, 22.5),
             (12.2, 10.8, 0), (8.6, 0.4, 0), (14.2, 1.4, 22.5), (3.6, 5.0, 0)]
    for n, (x, y, r) in enumerate(spots):
        P += card_parts(x, y, 15.94 - (n % 3) * 0.02, kinds[n % len(kinds)], seed=n, rot=r, scale=0.9)
    mW = fin(outline(wood(NOGAL, seed=641, base=3)))
    P += [box((7.4, 3.6, 15.0), (8.6, 13.4, 16.0), mW), box((5.4, 9.8, 15.0), (10.6, 11.0, 16.0), mW),
          box((7.6, 6.0, 14.7), (8.4, 10.6, 15.0), fin(flat(GOLD, 5), ao=0)),
          box((6.6, 10.0, 14.7), (9.4, 10.6, 15.0), fin(flat(GOLD, 5), ao=0)),
          box((7.6, 10.6, 14.7), (8.4, 11.4, 15.0), fin(flat(GOLD, 6), ao=0))]
    P += [box((9.0, 11.0, 15.2), (9.6, 15.6, 15.5), fin(palm_tone, ao=0), rot=('z', -22.5, (9.3, 11.0, 15.3))),
          box((8.6, 12.4, 15.2), (11.4, 13.0, 15.5), fin(palm_tone, ao=0), rot=('z', -22.5, (9.3, 11.0, 15.3)))]
    cv = Canvas(8, 10, hx('#e8dcc0'))
    for y in range(10):
        for x in range(8):
            cv.set(x, y, mix(hx('#f0c880'), hx('#8a5a2a'), math.hypot(x - 3.5, y - 3.5) / 6.0))
    cv.ascii(1, 1, ['..hh..', '.hssh.', '.hssh.', 'RRssRR', 'RRhrRR', 'RRRRRR', 'RRRRRR', '.RRRR.'],
             {'h': hx('#3a2018'), 's': hx('#e0b090'), 'R': hx('#b02020'), 'r': hx('#ffd040')})
    mPic = fin(canvas_tone(cv), ao=0, dust=0.2)
    mFr = fin(brass(GOLD, base=4, seed=643, tarnish=0.5), dust=0.4)
    P += [box((0.8, 9.0, 15.4), (4.8, 14.0, 15.5), mPic, faces=('north',)),
          box((0.4, 8.6, 15.5), (5.2, 9.0, 16.0), mFr), box((0.4, 14.0, 15.5), (5.2, 14.4, 16.0), mFr),
          box((0.4, 9.0, 15.5), (0.8, 14.0, 16.0), mFr), box((4.8, 9.0, 15.5), (5.2, 14.0, 16.0), mFr)]
    P += [box((13.0, 13.6, 15.6), (14.0, 15.6, 15.9), fin(flat(REDP, 5), ao=0)),
          box((12.6, 10.0, 15.7), (13.4, 13.6, 15.9), fin(flat(REDP, 6), ao=0), rot=('z', 22.5, (13.0, 13.6, 15.8))),
          box((13.6, 10.4, 15.7), (14.4, 13.6, 15.9), fin(flat(REDP, 4), ao=0), rot=('z', -22.5, (14.0, 13.6, 15.8)))]
    return P


def ball_parts(cx, cy, cz, r, m):
    """A wool ball / fruit / tennis ball: three crossed boxes (offsets keep every pair of faces apart: no z-fighting)."""
    a = r * 0.7
    return [box((cx - r, cy - a, cz - a), (cx + r, cy + a, cz + a), m),
            box((cx - a + 0.03, cy - r + 0.02, cz - a + 0.03), (cx + a - 0.03, cy + r - 0.02, cz + a - 0.03), m),
            box((cx - a + 0.06, cy - a + 0.06, cz - r), (cx + a - 0.06, cy + a - 0.06, cz + r), m)]


def wheel_yz(x0, x1, cy, cz, r, m):
    """A wheel turning about the x axis: two crossed boxes in the y-z plane (octagonal side view)."""
    return [box((x0, cy - r * 0.62, cz - r), (x1, cy + r * 0.62, cz + r), m),
            box((x0 + 0.02, cy - r, cz - r * 0.62), (x1 - 0.02, cy + r, cz + r * 0.62), m)]


def wicker(p=RUSH, base=4, seed=0):
    """Woven wicker: over-under strands, darker uprights every 3 px."""
    def t(ctx):
        u, v = uv2(ctx)
        if ctx.face in ('up', 'down'):
            x, y, z = tp(ctx)
            u, v = x, z
        iu, iv = int(math.floor(u)), int(math.floor(v))
        k = base + (1 if (iu // 2 + iv) % 2 == 0 else -1)
        if iu % 3 == 0:
            k -= 1
        if hh(iu, iv, seed) < 0.06:
            k -= 1
        return (p, k)
    return t


def canasta_lana_parts():
    """Wicker basket with balls of red wool, two knitting needles stuck in, the red scarf in progress over the rim."""
    mW = fin(wicker(RUSH, base=4, seed=651), dust=0.6)
    mWool = fin(knit(WOOL_R, base=5, seed=652), dust=0.1)
    P = rbox((2.6, 0.0, 3.0), (13.4, 6.4, 13.0), mW, r=1.6)
    P += [box((3.0, 6.4, 3.4), (13.0, 6.9, 12.6), fin(wicker(RUSH, base=3, seed=653), dust=0.4))]
    P += ball_parts(5.8, 7.4, 7.6, 1.8, mWool) + ball_parts(10.0, 7.2, 9.6, 1.7, fin(knit(WOOL_R, base=4, seed=654))) + \
        ball_parts(9.2, 7.4, 5.8, 1.4, fin(knit(WOOL_R, base=6, seed=655))) + ball_parts(6.6, 7.0, 10.6, 1.3, fin(knit(CROCHET, base=5, seed=658)))
    mN = fin(brass(NICKEL, base=6, seed=656), ao=0, dust=0)
    P += [box((7.6, 7.0, 6.6), (8.0, 15.0, 7.0), mN, rot=('z', 22.5, (7.8, 7.0, 6.8))),
          box((8.6, 7.0, 7.6), (9.0, 14.2, 8.0), mN, rot=('x', -22.5, (8.8, 7.0, 7.8))),
          box((8.4, 14.6, 7.6), (9.2, 15.4, 8.4), fin(flat(REDP, 6), ao=0))]
    mS = fin(knit(WOOL_R, base=5, seed=657, cable=True), dust=0.1)
    P += [box((4.6, 6.9, 2.6), (8.6, 7.3, 6.4), mS), box((4.6, 2.2, 2.2), (8.6, 7.3, 2.6), mS),
          box((4.6, 0.0, 0.6), (8.6, 0.4, 2.6), mS), box((4.6, 0.4, 1.6), (8.6, 2.2, 2.0), mS)]
    return P


def andador_parts():
    """Aluminium walker: front legs on two grey wheels (one is a mismatched red toy wheel wrapped in tape: the one that
    squeaks), back legs in split tennis balls, foam grips, a crocheted bag on the front bar with wool and a thermos.
    The user walks toward 'facing'."""
    mA = fin(brass(ALU, base=4, seed=661, tarnish=0.25), dust=0.4)
    mF = fin(smooth(GRAPH, base=4, seed=662, grime=0.0), dust=0.3)

    def wheel(col, taped=False):
        def t(ctx):
            if ctx.face in ('west', 'east'):
                d = math.hypot(ctx.pos[1] - 1.2, ctx.pos[2] - 2.8) / 2.4
                if d < 0.14:
                    return (RUST, 3) if taped else (NICKEL, 5)
                if taped and abs(ctx.s - 0.5) < 0.14:
                    return (BLACKP, 3)
                return (col, 3 + (d < 0.32))
            if taped and ctx.i % 3 == 0:
                return (BLACKP, 2)
            return (col, 2)
        return fin(t, ao=0.2)

    def ball(ctx):
        pl, k = fuzz(TENNIS, base=4, seed=663)(ctx)
        if abs(math.sin(ctx.pos[0] * 1.4) * 0.8 - (ctx.pos[1] - 1.4)) < 0.25:
            return (CROCHET, 7)                                                  # felt seam
        return (pl, k)
    P = []
    for x in (2.2, 13.0):
        P += [box((x, 2.4, 2.4), (x + 0.8, 13.0, 3.2), mA),                     # front leg
              box((x, 2.0, 12.6), (x + 0.8, 13.0, 13.4), mA),                    # back leg
              box((x, 12.6, 2.4), (x + 0.8, 13.4, 13.4), mA),                    # top side bar
              box((x - 0.2, 12.4, 9.0), (x + 1.0, 14.2, 13.6), mF),              # foam grip
              box((x + 0.1, 5.6, 3.2), (x + 0.7, 6.2, 12.6), mA)]                # lower side bar
        P += ball_parts(x + 0.4, 1.3, 13.0, 1.3, fin(ball, ao=0.2, dust=0.4))
    P += wheel_yz(1.9, 3.3, 1.2, 2.8, 1.2, wheel(STEEL)) + wheel_yz(12.7, 14.1, 1.2, 2.8, 1.2, wheel(REDP, taped=True))
    P += [box((2.0, 2.2, 2.4), (3.2, 2.6, 3.2), mA), box((12.8, 2.2, 2.4), (14.0, 2.6, 3.2), mA)]
    P += [box((3.0, 11.0, 2.4), (13.0, 11.8, 3.2), mA), box((3.0, 4.4, 2.4), (13.0, 5.2, 3.2), mA)]
    mBag = fin(granny(664, size=6), ao=0.5, dust=0.2)
    P += [box((5.0, 6.6, 1.8), (11.0, 11.0, 2.4), mBag), box((5.0, 6.6, 2.4), (11.0, 7.2, 4.4), mBag),
          box((5.0, 7.2, 3.8), (11.0, 10.0, 4.4), mBag)]
    P += ball_parts(6.8, 10.8, 3.2, 1.2, fin(knit(WOOL_R, base=5, seed=665)))
    P += [box((8.8, 6.4, 2.6), (10.6, 14.4, 4.0), fin(painted(pal('#3a0a0a', '#5a1010', '#7a1a16', '#9a2a20', '#b84030'), base=3, seed=666), dust=0.3)),
          box((8.7, 14.4, 2.5), (10.7, 15.4, 4.1), M_CHROME)]
    return P


def ropero_parts(half, pal_=CAOBA, seed=671):
    """Waterfall-style (late 40s) lustred wardrobe, 2 blocks tall ('abajo' / 'arriba'): two doors (left with a bevelled
    mirror), a drawer, rounded cornice. Front faces 'facing', back to the wall."""
    yo = 0 if half == 'abajo' else 16
    off = (0, yo, 0)
    wd = lambda sd, **kw: lustre(pal_, seed=seed + sd, off=off, worn_pal=RAW, **kw)
    mC = fin(panels(wd(0, base=3, axis=1), wd(1, base=4, axis=1), rects=((3, 3, -3, -3),), faces=('west', 'east')))
    mW = fin(wd(2, base=4))

    def door_tone(mirror):
        inner = wd(3 if mirror else 4, base=4, axis=1)
        fr = wd(5, base=4, axis=1)

        def t(ctx):
            if ctx.face != 'north':
                return fr(ctx)
            Y = int((ctx.pos[1] + yo - 5.6) * 2)
            Hd = int((30.0 - 5.6) * 2)
            j = Hd - 1 - Y
            i, w = ctx.i, ctx.w
            if 22 <= j <= 24:
                return (RAW, 3 + (j == 23))                                    # pale veneer band (deco)
            for (a, b) in ((3, 21), (26, Hd - 3)):
                if 2 <= i < w - 2 and a <= j < b:
                    m = min(i - 2, j - a, w - 3 - i, b - 1 - j)
                    if m == 0:
                        return (pal_, 1)
                    if mirror and a == 3:
                        return None
                    pl, k = inner(ctx)
                    if m == 1:
                        k += 1 if (j - a == m or i - 2 == m) else -1
                    return (pl, k)
            return fr(ctx)
        return t
    P = []
    if half == 'abajo':
        P += [box((0.4, 0.0, 2.0), (15.6, 2.2, 15.4), fin(wd(6, base=2, axis=0))),
              box((0.8, 2.2, 2.6), (15.2, 16.0, 15.0), mC),
              box((1.2, 2.6, 2.2), (14.8, 5.2, 2.6), fin(panels(wd(7, base=4, axis=0), rects=((1, 1, -1, -1),), faces=('north',), bevel=0))),
              box((6.4, 3.6, 1.8), (9.6, 4.2, 2.2), M_BRASS)]
    else:
        P += [box((0.8, 0.0, 2.6), (15.2, 14.0, 15.0), mC),
              box((0.4, 14.0, 2.0), (15.6, 15.0, 15.4), mW),
              box((1.0, 15.0, 2.6), (15.0, 15.8, 15.0), fin(wd(8, base=5, axis=0)))]
    y0, y1 = (5.6, 16.0) if half == 'abajo' else (0.0, 14.0)
    P.append(box((1.2, y0, 2.2), (8.0, y1, 2.6), fin(door_tone(True))))
    P.append(box((8.0, y0, 2.2), (14.8, y1, 2.6), fin(door_tone(False))))
    if half == 'abajo':
        P += [box((7.2, 12.0, 1.8), (7.7, 13.6, 2.2), M_BRASS), box((8.3, 12.0, 1.8), (8.8, 13.6, 2.2), M_BRASS),
              box((8.45, 11.0, 2.15), (8.65, 11.6, 2.2), fin(flat(IRON, 0), ao=0))]
    else:
        P.append(box((2.2, 2.6, 2.4), (6.9, 11.6, 2.4), fin(mirror_tone(seed=675), ao=0, dust=0), faces=('north',)))
        P.append(box((3.0, 14.0 + 1.8, 7.0), (11.0, 14.0 + 4.6, 13.0), fin(lambda c: (CARTON, 5 if c.face != 'up' else 6), ao=0.4)))   # hat box on top
        P.append(box((3.0, 17.2, 6.98), (11.0, 17.8, 7.0), fin(flat(REDP, 4), ao=0), faces=('north',)))
    return P


def mesa_luz_parts(kind='lisa'):
    """Lustred nightstand, top at 12/16 (so every 'sobre mesa' prop fits on it): turned feet, drawer over a door, a
    doily. kind 'nona': her 60s radio, a glass of water with her dentures, pills and a rosary."""
    wd = lambda sd, **kw: lustre(CAOBA, seed=681 + sd, worn_pal=RAW, **kw)
    mF = fin(panels(wd(0, base=4, axis=1), rects=((2, 2, -2, -2),), faces=('north',)))
    mD = fin(panels(wd(1, base=4, axis=0), rects=((1, 1, -1, -1),), faces=('north',), bevel=0))
    mL = fin(outline(wd(2, base=3, axis=1)))
    P = []
    for (x, z) in ((2.6, 3.0), (12.2, 3.0), (2.6, 13.0), (12.2, 13.0)):
        P.append(box((x, 0.0, z), (x + 1.2, 2.6, z + 1.2), mL))
    P += [box((2.4, 2.6, 2.8), (13.6, 11.2, 14.6), mF),
          box((2.8, 8.6, 2.4), (13.2, 10.8, 2.8), mD), box((7.4, 9.4, 2.0), (8.6, 10.0, 2.4), M_BRASS),
          box((11.4, 5.2, 2.4), (12.0, 6.4, 2.8), M_BRASS),
          box((2.0, 11.2, 2.2), (14.0, 12.0, 15.0), fin(wd(3, base=4, axis=0, boards=(2, 12))))]
    P.append(plane((3.6, 12.03, 4.0), (12.4, 12.03, 12.8), fin(doily_tone('disc', 683), ao=0, dust=0.3), faces=('up',)))
    if kind == 'nona':
        mR = fin(leatherette(pal('#1a0a0c', '#2c1014', '#40181e', '#562228', '#6c2e34', '#843c40'), base=3, seed=684), dust=0.6)

        def face(ctx):
            if ctx.face != 'north':
                return leatherette(pal('#1a0a0c', '#2c1014', '#40181e', '#562228', '#6c2e34', '#843c40'), base=3, seed=684)(ctx)
            i, j, w, h = ctx.i, ctx.j, ctx.w, ctx.h
            if 1 <= i < w * 0.55 and 1 <= j < h - 1:
                return (GOLD, 5) if (i + j) % 2 == 0 else (GOLD, 3)              # gilt speaker grille
            if w * 0.6 <= i < w - 1 and 1 <= j <= 3:
                return (PAPER, 7) if i % 2 else (BAKE, 3)                        # tuning dial
            if w * 0.6 <= i < w - 1 and j == 2 and i == int(w * 0.8):
                return INK_RED
            if w * 0.6 <= i < w - 1 and j > 4:
                return (CROCHET, 6) if (i - int(w * 0.6)) % 3 else (CROCHET, 4)
            return (pal('#1a0a0c', '#2c1014', '#40181e', '#562228'), 2)
        P += [box((2.4, 12.0, 8.6), (9.4, 16.4, 11.8), fin(face, dust=0.6)),
              box((3.0, 16.4, 9.8), (3.6, 17.6, 10.6), M_CHROME), box((8.2, 16.4, 9.8), (8.8, 17.6, 10.6), M_CHROME),
              box((3.0, 17.6, 9.8), (8.8, 18.2, 10.6), mR),
              box((8.6, 16.4, 11.0), (8.9, 23.0, 11.3), M_CHROME, rot=('z', -22.5, (8.75, 16.4, 11.15)))]

        def glass(ctx):
            if ctx.face == 'up':
                return (GLASS_J, 6) if (ctx.i + ctx.j) % 2 == 0 else None         # dithered water surface
            if ctx.i in (0, ctx.w - 1) or ctx.j == 0 or ctx.j == ctx.h - 1:
                return (GLASS_J, 5)
            if ctx.i == 1 and ctx.j < ctx.h - 2:
                return (GLASS_J, 6)
            return None
        P.append(box((10.4, 12.0, 5.0), (13.2, 16.2, 7.8), fin(glass, ao=0, dust=0)))

        def teeth(ctx):
            if ctx.face in ('north', 'south', 'west', 'east'):
                if ctx.j < ctx.h // 2:
                    return (PORC, 8) if ctx.i % 2 else (PORC, 6)
                return (ROSA_CH, 5)
            return (ROSA_CH, 4)
        P.append(box((10.9, 12.4, 5.6), (12.7, 13.8, 7.2), fin(teeth, ao=0, dust=0)))
        P += [box((4.6, 12.0, 4.4), (8.0, 12.3, 6.4), fin(lambda c: (NICKEL, 6) if (c.i % 3 == 1 and c.j % 3 == 1) else (PLAST_W, 6), ao=0)),
              box((10.0, 12.0, 9.0), (12.8, 15.4, 11.4), fin(lambda c: (PLAST_W, 7) if c.j > 1 else (ROSE, 5), ao=0.3, dust=0.3))]   # pill bottle
        mBead = fin(flat(GRAPH, 5), ao=0, dust=0.2)
        for k in range(8):
            a = k / 8 * 6.28
            P.append(box((6.0 + math.cos(a) * 1.2, 12.0, 7.4 + math.sin(a) * 0.9), (6.4 + math.cos(a) * 1.2, 12.3, 7.8 + math.sin(a) * 0.9), mBead))
    return P


def velador_parts(lit):
    """Bedside lamp ('sobre mesa'): turned brass base, pleated fabric shade. Lit / off pair."""
    y = -4.0
    mB = fin(brass(seed=691, base=4, tarnish=0.5), dust=0.6)
    P = rbox((5.0, y, 5.0), (11.0, y + 0.8, 11.0), mB, r=1.2)
    P += [box((6.4, y + 0.8, 6.4), (9.6, y + 3.4, 9.6), fin(lambda c: (PORC, 6 if c.i % 4 else 4) if c.face != 'up' else (PORC, 5), ao=0.3, dust=0.6)),
          box((7.4, y + 3.4, 7.4), (8.6, y + 6.0, 8.6), mB)]
    P += bulb_parts(8.0, y + 6.0, 8.0, lit, r=0.9, h=1.8)
    P += lamp_shade(3.8, 12.2, 3.8, 12.2, y + 5.4, y + 11.4, lit, seed=693, taper=1.0, th=0.3)
    return P


def plafon_parts(state):
    """Ceiling light of the bedrooms and the upstairs hall: frosted glass bowl on a brass ring, the dark specks of dead
    bugs collected in the bottom. state: 'on' | 'off' | 'roto' (burst bulb, half the bowl gone: the door-cascade scare)."""
    lit = state == 'on'

    def glass(ctx):
        if state == 'roto' and ctx.face in ('down',):
            return None
        P = tp(ctx)
        base = 6 if lit else 4
        if ctx.face == 'down':
            d = math.hypot(ctx.s - 0.5, ctx.t - 0.5)
            if hh(ctx.i, ctx.j, 701) < 0.12 and d < 0.35:
                return (BAKE, 2) if not lit else (OPAL_LIT, 2)                  # dead bugs
            k = base + (1 if d < 0.2 else 0)
            return (OPAL_LIT if lit else OPAL, k)
        k = base + (1 if (int(P[0] + P[2]) % 4 == 0 and ctx.j > 1) else 0)
        if ctx.j <= 0:
            k -= 1
        return (OPAL_LIT if lit else OPAL, k)
    mG = fin(glass, ao=0, dust=0 if lit else 0.4)
    mB = fin(brass(seed=703, base=4, tarnish=0.5), dust=0.5)
    P = [box((5.0, 15.2, 5.0), (11.0, 16.0, 11.0), mB), box((3.2, 14.6, 3.2), (12.8, 15.2, 12.8), mB)]
    if state == 'roto':
        sh = fin(lambda c: (OPAL, 4) if hh(c.i, c.j, 704) > 0.25 else None, ao=0, dust=0.3)
        P += [box((3.6, 12.4, 3.6), (12.4, 14.6, 4.0), sh), box((3.6, 13.2, 12.0), (12.4, 14.6, 12.4), sh),
              box((3.6, 11.6, 4.0), (4.0, 14.6, 12.0), sh), box((12.0, 12.8, 4.0), (12.4, 14.6, 12.0), sh)]
        P += [box((7.2, 13.4, 7.2), (8.8, 14.6, 8.8), M_CHROME),
              box((7.0, 11.2, 7.0), (9.0, 13.4, 9.0), fin(lambda c: (GLASS_J, 2) if hh(c.i, c.j, 705) > 0.4 else None, ao=0))]
        return P
    P += rbox((3.6, 11.8, 3.6), (12.4, 14.6, 12.4), mG, r=1.6, shade=not lit)
    P += [box((5.6, 10.8, 5.6), (10.4, 11.8, 10.4), mG, shade=not lit), box((7.5, 10.2, 7.5), (8.5, 10.8, 8.5), mB)]
    return P


def lata_parts(state, y=-4.0):
    """Round blue cookie tin ('lata Galletitas'): gilt bands, a painted plate of cookies on the lid.
    state 'cerrada' | 'abierta' (sewing kit inside: red thread, needles in a tomato pincushion, buttons, and the small
    photo 'Nelida y Ofelia, 1960') | 'vieja' (the 1961 one dug up: rusted, dented, empty, soil inside; on the floor)."""
    old = state == 'vieja'
    if old:
        y = 0.0

    def side(ctx):
        P = tp(ctx)
        Y = ctx.pos[1] - y
        if old and vn(P[0] / 2.0, P[1] / 2.0, P[2] / 2.0, 711) > 0.5:
            return (RUST, 3 + (hh(*P) > 0.6))
        if 0.3 < Y < 0.8 or 3.0 < Y < 3.5:
            return (GOLD, 5 if not old else 3)
        if 1.2 < Y < 2.6 and (int(P[0] + P[2]) % 6) < 2:
            return (CROCHET, 6)                                               # little white windmills/stars
        return (TIN_B, 4 if not old else 2)

    def lid(ctx):
        if ctx.face != 'up':
            return side(ctx)
        P = tp(ctx)
        d = math.hypot(ctx.pos[0] - 8.0, ctx.pos[2] - 8.0)
        if old and vn(P[0] / 2.0, P[2] / 2.0, 0.2, 712) > 0.45:
            return (RUST, 3 + (hh(*P) > 0.6))
        if d > 5.0:
            return (GOLD, 5)
        if d < 3.2:
            u, v = ctx.pos[0] - 8.0, ctx.pos[2] - 8.0
            if math.hypot(u, v) < 2.9 and math.hypot(u, v) > 2.4:
                return (PORC, 7)                                              # the plate
            for (cx, cz) in ((-1.0, -0.8), (1.0, -0.6), (0.0, 1.0), (-0.9, 0.9), (1.1, 0.9)):
                if math.hypot(u - cx, v - cz) < 0.75:
                    return (CARTON, 6 if hh(ctx.i, ctx.j) > 0.3 else 4)       # butter cookies
            return (PORC, 6)
        return (TIN_B, 5)
    mS = fin(side, dust=0.5)
    mL = fin(lid, dust=0.6)
    P = []
    if state == 'cerrada':
        P += rbox((3.4, y, 3.4), (12.6, y + 3.4, 12.6), mS, r=1.6)
        P += rbox((3.2, y + 3.4, 3.2), (12.8, y + 4.2, 12.8), mL, r=1.7)
        return P
    P += rbox((3.4, y, 3.4), (12.6, y + 3.4, 12.6), mS, r=1.6)
    P += [box((4.4, y + 0.6, 4.4), (11.6, y + 3.0, 11.6), fin(lambda c: (TIN_B, 2) if not old else (RUST, 2), ao=0.6, dust=0),
              faces=('up',))]
    if old:
        P += [box((4.6, y + 0.6, 4.6), (11.4, y + 1.4, 11.4), fin(lambda c: (BARK, 2 + (hh(c.i, c.j) > 0.5)), ao=0.4), faces=('up',))]
        lidp = rbox((12.0, y, 2.0), (16.0, y + 0.8, 11.6), mL, r=1.0)
        return P + lidp
    sp = lambda col: fin(lambda c, col=col: (col, 4 + (c.j % 2)) if c.face not in ('up', 'down') else (PINO, 6), ao=0.3)
    P += [box((5.0, y + 1.4, 5.0), (6.6, y + 3.6, 6.6), sp(REDP)), box((6.8, y + 1.4, 5.2), (8.4, y + 3.4, 6.8), sp(WOOL_R)),
          box((5.2, y + 1.4, 7.4), (6.8, y + 3.2, 9.0), sp(LINEN))]
    P += ball_parts(9.6, y + 2.6, 7.0, 1.2, fin(lambda c: (REDP, 5 + (c.i % 3 == 0)), ao=0.2))
    P += [box((9.0, y + 3.0, 6.6), (9.2, y + 5.2, 6.8), M_CHROME, rot=('z', 22.5, (9.1, y + 3.0, 6.7))),
          box((10.0, y + 3.0, 7.2), (10.2, y + 4.8, 7.4), M_CHROME, rot=('x', 22.5, (10.1, y + 3.0, 7.3)))]
    for n, (bx, bz, col) in enumerate(((7.6, 9.4, CELESTE), (9.0, 10.2, YELLOWP), (10.6, 9.6, LINEN), (6.4, 10.4, BAKE))):
        P.append(box((bx - 0.5, y + 1.4, bz - 0.5), (bx + 0.5, y + 1.7, bz + 0.5), fin(flat(col, 4), ao=0)))
    cv = photo_canvas('nelida')
    P.append(box((7.4, y + 3.1, 8.6), (10.0, y + 3.1, 12.5), fin(canvas_tone(cv, face='up'), ao=0, dust=0), faces=('up',),
                 rot=('y', 22.5, (8.7, y + 3.1, 10.5))))
    P += rbox((-1.0, y, 3.0), (3.2, y + 0.8, 12.6), mL, r=1.0)[:1]
    return P


def pantuflas_parts():
    """The Nona's felt slippers, bordo with a pompom, side by side and a little askew."""
    mF = fin(fuzz(pal('#1a0608', '#2e0a0e', '#461016', '#5e1820', '#76222a', '#8e3036'), base=4, seed=721), dust=0.3)
    mS = fin(flat(BAKE, 3), ao=0)
    P = []
    for (x, z, r) in ((4.0, 5.0, 0), (9.0, 6.0, 22.5)):
        rot = ('y', r, (x + 1.6, 0, z + 3.0)) if r else None
        kw = {'rot': rot} if rot else {}
        P += [box((x, 0.0, z), (x + 3.2, 0.5, z + 6.4), mS, **kw), box((x, 0.5, z + 2.6), (x + 3.2, 1.4, z + 6.4), mF, **kw),
              box((x, 0.5, z), (x + 3.2, 2.0, z + 2.6), mF, **kw),
              box((x + 0.9, 1.6, z + 0.2), (x + 2.3, 2.8, z + 1.6), fin(fuzz(PINK, base=6, seed=722), ao=0), **kw)]
    return P


# ------------------------------------------------------------------------------------------------ living extras
def mesita_auxiliar_parts():
    """Small lustred side table (top at 12/16, plain so a doily / vase / phone prop can go on top) with a lower shelf."""
    wd = lambda sd, **kw: lustre(CAOBA, seed=731 + sd, worn_pal=RAW, **kw)
    mL = fin(outline(wd(0, base=3, axis=1)))
    P = rbox((2.4, 11.2, 2.4), (13.6, 12.0, 13.6), fin(wd(1, base=4, axis=0, boards=(2, 12))), r=2.0)
    P += [box((3.6, 3.0, 3.6), (12.4, 3.6, 12.4), fin(wd(2, base=4, axis=0)))]
    for (x, z) in ((3.4, 3.4), (11.4, 3.4), (3.4, 11.4), (11.4, 11.4)):
        P += turned_leg(x, z, 0.0, 11.2, mL, w=1.2, rings=(0.45,))
    return P


def telefono_parts():
    """Beige 80s push-button phone ('sobre mesa') with the curly cord; the wall cable hangs cut ('nos cortaron el
    telefono en marzo')."""
    y = -4.0
    mB = fin(smooth(pal('#4a4236', '#6a604e', '#8a7e66', '#a69a80', '#bcb096', '#cec4aa', '#ddd5be'), base=4, seed=741), dust=0.6)

    def keys(ctx):
        if ctx.face == 'up' and 0.15 < ctx.s < 0.85 and ctx.t > 0.3:
            if ctx.i % 3 != 0 and ctx.j % 3 != 0:
                return (PLAST_W, 6)
            return (BAKE, 3)
        return smooth(pal('#4a4236', '#6a604e', '#8a7e66', '#a69a80', '#bcb096', '#cec4aa', '#ddd5be'), base=4, seed=742)(ctx)
    P = [box((4.0, y, 5.0), (12.0, y + 1.6, 12.0), mB),
         box((4.4, y + 1.6, 6.6), (11.6, y + 2.6, 11.6), fin(keys, dust=0.6), rot=('x', -22.5, (8.0, y + 1.6, 11.6))),
         box((4.2, y + 2.4, 3.8), (11.8, y + 3.6, 6.0), mB),                                    # handset
         box((3.8, y + 2.0, 3.6), (5.4, y + 3.8, 6.2), mB), box((10.6, y + 2.0, 3.6), (12.2, y + 3.8, 6.2), mB)]
    mCord = fin(lambda c: (pal('#4a4236', '#6a604e', '#8a7e66'), 1 + (c.j % 2)), ao=0)
    P += [box((3.2, y, 4.6), (4.0, y + 0.6, 9.0), mCord), box((12.0, y, 9.0), (14.6, y + 0.4, 9.4), fin(flat(BAKE, 4), ao=0)),
          box((14.6, y - 3.6, 9.0), (15.0, y + 0.4, 9.4), fin(flat(BAKE, 4), ao=0)),
          box((14.5, y - 3.8, 8.9), (15.1, y - 3.6, 9.5), fin(flat(NICKEL, 6), ao=0))]          # cut copper ends
    return P


# ============================================================================================ register: bathroom + nona + lights
F('inodoro', 'Inodoro con funda de chenille', 'Toilet with a chenille lid cover', inodoro_parts(), sound='ceramic')
F('bidet', 'Bidet', 'Bidet', bidet_parts(), sound='ceramic')
F('lavatorio', 'Lavatorio de pie', 'Pedestal washbasin', lavatorio_parts(), sound='ceramic')
F('botiquin', 'Botiquín con espejo', 'Mirrored medicine cabinet', botiquin_parts(), env=('wall',), collision='none', sound='glass')
F('botiquin_rajado', 'Botiquín con espejo rajado', 'Mirrored medicine cabinet (cracked)', botiquin_parts(True), env=('wall',),
  collision='none', sound='glass')
F('aplique_bano', 'Aplique del baño (encendido)', 'Bathroom wall light (lit)', aplique_parts(True), env=('wall',), light=11,
  collision='none', sound='glass')
F('aplique_bano_apagado', 'Aplique del baño (apagado)', 'Bathroom wall light (off)', aplique_parts(False), env=('wall',),
  collision='none', sound='glass')
F('banadera_izq', 'Bañadera (izquierda, canillas)', 'Bathtub (left, taps)', banadera_parts('izq'), sound='ceramic')
F('banadera_der', 'Bañadera (derecha)', 'Bathtub (right)', banadera_parts('der'), sound='ceramic')
F('cortina_ducha', 'Cortina de la ducha', 'Shower curtain', cortina_ducha_parts('cerrada'), env=(), render='translucent',
  collision='none', sound='cloth')
F('cortina_ducha_silueta', 'Cortina de la ducha (alguien detrás)', 'Shower curtain (someone behind it)',
  cortina_ducha_parts('silueta'), env=(), render='translucent', collision='none', sound='cloth')
F('cortina_ducha_corrida', 'Cortina de la ducha (corrida)', 'Shower curtain (drawn aside)', cortina_ducha_parts('corrida'),
  env=(), render='translucent', collision='none', sound='cloth')
F('ducha', 'Flor de la ducha', 'Shower head', ducha_parts(), env=('wall',), collision='none', sound='metal')
F('toallero', 'Toallero con toallas', 'Towel rail with towels', toallero_parts(), env=('wall',), collision='none', sound='cloth')
F('portarrollo', 'Portarrollos', 'Toilet roll holder', portarrollo_parts(), env=('wall',), collision='none', sound='metal')
F('alfombra_bano', 'Alfombra de baño de chenille', 'Chenille bath mat', alfombra_bano_parts(), collision='none', sound='wool')

F('cama_nona_cabecera', 'Cama de la Nona (cabecera)', "Nona's bed (head)", cama_nona_parts('cabecera'), sound='wool')
F('cama_nona_pie', 'Cama de la Nona (pie)', "Nona's bed (foot)", cama_nona_parts('pie'), sound='wool')
F('altar', 'Altar de la Nona (velas encendidas)', "Nona's home altar (candles lit)", altar_parts(True), light=12)
F('altar_apagado', 'Altar de la Nona (velas apagadas)', "Nona's home altar (candles out)", altar_parts(False))
F('altar_estampitas', 'Estampitas y crucifijo (sobre el altar)', 'Holy cards and crucifix (above the altar)', estampitas_parts(),
  env=('wall',), collision='none', sound='paper')
F('canasta_lana', 'Canasta de lana roja con agujas', 'Basket of red wool with knitting needles', canasta_lana_parts(), sound='wool')
F('andador', 'Andador de la Nona (la rueda que chilla)', "Nona's walker (the squeaky wheel)", andador_parts(), sound='metal')
F('ropero_abajo', 'Ropero lustrado (abajo)', 'Lustred wardrobe (bottom)', ropero_parts('abajo'))
F('ropero_arriba', 'Ropero lustrado (arriba)', 'Lustred wardrobe (top)', ropero_parts('arriba'), env=())
F('mesa_luz', 'Mesa de luz', 'Nightstand', mesa_luz_parts())
F('mesa_luz_nona', 'Mesa de luz de la Nona (radio y dentadura)', "Nona's nightstand (radio and dentures)", mesa_luz_parts('nona'))
F('velador', 'Velador (sobre mesa, encendido)', 'Bedside lamp (on a table, lit)', velador_parts(True), light=10,
  collision='none', directional=False)
F('velador_apagado', 'Velador (sobre mesa, apagado)', 'Bedside lamp (on a table, off)', velador_parts(False), collision='none',
  directional=False)
F('plafon', 'Plafón de vidrio (encendido)', 'Glass ceiling light (lit)', plafon_parts('on'), env=('ceil',), light=13,
  collision='none', directional=False, sound='glass')
F('plafon_apagado', 'Plafón de vidrio (apagado)', 'Glass ceiling light (off)', plafon_parts('off'), env=('ceil',),
  collision='none', directional=False, sound='glass')
F('plafon_roto', 'Plafón reventado', 'Burst ceiling light', plafon_parts('roto'), env=('ceil',), collision='none',
  directional=False, sound='glass')
F('lata_galletitas', 'Lata "Galletitas" (sobre mesa)', '"Galletitas" cookie tin (on a table)', lata_parts('cerrada'),
  collision='none', sound='metal')
F('lata_galletitas_abierta', 'Lata "Galletitas" abierta: hilos, agujas y la foto', 'Open cookie tin: thread, needles and the photo',
  lata_parts('abierta'), collision='none', sound='metal')
F('pantuflas', 'Pantuflas de la Nona', "Nona's slippers", pantuflas_parts(), collision='none', sound='wool')
F('mesita_auxiliar', 'Mesita auxiliar', 'Side table', mesita_auxiliar_parts())
F('telefono', 'Teléfono cortado (sobre mesa)', 'Disconnected phone (on a table)', telefono_parts(), collision='none',
  sound='stone')


# ============================================================================================ LUCIA'S ROOM
LACA = pal('#5a5450', '#7a746c', '#9a948a', '#b8b2a6', '#cfcabe', '#e0dcd2', '#ece9e1', '#f5f3ee', '#fbfaf7')   # white lacquer
LILA = pal('#2a1c3a', '#3e2a54', '#56396e', '#6e4c88', '#8a64a2', '#a682bc', '#c2a4d2', '#dcc8e6')
BLOND = pal('#4a3410', '#6e4e18', '#93702a', '#b8923e', '#d4b05a', '#e8cc80', '#f4e2a8')
GINGER = pal('#3a1206', '#5a1e0a', '#7e2e10', '#a24218', '#c25a24', '#d87a3c')


def tulle(p=PINK, base=6, seed=0):
    """Sheer tulle (cutout): a regular net of holes so the bed shows through, gathered folds."""
    def t(ctx):
        i, j = ctx.i, ctx.j
        if (i + j) % 2 == 1 and (j % 4) != 0:
            return None
        P = tp(ctx)
        u = P[0] if ctx.face in ('north', 'south') else P[2]
        f = math.sin(u * 1.1 + 0.8 * math.sin(u * 0.3))
        return T(p, base + (1 if f > 0.5 else (-1 if f < -0.5 else 0)))
    return t


def hearts_quilt(seed=0, off=(0, 0, 0)):
    """Lucia's pink duvet: quilted squares with little white hearts and stars."""
    def t(ctx):
        u, v = uv2(ctx, off)
        if ctx.face in ('up', 'down'):
            x, y, z = tp(ctx, off)
            u, v = x, z
        cu, cv_ = math.floor(u / 8), math.floor(v / 8)
        lu, lv = u - cu * 8, v - cv_ * 8
        k = 5
        if lu < 1 or lv < 1:
            return (PINK, 4)                                                   # quilting seams
        if (cu + cv_) % 2:
            k = 6
            hx_, hy_ = lu - 4.5, lv - 4.0
            if (hy_ < 0 and (math.hypot(hx_ - 1.0, hy_) < 1.3 or math.hypot(hx_ + 1.0, hy_) < 1.3)) or \
                    (hy_ >= 0 and abs(hx_) < 2.2 - hy_ * 0.9):
                return (CROCHET, 7)                                            # heart
        elif 3.5 < lu < 5.5 and 3.5 < lv < 5.5 and (int(lu) + int(lv)) % 2 == 0:
            return (YELLOWP, 7)                                                # star
        return (PINK, k)
    return t


def cama_dosel_parts(piece):
    """Lucia's canopy bed: white lacquered posts and frame, pink canopy with a scalloped valance, sheer pink tulle tied
    to the posts, heart duvet, a plush bunny. 'cabecera' (headboard against the wall opposite to facing) + 'pie'."""
    head = piece == 'cabecera'
    mW = fin(outline(smooth(LACA, base=6, seed=751, grime=0.2)), dust=0.5)
    mP = fin(smooth(PINK, base=5, seed=752, grime=0.0), dust=0.6)
    mT = fin(tulle(PINK, base=6, seed=753), ao=0, dust=0)
    mQ = fin(hearts_quilt(754, off=(0, 0, 0 if head else -16)), ao=0.6, dust=0.2)
    zp = 14.4 if head else 0.2                                                  # posts at the back (head) / front (foot)
    P = []
    for x0 in (0.4, 14.2):
        P.append(box((x0, 0.0, zp), (x0 + 1.4, 30.0, zp + 1.4), mW))
        P.append(box((x0 - 0.2, 30.0, zp - 0.2), (x0 + 1.6, 30.8, zp + 1.6), mW))           # post cap
        P.append(box((x0 + 0.3, 3.6, 0.0 if head else 1.6), (x0 + 1.1, 5.4, 14.4 if head else 16.0), mW))   # side rails
        P.append(box((x0 + 0.3, 28.4, 0.0 if head else 1.6), (x0 + 1.1, 29.2, 14.4 if head else 16.0), mW))  # canopy rails
    P.append(box((1.8, 28.4, zp + 0.3), (14.2, 29.2, zp + 1.1), mW))
    P.append(box((0.0, 29.2, 0.0 if head else 0.2), (16.0, 29.6, 16.0 if head else 15.8), mP))   # canopy fabric
    sc = lambda c: None if c.j > c.h - 1 - abs(((c.i / 3.0) % 1.0) - 0.5) * 4 else (PINK, 6 - (c.j == 0))
    for x in (-0.05, 16.05):
        P.append(box((x, 26.6, 0.0 if head else 0.2), (x, 29.6, 16.0 if head else 15.8), fin(sc, ao=0, dust=0), faces=('west', 'east')))
    if not head:
        P.append(box((0.0, 26.6, 0.15), (16.0, 29.6, 0.15), fin(sc, ao=0, dust=0), faces=('north', 'south')))
    if head:
        def hb(ctx):
            if ctx.face in ('north', 'south'):
                dx, dy = ctx.pos[0] - 8.0, ctx.pos[1] - 15.0
                if (dy > 0 and (math.hypot(dx - 1.6, dy - 0.0) < 1.9 or math.hypot(dx + 1.6, dy) < 1.9)) or (dy <= 0 and abs(dx) < 3.4 + dy * 1.0):
                    return (PINK, 5)                                           # painted heart
            return smooth(LACA, base=6, seed=755, grime=0.2)(ctx)
        P.append(box((1.8, 4.0, 14.7), (14.2, 19.0, 15.5), fin(hb, dust=0.5)))
        P.append(box((1.8, 19.0, 14.7), (14.2, 20.0, 15.5), mW))
    z0, z1 = (0.0, 14.4) if head else (1.6, 16.0)
    P.append(box((1.6, 5.4, z0), (14.4, 8.6, z1), fin(lambda c: (LINEN, 6), ao=0.8)))
    if head:
        P += [box((0.4, 8.6, 0.0), (15.6, 9.4, 9.0), mQ), box((0.4, 4.4, 0.0), (0.8, 8.6, 9.0), mQ), box((15.2, 4.4, 0.0), (15.6, 8.6, 9.0), mQ),
              box((0.4, 9.4, 7.6), (15.6, 9.8, 9.6), fin(cloth(LINEN, base=7, seed=756, folds=0.3, stains=0.05), ao=0.4))]
        P += rbox((2.4, 8.6, 10.0), (13.6, 11.2, 14.0), fin(cloth(PINK, base=7, seed=757, folds=0.5, fold_px=3.0, stains=0.05), ao=0.6), r=0.8)
        mB = fin(fuzz(LINEN, base=6, seed=758), dust=0.1)
        P += [box((9.6, 9.4, 9.8), (12.4, 12.2, 11.8), mB), box((10.0, 12.2, 10.0), (12.0, 14.2, 11.8), mB),
              box((10.2, 14.2, 10.6), (10.8, 17.2, 11.2), mB), box((11.2, 14.2, 10.6), (11.8, 17.0, 11.2), mB),
              box((10.6, 13.0, 9.9), (10.9, 13.3, 10.0), fin(flat(BAKE, 1), ao=0)), box((11.2, 13.0, 9.9), (11.5, 13.3, 10.0), fin(flat(BAKE, 1), ao=0)),
              box((10.8, 12.5, 9.9), (11.2, 12.8, 10.0), fin(flat(PINK, 4), ao=0))]               # plush bunny
    else:
        P += [box((0.4, 8.6, 1.6), (15.6, 9.4, 16.0), mQ), box((0.4, 4.4, 1.6), (0.8, 8.6, 16.0), mQ), box((15.2, 4.4, 1.6), (15.6, 8.6, 16.0), mQ),
              box((1.8, 4.0, 0.5), (14.2, 12.0, 1.3), mW)]                                          # low footboard
    # tulle draped at the posts, gathered with a pink bow at mid height
    for x0 in (0.4, 14.2):
        xa = x0 - 0.6 if x0 < 8 else x0 + 1.4
        za = zp if not head else zp - 2.4
        P += [box((xa, 4.0, za), (xa + 0.6, 29.0, za + 3.6), mT, faces=('north', 'south', 'west', 'east')),
              box((xa - 0.2, 15.0, za + 0.6), (xa + 0.8, 16.2, za + 3.0), mP)]
    return P


def doll_parts(cx, y0, zc, hair=HAIR, dress=PINK, bow=REDP, seed=0, s=0.9, cracked=False, dangle=False):
    """Sitting porcelain doll (front faces north): legs straight out toward z-, dress, lace collar, porcelain face with
    glass eyes, curls and a bow. zc = z of the front of her lap."""
    def face(ctx):
        if ctx.face != 'north':
            return (PORCELAIN, 5)
        i, j, w, h = ctx.i, ctx.j, ctx.w, ctx.h
        ey = int(h * 0.42)
        if j == ey and i in (1, w - 2):
            return hx('#2a3a6a') if hh(seed, i) > 0.3 else hx('#3a2a1a')            # glass eyes
        if j == ey - 1 and i in (1, w - 2):
            return (HAIR, 2)                                                    # lashes
        if j == ey + 1 and i in (0, w - 1):
            return (PINK, 5)                                                    # rosy cheeks
        if j == h - 2 and i in (w // 2 - 1, w // 2) and w > 3:
            return hx('#a01820')                                                # little red mouth
        if cracked and abs(i - j * 0.6 - 1) < 0.6 and j < h - 1:
            return (PORCELAIN, 1)
        return (PORCELAIN, 6 if 0 < i < w - 1 else 5)

    def dress_t(ctx):
        P = tp(ctx)
        k = 5 + ((int(P[0]) + int(P[1])) % 3 == 0)
        if ctx.face != 'up' and ctx.edge() == 0 and ctx.j == ctx.h - 1:
            return (LINEN, 7)                                                   # lace hem
        return (dress, k - (ctx.edge() == 0))
    mF = fin(face, ao=0, dust=0.4)
    mD = fin(dress_t, ao=0.4, dust=0.6)
    mH = fin(lambda c: (hair, 3 + ((c.i + c.j * 2) % 3 == 0) - (c.edge() == 0)), ao=0.4, dust=0.6)
    mL = fin(lambda c: (LINEN, 7) if c.face != 'down' else (LINEN, 5), ao=0.3, dust=0.4)
    mS = fin(flat(BAKE, 3), ao=0, dust=0.3)
    mSk = fin(flat(PORCELAIN, 6), ao=0.2, dust=0.3)
    q = lambda v: v * s
    P = [box((cx - q(2.2), y0, zc), (cx + q(2.2), y0 + q(2.2), zc + q(3.0)), mD),                  # skirt
         box((cx - q(1.4), y0 + q(2.2), zc + q(0.6)), (cx + q(1.4), y0 + q(4.4), zc + q(2.4)), mD),   # bodice
         box((cx - q(1.5), y0 + q(4.0), zc + q(0.5)), (cx + q(1.5), y0 + q(4.5), zc + q(2.5)), mL)]   # lace collar
    for sx in (-1, 1):
        x0 = cx + sx * q(0.85)
        if dangle:                                                              # sitting on the edge, legs hanging
            P += [box((x0 - q(0.45), y0, zc - q(1.6)), (x0 + q(0.45), y0 + q(0.9), zc), mL),
                  box((x0 - q(0.45), y0 - q(2.4), zc - q(2.5)), (x0 + q(0.45), y0 + q(0.9), zc - q(1.6)), mL),
                  box((x0 - q(0.5), y0 - q(3.0), zc - q(2.9)), (x0 + q(0.5), y0 - q(2.4), zc - q(1.5)), mS)]
        else:
            P += [box((x0 - q(0.45), y0, zc - q(2.6)), (x0 + q(0.45), y0 + q(0.9), zc), mL),              # stockings
                  box((x0 - q(0.5), y0, zc - q(3.2)), (x0 + q(0.5), y0 + q(1.2), zc - q(2.6)), mS)]        # shoes
        xa = cx + sx * q(1.7)
        P += [box((xa - q(0.35), y0 + q(2.4), zc + q(0.9)), (xa + q(0.35), y0 + q(4.2), zc + q(1.9)), mD),
              box((xa - q(0.3), y0 + q(1.8), zc + q(1.0)), (xa + q(0.3), y0 + q(2.4), zc + q(1.8)), mSk)]
    P += [box((cx - q(1.3), y0 + q(4.5), zc + q(0.4)), (cx + q(1.3), y0 + q(7.1), zc + q(2.6)), mF),   # head
          box((cx - q(1.5), y0 + q(3.8), zc + q(1.8)), (cx + q(1.5), y0 + q(7.5), zc + q(3.0)), mH),   # hair back
          box((cx - q(1.5), y0 + q(7.1), zc + q(0.2)), (cx + q(1.5), y0 + q(7.7), zc + q(3.0)), mH),   # hair top + fringe
          box((cx - q(1.7), y0 + q(3.6), zc + q(0.6)), (cx - q(1.3), y0 + q(7.3), zc + q(2.8)), mH),   # curls
          box((cx + q(1.3), y0 + q(3.6), zc + q(0.6)), (cx + q(1.7), y0 + q(7.3), zc + q(2.8)), mH),
          box((cx - q(1.1), y0 + q(7.7), zc + q(1.0)), (cx + q(1.1), y0 + q(8.5), zc + q(1.8)), fin(flat(bow, 5), ao=0.2, dust=0.4))]
    return P


DOLLS = [  # (hair, dress, bow)
    (BLOND, CELESTE, PINK), (HAIR, REDP, LINEN), (GINGER, LEAF, YELLOWP), (HAIR, LILA, PINK), (BLOND, PINK, CELESTE),
    (HAIR, LINEN, REDP), (GINGER, NAVY, LINEN), (BLOND, YELLOWP, REDP), (HAIR, PINK, LILA), (BLOND, LILA, LINEN)]


def dust_outline(x, y, z0, z1, w=4.0):
    """The clean, dust-free silhouette left where a doll used to sit (on a dusty shelf)."""
    def t(ctx):
        d = abs(ctx.pos[0] - x)
        if d < w / 2 and z0 < ctx.pos[2] < z1:
            return (LACA, 8)
        return None
    return [plane((x - w / 2 - 0.2, y + 0.02, z0), (x + w / 2 + 0.2, y + 0.02, z1), fin(t, ao=0, dust=0), faces=('up',))]


def estante_munecas_parts(n):
    """Lucia's white bookcase (1 block, 1.9 m): books and a music box at the bottom, porcelain dolls sitting on the
    middle and top shelves. n = 1 (4 dolls) | 2 (3 dolls + music box) | 3 (3 dolls + the dust-free spot where Ofelia
    sat) | 0 (empty: only the clean silhouettes in the dust). 1+2+3 = the 10 dolls. Back to the wall."""
    mW = fin(outline(smooth(LACA, base=6, seed=761, grime=0.2)), dust=1.4)
    mB = fin(smooth(PINK, base=5, seed=762, grime=0.0), dust=0.4)
    P = [box((0.2, 0.0, 7.4), (1.4, 31.0, 16.0), mW), box((14.6, 0.0, 7.4), (15.8, 31.0, 16.0), mW),
         box((1.4, 0.0, 15.2), (14.6, 31.0, 16.0), mB),
         box((1.4, 0.0, 7.8), (14.6, 1.2, 15.2), mW)]
    for y in (10.4, 20.4, 30.0):
        P.append(box((1.4, y, 7.8), (14.6, y + 1.0, 15.2), mW))
        P.append(box((1.4, y + 0.1, 7.6), (14.6, y + 0.9, 7.8), fin(smooth(PINK, base=4, seed=764 + int(y)), ao=0.2)))   # pink edge band
    P.append(box((0.0, 31.0, 7.2), (16.0, 31.8, 16.0), mW))
    P.append(box((0.2, 0.0, 7.2), (15.8, 0.4, 7.4), fin(smooth(PINK, base=4, seed=763), ao=0.3)))
    # bottom shelf: books
    x = 1.8
    for k in range(7 if n != 2 else 4):
        w = 0.9 + hh(n, k, 1) * 0.8
        hgt = 6.0 + hh(n, k, 2) * 2.6
        col = (PINK, LILA, CELESTE, YELLOWP, REDP, LEAF, ROSA_CH)[int(hh(n, k, 3) * 7)]
        P.append(box((x, 1.2, 9.4), (x + w, 1.2 + hgt, 15.0), fin(lambda c, col=col: (col, 4 + (c.j % 5 == 1)) if c.face in ('north', 'up', 'south')
                                                                  else (PAPER, 6), ao=0.4, dust=0.8)))
        x += w + 0.05
    if n == 2:
        mBox = fin(lambda c: (PINK, 6) if c.face != 'north' or (c.j > 1 and 1 < c.i < c.w - 2) else (GOLD, 5), ao=0.4, dust=0.6)
        P += [box((9.0, 1.2, 8.4), (14.0, 4.6, 13.0), mBox), box((8.8, 4.6, 8.2), (14.2, 5.4, 13.2), mBox),
              box((10.8, 5.4, 10.0), (12.2, 7.6, 11.4), fin(flat(LINEN, 7), ao=0))]               # music box + ballerina
    idx = {1: [0, 1, 2, 3], 2: [4, 5, 6], 3: [7, 8, 9], 0: []}[n]
    spots = {1: [(4.6, 11.4), (11.4, 11.4), (4.6, 21.4), (11.4, 21.4)], 2: [(4.6, 11.4), (11.4, 11.4), (8.0, 21.4)],
             3: [(11.4, 11.4), (4.6, 21.4), (11.4, 21.4)], 0: []}[n]
    for d, (cx, y0) in zip(idx, spots):
        hair, dress, bow = DOLLS[d]
        P += doll_parts(cx, y0, 9.2, hair, dress, bow, seed=d, s=0.86, cracked=(d == 5), dangle=True)
    if n == 3:
        P += dust_outline(4.6, 11.4, 8.0, 12.0)
    if n == 0:
        for (cx, y0) in ((4.6, 11.4), (11.4, 11.4), (4.6, 21.4), (11.4, 21.4)):
            P += dust_outline(cx, y0, 8.0, 12.0)
    return P


def tablet_canvas(on=True):
    """16x11 tablet screen: Tomi's VOD (facecam with an RGB headset, chat column, red EN VIVO tag)."""
    if not on:
        cv = Canvas(16, 11, hx('#0c0e12'))
        for y in range(11):
            for x in range(16):
                if 3 <= x + y * 0.6 <= 5:
                    cv.set(x, y, hx('#262a30'))
        return cv
    cv = Canvas(16, 11, hx('#1a1028'))
    for y in range(11):
        for x in range(11):
            cv.set(x, y, mix(hx('#3a2050'), hx('#10182a'), y / 11.0))
    for y in range(11):
        for x in range(11, 16):
            cv.set(x, y, hx('#e8e8f0') if y % 2 == 0 and x < 15 - (y * 7) % 3 else hx('#202030'))
    cv.ascii(2, 2, ['.hhhh.', 'hhhhhh', 'gssssg', 'gesseg', '.ssss.', '.smms.', 'HHHHHH', 'HHHHHH', 'HHHHHH'],
             {'h': hx('#2a1a10'), 's': hx('#e0b090'), 'e': hx('#141414'), 'g': hx('#40ff90'), 'm': hx('#a03030'), 'H': hx('#303040')})
    cv.rect(0, 0, 4, 2, hx('#e02030'))
    cv.set(1, 0, hx('#ffffff'))
    return cv


def escritorio_lucia_parts(on):
    """Lucia's small white desk (top at 11/16): the tablet on its stand playing Tomi's VOD (screen glows), crayons,
    a drawing, a pink pencil cup."""
    mW = fin(outline(smooth(LACA, base=6, seed=771, grime=0.25)), dust=0.6)
    P = [box((1.0, 10.2, 3.0), (15.0, 11.0, 14.6), fin(smooth(LACA, base=7, seed=772, grime=0.0), dust=0.6)),
         box((1.4, 0.0, 3.4), (2.6, 10.2, 4.6), mW), box((13.4, 0.0, 3.4), (14.6, 10.2, 4.6), mW),
         box((1.4, 0.0, 13.0), (2.6, 10.2, 14.2), mW), box((13.4, 0.0, 13.0), (14.6, 10.2, 14.2), mW),
         box((2.6, 7.6, 3.6), (13.4, 10.2, 4.0), fin(panels(smooth(PINK, base=5, seed=773), rects=((1, 1, -1, -1),), faces=('north',), bevel=0))),
         box((7.4, 8.6, 3.2), (8.6, 9.2, 3.6), fin(flat(LINEN, 7), ao=0))]
    cv = tablet_canvas(on)
    mScr = fin(canvas_tone(cv, other=lambda c: (GRAPH, 2)), ao=0, dust=0 if on else 0.4)
    rot = ('x', 22.5, (8.0, 11.0, 10.4))
    P += [box((3.6, 11.0, 10.0), (12.4, 17.0, 10.6), fin(smooth(PINK, base=4, seed=774)), rot=rot),     # case
          box((4.0, 11.4, 9.98), (12.0, 16.6, 10.0), mScr, faces=('north',), rot=rot, shade=not on),
          box((5.6, 11.0, 10.6), (10.4, 11.4, 12.4), fin(smooth(PINK, base=4, seed=775)))]               # stand
    P += [box((2.0, 11.0, 4.0), (6.4, 11.1, 9.0), fin(canvas_tone(fridge_drawing_canvas(), face='up'), ao=0, dust=0), faces=('up',),
              rot=('y', -22.5, (4.2, 11.0, 6.5)))]
    for n, col in enumerate((REDP, CELESTE, YELLOWP, LEAF, LILA)):
        P.append(box((9.0 + n * 0.7, 11.0, 5.0 + (n % 2) * 0.6), (9.4 + n * 0.7, 11.4, 7.6 + (n % 2) * 0.6), fin(flat(col, 5), ao=0)))
    P += rbox((12.6, 11.0, 4.6), (14.4, 13.6, 6.4), fin(smooth(PINK, base=5, seed=776)), r=0.4)
    for n, col in enumerate((REDP, LEAF, CELESTE)):
        P.append(box((12.9 + n * 0.4, 13.6, 5.0 + n * 0.3), (13.2 + n * 0.4, 15.6 - n * 0.4, 5.3 + n * 0.3), fin(flat(col, 4), ao=0)))
    return P


def silla_nena_parts():
    """Small pink child's chair with a heart cut-out in the back (sitter looks north)."""
    mW = fin(outline(smooth(PINK, base=5, seed=781, grime=0.2)), dust=0.5)

    def back(ctx):
        if ctx.face in ('north', 'south'):
            dx, dy = ctx.pos[0] - 8.0, ctx.pos[1] - 14.6
            if (dy > 0 and (math.hypot(dx - 0.9, dy) < 1.0 or math.hypot(dx + 0.9, dy) < 1.0)) or (dy <= 0 and abs(dx) < 1.9 + dy * 1.1):
                return None
        return smooth(PINK, base=5, seed=782)(ctx)
    P = []
    for (x, z) in ((3.6, 3.6), (11.2, 3.6), (3.6, 11.2), (11.2, 11.2)):
        P.append(box((x, 0.0, z), (x + 1.2, 6.0, z + 1.2), mW))
    P += [box((3.2, 6.0, 3.2), (12.8, 7.0, 12.8), fin(smooth(LACA, base=7, seed=783), dust=0.4)),
          box((3.6, 7.0, 11.4), (12.4, 17.0, 12.4), fin(back, dust=0.4))]
    return P


def notebook_canvas():
    """32x22 open notebook spread: lined pages, crayon block letters MI AMIGO / SE LLAMA / LEMAZA, a tall black figure."""
    cv = Canvas(32, 22, hx('#f2efe6'))
    for y in range(22):
        for x in range(32):
            c = hx('#f4f1e8')
            if y % 3 == 2:
                c = hx('#b8c8dc')
            if x in (15, 16):
                c = hx('#c8c2b4')
            cv.set(x, y, c)
    for y in range(22):
        cv.set(2, y, hx('#e0a0a0'))
        cv.set(18, y, hx('#e0a0a0'))
    cv.text(F35, 'MI AMIGO', 1, 1, hx('#2a3ab0'), sp=1, jitter=0.6, seed=3)
    cv.text(F35, 'SE LLAMA', 0, 8, hx('#2a3ab0'), sp=1, jitter=0.6, seed=4)
    cv.text(F35, 'LEMAZA', 4, 15, hx('#c01818'), sp=1, jitter=0.6, seed=5)
    cv.text(F35, 'LEMAZA', 5, 15, hx('#c01818'), sp=1, jitter=0.6, seed=5)
    cv.ascii(28, 9, ['.#.', '###', '.#.', '.#.', '###', '#.#', '#.#', '#.#', '#.#', '#.#', '#.#', '#.#'],
             {'#': hx('#101010')})
    cv.set(28, 9, hx('#e02020'))
    cv.set(30, 9, hx('#e02020'))
    return cv


def cuaderno_parts():
    """Lucia's notebook lying open on the floor: 'MI AMIGO SE LLAMA LEMAZA' in crayon across the spread."""
    cv = notebook_canvas()
    mP = fin(canvas_tone(cv, face='up', other=lambda c: (PAPER, 7)), ao=0, dust=0)
    mC = fin(lambda c: (REDP, 4) if c.face != 'up' else (REDP, 5), ao=0.3)
    P = [box((0.4, 0.0, 3.0), (15.6, 0.3, 13.6), mC),
         box((0.8, 0.3, 3.4), (15.2, 0.6, 13.2), mP)]
    P += [box((12.0, 0.6, 12.4), (15.4, 1.0, 13.0), fin(flat(REDP, 5), ao=0), rot=('y', 22.5, (13.7, 0.6, 12.7))),
          box((1.2, 0.0, 14.0), (5.0, 0.6, 14.6), fin(flat(GRAPH, 3), ao=0), rot=('y', -22.5, (3.1, 0.0, 14.3)))]
    return P


def dibujo_pared_parts():
    """Crayon drawing straight on the wall at child height: the family holding hands, the dog, and next to Lucia a
    very tall black figure with red eyes; 'LEMAZA' written over and over."""
    cv = Canvas(32, 32, None)
    cr = {'r': hx('#c82020'), 'b': hx('#2848c0'), 'y': hx('#e0b818'), 'g': hx('#2a9a3a'), 'k': hx('#121212'),
          'p': hx('#e070b0'), 'n': hx('#8a4a24'), 'R': hx('#ff2020')}
    cv.ascii(1, 14, ['..y.....r......p...........', '.yyy...rrr....ppp..........', '..y.....r......p...........',
                     '.yyyy.rrrrr..ppppp.........', '..y.....r......p...........', '.y.y...r.r....p.p..........',
                     '.y.y...r.r....p.p..........'], cr)
    cv.ascii(21, 3, ['.kkk.', 'kRkRk', '.kkk.', '..k..', 'kkkkk', 'k.k.k', 'k.k.k', '..k..', '..k..', '..k..', '.k.k.',
                     '.k.k.', 'k...k', 'k...k', 'k...k', 'k...k', 'k...k', 'k...k'], cr)
    cv.ascii(3, 23, ['nnnnn..', 'n...nn.', 'nnnnn..', 'n.n.n..'], cr)
    cv.text(F35, 'LEMAZA', 1, 1, cr['k'], sp=1, jitter=0.6, seed=8)
    cv.text(F35, 'LEMAZA', 2, 7, cr['r'], sp=1, jitter=0.8, seed=9)
    cv.line(3, 28, 30, 27, cr['g'])
    m = fin(lambda c: cv.get(c.i, c.j) if cv.get(c.i, c.j) is not None else None, ao=0, dust=0)
    return [box((0.0, 0.0, 15.96), (16.0, 16.0, 15.96), m, faces=('north',))]


def alfombra_redonda_parts():
    """Quarter of Lucia's round pink shag rug (the centre is at the block's back-right corner): place four of them in a
    2x2 square, each one turned toward its own corner (north, east, south, west)."""
    def t(ctx):
        d = math.hypot(ctx.pos[0] - 16.0, ctx.pos[2] - 16.0)
        if d > 15.6:
            return None
        P = tp(ctx)
        if d > 14.2:
            k, p = 4, LILA
        elif 11.0 < d < 12.4:
            k, p = 7, PINK
        elif d < 5.0:
            a = math.atan2(ctx.pos[2] - 16.0, ctx.pos[0] - 16.0)
            petal = abs(math.cos(a * 2)) * 4.2
            k, p = (6, CROCHET) if d < petal else (5, PINK)
            if d < 1.3:
                k, p = 5, YELLOWP
        else:
            k, p = 5, PINK
        v = hh(int(P[0]), int(P[2]), 791)
        k += -1 if v < 0.25 else (1 if v > 0.88 else 0)
        if ctx.face in ('north', 'south', 'west', 'east'):
            k -= 1
        return (p, k)
    m = fin(t, ao=0, dust=0.3)
    return [box((0.4, 0.0, 0.4), (16.0, 0.5, 16.0), m)]


def baul_juguetes_parts():
    """Painted toy chest (lid open against the wall): pastel planks with ABC blocks painted on, a teddy's head, a ball
    and a doll's leg poking out."""
    def body(ctx):
        P = tp(ctx)
        if ctx.face == 'north' and 0.25 < ctx.t < 0.75:
            col = int(ctx.s * 3)
            if 0.08 < (ctx.s * 3) % 1.0 < 0.92:
                letter = 'ABC'[min(2, col)]
                pts = set(draw_text(F35, letter, int(col * ctx.w / 3 + ctx.w / 6 - 1), int(ctx.h * 0.3), sp=1))
                if (ctx.i, ctx.j) in pts:
                    return (LINEN, 7)
                return ((REDP, CELESTE, YELLOWP)[min(2, col)], 5)
        k = 5 + (1 if int(P[1]) % 6 == 0 else 0)
        return (LILA, k) if ctx.face != 'up' else (LILA, 3)
    mB = fin(body, dust=0.4)
    mL = fin(lambda c: (LILA, 5 if c.face == 'north' else 4), dust=0.5)
    P = [box((1.6, 0.0, 3.0), (14.4, 8.4, 13.0), mB),
         box((2.2, 7.8, 3.6), (13.8, 8.0, 12.4), fin(flat(BAKE, 2), ao=0), faces=('up',)),
         box((1.4, 8.4, 13.0), (14.6, 18.4, 14.0), mL)]                                     # open lid leaning back
    mT = fin(fuzz(CARTON, base=5, seed=792), dust=0.2)
    P += ball_parts(5.4, 9.4, 7.0, 2.2, mT) + [box((3.6, 10.8, 6.2), (4.6, 12.0, 7.2), mT), box((6.2, 10.8, 6.2), (7.2, 12.0, 7.2), mT),
                                            box((4.6, 9.4, 4.7), (5.0, 9.8, 4.8), fin(flat(BAKE, 1), ao=0)), box((5.8, 9.4, 4.7), (6.2, 9.8, 4.8), fin(flat(BAKE, 1), ao=0))]
    P += ball_parts(10.8, 9.2, 9.0, 1.8, fin(lambda c: (REDP, 5) if (int(c.pos[1] * 2) % 3) else (LINEN, 7), ao=0.2))
    P += [box((8.6, 7.6, 5.6), (9.6, 13.0, 6.6), fin(flat(PORCELAIN, 6), ao=0.2), rot=('z', -22.5, (9.1, 7.6, 6.1))),
          box((8.5, 12.6, 5.5), (9.7, 13.8, 6.9), fin(flat(BAKE, 3), ao=0), rot=('z', -22.5, (9.1, 7.6, 6.1)))]
    return P


def lampara_hongo_parts(lit):
    """Mushroom night light ('sobre mesa'): red cap with white dots glowing, white stem. Lit / off."""
    y = -4.0

    def cap(ctx):
        P = tp(ctx)
        dot = (int(P[0]) * 3 + int(P[2]) * 5 + int(P[1])) % 7 == 0
        if lit:
            return (OPAL_LIT, 7) if dot else (pal('#5a1010', '#8a2020', '#c03a30', '#e86048', '#ff8a6a', '#ffb090'), 4 + (ctx.face == 'up'))
        return (LINEN, 7) if dot else (REDP, 4 + (ctx.face == 'up'))
    m = fin(cap, ao=0, dust=0 if lit else 0.4)
    P = rbox((6.4, y, 6.4), (9.6, y + 3.6, 9.6), fin(lambda c: (OPAL_LIT, 6) if lit else (LINEN, 6), ao=0.2), r=0.6, shade=not lit)
    P += rbox((4.0, y + 3.6, 4.0), (12.0, y + 5.6, 12.0), m, r=1.8, shade=not lit)
    P += rbox((5.4, y + 5.6, 5.4), (10.6, y + 6.6, 10.6), m, r=1.4, shade=not lit)
    return P


# ============================================================================================ TOTI'S ROOM
GAMER_R = pal('#1a0406', '#2e070a', '#4a0c10', '#6a1218', '#8e1a20', '#b02428', '#d0383a')
RGB = [hx('#ff2a6a'), hx('#ff8a1a'), hx('#ffe02a'), hx('#2aff7a'), hx('#2ad0ff'), hx('#7a4aff'), hx('#ff2aff')]


def silla_gamer_parts():
    """Black and red gamer chair on a five-star base, headrest pillow, torn faux leather on the seat edge. The sitter
    looks toward 'facing'."""
    def lea(p_, sd):
        def t(ctx):
            P = tp(ctx)
            k = 3 + (1 if hh(int(P[0]), int(P[1]), int(P[2]), sd) < 0.1 else 0)
            if ctx.face != 'up' and ctx.edge() == 0:
                k -= 1
            if ctx.face == 'north' and ctx.pos[1] < 9.0 and ctx.pos[0] < 7.0 and vn(P[0] / 1.5, P[1] / 1.5, 0.3, sd) > 0.6:
                return (CROCHET, 4)                                                    # torn, foam showing
            return (p_, k)
        return t
    mB = fin(lea(BLACKP, 801), dust=0.3)
    mR = fin(lea(GAMER_R, 802), dust=0.3)
    mBase = fin(smooth(GRAPH, base=3, seed=803, grime=0.0), dust=0.6)
    P = [box((7.2, 0.0, 7.2), (8.8, 1.2, 8.8), mBase), box((7.4, 1.2, 7.4), (8.6, 6.0, 8.6), M_CHROME)]
    for (dx, dz) in ((0, -1), (0.95, -0.31), (0.59, 0.81), (-0.59, 0.81), (-0.95, -0.31)):
        x, z = 8.0 + dx * 5.4, 8.0 + dz * 5.4
        P += [box((min(8.0, x) - 0.5, 0.8, min(8.0, z) - 0.5), (max(8.0, x) + 0.5, 1.6, max(8.0, z) + 0.5), mBase),
              box((x - 0.7, 0.0, z - 0.7), (x + 0.7, 0.8, z + 0.7), fin(flat(BLACKP, 2), ao=0))]
    P += [box((2.6, 6.0, 2.4), (13.4, 8.6, 12.6), mB), box((2.4, 6.2, 2.4), (4.0, 9.6, 12.6), mR), box((12.0, 6.2, 2.4), (13.6, 9.6, 12.6), mR),
          box((3.0, 8.6, 11.8), (13.0, 26.0, 13.8), mB),
          box((2.6, 8.6, 11.6), (4.4, 25.0, 14.0), mR), box((11.6, 8.6, 11.6), (13.4, 25.0, 14.0), mR),
          box((5.6, 21.4, 10.8), (10.4, 24.0, 11.8), mR),                                   # headrest pillow
          box((5.4, 13.0, 10.8), (10.6, 17.0, 11.8), mB),                                   # lumbar pillow
          box((6.2, 26.0, 12.0), (9.8, 27.0, 13.6), mB)]
    for x in (1.2, 13.8):
        P += [box((x + 0.2, 6.2, 6.0), (x + 0.8, 12.0, 7.0), mBase), box((x - 0.2, 12.0, 4.0), (x + 1.2, 12.8, 10.0), fin(lea(BLACKP, 804)))]
    return P


def monitor_canvas(on):
    """26x15 game frame: night neon city, an FPS rifle, HUD (minimap, health, kill feed, crosshair)."""
    if not on:
        cv = Canvas(26, 15, hx('#08090c'))
        for y in range(15):
            for x in range(26):
                if 5 <= x + y * 0.7 <= 8:
                    cv.set(x, y, hx('#1a1e24'))
        return cv
    cv = Canvas(26, 15, hx('#1a0a30'))
    for y in range(15):
        for x in range(26):
            c = mix(hx('#3a1a6a'), hx('#0a1430'), y / 9.0)
            if y > 8:
                c = mix(hx('#1a1a2a'), hx('#0a0a10'), (y - 8) / 7.0)
            cv.set(x, y, c)
    for n, (x0, w, hgt) in enumerate(((0, 4, 6), (5, 3, 8), (9, 5, 5), (15, 3, 9), (19, 4, 7), (23, 3, 5))):
        for y in range(9 - hgt, 9):
            for x in range(x0, x0 + w):
                c = hx('#141428')
                if (x + y) % 3 == 0 and y % 2 == 0:
                    c = RGB[(n + y) % len(RGB)]
                cv.set(x, y, c)
    cv.poly([(15, 15), (20, 10), (26, 9), (26, 15)], hx('#202024'))
    cv.line(17, 13, 24, 10, hx('#4a4a54'))
    cv.ellipse(3, 2.5, 2.4, 2.0, hx('#2a5a3a'))
    cv.set(3, 2, hx('#ff3030'))
    cv.rect(1, 13, 8, 14, hx('#30e060'))
    cv.rect(20, 1, 25, 2, hx('#e8e8e8'))
    cv.rect(20, 3, 24, 4, hx('#ff5050'))
    cv.set(13, 7, hx('#ffffff'))
    cv.set(12, 7, hx('#ffffff'))
    cv.set(14, 7, hx('#ffffff'))
    cv.set(13, 6, hx('#ffffff'))
    cv.set(13, 8, hx('#ffffff'))
    return cv


def rgb_tone(on, seed=0, base=BLACKP, k=3):
    """RGB strip: a running rainbow of LEDs when on, dark diodes when off."""
    def t(ctx):
        if not on:
            return (base, k - (ctx.i % 2))
        P = tp(ctx)
        n = int(P[0] + P[1] + P[2] + seed) // 2
        return RGB[n % len(RGB)]
    return t


def escritorio_pc_parts(side, on):
    """Toti's black melamine gaming desk, 2 blocks along x (top at 12/16): '_izq' (viewer's left) has the monitor,
    the RGB keyboard and the headset stand; '_der' the glass-side PC tower with RGB fans, the mouse on the big mouse
    pad, energy-drink cans and a cup of instant noodles. Lit (on) / off pairs."""
    izq = side == 'izq'
    mT = fin(smooth(MELA_WG, base=3, seed=811, grime=0.0), dust=0.6)
    mL = fin(smooth(BLACKP, base=3, seed=812, grime=0.2), dust=0.6)
    P = [box((0.0, 11.0, 2.0), (16.0, 12.0, 15.6), mT)]
    if izq:
        P += [box((14.0, 0.0, 2.4), (15.6, 11.0, 15.2), mL)]
    else:
        P += [box((0.4, 0.0, 2.4), (2.0, 11.0, 15.2), mL)]
    P += [box((0.0, 10.4, 15.0), (16.0, 11.0, 15.6), fin(rgb_tone(on, 3), ao=0, dust=0), shade=not on)]           # LED strip under the top edge (back)
    pad = fin(lambda c: (BLACKP, 2) if c.edge() > 0 else (RGB[(c.i // 2) % len(RGB)] if on else (BLACKP, 4)), ao=0, dust=0.2)
    P.append(box((0.0 if not izq else 4.0, 12.0, 3.0), (12.0 if not izq else 16.0, 12.15, 9.6), pad))
    if izq:
        cv = monitor_canvas(on)
        mS = fin(canvas_tone(cv, other=lambda c: (BLACKP, 2)), ao=0, dust=0 if on else 0.5)
        P += [box((5.2, 12.0, 11.0), (10.8, 12.5, 14.0), mL), box((7.4, 12.5, 12.4), (8.6, 17.0, 13.4), mL),
              box((1.2, 16.0, 11.2), (14.8, 24.4, 12.4), mL),
              box((1.6, 16.4, 11.18), (14.4, 24.0, 11.2), mS, faces=('north',), shade=not on),
              box((1.6, 15.6, 11.4), (14.4, 16.0, 12.2), fin(rgb_tone(on, 1), ao=0, dust=0), shade=not on)]
        kb = fin(lambda c: (RGB[(c.i // 2 + c.j) % len(RGB)] if on else (BLACKP, 5)) if (c.face == 'up' and c.i % 2 == 0 and c.j % 2 == 0)
                 else (BLACKP, 2), ao=0.2, dust=0.2)
        P += [box((3.6, 12.15, 4.2), (13.0, 12.9, 7.6), kb)]
        P += [box((0.8, 12.0, 11.6), (2.8, 12.4, 13.6), mL), box((1.6, 12.4, 12.4), (2.0, 17.6, 12.8), mL),
              box((0.6, 17.6, 11.8), (3.0, 18.4, 13.2), mL),
              box((0.4, 14.0, 11.6), (1.0, 18.0, 13.4), fin(lambda c: RGB[0] if on else (GRAPH, 3), ao=0), shade=not on),
              box((2.6, 14.0, 11.6), (3.2, 18.0, 13.4), fin(lambda c: RGB[4] if on else (GRAPH, 3), ao=0), shade=not on)]   # RGB headset
    else:
        def tower(ctx):
            if ctx.face in ('east', 'north') and 0 < ctx.i < ctx.w - 1 and 0 < ctx.j < ctx.h - 1:
                fans = ((0.5, 0.25), (0.5, 0.62)) if ctx.face == 'north' else ((0.3, 0.3), (0.3, 0.7))
                for (cz, cy) in fans:
                    d = math.hypot(ctx.s - cz, (ctx.t - cy) * (1.4 if ctx.face == 'east' else 0.9))
                    if 0.1 < d < 0.2:
                        return RGB[int(math.atan2(ctx.t - cy, ctx.s - cz) * 2 + 4) % len(RGB)] if on else (GRAPH, 4)
                    if d <= 0.1:
                        return (GRAPH, 3)
                if ctx.face == 'north':
                    return (BLACKP, 2 + (ctx.i + ctx.j) % 2)                       # mesh front
                if ctx.t > 0.85:
                    return (GRAPH, 3)
                return mix(hx('#1a1030'), hx('#3a1a6a'), ctx.t) if on else (GRAPH, 2 + (ctx.i + ctx.j) % 2)
            if ctx.face == 'up' and ctx.j % 2 == 0 and 1 < ctx.i < ctx.w - 2:
                return (BLACKP, 1)
            return (BLACKP, 3)
        P += [box((1.0, 12.6, 4.0), (7.0, 26.0, 14.0), fin(tower, ao=0.2, dust=0.4), shade=not on),
              box((0.8, 12.0, 3.8), (7.2, 12.6, 14.2), mL)]
        P += [box((12.6, 12.15, 5.0), (14.2, 12.9, 7.4), fin(lambda c: RGB[2] if (on and c.face == 'up' and c.j == 1) else (BLACKP, 3), ao=0.2))]   # mouse
        for n, (x, z) in enumerate(((8.4, 11.6), (10.0, 12.8), (8.0, 4.0))):
            col = (LEAF, CELESTE, REDP)[n]
            P.append(box((x, 12.0, z), (x + 1.2, 14.6 - (n == 2) * 2.0, z + 1.2), fin(lambda c, col=col: (NICKEL, 6) if c.face == 'up' else (col, 4 + (c.i == 1)), ao=0.2)))
        P += rbox((11.4, 12.0, 10.6), (14.2, 14.6, 12.8), fin(lambda c: (PLAST_W, 7) if c.face != 'up' else (CARTON, 6), ao=0.2), r=0.5)   # noodles
    return P


def cama_toti_parts(piece):
    """Toti's unmade bed: cheap black metal frame, grey sheets kicked into a heap, the navy duvet half on the floor,
    a hoodie and a phone charger cable. 'cabecera' / 'pie' as every bed in the kit."""
    head = piece == 'cabecera'
    mF = fin(iron(GRAPH, base=3, seed=821, rust=0.1), dust=0.4)
    mS = fin(cloth(pal('#2a2c30', '#3a3d42', '#4c5056', '#60646a', '#757980', '#8a8e94', '#9ea2a8'), base=4, seed=822, folds=0.9, fold_px=3.0, stains=0.3), ao=0.6)
    mD = fin(cloth(NAVY, base=4, seed=823, folds=0.8, fold_px=4.0, stains=0.1), ao=0.6, dust=0.1)
    P = []
    zp = (14.6, 15.6) if head else (0.4, 1.4)
    for x0 in (0.6, 14.4):
        P.append(box((x0, 0.0, zp[0]), (x0 + 1.0, 16.0 if head else 9.0, zp[1]), mF))
        P.append(box((x0, 4.0, 0.0 if head else zp[1]), (x0 + 1.0, 5.0, zp[0] if head else 16.0), mF))
    if head:
        for y in (10.0, 15.0):
            P.append(box((1.6, y, zp[0] + 0.2), (14.4, y + 1.0, zp[1] - 0.2), mF))
    P.append(box((1.6, 8.0, zp[0] + 0.2), (14.4, 9.0, zp[1] - 0.2), mF))
    z0, z1 = (0.0, 14.6) if head else (1.4, 16.0)
    P.append(box((1.6, 5.0, z0), (14.4, 8.0, z1), fin(lambda c: (LINEN, 5 if int(tp(c)[0]) % 5 else 4), ao=0.8)))
    if head:
        P += [box((2.6, 8.0, 10.6), (12.4, 10.2, 14.2), mS, rot=('y', 22.5, (7.5, 8.0, 12.4))),
              box((1.6, 8.0, 0.0), (11.0, 9.6, 7.0), mS), box((3.0, 9.6, 1.0), (9.0, 10.8, 5.6), mS),
              box((9.0, 8.0, 3.0), (14.0, 9.0, 9.0), fin(cloth(GAMER_R, base=4, seed=824, folds=0.7), ao=0.5))]   # hoodie
        P += [box((13.2, 8.0, 12.0), (14.0, 8.15, 14.0), fin(flat(BLACKP, 4), ao=0)), box((13.4, 8.0, 9.0), (13.6, 8.1, 12.0), fin(flat(PLAST_W, 6), ao=0))]
    else:
        P += [box((1.6, 8.0, 1.4), (14.4, 9.4, 12.0), mD), box((4.0, 9.4, 3.0), (13.0, 10.6, 9.0), mD),
              box((15.4, 0.0, 2.0), (16.0, 9.4, 14.0), mD, faces=('west', 'east', 'north', 'south')),
              box((16.0, 0.0, 2.0), (19.6, 0.8, 13.0), mD), box((14.4, 8.0, 2.0), (15.4, 9.4, 14.0), mD)]
    return P


def poster_canvas(kind):
    if kind == 'juego':
        cv = Canvas(28, 40, hx('#0a0a1a'))
        for y in range(40):
            for x in range(28):
                cv.set(x, y, mix(hx('#ff2a8a'), hx('#1a0a3a'), min(1.0, abs(y - 18) / 18.0)) if y < 30 else hx('#0a0a14'))
        cv.ellipse(14, 17, 8.5, 9.5, hx('#141418'))
        cv.rect(7, 14, 21, 19, hx('#2ad0ff'))
        cv.rect(8, 15, 20, 18, hx('#7aeaff'))
        cv.rect(5, 26, 23, 31, hx('#141418'))
        cv.text(F35, 'NEON', 7, 2, hx('#2affea'), sp=1)
        cv.text(F35, 'RAID', 8, 33, hx('#ff2a8a'), sp=1)
        return cv
    cv = Canvas(28, 40, hx('#e8e0c8'))
    for y in range(40):
        for x in range(28):
            cv.set(x, y, hx('#141414') if 8 <= y <= 36 else hx('#e83a1a'))
    cv.ellipse(14, 20, 6, 6.5, hx('#e8e4dc'))
    cv.rect(10, 25, 18, 29, hx('#e8e4dc'))
    cv.ellipse(11.5, 19.5, 1.6, 2.0, hx('#141414'))
    cv.ellipse(16.5, 19.5, 1.6, 2.0, hx('#141414'))
    for x in (11, 13, 15, 17):
        cv.set(x, 27, hx('#141414'))
    cv.line(4, 10, 8, 16, hx('#ffd02a'))
    cv.line(8, 16, 5, 17, hx('#ffd02a'))
    cv.line(5, 17, 9, 24, hx('#ffd02a'))
    cv.text(F57, 'FURIA', 1, 0, hx('#141414'), sp=1)
    cv.text(F35, 'EN VIVO', 1, 31, hx('#e83a1a'), sp=1)
    return cv


def poster_parts(kind):
    """Poster taped / pinned to the wall (1.4 m tall, place it at eye height)."""
    cv = poster_canvas(kind)

    def t(ctx):
        c = cv.get(int(ctx.s * cv.w), int(ctx.t * cv.h))
        if ctx.s > 0.9 and ctx.t < 0.08:
            return mix(c, hx('#f0e8d0'), 0.6)                                 # corner curling off
        if hh(ctx.i, ctx.j, 831) < 0.01:
            return mix(c, hx('#ffffff'), 0.4)
        return c
    P = [box((1.0, -2.0, 15.9), (15.0, 18.0, 15.9), fin(t, ao=0, dust=0.1), faces=('north',))]
    for (x, y) in ((1.2, 16.6), (13.6, 16.6), (1.2, -1.6), (13.6, -1.6)):
        P.append(box((x, y, 15.84), (x + 1.2, y + 1.0, 15.88), fin(lambda c: (LINEN, 7), ao=0), faces=('north',)))
    return P


# ------------------------------------------------------------------------------------------------ placard (Toti hides here)
def louvre_tone(bottom_half_j_offset=0, H=64, frame=PINO):
    """Louvred placard door (cutout: light leaks through the slats). Paints a 32-wide x H-tall door; ctx.j +
    offset = row from the top of the whole door."""
    def t(ctx, j_off=bottom_half_j_offset):
        i = ctx.i
        j = ctx.j + j_off
        w = 32
        if i < 3 or i > w - 4 or j < 3 or j > H - 4 or (H - 34 <= j <= H - 31) and H == 64:
            k = 6 if (i == 0 or j == 0) else (4 if (i == w - 1 or j == H - 1) else 5)
            if i in (25, 26, 27) and 30 <= j <= 33:
                return (BRASS, 6 if j == 30 else 4)                            # knob
            return (frame, k + (hh(i // 3, j // 7) > 0.8))
        r = (j - 3) % 3
        if r == 2:
            return None
        return (frame, 6 if r == 0 else 4)
    return t


def placard_door_tone(ctx):
    """Door painter for the real opening placard door (Door class: 32x32 'top' and 'bottom' halves)."""
    off = 0 if ctx.face == 'top' else 32
    c = louvre_tone(off)(ctx)
    if c is None:
        return None
    pl, k = c
    return T(pl, k)


def placard_fondo_parts(side):
    """Back of Toti's placard: it goes IN THE WALL SLOT behind each door column (full block = the wall), its front
    faces the room/door. Dark back board, chrome rail at 1.8 m with hoodies, shirts and a school uniform on hangers
    hanging forward into the door space, sneakers and a backpack on the floor. '_izq' / '_der' = viewer's left/right."""
    izq = side == 'izq'
    mBk = fin(lambda c: (MELA_WG, 3 + (hh(c.i // 3, c.j // 3) > 0.7)) if c.face == 'north' else (MELA_WG, 3), ao=0.2, dust=0.0)
    mWall = fin(lambda c: (MELA_WG, 3 + (hh(c.i // 3, c.j // 3) > 0.7)) if c.face == 'north' else (LACA, 5 + (hh(c.i, c.j, 3) > 0.8)), ao=0, dust=0)
    P = [box((0.0, 0.0, 0.0), (16.0, 16.0, 16.0), mWall),
         box((0.0, 16.0, -0.4), (16.0, 31.0, 0.0), mBk, faces=('north', 'down'))]
    mR = fin(brass(NICKEL, base=5, seed=841), dust=0.4)
    mSide = fin(lambda c: (MELA_W, 5 + (hh(c.i // 3, c.j // 5) > 0.8)) if c.face in ('west', 'east') else (MELA_W, 4), ao=0.3, dust=0.4)
    P += [box((15.38, 0.0, -15.98), (15.98, 31.6, -0.02), mSide) if izq else box((0.02, 0.0, -15.98), (0.62, 31.6, -0.02), mSide)]
    P += [box((0.0, 27.6, -7.4), (16.0, 28.2, -6.8), mR)]
    if izq:
        P.append(box((15.4, 26.6, -7.6), (16.0, 28.6, 0.0), mR))
    else:
        P.append(box((0.0, 26.6, -7.6), (0.6, 28.6, 0.0), mR))
    cols = [(GRAPH, 'buzo'), (GAMER_R, 'buzo'), (CELESTE, 'camisa'), (LINEN, 'camisa'), (NAVY, 'buzo'), (DENIM, 'jean')] if izq else \
        [(LINEN, 'camisa'), (GREENP, 'buzo'), (BLACKP, 'buzo'), (DENIM, 'jean'), (REDP, 'camisa')]
    x = 1.0
    for n, (col, kind) in enumerate(cols):
        w = 1.2 if kind != 'buzo' else 1.6
        top = 27.4
        bot = 14.0 if kind != 'jean' else 10.0
        m = fin(cloth(col, base=4, seed=842 + n, fold_axis='j', folds=0.5, stains=0.05), ao=0.6, dust=0.2)
        P += [box((x, bot, -12.6), (x + w, top - 1.0, -2.0), m),
              box((x + 0.1, top - 1.0, -11.0), (x + w - 0.1, top, -3.6), m),
              box((x + w / 2 - 0.15, top, -7.3), (x + w / 2 + 0.15, top + 0.8, -6.9), mR)]
        if kind == 'buzo':
            P.append(box((x - 0.2, bot + 2.0, -13.0), (x + w + 0.2, bot + 6.0, -12.4), m))
        x += w + 0.35
    if izq:
        mSh = fin(lambda c: (LINEN, 7) if c.pos[1] < 0.8 else (GAMER_R, 4 + (c.i % 4 == 0)), ao=0.3)
        P += [box((3.0, 0.0, -6.0), (5.4, 2.4, -1.0), mSh), box((5.8, 0.0, -6.4), (8.2, 2.4, -1.4), mSh)]
    else:
        P += rbox((5.0, 0.0, -6.0), (11.0, 8.0, -1.0), fin(cloth(NAVY, base=3, seed=849, folds=0.3), ao=0.5, dust=0.3), r=0.8)
        P.append(box((6.0, 3.0, -6.4), (10.0, 6.0, -6.0), fin(flat(GRAPH, 4), ao=0.3)))
    return P


def placard_maletero_parts(side):
    """Top row of the placard (maletero, y+2 over the doors): two small fixed louvred doors under a light-pine frame."""
    izq = side == 'izq'
    lt = louvre_tone(0, H=32)

    def t(ctx):
        q = _Q()
        q.i = int(ctx.s * 32) if izq else 31 - int(ctx.s * 32)
        q.j = int(ctx.t * 32)
        return lt(q)
    m = fin(t, ao=0.2, dust=0.5)
    P = [box((0.0, 0.0, 0.0), (16.0, 14.0, 1.0), m, faces=('north', 'south')),
         box((0.0, 14.0, 0.0), (16.0, 16.0, 1.2), fin(wood(PINO, base=5, seed=851, axis=0)))]
    P.append(box((0.0, 0.0, 1.0), (16.0, 16.0, 1.4), fin(flat(BAKE, 2), ao=0), faces=('north',)))
    return P


def placard_cerrado_parts(side):
    """A fixed (non-opening) louvred placard front, 2 m tall in one block, for the other bedrooms. '_izq' / '_der'
    (the knob is on the inner side of each leaf)."""
    izq = side == 'izq'
    lt = louvre_tone(0, H=64)

    def t(ctx):
        q = _Q()
        q.i = int(ctx.s * 32) if izq else 31 - int(ctx.s * 32)
        q.j = int(ctx.t * 64)
        return lt(q)
    m = fin(t, ao=0, dust=0.4)
    P = [box((0.0, 0.0, 0.2), (16.0, 31.0, 0.8), m, faces=('north',)),
         box((0.0, 0.0, 0.8), (16.0, 31.0, 1.2), fin(flat(BAKE, 2), ao=0), faces=('north',)),
         box((0.0, 31.0, 0.0), (16.0, 32.0, 1.4), fin(wood(PINO, base=5, seed=853, axis=0)))]
    return P


# ============================================================================================ MASTER BEDROOM
def quilt_flower(seed=0, off=(0, 0, 0)):
    """Quilted satin bedspread (acolchado): diamond quilting over a faded rose-and-beige print."""
    fl = floral(seed, off, fade=0.6)

    def t(ctx):
        u, v = uv2(ctx, off)
        if ctx.face in ('up', 'down'):
            x, y, z = tp(ctx, off)
            u, v = x, z
        a = (u + v) % 10.0
        b = (u - v) % 10.0
        pl, k = fl(ctx)
        if a < 1.0 or b < 1.0:
            k -= 1
        elif 4.0 < a < 6.0 and 4.0 < b < 6.0:
            k += 1
        if pl is FLORAL_BG:
            pl = QUILT
        return (pl, k)
    return t


def cama_matrimonial_parts(piece, side):
    """Marta and Jorge's double bed, 2x2 blocks: piece 'cabecera' / 'pie', side 'izq' / 'der' (viewer's left/right
    standing at the foot looking at the headboard; '_izq' is the +x block in authoring space). Lustred headboard with
    a buttoned bordo cuerina panel, quilted satin bedspread, two pillows; Marta's pink robe on her side ('izq'),
    Jorge's newspaper on his ('der')."""
    head = piece == 'cabecera'
    izq = side == 'izq'
    off = (16 if izq else 0, 0, 0 if head else -16)
    wd = lambda sd, **kw: lustre(CAOBA, seed=861 + sd, off=off, worn_pal=RAW, **kw)
    mP = fin(outline(wd(0, base=3, axis=1)))
    mR = fin(wd(1, base=4, axis=2))
    mQ = fin(quilt_flower(863, off=off), ao=0.6, dust=0.3)
    zp = (14.4, 16.0) if head else (0.0, 1.6)
    top = 24.0 if head else 13.0
    px0, px1 = (14.6, 16.0) if izq else (0.0, 1.4)                  # corner post on the outer side
    bx0, bx1 = (0.0, 14.6) if izq else (1.4, 16.0)                  # board between the posts
    P = [box((px0, 0.0, zp[0]), (px1, top, zp[1]), mP),
         box((px0 - 0.1, top, zp[0] - 0.1), (px1 + 0.1, top + 0.8, zp[1] + 0.1), mR),
         box((bx0, 4.0, zp[0] + 0.3), (bx1, top - 2.6, zp[1] - 0.3), fin(panels(wd(2, base=4, axis=0), rects=((2, 2, -2, -2),),
                                                                             faces=('north', 'south')))),
         box((bx0, top - 2.6, zp[0] + 0.1), (bx1, top - 1.6, zp[1] - 0.1), mR)]
    if head:
        cx0, cx1 = (0.0, 13.8) if izq else (2.2, 16.0)
        P.append(box((cx0, 9.0, zp[0] - 0.4), (cx1, 19.6, zp[0] + 0.3), fin(leatherette(REDP, base=3, seed=864, buttons=True))))
    rx0, rx1 = (14.8, 15.6) if izq else (0.4, 1.2)
    P.append(box((rx0, 3.6, 0.0 if head else 1.6), (rx1, 5.6, 14.4 if head else 16.0), mR))
    z0, z1 = (0.0, 14.4) if head else (1.6, 16.0)
    mx0, mx1 = (0.0, 14.8) if izq else (1.2, 16.0)
    P.append(box((mx0, 5.4, z0), (mx1, 8.8, z1), fin(lambda c: (LINEN, 5), ao=0.8)))
    qx0, qx1 = (0.0, 15.7) if izq else (0.3, 16.0)
    sx0, sx1 = (15.4, 15.7) if izq else (0.3, 0.6)                  # bedspread hanging down the outer side
    qz0, qz1 = (0.0, 9.6) if head else (1.6, 16.0)
    P += [box((qx0, 8.8, qz0), (qx1, 9.4, qz1), mQ), box((sx0, 4.4, qz0), (sx1, 8.8, qz1), mQ)]
    if head:
        P.append(box((qx0, 9.4, 8.0), (qx1, 10.4, 10.0), mQ))                                     # turned-over roll
        P += rbox((1.6 if izq else 2.4, 8.8, 10.4), (13.6 if izq else 14.4, 11.6, 14.2),
                  fin(cloth(LINEN, base=7, seed=865 + izq, folds=0.5, fold_px=3.0, stains=0.15), ao=0.6), r=0.9)
        if izq:
            mRobe = fin(fuzz(PINK, base=6, seed=867), dust=0.1)
            P += [box((3.0, 9.4, 2.0), (12.0, 10.4, 7.0), mRobe), box((6.0, 10.4, 3.0), (11.0, 11.0, 6.0), mRobe),
                  box((12.0, 9.4, 3.0), (13.0, 10.0, 9.0), mRobe, rot=('y', 22.5, (12.5, 9.4, 6.0)))]
        else:
            P += [box((4.0, 9.4, 2.0), (11.0, 9.7, 7.0), fin(lambda c: (PAPER, 7) if (c.j % 3) else (GRAPH, 5), ao=0.2), rot=('y', -22.5, (7.5, 9.4, 4.5)))]
    return P


def comoda_parts(side):
    """Lustred dresser 2 blocks wide (top at 13/16) with a tall bevelled mirror rising behind it: '_izq' has Marta's
    pink rollers, face cream and a jewellery box, '_der' a perfume tray, Jorge's watch and a framed photo."""
    izq = side == 'izq'
    off = (16, 0, 0) if izq else (0, 0, 0)
    wd = lambda sd, **kw: lustre(CAOBA, seed=871 + sd, off=off, worn_pal=RAW, **kw)
    mC = fin(wd(0, base=3, axis=1))
    mDr = fin(panels(wd(1, base=4, axis=0), rects=((1, 1, -1, -1),), faces=('north',), bevel=0))
    mTop = fin(wd(2, base=4, axis=0, boards=(2, 10)), dust=1.0)
    xe, xf = (0.0, 15.6) if izq else (0.4, 16.0)
    P = [box((xe + 0.4, 0.0, 4.0), (xf - 0.4, 1.6, 14.6), fin(wd(3, base=2, axis=0))),
         box((xe + 0.2, 1.6, 3.6), (xf - 0.2, 12.4, 15.0), mC),
         box((xe, 12.4, 3.0), (xf, 13.2, 15.4), mTop)]
    for n, (a, b) in enumerate(((2.0, 5.4), (5.6, 9.0), (9.2, 12.0))):
        P += [box((xe + 0.8, a, 3.2), (xf - 0.8, b, 3.6), mDr),
              box((7.4, (a + b) / 2 - 0.3, 2.8), (8.6, (a + b) / 2 + 0.3, 3.2), M_BRASS)]
    mF = fin(wd(4, base=3, axis=1))
    xm0, xm1 = (0.0, 14.0) if izq else (2.0, 16.0)
    P += [box((xm0, 13.2, 13.6), (xm1, 14.2, 15.0), mF), box((xm0, 30.4, 13.6), (xm1, 31.4, 15.0), mF)]
    P.append(box((xm1 - 1.0, 14.2, 13.6), (xm1, 30.4, 15.0), mF) if izq else box((xm0, 14.2, 13.6), (xm0 + 1.0, 30.4, 15.0), mF))
    P.append(box((xm0 + (0.0 if izq else 1.0), 14.2, 14.2), (xm1 - (1.0 if izq else 0.0), 30.4, 14.2),
                 fin(mirror_tone(seed=873 + izq, fog=0.2), ao=0, dust=0), faces=('north',)))
    if izq:
        for n, (x, z) in enumerate(((3.0, 6.0), (4.6, 6.4), (3.6, 7.8), (5.4, 8.0), (4.2, 9.4))):
            P.append(box((x, 13.2, z), (x + 1.2, 14.6, z + 1.2), fin(lambda c: (PINK, 5 + (c.j % 2)) if c.face != 'up' else (PINK, 3), ao=0.2)))
        P += rbox((8.0, 13.2, 5.0), (10.4, 14.8, 7.4), fin(lambda c: (PORC, 7) if c.face != 'up' else (CELESTE, 5), ao=0.2), r=0.5)
        P += [box((10.8, 13.2, 8.0), (14.2, 15.4, 11.0), fin(lambda c: (REDP, 4) if c.j > 1 else (GOLD, 5), ao=0.3)),
              box((10.6, 15.4, 7.8), (14.4, 16.0, 11.2), fin(flat(REDP, 5), ao=0.2))]
    else:
        P += [box((2.0, 13.2, 5.0), (8.0, 13.5, 9.0), M_CHROME)]
        for n, (x, col) in enumerate(((2.8, GOLD), (4.4, CELESTE), (6.0, PINK))):
            P += [box((x, 13.5, 6.0), (x + 1.2, 15.6 + n * 0.3, 7.2), fin(lambda c, col=col: (col, 5 + (c.i == 1)), ao=0.2)),
                  box((x + 0.3, 15.6 + n * 0.3, 6.3), (x + 0.9, 16.2 + n * 0.3, 6.9), fin(flat(GOLD, 6), ao=0))]
        P += [box((9.6, 13.2, 6.0), (12.0, 13.5, 7.0), fin(flat(GRAPH, 3), ao=0)), box((10.4, 13.2, 6.0), (11.2, 13.6, 7.0), M_CHROME)]
        P += [box((11.4, 13.2, 9.0), (14.6, 17.6, 10.0), fin(lambda c: (GOLD, 5) if (c.edge() == 0 or c.face != 'north') else
                                                         canvas_tone(photo_canvas('casamiento'))(c), ao=0.2), rot=('x', 22.5, (13.0, 13.2, 9.5)))]
    return P


def crucifijo_parts():
    """Wooden crucifix over the double bed with a sprig of dried olive (Domingo de Ramos) tucked behind it."""
    mW = fin(outline(lustre(NOGAL, seed=881, base=3)))
    P = [box((7.2, 2.0, 15.2), (8.8, 15.0, 16.0), mW), box((4.6, 10.0, 15.2), (11.4, 11.6, 16.0), mW),
         box((7.5, 5.0, 14.9), (8.5, 10.6, 15.2), fin(lambda c: (CROCHET, 6) if c.j > 0 else (GOLD, 5), ao=0)),
         box((5.6, 10.3, 14.9), (10.4, 10.9, 15.2), fin(flat(CROCHET, 6), ao=0)),
         box((7.4, 11.0, 14.9), (8.6, 12.2, 15.2), fin(flat(CROCHET, 6), ao=0)),
         box((7.0, 13.6, 14.9), (9.0, 14.6, 15.2), fin(flat(PAPER, 7), ao=0))]
    mO = fin(lambda c: (LEAF, 3 + (c.i % 2)), ao=0)
    P += [box((8.8, 11.0, 15.5), (9.2, 17.0, 15.7), mO, rot=('z', -22.5, (9.0, 11.0, 15.6))),
          box((9.2, 13.0, 15.5), (10.8, 13.8, 15.7), mO, rot=('z', -22.5, (9.0, 11.0, 15.6))),
          box((9.6, 15.0, 15.5), (11.0, 15.8, 15.7), mO, rot=('z', -22.5, (9.0, 11.0, 15.6)))]
    return P


def perchero_bata_parts():
    """Hook behind the door with Marta's fluffy pink robe and Jorge's black 'REY DEL ASADO' apron (wall piece, the
    hook at 1.8 m: place it in the block at y=1)."""
    mH = fin(brass(seed=891, base=4), dust=0.4)
    mRobe = fin(fuzz(PINK, base=6, seed=892), ao=0.5, dust=0.1)

    def apron(ctx):
        if ctx.face == 'north' and 0.2 < ctx.s < 0.8:
            pts = set(draw_text(F35, 'REY', int(ctx.w / 2) - 5, 3, sp=1))
            if (ctx.i, ctx.j) in pts:
                return (LINEN, 7)
            if 9 <= ctx.j <= 13 and abs(ctx.i - ctx.w / 2) < 3:
                return (LINEN, 7) if (ctx.i + ctx.j) % 3 else (BAKE, 1)      # cartoon cow
        return (BLACKP, 3 + (hh(ctx.i, ctx.j) > 0.8))
    P = [box((3.0, 12.0, 15.0), (13.0, 13.6, 16.0), fin(wood(NOGAL, base=4, seed=893, axis=0))),
         box((4.6, 11.4, 13.8), (5.4, 13.0, 15.0), mH), box((10.6, 11.4, 13.8), (11.4, 13.0, 15.0), mH)]
    P += [box((2.2, -8.0, 12.4), (8.2, 11.6, 14.8), mRobe), box((2.6, -9.0, 12.2), (7.8, -6.0, 14.6), mRobe),
          box((1.6, -2.0, 12.0), (2.4, 9.0, 14.4), mRobe), box((8.0, -2.0, 12.0), (8.8, 9.0, 14.4), mRobe),
          box((4.2, -4.0, 12.2), (6.2, 3.0, 12.4), fin(fuzz(PINK, base=4, seed=894), ao=0))]
    P += [box((9.0, -4.0, 13.4), (13.2, 11.0, 14.0), fin(apron, ao=0.4, dust=0.2)),
          box((10.4, 11.0, 13.4), (11.8, 11.6, 14.0), fin(flat(BLACKP, 3), ao=0))]
    return P


# ============================================================================================ everyday clutter
def zapatillas_parts():
    """Toti's beaten sneakers kicked off, one on its side."""
    def sn(col):
        def t(ctx):
            if ctx.pos[1] < 0.9:
                return (LINEN, 6 if ctx.face != 'down' else 4)
            if ctx.face == 'up' and ctx.i % 3 == 1 and ctx.t < 0.5:
                return (LINEN, 7)
            return (col, 4 + (ctx.edge() == 0))
        return fin(t, ao=0.3, dust=0.4)
    m = sn(GRAPH)
    P = [box((3.0, 0.0, 3.0), (6.0, 2.6, 10.4), m), box((3.2, 2.6, 7.0), (5.8, 3.6, 10.4), m),
         box((8.0, 0.0, 6.0), (11.0, 2.6, 13.4), m, rot=('y', 45, (9.5, 0, 9.7)))]
    return P


def ropa_tirada_parts():
    """A heap of worn clothes on the floor: jeans, a hoodie, socks."""
    P = [box((2.0, 0.0, 4.0), (12.0, 1.4, 12.0), fin(cloth(DENIM, base=4, seed=901, folds=0.9, fold_px=2.0), ao=0.5), rot=('y', 22.5, (7, 0, 8))),
         box((4.0, 1.4, 5.0), (11.0, 3.0, 10.0), fin(cloth(GAMER_R, base=4, seed=902, folds=0.9, fold_px=2.5), ao=0.5)),
         box((6.0, 3.0, 6.0), (9.6, 3.8, 9.0), fin(cloth(GRAPH, base=4, seed=903, folds=0.6), ao=0.4)),
         box((11.0, 0.0, 11.0), (14.0, 0.6, 12.4), fin(flat(LINEN, 6), ao=0.3)), box((12.0, 0.0, 3.0), (13.4, 0.6, 6.0), fin(flat(LINEN, 5), ao=0.3))]
    return P


def pelota_parts():
    """A scuffed leather football with black and white panels."""
    def t(ctx):
        P = tp(ctx)
        if (int(P[0] // 3) + int(P[1] // 3) + int(P[2] // 3)) % 3 == 0:
            return (BLACKP, 3)
        return (LINEN, 7 - (hh(int(P[0]), int(P[1]), int(P[2])) < 0.2))
    return ball_parts(8.0, 3.4, 8.0, 3.4, fin(t, ao=0.2, dust=0.4))


def cargador_parts():
    """A wall socket low on the wall with a phone charger plugged in and its white cable hanging to the floor."""
    mS = fin(smooth(PLAST_W, base=6, seed=911), dust=0.4)
    P = [box((5.4, 3.0, 15.4), (10.6, 8.0, 16.0), mS),
         box((6.6, 4.4, 15.2), (9.4, 6.6, 15.4), fin(lambda c: (BAKE, 2) if (c.face == 'north' and c.j == 2 and c.i in (1, 4)) else (PLAST_W, 5), ao=0)),
         box((6.8, 4.2, 13.2), (9.2, 6.8, 15.2), fin(lambda c: (PLAST_W, 7) if c.face != 'north' or c.j > 0 else (PLAST_W, 5), ao=0.2)),
         box((7.8, 0.0, 13.6), (8.2, 4.2, 14.0), fin(flat(PLAST_W, 6), ao=0)),
         box((7.8, 0.0, 9.0), (8.2, 0.3, 13.6), fin(flat(PLAST_W, 6), ao=0)),
         box((6.6, 0.0, 6.0), (9.4, 0.4, 9.0), fin(lambda c: (BLACKP, 2) if c.face == 'up' and c.edge() > 0 else (GRAPH, 4), ao=0.2))]   # phone
    return P


def mochila_parts():
    """Lucia's pink school backpack (with a keychain) slumped on the floor."""
    m = fin(cloth(PINK, base=5, seed=921, folds=0.4, stains=0.2), ao=0.5, dust=0.3)
    P = rbox((4.0, 0.0, 6.0), (12.0, 10.0, 11.0), m, r=1.2)
    P += [box((5.0, 1.0, 5.0), (11.0, 6.0, 6.0), fin(cloth(LILA, base=5, seed=922, folds=0.3), ao=0.4)),
          box((7.6, 6.0, 4.8), (8.4, 6.4, 5.0), fin(flat(NICKEL, 6), ao=0)),
          box((5.0, 3.0, 11.0), (6.2, 9.4, 11.8), m), box((9.8, 3.0, 11.0), (11.0, 9.4, 11.8), m),
          box((7.4, 3.6, 4.4), (8.6, 5.0, 4.8), fin(flat(YELLOWP, 6), ao=0))]
    return P


def juguetes_parts():
    """Toys on the floor: wooden blocks, a plastic horse, a crayon box."""
    P = []
    for n, (x, z, col) in enumerate(((3.0, 4.0, REDP), (5.4, 4.6, CELESTE), (4.0, 6.8, YELLOWP), (4.2, 5.0, LEAF))):
        y = 0.0 if n < 3 else 2.2
        P.append(box((x, y, z), (x + 2.2, y + 2.2, z + 2.2), fin(lambda c, col=col: (col, 5) if c.edge() > 0 else (col, 3), ao=0.3)))
    mH = fin(smooth(LILA, base=5, seed=931), ao=0.3, dust=0.3)
    P += [box((9.0, 2.0, 9.0), (13.0, 4.0, 10.6), mH), box((12.4, 3.4, 9.2), (13.8, 6.4, 10.4), mH), box((12.6, 5.8, 9.0), (15.0, 7.0, 10.6), mH)]
    for (x, z) in ((9.2, 9.0), (12.0, 9.0), (9.2, 9.8), (12.0, 9.8)):
        P.append(box((x, 0.0, z), (x + 0.8, 2.0, z + 0.8), mH))
    P += [box((3.0, 0.0, 11.0), (7.0, 1.2, 13.0), fin(lambda c: (YELLOWP, 5) if c.face != 'up' else (LEAF, 4), ao=0.3))]
    return P


# ============================================================================================ register: kids + master
F('cama_dosel_cabecera', 'Cama con dosel de Lucía (cabecera)', "Lucia's canopy bed (head)", cama_dosel_parts('cabecera'), sound='wool')
F('cama_dosel_pie', 'Cama con dosel de Lucía (pie)', "Lucia's canopy bed (foot)", cama_dosel_parts('pie'), sound='wool')
for _n, _es, _en in ((1, 'Estante con 4 muñecas de porcelana', 'Bookcase with 4 porcelain dolls'),
                     (2, 'Estante con 3 muñecas y la cajita de música', 'Bookcase with 3 dolls and the music box'),
                     (3, 'Estante con 3 muñecas (falta Ofelia)', 'Bookcase with 3 dolls (Ofelia missing)'),
                     (0, 'Estante de las muñecas vacío', 'Doll bookcase (empty)')):
    F('estante_munecas_' + (str(_n) if _n else 'vacio'), _es, _en, estante_munecas_parts(_n))
F('escritorio_lucia', 'Escritorio de Lucía (tablet prendida)', "Lucia's desk (tablet on)", escritorio_lucia_parts(True), light=4)
F('escritorio_lucia_apagada', 'Escritorio de Lucía (tablet apagada)', "Lucia's desk (tablet off)", escritorio_lucia_parts(False))
F('silla_nena', 'Sillita rosa', 'Pink child chair', silla_nena_parts())
F('cuaderno_lemaza', 'Cuaderno "MI AMIGO SE LLAMA LEMAZA"', 'Notebook "MY FRIEND IS CALLED LEMAZA"', cuaderno_parts(),
  collision='none', sound='paper')
F('dibujo_lemaza', 'Dibujo en la pared (LEMAZA)', 'Crayon drawing on the wall (LEMAZA)', dibujo_pared_parts(), env=('wall',),
  collision='none', sound='paper')
F('alfombra_lucia', 'Alfombra redonda rosa (cuarto, x4)', 'Round pink rug (quarter, x4)', alfombra_redonda_parts(), collision='none',
  sound='wool')
F('baul_juguetes', 'Baúl de juguetes', 'Toy chest', baul_juguetes_parts())
F('lampara_hongo', 'Lámpara hongo (sobre mesa, encendida)', 'Mushroom night light (on a table, lit)', lampara_hongo_parts(True),
  light=7, collision='none', directional=False)
F('lampara_hongo_apagada', 'Lámpara hongo (sobre mesa, apagada)', 'Mushroom night light (on a table, off)',
  lampara_hongo_parts(False), collision='none', directional=False)
F('silla_gamer', 'Silla gamer de Toti', "Toti's gamer chair", silla_gamer_parts(), sound='wool')
for _s in ('izq', 'der'):
    _w = 'izquierda' if _s == 'izq' else 'derecha'
    _e = 'left' if _s == 'izq' else 'right'
    F(f'escritorio_pc_{_s}', f'Escritorio gamer con PC RGB ({_w}, prendida)', f'Gaming desk with RGB PC ({_e}, on)',
      escritorio_pc_parts(_s, True), light=6)
    F(f'escritorio_pc_{_s}_apagado', f'Escritorio gamer con PC ({_w}, apagada)', f'Gaming desk with PC ({_e}, off)',
      escritorio_pc_parts(_s, False))
F('cama_toti_cabecera', 'Cama deshecha de Toti (cabecera)', "Toti's unmade bed (head)", cama_toti_parts('cabecera'), sound='wool')
F('cama_toti_pie', 'Cama deshecha de Toti (pie)', "Toti's unmade bed (foot)", cama_toti_parts('pie'), sound='wool')
F('poster_juego', 'Póster "NEON RAID"', '"NEON RAID" poster', poster_parts('juego'), env=('wall',), collision='none', sound='paper')
F('poster_banda', 'Póster de la banda "FURIA"', '"FURIA" band poster', poster_parts('banda'), env=('wall',), collision='none',
  sound='paper')
Door('casa_placard_puerta', 'Puerta del placard (persiana)', 'Louvred placard door', placard_door_tone, kit=KIT, sound='wood')
F('placard_fondo_izq', 'Fondo del placard con ropa colgada (izquierda)', 'Placard back with hanging clothes (left)',
  placard_fondo_parts('izq'), collision='full', env=())
F('placard_fondo_der', 'Fondo del placard con ropa colgada (derecha)', 'Placard back with hanging clothes (right)',
  placard_fondo_parts('der'), collision='full', env=())
F('placard_maletero_izq', 'Maletero del placard (izquierda)', 'Placard top cupboard (left)', placard_maletero_parts('izq'), env=())
F('placard_maletero_der', 'Maletero del placard (derecha)', 'Placard top cupboard (right)', placard_maletero_parts('der'), env=())
F('placard_cerrado_izq', 'Frente de placard fijo (izquierda)', 'Fixed placard front (left)', placard_cerrado_parts('izq'), env=())
F('placard_cerrado_der', 'Frente de placard fijo (derecha)', 'Fixed placard front (right)', placard_cerrado_parts('der'), env=())
for _p in ('cabecera', 'pie'):
    for _s in ('izq', 'der'):
        F(f'cama_matrimonial_{_p}_{_s}', f'Cama matrimonial ({_p}, {"izquierda" if _s == "izq" else "derecha"})',
          f'Double bed ({"head" if _p == "cabecera" else "foot"}, {"left" if _s == "izq" else "right"})',
          cama_matrimonial_parts(_p, _s), sound='wool')
F('comoda_izq', 'Cómoda con espejo (izquierda, ruleros)', 'Dresser with mirror (left, rollers)', comoda_parts('izq'))
F('comoda_der', 'Cómoda con espejo (derecha, perfumes)', 'Dresser with mirror (right, perfumes)', comoda_parts('der'))
F('crucifijo', 'Crucifijo con olivo', 'Crucifix with an olive sprig', crucifijo_parts(), env=('wall',), collision='none')
F('perchero_bata', 'Percha con la bata de Marta y el delantal de Jorge', "Hook with Marta's robe and Jorge's apron",
  perchero_bata_parts(), env=('wall',), collision='none', sound='cloth')
F('zapatillas', 'Zapatillas tiradas', 'Kicked-off sneakers', zapatillas_parts(), collision='none', sound='cloth')
F('ropa_tirada', 'Ropa tirada', 'Heap of clothes', ropa_tirada_parts(), collision='none', sound='cloth')
F('pelota', 'Pelota de fútbol', 'Football', pelota_parts(), collision='none', directional=False, sound='wool')
F('cargador', 'Cargador enchufado con el celular', 'Phone charging from a wall socket', cargador_parts(), env=('wall',),
  collision='none', sound='stone')
F('mochila', 'Mochila de Lucía', "Lucia's backpack", mochila_parts(), collision='none', sound='cloth')
F('juguetes', 'Juguetes en el piso', 'Toys on the floor', juguetes_parts(), collision='none')


# ============================================================================================ LAUNDRY (lavadero)
CHAPA = pal('#1e2224', '#2c3134', '#3c4246', '#4e5559', '#62696d', '#787f82', '#8f9598', '#a8adae')   # galvanised / grey steel
BAQUE = pal('#0e0806', '#1a100a', '#28180e', '#382214', '#4a2e1a', '#5e3c22')                        # bakelite


def tablero_parts(on):
    """The house's old breaker board on the laundry wall (place it at eye height): a wooden backboard, a grey steel
    box with porcelain fuses, the big knife-switch lever with a black bakelite handle (UP = on, DOWN = off: the outage
    gag), a hand-written 'LUZ' label taped above it and a paper sign with the electrician's number. Off: the lever is
    down and there is a fresh scorch mark."""
    mWd = fin(wood(PINO, base=3, seed=941, axis=0, boards=(1, 9)), dust=0.6)
    mBox = fin(painted(CHAPA, base=4, seed=942, chips=0.2, under=RUST, grime=0.0), dust=0.8)
    mP = fin(porcelain(PORC, base=6, seed=943, grime=0.0, streak=False), dust=0.6)
    mCu = fin(brass(BRASS, base=5, seed=944, tarnish=0.5), dust=0.3)
    mH = fin(smooth(BAQUE, base=3, seed=945, grime=0.0), dust=0.2)
    P = [box((0.6, 0.6, 15.2), (15.4, 15.4, 16.0), mWd),
         box((1.6, 1.6, 12.6), (14.4, 14.4, 15.2), mBox),
         box((2.0, 2.0, 12.4), (14.0, 14.0, 12.6), fin(lambda c: (CHAPA, 2) if c.edge() < 1 else (CHAPA, 3), ao=0), faces=('north',))]
    for n, x in enumerate((3.0, 5.2)):                                                      # porcelain fuses (tapones)
        for y in (10.0, 5.0):
            P += rbox((x, y, 11.0), (x + 1.6, y + 1.6, 12.4), mP, r=0.4)
            P.append(box((x + 0.5, y + 0.5, 10.9), (x + 1.1, y + 1.1, 11.0), fin(flat(BRASS, 4), ao=0), faces=('north',)))
    P += [box((8.6, 3.0, 11.8), (12.8, 3.8, 12.4), mP), box((8.6, 11.2, 11.8), (12.8, 12.0, 12.4), mP),   # switch base clips
          box((9.0, 2.8, 11.4), (9.6, 4.0, 12.0), mCu), box((11.8, 2.8, 11.4), (12.4, 4.0, 12.0), mCu),
          box((9.0, 11.0, 11.4), (9.6, 12.2, 12.0), mCu), box((11.8, 11.0, 11.4), (12.4, 12.2, 12.0), mCu)]
    if on:                                                                                  # knife switch closed (lever UP)
        P += [box((9.1, 3.4, 11.0), (9.5, 11.8, 11.4), mCu), box((11.9, 3.4, 11.0), (12.3, 11.8, 11.4), mCu),
              box((9.1, 11.2, 9.6), (12.3, 11.8, 11.4), mCu), box((9.6, 10.8, 7.4), (11.8, 12.4, 9.6), mH)]
    else:                                                                                   # pulled DOWN and open
        rot = ('x', 45, (10.7, 3.4, 11.2))
        P += [box((9.1, -5.0, 11.0), (9.5, 3.4, 11.4), mCu, rot=rot), box((11.9, -5.0, 11.0), (12.3, 3.4, 11.4), mCu, rot=rot),
              box((9.1, -5.0, 9.6), (12.3, -4.4, 11.4), mCu, rot=rot), box((9.6, -5.6, 7.4), (11.8, -4.0, 9.6), mH, rot=rot)]
        P.append(box((8.2, 11.0, 12.38), (13.2, 15.0, 12.4), fin(soot_stain_tone(946, 1.0), ao=0, dust=0), faces=('north',)))
    P.append(box((8.4, 12.8, 12.36), (13.0, 14.2, 12.38), fin(lambda c: INK if (c.i, c.j) in set(draw_text(F35, 'LUZ', 2, 0, sp=1))
                                                              else (PAPER, 7), ao=0, dust=0), faces=('north',)))
    P.append(box((2.4, 12.2, 12.36), (7.4, 14.0, 12.38), fin(lambda c: INK_RED if (c.i, c.j) in set(draw_text(F35, '911', 1, 0, sp=1)) else (CROCHET, 7),
                                                             ao=0, dust=0), faces=('north',)))
    P += cord_parts(2.4, 14.0, 14.4, 32.0, col=GRAPH, k=3)
    return P


def pileta_lavar_parts():
    """Laundry tub ('pileta de lavar') of cast granite on brick legs: the ribbed washboard half, the deep basin with a
    bit of grey water, a brass tap on the wall, the bar of white soap, a bucket underneath."""
    mG = fin(granite_tone(951), dust=0.5)

    def top(ctx):
        if ctx.face != 'up':
            return granite_tone(952)(ctx)
        x, z = ctx.pos[0], ctx.pos[2]
        if 1.6 < x < 7.4 and 2.6 < z < 13.4:
            return (GRANITO, 3 if int(z * 2) % 2 else 6)                       # washboard ribs
        return granite_tone(953)(ctx)
    P = [box((0.6, 0.0, 2.4), (3.0, 9.0, 14.6), fin(bricks(954, off=(0, 0, 0)), dust=0.3)),
         box((13.0, 0.0, 2.4), (15.4, 9.0, 14.6), fin(bricks(955, off=(0, 0, 0)), dust=0.3)),
         box((0.4, 9.0, 1.6), (8.0, 14.2, 15.6), fin(top, dust=0.2)),                        # washboard half
         box((8.0, 9.0, 1.6), (15.6, 10.2, 15.6), fin(lambda c: (WATER_T, 3 + (hh(c.i, c.j) > 0.85)) if c.face == 'up' else granite_tone(959)(c), ao=0.6)),
         box((8.0, 10.2, 1.6), (15.6, 14.2, 3.0), mG), box((8.0, 10.2, 14.2), (15.6, 14.2, 15.6), mG),
         box((14.2, 10.2, 3.0), (15.6, 14.2, 14.2), mG)]
    mCu = fin(brass(BRASS, base=4, seed=956, tarnish=0.6), dust=0.4)
    P += [box((10.6, 15.0, 14.8), (12.0, 16.4, 16.0), mCu), box((10.8, 15.4, 12.0), (11.8, 16.2, 14.8), mCu),
          box((10.9, 14.6, 12.0), (11.7, 15.4, 12.8), mCu), box((10.4, 16.4, 15.0), (12.2, 17.0, 15.6), fin(flat(REDP, 4), ao=0))]
    P += rbox((2.2, 14.2, 3.0), (5.6, 15.4, 5.4), fin(lambda c: (LINEN, 7 if c.face == 'up' else 6), ao=0.3), r=0.4)   # jabon blanco
    P += rbox((5.0, 0.0, 5.0), (11.0, 6.4, 11.0), fin(smooth(PVC_B, base=4, seed=957), dust=0.5), r=1.4)
    P += [box((5.4, 6.2, 5.4), (10.6, 6.3, 10.6), fin(flat(WATER_T, 3), ao=0), faces=('up',)),
          box((5.2, 6.4, 7.8), (10.8, 7.0, 8.2), fin(flat(GRAPH, 4), ao=0))]
    P.append(box((0.2, 4.0, 1.2), (3.2, 12.8, 1.6), fin(cloth(LINEN, base=4, seed=958, folds=0.5, stains=0.7, stain_col=hx('#6a5a3a')), ao=0.3)))
    return P


def bottle_parts(x, z, y0, w, d, h, col, cap, label=None, neck=0.5):
    """Plastic bottle / jug: body, shoulder, cap, optional paper label colour band."""
    def body(ctx):
        if label and 0.3 < ctx.t < 0.7 and ctx.face in ('north', 'south', 'west', 'east'):
            return (label, 6 if ctx.j % 3 else 5)
        return (col, 5 + (ctx.i == 1) - (ctx.edge() == 0 and ctx.face != 'up'))
    P = rbox((x, y0, z), (x + w, y0 + h, z + d), fin(body, ao=0.3, dust=0.8), r=min(w, d) * 0.22)
    P.append(box((x + w * 0.3, y0 + h, z + d * 0.3), (x + w * 0.7, y0 + h + neck + 0.4, z + d * 0.7), fin(flat(cap, 4), ao=0, dust=0.5)))
    return P


def estante_lavadero_parts(kind='lavadero'):
    """Grey steel shelving (1 block, 1.9 m) bolted to the wall. kind 'lavadero': bleach jugs, detergent, washing
    powder boxes, clothes pegs, a roll of bin bags. kind 'herramientas': paint cans, a toolbox, an extension cord,
    jars of screws, an old radio."""
    mS = fin(painted(CHAPA, base=5, seed=961, chips=0.15, under=RUST, grime=0.0), dust=1.0)
    P = []
    for (x, z) in ((0.4, 6.0), (14.6, 6.0), (0.4, 14.4), (14.6, 14.4)):
        P.append(box((x, 0.0, z), (x + 1.0, 30.0, z + 1.0), fin(lambda c: (CHAPA, 5) if not (c.face in ('north', 'south') and c.j % 4 == 0 and 0 < c.i < c.w - 1) else (BAKE, 2), ao=0.2, dust=0.4)))
    for y in (1.2, 10.6, 20.0, 29.0):
        P.append(box((0.4, y, 6.0), (15.6, y + 0.6, 15.4), mS))
    if kind == 'lavadero':
        P += bottle_parts(1.6, 8.0, 1.8, 3.4, 3.4, 6.6, YELLOWP, REDP, label=LINEN)
        P += bottle_parts(5.6, 8.4, 1.8, 3.0, 3.0, 6.0, PVC_B, LINEN, label=LINEN)
        P += bottle_parts(9.6, 9.0, 1.8, 2.2, 2.2, 7.2, LEAF, LINEN, label=YELLOWP)
        P += bottle_parts(12.2, 8.4, 1.8, 2.4, 2.4, 5.4, PINK, LINEN)
        for n, (x, col) in enumerate(((1.6, CELESTE), (6.6, REDP))):
            P.append(box((x, 11.2, 8.0), (x + 4.4, 18.4, 13.0), fin(lambda c, col=col: (col, 5) if c.face != 'north' or c.j < c.h - 6 else (LINEN, 7), ao=0.4, dust=1.0)))
        P += [box((11.6, 11.2, 8.4), (14.6, 14.6, 12.6), fin(cloth(LILA, base=4, seed=962, folds=0.6), ao=0.4))]
        for k in range(5):
            P.append(box((11.8 + k * 0.6, 14.6, 9.0 + (k % 2)), (12.2 + k * 0.6, 16.0, 9.4 + (k % 2)), fin(flat((REDP, YELLOWP, LEAF, CELESTE, PINK)[k], 5), ao=0)))
        P += rbox((2.0, 20.6, 8.0), (6.0, 24.6, 13.0), fin(lambda c: (BLACKP, 3 + (c.i % 3 == 0)), ao=0.4, dust=1.0), r=0.8)
        P += [box((7.0, 20.6, 7.6), (14.0, 22.0, 14.0), fin(cloth(LINEN, base=5, seed=963, folds=0.4, stains=0.5), ao=0.4, dust=1.2)),
              box((7.4, 22.0, 8.0), (13.4, 23.4, 13.6), fin(cloth(GERAN, base=4, seed=964, folds=0.4, stains=0.2), ao=0.4, dust=1.2))]
    else:
        for n, (x, col) in enumerate(((1.4, LINEN), (5.8, CELESTE), (10.4, GREENP))):
            def can(ctx, col=col):
                if ctx.face == 'up':
                    d = math.hypot(ctx.s - 0.5, ctx.t - 0.5)
                    return (NICKEL, 5 if d > 0.4 else 4) if d > 0.3 else (col, 4)
                if 0.25 < ctx.t < 0.75:
                    return (col, 5 if ctx.j % 3 else 6)
                return (NICKEL, 4 + (ctx.i == 1))
            P += rbox((x, 1.8, 8.0), (x + 4.0, 6.8, 12.6), fin(can, ao=0.3, dust=1.0), r=1.0)
            P.append(box((x, 6.8 - 0.01, 8.0 + 0.6), (x + 4.0, 7.4, 8.0 + 1.2), fin(flat(col, 3), ao=0)) if n == 1 else
                     box((x + 0.2, 6.8, 9.0), (x + 0.4, 9.0, 11.6), fin(flat(NICKEL, 5), ao=0)))
        mTb = fin(painted(REDP, base=4, seed=965, chips=0.2, under=IRON), dust=0.8)
        P += [box((1.4, 11.2, 7.8), (9.4, 15.4, 13.4), mTb), box((3.4, 15.4, 10.2), (7.4, 16.2, 11.0), fin(flat(BLACKP, 3), ao=0))]
        P += rbox((10.6, 11.2, 8.0), (14.6, 14.4, 13.0), fin(lambda c: (REDP, 6) if c.face != 'up' else (GRAPH, 4), ao=0.3), r=1.6)
        for n, x in enumerate((1.6, 4.2, 6.8, 9.4, 12.0)):
            P.append(box((x, 20.6, 9.0), (x + 2.0, 23.6, 11.0), fin(lambda c: (GLASS_J, 5 + (c.i == 1)) if c.j > 1 or c.face == 'up' else (GOLD, 4), ao=0.3, dust=1.0)))
        P += cobweb_parts(0.4, 29.0, 15.4, 'ne')
    return P


def cobweb_parts(x, y, z, corner='nw', size=5.0):
    """A dusty cobweb filling a top corner (cutout): radial threads and sagging rings."""
    def t(ctx):
        u = ctx.s if corner in ('nw', 'sw') else 1 - ctx.s
        v = ctx.t
        r = math.hypot(u, v)
        a = math.atan2(v, u)
        if r > 1.0:
            return None
        spoke = abs(((a / (math.pi / 2)) * 6) % 1.0 - 0.5) > 0.42
        ring = abs((r * 5 + 0.15 * math.sin(a * 8)) % 1.0 - 0.5) > 0.44
        if spoke or ring:
            return (230, 226, 216, 255) if hh(ctx.i, ctx.j, 966) > 0.35 else None
        return None
    return [plane((x, y - size, z - 0.05), (x + size, y, z - 0.05), fin(t, ao=0, dust=0), faces=('north', 'south'))]


def balde_parts():
    """Bucket with the floor cloth and the squeegee ('secador') leaning against it: the Argentine way to wash a floor."""
    mB = fin(smooth(GERAN, base=4, seed=971), dust=0.4)
    P = rbox((2.4, 0.0, 6.0), (8.4, 6.0, 12.0), mB, r=1.4)
    P += [box((2.8, 5.0, 6.4), (8.0, 5.1, 11.6), fin(flat(WATER_T, 4), ao=0), faces=('up',)),
          box((2.6, 5.4, 8.8), (8.2, 6.4, 9.2), fin(flat(GRAPH, 4), ao=0)),
          box((2.0, 3.0, 5.6), (6.0, 6.6, 7.4), fin(cloth(pal('#2a2620', '#3c372e', '#504a3e', '#66604f', '#7e7762', '#958d76'), base=3, seed=972, folds=0.7, stains=0.6), ao=0.4))]
    mW = fin(wood(PINO, base=4, seed=973, axis=1), dust=0.3)
    rot = ('x', 22.5, (12.0, 0.0, 6.0))
    P += [box((11.6, 0.0, 6.0), (12.4, 26.0, 6.8), mW, rot=rot),
          box((7.6, 0.0, 4.6), (16.4, 1.6, 6.2), fin(lambda c: (BLACKP, 3) if c.pos[1] < 0.6 else (PINO, 5), ao=0.3), rot=rot)]
    return P


# ============================================================================================ BASEMENT (sotano)
SABANA = pal('#3e3a34', '#56514a', '#706a60', '#8a8478', '#a39d90', '#bab4a7', '#ccc7bb', '#dcd8cd', '#e9e6dd')


def drape_tone(seed=0, axis='i', px=3.0, hem=True):
    """Old dust sheet: soft vertical folds, yellowed stains, dust on top, grime at the hem; scalloped hem cut-out."""
    def t(ctx):
        P = tp(ctx)
        if ctx.face == 'up':
            k = 6 + (1 if hh(int(P[0] / 2), int(P[2] / 2), seed) > 0.8 else 0)
            return (SABANA, k)
        u = (ctx.i if axis == 'i' else ctx.j) + 0.5
        ph = hh(seed, FI[ctx.face]) * 6.28
        f = math.sin(u / px * 2.1 + ph + 0.8 * math.sin(u / (px * 2.6) + ph))
        k = 6 + (1 if f > 0.55 else (-1 if f < -0.5 else 0)) - (1 if f < -0.88 else 0)
        if ctx.face != 'down' and P[1] < 3.0:
            k -= 1
        if hem and ctx.face != 'down' and ctx.j >= ctx.h - 2 and ctx.pos[1] < 1.2:
            if hh(ctx.i // 2, seed, 3) < 0.35 and ctx.j == ctx.h - 1:
                return None
        n = vn(P[0] / 6.0, P[1] / 6.0, P[2] / 6.0, seed + 30)
        c = T(SABANA, k)
        if n > 0.68:
            c = mix(c, hx('#9a845a'), 0.3)
        return c
    return t


def tapado_parts(kind):
    """Furniture under white dust sheets in the basement. kind: 'sillon' (an armchair), 'ropero' (a wardrobe, 1.9 m),
    'mesa' (a table with chairs upside-down on it), 'espejo' (a tall mirror, the sheet slipped off one corner),
    'figura' (something the size of a seated person... it has shoulders)."""
    m = lambda sd, **kw: fin(drape_tone(981 + sd, **kw), ao=0.5, dust=1.4)
    P = []
    if kind == 'sillon':
        P += [box((0.6, 0.0, 1.0), (15.4, 9.0, 15.0), m(0)), box((1.0, 9.0, 11.0), (15.0, 18.0, 15.0), m(1)),
              box((0.4, 9.0, 1.0), (3.2, 12.4, 11.0), m(2)), box((12.8, 9.0, 1.0), (15.6, 12.4, 11.0), m(3)),
              box((1.4, 18.0, 11.4), (14.6, 19.0, 14.6), m(4)),
              box((0.2, 0.0, 0.6), (15.8, 5.0, 1.0), m(5)), box((3.2, 9.0, 1.0), (12.8, 10.0, 11.0), m(6))]
    elif kind == 'ropero':
        P += [box((0.8, 0.0, 2.4), (15.2, 30.0, 15.2), m(0)), box((0.6, 30.0, 2.2), (15.4, 31.0, 15.4), m(1)),
              box((0.4, 0.0, 2.0), (15.6, 6.0, 2.4), m(2)), box((5.0, 18.0, 2.0), (11.0, 30.0, 2.4), m(3))]
    elif kind == 'mesa':
        P += [box((0.4, 9.6, 0.4), (15.6, 12.6, 15.6), m(0)),
              box((0.0, 2.0, 0.0), (0.4, 12.6, 16.0), m(1)), box((15.6, 2.0, 0.0), (16.0, 12.6, 16.0), m(2)),
              box((0.4, 2.6, 0.0), (15.6, 12.6, 0.4), m(3)), box((0.4, 3.4, 15.6), (15.6, 12.6, 16.0), m(4)),
              box((2.0, 12.6, 3.0), (8.0, 20.0, 9.0), m(5)), box((9.0, 12.6, 6.0), (14.0, 19.0, 12.0), m(6)),
              box((2.6, 20.0, 3.6), (7.4, 21.0, 8.4), m(7))]
        mL = fin(lustre(CAOBA, base=3, seed=989, axis=1))
        for (x, z) in ((1.2, 1.2), (13.6, 1.2), (1.2, 13.6), (13.6, 13.6)):
            P.append(box((x, 0.0, z), (x + 1.2, 2.6, z + 1.2), mL))
    elif kind == 'espejo':
        rot = ('x', 22.5, (8.0, 0.0, 4.0))
        P += [box((2.4, 0.0, 3.0), (13.6, 29.0, 4.2), fin(lustre(CAOBA, base=3, seed=991), dust=1.0), rot=rot),
              box((3.4, 1.4, 2.9), (12.6, 28.0, 3.0), fin(mirror_tone(cracked=True, seed=992, fog=0.5), ao=0, dust=0), faces=('north',), rot=rot),
              box((2.2, 0.0, 2.2), (13.8, 20.0, 2.8), m(0), rot=rot),
              box((7.6, 20.0, 2.4), (13.8, 29.6, 2.8), m(1), rot=rot),
              box((0.6, 0.0, 0.2), (12.0, 1.2, 3.4), m(2))]                                          # the part that slid off
    else:  # figura
        P += [box((2.0, 0.0, 2.0), (14.0, 8.0, 14.0), m(0)), box((3.0, 8.0, 6.0), (13.0, 16.0, 13.0), m(1)),
              box((2.6, 15.0, 6.4), (13.4, 18.4, 12.6), m(2)),                                          # shoulders
              box((5.6, 18.4, 7.6), (10.4, 20.0, 11.4), m(3)),                                          # neck
              box((5.0, 20.0, 6.8), (11.0, 25.6, 12.2), m(4)),                                          # the head
              box((5.6, 25.6, 7.4), (10.4, 26.4, 11.6), m(5)),
              box((1.6, 0.0, 1.6), (14.4, 3.0, 2.0), m(6)), box((2.0, 8.0, 2.0), (14.0, 9.0, 6.0), m(7))]   # lap
    return P


JARS = [(REDP, GOLD), (pal('#3a1a04', '#5a2a08', '#8a4410', '#b8621c', '#d8842c', '#eaa848'), CROCHET), (LEAF, GOLD),
        (pal('#140a1a', '#24102e', '#3a1a44', '#52245c', '#6a3274'), REDP), (CARTON, GOLD), (pal('#2e1406', '#4a220c', '#6a3414', '#8a4a1e'), LINEN)]


def jar_parts(x, z, y0, n, w=2.6, h=3.6):
    fill, lid = JARS[n % len(JARS)]

    def t(ctx):
        if ctx.face == 'up':
            return (fill, 3)
        if ctx.i in (0, ctx.w - 1):
            return (GLASS_J, 5)
        if ctx.j < 1:
            return (GLASS_J, 6)
        if 0.35 < ctx.t < 0.6 and n % 2 == 0:
            return (PAPER, 7)                                                     # hand-written label
        return (fill, 4 + (ctx.i == 1) + (hh(ctx.i, ctx.j, n) < 0.15))
    P = [box((x, y0, z), (x + w, y0 + h, z + w), fin(t, ao=0.3, dust=1.4))]
    if n % 3 == 1:
        P.append(box((x - 0.3, y0 + h, z - 0.3), (x + w + 0.3, y0 + h + 0.6, z + w + 0.3), fin(lambda c: (REDP, 5) if (c.i + c.j) % 2 else (LINEN, 7), ao=0, dust=1.2)))
    else:
        P.append(box((x + 0.1, y0 + h, z + 0.1), (x + w - 0.1, y0 + h + 0.6, z + w - 0.1), fin(brass(GOLD if lid is GOLD else NICKEL, base=4, seed=n), ao=0, dust=1.2)))
    return P


def estante_frascos_parts(v=1):
    """Rough pine shelves in the basement full of the Nona's preserves (tomato, peaches, eggplant in vinegar, plum jam,
    quince): dusty jars with cloth or tin lids, cobwebs in the corners. v=2: fewer jars, a demijohn and a box."""
    mW = fin(wood(PINO, base=3, seed=1001, axis=0, boards=(1, 9), wear=0.6), dust=1.6)
    mP = fin(wood(PINO, base=3, seed=1002, axis=1), dust=0.8)
    P = [box((0.4, 0.0, 7.0), (1.6, 30.0, 8.2), mP), box((14.4, 0.0, 7.0), (15.6, 30.0, 8.2), mP),
         box((0.4, 0.0, 14.6), (1.6, 30.0, 15.8), mP), box((14.4, 0.0, 14.6), (15.6, 30.0, 15.8), mP)]
    for y in (1.0, 10.4, 19.8, 29.0):
        P.append(box((0.0, y, 7.0), (16.0, y + 0.8, 15.8), mW))
    n = 0
    for (y, cnt) in ((1.8, 4 if v == 1 else 0), (11.2, 4 if v == 1 else 3), (20.6, 4 if v == 1 else 2)):
        for k in range(cnt):
            x = 1.8 + k * 3.3 + (hh(v, y, k) - 0.5) * 0.6
            z = 9.0 + (k % 2) * 2.4
            P += jar_parts(x, z, y, n + v * 3, h=3.2 + hh(v, k, y) * 1.6)
            n += 1
    if v == 2:
        P += damajuana_parts(4.6, 11.2, 1.8, s=0.8)
        P.append(box((7.4, 1.8, 8.4), (14.8, 7.0, 15.0), fin(carton_box_tone('1961', 1003), dust=1.4)))
    P += cobweb_parts(1.6, 29.0, 15.2, 'nw') + cobweb_parts(9.4, 19.8, 15.2, 'ne', size=4.0)
    return P


def damajuana_parts(cx, cz, y0, s=1.0):
    """Wicker-covered demijohn of wine (damajuana)."""
    mW = fin(wicker(RUSH, base=4, seed=1011), dust=1.2)
    mG = fin(lambda c: (LEAF, 2 + (c.i == 1)), ao=0.2, dust=1.0)
    P = rbox((cx - 3.4 * s, y0, cz - 3.4 * s), (cx + 3.4 * s, y0 + 6.4 * s, cz + 3.4 * s), mW, r=1.4 * s)
    P += rbox((cx - 2.4 * s, y0 + 6.4 * s, cz - 2.4 * s), (cx + 2.4 * s, y0 + 8.0 * s, cz + 2.4 * s), mG, r=1.0 * s)
    P += [box((cx - 0.9 * s, y0 + 8.0 * s, cz - 0.9 * s), (cx + 0.9 * s, y0 + 10.4 * s, cz + 0.9 * s), mG),
          box((cx - 1.0 * s, y0 + 10.4 * s, cz - 1.0 * s), (cx + 1.0 * s, y0 + 11.0 * s, cz + 1.0 * s), fin(flat(CARTON, 3), ao=0)),
          box((cx + 2.6 * s, y0 + 4.0 * s, cz - 0.4), (cx + 3.8 * s, y0 + 7.4 * s, cz + 0.4), mW)]
    return P


def carton_box_tone(label, seed=0):
    """Cardboard box with packing tape and a marker label on the front."""
    def t(ctx):
        P = tp(ctx)
        if ctx.face == 'up':
            if abs(ctx.s - 0.5) < 0.12:
                return (CARTON, 6)                                                # tape
            return (CARTON, 4 + (abs(ctx.t - 0.5) < 0.03) * -1)
        if ctx.face == 'north' and label:
            pts = set(draw_text(F35, label, max(1, (ctx.w - text_width(F35, label)) // 2), max(1, ctx.h // 2 - 2), sp=1))
            if (ctx.i, ctx.j) in pts:
                return INK
        k = 4 + (1 if (int(P[1]) % 7 == 0) else 0) - (1 if vn(P[0] / 4, P[1] / 4, P[2] / 4, seed) > 0.72 else 0)
        if P[1] < 2.0:
            k -= 1                                                                # damp at the bottom
        return (CARTON, k)
    return t


def cajas_parts(kind):
    """Cardboard boxes. 'apiladas': three stacked, labelled NAVIDAD / ROPA / NONA. 'abierta': an open box spilling
    old things: a coil of Christmas lights, photos, a porcelain doll arm."""
    P = []
    if kind == 'apiladas':
        P += [box((1.0, 0.0, 2.0), (15.0, 8.0, 14.0), fin(carton_box_tone('NAVIDAD', 1021), dust=1.2)),
              box((2.0, 8.0, 3.0), (13.0, 15.0, 12.6), fin(carton_box_tone('ROPA', 1022), dust=1.4), rot=('y', 22.5, (7.5, 8.0, 7.8))),
              box((2.6, 15.0, 4.0), (12.6, 21.0, 11.0), fin(carton_box_tone('NONA', 1023), dust=1.6))]
    else:
        P += [box((2.0, 0.0, 3.0), (14.0, 7.0, 13.0), fin(carton_box_tone('FOTOS', 1024), dust=1.0), faces=('north', 'south', 'west', 'east', 'down')),
              box((2.6, 5.0, 3.6), (13.4, 5.2, 12.4), fin(flat(CARTON, 2), ao=0), faces=('up',)),
              box((2.0, 7.0, 1.4), (14.0, 7.4, 3.0), fin(carton_box_tone(None, 1025), dust=0.6), rot=('x', -45, (8.0, 7.0, 3.0))),
              box((2.0, 7.0, 13.0), (14.0, 7.4, 14.8), fin(carton_box_tone(None, 1026), dust=0.6), rot=('x', 45, (8.0, 7.0, 13.0)))]
        for n in range(5):
            x, z = 3.6 + n * 1.8, 5.0 + (n % 2) * 2.4
            P.append(box((x, 5.2, z), (x + 2.2, 5.5, z + 3.0), fin(canvas_tone(photo_canvas(('nona_joven', 'casamiento', 'choripan', 'cumple', 'nona_joven')[n]), face='up'),
                                                                 ao=0, dust=0.4), faces=('up',), rot=('y', 22.5 if n % 2 else -22.5, (x + 1.1, 5.2, z + 1.5))))
        P += [box((9.0, 5.2, 9.0), (10.0, 10.0, 10.0), fin(flat(PORCELAIN, 6), ao=0.2), rot=('z', -22.5, (9.5, 5.2, 9.5))),
              box((8.6, 9.6, 8.8), (10.2, 10.6, 10.2), fin(flat(PORCELAIN, 5), ao=0), rot=('z', -22.5, (9.5, 5.2, 9.5)))]   # doll arm
        for k in range(10):
            a = k / 10 * 6.28
            P.append(box((11.0 + math.cos(a) * 2.4, 0.0, 15.0 + math.sin(a) * 1.0), (11.4 + math.cos(a) * 2.4, 0.4, 15.4 + math.sin(a) * 1.0),
                         fin(flat((REDP, LEAF, YELLOWP, CELESTE)[k % 4], 5), ao=0)))
    return P


def caldera_parts(lit):
    """The old basement boiler: a riveted cylindrical tank on a cast-iron burner base, the little window with the
    blue pilot flame, a round pressure gauge, valves with red hand wheels, flue and pipes up into the ceiling.
    Lit (pilot on) / off. Model is 2 blocks tall (collision only on the lower block)."""
    mT = fin(painted(pal('#1a1c1a', '#262a26', '#343a34', '#444c44', '#566056', '#6a766a', '#7e8c7e'), base=4, seed=1031, chips=0.3,
                     under=RUST, grime=0.4), dust=1.0)
    mI = fin(iron(seed=1032, rust=0.5), dust=0.8)
    mCu = fin(brass(RUST, base=4, seed=1033, tarnish=0.3), dust=0.6)

    def base(ctx):
        if ctx.face == 'north':
            i, j, w, h = ctx.i, ctx.j, ctx.w, ctx.h
            if abs(i + 0.5 - w / 2) < 3.5 and 3 <= j < 9:
                if abs(i + 0.5 - w / 2) > 2.5 or j in (3, 8):
                    return (NICKEL, 4)
                if lit:
                    if j >= 6:
                        return T(FLAME_B, 4 + (abs(i + 0.5 - w / 2) < 1.2))
                    return T(EMBER, 3 + (hh(i, j) > 0.5))
                return (BAKE, 1)
            if j % 4 == 0 and 2 < i < w - 3 and j > 10:
                return (BAKE, 2)                                                  # air vents
        return iron(seed=1034, rust=0.4)(ctx)
    P = [box((1.0, 0.0, 2.0), (15.0, 8.0, 15.0), fin(base, dust=1.0), shade=True)]
    P += rbox((1.4, 8.0, 2.4), (14.6, 27.0, 14.6), mT, r=3.0)
    P += [box((1.0, 13.0, 2.0), (15.0, 13.6, 15.0), mI), box((1.0, 21.0, 2.0), (15.0, 21.6, 15.0), mI)]   # bands
    P += rbox((3.0, 27.0, 4.0), (13.0, 28.4, 13.0), mT, r=2.0)
    P += [box((6.4, 28.4, 7.4), (9.6, 32.0, 10.6), mI)]                                                   # flue

    def gauge(ctx):
        if ctx.face != 'north':
            return (NICKEL, 4)
        d = math.hypot(ctx.s - 0.5, ctx.t - 0.5)
        if d > 0.5:
            return None
        if d > 0.4:
            return (NICKEL, 5)
        a = math.atan2(ctx.t - 0.5, ctx.s - 0.5)
        if abs(a + 2.2) < 0.25 and d < 0.35:
            return INK_RED                                                         # needle (in the red)
        if d > 0.3 and int((a + 4) * 4) % 2 == 0:
            return (BAKE, 2)
        return (CROCHET, 7)
    P += [box((5.6, 17.0, 1.6), (10.4, 21.6, 2.4), fin(gauge, ao=0, dust=0.3)),
          box((7.6, 15.4, 2.0), (8.4, 17.0, 2.6), mCu)]
    mV = fin(lambda c: (REDP, 4 + (c.i % 3 == 0)), ao=0.2, dust=0.6)
    P += [box((14.6, 10.0, 6.6), (16.0, 11.4, 8.0), mCu), box((14.6, 22.0, 9.4), (16.0, 23.4, 10.8), mCu),
          box((15.0, 11.4, 6.8), (15.8, 32.0, 7.8), mCu), box((15.0, 23.4, 9.6), (15.8, 32.0, 10.6), mCu)]
    P += [box((15.8, 18.0, 5.4), (16.4, 18.4, 9.0), mV), box((15.8, 16.4, 7.0), (16.4, 20.0, 7.4), mV)]
    P += [box((3.0, 8.0, 1.6), (13.0, 8.6, 2.4), fin(lambda c: (PAPER, 6) if (c.i, c.j) not in set(draw_text(F35, 'OK', 1, 0)) else INK, ao=0, dust=0.4))]
    return P


def foco_parts(lit):
    """Bare bulb on a twisted cord hanging from the basement ceiling (porcelain socket); lit / off."""
    P = cord_parts(8.0, 8.0, 5.6, 16.0, col=GRAPH, k=3)
    P += [box((7.6, 15.6, 7.6), (8.4, 16.0, 8.4), fin(flat(PORC, 5), ao=0)),
          box((7.0, 4.0, 7.0), (9.0, 5.8, 9.0), fin(porcelain(PORC, base=5, seed=1041, grime=0.0), dust=0.6))]

    def bulb(ctx):
        if lit:
            if ctx.face in ('north', 'south', 'west', 'east') and abs(ctx.s - 0.5) < 0.15 and 0.2 < ctx.t < 0.6:
                return (FLAME, 6)                                                # filament
            return (OPAL_LIT, 6 + (ctx.edge() > 0))
        if ctx.face in ('north', 'south', 'west', 'east') and abs(ctx.s - 0.5) < 0.15 and 0.2 < ctx.t < 0.6:
            return (BAKE, 3)
        return (GLASS_J, 5 + (ctx.edge() > 0)) if hh(ctx.i, ctx.j, 1042) > 0.1 else (BAKE, 4)
    mB = fin(bulb, ao=0, dust=0 if lit else 0.6)
    P += [box((7.2, 3.4, 7.2), (8.8, 4.0, 8.8), M_CHROME)]
    P += rbox((6.6, 0.6, 6.6), (9.4, 3.4, 9.4), mB, r=0.7, shade=not lit)
    P += [box((7.3, 0.1, 7.3), (8.7, 0.6, 8.7), mB, shade=not lit)]
    return P


# ============================================================================================ THE 1961 ROOM
CORREA = pal('#140a06', '#22120a', '#32190e', '#442314', '#58301c', '#6e3e26', '#86503a')


def cama_hierro_parts(piece):
    """The 1961 iron bed: rusted black iron, a bare stained ticking mattress, cracked leather restraint straps with
    buckles (wrists at the head, ankles at the foot). 'cabecera' / 'pie' as every bed in the kit."""
    head = piece == 'cabecera'
    mI = fin(iron(seed=1051, rust=0.7, worn=0.4), dust=1.4)
    mIs = fin(iron(seed=1052, rust=0.6), dust=1.2)

    def mattress(ctx):
        P = tp(ctx)
        u = P[0]
        st = int(u) % 6
        k = 1 if st == 0 else (2 if st == 3 else 3)
        n = vn(P[0] / 5.0, P[1] / 5.0, P[2] / 5.0, 1053)
        if ctx.face == 'up':
            k = 3
            if n > 0.6:
                return (CARTON, 2 + (n > 0.72))                                  # old stains
            if vn(P[0] / 3.0, P[2] / 3.0, 0.5, 1054) > 0.78:
                return (pal('#1a0a08', '#2e120c', '#421a12'), 1)                # dark, dried
        return (pal('#1b2338', '#2a3550', '#a9ad9f', '#c9cbbd', '#dddccf'), k) if n < 0.6 else (CARTON, 3)
    mM = fin(mattress, ao=0.7, dust=0.6)

    def strap(ctx):
        k = 3 + (hh(ctx.i, ctx.j, 1055) > 0.8) - (ctx.edge() == 0)
        if hh(ctx.i // 2, ctx.j, 1056) < 0.08:
            return (CORREA, 1)                                                    # cracks
        return (CORREA, k)
    mS = fin(strap, ao=0.3, dust=0.6)
    mBk = fin(brass(BRASS, base=3, seed=1057, tarnish=0.8), ao=0, dust=0.5)
    P = []
    zb = (14.6, 15.8) if head else (0.2, 1.4)
    top = 20.0 if head else 13.0
    for x0 in (0.6, 14.2):
        P += [box((x0, 0.0, zb[0]), (x0 + 1.2, top, zb[1]), mI),
              box((x0 - 0.15, top, zb[0] - 0.15), (x0 + 1.35, top + 0.6, zb[1] + 0.15), mI),
              box((x0 + 0.2, 5.0, 0.0 if head else zb[1]), (x0 + 1.0, 6.2, zb[0] if head else 16.0), mI)]
    for y in (8.0, top - 1.4):
        P.append(box((1.8, y, zb[0] + 0.2), (14.2, y + 0.8, zb[1] - 0.2), mI))
    for k in range(6):
        x = 2.8 + k * 2.1
        P.append(box((x - 0.3, 8.8, zb[0] + 0.4), (x + 0.3, top - 1.4, zb[1] - 0.4), mIs))
    z0, z1 = (0.0, 14.6) if head else (1.4, 16.0)
    P.append(box((1.6, 6.2, z0), (14.4, 9.0, z1), mM))
    zs = (4.0, 6.0) if head else (9.0, 11.0)
    P += [box((1.4, 9.0, zs[0]), (14.6, 9.4, zs[1]), mS),                                # strap across
          box((1.0, 3.4, zs[0]), (1.4, 9.4, zs[1]), mS), box((14.6, 3.4, zs[0]), (15.0, 9.4, zs[1]), mS),
          box((7.2, 9.2, zs[0] - 0.2), (8.8, 9.6, zs[1] + 0.2), mBk)]
    if head:
        for x in (0.4, 14.6):                                                            # wrist cuffs hanging from the frame
            P += [box((x, 2.0, 9.0), (x + 1.0, 6.2, 10.6), mS), box((x - 0.1, 2.0, 8.8), (x + 1.1, 3.2, 10.8), mS),
                  box((x - 0.15, 2.4, 9.4), (x + 1.15, 2.8, 10.2), mBk)]
    else:
        P += [box((3.0, 9.0, 3.0), (6.0, 9.4, 4.4), mS), box((10.0, 9.0, 3.0), (13.0, 9.4, 4.4), mS),
              box((4.0, 9.4, 3.2), (5.0, 9.6, 4.2), mBk), box((11.0, 9.4, 3.2), (12.0, 9.6, 4.2), mBk)]
    return P


def velas_derretidas_parts(kind, lit):
    """Melted candles on the floor of the 1961 room (or wherever the director needs them): 'grupo' (a cluster of
    seven of different heights in one big wax puddle) | 'sueltas' (three stubs). Lit / off."""
    if kind == 'grupo':
        spots = ((5.0, 6.0, 7.0, 1.0), (8.6, 5.0, 4.6, 0.9), (11.2, 7.4, 6.0, 0.8), (6.4, 9.8, 3.0, 0.9), (9.8, 10.4, 8.4, 1.1),
                 (12.4, 11.6, 2.2, 0.7), (4.0, 12.0, 4.0, 0.8))
    else:
        spots = ((5.0, 6.0, 2.6, 0.9), (10.0, 8.0, 1.6, 0.8), (7.0, 11.0, 3.6, 0.7))
    P = []
    for n, (x, z, h, r) in enumerate(spots):
        P += candle(x, z, 0.0, h, r=r, lit=lit, seed=1061 + n, melted=1.0)
    centres = [(x, z, r * 2.6) for (x, z, h, r) in spots]
    P.append(plane((0.0, 0.04, 0.0), (16.0, 0.04, 16.0), fin(puddle_tone(centres, seed=1067), ao=0, dust=0.3), faces=('up',)))
    return P


def estola_parts():
    """Father Anselmo's purple stole hanging from a rusty nail: gold embroidered crosses at the ends, fringe, frayed
    and with a burn hole (wall piece at chest height)."""
    def stole(ctx):
        P = tp(ctx)
        Y = ctx.pos[1]
        k = 4 + (1 if (ctx.i + int(Y * 2)) % 4 == 0 else 0)
        if Y < -6.4:
            if ctx.i % 2 == 0:
                return (GOLD, 4)                                                   # fringe
            return None
        if -5.6 < Y < -2.2:
            dx = abs(ctx.s - 0.5)
            if (dx < 0.14) or (abs(Y + 4.4) < 0.45):
                return (GOLD, 5 + (ctx.j % 2))                                     # embroidered cross
        if abs(Y + 6.0) < 0.3:
            return (GOLD, 4)
        if vn(P[0] / 2.0, P[1] / 2.0, P[2] / 2.0, 1071) > 0.78:
            return None if vn(P[0] / 2.0, P[1] / 2.0, P[2] / 2.0, 1071) > 0.84 else (BAKE, 2)   # burn hole
        return (pal('#120818', '#1e0c28', '#2c1238', '#3c1a4a', '#4e245e', '#623072', '#783e86'), k)
    m = fin(stole, ao=0.4, dust=0.6)
    P = [box((7.6, 11.0, 13.4), (8.4, 11.8, 16.0), fin(iron(seed=1072, rust=0.9), dust=0)),
         box((7.4, 10.8, 13.2), (8.6, 12.0, 13.4), fin(iron(seed=1073, rust=0.9), dust=0))]
    P += [box((5.6, 11.8, 13.0), (10.4, 12.4, 15.6), m),
          box((5.6, -7.4, 14.9), (7.8, 11.8, 15.4), m),                                    # back end (longer)
          box((8.2, -6.0, 13.2), (10.4, 11.8, 13.7), m),                                    # front end
          box((7.8, 10.6, 13.6), (8.2, 11.8, 14.9), m)]
    return P


def zapatitos_parts():
    """A little girl's black patent shoes with a strap, 1961, grey with dust, one on its side."""
    m = fin(lambda c: (BLACKP, 4 + (c.i == 1 and c.face != 'up') * 2) if c.pos[1] > 0.4 else (CARTON, 3), ao=0.3, dust=1.6)
    P = [box((4.0, 0.0, 5.0), (6.4, 1.8, 9.8), m), box((4.0, 1.8, 6.0), (6.4, 2.0, 6.5), m),
         box((8.6, 0.0, 6.0), (11.0, 2.4, 10.8), m, rot=('z', 45, (9.8, 0.0, 8.4)))]
    return P


def misal_parts():
    """An old missal open face down on the floor, the purple ribbon marker trailing; loose holy cards."""
    mC = fin(leatherette(BLACKP, base=3, seed=1081), dust=1.4)
    P = [box((3.0, 0.0, 4.0), (8.0, 1.4, 11.0), mC, rot=('z', 22.5, (8.0, 0.0, 7.5))),
         box((8.0, 0.0, 4.0), (13.0, 1.4, 11.0), mC, rot=('z', -22.5, (8.0, 0.0, 7.5))),
         box((7.6, 0.0, 4.0), (8.4, 1.0, 11.0), fin(lambda c: (PAPER, 6 if c.j % 2 else 4), ao=0.3, dust=1.0)),
         box((7.8, 0.0, 11.0), (8.4, 0.1, 15.0), fin(flat(LILA, 3), ao=0))]
    for (x, z, kind) in ((1.4, 12.0, 'virgen'), (11.4, 1.4, 'expedito')):
        cv = card_canvas(kind)
        P.append(box((x, 0.02, z), (x + 2.4, 0.02, z + 3.6), fin(canvas_tone(cv, face='up'), ao=0, dust=1.0), faces=('up',)))
    return P


# ============================================================================================ register: laundry, basement, 1961
F('tablero', 'Tablero de luz (palanca arriba: hay luz)', 'Breaker board (lever up: power on)', tablero_parts(True), env=('wall',),
  collision='none', sound='metal')
F('tablero_apagado', 'Tablero de luz (palanca abajo: apagón)', 'Breaker board (lever down: blackout)', tablero_parts(False),
  env=('wall',), collision='none', sound='metal')
F('pileta_lavar', 'Pileta de lavar', 'Laundry tub with washboard', pileta_lavar_parts(), sound='stone')
F('estante_lavadero', 'Estante del lavadero (lavandina y jabón)', 'Laundry shelves (bleach and detergent)', estante_lavadero_parts('lavadero'),
  sound='metal')
F('estante_herramientas', 'Estante de chapa (pinturas y herramientas)', 'Steel shelves (paint and tools)',
  estante_lavadero_parts('herramientas'), sound='metal')
F('balde_secador', 'Balde, trapo y secador', 'Bucket, floor cloth and squeegee', balde_parts(), collision='none')
for _k, _es, _en in (('sillon', 'Sillón tapado con una sábana', 'Armchair under a dust sheet'),
                     ('ropero', 'Ropero tapado con una sábana', 'Wardrobe under a dust sheet'),
                     ('mesa', 'Mesa con sillas tapada con una sábana', 'Table and chairs under a dust sheet'),
                     ('espejo', 'Espejo tapado (la sábana se resbaló)', 'Mirror under a dust sheet (slipped)'),
                     ('figura', 'Algo tapado con una sábana (tiene hombros)', 'Something under a dust sheet (it has shoulders)')):
    F('tapado_' + _k, _es, _en, tapado_parts(_k), sound='cloth')
F('estante_frascos', 'Estante con frascos de conserva', 'Shelves of preserve jars', estante_frascos_parts(1), sound='glass')
F('estante_frascos_2', 'Estante con frascos y damajuana', 'Shelves with jars and a demijohn', estante_frascos_parts(2), sound='glass')
F('damajuana', 'Damajuana', 'Wicker demijohn', damajuana_parts(8.0, 8.0, 0.0), sound='glass')
F('cajas_apiladas', 'Cajas apiladas (NAVIDAD, ROPA, NONA)', 'Stacked boxes (CHRISTMAS, CLOTHES, NONA)', cajas_parts('apiladas'),
  sound='paper')
F('caja_abierta', 'Caja abierta con fotos viejas', 'Open box of old photos', cajas_parts('abierta'), sound='paper')
F('caldera', 'Caldera (piloto encendido)', 'Boiler (pilot lit)', caldera_parts(True), light=5, sound='metal')
F('caldera_apagada', 'Caldera (apagada)', 'Boiler (out)', caldera_parts(False), sound='metal')
F('foco', 'Foco pelado colgando (encendido)', 'Bare hanging bulb (lit)', foco_parts(True), env=('ceil',), light=12,
  collision='none', directional=False, sound='glass')
F('foco_apagado', 'Foco pelado colgando (apagado)', 'Bare hanging bulb (off)', foco_parts(False), env=('ceil',),
  collision='none', directional=False, sound='glass')
F('cama_hierro_cabecera', 'Cama de hierro con correas, 1961 (cabecera)', 'Iron bed with leather straps, 1961 (head)',
  cama_hierro_parts('cabecera'), sound='metal')
F('cama_hierro_pie', 'Cama de hierro con correas, 1961 (pie)', 'Iron bed with leather straps, 1961 (foot)', cama_hierro_parts('pie'),
  sound='metal')
F('velas_derretidas', 'Velas derretidas en el piso (encendidas)', 'Melted floor candles (lit)', velas_derretidas_parts('grupo', True),
  light=11, collision='none', sound='candle')
F('velas_derretidas_apagadas', 'Velas derretidas en el piso (apagadas)', 'Melted floor candles (out)',
  velas_derretidas_parts('grupo', False), collision='none', sound='candle')
F('velas_sueltas', 'Tres cabos de vela (encendidos)', 'Three candle stubs (lit)', velas_derretidas_parts('sueltas', True), light=8,
  collision='none', sound='candle')
F('velas_sueltas_apagadas', 'Tres cabos de vela (apagados)', 'Three candle stubs (out)', velas_derretidas_parts('sueltas', False),
  collision='none', sound='candle')
F('estola_anselmo', 'Estola del Padre Anselmo colgada de un clavo', "Father Anselmo's stole on a nail", estola_parts(), env=('wall',),
  collision='none', sound='cloth')
F('lata_galletitas_vieja', 'Lata de galletitas de 1961 (oxidada, vacía)', 'The 1961 cookie tin (rusted, empty)', lata_parts('vieja'),
  collision='none', sound='metal')
F('zapatitos', 'Zapatitos de nena (1961)', "Little girl's shoes (1961)", zapatitos_parts(), collision='none', sound='cloth')
F('misal', 'Misal abierto en el piso', 'Old missal open on the floor', misal_parts(), collision='none', sound='paper')
