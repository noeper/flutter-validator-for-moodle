import 'package:flutter/material.dart';

class TarjetaEvento extends StatelessWidget {
  final String titulo;
  final String fecha;
  final int plazasDisponibles;

  const TarjetaEvento({
    super.key,
    required this.titulo,
    required this.fecha,
    this.plazasDisponibles = 0,
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
              onPressed: () {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Inscripción realizada')),
                );
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

class PantallaEventos extends StatelessWidget {
  const PantallaEventos({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Próximos eventos')),
      body: const Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TarjetaEvento(
              titulo: 'Taller de Flutter',
              fecha: '24 de octubre',
              plazasDisponibles: 15,
            ),
            TarjetaEvento(
              titulo: 'Introducción a Git',
              fecha: '30 de octubre',
              plazasDisponibles: 8,
            ),
            TarjetaEvento(
              titulo: 'Charla de ciberseguridad',
              fecha: '5 de noviembre',
            ),
            TarjetaEvento(
              titulo: 'Diseño de interfaces',
              fecha: '12 de noviembre',
              plazasDisponibles: 20,
            ),
          ],
        ),
      ),
    );
  }
}
