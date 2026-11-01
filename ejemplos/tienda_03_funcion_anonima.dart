import 'package:flutter/material.dart';

void main() {
  runApp(const MaterialApp(home: Tienda()));
}

class Tienda extends StatefulWidget {
  const Tienda({super.key});
  @override
  State<Tienda> createState() => _TiendaState();
}

class _TiendaState extends State<Tienda> {
  int saldo = 20;

  void comprar(int precio) {
    if (saldo < precio) return;
    setState(() {
      saldo -= precio;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('La tienda de clase')),
      body: SingleChildScrollView(
        child: Column(
          children: [
            Text('Saldo: $saldo euros'),
            TarjetaProducto(nombre: 'Pegatina', precio: 2),
            TarjetaProducto(nombre: 'Libreta', precio: 5),
            TarjetaProducto(nombre: 'Camiseta', precio: 12),
            ElevatedButton(onPressed: () { comprar(2); }, child: const Text('Comprar pegatina')),
            ElevatedButton(onPressed: () { comprar(5); }, child: const Text('Comprar libreta')),
            ElevatedButton(onPressed: () { comprar(12); }, child: const Text('Comprar camiseta')),
          ],
        ),
      ),
    );
  }
}

class TarjetaProducto extends StatelessWidget {
  final String nombre;
  final int precio;

  const TarjetaProducto({
    super.key,
    required this.nombre,
    required this.precio,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(nombre),
            Text('$precio euros'),
          ],
        ),
      ),
    );
  }
}
