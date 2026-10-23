"""The 'copia' look shared by Marta, Jorge and Toti (DEAD LINE, casa_terror.md 2 Act 5 / event 41 copia_sonrie).

Not a model of its own (build_all never builds it): ent_marta.py, ent_jorge.py and ent_toti.py import it to paint their
VARIANT_MATS['copia'].  What walks the upper floor with the family's faces in Act 5 is a copy: the SAME face, but

* a smile far too wide -- from cheek to cheek, every tooth showing, clenched, a dark line above and below;
* eyes one texel too far apart and wide open (white all round a single dark pinpoint), never blinking;
* greyish skin -- desaturated, a little darker, a cold cast -- on every skin texel (face, neck, hands, legs).

Each module provides its own face grid with the copia rows (it knows where its eyes and mouth are) and falls back to its
own palette for every other character; the characters below are the copia's own.
"""
from paint import hx, mix

# copia face characters (never used by the three modules' own grids)
#   E sclera (wide open)  e sclera in shadow  O the pinpoint pupil  Q tooth (lit)  Y tooth (shade)  Z dark gap / lip line
#   G gum  N the grin's corner (pulled up into the cheek)
COPIA_CHARS = {
    'E': hx('#d9d6cf'), 'e': hx('#b4b0a8'), 'O': hx('#0d0909'),
    'Q': hx('#ece6d6'), 'Y': hx('#c4bba6'), 'Z': hx('#1a0a0c'), 'G': hx('#5c2a2e'), 'N': hx('#24100f'),
}


def char_rgba(ch):
    return COPIA_CHARS.get(ch)


def _lum(c):
    return (c[0] * 0.3 + c[1] * 0.59 + c[2] * 0.11) / 255.0


def grey(c, amount=0.8, dark=0.88):
    """Skin -> the copy's skin: most of the colour drained, a cold grey-green cast, slightly darker."""
    if c is None or len(c) < 4 or c[3] == 0:
        return c
    l = _lum(c) * 255.0
    g = (l * 0.95, l * 0.98, l * 0.97)
    r = [(c[k] * (1.0 - amount) + g[k] * amount) * dark for k in range(3)]
    return (max(0, min(255, int(r[0]))), max(0, min(255, int(r[1]))), max(0, min(255, int(r[2]))), c[3])


def teeth_row(n, start='Q'):
    """n alternating teeth: Q Y Q Y ... (or Y Q ... with start='Y')."""
    a, b = ('Q', 'Y') if start == 'Q' else ('Y', 'Q')
    return ''.join(a if i % 2 == 0 else b for i in range(n))


def check(grid, width):
    assert all(len(r) == width for r in grid), [(i, len(r)) for i, r in enumerate(grid) if len(r) != width]
    return grid


def mixc(a, b, t):
    return mix(a, b, t)
