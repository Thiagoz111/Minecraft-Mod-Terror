"""Dev check: can a player walk from the spawn to every story marker of a site?

    python3 tools/sites/walkcheck.py colegio [--from spawn] [--doors open|closed]

Breadth-first search over standing cells. Collision comes from the building kit (ModBlocksGen shapes): a block is
open (no collision), low (top <= 0.6 block: a step or a decal the player walks over), stairs/slab (a step), or solid.
Doors count as open (the script opens them chapter by chapter). Points that cannot be reached are listed with the
nearest reached cell, which usually points straight at the blocked doorway, stair or piece of furniture.
"""
import importlib
import os
import re
import sys
from collections import deque

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
GEN = os.path.join(ROOT, 'src/main/java/com/deadline/registry/gen/ModBlocksGen.java')

STEP = 9.6  # 0.6 block in model units


def free_gap(spans):
    """Widest uncovered stretch of 0..16 left by the given (lo, hi) intervals."""
    best, at = 0.0, 0.0
    for lo, hi in sorted((max(0.0, a), min(16.0, b)) for a, b in spans):
        best = max(best, lo - at)
        at = max(at, hi)
    return max(best, 16.0 - at)


def kit_shapes():
    """block key -> ('open' | 'low' | 'step' | 'solid' | 'door', top height in 1/16)."""
    src = open(GEN).read()
    out = {}
    for m in re.finditer(r'public static final (\w+) [A-Z0-9_]+ = reg\("([a-z0-9_]+)", (.*?)\);\n', src):
        cls, key, rest = m.group(1), m.group(2), m.group(3)
        if 'noCollision()' in rest:
            out[key] = ('open', 0.0)
        elif cls == 'DoorBlock':
            out[key] = ('door', 16.0)
        elif cls == 'TrapDoorBlock':
            out[key] = ('open', 0.0)
        elif cls in ('StairBlock',):
            out[key] = ('step', 16.0)
        elif cls in ('SlabBlock',):
            out[key] = ('step', 8.0)
        else:
            boxes = [[float(v) for v in b.split(',')] for b in re.findall(r'\{([-\d., ]+)\}', rest)]
            if 'new double[][]' in rest and boxes:
                top = max(b[4] for b in boxes)
                if top <= STEP:
                    out[key] = ('low', top)
                elif max(free_gap([(b[0], b[3]) for b in boxes]), free_gap([(b[2], b[5]) for b in boxes])) >= STEP:
                    out[key] = ('open', top)  # a rail or a thin panel at one edge: you walk past it
                else:
                    out[key] = ('solid', top)
            elif 'new double[][] {}' in rest:
                out[key] = ('open', 0.0)
            else:
                out[key] = ('solid', 16.0)
    return out


def classify(state, shapes):
    if state is None:
        return None
    bid = state.split('[')[0]
    if bid in ('minecraft:air', 'minecraft:light'):
        return 'open'
    if bid.startswith('deadline:'):
        kind, top = shapes.get(bid[9:], ('solid', 16.0))
        if kind == 'step' and 'type=top' in state:
            return 'solid'
        if kind == 'step' and 'half=top' in state:
            return 'solid'
        return kind
    return 'solid'


def run(key, start='spawn'):
    mod = importlib.import_module(key)
    site = mod.build()
    sealed = getattr(mod, 'SEALED', ())  # points nobody walks to (mirrored room, behind the brick wall...)
    shapes = kit_shapes()
    blocks = site.blocks
    x0, y0, z0, x1, y1, z1 = site.bounds()

    def kind(x, y, z):
        st = blocks.get((x, y, z))
        if st is None:
            return 'solid' if y < 0 else 'open'  # the flat world: grass at y=-1, dirt below
        return classify(st, shapes)

    def passable(x, y, z):
        return kind(x, y, z) in ('open', 'door')

    def standable(x, y, z):
        k = kind(x, y, z)
        if k in ('open', 'door'):
            below = kind(x, y - 1, z)
            return below in ('solid', 'step', 'low') and passable(x, y + 1, z)
        if k in ('low', 'step'):
            return passable(x, y + 1, z) and (kind(x, y, z) == 'low' or passable(x, y + 2, z) or True)
        return False

    pts = site.markers['points']
    sx, sy, sz = (int(v // 1) for v in pts[start][:3])
    seen = {(sx, sy, sz)}
    q = deque([(sx, sy, sz)])
    while q:
        x, y, z = q.popleft()
        here = kind(x, y, z)
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, nz = x + dx, z + dz
            if not (x0 - 4 <= nx <= x1 + 4 and z0 - 4 <= nz <= z1 + 4):
                continue
            cands = []
            if standable(nx, y, nz):
                cands.append(y)
            elif here in ('step', 'low') or kind(nx, y, nz) in ('step',):
                if standable(nx, y + 1, nz) and passable(x, y + 2, z):
                    cands.append(y + 1)
            if not cands and passable(nx, y, nz) and passable(nx, y + 1, nz):
                for k in range(1, 5):  # drop down
                    if standable(nx, y - k, nz):
                        cands.append(y - k)
                        break
                    if not passable(nx, y - k, nz):
                        break
            for ny in cands:
                c = (nx, ny, nz)
                if c not in seen:
                    seen.add(c)
                    q.append(c)
    bad = []
    for name, (px, py, pz, _) in sorted(pts.items()):
        if name.startswith(tuple(sealed)):
            continue
        bx, by, bz = int(px // 1), int(py // 1), int(pz // 1)
        ok = any((bx + dx, by + dy, bz + dz) in seen for dx in (-1, 0, 1) for dy in (-1, 0, 1) for dz in (-1, 0, 1))
        if not ok:
            near = min(seen, key=lambda c: (c[0] - bx) ** 2 + (c[1] - by) ** 2 * 4 + (c[2] - bz) ** 2)
            bad.append((name, (bx, by, bz), near))
    n = sum(1 for name in pts if not name.startswith(tuple(sealed)))
    print(f'{key}: {len(seen)} standing cells reachable from {start}; {n - len(bad)}/{n} points reachable'
          f' ({len(pts) - n} sealed on purpose)')
    for name, at, near in bad:
        print(f'  UNREACHABLE {name} at {at}; nearest reached {near}')
    return bad


if __name__ == '__main__':
    args = sys.argv[1:] or ['colegio']
    run(args[0], args[2] if len(args) > 2 and args[1] == '--from' else 'spawn')
