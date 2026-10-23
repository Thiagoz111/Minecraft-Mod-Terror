export const meta = {
  name: 'deadline-casa-sounds',
  description: 'Render every Casa Morales voice line (TTS + character DSP) and SFX, then independent QA per group',
  phases: [
    { title: 'Design', detail: 'one sound designer per group writes its generator and renders OGGs' },
    { title: 'QA', detail: 'independent audio engineer verifies files/levels/usage and improves weak sounds' },
  ],
}

const SP = '/tmp/claude-0/-home-user-Minecraft-Mod-Terror/f464a6ad-b203-50f8-a993-93d7fecfc5d1/scratchpad'
const COMMON = `You are a senior game sound designer on DEAD LINE, a Minecraft 1.21.11 Fabric horror-comedy mod made for a viral
Argentine YouTube video. Case 2 is "Casa Morales": a 1950s chalet in the Buenos Aires suburbs where a demon (AZAMEL)
locked in a porcelain doll (Ofelia) jumps from body to body: the dachshund Choripán (who becomes a chain-bodied beast
with six human arms), the dad Jorge (the barbecue king, possessed at the grill with blue fire and orbiting knives),
the girl Lucía and finally the Nona, who was the possessed girl in 1961. Marta (the mum, curlers and bathrobe) is the
comic guide; Toti (15) hides in the wardrobe playing ranked. Tone: suburban family comedy that turns into real dread;
the comic beats must land as hard as the scares. A neighbour's cumbia plays far away; when it cuts, something comes.
Spanish is RIOPLATENSE (voseo). Read docs/design/BIBLIA.md section 2.2 (Casa Morales: c, h, k, l, m) for every beat
these sounds serve.

Repository: /home/user/Minecraft-Mod-Terror. Toolkit: tools/audio/dsp.py (READ IT FIRST): oscillators, noise, envelopes,
filters, formant, reverb, echo, drive, bitcrush, ring, tremolo, reverse, resample, pitch_shift, time_stretch, granular,
mix/pan/concat, trim, master, TTS \`tts(text, voice, speed)\` (Kokoro; voices ef_dora = woman, em_alex = man,
em_santa = deep man; rioplatense accent by default; cached), phone_voice(), demonic(), save_ogg(x, 'path/name'),
analyse(x), spectrogram_png(x, path). The finished Colegio generators are the quality reference: tools/audio/snd_voices.py,
snd_colegio.py, snd_monja.py. Event list: tools/audio/sounds_def.py (name -> (variants, subtitle_es, subtitle_en, stream));
spoken lines: tools/audio/lines.py (LINES id -> speaker/es/en/voice/fx/say; the casa.* and operadora.casa_aviso entries
and the voice presets documented at the top). File naming: event 'knife.whoosh' with 3 variants ->
save_ogg(x, 'knife/whoosh_1'), 'knife/whoosh_2', 'knife/whoosh_3'; single-variant events have no suffix ('pool.splash' ->
'pool/splash'). Line 'casa.marta.hola' -> event 'line.casa.marta.hola' -> save_ogg(x, 'line/casa/marta/hola').
Every listed file MUST exist when you finish. Spectrograms/QA images go to the dev work dir (tools/workdir.py WORK).

Hard rules
* Positional sounds MUST be mono. Only events with stream=True (casa.cumbia_far, casa.cumbia_musicbox, casa.tv_novela, casa.tv_static, morning.birds, ambient.casa) may be stereo. All voice lines mono.
* Finish every file with dsp.master(x, peak_db=...): screams/stingers -0.5 dB, voices -1 dB, foley/UI -3 dB,
  loops/streams -4 dB. No clipping, no DC, trim dead air but keep reverb tails; loops must be seamless.
* Real quality: layered, physically plausible foley, rich spectra, clear attacks. Voices processed into characters
  (pitch, formants, room, breath, layering) but the WORDS MUST STAY INTELLIGIBLE (subtitles show them; the video
  audience must understand every line in Spanish).
* Only create/edit your own generator module (named below) and the OGG/JSON files it writes. Do NOT edit dsp.py,
  sounds_def.py, lines.py, sounds.json, Java or other groups' modules. Never run git.
* Self-review: run dsp.analyse on every file, write spectrograms to ${SP}/audio/casa_<group>/ and LOOK at them with
  Read. Iterate until each sound has the right envelope, spectrum, length and loudness. Keep module runtime < 6 min.`

