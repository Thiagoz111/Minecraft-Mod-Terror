# Aula de 6°: piso de tablas, friso de madera oscura, revoque crema arriba, cielorraso de machimbre.
import zlib


def h(*a):
    return zlib.crc32(repr(a).encode()) % 1000


B = []
W, D, H = 9, 7, 4
for x in range(0, W):
    for z in range(0, D):
        k = h(x, z)
        key = 'colegio_tablas' if k > 180 else 'colegio_tablas_gastadas'
        if (x, z) == (4, 3):
            key = 'colegio_tabla_floja'
        B.append((x, -1, z, key, 'north'))
        B.append((x, H, z, 'colegio_cielorraso_tablas', 'north'))
for x in range(-1, W + 1):
    for y in range(0, H):
        for z in (-1, D):
            key = 'colegio_friso' if y == 0 else 'colegio_crema'
            if y == 2 and x == 4 and z == D:
                key = 'colegio_crema_marcas'
            B.append((x, y, z, key, 'north'))
for z in range(0, D):
    for y in range(0, H):
        for x in (-1, W):
            key = 'colegio_friso' if y == 0 else 'colegio_crema'
            if y == 3 and h(x, z) < 250:
                key = 'colegio_crema_marcas'
            B.append((x, y, z, key, 'north'))
SCENE = dict(blocks=B, camera=(1.2, 1.62, 0.6), target=(6.0, 1.0, 6.5), fov=70)
