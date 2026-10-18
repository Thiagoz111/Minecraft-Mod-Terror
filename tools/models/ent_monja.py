"""La Monja 'Sor Agonia' -- the faceless sister of the Convento de Santa Ines."""
import math
from mcmodel import Model, fbm, vnoise, hash3, face_light, pick
from rig import Rig
from emat import *

HABIT = [hx('#030305'), hx('#08080c'), hx('#0f1016'), hx('#171923'), hx('#212433'), hx('#2d3144'), hx('#3c4157')]
COIF = [hx('#2d2e33'), hx('#4c4e55'), hx('#71747c'), hx('#979aa2'), hx('#babdc4'), hx('#d8dadf'), hx('#eff0f2')]
NUN_FACE = [hx('#1b1a1a'), hx('#323030'), hx('#4f4b4a'), hx('#6e6866'), hx('#8f8885'), hx('#b0a8a3'), hx('#d0c8c1')]


def ucoord(ctx):
    x, y, z = ctx.pos
    return x if ctx.face in ('front', 'back', 'top', 'bottom') else z + 30


def habit_mat(ctx):
    x, y, z = ctx.pos
    if ctx.face == 'bottom' and ctx.bone.name.startswith('robe'):
        return None
    v = 0.55 + face_light(ctx) * 1.2
    u = ucoord(ctx)
    k = (u * 0.55 + vnoise(u * 0.3, y * 0.07, 0, 3) * 1.6) % 2.8
    if k < 0.6:
        v -= 0.2
    elif k < 1.2:
        v += 0.1
    v += (fbm(x * 0.2, y * 0.2, z * 0.2, 2, 5) - 0.5) * 0.2
    c = pick(HABIT, v)
    if ctx.bone.name == 'robe3':
        col = hash3(math.floor(u), 0, 2, 7)
        if y > 21.5 + col * 2.8:
            return None
    return c


def coif_mat(ctx):
    x, y, z = ctx.pos
    if ctx.face == 'bottom':
        return None
    v = 0.6 + face_light(ctx) + (fbm(x * 0.3, y * 0.3, z * 0.3, 2, 11) - 0.5) * 0.2
    c = pick(COIF, v)
    if fbm(x * 0.4, y * 0.4, z * 0.4, 2, 13) > 0.7:
        c = mix(c, (96, 86, 60, 255), 0.4)  # yellowed, aged linen
    if ctx.face == 'front' and ctx.bone.name == 'coif':
        # open in the middle where the face shows
        if 1 <= ctx.i <= ctx.w - 2 and 1 <= ctx.j:
            return None
    return c


def face_mat(ctx):
    x, y, z = ctx.pos
    v = 0.55 + face_light(ctx) + (fbm(x * 0.5, y * 0.5, z * 0.5, 2, 17) - 0.5) * 0.25
    return pick(NUN_FACE, v)


def hand_mat(ctx):
    x, y, z = ctx.pos
    v = 0.5 + face_light(ctx) + (fbm(x * 0.5, y * 0.5, z * 0.5, 2, 19) - 0.5) * 0.25 - ctx.t * 0.2
    return pick(NUN_FACE, v)


def cross_mat(ctx):
    v = 0.55 + face_light(ctx) * 1.5
    return pick([hx('#2a1a08'), hx('#4a3010'), hx('#78501c'), hx('#a8762e'), hx('#d4a64a'), hx('#f2d684')], v)


FACE = [
    "SSSSSS",
    "dddddd",
    "dYYdYY",
    "SdddSd",
    "SSSSSS",
    "SkkkkS",
    "kTkTkT",
    "SkkkkS",
]


def face_decal(img, u0, v0, w, h):
    px = img.load()
    pal = {'d': (10, 8, 10, 255), 'Y': (250, 214, 90, 255), 'k': (8, 4, 6, 255), 'T': (220, 214, 196, 255)}
    for j, row in enumerate(FACE):
        for i, ch in enumerate(row):
            if ch in pal and i < w and j < h:
                px[u0 + i, v0 + j] = pal[ch]


def eyes_decal(img, u0, v0, w, h):
    px = img.load()
    for j, row in enumerate(FACE):
        for i, ch in enumerate(row):
            if ch == 'Y' and i < w and j < h:
                px[u0 + i, v0 + j] = (255, 226, 110, 255)


def build():
    r = Rig()
    r.bone('body', (0, -4, 0), mat=habit_mat)
    r.box('body', (-4, -4, -2), (8, 11, 4))
    r.bone('robe1', (0, 7, 0), parent='body', mat=habit_mat)
    r.box('robe1', (-4.5, 7, -2.5), (9, 6, 5))
    r.bone('robe2', (0, 13, 0), parent='robe1', mat=habit_mat)
    r.box('robe2', (-5.5, 13, -3.5), (11, 5, 7))
    r.bone('robe3', (0, 18, 0), parent='robe2', mat=habit_mat)
    r.box('robe3', (-6.5, 18, -4.5), (13, 6, 9))
    r.bone('head', (0, -4, 0), parent='body', mat=face_mat)
    r.box('head', (-3, -12, -3), (6, 8, 6), decals={'front': face_decal, 'eyes:front': eyes_decal})
    r.bone('coif', (0, -8, 0), parent='head', mat=coif_mat)
    r.box('coif', (-3.5, -12.5, -3.5), (7, 9, 7), inflate=0.15)
    r.bone('veil', (0, -13, 0), parent='head', mat=habit_mat)
    r.box('veil', (-4.5, -14, -3), (9, 3, 8))
    r.box('veil', (-5, -12, 1), (10, 16, 4))                    # back drape
    r.box('veil', (-5, -11, -2), (1, 10, 4))                     # side flaps
    r.box('veil', (4, -11, -2), (1, 10, 4))
    r.box('body', (-0.5, -3, -2.6), (1, 5, 0), mat=cross_mat)    # pendant cross (inverted)
    r.box('body', (-1.5, 1, -2.6), (3, 1, 0), mat=cross_mat)
    for side, sx in (('right', -1), ('left', 1)):
        x0 = -7 if sx < 0 else 4
        r.bone(f'{side}_arm', (5 * sx, -3, 0), parent='body', mat=habit_mat, rot=(-20, 0, 4 * sx))
        r.box(f'{side}_arm', (x0, -4, -1.5), (3, 10, 3))
        r.box(f'{side}_arm', (x0 - 0.5, 4, -2), (4, 5, 4))           # bell sleeve
        r.bone(f'{side}_hand', (5.5 * sx, 9, 0), parent=f'{side}_arm', mat=hand_mat)
        xh = -6.5 if sx < 0 else 4.5
        r.box(f'{side}_hand', (xh, 8, -1), (2, 2, 2))
        for k in range(3):
            r.box(f'{side}_hand', (xh + (k % 2), 10, -1 + k * 0.7), (1, 5 - (k == 1), 1))
    m = Model('monja', 128, 64, r.roots)
    return m
