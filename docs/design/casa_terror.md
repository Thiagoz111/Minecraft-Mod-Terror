# CASA MORALES v2 — "ELLA ESCUCHA TODO"

Rediseño de terror (23/10/2026). Reemplaza las secciones 2.2.c–2.2.n de `BIBLIA.md` y todo `casa_mecanicas.md`
(lo que no se nombre acá como reutilizado, se considera cortado). Este documento manda sobre cualquier otro.

## 0. Pilares (no negociables)

1. **Terror, no comedia.** Adulto: sangre, deformaciones, posesión, jumpscares ganados. Nada de gags, nada de "momentos
   graciosos" diseñados. El nombre del perro (Choripán) queda como la única ironía, y se usa para que duela.
2. **Sin misiones.** No hay objetivos en pantalla, ni checklist, ni "andá a X". La historia avanza sola y empeora.
   El jugador explora, se esconde, sobrevive. La casa lo empuja (puertas que se cierran, luces que se apagan, rastros).
3. **Sin diálogos hablados.** Ningún personaje habla. Toda la historia se cuenta con: mensajes de texto al celular,
   el entorno (fotos, cuadernos, escrituras en paredes), y lo que los personajes HACEN. Sonidos no verbales sí
   (respiración, risitas, gritos, gemidos, rezos ininteligibles al revés, huesos crujiendo).
4. **Justificación diegética del silencio: "ELLA ESCUCHA TODO".** La familia no habla porque la Nona escucha. Marta te
   escribe por WhatsApp aunque esté parada a dos metros tuyo. El jugador también tiene que callarse: el micrófono
   (Simple Voice Chat, sistema `Voice` ya existente) y el ruido (correr, puertas, objetos) la atraen.
5. **El mundo real.** La casa existe en el overworld del jugador. Se llega manejando. Al terminar sigue ahí.
6. **Nunca dos partidas iguales.** Un director de terror dinámico elige eventos al azar por tensión, lugar y momento;
   los set pieces fijos son pocos y marcan la progresión.
7. **Ritmo de película:** calma inquietante → grietas → escalada → cacería → descenso → final. Picos y valles:
   después de un susto grande, 40–90 s de silencio tenso. El silencio también asusta.

Referencias que se usan sin vergüenza: *El Conjuro* (palmadas, el ropero, sábanas), *Hereditary* (la cabeza, la
figura en el rincón oscuro, el chasquido de lengua → acá el chasquido de dentadura), *El Exorcista* (la caminata
araña por la escalera, la cabeza que gira), *Poltergeist* (la torre de sillas), *Aterrados* (el chico en la mesa,
el hombre debajo de la cama, ruidos en las paredes), *Sonríe* (las sonrisas de copia), *P.T.* (el pasillo que se
repite, el nene en la radio, la heladera), *Paranormal Activity* (la puerta que se mueve sola mientras dormís),
*It Follows* (lo que se acerca cada vez que no mirás), *Granny / Outlast* (escondites, escuchar), el creepypasta
del "Perro largo" (Trevor Henderson), *Insidious* (la figura detrás del hombro, la cara roja), *Gerald's Game*
(el visitante quieto en la oscuridad).

## 1. Cambios globales del mod (aplican a los dos casos)

| Cambio | Detalle |
|---|---|
| Borrar voces | Todas las líneas TTS de personajes (`sounds/line/*`, `lines.json`, eventos `line.*`, subtítulos de habla, `LineBook`, `Run.say` pasa a no hacer nada y devolver 0). Quedan los sonidos no verbales. La imitación de la voz DEL JUGADOR (SVC) se queda: es un evento de terror ("la casa te imita"). |
| Llamadas → mensajes | Se borra el sistema de llamadas (ring, atender, operadora, `incomingCall`, `PendingCall`, `callLine/noticeLine`). El celular recibe **mensajes de texto** (hilos tipo WhatsApp) con vibración + tono corto + toast arriba a la derecha. Los casos se aceptan desde el hilo ("Aceptar caso"). Mensajes pueden traer **foto** (textura). |
| Monja imponente | Sor Agonía mide ~2,6 bloques visuales (el jugador 1,8). Hitbox 0,7×1,95 para que pase puertas; bajo techo de menos de 3 bloques se encorva (lerp) — la encorvada vende el tamaño. Brazos y dedos más largos en proporción. |
| Sin HUD de misiones | Sin checklist ni objetivos en Casa. (El Colegio se rehace después con este mismo motor.) |

## 2. Estructura del caso (25–35 min de video)

La progresión es por **actos**. Cada acto tiene duración mínima/máxima y un "gatillo de avance" (tiempo, lugar,
cantidad de sustos vividos). No se le dice al jugador nada: la casa cambia.

### Acto 0 — El mensaje (casa del jugador, ~1 min)
- Al terminar el Colegio (o con `/deadline start casa`): el celular vibra. Hilo nuevo **"Marta Morales"**:
  1. "Buenas noches. El padre Ignacio me dio su número."
  2. "Es mi suegra. Ya no es ella."
  3. "Por favor venga esta noche. No llame. NO LLAME. Ella escucha todo."
  4. [foto] pasillo oscuro, al fondo una vieja de espaldas, demasiado alta (`msg_foto_pasillo`).
  5. "Le mando la ubicación."  → [ubicación] (botón **Aceptar caso**).
