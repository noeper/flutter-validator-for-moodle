import json
import re
import sys

from analizador_flutter import analizar_flutter


def iterar_widgets(elemento):
    """Recorre los widgets y constructores representados en el análisis."""
    if isinstance(elemento, list):
        for item in elemento:
            yield from iterar_widgets(item)
    elif isinstance(elemento, dict):
        if "tipo" in elemento:
            yield elemento
        for valor in elemento.values():
            yield from iterar_widgets(valor)


def widgets_directos(elemento):
    """Devuelve los widgets contenidos inmediatamente por un nodo."""
    if not isinstance(elemento, dict):
        return []

    valores = list(elemento.get("propiedades", {}).values())
    valores += elemento.get("argumentos_posicionales", [])
    if "implementacion" in elemento:
        valores.append(elemento["implementacion"])

    resultado = []
    for valor in valores:
        if isinstance(valor, dict) and "tipo" in valor:
            resultado.append(valor)
        elif isinstance(valor, list):
            resultado.extend(
                item for item in valor
                if isinstance(item, dict) and "tipo" in item
            )
    return resultado


def contiene_widget(elemento, padre, hijo):
    def buscar(nodo):
        if isinstance(nodo, list):
            return any(buscar(item) for item in nodo)

        if not isinstance(nodo, dict):
            return False

        if nodo.get("tipo") == padre:
            if buscar_descendiente(nodo, hijo):
                return True

        return any(buscar(valor) for valor in nodo.values())

    def buscar_descendiente(nodo, nombre):
        for clave, valor in nodo.items():
            if clave == "tipo":
                continue

            if isinstance(valor, dict):
                if valor.get("tipo") == nombre:
                    return True
                if buscar_descendiente(valor, nombre):
                    return True

            elif isinstance(valor, list):
                for item in valor:
                    if isinstance(item, dict):
                        if item.get("tipo") == nombre:
                            return True
                        if buscar_descendiente(item, nombre):
                            return True

        return False

    return buscar(elemento)



def propiedad_widget(elemento, widget, propiedad, valor):
    """Comprueba si un widget tiene una propiedad con el valor esperado."""
    if isinstance(elemento, list):
        return any(
            propiedad_widget(item, widget, propiedad, valor)
            for item in elemento
        )

    if not isinstance(elemento, dict):
        return False

    if elemento.get("tipo") == widget:
        propiedades = elemento.get("propiedades", {})
        if propiedades.get(propiedad) == valor:
            return True

    return any(
        propiedad_widget(v, widget, propiedad, valor)
        for v in elemento.values()
    )


def propiedades_widget(elemento, widget, propiedades):
    """Exige varias propiedades en una misma instancia del widget."""
    return any(
        nodo.get("tipo") == widget
        and all(
            nodo.get("propiedades", {}).get(nombre) == valor
            for nombre, valor in propiedades.items()
        )
        for nodo in iterar_widgets(elemento)
    )


def argumento_widget(elemento, widget, posicion, valor):
    """Comprueba un argumento posicional de un constructor o widget."""
    for nodo in iterar_widgets(elemento):
        argumentos = nodo.get("argumentos_posicionales", [])
        if (
            nodo.get("tipo") == widget
            and 0 <= posicion < len(argumentos)
            and argumentos[posicion] == valor
        ):
            return True
    return False


def jerarquia_widgets(elemento, ruta, relacion="descendiente"):
    """Busca una ruta de widgets mediante hijos directos o descendientes."""
    if not ruta:
        return False

    def continuar(nodo, restantes):
        if not restantes:
            return True
        candidatos = (
            widgets_directos(nodo)
            if relacion == "hijo_directo"
            else list(iterar_widgets(widgets_directos(nodo)))
        )
        return any(
            candidato.get("tipo") == restantes[0]
            and continuar(candidato, restantes[1:])
            for candidato in candidatos
        )

    return any(
        nodo.get("tipo") == ruta[0] and continuar(nodo, ruta[1:])
        for nodo in iterar_widgets(elemento)
    )


def cantidad_widget(elemento, widget, cantidad, dentro_de=None,
                    relacion="descendiente", comparador="igual"):
    """Cuenta widgets globalmente o dentro de cada widget indicado."""
    def comparar(valor):
        operaciones = {
            "igual": valor == cantidad,
            "minimo": valor >= cantidad,
            "maximo": valor <= cantidad
        }
        if comparador not in operaciones:
            raise ValueError(f"Comparador no implementado: {comparador}")
        return operaciones[comparador]

    if dentro_de:
        for padre in iterar_widgets(elemento):
            if padre.get("tipo") != dentro_de:
                continue
            candidatos = (
                widgets_directos(padre)
                if relacion == "hijo_directo"
                else list(iterar_widgets(widgets_directos(padre)))
            )
            if comparar(sum(n.get("tipo") == widget for n in candidatos)):
                return True
        return False

    unicos = {
        (nodo.get("tipo"), nodo.get("linea"))
        for nodo in iterar_widgets(elemento)
        if nodo.get("tipo") == widget
    }
    return comparar(len(unicos))


