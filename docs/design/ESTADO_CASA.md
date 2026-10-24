# Estado del proyecto y traspaso (actualizado 23/10/2026, sesión 2)

Leer esto primero en una sesión nueva, después `docs/design/casa_terror.md` completo (diseño vigente, §11 contrato de
marcadores, §12 API del motor de terror). `BIBLIA.md` y `casa_mecanicas.md` quedan como historia: donde contradigan
a `casa_terror.md`, manda `casa_terror.md`.

## Reglas del dueño (no negociables)
- Foco 100% en **Casa Morales**. El **Colegio está EN PAUSA** (no tocarlo salvo que no compile).
- Terror adulto: sangre, deformaciones, jumpscares ganados, eventos aleatorios que empeoran. **Sin misiones**, sin HUD
  de objetivos, **sin voces ni diálogos** (solo mensajes de texto al celular y sonidos no verbales). Nada de comedia.
- La casa está en el **overworld real**; se llega en **auto**; golpeás la puerta y abre la Nona.
- **Sin cordura** (decisión del dueño, 24/10/2026): la mecánica se sacó entera (valor guardado, HUD/ECG, celular,
  pastillas, alucinaciones por cordura baja, `/deadline sanity`). Los sustos quedan igual; nada nuevo guarda ni lee
  un valor de cordura.
- Respuestas en español rioplatense, cortas, sin preguntas ni sugerencias al final.
- Uso: esfuerzo **extra** por defecto, como máximo 3 agentes a la vez; ultracode/workflows solo para la revisión final
  de la partida completa. Guardar trabajo de agentes en el repo seguido (el contenedor se reinicia).

## Reglas técnicas
- Rama de trabajo actual `claude/dead-line-casa-morales-7r65e8` (sale de `claude/intelligent-mayer-xknxxf`, mismo
  historial). Commits terminan con `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>` y la línea
  `Claude-Session:` de la sesión que los hace.
  Sin PR salvo pedido. Sin identificadores de modelo en commits ni código. Repo PÚBLICO: nunca subir fuentes
  descompiladas de Minecraft.
- **No hay compilador local** (maven bloqueado): el CI (`.github/workflows/build.yml`) compila al pushear. Logs con
  `mcp__github__get_job_logs(run_id, failed_only, return_content)`; el paso "ERRORS BEGIN/END" resume los errores.
  Verificar APIs contra el código del repo, `/tmp/ref/probe/api*.txt`, `/tmp/ref/mc_imports.txt`, `/tmp/ref/fabric-api`
  (si `/tmp/ref` no existe en una sesión nueva, el workflow `.github/workflows/probe.yml` + `tools/ci/probe.sh`
  imprime firmas de clases vanilla). Red: Maven Central y `raw.githubusercontent.com` andan (fuentes de Fabric API:
  `curl -s https://raw.githubusercontent.com/FabricMC/fabric-api/1.21.11/<ruta>`); maven de Fabric/Mojang y la descarga
  de logs zip de Actions están bloqueados.
- `export DEADLINE_WORK=<scratchpad>/work` para que renders y QA no caigan en `<repo>/.work`.
- Capturas in-game del CI: `tools/ci/decode_shots.py` (base64 en los logs del job cliente).
- Herramientas: modelos `tools/models` (`preview.py <key> [--pose]`, `build_all.py <key>`, ART_GUIDE.md); sitios
  `tools/sites` (`casa.py`, `walkcheck.py casa`, `siterender.py casa --point X`); sonidos `tools/audio` (`sounds_def.py`
  + `gen_defs.py`); textos `tools/data/lang.py` → `gen_data.py`.

## Hecho
- **Diseño v2** (`casa_terror.md`): actos 0–6 + final, 54 eventos, mecánicas, personajes, mensajes, contrato §11.
- **Motor de terror** `com.deadline.horror` (compila en CI): `HorrorEvent`, `Ctx`, `Haunt` (tensión/picos/calma,
  elección aleatoria), `HorrorEvents`, `HouseQuery`, `HorrorCommands` (`/deadline horror ...`; falta registrarlo en
  `DeadLine.java` con `CommandRegistrationCallback`).
- **Limpieza A1**: voces TTS borradas (`Run.say` no-op), llamadas → **mensajes** (`com.deadline.phone.PhoneMessages`:
  `text/photo/typing/offerCase/clear/textLater/photoLater/offerCaseLater`, app Mensajes en `PhoneScreen`, toast +
  vibración), Acto 0 de Marta llega solo 15 s después de entrar al mundo o con `/deadline msg casa`; mecánicas cómicas
  borradas (choripán bendito, parrilla, chancleta, chat, rueda, puntadas, lana, fuego fatuo).
