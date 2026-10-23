"""La sabana -- event 44 'sabana' of Casa Morales (DEAD LINE, docs/design/casa_terror.md 5; El Conjuro).

A bedsheet on the patio clothesline fills out in the wind with the shape of a person -- a head, shoulders, two arms
reaching -- flies at you, and falls on the grass EMPTY.

Two shapes on one rig (toggles in Java, ModelPart.visible):
* figure (root): the sheet over somebody who is not there.  A round head under the cloth with the hollows of two eyes
  and an open mouth pressed into it, the shoulders, the arms reaching forward under two sleeves of sheet, and four
  hanging drapes (front, back, left, right), each in three segments that ripple and trail.  ~1.9 blocks.
* flat (root): the same sheet with nobody in it: a plain rectangle in three segments (flat_1 .. flat_3).  Java hangs it
  from the line (pivot on its top edge) or lays it on the ground (rotated flat, crumpled).

Authored at 2x texel density (model.scale = 0.5): +Y down, ground y = 24, faces -Z, right_* on -X.
Cloth: old off-white cotton, washed grey in the folds, a yellowed water stain, a darned hem; the cloth is thin at the
ragged bottom edge (alpha cut-outs).  Nothing glows.
"""
import math

from mcmodel import Model, fbm, vnoise, hash3, face_light, pick
from rig import Rig
from paint import hx, mix


def pal(*h):
    return [hx(c) for c in h]


CLOTH = pal('#3a3936', '#55534e', '#706d66', '#8a867e', '#a39e94', '#b9b4a8', '#cbc6ba', '#d9d5ca', '#e5e2d8', '#efede5')
STAIN = pal('#8f7c52', '#a8956a', '#bfae86')
HOLLOW = pal('#1c1b1a', '#2c2a28', '#403d39', '#57534d')
THREAD = hx('#7e7a72')


def clamp(v, a=0.0, b=1.0):
    return a if v < a else b if v > b else v


def local(ctx):
    w, h, d = ctx.cube.size
    s, t, f = ctx.s, ctx.t, ctx.face
    if f == 'front':
        return s * w, t * h, 0.0
    if f == 'back':
        return (1 - s) * w, t * h, float(d)
    if f == 'west':
        return 0.0, t * h, (1 - s) * d
    if f == 'east':
        return float(w), t * h, s * d
    if f == 'top':
        return s * w, 0.0, (1 - t) * d
    return s * w, float(h), (1 - t) * d


def cloth_v(ctx, base=0.66):
    """Folds: soft vertical waves across the drapes, a slow fbm for the weave's dirt, light from above."""
    x, y, z = ctx.pos
    lx, ly, lz = local(ctx)
    across = lx if ctx.face in ('front', 'back', 'top', 'bottom') else lz
    v = base + face_light(ctx) * 0.7
    v += math.sin(across * 0.9 + (hash3(ctx.cube.origin[0], ctx.cube.origin[2], 0, 3) * 6.0)) * 0.07
    v += (fbm(x * 0.18, y * 0.12, z * 0.18, 3, 5) - 0.5) * 0.18
    return v


def cloth(ctx, base=0.66, ragged=False):
    x, y, z = ctx.pos
    lx, ly, lz = local(ctx)
    w, h, d = ctx.cube.size
    if ragged and ctx.face in ('front', 'back', 'west', 'east'):
        # the bottom edge is torn: a ragged line of missing texels, longer strands here and there
        cut = h - 1 - int(hash3(math.floor(x if ctx.face in ('front', 'back') else z), 0, 0, 41) * 3.2)
        if ctx.j > cut:
            return None
    v = cloth_v(ctx, base)
    c = pick(CLOTH, v)
    # a yellowed water stain and a few darker spots
    st = fbm(x * 0.12 + 7, y * 0.1, z * 0.12, 3, 23)
    if st > 0.62:
        c = mix(c, STAIN[1], clamp((st - 0.62) * 3.5) * 0.55)
    if hash3(x * 1.7, y * 1.7, z * 1.7, 31) > 0.985:
        c = mix(c, CLOTH[2], 0.6)
    # the darned hem near the bottom of each drape
    if ragged and ctx.face in ('front', 'back') and ctx.j == h - 4 and ctx.i % 2 == 0:
        c = THREAD
    return c


