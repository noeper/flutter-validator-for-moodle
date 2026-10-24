import json
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from adaptar_coderunner import adaptar
from evaluador_generico import evaluar


def cargar_json(nombre):
    with (RAIZ / "rubricas" / nombre).open(encoding="utf-8") as archivo:
        return json.load(archivo)


class PruebasPropiedadWidget(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rubrica = cargar_json("rubrica_propiedades.json")

    def test_propiedades_correctas(self):
        codigo = """
        Widget build(BuildContext context) {
          return Column(
            mainAxisSize: MainAxisSize.min,
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: [
              Stack(
                alignment: Alignment.center,
                children: [Text('centro')],
              ),
            ],
          );
        }
        """

        resultado = evaluar(codigo, self.rubrica)

        self.assertEqual(resultado["puntuacion"], 3)
        self.assertTrue(all(r["cumple"] for r in resultado["resultados"]))

    def test_valores_incorrectos(self):
        codigo = """
        Widget build(BuildContext context) {
          return Column(
            mainAxisSize: MainAxisSize.max,
            mainAxisAlignment: MainAxisAlignment.start,
            children: [
              Stack(
                alignment: Alignment.topLeft,
                children: [Text('arriba')],
              ),
            ],
          );
        }
        """

        resultado = evaluar(codigo, self.rubrica)

        self.assertEqual(resultado["puntuacion"], 0)
        self.assertFalse(any(r["cumple"] for r in resultado["resultados"]))

    def test_propiedades_en_widgets_equivocados(self):
        codigo = """
        Widget build(BuildContext context) {
          return Row(
            mainAxisSize: MainAxisSize.min,
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: [
              Align(
                alignment: Alignment.center,
                child: Text('centro'),
              ),
            ],
          );
        }
        """

        resultado = evaluar(codigo, self.rubrica)

        self.assertEqual(resultado["puntuacion"], 0)
        self.assertFalse(any(r["cumple"] for r in resultado["resultados"]))


class PruebasRegresionTarjeta(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rubrica = cargar_json("rubrica_tarjeta.json")

    def comprobar_puntuacion(self, archivo, esperada):
        codigo = (RAIZ / "ejemplos" / archivo).read_text(encoding="utf-8")
        resultado = evaluar(codigo, self.rubrica)
        self.assertEqual(resultado["puntuacion"], esperada)
        self.assertEqual(resultado["maximo"], 3)

    def test_tarjeta_completa_obtiene_tres(self):
        self.comprobar_puntuacion("prueba_tarjeta.dart", 3)

    def test_tarjeta_parcial_obtiene_dos(self):
        self.comprobar_puntuacion("prueba_tarjeta_parcial.dart", 2)

    def test_tarjeta_sin_columna_obtiene_cero(self):
        self.comprobar_puntuacion("prueba_tarjeta_sin_column.dart", 0)


class PruebasAdaptadorCodeRunner(unittest.TestCase):
    def test_salida_serializable_como_json(self):
        codigo = (RAIZ / "ejemplos" / "prueba_tarjeta.dart").read_text(encoding="utf-8")
        salida = adaptar(codigo, cargar_json("rubrica_tarjeta.json"))

        texto = json.dumps(salida, ensure_ascii=False)
        reconstruida = json.loads(texto)

        self.assertEqual(reconstruida["fraction"], 1.0)
        self.assertIn("prologuehtml", reconstruida)
        self.assertIn("testresults", reconstruida)

    def test_muestra_parcialmente_cumplido(self):
        codigo = """Widget build(BuildContext context) => Container(
          child: Padding(
            padding: EdgeInsets.all(16),
            child: Column(children: []),
          ),
        );"""
        rubrica = cargar_json("rubrica_semaforo_generica.json")
        salida = adaptar(codigo, rubrica)
        fila_padding = next(
            fila for fila in salida["testresults"]
            if fila[0] == "La carcasa tiene espacio interior"
        )

        self.assertEqual(fila_padding[1], "Parcialmente cumplido")
        self.assertEqual(fila_padding[2], "0.5/1")


if __name__ == "__main__":
    unittest.main()
