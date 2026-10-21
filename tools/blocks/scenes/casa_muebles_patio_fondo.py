# Casa Morales - PATIO, the far end seen from the kitchen door (cap. 4 'La cucha'): Choripan's cucha with his bowls,
# the lemon tree, the murky pelopincho (no cover), the clothesline with sheets (one has something behind it).
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
X0, X1, Z0, Z1 = -7, 10, -2, 11
GRASS = pick('casa_cesped', 'colegio_cesped')
DIRT = pick('casa_tierra', 'colegio_tierra')
WALL = pick('casa_medianera', 'casa_ladrillo_visto', 'colegio_ladrillo')
for x in range(X0, X1 + 1):
    for z in range(Z0, Z1):
        B.append((x, -1, z, DIRT if (h(x, z) < 160 or (3 <= x <= 5 and 5 <= z <= 7)) else GRASS, 'north'))
for y in range(3):
    for x in range(X0, X1 + 1):
        B.append((x, y, Z1, WALL, 'north'))
    for z in range(Z0, Z1):
        B.append((X0, y, z, WALL, 'north'))
        B.append((X1, y, z, WALL, 'north'))
# pelopincho 4x3 (x -5..-2, z 3..5)
B += [(-5, 0, 5, 'casa_pelopincho_esquina', 'east'), (-4, 0, 5, 'casa_pelopincho_borde', 'north'), (-3, 0, 5, 'casa_pelopincho_borde', 'north'),
      (-2, 0, 5, 'casa_pelopincho_esquina', 'north'),
      (-5, 0, 4, 'casa_pelopincho_borde', 'east'), (-4, 0, 4, 'casa_pelopincho_agua', 'north'), (-3, 0, 4, 'casa_pelopincho_agua_pelota', 'east'),
      (-2, 0, 4, 'casa_pelopincho_borde', 'west'),
      (-5, 0, 3, 'casa_pelopincho_esquina', 'south'), (-4, 0, 3, 'casa_pelopincho_borde', 'south'), (-3, 0, 3, 'casa_pelopincho_borde', 'south'),
      (-2, 0, 3, 'casa_pelopincho_esquina', 'west')]
# clothesline along x at z=8
B += [(-6, 0, 8, 'casa_tendedero_poste', 'north'), (1, 0, 8, 'casa_tendedero_poste', 'north')]
for n, k in enumerate(('casa_sabana_blanca', 'casa_sabana_floreada', 'casa_sabana_silueta', 'casa_ropa_tendida', 'casa_sabana_rosa', 'casa_soga')):
    B.append((-5 + n, 0, 8, k, 'north'))
# the cucha, bowls, the lemon tree
B += [(4, 0, 7, 'casa_cucha', 'north'), (5, 0, 6, 'casa_platos_perro', 'north'), (3, 0, 6, 'casa_pelota', 'north')]
B += [(8, 0, 8, 'casa_limonero_tronco', 'north'), (8, 1, 8, 'casa_limonero_ramas', 'north'), (7, 0, 7, 'casa_limones_piso', 'north'),
      (9, 0, 9, 'casa_limones_piso', 'east')]
for dx in (-1, 0, 1):
    for dz in (-1, 0, 1):
        B.append((8 + dx, 2, 8 + dz, 'casa_limonero_copa_limones' if (dx + dz) % 2 else 'casa_limonero_copa', 'north'))
B += [(8, 3, 8, 'casa_limonero_copa_limones', 'north'), (7, 3, 8, 'casa_limonero_copa', 'north'), (8, 3, 9, 'casa_limonero_copa', 'north')]
B += [(9, 0, 1, 'casa_maceta_malvones', 'west'), (9, 0, 2, 'casa_maceta_malvones', 'west'), (-6, 0, 1, 'casa_maceta_lata', 'east')]
SCENE = dict(blocks=B, camera=(0.4, 1.62, 5.0), target=(-2.8, 1.15, 8.0), fov=72)   # close on the line and the silhouette
