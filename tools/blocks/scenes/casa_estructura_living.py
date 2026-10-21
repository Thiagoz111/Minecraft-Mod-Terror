# Casa Morales - LIVING (9x7, 3 high): herringbone parquet (worn on the walking path), beige walls with picture rail
# and skirting, cornice and ceiling rose, the street window (2x2, blind half down) on the north wall, the hall door
# with its casing, switch and outlet, and Jorge's 'humedad' climbing the north wall ('Es la humedad, flaco').
# Structure only (furniture lives in casa_muebles scenes).
import zlib


def h(*a):
    return zlib.crc32(repr(a).encode()) % 1000


B = []
W, D, H = 9, 7, 3
WIN = {(5, 1): 'casa_ventana_inf_izq', (4, 1): 'casa_ventana_inf_der', (5, 2): 'casa_ventana_sup_izq_cerrada', (4, 2): 'casa_ventana_sup_der_cerrada'}


def wall_key(x, y, z):
    if y == 0:
        return 'casa_pared_living_zocalo'
    if y == H - 1:
        return 'casa_pared_living_moldura'
    return 'casa_pared_living'


for x in range(-1, W + 1):
    for z in range(-1, D + 1):
        worn = (2 <= x <= 6 and 2 <= z <= 4) and h(x, z) < 600
        B.append((x, -1, z, 'casa_parquet_gastado' if worn else 'casa_parquet', 'north'))
        B.append((x, H, z, 'casa_cielorraso_humedad' if (x, z) == (6, 1) else 'casa_cielorraso', 'north'))
for y in range(H):
    for x in range(-1, W + 1):
        if (x, y) in WIN:
            B.append((x, y, -1, WIN[(x, y)], 'north'))
        else:
            B.append((x, y, -1, wall_key(x, y, -1), 'north'))
        if not (x == 4 and y < 2):
            B.append((x, y, D, wall_key(x, y, D), 'north'))
    for z in range(D):
        for x in (-1, W):
            B.append((x, y, z, wall_key(x, y, z), 'north'))
# cornice all round, rose in the middle of the ceiling
for x in range(W):
    B += [(x, 2, 0, 'casa_cornisa', 'south'), (x, 2, D - 1, 'casa_cornisa', 'north')]
for z in range(1, D - 1):
    B += [(0, 2, z, 'casa_cornisa', 'east'), (W - 1, 2, z, 'casa_cornisa', 'west')]
# inner corners: casa_cornisa_esquina_der has its walls BEHIND and on the RIGHT of a viewer looking at its front, so
# NW faces east, NE south, SE west, SW north (_izq: walls behind and on the LEFT -> NW south, NE west, SE north, SW east)
B += [(0, 2, 0, 'casa_cornisa_esquina_der', 'east'), (W - 1, 2, 0, 'casa_cornisa_esquina_der', 'south'),
      (W - 1, 2, D - 1, 'casa_cornisa_esquina_der', 'west'), (0, 2, D - 1, 'casa_cornisa_esquina_izq', 'east'), (4, 2, 3, 'casa_roseton', 'north')]
# the hall door in the south wall (x = 4): casing, switch beside it, outlet
B += [(5, 1, D - 1, 'casa_contramarco_izq', 'north'), (3, 1, D - 1, 'casa_contramarco_der', 'north'), (4, 2, D - 1, 'casa_contramarco_dintel', 'north'),
      (6, 1, D - 1, 'casa_llave_luz', 'north'), (8, 0, 4, 'casa_enchufe', 'west')]
B += [(4, -1, D, 'casa_granitico', 'north')]
# the damp stain climbing the north wall beside the window, behind where Jorge's armchair goes (on the north wall the
# preview shades decal and wall alike; brender shades a rotated decal by its model face, Minecraft by its real side)
B += [(2, 0, 0, 'casa_mancha_humedad', 'south')]
SCENE = dict(blocks=B, camera=(7.4, 1.62, 5.9), target=(1.0, 1.0, 1.2), fov=74)
