# -*- coding: utf-8 -*-
"""DEAD LINE - the red face (B2 jumpscare 'cara_roja'; docs/design/casa_terror.md 5 #38 'detras_hombro', 7 Lemaza).

Lemaza never shows itself whole: the tall shadow, the visitor, the red face.  The jumpscare uses the anima's skull of a
face with its huge torn maw (tools/models/ent_anima.py, AnimaModelBase) painted RED: raw red skin, black pits for eyes
with an amber ember in them, the long teeth yellowed.  Painted from the module itself so the UVs always match
AnimaModelBase (rerun after `build_all.py anima`).

    python3 tools/art/hunt_cara_roja.py
writes textures/entity/hunt/cara_roja.png and cara_roja_eyes.png.
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'models'))
import ent_anima as S  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.join(ROOT, 'src/main/resources/assets/deadline/textures/entity/hunt')
FACE_BONES = ('head', 'jaw', 'neck', 'brow_right', 'brow_left', 'skull_back', 'cheek_right', 'cheek_left')
RED = np.array([[16, 2, 3], [46, 6, 6], [88, 12, 10], [128, 20, 14], [168, 30, 20], [202, 52, 34], [226, 88, 60]], float)


def ramp(v):
    v = np.clip(v, 0.0, 0.999) * (len(RED) - 1)
    i = np.floor(v).astype(int)
    f = (v - i)[..., None]
    return RED[i] * (1 - f) + RED[np.minimum(i + 1, len(RED) - 1)] * f


def main():
    m = S.build().pack()
    base = np.array(m.paint(S.DEFAULT_MAT).convert('RGBA')).astype(float)
    glow = np.array(m.paint(S.DEFAULT_MAT, layer='eyes').convert('RGBA')).astype(float) if 'eyes' in m.layers() else None
    mask = np.zeros(base.shape[:2], bool)
    jaw = np.zeros(base.shape[:2], bool)
    for b in m.bones():
        if b.name not in FACE_BONES:
            continue
        for c in b.cubes:
            u, v = c.uv
            w, h = c.uv_size()
            mask[v:v + h, u:u + w] = True
            if b.name == 'jaw':
                jaw[v:v + h, u:u + w] = True
    rgb = base[..., :3]
    lum = (0.3 * rgb[..., 0] + 0.59 * rgb[..., 1] + 0.11 * rgb[..., 2]) / 255.0
    ref = np.percentile(lum[mask & (base[..., 3] > 0)], 92) if mask.any() else 0.3
    skin = ramp(np.clip(lum / max(ref, 0.05), 0, 1) * 0.85 + 0.12)
    mx = rgb.max(-1)
    sat = (mx - rgb.min(-1)) / np.maximum(mx, 1.0)
    teeth = jaw & (lum > 0.6) & (sat < 0.45)                         # only the teeth stay pale: the skull goes red
    out = rgb.copy()
    out[mask] = skin[mask]
    out[mask & teeth] = np.array([214, 196, 150]) * (0.75 + 0.25 * lum[mask & teeth, None])
    out[mask & (lum < 0.035)] = np.array([4, 0, 1])                 # the pits stay black
    out[~mask] = rgb[~mask] * np.array([0.55, 0.2, 0.2])             # the rest of him sinks into red-black
    img = np.concatenate([np.clip(out, 0, 255), base[..., 3:4]], -1).astype(np.uint8)
    os.makedirs(OUT, exist_ok=True)
    Image.fromarray(img, 'RGBA').save(os.path.join(OUT, 'cara_roja.png'))
    if glow is not None:
        g = glow.copy()
        on = g[..., 3] > 0
        lg = (0.3 * g[..., 0] + 0.59 * g[..., 1] + 0.11 * g[..., 2]) / 255.0
        g[on, :3] = np.stack([255 * np.ones(on.sum()), 150 + 90 * lg[on], 40 + 60 * lg[on]], -1)  # amber embers
        Image.fromarray(g.astype(np.uint8), 'RGBA').save(os.path.join(OUT, 'cara_roja_eyes.png'))
    print('cara_roja written to', OUT, '(face texels:', int(mask.sum()), ')')


if __name__ == '__main__':
    main()
