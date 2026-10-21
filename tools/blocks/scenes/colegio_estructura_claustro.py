# Claustro: arcada de columnas toscanas y arcos de medio punto (luces de 3 bloques), galería de 3 de fondo con damero,
# muro del pasillo con ventanas enrejadas, tejado de tejas a un agua con alero sobre la arcada. Vista desde el patio.
import zlib


def h(*a):
    return zlib.crc32(repr(a).encode()) % 1000


B = []
X0, X1 = -4, 17
COLS = [x for x in range(X0, X1 + 1) if (x - X0) % 4 == 0]
for x in range(X0, X1 + 1):
    # courtyard paving in front (z < 0) and gallery floor
    for z in range(-9, 0):
        B.append((x, -1, z, 'colegio_patio_lajas', 'north'))
    for z in range(0, 5):
        B.append((x, -1, z, 'colegio_damero' if h(x, z) > 90 else 'colegio_damero_roto', 'north'))
    # arcade at z = 0
    if x in COLS:
        B += [(x, 0, 0, 'colegio_columna_base', 'north'), (x, 1, 0, 'colegio_columna_fuste', 'north'),
              (x, 2, 0, 'colegio_columna_capitel', 'north'), (x, 3, 0, 'colegio_revoque', 'north'),
              (x, 4, 0, 'colegio_revoque', 'north')]
    else:
        k = (x - X0) % 4  # 1, 2, 3
        if k == 1:
            B += [(x, 3, 0, 'colegio_arco_bajo_izq', 'north'), (x, 4, 0, 'colegio_arco_alto_izq', 'north')]
        elif k == 2:
            B += [(x, 4, 0, 'colegio_arco_alto_centro', 'north')]
        else:
            B += [(x, 3, 0, 'colegio_arco_bajo_der', 'north'), (x, 4, 0, 'colegio_arco_alto_der', 'north')]
    B.append((x, 5, 0, 'colegio_revoque_humedad' if h(x, 5) < 300 else 'colegio_revoque', 'north'))
    # gallery ceiling beams + boards
    for z in range(1, 4):
        B.append((x, 5, z, 'colegio_cielorraso_tablas', 'north'))
        if x % 2 == 0:
            B.append((x, 4, z, 'colegio_viga', 'north'))
    # corridor wall at z = 4 with windows every 4
    for y in range(0, 6):
        if x % 4 == 2 and 1 <= y <= 3:
            B.append((x, y, 4, ['colegio_ventana_inf', 'colegio_ventana_med', 'colegio_ventana_sup'][y - 1], 'north'))
        else:
            B.append((x, y, 4, 'colegio_revoque_salitre' if y == 0 else 'colegio_revoque', 'north'))
    # lean-to roof (1 in 2) from the arcade up to the corridor wall, eave over the courtyard
    B.append((x, 5, -1, 'colegio_alero', 'north'))
    B.append((x, 6, -1, 'colegio_tejas_losa', 'north'))
    B.append((x, 6, 0, 'colegio_tejas_losa', 'north:top'))
    B.append((x, 7, 1, 'colegio_tejas_losa', 'north'))
    B.append((x, 7, 2, 'colegio_tejas_losa', 'north:top'))
    B.append((x, 8, 3, 'colegio_tejas_losa', 'north'))
    B.append((x, 8, 4, 'colegio_tejas_losa', 'north:top'))
    for y in (6, 7):
        for z in range(1, 5):
            if (y == 6 and z >= 1) or (y == 7 and z >= 3):
                B.append((x, y, z, 'colegio_revoque', 'north'))
# dry fountain (5 x 5) in the courtyard, the chalk hopscotch beside it
FX, FZ = 4, -7
for dx in range(-2, 3):
    for dz in range(-2, 3):
        x, z = FX + dx, FZ + dz
        edge = abs(dx) == 2 or abs(dz) == 2
        if not edge:
            B.append((x, -1, z, 'colegio_fuente_fondo', 'north'))
            continue
        if abs(dx) == 2 and abs(dz) == 2:
            fac = {(2, 2): 'north', (-2, 2): 'east', (-2, -2): 'south', (2, -2): 'west'}[(dx, dz)]
            B.append((x, 0, z, 'colegio_fuente_esquina', fac))
        else:
            fac = 'north' if dz == 2 else 'south' if dz == -2 else ('west' if dx == 2 else 'east')
            B.append((x, 0, z, 'colegio_fuente_borde', fac))
B.append((FX, -1, FZ, 'colegio_piedra_fuente', 'north'))
B.append((FX, 0, FZ, 'colegio_fuente_pila', 'north'))
for i, (dx, dz, n) in enumerate([(0, 0, '1'), (0, -1, '2'), (0, -2, '3'), (-1, -3, '4'), (1, -3, '5'), (0, -4, '6'),
                                 (-1, -5, '7'), (1, -5, '8'), (0, -6, '9')]):
    B.append((11 + dx, 0, -1 + dz, 'colegio_rayuela_' + n, 'south'))
B.append((11, 0, -8, 'colegio_rayuela_cielo', 'south'))
SCENE = dict(blocks=B, camera=(-2.5, 1.7, -7.5), target=(7.0, 3.0, 1.5), fov=70)
