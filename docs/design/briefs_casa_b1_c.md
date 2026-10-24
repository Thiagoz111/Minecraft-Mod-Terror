# Briefs de agentes: B1 (poltergeist, sangre, celular, lore) y C (set pieces)

Se lanzan como agentes sueltos (esfuerzo extra, máx. 3 a la vez). Cada brief se antepone con el bloque COMÚN.

## COMÚN
Project /home/user/Minecraft-Mod-Terror: Minecraft 1.21.11 Fabric mod "DEAD LINE" (Mojang mappings; Java in
src/main/java (common/server) and src/client/java (client only — never import client classes from main); asset
generators in tools/). Casa Morales is PURE adult HORROR: blood, deformations, earned jumpscares, escalating random
events, no missions, NO spoken dialogue (non-verbal sounds only; the story is told by phone texts). Read
docs/design/ESTADO_CASA.md and docs/design/casa_terror.md COMPLETELY first (binding: sections 2, 5, 6, 7, 8, 11 marker
contract, 12 horror-engine API in src/main/java/com/deadline/horror — use it, do not rewrite it). The act script is
src/main/java/com/deadline/director/casa/CasaScript.java (read it: acts = chapters, set pieces are scripted
HorrorEvents with ids sp_*, run events cena:fin, a_dormir:fin, cuarto61:fin, final:fin). The hunt is
com.deadline.horror.casa.hunt (Hunt.start/stop/active/captures/noise/transform, HideSpots.hidden(p)); apparitions,
the dog and the copies are com.deadline.horror.casa (ApparitionEvents, dog/, events/).
Reusable: casa/CasaProps (BlockDisplay props: lift, settle, levitate, chairTower, remember/swap/restore), casa/KnifeOrbit,
casa/DollShelf, casa/FamilyEntity (poses, walkTo, face, watch, floatTo, looks), director/Run, director/Props, net/Fx,
voice/NoiseMeter, phone/PhoneMessages.
Shared files (DeadLine.java, DeadLineClient.java, registries, FamilyEntity, sounds_def.py, lang.py, build_all.py KEYS)
only with small unique-anchor Edit calls; your sound/lang entries go in a block marked with your id; rerun
tools/audio/gen_defs.py and tools/data/gen_data.py at the end. `export DEADLINE_WORK=<scratchpad>/work`.
NO local Java compiler and no Minecraft jar (CI compiles after the lead pushes): verify every API against existing
repo usages (25k lines of working 1.21.11 code); Fabric API sources via
`curl -s https://raw.githubusercontent.com/FabricMC/fabric-api/1.21.11/<path>`; list unverifiable APIs as uncertain
(file:line). Re-read all your files at the end hunting compile errors. Read-only git; never commit/stash/checkout/reset.
Guard every marker lookup (canRun false if the site lacks it). Every stop() restores the world (except blood and
turned pictures, cleaned in CasaScript.onLeave through a static cleanup you expose). Never scare a hidden player
(HideSpots.hidden). Loud events call Hunt.noise(run, pos, loudness) so the hunter hears them in act 5.

## B1a — POLTERGEIST (eventos 1–32, interactuables, objetos voladores)
1. Events 1–32 of section 5 exactly (acts, intensity, conditions, in-view/out-of-view placement via HouseQuery), one
   class each under com.deadline.horror.casa.events (sound/ and polter/ subpackages ok), registered from
   com.deadline.horror.casa.PoltergeistEvents.register() called once in DeadLine.onInitialize. tres_golpes answers
   back when the player knocks (right-click a wall within 2 blocks during the event). tu_voz: if Voice has a
   recording of the player use it (check voice/), else a whispered non-verbal + knock.
2. Interactables (section 6.3) in com.deadline.horror.casa.Interactables: right-click reactions on the casa kit blocks
   (drawers with random contents: nothing / photo / broken rosary / teeth / letter; fridge light + contents; TV
   on/off/static; radio static/lullaby hum; tap water → blood from act 4; light switch toggles the room group, from act
   4 sometimes ignores you or turns itself back on; rocking chair; music box; landline phone; sewing machine; blinds;
   the breaker panel in the laundry (tablero) brings the lights back for 40-90 s after the blackout). Reuse the
   UseBlockCallback pattern of director/Director (do not break its door/prop handling).