def secuencia_hijos(elemento, padre, hijos, propiedad="children"):
    """Comprueba la secuencia exacta de widgets de una propiedad lista."""
    for nodo in iterar_widgets(elemento):
        if nodo.get("tipo") != padre:
            continue
        contenido = nodo.get("propiedades", {}).get(propiedad)
        if isinstance(contenido, list):
            tipos = [
                item.get("tipo") for item in contenido
                if isinstance(item, dict) and "tipo" in item
            ]
            if tipos == hijos:
                return True
    return False


def ruta_propiedad(elemento, widget, ruta, tipo_final=None,
                   argumentos=None, valor=None):
    """Sigue propiedades anidadas desde una misma instancia de widget."""
    for nodo in iterar_widgets(elemento):
        if nodo.get("tipo") != widget:
            continue
        actual = nodo
        for nombre in ruta:
            if not isinstance(actual, dict):
                break
            propiedades = actual.get("propiedades", {})
            if nombre not in propiedades:
                break
            actual = propiedades[nombre]
        else:
            if tipo_final is not None and (
                not isinstance(actual, dict)
                or actual.get("tipo") != tipo_final
            ):
                continue
            if argumentos is not None and (
                not isinstance(actual, dict)
                or actual.get("argumentos_posicionales") != argumentos
            ):
                continue
            if valor is not None and actual != valor:
                continue
            return True
    return False


def valor_ruta(nodo, ruta):
    actual = nodo
    for nombre in ruta:
        if not isinstance(actual, dict):
            return None
        actual = actual.get("propiedades", {}).get(nombre)
    return actual


def widgets_en_ambito(elemento, padre, widget, relacion="hijo_directo"):
    if padre is None:
        unicos = {}
        for nodo in iterar_widgets(elemento):
            if nodo.get("tipo") == widget:
                clave = (nodo.get("tipo"), nodo.get("linea"))
                unicos.setdefault(clave, nodo)
        yield list(unicos.values())
        return

    for ambito in iterar_widgets(elemento):
        if ambito.get("tipo") != padre:
            continue
        candidatos = (widgets_directos(ambito) if relacion == "hijo_directo"
                      else list(iterar_widgets(widgets_directos(ambito))))
        yield [n for n in candidatos if n.get("tipo") == widget]


def cantidad_widget_filtrado(elemento, padre, widget, cantidad, filtros,
                             relacion="hijo_directo"):
    for candidatos in widgets_en_ambito(elemento, padre, widget, relacion):
        validos = [n for n in candidatos if all(
            valor_ruta(n, f["ruta"]) == f["valor"] for f in filtros
        )]
        if len(validos) == cantidad:
            return True
    return False


def valores_widgets(elemento, padre, widget, ruta, valores,
                     relacion="hijo_directo"):
    esperados = sorted(valores)
    return any(
        sorted(valor_ruta(n, ruta) for n in candidatos) == esperados
        for candidatos in widgets_en_ambito(elemento, padre, widget, relacion)
        if len(candidatos) == len(valores)
    )


def dimensiones_uniformes(elemento, padre, widget, cantidad,
                          relacion="hijo_directo"):
    for candidatos in widgets_en_ambito(elemento, padre, widget, relacion):
        pares = [
            (valor_ruta(n, ["width"]), valor_ruta(n, ["height"]))
            for n in candidatos
        ]
        if (len(pares) == cantidad and all(a is not None and a == b for a, b in pares)
                and len(set(pares)) == 1):
            return True
    return False


def envoltorio_layout(elemento, widget, hijo, propiedades):
    """Comprueba un widget dimensionador que envuelve el layout indicado."""
    for nodo in iterar_widgets(elemento):
        if nodo.get("tipo") != widget:
            continue
        props = nodo.get("propiedades", {})
        if not all(nombre in props for nombre in propiedades):
            continue
        if any(
            descendiente.get("tipo") == hijo
            for descendiente in iterar_widgets(widgets_directos(nodo))
        ):
            return True
    return False


def propiedades_exactas_en_ambito(elemento, padre, widget, cantidad,
                                  propiedades, relacion="descendiente"):
    esperadas = set(propiedades)
    return any(
        len(candidatos) == cantidad
        and all(set(n.get("propiedades", {})) == esperadas for n in candidatos)
        for candidatos in widgets_en_ambito(elemento, padre, widget, relacion)
    )


