# DEAD LINE — Shared Systems Design v1
**Systems covered:** the Director, Voice Mimic (Simple Voice Chat), Poltergeist, Possession and Choripán, Dialogue/Subtitles, Live Chat and Tapes
**Target:** Fabric 1.21.11 · Java 21 · Mojang mappings · Fabric API 0.141.6
**Cases:** COLEGIO (La Monja) · CASA (La Muñeca + family + Choripán) · HOSPITAL (El Streamer)

Grounding: this design is based on the current repo (`CaseManager`, `SiteBuilder`, `HauntEntity`, `Fx/FxPayload`, `SanityManager`, `FlashlightLights`, `HauntModel/HauntRenderer`, `ClientAmbience`, `tools/audio`). I checked the Simple Voice Chat facts in its source (`henkelmax/simple-voice-chat`, branch `1.21.11`, mod `1.21.11-2.6.24`, API `2.6.24`). I could not check Minecraft facts against a local jar, so I marked them **(verify with probe)**. Those should be confirmed with `tools/ci/probe.sh` before coding.

---

## 0. Resumen para el creador (ES)

- **Director de escenas.** Cada susto es un "beat" con nombre. Se dispara solo cuando entrás a un lugar, mirás algo, pasa un tiempo, usás un ítem o tu cordura baja. También lo podés disparar vos con un comando o con F6–F9. Si un amigo co-protagoniza, puede manejar los sustos desde una "tablet de director".
- **Garantía de cámara.** Los sustos grandes solo pasan si los estás mirando, para que queden grabados. Los cambios del tipo "algo se movió cuando no mirabas" solo pasan cuando no mirás, y cuando lo descubrís suena un golpe musical.
- **Tomas repetibles.** `/deadline take reset` reconstruye el lugar idéntico. `/deadline take chapter 3` salta a un capítulo. El mod guarda un CSV con la hora exacta de cada susto, grito y muerte, y un botón **F10 = CLIP** para marcar momentos. El editor encuentra todo en segundos.
- **Imitación de tu voz (Simple Voice Chat).** El mod graba en memoria, nunca en disco, lo que decís mientras jugás. Después las entidades lo repiten:
  - la muñeca con voz de nena;
  - la monja al revés en el confesionario;
  - Choripán con voz demoníaca;
  - los parlantes del hospital con efecto radio;
  - un "coro" hecho con tus propias voces.
- **La llamada de consentimiento es parte del juego.** Al empezar, la operadora te pide permiso para grabar ("por calidad espiritual"), tu nombre y que digas "acepto el caso". Más tarde, algo te llama **por tu nombre con tu propia voz**.
- **"Te roban la voz".** Cuando la monja te agarra, tu amigo deja de escucharte y tu voz sale de la boca de la monja.
- **Mecánica "SILENCIO" en el colegio.** Si hablás fuerte o gritás, Sor Agonía te escucha y viene. Con Choripán transformado es al revés: si le hablás despacito ("¿quién es un buen chico?") se calma unos segundos.
- **Poltergeist de verdad:**
  - platos que orbitan y cuchillos que te apuntan y se clavan en la pared marcando tu silueta;
  - sillas que se apilan cuando no mirás;
  - puertas que se cierran de golpe;
  - luces que se apagan una por una hacia vos;
  - teles con estática;
  - mensajes que se escriben solos con sangre o tiza.
- **Posesiones de la familia.** El demonio salta de un familiar a otro y se ve la "chispa" viajando. La abuela poseída te sigue ofreciendo mate.
- **Choripán:**
  1. es detector de fantasmas (les ladra) y te roba el libro de rituales para guiarte;
  2. hace una transformación falsa que termina en estornudo;
  3. después viene la transformación real, con el perro "reventando" desde adentro;
  4. la bestia conserva el collar "CHORIPÁN".
- **Hospital:**
  - el celular del streamer sigue EN VIVO, con chat que reacciona a vos: "ATRÁS", "se cagó jajaja", donaciones con voz robótica;
  - cámaras de seguridad estilo FNAF donde te ves a vos mismo caminando;
  - cintas VHS de la última transmisión.

---

## 1. Design principles (why this films well)

1. **On-camera guarantee.** Every set piece can carry an `observed(marker)` gate, so it fires only when the target is in the player's view cone with line of sight. Its counterpart is `unobserved(...)`, which applies changes only off camera and plays a **discovery stinger** the first time the player looks at the change.
2. **Rhythm over volume.** The cycle is dread → scare → laugh → lull. A per-player tension meter gates ambient beats and schedules comedy relief after spikes.
3. **Everything can be filmed again.** Each case has a deterministic site seed, plus retake, chapters and named beats. A clip-marker CSV syncs to the video with a slate flash.
4. **The creator stays in control.** Every beat can be fired by command, hotkey, or the Director Tablet (for a co-star "puppeteer").
5. **The server is authoritative and the client stays cheap.** Hard budgets apply to props, light updates, displays and threads (§13).
6. **Optional dependencies degrade gracefully.** Without Simple Voice Chat (SVC), the mod falls back to TTS and resource-pack-overridable sounds. Nothing crashes, and no class references SVC outside one package.

---

## 2. Architecture overview

### 2.1 Packages
```
com.deadline.site        SiteMarkers, Marker, SiteState (SavedData), Actors, SiteKey
com.deadline.director    CaseScript, ScriptBuilder, Beat, Trigger*, Cond*, Step*, StepRunner, Director, Directors,
                         SiteContext, SiteEvent, Where, Who, TensionMeter, Chapters, TakeService
com.deadline.dialogue    Speaker, Speakers, DialogueLines (GENERATED), DialogueService, BarkPool, PhoneCalls
com.deadline.voice       VoiceBridge (no SVC types), NoVoiceBridge, VoiceConfig, MimicRequest, MimicIntent, Emitter,
                         VoiceFx, StealMode, SpeechEvent, NoiseMeter
com.deadline.voice.svc   DeadLineVoicechatPlugin, SvcVoiceBridge, VoiceRecorder, VoiceTrack, Utterance, VoiceAnalyzer,
                         ClipSelector, MimicScheduler, Playback, LiveSteal, dsp/{PitchShifter, Resampler, Reverb,
                         Biquad, Reverse, Stutter, Layer, Limiter}           <-- ONLY place importing de.maxhenkel.*
com.deadline.polter      Poltergeist (facade), PropManager, Prop, PropSpec, Motion*, PropCollision, DoorFx, DoorLocks,
                         LightGroups, FixtureBlock, TvBlock, BlockLoops, WallWriter, UnseenSwap, HauntActivity
com.deadline.npc         FamilyNpcEntity, NpcVariant, NpcState, Routine, PossessionComponent, Demon, HostBehaviour*,
                         ChoripanEntity, ChoripanForm, ActorSwap
com.deadline.stream      LiveChatService, ChatRule, ChatMood, Donation, StreamCameraItem, Tapes, Tape, TapeCue,
                         CctvCameraEntity, DoppelgangerEntity
com.deadline.mixin       (new COMMON mixin config) DisplayInvoker, BlockDisplayInvoker, ItemDisplayInvoker, TextDisplayInvoker
client: hud/SubtitleHud, hud/LiveChatHud, hud/NoiseHud, screen/DirectorTabletScreen, screen/TapeScreen,
        screen/CctvScreen, cine/CameraDirector (look-pull, camera entity switch, letterbox, dolly),
        BlockLoopSounds, ClientTakeLog, render/FamilyRenderer, render/PossessionLayer, render/ChoripanRenderer,
        render/DoppelgangerRenderer
```

### 2.2 Tick wiring (`DeadLine.onInitialize`)
```java
ServerTickEvents.END_SERVER_TICK.register(server -> {
    CaseManager.tick(server); SanityManager.tick(server); FlashlightLights.tick(server);
    Directors.tick(server);        // beats, sequences, tension, ambient pool
    Poltergeist.tick(server);      // prop kinematics, flicker patterns, unseen swaps, writers
    VoiceBridge.get().drainServerEvents(server); // speech start/end → NoiseMeter, Director (thread hop)
    LiveChatService.tick(server);  // chat rules (every 10 ticks)
});
UseBlockCallback.EVENT  → DoorLocks / Director.post(Interact)      UseItemCallback.EVENT  → Director.post(ItemUse)
UseEntityCallback.EVENT → Director.post(InteractActor)             ServerLifecycleEvents.SERVER_STOPPING → VoiceBridge.stopAll()
```

### 2.3 Threads
```
MC server thread ──── Director / Poltergeist / NPC AI / decides WHAT and WHEN to mimic
      ▲ server.execute(...)                       │ MimicRequest (immutable snapshot)
      │                                           ▼
"deadline-voice" (1 thread)  decode+VAD+segment   "deadline-mimic" (1 scheduled thread, 20 ms)
      ▲ ConcurrentLinkedQueue                        pre-render DSP, encode, channel.send(...)
SVC voice-server thread → MicrophonePacketEvent (O(1) enqueue; may cancel() for voice steal)
```

### 2.4 Data ownership
- **`HunterData`** (player attachment, persisted). Add `voiceConsent` (bool) and `star` (bool).
- **`ActiveCase`** (persisted). Add `seed` (long) and `chapter` (int).
- **`SiteState`** (SavedData per case dimension). Holds markers, actor UUIDs, fired beats, flags, demon state and lock sets.
- **Transient only, never saved:** running sequences, props in motion and voice buffers. They are cleaned on case end and server stop.

---

## 3. Foundation changes to existing code

### 3.1 Site markers (extend `SiteBuilder`)
Sites already build in site-relative coordinates, so scripts reference names, never coordinates.
```java
public record Marker(String id, Kind kind, Vec3 pos, @Nullable AABB box, Direction facing, List<BlockPos> blocks, String group) {
    enum Kind { POINT, AREA, DOOR, FIXTURE, TV, PROP, ACTOR, CAMERA, SPEAKER, WRITE_SURFACE }
}
// new SiteBuilder helpers (all register a marker and, where relevant, place blocks):
protected void marker(String id, double x, double y, double z)
protected void area(String id, int x0, int y0, int z0, int x1, int y1, int z1)          // rooms, triggers
protected void door(String id, int x, int y, int z, Block door, Direction f, boolean open) // overload of existing door()
protected void fixture(String group, int x, int y, int z, FixtureBlock.Kind kind)        // light in a group
protected void tv(String id, int x, int y, int z, Direction f, TvBlock.Channel ch)
protected void prop(String id, BlockState|Item what, double x, double y, double z, PropSpec spec)
protected void actor(String id, EntityType<?> type, double x, double y, double z, float yaw)
protected void camera(String id, double x, double y, double z, float yaw, float pitch)    // CCTV
protected void speaker(String group, double x, double y, double z)                         // PA / intercom
protected void writeSurface(String id, double x, double y, double z, Direction facing)     // walls, blackboards
```
`Layout` gains a `SiteMarkers markers` field. `CaseManager.startCase` stores the markers in `SiteState` and spawns `actor(...)` entries, recording `actorId → UUID`. Actor spawning is generalised from today's `extras`, which remains as is.

