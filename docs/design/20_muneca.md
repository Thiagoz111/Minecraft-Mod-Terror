# DEAD LINE — Caso 2: LA MUÑECA
## "Casa Morales — Las Glicinas 1961"

> Design bible for the haunted-family case. In-game text is in Spanish (rioplatense voseo); notes are in English.
> I built it from what's already in the repo: `MoralesHouseSite` (house), `MunecaEntity` (weeping-angel doll), `PoseidaEntity` (Lucía: spider-walk, 180° head turn, levitation, exorcism bar), the `CURSED_DOLL` anchor, sanity, poltergeist-friendly FX (`Fx`, camera shake, jumpscare portraits), and the existing lang keys (Marta, Jorge, Lucía, Padre Ignacio). Wherever it can, the design reuses those pieces.

---

## 1. Logline + backstory

**Logline.** A dachshund dug up a cookie tin. Inside was a porcelain doll with its mouth sewn shut. A little girl cut the thread. Now something called **El Inquilino** is moving through the Morales family one body at a time: the dog, the dad, the girl. When you finally corner it, the person waiting for it is the one you least expected: the grandma who has been offering you mate all night.

**The twist.** The grandma isn't the villain. She is the original victim, from 1961, and in the last act she invites the demon back into herself to save her granddaughter: *"Vení conmigo, como antes. Dejala a la nena."* The final boss is a 73-year-old woman floating in her rocking chair. You save her, and she sews the doll's mouth shut herself.

### Timeline (the player pieces this together from clues)

