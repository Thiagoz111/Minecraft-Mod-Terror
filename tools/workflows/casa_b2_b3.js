export const meta = {
  name: 'casa-b2-b3',
  description: 'Casa horror: B2 hunt + hiding + jumpscares, B3 apparitions + dog + art; each built, adversarially reviewed and fixed',
  phases: [
    { title: 'Build', detail: 'B2 hunter/hiding, B3 apparitions/dog/art' },
    { title: 'Review', detail: 'compile/runtime lens + horror-design lens per item' },
    { title: 'Fix', detail: 'apply every confirmed issue' },
  ],
}

const ROOT = '/home/user/Minecraft-Mod-Terror'
const SP = '/tmp/claude-0/-home-user-Minecraft-Mod-Terror/f464a6ad-b203-50f8-a993-93d7fecfc5d1/scratchpad'

const common = `Project ${ROOT}: Minecraft 1.21.11 Fabric mod "DEAD LINE" (Mojang mappings; Java in src/main/java (common/server) and src/client/java (client only — never import client classes from main); asset generators in tools/). The owner rejected the old comedy/mission style: Casa Morales must be PURE HORROR (adult, blood, deformations, earned jumpscares, escalating random events, no missions, NO spoken dialogue — characters never talk; non-verbal sounds only). Read ${ROOT}/docs/design/casa_terror.md COMPLETELY first: it is the binding design (sections 2 acts, 5 event catalogue, 6 mechanics, 7 characters, 11 marker contract of the site, 12 the horror-engine API that already exists in src/main/java/com/deadline/horror: HorrorEvent, Ctx, Haunt, HorrorEvents, HouseQuery, HorrorCommands — use it, do not rewrite it).
Reusable code: HauntEntity (base of our monsters), MonjaEntity (a finished hearing-based hunter: study its AI, door handling, stun, canWalkTo, teleportNear), casa/FamilyEntity + client casa/FamilyRenderer(s) (family NPCs with poses and looks), PoseidaEntity (Lucía possessed), SombraEntity, MunecaEntity (Ofelia), voice/NoiseMeter + voice/Voice (microphone via Simple Voice Chat), net/Fx (jumpscare, shake, flash, redFlash, staticNoise, fade, soundAt, noise HUD...), director/Run (markers at/yaw/area/inside/looking, door(name,open,slam), lights(group,on), actor/despawn, post(event)), director/Props (spawn actors at markers), phone/PhoneMessages (text/photo/typing to the phone).
Other agents work in the same tree at the same time: A2 (car + overworld placement: com.deadline.car, com.deadline.world, CaseManager, CaseSites, Director, a tiny placeholder director/casa/CasaScript), A3 (rebuilding tools/sites/casa.py — the house; use only marker names from section 11), and the sibling of this workflow (B2 = hunt/hiding, B3 = apparitions/dog/art). Do not edit files owned by others; shared files (DeadLine.java, DeadLineClient.java, ModEntities/registries, FamilyEntity, tools/audio/sounds_def.py, tools/data/lang.py, tools/models/build_all.py KEYS) only with small, unique-anchor Edit calls, never rewriting them; append your sound/lang entries in a block marked with your id ("# --- B2 hunt" / "# --- B3 apparitions") and rerun the generators at the end (tools/audio/gen_defs.py etc. — read how they run; tools/data/lang.py).
THERE IS NO LOCAL JAVA COMPILER (maven blocked; CI compiles after the lead pushes). Be meticulous: verify every Minecraft/Fabric API against existing usages in this repo, /tmp/ref/probe/api*.txt, /tmp/ref/mc_imports.txt and /tmp/ref/fabric-api; prefer patterns the repo already uses; re-read all your files at the end hunting compile errors. Python tools must run. Read-only git (status, diff, log) is allowed; never commit, stash, checkout or reset.`

