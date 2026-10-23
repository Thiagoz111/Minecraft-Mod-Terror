"""DEAD LINE item icon: the car keys (32x32), plus their item model definitions.

    python3 tools/art/item_car.py            writes textures/item/car_keys.png + models/item + items JSON
    python3 tools/art/item_car.py --preview  also writes a big preview into the work dir

Two old steel keys (single-sided blades, black bakelite heads) on a ring with a worn leather fob and a little tin
saint's medal. No brand, no logo.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
from px import Sprite, Material, upscale  # noqa: E402
from mats import STEEL, PLASTIC, LEATHER, SILVER  # noqa: E402

S = 32
RES = os.path.join(HERE, '..', '..', 'src/main/resources/assets/deadline')
BRASS = Material(['#2e1d08', '#56380f', '#80581c', '#a87c30', '#cba150', '#e8c97c'], spec=0.45, shininess=10)


def car_keys():
    s = Sprite(S, seed=211)
    # leather fob hanging from the ring
    s.poly([(3, 14), (8, 12), (11, 24), (5, 27)], LEATHER)
    # key 1: round black head + long steel blade to the right
    s.ellipse(17, 8, 4.2, 4.2, PLASTIC)
    s.rect(20, 7, 30, 9, STEEL, bevel=0.8)
    # key 2: the brass one, hanging down to the right
    s.ellipse(14.5, 17, 3.0, 3.0, PLASTIC)
    s.poly([(15, 19), (17, 19), (23, 29), (21, 30)], BRASS)
    # the ring
    ring = s.mask_ellipse(9, 10, 4.3, 4.3) & ~s.mask_ellipse(9, 10, 2.9, 2.9)
    s._apply(ring, SILVER, dome=True)
    img = s.render()
    px = img.load()
    # teeth under the steel blade, notches on the brass one
    for x in (22, 24, 25, 27, 29):
        px[x, 10] = (96, 102, 112, 255)
    for (x, y) in ((22, 26), (20, 23), (19, 21)):
        px[x, y] = (120, 86, 34, 255)
    # holes in the heads, stitches on the fob, the saint's medal on the fob
    px[15, 8] = px[15, 7] = (8, 8, 10, 255)
    px[13, 17] = (8, 8, 10, 255)
    for (x, y) in ((5, 16), (6, 19), (7, 22), (8, 25)):
        px[x, y] = (196, 160, 112, 255)
    for (x, y) in ((7, 17), (8, 17), (7, 18), (8, 18)):
        px[x, y] = (206, 210, 214, 255)
    px[7, 17] = (240, 244, 248, 255)
    # glints
    for (x, y) in ((16, 5), (22, 7), (7, 6), (14, 15)):
        px[x, y] = (255, 255, 255, 255)
    return img


def export():
    img = car_keys()
    os.makedirs(os.path.join(RES, 'textures/item'), exist_ok=True)
    img.save(os.path.join(RES, 'textures/item/car_keys.png'))
    for rel, obj in (('models/item/car_keys.json', {'parent': 'minecraft:item/generated', 'textures': {'layer0': 'deadline:item/car_keys'}}),
                     ('items/car_keys.json', {'model': {'type': 'minecraft:model', 'model': 'deadline:item/car_keys'}})):
        path = os.path.join(RES, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(obj, f, indent=2, ensure_ascii=False)
    return img


if __name__ == '__main__':
    im = export()
    if '--preview' in sys.argv:
        from workdir import WORK
        out = os.path.join(WORK, 'car_keys_preview.png')
        upscale(im, 12).save(out)
        print(out)
    print('car_keys written')
