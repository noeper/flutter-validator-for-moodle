import json
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from evaluador_generico import evaluar


class PruebasRubricaCartaColeccionable(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rubrica = json.loads(
            (RAIZ / "rubricas" / "rubrica_carta_coleccionable.json").read_text(
                encoding="utf-8")
        )
        cls.codigo = (RAIZ / "ejemplos" / "carta_coleccionable.dart").read_text(
            encoding="utf-8")

    def criterio(self, identificador):
        original = next(c for c in self.rubrica["criterios"]
                        if c["id"] == identificador)
        return {"nombre": "prueba parcial", "criterios": [original]}

    def test_solucion_de_referencia_obtiene_diez(self):
        resultado = evaluar(self.codigo, self.rubrica)
        self.assertEqual(resultado["puntuacion"], 10)
        self.assertEqual(resultado["maximo"], 10)

    def test_no_confunde_los_estilos_de_los_textos(self):
        codigo = self.codigo.replace("fontSize: 24", "fontSize: 18", 1)
        nombre = evaluar(codigo, self.criterio("nombre"))
        salud = evaluar(codigo, self.criterio("puntos_salud"))
        self.assertEqual(nombre["puntuacion"], 0)
        self.assertEqual(salud["puntuacion"], 1)

    def test_no_confunde_los_dos_iconos(self):
        codigo = self.codigo.replace(
            "Icons.bolt, size: 28", "Icons.bolt, size: 100", 1)
        rayo = evaluar(codigo, self.criterio("icono_rayo"))
        dash = evaluar(codigo, self.criterio("icono_dash"))
        self.assertEqual(rayo["puntuacion"], 0)
        self.assertEqual(dash["puntuacion"], 0.5)

    def test_el_borde_debe_estar_en_la_caja_de_la_ilustracion(self):
        codigo = self.codigo.replace(
            "border: Border.all(color: Colors.amber, width: 4),", "", 1)
        resultado = evaluar(codigo, self.criterio("caja_ilustracion_borde"))
        self.assertEqual(resultado["puntuacion"], 0)

    def test_el_estilo_debe_pertenecer_al_boton_atacar(self):
        codigo = self.codigo.replace(
            "backgroundColor: Colors.red", "backgroundColor: Colors.green", 1)
        resultado = evaluar(codigo, self.criterio("boton_colores"))
        self.assertEqual(resultado["puntuacion"], 0)


if __name__ == "__main__":
    unittest.main()
