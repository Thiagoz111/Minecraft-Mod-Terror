"""DEAD LINE item icons (32x32)."""
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..'))
from workdir import WORK  # noqa: E402
import math
import numpy as np
from PIL import Image
from px import Sprite, glow, hexc, shade, lerp, Material
from mats import *

S = 32
OUT = WORK


def with_glow(img, color, radius=1.6, strength=0.5):
    out = glow(img, color, radius=radius, strength=strength)
    out.alpha_composite(img)
    return out


# ----------------------------------------------------------------------------
def crucifix():
    s = Sprite(S, seed=3)
    ring = s.mask_ellipse(16, 12, 7.4, 7.4) & ~s.mask_ellipse(16, 12, 5.4, 5.4)
    s._apply(ring, GOLD, dome=True)
    s.rect(14, 1, 17, 30, SILVER, bevel=2)
    s.rect(5, 10, 26, 13, SILVER, bevel=2)
    for cx, cy in ((16, 2.6), (5.6, 11.9), (26.4, 11.9)):
        s.ellipse(cx, cy, 2.7, 2.7, SILVER)
    s.ellipse(16, 29.2, 3.0, 2.5, SILVER)
    s.ellipse(16, 12, 3.1, 3.1, GOLD, outline=False)
    s.ellipse(16, 12, 2.0, 2.0, BLUE_GEM, outline=False)
    img = s.render()
    px = img.load()
    px[15, 11] = (240, 250, 255, 255)
    # engraved filigree on the long beam
    for y in (17, 20, 23, 26):
        px[15, y] = (86, 93, 115, 255); px[16, y + 1] = (86, 93, 115, 255)
    for x in (9, 22):
        px[x, 11] = (86, 93, 115, 255); px[x + 1, 12] = (86, 93, 115, 255)
    for (x, y) in ((15, 1), (4, 10), (25, 10), (15, 28)):
        px[x, y] = (255, 255, 255, 255)
    return with_glow(img, (255, 236, 160), radius=1.3, strength=0.35)


def holy_water():
    s = Sprite(S, seed=5)
    body = s.mask_ellipse(16, 21, 9.5, 9)
    neck = s.mask_rect(13, 6, 18, 13)
    s._apply(body | neck, GLASS, dome=True)
    water = s.mask_ellipse(16, 21.5, 8.2, 7.6) & (s._grid()[1] > 15.2)
    s._apply(water, HOLYWATER, dome=True, outline=False)
    s.rect(12, 5, 19, 6, GLASS, bevel=0.8)
    s.rect(13, 1, 18, 4, CORK, bevel=1, noise=0.06)
    s.rect(15, 17, 16, 25, SILVER, bevel=0.6, outline=False)
    s.rect(13, 19, 18, 20, SILVER, bevel=0.6, outline=False)
    img = s.render()
    px = img.load()
    for p in ((10, 17), (9, 18), (9, 19), (9, 20), (10, 15), (14, 8), (14, 9), (14, 10)):
        px[p] = (235, 250, 255, 230)
    for p in ((20, 24), (21, 21), (19, 27), (12, 26), (22, 19)):
        px[p] = (200, 245, 255, 255)
    for x in range(12, 20):
        px[x, 13] = (139, 104, 60, 255) if x % 2 else (104, 74, 40, 255)
    for p, c in (((20, 14), (139, 104, 60)), ((21, 15), (104, 74, 40)), ((21, 16), (139, 104, 60)), ((22, 17), (230, 200, 120)), ((22, 18), (180, 140, 70))):
        px[p] = c + (255,)
    return with_glow(img, (90, 190, 255), radius=1.6, strength=0.5)


SKULL = ['.#####.', '#######', '#..#..#', '###.###', '.#####.', '.#.#.#.']


