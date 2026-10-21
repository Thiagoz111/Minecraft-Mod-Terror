# Casa Morales - DORMITORIO PRINCIPAL (7x6, upstairs): the lustred double bed with the quilted satin bedspread, the
# two nightstands with their lamps, the dresser with the tall mirror, a fixed louvred placard, the crucifix, Marta's
# robe and Jorge's apron on the hook.
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
W, D, H = 7, 6, 3
room(B, W, D, H, lambda x, z: pick('casa_parquet', 'colegio_tablas'), pick('casa_empapelado_matrimonial', 'colegio_revoque'),
     pick('casa_empapelado_matrimonial_zocalo', 'colegio_revoque_zocalo'), pick('casa_cielorraso', 'colegio_cielorraso'))
B += [(2, 0, 0, 'casa_cama_matrimonial_cabecera_izq', 'south'), (3, 0, 0, 'casa_cama_matrimonial_cabecera_der', 'south'),
      (2, 0, 1, 'casa_cama_matrimonial_pie_izq', 'south'), (3, 0, 1, 'casa_cama_matrimonial_pie_der', 'south')]
B += [(1, 0, 0, 'casa_mesa_luz', 'south'), (1, 1, 0, 'casa_velador', 'south'), (4, 0, 0, 'casa_mesa_luz', 'south'),
      (4, 1, 0, 'casa_velador_apagado', 'south'), (2, 2, 0, 'casa_crucifijo', 'south')]
B += [(6, 0, 2, 'casa_comoda_izq', 'west'), (6, 0, 3, 'casa_comoda_der', 'west')]
B += [(0, 0, 2, 'casa_placard_cerrado_der', 'east'), (0, 0, 3, 'casa_placard_cerrado_izq', 'east'),
      (0, 2, 2, 'casa_placard_maletero_der', 'east'), (0, 2, 3, 'casa_placard_maletero_izq', 'east')]
B += [(5, 1, 5, 'casa_perchero_bata', 'north'), (3, 2, 3, 'casa_plafon_apagado', 'north'), (5, 0, 1, 'casa_pantuflas', 'south')]
SCENE = dict(blocks=B, camera=(1.7, 1.62, 5.5), target=(4.8, 0.95, 1.8), fov=78)   # bed + the one-piece dresser mirror
