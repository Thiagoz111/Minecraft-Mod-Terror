# Casa Morales - CUARTO DE TOTI (5x6, upstairs): unmade bed, the RGB gaming desk and the gamer chair, posters, and the
# PLACARD on the east wall (2 wide x 3 tall: doors not drawn here, so the hanging clothes of the placard back show).
import glob
import json
import os
import zlib


def h(*a):
    return zlib.crc32(repr(a).encode()) % 1000


def _have():
    keys = set()
    for p in glob.glob(os.path.join('tools', 'blocks', 'out', 'preview_*.json')):
        try:
            d = json.load(open(p))
        except Exception:
            continue
        keys |= set(d.get('models', {})) | set(d.get('cubes', {}))
    return keys


HAVE = _have()


def pick(*keys):
    """First key that exists (casa_estructura when built, otherwise a Colegio stand-in)."""
    for k in keys:
        if k in HAVE:
            return k
    return keys[-1]


def room(B, W, D, H, floor, wall, base, ceil, x0=0, z0=0, walls=None):
    """Floor at y=-1, ceiling at y=H, walls around (callables get (x, y, z))."""
    for x in range(W):
        for z in range(D):
            B.append((x0 + x, -1, z0 + z, floor(x, z) if callable(floor) else floor, 'north'))
            B.append((x0 + x, H, z0 + z, ceil, 'north'))
    for y in range(H):
        for x in range(-1, W + 1):
            for z in (-1, D):
                k = (walls(x, y, z) if walls else None) or (base if y == 0 else wall)
                B.append((x0 + x, y, z0 + z, k, 'north'))
        for z in range(D):
            for x in (-1, W):
                k = (walls(x, y, z) if walls else None) or (base if y == 0 else wall)
                B.append((x0 + x, y, z0 + z, k, 'north'))


B = []
W, D, H = 5, 6, 3


def twall(x, y, z):
    if x == W and z in (2, 3) and y in (0, 1):
        return 'casa_placard_fondo_izq' if z == 2 else 'casa_placard_fondo_der'
    if x == -1 and y == 1 and z == 4:
        return pick('casa_pared_toti_poster', 'casa_pared_toti')
    return None


room(B, W, D, H, lambda x, z: pick('casa_parquet_gastado', 'colegio_tablas_gastadas') if h(x, z) < 400 else pick('casa_parquet', 'colegio_tablas'),
     pick('casa_pared_toti', 'colegio_revoque'), pick('casa_pared_toti_zocalo', 'colegio_revoque_zocalo'), pick('casa_cielorraso', 'colegio_cielorraso'),
     walls=twall)
B = [b if not (b[3].startswith('casa_placard_fondo')) else (b[0], b[1], b[2], b[3], 'west') for b in B]
B = [b for b in B if not (b[0] == W and b[2] in (2, 3) and b[1] == 1)]
B += [(0, 0, 0, 'casa_cama_toti_cabecera', 'south'), (0, 0, 1, 'casa_cama_toti_pie', 'south')]
B += [(2, 0, 0, 'casa_escritorio_pc_izq', 'south'), (3, 0, 0, 'casa_escritorio_pc_der', 'south'), (2, 0, 1, 'casa_silla_gamer', 'north')]
B += [(0, 1, 1, 'casa_poster_banda', 'east'), (0, 1, 3, 'casa_poster_juego', 'east')]
B += [(4, 2, 2, 'casa_placard_maletero_izq', 'west'), (4, 2, 3, 'casa_placard_maletero_der', 'west')]
B += [(1, 0, 3, 'casa_ropa_tirada', 'north'), (2, 0, 4, 'casa_zapatillas', 'east'), (0, 0, 3, 'casa_cargador', 'east'),
      (3, 0, 4, 'casa_pelota', 'north'), (2, 2, 3, 'casa_plafon', 'north')]
SCENE = dict(blocks=B, camera=(0.9, 1.62, 5.6), target=(3.4, 0.9, 1.2), fov=76)
