"""La Llorona -- the Weeping Woman of the river."""
import math
from mcmodel import Model, fbm, vnoise, hash3, face_light, pick
from rig import Rig
from emat import *
LLORONA_SKIN = [hx("#14161d"), hx("#262a35"), hx("#3b404e"), hx("#545b6a"), hx("#6e7686"), hx("#8b93a1"), hx("#a9afba")]


def ucoord(ctx):
    """Horizontal surface coordinate that wraps around the body."""
    x, y, z = ctx.pos
    return x if ctx.face in ('front', 'back', 'top', 'bottom') else z + 40


def dress_mat(ctx):
    x, y, z = ctx.pos
    if ctx.face == 'bottom' and ctx.bone.name in ('skirt3', 'skirt2', 'skirt1'):
        return None
    if ctx.face == 'top' and ctx.bone.name in ('skirt2', 'skirt3'):
        # visible ledge of each tier: shadowed fabric folding over
        v = 0.42
    else:
        v = 0.6 + face_light(ctx)
    u = ucoord(ctx)
    # deliberate fold lines: dark crease + lit ridge
    k = (u * 0.62 + vnoise(u * 0.3, y * 0.08, 0, 5) * 1.4) % 2.6
    if k < 0.55:
        v -= 0.17
    elif k < 1.1:
        v += 0.08
    v += (fbm(x * 0.16, y * 0.12, z * 0.16, 2, 7) - 0.5) * 0.22
    # wet, heavier and darker toward the hem
    v -= max(0.0, (y - 6) / 18) * 0.3
    c = pick(WHITE_DRESS, v)
    # algae + river mud creeping up from the hem, low frequency blobs
    m = fbm(x * 0.22, y * 0.22, z * 0.22, 2, 11)
    if y > 13 and m + (y - 13) * 0.035 > 0.74:
        c = mix(c, (48, 62, 38, 255), 0.5)
    if y > 18 and m + (y - 18) * 0.05 > 0.66:
        c = mix(c, (38, 29, 22, 255), 0.55)
    if ctx.bone.name == 'skirt3':
        col = hash3(math.floor(u * 1.0), 0, 3, 21)
        if y > 21.0 + col * 3.2:
            return None
    if ctx.bone.name == 'body' and -4 <= y < -3:
        c = pick(WHITE_DRESS, 0.75)  # neckline trim
    return c


def skin_mat(ctx):
    x, y, z = ctx.pos
    v = 0.62 + face_light(ctx) + (fbm(x * 0.25, y * 0.25, z * 0.25, 2, 41) - 0.5) * 0.18
    if ctx.bone.name.endswith(('forearm', 'hand')):
        v -= max(0.0, (y - 6) / 16) * 0.25  # extremities get darker, bluish
    c = pick(LLORONA_SKIN, v)
    vein = abs(fbm(x * 0.5, y * 0.2, z * 0.5, 2, 43) - 0.5)
    if vein < 0.018 and ctx.bone.name not in ('head',):
        c = mix(c, (56, 66, 108, 255), 0.5)
    return c


def hair_color(ctx):
    x, y, z = ctx.pos
    u = ucoord(ctx)
    strand = hash3(math.floor(u * 1.0), 0, 7, 51)
    v = 0.25 + strand * 0.45 + face_light(ctx) * 0.5
    v += (vnoise(u * 0.5, y * 0.12, 0, 52) - 0.5) * 0.3
    c = pick(BLACK_HAIR, v)
    if strand > 0.82 and (int(y) % 4) < 2:
        c = mix(c, (78, 88, 116, 255), 0.35)  # wet sheen
    return c


def hair_mat(alpha_fn=None):
    def f(ctx):
        if alpha_fn is not None and not alpha_fn(ctx):
            return None
        return hair_color(ctx)
    return f


def back_hair_alpha(ctx):
    x = ctx.pos[0]
    col = hash3(math.floor(x), 0, 0, 61)
    return ctx.pos[1] < 9 + col * 7


def front_strand_alpha(ctx):
    x, y = ctx.pos[0], ctx.pos[1]
    col = hash3(math.floor(x * 1.0), 0, 0, 63)
    return y < -3 + col * 7


def shell_alpha(ctx):
    """Hair shell around the skull: open over the face, parted in the middle."""
    if ctx.face == 'bottom':
        return False
    if ctx.face == 'front':
        return ctx.j == 0 or ctx.i == 0 or ctx.i == ctx.w - 1 or (ctx.j <= 1 and ctx.i in (1, ctx.w - 2))
    return True


