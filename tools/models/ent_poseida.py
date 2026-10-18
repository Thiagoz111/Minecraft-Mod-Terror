"""La Poseida (Lucia) -- the possessed girl of Casa Morales. Rig supports spider-walk."""
import math
from mcmodel import Model, fbm, vnoise, hash3, face_light, pick
from rig import Rig
from emat import *

GIRL_SKIN = [hx('#1e1a1d'), hx('#352f33'), hx('#51494c'), hx('#706466'), hx('#8f8283'), hx('#ada0a0'), hx('#c9bdbb')]


def ucoord(ctx):
    x, y, z = ctx.pos
    return x if ctx.face in ('front', 'back', 'top', 'bottom') else z + 30


def gown_mat(ctx):
    x, y, z = ctx.pos
    if ctx.face == 'bottom' and ctx.bone.name == 'gown':
        return None
    v = 0.6 + face_light(ctx)
    u = ucoord(ctx)
    k = (u * 0.7 + vnoise(u * 0.4, y * 0.1, 0, 3) * 1.2) % 2.4
    if k < 0.5:
        v -= 0.15
    v += (fbm(x * 0.2, y * 0.2, z * 0.2, 2, 5) - 0.5) * 0.22
    c = pick(NIGHTGOWN, v)
    # vomit / blood stains down the front
    st = fbm(x * 0.35, y * 0.12, z * 0.35, 2, 9)
    if ctx.face == 'front' and st > 0.62 and y < 8:
        c = mix(c, (88, 14, 18, 255), 0.7)
    elif st > 0.7:
        c = mix(c, (92, 84, 52, 255), 0.4)
    if ctx.bone.name == 'gown':
        col = hash3(math.floor(u), 0, 1, 7)
        if y > 13.5 + col * 2.2:
            return None
    # lace trim at the collar
    if ctx.bone.name == 'body' and y < 1 and ctx.face in ('front', 'back') and int(x * 2) % 2 == 0:
        c = pick(NIGHTGOWN, 0.85)
    return c


def skin_mat(ctx):
    x, y, z = ctx.pos
    v = 0.6 + face_light(ctx) + (fbm(x * 0.3, y * 0.3, z * 0.3, 2, 11) - 0.5) * 0.2
    c = pick(GIRL_SKIN, v)
    vein = abs(fbm(x * 0.55, y * 0.25, z * 0.55, 3, 13) - 0.5)
    if vein < 0.022:
        c = mix(c, (30, 18, 40, 255), 0.65)  # black, spidery veins
    if fbm(x * 0.4, y * 0.4, z * 0.4, 2, 17) > 0.72:
        c = mix(c, (70, 40, 60, 255), 0.4)  # bruises
    return c


def hair_mat(alpha=None):
    def f(ctx):
        x, y, z = ctx.pos
        if alpha and not alpha(ctx):
            return None
        u = ucoord(ctx)
        s = hash3(math.floor(u * 1.2), 0, 0, 21)
        v = 0.3 + s * 0.45 + face_light(ctx) * 0.5 + (vnoise(u, y * 0.2, 0, 22) - 0.5) * 0.25
        return pick(BROWN_HAIR, v)
    return f


def shell_alpha(ctx):
    if ctx.face == 'bottom':
        return False
    if ctx.face == 'front':
        return ctx.j == 0 or (ctx.j <= 2 and (ctx.i <= 1 or ctx.i >= ctx.w - 2)) or ctx.i == 0 or ctx.i == ctx.w - 1
    return True


def back_hair_alpha(ctx):
    col = hash3(math.floor(ctx.pos[0] * 1.3), 0, 0, 25)
    return ctx.pos[1] < 3 + col * 6


def front_strand_alpha(ctx):
    col = hash3(math.floor(ctx.pos[0] * 1.5), 0, 0, 27)
    return ctx.pos[1] < -7 + col * 5


FACE = [
    "SSSSSSS",
    "SdSSSdS",
    "dWWSWWd",
    "dWWdWWd",
    "SdSSSdS",
    "SScccSS",
    "SckkkcS",
]


def face_decal(img, u0, v0, w, h):
    px = img.load()
    pal = {'d': (40, 22, 34, 255), 'W': (232, 236, 214, 255), 'c': (60, 16, 24, 255), 'k': (8, 3, 4, 255)}
    for j, row in enumerate(FACE):
        for i, ch in enumerate(row):
            if ch in pal:
                px[u0 + i, v0 + j] = pal[ch]
    # cracked lips glint + teeth
    px[u0 + 3, v0 + 6] = (210, 196, 160, 255)


def eyes_only(img, u0, v0, w, h):
    """Emissive layer: just the eyes."""
    px = img.load()
    for j, row in enumerate(FACE):
        for i, ch in enumerate(row):
            if ch == 'W':
                px[u0 + i, v0 + j] = (255, 250, 200, 255)


def build():
    r = Rig()
    skin = skin_mat
    r.bone('root', (0, 12, 0))
    r.bone('body', (0, 12, 0), parent='root', mat=gown_mat)
    r.box('body', (-3, 0, -1.5), (6, 9, 3))
    r.bone('gown', (0, 9, 0), parent='body', mat=gown_mat)
    r.box('gown', (-3.5, 8, -2), (7, 7, 4))
    r.bone('head', (0, 0, 0), parent='body', mat=skin)
    r.box('head', (-3.5, -7, -3.5), (7, 7, 7), decals={'front': face_decal, 'eyes:front': eyes_only})
    if True:
        r.box('head', (-3.5, -7, -3.5), (7, 7, 7), mat=hair_mat(shell_alpha), inflate=0.35)
        r.bone('hair_back', (0, -5, 3.8), parent='head', mat=hair_mat(back_hair_alpha))
        r.box('hair_back', (-4, -6, 3.8), (8, 16, 1))
        r.bone('hair_front', (0, -7, -3.9), parent='head', mat=hair_mat(front_strand_alpha))
        r.box('hair_front', (-3.8, -7.2, -3.95), (2, 7, 0))
        r.box('hair_front', (2, -7.2, -3.95), (2, 6, 0))
    for side, sx in (('right', -1), ('left', 1)):
        x0 = -5 if sx < 0 else 3
        r.bone(f'{side}_arm', (4 * sx, 1, 0), parent='body', mat=skin)
        r.box(f'{side}_arm', (x0, 0, -1), (2, 11, 2))
        r.box(f'{side}_arm', (x0, 0, -1), (2, 3, 2), mat=gown_mat, inflate=0.25)
        r.bone(f'{side}_leg', (1.5 * sx, 13, 0), parent='root', mat=skin)
        r.box(f'{side}_leg', (1.5 * sx - 1, 12, -1), (2, 12, 2))
    m = Model('poseida', 64, 64, r.roots)
    return m
