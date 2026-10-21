# Casa Morales: mecánicas Java (plan de implementación)

Plan técnico del caso 2 (BIBLIA §2.2). Todo lo que necesita `CasaScript` (el guion, que se escribe al final contra
estas APIs) se reparte en **paquetes con dueño exclusivo de archivos**, para implementarlos en paralelo sin pisarse.
Regla de oro: reusar lo que ya existe (`Props`, `Run.actor`, `Fixtures`, `Fx`, `Voice`, `SaltGuard`,
`HolyWaterEntity`, `ApparitionEntity`, `HauntRenderer`) antes de inventar sistemas nuevos.

## Convenciones comunes

- Paquete Java nuevo: `com.deadline.casa` (servidor) y `com.deadline.client.casa` (cliente).
- **Registros sin archivos compartidos:** cada paquete registra lo suyo en **su propia clase** de registro
  (`CasaEntities`, `CasaItems`, `CasaRenderers`, `CasaNet`...) con un `static void init()`. El paquete de integración
  (P6) agrega una sola línea por clase en `DeadLine.onInitialize` / `DeadLineClient.onInitializeClient`.
  Nadie más toca `ModEntities`, `ModItems`, `ModRenderers`, `DeadLine.java`, `DeadLineClient.java`.
- Sonidos: ya están generados en `ModSounds` (`CASA_*`, `CHORIPAN_*`, `GRILL_SIZZLE`, `KNIFE_*`, ... ver
  `tools/audio/sounds_def.py`); líneas `casa.*` en `tools/audio/lines.py` (se dicen con `Run.say`).
- Textos de idioma: cada paquete agrega sus claves a `tools/data/lang.py` **en un bloque propio** marcado
  `# --- casa:<paquete>` y corre `python3 tools/data/gen_data.py`. (Conflictos de merge triviales: bloques separados.)
- Modelos: `tools/models/build_all.py <key>` genera `client/model/gen/<Key>ModelBase.java`, `<key>.png`,
  `<key>_<variant>.png` (looks de `VARIANT_MATS`) y `<key>_eyes.png`. El animador va en `client/model/<Key>Model.java`.
- No se puede compilar local (maven bloqueado): CI compila, corre el smoke de servidor y saca capturas del cliente.
  Leer firmas reales en el código existente; ante la duda, la sonda `tools/ci` (javap) del workflow `api-probe`.

## P1 · Familia (Marta, Jorge, Nona, Toti) + Lucía normal + Ofelia con looks

Archivos: `casa/FamilyEntity.java`, `casa/CasaEntities.java` (solo los tipos de P1), `client/casa/FamilyRenderer.java`,
`client/model/{Marta,Jorge,Nona,Toti}Model.java`, cambios en `client/model/PoseidaModel.java`,
`client/model/MunecaModel.java`, `client/casa/CasaRenderers.java` (solo P1), `entity/PoseidaEntity.java`
(solo el modo guionado normal), `entity/MunecaEntity.java` (solo looks + `purify`).

- `FamilyEntity extends HauntEntity`: guionada como `ApparitionEntity` (sin IA propia, invulnerable, no empujable,
  `scripted = true`) pero **con física** (gravedad, colisión) y con `walkTo(Vec3 target, double speed)` (usa la
  navegación terrestre y apaga `noAi` mientras camina) y `float(boolean)` (sin gravedad, se mece: la Nona flotando).
  Tipos: `MARTA`, `JORGE`, `NONA`, `TOTI` (hitboxes 0.6×1.75 / 0.7×1.9 / 0.6×1.5 / 0.6×1.8).
- Poses = `action` (ints en `FamilyEntity.POSE_*`, nombres = poses de `ent_<key>.py`): `IDLE, POINT, SCARED,
  SHOW_PHONE, THROW` (Marta) · `GRILL_FLIP, KNIFE_CONDUCT, LIMP_FALL, CARRY_BAG` (Jorge) · `KNIT_SIT,
  STAND_WALKER, STAND_NO_WALKER, THROW_CHANCLETA, FLOAT_ROCK, YARN_CAST, SCREAM_DENTURES, SEW_CALM, OFFER_MATE`
  (Nona) · `CROUCH_CLOSET, SLAM` (Toti). Looks = `variant` (0 normal, 1 poseído/a).
