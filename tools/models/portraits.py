"""Render the jumpscare / bestiary portraits (512x512) for every creature module.

    python3 tools/models/portraits.py [key ...]
"""
import importlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import render  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.join(ROOT, 'src/main/resources/assets/deadline/textures/gui/jumpscare')
KEYS = ['llorona', 'wendigo', 'poseida', 'payaso', 'monja', 'sombra', 'muneca', 'anima']


def portrait(key):
    mod = importlib.import_module('ent_' + key)
    m = mod.build().pack()
    mat = getattr(mod, 'DEFAULT_MAT', None)
    img = m.paint(mat)
    glow = m.paint(mat, layer='eyes') if 'eyes' in m.layers() else None
    poses = getattr(mod, 'POSES', {}) or {}
    pose = {'head': (0.12, 0, 0, 0, 0, 0)}
    for name in ('attack', 'scream', 'laugh'):
        if name in poses and 'jaw' in poses[name]:
            pose['jaw'] = poses[name]['jaw']
            break
    os.makedirs(OUT, exist_ok=True)
    render.render_portrait(m, img, os.path.join(OUT, key + '.png'), getattr(mod, 'FOCUS', 'head'), pose, glow,
                           size=512, angle=0, elev=-6, zoom=1.0)


if __name__ == '__main__':
    for k in sys.argv[1:] or KEYS:
        try:
            portrait(k)
            print('portrait', k)
        except Exception as e:
            print('skip', k, e)
