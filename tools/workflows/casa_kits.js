export const meta = {
  name: 'deadline-build-kits-casa-2',
  description: 'Design the Casa Morales building kits (structure + furniture) with art-director critique loops',
  phases: [
    { title: 'Build', detail: 'one set designer per kit: blocks, furniture, room mock-ups' },
    { title: 'Critique', detail: 'art director reviews showroom + room renders' },
    { title: 'Refine', detail: 'designer fixes issues' },
  ],
}

const ROOT = '/home/user/Minecraft-Mod-Terror'
const SP = '/tmp/claude-0/-home-user-Minecraft-Mod-Terror/f464a6ad-b203-50f8-a993-93d7fecfc5d1/scratchpad'
const KITS = args.kits
const MAX = args.rounds || 2

const SUM = { type: 'object', properties: {
  kit: { type: 'string' }, module: { type: 'string' }, blocks: { type: 'array', items: { type: 'string' } },
  scenes: { type: 'array', items: { type: 'string' } }, notes: { type: 'string' } }, required: ['kit', 'module', 'blocks', 'notes'] }
const CRIT = { type: 'object', properties: {
  realism: { type: 'number' }, craft: { type: 'number' }, atmosphere: { type: 'number' }, completeness: { type: 'number' },
  verdict: { type: 'string', enum: ['ship', 'revise'] },
  issues: { type: 'array', items: { type: 'object', properties: { severity: { type: 'string', enum: ['critical', 'major', 'minor'] },
    problem: { type: 'string' }, fix: { type: 'string' } }, required: ['severity', 'problem', 'fix'] } } },
  required: ['realism', 'craft', 'atmosphere', 'completeness', 'verdict', 'issues'] }

const common = (k) => `Project root: ${ROOT}. Horror-comedy Minecraft 1.21.11 mod "DEAD LINE" for a 20-minute YouTube video (Argentine creator).
The owner decided the locations must NOT use vanilla Minecraft blocks: we design every wall, floor, door, window and piece of furniture
ourselves, at 32 px per block, so it "looks better" than anything in Minecraft.
READ FIRST: ${ROOT}/tools/blocks/BLOCK_GUIDE.md (rules, workflow, quality bar) and ${ROOT}/tools/blocks/bkit.py (framework API, coordinates,
face orientation). The finished Colegio kits are the quality bar and the best code reference: ${ROOT}/tools/blocks/kit_colegio_estructura.py and kit_colegio_muebles.py (helpers: palettes, wood/cloth/brass tones, Canvas pictures, draw_text fonts, multi-block pieces, mirror_parts) — copy what you need into your own module (do not import from them; key prefixes must stay yours), and see tools/blocks/scenes/colegio_*.py for room mock-ups. Furniture facing convention used on site: the front of a piece faces 'facing'; wall pieces sit against the wall opposite to 'facing'; multi-block pieces are named _izq/_der (document which side is which in a docstring).
Location design (story, rooms, props, clue placements, mood): ${ROOT}/docs/design/${k.doc} — read the location/layout sections and the scare
script so every prop the story needs exists.

YOUR KIT: "${k.kit}" -> module ${ROOT}/tools/blocks/kit_${k.kit}.py, every block with kit='${k.kit}' and key prefix '${k.prefix}'.
SCOPE:
${k.scope}

Commands (run from ${ROOT}): \`python3 tools/blocks/build_blocks.py ${k.kit}\`, \`python3 tools/blocks/brender.py showroom ${k.kit}\`,
\`python3 tools/blocks/brender.py scene tools/blocks/scenes/${k.kit}_<room>.py\`. Renders land in ${SP}/blocks/. Read them with the Read tool.
Only create/edit kit_${k.kit}.py and tools/blocks/scenes/${k.kit}_*.py. Never edit bkit.py, build_blocks.py, brender.py, other kits, Java code;
never run \`build_blocks.py --all\`; never run git.`

const build = (k) => `${common(k)}

IMPORTANT: an earlier run was interrupted. ${ROOT}/tools/blocks/kit_${k.kit}.py already exists (thousands of lines) and so may some
scenes in tools/blocks/scenes/. Do NOT start over: read the module, build and render it first, keep what is good, fix what is weak,
and complete everything in SCOPE that is still missing.
Design and build the whole kit. Plan the full block list first (aim for completeness: everything the rooms need), define consistent palettes,
then implement in batches. After each batch: build, render the showroom, and render 2-4 room mock-up scenes that combine your blocks into
real rooms from the design doc (by day and night with flashlight). Judge honestly: does it read as a real place? Is it crafted pixel art?
Is it creepy at night? Fix and iterate many times (at least 8 render cycles). Return the summary (block keys, scenes, notes).`

const critique = (k, round) => `${common(k)}

YOU ARE THE ART DIRECTOR (round ${round}) of a top studio, judging this kit for a horror video. Do NOT edit files.
Build and render: \`python3 tools/blocks/build_blocks.py ${k.kit}\`, showroom, and every scene in tools/blocks/scenes/${k.kit}_*.py; Read the PNGs and the source.
Judge: realism and proportions (believable rooms at player scale), pixel-art craftsmanship (no noise mush, crisp edges, wear and story
details), atmosphere (creepy at night under the flashlight, colour mood), completeness vs the design doc (missing rooms/props/clues),
tiling/repetition, technical errors (z-fighting, gaps, wrong-facing, transparent holes, bad collision splits).
Scores 1-10 (realism, craft, atmosphere, completeness). verdict 'ship' only if all >= 8 and no critical/major issue. Concrete fixes by severity.`

const refine = (k, c, round) => `${common(k)}

The art director reviewed your kit (round ${round}): realism ${c.realism}, craft ${c.craft}, atmosphere ${c.atmosphere}, completeness ${c.completeness}.
${c.issues.map((i, n) => `${n + 1}. [${i.severity}] ${i.problem}\n   FIX: ${i.fix}`).join('\n')}
Fix every critical and major issue, then minor ones. Iterate with builds and renders (at least 5 cycles). Return the summary.`

const results = await pipeline(KITS, async (k) => {
  const b = await agent(build(k), { label: `build:${k.kit}`, phase: 'Build', schema: SUM })
  if (!b) return { kit: k.kit, failed: true }
  const hist = []
  for (let r = 1; r <= MAX; r++) {
    const c = await agent(critique(k, r), { label: `critic${r}:${k.kit}`, phase: 'Critique', schema: CRIT })
    if (!c) break
    hist.push({ r, realism: c.realism, craft: c.craft, atmosphere: c.atmosphere, completeness: c.completeness, verdict: c.verdict })
    if (c.verdict === 'ship' && !c.issues.some((i) => i.severity !== 'minor')) return { kit: k.kit, shipped: true, hist, blocks: b.blocks }
    const f = await agent(refine(k, c, r), { label: `refine${r}:${k.kit}`, phase: 'Refine', schema: SUM })
    if (!f) break
  }
  return { kit: k.kit, shipped: false, hist }
})
return results