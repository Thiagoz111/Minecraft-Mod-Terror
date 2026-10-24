# -*- coding: utf-8 -*-
"""Master list of DEAD LINE sound events.

name -> (variants, subtitle_es, subtitle_en, stream)
Generates assets/deadline/sounds.json, lang subtitle keys and the Java ModSounds class.
"""
SOUNDS = {
    # phone
    'phone.vibrate': (1, 'El celular vibra', 'Phone vibrates', False),
    'phone.notify': (1, 'Mensaje nuevo', 'New message', False),
    'phone.accept': (1, 'Caso aceptado', 'Case accepted', False),
    'teleport.whoosh': (1, 'Transmisión', 'Transmission', False),
    # ambience
    'ambient.casa': (1, 'La casa cruje', 'The house creaks', True),
    'ambient.colegio': (1, 'Coro lejano', 'Distant choir', True),
    'ambient.whispers': (4, 'Susurros', 'Whispers', False),
    'ambient.stinger': (4, 'Algo se acerca', 'Something approaches', False),
    'music.case': (1, 'Música', 'Music', True),
    # stock noises of the house (set pieces and the act script play them; tools/audio/snd_tools.py)
    'horror.heartbeat': (1, 'Latidos', 'Heartbeat', False),
    'horror.footsteps': (3, 'Pasos detrás tuyo', 'Footsteps behind you', False),
    'horror.knock': (3, 'Golpes en la pared', 'Knocking', False),
    'horror.breath': (2, 'Respiración', 'Breathing', False),
    # tools
    'crucifix.activate': (1, 'Crucifijo brilla', 'Crucifix glows', False),
    'crucifix.repel': (1, 'Entidad repelida', 'Entity repelled', False),
    'holy_water.throw': (1, 'Agua bendita lanzada', 'Holy water thrown', False),
    'holy_water.splash': (1, 'Agua bendita salpica', 'Holy water splashes', False),
    'holy_water.sizzle': (1, 'Algo se quema', 'Something burns', False),
    'salt.place': (1, 'Sal derramada', 'Salt poured', False),
    'emf.beep': (1, 'EMF pita', 'EMF beeps', False),
    'flashlight.click': (1, 'Linterna', 'Flashlight clicks', False),
    'flashlight.flicker': (1, 'La linterna parpadea', 'Flashlight flickers', False),
    'spirit_box.static': (1, 'Estática', 'Static', False),
    'spirit_box.voice': (8, 'Una voz responde', 'A voice answers', False),
    'camera.flash': (1, 'Flash', 'Camera flash', False),
    'ritual.chant': (1, 'Rezo en latín', 'Latin chanting', False),
    'ritual.complete': (1, 'Exorcismo completo', 'Exorcism complete', False),
    'jar.capture': (1, 'Alma atrapada', 'Soul captured', False),
    'flare.ignite': (1, 'Bengala encendida', 'Flare ignites', False),
    'flare.burn': (1, 'Bengala arde', 'Flare burns', False),
    # entities
    'poseida.giggle': (2, 'Risa de niña', 'Girl giggles', False),
    'poseida.crack': (2, 'Huesos crujen', 'Bones crack', False),
    'poseida.scream': (1, 'Grito', 'Scream', False),
    'poseida.hurt': (1, 'Lucía se queja', 'Lucia hurts', False),
    'poseida.death': (1, 'Lucía se libera', 'Lucia is freed', False),
    'monja.whisper': (3, 'Rezo invertido', 'Inverted prayer', False),
    'monja.hiss': (1, 'Siseo', 'Hiss', False),
    'monja.scream': (1, 'La monja grita', 'Nun screams', False),
    'monja.hurt': (1, 'La monja se quema', 'Nun burns', False),
    'monja.death': (1, 'La monja se desvanece', 'Nun fades', False),
    'sombra.vanish': (1, 'Se desvanece', 'Vanishes', False),
    'muneca.giggle': (2, 'La muñeca se ríe', 'Doll giggles', False),
    'muneca.creak': (1, 'Porcelana cruje', 'Porcelain creaks', False),
    'anima.moan': (2, 'Lamento', 'Moan', False),
    'jumpscare': (2, '¡!', '!', False),
    'anchor.purify': (1, 'Ancla purificada', 'Anchor purified', False),
    'anchor.pulse': (1, 'Pulso maligno', 'Evil pulse', False),
    'case.solved': (1, 'Caso resuelto', 'Case solved', False),
    # ---- case 1: Colegio Santa Ines (SFX only: nobody speaks)
    'colegio.timbre': (1, 'Suena el timbre', 'School bell rings', False),
    'colegio.campana': (1, 'Campanada', 'Bell tolls', False),
    'colegio.campana_triple': (1, 'Tres campanadas', 'Three bell tolls', False),
    'colegio.pa_chime': (1, 'Megafonía', 'PA chime', False),
    'colegio.viento': (2, 'Viento en los postigos', 'Wind on the shutters', False),
    'colegio.polvo': (1, 'Cae polvo', 'Dust falls', False),
    'door.slam': (2, 'Portazo', 'Door slams', False),
    'tiza.escribe': (3, 'La tiza escribe sola', 'Chalk writes by itself', False),
    'tiza.rompe': (1, 'La tiza se quiebra', 'Chalk snaps', False),
    'pupitres.giran': (1, 'Las sillas se arrastran', 'Chairs drag', False),
    'farol.revienta': (3, 'Revienta un farol', 'A lamp bursts', False),
    'luces.fuera': (1, 'Se cortan las luces', 'The lights go out', False),
    'silla.arrastra': (2, 'Una silla se arrastra', 'A chair drags', False),
    'silla.gira': (1, 'Una silla gira', 'A chair turns', False),
    'telefono_baquelita.ring': (1, 'Suena un teléfono viejo', 'Old phone rings', False),
    'telefono.linea': (1, 'Estática en la línea', 'Static on the line', False),
    'mate.sorbo': (1, 'Sorbo de mate', 'Mate sip', False),
    'confesionario.rejilla': (1, 'La rejilla se abre', 'The grille slides', False),
    'espejo.raja': (1, 'El espejo se raja', 'The mirror cracks', False),
    'muro.cae': (1, 'Se derrumba un muro', 'A wall collapses', False),
    'tumba.tapa': (1, 'Piedra sobre piedra', 'Stone grinds', False),
    'regla.rompe': (1, 'La regla se parte', 'The ruler snaps', False),
    'ui.amonestacion': (1, 'Amonestación', 'Reprimand', False),
    'madre.pluma': (1, 'Una pluma escribe', 'A quill scratches', False),
    'dormitorio.respira': (2, 'Respiraciones bajo las sábanas', 'Breathing under the sheets', False),
    'alumna.pasos': (2, 'Pasos de nenas', 'Little footsteps', False),
    'monja.campanita': (1, 'Tilín, tilín', 'A little bell', False),
    'monja.regla_tap': (1, 'Tac... tac...', 'Tap... tap...', False),
    'monja.reglazo': (1, 'Reglazo', 'Ruler strike', False),
    'monja.shh': (1, 'Shhh', 'Shhh', False),
    'monja.burn': (1, 'La monja se quema', 'The nun burns', False),
    'monja.soplido': (1, 'Sopla una vela', 'A candle is blown out', False),
    'monja.ceiling': (1, 'Algo se arrastra por el techo', 'Something crawls on the ceiling', False),
    'monja.mojada': (1, 'Quejido indignado', 'Indignant groan', False),
    'coro.ave_reves': (1, 'Un coro canta al revés', 'A choir sings backwards', True),
    'coro.ave_derecho_1': (1, 'El coro canta', 'The choir sings', True),
    'coro.ave_derecho_2': (1, 'El coro canta', 'The choir sings', True),
    'coro.ave_derecho_3': (1, 'El coro canta', 'The choir sings', True),
    'coro.acorde_final': (1, 'Acorde luminoso', 'Bright chord', False),
    # ---------------------------------------------------------------- case 2: Casa Morales
    'casa.breaker_trip': (1, 'Salta la térmica', 'The breaker trips', False),
    'casa.breaker_reset': (1, 'Vuelve la luz', 'Power comes back', False),
    'casa.tv_static': (1, 'Estática', 'TV static', True),
    'choripan.whine': (2, 'Choripán gime', 'Choripán whines', False),
    'choripan.growl_low': (2, 'Choripán gruñe', 'Choripán growls', False),
    'choripan.crack': (6, 'Crujido húmedo', 'Wet crack', False),
    'choripan.unspool': (1, 'Algo sale y no termina de salir', 'Something keeps coming out', False),
    'choripan.demon_roar': (2, 'Rugido', 'Roar', False),
    'knife.lift': (2, 'Los cuchillos se elevan', 'Knives rise', False),
    'knife.whoosh': (3, 'Un cuchillo vuela', 'A knife flies', False),
    'knife.impact': (3, 'Un cuchillo se clava', 'A knife hits', False),
    'plate.whoosh': (4, 'Un plato vuela', 'A plate flies', False),
    'plate.shatter': (3, 'Un plato se rompe', 'A plate shatters', False),
    'plate.storm': (1, 'Tormenta de platos', 'Storm of plates', False),
    'alacena.golpe': (3, 'Golpean las alacenas', 'Cupboards bang', False),
    'chair.stack': (1, 'Sillas apiladas', 'Chairs stacked', False),
    'door.slam_cascade': (1, 'Portazos en cadena', 'Doors slam in a row', False),
    'bulb.pop': (2, 'Revienta un foco', 'A bulb pops', False),
    'doll.turn': (3, 'Clic de porcelana', 'Porcelain click', False),
    'doll.giggle_chorus': (1, 'Risitas de muñecas', 'Dolls giggle', False),
    'andador.squeak': (3, 'Rueda que chilla', 'Squeaky wheel', False),
    'rocking.creak_slow': (1, 'Mecedora', 'Rocking chair', False),
    'candles.out': (1, 'Se apagan las velas', 'Candles go out', False),
    'wall.break': (1, 'Se derrumba una pared', 'A wall collapses', False),
    'morning.birds': (1, 'Pájaros', 'Birds', True),
    'kettle.whistle': (1, 'Silba la pava', 'Kettle whistles', False),
}