- Al aceptar: aparece **el auto** (Renault 12 gris, abollado, rosario colgando del espejo) a 4 bloques, y el
  celular/HUD muestra GPS (flecha + distancia). La hora del mundo se va llevando al anochecer.

### Acto 1 — El viaje (2–4 min)
- Manejás por el mundo real hasta el sitio (150–400 bloques, en una llanura buscada por bioma).
- Radio del auto: estática, y entre la estática un nene cantando una canción de cuna (sin palabras, tarareo).
- Evento fijo: a mitad de camino, en los faros, **Choripán parado en dos patas en medio del camino, de espaldas**.
  Parpadeo de faros, ya no está. (Si el jugador no mira, se repite más adelante).
- Mensaje de Marta: "¿Ya viene?" ... (30 s) "Apague las luces del auto cuando llegue."
- Al llegar (radio 30 bloques): la calle con un farol que titila, la casa con UNA luz prendida arriba.

### Acto 2 — La llegada (2–3 min)
- Estacionás. Golpeás la puerta (click derecho en la puerta: tres golpes). Silencio. Golpeás de nuevo.
- Pasos lentos adentro. Cerrojo, dos vueltas. La puerta se abre sola despacio: **la Nona** en el umbral, a
  contraluz, cara en sombra, andador. Te mira 4 s sin parpadear. Sonríe (dentadura demasiado blanca). Se corre a un
  costado sin dejar de mirarte, la cabeza la sigue un poco más de lo que debería.
- Entrás. La puerta se cierra detrás tuyo. Cerrojo. **No se vuelve a abrir hasta el final** (la reja de las
  ventanas tampoco deja salir). Mensaje de Marta: "No la deje sola con los chicos."
- La familia está en el comedor, cenando en silencio: Marta, Jorge, Lucía (12), Toti (6). Nadie habla. Marta te mira,
  baja la vista al celular, y te llega: "No hable. Siéntese." La Nona se sienta en la cabecera. Choripán debajo de
  la mesa, gruñendo bajito hacia la Nona.

### Acto 3 — La primera hora (5–7 min, tensión 1–2)
- Libre. La familia hace rutinas silenciosas (lavar platos, tele, Toti dibujando). Eventos aleatorios suaves.
- Lore para el que mira: fotos de 1961, la Nona de nena con una sotana de cura al lado, el cuaderno de Lucía
  ("MI AMIGO SE LLAMA LEMAZA", "LEMAZA DICE QUE LA NONA ES SUYA"), cartas del padre Anselmo, rosarios rotos.
- **El perro que mira** (motivo recurrente): Choripán parado en dos patas en el fondo del patio, mirando la casa.
  Cada vez que lo perdés de vista aparece más cerca (patio → ventana → pasillo → al pie de tu cama).
- Mensajes de Marta: "Lucía no duerme hace 9 días." "La escucho hablar de noche con alguien en el ropero."
- Avance: a los 6 min o al subir a la planta alta → **Acto 4**. La familia se va a dormir: Marta te deja el cuarto de
  huéspedes señalando la puerta. Apagón general (tablero del lavadero: se puede volver a subir; dura poco).

### Acto 4 — La noche (6–9 min, tensión 2–4)
- Casa a oscuras: linterna. Los eventos suben de nivel: puertas, sillas, sombras, sangre, apariciones.
- Set pieces (orden aleatorio, cada uno una vez): **Lucía en el techo**, **Jorge sonámbulo con el cuchillo**,
  **los golpes del ropero de Toti**, **la torre de sillas**, **la Nona rezando de espaldas en el pasillo**.
- Mensajes cada vez más rotos: "Jorge no está en la cama." / "Lucía no está en la cama." / "¿Usted está en el
  pasillo?" / "No es usted el que está en el pasillo." / mensajes de un número desconocido sin texto, solo `...`.
- Avance: a los 8 min o con 5 sustos grandes vividos → **Acto 5**.

### Acto 5 — La cacería (5–8 min, tensión 4–5)
- La Nona se transforma (set piece **"La Nona se rompe"**): en la cocina, de espaldas; huesos que crujen, el cuello
  gira 180°, la mandíbula se descuelga, se alarga hasta casi tocar el techo y baja a cuatro patas (caminata araña).
- Desde acá **ella caza**: no ve bien (cataratas) pero escucha todo: micrófono, correr, puertas, objetos que tirás,
  linterna haciendo click. Patrulla, revisa escondites, abre roperos. Si te agarra: jumpscare y te desmayás (fade);
  te despertás atado a la cama de tu cuarto, sangre en la boca, ciego y mareado unos segundos (fail-forward, sin game
  over).
