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