def phone(ringing=False):
    s = Sprite(S, seed=7)
    s.poly([(9, 2), (23, 2), (25, 4), (25, 29), (23, 31), (9, 31), (7, 29), (7, 4)], PLASTIC, bevel=1.8)
    img = s.render()
    px = img.load()
    # screen with radial red glow
    cx, cy = 16, 12
    for y in range(5, 28):
        for x in range(9, 23):
            d = math.hypot(x + 0.5 - cx, (y + 0.5 - cy) * 0.9)
            t = max(0, 1 - d / (11 if ringing else 9))
            base = (14, 3, 7)
            top = (120, 10, 22) if ringing else (70, 6, 14)
            c = tuple(int(base[i] + (top[i] - base[i]) * t ** 1.6) for i in range(3))
            # scanlines
            if y % 2 == 0:
                c = tuple(int(v * 0.86) for v in c)
            px[x, y] = c + (255,)
    # bezel notch + status bar
    px[15, 5] = px[16, 5] = (6, 6, 8, 255)
    px[10, 6] = px[11, 6] = (160, 150, 160, 255)
    px[20, 6] = (90, 220, 120, 255); px[21, 6] = (90, 220, 120, 255)
    # pulse rings
    rings = (3.6, 5.6, 7.6) if ringing else (4.4,)
    for r in rings:
        for a in range(0, 360, 6):
            x = round(cx - 0.5 + math.cos(math.radians(a)) * r)
            y = round(cy - 0.5 + math.sin(math.radians(a)) * r)
            if 9 <= x <= 22 and 5 <= y <= 19:
                k = 1 - (r - 3.6) / 6
                px[x, y] = (int(200 * k + 60), int(20 * k + 8), int(36 * k + 10), 255)
    # skull glyph
    for j, row in enumerate(SKULL):
        for i, ch in enumerate(row):
            if ch == '#':
                px[13 + i, 9 + j] = (255, 236, 236, 255) if j < 2 else (236, 210, 214, 255)
            elif ch == '.' and j in (2, 3) and 0 < i < 6:
                px[13 + i, 9 + j] = (255, 40, 50, 255) if ringing else (150, 10, 20, 255)
    # caller name + subtitle
    for x in range(11, 21):
        px[x, 18] = (240, 232, 236, 255) if x not in (14, 18) else (120, 40, 50, 255)
    for x in range(12, 20):
        px[x, 20] = (150, 120, 128, 255) if x % 2 == 0 else (110, 80, 90, 255)
    # answer / decline buttons
    for (bx, col) in ((12, (46, 204, 96)), (19, (232, 46, 58))):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if abs(dx) + abs(dy) < 2:
                    px[bx + dx, 24 + dy] = col + (255,)
        px[bx - 1, 23] = shade(col + (255,), 1.45)
        px[bx, 24] = (255, 255, 255, 255)
    # spiderweb crack (top-right)
    crack = [(21, 5), (20, 6), (20, 7), (19, 8), (19, 9), (20, 10), (21, 11), (21, 12), (22, 13)]
    crack += [(19, 8), (18, 7), (17, 7)] + [(20, 6), (21, 7), (22, 7)] + [(19, 9), (18, 10), (17, 11)]
    for p in crack:
        px[p] = (205, 210, 225, 255)
    for p in ((22, 6), (18, 9), (20, 11), (16, 11), (18, 6)):
        px[p] = (40, 30, 40, 255)
    # camera + side buttons + chin
    px[18, 3] = (60, 80, 140, 255)
    px[7, 9] = px[7, 10] = px[7, 13] = (80, 84, 100, 255)
    px[25, 11] = px[25, 12] = (80, 84, 100, 255)
    for x in (14, 15, 16, 17):
        px[x, 29] = (36, 38, 48, 255)
    if ringing:
        for p in ((4, 8), (3, 9), (3, 10), (4, 11), (28, 8), (29, 9), (29, 10), (28, 11)):
            px[p] = (255, 60, 70, 255)
        for p in ((2, 6), (1, 8), (1, 9), (1, 10), (1, 11), (2, 13), (30, 6), (31, 8), (31, 9), (31, 10), (31, 11), (30, 13)):
            px[p] = (150, 20, 30, 220)
        return with_glow(img, (255, 40, 60), radius=1.5, strength=0.45)
    return img


LED_COLORS = [(40, 230, 70), (150, 240, 40), (250, 220, 30), (255, 140, 20), (255, 30, 30)]


def emf(level=0):
    s = Sprite(S, seed=11)
    s.poly([(10, 4), (21, 4), (23, 6), (23, 22), (21, 30), (11, 30), (9, 22), (9, 6)], PLASTIC, bevel=1.8)
    s.rect(9, 5, 23, 7, YELLOW_PLASTIC, bevel=1)          # yellow top band
    s.rect(11, 9, 21, 13, SCREEN, bevel=0.2, outline=False)  # LED window
    s.poly([(11, 20), (21, 20), (20, 29), (12, 29)], RUBBER, bevel=1.2, noise=0.05, outline=False)  # grip
    img = s.render()
    px = img.load()
    # LEDs
    for i in range(5):
        x = 12 + i * 2
        on = i < level
        c = LED_COLORS[i]
        if on:
            px[x, 10] = shade(c + (255,), 1.5); px[x, 11] = c + (255,); px[x, 12] = shade(c + (255,), 0.7)
        else:
            px[x, 10] = (40, 40, 46, 255); px[x, 11] = shade(c + (255,), 0.28); px[x, 12] = (22, 22, 28, 255)
    # label "EMF" pixel text
    pal = {'#': (230, 200, 60, 255)}
    s2 = ['###.#...#.###', '#...##.##.#..', '##..#.#.#.##.', '#...#...#.#..', '###.#...#.#..']
    for j, row in enumerate(s2):
        for i, ch in enumerate(row):
            if ch == '#' and 10 + i <= 22:
                px[10 + i, 14 + j] = (220, 190, 60, 255) if j else (250, 225, 100, 255)
    # grip ridges
    for y in range(21, 29, 2):
        for x in range(13, 20):
            px[x, y] = (12, 12, 12, 255)
    # power button
    px[20, 15] = (200, 30, 30, 255); px[20, 16] = (120, 10, 10, 255)
    # yellow band highlight
    for x in range(11, 21):
        px[x, 5] = (255, 238, 140, 255)
    if level >= 1:
        leds = Image.new('RGBA', (S, S))
        for i in range(level):
            for y in (10, 11, 12):
                leds.putpixel((12 + i * 2, y), px[12 + i * 2, y])
        g = glow(leds, LED_COLORS[level - 1], radius=1.2, strength=0.5 + level * 0.06)
        g.alpha_composite(img)
        return g
    return img


