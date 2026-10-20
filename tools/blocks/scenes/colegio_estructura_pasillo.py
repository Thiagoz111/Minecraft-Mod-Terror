# Planta baja: pasillo de 3 de ancho con damero, ventanas al claustro (oeste) cada 4 bloques, puertas de aulas
# (este) con banderola, paredes a la cal con salitre abajo, vigas bajo el cielorraso a 5 de alto.
import zlib


def h(*a):
    return zlib.crc32(repr(a).encode()) % 1000


B = []
L = 22
WIN = (2, 6, 10, 14, 18)
DOORS = {5: 'colegio_puerta_aula_6', 13: 'colegio_puerta_aula_4'}
for z in range(-1, L):
    for x in range(-1, 2):
        k = h(x, z)
        key = 'colegio_damero'
        if k < 70:
            key = 'colegio_damero_roto'
        elif k < 85:
            key = 'colegio_damero_faltante'
        if x == 0 and z in (6, 8, 10, 12):
            key = 'colegio_damero_huellas'
        B.append((x, -1, z, key, 'north'))
        B.append((x, 5, z, 'colegio_cielorraso', 'north'))
        if z % 3 == 0:
            B.append((x, 4, z, 'colegio_viga', 'east'))
    for x in (-2, 2):
        for y in range(0, 5):
            k = h(x, y, z)
            if x == -2 and z in WIN and 1 <= y <= 3:
                B.append((x, y, z, ['colegio_ventana_inf', 'colegio_ventana_med', 'colegio_ventana_sup'][y - 1] if z != 10 else
                          ['colegio_postigo_inf', 'colegio_postigo_med', 'colegio_postigo_sup'][y - 1], 'west'))
                continue
            if x == 2 and z in DOORS and y <= 2:
                if y == 0:
                    B.append((x, y, z, DOORS[z], 'east'))
                elif y == 2:
                    B.append((x, y, z, 'colegio_banderola', 'east'))
                continue
            key = 'colegio_revoque'
            if y == 0:
                key = 'colegio_revoque_salitre'
            elif y == 4 and k < 300:
                key = 'colegio_revoque_humedad'
            elif k < 50:
                key = 'colegio_revoque_descascarado'
            elif k < 80 and y == 2:
                key = 'colegio_revoque_marcas'
            elif k < 100 and y == 1:
                key = 'colegio_revoque_grafiti'
            B.append((x, y, z, key, 'north'))
for x in range(-1, 2):
    for y in range(0, 5):
        B.append((x, y, L, 'colegio_friso' if y == 0 else 'colegio_crema', 'north'))
SCENE = dict(blocks=B, camera=(0.6, 1.62, 0.3), target=(0.0, 1.5, 14.0), fov=70)
