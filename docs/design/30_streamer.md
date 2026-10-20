# CASO 3: "EN VIVO" · Policlínico San Lázaro

*(case key `hospital` · dimensión `deadline:caso_hospital` · boss `ojo` (Dr. Mendizábal) · ancla `celular_lauti` · antagonista secundario `lauti` · peligro ★★★★ · pago $1.600)*

> ## **"No está vivo. Está EN VIVO."**
> (tagline del caso y texto para la miniatura)

---

## 0. El caso en una página

**Qué es.** Un streamer argentino entró a un hospital abandonado a hacer "24 horas" en vivo. Hace 37 días que la transmisión no se corta. Te llama su mamá para que vayas a buscarlo. Su mamá murió en 2019.

**Las 3 reglas del caso.** Son pocas y claras para que el público las aprenda. Conviene ponerlas en pantalla en la edición.
1. **No mires a Lauti.** Cada mirada es una vista, y con vistas se acerca (es una "weeping angel" invertida: la muñeca se mueve cuando NO la mirás y Lauti se mueve cuando SÍ).
2. **No te quedes en la luz.** El Doctor solo puede existir donde hay luz o donde una cámara te ve. Es el espejo de la Monja, que solo se mueve en la oscuridad.
3. **El chat miente, menos uno.** Cuando `nn_13` escribe "atrás tuyo", es verdad.

**Tema.** Mirar no es lo mismo que recordar. El monstruo vive de vistas. El caso funciona como meta-comentario sobre el medio del propio creador: el clímax es un youtuber apretando **"Finalizar transmisión"** delante de 1.990 espectadores muertos.

**Lugar en el video:** **último caso.** Tiene el giro más fuerte, el final más emotivo y el cierre más natural para un video de YouTube.

**Reuso de código.** La lógica `isWatchedBy()` de `HauntEntity`/`MunecaEntity` sirve para Lauti invirtiendo la condición. El sistema de ancla/boss, la cordura, `Fx` (shake/flash/static/title/jumpscare/soundAt), el shader VHS y todas las herramientas existentes se usan tal cual. Lo nuevo se describe en las secciones 7 a 9.

---

## 1. Logline e historia

### Logline
*"LAUTI EXTREMO" entró al Policlínico San Lázaro a hacer "24 HS EN EL HOSPITAL MÁS EMBRUJADO DE ARGENTINA (REAL) (NO FAKE)". Hace 37 días que el directo sigue: no habla, no come, no corta. Hay 1.989 espectadores que nadie sabe de dónde salen y que no dejan de mirar. Su mamá te pide que lo traigas de vuelta. Su mamá está muerta.*

### Cronología (todo ficticio: ni el hospital, ni el pueblo, ni el streamer existen)

| Fecha | Qué pasó |
|---|---|
| **1953** | Se inaugura el **Policlínico San Lázaro** en **Villa Lucero** (partido ficticio de General Arriaga, prov. de Buenos Aires). Es un monoblock racionalista blanco de 3 pisos con tanque de agua y chimenea, "el hospital más moderno del sur del conurbano". |
| **1971** | Abre el **Pabellón C** (psiquiatría), en el 2º piso del ala oeste. |
| **3-III-1974** | El **Dr. Aurelio Mendizábal** (n. 1928), director del Pabellón C, instala el **Sistema de Observación Continua (SOC)**: 32 cámaras de circuito cerrado, una Sala de Observación en el 2º piso y una central de grabación U-matic en el Subsuelo 2. Su teoría era que la locura es el alma "escurriéndose" cuando nadie la mira. Su lema: ***"Mientras alguien mire, nadie se va."*** Las luces del C quedan prendidas 24 horas, hay una cámara en cada celda y el pizarrón de actividades dice "Observación" todos los días. Los pacientes le dicen **"el Ojo"**. |
| **1974–1989** | Los pacientes del C dejan de dormir. A los que mueren se los filma en la morgue "para que no se vayan". Mendizábal se muda a la central y escribe: "Los ojos me sobran". |
| **9-VII-1989, 23:58** | Es el Día de la Independencia, en plena hiperinflación. La compañía eléctrica corta el suministro por deuda y, por primera vez en 15 años, el Pabellón C queda a oscuras. |
| **10-VII-1989, amanecer** | Encuentran a los **13 pacientes del C** sentados en la Sala de Día, frente al televisor apagado, con los ojos abiertos y muertos. **Mendizábal desaparece.** El sereno, **Ernesto "Cacho" Funes**, muere de un infarto en su garita con el mate en la mano. Nadie fue a relevarlo y nunca lo anotaron en el libro de la morgue. Ese mismo día el hospital cierra "por falta de fondos". El libro de la morgue cierra con: **TOTAL 1953–1989: 1.988.** |
| **1990–2026** | Nace la leyenda urbana: *"si prendés una cámara en el San Lázaro, alguien te mira del otro lado"*. Graffitis, chicos del barrio, una ermita roja en la reja. |
| **2019** | Muere **Norma Benítez**, mamá de Lautaro. Era su primera espectadora y comentaba en todos los directos "abrigate, nene", "comé algo, Lauti". |
| **13-IX-2026, 23:00** | **Lautaro "LAUTI EXTREMO" Benítez** (24 años, de Lanús, 380 mil seguidores, baneado dos veces, **debe un sorteo hace 8 meses**) arranca el directo. Lo modera desde su casa en Banfield su amigo de la secundaria, **Gonza** (`Gonza_Mod`). |
| **14-IX-2026, 03:31** | En la Sala de Observación, Lauti engancha su capturadora a la consola del SOC "para que el chat vea las cámaras del 74". **Las cámaras prenden sin electricidad.** "¡Chat, ¿se ve?! ¡ANDAN SIN LUZ!" |
| **03:33** | El contador salta de 412 a **1.989 espectadores**. El circuito cerrado ya no está cerrado: los muertos del San Lázaro encontraron una ventana y el Ojo encontró 1.989 ojos nuevos. Lauti se esconde en la Sala 14 y escribe su última página. |
| **04:02** | "El ascensor anda. No tiene luz y anda. Me está llamando." Lauti baja al Subsuelo 2 y **muere sentado en la silla de la central**, de cara a su celular. El directo sigue: lo que camina por los pasillos es **lo que el chat quiere ver**. |
| **20-X-2026 (hoy)** | Día 37. Te llama Norma. |

**Por qué 1.989 espectadores:** son los 1.988 muertos del hospital más **una** que está ahí por amor: Norma. Cuando el hospital te "interna", el contador pasa a **1.990**, que es el número que te da el turnero de la recepción. Todo cierra.

### Lo que el jugador descubre, en tres capas
1. **Superficie (llamada + exterior + Guardia):** un streamer desaparecido y un directo que no se corta. ¿Es fake? Gonza y los trolls del chat dudan. Es el tono de humor.
2. **Giro 1, a la mitad (Sala 14):** quien te llamó **murió en 2019**. Encontrás la foto de Norma ("1968–2019"), el registro de la llamada dice "sin número, 03:33" y en el chat aparece `MamaDeLauti`: *"perdón que no te dije, querido. Si te decía, no venías."* Opcional como lore general del mod: **DEAD LINE es una línea que los muertos pueden llamar.** Solo si no choca con los otros dos casos; si no, que quede como algo de este caso.
3. **Giro 2 (Pabellón C + cintas):** **el chat son los muertos del hospital.** Los usuarios coinciden con las pulseras de los pacientes y con el libro de la morgue. Lauti abrió el circuito. El hospital lo internó: ficha **C-14**, *"Motivo: necesidad patológica de ser mirado. Alta: NO."* Y hay una ficha **C-15 con tu nombre**: *"Ingreso: HOY. Motivo: vino a mirar."*
4. **Giro final (Subsuelo 2):** **Lauti está muerto desde la primera noche.** Su cuerpo está en la silla con los auriculares puestos y lo que te persigue es su "personaje", sostenido por las vistas. No hay rescate posible: **hay que cortar.** Sin nadie que lo mire, el monstruo es un viejito que llora. *"El monstruo nunca fue el que miraba. Era el miedo a que nadie mire."*

---

## 2. La llamada y el flujo de objetivos

### Avatar del llamador
**Norma B.**: mujer de unos 55 años, cárdigan lila, anteojos con cadenita, sonrisa cansada. La foto está apenas sobreexpuesta y desenfocada, como si fuera vieja. El marco del avatar es lila y en la segunda llamada parpadea con estática.

### Variantes (lang `deadline.case.hospital.caller.N` / `msg.N`)

**0 · "Norma B." (la que se usa en el video: `/deadline call hospital` fuerza la variante 0)**
> "Hola, perdón la hora. Soy Norma, la mamá de Lautaro... Lauti, el de los videos. Hace 37 días entró al Policlínico San Lázaro a hacer un directo y no salió más. La policía dice que es todo armado, para las visitas. Pero yo lo sigo mirando, todas las noches. El directo sigue. No come, no duerme, no corta. Vaya a buscarlo, por favor. Yo no puedo entrar ahí. **Ya no.**"

**1 · "Gonza_Mod"** (avatar: pibe con gorra y ojeras, pantalla iluminándole la cara)
> "Hola, ¿vos sos el de los fantasmas? Soy Gonza, modero el canal de Lauti Extremo. Hace 37 días que el stream sigue en vivo y no lo puedo cortar: no tengo permisos, la plataforma no contesta y Lauti no habla, solo mira a cámara. Hay 1.989 espectadores clavados y vivos somos como seis. Banneo gente y vuelve. Gente con nombres de viejos. Te pago lo que quieras. Bueno, lo que quieras no. Algo."

**2 · "LAUTI EXTREMO ● EN VIVO"** (avatar: su cara de miniatura, con glitch)
> "*(muchas notificaciones)* ...¿Hola? ¿Se escucha? Chat, saluden, tenemos invitado. Vení al San Lázaro, amigo. Traé cámara. Hay lugar. Hay un montón de lugar. Turno mil novecientos noventa."

### Flujo de etapas (HUD "objetivo" + pista en el teléfono)

| # | Objetivo (HUD) | Pista (teléfono) | Se completa cuando... | Notas |
|---|---|---|---|---|
| **E0** | Encontrá el auto de Lauti. | Seguí las balizas. | Llegás a 4 bloques del auto. | Se prende la radio de 1989 (B01). |
| **E1** | Entrá al Policlínico. | La puerta principal tiene cadena. La Guardia siempre está abierta. | Entrás a la Guardia. | Pasás por la garita vacía con el mate humeando. |
| **E2** | Encontrá el equipo de Lauti. | Un directo de 24 horas necesita batería. | Agarrás la **Cámara de Lauti** de su mochila. | Se desbloquean la app **EN VIVO** y el chat en el HUD. Primer mensaje de Gonza. |
| **E3** | Mirá el directo: averiguá dónde está Lauti. | Abrí EN VIVO (G). Lo que ve él, lo ves vos. | Abrís la vista POV una vez (B03) **y** llegás al Quirófano 2. | En la vista se ve el cartel "QUIRÓFANO 2". |
| **E4** | Subí al Pabellón C. | La llave del C no está en el tablero de enfermería. | Leés el papel del tablero: "Llave C: la tiene Cacho". | El office de enfermería está al lado del quirófano. |
| **E5** | Encontrá al sereno. | La garita, al lado de la Guardia. | Hablás con **Don Cacho**. | Te pide el choripán. |
| **E6** | Traele el choripán al sereno. | "Es la única heladera que enfría." ¿Cajón 7 o 14? | Le das el choripán y te da la **Llave del Pabellón C**. | La morgue está en el Subsuelo 1, por la escalera de servicio. |
| **E7** | Investigá el Pabellón C. | Prendé la cámara de Lauti en la Sala de Día. Contá cuántos son. | Leés la **ficha C-14** y entrás a la **Sala de Observación**. | La puerta del consultorio tiene candado: **1988**. |
| **E8** | Encontrá la Sala 14. | La cámara 14 muestra una sala que no está en el plano. Entre la 13 y la 15. | Rompés la pared de yeso y entrás. | **Giro 1.** Llave de bombero. |
| **E9** | Bajá al Subsuelo 2 por el hueco del ascensor. | Llave de bombero en la puerta del ascensor, 1er piso. **No mires para arriba.** | Llegás a la escotilla del fondo del pozo. | Secuencia del ascensor (B15). |
| **E10a** | Apagá las cámaras de la central (0/8). | El Doctor viaja por las cámaras. Sacale los ojos. | Quedan 6 de 8 cámaras destruidas o quemadas. | Boss, fase 1. |
| **E10b** | Purificá el celular de Lauti. | Agua bendita. Es lo que lo mantiene en vivo. | Ancla purificada. | Fase 2. |
| **E10c** | Debilitá al Doctor. | Solo puede estar en la luz. | Al Doctor le queda menos del 25% de vida. | Fase 3. |
| **E10d** | Finalizá la transmisión. | Mantené apretado. No sueltes. | Mantenés 5 segundos sobre el celular. | Fase 4, el apagón. |
| **E10e** | Atrapá al Doctor. | Frasco de Almas (o Libro de Rituales). | Captura o exorcismo. | |
| **E11** | Salí del hospital. | Acompañalos. | Cruzás la puerta principal. | Éxodo, final y vuelta a casa. |

---

## 3. La locación: Policlínico San Lázaro

**Escala.** Extensión total del sitio X −42..42, Z −44..36, Y −16..26, parecida al Convento (`clearAbove(42, 34)`). Origen (0,0,0) en el centro del umbral de la fachada principal (lado sur, Z=0). El edificio va de **X −30..30, Z 0..24**.
**Pisos:** Subsuelo 2 (SOC) piso y −16, aire −15..−9 · Subsuelo 1 piso y −7, aire −6..−2 · **PB** piso y −1, aire 0..4 · **1P** piso y 5, aire 6..10 · **2P** piso y 11, aire 12..16 · **Techo** y 17 (se camina en y 18).

