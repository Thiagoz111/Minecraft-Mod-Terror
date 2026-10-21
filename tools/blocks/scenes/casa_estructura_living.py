# Casa Morales - LIVING (9x7, 3 high): herringbone parquet (worn on the walking path), beige walls with picture rail
# and skirting, plaster ceiling with a damp stain. Structure only (furniture lives in casa_muebles scenes).
import zlib


def h(*a):
    return zlib.crc32(repr(a).encode()) % 1000


B = []
W, D, H = 9, 7, 3


def wall_key(x, y, z):
    if y == 0:
        return 'casa_pared_living_zocalo'
    if y == H - 1:
        return 'casa_pared_living_moldura'
    return 'casa_pared_living'


for x in range(W):
    for z in range(D):
        worn = (2 <= x <= 6 and 2 <= z <= 4) and h(x, z) < 600
        B.append((x, -1, z, 'casa_parquet_gastado' if worn else 'casa_parquet', 'north'))
        B.append((x, H, z, 'casa_cielorraso_humedad' if (x, z) == (6, 1) else 'casa_cielorraso', 'north'))
for y in range(H):
    for x in range(-1, W + 1):
        for z in (-1, D):
            B.append((x, y, z, wall_key(x, y, z), 'north'))
    for z in range(D):
        for x in (-1, W):
            B.append((x, y, z, wall_key(x, y, z), 'north'))
SCENE = dict(blocks=B, camera=(7.6, 1.62, 6.3), target=(1.5, 1.0, 0.5), fov=72)
