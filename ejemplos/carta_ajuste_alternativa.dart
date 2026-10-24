import 'package:flutter/material.dart';

void main() {
  runApp(
    const MaterialApp(
      debugShowCheckedModeBanner: false,
      home: Scaffold(body: CartaAjuste()),
    ),
  );
}

class CartaAjuste extends StatelessWidget {
  const CartaAjuste({super.key});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Stack(
        children: [
          SizedBox(
            height: 220,
            width: 320,
            child: Column(
              children: [
                Expanded(
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
                Container(
                  height: 220 / 4,
                  width: 320,
                  color: Colors.black,
                  child: Center(
                    child: Text(
                      'SIN SEÑAL',
                      style: TextStyle(
                        fontSize: 20,
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
          Positioned(
            top: 8,
            right: 8,
            child: Text(
              '2DAM TV',
              style: TextStyle(
                color: Colors.black,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
