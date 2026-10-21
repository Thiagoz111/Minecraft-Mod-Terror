# Casa Morales - roof test: a small gable volume (7 wide x 7 deep, 4-block walls) with the 45-degree tile roof, eaves
# with gutters on both sides, the ridge, rendered gables and a downpipe at the front corner.
import zlib


def h(*a):
    return zlib.crc32(repr(a).encode()) % 1000


B = []
W, D, HW = 7, 7, 4          # x 0..6, z 0..6, walls y 0..3
for x in range(-4, W + 4):
    for z in range(-5, D + 3):
        k = 'casa_cesped'
        if -3 <= z <= -1:
            k = 'casa_vereda_rota' if h(x, z) < 180 else 'casa_vereda'
        if z == -4:
            k = 'casa_cordon'
        if z < -4:
            k = 'casa_asfalto'
        B.append((x, -1, z, k, 'north'))
for y in range(HW):
    for x in range(W):
        for z in (0, D - 1):
            if y == 0:
                k = 'casa_zocalo_ladrillo'
            elif y == 1:
                k = 'casa_ladrillo_visto' if h(x, y, z) > 150 else 'casa_ladrillo_salitre'
            else:
                k = 'casa_revoque_chorreado' if (y == HW - 1 and h(x, z) < 300) else 'casa_revoque_blanco'
            B.append((x, y, z, k, 'north'))
    for z in range(1, D - 1):
        for x in (0, W - 1):
            # rising damp along the whole west side wall (damp courses meet at the same height on every seam), dry east
            wet = x == 0
            k = ('casa_zocalo_revoque_humedad' if wet else 'casa_zocalo_revoque') if y == 0 else \
                ('casa_revoque_humedad' if (y == 1 and wet) else 'casa_revoque_blanco')
            B.append((x, y, z, k, 'north'))
# gable walls above the eave level (full blocks under the roof line)
for x in (0, W - 1):
    for (y, z) in ((4, 1), (4, 2), (4, 3), (4, 4), (4, 5), (5, 2), (5, 3), (5, 4), (6, 3)):
        B.append((x, y, z, 'casa_revoque_blanco', 'north'))
# roof: front slope faces north, back slope faces south
rows_f = [(4, 0, 'alero'), (5, 1, 'techo'), (6, 2, 'techo')]
rows_b = [(4, 6, 'alero'), (5, 5, 'techo'), (6, 4, 'techo')]
for x in range(W):
    for (y, z, kind) in rows_f:
        if x == 0:
            k = 'casa_hastial_alero_der' if kind == 'alero' else 'casa_hastial_der'
        elif x == W - 1:
            k = 'casa_hastial_alero_izq' if kind == 'alero' else 'casa_hastial_izq'
        else:
            k = 'casa_techo_alero' if kind == 'alero' else ('casa_techo_musgo' if h(x, y) < 250 else ('casa_techo_roto' if (x, y) == (3, 5) else 'casa_techo'))
        B.append((x, y, z, k, 'north'))
    for (y, z, kind) in rows_b:
        if x == 0:
            k = 'casa_hastial_alero_izq' if kind == 'alero' else 'casa_hastial_izq'
        elif x == W - 1:
            k = 'casa_hastial_alero_der' if kind == 'alero' else 'casa_hastial_der'
        else:
            k = 'casa_techo_alero_musgo' if kind == 'alero' else 'casa_techo_musgo'
        B.append((x, y, z, k, 'south'))
    k = 'casa_hastial_cumbrera_der' if x == 0 else ('casa_hastial_cumbrera_izq' if x == W - 1 else 'casa_techo_cumbrera')
    B.append((x, 7, 3, k, 'north'))
# downpipe at the front left: swan neck under the gutter, straight runs, shoe
B += [(1, 3, -1, 'casa_bajada_codo', 'north'), (1, 2, -1, 'casa_bajada', 'north'), (1, 1, -1, 'casa_bajada', 'north'),
      (1, 0, -1, 'casa_bajada_pie', 'north')]
SCENE = dict(blocks=B, camera=(-4.5, 2.4, -8.5), target=(3.2, 3.6, 2.0), fov=62)
