"""Placeholder photos for the phone's text threads (com.deadline.phone.PhoneMessages.photo).

Writes src/main/resources/assets/deadline/textures/gui/photo/<id>.png, 128x96: dark, grainy phone shots with a vague
shape in them so the bubble reads as a photo. Real art comes later (same ids, same size).

Run from the repo root:  python3 tools/art/photos.py
"""
import os

import numpy as np
from PIL import Image

W, H = 128, 96
OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src/main/resources/assets/deadline/textures/gui/photo'))


def _base(seed, tint=(1.0, 0.95, 0.85), level=34.0):
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    # a low-light phone shot: dark, warm cast, heavy sensor noise, vignette
    vig = 1.0 - 0.75 * (((x - W / 2) / (W / 2)) ** 2 + ((y - H / 2) / (H / 2)) ** 2) / 2
    lum = level * np.clip(vig, 0.15, 1.0)
    lum = lum + rng.normal(0, 7.0, (H, W))
    return rng, x, y, lum, tint


def _figure(lum, x, y, cx, top, bottom, half_w, darkness):
    """A tall, thin silhouette (head + body tapering to the floor)."""
    h = bottom - top
    t = np.clip((y - top) / max(1.0, h), 0, 1)
    width = half_w * (0.55 + 0.45 * t)
    body = (np.abs(x - cx) < width) & (y > top + h * 0.12) & (y < bottom)
    head = ((x - cx) ** 2 / (half_w * 0.6) ** 2 + (y - (top + h * 0.06)) ** 2 / (h * 0.07) ** 2) < 1
    m = body | head
    lum[m] = lum[m] * (1 - darkness)
    return m


def _save(name, lum, tint):
    rgb = np.stack([lum * tint[0], lum * tint[1], lum * tint[2]], -1)
    img = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8), 'RGB').convert('RGBA')
    os.makedirs(OUT, exist_ok=True)
    img.save(os.path.join(OUT, name + '.png'))


def pasillo_nona():
    """A dark hallway; far at the end, an old woman with her back turned, too tall."""
    rng, x, y, lum, tint = _base(61)
    # corridor perspective: floor and ceiling lines converging, a faint light at the end
    end = (np.abs(x - 64) < 14) & (np.abs(y - 44) < 20)
    lum[end] += 26
    walls = np.abs(x - 64) > (14 + np.abs(y - 44) * 1.6)
    lum[walls] *= 0.55
    _figure(lum, x, y, 66, 18, 64, 5.5, 0.85)
    _save('pasillo_nona', lum, tint)


def foto_familia_61():
    """1961: a faded group photo, sepia, one face scratched out."""
    rng, x, y, lum, _ = _base(1961, level=70.0)
    lum = lum * 0.9 + 18
    for i, cx in enumerate((26, 46, 66, 86, 104)):
        _figure(lum, x, y, cx, 30 + (i % 2) * 6, 92, 7.0, 0.55)
    scratch = (np.abs((x - 66) - (y - 34) * 0.4) < 1.2) & (y > 26) & (y < 46)
    lum[scratch] = 150
    _save('foto_familia_61', lum, (1.0, 0.82, 0.6))


def espalda_jugador():
    """You, from behind, taken from inside the house (someone was right there)."""
    rng, x, y, lum, tint = _base(404, level=30.0)
    # shoulders and the back of a head filling the lower half, very close
    shoulders = ((x - 64) ** 2 / 52 ** 2 + (y - 112) ** 2 / 46 ** 2) < 1
    head = ((x - 64) ** 2 / 17 ** 2 + (y - 52) ** 2 / 20 ** 2) < 1
    lum[shoulders | head] *= 0.2
    _save('espalda_jugador', lum, tint)


def final_familia():
    """The family in the 1961 room, smiling, and someone new in the middle."""
    rng, x, y, lum, _ = _base(2026, level=42.0)
    for cx in (20, 40, 88, 108):
        _figure(lum, x, y, cx, 28, 92, 7.0, 0.7)
    m = _figure(lum, x, y, 64, 22, 92, 8.0, 0.4)
    # white eyes on the one in the middle
    for ex in (61, 67):
        lum[(np.abs(x - ex) < 1.2) & (np.abs(y - 29) < 0.8)] = 230
    _save('final_familia', lum, (1.0, 0.9, 0.8))


PHOTOS = {'pasillo_nona': pasillo_nona, 'foto_familia_61': foto_familia_61, 'espalda_jugador': espalda_jugador,
          'final_familia': final_familia}

if __name__ == '__main__':
    for fn in PHOTOS.values():
        fn()
    print('photos ->', OUT, sorted(PHOTOS))
