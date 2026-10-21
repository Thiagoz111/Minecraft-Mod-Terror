# Casa Morales - LAVADERO (4 x 5) and the way down (cap. 7 'Bajá al sótano'): grey cement walls and floor, the
# electrical board on the wall (casa_muebles 'tablero': the scripted blackout), the laundry sink, a gas vent, and the
# cement flight going down to the basement inside a walled well (2 half-steps per block, 45 degrees), the galvanised
# pipe handrail on the wall, damp basement plaster in the well, the bulb burning at the bottom. Seen from the top
# step, as the player sees it before going down. (Plank basement Door: not drawn in previews.)
B = []
W, D, H = 4, 5, 3
WELL_X = 3
for x in range(-1, W + 1):
    for z in range(-1, D + 1):
        if not (x == WELL_X and 1 <= z <= 4):
            B.append((x, -1, z, 'casa_cemento_piso', 'north'))
        B.append((x, H, z, 'casa_cielorraso', 'north'))
for y in range(H):
    cw = 'casa_cemento_lavadero_zocalo' if y == 0 else 'casa_cemento_lavadero'     # grimy foot course, plain above
    for x in range(-1, W + 1):
        B.append((x, y, -1, cw, 'north'))
        B.append((x, y, D, cw, 'north'))
    for z in range(D):
        B.append((-1, y, z, cw, 'north'))
        B.append((W, y, z, cw, 'north'))
# the flight: one block per step pair, going down towards +z (low side faces south)
for k in range(4):
    z, y = 1 + k, -1 - k
    B.append((WELL_X, y, z, 'casa_escalon_cemento', 'south'))
    for yy in range(-6, y):
        B.append((WELL_X, yy, z, 'casa_cemento_piso', 'north'))
    B.append((WELL_X, y + 1, z, 'casa_pasamanos_der', 'south'))
for z in range(1, 9):
    for y in range(-6, -1 if z <= 4 else 0):
        B.append((WELL_X - 1, y, z, 'casa_pared_sotano_zocalo' if y == -5 else 'casa_pared_sotano', 'north'))
        B.append((WELL_X + 1, y, z, 'casa_pared_sotano_zocalo' if y == -5 else 'casa_pared_sotano', 'north'))
B += [(WELL_X - 1, -1, z, 'casa_cemento_lavadero', 'north') for z in range(1, 5)]
# bottom: basement floor, ceiling over the lower landing, the far wall with the crack's first block
for z in range(5, 9):
    B.append((WELL_X, -6, z, 'casa_cemento_piso', 'north'))
    B.append((WELL_X, -1, z, 'casa_losa_sotano', 'north'))
for y in range(-5, -1):
    B.append((WELL_X, y, 9, 'casa_pared_sotano_zocalo' if y == -5 else 'casa_pared_sotano', 'north'))
B += [(WELL_X, -2, 7, 'casa_foco', 'north')]
# the room: board, sink, vent, switch, a rail at the open side of the well
B += [(0, 1, 0, 'casa_tablero', 'south'), (0, 0, 3, 'casa_pileta_lavar', 'east'), (1, 2, 0, 'casa_rejilla', 'south'),
      (2, 1, 0, 'casa_llave_luz', 'south'), (2, 0, 1, 'casa_baranda', 'east'), (2, 0, 2, 'casa_baranda', 'east'),
      (2, 0, 3, 'casa_baranda', 'east'), (2, 0, 4, 'casa_baranda', 'east')]
B = [b for b in B if not (b[0] == WELL_X - 1 and b[1] == -1 and 1 <= b[2] <= 4) or b[3] != 'casa_cemento_lavadero'] + \
    [(WELL_X - 1, -1, z, 'casa_cemento_piso', 'north') for z in range(1, 5)]
SCENE = dict(blocks=B, camera=(3.5, 1.5, 0.35), target=(3.5, -3.2, 6.0), fov=78)
