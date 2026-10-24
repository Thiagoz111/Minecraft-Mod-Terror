"""DEAD LINE - blood decals, blood letters, teeth and the lore papers of the Casa Morales (B1b).

Writes:
  textures/item/sangre/*.png   decals (com.deadline.horror.casa.BloodDecals): splatters, pool, hand prints, bare
                               footprints, runs, the ceiling stain, the bathtub, the letters of the blood writing,
                               human teeth and the Nona's dentures
  textures/item/lore/*.png     props lying in the house: Father Anselmo's letters, the broken rosary
  models/item/<group>/*.json   a two-sided flat quad per texture (item displays show them as decals)
  items/<group>/*.json         item model definitions (the displays set minecraft:item_model to deadline:<group>/<n>)
  textures/gui/lore/*.png      the documents read full screen (com.deadline.client.lore.LoreScreen): paper, Lucia's
                               notebook, the newspaper, the missal, the back of a photo, three 1961 photos, the rosary

Pixel art at the kit's density (32-64 px per block): shapes are rasterised as masks, shaded with hue-shifted ramps
by thickness (distance to the edge), rimmed and given a few deliberate highlights; alpha is 0 or 255 (cutout look).
Deterministic (seeded).  Run from the repo root:  python3 tools/art/sangre.py  (review sheet in <work>/art/sangre.png)
"""
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..'))
from workdir import WORK  # noqa: E402
import json
import math
import os

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
A = os.path.join(ROOT, 'src/main/resources/assets/deadline')
NS = 'deadline'

# ------------------------------------------------------------------ palettes
# blood: hue-shifted from cold near-black maroon (thick, in shadow) to warm red (thin film), a wet highlight
BLOOD = [(28, 2, 9), (52, 3, 11), (84, 6, 13), (116, 12, 15), (148, 22, 20), (176, 40, 30)]
SHINE = (222, 112, 98)
DRIED = [(46, 14, 12), (70, 22, 15), (92, 30, 18)]
ENAMEL = [(150, 132, 98), (186, 170, 132), (214, 202, 168), (236, 228, 204), (250, 246, 232)]
GUM = [(92, 30, 40), (134, 52, 62), (176, 84, 92), (206, 120, 124)]


def rng(seed):
    return np.random.default_rng(seed)


def save(img, rel):
    path = os.path.join(A, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)
    return path


def field(w, h):
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    return x + 0.5, y + 0.5


def blob(x, y, cx, cy, rx, ry, ang=0.0):
    c, s = math.cos(ang), math.sin(ang)
    dx, dy = x - cx, y - cy
    u = (dx * c + dy * s) / max(rx, 1e-3)
    v = (-dx * s + dy * c) / max(ry, 1e-3)
    return np.exp(-(u * u + v * v) * 1.6)


