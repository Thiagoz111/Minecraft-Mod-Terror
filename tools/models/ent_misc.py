"""Hombre Sombra (Hat Man), Munieca Maldita (cursed doll), Anima (wandering soul)."""
import math
from mcmodel import Model, fbm, vnoise, hash3, face_light, pick
from rig import Rig
from emat import *


# ------------------------------------------------------------------ Hombre Sombra
SHADE = [hx('#000000', 235), hx('#040407', 235), hx('#08080d', 235), hx('#0d0d14', 235), hx('#13131c', 235), hx('#1b1b27', 235)]


def shadow_mat(ctx):
    x, y, z = ctx.pos
    if ctx.face == 'bottom' and ctx.bone.name == 'coat':
        return None
    v = 0.45 + face_light(ctx) * 0.6 + (fbm(x * 0.25, y * 0.15, z * 0.25, 3, 3) - 0.5) * 0.35
    c = pick(SHADE, v)
    # smoky dissolving edges toward the bottom of the coat and the hands
    n = fbm(x * 0.5, y * 0.5, z * 0.5, 2, 5)
    if ctx.bone.name == 'coat' and y > 14 + n * 9:
        return None
    if ctx.bone.name == 'coat' and y > 10:
        return (c[0], c[1], c[2], int(235 - (y - 10) * 9))
    return c


def shadow_eyes(img, u0, v0, w, h):
    px = img.load()
    px[u0 + 2, v0 + 3] = (190, 10, 14, 255)
    px[u0 + w - 3, v0 + 3] = (190, 10, 14, 255)


def shadow_eyes_glow(img, u0, v0, w, h):
    px = img.load()
    px[u0 + 2, v0 + 3] = (255, 40, 40, 255)
    px[u0 + w - 3, v0 + 3] = (255, 40, 40, 255)


def build_sombra():
    r = Rig()
    r.bone('body', (0, -12, 0), mat=shadow_mat)
    r.box('body', (-3.5, -12, -1.5), (7, 14, 3))
    r.bone('coat', (0, 2, 0), parent='body', mat=shadow_mat)
    r.box('coat', (-4, 2, -2), (8, 22, 4))
    r.bone('head', (0, -12, 0), parent='body', mat=shadow_mat)
    r.box('head', (-3, -19, -3), (6, 7, 6), decals={'front': shadow_eyes, 'eyes:front': shadow_eyes_glow})
    r.bone('hat', (0, -19, 0), parent='head', mat=shadow_mat, rot=(-6, 0, 0))
    r.box('hat', (-6.5, -20, -6.5), (13, 1, 13))
    r.box('hat', (-3.5, -24, -3.5), (7, 4, 7))
    for side, sx in (('right', -1), ('left', 1)):
        x0 = -5.5 if sx < 0 else 3.5
        r.bone(f'{side}_arm', (4.5 * sx, -11, 0), parent='body', mat=shadow_mat, rot=(0, 0, 3 * sx))
        r.box(f'{side}_arm', (x0, -12, -1), (2, 26, 2))
        r.box(f'{side}_arm', (x0, 14, -1), (1, 5, 1))
        r.box(f'{side}_arm', (x0 + 1, 14, 0), (1, 6, 1))
    m = Model('sombra', 64, 64, r.roots)
    m.render_type = 'entityTranslucent'
    return m


# ------------------------------------------------------------------ Munieca Maldita
DOLL_HAIR = [hx('#0e0806'), hx('#1c110b'), hx('#2e1d12'), hx('#432b1b'), hx('#5a3b25'), hx('#734e31')]


def porcelain(ctx):
    x, y, z = ctx.pos
    v = 0.62 + face_light(ctx) * 1.2 + (fbm(x * 0.7, y * 0.7, z * 0.7, 2, 3) - 0.5) * 0.12
    c = pick(PORCELAIN, v)
    crack = abs(fbm(x * 0.9, y * 0.9, z * 0.9, 3, 7) - 0.5)
    if crack < 0.03:
        c = (52, 44, 48, 255)
    return c


def doll_dress(ctx):
    x, y, z = ctx.pos
    if ctx.face == 'bottom' and ctx.bone.name == 'skirt':
        return None
    v = 0.58 + face_light(ctx) + (fbm(x * 0.5, y * 0.5, z * 0.5, 2, 9) - 0.5) * 0.25
    c = pick(DOLL_DRESS, v)
    if ctx.bone.name == 'skirt' and y > 21.5:
        c = pick(CLOTH_LACE, 0.5 + face_light(ctx))  # lace hem
    return c


CLOTH_LACE = [hx('#5b5560'), hx('#8b8590'), hx('#b5b0b8'), hx('#dcd8dc'), hx('#f3f0f2')]


def doll_hair(ctx):
    x, y, z = ctx.pos
    if ctx.face == 'bottom':
        return None
    if ctx.face == 'front' and ctx.bone.name == 'head' and ctx.j >= 2 and 1 <= ctx.i <= ctx.w - 2:
        return None
    s = hash3(math.floor((x if ctx.face in ('front', 'back', 'top') else z) * 1.5), 0, 0, 11)
    v = 0.35 + s * 0.4 + face_light(ctx) * 0.5
    return pick(DOLL_HAIR, v)


