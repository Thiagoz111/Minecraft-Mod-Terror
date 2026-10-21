# The hall, looking straight at Lucía's door opening with its casing.
import os
exec(open(os.path.join('tools', 'blocks', 'scenes', 'casa_estructura_pasillo.py')).read())
SCENE = dict(blocks=B, camera=(0.2, 1.5, 1.5), target=(3.0, 1.1, 1.5), fov=70)
