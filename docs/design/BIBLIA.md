> **Nota del dueño (20/10/2026, posterior a esta biblia): el caso 3 (Streamer / hospital) queda CORTADO.**
> El video tiene 2 casos: 1) Colegio Santa Inés (Sor Agonía) y 2) Casa Morales (Ofelia + Choripán).
> Todo lo que esta biblia dice del hospital, Tomi Dark y El Eco como jefe del caso 3 queda archivado;
> la imitación de voz y el cierre de la metahistoria se reubican dentro de los casos 1 y 2.

# DEAD LINE: la Biblia
### Documento rector del mod y del video (v1, 20/10/2026)

> **Para qué sirve.** Esta biblia manda sobre todo lo demás. `docs/design/00_video.md`, `01_sistemas.md`, `10_monja.md`, `20_muneca.md` y `30_streamer.md` quedan como archivo de ideas. Si algo de esos documentos contradice lo que dice acá, vale lo de acá. Lo que no figura en esta biblia no se construye. Si una idea vieja aparece en una lista de "Cortado", tampoco se vuelve a meter.
>
> **Convenciones.**
> - Prioridad: **P0** = sin esto no se graba · **P1** = sube mucho la calidad · **P2** = solo si sobra tiempo.
> - Tamaño (en días de agente): **S** = 1 día o menos · **M** = 2 a 3 · **L** = 4 a 6.
> - Las marcas `[CLIP]` señalan momentos pensados para Shorts y TikTok. `[JUMPSCARE]` es un susto a pantalla completa (máximo 3 por caso). `[RISA]` es un remate de humor.
> - Los identificadores técnicos (clases, ids de beats, claves de sonido) van en inglés o con la clave del caso.

---

## 0. Decisiones de canon y reglas de oro

### 0.1 Contradicciones resueltas

| Tema | Decisión final | Por qué |
|---|---|---|
| Orden de los casos | **1. Monja → 2. Muñeca + Choripán → 3. Streamer** | La Monja enseña las reglas (luz y silencio). La casa es el pico de espectáculo y de risa en la mitad del video. El hospital es lo más personal (tu voz) y cierra la metahistoria. |
| Claves técnicas | `colegio`, `casa`, `hospital` (+ `base`). Las dimensiones pasan a `caso_colegio`, `caso_casa`, `caso_hospital` y `deadline:base` | Un solo vocabulario para comandos, beats, sonidos y lang. |
| Identidad de cada monstruo | **Cada uno tiene UNA regla y no se repite** (ver 0.2) | El crítico marcó que la monja que "se congela con la luz" y la muñeca que "se mueve cuando no mirás" eran la misma mecánica. |
| Sor Agonía | **Caza por el SONIDO.** La luz la quema y la hace retroceder, pero no la congela ni la deja mirándote al borde del haz. "Prendo, apago" es el ÚNICO gag de luz guionado | Le deja a Ofelia el "se mueve cuando no la mirás". Además, el micrófono pasa a ser parte del terror. |
| Muñeca | Se llama **Ofelia** (no Clarita, que chocaba con Clara del caso 1) | Es el nombre del plan maestro y evita confundir nombres. |
| La Nona | **Se fusionan** la Nona Pocha cómica (mate, chancleta, sorda a conveniencia) y el giro de Nélida, la víctima de 1961 que al final se ofrece al demonio | Recontextualiza todos sus chistes. Los dos remates, "¡SALÍ DE MI NIETA, ATORRANTE!" y la mecedora flotando, son clips. |
| Streamer | **Tomi Dark** (@TomiDarkTV). Lauti Extremo queda cortado | Es el canon del plan maestro, y las orejitas RGB ya forman parte del cold open y de la miniatura. Del diseño de Lauti se conservan el sorteo adeudado, Gonza_Mod y "es el viento, chat". |
| Hospital | **Policlínico San Lázaro, Pabellón 6** (Villa Lucero, partido ficticio). Cerró en julio de 1989 | San Lázaro remite al que vuelve de la muerte. Las fechas del 89 permiten los gags con australes. Antes de grabar se busca el nombre para descartar uno real (ver §4.4). |
| Jefe del hospital | **El Eco**. Se cortan el Dr. Mendizábal/"El Ojo" (se leía como el camarógrafo de Skibidi Toilet y además duplicaba el alcance) y Lauti como acechador | El Eco es el hilo de los tres casos, y un solo monstruo nuevo es más barato. |
| ¿Tomi está vivo? | **Sí.** El Eco le robó la voz y lo tiene en el cajón 14 de la morgue | Habilita la mímica, el modo coprotagonista y el remate "like y suscríbanse... / Te mato". Además evita un tercer final trágico con una mujer mayor. |
| La mamá de Tomi | **Graciela, viva.** Llama ella y escribe en el chat sin que nadie le preste atención ("abrigate, Tomi") | Se descarta el giro "la mamá estaba muerta": era el tercer "quien te llamó no es quien creés" y se veía venir. |
| Quién te llama | Una **escalera única**: caso 1, la que llama es la monja (su pedido de 1984, que la línea te entregó ahora); caso 2, Marta jura que nunca llamó; caso 3, el registro del teléfono de Tomi muestra que tus llamadas salieron de ahí; final, te llamás vos | Cada paso sube un escalón del mismo misterio. No es el mismo truco repetido. |
| Imitación de voz | **1 uso en el caso 1, 2 en el caso 2 y uso pleno en el caso 3**, más el final | Si se gasta temprano deja de asustar. |
| Límite técnico convertido en historia | **El Eco no puede inventar palabras: solo repite lo que escuchó.** Para su voz robótica aprendió a encadenar palabras con las donaciones TTS del stream de Tomi | Es exactamente lo que el mod puede hacer (reproducir lo capturado, más TTS), y queda justificado dentro de la historia. |
| Persistencia de la voz | La memoria RAM se borra al terminar cada caso. Las excepciones son los **clips fijados** (opt-in): `hola`, `nombre`, `acepto`, `presente`, `chori_call`, `tomi_call` y los 6 mejores gritos. Esos se guardan en disco, en la carpeta del mundo, entre sesiones | El final necesita el "¿Hola?" del minuto 1, que se graba en otra sesión. Se borra con `/deadline voice clear`. |
| La muerte | **Nunca hace fallar el caso.** Reaparecés en el checkpoint del capítulo y La Operadora dice: *"DEAD LINE le recuerda que la muerte no lo exime del pago."* | Hoy `CaseManager.onRespawn` limpia el sitio y da el caso por fallado: con eso se perderían 40 minutos de material. |
| Bloques de los sitios | **Kits propios** (`tools/blocks`, 32 px): `colegio_*`, `casa_*`, `hosp_*`. Si un kit no llega a tiempo se usa vanilla como respaldo | El dueño pidió "no uses bloques de Minecraft, diseñá todo". |
| Humanos | Un **rig humano base compartido** (2x, cara de 14×14 o más, mandíbula) con variantes por accesorios | Respeta el nivel de calidad del ART_GUIDE sin pagar 5 rigs completos. |

### 0.2 Las cuatro identidades (una regla por monstruo)

| Monstruo | Su regla, en una frase de cartel | Qué hace el jugador |
|---|---|---|
| **Sor Agonía** | *"Si hacés ruido, ya te escuchó."* | Hablar en susurros, no correr, usar la luz como escudo |
| **Ofelia** | *"Se mueve cuando no la mirás. Donde se sienta, ahí va el demonio."* | Mirarla, flashearla, leer dónde se sienta |
| **Choripán** | *"Sigue siendo un perro."* | Darle de comer (choripán bendito), tirarle cosas para distraerlo |
| **El Eco** | *"La voz es mentira. Las orejitas, no."* | No seguir voces y buscar el brillo RGB en la oscuridad |

### 0.3 Reglas de oro del video
1. **Cada 45–60 s algo corta el patrón** (un susto, un chiste, un cambio de lugar o una llamada). Nunca hay más de 90 s seguidos de caminar.
2. **El humor sale de los humanos y del contexto. Los monstruos siempre dan miedo**, salvo Choripán, que es la excepción absurda planificada: primero asusta y después da risa.
3. **En los 60 s anteriores a un jefe no hay chistes.** Única excepción: la chancleta de la Nona, que cae *entre* las dos fases.
4. **Todo chiste plantado vuelve después como susto** ("Prohibido correr", "Es la humedad", "¿Quién es un buen chico?", las donaciones TTS, "¿Hola?").
5. **Lo que importa pasa en cámara.** Los beats grandes se disparan solo si el jugador está mirando (`observed`). Los cambios de "algo se movió" pasan solo cuando no mira (`unobserved`) y suenan con un acento cuando los descubre.
6. **Ningún clip ni gag clave es opcional.** Todo `[CLIP]` está en el camino crítico o lo fuerza un objetivo.
7. **Nada se lee en silencio.** Como mucho hay un texto grande para leer por caso; el resto llega por audio (llamadas, megafonía, chat con TTS, voces).
8. **Qué evitar:** política o figuras públicas, burlarse de la fe (el villano es el demonio, no la Iglesia; Clara es buena), lugares o tragedias reales, autolesiones, maltrato animal (Choripán termina siempre bien), clubes de fútbol que dividan, y malas palabras en los primeros 30 s, en el título y en la miniatura.

---

## 1. Concepto, metahistoria y estructura del video

### 1.1 Premisa
**Logline:** *"Me llamaron para tres casos: una monja que te castiga si gritás, una familia con un perro salchicha poseído y un streamer que entró a un hospital y no volvió. El tercero me estaba llamando con mi propia voz."*

**Protagonista:** el creador, un **exorcista monotributista** (gag recurrente). Tiene un teléfono maldito, DEAD LINE (tecla G), que suena a las **3:33**. Atiende, acepta y lo teletransporta al caso.

**La Operadora.** Es la voz de DEAD LINE: TTS femenina, calma, burocrática, filtrada como teléfono. Asigna casos, paga, cobra retenciones y lee avisos legales absurdos. Nunca se explica quién es. Al final habla después de tu voz.

**El Eco: la verdad interna (para el equipo, no se cuenta entera en pantalla).**
1. Vive en las líneas telefónicas. Nació en 1989 en el **conmutador** del Policlínico San Lázaro: los 13 pacientes del Pabellón 6 recibían llamadas "de sus familiares" con la voz de sus familiares, y la noche del apagón bajaron al subsuelo siguiendo esas voces. No volvieron.
2. **Solo repite lo que escuchó.** No inventa palabras.
3. En 2026 **Tomi Dark** hizo un stream de 24 horas en el San Lázaro. Desde el conmutador del subsuelo, que todavía daba tono, llamó en vivo "AL NÚMERO MALDITO A LAS 3AM (NO CLICKBAIT)": DEAD LINE. La Operadora aceptó la llamada. El Eco entró al stream, le robó la voz a Tomi y lo guardó en un cajón de la morgue. Con las **donaciones TTS** del chat aprendió a encadenar palabras, y por eso su voz "propia" suena robótica.
4. Con el teléfono de Tomi te llamó a vos. Usó voces que tenía grabadas en la línea: el pedido de auxilio de **Clara en 1984** (caso 1) y la voz de **Marta** (caso 2). Te mandó a lugares donde ibas a **gritar y hablar mucho**: estaba **aprendiendo tu voz**.
5. A **Graciela** (caso 3) no la falsificó: es real. Tomi le había dicho "si no vuelvo, llamá a DEAD LINE". El Eco te deja entrar porque le falta tu último pedazo de voz.
6. Lo atrapás en el frasco, pero tu voz ya está copiada en la línea. El frasco aparece rajado y vacío, y la llamada final viene **de tu número**.

**Semillas en pantalla (3) y giro (1):**

| # | Dónde | Qué ve u oye el público |
|---|---|---|
| S1 | Caso 1, dirección | El teléfono de baquelita suena. Se cruzan 2 s de un stream ("...chicos, llegué al hospital, esto está re turbio...") y después tu propio "presente". Al cierre, Clara: *"Yo llamé en 1984 y nadie vino. ¿Quién te pasó mi llamada? Tené cuidado con quien te llama con tu voz."* |
| S2 | Caso 2, cocina y cuarto de Lucía | Marta: *"¿Yo te llamé? Nos cortaron el teléfono en marzo."* La tablet de Lucía pasa un VOD de Tomi: *"...hoy voy al San Lázaro, si no vuelvo llamen a DEAD LINE, jajaja."* Lucía poseída: *"Él te llamó. Él tiene muchas voces."* |
| S3 | Caso 3, la central | El teléfono de Tomi (es un DEAD LINE igual al tuyo) muestra **tus dos llamadas anteriores como salientes** y una programada: *"HOY 03:33 → [TU NOMBRE]"*. |
| Giro | Final | Reseña: *"El Eco ★★★★★: 'Excelente voz. Ya la tengo.'"* Suena el teléfono y el identificador dice **[TU NOMBRE]**. Atendés y escuchás tu *"¿Hola? ¿Hay alguien?"* del minuto 1, y después tu *"Acepto el caso."* La Operadora: *"Caso aceptado. Ubicación: su domicilio. Pago: no aplica."* El frasco está rajado y vacío, Choripán le gruñe a la puerta y se oye toc, toc, toc. Negro. |

**Hilos baratos entre casos:**
- Grafiti "TOMI DARK ESTUVO ACÁ #NOFAKE" en el muro del colegio.
- El VOD de Tomi en la tablet de Lucía.
- En el chat del hospital: *"tomi ya había ido al colegio de las monjas jaja"* y *"y el perro?? el choripán??"*.
- La **libreta de amonestaciones** te sigue en los tres casos: caso 2, *"Por entrar a casa ajena sin limpiarse los pies"*; caso 3, *"Por transmitir sin permiso"*.
- Ofelia "aparece" en tu casa.

### 1.2 Estructura minuto a minuto (20:00)

| Tiempo | Bloque | Contenido | Intensidad (1–10) | Tono |
|---|---|---|---|---|
| 0:00–0:15 | **Cold open** | Pasillo del hospital en VHS. Tu "¿Tomi...?" vuelve como eco. Montaje relámpago de los tres casos | 9 | Terror |
| 0:15–0:35 | **Título y premisa** | "Soy [Nombre], exorcista monotributista." Logo DEAD LINE en glitch | 3 | Humor seco |
| 0:35–1:20 | **Casa base** | Monoambiente, mate y kit. Primera llamada atendida **con la voz** (se capturan `hola`, `nombre` y `acepto`). Avisos legales | 2→5 | Humor → tensión |
| 1:20–6:40 | **CASO 1: La Monja** (5:20) | Colegio Santa Inés | 4→9 | Terror lento, chistes en los valles |
| 6:40–7:10 | **Transición 1** | Reseña y pago con retención, libreta, llamada de Marta: *"...y el perro. El perro está raro."* | 2 | Humor |
| 7:10–13:05 | **CASO 2: La Muñeca** (5:55) | Casa Morales, Choripán, Jorge, Lucía y la Nona | 3→10 | El más cómico y espectacular |
| 13:05–13:35 | **Transición 2** | Choripán ya vive con vos, Ofelia en tu estante, llamada de Graciela. Choripán llora para que no vayas | 3 | Drama con remate |
| 13:35–18:35 | **CASO 3: El Streamer** (5:00) | Policlínico San Lázaro | 5→10 | Found footage, el más aterrador |
| 18:35–19:40 | **Final y giro** | Estante de trofeos, reseñas, te llamás a vos mismo, el frasco vacío, toc toc toc | 10 | Terror |
| 19:40–20:00 | **Outro y post-créditos** | Fuera de personaje: "¿Parte 2?". Post-créditos: Ofelia en tu cama, "¿Otra vez vos?" | 1 | Risa final |

**Crudo estimado:** caso 1 unos 40 min, caso 2 unos 45, caso 3 unos 40, más base y final unos 15 (con varias tomas).
**Capítulos para la descripción:** 0:00 La llamada · 1:20 La Monja · 7:10 La Casa Morales · 13:35 El Hospital · 18:35 ¿Quién llama?

### 1.3 Cold open (guion segundo a segundo)

| s | Imagen | Audio |
|---|---|---|
| 0.0 | Negro. Pantalla del teléfono: **LLAMADA ENTRANTE · NÚMERO DESCONOCIDO · 3:33 AM** | Vibración y un tono distorsionado |
| 1.5 | Pasillo del hospital en VHS, la linterna temblando (beat `hospital.eco_tomi`) | Vos susurrás: "¿Tomi...?" |
| 3.5 | El mismo plano, más oscuro | Desde el fondo del pasillo, **tu propia voz**: "¿Tomi...?" |
| 5.5 | Primer plano de tu skin, quieto | Vos: "...¿ese fui yo?" |
| 7.0 | Al fondo se prenden **las orejitas de gato RGB** | Silencio total (1 s) |
| 8.0–12.5 | Cortes secos de 0,3 s: la monja a centímetros de la ventanilla, Ofelia girando la cabeza, la boca de Choripán abriéndose en flor, el termo volando, la Nona flotando en la mecedora | Golpes sincronizados y un grito cortado |
| 12.5 | Negro | Vos en off: "Soy exorcista. Y esta noche atendí tres llamadas." |
| 14.0 | Logo **DEAD LINE** en glitch | Corte de estática |

### 1.4 Casa base y primera llamada (0:35–1:20)
**Lugar:** `deadline:base`, un monoambiente de noche fija (ver §2.4/B01). Hay una mesa con mate y termo, una cama, el **estante de trofeos** (vacío, con 3 lugares marcados), la puerta de entrada (marker `base_door`) y una ventana con lluvia.

**Guion de la llamada:**
1. A las 3:33 suena el teléfono (`phone.ring_333`). La pantalla dice: **"Hablá para atender."**
   - Con SVC: lo primero que digas (de 0,6 a 3 s) se guarda con la etiqueta `hola` y la llamada se atiende sola. Se espera "¿Hola? ¿Hay alguien?".
   - Sin SVC: se atiende con un clic.
2. La Operadora: *"Bienvenido a DEAD LINE, la línea que atiende a los que nadie atiende. Esta llamada puede ser grabada para garantizar la calidad espiritual del servicio... y por entidades. ¿Acepta?"* Aparecen [ACEPTO] / [NO ACEPTO] (`ConsentPayload`). Este paso es el consentimiento dentro de la historia; el real ya se dio en la pantalla de opciones del primer arranque.
3. *"Diga su nombre después del tono."* Se guarda con la etiqueta `nombre`.
4. Entra el caso: la llamada de Hermana Clara (§2.1c).
5. *"Para aceptar el caso, diga: 'Acepto el caso'."* Se guarda con la etiqueta `acepto`. Aviso legal y teletransporte.

**Avisos legales de La Operadora** (se rota uno por llamada, `operadora.disclaimer.N`):
- *"DEAD LINE no se responsabiliza por posesiones, desmembramientos ni pérdida de objetos personales."*
- *"Para exorcismos en cuotas, marque 2."*
- *"Si el ente le pide pasar, por favor no lo invite a pasar."*
- *"Su llamada es muy importante para nosotros. Y para ellos."*
- *"DEAD LINE le recuerda que la muerte no lo exime del pago."* (este es el de la muerte)

### 1.5 Transiciones
**Transición 1 (6:40–7:10).** Volvés a la base y la Regla de quebracho queda en el estante.
- El teléfono muestra la reseña *"Hermana Clara ★★★★☆: 'Muy amable. Gritó bastante.'"*
- Pago: **$1.200**, *"retención: −$300"*.
- Notificación: *"LIBRETA DE COMUNICACIONES: [NOMBRE] registra N amonestaciones. Conducta: REGULAR. Se solicita firma de padre, madre o tutor. [FIRMAR]"*. Al tocar suena un reglazo.
- Suena el teléfono: **Marta** (§2.2c). Remata: *"...y el perro. El perro está raro."*

**Transición 2 (13:05–13:35).**
- Choripán duerme en tu cama con la bufanda roja de la Nona.
- **Ofelia aparece sentada en tu estante**, al lado del frasco vacío: *"¿Qué hacés acá vos?"* `[RISA]`
- Reseña *"Marta Morales ★★★☆☆: 'Salvó a mi hija. Se llevó al perro.'"* y pago **$18.000**, *"ajuste por inflación"*.
- La tienda sube precios: *"Agua bendita: antes $50, ahora $900."*
- Llama **Graciela** (§2.3c). Mientras habla se oyen 4 s del último stream de Tomi.
- Choripán gime y te tironea el pantalón. Vos: *"Esta vez vas a quedarte, Chori."*

### 1.6 Final, giro y outro (18:35–20:00)
1. **Base (0:15).** El estante tiene la Regla, a Ofelia (cosida) y el **frasco de El Eco**, con el brillo RGB latiendo adentro. Mate. Choripán duerme.
2. **Reseñas (0:10).**
   - *"Graciela ★★★★★: 'Me lo trajo. Sin abrigo, pero me lo trajo.'"*
   - Pago **$1.500.000**, *"y ni así alcanza"*.
   - La pantalla se refresca y aparece una reseña nueva: *"El Eco ★★★★★: 'Excelente voz. Ya la tengo.'"*
3. **La llamada (0:25).**
   - El identificador dice **[TU NOMBRE]** y tu propio número.
   - Atendés con la voz ("¿Hola?") y del otro lado se oye tu "¿Hola? ¿Hay alguien?" del minuto 1 (QUOTE `hola`, InHead, RADIO).
   - Después tu *"Acepto el caso."* (QUOTE `acepto`).
   - La Operadora, normal: *"Caso aceptado. Ubicación: su domicilio. Pago: no aplica."*
4. **Remate (0:15).**
   - Paneo al frasco: rajado, vacío, sin brillo.
   - Choripán se para y le gruñe a la puerta (`base_door`).
   - **Toc, toc, toc.** Negro y logo.
5. **Outro (0:15).** Fuera de personaje: *"Si llegamos a X likes, hay parte 2."* Pantalla final.
6. **Post-créditos (0:05).** Ofelia sentada en tu cama. *"¿Otra vez vos?"*

### 1.7 Presupuesto de imitación de voz (todo el video)

| Momento | Captura | Uso | Intento / Emisor / FX |
|---|---|---|---|
| Minuto 1 | `hola`, `nombre`, `acepto` (fijados) | — | — |
| Caso 1, la lista | `presente` (fijado) y calibración del micrófono | — | — |
| **Caso 1, uso 1** | — | Teléfono de la dirección: tu "presente" por la línea, primero normal y después al revés | QUOTE `presente` / At(teléfono) / RADIO → BACKWARDS |
| Caso 2, Marta te pide que lo llames | `chori_call` (fijado) | — | — |
| **Caso 2, uso 1** | — | Desde arriba, a oscuras: tu "¡Choripán, vení!" | QUOTE `chori_call` / At(escalera_arriba) / DRY con reverb de cuarto |
| **Caso 2, uso 2** | — | Detrás tuyo, en la pelea con Lucía: **tu nombre con tu voz** | QUOTE `nombre` / Follow(lucia) / DRY |
| Caso 3, "Llamá a Tomi" | `tomi_call` (fijado) | **Eco inmediato** "¿Tomi...?" (cold open) | ECHO / At(fondo_pasillo) / DRY con retardo de 0,3 s |
| Caso 3 | Gritos del caso | **Repetición** por megafonía, normal y en cámara lenta | SCREAM / Speakers(pa) / PA, después SLOWMO |
| Caso 3 | — | **Tu voz** desde el pasillo opuesto | CALL (prefiere `tomi_call`) / At(pasillo_fin) / DRY |
| Caso 3 | Gritos fijados de los casos 1 y 2 | **Popurrí de tus gritos** desde todos los teléfonos de pared | CHOIR / Speakers(telefonos) / CHOIR |
| Caso 3, jefe | Cualquier clip | Señuelos desde direcciones falsas y el **ruego** durante "Finalizar transmisión" | CALL/QUOTE / At(teléfonos) / DRY o SLOWMO |
| P1 | Voz en vivo | El Eco te agarra y **tu voz sale de su boca** | steal REDIRECT |
| Final | — | `hola` y `acepto` por el teléfono | QUOTE / InHead / RADIO |

**Sin SVC o sin clip disponible:** cada uso tiene una línea TTS de respaldo (`mimic.fallback.*`, voz `em_alex` procesada) con el subtítulo *"(una voz parecida a la tuya)"*, más un espacio en el resource pack para que el creador ponga su propia grabación.

