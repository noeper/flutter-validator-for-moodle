import 'package:flutter/material.dart';

void main() {
  runApp(
    const MaterialApp(
      debugShowCheckedModeBanner: false,
      home: MascotaApp(),
    ),
  );
}

IconData caraMascota(int comida, int diversion, bool dormida) {
  if (dormida) return Icons.bedtime;
  if (comida <= 2 || diversion <= 2) return Icons.sentiment_very_dissatisfied;
  if (comida >= 8 && diversion >= 8) return Icons.sentiment_very_satisfied;
  return Icons.sentiment_neutral;
}

class MascotaApp extends StatelessWidget {
  const MascotaApp({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Mascota virtual'),
        backgroundColor: Colors.teal,
        foregroundColor: Colors.white,
      ),
      body: const Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            CabeceraJuego(),
            SizedBox(height: 16),
            PanelMascota(),
          ],
        ),
      ),
    );
  }
}

class CabeceraJuego extends StatelessWidget {
  const CabeceraJuego({super.key});

  @override
  Widget build(BuildContext context) {
    return const Text(
      'Cuida de Dashi: dale de comer, juega con él y déjale dormir',
      textAlign: TextAlign.center,
    );
  }
}

class PanelMascota extends StatefulWidget {
  const PanelMascota({super.key});

  @override
  State<PanelMascota> createState() => _PanelMascotaState();
}

class _PanelMascotaState extends State<PanelMascota> {
  int comida = 5;
  int diversion = 5;
  bool dormida = false;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Icon(caraMascota(comida, diversion, dormida), size: 120, color: Colors.teal),
        Text('Comida: $comida', style: const TextStyle(fontSize: 20)),
        Text('Diversión: $diversion', style: const TextStyle(fontSize: 20)),
        const SizedBox(height: 16),
        Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            ElevatedButton(
              onPressed: () {
                if (dormida) return;
                setState(() {
                  if (comida < 10) comida++;
                });
              },
              child: const Text('Comer'),
            ),
            const SizedBox(width: 12),
            ElevatedButton(
              onPressed: () {
                if (dormida) return;
                setState(() {
                  if (diversion < 10) diversion++;
                  if (comida > 0) comida--;
                });
              },
              child: const Text('Jugar'),
            ),
          ],
        ),
        const SizedBox(height: 16),
        Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text('Dormir'),
            Switch(
              value: dormida,
              onChanged: (bool nuevoValor) {
                setState(() {
                  dormida = nuevoValor;
                });
              },
            ),
          ],
        ),
      ],
    );
  }
}
