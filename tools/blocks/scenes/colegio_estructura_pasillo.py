# Planta baja: pasillo de 3 de ancho con damero, paredes a la cal (salitre abajo), cielorraso a 5 de alto.
import zlib


def h(*a):
    return zlib.crc32(repr(a).encode()) % 1000


B = []
L = 22
for z in range(-1, L):
    for x in range(-1, 2):
        k = h(x, z)
        key = 'colegio_damero'
        if k < 90:
            key = 'colegio_damero_roto'
        elif k < 120:
            key = 'colegio_damero_faltante'
        if x == 0 and z in (6, 8, 10, 12):
            key = 'colegio_damero_huellas'
        B.append((x, -1, z, key, 'north'))
        B.append((x, 5, z, 'colegio_cielorraso', 'north'))
    for x in (-2, 2):
        for y in range(0, 5):
            k = h(x, y, z)
            key = 'colegio_revoque'
            if y == 0:
                key = 'colegio_revoque_salitre'
            elif y == 4 and k < 300:
                key = 'colegio_revoque_humedad'
            elif k < 120:
                key = 'colegio_revoque_descascarado'
            elif k < 160 and y == 2:
                key = 'colegio_revoque_marcas'
            elif k < 185 and y == 1:
                key = 'colegio_revoque_grafiti'
            B.append((x, y, z, key, 'north'))
for x in range(-1, 2):
    for y in range(0, 5):
        B.append((x, y, L, 'colegio_friso' if y == 0 else 'colegio_crema', 'north'))
SCENE = dict(blocks=B, camera=(0.5, 1.62, 0.3), target=(0.3, 1.2, 14.0), fov=70)
