import 'package:flutter/material.dart';

class TarjetaEvento extends StatelessWidget {
  final String titulo;
  final String fecha;
  final int plazasDisponibles;
  final void Function(String)? onInscribirse;

  const TarjetaEvento({
    super.key,
    required this.titulo,
    required this.fecha,
    this.plazasDisponibles = 0,
    this.onInscribirse,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              titulo,
              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Text(fecha),
            Text('$plazasDisponibles plazas disponibles'),
            const SizedBox(height: 12),
            ElevatedButton(
              onPressed: onInscribirse == null
                  ? null
                  : () {
                      onInscribirse!(titulo);
                    },
              child: const Text('Inscribirse'),
            ),
          ],
        ),
      ),
    );
  }
}

import 'package:flutter/material.dart';
import '../widgets/tarjeta_evento.dart';

class PantallaEventos extends StatefulWidget {
  const PantallaEventos({super.key});

  @override
  State<PantallaEventos> createState() => _PantallaEventosState();
}

class _PantallaEventosState extends State<PantallaEventos> {
  int _inscripciones = 0;
  String _ultimoEvento = 'ninguna';
  int _plazasFlutter = 15;
  int _plazasGit = 8;
  int _plazasDiseno = 3;

  void _inscribirse(String nombreEvento) {
    setState(() {
      _inscripciones++;
      _ultimoEvento = nombreEvento;
    });
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('Te has inscrito en $nombreEvento')),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Próximos eventos'),
        actions: [
          Center(child: Text('🎟️ Mis inscripciones: $_inscripciones')),
          const SizedBox(width: 16),
        ],
      ),
      body: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text('Última inscripción: $_ultimoEvento'),
            const SizedBox(height: 12),
            TarjetaEvento(
              titulo: 'Taller de Flutter',
              fecha: '24 de octubre',
              plazasDisponibles: _plazasFlutter,
              onInscribirse: _plazasFlutter > 0
                  ? (nombreEvento) {
                      setState(() {
                        _plazasFlutter--;
                      });
                      _inscribirse(nombreEvento);
                    }
                  : null,
            ),
            TarjetaEvento(
              titulo: 'Introducción a Git',
              fecha: '30 de octubre',
              plazasDisponibles: _plazasGit,
              onInscribirse: _plazasGit > 0
                  ? (nombreEvento) {
                      setState(() {
                        _plazasGit--;
                      });
                      _inscribirse(nombreEvento);
                    }
                  : null,
            ),
            const TarjetaEvento(
              titulo: 'Charla de ciberseguridad',
              fecha: '5 de noviembre',
            ),
            TarjetaEvento(
              titulo: 'Diseño de interfaces',
              fecha: '12 de noviembre',
              plazasDisponibles: _plazasDiseno,
              onInscribirse: _plazasDiseno > 0
                  ? (nombreEvento) {
                      setState(() {
                        _plazasDiseno--;
                      });
                      _inscribirse(nombreEvento);
                    }
                  : null,
            ),
          ],
        ),
      ),
    );
  }
}