- `FamilyRenderer`: como `HauntRenderer` pero elige `textures/entity/<key>.png` o `<key>_<look>.png` según
  `variant`, y la capa `eyes` correspondiente. Generalizarlo para que **Lucía** (`PoseidaEntity`: 0 normal,
  1 poseída) y **Ofelia** (`MunecaEntity`: 0 cortado, 1 cosida) usen el mismo mecanismo.
- `PoseidaEntity`: con `scripted` sus metas no corren (normal: debajo de la cama, parada tímida, mareada);
  al pasar a poseída el guion hace `setVariant(1)`, `scripted=false`, `setNoAi(false)`.
- `MunecaEntity`: `purify()` (agua bendita guionada: humo, chillido, `setWeakened(true)`, evento
  `run.post("purify:ofelia")` si está en un Run); look 1 = cosida.
- Animadores: siguiendo ANIM_NOTES de cada `ent_*.py` (toggles: sonrisa de Jorge, dentadura/pelo suelto de la
  Nona, andador/mecedora, auriculares RGB de Toti). **Depende de los modelos terminados.**

## P2 · Choripán (perro) y Choripán demonio (cadena)

Archivos: `casa/ChoripanEntity.java`, `casa/ChoripanDemonEntity.java`, `casa/ChoripanEntities.java`,
`client/casa/ChainRenderer.java`, `client/model/ChoripanModel.java`, `client/model/ChoripanDemonModel.java`,
`client/casa/ChoripanRenderers.java`, hook en `sanity/SanityManager.java` (solo la demora de alucinaciones).

- `ChoripanEntity` (perro, forma DOG, 0.5×0.6): sigue a la familia o al jugador (meta follow), mueve la cola, olfatea;
  poses `SIT, BEG, BELLY_UP, TILT, GROWL, BIPEDAL_180, SNEEZE, SLEEP`; look 0 suéter, 1 bufanda (final).
  **Avisa alucinaciones:** `SanityManager` demora cada alucinación 40 ticks y llama
  `ChoripanEntity.warn(ServerLevel, Vec3)`: el perro más cercano (≤24 bloques) gira y gruñe a ese punto.
  Le ladra a cualquier `HauntEntity` espectral a <10 bloques (cooldown).
- `ChoripanDemonEntity` (BEAST): **hitbox solo cabeza 0.8×0.8**, velocidad 0.36, persigue al jugador.
  - Cuerpo = cadena: eslabones `link_0..link_N` del modelo; el cliente guarda el historial de posiciones de la cabeza
    (por id de entidad, cada 0.25 bloques) y dibuja cada eslabón en el punto del historial a su distancia acumulada.
    Estado `UNSPOOL` (action): los eslabones salen de un **ancla** (puerta de la cucha, sincronizada como
    `BlockPos`/Vec3 en entity data) y la cola sigue adentro meneándose hasta que la cadena se estira entera.
  - "Sigue siendo un perro": un `ItemEntity` a <8 bloques lo distrae 3 s (va, lo olfatea). Una vez guionado:
    `fetch(ItemEntity, ServerPlayer)` lo trae, lo deja a los pies (pose `FETCH_DROP`), 3 s quieto, se lanza.
  - Sal: no cruza `SaltGuard` (navegación y teleports); contra la línea gime (`CHORIPAN_WHINE`).
  - Si el jugador tiene `CHORIZO_*` o `CHORIPAN*` en la mano a <6 bloques: pose `BEG` (sentado sobre los brazos).
  - Ataque: `LUNGE`; al pegar `Fx.jumpscare(p, "choripan_demonio")`, 4 de daño, −10 de cordura.
  - Agua bendita / crucifijo: `stun`. No va al frasco (`requiresExorcism` o rechazo del frasco).
  - `catchChoripan(ChoripanBenditoEntity)`: si un choripán bendito pasa a <2 bloques de la cabeza lo atrapa en el
    aire (pose `CATCH`, golpe de FOV vía `Fx.shake`), mastica 2 s, `VOMIT` (spawnea `DemonWisp`), `RETRACT`
    (la cadena se recoge con `CHORIPAN_METRO_RETRACT`) y se reemplaza por un `ChoripanEntity` temblando
    (`SNEEZE`). Postea `run.post("choripan:calmado")`.
