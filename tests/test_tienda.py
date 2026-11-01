"""Soluciones y fallos representativos de cada paso de la tienda."""
import json
from pathlib import Path
import sys
import unittest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
from adaptar_coderunner import adaptar
from evaluador_generico import evaluar

MANIFEST = json.loads((RAIZ / "actividades" / "tienda" / "manifest.json").read_text(encoding="utf-8"))


class PruebasTienda(unittest.TestCase):
    def cargar(self, item):
        slug = item["actividad"]
        code = (RAIZ / "ejemplos" / f"{slug}.dart").read_text(encoding="utf-8")
        base = (RAIZ / "iniciales" / f"{slug}.dart").read_text(encoding="utf-8")
        rubric = json.loads((RAIZ / "rubricas" / f"rubrica_{slug}.json").read_text(encoding="utf-8"))
        return code, base, rubric

    def test_seis_soluciones_obtienen_el_total(self):
        for item in MANIFEST:
            with self.subTest(paso=item["paso"]):
                code, _, rubric = self.cargar(item)
                result = evaluar(code, rubric)
                self.assertEqual(result["puntuacion"], result["maximo"])
                self.assertGreater(result["maximo"], 0)
                self.assertEqual(adaptar(code, rubric)["fraction"], 1)

    def test_iniciales_no_resuelven_el_paso(self):
        for item in MANIFEST:
            with self.subTest(paso=item["paso"]):
                _, base, rubric = self.cargar(item)
                result = evaluar(base, rubric)
                self.assertNotIn("error", result)
                self.assertLess(result["puntuacion"], result["maximo"])

    def test_entregas_vacias_y_soluciones_comentadas_no_aprueban(self):
        for item in MANIFEST:
            code, _, rubric = self.cargar(item)
            for invalid in ("", "/*\n" + code + "\n*/"):
                with self.subTest(paso=item["paso"], vacio=not invalid):
                    result = evaluar(invalid, rubric)
                    self.assertLess(result["puntuacion"], result["maximo"])

    def test_descontar_sin_setstate_pierde_puntos(self):
        for item in MANIFEST[1:]:
            with self.subTest(paso=item["paso"]):
                code, _, rubric = self.cargar(item)
                invalid = code.replace("setState(() {", "(() {")
                self.assertNotEqual(code, invalid)
                result = evaluar(invalid, rubric)
                self.assertLess(result["puntuacion"], result["maximo"])

    def test_hijo_con_estado_pierde_el_criterio(self):
        for item in MANIFEST[3:]:
            with self.subTest(paso=item["paso"]):
                code, _, rubric = self.cargar(item)
                invalid = code.replace("TarjetaProducto extends StatelessWidget", "TarjetaProducto extends StatefulWidget")
                result = evaluar(invalid, rubric)
                self.assertLess(result["puntuacion"], result["maximo"])

    def test_retorno_que_acepta_sin_saldo_pierde_puntos(self):
        code, _, rubric = self.cargar(MANIFEST[-1])
        result = evaluar(code.replace("return false;", "return true;"), rubric)
        self.assertLess(result["puntuacion"], result["maximo"])


if __name__ == "__main__":
    unittest.main()
