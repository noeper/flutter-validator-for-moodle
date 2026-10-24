import analizar_dart as a

codigo = open("prueba_stateful.dart", encoding="utf-8").read()
datos = codigo.encode("utf-8")

parser = a.lib.ts_parser_new()
tree = None

try:
    lenguaje = a.lib.tree_sitter_dart()

    if not a.lib.ts_parser_set_language(parser, lenguaje):
        raise RuntimeError("Gramatica Dart incompatible")

    tree = a.lib.ts_parser_parse_string(
        parser, None, datos, len(datos)
    )

    raiz = a.lib.ts_tree_root_node(tree)

    for nodo in a.recorrer_nodos(raiz):
        texto = a.texto_nodo(nodo, datos)

        if texto == "StatefulWidget":
            print("NODO ENCONTRADO")
            print("------------------------")

            actual = nodo

            for nivel in range(7):
                print(
                    "Nivel:", nivel,
                    "| Tipo:", a.tipo_nodo(actual),
                    "| Texto:", " ".join(
                        a.texto_nodo(actual, datos).split()
                    )[:150]
                )

                actual = a.lib.ts_node_parent(actual)

            break
    else:
        print("No se encontro el nodo StatefulWidget")

finally:
    if tree:
        a.lib.ts_tree_delete(tree)
    a.lib.ts_parser_delete(parser)