# No character speaks (docs/design/casa_terror.md 0.3): there are no spoken-line events any more. Only non-verbal
# sounds live here; the hunter's own voice imitation goes through Simple Voice Chat (com.deadline.voice).

# --- car / overworld (the hunter's car, tools/audio/snd_car.py; loops are played and pitched by client CarSounds)
SOUNDS.update({
    'car.engine_start': (1, 'Arranca el motor', 'Engine starts', False),
    'car.idle': (1, 'Motor en marcha', 'Engine idles', False),
    'car.rev': (1, 'Motor acelerando', 'Engine revs', False),
    'car.door_open': (1, 'Se abre la puerta del auto', 'Car door opens', False),
    'car.door_close': (1, 'Se cierra la puerta del auto', 'Car door closes', False),
    'car.horn': (1, 'Bocina', 'Car horn', False),
    'car.radio_static': (1, 'Estática de radio', 'Radio static', False),
    'car.gravel': (1, 'Ruedas sobre el ripio', 'Tyres on gravel', False),
    'car.bump': (1, 'El auto choca', 'Car bumps', False),
    'car.lights': (1, 'Clic de las luces', 'Light switch clicks', False),
})
# --- end car / overworld

# --- B3 apparitions (Casa Morales events 33-45, the dog that watches, the long dog; tools/audio/snd_apariciones.py)
SOUNDS.update({
    'aparicion.sombra_paso': (2, 'Pasos pesados', 'Heavy footsteps', False),
    'aparicion.nona_respira': (2, 'Respiración de vieja', 'Old woman breathing', False),
    'aparicion.vidrio_unas': (1, 'Uñas contra el vidrio', 'Nails on the glass', False),
    'aparicion.perro_respira': (2, 'Algo respira como una persona', 'Something breathes like a person', False),
    'aparicion.espejo': (1, 'El espejo zumba', 'The mirror hums', False),
    'aparicion.aliento': (1, 'Un aliento en la nuca', 'Breath on your neck', False),
    'aparicion.mano_rasguno': (2, 'Uñas rascan el piso', 'Nails scrape the floor', False),
    'aparicion.mano_retira': (1, 'Algo se arrastra bajo la cama', 'Something drags under the bed', False),
    'aparicion.cuello': (2, 'Un cuello cruje', 'A neck creaks', False),
    'aparicion.copia': (1, 'Dientes que rechinan', 'Grinding teeth', False),
    'aparicion.techo_corre': (1, 'Algo corre por el techo', 'Something runs across the ceiling', False),
    'aparicion.ofelia': (1, 'Porcelana', 'Porcelain', False),
    'aparicion.sabana': (1, 'Una sábana flamea', 'A sheet flaps', False),
    'aparicion.visitante': (1, 'Una presencia', 'A presence', False),
    'perro_largo.reptar': (1, 'Manos que corren', 'Running hands', False),
    'perro_largo.retrae': (1, 'Algo se recoge', 'Something pulls back', False),
    'perro_largo.respira': (1, 'Jadeo enorme', 'Huge panting', False),
})
# --- end B3 apparitions

