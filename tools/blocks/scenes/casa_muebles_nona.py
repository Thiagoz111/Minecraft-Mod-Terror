# Casa Morales - CUARTO DE LA NONA (6x6): her single bed against the north wall with the radio nightstand, the
# home altar (lit candles: the only always-safe light) on the east wall under the holy cards, the rocking chair facing
# it with the basket of red wool, the walker parked, the waterfall wardrobe, the cookie tin on a side table.
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
W, D, H = 6, 6, 3
room(B, W, D, H, lambda x, z: pick('casa_parquet_gastado', 'colegio_tablas_gastadas') if h(x, z) < 250 else pick('casa_parquet', 'colegio_tablas'),
     pick('casa_empapelado_nona', 'colegio_revoque'), pick('casa_empapelado_nona_zocalo', 'colegio_revoque_zocalo'),
     pick('casa_cielorraso', 'colegio_cielorraso'))
B += [(1, 0, 0, 'casa_cama_nona_cabecera', 'south'), (1, 0, 1, 'casa_cama_nona_pie', 'south'),
      (2, 0, 0, 'casa_mesa_luz_nona', 'south'), (0, 0, 0, 'casa_mesa_luz', 'south'), (0, 1, 0, 'casa_velador_apagado', 'south'),
      (2, 0, 1, 'casa_pantuflas', 'south'), (2, 1, 0, 'casa_foto_nona_joven', 'south')]
B += [(4, 0, 0, 'casa_ropero_abajo', 'south'), (4, 1, 0, 'casa_ropero_arriba', 'south')]
B += [(5, 0, 2, 'casa_altar', 'west'), (5, 1, 2, 'casa_altar_estampitas', 'west')]
B += [(3, 0, 2, 'casa_mecedora', 'east'), (3, 0, 3, 'casa_canasta_lana', 'east'), (2, 0, 4, 'casa_andador', 'north'),
      (5, 0, 4, 'casa_mesita_auxiliar', 'west'), (5, 1, 4, 'casa_lata_galletitas', 'west'), (2, 2, 2, 'casa_plafon_apagado', 'north')]
SCENE = dict(blocks=B, camera=(4.7, 1.62, 5.6), target=(1.8, 0.7, 0.8), fov=74)
