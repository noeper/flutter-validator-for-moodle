"""Extrae hechos reutilizables sobre estado y callbacks de código Dart."""

import re

import analizar_dart as dart
from extraer_arbol import hijos


def _texto(nodo, fuente):
    return dart.texto_nodo(nodo, fuente)


def _nombre_clase(nodo, fuente):
    return next(
        (_texto(h, fuente) for h in hijos(nodo)
         if dart.tipo_nodo(h) == "identifier"),
        None,
    )


def _propiedades_llamada(nodo, fuente):
    propiedades = {}
    argumentos = []
    for parte in hijos(nodo):
        if dart.tipo_nodo(parte) != "arguments":
            continue
        for argumento in hijos(parte):
            tipo = dart.tipo_nodo(argumento)
            if tipo in ("(", ")", ","):
                continue
            if tipo != "named_argument":
                argumentos.append(_texto(argumento, fuente))
                continue
            piezas = hijos(argumento)
            if len(piezas) >= 2:
                nombre = _texto(piezas[0], fuente).rstrip(":").strip()
                valores = [p for p in piezas[1:] if dart.tipo_nodo(p) != ":"]
                if valores:
                    propiedades[nombre] = _texto(valores[0], fuente)
    return propiedades, argumentos


def extraer_estado(codigo):
    fuente = codigo.encode("utf-8")
    parser = dart.lib.ts_parser_new()
    arbol = None
    try:
        if not dart.lib.ts_parser_set_language(parser, dart.lib.tree_sitter_dart()):
            raise RuntimeError("No se pudo cargar la gramática Dart")
        arbol = dart.lib.ts_parser_parse_string(parser, None, fuente, len(fuente))
        raiz = dart.lib.ts_tree_root_node(arbol)
        if dart.lib.ts_node_has_error(raiz):
            return {"clases": [], "llamadas": []}

        clases = []
        for nodo in dart.recorrer_nodos(raiz):
            if dart.tipo_nodo(nodo) != "class_declaration":
                continue
            nombre = _nombre_clase(nodo, fuente)
            herencia = next(
                (_texto(h, fuente)[len("extends"):].strip()
                 for h in hijos(nodo) if dart.tipo_nodo(h) == "superclass"),
                None,
            )
            variables = []
            cuerpo = next((h for h in hijos(nodo)
                           if dart.tipo_nodo(h) == "class_body"), None)
            if cuerpo is not None:
                for miembro in hijos(cuerpo):
                    if dart.tipo_nodo(miembro) != "class_member":
                        continue
                    declaraciones = [h for h in hijos(miembro)
                                     if dart.tipo_nodo(h) == "declaration"]
                    if not declaraciones:
                        continue
                    texto = _texto(declaraciones[0], fuente).strip()
                    coincidencia = re.fullmatch(
                        r"(?:final\s+|late\s+)?([A-Za-z_]\w*(?:<[^>]+>)?)\s+"
                        r"([A-Za-z_]\w*)\s*=\s*(.+)", texto, re.S)
                    if coincidencia:
                        variables.append({
                            "tipo": coincidencia.group(1),
                            "nombre": coincidencia.group(2),
                            "valor_inicial": coincidencia.group(3).strip(),
                        })
            clases.append({
                "nombre": nombre,
                "herencia": herencia,
                "variables": variables,
                "codigo": _texto(nodo, fuente),
            })

        llamadas = []
        for nodo in dart.recorrer_nodos(raiz):
            if dart.tipo_nodo(nodo) not in ("call_expression", "const_object_expression"):
                continue
            partes = hijos(nodo)
            candidatos = [h for h in partes if dart.tipo_nodo(h) in
                          ("identifier", "member_expression", "type")]
            if not candidatos:
                continue
            propiedades, argumentos = _propiedades_llamada(nodo, fuente)
            llamadas.append({
                "nombre": _texto(candidatos[0], fuente),
                "propiedades": propiedades,
                "argumentos": argumentos,
                "codigo": _texto(nodo, fuente),
            })
        return {"clases": clases, "llamadas": llamadas}
    finally:
        if arbol:
            dart.lib.ts_tree_delete(arbol)
        dart.lib.ts_parser_delete(parser)
