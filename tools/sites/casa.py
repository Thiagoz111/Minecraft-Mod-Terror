"""Casa Morales (case 2): Pasaje Las Glicinas 1961, Villa Esperanza. Layout from docs/design/BIBLIA.md 2.2 f.

    python3 tools/sites/casa.py      -> src/main/resources/data/deadline/sites/casa.json (+ plan images)

Origin: x east, y up (y=0 = ground-floor level, the grass is y=-1), z south; the street is towards -z.
The house rooms fill X -10..10, Z 0..14 inside an outer skin of facade brick and render (x=+-11, z=-1 / 15), so the
windows sit in a deep reveal. Ground floor (PB) y 0..2 under a ceiling at y=3, first floor (1P) floor at y=4, rooms
y 5..7, ceiling y=8; basement y -5..-3 (floor -6, slab -2); the sealed 1961 room one step lower (floor -7, 4 high).

Every room is a box carved out of solid filler and paints its own ring, so two rooms with different finishes never
share a wall block: their partition is two blocks thick, one face each (House.check_finishes() lists any wall cell
that would show a neighbour's paint). A door in a double wall sits in one layer, the other layer is an open reveal.

PB  front: NONA (x -9..-4, z 1..5) | LIVING (x -1..5, z 1..6) | HALL (x 7..8) + STAIR (x 9, rising +z)
    back:  LAVADERO (x -7..-5, z 8..13, basement stair at x -9) | COCINA (x -3..2, z 9..13) | COMEDOR (x 5..9)
1P  a 1 m corridor (z 7, x -1..9) with five doors in a row (the cascade): LUCIA at the far end (x -9..-4, z 7..13),
    MATRIMONIAL (x -9..-1, z 1..4) and COSTURA (x 2..7 + the balcony over the entrance) on the street side,
    TOTI (x -1..3, z 10..13, walk-in placard on the back wall) and BANO (x 6..9, z 10..13) on the patio side.
Everything is built from the casa_* building kits (tools/blocks/kit_casa_estructura.py, kit_casa_muebles.py): K()
places a kit block and refuses to overwrite a piece of furniture already placed (build() raises on any clash).
Lamps are placed OFF by default (the _apagado/_apagada variant) except the living lamp and TV, the Nona's altar, the
porch lamp, the street lamps, the patio lamp by the kitchen door (it lights the cucha), Toti's PC and the neighbours'.
"""
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..'))
from workdir import WORK  # noqa: E402
import json
import math
import os
import sys
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sitekit import Site, Palette  # noqa: E402

PALETTE = Palette({})
# story points nobody walks to: behind the cracked wall until the Nona breaks it, Lucia on the ceiling, the tail
# inside the doghouse, the top of the party wall the wisp crosses, the thermos lifted off the counter (a prop anchor),
# the neighbour's patio the cumbia comes from
SEALED = ('cuarto61', 'nona_flota', 'ofelia_flota', 'lucia_techo', 'cucha_cola', 'medianera', 'termo_spot', 'cumbia')

AIR = 'minecraft:air'
VEC = {'north': (0, -1), 'south': (0, 1), 'east': (1, 0), 'west': (-1, 0)}
OPP = {'north': 'south', 'south': 'north', 'east': 'west', 'west': 'east'}

# per-room wall finishes: (foot course, body [variants], top course); 1P rooms use the same 3 rows at y 5..7
FIN = {
    'living': ('pared_living_zocalo', ['pared_living'] * 11 + ['pared_living_marco'], 'pared_living_moldura'),
    'hall': ('pared_living_zocalo', ['pared_living'] * 8 + ['pared_living_marco'], 'pared_living_moldura'),
    'nona': ('empapelado_nona_zocalo', ['empapelado_nona'], 'empapelado_nona'),
    'cocina': ('pared_cocina', ['pared_cocina'], 'pared_cocina'),
    'lavadero': ('cemento_lavadero_zocalo', ['cemento_lavadero'], 'cemento_lavadero'),
    'pasillo': ('pared_pasillo_zocalo', ['pared_pasillo'] * 10 + ['pared_pasillo_rayada', 'pared_pasillo_marco'], 'pared_pasillo'),
    'lucia': ('pared_lucia_zocalo', ['pared_lucia'] * 4 + ['pared_lucia_stickers'], 'pared_lucia'),
    'toti': ('pared_toti_zocalo', ['pared_toti'] * 4 + ['pared_toti_poster'], 'pared_toti'),
    'matrimonial': ('empapelado_matrimonial_zocalo', ['empapelado_matrimonial'], 'empapelado_matrimonial'),
    'costura': ('pared_living_zocalo', ['pared_living'] * 6 + ['pared_living_marco'], 'pared_living'),
    'bano': ('azulejo_celeste_sucio', ['azulejo_celeste'] * 9 + ['azulejo_celeste_falta'], 'azulejo_celeste_guarda'),
    'sotano': ('pared_sotano_zocalo', ['pared_sotano'] * 13 + ['pared_sotano_ladrillo'], 'pared_sotano'),
    'cuarto61': ('pared_61_zocalo', ['pared_61'], 'pared_61'),
}
# finishes that read as the same paint (a single wall between them is fine)
FAMILY = {'living': 'beige', 'hall': 'beige', 'costura': 'beige'}

# ----------------------------------------------------------------------------------------- kit lookup + overwrite guard
_PREVIEW = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'blocks', 'out', 'preview_all.json')
try:
    KIND = {b['key'][5:]: b['kind'] for kit in ('casa_estructura', 'casa_muebles')
            for b in json.load(open(_PREVIEW))['kits'][kit]}
except (OSError, ValueError, KeyError):
    KIND = {}
CLASHES = []


def H(*a):
    return zlib.crc32(repr(a).encode()) % 1000


def pick(lst, *a):
    return lst[H(*a) % len(lst)] if isinstance(lst, list) else lst


def key_at(s, x, y, z):
    st = s.get(x, y, z)
    if not st or not st.startswith('deadline:casa_'):
        return None
    return st.split('[')[0][len('deadline:casa_'):]


def K(s, x, y, z, key, facing=None, replace=False, **props):
    """Places a building-kit block (key without the casa_ prefix). Overwriting a non-cube kit piece (furniture, trim,
    window, stair...) is a layout bug unless `replace` says it is meant: it is recorded in CLASHES."""
    if facing:
        props['facing'] = facing
    old = key_at(s, x, y, z)
    if old and not replace and old != key and KIND.get(old, 'cube') != 'cube':
        CLASHES.append(((x, y, z), old, key))
    s.set(x, y, z, 'casa_' + key, **props)


def stair(s, x, y, z, key, facing, half='bottom', replace=False):
    """Real stair block (walkable): `facing` = the side of the tall half = the direction the stair rises to."""
    K(s, x, y, z, key, facing, replace=replace, half=half, shape='straight', waterlogged=False)


def left_of(facing):
    """Viewer's left as he stands in front of a piece facing `facing` and looks at it (the kit's '_izq' side)."""
    fx, fz = VEC[facing]
    dx, dz = -fx, -fz
    return dz, -dx


def pair(s, x, y, z, facing, izq, der, **props):
    """Two-block piece: der at (x, z), izq next to it on the viewer's left."""
    lx, lz = left_of(facing)
    K(s, x, y, z, der, facing, **props)
    K(s, x + lx, y, z + lz, izq, facing, **props)
    return (x + lx, z + lz)


def is_air(s, x, y, z):
    st = s.get(x, y, z)
    return st is None or st == AIR


def is_wall(s, x, y, z):
    k = key_at(s, x, y, z)
    return k is not None and KIND.get(k, 'cube') == 'cube'


def yaw_to(x, z, tx, tz):
    """Marker yaw (south 0, west 90, north 180, east -90) from block (x, z) towards point (tx, tz) (block centres)."""
    return round(math.degrees(math.atan2(-(tx - x), tz - z)), 1)


def interior(boxes):
    return {(x, z) for (x1, z1, x2, z2) in boxes for x in range(x1, x2 + 1) for z in range(z1, z2 + 1)}


def ring(boxes):
    inn = interior(boxes)
    return {(x + dx, z + dz) for (x, z) in inn for dx in (-1, 0, 1) for dz in (-1, 0, 1)} - inn


class House:
    """Walls are filler cells; rooms are carved boxes that paint their own ring; openings, doors and windows cut it."""

    def __init__(self, s):
        self.s = s
        self.walls = set()
        self.rooms = []
        self.tiled = set()      # cells tiled on both faces on purpose (wet-room partitions)

    def wall(self, x1, y1, z1, x2, y2, z2, key='revoque_blanco'):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            for y in range(min(y1, y2), max(y1, y2) + 1):
                for z in range(min(z1, z2), max(z1, z2) + 1):
                    K(self.s, x, y, z, key)
                    self.walls.add((x, y, z))

    def room(self, name, fin, boxes, y0, h=3, carve=True):
        self.rooms.append((name, fin, boxes, y0, h))
        if carve:
            for (x, z) in interior(boxes):
                for y in range(y0, y0 + h):
                    self.cut(x, y, z)

    def paint(self, name):
        """Paints the wall cells around room `name` (rows y0..y0+h-1) with its finish. A ring cell the room only touches
        at a corner is left to a room that faces it."""
        _, fin, boxes, y0, h = next(r for r in self.rooms if r[0] == name)
        foot, body, top = FIN[fin]
        inn = interior(boxes)
        faced = {}
        for (n2, f2, b2, yy0, hh) in self.rooms:
            if n2 != name:
                for (x, z) in interior(b2):
                    for y in range(yy0, yy0 + hh):
                        faced[(x, y, z)] = n2
        for (x, z) in sorted(ring(boxes)):
            side = {(x + 1, z), (x - 1, z), (x, z + 1), (x, z - 1)}
            for k in range(h):
                y = y0 + k
                if (x, y, z) not in self.walls:
                    continue
                if not (side & inn) and any((cx, y, cz) in faced for (cx, cz) in side):
                    continue
                key = foot if k == 0 else (top if k == h - 1 and h > 2 else pick(body, x, y, z))
                K(self.s, x, y, z, key)

    def check_finishes(self):
        """Wall cells with rooms of different finishes on two of their faces (a single wall showing one room's paint
        to the other room)."""
        owner = {}
        for (name, fin, boxes, y0, h) in self.rooms:
            for (x, z) in interior(boxes):
                for y in range(y0, y0 + h):
                    owner[(x, y, z)] = FAMILY.get(fin, fin)
        keys = {}
        for fin, (foot, body, top) in FIN.items():
            for k in [foot, top] + list(body):
                keys.setdefault(k, set()).add(FAMILY.get(fin, fin))
        bad = []
        for (x, y, z) in sorted(self.walls):
            if (x, y, z) in self.tiled:
                continue
            fams = {owner[c] for c in ((x + 1, y, z), (x - 1, y, z), (x, y, z + 1), (x, y, z - 1)) if c in owner}
            k = key_at(self.s, x, y, z)
            if len(fams) > 1:
                bad.append(((x, y, z), sorted(fams)))
            elif len(fams) == 1 and k in keys and not (fams & keys[k]):
                bad.append(((x, y, z), [k, 'facing'] + sorted(fams)))   # painted by a room it only touches at a corner
        return bad

    def cut(self, x, y, z):
        self.s.set(x, y, z, AIR)
        self.walls.discard((x, y, z))

    def opening(self, x, y, z, h=2, sill='umbral_marmol'):
        for k in range(h):
            self.cut(x, y + k, z)
        if sill:
            K(self.s, x, y - 1, z, sill)

    def door(self, name, x, y, z, facing, key, hinge='left', open_=False, sill=True):
        self.walls.discard((x, y, z))
        self.walls.discard((x, y + 1, z))
        self.s.door(name, x, y, z, facing, mat='casa_' + key, hinge=hinge, open_=open_)
        if sill:
            K(self.s, x, y - 1, z, 'umbral_marmol')

    def window(self, x, y, z, facing, mode='open', inner=True):
        """2x2 window in the outer skin (x, z = the 'der' column, sill row y); the inner ring cell becomes a reveal."""
        lx, lz = left_of(facing)
        fx, fz = VEC[facing]
        for (cx, cz, side) in ((x, z, 'der'), (x + lx, z + lz, 'izq')):
            inf = f'ventana_inf_{side}' + ('_cerrada' if mode == 'closed' else '')
            sup = f'ventana_sup_{side}' + ('_cerrada' if mode in ('closed', 'half') else '')
            K(self.s, cx, y, cz, inf, facing)
            K(self.s, cx, y + 1, cz, sup, facing)
            self.walls.discard((cx, y, cz))
            self.walls.discard((cx, y + 1, cz))
            if inner:
                self.cut(cx - fx, y, cz - fz)
                self.cut(cx - fx, y + 1, cz - fz)
        return [(x - fx, z - fz), (x + lx - fx, z + lz - fz)]


