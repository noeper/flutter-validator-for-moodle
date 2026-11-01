
import ctypes
import os
import sys

# Cargar la biblioteca compilada
ruta = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "libdartparser.so"
)

lib = ctypes.CDLL(ruta)

# Declarar las funciones de Tree-sitter
lib.ts_parser_new.restype = ctypes.c_void_p

lib.tree_sitter_dart.restype = ctypes.c_void_p

lib.ts_parser_set_language.argtypes = [
    ctypes.c_void_p,
    ctypes.c_void_p
]
lib.ts_parser_set_language.restype = ctypes.c_bool

lib.ts_parser_parse_string.argtypes = [
    ctypes.c_void_p,
    ctypes.c_void_p,
    ctypes.c_char_p,
    ctypes.c_uint32
]
lib.ts_parser_parse_string.restype = ctypes.c_void_p

lib.ts_tree_root_node.argtypes = [ctypes.c_void_p]

# TSNode es una estructura, no un puntero.
class TSNode(ctypes.Structure):
    _fields_ = [
        ("context", ctypes.c_uint32 * 4),
        ("id", ctypes.c_void_p),
        ("tree", ctypes.c_void_p)
    ]

lib.ts_tree_root_node.restype = TSNode

lib.ts_node_has_error.argtypes = [TSNode]
lib.ts_node_has_error.restype = ctypes.c_bool

# Obtener el tipo de un nodo
lib.ts_node_type.argtypes = [TSNode]
lib.ts_node_type.restype = ctypes.c_char_p

# Obtener el número de hijos
lib.ts_node_child_count.argtypes = [TSNode]
lib.ts_node_child_count.restype = ctypes.c_uint32

# Obtener un hijo
lib.ts_node_child.argtypes = [
    TSNode,
    ctypes.c_uint32
]
lib.ts_node_child.restype = TSNode

# Obtener el nodo padre
lib.ts_node_parent.argtypes = [TSNode]
lib.ts_node_parent.restype = TSNode


# Obtener posiciones en el código fuente
lib.ts_node_start_byte.argtypes = [TSNode]
lib.ts_node_start_byte.restype = ctypes.c_uint32

lib.ts_node_end_byte.argtypes = [TSNode]
lib.ts_node_end_byte.restype = ctypes.c_uint32

# Posicion de un nodo en el codigo fuente
class TSPoint(ctypes.Structure):
    _fields_ = [
        ("row", ctypes.c_uint32),
        ("column", ctypes.c_uint32)
    ]

lib.ts_node_start_point.argtypes = [TSNode]
lib.ts_node_start_point.restype = TSPoint

lib.ts_tree_delete.argtypes = [ctypes.c_void_p]
lib.ts_parser_delete.argtypes = [ctypes.c_void_p]

def analizar(codigo):
    parser = lib.ts_parser_new()

    if not parser:
        raise RuntimeError("No se pudo crear el parser")

    tree = None

    try:
        lenguaje = lib.tree_sitter_dart()

        if not lib.ts_parser_set_language(parser, lenguaje):
            raise RuntimeError("Gramática Dart incompatible")

        datos = codigo.encode("utf-8")

        tree = lib.ts_parser_parse_string(
            parser,
            None,
            datos,
            len(datos)
        )

        if not tree:
            raise RuntimeError("No se pudo analizar el código")

        raiz = lib.ts_tree_root_node(tree)

        if lib.ts_node_has_error(raiz):
            print("ERROR_SINTAXIS")
        else:
            print("SINTAXIS_CORRECTA")
            comprobar_container_padding(raiz, datos)
            comprobar_stateful_widget(raiz, datos)
            comprobar_estructura_flutter(raiz, datos)
            comprobar_centrado(raiz, datos)
            # comprobar_align_redundante(raiz, datos)

    finally:
        if tree:
            lib.ts_tree_delete(tree)
        lib.ts_parser_delete(parser)




def recorrer_nodos(nodo):
    """Recorre recursivamente el árbol sintáctico."""
    yield nodo

    for i in range(lib.ts_node_child_count(nodo)):
        hijo = lib.ts_node_child(nodo, i)
        yield from recorrer_nodos(hijo)


