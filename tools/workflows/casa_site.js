export const meta = {
  name: 'deadline-casa-site',
  description: 'Build the Casa Morales site (tools/sites/casa.py) from the casa kits with story markers, then art-direct and playtest it',
  phases: [
    { title: 'Build', detail: 'site designer builds the house, patio, basement and markers' },
    { title: 'Review', detail: 'art director (renders) + level designer (walkcheck, markers vs script)' },
    { title: 'Refine', detail: 'fix every issue' },
  ],
}
const ROOT = '/home/user/Minecraft-Mod-Terror'
const SP = '/tmp/claude-0/-home-user-Minecraft-Mod-Terror/f464a6ad-b203-50f8-a993-93d7fecfc5d1/scratchpad'

const common = `Project ${ROOT}: Minecraft 1.21.11 horror-comedy mod "DEAD LINE" for a 20-minute YouTube video. Case 2 is "Casa Morales": design in ${ROOT}/docs/design/BIBLIA.md section 2.2 (read ALL of it: f. El lugar with the floor plan and room table, h. Guion de sustos (17 beats), j. Mecánicas, m. Resolución).
The site is authored in Python like the finished Colegio: read ${ROOT}/tools/sites/sitekit.py (Site, Palette, room/fill/set/door, markers: points (x,y,z,facing), areas, groups, doors, writes, lights; check_markers) and ${ROOT}/tools/sites/colegio.py (the reference: helpers K(), stairs(), doorway(), skirting(), how furniture faces, SEALED, lights/fixtures, export to src/main/resources/data/deadline/sites/<key>.json). Block conventions (facing, izq/der, doors, in-wall windows) are documented in ${ROOT}/tools/blocks/BLOCK_GUIDE.md and in the docstrings of the kits.
Use ONLY the casa building kits for the house (no vanilla blocks except air/light/water where the kit has nothing): ${ROOT}/tools/blocks/kit_casa_estructura.py and kit_casa_muebles.py (block keys 'casa_*'; list them with: python3 -c "import json; d=json.load(open('${ROOT}/tools/blocks/out/preview_all.json')); print([b['key'] for k in ('casa_estructura','casa_muebles') for b in d['kits'][k]])"; the room mock-ups in ${ROOT}/tools/blocks/scenes/casa_*.py show how the pieces combine). Lamps exist in lit/off pairs (<key> and <key>_apagado/_apagada) that the director swaps (Fixtures).
Tools: \`python3 tools/sites/casa.py\` (export + plan image), \`python3 tools/sites/walkcheck.py casa\` (can the player walk from spawn to every story point; SEALED points are skipped), \`python3 tools/sites/siterender.py casa --point <marker>\` or \`--camera x y z --target x y z [--box ...]\` (day + night render of the real site; Read the PNG in ${SP}/blocks/).

MARKER CONTRACT (the script CasaScript will use exactly these names; add more if a beat needs them, never rename):
points (x,y,z,facing; standing positions): spawn (sidewalk, facing the house), vereda, marta_puerta, living, jorge_sillon, tv, nona_living, pasillo_pb, comedor, torre_sillas, cocina, mate_spot, termo_spot, ventana_cocina (inside, at the kitchen window over the patio), tablero (laundry breaker), lavadero, sotano_escalera, nona_cuarto (Nona in her rocker), altar, choripan_333 (where Choripan sits in the ground-floor hall at 3:33), escalera_arriba (top of the stair, dark), pasillo_1p, lucia_cuarto, lucia_cama, lucia_bajo_cama, lucia_techo, estante_munecas, toti_cuarto, placard (inside the 2x1x3 wardrobe, where the player hides), toti_placard (Toti inside, next to it), matrimonial, bano, espejo_bano, patio, ventana_fondo (a window in the house from which the doghouse is visible), cucha (doghouse door), cucha_techo, cucha_cola (tail inside the doghouse), parrilla (the grill cooking spot, INSIDE the salt circle), silla_jorge (Jorge's plastic chair next to the grill), porton (car gate where Jorge comes in), pelopincho (pool centre), medianera (top of the party wall the wisp crosses), ofelia_cucha, ofelia_silla_jorge, ofelia_almohada, ofelia_falda, sotano, sotano_pared (in front of the cracked wall), cuarto61 (centre of the 1961 room), nona_flota (where the floating rocker hangs), desayuno, marta_desayuno, jorge_desayuno, toti_desayuno, nona_desayuno, choripan_desayuno, marta_chat (where Marta shows the phone, living/hall), choripan_casa (dog's bed or spot near Nona).
areas: casa, vereda, living, comedor, cocina, nona_cuarto, lavadero, pasillo_pb, escalera, pasillo_1p, lucia, toti, matrimonial, bano, sotano, cuarto61, patio, parrilla_circulo, placard.
groups: comedor_sillas (the 8 chairs), alacenas (kitchen cupboards), luces_pb (ground-floor lamps), luces_cocina, pasillo_1p_luces (one lamp every 4 blocks along the upper hall), altar_velas, estante_munecas (the doll shelf blocks), cuchillos (the knife rack), sotano_pared (the cracked wall blocks the Nona breaks: swapped to the broken-through variant / air), sal_parrilla (the r=3 salt circle around the grill: use the floor decal quarter pieces), farol (street lamp), tv (the CRT TV, on/static/off variants).
doors: entrada, puerta_vereda (pedestrian gate), porton (car gate, 2 wide), nona, bano, cocina, lavadero, sotano, lucia, toti, matrimonial, placard (the wardrobe door), and pasillo_1p doors in a row (the cascade: lucia, toti, matrimonial, bano_1p if any).
writes: lemaza (1961 room wall, children's scratches), espejo_azamel (bathroom mirror, UV only), cuaderno (Lucia's notebook 'MI AMIGO SE LLAMA LEMAZA').
SEALED in walkcheck: cuarto61 and nona_flota (behind the cracked wall until the Nona breaks it), placard/toti_placard only if the wardrobe is not walkable, lucia_techo, cucha_cola, medianera.
Layout constraints from the bible: lot 36x40, sidewalk towards -Z; house X -10..10, Z 0..14 (21x15), ground floor y=0, first floor y=5, basement y=-5; patio Z 15..34 with the grill + salt circle r=3 on brick paving, long table, pelopincho 6x4 with murky green water (no lid), doghouse 'CHORIPAN' 3x3, lemon tree, clothesline with sheets; basement 15x9 (boiler, sheeted furniture, jars, hanging bulb, the CRACKED wall) leading to the 1961 room 9x9x4 with sand floor, iron bed with straps, old salt circle, melted candles, Anselmo's stole. No garage, no attic. Real-world believable proportions (ceiling 3 high, doors 2, windows with rejas and persianas, skirting, cornices), lived-in clutter, night mood. The player must be able to walk every room (doors 1 wide minimum, stairs walkable), and the chase (demon dog through patio and house) needs loops.`