def propiedades_requeridas_en_ambito(elemento, padre, widget, cantidad,
                                     propiedades, relacion="descendiente"):
    """Exige ciertas propiedades, permitiendo propiedades adicionales."""
    requeridas = set(propiedades)
    return any(
        len(candidatos) == cantidad
        and all(
            requeridas.issubset(set(n.get("propiedades", {})))
            for n in candidatos
        )
        for candidatos in widgets_en_ambito(elemento, padre, widget, relacion)
    )


def hijos_expandidos_equivalentes(elemento, padre, cantidad, hijo):
    """Exige Expanded hermanos con igual flex y el mismo tipo de contenido."""
    for nodo in iterar_widgets(elemento):
        if nodo.get("tipo") != padre:
            continue
        candidatos = widgets_directos(nodo)
        if len(candidatos) != cantidad:
            continue
        if any(n.get("tipo") != "Expanded" for n in candidatos):
            continue
        flex = [n.get("propiedades", {}).get("flex", "1") for n in candidatos]
        if len(set(flex)) != 1:
            continue
        if all(any(
            d.get("tipo") == hijo
            for d in iterar_widgets(widgets_directos(n))
        ) for n in candidatos):
            return True
    return False


def _numero_positivo(valor):
    """Reconoce literales numéricos positivos sin ejecutar código Dart."""
    try:
        return float(valor) > 0
    except (TypeError, ValueError):
        return False


def _lados_edge_insets(nodo):
    """Normaliza los constructores EdgeInsets habituales a L, T, R, B."""
    if not isinstance(nodo, dict):
        return None
    tipo = nodo.get("tipo")
    props = nodo.get("propiedades", {})
    args = nodo.get("argumentos_posicionales", [])
    if tipo == "EdgeInsets.symmetric":
        horizontal = props.get("horizontal", "0")
        vertical = props.get("vertical", "0")
        return horizontal, vertical, horizontal, vertical
    if tipo == "EdgeInsets.only":
        return (props.get("left", "0"), props.get("top", "0"),
                props.get("right", "0"), props.get("bottom", "0"))
    if tipo == "EdgeInsets.fromLTRB" and len(args) == 4:
        return tuple(args)
    if tipo == "EdgeInsets.all" and len(args) == 1:
        return (args[0],) * 4
    return None


def _cumple_requisito_ruta(actual, requisito):
    if "valor" in requisito and actual != requisito["valor"]:
        return False
    tipos = requisito.get("tipos_finales")
    if tipos is not None and (
        not isinstance(actual, dict) or actual.get("tipo") not in tipos
    ):
        return False
    if "tipo_final" in requisito and (
        not isinstance(actual, dict)
        or actual.get("tipo") != requisito["tipo_final"]
    ):
        return False
    if "argumentos" in requisito and (
        not isinstance(actual, dict)
        or actual.get("argumentos_posicionales") != requisito["argumentos"]
    ):
        return False
    if "argumento_positivo" in requisito:
        if not isinstance(actual, dict):
            return False
        indice = requisito["argumento_positivo"]
        argumentos = actual.get("argumentos_posicionales", [])
        if indice >= len(argumentos) or not _numero_positivo(argumentos[indice]):
            return False
    if "edge_insets" in requisito:
        lados = _lados_edge_insets(actual)
        esperado = requisito["edge_insets"]
        if lados != (esperado["left"], esperado["top"],
                     esperado["right"], esperado["bottom"]):
            return False
    return True


def _cumple_configuracion(nodo, configuracion):
    if nodo.get("tipo") != configuracion["tipo"]:
        return False
    propiedades = nodo.get("propiedades", {})
    if not all(propiedades.get(nombre) == valor for nombre, valor in
               configuracion.get("propiedades", {}).items()):
        return False
    if not all(nombre in propiedades
               for nombre in configuracion.get("propiedades_presentes", [])):
        return False
    if not all(_numero_positivo(propiedades.get(nombre))
               for nombre in configuracion.get("propiedades_positivas", [])):
        return False
    argumentos = configuracion.get("argumentos")
    if argumentos is not None and nodo.get("argumentos_posicionales") != argumentos:
        return False
    for requisito in configuracion.get("rutas", []):
        actual = valor_ruta(nodo, requisito["ruta"])
        if not _cumple_requisito_ruta(actual, requisito):
            return False
    hijo = configuracion.get("hijo")
    if hijo is not None and not any(
        _cumple_configuracion(candidato, hijo)
        for candidato in widgets_directos(nodo)
    ):
        return False
    return True


def secuencia_hijos_configurados(elemento, padre, hijos):
    """Comprueba tipo, propiedades y descendencia de hijos directos ordenados."""
    for nodo in iterar_widgets(elemento):
        if nodo.get("tipo") != padre:
            continue
        candidatos = widgets_directos(nodo)
        if len(candidatos) == len(hijos) and all(
            _cumple_configuracion(candidato, esperado)
            for candidato, esperado in zip(candidatos, hijos)
        ):
            return True
    return False