const GROUPS = [
  { key: 'voices', module: 'snd_voices.py', brief: `Extend tools/audio/snd_voices.py (do NOT change how the Colegio lines sound; add a way to
render only the casa lines, e.g. \`python3 tools/audio/snd_voices.py casa\`, so the Colegio files are not re-rendered)
with the Casa presets documented at the top of lines.py and render EVERY voiced casa.* line plus operadora.casa_aviso:
  marta: ef_dora natural, nervous and fast, small living-room ambience; 'phone' fx -> dsp.phone_voice (her call).
  jorge: em_alex, jovial, low, a bit hoarse, patio air; jorge_poseido: jorge layered with em_santa -5 st, grit, a wet
         crackle like fat on a grill under the words.
  nona: ef_dora -2 st, slow, old rasp + slight tremolo, a little deaf-loud; nona_grito: the same woman SHOUTING, strong
        and clear, no old-age effect (it is the hero moment); nona_poseida: whispered, demonic layer, head-close.
  lucia: ef_dora +3 st, small and shy; lucia_doble: lucia in unison with em_santa -9 st (both intelligible).
  toti: em_alex +2 st, annoyed teen, muffled as if inside a wardrobe (low-pass, boxy) for ocupado/callate, clear for
        que_perdi.
  choripan: em_santa -5 st with an octave-down layer and a wet growl between the two halves ("¿Quién es un buen
            chico?" ... beat ... "YO NO.").
  spirit: syllables chopped by radio sweeps with static between them (use the same voice family as the spirit box).
  tomi: em_alex laughing, tiny tablet speaker band.
Also update src/main/resources/data/deadline/lines.json with the new ids (ceil(seconds*20) ticks) without removing the
Colegio entries.` },
  { key: 'sfx', module: 'snd_casa.py', brief: `Write tools/audio/snd_casa.py rendering these house/foley events (all variants listed in
sounds_def.py): casa.breaker_trip (clonk of a 1960s breaker with a spark and every hum dying), casa.breaker_reset (lever
thunk + fluorescent/fridge hum returning), casa.tv_novela (STREAM-like 20 s loop: a telenovela at full volume through
an old CRT speaker: dramatic Spanish dialogue murmur (TTS fragments, unintelligible-ish), violins sting), casa.tv_static
(CRT static loop with the high whine), grill.sizzle (fat sizzling on embers, 5 s, loopable), fire.blue_whoosh (gas-like
ignition whoosh turning unnatural and low), knife.lift (2: steel knives rising off a rack, metallic shing), knife.whoosh
(3: a knife spinning through the air), knife.impact (3: a knife thunking into wood), salt.hit_scream (a handful of salt
hitting skin with a hiss and a demonic yelp), pool.splash (a heavy body falling into an above-ground pool), plate.whoosh
(4: a china plate frisbeeing past your head), plate.shatter (3), plate.storm (a storm of plates and crockery cascading
down a stair, 4 s), mate.slide (a ceramic mate sliding 2 blocks on a laminate counter), mate.sip_empty (THE empty mate
gurgle through a metal bombilla - must be funny), termo.fly (a thermos whistling through the air then clanging),
alacena.golpe (3: kitchen cupboard doors banging), chair.stack (wooden chairs rattling/settling into a tower "that
happened while you weren't looking"), door.slam_cascade (5 doors slamming in a row, accelerating, closer each time),
bulb.pop (2: a light bulb bursting), doll.turn (3: porcelain head clicks), doll.giggle_chorus (10 little giggles out of
phase in a small room), andador.squeak (3: one squeaky walker wheel - a running gag), chancleta.whip (a rubber slipper
whipping through the air), chancleta.hit (the slap - cartoonishly satisfying), rocking.creak_slow (a rocking chair
creaking slowly, 4 s), yarn.twang (2: taut wool string twang), yarn.snap, stitch.pull (3: a needle pulling thread
through cloth, ASMR close), azamel.suck (a reversed scream sucked into a point + a porcelain "tink"), candles.out (one
long breath and 7 flames dying), wall.break (a huge impact and a brick wall collapsing into a basement), wisp.whistle
(a thin whistle with ember crackle travelling past), morning.birds (STREAM loop 20 s: suburban morning birds, a far
bus), kettle.whistle (a kettle coming to the boil and whistling), ambient.casa (REPLACE: stereo 60 s seamless loop of a
suburban house at night: fridge hum, a clock, distant dogs, the house settling).` },
  { key: 'choripan', module: 'snd_choripan.py', brief: `Write tools/audio/snd_choripan.py rendering: choripan.bark_cute (3: small cute dachshund
barks), choripan.whine (2), choripan.growl_low (2), choripan.sneeze (a tiny dog sneeze - adorable), choripan.crack (6:
wet bone cracks: celery snap + low thump, each different), choripan.unspool (one long uninterrupted stretch of rubber over
flesh while links keep coming out, 5 s), choripan.demon_roar (2: a small bark that turns into a deep roar and a reversed
scream), choripan.fetch_drop (an object dropped at your feet, panting, tail thumping), choripan.chomp (a cartoonish chomp),
choripan.vomit (a thick black gurgling vomit with splatter), choripan.metro_retract (a TAPE MEASURE zipping back + "boing"
- the only explicit cartoon sound of the case); and the music: casa.cumbia_far (STREAM: an ORIGINAL 40 s cumbia loop -
güiro, bouncy bass, synth accordion melody, timbales - heard band-passed as if from three houses away at night; seamless
loop; no copyrighted melody), casa.cumbia_cut (the same cumbia cut by a needle scratch / power cut), casa.cumbia_musicbox
(STREAM: the cumbia melody sliding into a 1961 music box, detuned and slowing, loop).` },
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
  (args && args.only) ? GROUPS.filter(g => args.only.includes(g.key)) : GROUPS,
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
