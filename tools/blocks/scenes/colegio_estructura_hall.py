# Hall de doble altura: damero, friso de madera oscura, revoque a la cal con cornisa, escalera principal de madera
# oscura de 3 de ancho que sube al balcón del primer piso con baranda torneada y poste; vigas y cielorraso.
import zlib


def h(*a):
    return zlib.crc32(repr(a).encode()) % 1000


B = []
X0, X1, Z0, Z1, H = -5, 5, 0, 8, 10
for x in range(X0, X1 + 1):
    for z in range(Z0, Z1 + 1):
        B.append((x, -1, z, 'colegio_damero_roto' if h(x, z) < 90 else 'colegio_damero', 'north'))
        B.append((x, H, z, 'colegio_cielorraso', 'north'))
        if z % 3 == 1:
            B.append((x, H - 1, z, 'colegio_viga', 'east'))
# walls
for y in range(0, H):
    for z in range(Z0, Z1 + 1):
        for x in (X0 - 1, X1 + 1):
            key = 'colegio_friso' if y == 0 else 'colegio_revoque_humedad' if (y == H - 1 and h(x, z) < 300) else 'colegio_revoque'
            if y == 6:
                key = 'colegio_friso'
            B.append((x, y, z, key, 'north'))
    for x in range(X0 - 1, X1 + 2):
        key = 'colegio_friso' if y in (0, 6) else 'colegio_revoque'
        if y == 3 and x == -1:
            key = 'colegio_revoque_marcas'
        B.append((x, y, Z0 - 1, key, 'north'))
# balcony (first floor) along the north wall: floor at y = 5, z = 0..1
for x in range(X0, X1 + 1):
    for z in (0, 1):
        B.append((x, 5, z, 'colegio_madera_oscura', 'north'))
    if x < 2:
        B.append((x, 6, 2, 'colegio_baranda', 'north'))
B.append((2, 6, 2, 'colegio_baranda_poste', 'north'))
# main staircase along the east wall, 3 wide, rising towards the north from z = 7 (y = 0) to z = 2 (y = 4)
for k in range(0, 6):
    z = 7 - k
    for x in (3, 4, 5):
        if k < 5:
            B.append((x, k, z, 'colegio_escalera_madera', 'north'))
        for yy in range(0, k):
            B.append((x, yy, z, 'colegio_madera_oscura', 'north'))
    if k < 5:
        B.append((3, k + 1, z, 'colegio_baranda_escalera_izq', 'north'))
B.append((3, 0, 8, 'colegio_baranda_poste', 'north'))
# cornice around the top
for x in range(X0, X1 + 1):
    B.append((x, H - 1, Z1, 'colegio_cornisa', 'south'))
SCENE = dict(blocks=B, camera=(-3.5, 1.7, 7.8), target=(3.0, 3.0, 2.0), fov=75)
