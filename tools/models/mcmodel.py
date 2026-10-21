"""Single-source entity model definitions for DEAD LINE.

A model is a tree of bones (ModelPart) holding box cubes in Minecraft model space
(+Y is down, ground at y=24, the model faces -Z). From one definition we emit:
  * the Java `createBodyLayer()` (generated *ModelBase class),
  * a texture painted in 3D (every texel knows its model-space position/normal),
  * a JSON description used by the three.js preview.
"""
import json
import math
import numpy as np
from PIL import Image


class Cube:
    def __init__(self, origin, size, mat=None, inflate=0.0, name=None, uv=None, mirror=False, decals=None):
        self.origin = tuple(float(v) for v in origin)
        self.size = tuple(int(v) for v in size)
        self.mat = mat
        self.inflate = inflate
        self.name = name
        self.uv = uv
        self.mirror = mirror
        self.decals = decals or {}  # face -> fn(img, u0, v0, w, h)

    def uv_size(self):
        w, h, d = self.size
        return 2 * (d + w), d + h


class Bone:
    def __init__(self, name, pivot=(0, 0, 0), rot=(0, 0, 0), cubes=(), children=(), mat=None):
        self.name = name
        self.pivot = tuple(float(v) for v in pivot)
        self.rot = tuple(float(v) for v in rot)  # degrees
        self.cubes = list(cubes)
        self.children = list(children)
        self.mat = mat
        self.parent = None
        for c in self.children:
            c.parent = self

    def add(self, *bones):
        for b in bones:
            b.parent = self
            self.children.append(b)
        return self

    def walk(self):
        yield self
        for c in self.children:
            yield from c.walk()


def rot_matrix(rx, ry, rz):
    """Minecraft ModelPart rotation: rotationZYX(z, y, x) -> Rz*Ry*Rx (radians)."""
    cx, sx = math.cos(rx), math.sin(rx)
    cy, sy = math.cos(ry), math.sin(ry)
    cz, sz = math.cos(rz), math.sin(rz)
    Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return Rz @ Ry @ Rx


