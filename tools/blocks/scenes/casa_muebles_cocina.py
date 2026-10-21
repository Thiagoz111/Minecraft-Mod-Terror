# Casa Morales - COCINA (7x6): counters on the north wall (fridge, drawers, sink, stove with the kettle on, plain
# counter), wall cupboards above, mate+termo / panera / dish rack on the counter, the 3:33 clock, the gingham table
# with breakfast and four chrome chairs, fluorescent tube.
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


def kwall(x, y, z):
    if z == -1 and y in (1, 2):
        return pick('casa_azulejo_verde', 'colegio_azulejo')
    if z == -1 and y == 0:
        return pick('casa_azulejo_verde_guarda', 'colegio_azulejo_guarda')
    return None


room(B, W, D, H, pick('casa_ceramica_cocina', 'colegio_baldosa_colorada'), pick('casa_pared_cocina', 'colegio_revoque'),
     pick('casa_pared_cocina', 'colegio_revoque_zocalo'), pick('casa_cielorraso', 'colegio_cielorraso'), walls=kwall)
B += [(0, 0, 0, 'casa_heladera_abajo', 'south'), (0, 1, 0, 'casa_heladera_arriba', 'south'),
      (1, 0, 0, 'casa_mesada_cajones', 'south'), (2, 0, 0, 'casa_mesada_pileta', 'south'), (3, 0, 0, 'casa_mesada', 'south'),
      (4, 0, 0, 'casa_cocina_gas_pava', 'south'), (5, 0, 0, 'casa_mesada', 'south'), (6, 0, 0, 'casa_mesada_esquina', 'south'),
      (6, 0, 1, 'casa_mesada', 'west')]
B += [(1, 1, 0, 'casa_panera', 'south'), (3, 1, 0, 'casa_mate_termo', 'south'), (5, 1, 0, 'casa_escurridor', 'south')]
B += [(1, 2, 0, 'casa_alacena', 'south'), (3, 2, 0, 'casa_alacena_abierta', 'south'), (5, 2, 0, 'casa_alacena', 'south'),
      (6, 2, 0, 'casa_alacena', 'south')]
B += [(6, 2, 3, 'casa_reloj_cocina_333', 'west')]
B += [(3, 0, 3, 'casa_mesa_cocina', 'north'), (3, 1, 3, 'casa_desayuno', 'north'),
      (3, 0, 2, 'casa_silla_cocina', 'south'), (3, 0, 4, 'casa_silla_cocina', 'north'), (2, 0, 3, 'casa_silla_cocina', 'east'),
      (4, 0, 3, 'casa_silla_cocina', 'west'), (0, 0, 5, 'casa_tacho_basura', 'east')]
B += [(3, 2, 2, 'casa_tubo', 'north')]
SCENE = dict(blocks=B, camera=(0.6, 1.62, 5.4), target=(4.0, 1.0, 0.4), fov=72)