- Modelos: `ent_choripan.py`, `ent_choripan_demonio.py`. **Animadores dependen de los modelos terminados.**

## P3 · Ítems: cadena del choripán, lata, chancleta

Archivos: `casa/CasaItems.java`, `casa/ChoripanBenditoEntity.java`, `casa/ChancletaEntity.java`,
`casa/GrillSpot.java`, recetas en `src/main/resources/data/deadline/recipe/` (`choripan.json`, `choripan_bendito.json`,
`chorizo_asado.json`), modelos/texturas de ítem (`tools/art/items.py`, bloque propio), `client/casa/CasaItemRenderers.java`.

- Ítems: `chorizo_crudo`, `chorizo_asado`, `pan`, `choripan`, `choripan_bendito` (arrojable, copia de
  `HolyWaterEntity`: al impactar sin atrapar, salpica y aturde 40 ticks), `lata_galletitas` (uso: se abre →
  `hilo_bendito` + `aguja` + `foto_1960`, mensaje "Nunca son galletitas"), `hilo_bendito`, `aguja`, `foto_1960`
  (texto `casa.foto`), `chancleta` (trofeo P2).
- Recetas de datos: `campfire_cooking` chorizo_crudo→chorizo_asado; `shapeless` pan+chorizo_asado→choripan;
  `shapeless` choripan+holy_water→choripan_bendito.
- `GrillSpot.cook(Run, ServerPlayer, BlockPos grill)`: clic derecho en la parrilla con chorizo crudo → 5 s de anillo
  de progreso (`Fx.bigText` con progreso o payload nuevo de P5) con `GRILL_SIZZLE` y humo; si el jugador sale de la
  línea de sal o se aleja >3 bloques, se corta. Al terminar reemplaza el chorizo por asado y postea
  `run.post("grill:cocido")`.
- `ChancletaEntity`: proyectil visual (ItemDisplay o thrown item) desde la Nona a Lucía/posición; al llegar
  `CHANCLETA_HIT`, aturde 60 ticks y postea `chancleta:hit`. API: `ChancletaEntity.throwFrom(Entity from, Entity to)`.

## P4 · Utilería y set pieces (Display entities)

Archivos: `casa/DemonWisp.java` (entidad), `casa/KnifeOrbit.java`, `casa/SaltHits.java`, `casa/DollShelf.java`,
`casa/YarnWeb.java`, `casa/CasaProps.java`, `casa/CasaSetEntities.java`.

- `DemonWisp` (entidad invisible sin modelo): recorre una curva (lista de puntos, Catmull-Rom) en N ticks soltando humo
  negro y brasas con `WISP_WHISTLE`; `DemonWisp.fly(ServerLevel, List<Vec3>, int ticks, Consumer<DemonWisp> onArrive)`;
  `hover(Vec3, int ticks)` (duda entre dos puntos); `enter(Entity)` (se mete en la boca: partículas hacia la cabeza).
- `KnifeOrbit`: 6 `ItemDisplay` de cuchillo levantados del rack (`KNIFE_LIFT`), orbitan alrededor de un actor; `launch(target)`
  lanza uno por vez (`KNIFE_WHOOSH`, 3 de daño si toca, `KNIFE_IMPACT` en bloque); si un cuchillo cruza una línea de sal
  cae (`ItemEntity`). `start(Run, Entity holder, BlockPos rack)`, `tick()`, `stop()`, `remaining()`.
- `SaltHits`: cuenta golpes de sal arrojada (`SaltItem` uso a <6 bloques mirando al actor, o puñado que impacta) sobre
  un actor; cada golpe `SALT_HIT_SCREAM` + `stun`; a los 3 postea `run.post("sal:3")`. Subtítulo `casa.cartel.sal`.
