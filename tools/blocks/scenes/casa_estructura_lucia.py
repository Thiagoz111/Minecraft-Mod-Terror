# Casa Morales - CUARTO DE LUCÍA (1P, 6 x 6): pink latex walls with skirting and a few stickers, parquet, street
# window (2x2, blind up) on the north wall, door to the upstairs hall on the south wall (Door: opening), switch.
# casa_muebles: canopy bed, the doll shelf, desk. Also defines room() used by the other bedroom scenes.
import zlib


def h(*a):
    return zlib.crc32(repr(a).encode()) % 1000


def room(W, D, wall, floor='casa_parquet', H=3, win=None, win_mode='open', door_x=None, ceil='casa_cielorraso', damp=None):
    """Box room x 0..W-1, z 0..D-1. wall(x, y, z) -> key. 2x2 window centred on the north wall (facing north =
    outside); door opening on the south wall at door_x with its casing."""
    B = []
    for x in range(-1, W + 1):
        for z in range(-1, D + 1):
            B.append((x, -1, z, floor(x, z) if callable(floor) else floor, 'north'))
            B.append((x, H, z, 'casa_cielorraso_humedad' if (x, z) == damp else ceil, 'north'))
    wx = W // 2 - 1
    WIN = {}
    if win:
        for (x, side) in ((wx, 'der'), (wx + 1, 'izq')):
            WIN[(x, 1)] = f'casa_ventana_inf_{side}' + ('_cerrada' if win_mode == 'closed' else '')
            WIN[(x, 2)] = f'casa_ventana_sup_{side}' + ('_cerrada' if win_mode in ('closed', 'half') else '')
    for y in range(H):
        for x in range(-1, W + 1):
            B.append((x, y, -1, WIN[(x, y)] if (x, y) in WIN else wall(x, y, -1), 'north'))
            if not (x == door_x and y < 2):
                B.append((x, y, D, wall(x, y, D), 'north'))
        for z in range(D):
            B.append((-1, y, z, wall(-1, y, z), 'north'))
            B.append((W, y, z, wall(W, y, z), 'north'))
    if door_x is not None:
        B += [(door_x + 1, 1, D - 1, 'casa_contramarco_izq', 'north'), (door_x - 1, 1, D - 1, 'casa_contramarco_der', 'north'),
              (door_x, 2, D - 1, 'casa_contramarco_dintel', 'north'), (door_x + 2, 1, D - 1, 'casa_llave_luz', 'north'),
              (door_x, -1, D, 'casa_parquet_gastado', 'north')]
        for z in (D + 1, D + 2):
            B.append((door_x, -1, z, 'casa_parquet', 'north'))
            B.append((door_x, 0, z + 1, 'casa_pared_pasillo_zocalo', 'north'))
    return B


def lucia_wall(x, y, z):
    if y == 0:
        return 'casa_pared_lucia_zocalo'
    if y == 1 and h(x, z) < 330:
        return 'casa_pared_lucia_stickers'
    return 'casa_pared_lucia'


B = room(6, 6, lucia_wall, win=True, door_x=2, damp=(4, 1))
B += [(0, 0, 1, 'casa_cama_dosel_cabecera', 'east'), (1, 0, 1, 'casa_cama_dosel_pie', 'east'), (5, 1, 3, 'casa_estante_munecas_1', 'west'),
      (5, 1, 2, 'casa_estante_munecas_2', 'west'), (0, 0, 4, 'casa_escritorio_lucia', 'east'), (3, 0, 3, 'casa_alfombra_lucia', 'north'),
      (5, 0, 0, 'casa_enchufe', 'south')]
SCENE = dict(blocks=B, camera=(4.6, 1.62, 5.4), target=(1.2, 1.0, 0.0), fov=76)