const B2 = `${common}

YOUR PART: B2 — THE HUNT, HIDING, BREATH, JUMPSCARES ("Ella escucha todo"; Act 5 of the design, sections 6.1, 6.2, 6.6, 6.7, 7 Nona).
1. NonaRotaEntity (package com.deadline.horror.casa.hunt; register in a new HuntEntities.init() wired from DeadLine.java; client renderer wired from DeadLineClient): the possessed grandmother as a hearing-based hunter. She is half-blind (cataracts) and hears everything: player noise from NoiseMeter (scaled by distance, walls/closed doors attenuate), the microphone (Voice.speaking → she goes straight there; loud = immediate chase), doors, thrown/broken objects (expose a static Hunt.noise(Run, Vec3 pos, float loudness) so other events can make noise), flashlight clicks. States: PATROL (wanders between room markers, slow, sometimes upright with walker-less stumble, sometimes spider-crawl), LISTEN (freezes, head tilts, sniffs — the scariest moment, 2-4 s), INVESTIGATE (goes to the last heard spot, opens doors, checks hide spots within 8 blocks of it), CHASE (when she hears you close or you are in her short sight cone < 6 blocks lit by your flashlight: fast spider-crawl ~0.36, opens doors, climbs stairs), SEARCH_HIDE (stands at hide_<id>_out, opens the wardrobe/looks under the bed, her face 30 cm from the slats; if the player is holding breath and silent she leaves, else she drags him out = capture), REPEL (crucifix makes her recoil 3 s and hiss; holy water makes her flee 8 s; salt line she won't cross 20 s — hook into the existing items the way MonjaEntity reacts to them). Capture = fail-forward: Fx.jumpscare('nona_rota') + loud stinger, fade, the player wakes up on huespedes_cama (marker) with blindness 3 s, nausea, the run posts 'hunt:captured'; count captures. Expose class Hunt: start(Run), stop(Run), active(Run), captures(Run), noise(Run, Vec3, float), and a transform(Run, Vec3 at, float yaw) that spawns her playing the TRANSFORM animation (Act 5 set piece "La Nona se rompe": back turned, bones crack, neck turns 180 over ~3 s, jaw unhinges, she stretches up to ~2.4 blocks, then drops to the spider-crawl and the hunt starts; posts 'hunt:transformed').
2. Her look: the Nona model already exists (tools/models/ent_nona.py → generated client/model/gen/NonaModelBase + client/model/NonaModel.java, texture nona.png; read tools/models/ART_GUIDE.md, rig.py, build_all.py, preview.py). Add a VARIANT 'rota' (VARIANT_MATS): milky white cataract eyes, grey-blue skin, dark veins, blood from mouth/nose/eyes, nightgown dirty; toggle bones hidden by default: unhinged long jaw with dentures, maybe longer finger bones. Add POSES in the module for preview: crawl_spider (bridge backwards, belly up, head upside down facing forward), stand_tall (stretched), neck_twist, listen (head tilted), ceiling_hang. Iterate with preview.py (Read the PNGs, at least 6 cycles), run build_all for nona, and implement the Java animations for NonaRotaEntity in a renderer/model that reuses the Nona geometry (stretch by scaling limb/neck bones and the root, spider crawl by rotating the root 180° on X and posing limbs, walk cycles for both gaits, TRANSFORM timeline). Do NOT change the normal Nona's existing look/poses used by FamilyEntity.
3. HIDING (com.deadline.horror.casa.hunt.HideSpots): right-click a wardrobe door / bed / bathtub / pantry door / chest within 2 blocks of a marker hide_<id>_out (section 11 list) → the player enters: sits on an invisible seat entity at hide_<id> (movement locked, can look around ±70°), exit with sneak. Client overlay by type: wardrobe slats (dark with thin horizontal light slits), under-bed (dark, a low gap of light), bathtub curtain, chest keyhole; heartbeat louder as she gets closer (client sound loop, volume from a synced distance). While hidden the player's noise is halved and she cannot see him unless she searches that spot.
4. HOLD BREATH: keybind (default B, add in DeadLineKeys) → payload; server breath 100 → 0 in 8 s while held; while held the player makes no noise (voice too); at 0 he gasps (big noise spike + sound); releasing refills in 5 s. HUD: a thin lungs bar near the noise meter (client hud).
5. JUMPSCARE OVERLAY: make Fx.jumpscare(p, key) render the creature's head/face filling the screen (3D model rendered close to the camera with violent shake, red flash, 0.6-0.9 s) for keys 'nona_rota', 'lucia', 'copia', 'perro_largo', 'cara_roja' (if a model for a key does not exist yet, fall back to the closest existing one; B3 is building the dog and copies — read client code to see how the existing jumpscare works and extend it). Generate 5 distinct stingers procedurally (tools/audio dsp style, harsh, layered, not cartoonish) + bone-cracking, neck-twist, crawl tapping, sniffing, hiss, gasp, heartbeat loop, and a chase music loop (dissonant strings, pounding low drum, no melody).
Return a concise summary with: files added/changed, the public Hunt/HideSpots API, entity/renderer registrations, sounds added, uncertain API spots (file:line).`

