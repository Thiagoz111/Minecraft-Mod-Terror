// Minecraft box-model builder for three.js (shared by the local renderer and the preview page).
// Model space: +Y down, model faces -Z, ground at y=24. three space: (x, -y, -z), ground at 0.
(function (global) {
  function cubeMesh(THREE, c, texW, texH, mat) {
    const [w, h, d] = c.size;
    const g = c.inflate || 0;
    let x0 = c.origin[0] - g, y0 = c.origin[1] - g, z0 = c.origin[2] - g;
    let x1 = c.origin[0] + w + g, y1 = c.origin[1] + h + g, z1 = c.origin[2] + d + g;
    if (c.mirror) { const t = x0; x0 = x1; x1 = t; }
    const W = x1 - x0, H = y1 - y0, D = z1 - z0;
    const [u, v] = c.uv;
    const faces = [
      // rect [u0, v0, fw, fh], point(s,t)
      [[u + d, v + d, w, h], (s, t) => [x0 + s * W, y0 + t * H, z0]],              // front (-Z)
      [[u + 2 * d + w, v + d, w, h], (s, t) => [x1 - s * W, y0 + t * H, z1]],      // back
      [[u, v + d, d, h], (s, t) => [x0, y0 + t * H, z1 - s * D]],                  // west
      [[u + d + w, v + d, d, h], (s, t) => [x1, y0 + t * H, z0 + s * D]],          // east
      [[u + d, v, w, d], (s, t) => [x0 + s * W, y0, z1 - t * D]],                  // top
      [[u + d + w, v, w, d], (s, t) => [x0 + s * W, y1, z1 - t * D]],              // bottom
    ];
    const pos = [], uvs = [];
    for (const [[fu, fv, fw, fh], P] of faces) {
      if (fw <= 0 || fh <= 0) continue;
      const corners = [[0, 0], [1, 0], [1, 1], [0, 1]];
      const pts = corners.map(([s, t]) => { const p = P(s, t); return [p[0], -p[1], -p[2]]; });
      const tex = corners.map(([s, t]) => [(fu + s * fw) / texW, 1 - (fv + t * fh) / texH]);
      for (const idx of [0, 1, 2, 0, 2, 3]) { pos.push(...pts[idx]); uvs.push(...tex[idx]); }
    }
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
    geo.setAttribute('uv', new THREE.Float32BufferAttribute(uvs, 2));
    geo.computeVertexNormals();
    return new THREE.Mesh(geo, mat);
  }

  function buildModel(THREE, data, texture) {
    texture.magFilter = THREE.NearestFilter;
    texture.minFilter = THREE.NearestFilter;
    texture.generateMipmaps = false;
    if (THREE.SRGBColorSpace) texture.colorSpace = THREE.SRGBColorSpace;
    const mat = new THREE.MeshLambertMaterial({ map: texture, transparent: true, alphaTest: 0.04, side: THREE.DoubleSide });
    const groups = {}, rest = {};
    const root = new THREE.Group();
    const d2r = Math.PI / 180;
    for (const b of data.bones) {
      const g = new THREE.Group();
      g.position.set(b.pivot[0], -b.pivot[1], -b.pivot[2]);
      g.rotation.order = 'ZYX';
      g.rotation.set(b.rot[0] * d2r, -b.rot[1] * d2r, -b.rot[2] * d2r);
      groups[b.name] = g;
      rest[b.name] = { p: g.position.clone(), r: g.rotation.clone() };
      (b.parent ? groups[b.parent] : root).add(g);
      for (const c of b.cubes) g.add(cubeMesh(THREE, c, data.texW, data.texH, mat));
    }
    const holder = new THREE.Group();
    root.position.y = 24;
    holder.add(root);
    if (data.scale && data.scale !== 1) holder.scale.setScalar(data.scale);
    // MC rotation helpers: set(part, xRot, yRot, zRot) in MC radians, added to rest pose
    function pose(name, xr, yr, zr, dx, dy, dz) {
      const g = groups[name]; if (!g) return;
      const r0 = rest[name];
      g.rotation.set(r0.r.x + (xr || 0), r0.r.y - (yr || 0), r0.r.z - (zr || 0));
      g.position.set(r0.p.x + (dx || 0), r0.p.y - (dy || 0), r0.p.z - (dz || 0));
    }
    return { object: holder, groups, pose };
  }
  global.MCViewer = { buildModel };
})(typeof window !== 'undefined' ? window : globalThis);
