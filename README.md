# DEAD LINE

Mod de terror para **Minecraft 1.21.11 (Fabric)**, pensado para grabar videos.

Sos exorcista. Tu teléfono vibra de madrugada: alguien te escribe pidiendo ayuda. No llama: ella escucha todo.
Aceptás el caso, te ponés la sotana y vas al lugar. Dos casos, cada uno con su historia, sus personajes y su edificio hecho a mano:

- **Colegio Santa Inés de la Vigilia** — un internado de monjas cerrado desde 1984. Sor Agonía sigue tomando lista.
  *(jugable de punta a punta)*
- **Casa Morales** — una familia, una muñeca que se llama Ofelia y Choripán, el salchicha. *(en desarrollo)*

## Instalar y probar

1. Instalá **Fabric Loader 0.19.5** (o más nuevo) para **Minecraft 1.21.11** y **Fabric API 0.141.6+1.21.11**.
2. Bajá el mod: en GitHub, pestaña **Actions** → la última ejecución verde de **build** → al pie, el artefacto
   **deadline-mod** (es un .zip con el `.jar` adentro). Copiá el `deadline-0.1.0.jar` a la carpeta `mods`.
3. *(Opcional, muy recomendado)* **Simple Voice Chat** para 1.21.11: el colegio escucha tu micrófono. La monja te
   oye si hablás fuerte, te toman lista y tenés que contestar "presente", y al final hay que rezar en voz alta. Sin
   micrófono todo se puede jugar igual (agachate para levantar la mano; el libro de rituales reza por vos).
4. Creá un mundo, abrí el chat y poné `/deadline start colegio`. Jugalo en **Supervivencia**, de noche y con el
   volumen alto.

## Cómo se juega

- **G** abre el teléfono (mensajes, casos, tienda, bestiario). **H** activa la cámara VHS para grabar.
- Arriba a la izquierda tenés el **capítulo** y la lista de **objetivos**; si te trabás, a los tres minutos aparece una
  pista. Si morís, volvés al principio del capítulo.
- Abajo a la izquierda, la **cordura**. Baja en la oscuridad y cerca de lo que no tiene que estar ahí.
- El **ruido** importa: correr, saltar, dar portazos y gritar te delatan. En el colegio no se corre por los pasillos.
- La **linterna** quema a la monja. Las pilas no duran para siempre.
- El **traje de exorcista** (sombrero, sotana, faldón y zapatos) te protege de perder cordura tan rápido.

## Comandos para grabar

| Comando | Qué hace |
|---|---|
| `/deadline start colegio [jugador]` | Empieza el caso del colegio |
| `/deadline chapter <n>` | Salta al capítulo n del caso en curso (1 a 9) |
| `/deadline beat <id>` | Dispara una escena puntual del guion |
| `/deadline flag <nombre>` | Marca un paso como hecho (por ejemplo `lista_done` para saltear la lista) |
| `/deadline voice on\|off` | Usa o ignora tu micrófono en el caso |
| `/deadline home [jugador]` | Vuelve a casa |
| `/deadline msg <caso> [jugador]` | Manda ya el hilo de mensajes del caso (casa: Marta, foto y "Aceptar caso") |
| `/deadline sanity <0-100> [jugador]` | Fija la cordura (10 = modo pesadilla) |
| `/deadline jumpscare <entidad> [jugador]` | Jumpscare a pantalla completa (`monja`, `poseida`, `sombra`, `muneca`, `anima`) |
| `/deadline kit [jugador]` | Traje y equipo completos |
| `/deadline money <cantidad> [jugador]` | Da dinero |

## Compilar

Requiere JDK 25 para Gradle/Loom (el mod apunta a Java 21).

```
./gradlew build
```

El `.jar` queda en `build/libs/`.

## Estructura

- `src/main` — lógica común: casos, director de escenas (capítulos, guion, puertas, luces), entidades, ítems,
  cordura, ruido y voz, red, comandos.
- `src/client` — HUD de historia, teléfono, renderers y animaciones, shaders y efectos de pantalla.
- `tools/blocks` — el kit de construcción (cada bloque y mueble del colegio, pintado a mano en Python).
- `tools/sites` — los edificios de cada caso, armados con el kit.
- `tools/models`, `tools/art`, `tools/audio`, `tools/data` — criaturas, ítems, sonido (voces + DSP) e idiomas.
- `docs/design` — la biblia de los casos y la dirección del video.
