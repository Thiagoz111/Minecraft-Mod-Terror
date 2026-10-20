# Close view of the presbytery (reuses the chapel layout).
import os
_ns = {}
exec(open(os.path.join('tools', 'blocks', 'scenes', 'colegio_muebles_capilla.py')).read(), _ns)
SCENE = dict(_ns['SCENE'], camera=(1.6, 1.7, 6.8), target=(-0.4, 1.5, 0.5), fov=70)