### Paleta de materiales ("hospital argentino de los 50 abandonado")
- **Fachada:** mezcla de `calcite`, `diorite`, `tuff`, `light_gray_concrete` y chorreaduras de `light_gray_terracotta`. Ventanas en banda con `glass_pane`, al 40% faltantes o reemplazadas por `gray_stained_glass_pane`. Rejas `iron_bars` en todo el 2º piso oeste (Pabellón C).
- **Piso interior:** "linóleo" en damero de `white_concrete` y `light_gray_concrete`, con parches rotos de `gravel`, `coarse_dirt` y `tuff`.
- **Paredes:** zócalo de azulejo "verde hospital" de 2 bloques en `waxed_oxidized_cut_copper`, que es estable y no cambia. Arriba, pintura descascarada en `white_concrete`/`calcite` con manchas de `mushroom_stem`/`light_gray_terracotta`. Cielorraso de `smooth_stone_slab`.
- **Puertas:** `pale_oak_door` para las salas (pálidas y fantasmales), `iron_door` para el Pabellón C y la morgue, `birch_door` en la administración.
- **Decadencia:** `cobweb`, `pale_moss_carpet` y `pale_hanging_moss` colgando de balcones y cielorrasos rotos (**no** poner `creaking_heart`), sangre seca con el `BloodStainBlock` existente.
- **Mobiliario:** camas `white_bed` con barandas `iron_bars`; pies de suero de `iron_bars` + `lightning_rod` + `chain`; sillas de espera de `smooth_quartz_stairs`; mesas de `oak_fence` + `pressure_plate`; archivos de `barrel` + `chiseled_bookshelf`; mesas de autopsia de `smooth_stone_slab` sobre `iron_bars`.
- **Carteles y graffiti:** entidades **TextDisplay** (escala, color y sin fondo) para graffitis rojos/negros, pizarrones con tiza, carteles de salas y números de cajones. Dibujos, fotos, radiografías y afiches como **variantes de cuadro** data-driven (`painting_variant`) con texturas propias.

### EXTERIOR (Z −44..0)
- **Spawn:** (0, 0, −40), mirando a la fachada. Primer plano del video: niebla densa, la mole blanca del hospital y en el techo las letras **"POLICLÍNICO SAN LÁZARO"** (bloques de `white_concrete` de 3 de alto), con letras caídas: **"POLI LÍNICO SA  L ZARO"**. Las ilumina una sola luz roja que parpadea.
- **Reja perimetral** (Z −28): `iron_bars` rotas, portón con `chain`. Al lado, una **ermita**: velas, flores, latas de energizante como ofrenda, el cuadro "SE BUSCA: LAUTARO BENÍTEZ — Visto por última vez: EN VIVO" y banderitas rojas.
- **Graffitis** en el muro (TextDisplay): "VOLVÉ LAUTI", "**LAUTI PAGÁ EL SORTEO**", "FAKE", "acá murió el contenido", "NO ENTRES", "el ojo te mira".
- **Estacionamiento** (Z −26..−10): **el auto de Lauti** en (−8, 0, −18). Es rojo y destartalado, de `red_concrete` + `red_terracotta` + `glass_pane`, con la puerta abierta, una calcomanía "LX" (TextDisplay verde neón) y **balizas** (redstone lamps naranjas a los costados que parpadean con relé). En el asiento hay una lata de energizante por la mitad.
- **Bahía de ambulancias** (lado este, X 31..38, Z 2..12): ambulancia oxidada (`white_concrete` + franja `red_concrete`) con las puertas traseras abiertas y la camilla faltante. Puerta doble **"GUARDIA"** en el muro este.
- **Garita del sereno** (X 31..34, Z −3..0, 4×4): ventanita, un mini televisor (`monitor_crt` en "partido con estática"), silla, termo y mate (ItemDisplay) y una radio. Al principio está vacía y el mate humea (partícula de vapor).
- **Chimenea** de la sala de calderas (al norte) y **tanque de agua** sobre pilotes en el techo: la silueta clásica de hospital argentino.

### PLANTA BAJA (y 0..4)
```
 Z=24 ┌──────────┬────────┬─────┬───┬───┬────────────┬──────────┐
      │ CAPILLA  │ BAÑOS  │ESCAL│ASC│ASC│  DEPÓSITO  │ ESC.SERV │
      │(pila AB) │        │PPAL │ A │ B │(sillas de  │  → S1    │
      │          │        │     │   │   │  ruedas)   │          │
 Z=14 ├──────────┴────────┴─────┴───┴───┴────────────┴──────────┤
      │═════════════════════ PASILLO PB ════════════════════════│
 Z=12 ├──────────┬──────────┬─────────────────┬────┬────────────┤
      │CAFETERÍA │ ADMIN /  │ HALL RECEPCIÓN  │ RX │  GUARDIA   ├─ bahía
      │(menú en  │ ARCHIVO  │ (doble altura,  ├────┤ (mochila   │  ambulancias
      │australes)│          │  turnero)       │FARM│  de Lauti) │  + GARITA
 Z=0  └──────────┴──────────┴────[PUERTA]─────┴────┴────────────┘
     X=-30     -21        -9                  9   14          30
```
| Sala | Caja (X, Z) | Contenido clave |
|---|---|---|
| **Hall / Recepción** | −8..8, 1..11 (17×11), **doble altura** hasta el techo del 1P y con balcón alrededor | Mostrador (`smooth_stone` + `quartz_slab`), 3 filas de sillas, **turnero** encima del mostrador ("TURNO 13"), **reloj parado en 03:33**, directorio ("GUARDIA →, RAYOS X →, PABELLÓN C ↑ CLAUSURADO"), **cartelera** con recortes de diario y el afiche **"SE BUSCA: CHORIPÁN"** (guiño al caso 2), un TV de pared con estática y la puerta principal encadenada. Musgo pálido colgando del balcón. |
| **Pasillo PB** | −29..29, 12..13 | Carteles verdes de SALIDA (emisivos), una silla de ruedas sola. |
| **Escalera principal** | −6..−2, 14..22 | Sube al 1P y al 2P. La bajada al S1 está **derrumbada** (escombro de `gravel`/`cobblestone` y el cartel "CLAUSURADA"); después del final aparece despejada. |
| **Ascensores A/B** | A: 2..4 × 15..17 · B: 6..8 × 15..17 | A es el pozo jugable (y −15..16). B está soldado, es decorado. |
| **Guardia** | 14..29, 1..11 | 4 boxes con "cortinas" de `white_stained_glass_pane` + telarañas, 4 camillas, **carro de paro** con el **Desfibrilador**, **monitor cardíaco** (B04) y **la mochila de Lauti**: Cámara de Lauti, powerbank, energizante y **Libreta pág. 1**. Un farol de camping prendido (luz 12): la primera "zona segura". |
| **Rayos X** | 9..13, 1..6 | Puerta de plomo (`iron_door`), **negatoscopios** con 3 radiografías: una **con un celular dentro de las costillas** y otra con **un cráneo con lente de cámara**. |
| **Farmacia** | 9..13, 7..11 | Ventanilla con rejas, cartel **"NO HAY"**, 2 Pastillas, nota: "No hay ibuprofeno. No hay nada. Vaya a la de enfrente." |
| **Administración / Archivo** | −20..−10, 1..11 | **Memo 114/74 del SOC**, circular "PROHIBIDO APAGAR LAS LUCES DEL PABELLÓN C", planilla de sueldos ("Sereno: Ernesto 'Cacho' Funes") y una máquina de escribir (ItemDisplay). |
| **Cafetería** | −29..−21, 1..11 | Mesas, **pizarrón del menú en australes** (humor), almanaque de julio de 1989, una pava en la hornalla. |
| **Capilla** | −29..−22, 14..22 | **Pila de agua bendita**: recarga el Agua Bendita (2 cargas por visita). Bancos, crucifijo, velas. **Santuario**: ninguna entidad entra, es el respiro de la partida. |
| **Depósito** | 10..23, 14..23 | Sillas de ruedas apiladas que a veces "giran" (poltergeist menor). |
| **Escalera de servicio** | 25..29, 16..22 | Única vía al Subsuelo 1 (morgue). |

### PRIMER PISO: Clínica y Quirófanos (y 6..10)
```
 Z=24 ┌───────┬───────┬────────┬───────┬─────┬───────┬─────────────┬───────────┐
      │SALA 12│SALA 13│SALA 14 │SALA 15│ESCAL│ASC A/B│ QUIRÓFANO 2 │QUIRÓFANO 1│
      │       │       │(OCULTA)│       │     │       │  + GALERÍA  │ clausurado│
 Z=15 ├───────┴───────┴─[YESO]─┴───────┴─────┴───────┴─────────────┴───────────┤
      │═══ PASILLO LARGO 3×59 · tubo #4 parpadea · camilla al fondo (este) ═════│
 Z=12 ├───────┬───────┬───────┬──────────────────────────┬──────┬──────┬──────┤
      │SALA 1 │SALA 2 │SALA 3 │ BALCÓN SOBRE EL HALL     │SALA 4│SALA 5│SALA 6│
      │       │       │       │ + OFFICE DE ENFERMERÍA   │      │      │      │
 Z=0  └───────┴───────┴───────┴──────────────────────────┴──────┴──────┴──────┘
```
| Sala | Caja | Contenido clave |
|---|---|---|
| **Pasillo largo** | −29..29, 12..14 (**3×59**) | El set principal: tomas largas, la persecución de la camilla, Lauti al fondo. 10 tubos fluorescentes cada 6 bloques: **solo el #4 funciona, y parpadea**. La camilla queda en el extremo este y la silla de ruedas en X −20. **Plano de evacuación** en la pared ("Usted está aquí"): muestra la 13 pegada a la 15, **sin la 14** (pista). |
| **Salas 1–6** (internación) | lado sur, unos 7×10 cada una | 2 a 4 camas. En la **Sala 3**, una sábana con forma de cuerpo **respira** (BlockDisplay que escala). Pulseras de pacientes escondidas bajo las camas. |
| **Balcón + Office de enfermería** | −8..8, 1..11 (anillo de 3) + mostrador −5..5, 9..11 | **Tablero de llaves** (falta la C: "Llave C: la tiene Cacho. NO LA PIERDAS CACHO. — Enf. Ruiz"), **llamador de enfermería** de 15 lamparitas (salas 1–15; las 7–11 "están en el ala este del 2º, colapsada") y el **libro de guardia** de la enfermera. Desde la baranda se ve el hall de abajo: Lauti se asoma por aquí (B-sistémico). |
| **Salas 12, 13, 15** | −29..−25, −24..−20, −14..−9 × 15..24 | Internación; la 13 con dibujos infantiles en la pared. |
| **SALA 14 (oculta)** | −19..−15 × 15..24 | Tapiada con **pared de yeso fresco** (bloque `pared_yeso`, se rompe en 3 golpes). Del otro lado, con UV, se ven **las manos de Lauti**. Es el campamento de Lauti: bolsa de dormir, envoltorios de alfajores, un ring light chico apagado, **la foto de Norma** con un moño lila y una vela, **Libreta pág. 3**, **Llave de bombero** y en la pared, con marcador: **"SI ALGUIEN VE ESTO: NO MIRES EL CHAT"**. |
| **Quirófano 2** | 10..21, 15..21 + **Galería** 10..21, 22..24 | Mesa de operaciones, **lámpara quirúrgica** grande (anillo de bloques `lámpara_quirúrgica` controlable), bandeja de instrumental y una mancha de sangre con forma de persona. **El ring light de Lauti** (luz 15) apunta a la mesa: Lauti hizo su "bit del cirujano". **Libreta pág. 2.** Al norte, detrás de un vidrio, la **galería de observación**: 2 gradas de 7 asientos, sin acceso. Ahí se sienta la Audiencia (B05). |
| **Quirófano 1** | 23..29, 15..24 | Clausurado con tablas cruzadas y "NO PASAR". Desde adentro golpean. |

### SEGUNDO PISO: Pabellón C + ala este colapsada (y 12..16)
```
 Z=24 ┌──────────────────────┬───────────┬──────────┬─────┬─────────────────────┐
      │    SALA DE DÍA       │CONSULTORIO│ SALA DE  │ESCAL│                     │
      │ (15 sillas → TV)     │MENDIZÁBAL │OBSERVAC. │     │  ALA ESTE COLAPSADA │
      │                      │ [1988]    │ (12 CRT) │     │  (techo abierto,    │
 Z=15 ├──────────────────────┴───────────┴──────────┤     │   musgo pálido,     │
      │═══ PASILLO C · TODO ILUMINADO 24 hs ═══════╡REJA │   agujeros al 1P,   │
 Z=11 ├────┬────┬────┬────┬────┬────┬────┬────┬────┤     │   escalera al techo)│
      │C-01│C-02│C-03│C-04│C-05│C-06│C-07│C-08│BAÑO│     │                     │
 Z=0  └────┴────┴────┴────┴────┴────┴────┴────┴────┴─────┴─────────────────────┘
```
**Inversión visual clave:** el Pabellón C es **el único lugar del hospital con todas las luces prendidas**, con tubos a luz 15 que zumban. Es blanco, estéril y enceguecedor: el territorio del Doctor. A simple vista no hay nadie. Con la cámara de Lauti, el pasillo está **lleno de gente parada**.

