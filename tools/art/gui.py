"""GUI textures for DEAD LINE: phone frame, wallpaper, app icons (messages, case, shop, bestiary), contact avatars, overlays."""
import math
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from px import Sprite, Material, glow, hexc, shade, lerp, ramp  # noqa: E402
from mats import *  # noqa: E402,F401

OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src/main/resources/assets/deadline/textures/gui'))
RNG = np.random.default_rng(7)


def save(img, name):
    p = os.path.join(OUT, name)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    img.save(p)
    return img


# ------------------------------------------------------------------ phone frame (192x352, screen at 8,22 176x308)
def phone_frame():
    W, H = 192, 352
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    a = np.zeros((H, W, 4), np.uint8)
    ys, xs = np.mgrid[0:H, 0:W]
    r = 22
    # rounded rectangle mask
    def rounded(x0, y0, x1, y1, rad):
        cx = np.clip(xs, x0 + rad, x1 - rad)
        cy = np.clip(ys, y0 + rad, y1 - rad)
        return (xs - cx) ** 2 + (ys - cy) ** 2 <= rad * rad
    body = rounded(0, 0, W - 1, H - 1, r)
    inner = rounded(3, 3, W - 4, H - 4, r - 3)
    screen = (xs >= 8) & (xs < 184) & (ys >= 22) & (ys < 330)
    # body gradient: gunmetal with light from top-left
    base = np.array([28, 29, 36])
    shadeval = 1.0 - (xs / W) * 0.25 - (ys / H) * 0.2
    col = (base[None, None, :] * shadeval[..., None]).clip(0, 255)
    a[body, :3] = col[body]
    a[body, 3] = 255
    # outer rim highlight / shadow
    rim = body & ~inner
    a[rim & (xs + ys < W), :3] = [86, 90, 108]
    a[rim & (xs + ys >= W), :3] = [12, 12, 16]
    a[screen] = [0, 0, 0, 0]
    # screen inner bevel
    edge = ((xs == 7) | (xs == 184) | (ys == 21) | (ys == 330)) & (xs >= 7) & (xs <= 184) & (ys >= 21) & (ys <= 330)
    a[edge] = [6, 6, 8, 255]
    img = Image.fromarray(a, 'RGBA').copy()
    px = img.load()
    # speaker grille + camera
    for x in range(80, 112):
        if x % 2 == 0:
            px[x, 11] = (8, 8, 10, 255)
            px[x, 12] = (50, 52, 64, 255)
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            if dx * dx + dy * dy <= 5:
                px[124 + dx, 11 + dy] = (14, 16, 30, 255)
    px[123, 10] = (90, 120, 200, 255)
    # home pill
    for x in range(78, 114):
        for y in range(338, 342):
            if not ((x in (78, 113)) and (y in (338, 341))):
                px[x, y] = (60, 62, 76, 255)
    # side buttons
    for y in range(70, 100):
        px[0, y] = (60, 62, 76, 255)
    for y in range(110, 150):
        px[W - 1, y] = (60, 62, 76, 255)
    return save(img, 'phone/frame.png')


def wallpaper():
    W, H = 176, 308
    ys, xs = np.mgrid[0:H, 0:W].astype(float)
    d = np.sqrt(((xs - W / 2) / W) ** 2 + ((ys - H * 0.42) / H) ** 2)
    t = np.clip(1 - d * 2.1, 0, 1) ** 1.8
    noise = RNG.normal(0, 0.035, (H, W))
    base = np.array([9, 4, 7], float)
    top = np.array([96, 10, 22], float)
    col = base[None, None] + (top - base)[None, None] * np.clip(t + noise, 0, 1)[..., None]
    # scanlines
    col[::2] *= 0.88
    a = np.dstack([col.clip(0, 255), np.full((H, W), 255)]).astype(np.uint8)
    img = Image.fromarray(a, 'RGBA').copy()
    px = img.load()
    # faint sigil: rings + inverted cross
    cx, cy = W // 2, int(H * 0.42)
    for r_, al in ((44, 70), (52, 40), (60, 22)):
        for k in range(720):
            ang = k / 720 * math.tau
            x, y = int(cx + math.cos(ang) * r_), int(cy + math.sin(ang) * r_)
            c = px[x, y]
            px[x, y] = lerp(c, (200, 30, 40, 255), al / 255)
    for y in range(cy - 30, cy + 30):
        for x in (cx - 1, cx, cx + 1):
            px[x, y] = lerp(px[x, y], (200, 30, 40, 255), 0.25)
    for x in range(cx - 14, cx + 15):
        for y in (cy + 12, cy + 13, cy + 14):
            px[x, y] = lerp(px[x, y], (200, 30, 40, 255), 0.25)
    return save(img, 'phone/wallpaper.png')


