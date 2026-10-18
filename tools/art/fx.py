"""Particle sprites, block textures and the mod icon for DEAD LINE (hand-shaped pixel art, numpy)."""
import math
import os

import numpy as np
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src/main/resources/assets/deadline'))
PART = os.path.join(ROOT, 'textures/particle')
BLOCK = os.path.join(ROOT, 'textures/block')
RNG = np.random.default_rng(13)


def hx(h, a=255):
    h = h.lstrip('#')
    return np.array([int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a], np.uint8)


def canvas(n):
    return np.zeros((n, n, 4), np.uint8)


def put(img, x, y, c):
    n = img.shape[0]
    if 0 <= x < n and 0 <= y < n:
        img[y, x] = c


def save(img, folder, name):
    os.makedirs(folder, exist_ok=True)
    Image.fromarray(img, 'RGBA').save(os.path.join(folder, name + '.png'))


def blob(n, cx, cy, r, ramp, seed=0, wob=0.6):
    """Soft round blob shaded with a ramp (dark edge -> bright core, light from top-left)."""
    img = canvas(n)
    for y in range(n):
        for x in range(n):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            ang = math.atan2(dy, dx)
            rr = r * (1 + wob * 0.18 * math.sin(ang * 3 + seed) + wob * 0.1 * math.sin(ang * 5 + seed * 2))
            d = math.hypot(dx, dy) / max(0.01, rr)
            if d > 1.0:
                continue
            lightv = 1 - d + 0.35 * (-(dx + dy) / max(1, rr * 2))
            k = int(max(0, min(len(ramp) - 1, round(lightv * (len(ramp) - 1) * 1.4))))
            img[y, x] = ramp[k]
    return img


