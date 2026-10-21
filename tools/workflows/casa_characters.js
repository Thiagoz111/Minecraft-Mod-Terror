export const meta = {
  name: 'deadline-casa-characters',
  description: 'Casa Morales characters: design the family (Marta, Jorge, Nona, Toti) and update Choripan, the demon dog, Ofelia and Lucia, with art-director critique loops',
  phases: [
    { title: 'Build', detail: 'design new humans / update existing modules with the casa brief' },
    { title: 'Critique', detail: 'art-director review' },
    { title: 'Refine', detail: 'fix issues' },
  ],
}

const ENTITIES = args.entities
const ROOT = '/home/user/Minecraft-Mod-Terror'
const SP = '/tmp/claude-0/-home-user-Minecraft-Mod-Terror/f464a6ad-b203-50f8-a993-93d7fecfc5d1/scratchpad'

const BUILD_SCHEMA = { type: 'object', properties: {
  key: { type: 'string' }, file: { type: 'string' }, cubes: { type: 'number' }, bones: { type: 'array', items: { type: 'string' } },
  poses: { type: 'array', items: { type: 'string' } }, variants: { type: 'array', items: { type: 'string' } }, notes: { type: 'string' } },
  required: ['key', 'file', 'cubes', 'bones', 'notes'] }
const CRIT_SCHEMA = { type: 'object', properties: {
  appeal: { type: 'number' }, professional: { type: 'number' }, silhouette: { type: 'number' }, face: { type: 'number' },
  verdict: { type: 'string', enum: ['ship', 'revise'] },
  issues: { type: 'array', items: { type: 'object', properties: { severity: { type: 'string', enum: ['critical', 'major', 'minor'] },
    problem: { type: 'string' }, fix: { type: 'string' } }, required: ['severity', 'problem', 'fix'] } } },
  required: ['appeal', 'professional', 'silhouette', 'face', 'verdict', 'issues'] }

const common = (e) => `Project root: ${ROOT}. Horror-comedy mod "DEAD LINE" (Minecraft 1.21.11) for a 20-minute YouTube video by an Argentine creator. Quality bar: better than any existing Minecraft mod; the owner rejects anything amateur ("realmente profesionales").
First read ${ROOT}/tools/models/ART_GUIDE.md completely (2x texel density with model.scale = 0.5, coordinates: +Y down, ground y=24, faces -Z, module contract DEFAULT_MAT/FOCUS/POSES/ANIM_NOTES/build(), preview loop) and look at rig.py, mcmodel.py, paint.py, emat.py. Finished reference modules: ${ROOT}/tools/models/ent_alumna.py, ent_madre.py, ent_monja.py, ent_muneca.py.
Export rules: unique bone names, not Java keywords; emissive decal layer named exactly 'eyes'; ANIM_NOTES must document every bone's role, every pose and every toggle; model centred on the entity origin (x≈0, z≈0) and standing on y=24; within ${e.budget || '220 cubes / 60 bones / 256x256 texture'}.
VARIANTS CONTRACT (only if this character has looks that change): the module may export VARIANT_MATS = {'name': material, ...} (ordered; index 0 is DEFAULT_MAT's look) - each is painted to its own texture <key>_<name>.png and Java picks it by the entity's variant index; geometry that only exists in one look (dentures, a wide smile plane, a burned patch, sewn thread...) is a separate bone hidden by default and listed in ANIM_NOTES under "Toggles" with the variant that shows it. Shared human bone names: body, neck, head, jaw, right_arm/right_forearm/right_hand, left_arm/left_forearm/left_hand, right_leg/left_leg (+ shins/feet as needed).
The design document is ${ROOT}/docs/design/BIBLIA.md, section 2.2 CASO 2 'Casa Morales' (read b. Historia/Elenco, g. Entidades y pedidos de arte, h. Guion de sustos for how this character is staged).

CHARACTER: ${e.name} (module tools/models/ent_${e.key}.py)
ROLE: ${e.role}
ART BRIEF:
${e.brief}`

