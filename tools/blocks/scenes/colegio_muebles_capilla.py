# Capilla (partial nave, 11 wide): altar with cloth + crucifix, candlesticks, sanctuary lamp, pews, confessional,
# Virgin of Luján, Saint Agnes, baptismal font, stoup. Floor/walls from kit colegio_estructura.
import zlib


def h(*a):
    return zlib.crc32(repr(a).encode()) % 1000


B = []
X0, X1, D, H = -5, 5, 15, 7
for x in range(X0, X1 + 1):
    for z in range(0, D):
        B.append((x, -1, z, 'colegio_damero' if h(x, z) > 120 else 'colegio_damero_roto', 'north'))
for x in range(X0 - 1, X1 + 2):
    for y in range(0, H):
        B.append((x, y, -1, 'colegio_revoque' if h(x, y) > 250 else 'colegio_revoque_humedad', 'north'))
for x in range(X0 - 1, X1 + 2):
    for y in range(0, H):
        B.append((x, y, D, 'colegio_revoque', 'north'))
for z in range(0, D):
    for y in range(0, H):
        for x in (X0 - 1, X1 + 1):
            B.append((x, y, z, 'colegio_revoque_descascarado' if h(x, y, z) < 150 else 'colegio_revoque', 'north'))
# presbytery step + altar (front faces south, toward the pews)
for x in range(-2, 3):
    B.append((x, 0, 0, 'colegio_tarima', 'south'))
    B.append((x, 0, 2, 'colegio_tarima_borde', 'south'))
B.append((-1, 0, 1, 'colegio_altar_izq', 'south'))
B.append((0, 0, 1, 'colegio_altar_centro', 'south'))
B.append((1, 0, 1, 'colegio_altar_der', 'south'))
for x in (-2, 2):
    B.append((x, 0, 1, 'colegio_tarima', 'south'))
B.append((-1, 1, 1, 'colegio_candelero', 'south'))
B.append((1, 1, 1, 'colegio_candelero', 'south'))
B.append((0, 2, 0, 'colegio_crucifijo_grande', 'south'))
B.append((-3, 0, 1, 'colegio_candelabro', 'south'))
B.append((3, 0, 1, 'colegio_candelabro_apagado', 'south'))
B.append((2, 4, 3, 'colegio_lampara_santisimo', 'south'))
B.append((2, 5, 3, 'colegio_cadena', 'south'))
B.append((2, 6, 3, 'colegio_cadena', 'south'))
B.append((-4, 0, 1, 'colegio_virgen', 'south'))
B.append((4, 0, 1, 'colegio_santa_ines', 'south'))
B.append((-3, 0, 2, 'colegio_velas', 'south'))
# pews: two blocks of 3 (aisle at x=0), sitter looks north
for z in range(4, 12, 2):
    for (xa, xb) in ((-4, -1), (1, 4)):
        B.append((xa, 0, z, 'colegio_banco_iglesia_izq', 'north'))
        for x in range(xa + 1, xb):
            B.append((x, 0, z, 'colegio_banco_iglesia_centro', 'north'))
        B.append((xb, 0, z, 'colegio_banco_iglesia_der', 'north'))
# confessional on the west wall (front faces east)
for r, rn in ((0, 'abajo'), (1, 'arriba')):
    B.append((-5, r, 12, f'colegio_confesionario_izq_{rn}', 'east'))
    B.append((-5, r, 13, f'colegio_confesionario_centro_{rn}', 'east'))
    B.append((-5, r, 14, f'colegio_confesionario_der_{rn}', 'east'))
B.append((4, 0, 13, 'colegio_pila_bautismal', 'north'))
B.append((5, 1, 11, 'colegio_pila_agua_bendita', 'west'))
B.append((4, 0, 3, 'colegio_reclinatorio', 'north'))
SCENE = dict(blocks=B, camera=(0.5, 1.65, 14.2), target=(0.0, 1.4, 0.0), fov=72)
