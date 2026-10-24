# -*- coding: utf-8 -*-
"""All player-facing text. ES is the primary language of the mod; EN mirrors it."""

ITEMS = {
    'phone': ('Teléfono DEAD LINE', 'DEAD LINE Phone'),
    'crucifix': ('Crucifijo Bendito', 'Blessed Crucifix'),
    'holy_water': ('Agua Bendita', 'Holy Water'),
    'salt': ('Sal Consagrada', 'Consecrated Salt'),
    'emf': ('Detector EMF', 'EMF Reader'),
    'flashlight': ('Linterna', 'Flashlight'),
    'spirit_box': ('Spirit Box', 'Spirit Box'),
    'camera': ('Cámara de Espíritus', 'Spirit Camera'),
    'ritual_book': ('Libro de Rituales', 'Book of Rites'),
    'spirit_jar': ('Frasco de Almas', 'Spirit Jar'),
    'spirit_jar_full': ('Frasco con Alma', 'Filled Spirit Jar'),
    'silver_dagger': ('Daga de Plata', 'Silver Dagger'),
    'rosary': ('Rosario', 'Rosary'),
    'exorcist_hat': ('Sombrero de exorcista', "Exorcist's Hat"),
    'exorcist_cassock': ('Sotana de exorcista', "Exorcist's Cassock"),
    'exorcist_skirt': ('Faldón de la sotana', 'Cassock Skirt'),
    'exorcist_boots': ('Botas de exorcista', "Exorcist's Boots"),
    'flare': ('Bengala', 'Flare'),
    'inverted_rosary': ('Rosario Invertido', 'Inverted Rosary'),
    'cursed_doll': ('Muñeca de Lucía', "Lucia's Doll"),
}

ENTITIES = {
    'poseida': ('Lucía, la Poseída', 'Lucia, the Possessed'),
    'monja': ('Sor Agonía', 'Sister Agony'),
    'sombra': ('Hombre Sombra', 'Shadow Man'),
    'muneca': ('Muñeca Maldita', 'Cursed Doll'),
    'anima': ('Ánima', 'Lost Soul'),
    'anchor': ('Objeto Maldito', 'Cursed Object'),
    'holy_water': ('Agua Bendita', 'Holy Water'),
    'flare': ('Bengala', 'Flare'),
}

BLOCKS = {
    'salt_line': ('Línea de Sal', 'Salt Line'),
    'ritual_candle': ('Vela Ritual', 'Ritual Candle'),
    'blood_stain': ('Mancha de Sangre', 'Blood Stain'),
}

CASES = {
    'casa': {
        'place': ('Casa Morales', 'The Morales House'),
        'hint': ('', ''),
    },
    'colegio': {
        'place': ('Colegio Santa Inés de la Vigilia', 'Saint Agnes of the Vigil School'),
        'hint': ('Lo que buscan está abajo, en la cripta.', 'What they are looking for is down below, in the crypt.'),
    },
}

BESTIARY = {
    'poseida': ('Lucía jugó con una tabla de espíritus. Algo contestó. Trepa paredes, levita y no puede ser atrapada: sólo exorcizada.',
                'Lucia played with a spirit board. Something answered. She climbs walls, levitates and cannot be jarred: only exorcised.'),
    'monja': ('Una monja expulsada que hizo un pacto. Sólo se mueve en la oscuridad. La luz la congela y la quema.',
              'An expelled nun who made a pact. She only moves in darkness. Light freezes and burns her.'),
    'sombra': ('Espera en lo oscuro, al borde de la vista. Si lo mirás, desaparece. Si no lo mirás, se acerca.',
               'It waits in the dark, at the edge of your vision. Look at it and it disappears. Look away and it comes closer.'),
    'muneca': ('Porcelana poseída. Sólo se mueve cuando nadie la mira.', 'Possessed porcelain. It only moves when nobody is looking.'),
    'anima': ('Almas en pena. Invisibles salvo para la cámara o la luz UV. Dejan un frío inconfundible.',
              'Lost souls. Invisible except to the camera or UV light. They leave an unmistakable chill.'),
}

SPIRIT_BOX = [  # one per spirit_box/voice_N.ogg, in file order (tools/audio/snd_tools.py SPIRIT_LINES)
    ('...Clara... Clara...', '...Clara... Clara...'), ('...ocho...', '...eight...'), ('...shhh...', '...shhh...'),
    ('...mirá...', '...look...'), ('...vacío...', '...empty...'), ('...te veo...', '...I see you...'),
    ('...ayuda...', '...help...'), ('...frío...', '...cold...'),
]