| Sala | Caja | Contenido clave |
|---|---|---|
| **Reja del C** | X −1, Z 12..14 | Reja de `iron_bars` + `iron_door` con cerradura. Cartel "PABELLÓN C — CLAUSURADO 10/7/1989". |
| **Celdas C-01..C-08** | lado sur, 3×4 interior cada una | Acolchadas (`white_wool`), puerta con mirilla y **una cámara CCTV sobre cada puerta, adentro**. Rayones de TextDisplay: "NO ME MIRES", "APAGÁ", "5.479" (días tachados). **C-08** es la celda de "internación" a la que te manda el Doctor si te atrapa. |
| **Baño del C** | −3..−1 aprox., lado sur | **Secreto del espejo** (ver Secretos). |
| **Sala de Día** | −29..−16, 15..24 (14×10) | **15 sillas** en 3 filas de 5, mirando un **televisor en un estante alto** (pared norte). Rejas en las ventanas. Pizarrón **ACTIVIDADES** y revistas de crucigramas de 1989. En la silla 14, cinta de papel: **"LAUTI ❤"**. En la **silla 15**, cinta con **el nombre del jugador** (TextDisplay con `player.getName()`). |
| **Consultorio Mendizábal** | −15..−9, 15..22 | Puerta con **candado de combinación (1988)** y el cartel "Dr. A. Mendizábal — Pase sin golpear. Ya lo estoy mirando." Escritorio, **Diario del Dr.**, diploma, **pared de polaroids de ojos** (cuadro 3×2), frasco de formol vacío con la etiqueta "MÍOS — ya no los necesito" (el contenido aparece en el Archivo Muerto), **fichas C-14 y C-15** y una biblioteca: el libro "Tratado de la Observación" abre el pasadizo. |
| **Sala de Observación** | −8..−2, 15..22 | **Pared de 12 monitores CRT** (4×3) **interactuables** (ver mecánicas: vista POV de cámaras), consola con perillas, estante de **cintas U-matic** y reproductor, una silla mirando los monitores. **La capturadora de Lauti** sigue enchufada con un cable que baja por la pared hacia el suelo. Sobre la puerta está la **CAM 12, que apunta a la silla** (B12). |
| **Ala este** | 1..29, 0..24 | Techo derrumbado, cielo abierto con niebla y relámpagos, piso con agujeros hacia el 1P (caída de 6 bloques), musgo pálido, ruido de lluvia. Una escalera rota sube al techo. |

### TECHO (y 18)
Tanque de agua sobre pilotes (18..24, 16..22), antena (`lightning_rod` + `iron_bars`), el dorso de las letras gigantes y la luz roja. **Secreto:** el **dron de Lauti** estrellado, con la etiqueta "comprado con la plata del sorteo", y la **pulsera C-13**.

### SUBSUELO 1: zona morgue (y −6..−2, solo ala este, por la escalera de servicio)
| Sala | Caja | Contenido clave |
|---|---|---|
| **Pasillo de servicio** | 10..29, 12..14 | Caños (`copper_grate`, `chain`) y goteo. |
| **Morgue** | 14..29, 1..11 (16×11) | **24 cajones** (`cajon_morgue`) en 3 filas de 8 sobre el muro sur, numerados con TextDisplay. 2 mesas de autopsia, rejilla de desagüe, balanza y bandeja. **Libro de ingresos** en un atril ("TOTAL 1953–1989: 1.988"; agregado en lápiz: "14-IX-2026 — C-14 — BENÍTEZ L. — PENDIENTE"). Luz fría de `soul_lantern` en el techo, un tubo que parpadea y neblina fría (partículas). 2 **Ánimas** existentes. **Cajón 7: el choripán.** **Cajón 14: golpea.** |
| **Lavandería** | 10..22, 15..24 | Lavarropas industriales, **sábanas colgando** (BlockDisplay finos y blancos que se mecen) y un conducto de ropa sucia que baja del 2P. La camilla reaparece acá (B-sistémico). |
| **Sala de calderas** | 23..29, 15..24 | Calderas (`blast_furnace`), vapor, el libro de guardia de Cacho ("Noche 9/7/89: se cortó la luz. Raro. Me quedo hasta que me releven."). |

### SUBSUELO 2: Central del SOC (arena del boss, y −15..−9, oeste)
- **Acceso único:** fondo del pozo del ascensor A (X 2..4, Z 15..17, piso y −16) → escotilla en el muro oeste → pasillo corto → la central.
- **Arena: X −16..2, Z 2..20 (19×19, 7 de alto).**
  - **32 monitores CRT** en los muros norte y este (en estática; muestran "EN VIVO" y tu silueta).
  - Racks de grabadoras U-matic en el muro oeste. Cables por todos lados: alfombras negras en el piso, `chain` colgando y manojos de `black_concrete` que convergen al centro.
  - **"La Silla"** en un estrado central: sillón de dentista/psiquiátrico (`smooth_stone` + `iron_bars` + `black_wool`). En la silla, **el cuerpo de Lauti**, momificado, con los auriculares puestos e iluminado por un **segundo ring light**.
  - Delante, en un trípode con gimbal, **el celular de Lauti** (ancla, `AnchorEntity`), con un cable a la consola.
  - **8 cámaras CCTV** (CAM 25–32) en los muros a media altura, más **la cámara del celular** como "novena".
  - **4 pilares** para cortar línea de visión y **4 luces de emergencia rojas giratorias** en las esquinas.
- **Archivo Muerto (secreto):** −16..−12, 21..24, detrás de un rack flojo. Catre del Doctor, sus anteojos, **la última página de su diario** y el frasco con sus ojos.

### Plan de iluminación
| Zona | Fuentes | Intención |
|---|---|---|
| Exterior | Luna/niebla de la dimensión, **balizas** naranjas, velas de la ermita (3), luz roja de las letras, brillo azul del TV de la garita (6), **relámpagos lejanos** cada 40–90 s (rayo `visualOnly`) | Plano de establecimiento: las balizas en la niebla. |
| PB | Oscuridad total + carteles **SALIDA** verdes (luz 4) para orientarse, estática del TV de recepción (6), farol de la Guardia (12), velas de la capilla (6) | Navegar por "islas" de luz. |
| 1P | Tubo #4 que parpadea, lamparitas del llamador (3), ring light del quirófano (15, blanco puro), lámpara quirúrgica que se prende de golpe (B05) | El **círculo blanco al fondo del pasillo** se vuelve el lenguaje visual de "Lauti está ahí". |
| 2P – C | **TODO prendido** (15) y zumbando | Terror a plena luz, territorio del Doctor. |
| 2P este | Luna + relámpagos | Respiro visual. |
| S1 | `soul_lantern` frío en la morgue (10), un tubo que parpadea y el resto negro | Frío y claustrofobia. |
| S2 | Luces rojas giratorias + 32 monitores (5 cada uno) | La arena está iluminada por pantallas que te muestran a vos. A medida que rompés cámaras **se va oscureciendo**. |

### Mapa de pistas
| Dónde | Pista | Qué revela |
|---|---|---|
| Auto | Radio 1989 (audio) | Apagón, 13 muertos, el doctor desaparecido. |
| Reja exterior | Afiche SE BUSCA + graffitis | Lauti, el sorteo, el tono. |
| Recepción | Recorte "EL ECO DE VILLA LUCERO" | Tragedia del 89 + chiste de la hiperinflación. |
| Recepción | Afiche "SE BUSCA: CHORIPÁN" | Cruce con el caso 2. |
| Guardia | Libreta pág. 1 | El plan de Lauti, "es el viento, chat". |
| Administración | Memo 114/74 + circular | El SOC y la regla de la luz. |
| Cafetería | Menú en australes | Humor, la fecha 9/7/89. |
| Quirófano 2 | Libreta pág. 2 | La llave C y Cacho. |
| Office de enfermería | Nota del tablero + libro de guardia | "Si se corta la luz, se van." |
| 1P pasillo | Plano de evacuación | No existe la Sala 14. |
| Morgue | Libro de ingresos | **1.988** (clave del candado) y C-14 pendiente. |
| Pabellón C | 13 pulseras (coleccionables) | Nombres reales de los usuarios del chat. |
| Sala de Día | Silla 14 "LAUTI ❤" y silla 15 con tu nombre | Que te están esperando. |
| Consultorio | Diario + fichas C-14 / C-15 | La teoría del Doctor y tu internación. |
| Sala de Observación | Cintas 1–4 | Ver el detalle abajo. |
| Sala 14 | Foto de Norma + registro de llamada + Libreta pág. 3 | **Giro 1.** |
| Archivo Muerto | Última página del diario | "Tengo treinta y dos." |

### Textos (in-game, listos para el lang)

**Libreta de Lauti, pág. 1 (Guardia)**
> PLAN STREAM 24HS SAN LÁZARO
> 1) Entrar por la guardia (la puerta tiene cadena, re cine)
> 2) Asustarme (de verdad, el chat se da cuenta)
> 3) Quirófano → bit del "cirujano"
> 4) Pabellón C → LAS CÁMARAS DEL 74!!! (dicen que andan sin luz, mentira pero queda bien)
> 5) Llegar a 1000 viewers
> 6) Sorteo (??? ver con Gonza)
> Frase para cuando tenga miedo: "es el viento, chat".

**Pág. 2 (Quirófano)**
> 02:10 — Algo me tocó la nuca. Es el viento, chat.
> 02:40 — La llave del C no está en el tablero. Hay un papelito: "la tiene Cacho". ¿Quién es Cacho?
> 03:05 — Cacho existe. Está en la garita. Le di un alfajor y me dio la llave. No le vi los pies.

**Pág. 3 (Sala 14, letra temblorosa)**
> 03:29 — HAY UNA CONSOLA. Si le enchufo la capturadora el chat ve las cámaras del 74. Clip del año.
> 03:33 — 1.989 viewers. No conozco a nadie. Me escriben como si me conocieran.
> Hay uno que me dice "comé algo, Lauti". Así me escribía mamá.
> Si mamá me está mirando desde algún lado, que vea que la rompí.
> 04:02 — El ascensor anda. No tiene luz y anda. Me está llamando. Voy a bajar. Si no vuelvo, el sorteo lo gana...

**Diario del Dr. Mendizábal (consultorio)**
> 3-III-1974. Instalamos las 32 cámaras. La enfermera Ruiz preguntó para qué. Le expliqué: la locura es un alma que se escurre cuando nadie la mira. Mientras alguien mire, nadie se va.
> 11-VIII-1981. Ya no duermo en mi casa. Duermo frente a los monitores. Cuando cierro los ojos, sigo viendo por las cámaras. Los ojos me sobran.
> 8-VII-1989. La compañía eléctrica avisa el corte. El Ministerio no contesta. Si se apaga la luz, se van a ir. Todos. No lo voy a permitir.
> 9-VII-1989, 23:50. Si nadie más puede mirarlos, los miro yo. Para siempre. Me quedo en la central. Que nadie apague.

**Última página (Archivo Muerto):** *"Ya no necesito los ojos. Tengo treinta y dos."*

**Ficha C-14** (formulario a máquina de los 70)
> POLICLÍNICO SAN LÁZARO — PABELLÓN C — FICHA DE INGRESO
> Paciente: BENÍTEZ, Lautaro. Edad: 24. Nº: C-14.
> Ingreso: 14-IX-2026, 03:33 hs.
> Motivo: necesidad patológica de ser mirado.
> Tratamiento: observación continua.
> Alta: NO.
> Firma: Dr. A. Mendizábal

**Ficha C-15:** Paciente: **[NOMBRE DEL JUGADOR]**. Nº: C-15. Ingreso: **HOY**. Motivo: **vino a mirar.** Tratamiento: observación continua. Alta: NO.

**Memo 114/74:** "Se instalan 32 cámaras de circuito cerrado y una central de grabación en el Subsuelo 2. Queda PROHIBIDO apagar las luces del Pabellón C bajo ninguna circunstancia. Ningún paciente debe permanecer sin observación. — Dr. A. Mendizábal"

**Recorte:** "EL ECO DE VILLA LUCERO — 11 de julio de 1989 — TRAGEDIA EN EL SAN LÁZARO: TRECE PACIENTES MUERTOS TRAS EL APAGÓN. El director del pabellón psiquiátrico, Dr. Aurelio Mendizábal, se encuentra desaparecido. El hospital cerró 'por falta de fondos'. *(Pág. 2: el litro de leche ya cuesta ₳ 1.200.)*"

**Menú (cafetería):** "MENÚ DEL DÍA 9/7/89 — Guiso de lentejas ~~₳ 1.400~~ ~~₳ 2.100~~ **₳ 3.800** (precio de las 15 hs). Postre: no hay. Café: preguntar."

**Pizarrón ACTIVIDADES:** "LUNES: Observación. MARTES: Observación. MIÉRCOLES: Taller de mimbre (SUSPENDIDO). JUEVES: Observación. VIERNES: Observación grupal. SÁBADO: TV. DOMINGO: Observación."

**Libro de guardia de enfermería:** "Noche del 8/7/89. El Dr. dice que si se corta la luz 'se van'. Le pregunté adónde. Me dijo: 'A ningún lado, si yo los miro'."

**Cintas U-matic (Sala de Observación, voz TTS + VHS):**
1. **"SESIÓN 1 — 1974":** el Doctor (em_santa, lento) explica la teoría frente a un paciente que no contesta. "Míreme. Míreme. ¿Ve? Ya no se va."
2. **"PACIENTE C-13 — N.N.":** un nene (ef_dora con pitch alto) pregunta todo el tiempo "¿me mirás?". El Doctor: "Siempre."
3. **"09-VII-1989 23:58":** solo audio. Pánico, gente que llama a la enfermera, el clic de la luz que se corta, silencio de 6 segundos y el susurro del Doctor: "Acá estoy. Acá estoy. Yo los miro."
4. **"LAUTI — 14-IX-2026 03:31"** (sin etiqueta, la grabó la central): "¡Chat! ¿Se ve? ¡Las cámaras andan! ¡ANDAN SIN LUZ! ...Ey, ¿quiénes son todos esos? ¿Mil novecientos...? Hola, hola, bienvenidos..."

