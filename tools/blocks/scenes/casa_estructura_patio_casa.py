# Casa Morales - the back facade seen from the parrilla (same build as casa_estructura_patio).
ns = {}
exec(open('tools/blocks/scenes/casa_estructura_patio.py').read(), ns)
SCENE = dict(blocks=ns['B'], camera=(5.0, 1.62, 10.6), target=(4.5, 1.8, 0.0), fov=72)
