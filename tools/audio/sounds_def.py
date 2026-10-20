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
    # ---- case 1: Colegio Santa Ines (SFX; spoken lines are 'line.*', see tools/audio/lines.py)
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
}


try:
    from lines import LINES as _LINES
except ImportError:  # imported from another directory
    import importlib.util as _u, os as _os
    _spec = _u.spec_from_file_location('lines', _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'lines.py'))
    _m = _u.module_from_spec(_spec)
    _spec.loader.exec_module(_m)
    _LINES = _m.LINES
# every voiced line is its own event 'line.<id>' (file sounds/line/<id with dots -> slashes>.ogg); subtitle = the line
LINE_EVENTS = {'line.' + k: v for k, v in _LINES.items() if v.get('voice')}


def java_name(s):
    return s.replace('.', '_').upper()
