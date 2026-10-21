# Casa Morales - SOTANO (before the break): the basement (9 x 7, 4 high) under the laundry. Cement floor, raw concrete
# slab, grey-ochre lime plaster gone damp (rotten foot along the floor, brick showing where it fell), cement steps
# coming down from the laundry with the galvanised pipe handrail, the ventiluz at patio level, and the CRACK in the
# back wall (towards the sealed 1961 room) leaking sand. A few casa_muebles props (boiler, covered furniture, bulb).
import zlib


def h(*a):
    return zlib.crc32(repr(a).encode()) % 1000


B = []
W, D, H = 9, 7, 4
for x in range(-1, W + 1):
    for z in range(-1, D + 1):
        B.append((x, -1, z, 'casa_cemento_piso', 'north'))
        if not (x == 8 and z in (0, 1)):
            B.append((x, H, z, 'casa_losa_sotano', 'north'))


def wall(x, y, z):
    if y == 0:
        return 'casa_pared_sotano_zocalo'
    return 'casa_pared_sotano_ladrillo' if x == W else 'casa_pared_sotano'


for y in range(H):
    for x in range(-1, W + 1):
        B.append((x, y, -1, wall(x, y, -1), 'north'))
        if x == 4 and y < 3:
            B.append((x, y, D, ('casa_pared_sotano_grieta_abajo', 'casa_pared_sotano_grieta', 'casa_pared_sotano_grieta_arriba')[y], 'north'))
        else:
            B.append((x, y, D, wall(x, y, D), 'north'))
    for z in range(D):
        if (y, z) == (3, 3):
            B.append((-1, y, z, 'casa_ventana_sotano', 'west'))
        else:
            B.append((-1, y, z, wall(-1, y, z), 'north'))
        B.append((W, y, z, wall(W, y, z), 'north'))
# cement steps down from the laundry along the east wall (low side towards +z) and the pipe handrail
for k, (y, z) in enumerate(((3, 0), (2, 1), (1, 2), (0, 3))):
    B.append((8, y, z, 'casa_escalon_cemento', 'south'))
    for yy in range(y):
        B.append((8, yy, z, 'casa_cemento_piso', 'north'))
    if y + 1 < H:
        B.append((8, y + 1, z, 'casa_pasamanos_der', 'south'))
# props (casa_muebles)
B += [(0, 0, 6, 'casa_caldera', 'east'), (4, 3, 3, 'casa_foco', 'north'), (1, 0, 1, 'casa_tapado_sillon', 'east'),
      (0, 0, 3, 'casa_estante_frascos', 'east'), (6, 0, 6, 'casa_cajas_apiladas', 'north'), (2, 0, 6, 'casa_tapado_ropero', 'north')]
SCENE = dict(blocks=B, camera=(7.2, 1.55, 0.9), target=(3.6, 1.2, 7.0), fov=72)
