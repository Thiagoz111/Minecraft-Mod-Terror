# DEAD LINE — building kit guide

The owner wants every location built from OUR OWN blocks and furniture ("no uses bloques de Minecraft, diseñá todo, se ve
mejor"). Every case (family house, nun school, abandoned hospital) gets a complete kit: walls, floors, ceilings, trims,
doors, windows, furniture, appliances, props and set dressing — all hand-designed, 32 px per block (twice vanilla
resolution), consistent in style, believable, filthy/abandoned where the story needs it, and creepy at night under a
flashlight. It must look better than any Minecraft map or furniture mod.

## Files
* `tools/blocks/bkit.py` — the framework (read its docstring: coordinates, face orientation, classes).
* `tools/blocks/kit_<case>_<theme>.py` — one module per kit theme; importing it registers its blocks.
* `tools/blocks/build_blocks.py <kit>` — exports only `kit_<kit>*.py` (fast, isolated from other kits being edited).
  `build_blocks.py --all` (run by the lead, not by kit designers) also regenerates the Java registry and lang.
* `tools/blocks/brender.py` — previews: `showroom <kit>` (every block of a kit) and `scene <file>` (a room mock-up,
  rendered by day and at night with a flashlight).
* `tools/blocks/scenes/<name>.py` — room mock-ups (`SCENE = dict(blocks=[(x, y, z, key, facing), ...], camera=..., target=...)`).

Loop: edit kit -> `python3 tools/blocks/build_blocks.py <kit>` -> `python3 tools/blocks/brender.py showroom <kit>` and
`... scene tools/blocks/scenes/<room>.py` -> Read the PNGs in the scratchpad `blocks/` folder -> judge -> repeat.

## Block types (bkit classes)
* `Cube(key, name_es, name_en, mat=..., faces={'up':..,'side':..,'down':..}, variants=n, animated=(frames, ticks))` —
  full blocks: walls, floors, ceilings, tiles. `variants>1` = random texture per placed block (break repetition: dirt,
  cracks, stains). Textures must TILE seamlessly with neighbours of the same block (paint patterns periodic in 32 px).
* `Slab`, `Stairs` (`of=<Cube>`) — reuse a cube's textures.
* `Furniture(key, name_es, name_en, parts=[box(...), plane(...)], directional=True, collision='auto'|'full'|'none', light=0..15)`
  — anything modelled from boxes: furniture, appliances, props, lamps, windows, trims, wall panels, wainscoting, curtains,
  hanging lights, signs, wall decals. Faces north. Parts can rotate (axis, ±22.5/±45). Elements may span -16..32 for
  pieces bigger than a block, but collision is clipped to the block — split very big objects (double bed, sofa, hospital
  bed) into left/right or head/foot blocks with matching keys (`sofa_left`, `sofa_right`).
* `Door(key, ..., mat)` — real opening doors (32x32 'bottom' and 'top' halves; `ctx.face` is 'bottom' or 'top').
* `Trapdoor(key, ..., mat)`.
* Common args: `kit` (e.g. 'casa'), `sound` (wood/stone/wool/metal/glass/tile/plaster/ceramic/cloth/paper/dirt/grass/plant/sand),
  `render` ('solid' cubes, 'cutout' anything with transparent pixels, 'translucent' for glass/curtains/ghostly),
  `light` (0-15), `breakable` (False = props survive survival players).

## Painting rules
* Materials are `fn(ctx) -> (r, g, b, a)` or `None` (transparent; needs render 'cutout'). Use `tools/models/paint.py`
  helpers: `hx`, `ramp` (hue-shifted 4-8 tone ramps), `pick(ramp, v)`, `mix`, `edge_dark`, `pixelart` decals, `dither`.
* Hand-crafted pixel art, not noise: deliberate patterns (wallpaper motifs, tile grout, wood grain with knots, fabric
  weave), clear value structure, crisp 1 px edges/bevels, believable wear (scuffs at the bottom of walls, water stains
  from the ceiling, grime in grout lines, chipped paint, mould, fingerprints, blood only where the story puts it).
* Never bake directional light (Minecraft shades faces). Do paint ambient-occlusion-like darkening in corners/crevices.
* Consistent palettes per location (the bible defines the mood). Keep saturation natural; the horror comes from wear,
  details and contrast under the flashlight.
* Use `variants` and decorative separate blocks (stained versions, cracked versions, versions with writing) so builds
  never look tiled.

## Quality bar
* Recognisable at a glance in first person, readable under a flashlight in the dark (check the night half of scenes).
* Proportions right for a player (1.8 blocks tall): door height 2 blocks, table top at ~12/16, chair seat at ~8/16,
  counters at ~14/16, beds ~9/16, ceilings 3 blocks.
* Every important story clue/prop is its own block (e.g. the family photo with scratched faces, the blackboard with
  writing, the streamer's ring light).
* No z-fighting (offset overlapping faces by >= 0.01), no gaps, no floating parts, no missing faces seen from the player.
* Name every block in Spanish (rioplatense) and English. Prefix keys with the location: `casa_`, `colegio_`, `hosp_`.
