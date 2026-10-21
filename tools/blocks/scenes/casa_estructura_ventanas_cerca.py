# The window test wall, close from the outside: half-closed blind on the left, open on the right.
import os
exec(open(os.path.join('tools', 'blocks', 'scenes', 'casa_estructura_ventanas.py')).read())
SCENE = dict(blocks=B, camera=(4.6, 1.9, -2.6), target=(4.2, 1.8, 0.5), fov=72)
