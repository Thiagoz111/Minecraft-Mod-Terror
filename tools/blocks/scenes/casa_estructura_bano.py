# Casa Morales - BAÑO (4 x 3): light-blue tiles to door height with the border row, white paint above, the 1950s
# octagon-and-taco floor, the tilt window high on the back wall, plaster ceiling with damp from the shower.
# Fixtures from casa_muebles for scale.
B = []
W, D, H = 4, 3, 3


def wall(y, x=None, z=None):
    # dirty grout only where the water runs: the course along the bath (x = -1, z 0..1) and behind the basin (x = W);
    # one tile missing over the toilet
    if y == 0 and ((x == -1 and z in (0, 1)) or (x == W and z == 1) or (z == -1 and x in (-1, 0))):
        return 'casa_azulejo_celeste_sucio'
    if y == 0 and (x, z) == (2, -1):
        return 'casa_azulejo_celeste_falta'
    return ('casa_azulejo_celeste', 'casa_azulejo_celeste_guarda', 'casa_pared_bano')[y]


for x in range(-1, W + 1):
    for z in range(-1, D + 2):
        B.append((x, -1, z, 'casa_piso_bano' if z < D else 'casa_granitico', 'north'))
        B.append((x, H, z, 'casa_cielorraso_humedad' if (x, z) == (0, 0) else 'casa_cielorraso', 'north'))
for y in range(H):
    for x in range(-1, W + 1):
        B.append((x, y, -1, 'casa_ventana_bano' if (x, y) == (1, 2) else wall(y, x, -1), 'north'))
        if not (x == 2 and y < 2):
            B.append((x, y, D, wall(y, x, D), 'north'))
    for z in range(D):
        B.append((-1, y, z, wall(y, -1, z), 'north'))
        B.append((W, y, z, wall(y, W, z), 'north'))
B += [(0, 0, 0, 'casa_banadera_izq', 'east'), (0, 0, 1, 'casa_banadera_der', 'east'), (2, 0, 0, 'casa_inodoro', 'south'),
      (3, 0, 1, 'casa_lavatorio', 'west'), (3, 1, 1, 'casa_botiquin', 'west'), (2, 2, D - 1, 'casa_contramarco_dintel', 'north')]
SCENE = dict(blocks=B, camera=(2.6, 1.62, 2.5), target=(0.6, 0.9, -0.6), fov=82)
