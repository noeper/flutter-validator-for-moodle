import json
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from evaluador_generico import evaluar


class PruebasRubricaCartaAjuste(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rubrica = json.loads(
            (RAIZ / "rubricas" / "rubrica_carta_ajuste.json").read_text(
                encoding="utf-8")
        )
        cls.codigo = (RAIZ / "ejemplos" / "carta_ajuste.dart").read_text(
            encoding="utf-8")

    def criterio(self, identificador):
        original = next(c for c in self.rubrica["criterios"]
                        if c["id"] == identificador)
        return {"nombre": "prueba parcial", "criterios": [original]}

    def test_solucion_de_referencia_obtiene_diez(self):
        resultado = evaluar(self.codigo, self.rubrica)
        self.assertEqual(resultado["puntuacion"], 10)
        self.assertEqual(resultado["maximo"], 10)

    def test_el_orden_de_los_colores_importa(self):
        codigo = self.codigo.replace("Colors.white", "Colors.orange", 1)
        resultado = evaluar(codigo, self.criterio("franjas"))
        self.assertEqual(resultado["puntuacion"], 0)

    def test_los_flex_deben_ser_tres_y_uno(self):
        codigo = self.codigo.replace("flex: 3", "flex: 2", 1)
        resultado = evaluar(codigo, self.criterio("proporcion_vertical"))
        self.assertEqual(resultado["puntuacion"], 0)

    def test_positioned_debe_contener_la_etiqueta_correcta(self):
        codigo = self.codigo.replace("'2DAM TV'", "'OTRO CANAL'", 1)
        resultado = evaluar(codigo, self.criterio("etiqueta"))
        self.assertEqual(resultado["puntuacion"], 0)

    def test_un_stateful_widget_invalida_el_criterio_estatico(self):
        codigo = self.codigo.replace(
            "class CartaAjuste extends StatelessWidget",
            "class CartaAjuste extends StatefulWidget",
        )
        resultado = evaluar(codigo, self.criterio("sin_estado"))
        self.assertEqual(resultado["puntuacion"], 0)

    def test_estructura_alternativa_cumple_los_criterios_equivalentes(self):
        codigo = (RAIZ / "ejemplos" / "carta_ajuste_alternativa.dart").read_text(
            encoding="utf-8")
        for identificador in ("centrada", "superposicion", "etiqueta",
                              "widget_propio"):
            with self.subTest(criterio=identificador):
                resultado = evaluar(codigo, self.criterio(identificador))
                self.assertEqual(resultado["puntuacion"], 1)


if __name__ == "__main__":
    unittest.main()