| Fecha | Qué pasó |
|---|---|
| **1958** | The Bertolotti family buys the chalet at Las Glicinas 1961, Temperley (southern conurbano). For her 5th birthday, **Nélida Bertolotti** gets a French-style porcelain doll from the downtown store "La Parisina". She names it **Clarita**. |
| **Winter 1961** | Nélida, now 8, starts speaking backwards, writing "LEMAZA" on the walls and laughing in the basement. Her father says "hay alguien viviendo en la casa". The neighbours call it **"el inquilino"** because it "never pays and never leaves". |
| **11–14 Aug 1961** | **Padre Anselmo Ruiz** (fictional parish Nuestra Señora del Carmen) spends four nights performing an exorcism in the basement and records it on a reel tape recorder. He can't cast the demon out, so he **binds it into Clarita**: he sews the doll's mouth shut with blessed red thread, packs it with coarse salt in a Danish-style **butter cookie tin** and buries it under the lemon tree he plants in the backyard. Note in the tin: *"NUNCA LA DESENTIERREN. NUNCA LE CORTEN EL HILO."* |
| **17 Aug 1961** | Anselmo dies of "heart failure" at 41. The local paper: *"NIÑA DE TEMPERLEY 'HABLÓ EN LATÍN' — MUERE EL SACERDOTE QUE LA ATENDIÓ."* |
| **1961–2026** | Nélida grows up, marries Morales, has Jorge, buries the memory. She knits **red wool** compulsively for 65 years and dresses everyone in red sweaters "por las dudas". Nobody knows why. Jorge inherits the house. |
| **Sep 2026** | **Choripán**, the family dachshund (bred to dig), digs up the tin under the lemon tree and chews the doll's left arm off. **Lucía (8)** finds Clarita. She hears it "talking through the thread" and cuts the stitches with her mom's scissors on **29 Sep**. |
| **Oct 2026** | Poltergeist activity escalates: plates, chairs, the TV, lights. Choripán won't stop staring at the stairs. Jorge "went out to buy charcoal" two hours ago. |
| **20 Oct 2026, 03:07** | The phone rings. *(Tonight's date, so it feels live on camera.)* |

**The demon.** True name **AZAMEL**. Nickname **El Inquilino**. It wants "volver a casa", meaning back to its first host, Nélida. Each host it takes is a step up the chain toward her. It can't be killed, only **sealed back into Clarita** by re-sewing the mouth while the host is exorcised and its name is spoken.

**The rule the audience learns:** *Where Clarita is sitting, that's who's next.* The doll relocates at each stage and always sits next to the next victim. A tense, readable rule for viewers ("¡LA MUÑECA ESTÁ EN LA CUCHA!").

### Cast

| Personaje | Edad | Rol | Voz (TTS) |
|---|---|---|---|
| **Marta Morales** | 42 | Mom, the caller and your guide. Hair curlers, robe, slippers. Nervous and talkative. She **never gets possessed** and is the comic anchor. | ef_dora |
| **Jorge Morales** | 46 | Dad, "rey del asado". Went out for charcoal and comes back at the worst possible moment. Host #2. | em_alex (+em_santa doubled when possessed) |
| **Lucía Morales** | 8 | Cut the thread. Talks to Clarita. Host #3 (reuses Poseída). | ef_dora pitched up |
| **Tobías "Toti" Morales** | 15 | Shut in his wardrobe with headphones playing ranked online all night. Notices nothing. Running gag. | em_alex pitched up |
| **Nélida "la Nona" Bertolotti de Morales** | 73 | Grandma, knits red, offers mate. 1961 victim. Final host and the twist. | ef_dora slowed/aged |
| **Choripán** | 6 | Dachshund in a red knitted sweater (by the Nona). Host #1, **transforms**. | synth barks |
| **Clarita** | 1958 | Doll, anchor, the demon's jail. | giggle / voice-mimic |
| **Don Ramón** | ? | Garden gnome. Always facing you. Running gag. | ceramic scrape |
| **Doña Chela** | ? | Nosy neighbour, phone calls only. | ef_dora older |

---

## 2. The phone call + objective flow

### Caller variants (`deadline.case.casa.caller.N` / `msg.N`)

**0 — Marta Morales**
> "Hola... ¿es la línea de los exorcistas? Perdón la hora. Es mi perro... Choripán... camina por el techo. No, no, el perro no. Mi hija. Bueno... los dos, no sé. Y mi marido fue a comprar carbón hace dos horas y no vuelve. Las Glicinas 1961, Temperley. Por favor, vení rápido."

**1 — Nona Nélida**
> "Buenas noches, joven. Necesito que venga a terminar algo que empezó un cura en 1961. Traiga hilo rojo. Y no le haga caso a la muñeca, que miente."

**2 — "Lucía"** (it's the demon; the last word comes out in a deep doubled voice)
> "Hola. Soy Lucía. Clarita quiere conocerte. Choripán también. Vení con hambre... *CON HAMBRE.*"

**3 — Doña Chela (vecina)**
> "Mirá, querido, yo no me meto en nada. Pero en lo de Morales vuelan los platos, y no es una pelea, eh, que eso ya lo conozco. El salchicha aúlla en otro idioma. Yo te aviso y me voy a dormir."

### Objective flow (new per-case stage script; the HUD objective line + phone "Caso activo" app)

| # | Etapa | Objetivo en pantalla | Pista (phone) | Exit condition |
|---|---|---|---|---|
| 0 | **Llegada** | "Hablá con Marta." | "La señora está en la puerta, en ruleros." | Talk to Marta at the porch. |
| 1 | **La casa** | "Reuní 3 evidencias de actividad paranormal." | "Probá el EMF cerca de las muñecas. Preguntale algo a la Spirit Box." | 3 of: EMF 5, Spirit Box answer, spirit photo, UV prints, family chat, tape. |
| 2 | **Choripán** | "Algo le pasa a Choripán. Calmalo sin lastimarlo." | "¿Qué es lo único que un perro no puede rechazar?" | Blessed choripán eaten. |
| 3 | **El rey del asado** | "Liberá a Jorge." | "El crucifijo lo frena. El flash le muestra lo que lleva encima." | Jorge's possession bar to 0. |
| 4 | **Lucía** | "Exorcizá a Lucía. No pierdas de vista a las muñecas." | "No podés mirar a las dos cosas a la vez. Usá sal." | Ritual book exorcism complete. |
| 5 | **La Nona** | "Encontrá el nombre del Inquilino y bajá al sótano." | "La Nona tiene una lata de galletitas. Nunca tiene galletitas." | Get Hilo Bendito + know the name; enter the cuarto del 61. |
| 6 | **Coser la boca** | "Purificá a Clarita y cosele la boca. 3 puntadas." | "Agua bendita, flash, aguja." | 3 stitches + exorcism on Nélida. |
| 7 | **Resuelto** | "Encerrá a Clarita en el Frasco de Almas. Desayuná." | — | Jar the doll, talk to the family, return home. |

Implementation note: generalise `ActiveCase.stage` into a per-case `CaseScript` (a list of stages with enter/tick/exit hooks) so stages 2–6 can each be their own small class. Stage 7 maps to the existing "solved" (stage ≥ 3) logic.

---

## 3. The location: Casa Morales, Las Glicinas 1961

**Style:** a 1950s Buenos Aires suburban chalet. Pale brick and white render, pitched terracotta roof (`granite`/`terracotta` stairs), wrought-iron grilles on the windows, a front garden with a low wall, a long backyard with a brick **parrilla/quincho**, an above-ground pool full of green water, a lemon tree. Warm interior, nicotine-yellow walls, saints' cards everywhere, doilies on every surface.

**Lot:** x −22..22, z −24..26 (45 × 51), with the dirt street (`coarse_dirt` + `gravel`) to the north. Night, fog, a street lamp outside.

### Exterior

| Zona | Tamaño | Bloques / props clave |
|---|---|---|
| **Vereda + calle** | 45×6 | Flickering street lamp (`lantern` on `dark_oak_fence`, flicker via block swap). Mailbox. Parked old car under a tarp (`gray_wool` shell over a stair/slab shape); the horn honks by itself. |
| **Jardín delantero** | 21×7 | Low brick wall + iron gate (`iron_bars`), rose bushes, **Don Ramón** the gnome (prop entity) on a flower pot. A sign on the gate: "CUIDADO CON EL PERRO" (with someone adding in marker: "...y con la nona"). |
| **Porch** | 7×3 | Doormat "BIENVENIDOS", a porch light that buzzes, a rocking chair (stairs) that rocks empty during beat 1. |
| **Patio trasero** | 31×16 | **Parrilla/quincho** (6×4 brick with `campfire` + `iron_bars` grill + chimney), long table with a vinyl checked tablecloth (red/white carpet), plastic chairs. **Pelopincho** pool (6×4, `water` + `green_stained_glass` on top + `blue_concrete` walls). Clothesline with sheets (`white_banner`s). **Choripán's doghouse** (3×3 `spruce_planks`, name sign "CHORIPÁN"). **Lemon tree** with a **dug-up hole** (2×2×2) ringed with salt (salt_line block) and the empty, rusted tin. Paved area around the parrilla (`bricks`, `stone`): the dog **cannot burrow** through it (mechanic). |
| **Garaje** | 6×9 | Fuse box (**tablero**: `lever` on `iron_block` + custom sign), shelves, **the neighbour's ladder (borrowed in 2019)**, charcoal bags, an old fridge. Side door to the backyard. |

### Ground floor (y 0..4, house footprint x −11..11, z −8..8 = 23×17)

```
 N (street)
 +-------+---------+--------+
 | GARAJ | LIVING  |  HALL  |  <- porch / front door
 |  6x9  |  9x7    | 3x5    |
 |       +----+----+--+-----+
 |       |COMEDOR | ESCALERA |
 +-------+  7x6   |  + BAÑO  |
 | NONA  +--------+--+------+
 |  6x6  | COCINA 7x6  |LAVADERO -> stairs down
 +-------+-------------+------+
 S (backyard)
```

| Cuarto | Tamaño | Props (vanilla) | Story clue / beat |
|---|---|---|---|
| **Hall** | 3×5 | Coat rack (fence + item frames with coats), mirror (`glass_pane` over `black_concrete`), crucifix on the wall, a saint's card in a frame. | The wall crucifix is **upside down** when you come back. |
| **Living** | 9×7 | Floral sofa (stairs + red wool), doilies (white carpet), **old CRT TV** (new block `tele_vieja` with animated texture) on a cart, a cabinet full of glassware (`glass_pane` + `item_frame` glasses), a **ceiling fan** (prop: rotating ItemDisplay blades), a ceramic dog figurine, family photos (item frames with custom map art). | Family photo wall: in every photo Choripán is looking at the camera... and in the 2026 photo a pale shape is standing behind Lucía. **TV beats** (6, 14). |
| **Comedor** | 7×6 | Long table (`dark_oak_planks` on fences), **8 chairs** (stairs), a sideboard with plates (ItemDisplay plates), a wall clock stopped at 3:07. | **Chair tower** (beat 5). The tablecloth has a red-wine stain shaped like a hand with 6 fingers. |
| **Cocina** | 7×6 | 1970s green tiles (`green_terracotta`), a stove (smoker), a **fridge** (white concrete + iron door, a container holding the **chorizo**), a breadbox (barrel holding the **pan**), a sink (cauldron) with a running tap, **mate + termo** on the table (props). Fridge magnets. | Fridge magnets spell **"ABRIME LA BOCA"**. Mate beats (4). |
| **Cuarto de la Nona** | 6×6 | Single bed with a crocheted blanket, **rocking chair** (prop entity, it rocks), a saints' shrine with candles (**the only always-safe light: sanity regen**), a knitting basket with red yarn, the **"Galletitas" cookie tin** (container block: needles, thread, the **Hilo Bendito**), a 1961 b/w photo of a girl with Clarita. | The tin joke + key item. The photo's caption: "Nélida y Clarita, 1960". |
| **Baño** | 3×4 | Bathtub (cauldron ×2), toilet (`white_concrete` + trapdoor lid), a **mirror** above the sink. | **UV on the mirror reveals "AZAMEL"** written by a finger in the steam (decal on a hidden item frame). Mirror jumpscare (beat 16). |
| **Lavadero** | 4×4 | Washing machine (`iron_block` + `glass_pane` window), laundry basket, stairs down to the basement. | The washing machine turns on by itself; a red sweater spins in the window. |

### Upper floor (y 5..9)

| Cuarto | Tamaño | Props | Clue / beat |
|---|---|---|---|
| **Pasillo** | 2×15 | Long runner rug (red carpet), 5 doors in a row, a ceiling light every 4 blocks, an **attic hatch** (trapdoor) at the end. | **Choripán transformation** (beat 9), door-slam cascade (beat 13). Built long and straight on purpose so the flashlight frames it. |
| **Cuarto de Lucía** | 6×6 | Pink wool, a canopy bed (fences + pink banners), **a shelf holding 30 dolls** (prop dolls as ItemDisplays + 3 real `MunecaEntity`s), crayon drawings (item frames + map art), a music box, a nightlight (`sea_lantern` dimmed with `light` block level 4). | Drawing: 6 stick figures (Mamá, Papá, Toti, Nona, Chori, Yo) and a tall grey one with its hands over Papá's eyes. School notebook: **"MI AMIGO SE LLAMA LEMAZA"** (AZAMEL backwards). |
| **Cuarto de Toti** | 5×6 | Gamer chair (stairs + black wool), PC (`black_concrete` + `redstone_lamp` RGB), posters, an energy-drink pyramid, a **wardrobe** (2×1×3 dark oak) with Toti inside. | Humour beat (Toti in ranked). The PC shows the family chat open. |
| **Matrimonial** | 7×6 | Double bed, dresser, a Virgin-and-child picture, a wedding photo, Jorge's "REY DEL ASADO" trophy. | Marta's diary on the bedside table (dates, escalation). Above the bed a **crucifix that rotates** when you look away. |
| **Baño de arriba** | 3×4 | Bathtub with red water. | Red handprints, child-sized and tiny (doll-sized), UV only. |

### Basement (y −6..−1)

| Zona | Tamaño | Props | Clue |
|---|---|---|---|
| **Sótano** | 15×11 | Water heater (`blast_furnace`), old furniture under sheets (wool), tools, jars of preserves (`decorated_pot`s), a hanging bulb (`lantern` on a chain). | Choripán's paw prints (UV) lead to a **cracked wall**. |
| **Secreto: el cuarto del 61** | 6×6 | Behind a wall of `cracked_stone_bricks` (break it or use the "Pala" from the garage). Untouched since 1961: a child's iron bed with leather straps, **salt circle** on the floor, melted candles, Latin written on the walls ("LEMAZA LEMAZA LEMAZA" scratched in a child's hand), a broken reel tape recorder. | Final arena (stage 6). Anselmo's stole hanging on a nail. |

### Attic (secret, y 10..12)

Reached by the hatch at the end of the upstairs hallway (needs the **neighbour's ladder** from the garage, a humour payoff). 9×5, `spruce` beams, cobwebs, Christmas decorations, a trunk.
Holds the **cassette/reel "ANSELMO 14-8-61"**, the **1961 newspaper** and **Anselmo's letter**.

### Lighting plan

- **Electricity is a resource.** The house has working lights (`redstone_lamp` behind `light_gray_stained_glass` lampshades, toggled by the script). The demon trips the **fuse box** at stages 1→2, 3→4 and 5→6. Reset it at the garage lever. Every reset gives about 60 seconds of calm, then it flickers again.
- **Safe light:** the Nona's shrine candles (sanity regen, entities won't enter the 3-block radius until stage 5... when the Nona herself puts them out with one breath: a strong beat).
- **Diegetic sources:** TV glow (light 6, flickers with static), parrilla embers (light 8, **blue soul fire** while Jorge is possessed), street lamp, nightlight in Lucía's room, the washing-machine window.
- **Darkness zones:** the basement, the attic, the backyard past the pool (fog), the upstairs hallway after beat 9.
- **Distant cumbia** from a neighbour's party plays at low volume through all of stage 1. **When the cumbia cuts out, danger is coming.** It's a diegetic tension meter the audience learns within 3 minutes. It comes back in the epilogue.

### Clue texts (exact)

1. **Family group chat** (new tab in the phone app, "Familia Morales"):
   - Jorge (28/09): "El Chori desenterró una lata en el fondo jaja. Hay una muñeca adentro"
   - Marta: "Tirala que da asco"
   - Nona (all caps): "NO LA ABRAN"
   - Nona: "JORGE ATENDÉ EL TELÉFONO"
   - Lucía (29/09, 03:07): "ya le saqué los hilos"
   - Marta: "¿Lucía? ¿De qué celular escribís?"
   - **Live message during beat 3** (Lucía): "ya llegó?"
2. **Anselmo's letter** (attic): *"A quien la encuentre: lo que vive en la muñeca no es Clarita. Se llama como la niña escribía al revés. No lo pude echar, solo encerrar. Si alguien corta el hilo, buscará volver a su primera casa: la niña. Cosé la boca con hilo bendito mientras se dice su nombre. Y que Dios me perdone por lo que le dejé a esa criatura. — P. Anselmo Ruiz, 15 de agosto de 1961."*
3. **Newspaper** (map art): "EL DIARIO DEL SUR — 18 de agosto de 1961 — NIÑA DE TEMPERLEY 'HABLÓ EN LATÍN' — MUERE EL SACERDOTE QUE LA ATENDIÓ".
4. **Tape "ANSELMO 14-8-61"** (playable in the grabador): Anselmo's prayers, a little girl answering in Latin, then a deep doubled voice: *"Me voy a ir, cura. Pero voy a volver a casa."* Click.
5. **Lucía's notebook:** "MI AMIGO SE LLAMA LEMAZA. VIVE EN CLARITA. DICE QUE TIENE HAMBRE."
6. **Fridge magnets:** "ABRIME LA BOCA".
7. **Marta's diary:** "Día 4: los platos. Día 9: el Chori no duerme, mira la escalera. Día 15: Jorge dice que es la humedad. Día 21: la Nona tejió un suéter rojo para cada uno. Dice que 'por las dudas'."
8. **Bathroom mirror (UV):** "AZAMEL".
9. **The tin under the lemon tree:** "NUNCA LA DESENTIERREN. NUNCA LE CORTEN EL HILO."
10. **1960 photo:** "Nélida y Clarita, 1960".
11. **Choripán's vet card** (doghouse): "Paciente: Choripán. Raza: salchicha. Observaciones: Muy bueno. Come de todo." (Later a 2nd card appears: "Observaciones: YA NO.")

---

## 4. Entities + NPCs

Common system: **`FamiliarEntity`** (an NPC that isn't a `Monster`, can't be hurt by player weapons: damage is redirected to sanity loss + Marta yelling "¡ES MI MARIDO!"). Right-click = next dialogue line (subtitle + TTS). A synced `possession` float (0..1) drives the texture swap/emissive and the boss-style bar **"POSESIÓN — Jorge"**.

**Host-jump rule:** when a host's possession bar hits 0, the demon leaves as **"Humo del Inquilino"**: a particle stream (black smoke + red embers) that **flies visibly** along a path to the next host. Viewers always see where it's going. Clarita teleports next to the next host the moment the player looks away.

### 4.1 Choripán (normal) — `choripan`
- **Behaviour:** follows the player like a vanilla wolf, wags, sniffs. **Dog-sense:** growls at the stairs / at empty corners where a hallucination is about to happen (the hallucination system pre-warns via Choripán; a great free "tell"). Barks at Don Ramón. Lies down at the shrine.
- **Art brief:** dachshund, about 0.55 blocks tall and 1.2 long. Long sausage body (rounded with a stepped profile: 3 cubes), 4 tiny legs, huge floppy ears (rotating bones), long snout with a black shiny nose, big wet brown eyes with 2 white glints. Red-brown coat (`#7a3a1c → #c06a33` ramp), darker back stripe. **Red knitted sweater** (by the Nona) with a cable-knit pattern and a white "C". Name tag on the collar. Tail is a separate bone (wag). Poses: sit, beg, belly-up (for the "rascar la panza" beat), head tilt. About 45 cubes.

### 4.2 CHORIPÁN, VERSIÓN COMPLETA (demon form) — `choripan_demonio` — **the highlight**
- **Transformation (scripted, 6 s):** sits → head rotates 180° → **the body stretches toward the camera one segment at a time** with wet bone cracks, like a slinky going down stairs → the sweater rips into strands → the snout **splits vertically** into a 4-flap mouth → stands taller on 8 legs. The final length is **4.5 blocks**.
- **Movement:** fast on flat ground (0.38). The body follows the head like a snake (8 segment bones; each segment's yaw lags the previous one by N ticks, driven by a position-history buffer synced to the client). Round corners are spectacular: the head turns the corner while the body is still in the previous room.
- **Burrow (backyard only):** dives into grass/dirt and travels as a **moving mound** (block-break particles + a FallingBlock "hump" + a rumble sound) toward the player, then erupts. **It can't burrow through stone/brick**, so the paved parrilla area and the porch are safe islands (strategy + clip).
- **Attacks:** lunge bite (4 dmg + sanity −10), tail whip, the **"long hug"**: it coils around the player 1.5 times and squeezes (screen shake, dark vignette) until you look at it with the crucifix.
- **It's still a dog (humour + mechanic):** throw ANY item → it **stops and chases it** for 3 s (subtitle: "Sigue siendo un perro."). Salt lines stop it; it whines at the line like a dog at a closed door. Marta's chancleta stuns it (§7).
- **Defeat:** the **Choripán Bendito** (§7). It catches it in the air (0.4 s of slow motion via a client-side tick-rate FX + camera zoom), chews, freezes, then **vomits a column of black ectoplasm** (the demon smoke) and retracts with a comic **"boing" slinky sound** back into a cute shivering dachshund, who sneezes. The sweater is gone, so the Nona hands him a scarf in the epilogue.
- **Art brief:** the same palette as Choripán, but the skin between segments is stretched pink-grey and translucent, with ribs visible as ridges pushing through. **The eyes stay big and cute but turn milk-white with tiny red pinpoint pupils** (emissive). This is what makes it funny AND wrong. The mouth split goes from the nose to the throat: 4 flaps (upper-left, upper-right, lower-left, lower-right bones), each lined with **needle teeth** (zero-thickness planes), red gums, a long black tongue (2 bones). Ears hang limp and too long, nearly touching the ground. Red sweater strands hang from the spine (zero-thickness planes, fluttering). **The tail still wags** in every pose. Legs: the front pair is normal dachshund, the 3 extra pairs are thin, human-like with fingers (wrong). Segments: head (snout + 4 jaw flaps), neck, 6 body segments, hips, tail. About 190 cubes, 50 bones. Poses: `stretch` (intermediate lengths for the transformation), `lunge` (jaws open 70°), `coil`, `burrow_dive`, `vomit` (jaws open, neck arched), `beg` (the funniest pose: an 8-legged monster sitting and begging).

### 4.3 Jorge Morales (possessed) — `familiar/jorge`
- **Normal:** comes back through the side gate with a charcoal bag: *"Llegué. No había carbón en lo de Rubén, tuve que ir hasta la estación."* The smoke enters his mouth mid-sentence.
- **Possessed behaviour:** **he keeps making asado.** He walks to the parrilla, the fire lights blue, and he flips chorizos with his **bare hands** while smiling too wide. He talks to you calmly in a doubled voice: *"¿Jugoso o a punto, pibe?"* He attacks only if you come within 5 blocks or turn your back on him:
  - **Brasas:** throws a handful of embers (3 small fireballs, they set the grass on fire).
  - **Cuchillos:** the 6 knives on the parrilla rack **lift up and fly** at you one by one (ItemDisplays with a trail; 2 dmg each). Dodge, or block with a salt line (knives drop when they cross it).
  - **Pinza:** grabs you with the tongs from 3 blocks away (a pull, like a fishing rod).
  - **Neck snap:** the head tilts 90° when the camera flash hits him (also reveals the Inquilino on his back in the photo; §4.9).
- **Freeing him:** the possession bar drops with flash stuns (−15%), holy water (−20%), and **holding the crucifix** on him from within 4 blocks (−5%/s while he's stunned). At 0 he goes limp, falls backwards **into the pelopincho** (big splash). Marta: *"¡Te dije que no comas tanto chorizo!"*
- **Art brief (one model, texture swap normal/possessed):** villager-sized human, 1.9 blocks, big round belly (an overhang cube), short legs, flip-flops. Light-blue and white striped football-style shirt (generic, no crest) under a **black apron reading "REY DEL ASADO"** with a cartoon cow (painted). Bushy black moustache, receding hairline, thick eyebrows. Tongs in his right hand (item bone). Possessed: grey-green skin, black sclera with white pinpoint pupils (emissive), **the smile extended to the ears** (jaw bone + painted stretched lips), burns on his hands, steam from his collar (particles). Poses: grilling (right arm flipping), knife-throw (arm raised, fingers spread, knives orbit), neck-90, limp-fall. About 90 cubes.

### 4.4 Lucía (possessed) — reuses `PoseidaEntity`
- **Before** (normal NPC skin variant, stages 0–3): hides under her bed, talks to Clarita, says creepy-sweet lines (§6, §5).
- **Possessed** (stage 4): the existing behaviour (wall/ceiling climbing, belly-up crawl, 180° head, levitating the player, exorcism bar) **plus** a case-specific rule: **she commands her 30 dolls.** While Lucía hunts, the 3 real `MunecaEntity` dolls and the shelf dolls activate. The weeping-angel rule turns into a **dilemma: you can't look at Lucía and at the dolls at the same time.** Solutions: salt lines behind you (dolls can't cross), or flash the dolls (a 6 s freeze) and then turn back to Lucía.
- **Art changes:** red knitted sweater over the existing nightgown (the Nona's sweater, burnt through at the chest), her left hand holding **Clarita's chewed-off arm**. A new pose: `doll_conductor` (arms raised like a conductor, head 180°).
- **Freed line:** *"No era Clarita... Clarita tenía miedo. El señor feo quiere ir con la Nona."*

### 4.5 La Nona Nélida — `familiar/nona` (final boss)
- **Before (stages 0–4):** sits knitting red in her rocking chair. Hard of hearing ("¿QUÉ?"), offers mate (sanity +15), offers pastries. Tells you off for walking in muddy ("¿No te limpiaste los pies?"). Talks about "el cura" as if senile. **She's been knitting the Hilo Bendito into everything.**
- **The twist (start of stage 5):** after Lucía's exorcism the smoke hovers over Lucía, undecided. The Nona stands up **without her walker** for the first time and shouts: *"¡ACÁ, AZAMEL! ¡VENÍ CON LA VIEJA, COMO ANTES! ¡DEJALA A LA NENA!"*. The smoke goes into her mouth. She blows out the shrine candles with one breath. She walks calmly down to the basement and breaks the wall of the cuarto del 61 **with her hand**.
- **Boss behaviour (stage 6, cuarto del 61):**
  - She **floats seated in her rocking chair**, which rocks in mid-air (chair attached to the model).
  - **Red yarn:** she knits at impossible speed. Her yarn shoots out and **stretches across the room like laser tripwires** (rendered as stretched thin red cubes / leash-like lines between anchor points). Touching one = rooted 2 s + sanity −8. The web densifies every 20 s. Cut it with the **silver dagger** or burn it with a flare.
  - **"Nene, vení"**: calls you in her sweet voice (and in YOUR voice, §8); if you walk toward her while she's at full power, she lifts you (reuse the Poseída levitation).
  - **Knitting needles** fly like the dad's knives, but in pairs.
  - **Poltergeist storm:** every object in the house is thrown around (the whole director runs at max).
- **Resolution:** see §7 "Coser la boca". The last stitch is hers: she grabs your hand: *"Dámelo, nene. Esta vez lo cierro yo."* (an emotional beat). She lands softly. Freed line: *"Sesenta y cinco años tejiendo para esto. ¿Me alcanzás el mate?"*
- **Art brief:** small, hunched (1.5 blocks), wide hips, grey **bun** with a hairnet, **thick round glasses that glare white** (emissive lenses: under the flashlight you can't see her eyes, which is creepy even before the twist), a powdered wrinkled face, a mole, a pearl necklace, a **burgundy cardigan over a floral dress**, thick tights, felt slippers, red yarn and needles in her hands, a ball of yarn in her lap. Possessed: the glasses crack in a spiderweb, behind them **eyes like Clarita's** (one glass-blue, one black hole leaking a black tear: visual rhyme with the doll), the jaw dislocated down to her chest with **her dentures floating out in front of her mouth** (a separate floating bone: horrible and slightly funny), the bun undone into long white strands that move as if underwater. **The rocking chair is part of the model** (pale oak, curved runners, a crocheted cushion). Poses: knitting, levitate-rock, scream (jaw + dentures), yarn-cast (both arms forward), sew (final, calm, hands together). About 170 cubes.

### 4.6 Marta Morales — `familiar/marta` (ally)
- Follows you at a distance in the early stages; hides in the kitchen pantry from stage 2 on. She gives hints in character and **throws the chancleta** (once per stage, automatically, when Choripán or a doll is within 3 blocks of you): a stun plus the line *"¡CHORIPÁN, CHANCLETA!"*.
- **Art brief:** 1.75 blocks, pink fluffy robe, **pink hair curlers** (5 small cylinder cubes on her head), a face-mask cream on one cheek only (she was interrupted), a phone in one hand, a slipper in the other. Expressive eyebrows. Poses: scared (hands to face), chancleta throw, pointing.

### 4.7 Toti — `familiar/toti` (gag NPC)
- Inside the wardrobe all night. Opening it triggers the **fake jumpscare** (§6). He reappears in the epilogue.
- **Art brief:** a lanky teen, hoodie, a huge **RGB headset** (emissive), pimples, fringe over his eyes, a controller in hand. About 50 cubes.

### 4.8 Clarita — reuses `MunecaEntity` + the `CURSED_DOLL` anchor
- **Changes to the existing model:** the mouth thread becomes **red, cut**, with 2 loose ends hanging (the strands sway). The **left arm is missing** (Choripán), with a ragged porcelain stump and stringing cord hanging out. A small **tooth mark** on the skirt. Keep the existing broken-eye design (it rhymes with the possessed Nona).
- **Behaviour:** the anchor. It **teleports to the next host** whenever unobserved (the readable rule). When looked at for more than 4 s without blinking (no crosshair movement), its head turns slowly to follow you, with a porcelain creak. In stage 6 it sits in the Nona's lap: purify it (holy water), then sew it.
- **The 30 shelf dolls:** cheap ItemDisplays with 4 variants (pre-painted textures), rotated toward the player by the poltergeist director.

### 4.9 El Inquilino (Azamel) — `inquilino` (photo-only + final 2 seconds)
- **Never seen with the naked eye.** It appears **only in Spirit Camera photos** (and on the CRT TV in beat 14). Every photo of a possessed host shows it **crouched on their shoulders with its long hands covering the host's eyes**, like a "¿quién soy?" game. In the final seal, it shows for 2 s as it gets sucked into the doll's mouth.
- **Art brief:** translucent (`entityTranslucent`), grey-blue, 2.6 blocks if it stood up, but always **crouched like a frog**. Skeletal, hairless, a long neck, **a face like a smooth porcelain mask without features except a sewn mouth** (it echoes the doll: the stitched mouth is the demon's own signature). Hands enormous (fingers 1 block long, 4 joints). Ribs and spine visible. Poses: `ride` (crouched with its hands forward over an invisible face), `suck` (stretched toward a point, the body thinning like smoke). About 80 cubes.

### 4.10 Don Ramón (garden gnome) — `gnome` prop entity
- **Rule:** whenever you look away, it rotates to face you (the weeping-angel system, but only rotation, never movement). Five scripted relocations across the case (the porch, the parrilla, the pantry, the basement stairs, finally **your home**).
- **Art brief:** classic garden gnome, 0.6 blocks, a chipped red hat, a white beard, a blue shirt, holding a little shovel (that's how the hole got dug? a joke in the bestiary). The paint on one eye is chipped so it looks winking. About 30 cubes.

### 4.11 Background systems
- **Shadow Man / Ánima / hallucinations:** existing, at normal rates. The Shadow Man is replaced in this case by **Inquilino silhouettes in mirrors and windows** (a reflection-only flicker FX).

---

## 5. Scare script (escalation order)

`[CLIP]` = top TikTok/Shorts moment. `[JS]` = full-screen or close-up jumpscare. `[FAKE]` = false scare / laugh.

| # | Trigger | What happens | Sound | Why it works on camera |
|---|---|---|---|---|
| 1 | Teleport arrival | Night street, cumbia in the distance, a street lamp flickering. Don Ramón faces the house. You walk past it to the porch... it's now **facing you**. The empty porch rocking chair rocks once. | `gnome.turn` (ceramic scrape), `porch.creak` | Opening hook in the first 20 s; it sets up a running gag. |
| 2 | Talk to Marta | Choripán runs out, wags, and does the cute greeting (clip of the "protagonist" dog). He walks in with you, **stops at the foot of the stairs and growls at nothing upstairs**. Something small crosses the top step. | `choripan.bark_cute`, `choripan.growl_low`, tiny footsteps | Viewers fall in love with the dog: this sets up the betrayal. |
| 3 | Reading the family chat with Marta next to you | The phone vibrates: a **live message from "Lucía": "ya llegó?"** Marta, white-faced: *"...Lucía no tiene celular."* The cumbia stops. | `phone.notify`, silence drop | **[CLIP]** A perfect 10-second TikTok: setup, punchline, silence. |
| 4 | Kitchen, first evidence | The mate on the table **slides 2 blocks on its own**; the termo tilts and pours into it ("te ceban un mate"). The player laughs... and a plate flies off the sideboard and **shatters 1 block from his head**. | `mate.slide`, `termo.pour`, `plate.whoosh` + `plate.shatter` | First physical poltergeist. The laugh-then-hit structure catches the player off guard. |
| 5 | Leaving the dining room, then turning back | **All 8 chairs stacked in a tower on the table**, up to the ceiling, the top chair swaying. Marta: *"¡Esas sillas eran de mi suegra!"* (the Nona, from the other room: *"¡TODAVÍA SON MÍAS!"*) | `chair.stack` (wood clatter that happened "while you weren't looking"), silence | Iconic, immediately readable, a thumbnail image. |
| 6 | Walking through the living room | The CRT **turns on by itself**: static, then a slow zoom on Clarita's cracked face, then text: **"CHORIPÁN TIENE HAMBRE"**. Off. | `tv.on_thunk`, `tv.static`, a low hum | **[JS]** (small) Sets up the dog. |
| 7 | Upstairs, Lucía's door | Knocks from inside in the "shave and a haircut" rhythm. If the player knocks back ("dos golpes"), it answers... **from the door behind him** (the master bedroom). Then from the ceiling. | `sanity.knock` variants, positional | Interactive. Players love knocking back. |
| 8 | Lucía's room | 30 dolls on the shelf. Each flashlight sweep: **one more doll is turned toward you**. On the 4th sweep all of them are. A small voice from under the bed: *"Clarita dice que tu perro... digo, nuestro perro... tiene hambre."* Lucía is under the bed, normal, hugging Clarita. When you look at Clarita: she's gone from Lucía's arms. | `doll.turn` (soft clicks), `lucia.whisper` | Slow-burn dread; no monster, all implication. |
| 9 | 3 evidences collected | **CHORIPÁN TRANSFORMATION** in the upstairs hallway. Power cut. Flashlight on: Choripán is sitting at the end of the hallway, **chewing Clarita's arm**. Player says "¿Choripán?" (voice capture §8). The head turns 180°. Then the body **stretches toward the camera segment by segment** down the 15-block hallway, the sweater ripping. The jaw splits open. Chase down the stairs. | `choripan.crack` ×8, `choripan.stretch` (wet rubber), `sweater.rip`, `choripan.demon_roar`, the music stinger | **[CLIP] [JS]** THE moment of the video. Absurd and terrifying; the slow stretch gives the streamer time to react. |
| 10 | Backyard chase | The demon dog dives into the lawn. A **dirt mound races toward you** across the backyard (Tremors homage). You jump onto the paved parrilla area: it erupts 1 block short and **hits the edge like a dog hitting a glass door**, then circles. From the dark garden **YOUR voice** calls "¡Choripán, vení!" (§8). | `burrow.rumble`, `dirt.erupt`, a thump + whine, the voice-mimic clip | **[CLIP]** Readable mechanics, a funny slapstick impact, then the creepy voice. |
| 11 | Throwing the Choripán Bendito | **Slow-motion catch** in the air, chew, freeze, a **fountain of black vomit**, then it retracts with a cartoon **"boing"**, shrinks back to a cute dog who sneezes. Silence. The black smoke rises, hangs... and flies over the wall into the side gate where Jorge is entering: *"Llegué. No había carbón en lo de—"* (smoke into the mouth). | `choripan.chomp`, `choripan.vomit`, `slinky.boing`, `choripan.sneeze` | **[CLIP]** Hilarious payoff into a cliffhanger in the same 15 seconds. |
| 12 | Jorge possessed at the parrilla | Blue fire. He flips chorizos with his bare hands: *"¿Jugoso o a punto, pibe?"* The 6 knives lift from the rack and **orbit him**, then fly one by one. The camera flash shows the **Inquilino on his shoulders covering his eyes** (the photo is saved to the phone gallery). | `fire.blue_whoosh`, `jorge.demon_lines`, `knife.whoosh`, `camera.flash` | **[CLIP]** Horror-comedy in one frame; the photo is a ready-made thumbnail. |
| 13 | Jorge freed (falls into the pool) | The smoke flies upstairs. Lucía screams. **Every door in the upstairs hallway slams in sequence toward the camera**: BANG, BANG, BANG, BANG, BANG, the last one in your face. Lights burst one by one. | `door.slam` ×5 with increasing volume, `bulb.pop` | **[JS]** Classic, rhythmic, built to be cut to the beat. |
| 14 | Hunting Lucía | The TV in the living room turns on alone, upstairs audible: it shows a **static image of the hallway from above, with you in it and a small figure on the ceiling above you**. Look up: Lucía drops from the ceiling (existing spider-walk + head-180). The dolls activate: **you can't look at both.** | `tv.static`, `poseida.crack`, `poseida.scream`, `doll.giggle` chorus | **[JS]** A layered threat; the "look at both" dilemma creates panic you can't fake. |
| 15 | Exorcism of Lucía done | Silence. A red sky through the window. The smoke hovers over Lucía, choosing. The **Nona stands up without her walker**: *"¡ACÁ, AZAMEL! ¡VENÍ CON LA VIEJA, COMO ANTES!"* The smoke enters her. She blows out the shrine candles in one breath. Walks to the basement. You hear **the wall breaking with one blow**. | `nona.call` (strong, not aged), `candles.out`, `wall.break` | The twist. Emotional, and it reframes all her comic scenes. |
| 16 | Going to the bathroom for the name (if not found yet) or passing any mirror in stage 5 | UV on the mirror reveals AZAMEL... and the **Nona's face is in the mirror behind you**, glasses cracked, dentures floating. Turn around: no one. | `mirror.sting`, a shriek | **[JS]** The Nona's portrait as the full-screen jumpscare image. |
| 17 | Entering the cuarto del 61 | The Nona **floating in her rocking chair**, which rocks in the air; red yarn shooting out to lace the room; Clarita in her lap, laughing through the cut thread; the Latin scratchings glow. The cumbia comes back distorted and slow from upstairs. | `rocking.creak` (slowed), `yarn.twang`, `cumbia_dist` | **[CLIP]** The final image of the case: grotesque, iconic, impossible to scroll past. |
| 18 | The 3 stitches | Each stitch, the house goes crazy: **stitch 1** all the plates fly through the basement door; **stitch 2** the TV upstairs screams with Lucía's voice; **stitch 3** Choripán (cute) runs in, barks, and **bites the Nona's yarn** to free your hand. The Nona sews the last pass. The Inquilino becomes visible for 2 s and gets **sucked into Clarita's mouth**. | `stitch.pull` ×3, `poltergeist.storm`, `inquilino.suck` (reverse scream) | The climax uses everything set up before (the dog as an ally is the emotional payoff). |
| 19 | Epilogue | Morning. Birds. The family at breakfast with pastries. Jorge in a towel: *"¿Te quedás al asado?"* **Toti comes out of the wardrobe**: *"¿Qué me perdí?"* The cumbia is back. | birds, kettle whistle, laugh | The breath before the next case. |
| 20 | Post-credits, at home | Back home, the phone gets a **voice message in YOUR voice**: *"...Choripán... vení..."*. Turn around: **Don Ramón the gnome is in your room, facing you.** | the voice-mimic clip, `gnome.turn` | **[CLIP]** A creepy laugh to end the case, perfect for the end of a Short. |

**The 5 best clips:** #9 transformation, #11 blessed choripán + vomit + the dad possessed mid-sentence, #12 "¿jugoso o a punto?" with orbiting knives, #17 the floating Nona in her rocking chair with red yarn, #3 "Lucía no tiene celular". Honourable mentions: #20 voice message + gnome, #10 burrow-into-glass-wall.
**Jumpscares:** #6 (TV doll), #9 (split snout close-up), #13 (door cascade), #14 (Lucía from the ceiling), #16 (Nona in the mirror). Plus the fake one (Toti).

---

## 6. Humour beats (without killing the fear)

Rule: **the laugh comes first and the scare follows within 10 seconds** (laugh → release → strike). Or the laugh comes after a scare as a release valve, never in the middle of one.

1. **"Fue a comprar carbón."** Jorge has been gone 2 hours. Marta: *"Como mi viejo con los cigarrillos, ¿viste? Bueno, mi viejo volvió a los 3 años."* Running gag: every phone hint in stages 0–2 ends with "(Jorge sigue sin volver)". The payoff is his entrance in beat 11.
2. **Don Ramón the gnome.** Always facing you. The bestiary entry: *"Gnomo de jardín. Peligro: desconocido. Tiene una pala. Sacá tus conclusiones."* The payoff: in your house at the end.
3. **Toti in the wardrobe [FAKE].** Tense music, a wardrobe that knocks; the player opens it ready for a jumpscare... a teen with an RGB headset screams louder than him: *"¡CERRÁ, CERRÁ, QUE ESTOY EN RANKED!"*. He closes it himself. If you open it again: *"¿Sos el de las pizzas?"*.
4. **The chancleta de madre.** Marta's thrown slipper stuns the demon dog. Phone tip: *"Dato: la chancleta de una madre argentina tiene más poder que el agua bendita."* Afterwards she hands it to you: **"Chancleta de Madre"** item (§7). It flies like a boomerang.
5. **The cookie tin.** The key item for the final is in the Nona's "Galletitas" tin. Opening it shows a full-screen tooltip: *"Hilos, agujas y botones. Obvio. Nunca son galletitas."* Universal Latin American joke; it lands every time.
6. **The Spirit Box comedic answers** (functional too):
   - "¿Cómo te llamás?" → "AZAMEL" (the name clue)
   - "¿Quién sos?" → "EL INQUILINO"
   - "¿Qué querés?" → "UN CHORIPÁN" (the puzzle clue for stage 2)
   - "¿Sos de Boca o de River?" → long static... "SOY DE TEMPERLEY"
   - "¿Pagás el alquiler?" → "NUNCA"
7. **The possessed dad stays an Argentine dad.** Demon voice, mundane lines: *"PASAME LA PINZA."* / *"LE FALTA SAL."*. If you throw consecrated salt at him he screams, and the subtitle reads: *"Ahora sí tiene sal."*
8. **"Sigue siendo un perro."** The 4.5-block demon dog stops mid-chase to chase a thrown stick, or **sits and begs** when you hold a chorizo (8-legged monster begging). Bestiary entry: *"Choripán (versión completa). Peligro: 5/5. Ternura: 5/5. No le tires la pelota, o sí."*
9. **The Nona's mate.** She always offers it (sanity +15). At peak tension she yells from her room *"¿QUERÉS UN MATECITO?"*. Funny until the twist recontextualises it.
10. **Doña Chela, the neighbour, calls mid-case** (the phone rings during stage 3): *"Ya que estás ahí, ¿le podés pedir a Jorge la escalera que le presté en el 2019?"*. The ladder is in the garage and is needed for the attic: a callback.
11. **The sign on the gate:** "CUIDADO CON EL PERRO" + marker underneath: "...y con la nona". Viewers only get it after the twist.

---

## 7. New mechanics for this case + use of existing tools

### New items / mechanics

| Ítem / mecánica | Cómo funciona |
|---|---|
| **Choripán Bendito** (craft-in-world puzzle) | 1) **Chorizo crudo** from the fridge. 2) Cook it on the **parrilla** (campfire use, 10 s). 3) Put it into **pan** from the breadbox (right-click pan with the cooked chorizo → **Choripán**). 4) Sprinkle **holy water** on it → **Choripán Bendito** (gold sparkle). Throw it (like a snowball). It's only accepted by the demon dog in a calm moment: it has to see it (in its line of sight). Clue sources: the Spirit Box ("UN CHORIPÁN"), the TV ("CHORIPÁN TIENE HAMBRE"), the call variant "Vení con hambre", and Marta: *"Lo único que lo calma es un choripán... pero no le vamos a dar uno a ESO, ¿no?"* |
| **Chancleta de Madre** | Thrown boomerang: comes back to you, stuns minor entities 2 s (dolls, demon dog), 0 damage. 1 per case, kept as a trophy and usable in later cases. |
| **Hilo Bendito + Aguja** | Found in the Nona's cookie tin (stage 5). Used on the purified Clarita while the Nona is stunned: a **3-stitch minigame**. The doll jerks its head; keep the crosshair on the mouth (a shrinking target circle on the HUD) for 2 s per stitch. If you miss, the stitch tears out and the room slaps you (knockback + sanity −10). While stitching, you must **say/choose the name** (ritual book prompt). |
| **El nombre** | The ritual book in this case opens a 3-option prompt: **LEMAZA / AZAMEL / CLARITA**. Wrong name = the demon laughs in Lucía's voice and the exorcism bar resets 30%. Clues: Spirit Box, the UV mirror, Lucía's notebook (reversed), Anselmo's letter. |
| **Posesión (host bar)** | Per-host boss bar. It goes down with: flash stun −15%, holy water −20%, crucifix hold −5%/s while stunned, ritual book (Lucía, Nona). The host can't be "killed". At 0 → the smoke flies to the next host (visible). |
| **Tablero (fuse box)** | The demon trips the breakers at fixed stage transitions + 1 random trip. Reset at the garage lever. Lights = sanity regen indoors. On reset, the house hums back to life (sound) — 60 s of calm. |
| **Grabador + cinta "ANSELMO 14-8-61"** | A reel recorder (block). Insert the tape → plays the 1961 exorcism (45 s audio, subtitles). Counts as evidence. While it plays, the poltergeist director is at 0: a forced calm to listen to the story. |
| **Mate de la Nona** | Consumable (sanity +15, 3 uses). After the twist, the remaining mates turn to **"Mate frío"**: sanity −5 and a hair in the bombilla. |
| **Escalera de Doña Chela** | Placeable item: a ladder needed to reach the attic hatch. |
| **Bufanda roja de la Nona** | Found in a drawer (optional): wearing it (head slot) **halves possession effects** on the player (levitation duration, voice-mimic sanity drain). Lore: the Nona knew all along. |
| **Pala** (garage) | Breaks the cracked wall in the basement (alternative: the Nona breaks it in beat 15). |
| **Poltergeist director** | A per-case system: a tension budget that rises with stage and time; events cost points and have cooldowns. **Off-camera rule:** most events (chair tower, doll turns, crucifix flipped, gnome) happen only when outside the player's view cone; **on-camera** events (plate throw, mate slide, TV, door cascade) are rationed (max 1 per 45 s) to stay special. Events: plates/glasses fly (ItemDisplay ballistic + shatter particles), chairs stack (BlockDisplay stairs animated over 0 ticks while unseen), cabinets/trapdoors/doors toggle, the tap runs, the TV powers on, the ceiling fan accelerates until **a blade flies off** (ItemDisplay), the washing machine spins, pictures turn upside down, the car horn, the wall crucifix inverts, the gnome relocates, a doll turns. |

### Existing tools in this case

| Herramienta | Uso específico |
|---|---|
| **EMF** | Level 5 near Clarita and near the next host (the meter is the alternative "where is the doll" read). Level 5 on Choripán's doghouse before the transformation: a hint. |
| **Spirit Box** | The comic + functional answers (§6). 1 evidence. |
| **Spirit Camera** | Flash stuns hosts and dolls. **Photos reveal the Inquilino on the host's shoulders** (saved in a phone gallery tab: the video's thumbnail images). 1 evidence. |
| **Linterna UV** | Doll-sized red handprints on the bathroom tub → the stairs → the basement wall; dog paw prints to the cracked wall; **AZAMEL** on the mirror. |
| **Sal** | Stops the demon dog (it whines at the line), stops dolls, drops flying knives, makes the dad scream ("ahora sí tiene sal"). |
| **Crucifijo** | Hold on stunned hosts to lower possession; pushes the demon dog's coil off. |
| **Agua Bendita** | Purify Clarita (anchor), bless the choripán, −20% possession. |
| **Libro de Rituales** | Lucía's exorcism (existing) + the final exorcism with the name prompt. |
| **Daga de plata** | Cuts the Nona's red yarn tripwires. |
| **Bengalas** | Burn the yarn; scare dolls (they freeze in bright light for 4 s). |
| **Frasco de Almas** | Final: jar the sealed Clarita (the demon inside). The jar shows the doll inside, mouth sewn: it goes on the trophy shelf at home. |
| **Velas rituales / pastillas** | Standard sanity. |

---

## 8. Voice-mimic (Simple Voice Chat) in this case

### Technical approach (optional dependency)
- `fabric.mod.json` → `"suggests": {"voicechat": "*"}` and an entrypoint `"voicechat": ["com.deadline.compat.voice.DeadLineVoicePlugin"]` (class implements `VoicechatPlugin`). Load it only if the mod is present (the class isn't referenced from the main mod otherwise).
- **Capture:** `MicrophonePacketEvent` → `event.getPacket().getOpusEncodedData()` per sender. Keep a per-player **in-memory ring buffer** (last 90 s) of 20 ms opus frames with timestamps. Split into **utterances** on silence > 350 ms (a frame-energy estimate after decoding with `api.createDecoder()`; you need PCM anyway for tagging).
- **Context tagging (the key idea, no speech recognition needed):** each utterance is stored with game context at the time of speaking:
  - `NEAR_DOG` (within 8 blocks of Choripán or looking at him) → is likely "Choripán", "vení", "buen chico".
  - `SCREAM` (peak amplitude > threshold, or spoken within 2 s of a jumpscare FX).
  - `CALLING` (spoken while another player is > 15 blocks away; co-op) → likely the friend's name.
  - `QUESTION` (spoken while holding the Spirit Box).
  - `NEAR_NONA` / `NEAR_LUCIA`.
- **Engineered capture moments:** the design pushes the player to speak:
  - Marta: *"Llamalo vos, decile 'Choripán', capaz a vos te hace caso."* (guaranteed NEAR_DOG clip before beat 9).
  - The Spirit Box needs a spoken question (with SVC on, the question is the player's mic, and the box answers after a pause).
  - Beat 7 invites knocking and talking at the door.
- **Playback:** `api.createLocationalAudioChannel(uuid, level, pos)` or `createEntityAudioChannel(uuid, entity)` + `api.createAudioPlayer(channel, api.createEncoder(), pcmSupplier)`. Process the PCM before re-encoding: **pitch shift, reverb, low-pass "from behind a wall", or a demon double** (the original + −5 semitones mixed). Custom volume category "DEAD LINE — voces" so players can adjust/mute it.
- **Privacy/consent (important for a public video):** a one-time screen on first join: *"DEAD LINE puede grabar fragmentos de tu voz (solo en memoria, nunca en disco) para que las entidades te imiten. ¿Activar?"*. A per-player toggle in the phone settings. Buffers are wiped when the case ends. In co-op, each player consents separately.
- **Fallback without SVC:** the same beats play a TTS line with the player's name (`em_alex` pitched to match), so the video works either way.

### Uses in this case

1. **Beat 10 (backyard):** from the dark garden, YOUR voice: *"¡Choripán, vení!"* (NEAR_DOG clip, low-passed, positional), when the dog is already next to you. Who's calling it?
2. **The demon dog "barks" your voice:** once in the chase, its bark morphs into your last NEAR_DOG utterance, pitched down 7 semitones with a growl layer. Horrible and funny.
3. **Lucía's room:** the baby monitor (a prop on the nightstand) plays your voice from 10 minutes ago, pitched up as a child: the "doll voice". Clarita repeats you.
4. **Your scream from the basement** (SCREAM clip) during stage 4, when you're upstairs. In co-op it's devastating: the friend runs to the basement to "help" you.
5. **The Nona's boss phase:** "Nene, vení" alternates with **your own NEAR_NONA clip**. When she lifts you, she whispers your clip right in your ear (headphones + a 3D position 0.3 blocks from the head).
6. **Co-op (friend as co-star):** the demon copies the friend's CALLING clip from the opposite side of the house: *"¡Vení, encontré algo!"* while the friend is next to you.
7. **Post-credits:** the voice message at home, your NEAR_DOG clip: *"...Choripán... vení..."*. Played through the phone UI as a voicemail with a waveform.
8. **Spirit Box echo:** occasionally the box "answers" with a 0.5 s fragment of your own previous question, reversed. The viewers notice; the player doesn't.

---

## 9. Sound list + new items/blocks/textures

### New sounds (TTS = Kokoro voice, DSP from `tools/audio/dsp.py`)

| Clave | Descripción |
|---|---|
| `casa.cumbia_far` | Loop, 40 s: an original synthesized cumbia (güiro + a bouncy bass + an accordion-ish synth lead), band-passed as if from 3 houses away. Plus `casa.cumbia_dist`: slowed −40%, reverb, pitch wobble. |
| `casa.house_hum` | Fridge + fluorescent hum loop; dies on the breaker trip. `casa.breaker_trip` (clunk + spark), `casa.breaker_reset` (clunk + lights buzz on). |
| `choripan.bark_cute` / `.whine` / `.sneeze` / `.growl_low` | Synth small-dog barks (formant-shifted noise bursts), high and friendly. |
| `choripan.crack` | Wet bone crack (celery snap + low thump), 6 variations. |
| `choripan.stretch` | Long rubbery stretching creak (a slowed-down balloon squeak + flesh). |
| `choripan.demon_roar` | A small-dog bark layered with a big low roar and a reversed scream. |
| `choripan.burrow` / `dirt.erupt` | A rumble loop + a dirt explosion. |
| `choripan.chomp` / `.vomit` | A comic chomp; a long thick gurgle + splatter. |
| `slinky.boing` | A cartoon spring retraction (descending pitch-bent boing). The only explicitly cartoon sound in the case. |
| `sweater.rip` | Fabric tear. |
| `jorge.lines` | TTS em_alex: "Llegué. No había carbón en lo de Rubén..." / "¿Jugoso o a punto, pibe?" / "PASAME LA PINZA" / "LE FALTA SAL" / "EL ASADO ES SAGRADO" (possessed = em_alex + em_santa −5 st doubled). |
| `fire.blue_whoosh`, `grill.sizzle` | The parrilla ignition; sizzling fat. |
| `knife.lift` / `.whoosh` / `.impact` | A metal shing, an air cut, a thunk into wood. |
| `plate.whoosh` / `.shatter`, `glass.shatter` | Ceramic and glass breaking, 4 variations. |
| `chair.stack` | A short dense wood clatter (plays only after the fact, as if heard while you weren't looking). |
| `door.slam` | Heavy door slam, a 5-step cascade version with escalating volume and closeness. |
| `bulb.pop` | Glass pop + spark. |
| `tv.on_thunk` / `tv.static` / `tv.scream` | CRT power-on degauss thunk + whine; static; Lucía's scream through a tiny speaker. |
| `mate.slide` / `mate.sip` / `termo.pour` | Ceramic slide on wood; **the empty mate gurgle** (an iconic sound); hot water pour. |
| `fan.accelerate` / `fan.blade_off` | Ceiling fan whir pitching up; snap + whoosh. |
| `washer.spin` | Washing machine drum, unbalanced. |
| `gnome.turn` | A short ceramic scrape on stone. |
| `doll.turn` / `doll.giggle_chorus` | Porcelain clicks; 30 tiny giggles offset in time and pitch. |
| `lucia.lines` | TTS ef_dora +3 st: "Clarita dice que tu perro... digo, nuestro perro... tiene hambre." / "No era Clarita..." |
| `marta.lines` | TTS ef_dora: greeting, hints, "¡CHORIPÁN, CHANCLETA!", "¡Esas sillas eran de mi suegra!", "¡Te dije que no comas tanto chorizo!" |
| `chancleta.throw` / `.hit` | A rubber whip; a slap. |
| `nona.lines` | TTS ef_dora −3 st + tremolo + slower: "¿QUERÉS UN MATECITO?", "¿No te limpiaste los pies?"; the twist line **without the aging effect** (strong, clear); possessed = ef_dora + em_santa doubled. |
| `rocking.creak` | Wooden rocking chair creak, a looping rhythm; a slowed version for the boss. |
| `yarn.twang` / `yarn.snap` | A tight-string pluck; a cut string. |
| `stitch.pull` | A needle through cloth + thread pulled tight (close, ASMR-ish). |
| `inquilino.suck` | A reversed scream sucked into a point + a porcelain "tink". |
| `candles.out` | A single long breath + 7 small flame-outs. |
| `wall.break` | A single massive blow + brick rubble. |
| `tape.anselmo` | 45 s: a reel hiss + Anselmo (em_santa, aged, Latin and Spanish) + the girl (ef_dora +5 st) answering in Latin + the demon line "Me voy a ir, cura. Pero voy a volver a casa." `tape.insert` / `tape.click`. |
| `toti.lines` | TTS em_alex +4 st: "¡CERRÁ, CERRÁ, QUE ESTOY EN RANKED!" / "¿Sos el de las pizzas?" / "¿Qué me perdí?" |
| `chela.call` | TTS ef_dora −2 st, "phone EQ": the ladder call. |
| `morning.birds` / `kettle.whistle` | Epilogue. |
| `mirror.sting` | A glassy string scrape + a shriek. |
| `phone.voicemail` | Voicemail beep + playback frame (wraps the voice-mimic clip). |

### New items

`chorizo_crudo`, `chorizo_asado`, `pan`, `choripan`, `choripan_bendito`, `chancleta_de_madre`, `hilo_bendito`, `aguja`, `cinta_anselmo`, `mate_nona` (+ `mate_frio`), `escalera_chela` (ladder placer), `bufanda_roja` (wearable), `pala`.

### New blocks

`tele_vieja` (animated texture: off / static / Clarita / text "CHORIPÁN TIENE HAMBRE" / hallway image), `grabador` (reel tape recorder, accepts the tape), `lata_galletitas` (container, blue tin), `tablero` (fuse box), `heladera` (fridge container), `heladera` magnets decal, `mirror` (UV-reveal surface), `estampita` (saint card, wall decoration), `carpeta_crochet` (doily carpet).

### New entities / props

`choripan`, `choripan_demonio`, `familiar` (Jorge / Marta / Toti / Nona variants), `inquilino`, `gnome`, `rocking_chair_prop`, `ceiling_fan_prop`, `humo_inquilino` (particle-trail entity), Lucía normal skin variant, Clarita model update.

### Textures / art

- Map-art clues: family photos (×4, one with the shape behind Lucía), Lucía's drawings (×3), the 1961 newspaper, Anselmo's letter, the vet card(s).
- Jumpscare portraits: **Choripán split snout**, **Nona with floating dentures**, Jorge's ear-to-ear smile.
- Phone UI: a "Familia Morales" chat tab, a photo gallery tab (Inquilino photos), voicemail UI.
- Bestiary entries: Choripán (versión completa), El Inquilino, Don Ramón.

---

## 10. Minutes of video + pacing

**Target in the final edit: about 7 minutes** of the 20 (intro/outro about 1.5 min; the other two cases about 5.5–6 min each). This is the funniest of the three, so put it **second**: after the school-of-nuns case sets the tone, and before the hospital closes on pure horror. **Raw gameplay to record: 35–45 min** (with co-op, 2 POVs).

| Tramo | Contenido | Minutos en el edit | Tono |
|---|---|---|---|
| Call + arrival | The call (Marta) + the gnome + Choripán's greeting + "fue a comprar carbón" | 0:45 | Comedy, cozy-wrong |
| Investigation | The chat ("Lucía no tiene celular"), mate + plate, chair tower, TV, knocks, the doll shelf, Toti's wardrobe (fake), the Spirit Box jokes | 1:30 | Rising dread, laughs as relief |
| **Choripán** | Transformation, chase, burrow, chancleta, blessed choripán puzzle, slow-mo catch, vomit, boing | 1:30 | **Peak horror-comedy** |
| Jorge | "Llegué..." → possessed, asado, knives, photo, falls into the pool | 0:45 | Horror-comedy |
| Lucía | Door cascade, ceiling drop, dolls dilemma, exorcism | 1:00 | Pure horror |
| Twist + finale | The Nona's sacrifice, candles out, mirror, floating rocking chair, yarn, 3 stitches, Choripán bites the yarn, the seal | 1:15 | Horror, then emotion |
| Epilogue + stinger | Breakfast, Toti "¿qué me perdí?", the voicemail + the gnome at home | 0:15 | Laugh + chill |

**Pacing curve:** a laugh every 60–90 s in the first half, falling to zero during Lucía and the final; one big release at the epilogue. Never two jumpscares less than 45 s apart. Every stage ends on a cliffhanger (smoke flying somewhere), so the edit can cut on hard transitions.

**Editing hooks for the creator:** the cumbia stopping as the audio cue for "something is coming"; the gnome as a recurring cutaway; the Inquilino photo as the thumbnail ("¿LO VES?"); the 5 marked clips as Shorts.

---

## Build-order recommendation (smallest path to a filmable case)

1. Site rebuild (expand `MoralesHouseSite`: backyard, parrilla, pool, garage, the cuarto del 61, the attic) + clues as map art.
2. `CaseScript` stages + `FamiliarEntity` dialogue + the possession bar + the smoke host-jump.
3. **Choripán + Choripán Demonio** (the highlight first), blessed-choripán items.
4. Poltergeist director (plates, chairs, TV, doors, mate) + the fuse box.
5. Jorge, then the Nona boss + the stitch minigame. Lucía is already mostly done.
6. SVC voice-mimic compat module (optional) + the fallback.
7. Sounds/TTS batch, jumpscare portraits, the epilogue + stinger.
