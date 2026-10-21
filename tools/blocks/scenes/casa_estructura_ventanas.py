# Window test wall: a brick + render facade with three 2x2 windows (blind up, half down, down), the kitchen window
# (one leaf open) and the bathroom tilt window; living-room interior behind so the inside can be checked too.
import zlib


def h(*a):
    return zlib.crc32(repr(a).encode()) % 1000


B = []
for x in range(-3, 16):
    for z in range(-4, 6):
        k = 'casa_cesped' if z < 0 else 'casa_parquet'
        B.append((x, -1, z, k, 'north'))
WIN = {}
# window 1 at x=1..2 open, window 2 at x=5..6 half (sup closed), window 3 at x=9..10 closed: sill on y=1
for (x0, mode) in ((1, 'open'), (5, 'half'), (9, 'closed')):
    der, izq = x0, x0 + 1          # facing north: der (viewer's right) is at the lower x
    for (x, side) in ((der, 'der'), (izq, 'izq')):
        WIN[(x, 1)] = f'casa_ventana_inf_{side}' + ('_cerrada' if mode == 'closed' else '')
        WIN[(x, 2)] = f'casa_ventana_sup_{side}' + ('_cerrada' if mode in ('closed', 'half') else '')
WIN[(12, 2)] = 'casa_ventana_bano'
WIN[(13, 1)] = 'casa_ventana_cocina_der'
WIN[(14, 1)] = 'casa_ventana_cocina_izq_abierta'
for x in range(-1, 16):
    for y in range(0, 4):
        if (x, y) in WIN:
            B.append((x, y, 0, WIN[(x, y)], 'north'))
            continue
        if y == 0:
            k = 'casa_zocalo_ladrillo'
        elif y == 1:
            k = 'casa_ladrillo_salitre' if h(x, y) < 300 else 'casa_ladrillo_visto'
        else:
            k = 'casa_revoque_chorreado' if (y == 3 and h(x) < 400) else 'casa_revoque_blanco'
        B.append((x, y, 0, k, 'north'))
SCENE = dict(blocks=B, camera=(6.5, 1.7, -5.8), target=(6.5, 1.6, 0.5), fov=75)
