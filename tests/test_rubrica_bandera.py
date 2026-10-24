import json
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from evaluador_generico import evaluar


class PruebasRubricaBandera(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rubrica = json.loads(
            (RAIZ / "rubricas" / "rubrica_bandera_francesa.json").read_text(encoding="utf-8")
        )
        cls.codigo = (RAIZ / "ejemplos" / "prueba_bandera_francesa.dart").read_text(encoding="utf-8")

    def criterio(self, identificador):
        original = next(c for c in self.rubrica["criterios"] if c["id"] == identificador)
        return {"nombre": "prueba parcial", "criterios": [original]}

    def test_solucion_de_referencia_obtiene_diez(self):
        resultado = evaluar(self.codigo, self.rubrica)
        self.assertEqual(resultado["puntuacion"], 10)

    def test_container_dimensionador_recibe_medio_punto(self):
        codigo = self.codigo.replace(
            "Widget build(BuildContext context) => SizedBox(",
            "Widget build(BuildContext context) => Container(",
        )
        resultado = evaluar(codigo, self.rubrica)
        self.assertEqual(resultado["puntuacion"], 8.5)

    def test_propiedad_sobrante_recibe_medio_punto(self):
        codigo = self.codigo.replace(
            "Container(color: Colors.blue)",
            "Container(color: Colors.blue, width: 100)",
        )
        resultado = evaluar(codigo, self.criterio("propiedades_minimas"))
        self.assertEqual(resultado["puntuacion"], 0.5)

    def test_propiedad_requerida_ausente_no_puntua(self):
        codigo = self.codigo.replace(
            "Container(color: Colors.blue)",
            "Container()",
        )
        resultado = evaluar(codigo, self.criterio("propiedades_minimas"))
        self.assertEqual(resultado["puntuacion"], 0)

    def test_flex_distintos_no_forman_tres_tercios(self):
        codigo = self.codigo.replace(
            "Expanded(child: Container(color: Colors.blue))",
            "Expanded(flex: 2, child: Container(color: Colors.blue))",
        )
        resultado = evaluar(codigo, self.criterio("tercios"))
        self.assertEqual(resultado["puntuacion"], 0)

    def test_colores_no_se_evalúan(self):
        codigo = self.codigo.replace("Colors.blue", "Colors.orange")
        codigo = codigo.replace("Colors.white", "Colors.purple")
        codigo = codigo.replace("Colors.red", "Colors.black")
        resultado = evaluar(codigo, self.rubrica)
        self.assertEqual(resultado["puntuacion"], 10)


if __name__ == "__main__":
    unittest.main()