- Te escondés: roperos, debajo de las camas, la despensa, la bañadera con la cortina. Adentro: rendijas, latido,
  **contener la respiración** (tecla; 8 s como máximo, después jadeás fuerte y ella te oye) cuando ella está cerca.
- El resto de la familia ya no es la familia: **copias** que sonríen demasiado, paradas en rincones, que giran la
  cabeza para seguirte. Marta te escribe desde OTRO lugar: "Estamos encerrados en el sótano. No sé quién está arriba."
- Avance: sobrevivir 6 min, o ser agarrado 2 veces → **Acto 6**.

### Acto 6 — El sótano (3–5 min)
- La casa abre UN camino: todas las puertas se cierran de golpe salvo las que llevan al sótano; huellas de pies
  descalzos con sangre, velas que se prenden solas al pasar. La pared rajada del sótano está rota desde adentro.
- **El cuarto de 1961**: piso de arena, cama de hierro con correas, círculo de sal viejo, estola del padre Anselmo,
  rayones en la pared: LEMAZA LEMAZA LEMAZA. La familia entera parada de cara a la pared, inmóvil. Ofelia (la
  muñeca) sentada en la cama. Cuando entrás: todos giran la cabeza 180° a la vez. Apagón.
- Linterna: la Nona colgando del techo como una araña encima tuyo. Grito. Corrida final hacia arriba (la casa se
  "estira": el pasillo de la planta baja se repite dos veces, estilo P.T.) hasta la puerta de entrada, que AHORA
  está abierta.

### Final
- Salís a la calle. Amanece (cielo gris). La casa a oscuras. Subís al auto. Silencio.
- Mensaje de Marta: "Gracias por venir." ... "Ya somos todos." → [foto] la familia en el cuarto de 1961, sonriendo,
  y en el medio de la foto **vos** (skin del jugador) con los ojos en blanco.
- Arrancás. El espejo retrovisor: la Nona sentada en el asiento de atrás. Jumpscare final, corte a negro,
  "DEAD LINE". Créditos. La casa queda en el mundo (de día, vacía; de noche, una luz arriba).

## 3. La casa v2: "la casona de los Morales"

Más grande que la v1: una casona de 1952 en un lote de 46×56, dos plantas + altillo + sótano, ~22 ambientes,
**dos escaleras** (principal y de servicio) para que la cacería tenga loops. Pensada para esconderse y para sustos.

- **PB:** hall de entrada con perchero y espejo grande; living (TV de tubo, sillón de Jorge, mecedora); comedor (mesa
  de 8, aparador con platos); cocina (alacenas, heladera vieja, mesada, cuchillos); despensa (escondite); lavadero
  (tablero); baño PB; cuarto de la Nona (cama, altar con estampitas, mecedora, ropero grande); costurero (máquina
  Singer, maniquí, ovillos); escritorio del Nono muerto (cerrado al principio, se abre solo en el Acto 4: escritorio,
  fotos de 1961, rosarios); pasillo largo; escalera principal; escalera de servicio (cocina → 1P).
- **1P:** pasillo largo con lámparas cada 4 bloques y 6 puertas (cascada de portazos); cuarto de Lucía (cama, estante
  de muñecas, ropero); cuarto de Toti (cama, cajón de juguetes, ropero con persianas = escondite); matrimonial (cama,
  ropero de 3 puertas, tocador con espejo); cuarto de huéspedes (el del jugador: cama, ropero); baño grande
  (bañadera con cortina = escondite, espejo, botiquín); balcón al frente; cuarto cerrado (del Nono, intacto, polvo).
- **Altillo:** escalera rebatible desde el pasillo del 1P; baúles, muñecas viejas, cuna, caballito de madera,
  maniquíes con sábanas, ventanita redonda.
- **Sótano:** caldera, depósito, frascos, muebles con sábanas, la pared rajada → cuarto de 1961.
- **Patio:** parrilla, pileta de lona con agua verde, cucha de Choripán, limonero, soga con sábanas, galpón.
- **Escondites (≥14):** todos los roperos (marcadores `hide_*`), debajo de 5 camas, despensa, bañadera, galpón,
  baúl del altillo. Cada uno con marcador de entrada y de "adentro".
- **Interactuables** (bloques con reacción al click derecho, ver §6.3): cajones, heladera, TV, radio, canilla,
  llaves de luz, mecedora, caja de música, teléfono fijo, máquina de coser, persianas, roperos.

## 4. El director de terror (`com.deadline.horror`)

- **Tensión** `0..100` y **acto** `0..6`. La tensión sube con el tiempo y con cada evento (cada evento declara su
  `intensity`); baja sola cuando no pasa nada. Ciclo tipo AI Director: `BUILD` (sube) → `PEAK` (evento grande) →
  `RELAX` (40–90 s de silencio, solo ambiente) → `BUILD`...
- **Selección:** cada `2–25 s` (más corto cuanto mayor el acto y la tensión) el director tira un evento elegible:
  acto dentro de `[minAct,maxAct]`, cooldown cumplido, no repetido en los últimos 6, condiciones de lugar (habitación
  del jugador, distancia, si está mirando o no, luz/oscuridad, si está escondido). Peso por tier y por "novedad".