def widget_configurado(elemento, configuracion):
    """Busca una instancia que cumpla una configuración anidada completa."""
    return any(_cumple_configuracion(nodo, configuracion)
               for nodo in iterar_widgets(elemento))


def secuencia_flex_configurada(elemento, padre, proporcion, hijos):
    """Comprueba Expanded ordenados, normalizando flex omitido a uno."""
    for nodo in iterar_widgets(elemento):
        if nodo.get("tipo") != padre:
            continue
        candidatos = widgets_directos(nodo)
        if len(candidatos) != len(hijos):
            continue
        if any(c.get("tipo") != "Expanded" for c in candidatos):
            continue
        try:
            flex = [float(c.get("propiedades", {}).get("flex", "1"))
                    for c in candidatos]
            esperada = [float(valor) for valor in proporcion]
        except (TypeError, ValueError):
            continue
        if any(valor <= 0 for valor in flex + esperada):
            continue
        if any(flex[i] * esperada[0] != flex[0] * esperada[i]
               for i in range(len(flex))):
            continue
        if all(_cumple_configuracion(candidato, esperado)
               for candidato, esperado in zip(candidatos, hijos)):
            return True
    return False


def _normalizar(texto):
    return re.sub(r"\s+", "", texto or "")


def _clase_estado(analisis, widget=None):
    clases = analisis.get("estado", {}).get("clases", [])
    patron = re.compile(r"^State\s*<\s*([^>]+)\s*>$")
    for clase in clases:
        coincidencia = patron.match(clase.get("herencia") or "")
        if coincidencia and (widget is None or coincidencia.group(1) == widget):
            return clase
    return None


def _llamadas(analisis, nombre):
    return [l for l in analisis.get("estado", {}).get("llamadas", [])
            if l.get("nombre") == nombre]


def _variable_por_ancla(analisis, ancla, widget_estado=None):
    """Resuelve una variable por cómo se presenta en la interfaz."""
    clase = _clase_estado(analisis, widget_estado)
    if not clase:
        return None
    nombres = {v["nombre"] for v in clase["variables"]}
    for llamada in _llamadas(analisis, ancla["widget"]):
        if "texto_contiene" in ancla:
            codigo = llamada["codigo"]
            if ancla["texto_contiene"].casefold() not in codigo.casefold():
                continue
            usados = [n for n in nombres if re.search(
                rf"(?:\$\s*{re.escape(n)}\b|\$\{{\s*{re.escape(n)}\s*\}})", codigo)]
        else:
            valor = llamada["propiedades"].get(ancla.get("propiedad", "value"), "")
            usados = [n for n in nombres if _normalizar(valor) == n]
        if len(usados) == 1:
            return usados[0]
    return None


def _llamada_accion(analisis, selector):
    for llamada in _llamadas(analisis, selector["widget"]):
        codigo = llamada["codigo"]
        texto = selector.get("texto")
        if texto is not None and not re.search(
            rf"Text\s*\(\s*(?:const\s+)?['\"]{re.escape(texto)}['\"]", codigo):
            continue
        return llamada
    return None


def _cuerpos_set_state(callback):
    """Obtiene el texto encerrado en cada setState equilibrando paréntesis."""
    cuerpos = []
    for coincidencia in re.finditer(r"\bsetState\s*\(", callback or ""):
        inicio = coincidencia.end()
        nivel = 1
        for indice in range(inicio, len(callback)):
            if callback[indice] == "(":
                nivel += 1
            elif callback[indice] == ")":
                nivel -= 1
                if nivel == 0:
                    cuerpos.append(callback[inicio:indice])
                    break
    return cuerpos


def _cambia_variable(texto, variable, cambio):
    nombre = re.escape(variable)
    patrones = {
        "incrementar": [rf"\b{nombre}\s*\+\+", rf"\b{nombre}\s*\+=\s*1\b",
                        rf"\b{nombre}\s*=\s*{nombre}\s*\+\s*1\b"],
        "decrementar": [rf"\b{nombre}\s*--", rf"\b{nombre}\s*-=\s*1\b",
                        rf"\b{nombre}\s*=\s*{nombre}\s*-\s*1\b"],
        "asignar": [rf"\b{nombre}\s*=(?!=)"],
    }
    return any(re.search(p, texto) for p in patrones[cambio])


def clase_hereda_de(analisis, clase, herencia):
    return any(c.get("nombre") == clase and c.get("herencia") == herencia
               for c in analisis.get("estado", {}).get("clases", []))


def state_asociado_a_widget(analisis, widget):
    if not clase_hereda_de(analisis, widget, "StatefulWidget"):
        return False
    return _clase_estado(analisis, widget) is not None