### Secretos y easter eggs
1. **Sala 14:** está en el camino crítico pero escondida. El yeso **está fresco**: el hospital la volvió a tapiar.
2. **Archivo Muerto (S2):** el final del Doctor y el frasco con sus ojos.
3. **Baño del espejo (2P):** el "espejo" es un vidrio que da a una habitación espejada construida detrás. En el "reflejo" hay un paciente parado que en la habitación real no está, y **vos no aparecés** en el espejo. Chat: `pelusa_10: no tenés reflejo jajaja estás muerto`.
4. **Techo:** el dron del sorteo y la pulsera C-13.
5. **Cajón 7 de la morgue:** el choripán del sereno, envuelto en el diario del 10/7/89.
6. **Afiche "SE BUSCA: CHORIPÁN"** en la recepción. Chat: `pelusa_10: choripán no era el perro poseído del otro video??`.
7. **Flechas UV de Lauti:** llevó un marcador UV "para el chat". La linterna en modo UV muestra su ruta y funciona como guía opcional.

---

## 4. Entidades

### 4.1 LAUTI EXTREMO, "El Streamer" (Paciente C-14) · `lauti`
**Rol:** acechador secundario y cara del caso. No se puede matar, solo aturdir. Se libera al final.

**Regla núcleo: se mueve cuando lo mirás.** Se reusa `isWatchedBy()` invirtiendo la condición. La velocidad escala con lo centrado que esté en tu pantalla: 0 si está fuera de vista, 0,25 en el borde y 0,5 en el centro. Si además lo iluminás con la linterna, ×1,5. Cuando no lo mirás **se congela en una pose ridícula**, y cada vez que te das vuelta está en otra pose y más cerca. Es la gag visual recurrente del caso.

**Estados:**
1. **ACECHO (E2–E9).** Aparece en fondos de pasillo, marcos de puerta y la baranda del balcón, siempre fuera de cuadro. El zumbido del ring light y su **música lo-fi de stream** (posicional, desafinada) suben al acercarte: es la pista sonora de que está cerca. Sus pasos **tartamudean** como un video con lag. Si lo mirás más de 1,5 s avanza diciendo "¡Hola chat!".
2. **DONACIÓN (embestida).** Una vez cada ~90 s, si tiene línea de visión, suenan **el jingle de donación** y el TTS robótico: *"pelusa_10 donó cien australes: CORRÉ."* Durante 3 s corre al doble de velocidad **aunque no lo mires**, con los brazos para atrás. Es un aviso telegrafiado, gracioso y aterrador.
3. **CHIVATEO.** Si tenés la cámara de Lauti prendida, el chat le pasa tu ubicación (ver mecánicas).
4. **"Saludo" (ataque).** Si te alcanza te agarra la cara: la cámara queda trabada mirándolo 1,5 s, salta el jumpscare `lauti` con el grito **"¡SUSCRIBITE!"** distorsionado, 4 de daño y −25 de cordura. Después se teletransporta riéndose con glitch de buffer. No mata salvo que tengas poca vida.

**Contras:**
- **No mirarlo.** Mirar el piso en pánico es tensión pura en cámara.
- El crucifijo lo repele y una línea de sal lo frena.
- **Agua bendita → BUFFERING** (4 s): queda congelado con un **círculo de carga** de partículas blancas girando sobre la cabeza.
- **Desfibrilador → "REINICIO"** (8 s): "...se me cortó...".
- **Flash de la Cámara de Espíritus → SELFIE** (4 s): **posa** con dos dedos en V, lengua afuera y cabeza ladeada, y no se puede mover. Es un aturdimiento cómico.
- **Bengala → señuelo** (10 s): va a "posar" en la luz como una polilla.

**ART BRIEF** (unos 150 cubos; 16 px = 1 bloque; densidad 2×)
- **Silueta:** flaco, encorvado, unos 31 px de alto erguido y 27 encorvado. Brazos largos hasta las rodillas. Sobre la cabeza, **un ring light octogonal como aureola**: 8–10 cubos, unos 14 px de diámetro, en un caño de 1×12×1 que sale de la espalda, **emisivo blanco puro** con una capa de brillo suave. Es un santo falso del contenido.
- **Cabeza** 8×8×8 con capucha (cáscara inflada 0,5 en los lados y atrás). **Auriculares gamer fusionados al cráneo:** copas de 2×4×4, vincha y micrófono de brazo (3 cubos), con una **tira RGB** emisiva que cicla color. Los cables de las copas entran en el cuello como venas.
- **Cara (textura 16×16):** ojos enormes y redondos con pupilas mínimas. **Tiras de cinta** amarillenta tiran de los párpados hacia la frente para que no pueda cerrarlos. Ojeras moradas. La cara está iluminada desde abajo en azul pálido, como si mirara el celular. **Mandíbula como cubo aparte, con bisagra**, que se abre 70° en la **"cara de miniatura"**: una O negra con reflejo azul en los dientes y labios agrietados.
- **Torso** 9×12×5 con buzo negro y el logo "LX" en verde neón. **Arnés en el pecho con una cámara de acción** (3×3×2) y LED rojo emisivo. Una lata de energizante asoma del bolsillo.
- **Brazos** en dos segmentos de 3×10×3. Manos de 3×4×2 con dedos largos (4 cubos) y **pulgares exageradamente largos de 1×5×1** ("pulgares de scrollear").
- **Piernas:** jogging gris de 4×12×4. Una zapatilla blanca sucia y un **pie en media agujereada**.
- **Paleta:** buzo #17171B, logo #3BFF5C, auriculares #0C0C0C + RGB, piel #A9A49A con sombras #6E7480, ojeras #4A3A44, boca #120608, cinta #D9C99A, jogging #3A3D44, media #E8E4DA, ring light #FFFFFF emisivo, LED #FF2020.
- **Poses/animaciones:** `idle_reacting` (cabeceo nervioso, como hablándole al chat), `peek` (solo la cabeza y la aureola asomando por un marco), `walk_hunched`, `crawl` (en cuatro patas con la cabeza en alto), `dash` (corriendo con los brazos para atrás), `thumbnail_scream` (manos en las mejillas, boca al máximo), `selfie`, `buffering` (congelado con micro-temblor), **6 poses congeladas ridículas** (señalándote, manos en las rodillas riéndose, festejo de gol con los brazos arriba, mano en la boca sorprendido, saludo de "¡hola chat!", tirando corazón con las manos), `sit_streaming`, `beg` (de rodillas con las manos juntas), `dissolve` (se sienta, se saca los auriculares y se deshace en partículas).
- **Variante "cuerpo":** el mismo modelo, `sit_dead`, textura desaturada y momificada y mandíbula caída, sin aureola. Es el cuerpo de la silla.

### 4.2 EL OJO, Dr. Aurelio Mendizábal (boss) · `ojo`
**Rol:** boss principal, omnipresente a través de las cámaras.

**Reglas:**
1. **Atado a la luz:** solo puede existir físicamente donde la luz es ≥ 7 **o** dentro del cono de una cámara CCTV activa. La oscuridad es una pared para él. La mamá lo avisa en el chat: *"el doctor le tiene miedo a la oscuridad, querido"*.
2. **Viaje por cámaras:** si una cámara te ve (cono de 40°, alcance 14, línea de visión), su **LED** pasa de apagado a **parpadeando** (2 s de aviso) y a **fijo** (3 s). Después **te transfiere** al Doctor: ráfaga de estática con "BWOOM" de desmagnetización y él sale caminando debajo de esa cámara. Enfriamiento de 25 s (10 s en el boss). **Las cámaras giran físicamente siguiéndote**, con un BlockEntityRenderer que rota el cabezal con pasos de servo audibles ("zzt-tic").
3. **"TE ESTÁ GRABANDO" (secuestro de POV):** si su lente te ve 2 s seguidos a menos de 16 bloques, **tu vista pasa a su POV**: shader de CCTV en blanco y negro con "CAM 00 · DR. A. M. · REC ●" y timecode de 1989. Dura hasta 6 s o hasta que se corte la línea de visión. **Seguís controlando tu cuerpo**, así que tenés que escapar mirándote desde los ojos del enemigo. Es oro para clips. −10 de cordura. Con el rosario en la mano dura la mitad.
4. **Rondas:** camina lento (0,6× la caminata del jugador), con las manos en la espalda como en una recorrida de sala. Se detiene a "observar": el lente barre la habitación en pasos mecánicos.
5. **"Internación" (agarre):** te levanta, el lente hace zoom hasta tu cara y dice con TTS: *"Paciente C-15. Ingreso."* Fundido a negro y **despertás en la celda C-08** con una pulsera "C-15 [Nombre]" en el inventario y la puerta abierta. Chat: *"JAJAJA LO INTERNARON"*. Te hace perder tiempo, no la vida. Con el ancla ya purificada, el agarre hace daño en vez de teletransportarte.
6. **Antes de purificar el ancla es invulnerable.** Agua bendita: **lente rajado** (aturdido 5 s). **Flash: sobreexposición** (ciego 8 s: choca con paredes y no puede secuestrar el POV). Es el duelo cámara contra cámara. El crucifijo lo empuja. La sal frena su caminata pero no su viaje por cámaras (eso le enseña al jugador a ocuparse de las cámaras).

**ART BRIEF** (unos 170 cubos)
- **Silueta:** **2,5 bloques (40 px)**, flaquísimo, sin cabeza. **En el muñón del cuello, un soporte de metal doblado sostiene una cámara de circuito cerrado de los 70.** Desde lejos se lee como un médico con una cámara de seguridad por cabeza.
- **Cámara-cabeza:** carcasa beige-gris de metal de 6×6×12 con visera fina sobre el lente. **El lente son 4 cilindros telescópicos** (cada uno con 2 cubos cruzados para que se vea octogonal) que **se extienden de 0 a 10 px** al hacer zoom. **Dentro del lente hay un ojo humano real**, emisivo: esclerótica #E8E2D0 e iris rojo-ámbar #C0392B. **Luz tally roja** de 1×1×1 arriba, emisiva, que parpadea al "grabar".
- **Cola:** un **cable coaxial** sale de atrás de la carcasa, baja por la columna y **se arrastra por el piso** detrás de él: 12 segmentos de 1×1×4 encadenados con balanceo animado.
- **Cuerpo:** guardapolvo largo hasta media canilla. Torso de 8×14×4 y **faldón de 4 paneles con bisagra** que flamean al caminar. Abotonado torcido, manchado de amarillo y marrón en el ruedo. Estetoscopio alrededor del muñón. Plaqueta "DR. A. MENDIZÁBAL — DIRECCIÓN". Lapiceras y martillo de reflejos en el bolsillo. Pantalón gris y zapatos de cuero viejos.
- **Manos:** guantes de látex amarillentos con dedos de 1×6×1, demasiado largos.
- **Paleta:** guardapolvo #D9D2B6, manchas #8A6E3A, carcasa #8E8C84, lente #111111, ojo #E8E2D0 / #C0392B emisivo, tally #FF1A1A, guantes #E6DCA8, cable #0A0A0A.
- **Poses/animaciones:** `idle_pan` (el lente barre en **pasos de servo**, no en movimiento suave; es lo más inquietante), `walk_rounds` (zancadas rígidas con las manos atrás), `zoom` (se inclina hacia adelante y el lente se extiende), `record` (congelado con el tally encendido), `grab_lift`, `transfer_in/out` (se disuelve en estática), `blind` (se tambalea con la mano en el lente), `hurt_crack`, `kneel_guard` (arrodillado frente al celular), `reveal` (**la carcasa se desprende** y debajo aparece **una cabeza de viejito diminuta**, de 6×6×6, ridículamente chica para el cuerpo, **con los párpados cosidos** con X de hilo negro, sollozando).

### 4.3 LA AUDIENCIA, los 13 del Pabellón C · `audiencia` (13 variantes de textura)
**Reglas:**
1. **Invisibles a simple vista.** Se ven a través de la **cámara de Lauti**, de los **monitores y POV del CCTV**, durante **los destellos de los relámpagos** (3 ticks: se ven siluetas en las ventanas) y con cordura menor a 20.
2. **No atacan: miran.** Las cabezas te siguen 180°. Se montan en "cuadros vivos": sentados en las sillas, en fila a lo largo del pasillo, en la galería del quirófano o alrededor del lugar donde estabas cuando te diste vuelta.
3. **Tienen cuerpo:** son invisibles pero sólidos. Si te chocás con uno en la oscuridad se oye una respiración, sentís un empujón suave y en el chat aparece *"pochamedina: ups perdón nene"*.
4. **Drenaje por mirada:** cada paciente visible que te mira drena 0,3 de cordura por segundo (se acumula) y acelera los avisos de las cámaras del Doctor.
5. Con la cámara prendida **flotan sus nombres de usuario** sobre la cabeza, con el color de su nombre en el chat. Así se conecta el chat con los cuerpos.
6. **Final:** salen caminando con vos. En la puerta principal cada uno se detiene, se da vuelta, asiente y se deshace en partículas de Ánima. Si juntaste su pulsera, se despide en el chat con su nombre real: *"Ofelia Duarte (1931–1989): gracias por el nombre, nene."*