class Model:
    def __init__(self, name, tex_w, tex_h, root_bones, java_class=None):
        self.name = name
        self.tex_w, self.tex_h = tex_w, tex_h
        self.roots = root_bones
        self.java_class = java_class or ''.join(p.capitalize() for p in name.split('_')) + 'ModelBase'

    def bones(self):
        for r in self.roots:
            yield from r.walk()

    # ---------------- UV packing ----------------
    def pack(self, pad=0):
        items = []
        for b in self.bones():
            for c in b.cubes:
                if c.uv is None:
                    items.append(c)
        items.sort(key=lambda c: (-c.uv_size()[1], -c.uv_size()[0]))
        used = np.zeros((self.tex_h, self.tex_w), bool)
        for b in self.bones():
            for c in b.cubes:
                if c.uv is not None:
                    w, h = c.uv_size()
                    used[c.uv[1]:c.uv[1] + h, c.uv[0]:c.uv[0] + w] = True
        for c in items:
            w, h = c.uv_size()
            w2, h2 = w + pad, h + pad
            placed = False
            for y in range(0, self.tex_h - h + 1):
                for x in range(0, self.tex_w - w + 1):
                    if not used[y:y + h2, x:x + w2].any():
                        used[y:y + h2, x:x + w2] = True
                        c.uv = (x, y)
                        placed = True
                        break
                if placed:
                    break
            if not placed:
                raise RuntimeError(f'{self.name}: no room for cube {c.size} (texture {self.tex_w}x{self.tex_h})')
        return self

    # ---------------- transforms ----------------
    def world_matrix(self, bone):
        chain = []
        b = bone
        while b is not None:
            chain.append(b)
            b = b.parent
        M = np.eye(4)
        for b in reversed(chain):
            T = np.eye(4)
            T[:3, 3] = b.pivot
            R = np.eye(4)
            R[:3, :3] = rot_matrix(*[math.radians(a) for a in b.rot])
            M = M @ T @ R
        return M

    # ---------------- texture painting ----------------
    def paint(self, default_mat, seed=1, layer='base'):
        """Paint every face texel through its material: mat(ctx) -> rgba.

        layer='base' paints materials + plain decals; any other layer name paints only
        decals keyed '<layer>:<face>' on a transparent canvas (e.g. emissive eyes)."""
        img = np.zeros((self.tex_h, self.tex_w, 4), np.uint8)
        rng = np.random.default_rng(seed)
        if layer == 'base':
            for b in self.bones():
                M = self.world_matrix(b)
                for c in b.cubes:
                    mat = c.mat or b.mat or default_mat
                    self._paint_cube(img, M, c, mat, b, rng)
        out = Image.fromarray(img, 'RGBA').copy()
        for b in self.bones():
            for c in b.cubes:
                for key, fn in c.decals.items():
                    lay, _, face = key.rpartition(':')
                    if (lay or 'base') != layer:
                        continue
                    u0, v0, w, h = self.face_rect(c, face)
                    fn(out, u0, v0, w, h)
        return out

    def layers(self):
        names = set()
        for b in self.bones():
            for c in b.cubes:
                for key in c.decals:
                    lay, _, _ = key.rpartition(':')
                    if lay:
                        names.add(lay)
        return sorted(names)

    def face_rect(self, c, face):
        u, v = c.uv
        w, h, d = c.size
        return {
            'top': (u + d, v, w, d), 'bottom': (u + d + w, v, w, d),
            'west': (u, v + d, d, h), 'front': (u + d, v + d, w, h),
            'east': (u + d + w, v + d, d, h), 'back': (u + 2 * d + w, v + d, w, h),
        }[face]

    def _paint_cube(self, img, M, c, mat, bone, rng):
        x0, y0, z0 = c.origin
        w, h, d = c.size
        x1, y1, z1 = x0 + w, y0 + h, z0 + d
        R = M[:3, :3]

        def P(p):
            return (M @ np.array([p[0], p[1], p[2], 1.0]))[:3]

        # face -> (rect, fn(s,t)->local point, normal)
        faces = {
            'front': (lambda s, t: (x0 + s * w, y0 + t * h, z0), (0, 0, -1)),
            'back': (lambda s, t: (x1 - s * w, y0 + t * h, z1), (0, 0, 1)),
            'west': (lambda s, t: (x0, y0 + t * h, z1 - s * d), (-1, 0, 0)),
            'east': (lambda s, t: (x1, y0 + t * h, z0 + s * d), (1, 0, 0)),
            'top': (lambda s, t: (x0 + s * w, y0, z1 - t * d), (0, -1, 0)),
            'bottom': (lambda s, t: (x0 + s * w, y1, z1 - t * d), (0, 1, 0)),
        }
        for face, (fn, n) in faces.items():
            u0, v0, fw, fh = self.face_rect(c, face)
            if fw <= 0 or fh <= 0:
                continue
            nw = R @ np.array(n, float)
            for j in range(fh):
                for i in range(fw):
                    s, t = (i + 0.5) / fw, (j + 0.5) / fh
                    pos = P(fn(s, t))
                    ctx = Ctx(pos, nw, face, s, t, i, j, fw, fh, c, bone, rng)
                    col = mat(ctx)
                    if col is not None:
                        img[v0 + j, u0 + i] = col

    # ---------------- exports ----------------
    def to_json(self):
        bones = []
        for b in self.bones():
            bones.append({
                'name': b.name, 'parent': b.parent.name if b.parent else None,
                'pivot': b.pivot, 'rot': b.rot,
                'cubes': [{'origin': c.origin, 'size': c.size, 'uv': c.uv, 'inflate': c.inflate, 'mirror': c.mirror} for c in b.cubes],
            })
        return {'name': self.name, 'texW': self.tex_w, 'texH': self.tex_h, 'scale': self.scale, 'bones': bones}

    def to_java(self, package):
        def f(v):
            s = ('%.4f' % v).rstrip('0').rstrip('.')
            if s in ('-0', ''):
                s = '0'
            return s + 'F'

        lines = []
        fields = []
        lookups = []
        scaled = abs(self.scale - 1.0) > 1e-6
        top_var = 'root'
        if scaled:
            # Whole model authored at higher texel density, shrunk around the ground point (y=24).
            lines.append('\t\tPartDefinition pScaleRoot = root.addOrReplaceChild("scale_root", CubeListBuilder.create(), PartPose.offset(0F, 24F, 0F).withScale(%s));' % f(self.scale))
            top_var = 'pScaleRoot'
        for b in self.bones():
            var = 'p' + _camel(b.name)[0].upper() + _camel(b.name)[1:]
            parent_var = top_var if b.parent is None else 'p' + _camel(b.parent.name)[0].upper() + _camel(b.parent.name)[1:]
            cl = 'CubeListBuilder.create()'
            for c in b.cubes:
                cl += '.texOffs(%d, %d)' % c.uv
                if c.mirror:
                    cl += '.mirror()'
                cl += '.addBox(%s, %s, %s, %s, %s, %s, new CubeDeformation(%s))' % (
                    f(c.origin[0]), f(c.origin[1]), f(c.origin[2]),
                    f(c.size[0]), f(c.size[1]), f(c.size[2]), f(c.inflate))
                if c.mirror:
                    cl += '.mirror(false)'
            rx, ry, rz = [math.radians(a) for a in b.rot]
            py = b.pivot[1] - 24.0 if (scaled and b.parent is None) else b.pivot[1]
            pose = 'PartPose.offsetAndRotation(%s, %s, %s, %s, %s, %s)' % (
                f(b.pivot[0]), f(py), f(b.pivot[2]), f(rx), f(ry), f(rz))
            lines.append('\t\tPartDefinition %s = %s.addOrReplaceChild("%s", %s, %s);' % (var, parent_var, b.name, cl, pose))
            fields.append('\tprotected final ModelPart %s;' % _camel(b.name))
            if b.parent is None:
                lookups.append('\t\tthis.%s = %s.getChild("%s");' % (_camel(b.name), 'root.getChild("scale_root")' if scaled else 'root', b.name))
            else:
                lookups.append('\t\tthis.%s = this.%s.getChild("%s");' % (_camel(b.name), _camel(b.parent.name), b.name))
            if self.haunt:
                lookups.append('\t\tthis.part("%s", this.%s);' % (b.name, _camel(b.name)))
        state = self.render_state
        cls = self.java_class
        return f'''// GENERATED by tools/models -- do not edit by hand.
package {package};

import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.CubeDeformation;
import net.minecraft.client.model.geom.builders.CubeListBuilder;
import net.minecraft.client.model.geom.builders.LayerDefinition;
import net.minecraft.client.model.geom.builders.MeshDefinition;
import net.minecraft.client.model.geom.builders.PartDefinition;
import net.minecraft.client.renderer.rendertype.RenderTypes;
{self.state_import}

public abstract class {cls} extends {self.base_class() if self.haunt else 'EntityModel<' + state + '>'} {{
	public static final int TEXTURE_WIDTH = {self.tex_w};
	public static final int TEXTURE_HEIGHT = {self.tex_h};
{chr(10).join(fields)}
{self.pose_tables()}

	protected {cls}(ModelPart root) {{
		super(root, RenderTypes::{self.render_type});
{chr(10).join(lookups)}
	}}

	@SuppressWarnings("unused")
	public static LayerDefinition createBodyLayer() {{
		MeshDefinition mesh = new MeshDefinition();
		PartDefinition root = mesh.getRoot();
{chr(10).join(lines)}
		return LayerDefinition.create(mesh, TEXTURE_WIDTH, TEXTURE_HEIGHT);
	}}
}}
'''

    def base_class(self):
        return 'HauntModel'

    def pose_tables(self):
        """Static pose tables (bone -> {xRot, yRot, zRot, dx, dy, dz}) exported from the module's POSES."""
        if not self.poses:
            return ''
        out = []
        for name, table in self.poses.items():
            entries = ', '.join('"%s", new float[] {%s}' % (bone, ', '.join(('%.4fF' % float(v)) for v in (list(vals) + [0] * 6)[:6]))
                                for bone, vals in table.items() if any(b.name == bone for b in self.bones()))
            out.append('\tpublic static final java.util.Map<String, float[]> POSE_%s = HauntModel.table(%s);' % (name.upper(), entries))
        names = [n for n in self.poses]
        out.append('\tpublic static final java.util.Map<String, java.util.Map<String, float[]>> POSES = java.util.Map.ofEntries(%s);'
                   % ', '.join('java.util.Map.entry("%s", POSE_%s)' % (n, n.upper()) for n in names))  # Map.of stops at 10
        out.append('')
        out.append('\t@Override')
        out.append('\tprotected java.util.Map<String, java.util.Map<String, float[]>> poses() {')
        out.append('\t\treturn POSES;')
        out.append('\t}')
        return '\n'.join(out) + '\n'

    haunt = False
    poses = None
    scale = 1.0
    render_state = 'LivingEntityRenderState'
    state_import = 'import net.minecraft.client.renderer.entity.state.LivingEntityRenderState;'
    render_type = 'entityCutoutNoCull'