MISC = {
    'itemGroup.deadline': ('DEAD LINE', 'DEAD LINE'),
    'item.deadline.spirit_jar_full.named': ('Frasco con Alma: %s', 'Filled Spirit Jar: %s'),
    'deadline.boss.exorcism': ('EXORCISMO', 'EXORCISM'),
    'deadline.title.solved': ('CASO RESUELTO', 'CASE SOLVED'),
    'deadline.msg.welcome': ('§4[DEAD LINE]§r Tu teléfono está encendido. Tenelo cerca: alguien te va a escribir.',
                             '§4[DEAD LINE]§r Your phone is on. Keep it close: someone is going to write to you.'),
    'deadline.msg.case_failed': ('§4Caso fallido:§r %s. La entidad sigue ahí.', '§4Case failed:§r %s. The entity is still there.'),
    'deadline.msg.no_dimension': ('§cNo se encontró la dimensión del caso.', '§cCase dimension not found.'),
    'deadline.msg.no_money': ('§cNo te alcanza el dinero.', '§cNot enough money.'),
    'deadline.msg.anchored': ('§8Algo la protege... encontrá su objeto maldito.', '§8Something protects it... find its cursed object.'),
    'deadline.msg.anchor_hint': ('§7Está maldito. Usá §bAgua Bendita§7.', '§7It is cursed. Use §bHoly Water§7.'),
    'deadline.msg.anchor_purified': ('§b✟ Objeto purificado.§r La entidad ahora es vulnerable.', '§b✟ Object purified.§r The entity is now vulnerable.'),
    'deadline.msg.stage_jar': ('§6¡Está debilitada!§r Atrapala con el §bFrasco de Almas§r.', '§6It is weakened!§r Trap it with the §bSpirit Jar§r.'),
    'deadline.msg.stage_exorcise': ('§6¡Está atada!§r Mantené el §bLibro de Rituales§r cerca para exorcizarla.', '§6It is bound!§r Hold the §bBook of Rites§r near it to exorcise it.'),
    'deadline.msg.weakened_jar': ('§6Entidad debilitada — usá el Frasco de Almas', '§6Entity weakened — use the Spirit Jar'),
    'deadline.msg.weakened_exorcism': ('§6Entidad atada — recitá el exorcismo', '§6Entity bound — perform the exorcism'),
    'deadline.msg.needs_exorcism': ('§cNo cabe en un frasco. Necesita un exorcismo.', '§cIt will not fit in a jar. It needs an exorcism.'),
    'deadline.msg.too_strong': ('§cTodavía es demasiado fuerte.', '§cIt is still too strong.'),
    'deadline.msg.nothing_to_exorcise': ('§7No hay nada atado cerca.', '§7Nothing bound nearby.'),
    'deadline.msg.evidence': ('§aEvidencia registrada (%s)', '§aEvidence recorded (%s)'),
    'deadline.msg.uv_on': ('§dModo UV', '§dUV mode'),
    'deadline.msg.uv_off': ('§fLuz blanca', '§fWhite light'),
    'deadline.msg.no_battery': ('§cSin batería', '§cBattery dead'),
    'deadline.objective.0': ('Encontrá el objeto maldito y purificalo con agua bendita', 'Find the cursed object and purify it with holy water'),
    'deadline.objective.1': ('La entidad es vulnerable: debilitala', 'The entity is vulnerable: weaken it'),
    'deadline.objective.2': ('Atrapala con el Frasco de Almas', 'Trap it with the Spirit Jar'),
    'deadline.objective.2x': ('Exorcizala con el Libro de Rituales', 'Exorcise it with the Book of Rites'),
    'deadline.objective.3': ('Caso resuelto. Volviendo a casa...', 'Case solved. Heading home...'),
    'deadline.hud.open_phone': ('Abrí el teléfono [%s]', 'Open the phone [%s]'),
    'deadline.hud.reward': ('+$%s', '+$%s'),
    'deadline.hud.failed': ('CASO ABANDONADO', 'CASE ABANDONED'),
    'deadline.phone.case': ('Caso', 'Case'),
    'deadline.phone.shop': ('Tienda', 'Shop'),
    'deadline.phone.bestiary': ('Bestiario', 'Bestiary'),
    'deadline.phone.go_home': ('VOLVER A CASA', 'GO HOME'),
    'deadline.phone.abandon': ('ABANDONAR', 'ABANDON'),
    'deadline.phone.no_case': ('No tenés un caso activo.', 'No active case.'),
    'deadline.phone.busy': ('Terminá tu caso actual primero.', 'Finish your current case first.'),
    'deadline.phone.solved': ('Casos resueltos: %s', 'Cases solved: %s'),
    'deadline.phone.evidence': ('Evidencia: %s', 'Evidence: %s'),
    'deadline.phone.unknown': ('???', '???'),
    'deadline.phone.locked': ('Todavía no la conocés.', 'You have not met it yet.'),
    'deadline.phone.weakness': ('Debilidad', 'Weakness'),
    'deadline.phone.buy': ('COMPRAR', 'BUY'),
    'deadline.phone.home': ('Inicio', 'Home'),
    'deadline.phone.day': ('Día %s', 'Day %s'),
    'deadline.phone.money': ('Saldo', 'Balance'),
    'deadline.phone.objective': ('Objetivo', 'Objective'),
    'deadline.phone.hint': ('Pista', 'Hint'),
    'deadline.phone.sure': ('¿SEGURO? TOCÁ DE NUEVO', 'SURE? TAP AGAIN'),
    'key.deadline.phone': ('Abrir teléfono', 'Open phone'),
    'key.deadline.vhs': ('Modo cámara VHS', 'VHS camera mode'),
    'key.category.deadline.deadline': ('DEAD LINE', 'DEAD LINE'),
}

