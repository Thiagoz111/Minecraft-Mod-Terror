# Casa Morales - LAVADERO during the blackout (cap. 2-3): the old breaker board with the knife lever DOWN, the cast
# granite laundry tub, the steel shelves (bleach, detergent; paint and tools), bucket and squeegee, the dead tube.
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
W, D, H = 5, 4, 3
room(B, W, D, H, pick('casa_cemento_piso', 'colegio_cemento'), pick('casa_cemento_lavadero', 'colegio_revoque'),
     pick('casa_zocalo_revoque', 'casa_cemento_lavadero'), pick('casa_cielorraso_humedad', 'casa_cielorraso', 'colegio_cielorraso'))
B += [(1, 1, 0, 'casa_tablero_apagado', 'south'), (3, 0, 0, 'casa_pileta_lavar', 'south'), (4, 0, 0, 'casa_balde_secador', 'south'),
      (0, 0, 2, 'casa_estante_lavadero', 'east'), (0, 0, 3, 'casa_estante_herramientas', 'east'), (2, 2, 2, 'casa_tubo_apagado', 'north'),
      (4, 0, 3, 'casa_cajon_cerveza', 'west')]
if 'casa_puerta_sotano' in HAVE:
    B.append((5, 0, 2, 'casa_puerta_sotano', 'west'))
SCENE = dict(blocks=B, camera=(4.3, 1.62, 3.5), target=(1.4, 1.2, 0.2), fov=74)
