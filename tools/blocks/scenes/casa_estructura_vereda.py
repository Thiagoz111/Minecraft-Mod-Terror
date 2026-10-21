# Casa Morales - LA VEREDA (arrival, chapter 1): Pasaje Las Glicinas at night. Old asphalt, granite curb, broken
# 'vainilla' sidewalk, the concrete lamp post with flyers and the flickering sodium lamp, the street-name plate, the
# front fence (low brick wall + railing with the dog sign and the Nona scribble, brick piers, the electricity pier,
# gaps for the pedestrian gate and the car gate - Door blocks do not render in previews), the front garden and the
# chalet facade: plinth, face brick, white render, two barred windows (one blind half down), number and doorbell,
# the eave with its gutter and downpipe.
import zlib


def h(*a):
    return zlib.crc32(repr(a).encode()) % 1000


B = []
for x in range(-6, 16):
    for z in range(-9, 9):
        if z <= -6:
            k = 'casa_asfalto'
        elif z == -5:
            k = 'casa_cordon'
        elif z <= -1:
            k = 'casa_vereda_rota' if h(x, z) < 220 else 'casa_vereda'
        elif z == 0:
            k = 'casa_vereda'
        else:
            k = 'casa_cesped'
            if x == 3 and z < 4:
                k = 'casa_baldosa_patio'
            if 8 <= x <= 9 and z < 4:
                k = 'casa_cemento_piso'
        B.append((x, -1, z, k, 'north'))
# fence at z = 0
FENCE = {-2: 'pilar', -1: 'm', 0: 'm', 1: 'm', 2: 'pilar', 3: 'gate', 4: 'pilar', 5: 'm', 6: 'm', 7: 'pilar_luz',
         8: 'gate', 9: 'gate', 10: 'pilar', 11: 'm', 12: 'm', 13: 'pilar'}
for x, kind in FENCE.items():
    if kind == 'm':
        B.append((x, 0, 0, 'casa_murito', 'north'))
        r = 'casa_reja_cartel_perro_nona' if x == 5 else 'casa_reja'
        B.append((x, 1, 0, r, 'north'))
    elif kind == 'pilar':
        B += [(x, 0, 0, 'casa_pilar', 'north'), (x, 1, 0, 'casa_pilar_remate', 'north')]
    elif kind == 'pilar_luz':
        B += [(x, 0, 0, 'casa_pilar_luz', 'north'), (x, 1, 0, 'casa_pilar_remate', 'north')]
# lamp post on the sidewalk, arm over the street
B += [(5, 0, -4, 'casa_poste_pie', 'north'), (5, 1, -4, 'casa_poste_afiches', 'north'), (5, 2, -4, 'casa_poste', 'north'),
      (5, 3, -4, 'casa_poste', 'north'), (5, 4, -4, 'casa_farol', 'north')]
B += [(-4, 0, -4, 'casa_poste_pie', 'north'), (-4, 1, -4, 'casa_poste', 'north'), (-4, 2, -4, 'casa_poste_cartel_calle', 'north')]
# facade at z = 4 (x 0..11), 4 high, eave on top
WIN = {}
for (x0, half) in ((1, False), (9, True)):
    for (x, side) in ((x0, 'der'), (x0 + 1, 'izq')):
        WIN[(x, 1)] = f'casa_ventana_inf_{side}'
        WIN[(x, 2)] = f'casa_ventana_sup_{side}' + ('_cerrada' if half else '')
for x in range(0, 12):
    for y in range(4):
        if (x, y) in WIN:
            B.append((x, y, 4, WIN[(x, y)], 'north'))
            continue
        if x == 5 and y < 2:
            continue                           # front door opening (casa_puerta_entrada)
        if y == 0:
            k = 'casa_zocalo_ladrillo'
        elif y == 1:
            k = 'casa_ladrillo_salitre' if h(x, y) < 350 else 'casa_ladrillo_visto'
        elif y == 3:
            k = 'casa_revoque_chorreado' if h(x) < 450 else 'casa_revoque_blanco'
        else:
            k = 'casa_revoque_blanco'
        B.append((x, y, 4, k, 'north'))
    B.append((x, 4, 4, 'casa_techo_alero', 'north'))
    B.append((x, 5, 5, 'casa_techo_musgo' if h(x, 5) < 300 else 'casa_techo', 'north'))
    B.append((x, 6, 6, 'casa_techo', 'north'))
B += [(6, 1, 3, 'casa_numero_1961', 'north'), (4, 1, 3, 'casa_timbre', 'north'), (7, 0, 3, 'casa_medidor_gas', 'north'),
      (11, 3, 3, 'casa_bajada_codo', 'north'), (11, 2, 3, 'casa_bajada', 'north'), (11, 1, 3, 'casa_bajada', 'north'),
      (11, 0, 3, 'casa_bajada_pie', 'north')]
SCENE = dict(blocks=B, camera=(0.2, 1.7, -8.4), target=(6.0, 1.6, 0.5), fov=72)