# --- B1a poltergeist (Casa Morales events 1-32 and the interactables of 6.3; tools/audio/snd_polter.py)
SOUNDS.update({
    'polter.pasos_arriba': (3, 'Pasos en el piso de arriba', 'Footsteps upstairs', False),
    'polter.golpe': (3, 'Un golpe dentro de la pared', 'A knock inside the wall', False),
    'polter.palmadas': (1, 'Dos palmadas detrás tuyo', 'Two claps behind you', False),
    'polter.risita': (2, 'Una nena se ríe', 'A little girl giggles', False),
    'polter.caja_musica': (1, 'Una cajita de música', 'A music box', False),
    'polter.dentadura': (2, 'Chasquido de dentadura', 'Dentures click', False),
    'polter.susurro': (2, 'Alguien susurra', 'Someone whispers', False),
    'polter.respira': (2, 'Alguien respira a tu lado', 'Someone breathes beside you', False),
    'polter.rezo_reves': (1, 'Un rezo al revés', 'A prayer, backwards', False),
    'polter.rasguno_puerta': (2, 'Algo rasca la puerta', 'Something scratches the door', False),
    'polter.telefono_ring': (1, 'Suena el teléfono', 'The phone rings', False),
    'polter.telefono_respira': (1, 'Estática y una respiración', 'Static and breathing', False),
    'polter.llanto_rejilla': (1, 'Un nene llora en el sótano', 'A child cries in the basement', False),
    'polter.picaporte': (2, 'El picaporte se mueve', 'The door handle moves', False),
    'polter.heladera': (1, 'La heladera zumba', 'The fridge hums', False),
    'polter.papel': (1, 'Algo se mueve en un papel', 'Something moves inside paper', False),
    'polter.canilla': (1, 'Corre el agua', 'Water runs', False),
    'polter.canilla_sangre': (1, 'Algo espeso sale de la canilla', 'Something thick pours from the tap', False),
    'polter.persianas': (1, 'Caen las persianas', 'The blinds crash down', False),
    'polter.persiana': (1, 'Una persiana', 'A roller blind', False),
    'polter.mecedora': (1, 'La mecedora se mece sola', 'The rocking chair rocks by itself', False),
    'polter.cajon': (2, 'Un cajón', 'A drawer', False),
    'polter.cajones': (1, 'Se cierran todos los cajones', 'Every drawer slams shut', False),
    'polter.tele_on': (1, 'Se prende la tele', 'The TV comes on', False),
    'polter.tele_off': (1, 'Se apaga la tele', 'The TV goes off', False),
    'polter.radio': (1, 'Estática de radio', 'Radio static', False),
    'polter.llave_luz': (1, 'Clic', 'Click', False),
    'polter.zumbido': (1, 'Zumba la luz', 'The light buzzes', False),
    'polter.maquina_coser': (1, 'La máquina de coser', 'The sewing machine', False),
    'polter.puerta_lenta': (1, 'Una puerta se abre sola', 'A door creaks open', False),
    'polter.cuadro': (1, 'Un cuadro raspa la pared', 'A picture scrapes the wall', False),
    'polter.objeto': (2, 'Algo te golpea', 'Something hits you', False),
    'polter.vidrio': (2, 'Se rompe un vidrio', 'Glass shatters', False),
})
# --- end B1a poltergeist