WEAKNESS = {
    'poseida': ('Exorcismo', 'Exorcism'),
    'monja': ('Luz, crucifijo', 'Light, crucifix'),
    'sombra': ('Mirarlo', 'Looking at it'),
    'muneca': ('No dejar de mirarla', 'Never looking away'),
    'anima': ('Cámara, luz UV, frasco', 'Camera, UV light, jar'),
}

# Scripted case texts (director): chapter cards, objectives, hints, reprimand reasons.
SCRIPT = {
    'deadline.colegio.caption.archivero': ('Un cajón del archivero de la Madre se abre solo.', "A drawer of the Mother's filing cabinet slides open by itself."),
    'deadline.door.locked': ('Está cerrada con llave.', "It's locked."),
    'deadline.casa.fin': ('DEAD LINE', 'DEAD LINE'),
    'deadline.casa.creditos': ('Casa Morales\n\nla Nona · Marta · Jorge · Lucía · Toti · Choripán', 'The Morales House\n\nthe Nona · Marta · Jorge · Lucía · Toti · Choripán'),
    'deadline.colegio.ch.1': ('03:33 · LLEGADA', '03:33 · ARRIVAL'),
    'deadline.colegio.ch.1.sub': ('Colegio Santa Inés de la Vigilia', 'Saint Agnes of the Vigil School'),
    'deadline.colegio.ch.2': ('20:00 · ESTUDIO', '20:00 · STUDY'),
    'deadline.colegio.ch.2.sub': ('Silencio en las aulas.', 'Silence in the classrooms.'),
    'deadline.colegio.ch.3': ('20:45 · CENA', '20:45 · DINNER'),
    'deadline.colegio.ch.3.sub': ('Se come en silencio.', 'We eat in silence.'),
    'deadline.colegio.ch.4': ('21:15 · DIRECCIÓN', "21:15 · PRINCIPAL'S OFFICE"),
    'deadline.colegio.ch.4.sub': ('Se lo llama por megafonía.', 'You are wanted over the PA.'),
    'deadline.colegio.ch.5': ('21:45 · COMPLETAS', '21:45 · COMPLINE'),
    'deadline.colegio.ch.5.sub': ('El coro canta.', 'The choir sings.'),
    'deadline.colegio.ch.6': ('22:00 · GRAN SILENCIO', '22:00 · GREAT SILENCE'),
    'deadline.colegio.ch.6.sub': ('Nadie sale de su cama.', 'Nobody leaves their bed.'),
    'deadline.colegio.ch.7': ('03:00 · HORA MUERTA', '03:00 · DEAD HOUR'),
    'deadline.colegio.ch.7.sub': ('La tercera campanada.', 'The third bell.'),
    'deadline.colegio.ch.8': ('03:33 · MAITINES', '03:33 · MATINS'),
    'deadline.colegio.ch.8.sub': ('Falta una voz.', 'One voice is missing.'),
    'deadline.colegio.ch.9': ('06:00 · LAUDES', '06:00 · LAUDS'),
    'deadline.colegio.ch.9.sub': ('Amanece en Santa Inés.', 'Dawn at Saint Agnes.'),
    'deadline.colegio.obj.entrar': ('Entrá al colegio.', 'Enter the school.'),
    'deadline.colegio.obj.aula': ('Andá al aula de 6°.', 'Go to the 6th grade classroom.'),
    'deadline.colegio.obj.frente': ('Pasá al frente.', 'Come up to the front.'),
    'deadline.colegio.obj.llave': ('Buscá la llave en la cocina.', 'Find the key in the kitchen.'),
    'deadline.colegio.obj.direccion': ('Presentate en Dirección.', "Report to the Principal's office."),
    'deadline.colegio.obj.confesar': ('Confesate antes de Completas.', 'Go to confession before Compline.'),
    'deadline.colegio.obj.coro': ('Subí al coro alto.', 'Go up to the choir loft.'),
    'deadline.colegio.obj.dormitorio': ('Cruzá el dormitorio sin hacer ruido.', 'Cross the dormitory without a sound.'),
    'deadline.colegio.obj.espejo': ('Leé el diario en el espejo del baño.', 'Read the diary in the bathroom mirror.'),
    'deadline.colegio.obj.silencio': ('Salí del Cuarto del Silencio.', 'Get out of the Silence Room.'),
    'deadline.colegio.obj.regla': ('Encontrá la regla en la cripta.', 'Find the ruler in the crypt.'),
    'deadline.colegio.obj.volver': ('¡Volvé a la capilla!', 'Get back to the chapel!'),
    'deadline.colegio.obj.velas': ('Prendé las 7 velas del coro.', 'Light the 7 choir candles.'),
    'deadline.colegio.obj.rezar': ('Ocupá el atril 8 y rezá en voz alta (o arrodillate).', 'Take lectern 8 and pray out loud (or kneel).'),
    'deadline.colegio.obj.romper': ('Rompé la regla.', 'Break the ruler.'),
    'deadline.colegio.obj.volver_casa': ('Volvé a casa.', 'Go home.'),
    'deadline.colegio.hint.entrar': ('La puerta está abierta. Demasiado abierta.', 'The door is open. Too open.'),
    'deadline.colegio.hint.aula': ('La lista se toma en 6°.', 'Roll call is taken in 6th grade.'),
    'deadline.colegio.hint.llave': ('Las llaves cuelgan en la cocina. La cocina está oscura.', 'The keys hang in the kitchen. The kitchen is dark.'),
    'deadline.colegio.hint.direccion': ('Te llamaron por megafonía.', 'They called you over the PA.'),
    'deadline.colegio.hint.confesar': ('Arrodillate (agachate) frente al confesionario de la capilla.', 'Kneel (crouch) at the confessional in the chapel.'),
    'deadline.colegio.hint.dormitorio': ('Moverse con la luna. Quieto cuando se nubla.', 'Move with the moonlight. Freeze when it clouds over.'),
    'deadline.colegio.hint.regla': ('Con la fundadora.', 'With the foundress.'),
    'deadline.colegio.hint.velas': ('Ocho voces al derecho.', 'Eight voices, forwards.'),
    'deadline.colegio.stamp.correr': ('Por correr en el pasillo.', 'For running in the hall.'),
    'deadline.colegio.stamp.gritar': ('Por gritar en la casa del Señor.', "For shouting in the Lord's house."),
    'deadline.colegio.stamp.danos': ('Por daños al edificio. Se notificará a sus padres.', 'For damage to the building. Your parents will be notified.'),
    'deadline.colegio.stamp.lista': ('Por no responder a la lista.', 'For not answering the roll call.'),
    'deadline.colegio.stamp.irrespeto': ('Por faltarle el respeto a la institución.', 'For disrespecting the institution.'),
    'deadline.colegio.stamp.felicitacion': ('FELICITACIÓN', 'COMMENDATION'),
    'deadline.hud.amonestacion': ('AMONESTACIÓN', 'REPRIMAND'),
    'deadline.hud.amonestaciones': ('Amonestaciones: %s', 'Reprimands: %s'),
    'deadline.hud.te_escucha': ('TE ESCUCHA', 'SHE HEARS YOU'),
    'item.deadline.llave_capilla': ('Llave de la capilla', 'Chapel key'),
    'item.deadline.regla_quebracho': ('Regla de quebracho', 'Quebracho ruler'),
    'item.deadline.diario_teresita': ('Diario de Teresita', "Teresita's diary"),
    'item.deadline.agua_canilla': ('Agua bendita', 'Holy Water'),
    'entity.deadline.alumna': ('Alumna', 'Schoolgirl'),
    'entity.deadline.madre': ('Madre Remedios', 'Mother Remedios'),
    'entity.deadline.clara': ('Clara', 'Clara'),
}