def floor(s, x1, z1, x2, z2, y, key, worn=None, worn_p=250, replace=False):
    for x in range(min(x1, x2), max(x1, x2) + 1):
        for z in range(min(z1, z2), max(z1, z2) + 1):
            k = worn if (worn and H(x, z, y) < worn_p) else key
            K(s, x, y, z, k, replace=replace)


def ceiling(s, x1, z1, x2, z2, y, damp=()):
    for x in range(min(x1, x2), max(x1, x2) + 1):
        for z in range(min(z1, z2), max(z1, z2) + 1):
            K(s, x, y, z, 'cielorraso_humedad' if (x, z) in damp else 'cielorraso')


def trims(s, x1, z1, x2, z2, y, key):
    """Cornice / skirting run around a room's inner perimeter (pieces in the room cells, facing into the room). A piece
    goes only into air with a solid wall block behind it (not in front of a reveal, opening or window)."""
    def put(x, z, k, f, backs):
        if not is_air(s, x, y, z) or not all(is_wall(s, bx, y, bz) for (bx, bz) in backs):
            return
        K(s, x, y, z, k, f)
    for x in range(x1 + 1, x2):
        put(x, z1, key, 'south', [(x, z1 - 1)])
        put(x, z2, key, 'north', [(x, z2 + 1)])
    for z in range(z1 + 1, z2):
        put(x1, z, key, 'east', [(x1 - 1, z)])
        put(x2, z, key, 'west', [(x2 + 1, z)])
    put(x1, z1, key + '_esquina_der', 'east', [(x1 - 1, z1), (x1, z1 - 1)])
    put(x2, z1, key + '_esquina_der', 'south', [(x2 + 1, z1), (x2, z1 - 1)])
    put(x2, z2, key + '_esquina_der', 'west', [(x2 + 1, z2), (x2, z2 + 1)])
    put(x1, z2, key + '_esquina_izq', 'east', [(x1 - 1, z2), (x1, z2 + 1)])


def casings(s, x, y, z, facing):
    """Door casing pieces on the side `facing` of an opening / door cell (in the cells in front of the wall there)."""
    fx, fz = VEC[facing]
    lx, lz = left_of(facing)
    cx, cz = x + fx, z + fz
    for (px, pz, k) in ((cx + lx, cz + lz, 'contramarco_izq'), (cx - lx, cz - lz, 'contramarco_der')):
        if is_air(s, px, y + 1, pz) and is_wall(s, px - fx, y + 1, pz - fz):
            K(s, px, y + 1, pz, k, facing)
    if is_air(s, cx, y + 2, cz) and is_wall(s, x, y + 2, z):
        K(s, cx, y + 2, cz, 'contramarco_dintel', facing)


def group(s, name, *cells):
    s.markers['groups'].setdefault(name, []).extend([list(c) for c in cells])


def lamp(s, x, y, z, key, groups, lit=False, facing=None):
    """A light fixture placed lit or as its _apagado/_apagada twin, registered in the director's groups."""
    if not lit:
        key = key + ('_apagada' if key in ('lampara_pie', 'lampara_comedor', 'lampara_hongo', 'escritorio_lucia',
                                           'tele_vieja', 'parrilla', 'caldera', 'estufa') else '_apagado')
    K(s, x, y, z, key, facing)
    for g in ((groups,) if isinstance(groups, str) else groups):
        group(s, g, (x, y, z))


# ===================================================================================================== the house
PB_ROOMS = [   # (name, finish, boxes x1 z1 x2 z2)
    ('lavadero', 'lavadero', [(-7, 8, -5, 13), (-9, 8, -9, 11)]),    # + the box of the basement stair (x -9)
    ('cocina', 'cocina', [(-3, 9, 2, 13)]),
    ('hall', 'hall', [(7, 1, 9, 6)]),
    ('comedor', 'living', [(5, 8, 9, 13)]),
    ('nona', 'nona', [(-9, 1, -4, 5)]),
    ('living', 'living', [(-1, 1, 5, 6)]),
]
P1_ROOMS = [
    ('escalera', 'hall', [(9, 4, 9, 5)]),                            # the stairwell, painted like the hall below
    ('costura', 'costura', [(2, 1, 7, 4), (8, 1, 9, 2)]),            # + the nook over the entrance (balcony)
    ('matrimonial', 'matrimonial', [(-9, 1, -1, 4)]),
    ('bano', 'bano', [(6, 10, 9, 13)]),
    ('toti', 'toti', [(-1, 10, 3, 13)]),
    ('lucia', 'lucia', [(-9, 7, -4, 13)]),
    ('pasillo', 'pasillo', [(-1, 7, 9, 7), (9, 6, 9, 6)]),           # + the top step of the stair
]


def shell(s, hs):
    """Outer skin, the solid filler both storeys are carved from, slabs, floors and ceilings."""
    floor(s, -11, -1, 11, 15, -1, 'cemento_piso')                    # foundations under every wall and floor
    # outer skin y 0..8: front = cement plinth + face brick on the ground floor + white render; sides and back render
    for x in range(-11, 12):
        for z in range(-1, 16):
            if x not in (-11, 11) and z not in (-1, 15):
                continue
            for y in range(0, 9):
                if z == -1:      # face brick on the ground floor (salt bloom low down), white render upstairs
                    k = 'zocalo_ladrillo' if y == 0 else \
                        ('ladrillo_salitre' if H(x, y) < (420 if y == 1 else 90) else 'ladrillo_visto') if y <= 3 else \
                        ('revoque_chorreado' if y in (4, 8) and H(x, y, 1) < 420 else 'revoque_blanco')
                else:
                    wet = x == -11 or (z == 15 and x < 3)
                    k = ('zocalo_revoque_humedad' if wet else 'zocalo_revoque') if y == 0 else \
                        ('revoque_humedad' if wet and y == 1 else 'revoque_chorreado' if y == 8 and H(x, z) < 380 else 'revoque_blanco')
                hs.wall(x, y, z, x, y, z, k)
    for y in (0, 1, 2, 5, 6, 7):
        hs.wall(-10, y, 0, 10, y, 14, 'revoque_blanco')
    floor(s, -10, 0, 10, 14, 3, 'cielorraso')
    floor(s, -10, 0, 10, 14, 4, 'parquet', 'parquet_gastado', 220)
    floor(s, -10, 0, 10, 14, 8, 'cielorraso')


def ground_floor(s, hs):
    for (name, fin, boxes) in PB_ROOMS:
        hs.room(name, fin, boxes, 0)
    # floors and ceilings
    floor(s, -9, 1, -4, 5, -1, 'parquet', 'parquet_gastado', 200)                                  # Nona
    floor(s, -1, 1, 5, 6, -1, 'parquet')                                                           # living
    for x in range(-1, 6):
        for z in range(1, 7):
            if 0 <= x <= 4 and 2 <= z <= 5 and H(x, z, 'w') < 520:
                K(s, x, -1, z, 'parquet_gastado')                                                  # the walking path
    K(s, 4, -1, 5, 'parquet_mancha')
    floor(s, 7, 1, 9, 6, -1, 'granitico')                                                          # hall
    K(s, 7, -1, 4, 'granitico_roto')
    floor(s, 5, 8, 9, 13, -1, 'parquet', 'parquet_gastado', 260)                                   # comedor
    floor(s, -3, 9, 2, 13, -1, 'ceramica_cocina')                                                  # cocina
    floor(s, -9, 8, -5, 13, -1, 'cemento_piso')                                                    # lavadero
    ceiling(s, -9, 1, 9, 13, 3, damp={(-6, 3), (1, 1), (0, 12), (-7, 11), (7, 10)})
    for name in ('lavadero', 'cocina', 'hall', 'comedor', 'nona', 'living'):
        hs.paint(name)
    # kitchen: green tiles behind the counters (back wall), soot over the stove; the laundry partition tiled both sides
    for x in range(-3, 3):
        K(s, x, 0, 14, 'azulejo_verde_sucio' if H(x, 'k') < 400 else 'azulejo_verde')
        K(s, x, 1, 14, 'azulejo_verde_falta' if x == -2 else 'azulejo_verde')
        K(s, x, 2, 14, 'azulejo_verde_guarda')
    for y in (1, 2):
        K(s, 1, y, 14, 'pared_cocina_hollin')
    for z in range(8, 14):
        K(s, -4, 0, z, 'azulejo_verde_sucio')
        K(s, -4, 1, z, 'azulejo_verde_falta' if z == 9 else 'azulejo_verde')
        K(s, -4, 2, z, 'azulejo_verde_guarda')
        hs.tiled |= {(-4, y, z) for y in (0, 1, 2)}
    for x in (-7, -5):                          # the laundry tub corner: tiles behind it
        K(s, x, 0, 14, 'azulejo_verde_sucio')
        K(s, x, 1, 14, 'azulejo_verde')
        K(s, x, 2, 14, 'azulejo_verde_guarda')

    # ---------------------------------------------------------------- stair to the 1P (x=9, rising south)
    for z in range(2, 7):                       # the stairwell through the ceiling and the 1P floor (headroom)
        s.set(9, 3, z, AIR)
    for z in range(3, 6):
        s.set(9, 4, z, AIR)
    for k in range(5):
        z = 2 + k
        stair(s, 9, k, z, 'escalera_madera', 'south', replace=True)
        for y in range(0, k):
            K(s, 9, y, z, 'pared_living')
        if k <= 3:
            K(s, 9, k + 1, z, 'baranda_escalera_der', 'north')
    for (y, z) in ((1, 2), (2, 2), (2, 3)):    # invisible rail on the hall side of the low steps (the baranda has none)
        K(s, 8, y, z, 'tope_frente', 'east')

    # ---------------------------------------------------------------- openings and doors
    hs.door('entrada', 8, 0, 0, 'south', 'puerta_entrada', hinge='right')
    hs.opening(8, 0, -1, sill='granitico')      # the outer skin is open in front of it: a recessed entrance
    hs.opening(6, 0, 3)                         # hall -> living
    casings(s, 6, 0, 3, 'west')
    casings(s, 6, 0, 3, 'east')
    hs.door('nona', -3, 0, 3, 'west', 'puerta_nona', hinge='left')
    hs.opening(-2, 0, 3)                        # (the living's layer of the double wall)
    casings(s, -3, 0, 3, 'west')
    casings(s, -2, 0, 3, 'east')
    hs.opening(-1, 0, 7)                        # living -> kitchen, through both layers
    hs.opening(-1, 0, 8)
    casings(s, -1, 0, 7, 'north')
    casings(s, -1, 0, 8, 'south')
    hs.opening(5, 0, 7)                         # living -> dining room
    casings(s, 5, 0, 7, 'north')
    casings(s, 5, 0, 7, 'south')
    hs.opening(8, 0, 7)                         # hall -> dining room
    casings(s, 8, 0, 7, 'south')
    casings(s, 8, 0, 7, 'north')
    hs.opening(3, 0, 10)                        # kitchen -> dining room
    hs.opening(4, 0, 10)
    casings(s, 3, 0, 10, 'west')
    casings(s, 4, 0, 10, 'east')
    hs.opening(-4, 0, 11)                       # kitchen -> laundry (one tiled wall)
    casings(s, -4, 0, 11, 'east')
    casings(s, -4, 0, 11, 'west')
    hs.door('cocina', 2, 0, 14, 'south', 'puerta_cocina', hinge='left')
    hs.opening(2, 0, 15, sill='cemento_piso')
    hs.door('lavadero', -6, 0, 14, 'south', 'puerta_lavadero', hinge='right', sill=False)
    hs.opening(-6, 0, 15, sill=None)

    # ---------------------------------------------------------------- windows
    hs.window(-6, 1, -1, 'north', 'half')       # Nona, street
    hs.window(-11, 1, 4, 'west', 'closed')      # Nona, side passage
    hs.window(2, 1, -1, 'north', 'half')        # living, street
    hs.window(6, 1, 15, 'south', 'open')        # comedor: the window over the patio (ventana_fondo), the cucha in view
    hs.window(11, 1, 10, 'east', 'closed')      # comedor, driveway
    for (x, side) in ((0, 'der'), (-1, 'izq')):  # kitchen window over the counter (facing south: der at the higher x)
        K(s, x, 1, 15, f'ventana_cocina_{side}' + ('_abierta' if side == 'izq' else ''), 'south')
        hs.walls.discard((x, 1, 15))
        hs.cut(x, 1, 14)
    hs.window(11, 3, 4, 'east', 'open')         # stair window, halfway up

    # ---------------------------------------------------------------- the laundry and the basement stair (x=-9)
    hs.door('sotano', -8, 0, 8, 'west', 'puerta_sotano', hinge='left')


