# Recuperación de las preguntas de DAD

Origen: exportación Moodle XML de la categoría «26/27 UT 2. Componentes
reutilizables», curso 98919 del campus de eForma de Canarias.
Fecha de recuperación: 1 de noviembre de 2026.

Se incorporan al repositorio los archivos de soporte de las cinco preguntas
«UT2 · Eventos y callbacks» y la rúbrica del reto «El clásico 2DAM vs 2DAW».
No se publican exportaciones completas del banco ni datos de estudiantes.

La versión del motor de las cinco preguntas de callbacks era idéntica. El
clásico usaba otra versión de `evaluador_generico.py`: la comparación muestra
que la versión de callbacks añade funciones y el despacho de sus reglas, sin
eliminar las del clásico. Los otros siete archivos de soporte coincidían.

Respecto al repositorio original, seis archivos Python y la biblioteca
compilada no cambian (ignorando CRLF/LF). Se actualiza únicamente
`src/evaluador_generico.py`, incorporando las reglas recuperadas y sus
ampliaciones de propiedades, layouts y callbacks.

Las soluciones Dart se recuperan de los bloques `pre` de la retroalimentación
general: el campo de respuesta de referencia estaba vacío. Son ejemplos para
regresión local; no sustituyen la validación del despliegue en CodeRunner.

| Actividad | Pregunta de Moodle | Puntos de rúbrica |
| --- | --- | ---: |
| callbacks_01_boton | 151674927 | 5 |
| callbacks_02_contador | 151674930 | 7 |
| callbacks_03_personalizar | 151674933 | 7 |
| callbacks_04_informacion | 151674934 | 6 |
| callbacks_05_opcional | 151674938 | 8 |
| clasico_dam_daw | 151653807 | 10 |

Esta sincronización es de Moodle hacia el repositorio. No modifica preguntas,
calificaciones ni intentos existentes y no implica migrar las preguntas al
motor común. Para una migración posterior se necesita probar la configuración
real en Moodle y decidir cómo tratar intentos previos y recalificaciones.

## Validación realizada

Las 47 pruebas pasan, incluidas las seis soluciones de UT2 y las 43 pruebas
anteriores. Se usaron Python 3.12 y las mismas fuentes de Tree-sitter y Dart
de los submódulos del repositorio (2a835ee0 y b57d734), compiladas con MSVC
para una copia temporal de pruebas en Windows. No se sustituye la biblioteca
Linux publicada para Moodle. La comprobación Linux se configura también en
GitHub Actions; su ejecución queda pendiente de publicar los cambios.

No se han ejecutado las soluciones dentro del sandbox de Moodle, porque esta
recuperación no cambia las preguntas del aula. Una migración posterior sí
deberá validar las preguntas afectadas en CodeRunner.