- **Reglas de oro:** nunca dos sustos grandes seguidos; nunca jumpscare con el jugador en un menú o escondido sin
  que la cacería lo haya encontrado; los eventos "fuera de vista" se ubican donde el jugador NO mira (detrás, otra
  habitación); los "a la vista" donde mira o va a mirar (fin del pasillo, marco de puerta).
- Debug: `/deadline horror event <id>`, `/deadline horror act <n>`, `/deadline horror tension <v>`, overlay F3 con
  acto/tensión/último evento.

## 5. Catálogo de eventos aleatorios (mínimo 50)

Formato: `id` — qué pasa (acto mín.–máx., intensidad 1–5). "Fuera" = fuera de la vista, "Vista" = frente al jugador.

**Sonido (casa viva)**
1. `pasos_arriba` — pasos lentos en el piso de arriba justo sobre el jugador, se detienen (1–5, 1).
2. `tres_golpes` — tres golpes dentro de la pared al lado del jugador; si golpeás, contestan (1–5, 2).
3. `palmadas` — dos palmadas detrás del jugador (El Conjuro) (3–5, 3).
4. `risita` — risita de nena en otra habitación (1–5, 1).
5. `caja_musica` — la caja de música suena sola en el cuarto de Lucía; se corta cuando entrás (1–4, 2).
6. `dentadura` — chasquido de dentadura postiza muy cerca del oído (3–5, 3).
7. `tu_voz` — tu propia voz (grabada del micrófono) llamándote desde otra habitación (2–5, 3; si no hay SVC: tu
   nombre en un susurro no verbal + golpe).
8. `respiracion` — respiración pesada pegada al jugador, solo de un lado (2–5, 2).
9. `rezo_reves` — rezo ininteligible al revés desde el cuarto de la Nona (2–5, 2).
10. `perro_rasca` — algo rasca la puerta del cuarto donde estás, de afuera (2–5, 2).
11. `telefono_fijo` — suena el teléfono fijo; al levantar: estática y respiración (2–5, 2).
12. `llanto_sotano` — llanto de nene que viene del sótano, por la rejilla (3–5, 2).

**Puertas, luces y objetos (poltergeist)**
13. `puerta_lenta` — una puerta del pasillo se abre despacio sola, a la vista (1–5, 2).
14. `portazo` — portazo fuerte en otra habitación (1–5, 2).
15. `cascada` — todas las puertas del pasillo del 1P se cierran una tras otra hacia el jugador (4–6, 4).
16. `picaporte` — el picaporte de la puerta del cuarto donde estás se mueve solo, desde afuera (2–5, 3).
17. `parpadeo` — las luces de la habitación titilan y vuelven (1–3, 1).
18. `apagon_cuarto` — se apaga la habitación; al volver, algo cambió de lugar (2–5, 3).
19. `lampara_fondo` — se prende SOLA una lámpara al fondo del pasillo; debajo, una figura; se apaga (3–5, 4).
20. `tele_sola` — la tele se prende con estática a todo volumen; en la estática se ve una cara (2–5, 3).
21. `silla_corre` — una silla se arrastra sola unos bloques, a la vista (1–5, 2).
22. `torre_sillas` — saliste del comedor 10 s y al volver las 8 sillas están apiladas en torre (Poltergeist) (3–5, 4).
23. `platos_vuelan` — el aparador escupe platos que se estrellan alrededor del jugador (3–5, 4).
24. `cuchillos` — los cuchillos de la cocina flotan, apuntan al jugador y se clavan en la pared al lado (4–6, 5).
25. `cuadros` — todos los cuadros del pasillo aparecen dados vuelta (2–5, 2).
26. `cajones` — todos los cajones de la habitación abiertos a la vez cuando te das vuelta (2–5, 3).
27. `mecedora` — la mecedora de la Nona se mece sola, más y más rápido, se para en seco (1–5, 2).
28. `munecas_miran` — las muñecas del estante giraron la cabeza hacia el jugador (2–5, 2).
29. `canilla_sangre` — la canilla se abre sola; sale agua, después sangre espesa (3–6, 3).
30. `persianas` — todas las persianas de la planta bajan de golpe a la vez (3–5, 3).
31. `heladera` — la heladera se abre sola; adentro, luz parpadeante y algo envuelto en papel que se mueve (2–5, 3).
32. `vuela_objeto` — un objeto (libro, vaso, frasco) sale volando hacia el jugador y lo golpea (3–6, 3).