def flashlight(on=False):
    s = Sprite(S, seed=13)
    # diagonal body: handle bottom-left -> head top-right
    BLACKMETAL = Material(['#050508', '#0b0c11', '#14161e', '#1f222d', '#2d3140', '#424759', '#5d6377'], spec=0.5, shininess=12)
    s.cylinder(6, 26, 17, 15, 3.2, BLACKMETAL)
    s.cylinder(16, 16, 22, 10, 4.6, STEEL)
    s.cylinder(21, 11, 23, 9, 5.2, STEEL)
    s.cylinder(4.5, 27.5, 6.5, 25.5, 3.0, STEEL)
    img = s.render()
    px = img.load()
    # knurled grip (diagonal hatch)
    for i in range(7, 16):
        for k in (-2, 0, 2):
            x, y = i + k // 2, 26 - (i - 6) + k // 2 + 1
            if 0 <= x < 32 and 0 <= y < 32 and px[x, y][3] and (i + k) % 2 == 0:
                px[x, y] = shade(px[x, y], 0.55)
    # switch
    px[12, 19] = (200, 40, 40, 255); px[13, 19] = (140, 20, 20, 255)
    # lens (face of the head)
    lens = [(24, 5), (25, 6), (26, 7), (26, 8), (27, 9), (26, 10), (25, 11), (24, 12), (23, 8), (24, 8), (25, 8), (24, 9), (25, 9), (24, 10), (25, 10), (24, 7), (25, 7), (23, 9), (23, 10), (24, 11)]
    for p in lens:
        px[p] = (255, 250, 220, 255) if on else (120, 140, 160, 255)
    if not on:
        px[24, 7] = px[25, 8] = (210, 225, 240, 255)
    if on:
        out = Image.new('RGBA', (S, S))
        o = out.load()
        for r in range(1, 8):
            for a in range(-35, 36, 5):
                ang = math.radians(-45 + a)
                x = round(25 + math.cos(ang) * (2 + r))
                y = round(9 + math.sin(ang) * (2 + r))
                if 0 <= x < 32 and 0 <= y < 32:
                    al = int(200 * (1 - r / 8))
                    o[x, y] = (255, 246, 200, al)
        out.alpha_composite(img)
        return with_glow(out, (255, 240, 180), radius=1.2, strength=0.3)
    return img


def salt():
    s = Sprite(S, seed=17)
    s.poly([(7, 13), (10, 9), (22, 9), (25, 13), (27, 24), (24, 30), (8, 30), (5, 24)], BURLAP, dome=True, noise=0.07)
    s.ellipse(16, 10, 6.8, 2.6, SALT, dome=True, noise=0.06)
    s.ellipse(16, 8.4, 4.6, 2.6, SALT, dome=True, noise=0.08, outline=False)
    img = s.render()
    px = img.load()
    # burlap weave
    for y in range(13, 30):
        for x in range(6, 27):
            if px[x, y][3] and (x + y) % 3 == 0 and px[x, y][0] > 60:
                px[x, y] = shade(px[x, y], 0.82)
    # twine tie
    for x in range(9, 24):
        px[x, 13] = (186, 150, 96, 255) if x % 2 else (128, 96, 56, 255)
    px[22, 14] = (186, 150, 96, 255); px[23, 15] = (128, 96, 56, 255); px[23, 16] = (186, 150, 96, 255); px[22, 17] = (128, 96, 56, 255)
    # stamped cross (dark red ink, slightly worn)
    ink = (96, 20, 24, 255)
    for y in range(17, 27):
        if y != 22: px[15, y] = ink
        px[16, y] = ink
    for x in range(12, 20):
        px[x, 20] = ink
        if x not in (13, 18): px[x, 21] = ink
    # salt sparkles & spilled grains
    for p in ((14, 7), (18, 8), (12, 9), (20, 10)):
        px[p] = (255, 255, 255, 255)
    for p in ((4, 30), (6, 31), (27, 30), (28, 31), (2, 31), (30, 29)):
        px[p] = (236, 242, 248, 255)
    return img


def spirit_box():
    s = Sprite(S, seed=19)
    s.capsule(8, 13, 2.5, 3.5, 1.0, STEEL, dome=False)  # antenna
    s.rect(4, 12, 28, 27, Material(['#1a0a0a', '#2e1212', '#481c1a', '#652a24', '#833a2e', '#a24d3a'], spec=0.3, shininess=14), bevel=1.8)
    s.rect(17, 15, 26, 20, Material(['#2a1404', '#4a2408', '#d06a12', '#ff9a2a', '#ffc76a'], emissive=True), bevel=0.4, outline=False)
    s.ellipse(2.5, 3.5, 1.6, 1.6, STEEL)
    s.ellipse(22, 24, 2.1, 2.1, STEEL)
    img = s.render()
    px = img.load()
    # speaker grille dot matrix
    for y in range(15, 26, 2):
        for x in range(6, 15, 2):
            px[x, y] = (18, 6, 6, 255)
            px[x + 1, y] = (120, 60, 50, 255) if y < 17 else px[x + 1, y]
    # LCD digits "66.6" (pixel font 3x4)
    D = {'6': ['###', '#..', '###', '#.#', '###'], '.': ['.', '.', '.', '.', '#']}
    xx = 19
    for ch in '66':
        g = D[ch]
        for j, row in enumerate(g):
            for i, c in enumerate(row):
                if c == '#':
                    px[xx + i, 15 + j] = (60, 20, 4, 255)
        xx += len(g[0]) + 1 if ch != '.' else 2
    # static waveform under display
    for x in range(17, 27):
        px[x, 21] = (255, 190, 90, 255) if x % 3 == 0 else (120, 60, 30, 255)
    # knob notch
    px[22, 23] = (250, 250, 255, 255)
    # antenna segments
    for p in ((6, 11), (4, 8)):
        px[p] = (210, 215, 225, 255)
    return img