def tipo_nodo(nodo):
    """Devuelve el tipo de nodo de Tree-sitter."""
    return lib.ts_node_type(nodo).decode("utf-8")


def texto_nodo(nodo, fuente):
    """Extrae el texto original de un nodo."""
    inicio = lib.ts_node_start_byte(nodo)
    fin = lib.ts_node_end_byte(nodo)
    return fuente[inicio:fin].decode("utf-8")


def explorar_widgets(raiz, fuente):
    """Muestra los nodos de invocación para estudiar
    cómo la gramática Dart representa los widgets.
    """


def explorar_widgets(raiz, fuente):
    """Muestra los nodos de invocación para estudiar
    cómo la gramática Dart representa los widgets.
    """

    for nodo in recorrer_nodos(raiz):
        if tipo_nodo(nodo) == "identifier" and texto_nodo(nodo, fuente) == "Container":
            print("\nESTRUCTURA DEL PRIMER CONTAINER:")

            actual = nodo

            for nivel in range(4):
                print(
                    "Nivel", nivel,
                    "| Tipo:", tipo_nodo(actual),
                    "| Texto:", " ".join(texto_nodo(actual, fuente).split())[:180]
                )

                lib.ts_node_parent.argtypes = [TSNode]
                lib.ts_node_parent.restype = TSNode
                actual = lib.ts_node_parent(actual)

            break

    return








def comprobar_container_padding(raiz, fuente):
    """Detecta Container utilizado únicamente para padding."""

    for nodo in recorrer_nodos(raiz):
        if tipo_nodo(nodo) != "call_expression":
            continue

        hijos = [
            lib.ts_node_child(nodo, i)
            for i in range(lib.ts_node_child_count(nodo))
        ]

        if not hijos:
            continue

        # Comprobar que la llamada es a Container
        if tipo_nodo(hijos[0]) != "identifier":
            continue

        if texto_nodo(hijos[0], fuente) != "Container":
            continue

        # Buscar sus argumentos nombrados
        propiedades = set()

        for hijo in hijos:
            if tipo_nodo(hijo) != "arguments":
                continue

            for argumento in recorrer_nodos(hijo):
                if tipo_nodo(argumento) == "named_argument":
                    # Solo argumentos directos de este Container
                    # (evitamos contar los de widgets anidados).
                    padre = lib.ts_node_parent(argumento)
                    if tipo_nodo(padre) != "arguments":
                        continue
                    if (
                        lib.ts_node_start_byte(padre)
                        != lib.ts_node_start_byte(hijo)
                        or lib.ts_node_end_byte(padre)
                        != lib.ts_node_end_byte(hijo)
                    ):
                        continue

                    nombre = texto_nodo(argumento, fuente).split(":", 1)[0].strip()
                    propiedades.add(nombre)




        if propiedades == {"padding", "child"}:
            posicion = lib.ts_node_start_point(nodo)
            linea = posicion.row + 1

            print(
                "ADVERTENCIA [linea {}]: Container utilizado solo para padding.".format(linea)
            )
            print("Recomendacion: utilizar Padding.")
            print("Penalizacion propuesta: 0.25 puntos.")





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



def comprobar_stateful_widget(raiz, fuente):
    """Detecta clases que heredan directamente de StatefulWidget."""

    for nodo in recorrer_nodos(raiz):
        if tipo_nodo(nodo) != "class_declaration":
            continue

        for hijo in recorrer_nodos(nodo):
            if tipo_nodo(hijo) != "superclass":
                continue

            for descendiente in recorrer_nodos(hijo):
                if (
                    tipo_nodo(descendiente) == "type"
                    and texto_nodo(descendiente, fuente) == "StatefulWidget"
                ):
                    linea = lib.ts_node_start_point(nodo).row + 1
                    print(
                        "STATEFUL_WIDGET_DETECTADO [linea {}]".format(linea)
                    )
                    break