# ------------------------------------------------------------------ particles
def ectoplasm():
    ramp = [hx('#0f4a26'), hx('#1f8a3c'), hx('#46d158'), hx('#9dff7a'), hx('#e9ffd2')]
    for f, r in enumerate([3.6, 3.0, 2.3, 1.5]):
        img = blob(8, 4, 3.6 + f * 0.25, r, ramp, seed=f)
        # dripping tail
        if f < 3:
            for t in range(2 - f // 2):
                put(img, 4, int(3.6 + r + t), ramp[2 - min(2, t)])
        save(img, PART, f'ectoplasm_{f}')


def holy_spark():
    core, mid, edge = hx('#fffbe6'), hx('#ffd45a'), hx('#d9822b')
    for f in range(4):
        img = canvas(8)
        arm = 3 - f
        for i in range(-arm, arm + 1):
            c = core if abs(i) <= max(0, arm - 2) else (mid if abs(i) < arm else edge)
            put(img, 3 + i, 3, c)
            put(img, 3, 3 + i, c)
            put(img, 4 + i, 4, c)
            put(img, 4, 4 + i, c)
        if f < 2:
            for dx, dy in ((-2, -2), (2, -2), (-2, 2), (2, 2)):
                put(img, (3 if dx < 0 else 4) + dx, (3 if dy < 0 else 4) + dy, edge)
        for x, y in ((3, 3), (4, 3), (3, 4), (4, 4)):
            put(img, x, y, core)
        save(img, PART, f'holy_spark_{f}')


def demon_smoke():
    ramp = [hx('#0b0306', 210), hx('#1d070b', 220), hx('#3a0d12', 230), hx('#5e1a1c', 235), hx('#84302a', 240)]
    for f in range(6):
        img = canvas(8)
        k = f / 5
        puffs = [(3.5, 4.5, 2.6 + k), (5.2, 3.2, 1.6 + k * 0.8), (2.4, 2.6, 1.4 + k * 0.7)]
        for (cx, cy, r) in puffs:
            b = blob(8, cx, cy - k * 0.8, min(3.8, r), ramp, seed=f * 3 + cx, wob=1.0)
            m = b[..., 3] > 0
            img[m] = b[m]
        # break up late frames
        if f >= 3:
            holes = RNG.random((8, 8)) < (f - 2) * 0.16
            img[holes] = 0
        save(img, PART, f'demon_smoke_{f}')


def wisp():
    ramp = [hx('#2a5a8a', 200), hx('#4aa0d8', 220), hx('#9ae6ff'), hx('#e6fbff')]
    for f in range(4):
        img = canvas(8)
        sway = [0, 1, 0, -1][f]
        # flame body
        for y in range(1, 8):
            w = [0, 1, 1, 2, 2, 2, 2, 1][y]
            cx = 3.5 + (sway * (7 - y) / 7.0)
            for x in range(8):
                d = abs(x + 0.5 - cx)
                if d <= w:
                    k = 3 if d < w * 0.4 and y > 3 else 2 if d < w * 0.8 else 1
                    if y == 1:
                        k = 1
                    put(img, x, y, ramp[k])
        put(img, int(3.5 + sway), 0, ramp[0])
        save(img, PART, f'wisp_{f}')


def salt_sparkle():
    w, g = hx('#ffffff'), hx('#cfd6e6')
    img = canvas(8)
    for p in ((3, 2), (3, 3), (3, 4), (2, 3), (4, 3)):
        put(img, *p, w)
    put(img, 6, 6, g)
    save(img, PART, 'salt_sparkle_0')
    img = canvas(8)
    put(img, 3, 3, w)
    put(img, 2, 2, g)
    put(img, 4, 4, g)
    save(img, PART, 'salt_sparkle_1')


def blood_drip():
    d, m, l, hl = hx('#3a0207'), hx('#6e0a12'), hx('#a3141d'), hx('#e0545a')
    shapes = [
        ["...m....", "...m....", "..mlm...", "..mlm...", ".dmlhm..", ".dmllm..", "..dmm...", "........"],
        ["........", "........", "..mmm...", ".mlllm..", ".mlhlm..", ".dmllm..", "..ddd...", "........"],
        ["........", "........", "........", "........", ".m.m..m.", "dmlllmmd", ".ddmmdd.", "........"],
    ]
    pal = {'d': d, 'm': m, 'l': l, 'h': hl}
    for f, rows in enumerate(shapes):
        img = canvas(8)
        for y, row in enumerate(rows):
            for x, ch in enumerate(row):
                if ch in pal:
                    put(img, x, y, pal[ch])
        save(img, PART, f'blood_drip_{f}')


def handprint():
    img = canvas(16)
    col = [hx('#4b1f8a', 150), hx('#7a3fd6', 200), hx('#b48cff', 230), hx('#ecdcff', 255)]
    palm = (8.0, 10.5, 3.6)
    for y in range(16):
        for x in range(16):
            d = math.hypot((x + 0.5 - palm[0]) / 1.05, (y + 0.5 - palm[1]) / 0.95) / palm[2]
            if d <= 1:
                k = 3 if d < 0.35 else 2 if d < 0.7 else 1
                if RNG.random() < 0.12:
                    k = max(0, k - 1)
                img[y, x] = col[k]
    fingers = [(4.0, 8.5, -0.55, 4), (6.3, 6.6, -0.18, 5), (8.6, 6.2, 0.0, 5.5), (10.8, 6.8, 0.18, 5), (12.6, 9.2, 0.75, 3.5)]
    for fx_, fy, ang, ln in fingers:
        for t in np.linspace(0, ln, 14):
            x = fx_ + math.sin(ang) * t
            y = fy - math.cos(ang) * t
            for ox in (0, 1):
                xi, yi = int(x + ox * 0.6), int(y)
                k = 2 if t < ln - 1 else 3
                put(img, xi, yi, col[k] if ox == 0 else col[1])
    # smear / drips under the palm
    for x in (6, 9):
        for y in range(14, 16):
            put(img, x, y, col[0])
    save(img, PART, 'handprint_0')


def cold_breath():
    ramp = [hx('#9fb6cc', 70), hx('#c9d9e8', 110), hx('#eef6ff', 150), hx('#ffffff', 180)]
    for f in range(4):
        img = blob(8, 4, 4, 1.8 + f * 0.6, ramp, seed=f * 1.7, wob=1.2)
        if f >= 2:
            holes = RNG.random((8, 8)) < (f - 1) * 0.2
            img[holes] = 0
        save(img, PART, f'cold_breath_{f}')


# ------------------------------------------------------------------ blocks
def salt_line():
    img = canvas(16)
    cols = [hx('#d7dce6'), hx('#eef2f8'), hx('#ffffff'), hx('#b9c0cf')]
    # a granular band running north-south and east-west so rotations read as a continuous ring
    for y in range(16):
        for x in range(16):
            band = min(abs(x - 7.5), abs(y - 7.5))
            p = 0.92 if band < 1.6 else 0.45 if band < 3.0 else 0.06
            if RNG.random() < p:
                img[y, x] = cols[RNG.integers(0, 4)]
    save(img, BLOCK, 'salt_line')


def blood_stains():
    pal = [hx('#2a0105'), hx('#4d040b'), hx('#760a13'), hx('#9e1620'), hx('#d24a4f')]
    for v in range(4):
        rng = np.random.default_rng(100 + v)
        img = canvas(16)
        blobs = [(8 + rng.normal(0, 1), 8 + rng.normal(0, 1), 3.2 + rng.random() * 1.8)]
        for _ in range(3 + v * 2):
            a = rng.random() * math.tau
            d = 3 + rng.random() * 4.5
            blobs.append((8 + math.cos(a) * d, 8 + math.sin(a) * d, 0.6 + rng.random() * 1.3))
        field = np.zeros((16, 16))
        for (cx, cy, r) in blobs:
            for y in range(16):
                for x in range(16):
                    dd = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
                    field[y, x] = max(field[y, x], 1 - dd / r)
        # streaks from the centre
        for _ in range(2 + v):
            a = rng.random() * math.tau
            for t in np.linspace(2, 7.5, 12):
                x, y = int(8 + math.cos(a) * t), int(8 + math.sin(a) * t)
                if 0 <= x < 16 and 0 <= y < 16:
                    field[y, x] = max(field[y, x], 0.25)
        for y in range(16):
            for x in range(16):
                f = field[y, x]
                if f <= 0:
                    continue
                k = 0 if f < 0.18 else 1 if f < 0.35 else 2 if f < 0.6 else 3
                if f > 0.6 and (x + y) % 5 == 0 and y < 9:
                    k = 4
                img[y, x] = pal[k]
        save(img, BLOCK, f'blood_stain_{v}')


def ritual_candle():
    for lit in (False, True):
        img = canvas(16)
        wax = [hx('#120a0e'), hx('#1f1218'), hx('#2e1b22')]
        drip = [hx('#5a0a12'), hx('#8c1520')]
        for y in range(6, 16):
            for x in range(2):
                img[y, x] = wax[(x + (y % 3 == 0)) % 3]
        # top of the candle (uv 0,6 - 2,8): melted pool
        img[6, 0] = drip[1]
        img[6, 1] = drip[0]
        img[7, 0] = drip[0]
        # red wax runs
        for y in (8, 9, 10):
            img[y, 0] = drip[1] if y < 10 else drip[0]
        img[12, 1] = drip[0]
        # wick
        img[5, 0] = hx('#ffcf6a') if lit else hx('#2a2420')
        save(img, BLOCK, 'ritual_candle_lit' if lit else 'ritual_candle')


# ------------------------------------------------------------------ mod icon (128x128)
def icon():
    n = 128
    img = np.zeros((n, n, 4), np.uint8)
    for y in range(n):
        for x in range(n):
            d = math.hypot(x - 64, y - 70) / 90
            r = int(120 * max(0, 1 - d) + 10)
            img[y, x] = (r, 6, 12, 255)
    av = Image.open(os.path.join(ROOT, 'textures/gui/phone/frame.png')).convert('RGBA')
    ph = av.resize((44, 81), Image.NEAREST)
    base = Image.fromarray(img, 'RGBA')
    # glowing screen with the unknown caller skull
    scr = Image.new('RGBA', (40, 70), (8, 6, 10, 255))
    skull = Image.open(os.path.join(ROOT, 'textures/gui/phone/avatars.png')).convert('RGBA').crop((96, 32, 128, 64)).resize((32, 32), Image.NEAREST)
    scr.alpha_composite(skull, (4, 16))
    base.alpha_composite(scr.resize((80, 140), Image.NEAREST).crop((0, 0, 80, 140)), (24, 0) if False else (24, -6))
    big = ph.resize((88, 162), Image.NEAREST)
    base.alpha_composite(big.crop((0, 0, 88, 128)), (20, 0))
    # cracks
    px = base.load()
    rng = np.random.default_rng(3)
    for _ in range(3):
        x, y = 64 + rng.integers(-6, 6), 40 + rng.integers(-6, 6)
        for _ in range(26):
            x += rng.integers(-1, 2)
            y += rng.integers(-1, 2)
            if 24 <= x < 104 and 0 <= y < 128:
                px[int(x), int(y)] = (220, 230, 240, 255)
    os.makedirs(ROOT, exist_ok=True)
    base.save(os.path.join(ROOT, 'icon.png'))


if __name__ == '__main__':
    ectoplasm()
    holy_spark()
    demon_smoke()
    wisp()
    salt_sparkle()
    blood_drip()
    handprint()
    cold_breath()
    salt_line()
    blood_stains()
    ritual_candle()
    icon()
    print('fx textures written')
