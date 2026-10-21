# The window test wall seen from inside (interior faces, sill board, blind box cover, strap and winder).
import os
exec(open(os.path.join('tools', 'blocks', 'scenes', 'casa_estructura_ventanas.py')).read())
SCENE = dict(blocks=B, camera=(3.5, 1.65, 3.6), target=(3.2, 1.7, 0.0), fov=75)
