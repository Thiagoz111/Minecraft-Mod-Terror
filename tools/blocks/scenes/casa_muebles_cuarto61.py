# Casa Morales - THE 1961 ROOM (cap. 7, the boss): the iron bed with leather straps, puddles of melted candles burning,
# Father Anselmo's stole on a nail, the old rusted cookie tin, the little patent shoes, the missal open on the floor,
# the Nona's rocking chair in the middle (she floats in it). Walls / sand / salt circle from casa_estructura.
import glob
import json
import os
import zlib


def h(*a):
    return zlib.crc32(repr(a).encode()) % 1000


def _have():
    keys = set()
    for p in glob.glob(os.path.join("tools", "blocks", "out", "preview_*.json")):
        try:
            d = json.load(open(p))
        except Exception:
            continue
        keys |= set(d.get("models", {})) | set(d.get("cubes", {}))
    return keys


HAVE = _have()


def pick(*keys):
    for k in keys:
        if k in HAVE:
            return k
    return keys[-1]


def room(B, W, D, H, floor, wall, base, ceil, walls=None):
    """Floor at y=-1, ceiling at y=H, walls around (walls(x, y, z) may override a wall block)."""
    for x in range(W):
        for z in range(D):
            B.append((x, -1, z, floor(x, z) if callable(floor) else floor, "north"))
            if ceil:
                B.append((x, H, z, ceil, "north"))
    for y in range(H):
        for x in range(-1, W + 1):
            for z in (-1, D):
                k = (walls(x, y, z) if walls else None) or (base if y == 0 else wall)
                B.append((x, y, z, k, "north"))
        for z in range(D):
            for x in (-1, W):
                k = (walls(x, y, z) if walls else None) or (base if y == 0 else wall)
                B.append((x, y, z, k, "north"))


B = []
W, D, H = 7, 7, 4


def walls(x, y, z):
    if x == W and z == 2:
        return pick(('casa_pared_61_hollin', 'casa_pared_61_hollin_alto', 'casa_pared_61_hollin_alto', 'casa_pared_61')[y], 'casa_pared_61')
    return None


room(B, W, D, H, pick('casa_arena', 'casa_cemento_piso'), pick('casa_pared_61', 'casa_pared_sotano', 'colegio_revoque'),
     pick('casa_pared_61_zocalo', 'casa_pared_sotano_zocalo', 'colegio_revoque_zocalo'), pick('casa_losa_sotano', 'colegio_cielorraso'), walls)
B += [(3, 0, 4, 'casa_cama_hierro_cabecera', 'south'), (3, 0, 5, 'casa_cama_hierro_pie', 'south'),
      (1, 0, 5, 'casa_velas_derretidas', 'north'), (5, 0, 6, 'casa_velas_derretidas', 'west'), (5, 0, 3, 'casa_velas_sueltas', 'north'),
      (1, 0, 2, 'casa_velas_sueltas_apagadas', 'east'), (6, 0, 0, 'casa_velas_derretidas_apagadas', 'south'),
      (0, 1, 3, 'casa_estola_anselmo', 'east'), (2, 0, 2, 'casa_lata_galletitas_vieja', 'north'), (4, 0, 6, 'casa_zapatitos', 'north'),
      (4, 0, 2, 'casa_misal', 'north'), (3, 0, 2, 'casa_mecedora', 'north')]
for (x, z, k) in ((6, 4, 'casa_rayones_lemaza'), (6, 6, 'casa_rayones_lemaza_chico')):
    if k in HAVE:
        B.append((x, 0, z, k, 'west'))
SCENE = dict(blocks=B, camera=(5.8, 1.62, 0.2), target=(2.4, 0.6, 4.6), fov=74)