const loop = (e) => `Loop: \`cd ${ROOT} && python3 tools/models/preview.py ${e.key}\` (+ \`--pose <name>\` for every pose) -> Read ${SP}/models/${e.key}/views*.png and texture.png after EVERY change -> judge honestly -> fix.
Only edit ent_${e.key}.py (and optional ent_${e.key}_*.py helpers). Never run git. Never edit shared framework files or other modules. Return the structured summary.`

const build = (e) => e.resume
  ? `${common(e)}

A previous designer was interrupted mid-work: ${ROOT}/tools/models/ent_${e.key}.py exists but may be incomplete or broken. Read it, make it run, render it, keep what is good and finish the design to the full brief. At least 8 render cycles.
${loop(e)}`
  : e.existing
  ? `${common(e)}

The module ALREADY EXISTS and was polished before: keep its quality and identity. Read it fully, render it, then implement every addition in the brief (new poses, toggles, variants, details), and fix anything that is broken. At least 6 render cycles.
${loop(e)}`
  : `${common(e)}

Create ${ROOT}/tools/models/ent_${e.key}.py from scratch. Sketch the design first (silhouette, proportions, bones, palette ramps, face detail, how the comedy and the horror read), then build. At least 8 render cycles.
${loop(e)}`

const critique = (e, round) => `${common(e)}

YOU ARE THE CRITIC (round ${round}): a brutally honest art director at a top studio and a horror/comedy YouTube viewer who knows every popular Minecraft mod. Do NOT edit files.
Run \`cd ${ROOT} && python3 tools/models/preview.py ${e.key}\` and every pose in POSES; Read ${SP}/models/${e.key}/views*.png and texture.png; read the source.
If the module does not run, report that as a critical issue with the traceback.
Judge against the brief (the intended mix of funny and scary, instantly readable character from 10 blocks away in a video), silhouette, face close-up, geometric depth, hand-crafted pixel-art texture (no noise mush), readability at night, rig and poses, variants/toggles, technical errors (wrong-side faces, z-fighting, gaps, floating parts, off-centre model), export rules.
Score 1-10 (appeal, professional, silhouette, face). verdict 'ship' only if every score >= 8 and no critical/major issue remains. Concrete, actionable issues ordered by severity.`

const refine = (e, c, round) => `${common(e)}

A critic reviewed tools/models/ent_${e.key}.py (round ${round}). Scores: appeal ${c.appeal}, professional ${c.professional}, silhouette ${c.silhouette}, face ${c.face}. Issues:
${c.issues.map((i, n) => `${n + 1}. [${i.severity}] ${i.problem}\n   FIX: ${i.fix}`).join('\n')}

Fix every critical and major issue, then the minor ones; restructure geometry or repaint as much as needed. If the module is broken, first make it run again. At least 5 render cycles.
${loop(e)}`

const results = await pipeline(ENTITIES, async (e) => {
  const b = await agent(build(e), { label: `build:${e.key}`, phase: 'Build', schema: BUILD_SCHEMA })
  if (!b) return { key: e.key, failed: true }
  const history = []
  for (let round = 1; round <= (e.rounds || 2); round++) {
    const c = await agent(critique(e, round), { label: `critic${round}:${e.key}`, phase: 'Critique', schema: CRIT_SCHEMA })
    if (!c) break
    history.push({ round, appeal: c.appeal, professional: c.professional, silhouette: c.silhouette, face: c.face, verdict: c.verdict })
    if (c.verdict === 'ship' && !c.issues.some((i) => i.severity !== 'minor')) return { key: e.key, shipped: true, history }
    const r = await agent(refine(e, c, round), { label: `refine${round}:${e.key}`, phase: 'Refine', schema: BUILD_SCHEMA })
    if (!r) break
  }
  return { key: e.key, shipped: false, history }
})
return results
