"""Refresh the gallery with the current state of every ent_<key>.py (in-progress redesigns included).

Writes tools/preview/models/<key>.json + tools/preview/tex/<key>.png for each model that builds cleanly; models
that fail (mid-edit) keep their previous snapshot. Then rebuilds the gallery HTML.
"""
import importlib
import json
import os
import sys
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'tools/models'))
sys.path.insert(0, HERE)
KEYS = ['llorona', 'wendigo', 'poseida', 'payaso', 'monja', 'sombra', 'muneca', 'anima']


def snap(key):
    mod = importlib.import_module('ent_' + key)
    if not hasattr(mod, 'DEFAULT_MAT'):
        return False
    m = mod.build().pack()
    img = m.paint(mod.DEFAULT_MAT)
    os.makedirs(os.path.join(HERE, 'tex'), exist_ok=True)
    img.save(os.path.join(HERE, 'tex', key + '.png'))
    for lay in m.layers():
        m.paint(mod.DEFAULT_MAT, layer=lay).save(os.path.join(HERE, 'tex', f'{key}_{lay}.png'))
    data = m.to_json()
    data['poses'] = getattr(mod, 'POSES', {})
    json.dump(data, open(os.path.join(HERE, 'models', key + '.json'), 'w'))
    return True


if __name__ == '__main__':
    done = []
    for k in (sys.argv[2:] if len(sys.argv) > 2 else KEYS):
        try:
            if snap(k):
                done.append(k)
        except Exception:
            print('skip', k, traceback.format_exc().splitlines()[-1])
    print('snapshot', done)
    import build_gallery
    build_gallery.build(sys.argv[1] if len(sys.argv) > 1 else '/tmp/gallery.html')
