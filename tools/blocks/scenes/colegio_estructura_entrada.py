# Entrada desde la calle: muro perimetral de piedra con coronamiento y reja de lanzas, pilares revocados con
# remate, reja doble bajo el letrero de hierro "COLEGIO SANTA INÉS DE LA VIGILIA · 1931", grafitis de Kevin y
# "ACÁ ESPANTAN", sendero de ladrillo hasta la fachada con el portón, ventanas enrejadas y tejado.
import zlib


def h(*a):
    return zlib.crc32(repr(a).encode()) % 1000


B = []
# ground
for x in range(-12, 14):
    for z in range(-8, 16):
        key = 'colegio_patio_lajas'
        if 1 <= x <= 4 and z >= 0:
            key = 'colegio_patio_ladrillo'
        B.append((x, -1, z, key, 'north'))
# perimeter wall at z = 0 (gate opening x = 1..4, piers at x = 0 and 5)
for x in range(-12, 14):
    if 1 <= x <= 4:
        continue
    if x in (0, 5):
        for y in range(0, 4):
            B.append((x, y, 0, 'colegio_revoque_descascarado' if y == 1 else 'colegio_revoque', 'north'))
        B.append((x, 4, 0, 'colegio_pilar_remate', 'north'))
        continue
    for y in range(0, 3):
        B.append((x, y, 0, 'colegio_muro_perimetral', 'north'))
    B.append((x, 3, 0, 'colegio_muro_coronamiento', 'north'))
    B.append((x, 4, 0, 'colegio_reja_cerca', 'north'))
for x in range(1, 5):
    B.append((x, 0, 0, 'colegio_reja_porton_inf', 'north'))
    B.append((x, 1, 0, 'colegio_reja_porton_sup', 'north'))
    B.append((x, 2, 0, 'colegio_letrero_%d' % (5 - x), 'north'))   # 1..4 from the viewer's left (+x is left)
# graffiti on the street face of the wall (decals in the street cells, z = -1, facing the street)
B.append((-4, 0, -1, 'colegio_grafiti_kevin', 'north'))
B.append((10, 0, -1, 'colegio_grafiti_aca_espantan', 'north'))
# facade of the school at z = 14
for x in range(-12, 14):
    for y in range(0, 6):
        key = 'colegio_revoque' if y > 0 else 'colegio_revoque_salitre'
        if x in (2, 3) and y <= 1:
            if y == 0:
                B.append((x, y, 14, 'colegio_porton', 'north'))
            continue
        if x in (2, 3) and y == 2:
            key = 'colegio_banderola'
        if x % 4 == 0 and x not in (0, 4) and 1 <= y <= 3:
            key = ['colegio_postigo_inf', 'colegio_postigo_med', 'colegio_postigo_sup'][y - 1] if h(x) < 400 else \
                ['colegio_ventana_inf', 'colegio_ventana_med', 'colegio_ventana_sup'][y - 1]
        B.append((x, y, 14, key, 'north'))
    B.append((x, 6, 13, 'colegio_alero', 'north'))
    B.append((x, 7, 13, 'colegio_tejas_losa', 'north'))
    B.append((x, 7, 14, 'colegio_tejas_losa', 'north:top'))
    B.append((x, 8, 15, 'colegio_tejas_losa', 'north'))
    B.append((x, 6, 14, 'colegio_revoque', 'north'))
SCENE = dict(blocks=B, camera=(2.6, 1.7, -6.5), target=(2.6, 2.6, 6.0), fov=72)
