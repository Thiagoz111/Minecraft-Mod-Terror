# Casa Morales - PATIO, the parrilla corner (cap. 5 'LE FALTA SAL'): brick parrilla against the back medianera with
# its hood and chimney, the knife board, counters with tongs and the bag of coarse salt, Jorge's chair facing the fire,
# the long table on trestles with plastic chairs, charcoal, beer crate, pots, the 'tortuga' wall lamp.
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
    for k in keys:
        if k in HAVE:
            return k
    return keys[-1]


B = []
W, D = 10, 8
FLOOR = pick('casa_ladrillo_patio', 'colegio_baldosa')
WALL = pick('casa_medianera', 'casa_ladrillo_visto', 'colegio_ladrillo')
for x in range(-1, W + 1):
    for z in range(-1, D):
        B.append((x, -1, z, FLOOR, 'north'))
for y in range(3):
    for x in range(-1, W + 1):
        B.append((x, y, D, WALL, 'north'))
    for z in range(-1, D):
        B.append((W, y, z, WALL, 'north'))
# the parrilla against the back wall, facing north (toward the house)
B += [(3, 0, D - 1, 'casa_parrilla_mesada_der', 'north'), (4, 0, D - 1, 'casa_parrilla', 'north'),
      (5, 0, D - 1, 'casa_parrilla_mesada_izq', 'north'), (6, 0, D - 1, 'casa_parrilla_mesada', 'north'),
      (2, 0, D - 1, 'casa_parrilla_mesada', 'north'),
      (4, 1, D - 1, 'casa_parrilla_campana', 'north'), (4, 2, D - 1, 'casa_parrilla_chimenea', 'north'),
      (3, 1, D - 1, 'casa_cuchillos', 'north'), (6, 1, D - 1, 'casa_pinza', 'north'), (2, 1, D - 1, 'casa_sal_gruesa', 'north'),
      (8, 2, D - 1, 'casa_aplique_patio', 'north'), (0, 2, D - 1, 'casa_aplique_patio_apagado', 'north')]
# Nona's salt circle (r ~3) in front of the parrilla (casa_estructura quarter pieces, if built)
if 'casa_sal_patio_a' in HAVE:
    PIECES = {'a': (0, 2), 'b': (1, 2), 'c': (2, 2), 'd': (2, 1), 'e': (2, 0), 'f': (1, 1)}
    CX, CZ = 5, 5
    for p_, (i, j) in PIECES.items():
        for (x, z, f) in ((CX + i, CZ + j, 'north'), (CX - 1 - j, CZ + i, 'east'), (CX - 1 - i, CZ - 1 - j, 'south'), (CX + j, CZ - 1 - i, 'west')):
            if z < D - 1:
                B.append((x, 0, z, 'casa_sal_patio_' + p_, f))
B += [(5, 0, 5, 'casa_silla_jorge', 'south'), (7, 0, D - 1, 'casa_bolsa_carbon', 'north'), (8, 0, D - 1, 'casa_cajon_cerveza', 'north'),
      (8, 0, 5, 'casa_bolsa_carbon_volcada', 'west'), (3, 0, 4, 'casa_cuchillo', 'east'), (6, 0, 3, 'casa_plato_roto', 'north')]
# long table on trestles along z with plastic chairs
B += [(1, 0, 0, 'casa_mesa_patio_extremo', 'east'), (1, 0, 1, 'casa_mesa_patio_centro', 'east'), (1, 0, 2, 'casa_mesa_patio_centro', 'east'),
      (1, 0, 3, 'casa_mesa_patio_extremo', 'west')]
B += [(0, 0, 1, 'casa_silla_plastica', 'east'), (0, 0, 3, 'casa_silla_plastica', 'east'), (2, 0, 0, 'casa_silla_plastica', 'west'),
      (2, 0, 2, 'casa_silla_plastica', 'west'), (9, 0, 5, 'casa_sillas_apiladas', 'west')]
B += [(9, 0, 0, 'casa_maceta_malvones', 'west'), (9, 0, 1, 'casa_maceta_lata', 'west'), (9, 0, 2, 'casa_macetas_grupo', 'west'),
      (8, 0, 2, 'casa_manguera', 'north')]
SCENE = dict(blocks=B, camera=(5.2, 1.62, 0.6), target=(4.0, 1.0, 7.0), fov=72)
