"""DEAD LINE case sites authored in Python.

A site is a sparse voxel map of block states plus named markers. `Site.export()` writes
`src/main/resources/data/deadline/sites/<key>.json`, which the mod places in batches when a case starts
(com.deadline.site.SitePlacer) and which the case director reads for its markers.

Coordinates are relative to the site origin: x east, y up (y=0 is the first air layer above the ground, the
grass is y=-1), z south. Layouts address blocks with SEMANTIC material names ('wall', 'floor_checker', 'desk'...)
that a palette maps to real block ids, so a building can be laid out before its building kit exists and switch
to the kit blocks later by editing the palette only.

File format (JSON):
  size [W,H,D], min [x,y,z]          bounding box of the placed blocks
  palette [state, ...]               index 0 is unused ("leave the world alone"); states look like
                                     "deadline:colegio_pupitre[facing=north]" or "minecraft:air"
  data                               base64(zlib(uint16 little endian)), index = ((y*D)+z)*W+x, y-major so floors
                                     are placed before what stands on them
  markers                            points {name: [x,y,z,yaw]}, areas {name: [x1,y1,z1,x2,y2,z2]} (inclusive
                                     block corners), groups {name: [[x,y,z], ...]} (fixtures such as lamps),
                                     doors {name: [x,y,z]} (lower half), props {name: {pos, state}},
                                     writes {name: {pos, facing, width}} (chalk/board text anchors)
"""
import base64
import json
import os
import struct
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.join(ROOT, 'src/main/resources/data/deadline/sites')

FACINGS = ('north', 'east', 'south', 'west')
YAW = {'south': 0.0, 'west': 90.0, 'north': 180.0, 'east': -90.0}


def state(block, **props):
    """'deadline:x' + {'facing': 'north'} -> 'deadline:x[facing=north]' (block may omit the namespace)."""
    if ':' not in block:
        block = 'deadline:' + block
    if not props:
        return block
    return block + '[' + ','.join(f'{k}={str(v).lower()}' for k, v in sorted(props.items())) + ']'


def rotate_facing(f, turns):
    return FACINGS[(FACINGS.index(f) + turns) % 4]


class Palette:
    """Semantic material -> block id. A material may map to a list (picked per position for variety)."""

    def __init__(self, table):
        self.table = dict(table)

    def resolve(self, name, x, y, z):
        v = self.table.get(name, name)
        if isinstance(v, (list, tuple)):
            h = (x * 73856093) ^ (y * 19349663) ^ (z * 83492791)
            v = v[h % len(v)]
        return v