### 3.2 `SiteState` (SavedData, per case dimension)
```java
public final class SiteState extends SavedData {   // TYPE = new SavedDataType<>("deadline_site_state", ...), like CaseSites
  Map<Integer, Record> sites;
  public static final class Record {
    SiteMarkers markers; Map<String, UUID> actors; Set<String> fired; Map<String, Integer> flags;
    Map<String, Long> cooldownUntil; Set<BlockPos> lockedDoors; DemonState demon; int chapter; long takeStartTick;
  }
}
```

### 3.3 Deterministic sites and retakes
- `SiteBuilder.build(level, origin, RandomSource.create(seed))` replaces `level.getRandom()`. The `seed` is stored in `ActiveCase`.
- `CaseManager.restartSite(ServerPlayer)` is used by `/deadline take reset`. It runs these steps in order:
  1. Run `cleanupSite`, extended to remove displays and NPCs tagged `deadline:site/<n>`.
  2. Re-run the builder with the same seed.
  3. Reset the `SiteState.Record`.
  4. Respawn the boss, anchor and actors.
  5. Teleport hunters to the spawn point or chapter marker.
  6. Emit a SLATE take event.

### 3.4 `Spectral` interface (holy tools work on possessed hosts)
Today `CrucifixItem`, `HolyWaterEntity`, `CameraItem`, `SpiritBoxItem`, `EmfItem` and `SpiritJarItem` query `HauntEntity`. Introduce:
```java
public interface Spectral {
    boolean spectralActive();                                 // HauntEntity: true; FamilyNpc: possessed; Choripán: UNEASY/BEAST
    void onHoly(HolySource src, @Nullable ServerPlayer by, float power); // CRUCIFIX, HOLY_WATER, DAGGER, FLASH, RITE
    default boolean jarable() { return false; }
    default float emfStrength() { return 1f; }
}
```
`HauntEntity implements Spectral` by mapping onto its existing `stun` and holy-damage path, so its behaviour does not change. The tools switch to `level.getEntities(holder, box, e -> e instanceof Spectral s && s.spectralActive())`. This is a minimal, mechanical diff.

### 3.5 `CaseType` for the three cases
`COLEGIO("colegio", …, ColegioSite::new, MONJA, INVERTED_ROSARY, ColegioScript::new)`, `CASA("casa", …, MoralesHouseSite::new, …, CasaScript::new)`, `HOSPITAL("hospital", …, HospitalSite::new, …, HospitalScript::new)`.

