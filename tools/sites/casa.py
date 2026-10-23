"""Casa Morales v2 (case 2): "la casona de los Morales", a 1952 two-storey chalet standing alone on a rural lot.
Layout from docs/design/casa_terror.md sections 2, 3 and 11 (section 11 is the marker contract).

    python3 tools/sites/casa.py      -> src/main/resources/data/deadline/sites/casa.json (+ plan images)

Origin: x east, y up (y=0 = ground-floor level, the ground is y=-1), z south; the gate and the dirt track are towards -z.
LOT 46 x 56 (fence ring x -23 / 22, z -16 / 39); HOUSE 34 x 23 (outer skin x -17 / 16, z 0 / 22) with two-layer outer
walls: the facade skin and an inner plaster layer painted by the room behind it, so windows sit in a deep reveal.
Levels: basement y -5..-3 (floor -6, slab -2, the sealed 1961 room one step lower: sand -7, 4 high), ground floor (PB)
y 0..2 under a ceiling at y=3, first floor (1P) slab y=4, rooms y 5..7, ceiling y=8, attic floor y=9, attic from y=10
under a 45 degree gable roof (ridge along x at z=11, y=20).

Both storeys share one grid: front rooms z 2..7, a double wall (z 8, 9), a 2-wide corridor running the whole width
(z 10..11, x -15..14), a double wall (z 12, 13), back rooms z 14..20.
PB  front: NONA (x -15..-10) | BANO PB (-7..-4) | ESCRITORIO del Nono (-1..2) | LIVING (4..9) | HALL + main stair (11..14)
    back:  service shaft (x -15: service stair up, basement stair down under it) | COCINA (-13..-8, despensa in its NE
           corner) | COMEDOR (-5..2) | LAVADERO (5..8) | COSTURERO (11..14)
1P  front: MATRIMONIAL (x -15..-8) | CUARTO DEL NONO (-5..0) | HUESPEDES (2..8) | stair hall + balcony (11..14)
    back:  service stair arrival (x -15) | LUCIA (-12..-7) | TOTI (-4..1) | BANO 1P (4..8) | TRASTERO with the steep
           attic stair (11..14)
The 1P corridor is 30 long and straight with six doors alternating front/back (the cascade) and a lamp every 4 blocks;
the main stair lands at its east end, the service stair at the west end (fondo): PB corridor + stairs + 1P corridor make
the chase loop, the comedor/cocina/corridor a second loop downstairs.

Every room is a box carved out of solid filler and paints its own ring (House), so two rooms with different finishes
never share a wall block. Everything is built from the casa_* building kits (tools/blocks/kit_casa_estructura.py,
kit_casa_muebles.py); vanilla only for air, light, the lawn, gravel, logs and leaves outside. K() places a kit block and
refuses to overwrite a piece of furniture already placed (build() raises on any clash). Lamps are placed OFF (their
_apagado/_apagada twin) and listed in luces_<area> groups the director switches; lit at arrival: the street lamp, the
Nona's altar candles and ONE light upstairs (the dead grandfather's room).
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
# story points nobody walks to: Lucia / the Nona on ceilings, the 1961 room behind the cracked wall (and the family
# standing in it), the floating Nona outside a 1P window, Ofelia on the doghouse roof
SEALED = ('lucia_techo', 'pasillo_techo', 'cuarto61', 'familia61_', 'ventana_1p_afuera', 'cucha_techo')

AIR = 'minecraft:air'
VEC = {'north': (0, -1), 'south': (0, 1), 'east': (1, 0), 'west': (-1, 0)}
OPP = {'north': 'south', 'south': 'north', 'east': 'west', 'west': 'east'}

# house grid
SX0, SX1, SZ0, SZ1 = -17, 16, 0, 22          # outer skin
IX0, IX1, IZ0, IZ1 = -16, 15, 1, 21          # inner plaster layer
FZ0, FZ1 = 2, 7                              # front rooms
CZ0, CZ1 = 10, 11                            # corridors
BZ0, BZ1 = 14, 20                            # back rooms
# lot
LX0, LX1, LZ0, LZ1 = -23, 22, -16, 39        # fence ring

# per-room wall finishes: (foot course, body [variants], top course); 1P rooms use the same 3 rows at y 5..7
FIN = {
    'living': ('pared_living_zocalo', ['pared_living'] * 11 + ['pared_living_marco'], 'pared_living_moldura'),
    'hall': ('pared_living_zocalo', ['pared_living'] * 8 + ['pared_living_marco'], 'pared_living_moldura'),
    'escritorio': ('pared_living_zocalo', ['pared_living'] * 4 + ['pared_living_marco'], 'pared_living_moldura'),
    'costurero': ('pared_living_zocalo', ['pared_living'] * 7 + ['pared_living_marco'], 'pared_living'),
    'nono': ('pared_living_zocalo', ['pared_living'] * 3 + ['pared_living_marco'], 'pared_living_moldura'),
    'huespedes': ('pared_living_zocalo', ['pared_living'] * 9 + ['pared_living_marco'], 'pared_living'),
    'nona': ('empapelado_nona_zocalo', ['empapelado_nona'], 'empapelado_nona'),
    'cocina': ('pared_cocina', ['pared_cocina'], 'pared_cocina'),
    'lavadero': ('cemento_lavadero_zocalo', ['cemento_lavadero'], 'cemento_lavadero'),
    'pasillo': ('pared_pasillo_zocalo', ['pared_pasillo'] * 9 + ['pared_pasillo_rayada', 'pared_pasillo_marco'], 'pared_pasillo'),
    'lucia': ('pared_lucia_zocalo', ['pared_lucia'] * 4 + ['pared_lucia_stickers'], 'pared_lucia'),
    'toti': ('pared_toti_zocalo', ['pared_toti'] * 4 + ['pared_toti_poster'], 'pared_toti'),
    'matrimonial': ('empapelado_matrimonial_zocalo', ['empapelado_matrimonial'], 'empapelado_matrimonial'),
    'bano': ('azulejo_celeste_sucio', ['azulejo_celeste'] * 9 + ['azulejo_celeste_falta'], 'azulejo_celeste_guarda'),
    'sotano': ('pared_sotano_zocalo', ['pared_sotano'] * 13 + ['pared_sotano_ladrillo'], 'pared_sotano'),
    'cuarto61': ('pared_61_zocalo', ['pared_61'], 'pared_61'),
}
# finishes that read as the same paint (a single wall between them is fine)
FAMILY = {'living': 'beige', 'hall': 'beige', 'escritorio': 'beige', 'costurero': 'beige', 'nono': 'beige',
          'huespedes': 'beige'}

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


def V(s, x, y, z, block):
    """A vanilla block (outside only: lawn, gravel, trees, plants)."""
    s.set(x, y, z, 'minecraft:' + block)


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


def group(s, name, *cells):
    lst = s.markers['groups'].setdefault(name, [])
    for c in cells:
        if list(c) not in lst:
            lst.append(list(c))


OFF_A = ('lampara_pie', 'lampara_comedor', 'lampara_hongo', 'escritorio_lucia', 'tele_vieja', 'parrilla', 'caldera',
         'estufa')


def lamp(s, x, y, z, key, groups, lit=False, facing=None):
    """A light fixture placed lit or as its _apagado/_apagada twin, registered in the director's groups."""
    if not lit:
        key = key + ('_apagada' if key in OFF_A else '_apagado')
    K(s, x, y, z, key, facing)
    for g in ((groups,) if isinstance(groups, str) else groups):
        group(s, g, (x, y, z))


def tall(s, x, y, z, key, facing, cap='tope'):
    """A ~2 m single-block piece plus the invisible collision cap in the block above (same facing)."""
    K(s, x, y, z, key, facing)
    K(s, x, y + 1, z, cap, facing)


class House:
    """Walls are filler cells; rooms are carved boxes that paint their own ring; openings, doors and windows cut it."""

    def __init__(self, s):
        self.s = s
        self.walls = set()
        self.rooms = []
        self.tiled = set()      # cells tiled on both faces on purpose

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

    def fill(self, x, y, z, key):
        """A solid cell inside a room (under a stair, a closet side): a wall that is not repainted."""
        K(self.s, x, y, z, key, replace=True)

    def opening(self, x, y, z, h=2, sill='umbral_marmol'):
        for k in range(h):
            self.cut(x, y + k, z)
        if sill:
            K(self.s, x, y - 1, z, sill, replace=True)

    def door(self, name, x, y, z, facing, key, hinge='left', open_=False, sill=True):
        self.walls.discard((x, y, z))
        self.walls.discard((x, y + 1, z))
        self.s.door(name, x, y, z, facing, mat='casa_' + key, hinge=hinge, open_=open_)
        if sill:
            K(self.s, x, y - 1, z, 'umbral_marmol', replace=True)

    def window(self, x, y, z, facing, mode='open', inner=True):
        """2x2 window in the outer skin (x, z = the 'der' column, sill row y); the inner ring cell becomes a reveal."""
        lx, lz = left_of(facing)
        fx, fz = VEC[facing]
        cells = []
        for (cx, cz, side) in ((x, z, 'der'), (x + lx, z + lz, 'izq')):
            inf = f'ventana_inf_{side}' + ('_cerrada' if mode == 'closed' else '')
            sup = f'ventana_sup_{side}' + ('_cerrada' if mode in ('closed', 'half') else '')
            K(self.s, cx, y, cz, inf, facing)
            K(self.s, cx, y + 1, cz, sup, facing)
            self.walls.discard((cx, y, cz))
            self.walls.discard((cx, y + 1, cz))
            cells += [(cx, y, cz), (cx, y + 1, cz)]
            if inner:
                self.cut(cx - fx, y, cz - fz)
                self.cut(cx - fx, y + 1, cz - fz)
        return cells


