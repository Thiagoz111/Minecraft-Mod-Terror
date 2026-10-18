"""Texture painting helpers for entity models (import freely in ent_*.py files).

Materials are functions ctx -> (r, g, b, a) or None (transparent). See mcmodel.Ctx:
  ctx.pos (x, y, z) model-space texel centre (rest pose), ctx.n world normal, ctx.face in
  {'front','back','west','east','top','bottom'}, ctx.i/ctx.j texel index in the face, ctx.w/ctx.h face size,
  ctx.s/ctx.t normalised 0..1 coordinates, ctx.cube, ctx.bone (ctx.bone.name), ctx.rng.
Decals are functions (img, u0, v0, w, h) painting straight into the PIL image over a face rect.
"""
import colorsys
import math

from mcmodel import fbm, vnoise, hash3, face_light, pick  # re-exported

BAYER4 = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]


def hx(h, a=255):
    h = h.lstrip('#')
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def mix(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(4))


def scale(c, f):
    return (max(0, min(255, int(c[0] * f))), max(0, min(255, int(c[1] * f))), max(0, min(255, int(c[2] * f))), c[3])


def alpha(c, a):
    return (c[0], c[1], c[2], int(a))


def ramp(base, n=8, spread=0.62, hue_shift=0.05, alpha_=255):
    """Hue-shifted ramp from dark to light around a base colour (shadows cool/purple, lights warm)."""
    r, g, b = [c / 255 for c in hx(base)[:3]]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    out = []
    for i in range(n):
        t = i / (n - 1) * 2 - 1
        hh = h
        if s > 0.06:
            target = 1 / 6 if t > 0 else 0.72
            hh = (h + (((target - h + 0.5) % 1.0) - 0.5) * abs(t) * hue_shift * 3) % 1.0
        ll = min(0.97, max(0.02, l + t * spread * (0.5 if t > 0 else 0.62)))
        ss = min(1, max(0, s * (1 + 0.12 * (0.5 - abs(t)))))
        rr, gg, bb = colorsys.hls_to_rgb(hh, ll, ss)
        out.append((int(rr * 255), int(gg * 255), int(bb * 255), alpha_))
    return out


def dither(ctx, v, amount=0.06):
    """Ordered dither added to a 0..1 value for smoother ramps (keeps pixel-art crispness)."""
    return v + (BAYER4[ctx.j % 4][ctx.i % 4] / 16.0 - 0.5) * amount


def edge(ctx):
    """Texel distance to the nearest edge of its face (0 at the border)."""
    return min(ctx.i, ctx.j, ctx.w - 1 - ctx.i, ctx.h - 1 - ctx.j)


def edge_dark(ctx, v, amount=0.08, width=1):
    """Darken the border texels of a face: gives cubes crisp definition like vanilla mobs."""
    e = edge(ctx)
    return v - amount if e < width else v


def lit(ctx, v, strength=1.0):
    """Baked directional light (tops brighter, undersides darker)."""
    return v + face_light(ctx) * strength


def pixelart(rows, palette, anchor='center', dx=0, dy=0, flip=False):
    """Decal from ASCII art. palette: char -> rgba; chars not in palette are skipped (left untouched).

    anchor: 'center' | 'top' | 'bottom' | 'topleft'. Returns fn(img, u0, v0, w, h)."""
    rh = len(rows)
    rw = max(len(r) for r in rows)

    def fn(img, u0, v0, w, h):
        px = img.load()
        if anchor == 'topleft':
            ox, oy = 0, 0
        elif anchor == 'top':
            ox, oy = (w - rw) // 2, 0
        elif anchor == 'bottom':
            ox, oy = (w - rw) // 2, h - rh
        else:
            ox, oy = (w - rw) // 2, (h - rh) // 2
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                c = palette.get(ch)
                if c is None:
                    continue
                ii = (rw - 1 - i) if flip else i
                x, y = u0 + ox + dx + ii, v0 + oy + dy + j
                if u0 <= x < u0 + w and v0 <= y < v0 + h:
                    if callable(c):
                        c = c(px[x, y])
                    px[x, y] = c
    return fn


def darken(f):
    """Palette entry that multiplies the existing texel instead of replacing it."""
    return lambda old: scale(old, f)


def tint(color, t):
    """Palette entry that blends the existing texel toward a colour."""
    return lambda old: mix(old, color, t)


def chain(*fns):
    """Combine several decal functions on one face."""
    def fn(img, u0, v0, w, h):
        for f in fns:
            f(img, u0, v0, w, h)
    return fn