**Apariciones (lo que se ve)**
33. `sombra_cruza` — una sombra alta cruza el marco de una puerta al fondo (1–5, 2).
34. `nona_fondo` — la Nona parada al final del pasillo, de cara a la pared; si te acercás, desaparece (2–4, 3).
35. `nona_ventana` — la Nona mirando desde AFUERA por la ventana del 1P (no hay balcón ahí) (2–5, 4).
36. `perro_mira` — Choripán en dos patas mirando, cada vez más cerca (ver §2 Acto 3) (1–6, 2→4).
37. `figura_espejo` — en el espejo del baño/hall, alguien detrás tuyo; te das vuelta: nada (2–5, 4).
38. `detras_hombro` — al darte vuelta rápido, una cara roja por medio segundo pegada a tu cara (Insidious) (4–6, 5, jumpscare).
39. `bajo_cama` — una mano gris sale de debajo de la cama y se retira (Aterrados) (3–6, 3).
40. `toti_rincon` — Toti parado en el rincón de la habitación, de cara a la pared, inmóvil. Si lo mirás 3 s, gira la
    cabeza sin mover el cuerpo (3–5, 4).
41. `copia_sonrie` — un familiar parado quieto en un rincón sonriendo demasiado (sonrisa de copia), te sigue con la
    mirada; al volver a mirar ya no está (4–6, 4).
42. `lucia_techo_corre` — Lucía corre por el techo del pasillo como araña y se mete en un cuarto (4–6, 5).
43. `ofelia_aparece` — la muñeca Ofelia aparece en lugares imposibles: tu cama, la silla del comedor, la heladera
    (2–6, 2).