def floor(s, x1, z1, x2, z2, y, key, worn=None, worn_p=250, replace=False):
    for x in range(min(x1, x2), max(x1, x2) + 1):
        for z in range(min(z1, z2), max(z1, z2) + 1):
            k = worn if (worn and H(x, z, y) < worn_p) else key
            K(s, x, y, z, k, replace=replace)


def ceiling(s, x1, z1, x2, z2, y, damp=()):
    for x in range(min(x1, x2), max(x1, x2) + 1):
        for z in range(min(z1, z2), max(z1, z2) + 1):
            K(s, x, y, z, 'cielorraso_humedad' if (x, z) in damp else 'cielorraso', replace=True)


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


# ===================================================================================================== the house
PB_ROOMS = [   # (name, finish, boxes x1 z1 x2 z2)
    ('nona_cuarto', 'nona', [(-15, FZ0, -10, FZ1)]),
    ('bano_pb', 'bano', [(-7, FZ0, -4, FZ1)]),
    ('escritorio', 'escritorio', [(-1, FZ0, 2, FZ1)]),
    ('living', 'living', [(4, FZ0, 9, FZ1)]),
    ('hall', 'hall', [(11, FZ0, 14, 9)]),                       # merges into the corridor at z 10
    ('pasillo_pb', 'hall', [(-15, CZ0, 14, CZ1)]),
    ('esc_servicio', 'cocina', [(-15, BZ0, -15, BZ1)]),       # the shaft: service stair up, basement stair down
    ('cocina', 'cocina', [(-13, BZ0, -8, BZ1)]),
    ('comedor', 'living', [(-5, BZ0, 2, BZ1)]),
    ('lavadero', 'lavadero', [(5, BZ0, 8, BZ1)]),
    ('costurero', 'costurero', [(11, BZ0, 14, BZ1)]),
]
P1_ROOMS = [
    ('matrimonial', 'matrimonial', [(-15, FZ0, -8, FZ1)]),
    ('cuarto_nono', 'nono', [(-5, FZ0, 0, FZ1)]),
    ('huespedes', 'huespedes', [(2, FZ0, 8, FZ1)]),
    ('esc_principal', 'pasillo', [(11, FZ0, 14, 9)]),           # the stair hall over the PB hall, balcony at the front
    ('pasillo_1p', 'pasillo', [(-15, CZ0, 14, CZ1)]),
    ('esc_servicio_1p', 'pasillo', [(-15, 12, -15, 16)]),      # the service stair landing + its passage
    ('lucia', 'lucia', [(-12, BZ0, -7, BZ1)]),
    ('toti', 'toti', [(-4, BZ0, 1, BZ1)]),
    ('bano_1p', 'bano', [(4, BZ0, 8, BZ1)]),
    ('trastero', 'pasillo', [(11, BZ0, 14, BZ1)]),
]
WINDOWS = {'pb': [], '1p': [], 'altillo': []}


def yroof(z):
    return 9 + z if z <= 11 else 9 + (SZ1 - z)


def shell(s, hs):
    """Foundations, the outer skin (front: brick plinth + face brick on the ground floor, white render upstairs; sides
    and back render with rising damp on the west), the solid filler both storeys are carved from, floors, ceilings."""
    floor(s, SX0, SZ0, SX1, SZ1, -1, 'cemento_piso')
    for x in range(SX0, SX1 + 1):
        for z in range(SZ0, SZ1 + 1):
            if x not in (SX0, SX1) and z not in (SZ0, SZ1):
                continue
            for y in range(0, 9):
                if z == SZ0:
                    k = 'zocalo_ladrillo' if y == 0 else \
                        ('ladrillo_salitre' if H(x, y) < (420 if y == 1 else 90) else 'ladrillo_visto') if y <= 3 else \
                        ('revoque_chorreado' if y in (4, 8) and H(x, y, 1) < 420 else 'revoque_blanco')
                else:
                    wet = x == SX0 or (z == SZ1 and x < -4)
                    k = ('zocalo_revoque_humedad' if wet else 'zocalo_revoque') if y == 0 else \
                        ('revoque_humedad' if wet and y == 1 else
                         'revoque_chorreado' if y in (4, 8) and H(x, z, y) < 380 else 'revoque_blanco')
                hs.wall(x, y, z, x, y, z, k)
    for y in (0, 1, 2, 5, 6, 7):
        hs.wall(IX0, y, IZ0, IX1, y, IZ1, 'revoque_blanco')
    floor(s, IX0, IZ0, IX1, IZ1, 3, 'cielorraso')
    floor(s, IX0, IZ0, IX1, IZ1, 4, 'parquet', 'parquet_gastado', 220)
    floor(s, IX0, IZ0, IX1, IZ1, 8, 'cielorraso')
    floor(s, IX0, IZ0, IX1, IZ1, 9, 'machimbre')


def ground_floor(s, hs):
    for (name, fin, boxes) in PB_ROOMS:
        hs.room(name, fin, boxes, 0)
    # floors
    floor(s, -15, 2, -10, 7, -1, 'parquet', 'parquet_gastado', 260)                 # Nona
    floor(s, -7, 2, -4, 7, -1, 'piso_bano')                                         # bano PB
    floor(s, -1, 2, 2, 7, -1, 'parquet', 'parquet_gastado', 120)                    # escritorio
    floor(s, 4, 2, 9, 7, -1, 'parquet')                                             # living
    for x in range(5, 9):
        for z in range(3, 7):
            if H(x, z, 'w') < 520:
                K(s, x, -1, z, 'parquet_gastado')                                   # the walking path
    floor(s, 11, 2, 14, 9, -1, 'granitico', 'granitico_roto', 40)                   # hall
    floor(s, -15, CZ0, 14, CZ1, -1, 'granitico', 'granitico_roto', 30)              # corridor
    floor(s, -15, BZ0, -15, BZ1, -1, 'ceramica_cocina')                             # shaft
    floor(s, -13, BZ0, -8, BZ1, -1, 'ceramica_cocina')                              # cocina
    floor(s, -5, BZ0, 2, BZ1, -1, 'parquet', 'parquet_gastado', 200)                # comedor
    floor(s, 5, BZ0, 8, BZ1, -1, 'cemento_piso')                                    # lavadero
    floor(s, 11, BZ0, 14, BZ1, -1, 'parquet', 'parquet_gastado', 300)               # costurero
    ceiling(s, IX0, IZ0, IX1, IZ1, 3, damp={(-12, 4), (-6, 3), (7, 2), (-1, 11), (-10, 17), (0, 19), (6, 16),
                                             (13, 18), (-14, 10)})
    for (name, _, _) in PB_ROOMS:
        hs.paint(name)
    # kitchen: green tiles behind the counters (back wall + the west wall by the stove)
    for x in range(-13, -7):
        K(s, x, 0, IZ1, 'azulejo_verde_sucio' if H(x, 'k') < 400 else 'azulejo_verde')
        K(s, x, 1, IZ1, 'azulejo_verde_falta' if x == -10 else 'azulejo_verde')
        K(s, x, 2, IZ1, 'azulejo_verde_guarda')
    for y in (1, 2):
        K(s, -13, y, IZ1, 'pared_cocina_hollin')
    # laundry: tiles behind the tub
    for x in (7, 8):
        K(s, x, 0, IZ1, 'azulejo_verde_sucio')
        K(s, x, 1, IZ1, 'azulejo_verde')
        K(s, x, 2, IZ1, 'azulejo_verde_guarda')

    # ---------------------------------------------------------------- main stair (x=14, rising south from z=5 to z=9)
    for z in (6, 7, 8):
        s.set(14, 3, z, AIR)
    for z in (7, 8):
        s.set(14, 4, z, AIR)
    for k in range(5):
        z = 5 + k
        stair(s, 14, k, z, 'escalera_madera', 'south', replace=True)
        for y in range(0, k):
            hs.fill(14, y, z, 'pared_living_zocalo' if y == 0 else 'pared_living')
        if k <= 3:
            K(s, 14, k + 1, z, 'baranda_escalera_der', 'north')
    # the coat closet under the stair (ropero_hall): door in the stair's side, the hanging space cut into the inner layer
    s.set(14, 0, 8, AIR)
    s.set(14, 1, 8, AIR)
    s.door('ropero_hall', 14, 0, 8, 'east', mat='casa_puerta_placard', hinge='left')
    hs.cut(15, 0, 8)
    hs.cut(15, 1, 8)
    K(s, 15, -1, 8, 'granitico')

    # ---------------------------------------------------------------- service stair (x=-15, rising north z 19 -> 15)
    # and the basement stair under it (descending south z 15 -> 19): see the docstring of basement()
    for k in range(5):
        z = 19 - k
        stair(s, -15, k, z, 'escalera_madera', 'north', replace=True)
        for y in range(0, k):
            if (z, y) in ((16, 0), (15, 0), (15, 1)):
                continue                       # headroom of the basement stair below
            hs.fill(-15, y, z, 'pared_cocina')
        if k >= 1:
            K(s, -15, k + 1, z, 'pasamanos_izq', 'south')
    for (y, z) in ((3, 18), (3, 17), (4, 17), (4, 16)):
        s.set(-15, y, z, AIR)

    # ---------------------------------------------------------------- doors and openings
    hs.door('entrada', 12, 0, IZ0, 'south', 'puerta_entrada', hinge='right')
    hs.opening(12, 0, SZ0, sill='granitico')                     # a recessed entrance in the skin
    casings(s, 12, 0, IZ0, 'south')
    # front rooms off the corridor: door in the room's layer (z 8), the corridor's layer (z 9) is a reveal
    for (name, x, key, hinge) in (('nona_cuarto', -12, 'puerta_nona', 'left'), ('bano_pb', -5, 'puerta_bano', 'right'),
                                  ('escritorio', 0, 'puerta_placa', 'left')):
        hs.door(name, x, 0, 8, 'north', key, hinge=hinge)
        hs.opening(x, 0, 9)
        casings(s, x, 0, 8, 'north')
        casings(s, x, 0, 9, 'south')
    for x in (6, 7):                                             # living <-> corridor: a wide arch through both layers
        hs.opening(x, 0, 8)
        hs.opening(x, 0, 9)
    for z in (3, 4):                                             # living <-> hall: arch in the single wall
        hs.opening(10, 0, z)
    # back rooms off the corridor: door in the room's layer (z 13), the corridor's layer (z 12) a reveal
    for (name, x, key, hinge) in (('sotano', -15, 'puerta_sotano', 'left'), ('cocina', -10, 'puerta_placa_blanca', 'right'),
                                  ('lavadero', 6, 'puerta_placa_blanca', 'left'), ('costurero', 12, 'puerta_placa', 'right')):
        hs.door(name, x, 0, 13, 'south', key, hinge=hinge)
        hs.opening(x, 0, 12)
        casings(s, x, 0, 13, 'south')
        casings(s, x, 0, 12, 'north')
    for x in (-2, -1):                                           # comedor <-> corridor arch
        hs.opening(x, 0, 12)
        hs.opening(x, 0, 13)
    # cocina <-> comedor (double wall x -7 / -6) and cocina <-> service stair (single wall x -14)
    hs.door('cocina_comedor', -6, 0, 17, 'west', 'puerta_placa_blanca', hinge='left')
    hs.opening(-7, 0, 17)
    casings(s, -6, 0, 17, 'east')
    casings(s, -7, 0, 17, 'west')
    hs.opening(-14, 0, 20, sill='ceramica_cocina')
    # to the patio: the kitchen's half-glazed door and the laundry's plank door (both recessed in the skin)
    hs.door('puerta_patio', -11, 0, IZ1, 'south', 'puerta_cocina', hinge='left')
    hs.opening(-11, 0, SZ1, sill='cemento_piso')
    hs.door('lavadero_patio', 6, 0, IZ1, 'south', 'puerta_lavadero', hinge='right', sill=False)
    hs.opening(6, 0, SZ1, sill=None)

    # ---------------------------------------------------------------- windows (sill y=1)
    W = WINDOWS['pb']
    W += hs.window(-13, 1, SZ0, 'north', 'half')        # Nona, front
    W += hs.window(SX0, 1, 4, 'west', 'closed')         # Nona, side
    W += hs.window(0, 1, SZ0, 'north', 'closed')        # escritorio (shut since 1987)
    W += hs.window(5, 1, SZ0, 'north', 'half')          # living, front
    W += hs.window(8, 1, SZ0, 'north', 'open')          # living, front (the car is parked out there)
    W += hs.window(SX0, 1, 11, 'west', 'open')          # end of the PB corridor
    W += hs.window(-1, 1, SZ1, 'south', 'open')         # comedor, over the patio
    W += hs.window(-4, 1, SZ1, 'south', 'half')
    W += hs.window(13, 1, SZ1, 'south', 'closed')       # costurero
    W += hs.window(SX1, 1, 17, 'east', 'half')          # costurero, side
    W += hs.window(SX1, 3, 6, 'east', 'open')           # stair window, halfway up
    for (x, side) in ((-12, 'der'), (-13, 'izq')):     # kitchen window over the counter (facing south: der = higher x)
        K(s, x, 1, SZ1, f'ventana_cocina_{side}' + ('_abierta' if side == 'izq' else ''), 'south')
        hs.walls.discard((x, 1, SZ1))
        hs.cut(x, 1, IZ1)
        W.append((x, 1, SZ1))
    K(s, -6, 2, SZ0, 'ventana_bano', 'north')           # bathroom tilt window, high
    hs.walls.discard((-6, 2, SZ0))
    hs.cut(-6, 2, IZ0)
    W.append((-6, 2, SZ0))
    K(s, 7, 2, SZ1, 'ventana_bano', 'south')            # laundry tilt window over the tub
    hs.walls.discard((7, 2, SZ1))
    hs.cut(7, 2, IZ1)
    W.append((7, 2, SZ1))


