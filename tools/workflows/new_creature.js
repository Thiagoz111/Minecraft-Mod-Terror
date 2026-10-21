export const meta = {
  name: 'deadline-new-creature',
  description: 'Design new DEAD LINE creatures from art briefs, then critique/refine loop until they ship',
  phases: [
    { title: 'Design', detail: 'builder per creature with 3D render loop' },
    { title: 'Critique', detail: 'art-director review' },
    { title: 'Refine', detail: 'fix issues' },
  ],
}

const ENTITIES = args.entities
const MAX = args.rounds || 2
const ROOT = '/home/user/Minecraft-Mod-Terror'
const SP = '/tmp/claude-0/-home-user-Minecraft-Mod-Terror/f464a6ad-b203-50f8-a993-93d7fecfc5d1/scratchpad'

const BUILD_SCHEMA = { type: 'object', properties: {
  key: { type: 'string' }, file: { type: 'string' }, cubes: { type: 'number' }, bones: { type: 'array', items: { type: 'string' } },
  poses: { type: 'array', items: { type: 'string' } }, notes: { type: 'string' } }, required: ['key', 'file', 'cubes', 'bones', 'notes'] }
const CRIT_SCHEMA = { type: 'object', properties: {
  scary: { type: 'number' }, professional: { type: 'number' }, silhouette: { type: 'number' }, face: { type: 'number' },
  verdict: { type: 'string', enum: ['ship', 'revise'] },
  issues: { type: 'array', items: { type: 'object', properties: { severity: { type: 'string', enum: ['critical', 'major', 'minor'] },
    problem: { type: 'string' }, fix: { type: 'string' } }, required: ['severity', 'problem', 'fix'] } } },
  required: ['scary', 'professional', 'silhouette', 'face', 'verdict', 'issues'] }

const common = (e) => `Project root: ${ROOT}. Horror-comedy mod "DEAD LINE" (Minecraft 1.21.11) for a 20-minute YouTube video by an Argentine creator. Quality bar: better than any existing Minecraft mod.
First read ${ROOT}/tools/models/ART_GUIDE.md completely (2x texel density with model.scale = 0.5, coordinates: +Y down, ground y=24, faces -Z, module contract DEFAULT_MAT/FOCUS/POSES/ANIM_NOTES/build(), preview loop) and look at rig.py, mcmodel.py, paint.py, emat.py. Study a finished reference module for API usage, e.g. ${ROOT}/tools/models/ent_muneca.py or ent_monja.py.
Export rules: unique bone names, not Java keywords; emissive decal layer named exactly 'eyes'; ANIM_NOTES must document every bone's role and how it animates; model centred on the entity origin (x≈0, z≈0) and standing on y=24; within ${e.budget || '220 cubes / 60 bones / 256x256 texture'}.
The design document for this creature's case is ${ROOT}/docs/design/${e.doc} (read the relevant section for context).

CREATURE: ${e.name} (module tools/models/ent_${e.key}.py)
ROLE: ${e.role}
ART BRIEF:
${e.brief}`

const design = (e) => `${common(e)}

Create ${ROOT}/tools/models/ent_${e.key}.py from scratch. Sketch the design first (silhouette, proportions, bones, palette ramps, face detail), then build.
Loop: \`cd ${ROOT} && python3 tools/models/preview.py ${e.key}\` (+ \`--pose <name>\` for every pose) -> Read ${SP}/models/${e.key}/views*.png and texture.png after EVERY change -> judge honestly -> fix. At least 8 render cycles.
Only edit ent_${e.key}.py (and optional ent_${e.key}_*.py helpers). Never run git. Never edit shared framework files. Return the summary.`

const critique = (e, round) => `${common(e)}

YOU ARE THE CRITIC (round ${round}): a brutally honest art director at a top studio and a horror/comedy YouTube viewer who knows every popular Minecraft mod. Do NOT edit files.
Run \`cd ${ROOT} && python3 tools/models/preview.py ${e.key}\` and every pose in POSES; Read ${SP}/models/${e.key}/views*.png and texture.png; read the source.
Judge against the brief (including the intended mix of cute/funny and scary where the brief asks for it), silhouette, face close-up (jumpscare/bestiary portrait), geometric depth, hand-crafted pixel-art texture (no noise mush), readability at night, rig and poses, technical errors (wrong-side faces, z-fighting, gaps, floating parts, off-centre model), export rules.
Scores 1-10 (scary = "effect": scary for monsters, charming for the cute form; professional; silhouette; face). verdict 'ship' only if every score >= 8 and no critical/major issue. Concrete fixes ordered by severity.`

const refine = (e, c, round) => `${common(e)}

A critic reviewed tools/models/ent_${e.key}.py (round ${round}). Scores: effect ${c.scary}, professional ${c.professional}, silhouette ${c.silhouette}, face ${c.face}. Issues:
${c.issues.map((i, n) => `${n + 1}. [${i.severity}] ${i.problem}\n   FIX: ${i.fix}`).join('\n')}

Fix every critical and major issue, then the minor ones; restructure as needed. Loop edit -> preview (+ poses) -> Read renders -> judge (at least 5 cycles). Only edit ent_${e.key}.py (+ helpers); never git; never shared files. Return the summary.`

const results = await pipeline(ENTITIES, async (e) => {
  const d = await agent(design(e), { label: `design:${e.key}`, phase: 'Design', schema: BUILD_SCHEMA })
  if (!d) return { key: e.key, failed: true }
  const history = []
  for (let round = 1; round <= MAX; round++) {
    const c = await agent(critique(e, round), { label: `critic${round}:${e.key}`, phase: 'Critique', schema: CRIT_SCHEMA })
    if (!c) break
    history.push({ round, effect: c.scary, professional: c.professional, silhouette: c.silhouette, face: c.face, verdict: c.verdict })
    if (c.verdict === 'ship' && !c.issues.some((i) => i.severity !== 'minor')) return { key: e.key, shipped: true, history }
    const r = await agent(refine(e, c, round), { label: `refine${round}:${e.key}`, phase: 'Refine', schema: BUILD_SCHEMA })
    if (!r) break
  }
  return { key: e.key, shipped: false, history }
})
return results