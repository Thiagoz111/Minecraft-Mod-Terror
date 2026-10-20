# Turntable of multi-block pieces (wardrobe, curtain, beds) for close inspection.
B = [(0, 0, 0, 'colegio_ropero_abajo', 'north'), (0, 1, 0, 'colegio_ropero_arriba', 'north'),
     (2, 0, 0, 'colegio_cortina_blanca', 'north'), (3, 0, 0, 'colegio_cortina_blanca', 'north'),
     (5, 0, 0, 'colegio_cama_bulto_cabecera', 'north'), (5, 0, 1, 'colegio_cama_bulto_pie', 'north'),
     (6, 0, 0, 'colegio_cama_cabecera', 'north'), (6, 0, 1, 'colegio_cama_pie', 'north'),
     (7, 0, 0, 'colegio_cama_deshecha_cabecera', 'north'), (7, 0, 1, 'colegio_cama_deshecha_pie', 'north')]
for x in range(-1, 10):
    for z in range(-1, 4):
        B.append((x, -1, z, 'colegio_tablas', 'north'))
SCENE = dict(blocks=B, camera=(3.8, 2.6, -3.4), target=(3.8, 0.7, 0.8), fov=70)