const B3 = `${common}

YOUR PART: B3 — APPARITIONS, THE DOG, THE COPIES (design sections 5 'Apariciones' events 33-45 + 36 perro_mira, 7 characters, 2 Act 3-6 uses).
1. CHORIPAN, the family dog (com.deadline.horror.casa.dog): ChoripanEntity (Java, registered in a new DogEntities.init() wired from DeadLine.java; renderer wired from DeadLineClient). The model module tools/models/ent_choripan.py exists with a generated base (client/model/gen/ChoripanModelBase + choripan.png); read it and its POSES. Java poses needed: SLEEP, SIT, GROWL (at the Nona), WALK, RUN, and the horror one STAND (upright on the hind legs like a person, front legs hanging limp, head slightly tilted, perfectly still, staring) + look variant 'muerto' (VARIANT_MATS: eyes fully black wet, gums bloody, fur matted) — add to the module (render loop with preview.py, at least 5 cycles) and regenerate with build_all. The ChoripanDemonioEntity "perro largo" (tools/models/ent_choripan_demonio.py, base ChoripanDemonioModelBase already generated: a dog whose impossibly long body made of segments with human arms/legs keeps coming out of the doghouse): Java entity + renderer that animates the EMERGE (body keeps unspooling from the doghouse marker 'cucha' for ~6 s), a fast skittering CRAWL chase along a path of markers, and RETRACT; make its eyes less cartoonish (small pinprick pupils, bloodshot) in the module.
2. EVENTS (register all in com.deadline.horror.casa.ApparitionEvents.register() → HorrorEvents.register("casa", ...); one class per event under com.deadline.horror.casa.events): implement catalogue entries 33-45 exactly as described in section 5 (sombra_cruza, nona_fondo, nona_ventana, perro_mira, figura_espejo, detras_hombro, bajo_cama, toti_rincon, copia_sonrie, lucia_techo_corre, ofelia_aparece, sabana, visitante) with the acts/intensity/conditions given there. Use HouseQuery for 'out of view'/'in view' placement, Run markers from section 11 (perro_mira_1..4 for the stalker dog that advances one stage each time it is seen and then lost from view; ventana_1p_afuera; espejo_hall/espejo_bano; toti_rincon; lucia_techo/pasillo_techo; hide beds for bajo_cama...). Apparitions must disappear when the player looks away or approaches (unless the event says otherwise), never be killable, never block doorways for long, and every stop() must despawn what it spawned. Use FamilyEntity for the family figures (Nona normal, Toti, Marta/Jorge copies), PoseidaEntity for Lucía, SombraEntity for the tall shadow/visitor (scale it to ~2.6 blocks for 'visitante'), MunecaEntity for Ofelia; new small entities where needed: a grey hand for bajo_cama, a floating bedsheet with a human shape for sabana, a red face for detras_hombro (or a jumpscare flash via Fx.jumpscare('cara_roja') that B2 renders). Each event plays positional non-verbal sounds you generate procedurally (tools/audio dsp style; register in sounds_def.py block "# --- B3 apparitions").
3. THE COPIES (section 2 Act 5, event copia_sonrie): add a look variant 'copia' to Marta, Jorge and Toti (tools/models/ent_marta.py, ent_jorge.py, ent_toti.py VARIANT_MATS: the SAME face but with a smile far too wide showing all teeth, eyes slightly too far apart and unblinking, greyish skin) — render loop, build_all — and support it in FamilyEntity looks (add LOOK_COPIA = 2 with a small Edit; FamilyRenderers must pick the texture). Lucía (PoseidaEntity / ent_poseida.py): add a CEILING_CRAWL pose (upside down on the ceiling, limbs bent wrong, head turned up to face the floor) with a fast scuttle animation in Java, and a 'normal' look so she can sit at dinner before Act 4 (VARIANT_MATS).
Do NOT edit ent_nona.py / NonaModel (B2 owns the Nona). Return a concise summary with: files added/changed, the event ids registered and the entities/renderers added, sounds added, uncertain API spots (file:line).`