def variable_estado(analisis, widget_estado, tipo, valor_inicial, ancla):
    nombre = _variable_por_ancla(analisis, ancla, widget_estado)
    clase = _clase_estado(analisis, widget_estado)
    return bool(nombre and any(
        v["nombre"] == nombre and v["tipo"] == tipo
        and _normalizar(v["valor_inicial"]) == _normalizar(valor_inicial)
        for v in clase["variables"]
    ))


def cantidad_variables_estado(analisis, widget_estado, tipo, valor_inicial,
                              cantidad, comparador="igual"):
    clase = _clase_estado(analisis, widget_estado)
    if not clase:
        return False
    total = sum(v["tipo"] == tipo and
                _normalizar(v["valor_inicial"]) == _normalizar(valor_inicial)
                for v in clase["variables"])
    return {"igual": total == cantidad, "minimo": total >= cantidad,
            "maximo": total <= cantidad}[comparador]


def widget_muestra_estado(analisis, widget_estado, ancla):
    return _variable_por_ancla(analisis, ancla, widget_estado) is not None


def funcion_recibe_estado(analisis, funcion, variables, widget_estado):
    nombres = [_variable_por_ancla(analisis, a, widget_estado) for a in variables]
    if any(n is None for n in nombres):
        return False
    esperados = [_normalizar(n) for n in nombres]
    return any([_normalizar(a) for a in l["argumentos"]] == esperados
               for l in _llamadas(analisis, funcion))


def callback_modifica_estado(analisis, selector, propiedad_callback, ancla,
                             cambio, widget_estado, dentro_de_set_state=True):
    variable = _variable_por_ancla(analisis, ancla, widget_estado)
    llamada = _llamada_accion(analisis, selector)
    if not variable or not llamada:
        return False
    callback = llamada["propiedades"].get(propiedad_callback, "")
    textos = _cuerpos_set_state(callback) if dentro_de_set_state else [callback]
    return any(_cambia_variable(texto, variable, cambio) for texto in textos)


def callback_bloqueado_por_estado(analisis, selector, propiedad_callback,
                                  ancla_bloqueo, widget_estado):
    variable = _variable_por_ancla(analisis, ancla_bloqueo, widget_estado)
    llamada = _llamada_accion(analisis, selector)
    if not variable or not llamada:
        return False
    callback = llamada["propiedades"].get(propiedad_callback, "")
    nombre = re.escape(variable)
    retorno = re.search(rf"\bif\s*\(\s*{nombre}\s*\)\s*(?:\{{\s*)?return\s*;", callback)
    condicionado = re.search(rf"\bif\s*\(\s*!\s*{nombre}\s*\)", callback)
    return bool(retorno or condicionado)


def valor_acotado(analisis, selector, propiedad_callback, ancla,
                  widget_estado, minimo=None, maximo=None):
    variable = _variable_por_ancla(analisis, ancla, widget_estado)
    llamada = _llamada_accion(analisis, selector)
    if not variable or not llamada:
        return False
    callback = llamada["propiedades"].get(propiedad_callback, "")
    nombre = re.escape(variable)
    comprobaciones = []
    if minimo is not None:
        comprobaciones.append(bool(
            re.search(rf"\bif\s*\(\s*{nombre}\s*>\s*{re.escape(str(minimo))}\s*\)", callback)
            or re.search(rf"\b{nombre}\s*=.*\.clamp\s*\(\s*{re.escape(str(minimo))}\s*,", callback)
            or re.search(rf"\bmax\s*\(\s*{re.escape(str(minimo))}\s*,", callback)
        ))
    if maximo is not None:
        comprobaciones.append(bool(
            re.search(rf"\bif\s*\(\s*{nombre}\s*<\s*{re.escape(str(maximo))}\s*\)", callback)
            or re.search(rf"\b{nombre}\s*=.*\.clamp\s*\([^,]+,\s*{re.escape(str(maximo))}\s*\)", callback)
            or re.search(rf"\bmin\s*\([^,]+,\s*{re.escape(str(maximo))}\s*\)", callback)
        ))
    return bool(comprobaciones) and all(comprobaciones)


def _fuente_clase(codigo, clase):
    """Texto de la clase (cabecera y cuerpo), equilibrando llaves."""
    coincidencia = re.search(rf"\bclass\s+{re.escape(clase)}\b[^{{]*\{{", codigo or "")
    if not coincidencia:
        return None
    nivel = 1
    for indice in range(coincidencia.end(), len(codigo)):
        if codigo[indice] == "{":
            nivel += 1
        elif codigo[indice] == "}":
            nivel -= 1
            if nivel == 0:
                return codigo[coincidencia.start():indice + 1]
    return None


def _sin_comentarios(codigo):
    codigo = re.sub(r"/\*.*?\*/", "", codigo or "", flags=re.S)
    return re.sub(r"//[^\n]*", "", codigo)


def clase_contiene(analisis, clase, patron):
    fuente = _fuente_clase(_sin_comentarios(analisis.get("codigo")), clase)
    return bool(fuente and re.search(patron, fuente, flags=re.S))


