# Casa Morales - HALL AND STAIR (PB granítico hall 3 x 8 under a double-height stairwell): pitch-pine stair rising
# along +z against the west wall (two 8/16 steps per block), the iron-and-cedar balustrade on the open side with the
# newel post at the foot, the upstairs landing (1P floor at y=5) with the straight balustrade at the well edge and
# the red runner going down the upstairs hall, aqua walls with skirting, hall doors (openings) and switches.
B = []
W, D = 3, 8
for x in range(-1, W + 1):
    for z in range(-1, D + 1):
        B.append((x, -1, z, 'casa_granitico_roto' if (x, z) == (2, 1) else 'casa_granitico', 'north'))
        B.append((x, 8, z, 'casa_cielorraso_humedad' if (x, z) == (1, 6) else 'casa_cielorraso', 'north'))
# stair: x = 0, rising from z = 1 (y 0) to z = 5 (y 4); 1P floor at y = 4 (slab top = 5) for z >= 6
for k in range(5):
    z, y = 1 + k, k
    B.append((0, y, z, 'casa_escalon_madera', 'south' if False else 'north'))
    for yy in range(y):
        B.append((0, yy, z, 'casa_pared_pasillo', 'north'))
    B.append((0, y + 1, z, 'casa_baranda_escalera_der', 'north'))
for x in range(-1, W + 1):
    for z in range(6, D + 1):
        B.append((x, 4, z, 'casa_parquet', 'north'))
for x in (1, 2):
    B.append((x, 5, 6, 'casa_baranda', 'north'))
B += [(0, 1, 0, 'casa_baranda_poste', 'north')]
# upstairs runner
for z in range(7, D + 1):
    B.append((1, 5, z, 'casa_alfombra', 'north'))
B.append((1, 5, 6, 'casa_alfombra_punta', 'north'))
# walls: aqua with skirting, double height
for y in range(8):
    for z in range(-1, D + 2):
        for x in (-1, W):
            k = 'casa_pared_pasillo_zocalo' if y in (0, 5) else 'casa_pared_pasillo'
            if x == W and z == 2 and y < 2:
                continue
            if x == W and z == 7 and y in (5, 6):
                continue
            B.append((x, y, z, k, 'north'))
    for x in range(-1, W + 1):
        B.append((x, y, -1, 'casa_pared_pasillo_zocalo' if y == 0 else 'casa_pared_pasillo', 'north'))
        B.append((x, y, D + 1, 'casa_pared_pasillo_zocalo' if y in (0, 5) else 'casa_pared_pasillo', 'north'))
B += [(2, 2, 2, 'casa_contramarco_dintel', 'west'), (2, 1, 1, 'casa_contramarco_izq', 'west'), (2, 1, 3, 'casa_contramarco_der', 'west'),
      (2, 7, 7, 'casa_contramarco_dintel', 'west'), (2, 1, 4, 'casa_llave_luz', 'west'), (2, 6, 8, 'casa_llave_luz', 'west')]
SCENE = dict(blocks=B, camera=(2.2, 1.62, 0.3), target=(0.5, 3.4, 5.5), fov=80)