def first_floor(s, hs):
    for (name, fin, boxes) in P1_ROOMS:
        hs.room(name, fin, boxes, 5)
    # floors
    floor(s, -1, 7, 9, 7, 4, 'parquet', 'parquet_gastado', 380, replace=True)
    floor(s, -9, 1, -1, 4, 4, 'parquet', 'parquet_gastado', 180)
    floor(s, 2, 1, 7, 4, 4, 'parquet', 'parquet_gastado', 300)
    floor(s, -9, 7, -4, 13, 4, 'parquet', 'parquet_mancha', 40)
    floor(s, -1, 10, 3, 13, 4, 'parquet', 'parquet_gastado', 450)
    floor(s, 6, 10, 9, 13, 4, 'piso_bano')
    ceiling(s, -9, 1, 9, 13, 8, damp={(1, 7), (6, 7), (7, 12), (-8, 3), (-5, 12)})
    for name in ('escalera', 'costura', 'matrimonial', 'bano', 'toti', 'lucia', 'pasillo'):
        hs.paint(name)
    # doors in a row along the corridor (the cascade, from the far end towards the stair); each door sits in the
    # room's layer of the double wall, the corridor's layer is a reveal
    hs.door('lucia', -3, 5, 7, 'west', 'puerta_lucia', hinge='left')
    hs.opening(-2, 5, 7)
    casings(s, -3, 5, 7, 'west')
    for (name, x, z, f, key, hinge) in (('matrimonial', -1, 5, 'north', 'puerta_placa', 'right'),
                                        ('toti', 2, 9, 'south', 'puerta_toti', 'left'),
                                        ('costura', 5, 5, 'north', 'puerta_placa_blanca', 'right'),
                                        ('bano', 8, 9, 'south', 'puerta_bano', 'left')):
        hs.door(name, x, 5, z, f, key, hinge=hinge)
        fx, fz = VEC[f]
        hs.opening(x, 5, z - fz)
        casings(s, x, 5, z, f)
        casings(s, x, 5, z - fz, OPP[f])
    group(s, 'puertas_cascada', (-3, 5, 7), (-1, 5, 5), (2, 5, 9), (5, 5, 5), (8, 5, 9))
    # windows
    hs.window(-6, 6, -1, 'north', 'half')       # matrimonial
    hs.window(-3, 6, -1, 'north', 'closed')
    hs.window(2, 6, -1, 'north', 'closed')      # costura (over the living window)
    hs.window(8, 5, -1, 'north', 'open')        # costura: French window onto the balcony over the entrance
    hs.window(11, 6, 6, 'east', 'half')         # top of the stair / end of the corridor
    hs.window(-4, 5, 15, 'south', 'open')       # Lucia: French window down to the floor, the cucha is out there
    hs.window(-11, 6, 9, 'west', 'closed')      # Lucia, side
    hs.window(0, 6, 15, 'south', 'half')        # Toti
    K(s, 8, 7, 15, 'ventana_bano', 'south')     # bathroom tilt window over the tub
    hs.walls.discard((8, 7, 15))
    hs.cut(8, 7, 14)


def roof(s, hs):
    """Gable roof over the outer skin (x -11..11, z -1..15): eaves at y=9, ridge row z=7 at y=17; a brick chimney over
    the living, a vent in each gable, downpipes at the four corners."""
    def yroof(z):
        return 9 + (z + 1) if z <= 7 else 9 + (15 - z)
    for x in range(-11, 12):
        for z in range(-1, 16):
            y = yroof(z)
            end = x in (-11, 11)
            brick = '_ladrillo' if x == 11 else ''      # the gable over the driveway is in face brick, like the front
            if z == 7:
                k = ('hastial_cumbrera_der' if x == -11 else f'hastial{brick}_cumbrera_izq') if end else 'techo_cumbrera'
                K(s, x, y, z, k, 'north')
                continue
            front = z < 7
            f = 'north' if front else 'south'
            eave = z in (-1, 15)
            if end:
                side = ('der' if x == -11 else 'izq') if front else ('izq' if x == -11 else 'der')
                k = f'hastial{brick}_alero_{side}' if eave else f'hastial{brick}_{side}'
            else:
                mossy = H(x, z, 'r') < (380 if not front else 160)
                k = ('techo_alero_musgo' if mossy else 'techo_alero') if eave else ('techo_musgo' if mossy else 'techo')
                if (x, z) in ((-4, 3), (6, 11)):
                    k = 'techo_roto'
            K(s, x, y, z, k, f)
        if x in (-11, 11):
            for z in range(0, 15):
                for y in range(9, yroof(z)):
                    if x == 11:
                        hs.wall(x, y, z, x, y, z, 'ladrillo_salitre' if H(x, y, z) < 90 else 'ladrillo_visto')
                    else:
                        hs.wall(x, y, z, x, y, z, 'revoque_chorreado' if y == 9 and H(x, z) < 400 else 'revoque_blanco')
    # chimney stack of the old living fireplace, through the front slope and past the ridge, with its rain cap
    for y in range(yroof(4), 18):
        K(s, 4, y, 4, 'ladrillo_salitre' if y == yroof(4) else 'ladrillo_visto', replace=True)
    K(s, 4, 18, 4, 'parrilla_chimenea', 'north')
    for x, f in ((-12, 'west'), (12, 'east')):  # attic vents in the gables
        K(s, x, 13, 7, 'rejilla', f)
    # downpipes: front corners from the eave to the ground, back corners down onto the gallery roof
    for x in (-10, 10):
        K(s, x, 8, -2, 'bajada_codo', 'north')
        for y in range(1, 8):
            K(s, x, y, -2, 'bajada', 'north')
        K(s, x, 0, -2, 'bajada_pie', 'north')
        K(s, x, 8, 16, 'bajada_codo', 'south')
        for y in range(5, 8):
            K(s, x, y, 16, 'bajada', 'south')


def porch_and_gallery(s):
    """The balcony slab over the front door (the porch canopy, with the costura's Juliet railing on it), a plaster band
    course over the brick base, and the back GALERIA: brick piers 3 high carrying a lean-to tile roof."""
    for x in (7, 8, 9):
        K(s, x, 4, -2, 'granitico')             # terrazzo on top, plaster underneath
    K(s, 7, 5, -2, 'baranda_poste', 'north')
    for x in (8, 9):
        K(s, x, 5, -2, 'baranda', 'north')
    for x in range(-11, 12):                    # band course capping the face brick
        if x not in (-10, 10):
            K(s, x, 3, -2, 'cornisa', 'north')
    for x in range(-11, 12):
        K(s, x, 3, 17, 'techo_alero_musgo' if H(x, 'ga') < 300 else 'techo_alero', 'south')
        K(s, x, 4, 16, 'techo_musgo' if H(x, 'gb') < 200 else 'techo', 'south')
    for x in (-11, -7, -3, 3, 7, 11):           # clear of the sightlines from the kitchen and dining-room windows
        for y in (0, 1, 2):
            K(s, x, y, 17, 'pilar', 'south')
    for x in (-11, 11):                         # the gallery gutter's downpipes
        K(s, x, 2, 18, 'bajada_codo', 'south')
        K(s, x, 1, 18, 'bajada', 'south')
        K(s, x, 0, 18, 'bajada_pie', 'south')


def basement(s, hs):
    """Basement 15x9 (x -9..5, z 5..13) under the laundry and kitchen; the sealed 1961 room (x -9..-1, z -5..2) behind a
    double wall: the basement's plaster layer at z=4 (with the crack), the 1961 lime wash layer at z=3."""
    for x in range(-10, 7):
        for z in range(4, 15):
            for y in range(-6, -1):
                edge = x in (-10, 6) or z in (4, 14)
                if y == -6:
                    K(s, x, y, z, 'cemento_piso')
                elif y == -2:
                    K(s, x, y, z, 'losa_sotano')
                elif edge:
                    hs.wall(x, y, z, x, y, z, 'pared_sotano')
                else:
                    s.set(x, y, z, AIR)
    for x in range(-10, 1):
        for z in range(-6, 4):
            for y in range(-7, -1):
                edge = x in (-10, 0) or z in (-6, 3)
                if y == -7:
                    K(s, x, y, z, 'arena_pisadas' if H(x, z) < 160 else 'arena')
                elif y == -2:
                    K(s, x, y, z, 'losa_sotano')
                elif edge:
                    hs.wall(x, y, z, x, y, z, 'pared_61')
                else:
                    s.set(x, y, z, AIR)
    hs.room('sotano', 'sotano', [(-9, 5, 5, 13)], -5, carve=False)
    hs.room('cuarto61', 'cuarto61', [(-9, -5, -1, 2)], -6, h=4, carve=False)
    hs.paint('sotano')
    hs.paint('cuarto61')
    for (x, z) in ((-4, 1), (-4, 2), (-5, 2), (-6, 1), (-5, 0), (-4, -2)):
        K(s, x, -7, z, 'arena_arrastre')          # drag marks from the bed to the wall
    for y, k in ((-5, 'pared_sotano_grieta_abajo'), (-4, 'pared_sotano_grieta'), (-3, 'pared_sotano_grieta_arriba')):
        K(s, -5, y, 4, k)                       # the crack (its back is hidden by the 1961 layer)
    for x in (-5, -4):                          # a cement step in the 1961 layer, under the future hole
        stair(s, x, -6, 3, 'escalera_cemento', 'south')
        hs.walls.discard((x, -6, 3))
    # stair down from the laundry along x=-9 (descending south), top step level with the laundry floor
    for k in range(5):
        y, z = -1 - k, 8 + k
        stair(s, -9, y, z, 'escalera_cemento', 'north', replace=True)
        for yy in range(-5, y):
            K(s, -9, yy, z, 'pared_sotano')
        for yy in range(y + 1, y + 4):
            if yy <= -2 or (yy <= 2 and z <= 11):
                s.set(-9, yy, z, AIR)
                hs.walls.discard((-9, yy, z))
        if k > 0:
            K(s, -9, y + 1, z, 'pasamanos_izq', 'south')
    s.set(-9, -2, 12, AIR)
    # a moonlight shaft: the basement ventiluz high on the back wall, a lit pocket behind it
    K(s, -1, -3, 14, 'ventana_sotano', 'south')
    hs.walls.discard((-1, -3, 14))
    s.light(-1, -3, 15, 7, 'sotano_luna')


# ===================================================================================================== furniture
def tall(s, x, y, z, key, facing, cap='tope'):
    """A ~2 m single-block piece plus the invisible collision cap in the block above (same facing)."""
    K(s, x, y, z, key, facing)
    K(s, x, y + 1, z, cap, facing)


