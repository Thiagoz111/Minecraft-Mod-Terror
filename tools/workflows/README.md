# Workflow scripts (multi-agent orchestration used to build DEAD LINE)

Run with the Workflow tool (`scriptPath`) passing the JSON `args` the script expects (see each script's top).
`SP` inside the scripts must point at the dev work dir of `tools/workdir.py` (renders land there).
Keep at most 3-5 agents running at once: the session usage limit kills every running agent when it is hit.

- `new_creature.js` / `creature_polish.js` / `casa_characters.js`: model design + art-director critique/refine loops.
- `casa_kits.js`: building-kit design with art-director critique.
- `casa_site.js`: site build + art director + level designer + refine (contains the Casa marker contract).
- `colegio_sounds.js`: voice lines and SFX per group with QA.
- `integrate_animators.js`: Java animators from ANIM_NOTES + adversarial verify.
- `playthrough_review.js`: adversarial full-case playthrough review.
