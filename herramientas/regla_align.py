def comprobar_align_redundante(raiz, fuente):
    """Busca Align que envuelven directamente un Container."""

    for nodo in recorrer_nodos(raiz):
        if tipo_nodo(nodo) != "call_expression":
            continue

        hijos = [
            lib.ts_node_child(nodo, i)
            for i in range(lib.ts_node_child_count(nodo))
        ]

        if not hijos:
            continue

        if tipo_nodo(hijos[0]) != "identifier":
            continue

        if texto_nodo(hijos[0], fuente) != "Align":
            continue

        argumentos = next(
            (h for h in hijos if tipo_nodo(h) == "arguments"),
            None
        )

        if argumentos is None:
            continue

        propiedades = {}

        for argumento in recorrer_nodos(argumentos):
            if tipo_nodo(argumento) != "named_argument":
                continue

            padre = lib.ts_node_parent(argumento)

            if (
                lib.ts_node_start_byte(padre) != lib.ts_node_start_byte(argumentos)
                or lib.ts_node_end_byte(padre) != lib.ts_node_end_byte(argumentos)
            ):
                continue

            texto = texto_nodo(argumento, fuente)
            nombre, _, valor = texto.partition(":")
            propiedades[nombre.strip()] = valor.strip()

        hijo = propiedades.get("child", "")

        if hijo.startswith("Container(") or hijo.startswith("const Container("):
            linea = lib.ts_node_start_point(nodo).row + 1

            print(
                "AVISO [linea {}]: Align envuelve directamente un Container.".format(linea)
            )
            print(
                "Revisar si puede utilizarse la propiedad alignment del Container."
            )
            print(
                "Penalizacion propuesta: ninguna (requiere revision)."
            )