# --- B2 hunt (Act 5 "Ella escucha todo": the broken Nona, hiding, holding the breath, 3D jumpscares; tools/audio/snd_hunt.py)
SOUNDS.update({
    'hunt.stinger_nona': (1, 'Un alarido', 'A shriek', False),
    'hunt.stinger_lucia': (1, 'Un grito de nena', 'A girl screams', False),
    'hunt.stinger_copia': (1, 'Dientes y estática', 'Teeth and static', False),
    'hunt.stinger_perro': (1, 'Un rugido húmedo', 'A wet roar', False),
    'hunt.stinger_cara': (1, 'Un chillido demoníaco', 'A demonic screech', False),
    'hunt.bone_crack': (4, 'Huesos que crujen', 'Bones crack', False),
    'hunt.neck_twist': (1, 'Un cuello que gira', 'A neck twists', False),
    'hunt.crawl_tap': (4, 'Manos y pies contra el piso', 'Hands and feet patter', False),
    'hunt.sniff': (3, 'Algo olfatea', 'Something sniffs', False),
    'hunt.hiss': (2, 'Siseo', 'Hiss', False),
    'hunt.groan': (3, 'Un gemido gutural', 'A guttural groan', False),
    'hunt.jaw': (2, 'Chasquido de dentadura', 'Dentures clack', False),
    'hunt.scream': (1, 'La Nona chilla', 'The Nona shrieks', False),
    'hunt.rattle': (2, 'Un picaporte se sacude', 'A door handle rattles', False),
    'hunt.grab': (1, 'Te agarra', 'She grabs you', False),
    'hunt.gasp': (2, 'Te falta el aire', 'You gasp for air', False),
    'hunt.breath_in': (1, 'Contenés la respiración', 'You hold your breath', False),
    'hunt.breath_out': (1, 'Soltás el aire', 'You let your breath out', False),
    'hunt.heartbeat': (1, 'Tu corazón', 'Your heartbeat', False),
    'hunt.chase': (1, 'Te persigue', 'She is after you', True),
})
# --- end B2 hunt