def camera():
    s = Sprite(S, seed=23)
    BODY = Material(['#2a2620', '#4a443a', '#6e6656', '#958b77', '#bcb39c', '#ded6bf'], ambient=0.4, spec=0.2)
    s.rect(3, 11, 28, 27, BODY, bevel=1.8)
    s.rect(3, 23, 28, 27, PLASTIC, bevel=1)
    s.rect(5, 7, 12, 11, WHITE_PLASTIC, bevel=1)    # flash
    s.rect(21, 8, 26, 11, PLASTIC, bevel=0.8)       # viewfinder
    s.ellipse(16, 18, 6.8, 6.8, PLASTIC)
    s.ellipse(16, 18, 4.6, 4.6, STEEL, outline=False)
    s.ellipse(16, 18, 3.0, 3.0, GLASS, outline=False, dome=True)
    img = s.render()
    px = img.load()
    px[14, 16] = (240, 250, 255, 255); px[15, 16] = (200, 220, 240, 255); px[14, 17] = (200, 220, 240, 255)
    px[17, 20] = (80, 110, 150, 255)
    # red stripe + shutter button
    for y in range(12, 23):
        px[26, y] = (170, 30, 30, 255)
    px[25, 6] = px[26, 6] = (200, 30, 30, 255); px[25, 7] = px[26, 7] = (140, 20, 20, 255)
    # flash lens texture
    for x in range(6, 12):
        px[x, 9] = (250, 250, 230, 255) if x % 2 else (210, 210, 200, 255)
    # photo sliding out of the bottom
    for x in range(8, 24):
        for y in (28, 29, 30):
            px[x, y] = (236, 232, 222, 255)
    for x in range(10, 22):
        px[x, 28] = (40, 30, 40, 255)
        px[x, 29] = (60, 40, 50, 255)
    px[15, 29] = (200, 40, 40, 255)  # a red dot on the photo... eyes?
    px[17, 29] = (200, 40, 40, 255)
    for x in range(8, 24):
        px[x, 31] = (80, 78, 72, 255)
    px[7, 28] = px[7, 29] = px[7, 30] = px[24, 28] = px[24, 29] = px[24, 30] = (80, 78, 72, 255)
    return img


def ritual_book():
    s = Sprite(S, seed=29)
    s.rect(7, 4, 25, 29, PAPER, bevel=1)           # page block
    s.poly([(5, 3), (23, 3), (24, 4), (24, 28), (23, 29), (5, 29), (4, 28), (4, 4)], LEATHER, bevel=1.6, noise=0.05)
    s.rect(4, 3, 7, 29, Material(['#120404', '#240808', '#3a0e0c', '#521612', '#6a2018']), bevel=1.2)  # spine
    s.rect(12, 8, 15, 23, SILVER, bevel=1.2, outline=False)
    s.rect(9, 12, 18, 14, SILVER, bevel=1.2, outline=False)
    s.ellipse(13.5, 13, 1.6, 1.6, RED_GEM, outline=False)
    for (x, y) in ((20, 4), (20, 25)):
        s.rect(x, y, x + 3, y + 3, SILVER, bevel=1, outline=False)
    s.rect(23, 14, 27, 18, GOLD, bevel=1)          # clasp
    img = s.render()
    px = img.load()
    for y in range(5, 29):
        if y % 2:
            px[25, y] = (190, 176, 150, 255)
    # ribbons
    for y in range(29, 32):
        px[10, y] = (170, 20, 30, 255); px[12, y] = (30, 30, 40, 255)
    px[10, 31] = (110, 10, 20, 255)
    # embossed border lines
    for y in range(6, 27):
        px[9, y] = shade(px[9, y], 0.7) if px[9, y][3] else px[9, y]
    px[13, 12] = (255, 200, 200, 255)
    return img


def spirit_jar(frame=None):
    s = Sprite(S, seed=31)
    s.rect(8, 9, 23, 29, GLASS, bevel=2.5)
    s.rect(10, 6, 21, 9, GLASS, bevel=1)
    s.rect(9, 2, 22, 6, GOLD, bevel=1.4)
    if frame is not None:
        mask = s.mask_rect(9, 10, 22, 28)
        s._apply(mask, SPIRIT, dome=True, outline=False)
    img = s.render()
    px = img.load()
    if frame is not None:
        # swirling wisps: rotating spiral pattern
        t = frame / 8 * math.tau
        for y in range(10, 29):
            for x in range(9, 23):
                dx, dy = x + 0.5 - 16, (y + 0.5 - 19.5) * 0.75
                r = math.hypot(dx, dy)
                a = math.atan2(dy, dx)
                v = math.sin(a * 2 + r * 0.9 - t * 1.0) * 0.5 + 0.5
                v *= max(0, 1 - r / 9)
                if v > 0.62:
                    px[x, y] = (230, 255, 248, 255)
                elif v > 0.45:
                    px[x, y] = (120, 255, 220, 255)
                elif v < 0.12 and r < 7:
                    px[x, y] = (10, 90, 90, 255)
        # ghost face in the swirl
        fy = 17 + (1 if frame % 4 < 2 else 0)
        for p in ((14, fy), (17, fy)):
            px[p] = (6, 30, 40, 255)
        px[15, fy + 2] = px[16, fy + 2] = (6, 30, 40, 255)
        px[15, fy + 3] = px[16, fy + 3] = (6, 30, 40, 255)
    else:
        for y in range(11, 28):
            for x in range(10, 22):
                if px[x, y][3]:
                    c = px[x, y]
                    px[x, y] = (c[0], c[1], c[2], 110)
        for p in ((20, 12), (20, 13), (21, 14), (12, 26), (13, 27)):
            px[p] = (220, 240, 255, 200)
    # lid engraving: runes
    for x in range(10, 22, 2):
        px[x, 4] = (110, 60, 16, 255)
    # glass highlights
    for y in range(11, 26):
        px[10, y] = (235, 248, 255, 230)
    px[11, 11] = px[11, 12] = (235, 248, 255, 200)
    # paper seal with cross
    for y in range(20, 26):
        for x in range(17, 22):
            px[x, y] = (220, 205, 170, 255) if (x + y) % 5 else (196, 180, 146, 255)
    for y in range(21, 25):
        px[19, y] = (140, 20, 20, 255)
    px[18, 22] = px[20, 22] = (140, 20, 20, 255)
    if frame is not None:
        return with_glow(img, (80, 255, 210), radius=1.8, strength=0.55)
    return img