# ------------------------------------------------------------------ app icons (32x32 each, atlas 128x32)
def app_icon(bg, draw):
    s = Sprite(32, seed=5)
    m = Material(ramp(bg, 6, spread=0.4), spec=0.25)
    rr = s.mask_rect(1, 1, 30, 30)
    xs, ys = s._grid()
    corner = ((xs - 7) ** 2 + (ys - 7) ** 2 > 36) & (xs < 7) & (ys < 7)
    corner |= ((xs - 25) ** 2 + (ys - 7) ** 2 > 36) & (xs > 25) & (ys < 7)
    corner |= ((xs - 7) ** 2 + (ys - 25) ** 2 > 36) & (xs < 7) & (ys > 25)
    corner |= ((xs - 25) ** 2 + (ys - 25) ** 2 > 36) & (xs > 25) & (ys > 25)
    s._apply(rr & ~corner, m, bevel=2.5)
    draw(s)
    return s.render(outline=False)


def icons():
    def calls(s):
        # the messages app (there are no calls any more): a speech bubble with three dots of "escribiendo..."
        BUBBLE = Material(['#7a0d15', '#b4141f', '#e02a33', '#ff6a63', '#ffc2b8'], spec=0.5)
        s.ellipse(16, 14, 10.5, 8, BUBBLE)
        s.poly([(8, 18), (12, 20), (6, 26)], BUBBLE, bevel=0.5)
        DOT = Material(['#2a0406', '#3a070a', '#4a0a0e', '#5a0e12', '#6a1216'])
        for cx in (11.5, 16, 20.5):
            s.ellipse(cx, 14, 1.6, 1.6, DOT, outline=False)
    def case(s):
        FOLDER = Material(['#5c3d14', '#8a5d22', '#b88a3c', '#d9b062', '#f0d496'], spec=0.2)
        s.rect(6, 9, 26, 25, FOLDER, bevel=1.5)
        s.rect(6, 7, 14, 10, FOLDER, bevel=1)
        s.rect(9, 13, 23, 22, PAPER, bevel=0.5, outline=False)
    def shop(s):
        BAG = Material(['#0e3a24', '#16583a', '#227a50', '#3aa06c', '#7fd6a0'], spec=0.2)
        s.rect(8, 12, 24, 26, BAG, bevel=1.5)
        s.capsule(12, 12, 12, 7, 1.2, GOLD)
        s.capsule(20, 12, 20, 7, 1.2, GOLD)
        s.capsule(12, 7, 20, 7, 1.2, GOLD)
        s.ellipse(16, 19, 3.2, 3.2, GOLD)
    def best(s):
        s.rect(8, 6, 24, 26, LEATHER, bevel=1.5)
        s.rect(8, 6, 10, 26, Material(['#120404', '#240808', '#3a0e0c', '#521612']), bevel=1)
        s.ellipse(17, 14, 4.5, 4, BONE)
        s.rect(14, 17, 20, 20, BONE, bevel=0.6, outline=False)
    out = Image.new('RGBA', (128, 32))
    imgs = [app_icon('#3a0a10', calls), app_icon('#3a2a10', case), app_icon('#0e2a1e', shop), app_icon('#1a1020', best)]
    for i, im in enumerate(imgs):
        out.paste(im, (i * 32, 0))
    px = out.load()
    # skull eyes on the bestiary book
    for (x, y) in ((96 + 15, 14), (96 + 18, 14)):
        px[x, y] = (20, 8, 8, 255)
    # folder stamp
    for i in range(6):
        px[32 + 13 + i, 15 + i] = (170, 20, 30, 255)
        px[32 + 18 - i, 15 + i] = (170, 20, 30, 255)
    return save(out, 'phone/apps.png')


