# Casa Morales - COCINA (7 x 6, cap. 4 poltergeist): 70s green tiles to door height with the decorated border row,
# beige paint above, ceramic floor, plaster ceiling, the window over the sink towards the patio (one leaf open: Marta
# throws the chorizo through it), the kitchen door to the patio (Door: not drawn, opening only), gas vent grille by
# the stove, switch and outlet. A few casa_muebles pieces for scale (counter, stove, fridge, table).
import zlib


def h(*a):
    return zlib.crc32(repr(a).encode()) % 1000


B = []
W, D, H = 7, 6, 3
WIN = {(3, 1): 'casa_ventana_cocina_izq_abierta', (2, 1): 'casa_ventana_cocina_der'}


def wall(x, y, z):
    # greasy grout behind the stove and the sink (the course over the counter), one tile gone by the door, the soot
    # cloud over the burners in the painted course
    if y == 1 and z == D and x in (0, 1, 2):
        return 'casa_azulejo_verde_sucio'
    if y == 0 and (x, z) == (W, 4):
        return 'casa_azulejo_verde_falta'
    if y == 2 and (x, z) == (0, D):
        return 'casa_pared_cocina_hollin'
    return ('casa_azulejo_verde', 'casa_azulejo_verde_guarda', 'casa_pared_cocina')[y]


for x in range(-1, W + 1):
    for z in range(-1, D + 1):
        B.append((x, -1, z, 'casa_ceramica_cocina', 'north'))
        B.append((x, H, z, 'casa_cielorraso_humedad' if (x, z) == (1, 4) else 'casa_cielorraso', 'north'))
for y in range(H):
    for x in range(-1, W + 1):
        B.append((x, y, -1, wall(x, y, -1), 'north'))
        if (x, y) in WIN:
            B.append((x, y, D, WIN[(x, y)], 'south'))
        elif x == 5 and y < 2:
            pass                                       # door to the patio
        else:
            B.append((x, y, D, wall(x, y, D), 'north'))
    for z in range(D):
        if not (x == -1 and z == 2 and y < 2):
            B.append((-1, y, z, wall(-1, y, z), 'north'))
        B.append((W, y, z, wall(W, y, z), 'north'))
# patio glimpse through the door and window
for x in range(0, 7):
    for z in (D + 1, D + 2, D + 3):
        B.append((x, -1, z, 'casa_baldosa_patio' if z == D + 1 else 'casa_ladrillo_patio', 'north'))
B += [(x, y, D + 4, 'casa_medianera', 'north') for x in range(-1, 8) for y in range(3)]
B += [(5, 2, D - 1, 'casa_contramarco_dintel', 'north'), (6, 1, D - 1, 'casa_contramarco_izq', 'north'), (4, 1, D - 1, 'casa_contramarco_der', 'north'),
      (0, 2, 4, 'casa_rejilla', 'east'), (6, 1, 0, 'casa_llave_luz', 'south'), (1, 1, D - 1, 'casa_enchufe', 'north')]
B += [(0, 0, 5, 'casa_cocina_gas_pava', 'north'), (1, 0, 5, 'casa_mesada', 'north'), (2, 0, 5, 'casa_mesada_pileta', 'north'),
      (3, 0, 5, 'casa_mesada_cajones', 'north'), (6, 0, 1, 'casa_heladera_abajo', 'west'), (6, 1, 1, 'casa_heladera_arriba', 'west'),
      (3, 0, 2, 'casa_mesa_cocina', 'north'), (3, 2, 2, 'casa_tubo', 'north')]
SCENE = dict(blocks=B, camera=(6.2, 1.62, 0.4), target=(1.8, 1.0, 5.6), fov=74)