def pills():
    s = Sprite(S, seed=37)
    ORANGE_GLASS = Material([(80, 30, 4, 230), (150, 60, 8, 220), (210, 104, 16, 210), (244, 150, 40, 210), (255, 206, 120, 230)], spec=0.8, shininess=14)
    s.rect(9, 10, 22, 29, ORANGE_GLASS, bevel=2.4)
    s.rect(8, 4, 23, 9, WHITE_PLASTIC, bevel=1.5)
    s.rect(9, 15, 22, 24, PAPER, bevel=0.5, outline=False)
    s.capsule(24, 28, 28, 25, 1.6, WHITE_PLASTIC)
    img = s.render()
    px = img.load()
    for x in range(9, 23, 2):
        px[x, 5] = (150, 154, 164, 255); px[x, 7] = (150, 154, 164, 255)
    for y in range(17, 23):
        px[12, y] = (200, 30, 40, 255)
    for x in range(10, 15):
        px[x, 19] = (200, 30, 40, 255)
    for x in range(15, 21):
        px[x, 17] = (60, 60, 70, 255)
        if x < 20: px[x, 19] = (110, 110, 120, 255)
        if x < 19: px[x, 21] = (110, 110, 120, 255)
    for y in range(11, 28):
        px[10, y] = (255, 230, 180, 220)
    px[26, 27] = (230, 70, 60, 255); px[27, 26] = (230, 70, 60, 255)
    return img


def silver_dagger():
    s = Sprite(S, seed=41)
    s.poly([(13, 17), (27, 3), (29, 2), (28, 5), (15, 19)], SILVER, bevel=1.5)    # blade
    s.capsule(9, 15, 16, 22, 1.7, GOLD)                                                 # crossguard
    s.cylinder(5, 25, 11, 19, 2.0, LEATHER, noise=0.05)                                  # grip
    s.ellipse(4, 26.5, 2.6, 2.6, GOLD)                                                   # pommel
    s.ellipse(4, 26.5, 1.4, 1.4, RED_GEM, outline=False)
    s.ellipse(12.5, 18.5, 1.5, 1.5, RED_GEM, outline=False)
    img = s.render()
    px = img.load()
    # fuller (central groove) + runes
    for i in range(0, 10):
        x, y = 16 + i, 16 - i
        px[x, y] = (230, 236, 246, 255)
        if i % 3 == 1:
            px[x - 1, y] = (90, 100, 130, 255)
    # grip wrap
    for i in range(6, 11):
        x, y = i, 25 - (i - 5)
        px[x, y] = (40, 10, 10, 255)
    px[3, 25] = (255, 200, 200, 255)
    px[28, 3] = (255, 255, 255, 255)
    return with_glow(img, (200, 220, 255), radius=1.0, strength=0.25)


def rosary(inverted=False):
    s = Sprite(S, seed=43)
    BEAD = RED_GEM if inverted else Material(['#1a0e08', '#33200f', '#523519', '#734c26', '#946537', '#b5824c'], spec=0.5, shininess=8)
    pts = []
    for i in range(22):
        a = math.radians(-90 + i * 360 / 22)
        x, y = 16 + math.cos(a) * 10, 11 + math.sin(a) * 8
        if abs(x - 16) < 2 and y > 16:
            continue
        pts.append((x, y))
    for (x, y) in pts:
        s.ellipse(x, y, 1.3, 1.3, BEAD)
    # dangling strand
    for y in (21, 23.5):
        s.ellipse(16, y, 1.3, 1.3, BEAD)
    METAL = BLACK_WAX if inverted else SILVER
    if inverted:
        s.rect(15, 25, 16, 31, STEEL, bevel=1)
        s.rect(13, 28, 18, 29, STEEL, bevel=1)
    else:
        s.rect(15, 25, 16, 31, METAL, bevel=1)
        s.rect(13, 27, 18, 28, METAL, bevel=1)
    s.ellipse(16, 19.5, 1.6, 1.2, GOLD if not inverted else STEEL)
    img = s.render()
    px = img.load()
    for (x, y) in pts:
        px[int(x) - 1 + 0, int(y) - 1 + 0] = (255, 220, 200, 255) if inverted else (220, 170, 120, 255)
    if inverted:
        return with_glow(img, (200, 20, 30), radius=1.4, strength=0.4)
    return img


def flare(lit=False):
    s = Sprite(S, seed=47)
    RED = Material(['#2a0306', '#5a0a10', '#931520', '#c92a2e', '#ee5a4a', '#ff9a80'], spec=0.4, shininess=12)
    s.cylinder(7, 25, 20, 12, 2.6, RED)
    s.cylinder(5, 27, 8, 24, 2.7, PLASTIC)
    s.cylinder(20, 12, 22, 10, 2.2, Material(['#3a3020', '#5e5034', '#8a7a52', '#b0a070']))
    img = s.render()
    px = img.load()
    # label band
    for i in range(10, 15):
        x, y = i, 25 - (i - 7)
        for k in (-1, 0, 1):
            if px[x + k, y + k][3]:
                px[x + k, y + k] = (236, 226, 200, 255) if i % 2 else (210, 196, 160, 255)
    if lit:
        out = Image.new('RGBA', (S, S))
        o = out.load()
        rng = np.random.default_rng(4)
        for k in range(46):
            r = rng.uniform(0, 8)
            a = rng.uniform(-1.6, 0.2)
            x = int(23 + math.cos(a) * r)
            y = int(9 + math.sin(a) * r)
            if 0 <= x < 32 and 0 <= y < 32:
                o[x, y] = (255, int(200 - r * 20), int(160 - r * 18), int(255 - r * 22))
        for p in ((23, 8), (24, 8), (23, 9), (24, 7), (22, 8)):
            o[p] = (255, 255, 240, 255)
        img.alpha_composite(out)
        return with_glow(img, (255, 60, 50), radius=2.0, strength=0.6)
    return img


