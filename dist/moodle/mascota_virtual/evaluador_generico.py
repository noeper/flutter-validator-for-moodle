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


def _cumple_configuracion(nodo, configuracion):
    if nodo.get("tipo") != configuracion["tipo"]:
        return False
    propiedades = nodo.get("propiedades", {})
    if not all(propiedades.get(nombre) == valor for nombre, valor in
               configuracion.get("propiedades", {}).items()):
        return False
    argumentos = configuracion.get("argumentos")
    if argumentos is not None and nodo.get("argumentos_posicionales") != argumentos:
        return False
    for requisito in configuracion.get("rutas", []):
        actual = valor_ruta(nodo, requisito["ruta"])
        if "valor" in requisito and actual != requisito["valor"]:
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


def aplicar_regla(elemento, criterio, analisis=None):
    regla = criterio["regla"]
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
    analisis = analizar_flutter(codigo)

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
