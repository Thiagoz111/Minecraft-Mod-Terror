B = []
for x in range(-3, 4):
    for z in range(-3, 4):
        B.append((x, -1, z, 'zz_parquet', 'north'))
for x in range(-3, 4):
    for y in range(0, 3):
        B.append((x, y, 4, 'zz_wallpaper', 'north'))
B.append((0, 0, 1, 'zz_chair', 'north'))
B.append((2, 0, 1, 'zz_chair', 'east'))
SCENE = dict(blocks=B, camera=(0.5, 1.6, -3.5), target=(0.5, 0.8, 3.0), fov=70)
