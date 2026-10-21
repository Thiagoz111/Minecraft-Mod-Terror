# Casa Morales - CUARTO DE TOTI with the placard CLOSED (the hiding spot as the player sees it from the room).
# brender cannot preview Door blocks, so casa_placard_cerrado_izq/der (the fixed louvred fronts, flush with the wall)
# stand in for the two casa_placard_puerta leaves; the room is casa_muebles_toti.py.
exec(open('tools/blocks/scenes/casa_muebles_toti.py').read())
B = [b if not b[3].startswith('casa_placard_fondo') else (b[0], b[1], b[2], 'casa_placard_cerrado_izq' if b[2] == 2 else
                                                            'casa_placard_cerrado_der', 'west') for b in B]
SCENE = dict(blocks=B, camera=(0.9, 1.62, 4.8), target=(4.6, 1.1, 2.6), fov=74)
