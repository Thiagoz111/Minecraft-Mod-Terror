# Dormitorio (section 11x12): two rows of iron beds with trunks, 'bultos' under the sheets, nightstands, and at the
# north end the celadora's cubicle (white curtain, her chair facing the beds, nightstand with the hand bell).
import zlib


def h(*a):
    return zlib.crc32(repr(a).encode()) % 1000


B = []
W, D, H = 11, 12, 4
for x in range(0, W):
    for z in range(0, D):
        B.append((x, -1, z, 'colegio_tablas' if h(x, z) > 300 else 'colegio_tablas_gastadas', 'north'))
        B.append((x, H, z, 'colegio_cielorraso', 'north'))
for x in range(-1, W + 1):
    for y in range(0, H):
        for z in (-1, D):
            B.append((x, y, z, 'colegio_friso' if y == 0 else 'colegio_crema', 'north'))
for z in range(0, D):
    for y in range(0, H):
        for x in (-1, W):
            B.append((x, y, z, 'colegio_friso' if y == 0 else ('colegio_crema_marcas' if h(x, y, z) < 150 else 'colegio_crema'), 'north'))
west = ['', '_bulto', '_bulto', '_deshecha', '_bulto']
east = ['_bulto', '', '_bulto', '_bulto', '']
for n, z in enumerate((3, 5, 7, 9, 11)):
    B.append((0, 0, z, f'colegio_cama{west[n]}_cabecera', 'west'))
    B.append((1, 0, z, f'colegio_cama{west[n]}_pie', 'west'))
    B.append((2, 0, z, 'colegio_baul', 'east'))
    B.append((10, 0, z, f'colegio_cama{east[n]}_cabecera', 'east'))
    B.append((9, 0, z, f'colegio_cama{east[n]}_pie', 'east'))
    B.append((8, 0, z, 'colegio_baul', 'west'))
for z in (4, 8):
    B.append((0, 0, z, 'colegio_mesita_luz', 'east'))
    B.append((10, 0, z, 'colegio_mesita_luz', 'west'))
# the celadora's cubicle at the north end
for x in (3, 4, 6, 7):
    B.append((x, 0, 1, 'colegio_cortina_blanca', 'south'))
B.append((5, 0, 1, 'colegio_silla_monja', 'south'))
B.append((4, 0, 0, 'colegio_mesita_luz_campanita', 'south'))
B.append((5, 2, 0, 'colegio_crucifijo_chico', 'south'))
B.append((9, 0, 0, 'colegio_ropero_abajo', 'south'))
B.append((9, 1, 0, 'colegio_ropero_arriba', 'south'))
SCENE = dict(blocks=B, camera=(5.5, 1.62, 11.6), target=(5.3, 0.9, 1.0), fov=72)
