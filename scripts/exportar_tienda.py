"""Regenera las siete preguntas desde sus fuentes; no conecta con Moodle."""
import argparse
import base64
import html
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from preparar_moodle import COMUNES

RAIZ = Path(__file__).resolve().parents[1]
CONTENIDOS = RAIZ / "actividades" / "tienda"


def nodo(parent, tag, text=None, **attributes):
    child = ET.SubElement(parent, tag, attributes)
    if text is not None:
        child.text = str(text)
    return child


def campo_html(parent, tag, value):
    nodo(nodo(parent, tag, format="html"), "text", value)


def generar():
    manifest = json.loads((CONTENIDOS / "manifest.json").read_text(encoding="utf-8"))
    config = json.loads((RAIZ / "moodle" / "configuracion_tienda.json").read_text(encoding="utf-8"))
    quiz = ET.Element("quiz")
    intro = nodo(quiz, "question", type="description")
    nodo(nodo(intro, "name"), "text", "Tienda Flutter · 00 · Antes de empezar")
    campo_html(intro, "questiontext", (CONTENIDOS / "introduccion.html").read_text(encoding="utf-8"))
    nodo(intro, "defaultgrade", "0")
    nodo(intro, "penalty", "0")
    for item in manifest:
        slug = item["actividad"]
        initial = (RAIZ / "iniciales" / f"{slug}.dart").read_text(encoding="utf-8")
        solution = (RAIZ / "ejemplos" / f"{slug}.dart").read_text(encoding="utf-8")
        rubric = json.loads((RAIZ / "rubricas" / f"rubrica_{slug}.json").read_text(encoding="utf-8"))
        statement = (CONTENIDOS / f"{slug}-enunciado.html").read_text(encoding="utf-8")
        feedback = (CONTENIDOS / f"{slug}-feedback.html").read_text(encoding="utf-8")
        criteria = "<ul>" + "".join("<li>" + html.escape(c["descripcion"]) + "</li>" for c in rubric["criterios"]) + "</ul>"
        statement = statement.replace("{{CODIGO_INICIAL}}", html.escape(initial)).replace("{{CRITERIOS}}", criteria)
        feedback = feedback.replace("{{CODIGO_SOLUCION}}", html.escape(solution))
        question = nodo(quiz, "question", type="coderunner")
        nodo(nodo(question, "name"), "text", item["nombre"])
        nodo(question, "idnumber", item["idnumber"])
        campo_html(question, "questiontext", statement)
        campo_html(question, "generalfeedback", feedback)
        for field, value in config.items():
            nodo(question, field, value)
        nodo(question, "answer", solution)
        nodo(question, "answerpreload", initial)
        tests = nodo(question, "testcases")
        case = nodo(tests, "testcase", testtype="0", useasexample="0", hiderestiffail="0", mark="1.0000000")
        total = sum(c["puntos"] for c in rubric["criterios"])
        for field, value in (("testcode", ""), ("stdin", ""), ("expected", f"Puntuación: {total}/{total}"), ("extra", ""), ("display", "SHOW")):
            nodo(nodo(case, field), "text", value)
        for filename in (*COMUNES, "rubrica.json"):
            data = json.dumps(rubric, ensure_ascii=False).encode("utf-8") if filename == "rubrica.json" else (RAIZ / "src" / filename).read_bytes()
            nodo(tests, "file", base64.b64encode(data).decode("ascii"), name=filename, path="/", encoding="base64")
    return quiz


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", type=Path, default=RAIZ / "build" / "tienda-flutter.xml")
    args = parser.parse_args()
    args.salida.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(generar()).write(args.salida, encoding="utf-8", xml_declaration=True)
    print(args.salida)


if __name__ == "__main__":
    main()
