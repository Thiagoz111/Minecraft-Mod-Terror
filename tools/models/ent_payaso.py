"""El Payaso 'Sonrisas' -- the thing that stayed behind at Parque Mundo Feliz."""
import math
from mcmodel import Model, fbm, vnoise, hash3, face_light, pick
from rig import Rig
from emat import *

SUIT = [hx('#120c12'), hx('#22141f'), hx('#361f31'), hx('#4c2b45'), hx('#633a59'), hx('#7b4b6f')]
STRIPE = [hx('#26200c'), hx('#3f3413'), hx('#5e4e1c'), hx('#7f6a29'), hx('#a08638'), hx('#bea24c')]
RUFF = [hx('#3c3a3e'), hx('#646167'), hx('#8f8b90'), hx('#b8b4b6'), hx('#d9d5d3'), hx('#efebe6')]
GLOVE = [hx('#4a4643'), hx('#706b67'), hx('#9a948e'), hx('#c0b9b1'), hx('#dcd5cb'), hx('#efe9df')]
SHOE = [hx('#1a0405'), hx('#33080b'), hx('#520e12'), hx('#71151a'), hx('#8f2026')]
RED_HAIR = [hx('#2a0404'), hx('#4b0808'), hx('#700d0c'), hx('#961612'), hx('#b8241a'), hx('#d33a24')]
BALLOON = [hx('#3a0207'), hx('#64040d'), hx('#920a15'), hx('#c0141f'), hx('#e5303a'), hx('#ff6e6a')]


def ucoord(ctx):
    x, y, z = ctx.pos
    return x if ctx.face in ('front', 'back', 'top', 'bottom') else z + 30


def suit_mat(ctx):
    """Faded purple suit with mustard pinstripes, grime and torn patches."""
    x, y, z = ctx.pos
    v = 0.58 + face_light(ctx) + (fbm(x * 0.25, y * 0.25, z * 0.25, 2, 3) - 0.5) * 0.25
    u = ucoord(ctx)
    c = pick(SUIT, v)
    if int(math.floor(u)) % 3 == 0:
        c = pick(STRIPE, v - 0.1)
    if fbm(x * 0.3, y * 0.3, z * 0.3, 2, 9) > 0.7:
        c = mix(c, (40, 34, 20, 255), 0.5)  # filth
    if fbm(x * 0.5, y * 0.5, z * 0.5, 2, 11) > 0.78:
        c = mix(c, (100, 12, 16, 255), 0.65)  # blood splatter
    return c


def ruff_mat(ctx):
    x, y, z = ctx.pos
    u = ucoord(ctx)
    v = 0.6 + face_light(ctx) + (0.18 if int(math.floor(u)) % 2 == 0 else -0.12)
    c = pick(RUFF, v)
    if fbm(x * 0.4, y * 0.4, z * 0.4, 2, 13) > 0.66:
        c = mix(c, (110, 96, 64, 255), 0.5)
    return c


def face_mat(ctx):
    x, y, z = ctx.pos
    v = 0.66 + face_light(ctx) + (fbm(x * 0.4, y * 0.4, z * 0.4, 2, 17) - 0.5) * 0.2
    c = pick(CLOWN_WHITE, v)
    if fbm(x * 0.6, y * 0.6, z * 0.6, 2, 19) > 0.7:
        c = mix(c, (130, 120, 104, 255), 0.45)  # cracked greasepaint
    return c


def hair_mat(ctx):
    x, y, z = ctx.pos
    v = 0.4 + face_light(ctx) * 0.6 + (hash3(math.floor(x * 1.4), math.floor(y * 1.4), math.floor(z * 1.4), 23) - 0.5) * 0.7
    if ctx.face == 'bottom':
        return None
    if hash3(math.floor(x * 1.4), math.floor(y * 1.4), math.floor(z * 1.4), 29) > 0.82:
        return None  # frizzy gaps
    return pick(RED_HAIR, v)


def glove_mat(ctx):
    v = 0.6 + face_light(ctx) + (fbm(*[p * 0.5 for p in ctx.pos], 2, 31) - 0.5) * 0.25
    c = pick(GLOVE, v)
    if ctx.pos[1] > 14 and fbm(*[p * 0.4 for p in ctx.pos], 2, 33) > 0.55:
        c = mix(c, (110, 10, 14, 255), 0.7)  # blood-soaked fingertips
    return c


def shoe_mat(ctx):
    v = 0.55 + face_light(ctx) + (fbm(*[p * 0.4 for p in ctx.pos], 2, 37) - 0.5) * 0.25
    return pick(SHOE, v)


def balloon_mat(ctx):
    x, y, z = ctx.pos
    v = 0.55 + face_light(ctx) * 1.5
    if ctx.face == 'front' and 1 <= ctx.i <= 2 and 1 <= ctx.j <= 2:
        v += 0.35  # specular glint
    return pick(BALLOON, v)


def string_mat(ctx):
    return (200, 196, 186, 255)


def hat_mat(ctx):
    v = 0.55 + face_light(ctx)
    u = ucoord(ctx)
    c = pick(SUIT, v)
    if 1 <= (ctx.pos[1] % 4) < 2:
        c = pick(STRIPE, v)
    return c