class Site:
    def __init__(self, key, palette):
        self.key = key
        self.pal = palette
        self.blocks = {}
        self.markers = {'points': {}, 'areas': {}, 'groups': {}, 'doors': {}, 'props': {}, 'writes': {}}

    # ------------------------------------------------------------------ blocks
    def set(self, x, y, z, mat, **props):
        block = self.pal.resolve(mat, x, y, z)
        self.blocks[(x, y, z)] = state(block, **props)

    def get(self, x, y, z):
        return self.blocks.get((x, y, z))

    def clear(self, x, y, z):
        self.blocks.pop((x, y, z), None)

    def fill(self, x1, y1, z1, x2, y2, z2, mat, **props):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            for y in range(min(y1, y2), max(y1, y2) + 1):
                for z in range(min(z1, z2), max(z1, z2) + 1):
                    self.set(x, y, z, mat, **props)

    def air(self, x1, y1, z1, x2, y2, z2):
        self.fill(x1, y1, z1, x2, y2, z2, 'minecraft:air')

    def room(self, x1, z1, x2, z2, y1, y2, wall='wall', floor='floor', ceiling='ceiling', floor_y=None):
        """Hollow box: floor at y1-1, ceiling at y2+1, walls on the outer ring x1..x2 / z1..z2, air inside."""
        self.fill(x1, y1 - 1, z1, x2, y1 - 1, z2, floor)
        self.fill(x1, y2 + 1, z1, x2, y2 + 1, z2, ceiling)
        for y in range(y1, y2 + 1):
            for x in range(x1, x2 + 1):
                self.set(x, y, z1, wall)
                self.set(x, y, z2, wall)
            for z in range(z1, z2 + 1):
                self.set(x1, y, z, wall)
                self.set(x2, y, z, wall)
        self.air(x1 + 1, y1, z1 + 1, x2 - 1, y2, z2 - 1)

    def door(self, name, x, y, z, facing, mat='door', hinge='left', open_=False):
        """Two-block door; `facing` is the direction a player walking through it faces when entering."""
        self.set(x, y, z, mat, facing=facing, half='lower', hinge=hinge, open=open_, powered=False)
        self.set(x, y + 1, z, mat, facing=facing, half='upper', hinge=hinge, open=open_, powered=False)
        if name:
            self.markers['doors'][name] = [x, y, z]

    def furniture(self, x, y, z, mat, facing='north'):
        self.set(x, y, z, mat, facing=facing)

    def light(self, x, y, z, level, group=None):
        """Invisible light source (minecraft:light). Groups can be switched on/off by the director."""
        self.blocks[(x, y, z)] = state('minecraft:light', level=level, waterlogged=False)
        if group:
            self.markers['groups'].setdefault(group, []).append([x, y, z])

    def fixture(self, group, x, y, z):
        self.markers['groups'].setdefault(group, []).append([x, y, z])

    # ------------------------------------------------------------------ markers
    def point(self, name, x, y, z, facing_or_yaw='south'):
        yaw = YAW[facing_or_yaw] if isinstance(facing_or_yaw, str) else float(facing_or_yaw)
        self.markers['points'][name] = [x, y, z, yaw]

    def area(self, name, x1, y1, z1, x2, y2, z2):
        self.markers['areas'][name] = [min(x1, x2), min(y1, y2), min(z1, z2), max(x1, x2), max(y1, y2), max(z1, z2)]

    def prop(self, name, x, y, z, block, **props):
        self.markers['props'][name] = {'pos': [x, y, z], 'state': state(block, **props)}

    def write(self, name, x, y, z, facing, width=3.0):
        self.markers['writes'][name] = {'pos': [x, y, z], 'facing': facing, 'width': width}

    # ------------------------------------------------------------------ export
    def bounds(self):
        xs = [p[0] for p in self.blocks]
        ys = [p[1] for p in self.blocks]
        zs = [p[2] for p in self.blocks]
        return min(xs), min(ys), min(zs), max(xs), max(ys), max(zs)

    def export(self):
        x0, y0, z0, x1, y1, z1 = self.bounds()
        W, H, D = x1 - x0 + 1, y1 - y0 + 1, z1 - z0 + 1
        palette = ['']
        index = {}
        data = bytearray(W * H * D * 2)
        for (x, y, z), st in self.blocks.items():
            i = index.get(st)
            if i is None:
                i = index[st] = len(palette)
                palette.append(st)
            n = ((y - y0) * D + (z - z0)) * W + (x - x0)
            struct.pack_into('<H', data, n * 2, i)
        doc = {'key': self.key, 'size': [W, H, D], 'min': [x0, y0, z0], 'palette': palette,
               'data': base64.b64encode(zlib.compress(bytes(data), 9)).decode(), 'markers': self.markers}
        os.makedirs(OUT, exist_ok=True)
        path = os.path.join(OUT, self.key + '.json')
        with open(path, 'w') as fh:
            json.dump(doc, fh, separators=(',', ':'))
        return path, len(self.blocks), len(palette) - 1

    def unknown_blocks(self, known):
        """Block ids used by the site that are neither vanilla nor in `known` (exported kit keys)."""
        out = set()
        for st in self.blocks.values():
            bid = st.split('[')[0]
            if bid.startswith('deadline:') and bid[9:] not in known:
                out.add(bid)
        return sorted(out)
