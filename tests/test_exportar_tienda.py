"""El XML regenerado conserva código, soporte y descripción inicial."""
import base64
import hashlib
import json
from pathlib import Path
import sys
import unittest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "scripts"))
from exportar_tienda import generar
from preparar_moodle import COMUNES


class PruebasExportarTienda(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.quiz = generar()
        cls.manifest = json.loads((RAIZ / "actividades" / "tienda" / "manifest.json").read_text(encoding="utf-8"))

    def test_descripcion_es_la_primera_y_hay_siete_preguntas(self):
        self.assertEqual(len(self.quiz), 7)
        self.assertEqual(self.quiz[0].attrib["type"], "description")
        self.assertEqual(self.quiz[0].findtext("defaultgrade"), "0")
        self.assertIn("main.dart", self.quiz[0].findtext("questiontext/text"))

    def test_respuestas_y_archivos_de_soporte_son_las_fuentes(self):
        for item, question in zip(self.manifest, self.quiz[1:], strict=True):
            slug = item["actividad"]
            with self.subTest(actividad=slug):
                self.assertEqual(question.findtext("answer"), (RAIZ / "ejemplos" / f"{slug}.dart").read_text(encoding="utf-8"))
                self.assertEqual(question.findtext("answerpreload"), (RAIZ / "iniciales" / f"{slug}.dart").read_text(encoding="utf-8"))
                files = {f.attrib["name"]: base64.b64decode(f.text) for f in question.findall("testcases/file")}
                self.assertEqual(set(files), set(COMUNES) | {"rubrica.json"})
                for name in COMUNES:
                    self.assertEqual(hashlib.sha256(files[name]).digest(), hashlib.sha256((RAIZ / "src" / name).read_bytes()).digest())
                self.assertEqual(json.loads(files["rubrica.json"]), json.loads((RAIZ / "rubricas" / f"rubrica_{slug}.json").read_text(encoding="utf-8")))

    def test_plantillas_resueltas_y_retorno_opcional(self):
        for question in self.quiz[1:]:
            for field in ("questiontext/text", "generalfeedback/text"):
                content = question.findtext(field)
                self.assertNotIn("{{CODIGO_", content)
                self.assertNotIn("{{CRITERIOS}}", content)
            self.assertIn("#4174c0", question.findtext("questiontext/text"))
            self.assertIn("#0c7c59", question.findtext("generalfeedback/text"))
        self.assertTrue(self.manifest[-1]["opcional"])
        self.assertEqual(self.manifest[-1]["peso_cuestionario"], 0)
        self.assertTrue(all(i["peso_cuestionario"] == 1 for i in self.manifest[:-1]))


if __name__ == "__main__":
    unittest.main()
