# -*- coding: utf-8 -*-
"""Every spoken line of DEAD LINE: the single source for TTS audio, subtitles and the director's timings.

id -> dict(speaker, es, en, voice, fx)
  speaker  key of deadline.speaker.<speaker> (name shown above the subtitle)
  es / en  subtitle text (rioplatense Spanish / English). The Spanish text is also what the TTS says, unless `say`
           gives a different spoken text (e.g. to spell out numbers or add pauses).
  voice    None = subtitle only (no audio). Otherwise a voice preset of tools/audio/snd_voices.py:
             madre   old strict nun (ef_dora, -3 st, slow, dry room)
             clara   young nun, whispering and scared (ef_dora, breathy, phone band)
             clara84 Clara's 1984 recording (clara + tape hiss, wow/flutter, crying breaths)
             cura    old priest behind the confessional grille (em_santa, slow, wooden box resonance)
             alumna  ghost schoolgirl (ef_dora +4 st, band-limited, long reverb)
             paloma  the choir leader, the only girl who talks (alumna, closer and clearer)
             coro    the 7 girls at once (alumna layered x7 with detune and delays)
             monja   Sor Agonia (ef_dora -5 st layered with em_santa -9 st, distortion)
             operadora the DEAD LINE switchboard (ef_dora, bright, telephone band, polite)
  fx       optional placement hint: 'phone' (heard through the phone), 'pa' (loudspeakers), 'room', 'head'

Sound events are 'line.<id>' (files assets/deadline/sounds/line/<id>.ogg); subtitles are deadline.line.<id>.
tools/audio/snd_voices.py renders them and writes data/deadline/lines.json with each line's length in ticks.
"""

SPEAKERS = {
    'madre': ('Madre Remedios', 'Mother Remedios'),
    'clara': ('Hermana Clara', 'Sister Clara'),
    'cura': ('El cura', 'The priest'),
    'alumna': ('Alumna', 'Schoolgirl'),
    'paloma': ('Paloma', 'Paloma'),
    'coro': ('El coro', 'The choir'),
    'monja': ('Sor Agonía', 'Sister Agony'),
    'operadora': ('La Operadora', 'The Operator'),
    'tu': ('Vos', 'You'),
    'cartel': ('', ''),
}