def furnish_pb(s):
    # ---------------------------------------------------------------- LIVING (x -1..5, z 1..6): sofa under the street
    # window facing the CRT on the back wall, Jorge's armchair, the Nona's rocker facing the novela, the photo wall,
    # the damp stain of 'es la humedad', the floor lamp lit, the ceiling lamp off
    for x, k in ((3, 'sillon_der'), (2, 'sillon_centro'), (1, 'sillon_izq')):
        K(s, x, 0, 1, k, 'south')
    for x, k in ((2, 'cortina_floreada_izq'), (3, 'cortina_floreada_der')):
        K(s, x, 1, 1, k, 'south')
    K(s, 2, 0, 2, 'mesa_ratona', 'south')
    K(s, 0, 0, 3, 'alfombra_punta', 'west')     # a short runner between the coffee table and the rocker
    for x in (1, 2):
        K(s, x, 0, 3, 'alfombra', 'east')
    K(s, 3, 0, 3, 'alfombra_punta', 'east')
    tall(s, 1, 0, 6, 'tele_vieja', 'north')
    group(s, 'tv', (1, 0, 6))
    K(s, 0, 0, 6, 'enchufe', 'north')
    K(s, -1, 0, 5, 'sillon_individual', 'east')
    K(s, 2, 0, 4, 'mecedora', 'south')
    tall(s, -1, 0, 1, 'lampara_pie', 'south')
    group(s, 'luces_pb', (-1, 0, 1))
    group(s, 'luces_living', (-1, 0, 1))
    lamp(s, 2, 2, 3, 'lampara_comedor', ('luces_pb', 'luces_living'))
    lamp(s, 5, 0, 5, 'estufa', 'estufa', facing='west')
    K(s, 5, 0, 1, 'mesita_auxiliar', 'west')
    K(s, 5, 1, 1, 'carpetita_florero', 'west')
    K(s, 4, 0, 1, 'mancha_humedad', 'south')
    K(s, 5, 1, 6, 'llave_luz', 'west')
    for (x, y, z, k, f) in ((-1, 1, 5, 'foto_choripan', 'east'), (2, 1, 6, 'foto_familia', 'north'),
                            (3, 1, 6, 'foto_cumple', 'north')):
        K(s, x, y, z, k, f)
    # ---------------------------------------------------------------- HALL (x 7..8) and the stair
    K(s, 7, 1, 1, 'llave_luz', 'east')
    K(s, 7, 0, 5, 'mesita_auxiliar', 'east')
    K(s, 7, 1, 5, 'telefono', 'east')
    K(s, 9, 1, 1, 'perchero_bata', 'west')
    lamp(s, 8, 2, 4, 'plafon', 'luces_pb')
    # ---------------------------------------------------------------- NONA (x -9..-4, z 1..5): the bed, the home altar
    # with its candles (the only light always on), the rocker facing it, the wool basket, the walker, the wardrobe
    K(s, -8, 0, 5, 'cama_nona_cabecera', 'north')
    K(s, -8, 0, 4, 'cama_nona_pie', 'north')
    K(s, -8, 1, 6, 'empapelado_nona_cruz')       # the ghost of a crucifix over the bed
    K(s, -9, 0, 5, 'mesa_luz_nona', 'north')
    K(s, -7, 0, 5, 'mesa_luz', 'north')
    K(s, -7, 1, 5, 'lata_galletitas', 'north')
    K(s, -6, 1, 5, 'foto_nona_joven', 'north')
    K(s, -7, 0, 4, 'pantuflas', 'north')
    K(s, -5, 0, 5, 'ropero_abajo', 'north')
    K(s, -5, 1, 5, 'ropero_arriba', 'north')
    K(s, -8, 0, 1, 'altar', 'south')
    K(s, -8, 1, 1, 'altar_estampitas', 'south')
    group(s, 'altar_velas', (-8, 0, 1))
    K(s, -8, 0, 3, 'mecedora', 'north')
    K(s, -9, 0, 3, 'canasta_lana', 'east')
    K(s, -7, 0, 3, 'andador', 'north')
    K(s, -9, 0, 1, 'mesita_auxiliar', 'east')
    K(s, -9, 1, 1, 'mate_termo_mesa', 'east')
    lamp(s, -6, 2, 3, 'plafon', 'luces_pb')
    for x, k in ((-6, 'cortina_floreada_izq'), (-5, 'cortina_floreada_der')):
        K(s, x, 1, 1, k, 'south')
    for z, k in ((3, 'cortina_floreada_der'), (4, 'cortina_floreada_izq')):
        K(s, -9, 1, z, k, 'east')
    # ---------------------------------------------------------------- COMEDOR (x 5..9, z 8..13): the long lustred table
    # with its 8 chairs, the sideboard with the plates, the brass lamp, the Last Supper at eye level
    K(s, 7, 0, 9, 'mesa_comedor_extremo', 'east')     # the table runs north-south: an aisle on both sides
    K(s, 7, 0, 10, 'mesa_comedor_centro', 'east')
    K(s, 7, 0, 11, 'mesa_comedor_extremo', 'west')
    sillas = []
    for z in (9, 10, 11):
        K(s, 6, 0, z, 'silla_comedor', 'east')
        K(s, 8, 0, z, 'silla_comedor', 'west')
        sillas += [(6, 0, z), (8, 0, z)]
    K(s, 7, 0, 8, 'silla_comedor', 'south')
    K(s, 7, 0, 12, 'silla_comedor', 'north')
    sillas += [(7, 0, 8), (7, 0, 12)]
    group(s, 'comedor_sillas', *sillas)
    pair(s, 8, 0, 13, 'north', 'aparador_izq', 'aparador_der')     # the sideboard on the back wall, by the window
    for x in (8, 9):
        K(s, x, 1, 13, 'tope_fondo', 'north')
    K(s, 5, 1, 12, 'cuadro_ultima_cena', 'east')
    lamp(s, 7, 2, 10, 'lampara_comedor', 'luces_pb')
    for z in (10, 11):
        K(s, 9, 1, z, 'visillo', 'west')
    K(s, 5, 0, 13, 'maceta_malvones', 'north')
    # ---------------------------------------------------------------- COCINA (x -3..2, z 9..13): counters under the
    # window over the patio, the old fridge, mate and thermos, bread box, dish rack, cupboards, the table, the 3:33 clock
    K(s, -3, 0, 13, 'heladera_abajo', 'north')
    K(s, -3, 1, 13, 'heladera_arriba', 'north')
    K(s, -2, 0, 13, 'mesada_cajones', 'north')
    K(s, -1, 0, 13, 'mesada_pileta', 'north')
    K(s, 0, 0, 13, 'mesada', 'north')
    K(s, 1, 0, 13, 'cocina_gas_pava', 'north')
    K(s, -2, 1, 13, 'panera', 'north')
    K(s, -1, 1, 13, 'escurridor', 'north')
    K(s, 0, 1, 13, 'mate_termo', 'north')
    for (x, y, z, f) in ((-2, 2, 13, 'north'), (1, 2, 13, 'north'), (-3, 2, 12, 'east')):
        K(s, x, y, z, 'alacena', f)
        group(s, 'alacenas', (x, y, z))
    for x in (-1, 0):
        K(s, x, 0, 11, 'mesa_cocina', 'north')
    for (x, z, f) in ((-2, 11, 'east'), (1, 11, 'west'), (-1, 10, 'south'), (0, 10, 'south')):
        K(s, x, 0, z, 'silla_cocina', f)
    K(s, -1, 1, 11, 'plato', 'north')
    lamp(s, -1, 2, 11, 'tubo', 'luces_cocina')
    K(s, 1, 2, 9, 'reloj_cocina_333', 'south')    # the only clock in the house
    K(s, -3, 1, 9, 'almanaque', 'east')
    K(s, 1, 0, 9, 'tacho_basura', 'south')
    K(s, 2, 1, 12, 'llave_luz', 'west')
    # ---------------------------------------------------------------- LAVADERO (x -7..-5 + the basement stair box)
    K(s, -6, 1, 8, 'tablero', 'south')
    group(s, 'tablero', (-6, 1, 8))
    K(s, -5, 1, 8, 'medidor_luz', 'south')
    K(s, -5, 0, 13, 'pileta_lavar', 'north')
    K(s, -7, 0, 13, 'balde_secador', 'north')
    tall(s, -7, 0, 10, 'estante_lavadero', 'east', 'tope_fondo')
    tall(s, -7, 0, 11, 'estante_herramientas', 'east', 'tope_fondo')
    K(s, -5, 0, 9, 'cajon_cerveza', 'west')
    K(s, -7, 0, 12, 'bolsa_carbon', 'east')
    for x, k in ((-7, 'soga'), (-6, 'ropa_tendida'), (-5, 'soga')):    # washing hung indoors, over head height
        K(s, x, 1, 9, k, 'north')
    lamp(s, -6, 2, 10, 'tubo', 'luces_pb')


def furnish_1p(s):
    # ---------------------------------------------------------------- corridor: a 1 m red runner, a lamp every 4,
    # the family photo with Ofelia, the crucifix, the light switch
    K(s, -1, 5, 7, 'alfombra_punta', 'west')
    for x in range(0, 9):
        K(s, x, 5, 7, 'alfombra_mancha' if x == 4 else 'alfombra', 'east')
    K(s, 9, 5, 7, 'alfombra_punta', 'east')
    for x in (0, 4, 9):
        lamp(s, x, 7, 7, 'plafon', 'pasillo_1p_luces')
    K(s, -1, 6, 7, 'foto_familia_ofelia', 'north')
    K(s, 2, 6, 7, 'crucifijo', 'south')
    K(s, 5, 6, 7, 'llave_luz', 'north')
    K(s, 9, 5, 5, 'mancha_humedad_cara', 'west')   # a face in the damp, on the stairwell wall as you come up
    # ---------------------------------------------------------------- MATRIMONIAL (x -9..-1, z 1..4)
    pair(s, -9, 5, 2, 'east', 'cama_matrimonial_cabecera_izq', 'cama_matrimonial_cabecera_der')
    pair(s, -8, 5, 2, 'east', 'cama_matrimonial_pie_izq', 'cama_matrimonial_pie_der')
    K(s, -9, 5, 1, 'mesa_luz', 'east')
    lamp(s, -9, 6, 1, 'velador', 'luces_1p', facing='east')
    K(s, -9, 5, 4, 'mesa_luz', 'east')
    lamp(s, -9, 6, 4, 'velador', 'luces_1p', facing='east')
    K(s, -9, 7, 2, 'foto_casamiento', 'east')      # the wedding photo over the bed
    pair(s, -6, 5, 4, 'north', 'comoda_izq', 'comoda_der')
    for x in (-6, -5):
        K(s, x, 6, 4, 'tope_fondo', 'north')
    pair(s, -1, 5, 2, 'west', 'placard_cerrado_izq', 'placard_cerrado_der')
    pair(s, -1, 6, 2, 'west', 'tope_frente', 'tope_frente')
    pair(s, -1, 7, 2, 'west', 'placard_maletero_izq', 'placard_maletero_der')
    K(s, -7, 5, 4, 'pantuflas', 'south')
    K(s, -4, 5, 1, 'ropa_tirada', 'south')
    K(s, -5, 7, 2, 'roseton')
    for x in (-6, -5, -3, -2):
        K(s, x, 6, 1, 'visillo', 'south')
    # ---------------------------------------------------------------- COSTURA (x 2..7, z 1..4 + the balcony nook): the
    # Nona's sewing room, where everything that has no place ends up
    K(s, 2, 5, 4, 'ropero_abajo', 'east')
    K(s, 2, 6, 4, 'ropero_arriba', 'east')
    K(s, 2, 5, 3, 'tapado_sillon', 'east')
    K(s, 3, 5, 1, 'cajas_apiladas', 'south')
    K(s, 6, 5, 1, 'caja_abierta', 'south')
    K(s, 7, 5, 1, 'ropa_tirada', 'west')
    K(s, 4, 5, 2, 'tapado_mesa', 'north')
    K(s, 4, 5, 3, 'silla_comedor', 'north')
    K(s, 7, 5, 3, 'sillas_apiladas', 'west')
    tall(s, 7, 5, 4, 'tapado_espejo', 'west')
    K(s, 6, 5, 3, 'plato_roto', 'north')
    K(s, 3, 5, 4, 'ropa_tirada', 'north')
    K(s, 9, 5, 2, 'maceta_malvones', 'west')
    lamp(s, 4, 7, 2, 'plafon', 'luces_1p')
    # ---------------------------------------------------------------- LUCIA (x -9..-4, z 7..13): the canopy bed on the
    # west wall, the doll shelves on the east wall (you cannot watch both), the desk with the tablet, a clear middle
    K(s, -9, 5, 7, 'ropero_abajo', 'south')
    K(s, -9, 6, 7, 'ropero_arriba', 'south')
    K(s, -7, 5, 7, 'escritorio_lucia_apagada', 'south')
    group(s, 'tablet', (-7, 5, 7))
    K(s, -8, 5, 8, 'silla_nena', 'north')
    K(s, -6, 5, 7, 'cuaderno_lemaza', 'south')
    K(s, -6, 6, 7, 'dibujo_lemaza', 'south')
    K(s, -9, 5, 8, 'baul_juguetes', 'east')
    K(s, -9, 5, 10, 'mesa_luz', 'east')
    lamp(s, -9, 6, 10, 'lampara_hongo', 'luces_1p', facing='east')
    for (x, k) in ((-9, 'cama_dosel_cabecera'), (-8, 'cama_dosel_pie')):
        tall(s, x, 5, 11, k, 'east')
    shelves = []
    for z, k in ((10, 'estante_munecas_1'), (11, 'estante_munecas_2'), (12, 'estante_munecas_3')):
        tall(s, -4, 5, z, k, 'west', 'tope_fondo')
        shelves.append((-4, 5, z))
    group(s, 'estante_munecas', *shelves)
    for (x, z, f) in ((-7, 10, 'north'), (-6, 10, 'east'), (-7, 11, 'west'), (-6, 11, 'south')):
        K(s, x, 5, z, 'alfombra_lucia', f)
    K(s, -9, 5, 13, 'juguetes', 'north')
    K(s, -8, 5, 13, 'mochila', 'north')
    lamp(s, -6, 7, 10, 'plafon', 'luces_1p')
    for x, k in ((-4, 'cortina_rosa_der'), (-5, 'cortina_rosa_izq')):
        K(s, x, 5, 13, k, 'north')
    # ---------------------------------------------------------------- TOTI (x -1..3, z 10..13): the gaming desk (the RGB
    # PC stays on: the only glow under a door), the unmade bed, posters, and the walk-in PLACARD on the back wall
    pair(s, 0, 5, 10, 'south', 'escritorio_pc_izq', 'escritorio_pc_der')
    group(s, 'toti_pc', (-1, 5, 10), (0, 5, 10))
    K(s, 0, 5, 11, 'silla_gamer', 'north')
    K(s, -1, 5, 13, 'cama_toti_cabecera', 'north')
    K(s, -1, 5, 12, 'cama_toti_pie', 'north')
    # placard 2 wide, 2 deep: doors in the room row z=12 (left leaf = east), the hanging space z=13, the backs in the
    # outer ring (z=14); the clothes hang into z=13 only, so a player in the door cells has a clear view
    s.door('placard', 2, 5, 12, 'south', mat='casa_placard_puerta', hinge='right')
    s.door('placard_2', 3, 5, 12, 'south', mat='casa_placard_puerta', hinge='left')
    pair(s, 2, 7, 12, 'north', 'placard_maletero_izq', 'placard_maletero_der')
    pair(s, 2, 5, 14, 'north', 'placard_fondo_izq', 'placard_fondo_der', replace=True)
    for x in (2, 3):
        K(s, x, 7, 13, 'machimbre')
    for z in (12, 13):                          # the wardrobe is built into an alcove: a side wall on its west
        for y in (5, 6, 7):
            K(s, 1, y, z, FIN['toti'][0] if y == 5 else 'pared_toti')
    for (x, y, z, k, f) in ((-1, 6, 11, 'poster_toti_1', 'east'), (-1, 7, 12, 'poster_toti_3', 'east'),
                            (-1, 7, 10, 'poster_toti_4', 'south'), (0, 7, 10, 'poster_banda', 'south'),
                            (3, 7, 11, 'poster_toti_2', 'west'),
                            (0, 6, 12, 'poster_juego', 'west')):
        K(s, x, y, z, k, f)
    K(s, 0, 5, 12, 'zapatillas', 'north')
    K(s, 0, 5, 13, 'ropa_tirada', 'north')
    K(s, -1, 5, 11, 'cargador', 'east')
    lamp(s, 1, 7, 12, 'plafon', 'luces_1p')
    # ---------------------------------------------------------------- BANO (x 6..9, z 10..13)
    pair(s, 8, 5, 13, 'north', 'banadera_izq', 'banadera_der')
    K(s, 8, 6, 13, 'cortina_ducha_silueta', 'north')
    K(s, 9, 6, 13, 'cortina_ducha_corrida', 'north')
    K(s, 9, 7, 13, 'ducha', 'north')
    K(s, 9, 5, 11, 'inodoro', 'west')
    K(s, 9, 5, 12, 'bidet', 'west')
    K(s, 9, 6, 11, 'portarrollo', 'west')
    K(s, 6, 5, 11, 'lavatorio', 'east')
    K(s, 6, 6, 11, 'botiquin', 'east')
    lamp(s, 6, 7, 11, 'aplique_bano', 'luces_1p', facing='east')
    K(s, 6, 6, 12, 'toallero', 'east')
    K(s, 7, 5, 12, 'alfombra_bano', 'north')
    lamp(s, 7, 7, 12, 'plafon', 'luces_1p')


