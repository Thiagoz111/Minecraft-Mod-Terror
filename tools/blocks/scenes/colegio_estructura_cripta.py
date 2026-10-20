# Cripta bajo la capilla: mampostería húmeda, bóveda de escaleras invertidas, nichos con lápidas (Garay, Roldán,
# Iturbe, el nicho vacío de Sor María), al fondo el muro de ladrillo de 1984 con la grieta y un hueco.
B = []
W0, W1 = -2, 2
L = 12
for z in range(0, L + 1):
    for x in range(W0, W1 + 1):
        B.append((x, -1, z, 'colegio_cripta_piso', 'north'))
        B.append((x, 4, z, 'colegio_cripta_piedra', 'north'))
    # vault springing: upside-down stairs along both sides
    B.append((W0, 3, z, 'colegio_cripta_escalera', 'west:top'))
    B.append((W1, 3, z, 'colegio_cripta_escalera', 'east:top'))
    for x in (W0 - 1, W1 + 1):
        for y in range(0, 4):
            key = 'colegio_cripta_piedra'
            fac = 'east' if x < 0 else 'west'
            if y == 1 and z in (3, 6, 9):
                names = {(W0 - 1, 3): 'colegio_nicho_garay', (W0 - 1, 6): 'colegio_nicho_roldan',
                         (W0 - 1, 9): 'colegio_nicho_sellado', (W1 + 1, 3): 'colegio_nicho_iturbe',
                         (W1 + 1, 6): 'colegio_nicho_agonia', (W1 + 1, 9): 'colegio_nicho_roto'}
                key = names[(x, z)]
            B.append((x, y, z, key, fac))
for x in range(W0 - 1, W1 + 2):
    for y in range(0, 4):
        key = 'colegio_muro_ladrillo'
        if x == 0 and y in (0, 1, 2):
            key = 'colegio_muro_ladrillo_grieta'
        if (x, y) == (1, 1):
            key = 'colegio_muro_ladrillo_hueco'
        B.append((x, y, L + 1, key, 'north'))
    for y in range(0, 5):
        B.append((x, y, -1, 'colegio_cripta_piedra', 'north'))
SCENE = dict(blocks=B, camera=(0.4, 1.6, 0.5), target=(0.2, 1.3, 12.0), fov=70)
