"""Preview renders for the building kit (three.js in headless Chromium).

    python3 tools/blocks/brender.py showroom casa          -> scratchpad/blocks/showroom_casa.png (every block of a kit)
    python3 tools/blocks/brender.py scene scenes/cocina.py -> scratchpad/blocks/scene_cocina.png (day + night with flashlight)

A scene file defines SCENE = dict(blocks=[(x, y, z, key, facing), ...], camera=(x, y, z), target=(x, y, z), fill=...)
`fill` helpers: see room() below. Block keys must exist in tools/blocks/out/preview.json (run build_blocks.py first).
"""
import base64
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'models'))
import render  # noqa: E402  (shared scratchpad paths + shot.mjs)

from PIL import Image, ImageDraw  # noqa: E402

SP = render.SP
OUTDIR = os.path.join(SP, 'blocks')
THREE = render.THREE
SHOT = render.SHOT

PAGE = r'''<!doctype html><html><body style="margin:0;background:#000">
<canvas id=c></canvas>
<script src="file://%(three)s"></script>
<script src="file://%(viewer)s"></script>
<script>
const SPEC = %(spec)s;
const renderer = new THREE.WebGLRenderer({canvas: document.getElementById('c'), antialias: false, preserveDrawingBuffer: true});
renderer.setSize(SPEC.w, SPEC.h);
renderer.setScissorTest(true);
const texCache = {};
function tex(uri) { return texCache[uri]; }
function preload(done) {
  const uris = new Set();
  for (const m of Object.values(SPEC.models)) { if (m.cube) Object.values(m.cube).forEach(u => uris.add(u)); else uris.add(m.tex); }
  let left = uris.size;
  if (!left) { done(); return; }
  for (const u of uris) {
    const img = new Image();
    img.onload = () => {
      const t = new THREE.Texture(img); t.needsUpdate = true; t.magFilter = THREE.NearestFilter; t.minFilter = THREE.NearestFilter;
      t.generateMipmaps = false; if (THREE.SRGBColorSpace) t.colorSpace = THREE.SRGBColorSpace; texCache[u] = t;
      if (--left === 0) done();
    };
    img.onerror = () => { if (--left === 0) done(); };
    img.src = u;
  }
}
function buildBlock(key) {
  const m = SPEC.models[key];
  if (m.cube) {
    const g = new THREE.Group();
    for (const f of ['north', 'south', 'west', 'east', 'up', 'down']) {
      const faces = {}; faces[f] = { uv: [0, 0, 16, 16] };
      g.add(BlockView.buildElements(THREE, [{ from: [0, 0, 0], to: [16, 16, 16], faces }], tex(m.cube[f]), { translucent: m.translucent }));
    }
    return g;
  }
  return BlockView.buildElements(THREE, m.elements, tex(m.tex), { translucent: m.translucent, emissive: m.light ? 0.25 : 0 });
}
function makeScene(cell) {
  const scene = new THREE.Scene();
  const night = cell.night;
  scene.background = new THREE.Color(night ? 0x040306 : 0x8a8f9c);
  if (night) {
    scene.fog = new THREE.Fog(0x040306, 4, 22);
    scene.add(new THREE.AmbientLight(0x6a6a8a, 0.18));
  } else {
    scene.add(new THREE.AmbientLight(0xffffff, 0.95));
    const sun = new THREE.DirectionalLight(0xfff4e0, 0.7); sun.position.set(-3, 8, -5); scene.add(sun);
  }
  for (const [x, y, z, key, facing] of cell.blocks) {
    if (!SPEC.models[key]) continue;
    scene.add(BlockView.place(THREE, buildBlock(key), x, y, z, facing));
    const m = SPEC.models[key];
    if (m.light && cell.lights !== false) {
      const l = new THREE.PointLight(0xffc98a, night ? 1.6 : 0.6, m.light * 0.9, 1.6); l.position.set(x + 0.5, y + 0.6, z + 0.5); scene.add(l);
    }
  }
  const cam = new THREE.PerspectiveCamera(cell.fov || 60, cell.w / cell.h, 0.05, 200);
  cam.position.set(...cell.camera);
  cam.lookAt(...cell.target);
  if (night && cell.flashlight !== false) {
    const spot = new THREE.SpotLight(0xfff2d8, 3.2, 26, Math.PI / 7, 0.45, 1.2);
    spot.position.set(...cell.camera); spot.target.position.set(...cell.target); scene.add(spot); scene.add(spot.target);
  }
  return { scene, cam };
}
preload(() => {
  for (const cell of SPEC.cells) {
    const { scene, cam } = makeScene(cell);
    renderer.setViewport(cell.x, SPEC.h - cell.y - cell.h, cell.w, cell.h); renderer.setScissor(cell.x, SPEC.h - cell.y - cell.h, cell.w, cell.h);
    renderer.render(scene, cam);
  }
  window.__done = true;
});
</script></body></html>'''