### 1.8 Ritmo, humor y miedo
**Ciclo base** (se repite en cada bloque):
1. Construcción: 20–60 s de silencio, ambiente y pasos.
2. Falso susto: una rata, Choripán, la Nona o Toti.
3. Susto real, entre 2 y 8 s después del falso.
4. Reacción: 2–4 s sin cortar.
5. Descompresión cómica: 10–30 s.

**Proporciones:**
- Cerca de **70 % tensión y 30 % alivio** en todo el video.
- La risa vive en llegadas, investigaciones, transiciones y cierres.
- Los clímax son 100 % terror.
- El hospital es el que menos humor tiene: chat, mímica y el remate de Tomi.

**Trucos de edición:**
- 2 a 3 s de silencio antes de cada susto grande.
- Cortar en el pico del grito.
- Congelado con zoom para los chistes, como mucho una vez cada 2 minutos.
- VHS solo en el cold open y en el hospital.
- **No musicalizar el apagón final del caso 3**: los 5 s de negro van enteros.

### 1.9 Gags recurrentes

| Gag | Cómo se repite | Remate |
|---|---|---|
| Avisos legales de La Operadora | Uno en cada llamada | Al final llega después de tu propia voz |
| Reseñas con estrellas (estilo marketplace) | Al cerrar cada caso | La reseña de El Eco abre el giro |
| Inflación | $1.200 → $18.000 → $1.500.000. Retenciones absurdas, la tienda remarca precios, el menú en australes del hospital | "Pago: no aplica." |
| Libreta de amonestaciones | Se estrena en el colegio, sigue en la casa ("sin limpiarse los pies") y en el hospital ("transmitir sin permiso") | Notificación final, con conducta que va empeorando |
| El chiste que vuelve como susto | "Prohibido correr", "Es la humedad", "¿Quién es un buen chico?", donaciones TTS, "¿Hola?" | Cada uno vuelve en versión terror |
| Ofelia aparece | Estante (transición 2), en la morgue (opcional, P2: "¿¡Cómo llegaste acá!?"), en tu cama | Post-créditos |
| El mate | El "lavado desde 1984" de la Madre, el termo que vuela, el mate de la Nona, el mate de Cacho | — |
| "Todo bajo control." | El creador lo dice como mucho una vez por caso | Corte seco al caos |

### 1.10 Shorts (16 momentos diseñados para clipear)

| # | Short | Beat | Dur. |
|---|---|---|---|
| 1 | "No grites en este colegio" | `colegio.*` (gritás y aparece adelante) | 15–25 s |
| 2 | "NO MIRES ATRÁS... TE DIJE" | `colegio.pizarron` | 12 s |
| 3 | "Prendo, apago" | `colegio.prendo_apago` | 15 s |
| 4 | "Mi boletín: grita mucho" | `colegio.direccion` | 8 s |
| 5 | "El teléfono tenía MI voz" | `colegio.telefono` | 15 s |
| 6 | "Recé a los gritos para ganarle a la monja" | `colegio.maitines` | 25 s |
| 7 | "Lucía no tiene celular" | `casa.ya_llego` | 10 s |
| 8 | "¡EL TERMO NO!" | `casa.cocina` | 12 s |
| 9 | "¿Quién es un buen chico? YO NO." | `casa.buen_chico` | 10 s |
| 10 | "El perro que no termina de salir" | `casa.cucha` | 20 s |
| 11 | "¡OCUPADO! ESTOY EN RANKED" | `casa.ropero` | 12 s |
| 12 | "Le hice un choripán al demonio" | `casa.parrilla` | 20 s |
| 13 | "La Nona vs. el demonio" (chancleta) | `casa.chancleta` | 10 s |
| 14 | "Repetición en cámara lenta (de MI grito)" | `hospital.repeticion` | 15 s |
| 15 | "La entidad usó MIS GRITOS" | `hospital.popurri` | 20 s |
| 16 | "Me llamé a mí mismo" | `final.llamada` | 25 s |

**Formato:** 9:16 con la acción centrada (el HUD tiene modo `shorts`, ver §3.11), acción desde el primer cuadro, subtítulos y el final enlazado con el principio.

### 1.11 Títulos y miniaturas (para probar con "Test & Compare")

| # | Título | Miniatura |
|---|---|---|
| 1 | **Me llamaron para EXORCIZAR A UN PERRO en Minecraft** | Choripán saliendo de la cucha con la boca en flor, tu cara de espanto, "CHORIPÁN??" |
| 2 | **Un STREAMER entró a este hospital y NUNCA VOLVIÓ... fui a buscarlo** | Pasillo negro, orejitas RGB rosas al fondo, chat con "ESTÁ ATRÁS" |
| 3 | **La entidad aprendió a hablar CON MI VOZ (Minecraft Terror)** | Tu cara y una onda de audio saliendo de la boca de El Eco: "ESA NO ES MI VOZ" |
| 4 | **No grites en este colegio... (Minecraft)** | La monja en el marco de una puerta, a centímetros, con el cartel "SILENCIO" |
| 5 | **Soy EXORCISTA y mi teléfono suena a las 3:33** | Teléfono gigante con "LLAMADA ENTRANTE 3:33 AM" y las tres siluetas |

Se sale con la 1 o la 3, y la 2 queda como alternativa. Las poses se arman con `/deadline pose` y `/deadline freeze` (§4).

---

## 2. Los tres casos

---

### 2.1 CASO 1: LA MONJA · "Colegio Santa Inés de la Vigilia"

#### a. Ficha

| | |
|---|---|
| Clave / dimensión | `colegio` / `deadline:caso_colegio` (se renombra desde `caso_convento`) |
| Lugar | Internado religioso de señoritas en Villa Santa Inés (pueblo ficticio, Valle de Punilla, Córdoba). Estilo colonial cordobés: revoque blanco descascarado, tejas, postigos verdes, damero blanco y negro. Lo gótico se reserva para la capilla y la cripta |
| Antagonista | **Sor Agonía**: Sor María de la Agonía, nombre secular **Clara Inés Bustos**. La posee *La Celadora*, un demonio que castiga la voz |
| Ancla | **La Regla de quebracho** (la de la Madre Remedios), escondida en la tumba de la cripta |
| Mecánicas estrella | Caza por ruido y voz · amonestaciones · **rezar en voz alta** como final |
| Nombres en pantalla | Clara / Sor Agonía, la Madre Remedios, Paloma (la líder del coro), Teresita (solo en el diario) |
| Edición | 5:20 (1:20–6:40) |

#### b. Historia
**Lo que entiende el público (en orden):**
1. **El rumor** (llamada y reglamento): una monja cruel castiga a quien hace ruido.
2. **La dirección:** el legajo dice *"Nombre religioso: Sor María de la Agonía. Nombre secular: CLARA INÉS BUSTOS"*. La que te pidió ayuda es la monja. En el teléfono se oye a Clara en 1984: *"...les dije que me llevaran a mí."* No era cruel: se sacrificó.
3. **El espejo:** el diario de Teresita, tres líneas grandes: *"Lo hicieron sin mí. Eran siete. EL LIBRO DICE OCHO."*
4. **Maitines:** vos sos la octava voz.

**Verdad interna:**
- 1984. La directora, la **Madre Remedios Iturbe**, gobierna con la regla de quebracho y la frase "el silencio es la primera oración".
- **Sor María de la Agonía (Clara)**, directora del coro, cumple los castigos pero a escondidas deja cantar a las chicas.
- **Teresita Albornoz** (11 años) encuentra un libro viejo en la sección bajo llave. Por cantar en el dormitorio la Madre la encierra en el **Cuarto del Silencio**.
- El **21/6/84 a las 3:00**, en la tercera campanada, las **7 chicas del coro** (con Paloma Ferreyra a la cabeza) cantan el Ave María al revés en el coro alto. Ponen la regla de la Madre en el atril y **nombran a "la Madre Remedios"** para que la castiguen. El libro pedía **8 voces** y eran 7.
- Clara entra, agarra la regla y grita **"¡Llevame a mí! ¡A mí!"**. La Celadora entra en ella. Esa noche las 7 pierden la voz y la boca y quedan sentadas en la cripta, mirando la pared.
- Teresita se salva porque se queda callada. Al día siguiente esconde la regla en la tumba de la fundadora, "para que no le pegue a nadie más", y sin saberlo ancla al demonio.
- La Madre tapia la cripta y declara "fugadas" a las chicas. El colegio cierra.
- Desde entonces el colegio repite cada noche aquella noche.
- En 1984, desde el teléfono de la dirección, Clara llamó pidiendo ayuda y nadie vino. La línea guardó esa llamada (S1).

#### c. Llamadas
**Llamada del caso. Hermana Clara** (voz real recomendada: mujer joven, susurrando y apurada; el TTS queda de respaldo). En el avatar, una monja joven en penumbra con un brillo naranja apenas visible en los ojos:
> *"Perdón que llamo tan tarde... no puedo hablar fuerte, ella escucha. Colegio Santa Inés. Si la ves, apagá todo... ¡no, no, al revés! Prendé todo. La luz la quema. Y por favor... no se corre en los pasillos."*

Al cortar se oye un "shhh" que no es de ella. Aviso legal de La Operadora.

**Llamadas durante el caso** (P1, cortas, al teléfono del jugador):
- Al empezar el Gran Silencio: *"No prenda la luz en el dormitorio. Y si me ve sentada... no me mire mucho."*
- Al entrar a la capilla en Maitines: *"Falta una voz. Siempre faltó una."*

#### d. Reglas del caso (cartel en pantalla la primera vez que caza, `colegio.reglas`)
> **SI LA ILUMINÁS, SE QUEMA. SI HACÉS RUIDO, YA TE ESCUCHÓ. NO SE CORRE EN LOS PASILLOS.**
> *(Usá la tecla de SUSURRO.)*

#### e. Capítulos, objetivos y checkpoints
Cada capítulo empieza con una campana y un cartel de título (separador de capítulo para el editor). También es un checkpoint (`/deadline chapter N`). Si el jugador pasa **3 minutos** sin avanzar, aparece la pista; a los 5 minutos, la Madre señala hacia dónde ir (P1).

| Cap. | Cartel | Objetivo en el HUD | Pista | Termina cuando | Checkpoint |
|---|---|---|---|---|---|
| 1 | **03:33 · LLEGADA** | "Entrá al colegio." | "La puerta está abierta. Demasiado abierta." | Cruzás el umbral del hall | `spawn` |
| 2 | **20:00 · ESTUDIO** "Silencio en las aulas." | "Andá al aula de 6°." / "Pasá al frente." | "La lista se toma en 6°." | Termina la pregunta 3 | `aula_puerta` |
| 3 | **20:45 · CENA** "Se come en silencio." | "Buscá la llave en la cocina." | "Las llaves cuelgan en la cocina. La cocina está oscura." | Agarrás la llave del tablero | `refectorio` |
| 4 | **21:15 · DIRECCIÓN** | "Presentate en dirección." | "Te llamaron por megafonía." | Termina la llamada del teléfono | `hall` |
| 5 | **21:45 · COMPLETAS** "El coro canta." | "Confesate antes de Completas." / "Subí al coro alto." | "El confesionario está en la capilla." | Termina el beat de las 8 cabezas | `capilla_puerta` |
| 6 | **22:00 · GRAN SILENCIO** "Nadie sale de su cama." | "Cruzá el dormitorio sin hacer ruido." / "Leé el diario en el espejo del baño." / "Salí del Cuarto del Silencio." | "Moverse con la luna. Quieto cuando se nubla." | Salís del Cuarto del Silencio | `dormitorio_puerta` |
| 7 | **03:00 · HORA MUERTA** "La tercera campanada." | "Encontrá la regla en la cripta." / "¡Volvé a la capilla!" | "Con la fundadora." | Entrás a la capilla | `sacristia` |
| 8 | **03:33 · MAITINES** "Falta una voz." | "Prendé las 7 velas del coro." / "Ocupá el atril 8 y rezá en voz alta." / "Rompé la regla." | "Ocho voces al derecho." | La Celadora en el frasco | `coro_alto` |
| 9 | **06:00 · LAUDES** | "Volvé a casa." | — | Volvés | — |

#### f. El lugar
Origen (0,0,0) en el centro de la puerta principal, a nivel del piso. La fachada está en Z=0, el edificio se extiende hacia +Z y el spawn queda en (0,0,−26) mirando a +Z. Planta baja en y=0 (techo y=5), primer piso en y=6, cripta en y=−6. Hay unas 13 salas jugables y todo lo demás es fachada.

```
PLANTA BAJA                                   FONDO (Z+)
+-----------+------------------+-----------------------------+
| COCINA    | (ventanilla 2x1) |   CAPILLA 11x24, alto 10    |
| 9x7       |                  |   altar, lampara roja,      |
+-----------+   REFECTORIO     |   CONFESIONARIO (oeste),    |
            |   11x13          |   pila bautismal            |
            |                  |   CORO ALTO arriba (y=6),   |
+-----------+------------------+   11x6, del lado entrada    |
|   PASILLO PB 3x30  (6 faroles, guardapolvos)  +---------+  |
+---------+-----------+----------+--------------+SACRIST. |--+
| AULA 6° | HALL 11x9 | DIRECCION|                6x6 ->   |
| 9x7     | doble alt.| 9x7      |                CRIPTA   |
+---------+--[PUERTA]-+----------+-------------------------+
           FRENTE (Z=0)       campanario decorativo (no se entra)
  jardin: gruta de la Virgen (refugio) - reja (Z=-20) - graffiti
1er PISO: DORMITORIO 11x22 (sobre aula y refectorio) | BAÑOS 8x8 | [CUARTO ESPEJO 8x8 sellado]
          pasillo 1P 3x20 (tablas que crujen) -> puerta al CORO ALTO
CRIPTA (y=-6, bajo la capilla): 11x16, nichos, TUMBA de la fundadora, MURO nuevo 7x4 -> SALA DE LAS 7 SILLAS 7x4
CUARTO DEL SILENCIO: 2x3, alto 2, bajo la escalera principal (puerta de hierro que maneja el guion)
```

| Zona | Tamaño | Kit / props | Pistas y beats |
|---|---|---|---|
| **Exterior** | Reja en Z −20 | `colegio_reja`, portón doble con cadena caída, camino de tierra con charcos. **Gruta de la Virgen** con velas que nunca se apagan (luz 12): zona segura y punto de reaparición. Campanario decorativo (silueta para el plano de apertura). Grafitis en TextDisplay: "ACÁ ESPANTAN", **"TOMI DARK ESTUVO ACÁ #NOFAKE"** | `colegio.llegada` |
| **Hall** | 11×9, doble altura | Damero `colegio_piso_damero`. Escalera de roble oscuro al balcón del 1P. **Cuadro de honor**: retrato de la Madre Remedios (pintura 2×3, ojos abiertos/cerrados) y foto **"Coro 1984"** (pintura 4×2 a 64 px/bloque: 7 chicas, un hueco, Hna. Clara joven y la Madre). Cartel grande **"PROHIBIDO CORRER EN LOS PASILLOS"** y "SILENCIO". **Pila de agua bendita** (recarga 2 cargas por capítulo) | `colegio.timbre` |
| **Aula de 6°** | 9×7 | **16 sillas como BlockDisplay** (silla escolar del kit) más pupitres reales. Pizarrón verde 5×2 (`colegio_pizarron`) con TextDisplay de tiza. 4 cuadros de tiza en el piso (a/b/c/d). Tarima, escritorio, crucifijo, mapa. Pupitre 8 con el cartel "T. ALBORNOZ" | Beats 2 a 4 |
| **Pasillo PB** | 3×30 | 6 faroles (fixtures del grupo `pasillo_pb`), percheros con **guardapolvos que se mecen** (BlockDisplay con oscilación), crucifijos, ventanas | `colegio.pasillo` |
| **Refectorio** | 11×13 | Dos mesas largas, bancos, velas en las mesas (grupo `refectorio_velas`), **ventanilla de servicio 2×1** hacia la cocina, con trapdoor | `colegio.prendo_apago` |
| **Cocina** | 9×7 | Fogones, ollas, cadenas, **tablero de llaves** con la llave del pasillo de la capilla. Oscura (luz 0): es su dominio | Ídem |
| **Dirección** | 9×7 | Escritorio, **teléfono de baquelita** (ItemDisplay `prop_telefono_baquelita`), **boletín** (prop con TextDisplay dinámico), **legajo** (libro que abre la pantalla de lectura con UNA línea gigante), **mate y termo** (interactuables), silla de la Madre (BlockDisplay que gira) | Beats 5 y 6 |
| **Capilla** | 11×24, alto 10 | Damero, 2×8 bancos, vitrales, **confesionario** en la pared oeste (3×2×3, rejilla de trapdoor de hierro), **pila bautismal**, altar, **lámpara del Santísimo** roja (luz 10), crucifijo grande. **Coro alto** en y=6 (11×6) con **8 atriles en semicírculo**, cada uno con su nombre en TextDisplay y una vela apagada. El del centro dice "T. ALBORNOZ" | Beats 7, 8, 13 y 14 |
| **Dormitorio** | 11×22 (1P) | Dos filas de 8 camas, 8 **bultos bajo las sábanas** que "respiran" (BlockDisplay de lana que escala), **manchas de luna** de 2×2 (bloque de luz nivel 9 + plano translúcido visible) cada 4 bloques por el pasillo central, la **silla de la celadora** al fondo, al norte | `colegio.gran_silencio` |
| **Baños + cuarto espejo** | 8×8 + 8×8 sellado | Piletas, duchas, **pared espejo** de paneles de vidrio sobre una copia invertida y sellada del baño (barreras, irrompible, la linterna no pone luz adentro). En la copia: el diario "al derecho" en TextDisplay, luz 4 | `colegio.espejo` |
| **Cuarto del Silencio** | 2×3, alto 2 | Banquito, marcas de conteo "TERESITA 18-6-84", rendija con luz 3. Sale a la sacristía | `colegio.cuarto_silencio` |
| **Sacristía** | 6×6 | Ornamentos, "vino de misa" (P2: *"Cosecha 1983. Cordura +5, dignidad −10."*), escalera a la cripta | — |
| **Cripta** | 11×16 | Bóveda, nichos (uno: **"Sor María de la Agonía 1951–"**, vacío), **tumba de la fundadora** (sarcófago con tapa BlockDisplay que se desliza), **muro nuevo de ladrillo** 7×4 con grieta, detrás la **Sala de las 7 sillas** (sillitas mirando la pared) | `colegio.hora_muerta` |

**Iluminación** (Sor Agonía no entra a nodos con luz de bloque ≥ 8):

| Zona | Luz base | Cambios |
|---|---|---|
| Exterior | Cielo 4. Gruta 12 | La gruta nunca se apaga |
| Hall | Araña 10, titilando | Se apaga en el Gran Silencio |
| Pasillo PB | 6 faroles de 12 | Revientan en cadena hacia vos (`colegio.pasillo`) |
| Aula | Ventanas 6 | — |
| Refectorio | 0 | Las velas se prenden solas en la Cena y ella las sopla |
| Capilla | Lámpara roja 10 | Se apaga en la Hora Muerta. Las 7 velas del coro valen 12 cada una |
| Dormitorio | Manchas de luna de 9 | Cada 20–30 s "se nubla" (bajan a 5 durante 6 s; antes avisa el viento) |
| Cripta | 0 | En la Hora Muerta las chicas prenden 4 islas de velas de 11 |

**Textos de pistas** (solo dos se leen; el resto es audio):
- **Legajo N° 112** (pantalla de lectura, una línea gigante): *"Nombre religioso: Sor María de la Agonía. Nombre secular: **CLARA INÉS BUSTOS**. Baja: 22/6/1984. 'No figura. No se busca.'"*
- **Diario de Teresita**: el libro está escrito al revés y se lee en el espejo. Tres líneas grandes: *"21/6. Las escucho cantar al revés. Lo hicieron sin mí. / Eran siete. / **EL LIBRO DICE OCHO.**"*
- **Boletín** (prop, texto dinámico): *"Alumno: [NOMBRE]. Conducta: INSUFICIENTE. Observaciones: grita mucho ([N] veces)."* N sale del contador real de gritos.
- **Reglamento** (cartel grande en el hall, se lee de un vistazo): *"1. Silencio. 2. En el colegio se camina. No se corre. 3. **Toda voz será escuchada.**"* La regla 3 avisa dentro del juego que el micrófono cuenta.

#### g. Entidades y pedidos de arte

**1. Sor Agonía** (`MonjaEntity`, existe; P0)

*Comportamiento:*
- **Hitbox:** pasa a 0,7×1,95. El modelo sigue midiendo 2,7 y la cabeza se agacha en los marcos.
- **Oído (`HearingGoal`):** con ruido mayor a 55 dentro de 40 bloques camina hacia la *marca de sonido* por la oscuridad (ver §3.4).
  - Fuera de los capítulos 6 y 8 solo cuentan los **gritos** (base calibrada + 12 dB), correr, portazos y romper cosas.
  - En el Gran Silencio cuenta **hablar** (base − 6 dB).
  - Con la tecla de susurro de SVC no te oye (`isWhispering`).
- **Luz:**
  - Si el haz de la linterna la toca (cono con producto punto mayor a 0,94, hasta 12 bloques, con línea de visión), **se quema**: humo, siseo y un retroceso brusco. Después **se hunde en el piso** y reaparece en otro nodo oscuro a 10 o más bloques, fuera de tu vista, entre 3 y 6 s más tarde. No se congela mirándote.
  - Las velas y lámparas con luz ≥ 8 le bloquean el paso: en el borde gira y busca otra ruta.
  - Si está a menos de 6 bloques de una vela, la **sopla** cada 10–14 s (se ve el aliento y queda el humo).
- **Pasillos:** si corrés dentro del edificio, te ponen la amonestación y se oye un susurro detrás tuyo: *"No se corre en los pasillos."* Ella reaparece 6–8 bloques detrás de vos (como mucho una vez cada 90 s).
- **Avisos al jugador:** la **campanita** ("tilín-tilín") 2 s antes de un teletransporte (en el Gran Silencio no avisa); el loop "tac... tac" de la regla a menos de 16 bloques; la linterna titila a menos de 10; el EMF marca 4 o 5.
- **Ataque, el reglazo:** 5 de daño, sacudón y destello rojo. Con 15 amonestaciones o más, te captura y vas al Cuarto del Silencio en lugar de recibir daño.
- **Persecución con elástico:** velocidad entre 0,30 y 0,42 según la distancia. Afloja a menos de 3 bloques. Nunca mata de un golpe.
- **Teletransporte "detrás tuyo":** como mucho uno cada 3 minutos fuera de los beats guionados.
- **Sin IA en los beats guionados:** prendo/apago, coro alto, Gran Silencio, espejo y Maitines siempre salen igual.

*Pedido de arte* (se mantiene `ent_monja.py`; se agrega lo siguiente):
- **Utilería:** campanita de bronce (3×4×3, mano izquierda) y manojo de 5 llaves en el cíngulo.
- **Plano `face_crack`:** una grieta vertical en la cara. Al abrirse muestra un **ojo humano marrón y húmedo**, una franja de piel tibia y una lágrima. Es la revelación de Clara.
- **Poses nuevas:** `conduct` (dirige el coro con el índice como batuta), `sit` (sentada, inmóvil, cabeza inclinada 30°), `ceiling` (boca abajo en el techo, miembros abiertos), `blow` (cabeza adelantada, mandíbula entreabierta), `wet` (gag: mira el hábito empapado, velo caído), `kneel_wall` (de rodillas con la frente contra la pared), `reveal` (brazos abiertos y la grieta visible), `burn` (se cubre la cara, humo).
- **Retrato de jumpscare:** existe; se le suma una variante "pegada al vidrio".

**2. Las alumnas del coro** (`AlumnaEntity`, nueva, ×7 instancias; P0)

*Comportamiento:*
- Sin IA, sin colisión, invulnerables. Se colocan en forma cinemática con los beats.
- Solo aparecen en 4 beats: lista (susurros, sin cuerpo), coro alto, Hora Muerta y Maitines/Laudes.
- Son semitransparentes. En las fotos de la cámara de espíritus tienen boca.
- Cuando ella caza cerca: se agachan, se tapan los oídos, susurran *"shh, viene"* y se desvanecen. Le enseñan al jugador a esconderse.
- **No giran la cabeza 180°**, salvo en el coro alto (es el único giro de cabeza del caso). En la cripta giran **el cuerpo**.

