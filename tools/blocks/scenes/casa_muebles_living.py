# Casa Morales - LIVING (9x7): floral sofa against the west wall under the family photo wall, coffee table, the
# Nona's rocking chair facing the CRT TV (telenovela on), armchair, standing lamp, gas heater on the north wall.
# Walls/floors: casa_estructura blocks when that kit exists, otherwise Colegio stand-ins.
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
W, D, H = 9, 7, 3
WALL = pick('casa_pared_living', 'colegio_revoque')
BASE = pick('casa_pared_living_zocalo', 'colegio_revoque_zocalo')
room(B, W, D, H, lambda x, z: pick('casa_parquet_gastado', 'colegio_tablas_gastadas') if h(x, z) < 200 else pick('casa_parquet', 'colegio_tablas'),
     WALL, BASE, pick('casa_cielorraso', 'colegio_cielorraso'))
# sofa against the west wall, sitters look east: a viewer in front looks west -> his left is south (+z)
B += [(0, 0, 2, 'casa_sillon_der', 'east'), (0, 0, 3, 'casa_sillon_centro', 'east'), (0, 0, 4, 'casa_sillon_izq', 'east')]
B += [(2, 0, 3, 'casa_mesa_ratona', 'east')]
B += [(0, 0, 5, 'casa_lampara_pie', 'east'), (1, 0, 0, 'casa_sillon_individual', 'south')]
# photo wall above the sofa
B += [(0, 2, 3, 'casa_foto_familia', 'east'), (0, 1, 2, 'casa_foto_cumple', 'east'), (0, 1, 4, 'casa_foto_choripan', 'east'),
      (0, 2, 2, 'casa_foto_casamiento', 'east'), (0, 2, 4, 'casa_foto_nona_joven', 'east'), (0, 1, 3, 'casa_foto_nelida', 'east')]
# TV against the north wall, the Nona's empty rocking chair facing it
B += [(5, 0, 0, 'casa_tele_vieja', 'south'), (5, 0, 3, 'casa_mecedora', 'north')]
B += [(8, 0, 1, 'casa_estufa', 'west'), (3, 0, 0, 'casa_mesita_auxiliar', 'south'), (3, 1, 0, 'casa_carpetita_florero', 'south')]
SCENE = dict(blocks=B, camera=(7.8, 1.62, 6.6), target=(2.6, 0.8, 1.4), fov=72)
