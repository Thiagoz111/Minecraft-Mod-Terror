export const meta = {
  name: 'deadline-colegio-sounds',
  description: 'Render every Colegio Santa Ines voice line (TTS + character DSP) and SFX, then independent QA per group',
  phases: [
    { title: 'Design', detail: 'one sound designer per group writes its generator and renders OGGs' },
    { title: 'QA', detail: 'independent audio engineer verifies files/levels/usage and improves weak sounds' },
  ],
}

const SP = '/tmp/claude-0/-home-user-Minecraft-Mod-Terror/f464a6ad-b203-50f8-a993-93d7fecfc5d1/scratchpad'
const COMMON = `You are a senior game sound designer on DEAD LINE, a Minecraft 1.21.11 Fabric horror-comedy mod made for a viral
Argentine YouTube video. Case 1 is "Colegio Santa Inés de la Vigilia": a closed 1984 Catholic girls' boarding school
in Córdoba where every night repeats June 21st 1984. Sor Agonía (a possessed nun who hunts by SOUND and burns in
light), the ghost of the strict principal Madre Remedios (takes roll call, writes reprimands, "Ajá."), 7 mouthless
ghost schoolgirls of the choir (Paloma is their leader and the only one who talks, she tells jokes), Hermana Clara
(the nun's human self, calling for help from 1984), a priest behind a confessional grille (comic). Tone: real dread
with planned comic beats. Spanish is RIOPLATENSE (voseo: "prendé", "corré", "vení"). Read docs/design/BIBLIA.md
section 2.1 (lines 276-583) for every beat these sounds serve.

Repository: /home/user/Minecraft-Mod-Terror. Toolkit: tools/audio/dsp.py (READ IT FIRST): oscillators, noise, envelopes,
filters, formant, reverb, echo, drive, bitcrush, ring, tremolo, reverse, resample, pitch_shift, time_stretch, granular,
mix/pan/concat, trim, master, TTS \`tts(text, voice, speed)\` (Kokoro; voices ef_dora = woman, em_alex = man,
em_santa = deep man; rioplatense accent by default; cached), phone_voice(), demonic(), save_ogg(x, 'path/name'),
analyse(x), spectrogram_png(x, path). Existing generators for reference: tools/audio/snd_ambience.py, snd_ui.py.
Event list: tools/audio/sounds_def.py (name -> (variants, subtitle_es, subtitle_en, stream)); spoken lines:
tools/audio/lines.py (LINES id -> speaker/es/en/voice/fx/say). File naming: event 'tiza.escribe' with 3 variants ->
save_ogg(x, 'tiza/escribe_1'), 'tiza/escribe_2', 'tiza/escribe_3'; single-variant events have no suffix
('door.slam' has 2 -> 'door/slam_1','door/slam_2'; 'muro.cae' -> 'muro/cae'). Line 'colegio.madre.lista' -> event
'line.colegio.madre.lista' -> save_ogg(x, 'line/colegio/madre/lista'). Every listed file MUST exist when you finish.

Hard rules
* Positional sounds MUST be mono. Only events with stream=True (coro.*) may be stereo. All voice lines mono.
* Finish every file with dsp.master(x, peak_db=...): screams/stingers -0.5 dB, voices -1 dB, foley/UI -3 dB,
  loops/streams -4 dB. No clipping, no DC, trim dead air but keep reverb tails; loops must be seamless.
* Real quality: layered, physically plausible foley, rich spectra, clear attacks. Voices processed into characters
  (pitch, formants, room, breath, layering) but the WORDS MUST STAY INTELLIGIBLE (subtitles show them; the video
  audience must understand every line in Spanish).
* Only create/edit your own generator module (named below) and the OGG/JSON files it writes. Do NOT edit dsp.py,
  sounds_def.py, lines.py, sounds.json, Java or other groups' modules. Never run git.
* Self-review: run dsp.analyse on every file, write spectrograms to ${SP}/audio/colegio_<group>/ and LOOK at them with
  Read. Iterate until each sound has the right envelope, spectrum, length and loudness. Keep module runtime < 6 min.`

