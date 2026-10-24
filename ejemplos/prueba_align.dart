import 'package:flutter/material.dart';

void main() {
  runApp(
    Align(
      alignment: Alignment.center,
      child: Container(
        color: Colors.red,
        child: const Text('Hola'),
      ),
    ),
  );
}
