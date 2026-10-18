# DEAD LINE — entity art guide

DEAD LINE is a Minecraft 1.21.11 horror mod built to be filmed for YouTube/TikTok. Every creature must be
**instantly terrifying in a thumbnail and in a jumpscare close-up**. The first versions were rejected by the
owner as amateur: "thin, no faces, not scary — they must be deformed, with a characteristic shape, truly
professional, better than any existing mod". Treat that as the bar.

## What "professional" means here

* **Silhouette first.** Readable as a black shape: exaggerated, wrong proportions (too-long limbs/fingers/neck,
  hunched spines, dislocated jaws, oversized heads, protruding ribs/vertebrae, antlers, tattered cloth). Thick
  enough masses — no stick figures. Asymmetry is good (a dropped shoulder, a twisted wrist, a tilted head).
* **A face you remember.** Big head relative to vanilla, a front face of at least ~14×14 texels, hand-placed pixel
  art with shading: eye sockets with depth (darker ring → black → tiny glint), mouths with teeth/gums/darkness,
  wrinkles, cracks, veins, tears. A separate `jaw` bone wherever a mouth can open. Faces must read at 64 px tall.
* **Depth in the geometry.** Layer cubes: skull + jaw + brow ridge + nose, ribs as separate slats, fingers and
  claws as separate cubes/bones, clothing as several angled panels (rotated bones), hair as many rotated strands.
  Use `inflate` for overlapping cloth/hair shells and zero-thickness planes (one size = 0) for strands, tatters,
  teeth, claws and veils.
* **Painted textures, not noise.** Vanilla-quality pixel art: 4–7 tone hue-shifted ramps per material, clear value
  grouping, darker edges/creases, deliberate highlights, hand-placed details (stitches, stains, bones under skin,
  blood drips, mud, frayed hems). Avoid uniform fbm static. Use `paint.dither` sparingly.
* **Contrast that survives darkness.** Cases are filmed at night with fog and a flashlight. Pale skin vs black hair,
  glowing eyes (emissive layer), red accents. Check the "dark" cell of the preview.

## Technical conventions (read carefully)

* Author with `rig.Rig` in ABSOLUTE model coordinates: units are texels, **+Y is down**, the ground is **y = 24**,
  the creature **faces −Z** (its face goes on the cube's `'front'` face), −X is the viewer's left when looking at the
  creature's face.
* **Work at 2× texel density:** build the creature at twice its real size and set `model.scale = 0.5`.
  Real height in blocks = (24 − top_y) / 32. Example: a 2.5-block creature spans y = 24 down to y = −56.
* Texture: width/height multiples of 16, at most 256×256 (`Model(name, w, h, roots)`); UVs are auto-packed.
  Budget: ≤ 220 cubes, ≤ 60 bones.
* Bones rotate around their pivot (degrees in `rig.bone(..., rot=(x, y, z))`); MC applies Z·Y·X. A positive X
  rotation swings a hanging limb's lower end **backwards (+Z)**; negative swings it forward.
* Render type: default `entityCutoutNoCull` (alpha must be 0 or 255). For semi-transparent ghosts set
  `model.render_type = 'entityTranslucent'` (or `'entityTranslucentEmissive'` for glowing spirits).
* Emissive glow (eyes, ember pupils, mouth glow): add a decal under the key `'eyes:<face>'`
  (e.g. `'eyes:front'`) that paints ONLY the glowing pixels; it is rendered full-bright on top of the model.
* Materials: `fn(ctx) -> rgba | None`; decals: `fn(img, u0, v0, w, h)`. Helpers in `tools/models/paint.py`
  (`ramp`, `pixelart`, `edge_dark`, `lit`, `dither`, `mix`, …) and noise in `mcmodel.py` (`fbm`, `vnoise`, `hash3`).
  Existing palettes in `emat.py` may be reused.
* Bone names are a contract with the Java animation code. Use these names where the anatomy exists:
  `body` (or `torso`), `neck`, `head`, `jaw`, `right_arm`/`left_arm`, `right_forearm`/`left_forearm`,
  `right_hand`/`left_hand`, `right_leg`/`left_leg` (+ `_shin`, `_foot`), plus any extra parts with clear names
  (`hair_back`, `veil`, `skirt_front`, `tail`, `right_antler`, …). `right_*` is on −X. Put pivots at the joints.

## Module contract — `tools/models/ent_<key>.py`

```python
DEFAULT_MAT = some_material          # used for cubes/bones without a material
FOCUS = 'head'                       # bone framed in the close-up views
POSES = {'attack': {'jaw': (0.9, 0, 0, 0, 0, 0), ...}}   # optional: bone -> (xRot, yRot, zRot, dx, dy, dz),
                                     # radians / texels, ADDED to the rest pose (preview: --pose attack)
ANIM_NOTES = "..."                   # bone roles + how each part should move (idle / chase / attack / special)
def build() -> Model: ...            # returns mcmodel.Model with scale = 0.5
```

## Preview loop (mandatory)

```
python3 tools/models/preview.py <key>              # rest pose
python3 tools/models/preview.py <key> --pose attack
```
Outputs `<scratchpad>/models/<key>/views.png` (5 angles + face close-ups + dark night shot) and `texture.png`
(the UV sheet, 6× with face outlines). **Open both images with the Read tool after every change** and judge them
honestly against the bar above. Iterate many times. The preview is a faithful MC box-model renderer.

Vanilla textures for style reference can be fetched, e.g.
`curl -s -o /tmp/x.png https://raw.githubusercontent.com/misode/mcmeta/1.21.11-assets/assets/minecraft/textures/entity/warden/warden.png`.

## Rules

* Only create/edit `tools/models/ent_<key>.py` (and optional `tools/models/ent_<key>_*.py` helpers).
  Do NOT edit shared files (`mcmodel.py`, `rig.py`, `paint.py`, `emat.py`, `render.py`, `preview.py`,
  `build_all.py`, `tools/preview/*`) and never run git.
* Keep it original (inspired by folklore and the horror genre, not copies of film characters).
