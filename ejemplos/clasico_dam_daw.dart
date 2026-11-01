import 'package:flutter/material.dart';

void main() {
  runApp(
    const MaterialApp(
      debugShowCheckedModeBanner: false,
      home: PantallaPartido(),
    ),
  );
}

// --------------------------------------------------
// PANTALLA DEL PARTIDO: la única con estado
// --------------------------------------------------
class PantallaPartido extends StatefulWidget {
  const PantallaPartido({super.key});

  @override
  State<PantallaPartido> createState() => _PantallaPartidoState();
}

class _PantallaPartidoState extends State<PantallaPartido> {
  static const int puntosParaGanar = 21;

  int _puntos2dam = 0;
  int _puntos2daw = 0;
  String _ultimoEquipo = '';
  int _ultimosPuntos = 0;

  void _sumar2dam(int puntos) {
    setState(() {
      _puntos2dam += puntos;
      _ultimoEquipo = '2DAM';
      _ultimosPuntos = puntos;
    });
  }

  void _sumar2daw(int puntos) {
    setState(() {
      _puntos2daw += puntos;
      _ultimoEquipo = '2DAW';
      _ultimosPuntos = puntos;
    });
  }

  void _reiniciar() {
    setState(() {
      _puntos2dam = 0;
      _puntos2daw = 0;
      _ultimoEquipo = '';
      _ultimosPuntos = 0;
    });
  }

  void _deshacer() {
    setState(() {
      if (_ultimoEquipo == '2DAM') _puntos2dam -= _ultimosPuntos;
      if (_ultimoEquipo == '2DAW') _puntos2daw -= _ultimosPuntos;
      _ultimoEquipo = '';
      _ultimosPuntos = 0;
    });
  }

  @override
  Widget build(BuildContext context) {
    final bool hayGanador =
        _puntos2dam >= puntosParaGanar || _puntos2daw >= puntosParaGanar;
    final String mensaje = !hayGanador
        ? 'Gana el primero que llegue a $puntosParaGanar'
        : _puntos2dam > _puntos2daw
            ? '🏆 ¡Gana 2DAM!'
            : '🏆 ¡Gana 2DAW!';

    return Scaffold(
      appBar: AppBar(
        title: const Text('El clásico: 2DAM vs 2DAW'),
        backgroundColor: Colors.deepPurple,
        foregroundColor: Colors.white,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Text(
              mensaje,
              style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            Expanded(
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Expanded(
                    child: PanelEquipo(
                      nombre: '2DAM',
                      puntos: _puntos2dam,
                      color: Colors.blue,
                      activo: !hayGanador,
                      alSumar: _sumar2dam,
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: PanelEquipo(
                      nombre: '2DAW',
                      puntos: _puntos2daw,
                      color: Colors.red,
                      activo: !hayGanador,
                      alSumar: _sumar2daw,
                    ),
                  ),
                ],
              ),
            ),
            Wrap(
              alignment: WrapAlignment.center,
              spacing: 16,
              runSpacing: 8,
              children: [
                BotonAccion(
                  texto: 'Deshacer',
                  icono: Icons.undo,
                  alPulsar: _ultimoEquipo.isEmpty ? null : _deshacer,
                ),
                BotonAccion(
                  texto: 'Reiniciar',
                  icono: Icons.refresh,
                  color: Colors.grey,
                  alPulsar: _reiniciar,
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

// --------------------------------------------------
// COMPONENTES REUTILIZABLES (todos sin estado)
// --------------------------------------------------
class MarcadorEquipo extends StatelessWidget {
  final String nombre;
  final int puntos;
  final Color color;
  final IconData icono;

  const MarcadorEquipo({
    super.key,
    required this.nombre,
    required this.puntos,
    this.color = Colors.blue,
    this.icono = Icons.sports_basketball,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: double.infinity,
      child: Card(
        color: color,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            children: [
              Icon(icono, color: Colors.white, size: 36),
              Text(
                nombre,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
              Text('$puntos',
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 56,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class BotonPuntos extends StatelessWidget {
  final int puntos;
  final Color color;
  final bool activo;
  final ValueChanged<int> alSumar;

  const BotonPuntos({
    super.key,
    required this.puntos,
    required this.alSumar,
    this.color = Colors.orange,
    this.activo = true,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: SizedBox(
        width: double.infinity,
        child: ElevatedButton(
          style: ElevatedButton.styleFrom(
            backgroundColor: color,
            foregroundColor: Colors.white,
          ),
          onPressed: activo ? () => alSumar(puntos) : null,
          child: Text('+$puntos', style: const TextStyle(fontSize: 20)),
        ),
      ),
    );
  }
}

class PanelEquipo extends StatelessWidget {
  final String nombre;
  final int puntos;
  final Color color;
  final bool activo;
  final ValueChanged<int> alSumar;

  const PanelEquipo({
    super.key,
    required this.nombre,
    required this.puntos,
    required this.alSumar,
    this.color = Colors.blue,
    this.activo = true,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        MarcadorEquipo(nombre: nombre, puntos: puntos, color: color),
        const SizedBox(height: 12),
        BotonPuntos(puntos: 1, color: color, activo: activo, alSumar: alSumar),
        BotonPuntos(puntos: 2, color: color, activo: activo, alSumar: alSumar),
        BotonPuntos(puntos: 3, color: color, activo: activo, alSumar: alSumar),
      ],
    );
  }
}

class BotonAccion extends StatelessWidget {
  final String texto;
  final IconData icono;
  final Color color;
  final VoidCallback? alPulsar;

  const BotonAccion({
    super.key,
    required this.texto,
    required this.icono,
    this.color = Colors.deepPurple,
    this.alPulsar,
  });

  @override
  Widget build(BuildContext context) {
    return ElevatedButton.icon(
      style: ElevatedButton.styleFrom(
        backgroundColor: color,
        foregroundColor: Colors.white,
      ),
      onPressed: alPulsar,
      icon: Icon(icono),
      label: Text(texto),
    );
  }
}