def baby_shoe():
    s = Sprite(S, seed=53)
    LEATHER_W = Material(['#3a3436', '#5e5658', '#857c7c', '#aca2a0', '#cdc4bf', '#e9e2db'], ambient=0.4, spec=0.25)
    SOLE = Material(['#22160e', '#36241a', '#4e3626', '#684a34', '#7e5c42'])
    s.poly([(4, 22), (6, 16), (11, 14), (13, 18), (19, 18), (23, 15), (27, 17), (29, 21), (29, 24), (4, 25)], LEATHER_W, dome=True, noise=0.05)
    s.rect(3, 24, 29, 26, SOLE, bevel=0.8)
    s.poly([(7, 16), (11, 14), (13, 18), (8, 19)], Material(['#0c0909', '#171212', '#231b1b']), bevel=0.5, outline=False)  # opening
    img = s.render()
    px = img.load()
    # strap with buckle
    for i, x in enumerate(range(11, 19)):
        y = 15 + (1 if 12 < x < 17 else 0)
        px[x, y - 1] = (70, 62, 66, 255); px[x, y] = (110, 100, 104, 255)
    px[18, 15] = (210, 190, 120, 255); px[18, 14] = (160, 140, 80, 255)
    # stitching along the toe
    for x in range(19, 28, 2):
        px[x, 21] = (150, 140, 136, 255)
    # grime / algae / mud
    rng = np.random.default_rng(9)
    for k in range(55):
        x, y = int(rng.integers(5, 29)), int(rng.integers(18, 25))
        if px[x, y][3] and px[x, y][0] > 80:
            px[x, y] = [(84, 96, 52, 255), (64, 52, 36, 255), (104, 112, 70, 255)][k % 3]
    for y in range(19, 25):
        px[5, y] = (60, 74, 40, 255)
    # dripping water
    for p in ((9, 27), (9, 28), (16, 27), (24, 27), (24, 28), (24, 29), (12, 30)):
        px[p] = (110, 165, 210, 210)
    # untied lace
    for p in ((14, 12), (13, 11), (12, 11), (11, 10), (19, 12), (20, 11), (21, 11)):
        px[p] = (200, 190, 180, 255)
    return img


