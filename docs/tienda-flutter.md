# Tienda Flutter: funciones y callbacks

Material creado para DAD, UT2, como actividad previa al cuestionario 2.3.
Cuestionario Moodle: 10460098. No se ha modificado el motor del corrector.

La primera pregunta es de tipo descripción y explica el recorrido. Cada paso
tiene un código inicial funcional, una solución completa y una rúbrica. Todo
el trabajo del alumnado está en un único `main.dart`.

| Paso | Necesidad | Concepto | Pregunta Moodle | Peso |
| --- | --- | --- | --- | ---: |
| 1 | Tres productos repiten el diseño | Tarjeta reutilizable | 151704574 | 1 |
| 2 | Dos botones comparten la compra de una pegatina | Método con nombre | 151704575 | 1 |
| 3 | Los productos cuestan cantidades distintas | Parámetro y función anónima | 151704576 | 1 |
| 4 | El botón debe estar dentro de la tarjeta | VoidCallback | 151704577 | 1 |
| 5 | El precio ya pertenece a la tarjeta | Callback con int | 151704578 | 1 |
| 6 | La tarjeta necesita saber si se aceptó la compra | Retorno bool, ampliación | 151704579 | 0 |

La descripción inicial es la pregunta 151704573. El padre conserva un saldo
único; los hijos piden comprar, sin poseer su propio saldo ni llamar a setState.
El paso 6 solo añade un retorno porque el hijo lo utiliza para mostrar el aviso.

## Fuentes y generación

- `actividades/tienda/manifest.json`: orden, nombres, identificadores y pesos.
- `actividades/tienda/introduccion.html`: primera pregunta de descripción.
- `actividades/tienda/*-enunciado.html`: plantillas con marcadores de código y criterios.
- `actividades/tienda/*-feedback.html`: explicaciones con marcador de solución.
- `iniciales/tienda_*.dart` y `ejemplos/tienda_*.dart`: códigos fuente del alumnado.
- `rubricas/rubrica_tienda_*.json`: criterios específicos.
- `moodle/configuracion_tienda.json`: configuración CodeRunner probada en el aula.

`python3 scripts/exportar_tienda.py` sustituye los marcadores usando los fuentes
actuales e incrusta los archivos de soporte de `src/`. El XML no guarda los
pesos del cuestionario ni crea su actividad: tras importarlo, colocar la
descripción primero, una pregunta por página, sin barajar el orden, intentos
ilimitados y comportamiento adaptativo sin penalización. Dar peso 1 a los pasos
1–5 y peso 0 a la ampliación. No reimportar automáticamente sobre el banco del
aula: ya contiene estas preguntas.

Los paquetes individuales se generan con
`python3 scripts/preparar_moodle.py tienda_01_tarjetas` (y los otros cinco nombres
del manifest). Son archivos de soporte para CodeRunner; el contenido completo
de las preguntas lo genera el exportador XML.

## Plantillas

Enunciados derivados de **Activity template** y feedback de **Feedback template**
de [noeper/moodle-ui-kit](https://github.com/noeper/moodle-ui-kit), revisión
`703f6fc66f7601e615ce1f8ee0db1adb240b1ff0`. Licencia declarada: CC0 1.0.
Se conserva el diseño HTML inline; la generación actualiza código y criterios
sin depender de una conexión al repositorio de plantillas.

## Validación

Las seis soluciones se comprobaron en las vistas previas de CodeRunner de Moodle
y obtuvieron el 100 % de sus criterios. El análisis Dart no encontró incidencias
en los doce ficheros y las siete pruebas Flutter de interacción pasaron con
Flutter 3.35.7 / Dart 3.9.2. Las pruebas distinguen solución, código inicial,
entregas vacías, soluciones comentadas, descuentos sin setState y rechazo sin saldo.

El corrector es estático; las pruebas Flutter complementan esa comprobación.
Actualizar estos materiales en GitHub no modifica las preguntas existentes.
Si se cambia una rúbrica o una solución, probarla antes de desplegarla; si se
cambia el motor, probar además las actividades afectadas y su sandbox Moodle.