def first_floor(s, hs):
    for (name, fin, boxes) in P1_ROOMS:
        hs.room(name, fin, boxes, 5)
    floor(s, -15, CZ0, 14, CZ1, 4, 'parquet', 'parquet_gastado', 380, replace=True)
    floor(s, -15, 2, -8, 7, 4, 'parquet', 'parquet_gastado', 180, replace=True)
    floor(s, -5, 2, 0, 7, 4, 'parquet', 'parquet_gastado', 60, replace=True)
    floor(s, 2, 2, 8, 7, 4, 'parquet', 'parquet_gastado', 300, replace=True)
    floor(s, -12, BZ0, -7, BZ1, 4, 'parquet', 'parquet_mancha', 40, replace=True)
    floor(s, -4, BZ0, 1, BZ1, 4, 'parquet', 'parquet_gastado', 450, replace=True)
    floor(s, 4, BZ0, 8, BZ1, 4, 'piso_bano', replace=True)
    floor(s, 11, BZ0, 14, BZ1, 4, 'parquet_gastado', replace=True)
    for z in (7, 8):
        s.set(14, 4, z, AIR)
    for z in (16, 17):
        s.set(-15, 4, z, AIR)
    ceiling(s, IX0, IZ0, IX1, IZ1, 8, damp={(-12, 3), (-2, 5), (6, 3), (0, 10), (-9, 11), (-10, 18), (7, 17),
                                             (12, 16), (-3, 18)})
    for (name, _, _) in P1_ROOMS:
        hs.paint(name)
    # the six doors along the corridor, alternating front / back (the cascade, from the fondo towards the stair)
    cascade = []
    for (name, x, front, key, hinge) in (('matrimonial', -10, True, 'puerta_placa', 'left'),
                                         ('lucia', -8, False, 'puerta_lucia', 'right'),
                                         ('cuarto_nono', -3, True, 'puerta_placa', 'right'),
                                         ('toti', 0, False, 'puerta_toti', 'left'),
                                         ('huespedes', 4, True, 'puerta_placa_blanca', 'left'),
                                         ('bano_1p', 6, False, 'puerta_bano', 'right')):
        zd, zr, f = (8, 9, 'north') if front else (13, 12, 'south')
        hs.door(name, x, 5, zd, f, key, hinge=hinge)
        hs.opening(x, 5, zr)
        casings(s, x, 5, zd, f)
        casings(s, x, 5, zr, OPP[f])
        cascade.append([x, 5, zd])
    s.markers['groups']['pasillo_1p_cascada'] = cascade
    for x in (12, 13):                                           # the trastero opens off the corridor (no door)
        hs.opening(x, 5, 12)
        hs.opening(x, 5, 13)
    # balcony door over the entrance (recessed in the skin) and the stair hall's balustrade around the well
    hs.door('balcon', 12, 5, SZ0, 'north', 'puerta_cocina', hinge='right', sill=False)
    hs.cut(12, 5, IZ0)
    hs.cut(12, 6, IZ0)
    K(s, 12, 4, IZ0, 'umbral_marmol', replace=True)
    for z in (7, 8):
        K(s, 13, 5, z, 'baranda', 'east')
    K(s, 14, 5, 6, 'baranda', 'south')
    K(s, 13, 5, 6, 'baranda_poste', 'south')
    # windows (sill y=6)
    W = WINDOWS['1p']
    W += hs.window(-13, 6, SZ0, 'north', 'half')        # matrimonial
    W += hs.window(-10, 6, SZ0, 'north', 'closed')
    W += hs.window(SX0, 6, 4, 'west', 'closed')         # matrimonial, side
    W += hs.window(-2, 6, SZ0, 'north', 'closed')       # cuarto del Nono (blinds down since the funeral)
    W += hs.window(5, 6, SZ0, 'north', 'open')          # huespedes: ventana_1p_afuera floats out there
    W += hs.window(14, 6, SZ0, 'north', 'half')         # stair hall
    W += hs.window(SX0, 6, 11, 'west', 'open')          # end of the 1P corridor (fondo)
    W += hs.window(-9, 6, SZ1, 'south', 'open')         # Lucia, over the patio and the cucha
    W += hs.window(-1, 6, SZ1, 'south', 'half')         # Toti
    W += hs.window(13, 6, SZ1, 'south', 'closed')       # trastero
    W += hs.window(SX1, 6, 17, 'east', 'closed')        # trastero, side
    K(s, 6, 7, SZ1, 'ventana_bano', 'south')            # bathroom tilt window over the tub
    hs.walls.discard((6, 7, SZ1))
    hs.cut(6, 7, IZ1)
    W.append((6, 7, SZ1))

    # ---------------------------------------------------------------- attic stair (trastero, x=14, rising north)
    for k in range(5):
        z = 19 - k
        stair(s, 14, 5 + k, z, 'escalera_madera', 'north', replace=True)
        for y in range(5, 5 + k):
            hs.fill(14, y, z, 'pared_pasillo_zocalo' if y == 5 else 'pared_pasillo')
        if k >= 1:
            K(s, 14, 6 + k, z, 'pasamanos_der', 'south')
    for (y, z) in ((8, 18), (8, 17), (9, 17), (9, 16)):
        s.set(14, y, z, AIR)


def attic(s, hs):
    """The attic under the whole roof: rough boards on the slab, air up to the roof, the gable walls, the hatch rail."""
    for x in range(IX0, IX1 + 1):
        for z in range(IZ0, IZ1 + 1):
            for y in range(10, yroof(z)):
                s.set(x, y, z, AIR)
    for z in (16, 17):
        K(s, 13, 10, z, 'baranda', 'east')
    K(s, 14, 10, 18, 'baranda', 'north')
    K(s, 13, 10, 18, 'baranda_poste', 'north')


