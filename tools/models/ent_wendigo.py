"""El Wendigo -- emaciated antlered horror of the Bosque Negro."""
import math
from mcmodel import Model, fbm, vnoise, hash3, face_light, pick
from rig import Rig
from emat import *

HIDE = [hx('#0d0b0a'), hx('#1a1513'), hx('#2a221d'), hx('#3b3029'), hx('#4e4037'), hx('#665446'), hx('#7f6b5a')]
FLESH = [hx('#1d0f0e'), hx('#341917'), hx('#4f2622'), hx('#6b3530'), hx('#86493f'), hx('#9f6152')]
SKULL = [hx('#2a2219'), hx('#463b2d'), hx('#665844'), hx('#8a7b61'), hx('#ab9c7e'), hx('#cbbd9e'), hx('#e6dcc3')]


def ucoord(ctx):
    x, y, z = ctx.pos
    return x if ctx.face in ('front', 'back', 'top', 'bottom') else z + 30


def hide_mat(ctx):
    """Taut grey-brown skin stretched over bone, matted fur patches, rot."""
    x, y, z = ctx.pos
    v = 0.55 + face_light(ctx)
    v += (fbm(x * 0.3, y * 0.3, z * 0.3, 3, 3) - 0.5) * 0.3
    fur = fbm(x * 0.18, y * 0.18, z * 0.18, 2, 9)
    if fur > 0.56:
        # matted fur: vertical streaks, darker
        v -= 0.12 + (hash3(math.floor(ucoord(ctx) * 1.5), math.floor(y * 0.5), 0, 4) - 0.5) * 0.25
    c = pick(HIDE, v)
    if fur < 0.32:
        c = mix(c, pick(FLESH, v), 0.65)  # raw exposed flesh
    if hash3(x * 1.7, y * 1.7, z * 1.7, 13) > 0.94:
        c = mix(c, (60, 12, 12, 255), 0.6)  # dried blood flecks
    return c


def rib_mat(ctx):
    """Ribcage: bone ribs over a dark hollow torso."""
    x, y, z = ctx.pos
    if ctx.face in ('front', 'west', 'east'):
        rib = (y * 0.95) % 2.2
        if rib < 1.0 and ctx.face == 'front' and abs(x) > 0.6:
            v = 0.55 + face_light(ctx) + (fbm(x, y, z, 2, 5) - 0.5) * 0.2
            return pick(SKULL, v - 0.12)
        if ctx.face == 'front' and abs(x) <= 0.6:
            return pick(SKULL, 0.5)  # sternum
    return hide_mat(ctx)


def skull_mat(ctx):
    x, y, z = ctx.pos
    v = 0.6 + face_light(ctx) + (fbm(x * 0.5, y * 0.5, z * 0.5, 3, 21) - 0.5) * 0.28
    c = pick(SKULL, v)
    crack = abs(fbm(x * 0.6, y * 0.6, z * 0.6, 2, 23) - 0.5)
    if crack < 0.02:
        c = pick(SKULL, 0.15)
    if fbm(x * 0.4, y * 0.4, z * 0.4, 2, 29) > 0.7:
        c = mix(c, (70, 20, 18, 255), 0.45)  # old blood stains
    return c


def antler_mat(ctx):
    x, y, z = ctx.pos
    v = 0.5 + face_light(ctx) + (hash3(x * 2, y * 2, z * 2, 31) - 0.5) * 0.2
    return pick(SKULL, v - 0.05)


def claw_mat(ctx):
    v = 0.4 + face_light(ctx) + (1 - ctx.t) * 0.25
    return pick([hx('#0a0807'), hx('#1c1612'), hx('#3a3027'), hx('#5d5142'), hx('#857862')], v)


