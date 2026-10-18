"""Pixel-art engine for DEAD LINE textures.

Shapes are rasterised into a G-buffer (material, normal, depth). A lighting pass
quantises shading into hand-tuned, hue-shifted material ramps, then outlines and
hand-placed detail pixels are layered on top. Everything is deterministic (seeded).
"""
import colorsys
import math
import numpy as np
from PIL import Image
from scipy import ndimage

LIGHT = np.array([-0.55, -0.70, 0.75])
LIGHT = LIGHT / np.linalg.norm(LIGHT)
HALF = LIGHT + np.array([0, 0, 1.0])
HALF = HALF / np.linalg.norm(HALF)


def hexc(h, a=255):
    h = h.lstrip('#')
    if len(h) == 8:
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4, 6))
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (a,)


def ramp(base, n=7, spread=0.55, hue_shift=0.06, sat_boost=0.15, alpha=255):
    """Hue-shifted ramp: shadows drift to cool/purple, lights to warm/yellow."""
    r, g, b = [c / 255 for c in hexc(base)[:3]]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    out = []
    for i in range(n):
        t = i / (n - 1) * 2 - 1  # -1..1
        hh = (h - hue_shift * t) % 1.0 if h > 0.05 or s > 0.08 else h
        # warm highlight hue goes toward yellow (1/6), shadow toward blue/purple (0.7)
        if s > 0.08:
            target = 1 / 6 if t > 0 else 0.72
            hh = h + (((target - h + 0.5) % 1.0) - 0.5) * abs(t) * hue_shift * 3
            hh %= 1.0
        ll = min(0.97, max(0.03, l + t * spread * (0.5 if t > 0 else 0.6)))
        ss = min(1, max(0, s * (1 + sat_boost * (-abs(t) + 0.5))))
        rr, gg, bb = colorsys.hls_to_rgb(hh, ll, ss)
        out.append((int(rr * 255), int(gg * 255), int(bb * 255), alpha))
    return out


def lerp(c1, c2, t):
    return tuple(int(round(c1[i] + (c2[i] - c1[i]) * t)) for i in range(4))


def shade(c, f):
    """Multiply rgb by f (>1 lightens toward white)."""
    if f >= 1:
        return lerp(c, (255, 255, 255, c[3]), min(1, f - 1))
    return (int(c[0] * f), int(c[1] * f), int(c[2] * f), c[3])


class Material:
    def __init__(self, colors, spec=0.0, shininess=12, outline=None, ambient=0.32, emissive=False, base=0.5, contrast=1.0):
        if isinstance(colors, list):
            self.colors = [hexc(c) if isinstance(c, str) else (tuple(c) if len(c) == 4 else tuple(c) + (255,)) for c in colors]
        else:
            self.colors = ramp(colors)
        if outline is not None and isinstance(outline, str):
            outline = hexc(outline)
        self.spec = spec
        self.shininess = shininess
        self.outline = outline or shade(self.colors[0], 0.55)
        self.ambient = ambient
        self.emissive = emissive
        self.base = base
        self.contrast = contrast


BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0


