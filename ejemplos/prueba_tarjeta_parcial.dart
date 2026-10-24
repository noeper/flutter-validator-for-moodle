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
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.person, size: 48),
            const Icon(Icons.star),
            const Icon(Icons.favorite),
          ],
        ),
      ),
    );
  }
}
