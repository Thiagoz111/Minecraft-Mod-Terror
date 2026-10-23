# Estado del proyecto y traspaso (24/10/2026)

Leer esto primero en una sesión nueva, después `docs/design/casa_terror.md` completo (diseño vigente, §11 contrato de
marcadores, §12 API del motor de terror). `BIBLIA.md` y `casa_mecanicas.md` quedan como historia: donde contradigan
a `casa_terror.md`, manda `casa_terror.md`.

## Reglas del dueño (no negociables)
- Foco 100% en **Casa Morales**. El **Colegio está EN PAUSA** (no tocarlo salvo que no compile).
- Terror adulto: sangre, deformaciones, jumpscares ganados, eventos aleatorios que empeoran. **Sin misiones**, sin HUD
  de objetivos, **sin voces ni diálogos** (solo mensajes de texto al celular y sonidos no verbales). Nada de comedia.
- La casa está en el **overworld real**; se llega en **auto**; golpeás la puerta y abre la Nona.
- Respuestas en español rioplatense, cortas, sin preguntas ni sugerencias al final.
- Uso: esfuerzo **extra** por defecto, como máximo 3 agentes a la vez; ultracode/workflows solo para la revisión final
  de la partida completa. Guardar trabajo de agentes en el repo seguido (el contenedor se reinicia).

## Reglas técnicas
- Rama `claude/intelligent-mayer-xknxxf`; commits terminan con
  `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>` y `Claude-Session: https://claude.ai/code/session_01C2PSZfs8x2BhoyHGNbsV9v`.
  Sin PR salvo pedido. Sin identificadores de modelo en commits ni código. Repo PÚBLICO: nunca subir fuentes
  descompiladas de Minecraft.
- **No hay compilador local** (maven bloqueado): el CI (`.github/workflows/build.yml`) compila al pushear. Logs con
  `mcp__github__get_job_logs(run_id, failed_only, return_content)`; el paso "ERRORS BEGIN/END" resume los errores.
  Verificar APIs contra el código del repo, `/tmp/ref/probe/api*.txt`, `/tmp/ref/mc_imports.txt`, `/tmp/ref/fabric-api`
  (si `/tmp/ref` no existe en una sesión nueva, el workflow `.github/workflows/probe.yml` + `tools/ci/probe.sh`
  imprime firmas de clases vanilla).
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

## Pendiente (en orden)
1. **CI verde** del commit del auto/overworld (arreglar errores de compilación).
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