def head_mat(ctx):
    """The head under the sheet: no holes -- the cloth is PRESSED into a face from behind.  Soft relief only: two deep
    eye sockets (darkest in the middle, the cloth sloping into them), the brow and the cheekbones pushing it out (lit),
    a thin nose ridge, and a mouth dragged open far too long, the cotton stretched into creases round it."""
    c = cloth(ctx, 0.7)
    if ctx.face != 'front' or c is None:
        return c
    i, j, w, h = ctx.i, ctx.j, ctx.w, ctx.h
    cx = (w - 1) / 2.0
    v = cloth_v(ctx, 0.7)
    # relief height field: + pushes the cloth toward the light, - sinks it into shadow
    rel = 0.0
    for ex in (cx - 3.2, cx + 3.0):                       # eye sockets (the right one a little lower: wrong)
        ey = 5.6 if ex < cx else 6.1
        dx, dy = (i - ex) / 2.3, (j - ey) / 2.0
        r = dx * dx + dy * dy
        rel -= max(0.0, 1.0 - r) * 0.72
    rel += max(0.0, 1.0 - ((j - 3.4) / 1.2) ** 2) * 0.14 * (1.0 if abs(i - cx) < 5.5 else 0.0)   # brow ridge
    for kx in (cx - 4.2, cx + 4.2):                       # cheekbones
        dx, dy = (i - kx) / 1.6, (j - 8.6) / 1.2
        rel += max(0.0, 1.0 - dx * dx - dy * dy) * 0.16
    if abs(i - cx) < 0.7 and 6 <= j <= 9:
        rel += 0.12                                       # the nose ridge
    # the mouth: a long slot dragged open (taller than wide), a little crooked
    mx = cx + 0.5 + (j - 11.0) * 0.12
    dx, dy = (i - mx) / 1.4, (j - 11.8) / 3.0
    rm = dx * dx + dy * dy
    rel -= max(0.0, 1.0 - rm) * 0.75
    if 1.0 <= rm < 2.4 and abs(i - mx) < 3.2:
        rel += 0.08 * (1 if (i + j) % 2 else -1)          # the cotton stretched into creases round it
    c = pick(CLOTH, v + rel)
    if rel < -0.45:
        c = pick(HOLLOW, 1.0 + (rel + 0.45) * 4.0)        # the deepest pits fall into real shadow
    return c


def figure_mat(ctx):
    name = ctx.cube.name or ''
    if name == 'head':
        return head_mat(ctx)
    return cloth(ctx, 0.64, ragged=name.startswith('drape_3') or name == 'sleeve_hang')


def flat_mat(ctx):
    name = ctx.cube.name or ''
    return cloth(ctx, 0.68, ragged=name == 'flat_3')


DEFAULT_MAT = figure_mat
FOCUS = 'head'

TOGGLE_DEFAULT = {'figure': True, 'flat': False}


