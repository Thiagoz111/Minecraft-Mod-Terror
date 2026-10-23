"""Build every entity model: textures, generated Java bases (HauntModel), preview JSON + textures.

    python3 tools/models/build_all.py [key ...]
"""
import importlib
import json
import keyword
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
TEX = os.path.join(ROOT, 'src/main/resources/assets/deadline/textures/entity')
JAVA = os.path.join(ROOT, 'src/client/java/com/deadline/client/model/gen')
PREV = os.path.join(ROOT, 'tools/preview/models')
PREV_TEX = os.path.join(ROOT, 'tools/preview/tex')
PKG = 'com.deadline.client.model.gen'
KEYS = ['monja', 'poseida', 'sombra', 'muneca', 'anima', 'alumna', 'madre', 'clara', 'marta', 'jorge', 'nona', 'toti', 'choripan', 'choripan_demonio']
JAVA_RESERVED = set(keyword.kwlist) | {'default', 'new', 'public', 'private', 'static', 'final', 'class', 'int', 'float', 'root'}


def check(m, key):
    names = [b.name for b in m.bones()]
    dup = {n for n in names if names.count(n) > 1}
    assert not dup, f'{key}: duplicate bone names {dup}'
    from mcmodel import _camel
    bad = [n for n in names if _camel(n) in JAVA_RESERVED]
    assert not bad, f'{key}: bone names clash with Java keywords {bad}'
    cubes = sum(len(b.cubes) for b in m.bones())
    return len(names), cubes


def build_one(key):
    mod = importlib.import_module('ent_' + key)
    m = mod.build().pack()
    m.java_class = ''.join(p.capitalize() for p in key.split('_')) + 'ModelBase'
    bones, cubes = check(m, key)
    mat = getattr(mod, 'DEFAULT_MAT', None)
    img = m.paint(mat)
    os.makedirs(TEX, exist_ok=True)
    os.makedirs(PREV_TEX, exist_ok=True)
    img.save(os.path.join(TEX, key + '.png'))
    img.save(os.path.join(PREV_TEX, key + '.png'))
    layers = m.layers()
    for lay in layers:
        li = m.paint(mat, layer=lay)
        li.save(os.path.join(TEX, f'{key}_{lay}.png'))
        li.save(os.path.join(PREV_TEX, f'{key}_{lay}.png'))
    # extra looks (normal / possessed ...): <key>_<name>.png (+ _<layer>), picked in Java by variant index
    variants = list(getattr(mod, 'VARIANT_MATS', {}).items())
    for vname, vmat in variants[1:]:
        m.paint(vmat).save(os.path.join(TEX, f'{key}_{vname}.png'))
        for lay in layers:
            m.paint(vmat, layer=lay).save(os.path.join(TEX, f'{key}_{vname}_{lay}.png'))
    m.haunt = True
    m.poses = getattr(mod, 'POSES', {}) or {}
    m.render_state = 'HauntRenderState'
    m.state_import = 'import com.deadline.client.render.HauntModel;\nimport com.deadline.client.render.HauntRenderState;'
    os.makedirs(JAVA, exist_ok=True)
    open(os.path.join(JAVA, m.java_class + '.java'), 'w').write(m.to_java(PKG))
    data = m.to_json()
    data['poses'] = m.poses
    data['render_type'] = m.render_type
    json.dump(data, open(os.path.join(PREV, key + '.json'), 'w'))
    top = min(c.origin[1] - c.inflate for b in m.bones() for c in b.cubes) if cubes else 24
    return {'key': key, 'class': m.java_class, 'bones': bones, 'cubes': cubes, 'tex': f'{m.tex_w}x{m.tex_h}',
            'layers': layers, 'variants': [v for v, _ in variants], 'render_type': m.render_type, 'scale': m.scale, 'poses': list(m.poses),
            'bone_names': [b.name for b in m.bones()]}


def build_balloon():
    """Plain (non-haunt) prop model for the clown's balloons."""
    mod = importlib.import_module('ent_balloon')
    m = mod.build().pack()
    m.java_class = 'BalloonModelBase'
    img = m.paint(mod.DEFAULT_MAT)
    img.save(os.path.join(TEX, 'balloon.png'))
    m.render_state = 'EntityRenderState'
    m.state_import = 'import net.minecraft.client.renderer.entity.state.EntityRenderState;'
    open(os.path.join(JAVA, m.java_class + '.java'), 'w').write(m.to_java(PKG))
    return {'key': 'balloon', 'cubes': sum(len(b.cubes) for b in m.bones())}


if __name__ == '__main__':
    keys = sys.argv[1:] or KEYS
    out = [build_balloon() if k == 'balloon' else build_one(k) for k in keys]
    for o in out:
        print(json.dumps({k: v for k, v in o.items() if k != 'bone_names'}))