def _uri(path):
    with open(path, 'rb') as fh:
        return 'data:image/png;base64,' + base64.b64encode(fh.read()).decode()


def load_models(keys=None):
    """Merge every out/preview_*.json (each kit build writes its own) and turn textures into data URIs."""
    import glob
    data = {'models': {}, 'cubes': {}, 'kits': {}}
    for p in sorted(glob.glob(os.path.join(HERE, 'out', 'preview_*.json')), key=os.path.getmtime):
        d = json.load(open(p))
        data['models'].update(d['models'])
        data['cubes'].update(d['cubes'])
        data['kits'].update(d['kits'])
    kinds = {b['key']: b for kit in data['kits'].values() for b in kit}
    models = {}
    for k, m in data['models'].items():
        if keys and k not in keys:
            continue
        info = kinds.get(k, {})
        models[k] = {'elements': m['elements'], 'tex': _uri(m['texture']), 'light': info.get('light', 0),
                     'translucent': info.get('render') == 'translucent'}
    for k, faces in data['cubes'].items():
        if keys and k not in keys:
            continue
        info = kinds.get(k, {})
        models[k] = {'cube': {f: _uri(p) for f, p in faces.items()}, 'light': info.get('light', 0),
                     'translucent': info.get('render') == 'translucent'}
    return data, models


def _run(spec, out):
    html = PAGE % {'three': THREE, 'viewer': os.path.join(HERE, 'bview.js'), 'spec': json.dumps(spec)}
    os.makedirs(OUTDIR, exist_ok=True)
    fd, path = tempfile.mkstemp(suffix='.html', dir=os.path.join(SP, 'render'))
    with os.fdopen(fd, 'w') as fh:
        fh.write(html)
    try:
        r = subprocess.run(['node', SHOT, path, out, str(spec['w']), str(spec['h'])], capture_output=True, text=True, timeout=180)
        if r.returncode:
            print('render problem', r.stdout[-1500:], r.stderr[-1500:])
    finally:
        os.unlink(path)


def showroom(kit, cols=6, cell=260):
    data, models = load_models()
    blocks = [b for b in data['kits'].get(kit, [])]
    rows = (len(blocks) + cols - 1) // cols
    cells = []
    for n, b in enumerate(blocks):
        x, y = (n % cols) * cell, (n // cols) * cell
        cells.append({'x': x, 'y': y, 'w': cell, 'h': cell, 'blocks': [[0, 0, 0, b['key'], 'north']],
                      'camera': [-1.15, 1.35, -1.25], 'target': [0.5, 0.45, 0.5], 'fov': 40, 'lights': True})
    spec = {'w': cols * cell, 'h': rows * cell, 'cells': cells, 'models': {b['key']: models[b['key']] for b in blocks if b['key'] in models}}
    out = os.path.join(OUTDIR, f'showroom_{kit}.png')
    _run(spec, out)
    img = Image.open(out).convert('RGB')
    d = ImageDraw.Draw(img)
    for n, b in enumerate(blocks):
        x, y = (n % cols) * cell, (n // cols) * cell
        d.rectangle([x, y + cell - 16, x + cell, y + cell], fill=(0, 0, 0))
        d.text((x + 4, y + cell - 14), b['key'], fill=(230, 230, 230))
    img.save(out)
    return out


def scene(path, w=960, h=540):
    ns = {}
    exec(open(path).read(), ns)
    S = ns['SCENE']
    data, models = load_models()
    used = {b[3] for b in S['blocks']}
    cells = []
    for i, night in enumerate((False, True)):
        cells.append({'x': i * w, 'y': 0, 'w': w, 'h': h, 'night': night, 'blocks': S['blocks'], 'camera': S['camera'],
                      'target': S['target'], 'fov': S.get('fov', 70)})
    spec = {'w': w * 2, 'h': h, 'cells': cells, 'models': {k: models[k] for k in used if k in models}}
    missing = [k for k in used if k not in models]
    if missing:
        print('missing blocks in scene:', missing)
    out = os.path.join(OUTDIR, 'scene_' + os.path.basename(path).replace('.py', '') + '.png')
    _run(spec, out)
    return out


if __name__ == '__main__':
    if sys.argv[1] == 'showroom':
        print(showroom(sys.argv[2]))
    else:
        print(scene(sys.argv[2]))
