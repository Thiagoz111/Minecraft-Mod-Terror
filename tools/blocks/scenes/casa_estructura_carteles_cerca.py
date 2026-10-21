# Closer still: the Nona's marker scribble, the number tile and the doorbell must read at arm's length.
import os
exec(open(os.path.join('tools', 'blocks', 'scenes', 'casa_estructura_carteles.py')).read())
SCENE = dict(blocks=B, camera=(3.0, 1.45, -1.3), target=(3.4, 1.2, 0.8), fov=70)
