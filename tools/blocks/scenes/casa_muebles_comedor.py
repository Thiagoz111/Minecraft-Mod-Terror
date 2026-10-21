# Casa Morales - COMEDOR (7x6): the long lustred table (3 blocks) with its 8 matching chairs, the sideboard with the
# plates against the north wall, the brass three-arm lamp, one chair knocked over (after the tower).
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
room(B, W, D, H, lambda x, z: pick('casa_parquet_gastado', 'colegio_tablas_gastadas') if h(x, z) < 250 else pick('casa_parquet', 'colegio_tablas'),
     pick('casa_pared_living', 'colegio_revoque'), pick('casa_pared_living_zocalo', 'colegio_revoque_zocalo'),
     pick('casa_cielorraso', 'colegio_cielorraso'))
B += [(2, 0, 3, 'casa_mesa_comedor_extremo', 'north'), (3, 0, 3, 'casa_mesa_comedor_centro', 'north'),
      (4, 0, 3, 'casa_mesa_comedor_extremo', 'south')]
for x in (2, 3, 4):
    B += [(x, 0, 2, 'casa_silla_comedor', 'south'), (x, 0, 4, 'casa_silla_comedor', 'north')]
B += [(1, 0, 3, 'casa_silla_comedor', 'east'), (5, 0, 3, 'casa_silla_comedor', 'west')]
B = [b for b in B if b[:3] != (3, 0, 4)] + [(3, 0, 5, 'casa_silla_comedor_volcada', 'north')]
B += [(2, 0, 0, 'casa_aparador_izq', 'south'), (3, 0, 0, 'casa_aparador_der', 'south')]
B += [(3, 2, 3, 'casa_lampara_comedor', 'north'), (5, 2, 0, 'casa_reloj_cocina', 'south'), (0, 1, 2, 'casa_foto_nona_joven', 'east')]
SCENE = dict(blocks=B, camera=(6.4, 1.62, 5.6), target=(2.4, 0.8, 1.6), fov=72)
