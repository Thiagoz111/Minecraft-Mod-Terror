# Close-up of the roof test: eave, gutter, swan neck and the gable verge.
import os
exec(open(os.path.join('tools', 'blocks', 'scenes', 'casa_estructura_techo.py')).read())
SCENE = dict(blocks=B, camera=(-1.6, 3.2, -2.6), target=(1.5, 4.2, 0.5), fov=60)
