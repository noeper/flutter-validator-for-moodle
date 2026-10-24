import 'package:flutter/material.dart';

void main() => runApp(
  const MaterialApp(
    debugShowCheckedModeBanner: false,
    home: Scaffold(
      backgroundColor: Colors.black87,
      body: Center(child: CartaAjuste()),
    ),
  ),
);

class CartaAjuste extends StatelessWidget {
  const CartaAjuste({super.key});

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 320,
      height: 220,
      child: Stack(
        children: [
          Column(
            children: [
              Expanded(
                flex: 3,
                child: Row(
                  children: [
                    Expanded(child: Container(color: Colors.white)),
                    Expanded(child: Container(color: Colors.yellow)),
                    Expanded(child: Container(color: Colors.cyan)),
                    Expanded(child: Container(color: Colors.green)),
                    Expanded(child: Container(color: Colors.purpleAccent)),
                    Expanded(child: Container(color: Colors.red)),
                    Expanded(child: Container(color: Colors.blue)),
                  ],
                ),
              ),
              Expanded(
                flex: 1,
                child: Container(
                  color: Colors.black,
                  child: const Center(
                    child: Text(
                      'SIN SEÑAL',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ),
              ),
            ],
          ),
          const Positioned(
            top: 8,
            right: 8,
            child: Text(
              '2DAM TV',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
          ),
        ],
      ),
    );
  }
}
