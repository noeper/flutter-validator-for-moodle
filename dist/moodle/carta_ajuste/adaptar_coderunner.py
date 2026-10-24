import json
import sys
from html import escape

from evaluador_generico import evaluar


def adaptar(codigo, rubrica):
    resultado = evaluar(codigo, rubrica)

    maximo = resultado["maximo"]
    puntuacion = resultado["puntuacion"]

    fraccion = puntuacion / maximo if maximo > 0 else 0

    filas = [
        ["Criterio", "Resultado", "Puntuación"]
    ]

    for criterio in resultado["resultados"]:
        if criterio["puntos"] == criterio["maximo"]:
            estado = "Cumplido"
        elif criterio["puntos"] > 0:
            estado = "Parcialmente cumplido"
        else:
            estado = "No cumplido"

        filas.append([
            escape(criterio["descripcion"]),
            estado,
            f'{criterio["puntos"]}/{criterio["maximo"]}'
        ])

    if "error" in resultado:
        mensaje = escape(resultado["error"])
    else:
        mensaje = (
            f"Has obtenido {puntuacion:g} "
            f"de {maximo:g} puntos."
        )

    return {
        "fraction": fraccion,
        "prologuehtml": f"<p>{mensaje}</p>",
        "testresults": filas
    }


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Uso: python3 adaptar_coderunner.py rubrica.json")

    codigo = sys.stdin.read()

    with open(sys.argv[1], encoding="utf-8") as archivo:
        rubrica = json.load(archivo)

    print(json.dumps(
        adaptar(codigo, rubrica),
        ensure_ascii=False
    ))