def codigo_contiene(analisis, patron):
    return bool(re.search(patron, _sin_comentarios(analisis.get("codigo")), flags=re.S))


def codigo_cuenta(analisis, patron, minimo=None, maximo=None):
    total = len(re.findall(patron, _sin_comentarios(analisis.get("codigo")), flags=re.S))
    return ((minimo is None or total >= minimo)
            and (maximo is None or total <= maximo))


def _fuente_estado(codigo, widget):
    """Texto de la clase State asociada al widget."""
    coincidencia = re.search(
        rf"\bclass\s+(\w+)\s+extends\s+State\s*<\s*{re.escape(widget)}\s*>", codigo or "")
    return _fuente_clase(codigo, coincidencia.group(1)) if coincidencia else None


def _argumentos_llamadas(fuente, nombre):
    """Texto entre los paréntesis de cada llamada nombre(...)."""
    resultado = []
    for coincidencia in re.finditer(rf"(?<![\w.]){re.escape(nombre)}\s*\(", fuente or ""):
        nivel = 1
        for indice in range(coincidencia.end(), len(fuente)):
            if fuente[indice] in "([{":
                nivel += 1
            elif fuente[indice] in ")]}":
                nivel -= 1
                if nivel == 0:
                    resultado.append(fuente[coincidencia.end():indice])
                    break
    return resultado


def _valor_argumento(argumentos, propiedad):
    """Expresión pasada a propiedad: en unos argumentos, o None."""
    coincidencia = re.search(rf"(?<![\w.]){re.escape(propiedad)}\s*:", argumentos)
    if not coincidencia:
        return None
    nivel = 0
    for indice in range(coincidencia.end(), len(argumentos)):
        caracter = argumentos[indice]
        if caracter in "([{":
            nivel += 1
        elif caracter in ")]}":
            nivel -= 1
        elif caracter == "," and nivel == 0:
            return argumentos[coincidencia.end():indice].strip()
    return argumentos[coincidencia.end():].strip()


def _fuente_ambito(analisis, criterio):
    codigo = _sin_comentarios(analisis.get("codigo"))
    if "estado_de" in criterio:
        return _fuente_estado(codigo, criterio["estado_de"])
    if "clase" in criterio:
        return _fuente_clase(codigo, criterio["clase"])
    return codigo


def ambito_contiene(analisis, criterio):
    fuente = _fuente_ambito(analisis, criterio)
    return bool(fuente and re.search(criterio["patron"], fuente, flags=re.S))


def ambito_cuenta(analisis, criterio):
    fuente = _fuente_ambito(analisis, criterio)
    total = len(re.findall(criterio["patron"], fuente or "", flags=re.S))
    return ((criterio.get("minimo") is None or total >= criterio["minimo"])
            and (criterio.get("maximo") is None or total <= criterio["maximo"]))


def llamadas_sin_propiedad(analisis, criterio):
    fuente = _fuente_ambito(analisis, criterio)
    total = sum(_valor_argumento(a, criterio["propiedad"]) is None
                for a in _argumentos_llamadas(fuente, criterio["llamada"]))
    return total >= criterio.get("minimo", 1)


def llamadas_con_propiedad(analisis, criterio):
    fuente = _fuente_ambito(analisis, criterio)
    valores = [_valor_argumento(a, criterio["propiedad"])
               for a in _argumentos_llamadas(fuente, criterio["llamada"])]
    valores = [v for v in valores if v is not None]
    if "patron_valor" in criterio:
        valores = [v for v in valores if re.search(criterio["patron_valor"], v, flags=re.S)]
    return len(valores) >= criterio.get("minimo", 1)


def textos_distintos_en_propiedad(analisis, criterio):
    """Cada valor de la propiedad aporta los textos literales que contiene."""
    fuente = _fuente_ambito(analisis, criterio)
    literales = re.compile(r"'(?:[^'\\]|\\.)*'|\"(?:[^\"\\]|\\.)*\"")
    distintos = set()
    for argumentos in _argumentos_llamadas(fuente, criterio["llamada"]):
        valor = _valor_argumento(argumentos, criterio["propiedad"])
        if valor:
            textos = tuple(t.strip() for t in literales.findall(valor) if len(t) > 2)
            if textos:
                distintos.add(textos)
    return len(distintos) >= criterio.get("minimo", 2)


def contador_en_llamada(analisis, criterio):
    """Un texto de la llamada (AppBar...) interpola una variable que se incrementa en setState."""
    fuente = _fuente_ambito(analisis, criterio) or ""
    nombres = set()
    for argumentos in _argumentos_llamadas(fuente, criterio["llamada"]):
        for literal in re.findall(r"'(?:[^'\\]|\\.)*'|\"(?:[^\"\\]|\\.)*\"", argumentos):
            nombres.update(re.findall(r"\$\{?\s*(_?[A-Za-z]\w*)", literal))
        nombres.update(re.findall(r"\b(_?[A-Za-z]\w*)\s*\.\s*toString\s*\(\s*\)", argumentos))
    for cuerpo in _cuerpos_set_state(fuente):
        for nombre in nombres:
            if _cambia_variable(cuerpo, nombre, "incrementar"):
                return True
    return False