def _camel(name):
    parts = name.split('_')
    return parts[0] + ''.join(p.capitalize() for p in parts[1:])


class Ctx:
    """Everything a material needs to colour one texel."""
    __slots__ = ('pos', 'n', 'face', 's', 't', 'i', 'j', 'w', 'h', 'cube', 'bone', 'rng')

    def __init__(self, pos, n, face, s, t, i, j, w, h, cube, bone, rng):
        self.pos, self.n, self.face, self.s, self.t = pos, n, face, s, t
        self.i, self.j, self.w, self.h = i, j, w, h
        self.cube, self.bone, self.rng = cube, bone, rng

    @property
    def x(self): return self.pos[0]

    @property
    def y(self): return self.pos[1]

    @property
    def z(self): return self.pos[2]

    def edge(self):
        """Distance in texels to the nearest face edge (0 = border texel)."""
        return min(self.i, self.j, self.w - 1 - self.i, self.h - 1 - self.j)


# ---------------------------------------------------------------- noise helpers
def hash3(x, y, z, seed=0):
    h = (int(math.floor(x)) * 374761393 + int(math.floor(y)) * 668265263 + int(math.floor(z)) * 2147483647 + seed * 1442695041) & 0xffffffff
    h = ((h ^ (h >> 13)) * 1274126177) & 0xffffffff
    return ((h ^ (h >> 16)) & 0xffff) / 65535.0


