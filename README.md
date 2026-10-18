# DEAD LINE

Mod de terror para **Minecraft 1.21.11 (Fabric)**, pensado para grabar videos y clips.

Sos exorcista. Tu teléfono suena de madrugada y del otro lado alguien pide ayuda. Aceptás la llamada y el teléfono
te lleva al lugar: una casa con una nena poseída, el río de La Llorona, un bosque donde algo imita voces, un parque de
diversiones abandonado y un convento donde hay una monja de más.

## Cómo se juega

1. Al entrar recibís el **Teléfono DEAD LINE** y un kit básico. A los pocos minutos suena la primera llamada.
2. Abrí el teléfono con **G** (o click derecho con el teléfono en la mano): leé el mensaje, mirá el peligro y el pago,
   y tocá **ACEPTAR**. Te teletransporta al caso.
3. Cada caso tiene un **objeto maldito** escondido (zapatito, tótem de hueso, caja musical, rosario invertido, muñeca).
   Mientras exista, la entidad es casi invulnerable. Purificalo con **Agua Bendita**.
4. Debilitá a la entidad con tus herramientas y terminá el caso: **Frasco de Almas** o, con la Poseída, el
   **Libro de Rituales** (exorcismo).
5. Volvé a casa desde el teléfono, cobrá y comprá mejor equipo en la **Tienda**. El **Bestiario** se completa a medida
   que te cruzás con cada entidad.

La **cordura** (abajo a la izquierda, con electrocardiograma) baja en la oscuridad y cerca de las entidades. Con poca
cordura escuchás susurros y pasos, ves figuras, la pantalla se tiñe y aparece el **Hombre Sombra**. Las pastillas, la
luz y las velas rituales la recuperan.

## Teclas

| Tecla | Acción |
|---|---|
| **G** | Abrir el teléfono |
| **H** | Modo cámara VHS (REC, timecode, scanlines, shader) — ideal para grabar |

## Herramientas

Crucifijo (repele en cono), Agua Bendita (se arroja), Sal (líneas que ninguna entidad cruza), Detector EMF,
Linterna (luz real + modo UV que revela huellas), Spirit Box (responde frases), Cámara de Espíritus (flash que aturde
y revela ánimas), Libro de Rituales, Frasco de Almas, Pastillas, Daga de Plata, Rosario, Bengalas, Velas Rituales.

## Comandos para creadores

| Comando | Qué hace |
|---|---|
| `/deadline call <caso> [jugador]` | Hace sonar el teléfono con un caso específico |
| `/deadline start <caso> [jugador]` | Salta directo al caso |
| `/deadline home [jugador]` | Vuelve a casa |
| `/deadline sanity <0-100> [jugador]` | Fija la cordura (probá 10 para el modo pesadilla) |
| `/deadline money <cantidad> [jugador]` | Da dinero |
| `/deadline jumpscare <entidad> [jugador]` | Dispara un jumpscare a pantalla completa |
| `/deadline kit [jugador]` | Kit completo de cazador |
| `/deadline calls <minSeg> <maxSeg>` | Cada cuánto suena el teléfono |

Casos: `casa`, `rio`, `bosque`, `parque`, `convento`.
Entidades para jumpscare: `llorona`, `wendigo`, `poseida`, `payaso`, `monja`, `sombra`, `muneca`.

## Compilar

Requiere JDK 25 para Gradle/Loom (el mod apunta a Java 21).

```
./gradlew build
```

El `.jar` queda en `build/libs/`. Depende de **Fabric Loader ≥ 0.19.5** y **Fabric API**.

## Estructura

- `src/main` — lógica común: casos, entidades, ítems, cordura, red, comandos.
- `src/client` — HUD, teléfono, partículas, renderers/animaciones, shaders y efectos de pantalla.
- `tools/` — generadores de arte (modelos 3D, texturas, GUI, partículas), sonido (TTS + DSP) y datos/idiomas.