def skull_face(img, u0, v0, w, h):
    """Front of the snout: nasal cavity."""
    px = img.load()
    for j in range(h):
        for i in range(w):
            if 2 <= i <= w - 3 and 1 <= j <= 2:
                px[u0 + i, v0 + j] = (14, 9, 8, 255)
    px[u0 + w // 2 - 1, v0 + h - 1] = (230, 220, 200, 255)
    px[u0 + w // 2, v0 + h - 1] = (230, 220, 200, 255)


def skull_side(img, u0, v0, w, h):
    """Side of the cranium: deep eye socket near the back half."""
    px = img.load()
    for j in range(1, 3):
        for i in range(w - 4, w - 2):
            px[u0 + i, v0 + j] = (8, 5, 5, 255)


def skull_side_l(img, u0, v0, w, h):
    px = img.load()
    for j in range(1, 3):
        for i in range(2, 4):
            px[u0 + i, v0 + j] = (8, 5, 5, 255)


def teeth(img, u0, v0, w, h):
    px = img.load()
    for i in range(w):
        if i % 2 == 0:
            px[u0 + i, v0] = (236, 228, 206, 255)
            if h > 1:
                px[u0 + i, v0 + 1] = (200, 190, 168, 255)


def build():
    r = Rig()
    # pelvis + digitigrade legs
    r.bone('pelvis', (0, -4, 1), mat=hide_mat)
    r.box('pelvis', (-3.5, -6, -1), (7, 4, 4))
    for side, sx in (('right', -1), ('left', 1)):
        x0 = -4.5 if sx < 0 else 1.5
        r.bone(f'{side}_thigh', (2.8 * sx, -3, 1), parent='pelvis', rot=(-28, 0, 3 * sx), mat=hide_mat)
        r.box(f'{side}_thigh', (x0, -4, -0.5), (3, 11, 3))
        r.bone(f'{side}_shin', (2.8 * sx, 7, 1), parent=f'{side}_thigh', rot=(62, 0, 0), mat=hide_mat)
        r.box(f'{side}_shin', (x0 + 0.5, 6, 0), (2, 11, 2))
        r.bone(f'{side}_foot', (2.8 * sx, 17, 1), parent=f'{side}_shin', rot=(-34, 0, 0), mat=hide_mat)
        r.box(f'{side}_foot', (x0 + 0.5, 16.5, 0), (2, 8, 2))
        r.box(f'{side}_foot', (x0, 22, -2), (3, 2, 4), mat=claw_mat)          # cloven hoof
    # hunched torso
    r.bone('torso', (0, -5, 1), parent='pelvis', rot=(38, 0, 0), mat=hide_mat)
    r.box('torso', (-3, -11, -1), (6, 6, 4))                                    # gut (sunken)
    r.box('torso', (-4.5, -22, -2), (9, 11, 5), mat=rib_mat)                    # ribcage
    r.box('torso', (-5.5, -24, -1.5), (11, 3, 4))                               # shoulders
    r.bone('neck', (0, -23, 0), parent='torso', rot=(-50, 0, 0), mat=hide_mat)
    r.box('neck', (-1.5, -28, -1.5), (3, 6, 3))
    r.bone('head', (0, -28, 0), parent='neck', rot=(18, 0, 0), mat=skull_mat)
    r.box('head', (-3, -33, -3), (6, 6, 6), decals={'west': skull_side, 'east': skull_side_l})  # cranium
    r.box('head', (-2, -32, -9), (4, 4, 6), decals={'front': skull_face})      # snout
    r.bone('jaw', (0, -28.5, -2), parent='head', rot=(8, 0, 0), mat=skull_mat)
    r.box('jaw', (-1.5, -29, -8.5), (3, 1, 6), decals={'top': teeth})
    r.box('jaw', (-2, -28, -6), (4, 2, 6), mat=hide_mat)
    # antlers: main beam + tines, each side
    for side, sx in (('right', -1), ('left', 1)):
        b = f'{side}_antler'
        r.bone(b, (2.5 * sx, -33, 0), parent='head', rot=(-20, 0, 35 * sx), mat=antler_mat)
        xa = 2.5 * sx - 0.5
        r.box(b, (xa, -45, -0.5), (1, 12, 1))
        r.box(b, (xa, -41, -4), (1, 1, 4))
        r.box(b, (xa, -44, 0.5), (1, 1, 3))
        r.bone(b + '_tip', (2.5 * sx, -45, 0), parent=b, rot=(0, 0, -45 * sx), mat=antler_mat)
        r.box(b + '_tip', (xa, -52, -0.5), (1, 7, 1))
        r.box(b + '_tip', (xa, -49, -3.5), (1, 1, 3))
        r.bone(b + '_tine', (2.5 * sx, -38, 0), parent=b, rot=(0, 0, 55 * sx), mat=antler_mat)
        r.box(b + '_tine', (xa, -44, -0.5), (1, 6, 1))
    # very long arms
    for side, sx in (('right', -1), ('left', 1)):
        x0 = -7 if sx < 0 else 5
        r.bone(f'{side}_arm', (5.5 * sx, -23, 0), parent='torso', rot=(-35, 0, 6 * sx), mat=hide_mat)
        r.box(f'{side}_arm', (x0, -24, -1), (2, 14, 2))
        r.bone(f'{side}_forearm', (5.5 * sx, -10, 0), parent=f'{side}_arm', rot=(-25, 0, 0), mat=hide_mat)
        r.box(f'{side}_forearm', (x0, -10, -1), (2, 14, 2))
        r.bone(f'{side}_hand', (5.5 * sx, 4, 0), parent=f'{side}_forearm', mat=hide_mat)
        r.box(f'{side}_hand', (x0 - 0.5, 4, -1.5), (3, 3, 3))
        for k, dz in enumerate((-1.5, -0.5, 0.5)):
            r.box(f'{side}_hand', (x0 + (0 if k % 2 else 1), 7, dz), (1, 7 - k, 1), mat=claw_mat)
    m = Model('wendigo', 128, 128, r.roots)
    return m
