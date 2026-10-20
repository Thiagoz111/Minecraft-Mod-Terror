# Aula de 6° (9x7): pizarrón 5x2 "NO DEBO HABLAR EN CLASE" on the north wall, tarima + escritorio, pupitres dobles,
# a few separate chairs (one turned toward the camera), crucifix, map. Walls/floor from kit colegio_estructura.
import zlib


def h(*a):
    return zlib.crc32(repr(a).encode()) % 1000


BOARD = globals().get('BOARD', 'nodebo')
B = []
W, D, H = 9, 7, 4
for x in range(0, W):
    for z in range(0, D):
        B.append((x, -1, z, 'colegio_tablas' if h(x, z) > 200 else 'colegio_tablas_gastadas', 'north'))
        B.append((x, H, z, 'colegio_cielorraso_tablas', 'north'))
for x in range(-1, W + 1):
    for y in range(0, H):
        for z in (-1, D):
            B.append((x, y, z, 'colegio_friso' if y == 0 else 'colegio_crema', 'north'))
for z in range(0, D):
    for y in range(0, H):
        for x in (-1, W):
            B.append((x, y, z, 'colegio_friso' if y == 0 else ('colegio_crema_marcas' if h(x, y, z) < 200 else 'colegio_crema'), 'north'))

# --- front: tarima along the board, board 5x2 centred, teacher desk + chair
for x in range(1, 8):
    B.append((x, 0, 0, 'colegio_tarima', 'south'))
    B.append((x, 0, 1, 'colegio_tarima_borde', 'south'))
B[:] = [b for b in B if not (b[1] == 0 and b[2] in (0, 1) and b[0] in (5, 6))]
B.append((6, 0, 1, 'colegio_escritorio_maestra_izq', 'south'))   # teacher looks south: her left is east
B.append((5, 0, 1, 'colegio_escritorio_maestra_der', 'south'))
B.append((5, 0, 0, 'colegio_silla_maestra', 'south'))
B.append((6, 0, 0, 'colegio_tarima', 'south'))
for c in range(5):
    x = 2 + c
    for r in range(2):
        if BOARD == 'blank':
            cn = 'izq' if c == 0 else ('der' if c == 4 else 'centro')
            B.append((x, 2 - r, 0, f'colegio_pizarron_{"arriba" if r == 0 else "abajo"}_{cn}', 'south'))
        else:
            B.append((x, 2 - r, 0, f'colegio_pizarron_{BOARD}_{c + 1}_{r + 1}', 'south'))
B.append((4, 3, 0, 'colegio_crucifijo_chico', 'south'))
B.append((-0, 2, 3, 'colegio_mapa_argentina', 'east'))

# --- pupils: double desks facing north (pupil looks at the board); left half at the smaller x
for (x0, z) in ((0, 3), (3, 3), (6, 3), (0, 4), (3, 4), (0, 5), (6, 5)):
    B.append((x0, 0, z, 'colegio_pupitre_doble_izq', 'north'))
    B.append((x0 + 1, 0, z, 'colegio_pupitre_doble_der', 'north'))
# a desk without its bench + two loose chairs, one turned to stare at the door/camera
B.append((3, 0, 5, 'colegio_pupitre_mesa_izq', 'north'))
B.append((4, 0, 5, 'colegio_pupitre_mesa_der', 'north'))
B.append((3, 0, 6, 'colegio_silla_escolar', 'north'))
B.append((4, 0, 6, 'colegio_silla_escolar', 'south'))
B.append((7, 0, 4, 'colegio_silla_escolar', 'west'))

SCENE = dict(blocks=B, camera=(7.6, 1.62, 6.6), target=(3.0, 1.1, 0.2), fov=72)