const build = `${common}

Write ${ROOT}/tools/sites/casa.py (if it already exists from an interrupted run, read it and CONTINUE it instead of starting over; export key 'casa', site json ${ROOT}/src/main/resources/data/deadline/sites/casa.json). SAVE EARLY AND OFTEN: write the file to disk at the end of the very first pass and after every later pass, always leaving it runnable, so an interruption never loses the work. Build in passes: shell and floors -> rooms and doors/windows -> stairs and basement -> furniture and clutter per room -> patio -> street -> markers -> lights. After each pass: export, walkcheck, render several rooms by day and night with siterender and Read them; fix what looks wrong (wrong facing, floating props, gaps, missing ceilings, blocks clipping, empty rooms). At least 10 render cycles. Only create/edit tools/sites/casa.py (and scratch files under ${SP}). Never edit kits, sitekit.py, walkcheck.py or Java; never run git. Return a summary: rooms built, marker list, walkcheck result, known issues.`

const ISSUES = { type: 'object', properties: { scores: { type: 'object', properties: { believable: { type: 'number' }, craft: { type: 'number' }, mood: { type: 'number' }, playable: { type: 'number' } } },
  issues: { type: 'array', items: { type: 'object', properties: { severity: { type: 'string', enum: ['critical', 'major', 'minor'] }, problem: { type: 'string' }, fix: { type: 'string' } }, required: ['severity', 'problem', 'fix'] } } }, required: ['issues'] }

const art = `${common}

YOU ARE THE ART DIRECTOR. Do NOT edit files. Export the site, then render at least 14 views (every room, the facade from the sidewalk, the patio with the grill, the doghouse, the basement and the 1961 room) with siterender (use --point on the markers and --camera/--target for wide shots) and Read them. Judge: does it read as a real 1950s Argentine chalet lived in by a working-class family in 2026; proportions at player scale; furniture placement and facing; clutter and story details; night mood; repetition; technical errors (floating blocks, gaps in walls/ceilings, wrong-facing furniture, z-fighting, missing roof parts, windows into nothing). Scores 1-10 and concrete fixes ordered by severity.`

const level = `${common}

YOU ARE THE LEVEL DESIGNER. Do NOT edit files. Export the site, run walkcheck, read casa.py and the beats in the bible. Check: every marker in the contract exists with sensible coordinates and facing (actors face where the beat needs; Ofelia spots are on the doghouse roof/Jorge's chair/Lucía's pillow/Nona's lap; parrilla is inside the salt circle; placard really fits the player inside the wardrobe with the door closable; the ventana_fondo window really shows the doghouse; the porton opens to the street; the cracked wall separates the basement from the 1961 room), every group/door/write exists, doors open the right way, the demon-dog chase has loops and is not a dead end, the stair is walkable, nothing blocks a doorway, the house is not too big to cross in the video's pacing. Render any spot you need with siterender. Concrete fixes ordered by severity.`

const refine = (a, l) => `${common}

Two reviewers checked ${ROOT}/tools/sites/casa.py.
ART DIRECTOR (${JSON.stringify(a && a.scores || {})}):
${(a && a.issues || []).map((i, n) => `${n + 1}. [${i.severity}] ${i.problem}\n   FIX: ${i.fix}`).join('\n')}
LEVEL DESIGNER:
${(l && l.issues || []).map((i, n) => `${n + 1}. [${i.severity}] ${i.problem}\n   FIX: ${i.fix}`).join('\n')}

Fix every critical and major issue, then the minor ones, re-exporting, running walkcheck and rendering after each batch (at least 6 render cycles). Only edit tools/sites/casa.py. Never run git. Return a summary with the final marker list and walkcheck output.`

phase('Build')
const b = await agent(build, { label: 'build:casa_site', phase: 'Build' })
phase('Review')
const [a, l] = await parallel([
  () => agent(art, { label: 'art-director', phase: 'Review', schema: ISSUES }),
  () => agent(level, { label: 'level-designer', phase: 'Review', schema: ISSUES }),
])
phase('Refine')
const r = await agent(refine(a, l), { label: 'refine:casa_site', phase: 'Refine' })
return { build: b, art: a, level: l, refine: r }
