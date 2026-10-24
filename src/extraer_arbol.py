import json
import sys

import analizar_dart as dart


def hijos(nodo):
    return [
        dart.lib.ts_node_child(nodo, i)
        for i in range(dart.lib.ts_node_child_count(nodo))
    ]


def convertir(nodo, fuente):
    tipo = dart.tipo_nodo(nodo)
    elementos = hijos(nodo)

    if tipo in ("call_expression", "const_object_expression"):
        if tipo == "call_expression":
            candidatos = [
                h for h in elementos
                if dart.tipo_nodo(h) in ("identifier", "member_expression")
            ]
        else:
            candidatos = [
                h for h in elementos
                if dart.tipo_nodo(h) == "type"
            ]

        if not candidatos:
            return dart.texto_nodo(nodo, fuente)

        nombre = dart.texto_nodo(candidatos[0], fuente)

        resultado = {
            "tipo": nombre,
            "linea": dart.lib.ts_node_start_point(nodo).row + 1,
            "propiedades": {},
            "argumentos_posicionales": []
        }

        for elemento in elementos:
            if dart.tipo_nodo(elemento) != "arguments":
                continue

            for argumento in hijos(elemento):
                tipo_argumento = dart.tipo_nodo(argumento)

                if tipo_argumento in ("(", ")", ","):
                    continue

                if tipo_argumento != "named_argument":
                    resultado["argumentos_posicionales"].append(
                        convertir(argumento, fuente)
                    )
                    continue

                partes = hijos(argumento)

                if len(partes) < 2:
                    continue

                etiqueta = partes[0]

                if dart.tipo_nodo(etiqueta) != "label":
                    continue

                nombre_propiedad = (
                    dart.texto_nodo(etiqueta, fuente)
                    .rstrip(":")
                    .strip()
                )

                valores = [
                    p for p in partes[1:]
                    if dart.tipo_nodo(p) != ":"
                ]

                if valores:
                    resultado["propiedades"][nombre_propiedad] = convertir(
                        valores[0], fuente
                    )

        return resultado

    if tipo == "list_literal":
        return [
            convertir(elemento, fuente)
            for elemento in elementos
            if dart.tipo_nodo(elemento)
            not in ("[", "]", ",")
        ]

    return dart.texto_nodo(nodo, fuente)


def extraer(codigo):
    fuente = codigo.encode("utf-8")
    parser = dart.lib.ts_parser_new()
    arbol = None

    try:
        lenguaje = dart.lib.tree_sitter_dart()

        if not dart.lib.ts_parser_set_language(parser, lenguaje):
            raise RuntimeError("No se pudo cargar la gramática Dart")

        arbol = dart.lib.ts_parser_parse_string(
            parser, None, fuente, len(fuente)
        )

        raiz = dart.lib.ts_tree_root_node(arbol)

        if dart.lib.ts_node_has_error(raiz):
            return {
                "sintaxis_correcta": False,
                "objetos": []
            }

        objetos = []

        for nodo in dart.recorrer_nodos(raiz):
            if dart.tipo_nodo(nodo) not in (
                "call_expression",
                "const_object_expression"
            ):
                continue

            # Conservamos solo construcciones que no estén
            # dentro de otra llamada o constructor.
            padre = dart.lib.ts_node_parent(nodo)
            anidado = False

            while dart.tipo_nodo(padre) != "source_file":
                if dart.tipo_nodo(padre) in (
                    "call_expression",
                    "const_object_expression"
                ):
                    anidado = True
                    break

                siguiente = dart.lib.ts_node_parent(padre)

                if dart.lib.ts_node_start_byte(siguiente) == dart.lib.ts_node_start_byte(padre) and dart.lib.ts_node_end_byte(siguiente) == dart.lib.ts_node_end_byte(padre):
                    break

                padre = siguiente

            if not anidado:
                objetos.append(convertir(nodo, fuente))

        return {
            "sintaxis_correcta": True,
            "objetos": objetos
        }

    finally:
        if arbol:
            dart.lib.ts_tree_delete(arbol)
        dart.lib.ts_parser_delete(parser)


if __name__ == "__main__":
    codigo = sys.stdin.read()
    print(json.dumps(extraer(codigo), ensure_ascii=False, indent=2))