*Pedido de arte:*
- **Escala:** nena de 1,35 bloques (43 texels a 2x). Cabeza demasiado grande (14×15×13), brazos demasiado largos (los dedos a mitad del muslo), cuello de camisa blanco.
- **Ropa:** **guardapolvo blanco** acampanado en 4 paneles tableados, **moño azul marino** de 8×4 con dos colas, medias tres cuartos azul marino, guillerminas negras de charol.
- **Cara:** cuencas de 4×4 que pasan de un aro gris a negro, con 1 px de brillo celeste emisivo. **Sin boca**: piel lisa con una "costura" de 1 px. Mejillas rosadas de muñeca.
- **Variante `freed`:** hueso `jaw` con la boca en "O" de canto.
- **Peinados:**
  - **Paloma**: dos trenzas largas con cintas. Es la reconocible y la única que habla.
  - Otras tres: carré con flequillo, cola de caballo, corto con moño enorme.
  - Las 7 instancias se arman combinando esos peinados con el color del moño.
- **Paleta:** guardapolvo #f2f4f6 → #8691a6 (mugre en el ruedo #9b8f7a), azul marino #121a33 → #2b3a66, piel #e8dcd6 → #8a7676.
- **Render:** `entityTranslucent`, alfa de unos 220.
- **Poses:** `stand`, `sing`, `face_wall`, `turn_body`, `cover_ears`, `run`, `point`, `wave`.
- **Presupuesto:** 80–110 cubos.

**3. La Madre Remedios** (`MadreEntity`, aparición estática; P1. Su voz es P0)

*Comportamiento:* no camina, aparece y desaparece. Se presenta:
- al llegar a 5 amonestaciones: escribe *"Ajá."* y la sala se oscurece 8 s;
- cuando hay que señalar el camino;
- en el remate final, cuando la callan.

*Pedido de arte:*
- **Silueta:** 2,3 bloques. Una **columna negra rígida**: hombros cuadrados y el ruedo apoyado en el piso.
- **Hábito:** toca blanca almidonada que le enmarca la cara como un rectángulo, con un gran babero blanco.
- **Cara:** **anteojos redondos de cristales blancos opacos y emisivos** (nunca se le ven los ojos), labios finos en línea, piel cerosa entre amarillo y gris.
- **Utilería:** **libro de actas** de cuero sangre de toro y pluma.
- **Render:** translúcido (alfa de unos 210), tinte frío.
- **Poses:** `write`, `stare` y `point`.
- **Presupuesto:** unos 45 cubos.

**4. Clara liberada** (retextura del Ánima; P0). Mismo hábito pero limpio, toca blanca, rostro sereno de 33 años. Abre los ojos, marrones y cálidos. Brillo blanco cálido emisivo. Pose de elevarse con los brazos abiertos.

**5. El cura** (solo voz; sin modelo).

#### h. Guion de sustos