# --- B1b blood, phone, lore (Casa Morales events 46-54, the lore papers; tools/audio/snd_sangre.py)
SOUNDS.update({
    'sangre.gota': (3, 'Gotea algo espeso', 'Something thick drips', False),
    'sangre.escribe': (1, 'Dedos húmedos sobre la pared', 'Wet fingers on the wall', False),
    'sangre.revela': (1, 'Algo está escrito', 'Something is written there', False),
    'sangre.mano_vidrio': (3, 'Una mano golpea el vidrio', 'A hand slaps the glass', False),
    'sangre.arrastre': (1, 'Una mano se arrastra por el vidrio', 'A hand drags down the glass', False),
    'sangre.pisada': (3, 'Pasos descalzos, mojados', 'Wet bare footsteps', False),
    'sangre.burbujea': (1, 'Burbujea algo espeso', 'Something thick bubbles', False),
    'sangre.hunde': (1, 'Algo se hunde', 'Something sinks', False),
    'sangre.dientes': (1, 'Algo chico repiquetea', 'Something small rattles', False),
    'sangre.cajon': (1, 'Un cajón se abre', 'A drawer slides open', False),
    'sangre.respira': (2, 'Algo respira muy cerca', 'Something breathes very close', False),
    'linterna.muere': (1, 'La linterna se muere', 'The flashlight dies', False),
    'celular.obturador': (1, 'Una foto, detrás tuyo', 'A photo, behind you', False),
    'lore.papel': (2, 'Papel viejo', 'Old paper', False),
})
# --- end B1b blood, phone, lore

# --- C set pieces (the acts of Casa Morales: the arrival, the dinner, the car; tools/audio/snd_setpieces.py)
SOUNDS.update({
    'sp.cerrojo': (1, 'Un cerrojo gira', 'A deadbolt turns', False),
    'sp.puerta_cruje': (1, 'Una puerta se abre sola', 'A door creaks open by itself', False),
    'sp.cubiertos': (3, 'Cubiertos contra los platos', 'Cutlery on plates', False),
    'sp.radio_cuna': (1, 'Un nene tararea entre la estática', 'A child hums through the static', True),
    'sp.asiento': (1, 'Cruje el asiento de atrás', 'The back seat creaks', False),
})
# --- end C set pieces

def java_name(s):
    return s.replace('.', '_').upper()