def furnish_basement(s):
    # ---------------------------------------------------------------- SOTANO: sheeted furniture in the middle (aisles
    # around it), the Nona's preserves, the boiler with its blue pilot and flue, bare bulbs on cords, the Christmas boxes
    lamp(s, -3, -3, 9, 'foco', 'sotano_foco')
    lamp(s, 3, -3, 9, 'foco', 'sotano_foco')
    tall(s, 5, -5, 13, 'caldera', 'west')
    K(s, 5, -3, 13, 'bajada', 'west')            # the boiler flue up to the slab
    K(s, 5, -5, 12, 'damajuana', 'west')
    tall(s, -9, -5, 5, 'estante_frascos', 'east', 'tope_fondo')
    tall(s, -9, -5, 6, 'estante_frascos_2', 'east', 'tope_fondo')
    K(s, -8, -5, 5, 'damajuana', 'east')
    K(s, 0, -5, 9, 'tapado_mesa', 'north')
    K(s, -1, -5, 9, 'tapado_sillon', 'east')
    K(s, 1, -5, 10, 'tapado_figura', 'west')
    tall(s, 0, -5, 11, 'tapado_ropero', 'south')
    tall(s, 2, -5, 7, 'tapado_espejo', 'west')
    K(s, -2, -5, 11, 'tapado_sillon', 'north')
    K(s, 4, -5, 5, 'cajas_apiladas', 'south')
    K(s, 5, -5, 5, 'caja_abierta', 'west')
    K(s, 3, -5, 12, 'cajas_apiladas', 'north')
    K(s, -7, -5, 13, 'balde_secador', 'north')
    tall(s, 5, -5, 9, 'estante_herramientas', 'west', 'tope_fondo')
    K(s, -6, -5, 13, 'caja_abierta', 'north')
    K(s, 0, -5, 5, 'sillas_apiladas', 'south')
    K(s, -4, -5, 13, 'bolsa_carbon', 'north')
    K(s, -3, -5, 13, 'bolsa_carbon_volcada', 'north')
    K(s, 4, -5, 13, 'damajuana', 'north')
    # ---------------------------------------------------------------- the sealed 1961 room: the old salt circle round
    # the iron bed, melted candles, the stole on a nail, scratches, soot
    cx, cz = -4, 0
    for p, (i, j) in {'a': (0, 2), 'b': (1, 2), 'c': (2, 2), 'd': (2, 1), 'e': (2, 0), 'f': (1, 1)}.items():
        for (x, z, f) in ((cx + i, cz + j, 'north'), (cx - 1 - j, cz + i, 'east'), (cx - 1 - i, cz - 1 - j, 'south'),
                          (cx + j, cz - 1 - i, 'west')):
            K(s, x, -6, z, 'sal_61_a_rota' if (p, f) == ('a', 'north') else f'sal_61_{p}', f)
    K(s, -5, -6, -1, 'cama_hierro_cabecera', 'south')
    K(s, -5, -6, 0, 'cama_hierro_pie', 'south')
    velas = [(-4, -6, -2), (-6, -6, -1), (-3, -6, 0), (-4, -6, 1), (-1, -6, 2)]
    for (x, y, z) in velas[:4]:
        K(s, x, y, z, 'velas_derretidas_apagadas', 'north')
    K(s, -1, -6, 2, 'velas_sueltas_apagadas', 'west')
    group(s, 'cuarto61_velas', *velas)
    for y, k in ((-6, 'pared_61_hollin'), (-5, 'pared_61_hollin_alto'), (-4, 'pared_61_hollin_alto')):
        K(s, 0, y, 2, k)
    K(s, -9, -5, -3, 'estola_anselmo', 'east')
    K(s, -9, -6, 1, 'rayones_latin', 'east')
    group(s, 'rayones', (-9, -6, 1))
    K(s, -1, -6, -1, 'rayones_lemaza', 'west')
    K(s, -1, -6, -4, 'rayones_lemaza_chico', 'west')
    K(s, -3, -6, -5, 'rayones_lemaza_chico', 'south')
    K(s, -6, -6, -5, 'rayones_dibujo', 'south')
    K(s, -8, -6, -5, 'rayones_palitos', 'south')
    K(s, -8, -6, 2, 'manos_hollin', 'north')
    K(s, -1, -5, 1, 'manos_hollin', 'west')
    K(s, -8, -6, 1, 'lata_galletitas_vieja', 'east')
    K(s, -8, -6, -2, 'zapatitos', 'east')
    K(s, -4, -6, -1, 'misal', 'north')


# ===================================================================================================== outside
LOT_X0, LOT_X1, LOT_Z0, LOT_Z1 = -18, 17, -4, 34      # inside the boundary walls (36 x 39 + the fence row)
SALT_PIECES = {'a': (0, 2), 'b': (1, 2), 'c': (2, 2), 'd': (2, 1), 'e': (2, 0), 'f': (1, 1)}
CUCHA = (2, 24)                                         # Choripan's doghouse, in view of the comedor, kitchen and Lucia's windows
POOL = (-11, -6, 27, 30)                                # pelopincho x0, x1, z0, z1


def salt_cells(cx, cz):
    """(x, z, piece, facing) of an r~3 salt circle centred on the block corner (cx, cz) (kit SAL_LAYOUT)."""
    out = []
    for p, (i, j) in SALT_PIECES.items():
        out += [(cx + i, cz + j, p, 'north'), (cx - 1 - j, cz + i, p, 'east'), (cx - 1 - i, cz - 1 - j, p, 'south'),
                (cx + j, cz - 1 - i, p, 'west')]
    return out


def medianera(s, x, z, top=2, y0=0):
    for y in range(y0, top + 1):
        h = H(x, y, z, 'm')
        K(s, x, y, z, 'medianera_hueco' if h < 25 else 'medianera_parche' if h < 110 else 'medianera')


