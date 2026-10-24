import json
import subprocess
import sys
from pathlib import Path


def cargar_rubrica(ruta):
    with open(ruta, encoding="utf-8") as archivo:
        return json.load(archivo)


def evaluar(codigo, rubrica):
    resultados = []

    proceso = subprocess.run(
        [sys.executable, "analizar_dart.py"],
        input=codigo,
        text=True,
        capture_output=True
    )

    salida = proceso.stdout

    sintaxis_correcta = (
        proceso.returncode == 0
        and "SINTAXIS_CORRECTA" in salida.splitlines()
    )

    stateful_detectado = any(
        linea.startswith("STATEFUL_WIDGET_DETECTADO")
        for linea in salida.splitlines()
    )

    for criterio in rubrica["criterios"]:
        resultado = {
            "id": criterio["id"],
            "descripcion": criterio["descripcion"],
            "maximo": criterio["puntos"],
            "obtenido": None,
            "estado": "PENDIENTE",
            "observaciones": []
        }

        if criterio["id"] == "estructura":
            if not sintaxis_correcta:
                resultado["estado"] = "REVISAR"
                resultado["observaciones"].append(
                    "No se ha confirmado una sintaxis Dart correcta."
                )
            else:
                componentes = [
                    ("StatelessWidget", "ESTRUCTURA_STATELESS: 1", 0.4),
                    ("Scaffold", "ESTRUCTURA_SCAFFOLD: 1", 0.3),
                    ("MaterialApp", "ESTRUCTURA_MATERIALAPP: 1", 0.3)
                ]

                puntos = 0.0

                for nombre, marca, valor in componentes:
                    if marca in salida.splitlines():
                        puntos += valor
                        resultado["observaciones"].append(
                            nombre + ": detectado"
                        )
                    else:
                        resultado["observaciones"].append(
                            nombre + ": no detectado"
                        )

                resultado["obtenido"] = round(puntos, 2)
                resultado["estado"] = "EVALUADO"
                resultado["observaciones"].append(
                    "Comprobacion estructural preliminar."
                )

        if criterio["id"] == "centrado":
            if not sintaxis_correcta:
                resultado["estado"] = "REVISAR"
                resultado["observaciones"].append(
                    "No se ha confirmado una sintaxis Dart correcta."
                )
            else:
                horizontal = "CENTRADO_HORIZONTAL: 1" in salida.splitlines()
                vertical = "CENTRADO_VERTICAL: 1" in salida.splitlines()

                puntos = (0.5 if horizontal else 0) + (0.5 if vertical else 0)

                resultado["obtenido"] = puntos
                resultado["estado"] = "EVALUADO_PRELIMINAR"

                resultado["observaciones"].append(
                    "Centrado horizontal: " + ("detectado" if horizontal else "no detectado")
                )
                resultado["observaciones"].append(
                    "Centrado vertical: " + ("detectado" if vertical else "no detectado")
                )
                resultado["observaciones"].append(
                    "Deteccion estatica provisional; no verifica aun toda la jerarquia visual."
                )

        resultados.append(resultado)

    return resultados, stateful_detectado


def mostrar_informe(rubrica, resultados, stateful_detectado):
    print("\nEVALUACION:", rubrica["practica"])
    print("=" * 50)

    for resultado in resultados:
        print("\n" + resultado["descripcion"])
        print("Puntuacion maxima:", resultado["maximo"])
        print("Estado:", resultado["estado"])
        if resultado["obtenido"] is not None:
            print("Puntos obtenidos:", resultado["obtenido"])

        for observacion in resultado["observaciones"]:
            print("Observacion:", observacion)

    if stateful_detectado:
        print("\nCONDICION EXCLUYENTE INCUMPLIDA")
        print("Se ha utilizado StatefulWidget.")
        print("NOTA FINAL: 0/10")
    else:
        print("\nNOTA FINAL: pendiente de evaluacion")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(
            "Uso: python3 evaluar_practica.py "
            "rubrica.json codigo.dart"
        )
        sys.exit(1)

    ruta_rubrica = Path(sys.argv[1])
    ruta_codigo = Path(sys.argv[2])

    rubrica = cargar_rubrica(ruta_rubrica)
    codigo = ruta_codigo.read_text(encoding="utf-8")

    resultados, stateful_detectado = evaluar(codigo, rubrica)
    mostrar_informe(rubrica, resultados, stateful_detectado)
