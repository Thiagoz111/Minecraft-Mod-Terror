export const meta = {
  name: 'colegio-playthrough-review',
  description: 'Find and adversarially verify gameplay-breaking bugs in the Colegio case (chapters 1-9, director, nun AI, voice, HUD)',
  phases: [
    { title: 'Find', detail: 'one reviewer per dimension traces the code paths' },
    { title: 'Verify', detail: 'a skeptic per dimension tries to refute every finding' },
  ],
}

const ROOT = '/home/user/Minecraft-Mod-Terror'
const CTX = `Project: ${ROOT}, a Fabric 1.21.11 (Mojang mappings) horror mod "DEAD LINE". Case 1 "Colegio Santa Inés" is a scripted case run by a
"director": src/main/java/com/deadline/director/ (Run, Exec, Step, Steps, Trigger, Triggers, Beat, Chapter, Script, Director, Props, LineBook,
CaseScript) and src/main/java/com/deadline/director/colegio/ColegioScript.java (chapters 1-9 and all beats). The building is authored in Python:
tools/sites/colegio.py (markers: points, areas, groups, doors, writes) exported to src/main/resources/data/deadline/sites/colegio.json and read by
src/main/java/com/deadline/site/SiteDef.java; placed by SitePlacer. Entities: src/main/java/com/deadline/entity/MonjaEntity.java (Sor Agonía),
ApparitionEntity.java, HauntEntity.java. Voice/noise: src/main/java/com/deadline/voice/ (Voice, NoiseMeter, svc/*). Case lifecycle:
src/main/java/com/deadline/caseload/CaseManager.java, CaseType.java, ActiveCase.java. Client HUD: src/client/java/com/deadline/client/hud/StoryHud.java,
ClientFx.java, net/Fx.java. Lang strings are generated from tools/data/lang.py + tools/audio/lines.py into src/main/resources/assets/deadline/lang/*.json.
The design intent is in docs/design/BIBLIA.md section 2.1 (chapters table e., scare script h., mechanics j., resolution m.).
Recent changes to keep in mind: story doors are locked per chapter via Script.lock + Director UseBlockCallback; Run.lights/light swap kit fixtures
to *_apagado/_apagada via site/Fixtures.java; the nun blows kit candles; double doors open together; the legacy stage>=3 auto-solve was just
disabled for scripted cases (CaseManager); console commands target the first player.
Do NOT edit any file and do NOT run git or gradle (the build happens in CI). You may run python3 to inspect the site (e.g.
python3 -c "import sys; sys.path.insert(0,'tools/sites'); import colegio; s=colegio.build(); print(s.markers['points']['cama8'])").
Report only REAL defects a player or the video creator would hit (soft-lock, beat that can never fire, wrong marker/position after the building-kit
rebuild, crash/NPE, state lost on death/checkpoint/restart, mic-less players stuck, missing lang key shown raw, etc.), each with the exact file:line,
a concrete trigger scenario and a proposed minimal fix. No style nits. Be thorough: trace every beat and every marker name used.`