def bone_totem():
    s = Sprite(S, seed=59)
    s.cylinder(16, 31, 16, 17, 1.5, DARKWOOD)
    # antlers
    for (pts) in ([(12, 10), (8, 6), (6, 2)], [(20, 10), (24, 6), (26, 2)], [(8, 6), (4, 6)], [(24, 6), (28, 6)], [(10, 8), (9, 3)], [(22, 8), (23, 3)]):
        for a, b in zip(pts, pts[1:]):
            s.capsule(a[0], a[1], b[0], b[1], 1.0, BONE)
    # deer skull
    s.poly([(11, 9), (21, 9), (22, 13), (19, 21), (17, 25), (15, 25), (13, 21), (10, 13)], BONE, dome=True, noise=0.04)
    img = s.render()
    px = img.load()
    # eye sockets + nasal
    for p in ((13, 13), (14, 13), (13, 14), (14, 14), (18, 13), (19, 13), (18, 14), (19, 14), (15, 19), (17, 19), (16, 20)):
        px[p] = (20, 10, 10, 255)
    px[13, 13] = (200, 20, 20, 255); px[19, 13] = (200, 20, 20, 255)  # red ember eyes
    # cracks
    for p in ((16, 10), (16, 11), (17, 12), (12, 17)):
        px[p] = (110, 96, 72, 255)
    # twine + feathers
    for y in (26, 27):
        for x in (14, 15, 16, 17, 18):
            px[x, y] = (150, 120, 70, 255) if (x + y) % 2 else (100, 74, 40, 255)
    for i, c in enumerate([(30, 30, 30), (60, 60, 60), (30, 30, 30), (90, 20, 20)]):
        px[19 + i // 2, 28 + i] = c + (255,)
        px[12 - i // 2, 28 + i] = c + (255,)
    # blood smear
    for p in ((16, 15), (16, 16), (15, 17)):
        px[p] = (120, 16, 20, 255)
    return with_glow(img, (180, 20, 20), radius=1.0, strength=0.2)


def music_box(frame=0):
    s = Sprite(S, seed=61)
    s.poly([(4, 18), (27, 18), (28, 29), (3, 29)], DARKWOOD, bevel=1.5, noise=0.05)
    s.poly([(4, 18), (27, 18), (25, 7), (6, 7)], WOOD, bevel=1.2, noise=0.05)     # open lid (inside)
    s.rect(6, 9, 25, 16, Material(['#3a0810', '#5c0f1a', '#801a26', '#a02a34', '#c04048']), bevel=0.6, outline=False)  # velvet mirror area
    s.rect(4, 22, 27, 23, GOLD, bevel=0.6, outline=False)
    s.cylinder(28, 24, 31, 24, 1.0, GOLD)   # crank
    img = s.render()
    px = img.load()
    # mirror in lid
    for y in range(10, 15):
        for x in range(9, 15):
            px[x, y] = (150, 170, 190, 255) if (x - y) % 4 else (210, 225, 240, 255)
    # tiny ballerina (rotates by frame)
    bx = 18 + (frame % 2)
    for p in ((bx, 12), (bx, 13), (bx, 14), (bx, 15)):
        px[p] = (240, 230, 225, 255)
    px[bx, 11] = (250, 220, 210, 255)
    px[bx - 1, 14] = px[bx + 1, 14] = (255, 180, 200, 255)
    px[bx - 2, 14] = (255, 150, 180, 255) if frame % 2 else (0, 0, 0, 0)
    px[bx + 1, 12] = (240, 230, 225, 255) if frame % 2 else px[bx + 1, 12]
    # front ornaments + keyhole
    for x in (8, 23):
        px[x, 26] = (230, 190, 80, 255)
    px[15, 26] = px[16, 26] = (20, 12, 8, 255); px[15, 27] = (20, 12, 8, 255)
    # notes floating
    for (x, y) in ((24, 2), (27, 4)):
        px[x, y] = (230, 200, 230, 255); px[x + 1, y] = (230, 200, 230, 255); px[x + 1, y - 1] = (230, 200, 230, 255)
        px[x, y + 1] = (200, 160, 200, 255)
    return img


def cursed_doll():
    s = Sprite(S, seed=67)
    DRESS = Material(['#1a0a14', '#2e1224', '#4a1c38', '#66284c', '#823660', '#a04c78'], ambient=0.38)
    HAIR = Material(['#120a06', '#24140c', '#3a2214', '#52321e', '#6a4428'], ambient=0.35)
    s.poly([(10, 17), (22, 17), (27, 31), (5, 31)], DRESS, dome=True, noise=0.04)
    s.capsule(9, 18, 6, 25, 1.3, PORCELAIN)
    s.capsule(23, 18, 26, 25, 1.3, PORCELAIN)
    s.ellipse(16, 10, 7.5, 7.8, HAIR, dome=True, noise=0.05)
    s.ellipse(16, 11, 5.6, 6.0, PORCELAIN, outline=False)
    s.rect(9, 3, 23, 6, HAIR, bevel=1, outline=False)
    img = s.render()
    px = img.load()
    # black hollow eyes with pin pupils
    for (x, y) in ((13, 10), (14, 10), (13, 11), (14, 11), (18, 10), (19, 10), (18, 11), (19, 11)):
        px[x, y] = (10, 6, 10, 255)
    px[14, 10] = (255, 255, 255, 255); px[18, 10] = (255, 255, 255, 255)
    # tear of blood
    px[13, 12] = (150, 10, 16, 255); px[13, 13] = (120, 8, 12, 255); px[13, 14] = (90, 6, 10, 255)
    # rosy cheeks + stitched smile
    px[12, 13] = (230, 150, 150, 255); px[20, 13] = (230, 150, 150, 255)
    for x in range(14, 19):
        px[x, 14] = (80, 20, 30, 255)
    px[14, 13] = (80, 20, 30, 255); px[18, 13] = (80, 20, 30, 255)
    # crack across face
    for p in ((17, 6), (17, 7), (16, 8), (17, 9), (16, 12), (15, 13)):
        px[p] = (60, 50, 60, 255)
    # lace collar
    for x in range(11, 22):
        px[x, 17] = (230, 225, 230, 255) if x % 2 else (190, 185, 195, 255)
    # bow
    px[9, 5] = px[10, 4] = px[10, 6] = (170, 20, 40, 255); px[11, 5] = (120, 10, 30, 255)
    return img


ALL = {
    'phone': phone, 'phone_ringing': lambda: phone(True), 'crucifix': crucifix, 'holy_water': holy_water,
    'salt': salt, **{f'emf_{i}': (lambda i=i: emf(i)) for i in range(6)}, 'flashlight': flashlight,
    'flashlight_on': lambda: flashlight(True), 'spirit_box': spirit_box, 'camera': camera,
    'ritual_book': ritual_book, 'spirit_jar': spirit_jar, 'spirit_jar_full': lambda: spirit_jar(0), 'pills': pills,
    'silver_dagger': silver_dagger, 'rosary': rosary, 'inverted_rosary': lambda: rosary(True), 'flare': flare,
    'flare_lit': lambda: flare(True), 'baby_shoe': baby_shoe, 'bone_totem': bone_totem, 'music_box': music_box,
    'cursed_doll': cursed_doll,
}

if __name__ == '__main__':
    from px import sheet
    names = list(ALL)
    imgs = [ALL[n]() for n in names]
    sheet(imgs, k=8, cols=7, labels=names).save(OUT + '/items2.png')


# ---------------------------------------------------------------- extra variants
def flashlight_uv():
    img = flashlight(True)
    px = img.load()
    for y in range(32):
        for x in range(32):
            r, g, b, a = px[x, y]
            if a and r > 200 and g > 200 and b > 120:  # beam + lens -> ultraviolet
                px[x, y] = (min(255, int(r * 0.75)), int(g * 0.35), 255, a)
            elif a and r > 180 and g > 170 and b < 200 and (x + y) > 28:
                px[x, y] = (190, 90, 255, a)
    return img


EGG_COLORS = {
    'llorona': ('#d8dbe0', '#11131a'), 'wendigo': ('#4e4037', '#d9cfb4'), 'poseida': ('#c2b7ae', '#5e090e'),
    'payaso': ('#7d4c75', '#c42730'), 'monja': ('#181a24', '#f6d24a'), 'sombra': ('#0c0c12', '#b0141c'),
    'muneca': ('#f2ece8', '#66284c'), 'anima': ('#3fbcb0', '#e8fff8'),
}


def spawn_egg(key):
    base, spot = EGG_COLORS[key]
    s = Sprite(S, seed=hash(key) % 1000)
    m = Material(base) if False else None
    from px import ramp
    egg = Material(ramp(base, 7, spread=0.5), spec=0.35, shininess=10)
    s.ellipse(16, 17.5, 9.2, 12.5, egg)
    img = s.render()
    px = img.load()
    rng = np.random.default_rng(abs(hash(key)) % 2**31)
    sc = hexc(spot)
    for k in range(9):
        cx, cy = rng.integers(10, 23), rng.integers(9, 27)
        rad = rng.integers(1, 3)
        for y in range(cy - rad, cy + rad + 1):
            for x in range(cx - rad, cx + rad + 1):
                if (x - cx) ** 2 + (y - cy) ** 2 <= rad * rad + 0.5 and px[x, y][3] and px[x, y] != (0, 0, 0, 0):
                    c = px[x, y]
                    lum = (c[0] + c[1] + c[2]) / 3 / 255
                    px[x, y] = shade(sc, 0.6 + lum * 0.7)
    for p in ((12, 9), (11, 10), (11, 11)):
        px[p] = (255, 255, 255, 230)
    return img


def candle_item():
    s = Sprite(S, seed=71)
    s.rect(12, 10, 19, 29, BLACK_WAX, bevel=1.5)
    s.ellipse(15.5, 10.5, 4.2, 1.6, BLACK_WAX, outline=False)
    img = s.render()
    px = img.load()
    for p in ((13, 11), (13, 12), (13, 13), (18, 11), (18, 12)):
        px[p] = (70, 70, 90, 255)  # wax drips
    px[15, 8] = px[15, 9] = (40, 30, 30, 255)
    for p, c in (((15, 3), (255, 240, 180)), ((15, 4), (255, 200, 80)), ((14, 5), (255, 140, 30)), ((15, 5), (255, 230, 150)), ((16, 5), (255, 140, 30)), ((15, 6), (255, 120, 20)), ((15, 7), (200, 60, 10))):
        px[p] = c + (255,)
    return with_glow(img, (255, 150, 40), radius=1.3, strength=0.4)


def llave_capilla():
    """Old wrought-iron chapel key: a cross-shaped bow, long shank, toothed bit, a brass tag on a string."""
    s = Sprite(S, seed=91)
    iron = STEEL
    # cross-shaped bow
    s.rect(6, 4, 9, 15, iron, bevel=1.2)
    s.rect(2, 8, 13, 11, iron, bevel=1.2)
    s.ellipse(7.5, 9.5, 2.0, 2.0, Material(['#050608', '#0c0e12', '#15181e']), dome=False, outline=False)
    # shank and bit
    s.rect(9, 8, 27, 11, iron, bevel=1.0)
    s.rect(22, 11, 24, 17, iron, bevel=0.8)
    s.rect(25, 11, 27, 15, iron, bevel=0.8)
    s.rect(20, 11, 21, 14, iron, bevel=0.6)
    # brass tag on a string
    s.poly([(10, 19), (17, 19), (18, 25), (11, 26)], GOLD)
    img = s.render()
    px = img.load()
    for p in ((9, 12), (9, 13), (10, 14), (10, 15), (10, 16), (11, 17), (11, 18)):
        px[p] = (120, 96, 60, 255)  # string
    for p in ((12, 21), (13, 21), (14, 21), (15, 22), (13, 23), (14, 23)):
        px[p] = (90, 54, 14, 255)  # engraved 'C'
    for p in ((3, 8), (6, 4), (10, 8), (22, 8)):
        px[p] = (230, 236, 244, 255)
    return img


def regla_quebracho():
    """Mother Remedios' quebracho ruler: a long dark-red hardwood ruler with brass-capped ends and cut marks."""
    s = Sprite(S, seed=93)
    wood = Material(['#1a0705', '#2e0e09', '#47170f', '#622418', '#7e3322', '#99462e'], spec=0.3, shininess=10)
    s.poly([(3, 25), (25, 3), (29, 7), (7, 29)], wood)
    s.poly([(3, 25), (6, 22), (10, 26), (7, 29)], GOLD)
    s.poly([(22, 6), (25, 3), (29, 7), (26, 10)], GOLD)
    img = s.render()
    px = img.load()
    for k in range(8, 24, 2):  # graduation marks along the edge
        x, y = k + 1, 29 - k - 2
        if 0 <= x < 32 and 0 <= y < 32 and px[x, y][3]:
            px[x, y] = (214, 182, 120, 255)
    for (x, y) in ((14, 17), (15, 16), (18, 14)):
        px[x, y] = (30, 8, 6, 255)
    return img


def diario_teresita():
    """Teresita's diary: a small navy notebook with a school label, a hair ribbon as bookmark, written backwards."""
    s = Sprite(S, seed=94)
    cover = Material(['#0b1024', '#121a33', '#1d2850', '#2b3a66', '#41558c'], ambient=0.4)
    s.rect(7, 4, 25, 28, cover, bevel=1.5)
    s.rect(9, 6, 24, 27, PAPER, bevel=0.5)
    s.rect(7, 4, 23, 26, cover, bevel=1.5)
    s.rect(11, 9, 20, 14, PAPER, bevel=0.5)
    img = s.render()
    px = img.load()
    for x in range(12, 20):  # label lines
        px[x, 11] = (90, 80, 70, 255) if x % 3 else px[x, 11]
        px[x, 12] = (90, 80, 70, 255) if x % 2 else px[x, 12]
    for y in range(3, 12):  # red hair ribbon bookmark
        px[21, y] = (190, 30, 40, 255)
        px[22, y] = (140, 20, 30, 255)
    px[21, 12] = px[22, 13] = (190, 30, 40, 255)
    return img


ALL.update({'flashlight_uv': flashlight_uv, 'ritual_candle': candle_item, 'llave_capilla': llave_capilla,
            'regla_quebracho': regla_quebracho, 'diario_teresita': diario_teresita})
for _k in EGG_COLORS:
    ALL[f'{_k}_spawn_egg'] = (lambda k=_k: spawn_egg(k))
