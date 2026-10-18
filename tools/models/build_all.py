"""Build every entity model: textures, generated Java bases, preview JSON, review renders."""
import json, os, sys
import ent_llorona, ent_wendigo, ent_poseida, ent_payaso, ent_monja, ent_misc

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
TEX = os.path.join(ROOT, 'src/main/resources/assets/deadline/textures/entity')
JAVA = os.path.join(ROOT, 'src/client/java/com/deadline/client/model/gen')
PREV = os.path.join(ROOT, 'tools/preview/models')
PKG = 'com.deadline.client.model.gen'

MODELS = {
    'llorona': (ent_llorona.build, ent_llorona.dress_mat),
    'wendigo': (ent_wendigo.build, ent_wendigo.hide_mat),
    'poseida': (ent_poseida.build, ent_poseida.gown_mat),
    'payaso': (ent_payaso.build, ent_payaso.suit_mat),
    'monja': (ent_monja.build, ent_monja.habit_mat),
    'sombra': (ent_misc.build_sombra, ent_misc.shadow_mat),
    'muneca': (ent_misc.build_muneca, ent_misc.doll_dress),
    'anima': (ent_misc.build_anima, ent_misc.spirit_mat),
}


def build(names=None):
    os.makedirs(TEX, exist_ok=True); os.makedirs(JAVA, exist_ok=True); os.makedirs(PREV, exist_ok=True)
    out = {}
    for name, (fn, mat) in MODELS.items():
        if names and name not in names:
            continue
        m = fn().pack()
        img = m.paint(mat)
        img.save(os.path.join(TEX, name + '.png'))
        layers = {}
        for lay in m.layers():
            li = m.paint(mat, layer=lay)
            li.save(os.path.join(TEX, f'{name}_{lay}.png'))
            layers[lay] = li
        open(os.path.join(JAVA, m.java_class + '.java'), 'w').write(m.to_java(PKG))
        json.dump(m.to_json(), open(os.path.join(PREV, name + '.json'), 'w'))
        out[name] = (m, img, layers)
    return out


if __name__ == '__main__':
    names = sys.argv[1:] or None
    res = build(names)
    import render
    SP = render.SP
    views = []
    for name, (m, img, _) in res.items():
        views.append(dict(data=m.to_json(), png=img, angles=[20], dist=125, camY=16, lookY=17))
    render.render(views, SP + '/all_models.png', 230 * len(views), 520)
    print('built', list(res))
