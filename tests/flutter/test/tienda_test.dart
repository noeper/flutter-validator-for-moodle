import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import '../lib/paso1.dart' as p1;
import '../lib/paso2.dart' as p2;
import '../lib/paso3.dart' as p3;
import '../lib/paso4.dart' as p4;
import '../lib/paso5.dart' as p5;
import '../lib/paso6.dart' as p6;

void main() {
  testWidgets('Paso 1: tres tarjetas comparten el saldo visible del padre', (t) async {
    await t.pumpWidget(const MaterialApp(home: p1.Tienda()));
    expect(find.byType(p1.TarjetaProducto), findsNWidgets(3));
    expect(find.text('Saldo: 20 euros'), findsOneWidget);
  });
  testWidgets('Paso 2: los dos botones compran y no permiten saldo negativo', (t) async {
    await t.pumpWidget(const MaterialApp(home: p2.Tienda()));
    await t.tap(find.text('Comprar pegatina'));
    await t.pump();
    await t.tap(find.text('Comprar otra pegatina'));
    await t.pump();
    expect(find.text('Saldo: 16 euros'), findsOneWidget);
    for (var i = 0; i < 10; i++) {
      await t.tap(find.text('Comprar pegatina'));
      await t.pump();
    }
    expect(find.text('Saldo: 0 euros'), findsOneWidget);
  });
  testWidgets('Paso 3: funciones anónimas compran con su argumento al pulsar', (t) async {
    await t.pumpWidget(const MaterialApp(home: p3.Tienda()));
    expect(find.text('Saldo: 20 euros'), findsOneWidget);
    await t.ensureVisible(find.text('Comprar libreta'));
    await t.tap(find.text('Comprar libreta'));
    await t.pump();
    await t.ensureVisible(find.text('Comprar camiseta'));
    await t.tap(find.text('Comprar camiseta'));
    await t.pump();
    expect(find.text('Saldo: 3 euros'), findsOneWidget);
    await t.tap(find.text('Comprar libreta'));
    await t.pump();
    expect(find.text('Saldo: 3 euros'), findsOneWidget);
  });
  for (final entry in <String, Widget>{
    'Paso 4': const p4.Tienda(), 'Paso 5': const p5.Tienda(), 'Paso 6': const p6.Tienda(),
  }.entries) {
    testWidgets('${entry.key}: la tarjeta avisa, el padre descuenta y rechaza otra compra', (t) async {
      await t.pumpWidget(MaterialApp(home: entry.value));
      final button = find.widgetWithText(ElevatedButton, 'Comprar').at(2);
      await t.ensureVisible(button);
      await t.tap(button);
      await t.pump();
      expect(find.text('Saldo: 8 euros'), findsOneWidget);
      await t.tap(button);
      await t.pump();
      expect(find.text('Saldo: 8 euros'), findsOneWidget);
    });
  }
  testWidgets('Paso 6: se consume el bool devuelto para mostrar ambos mensajes', (t) async {
    await t.pumpWidget(const MaterialApp(home: p6.Tienda()));
    final button = find.widgetWithText(ElevatedButton, 'Comprar').at(2);
    await t.ensureVisible(button);
    await t.tap(button);
    await t.pumpAndSettle();
    expect(find.text('Compra realizada'), findsOneWidget);
    await t.pump(const Duration(seconds: 5));
    await t.pumpAndSettle();
    await t.tap(button);
    await t.pumpAndSettle();
    expect(find.text('Saldo insuficiente'), findsOneWidget);
  });
}
