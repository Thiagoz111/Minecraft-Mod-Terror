from bkit import Cube, Furniture, Door, box, plane
from paint import hx, ramp, pick, edge_dark

PAPER = ramp('#8a6f5a', n=7, spread=0.5)
WOOD = ramp('#6b4226', n=7, spread=0.55)


def wallpaper(ctx):
    v = 0.55 + (0.06 if (ctx.i // 4 + ctx.j // 4) % 2 else -0.02)
    if (ctx.i % 8 == 3 and ctx.j % 8 in (2, 3, 4)) or (ctx.j % 8 == 3 and ctx.i % 8 in (2, 3, 4)):
        v += 0.18
    v -= 0.15 * ctx.rng.random() * (ctx.j > 24)
    return pick(PAPER, v)


def parquet(ctx):
    plank = (ctx.i // 8 + (ctx.j // 16) * 3) % 4
    v = 0.45 + plank * 0.06 + (0.08 if ctx.j % 16 == 0 or ctx.i % 8 == 0 else 0) * -1
    return pick(WOOD, v)


def chair_mat(ctx):
    return pick(WOOD, edge_dark(ctx, 0.55, 0.12))


def door_mat(ctx):
    v = 0.5
    if ctx.i in (0, 31) or (ctx.face == 'top' and ctx.j == 0) or (ctx.face == 'bottom' and ctx.j == 31):
        v -= 0.2
    if 5 <= ctx.i <= 26 and 5 <= ctx.j <= 26:
        v += 0.08
    return pick(WOOD, v)


Cube('zz_wallpaper', 'Papel tapiz', 'Wallpaper', mat=wallpaper, kit='zz', sound='plaster', variants=2)
Cube('zz_parquet', 'Parquet', 'Parquet', mat=parquet, kit='zz')
Furniture('zz_chair', 'Silla', 'Chair', kit='zz', mat=chair_mat, parts=[
    box((3, 0, 3), (5, 8, 5)), box((11, 0, 3), (13, 8, 5)), box((3, 0, 11), (5, 8, 13)), box((11, 0, 11), (13, 8, 13)),
    box((2, 8, 2), (14, 10, 14)), box((2, 10, 12), (14, 22, 14)),
])
Door('zz_door', 'Puerta', 'Door', mat=door_mat, kit='zz')