- **A2 overworld + auto**: `OverworldSite`/`OverworldCase` (busca llanura a 150–400 bloques, nivela, coloca, guarda
  origen en `CaseSites`, noche fija, limpia monstruos), `com.deadline.car` (`CarEntity`: 4 asientos `seat(e,i)`,
  `radio(SoundEvent)`, faros J, radio R, bocina click medio; `car_keys`), GPS en el HUD, `CasaScript` placeholder
  (1 capítulo sin objetivos, postea `llegada` a 24 bloques del marcador). Commit `53d985c`: **CI sin verificar todavía**;
  puntos dudosos listados por el agente: overrides de `CarEntity` (addPassenger, positionRider, getRiddenInput, travel,
  onPassengerTurned, getDismountLocationForPassenger, makeBoundingBox...), `OverworldSite` (findClosestBiome3d,
  setChunkForced, hasChunk, randomState), `CarKeysItem.teleportTo`, `CarRenderer` (layer tipo EyesLayer),
  `CarSounds.canStartSilent`.
- **Casona v2** (`tools/sites/casa.py`, casi terminada): 2 plantas + altillo + sótano + cuarto 1961, dos escaleras,
  15 escondites, 116/116 marcadores alcanzables (11 sellados a propósito), según §11. Falta solo una pasada de revisión
  visual (renders día/noche) y exportar `casa.json` final.

## Sesión 2 (en curso)
- CI verde de nuevo (`976d300`: el culling del auto pasó a `CarRenderer.getBoundingBoxForCulling`).
- `HorrorCommands` registrado en `DeadLine.java`. `Director` postea `use:<puerta>` también en puertas trabadas (golpear).
- `CasaScript` real: un capítulo por acto (cap. n = acto n, cap. 7 = final; checkpoints por acto), transiciones por
  tiempo/lugar/sustos, mensajes de §8, `Haunt` con el acto y `tick()`, `Hunt` en el acto 5. Los set pieces son
  `HorrorEvent` scripted con id `sp_*` (`sp_perro_camino`, `sp_llegada`, `sp_cena`, `sp_a_dormir`, `sp_lucia_techo`,
  `sp_jorge_sonambulo`, `sp_ropero_toti`, `sp_nona_reza`, `sp_nona_se_rompe`, `sp_cuarto61`, `sp_final_auto`) y postean
  `cena:fin`, `a_dormir:fin`, `cuarto61:fin`, `final:fin`; si un set piece no existe, el acto usa una versión simple.
- **Casona cerrada** (pendiente 2): 4 ciclos de render, camas-escondite con faldón, máquina Singer, cuarto de huéspedes
  amueblado, cuarto 1961 con LEMAZA en tres paredes, ventana del Nono con luz (grupo `luces_cuarto_nono`); 11 bloques
  nuevos de kit; 116/116 marcadores; `casa.json` 52 KB. Renderer con puertas/escaleras: `<scratchpad>/work/../srender.py`
  (no versionado).
- **B3 hecho**: eventos 33–45 (`ApparitionEvents`, helpers en `horror/casa/Apparitions`), `ChoripanEntity` (poses STAND,
  GROWL...; looks normal/bufanda/muerto), `ChoripanDemonioEntity` + `PerroLargo.emerge/chase/crawl/retract`, `Choripan.spawn/
  standAt`, copias (`FamilyEntity.LOOK_COPIA`, `POSE_CORNER(_TURN)`), Lucía `ACT_CEILING(_RUN)`, `ACT_SIT`, `LOOK_NORMAL`.
- **Smoke de la Casa** (`horror/CasaSmoke`): contrato §11 + cada evento disparado con un `FakePlayer`; cualquier excepción
  en un evento (`Haunt.errors`) rompe el CI.
- **B2 hecho** (cacería: `horror/casa/hunt`), **B1a hecho** (poltergeist 1–32, `Interactables`, `FlyingProp`; limpieza
  `PoltergeistEvents.cleanup`), **B1b hecho** (sangre 46–51, celular 52–53, linterna 54, `BloodDecals`, documentos de lore).
- **C hecho** (set pieces `sp_*` en `horror/casa/setpiece/**` + `SetPieces.java`): llegada, cena muda, a dormir, Lucía en
  el techo, Jorge sonámbulo, ropero de Toti, la Nona reza, la Nona se rompe, cuarto 1961 (cabezas 180°, Ofelia, la Nona en
  el techo, loop P.T. del pasillo PB ×2, la puerta ahora abierta) y el final en el auto (espejo retrovisor). Falta: foto
  final con la skin del jugador (`final_familia` sigue siendo placeholder).
- **Cordura eliminada** por decisión del dueño (manager, HUD, pastillas, alucinaciones por cordura, payloads, comando). Los
  sonidos que quedaron pasaron de `sanity.*` a `horror.*` (`ModSounds.HORROR_HEARTBEAT/FOOTSTEPS/KNOCK/BREATH`).
