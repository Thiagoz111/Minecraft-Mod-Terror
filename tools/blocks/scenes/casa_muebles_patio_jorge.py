# Casa Morales - PATIO at night, beat 11 'LE FALTA SAL': Jorge is possessed. Blue fire in the parrilla, the knife
# board empty (the six knives are orbiting him), one knife already stuck in the medianera, Jorge's chair with Ofelia's
# place on it, the salt circle, the charcoal bag he dropped, the patio lamp off. Same layout as casa_muebles_patio.
ns = {}
exec(open('tools/blocks/scenes/casa_muebles_patio.py').read(), ns)
SWAP = {'casa_parrilla': 'casa_parrilla_azul', 'casa_cuchillos': 'casa_cuchillos_vacio', 'casa_aplique_patio': 'casa_aplique_patio_apagado',
        'casa_bolsa_carbon': 'casa_bolsa_carbon_volcada'}
B = [(x, y, z, SWAP.get(k, k), f) for (x, y, z, k, f) in ns['B']]
B += [(1, 1, ns['D'] - 1, 'casa_cuchillo_clavado', 'north'), (7, 1, ns['D'] - 1, 'casa_cuchillo_clavado', 'north'),
      (4, 0, 3, 'casa_cuchillo', 'north'), (5, 0, 2, 'casa_plato_roto', 'east')]
SCENE = dict(blocks=B, camera=(4.6, 1.5, 2.2), target=(4.4, 1.0, 7.0), fov=70)
