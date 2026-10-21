# Casa Morales - DORMITORIO MATRIMONIAL (1P, 7 x 6): mustard-and-brown 70s wallpaper over the skirting, parquet,
# window with the blind half down, damp ceiling corner. casa_muebles: double bed, chest of drawers, crucifix.
ns = {}
exec(open('tools/blocks/scenes/casa_estructura_lucia.py').read(), ns)
room = ns['room']


def mat_wall(x, y, z):
    return 'casa_empapelado_matrimonial_zocalo' if y == 0 else 'casa_empapelado_matrimonial'


B = room(7, 6, mat_wall, win=True, win_mode='half', door_x=5, damp=(6, 0))
B += [(2, 0, 4, 'casa_cama_matrimonial_cabecera_izq', 'north'), (3, 0, 4, 'casa_cama_matrimonial_cabecera_der', 'north'),
      (2, 0, 3, 'casa_cama_matrimonial_pie_izq', 'north'), (3, 0, 3, 'casa_cama_matrimonial_pie_der', 'north'),
      (6, 0, 2, 'casa_comoda_izq', 'west'), (6, 0, 1, 'casa_comoda_der', 'west'), (2, 2, 5, 'casa_crucifijo', 'north')]
SCENE = dict(blocks=B, camera=(5.6, 1.62, 5.4), target=(1.6, 0.9, 0.5), fov=76)