3. FlyingPropEntity (section 6.4) or a Display-based equivalent built on CasaProps: takes a decorative block (chair,
   plate, picture, knife, book), flies with physics (directed throw, gravity, bounce, spin), light damage on hit
   (never lethal), becomes a block again where it lands or breaks (plates: glass particles + shatter sound).
4. Procedural non-verbal sounds needed (tools/audio dsp style): footsteps above, wall knocks, two claps, girl giggle,
   music box lullaby, denture click, close breathing (left/right), backwards prayer murmur, dog scratching a door,
   landline ring + static breath, child crying through a vent, handle rattle, fridge hum, tap gush/blood glug, blinds
   crash, rocking chair accelerating.

## B1b — SANGRE, CELULAR, LORE (eventos 46–54, decals, documentos)
1. Blood decals (section 6.5): thin floor/wall decal blocks or Display entities (splatter, growing pool, hand print,
   bare footprint, drip/streak) + blood writing on the `writes` markers (ELLA ESCUCHA, NO HABLES, LEMAZA, ESTÁ DETRÁS)
   with a hand-written look (decal per letter or TextDisplay dark red); everything tracked per run and cleaned by a
   static BloodDecals.clear(Run) the script calls on leave.
2. Events 46–54 of section 5 (escritura, huellas, pisadas, gotea_techo, banera, diente, msg_marta, msg_desconocido,
   linterna_muere) registered from com.deadline.horror.casa.BloodEvents.register() (msg_marta picks act-appropriate
   texts not yet sent; msg_desconocido "..." typing or the photo espalda_jugador; linterna_muere uses the flashlight
   item/FlashlightLights to kill the beam 4 s with breathing nearby).
3. Lore documents for whoever looks (section 2 Act 3): photos of 1961, the Nona as a girl next to a priest, Lucía's
   notebook ("MI AMIGO SE LLAMA LEMAZA", "LEMAZA DICE QUE LA NONA ES SUYA"), Father Anselmo's letters, broken
   rosaries: readable in-world objects (right-click → a full-screen paper/photo overlay drawn by the client, no voice),
   placed at site markers or kit blocks; textures painted procedurally (tools/art style), text in lang (ES/EN).

## C — SET PIECES (los actos)
Implement every sp_* event CasaScript fires, as scripted HorrorEvents (Kind.SETPIECE, .scripted().once()) registered
from com.deadline.horror.casa.SetPieces.register(): sp_perro_camino (Choripán on two legs in the car headlights, back
turned; headlights flicker; gone — repeat later if not seen), sp_llegada (slow steps, the bolt twice, the door opens by
itself, the Nona at nona_umbral backlit with her walker, stares 4 s, smiles, steps aside with the head following too
far), sp_cena (silent dinner at silla_1..5: Marta looks at you then at her phone, the Nona at the head, Choripán
growling under the table at her; posts cena:fin when the player leaves the dining room after >= 60 s or after 4 min),
sp_a_dormir (the family goes upstairs in silence, Marta points at the guest room door, posts a_dormir:fin when they are
in their rooms), sp_lucia_techo, sp_jorge_sonambulo (knife, walks past without seeing you, stops at the kids' door),
sp_ropero_toti (knocks inside Toti's wardrobe answering yours), sp_nona_reza (the Nona praying backwards with her back
turned in the 1P corridor), sp_nona_se_rompe (kitchen, back turned; Hunt.transform), sp_cuarto61 (the whole family
facing the wall at familia61_1..4, Ofelia on the bed; everyone turns the head 180° at once; blackout; flashlight: the
Nona hanging from the ceiling above you; scream; the P.T. corridor loop on the way up (the PB corridor repeats twice);
posts cuarto61:fin when the front door is reached), sp_final_auto (in the car: start the engine, the rear-view mirror —
the Nona in the back seat; final jumpscare, cut to black, posts final:fin). Pull the family's comedic leftovers out of
FamilyEntity (grill flip, bread throw, knife conduct, shout poses) and unused comedic sounds/props if nothing uses them.