def aplicar_regla(elemento, criterio, analisis=None):
    regla = criterio["regla"]
    if regla == "contador_en_llamada":
        return contador_en_llamada(analisis, criterio)
    if regla == "no":
        return not aplicar_regla(elemento, criterio["subregla"], analisis)
    if regla == "ambito_contiene":
        return ambito_contiene(analisis, criterio)
    if regla == "ambito_cuenta":
        return ambito_cuenta(analisis, criterio)
    if regla == "llamadas_sin_propiedad":
        return llamadas_sin_propiedad(analisis, criterio)
    if regla == "llamadas_con_propiedad":
        return llamadas_con_propiedad(analisis, criterio)
    if regla == "textos_distintos_en_propiedad":
        return textos_distintos_en_propiedad(analisis, criterio)
    if regla == "clase_contiene":
        return clase_contiene(analisis, criterio["clase"], criterio["patron"])
    if regla == "codigo_contiene":
        return codigo_contiene(analisis, criterio["patron"])
    if regla == "codigo_cuenta":
        return codigo_cuenta(analisis, criterio["patron"],
                             criterio.get("minimo"), criterio.get("maximo"))
    if regla == "todas":
        return all(aplicar_regla(elemento, subregla, analisis)
                   for subregla in criterio["reglas"])
    if regla == "alguna":
        return any(aplicar_regla(elemento, subregla, analisis)
                   for subregla in criterio["reglas"])
    if regla == "clase_hereda_de":
        return clase_hereda_de(analisis, criterio["clase"], criterio["herencia"])
    if regla == "state_asociado_a_widget":
        return state_asociado_a_widget(analisis, criterio["widget"])
    if regla == "variable_estado":
        return variable_estado(
            analisis, criterio["widget_estado"], criterio["tipo"],
            criterio["valor_inicial"], criterio["ancla"])
    if regla == "cantidad_variables_estado":
        return cantidad_variables_estado(
            analisis, criterio["widget_estado"], criterio["tipo"],
            criterio["valor_inicial"], criterio["cantidad"],
            criterio.get("comparador", "igual"))
    if regla == "widget_muestra_estado":
        return widget_muestra_estado(
            analisis, criterio["widget_estado"], criterio["ancla"])
    if regla == "funcion_recibe_estado":
        return funcion_recibe_estado(
            analisis, criterio["funcion"], criterio["variables"],
            criterio["widget_estado"])
    if regla == "callback_modifica_estado":
        return callback_modifica_estado(
            analisis, criterio["selector"],
            criterio.get("propiedad_callback", "onPressed"), criterio["ancla"],
            criterio["cambio"], criterio["widget_estado"],
            criterio.get("dentro_de_set_state", True))
    if regla == "callback_bloqueado_por_estado":
        return callback_bloqueado_por_estado(
            analisis, criterio["selector"],
            criterio.get("propiedad_callback", "onPressed"),
            criterio["ancla_bloqueo"], criterio["widget_estado"])
    if regla == "valor_acotado":
        return valor_acotado(
            analisis, criterio["selector"],
            criterio.get("propiedad_callback", "onPressed"), criterio["ancla"],
            criterio["widget_estado"], criterio.get("minimo"),
            criterio.get("maximo"))
    if regla == "contiene_widget":
        return contiene_widget(elemento, criterio["padre"], criterio["hijo"])
    if regla == "propiedad_widget":
        return propiedad_widget(elemento, criterio["widget"], criterio["propiedad"], criterio["valor"])
    if regla == "propiedades_widget":
        return propiedades_widget(elemento, criterio["widget"], criterio["propiedades"])
    if regla == "argumento_widget":
        return argumento_widget(elemento, criterio["widget"], criterio.get("posicion", 0), criterio["valor"])
    if regla == "jerarquia_widgets":
        return jerarquia_widgets(elemento, criterio["ruta"], criterio.get("relacion", "descendiente"))
    if regla == "cantidad_widget":
        return cantidad_widget(elemento, criterio["widget"], criterio["cantidad"], criterio.get("dentro_de"), criterio.get("relacion", "descendiente"), criterio.get("comparador", "igual"))
    if regla == "secuencia_hijos":
        return secuencia_hijos(elemento, criterio["padre"], criterio["hijos"], criterio.get("propiedad", "children"))
    if regla == "ruta_propiedad":
        return ruta_propiedad(elemento, criterio["widget"], criterio["ruta"], criterio.get("tipo_final"), criterio.get("argumentos"), criterio.get("valor"))
    if regla == "cantidad_widget_filtrado":
        return cantidad_widget_filtrado(elemento, criterio.get("padre"), criterio["widget"], criterio["cantidad"], criterio["filtros"], criterio.get("relacion", "hijo_directo"))
    if regla == "valores_widgets":
        return valores_widgets(elemento, criterio["padre"], criterio["widget"], criterio["ruta"], criterio["valores"], criterio.get("relacion", "hijo_directo"))
    if regla == "dimensiones_uniformes":
        return dimensiones_uniformes(elemento, criterio["padre"], criterio["widget"], criterio["cantidad"], criterio.get("relacion", "hijo_directo"))
    if regla == "envoltorio_layout":
        return envoltorio_layout(elemento, criterio["widget"], criterio["hijo"], criterio["propiedades"])
    if regla == "propiedades_exactas_en_ambito":
        return propiedades_exactas_en_ambito(elemento, criterio["padre"], criterio["widget"], criterio["cantidad"], criterio["propiedades"], criterio.get("relacion", "descendiente"))
    if regla == "propiedades_requeridas_en_ambito":
        return propiedades_requeridas_en_ambito(elemento, criterio["padre"], criterio["widget"], criterio["cantidad"], criterio["propiedades"], criterio.get("relacion", "descendiente"))
    if regla == "hijos_expandidos_equivalentes":
        return hijos_expandidos_equivalentes(elemento, criterio["padre"], criterio["cantidad"], criterio["hijo"])
    if regla == "secuencia_hijos_configurados":
        return secuencia_hijos_configurados(
            elemento, criterio["padre"], criterio["hijos"])
    if regla == "secuencia_flex_configurada":
        return secuencia_flex_configurada(
            elemento, criterio["padre"], criterio["proporcion"],
            criterio["hijos"])
    if regla == "widget_configurado":
        return widget_configurado(elemento, criterio["configuracion"])
    if regla == "sin_stateful_widget":
        return all(
            "StatefulWidget" not in (clase.get("herencia") or "")
            for clase in analisis.get("clases", [])
        )
    if regla == "widget_personalizado_usado":
        clases = {
            clase["nombre"] for clase in analisis.get("clases", [])
            if clase.get("nombre")
            and (
                criterio.get("nombre") is None
                or clase["nombre"] == criterio["nombre"]
            )
            and "StatelessWidget" in (clase.get("herencia") or "")
            and clase.get("build") is not None
            and (
                criterio.get("raiz_build") is None
                or clase["build"].get("tipo") == criterio["raiz_build"]
            )
            and (
                criterio.get("contiene") is None
                or any(
                    nodo.get("tipo") == criterio["contiene"]
                    for nodo in iterar_widgets(clase["build"])
                )
            )
        }
        return any(
            nodo.get("tipo") in clases and "implementacion" in nodo
            for nodo in iterar_widgets(elemento)
        )
    raise ValueError(f"Regla no implementada: {regla}")