# --- phone messages (A1: calls -> WhatsApp-style text threads; docs/design/casa_terror.md 1, 2, 8) ---
# Thread names: deadline.thread.<thread>. Message texts: deadline.sms.<thread>.<id> (com.deadline.phone.PhoneMessages).
SCRIPT.update({
    'deadline.thread.marta': ('Marta Morales', 'Marta Morales'),
    'deadline.thread.desconocido': ('Desconocido', 'Unknown'),
    'deadline.thread.ignacio': ('Padre Ignacio', 'Father Ignacio'),
    'deadline.thread.clara': ('Hermana Clara', 'Sister Clara'),
    # the phone app
    'deadline.phone.messages': ('Mensajes', 'Messages'),
    'deadline.phone.no_messages': ('Sin mensajes.', 'No messages.'),
    'deadline.phone.typing': ('escribiendo...', 'typing...'),
    'deadline.phone.photo': ('Foto', 'Photo'),
    'deadline.phone.location': ('Ubicación', 'Location'),
    'deadline.phone.accept_case': ('Aceptar caso', 'Accept case'),
    'deadline.phone.case_accepted': ('Caso aceptado', 'Case accepted'),
    # case 1: the Colegio (Sister Clara writes; she cannot call: "ella escucha")
    'deadline.sms.clara.hora': ('Perdón la hora. No puedo llamarlo. Ella escucha.', "Sorry about the hour. I can't call you. She listens."),
    'deadline.sms.clara.colegio': ('Colegio Santa Inés de la Vigilia. Cerrado desde 1984.', 'Saint Agnes of the Vigil School. Closed since 1984.'),
    'deadline.sms.clara.coro': ('Las chicas del coro siguen cantando. Al revés.', 'The choir girls are still singing. Backwards.'),
    'deadline.sms.clara.luz': ('Si la ve, ilumínela. La luz la quema.', 'If you see her, shine a light on her. Light burns her.'),
    'deadline.sms.clara.no_corra': ('Y no corra en los pasillos. Nunca.', 'And never run in the halls. Never.'),
    # case 2: Casa Morales, act 0 (after the Colegio)
    'deadline.sms.marta.numero': ('Buenas noches. El padre Ignacio me dio su número.', 'Good evening. Father Ignacio gave me your number.'),
    'deadline.sms.marta.suegra': ('Es mi suegra. Ya no es ella.', "It's my mother-in-law. She isn't herself any more."),
    'deadline.sms.marta.no_llame': ('Por favor venga esta noche. No llame. NO LLAME. Ella escucha todo.',
                                    "Please come tonight. Don't call. DON'T CALL. She hears everything."),
    'deadline.sms.marta.ubicacion': ('Le mando la ubicación.', "I'm sending you the location."),
    # acts 1-6 and the ending (sent by the Casa director)
    'deadline.sms.marta.ya_viene': ('¿Ya viene?', 'Are you on your way?'),
    'deadline.sms.marta.luces_auto': ('Apague las luces del auto cuando llegue.', 'Turn off the car lights when you get here.'),
    'deadline.sms.marta.no_sola': ('No la deje sola con los chicos.', "Don't leave her alone with the kids."),
    'deadline.sms.marta.no_hable': ('No hable. Siéntese.', "Don't speak. Sit down."),
    'deadline.sms.marta.no_duerme': ('Lucía no duerme hace 9 días.', "Lucía hasn't slept in 9 days."),
    'deadline.sms.marta.ropero': ('La escucho hablar de noche con alguien en el ropero.', 'At night I hear her talking to someone in the wardrobe.'),
    'deadline.sms.marta.perro': ('El perro no entra a la casa desde el martes.', "The dog hasn't come into the house since Tuesday."),
    'deadline.sms.marta.no_coma': ('No coma lo que ella le sirva.', "Don't eat what she serves you."),
    'deadline.sms.marta.jorge_cama': ('Jorge no está en la cama.', "Jorge isn't in bed."),
    'deadline.sms.marta.lucia_cama': ('Lucía no está en la cama.', "Lucía isn't in bed."),
    'deadline.sms.marta.pasillo': ('¿Usted está en el pasillo?', 'Are you in the hallway?'),
    'deadline.sms.marta.no_es_usted': ('No es usted el que está en el pasillo.', "It isn't you in the hallway."),
    'deadline.sms.marta.escondase': ('Escóndase.', 'Hide.'),
    'deadline.sms.marta.sotano': ('Estamos encerrados en el sótano.', "We're locked in the basement."),
    'deadline.sms.marta.arriba': ('No sé quién está arriba.', "I don't know who is upstairs."),
    'deadline.sms.marta.no_respire': ('Si la escucha cerca no respire.', "If you hear her close, don't breathe."),
    'deadline.sms.marta.escucha': ('Ella no ve. Ella ESCUCHA.', "She can't see. She LISTENS."),
    'deadline.sms.marta.gracias': ('Gracias por venir.', 'Thank you for coming.'),
    'deadline.sms.marta.ya_somos': ('Ya somos todos.', "We're all here now."),
    'deadline.sms.desconocido.puntos': ('...', '...'),
    'deadline.sms.desconocido.baja': ('bajá', 'come down'),
})
# --- end phone messages