const GROUPS = [
  { key: 'voices', module: 'snd_voices.py', brief: `Write tools/audio/snd_voices.py: render EVERY entry of lines.LINES whose voice is not None
(use the 'say' text when present, else 'es') with these character presets (tune them by ear-proxy: spectrograms,
pitch tracks, intelligibility):
  madre: ef_dora, about -3 semitones (formant-preserving if you can: pitch_shift + time_stretch), slow (speed 0.8),
         clipped stern delivery, small dry office/classroom room, a hint of old-woman rasp. 'pa' fx lines: 1980s
         school loudspeaker (band 300-3500 Hz, horn resonance, slapback from a long corridor).
  clara: ef_dora, whispered/breathy (mix in shaped noise following the envelope), scared, fast-ish (speed 0.95),
         'phone' fx -> dsp.phone_voice. clara84: same but a 1984 answering-machine tape: hiss, wow/flutter, dropouts,
         crying breaths between phrases.
  cura:  em_santa, slow (0.8), warm old man, inside a wooden confessional box (short boxy reverb, low-mid resonance).
  alumna: ef_dora +4 semitones, thin (band-limited 400-6000), long cold reverb, breathy whisper where the text says
         (susurro); a little unnatural (slight pitch wobble). paloma: same girl but closer, clearer, less reverb.
  coro:  7 girl takes layered (different speeds/seeds/detune +-20 cents, 10-40 ms offsets), big chapel reverb.
  monja: ef_dora -5 st layered with em_santa -9 st, grit/distortion, close and whispered for 'head' fx lines.
  operadora: ef_dora, bright, overly polite, telephone band, tiny digital artifacts.
Also write src/main/resources/data/deadline/lines.json = {id: length_in_ticks} (ceil(seconds*20)) for EVERY voiced
line (the case director waits that long). Clean leading/trailing silence so timings are tight.` },
  { key: 'sfx', module: 'snd_colegio.py', brief: `Write tools/audio/snd_colegio.py rendering these school/foley events (all variants):
colegio.timbre (4 s electric school bell hammering at full volume, metallic, slight room), colegio.campana (one deep
bronze bell toll, 8 s tail), colegio.campana_triple (three tolls, ~9 s, the last one longest), colegio.pa_chime (1980s
two-tone PA ding-dong), colegio.viento (2: gust through old wooden shutters, rattling, 3-4 s; warns that the moon is
about to be covered), colegio.polvo (plaster dust and grit trickling from the ceiling after a slam), door.slam (2:
heavy old wooden school door slammed, big hall reverb), tiza.escribe (3: chalk writing a few words on a blackboard by
itself, 2-3 s, squeaks + taps, variable speed), tiza.rompe (chalk snapping), pupitres.giran (16 wooden school chairs
scraping on a tiled floor at the same time, 2.5 s, ends in unison), farol.revienta (3: glass lamp bursting with an
electrical pop and tinkling shards), luces.fuera (main breaker thunk + all hum dying), silla.arrastra (2: one heavy
chair dragged slowly on floorboards, 1.5 s), silla.gira (old wooden swivel chair creaking round), telefono_baquelita.ring
(old mechanical bakelite phone bell, one ring cycle ~2.5 s, loopable), telefono.linea (crackly line static/pulse
clicks transition, 1.5 s), mate.sorbo (sip through a metal bombilla of a washed-out mate: the empty gurgle), 
confesionario.rejilla (small wooden grille sliding), espejo.raja (mirror glass cracking slowly, 2 s), muro.cae (brick
wall collapsing, dust, 3 s), tumba.tapa (heavy stone lid grinding open, 2.5 s), regla.rompe (hard quebracho ruler
snapping with an echo and a shimmering choir swell), ui.amonestacion (rubber stamp thump + little desk bell — a comic
"REPRIMAND" sting, UI sound), madre.pluma (quill scratching quickly then a stamp), dormitorio.respira (2: several
sleepers breathing slow under sheets, 4 s, eerie), alumna.pasos (2: a group of little girls running on wooden floors,
3 s). Use "silla.arrastra"-like care: these are clip-defining moments in the video.` },
  { key: 'nun', module: 'snd_monja.py', brief: `Write tools/audio/snd_monja.py rendering the nun and choir events (all variants):
monja.campanita (her warning: a small brass hand-bell "tilín-tilín", 1 s, clean and creepy), monja.regla_tap (a
wooden ruler tapped against a palm "tac... tac..." two taps over ~1.4 s, loopable proximity cue), monja.reglazo (the
ruler striking hard: a painful slap + whoosh), monja.shh (a long enveloping SHHHHH that seems to come from everywhere,
2.5 s), monja.burn (flesh sizzling, smoke, a pained inhuman intake of breath, 2 s), monja.soplido (a cold breath that
blows out a candle: blow + flame flutter + tiny smoke hiss), monja.ceiling (cloth and bones dragging across a ceiling
above you, 3 s), monja.mojada (an indignant offended groan with dripping water — comic but still unsettling),
monja.scream (REPLACE the existing file: piercing scream with choir-like harmonics and a demonic undertone, 1.6 s,
jumpscare-grade), monja.hiss (REPLACE: feral cat-like hiss of a large creature), coro.ave_reves (STEREO stream: a
lo-fi girls' choir singing the traditional Ave Maria melody (public domain, Schubert or Gregorian) as hummed vowels
"ah/oh" via formant synthesis or layered TTS vowels, then REVERSED, in a big chapel; seamless 20 s loop),
coro.ave_derecho_1/_2/_3 (STEREO: the same choir singing forward, each a ~8-10 s phrase, in crescendo: 1 = 3 voices
timid, 2 = 7 voices, 3 = full choir with organ-like pad and swelling reverb), coro.acorde_final (bright luminous
major chord swell with bells, 5 s, catharsis), ambient.colegio (REPLACE: stereo 60 s seamless loop: wind on old
shutters, a distant boiler knocking, far away the choir humming barely audible, an old building settling).` },
]

