import 'package:flutter/material.dart';

void main() {
  runApp(const MaterialApp(
    home: Scaffold(
      body: Center(child: Text('Prueba')),
    ),
  ));
}

class MiWidget extends StatefulWidget {
  const MiWidget({super.key});

  @override
  State<MiWidget> createState() => _MiWidgetState();
}

class _MiWidgetState extends State<MiWidget> {
  @override
  Widget build(BuildContext context) {
    return const Text('Hola');
  }
}