# --- casa:P1 (the family: Marta, Jorge, the Nona, Toti) ---
ENTITIES.update({
    'marta': ('Marta', 'Marta'),
    'jorge': ('Jorge', 'Jorge'),
    'nona': ('La Nona', 'Grandma'),
    'toti': ('Toti', 'Toti'),
})
# --- end casa:P1

# --- car / overworld (the hunter's car, its keys, the GPS of an overworld case)
ITEMS['car_keys'] = ('Llaves del auto', 'Car keys')
ENTITIES['auto'] = ('Auto', 'Car')
MISC.update({
    'key.deadline.car_lights': ('Faros del auto', 'Car headlights'),
    'key.deadline.car_radio': ('Radio del auto', 'Car radio'),
    'deadline.car.brought': ('Tu auto está detrás tuyo.', 'Your car is right behind you.'),
    'deadline.gps.label': ('UBICACIÓN', 'LOCATION'),
})
# --- end car / overworld

# --- B2 hunt (the broken Nona, hiding places, holding the breath)
ENTITIES.update({
    'nona_rota': ('La Nona', 'Grandma'),
    'hide_seat': ('Escondite', 'Hiding place'),
})
MISC.update({
    'key.deadline.breath': ('Contener la respiración', 'Hold your breath'),
})
# --- end B2 hunt

