"""DEAD LINE building kit: custom blocks and furniture defined in Python, exported to Minecraft.

One definition produces: painted texture(s) (32 px per block, twice vanilla), block model JSON, blockstate, item model,
lang names, the generated Java registration (ModBlocksGen) and preview data for the three.js renderer.

COORDINATES (Minecraft block-model space): x 0..16 west->east, y 0..16 bottom->top (+Y is UP), z 0..16 north->south.
Elements may extend from -16 to 32 for furniture bigger than one block (collision is clipped to the block).
Furniture is authored FACING NORTH: its front is the z=0 side. Rotated variants (east/south/west) are generated.

TEXTURE ORIENTATION (what a material sees): every face is painted as seen from OUTSIDE the element:
ctx.i/ctx.j = pixel column/row (0 = left/top as you look at that face), ctx.s/ctx.t = 0..1 across the face,
ctx.pos = block-space position of the texel centre, ctx.n = outward normal, ctx.face in
{'north','south','west','east','up','down'} (north is the front of north-facing furniture).
The 'up' face has north at the top of the image; 'down' has south at the top.
Do NOT bake directional lighting into block textures (Minecraft shades faces itself); paint material, wear, AO-ish
crevices and edges only.
"""
import json
import math
import os
import zlib

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
ASSETS = os.path.join(ROOT, 'src/main/resources/assets/deadline')
NS = 'deadline'
PX = 2  # texture pixels per model unit (32 px per block)

FACES = ('north', 'south', 'west', 'east', 'up', 'down')
NORMALS = {'north': (0, 0, -1), 'south': (0, 0, 1), 'west': (-1, 0, 0), 'east': (1, 0, 0), 'up': (0, 1, 0), 'down': (0, -1, 0)}

REGISTRY = []


class Ctx:
    """Everything a material needs to colour one texel."""
    __slots__ = ('pos', 'n', 'face', 's', 't', 'i', 'j', 'w', 'h', 'part', 'block', 'rng', 'seed')

    def __init__(self, pos, n, face, s, t, i, j, w, h, part, block, rng, seed):
        self.pos, self.n, self.face, self.s, self.t = pos, n, face, s, t
        self.i, self.j, self.w, self.h = i, j, w, h
        self.part, self.block, self.rng, self.seed = part, block, rng, seed

    @property
    def x(self):
        return self.pos[0]

    @property
    def y(self):
        return self.pos[1]

    @property
    def z(self):
        return self.pos[2]

    def edge(self):
        return min(self.i, self.j, self.w - 1 - self.i, self.h - 1 - self.j)


# ---------------------------------------------------------------------------------------------- parts
class Part:
    """One box element. frm/to in block units. mat: fn(ctx)->rgba|None (None = transparent, needs render='cutout').

    faces: subset of FACES to emit (default all). rot: (axis, angle, origin) with angle in {-45,-22.5,0,22.5,45}.
    decals: {face: fn(img, u0, v0, w, h)} painted after the material. shade: False for emissive-looking parts.
    """

    def __init__(self, frm, to, mat=None, faces=None, rot=None, decals=None, shade=True, name=None, cull=True):
        self.frm = tuple(float(v) for v in frm)
        self.to = tuple(float(v) for v in to)
        self.mat = mat
        self.faces = tuple(faces) if faces else FACES
        self.rot = rot
        self.decals = decals or {}
        self.shade = shade
        self.name = name
        self.cull = cull
        self.uv = {}  # face -> (u_px, v_px, w_px, h_px)

    def size(self):
        return tuple(self.to[i] - self.frm[i] for i in range(3))

    def face_px(self, face):
        w, h, d = self.size()
        dims = {'north': (w, h), 'south': (w, h), 'west': (d, h), 'east': (d, h), 'up': (w, d), 'down': (w, d)}[face]
        return max(1, int(round(dims[0] * PX))), max(1, int(round(dims[1] * PX)))

    def point(self, face, s, t):
        (x1, y1, z1), (x2, y2, z2) = self.frm, self.to
        W, H, D = x2 - x1, y2 - y1, z2 - z1
        if face == 'north':
            return (x2 - s * W, y2 - t * H, z1)
        if face == 'south':
            return (x1 + s * W, y2 - t * H, z2)
        if face == 'west':
            return (x1, y2 - t * H, z1 + s * D)
        if face == 'east':
            return (x2, y2 - t * H, z2 - s * D)
        if face == 'up':
            return (x1 + s * W, y2, z1 + t * D)
        return (x1 + s * W, y1, z2 - t * D)  # down


