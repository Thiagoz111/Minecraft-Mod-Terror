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
        snap = os.path.join(HERE, 'tex', key + '.png')
        tex = snap if os.path.exists(snap) else os.path.join(TEX, 'entity', key + '.png')
        models[key] = {'data': data, 'tex': uri(tex)}
        glow = os.path.join(HERE, 'tex', key + '_eyes.png')
        if os.path.exists(glow):
            models[key]['glow'] = uri(glow)
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
const POSE_ES = { attack: 'Ataque', scream: 'Grito', spider: 'Araña', headturn: 'Cabeza girada', float: 'Levitar', laugh: 'Risa', burn: 'Quemándose', reach: 'Te alcanza', creep: 'Acecho', crawl: 'Arrastrarse', chase: 'Persecución', hunt: 'Caza', idle: 'Reposo' };
// generic idle: breathing + slow head drift; a selected pose blends in on top
function animate(cur, t) {
  const fns = cur.glow ? [cur.pose, cur.glow.pose] : [cur.pose];
  const g = cur.groups, P = cur.poseName ? (cur.data.poses || {})[cur.poseName] : null;
  cur.blend += ((P ? 1 : 0) - cur.blend) * 0.08;
  for (const n of Object.keys(g)) fns.forEach(f => f(n, 0, 0, 0, 0, 0, 0));
  const idle = { head: [S(t * .7) * .05, S(t * .45) * .14, S(t * .6) * .05, 0, 0, 0], neck: [S(t * .9) * .03, 0, 0, 0, 0, 0],
    jaw: [Math.max(0, S(t * 1.3)) * .12, 0, 0, 0, 0, 0], body: [S(t * 1.6) * .015, 0, 0, 0, S(t * 1.6) * .4, 0], torso: [S(t * 1.6) * .02, 0, 0, 0, 0, 0] };
  const names = new Set([...Object.keys(idle), ...Object.keys(P || cur.lastP || {})]);
  if (P) cur.lastP = P;
  const L = cur.lastP || {};
  for (const n of names) {
    const a = idle[n] || [0, 0, 0, 0, 0, 0], b = L[n] || null;
    const v = a.map((x, i) => b ? x * (1 - cur.blend) + (b[i] || 0) * cur.blend + (i < 3 ? x * .3 * cur.blend : 0) : x);
    fns.forEach(f => f(n, ...v));
  }
}
let renderer, scene, camera, current = null, yaw = 0.5, pitch = 0.12, auto = true, night = false, height = 40, amb, key, rim, torch;
const screen = document.getElementById('screen');
function initGL() {
  try { renderer = new THREE.WebGLRenderer({ antialias: false, alpha: true }); } catch (e) { screen.querySelector('#osd').textContent = 'SIN WEBGL'; return false; }
  renderer.setPixelRatio(Math.min(2, window.devicePixelRatio || 1));
  screen.prepend(renderer.domElement);
  scene = new THREE.Scene();
  scene.fog = new THREE.Fog(0x0c0a0e, 120, 260);
  amb = new THREE.AmbientLight(0xd6cede, 1.05); scene.add(amb);
  key = new THREE.DirectionalLight(0xfff1dc, 1.0); key.position.set(-40, 80, 60); scene.add(key);
  rim = new THREE.DirectionalLight(0xc7252f, 0.55); rim.position.set(50, 20, -60); scene.add(rim);
  torch = new THREE.PointLight(0xffd29a, 0, 220, 1.4); scene.add(torch);
  const floor = new THREE.Mesh(new THREE.CircleGeometry(26, 40), new THREE.MeshBasicMaterial({ color: 0x15111a }));
  floor.rotation.x = -Math.PI / 2; scene.add(floor);
  camera = new THREE.PerspectiveCamera(30, 1, 1, 600);
  return true;
}
function fit() { if (!renderer) return; const r = screen.getBoundingClientRect(); renderer.setSize(r.width, r.height, false); camera.aspect = r.width / r.height; camera.updateProjectionMatrix(); }
const loader = typeof THREE !== 'undefined' ? new THREE.TextureLoader() : null;
function setNight(on) {
  night = on; if (!amb) return;
  amb.intensity = on ? 0.34 : 1.05; key.intensity = on ? 0.12 : 1.0; rim.intensity = on ? 0.5 : 0.55; torch.intensity = on ? 3.2 : 0;
  scene.fog.color.set(on ? 0x050407 : 0x0c0a0e); scene.fog.near = on ? 60 : 120; scene.fog.far = on ? 190 : 260;
}
function show(key) {
  document.querySelectorAll('#roster button').forEach(b => b.setAttribute('aria-pressed', b.dataset.key === key));
  const e = ENTS.find(x => x.key === key);
  document.getElementById('dossier').innerHTML = `<div class="place">${e.place.toUpperCase()}</div><h3>${e.name}</h3><blockquote>${e.quote}</blockquote><ul>${e.traits.map(t => `<li>${t}</li>`).join('')}</ul><div class="weak">DEBILIDAD: <b>${e.weak}</b></div>`;
  if (!renderer) { renderCtrl(key); return; }
  const m = MODELS[key];
  loader.load(m.tex, tex => {
    const built = MCViewer.buildModel(THREE, m.data, tex);
    let glow = null;
    const finish = () => {
      if (current) { scene.remove(current.object); if (current.glow) scene.remove(current.glow.object); }
      current = Object.assign(built, { key, data: m.data, poseName: null, blend: 0, lastP: null, glow });
      scene.add(built.object);
      if (glow) scene.add(glow.object);
      const box = new THREE.Box3().setFromObject(built.object); height = box.max.y - box.min.y;
      renderCtrl(key);
    };
    if (!m.glow) { finish(); return; }
    loader.load(m.glow, gt => {
      glow = MCViewer.buildModel(THREE, m.data, gt);
      const gm = new THREE.MeshBasicMaterial({ map: gt, transparent: true, alphaTest: 0.04, side: THREE.DoubleSide, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2 });
      glow.object.traverse(o => { if (o.isMesh) o.material = gm; });
      finish();
    });
  });
}
function renderCtrl(key) {
  const c = document.getElementById('ctrl');
  const poses = current && current.key === key ? Object.keys(current.data.poses || {}) : [];
  const cur = current && current.key === key ? current.poseName : null;
  c.innerHTML = `<button type="button" id="b-auto" aria-pressed="${auto}">AUTO-GIRO</button><button type="button" id="b-night" aria-pressed="${night}">NOCHE</button>` +
    `<button type="button" data-pose="" aria-pressed="${!cur}">REPOSO</button>` +
    poses.map(p => `<button type="button" data-pose="${p}" aria-pressed="${cur === p}">${(POSE_ES[p] || p).toUpperCase()}</button>`).join('');
  c.querySelector('#b-auto').onclick = () => { auto = !auto; renderCtrl(key); };
  c.querySelector('#b-night').onclick = () => { setNight(!night); renderCtrl(key); };
  c.querySelectorAll('[data-pose]').forEach(b => b.onclick = () => { if (current) current.poseName = b.dataset.pose || null; renderCtrl(key); });
}
const roster = document.getElementById('roster');
ENTS.forEach(e => { const li = document.createElement('li'); li.innerHTML = `<button type="button" data-key="${e.key}">${e.name}<span>${MODELS[e.key].data.texW}×${MODELS[e.key].data.texH}</span></button>`; li.firstChild.onclick = () => show(e.key); roster.appendChild(li); });
let drag = null;
screen.addEventListener('pointerdown', ev => { if (ev.target.closest('#ctrl')) return; drag = { x: ev.clientX, y: ev.clientY, yaw, pitch }; screen.setPointerCapture(ev.pointerId); auto = false; renderCtrl(current ? current.key : 'llorona'); });
screen.addEventListener('pointermove', ev => { if (!drag) return; yaw = drag.yaw - (ev.clientX - drag.x) * 0.01; pitch = Math.max(-0.3, Math.min(0.9, drag.pitch + (ev.clientY - drag.y) * 0.006)); });
screen.addEventListener('pointerup', () => drag = null);
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
const t0 = performance.now();
function loop(now) {
  const t = (now - t0) / 1000;
  const s = Math.floor(t); document.getElementById('clock').textContent = '00:' + String(Math.floor(s / 60) % 60).padStart(2, '0') + ':' + String(s % 60).padStart(2, '0');
  if (renderer) {
    if (auto && !reduce) yaw += 0.006;
    if (current) animate(current, reduce ? 0 : t);
    const d = Math.max(90, height * 2.6), cy = height * 0.55;
    camera.position.set(Math.sin(yaw) * Math.cos(pitch) * d, cy + Math.sin(pitch) * d, Math.cos(yaw) * Math.cos(pitch) * d);
    camera.lookAt(0, cy, 0);
    if (torch) torch.position.set(camera.position.x * 0.55, cy + 4, camera.position.z * 0.55);
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