LINES = {
    # ---------------------------------------------------------------- the call
    'colegio.clara.llamada': dict(
        speaker='clara', voice='clara', fx='phone',
        es='Perdón que llamo tan tarde... no puedo hablar fuerte, ella escucha. Colegio Santa Inés. Si la ves, apagá todo... ¡no, no, al revés! Prendé todo. La luz la quema. Y por favor... no se corre en los pasillos.',
        en="Sorry for calling so late... I can't speak up, she listens. Saint Agnes School. If you see her, turn everything off... no, no, the other way! Turn everything on. Light burns her. And please... no running in the halls."),
    'operadora.aviso': dict(
        speaker='operadora', voice='operadora', fx='phone',
        es='DEAD LINE le informa que esta llamada puede ser grabada con fines de exorcismo. Gracias por elegirnos.',
        en='DEAD LINE informs you that this call may be recorded for exorcism purposes. Thank you for choosing us.'),
    'operadora.muerte': dict(
        speaker='operadora', voice='operadora', fx='head',
        es='DEAD LINE le recuerda que la muerte no lo exime del pago.',
        en='DEAD LINE reminds you that death does not exempt you from payment.'),

    # ---------------------------------------------------------------- chapter 2: roll call
    'colegio.madre.lista': dict(
        speaker='madre', voice='madre', fx='room',
        es='Silencio. Se toma lista.', en='Silence. Roll call.'),
    'colegio.madre.ferreyra': dict(speaker='madre', voice='madre', fx='room', es='Ferreyra.', en='Ferreyra.'),
    'colegio.madre.quiroga': dict(speaker='madre', voice='madre', fx='room', es='Quiroga.', en='Quiroga.'),
    'colegio.madre.bazan': dict(speaker='madre', voice='madre', fx='room', es='Bazán.', en='Bazan.'),
    'colegio.madre.luna': dict(speaker='madre', voice='madre', fx='room', es='Luna.', en='Luna.'),
    'colegio.madre.sosa': dict(speaker='madre', voice='madre', fx='room', es='Sosa.', en='Sosa.'),
    'colegio.madre.heredia': dict(speaker='madre', voice='madre', fx='room', es='Heredia.', en='Heredia.'),
    'colegio.madre.moyano': dict(speaker='madre', voice='madre', fx='room', es='Moyano.', en='Moyano.'),
    'colegio.madre.albornoz': dict(speaker='madre', voice='madre', fx='room', es='Albornoz...', en='Albornoz...'),
    'colegio.madre.ausente': dict(speaker='madre', voice='madre', fx='room', es='Ausente.', en='Absent.'),
    'colegio.madre.usted': dict(speaker='madre', voice='madre', fx='room', es='¿Y usted? ¿Cómo se llama?', en='And you? What is your name?'),
    'colegio.alumna.presente': dict(speaker='alumna', voice='alumna', fx='room', es='(susurro) Presente.', say='Presente.', en='(whisper) Present.'),

    # ---------------------------------------------------------------- chapter 2: the lesson
    'colegio.madre.pregunta1': dict(
        speaker='madre', voice='madre', fx='room',
        es='Primera pregunta. ¿Cuántas eran en el coro? A, siete. B, ocho. C, doce. D, ni idea, profe.',
        en='First question. How many were in the choir? A, seven. B, eight. C, twelve. D, no idea, miss.'),
    'colegio.madre.conta_bien': dict(speaker='madre', voice='madre', fx='room', es='Contá bien.', en='Count again.'),
    'colegio.madre.correcto': dict(speaker='madre', voice='madre', fx='room', es='Correcto. Siéntese.', en='Correct. Sit down.'),
    'colegio.madre.pregunta2': dict(
        speaker='madre', voice='madre', fx='room',
        es='Segunda pregunta. ¿Quién castiga? A, la Madre. B, Sor María. C, Dios. D, tu vieja.',
        en='Second question. Who punishes? A, the Mother. B, Sister Maria. C, God. D, your mom.'),
    'colegio.madre.como_dijo': dict(speaker='madre', voice='madre', fx='room', es='¡¿Cómo dijo?!', en='I beg your pardon?!'),
    'colegio.alumna.risitas': dict(speaker='alumna', voice='coro', fx='room', es='(risitas)', say='ji ji ji ji', en='(giggles)'),

    # ---------------------------------------------------------------- chapter 3-4
    'colegio.monja.no_se_corre': dict(speaker='monja', voice='monja', fx='head', es='No se corre en los pasillos.', en='No running in the halls.'),
    'colegio.madre.megafonia': dict(
        speaker='madre', voice='madre', fx='pa',
        es='Se solicita al alumno nuevo en Dirección. Inmediatamente.', en='The new student is wanted in the Principal\'s office. Immediately.'),
    'colegio.mate.lavado1': dict(speaker='tu', voice=None, es='Está lavado.', en="It's washed out."),
    'colegio.mate.lavado2': dict(speaker='tu', voice=None, es='Sigue lavado. Desde 1984.', en='Still washed out. Since 1984.'),
    'colegio.mimic.presente': dict(speaker='tu', voice=None, es='(una voz igual a la tuya) ...Presente.', en='(a voice just like yours) ...Present.'),
    'colegio.clara.1984': dict(
        speaker='clara', voice='clara84', fx='phone',
        es='¿Hay alguien? ...Por favor... les dije que me llevaran a mí... a mí...',
        en="Is anyone there? ...Please... I told them to take me... me..."),
    'colegio.clara.ya_sabe': dict(
        speaker='clara', voice='clara', fx='phone',
        es='Ya sabe quién soy. No me tenga lástima. Lo que buscan está abajo.',
        en='Now you know who I am. Don\'t pity me. What they want is down below.'),

    # ---------------------------------------------------------------- chapter 5: confession and choir
    'colegio.cura.ave': dict(speaker='cura', voice='cura', fx='room', es='Ave María Purísima... Contame, hijo.', en='Hail Mary most pure... Tell me, son.'),
    'colegio.cura.r1': dict(speaker='cura', voice='cura', fx='room', es='Tres avemarías y no lo hagas más.', en='Three Hail Marys and don\'t do it again.'),
    'colegio.cura.r2': dict(speaker='cura', voice='cura', fx='room', es='Eso no es pecado, es mal gusto.', en='That\'s not a sin, that\'s bad taste.'),
    'colegio.cura.r3': dict(speaker='cura', voice='cura', fx='room', es='¿Terminaste? Tengo el asado en el fuego.', en='Are you done? I have a barbecue on the grill.'),
    'colegio.cura.r4': dict(speaker='cura', voice='cura', fx='room', es='Decime una cosa, hijo... ¿ganamos otro Mundial?', en='Tell me something, son... did we win another World Cup?'),
    'colegio.cura.corre': dict(speaker='cura', voice='cura', fx='room', es='...Y corré.', say='Y... corré.', en='...And run.'),
    'colegio.paloma.toma': dict(speaker='paloma', voice='paloma', fx='room', es='Tomá, se te cayó.', en='Here, you dropped this.'),

    # ---------------------------------------------------------------- chapter 6: the great silence
    'colegio.clara.dormitorio': dict(
        speaker='clara', voice='clara', fx='phone',
        es='No prenda la luz en el dormitorio. Y si me ve sentada... no me mire mucho.',
        en="Don't turn on the light in the dormitory. And if you see me sitting... don't stare at me."),
    'colegio.alumna.shh': dict(speaker='alumna', voice='alumna', fx='room', es='Shhh...', en='Shhh...'),
    'colegio.alumna.shh_viene': dict(speaker='alumna', voice='alumna', fx='room', es='Shh... viene.', en="Shh... she's coming."),
    'colegio.cartel.canilla': dict(speaker='cartel', voice=None, es='Era agua de la canilla.', en='It was tap water.'),
    'colegio.cartel.agua': dict(speaker='cartel', voice=None, es='Si se acerca, tirale agua bendita.', en='If she comes close, throw holy water at her.'),
    'colegio.paloma.perdon': dict(speaker='paloma', voice='paloma', fx='room', es='Perdón.', en='Sorry.'),
    'colegio.madre.pensa': dict(speaker='madre', voice='madre', fx='head', es='Pensá en lo que hiciste.', en='Think about what you did.'),
    'colegio.paloma.chiste1': dict(
        speaker='paloma', voice='paloma', fx='room',
        es='Toc, toc. ¿Quién es? La monja. ¿Qué monja? ...La que está atrás tuyo.',
        en="Knock knock. Who's there? The nun. The nun who? ...The one behind you."),
    'colegio.paloma.chiste2': dict(speaker='paloma', voice='paloma', fx='room', es='¿Querés saber un secreto? Sor Agonía ronca.', en='Wanna know a secret? Sister Agony snores.'),

    # ---------------------------------------------------------------- chapters 7-9
    'colegio.alumnas.corre': dict(speaker='coro', voice='coro', fx='room', es='¡CORRÉ!', en='RUN!'),
    'colegio.clara.falta_voz': dict(speaker='clara', voice='clara', fx='phone', es='Falta una voz. Siempre faltó una.', en='One voice is missing. One was always missing.'),
    'colegio.monja.quien_hablo': dict(speaker='monja', voice='monja', fx='room', es='¿Quién habló?', en='Who spoke?'),
    'colegio.monja.a_la_pared': dict(speaker='monja', voice='monja', fx='room', es='A la pared.', en='Face the wall.'),
    'colegio.monja.castigo': dict(speaker='monja', voice='monja', fx='room', es='Castigo para todas.', en='Punishment for everyone.'),
    'colegio.clara.gracias': dict(
        speaker='clara', voice='clara', fx='room',
        es='Gracias por venir. Yo llamé en 1984 y nadie vino. ¿Quién te pasó mi llamada? ...Tené cuidado con quien te llama con tu voz.',
        say='Gracias por venir. Yo llamé en mil novecientos ochenta y cuatro, y nadie vino. ¿Quién te pasó mi llamada? ...Tené cuidado con quien te llama con tu voz.',
        en='Thank you for coming. I called in 1984 and nobody came. Who passed you my call? ...Be careful with whoever calls you with your own voice.'),
    'colegio.madre.aja': dict(speaker='madre', voice='madre', fx='room', es='Ajá.', en='Aha.'),
    'colegio.alumnas.shhh': dict(speaker='coro', voice='coro', fx='room', es='¡SHHHHHH!', en='SHHHHHH!'),
}

