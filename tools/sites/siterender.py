"""Dev preview of a built site (day + night with flashlight), through the building-kit renderer.

    python3 tools/sites/siterender.py casa --camera X Y Z --target X Y Z [--box X0 Y0 Z0 X1 Y1 Z1] [--fov 70] [--name living]
    python3 tools/sites/siterender.py casa --point living          (camera at a marker point, looking along its yaw)

Renders the kit blocks of the site (vanilla blocks and blocks missing from tools/blocks/out are skipped), cropped to
--box (default: 14 blocks around the camera). Output: scratchpad/blocks/scene_site_<site>_<name>.png.
"""
import importlib
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'blocks'))
import brender  # noqa: E402


def parse(state):
    """'deadline:key[facing=east,half=lower]' -> (key, facing, props) or None for vanilla blocks."""
    if not state.startswith('deadline:'):
        return None
    body = state[len('deadline:'):]
    key, props = body, {}
    if '[' in body:
        key, rest = body[:-1].split('[', 1)
        props = dict(kv.split('=', 1) for kv in rest.split(',') if '=' in kv)
    return key, props.get('facing', 'north'), props


def arg(name, n, default=None, cast=float):
    if name not in sys.argv:
        return default
    i = sys.argv.index(name)
    vals = [cast(v) for v in sys.argv[i + 1:i + 1 + n]]
    return vals if n > 1 else vals[0]


def main():
    key = sys.argv[1]
    site = importlib.import_module(key).build()
    name = arg('--name', 1, None, str)
    point = arg('--point', 1, None, str)
    if point:
        x, y, z, yaw = site.markers['points'][point][:4]
        cam = [x + 0.5, y + 1.62, z + 0.5]
        a = math.radians(yaw or 0)
        tgt = [cam[0] - math.sin(a) * 6, cam[1] - 0.4, cam[2] + math.cos(a) * 6]
        name = name or point
    else:
        cam = arg('--camera', 3)
        tgt = arg('--target', 3)
    box = arg('--box', 6, None, int)
    if box is None:
        r = 14
        box = [int(cam[0]) - r, int(cam[1]) - 6, int(cam[2]) - r, int(cam[0]) + r, int(cam[1]) + 8, int(cam[2]) + r]
    x0, y0, z0, x1, y1, z1 = box
    blocks = []
    for (x, y, z), st in site.blocks.items():
        if x0 <= x <= x1 and y0 <= y <= y1 and z0 <= z <= z1:
            p = parse(st)
            if p and p[2].get('half') != 'upper':
                blocks.append((x, y, z, p[0], p[1]))
    scene = dict(blocks=blocks, camera=tuple(cam), target=tuple(tgt), fov=arg('--fov', 1, 70))
    out = os.path.join(brender.SP, 'sites')
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, f'site_{key}_{name or "view"}.py')
    with open(path, 'w') as f:
        f.write('SCENE = ' + repr(scene) + '\n')
    print(brender.scene(path))


if __name__ == '__main__':
    main()