def smooth_noise(w, h, scale, seed):
    r = rng(seed)
    gw, gh = max(2, int(w / scale) + 2), max(2, int(h / scale) + 2)
    g = r.random((gh, gw)).astype(np.float32)
    big = np.array(Image.fromarray((g * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC), np.float32) / 255.0
    return big


def shade(mask, seed, ramp=BLOOD, gloss=True, rim=True, dry_edge=0.0, depth_scale=3.0):
    """RGBA from a boolean mask: thickness = distance to the edge picks the ramp tone; a darker rim; wet highlights."""
    h, w = mask.shape
    out = np.zeros((h, w, 4), np.uint8)
    if not mask.any():
        return Image.fromarray(out, 'RGBA')
    d = ndimage.distance_transform_edt(mask)
    n = smooth_noise(w, h, 5.0, seed) - 0.5
    # thin film at the edge is brighter, the thick middle darker (and darker still where it pooled)
    t = np.clip(1.0 - d / depth_scale + n * 0.5, 0, 1)
    idx = np.clip((t * (len(ramp) - 1) + 0.5).astype(int), 0, len(ramp) - 1)
    cols = np.array(ramp, np.uint8)[idx]
    out[..., :3] = cols
    out[..., 3] = np.where(mask, 255, 0)
    if rim:
        # the outermost pixel: a dark, dried edge (blood dries from the rim)
        er = mask & ~ndimage.binary_erosion(mask)
        rimcol = np.array(DRIED[1] if dry_edge > 0.5 else ramp[1], np.uint8)
        out[er, :3] = rimcol
        # a lit lower-left / shadowed upper-right bevel on the thickest parts
        sh = mask & ~np.roll(mask, (1, -1), (0, 1))
        out[sh & (d > 1.5), :3] = np.array(ramp[0], np.uint8)
    if gloss:
        r = rng(seed + 5)
        # wet glints: a few pixels on the upper-left slope of thick areas
        hl = mask & (d > 2.2) & ~np.roll(mask, (2, 2), (0, 1))
        ys, xs = np.nonzero(hl)
        if len(ys):
            pick = r.choice(len(ys), size=min(len(ys), max(1, len(ys) // 9)), replace=False)
            for i in pick:
                out[ys[i], xs[i], :3] = SHINE
                if xs[i] + 1 < w and mask[ys[i], xs[i] + 1]:
                    out[ys[i], xs[i] + 1, :3] = ramp[-1]
    return Image.fromarray(out, 'RGBA')


def thresh(f, level):
    return f > level


# ------------------------------------------------------------------ blood shapes
def splat(seed, size=48):
    """An impact splatter: a lobed body, satellite drops, spikes thrown outwards."""
    r = rng(seed)
    x, y = field(size, size)
    c = size / 2
    f = np.zeros_like(x)
    for _ in range(7):
        a = r.random() * 6.283
        d = r.random() * size * 0.12
        f += blob(x, y, c + math.cos(a) * d, c + math.sin(a) * d, size * (0.10 + r.random() * 0.08), size * (0.09 + r.random() * 0.07), r.random() * 3)
    f += (smooth_noise(size, size, 4.0, seed) - 0.5) * 0.35
    m = thresh(f, 0.55)
    # spikes: long thin drops thrown radially
    for _ in range(r.integers(6, 11)):
        a = r.random() * 6.283
        d0 = size * (0.2 + r.random() * 0.08)
        L = size * (0.08 + r.random() * 0.14)
        for k in range(int(L)):
            t = k / max(1, L)
            px, py = c + math.cos(a) * (d0 + k), c + math.sin(a) * (d0 + k)
            rad = (1.6 - t * 1.2) * (size / 48)
            m |= (x - px) ** 2 + (y - py) ** 2 < max(0.35, rad) ** 2
        # a drop at the tip
        px, py = c + math.cos(a) * (d0 + L + 1.5), c + math.sin(a) * (d0 + L + 1.5)
        m |= (x - px) ** 2 + (y - py) ** 2 < (0.9 + r.random()) ** 2
    # satellites
    for _ in range(r.integers(10, 18)):
        a = r.random() * 6.283
        d = size * (0.28 + r.random() * 0.2)
        rad = 0.6 + r.random() * 1.4
        m |= (x - c - math.cos(a) * d) ** 2 + (y - c - math.sin(a) * d) ** 2 < rad ** 2
    m &= (x > 0.5) & (x < size - 0.5) & (y > 0.5) & (y < size - 0.5)
    return shade(m, seed, depth_scale=4.0)


def pool(seed, size=48):
    """Thick, slow blood: a round pool with soft lobes, darker and glossier than a splatter."""
    r = rng(seed)
    x, y = field(size, size)
    c = size / 2
    ang = np.arctan2(y - c, x - c)
    rad = np.hypot(x - c, y - c)
    edge = size * 0.40 + size * 0.04 * np.sin(ang * 3 + r.random() * 6) + size * 0.03 * np.sin(ang * 5 + r.random() * 6)
    edge = edge + (smooth_noise(size, size, 6.0, seed) - 0.5) * size * 0.06
    m = rad < edge
    for _ in range(4):
        a = r.random() * 6.283
        m |= (x - c - math.cos(a) * size * 0.43) ** 2 + (y - c - math.sin(a) * size * 0.43) ** 2 < (1.0 + r.random()) ** 2
    img = shade(m, seed, ramp=BLOOD[:5], depth_scale=7.0)
    a = np.array(img)
    # a short curved reflection near the rim (the room's light on a thick wet surface)
    arc = m & (np.abs(np.hypot(x - c, y - c) - size * 0.30) < 0.7) & (ang > -2.6) & (ang < -1.9)
    a[arc, :3] = np.array(BLOOD[4], np.uint8)
    return Image.fromarray(a, 'RGBA')


def ceiling_stain(seed, size=32):
    """Blood soaking through plaster: a ragged brown-red stain, darker and wetter in the middle."""
    x, y = field(size, size)
    c = size / 2
    n = smooth_noise(size, size, 3.0, seed)
    rad = np.hypot(x - c, y - c) / (size * 0.47)
    m = rad + (n - 0.5) * 0.55 < 0.85
    img = shade(m, seed, ramp=[(40, 6, 9), (66, 12, 12), (90, 22, 16), (112, 36, 22), (128, 52, 34)], gloss=False, dry_edge=1.0,
                depth_scale=6.0)
    a = np.array(img)
    core = rad < 0.18
    a[core & m, :3] = np.array(BLOOD[1], np.uint8)
    return Image.fromarray(a, 'RGBA')


def hand(seed, left, w=24, h=28, drag=False):
    """A bloody hand print, fingers up; uneven coverage (skin lines), the thumb on the right for a left hand."""
    r = rng(seed)
    x, y = field(w, h)
    m = np.zeros((h, w), bool)
    palm_cx, palm_cy = w * 0.5, h * 0.66
    m |= ((x - palm_cx) / (w * 0.30)) ** 2 + ((y - palm_cy) / (h * 0.22)) ** 2 < 1
    # four fingers: capsules fanning slightly
    tips = [(-0.27, 0.10), (-0.09, 0.03), (0.09, 0.06), (0.25, 0.17)]
    for i, (dx, ty) in enumerate(tips):
        bx = palm_cx + dx * w
        by = palm_cy - h * 0.16
        tx = bx + dx * w * 0.25
        tyy = ty * h + r.random() * 1.2
        for k in range(24):
            t = k / 23
            px, py = bx + (tx - bx) * t, by + (tyy - by) * t
            rad = w * (0.075 if i != 3 else 0.065)
            m |= (x - px) ** 2 + (y - py) ** 2 < rad ** 2
        # the fingertip print is the darkest
    # thumb, out to the side
    side = 1 if left else -1
    bx, by = palm_cx + side * w * 0.22, palm_cy - h * 0.02
    tx, ty = palm_cx + side * w * 0.46, palm_cy - h * 0.24
    for k in range(20):
        t = k / 19
        px, py = bx + (tx - bx) * t, by + (ty - by) * t
        m |= (x - px) ** 2 + (y - py) ** 2 < (w * 0.08) ** 2
    # skin lines and pressure gaps: the middle of the palm prints badly
    gaps = (smooth_noise(w, h, 1.6, seed + 3) > 0.74) & (((x - palm_cx) / (w * 0.18)) ** 2 + ((y - palm_cy) / (h * 0.12)) ** 2 < 1)
    m &= ~gaps
    m &= (x > 0) & (x < w) & (y > 0) & (y < h)
    return shade(m, seed, depth_scale=2.5)


def hand_drag(seed, left, w=24, h=60):
    """A hand print at the top and the smear it left sliding down: four finger tracks, the palm's wide trail."""
    r = rng(seed)
    x, y = field(w, h)
    top = np.array(hand(seed, left, w, 28))[..., 3] > 0
    m = np.zeros((h, w), bool)
    m[:28] = top
    for i, cx in enumerate((0.27, 0.42, 0.58, 0.73)):
        x0 = cx * w + (r.random() - 0.5) * 1.5
        y0 = 8 + r.random() * 4
        L = h * (0.55 + r.random() * 0.4)
        wob = r.random() * 6
        for k in range(int(L)):
            py = y0 + k
            px = x0 + math.sin(k * 0.08 + wob) * 0.8
            rad = 1.3 * (1 - k / L) + 0.35
            m |= (x - px) ** 2 + (y - py) ** 2 < rad ** 2
    trail = (np.abs(x - w * 0.5) < w * 0.26 * (1 - (y - 20) / (h - 20)) + 0.5) & (y > 18) & (y < h * 0.7)
    trail &= smooth_noise(w, h, 2.0, seed + 7) > 0.38
    m |= trail
    m &= (y < h - 0.5)
    return shade(m, seed, depth_scale=2.2)


FOOT = [  # a LEFT bare footprint, toes up ('#' printed, '+' printed thin, '.' nothing); the arch is the notch
    "..........###.",
    "......##..####",
    "....#.##..####",
    "..#.#.##..####",
    "..#.#..#...##.",
    "..#...........",
    "..............",
    "....########..",
    "..###########.",
    ".######+######",
    ".#####++######",
    ".######+######",
    ".############.",
    ".###########..",
    ".#########....",
    ".########.....",
    ".#######......",
    ".######.......",
    ".######.......",
    ".######.......",
    ".#######......",
    ".########.....",
    "..########....",
    "..####+####...",
    "..###+++###...",
    "..####+####...",
    "..#########...",
    "...#######....",
    "....#####.....",
    "..............",
]


def foot(seed, left, w=14, h=30):
    """A bare footprint, toes at the top: five toes (the big one fat), the ball, the outer edge of the sole (the arch
    never touches the floor) and the heel, thinner where the skin pressed less. Texture +x is the walker's right: the
    big toe is on the right of a LEFT foot; a right foot is its mirror image."""
    r = rng(seed)
    full = np.array([[ch == '#' for ch in row] for row in FOOT])
    thin = np.array([[ch == '+' for ch in row] for row in FOOT])
    if not left:
        full, thin = full[:, ::-1], thin[:, ::-1]
    m = full | (thin & (r.random(thin.shape) < 0.4))
    img = np.array(shade(m, seed, ramp=BLOOD[1:5], depth_scale=1.6, gloss=False))
    return Image.fromarray(img, 'RGBA')


def runs(seed, w=24, h=48):
    """Blood running down a wall from a smear at the top: a few drips of different lengths, each ending in a bead."""
    r = rng(seed)
    x, y = field(w, h)
    m = ((x - w / 2) / (w * 0.45)) ** 2 + ((y - 5) / 5.0) ** 2 < 1
    m &= smooth_noise(w, h, 2.5, seed) > 0.25
    for _ in range(r.integers(3, 6)):
        x0 = w * (0.15 + r.random() * 0.7)
        L = h * (0.3 + r.random() * 0.62)
        wid = 0.7 + r.random() * 0.9
        for k in range(int(L)):
            py = 4 + k
            px = x0 + math.sin(k * 0.05 + x0) * 0.6
            m |= (x - px) ** 2 + (y - py) ** 2 < (wid * (1 - 0.3 * k / L)) ** 2
        m |= (x - x0) ** 2 + (y - (4 + L)) ** 2 < (wid + 0.7) ** 2
    m &= (y < h - 0.5)
    return shade(m, seed, depth_scale=2.2)


def tub(seed, w=96, h=36, ring=False):
    """The bathtub basin seen from above, full of blood (or: the ring it left when it drained)."""
    x, y = field(w, h)
    rr = h * 0.48
    inside = (np.maximum(0, np.abs(x - w / 2) - (w / 2 - rr)) ** 2 + (y - h / 2) ** 2) < rr ** 2
    if not ring:
        img = shade(inside, seed, ramp=BLOOD[:5], depth_scale=10.0)
        a = np.array(img)
        r = rng(seed)
        for _ in range(7):  # bubbles breaking the skin
            cx, cy = r.random() * w * 0.8 + w * 0.1, r.random() * h * 0.6 + h * 0.2
            rad = 1.0 + r.random() * 1.6
            ringm = inside & (np.abs(np.hypot(x - cx, y - cy) - rad) < 0.6)
            a[ringm, :3] = np.array(BLOOD[4], np.uint8)
        band = inside & (np.abs(y - h * 0.3 - (x - w / 2) * 0.05) < 0.8) & (np.abs(x - w / 2) < w * 0.32)
        a[band, :3] = np.array(BLOOD[3], np.uint8)
        return Image.fromarray(a, 'RGBA')
    edge = inside & ~ndimage.binary_erosion(inside, iterations=2)
    edge &= smooth_noise(w, h, 2.0, seed + 1) > 0.3
    smear = inside & (smooth_noise(w, h, 3.0, seed) > 0.84)
    plug = (x - w * 0.12) ** 2 + (y - h / 2) ** 2 < 9
    m = edge | smear | (plug & inside)
    return shade(m, seed, ramp=DRIED + [BLOOD[3]], gloss=False, dry_edge=1.0, depth_scale=2.0)


# ------------------------------------------------------------------ the blood letters
_C = [(0.85, 0.15), (0.6, 0.0), (0.3, 0.05), (0.12, 0.3), (0.1, 0.62), (0.25, 0.92), (0.55, 1.0), (0.85, 0.86)]
_O = [(0.5 + 0.42 * math.cos(a), 0.5 + 0.5 * math.sin(a)) for a in np.linspace(-1.5, 4.9, 14)]
_P = [(0.15, 1.0), (0.15, 0.0), (0.62, 0.0), (0.84, 0.13), (0.84, 0.38), (0.62, 0.52), (0.15, 0.52)]
GLYPHS = {
    'a': [[(0.08, 1.0), (0.5, 0.0), (0.92, 1.0)], [(0.27, 0.62), (0.73, 0.62)]],
    'b': [[(0.15, 0.0), (0.15, 1.0)], [(0.15, 0.0), (0.62, 0.0), (0.8, 0.12), (0.8, 0.35), (0.62, 0.48), (0.15, 0.48)],
          [(0.62, 0.48), (0.86, 0.62), (0.86, 0.87), (0.66, 1.0), (0.15, 1.0)]],
    'c': [_C],
    'd': [[(0.15, 0.0), (0.15, 1.0)], [(0.15, 0.0), (0.55, 0.0), (0.82, 0.2), (0.9, 0.5), (0.82, 0.8), (0.55, 1.0), (0.15, 1.0)]],
    'e': [[(0.84, 0.0), (0.15, 0.0), (0.15, 1.0), (0.84, 1.0)], [(0.15, 0.5), (0.66, 0.5)]],
    'f': [[(0.84, 0.0), (0.15, 0.0), (0.15, 1.0)], [(0.15, 0.5), (0.66, 0.5)]],
    'g': [_C, [(0.86, 0.86), (0.86, 0.58), (0.55, 0.58)]],
    'h': [[(0.15, 0.0), (0.15, 1.0)], [(0.85, 0.0), (0.85, 1.0)], [(0.15, 0.5), (0.85, 0.5)]],
    'i': [[(0.5, 0.0), (0.5, 1.0)], [(0.28, 0.0), (0.72, 0.0)], [(0.28, 1.0), (0.72, 1.0)]],
    'j': [[(0.75, 0.0), (0.75, 0.75), (0.6, 0.98), (0.35, 1.0), (0.15, 0.8)]],
    'k': [[(0.15, 0.0), (0.15, 1.0)], [(0.85, 0.0), (0.18, 0.56)], [(0.38, 0.42), (0.88, 1.0)]],
    'l': [[(0.18, 0.0), (0.18, 1.0), (0.85, 1.0)]],
    'm': [[(0.08, 1.0), (0.12, 0.0), (0.5, 0.58), (0.88, 0.0), (0.92, 1.0)]],
    'n': [[(0.15, 1.0), (0.15, 0.0), (0.85, 1.0), (0.85, 0.0)]],
    'o': [_O],
    'p': [_P],
    'q': [_O, [(0.6, 0.72), (0.94, 1.04)]],
    'r': [_P, [(0.45, 0.52), (0.88, 1.0)]],
    's': [[(0.86, 0.12), (0.6, 0.0), (0.3, 0.02), (0.13, 0.2), (0.25, 0.43), (0.7, 0.55), (0.88, 0.76), (0.75, 0.96),
           (0.4, 1.0), (0.12, 0.88)]],
    't': [[(0.06, 0.0), (0.94, 0.0)], [(0.5, 0.0), (0.5, 1.0)]],
    'u': [[(0.15, 0.0), (0.15, 0.72), (0.3, 0.96), (0.5, 1.0), (0.7, 0.96), (0.85, 0.72), (0.85, 0.0)]],
    'v': [[(0.08, 0.0), (0.5, 1.0), (0.92, 0.0)]],
    'w': [[(0.04, 0.0), (0.25, 1.0), (0.5, 0.4), (0.75, 1.0), (0.96, 0.0)]],
    'x': [[(0.12, 0.0), (0.88, 1.0)], [(0.88, 0.0), (0.12, 1.0)]],
    'y': [[(0.08, 0.0), (0.5, 0.5), (0.92, 0.0)], [(0.5, 0.5), (0.5, 1.0)]],
    'z': [[(0.12, 0.0), (0.88, 0.0), (0.12, 1.0), (0.88, 1.0)]],
}
ACCENT = [(0.5, -0.12), (0.78, -0.34)]
LW, LH = 24, 30
GTOP, GBOT = 6.0, 22.0  # the glyph's box (rows); the accent goes above, drips below


def letter(ch, seed, accent=False):
    """A letter written with a finger dipped in blood: wobbling strokes, blobs where the finger pressed, runs below."""
    r = rng(seed)
    x, y = field(LW, LH)
    m = np.zeros((LH, LW), bool)
    strokes = [list(s) for s in GLYPHS[ch]] + ([ACCENT] if accent else [])
    bottoms = []
    for si, s in enumerate(strokes):
        pts = [(2.5 + px * (LW - 5), GTOP + py * (GBOT - GTOP)) for px, py in s]
        total = sum(math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(len(pts) - 1))
        walked = 0.0
        wob = r.random() * 6
        for i in range(len(pts) - 1):
            (x0, y0), (x1, y1) = pts[i], pts[i + 1]
            L = math.hypot(x1 - x0, y1 - y0)
            n = max(2, int(L * 3))
            for k in range(n):
                t = k / (n - 1)
                px, py = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
                u = (walked + L * t) / max(1e-3, total)
                # the finger presses hard at the start and runs dry at the end
                rad = 1.75 - 0.75 * u + 0.25 * math.sin(u * 9 + wob)
                px += 0.35 * math.sin(u * 7 + wob)
                m |= (x - px) ** 2 + (y - py) ** 2 < rad ** 2
                if py > GBOT - 1.5:
                    bottoms.append((px, py))
            walked += L
        # a blob where the stroke began
        sx, sy = pts[0]
        m |= (x - sx) ** 2 + (y - sy) ** 2 < (2.1 + r.random() * 0.4) ** 2
    # runs: from the lowest points of the letter (and one from the middle bar sometimes)
    r.shuffle(bottoms)
    for (bx, by) in bottoms[:r.integers(1, 3)]:
        L = 2 + r.random() * (LH - by - 3)
        for k in range(int(L)):
            m |= (x - bx - math.sin(k * 0.3) * 0.2) ** 2 + (y - by - k) ** 2 < (0.75 - 0.25 * k / max(1, L)) ** 2 * 1.8
        m |= (x - bx) ** 2 + (y - by - L) ** 2 < 1.2 ** 2
    m &= (x > 0) & (x < LW) & (y > 0) & (y < LH)
    return shade(m, seed, depth_scale=2.0, gloss=False)


# ------------------------------------------------------------------ teeth
TOOTH = {
    # molar: a crown with cusps and two roots; incisor: a flat blade; canine: a fang with a long root ('.' = empty,
    # 'w' enamel light, 'e' enamel, 's' shade, 'y' yellowed root, 'r' blood, 'd' dark blood)
    0: ["............",
        "..ww.ww.ww..",
        ".weeeeeeeew.",
        ".weeeeeeees.",
        ".eeeeeeeess.",
        ".seeeeeeess.",
        "..syyyyyys..",
        "..yy.....yy.",
        "..yy....yy..",
        "..yr....yr..",
        "..dr....rd..",
        "............"],
    1: ["....wwww....",
        "....weee....",
        "....weee....",
        "....eees....",
        "....eees....",
        "....eess....",
        ".....yy.....",
        ".....yy.....",
        ".....yy.....",
        ".....yr.....",
        ".....rd.....",
        "............"],
    2: [".....w......",
        "....wee.....",
        "....wees....",
        "...weees....",
        "...eeess....",
        "...seess....",
        "....yys.....",
        "....yy......",
        "....yy......",
        ".....yr.....",
        ".....rd.....",
        "......d....."],
}
TOOTH_COL = {'w': ENAMEL[4], 'e': ENAMEL[3], 's': ENAMEL[1], 'y': (196, 178, 128), 'r': BLOOD[3], 'd': BLOOD[1]}


def tooth(kind, seed, size=12):
    img = np.zeros((size, size, 4), np.uint8)
    for j, row in enumerate(TOOTH[kind]):
        for i, ch in enumerate(row):
            if ch in TOOTH_COL:
                img[j, i, :3] = TOOTH_COL[ch]
                img[j, i, 3] = 255
    return Image.fromarray(img, 'RGBA')


def denture(seed, size=32):
    """The Nona's upper dentures seen from above, front teeth at the top: the pink horseshoe with its palate plate, a row
    of too-white teeth on the outer arc, blood dark in the joints and smeared on the gum."""
    x, y = field(size, size)
    r = rng(seed)
    img = np.zeros((size, size, 4), np.uint8)
    cx, cy = size / 2, size * 0.62
    outer = ell(x, y, cx, cy, size * 0.44, size * 0.52) & (y < size * 0.9)
    inner = ell(x, y, cx, cy + 1.5, size * 0.24, size * 0.32) & (y < size * 0.9)
    gum = outer & ~inner
    plate = inner
    img[gum, :3] = GUM[2]
    img[plate, :3] = GUM[3]
    img[outer, 3] = 255
    rim = outer & ~ndimage.binary_erosion(outer)
    img[rim, :3] = GUM[0]
    for k in range(4):  # palate ridges
        ridge = plate & (np.abs(y - (cy - 5 + k * 3) + np.abs(x - cx) * 0.25) < 0.5) & (np.abs(x - cx) < 5)
        img[ridge, :3] = GUM[2]
    # teeth along the outer arc (front ones bigger)
    for a in np.linspace(math.pi * 1.06, math.pi * 1.94, 12):
        tx = cx + math.cos(a) * size * 0.35
        ty = cy + math.sin(a) * size * 0.42
        front = abs(a - math.pi * 1.5) < 0.45
        rr = 2.3 if front else 1.9
        t = ((x - tx) ** 2 + (y - ty) ** 2) < rr ** 2
        img[t, :3] = ENAMEL[3]
        img[t & (y < ty), :3] = ENAMEL[4]
        img[t & (y > ty + 0.8), :3] = ENAMEL[1]
        img[t, 3] = 255
    teeth = (img[..., :3] == np.array(ENAMEL[3], np.uint8)).all(-1) | (img[..., :3] == np.array(ENAMEL[4], np.uint8)).all(-1)
    joints = teeth & ~ndimage.binary_erosion(teeth) & (y > cy - size * 0.42 + 2)
    img[joints, :3] = BLOOD[2]
    blood = outer & (smooth_noise(size, size, 2.0, seed) > 0.8)
    img[blood, :3] = BLOOD[3]
    img[blood & (r.random((size, size)) < 0.3), :3] = BLOOD[1]
    return Image.fromarray(img, 'RGBA')


# ------------------------------------------------------------------ lore props (lying in the house)
def cartas(seed=401, size=32):
    """Three old letters in their envelopes, yellowed, tied crosswise with red string (seen from above)."""
    r = rng(seed)
    im = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    papers = [(212, 198, 160), (198, 182, 140), (224, 212, 178)]
    for i, (ox, oy, ang) in enumerate(((5, 9, -8), (4, 8, 6), (6, 7, -2))):
        env = Image.new('RGBA', (22, 15), papers[i] + (255,))
        e = ImageDraw.Draw(env)
        e.rectangle((0, 0, 21, 14), outline=(150, 132, 96, 255))
        e.line((0, 0, 11, 8, 21, 0), fill=(168, 150, 112, 255))
        for k in range(3):
            e.line((5, 9 + k * 2 if i == 2 else 10 + k * 2, 5 + r.integers(8, 13), 9 + k * 2 if i == 2 else 10 + k * 2),
                   fill=(52, 56, 82, 255))
        env = env.rotate(ang, resample=Image.NEAREST, expand=True)
        im.alpha_composite(env, (ox - 1, oy - 2 + i))
    d.line((3, 16, 29, 17), fill=(150, 22, 26, 255), width=1)
    d.line((15, 4, 16, 29), fill=(150, 22, 26, 255), width=1)
    d.point([(15, 16), (16, 17), (14, 17)], fill=(110, 12, 18, 255))
    return im


def rosario(seed=402, size=32, scale=1):
    """A rosary with its string broken: the loop of dark beads open, the frayed (bitten) ends, beads rolled away."""
    r = rng(seed)
    S = size * scale
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    bead = [(26, 16, 14), (58, 36, 28), (96, 66, 48), (150, 116, 86)]
    chain = (96, 90, 82, 255)
    pts = []
    for a in np.linspace(-0.6, 4.4, 22):
        pts.append((S * 0.5 + math.cos(a) * S * 0.33 + r.normal(0, 0.4 * scale), S * 0.45 + math.sin(a) * S * 0.27 + r.normal(0, 0.4 * scale)))
    for i in range(len(pts) - 1):
        d.line((pts[i], pts[i + 1]), fill=chain, width=max(1, scale // 2))
    br = 1.3 * scale
    for (px, py) in pts[::2]:
        d.ellipse((px - br, py - br, px + br, py + br), fill=bead[1] + (255,))
        d.point((px - br * 0.4, py - br * 0.4), fill=bead[3] + (255,))
    # the tail and the crucifix
    tail = [pts[0], (S * 0.62, S * 0.68), (S * 0.6, S * 0.78)]
    d.line(tail, fill=chain, width=max(1, scale // 2))
    cx, cy = S * 0.6, S * 0.84
    d.rectangle((cx - 0.6 * scale, cy - 3 * scale, cx + 0.6 * scale, cy + 4 * scale), fill=(176, 170, 156, 255))
    d.rectangle((cx - 2.4 * scale, cy - 1.3 * scale, cx + 2.4 * scale, cy - 0.2 * scale), fill=(176, 170, 156, 255))
    # frayed, bitten ends at the break
    for (ex, ey) in (pts[-1],):
        for k in range(3):
            d.line((ex, ey, ex + r.normal(0, 1.6) * scale, ey + r.normal(1.5, 1.0) * scale), fill=(140, 128, 108, 255))
    for _ in range(5):  # loose beads
        bx, by = S * (0.2 + r.random() * 0.6), S * (0.7 + r.random() * 0.25)
        d.ellipse((bx - br, by - br, bx + br, by + br), fill=bead[1] + (255,))
        d.point((bx - br * 0.4, by - br * 0.4), fill=bead[3] + (255,))
    return im


# ------------------------------------------------------------------ the papers (GUI, full screen)
def paper_base(w, h, seed, base=(222, 210, 178), dark=(176, 150, 104)):
    r = rng(seed)
    x, y = field(w, h)
    n = smooth_noise(w, h, 9.0, seed) * 0.6 + smooth_noise(w, h, 2.5, seed + 1) * 0.4
    edge = np.minimum(np.minimum(x, w - x), np.minimum(y, h - y))
    k = np.clip(1.0 - edge / 22.0, 0, 1) ** 1.6 * 0.55 + (n - 0.5) * 0.18
    rgb = np.array(base, np.float32)[None, None, :] * (1 - k[..., None]) + np.array(dark, np.float32)[None, None, :] * k[..., None]
    # foxing: small brown spots
    for _ in range(int(w * h / 1400)):
        cx, cy, rr = r.random() * w, r.random() * h, 0.8 + r.random() * 2.2
        spot = (x - cx) ** 2 + (y - cy) ** 2 < rr ** 2
        rgb[spot] = rgb[spot] * 0.86 + np.array((150, 104, 60), np.float32) * 0.14
    grain = r.normal(0, 3.0, (h, w, 1))
    rgb = np.clip(rgb + grain, 0, 255)
    a = np.full((h, w), 255, np.uint8)
    return rgb, a


def to_img(rgb, a):
    out = np.zeros(rgb.shape[:2] + (4,), np.uint8)
    out[..., :3] = np.clip(rgb, 0, 255).astype(np.uint8)
    out[..., 3] = a
    return Image.fromarray(out, 'RGBA')


def ragged(a, seed, depth=3.0):
    """Torn / worn edges: alpha cut by a noisy margin."""
    h, w = a.shape
    x, y = field(w, h)
    n = smooth_noise(w, h, 3.0, seed)
    edge = np.minimum(np.minimum(x, w - x), np.minimum(y, h - y))
    a = a.copy()
    a[edge < 1.0 + n * depth] = 0
    return a


def gui_papel():
    """A letter on thin paper, folded in three, the folds darker, foxed."""
    w, h = 192, 256
    rgb, a = paper_base(w, h, 11, base=(226, 216, 186), dark=(184, 160, 116))
    x, y = field(w, h)
    for fy in (h / 3, 2 * h / 3):
        fold = np.abs(y - fy) < 1.0
        rgb[fold] *= 0.9
        rgb[np.abs(y - fy - 1.5) < 0.5] = np.minimum(255, rgb[np.abs(y - fy - 1.5) < 0.5] * 1.04)
    a = ragged(a, 12, 1.5)
    return to_img(rgb, a)


def gui_cuaderno():
    """A page torn from a school notebook: blue rules every 12 px, a red margin, the spiral's holes, a child's doodle."""
    w, h = 192, 256
    rgb, a = paper_base(w, h, 21, base=(236, 234, 224), dark=(204, 196, 176))
    x, y = field(w, h)
    for yy in range(25 + 9, h - 6, 12):
        line = np.abs(y - yy) < 0.5
        rgb[line] = rgb[line] * 0.55 + np.array((120, 150, 196), np.float32) * 0.45
    margin = np.abs(x - 28) < 0.6
    rgb[margin] = rgb[margin] * 0.4 + np.array((200, 70, 76), np.float32) * 0.6
    for yy in range(14, h - 8, 16):
        hole = (x - 9) ** 2 + (y - yy) ** 2 < 9
        a[hole] = 0
        ring = ((x - 9) ** 2 + (y - yy) ** 2 < 14) & ~hole
        rgb[ring] *= 0.86
    # the torn left edge (ripped out of the spiral)
    n = smooth_noise(w, h, 2.0, 22)
    a[x < 2.5 + n * 2.5] = 0
    a = ragged(a, 23, 1.0)
    return to_img(rgb, a)


def gui_recorte():
    """A clipping of 1961 newsprint: grey-yellow, coarse, cut by hand with scissors, a fold across."""
    w, h = 192, 256
    rgb, a = paper_base(w, h, 31, base=(206, 198, 168), dark=(168, 150, 110))
    r = rng(32)
    rgb = rgb + r.normal(0, 5.0, rgb.shape)
    x, y = field(w, h)
    rule = (np.abs(y - 37) < 0.6) | (np.abs(y - 39.5) < 0.5)
    rgb[rule & (x > 12) & (x < w - 12)] = (40, 38, 34)
    fold = np.abs(y - h * 0.55) < 0.8
    rgb[fold] *= 0.88
    # scissor cut: a slightly crooked rectangle
    tilt = (x - w / 2) * 0.015
    a[(y < 3 + tilt) | (y > h - 4 + tilt) | (x < 3) | (x > w - 3)] = 0
    return to_img(np.clip(rgb, 0, 255), a)


def gui_misal():
    """A page of an old missal: thick cream paper, a red double frame, fake Latin print at the foot of the page."""
    w, h = 192, 256
    rgb, a = paper_base(w, h, 41, base=(232, 220, 190), dark=(190, 168, 124))
    x, y = field(w, h)
    red = np.array((150, 30, 28), np.float32)
    for m in (10, 13):
        fr = ((np.abs(x - m) < 0.6) | (np.abs(x - (w - m)) < 0.6)) & (y > m) & (y < h - m) | \
             ((np.abs(y - m) < 0.6) | (np.abs(y - (h - m)) < 0.6)) & (x > m) & (x < w - m)
        rgb[fr] = rgb[fr] * 0.3 + red * 0.7
    r = rng(42)
    for row in range(186, h - 18, 7):
        cx = 20.0
        while cx < w - 22:
            wl = r.integers(4, 15)
            word = (x > cx) & (x < cx + wl) & (np.abs(y - row) < 1.2)
            word &= r.random((h, w)) < 0.75
            ink = red if r.random() < 0.08 else np.array((50, 40, 34), np.float32)
            rgb[word] = rgb[word] * 0.35 + ink * 0.65
            cx += wl + 3
    a = ragged(a, 43, 1.2)
    return to_img(rgb, a)


def gui_dorso():
    """The back of an old photograph: a card yellowed from the edges, a studio stamp, a glue stain from an album."""
    w, h = 192, 144
    rgb, a = paper_base(w, h, 51, base=(230, 224, 206), dark=(196, 180, 140))
    x, y = field(w, h)
    stamp = (np.abs(x - 150) < 26) & (np.abs(y - 120) < 9) & ~((np.abs(x - 150) < 24.5) & (np.abs(y - 120) < 7.5))
    rgb[stamp] = rgb[stamp] * 0.45 + np.array((110, 80, 140), np.float32) * 0.55
    r = rng(52)
    for k in range(5):
        m = (np.abs(x - (132 + k * 8)) < 2.5) & (np.abs(y - 120) < 2.5) & (r.random((h, w)) < 0.6)
        rgb[m] = rgb[m] * 0.5 + np.array((110, 80, 140), np.float32) * 0.5
    for (cx, cy) in ((12, 12), (w - 12, 12)):
        glue = (x - cx) ** 2 + (y - cy) ** 2 < 64
        rgb[glue] = rgb[glue] * 0.9 + np.array((150, 120, 70), np.float32) * 0.1
    return to_img(rgb, a)


def photo_base(w, h, seed, level=150.0):
    r = rng(seed)
    x, y = field(w, h)
    vig = 1.0 - 0.6 * (((x - w / 2) / (w / 2)) ** 2 + ((y - h / 2) / (h / 2)) ** 2) / 2
    lum = np.full((h, w), level, np.float32) * np.clip(vig, 0.25, 1)
    return r, x, y, lum


def sepia(lum, seed, scratches=3, tone=(1.0, 0.84, 0.62)):
    r = rng(seed)
    h, w = lum.shape
    x, y = field(w, h)
    lum = lum + r.normal(0, 6.0, lum.shape)
    for _ in range(scratches):
        x0 = r.random() * w
        sl = (r.random() - 0.5) * 0.3
        m = np.abs(x - x0 - (y - h / 2) * sl) < 0.5
        y0 = r.random() * h * 0.7
        m &= (y > y0) & (y < y0 + h * (0.1 + r.random() * 0.25))
        lum[m] = lum[m] * 0.4 + 120
    for _ in range(14):
        cx, cy = r.random() * w, r.random() * h
        lum[(x - cx) ** 2 + (y - cy) ** 2 < 1.1] = 230
    rgb = np.stack([lum * tone[0], lum * tone[1], lum * tone[2]], -1)
    out = np.zeros((h, w, 4), np.uint8)
    out[..., :3] = np.clip(rgb, 0, 255).astype(np.uint8)
    out[..., 3] = 255
    return Image.fromarray(out, 'RGBA')


def ell(x, y, cx, cy, rx, ry):
    return ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 < 1


def photo_nona_cura():
    """1961: a girl of eight in a white dress beside a priest's black cassock -- his head out of the frame, his hand
    on her shoulder. She does not smile. Her eyes have caught the light wrong: two pale dots."""
    w, h = 160, 120
    r, x, y, lum = photo_base(w, h, 61, 158)
    # the wall and a door frame behind
    lum[(np.abs(x - 34) < 3) & (y < 104)] *= 0.7
    lum[(x > 22) & (x < 46) & (y < 104)] *= 0.86
    floor = y > 100
    lum[floor] *= 0.78
    # the cassock: a tall black column from above the frame to the floor, an arm reaching over
    cass = (np.abs(x - 98) < 15 + (y / h) * 6) & (y < 112)
    lum[cass] = 34
    lum[(np.abs(x - 98) < 3) & (y < 60)] = 26  # the buttons' line
    for by in range(8, 100, 8):
        lum[(np.abs(x - 98) < 1) & (np.abs(y - by) < 1)] = 70
    arm = ell(x, y, 80, 44, 12, 4.5)
    lum[arm] = 30
    hand_m = ell(x, y, 69, 46, 4.5, 3.6)
    lum[hand_m] = 178
    # the girl: white dress, dark hair, a small pale face
    dress = (np.abs(x - 64) < 9 + (y - 48) * 0.18) & (y > 48) & (y < 98)
    lum[dress] = 214
    lum[(np.abs(x - 64) < 9 + (y - 48) * 0.18) & (np.abs(y - 60) < 1)] = 190  # a sash
    legs = ((np.abs(x - 60) < 2) | (np.abs(x - 68) < 2)) & (y >= 98) & (y < 108)
    lum[legs] = 190
    lum[(y >= 106) & (y < 110) & ((np.abs(x - 60) < 3) | (np.abs(x - 68) < 3))] = 40  # shoes
    hair = ell(x, y, 64, 36, 9, 10)
    lum[hair] = 46
    face = ell(x, y, 64, 39, 6.2, 7.5)
    lum[face] = 196
    for ex in (61.5, 66.5):
        lum[ell(x, y, ex, 38, 1.4, 1.0)] = 120
        lum[(np.abs(x - ex) < 0.6) & (np.abs(y - 38) < 0.6)] = 245   # the eyes: pale dots
    lum[(np.abs(x - 64) < 2) & (np.abs(y - 43.5) < 0.5)] = 120  # a straight mouth
    lum[(x - 64) ** 2 + (y - 52) ** 2 < 4] = 120  # a cross on a chain
    return sepia(lum, 62)


def photo_nelida():
    """Christmas 1960: a girl on a chair with a porcelain doll on her lap. The girl moved: her face is a blur. The
    doll did not: it looks straight at the camera, the sharpest thing in the picture."""
    w, h = 160, 120
    r, x, y, lum = photo_base(w, h, 71, 140)
    tree = (np.abs(x - 124) < (y - 14) * 0.38) & (y > 14) & (y < 92)
    lum[tree] = 58
    for _ in range(18):
        bx, by = 124 + r.normal(0, 9), 30 + r.random() * 58
        if abs(bx - 124) < (by - 14) * 0.38:
            lum[(x - bx) ** 2 + (y - by) ** 2 < 2.2] = 200
    lum[(np.abs(x - 124) < 3) & (y >= 92) & (y < 100)] = 40
    chair = (np.abs(x - 64) < 20) & (y > 62) & (y < 108)
    lum[chair] = 66
    lum[(np.abs(x - 64) < 22) & (y > 30) & (y < 64) & (np.abs(x - 64) > 18)] = 60
    # the girl
    body = (np.abs(x - 64) < 13 + (y - 50) * 0.2) & (y > 50) & (y < 92)
    lum[body] = 180
    hair = ell(x, y, 64, 34, 11, 12)
    lum[hair] = 52
    face = ell(x, y, 64, 37, 7, 8.5)
    lum[face] = 176
    # her face smeared sideways (she moved)
    rows = (y > 26) & (y < 48) & (np.abs(x - 64) < 16)
    blurred = ndimage.uniform_filter1d(lum, 9, axis=1)
    lum[rows] = blurred[rows]
    # the doll on her lap, sharp: white porcelain face, black eyes, ringlets
    lum[ell(x, y, 64, 76, 6, 8)] = 132  # the doll's dress
    lum[ell(x, y, 64, 63, 6.5, 5.5) & (y < 61)] = 40  # ringlets
    lum[ell(x, y, 58, 66, 1.6, 4)] = 40
    lum[ell(x, y, 70, 66, 1.6, 4)] = 40
    lum[ell(x, y, 64, 64.5, 4.2, 4.8)] = 240  # porcelain face
    for ex in (62.3, 65.7):
        lum[ell(x, y, ex, 64, 0.9, 1.1)] = 14
    lum[(np.abs(x - 64) < 0.8) & (np.abs(y - 67) < 0.5)] = 90
    lum[ell(x, y, 51, 72, 3, 2.2) | ell(x, y, 77, 72, 3, 2.2)] = 178  # her hands around it
    return sepia(lum, 72)


def photo_cama_61():
    """13 August 1961, the basement, a flash in the dark: an iron bed, leather straps, something small strapped under
    a sheet. Scratches on the wall behind."""
    w, h = 160, 120
    r, x, y, lum = photo_base(w, h, 81, 40)
    flash = np.exp(-(((x - 78) / 70) ** 2 + ((y - 64) / 52) ** 2) * 1.4)
    lum = lum * 0.4 + flash * 175
    # scratches on the wall: groups of short strokes
    for g in range(4):
        gx, gy = 26 + g * 34 + r.normal(0, 4), 22 + r.normal(0, 5)
        for k in range(6):
            sx = gx + k * 3.2
            m = (np.abs(x - sx - (y - gy) * 0.25) < 0.45) & (y > gy) & (y < gy + 9 + r.random() * 4)
            lum[m] *= 0.55
    # the bed: head and foot rails, the mattress, the sheet with a small shape, the straps
    for rx_ in (30, 128):
        lum[(np.abs(x - rx_) < 1.5) & (y > 44) & (y < 104)] = 30
        lum[(np.abs(y - 48) < 1.2) & (np.abs(x - rx_) < 10)] = 34
    mat = (x > 30) & (x < 128) & (y > 70) & (y < 84)
    lum[mat] = lum[mat] * 0.5 + 92
    sheet = (x > 40) & (x < 116) & (y > 58 + 6 * np.exp(-((x - 60) / 10) ** 2) * -1) & (y < 74)
    body = ell(x, y, 76, 66, 30, 7) | ell(x, y, 48, 64, 7, 6)
    lum[sheet & body] = 196
    for sx in (56, 80, 102):
        lum[(np.abs(x - sx) < 2.2) & (y > 56) & (y < 86)] = 46
        lum[(np.abs(x - sx) < 1.2) & (np.abs(y - 70) < 1.5)] = 150   # buckles
    lum[(y > 84) & (y < 104) & (x > 31) & (x < 127)] *= 0.25         # under the bed: black
    lum[ell(x, y, 47, 64, 2.2, 2.5)] *= 0.6                          # where the face is, the sheet is wet
    return sepia(lum, 82, scratches=4, tone=(1.0, 0.86, 0.66))


def gui_rosario():
    """The broken rosary up close, on the dark wood of the altar: the loop of beads open where the string was bitten
    through, the frayed ends, the beads that rolled away, the little crucifix."""
    w, h = 192, 144
    r = rng(91)
    x, y = field(w, h)
    grain = smooth_noise(w, h, 12.0, 92)
    plank = np.floor(y / 36.0)
    wood = 46 + 10 * np.sin(x * 0.05 + plank * 2.1 + grain * 5) + 8 * np.sin(x * 0.31 + y * 0.05 + plank) * grain
    wood -= (np.abs((y % 36.0) - 0.5) < 0.8) * 22
    rgb = np.stack([wood * 0.92, wood * 0.6, wood * 0.42], -1)
    vig = 1.0 - 0.75 * (((x - w / 2) / (w / 2)) ** 2 + ((y - h / 2) / (h / 2)) ** 2) / 2
    rgb = rgb * np.clip(vig, 0.2, 1)[..., None]
    im = to_img(rgb, np.full((h, w), 255, np.uint8))
    d = ImageDraw.Draw(im)
    chain = (122, 114, 100, 255)
    pts = []
    for a in np.linspace(-0.5, 4.3, 30):
        pts.append((w * 0.5 + math.cos(a) * 58 + r.normal(0, 1.2), h * 0.44 + math.sin(a) * 40 + r.normal(0, 1.2)))
    d.line(pts, fill=chain, width=1)
    bead = [(20, 12, 10), (52, 32, 24), (88, 58, 42), (150, 116, 86)]
    def b(px, py, rr=4.2):
        d.ellipse((px - rr, py - rr, px + rr, py + rr), fill=bead[1] + (255,), outline=bead[0] + (255,))
        d.ellipse((px - rr * 0.6, py - rr * 0.7, px - rr * 0.05, py - rr * 0.15), fill=bead[2] + (255,))
        d.point((px - rr * 0.45, py - rr * 0.5), fill=bead[3] + (255,))
    for (px, py) in pts[::2]:
        b(px, py)
    # the tail, the crucifix
    tail = [pts[0], (w * 0.66, h * 0.72), (w * 0.64, h * 0.8)]
    d.line(tail, fill=chain, width=1)
    b(w * 0.66, h * 0.72, 3.6)
    cx, cy = w * 0.64, h * 0.82
    metal = (186, 178, 160, 255)
    d.rectangle((cx - 2, cy - 12, cx + 2, cy + 14), fill=metal, outline=(90, 84, 74, 255))
    d.rectangle((cx - 9, cy - 5, cx + 9, cy - 1), fill=metal, outline=(90, 84, 74, 255))
    # the break: two frayed ends, teeth marks (a flattened kink), beads gone from there
    ex, ey = pts[-1]
    for k in range(4):
        d.line((ex, ey, ex + r.normal(4, 2.5), ey + r.normal(3, 2.5)), fill=(150, 138, 116, 255))
    sx, sy = pts[1]
    for k in range(3):
        d.line((sx, sy, sx + r.normal(-4, 2), sy + r.normal(4, 2)), fill=(150, 138, 116, 255))
    for _ in range(6):  # loose beads on the wood
        b(w * (0.12 + r.random() * 0.76), h * (0.74 + r.random() * 0.2), 3.8)
    return im


# ------------------------------------------------------------------ models
def flat_model(group, name):
    tex = f'{NS}:item/{group}/{name}'
    model = {'textures': {'t': tex, 'particle': tex}, 'elements': [{
        'from': [0, 0, 8], 'to': [16, 16, 8], 'shade': False,
        'faces': {'north': {'uv': [0, 0, 16, 16], 'texture': '#t'}, 'south': {'uv': [0, 0, 16, 16], 'texture': '#t'}}}]}
    p = os.path.join(A, 'models/item', group, name + '.json')
    os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump(model, open(p, 'w'), indent=1)
    q = os.path.join(A, 'items', group, name + '.json')
    os.makedirs(os.path.dirname(q), exist_ok=True)
    json.dump({'model': {'type': 'minecraft:model', 'model': f'{NS}:item/{group}/{name}'}}, open(q, 'w'), indent=1)


def item(group, name, img):
    save(img, f'textures/item/{group}/{name}.png')
    flat_model(group, name)
    return img


def build():
    sheet = []
    for i in range(3):
        sheet.append(item('sangre', f'splat_{i}', splat(100 + i * 7)))
    sheet.append(item('sangre', 'charco', pool(130)))
    sheet.append(item('sangre', 'mancha_techo', ceiling_stain(140)))
    sheet.append(item('sangre', 'mano_izq', hand(150, True)))
    sheet.append(item('sangre', 'mano_der', hand(151, False)))
    sheet.append(item('sangre', 'mano_arrastre', hand_drag(152, True)))
    sheet.append(item('sangre', 'pie_izq', foot(160, True)))
    sheet.append(item('sangre', 'pie_der', foot(161, False)))
    sheet.append(item('sangre', 'chorreado_0', runs(170)))
    sheet.append(item('sangre', 'chorreado_1', runs(171)))
    sheet.append(item('sangre', 'banera', tub(180)))
    sheet.append(item('sangre', 'banera_aro', tub(181, ring=True)))
    for i, ch in enumerate('abcdefghijklmnopqrstuvwxyz'):
        sheet.append(item('sangre', f'letra_{ch}', letter(ch, 300 + i)))
    sheet.append(item('sangre', 'letra_a_acento', letter('a', 340, accent=True)))
    sheet.append(item('sangre', 'letra_e_acento', letter('e', 341, accent=True)))
    for i in range(3):
        sheet.append(item('sangre', f'diente_{i}', tooth(i, 200 + i)))
    sheet.append(item('sangre', 'dentadura', denture(210)))
    sheet.append(item('lore', 'cartas', cartas()))
    sheet.append(item('lore', 'rosario_roto', rosario()))
    gui = {'papel': gui_papel(), 'cuaderno': gui_cuaderno(), 'recorte': gui_recorte(), 'misal': gui_misal(), 'dorso': gui_dorso(),
           'foto_nona_cura': photo_nona_cura(), 'foto_nelida': photo_nelida(), 'foto_cama_61': photo_cama_61(),
           'rosario': gui_rosario()}
    for k, img in gui.items():
        save(img, f'textures/gui/lore/{k}.png')
    review(sheet, list(gui.values()))
    print(f'sangre: {len(sheet)} decal/prop textures + models, {len(gui)} lore pages')


def review(decals, pages):
    """A contact sheet on wall-grey and on floor-wood, 4x, in <work>/art/sangre.png."""
    cell = 112
    cols = 10
    rows = (len(decals) + cols - 1) // cols
    W = cols * cell
    H = rows * cell + 300
    out = Image.new('RGBA', (W, H), (60, 58, 56, 255))
    for i, im in enumerate(decals):
        cx, cy = (i % cols) * cell, (i // cols) * cell
        bg = (150, 146, 136, 255) if (i // cols) % 2 == 0 else (92, 64, 44, 255)
        out.paste(Image.new('RGBA', (cell - 4, cell - 4), bg), (cx + 2, cy + 2))
        k = max(1, min((cell - 8) // im.width, (cell - 8) // im.height))
        big = im.resize((im.width * k, im.height * k), Image.NEAREST)
        out.alpha_composite(big, (cx + (cell - big.width) // 2, cy + (cell - big.height) // 2))
    x = 4
    for im in pages:
        k = 280 / im.height
        big = im.resize((int(im.width * k), 280), Image.NEAREST)
        if x + big.width > W:
            break
        out.alpha_composite(big, (x, rows * cell + 10))
        x += big.width + 6
    os.makedirs(os.path.join(WORK, 'art'), exist_ok=True)
    out.save(os.path.join(WORK, 'art', 'sangre.png'))


if __name__ == '__main__':
    build()