FACE = [
    "SSSSSSS",
    "SdSSSdS",
    "dKwSwKd",
    "dKKSKKd",
    "StdSdtS",
    "StSSStS",
    "SSSmSSS",
    "StmmmtS",
]


def face_decal(img, u0, v0, w, h):
    px = img.load()
    pal = {'d': (36, 40, 52, 255), 'K': (5, 5, 8, 255), 'w': (225, 232, 240, 255),
           't': (8, 8, 12, 255), 'm': (10, 4, 6, 255)}
    for j, row in enumerate(FACE):
        for i, ch in enumerate(row):
            if ch in pal:
                px[u0 + i, v0 + j] = pal[ch]
            elif j <= 1:
                px[u0 + i, v0 + j] = scale(px[u0 + i, v0 + j], 0.78)


def build():
    r = Rig()
    skin = skin_mat
    r.bone('body', (0, -4, 0), mat=dress_mat)
    r.box('body', (-3, -4, -1.5), (6, 10, 3))
    r.box('body', (-1, -6, -1), (2, 2, 2), mat=skin)                   # neck
    r.bone('head', (0, -6, 0), parent='body', mat=skin)
    r.box('head', (-3.5, -14, -3.5), (7, 8, 7), decals={'front': face_decal})
    r.box('head', (-3.5, -14, -3.5), (7, 8, 7), mat=hair_mat(shell_alpha), inflate=0.4)
    r.bone('hair_back', (0, -12, 3.9), parent='head', mat=hair_mat(back_hair_alpha))
    r.box('hair_back', (-4, -13, 3.9), (8, 29, 1))
    r.bone('hair_front', (0, -14, -3.9), parent='head', mat=hair_mat(front_strand_alpha))
    r.box('hair_front', (-3.9, -14, -3.95), (2, 16, 0))
    r.box('hair_front', (1.9, -14, -3.95), (2, 13, 0))
    r.box('hair_front', (-0.5, -14, -4.0), (1, 9, 0))
    r.bone('skirt1', (0, 6, 0), parent='body', mat=dress_mat)
    r.box('skirt1', (-3.5, 6, -2), (7, 4, 4))
    r.box('skirt1', (-4, 10, -2.5), (8, 4, 5))
    r.bone('skirt2', (0, 14, 0), parent='skirt1', mat=dress_mat)
    r.box('skirt2', (-5, 14, -3.5), (10, 5, 7))
    r.bone('skirt3', (0, 19, 0), parent='skirt2', mat=dress_mat)
    r.box('skirt3', (-6, 19, -4.5), (12, 5, 9))
    for side, sx in (('right', -1), ('left', 1)):
        x0 = -5 if sx < 0 else 3
        r.bone(f'{side}_arm', (4 * sx, -3, 0), parent='body', mat=skin, rot=(-16, 0, 7 * sx))
        r.box(f'{side}_arm', (x0, -4, -1), (2, 9, 2))
        r.box(f'{side}_arm', (x0, -4, -1), (2, 4, 2), mat=dress_mat, inflate=0.3)  # sleeve
        r.bone(f'{side}_forearm', (4 * sx, 5, 0), parent=f'{side}_arm', mat=skin, rot=(-10, 0, 0))
        r.box(f'{side}_forearm', (x0, 5, -1), (2, 8, 2))
        r.bone(f'{side}_hand', (4 * sx, 13, 0), parent=f'{side}_forearm', mat=skin)
        r.box(f'{side}_hand', (x0, 13, -1), (2, 2, 2))
        r.box(f'{side}_hand', (x0, 15, -1), (1, 5, 1))
        r.box(f'{side}_hand', (x0 + 1, 15, -1), (1, 4, 1))
        r.box(f'{side}_hand', (x0, 15, 0), (1, 4, 1))
        r.box(f'{side}_hand', (x0 + 1, 15, 0), (1, 3, 1))
    m = Model('llorona', 128, 64, r.roots)
    m.render_type = 'entityTranslucent'
    return m


if __name__ == '__main__':
    import sys
    m = build().pack()
    img = m.paint(dress_mat)
    img.save(sys.argv[1] if len(sys.argv) > 1 else '/tmp/llorona.png')