class Sprite:
    def __init__(self, w, h=None, seed=1):
        h = h or w
        self.w, self.h = w, h
        self.mat = np.full((h, w), -1, int)
        self.nrm = np.zeros((h, w, 3))
        self.nrm[..., 2] = 1
        self.extra = np.zeros((h, w))  # per-pixel brightness offset (texture noise)
        self.mats = []
        self.overlay = {}  # (x,y) -> rgba painted after lighting
        self.rng = np.random.default_rng(seed)
        self.no_outline = np.zeros((h, w), bool)
        self.dither = np.zeros((h, w), bool)

    # ---------- material registry ----------
    def m(self, mat):
        if mat not in self.mats:
            self.mats.append(mat)
        return self.mats.index(mat)

    # ---------- raster primitives ----------
    def _grid(self):
        ys, xs = np.mgrid[0:self.h, 0:self.w]
        return xs + 0.5, ys + 0.5

    def _apply(self, mask, mat, bevel=1.5, dome=False, height=None, noise=0.0, tilt=(0, 0), dither=False, outline=True):
        mid = self.m(mat)
        if not mask.any():
            return mask
        if height is None:
            dist = ndimage.distance_transform_edt(np.pad(mask, 1))[1:-1, 1:-1]
            if dome:
                mx = max(dist.max(), 1)
                hgt = np.sqrt(np.clip(1 - (1 - dist / mx) ** 2, 0, 1)) * mx
            else:
                hgt = np.clip(dist / max(bevel, 0.01), 0, 1) * bevel
        else:
            hgt = height
        gy, gx = np.gradient(hgt)
        n = np.dstack([-gx + tilt[0], -gy + tilt[1], np.ones_like(hgt) * 0.9])
        n /= np.linalg.norm(n, axis=2, keepdims=True)
        self.mat[mask] = mid
        self.nrm[mask] = n[mask]
        if noise:
            self.extra[mask] = self.rng.normal(0, noise, mask.sum())
        else:
            self.extra[mask] = 0
        self.no_outline[mask] = not outline
        self.dither[mask] = dither
        return mask

    def mask_rect(self, x0, y0, x1, y1):
        xs, ys = self._grid()
        return (xs >= x0) & (xs <= x1 + 1) & (ys >= y0) & (ys <= y1 + 1)

    def rect(self, x0, y0, x1, y1, mat, **kw):
        return self._apply(self.mask_rect(x0, y0, x1, y1), mat, **kw)

    def mask_ellipse(self, cx, cy, rx, ry):
        xs, ys = self._grid()
        return ((xs - cx) / rx) ** 2 + ((ys - cy) / ry) ** 2 <= 1.0

    def ellipse(self, cx, cy, rx, ry, mat, dome=True, **kw):
        return self._apply(self.mask_ellipse(cx, cy, rx, ry), mat, dome=dome, **kw)

    def mask_poly(self, pts):
        xs, ys = self._grid()
        inside = np.zeros(xs.shape, bool)
        n = len(pts)
        for i in range(n):
            x0, y0 = pts[i]
            x1, y1 = pts[(i + 1) % n]
            if y0 == y1:
                continue
            cond = ((y0 > ys) != (y1 > ys))
            xint = x0 + (ys - y0) * (x1 - x0) / (y1 - y0)
            inside ^= cond & (xs < xint)
        return inside

    def poly(self, pts, mat, **kw):
        return self._apply(self.mask_poly(pts), mat, **kw)

    def mask_capsule(self, x0, y0, x1, y1, r):
        xs, ys = self._grid()
        dx, dy = x1 - x0, y1 - y0
        L2 = dx * dx + dy * dy or 1e-9
        t = np.clip(((xs - x0) * dx + (ys - y0) * dy) / L2, 0, 1)
        px, py = x0 + t * dx, y0 + t * dy
        return (xs - px) ** 2 + (ys - py) ** 2 <= r * r

    def capsule(self, x0, y0, x1, y1, r, mat, dome=True, **kw):
        return self._apply(self.mask_capsule(x0, y0, x1, y1, r), mat, dome=dome, **kw)

    def cylinder(self, x0, y0, x1, y1, r, mat, **kw):
        """Capsule shaded as a cylinder across its axis (for handles/tubes)."""
        mask = self.mask_capsule(x0, y0, x1, y1, r)
        xs, ys = self._grid()
        dx, dy = x1 - x0, y1 - y0
        L = math.hypot(dx, dy) or 1e-9
        nx, ny = -dy / L, dx / L
        d = ((xs - x0) * nx + (ys - y0) * ny) / max(r, 0.5)
        d = np.clip(d, -1, 1)
        hgt = np.sqrt(1 - d ** 2) * r * 0.55
        return self._apply(mask, mat, height=hgt, **kw)

    # ---------- direct painting (post-lighting overlay) ----------
    def put(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.overlay[(int(x), int(y))] = c if len(c) == 4 else tuple(c) + (255,)

    def puts(self, pts, c):
        for x, y in pts:
            self.put(x, y, c)

    def pattern(self, x0, y0, rows, pal):
        """Paint ASCII pixel art. pal maps char -> rgba (or None for skip)."""
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                c = pal.get(ch)
                if c is not None:
                    self.put(x0 + i, y0 + j, c)

    def line(self, x0, y0, x1, y1, c):
        n = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
        for i in range(n):
            t = i / max(n - 1, 1)
            self.put(round(x0 + (x1 - x0) * t), round(y0 + (y1 - y0) * t), c)

    def erase(self, mask):
        self.mat[mask] = -1

    # ---------- render ----------
    def render(self, outline=True, outline_color=None, light=None):
        L = LIGHT if light is None else np.array(light) / np.linalg.norm(light)
        H = L + np.array([0, 0, 1.0]); H /= np.linalg.norm(H)
        img = np.zeros((self.h, self.w, 4), np.uint8)
        for mid, mat in enumerate(self.mats):
            mask = self.mat == mid
            if not mask.any():
                continue
            n = self.nrm[mask]
            d = n @ L - L[2]
            sp = np.clip((n @ H - H[2]) / (1 - H[2]), 0, 1) ** max(1, mat.shininess / 4) * mat.spec
            if mat.emissive:
                inten = mat.base + d * 1.2 * mat.contrast + self.extra[mask]
            else:
                inten = mat.base + d * 1.7 * mat.contrast + sp + self.extra[mask]
            k = len(mat.colors)
            ys, xs = np.nonzero(mask)
            dith = self.dither[mask]
            v = inten * (k - 1)
            v = np.where(dith, v + (BAYER[ys % 4, xs % 4] - 0.5) * 0.9, v)
            idx = np.clip(np.round(v), 0, k - 1).astype(int)
            cols = np.array(mat.colors, np.uint8)
            img[ys, xs] = cols[idx]
        if outline:
            solid = self.mat >= 0
            out = np.zeros_like(solid)
            src_mat = np.full(self.mat.shape, -1)
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                sh = np.roll(np.roll(solid & ~self.no_outline, dy, 0), dx, 1)
                shm = np.roll(np.roll(self.mat, dy, 0), dx, 1)
                # avoid wrap-around
                if dx == 1: sh[:, 0] = False
                if dx == -1: sh[:, -1] = False
                if dy == 1: sh[0, :] = False
                if dy == -1: sh[-1, :] = False
                new = sh & ~solid & ~out
                src_mat[new] = shm[new]
                out |= new
            ys, xs = np.nonzero(out)
            for y, x in zip(ys, xs):
                if outline_color:
                    img[y, x] = outline_color
                else:
                    img[y, x] = self.mats[src_mat[y, x]].outline
        for (x, y), c in self.overlay.items():
            if c[3] == 0:
                img[y, x] = (0, 0, 0, 0)
            elif c[3] < 255 and img[y, x, 3] > 0:
                a = c[3] / 255
                img[y, x, :3] = (np.array(c[:3]) * a + img[y, x, :3] * (1 - a)).astype(np.uint8)
            else:
                img[y, x] = c
        return Image.fromarray(img, 'RGBA').copy()


def glow(img, color, radius=2, strength=0.6):
    """Soft additive halo around bright pixels -- for emissive items (stays pixel-crisp)."""
    a = np.array(img).astype(float)
    mask = (a[..., 3] > 0).astype(float)
    blur = ndimage.gaussian_filter(mask, radius)
    halo = np.clip(blur * strength * 2, 0, 1) * (1 - mask)
    q = np.round(halo * 3) / 3 * 0.75
    c = np.array(color[:3], float)
    out = a.copy()
    sel = q > 0
    out[sel, :3] = c
    out[sel, 3] = q[sel] * 255
    return Image.fromarray(out.astype(np.uint8), 'RGBA').copy()


def upscale(img, k):
    return img.resize((img.width * k, img.height * k), Image.NEAREST)


def sheet(images, k=10, cols=6, bg=(24, 22, 28), pad=6, labels=None):
    from PIL import ImageDraw
    cw = max(i.width for i in images) * k + pad * 2
    ch = max(i.height for i in images) * k + pad * 2 + (14 if labels else 0)
    rows = math.ceil(len(images) / cols)
    out = Image.new('RGBA', (cw * cols, ch * rows), bg + (255,))
    d = ImageDraw.Draw(out)
    for i, im in enumerate(images):
        x, y = (i % cols) * cw, (i // cols) * ch
        # checker to show transparency
        for cy in range(0, im.height * k, k * 2):
            for cx in range(0, im.width * k, k * 2):
                d.rectangle([x + pad + cx, y + pad + cy, x + pad + cx + k - 1, y + pad + cy + k - 1], fill=(32, 30, 38))
        out.alpha_composite(upscale(im, k), (x + pad, y + pad))
        if labels:
            d.text((x + pad, y + ch - 14), labels[i], fill=(200, 200, 200))
    return out
