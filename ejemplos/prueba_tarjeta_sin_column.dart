import 'package:flutter/material.dart';

void main() => runApp(
  MaterialApp(
    home: Scaffold(
      body: Center(
        child: TarjetaPerfil(),
      ),
    ),
  ),
);

class TarjetaPerfil extends StatelessWidget {
  const TarjetaPerfil({super.key});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.person, size: 48),
            const Text('Ana'),
            const Text('Desarrolladora'),
          ],
        ),
      ),
    );
  }
}