**Elenco y "poderes" (cada usuario muerto tiene una personalidad y un efecto en el juego):**
| Paciente | Usuario | Personalidad / efecto |
|---|---|---|
| C-01 Ofelia Duarte | `ofeliaD31` | Abuela simpática, da la bienvenida ("qué lindo que vino otro"). **Gana el sorteo.** |
| C-02 Teodoro "Tito" Barrionuevo | `TITO_ELMAGO` | Se creía mago. **Anuncia los poltergeist:** "¿quieren ver un truco?" y se apagan las luces o arranca la camilla. "...¡y desapareció!" |
| C-03 Raúl Cufré | `raulcufre_tv` | Pide que cambies de canal. "Esto ya lo vi." |
| C-04 Amalia Rosas | `amaliarosas` | Romántica: "qué buen mozo el nuevo". |
| C-05 Jalil, "el Turco" | `elturco_jalil` | Opina de precios: "en mi época esto costaba dos australes". |
| C-06 "Pocha" Medina | `pochamedina` | Abuela total: "abrigate", "¿comiste?", "ups perdón". |
| C-07 Ernesto Lugones | `ernesto_77` | **Cuenta.** "Faltan dos." Da la clave **1988**: "mil novecientos ochenta y ocho. yo los conté." |
| C-08 Mirta Galván | `mirta_g` | **Chusma.** Le cuenta a todos: te avisa dónde está el Doctor ("el doctor está en la morgue, eh, yo no dije nada") y **también le avisa al Doctor dónde estás vos**. |
| C-09 Néstor "Pelusa" Rivas | `pelusa_10` | Futbolero: relata como partido ("¡qué jugada!", "GOOOL" cuando te pegan) y **dispara las "Repeticiones"** de tu voz. |
| C-10 Beatriz Lell | `bea_lell` | Rezadora: "Ave María Purísima" cuando usás el crucifijo. |
| C-11 Hugo Molina | `hugomol` | Escéptico muerto: "esto es fake". El chiste es que está muerto. |
| C-12 Dorita Sosa | `dorita` | Solo manda corazones y "hermoso". |
| C-13 N.N., varón, unos 10 años | `nn_13` | **El Nene de la Caja.** Su "atrás tuyo" **siempre es verdad**. |

