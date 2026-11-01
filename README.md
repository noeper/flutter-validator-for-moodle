# Evaluador Flutter para Moodle CodeRunner

El motor analiza código Dart con Tree-sitter y aplica rúbricas JSON para
producir puntuación parcial y feedback compatible con CodeRunner.

## Estructura

- `src/`: motor Python y biblioteca compilada.
- `rubricas/`: criterios de cada actividad.
- `ejemplos/`: soluciones y casos Dart.
- `iniciales/`: aplicaciones de partida que todavía no resuelven el ejercicio.
- `actividades/tienda/`: descripción inicial, enunciados y feedback regenerables.
- `tests/`: pruebas automáticas.
- `moodle/`: personalización común de CodeRunner.
- `scripts/`: preparación de paquetes para Moodle.
- `dist/moodle/`: paquetes generados; no es código fuente.
- `herramientas/`: utilidades históricas de inspección.
- `artefactos/`: resultados de análisis conservados como referencia.
- `vendor/`: fuentes externas de Tree-sitter.

## Pruebas

```bash
python3 -m unittest discover -s tests -v
```

## Preparar una pregunta Moodle

```bash
python3 scripts/preparar_moodle.py semaforo
python3 scripts/preparar_moodle.py bandera_francesa
python3 scripts/preparar_moodle.py carta_ajuste
python3 scripts/preparar_moodle.py carta_coleccionable
python3 scripts/preparar_moodle.py mascota_virtual
```

Cada carpeta generada contiene los archivos de soporte. La rúbrica específica
se llama siempre `rubrica.json`. El contenido de `PERSONALIZACION.txt` se copia
en el campo **Personalización** de CodeRunner y no se sube como archivo.

También están disponibles `callbacks_01_boton`, `callbacks_02_contador`,
`callbacks_03_personalizar`, `callbacks_04_informacion`,
`callbacks_05_opcional` y `clasico_dam_daw`.

## Tienda Flutter: funciones y callbacks paso a paso

Seis pasos de una tienda con saldo compartido, todos en un único `main.dart`.
Incluye rúbricas, códigos iniciales, soluciones y contenido HTML basado en
Activity template y Feedback template de
[moodle-ui-kit](https://github.com/noeper/moodle-ui-kit).

Las actividades `tienda_01_tarjetas`, `tienda_02_metodo`,
`tienda_03_funcion_anonima`, `tienda_04_voidcallback`, `tienda_05_parametro`
y `tienda_06_retorno` se preparan con `scripts/preparar_moodle.py`.

Para regenerar las siete preguntas (una descripción inicial y seis CodeRunner):

```bash
python3 scripts/exportar_tienda.py
```

Produce `build/tienda-flutter.xml`, con los códigos actuales y todos los archivos
de soporte. No crea ni actualiza nada en Moodle. El peso cero del paso 6 se
configura en el cuestionario, no en la importación del banco. Ver la
[guía de la tienda](docs/tienda-flutter.md).

Las pruebas del corrector están en `tests/test_tienda.py`. Para comprobar también
las aplicaciones reales con Flutter (versión probada: 3.35.7):

```bash
python3 scripts/preparar_pruebas_flutter.py
cd tests/flutter
flutter pub get
flutter analyze --no-pub
flutter test --no-pub
```

GitHub Actions ejecuta las pruebas Python y las de Flutter en trabajos separados.

## Sincronización con DAD

Se han recuperado los archivos de soporte, seis rúbricas y las soluciones de
la retroalimentación general de las preguntas CodeRunner de UT2 de DAD.
Las cinco preguntas de callbacks compartían el mismo motor. El clásico
conservaba una versión anterior cuyo código está incluido en el motor común,
con las ampliaciones de callbacks añadidas. Ver `docs/sincronizacion-dad.md`.

## Actualizar preguntas existentes

Cada pregunta CodeRunner contiene su propia copia de los archivos de soporte.
Cambiar este repositorio no modifica las preguntas de Moodle.

- Una rúbrica nueva para una pregunta nueva no obliga a actualizar las antiguas.
- Una corrección del motor debe desplegarse en las preguntas afectadas que
  deban recibirla. No es obligatorio migrar todas a la vez.
- Antes de desplegar, ejecutar todas las pruebas y comprobar la solución de
  referencia, soluciones alternativas y casos incorrectos de cada actividad
  afectada. Después, validar también en CodeRunner: los tests locales no
  comprueban la configuración del sandbox ni los archivos cargados en Moodle.
- Registrar la versión y las huellas de los archivos desplegados. Conservar
  una exportación XML anterior para poder restaurar la pregunta.

Los tests requieren un entorno Linux compatible con `src/libdartparser.so`.
El analizador es estático: comprueba estructura y patrones del código Dart,
sin ejecutar Flutter ni verificar el resultado visual o funcional completo.
