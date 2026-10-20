# Capilla (lo único gótico del colegio): nave de sillería, banda de arquería ciega, moldura corrida, vitrales de
# lanceta (Santa Inés y geométricos), rosetón sobre la puerta doble, lápidas en el piso. Vista desde el altar
# hacia la entrada.
import zlib


def h(*a):
    return zlib.crc32(repr(a).encode()) % 1000


B = []
W0, W1 = -4, 4   # interior x range
L = 16           # z from 0 (entrance) to L (altar)
H = 9
for z in range(0, L + 1):
    for x in range(W0, W1 + 1):
        key = 'colegio_piso_capilla'
        if x == 0 and z in (6, 10):
            key = 'colegio_lapida_piso'
        B.append((x, -1, z, key, 'north'))
        B.append((x, H, z, 'colegio_cielorraso_tablas', 'north'))
        if z % 3 == 1:
            B.append((x, H - 1, z, 'colegio_viga', 'east'))
    for x in (W0 - 1, W1 + 1):
        for y in range(0, H):
            fac = 'east' if x < 0 else 'west'
            win = z in (4, 8, 12)
            if win and 2 <= y <= 4:
                nm = 'ines' if z == 8 else 'geo'
                B.append((x, y, z, f'colegio_vitral_{nm}_' + ['inf', 'med', 'sup'][y - 2], fac))
                continue
            key = 'colegio_sillar'
            if y == 1:
                key = 'colegio_sillar_tallado'
            elif y == 6:
                key = 'colegio_sillar_moldura'
            B.append((x, y, z, key, 'north'))
# entrance wall (z = -1): double door, rose window above
for x in range(W0 - 1, W1 + 2):
    for y in range(0, H):
        if x in (0, 1) and y == 0:
            B.append((x, y, -1, 'colegio_puerta_capilla', 'north'))
            continue
        if x in (0, 1) and y == 1:
            continue
        if x in (0, 1) and y in (4, 5):
            gx = 0 if x == 1 else 1   # seen from the nave (looking -z) the left piece is at higher x
            gy = 0 if y == 5 else 1
            B.append((x, y, -1, 'colegio_roseton_' + ['sup', 'inf'][gy] + '_' + ['izq', 'der'][gx], 'south'))
            continue
        B.append((x, y, -1, 'colegio_sillar_moldura' if y == 6 else 'colegio_sillar', 'north'))
SCENE = dict(blocks=B, camera=(0.5, 1.7, 14.5), target=(0.6, 3.2, -1.0), fov=72)
