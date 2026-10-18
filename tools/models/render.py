"""Local preview: render model views to PNG with three.js in headless Chromium."""
import base64, io, json, os, subprocess, sys
SP = '/tmp/claude-0/-home-user-Minecraft-Mod-Terror/f464a6ad-b203-50f8-a993-93d7fecfc5d1/scratchpad'
HERE = os.path.dirname(os.path.abspath(__file__))

PAGE = r'''<!doctype html><html><body style="margin:0;background:#16141c">
<canvas id=c></canvas>
<script src="file://%(three)s"></script>
<script src="file://%(viewer)s"></script>
<script>
const models = %(models)s;
const W = %(w)d, H = %(h)d;
const renderer = new THREE.WebGLRenderer({canvas: document.getElementById('c'), antialias: false, preserveDrawingBuffer: true});
renderer.setSize(W, H);
renderer.setScissorTest(true);
let loaded = 0;
const views = [];
models.forEach((m, mi) => {
  const img = new Image();
  img.onload = () => {
    const tex = new THREE.Texture(img); tex.needsUpdate = true;
    for (const ang of m.angles) {
      const scene = new THREE.Scene();
      scene.add(new THREE.AmbientLight(0xffffff, 1.4));
      const dl = new THREE.DirectionalLight(0xffffff, 1.6); dl.position.set(-0.6, 1, 1.2); scene.add(dl);
      const built = MCViewer.buildModel(THREE, m.data, tex);
      if (m.pose) for (const [k, v] of Object.entries(m.pose)) built.pose(k, ...v);
      scene.add(built.object);
      const cam = new THREE.PerspectiveCamera(32, 1, 1, 500);
      const r = m.dist, a = ang * Math.PI / 180;
      cam.position.set(Math.sin(a) * r, m.camY, Math.cos(a) * r);
      cam.lookAt(0, m.lookY, 0);
      views.push({scene, cam});
    }
    if (++loaded === models.length) draw();
  };
  img.src = m.png;
});
function draw() {
  const n = views.length, vw = Math.floor(W / n);
  views.forEach((v, i) => {
    renderer.setViewport(i * vw, 0, vw, H); renderer.setScissor(i * vw, 0, vw, H);
    v.cam.aspect = vw / H; v.cam.updateProjectionMatrix();
    renderer.setClearColor(0x1d1a24); renderer.render(v.scene, v.cam);
  });
  window.__done = true;
}
</script></body></html>'''


def render(models, out, w=1400, h=560):
    """models: list of dict(data=json, png=PIL, angles=[...], dist, camY, lookY, pose)"""
    ms = []
    for m in models:
        b = io.BytesIO(); m['png'].save(b, 'PNG')
        ms.append({'data': m['data'], 'png': 'data:image/png;base64,' + base64.b64encode(b.getvalue()).decode(),
                   'angles': m.get('angles', [0, 35, 90, 180]), 'dist': m.get('dist', 90), 'camY': m.get('camY', 22),
                   'lookY': m.get('lookY', 16), 'pose': m.get('pose')})
    html = PAGE % {'three': SP + '/render/node_modules/three/build/three.min.js', 'viewer': HERE + '/../preview/mcviewer.js',
                   'models': json.dumps(ms), 'w': w, 'h': h}
    p = SP + '/render/page.html'
    open(p, 'w').write(html)
    r = subprocess.run(['node', SP + '/render/shot.mjs', p, out, str(w), str(h)], capture_output=True, text=True)
    if r.returncode or r.stdout.strip():
        print(r.stdout[-3000:], r.stderr[-3000:])