def evaluar(codigo, rubrica):
    codigo = re.sub(r"^\s*(import|export|part)\s+['\"][^'\"]+['\"][^;]*;[ \t]*$", "",
                    codigo, flags=re.M)
    codigo = "import 'package:flutter/material.dart';\n" + codigo
    analisis = analizar_flutter(codigo)
    analisis["codigo"] = codigo

    if not analisis["sintaxis_correcta"]:
        return {
            "puntuacion": 0,
            "maximo": sum(c["puntos"] for c in rubrica["criterios"]),
            "resultados": [],
            "error": "El código contiene errores de sintaxis."
        }

    resultados = []

    for criterio in rubrica["criterios"]:
        if criterio["regla"] == "alternativas_puntuadas":
            puntos = max((a["puntos"] for a in criterio["alternativas"]
                          if aplicar_regla(analisis["objetos"], a, analisis)), default=0)
            cumple = puntos > 0
        else:
            cumple = aplicar_regla(analisis["objetos"], criterio, analisis)
            puntos = criterio["puntos"] if cumple else 0

        resultados.append({
            "id": criterio["id"],
            "descripcion": criterio["descripcion"],
            "cumple": cumple,
            "puntos": puntos,
            "maximo": criterio["puntos"]
        })

    return {
        "puntuacion": sum(r["puntos"] for r in resultados),
        "maximo": sum(r["maximo"] for r in resultados),
        "resultados": resultados
    }


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python3 evaluador_generico.py rubrica.json", file=sys.stderr)
        sys.exit(1)

    codigo = sys.stdin.read()

    with open(sys.argv[1], encoding="utf-8") as archivo:
        rubrica = json.load(archivo)

    print(json.dumps(
        evaluar(codigo, rubrica),
        ensure_ascii=False,
        indent=2
    ))
