// Block-model builder for three.js (DEAD LINE building kit previews). Mirrors Minecraft's block model UV rules.
(function (global) {
  const FACE_POINT = {
    north: (e, s, t) => [e.to[0] - s * (e.to[0] - e.from[0]), e.to[1] - t * (e.to[1] - e.from[1]), e.from[2]],
    south: (e, s, t) => [e.from[0] + s * (e.to[0] - e.from[0]), e.to[1] - t * (e.to[1] - e.from[1]), e.to[2]],
    west: (e, s, t) => [e.from[0], e.to[1] - t * (e.to[1] - e.from[1]), e.from[2] + s * (e.to[2] - e.from[2])],
    east: (e, s, t) => [e.to[0], e.to[1] - t * (e.to[1] - e.from[1]), e.to[2] - s * (e.to[2] - e.from[2])],
    up: (e, s, t) => [e.from[0] + s * (e.to[0] - e.from[0]), e.to[1], e.from[2] + t * (e.to[2] - e.from[2])],
    down: (e, s, t) => [e.from[0] + s * (e.to[0] - e.from[0]), e.from[1], e.to[2] - t * (e.to[2] - e.from[2])],
  };
  const SHADE = { up: 1.0, down: 0.5, north: 0.8, south: 0.8, west: 0.6, east: 0.6 };

  function rotatePoint(p, rot) {
    if (!rot) return p;
    const a = rot.angle * Math.PI / 180, o = rot.origin;
    let [x, y, z] = [p[0] - o[0], p[1] - o[1], p[2] - o[2]];
    const c = Math.cos(a), s = Math.sin(a);
    if (rot.axis === 'x') [y, z] = [y * c - z * s, y * s + z * c];
    else if (rot.axis === 'y') [x, z] = [x * c + z * s, -x * s + z * c];
    else [x, y] = [x * c - y * s, x * s + y * c];
    return [x + o[0], y + o[1], z + o[2]];
  }

  // elements: block-model elements; tex: THREE.Texture; returns a Group in block units (1 = one block), origin at block corner
  function buildElements(THREE, elements, tex, opts) {
    opts = opts || {};
    const group = new THREE.Group();
    const pos = [], uv = [], col = [];
    for (const e of elements) {
      for (const [f, face] of Object.entries(e.faces)) {
        const P = FACE_POINT[f];
        const corners = [[0, 0], [1, 0], [1, 1], [0, 1]].map(([s, t]) => rotatePoint(P(e, s, t), e.rotation));
        const [u0, v0, u1, v1] = face.uv;
        const tuv = [[u0, v0], [u1, v0], [u1, v1], [u0, v1]].map(([u, v]) => [u / 16, 1 - v / 16]);
        const sh = e.shade === false ? 1.0 : SHADE[f];
        for (const idx of [0, 1, 2, 0, 2, 3]) {
          pos.push(corners[idx][0] / 16, corners[idx][1] / 16, corners[idx][2] / 16);
          uv.push(tuv[idx][0], tuv[idx][1]);
          col.push(sh, sh, sh);
        }
      }
    }
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
    geo.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2));
    geo.setAttribute('color', new THREE.Float32BufferAttribute(col, 3));
    geo.computeVertexNormals();
    const mat = new THREE.MeshLambertMaterial({ map: tex, vertexColors: true, transparent: !!opts.translucent, alphaTest: opts.translucent ? 0.01 : 0.5, side: THREE.DoubleSide });
    if (opts.emissive) { mat.emissive = new THREE.Color(0xffffff); mat.emissiveMap = tex; mat.emissiveIntensity = opts.emissive; }
    group.add(new THREE.Mesh(geo, mat));
    return group;
  }

  function cubeElements() {
    const faces = {};
    for (const f of ['north', 'south', 'west', 'east', 'up', 'down']) faces[f] = { uv: [0, 0, 16, 16] };
    return [{ from: [0, 0, 0], to: [16, 16, 16], faces }];
  }

  // place: wraps a block group so it rotates around the block centre (facing) and sits at integer pos
  function place(THREE, g, x, y, z, facing) {
    const holder = new THREE.Group();
    const inner = new THREE.Group();
    g.position.set(-0.5, 0, -0.5);
    inner.add(g);
    const yr = { north: 0, east: -Math.PI / 2, south: Math.PI, west: Math.PI / 2 }[facing || 'north'];
    inner.rotation.y = yr;
    inner.position.set(0.5, 0, 0.5);
    holder.add(inner);
    holder.position.set(x, y, z);
    return holder;
  }
  global.BlockView = { buildElements, cubeElements, place };
})(typeof window !== 'undefined' ? window : globalThis);
