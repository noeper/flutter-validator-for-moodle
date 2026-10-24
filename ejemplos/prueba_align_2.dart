import 'package:flutter/material.dart';

void main() {
  runApp(
    Align(
      alignment: Alignment.center,
      child: Container(
        width: 120,
        height: 80,
        color: Colors.red,
        child: const Text('Hola'),
      ),
    ),
  );
}