- Pendiente anotado (no empezar sin pedido del dueño): resource pack de interfaz (inventario, hotbar, botones) con
  estética del mod; el probe del CI ya lista tamaños y `.mcmeta` de `textures/gui` vanilla (`tools/ci/probe-assets.txt`).

## Revisión final (sesión 2)
Arreglado (compila en sintaxis; nada probado en juego todavía):
- **Flujo**: puertas traseras y balcón trabados en actos 1–2; portones del terreno cerrados con llave en actos 3–6 y
  abiertos al amanecer; la puerta del acto 2 se traba recién cuando todos los cazadores del terreno pasaron el umbral.
  Watchdogs que re-arman `cuarto61`, `final:auto` y la cacería. El acto 6 empieza tras despertar de la segunda captura.
  El acto 4 dura hasta terminar sus set pieces y "Escóndase" (tope 9 min). Los textos de la historia llegan a todos.
- **Final**: DEAD LINE + tarjeta de créditos (`deadline.casa.creditos`) antes de cerrar el caso; la luz de arriba queda
  prendida. El "CASO RESUELTO +$" suena después de los créditos (no se agregó el `returnHome` silencioso).
- **Multijugador**: si se va uno de varios cazadores, `Haunt.stopFor(p)` corta solo sus eventos y `Hunt.letGo(p)` lo
  saca del escondite y le limpia el HUD; el que se une toma el capítulo de la noche (`stage`), y tras un reinicio el
  capítulo sale del máximo `stage` de los cazadores online.
- **Sustos**: los jumpscares del acto 6 y de Lucía son incondicionales; `detras_hombro` toma el bloqueo de 3 min solo si
  la cara aparece. La linterna (clic) y salir de un escondite (15) son ruido que la Nona oye. El perro largo es el set
  piece `sp_perro_largo` (`horror/casa/dog/SpPerroLargo`), disparado por `CasaScript` a los 3 min de cacería cerca de
  la cucha, o al principio del acto 6 si no salió. El tablero eléctrico solo se rearma en el acto 4.
- `sombra_cruza`, `puerta_lenta` y `lucia_techo_corre` apuntan a la boca del vano (`Apparitions.doorway`); desde un
  pasillo la sombra cruza el pasillo. `huellas` busca la habitación a 1–3 bloques del vidrio; `linterna_muere` mira las
  lámparas del cuarto y el cielo en vez de la luz del propio haz. GPS oculto a menos de 64 bloques. Sin pista en el
  celular para la Casa. CI: captura extra `casa_js_nona_rota_wall` (la cara contra una pared, NEAR 0.35).

A verificar en juego (incierto): que los 6 eventos que el smoke no ubicó (`sombra_cruza`, `lucia_techo_corre`,
`lampara_fondo`, `mecedora`, `huellas`, `linterna_muere`) ahora encuentren lugar; que `sp_perro_largo` llegue a salir
(depende de pasar cerca de la cucha); el ritmo del acto 4 sin tope de intensidad aleatoria (no se aplicó `capOverride`);
salir/entrar de cazadores a mitad de set piece; que el tiempo vuelva a correr al terminar (no se dejó el amanecer fijo).

## Pendiente (en orden)
1. ~~CI verde~~ (hecho).
2. **Cerrar la casona**: revisar renders (`siterender.py casa --point living|hall|pasillo_1p|cuarto61|patio`), corregir
   lo que se vea mal, exportar.
3. **B2 cacería** y **B3 apariciones/perro/copias**: el brief exacto de cada uno está en `tools/workflows/casa_b2_b3.js`
   (constantes `B2` y `B3`). Se cortaron por un reinicio casi al principio: solo quedaron `tools/models/ent_mano.py` y
   `ent_sabana.py` empezados. Relanzar como agentes sueltos (esfuerzo extra), no como workflow.
4. **B1 poltergeist + actos**: eventos 1–32 y 46–54 del catálogo, interactuables (§6.3), `FlyingPropEntity` (§6.4),
   sangre (§6.5), documentos de lore, y el `CasaScript` real: actos 0–6 con `Haunt.of(run).act(n)`, transiciones por
   tiempo/lugar/sustos, mensajes de §8, llamar `Haunt.of(run).tick()` en `tick(run)`, `Haunt.forget(run)` al salir.
5. **C set pieces**: llegada (golpear, la Nona abre, la puerta se traba), cena muda, Lucía en el techo, Jorge sonámbulo,
   la Nona se rompe (inicio de la cacería), descenso al sótano, cuarto 1961, final en el auto (foto + la Nona en el
   asiento de atrás).
6. Revisión completa de la partida (acá sí workflow/ultracode), capturas CI, pulido.