def roof(s, hs):
    """Gable roof over the skin (x -17..16, z 0..22): eaves at y=9, ridge row z=11 at y=20; gable walls at the x ends
    (the east one in face brick, like the front), a brick chimney stack, attic windows and vents in the gables,
    downpipes at the four corners."""
    for x in range(SX0, SX1 + 1):
        for z in range(SZ0, SZ1 + 1):
            y = yroof(z)
            end = x in (SX0, SX1)
            brick = '_ladrillo' if x == SX1 else ''
            if z == 11:
                k = ('hastial_cumbrera_der' if x == SX0 else f'hastial{brick}_cumbrera_izq') if end else 'techo_cumbrera'
                K(s, x, y, z, k, 'north')
                continue
            front = z < 11
            f = 'north' if front else 'south'
            eave = z in (SZ0, SZ1)
            if end:
                side = ('der' if x == SX0 else 'izq') if front else ('izq' if x == SX0 else 'der')
                k = f'hastial{brick}_alero_{side}' if eave else f'hastial{brick}_{side}'
            else:
                mossy = H(x, z, 'r') < (380 if not front else 160)
                k = ('techo_alero_musgo' if mossy else 'techo_alero') if eave else ('techo_musgo' if mossy else 'techo')
                if (x, z) in ((-11, 6), (4, 15), (9, 4)):
                    k = 'techo_roto'
            K(s, x, y, z, k, f)
        if x in (SX0, SX1):
            for z in range(IZ0, IZ1 + 1):
                for y in range(9, yroof(z)):
                    if x == SX1:
                        hs.wall(x, y, z, x, y, z, 'ladrillo_salitre' if H(x, y, z) < 90 else 'ladrillo_visto')
                    else:
                        hs.wall(x, y, z, x, y, z, 'revoque_chorreado' if y == 9 and H(x, z) < 400 else 'revoque_blanco')
    # attic windows (small tilt windows) and vents in both gables
    for (x, f) in ((SX0, 'west'), (SX1, 'east')):
        K(s, x, 14, 11, 'ventana_bano', f, replace=True)
        hs.walls.discard((x, 14, 11))
        WINDOWS['altillo'].append((x, 14, 11))
        K(s, x + (-1 if x == SX0 else 1), 17, 11, 'rejilla', f)
    # chimney stack of the old salamandra, through the attic and past the ridge, with its rain cap
    for y in range(10, 22):
        K(s, -7, y, 5, 'ladrillo_salitre' if y in (10, yroof(5)) else 'ladrillo_visto', replace=True)
    K(s, -7, 22, 5, 'parrilla_chimenea', 'north')
    # downpipes
    for x in (SX0 + 1, SX1 - 1):
        K(s, x, 8, SZ0 - 1, 'bajada_codo', 'north')
        for y in range(1, 8):
            K(s, x, y, SZ0 - 1, 'bajada', 'north')
        K(s, x, 0, SZ0 - 1, 'bajada_pie', 'north')
        K(s, x, 8, SZ1 + 1, 'bajada_codo', 'south')
        for y in range(1, 8):
            K(s, x, y, SZ1 + 1, 'bajada', 'south')
        K(s, x, 0, SZ1 + 1, 'bajada_pie', 'south')


def porch(s):
    """The porch in front of the door: two brick piers carrying the balcony slab (terrazzo on top, render under), the
    balcony railing, a plaster band course over the face brick, the facade dressing."""
    for x in range(10, 15):
        for z in range(-3, 0):
            K(s, x, -1, z, 'granitico')
            K(s, x, 3, z, 'losa_sotano')
            K(s, x, 4, z, 'granitico')
    for x in (10, 14):
        for y in (0, 1, 2):
            K(s, x, y, -3, 'pilar', 'north')
    K(s, 10, 5, -3, 'baranda_poste', 'north')
    K(s, 14, 5, -3, 'baranda_poste', 'north')
    for x in (11, 12, 13):
        K(s, x, 5, -3, 'baranda', 'north')
    for z in (-2, -1):
        K(s, 10, 5, z, 'baranda', 'west')
        K(s, 14, 5, z, 'baranda', 'east')
    for x in range(SX0, SX1 + 1):                 # band course capping the face brick
        if x not in (SX0 + 1, SX1 - 1) and not 10 <= x <= 14:
            K(s, x, 3, SZ0 - 1, 'cornisa', 'north')


def basement(s, hs):
    """Basement 12x8 (x -15..-4, z 14..21) under the kitchen and the comedor, reached by the stair that runs down under
    the service stair (x=-15, top step flush with the PB floor at z=15, bottom at z=19). The sealed 1961 room (x -1..6,
    z 14..20) lies east of it behind a double wall: the basement's plaster layer at x=-3 (with the crack), the 1961
    lime wash layer at x=-2."""
    BX0, BX1, BZa, BZb = -15, -4, 14, 21
    for x in range(BX0 - 1, BX1 + 2):
        for z in range(BZa - 1, BZb + 2):
            edge = x in (BX0 - 1, BX1 + 1) or z in (BZa - 1, BZb + 1)
            K(s, x, -6, z, 'cemento_piso')
            K(s, x, -2, z, 'losa_sotano', replace=True)
            for y in (-5, -4, -3):
                if edge:
                    hs.wall(x, y, z, x, y, z, 'pared_sotano')
                else:
                    s.set(x, y, z, AIR)
    RX0, RX1, RZa, RZb = -1, 6, 14, 20
    for x in range(RX0 - 1, RX1 + 2):
        for z in range(RZa - 1, RZb + 2):
            edge = x in (RX0 - 1, RX1 + 1) or z in (RZa - 1, RZb + 1)
            K(s, x, -7, z, 'arena_pisadas' if H(x, z) < 160 else 'arena')
            K(s, x, -2, z, 'losa_sotano', replace=True)
            for y in (-6, -5, -4, -3):
                if edge:
                    hs.wall(x, y, z, x, y, z, 'pared_61')
                else:
                    s.set(x, y, z, AIR)
    hs.room('sotano', 'sotano', [(BX0, BZa, BX1, BZb)], -5, carve=False)
    hs.room('cuarto61', 'cuarto61', [(RX0, RZa, RX1, RZb)], -6, h=4, carve=False)
    hs.paint('sotano')
    hs.paint('cuarto61')
    # the crack (its back hidden by the 1961 layer) and a cement step in the 1961 layer under the future hole
    for y, k in ((-5, 'pared_sotano_grieta_abajo'), (-4, 'pared_sotano_grieta'), (-3, 'pared_sotano_grieta_arriba')):
        K(s, -3, y, 17, k)
    for z in (17, 18):
        stair(s, -2, -6, z, 'escalera_cemento', 'west')
        hs.walls.discard((-2, -6, z))
    for (x, z) in ((2, 15), (1, 16), (3, 16), (2, 17), (4, 18), (3, 19), (5, 17)):
        K(s, x, -7, z, 'arena_arrastre')          # drag marks from the bed to the wall
    # the stair down (x=-15, descending south), under the service stair
    for k in range(5):
        y, z = -1 - k, 15 + k
        stair(s, -15, y, z, 'escalera_cemento', 'north', replace=True)
        for yy in range(-5, y):
            if yy >= -5:
                hs.fill(-15, yy, z, 'pared_sotano')
        if k >= 1:
            K(s, -15, y + 1, z, 'pasamanos_izq', 'south', replace=True)
    for (y, z) in ((-1, 16), (0, 16), (-2, 17), (-1, 17), (-3, 18), (-2, 18), (-4, 19), (-3, 19)):
        s.set(-15, y, z, AIR)
    # a moonlight shaft: the ventiluz high on the back wall, a lit pocket behind it
    K(s, -9, -3, 22, 'ventana_sotano', 'south', replace=True)
    hs.walls.discard((-9, -3, 22))
    s.light(-9, -3, 23, 6, 'sotano_luna')


# ===================================================================================================== hiding places
HIDES = {}      # id -> (inside (x, y, z, facing), out (x, y, z, facing))


def side_wall(s, hs, x, y, z, fin):
    """A wall cell standing inside a room (alcove side, closet side), painted with the room's finish."""
    foot, body, top = FIN[fin]
    for k in range(3):
        if is_air(s, x, y + k, z):
            hs.fill(x, y + k, z, foot if k == 0 else (top if k == 2 else pick(body, x, y + k, z)))


