# Evaluador Flutter para Moodle CodeRunner

El motor analiza código Dart con Tree-sitter y aplica rúbricas JSON para
producir puntuación parcial y feedback compatible con CodeRunner.

## Estructura

- `src/`: motor Python y biblioteca compilada.
- `rubricas/`: criterios de cada actividad.
- `ejemplos/`: soluciones y casos Dart.
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
