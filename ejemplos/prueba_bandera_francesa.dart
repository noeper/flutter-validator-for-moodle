import 'package:flutter/material.dart';

void main() => runApp(
  MaterialApp(
    debugShowCheckedModeBanner: false,
    home: Scaffold(
      appBar: AppBar(title: Text('Bandera francesa')),
      body: Center(child: Bandera()),
    ),
  ),
);

class Bandera extends StatelessWidget {
  const Bandera({super.key});

  @override
  Widget build(BuildContext context) => SizedBox(
    width: 300,
    height: 200,
    child: Row(
      children: [
        Expanded(child: Container(color: Colors.blue)),
        Expanded(child: Container(color: Colors.white)),
        Expanded(child: Container(color: Colors.red)),
      ],
    ),
  );
}
