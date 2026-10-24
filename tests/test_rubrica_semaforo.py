import json
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from evaluador_generico import evaluar

class PruebaSemaforo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rubrica = json.loads((RAIZ / "rubricas" / "rubrica_semaforo_generica.json").read_text(encoding="utf-8"))

    def criterio(self, identificador):
        original = next(c for c in self.rubrica["criterios"] if c["id"] == identificador)
        return {"nombre": "prueba parcial", "criterios": [original]}

    def test_solucion_de_referencia_obtiene_diez(self):
        codigo = (RAIZ / "ejemplos" / "semaforo.dart").read_text(encoding="utf-8")
        resultado = evaluar(codigo, self.rubrica)
        self.assertEqual(resultado["puntuacion"], 10)
        self.assertEqual(resultado["maximo"], 10)

    def test_widget_padding_recibe_medio_punto(self):
        codigo = """Widget build(BuildContext context) => Container(
          child: Padding(padding: EdgeInsets.all(16), child: Column(children: [])),
        );"""
        resultado = evaluar(codigo, self.criterio("padding"))
        self.assertEqual(resultado["puntuacion"], 0.5)
        resultado_columna = evaluar(codigo, self.criterio("columna"))
        self.assertEqual(resultado_columna["puntuacion"], 1)

    def test_los_colores_no_afectan_a_las_luces_circulares(self):
        codigo = """Widget build(BuildContext context) => Column(children: [
          Container(decoration: BoxDecoration(color: Colors.purple, shape: BoxShape.circle)),
          Container(decoration: BoxDecoration(color: Colors.white, shape: BoxShape.circle)),
          Container(decoration: BoxDecoration(color: Colors.orange, shape: BoxShape.circle)),
        ]);"""
        resultado = evaluar(codigo, self.criterio("circulos"))
        self.assertEqual(resultado["puntuacion"], 1)

    def test_card_no_puntua_como_carcasa_container(self):
        codigo = """Widget build(BuildContext context) => Card(
          child: Column(children: []),
        );"""
        resultado = evaluar(codigo, self.criterio("carcasa_container"))
        self.assertEqual(resultado["puntuacion"], 0)

    def test_semaforo_inline_no_puntua_en_organizacion(self):
        codigo = """void main() => runApp(MiApp());
        class MiApp extends StatelessWidget {
          Widget build(BuildContext context) => MaterialApp(home: Scaffold(
            body: Center(child: Container(child: Column(children: []))),
          ));
        }"""
        resultado = evaluar(codigo, self.criterio("widget_propio"))
        self.assertEqual(resultado["puntuacion"], 0)

    def test_stateful_widget_pierde_el_criterio(self):
        codigo = """class Semaforo extends StatefulWidget {
          State<Semaforo> createState() => _SemaforoState();
        }
        class _SemaforoState extends State<Semaforo> {
          Widget build(BuildContext context) => Container();
        }"""
        resultado = evaluar(codigo, self.criterio("sin_estado"))
        self.assertEqual(resultado["puntuacion"], 0)

    def test_stack_conserva_carcasa_y_circulos_pero_no_widget_propio(self):
        codigo = """void main() => runApp(MaterialApp(home: Scaffold(body:
          Center(child: Container(decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(20)), child: Stack(children: [
              Container(decoration: BoxDecoration(shape: BoxShape.circle)),
              Container(decoration: BoxDecoration(shape: BoxShape.circle)),
              Container(decoration: BoxDecoration(shape: BoxShape.circle)),
            ]))),
        )));"""
        for identificador, puntos in (
            ("carcasa_container", 1),
            ("circulos", 1),
            ("widget_propio", 0),
            ("columna", 0),
        ):
            with self.subTest(criterio=identificador):
                resultado = evaluar(codigo, self.criterio(identificador))
                self.assertEqual(resultado["puntuacion"], puntos)

if __name__ == "__main__":
    unittest.main()