def box(frm, to, mat=None, **kw):
    return Part(frm, to, mat, **kw)


def plane(frm, to, mat=None, **kw):
    """A zero-thickness plane (one size 0): only the two meaningful faces are emitted."""
    size = [to[i] - frm[i] for i in range(3)]
    axis = size.index(0) if 0 in size else None
    faces = {0: ('west', 'east'), 1: ('up', 'down'), 2: ('north', 'south')}.get(axis, FACES)
    kw.setdefault('faces', faces)
    kw.setdefault('cull', False)
    return Part(frm, to, mat, **kw)


# ---------------------------------------------------------------------------------------------- blocks
class Block:
    """Base for every exported block. kind decides the Java class and the blockstate."""
    kind = 'decor'

    def __init__(self, key, name_es, name_en, kit='misc', light=0, sound='wood', render='cutout', collision='auto',
                 variants=1, breakable=False, desc=None, tags=()):
        self.key = key
        self.name_es, self.name_en = name_es, name_en
        self.kit = kit
        self.light = light
        self.sound = sound
        self.render = render  # solid | cutout | translucent
        self.collision = collision  # auto | full | none
        self.variants = variants
        self.breakable = breakable
        self.desc = desc
        self.tags = tags
        REGISTRY.append(self)


class Furniture(Block):
    """Element-based model (facing north by default). Rotates with the player when placed if directional=True."""
    kind = 'furniture'

    def __init__(self, key, name_es, name_en, parts, directional=True, mat=None, ao=True, **kw):
        super().__init__(key, name_es, name_en, **kw)
        self.parts = list(parts)
        self.directional = directional
        self.mat = mat
        self.ao = ao


class Cube(Block):
    """Full block. mat paints every face; or per-face materials via faces={'up': mat, 'side': mat, 'down': mat}.
    variants>1 renders several random textures (seeded) chosen randomly per placed block."""
    kind = 'cube'

    def __init__(self, key, name_es, name_en, mat=None, faces=None, animated=None, **kw):
        kw.setdefault('render', 'solid')
        kw.setdefault('collision', 'full')
        super().__init__(key, name_es, name_en, **kw)
        self.mat = mat
        self.face_mats = faces or {}
        self.animated = animated  # (frames, frametime) -> mat receives ctx.seed as frame index

    def mat_for(self, face):
        if face in self.face_mats:
            return self.face_mats[face]
        if face in ('north', 'south', 'west', 'east') and 'side' in self.face_mats:
            return self.face_mats['side']
        return self.face_mats.get('all', self.mat)


class Slab(Block):
    kind = 'slab'

    def __init__(self, key, name_es, name_en, of, **kw):
        kw.setdefault('render', 'solid')
        super().__init__(key, name_es, name_en, **kw)
        self.of = of  # Cube whose texture is reused


class Stairs(Block):
    kind = 'stairs'

    def __init__(self, key, name_es, name_en, of, **kw):
        kw.setdefault('render', 'solid')
        super().__init__(key, name_es, name_en, **kw)
        self.of = of


class Door(Block):
    """Two-block door (vanilla door logic, opens by hand). mat paints 32x64: ctx.face is 'bottom' or 'top' half."""
    kind = 'door'

    def __init__(self, key, name_es, name_en, mat, **kw):
        kw.setdefault('render', 'cutout')
        super().__init__(key, name_es, name_en, **kw)
        self.mat = mat


class Trapdoor(Block):
    kind = 'trapdoor'

    def __init__(self, key, name_es, name_en, mat, **kw):
        kw.setdefault('render', 'cutout')
        super().__init__(key, name_es, name_en, **kw)
        self.mat = mat


# ---------------------------------------------------------------------------------------------- painting
def shash(*parts):
    """Stable hash (Python's hash() is salted per process)."""
    return zlib.crc32('|'.join(str(p) for p in parts).encode()) & 0xffff


def _rng(seed):
    return np.random.default_rng(seed)


