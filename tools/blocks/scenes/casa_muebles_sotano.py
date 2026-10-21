# Casa Morales - SOTANO (cap. 7): furniture under yellowed dust sheets (one of them has shoulders), the Nona's
# preserves, the demijohn, boxes, the old boiler with its blue pilot, a bare bulb on a cord; the cracked wall behind.
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
W, D, H = 8, 7, 3


def walls(x, y, z):
    if z == D and x == 3:
        return pick(('casa_pared_sotano_grieta_abajo', 'casa_pared_sotano_grieta', 'casa_pared_sotano_grieta_arriba')[y], 'casa_pared_sotano')
    if x == W:
        return pick('casa_pared_sotano_ladrillo', 'casa_pared_sotano') if y else None
    return None


room(B, W, D, H, pick('casa_cemento_piso', 'colegio_cemento'), pick('casa_pared_sotano', 'colegio_revoque'),
     pick('casa_pared_sotano_zocalo', 'colegio_revoque_zocalo'), pick('casa_losa_sotano', 'colegio_cielorraso'), walls)
B += [(0, 0, 5, 'casa_caldera', 'east'), (0, 0, 6, 'casa_damajuana', 'east'),
      (0, 0, 2, 'casa_estante_frascos', 'east'), (0, 0, 3, 'casa_estante_frascos_2', 'east'),
      (1, 0, 0, 'casa_tapado_sillon', 'south'), (3, 0, 3, 'casa_tapado_mesa', 'north'), (5, 0, 6, 'casa_tapado_figura', 'north'),
      (2, 0, 6, 'casa_tapado_ropero', 'north'), (7, 0, 3, 'casa_tapado_espejo', 'west'),
      (6, 0, 6, 'casa_cajas_apiladas', 'north'), (7, 0, 6, 'casa_cajas_apiladas', 'west'), (4, 0, 5, 'casa_caja_abierta', 'north'),
      (3, 2, 2, 'casa_foco', 'north'), (6, 0, 0, 'casa_balde_secador', 'south')]
SCENE = dict(blocks=B, camera=(7.3, 1.6, 0.4), target=(2.6, 0.8, 5.0), fov=74)
