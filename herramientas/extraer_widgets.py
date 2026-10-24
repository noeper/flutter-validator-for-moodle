import json
import sys

import analizar_dart as dart


def extraer(codigo):
    datos = codigo.encode("utf-8")
    parser = dart.lib.ts_parser_new()
    arbol = None

    try:
        lenguaje = dart.lib.tree_sitter_dart()

        if not dart.lib.ts_parser_set_language(parser, lenguaje):
            raise RuntimeError("No se pudo cargar la gramática Dart")

        arbol = dart.lib.ts_parser_parse_string(
            parser, None, datos, len(datos)
        )

        raiz = dart.lib.ts_tree_root_node(arbol)

        resultado = {
            "sintaxis_correcta": not dart.lib.ts_node_has_error(raiz),
            "widgets": []
        }

        if not resultado["sintaxis_correcta"]:
            return resultado

        for nodo in dart.recorrer_nodos(raiz):
            tipo = dart.tipo_nodo(nodo)

            if tipo not in ("call_expression", "const_object_expression"):
                continue

            hijos = [
                dart.lib.ts_node_child(nodo, i)
                for i in range(dart.lib.ts_node_child_count(nodo))
            ]

            if not hijos:
                continue

            if tipo == "call_expression":
                if dart.tipo_nodo(hijos[0]) != "identifier":
                    continue
                nombre = dart.texto_nodo(hijos[0], datos)

            else:
                tipos = [
                    hijo for hijo in hijos
                    if dart.tipo_nodo(hijo) == "type"
                ]

                if not tipos:
                    continue

                nombre = dart.texto_nodo(tipos[0], datos)

            # Por ahora, registramos las llamadas con nombre
            # que empiezan por mayúscula.
            # Es una heurística, no una identificación definitiva
            # de clases Widget.
            if not nombre or not nombre[0].isupper():
                continue

            propiedades = {}

            for hijo in hijos:
                if dart.tipo_nodo(hijo) != "arguments":
                    continue

                for argumento in dart.recorrer_nodos(hijo):
                    if dart.tipo_nodo(argumento) != "named_argument":
                        continue

                    padre = dart.lib.ts_node_parent(argumento)

                    # Solo propiedades directas de esta llamada.
                    if (
                        dart.lib.ts_node_start_byte(padre)
                        != dart.lib.ts_node_start_byte(hijo)
                        or dart.lib.ts_node_end_byte(padre)
                        != dart.lib.ts_node_end_byte(hijo)
                    ):
                        continue

                    texto = dart.texto_nodo(argumento, datos)
                    nombre_propiedad, separador, valor = texto.partition(":")

                    if separador:
                        propiedades[nombre_propiedad.strip()] = valor.strip()

            linea = dart.lib.ts_node_start_point(nodo).row + 1

            resultado["widgets"].append({
                "tipo": nombre,
                "linea": linea,
                "propiedades": propiedades
            })

        return resultado

    finally:
        if arbol:
            dart.lib.ts_tree_delete(arbol)
        dart.lib.ts_parser_delete(parser)


if __name__ == "__main__":
    codigo = sys.stdin.read()
    print(json.dumps(extraer(codigo), ensure_ascii=False, indent=2))
