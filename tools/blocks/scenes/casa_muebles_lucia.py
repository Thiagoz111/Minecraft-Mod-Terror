# Casa Morales - CUARTO DE LUCIA (6x6, upstairs): pink canopy bed, the white bookcases with the porcelain dolls on the
# east wall, her desk with the tablet playing Tomi's VOD, the round rug, the notebook open on the floor (LEMAZA), the
# crayon drawing on the wall, the toy chest.
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
WALL = pick('casa_pared_lucia', 'colegio_revoque')
room(B, W, D, H, lambda x, z: pick('casa_parquet', 'colegio_tablas'), WALL, pick('casa_pared_lucia_zocalo', 'colegio_revoque_zocalo'),
     pick('casa_cielorraso', 'colegio_cielorraso'),
     walls=lambda x, y, z: pick('casa_pared_lucia_stickers', 'casa_pared_lucia') if (x == -1 and y == 1 and z in (1, 2)) else None)
B += [(1, 0, 0, 'casa_cama_dosel_cabecera', 'south'), (1, 0, 1, 'casa_cama_dosel_pie', 'south'),
      (0, 0, 0, 'casa_mesa_luz', 'south'), (0, 1, 0, 'casa_lampara_hongo', 'south')]
B += [(5, 0, 1, 'casa_estante_munecas_1', 'west'), (5, 0, 2, 'casa_estante_munecas_2', 'west'), (5, 0, 3, 'casa_estante_munecas_3', 'west')]
B += [(3, 0, 0, 'casa_escritorio_lucia', 'south'), (3, 0, 1, 'casa_silla_nena', 'north')]
B += [(2, 0, 2, 'casa_alfombra_lucia', 'north'), (3, 0, 2, 'casa_alfombra_lucia', 'east'), (2, 0, 3, 'casa_alfombra_lucia', 'west'),
      (3, 0, 3, 'casa_alfombra_lucia', 'south'), (2, 0, 3, 'casa_cuaderno_lemaza', 'east')]
B += [(0, 0, 4, 'casa_baul_juguetes', 'east'), (0, 0, 3, 'casa_dibujo_lemaza', 'east'), (4, 0, 4, 'casa_mochila', 'west'),
      (1, 0, 4, 'casa_juguetes', 'north'), (3, 2, 3, 'casa_plafon_apagado', 'north')]
SCENE = dict(blocks=B, camera=(4.6, 1.62, 5.6), target=(1.8, 0.8, 1.2), fov=76)