def vnoise(x, y, z, seed=0):
    xi, yi, zi = math.floor(x), math.floor(y), math.floor(z)
    xf, yf, zf = x - xi, y - yi, z - zi
    u, v, w = [t * t * (3 - 2 * t) for t in (xf, yf, zf)]

    def g(a, b, c):
        return hash3(xi + a, yi + b, zi + c, seed)
    x00 = g(0, 0, 0) * (1 - u) + g(1, 0, 0) * u
    x10 = g(0, 1, 0) * (1 - u) + g(1, 1, 0) * u
    x01 = g(0, 0, 1) * (1 - u) + g(1, 0, 1) * u
    x11 = g(0, 1, 1) * (1 - u) + g(1, 1, 1) * u
    y0 = x00 * (1 - v) + x10 * v
    y1 = x01 * (1 - v) + x11 * v
    return y0 * (1 - w) + y1 * w


def fbm(x, y, z, octaves=3, seed=0):
    a, f, s, t = 0.5, 1.0, 0.0, 0.0
    for o in range(octaves):
        s += a * vnoise(x * f, y * f, z * f, seed + o * 17)
        t += a
        a *= 0.5
        f *= 2.0
    return s / t


def pick(ramp, v):
    v = max(0.0, min(0.999, v))
    return ramp[int(v * len(ramp))]


def face_light(ctx):
    """Baked directional light: tops bright, bottoms dark (vanilla-like)."""
    ny = ctx.n[1]
    if ny < -0.5:
        return 0.16
    if ny > 0.5:
        return -0.22
    nx, nz = ctx.n[0], ctx.n[2]
    return -0.04 * nx - 0.02 * nz