- `DollShelf`: las 10 muñecas del estante = `ItemDisplay` (o bloques del kit que rotan) que **giran a mirarte cuando no
  las mirás** (`DOLL_TURN`) y avanzan del estante al piso de a una; el jugador no puede mirar a la vez Ofelia y el estante.
  El flash de la cámara las congela 6 s. `start(Run, BlockPos shelf)`, `tick()`, `stop()`.
- `YarnWeb`: segmentos `BlockDisplay` de lana roja escalados (0.05, 0.05, L) entre anclas; tocar uno engancha 2 s y −8 de
  cordura (`YARN_TWANG`); se corta con la daga de plata o se quema con bengala (`YARN_SNAP`).
  `cast(ServerLevel, Vec3 from, List<Vec3> to)`, `clear()`.
- `CasaProps`: `chairTower(Run, String group, BlockPos base)` (cambia las 8 sillas por una torre de `BlockDisplay` mientras
  nadie mira; la de arriba se balancea), `levitate(Run, List<BlockPos>, int ticks)` (6-10 muebles flotan como
  `BlockDisplay`), `plateStorm(Run, Vec3 from, Vec3 to, int ticks)`, `mateSlide/termoFly` (ItemDisplay animados),
  `unseenSwap(Run, String actor, String point)` (mueve un actor solo cuando ningún cazador lo mira; acento `DOLL_TURN`),
  `doorCascade(Run, List<String> doors, int every)` y `bulbPop(Run, String group)`.

## P5 · UI: chat familiar, puntadas, nombre, spirit box

Archivos: `casa/CasaNet.java` (payloads), `client/casa/ChatScreen.java`, `client/casa/StitchOverlay.java`,
`client/casa/NameScreen.java`, `casa/Stitch.java`, cambios en `item/SpiritBoxItem.java` (solo el hook de preguntas
guionadas).

- **Chat familiar** (§3.10): `CasaNet.openChat(ServerPlayer, List<ChatMsg> history)` abre una pantalla de chat de
  WhatsApp-like (burbujas, horas, nombres; último mensaje de Lucía 29/09 03:07 "ya le saqué los hilos" sin respuesta).
  `CasaNet.liveMessage(ServerPlayer, ChatMsg)` agrega en vivo un mensaje de **número desconocido con el logo de DEAD LINE**:
  "ya llegó?" con `PHONE_NOTIFY`. Al cerrar, el cliente manda `chat:closed` → `run.post("chat:closed")`.
- **Puntadas**: `Stitch.step(int n)` = `Step` del director: mantener la mira en la boca de Ofelia 2 s (el servidor chequea el
  ángulo como `Run.looking`), el cliente muestra un anillo que se achica (`CasaNet.stitchRing(p, progress)`); si soltás la
  mira la puntada se suelta: sacudón, −10 de cordura, `STITCH_PULL` al revés. Éxito: `STITCH_PULL`.
- **Nombre** (P1): `CasaNet.askName(p)` → pantalla LEMAZA / AZAMEL / OFELIA; respuesta `name:<opcion>` como evento.
- **Spirit box guionada**: si el jugador está en el Run de la casa y el capítulo lo pide, la rueda de preguntas
  ("¿Cómo te llamás?", "¿Qué querés?", "¿Pagás el alquiler?", "¿Sos de Boca o de River?") responde con las líneas
  `casa.spirit.*`, y postea `spirit:<pregunta>`.

## P6 · Integración

Archivos: `DeadLine.java`, `DeadLineClient.java`, `caseload/CaseType.java` (casa → guionado, sitio `casa`),
`tools/models/build_all.py` (KEYS), `ClientSmoke.java` (capturas de la familia y Choripán), `README.md`.
Corre al final de las olas A y B.

## P7 · CasaScript

`director/casa/CasaScript.java`: 8 capítulos y 17 beats de la BIBLIA contra los marcadores de `tools/sites/casa.py`
(contrato de marcadores en `tools/workflows/casa_site.js`) y las APIs de P1-P5. Después: revisión de partida completa
(workflow de "playthrough review" como el del colegio) y arreglos.

## Olas

- **A (sin modelos):** P3, P4, P5 en paralelo.
- **B (con modelos terminados):** P1, P2.
- **C:** P6 + P7, luego revisión y CI.