def _paint_face(img, rect, part, face, mat, block, seed, label=None):
    u0, v0, fw, fh = rect
    rng = _rng(seed)
    px = img.load()
    for j in range(fh):
        for i in range(fw):
            s, t = (i + 0.5) / fw, (j + 0.5) / fh
            ctx = Ctx(part.point(face, s, t), NORMALS[face], label or face, s, t, i, j, fw, fh, part, block, rng, seed)
            c = mat(ctx) if mat else (255, 0, 255, 255)
            if c is not None:
                px[u0 + i, v0 + j] = tuple(int(v) for v in c)


def _pack(rects, start=32):
    """Shelf-pack face rects into the smallest power-of-two square texture."""
    size = start
    while size <= 512:
        used = np.zeros((size, size), bool)
        out = []
        ok = True
        for (w, h) in rects:
            placed = None
            if w > size or h > size:
                ok = False
                break
            for y in range(0, size - h + 1):
                row = used[y:y + h]
                for x in range(0, size - w + 1):
                    if not row[:, x:x + w].any():
                        placed = (x, y)
                        break
                if placed:
                    break
            if not placed:
                ok = False
                break
            used[placed[1]:placed[1] + h, placed[0]:placed[0] + w] = True
            out.append(placed)
        if ok:
            return size, out
        size *= 2
    raise RuntimeError('texture too large')


