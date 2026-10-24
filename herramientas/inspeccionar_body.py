import analizar_dart as a

codigo = open("semaforo.dart", encoding="utf-8").read()
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
        if a.tipo_nodo(nodo) != "named_argument":
            continue

        texto = a.texto_nodo(nodo, datos)

        if not texto.lstrip().startswith("body:"):
            continue

        print("ARGUMENTO BODY ENCONTRADO")
        print("------------------------")

        def mostrar(nodo, nivel=0):
            if nivel > 4:
                return

            tipo = a.tipo_nodo(nodo)
            contenido = " ".join(
                a.texto_nodo(nodo, datos).split()
            )[:110]

            print("  " * nivel + tipo + " | " + contenido)

            for i in range(a.lib.ts_node_child_count(nodo)):
                hijo = a.lib.ts_node_child(nodo, i)
                mostrar(hijo, nivel + 1)

        mostrar(nodo)
        break

    else:
        print("No se encontro el argumento body")

finally:
    if tree:
        a.lib.ts_tree_delete(tree)
    a.lib.ts_parser_delete(parser)