def build(variant=None, pose=None):
    r = Rig()
    # ---------------- the figure under the sheet (root 'figure' at the neck)
    r.bone('figure', (0, -22, 0), mat=figure_mat)
    c = r.box('figure', (-15, -22, -7), (30, 6, 14))
    c.name = 'shoulders'
    r.bone('head', (0, -22, 0), parent='figure', mat=figure_mat)
    c = r.box('head', (-7, -36, -8), (14, 14, 14), inflate=0.5)
    c.name = 'head'
    # arms reaching forward under the cloth, with a flap of sheet hanging under each
    for side, sx in (('right', -1), ('left', 1)):
        b = f'{side}_sleeve'
        r.bone(b, (11 * sx, -19, -4), parent='figure', rot=(-70, 0, 0), mat=figure_mat)
        c = r.box(b, (11 * sx - 3, -19, -7), (6, 22, 6))
        c.name = 'sleeve'
        bh = f'{side}_sleeve_hang'
        r.bone(bh, (11 * sx, -19, -1), parent=b, rot=(0, 0, 0), mat=figure_mat)
        c = r.box(bh, (11 * sx, -19, -1), (0, 20, 9))
        c.name = 'sleeve_hang'
    # four drapes, three segments each (pivots on the shoulder line, every segment hinged on the one above)
    drapes = {'front': ((-15, -16, -7.5), (30, 0)), 'back': ((-15, -16, 7.5), (30, 0)),
              'right': ((-15.5, -16, -7), (0, 14)), 'left': ((15.5, -16, -7), (0, 14))}
    for dname, ((x0, y0, z0), (w, d)) in drapes.items():
        parent = 'figure'
        y = y0
        for k, hgt in enumerate((13, 13, 14)):
            b = f'drape_{dname}_{k + 1}'
            px = 0 if w else x0
            pz = z0 if w else 0
            r.bone(b, (px, y, pz), parent=parent, mat=figure_mat)
            c = r.box(b, (x0 if w else x0, y, z0 if w else -7), (w, hgt, 0) if w else (0, hgt, d))
            c.name = f'drape_{k + 1}'
            parent = b
            y += hgt
    # ---------------- the empty sheet (root 'flat', pivot on its top edge)
    r.bone('flat', (0, -26, 0), mat=flat_mat)
    y = -26
    parent = 'flat'
    for k, hgt in enumerate((16, 17, 17)):
        b = f'flat_{k + 1}'
        if k == 0:
            c = r.box('flat', (-17, y, 0), (34, hgt, 0))
            c.name = 'flat_1'
        else:
            r.bone(b, (0, y, 0), parent=parent, mat=flat_mat)
            c = r.box(b, (-17, y, 0), (34, hgt, 0))
            c.name = b
            parent = b
        y += hgt
    m = Model('sabana', 256, 128, r.roots)
    m.scale = 0.5
    return m


POSES = {
    # flying at you: the arms up and forward, the head pitched toward you, the drapes streaming back
    'fly': {'figure': (0.35, 0, 0, 0, 0, 0), 'head': (-0.25, 0, 0.12, 0, 0, 0),
            'right_sleeve': (-0.35, 0.15, 0.2, 0, 0, 0), 'left_sleeve': (-0.25, -0.15, -0.2, 0, 0, 0),
            'drape_front_1': (-0.25, 0, 0, 0, 0, 0), 'drape_front_2': (-0.3, 0, 0, 0, 0, 0),
            'drape_front_3': (-0.35, 0, 0, 0, 0, 0), 'drape_back_1': (0.55, 0, 0, 0, 0, 0),
            'drape_back_2': (0.35, 0, 0, 0, 0, 0), 'drape_back_3': (0.3, 0, 0, 0, 0, 0),
            'drape_right_1': (0.4, 0, 0.2, 0, 0, 0), 'drape_right_2': (0.25, 0, 0.1, 0, 0, 0),
            'drape_left_1': (0.4, 0, -0.2, 0, 0, 0), 'drape_left_2': (0.25, 0, -0.1, 0, 0, 0)},
}

ANIM_NOTES = """La sabana (SabanaEntity) -- animation notes.  Radians; offsets in texels at 2x density; t = ageInTicks.
action 0 = HANG (on the line: only 'flat' visible, pivot = the line; flat_k xRot = sin(t * 0.08 + k) * 0.06 * (k + 1)
           and a gust now and then), 1 = FLY (only 'figure': pose 'fly' + every drape segment k ripples
           xRot += sin(t * 0.5 - k * 0.9) * 0.12 * (k + 1), the sleeves wave zRot sin(t * 0.3) * 0.1, the head tilts),
2 = COLLAPSE ('figure' deflates over 8 ticks: figure yScale 1 -> 0.15, x/z 1 -> 1.25, then hidden; 'flat' shown at the
           ground), 3 = FLAT (only 'flat', lying on the ground: flat xRot pi/2, crumpled: flat_2 xRot -0.18, flat_3 0.12,
           pivot lowered to y 23.6).
"""
