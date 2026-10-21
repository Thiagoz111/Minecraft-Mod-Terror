# Casa Morales - CUARTO DE TOTI (1P, 5 x 6): dark blue walls with skirting and four gamer poster decals, worn parquet, the street
# window with the blind DOWN (gamer cave), and the PLACARD on the east wall for the hiding gag: two louvred placard
# Doors (not drawn in previews: the opening shows the dark inside) under the top cupboards (casa_placard_maletero).
ns = {}
exec(open('tools/blocks/scenes/casa_estructura_lucia.py').read(), ns)
room, h = ns['room'], ns['h']


def toti_wall(x, y, z):
    return 'casa_pared_toti_zocalo' if y == 0 else 'casa_pared_toti'


B = room(5, 6, toti_wall, floor=lambda x, z: 'casa_parquet_gastado' if h(x, z) < 500 else 'casa_parquet', win=True, win_mode='closed', door_x=1)
# the placard: carve the east wall at z 2..3 (2 wide x 2 high), its back and the top cupboards above
B = [b for b in B if not (b[0] == 5 and b[2] in (2, 3) and b[1] in (0, 1))]
for z in (2, 3):
    for y in (0, 1):
        B.append((6, y, z, 'casa_pared_toti', 'north'))
    B.append((5, -1, z, 'casa_parquet', 'north'))
    B.append((5, 2, z, 'casa_placard_maletero', 'east'))   # same facing as the placard Door below (placed from the room)
B += [(0, 0, 0, 'casa_escritorio_pc_izq', 'south'), (1, 0, 0, 'casa_escritorio_pc_der', 'south'), (1, 0, 1, 'casa_silla_gamer', 'north'),
      (0, 0, 4, 'casa_cama_toti_cabecera', 'east'), (1, 0, 4, 'casa_cama_toti_pie', 'east'), (2, 0, 3, 'casa_ropa_tirada', 'north')]
# the four poster decals (each in the air block in front of the wall, facing the room)
B += [(3, 1, 0, 'casa_poster_toti_1', 'south'), (4, 1, 1, 'casa_poster_toti_4', 'west'), (4, 1, 4, 'casa_poster_toti_3', 'west'),
      (0, 1, 0, 'casa_poster_toti_2', 'south')]
SCENE = dict(blocks=B, camera=(0.6, 1.62, 5.3), target=(4.6, 1.1, 2.4), fov=76)