def nose_mat(ctx):
    v = 0.55 + face_light(ctx) * 1.4
    if ctx.face == 'front' and ctx.i == 0 and ctx.j == 0:
        v += 0.4
    return pick(BALLOON, v)


FACE = [
    "WWWWWWWW",
    "WbWWWWbW",
    "bKbWWbKb",
    "WbWWWWbW",
    "WWWWWWWW",
    "rWWWWWWr",
    "rrtttttr",
    "WrrtktrW",
    "WWrrrrWW",
]


def face_decal(img, u0, v0, w, h):
    px = img.load()
    pal = {'b': (24, 14, 40, 255), 'K': (6, 4, 8, 255), 'r': (150, 12, 22, 255), 't': (226, 214, 176, 255), 'k': (20, 4, 6, 255)}
    for j, row in enumerate(FACE):
        for i, ch in enumerate(row):
            if ch in pal:
                px[u0 + i, v0 + j] = pal[ch]
    # red lipstick tear drips
    px[u0 + 0, v0 + 6] = (110, 8, 16, 255)
    px[u0 + 7, v0 + 6] = (110, 8, 16, 255)


def eyes_decal(img, u0, v0, w, h):
    px = img.load()
    px[u0 + 1, v0 + 2] = (255, 220, 120, 255)
    px[u0 + 6, v0 + 2] = (255, 220, 120, 255)


def build():
    r = Rig()
    r.bone('body', (0, -2, 0), mat=suit_mat)
    r.box('body', (-4, -2, -2), (8, 11, 4))
    r.box('body', (-4.5, 6, -2.5), (9, 4, 5))                            # baggy waist
    r.bone('ruff', (0, -3, 0), parent='body', mat=ruff_mat)
    r.box('ruff', (-5.5, -4, -3.5), (11, 2, 7))
    r.box('ruff', (-4.5, -2.5, -3), (9, 1, 6), inflate=0.2)
    r.bone('head', (0, -4, 0), parent='body', mat=face_mat)
    r.box('head', (-4, -13, -4), (8, 9, 8), decals={'front': face_decal, 'eyes:front': eyes_decal})
    r.box('head', (-1, -9, -5.5), (2, 2, 2), mat=nose_mat)                  # nose
    r.bone('hair', (0, -10, 0), parent='head', mat=hair_mat)
    r.box('hair', (-7, -12, -2), (3, 5, 5))
    r.box('hair', (4, -12, -2), (3, 5, 5))
    r.box('hair', (-6, -9, -1), (2, 3, 4))
    r.box('hair', (4, -9, -1), (2, 3, 4))
    r.bone('hat', (0, -13, 0), parent='head', rot=(0, 0, -12), mat=hat_mat)
    r.box('hat', (-2, -17, -2), (4, 4, 4))
    r.box('hat', (-3, -14, -3), (6, 1, 6))
    r.box('hat', (-0.5, -19, -0.5), (1, 2, 1), mat=nose_mat)                # pom-pom
    for side, sx in (('right', -1), ('left', 1)):
        x0 = -6 if sx < 0 else 4
        r.bone(f'{side}_arm', (5 * sx, -1, 0), parent='body', mat=suit_mat, rot=(0, 0, 5 * sx))
        r.box(f'{side}_arm', (x0, -2, -1), (2, 12, 2))
        r.box(f'{side}_arm', (x0, 7, -1.5), (2, 2, 3), mat=ruff_mat, inflate=0.3)   # cuff ruffle
        r.bone(f'{side}_hand', (5 * sx, 10, 0), parent=f'{side}_arm', mat=glove_mat)
        r.box(f'{side}_hand', (x0 - 0.5, 10, -1.5), (3, 3, 3))
        r.box(f'{side}_hand', (x0, 13, -1.5), (1, 3, 1))
        r.box(f'{side}_hand', (x0 + 1, 13, -1.5), (1, 4, 1))
        r.box(f'{side}_hand', (x0, 13, 0), (1, 3, 1))
        xl = -3.5 if sx < 0 else 0.5
        r.bone(f'{side}_leg', (2 * sx, 10, 0), parent='body', mat=suit_mat)
        r.box(f'{side}_leg', (xl, 10, -1.5), (3, 11, 3))
        r.box(f'{side}_leg', (xl - 0.5, 21, -6), (4, 3, 8), mat=shoe_mat)      # huge shoes
    r.bone('balloon_string', (-5, 13, -1), parent='right_hand', mat=string_mat)
    r.box('balloon_string', (-5, -6, -1.5), (0, 19, 1))
    r.box('balloon_string', (-5.5, -6, -1), (1, 19, 0))
    r.bone('balloon', (-5, -7, -1), parent='balloon_string', mat=balloon_mat)
    r.box('balloon', (-8, -15, -4), (6, 7, 6))
    r.box('balloon', (-7, -16, -3), (4, 1, 4))
    r.box('balloon', (-6, -8, -2), (2, 1, 2))
    m = Model('payaso', 128, 64, r.roots)
    return m
