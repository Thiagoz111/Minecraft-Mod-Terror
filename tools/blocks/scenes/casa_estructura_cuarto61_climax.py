# Casa Morales - the 1961 room at the climax (beat 15 'Los rayones en latín se iluminan'): the same build as
# casa_estructura_cuarto61 with the priest's Latin swapped for the glowing variant (light 7) and the camera on the
# west wall, the bed in the old salt circle and the soot tongue over the candle by the hole.
ns = {}
exec(open('tools/blocks/scenes/casa_estructura_cuarto61.py').read(), ns)
B = [(x, y, z, 'casa_rayones_latin_brillo' if k == 'casa_rayones_latin' else k, f) for (x, y, z, k, f) in ns['B']]
SCENE = dict(blocks=B, camera=(7.5, 1.55, 8.2), target=(0.0, 1.4, 4.0), fov=72)