def bow_mat(ctx):
    return pick([hx('#2a0306'), hx('#4f070c'), hx('#7d0d14'), hx('#a8161d'), hx('#cc2a2a')], 0.55 + face_light(ctx) * 1.3)


DOLL_FACE = [
    "SSSSS",
    "KwSKw",
    "KKSKK",
    "rSSSr",
    "SmmmS",
]


def doll_face(img, u0, v0, w, h):
    px = img.load()
    pal = {'K': (6, 4, 6, 255), 'w': (240, 240, 240, 255), 'r': (226, 140, 146, 255), 'm': (120, 16, 30, 255)}
    for j, row in enumerate(DOLL_FACE):
        for i, ch in enumerate(row):
            if ch in pal and i < w and j < h:
                px[u0 + i, v0 + j] = pal[ch]
    px[u0 + 0, v0 + 3] = (120, 6, 14, 255)  # blood tear
    px[u0 + 0, v0 + 4] = (90, 4, 10, 255)


def build_muneca():
    r = Rig()
    r.bone('body', (0, 17, 0), mat=doll_dress)
    r.box('body', (-2, 13, -1), (4, 5, 2))
    r.bone('skirt', (0, 18, 0), parent='body', mat=doll_dress)
    r.box('skirt', (-3, 17, -2), (6, 4, 4))
    r.bone('head', (0, 13, 0), parent='body', mat=porcelain)
    r.box('head', (-2.5, 8, -2.5), (5, 5, 5), decals={'front': doll_face})
    r.box('head', (-2.5, 8, -2.5), (5, 5, 5), mat=doll_hair, inflate=0.3)
    r.box('head', (-3, 8.5, 1.5), (6, 8, 1), mat=doll_hair)
    r.box('head', (1.5, 7, -1), (3, 2, 1), mat=bow_mat)
    for side, sx in (('right', -1), ('left', 1)):
        x0 = -3 if sx < 0 else 2
        r.bone(f'{side}_arm', (2.5 * sx, 13.5, 0), parent='body', mat=porcelain, rot=(0, 0, 10 * sx))
        r.box(f'{side}_arm', (x0, 13, -0.5), (1, 5, 1))
        r.bone(f'{side}_leg', (1 * sx, 21, 0), mat=porcelain)
        r.box(f'{side}_leg', (1 * sx - 0.5, 20, -0.5), (1, 4, 1))
    m = Model('muneca', 64, 32, r.roots)
    return m


# ------------------------------------------------------------------ Anima
def spirit_mat(ctx):
    x, y, z = ctx.pos
    if ctx.face == 'bottom' and ctx.bone.name in ('tail1', 'tail2', 'tail3'):
        return None
    v = 0.55 + face_light(ctx) * 0.8 + (fbm(x * 0.3, y * 0.2, z * 0.3, 3, 3) - 0.5) * 0.4
    c = pick(SPIRIT, v)
    a = 170
    if ctx.bone.name.startswith('tail'):
        n = fbm(x * 0.6, y * 0.3, z * 0.6, 2, 7)
        a = int(170 - (y - 8) * 7 - n * 50)
        if a < 30:
            return None
    return (c[0], c[1], c[2], max(30, min(200, a)))


ANIMA_FACE = ["SSSSSS", "SKSSKS", "SKSSKS", "SSSSSS", "SSKKSS", "SSKKSS"]


def anima_face(img, u0, v0, w, h):
    px = img.load()
    for j, row in enumerate(ANIMA_FACE):
        for i, ch in enumerate(row):
            if ch == 'K' and i < w and j < h:
                px[u0 + i, v0 + j] = (4, 30, 38, 230)


def build_anima():
    r = Rig()
    r.bone('body', (0, 0, 0), mat=spirit_mat)
    r.box('body', (-3, 0, -1.5), (6, 8, 3))
    r.bone('head', (0, 0, 0), parent='body', mat=spirit_mat)
    r.box('head', (-3, -6, -3), (6, 6, 6), decals={'front': anima_face})
    r.bone('tail1', (0, 8, 0), parent='body', mat=spirit_mat)
    r.box('tail1', (-2.5, 8, -1.5), (5, 5, 3))
    r.bone('tail2', (0, 13, 0), parent='tail1', mat=spirit_mat)
    r.box('tail2', (-2, 13, -1), (4, 5, 2))
    r.bone('tail3', (0, 18, 0), parent='tail2', mat=spirit_mat)
    r.box('tail3', (-1, 18, -0.5), (2, 5, 1))
    for side, sx in (('right', -1), ('left', 1)):
        x0 = -5 if sx < 0 else 3
        r.bone(f'{side}_arm', (4 * sx, 1, 0), parent='body', mat=spirit_mat, rot=(-30, 0, 20 * sx))
        r.box(f'{side}_arm', (x0, 0, -1), (2, 9, 2))
    m = Model('anima', 64, 32, r.roots)
    m.render_type = 'entityTranslucentEmissive'
    return m
