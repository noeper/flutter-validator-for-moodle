import json
import sys
from copy import deepcopy

from extraer_arbol import extraer
from extraer_clases import extraer_clases
from extraer_estado import extraer_estado


def analizar_flutter(codigo):
    arbol = extraer(codigo)
    clases = extraer_clases(codigo)
    estado = extraer_estado(codigo)

    if not arbol["sintaxis_correcta"] or not clases["sintaxis_correcta"]:
        return {"sintaxis_correcta": False, "objetos": []}

    indice = {
        clase["nombre"]: clase
        for clase in clases["clases"]
        if clase["nombre"]
    }

    def resolver(elemento, visitadas=frozenset()):
        if isinstance(elemento, list):
            return [resolver(item, visitadas) for item in elemento]

        if not isinstance(elemento, dict):
            return elemento

        resultado = {
            clave: resolver(valor, visitadas)
            for clave, valor in elemento.items()
        }

        nombre = elemento.get("tipo")

        if nombre in indice:
            clase = indice[nombre]

            if nombre in visitadas:
                resultado["resolucion"] = "REFERENCIA_CIRCULAR"
            elif clase["build"] is not None:
                resultado["implementacion"] = resolver(
                    deepcopy(clase["build"]),
                    visitadas | {nombre}
                )
            else:
                resultado["resolucion"] = "BUILD_NO_RESUELTO"

        return resultado

    return {
        "sintaxis_correcta": True,
        "objetos": resolver(arbol["objetos"]),
        "clases": clases["clases"],
        "estado": estado,
    }


if __name__ == "__main__":
    codigo = sys.stdin.read()
    print(json.dumps(
        analizar_flutter(codigo),
        ensure_ascii=False,
        indent=2
    ))