# Text shown big on screen (no audio): prayers the player must say aloud, the file, the diary.
TEXTS = {
    'colegio.oracion.1': ('Dios te salve, María, llena eres de gracia, el Señor es contigo.',
                          'Hail Mary, full of grace, the Lord is with thee.'),
    'colegio.oracion.2': ('Bendita tú eres entre todas las mujeres, y bendito es el fruto de tu vientre, Jesús.',
                          'Blessed art thou among women, and blessed is the fruit of thy womb, Jesus.'),
    'colegio.oracion.3': ('Santa María, Madre de Dios, ruega por nosotros pecadores, ahora y en la hora de nuestra muerte. Amén.',
                          'Holy Mary, Mother of God, pray for us sinners, now and at the hour of our death. Amen.'),
    'colegio.legajo': ('Nombre religioso: Sor María de la Agonía. Nombre secular: CLARA INÉS BUSTOS. Baja: 22/6/1984. «No figura. No se busca.»',
                       'Religious name: Sister Maria of the Agony. Secular name: CLARA INES BUSTOS. Discharged: 22/6/1984. "Not on record. Not to be searched for."'),
    'colegio.diario': ('21/6. Las escucho cantar al revés. Lo hicieron sin mí. Eran siete. EL LIBRO DICE OCHO.',
                       '21/6. I hear them singing backwards. They did it without me. There were seven. THE BOOK SAYS EIGHT.'),
    'colegio.silencio': ('Silencio. Quince segundos. Ni una palabra.', 'Silence. Fifteen seconds. Not a word.'),
    'colegio.reglamento': ('1. Silencio. 2. En el colegio se camina. No se corre. 3. Toda voz será escuchada.',
                           '1. Silence. 2. In this school we walk. No running. 3. Every voice will be heard.'),
    'colegio.reglas': ('SI LA ILUMINÁS, SE QUEMA. SI HACÉS RUIDO, YA TE ESCUCHÓ. NO SE CORRE EN LOS PASILLOS.',
                       'LIGHT BURNS HER. IF YOU MAKE NOISE, SHE ALREADY HEARD YOU. NO RUNNING IN THE HALLS.'),
}