Add a `Supplier<CaseScript> script`. `ConventSite` becomes `ColegioSite` (a religious girls' school). The cut cases are removed from `values()`, but their classes can stay for now. The `CaseManager` progress hooks (`onAnchorPurified`, `onBossWeakened`, `onBossBanished`) forward to `Director.post(...)`. A script can then add conditions: for example, CASA is not solved until every host is freed.

---

## 4. The Director (scripted-event framework)

### 4.1 Concepts
- **Beat:** a named unit, `"<case>.<name>"`, made of a trigger, conditions, a repeat policy, a scope, targeting, priority, tags and a body (Step).
- **Step:** an executable node, which may be a nested sequence, parallel block, wait, or action.
- **Director:** one instance per `(CaseType, siteIndex)` while at least one hunter is inside. It evaluates polled triggers, receives `SiteEvent`s and advances running sequences.

### 4.2 Triggers
| Trigger | Kind | Notes |
|---|---|---|
| `enter(area)` / `exit(area)` / `inside(area, ticks)` | polled every 2 ticks | AABB contains the player's feet |
| `lookAt(target, maxDeg=20, minTicks=10, maxDist=32, los=true)` | polled every 2 ticks, staggered | target is a marker, actor or area. LOS uses `level.clip` to the target centre (and to box corners for areas) |
| `notLooking(target, ticks)` | polled | precondition for off-camera changes |
| `time(since=CASE_START or FLAG or BEAT, ticks)` | polled | |
| `sanityBelow(x)`, `stage(>=n)`, `flag(name op value)`, `near(actor, d)`, `holding(item)`, `dark(lightBelow)` | polled | |
| `itemUse(item [, area])`, `interact(marker or actor)`, `doorUse(marker)` | event | Fabric `Use*Callback` |
| `voice(minDb, minMs)`, `silence(ms)`, `scream()` | event | from VoiceBridge speech events (§6.10). Without SVC, `noise(>= x)` from movement is used instead |
| `entity(actor, WEAKENED / BANISHED / POSSESSED / FREED / STUNNED / TRANSFORMED)` | event | |
| `anchorPurified()`, `playerDamaged()`, `playerDied()`, `beatDone(id)` | event | |
| `cue(slot)` | event | hotkey, command or tablet |
| `all(...)`, `any(...)` | composite | |

### 4.3 Modifiers
- `once()` (default) / `oncePerPlayer()` / `repeat(cooldownTicks [, maxFires])`
- `scope(SITE or PLAYER)`
- `chance(p)`
- `requires(flag...)`
- `gate(tensionBelow(30))`
- `observed(target)` / `unobserved(target)`
- `priority(n)`: a higher-priority beat can `interrupt` lower-priority running sequences tagged `interruptible`
- `tags("scare", "comedy", "ambient", "setpiece", "chapter:3")`

### 4.4 Steps (actions)
| Group | Steps |
|---|---|
| Flow | `seq`, `par` (wait for all), `race`, `wait(t)`, `waitUntil(cond, timeout)`, `random(weights…)`, `ifElse`, `loop(n or until)`, `call(beatId)` |
| State | `flag(name, v)`, `stage(n)`, `hint(key)`, `evidence()`, `chapter(n)` |
| FX (reuse `Fx`) | `sound(ev, where, vol, pitch)`, `loop(ev, where)` / `stopLoop`, `shake`, `flash`, `redFlash`, `static`, `fade`, `jumpscare(key)`, `title(key)`, `hallucination(kind)`, `particles(...)`, **new:** `lookPull(where, strength, ticks)`, `dolly(ticks)`, `letterbox(on)`, `brownout(ticks)` |
| Dialogue | `say(speakerOrActor, lineId)`, `bark(actor, pool)`, `phoneCall(callerId, lines…)` |
| Voice | `mimic(intent, emitter, fx [, tag])`, `steal(who, mode, ticks, thiefActor)` |
| Poltergeist | `door(marker, OPEN/CLOSE/SLAM/LOCK/UNLOCK/KNOCK/RATTLE)`, `lights(group, OFF/ON/FLICKER(pattern, ticks)/CHASE(order, delay)/BLACKOUT(ticks))`, `tv(marker, channel)`, `lift(propOrBlock)`, `levitate(props, h, ticks)`, `orbit(props, center, r, speed)`, `aim(props, who)`, `throwAt(props, who, speed)`, `stack(props, at)`, `drop(props)`, `write(surface, text, font, speed)`, `swapUnseen(area, rule)` |
| Actors | `spawn(actorId, type, marker)`, `despawn`, `teleport`, `walkTo(actor, marker, speed)`, `face(actor, who)`, `anim(actor, actionId, ticks)` (sets `HauntEntity.ACTION` / NPC action), `possess(npc, SUBTLE or FULL)`, `free(npc)`, `demonJump(to)`, `choripan(form)`, `swap(actorId, newType)` |
| Stream | `chat(user, textKey)`, `chatCue(pool, n, spread)`, `chatMood(mood, ticks)`, `donate(user, amount, textKey, lineId)`, `viewers(n)`, `tape(id)` |
| Take | `clipMark(note)` |

`Where`:
- `marker(id)`
- `actor(id)`
- `player(BEHIND(d) | LEFT_EAR | RIGHT_EAR | ABOVE | AHEAD(d))`
- `randomIn(area)`
- `speakers(group)`

`Who`:
- `TRIGGERER`
- `STAR` (the protagonist; see §4.8)
- `ALL_IN_SITE`
- `ALL_IN(area)`
- `NEAREST(marker)`

Each step declares a **tension weight**: jumpscare 40, slam 15, mimic 20, levitate 10, whisper 5, bark −10 (comedy lowers tension).

### 4.5 DSL (Java; compiled and type-checked, validated in CI)
```java
public final class ColegioScript extends CaseScript {
  @Override protected void define(ScriptBuilder s) {
    s.chapter(1, "Llegada", "spawn");
    s.beat("colegio.pizarron")
      .when(Trig.lookAt("pizarron_aula3", 25, 15)).observed("pizarron_aula3").once().tags("setpiece")
      .run(Steps.seq(
         Steps.lights("aula3", Light.flicker("mmamammmmammamamaaamammma", 60)),
         Steps.write("pizarron_aula3", "No debo hablar en clase.\nNo debo hablar en clase.", Font.CHALK, 3),
         Steps.wait(20),
         Steps.write("pizarron_aula3", "\nTE ESCUCHÉ, {player}.", Font.CHALK, 5),
         Steps.sound(ModSounds.AMBIENT_STINGER, Where.marker("pizarron_aula3"), 1.5f, 0.8f),
         Steps.mimic(MimicIntent.ECHO, Emitter.marker("pasillo_b"), VoiceFx.WHISPER_IN_HEAD)));
    s.beat("colegio.pupitres")
      .when(Trig.inside("aula3", 100)).unobserved("aula3_pupitres").once()
      .run(Steps.swapUnseen("aula3_pupitres", SwapRule.faceToward(Who.TRIGGERER)));   // + discovery stinger
    s.beat("colegio.silencio")
      .when(Trig.voice(-28f, 400)).requires("en_capilla").repeat(200)
      .run(Steps.seq(Steps.say("sor_agonia", "monja.shh.1"), Steps.anim("sor_agonia", MonjaEntity.ACT_HUNT, 0)));
    s.cue(1, "colegio.pizarron"); s.cue(2, "colegio.coro");
  }
}
```

### 4.6 Runtime
```java
public final class Director {
  final SiteKey key; final CaseScript script; final SiteContext ctx; final SiteState.Record rec;
  final List<RunningSeq> running = new ArrayList<>(); final Map<UUID, TensionMeter> tension; boolean paused;
  void tick();                                             // stagger polled triggers (½ per tick), advance sequences
  void post(SiteEvent e);                                  // event triggers
  FireResult fire(String beatId, @Nullable ServerPlayer target, boolean force); // commands/cues bypass conds if force
  void cancelAll(boolean restore);                         // take reset / case end (lights back on, props settle)
}
final class RunningSeq { StepInstance root; ServerPlayer target; String beatId; boolean interruptible; }
interface StepInstance { boolean tick(SiteContext c); void cancel(SiteContext c); } // returns true when done
```
- **Sequences are not persisted.** A `once` beat is marked fired when it starts, so a server restart never repeats a set piece.
- **Multiplayer.** `scope(PLAYER)` beats evaluate per hunter. The `STAR` target lets the friend in spectator mode never be the victim.

### 4.7 Pacing (tension and ambient)
- **`TensionMeter` per player (0–100).** It rises with step weights, damage and sanity loss, and decays 1 per second (0.5 per second while the player is in darkness).
- **Ambient pool.** The ambient pool holds beats tagged `ambient`: creaks, door creak, cup falls, chair scoot, a whisper, a light blink. The Director picks one by weighted random when:
  - tension is below 35;
  - the time since the last beat exceeds `density.gap`;
  - the beat's room is near the player, weighted by `HauntActivity` heat.
- **Comedy relief.** After a spike above 70 decays below 40, the Director schedules the best available `comedy` beat (a family bark, a Choripán gag, a chat joke) within 10–20 seconds.
- **Density presets** (`/deadline director density`): CALM gap 60 s, NORMAL 35 s, HIGH 20 s, INSANE 10 s.

### 4.8 Creator controls
```
/deadline beat list [filter]                 ✔ fired · ◷ cooldown · ● armed · ▶ running (suggestions list beat ids)
/deadline beat fire <id> [player] [force]    /deadline beat reset <id|all>    /deadline beat arm|disarm <id>
/deadline director pause|resume|status|density <calm|normal|high|insane>
/deadline cue <1-9>                          /deadline star <player>      (scares target the protagonist)
/deadline take start|slate|mark [note]|reset|chapter <n>|goto <marker>
/deadline say <speaker> <lineId>             /deadline npc possess|free <actor> · /deadline choripan <form>
/deadline polter <slam|flicker|blackout|throw|levitate|orbit|stack|write|tv> <marker…>
/deadline mimic optin|optout|status|clear|tag last <tag>|play <intent> [at <marker|actor|player>]|steal <player> <ticks> [mode]
/deadline chat say <user> <text>|mood <m>|donate <user> <amount> <text>|viewers <n>      /deadline tape play <id>
```
- **Cue hotkeys.** F6–F9 (rebindable) send a C2S `CuePayload(slot)`. The server requires permission level 2.
- **Director Tablet** (key K, operators only). A non-pausing screen styled like the phone with two tabs:
  - **Beats:** grouped by chapter, with a FIRE button, state icons and cue slots.
  - **Live:** each hunter's sanity, tension and noise; the last 10 beats; the mimic clip count per player with PLAY (ECHO / CALL / SCREAM); a STEAL VOICE button.

  It sends `DirectorActionPayload`. This lets a friend in spectator mode act as the puppeteer.

### 4.9 Takes, chapters, slate, clip markers
- **Chapters.**
  - `s.chapter(n, name, spawnMarker, setup)`: `setup` sets flags, marks earlier beats as fired, positions actors and sets possession or Choripán form.
  - `/deadline take chapter 4` jumps straight to "Choripán se transforma".
- **Slate.** `/deadline take slate` shows a 1-second white flash with a 1 kHz beep and the title "TOMA 3". The editor aligns the CSV to the video at that frame.
- **`ClientTakeLog`** (written client-side, so it works in singleplayer and multiplayer). The server sends `TakeEventPayload(kind, id, note)`, and F10 adds `CLIP`. The log is written to `<gameDir>/deadline/takes/<yyyy-MM-dd_HH-mm-ss>.csv`:
  ```
  wall_clock_iso,ms_since_slate,game_tick,player,kind,id,note
  2026-10-20T21:14:03.120,754310,183200,Thiago,BEAT,casa.mesa_cuchillos,
  2026-10-20T21:14:05.880,757070,183255,Thiago,SCREAM,,peak=-4.1dB len=1.9s
  2026-10-20T21:15:40.002,851192,185138,Thiago,CLIP,,
  ```
  Kinds: SLATE, BEAT, JUMPSCARE, MIMIC, SCREAM (from VAD), DEATH, SANITY_LOW, CHAPTER, CLIP. A `chapters.txt` in YouTube `mm:ss Title` format is also emitted.

### 4.10 CI validation (extend `SmokeTest`)
For every case, on the dedicated-server smoke run:
1. Build the site.
2. Instantiate the script and assert that every marker, actor and line id referenced exists.
3. Fire every beat with `force` on a Fabric `FakePlayer`, then tick 400 ticks and assert no exceptions.
4. Assert that the prop and display budgets are respected.

---

## 5. Dialogue, subtitles, barks, phone calls

### 5.1 Data and pipeline (`tools/audio/lines_def.py` → generator)
```python
VOICES = {   # Kokoro es voices: ef_dora, em_alex, em_santa  + DSP chain from dsp.py
  'madre':      dict(kokoro='ef_dora',  speed=1.00, semis=0,  chain=['room_small']),
  'padre':      dict(kokoro='em_alex',  speed=0.97, semis=-1, chain=['room_small']),
  'abuela':     dict(kokoro='ef_dora',  speed=0.85, semis=-2, chain=['tremolo_old', 'room_small']),
  'lucia':      dict(kokoro='ef_dora',  speed=1.05, semis=+4, chain=['room_small']),
  'sor_agonia': dict(kokoro='ef_dora',  speed=0.85, semis=-3, chain=['whisper_layer', 'chapel_reverb']),
  'demonio':    dict(kokoro='em_santa', speed=0.90, semis=-5, chain=['octave_down_layer', 'saturate', 'reverb_big']),
  'streamer':   dict(kokoro='em_alex',  speed=1.15, semis=+1, chain=['usb_mic', 'compressor']),
  'donacion':   dict(kokoro='em_alex',  speed=1.05, semis=0,  chain=['robot_tts_2000s']),   # "Loquendo-like" parody
  'operadora':  dict(kokoro='ef_dora',  speed=1.00, semis=0,  chain=['phone_band']),
  'pa':         dict(kokoro='ef_dora',  speed=0.95, semis=0,  chain=['pa_horn', 'slap_120ms']),
}
LINES = {  # id: (speaker, es_AR, en_US, opts)
  'casa.madre.saludo.1': ('madre', 'Ay, gracias a Dios que vino. Pase, pase... y límpiese los pies.', 'Oh thank God...', {}),
  'casa.padre.canerias.1': ('padre', 'Son las cañerías. Esta casa es vieja, nada más.', "It's the pipes.", {'bark': 'polter_near'}),
  'monja.shh.1': ('sor_agonia', 'Shhh... en mi colegio no se habla.', 'Shhh...', {}),
}
```
The generator produces:
- `sounds/line/<id>.ogg`, registered as `deadline:line.<id>` in `sounds.json` with **no vanilla subtitle**;
- lang keys `deadline.line.<id>` in `es_ar` (copied to `es_*`) and `en_us`;
- **`DialogueLines.java`** (common), containing `LineDef(id, speaker, durationTicks, byte[] envelope10Hz)`. The envelope drives lip flap.

**Overrides:** when `tools/audio/voice_overrides/<id>.wav` exists, the creator's or friends' real recording replaces the TTS and gets the same DSP chain. Use this for comedic lines, because Kokoro has a neutral or Spain accent and cannot deliver rioplatense comic timing.

### 5.2 Runtime
- **`Speaker`** registry: id, name key, ARGB colour, style (NORMAL, WHISPER = grey italic, DEMON = red jitter, PHONE = phone icon, STREAM = platform icon, PA = speaker icon, TV, MIMIC = "[tu voz]"), and phone avatar index.
- **`DialogueService.say(ctx, source, lineId, audience)`:**
  - Plays an **entity-bound** sound (`SoundSource.VOICE`, the `ClientboundSoundEntityPacket` path, e.g. `ServerLevel#playSeededSound(null, entity, holder, …)`) **(verify with probe)**, so the voice follows the moving speaker.
  - Sends `SubtitlePayload(lineId, speakerId, durationTicks, entityId, flags)` to listeners within 24 blocks, or to the phone target.
  - Keeps a per-speaker queue (no overlap); screams interrupt.
- **Lip flap.** The client keeps `ClientDialogue.active[entityId] = (lineId, startTick)`. The renderer reads the envelope and opens the `jaw` bone accordingly.
- **Barks.** `BarkPool(id, lines[], cooldown, chance, cond)` subscribes to `SiteEvent`s (PropThrown, DoorSlam, LightsOut, PlayerScream, PlayerHitNpc, ChoripanBark). For example, the father within 10 blocks of a flying plate says "Son las cañerías". This is the comedy engine.
- **`SubtitleHud`.**
  - Bottom centre at `h - 68`, at most 60% of screen width, 3 lines stacked.
  - Speaker name in its colour; text revealed at `elapsed / duration * 1.15`; fades 10 ticks after the line ends.
  - A ◀/▶ arrow appears when the speaker is off-screen.
  - Toggle with `/deadline subtitles` or the config. Default on, because burned-in subtitles help TTS clarity.
- **In-case phone calls.** `PhoneCalls.ring(player, callerId, lines…)` reuses `INCOMING_CALL`. When answered, lines play with the `phone_band` preset and render as chat bubbles in `PhoneScreen`. Example: the streamer's mother calls mid-case.

---

## 6. Voice mimic with Simple Voice Chat (optional dependency)

### 6.1 Verified facts (SVC source, branch 1.21.11, API 2.6.24)
- **Plugin discovery.** On Fabric, SVC loads plugins via `FabricLoader.getEntrypointContainers("voicechat", VoicechatPlugin.class)`.
- **`VoicechatPlugin`:** `getPluginId()`, `initialize(VoicechatApi)`, `registerEvents(EventRegistration)`. Priority: higher runs first.
- **`MicrophonePacketEvent`:**
  - `getPacket()` gives `getOpusEncodedData()` and `isWhispering()`; `getSenderConnection().getPlayer().getUuid()` identifies the speaker.
  - It is **cancellable**: a cancelled packet is not relayed to other players.
  - It fires on SVC's voice-server thread, not the Minecraft thread.
- **Audio format:** Opus at **48 kHz mono, 20 ms frames = 960 samples**. When a player stops talking, the client sends an **empty packet** (`byte[0]`).
- **Channels:**
  - `createLocationalAudioChannel(UUID, ServerLevel, Position)` and `createEntityAudioChannel(UUID, Entity)`;
  - `createStaticAudioChannel(UUID)` plus `addTarget(connection)`;
  - `send(byte[] opus)`, `flush()`, `setCategory(String)`, `setDistance(float)`.

  A locational channel broadcasts to **all** players in range, including the original speaker, so the creator hears his own voice.
- **Encoder and decoder:**
  - `createEncoder(OpusEncoderMode.VOIP)`: `encode(short[960]) → byte[]`.
  - `createDecoder()`: `decode(byte[]) → short[]`; `decode(null)` gives packet-loss concealment.
- **`createAudioPlayer(channel, encoder, Supplier<short[]>)`** spawns **one thread per player** with 20 ms pacing and closes the encoder at the end. We avoid it and use one shared scheduler instead (§6.8).
- **Volume category:** `registerVolumeCategory(volumeCategoryBuilder()...)`. The id must be `[a-z_]` and at most 16 characters (`deadline_mimic` is valid). The icon must be 16×16 ARGB.
- **Singleplayer works.** The integrated server runs the voice server when the client config `run_local_server` is true, which is the default.
- **`AudioSender`** (fake a player's mic) works **only for players without the mod**, so it is not useful here.

### 6.2 Gradle and `fabric.mod.json`
```groovy
repositories {
    maven { name = "henkelmax"; url = "https://maven.maxhenkel.de/repository/public"
            content { includeGroup "de.maxhenkel.voicechat" } }
    exclusiveContent { forRepository { maven { name = "Modrinth"; url = "https://api.modrinth.com/maven" } }
                       filter { includeGroup "maven.modrinth" } }
}
dependencies {
    compileOnly "de.maxhenkel.voicechat:voicechat-api:${voicechat_api_version}"   // plain Java-8 interfaces, no remap
    if (findProperty("svc_dev") == "true") modLocalRuntime "maven.modrinth:simple-voice-chat:${svc_dev_version}"
}
```
- **`gradle.properties`:** `voicechat_api_version=2.6.24`. This is the API version the 1.21.11 branch publishes; any 2.6.x works, because we only use long-stable methods. Set `svc_dev_version` to the Modrinth version id of the 1.21.11 Fabric build (look it up).
- **Sandbox note:** this agent sandbox's proxy blocks `maven.maxhenkel.de` and Modrinth with 403, while GitHub Actions can reach them. CI builds normally. For offline builds, `-PnoVoicechat` should `sourceSets.main.java.exclude 'com/deadline/voice/svc/**'` and drop the entrypoint in `processResources`.

```json
"entrypoints": {
  "main": ["com.deadline.DeadLine"], "client": ["com.deadline.client.DeadLineClient"],
  "voicechat": ["com.deadline.voice.svc.DeadLineVoicechatPlugin"]
},
"suggests": { "voicechat": "*" }
```
**Class-loading rule:** nothing outside `com.deadline.voice.svc` may import `de.maxhenkel.*`. If SVC is absent, nobody requests the `voicechat` entrypoint, so the plugin class is never loaded. The game code talks only to `VoiceBridge`.

### 6.3 Classes
```java
// com.deadline.voice  (always present)
public interface VoiceBridge {
  static VoiceBridge get();                       // volatile INSTANCE, default NoVoiceBridge
  boolean available();                            // SVC server running
  boolean consented(UUID p); int clipCount(UUID p);
  OptionalLong play(MimicRequest r);              // empty -> caller uses fallback (NoVoiceBridge does it itself)
  void stop(long id); void stopAll();
  void steal(UUID p, StealMode mode, int ticks, @Nullable Entity thief);
  boolean speaking(UUID p); float loudnessDb(UUID p);      // last 200 ms
  void tagLast(UUID p, String tag); void clear(UUID p);
  void drainServerEvents(MinecraftServer s);      // delivers SpeechEvents on the MC thread
  void addListener(VoiceListener l);
}
public record MimicRequest(UUID source, MimicIntent intent, @Nullable String tag, Emitter emitter, VoiceFx fx,
                           float distance, @Nullable Predicate<ServerPlayer> audience, @Nullable Entity animateSpeaker) {}
public sealed interface Emitter { record At(ServerLevel l, Vec3 p) implements Emitter {}  record Follow(Entity e) implements Emitter {}
                                  record InHead(ServerPlayer listener) implements Emitter {} record Speakers(ServerLevel l, List<Vec3> ps) implements Emitter {} }
public enum MimicIntent { CALL, ECHO, SCREAM, WHISPER, CHOIR, QUOTE }
public enum StealMode { MUTE, REDIRECT, POSSESSED }
public record VoiceFx(float semis, float speed, boolean reverse, int stutter, float octaveLayer, float reverb,
                      Band band, float gainDb) {   // presets:
  DRY, CHILD(+5), DOLL(+7, reverb .2), DEMON(-5, octave .6, sat), BACKWARDS(reverse, reverb .5), RADIO(band 300-3400 + clip),
  PA(band + slap 120ms + reverb .4), WHISPER_IN_HEAD(hp 900, -10 dB), CHOIR(3 layers ±3/±7 semis, delays 0/90/170 ms, reverb .7), SLOWMO(speed .75)
}
// com.deadline.voice.svc  (only with SVC)
DeadLineVoicechatPlugin, SvcVoiceBridge, VoiceRecorder, VoiceTrack, Utterance, VoiceAnalyzer, ClipSelector,
MimicScheduler, Playback, LiveSteal, dsp.*
```
```java
public final class DeadLineVoicechatPlugin implements VoicechatPlugin {
  private SvcVoiceBridge bridge;
  @Override public String getPluginId() { return DeadLine.MOD_ID; }
  @Override public void initialize(VoicechatApi api) { bridge = new SvcVoiceBridge(api); VoiceBridge.install(bridge); }
  @Override public void registerEvents(EventRegistration r) {
    r.registerEvent(VoicechatServerStartedEvent.class, e -> bridge.onServerStarted(e.getVoicechat())); // registers category
    r.registerEvent(VoicechatServerStoppedEvent.class, e -> bridge.onServerStopped());
    r.registerEvent(MicrophonePacketEvent.class, bridge::onMic, 100);   // high priority: we may cancel (steal)
    r.registerEvent(PlayerDisconnectedEvent.class, e -> bridge.forget(e.getPlayerUuid()));
  }
}
// SvcVoiceBridge.onMic — runs on SVC thread; must be O(1), never touch the world
void onMic(MicrophonePacketEvent e) {
  VoicechatConnection c = e.getSenderConnection(); if (c == null) return;
  UUID id = c.getPlayer().getUuid();
  byte[] opus = e.getPacket().getOpusEncodedData();
  LiveSteal st = steals.get(id);
  if (st != null && st.active()) { e.cancel(); st.forward(opus); }          // §6.9
  if (consent.contains(id)) recorder.ingest(id, opus, e.getPacket().isWhispering(), System.nanoTime());
}
```
`consent` is a `ConcurrentHashMap.newKeySet()` mirrored from `HunterData.voiceConsent`. It is updated on the Minecraft thread at join, opt-in and opt-out.

### 6.4 Threads and safety
- **SVC thread:** consent check, append to the ring (the `VoiceTrack` monitor) and an `analysisQueue.offer` only.
- **`deadline-voice` executor** (single thread, daemon): per-player `OpusDecoder` (stateful, decoded in order), VAD, segmentation and statistics. It posts `SpeechEvent`s to a queue that the Minecraft thread drains each tick.
- **`deadline-mimic`** (`ScheduledExecutorService`, 1 thread, `scheduleAtFixedRate(…, 20, MILLISECONDS)`):
  - Each run advances every active `Playback` by one frame. Late runs catch up, which SVC's jitter buffer tolerates.
  - Per-playback `OpusEncoder` is closed on finish, followed by `channel.flush()`.
- **Minecraft thread** creates channels, resolves `Emitter → Position or Entity` (`api.fromEntity`, `api.createPosition`, `api.fromServerLevel`), and updates moving locational emitters via `updateLocation`.
- All maps are `ConcurrentHashMap`. Nothing on the voice threads calls Minecraft world methods.

### 6.5 Recording and memory limits
```java
final class VoiceTrack {                 // per consenting player, guarded by 'this'
  final ArrayDeque<Frame> open;          // frames of the utterance being spoken
  final ArrayDeque<Utterance> clips;     // closed utterances, newest last
  long bytes; long lastNanos; int noiseFloorDb10;
}
record Frame(byte[] opus, long nanos, short rmsDb10) {}
final class Utterance { int id; byte[][] frames; long startNanos; float meanDb, peakDb, loudRatio;
                        boolean whisper, rising, contaminated; Set<String> tags; int uses; long lastUsedNanos; }
```
| Limit (config) | Default | Why |
|---|---|---|
| `maxUtterances` per player | 48 | selection quality vs memory |
| `maxBytesPerPlayer` | 1.5 MB | about 3–6 minutes of speech at SVC's VOIP bitrate (frames are about 60–120 bytes) |
| `maxTotalBytes` | 24 MB | hard global cap |
| `maxUtteranceMs` / `minUtteranceMs` | 6000 / 350 | longer utterances are split at the quietest point; shorter ones are useless |
| `retention` | CASE | cleared on `returnHome`, case failure, disconnect and server stop. SESSION is optional |

Eviction removes the oldest **untagged** utterance first. Tagged clips (`name`, `acepto`, creator tags) survive until `clear`. Audio is **never written to disk**.

### 6.6 Segmentation and analysis (`deadline-voice` thread)
For each frame:
1. Decode it with the player's decoder and compute RMS in dBFS.
2. Track the noise floor (fast fall, slow rise). The threshold is `max(-45, floor + 10)` dB.
3. Run the state machine:
   - IDLE → SPEECH when a frame is above the threshold.
   - SPEECH → HANG when below.
   - HANG → **close** when the hang exceeds 280 ms.
   - An empty packet or an arrival gap over 220 ms also **closes** the utterance.
4. Trim sub-threshold edges, keeping 40 ms of padding.
5. Compute statistics: mean and peak dB; `loudRatio` (frames above −14 dBFS); whisper flag.
6. Compute the **rising** flag: autocorrelation F0 over the last 300 ms against the utterance median, rising when above +15% (good for "¿Hola?").
7. Set **contaminated** if any of our playbacks was audible to that player during the utterance. This avoids feedback loops on speakers, and those clips are never mimicked.
8. Emit `SpeechEvent(start, durationMs, meanDb, peakDb, loudRatio, ongoing)`. A live "speaking now" event is emitted every 200 ms while speech continues.

The cost is about 0.1 ms per frame (decode plus statistics), or about 5 ms of CPU per second per talking player, all off-thread.

### 6.7 Clip selection (`ClipSelector`, called on the Minecraft thread; O(48))
| Intent | Duration | Age window | Prefers | Default FX |
|---|---|---|---|---|
| CALL (lure) | 0.5–2.5 s | 45 s – 15 min | tags `call`/`name`, `rising`, normal loudness | DRY + room reverb |
| ECHO (instant repeat) | ≤ 3 s | ≤ 12 s | newest | DRY, 0.3 s delay |
| SCREAM | 0.4–3 s | ≥ 20 s | highest `loudRatio`/peak | DEMON or DRY |
| WHISPER | 0.5–3 s | ≥ 30 s | quiet or `whisper` | WHISPER_IN_HEAD |
| CHOIR | 3–5 clips | any | variety | CHOIR (layered) |
| QUOTE | — | — | an exact tag | caller-chosen |

The score combines duration fit, an age bell curve for the intent, loudness for the intent, novelty `1 / (1 + uses)`, tag match and rising. Contaminated clips, or clips younger than the intent's minimum age, score −∞. The selector picks randomly among the top 3 (weighted) so repeats do not feel mechanical.

### 6.8 Playback and DSP
- **Pass-through (DRY, no FX):** stored Opus frames go straight to `channel.send(frame)` every 20 ms. There is no quality loss and no encode cost.
- **Processed:**
  1. On the mimic thread, before start, decode the whole clip (at most 6 s, about 288k samples).
  2. Run the DSP chain on that PCM.
  3. Re-encode it in 960-sample chunks with a per-playback `OpusEncoder(VOIP)`.
- **DSP chain:** whole-buffer and simple, at 48 kHz.
  - `PitchShifter`: granular OLA, 40 ms Hann grains, 10 ms hop; pitch changes and duration is kept.
  - `Resampler`: tape slow or fast.
  - `Reverse`.
  - `Stutter`: repeat the last 180 ms n times ("ho-ho-hola").
  - `Layer`: octave-down mix.
  - `Biquad`: HP, LP and band-pass.
  - `Reverb`: Freeverb-lite with 4 combs and 2 all-pass filters.
  - `Limiter` at −1 dBFS.
- **Channels:**
  - One channel per emitter, `setCategory("deadline_mimic")`, distance 24–48.
  - `Follow` uses `createEntityAudioChannel(UUID.randomUUID(), api.fromEntity(e))`.
  - `At` uses a locational channel.
  - `Speakers` (PA) uses N locational channels fed the same frames, so it costs one encode.
  - `InHead` uses `createStaticAudioChannel(id)` plus `addTarget(api.getConnectionOf(uuid))`.
- **Visual sync.** If `animateSpeaker` is set, the Minecraft thread sets that entity's speaking state, so the jaw flaps from loudness. It sends `SubtitlePayload` with style MIMIC: "[tu voz]". Each `PLAYBACK` writes a MIMIC take event.
- **Concurrency cap:** 4 playbacks, plus 1 live steal per player.

### 6.9 "Te roban la voz" (live steal)
- **MUTE:** cancel the event. The friend cannot hear you, the chat says "no te escuchamos".
- **REDIRECT:** cancel and forward the raw Opus to the thief's `EntityAudioChannel`. Your live voice comes out of the nun or dog, with no added latency.
- **POSSESSED:** cancel, then for each frame decode → streaming `PitchShifter(-5)` + `Layer` → encode → thief channel.
  - This needs a stateful streaming DSP per player and about 0.3 ms per frame on the SVC thread.
  - Optional `echoToSelf` (config `allowEchoToSelf`, **default false**) also plays it back to you. You then hear your own voice delayed by about 60–120 ms, which makes speaking hard (a funny, uncanny "I can't talk" moment). Headphones only.
- `steal` ends automatically after `ticks`. `forward` calls `channel.flush()` on end.

### 6.10 Voice activity as gameplay (works partially without SVC)
- **`NoiseMeter`** per player (0–100):
  - Speech adds `(dB + 40) * k` per frame; screams add a big bump.
  - Sprinting, jumping, door use and dropped props add noise even without SVC.
  - It decays 8 per second.
  - `NoiseHud` shows a small waveform icon next to the ECG, only in COLEGIO.
- **COLEGIO "SILENCIO":** `MonjaEntity` gets a `HearingGoal`. When noise exceeds 55 within 40 blocks, the nun navigates to the noise position, a "Shhh…" bark plays, and a chat cue fires if stream mode is active.
- **CASA / Choripán BEAST:** soft speech (−40 to −25 dB for 2 s or more within 6 blocks) gives a calm window: stun 40 ticks, whimper, tail wag, then a 30 s cooldown. Yelling enrages him (speed +20% for 5 s). Fallback without SVC: sneak within 4 blocks.
- **HOSPITAL chat:** 45 s of silence triggers "¿se le cortó el mic?"; a scream triggers "JAJAJA el grito", "CLIPEEN ESO".
- **Clip markers:** every SCREAM goes into the take log with its peak level.

### 6.11 Fallback (no SVC, no consent, or no usable clip)
`NoVoiceBridge.play()` maps the intent to sound events: `deadline:mimic.fallback.call | echo | scream | name | laugh`, each with 4 Kokoro `em_alex` variants ("¿Hola? ¿Hay alguien?", "Vení, por acá", "¡Ayudame!"). These go through the same FX chain, rendered offline in `tools/audio`. They play as vanilla positional sounds at the emitter, with the subtitle "(una voz parecida a la tuya)".

**Resource-pack override:** the creator can drop his own recordings into a pack that overrides those `sounds.json` entries. That gives the "his voice" effect even without SVC.

### 6.12 Consent, privacy, config
- **Opt-in by default** (`voice.requireOptIn=true`). Each player, including a co-star friend, consents separately.
- **Diegetic consent call** (first case of the session):
  - The operator says: "Esta llamada puede ser grabada para garantizar la calidad espiritual del servicio. ¿Acepta?" and the phone shows [ACEPTO] / [NO ACEPTO] (`ConsentPayload`).
  - If he accepts: "Diga su nombre después del tono…" records an utterance tagged `name`, and "Ahora diga: 'acepto el caso'" records one tagged `acepto`. This guarantees clean, predictable clips for the big payoffs.
  - `/deadline mimic optin|optout` also works.
- **Disclosure:** a small red "● VOZ" in the phone status bar and HUD corner while recording in a case.
- **Never persisted:** audio lives in RAM only. It is cleared per retention policy, and `/deadline mimic clear` wipes it.
- **`config/deadline/server.json`** (Gson, created on first run):
```json
{ "voice": { "enabled": true, "requireOptIn": true, "retention": "CASE", "maxUtterances": 48,
             "maxBytesPerPlayer": 1572864, "maxTotalBytes": 25165824, "mimicDistance": 32,
             "allowSteal": true, "allowEchoToSelf": false, "maxConcurrentPlaybacks": 4 },
  "director": { "density": "NORMAL", "autoBeats": true, "cueSlots": 9 },
  "stream": { "chat": true }, "takes": { "log": true } }
```

### 6.13 Who uses the voice, and when
| Case | Moment | Intent / Emitter / FX |
|---|---|---|
| Prologue | consent call | records `name` and `acepto` |
| COLEGIO | confessional: the voice behind the grille | QUOTE `acepto` / At(confesionario) / BACKWARDS; then ECHO DRY |
| COLEGIO | chapel climax: "coro" of the student ghosts | CHOIR / Speakers(capilla) / CHOIR |
| COLEGIO | intercom roll call ends with your name | QUOTE `name` / Speakers(intercom) / PA |
| COLEGIO | Sor Agonía grabs you | steal REDIRECT, or POSSESSED when sanity < 20 |
| CASA | the doll repeats what you just said | ECHO / Follow(muñeca) / DOLL |
| CASA | a possessed family member says your line | CALL / Follow(npc) / DRY → uncanny |
| CASA | Choripán beast: "¿Quién es un buen chico?" (fallback TTS) or your scream | SCREAM / Follow(choripán) / DEMON |
| HOSPITAL | the PA system broadcasts "¿Hola? ¿Hay alguien?" in your voice | CALL / Speakers(pa) / RADIO |
| HOSPITAL | behind a locked door: "¡Abrí, soy yo!" | CALL tag `call` / At(door) / DRY |
| HOSPITAL | doppelgänger on CCTV and in the final corridor | QUOTE `name` / Follow(doppel) / DRY |
| Multiplayer | the friend's voice lures the creator into a dark room | CALL (source = friend) / At(room) / DRY |
| Ending | back home, the phone rings with your own voice | QUOTE `acepto` / InHead / RADIO (phone) |

---

## 7. Poltergeist system (server-driven, performance-safe)

### 7.1 Tiers (cheapest first)
1. **Block-state effects:** doors, barrels opening, trapdoors, fixture lights, TV channels, painting or portrait swaps. These cost no entities.
2. **Display props:** vanilla `BlockDisplay`, `ItemDisplay` and `TextDisplay`, moved kinematically by the server with client interpolation and no physics ticking. Used for levitation, orbiting, aiming, thrown objects and wall writing.
3. **`FallingBlockEntity`** only for cosmetic debris (gravel or plaster falling from the ceiling). It auto-places blocks and cannot rotate, so it is not used for furniture.

### 7.2 Display props
- **Common mixin config** `deadline.mixins.json` (environment `*`). Invokers on the private setters; Mojang names **(verify with probe: `net.minecraft.world.entity.Display#p | set`)**:
  - `Display`: `setTransformation`, `setTransformationInterpolationDuration`, `setTransformationInterpolationDelay`, `setPosRotInterpolationDuration`, `setViewRange`, `setBillboardConstraints`, `setShadowRadius`, `setBrightnessOverride`.
  - `BlockDisplay`: `setBlockState`.
  - `ItemDisplay`: `setItemStack`, `setItemTransform`.
  - `TextDisplay`: `setText`, `setBackgroundColor`, `setTextOpacity`, flags.
- **Interpolation gotcha.** Re-triggering a transform interpolation requires the "start delay" data entry to be re-sent. Vanilla forces that sync when set. Verify, and if needed force it with `entityData.set(accessor, value, true)` through an accessor.
- **`Prop` = Display + `PropSpec` + `Motion`:**
  - `PropSpec`: radius, damage, onHit (SHATTER / STICK / BOUNCE_SETTLE), break sound, particle, `homeBlock`.
  - Displays are tagged `deadline:prop` and `deadline:site/<n>` for cleanup.
  - BlockDisplay pivots at its corner, so translate by (−0.5, −0.5, −0.5) inside the transform to spin around the centre.
- **Smoothness:** `posRotInterpolationDuration = 2`, with the position updated every tick. Spin is set every 4 ticks with transformation interpolation 4.
- **`PropManager.lift(BlockPos)`:** reads the block state, sets air, and spawns an identical BlockDisplay at that spot. The real chair starts to float, which looks seamless. **Settle** places a real block back at the nearest free spot, so displaced furniture stays displaced.

### 7.3 Motions and collision
`Motion` implementations: `Rest`, `Hover(amp, freq, spin)`, `Rise(h, ticks)`, `Orbit(center, r, ω, heightWave)`, `Aim(who, jitter)` (knives point at the player and shiver), `Throw(v0, g, spin)`, `Path(spline, ticks)` (gurney or wheelchair rolling), `Fall`, `Stuck`.

For a thrown prop, each tick from `p0` to `p1`:
- **Blocks:** `level.clip(new ClipContext(p0, p1, COLLIDER, NONE, CollisionContext.empty()))`.
- **Players:** within 16 blocks, `player.getBoundingBox().inflate(radius).clip(p0, p1)`.
- **Player hit:**
  - Damage through a data-driven damage type `deadline:poltergeist` with funny death messages ("recibió un platazo del más allá").
  - Knockback, `Fx.shake` + `redFlash`, sanity −5.
  - `SiteEvent.PropHit`, which fires barks and chat.
- **Block hit:**
  - SHATTER (plates, frames): particles + sound, then remove.
  - STICK (knives): orientation from velocity, Motion=Stuck, stays. Knives can outline the player on the wall.
  - BOUNCE_SETTLE (chairs): damped bounce, then settle.

### 7.4 Prop catalogue
Custom 3D item models (JSON cube elements generated by `tools/art`, at most about 24 elements each): `prop_plato`, `prop_taza`, `prop_cuchillo`, `prop_tenedor`, `prop_cuadro_familia`, `prop_cuadro_cruz`, `prop_regla` (the nun's ruler), `prop_biblia`, `prop_osito`, `prop_control_tv`, `prop_silla_ruedas`, `prop_suero`, `prop_camilla`, `prop_ring_light`, `prop_lata_energizante`.

Furniture is lifted from real blocks: stairs (chairs), slabs, barrels, lanterns, flower pots, candles. Portrait textures can be **animated item textures** (`.mcmeta`), so painted eyes shift every few seconds.

### 7.5 Doors (`DoorFx`, `DoorLocks`)
- **OPEN/CLOSE:** `DoorBlock#setOpen(entity, level, state, pos, open)` (public).
- **SLAM:** close + `deadline:door.slam` at volume 2 + shake for players within 10 + dust particles.
- **KNOCK:** sound one block behind the door.
- **RATTLE:** rapid open and close over 6 ticks.
- **LOCK:** `UseBlockCallback` returns FAIL for locked positions, plus a rattle sound and the bark "Está trabada".
- Barrels and trapdoors flap as cupboard doors (they have an OPEN state).

### 7.6 Lights (`FixtureBlock`, `LightGroups`)
- **Our own blocks** avoid redstone-lamp neighbour-update bugs: `ceiling_bulb`, `fluorescent_tube` (hospital), `chandelier`, `candelabra` (school chapel), `desk_lamp`.
- Each has `LEVEL` (IntegerProperty 0–15) with `lightLevel(s -> s.getValue(LEVEL))`, which gives **real dimming**. Unlit and lit textures switch at LEVEL 0.
- **Patterns:**
  - Quake-style strings (`'a'` = 0 … `'z'` = 15), stepped every 2 ticks.
  - `CHASE(order, delay)`: corridor lights go out one by one toward the player.
  - `BLACKOUT(ticks)`: everything off, then restored.
  - The cancel or restore step always relights.
- **Budgets:** at most 10 fixture state changes per tick and at most 8 fixtures flickering at once. A client-only `BROWNOUT` Fx (HUD darkening flicker) adds stutter without relighting.
- **Existing behaviour stays:** the flashlight flicker near haunts.

### 7.7 TVs, monitors, loop sounds
- **`TvBlock`:** `HORIZONTAL_FACING` + `CHANNEL` enum (OFF, STATIC, TELENOVELA, FACE, LUCIA, COLOR_BARS, TEXT_VETE, STREAM). Each channel has a block model whose screen texture is animated (`.mcmeta`), and light 6 when on. Example: the FACE channel is static with a face fading in for 2 frames out of 40.
- **Hospital:** `MonitorBlock` (CRT; channels STATIC / STREAM_OVERLAY / CAM_LABEL) and `EkgBlock` (`BPM` enum: OFF, 60, 100, 160, FLAT).
  - EKG BPM is driven by distance to the nearest Spectral, which makes monitors an in-world detector.
  - Flatline means something is right here.
- **`BlockLoops`:**
  - The server sends `LoopPayload(pos, soundId, on)`.
  - The client plays an `AbstractTickableSoundInstance` at that position, checks the block state every 10 ticks, and stops itself if the state changed.
  - Used for TV hiss, telenovela murmur, the music box, EKG beeps and radio.

### 7.8 Writing on walls (`WallWriter`)
- **`TextDisplay` setup:** billboard FIXED, yaw from the `writeSurface` facing, background `0x00000000`, no shadow, `lineWidth` 200, scale 1.5–3 via transformation.
- **Reveal:** letter by letter, appending text every N ticks (one metadata packet each) with a scratch or squelch sound per glyph.
- **Bitmap fonts** (glyph atlases generated by `tools/art`, including Ñ Á É Í Ó Ú ¿ ¡):
  - `assets/deadline/font/blood.json`: drippy red;
  - `chalk.json`: blackboard;
  - `scrawl.json`: scratched into hospital walls.

  Applied with `Style#withFont(…)` **(1.21.11 takes a font description object; verify with probe)**.
- **UV-only messages:** `textOpacity` starts low. `FlashlightLights.update` (already raycasting in UV mode) calls `WallWriter.revealNear(hitPos)`, which sets opacity to 255 for 60 ticks and then fades. Fits the existing UV handprints.
- **Tokens:** `{player}` (name), `{caller}`.

### 7.9 Unseen swaps and discovery stingers (`UnseenSwap`)
- **Registration:** a change is registered as block states in an area, an entity repositioned, a portrait swapped, or a desk re-facing (`SwapRule.faceToward(who)`).
- **Application:** it applies when no hunter has had the area within a 100° cone with line of sight (sampled over corners and centre) for at least N ticks.
- **Discovery:** `onFirstSeen` plays a low stinger and writes a take marker exactly when the player first looks at the change.
- **Uses:**
  - school desks turned toward you;
  - chairs stacked on the table (a nod to the Poltergeist film);
  - the Mother Superior's portrait now empty;
  - Lucía's doll sitting in a different chair.

### 7.10 `HauntActivity` (ambient poltergeist)
- **Site level (0–1)** rises with case stage, time, noise (yelling provokes it), and proximity to the anchor. **Room heat** comes from area markers.
- **Feeds the Director's ambient pool:** cup slides off and falls, a barrel opens, a chair scoots (small display nudge plus scrape), a 1 s flicker, the TV turns to static, the music box plays, footsteps upstairs, the doll's head turns.
- **Existing code:** `PoseidaEntity.poltergeist()` is refactored to call this facade.

### 7.11 Budgets and cleanup
- **Per site:**
  - at most 48 Display props (at most 10 in Throw at once);
  - at most 12 `TextDisplay`s;
  - at most 2 `FallingBlock`s airborne;
  - props more than 48 blocks from every hunter freeze (no updates).
- **Cleanup:** `cleanupSite` and take reset remove entities tagged `deadline:site/<n>` and restore locked doors and lights.

---

## 8. Possession system (family NPCs)

### 8.1 `FamilyNpcEntity extends PathfinderMob implements Spectral`
- **Synced data:** `VARIANT` (MADRE, PADRE, ABUELA, LUCIA, plus any extra), `STATE`, `POSSESSION` (float 0–1), `ACTION`, `KO_TICKS`.
- **Attributes:** health 40, speed 0.25 calm and 0.34 possessed. `setPersistenceRequired`.
- **Damage rule:** invulnerable to non-holy damage. Hitting a calm NPC gives the bark "¡Oiga! ¿Qué le pasa?" and the take kind NPC_HIT, a comedy beat.
- **Calm goals:**
  - `NpcRoutineGoal`: waypoints from markers with idle actions (cooking, sofa watching TV, knitting, mate).
  - `LookAtPlayerGoal`.
  - `NpcFleeSpectralGoal`.
  - `NpcFollowHunterGoal` when SCARED.
- **Talk:** `mobInteract` triggers `DialogueService.say` from a topic pool keyed by state, flags and chapter.

### 8.2 States and `PossessionComponent`
`CALM → SCARED → UNEASY → TRANSITION → POSSESSED ⇄ STUNNED → FREED(KO) → CALM`
```java
final class PossessionComponent { float grip; NpcState state; int stateTicks; HostBehaviour behaviour;
  void begin(Mode m);             // SUBTLE: UNEASY (possession 0.1–0.3); FULL: runs transition sequence
  void tick();                    // ramps POSSESSION, drives behaviour
  void onHoly(HolySource s, float power) { grip -= power * k(s); stun(s); if (grip <= 0) free(); }
}
```
- **UNEASY foreshadowing:** repeats the same line twice; stares at a corner; a 2-tick eye glow; nosebleed particle; the voice is slightly pitched.
- **Holy tools:**
  - The crucifix stuns.
  - Holy water costs 25 grip.
  - **Short rite:** a ritual book chant for 3 s or more nearby drains grip continuously, reusing the `chant()` pattern from `PoseidaEntity`.

### 8.3 `Demon`: host hopping (state in `SiteState`)
- **Fields:** `hostActorId`, `queue`, `anger`.
- **`jump(to)`:**
  - A visible "wisp" travels from host to host over 20–30 ticks: server `sendParticles` along a curved path (`WISP`, `DEMON_SMOKE`) plus a whoosh.
  - The lights in rooms it passes flicker.
  - Then `possess(to, FULL)`.
- **When freed, the demon goes to the next host,** or to the doll (anchor) if the queue is empty.
- **Case integration:** while hosts remain, `onAnchorPurified` and the final exorcism are blocked by script conditions.

### 8.4 Transition sequence (director sequence `possession.full`, actor-parameterised; gate `observed(actor)`)
| t (ticks) | Event |
|---|---|
| t0 | the NPC freezes; room lights FLICKER |
| t10 | twitch anim + `poseida.crack` |
| t30 | levitates 0.6 blocks (`setNoGravity`, kinematic) while `POSSESSION` ramps 0→1 over 40 ticks |
| t50 | head snaps 180° (ACTION) |
| t55 | demon line (or a mimic CALL with DEMON fx) |
| t70 | flash + scream (+ jumpscare portrait only if the player is within 6 blocks and looking) |
| t80 | lands; `HostBehaviour` installed |

### 8.5 Possessed behaviours (strategy objects that install and remove goals)
- **`MotherPossessed`:** stands facing a wall and turns her head when you approach. She sprints only while unobserved (reusing the doll's "seen" test). Kitchen knives `Orbit` her, then `Aim` and `Throw` at you.
- **`FatherPossessed`:** sits in the armchair laughing at a static TV. When you get close he throws furniture via `PropManager.lift` + Throw, and swings heavily.
- **`GrandmaPossessed`** (horror-comedy):
  - She keeps knitting while levitating in the rocking chair.
  - She offers "¿Un matecito… para tu alma?" in the demon voice.
  - Knitting needles orbit her.
- **`LuciaPossessed`:** Lucía's spider-walk, wall climbing, headspin and levitation behaviours port from `PoseidaEntity`, or the full possession can be staged with `ActorSwap` to the existing `PoseidaEntity` (§8.8).

### 8.6 Rendering
- **`FamilyRenderer`:** one model class per variant (generated `ent_madre.py` etc.) sharing bone names (`neck`, `head`, `jaw`, `*_arm`, …).
- **`PossessionLayer`:** re-renders the model with `<variant>_possessed.png` using a translucent entity render type, with alpha equal to `possession`. This is a smooth cross-fade covering veins, black eyes and torn mouth corners.
- **`GlowLayer` eyes:** alpha equals possession.
- **Deformation scaled by possession:** jaw drop, `neck` yScale 1 → 1.35, head tilt, finger splay, seeded jitter above 0.8.
- **Jaw lip flap:** from the dialogue envelope.

### 8.7 Humour rules (systemic, not scripted)
- **Calm NPCs react to poltergeist events with barks:**
  - the father explains everything as "las cañerías";
  - the mother's priority is that you clean your feet;
  - the grandma treats the TV static as her telenovela.
- **After being freed:** KO for 100 ticks, then a recovery line ("¿Qué hago arriba del ropero?").

### 8.8 `ActorSwap` (general)
`ActorSwap.swap(actorId, newType, fx)`:
1. Spawn the new entity at the same position and rotation.
2. Copy the custom name and site index.
3. Remap `actors[actorId]`.
4. Discard the old entity.
5. Hide the cut with a flash, smoke and a sound.

Uses: Lucía → `PoseidaEntity`, and as a fallback if the Choripán morph render slips (§9).

---

## 9. Choripán (the dog)

### 9.1 Entity
`ChoripanEntity extends PathfinderMob implements Spectral`:
- **Synced:** `FORM` (DOG, UNEASY, TRANSFORMING, BEAST, REVERTING), `FORM_TICKS`, `ACTION`, `HELD_ITEM` (ItemStack).
- **Size:** `getDefaultDimensions(pose)` returns DOG 0.6×0.85 or BEAST 1.5×2.4. Call `refreshDimensions()` on form change, on the server and in `onSyncedDataUpdated` on the client.

### 9.2 Dog behaviours (cute, and useful)
- **Detector:** `BarkAtSpectralGoal` barks and stares at Spectral entities (including the invisible Ánima) and at the anchor within 12 blocks. It works like an EMF on legs.
- **Thief and guide:** a scripted `StealGoal` grabs the ritual book from the table and runs to the doll's room. `HELD_ITEM` is rendered in his mouth.
- **Idles:** follow the family or the hunter, beg, scratch, play dead, wag.

### 9.3 Transformation (100 ticks, `observed` gate)
1. **Fake-out first** (comedy): uneasy growl, the camera pulls in (`lookPull`), the lights flicker… and he sneezes and wags.
2. **Real transform:**
   - **0–40:** dog model with jitter; spine arch; head twist 180°; parts swell 1 → 1.6 with noise. The bark pitches down.
   - **40–60, the burst:** dog parts translate outward along their normals while the beast model scales 0.2 → 1 from inside. Blood and `DEMON_SMOKE` particles. `Fx.flash` at t50 hides the swap.
   - **60–100:** the beast rises and roars. `BLACKOUT` in radius 16; shake ramp.
   - Invulnerable and no AI during the transform.
3. **Models:**
   - `ChoripanDogModel`: about 40 cubes, 64×64.
   - `ChoripanBeastModel`: about 200 cubes, 256×256. Elongated, ribs, six legs, split jaw, and it **still wears the collar tag "CHORIPÁN"** and wags a huge tail.

   `ChoripanRenderer` picks the model by `FORM` and phase, and renders both during 40–60.

### 9.4 Beast behaviours
- `PounceGoal`, `ChargeGoal` (bursts doors open).
- `HowlGoal`: light `BLACKOUT` around him and sanity −8.
- `MimicGoal`: the player's SCREAM with DEMON fx, or the fallback line "¿Quién es un buen chico?" in the demon voice.
- **Calming mechanic:** speaking softly or sneaking (§6.10).
- **Weaknesses:** holy water and the crucifix stun. Not jarable.
- **Finale:** a ritual-book exorcism leads to REVERTING (reverse burst and smoke), then a small dog asleep. He wakes, licks the player, burps black smoke and wags. **End-card gag:** a 1-frame eye glow.

---

## 10. Streamer systems (HOSPITAL)

### 10.1 Live chat overlay
- **Server, `LiveChatService` per site:**
  - Tracks `mood` (CHILL, HYPE, SCARED, WARNING, EVIL, DEAD), `viewers` and `streamActive` per player. The stream is active while the **Celular del streamer** item (`StreamCameraItem`) is in a hand, or when a beat forces it.
  - `ChatRule(cond, pool, priority, cooldown, burst)` rules are evaluated every 10 ticks.

| Rule | Condition | Pool |
|---|---|---|
| ENTITY_BEHIND | a Spectral within 7 blocks, dot < −0.3, not visible | `warn_behind` (burst 4–6 over 2 s) |
| DARK | light < 3 and flashlight off | `dark` ("prendé la linterna bro") |
| SILENT / YELL | SVC speech events | `silent` / `yell` |
| SCARE | tension spike or jumpscare | `scared_spam` |
| STUCK | no progress for 3 min | `hint_<objective>` (the chat is the hint system) |
| LOW_SANITY | sanity < 25 | `glitchy` (Zalgo-ish text) |
| DEATH | player died | `F` |
| IDLE | — | `idle` banter (client-generated) |

- **Network:**
  - The server sends cues, `ChatCuePayload(poolId, count, spreadTicks)`, and the client picks lines and usernames from its asset pools. This costs very little bandwidth.
  - Scripted lines use `ChatBatchPayload`.
  - `StreamStatePayload(active, viewers, mood)`.
- **Asset pools** (`assets/deadline/livechat/es_ar.json`, resource-pack overridable, so the creator can add his community's in-jokes and subscriber names):
```json
{ "users": { "normal": ["mate_amargo99", "ElPibeDeLaLuz", "chori_master", "tu_tia_en_tiktok", "lechuga_frita"],
             "evil": ["paciente_0413", "enfermera_rosa", "EL_DE_ATRAS"] },
  "colors": ["#ff6b6b", "#4dd0e1", "#ffd54f", "#81c784", "#ba68c8"],
  "pools": { "warn_behind": ["ATRAS", "DATE VUELTA", "ATRÁS ATRÁS ATRÁS", "bro mirá atrás :skull:"],
             "yell": ["JAJAJAJAJA", "se cagó", "CLIPEEN ESO", "ese grito fue de nena"],
             "idle": ["quién es este?", "dónde está el streamer original", "ES EL EXORCISTA DE YOUTUBE"] },
  "emotes": { ":skull:": "", ":kek:": "", ":chori:": "", ":mate:": "" } }
```
- **Emotes:** an original bitmap font `deadline:emotes` using private-use codepoints.
- **`LiveChatHud`** (right side, about 32% width, at most 10 lines):
  - Header "● EN VIVO · 1.284 👁"; messages slide in.
  - Works with VHS mode (H). Never overlaps the objective panel (top-left) or the ECG (bottom-left).
- **Donations:**
  - `DonationPayload(user, amount, textKey, lineId)` shows a top-centre alert with a sound and a robotic-TTS line, and the message is highlighted in chat.
  - Uses: jokes ("andá al sótano, cagón") and hints.
- **Evil phase:**
  - Usernames switch to the `evil` pool and viewers climb to 666.
  - Messages synchronise ("QUEDATE" × 20).
  - Finally every message is the player's own name.
  - The chat can **lie** ("abrí la puerta 3").

### 10.2 Found-footage tapes (`Tapes`)
- **Items:** a `vhs_tape` item with data component `deadline:tape_id` (String; persistent + network codec). It plays when used on a `TvBlock`, a VCR, or the streamer's laptop.
- **`Tape` structure:** `id`, `labelKey` (e.g. "Cumple Lucía 2003"), `mode`, `durationTicks`, and `List<TapeCue>` (tick → frame, Ken Burns pan/zoom, line, sound, subtitle, chat message, static burst, cut).

The three modes:
1. **SLIDESHOW** (cheap and robust):
   - A non-pausing `TapeScreen` with the VHS post shader, timecode and letterbox.
   - Frames in `textures/gui/tape/<id>/<n>.png` are **rendered offline from our own models and scenes** with `tools/models/render.py` and VHS-graded.
   - Uses: home videos (in Lucía's birthday the doll moves between frames), the 1987 school play, the streamer's VOD stills with the old chat.
   - The Director can declare a `safeZone` while a tape plays… or, deliberately, the entity is behind you when it ends.
2. **CCTV_LIVE** (the hospital security room):
   - `CctvCameraEntity`: invisible, no AI, no collision, spawned from `camera(...)` markers.
   - Using the security desk opens `CctvScreen`, and the client calls `mc.setCameraEntity(cam)`. Number keys and arrows switch cameras.
   - Overlay "CAM 03 — PASILLO B — 03:17", plus a `deadline:cctv` post effect (green night-vision with noise).
   - While in CCTV the server locks movement (a speed-attribute modifier of −100%), and the player stays vulnerable: knocking at the door is a warning.
   - **Set pieces:**
     - the entity looks into the camera;
     - it disappears between switches;
     - **your doppelgänger walks by and waves**;
     - CAM 6 shows the security room itself: you from behind, and something standing behind you.
   - Entities stay tracked because the site is within view distance and `clientTrackingRange(12)`.
3. **REENACT** (stretch goal):
   - A first-person replay of the streamer's last stream, with his stream overlay and old chat.
   - A `TapeCameraEntity` follows a Catmull-Rom spline through markers with handheld shake. Ghost "echo" actors are rendered translucent.
   - It ends in a grab, then static, then back to the player… and the streamer's camera now lies in the corridor ahead.

### 10.3 Doppelgänger and mirror (`DoppelgangerEntity`)
- **Rendering:** vanilla `PlayerModel` with the target player's skin (client `PlayerSkin` lookup by UUID, falling back to the default skin).
- **Modes:**
  - MIRROR: reflected across a plane marker, copying the player's mirrored yaw and pose; then one moment it stops copying and smiles.
  - WALKER: a route, seen on CCTV.
  - STALKER: stands far away facing you.
- **Voice:** mimic `QUOTE name` via `Follow(doppel)`.
- Fits the hospital twist: the streamer never came back… and maybe you didn't either.

---

## 11. Proposed set pieces per case (what these systems enable)

**COLEGIO — La Monja (Sor Agonía).**
- The "SILENCIO" rule (noise meter) in the chapel and library. Running and yelling attract her, and the creator will inevitably scream.
- The blackboard writes itself in chalk "No debo hablar en clase" again and again, ending with "TE ESCUCHÉ, {player}."
- Desks turn to face you when you look away.
- The confessional speaks with your own voice backwards; the curtain opens on the nun.
- Portraits of past Mother Superiors with moving eyes; one becomes empty.
- Corridor lights chase toward you; the bell tolls by itself; the nun's ruler flies and smacks your hand (comedy).
- The intercom roll call ends with your name, in your voice.
- Chapel climax: a choir made of your voices; the candelabras flicker in rhythm.
- She steals your voice when she grabs you.

**CASA — La Muñeca + family + Choripán.**
- Comedic intro: mate, "límpiese los pies", the grandma's telenovela on a static TV, the father's "cañerías".
- The doll (weeping-angel) repeats your words in a child voice.
- Dinner-table set piece: plates orbit, knives aim and then nail your silhouette on the wall.
- Chairs stacked on the table off-camera, then they collapse when seen.
- A possession chain (grandma → father → mother) with the demon wisp visibly jumping between hosts; each one is freed with a short rite.
- The TV channel changes from telenovela to FACE to "LUCÍA".
- "LIMPIATE LOS PIES" written in blood.
- Home-video tapes.
- Choripán's arc: detector → steals the book and guides you → fake-out sneeze → real transformation → calm him by speaking softly → exorcism → licks you → end-card eye glow.

**HOSPITAL — El Streamer.**
- His car, ring light and energy drinks.
- His phone still LIVE: picking it up turns on the chat ("¿quién es este?"). The chat warns "ATRÁS", jokes, hints through donations, and later lies.
- The PA broadcasts your voice; lights chase down the corridors; a gurney and a wheelchair roll on their own.
- EKG monitors speed up near the entity, then flatline.
- The CCTV security-room segment with the doppelgänger.
- The streamer's VOD tape.
- The evil-chat phase (666 viewers, every username your name).
- Finale: the streamer is found hollow and speaks with your voice.
- Epilogue at home: the phone rings, and it's you saying "acepto el caso".

---

## 12. Networking summary (new payloads; register in `ModNetworking`)

| Direction | Payload | Fields |
|---|---|---|
| S2C | `SubtitlePayload` | lineId, speakerId, durationTicks, entityId, flags |
| S2C | `LoopPayload` | pos, soundId, on |
| S2C | `CameraPayload` | mode (LOOK_PULL, CCTV, TAPE, RESET, LETTERBOX, DOLLY), entityId or position, strength, ticks |
| S2C | `TapePayload` | tapeId, startTick |
| S2C | `StreamStatePayload` / `ChatCuePayload` / `ChatBatchPayload` / `DonationPayload` | see §10.1 |
| S2C | `TakeEventPayload` | kind, id, note |
| S2C | `DirectorStatePayload` | tablet data (beats + state, hunters, clip counts) |
| S2C | `FxPayload` new kinds | BROWNOUT, NOISE (HUD level), VOICE_REC (indicator) |
| C2S | `CuePayload`, `DirectorActionPayload` | permission level ≥ 2 checked server-side |
| C2S | `CctvActionPayload`, `ConsentPayload` | |

Client "look pull": the client lerps `player.yRot/xRot` toward the target with ease-out, with `strength` capping degrees per tick. It uses the real player rotation, not the camera, so the crosshair stays consistent. "Dolly zoom" needs a small client mixin on the FOV computation **(verify with probe)**.

---

## 13. Performance budgets (added server cost at most 3 ms per tick at peak)
- **Director:** polled triggers are staggered (half per tick), with at most 20 LookAt raycasts per tick and a cap of 6 running sequences per site.
- **Poltergeist:** see §7.11. Light changes are capped at 10 per tick.
- **Voice:** off-thread. The Minecraft thread only does clip selection (O(48)) and channel creation. At most 4 playbacks and at most 24 MB of buffers.
- **Entities per site:**
  - at most 6 NPCs + Choripán + the boss + 6 minor haunts;
  - Displays as in §7.11;
  - CCTV cameras at most 8, with no tick logic.
- **Client:**
  - chat at most 10 lines; subtitles at most 3;
  - one post effect at a time (VHS, insanity or CCTV, with priority rules in `ClientFx.updatePostEffect`).

---

## 14. Risks and mitigations
| Risk | Mitigation |
|---|---|
| SVC Maven blocked in the agent sandbox (verified 403) | Builds in CI; `-PnoVoicechat` excludes `voice/svc` for local or offline builds |
| SVC events on a foreign thread → world access races | Strict hand-off: SVC thread → queues → MC thread; no world calls off-thread |
| Mic picks up the replayed voice (speakers) → feedback, recursive mimic | Contamination flag on utterances recorded during audible playback; recommend headphones; `echoToSelf` off by default |
| Mimic sounds "obviously recorded" | Use tagged consent clips for big payoffs; FX presets; context (behind doors, PA, in-head); keep clips short |
| Privacy and consent (creator and co-star) | Opt-in, diegetic consent, RAM only, indicator, `clear`, retention=CASE; mention in README and video |
| SVC not installed on the co-star's client | `available()` and consent per player; fallback sounds; Director checks `consented()` before choosing intents |
| Private `Display` setters and interpolation restart gotcha | Accessor-invoker mixins; force-sync start delay; verify names with `probe.sh` first (day 1) |
| Light engine cost from flicker | Our own `FixtureBlock` with LEVEL; caps; client brownout for extra effect |
| `FallingBlock` places blocks randomly | Not used for furniture; Display + settle instead |
| Possessed NPCs killed by normal weapons | Non-holy damage cancelled (with a comedic bark) |
| Camera-entity modes (CCTV, tapes) leave the player stuck | ESC always restores; server timeout 120 s; `CameraPayload(RESET)` on case end, death or disconnect |
| Set pieces happen off-camera | `observed` gates, `lookPull`, discovery stingers |
| Retakes diverge (random decay) | Seeded site builds, chapter setups, Director `cancelAll(restore)` |
| Kokoro accent is not rioplatense; comic timing suffers | `voice_overrides/*.wav` for real recordings; TTS reserved for processed or creepy voices |
| Scope creep (REENACT, doppelgänger) | Marked as stretch goals in phase 5; SLIDESHOW and CCTV deliver most of the value |
| Monetisation and gore | Blood kept stylised (decals, text), no dismemberment; the beast is creepy, not gory |

---

## 15. Implementation order

**Phase 0: foundation (needed by all 3 cases), about 8 days**
1. Probe day: add `Display#p`, `TextDisplay#p`, `Style`, `ServerLevel#playSeededSound`, `DoorBlock#setOpen` and the `GameRenderer` FOV method to `tools/ci/probe-javap.txt`; confirm the names.
2. Site markers + `SiteState` + seeded builds + `restartSite` + `Spectral` refactor (no behaviour change).
3. Director core: the triggers enter, lookAt, time, flag, stage, itemUse, interact and cue; the steps seq, par, wait, sound, fx, flag, say and anim; `/deadline beat|director|cue|take`; `ClientTakeLog` + slate + F10 CLIP; CI beat validation.
4. Dialogue: `lines_def.py` + generator → `DialogueLines.java`, `SubtitleHud`, entity-bound speech, lip-flap envelope, barks.
5. **SVC spike (in parallel, to de-risk early):**
   - plugin + recorder + segmentation;
   - `/deadline mimic play echo` DRY via a locational channel;
   - `SpeechEvent`s → `NoiseMeter`;
   - confirm singleplayer, and multiplayer with a friend.

**Phase 1: Poltergeist + CASA core, about 14 days**

6. Display invokers + `PropManager` + motions + collision + prop item models.
7. Doors/locks, `FixtureBlock` lights (patterns, chase, blackout), `TvBlock` + `BlockLoops`, `WallWriter` + blood/chalk fonts, `UnseenSwap` + stingers, `HauntActivity` ambient pool.
8. `FamilyNpcEntity` (routines, talk, barks) → `PossessionComponent` + `Demon` + transition sequence + 3 behaviours + `PossessionLayer`.
9. Choripán: dog AI → models (art pipeline in parallel) → transformation staging → beast → calming mechanic.

**Phase 2: voice polish + COLEGIO, about 6 days**

10. DSP chain + intents and selection + Speakers/InHead emitters + steal modes + consent call + fallback sounds + config.
11. Nun `HearingGoal` + `NoiseHud` + the chalk, confessional and choir beats.

**Phase 3: HOSPITAL, about 10 days**

12. `LiveChatService` + `LiveChatHud` + pools + emotes font + donations + `StreamCameraItem`.
13. Tapes SLIDESHOW (+ offline still rendering) → CCTV mode + cameras + post shader → `DoppelgangerEntity` → (stretch) REENACT.

**Phase 4: production polish, about 5 days**

14. Director Tablet + cue hotkeys + tension pacing + density presets + comedy relief.
15. Performance pass with budget assertions in CI smoke; client-smoke screenshots of subtitles, chat, levitating props, possession blend and Choripán forms; README for the creator (commands, consent, recording tips: headphones, SVC settings, slate).

Dependencies: 2 → 3 → (4, 6, 7, 8, 12). 5 is independent and should be done early. 9 depends on 8 (Spectral, Possession). 13 depends on 3 and 4.

---

## 16. Open questions for the owner
1. Will a friend co-star (multiplayer)? That enables the friend's voice as a lure, voice stealing between players, and the friend as a Director-Tablet puppeteer.
2. Should we use real voice acting (you or friends) for the comedic lines, or TTS everywhere?
3. Are you comfortable with the diegetic consent call recording your name? Should the co-star get the same?
4. What should the streamer be called and look like, and what is the parody streaming platform's name? Avoid real streamers and brands.
5. Subtitles burned in-game (default on) or added in the edit?
6. Will you record in singleplayer (SVC works with `run_local_server=true`, the default) or on a small server?
7. Gore ceiling for YouTube: keep the stylised-blood default?
