# Close-up of 'Es la humedad' (beats 1 and 11) on the living's north wall at flashlight distance: the plain stain and,
# one block to the left, the version with the face. Both must read as water soaking and darkening the paint.
ns = {}
exec(open('tools/blocks/scenes/casa_estructura_living.py').read(), ns)
B = [b for b in ns['B'] if b[3] != 'casa_mancha_humedad']
B += [(1, 0, 0, 'casa_mancha_humedad', 'south'), (-1 + 8, 0, 0, 'casa_mancha_humedad_cara', 'south')]
SCENE = dict(blocks=B, camera=(4.0, 1.4, 4.6), target=(4.0, 0.9, 0.0), fov=80)