def comprobar_estructura_flutter(raiz, fuente):
    """Identifica componentes basicos de la aplicacion Flutter."""

    stateless = False
    scaffold = False
    materialapp = False

    for nodo in recorrer_nodos(raiz):
        tipo = tipo_nodo(nodo)
        texto = texto_nodo(nodo, fuente)

        if tipo == "class_declaration":
            for hijo in recorrer_nodos(nodo):
                if tipo_nodo(hijo) == "superclass":
                    for descendiente in recorrer_nodos(hijo):
                        if (
                            tipo_nodo(descendiente) == "type"
                            and texto_nodo(descendiente, fuente) == "StatelessWidget"
                        ):
                            stateless = True

        if tipo == "call_expression":
            primer_hijo = lib.ts_node_child(nodo, 0)

            if tipo_nodo(primer_hijo) == "identifier":
                nombre = texto_nodo(primer_hijo, fuente)

                if nombre == "Scaffold":
                    scaffold = True

                if nombre == "MaterialApp":
                    materialapp = True

    print("ESTRUCTURA_STATELESS:", int(stateless))
    print("ESTRUCTURA_SCAFFOLD:", int(scaffold))
    print("ESTRUCTURA_MATERIALAPP:", int(materialapp))



def comprobar_centrado(raiz, fuente):
    """Detecta patrones de centrado directamente en Scaffold.body."""

    for nodo in recorrer_nodos(raiz):
        if tipo_nodo(nodo) != "call_expression":
            continue

        hijos = [
            lib.ts_node_child(nodo, i)
            for i in range(lib.ts_node_child_count(nodo))
        ]

        if not hijos or tipo_nodo(hijos[0]) != "identifier":
            continue

        if texto_nodo(hijos[0], fuente) != "Scaffold":
            continue

        for hijo in hijos:
            if tipo_nodo(hijo) != "arguments":
                continue

            for argumento in recorrer_nodos(hijo):
                if tipo_nodo(argumento) != "named_argument":
                    continue

                padre = lib.ts_node_parent(argumento)

                if (
                    lib.ts_node_start_byte(padre) != lib.ts_node_start_byte(hijo)
                    or lib.ts_node_end_byte(padre) != lib.ts_node_end_byte(hijo)
                ):
                    continue

                partes = [
                    lib.ts_node_child(argumento, i)
                    for i in range(lib.ts_node_child_count(argumento))
                ]

                if not partes:
                    continue

                etiqueta = texto_nodo(partes[0], fuente).strip()

                if etiqueta != "body:":
                    continue

                llamadas = [
                    p for p in partes
                    if tipo_nodo(p) == "call_expression"
                ]

                if not llamadas:
                    continue

                cuerpo = llamadas[0]
                nombre = texto_nodo(
                    lib.ts_node_child(cuerpo, 0), fuente
                )

                horizontal = False
                vertical = False

                if nombre == "Center":
                    horizontal = True
                    vertical = True

                elif nombre == "Align":
                    argumentos_align = [
                        lib.ts_node_child(cuerpo, i)
                        for i in range(lib.ts_node_child_count(cuerpo))
                        if tipo_nodo(lib.ts_node_child(cuerpo, i)) == "arguments"
                    ]

                    alineacion = None

                    for args in argumentos_align:
                        for arg in recorrer_nodos(args):
                            if tipo_nodo(arg) != "named_argument":
                                continue

                            padre = lib.ts_node_parent(arg)

                            if (
                                lib.ts_node_start_byte(padre) != lib.ts_node_start_byte(args)
                                or lib.ts_node_end_byte(padre) != lib.ts_node_end_byte(args)
                            ):
                                continue

                            partes_arg = texto_nodo(arg, fuente).split(":", 1)

                            if len(partes_arg) == 2 and partes_arg[0].strip() == "alignment":
                                alineacion = partes_arg[1].strip()

                    if alineacion == "Alignment.center":
                        horizontal = True
                        vertical = True
                    elif alineacion in ("Alignment.topCenter", "Alignment.bottomCenter"):
                        horizontal = True
                    elif alineacion in ("Alignment.centerLeft", "Alignment.centerRight"):
                        vertical = True

                print("CENTRADO_HORIZONTAL:", int(horizontal))
                print("CENTRADO_VERTICAL:", int(vertical))
                return

    print("CENTRADO_HORIZONTAL: 0")
    print("CENTRADO_VERTICAL: 0")


if __name__ == "__main__":
    codigo = sys.stdin.read()
    analizar(codigo)
