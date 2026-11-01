"""Regresión de soluciones recuperadas de DAD y cambios incorrectos."""
import json
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
from adaptar_coderunner import adaptar
from evaluador_generico import evaluar

ACTIVIDADES = (
    "callbacks_01_boton", "callbacks_02_contador", "callbacks_03_personalizar",
    "callbacks_04_informacion", "callbacks_05_opcional", "clasico_dam_daw",
)


class PruebasRubricasUT2(unittest.TestCase):
    def cargar(self, nombre):
        rubrica = json.loads((RAIZ / "rubricas" / f"rubrica_{nombre}.json").read_text(encoding="utf-8"))
        codigo = (RAIZ / "ejemplos" / f"{nombre}.dart").read_text(encoding="utf-8")
        return codigo, rubrica

    def test_soluciones_de_moodle_obtienen_puntuacion_completa(self):
        for nombre in ACTIVIDADES:
            with self.subTest(actividad=nombre):
                codigo, rubrica = self.cargar(nombre)
                resultado = evaluar(codigo, rubrica)
                self.assertEqual(resultado["puntuacion"], resultado["maximo"])
                self.assertGreater(resultado["maximo"], 0)
                self.assertEqual(adaptar(codigo, rubrica)["fraction"], 1)

    def test_codigo_vacio_no_aprueba(self):
        for nombre in ACTIVIDADES:
            with self.subTest(actividad=nombre):
                _, rubrica = self.cargar(nombre)
                resultado = evaluar("", rubrica)
                self.assertLess(resultado["puntuacion"], resultado["maximo"])

    def test_snackbar_incorrecto_pierde_puntos(self):
        codigo, rubrica = self.cargar("callbacks_01_boton")
        incorrecto = codigo.replace("Inscripción realizada", "Otro mensaje")
        self.assertNotEqual(incorrecto, codigo)
        resultado = evaluar(incorrecto, rubrica)
        self.assertLess(resultado["puntuacion"], resultado["maximo"])
        self.assertGreater(resultado["puntuacion"], 0)

    def test_textos_en_comentarios_no_suplen_el_snackbar(self):
        codigo, rubrica = self.cargar("callbacks_01_boton")
        codigo = codigo.replace("Inscripción realizada", "Otro mensaje")
        codigo += "\n// SnackBar(content: Text('Inscripción realizada'))\n"
        resultado = evaluar(codigo, rubrica)
        mensaje = next(c for c in resultado["resultados"] if c["id"] == "mensaje")
        self.assertFalse(mensaje["cumple"])


if __name__ == "__main__":
    unittest.main()