def placard(s, hs, hid, cells, facing, fin, door_key='placard_puerta'):
    """Built-in louvred wardrobe, a hiding place: real placard doors in the room row `cells` (x, y, z at floor level),
    `facing` = the way you walk in; behind each door a 1x2 hanging space of air; the back with the clothes on its rail
    sits in the wall layer behind (another layer behind it, so its back never shows); the maletero over the doors, boards
    over the hanging space; the alcove's ends get side walls in the room's finish."""
    fx, fz = VEC[facing]
    front = OPP[facing]
    lx, lz = left_of(front)
    cells = sorted(cells, key=lambda c: -(c[0] * lx + c[2] * lz))      # viewer's left first
    n = len(cells)
    for i, (x, y, z) in enumerate(cells):
        side = 'der' if (i == n - 1 and n > 1) else 'izq'
        ix, iz, bx, bz = x + fx, z + fz, x + 2 * fx, z + 2 * fz
        for yy in (y, y + 1):
            s.set(x, yy, z, AIR)
            hs.cut(ix, yy, iz)
        s.door(hid if i == 0 else f'{hid}_{i + 1}', x, y, z, facing, mat='casa_' + door_key,
               hinge='left' if i < n - 1 or n == 1 else 'right')
        K(s, bx, y, bz, f'placard_fondo_{side}', front, replace=True)
        hs.walls.discard((bx, y, bz))
        K(s, x, y + 2, z, f'placard_maletero_{side}', front, replace=True)
        K(s, ix, y + 2, iz, 'machimbre', replace=True)
    (x, y, z), (x2, _, z2) = cells[0], cells[-1]
    for (cx, cz) in ((x + lx, z + lz), (x2 - lx, z2 - lz)):
        for row in (0, 1):
            side_wall(s, hs, cx + row * fx, y, cz + row * fz, fin)
    mid = cells[n // 2]
    HIDES[hid] = ((mid[0] + fx, mid[1], mid[2] + fz, front), (mid[0] - fx, mid[1], mid[2] - fz, facing))


def raised_bed(s, pieces, y):
    """A hiding bed: its blocks one level up (y+1) with a block of air under them (the space under the bed)."""
    for (x, z, key, f) in pieces:
        s.set(x, y, z, AIR)
        K(s, x, y + 1, z, key, f)


# ===================================================================================================== furniture
DRAWERS = ('mesa_luz', 'mesa_luz_nona', 'comoda_izq', 'comoda_der', 'mesada_cajones', 'aparador_izq', 'aparador_der',
           'mesita_auxiliar', 'escritorio_lucia', 'escritorio_lucia_apagada', 'mesa_comedor_extremo')


def furnish_pb(s, hs):
    # ---------------------------------------------------------------- NONA (x -15..-10, z 2..7): the raised lustred bed,
    # the home altar with its candles (lit) and the rocker facing it, wool basket, walker, the big placard (hiding place)
    placard(s, hs, 'ropero_nona', [(-15, 0, 6), (-14, 0, 6)], 'south', 'nona')
    raised_bed(s, [(-15, 3, 'cama_nona_cabecera', 'east'), (-14, 3, 'cama_nona_pie', 'east')], 0)
    HIDES['cama_nona'] = ((-14, 0, 3, 'east'), (-13, 0, 3, 'west'))
    K(s, -16, 1, 3, 'empapelado_nona_cruz', replace=True)          # the ghost of a crucifix over the bed
    K(s, -15, 0, 2, 'mesa_luz_nona', 'east')
    lamp(s, -15, 1, 2, 'velador', 'luces_nona_cuarto', facing='east')
    K(s, -15, 0, 4, 'mesa_luz', 'east')
    K(s, -15, 1, 4, 'lata_galletitas', 'east')
    K(s, -13, 0, 3, 'pantuflas', 'west')
    lamp(s, -10, 0, 4, 'altar', ('altar_velas', 'luces_nona_cuarto'), lit=True, facing='west')
    K(s, -10, 1, 4, 'altar_estampitas', 'west')
    K(s, -12, 0, 4, 'mecedora', 'east')
    K(s, -12, 0, 5, 'canasta_lana', 'east')
    K(s, -11, 0, 6, 'andador', 'west')
    K(s, -10, 0, 2, 'ropero_abajo', 'west')
    K(s, -10, 1, 2, 'ropero_arriba', 'west')
    K(s, -11, 1, 2, 'foto_nona_joven', 'south')
    K(s, -10, 1, 6, 'crucifijo', 'west')
    lamp(s, -12, 2, 4, 'plafon', 'luces_nona_cuarto')
    pair(s, -12, 1, 2, 'south', 'cortina_floreada_izq', 'cortina_floreada_der')
    pair(s, -15, 1, 4, 'east', 'cortina_floreada_izq', 'cortina_floreada_der')
    K(s, -13, 1, 7, 'llave_luz', 'north')
    # ---------------------------------------------------------------- BANO PB (x -7..-4, z 2..7)
    K(s, -7, 0, 3, 'inodoro', 'east')
    K(s, -7, 0, 4, 'bidet', 'east')
    K(s, -7, 1, 2, 'portarrollo', 'east')
    K(s, -4, 0, 3, 'lavatorio', 'west')
    K(s, -4, 1, 3, 'botiquin', 'west')
    lamp(s, -4, 2, 3, 'aplique_bano', 'luces_bano_pb', facing='west')
    K(s, -7, 2, 6, 'ducha', 'east')
    K(s, -7, 0, 6, 'balde_secador', 'east')
    K(s, -6, 1, 7, 'toallero', 'north')
    K(s, -5, 0, 4, 'alfombra_bano', 'north')
    lamp(s, -5, 2, 5, 'plafon', 'luces_bano_pb')
    # ---------------------------------------------------------------- ESCRITORIO del Nono (x -1..2, z 2..7): shut since
    # 1987; the lustred desk under the window, his chair, the photos of 1961 on the walls, boxes of papers, the armchair
    K(s, 0, 0, 2, 'mesa_comedor_extremo', 'north')
    K(s, 1, 0, 2, 'mesa_comedor_extremo', 'south')
    K(s, 0, 0, 3, 'silla_comedor', 'north')
    lamp(s, 0, 1, 2, 'velador', 'luces_escritorio', facing='south')
    K(s, 1, 1, 2, 'lata_galletitas', 'south')
    K(s, -1, 1, 3, 'foto_nona_joven', 'east')
    K(s, -1, 1, 5, 'foto_casamiento', 'east')
    K(s, 2, 1, 4, 'foto_familia', 'west')
    K(s, 2, 2, 6, 'crucifijo', 'west')
    K(s, 2, 0, 6, 'sillon_individual', 'west')
    K(s, -1, 0, 7, 'cajas_apiladas', 'north')
    K(s, -1, 0, 6, 'caja_abierta', 'east')
    tall(s, 2, 0, 3, 'tapado_ropero', 'west')
    tall(s, -1, 0, 2, 'lampara_pie', 'east')
    group(s, 'luces_escritorio', (-1, 0, 2))
    s.set(-1, 0, 2, s.get(-1, 0, 2).replace('lampara_pie', 'lampara_pie_apagada'))
    lamp(s, 1, 2, 5, 'plafon', 'luces_escritorio')
    # ---------------------------------------------------------------- LIVING (x 4..9, z 2..7): the CRT on the west wall,
    # the floral sofa facing it, Jorge's armchair, the Nona's rocker, the gas heater, the photo wall, 'es la humedad'
    tall(s, 4, 0, 4, 'tele_vieja', 'east')
    s.set(4, 0, 4, s.get(4, 0, 4).replace('tele_vieja', 'tele_vieja_apagada'))
    group(s, 'tv', (4, 0, 4))
    for z, k in ((3, 'sillon_izq'), (4, 'sillon_centro'), (5, 'sillon_der')):
        K(s, 8, 0, z, k, 'west')
    K(s, 6, 0, 4, 'mesa_ratona', 'east')
    K(s, 6, 0, 2, 'sillon_individual', 'west')                    # Jorge's armchair
    K(s, 6, 0, 6, 'mecedora', 'west')                             # the Nona's rocker, two blocks from the novela
    lamp(s, 4, 0, 6, 'estufa', 'luces_living', facing='east')
    K(s, 4, 0, 2, 'mesita_auxiliar', 'east')
    K(s, 4, 1, 2, 'carpetita_florero', 'east')
    tall(s, 9, 0, 2, 'lampara_pie', 'west')
    group(s, 'luces_living', (9, 0, 2))
    s.set(9, 0, 2, s.get(9, 0, 2).replace('lampara_pie', 'lampara_pie_apagada'))
    lamp(s, 6, 2, 4, 'lampara_comedor', 'luces_living')
    K(s, 9, 0, 6, 'mancha_humedad', 'west')
    K(s, 9, 1, 7, 'llave_luz', 'north')
    for (x, y, z, k, f) in ((4, 1, 3, 'foto_choripan', 'east'), (4, 2, 5, 'foto_familia', 'east'),
                            (5, 1, 7, 'foto_cumple', 'north'), (8, 2, 7, 'cuadro_ultima_cena', 'north')):
        K(s, x, y, z, k, f)
    for x0 in (5, 8):
        pair(s, x0 + 1, 1, 2, 'south', 'cortina_floreada_izq', 'cortina_floreada_der')
    for x in (5, 6, 7):
        K(s, x, 0, 5, 'alfombra_punta' if x != 6 else 'alfombra', 'east' if x == 7 else 'west')
    # ---------------------------------------------------------------- HALL (x 11..14, z 2..9): the big mirror (the dresser),
    # the landline on its side table, the hooks by the door, the coat closet under the stair
    pair(s, 11, 0, 6, 'east', 'comoda_izq', 'comoda_der')
    for z in (6, 7):
        K(s, 11, 1, z, 'tope_fondo', 'east')
    K(s, 11, 0, 5, 'mesita_auxiliar', 'east')
    K(s, 11, 1, 5, 'telefono', 'east')
    K(s, 11, 1, 2, 'perchero_bata', 'east')
    K(s, 13, 0, 2, 'maceta_malvones', 'south')
    K(s, 13, 1, 2, 'llave_luz', 'south')
    lamp(s, 12, 2, 4, 'plafon', 'luces_hall')
    lamp(s, 12, 2, 8, 'plafon', 'luces_hall')
    HIDES['ropero_hall'] = ((15, 0, 8, 'west'), (13, 0, 8, 'east'))
    # ---------------------------------------------------------------- PB corridor: pictures, a lamp every 4
    for x in (12, 8, 4, 0, -4, -8, -12):
        lamp(s, x, 2, 10, 'plafon', 'luces_pasillo_pb')
    for (x, z, k) in ((9, 10, 'foto_cumple'), (2, 10, 'foto_familia'), (-7, 10, 'foto_nona_joven'), (-14, 10, 'crucifijo'),
                      (4, 11, 'foto_choripan'), (-4, 11, 'foto_casamiento'), (-12, 11, 'foto_nelida')):
        K(s, x, 1, z, k, 'south' if z == 10 else 'north')
        group(s, 'cuadros_pasillo', (x, 1, z))
    K(s, 13, 1, 11, 'llave_luz', 'north')
    K(s, -15, 0, 14, 'velas_derretidas_apagadas', 'north')        # the Nona's candles at the top of the basement stair
    group(s, 'velas_sotano', (-15, 0, 14))
    # ---------------------------------------------------------------- COCINA (x -13..-8, z 14..20): counters under the
    # window, the stove, the old fridge, cupboards, the oilcloth table, the knife board, the 3:33 clock; the walk-in
    # despensa (hiding place) in the NE corner
    K(s, -13, 0, 20, 'mesada', 'north')
    K(s, -12, 0, 20, 'mesada_pileta', 'north')
    K(s, -10, 0, 20, 'mesada_cajones', 'north')
    K(s, -9, 0, 20, 'cocina_gas_pava', 'north')
    K(s, -8, 0, 20, 'heladera_abajo', 'north')
    K(s, -8, 1, 20, 'heladera_arriba', 'north')
    K(s, -13, 1, 20, 'escurridor', 'north')
    K(s, -10, 1, 20, 'mate_termo', 'north')
    for (x, y, z, f) in ((-10, 2, 20, 'north'), (-9, 2, 20, 'north'), (-13, 2, 18, 'east'), (-13, 2, 17, 'east')):
        K(s, x, y, z, 'alacena', f)
    K(s, -13, 0, 18, 'mesada', 'east')
    K(s, -13, 1, 18, 'panera', 'east')
    K(s, -13, 0, 17, 'tacho_basura', 'east')
    K(s, -13, 1, 16, 'cuchillos', 'east')
    group(s, 'cuchillos', (-13, 1, 16))
    K(s, -13, 2, 15, 'reloj_cocina_333', 'east')
    K(s, -13, 1, 14, 'almanaque', 'east')
    for x in (-11, -10):
        K(s, x, 0, 17, 'mesa_cocina', 'north')
    for (x, z, f) in ((-12, 17, 'east'), (-9, 17, 'west'), (-11, 16, 'south'), (-10, 18, 'north')):
        K(s, x, 0, z, 'silla_cocina', f)
    K(s, -11, 1, 17, 'plato', 'north')
    lamp(s, -11, 2, 17, 'tubo', 'luces_cocina')
    K(s, -11, 1, 14, 'llave_luz', 'south')
    # the despensa: door at z 16 (facing north), the player's space at z 15, the jar shelf at the back (z 14)
    for z in (14, 15, 16):
        side_wall(s, hs, -9, 0, z, 'cocina')
    s.door('despensa', -8, 0, 16, 'north', mat='casa_puerta_placard', hinge='right')
    K(s, -8, 2, 16, 'pared_cocina', replace=True)
    tall(s, -8, 0, 14, 'estante_frascos', 'south', 'tope_fondo')
    K(s, -8, 2, 15, 'machimbre', replace=True)
    HIDES['despensa'] = ((-8, 0, 15, 'south'), (-8, 0, 17, 'north'))
    # ---------------------------------------------------------------- COMEDOR (x -5..2, z 14..20): the long lustred table
    # with its 8 chairs (the Nona at the east head), the sideboard with the plates, the brass lamp, the Last Supper
    K(s, -3, 0, 17, 'mesa_comedor_extremo', 'north')
    K(s, -2, 0, 17, 'mesa_comedor_centro', 'north')
    K(s, -1, 0, 17, 'mesa_comedor_extremo', 'south')
    sillas = [(0, 17, 'west'), (-1, 16, 'south'), (-1, 18, 'north'), (-2, 16, 'south'), (-2, 18, 'north'),
              (-3, 16, 'south'), (-3, 18, 'north'), (-4, 17, 'east')]
    for (x, z, f) in sillas:
        K(s, x, 0, z, 'silla_comedor', f)
    group(s, 'comedor_sillas', *[(x, 0, z) for (x, z, f) in sillas])
    pair(s, 2, 0, 16, 'west', 'aparador_izq', 'aparador_der')
    for z in (15, 16):
        K(s, 2, 1, z, 'tope_fondo', 'west')
    group(s, 'aparador_platos', (2, 0, 15), (2, 0, 16))
    K(s, -5, 1, 15, 'cuadro_ultima_cena', 'east')
    lamp(s, -2, 2, 17, 'lampara_comedor', 'luces_comedor')
    K(s, 2, 0, 20, 'maceta_malvones', 'west')
    K(s, -5, 0, 20, 'macetas_grupo', 'east')
    for x in (-5, -4, -2, -1):
        K(s, x, 1, 20, 'visillo', 'north')
    K(s, 2, 1, 19, 'foto_familia_ofelia', 'west')
    K(s, -3, 1, 14, 'llave_luz', 'south')
    # ---------------------------------------------------------------- LAVADERO (x 5..8, z 14..20): the breaker board,
    # the meter, the concrete tub, shelves, washing hung indoors
    K(s, 8, 1, 14, 'tablero', 'south')
    group(s, 'tablero', (8, 1, 14))
    K(s, 7, 1, 14, 'medidor_luz', 'south')
    K(s, 8, 0, 20, 'pileta_lavar', 'north')
    K(s, 7, 0, 20, 'balde_secador', 'north')
    tall(s, 5, 0, 16, 'estante_lavadero', 'east', 'tope_fondo')
    tall(s, 5, 0, 17, 'estante_herramientas', 'east', 'tope_fondo')
    K(s, 8, 0, 16, 'cajon_cerveza', 'west')
    K(s, 8, 0, 17, 'bolsa_carbon', 'west')
    for x, k in ((5, 'soga'), (6, 'ropa_tendida'), (7, 'ropa_tendida'), (8, 'soga')):
        K(s, x, 1, 18, k, 'north')
    lamp(s, 6, 2, 16, 'tubo', 'luces_lavadero')
    # ---------------------------------------------------------------- COSTURERO (x 11..14, z 14..20): the sewing table
    # with the cookie tin of buttons, the dress form under a sheet, wool, the old wardrobe, offcuts on the floor
    K(s, 14, 0, 19, 'mesa_cocina', 'west')
    K(s, 14, 1, 19, 'lata_galletitas_abierta', 'west')
    K(s, 13, 0, 19, 'silla_cocina', 'east')
    K(s, 14, 0, 20, 'canasta_lana', 'west')
    K(s, 11, 0, 19, 'tapado_figura', 'east')                      # the dress form (maniqui) under a sheet
    K(s, 11, 0, 17, 'ropero_abajo', 'east')
    K(s, 11, 1, 17, 'ropero_arriba', 'east')
    K(s, 11, 0, 15, 'tapado_sillon', 'east')
    K(s, 14, 0, 15, 'cajas_apiladas', 'west')
    K(s, 13, 0, 16, 'ropa_tirada', 'north')
    tall(s, 14, 0, 17, 'tapado_espejo', 'west')
    lamp(s, 12, 2, 17, 'plafon', 'luces_costurero')
    K(s, 11, 1, 14, 'llave_luz', 'south')


def furnish_1p(s, hs):
    # ---------------------------------------------------------------- corridor: the 2-wide red runner, a lamp every 4,
    # the family photos, the crucifix
    K(s, -15, 5, 10, 'alfombra_punta_der', 'west')
    K(s, -15, 5, 11, 'alfombra_punta_izq', 'west')
    for x in range(-14, 14):
        pair(s, x, 5, 10, 'east', 'alfombra_izq', 'alfombra_der')
    s.set(4, 5, 10, s.get(4, 5, 10))
    for x in (13, 9, 5, 1, -3, -7, -11, -15):
        lamp(s, x, 7, 11, 'plafon', 'luces_pasillo_1p')
    for (x, z, k) in ((12, 10, 'foto_familia_ofelia'), (7, 10, 'foto_cumple'), (-1, 10, 'crucifijo'), (-6, 10, 'foto_nelida'),
                      (-13, 10, 'foto_nona_joven'), (10, 11, 'foto_casamiento'), (3, 11, 'foto_familia'),
                      (-5, 11, 'foto_choripan'), (-12, 11, 'foto_cumple')):
        K(s, x, 6, z, k, 'south' if z == 10 else 'north')
        group(s, 'cuadros_pasillo', (x, 6, z))
    K(s, 13, 6, 10, 'llave_luz', 'south')
    # stair hall: a side table with a vase on the landing, the wedding photo
    K(s, 11, 5, 2, 'mesita_auxiliar', 'south')
    K(s, 11, 6, 2, 'carpetita_florero', 'south')
    K(s, 11, 6, 5, 'foto_casamiento', 'east')
    lamp(s, 12, 7, 5, 'plafon', 'luces_esc_principal')
    # ---------------------------------------------------------------- MATRIMONIAL (x -15..-8, z 2..7): the raised double
    # bed against the east wall, bedside tables and lamps, the dresser with its mirror (tocador), the 3-door placard
    placard(s, hs, 'ropero_matrimonial', [(-15, 5, 6), (-14, 5, 6), (-13, 5, 6)], 'south', 'matrimonial')
    raised_bed(s, [(-8, 4, 'cama_matrimonial_cabecera_der', 'west'), (-8, 3, 'cama_matrimonial_cabecera_izq', 'west'),
                   (-9, 4, 'cama_matrimonial_pie_der', 'west'), (-9, 3, 'cama_matrimonial_pie_izq', 'west')], 5)
    HIDES['cama_matrimonial'] = ((-9, 5, 4, 'west'), (-10, 5, 4, 'east'))
    for z in (2, 5):
        K(s, -8, 5, z, 'mesa_luz', 'west')
        lamp(s, -8, 6, z, 'velador', 'luces_matrimonial', facing='west')
    pair(s, -14, 5, 2, 'south', 'comoda_izq', 'comoda_der')
    for x in (-15, -14):
        K(s, x, 6, 2, 'tope_fondo', 'south')
    K(s, -15, 6, 5, 'foto_casamiento', 'east')
    K(s, -15, 5, 4, 'sillon_individual', 'east')
    K(s, -10, 5, 5, 'pantuflas', 'east')
    K(s, -12, 5, 3, 'ropa_tirada', 'south')
    lamp(s, -11, 7, 4, 'plafon', 'luces_matrimonial')
    pair(s, -12, 6, 2, 'south', 'visillo', 'visillo')
    pair(s, -9, 6, 2, 'south', 'visillo', 'visillo')
    K(s, -11, 6, 7, 'llave_luz', 'north')
    # ---------------------------------------------------------------- CUARTO DEL NONO (x -5..0, z 2..7): untouched since
    # the funeral: the made bed, his bedside lamp (the one light left on upstairs), the mirrors covered with sheets
    K(s, -5, 5, 4, 'cama_nona_cabecera', 'east')
    K(s, -4, 5, 4, 'cama_nona_pie', 'east')
    K(s, -5, 5, 3, 'mesa_luz', 'east')
    lamp(s, -5, 6, 3, 'velador', 'luces_cuarto_nono', lit=True, facing='east')
    K(s, -5, 7, 4, 'crucifijo', 'east')
    tall(s, 0, 5, 3, 'tapado_espejo', 'west')
    tall(s, -5, 5, 7, 'tapado_espejo', 'north')
    K(s, 0, 5, 6, 'ropero_abajo', 'west')
    K(s, 0, 6, 6, 'ropero_arriba', 'west')
    K(s, -1, 5, 2, 'tapado_sillon', 'south')
    K(s, 0, 6, 5, 'foto_nelida', 'west')
    K(s, -4, 5, 2, 'cajas_apiladas', 'south')
    lamp(s, -3, 7, 4, 'plafon', 'luces_cuarto_nono')
    # ---------------------------------------------------------------- HUESPEDES (x 2..8, z 2..7): the player's room: a
    # raised old single bed, a bedside table, a chair, the crucifix, a placard (hiding place)
    placard(s, hs, 'ropero_huespedes', [(7, 5, 6), (8, 5, 6)], 'south', 'huespedes')
    raised_bed(s, [(2, 4, 'cama_nona_cabecera', 'east'), (3, 4, 'cama_nona_pie', 'east')], 5)
    HIDES['cama_huespedes'] = ((3, 5, 4, 'east'), (4, 5, 4, 'west'))
    K(s, 2, 5, 3, 'mesa_luz', 'east')
    lamp(s, 2, 6, 3, 'velador', 'luces_huespedes', facing='east')
    K(s, 2, 5, 5, 'silla_comedor', 'east')
    K(s, 3, 7, 2, 'crucifijo', 'south')
    K(s, 8, 5, 2, 'mesita_auxiliar', 'west')
    K(s, 8, 6, 2, 'mate_termo_mesa', 'west')
    lamp(s, 5, 7, 4, 'plafon', 'luces_huespedes')
    pair(s, 5, 6, 2, 'south', 'visillo', 'visillo')
    K(s, 3, 6, 7, 'llave_luz', 'north')
    # ---------------------------------------------------------------- LUCIA (x -12..-7, z 14..20): the raised canopy bed,
    # the doll shelves on the east wall, the desk with the notebook, the toy chest, the placard (hiding place)
    placard(s, hs, 'ropero_lucia', [(-12, 5, 15), (-11, 5, 15)], 'north', 'lucia')
    for (x, k) in ((-12, 'cama_dosel_cabecera'), (-11, 'cama_dosel_pie')):
        s.set(x, 5, 18, AIR)
        tall(s, x, 6, 18, k, 'east')
    HIDES['cama_lucia'] = ((-11, 5, 18, 'east'), (-10, 5, 18, 'west'))
    K(s, -12, 5, 19, 'mesa_luz', 'east')
    lamp(s, -12, 6, 19, 'lampara_hongo', 'luces_lucia', facing='east')
    shelves = []
    for z, k in ((17, 'estante_munecas_1'), (18, 'estante_munecas_2'), (19, 'estante_munecas_3')):
        tall(s, -7, 5, z, k, 'west', 'tope_fondo')
        shelves.append((-7, 5, z))
    group(s, 'estante_munecas', *shelves)
    lamp(s, -8, 5, 20, 'escritorio_lucia', 'luces_lucia', facing='north')
    K(s, -8, 5, 19, 'silla_nena', 'south')
    K(s, -7, 5, 20, 'cuaderno_lemaza', 'north')
    K(s, -7, 6, 20, 'dibujo_lemaza', 'north')
    K(s, -12, 5, 17, 'baul_juguetes', 'east')
    for (x, z, f) in ((-10, 17, 'north'), (-9, 17, 'east'), (-10, 18, 'west'), (-9, 18, 'south')):
        K(s, x, 5, z, 'alfombra_lucia', f)
    K(s, -9, 5, 20, 'juguetes', 'north')
    K(s, -10, 5, 16, 'mochila', 'south')
    lamp(s, -9, 7, 17, 'plafon', 'luces_lucia')
    pair(s, -10, 6, 20, 'north', 'cortina_rosa_izq', 'cortina_rosa_der')
    K(s, -9, 6, 14, 'llave_luz', 'south')
    # ---------------------------------------------------------------- TOTI (x -4..1, z 14..20): the raised unmade bed, the
    # gaming desk, posters, the toy chest, the louvred placard (hiding place)
    placard(s, hs, 'ropero_toti', [(-4, 5, 15), (-3, 5, 15)], 'north', 'toti')
    raised_bed(s, [(1, 18, 'cama_toti_cabecera', 'west'), (0, 18, 'cama_toti_pie', 'west')], 5)
    HIDES['cama_toti'] = ((0, 5, 18, 'west'), (-1, 5, 18, 'east'))
    pair(s, -4, 5, 18, 'east', 'escritorio_pc_izq_apagado', 'escritorio_pc_der_apagado')
    group(s, 'luces_toti', (-4, 5, 18), (-4, 5, 19))
    K(s, -3, 5, 18, 'silla_gamer', 'west')
    K(s, 1, 5, 15, 'baul_juguetes', 'west')
    for (x, y, z, k, f) in ((-4, 6, 17, 'poster_toti_1', 'east'), (1, 6, 19, 'poster_toti_2', 'west'),
                            (-4, 7, 20, 'poster_juego', 'north'), (-3, 6, 20, 'poster_banda', 'north'),
                            (1, 7, 16, 'poster_toti_3', 'west')):
        K(s, x, y, z, k, f)
    K(s, -1, 5, 16, 'zapatillas', 'south')
    K(s, -2, 5, 19, 'ropa_tirada', 'north')
    K(s, 1, 6, 17, 'cargador', 'west')
    K(s, -1, 5, 20, 'pelota', 'north')
    lamp(s, -1, 7, 17, 'plafon', 'luces_toti')
    K(s, -1, 6, 14, 'llave_luz', 'south')
    # ---------------------------------------------------------------- BANO 1P (x 4..8, z 14..20): the tub with its
    # curtain (hiding place) against the back wall, toilet, bidet, basin with the mirrored cabinet
    pair(s, 7, 5, 20, 'north', 'banadera_izq', 'banadera_der')
    K(s, 7, 6, 20, 'cortina_ducha', 'north')
    K(s, 8, 6, 20, 'cortina_ducha_corrida', 'north')
    K(s, 8, 7, 20, 'ducha', 'north')
    HIDES['banera'] = ((7, 5, 20, 'north'), (7, 5, 18, 'south'))
    K(s, 4, 5, 18, 'inodoro', 'east')
    K(s, 4, 5, 17, 'bidet', 'east')
    K(s, 4, 6, 19, 'portarrollo', 'east')
    K(s, 8, 5, 16, 'lavatorio', 'west')
    K(s, 8, 6, 16, 'botiquin', 'west')
    lamp(s, 8, 7, 16, 'aplique_bano', 'luces_bano_1p', facing='west')
    K(s, 8, 6, 18, 'toallero', 'west')
    K(s, 6, 5, 18, 'alfombra_bano', 'north')
    lamp(s, 6, 7, 17, 'plafon', 'luces_bano_1p')
    K(s, 5, 6, 14, 'llave_luz', 'south')
    # ---------------------------------------------------------------- TRASTERO (x 11..14, z 14..20): junk around the
    # steep stair to the attic (kept clear from the corridor opening to its foot)
    K(s, 11, 5, 14, 'cajas_apiladas', 'east')
    K(s, 11, 5, 15, 'sillas_apiladas', 'east')
    tall(s, 11, 5, 17, 'tapado_ropero', 'east')
    K(s, 11, 5, 18, 'tapado_sillon', 'east')
    K(s, 11, 5, 19, 'caja_abierta', 'east')
    K(s, 11, 5, 20, 'cajas_apiladas', 'north')
    K(s, 12, 5, 20, 'balde_secador', 'north')
    lamp(s, 12, 7, 17, 'foco', 'luces_trastero')


def furnish_attic(s, hs):
    """Collar beams under the roof with bare bulbs, the junk of seventy years in clusters, the baulera under the front
    eave (the trunk store, a hiding place behind a low door)."""
    for x in (-13, -5, 3, 11):
        for z in range(5, 18):
            K(s, x, 13, z, 'madera_escalera', replace=True)
        lamp(s, x, 12, 11, 'foco', 'luces_altillo')
    # the baulera: knee wall at z 4 (y 10..12), the door in the middle, a trunk each side of the player's space
    for x in range(-3, 4):
        for y in (10, 11, 12):
            if x == 0 and y < 12:
                continue
            K(s, x, y, 4, 'machimbre', replace=True)
    s.door('baul_altillo', 0, 10, 4, 'north', mat='casa_puerta_placard', hinge='left')
    for x in (-3, 3):
        for y in (10, 11):
            K(s, x, y, 3, 'machimbre', replace=True)
    K(s, -1, 10, 3, 'baul_juguetes', 'east')
    K(s, 1, 10, 3, 'cajon_cerveza', 'west')
    K(s, -2, 10, 3, 'cajas_apiladas', 'north')
    K(s, 2, 10, 3, 'caja_abierta', 'north')
    for x in range(-2, 3):
        K(s, x, 10, 2, 'machimbre', replace=True)
    HIDES['baul_altillo'] = ((0, 10, 3, 'south'), (0, 10, 5, 'north'))
    # clusters: dolls and toys, the sheeted dress forms, old furniture, boxes, chairs
    for (x, z, k, f) in ((-12, 8, 'tapado_figura', 'south'), (-11, 9, 'tapado_figura', 'east'), (-13, 10, 'tapado_figura', 'east'),
                         (-9, 7, 'baul_juguetes', 'south'), (-8, 7, 'juguetes', 'south'), (-7, 8, 'mecedora', 'south'),
                         (-2, 14, 'tapado_mesa', 'north'), (-1, 15, 'sillas_apiladas', 'north'), (-3, 15, 'cajas_apiladas', 'north'),
                         (5, 7, 'tapado_sillon', 'south'), (6, 7, 'cajas_apiladas', 'south'), (7, 8, 'caja_abierta', 'west'),
                         (8, 15, 'baul_juguetes', 'north'), (9, 15, 'cajon_cerveza', 'north'), (-10, 15, 'tapado_sillon', 'north'),
                         (-12, 15, 'cajas_apiladas', 'north'), (1, 9, 'pelota', 'north'), (-6, 12, 'canasta_lana', 'east')):
        K(s, x, 10, z, k, f)
    for (x, z, f) in ((-14, 12, 'east'), (6, 14, 'north'), (-4, 7, 'south')):
        tall(s, x, 10, z, 'tapado_ropero', f)
    tall(s, -14, 10, 9, 'tapado_espejo', 'east')
    tall(s, 2, 10, 15, 'tapado_espejo', 'north')
    K(s, 12, 11, 11, 'estante_munecas_vacio', 'west')     # the empty doll shelf against the chimney? (on a box)
    K(s, 12, 10, 11, 'cajas_apiladas', 'west')


def furnish_basement(s):
    # ---------------------------------------------------------------- SOTANO (x -15..-4, z 14..21): the boiler, the
    # Nona's preserves, sheeted furniture with aisles round it, bare bulbs, candles towards the cracked wall
    lamp(s, -11, -3, 17, 'foco', 'luces_sotano')
    lamp(s, -6, -3, 17, 'foco', 'luces_sotano')
    tall(s, -4, -5, 21, 'caldera', 'west')
    s.set(-4, -5, 21, s.get(-4, -5, 21).replace('caldera', 'caldera_apagada'))
    group(s, 'caldera', (-4, -5, 21))
    K(s, -4, -5, 20, 'damajuana', 'west')
    for (x, k) in ((-13, 'estante_frascos'), (-12, 'estante_frascos_2'), (-11, 'estante_frascos'), (-8, 'estante_frascos_2')):
        tall(s, x, -5, 14, k, 'south', 'tope_fondo')
    K(s, -10, -5, 14, 'damajuana', 'south')
    K(s, -9, -5, 18, 'tapado_mesa', 'north')
    K(s, -10, -5, 18, 'tapado_sillon', 'east')
    K(s, -8, -5, 19, 'tapado_figura', 'west')
    tall(s, -9, -5, 20, 'tapado_ropero', 'south')
    tall(s, -11, -5, 20, 'tapado_espejo', 'east')
    K(s, -13, -5, 21, 'cajas_apiladas', 'north')
    K(s, -12, -5, 21, 'caja_abierta', 'north')
    K(s, -7, -5, 21, 'bolsa_carbon', 'north')
    K(s, -6, -5, 21, 'bolsa_carbon_volcada', 'north')
    K(s, -14, -5, 16, 'sillas_apiladas', 'east')
    K(s, -14, -5, 14, 'balde_secador', 'east')
    for (x, z, k) in ((-14, 20, 'velas_derretidas_apagadas'), (-11, 19, 'velas_sueltas_apagadas'),
                      (-7, 18, 'velas_derretidas_apagadas'), (-5, 16, 'velas_sueltas_apagadas'),
                      (-5, 19, 'velas_derretidas_apagadas')):
        K(s, x, -5, z, k, 'north')
        group(s, 'velas_sotano', (x, -5, z))
    # ---------------------------------------------------------------- the sealed 1961 room: the old salt circle round
    # the iron bed, melted candles, the stole on a nail, the scratches, soot
    cx, cz = 3, 17
    for p, (i, j) in {'a': (0, 2), 'b': (1, 2), 'c': (2, 2), 'd': (2, 1), 'e': (2, 0), 'f': (1, 1)}.items():
        for (x, z, f) in ((cx + i, cz + j, 'north'), (cx - 1 - j, cz + i, 'east'), (cx - 1 - i, cz - 1 - j, 'south'),
                          (cx + j, cz - 1 - i, 'west')):
            K(s, x, -6, z, 'sal_61_a_rota' if (p, f) == ('a', 'north') else f'sal_61_{p}', f)
    K(s, 2, -6, 16, 'cama_hierro_cabecera', 'south')
    K(s, 2, -6, 17, 'cama_hierro_pie', 'south')
    velas = [(3, -6, 15), (1, -6, 16), (4, -6, 17), (3, -6, 18), (6, -6, 19)]
    for (x, y, z) in velas[:4]:
        K(s, x, y, z, 'velas_derretidas_apagadas', 'north')
    K(s, 6, -6, 19, 'velas_sueltas_apagadas', 'west')
    group(s, 'cuarto61_velas', *velas)
    for y, k in ((-6, 'pared_61_hollin'), (-5, 'pared_61_hollin_alto'), (-4, 'pared_61_hollin_alto')):
        K(s, 7, y, 19, k)
    K(s, -1, -5, 14, 'estola_anselmo', 'east')
    K(s, -1, -6, 18, 'rayones_latin', 'east')
    group(s, 'rayones', (-1, -6, 18))
    K(s, 6, -6, 16, 'rayones_lemaza', 'west')
    K(s, 6, -6, 13 + 1, 'rayones_lemaza_chico', 'west')
    K(s, 4, -6, 20, 'rayones_lemaza_chico', 'north')
    K(s, 1, -6, 20, 'rayones_dibujo', 'north')
    K(s, -1, -6, 20, 'rayones_palitos', 'north')
    K(s, -1, -6, 15, 'manos_hollin', 'east')
    K(s, 6, -5, 18, 'manos_hollin', 'west')
    K(s, 0, -6, 19, 'lata_galletitas_vieja', 'east')
    K(s, 0, -6, 15, 'zapatitos', 'east')
    K(s, 2, -6, 18, 'misal', 'north')


# ===================================================================================================== outside
def grounds(s):
    """The lot: lawn (vanilla, overgrown) everywhere nothing else is laid; the dirt track outside the gate."""
    for x in range(LX0, LX1 + 1):
        for z in range(LZ0, LZ1 + 1):
            if s.get(x, -1, z) is None:
                V(s, x, -1, z, 'grass_block')


def build():
    CLASHES.clear()
    WINDOWS['pb'].clear()
    WINDOWS['1p'].clear()
    WINDOWS['altillo'].clear()
    s = Site('casa', PALETTE)
    hs = House(s)
    shell(s, hs)
    ground_floor(s, hs)
    first_floor(s, hs)
    attic(s, hs)
    roof(s, hs)
    porch(s)
    basement(s, hs)
    grounds(s)
    s.point('spawn', 4, 0, -8, 'south')
    s.point('llegada', 4, 0, -8, 'south')
    s.finish_conflicts = hs.check_finishes()
    if CLASHES:
        raise AssertionError('casa: placements overwrite furniture: ' +
                             '; '.join(f'{p} {old} <- {new}' for (p, old, new) in CLASHES[:20]))
    return s


# ===================================================================================================== plan images
def plan_png(s, path, levels=((-6, 'sotano/61 y=-5/-6'), (0, 'PB y=0'), (5, '1P y=5'), (10, 'altillo y=10'))):
    """Top-down plans (one per storey) coloured by kind of block, with the marker points."""
    from PIL import Image, ImageDraw
    x0, y0, z0, x1, y1, z1 = s.bounds()
    x0, x1, z0, z1 = max(x0, LX0 - 3), min(x1, LX1 + 3), max(z0, LZ0 - 10), min(z1, LZ1 + 2)
    k = 9
    W, D = (x1 - x0 + 1) * k, (z1 - z0 + 1) * k
    img = Image.new('RGB', (W * 2 + 10, (D + 16) * 2 + 10), (20, 24, 20))
    d = ImageDraw.Draw(img)
    for n, (ly, title) in enumerate(levels):
        ox = (n % 2) * (W + 10)
        oz = (n // 2) * (D + 26)
        d.text((ox + 4, oz + 2), title, fill=(255, 255, 255))
        for x in range(x0, x1 + 1):
            for z in range(z0, z1 + 1):
                lyy = ly
                if ly == -6 and x < -2:
                    lyy = -5
                st = s.get(x, lyy, z)
                below = s.get(x, lyy - 1, z)
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
                                             'medianera', 'zocalo_', 'murito', 'pilar', 'divisoria', 'machimbre')):
                    col = (215, 215, 205)
                elif 'sal_' in name:
                    col = (250, 250, 250)
                elif name in ('grass_block', 'short_grass', 'tall_grass', 'fern'):
                    col = (40, 70, 35)
                else:
                    col = (90, 150, 90)
                X, Z = ox + (x - x0) * k, oz + 14 + (z - z0) * k
                d.rectangle([X, Z, X + k - 1, Z + k - 1], fill=col)
        for name, (x, y, z, yaw) in s.markers['points'].items():
            ref = -5.5 if ly == -6 else ly
            if abs(y - ref) > 2 or not (x0 <= x <= x1 and z0 <= z <= z1):
                continue
            X, Z = ox + (x - x0) * k + k // 2, oz + 14 + (z - z0) * k + k // 2
            d.ellipse([X - 3, Z - 3, X + 3, Z + 3], fill=(230, 40, 40))
            d.text((X + 4, Z - 5), name, fill=(255, 230, 120))
    img.save(path)


if __name__ == '__main__':
    site = build()
    out, n, pal = site.export()
    print(f'{out}: {n} blocks, {pal} states')
    x0, y0, z0, x1, y1, z1 = site.bounds()
    print(f'bounds x {x0}..{x1}  y {y0}..{y1}  z {z0}..{z1}  ({x1 - x0 + 1} x {y1 - y0 + 1} x {z1 - z0 + 1})')
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