44. `sabana` — una sábana de la soga del patio vuela con forma de persona y cae vacía (El Conjuro) (2–5, 3).
45. `visitante` — una figura alta y quieta en el rincón más oscuro de la habitación, solo visible sin linterna
    (Gerald's Game) (3–6, 4).

**Sangre y cuerpo**
46. `escritura` — escritura con sangre en la pared, en una pared que miraste hace segundos: "ELLA ESCUCHA", "NO
    HABLES", "LEMAZA", "ESTÁ DETRÁS" (2–6, 3).
47. `huellas` — huellas de manos ensangrentadas aparecen en una ventana, una por una, de afuera (3–6, 3).
48. `pisadas` — huellas de pies descalzos con sangre que llevan a un ropero cerrado (3–6, 3).
49. `gotea_techo` — sangre gotea del techo, en el piso se forma un charco que crece (3–6, 2).
50. `banera` — la bañadera llena de sangre, burbujea, algo se hunde (4–6, 4).
51. `diente` — al abrir un cajón: dientes humanos y la dentadura postiza de la Nona, ensangrentada (2–6, 2).

**Celular**
52. `msg_marta` — mensaje de Marta según acto (lista en §8) (0–6, 1).
53. `msg_desconocido` — número desconocido: solo "..." escribiendo, nunca llega nada; o una foto tuya DE ESPALDAS
    tomada desde adentro de la casa (2–6, 3).
54. `linterna_muere` — la linterna titila y se apaga 4 s; en esos 4 s, algo respira cerca (3–6, 3).

## 6. Mecánicas

### 6.1 Ruido y escucha ("Ella escucha todo")
- Medidor de ruido en el HUD (reutilizar `Fx.noise`): correr, saltar, portazos, objetos rotos, click de linterna,
  y sobre todo **el micrófono** (SVC: hablar = ruido alto; gritar = la Nona va directo a vos).
- Agacharse = silencio. Contener la respiración (tecla `B` por defecto) cuando estás escondido.
- Antes del Acto 5 el ruido solo provoca eventos ("la casa responde"). Desde el Acto 5 atrae a la cazadora.

### 6.2 Escondites
- Click derecho en un ropero/cama/despensa/bañadera marcado: entrás (cámara fija dentro, vista entre rendijas;
  overlay de rendijas oscuras, latido según distancia de la cazadora). Salís con shift.
- La cazadora revisa escondites cerca de donde escuchó el último ruido; si estás conteniendo la respiración y no
  hiciste ruido, abre, mira (cara a 30 cm por las rendijas: susto), y se va. Si respirás/hablás: te saca.

### 6.3 Interactuables (click derecho en bloques decorativos)
Cajones (contenido aleatorio: nada, fotos, rosario roto, dientes, carta), heladera (luz + contenido), TV (on/off/
estática), radio (estática/canción de cuna), canilla (agua/sangre en acto 4+), llave de luz (prende/apaga el grupo
de la habitación; en acto 4+ a veces no responde, o la apagás y se vuelve a prender), mecedora, caja de música,
teléfono fijo, máquina de coser, persianas (subir/bajar), roperos (abrir/esconderse), puertas con cerrojo.

### 6.4 Objetos voladores
- `FlyingPropEntity`: toma un bloque decorativo del mundo (silla, plato, cuadro, cuchillo, libro), lo convierte en
  entidad que renderiza ese bloque, con física (vuelo dirigido, gravedad, rebote, rotación) y daño leve si pega.
  Al terminar vuelve a ser bloque (en su lugar o donde cayó) o se rompe (platos: partículas + sonido de vidrio).

### 6.5 Sangre
- Decals de sangre en piso/pared (bloques finos tipo alfombra/placa): salpicadura, charco que crece, mano, pisada,
  chorreado, escritura (TextDisplay rojo oscuro con fuente "manuscrita" o decal por letras). Se limpian al terminar.

### 6.6 Jumpscares
- Overlay de cara completa (modelo 3D renderizado pegado a la cámara + sacudida + sonido estridente). Máximo uno
  cada 3 minutos, nunca en los primeros 4 minutos del caso. Lista: Nona rota, Lucía, copia sonriente, perro largo,
  cara roja.

### 6.7 Las herramientas del exorcista (no son para ganar: compran segundos)
- Linterna (pila que se gasta; el click hace ruido), crucifijo (la cazadora retrocede 3 s, se calienta y quema),
  agua bendita (la cazadora huye 8 s; 3 usos), sal (línea que no cruza 20 s).

### 6.8 (sin cordura)
- No hay cordura: el dueño la sacó (24/10/2026). Nada guarda, muestra ni reacciona a un valor de cordura; no hay
  pastillas ni alucinaciones por cordura baja. Los sustos son los mismos (sonido, sacudida, flash, jumpscare,
  ceguera, náusea), sin el descuento. Se deja el número para no correr las referencias a 6.9 y 6.10.

### 6.9 El auto y el GPS
- `CarEntity` (Renault 12): W/S acelera/frena/reversa, A/D dobla (radio de giro según velocidad), sube escalones
  de 1 bloque, gravedad, choque frena. Faros (luz dinámica tipo linterna), radio, bocina, sonido de motor por rpm.
  Se sube con click derecho. Llave en el inventario (`car_keys`): llama al auto si está lejos.
- GPS: flecha en el HUD + distancia mientras haya un caso aceptado y el jugador no esté en el sitio.

### 6.10 El sitio en el overworld
- Al aceptar: buscar una llanura (plains/savanna/meadow/sunflower) a 150–400 bloques; nivelar un terreno del lote +
  6 de margen (rellenar abajo, despejar arriba 40 bloques), colocar el sitio por tandas con chunks forzados, guardar
  el origen en el SavedData del mundo. La casa queda. Durante el caso la noche se fija (y se restaura al final).

## 7. Los personajes (sin voz)

- **Nona Pocha (82):** la poseída. Antes del Acto 5: lenta, andador, sonríe, aparece donde no debería, reza al revés,
  se queda mirando. Deformaciones (variante `rota`): cuello 180°, mandíbula descolgada, alargada (2,4 bloques),
  caminata araña boca arriba, cuelga del techo. Cataratas: ojos blancos.
- **Marta (44):** la que escribe. Ojeras, celular siempre en la mano. Gestos: señala, niega con la cabeza, se tapa la
  boca. En el Acto 5 desaparece (está en el sótano) y lo que anda arriba con su cara es una copia.
- **Jorge (47):** callado, quebrado. Sonámbulo con cuchillo en el Acto 4 (te pasa al lado sin verte, se para en
  la puerta de los chicos). Copia en el Acto 5.
- **Lucía (12):** la que habla con Lemaza. Variante poseída: camina por el techo, ojos negros, sangra por la nariz.
- **Toti (6):** el que dibuja (dibujos en la heladera: la casa con una figura larga en el techo). Rincones.
- **Choripán (perro):** el que avisa. Al principio normal, gruñe a la Nona. Después: parado en dos patas mirando.
  Final del Acto 5 o 6: **el perro largo** (modelo `choripan_demonio`): sale de la cucha y no termina de salir.
- **Ofelia (muñeca):** aparece donde no debe. En el cuarto de 1961, sentada en la cama.
- **Lemaza / Azamel:** nunca se ve entero. Es la sombra alta, el visitante, la cara roja.

## 8. Mensajes (todos de texto, cortos, en rioplatense)

Acto 0: ver §2. Acto 1: "¿Ya viene?", "Apague las luces del auto cuando llegue." Acto 2: "No la deje sola con los
chicos.", "No hable. Siéntese." Acto 3: "Lucía no duerme hace 9 días.", "La escucho hablar de noche con alguien en
el ropero.", "El perro no entra a la casa desde el martes.", "No coma lo que ella le sirva." Acto 4: "Jorge no está
en la cama.", "Lucía no está en la cama.", "¿Usted está en el pasillo?", "No es usted el que está en el pasillo.",
"Escóndase.", (desconocido) "...". Acto 5: "Estamos encerrados en el sótano.", "No sé quién está arriba.", "Si la
escucha cerca no respire.", "Ella no ve. Ella ESCUCHA." Acto 6: (desconocido) "bajá", "bajá", "bajá". Final: "Gracias
por venir.", "Ya somos todos." + foto.

## 9. Lo que se reutiliza y lo que se corta

- Se reutiliza: sitio y kits de la casa (se agranda), modelos de Marta/Jorge/Nona/Toti/Lucía (poseída)/Ofelia/
  Choripán/perro largo, `FamilyEntity` (poses + `walkTo`/`face`/`watch`), `Run` (marcadores, puertas, luces,
  actores), `KnifeOrbit` (cuchillos), `DollShelf` (muñecas que giran), sistema de ruido/voz del Colegio, jumpscare,
  linterna/crucifijo/agua bendita/sal.
- Se corta (borrar código y assets): choripán bendito y su receta, parrilla/cocinar, chancleta, chat de nombres,
  rueda de espíritus, puntadas (`Stitch`), telarañas de lana (`YarnWeb`), el fuego fatuo (`DemonWisp`), voces,
  llamadas, `CasaScript` de 8 capítulos con objetivos, la cordura (valor, HUD, pastillas, alucinaciones).

## 10. Plan de implementación (tandas de 3 agentes como máximo)

- **Tanda A:** (A1) limpieza global: voces, llamadas → mensajes, monja alta, cortes de §9. (A2) overworld + auto +
  GPS. (A3) casona v2 (`tools/sites/casa.py`).
- **Tanda B:** (B1) motor `com.deadline.horror` + interactuables + objetos voladores + sangre + 30 eventos.
  (B2) cacería + escondites + respiración + jumpscare overlay. (B3) arte: poses/variantes de deformación, perro
  parado, decals de sangre, sonidos nuevos.
- **Tanda C:** set pieces y actos (llegada, cena, Lucía techo, Jorge sonámbulo, la Nona se rompe, sótano, final en el
  auto), los otros 24 eventos, revisión de partida completa, CI con capturas.

## 11. Contrato de marcadores de la casona v2 (`tools/sites/casa.py` → `sites/casa.json`)

El script y el director usan EXACTAMENTE estos nombres (se pueden agregar más, nunca renombrar).
Puntos `(x,y,z,facing)` = donde se para un actor/jugador mirando hacia `facing`.

**Exterior:** `spawn` (=`llegada`), `llegada` (donde estaciona el auto, en el camino de entrada, mirando a la casa),
`porton`, `camino` (mitad del camino de entrada), `puerta_entrada` (afuera, frente a la puerta: donde se golpea),
`nona_umbral` (adentro, en el umbral, mirando afuera), `farol`, `patio`, `patio_fondo` (lo más lejos de la casa),
`cucha`, `cucha_techo`, `parrilla`, `pileta`, `soga`, `galpon`, `limonero`, `ventana_1p_afuera` (punto en el aire
afuera de una ventana del 1P sin balcón: donde "flota" la Nona mirando adentro), `final_auto` (donde aparece el auto
al final), `perro_mira_1` (patio_fondo, mirando la casa), `perro_mira_2` (afuera de la ventana del living),
`perro_mira_3` (fondo del pasillo PB), `perro_mira_4` (al pie de la cama de huéspedes).
**PB:** `hall`, `espejo_hall` (frente al espejo grande), `living`, `tv`, `sillon_jorge`, `mecedora`, `comedor`,
`silla_1`..`silla_8` (cabecera = `silla_1` = Nona; `silla_2` Marta, `silla_3` Jorge, `silla_4` Lucía, `silla_5` Toti,
`silla_6` jugador), `aparador`, `cocina`, `heladera`, `mesada`, `cuchillos`, `canilla_cocina`, `despensa`,
`lavadero`, `tablero`, `bano_pb`, `nona_cuarto`, `nona_cama`, `nona_altar`, `nona_mecedora`, `costurero`,
`maquina_coser`, `escritorio`, `escritorio_silla`, `pasillo_pb`, `pasillo_pb_fondo`, `esc_principal_pie`,
`esc_principal_arriba`, `esc_servicio_pie`, `esc_servicio_arriba`, `telefono_fijo`.
**1P:** `pasillo_1p`, `pasillo_1p_fondo`, `lucia_cuarto`, `lucia_cama`, `lucia_techo` (en el techo del cuarto,
SEALED), `pasillo_techo` (techo del pasillo 1P, SEALED), `estante_munecas`, `caja_musica`, `toti_cuarto`,
`toti_cama`, `toti_rincon` (rincón de cara a la pared), `matrimonial`, `matrimonial_cama`, `tocador`,
`huespedes` (cuarto del jugador), `huespedes_cama`, `bano_1p`, `banera`, `espejo_bano`, `balcon`, `cuarto_nono`,
`altillo_trampa` (debajo de la escalera rebatible), `altillo`, `altillo_baul`.
**Sótano:** `sotano_escalera` (pie de la escalera), `sotano`, `caldera`, `sotano_pared` (frente a la pared rajada),
`cuarto61` (centro, SEALED hasta romper la pared), `cuarto61_cama`, `cuarto61_techo` (SEALED), `familia61_1`..`4`
(parados de cara a la pared, SEALED).
**Escondites** (≥14): para cada uno `hide_<id>` (posición del jugador ADENTRO, mirando hacia afuera) y
`hide_<id>_out` (afuera, frente a la entrada; ahí se para la cazadora para revisarlo). Ids: `ropero_nona`,
`ropero_lucia`, `ropero_toti`, `ropero_matrimonial`, `ropero_huespedes`, `ropero_hall`, `cama_lucia`, `cama_toti`,
`cama_matrimonial`, `cama_huespedes`, `cama_nona`, `despensa`, `banera`, `baul_altillo`, `galpon`. Las camas-escondite
dejan 1 bloque libre debajo (cama elevada) y el ropero es 1×1×2 por dentro como mínimo.
**Escrituras** (`writes`, paredes donde aparece sangre/escritura): `lemaza`, `espejo_azamel`, `cuaderno`,
`escritura_1`..`escritura_12` repartidas (hall, living, comedor, cocina, pasillo PB, pasillo 1P ×2, cuartos, baño,
sótano), cada una sobre una pared lisa de al menos 3×2.
**Áreas** (una por ambiente, para saber dónde está el jugador): `sitio`, `casa` (todo el interior), `exterior`, `hall`,
`living`, `comedor`, `cocina`, `despensa`, `lavadero`, `bano_pb`, `nona_cuarto`, `costurero`, `escritorio`,
`pasillo_pb`, `esc_principal`, `esc_servicio`, `pasillo_1p`, `lucia`, `toti`, `matrimonial`, `huespedes`, `bano_1p`,
`balcon`, `cuarto_nono`, `altillo`, `sotano`, `cuarto61`, `patio`.
**Grupos:** `luces_<area>` por ambiente (pares prendida/apagada), `luces_pasillo_1p` (una cada 4), `comedor_sillas`,
`aparador_platos`, `cuchillos`, `cuadros_pasillo`, `persianas_pb`, `persianas_1p`, `estante_munecas`, `tv`,
`sotano_pared`, `velas_sotano` (camino de velas al sótano), `altar_velas`, `ventanas_1p`, `cajones` (todos los
muebles con cajones).
**Puertas:** `entrada`, `porton`, `puerta_patio`, una por ambiente con el nombre del área (`living` si tiene,
`cocina`, `despensa`, `lavadero`, `bano_pb`, `nona_cuarto`, `costurero`, `escritorio`, `lucia`, `toti`,
`matrimonial`, `huespedes`, `bano_1p`, `balcon`, `cuarto_nono`, `sotano`, `galpon`), y los roperos
`ropero_<id>`. `pasillo_1p_cascada`: lista ordenada de las puertas del pasillo 1P desde el fondo hacia la escalera.

## 12. Motor de terror: API fija (`com.deadline.horror`, ya escrito)

- `HorrorEvent` (abstracta): `id`, `Kind` (SOUND, POLTER, APPARITION, BLOOD, PHONE, SCARE, SETPIECE); configuración
  fluida en el constructor: `acts(min,max)`, `intensity(1..5)`, `cooldown(seg)`, `weight(w)`, `once()`,
  `scripted()` (nunca al azar). Ciclo: `canRun(Ctx)` (condiciones; guardar lo encontrado en `c.data`) →
  `start(Ctx)` → `tick(Ctx)` cada tick hasta devolver `true` → `stop(Ctx)` SIEMPRE una vez (restaurar el mundo,
  despawnear actores). `maxTicks()` corta por seguridad (90 s por defecto).
- `Ctx`: `run`, `haunt`, `p` (el jugador objetivo), `event`, `rnd`, `t` (ticks desde el inicio), `data`,
  `room()`, `get/put`, `chance(f)`, `between(a,b)`.
- `HorrorEvents.register("casa", new MiEvento())` (una vez al iniciar el mod); `of`, `get`, `ids`.
- `Haunt.of(run)` (uno por run): `tick()` (lo llama el script del caso cada tick), `act()`/`act(n)`,
  `actTicks()`, `caseTicks()`, `tension()`/`addTension`, `phase()` (BUILD/PEAK/RELAX), `bigScares()`,
  `times(id)`/`happened(id)`, `fire(id[, jugador, chequearCondiciones])`, `isRunning(id)`, `busy()`,
  `relax(ticks)`, `pause(bool)`, `canJumpscare()`/`jumpscared()`, `stopAll()`, `Haunt.forget(run)` al terminar.
  Los eventos de intensidad 4+ son PICO y después hay 40–90 s de calma. Un `SCARE` solo sale si `canJumpscare()`.
- `HouseQuery`: `room(run, entidad)`, `roomAt`, `inHouse`, `points(run, prefijo)`, `sees(run, p, pos)`,
  `nearest`, `outOfView(run, p, prefijo, min, max)`, `inView(...)`, `random(...)`, `doorsNear`, `doorPos`,
  `behind(run, p, dist)` (lugar libre detrás del jugador), `standable`, `dark(run, pos)`,
  `blocks(run, área, test)` (p. ej. todas las sillas del comedor), `key(state)` (clave del bloque del kit).
- `HorrorCommands.register(dispatcher)`: `/deadline horror status|event <id>|act <n>|tension <v>|pause`
  (el cambio de acto postea `act:<n>` en el run para que el script reaccione).
- Convenciones: cada evento en su clase dentro de `com.deadline.horror.casa.events` (o agrupados por tipo), sin
  dejar bloques cambiados al terminar salvo lo que la historia quiere que quede (sangre, cuadros dados vuelta: se
  limpian en `onLeave`). Sonidos por `run.sound(...)`/`Fx.soundAt` (posicional), nunca globales salvo los del celular.