**ART BRIEF base** (unos 65 cubos + accesorios por variante)
- Humano de 28 px, flaco. **Bata de hospital verde-celeste #9FB7B0** con tiras atadas atrás y manchas desteñidas. Piel #C9C2B8 desaturada, pies descalzos grises #8A8780.
- **Cabezas rapadas con cicatriz quirúrgica y ganchitos.** **Ojos: cuencas negras hundidas** (#050505) con 1 px de reflejo celeste.
- Capa emisiva suave en la cara: **brillo azul de pantalla**, siempre iluminados desde abajo por un televisor que no existe.
- Pulsera blanca con raya roja.
- **Accesorios por variante:** redecilla y ruleros (Pocha), gorro cónico de papel con estrella (Tito), camiseta a rayas bajo la bata y bufanda (Pelusa), trenza gris larga (Ofelia), bigote y cuerpo ancho (Turco), anteojos, labios pintados y mano en la boca (Mirta), dedos contando (Ernesto).
- **Poses:** `seated`, `stand_still`, `head_track`, **`slow_clap`**, **`point_all`** (todos te señalan a la vez), `whisper` (Mirta), `walk_calm`, `nod_goodbye`, `fade`.

### 4.4 EL NENE DE LA CAJA (C-13, N.N.) · variante especial
- **Arte:** Audiencia a escala 0,7 con la bata enorme. **Cabeza: una caja de cartón** de 10×9×10 (#B08A5A) con **una pantalla de TV dibujada con marcador**, una sonrisa dibujada, dos agujeros por ojos (vacío negro con puntito blanco) y dos "antenas" de alambre. En la mano, un control remoto de juguete.
- **Conducta:** es el único que aparece **sin cámara**. Solo se materializa **justo detrás tuyo** después de que `nn_13` escribe "atrás tuyo" (enfriamiento de 3–4 min). Si lo mirás 1 s, se ríe, dice ***"¿Me mirás?"*** y desaparece. No hace daño; −8 de cordura.
- **Final:** es el último en irse. **Deja la caja en el piso** y sale caminando de espaldas; nunca le ves la cara. La caja queda como trofeo: **"Caja del Nene"**.

### 4.5 LA CAMILLA · `camilla` (peligro poltergeist)
- **Conducta:** en el pasillo largo del 1P, cuando `TITO_ELMAGO` escribe "¿quieren ver un truco?", **los tubos se apagan uno por uno hacia vos** y la camilla del fondo arranca y acelera hasta 1,3× tu sprint. Si te alcanza: empujón fuerte, 4 de daño y −15 de cordura. Si entrás a una sala y cerrás la puerta, la camilla **golpea la puerta**. Una **línea de sal la frena en seco**, y entonces la sábana se incorpora.
- **Remate:** la camilla choca contra la pared, la sábana sale volando, **se para sola como fantasma de dibujito animado**, da dos pasos y cae vacía. Chat: *"TITO_ELMAGO: ...¡y desapareció!"* y suena el aplauso de la Audiencia.
- **Reaparición cómica** (más tarde, en la lavandería o al fondo de un pasillo): **Lauti pasa montado en la camilla como en una patineta**, filmándose: "¡CHAT, MIREN!". Es absurdo puro.
- **Arte** (unos 40 cubos): estructura de acero #8C9196 con óxido #7A4A2A, 4 ruedas que giran (**una baila**), cuerpo bajo una sábana #E4E0D6 con manchas #6B1E1E, **un brazo gris colgando** y un pie asomando con la etiqueta **"Nº 1.989"**.

### 4.6 DON CACHO, el sereno (Ernesto Funes) · `sereno` (PNJ fantasma amigable)
- **No sabe que está muerto.** Está sentado en la garita **mirando un partido** de 1989 en un TV con estática. Es **el único muerto que no mira a Lauti**: *"Yo no miro eso del chico. Yo miro el partido."*
- **Diálogo** (TTS em_alex, voz mayor y cálida, con subtítulos):
  - "¿Usted es de la empresa? Estoy acá desde el 89. Nadie me vino a relevar."
  - "¿La llave del C? La tengo. El otro pibe me la devolvió... bah, la llave siempre vuelve a mi bolsillo."
  - "Pero estoy sin comer, pibe. El de los auriculares me trajo **un alfajor**. Un alfajor. Treinta y siete años sin comer y me trae un alfajor."
  - "Dejé un choripán en la heladera de abajo." / "¿Qué heladera?" / "**La de la morgue. Es la única que enfría.** El cajón siete. O el catorce. El siete."
  - Al recibirlo: *(mastica)* "...Está frío. Pero está bueno." Te da la llave: "No mire mucho las cámaras, pibe. Al doctor le gusta que lo miren mirar."
  - **Final:** sale de la garita y saluda: "Bueno, pibe. Parece que ya me relevaron." Su TV se apaga.
- **Arte** (unos 60 cubos, **translúcido cálido**, alpha 0,75 con tinte sepia #E8D2A8; no es azul porque es un fantasma "bueno"): petiso y panzón, gorra con escudo, **bigotazo**, chaleco de lana sobre camisa, linterna en el cinto, **mate (#6B4A2A con bombilla de metal) y termo (#3E6B4A)**. Poses: `sit_mate` (sorbe en loop), `point`, `eat_bite`, `wave_goodbye`.

### 4.7 Reusadas y opcionales
- **Ánimas** (existentes): 2 en la morgue. En el éxodo final la Audiencia se deshace en sus partículas.
- **Hombre Sombra** (existente): con cordura baja aparece **dentro de los monitores** como una silueta con sombrero detrás de tu imagen.
- **Alucinación nueva del caso:** con cordura menor a 25, **aparecen en el chat mensajes con TU nombre de usuario que no escribiste**: *"[Jugador]: no quiero estar acá"*, *"[Jugador]: está atrás mío"*. En multijugador, con el nombre del compañero.
- **Dron de Lauti** (P2, unos 20 cubos): 4 rotores que giran, LED rojo y la calcomanía "LX". En el techo **sube desde abajo del borde** y te mira. Chat: *"ese es el dron que se compró con la plata del sorteo"*.

---

## 5. Guion de sustos (en orden de escalada)

Marcas: ★ = **TOP 5 CLIP** · ⚡ = **jumpscare de pantalla completa** (máximo 3 en todo el caso, más el agarre) · ☺ = susto con remate de humor.

**B01: Las balizas (E0).** *Disparador:* llegar al auto.
*Qué pasa:* las balizas laten en la niebla. **La radio del auto se prende sola**: un boletín de AM de 1989 ("...apagón total en el Policlínico San Lázaro... trece pacientes...") que se corta a un fragmento de cumbia, después estática, y una voz cerca del micrófono: *"¿...estás en vivo?"*.
*Sonido:* `hospital.radio_1989` y `hospital.balizas`.
*En cámara:* da toda la exposición en 15 segundos sin un solo cartel, y es un plano de apertura hermoso.

**B02: El turnero (E1) ☺.** *Disparador:* entrar al hall.
*Qué pasa:* **"DING-DONG: TURNO 13"** y el turnero **imprime un ticket solo: Nº 1.990**.
*En cámara:* un sobresalto suave y el chiste del hospital público argentino ("sacá número"). Es la semilla del 1.990.

**B03: ★ "Atrás tuyo" (E3), CLIP 1.** *Disparador:* la primera vez que abrís EN VIVO.
*Qué pasa:* tu vista salta al POV de Lauti. Ves un pasillo oscuro y a alguien con linterna caminando de espaldas, a 5 bloques: **sos vos.** El chat explota: "ATRÁS TUYO" ×40. Cerrás, te das vuelta y no hay nadie. Solo el zumbido del ring light apagándose.
*Sonido:* `stream.pov_in/out`, ráfaga de `chat.pop`.
*En cámara:* el espectador entiende antes que el jugador. Es un clip perfecto de 10 segundos. *(Guionado: Lauti aparece 5 bloques detrás tuyo al abrir el POV por primera vez.)*

**B04: El monitor cardíaco (E2/E3).** *Disparador:* acercarte a un box de la Guardia.
*Qué pasa:* un monitor late **sincronizado con tu ECG del HUD**. Al llegar al lado, el monitor **se va a plano** y **tu ECG también** durante 2 s: la pantalla se pone gris y se corta el sonido. Después vuelve.
*Sonido:* `hospital.heart_monitor_beep`, `hospital.flatline`.
*En cámara:* usa la propia interfaz del mod para asustar, como un susto "meta".

**B05: La galería que aplaude (E3) ☺.** *Disparador:* pararte junto a la mesa del Quirófano 2.
*Qué pasa:* **la lámpara quirúrgica se prende a toda potencia** con un flash blanco que ciega. Cuando baja, detrás del vidrio de la galería **están los 13 sentados mirándote**, y **aplauden despacio**. Clac. Se apaga y no queda nadie.
*Sonido:* `hospital.surgical_lamp`, `hospital.applause`.
*En cámara:* aterrador y ridículo a la vez. Es el clip de reserva más fuerte.

**B06: La camilla (E3/E4) ☺.** *Disparador:* `TITO_ELMAGO: ¿quieren ver un truco?` estando en el pasillo largo.
*Qué pasa:* los tubos se apagan hacia vos, la camilla acelera, persecución hasta la escalera, choque, la sábana se para sola, da dos pasos y cae. "...¡y desapareció!" y aplausos.
*Sonido:* `hospital.gurney_roll` con el pitch subiendo según la velocidad, `hospital.gurney_crash`, `hospital.sheet_flap`.
*En cámara:* persecución con la cámara temblando y una liberación cómica.

**B07: Primera donación.** *Disparador:* el primer silencio largo después de B06, a los 20–40 s.
*Qué pasa:* silencio total, y de golpe el **jingle de donación a todo volumen** y la voz robótica: ***"ofeliaD31 donó cincuenta australes: qué lindo que vino otro."***
*En cámara:* usa un sonido que el público tiene grabado (las alertas de stream) como arma. Gracioso y desconcertante, y los australes adelantan el giro.

**B08: ★ "Repetición" (cualquier momento después del primer grito detectado), CLIP 2 ☺.** *Disparador:* el mod de voz detecta tu primer grito. Entre 60 y 180 s después, `pelusa_10` escribe "REPETICIÓN".
*Qué pasa:* suena **el ding-dong de la megafonía** y una locutora de los 80: *"Repetición."* Y por los parlantes del pasillo suena **tu propio grito**. Después: *"Repetición en cámara lenta."* Y tu grito otra vez, **lento y grave**.
*Sonido:* `hospital.pa_chime`, `hospital.pa_voice` y el clip de Simple Voice Chat procesado.
*En cámara:* es **el** clip de humor del video. Muy argentino (repetición de jugada en la tele) y personalizado: nadie más tiene ese clip.

**B09: Cajón 14 (E6).** *Disparador:* entrar a la morgue.
*Qué pasa:* golpes desde adentro del cajón 14 y después, **ahogada, tu voz**: un fragmento tuyo (*"¿hola?"*, lo que hayas dicho) con filtro pasa-bajos, desde adentro del metal. Lo abrís y está **vacío**, con la etiqueta "C-14 BENÍTEZ L. — PENDIENTE". **Detrás tuyo, el cajón 7 se abre solo**: el choripán. Si te das vuelta hacia la mesa de autopsias, **una Ánima está sentada** y se desvanece.
*Sonido:* `hospital.morgue_knock`, `hospital.morgue_drawer`.
*En cámara:* tensión, tu propia voz y alivio cómico (el choripán).

**B10: ★ La Audiencia (E7), CLIP 3. El momento más fuerte del caso.** *Disparador:* entrar a la Sala de Día.
*Qué pasa:* a simple vista hay **15 sillas vacías** frente a un TV apagado, a plena luz. Prendés la cámara de Lauti: **13 pacientes sentados, y las 13 cabezas giran 180° al mismo tiempo** para mirarte, con sus nombres de usuario flotando. Apagás y está vacío. Prendés de nuevo: **están parados, tres bloques más cerca, señalándote todos.** Apagás. Prendés: **la cara de Pocha a 20 cm.** *"nene, abrigate."*
*Sonido:* `audiencia.necks` (crujido de muchos cuellos), `cam.on/off`, `audiencia.count`.
*En cámara:* la mecánica de prender y apagar es un susto que el propio jugador provoca, y el público grita "¡NO LA PRENDAS!". El remate de Pocha corta la tensión justo antes de que sea demasiado.

**B11: La silla 15 + ficha C-15 (E7).** *Disparador:* leer las sillas y las fichas.
*Qué pasa:* tu nombre en la cinta de la silla 15 y la ficha con "Motivo: **vino a mirar.**" El contador del HUD pasa de 1.989 a **1.990**.
*En cámara:* escalofrío personalizado (con el nombre real del canal), sin jumpscare.

**B12: ★⚡ Las cámaras (E7, Sala de Observación), CLIP 4.** *Disparador:* recorrer los monitores.
*Qué pasa:* CAM 03: la Sala de Día con los 13 sentados. CAM 07: el pasillo, **el Doctor caminando**. CAM 09: **el Doctor parado frente a la puerta de ESTA sala.** CAM 12, la que apunta a la silla: **vos sentado mirando los monitores, y él parado detrás tuyo.** Salís del monitor y te das vuelta: **JUMPSCARE `ojo`** (el lente hace zoom hasta tu cara) y el primer **"TE ESTÁ GRABANDO"**: tu vista pasa a la de él y tenés que escapar mirándote desde sus ojos.
*Sonido:* `hospital.crt_on`, `ojo.servo`, `ojo.zoom`, `jumpscare`, `ojo.voice` ("Lo estoy mirando.").
*En cámara:* el patrón de "revisar las cámaras" de la cultura gamer, resuelto con una mecánica nueva (el secuestro del POV).

**B13: La sala que no existe (E8). El silencio.** *Disparador:* entrar a la Sala 14.
*Qué pasa:* **el chat se calla por primera vez.** La foto de Norma, "1968–2019". El teléfono vibra: *"Registro: Norma B. — 03:33 — 0:37 — (sin número)"*. Y un único mensaje: ***"MamaDeLauti: perdón que no te dije, querido. Si te decía, no venías."*** Después suena tu teléfono, y al atender solo se oye una notificación de chat y un susurro: *"gracias por ir."*
*Sonido:* `norma.gracias`; la música baja y queda una nota sostenida.
*En cámara:* el momento emocional. El contraste con el ruido del chat hace que funcione, y le da al video un corazón.

**B14: El Nene de la Caja (sistémico, a partir de E7).** *Disparador:* `nn_13: atrás tuyo`.
*Qué pasa:* si te das vuelta, la caja de cartón está a un bloque y ladea la cabeza. *"¿Me mirás?"* Risita y desaparece.
*Sonido:* `nene.me_miras`, `nene.giggle`.
*En cámara:* el público aprende la regla "el chat miente menos uno" y empieza a leer los nombres. Genera participación.

**B15: ★⚡ El ascensor (E9), CLIP 5.** *Disparador:* estar a mitad de la bajada por la escalera del pozo.
*Qué pasa:* arriba, **un cable se corta** (twang metálico) y **la cabina empieza a bajar**, primero despacio y después cayendo. Carrera escalera abajo y salto por la escotilla del fondo. **La cabina se estrella** a un bloque de tu cabeza. Silencio. **La trampilla del techo de la cabina se abre y asoma Lauti, iluminado por su aureola: *"¡HOLA CHAT!"*** (o tu voz, si hay un clip disponible). ⚡ `lauti`.
*Sonido:* `hospital.elevator_snap`, `hospital.elevator_fall`, `hospital.elevator_impact`, `lauti.hola_chat`.
*En cámara:* persecución vertical, golpe de impacto y una primera aparición completa que es aterradora y absurda a la vez.

**B16: Selfie (S2, sistémico) ☺.** *Disparador:* flashear a Lauti con la Cámara de Espíritus.
*Qué pasa:* en vez de gritar, **posa**: dos dedos en V, lengua afuera, *"¡Foto!"*. Se queda 4 s congelado así mientras escapás.
*En cámara:* un clip corto ideal para un Short.

**B17: El raid (inicio del boss).** *Disparador:* entrar a la central.
*Qué pasa:* oscuridad total y **32 monitores se prenden uno por uno** (clic, clic, clic). **Tres cortes rápidos de POV** desde tres cámaras distintas te muestran a vos desde todos los ángulos. Alerta: ***"¡pabellon_c está raideando con 1.988 espectadores!"*** La Audiencia aparece contra las paredes, **visible sin cámara**. Lauti está parado junto a la silla **donde está su propio cuerpo**. El Doctor sale de la CAM 32 en medio de una ráfaga de estática.
*Sonido:* `chat.raid` (fanfarria desafinada), `hospital.crt_on` ×32, `ojo.transfer`.
*En cámara:* el gran plano del boss, y la revelación de que Lauti está muerto.

**B18: Finalizar transmisión (clímax).** *Disparador:* mantener apretado sobre el celular.
*Qué pasa:* el chat se inunda de "NO CORTES" ×100 y la voz robótica lee una andanada de donaciones: "NO." "NO." "NO." **Lauti te pone la mano en el hombro** (empujón de cámara) y te ruega **con tu propia voz**. Un solo mensaje distinto: ***"MamaDeLauti: cortá, nene. dejalo descansar."*** A los 5 s: **APAGÓN.** **Negro absoluto y silencio total durante 5 segundos.** Después, un único *clic* de linterna.
*En cámara:* el silencio es el sonido más fuerte del video. El editor debería dejarlo entero.

**B19: Sting en casa.** Ver "Final" en la sección 7.

### Los 5 mejores clips (para TikTok/Shorts)
1. **B03:** el POV de Lauti te muestra a vos de espaldas y el chat grita "ATRÁS TUYO".
2. **B08:** "Repetición... en cámara lenta" con tu propio grito.
3. **B10:** prender y apagar la cámara frente a la Audiencia (cabezas que giran 180° y "nene, abrigate").
4. **B12:** CAM 12, el Doctor detrás tuyo, jumpscare y escape desde su POV.
5. **B15:** el ascensor cae, el impacto y "¡HOLA CHAT!".
*Reserva:* B05 (la galería que aplaude) y B16 (la selfie).

---

## 6. Momentos de humor

1. **El sorteo (gag recurrente).** Graffiti "LAUTI PAGÁ EL SORTEO", la libreta ("Sorteo (??? ver con Gonza)"), trolls del chat cada pocos minutos ("LAUTI Y EL SORTEO???"), el dron "comprado con la plata del sorteo" y la página 3 cortada a mitad de frase ("el sorteo lo gana..."). **Remate al final:** Lauti, a punto de deshacerse: *"¡Ah! El sorteo. El sorteo lo gana..."*, mira a los pacientes: *"...ofeliaD31."* → ***"ofeliaD31: ¡AY, SÍ!"*** (TTS de viejita). El público se ríe justo antes del momento emotivo.
2. **Gonza_Mod, el moderador que no puede.** Es el único vivo útil. Banea muertos y vuelven: *"Gonza_Mod baneó a ofeliaD31 por 600 segundos"* → *"ofeliaD31: nene, yo ya cumplí mi tiempo"*. *"Gonza_Mod: chicos respeten"*, *"Gonza_Mod: perdón no sé cómo apagarlo"*. Al final: *"Gonza_Mod: se cortó... ¿se cortó? ¿LAUTI?"* y *"gracias, loco. de verdad."*
3. **"Repetición en cámara lenta"** (B08): el jugador escucha su propio grito en cámara lenta por la megafonía. Es humor que el mod genera solo.
4. **La hiperinflación como escenografía:** el menú con precios tachados por hora, las donaciones **en australes** y el Turco: *"en mi época esto costaba dos australes"*.
5. **Don Cacho y el choripán de la morgue:** "Treinta y siete años sin comer y me trae un alfajor." / "Está frío. Pero está bueno." Además, el chat: *"pelusa_10: choripán no era el perro poseído del otro video??"* (gag que cruza todo el video).
6. **Las poses de Lauti:** cada vez que te das vuelta está más cerca **y en una pose más estúpida** (festejo de gol, corazón con las manos). Y la **selfie** con el flash.
7. **"Es el viento, chat":** el latiguillo de Lauti. Lo escribe en la libreta, suena en su voz cuando pasa algo sobrenatural cerca suyo y los trolls lo copian en el chat. Se usa 3 o 4 veces como mucho.
8. **El turnero:** "TURNO 1.990", la megafonía *"Número mil novecientos noventa, pase por Pabellón C"* cuando el Doctor ya te está cazando, y al final, en tu casa, **ding**.
9. **Abuelas del chat:** Pocha ("abrigate", "¿comiste?", "ese muchacho necesita una novia"), Amalia ("qué buen mozo el nuevo") y el **"ups perdón"** al chocarte con un fantasma invisible en la oscuridad.
10. **Los muertos que causan los sustos:** Tito "el mago" anuncia los poltergeist como trucos, Mirta la chusma te vende con el Doctor ("yo no dije nada") y Hugo, muerto, insiste en que "esto es fake".

*Regla de tono:* el humor siempre llega **después** del susto, como liberación, nunca antes. En la Sala 14 y en el apagón **no hay chistes**.

---

## 7. Mecánicas nuevas

### 7.1 App EN VIVO + chat en el HUD
- **App EN VIVO** en el teléfono (se desbloquea en E2). Muestra la transmisión con título, tiempo en vivo ("37d 03:33:xx", corriendo) y el contador de espectadores.
- **Botón VER:** cambia tu cámara al **POV de la entidad Lauti** durante 4 s (`Minecraft.setCameraEntity`; tu cuerpo sigue controlable) con el marco de stream ("● EN VIVO", contador y chat). Cuesta 5 de cordura y tiene un enfriamiento de 20 s. Si Lauti está lejos o descargado: estática y "Reconectando...". Sirve para saber dónde está, y a veces **lo que ve sos vos.**
- **Chat en el HUD:** panel a la derecha, unos 7 renglones de 30% de ancho, que se desvanece. Lo alimenta el servidor con un payload nuevo (`ChatFeedPayload(user, color, text, flags)`).
  - **Pools contextuales** en el lang (`deadline.chat.hospital.<pool>.<n>`): ambiente, oscuridad, grito detectado ("JAJAJA", "se re cagó", "CLIP"), mirar a Lauti ("MIRALO MIRALO MIRALO"), entidad cerca ("ATRÁS TUYO"), cordura baja ("dale una pastilla"), uso de herramientas ("el crucifijo es del todo por dos pesos"), Gonza, trolls ("fake", "primero", "es el viento chat", "VENDO DÓLARES", "saludos desde Rosario").
  - **Límite de ritmo:** como máximo 1 mensaje cada 1,2 s, con ráfagas permitidas para "spam" (20 mensajes en 2 s) y **silencios guionados** (Sala 14).
  - **Después del Giro 2**, los nombres de los muertos **se vuelven gris pálido**: confirmación visual del giro.
- **Donaciones:** un banner animado arriba al centro durante 3 s, con el jingle y el **TTS robótico** (estilo voces sintéticas viejas de internet: em_alex monótono con cuantización de pitch). Se usan como sustos y como aviso de la embestida.

### 7.2 Cámara de Lauti (ítem clave, riesgo y recompensa)
- **Al prenderla (clic derecho):** shader de **visión nocturna verde** (fósforo, ruido, brillo exagerado en las luces) y **"● REC"**. Revela **la Audiencia**, la **tinta IR** (mensajes escondidos en las paredes: "NO MIRES EL CHAT", "14", flechas) y huellas invisibles.
- **Mientras está prendida, ESTÁS EN VIVO:** el contador sube y **cada 12–20 s el chat "chivatea" tu ubicación** ("jaja está en la morgue", "se escondió en el placard"). Esa posición se le pasa a Lauti y al Doctor como punto a investigar.
- **Batería** de 90 s, que se recarga con **powerbanks** (5 escondidos).
- Es un dilema puro: ves más y te ven más.

### 7.3 Cámaras CCTV y monitores
- **Bloque `camara_cctv`:** direccional, con un BlockEntityRenderer cuyo cabezal **rota siguiendo al jugador** a pasos de servo. LED con 5 estados: apagado / mirando / aviso / grabando / rota. Hay unas 32 en el sitio: Pabellón C, pasillos, morgue y central.
- **Formas de anularlas:**
  - **Daga de plata:** 3 golpes, la destruye.
  - **Flash de la Cámara de Espíritus:** a menos de 8 bloques **quema el lente** para siempre.
  - **Agua bendita:** la ciega durante 20 s.
  - **Crucifijo activo** a menos de 3 bloques: la apaga durante 10 s.
- **Monitores (`monitor_crt`)** en la Sala de Observación y en la central. Hacer clic en uno cambia tu vista a esa cámara (shader de CCTV en blanco y negro, rótulo "CAM 07 · PAB C · 1989", timecode). Las flechas cambian de cámara y ESC sale. A través de los monitores **se ve la Audiencia** y al Doctor. Así se descubre la **CAM 14** (la sala que no existe). En coop, uno puede quedarse de **operador de cámaras** guiando al otro por voz.

### 7.4 Llamador de enfermería
Un tablero de 15 lamparitas en el office del 1P. **Una lamparita se prende cuando hay una entidad en esa sala** (incluidas Lauti y la Audiencia). Funciona como un radar sistémico que el jugador aprende a leer. **La 14 siempre está prendida.**

### 7.5 Turnero
Bloque con display de números. Imprime el ticket "Nº 1.990" y avanza solo a lo largo del caso (13 → 400 → 1.200 → 1.989). Al llegar a 1.990, la megafonía te llama al Pabellón C. Combina humor y señal de escalada.

### 7.6 Desfibrilador (ítem del caso, en la Guardia)
3 cargas. Primero suena una carga ascendente y después **"¡DESPEJEN!"** (TTS) y el golpe.
- Sobre Lauti: "reinicio" de 8 s.
- Sobre el Doctor: aturdido 4 s (y 25 de daño cuando es vulnerable).
- **Sobre vos mismo con cordura menor a 30:** +30 de cordura con sacudida de cámara y flash. Humor negro: "auto-desfibrilarse".

### 7.7 Otros elementos
- **Pila de agua bendita** (capilla): recarga el Agua Bendita, 2 cargas por visita.
- **Candado de combinación** del consultorio: 4 dígitos que se giran con clic. Clave **1988**, que aparece en tres fuentes: el libro de la morgue, `ernesto_77` en el chat y los pacientes susurrando la cuenta "...1986, 1987, 1988...". Pista en el pizarrón: "La clave es cuántos se fueron."
- **Pared de yeso fresco:** se rompe en 3 golpes con cualquier ítem. Con UV se ven las manos del otro lado.
- **Secuencia del ascensor:** la cabina es un grupo de BlockDisplay que baja por un riel (`hospital.elevator_fall`). Se guiona para que frene a 1 bloque de tu cabeza si llegás a la escotilla. Si no llegás, te aplasta de mentira: fundido a negro y despertás en el fondo con −30 de cordura y "JAJAJA". No es muerte real.
- **13 pulseras de pacientes** (coleccionables de evidencia): debajo de camas, en cajones de la morgue, en la cafetería, en el techo y en las celdas. Cada una da un nombre real. **Si juntás las 13**, todos se despiden en el chat con su nombre y aparece el título: ***"Los nombraste a todos. Mirar no es lo mismo que recordar."***

### 7.8 Resolución: ancla y boss ("Circuito cerrado")
Arena de 19×19×7: 8 cámaras (CAM 25–32), el celular de Lauti como ancla, la silla con el cuerpo, 4 pilares y luces rojas.

**Fase 1, APAGAR LOS OJOS (0/8).** El Doctor es invulnerable y viaja por cámaras con un enfriamiento de 10 s. Lauti acecha con su regla de siempre y Mirta chivatea. Cada cámara anulada provoca:
- un **tambaleo del Doctor**, con el lente que se raja;
- **una sección de monitores que se apaga**, así que la arena **se oscurece**: el territorio del Doctor se achica y la aureola de Lauti pasa a ser la luz principal, lo que lo mete en el juego;
- unos −250 espectadores en el contador.

Con 6 de 8, el gimbal queda accesible.

**Fase 2, PURIFICAR.** Agua bendita sobre el celular: la pantalla se raja, el HUD muestra "Conexión inestable", el stream tartamudea y **el Doctor se vuelve vulnerable** (lógica de ancla existente). Lauti grita: *"¡NO! ¡SE ME CAE EL STREAM!"*.

**Fase 3, DEBILITAR.** Ahora el Doctor **solo puede caminar en la luz que queda**: las luces rojas, los monitores encendidos y la aureola de Lauti. Se lo daña con el crucifijo, la daga, el agua bendita y el desfibrilador, y se lo ciega con el flash.
- **Al 50%, "Examen":** secuestra tu POV durante 4 s seguidos y hay que pelear y moverse viéndose desde su lente.
- **Al 25%:** se arrodilla frente al celular, protegiéndolo: *"No apague. No apague. Que nadie apague."* En la pantalla aparece **FINALIZAR TRANSMISIÓN**.

**Fase 4, FINALIZAR TRANSMISIÓN.** Mantener apretado 5 s sobre el celular, con un anillo de progreso y el texto **"¿Finalizar transmisión? 1.990 espectadores"**.
- Mientras tanto, **la regla de Lauti se rompe**: avanza despacio aunque no lo mires, te pone la mano en el hombro y ruega **con tu voz** (y con la suya: *"no cortes... si cortás me voy... no cortes"*).
- El chat pide que no cortes y solo **MamaDeLauti** dice que cortes.
- Si soltás, Lauti retrocede y se reinicia. Esto pasa una sola vez; el segundo intento no se puede interrumpir.

**Apagón.** Negro y silencio absolutos durante 5 s y después el clic de la linterna.
- **La carcasa de la cámara del Doctor cae al piso con un CLONK.** Queda un viejito diminuto con los ojos cosidos, arrodillado: *"No me dejen de mirar... no me dejen solo..."*
- **Objetivo:** atraparlo en el **Frasco de Almas** (dentro queda brillando **una lucecita tally roja**) o **exorcizarlo** con el Libro de Rituales.

**Éxodo y final.**
- Lauti se sienta en el piso junto a su cuerpo y se saca los auriculares: *"¿Se cortó?... Bueno."* Pausa. *"Gracias por mirar, chat."* Después llega el remate del sorteo ("...ofeliaD31" / "¡AY, SÍ!") y se deshace. Su aureola cae y se apaga.
- La escalera principal aparece **despejada**. Los 13 suben con vos, sin apuro, hasta el hall. **La cadena de la puerta principal está rota.** Cada paciente asiente en la puerta y se desvanece. El último es el Nene, que deja la caja. Cacho saluda desde la garita: "Ya me relevaron."
- Afuera, **tinte de amanecer** en el cielo y la niebla (lado cliente).
- Título final:

> **TRANSMISIÓN FINALIZADA**
> Duración: 37 días · Espectadores: 0

**Sting en casa (B19).** El teléfono vibra: *"MamaDeLauti está en vivo · 1 espectador"*. Al abrirlo se ve un único mensaje: ***"gracias, nene. ya lo llevo a casa."*** **Opción oscura** (para cerrar el video con un último susto, activable por comando): suena el turnero desde algún lugar de tu casa, **"DING: TURNO 1.991"**.

**Recompensas:** $1.600, **Caja del Nene** (trofeo), **Ring light de Lauti** (bloque de luz decorativo), **frasco con el tally del Ojo** y entrada del bestiario.

### 7.9 Herramientas existentes en este caso
| Herramienta | Uso en el caso |
|---|---|
| **Crucifijo** | Repele a Lauti y al Doctor. Cerca de una cámara, la apaga 10 s. Bea reza en el chat. |
| **Agua Bendita** | **Purifica el ancla.** Raja el lente del Doctor (5 s), pone a Lauti en buffering (4 s) y ciega cámaras (20 s). Se recarga en la capilla. |
| **Sal** | Frena a Lauti, a la camilla y la caminata del Doctor, pero **no** su viaje por cámaras. Las líneas de sal son muros invisibles para la Audiencia: se los ve "amontonados" contra la sal con la cámara. |
| **EMF** | Nivel 3 cerca de cámaras activas, nivel 5 cerca del Doctor y **siempre 5 cerca del celular de Lauti** (te guía hacia abajo). |
| **Linterna / UV** | La luz normal **acelera a Lauti si lo iluminás** (le das "vistas"). El UV revela las flechas de Lauti, las manos en el yeso, el "7" que Cacho marcó en el cajón y las huellas en las puertas del ascensor. |
| **Spirit Box** | "¿Dónde está Lauti?" → *"abajo"* / *"en la silla"*. "¿Quién me llamó?" → ***"mamá"*** (adelanta el giro). "¿Cuántos son?" → *"mil novecientos ochenta y ocho"*. "¿Qué querés?" → *"que mires"*. **"¿Estás vivo?" → *"en vivo"*** (juego de palabras central del caso). Aleatorias: *"suscribite"*, *"apagá"*, *"no cortes"*. |
| **Cámara de Espíritus** | Flash: **selfie** de Lauti, **sobreexposición** del Doctor (8 s) y **quema el lente** de las cámaras. Las fotos revelan a la Audiencia. |
| **Libro de Rituales** | Final alternativo: exorcizar al Doctor. |
| **Frasco de Almas** | Final principal: atrapar al Doctor. |
| **Pastillas** | Cordura (2 en la farmacia y 1 en la Sala 14). |
| **Rosario** | En la mano, reduce a la mitad el secuestro de POV del Doctor. |
| **Bengalas** | **Señuelo para Lauti** (va a "posar" a la luz 10 s). ¡Cuidado!: crean luz y por lo tanto **territorio del Doctor**. |
| **Velas rituales** | Zona segura frente a la Audiencia y a Lauti, pero también son luz: el Doctor sí puede entrar. Es una decisión táctica. |
| **Daga de plata** | Rompe cámaras y daña al Doctor cuando es vulnerable. |

---

## 8. Imitación de voz (Simple Voice Chat)

### Usos en el caso
1. **"Repetición"** (B08, la estrella). Se detecta tu grito y después la megafonía lo repite a velocidad normal y **en cámara lenta** (remuestreo a 0,6 con el pitch más grave). Locación: parlantes del pasillo, lejos tuyo, así se oye tu propio grito en otra parte del hospital. En coop, el compañero lo escucha y cree que sos vos.
2. **Eco del pasillo largo y de la morgue.** Lo que decís vuelve con 2,5 s de retardo, más bajo y desde el fondo del pasillo. A la tercera vez **el eco se desincroniza** y devuelve algo que dijiste **hace 10 minutos**.
3. **Cajón 14** (B09): una frase corta tuya, ahogada (pasa-bajos) desde adentro del metal.
4. **Lauti habla con tu voz:** en el ascensor ("¡HOLA CHAT!" reemplazado por tu frase más fuerte), en sus apariciones de acecho (frases cortas de 1–3 s desde su posición) y **en el ruego final**.
5. **"Tu primera frase":** en la Sala de Observación, **CAM 15** reproduce como "grabación de archivo" **lo primero que dijiste al llegar al caso** (los primeros 10 s de voz). El hospital lo graba todo.
6. **El Nene te imita** con tu voz aguda (+5 semitonos): *"¿Me mirás?"* con tu timbre.
7. **Coop: señuelos cruzados.** El jugador B escucha la voz de A desde otra sala (lo último que A le dijo), y el teléfono de B suena con el nombre de A en pantalla: al atender, un clip de A (canal estático solo para B).
8. **Fallback sin SVC:** se usan las líneas TTS de Lauti y los clips genéricos. Todo el caso funciona igual, con menos magia.

### Implementación (API de servidor de Simple Voice Chat, dependencia opcional)
- `compileOnly "de.maxhenkel.voicechat:voicechat-api:2.5.x"` (repo `maven.maxhenkel.de/repository/public`) y la entrypoint `"voicechat"` en `fabric.mod.json` con una clase `VoicechatPlugin`. Todo detrás de `FabricLoader.isModLoaded("voicechat")`.
- **Captura:** `MicrophonePacketEvent`, de donde salen `getSenderConnection().getPlayer()` y `getPacket().getOpusEncodedData()`. Se usa un **buffer circular por jugador de unos 90 s** (tramas opus de 20 ms, unos 4.500 paquetes y menos de 300 KB). Se decodifica cada trama con `api.createDecoder()` para medir RMS y pico.
- **Segmentación (VAD):** hay voz si el nivel supera −45 dBFS. La frase termina tras 15 tramas en silencio (300 ms). Cada clip se guarda con duración, pico, RMS, sala (volumen del sitio) y etiqueta: **grito** (pico mayor a −6 dBFS, más de 400 ms), **frase** (0,6–3 s) o **susurro** (RMS bajo con voz).
- **Reproducción:** se decodifica a PCM, se aplica DSP (pasa-bajos para el cajón, remuestreo para cámara lenta o voz de nene, banda 400–3.000 Hz + saturación + reverb de peine para la megafonía) y se reproduce con `api.createAudioPlayer(channel, api.createEncoder(), supplier)`. Canales:
  - `createEntityAudioChannel` para Lauti y el Nene;
  - `createLocationalAudioChannel` para la megafonía, el cajón y el eco, con `setDistance(24–48)`;
  - `createStaticAudioChannel` para la "llamada" en coop.
  
  Además se registra una categoría de volumen **"DEAD LINE — Imitaciones"** para que cada jugador la regule.
- **Consentimiento y privacidad:** al entrar al caso por primera vez aparece el cartel *"Este caso usa tu micrófono (Simple Voice Chat) para imitarte. Nada se guarda en disco."* Hay un comando `/deadline mimic off`. Los clips viven solo en RAM y se descartan al terminar el caso. **Opcional para el creador:** `/deadline mimic export` escribe WAVs **solo de la voz del host** en `deadline_clips/` para usar en la edición. Los clips del compañero se exportan solo si él ejecutó `/deadline mimic share on`.

---

## 9. Sonidos, ítems, bloques y texturas

### 9.1 Sonidos nuevos (unos 45 eventos y 75 archivos; TTS Kokoro + DSP, o síntesis)
| ID | Descripción | Fuente |
|---|---|---|
| `ambient.hospital` | Loop: goteos, zumbido de fluorescente lejano, viento por ventanas rotas, una silla de ruedas que cruje lejos, dron grave de 40 Hz. | Síntesis |
| `music.stream_bgm` | La música lo-fi del stream de Lauti, desafinada y lenta, **posicional en Lauti** (indica cercanía). | Síntesis |
| `hospital.fluor_buzz` / `fluor_flicker` / `fluor_pop` | Hum de 50 Hz con tic de arrancador, parpadeo y tubo que revienta. | Síntesis |
| `hospital.balizas` | Relé de balizas "tic... tac". | Síntesis |
| `hospital.radio_1989` | Boletín de AM (em_alex con filtro de radio de AM), fragmento de cumbia original, sintonía con estática y la voz "¿estás en vivo?". | TTS + síntesis |
| `hospital.turnero` / `ticket_print` | "Ding-dong" con dígitos que pasan, e impresora térmica. | Síntesis |
| `hospital.pa_chime` | Campanita de 3 notas de megafonía de los 80, con reverb. | Síntesis |
| `hospital.pa_voice` (×5) | ef_dora con filtro de megafonía: "Número mil novecientos noventa, pase por Pabellón C" · "Doctor Mendizábal, se lo solicita en quirófano dos" · "El horario de visita ha finalizado" · "Repetición" · "Repetición en cámara lenta". | TTS |
| `hospital.heart_monitor_beep` / `flatline` | Bip y plano. | Síntesis |
| `hospital.surgical_lamp` | Clonk + zumbido de lámpara potente. | Síntesis |
| `hospital.applause` | Aplauso lento y espaciado de 13 personas en una sala chica. | Síntesis por capas |
| `hospital.gurney_roll` / `gurney_crash` / `sheet_flap` | Rueda que chilla (con el pitch según la velocidad), choque metálico y sábana. | Síntesis |
| `hospital.nurse_call` | Chicharra del llamador. | Síntesis |
| `hospital.morgue_drawer` / `morgue_knock` | Cajón pesado de metal deslizándose y golpes huecos desde adentro. | Síntesis |
| `hospital.newspaper` | Papel de diario al desenvolver el choripán. | Síntesis |
| `hospital.plaster_break` | Yeso que se rompe. | Síntesis |
| `hospital.gate_unlock` / `combo_lock` | Reja de hierro y clics del dial con apertura. | Síntesis |
| `hospital.elevator_ding` / `elevator_snap` / `elevator_fall` / `elevator_impact` | Ding (cuando no debería andar), twang de cable, chirrido de rieles e impacto masivo. | Síntesis |
| `hospital.crt_on` | Silbido agudo de CRT + estática + desmagnetización. | Síntesis |
| `hospital.tape_insert` / `tape_play` | Mecánica U-matic con motor. | Síntesis |
| `tape.doctor_1974` / `tape.c13` / `tape.apagon` / `tape.lauti` | Las 4 cintas (ver la sección 3). | TTS em_santa / ef_dora / em_alex + DSP de VHS |
| `chat.pop` | Tic sutil de mensaje entrante. | Síntesis |
| `chat.donation` | **Jingle de donación** original (arpegio de 8 bits ascendente + moneda). Tiene que ser icónico. | Síntesis |
| `chat.tts` (×8) | Voz robótica monótona: "ofeliaD31 donó cincuenta australes: qué lindo que vino otro" · "pelusa_10 donó cien australes: CORRÉ" · "Gonza_Mod donó mil pesos: perdón, no sé cómo apagarlo" · "nn_13 donó cero pesos: atrás tuyo" · "anónimo donó: mirá arriba" · "NO" · "pochamedina donó: comé algo, nene" · "DIRECCIÓN donó: paciente C-15, presentarse". | TTS + cuantización de pitch |
| `chat.raid` | Fanfarria de raid desafinada. | Síntesis |
| `stream.pov_in` / `pov_out` / `live` / `end` | Encendido de CRT, estática, sting de "EN VIVO" y golpe sordo de apagado seguido de silencio. | Síntesis |
| `lauti.hola_chat` | "¡Hola chat! ¡Hola, hola, hola!" con tartamudeo de lag. | TTS em_alex con pitch alto + glitch |
| `lauti.es_el_viento` | "Es el viento, chat." | TTS |
| `lauti.laugh` / `lauti.buffer` | Risa de stream con glitch en loop y bucle de buffer entrecortado. | TTS + DSP |
| `lauti.suscribite` | Grito distorsionado "¡SUSCRIBITE!" (jumpscare). | TTS + distorsión |
| `lauti.step_lag` | Pasos que se repiten con lag. | Síntesis |
| `lauti.selfie` | "¡Foto!" + obturador. | TTS |
| `lauti.ringlight_hum` | Zumbido agudo del ring light (posicional). | Síntesis |
| `lauti.se_me_cae` | "¡NO! ¡SE ME CAE EL STREAM!" | TTS |
| `lauti.beg` / `lauti.final` / `lauti.sorteo` | "No cortes... si cortás me voy..." · "¿Se cortó?... Bueno. Gracias por mirar, chat." · "El sorteo lo gana... ofeliaD31." | TTS sin glitch al final (es su voz humana) |
| `ojo.servo` / `ojo.zoom` / `ojo.tally` | Servo de paneo con pasos "zzt-tic" (sonido firma), motor de lente y relé. | Síntesis |
| `ojo.transfer` | Ráfaga de estática + "BWOOM". | Síntesis |
| `ojo.voice` (×4) | em_santa lento: "Paciente C-15. Ingreso." · "Mientras alguien mire, nadie se va." · "No apague." · "Lo estoy mirando." | TTS + DSP |
| `ojo.grab` / `ojo.hurt` / `ojo.crack` / `ojo.fall` / `ojo.sob` | Agarre, vidrio que se raja con chillido eléctrico, carcasa que cae y el llanto del viejito: "no me dejen de mirar". | TTS + síntesis |
| `audiencia.count` | Susurros contando "...mil novecientos ochenta y seis, ochenta y siete, ochenta y ocho...". | TTS por capas |
| `audiencia.necks` | Muchos cuellos crujiendo a la vez (capas de `poseida.crack`). | DSP |
| `audiencia.bump` | Respiración cercana + "ups perdón" (Pocha). | TTS |
| `audiencia.goodbye` | Coro suave de despedida, casi un suspiro. | Síntesis |
| `nene.me_miras` / `nene.giggle` | Voz de nene íntima. | TTS ef_dora con pitch alto |
| `cacho.voice` (×6) / `cacho.mate` / `cacho.chew` | Líneas de Cacho, **sorbo de mate con bombilla** y masticada. | TTS em_alex mayor + síntesis |
| `norma.call` / `norma.gracias` | Mensaje de la llamada y "gracias por ir". | TTS ef_dora suave y mayor |
| `ofelia.ay_si` | "¡AY, SÍ!" de viejita. | TTS |
| `defib.charge` / `defib.shock` / `defib.despejen` | Carga ascendente, golpe con zap y "¡DESPEJEN!". | Síntesis + TTS |
| `cam.on` / `cam.off` / `cam.battery_low` | Bips de la cámara de acción. | Síntesis |
| `cctv.break` | Vidrio que se rompe + chispa. | Síntesis |

### 9.2 Ítems nuevos
`camara_lauti` (cámara con visión nocturna; estado REC; batería) · `celular_lauti` (**ancla**: pantalla rajada y "1%") · `desfibrilador` (3 cargas) · `llave_pabellon_c` · `llave_bombero` · `choripan_sereno` (envuelto en diario; si te lo comés: náusea 10 s y −10 de cordura, y en el chat *"NOOO ERA DE CACHO"*) · `pulsera_paciente` (13 variantes por componente) · `cinta_umatic` (4) · `libreta_lauti` (3 páginas, libro escrito) · `diario_mendizabal` (libro escrito) · `ficha_c14` y `ficha_c15` (papel con pantalla de texto; la C-15 inserta el nombre del jugador) · `numero_turno` ("Nº 1.990") · `powerbank` · `bebida_energizante` (velocidad 20 s + temblor de mano) · `caja_del_nene` (trofeo, se puede usar en la cabeza) · `ring_light` (trofeo, bloque de luz).

### 9.3 Bloques nuevos
`camara_cctv` (direccional, con BlockEntityRenderer rotatorio y LED de 5 estados) · `monitor_crt` (apagado / estática / en vivo / partido / texto; textura emisiva animada) · `turnero` (display numérico) · `llamador_enfermeria` (lamparita numerada) · `cajon_morgue` (abierto/cerrado, con contenido) · `pared_yeso` (rompible) · `cartel_salida` (verde emisivo, luz 4) · `tubo_fluorescente` (encendido / apagado / parpadeo; panel de techo) · `lampara_quirurgica` · `negatoscopio` (emisivo) · `luz_emergencia` (roja, giratoria con BlockEntityRenderer) · `consola_soc` (perillas y LEDs) · `candado_combinacion` (4 dígitos) · `silla_ruedas` y `pie_suero` (modelos JSON decorativos).

### 9.4 Cuadros (variantes `painting_variant` data-driven)
Radiografías ×3 (una normal, una **con un celular en las costillas**, una con **un cráneo con lente**) · dibujos de pacientes ×4 (el doctor con cabeza de cámara; 13 palitos mirando la tele; un ojo gigante; "NO ME MIRES") · **foto de Norma** · **miniatura de Lauti** ("24 HS EN EL HOSPITAL... (REAL) (NO FAKE)" con flecha y círculo rojos) · afiche "SE BUSCA" de Lauti · **afiche "SE BUSCA: CHORIPÁN"** · diploma de Mendizábal · pared de polaroids de ojos (3×2) · reloj en 03:33 · plano de evacuación sin la Sala 14.

### 9.5 Texturas de entidades y de interfaz
- **Entidades:** Lauti (normal + cuerpo momificado), Ojo (+ cabeza de viejito), Audiencia (base + 12 overlays de variante), Nene de la Caja, Camilla, Don Cacho (translúcido) y Dron (P2).
- **Retratos de jumpscare:** `lauti` (cara de miniatura con el resplandor del ring light), `ojo` (primerísimo plano del lente con el ojo humano) y `nene` (la caja con la sonrisa dibujada llenando la pantalla).
- **Shaders de postproceso:** `cctv` (blanco y negro, alto contraste, scanlines, viñeta y rótulo con timecode) y `nightvision` (fósforo verde, bloom en las luces, ruido y "● REC").
- **HUD y teléfono:** panel de chat, punto rojo "EN VIVO" con contador e ícono de ojo, banner de donación, badges (espada de MOD, ícono de streamer), batería de la cámara, ícono de la app EN VIVO y avatares de llamada (Norma, Gonza y Lauti con glitch).
- **Partículas:** **spinner de carga** (puntos blancos en círculo), chispas de estática, vapor del mate y neblina fría.
- **Lang:** unas 250 claves (chat, donaciones, notas, objetivos, Spirit Box, bestiario).

### 9.6 Bestiario (texto)
- **LAUTI EXTREMO, Paciente C-14:** "Streamer. 37 días en vivo. Se alimenta de miradas: cuanto más lo mirás, más cerca está. No lo mires. Si te saca una foto, posá vos también."
- **EL OJO, Dr. Aurelio Mendizábal:** "Director del Pabellón C (1974–1989). Viaja por las cámaras y solo existe en la luz. Le tiene miedo a una sola cosa: que nadie lo mire."
- **LA AUDIENCIA:** "Los 13 del Pabellón C. No te hacen nada. Solo miran. Querían que alguien los recordara, no que los vigilaran."

---

## 10. Minutos de video y ritmo

**Objetivo: unos 7 minutos editados** de los 20 (es el caso más largo porque cierra el video). **Grabación cruda estimada: 55–75 min** (más las tomas repetidas con los comandos de director).

| Minuto (editado) | Bloque | Energía |
|---|---|---|
| 0:00–0:30 | Llamada de Norma, balizas en la niebla, radio de 1989 | Intriga |
| 0:30–1:15 | Turnero, Guardia, equipo y **primer POV: "atrás tuyo"** (CLIP 1) | Primer pico |
| 1:15–2:15 | 1er piso: la galería que aplaude, la camilla, primera donación, **"Repetición"** (CLIP 2) | Susto y risa alternados |
| 2:15–3:00 | Don Cacho, morgue, cajón 14 con tu voz, choripán | Valle cómico (respiro) |
| 3:00–4:15 | Pabellón C iluminado: **la Audiencia** (CLIP 3), silla 15, candado 1988, **CAM 12** (CLIP 4) | Escalada fuerte |
| 4:15–4:50 | **Sala 14:** el chat se calla y aparece la mamá (Giro 1) | Emoción, silencio |
| 4:50–5:20 | El pozo: **"¡HOLA CHAT!"** (CLIP 5) | Pico |
| 5:20–6:40 | Boss: raid, apagar cámaras, selfie, purificar, debilitar, **FINALIZAR TRANSMISIÓN**, apagón, viejito, frasco | Clímax |
| 6:40–7:10 | "Gracias por mirar, chat", el sorteo, el éxodo, Cacho, título final y casa | Catarsis, risa y lágrima |

**Curva:** alternar un susto y una risa cada unos 45 s hasta el minuto 4, y después **quitar el humor** en la Sala 14 y en el apagón para que el final golpee. Recomendación para la edición: **no musicalizar** el apagón y dejar los 5 segundos de negro enteros.

---

## 11. Extras para el rodaje

**Comandos de director**, para repetir tomas y no depender de la suerte:
- `/deadline beat hospital <B01..B19>` dispara un beat;
- `/deadline stage hospital <n>` salta a una etapa;
- `/deadline chat <usuario> <texto>` inyecta mensajes propios para chistes en la edición;
- `/deadline donate <usuario> <monto> <texto>` dispara una donación con TTS;
- `/deadline viewers <n>`;
- `/deadline mimic on|off|export`;
- `/deadline pov <lauti|ojo|camN>`.

**Fans en el chat (idea para el canal):** un archivo `config/deadline/chat_fans.txt` con nombres de suscriptores **que pidieron aparecer** (por ejemplo, "comentá para salir en el chat del próximo video"). Se usan como los trolls vivos. Genera mucho engagement y no toca a nadie sin permiso.

**Coop con un amigo:**
- **Rol "operador de cámaras":** se queda en la Sala de Observación y guía por voz al otro, que va con la cámara de Lauti. Si mira la misma cámara mucho tiempo, el Doctor lo detecta a él ("él también te mira a vos").
- Las imitaciones de voz cruzadas son el material más gracioso del coop.

**Prioridades de construcción:**
- **P0:** dimensión y sitio; chat en el HUD + app EN VIVO + POV; Lauti (regla invertida, selfie, embestida por donación); el Ojo (cámaras, secuestro de POV, internación); la Audiencia (render solo con cámara); bloques CCTV y monitores; las 4 fases del boss; el apagón y el éxodo; sonidos clave; imitación de voz ("Repetición" y la voz de Lauti).
- **P1:** camilla, Cacho, cajones de la morgue, ascensor, yeso, candado, cintas, revelación con relámpagos, Nene y desfibrilador.
- **P2:** dron, baño del espejo, Archivo Muerto, despedidas por pulsera, archivo de fans y sting oscuro.

**Riesgos a cuidar:**
- **Legibilidad del chat en video:** fuente grande, 7 renglones como máximo y silencios guionados.
- **Desorientación por POV:** 6 s como máximo y marco siempre claro.
- **Jumpscares:** no más de 3 de pantalla completa en todo el caso.
- **Ficción:** todo inventado (hospital, pueblo, streamer y plataforma). Sin parecido con streamers reales ni con hospitales abandonados reales.
