import json
import sys

import analizar_dart as dart
from extraer_arbol import convertir, hijos


def buscar_build(clase, fuente):
    for nodo in dart.recorrer_nodos(clase):
        if dart.tipo_nodo(nodo) != "method_declaration":
            continue

        firmas = [
            h for h in hijos(nodo)
            if dart.tipo_nodo(h) == "method_signature"
        ]

        if not firmas:
            continue

        nombres = [
            dart.texto_nodo(h, fuente)
            for h in dart.recorrer_nodos(firmas[0])
            if dart.tipo_nodo(h) == "identifier"
        ]

        if "build" not in nombres:
            continue

        cuerpos = [
            h for h in hijos(nodo)
            if dart.tipo_nodo(h) == "function_body"
        ]

        if not cuerpos:
            return None

        cuerpo = cuerpos[0]

        # Caso: Widget build(...) => Container(...)
        for h in hijos(cuerpo):
            if dart.tipo_nodo(h) in (
                "call_expression",
                "const_object_expression"
            ):
                return convertir(h, fuente)

        # Caso: Widget build(...) { return Container(...); }
        for h in dart.recorrer_nodos(cuerpo):
            if dart.tipo_nodo(h) != "return_statement":
                continue

            for valor in hijos(h):
                if dart.tipo_nodo(valor) in (
                    "call_expression",
                    "const_object_expression"
                ):
                    return convertir(valor, fuente)

        return None

    return None


def extraer_clases(codigo):
    fuente = codigo.encode("utf-8")
    parser = dart.lib.ts_parser_new()
    arbol = None

    try:
        if not dart.lib.ts_parser_set_language(
            parser, dart.lib.tree_sitter_dart()
        ):
            raise RuntimeError("No se pudo cargar la gramática Dart")

        arbol = dart.lib.ts_parser_parse_string(
            parser, None, fuente, len(fuente)
        )

        raiz = dart.lib.ts_tree_root_node(arbol)

        if dart.lib.ts_node_has_error(raiz):
            return {"sintaxis_correcta": False, "clases": []}

        clases = []

        for nodo in dart.recorrer_nodos(raiz):
            if dart.tipo_nodo(nodo) != "class_declaration":
                continue

            nombre = next(
                (
                    dart.texto_nodo(h, fuente)
                    for h in hijos(nodo)
                    if dart.tipo_nodo(h) == "identifier"
                ),
                None
            )

            herencia = next(
                (
                    dart.texto_nodo(h, fuente)
                    for h in hijos(nodo)
                    if dart.tipo_nodo(h) == "superclass"
                ),
                None
            )

            clases.append({
                "nombre": nombre,
                "herencia": herencia,
                "build": buscar_build(nodo, fuente)
            })

        return {
            "sintaxis_correcta": True,
            "clases": clases
        }

    finally:
        if arbol:
            dart.lib.ts_tree_delete(arbol)
        dart.lib.ts_parser_delete(parser)


if __name__ == "__main__":
    codigo = sys.stdin.read()
    print(json.dumps(
        extraer_clases(codigo),
        ensure_ascii=False,
        indent=2
    ))
