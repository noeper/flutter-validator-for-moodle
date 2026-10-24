import json
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from evaluador_generico import evaluar


class PruebasRubricaMascota(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rubrica = json.loads(
            (RAIZ / "rubricas" / "rubrica_mascota_virtual.json").read_text(
                encoding="utf-8")
        )
        cls.codigo = (RAIZ / "ejemplos" / "mascota_virtual.dart").read_text(
            encoding="utf-8")

    def criterio(self, identificador):
        original = next(c for c in self.rubrica["criterios"]
                        if c["id"] == identificador)
        return {"nombre": "prueba parcial", "criterios": [original]}

    def test_solucion_de_referencia_obtiene_diez(self):
        resultado = evaluar(self.codigo, self.rubrica)
        self.assertEqual(resultado["puntuacion"], 10)
        self.assertEqual(resultado["maximo"], 10)

    def test_los_nombres_de_variables_no_importan(self):
        codigo = self.codigo.replace("comida", "energia")
        codigo = codigo.replace("diversion", "animo")
        codigo = codigo.replace("dormida", "descansando")
        resultado = evaluar(codigo, self.rubrica)
        self.assertEqual(resultado["puntuacion"], 10)

    def test_modificar_fuera_de_setstate_no_puntua(self):
        codigo = self.codigo.replace(
            "setState(() {\n                  if (comida < 10) comida++;\n                });",
            "if (comida < 10) comida++;",
            1,
        )
        resultado = evaluar(codigo, self.criterio("comer_incrementa"))
        self.assertEqual(resultado["puntuacion"], 0)

    def test_un_solo_limite_recibe_medio_punto(self):
        codigo = self.codigo.replace(
            "if (diversion < 10) diversion++;", "diversion++;")
        codigo = codigo.replace("if (comida > 0) comida--;", "comida--;")
        resultado = evaluar(codigo, self.criterio("limites"))
        self.assertEqual(resultado["puntuacion"], 0.5)

    def test_cada_accion_debe_bloquearse_al_dormir(self):
        codigo = self.codigo.replace("if (dormida) return;", "", 1)
        comer = evaluar(codigo, self.criterio("comer_bloqueado"))
        jugar = evaluar(codigo, self.criterio("jugar_bloqueado"))
        self.assertEqual(comer["puntuacion"], 0)
        self.assertEqual(jugar["puntuacion"], 0.5)


if __name__ == "__main__":
    unittest.main()
