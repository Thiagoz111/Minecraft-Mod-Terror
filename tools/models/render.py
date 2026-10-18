"""Local preview renderer: three.js in headless Chromium -> PNG.

render_views(model, texture, out_png, focus_bone='head') writes one image with:
  row 1: full body from front, 3/4 front, side, 3/4 back, back (auto-framed)
  row 2: close-ups of `focus_bone` (front, 3/4) + full body under dark "in-game night" lighting
Safe to call from several processes at once (unique temp files).
"""
import base64
import io
import json
import os
import subprocess
import tempfile

SP = '/tmp/claude-0/-home-user-Minecraft-Mod-Terror/f464a6ad-b203-50f8-a993-93d7fecfc5d1/scratchpad'
HERE = os.path.dirname(os.path.abspath(__file__))
THREE = SP + '/render/node_modules/three/build/three.min.js'
SHOT = SP + '/render/shot.mjs'

PAGE = r'''<!doctype html><html><body style="margin:0;background:#1d1a24">
<canvas id=c></canvas>
<script src="file://%(three)s"></script>
<script src="file://%(viewer)s"></script>
<script>
const SPEC = %(spec)s;
const W = SPEC.w, H = SPEC.h;
const renderer = new THREE.WebGLRenderer({canvas: document.getElementById('c'), antialias: false, preserveDrawingBuffer: true});
renderer.setSize(W, H);
renderer.setScissorTest(true);
const img = new Image();
img.onload = () => {
  const tex = new THREE.Texture(img); tex.needsUpdate = true;
  const cells = [];
  for (const v of SPEC.views) {
    const scene = new THREE.Scene();
    const dark = v.dark;
    scene.background = new THREE.Color(dark ? 0x07060a : 0x2a2632);
    if (dark) {
      scene.fog = new THREE.Fog(0x07060a, 40, 220);
      scene.add(new THREE.AmbientLight(0x9a94b8, 0.35));
      const moon = new THREE.DirectionalLight(0xbfc8ff, 0.5); moon.position.set(-1, 1.4, 0.6); scene.add(moon);
      const torch = new THREE.PointLight(0xffb070, 2.2, 160, 1.2); torch.position.set(30, 20, 60); scene.add(torch);
    } else {
      scene.add(new THREE.AmbientLight(0xffffff, 1.25));
      const key = new THREE.DirectionalLight(0xffffff, 1.5); key.position.set(-0.6, 1, 1.2); scene.add(key);
      const fill = new THREE.DirectionalLight(0xffffff, 0.45); fill.position.set(0.8, 0.3, -1); scene.add(fill);
    }
    const built = MCViewer.buildModel(THREE, SPEC.data, tex);
    if (SPEC.pose) for (const [k, p] of Object.entries(SPEC.pose)) built.pose(k, ...p);
    scene.add(built.object);
    built.object.updateMatrixWorld(true);
    let box = new THREE.Box3().setFromObject(built.object);
    if (v.focus && built.groups[v.focus]) {
      box = new THREE.Box3();
      for (const ch of built.groups[v.focus].children) if (ch.isMesh) box.expandByObject(ch);
      if (box.isEmpty()) box = new THREE.Box3().setFromObject(built.groups[v.focus]);
    }
    const size = new THREE.Vector3(), center = new THREE.Vector3();
    box.getSize(size); box.getCenter(center);
    const cam = new THREE.PerspectiveCamera(v.fov || 28, 1, 0.5, 2000);
    const ext = Math.max(size.y, size.x * 1.1, size.z * 0.8) * (v.focus ? 1.25 : 1.0);
    const dist = ext / (2 * Math.tan((cam.fov * Math.PI / 180) / 2)) * 1.15;
    const a = v.angle * Math.PI / 180, el = (v.elev || 8) * Math.PI / 180;
    cam.position.set(center.x + Math.sin(a) * Math.cos(el) * dist, center.y + Math.sin(el) * dist, center.z + Math.cos(a) * Math.cos(el) * dist);
    cam.lookAt(center);
    cells.push({scene, cam, ...v});
  }
  for (const c of cells) {
    renderer.setViewport(c.x, H - c.y - c.h, c.w, c.h); renderer.setScissor(c.x, H - c.y - c.h, c.w, c.h);
    c.cam.aspect = c.w / c.h; c.cam.updateProjectionMatrix();
    renderer.render(c.scene, c.cam);
  }
  window.__done = true;
};
img.src = SPEC.png;
</script></body></html>'''


def _png_uri(im):
    b = io.BytesIO()
    im.save(b, 'PNG')
    return 'data:image/png;base64,' + base64.b64encode(b.getvalue()).decode()


def render_spec(data, texture, views, w, h, out, pose=None):
    spec = {'data': data, 'png': _png_uri(texture), 'views': views, 'w': w, 'h': h, 'pose': pose}
    html = PAGE % {'three': THREE, 'viewer': os.path.join(HERE, '..', 'preview', 'mcviewer.js'), 'spec': json.dumps(spec)}
    fd, path = tempfile.mkstemp(suffix='.html', dir=SP + '/render')
    with os.fdopen(fd, 'w') as fh:
        fh.write(html)
    try:
        r = subprocess.run(['node', SHOT, path, out, str(w), str(h)], capture_output=True, text=True, timeout=120)
        errs = [l for l in r.stdout.splitlines() if 'pageerror' in l or 'Error' in l]
        if r.returncode or errs:
            print('render problems:', r.returncode, '\n'.join(errs)[-2000:], r.stderr[-2000:])
    finally:
        os.unlink(path)


def render_views(model, texture, out, focus_bone='head', pose=None, cell=300):
    data = model.to_json()
    views = []
    angles = [0, 35, 90, 145, 180]
    for i, a in enumerate(angles):
        views.append({'angle': a, 'x': i * cell, 'y': 0, 'w': cell, 'h': int(cell * 1.6)})
    row2 = int(cell * 1.6)
    has_focus = focus_bone and any(b.name == focus_bone for b in model.bones())
    if has_focus:
        views.append({'angle': 0, 'focus': focus_bone, 'elev': 4, 'x': 0, 'y': row2, 'w': cell * 2, 'h': int(cell * 1.4)})
        views.append({'angle': 32, 'focus': focus_bone, 'elev': 10, 'x': cell * 2, 'y': row2, 'w': cell, 'h': int(cell * 1.4)})
    views.append({'angle': 20, 'dark': True, 'x': cell * 3, 'y': row2, 'w': cell * 2, 'h': int(cell * 1.4)})
    render_spec(data, texture, views, cell * 5, row2 + int(cell * 1.4), out, pose)


def render(models, out, w=1400, h=560):
    """Back-compat: several models side by side, one view each (auto-framed)."""
    from PIL import Image
    tiles = []
    for i, m in enumerate(models):
        fd, tmp = tempfile.mkstemp(suffix='.png', dir=SP + '/render')
        os.close(fd)
        n = len(m.get('angles', [20]))
        cw = w // max(1, len(models)) // n
        views = [{'angle': a, 'x': j * cw, 'y': 0, 'w': cw, 'h': h} for j, a in enumerate(m.get('angles', [20]))]
        render_spec(m['data'], m['png'], views, cw * n, h, tmp, m.get('pose'))
        tiles.append(Image.open(tmp).copy())
        os.unlink(tmp)
    sheet = Image.new('RGB', (sum(t.width for t in tiles), h), (29, 26, 36))
    x = 0
    for t in tiles:
        sheet.paste(t, (x, 0))
        x += t.width
    sheet.save(out)
