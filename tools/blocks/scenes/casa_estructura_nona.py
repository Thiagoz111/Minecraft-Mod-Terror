# Casa Morales - CUARTO DE LA NONA (PB, 6 x 6): faded floral wallpaper over a wooden skirting, parquet, the street
# window with the blind half down, damp in the ceiling corner. casa_muebles: knitted bed, the altar of holy cards
# with candles (the only always-safe light), rocking chair, wardrobe, basket of red wool.
ns = {}
exec(open('tools/blocks/scenes/casa_estructura_lucia.py').read(), ns)
room = ns['room']


def nona_wall(x, y, z):
    return 'casa_empapelado_nona_zocalo' if y == 0 else 'casa_empapelado_nona'


B = room(6, 6, nona_wall, win=True, win_mode='half', door_x=4, damp=(0, 0))
B += [(0, 0, 2, 'casa_cama_nona_cabecera', 'east'), (1, 0, 2, 'casa_cama_nona_pie', 'east'), (5, 0, 1, 'casa_altar', 'west'),
      (3, 0, 4, 'casa_mecedora', 'north'), (0, 0, 5, 'casa_ropero_abajo', 'east'), (0, 1, 5, 'casa_ropero_arriba', 'east'),
      (4, 0, 2, 'casa_canasta_lana', 'north'), (0, 0, 0, 'casa_mesa_luz_nona', 'east')]
SCENE = dict(blocks=B, camera=(4.6, 1.62, 5.3), target=(1.5, 1.0, 0.2), fov=78)
