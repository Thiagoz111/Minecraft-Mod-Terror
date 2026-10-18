"""Entity texture materials. Each returns fn(ctx) -> rgba tuple (or None = transparent)."""
import math
from mcmodel import fbm, vnoise, hash3, face_light, pick


def hx(h, a=255):
    h = h.lstrip('#')
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def mix(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(4))


def scale(c, f):
    return (max(0, min(255, int(c[0] * f))), max(0, min(255, int(c[1] * f))), max(0, min(255, int(c[2] * f))), c[3])


def with_alpha(c, a):
    return (c[0], c[1], c[2], a)


def ramp_pick(ramp, v):
    return pick(ramp, v)


def make(ramp, noise=0.18, freq=0.35, seed=0, light=True, grad=None, streak=None, extra=None, alpha=None):
    """Generic painterly material.

    ramp:   list of rgba colours dark->light
    noise:  amount of 3D fbm variation
    grad:   (y_top, y_bottom, amount) darkening toward y_bottom
    streak: (axis_scale_x, axis_scale_y) stretched noise for fibres/hair/folds
    extra:  fn(ctx, v)->v hook
    alpha:  fn(ctx)->alpha or None
    """
    def f(ctx):
        x, y, z = ctx.pos
        v = 0.55
        if streak:
            sx, sy = streak
            v += (fbm(x * sx, y * sy, z * sx, 3, seed) - 0.5) * noise * 2
        else:
            v += (fbm(x * freq, y * freq, z * freq, 3, seed) - 0.5) * noise * 2
        if light:
            v += face_light(ctx)
        if grad:
            y0, y1, amt = grad
            t = (y - y0) / (y1 - y0)
            v -= max(0, min(1, t)) * amt
        if extra:
            v = extra(ctx, v)
        if v is None:
            return None
        c = pick(ramp, v)
        if alpha:
            a = alpha(ctx)
            if a is None or a <= 0:
                return None
            c = with_alpha(c, a)
        return c
    return f


def solid(c):
    return lambda ctx: c


# ---------------------------------------------------------------- palettes
DEAD_SKIN = [hx('#1d2027'), hx('#363b46'), hx('#535a68'), hx('#737b88'), hx('#959ca6'), hx('#b8bcc2'), hx('#d6d8da')]
PALE_SKIN = [hx('#3a2a2c'), hx('#5c4446'), hx('#86696a'), hx('#ad9190'), hx('#cdb4ae'), hx('#e6d4cc'), hx('#f6ebe5')]
GRAY_SKIN = [hx('#16161a'), hx('#25252b'), hx('#393940'), hx('#4f4f57'), hx('#68676f'), hx('#84838a')]
WHITE_DRESS = [hx('#2b2c33'), hx('#4a4c55'), hx('#6f727c'), hx('#959aa3'), hx('#b9bdc4'), hx('#d8dbe0'), hx('#eef0f2')]
BLACK_HAIR = [hx('#050507'), hx('#0b0b10'), hx('#13141b'), hx('#1c1e28'), hx('#2a2d3b'), hx('#3f4458')]
MUD = [hx('#1d150e'), hx('#2f2317'), hx('#463423'), hx('#5c4630')]
BONE = [hx('#2e271d'), hx('#4d4333'), hx('#71654f'), hx('#988a6e'), hx('#bcae90'), hx('#d9cfb4'), hx('#efe8d6')]
DARK_FUR = [hx('#0a0807'), hx('#15100d'), hx('#211913'), hx('#2f241b'), hx('#3e3024'), hx('#4f3e2f')]
ROTTEN_SKIN = [hx('#16130f'), hx('#262019'), hx('#3a3126'), hx('#4f4535'), hx('#665a45'), hx('#807155')]
NIGHTGOWN = [hx('#2f2a2a'), hx('#4f4847'), hx('#776d6a'), hx('#9e938d'), hx('#c2b7ae'), hx('#ddd3c8'), hx('#efe7dc')]
BROWN_HAIR = [hx('#0d0806'), hx('#1a100b'), hx('#2b1b12'), hx('#3d281b'), hx('#523727'), hx('#6a4834')]
CLOWN_WHITE = [hx('#4d4a4e'), hx('#7a777c'), hx('#a3a0a5'), hx('#c8c5c8'), hx('#e3e0df'), hx('#f6f4f0')]
CLOWN_RED = [hx('#2a0306'), hx('#4a070d'), hx('#740d16'), hx('#9f1720'), hx('#c42730'), hx('#e2463f')]
CLOWN_SUIT = [hx('#1a1018'), hx('#2e1b2b'), hx('#472a42'), hx('#623a5b'), hx('#7d4c75'), hx('#986090')]
YELLOW_CLOTH = [hx('#2e2306'), hx('#4f3c0b'), hx('#7a5d12'), hx('#a37d1c'), hx('#c99d2c'), hx('#e6bf4a')]
NUN_BLACK = [hx('#040406'), hx('#09090d'), hx('#101118'), hx('#181a24'), hx('#222533'), hx('#2f3345')]
NUN_WHITE = [hx('#3d3f46'), hx('#62656e'), hx('#8d9099'), hx('#b3b6be'), hx('#d4d6dc'), hx('#eeeff2')]
SHADOW = [hx('#000000'), hx('#030305'), hx('#07070b'), hx('#0c0c12'), hx('#12121a'), hx('#191924')]
PORCELAIN = [hx('#4a4448'), hx('#72696d'), hx('#9b9094'), hx('#c2b8b9'), hx('#ddd5d3'), hx('#f2ece8'), hx('#ffffff')]
DOLL_DRESS = [hx('#1a0a14'), hx('#2e1224'), hx('#4a1c38'), hx('#66284c'), hx('#823660'), hx('#a04c78')]
SPIRIT = [hx('#0a3a44'), hx('#12626a'), hx('#1f8e8e'), hx('#3fbcb0'), hx('#7de6d2'), hx('#c4fff0')]
BLOOD = [hx('#1f0204'), hx('#3d0508'), hx('#5e090e'), hx('#7e0f14')]
