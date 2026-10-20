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
SCENE = dict(blocks=B, camera=(-2.5, 1.7, -7.5), target=(7.0, 3.0, 1.5), fov=70)