const BUILD = { type: 'object', properties: {
  files: { type: 'array', items: { type: 'string' } }, summary: { type: 'string' }, apis: { type: 'string' },
  uncertain: { type: 'array', items: { type: 'string' } } }, required: ['files', 'summary'] }
const ISSUES = { type: 'object', properties: { issues: { type: 'array', items: { type: 'object', properties: {
  severity: { type: 'string', enum: ['critical', 'major', 'minor'] }, file: { type: 'string' }, problem: { type: 'string' }, fix: { type: 'string' } },
  required: ['severity', 'problem', 'fix'] } } }, required: ['issues'] }

const ITEMS = [ { key: 'b2', brief: B2 }, { key: 'b3', brief: B3 } ]

const review = (it, b, lens) => `${common}

YOU ARE A REVIEWER (${lens === 'code' ? 'COMPILE + RUNTIME lens' : 'HORROR DESIGN + SPEC lens'}). Do NOT edit any file. Another agent just implemented part ${it.key.toUpperCase()} below. Files it reports: ${JSON.stringify(b.files || [])}. Its summary: ${b.summary}
Its uncertain spots: ${JSON.stringify(b.uncertain || [])}
THE BRIEF IT HAD:
${it.brief.slice(common.length)}

${lens === 'code'
  ? `Read every reported file fully (and git diff for the shared files it touched). Hunt, line by line, for anything javac would reject (missing imports, wrong method names/signatures in 1.21.11 Mojang mappings — verify against /tmp/ref/probe/api*.txt, /tmp/ref/mc_imports.txt, /tmp/ref/fabric-api and existing repo usage —, abstract methods not implemented, generics, records, switch exhaustiveness, client classes referenced from main), missing registrations (entity types, renderers, payload types registered on both sides, keybinds, sounds referenced but not generated, lang keys), and runtime bugs (null markers when the site lacks a point, entities never despawned, events whose stop() does not restore, server/client thread misuse, ticking cost). Also run the Python generators it touched to confirm they work.`
  : `Judge against docs/design/casa_terror.md: is it actually SCARY and adult (not goofy), does each event/mechanic match its catalogue entry (acts, intensity, placement out of view / in view, conditions), does it respect "no spoken dialogue", does it fail forward, does it use the section-11 marker names exactly, is anything from the brief missing or stubbed, are model looks/poses convincing (render with tools/models/preview.py and Read the PNGs for every model it changed).`}
Return only real, concrete issues ordered by severity (empty list if none).`

const fix = (it, b, issues) => `${common}

You are finishing part ${it.key.toUpperCase()} implemented by another agent. Files: ${JSON.stringify(b.files || [])}. Summary: ${b.summary}
THE ORIGINAL BRIEF:
${it.brief.slice(common.length)}

Two reviewers found these issues; verify each one against the code and fix every real one (critical and major first, then minor). If an issue is wrong, skip it and say why.
${issues.map((i, n) => `${n + 1}. [${i.severity}] ${i.file || ''} ${i.problem}\n   FIX: ${i.fix}`).join('\n')}

After fixing, re-read every changed file for compile errors once more and rerun the generators you touched. Return the same structured summary (all files of this part, final APIs, remaining uncertain spots).`

const results = await pipeline(ITEMS,
  (it) => agent(it.brief, { label: `build:${it.key}`, phase: 'Build', schema: BUILD }),
  async (b, it) => {
    if (!b) return { key: it.key, failed: 'build' }
    const rs = await parallel(['code', 'design'].map((lens) => () =>
      agent(review(it, b, lens), { label: `review-${lens}:${it.key}`, phase: 'Review', schema: ISSUES })))
    const issues = rs.filter(Boolean).flatMap((r) => r.issues || [])
    log(`${it.key}: ${issues.length} issues (${issues.filter((i) => i.severity !== 'minor').length} critical/major)`)
    return { b, issues }
  },
  async (r, it) => {
    if (!r || r.failed) return r
    if (!r.issues.length) return { key: it.key, build: r.b, fixed: null }
    const f = await agent(fix(it, r.b, r.issues), { label: `fix:${it.key}`, phase: 'Fix', schema: BUILD })
    return { key: it.key, build: r.b, issues: r.issues.length, fixed: f }
  })
return results