# ---------------------------------------------------------------------------------------------- export helpers
def _write(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if isinstance(data, (dict, list)):
        with open(path, 'w') as fh:
            json.dump(data, fh, indent=1)
    else:
        data.save(path)


def _rot_box(b, facing):
    """Rotate a (x1,y1,z1,x2,y2,z2) box around the block centre for a horizontal facing (north = identity)."""
    x1, y1, z1, x2, y2, z2 = b
    turns = {'north': 0, 'east': 1, 'south': 2, 'west': 3}[facing]
    for _ in range(turns):  # 90 degrees clockwise seen from above: (x, z) -> (16 - z, x)
        x1, z1, x2, z2 = 16 - z2, x1, 16 - z1, x2
    return (x1, y1, z1, x2, y2, z2)


def _clip(b):
    x1, y1, z1, x2, y2, z2 = b
    c = lambda v: max(0.0, min(16.0, v))
    r = (c(x1), c(y1), c(z1), c(x2), c(y2), c(z2))
    if r[3] - r[0] < 0.01 or r[4] - r[1] < 0.01 or r[5] - r[2] < 0.01:
        return None
    return r


def export_furniture(b, preview):
    rects, slots = [], []
    for p in b.parts:
        for f in p.faces:
            rects.append(p.face_px(f))
            slots.append((p, f))
    size, pos = _pack([(w, h) for (w, h) in rects])
    tex = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    elements = []
    for (p, f), (w, h), (x, y) in zip(slots, rects, pos):
        p.uv[f] = (x, y, w, h)
    for n, p in enumerate(b.parts):
        for f in p.faces:
            mat = p.mat or b.mat
            _paint_face(tex, p.uv[f], p, f, mat, b, shash(b.key, n, f))
        for f, fn in p.decals.items():
            if f in p.uv:
                u0, v0, w, h = p.uv[f]
                fn(tex, u0, v0, w, h)
        el = {'from': [round(v, 4) for v in p.frm], 'to': [round(v, 4) for v in p.to], 'faces': {}}
        if not p.shade:
            el['shade'] = False
        if p.rot:
            axis, ang, origin = p.rot
            el['rotation'] = {'angle': ang, 'axis': axis, 'origin': list(origin)}
        k = 16.0 / size
        for f in p.faces:
            u0, v0, w, h = p.uv[f]
            face = {'uv': [round(u0 * k, 4), round(v0 * k, 4), round((u0 + w) * k, 4), round((v0 + h) * k, 4)], 'texture': '#t'}
            el['faces'][f] = face
        elements.append(el)
    tex_id = f'{NS}:block/{b.key}'
    model = {'parent': 'minecraft:block/block', 'textures': {'t': tex_id, 'particle': tex_id}, 'elements': elements}
    if not b.ao:
        model['ambientocclusion'] = False
    _write(os.path.join(ASSETS, 'textures/block', b.key + '.png'), tex)
    _write(os.path.join(ASSETS, 'models/block', b.key + '.json'), model)
    mid = f'{NS}:block/{b.key}'
    if b.directional:
        bs = {'variants': {f'facing={f}': ({'model': mid, 'y': r} if r else {'model': mid})
                           for f, r in (('north', 0), ('east', 90), ('south', 180), ('west', 270))}}
    else:
        bs = {'variants': {'': {'model': mid}}}
    _write(os.path.join(ASSETS, 'blockstates', b.key + '.json'), bs)
    _write(os.path.join(ASSETS, 'items', b.key + '.json'), {'model': {'type': 'minecraft:model', 'model': mid}})
    # collision boxes (north) for Java
    boxes = []
    if b.collision == 'full':
        boxes = [(0, 0, 0, 16, 16, 16)]
    elif b.collision == 'auto':
        for p in b.parts:
            if p.rot or min(p.size()) < 0.01:
                continue
            c = _clip(p.frm + p.to)
            if c:
                boxes.append(c)
    preview['models'][b.key] = {'elements': elements, 'tex': tex, 'size': size}
    return boxes


def export_cube(b, preview):
    frames = b.animated[0] if b.animated else 1
    models = []
    for v in range(b.variants):
        tex_names = {}
        # group faces sharing a material so they share a texture
        groups = {}
        for f in FACES:
            groups.setdefault(id(b.mat_for(f)), []).append(f)
        for gi, (mid_, faces) in enumerate(groups.items()):
            mat = b.mat_for(faces[0])
            name = b.key + (f'_{v}' if b.variants > 1 else '') + ('' if len(groups) == 1 else '_' + faces[0])
            img = Image.new('RGBA', (32, 32 * frames), (0, 0, 0, 0))
            part = Part((0, 0, 0), (16, 16, 16))
            for fr in range(frames):
                sub = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
                _paint_face(sub, (0, 0, 32, 32), part, faces[0], mat, b, shash(b.key, v, faces[0]) + fr * 7919)
                img.paste(sub, (0, 32 * fr))
            _write(os.path.join(ASSETS, 'textures/block', name + '.png'), img)
            if frames > 1:
                _write(os.path.join(ASSETS, 'textures/block', name + '.png.mcmeta'), {'animation': {'frametime': b.animated[1]}})
            for f in faces:
                tex_names[f] = f'{NS}:block/{name}'
        mname = b.key + (f'_{v}' if b.variants > 1 else '')
        model = {'parent': 'minecraft:block/cube', 'textures': {
            'particle': tex_names['north'], 'north': tex_names['north'], 'south': tex_names['south'], 'east': tex_names['east'],
            'west': tex_names['west'], 'up': tex_names['up'], 'down': tex_names['down']}}
        _write(os.path.join(ASSETS, 'models/block', mname + '.json'), model)
        models.append(f'{NS}:block/{mname}')
        if v == 0:
            preview['cubes'][b.key] = {f: os.path.join(ASSETS, 'textures/block', tex_names[f].split('/')[-1] + '.png') for f in FACES}
            preview['cube_textures'][b.key] = tex_names
    bs = {'variants': {'': [{'model': m} for m in models] if len(models) > 1 else {'model': models[0]}}}
    _write(os.path.join(ASSETS, 'blockstates', b.key + '.json'), bs)
    _write(os.path.join(ASSETS, 'items', b.key + '.json'), {'model': {'type': 'minecraft:model', 'model': models[0]}})
    return [(0, 0, 0, 16, 16, 16)]


def export_slab(b, preview):
    tn = preview['cube_textures'][b.of.key]
    m = {'bottom': tn['down'], 'top': tn['up'], 'side': tn['north']}
    _write(os.path.join(ASSETS, 'models/block', b.key + '.json'), {'parent': 'minecraft:block/slab', 'textures': m})
    _write(os.path.join(ASSETS, 'models/block', b.key + '_top.json'), {'parent': 'minecraft:block/slab_top', 'textures': m})
    full = f'{NS}:block/{b.of.key}' + ('_0' if b.of.variants > 1 else '')
    bs = {'variants': {'type=bottom': {'model': f'{NS}:block/{b.key}'}, 'type=top': {'model': f'{NS}:block/{b.key}_top'},
                       'type=double': {'model': full}}}
    _write(os.path.join(ASSETS, 'blockstates', b.key + '.json'), bs)
    _write(os.path.join(ASSETS, 'items', b.key + '.json'), {'model': {'type': 'minecraft:model', 'model': f'{NS}:block/{b.key}'}})
    return None


def export_stairs(b, preview):
    tn = preview['cube_textures'][b.of.key]
    m = {'bottom': tn['down'], 'top': tn['up'], 'side': tn['north']}
    for suf, parent in (('', 'stairs'), ('_inner', 'inner_stairs'), ('_outer', 'outer_stairs')):
        _write(os.path.join(ASSETS, 'models/block', b.key + suf + '.json'), {'parent': f'minecraft:block/{parent}', 'textures': m})
    tpl = json.load(open(os.path.join(HERE, 'templates', 'stairs.json')))
    s = json.dumps(tpl).replace('minecraft:block/oak_stairs', f'{NS}:block/{b.key}')
    _write(os.path.join(ASSETS, 'blockstates', b.key + '.json'), json.loads(s))
    _write(os.path.join(ASSETS, 'items', b.key + '.json'), {'model': {'type': 'minecraft:model', 'model': f'{NS}:block/{b.key}'}})
    return None


def _paint_flat(b, w, h, face, seed):
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    part = Part((0, 0, 0), (16, 16, 16))
    geo = face if face in NORMALS else 'north'
    _paint_face(img, (0, 0, w, h), part, geo, b.mat, b, seed, label=face)
    return img


def export_door(b, preview):
    bottom = _paint_flat(b, 32, 32, 'bottom', 11)
    top = _paint_flat(b, 32, 32, 'top', 12)
    _write(os.path.join(ASSETS, 'textures/block', b.key + '_bottom.png'), bottom)
    _write(os.path.join(ASSETS, 'textures/block', b.key + '_top.png'), top)
    tex = {'bottom': f'{NS}:block/{b.key}_bottom', 'top': f'{NS}:block/{b.key}_top'}
    for half in ('bottom', 'top'):
        for hinge in ('left', 'right'):
            for op in ('', '_open'):
                name = f'{b.key}_{half}_{hinge}{op}'
                _write(os.path.join(ASSETS, 'models/block', name + '.json'),
                       {'parent': f'minecraft:block/door_{half}_{hinge}{op}', 'textures': tex})
    tpl = json.load(open(os.path.join(HERE, 'templates', 'door.json')))
    s = json.dumps(tpl).replace('minecraft:block/oak_door', f'{NS}:block/{b.key}')
    _write(os.path.join(ASSETS, 'blockstates', b.key + '.json'), json.loads(s))
    # item: the flat door icon (top above bottom)
    icon = Image.new('RGBA', (32, 64))
    icon.paste(top, (0, 0))
    icon.paste(bottom, (0, 32))
    icon = icon.resize((16, 32), Image.NEAREST)
    item = Image.new('RGBA', (32, 32))
    item.paste(icon, (8, 0))
    _write(os.path.join(ASSETS, 'textures/item', b.key + '.png'), item)
    _write(os.path.join(ASSETS, 'models/item', b.key + '.json'), {'parent': 'minecraft:item/generated', 'textures': {'layer0': f'{NS}:item/{b.key}'}})
    _write(os.path.join(ASSETS, 'items', b.key + '.json'), {'model': {'type': 'minecraft:model', 'model': f'{NS}:item/{b.key}'}})
    preview['doors'][b.key] = {'bottom': bottom, 'top': top}
    return None


def export_trapdoor(b, preview):
    img = _paint_flat(b, 32, 32, 'up', 13)
    _write(os.path.join(ASSETS, 'textures/block', b.key + '.png'), img)
    tex = {'texture': f'{NS}:block/{b.key}'}
    for part in ('bottom', 'top', 'open'):
        _write(os.path.join(ASSETS, 'models/block', f'{b.key}_{part}.json'),
               {'parent': f'minecraft:block/template_orientable_trapdoor_{part}', 'textures': tex})
    tpl = json.load(open(os.path.join(HERE, 'templates', 'trapdoor.json')))
    s = json.dumps(tpl).replace('minecraft:block/oak_trapdoor', f'{NS}:block/{b.key}')
    _write(os.path.join(ASSETS, 'blockstates', b.key + '.json'), json.loads(s))
    _write(os.path.join(ASSETS, 'items', b.key + '.json'), {'model': {'type': 'minecraft:model', 'model': f'{NS}:block/{b.key}_bottom'}})
    return None


EXPORTERS = {'furniture': export_furniture, 'cube': export_cube, 'slab': export_slab, 'stairs': export_stairs,
             'door': export_door, 'trapdoor': export_trapdoor}
