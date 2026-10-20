# The confessional on the west wall and the baptismal font (reuses the chapel layout).
import os
_ns = {}
exec(open(os.path.join('tools', 'blocks', 'scenes', 'colegio_muebles_capilla.py')).read(), _ns)
SCENE = dict(_ns['SCENE'], camera=(-1.2, 1.6, 10.4), target=(-5.0, 1.0, 13.4), fov=70)
