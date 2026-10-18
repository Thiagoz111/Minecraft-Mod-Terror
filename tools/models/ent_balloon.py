"""Sonrisas' red balloon: glossy latex with a faded printed grin, knot and a long string."""
from mcmodel import Model
from rig import Rig
from paint import hx, ramp, pick, lit, edge_dark, pixelart, chain

RED = ramp('#c8141e', n=7, spread=0.7, hue_shift=0.04)
STRING = [hx('#d8d2c4'), hx('#b8b0a0')]


def latex(ctx):
    v = 0.55 + ctx.n[1] * -0.25 + (0.5 - ctx.t) * 0.15
    v = edge_dark(ctx, lit(ctx, v, 0.6), 0.1)
    # specular highlight on the upper-left of the front/west faces
    if ctx.face in ('front', 'west', 'top') and ctx.s < 0.45 and ctx.t < 0.4:
        v += 0.25
    return pick(RED, v)


def string_mat(ctx):
    return STRING[(ctx.j // 2) % 2]


GRIN = pixelart([
    '.d..d.',
    '.d..d.',
    '......',
    'd....d',
    '.dddd.',
], {'d': hx('#4a070d')}, dy=0)
SHINE = pixelart(['ww', 'w.'], {'w': hx('#ffb0a8')}, anchor='topleft', dx=1, dy=1)

DEFAULT_MAT = latex
FOCUS = 'balloon'
POSES = {}
ANIM_NOTES = 'balloon bobs and slowly spins; string sways from the knot.'


def build():
    r = Rig()
    r.bone('string', (0, 24, 0))
    r.box('string', (0, 6, 0), (0, 18, 1), mat=string_mat)
    r.box('string', (-0.5, 6, 0.5), (1, 18, 0), mat=string_mat)
    r.bone('balloon', (0, 6, 0), parent='string')
    r.box('balloon', (-4, -4, -4), (8, 9, 8))
    r.box('balloon', (-3, -6, -3), (6, 2, 6))
    r.box('balloon', (-5, -2, -3), (1, 6, 6))
    r.box('balloon', (4, -2, -3), (1, 6, 6))
    r.box('balloon', (-3, -2, -5), (6, 6, 1), decals={'front': chain(GRIN, SHINE)})
    r.box('balloon', (-3, -2, 4), (6, 6, 1))
    r.box('balloon', (-1, 5, -1), (2, 2, 2))
    m = Model('balloon', 64, 32, r.roots)
    return m
