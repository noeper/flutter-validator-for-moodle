"""Prepara paquetes planos para preguntas Flutter de Moodle CodeRunner."""

import argparse
import shutil
from pathlib import Path


RAIZ = Path(__file__).resolve().parents[1]
COMUNES = (
    "adaptar_coderunner.py",
    "analizador_flutter.py",
    "analizar_dart.py",
    "evaluador_generico.py",
    "extraer_arbol.py",
    "extraer_clases.py",
    "extraer_estado.py",
    "libdartparser.so",
)
ACTIVIDADES = {
    "bandera_francesa": "rubrica_bandera_francesa.json",
    "carta_ajuste": "rubrica_carta_ajuste.json",
    "carta_coleccionable": "rubrica_carta_coleccionable.json",
    "mascota_virtual": "rubrica_mascota_virtual.json",
    "semaforo": "rubrica_semaforo_generica.json",
}


def preparar(nombre):
    destino = RAIZ / "dist" / "moodle" / nombre
    if destino.exists():
        shutil.rmtree(destino)
    destino.mkdir(parents=True)

    for archivo in COMUNES:
        shutil.copy2(RAIZ / "src" / archivo, destino / archivo)

    shutil.copy2(
        RAIZ / "rubricas" / ACTIVIDADES[nombre],
        destino / "rubrica.json",
    )
    shutil.copy2(
        RAIZ / "moodle" / "personalizacion_coderunner.py.twig",
        destino / "PERSONALIZACION.txt",
    )

    soporte = [p for p in destino.iterdir() if p.name != "PERSONALIZACION.txt"]
    if len(soporte) != len(COMUNES) + 1:
        raise RuntimeError("El paquete no contiene todos los archivos de soporte")
    return destino


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("actividad", choices=sorted(ACTIVIDADES))
    args = parser.parse_args()
    print(preparar(args.actividad))


if __name__ == "__main__":
    main()