const SUMMARY = {
  type: 'object',
  properties: {
    module: { type: 'string' },
    files_written: { type: 'array', items: { type: 'string' } },
    notes: { type: 'string' },
    issues: { type: 'array', items: { type: 'string' } },
  },
  required: ['module', 'files_written', 'notes', 'issues'],
}

const results = await pipeline(
  GROUPS,
  g => agent(`${COMMON}

YOUR GROUP: "${g.key}" (module tools/audio/${g.module}, expose build() and a __main__).
${g.brief}

Run it from the repo root, review, iterate. Return a summary.`, { label: `design:${g.key}`, phase: 'Design', schema: SUMMARY }),
  (design, g) => agent(`${COMMON}

You are the INDEPENDENT AUDIO QA ENGINEER for group "${g.key}" (module tools/audio/${g.module}, written by another
designer; their notes: ${JSON.stringify(design)}).
1. Verify every expected file exists for this brief (cross-check variants with tools/audio/sounds_def.py and, for
   voices, every voiced id in tools/audio/lines.py + src/main/resources/data/deadline/lines.json). Missing = blocking.
2. Decode every file (soundfile reads .ogg): channels, peak, RMS, length, clipping, DC, dead air, loop seams.
   Render spectrograms and LOOK at them.
3. Judge critically against the brief: frightening/comic as intended, layered, intelligible words for voices.
   Improve weak sounds directly in tools/audio/${g.module} and re-render. Brief: ${g.brief}
Return a summary (files_written = all files of the group).`, { label: `qa:${g.key}`, phase: 'QA', schema: SUMMARY }),
)
return results