def patio(s):
    """The long back patio (z 16..34): the gallery, Choripan's cucha in view of three windows with a line of sheets
    behind it, the path to the grill against the back party wall inside the Nona's salt, the pelopincho beside the
    grill's brick paving, the long table, the lemon tree and the shed (two loops for the chase)."""
    for x in range(LOT_X0, LOT_X1 + 1):
        for z in range(16, LOT_Z1 + 1):
            K(s, x, -1, z, 'tierra' if H(x, z, 'g') < 35 else 'cesped')
    floor(s, -11, 16, 11, 18, -1, 'baldosa_patio')
    floor(s, -5, 28, 5, 34, -1, 'ladrillo_patio')
    floor(s, 12, -4, LOT_X1, 21, -1, 'cemento_piso')
    for z in range(19, 28):                       # the cement path from the kitchen door to the grill, past the cucha
        for x in ((1, 2) if z <= 21 else (0, 1)):
            K(s, x, -1, z, 'cemento_piso')
    cx, cz = CUCHA
    for x in range(cx, cx + 3):                   # the dog's yard, worn to earth
        for z in range(cz - 1, cz + 2):
            K(s, x, -1, z, 'tierra')
    # party walls: sides and back (3 high), a taller brick wall behind the grill
    for z in range(-1, LOT_Z1 + 2):
        medianera(s, LOT_X0 - 1, z)
        medianera(s, LOT_X1 + 1, z)
    for x in range(LOT_X0 - 1, LOT_X1 + 2):
        medianera(s, x, LOT_Z1 + 1, 3 if -4 <= x <= 3 else 2)
    # ---------------------------------------------------------------- the parrilla (cold: Jorge went for charcoal)
    for x, k in ((-2, 'parrilla_mesada_der'), (0, 'parrilla_mesada_izq'), (1, 'parrilla_mesada')):
        K(s, x, 0, 34, k, 'north')
    lamp(s, -1, 0, 34, 'parrilla', 'parrilla_fuego', facing='north')
    K(s, -1, 1, 34, 'parrilla_campana', 'north')
    K(s, -1, 2, 34, 'parrilla_chimenea', 'north')
    K(s, -1, 3, 34, 'parrilla_chimenea', 'north')
    K(s, -2, 1, 34, 'cuchillos', 'north')
    group(s, 'cuchillos', (-2, 1, 34))
    K(s, 1, 1, 34, 'pinza', 'north')
    K(s, 0, 1, 34, 'sal_gruesa', 'north')
    sal = []
    for (x, z, p, f) in salt_cells(0, 34):        # the Nona's circle, closed on the back wall, a 6-cell pocket inside
        if z <= 34:
            K(s, x, 0, z, f'sal_patio_{p}', f)
            sal.append((x, 0, z))
    group(s, 'sal_parrilla', *sal)
    K(s, 3, 0, 33, 'silla_jorge', 'west')
    K(s, -4, 0, 34, 'bolsa_carbon', 'north')
    K(s, -5, 0, 34, 'cajon_cerveza', 'north')
    K(s, 5, 0, 34, 'sillas_apiladas', 'north')
    for x in (4, -5):
        lamp(s, x, 2, 34, 'aplique_patio', 'patio_luces', facing='north')
    # ---------------------------------------------------------------- long table on trestles with monobloc chairs
    K(s, 7, 0, 30, 'mesa_patio_extremo', 'north')
    for x in (8, 9, 10):
        K(s, x, 0, 30, 'mesa_patio_centro', 'north')
    K(s, 11, 0, 30, 'mesa_patio_extremo', 'south')
    for x in (7, 9, 11):
        K(s, x, 0, 29, 'silla_plastica', 'south')
    for x in (8, 10):
        K(s, x, 0, 31, 'silla_plastica', 'north')
    K(s, 9, 1, 30, 'plato', 'north')
    # ---------------------------------------------------------------- pelopincho 6x4 with murky green water, no lid,
    # beside the grill's paving (Jorge falls in from the edge of the salt)
    px0, px1, pz0, pz1 = POOL
    for x in range(px0, px1 + 1):
        for z in range(pz0, pz1 + 1):
            if (x, z) == (px0, pz1):
                k, f = 'pelopincho_esquina', 'east'
            elif (x, z) == (px1, pz1):
                k, f = 'pelopincho_esquina', 'north'
            elif (x, z) == (px0, pz0):
                k, f = 'pelopincho_esquina', 'south'
            elif (x, z) == (px1, pz0):
                k, f = 'pelopincho_esquina', 'west'
            elif z == pz1:
                k, f = 'pelopincho_borde', 'north'
            elif z == pz0:
                k, f = 'pelopincho_borde', 'south'
            elif x == px0:
                k, f = 'pelopincho_borde', 'east'
            elif x == px1:
                k, f = 'pelopincho_borde', 'west'
            else:
                k, f = ('pelopincho_agua_pelota', 'east') if (x, z) == (px0 + 2, pz0 + 1) else ('pelopincho_agua', 'north')
            K(s, x, 0, z, k, f)
    # ---------------------------------------------------------------- Choripan's cucha, facing the house, lit
    K(s, cx, 0, cz, 'cucha', 'north')
    K(s, cx + 1, 0, cz - 1, 'platos_perro', 'north')
    K(s, cx + 2, 0, cz, 'pelota', 'north')
    s.light(cx, 2, cz - 2, 9, 'cucha_luz')
    # ---------------------------------------------------------------- the clothesline across the path, behind the cucha:
    # the player walks under the rope between the sheets (the path cells hang no sheet), the silhouette beside it
    K(s, -7, 0, 25, 'tendedero_poste', 'south')
    K(s, 6, 0, 25, 'tendedero_poste', 'south')
    line = ['ropa_tendida', 'sabana_floreada', 'soga', 'sabana_blanca', 'sabana_rosa', 'sabana_silueta', 'soga',
            'ropa_tendida', 'sabana_blanca', 'sabana_floreada', 'ropa_tendida', 'sabana_rosa']   # x -6..5, path at 0..1
    for n, k in enumerate(line):
        K(s, -6 + n, 0, 25, k, 'south')
    # ---------------------------------------------------------------- lemon tree and the shed (the east loop)
    tx, tz = 13, 27
    K(s, tx, 0, tz, 'limonero_tronco', 'north')
    K(s, tx, 1, tz, 'limonero_ramas', 'north')
    for dx in (-1, 0, 1):
        for dz in (-1, 0, 1):
            K(s, tx + dx, 2, tz + dz, 'limonero_copa_limones' if (dx + dz) % 2 else 'limonero_copa', 'north')
    for (dx, dz) in ((0, 0), (-1, 0), (0, 1)):
        K(s, tx + dx, 3, tz + dz, 'limonero_copa_limones' if dx == 0 and dz == 0 else 'limonero_copa', 'north')
    for (x, z, f) in ((12, 25, 'north'), (14, 29, 'east'), (15, 26, 'west')):
        K(s, x, 0, z, 'limones_piso', f)
    for x in range(13, 17):                       # galponcito 4x4: brick and damp render, flat slab, plank door
        for z in range(30, 34):
            K(s, x, -1, z, 'cemento_piso')
            K(s, x, 3, z, 'losa_sotano')
            if x in (13, 16) or z in (30, 33):
                for y in range(0, 3):
                    K(s, x, y, z, 'ladrillo_visto' if y == 0 or H(x, y, z, 'gp') < 300 else 'revoque_chorreado')
    s.door('galpon', 13, 0, 31, 'east', mat='casa_puerta_lavadero', hinge='left')
    tall(s, 15, 0, 32, 'estante_herramientas', 'west', 'tope_fondo')
    K(s, 15, 0, 31, 'bolsa_carbon', 'west')
    K(s, 14, 0, 32, 'cajon_cerveza', 'north')
    # ---------------------------------------------------------------- clutter by the west party wall (beside the pool)
    K(s, -14, 0, 31, 'ladrillo_visto')
    K(s, -14, 1, 31, 'ladrillo_salitre')
    K(s, -13, 0, 31, 'cajon_cerveza', 'east')
    K(s, -13, 0, 30, 'bolsa_carbon_volcada', 'east')
    K(s, -14, 0, 30, 'cajon_cerveza', 'north')
    K(s, -2, 0, 27, 'manguera', 'north')
    for (x, z, k, f) in ((-10, 16, 'macetas_grupo', 'east'), (-4, 16, 'maceta_malvones', 'south'), (5, 16, 'maceta_lata', 'south'),
                         (10, 16, 'maceta_malvones', 'west'), (-18, 20, 'maceta_lata', 'east'), (-18, 24, 'macetas_grupo', 'east'),
                         (-18, 33, 'maceta_malvones', 'east'), (17, 23, 'maceta_lata', 'west'), (17, 25, 'maceta_malvones', 'west'),
                         (-12, 34, 'macetas_grupo', 'north')):
        K(s, x, 0, z, k, f)
    # ---------------------------------------------------------------- light: the tortoise lamp over the kitchen door
    # lights the cucha; the laundry one is off; the neighbours' yards spill over the walls
    lamp(s, 2, 2, 16, 'aplique_patio', ('patio_luces', 'cucha_luz'), lit=True, facing='south')
    lamp(s, 3, 2, 18, 'aplique_patio', ('patio_luces', 'cucha_luz'), lit=True, facing='south')   # on the gallery pier
    lamp(s, -6, 2, 16, 'aplique_patio', 'patio_luces', facing='south')
    # moonlight and the neighbours' spill: dim pools of light over the pool, the path, the table, the grill and the
    # side lawns (block light 4-7 on the ground), all in one group the cumbia cut / blackout can kill
    for (x, y, z, lv) in ((-8, 3, 28, 11), (1, 3, 27, 10), (9, 3, 29, 9), (0, 3, 32, 8), (-13, 3, 22, 9), (14, 3, 19, 9),
                          (7, 3, 22, 9), (12, 3, 33, 8), (-14, 3, 31, 8), (-15, 3, 6, 8), (14, 3, 6, 8)):
        s.light(x, y, z, lv, 'patio_luna')


def street(s):
    """Front garden, the fence with its gates, the vainilla sidewalk and its grass verge, the curb, the old asphalt of
    the pasaje, the opposite sidewalk; the street lamps."""
    for x in range(-40, 41):
        for z in range(-28, -4):
            if -19 <= z <= -14:
                k = 'asfalto_bache' if H(x, z, 'a') < 25 else 'asfalto'
            elif z in (-13, -20):
                k = 'cordon'
            elif -12 <= z <= -10 or z in (-22, -21):
                k = 'tierra' if (x % 9 == 0 and z in (-11, -21)) or H(x, z, 'c') < 60 else 'cesped'
            elif z >= -9 or -26 <= z <= -23:
                k = 'vereda_rota' if H(x, z, 'v') < 200 else 'vereda'
            else:
                k = 'cesped'
            K(s, x, -1, z, k)
    for x in range(LOT_X0, LOT_X1 + 1):
        for z in range(-4, -1):
            if s.get(x, -1, z) is None or 'cemento' not in s.get(x, -1, z):
                K(s, x, -1, z, 'cesped')
    for z in (-4, -3, -2):
        K(s, 8, -1, z, 'baldosa_patio')
    K(s, 8, -1, -5, 'baldosa_patio')
    for x in range(-11, 12):                       # a strip of earth with plants along the facade
        if x not in (8,) and s.get(x, -1, -2) and 'cesped' in s.get(x, -1, -2):
            K(s, x, -1, -2, 'tierra')
    # fence at z = -5: low brick wall + railing, brick piers, the pedestrian gate and the 2-leaf car gate
    piers = {-19, -13, -7, -1, 4, 7, 9, 13, 16, 18}
    for x in range(-19, 19):
        if x in (8, 14, 15):
            continue
        if x in piers:
            K(s, x, 0, -5, 'pilar_luz' if x == 4 else 'pilar', 'north')
            K(s, x, 1, -5, 'pilar_remate', 'north')
        else:
            K(s, x, 0, -5, 'murito', 'north')
            K(s, x, 1, -5, 'reja_cartel_perro' if x == 5 else 'reja', 'north')
    s.door('puerta_vereda', 8, 0, -5, 'south', mat='casa_puerta_reja', hinge='left')
    s.door('porton', 14, 0, -5, 'south', mat='casa_porton', hinge='right')
    s.door('porton_2', 15, 0, -5, 'south', mat='casa_porton', hinge='left')
    for z in range(-4, -1):                        # front-garden sides: low wall + railing towards the neighbours
        for x in (LOT_X0 - 1, LOT_X1 + 1):
            K(s, x, 0, z, 'murito', 'east' if x < 0 else 'west')
            K(s, x, 1, z, 'reja', 'east' if x < 0 else 'west')
    # the fence line continues along the sidewalk (neighbours), and across the street
    for x in list(range(-40, -19)) + list(range(19, 41)):
        p = x % 6 == 2
        K(s, x, 0, -5, 'pilar' if p else 'murito', 'north')
        K(s, x, 1, -5, 'pilar_remate' if p else 'reja', 'north')
    for x in range(-40, 41):
        p = x % 7 == 3
        K(s, x, 0, -26, 'pilar' if p else 'murito', 'south')
        K(s, x, 1, -26, 'pilar_remate' if p else 'reja', 'south')
    # the concrete lamp post with flyers and the flickering sodium lamp at the verge; more lamps down the street
    K(s, 2, 0, -10, 'poste_pie', 'south')      # its arm over the sidewalk: from the spawn it hangs top left of the gate
    K(s, 2, 1, -10, 'poste_afiches', 'south')
    K(s, 2, 2, -10, 'poste', 'south')
    K(s, 2, 3, -10, 'poste', 'south')
    lamp(s, 2, 4, -10, 'farol', 'farol', lit=True, facing='south')
    for (x, z, f) in ((-24, -11, 'north'), (27, -11, 'north'), (-12, -21, 'south'), (16, -21, 'south')):
        K(s, x, 0, z, 'poste_pie', f)
        for y in (1, 2, 3):
            K(s, x, y, z, 'poste_afiches' if y == 1 and x < 0 else 'poste', f)
        lamp(s, x, 4, z, 'farol', 'faroles_calle', lit=True, facing=f)
    K(s, -21, 0, -11, 'poste_pie', 'north')
    K(s, -21, 1, -11, 'poste', 'north')
    K(s, -21, 2, -11, 'poste_cartel_calle', 'north')
    # facade dressing: number, bell, the meters, the porch lamp, plants
    K(s, 6, 1, -2, 'numero_1961', 'north')
    K(s, 9, 1, -2, 'timbre', 'north')
    K(s, 4, 0, -2, 'medidor_gas', 'north')
    K(s, 4, 1, -2, 'medidor_luz', 'north')
    lamp(s, 7, 2, -2, 'aplique_patio', ('luces_pb', 'porch'), lit=True, facing='north')
    for (x, k) in ((-8, 'maceta_malvones'), (-3, 'macetas_grupo'), (10, 'maceta_lata'), (5, 'maceta_malvones')):
        K(s, x, 0, -3, k, 'north')