# ------------------------------------------------------------------ caller avatars (32x32 each)
SKIN = ['#f0c9a8', '#d9a47e', '#b07a55', '#8a5a3c', '#e8d6cc']


def avatar(bg, skin, hair, hair_style, cloth, extra=None, eyes='normal'):
    s = Sprite(32, seed=11)
    BG = Material(ramp(bg, 5, spread=0.3), ambient=1.0)
    s.rect(0, 0, 31, 31, BG, bevel=0.1, outline=False)
    C = Material(ramp(cloth, 6, spread=0.45))
    s.ellipse(16, 34, 14, 10, C, outline=False)
    SK = Material(ramp(skin, 6, spread=0.4))
    s.rect(13, 18, 18, 24, SK, bevel=1, outline=False)
    s.ellipse(16, 14, 7, 8.2, SK)
    H = Material(ramp(hair, 6, spread=0.45)) if hair else None
    if hair_style == 'short':
        s.ellipse(16, 8, 7.6, 3.8, H)
    elif hair_style == 'long':
        s.ellipse(16, 8, 8.2, 4.2, H)
        s.rect(8, 10, 10, 25, H, bevel=1)
        s.rect(22, 10, 24, 25, H, bevel=1)
    elif hair_style == 'bun':
        s.ellipse(16, 8, 7.6, 3.8, H)
        s.ellipse(16, 4, 3.4, 3, H)
    elif hair_style == 'cap':
        s.ellipse(16, 8, 8, 3.6, H)
        s.rect(16, 8, 25, 9, H, bevel=0.5)
    elif hair_style == 'hat':
        s.rect(5, 8, 27, 9, H, bevel=0.5)
        s.rect(10, 2, 22, 8, H, bevel=1)
    elif hair_style == 'veil':
        s.ellipse(16, 12, 10, 11, H)
        s.ellipse(16, 14, 6.5, 7.6, SK, outline=False)
    elif hair_style == 'mitre':
        s.poly([(10, 9), (16, 0), (22, 9)], H, bevel=1)
    img = s.render()
    px = img.load()
    if eyes == 'normal':
        for x in (12, 18):
            px[x, 15] = (235, 230, 225, 255)
            px[x + 1, 15] = (30, 22, 20, 255)
        for x in range(14, 18):
            px[x, 19] = shade(hexc(skin), 0.62)
        px[15, 17] = shade(hexc(skin), 0.8)
    elif eyes == 'white':
        for x in (12, 13, 18, 19):
            px[x, 14] = (245, 245, 235, 255)
        for x in range(12, 20):
            px[x, 19] = (40, 4, 8, 255)
        px[11, 18] = px[20, 18] = (40, 4, 8, 255)
    elif eyes == 'none':
        pass
    if extra:
        extra(px)
    return img


def unknown_avatar(seed):
    rng = np.random.default_rng(seed)
    a = rng.integers(0, 70, (32, 32))
    img = Image.fromarray(np.dstack([a, a, a, np.full((32, 32), 255)]).astype(np.uint8), 'RGBA').copy()
    px = img.load()
    skull = ['..#####..', '.#######.', '##..#..##', '###.#.###', '.#######.', '..#.#.#..']
    for j, row in enumerate(skull):
        for i, ch in enumerate(row):
            if ch == '#':
                px[12 + i, 12 + j] = (200, 20, 30, 255)
    return img


