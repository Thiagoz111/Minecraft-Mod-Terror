# -*- coding: utf-8 -*-
"""On-screen texts of DEAD LINE (no audio).

Nobody speaks in DEAD LINE (docs/design/casa_terror.md 0.3 "Sin dialogos hablados"): the spoken TTS lines, their
speakers and the line.* sound events were removed. What is left here is text shown big on screen (Fx.bigText):
prayers the player must say aloud, the file, the diary, notebooks. Lang keys: deadline.text.<id> (tools/data/gen_data.py).
Story beats reach the player as phone text messages instead (tools/data/lang.py, deadline.msg.* / deadline.thread.*).
"""

# id -> (es, en)
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
    'casa.cuaderno': ('MI AMIGO SE LLAMA LEMAZA', 'MY FRIEND IS CALLED LEMAZA'),
}