def house_shell(s, x0, x1, z0, z1, top, front_z, front_f, windows=(), lit=(), blind=None, roof='flat', door=None):
    """A neighbour's house as a closed shell from the casa kit: render walls on the plinth, a flat roof slab with a
    parapet (or a tiled pitched roof), the street facade at `front_z` facing `front_f`; `blind` = the x of a party
    wall left as exposed medianera brick; `windows` = (x, y, z, facing, mode); `lit` = cells with a lit lamp inside."""
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            if x not in (x0, x1) and z not in (z0, z1):
                continue
            for y in range(0, top + 1):
                if x == blind:
                    h = H(x, y, z, 'nb')
                    k = 'medianera_hueco' if h < 20 else 'medianera_parche' if h < 120 else 'medianera'
                else:
                    k = 'zocalo_revoque' if y == 0 else ('revoque_chorreado' if (y == top or H(x, y, z, 'nr') < 120) else 'revoque_blanco')
                K(s, x, y, z, k)
    if roof == 'flat':
        for x in range(x0, x1 + 1):
            for z in range(z0, z1 + 1):
                K(s, x, top + 1, z, 'losa_sotano')
                if x in (x0, x1) or z in (z0, z1):
                    K(s, x, top + 2, z, 'revoque_chorreado' if H(x, z, 'pp') < 400 else 'revoque_blanco')
    else:                                          # pitched, ridge parallel to the street, slopes facing front/back
        depth = abs(z1 - z0) + 1
        back_f = OPP[front_f]
        for x in range(x0, x1 + 1):
            for n in range(depth):
                z = front_z + (n if front_f == 'north' else -n)
                up = min(n, depth - 1 - n)
                f = front_f if n < depth // 2 else back_f
                K(s, x, top + 1 + up, z, 'techo_alero' if n in (0, depth - 1) else
                  ('techo_cumbrera' if n == depth // 2 else 'techo'), f)
    for (x, y, z, f, mode) in windows:
        lx, lz = left_of(f)
        for (cx, cz, side) in ((x, z, 'der'), (x + lx, z + lz, 'izq')):
            K(s, cx, y, cz, f'ventana_inf_{side}' + ('_cerrada' if mode == 'closed' else ''), f, replace=True)
            K(s, cx, y + 1, cz, f'ventana_sup_{side}' + ('_cerrada' if mode in ('closed', 'half') else ''), f, replace=True)
    if door:
        x, z, f, key = door
        s.door(None, x, 0, z, f, mat='casa_' + key, hinge='left')   # behind its fenced garden: never reached
    for (x, y, z, key, grp) in lit:
        lamp(s, x, y, z, key, grp, lit=True)


def neighbours(s):
    """The barrio: the two neighbours' two-storey houses built against the party walls (their blind brick walls rise
    over the side passages, with water tanks and TV antennas on the flat roofs), the west one has a party going on in
    the back (the cumbia), the east one has a floodlight on its back room over the wall; a row of houses across the
    street."""
    # west neighbour: x -27..-19 (its east wall IS our party wall), front at z=-1, back at z=15
    house_shell(s, -27, -19, -1, 15, 7, -1, 'north', blind=-19,
                windows=((-25, 1, -1, 'north', 'closed'), (-22, 5, -1, 'north', 'closed'), (-25, 5, -1, 'north', 'half'),
                         (-25, 1, 15, 'south', 'closed'), (-22, 5, 15, 'south', 'open')),
                lit=((-22, 7, 14, 'plafon', 'vecino_fiesta'),),
                door=(-22, -1, 'south', 'puerta_placa'))
    lamp(s, -25, 4, 16, 'aplique_patio', 'vecino_fiesta', lit=True, facing='south')
    s.light(-23, 3, 20, 10, 'vecino_fiesta')
    for (x, y, z) in ((-24, 9, 4), (-23, 9, 4), (-24, 9, 5), (-23, 9, 5), (-24, 10, 4), (-23, 10, 4), (-24, 10, 5), (-23, 10, 5)):
        K(s, x, y, z, 'revoque_chorreado')        # the concrete water tank on the roof
    for y in (9, 10, 11):
        K(s, -21, y, 10, 'tendedero_poste', 'east')   # the TV antenna mast
    # east neighbour: x 18..26 (its west wall IS our party wall)
    house_shell(s, 18, 26, -1, 15, 7, -1, 'north', blind=18,
                windows=((24, 1, -1, 'north', 'closed'), (21, 5, -1, 'north', 'closed'), (24, 5, -1, 'north', 'closed'),
                         (24, 1, 15, 'south', 'closed'), (21, 5, 15, 'south', 'half')),
                door=(21, -1, 'south', 'puerta_placa'))
    for (x, y, z) in ((22, 9, 9), (23, 9, 9), (22, 9, 10), (23, 9, 10), (22, 10, 9), (23, 10, 9), (22, 10, 10), (23, 10, 10)):
        K(s, x, y, z, 'losa_sotano')
    for y in (9, 10, 11, 12):
        K(s, 20, y, 4, 'tendedero_poste', 'north')
    # the east neighbour's back room against the party wall, with a floodlight over our patio
    for z in range(23, 30):
        medianera(s, LOT_X1 + 1, z, top=3, y0=3)
    lamp(s, 17, 3, 26, 'aplique_patio', ('vecino_reflector', 'patio_luna'), lit=True, facing='west')
    # across the street: facades at z=-29 facing the pasaje (south... towards +z), front gardens behind the fence
    for x in range(-40, 41):
        for z in (-28, -27):
            K(s, x, -1, z, 'cesped' if H(x, z, 'fg') > 120 else 'tierra')
    rows = [(-36, -27, 7, 'flat', ((-34, 1, -29, 'south', 'closed'), (-30, 5, -29, 'south', 'half'), (-34, 5, -29, 'south', 'closed')),
             ((-30, 7, -30, 'plafon', 'vecinos'),), (-31, 'puerta_placa_blanca')),
            (-24, -14, 2, 'pitched', ((-22, 1, -29, 'south', 'closed'), (-16, 1, -29, 'south', 'half')), (), (-19, 'puerta_placa')),
            (-11, -1, 7, 'flat', ((-9, 1, -29, 'south', 'closed'), (-4, 1, -29, 'south', 'closed'), (-9, 5, -29, 'south', 'closed'),
                                  (-4, 5, -29, 'south', 'half')), (), (-6, 'puerta_placa')),
            (2, 12, 2, 'pitched', ((4, 1, -29, 'south', 'half'), (10, 1, -29, 'south', 'closed')), ((4, 2, -30, 'plafon', 'vecinos'),),
             (7, 'puerta_placa_blanca')),
            (15, 25, 7, 'flat', ((17, 1, -29, 'south', 'closed'), (23, 5, -29, 'south', 'closed'), (17, 5, -29, 'south', 'closed')),
             (), (20, 'puerta_placa')),
            (28, 38, 2, 'pitched', ((30, 1, -29, 'south', 'closed'), (36, 1, -29, 'south', 'closed')), (), (33, 'puerta_placa'))]
    for (x0, x1, top, rf, wins, lit, door) in rows:
        house_shell(s, x0, x1, -35, -29, top, -29, 'south', windows=wins, lit=lit, roof=rf,
                    door=(door[0], -29, 'north', door[1]))


# ===================================================================================================== markers
def markers(s):
    P = s.point
    cx, cz = CUCHA
    # ---------------------------------------------------------------- arrival (chapter 1)
    P('spawn', 8, 0, -12, 25)                     # on the sidewalk's verge by the curb: facade, gate and farol in one frame
    P('vereda', 6, 0, -7, 'south')                # checkpoint 1
    P('marta_puerta', 8, 0, -1, 'north')          # Marta in curlers in the doorway recess
    P('porton', 14, 0, -3, 'south')               # the car gate (the script opens porton and porton_2 together)
    P('jorge_llega', 14, 0, 18, yaw_to(14, 18, -1, 33))   # Jorge walks into view from the driveway (beat 11)
    # ---------------------------------------------------------------- ground floor
    P('living', 4, 0, 4, 'west')                  # checkpoint 2
    P('jorge_sillon', -1, 0, 5, 'east')
    P('tv', 1, 0, 5, 'south')                     # standing in front of the CRT
    P('nona_living', 2, 0, 4, 'south')            # the Nona's rocker in the living, two blocks from the novela
    P('marta_chat', 4, 0, 2, 'west')              # Marta shows the phone (living, by the hall)
    P('pasillo_pb', 8, 0, 3, 'south')             # checkpoint 3 (the hall)
    P('choripan_333', 9, 0, 1, 'south')           # Choripan sits at the foot of the stair at 3:33, looking up into the dark
    P('comedor', 5, 0, 9, 'east')
    P('torre_sillas', 9, 0, 10, 'west')           # the chair tower goes up here (in line with the kitchen door, by the hall)
    P('cocina', 2, 0, 11, 'west')                 # checkpoint 8
    P('mate_spot', 0, 1, 13, 'north')             # the mate+thermos block on the counter
    P('termo_spot', 0, 2, 13, 'north')            # (the block above: the thermos is lifted from the block under it)
    P('ventana_cocina', -1, 0, 12, 'south')       # inside, at the kitchen window over the patio
    P('tablero', -6, 0, 9, 'north')               # in front of the breaker board
    P('lavadero', -6, 0, 11, 'south')
    P('sotano_escalera', -9, 0, 8, 'south')       # top of the basement stair (through the plank door)
    P('nona_cuarto', -8, 0, 3, 'north')           # the Nona in her rocker, facing the altar
    P('altar', -8, 0, 2, 'north')                 # in front of the altar
    P('choripan_casa', -7, 0, 2, 'west')          # the dog's spot at the Nona's feet
    P('ventana_fondo', 6, 0, 13, yaw_to(6, 13, cx, cz - 0.85))   # comedor window over the patio: the cucha in view
    # ---------------------------------------------------------------- stair and first floor
    P('escalera_arriba', 9, 5, 7, 'north')        # top of the stair, dark, looking down
    P('pasillo_1p', 4, 5, 7, 'west')              # checkpoint 6
    P('lucia_cuarto', -5, 5, 8, 'west')
    P('lucia_cama', -7, 5, 11, 'west')            # beside the canopy bed
    P('lucia_bajo_cama', -8, 5, 12, yaw_to(-8, 12, -7, 11))   # Lucia lying half under the bed, no physics, peeking out
    P('lucia_techo', -7, 7, 11, 'west')           # on the ceiling (sealed)
    P('estante_munecas', -5, 5, 11, 'east')       # in front of the doll shelves (the bed is behind you)
    P('ventana_lucia', -5, 5, 14, yaw_to(-5, 14, cx, cz - 0.85))  # in the French window's reveal: the cucha in view
    P('tablet', -6, 5, 8, yaw_to(-6, 8, -7, 7))   # in front of the desk with the tablet (VOD loop)
    P('toti_cuarto', 1, 5, 11, 'east')
    P('placard', 2, 5, 12, 'north')               # inside the placard, behind the closed right leaf, looking out
    P('toti_placard', 3, 5, 12, 'north')          # Toti inside, behind the left leaf (he holds it shut)
    P('matrimonial', -5, 5, 3, 'west')
    P('bano', 7, 5, 12, 'south')
    P('espejo_bano', 7, 5, 11, 'west')            # facing the medicine-cabinet mirror
    P('costura', 5, 5, 3, 'north')
    # ---------------------------------------------------------------- patio
    P('patio', 1, 0, 19, 'south')                 # checkpoint 4
    P('cucha', cx, 0, cz - 2, 'south')            # in front of the doghouse door
    P('cucha_techo', cx, 1.25, cz, 'north')       # on its roof (Ofelia, beat 7; spawn her with no gravity)
    P('cucha_cola', cx, 0.1, cz + 0.3, 'north')   # the tail still wagging inside (sealed)
    P('parrilla', -1, 0, 33, 'south')             # checkpoint 5: the cooking spot inside the salt
    P('silla_jorge', 3, 0, 33, 'west')
    P('pelopincho', -8.5, 0, 28.5, 'north')       # pool centre
    P('jorge_cae', -5, 0, 29, 'east')             # Jorge on the rim, facing the grill: he falls back into the pool
    P('medianera', 18, 3, 20, 'west')             # top of the east party wall by the driveway, where the wisp crosses
    P('cumbia', -23, 1, 22, 'east')               # the neighbours' party behind the west wall (sound source, sealed)
    # ---------------------------------------------------------------- Ofelia's four seats (always where she will be)
    P('ofelia_cucha', cx, 0, cz - 0.85, 'north')  # sitting on the ground in front of the doghouse door
    P('ofelia_silla_jorge', 3, 0.5, 33, 'west')
    P('ofelia_almohada', -9, 5.6, 11, 'east')     # on Lucia's pillow
    P('ofelia_falda', -8, 0.85, 2.7, 'north')     # on the Nona's lap (rocker in her room)
    # ---------------------------------------------------------------- basement and the 1961 room
    P('sotano', -3, -5, 10, 'north')              # checkpoint 7
    P('sotano_pared', -5, -5, 6, 'north')         # in front of the cracked wall
    P('cuarto61', -3, -6, 1, 'north')             # centre of the 1961 room (sealed until the wall falls)
    P('nona_flota', -4.5, -4.5, -0.5, 'south')    # the floating rocker, over the salt circle (sealed)
    P('ofelia_flota', -4.5, -4.05, -0.2, 'south')  # Ofelia on the floating Nona's lap (sealed)
    # ---------------------------------------------------------------- breakfast (chapter 8)
    P('desayuno', 2, 0, 10, 'west')
    P('marta_desayuno', 1, 0, 12, 'north')        # at the stove
    P('jorge_desayuno', 2, 0, 9, 'west')          # in a towel, by the dining-room door
    P('toti_desayuno', -1, 0, 9, 'south')         # coming in from the living
    P('nona_desayuno', -2, 0.5, 11, 'east')       # sitting at the table
    P('choripan_desayuno', -2, 0, 12, 'east')

    # ---------------------------------------------------------------- areas (inclusive block corners)
    A = s.area
    A('casa', -10, -7, -6, 10, 8, 14)             # includes the 1961 room
    A('vereda', -40, 0, -12, 40, 4, -6)
    A('living', -1, 0, 1, 5, 2, 6)
    A('comedor', 5, 0, 8, 9, 2, 13)
    A('cocina', -3, 0, 9, 2, 2, 13)
    A('nona_cuarto', -9, 0, 1, -4, 2, 5)
    A('lavadero', -9, 0, 8, -5, 2, 13)
    A('pasillo_pb', 7, 0, 1, 9, 2, 6)
    A('escalera', 9, 0, 2, 9, 7, 7)
    A('pasillo_1p', -2, 5, 6, 9, 7, 8)
    A('lucia', -9, 5, 7, -4, 7, 14)
    A('toti', -1, 5, 10, 3, 7, 13)
    A('matrimonial', -9, 5, 1, -1, 7, 4)
    A('costura', 2, 5, 0, 9, 7, 4)
    A('bano', 6, 5, 10, 9, 7, 13)
    A('sotano', -9, -5, 5, 5, -3, 13)
    A('cuarto61', -9, -6, -5, -1, -3, 2)
    A('patio', LOT_X0, 0, 16, LOT_X1, 6, LOT_Z1)
    A('parrilla_circulo', -2, 0, 32, 1, 2, 33)    # inside the Nona's salt (the 6-cell pocket in front of the grill)
    A('placard', 2, 5, 12, 3, 6, 13)
    A('jardin', LOT_X0, 0, -4, LOT_X1, 4, -2)
    A('pasillo_lateral', LOT_X0, 0, -1, -12, 4, 15)
    A('entrada_autos', 12, 0, -4, LOT_X1, 4, 21)
    A('cucha', CUCHA[0] - 2, 0, CUCHA[1] - 2, CUCHA[0] + 1, 2, CUCHA[1] + 1)

    # ---------------------------------------------------------------- writes (text anchors)
    s.write('lemaza', -1, -5, 0, 'west', width=3.0)          # the 1961 room east wall, over the children's scratches
    s.write('espejo_azamel', 6, 6, 11, 'east', width=0.8)    # the bathroom mirror (UV only)
    # the botiquin's mirror stands 0.275 off the wall: the text must sit 0.30 in front of the wall, not the default 0.15
    s.markers['writes']['espejo_azamel']['depth'] = 0.30
    s.write('cuaderno', -7, 6, 7, 'south', width=1.2)        # on the wall over Lucia's desk: 'MI AMIGO SE LLAMA LEMAZA'

    # ---------------------------------------------------------------- swaps the script makes (props)
    s.prop('tv_estatica', 1, 0, 6, 'casa_tele_vieja_estatica', facing='north')
    s.prop('parrilla_azul', -1, 0, 34, 'casa_parrilla_azul', facing='north')
    s.prop('parrilla_carne', -1, 0, 34, 'casa_parrilla', facing='north')
    s.prop('cuchillos_vacio', -2, 1, 34, 'casa_cuchillos_vacio', facing='north')
    s.prop('cucha_rota', CUCHA[0], 0, CUCHA[1], 'casa_cucha_rota', facing='north')
    s.prop('rayones_brillo', -9, -6, 1, 'casa_rayones_latin_brillo', facing='east')
    s.prop('lata_abierta', -7, 1, 5, 'casa_lata_galletitas_abierta', facing='north')
    s.prop('desayuno_mesa', 0, 1, 11, 'casa_desayuno', facing='north')
    s.prop('botiquin_rajado', 6, 6, 11, 'casa_botiquin_rajado', facing='east')
    for n, (x, y, z, f) in enumerate(((-2, 2, 13, 'north'), (1, 2, 13, 'north'), (-3, 2, 12, 'east'))):   # beat 4
        s.prop(f'alacena_abierta_{n}', x, y, z, 'casa_alacena_abierta', facing=f)
    for n, x in enumerate((0, 4, 9)):           # beat 12: the corridor bulbs burst one by one
        s.prop(f'plafon_roto_{n}', x, 7, 7, 'casa_plafon_roto')
    for n, z in enumerate((10, 11, 12)):        # beat 13: the dolls leave the shelf
        s.prop(f'estante_vacio_{n}', -4, 5, z, 'casa_estante_munecas_vacio', facing='west')
    for n, (x, y, z, f) in enumerate(((-4, 1, 34, 'north'), (3, 1, 34, 'north'), (3, 1, 18, 'south'))):   # beat 11
        s.prop(f'cuchillo_clavado_{n}', x, y, z, 'casa_cuchillo_clavado', facing=f)
    s.prop('chancleta', -5, 5, 10, 'casa_chancleta', facing='west')                   # beat 14, where it lands
    s.prop('silla_volcada', 9, 0, 9, 'casa_silla_comedor_volcada', facing='west')      # beat 4, after the tower
    s.prop('cartel_nona', 5, 1, -5, 'casa_reja_cartel_perro_nona', facing='north')    # P2: '...y con la nona'

    # ---------------------------------------------------------------- the cracked wall and what replaces it (beat 14)
    after = {(-6, -5): 'boquete_izq_abajo', (-6, -4): 'boquete_izq_arriba', (-5, -3): 'boquete_dintel_izq',
             (-4, -3): 'boquete_dintel_der', (-3, -5): 'boquete_der_abajo', (-3, -4): 'boquete_der_arriba',
             (-5, -5): 'escombros_arena', (-5, -4): None, (-4, -5): None, (-4, -4): None}
    cells = []
    n = 0
    for ((x, y), k) in sorted(after.items()):
        cells.append((x, y, 4))
        if k is None:
            s.prop(f'boquete_{n}', x, y, 4, 'minecraft:air')
        else:
            s.prop(f'boquete_{n}', x, y, 4, 'casa_' + k, facing='south')
        n += 1
    for (x, y) in ((-5, -5), (-5, -4), (-4, -5), (-4, -4)):   # and through the 1961 layer behind it
        cells.append((x, y, 3))
        s.prop(f'boquete_{n}', x, y, 3, 'minecraft:air')
        n += 1
    group(s, 'sotano_pared', *cells)
    s.prop('escombros_0', -5, -5, 5, 'casa_escombros', facing='south')     # rubble thrown into the basement
    s.prop('escombros_1', -4, -5, 5, 'casa_escombros_arena', facing='north')
    s.prop('escombros_2', -6, -5, 5, 'casa_escombros', facing='east')


def build():
    CLASHES.clear()
    s = Site('casa', PALETTE)
    hs = House(s)
    shell(s, hs)
    ground_floor(s, hs)
    first_floor(s, hs)
    roof(s, hs)
    porch_and_gallery(s)
    basement(s, hs)
    furnish_pb(s)
    furnish_1p(s)
    furnish_basement(s)
    patio(s)
    street(s)
    neighbours(s)
    # cornices (only where a solid wall stands behind: never across a reveal or an opening)
    for (x1, z1, x2, z2) in ((-1, 1, 5, 6), (5, 8, 9, 13), (-9, 1, -4, 5), (7, 1, 8, 6)):
        trims(s, x1, z1, x2, z2, 2, 'cornisa')
    trims(s, -9, 1, -1, 4, 7, 'cornisa')
    # lawn wherever nothing else was laid (side passages)
    for x in range(LOT_X0, LOT_X1 + 1):
        for z in range(-4, LOT_Z1 + 1):
            if s.get(x, -1, z) is None:
                K(s, x, -1, z, 'cesped')
    markers(s)
    s.finish_conflicts = hs.check_finishes()
    if CLASHES:
        raise AssertionError('casa: placements overwrite furniture: ' +
                             '; '.join(f'{p} {old} <- {new}' for (p, old, new) in CLASHES[:20]))
    return s


# ===================================================================================================== plan images
def plan_png(s, path, levels=((0, 'PB y=0'), (5, '1P y=5'), (-5, 'sotano y=-5'))):
    """Top-down plans (one per storey) coloured by kind of block, with the marker points."""
    from PIL import Image, ImageDraw
    x0, y0, z0, x1, y1, z1 = s.bounds()
    x0, x1, z0, z1 = max(x0, -22), min(x1, 22), max(z0, -14), min(z1, 36)
    k = 9
    W, D = (x1 - x0 + 1) * k, (z1 - z0 + 1) * k
    img = Image.new('RGB', (W * len(levels) + 10 * (len(levels) - 1), D + 16), (20, 24, 20))
    d = ImageDraw.Draw(img)
    for n, (ly, title) in enumerate(levels):
        ox = n * (W + 10)
        d.text((ox + 4, 2), title, fill=(255, 255, 255))
        for x in range(x0, x1 + 1):
            for z in range(z0, z1 + 1):
                st = s.get(x, ly, z)
                below = s.get(x, ly - 1, z)
                col = None
                name = st.split('[')[0].split(':')[1] if st else ''
                if not st or name in ('air', 'light'):
                    if below and 'air' not in below:
                        col = (70, 60, 50)
                    else:
                        continue
                elif 'puerta' in name or name == 'porton' or 'placard_puerta' in name:
                    col = (200, 120, 40)
                elif 'ventana' in name:
                    col = (110, 170, 230)
                elif 'escalera' in name or 'escalon' in name:
                    col = (160, 110, 60)
                elif any(w in name for w in ('pared', 'revoque', 'ladrillo', 'empapelado', 'azulejo', 'cemento_lavadero',
                                             'medianera', 'zocalo_', 'murito', 'pilar', 'divisoria')):
                    col = (215, 215, 205)
                elif 'sal_' in name:
                    col = (250, 250, 250)
                else:
                    col = (90, 150, 90)
                X, Z = ox + (x - x0) * k, 14 + (z - z0) * k
                d.rectangle([X, Z, X + k - 1, Z + k - 1], fill=col)
        for name, (x, y, z, yaw) in s.markers['points'].items():
            if abs(y - ly) > 1.5 or not (x0 <= x <= x1 and z0 <= z <= z1):
                continue
            X, Z = ox + (x - x0) * k + k // 2, 14 + (z - z0) * k + k // 2
            d.ellipse([X - 3, Z - 3, X + 3, Z + 3], fill=(230, 40, 40))
            d.text((X + 4, Z - 5), name, fill=(255, 230, 120))
    img.save(path)


if __name__ == '__main__':
    site = build()
    out, n, pal = site.export()
    print(f'{out}: {n} blocks, {pal} states')
    bad = site.finish_conflicts
    print(f'finish check: {len(bad)} wall cells show two rooms\' paints' + (': ' + ', '.join(f'{p}{f}' for p, f in bad[:12]) if bad else ''))
    sp = _os.path.join(WORK, 'sites')
    os.makedirs(sp, exist_ok=True)
    p = os.path.join(sp, 'casa_plan.png')
    plan_png(site, p)
    print(p)
    known = {b for b in KIND}
    if known:   # every deadline: block must be an exported kit block (casa_estructura / casa_muebles)
        bad = site.unknown_blocks({'casa_' + b for b in known})
        if bad:
            print('UNKNOWN KIT BLOCKS:', bad)
    else:
        print('kit check skipped: tools/blocks/out/preview_all.json not found')
