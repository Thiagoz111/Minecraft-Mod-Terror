# Casa Morales - CUARTO DEL 61 (after the Nona broke the wall): the sealed room, 9 x 9 x 4, packed sand floor, grey
# lime-washed walls with candle soot, the hole in the north wall (6 boquete pieces, rubble and spilled sand, the
# basement and its bulb beyond), the old salt circle (r ~3, one piece broken by a drag mark) around the iron bed,
# LEMAZA scratched at a child's height on the east wall, the priest's Latin on the west wall, the drawing 'MI AMIGO'
# and the day tallies on the south wall, sooty handprints by the hole. Iron bed / candles / stole from casa_muebles.
import zlib


def h(*a):
    return zlib.crc32(repr(a).encode()) % 1000


B = []
H = 4
# --- the 1961 room: x 0..8, z 1..9
for x in range(-1, 10):
    for z in range(1, 11):
        B.append((x, -1, z, 'casa_arena', 'north'))
        B.append((x, H, z, 'casa_losa_sotano', 'north'))
for y in range(H):
    for z in range(1, 10):
        for x in (-1, 9):
            k = 'casa_pared_61_zocalo' if y == 0 else 'casa_pared_61'
            if x == 9 and z == 2:
                k = ('casa_pared_61_hollin', 'casa_pared_61_hollin_alto', 'casa_pared_61_hollin_alto', 'casa_pared_61')[y]
            B.append((x, y, z, k, 'north'))
    for x in range(-1, 10):
        B.append((x, y, 10, 'casa_pared_61_zocalo' if y == 0 else 'casa_pared_61', 'north'))
# --- the dividing wall z = 0 with the hole at x 3..4 (pieces face the basement = north)
HOLE = {(5, 0): 'izq_abajo', (5, 1): 'izq_arriba', (4, 2): 'dintel_izq', (3, 2): 'dintel_der', (2, 1): 'der_arriba', (2, 0): 'der_abajo'}
for y in range(H):
    for x in range(-1, 10):
        if (x, y) in HOLE:
            B.append((x, y, 0, 'casa_boquete_' + HOLE[(x, y)], 'north'))
        elif x in (3, 4) and y < 2:
            continue
        else:
            k = 'casa_pared_divisoria_zocalo' if y == 0 else ('casa_pared_divisoria_b' if h(x, y) < 180 else 'casa_pared_divisoria')
            B.append((x, y, 0, k, 'north'))
B += [(3, 0, 0, 'casa_escombros_arena', 'north'), (4, 0, 0, 'casa_escombros', 'south'), (3, 0, 1, 'casa_escombros', 'south'),
      (4, 0, 1, 'casa_escombros', 'east'), (4, 0, -1, 'casa_escombros_arena', 'north')]
# --- the basement beyond the hole (z -6..-1)
for x in range(-1, 10):
    for z in range(-6, 0):
        B.append((x, -1, z, 'casa_cemento_piso', 'north'))
        B.append((x, H, z, 'casa_losa_sotano', 'north'))
for y in range(H):
    for x in range(-1, 10):
        B.append((x, y, -7, 'casa_pared_sotano_zocalo' if y == 0 else 'casa_pared_sotano', 'north'))
    for z in range(-6, 0):
        for x in (-2, 10):
            B.append((x, y, z, 'casa_pared_sotano_zocalo' if y == 0 else 'casa_pared_sotano', 'north'))
B += [(4, 3, -3, 'casa_foco', 'north'), (7, 0, -6, 'casa_caldera', 'south'), (1, 0, -5, 'casa_tapado_sillon', 'south')]
# --- the old salt circle around the bed, centred on the corner (4, 6)
PIECES = {'a': (0, 2), 'b': (1, 2), 'c': (2, 2), 'd': (2, 1), 'e': (2, 0), 'f': (1, 1)}
CX, CZ = 4, 6
for p, (i, j) in PIECES.items():
    for (x, z, f) in ((CX + i, CZ + j, 'north'), (CX - 1 - j, CZ + i, 'east'), (CX - 1 - i, CZ - 1 - j, 'south'), (CX + j, CZ - 1 - i, 'west')):
        key = 'casa_sal_61_a_rota' if (p, f) == ('a', 'north') else f'casa_sal_61_{p}'
        B.append((x, 0, z, key, f))
B += [(3, 0, 5, 'casa_cama_hierro_cabecera', 'south'), (3, 0, 6, 'casa_cama_hierro_pie', 'south'),
      (5, 0, 7, 'casa_velas_derretidas_apagadas', 'north'), (2, 0, 7, 'casa_velas_derretidas_apagadas', 'north'),
      (2, 0, 4, 'casa_velas_derretidas_apagadas', 'north'), (5, 0, 4, 'casa_velas_derretidas_apagadas', 'north'),
      (8, 0, 2, 'casa_velas_derretidas_apagadas', 'west'), (0, 1, 3, 'casa_estola_anselmo', 'east')]
# --- scratches and soot on the walls (decals sit in the air block in front of the wall, facing the room)
B += [(8, 0, 6, 'casa_rayones_lemaza', 'west'), (8, 0, 8, 'casa_rayones_lemaza_chico', 'west'), (0, 1, 6, 'casa_rayones_latin', 'east'),
      (5, 0, 9, 'casa_rayones_dibujo', 'north'), (7, 0, 9, 'casa_rayones_palitos', 'north'), (1, 0, 1, 'casa_manos_hollin', 'south'),
      (6, 0, 1, 'casa_rayones_lemaza_chico', 'south')]
SCENE = dict(blocks=B, camera=(7.4, 1.6, 9.3), target=(3.2, 0.9, 1.5), fov=74)