def collar(px):
    for x in range(14, 18):
        px[x, 24] = (240, 240, 240, 255)


def badge(px):
    for x in range(19, 22):
        for y in range(26, 29):
            px[x, y] = (220, 190, 60, 255)


def glasses(px):
    for x in (12, 13, 14, 17, 18, 19):
        px[x, 14] = (20, 20, 20, 255)
    px[15, 14] = px[16, 14] = (20, 20, 20, 255)


def blood(px):
    for (x, y) in ((12, 16), (12, 17), (19, 17), (19, 18), (15, 20)):
        px[x, y] = (120, 8, 14, 255)


AVATARS = {
    'casa': [
        lambda: avatar('#3b2a3a', SKIN[0], '#4a2a18', 'bun', '#6a4a7a'),
        lambda: avatar('#20202a', SKIN[1], '#2a2a2a', 'short', '#111111', collar),
        lambda: avatar('#2a2a30', '#9a9a9a', None, 'none', '#444444', eyes='none'),
        lambda: avatar('#2a3040', SKIN[2], '#1a1410', 'short', '#2a4a6a'),
        lambda: avatar('#1a0a10', '#bdbdb5', '#24140c', 'long', '#d8d2c8', blood, eyes='white'),
    ],
    'rio': [
        lambda: avatar('#203030', SKIN[3], '#3a3020', 'hat', '#3a5a3a'),
        lambda: avatar('#30283a', SKIN[1], '#1a1010', 'long', '#7a3a4a'),
        lambda: avatar('#1a2030', SKIN[2], '#101828', 'cap', '#1a2a4a', badge),
        lambda: unknown_avatar(1),
    ],
    'bosque': [
        lambda: avatar('#203020', SKIN[2], '#4a3a1a', 'hat', '#3a4a2a', badge),
        lambda: avatar('#30202a', SKIN[0], '#c08a40', 'long', '#a0402a'),
        lambda: avatar('#2a2420', SKIN[3], '#5a3a1a', 'cap', '#5a4a2a'),
        lambda: unknown_avatar(2),
    ],
    'parque': [
        lambda: avatar('#20202a', SKIN[2], '#3a3a3a', 'cap', '#2a2a4a'),
        lambda: avatar('#2a3040', SKIN[0], '#6a3a1a', 'short', '#c03a3a'),
        lambda: avatar('#302a20', SKIN[1], '#2a1a10', 'short', '#4a4a4a', glasses),
        lambda: unknown_avatar(3),
    ],
    'convento': [
        lambda: avatar('#20202a', SKIN[4], '#101010', 'veil', '#101010'),
        lambda: avatar('#2a1020', SKIN[1], '#e8e8e8', 'mitre', '#7a1020'),
        lambda: avatar('#2a2a3a', SKIN[0], '#4a3020', 'short', '#e8e8e8'),
        lambda: unknown_avatar(4),
    ],
}


def avatars():
    rows = list(AVATARS.items())
    out = Image.new('RGBA', (32 * 5, 32 * len(rows)))
    for r, (key, fns) in enumerate(rows):
        for c, fn in enumerate(fns):
            out.paste(fn(), (c * 32, r * 32))
    return save(out, 'phone/avatars.png')


# ------------------------------------------------------------------ overlays
def static_noise():
    S = 256
    rng = np.random.default_rng(9)
    v = rng.integers(0, 256, (S, S))
    a = rng.integers(60, 200, (S, S))
    img = np.dstack([v, v, v, a]).astype(np.uint8)
    # horizontal tearing bands
    for _ in range(14):
        y = rng.integers(0, S)
        h = rng.integers(1, 4)
        img[y:y + h, :, :3] = 255
        img[y:y + h, :, 3] = 120
    return save(Image.fromarray(img, 'RGBA'), 'overlay/static.png')


if __name__ == '__main__':
    phone_frame(); wallpaper(); icons(); avatars()
    static_noise()
    print('gui textures ->', OUT)