| # | id del beat | Disparador | Qué pasa | Sonido | Marcas |
|---|---|---|---|---|---|
| 1 | `colegio.timbre` | Cruzar el umbral del hall | El portazo cierra la entrada y el **timbre eléctrico** suena 4 s a fondo. Cae polvo. Cartel "20:00 · ESTUDIO". Se ve "PROHIBIDO CORRER" | `colegio.timbre`, `door.slam` | Chiste del creador: "Encima con reglamento." |
| 2 | `colegio.lista` | Entrar al aula | La **voz de la Madre toma lista**. Las nenas responden "presente" en susurros, y en "Albornoz" hay silencio y "Ausente". Después: *"¿Y usted? ¿Cómo se llama?"*. Se capturan `presente` y la calibración del micrófono. Si no contestás en 4 s: "Ausente." + amonestación | `madre.lista`, `alumna.presente` | — |
| 3 | `colegio.pizarron` | Termina la lista y el jugador mira el pizarrón | La tiza escribe **"NO MIRES ATRÁS"**. Mirás y no hay nada. Volvés al pizarrón: dice **"TE DIJE"** y ella está al fondo, en lo oscuro (aparece mientras no mirabas). La linterna la **quema**: sisea y se hunde. Las **16 sillas se arrastran a la vez** hasta quedar mirándote. Tiza: **"[NOMBRE] PASÁ AL FRENTE"** | `tiza.escribe`, `monja.burn`, `pupitres.giran` | `[CLIP]` |
| 4 | `colegio.leccion` | Pararse en los cuadros de tiza | **P1**: "¿Cuántas eran en el coro? a) 7 b) 8 c) 12 d) Ni idea, profe". Con la a): *"Contá bien."* y un reglazo. **P3**: "¿Quién castiga? a) La Madre b) Sor María c) Dios d) Tu vieja". Con la d): +3 amonestaciones y se ríe la clase fantasma. Cualquier respuesta hace que la tiza escriba **"ELLA"** y la puerta se cierre de golpe | `monja.reglazo`, `alumna.risitas` | `[RISA]` |
| 5 | `colegio.prendo_apago` | Mirar por la ventanilla de la cocina | Las velas del refectorio se prenden solas. En la cocina, la linterna la muestra al fondo, **quieta y humeando** (guionado, sin IA). Cada vez que apagás y prendés, está más cerca. A la tercera la tenés **cara a cara en la ventanilla**: sisea y la ventanilla se cierra de golpe. Después sopla las velas una por una | `monja.hiss`, `monja.soplido`, `monja.campanita` | `[CLIP]` |
| 6 | `colegio.pasillo` | Salir de la cocina con la llave | Los faroles **revientan desde el fondo hacia vos** y se oye "tac-tac-tac". El jugador corre y aparece el sello: **"AMONESTACIÓN: Por correr en el pasillo."** Atrás, el susurro: *"No se corre en los pasillos."* | `farol.revienta`, `monja.regla_tap`, `ui.amonestacion` | `[CLIP]` `[RISA]` |
| 7 | `colegio.megafonia` | Llegar al hall | Ding-dong: *"Se solicita al alumno [NOMBRE] en dirección."* | `colegio.pa_chime`, `madre.megafonia_nombre` | `[RISA]` |
| 8 | `colegio.direccion` | Entrar a la dirección | Boletín: *"grita mucho (N veces)"*. **Mate de la Madre:** sorbo 1, *"Está lavado."*; sorbo 2, *"Sigue lavado. Desde 1984."* (cordura +5). Foto del coro. El legajo está sobre el escritorio | `mate.sorbo_lavado` | `[RISA]` |
| 9 | `colegio.telefono` | Abrir el legajo | Aparece la línea gigante con el nombre de Clara. **Suena el teléfono de baquelita.** Al atender: 2 s cruzados de un stream (*"...chicos, llegué al hospital..."*), después **tu propio "presente"** por la línea, que enseguida se repite **al revés**. Luego, grabación de 1984: Clara llorando, *"...¿hay alguien? ...les dije que me llevaran a mí..."*. Por último, Clara en vivo: *"Ya sabe quién soy. No me tenga lástima. Lo que buscan está abajo."* La silla de la Madre ya está girada hacia vos | `telefono_baquelita.ring`, `telefono.crosstalk`, imitación, `clara.1984`, `clara.ya_sabe`, `silla.gira` | `[CLIP]` (uso de voz #1) |
| 10 | `colegio.confesionario` | Objetivo obligatorio. Arrodillarse adentro (agacharse 2 s) | El **cura** (voz real): *"Ave María Purísima... Contame, hijo."* Escucha entre 4 y 8 s de voz (sin SVC, espera 6 s) y responde al azar: *"Tres avemarías y no lo hagas más."* / *"Eso no es pecado, es mal gusto."* / *"¿Terminaste? Tengo el asado en el fuego."* / *"Decime una cosa, hijo... ¿ganamos otro Mundial?"*. Cierra: *"...Y corré."* La rejilla se abre y **su cara llena el hueco** (susto menor, no de pantalla completa). Abrís la puerta: adentro hay polvo de 40 años | `cura.voz`, `confesionario.rejilla`, `monja.scream` | `[RISA]` → susto |
| 11 | `colegio.coro_alto` | Entrar a la capilla en Completas | A contraluz de la lámpara roja, Sor Agonía de espaldas **dirige a 7 nenas que cantan al revés**. Si la iluminás, el coro **corta en seco y giran las 8 cabezas a la vez** (el ÚNICO giro de cabeza del caso). La lámpara titila y ya no hay nadie. Queda el atril 8 con "T. ALBORNOZ" | `coro.ave_reves`, corte a silencio | Imagen de miniatura |
| 12 | `colegio.canilla` | Fin del coro alto | Paloma aparece un segundo y **te pone una botella en la mano**: *"Tomá, se te cayó."* Es "Agua bendita" con la misma textura; la descripción dice *"Ideal para el mate."* (cambio garantizado) | `alumna.risitas` | Preparación |
| 13 | `colegio.gran_silencio` | Fin de Completas | Se cortan todas las luces con un golpe seco y la linterna titila hasta morir (guionado, 20 s). En el dormitorio los bultos respiran y uno se sienta: *"shhh"*. Ella está **sentada al fondo**. **Cada vez que se nubla, la silla aparece más cerca por el pasillo.** Pista: *"Si se acerca, tirale agua bendita."* Primer tiro: no chisporrotea. Ella queda **en pose `wet`** 1,5 s, se mira el hábito y te mira. Cartel: **"Era agua de la canilla."** Risitas. **Grita y carga.** Hay que huir a una mancha de luna. Después vuelve el agua bendita de verdad: *"Perdón."* | `luces.fuera`, `silla.arrastra`, `monja.mojada`, `monja.scream` | `[CLIP]` `[RISA]` → terror |
| 14 | `colegio.espejo` | Leer el diario frente al espejo | En el espejo, nenas cepillándose el pelo en piletas que de tu lado están vacías, y el diario se lee al derecho. **P1 (doppelgänger):** tu reflejo empieza a **atrasarse**, te sigue mirando cuando girás, inclina la cabeza y sonríe. Después ella **se levanta detrás del reflejo**. Te das vuelta y no hay nada. Volvés al espejo: está **pegada al vidrio**, el vidrio se raja (partículas y sonido) | `espejo.raja` | `[CLIP]` `[JUMPSCARE]` |
| 15 | `colegio.cuarto_silencio` | Captura guionada después del espejo | Despertás encerrado: *"Pensá en lo que hiciste."* Hay que aguantar **15 s de silencio** (con SVC: voz por debajo de la base − 10 dB; sin SVC: sin moverte). Paloma te cuenta chistes por la rendija: *"Toc, toc. ¿Quién es? La monja. ¿Qué monja? La que está atrás tuyo."* (y se siente un aliento en la nuca) / *"¿Querés saber un secreto? Sor Agonía ronca."* Si hablás, el contador vuelve a cero. Salir: felicitación −1 | `alumna.chistes` | `[RISA]` con tensión |
| 16 | `colegio.hora_muerta` | Sacar la regla de la tumba | El EMF al máximo, **tres campanadas** con sacudón de cámara y arriba se apaga la lámpara roja. El muro se derrumba: **7 nenas mirando la pared giran el cuerpo** y gritan **"¡CORRÉ!"**. Corren delante tuyo prendiendo **4 islas de velas** hasta la sacristía. Persecución con elástico y la linterna muerta | `colegio.campana_triple`, `muro.cae`, `alumna.corre` | `[CLIP]` |
| 17 | `colegio.maitines` | Entrar a la capilla | El final (ver m.) | `coro.ave_derecho_1..3`, `regla.rompe` | `[CLIP]` (`[JUMPSCARE]` solo si te alcanza la estocada) |
| 18 | `colegio.laudes` | Captura | El amanecer entra por el rosetón (tinte en el HUD). Las nenas, con boca, saludan. **La Madre aparece al fondo y escribe "Ajá."; las 7 se dan vuelta juntas y le gritan "¡SHHHHHH!"**, y la Madre se deshace. Clara se eleva | `alumna.shhh_final`, `coro.acorde_final` | `[RISA]` y catarsis |

#### i. Humor (resumen; todo en camino crítico)
- **Amonestaciones** con sello en pantalla. Motivos:
  - "Por correr en el pasillo."
  - "Por gritar en la casa del Señor." (aparece justo después de tu grito)
  - "Por daños al edificio. Se notificará a sus padres." (si rompés un bloque)
  - "Por no responder a la lista."
  - "Por faltarle el respeto a la institución." (+3)
  - "Por entrar a la capilla con la cabeza cubierta." (con casco)
- Boletín "grita mucho", mate lavado, "¿ganamos otro Mundial?", agua de la canilla, los chistes de Paloma, las chicas callando a la Madre.
- **Fuera:** combi escolar, Gauchito Gil, kiosco, Kevin, armonio secreto, campana a mano.

#### j. Mecánicas e ítems nuevos

| Ítem / mecánica | Detalle | Prio |
|---|---|---|
| `ConductTracker` (amonestaciones) | Attachment del jugador. Cada motivo tiene 20 s de enfriamiento. Umbrales: **5** = aparece la Madre y la sala queda 8 s a oscuras; **10** = citación (notificación en el teléfono y ella va un 15 % más rápido hasta el próximo capítulo); **15** = la próxima captura te manda al Cuarto del Silencio. **Felicitación −1**: respuesta correcta, prender una vela del coro, salir del Cuarto del Silencio. La libreta sigue activa en los casos 2 y 3 (con 1 o 2 motivos guionados) | P0 |
| Ruido y escucha | §3.4. Ícono de micrófono junto al ECG que se pone rojo con **"TE ESCUCHA"** | P0 |
| Lección oral | 4 cuadros de tiza (zonas). Se responde agachándose 1 s. 2 preguntas | P0 |
| Cuarto del Silencio | 15 s de silencio acumulado. Sale a la sacristía | P0 |
| Oración en voz alta | 3 frases. Cada una pide **6 s acumulados de voz** por encima de la base − 6 dB; el progreso baja 1 s por cada 2 s de silencio. Sin SVC: mantener el libro de rituales 8 s quieto. El texto de cada frase se muestra grande en pantalla | P0 |
| `agua_canilla` | Ítem trampa idéntico al agua bendita. Se cambia solo en `colegio.canilla` y se devuelve después del gag | P0 |
| `regla_quebracho` | Ancla. Se purifica sola cuando termina la frase 1 de la oración. "Rompé la regla" = usarla sobre ella cuando está arrodillada | P0 |
| `llave_capilla` | Llave del tablero de la cocina | P0 |
| Tiza que escribe | `WallWriter` con la fuente `chalk` | P0 |
| Reflejo doppelgänger | `DoppelgangerEntity` en modo MIRROR (§3.6) | P1 |
| Herramientas existentes | **Linterna**: la quema y muere en los capítulos 6 y 7. **Velas rituales**: islas propias. **Bengala**: la quema el doble y bloquea. **Crucifijo**: la empuja en cono. **Sal**: le corta el paso. **Agua bendita**: la empuja (anclada). **Cámara de espíritus**: la aturde 3 s y en la foto las nenas tienen boca. **EMF**: 5 cerca de la regla. **Spirit box** (rueda de preguntas): "¿Quién está ahí?" → "Clara... Clara..." / "¿Cuántas eran?" → "Ocho." / "¿Me vas a matar?" → "Shhh." / "¿Estás atrás mío?" → "Mirá." / "¿Te gusta el asado?" → "Vacío." **Frasco**: captura final | — |

#### k. Imitación de voz
Uso único: `colegio.telefono` (tu "presente"). Capturas fijadas: `presente` (más la calibración). En la oración final **no se reproduce tu voz**: rezás en vivo y las nenas cantan con vos. El momento emotivo queda limpio.

#### l. Sonidos nuevos

| Clave | Descripción | Fuente |
|---|---|---|
| `colegio.ambient` | Viento en los postigos, caldera lejana, coro lejano casi inaudible (reemplaza a `ambient.convento`) | Síntesis |
| `colegio.timbre` | Timbre eléctrico escolar, martilleo metálico de 4 s | Síntesis |
| `colegio.campana` / `campana_triple` | Campanada grave con cola de 8 s / las tres campanadas | FM + reverb |
| `colegio.pa_chime` | Ding-dong de megafonía de los 80 | Síntesis |
| `madre.lista` | Lista de 8 apellidos, "¿Y usted? ¿Cómo se llama?", "Ausente." | **Voz real** (mujer mayor) o ef_dora bajada |
| `madre.megafonia_nombre` | "Se solicita al alumno [NOMBRE] en dirección." | Pregenerada con `gen_name.py` o grabada |
| `madre.aja` / `madre.pluma` | "Ajá." / pluma raspando y sello | Real o TTS / síntesis |
| `monja.campanita` | "Tilín-tilín" de aviso | Síntesis |
| `monja.regla_tap` | "Tac... tac", loop 3D de proximidad | Síntesis |
| `monja.reglazo` | Regla de madera contra la palma | Síntesis |
| `monja.shh` | SHHH largo y envolvente | Ruido filtrado |
| `monja.burn` / `monja.hiss` | Chisporroteo de carne y siseo de gato grande | Síntesis |
| `monja.soplido` | Soplido que apaga velas | Ruido |
| `monja.ceiling` | Tela y huesos arrastrándose por el techo | Síntesis |
| `monja.dos_voces` | "¿Quién habló?", "A la pared.", "Castigo para todas." | ef_dora + em_santa en capas |
| `monja.mojada` | Quejido indignado con goteo | TTS + ruido |
| `monja.scream` | Grito del confesionario y del espejo | Capas + distorsión |
| `clara.llamada` / `clara.1984` / `clara.ya_sabe` / `clara.gracias` / `clara.dormitorio` / `clara.falta_voz` | Llamadas y despedida | **Voz real** (mujer joven) |
| `cura.voz` ×7 | "Ave María Purísima", "Contame, hijo", las 5 respuestas, "Y corré." | **Voz real** (hombre mayor) |
| `alumna.presente` / `risitas` / `shh_viene` / `corre` / `chistes` / `shhh_final` | Voces de nenas | Real (adultas con voz de nena) o ef_dora +4 st, banda limitada + reverb |
| `coro.ave_reves` | Coro lo-fi del Ave María (tradicional, dominio público) al revés, loop de 20 s | **Grabación real** invertida; respaldo: pad formántico tarareado |
| `coro.ave_derecho_1..3` | Las tres frases al derecho, in crescendo | Ídem |
| `coro.acorde_final` | Acorde mayor luminoso | Síntesis |
| `tiza.escribe` / `tiza.rompe` | Chirrido de tiza (con velocidad variable) / quiebre | Síntesis |
| `pupitres.giran` | 16 sillas arrastrándose a la vez | Capas |
| `farol.revienta` / `luces.fuera` | Pop de vidrio / golpe seco de llave general | Síntesis |
| `silla.arrastra` / `silla.gira` | Silla sobre tablones / silla de escritorio girando | Síntesis |
| `telefono_baquelita.ring` | Campanilla mecánica antigua | Síntesis |
| `telefono.crosstalk` | 2 s de stream de Tomi con estática | Voz real de Tomi + DSP |
| `mate.sorbo_lavado` | Sorbida de bombilla de un mate lavado | Síntesis/foley |
| `confesionario.rejilla` | Rejilla de madera deslizándose | Síntesis |
| `espejo.raja` | Vidrio rajándose despacio | Síntesis |
| `muro.cae` / `tumba.tapa` | Ladrillos derrumbándose / piedra sobre piedra | Síntesis |
| `regla.rompe` | Crack de madera dura con eco y coro | Síntesis |
| `ui.amonestacion` | Sello de goma y campanita | Síntesis |

#### m. Resolución: Maitines (`colegio.maitines`)
1. Entrás al coro alto con la regla. Llamada de Clara: *"Falta una voz."*
2. Hay 7 velas apagadas en 7 atriles. **Cada vela que prendés hace aparecer una alumna** (felicitación −1).
3. Te parás en el **atril 8 (T. ALBORNOZ)**. Aparece en grande la frase 1: *"Dios te salve, María, llena eres de gracia, el Señor es contigo."* **Rezás en voz alta.**
4. Al completar la frase 1: destello blanco y acorde, ella sale despedida, la regla **se purifica sola** y las nenas cantan al derecho.
5. **Oleada entre frases** (nunca durante una frase):
   - trepa por el techo por un riel fijo (pose `ceiling`, sin navegación real);
   - sopla 2 velas;
   - se lanza.

   Volvés a prender las velas o la frenás con la bengala o la linterna (que acá vuelve a andar).
6. Frase 2: *"Bendita tú eres entre todas las mujeres, y bendito es el fruto de tu vientre, Jesús."* Frase 3: *"Santa María, Madre de Dios, ruega por nosotros pecadores, ahora y en la hora de nuestra muerte. Amén."*
7. Después de la frase 3 se **arrodilla de cara a la pared** (`kneel_wall`, justicia poética). Objetivo: **"Rompé la regla."** Usás la regla sobre ella:
   - CRACK, `face_crack`, y se ve el ojo de Clara;
   - sale humo negro (**La Celadora**);
   - objetivo "Atrapala" y el frasco la absorbe con un solo clic.
8. Clara liberada: *"Gracias por venir. Yo llamé en 1984 y nadie vino. ¿Quién te pasó mi llamada? ...Tené cuidado con quien te llama con tu voz."* Después viene Laudes (beat 18).
9. Recompensa: **Regla de quebracho** (trofeo) y $1.200.

**En cooperativo:** uno reza y el otro la contiene con la linterna.

#### n. Cortado (no se vuelve a agregar)
Manual de 1767, Madre Benigna como personaje (la tumba queda sin nombre de personaje), llamadas alternativas B/C/D, caja fuerte y teclado, rayuela/ronda/"Arroz con leche", biblioteca, locutorio, lavadero, bodega, pasadizo, celdas, archivo, campanario jugable, enfermería, kiosco, combi, Gauchito, Kevin, armonio, campana a mano, amonestaciones 20 y 25, cassette (su contenido pasa al teléfono), lista de castigos/parte de enfermería/carta, llamada de Teresa en el epílogo (queda como P2), benteveo, nombres de las otras 6 nenas en pantalla, cabezas que giran fuera del coro alto, pathfinding que esquiva la luz con un NodeEvaluator propio, monja que trepa paredes con IA.

---

### 2.2 CASO 2: LA MUÑECA · "Casa Morales"

#### a. Ficha

| | |
|---|---|
| Clave / dimensión | `casa` / `deadline:caso_casa` |
| Lugar | **Pasaje Las Glicinas 1961, Villa Esperanza** (barrio ficticio del conurbano sur). Chalet de los años 50: ladrillo y revoque blanco, techo a dos aguas de tejas, rejas, patio largo con **parrilla**, pelopincho y limonero |
| Antagonista | **AZAMEL**, el demonio encerrado en **Ofelia** desde 1961, que salta de un cuerpo a otro |
| Ancla | **Ofelia** (`CURSED_DOLL`) |
| Huéspedes, un verbo cada uno | Choripán = **darle de comer** · Jorge = **sal** · Lucía = **sobrevivir a las muñecas y purificar a Ofelia** · la Nona = **coser la boca** |
| Regla visible | *"Donde se sienta Ofelia, ahí va el demonio."* (aviso **anticipado**) |
| Edición | 5:55 (7:10–13:05) |

#### b. Historia
**Lo que entiende el público:**
- Marta compró una muñeca de porcelana con la boca cosida, **Ofelia**, en la feria de San Telmo: *"re barata, dos lucas"*.
- Lucía (8) le cortó los hilos.
- Desde entonces vuelan cosas, el perro está raro y Ofelia "se sienta" al lado de quien va a ser poseído.
- La Nona sabe más de lo que dice.
- **Giro:** la Nona fue la nena poseída en 1961. Al final llama al demonio para sacárselo a su nieta y lo encerrás con ella.

**Verdad interna:**
- 1961. **Nélida "Pocha" Bertolotti**, de 8 años, poseída. El **Padre Anselmo** no logró expulsar al demonio: lo encerró en la muñeca Ofelia cosiéndole la boca con hilo bendito rojo y la enterró en una lata de galletitas.
- Décadas después alguien la desenterró. La muñeca pasó de mano en mano hasta un puesto de la feria. **Volvió a la casa**, que es lo que quería: volver con su primera huésped.
- La Nona la reconoció en silencio. Desde entonces teje bufandas rojas "por las dudas" y trazó un **círculo de sal alrededor de la parrilla**.
- Marta nunca llamó a DEAD LINE: esperaba al exorcista que iba a mandar el **Padre Ignacio**. La llamada con su voz la hizo El Eco (S2).

**Elenco:**

| Personaje | Rol | Voz |
|---|---|---|
| **Marta Morales** (42) | Mamá: ruleros, bata, crema de cara en un solo cachete. Guía cómica. **Nunca la poseen** | Real (mujer adulta) |
| **Jorge Morales** (46) | Papá y "rey del asado": *"Es la humedad, flaco."* Se va a buscar carbón. Huésped #2 | Real (hombre adulto) |
| **Lucía** (8) | Le cortó los hilos a la muñeca. Huésped #3 (`PoseidaEntity`) | ef_dora +3 st o una adulta con voz de nena |
| **Nona Pocha** (73) | Sorda a conveniencia, teje rojo, ofrece mate, **andador con una rueda que chilla**. Víctima de 1961. Huésped #4 y giro | **Voz real de una abuela** (ideal) |
| **Toti** (15) | Encerrado en el placard jugando rankeds. Gag | Real |
| **Choripán** (6) | Salchicha con suéter rojo tejido por la Nona y collar celeste con chapita. Huésped #1 | Síntesis + em_santa (demonio) |
| **Ofelia** | La muñeca, el ancla | Risitas, porcelana |

#### c. Llamada del caso (transición 1). **"Marta Morales"**
> *"Hola... ¿es la línea de los exorcistas? Perdón la hora. Es mi perro... Choripán... camina raro. No, no, el perro no. Mi hija. Bueno... los dos, no sé. Y la muñeca... la compré en la feria de San Telmo, re barata. Pasaje Las Glicinas 1961. Por favor, venga rápido... ...y el perro. El perro está raro."*

(El creador improvisa *"Y bueno... por algo estaba barata."*) Aviso legal: *"Si el ente le pide pasar, por favor no lo invite a pasar."*

#### d. Reglas del caso (cartel al ver a Ofelia mudarse por primera vez, `casa.reglas`)
> **OFELIA SE MUEVE CUANDO NO LA MIRÁS. DONDE SE SIENTA, AHÍ VA EL DEMONIO.**

#### e. Capítulos y objetivos

| Cap. | Objetivo en el HUD | Pista | Termina cuando | Checkpoint |
|---|---|---|---|---|
| 1 Llegada | "Hablá con la familia." | "La señora está en la puerta, en ruleros." | Termina la charla con Marta | `vereda` |
| 2 La casa | "Reuní 3 evidencias." (spirit box, foto, EMF 5, huellas UV, el chat) | "Probá la spirit box en el cuarto de Lucía." | 3 evidencias (el chat y Ofelia cuentan como dos) | `living` |
| 3 Choripán | "Algo le pasa a Choripán." | "Llamalo vos. A vos capaz te hace caso." | Termina `casa.buen_chico` | `pasillo_pb` |
| 4 La cucha | "Calmá a Choripán sin lastimarlo." | "¿Qué es lo único que un perro no puede rechazar?" | El choripán bendito se come | `patio` |
| 5 La parrilla | "Liberá a Jorge." | "LE FALTA SAL." | Tercer golpe de sal | `parrilla` |
| 6 Lucía | "Purificá a Ofelia. No pierdas de vista a las muñecas." | "No podés mirar a las dos cosas a la vez. Usá sal. Usá el flash." | Termina `casa.chancleta` | `pasillo_1p` |
| 7 La Nona | "Bajá al sótano y cosele la boca a Ofelia (0/3)." | "Hilo y aguja: la lata de la Nona." | Sello | `sotano` |
| 8 Desayuno | "Desayuná." / "Volvé a casa." | — | Volvés | `cocina` |

#### f. El lugar
Lote de 36×40 con la vereda hacia −Z. La casa ocupa X −10..10 y Z 0..14 (21×15), con PB en y=0, 1P en y=5 y sótano en y=−5. El patio queda en Z 15..34. **No hay garaje ni altillo.**

```
 VEREDA: farol que titila, reja, cartel "CUIDADO CON EL PERRO" (P2: + marcador "...y con la nona")
 +--------+-----------+-------+
 | NONA   |  LIVING   | HALL  |<- porch (mecedora de afuera: no)
 | 6x6    |  9x7 TV   | 3x4   |
 | altar  +-----+-----+--+----+
 | mecedora COMEDOR| ESCALERA|
 +--------+ 7x6  |  + BAÑO  |
 |LAVADERO+------+--+-------+
 |4x4 tablero COCINA 7x6     |-> ventana al patio
 +--------+-----------------+
 1P: PASILLO 2x12 | LUCIA 6x6 (estante de muñecas, tablet) | TOTI 5x6 (placard 2x1x3) | MATRIMONIAL 7x6
 SOTANO 15x9 (caldera, muebles con sabanas, PARED RAJADA) -> CUARTO DEL 61 9x9x4 (arena)
 PATIO: PARRILLA 6x4 con CIRCULO DE SAL r=3 (piso de ladrillo) | mesa larga | PELOPINCHO 6x4 | CUCHA 3x3 | limonero | soga con sabanas
```

| Cuarto | Kit / props | Pistas y beats |
|---|---|---|
| **Living** | Sillón floreado, carpetitas, **TV de tubo** (`casa_tele_vieja`: novela y estática, con loop de sonido), **mecedora de la Nona** (BlockDisplay que se mece), pared de fotos familiares (pintura 2026: Choripán siempre mira a cámara) | Llegada |
| **Comedor** | Mesa larga, **8 sillas** (bloques de kit: el `UnseenSwap` las cambia por una torre de BlockDisplay) y aparador con platos (ItemDisplay) | Torre de sillas |
| **Cocina** | Azulejos verdes 70s, heladera (contenedor: **chorizo**), panera (**pan**), **mate y termo** (ItemDisplay), alacenas (trapdoors) y ventana al patio | Poltergeist |
| **Cuarto de la Nona** | Cama tejida, **altar de estampitas con velas** (luz 12, la única luz siempre segura: recupera cordura y nadie entra hasta el cap. 6), canasta de lana roja, **lata "Galletitas"** (te la da la Nona), andador | Beat de calma |
| **Lavadero** | **Tablero** (palanca + cartel) y escalera al sótano | Apagón |
| **Pasillo 1P** | Alfombra larga, 4 puertas en fila, una luz cada 4 bloques (grupo `pasillo_1p`) | Cascada de puertas (P1) |
| **Cuarto de Lucía** | Rosa, cama con dosel, **estante con 10 muñecas** (ItemDisplay en 3 variantes que giran), **tablet** (prop con loop del VOD), cuaderno con "MI AMIGO SE LLAMA LEMAZA" en grande (P1) | Spirit box, Ofelia, VOD |
| **Cuarto de Toti** | Silla gamer, PC RGB y **placard** (2×1×3; adentro Toti con los auriculares RGB prendidos) | Gag del ropero |
| **Patio** | **Parrilla** con fuego (fogata; azul cuando Jorge está poseído), pinza, **6 cuchillos en el rack** (ItemDisplay), **círculo de sal r=3** sobre el piso de ladrillo, **pelopincho** con agua verde y sin tapa, **cucha "CHORIPÁN"**, limonero, sábanas en la soga (BlockDisplay que se mecen) | Cucha, parrilla, Jorge |
| **Sótano** | Caldera, muebles tapados con sábanas, frascos, foco colgando, **pared rajada** (la rompe la Nona) | — |
| **Cuarto del 61** | 9×9×4. Cama de hierro con correas, **círculo de sal viejo**, velas derretidas, rayones infantiles "LEMAZA LEMAZA" (TextDisplay), la estola de Anselmo colgada de un clavo | Jefe final |

**Iluminación:**
- La casa tiene luz eléctrica (fixtures del kit con LEVEL).
- **Dos apagones guionados:** el de la cocina, que se arregla en el tablero (opcional; el gag de Edesur lo improvisa el creador), y el de antes de Lucía, que vuelve por guion.
- Fuentes propias de la historia: la TV (6), la parrilla (8, azul en el cap. 5), el farol de la vereda y el altar de la Nona (12).
- **Cumbia de un vecino**, lejana y en loop durante los caps. 1 a 3. **Cuando se corta la cumbia, se viene algo.** El público lo aprende en 3 minutos. En el giro, la cumbia pasa a una cajita de música de 1961 en medio del tema. Vuelve normal en el desayuno.

**El agua del bioma** pasa de `water_color #4a0b0e` (roja) a un verde turbio (#3b4a2a), para que el pelopincho se vea verde.

#### g. Entidades y pedidos de arte

**1. Choripán, perro** (`ChoripanEntity`, forma DOG; modelo `ent_choripan.py` en proceso; P0)
- **Comportamiento:**
  - sigue a la familia o al jugador, mueve la cola, olfatea, se tira panza arriba (beat de calma);
  - **avisa las alucinaciones:** `SanityManager` demora cada alucinación 40 ticks y Choripán le gruñe a ese punto. El público aprende a creerle al perro antes de que se dé vuelta;
  - le ladra a lo espectral.
- **Arte** (ya definido en el modelo): salchicha largo y bajo, orejas enormes, ojos grandes con brillo emisivo, **suéter rojo de la Nona con una "C" blanca**, collar celeste con **chapita dorada que dice "CHORIPÁN"**.
- **Poses:** sentado, pidiendo, panza arriba, cabeza ladeada y la nueva `bipedal_180` (parado en dos patas con la cabeza girada 180°).

**2. Choripán, versión completa** (forma BEAST; modelo `ent_choripan_demonio.py` en proceso; P0)
- **Comportamiento:**
  - **Hitbox solo en la cabeza** (0,8×0,8), así pasa por puertas.
  - El cuerpo es una **cadena de segmentos que solo se dibuja** siguiendo el historial de posiciones de la cabeza (§3.7).
  - En la **salida de la cucha** los segmentos se desenrollan desde la puerta de la cucha, y **la cola sigue meneándose adentro** mientras la cabeza ya te persigue en el patio.
  - Velocidad 0,36.
  - **"Sigue siendo un perro":** cualquier ítem tirado a menos de 8 bloques lo distrae 3 s. Una vez, guionado, lo **trae, te lo deja en los pies y mueve la cola** con los ojos de leche: 3 s de silencio y después se lanza.
  - **La sal lo frena:** gime contra la línea como un perro frente a una puerta cerrada.
  - Si tenés un chorizo en la mano, **pide** (un monstruo de seis brazos sentado pidiendo).
  - **Ataque:** se te tira encima y la boca en flor llena la cámara (4 de daño y −10 de cordura) hasta que levantás el crucifijo.
  - El agua bendita y el crucifijo lo aturden. **No va al frasco.**
- **Arte:** el modelo existente.
  - **Cuerpo:** cadena con la cabeza sobre un cuello estirado, el pecho con restos del suéter, 5 eslabones de pelo y la cadera, unidos por piel rosa grisácea estirada con costillas.
  - **Patas:** 3 pares de **brazos humanos** largos.
  - **Cara:** ojos enormes **blanco leche con pupila roja** (emisivos); el hocico se abre **en 4 colgajos** con dientes de aguja; lengua negra.
  - **La cola sigue meneándose en todas las poses.** La chapita "CHORIPÁN" en el collar tiene que leerse.
  - **Agregar:** exportar los eslabones como partes que se dibujan por separado (para la cadena), y las poses `unspool`, `run`, `fetch_drop`, `beg`, `lunge`, `catch` (mandíbulas abiertas hacia arriba), `vomit`, `retract`.

**3. Ofelia** (`MunecaEntity`, existe; P0)
- **Comportamiento:** ángel llorón (se mueve solo cuando no la mirás; ya está en el código).
- **Ubicaciones guionadas como aviso anticipado:** se cambian solo con `UnseenSwap`, con un acento de sonido al descubrirla:
  1. en la cucha;
  2. en la silla de Jorge junto a la parrilla;
  3. en la almohada de Lucía;
  4. en la falda de la Nona.
- **Arte:** se mantiene el ojo roto. La boca lleva **hilo rojo cortado** con dos puntas que cuelgan y se mecen. Variante `sewn`, con la boca cosida con hilo rojo nuevo (al final).
- **Retrato de jumpscare:** "último giro hasta la cara".

**4. Lucía** (`PoseidaEntity`, existe; P0)
- **Normal:** variante de textura con camisón y **suéter rojo de la Nona** (quemado en el pecho cuando la poseen) y trenzas. Se esconde debajo de la cama.
- **Poseída:** el comportamiento existente (camina como araña por paredes y techo, levita). La transición se hace con `ActorSwap` entre la NPC normal y `PoseidaEntity`.
- Línea al liberarse (después de la chancleta): *"Ofelia tenía miedo... el señor feo quiere ir con la Nona."*

**5. Rig humano base** (`ent_humano.py`; P0)
- 2x de densidad, unos 60 cubos.
- Cara frontal de 14×14 o más con hueso `jaw`, manos con dedos, cuello separado.
- Proporciones paramétricas (alto, panza, joroba).
- Cada variante suma hasta 40 cubos de accesorios y su propia textura.
- Huesos compartidos: `neck`, `head`, `jaw`, `*_arm`, `*_hand`, `*_leg`.

| Variante | Arte | Poses |
|---|---|---|
| **Marta** (1,75) | Bata rosa peluda, **5 ruleros rosas**, crema en un solo cachete, celular en la mano, pantuflas, cejas expresivas | `scared`, `point`, `show_phone` |
| **Jorge** (1,9) | **Panza** saliente, camisa a rayas celeste y blanca (genérica, sin escudo), **delantal negro "REY DEL ASADO"** con una vaca de dibujito, bigote tupido, entradas, ojotas, pinza. **Poseído:** piel gris verdosa, esclerótica negra con pupila blanca emisiva, **sonrisa hasta las orejas** (mandíbula y labios pintados) y vapor en el cuello | `grill_flip`, `knife_conduct` (brazos arriba con los cuchillos orbitando), `limp_fall` |
| **Nona Pocha** (1,5, encorvada) | Rodete gris con redecilla, **anteojos redondos gruesos que brillan blancos** (emisivos), cara empolvada, lunar, collar de perlas, cárdigan bordó sobre vestido floreado, medias gruesas, pantuflas de fieltro, lana roja y agujas. **Accesorios:** **andador** y **mecedora** (roble claro, almohadón tejido), adosada al modelo para flotar. **Poseída:** anteojos rajados en telaraña; detrás, un ojo azul vidrioso y un agujero negro que llora negro (rima con Ofelia); mandíbula dislocada hasta el pecho con **la dentadura flotando adelante** (hueso aparte); el rodete deshecho en mechones blancos que flotan como bajo el agua | `knit_sit`, `stand_no_walker`, `throw_chancleta`, `float_rock`, `yarn_cast`, `scream_dentures`, `sew_calm` |
| **Toti** (1,8, P1) | Flaco, buzo con capucha, **auriculares RGB normales (sin orejitas)** emisivos, granitos, flequillo sobre los ojos, joystick | `crouch_closet`, `slam` |

**6. Tela de lana** (P1): segmentos de BlockDisplay de `red_wool` escalados a (0,05; 0,05; L) entre dos puntos de anclaje (§3.6).

**7. La voluta del demonio** (`DemonWisp`): una entidad invisible que recorre una curva soltando partículas (humo negro y brasas rojas) con un silbido. Sin modelo.

#### h. Guion de sustos

| # | id | Disparador | Qué pasa | Sonido | Marcas |
|---|---|---|---|---|---|
| 1 | `casa.llegada` | Teletransporte | Vereda, cumbia lejana, farol que titila. Marta en ruleros: *"Ay, gracias a Dios. ¿Lo mandó el Padre Ignacio? Pase, pase... y límpiese los pies."* Sello: **"AMONESTACIÓN: Por entrar a casa ajena sin limpiarse los pies."** Jorge en el sillón: *"Es la humedad, flaco."* Un plato le pasa rozando la cabeza: *"...Mucha humedad."* La Nona, con la novela a todo volumen: *"¿Querés un mate, nene?"* Choripán te saluda moviendo la cola. Jorge: *"Bueno, yo me voy a buscar carbón para el asado. Ya vuelvo."* Por la ventana del fondo se ve **a Ofelia sentada en la cucha** | `casa.cumbia_far`, `plate.whoosh`, `choripan.bark_cute` | `[RISA]` |
| 2 | `casa.ya_llego` | Marta te muestra el chat familiar en su celular (pantalla de chat) | El historial termina con Lucía (29/09, 03:07): *"ya le saqué los hilos"*, sin respuesta. Con la pantalla abierta y Marta a menos de 6 bloques (o a los 20 s) entra un mensaje en vivo de un **número desconocido con el logo de DEAD LINE**: *"ya llegó?"*. Marta, pálida: *"...Lucía no tiene celular."* **Se corta la cumbia.** Vos: "Pero si me llamaste vos." Marta: *"¿Yo? Nos cortaron el teléfono en marzo."* | `phone.notify`, `casa.cumbia_cut` | `[CLIP]` (semilla S2) |
| 3 | `casa.cuarto_lucia` | Entrar al cuarto de Lucía | Ofelia sentada en la cama. **Cada vez que dejás de mirarla está más cerca**; el último giro queda cara a cara. Lucía, debajo de la cama: *"Ofelia dice que tu perro... digo, nuestro perro... tiene hambre."* La **tablet** pasa el VOD de Tomi (*"si no vuelvo llamen a DEAD LINE, jajaja"*). Rueda de la spirit box: *"¿Cómo te llamás?"* → **AZAMEL**; *"¿Qué querés?"* → **AL PERRO**. Mirás para otro lado y **Ofelia no está**. Por la ventana: otra vez en la cucha, mirando la casa. Cartel con la regla | `ofelia.creak`, `doll.turn` | `[CLIP]` |
| 4 | `casa.cocina` | Primera evidencia en la cocina | El **mate se desliza** 2 bloques y el termo se inclina y lo ceba. Risa... y **el termo sale volando** por la cocina (`¡EL TERMO NO!`). Las alacenas golpean. En el comedor, **las 8 sillas apiladas en torre** hasta el techo (cambiadas mientras no mirabas), con la de arriba balanceándose. Marta: *"¡Esas sillas eran de mi suegra!"* La Nona, desde su cuarto: *"¡TODAVÍA SON MÍAS!"* Corte de luz en el tablero | `mate.slide`, `termo.fly`, `alacena.golpe`, `chair.stack`, `casa.breaker_trip` | `[CLIP]` `[RISA]` |
| 5 | `casa.calma` | Volver la luz | **Beat de calma (20 s):** cuarto de la Nona, velas del altar, mate (gorgoteo del mate vacío), Choripán dormido a sus pies, rascada de panza. Pista falsa: *"A vos te estaba esperando, nene."* Los anteojos brillan blancos y Choripán le gruñe una vez. Te da la **lata "Galletitas"**: *"Tomá, guardame esto."* Al abrirla: *"Hilos, agujas y botones. Obvio. Nunca son galletitas."* Adentro está la foto *"Nélida y Ofelia, 1960"*. Marta: *"Llamalo vos, decile 'Choripán', capaz a vos te hace caso."* Se captura `chori_call` | `mate.sip_empty`, `andador.squeak` | `[RISA]` (y pista sembrada) |
| 6 | `casa.buen_chico` | Las 3:33 | Las luces titilan. Choripán, sentado en el pasillo, te mira fijo. **Desde arriba, a oscuras, se oye TU voz: "¡Choripán, vení!"** Choripán se para en dos patas, **gira la cabeza 180°** y con voz grave dice: ***"¿Quién es un buen chico?"*** ... ***"YO NO."*** Sale corriendo al patio y se mete en la cucha | imitación de voz #1, `choripan.buen_chico` | `[CLIP]` |
| 7 | `casa.cucha` | Acercarse a la cucha | Gruñido. Ofelia arriba del techo de la cucha. Sale... y **no termina nunca de salir**: los eslabones se desenrollan y la **cola sigue meneándose adentro**. La cabeza **se abre en flor**. Persecución por el patio y la casa | `choripan.crack` ×6, `choripan.unspool`, `choripan.demon_roar` | `[CLIP]` `[JUMPSCARE]` (retrato de la boca en flor) |
| 8 | `casa.ropero` | Entrar al cuarto de Toti durante la persecución | Te metés al placard y **Toti ya está ahí adentro**, a oscuras, con los auriculares RGB: *"¡OCUPADO! ¡ESTOY EN RANKED!"* El hocico en flor empuja por la rendija y Toti cierra de un portazo sin mirar: *"¡Callate, Chori!"* | `toti.ocupado`, `door.slam` | `[CLIP]` `[RISA]` (P1; sin Toti, el escondite se hace igual sin el gag) |
| 9 | `casa.trae` | Bajar al living | Marta, desde algún lado: *"¡TIRALE ALGO!"* Tirás lo que tengas. El monstruo **lo trae, te lo deja en los pies y mueve la cola** con los ojos de leche. 3 s de silencio. Se lanza | `choripan.fetch_drop` | `[RISA]` → susto |
| 10 | `casa.parrilla` | Marta: *"¡Lo único que lo calma es un choripán! ¡Tomá!"* y te tira chorizo y pan por la ventana | Cocinás en la parrilla **dentro del círculo de sal** (5 s con anillo de progreso y chisporroteo) mientras él da vueltas, gime contra la sal y **pide sentado sobre los seis brazos**. Pan + chorizo asado = choripán; agua bendita = **choripán bendito**. Lo tirás: **lo atrapa en el aire** (pose `catch` con golpe de FOV), mastica y se congela. **Vomita una columna negra** (la voluta sale) y el cuerpo **se enrolla como un metro** con un "boing". Un salchicha temblando estornuda y mueve la cola | `grill.sizzle`, `choripan.chomp`, `choripan.vomit`, `choripan.metro_retract`, `choripan.sneeze` | `[CLIP]` ×2 `[RISA]` |
| 11 | `casa.jorge` | La voluta cruza la medianera | **Ofelia ya estaba sentada en la silla de Jorge** junto a la parrilla. Jorge entra por el portón con la bolsa de carbón: *"Llegué. No había carbón en lo de Rubén, tuve que ir hasta la—"* La voluta se le mete en la boca. Fuego azul. Da vuelta chorizos con las manos: *"¿Jugoso o a punto, pibe?"* ... *"Es la humedad... ES LA HUMEDAD."* Los **6 cuchillos suben, orbitan y vuelan** de a uno. *"LE FALTA SAL."* **3 golpes de sal** (subtítulo: *"Ahora sí tiene sal."*) y cae como una bolsa **adentro del pelopincho**. Marta: *"¡Te dije que no comas tanto chorizo!"* | `fire.blue_whoosh`, `jorge.*`, `knife.*`, `salt.hit_scream`, `pool.splash` | `[CLIP]` `[RISA]` |
| 12 | `casa.cascada` (P1) | La voluta sube | Las puertas del pasillo de arriba **se cierran en cadena** hacia vos y los focos revientan uno por uno | `door.slam_cascade`, `bulb.pop` | `[JUMPSCARE]` |
| 13 | `casa.lucia` | Entrar al pasillo de arriba | Ofelia en la almohada de Lucía. Lucía **en el techo**, caminando como araña: *"Él te llamó. Él tiene muchas voces."* (semilla). Se activan las muñecas del estante y Ofelia: **no podés mirarlas a las dos**. Los muebles levitan (6 a 10 BlockDisplay). **Detrás tuyo, en la oscuridad, tu NOMBRE con tu VOZ.** Objetivo: purificar a Ofelia (línea de sal atrás, flash a Ofelia para congelarla 6 s, agua bendita) | `poseida.*`, `doll.giggle_chorus`, imitación de voz #2 | Terror puro |
| 14 | `casa.chancleta` | Ofelia purificada **o** 60 s de pelea | La Nona aparece **sin andador**. La chancleta cruza volando: ***"¡SALÍ DE MI NIETA, ATORRANTE!"*** Lucía cae aturdida. La voluta flota, dudando. La Nona: ***"¡ACÁ! ¡VENÍ CON LA VIEJA, COMO ANTES! ¡DEJALA A LA NENA!"*** La voluta le entra. La cumbia de afuera se vuelve **cajita de música**. De un soplido apaga las velas del altar. Camina al lavadero fuera de cuadro. **Golpe**: la pared del sótano se cae (solo audio) | `nona.chancleta`, `chancleta.hit`, `nona.aca`, `candles.out`, `wall.break`, `casa.cumbia_musicbox` | `[CLIP]` `[RISA]` → giro |
| 15 | `casa.nona` | Entrar al cuarto del 61 | La Nona **flota sentada en la mecedora**, que se mece en el aire, con Ofelia en la falda. **La lana roja sale disparada y cruza el cuarto** (tela). Platos que vuelan desde arriba. Los rayones en latín se iluminan | `rocking.creak_slow`, `yarn.twang`, `plate.storm` | `[CLIP]` (imagen final del caso) |
| 16 | `casa.puntadas` | Ver m. | Las 3 puntadas, Choripán muerde la lana y el sello | `stitch.pull`, `azamel.suck` | Clímax y emoción |
| 17 | `casa.desayuno` | Sello | Mañana armada: luces de la cocina, fundido desde blanco, pájaros, pava, medialunas. Jorge en toalla: *"¿Te quedás al asado?"* Toti sale del placard: *"¿Qué me perdí?"* La Nona: *"¿Quién quiere asado?"* Marta: *"Llevate al perro un par de días, nos da miedo."* Choripán con la **bufanda roja** de la Nona. Vuelve la cumbia | `morning.birds`, `kettle.whistle` | `[RISA]` y alivio |

#### i. Humor
"Límpiese los pies" (sello), "Es la humedad" (después vuelve como terror), "¡TODAVÍA SON MÍAS!", el termo, la lata de galletitas, "¿Quién es un buen chico? YO NO.", "¡OCUPADO! ESTOY EN RANKED", "sigue siendo un perro", el choripán bendito, "¿Jugoso o a punto?", "Ahora sí tiene sal", el pelopincho, la chancleta, Toti al final. Respuestas de la spirit box: *"¿Pagás el alquiler?"* → "NUNCA"; *"¿Sos de Boca o de River?"* → estática... "SOY DE TEMPERLEY" (desactivable si el canal evita el fútbol).

#### j. Mecánicas e ítems nuevos

| Ítem / mecánica | Detalle | Prio |
|---|---|---|
| Cadena del choripán | **Recetas de datos:** `campfire_cooking` chorizo_crudo → chorizo_asado (con el tiempo bajado a 5 s solo en la parrilla del sitio, usando un `CookingSpot` propio con anillo de progreso); `shapeless` pan + chorizo_asado → choripán; `shapeless` choripán + agua bendita → `choripan_bendito`. Es arrojable (copia de `HolyWaterEntity`). Marta te da el chorizo y el pan, sin tener que ir a buscarlos | P0 |
| Círculo de sal de la Nona | `SaltLineBlock` ya colocado, de radio 3, alrededor de la parrilla | P0 |
| Distraer con objetos | Un `ItemEntity` tirado a menos de 8 bloques atrae al monstruo 3 s | P0 |
| Verbo sal (Jorge) | Contador de 3 golpes de sal tirada. Los cuchillos se caen al cruzar una línea de sal | P0 |
| Dilema de las muñecas | Ofelia (ángel llorón) + 10 muñecas de estante que giran + Lucía. Se purifica a Ofelia con agua bendita (`onAnchorPurified`) | P0 |
| Chancleta | La tira la Nona en un beat guionado (proyectil visual + aturdimiento). Trofeo `chancleta_nona` (P2: bumerán que aturde 2 s, una vez por caso) | P0 / P2 |
| Hilo bendito y aguja | En la lata "Galletitas" | P0 |
| Minijuego de puntadas | Hay que mantener la mira en la boca de Ofelia 2 s, con un anillo que se achica (el servidor chequea el ángulo de la mirada). Si fallás, la puntada se suelta, sacudón y −10 de cordura | P0 |
| Nombre | Pantalla con 3 opciones: **LEMAZA / AZAMEL / OFELIA**. Si te equivocás, se ríe con la voz de Lucía y se deshace una puntada. Pistas: spirit box y cuaderno de Lucía | P1 |
| Tela de lana | Segmentos de BlockDisplay. Tocar uno te deja enganchado 2 s y −8 de cordura. Se corta con la daga de plata o se quema con una bengala | P1 |
| Chat familiar | Pantalla de chat compartida (§3.10) | P0 |
| Tablero | Un corte guionado y una reposición en la palanca | P0 |
| Herramientas existentes | **EMF**: 5 en la cucha antes de la transformación. **Spirit box**: rueda de preguntas. **Cámara de espíritus**: el flash aturde a huéspedes y muñecas. **UV**: huellas de muñeca en la escalera, y "AZAMEL" en el espejo del baño (P1, TextDisplay solo con UV). **Sal, agua bendita, crucifijo, daga, bengala**: como arriba. **Frasco**: Ofelia sellada | — |

#### k. Imitación de voz (2 usos)
1. `casa.buen_chico`: tu "¡Choripán, vení!" desde el piso de arriba, a oscuras.
2. `casa.lucia`: tu **nombre** con tu voz detrás tuyo.

Capturas fijadas: `chori_call`.

#### l. Sonidos nuevos

| Clave | Descripción |
|---|---|
| `casa.cumbia_far` / `cumbia_cut` / `cumbia_musicbox` | Cumbia original de 40 s (güiro, bajo saltarín, acordeón sintetizado), con pasa-banda como si viniera de 3 casas más allá / corte con aguja / se desliza a una cajita de música de 1961. Respaldo: el creador pone su propio tema libre de derechos vía resource pack |
| `casa.breaker_trip` / `breaker_reset` | Clonk con chispa / zumbido de luces volviendo |
| `casa.tv_novela` / `tv_static` | Murmullo de novela a todo volumen / estática |
| `choripan.bark_cute` / `whine` / `growl_low` / `sneeze` | Ladridos chicos y simpáticos, gemido, gruñido, estornudo |
| `choripan.buen_chico` | em_santa −5 st con capa de octava: "¿Quién es un buen chico?" ... "YO NO." |
| `choripan.crack` (×6) | Hueso húmedo que cruje (apio partido + golpe grave) |
| `choripan.unspool` | Chirrido largo de goma estirada sobre carne, sin cortes mientras salen los eslabones |
| `choripan.demon_roar` | Ladrido chico + rugido grave + grito invertido |
| `choripan.fetch_drop` | Objeto que cae, jadeo, golpes de la cola |
| `choripan.chomp` / `vomit` | Mordida de dibujito / gorgoteo espeso con salpicadura |
| `choripan.metro_retract` | **Cinta métrica enrollándose** (zip) + "boing". El único sonido de dibujito explícito del caso |
| `grill.sizzle` / `fire.blue_whoosh` | Grasa chisporroteando / encendido azul |
| `jorge.lines` | "Es la humedad, flaco", "...Mucha humedad", "Me voy a buscar carbón", "Llegué. No había carbón en lo de Rubén...", "¿Jugoso o a punto, pibe?", "ES LA HUMEDAD", "LE FALTA SAL". Poseído = voz real + em_santa −5 st en capa |
| `knife.lift` / `whoosh` / `impact` | Shing metálico, corte de aire, golpe seco en madera |
| `salt.hit_scream` / `pool.splash` | Siseo con grito / chapuzón grande |
| `plate.whoosh` / `shatter` / `storm` | Platos (4 variantes) y tormenta |
| `mate.slide` / `mate.sip_empty` / `termo.fly` | Cerámica deslizándose / **gorgoteo de mate vacío** / termo silbando por el aire |
| `alacena.golpe` / `chair.stack` | Golpes de alacena / traqueteo de sillas "que pasó mientras no mirabas" |
| `door.slam_cascade` / `bulb.pop` | 5 portazos crecientes / foco que revienta |
| `ofelia.creak` / `doll.turn` / `doll.giggle_chorus` | Porcelana que cruje, clics, 10 risitas desfasadas |
| `marta.lines` | Saludo, "límpiese los pies", "Lucía no tiene celular", "Nos cortaron el teléfono en marzo", "¡TIRALE ALGO!", "¡Tomá!", "¡Esas sillas eran de mi suegra!", "¡Te dije que no comas tanto chorizo!", "Llevate al perro" |
| `nona.lines` | "¿Querés un mate, nene?", "¡TODAVÍA SON MÍAS!", "A vos te estaba esperando", "Tomá, guardame esto", **"¡SALÍ DE MI NIETA, ATORRANTE!"**, **"¡ACÁ! ¡VENÍ CON LA VIEJA...!"** (sin efecto de vejez: fuerte y clara), "Nene, vení" (poseída), "Dámelo, nene. Esta vez lo cierro yo.", "Sesenta y cinco años esperando para esto. ¿Me alcanzás el mate?", "¿Quién quiere asado?" |
| `andador.squeak` | Rueda que chilla (gag cada vez que se mueve) |
| `chancleta.whip` / `hit` | Látigo de goma / cachetazo |
| `lucia.lines` | "Ofelia dice que tu perro...", "Él te llamó. Él tiene muchas voces." (doble voz), "El señor feo quiere ir con la Nona." |
| `toti.lines` | "¡OCUPADO! ¡ESTOY EN RANKED!", "¡Callate, Chori!", "¿Qué me perdí?" |
| `rocking.creak_slow` / `yarn.twang` / `yarn.snap` / `stitch.pull` | Mecedora lenta / cuerda tensa / cuerda cortada / aguja atravesando tela, de cerca (ASMR) |
| `azamel.suck` | Grito invertido absorbido hacia un punto + "tink" de porcelana |
| `candles.out` / `wall.break` | Un soplido largo y 7 llamas apagándose / un golpe enorme y escombros |
| `phone.notify` | Notificación de chat |
| `morning.birds` / `kettle.whistle` | Desayuno |

#### m. Resolución: las 3 puntadas (secuencia lineal)
1. Cortás o quemás la lana para llegar a la Nona (daga o bengala).
2. **Agua bendita a Ofelia** en la falda de la Nona, si no quedó purificada antes.
3. **Puntada 1** (mantener la mirada): la tormenta de platos baja por la escalera.
4. **Puntada 2**: la Nona te **levanta** (la levitación de la Poseída) y te susurra con su voz de demonio: *"Nene, vení..."*.
5. **Puntada 3**: la lana te engancha el brazo y la puntada **se suelta**. **Choripán (ya bueno) entra corriendo, ladra y muerde la lana.** La mano de la Nona se cierra sobre la tuya: ***"Dámelo, nene. Esta vez lo cierro yo."*** Si está el P1, elegís **AZAMEL** mientras tira el último hilo.
6. La voluta se ve 2 s girando y **se la chupa la boca de Ofelia**. Se cose sola.
7. La Nona baja despacio: *"Sesenta y cinco años esperando para esto. ¿Me alcanzás el mate?"*
8. El frasco recoge a Ofelia sellada.
9. Desayuno (beat 17). Recompensa: $18.000, Ofelia, y **Choripán se va con vos**.

#### n. Cortado
Garaje, altillo, escalera de la vecina, pala, cartas largas de Anselmo, diario, cassette/grabador, recorte de diario, ficha del veterinario, Doña Chela, llamadas alternativas (en especial la de la Nona, que arruinaba el giro), bufanda como bonus de estadísticas, mate frío, ventilador, lavarropas, bocina, tablero aleatorio, enano de jardín Don Ramón, persecución bajo tierra, abrazo enroscado, tenazas/brasas/cuello quebrado de Jorge, exorcismo con libro de Lucía, barra de posesión de la Nona, agujas voladoras, siluetas en espejos, cámara lenta por tick rate, imagen en vivo en la TV, El Inquilino como entidad (P2: foto prerenderizada en la galería).

---

### 2.3 CASO 3: EL STREAMER · "Policlínico San Lázaro"

#### a. Ficha

| | |
|---|---|
| Clave / dimensión | `hospital` / `deadline:caso_hospital` (`fog_end` en 70) |
| Lugar | **Policlínico San Lázaro**, Villa Lucero (partido ficticio). Monoblock blanco de los 50. Cerró en julio de 1989, después del apagón del **Pabellón 6** |
| Antagonista | **El Eco** |
| Ancla | **El teléfono de Tomi**, que sigue transmitiendo, en un trípode con ring light, enchufado al conmutador de **La Central** (−3) |
| Personajes | Tomi Dark (vivo, sin voz), Graciela (mamá, por teléfono y en el chat), Gonza_Mod (moderador, por teléfono y en el chat), Don Cacho (el sereno, fantasma), la Audiencia (13 pacientes del Pabellón 6 = el chat muerto) |
| Tagline | **"No está vivo. Está EN VIVO."** |
| Edición | 5:00 (13:35–18:35) |

#### b. Historia
**Lo que entiende el público:**
1. Tomi entró a hacer *"24 HS EN EL HOSPITAL MÁS EMBRUJADO DE ARGENTINA (REAL) (NO FAKE)"*. El stream se cortó a las 3:33 con 40 espectadores. Agarrás su cámara y **el stream vuelve**.
2. **El chat son los muertos:** lo revela la Audiencia, con sus nombres de usuario flotando sobre las cabezas.
3. Tomi está **vivo** en un cajón de la morgue, sin voz: *"ME ROBÓ LA VOZ"*.
4. El Eco usa tu voz y tus gritos.
5. El teléfono de Tomi: **tus llamadas salieron de acá**.
6. Finalizás la transmisión, atrapás a El Eco y Tomi recupera la voz.

**Verdad interna:** ver §1.1. Además:
- El 9/7/1989 se cortó la luz por deuda (hiperinflación).
- Los 13 pacientes del Pabellón 6 siguieron las voces de sus familias por los teléfonos hasta el subsuelo.
- **Don Cacho** (Ernesto Funes), el sereno, murió en su puesto esperando un relevo que nunca llegó: hace 37 años.

#### c. Llamadas
**Llamada del caso (transición 2). "Graciela B."** (voz real recomendada, mujer mayor):
> *"Hola... ¿es el número de los fantasmas? Mi hijo es Tomás... Tomi Dark, en internet. Hace tres días que no vuelve. Me dijo que si no volvía los llamara a ustedes. Yo pensé que era para el video."* (pausa) *"Y decile que se lleve un abrigo."*

Aviso legal: *"Su llamada es muy importante para nosotros. Y para ellos."*

**Llamada durante el caso. Gonza_Mod** (voz real, en el ascensor):
> *"Loco, te estoy viendo en el stream de Tomi... ¿quién es el flaco alto de las orejitas que está en el ascensor con vos?"*

#### d. Reglas del caso
Están escritas por Tomi con **marcador IR** en la pared del hall. Solo se leen con la cámara (`hospital.reglas`) y también salen como cartel:
> **NO LE CREAS A NINGUNA VOZ · SI ESTÁS EN VIVO, TE VE · EL CHAT TE CUIDA... MENOS ECO_666**

#### e. Capítulos y objetivos

| Cap. | Objetivo en el HUD | Pista | Termina cuando | Checkpoint |
|---|---|---|---|---|
| 1 Llegada | "Entrá al hospital." | "La puerta está encadenada. La Guardia no." *(la entrada es el portón lateral, que lleva directo al hall)* | Entrás al hall | `auto` |
| 2 El hall de Tomi | "Agarrá la cámara de Tomi." / "Llamá a Tomi." | "Gritá su nombre. Capaz contesta." | Termina el eco | `hall` |
| 3 Pabellón 6 | "Subí al Pabellón 6." / "Prendé la cámara en la Sala de Día." | "Lo que ve la cámara, lo ves vos." | Termina la Audiencia | `pab6_reja` |
| 4 Ascensor | "Bajá." | "El ascensor anda. No tiene luz y anda." | Se abren las puertas en −3 | `ascensor_1p` |
| 5 Morgue | "Encontrá a Tomi." / "Traele el choripán al sereno." | "Cajón 7. ¿O 14?" | Cacho te da la llave de La Central | `morgue` |
| 6 La Central | "Purificá el teléfono de Tomi." / "Finalizá la transmisión." / "Atrapá a El Eco." | "La voz es mentira. Las orejitas, no." | El Eco en el frasco | `central_puerta` |
| 7 Salida | "Sacá a Tomi." | — | Cruzás la puerta | `central` |

#### f. El lugar
Es una **columna lineal**: hall → Pabellón 6 → ascensor → morgue → pasillo de servicio → La Central. Tiene unas 10 salas. Origen en el portón del hall; el edificio ocupa X −24..24 y Z 0..20. Pisos: PB en y=0 (techo y=5, hall de doble altura), 1P en y=6 y **−3** en y=−16.

```
EXTERIOR: auto de Tomi (rojo, balizas naranjas que parpadean) - ermita en la reja ("VOLVÉ TOMI", "TOMI PAGÁ EL SORTEO",
          velas, latas de energizante) - fachada con TextDisplay "POLICLÍNICO SAN LÁZARO" iluminado y con letras caídas
PB:  [HALL 17x11 doble altura: turnero, mostrador, sillas de espera, reloj parado 03:33, menú en australes,
      CAMPAMENTO DE TOMI: ring light prendido, silla gamer, latas, mochila con la CÁMARA] -> escalera -> 1P
1P:  PABELLÓN 6: reja + PASILLO 3x36 (8 tubos, CHASE) | 6 celdas 3x4 | SALA DE DÍA 14x10 (13 sillas -> TV en estante alto)
     | office de enfermería (llamador: solo la lamparita del 6 prendida) | ASCENSOR (cabina 3x3) al fondo
-3:  MORGUE 16x11 (24 cajones en 3 filas de 8, 2 mesas, Cacho) -> PASILLO DE SERVICIO 3x30 (teléfonos de pared cada 6,
     parlantes) -> LA CENTRAL 17x17x6 (paredes de conmutador con cables, 6 teléfonos de pared = puntos por donde sale
     El Eco, 4 pilares, luces de emergencia rojas, TRÍPODE con el teléfono de Tomi + ring light #2)
     ESCALERA DE SERVICIO -> PB (tapada con escombro hasta el apagón)
```

| Zona | Kit / props | Pistas y beats |
|---|---|---|
| **Exterior** | `hosp_fachada`, ventanas en banda a las que les faltan vidrios, auto rojo de Tomi (bloques y una calcomanía "TD" verde neón), **ermita** | `hospital.llegada` |
| **Hall** | Piso damero de linóleo, zócalo verde hospital, **turnero** (`hosp_turnero`, display con block entity: *"Su número: 666 · Atendiendo: 651"*), sillas de espera, reloj en 03:33, **menú del día en australes** (fondo, no se lee), **campamento de Tomi** (`hosp_ring_light` con luz 15, `hosp_silla_gamer`, latas, mochila) y la frase IR de las reglas en la pared | `hospital.hall`, `hospital.eco_tomi` |
| **Pabellón 6** | Reja de hierro + cartel "PABELLÓN 6 · CLAUSURADO 10/7/1989", pasillo de 36 con **8 tubos fluorescentes** (fixtures del grupo `pab6`), celdas acolchadas con mirilla, **Sala de Día** (13 sillas en 3 filas mirando una TV en un estante alto, rejas en las ventanas, pizarrón "ACTIVIDADES: Observación" de fondo) | `hospital.megafonia`, `hospital.audiencia`, `hospital.repeticion` |
| **Ascensor** | **Dos cabinas idénticas** (una en el 1P y otra en −3); el "viaje" es temblor + sonido + teletransporte invisible. Panel en TextDisplay: PB · 1 · S1 → "−3" | `hospital.ascensor` |
| **Morgue** | **24 cajones** (`hosp_cajon_morgue`, con estado abierto o cerrado y contenido). Luz fría de `soul_lantern` (10), un tubo que titila, 2 mesas de autopsia. Libro de ingresos en un atril (de fondo) | `hospital.morgue` |
| **Pasillo de servicio** | Caños, goteo, **teléfonos de pared** (`hosp_telefono_pared`) cada 6 bloques, parlantes | `hospital.tu_voz`, `hospital.popurri` |
| **La Central** | **Paneles de conmutador** con clavijas y cables (`hosp_conmutador`), sillas de operadoras, 6 teléfonos de pared, 4 pilares, 4 luces de emergencia rojas, **trípode con el teléfono de Tomi** y cable de clavija al conmutador, ring light #2 | Jefe |

**Iluminación:**
- **Exterior:** balizas, ermita y fachada (con luces débiles para que el monoblock blanco se lea en la niebla).
- **PB:** oscuro. Hay carteles SALIDA verdes (4) y el ring light de Tomi (15) es la primera "zona segura".
- **Pabellón 6:** prendido de entrada y apagado con CHASE en `hospital.megafonia`.
- **Morgue:** 10, frío.
- **La Central:** rojo giratorio. Se oscurece en el apagón.

**La linterna es una herramienta normal acá. No alimenta ninguna mecánica nueva.**

#### g. Entidades y pedidos de arte

**1. El Eco** (`EcoEntity`, nueva; P0)
- **Reglas:**
  1. **La voz es mentira.** Cuando habla (imitación o TTS robótica), el sonido sale de un teléfono de pared o de un parlante **lejos de su cuerpo**. El cuerpo, en silencio, se mueve hacia vos por otro lado.
  2. **Las orejitas, no.** Sus auriculares con orejitas RGB brillan siempre, en ciclo rosa y celeste. Es lo único que se ve en la oscuridad y la única forma confiable de ubicarlo.
  3. **Si estás EN VIVO, te ve.** No tiene ojos. Con la cámara de Tomi prendida, cada 12–20 s el chat dice dónde estás ("jaja está en la morgue") y El Eco recibe esa posición. Con la cámara apagada te busca por el último dato y por tu voz fuerte.
- **Movimiento:** **sale de los teléfonos de pared** (marcadores `phone_jack`): suena el auricular, se cae colgando del cable y salen los brazos. Camina encorvado (0,30) y no corre, salvo en la embestida guionada.
- **Ataque, "te roba la voz":** te agarra la cara con las dos manos: 4 de daño y −20 de cordura. **P1:** durante 6 s tu micrófono en vivo sale de su boca (steal REDIRECT).
- **Debilidades:**
  - la bengala lo hace gritar y meterse en el teléfono más cercano;
  - el agua bendita lo aturde 4 s;
  - el flash de la cámara de espíritus lo aturde 3 s, y en la foto se ve la boca abierta;
  - el crucifijo lo empuja;
  - **no se lo puede dañar hasta el apagón.**
- **Presencia:** el contador de espectadores sube con la cercanía (es un medidor de peligro) y el turnero avanza por capítulo.
- **Arte** (unos 180 cubos, 50 huesos, 256×256):
  - **Silueta:** 2,9 bloques, demacrado, torso demasiado largo, brazos hasta las rodillas, dedos de un bloque con 4 falanges, cabeza ladeada. Se lee como "un flaco alto con orejitas de gato".
  - **Cabeza:** óvalo alargado de piel gris blancuzca. **No tiene ojos**: donde deberían estar, **una boca estirada de sien a sien**, con labios agrietados, filas de dientes humanos chicos y una ranura negra. Esa boca tiene su propio hueso de mandíbula y se abre en vertical cuando imita. Donde debería estar la boca, piel lisa con una costura tenue.
  - **Auriculares:** los **de Tomi, gamer, con orejitas de gato RGB** (emisivas, ciclo #ff4fd8 → #3fe8ff), rajados, con el brazo del micrófono doblado delante de la boca de arriba.
  - **Cuerpo:** **envuelto en cables de teléfono en espiral** (beige, gris y negro) como vendas o venas. De la columna sale un cable enrulado que se arrastra hasta el piso (6 segmentos con balanceo): "el cordón a la línea". En el esternón, apenas visible, **un disco de teléfono incrustado**.
  - **Paleta:** piel #d8d4cc → #8f8a85, sombras #4e4a52, interior de la boca #1a0508, encías #6b1b22, dientes #e9e0c9, cables #c9b99a / #3b3b3b, auriculares #111.
  - **No** usar un aparato como cabeza (evita el parecido con Skibidi).
  - **Poses:** `emerge_phone`, `idle_listen` (cabeza ladeada), `mimic` (la boca de arriba bien abierta, la cabeza vibrando), `hunt`, `grab`, `shriek` (bengala), `hurt`, `husk` (enroscado en el piso, boca cerrada, orejitas titilando), `jar_suck`.
  - **Retrato de jumpscare:** la boca de arriba abierta a cuadro lleno, con las orejitas.

**2. La Audiencia, los 13 del Pabellón 6** (`AudienciaEntity`; P0)
- Sin IA, sin colisión salvo un empujón guionado opcional, y colocados por los beats.
- **Solo se ven con la cámara de Tomi prendida.** El renderer del cliente decide la visibilidad (cámara activa, o cordura menor a 20 en P2).
- Con la cámara prendida, **sobre cada cabeza flota su nombre de usuario** con el color de su nombre en el chat.
- **No giran la cabeza 180°:** se paran todos juntos, se dan vuelta con el cuerpo y señalan.
- El drenaje de cordura al verlos tiene un tope de 1 por segundo en total.
- **Arte** (variante del rig humano):
  - 1,8 bloques, flacos, **bata verde celeste #9fb7b0** con tiras atadas atrás, cabeza rapada con cicatriz y ganchitos, **cuencas negras hundidas** con 1 px de brillo celeste, **brillo azul de pantalla** emisivo desde abajo, pulsera blanca con raya roja, pies descalzos grises.
  - **Variantes:** **Chiche** (ruleros y redecilla: "abrigate, nene"), **Tito** (gorro de papel con una estrella: "¿quieren ver un truco?"), **Pelusa** (bufanda a rayas genérica: "REPETICIÓN"), **Hugo** (anteojos, brazos cruzados: "esto es fake"), **Tota** (trenza gris larga: gana el sorteo) y 8 genéricos.
  - **Poses:** `seated`, `stand`, `point_all`, `walk_calm`, `nod_goodbye`.

**3. Tomi Dark** (`TomiEntity`, variante del rig humano; P0)
- **Arte:**
  - 1,75 bloques, flaco, buzo negro con el logo **"TD"** verde neón, jogging gris, una media agujereada, pelo con las puntas decoloradas, ojeras.
  - **Sin auriculares**: tiene la marca roja en las orejas porque se los llevó El Eco.
  - Labios pálidos. Cuando intenta hablar, la boca se mueve y no sale nada.
- **Poses:** `lying_drawer`, `startled`, `write_glass` (dedo en el vidrio empañado), `mime_two_words`, `mime_movie` (manivela), `shake_head`, `grab_arm`, `stream_selfie` (celular en alto, al final).
- **Comportamiento:** después de la morgue **te sigue** (con IA simple de seguimiento y teletransporte si queda lejos). En el jefe se agacha detrás de un pilar.

**4. Don Cacho, el sereno** (`CachoEntity`; P1)
- Fantasma translúcido en sepia (alfa de unos 190, #e8d2a8). Petiso, panzón, gorra con el escudo genérico "SEGURIDAD", **bigotazo**, chaleco de lana, camisa celeste, linterna en el cinto, **mate y termo**.
- **Poses:** `stand_drawer` (la mano en la manija sin poder abrir), `eat_bite`, `sit_mate`, `wave_goodbye`.
- **Respaldo si no se hace:** la llave está en el cajón 7 y el gag se corta.

**5. Utilería:** `hosp_ring_light` (bloque de luz 15), `hosp_silla_gamer`, `hosp_turnero`, `hosp_telefono_pared` (auricular colgando como ItemDisplay), `hosp_conmutador`, `hosp_cajon_morgue`, trípode con el teléfono de Tomi (ItemDisplay `prop_celular_tomi` con pantalla emisiva "EN VIVO"), cámara de Tomi (ítem con modelo).

#### h. Guion de sustos

| # | id | Disparador | Qué pasa | Sonido | Marcas |
|---|---|---|---|---|---|
| 1 | `hospital.llegada` | Teletransporte | Aparecés junto al auto con las balizas en la niebla. La radio del auto se prende sola: estática y una voz cerca del micrófono, *"¿...estás en vivo?"* (5 s). La ermita: "VOLVÉ TOMI", "TOMI PAGÁ EL SORTEO" | `hospital.balizas`, `hospital.radio` | Plano de apertura |
| 2 | `hospital.hall` | Entrar al hall | El **ring light de Tomi sigue prendido** y hay una **silla gamer** en el hall (*"¿Trajo la silla gamer?"*). Ding-dong: el turnero **imprime un ticket solo: Nº 666.** "Atendiendo: 651." Agarrás la cámara: **EN VIVO · 3 espectadores**, se activa el chat (*"quién es este"*, *"volvió tomi?"*, *"nah este es más feo"*). Se reproduce el **VOD de 10 s de Tomi vivo** (voz real del amigo): *"¡Buenas buenas, chat! Tomi Dark, 24 horas en el hospital más embrujado de Argentina, REAL, NO FAKE. Saludos a mi vieja que me mira siempre... ¿qué fue eso? Es el viento, chat."* Con la cámara se leen **las reglas en IR** en la pared | `hospital.turnero`, `stream.live_on`, `tomi.vod` | `[RISA]` |
| 3 | `hospital.eco_tomi` | Objetivo "Llamá a Tomi" | Gritás "¡Tomi!" y se captura `tomi_call`. Desde el fondo oscuro del pasillo vuelve **tu propia voz**: *"¿Tomi...?"* Chat: *"eso fuiste vos?"* | imitación de voz (ECO) | `[CLIP]` (cold open) |
| 4 | `hospital.megafonia` | Llegar a la escalera | Ding de megafonía con **la voz de Tomi** (voz real): *"¡Chicos! ¡Estoy en el Pabellón 6! ¡Vengan!"*. Seguís arriba. Al fondo del pasillo **se prenden las orejitas RGB**. La voz de la megafonía **se degrada a TTS robótica a mitad de frase**: *"Chi-cos... es-toy... DONÓ CERO PESOS."* Los **espectadores saltan de 3 a 666**. Los tubos **se apagan uno por uno hacia vos**. Cuando volvés a mirar, las orejitas no están | `hospital.pa_chime`, `tomi.pa`, `eco.tts_degrade`, `hospital.chase_lights` | `[CLIP]` |
| 5 | `hospital.audiencia` | Entrar a la Sala de Día y prender la cámara | **Falso susto:** con la cámara se ve **una sola** paciente sentada, Chiche: *"¿Y vos quién sos, nene?"*. Apagás. Prendés: **13 sentados, todos con el cuerpo vuelto hacia vos**, con los nombres flotando: son los del chat. Apagás. Prendés: **parados, 3 bloques más cerca, señalándote todos.** Apagás. Prendés: **la cara de Chiche a 20 cm.** *"Abrigate, nene."* En el chat, los nombres de ellos **pasan a gris pálido** | `stream.cam_on/off`, `audiencia.stand`, `audiencia.abrigate` | `[CLIP]` (giro A: el chat son los muertos) |
| 6 | `hospital.repeticion` | Primer grito detectado en el caso (o, a los 60 s, el mejor grito fijado) | Chat, `pelusa_10`: **"REPETICIÓN"**. Ding de megafonía. Locutora de los 80: *"Repetición."* Por los parlantes del pasillo suena **tu grito**. *"Repetición en cámara lenta."* Tu grito otra vez, **lento y grave**. Chat: *"CLIPEEN ESO"*, *"JAJAJA"*. Subtítulo "[tu voz]" | `hospital.pa_voice`, imitación (SCREAM → SLOWMO) | `[CLIP]` `[RISA]` |
| 7 | `hospital.ascensor` | Usar el ascensor | Las puertas se cierran. Panel: PB · 1 · S1... y sigue bajando: *"Subsuelo... tres"* (TTS con glitch). **Te llama Gonza**: *"Loco, te estoy viendo en el stream... ¿quién es el flaco alto de las orejitas que está en el ascensor con vos?"* Te das vuelta: un rincón de la cabina, la luz titila, nadie. Ding. Se abren las puertas en la morgue | `hospital.elevator_*`, `gonza.call` | `[CLIP]` |
| 8 | `hospital.morgue` | Entrar a la morgue | **Cacho** frente al cajón 7: *"¿Usted es el relevo? Estoy acá desde el 89. Dejé un choripán en el siete y no lo puedo abrir: los muertos no tenemos fuerza en las manos, pibe."* (Chat: *"choripán? no era el perro del otro video??"*). **Golpes en el cajón 14.** Lo abrís: **Tomi, vivo.** Gritan los dos (susto cómico). No puede hablar: empaña el vidrio de la mesa y escribe **"ME ROBÓ LA VOZ"**. Mímica: *"¿Dos palabras? ¿Película?"*. Le das el choripán a Cacho: *"Está frío. Pero está bueno."* y te da la **llave de La Central**: *"No mire mucho los teléfonos, pibe."* | `hospital.morgue_knock`, `hospital.morgue_drawer`, `cacho.*`, `hospital.fog_squeak` | `[RISA]` (susto cómico + mímica) |
| 9 | `hospital.tu_voz` | Mitad del pasillo de servicio | Desde la otra punta, **TU voz**: tu mejor clip `call` (por ejemplo "¡Tomi!"). Tomi te agarra del brazo y niega con la cabeza | imitación (CALL) | Terror |
| 10 | `hospital.popurri` | Seguir avanzando | **Todos los teléfonos de pared suenan a la vez** y de todos sale **un coro con tus gritos del colegio y de la casa**. Chat: *"esos son los gritos del colegio jajaja"*; `Eco_666`: *"seguí la voz"*. Las orejitas RGB a 10 bloques. Corrés hacia La Central | imitación (CHOIR) | `[CLIP]` (el más viral) |
| 11 | `hospital.telefono_tomi` | Entrar a La Central | En el trípode, el teléfono de Tomi con la pantalla del **registro de llamadas**: tus dos llamadas anteriores como **salientes**, y **"HOY 03:33 → [TU NOMBRE] (programada)"**. Megafonía: *"Número seiscientos sesenta y seis, pase por La Central."* | `hospital.pa_voice` | Giro (S3) |
| 12 | `hospital.jefe` | Ver m. | El Eco sale del conmutador | — | Terror puro, sin chistes |
| 13 | `hospital.apagon` | Fin de "Finalizar transmisión" | **NEGRO ABSOLUTO Y SILENCIO TOTAL durante 5 s.** Un solo clic de linterna | `stream.end` | No se musicaliza |
| 14 | `hospital.cierre` | Frasco | A Tomi le vuelve la voz: ***"...¿Seguimos en vivo?"*** Reinicia el stream: **1.200.000 espectadores**, chat "LEYENDA" y "GG". *"Bueno chicos, like y suscríbanse... y el sorteo lo gana... tota1931."* Chat: *"tota1931: ¡AY, SÍ!"* Vos: ***"Te mato."*** Plano único: los 13 saliendo a contraluz por la escalera, con el amanecer (tinte del HUD), y Cacho saludando: *"Ya me relevaron."* | `tomi.final`, `tota.ay_si` | `[RISA]` y catarsis |

#### i. Humor (el mínimo, después de los sustos)
- El chat: *"quién es este bobo"*, *"F"*, *"TOMI PAGÁ EL SORTEO"*, *"VENDO DÓLARES"* (troll genérico), `hugomol`: *"esto es fake"* (está muerto).
- La silla gamer, el ticket 666, la Repetición, Cacho y el choripán, la mímica.
- Donaciones: arrancan graciosas (*"Juani_07 donó $50: saludos a mi vieja"*) y se vuelven siniestras (*"Anónimo donó $0: ya te vi"*; *"Eco_666 donó $666: apagá la linterna"*, y la linterna se apaga 3 s).
- El remate de Tomi y "Te mato".
- **Nada de chistes desde `hospital.tu_voz` hasta el apagón.**

#### j. Mecánicas e ítems nuevos

| Ítem / mecánica | Detalle | Prio |
|---|---|---|
| `camara_tomi` (StreamCameraItem) | Clic derecho: prende o apaga. **Prendida**: shader de **visión nocturna + VHS** combinado, marco "● EN VIVO · N 👁", chat en el HUD, Audiencia visible, texto IR visible. Mientras está prendida **estás en vivo**: el chat dice tu posición cada 12–20 s. Sin batería (el costo es que te delatan). Al agarrarla por primera vez se reproduce el VOD | P0 |
| Chat en vivo y donaciones | §3.9. Pools con guion + reglas + `Eco_666` que miente. Las donaciones con TTS usan **la voz robótica de El Eco**. Comandos del director | P0 |
| Espectadores como medidor de peligro | Base del capítulo + factor de cercanía a El Eco. Saltos guionados (3 → 666) | P0 |
| Turnero | Block entity con display. Ticket `numero_666`. Avanza por capítulo: 651 → 655 → 660 → 665 → 666. Megafonía | P0 |
| Ascensor | Dos cabinas idénticas + teletransporte durante el temblor | P0 |
| Cajones de la morgue | Bloque con estado abierto, actor adentro (Tomi acostado), escritura en el vidrio empañado (TextDisplay letra por letra) | P0 |
| Registro de llamadas | Pantalla de teléfono reutilizada (§3.10) | P0 |
| Mantener para cortar | "**¿Finalizar transmisión? N espectadores**": mantener 5 s con anillo de progreso | P0 |
| Apagón | Para todo: el sonido del cliente, `VoiceBridge.stopAll()`, vacía las colas de chat y donaciones, pone negro 5 s y deja un clic final | P0 |
| Modo coprotagonista "Tomi" | El amigo juega de Tomi desde el cajón 14. **Su micrófono queda silenciado hacia el creador** hasta el final del jefe (steal MUTE). El Eco reproduce los clips del amigo desde otros lugares (*"¡vení, por acá!"*). La mímica es real. Al terminar, el micrófono se abre: *"¿Seguimos en vivo?"* | P1 |
| Spirit box (rueda) | *"¿Dónde está Tomi?"* → "EN EL CAJÓN" / *"¿Quién me llamó?"* → "YO" (TTS robótica) / ***"¿Estás vivo?" → "EN VIVO"*** / *"¿Cuántos son?"* → "TRECE" / *"¿Qué querés?"* → "TU VOZ" | P0 |
| Herramientas | **Linterna** normal. **Bengala**: lo hace retroceder. **Agua bendita**: lo aturde y purifica el teléfono. **Flash**: lo aturde. **Crucifijo**: lo empuja. **Sal**: frena su caminata pero no que salga por los teléfonos. **EMF**: 5 cerca del teléfono de Tomi. **Frasco**: captura final | — |

#### k. Imitación de voz (uso pleno)
Eco "¿Tomi?" · Repetición (normal y cámara lenta) · tu voz CALL · popurrí CHOIR · señuelos y ruego en el jefe · P1: te roba la voz al agarrarte. **Respaldos:**
- si no hubo grito en el caso, se usa el mejor grito fijado de otro caso (*"Repetición... del colegio"*);
- sin SVC, se usan las líneas de `mimic.fallback.*`.

#### l. Sonidos nuevos

| Clave | Descripción |
|---|---|
| `hospital.ambient` | Goteo, zumbido lejano de fluorescente, viento por vidrios rotos, dron grave de 40 Hz |
| `hospital.balizas` / `hospital.radio` | Relé "tic... tac" / estática + "¿...estás en vivo?" |
| `hospital.turnero` | Ding-dong con dígitos que pasan + impresora térmica |
| `hospital.pa_chime` / `pa_voice` | Campanita de 3 notas con reverb / locutora TTS con filtro de megafonía: "Repetición.", "Repetición en cámara lenta.", "Número seiscientos sesenta y seis, pase por La Central.", "Número seiscientos sesenta y seis... atendido.", "Subsuelo... tres" |
| `hospital.fluor_buzz` / `flicker` / `chase_lights` | Hum de 50 Hz / arrancador / tubos que se apagan uno por uno con un "tunk" |
| `hospital.elevator_ding` / `motor` / `overrun` / `open` | Ding cuando no debería andar, motor, chirrido de seguir bajando, puertas |
| `hospital.morgue_drawer` / `morgue_knock` / `fog_squeak` | Cajón pesado de metal / golpes huecos desde adentro / dedo sobre vidrio empañado |
| `stream.live_on` / `live_off` / `end` | Sting de "EN VIVO" / clic / golpe sordo + silencio total |
| `stream.donation` | **Jingle original de donación**: arpegio de 8 bits ascendente + moneda. Tiene que volverse icónico |
| `stream.tts` (×10) | Voz robótica de El Eco (em_alex monótono con pitch cuantizado y bitcrush leve): las donaciones, "NO.", "DONÓ CERO PESOS" |
| `chat.pop` | Tic sutil de mensaje |
| `tomi.vod` / `tomi.pa` / `tomi.ruego` / `tomi.final` | **Voz real del amigo**: VOD; "¡Chicos! ¡Estoy en el Pabellón 6!"; "no cortes, chicos... no cortes"; "¿Seguimos en vivo?... like y suscríbanse... el sorteo lo gana..." |
| `eco.emerge_phone` | Auricular que se cae, tono de línea deformado, el cable estirándose |
| `eco.ears_hum` | Zumbido agudo de LED RGB (loop posicional) |
| `eco.step` / `grab` / `shriek` / `hurt` | Pasos de piel descalza, agarre, chillido con distorsión de línea, dolor |
| `eco.tts_degrade` | Una voz real que se rompe en TTS robótica |
| `eco.husk_whisper` | TTS robótica: "...sin... voz..." |
| `audiencia.stand` / `audiencia.abrigate` | 13 sillas arrastrándose a la vez / "Abrigate, nene" (Chiche) |
| `cacho.lines` / `cacho.chew` / `cacho.mate` | **Voz real** (hombre mayor), masticada, sorbo de mate |
| `gonza.call` | **Voz real** (amigo), filtro de teléfono |
| `graciela.call` | **Voz real** (mujer mayor) |
| `tota.ay_si` | "¡AY, SÍ!" de viejita |

#### m. Resolución: el jefe (`hospital.jefe`, unos 3–5 min en crudo)
1. **Fase 1: Llegar al teléfono.**
   - El Eco sale del conmutador y circula entre los 6 teléfonos de pared.
   - Suelta voces (tus clips, la voz de Tomi, *"¡Ayudame!"*) desde direcciones **falsas**.
   - El chat avisa *"ATRÁS"* (verdad) y `Eco_666` miente (*"izquierda"*, *"seguí la voz"*).
   - Hay que acercarse al trípode y tirarle **agua bendita al teléfono** (2 impactos, porque El Eco lo cubre). Las bengalas y el flash sirven para hacerle lugar.
2. **Purificado** → "Conexión inestable". El stream tartamudea. En la pantalla del teléfono aparece **FINALIZAR TRANSMISIÓN**.
3. **Mantener 5 s.**
   - El chat se inunda de *"NO CORTES"* ×100 y las donaciones TTS dicen *"NO. NO. NO."*
   - El Eco **ruega** con tus clips (SLOWMO, quebrados) y con la voz de Tomi (*"no cortes, chicos..."*).
   - Un mensaje distinto, de `graciela_mama`: ***"cortá, querido. traémelo."***
   - El Eco puede interrumpir **una sola vez**: te agarra y te aparta 4 bloques. El segundo intento ya no se puede interrumpir.
4. **Apagón** (beat 13).
5. **Clic.** El Eco está enroscado en el piso (`husk`), con la boca cerrada y las orejitas titilando, apagándose: *"...sin... voz..."*. Usás el **frasco**: queda adentro con el brillo RGB latiendo.
6. Megafonía: *"Número seiscientos sesenta y seis... atendido."*
7. La escalera de servicio aparece despejada. **Cierre** (beat 14). Recompensa: $1.500.000 y el frasco de El Eco (trofeo).

#### n. Cortado
Dr. Mendizábal / El Ojo, Lauti, Norma muerta, el sistema de 32 cámaras CCTV, el secuestro del POV, la sala de observación (queda en P2 con UN monitor-cámara), Rayos X, farmacia, cafetería, admin, capilla, depósito, quirófanos, ala colapsada, techo, dron, baño del espejo, archivo muerto, candado 1988, cintas U-matic, pulseras coleccionables, llamador como radar, desfibrilador, Nene de la Caja, camilla (P2), Lauti en patineta, eco con retardo de 10 minutos, CAM 15 con "tu primera frase", señuelos cruzados en cooperativo, llamadas de Gonza y Lauti como variantes del caso, exportar audio de imitación, cielo de amanecer por mixin (se usa tinte del HUD), "TURNO 1.991".

---

### 2.4 La base (`deadline:base`)
- **Monoambiente** de 9×7: cama, mesa con mate y termo, kit colgado, ventana con lluvia, puerta de entrada (`base_door`).
- **Estante de trofeos** con 3 marcadores (`trofeo_regla`, `trofeo_ofelia`, `trofeo_frasco`). Se llena con ItemDisplay según los casos resueltos.
- Lugar de Choripán (cucha y bufanda).
- Noche fija a las 3:33, sin niebla densa.
- Es donde transcurren la intro, las transiciones, el final y el post-créditos.
- Choripán vive acá después del caso 2: es una entidad mascota en forma DOG, sin IA hostil.

---

## 3. Sistemas compartidos (plan por clases)

### 3.0 Arreglos al código existente (P0, antes que nada)

| # | Archivo / sistema | Problema | Arreglo |
|---|---|---|---|
| F1 | `client/render/ModRenderers` | Todos los haunts usan `NoopRenderer`: hoy no se ve ninguna criatura | Conectar los modelos de `tools/models/java` (Monja, Muñeca, Poseida, Ánima, Sombra) + `ModelLayers` + `GlowLayer` |
| F2 | `CaseManager.onRespawn` | La muerte hace fallar el caso y limpia el sitio | Reaparecer en el checkpoint del capítulo actual con cordura 60 y mantener el caso. Gag de La Operadora |
| F3 | `ActiveCase.stage` 0–3, HUD con 4 marcas fijas | Las etapas están cableadas | `chapter` + `ObjectiveChecklist` por capítulo y HUD dinámico. "Resuelto" pasa a ser una bandera |
| F4 | `CaseType` | Hay 5 casos | Quedan `COLEGIO`, `CASA` y `HOSPITAL` (+ `BASE`) en `values()`. Las clases de río, bosque y parque se quedan sin registrar |
| F5 | `ModEntities.MONJA` 0,8×2,7 | No pasa por las puertas | 0,7×1,95, con el modelo de 2,7 |
| F6 | `FlashlightLights` | Solo pone luz donde el rayo pega en un bloque, así que la monja no se entera del haz en salas grandes | Agregar un chequeo de cono contra entidades `Spectral` (`onBeam`). No colocar luz en zonas marcadas `sealed` (cuarto espejo) |
| F7 | `SpiritBoxItem` | Elige una frase al azar | Rueda de preguntas por caso (§3.10) |
| F8 | `worldgen/biome/bruma_casa.json` | Agua roja | Verde turbio |
| F9 | `dimension_type/caso_*` | `fog_end` 40 | Hospital en 70. El colegio y la casa se quedan en 40 o 48. Se renombra `caso_convento` → `caso_colegio` |
| F10 | `ClientFx` | Un solo efecto de postproceso; el VHS, la visión nocturna y la locura se pisan | `PostEffectStack`: shader combinado `deadline:vhs_nv` con parámetros (visión nocturna on/off, locura 0–1, VHS on/off) + prioridad. Se vuelve a aplicar después de cambiar la cámara |
| F11 | Setters privados de `Display` | No hay acceso | Access widener (o un mixin común con invokers) para `setTransformation`, la interpolación, `BlockDisplay#setBlockState`, `ItemDisplay#setItemStack`, y el texto, fondo y opacidad de `TextDisplay` |
| F12 | Construcción del sitio en un tick | Trabón de varios segundos y chunks a medio iluminar en cámara | Construcción **en tandas** (unos 4.000 set por tick) durante el fundido de 70 ticks, más `/deadline case prebuild` |
| F13 | Romper o poner bloques en los casos | El creador puede romper vidrios, puertas o luces y saltearse un guion | Se cancelan en las dimensiones de caso (con lista blanca: tablas de la celda, velas) y se aplica la amonestación "Por daños al edificio" |
| F14 | `tools/audio/dsp.py:355` `lang='es'` | espeak "es" castellano: sale "grathias" | `lang='es-419'` + posprocesado de fonemas para el sheísmo (ll/y → ʃ) vía `is_phonemes`. Prueba de escucha con 3 líneas antes de generar en lote |
| F15 | `SanityManager` | El Hombre Sombra y la oscuridad drenan igual en todos los casos | Tabla por caso: el Hombre Sombra **apagado** en los 3 casos. Colegio: la Madre aparece como alucinación (P1). Hospital: la alucinación son mensajes del chat con **tu nombre** (*"[Jugador]: no quiero estar acá"*) |

### 3.1 Sitios (`com.deadline.site`)
- **`Marker(id, kind, pos, box, facing, blocks, group)`** con los tipos `POINT, AREA, DOOR, FIXTURE, PROP, ACTOR, SPEAKER, PHONE_JACK, WRITE_SURFACE, CHECKPOINT, SEALED`.
- **Helpers nuevos de `SiteBuilder`:** `marker`, `area`, `door`, `fixture`, `prop`, `actor`, `speaker`, `phoneJack`, `writeSurface`, `checkpoint`, `sealed`.
- **`SiteState`** (SavedData por dimensión de caso): marcadores, `actors` (id → UUID), beats disparados, banderas, puertas trabadas, estado del demonio, capítulo y `seed`.
- **`SliceBuilder`:** coloca los bloques de un `Layout` en tandas por tick. `CaseManager.startCase` espera a que termine la construcción antes del fundido de entrada.
- **`restartSite`** (`/deadline take reset`): limpia todas las entidades con tag `deadline:site/<n>` (displays, NPC, props), reconstruye con el mismo seed, reinicia el `SiteState` hasta el capítulo actual (con el `setup` del capítulo), reaparece actores y teletransporta.
- **`BuildProtection`:** un callback de break/place por dimensión.
- **Kits:** cada sitio usa sus bloques `colegio_*`, `casa_*`, `hosp_*` generados por `tools/blocks` (`ModBlocksGen`). Los fixtures del kit tienen la propiedad `LEVEL` (0–15) para atenuar (§3.5).

### 3.2 Director lite (`com.deadline.director`)
Versión recortada de `01_sistemas.md` §4: sin medidor de tensión ni pool de ambiente en P0.

- **`CaseScript`** (`ColegioScript`, `CasaScript`, `HospitalScript`): `define(ScriptBuilder s)` declara capítulos (`s.chapter(n, nombre, checkpointMarker, setup)`), beats y cues.
- **`Beat`:** id `"<caso>.<nombre>"`, disparador, condiciones (`requires(flag)`, `chapter(n)`), `once()` / `repeat(cooldown)`, `observed(marker)` / `unobserved(area)`, `tags(...)` y cuerpo (`Step`).
- **Disparadores P0:**
  - `enter(area)`, `inside(area, ticks)`, `lookAt(target, deg, ticks, dist)` (con línea de visión, escalonado);
  - `time(sinceFlag, ticks)`, `flag`, `itemUse(item[, area])`, `interact(marker|actor)`, `anchorPurified`;
  - `entity(actor, STATE)`, `voice(dbRel, ms)`, `scream()`, `silence(ms)`, `cue(slot)`, `beatDone(id)`.
- **Pasos P0:**
  - Flujo: `seq`, `par`, `wait`, `waitUntil`, `random`.
  - Estado: `flag`, `objective`, `chapter`, `title`.
  - Fx: `sound`, `loop/stopLoop`, `shake`, `flash`, `redFlash`, `static`, `fade`, `jumpscare`, `stamp(motivo)` (amonestación).
  - Diálogo: `say(speaker|actor, lineId)`, `phoneCall`.
  - Voz: `mimic(intent, emitter, fx, tag)`.
  - Poltergeist: `door`, `lights`, `lift/throw/orbit/aim/levitate`, `write`, `swapUnseen`.
  - Actores: `spawn`, `despawn`, `teleport`, `face`, `anim(actor, actionId, ticks)`, `possess`, `wisp(from, to)`, `choripan(form)`, `actorSwap`.
  - Stream: `chat`, `chatPool`, `donate`, `viewers`, `turnero(n)`.
  - Takes: `clipMark`.
- **`StepRunner`:** las secuencias corren sin persistirse. Un beat `once` se marca como disparado al empezar.
- **`Director`:** uno por sitio activo. `tick()` escalona los disparadores encuestados, `post(SiteEvent)` maneja los de evento, `fire(id, target, force)` y `cancelAll(restore)` (prende las luces y asienta los props).
- **Multijugador:** el objetivo `STAR` es el protagonista (`/deadline star`), así el amigo en espectador nunca es la víctima.
- **Validación en CI:** cada script referencia marcadores, actores y líneas que existen. En el smoke test se dispara cada beat con `force` sobre un `FakePlayer` y se corren 400 ticks sin excepciones.

### 3.3 Imitación de voz con Simple Voice Chat (`com.deadline.voice` + `.voice.svc`)
**Dependencia opcional:**
- `compileOnly "de.maxhenkel.voicechat:voicechat-api:2.6.24"` (maven henkelmax).
- Entrypoint `"voicechat"` → `DeadLineVoicechatPlugin` y `"suggests": {"voicechat": "*"}` en `fabric.mod.json`.
- **Nada fuera de `voice.svc` importa `de.maxhenkel.*`.**
- `-PnoVoicechat` excluye `voice/svc/**` para builds offline (el sandbox de agentes recibe 403 de ese maven; CI sí llega).

**Clases (siguen `01_sistemas.md` §6, que ya está verificado contra la API):**
- `VoiceBridge` (interfaz; `NoVoiceBridge` por defecto) con `available()`, `consented()`, `play(MimicRequest)`, `stop/stopAll`, `steal`, `speaking`, `loudnessDb`, `tagNext(uuid, tag, windowMs)`, `pin`, `clear` y `drainServerEvents`.
- **SVC:** `DeadLineVoicechatPlugin`, `SvcVoiceBridge` (en `onMic` hace solo trabajo O(1): consentimiento, robo de voz y encolado), `VoiceRecorder`/`VoiceTrack`/`Utterance`, `VoiceAnalyzer` (decodifica, VAD, segmenta, mide pico, `loudRatio`, `rising`, `contaminated`), `ClipSelector` (intentos CALL/ECHO/SCREAM/WHISPER/CHOIR/QUOTE), `MimicScheduler` (un hilo a 20 ms, sin `createAudioPlayer` por jugador), `Playback`, `LiveSteal` y `dsp/{PitchShifter, Resampler, Reverse, Stutter, Layer, Biquad, Reverb, Limiter}`.
- **Hilos:** el hilo de SVC encola. El ejecutor `deadline-voice` decodifica y segmenta. El programador `deadline-mimic` reproduce. El hilo de Minecraft elige clips y crea canales.
- **Emisores:** `At` (canal locacional), `Follow` (canal de entidad), `Speakers` (N canales locacionales con una sola codificación), `InHead` (canal estático + `addTarget`).
- **Presets de FX:** DRY, RADIO, PA, BACKWARDS, SLOWMO (remuestreo 0,6), CHOIR (3 capas ±3/±7 st con retardos y reverb), DEMON, WHISPER_IN_HEAD.
- **Categoría de volumen** `deadline_mimic` ("DEAD LINE — voces").

**Agregados de esta biblia:**
1. **Capturas etiquetadas sin reconocimiento de voz.** El guion abre una "ventana de etiqueta" (`tagNext(uuid, "chori_call", 4000)`) y la primera frase dentro de esa ventana recibe la etiqueta. Si no hubo voz, la etiqueta queda vacía y se usa el respaldo.
2. **`VoiceStore`** (persistencia opt-in):
   - los clips **fijados** se guardan como tramas Opus en `<mundo>/deadline_voice/<uuid>/<tag>.opus` (los gritos: `scream_1..6`, con los 6 picos más altos de cada caso);
   - el resto vive en RAM y se borra al terminar el caso;
   - `/deadline voice clear [all]`;
   - **solo** para jugadores con `voiceConsent && voicePersist` (pantalla de opciones del primer arranque).
3. **`Calibration`:** en la lista del colegio (o con `/deadline voice test`) se mide la voz normal (`baseDb`). Los umbrales se expresan relativos a esa base: grito = base + 12 dB; hablar en el Gran Silencio = base − 6 dB; silencio = base − 10 dB.
4. **Reglas de grabación:** **activación por voz** (no push-to-talk). `/deadline voice test` avisa si no llegan paquetes. Se recomiendan auriculares (la bandera `contaminated` evita realimentación).
5. **Inyección para CI y desarrollo:** `/deadline voice inject <wav> [tag]` carga un WAV en el mismo pipeline de PCM, para probar la selección y el DSP sin micrófono.
6. **Robo de voz:**
   - **MUTE** (modo coprotagonista): el paquete se cancela y no se reenvía.
   - **REDIRECT** (P1, El Eco te agarra): se cancela y se reenvía al canal de entidad del ladrón; en solitario el creador se oye a sí mismo desde el monstruo.
7. **Respaldo (`NoVoiceBridge`):** `mimic.fallback.call|echo|scream|name` (4 variantes `em_alex` procesadas) con el subtítulo *"(una voz parecida a la tuya)"*, más espacios de resource pack para grabaciones propias.
8. **Privacidad:** indicador rojo "● VOZ" en el teléfono y en el HUD mientras graba. Consentimiento por jugador. README con instrucciones.

### 3.4 Ruido y escucha (`NoiseMeter`, `HearingGoal`)
- **`NoiseMeter`** por jugador (0–100, baja 8 por segundo):
  - **voz:** solo cuando supera el umbral del modo; `isWhispering` cuenta como 0;
  - **otros ruidos (también sin SVC):** correr +12, aterrizar de un salto +8, puertas o trapdoors +10, romper o poner un bloque +15, tirar un ítem +5, bengala +20, tablas que crujen (bloque del kit) +10;
  - agachado, la mitad.
- **Modos (los pone el script):**
  - `SHOUT_ONLY` (por defecto en el colegio): solo gritos;
  - `SPEECH` (Gran Silencio): cualquier voz por encima de base − 6;
  - `PRAYER` (Maitines): la voz suma progreso de oración y también atrae.
- **`HearingGoal`:** con ruido mayor a 55 dentro de 40 bloques, la monja crea una marca de sonido y camina hacia ella. Escalonado: el primer ruido en 15 s solo provoca un "shh" de las nenas.
- **HUD:** ícono de micrófono junto al ECG, que se pone rojo con "TE ESCUCHA". **Solo en el colegio.**
- Se reutiliza en el hospital: un grito acerca a El Eco y dispara la Repetición.

### 3.5 Poltergeist (`com.deadline.polter`)
- **`PropManager`:**
  - `lift(BlockPos)`: lee el bloque, deja aire y crea un BlockDisplay idéntico. Sirve también para muebles del kit.
  - `settle`: vuelve a poner el bloque real en el lugar libre más cercano.
  - Props ItemDisplay para mate, termo, platos, cuchillos y muñecas.
- **`Motion`:** `Hover`, `Rise`, `Orbit`, `Aim`, `Throw`, `Fall`, `Stuck`. La posición se actualiza por tick con `posRotInterpolationDuration=2`. Para girar alrededor del centro, trasladar −0,5.
- **`PropCollision`:**
  - el clip contra bloques decide SHATTER, STICK o BOUNCE_SETTLE;
  - el clip contra el AABB del jugador inflado aplica daño `deadline:poltergeist` ("recibió un platazo del más allá"), empujón, sacudón y −5 de cordura;
  - **los tiros guionados de "casi te pega" usan una trayectoria fija sin colisión**.
- **`DoorFx` / `DoorLocks`:** OPEN, CLOSE, SLAM, KNOCK, RATTLE, LOCK.
- **`LightGroups`:** los fixtures del kit con `LEVEL`. Patrones: parpadeo tipo Quake (texto `a`–`z`), CHASE (en orden con retardo), BLACKOUT y RESTORE. Tope de 10 cambios por tick y 8 parpadeando a la vez. Además, un `BROWNOUT` solo del cliente.
- **`WallWriter`:** TextDisplay FIXED con fondo transparente, sin sombra, escala de 1,5 a 3. Escribe letra por letra con un sonido por glifo. Fuentes `chalk` y `blood` (P1) con Ñ, tildes, ¿ y ¡. Tokens `{player}` (lee `/deadline name`). `revealUV(near)` para los mensajes que solo se ven con UV.
- **`UnseenSwap`:** aplica un cambio cuando ningún jugador tuvo el área en un cono de 100° con línea de visión durante N ticks. `onFirstSeen` dispara el acento de sonido y un marcador de toma. Se usa para la torre de sillas, para dar vuelta los pupitres (en el caso de la lista se hace por guion con BlockDisplay), para la monja al fondo, para las ubicaciones de Ofelia y para la Audiencia.
- **Presupuestos por sitio:** 48 props display (10 volando a la vez), 12 TextDisplay, 0 FallingBlock para muebles. Los props a más de 48 bloques de cualquier jugador se congelan.

### 3.6 NPC, posesión y especiales (`com.deadline.npc`)
- **`Spectral`** (interfaz): `spectralActive()`, `onHoly(source, by, power)`, `onBeam(by)`, `jarable()`, `emfStrength()`. `HauntEntity` la implementa sobre su lógica actual. Las herramientas (crucifijo, agua bendita, cámara, spirit box, EMF, frasco) pasan a filtrar por `Spectral` (es un diff mecánico).
- **`FamilyNpcEntity`** (Marta, Jorge, Nona, Toti, Tomi, Cacho):
  - datos sincronizados `VARIANT`, `STATE`, `POSSESSION` (0–1), `ACTION`;
  - **invulnerable al daño no sagrado**: golpear a un familiar dispara un bark (*"¡Oiga! ¿Qué le pasa?"*, *"¡ES MI MARIDO!"*) y −5 de cordura;
  - charla con `mobInteract` → `DialogueService.say` desde un pool por capítulo;
  - **los recorridos guionados se hacen fuera de cámara + teletransporte** (no se confía en el pathfinding vanilla).
- **`PossessionComponent`** (simplificado): `begin(FULL)` corre la transición (congelarse, tic, levitar 0,6, `POSSESSION` de 0 a 1 en 40 ticks, línea, destello); `free()` deja KO 100 ticks y una línea al recuperarse. Cada huésped tiene **su verbo**: no hay barra de posesión genérica.
- **`DemonWisp`:** entidad invisible sin física que recorre una curva de Catmull-Rom soltando partículas y hace titilar las luces de las salas por donde pasa.
- **`ActorSwap`:** cambia una entidad por otra con destello, humo y sonido (Lucía normal ↔ `PoseidaEntity`).
- **`DoppelgangerEntity`** (P1, solo el modo MIRROR en el colegio): `PlayerModel` con la skin del jugador (busca la `PlayerSkin` por UUID) y una capa de **sonrisa** pintada. Copia la posición y la rotación espejadas sobre el plano del espejo. El guion puede "atrasarlo" (buffer de 10 ticks) y desacoplar su mirada.
- **`YarnWeb`** (P1): segmentos de BlockDisplay entre anclajes. La colisión es la distancia entre el segmento y el AABB. El corte es un rayo contra el segmento.
- **`StitchMinigame`:** el servidor chequea el ángulo de la mirada contra la cabeza de Ofelia (umbral fino). El cliente dibuja el anillo que se achica con un payload de Fx.

### 3.7 Choripán (`ChoripanEntity`, cliente `ChoripanRenderer`)
- **`FORM`:** DOG, UNEASY, TRANSFORMING, BEAST, REVERTING. `refreshDimensions` al cambiar: el DOG mide 0,6×0,85 y el BEAST tiene **hitbox de cabeza 0,8×0,8**.
- **Cuerpo en cadena (solo cliente):**
  - el renderer guarda por entidad un buffer circular de posiciones interpoladas de la cabeza;
  - los eslabones del modelo se dibujan en puntos sucesivos de esa historia;
  - con un `trailAnchor` (la puerta de la cucha) los eslabones salen de ahí: es el efecto de "salir sin terminar nunca" y la cola queda meneándose en el ancla;
  - **hay que ampliar el bounding box de culling** para que el cuerpo no desaparezca en las esquinas;
  - se respeta la escala 0,5 del modelo, el espacio +Y hacia abajo y la conversión del yaw del cuerpo.
- **Metas:** `FollowHunterGoal` / `BarkAtSpectralGoal` (DOG); `ChaseGoal`, `LungeGoal` (BEAST); `FetchDistractGoal` (ítem a menos de 8 bloques); `SaltBlockedGoal` (gime contra la sal); `BegGoal` (si tenés el chorizo en la mano); `CatchBlessedGoal`.
- Invulnerable, sin frasco. El agua bendita y el crucifijo lo aturden.
- **Reversión:** al comerse el choripán bendito: animación `retract`, la voluta sale, vuelve a DOG y estornuda.

### 3.8 Diálogo, subtítulos y voces (`com.deadline.dialogue` + `tools/audio`)
- **`tools/audio/lines_def.py`** define las voces y las líneas. El generador produce `sounds/line/<id>.ogg`, `sounds.json` (sin subtítulo vanilla), claves de lang en `es_ar` (copiadas a `es_*`) y `en_us`, y **`DialogueLines.java`** (id, hablante, duración, envolvente de 10 Hz para mover la mandíbula).
- **Voces TTS** (Kokoro, ya con el arreglo F14):

  | Voz | Base Kokoro | Ajuste | Cadena DSP |
  |---|---|---|---|
  | `operadora` | ef_dora | — | phone_band |
  | `pa` | ef_dora | velocidad 0,95 | pa_horn + slap |
  | `eco_robot` | em_alex | monótona, pitch cuantizado | bitcrush leve |
  | `demonio` | em_santa | −5 st | octava abajo + saturación + reverb grande |
  | `nena` | ef_dora | +4 st | banda limitada + reverb |
  | respaldos de imitación | em_alex | — | — |

- **Voces reales** (`tools/audio/voice_overrides/<lineId>.wav`): reemplazan al TTS y pasan por la misma cadena DSP. **`tools/audio/export_script.py`** genera un PDF o CSV por actor con las líneas, el contexto y la intención. **`tools/audio/gen_name.py <Nombre>`** genera las líneas con el nombre del creador (megafonía) en un resource pack.

  | Actor | Personajes | Líneas aprox. |
  |---|---|---|
  | Amiga joven | Clara | 8 |
  | Mujer mayor | Madre Remedios (lista), Graciela | 15 |
  | Hombre mayor | Cura, Cacho | 15 |
  | Mujer adulta | Marta | 12 |
  | Hombre adulto | Jorge | 10 |
  | Abuela real (ideal) | Nona | 12 |
  | Amigo | Tomi, Gonza | 15 |
  | Adolescente | Toti | 3 |
  | 3–4 voces femeninas | Coro: Ave María tradicional al derecho, tarareos (el DSP lo invierte) | — |

- **`DialogueService.say`:**
  - sonido atado a la entidad (`SoundSource.VOICE`, verificar con el probe) + `SubtitlePayload`;
  - una cola por hablante (los gritos interrumpen);
  - **`BarkPool`** reacciona a `SiteEvent`s (PropThrown → Jorge "es la humedad"; NpcHit → "¡ES MI MARIDO!").
- **`SubtitleHud`:**
  - abajo al centro **dentro de la columna 9:16**, 3 líneas como máximo;
  - el nombre del hablante en su color; estilos NORMAL, WHISPER (gris itálica), DEMON (rojo con temblor), PHONE, PA, STREAM y MIMIC ("[tu voz]");
  - flecha ◀/▶ cuando el hablante está fuera de pantalla;
  - activados por defecto.
- **`PhoneCalls.ring(player, callerId, lines...)`:** llamadas durante el caso, que se dibujan como burbujas en `PhoneScreen`.

### 3.9 Stream: chat, donaciones, espectadores y turnero (`com.deadline.stream`)
- **`LiveChatService`** por sitio:
  - estado: `mood` (CHILL, HYPE, SCARED, WARNING, EVIL), `viewers` y `streamActive` (cámara de Tomi prendida o forzada por un beat);
  - **reglas** cada 10 ticks:
    - ENTITY_BEHIND (`Spectral` a menos de 7 bloques detrás tuyo y fuera de vista) → ráfaga `warn_behind`;
    - DARK → *"prendé la linterna bro"*;
    - YELL → *"JAJAJA"*, *"CLIPEEN ESO"*;
    - SILENT de 45 s → *"¿se le cortó el mic?"*;
    - STUCK de 3 min → `hint_<objetivo>` (el chat es el sistema de pistas);
    - SNITCH (cada 12–20 s con la cámara prendida) → *"jaja está en la morgue"* + la posición a El Eco;
    - LOW_SANITY → mensajes con TU nombre;
    - DEATH → "F".
- **`Eco_666`:** en cada ráfaga de aviso, con probabilidad 0,3, manda un mensaje falso (dirección opuesta, "seguí la voz").
- **Pools** (`assets/deadline/livechat/es_ar.json`, se pueden reemplazar por resource pack):
  - usuarios vivos: `Gonza_Mod`, `graciela_mama`, `Juani_07`, `mate_amargo99`, `chori_master`, `lechuga_frita` y nombres de fans en `config/deadline/chat_fans.txt` (P1; solo suscriptores que pidieron aparecer);
  - muertos: `chiche_rulos`, `TITO_ELMAGO`, `pelusa_10`, `hugomol`, `tota1931` y 8 más;
  - mentiroso: `Eco_666`.
- **Red:** `ChatCuePayload(pool, n, spread)`, `ChatBatchPayload` (con guion), `StreamStatePayload(active, viewers, mood)`, `DonationPayload(user, amount, textKey, lineId)`.
- **`LiveChatHud`:** dentro de la columna 9:16, sobre el borde derecho. 5 líneas, fuente ×1,5, mensajes que entran deslizándose. Encabezado "● EN VIVO · 1.284 👁". Los nombres muertos pasan a gris después de `hospital.audiencia`.
- **Donaciones:** banner arriba al centro durante 3 s, `stream.donation` y la línea TTS robótica.
- **Emotes:** fuente bitmap original `deadline:emotes` (:skull:, :chori:, :mate:).
- **`TurneroBlockEntity`:** número que se dibuja con el texto del block entity (o un TextDisplay hijo). `turnero(n)` desde el guion.

### 3.10 Teléfono (extensiones de `PhoneScreen`)

| Función | Detalle | Prio |
|---|---|---|
| Atender con la voz | "Hablá para atender": la primera frase atiende y se etiqueta. Sin SVC se atiende con clic | P0 |
| Consentimiento | Pantalla real en el primer arranque (imitación sí/no, guardar entre sesiones sí/no) + llamada de consentimiento dentro de la historia | P0 |
| Avisos de La Operadora | Pool rotativo | P0 |
| Reseñas con estrellas | Al cerrar cada caso, con animación de estrellas y sonido | P0 |
| Pagos con inflación y retenciones | Línea de pago + saldo. La tienda remarca precios por caso | P0 |
| Notificación de la libreta | Con botón [FIRMAR] y sonido de reglazo | P0 |
| `ChatScreen` reutilizable | Chat familiar de Marta (con historial + mensaje en vivo), registro de llamadas del teléfono de Tomi (lista de llamadas) | P0 |
| Identificador con tu nombre | Llamada final desde "tu número" | P0 |
| Rueda de la spirit box | `SpiritBoxWheelScreen`: 5 preguntas por caso. La respuesta llega por la frase en pantalla existente + un susurro TTS, después de 1,5 s | P0 |
| Galería de fotos | Fotos prerenderizadas de la cámara de espíritus con marco "REC" y hora | P2 |
| Bestiario | Entradas de Sor Agonía ("Debilidad: la luz. Fortaleza: la puntualidad."), Ofelia, Choripán ("Peligro: 5/5. Ternura: 5/5."), El Eco ("Solo repite lo que escuchó. Escuchó mucho.") | P1 |

### 3.11 HUD y postproceso
- **Modos de layout:**
  - `normal`: el actual;
  - `shorts`: subtítulos, chat, sello de amonestación, objetivo y anillos de progreso **dentro de la columna central de 9:16**; el ECG y la cordura se achican a una esquina de esa columna.
- Comando: `/deadline hud layout <normal|shorts>`.
- **Ocultar automáticamente:** mientras habla un diálogo o hay una llamada, el objetivo se atenúa. En el apagón se oculta todo.
- **Capas nuevas:** `SubtitleHud`, `LiveChatHud`, `NoiseHud`, `ConductHud` (libreta "3/15" + sello animado de 3 s con el motivo), `ProgressRingHud` (mantener, cocinar, coser, rezar con el texto grande de la frase), `ChapterTitleHud` (campana + cartel).
- **`PostEffectStack`:** un shader combinado `vhs_nv` (VHS, visión nocturna e intensidad de locura como uniforms). Prioridad: apagón > cámara de Tomi > VHS (H) > locura.

### 3.12 Red (payloads nuevos en `ModNetworking`)

| Dir. | Payload | Campos |
|---|---|---|
| S2C | `SubtitlePayload` | lineId, speakerId, durationTicks, entityId, flags |
| S2C | `LoopPayload` | pos, soundId, on |
| S2C | `TakeEventPayload` | kind, id, note |
| S2C | `StreamStatePayload` / `ChatCuePayload` / `ChatBatchPayload` / `DonationPayload` | §3.9 |
| S2C | `ConductPayload` | count, reasonKey |
| S2C | `ChapterPayload` | n, titleKey, objectives[] |
| S2C | `FxPayload` (tipos nuevos) | BROWNOUT, NOISE, VOICE_REC, BLACKOUT_SILENCE, PROGRESS_RING, STITCH_TARGET |
| S2C | `PhoneScreenPayload` | CHAT / CALL_LOG / REVIEW / PAYMENT / CALLER_SELF |
| S2C | `DirectorStatePayload` (P1) | beats, estados, clips por jugador |
| C2S | `CuePayload`, `DirectorActionPayload` (P1) | Se verifica nivel de permiso 2 o más en el servidor |
| C2S | `ConsentPayload`, `SpiritBoxAskPayload`, `NameChoicePayload` | — |

### 3.13 Presupuestos de rendimiento (como mucho 3 ms extra por tick en el pico)
- **Director:** disparadores escalonados, como mucho 20 raycasts de `lookAt` por tick y 6 secuencias corriendo.
- **Luces:** 10 cambios por tick.
- **Voz:** todo fuera del hilo principal. Como mucho 4 reproducciones a la vez y 24 MB de buffers.
- **Entidades por sitio:** 6 NPC + Choripán + jefe + 13 de la Audiencia (sin IA) + props según §3.5.
- **Cliente:** como mucho 5 líneas de chat, 3 de subtítulos y un shader combinado.

### 3.14 CI
- **Smoke en servidor dedicado**, por caso:
  - construir el sitio con **tiempo medido**;
  - validar el script;
  - disparar cada beat con `force`;
  - correr 400 ticks;
  - verificar los presupuestos.
- **Smoke en cliente:** capturas de subtítulos, chat, libreta, props levitando, la mezcla de la posesión, las formas de Choripán, El Eco y la Audiencia con la cámara.
- **Voz:** `voice inject` con WAV de prueba para el selector y el DSP.

---

## 4. Funciones para grabar (priorizadas)

### 4.1 P0: imprescindibles antes de la primera sesión

| Función | Comandos / teclas | Para qué |
|---|---|---|
| Nombre del creador | `/deadline name <Nombre>` (+ `tools/audio/gen_name.py` para el audio) | Pizarrón, boletín, megafonía, chat, identificador final |
| Arrancar un caso o una llamada | `/deadline case start <colegio\|casa\|hospital> [cap]` · `/deadline case prebuild <caso>` · `/deadline call <caso\|final> [variante]` (variante 0 bloqueada por defecto) | Grabar en orden o por partes |
| Capítulos y checkpoints | `/deadline chapter <n>` (aplica el setup del capítulo y teletransporta) | Repetir desde cualquier punto |
| Beats | `/deadline beat list [filtro]` · `fire <id> [force]` · `reset <id\|all>` · `arm\|disarm <id>` | Repetir o forzar sustos para material de apoyo |
| Tomas | `/deadline take start\|slate\|mark [nota]\|reset` · **F10 = CLIP** | Reconstruir el sitio igual; CSV `deadline/takes/<fecha>.csv` (wall clock, ms desde el slate, tipo SLATE/BEAT/MIMIC/SCREAM/DEATH/CHAPTER/CLIP) + `chapters.txt` |
| Inmortalidad y muerte cinematográfica | `/deadline armor on\|off` | No se pierde la toma |
| Botón de pánico | `/deadline calm` | Borra entidades del caso, restaura la cordura, frena los efectos y prende las luces |
| HUD | `/deadline hud <all\|sanity\|objective\|subs\|chat\|libreta> on\|off` · `/deadline hud layout <normal\|shorts>` | HUD limpio y modo Shorts |
| Voz | `/deadline voice optin\|optout\|status\|test\|list\|play <tag\|id> [at <marker\|actor\|me>]\|pin <id> <tag>\|clear [all]` (dev: `inject`) | Revisar y fijar clips antes de los beats grandes |
| Stream | `/deadline chat say <usuario> <texto>` · `mood <m>` · `donate <usuario> <monto> <texto>` · `viewers <n>` | Chat escrito en vivo por el director |
| Protagonista | `/deadline star <jugador>` | Los sustos van al creador |
| Cues | `/deadline cue <1-9>` · **F6–F9** | Disparar en el momento justo |

### 4.2 P1: gran salto de calidad
- **Tablet del director** (K, solo operadores): pestaña Beats agrupada por capítulo con botón DISPARAR y estados; pestaña En vivo con la cordura, el ruido y la cantidad de clips de cada jugador, botones PLAY (ECO, CALL, GRITO) y BLOQUEAR VOZ. El amigo en espectador maneja los tiempos: el creador sabe *qué* pasa, pero no *cuándo*.
- **Modo coprotagonista Tomi:** `/deadline costar <jugador> tomi`.
- **Miniatura y poses:** `/deadline pose <actor> <pose>` · `/deadline freeze on|off` (congela entidades, props y partículas) · ojos con brillo extra · niebla ajustable `/deadline fog <dist>`.
- **Música apagable:** `/deadline music off`. Los efectos quedan y el editor pone su música.
- **Cámara de seguimiento:** `/deadline follow <jugador>`, para que el director grabe un segundo ángulo en tercera persona suave.

### 4.3 P2: si sobra tiempo
- Recorridos de cámara (`/deadline cam point add|play|clear`).
- Perillas de ritmo (`/deadline pace calm|normal|intense`, medidor de tensión y pool de ambiente).
- Modo sorpresa (con una semilla elige 3 de 8 sustos secundarios).
- Guía 9:16 visible solo para el director.
- Modo ensayo sin entidades.
- Bajar el ambiente cuando habla el creador.

### 4.4 Lista previa a la grabación (obligatoria)
1. **SVC en la configuración exacta de grabación** (un jugador con servidor integrado y `run_local_server=true`, o servidor con el amigo y el puerto UDP 24454 accesible). **Activación por voz.** `/deadline voice test` en verde.
2. **Auriculares** para el creador (evitan la contaminación y la realimentación).
3. **OBS:** juego y micrófono en **pistas separadas**. Confirmar que la voz imitada (canales SVC) entra en la pista del juego.
4. `/deadline name` y `gen_name.py` corridos. Resource pack de voces reales cargado.
5. **Buscar** "Tomi Dark", "TomiDarkTV", "Policlínico San Lázaro Villa Lucero" y "Colegio Santa Inés de la Vigilia" en YouTube, Twitch y Google Maps. Si existe algo real, cambiarlo antes de grabar.
6. Prebuild de los tres sitios y una pasada del director con `beat fire` de todos los `[CLIP]`.

### 4.5 Plan de sesiones

| Sesión | Quién | Qué | Salida |
|---|---|---|---|
| 0 | Director solo | Prueba de cues, material de apoyo (entidades congeladas), miniaturas, lista de bugs | Material de apoyo |
| 1 | Creador + director | Intro, base y caso 1 (se capturan `hola`, `nombre`, `acepto`, `presente`) | 60–90 min |
| 2 | Creador + director | Transición 1 y caso 2 (Choripán puede pedir 2 o 3 tomas) | ~90 min |
| 3 | Creador + director (+ amigo como Tomi) | Transición 2, caso 3 y final (El Eco usa la biblioteca de las sesiones 1 y 2) | ~90 min |

**Edición:** primero se ordena por marcadores (CSV), después se arma el esqueleto de 20 min de §1.2 y recién al final se pule. Momento de pedir la suscripción: después del caso 2 ("si te reíste con el chori, suscribite").

---

## 5. Backlog de construcción

### 5.1 Hitos (en orden)

| Hito | Contenido | Estimado |
|---|---|---|
| **H0. Cimientos y riesgos** | Día del probe; F1 a F15; access widener; `SliceBuilder` + marcadores + `SiteState`; **prueba de SVC en la configuración real (el día 1)**; arreglo del TTS | 7–9 días |
| **H1. Director, diálogo y tomas** | Director lite, takes y CSV, `DialogueService` + subtítulos + generador de líneas, capítulos y objetivos, comandos P0 | 8–10 días |
| **H2. Prueba de grabación del caso 2** | Base de la casa con kit, Marta y Jorge (rig humano), **Choripán perro → demonio → choripán bendito**, núcleo del poltergeist (mate, termo, sillas, platos), la llegada de Jorge. **Se graba una prueba** | 12–15 días |
| **H3. Colegio completo** | Sitio y kit, monja rehecha, alumnas, escucha y ruido, libreta, pizarrón, prendo/apago, teléfono con voz, Gran Silencio, Hora Muerta, Maitines | 14–17 días |
| **H4. Casa completa** | Lucía con el dilema, chancleta y Nona, puntadas, desayuno, el chat familiar, los 2 usos de voz | 8–10 días |
| **H5. Hospital completo** | Sitio y kit, cámara de Tomi, chat y donaciones, Audiencia, Repetición, ascensor, morgue, Tomi, El Eco, jefe y apagón | 15–18 días |
| **H6. Base, final y pulido** | Base y estante, llamada final, reseñas y pagos, voces reales integradas, capturas en CI, ensayo general | 6–8 días |

(Total unos 70–85 días de agente. El **arte es el camino crítico**: los modelos corren en paralelo desde H0.)

### 5.2 (a) Modelos y texturas

| ID | Tarea | Tam. | Prio |
|---|---|---|---|
| A01 | **Sor Agonía**: terminar el pulido + poses (`conduct`, `sit`, `ceiling`, `blow`, `wet`, `kneel_wall`, `reveal`, `burn`) + campanita y llaves + plano `face_crack` | M | P0 |
| A02 | **Alumna**: rig de nena + 4 peinados (Paloma reconocible) + `freed` + poses | L | P0 |
| A03 | **Madre Remedios** (unos 45 cubos, 3 poses) | M | P1 |
| A04 | **Clara liberada** (retextura del Ánima) | S | P0 |
| A05 | **Ofelia**: hilo cortado + variante `sewn` | S | P0 |
| A06 | **Lucía normal** (textura + suéter rojo) sobre el modelo de la Poseída | S | P0 |
| A07 | **Choripán perro**: terminar (en proceso) + chapita legible + pose `bipedal_180` | M | P0 |
| A08 | **Choripán demonio**: terminar (en proceso) + exportar eslabones para la cadena + poses `unspool/run/fetch_drop/beg/lunge/catch/vomit/retract` | L | P0 |
| A09 | **Rig humano base** `ent_humano.py` (cara de 14×14 o más, mandíbula, manos) | M | P0 |
| A10 | Marta | S | P0 |
| A11 | Jorge (+ textura poseído, delantal) | M | P0 |
| A12 | Nona (+ poseída, dentadura flotante, rodete suelto, andador, mecedora) | L | P0 |
| A13 | Toti | S | P1 |
| A14 | **El Eco** | L | P0 |
| A15 | Tomi (+ poses de mímica y en el cajón) | M | P0 |
| A16 | Audiencia: base + 5 variantes (Chiche, Tito, Pelusa, Hugo, Tota) | M | P0 |
| A17 | Cacho (sepia translúcido) | M | P1 |
| A18 | Retratos de jumpscare: monja pegada al vidrio, Ofelia en el último giro, boca en flor de Choripán, Nona con la dentadura, El Eco (`portraits.py`) | M | P0 |
| A19 | Avatares del teléfono: Operadora, Hna. Clara, Marta, Graciela, Gonza, "vos" | S | P0 |
| A20 | Modelos de props (ItemDisplay): mate, termo, plato, cuchillo, regla, chorizo, choripán, chancleta, teléfono de baquelita, teléfono de pared con auricular, celular de Tomi, cámara de Tomi, 3 muñecas de estante, ovillo | M | P0 |
| A21 | Fuentes: `chalk` (P0), `blood` (P1), `emotes` (P0) | S | P0/P1 |
| A22 | Pinturas: "Coro 1984" (3 estados, 64 px/bloque), retrato de la Madre (ojos abiertos/cerrados), foto "Nélida y Ofelia 1960", miniatura de Tomi y "SE BUSCA: TOMI" | M | P1 |
| A23 | **Kit colegio** (`colegio_*`): muros de revoque, damero, aula (pizarrón, silla escolar, pupitre), capilla (bancos, confesionario, atril, velas fixture), dormitorio (cama, bulto), cripta, faroles fixture | L | P0 |
| A24 | **Kit casa** (`casa_*`): chalet de los 50, cocina 70s, TV de tubo, mecedora, altar, parrilla, cucha, pelopincho, placard, sillas, fixtures | L | P0 |
| A25 | **Kit hospital** (`hosp_*`): linóleo, zócalo verde, tubo fluorescente fixture, cajón de morgue, conmutador, teléfono de pared, turnero, ring light, silla gamer, cabina de ascensor, cartel de salida | L | P0 |
| A26 | Kit base (monoambiente, estante de trofeos) | S | P0 |
| A27 | Íconos de los ítems nuevos | S | P0 |

### 5.3 (b) Sitios y construcción

| ID | Tarea | Tam. | Prio |
|---|---|---|---|
| B01 | **Base** `BaseSite` + dimensión `deadline:base` + marcadores del estante y de la puerta | M | P0 |
| B02 | **Colegio** `ColegioSite` (reemplaza a `ConventSite`): unas 13 salas, cripta, cuarto espejo sellado, exterior, marcadores y grupos de luz | L | P0 |
| B03 | **Casa Morales** (reconstrucción de `MoralesHouseSite`): casa, patio, sótano, cuarto del 61, marcadores | L | P0 |
| B04 | **Hospital** `HospitalSite`: columna lineal, cabinas dobles del ascensor, −3, marcadores de teléfonos y parlantes | L | P0 |
| B05 | Dimensiones: renombre `caso_colegio`, agua de la casa, niebla del hospital, `base` | S | P0 |
| B06 | Escenas de maqueta (`tools/blocks/scenes`) de las salas clave para revisar el arte de noche con linterna | M | P1 |

### 5.4 (c) Sistemas Java

| ID | Tarea | Tam. | Prio |
|---|---|---|---|
| C01 | Día del probe (nombres Mojang de Display/TextDisplay/Style font/sonido de entidad/`DoorBlock#setOpen`/`setCameraEntity`) | S | P0 |
| C02 | Access widener / mixins comunes de Display | S | P0 |
| C03 | F1: renderers reales de las criaturas existentes | M | P0 |
| C04 | F4 `CaseType` + `BASE` | S | P0 |
| C05 | F3 capítulos + `ObjectiveChecklist` | M | P0 |
| C06 | F2 muerte y checkpoint + inmortalidad | S | P0 |
| C07 | `SiteBuilder` con marcadores y seed + `SliceBuilder` + `restartSite` + prebuild | M | P0 |
| C08 | F13 `BuildProtection` | S | P0 |
| C09 | **Director lite** + comandos beat/cue/director + validación en CI | L | P0 |
| C10 | `TakeService` + `ClientTakeLog` + slate + F10 | S | P0 |
| C11 | `DialogueService` + `Speaker` + `BarkPool` + `PhoneCalls` | M | P0 |
| C12 | **Base de voz SVC** (plugin, grabador, segmentación, eventos, gradle, `-PnoVoicechat`) | L | P0 |
| C13 | **Reproducción de imitación** (selector, programador, cadena DSP, emisores) | L | P0 |
| C14 | `VoiceStore` (fijados en disco) + calibración + ventanas de etiqueta + comandos de voz + inject | M | P0 |
| C15 | `NoiseMeter` + modos + `HearingGoal` | M | P0 |
| C16 | `Spectral` + refactor de herramientas | M | P0 |
| C17 | F6 cono de la linterna + zonas selladas | S | P0 |
| C18 | Núcleo del poltergeist: `PropManager`, `Motion`, `PropCollision`, presupuestos | L | P0 |
| C19 | `DoorFx` / `DoorLocks` + `LightGroups` (fixtures con LEVEL, patrones) | M | P0 |
| C20 | `WallWriter` | S | P0 |
| C21 | `UnseenSwap` + acento al descubrir | M | P0 |
| C22 | **Rehacer `MonjaEntity`** (hitbox, oído, retroceso por luz, corte de camino en el borde, soplido, campanita, persecución con elástico, modos guionados, límites de teletransporte) | L | P0 |
| C23 | `AlumnaEntity` | M | P0 |
| C24 | `ConductTracker` (amonestaciones, compartido por los 3 casos) | S | P0 |
| C25 | Mecánicas del colegio: lección, Cuarto del Silencio, oración, agua de la canilla, regla, guion del espejo | M | P0 |
| C26 | `DoppelgangerEntity` MIRROR | M | P1 |
| C27 | `FamilyNpcEntity` + variantes + charla + bark al golpearlos | M | P0 |
| C28 | `PossessionComponent` + `DemonWisp` + `ActorSwap` | M | P0 |
| C29 | `ChoripanEntity` (formas, metas, cebo, sal, pedir, atrapar) | L | P0 |
| C30 | `ChoripanRenderer` en cadena (historial, ancla, culling) | M | P0 |
| C31 | Cadena del choripán: recetas de datos + `ChoripanBenditoEntity` + `CookingSpot` en el círculo de sal | S | P0 |
| C32 | Verbo sal de Jorge + cuchillos orbitando y apuntando | S | P0 |
| C33 | Dilema de las muñecas + purificación + secuencia de la chancleta y la Nona | M | P0 |
| C34 | Jefa Nona: mecedora flotante + puntadas | M | P0 |
| C35 | `YarnWeb` + pantalla del nombre | M | P1 |
| C36 | Rueda de la spirit box (tablas por caso) | S | P0 |
| C37 | `LiveChatService` + pools + reglas + `Eco_666` + donaciones + espectadores | M | P0 |
| C38 | `StreamCameraItem` (estado en vivo, delación, VOD, visibilidad de la Audiencia, texto IR) | M | P0 |
| C39 | Turnero (block entity + ticket) | S | P0 |
| C40 | Ascensor (cabinas dobles + teletransporte + panel) | S | P0 |
| C41 | Cajones de la morgue + escritura en el vidrio | S | P0 |
| C42 | **`EcoEntity`** (salir de los teléfonos, señuelos, orejitas, caza, agarre, bengala y aturdimiento, `husk`) | L | P0 |
| C43 | Mantener para finalizar + apagón global | S | P0 |
| C44 | `AudienciaEntity` (colocación + compuerta de visibilidad en el cliente) | S | P0 |
| C45 | `TomiEntity` (cajón, mímica, seguimiento, voz recuperada) | S | P0 |
| C46 | `CachoEntity` + intercambio del ítem | S | P1 |
| C47 | Modo coprotagonista (MUTE + clips del amigo) | M | P1 |
| C48 | Robo de voz REDIRECT al agarrar | S | P1 |
| C49 | Teléfono: atender con voz, consentimiento, reseñas, pagos, inflación en la tienda, libreta, identificador con tu nombre, avisos legales | M | P0 |
| C50 | Guion de la base + secuencia final + trofeos persistentes | M | P0 |
| C51 | F15 tabla de cordura por caso | S | P0 |
| C52 | F10 `PostEffectStack` + shader `vhs_nv` | M | P0 |
| C53 | Tablet del director + `DirectorActionPayload` | M | P1 |
| C54 | Pose, freeze, niebla, seguimiento | M | P1 |
| C55 | Recorridos de cámara, ritmo, tensión, ambiente, modo sorpresa, galería de fotos | L | P2 |
| C56 | Extensión del smoke test en CI (sitios con tiempo medido, todos los beats forzados, presupuestos, capturas) | M | P0 |

### 5.5 (d) Sonidos y voces

| ID | Tarea | Tam. | Prio |
|---|---|---|---|
| D01 | F14: Kokoro `es-419` + sheísmo + prueba de escucha | S | P0 |
| D02 | `lines_def.py` + generador (sounds.json, lang, `DialogueLines.java`, envolventes) | M | P0 |
| D03 | Pipeline de voces reales + `export_script.py` + `gen_name.py` | S | P0 |
| D04 | **Grabación de voces reales** (tarea del dueño, con el guion de D03; ver la tabla de §3.8) | — | P0 |
| D05 | Sonidos globales y del teléfono (timbre de las 3:33, avisos, reseña, caja, libreta, voces de La Operadora) | S | P0 |
| D06 | Sonidos del colegio (§2.1l) | M | P0 |
| D07 | Coro (grabación real invertida o respaldo lo-fi) | M | P0 |
| D08 | Sonidos de la casa (§2.2l) | M | P0 |
| D09 | Cumbia original (loop, corte, cajita de música) | S | P0 |
| D10 | Sonidos del hospital (§2.3l), jingle de donación y preset de voz robótica de El Eco | M | P0 |
| D11 | Respaldos de imitación sin SVC + espacios en el resource pack | S | P0 |
| D12 | Stingers musicales (apagables) | S | P1 |

### 5.6 (e) Interfaz

| ID | Tarea | Tam. | Prio |
|---|---|---|---|
| E01 | `SubtitleHud` (estilos, columna 9:16, flechas) | S | P0 |
| E02 | Sistema de layout del HUD (`normal`/`shorts`) + interruptores | S | P0 |
| E03 | HUD de objetivos (checklist) + `ChapterTitleHud` | S | P0 |
| E04 | `ConductHud` (libreta + sello) | S | P0 |
| E05 | `NoiseHud` ("TE ESCUCHA") + indicador "● VOZ" | S | P0 |
| E06 | `LiveChatHud` + banner de donación + contador + marco EN VIVO | M | P0 |
| E07 | Pantallas del teléfono (atender con voz, consentimiento, reseñas, pagos, identificador, registro de llamadas, `ChatScreen`) | M | P0 |
| E08 | `SpiritBoxWheelScreen` | S | P0 |
| E09 | `ProgressRingHud` (mantener, cocinar, coser, frases de oración) + anillo de puntada | S | P0 |
| E10 | Shader `vhs_nv` + capa de apagón | M | P0 |
| E11 | Pantalla de la tablet del director | M | P1 |
| E12 | Entradas del bestiario | S | P1 |
| E13 | Guía 9:16 para el director | S | P2 |

### 5.7 Qué cortar primero si falta tiempo (en este orden)
1. **Todo lo P2** (recorridos de cámara, ritmo y tensión, modo sorpresa, galería, guía 9:16, camilla, sala con un monitor).
2. **Toti** (el escondite en el ropero queda sin el gag).
3. **Tela de lana y pantalla del nombre** (la Nona flota, tormenta de platos y puntadas).
4. **Modelo de la Madre Remedios** (queda su voz; en el remate, las nenas callan al escritorio vacío donde la pluma escribe sola "Ajá.").
5. **Doppelgänger del espejo** (queda el respaldo: la monja en el cuarto espejo sellado).
6. **Cacho** (el choripán y la llave van al cajón 7 y el gag se pierde).
7. **Cascada de puertas** y **Madre como alucinación**.
8. **Robo de voz al agarrar** y **modo coprotagonista** (el amigo hace la voz de Tomi solo como grabación).
9. **Variantes de la Audiencia** (Chiche + genéricos).
10. **Kits completos**: solo los bloques héroe se hacen con kit (pizarrón, confesionario, parrilla, cucha, conmutador, cajones, turnero, ring light) y el resto se hace con la paleta vanilla del documento.

**Nunca se corta:** el Director con beats, capítulos y tomas · la muerte con checkpoint · los tres jefes con su verbo · la transformación de Choripán y el choripán bendito · la captura de voz (`hola`/`acepto`) y la llamada final · el chat en vivo · la Repetición · Finalizar transmisión con el apagón · los subtítulos.

---

## 6. Preguntas abiertas para el dueño (cada una con un default para no frenar la construcción)

| # | Pregunta | Default si no hay respuesta |
|---|---|---|
| 1 | Nombre de exorcista y ¿"monotributista"? ¿Facecam? | Nombre del canal; sí al monotributista; facecam opcional |
| 2 | ¿Juega un amigo? ¿Como director invisible, como Tomi o los dos? | Director en las sesiones 1 y 2, Tomi en la 3 |
| 3 | ¿Quién graba las voces reales (Clara, Madre, cura, Marta, Jorge, Nona, Tomi, Graciela, Cacho, Gonza)? | TTS es-419 con DSP hasta que haya grabaciones |
| 4 | ¿"SOY DE TEMPERLEY" en la spirit box (fútbol)? | Activado, con la opción de apagarlo |
| 5 | ¿Final abierto ("toc, toc, toc") o redondo? | Abierto (gancho para la parte 2) |
| 6 | Tope de gore | Sangre estilizada, sin desmembramientos; la bestia da asco, no es gore |
| 7 | ¿Guardar los clips de voz en disco entre sesiones? | Sí, solo los fijados, con opt-in y `/deadline voice clear` |
