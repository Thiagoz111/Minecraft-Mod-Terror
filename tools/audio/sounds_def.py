# -*- coding: utf-8 -*-
"""Master list of DEAD LINE sound events.

name -> (variants, subtitle_es, subtitle_en, stream)
Generates assets/deadline/sounds.json, lang subtitle keys and the Java ModSounds class.
"""
SOUNDS = {
    # phone
    'phone.ring': (1, 'El teléfono suena', 'Phone rings', False),
    'phone.vibrate': (1, 'Vibración', 'Phone vibrates', False),
    'phone.notify': (1, 'Notificación', 'Notification', False),
    'phone.accept': (1, 'Llamada aceptada', 'Call accepted', False),
    'phone.hangup': (1, 'Llamada cortada', 'Call ended', False),
    'phone.voice': (6, 'Voz al teléfono', 'Voice on the phone', False),
    'teleport.whoosh': (1, 'Transmisión', 'Transmission', False),
    # ambience
    'ambient.casa': (1, 'La casa cruje', 'The house creaks', True),
    'ambient.colegio': (1, 'Coro lejano', 'Distant choir', True),
    'ambient.whispers': (4, 'Susurros', 'Whispers', False),
    'ambient.stinger': (4, 'Algo se acerca', 'Something approaches', False),
    'music.case': (1, 'Música', 'Music', True),
    # sanity hallucinations
    'sanity.heartbeat': (1, 'Latidos', 'Heartbeat', False),
    'sanity.whisper': (5, 'Alguien susurra tu nombre', 'Someone whispers your name', False),
    'sanity.footsteps': (3, 'Pasos detrás tuyo', 'Footsteps behind you', False),
    'sanity.knock': (3, 'Golpes en la pared', 'Knocking', False),
    'sanity.breath': (2, 'Respiración', 'Breathing', False),
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
    'pills.swallow': (1, 'Pastillas', 'Pills', False),
    'flare.ignite': (1, 'Bengala encendida', 'Flare ignites', False),
    'flare.burn': (1, 'Bengala arde', 'Flare burns', False),
    # entities
    'poseida.giggle': (2, 'Risa de niña', 'Girl giggles', False),
    'poseida.demon': (5, 'Voz demoníaca', 'Demonic voice', False),
    'poseida.crack': (2, 'Huesos crujen', 'Bones crack', False),
    'poseida.scream': (1, 'Grito', 'Scream', False),
    'poseida.hurt': (1, 'Lucía se queja', 'Lucia hurts', False),
    'poseida.death': (1, 'Lucía se libera', 'Lucia is freed', False),
    'monja.whisper': (3, 'Rezo invertido', 'Inverted prayer', False),
    'monja.hiss': (1, 'Siseo', 'Hiss', False),
    'monja.scream': (1, 'La monja grita', 'Nun screams', False),
    'monja.hurt': (1, 'La monja se quema', 'Nun burns', False),
    'monja.death': (1, 'La monja se desvanece', 'Nun fades', False),
    'sombra.appear': (1, 'Presencia', 'Presence', False),
    'sombra.vanish': (1, 'Se desvanece', 'Vanishes', False),
    'muneca.giggle': (2, 'La muñeca se ríe', 'Doll giggles', False),
    'muneca.creak': (1, 'Porcelana cruje', 'Porcelain creaks', False),
    'anima.moan': (2, 'Lamento', 'Moan', False),
    'jumpscare': (2, '¡!', '!', False),
    'anchor.purify': (1, 'Ancla purificada', 'Anchor purified', False),
    'anchor.pulse': (1, 'Pulso maligno', 'Evil pulse', False),
    'case.solved': (1, 'Caso resuelto', 'Case solved', False),
}


def java_name(s):
    return s.replace('.', '_').upper()
