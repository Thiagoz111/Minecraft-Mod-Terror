# Casa Morales - BANO (4x4): built-in tub with the shower curtain along the north wall (taps at the west end), toilet
# and bidet on the west wall, pedestal basin with the medicine cabinet on the east wall. Celeste tiles to 2 m.
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
W, D, H = 4, 4, 3
TILE = pick('casa_azulejo_celeste', 'colegio_azulejo')
room(B, W, D, H, pick('casa_granitico', 'colegio_baldosa_colorada'), pick('casa_pared_bano', 'colegio_revoque'), TILE,
     pick('casa_cielorraso_humedad', 'colegio_cielorraso'),
     walls=lambda x, y, z: TILE if y == 1 else (pick('casa_azulejo_celeste_guarda', 'casa_azulejo_celeste') if y == 2 else None))
B += [(0, 0, 0, 'casa_banadera_izq', 'south'), (1, 0, 0, 'casa_banadera_der', 'south'),
      (0, 1, 0, 'casa_cortina_ducha_corrida', 'south'), (1, 1, 0, 'casa_cortina_ducha', 'south'), (0, 1, 0, 'casa_ducha', 'east')]
B += [(0, 0, 2, 'casa_inodoro', 'east'), (0, 0, 3, 'casa_bidet', 'east'), (0, 0, 1, 'casa_portarrollo', 'east'),
      (1, 0, 1, 'casa_alfombra_bano', 'south')]
B += [(3, 0, 1, 'casa_lavatorio', 'west'), (3, 1, 1, 'casa_botiquin', 'west'), (3, 2, 1, 'casa_aplique_bano', 'west'),
      (3, 1, 3, 'casa_toallero', 'west'), (2, 2, 2, 'casa_plafon', 'north')]
SCENE = dict(blocks=B, camera=(3.0, 1.62, 3.85), target=(0.6, 0.9, 0.6), fov=78)
