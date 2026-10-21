"""Build + paint + render one entity for review.

    python3 tools/models/preview.py <key> [--pose spider]

Expects tools/models/ent_<key>.py exposing build() -> Model and DEFAULT_MAT (fallback material); --variant <name> paints a
look from VARIANT_MATS (calling build(variant=name) when the module accepts it),
optionally POSES = {name: {bone: (xRot, yRot, zRot, dx, dy, dz)}} (radians / model units) and FOCUS = 'head'.
Writes to <scratchpad>/models/<key>/: views.png, texture.png (8x, with face grid), texture_raw.png, layers.
Prints cube count, texture size and output paths.
"""
import importlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import render  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402


def texture_sheet(model, img, k=6):
    big = Image.new('RGBA', (img.width * k, img.height * k), (40, 36, 48, 255))
    chk = ImageDraw.Draw(big)
    for y in range(0, big.height, 2 * k):
        for x in range(0, big.width, 2 * k):
            chk.rectangle([x, y, x + k - 1, y + k - 1], fill=(48, 44, 56, 255))
    big.alpha_composite(img.resize(big.size, Image.NEAREST))
    d = ImageDraw.Draw(big)
    for b in model.bones():
        for c in b.cubes:
            if c.uv is None:
                continue
            for face in ('top', 'bottom', 'west', 'front', 'east', 'back'):
                u0, v0, w, h = model.face_rect(c, face)
                if w > 0 and h > 0:
                    d.rectangle([u0 * k, v0 * k, (u0 + w) * k - 1, (v0 + h) * k - 1], outline=(90, 220, 200, 90))
    return big


def main():
    key = sys.argv[1]
    pose_name = sys.argv[sys.argv.index('--pose') + 1] if '--pose' in sys.argv else None
    variant = sys.argv[sys.argv.index('--variant') + 1] if '--variant' in sys.argv else None
    mod = importlib.import_module('ent_' + key)
    mat = getattr(mod, 'DEFAULT_MAT', None)
    if variant:
        # a look from VARIANT_MATS; build(variant=...) may show that look's toggle bones
        mat = getattr(mod, 'VARIANT_MATS', {})[variant]
        try:
            model = mod.build(variant=variant).pack()
        except TypeError:
            model = mod.build().pack()
    else:
        model = mod.build().pack()
    img = model.paint(mat)
    out = os.path.join(render.SP, 'models', key)
    os.makedirs(out, exist_ok=True)
    img.save(os.path.join(out, 'texture_raw.png'))
    texture_sheet(model, img).save(os.path.join(out, 'texture.png'))
    for lay in model.layers():
        model.paint(mat, layer=lay).save(os.path.join(out, f'layer_{lay}.png'))
    pose = getattr(mod, 'POSES', {}).get(pose_name) if pose_name else None
    focus = getattr(mod, 'FOCUS', 'head')
    name = 'views' + (f'_{variant}' if variant else '') + (f'_{pose_name}' if pose_name else '') + '.png'
    render.render_views(model, img, os.path.join(out, name), focus_bone=focus, pose=pose)
    cubes = sum(len(b.cubes) for b in model.bones())
    print(f'{key}: {cubes} cubes, {sum(1 for _ in model.bones())} bones, texture {model.tex_w}x{model.tex_h}, scale {model.scale}')
    print('views  :', os.path.join(out, name))
    print('texture:', os.path.join(out, 'texture.png'))


if __name__ == '__main__':
    main()
