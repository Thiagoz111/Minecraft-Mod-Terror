# Casa Morales - PATIO (cap. 4-5): red-tile gallery along the back of the house, brick paving beyond, medianeras on
# three sides, the parrilla (casa_muebles) against the back medianera and the Nona's salt line drawn as a HALF circle
# in front of it (the circle is centred on the wall face: only the 'south'/'west' quadrant pieces are placed).
# The house's back facade: damp cement plinth, white render with rising damp (wet down to the plinth), kitchen window (one leaf open), eave with gutter
# and downpipe. casa_estructura_patio_casa looks back at the facade from the grill.
import zlib


def h(*a):
    return zlib.crc32(repr(a).encode()) % 1000


B = []
X0, X1, ZB = -1, 10, 13          # patio x -1..10, z 1..12, back medianera at z = 13
for x in range(X0 - 1, X1 + 2):
    for z in range(1, ZB + 1):
        B.append((x, -1, z, 'casa_baldosa_patio' if z <= 3 else 'casa_ladrillo_patio', 'north'))
for y in range(3):
    for x in range(X0 - 1, X1 + 2):
        B.append((x, y, ZB, 'casa_medianera', 'north'))
    for z in range(1, ZB):
        for x in (X0 - 1, X1 + 1):
            B.append((x, y, z, 'casa_medianera', 'north'))
# back facade of the house (z = 0), facing the patio (south)
WIN = {(3, 1): 'casa_ventana_cocina_izq_abierta', (4, 1): 'casa_ventana_cocina_der', (8, 2): 'casa_ventana_bano'}
for x in range(X0 - 1, X1 + 2):
    for y in range(3):
        if (x, y) in WIN:
            B.append((x, y, 0, WIN[(x, y)], 'south'))
        elif x == 6 and y < 2:
            continue                                  # kitchen door opening (Door blocks are not drawn here)
        else:
            k = 'casa_zocalo_revoque_humedad' if y == 0 else ('casa_revoque_humedad' if y == 1 else
                                                              ('casa_revoque_chorreado' if y == 2 and h(x, 2) < 400 else 'casa_revoque_blanco'))
            B.append((x, y, 0, k, 'north'))
    B.append((x, 3, 0, 'casa_techo_alero_musgo' if h(x, 9) < 300 else 'casa_techo_alero', 'south'))
    B.append((x, 4, -1, 'casa_techo_musgo' if h(x, 8) < 250 else 'casa_techo', 'south'))
B += [(6, 0, -1, 'casa_granitico', 'north'), (6, 1, -1, 'casa_azulejo_verde', 'north'), (6, 2, 1, 'casa_contramarco_dintel', 'south')]
B += [(9, 2, 1, 'casa_bajada_codo', 'south'), (9, 1, 1, 'casa_bajada', 'south'), (9, 0, 1, 'casa_bajada_pie', 'south')]
# the parrilla against the back medianera (casa_muebles)
B += [(3, 0, 12, 'casa_parrilla_mesada_der', 'north'), (4, 0, 12, 'casa_parrilla', 'north'), (5, 0, 12, 'casa_parrilla_mesada_izq', 'north'),
      (6, 0, 12, 'casa_parrilla_mesada', 'north'), (4, 1, 12, 'casa_parrilla_campana', 'north'), (4, 2, 12, 'casa_parrilla_chimenea', 'north'),
      (3, 1, 12, 'casa_cuchillos', 'north'), (6, 1, 12, 'casa_sal_gruesa', 'north'), (5, 0, 10, 'casa_silla_jorge', 'south')]
# the Nona's salt: half circle centred on the wall-face corner (5, 13)
PIECES = {'a': (0, 2), 'b': (1, 2), 'c': (2, 2), 'd': (2, 1), 'e': (2, 0), 'f': (1, 1)}
CX, CZ = 5, 13
for p, (i, j) in PIECES.items():
    for (x, z, f) in ((CX - 1 - i, CZ - 1 - j, 'south'), (CX + j, CZ - 1 - i, 'west')):
        B.append((x, 0, z, f'casa_sal_patio_{p}', f))
SCENE = dict(blocks=B, camera=(5.2, 1.62, 3.2), target=(4.8, 0.5, 11.5), fov=72)
