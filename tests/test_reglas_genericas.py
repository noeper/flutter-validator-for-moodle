import unittest
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from evaluador_generico import evaluar


CODIGO = """
Widget build(BuildContext context) {
  return Card(
    color: Colors.blue.shade50,
    elevation: 8,
    shape: RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(20),
    ),
    child: Row(
      children: [
        Expanded(child: Text('A')),
        Expanded(child: Text('B')),
        Expanded(child: Text('C')),
      ],
    ),
  );
}
"""


def criterio(regla, **datos):
    return {
        "nombre": "prueba",
        "criterios": [{
            "id": regla,
            "descripcion": regla,
            "puntos": 1,
            "regla": regla,
            **datos,
        }]
    }


class PruebasReglasGenericas(unittest.TestCase):
    def cumple(self, regla, **datos):
        resultado = evaluar(CODIGO, criterio(regla, **datos))
        return resultado["resultados"][0]["cumple"]

    def test_propiedades_deben_estar_en_la_misma_instancia(self):
        self.assertTrue(self.cumple(
            "propiedades_widget", widget="Card",
            propiedades={"color": "Colors.blue.shade50", "elevation": "8"}
        ))
        self.assertFalse(self.cumple(
            "propiedades_widget", widget="Row",
            propiedades={"color": "Colors.blue.shade50", "elevation": "8"}
        ))

    def test_argumento_posicional(self):
        self.assertTrue(self.cumple(
            "argumento_widget", widget="BorderRadius.circular",
            posicion=0, valor="20"
        ))
        self.assertFalse(self.cumple(
            "argumento_widget", widget="BorderRadius.circular",
            posicion=0, valor="12"
        ))

    def test_jerarquia_directa(self):
        self.assertTrue(self.cumple(
            "jerarquia_widgets", ruta=["Card", "Row", "Expanded"],
            relacion="hijo_directo"
        ))
        self.assertFalse(self.cumple(
            "jerarquia_widgets", ruta=["Card", "Expanded"],
            relacion="hijo_directo"
        ))

    def test_cantidad_dentro_de_un_padre(self):
        self.assertTrue(self.cumple(
            "cantidad_widget", widget="Expanded", cantidad=3,
            dentro_de="Row", relacion="hijo_directo"
        ))
        self.assertFalse(self.cumple(
            "cantidad_widget", widget="Expanded", cantidad=2,
            dentro_de="Row", relacion="hijo_directo"
        ))

    def test_secuencia_exacta(self):
        self.assertTrue(self.cumple(
            "secuencia_hijos", padre="Row",
            hijos=["Expanded", "Expanded", "Expanded"]
        ))
        self.assertFalse(self.cumple(
            "secuencia_hijos", padre="Row", hijos=["Expanded", "Expanded"]
        ))

    def test_ruta_de_propiedad(self):
        self.assertTrue(self.cumple(
            "ruta_propiedad", widget="Card", ruta=["shape", "borderRadius"],
            tipo_final="BorderRadius.circular", argumentos=["20"]
        ))
        self.assertFalse(self.cumple(
            "ruta_propiedad", widget="Card", ruta=["shape", "borderRadius"],
            tipo_final="BorderRadius.circular", argumentos=["8"]
        ))


if __name__ == "__main__":
    unittest.main()
