# -*- coding: utf-8 -*-
"""Generates the DEAD LINE preview page (single self-contained HTML)."""
import base64, json, os, sys, html
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
from gallery_data import ENTITIES, ITEMS, STATUS

TEX = os.path.join(ROOT, 'src/main/resources/assets/deadline/textures')


def uri(path):
    return 'data:image/png;base64,' + base64.b64encode(open(path, 'rb').read()).decode()


def first_frame(path):
    from PIL import Image
    import io
    im = Image.open(path)
    if im.height > im.width:
        im = im.crop((0, 0, im.width, im.width))
    b = io.BytesIO(); im.save(b, 'PNG')
    return 'data:image/png;base64,' + base64.b64encode(b.getvalue()).decode()


def build(out):
    models = {}
    for key, *_ in ENTITIES:
        data = json.load(open(os.path.join(HERE, 'models', key + '.json')))
        models[key] = {'data': data, 'tex': uri(os.path.join(TEX, 'entity', key + '.png'))}
    emf = [uri(os.path.join(TEX, 'item', f'emf_{i}.png')) for i in range(6)]
    ents = [dict(key=k, name=n, place=p, quote=q, traits=t, weak=w) for k, n, p, q, t, w in ENTITIES]
    item_cards = []
    for key, name, desc in ITEMS:
        src = first_frame(os.path.join(TEX, 'item', key + '.png'))
        extra = ' data-emf="1"' if key.startswith('emf') else ''
        item_cards.append(f'<li class="item"><img src="{src}" alt="" width="64" height="64"{extra}>'
                          f'<div><h3>{html.escape(name)}</h3><p>{html.escape(desc)}</p></div></li>')
    status = ''.join(f'<li class="st st-{s}"><span class="dot"></span>{html.escape(t)}</li>' for s, t in STATUS)
    viewer = open(os.path.join(HERE, 'mcviewer.js')).read()
    page = TEMPLATE.replace('%%ITEMS%%', '\n'.join(item_cards)).replace('%%STATUS%%', status) \
        .replace('%%MODELS%%', json.dumps(models)).replace('%%ENTS%%', json.dumps(ents, ensure_ascii=False)) \
        .replace('%%EMF%%', json.dumps(emf)).replace('%%VIEWER%%', viewer)
    open(out, 'w').write(page)
    print('wrote', out, len(page) // 1024, 'KB')


TEMPLATE = r'''<title>Archivo DEAD LINE</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Special+Elite&family=Spectral:ital,wght@0,400;0,600;1,400&family=VT323&display=swap">
<style>
/* Layout: an investigator's case file read on a VHS monitor; entity viewer first, tools as an evidence grid. */
:root {
  color-scheme: dark;
  --bg: #0c0a0e;
  --panel: #151219;
  --line: #2a2430;
  --fg: #e7e0d4;
  --muted: #958c99;
  --blood: #c7252f;
  --spirit: #63dcc6;
  --font-display: "Special Elite", "Courier New", monospace;
  --font-body: "Spectral", Georgia, serif;
  --font-data: "VT323", "Courier New", monospace;
}
html, body { background: var(--bg); color: var(--fg); }
body { font-family: var(--font-body); font-size: 1.02rem; line-height: 1.55;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); padding-block: 28px 64px; }
.wrap { max-width: 1160px; margin: 0 auto; display: grid; gap: 56px; }
header { display: grid; gap: 10px; }
.rec { font-family: var(--font-data); font-size: 1.35rem; color: var(--muted); letter-spacing: .06em; display: flex; gap: 18px; flex-wrap: wrap; }
.rec b { color: var(--blood); font-weight: normal; }
.rec b::before { content: ""; display: inline-block; width: .6em; height: .6em; border-radius: 50%; background: var(--blood); margin-right: .4em; animation: blink 1.2s steps(1) infinite; }
@keyframes blink { 50% { opacity: 0; } }
h1 { font-family: var(--font-display); font-weight: normal; font-size: clamp(2.6rem, 8vw, 5.4rem); line-height: .95; margin: 0; letter-spacing: .02em; text-wrap: balance; }
h1 span { color: var(--blood); }
.lede { max-width: 62ch; color: var(--muted); margin: 0; }
h2 { font-family: var(--font-display); font-weight: normal; font-size: 1.7rem; margin: 0 0 18px; letter-spacing: .03em; }
h2 small { font-family: var(--font-data); font-size: 1.15rem; color: var(--muted); margin-left: 10px; letter-spacing: .05em; }
.stage { display: grid; grid-template-columns: 210px minmax(0, 1fr) 300px; gap: 18px; align-items: stretch; }
.roster { list-style: none; margin: 0; padding: 0; display: grid; gap: 4px; align-content: start; }
.roster button { width: 100%; text-align: left; background: transparent; border: 1px solid transparent; color: var(--fg); font-family: var(--font-display); font-size: 1.05rem; padding: 9px 12px; cursor: pointer; display: flex; justify-content: space-between; gap: 8px; }
.roster button span { font-family: var(--font-data); color: var(--muted); font-size: 1rem; }
.roster button:hover { border-color: var(--line); }
.roster button[aria-pressed="true"] { border-color: var(--blood); background: var(--panel); }
.roster button:focus-visible, .ctrl button:focus-visible { outline: 2px solid var(--spirit); outline-offset: 2px; }
.screen { position: relative; background: radial-gradient(ellipse at 50% 40%, #1d1922 0%, var(--bg) 75%); border: 1px solid var(--line); min-height: 480px; overflow: hidden; touch-action: none; cursor: grab; }
.screen canvas { display: block; width: 100%; height: 100%; position: absolute; inset: 0; }
.screen::after { content: ""; position: absolute; inset: 0; pointer-events: none; background: repeating-linear-gradient(0deg, rgba(0,0,0,.18) 0 1px, transparent 1px 3px); }
.osd { position: absolute; left: 14px; top: 10px; z-index: 2; font-family: var(--font-data); font-size: 1.25rem; color: var(--fg); opacity: .85; pointer-events: none; }
.osd.r { left: auto; right: 14px; color: var(--blood); }
.ctrl { position: absolute; left: 12px; bottom: 12px; z-index: 2; display: flex; gap: 8px; flex-wrap: wrap; }
.ctrl button { font-family: var(--font-data); font-size: 1.15rem; background: rgba(12,10,14,.75); color: var(--fg); border: 1px solid var(--line); padding: 2px 10px; cursor: pointer; }
.ctrl button[aria-pressed="true"] { border-color: var(--spirit); color: var(--spirit); }
.dossier { background: var(--panel); border: 1px solid var(--line); padding: 18px 18px 20px; display: grid; gap: 12px; align-content: start; min-width: 0; }
.dossier .place { font-family: var(--font-data); font-size: 1.2rem; color: var(--spirit); letter-spacing: .04em; }
.dossier h3 { font-family: var(--font-display); font-weight: normal; font-size: 1.7rem; margin: 0; line-height: 1.1; }
.dossier blockquote { margin: 0; font-style: italic; border-left: 2px solid var(--blood); padding-left: 12px; }
.dossier ul { margin: 0; padding-left: 18px; display: grid; gap: 4px; color: var(--fg); }
.dossier .weak { font-family: var(--font-data); font-size: 1.15rem; color: var(--muted); border-top: 1px dashed var(--line); padding-top: 10px; }
.dossier .weak b { color: var(--fg); font-weight: normal; }
.items { list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 12px; }
.item { display: grid; grid-template-columns: 64px minmax(0, 1fr); gap: 14px; align-items: center; padding: 12px; border: 1px solid var(--line); background: var(--panel); }
.item img { image-rendering: pixelated; width: 64px; height: 64px; }
.item h3 { margin: 0; font-family: var(--font-display); font-weight: normal; font-size: 1.05rem; }
.item p { margin: 2px 0 0; color: var(--muted); font-size: .92rem; line-height: 1.4; }
.status { list-style: none; margin: 0; padding: 0; display: grid; gap: 6px; font-family: var(--font-data); font-size: 1.3rem; }
.st { display: flex; gap: 10px; align-items: center; }
.st .dot { width: 10px; height: 10px; flex: none; border: 1px solid var(--muted); }
.st-done .dot { background: var(--spirit); border-color: var(--spirit); }
.st-wip .dot { background: var(--blood); border-color: var(--blood); animation: blink 1.2s steps(1) infinite; }
.st-todo { color: var(--muted); }
@media (max-width: 900px) { .stage { grid-template-columns: 1fr; } .roster { grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); } .screen { min-height: 420px; } }
@media (prefers-reduced-motion: reduce) { .rec b::before, .st-wip .dot { animation: none; } }
</style>
<div class="wrap">
  <header>
    <div class="rec"><b>REC</b><span>ARCHIVO DE ENTIDADES</span><span>MC 1.21.11 · FABRIC</span></div>
    <h1>DEAD <span>LINE</span></h1>
    <p class="lede">Sos exorcista. Tu teléfono suena de madrugada y del otro lado alguien pide ayuda. Esto es lo que te espera en cada caso: las entidades, las herramientas para cazarlas y el estado del mod.</p>
  </header>

  <section aria-labelledby="h-ent">
    <h2 id="h-ent">Entidades <small>arrastrá para girar</small></h2>
    <div class="stage">
      <ul class="roster" id="roster"></ul>
      <div class="screen" id="screen">
        <div class="osd" id="osd">PLAY ▸</div><div class="osd r" id="clock">00:00:00</div>
        <div class="ctrl" id="ctrl"></div>
      </div>
      <article class="dossier" id="dossier" aria-live="polite"></article>
    </div>
  </section>

  <section aria-labelledby="h-items">
    <h2 id="h-items">Herramientas y objetos <small>texturas 32×32</small></h2>
    <ul class="items">
%%ITEMS%%
    </ul>
  </section>

  <section aria-labelledby="h-status">
    <h2 id="h-status">Estado del desarrollo</h2>
    <ul class="status">%%STATUS%%</ul>
  </section>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
%%VIEWER%%
</script>
<script>
const MODELS = %%MODELS%%;
const ENTS = %%ENTS%%;
const EMF = %%EMF%%;
// EMF meter cycles through its levels
(() => { const img = document.querySelector('img[data-emf]'); if (!img) return; let i = 0;
  setInterval(() => { i = (i + 1) % 12; img.src = EMF[i < 6 ? i : 11 - i]; }, 260); })();

const S = Math.sin;
const ANIM = {
  llorona: (p, t, alt) => { p('body', 0, 0, 0, 0, -1.5 + S(t * 1.6) * 1.2, 0); p('hair_back', S(t * 1.3) * .06, 0, 0); p('skirt3', S(t * 1.7) * .05, 0, S(t) * .04);
    if (alt) { p('right_arm', -1.45, 0, -.2); p('left_arm', -1.45, 0, .2); p('head', .25, 0, S(t * 9) * .08); } else { p('right_arm', -0.28 + S(t) * .05, 0, -.12); p('left_arm', -0.28 - S(t) * .05, 0, .12); } },
  wendigo: (p, t, alt) => { p('torso', 0.66 + S(t * 1.2) * .03, 0, 0); p('head', 0.31 + (alt ? -.5 : 0), S(t * 3) * (alt ? .25 : .05), 0); p('jaw', alt ? .7 + S(t * 20) * .1 : .14 + S(t * 1.5) * .05, 0, 0); },
  poseida: (p, t, alt) => { if (alt) { p('root', -1.57, 0, 0, 0, -1, 0); p('right_arm', 1.57, 0, -.25); p('left_arm', 1.57, 0, .25); p('right_leg', 1.57, 0, -.25); p('left_leg', 1.57, 0, .25); p('head', 1.2, S(t * 6) * .3, 0); }
    else { p('head', 0, 0, S(t * 0.8) * .35 + (S(t * 13) > .97 ? .4 : 0)); p('right_arm', 0, 0, -.06); p('left_arm', 0, 0, .06); } },
  payaso: (p, t, alt) => { p('balloon_string', S(t * 1.1) * .08, 0, S(t * .9) * .06); p('head', 0, alt ? S(t * 7) * .5 : 0, S(t * .7) * .18); p('body', 0, 0, S(t * .7) * .03); },
  monja: (p, t, alt) => { p('body', 0, 0, 0, 0, -1 + S(t * 1.3) * .8, 0); p('robe3', S(t * 1.5) * .05, 0, 0); if (alt) { p('right_arm', -1.5, 0, -.1); p('left_arm', -1.5, 0, .1); p('head', 0, 0, .35); } },
  sombra: (p, t, alt) => { p('body', 0, 0, S(t * .6) * .02); p('head', 0, alt ? 1.2 : S(t * .5) * .2, 0); },
  muneca: (p, t, alt) => { p('head', 0, 0, alt ? .55 : S(t * .8) * .12); },
  anima: (p, t, alt) => { p('body', 0, 0, 0, 0, -2 + S(t * 1.4) * 1.5, 0); p('tail1', S(t * 2) * .15, 0, 0); p('tail2', S(t * 2 - .7) * .2, 0, 0); p('tail3', S(t * 2 - 1.4) * .25, 0, 0); p('right_arm', -.52 + S(t) * .2, 0, -.35); p('left_arm', -.52 - S(t) * .2, 0, .35); },
};
const ALT_LABEL = { llorona: 'Persecución', wendigo: 'Grito', poseida: 'Caminata araña', payaso: 'Risa', monja: 'Ataque', sombra: 'Te mira', muneca: 'Ladeo', anima: 'Flotar' };

let renderer, scene, camera, current = null, yaw = 0.5, pitch = 0.12, auto = true, alt = false, height = 40;
const screen = document.getElementById('screen');
function initGL() {
  try { renderer = new THREE.WebGLRenderer({ antialias: false, alpha: true }); } catch (e) { screen.querySelector('#osd').textContent = 'SIN WEBGL'; return false; }
  renderer.setPixelRatio(Math.min(2, window.devicePixelRatio || 1));
  screen.prepend(renderer.domElement);
  scene = new THREE.Scene();
  scene.fog = new THREE.Fog(0x0c0a0e, 120, 260);
  scene.add(new THREE.AmbientLight(0xd6cede, 1.05));
  const key = new THREE.DirectionalLight(0xfff1dc, 1.0); key.position.set(-40, 80, 60); scene.add(key);
  const rim = new THREE.DirectionalLight(0xc7252f, 0.55); rim.position.set(50, 20, -60); scene.add(rim);
  const floor = new THREE.Mesh(new THREE.CircleGeometry(26, 40), new THREE.MeshBasicMaterial({ color: 0x15111a }));
  floor.rotation.x = -Math.PI / 2; scene.add(floor);
  camera = new THREE.PerspectiveCamera(30, 1, 1, 600);
  return true;
}
function fit() { if (!renderer) return; const r = screen.getBoundingClientRect(); renderer.setSize(r.width, r.height, false); camera.aspect = r.width / r.height; camera.updateProjectionMatrix(); }
const loader = typeof THREE !== 'undefined' ? new THREE.TextureLoader() : null;
function show(key) {
  document.querySelectorAll('#roster button').forEach(b => b.setAttribute('aria-pressed', b.dataset.key === key));
  const e = ENTS.find(x => x.key === key);
  document.getElementById('dossier').innerHTML = `<div class="place">${e.place.toUpperCase()}</div><h3>${e.name}</h3><blockquote>${e.quote}</blockquote><ul>${e.traits.map(t => `<li>${t}</li>`).join('')}</ul><div class="weak">DEBILIDAD: <b>${e.weak}</b></div>`;
  alt = false; renderCtrl(key);
  if (!renderer) return;
  if (current) scene.remove(current.object);
  const m = MODELS[key];
  loader.load(m.tex, tex => {
    const built = MCViewer.buildModel(THREE, m.data, tex);
    if (current) scene.remove(current.object);
    current = Object.assign(built, { key });
    scene.add(built.object);
    const box = new THREE.Box3().setFromObject(built.object); height = box.max.y - box.min.y;
  });
}
function renderCtrl(key) {
  const c = document.getElementById('ctrl');
  c.innerHTML = `<button type="button" id="b-auto" aria-pressed="${auto}">AUTO-GIRO</button><button type="button" id="b-alt" aria-pressed="${alt}">${ALT_LABEL[key]}</button>`;
  c.querySelector('#b-auto').onclick = () => { auto = !auto; renderCtrl(key); };
  c.querySelector('#b-alt').onclick = () => { alt = !alt; renderCtrl(key); };
}
const roster = document.getElementById('roster');
ENTS.forEach(e => { const li = document.createElement('li'); li.innerHTML = `<button type="button" data-key="${e.key}">${e.name}<span>${MODELS[e.key].data.texW}×${MODELS[e.key].data.texH}</span></button>`; li.firstChild.onclick = () => show(e.key); roster.appendChild(li); });
let drag = null;
screen.addEventListener('pointerdown', ev => { drag = { x: ev.clientX, y: ev.clientY, yaw, pitch }; screen.setPointerCapture(ev.pointerId); auto = false; renderCtrl(current ? current.key : 'llorona'); });
screen.addEventListener('pointermove', ev => { if (!drag) return; yaw = drag.yaw - (ev.clientX - drag.x) * 0.01; pitch = Math.max(-0.3, Math.min(0.9, drag.pitch + (ev.clientY - drag.y) * 0.006)); });
screen.addEventListener('pointerup', () => drag = null);
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
const t0 = performance.now();
function loop(now) {
  const t = (now - t0) / 1000;
  const s = Math.floor(t); document.getElementById('clock').textContent = '00:' + String(Math.floor(s / 60) % 60).padStart(2, '0') + ':' + String(s % 60).padStart(2, '0');
  if (renderer) {
    if (auto && !reduce) yaw += 0.006;
    if (current && ANIM[current.key]) ANIM[current.key](current.pose, reduce ? 0 : t, alt);
    const d = Math.max(90, height * 2.6), cy = height * 0.55;
    camera.position.set(Math.sin(yaw) * Math.cos(pitch) * d, cy + Math.sin(pitch) * d, Math.cos(yaw) * Math.cos(pitch) * d);
    camera.lookAt(0, cy, 0);
    renderer.render(scene, camera);
  }
  requestAnimationFrame(loop);
}
if (typeof THREE !== 'undefined' && initGL()) { fit(); addEventListener('resize', fit); }
show('llorona');
requestAnimationFrame(loop);
</script>
'''

if __name__ == '__main__':
    build(sys.argv[1])
