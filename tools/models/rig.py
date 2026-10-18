"""Authoring helper: define bones with ABSOLUTE pivots and ABSOLUTE cube boxes."""
from mcmodel import Bone, Cube


class Rig:
    def __init__(self):
        self.bones = {}
        self.abs_pivot = {}
        self.roots = []

    def bone(self, name, pivot, parent=None, rot=(0, 0, 0), mat=None):
        pa = self.abs_pivot[parent] if parent else (0.0, 0.0, 0.0)
        rel = tuple(pivot[i] - pa[i] for i in range(3))
        b = Bone(name, rel, rot, mat=mat)
        self.bones[name] = b
        self.abs_pivot[name] = tuple(float(v) for v in pivot)
        if parent:
            self.bones[parent].add(b)
        else:
            self.roots.append(b)
        return b

    def box(self, bone, frm, size, mat=None, inflate=0.0, decals=None, mirror=False):
        """frm: absolute min corner (x, y, z); size: (w, h, d) integers."""
        p = self.abs_pivot[bone]
        origin = (frm[0] - p[0], frm[1] - p[1], frm[2] - p[2])
        c = Cube(origin, size, mat=mat, inflate=inflate, decals=decals, mirror=mirror)
        self.bones[bone].cubes.append(c)
        return c
