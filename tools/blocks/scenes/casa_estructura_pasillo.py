# Casa Morales - PASILLO 1P (2 x 12, chapter 6 'cascada de puertas'): the long red runner laid in two halves, pale
# aqua walls with skirting, four bedroom doors in a row with their cedar casings (Door blocks do not render in the
# preview: the openings show a glimpse of each room's wall - Lucía pink with stickers, Toti blue with posters, the
# master bedroom's 70s wallpaper, the bathroom tiles), a damp patch on the ceiling, light switch and outlet.
import zlib


def h(*a):
    return zlib.crc32(repr(a).encode()) % 1000


B = []
L = 12
DOORS = {1: ('casa_pared_lucia_stickers', 'casa_pared_lucia_zocalo'), 5: ('casa_pared_toti_poster', 'casa_pared_toti_zocalo'),
         9: ('casa_empapelado_matrimonial', 'casa_empapelado_matrimonial_zocalo')}
for z in range(-1, L + 1):
    for x in (0, 1):
        B.append((x, -1, z, 'casa_parquet_gastado' if h(x, z) < 300 else 'casa_parquet', 'north'))
        B.append((x, 3, z, 'casa_cielorraso_humedad' if (x, z) == (1, 7) else 'casa_cielorraso', 'north'))
        if 0 <= z < L:
            # facing north: izq (viewer's left = +x) is the x=1 half; facing south the halves swap
            if z == 0:
                k = 'casa_alfombra_punta_izq' if x == 0 else 'casa_alfombra_punta_der'
                B.append((x, 0, z, k, 'north'))
            elif z == L - 1:
                k = 'casa_alfombra_punta_der' if x == 1 else 'casa_alfombra_punta_izq'
                B.append((x, 0, z, k, 'south'))
            else:
                k = 'casa_alfombra_mancha' if False else ('casa_alfombra_izq' if x == 1 else 'casa_alfombra_der')
                B.append((x, 0, z, k, 'north'))
for y in range(3):
    for z in range(-1, L + 1):
        for x in (-1, 2):
            if x == 2 and z in DOORS and y < 2:
                wall, base = DOORS[z]
                B.append((3, -1, z, 'casa_parquet', 'north'))
                B.append((4, y, z, base if y == 0 else wall, 'north'))
                for zz in (z - 1, z + 1):
                    B.append((3, y, zz, base if y == 0 else wall, 'north'))
                continue
            k = 'casa_pared_pasillo_zocalo' if y == 0 else ('casa_pared_pasillo' if h(x, y, z) > 200 else 'casa_pared_pasillo')
            B.append((x, y, z, k, 'north'))
    for x in (0, 1):
        B.append((x, y, -1, 'casa_pared_pasillo_zocalo' if y == 0 else 'casa_pared_pasillo', 'north'))
        if not (x == 0 and y < 2):
            B.append((x, y, L, 'casa_pared_pasillo_zocalo' if y == 0 else 'casa_pared_pasillo', 'north'))
# the bathroom at the end of the corridor (door at x=0, z=L)
for y in range(2):
    B.append((0, y, L + 1, 'casa_azulejo_celeste' if y == 0 else 'casa_azulejo_celeste_guarda', 'north'))
B.append((0, -1, L, 'casa_piso_bano', 'north'))
# casings around the doors on the east wall (pieces face west, towards the corridor)
for z in DOORS:
    B += [(1, 1, z - 1, 'casa_contramarco_izq', 'west'), (1, 1, z + 1, 'casa_contramarco_der', 'west'), (1, 2, z, 'casa_contramarco_dintel', 'west')]
B += [(1, 1, L - 1, 'casa_contramarco_izq', 'south') if False else (1, 1, L - 1, 'casa_contramarco_der', 'north'),
      (0, 2, L - 1, 'casa_contramarco_dintel', 'north')]
B += [(0, 1, 3, 'casa_llave_luz', 'east'), (0, 0, 7, 'casa_enchufe', 'east') if False else (0, 1, 7, 'casa_llave_luz', 'east')]
SCENE = dict(blocks=B, camera=(0.45, 1.62, 0.15), target=(1.2, 1.0, 8.0), fov=74)
