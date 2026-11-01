"""Prepara una copia de los códigos Dart para analizarlos y probarlos."""
import json
from pathlib import Path
import shutil

RAIZ = Path(__file__).resolve().parents[1]


def main():
    manifest = json.loads((RAIZ / "actividades" / "tienda" / "manifest.json").read_text(encoding="utf-8"))
    destination = RAIZ / "tests" / "flutter" / "lib"
    destination.mkdir(parents=True, exist_ok=True)
    for item in manifest:
        slug, step = item["actividad"], item["paso"]
        shutil.copy2(RAIZ / "ejemplos" / f"{slug}.dart", destination / f"paso{step}.dart")
        shutil.copy2(RAIZ / "iniciales" / f"{slug}.dart", destination / f"inicial{step}.dart")
    print(destination)


if __name__ == "__main__":
    main()
