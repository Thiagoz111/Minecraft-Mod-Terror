export const meta = {
  name: 'deadline-creature-polish',
  description: 'Critique/refine loop on the existing DEAD LINE creature drafts until they ship (max 3 rounds each)',
  phases: [
    { title: 'Critique', detail: 'brutal art-director review of renders' },
    { title: 'Refine', detail: 'fix every critical/major issue, re-render' },
  ],
}

const ENTITIES = args.entities
const MAX = args.rounds || 3
const ROOT = '/home/user/Minecraft-Mod-Terror'
const SP = '/tmp/claude-0/-home-user-Minecraft-Mod-Terror/f464a6ad-b203-50f8-a993-93d7fecfc5d1/scratchpad'

const BUILD_SCHEMA = {
  type: 'object',
  properties: {
    key: { type: 'string' }, file: { type: 'string' }, cubes: { type: 'number' },
    bones: { type: 'array', items: { type: 'string' } }, poses: { type: 'array', items: { type: 'string' } },
    height_blocks: { type: 'number' }, render_type: { type: 'string' },
    notes: { type: 'string' },
  },
  required: ['key', 'file', 'cubes', 'bones', 'notes'],
}
const CRIT_SCHEMA = {
  type: 'object',
  properties: {
    scary: { type: 'number' }, professional: { type: 'number' }, silhouette: { type: 'number' }, face: { type: 'number' },
    verdict: { type: 'string', enum: ['ship', 'revise'] },
    issues: { type: 'array', items: { type: 'object', properties: {
      severity: { type: 'string', enum: ['critical', 'major', 'minor'] }, problem: { type: 'string' }, fix: { type: 'string' } },
      required: ['severity', 'problem', 'fix'] } },
  },
  required: ['scary', 'professional', 'silhouette', 'face', 'verdict', 'issues'],
}

const common = (e) => `Project root: ${ROOT}. Horror mod "DEAD LINE" (Minecraft 1.21.11), made for viral YouTube/TikTok clips.
First read ${ROOT}/tools/models/ART_GUIDE.md completely (quality bar, coordinates, 2x density with model.scale = 0.5, module contract, preview loop) and skim rig.py, mcmodel.py, paint.py.
The owner rejected the first versions as amateur ("flacos, sin cara, no dan miedo, deben ser deformes, con forma característica, realmente profesionales").
Extra technical rules for the Java export: bone names unique and not Java keywords; emissive decal layer named exactly 'eyes'; the FOCUS bone close-up is also the in-game JUMPSCARE portrait (frontal, very close), so the face must be devastating from the front; ANIM_NOTES must describe every bone's role; standard pose names 'attack' and 'scream' where they apply, plus creature-specific ones. The model must stand centred on the entity origin (x≈0, z≈0) so it fits its hitbox; it must touch the ground at y=24 unless it floats by design.

CREATURE: ${e.name} (module tools/models/ent_${e.key}.py)
ART DIRECTION:
${e.brief}
Target height: ${e.height} blocks. Hitbox: ${e.hitbox}.`

const critique = (e, round) => `${common(e)}

YOU ARE THE CRITIC (round ${round}). A brutally honest art director at a top horror studio AND a horror-YouTube viewer who knows every Minecraft horror mod (Cave Dweller, Man From The Fog, Goatman, The Mimicer, Alex's Mobs, Mutant Monsters). Do NOT edit files.
Run \`cd ${ROOT} && python3 tools/models/preview.py ${e.key}\` and every pose in POSES (\`--pose <name>\`); Read ${SP}/models/${e.key}/views*.png and texture.png; read the source.
If the module does not run (it may have been left mid-edit by an interrupted designer), report that as a critical issue with the traceback.
Judge silhouette, face (frontal close-up = jumpscare), anatomy vs brief, geometric depth, hand-crafted texture quality (no noise mush), readability in the dark cell, rig/poses, technical errors (wrong-side faces, z-fighting, gaps, floating cubes, off-centre model), and the extra rules.
Score 1-10 (scary, professional, silhouette, face). verdict 'ship' only if every score >= 8 and no critical/major issue remains. Concrete, actionable issues ordered by severity.`

const refine = (e, crit, round) => `${common(e)}

A critic reviewed tools/models/ent_${e.key}.py (round ${round}). Scores: scary ${crit.scary}, professional ${crit.professional}, silhouette ${crit.silhouette}, face ${crit.face}. Issues:
${crit.issues.map((i, n) => `${n + 1}. [${i.severity}] ${i.problem}\n   FIX: ${i.fix}`).join('\n')}

Improve the creature until every critical and major issue is solved, then the minor ones. Restructure geometry or repaint textures as much as needed. If the module is broken (left mid-edit), first make it run again.
Loop: edit -> \`cd ${ROOT} && python3 tools/models/preview.py ${e.key}\` (+ each --pose) -> Read ${SP}/models/${e.key}/views*.png and texture.png -> judge -> repeat (at least 5 render cycles). Only edit ent_${e.key}.py (and optional ent_${e.key}_*.py helpers); never run git; never edit shared framework files. Keep within 220 cubes / 60 bones / 256x256.
Return the structured summary.`

const results = await pipeline(ENTITIES, async (e) => {
  const history = []
  let last = null
  for (let round = 1; round <= MAX; round++) {
    const c = await agent(critique(e, round), { label: `critic${round}:${e.key}`, phase: 'Critique', schema: CRIT_SCHEMA })
    if (!c) break
    last = c
    history.push({ round, scary: c.scary, professional: c.professional, silhouette: c.silhouette, face: c.face, verdict: c.verdict })
    const blocking = c.issues.filter((i) => i.severity !== 'minor')
    if (c.verdict === 'ship' && blocking.length === 0) return { key: e.key, shipped: true, history }
    const r = await agent(refine(e, c, round), { label: `refine${round}:${e.key}`, phase: 'Refine', schema: BUILD_SCHEMA })
    if (!r) break
    log(`${e.key}: round ${round} refined (${r.cubes} cubes)`)
  }
  return { key: e.key, shipped: false, history, remaining: last ? last.issues.filter((i) => i.severity !== 'minor').map((i) => i.problem) : null }
})
return results