# --- B3 apparitions (Choripán, the long dog, the hand under the bed, the bedsheet)
ENTITIES.update({
    'choripan': ('Choripán', 'Choripán'),
    'choripan_demonio': ('Choripán', 'Choripán'),
    'mano': ('Una mano', 'A hand'),
    'sabana': ('Una sábana', 'A bedsheet'),
})
# --- end B3 apparitions

# --- B1a poltergeist (the interactables of the Casa: what a drawer holds, shown over the hotbar)
MISC.update({
    'deadline.casa.cajon.nada': ('Vacío.', 'Empty.'),
    'deadline.casa.cajon.foto': ('Una foto vieja. Alguien le tachó las caras.', 'An old photo. Somebody scratched the faces out.'),
    'deadline.casa.cajon.rosario': ('Un rosario roto. Las cuentas sueltas.', 'A broken rosary. The beads loose.'),
    'deadline.casa.cajon.dientes': ('Dientes. Humanos.', 'Teeth. Human.'),
    'deadline.casa.cajon.carta': ('Una carta. "P. Anselmo, 1961".', 'A letter. "Fr. Anselmo, 1961".'),
})
# --- end B1a poltergeist

# --- B1b blood, phone, lore (events 46-54: Marta's extra texts per act, msg_marta; the papers of the house, LoreBook)
SCRIPT.update({
    # msg_marta: a second pool per act, never the ones the act script sends on its own clock (8)
    'deadline.sms.marta.solo': ('Venga solo.', 'Come alone.'),
    'deadline.sms.marta.no_pare': ('No pare en la ruta. Por nada.', "Don't stop on the road. Not for anything."),
    'deadline.sms.marta.no_mire': ('No la mire a los ojos.', "Don't look her in the eyes."),
    'deadline.sms.marta.cubiertos': ('Coma despacio. Que no se oigan los cubiertos.', "Eat slowly. Don't let the cutlery make a sound."),
    'deadline.sms.marta.fotos_nono': ('En el escritorio del Nono hay fotos del 61. Mírelas.',
                                      "In Nono's study there are photos from '61. Look at them."),
    'deadline.sms.marta.cuaderno': ('Lucía escribe en un cuaderno. No es la letra de ella.',
                                    "Lucía writes in a notebook. It isn't her handwriting."),
    'deadline.sms.marta.cura': ('En el 61 vino un cura. No terminó.', "In '61 a priest came. He didn't finish."),
    'deadline.sms.marta.perro_parado': ('Si ve al perro parado en dos patas, no lo mire.',
                                        "If you see the dog standing on two legs, don't look at it."),
    'deadline.sms.marta.luz_bano': ('No prenda la luz del baño.', "Don't turn on the bathroom light."),
    'deadline.sms.marta.quien_camina': ('Estamos todos en la cama. ¿Quién camina?', "We're all in bed. Who is walking?"),
    'deadline.sms.marta.roperos': ('No abra los roperos.', "Don't open the wardrobes."),
    'deadline.sms.marta.cual_chico': ('Ya no sé cuál de los chicos es el que duerme.',
                                      "I don't know any more which of the children is the one asleep."),
    'deadline.sms.marta.no_corra': ('No corra. Oye los pasos.', "Don't run. She hears footsteps."),
    'deadline.sms.marta.pantalla': ('Apriete el celular contra el pecho cuando vibre.', 'Press the phone against your chest when it buzzes.'),
    'deadline.sms.marta.perdon': ('Perdón por hacerlo venir.', "I'm sorry I made you come."),
    'deadline.sms.marta.no_baje': ('No baje.', "Don't come down."),
    'deadline.sms.marta.no_soy_yo': ('Yo no le escribí «bajá».', "I didn't write 'come down' to you."),
    # the papers (com.deadline.horror.casa.lore.LoreBook): read full screen, nobody reads them aloud
    'deadline.lore.hint': ('clic: dar vuelta · esc: dejarlo', 'click: turn over · esc: put it down'),
    'deadline.lore.cuaderno_lucia.1': (
        'MI AMIGO SE LLAMA LEMAZA\nMI AMIGO SE LLAMA LEMAZA\nMI AMIGO SE LLAMA LEMAZA\n\nVive en mi ropero. De día no está. '
        'De noche se sienta a los pies de la cama y me mira dormir.',
        "MY FRIEND IS CALLED LEMAZA\nMY FRIEND IS CALLED LEMAZA\nMY FRIEND IS CALLED LEMAZA\n\nHe lives in my wardrobe. In "
        "the daytime he isn't there. At night he sits at the foot of my bed and watches me sleep."),
    'deadline.lore.cuaderno_lucia.2': (
        'Lemaza es muy alto. Para mirarme se tiene que doblar todo, como una percha.\n\nMe dijo que no le cuente a nadie. '
        'Que si hablo fuerte, ella escucha.',
        'Lemaza is very tall. To look at me he has to fold all the way down, like a coat hanger.\n\nHe told me not to tell '
        'anyone. That if I talk out loud, she hears.'),
    'deadline.lore.cuaderno_lucia.3': ('LEMAZA DICE QUE LA NONA ES SUYA', 'LEMAZA SAYS NONA IS HIS'),
    'deadline.lore.cuaderno_lucia.4': (
        'Dice que la Nona ya fue suya una vez, cuando era chiquita como yo. Que vino un cura y se la sacó, y a él lo '
        'encerraron abajo.\n\nQue ahora volvió a buscarla.',
        'He says Nona was his once before, when she was little like me. That a priest came and took her away from him, '
        'and they locked him downstairs.\n\nThat now he has come back for her.'),
    'deadline.lore.cuaderno_lucia.5': ('Le pregunté qué va a hacer con nosotros.\n\nSe rió con la boca de la Nona.',
                                       "I asked him what he is going to do with us.\n\nHe laughed with Nona's mouth."),
    'deadline.lore.cuaderno_lucia.6': ('LEMAZA LEMAZA LEMAZA\nLEMAZA LEMAZA\nLEMAZA\nAZAMEL',
                                       'LEMAZA LEMAZA LEMAZA\nLEMAZA LEMAZA\nLEMAZA\nAZAMEL'),
    'deadline.lore.cuaderno_lucia.7': ('YA SÉ QUE LO ESTÁS LEYENDO', 'I KNOW YOU ARE READING THIS'),
    'deadline.lore.foto_nona_cura.1': ('Pocha y el padre Anselmo.\nLas Glicinas, agosto de 1961.\n\n\nNo la dejen sola.',
                                       "Pocha and Father Anselmo.\nLas Glicinas, August 1961.\n\n\nDon't leave her alone."),
    'deadline.lore.foto_nelida.1': ('Nélida y Ofelia.\nNavidad de 1960.\n\n\nAntes.', 'Nélida and Ofelia.\nChristmas 1960.\n\n\nBefore.'),
    'deadline.lore.fotos_1961.1': ('Familia Bertolotti.\nJulio de 1961.', 'The Bertolotti family.\nJuly 1961.'),
    'deadline.lore.fotos_1961.2': ('Sótano, 13 de agosto.\nTercera noche.\n\n\nEn la foto no se ve, pero no estábamos solos.',
                                   "Basement, 13 August.\nThird night.\n\n\nYou can't see it in the photo, but we were not alone."),
    'deadline.lore.fotos_1961.3': (
        'EL DIARIO DEL SUR - 18 de agosto de 1961\n\nMURIÓ EL SACERDOTE QUE ATENDIÓ A LA NIÑA DE LAS GLICINAS\n\nEl padre '
        'Anselmo Ruiz, de 41 años, fue hallado sin vida en la casa parroquial de Nuestra Señora del Carmen.\n\nVecinos del '
        'pasaje Las Glicinas aseguran que durante cuatro noches se oyeron rezos en el sótano de la familia Bertolotti, '
        '«como si alguien los dijera al revés».\n\nLa niña, de 8 años, se encuentra bien.',
        'EL DIARIO DEL SUR - 18 August 1961\n\nPRIEST WHO TENDED THE LAS GLICINAS GIRL IS DEAD\n\nFather Anselmo Ruiz, 41, '
        'was found dead in the parish house of Our Lady of Carmel.\n\nNeighbours on Las Glicinas lane say that for four '
        'nights prayers were heard from the Bertolotti family\'s basement, "as if someone were saying them '
        'backwards".\n\nThe girl, aged 8, is well.'),
    'deadline.lore.cartas_anselmo.1': (
        '12 de agosto de 1961\n\nMonseñor:\n\nLa niña Bertolotti no está enferma. Habla con una voz que no es la suya y '
        'contesta en latín preguntas que todavía no le hice.\n\nPido su autorización para continuar.\n\nP. Anselmo Ruiz\n'
        'Nuestra Señora del Carmen',
        '12 August 1961\n\nMonsignor,\n\nThe Bertolotti girl is not ill. She speaks with a voice that is not hers and '
        'answers in Latin questions I have not yet asked.\n\nI ask your permission to continue.\n\nFr. Anselmo Ruiz\nOur '
        'Lady of Carmel'),
    'deadline.lore.cartas_anselmo.2': (
        '14 de agosto de 1961\n\nCuarta noche. Dice llamarse LEMAZA y lo escribe en las paredes con las uñas. Dice que al '
        'revés se lee su nombre verdadero.\n\nLo saqué de la niña. No pude sacarlo de la casa. Tapamos el cuarto con '
        'ladrillo y cal.\n\nA.',
        '14 August 1961\n\nFourth night. It calls itself LEMAZA and writes it on the walls with its nails. It says its '
        'true name is read backwards.\n\nI got it out of the girl. I could not get it out of the house. We walled up the '
        'room with brick and lime.\n\nA.'),
    'deadline.lore.cartas_anselmo.3': (
        '16 de agosto de 1961\n\nSeñora Bertolotti:\n\nNo abran el cuarto del sótano. Nunca. Si la nena vuelve a '
        'nombrarlo, no le contesten. No hablen de él en voz alta.\n\nEscucha. Escucha todo.\n\nQue Dios me perdone.\n'
        'P. Anselmo',
        '16 August 1961\n\nMrs Bertolotti,\n\nDo not open the basement room. Ever. If the girl names it again, do not '
        'answer her. Do not speak of it out loud.\n\nIt listens. It listens to everything.\n\nMay God forgive me.\nFr. '
        'Anselmo'),
    'deadline.lore.misal_anselmo.1': (
        'RITUALE ROMANUM\nDe exorcizandis obsessis a daemonio\n\n\nNo contesta a su nombre.\nContesta a su nombre al '
        'revés.\n\nSi lo nombran, oye.\nSi lo oyen, vuelve.\n\nA.',
        'RITUALE ROMANUM\nDe exorcizandis obsessis a daemonio\n\n\nIt does not answer to its name.\nIt answers to its '
        'name backwards.\n\nName it, and it hears.\nHear it, and it comes back.\n\nA.'),
    'deadline.lore.rosario_roto.1': ('El hilo no está cortado. Está mordido.', "The string wasn't cut. It was bitten."),
})
# --- end B1b blood, phone, lore