const DIMS = [
  { key: 'chapters-1-4', prompt: `Trace chapters 1-4 of ColegioScript (arrival, roll call, blackboard, lesson, dinner/prendo_apago/hatch/key/corridor lamps, PA, office: mate, legajo, bakelite phone, chair). For every beat: is its trigger reachable with the CURRENT site (check every point/area/group/door/write name exists in tools/sites/colegio.py and that the geometry makes sense, e.g. areas the player must enter, lookAt targets visible, use:<marker> events fire on the block the player can actually click: Director posts use:<m> for markerAt(pos) or markerAt(pos.above()) where points are mapped by BlockPos.containing(point+0.5 offset)). Does each chapter end (objectives completed, chapter(n+1) called)? Any way to get stuck (doors locked by Script.lock while the script expects the player to pass, etc.)?` },
  { key: 'chapters-5-9', prompt: `Trace chapters 5-9 of ColegioScript (confessional, choir loft, holy water swap/canilla, great silence: lights off, flashlights die, dormitory clouds and the nun's chair approaching, bed 8 diary, bathrooms/mirror, Silence Room, dead hour: tomb/ruler, bells, wall falls, girls run lighting candle islands, back to the sacristy, matins: 7 candles at lecterns, praying 3 phrases, waves, break the ruler, jar; lauds; return home). Same checks as a level designer: markers exist and make geometric sense in the CURRENT tools/sites/colegio.py (e.g. vela_i points sit on the velas_apagadas blocks at z=13 in front of the lecterns, the player can click them; dorm chair group; cripta_muro; coro_velas; espejo; cuarto_silencio door locked for the player; sacristy stairs), objectives complete, chapters advance, nothing soft-locks. Pay special attention to how the script places/moves blocks (chair moving along dorm_silla points, wall removal, candle lighting with Run.light which now LIGHTS unlit authored fixtures) and whether that still matches kit blocks (facing property, multi-block pieces).` },
  { key: 'director-engine', prompt: `Review the director engine for state bugs: Run (beats eligibility/once/repeat, events lifecycle, startChapter replay from checkpoint (flags/actors/execs reset), jump, checkpoint on death via CaseManager.onRespawn, restore after server restart in Director.of, hunters/star, chapter persistence in ActiveCase.stage, locked(), door() double-door partner search, light()/lights() with Fixtures, authored()), Exec/Steps (delay, waitUntil timeouts, loop termination, fork, target() null when the player logs out), Props (spawn/despawn actors, write/chalkWrite TextDisplay placement, faceGroup, reprimand cooldown, swap), Director callbacks (UseBlockCallback returning SUCCESS/FAIL for markers, UseItemCallback). Find crashes (NPE, ConcurrentModification, IndexOutOfBounds), leaks (entities left behind after returnHome/Director.end), and multiplayer issues (2 players in the same case).` },
  { key: 'nun-and-entities', prompt: `Review MonjaEntity (hunting by noise and sight, light avoidance, flashlight burn/sink/reappear, bell teleport behind the player every few minutes, blowCandles with the new Fixtures/blowable, scripted actions ACT_* and the 'scripted' flag that should disable AI during set pieces, attack/reglazo damage, capture to the Silence Room at 15 reprimands), ApparitionEntity and HauntEntity, plus how ColegioScript spawns/despawns them (Props.spawn/actor). Find behaviour that breaks the case: the nun attacking during scripted beats, killing the player in one hit, getting stuck inside kit furniture (custom collision shapes from DecorBlock), teleporting into walls/the sealed mirror room/the crypt behind the brick wall, never despawning, chunk-unload issues at the site origin (sites are placed far away, CaseSites.origin).` },
  { key: 'voice-hud-lang', prompt: `Review the voice/noise mechanics and the HUD/text pipeline. Voice: Voice.java, NoiseMeter, svc backend (optional dependency: everything must work and be completable WITHOUT Simple Voice Chat installed — check every place that waits for voice: roll call 'presente', the confessional, praying the 3 phrases, the Silence Room, the 'shout' corridor rule; each needs a non-mic path), calibration, tagged captures, playback effects. HUD: StoryHud (checklist, subtitles, chapter cards, stamps, bigText, noise meter), Fx payloads, ClientFx handlers. Text: collect every translation key the Java code uses for the colegio (deadline.colegio.*, deadline.speaker.*, line ids passed to say()/sayAsync()/caption(), objective ids, hint ids, stamp reasons, bigText keys like legajo/diario/oracion.1-3) and check each one exists in src/main/resources/assets/deadline/lang/es_ar.json AND en_us.json; also that every line id used in say() has a sound event + entry in lines.json (src/main/resources/data/deadline/lines.json) or degrades gracefully. List missing keys exactly.` },
]

const FIND = { type: 'object', properties: { findings: { type: 'array', items: { type: 'object', properties: {
  title: { type: 'string' }, file: { type: 'string' }, line: { type: 'number' }, severity: { type: 'string', enum: ['blocker', 'major', 'minor'] },
  scenario: { type: 'string' }, fix: { type: 'string' } }, required: ['title', 'file', 'severity', 'scenario', 'fix'] } } }, required: ['findings'] }
const VERD = { type: 'object', properties: { verdicts: { type: 'array', items: { type: 'object', properties: {
  title: { type: 'string' }, real: { type: 'boolean' }, reason: { type: 'string' }, better_fix: { type: 'string' } },
  required: ['title', 'real', 'reason'] } } }, required: ['verdicts'] }

const results = await pipeline(DIMS,
  d => agent(`${CTX}\n\nYOUR DIMENSION: ${d.key}\n${d.prompt}`, { label: `find:${d.key}`, phase: 'Find', schema: FIND }),
  (found, d) => {
    if (!found || !found.findings.length) return { key: d.key, findings: [], verdicts: [] }
    const list = found.findings.map((f, i) => `${i + 1}. [${f.severity}] ${f.title} (${f.file}:${f.line || '?'})\n   scenario: ${f.scenario}\n   fix: ${f.fix}`).join('\n')
    return agent(`${CTX}\n\nYou are a SKEPTICAL senior reviewer. Another reviewer (dimension ${d.key}) claims these defects. For EACH one, read the actual code and
site data and try hard to REFUTE it (is the path really reachable? is it already handled elsewhere? is the line number/marker right?). Mark real=true only if
you can confirm the failure scenario concretely. If real, propose the best minimal fix (better_fix) when the proposed one is wrong or incomplete.
Keep the same titles.\n\n${list}`, { label: `verify:${d.key}`, phase: 'Verify', schema: VERD })
      .then(v => ({ key: d.key, findings: found.findings, verdicts: v ? v.verdicts : [] }))
  })
const out = []
for (const r of results.filter(Boolean)) {
  for (const f of r.findings) {
    const v = (r.verdicts || []).find(x => x.title === f.title)
    out.push({ dim: r.key, ...f, real: v ? v.real : null, reason: v ? v.reason : 'no verdict', better_fix: v ? v.better_fix : '' })
  }
}
log(`${out.length} findings, ${out.filter(f => f.real).length} confirmed`)
return out