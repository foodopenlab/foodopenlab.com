import 'package:flutter_test/flutter_test.dart';

import 'package:plan_flutter/main.dart';

void main() {
  testWidgets('인트로 히어로 타이틀이 표시된다', (WidgetTester tester) async {
    await tester.pumpWidget(const FoodOpenLabApp());

    expect(find.text('위해식품 회수 정보를'), findsOneWidget);
    expect(find.textContaining('실시간 모니터링'), findsOneWidget);
    expect(find.text('식품안전나라 공공 API 연동'), findsOneWidget);
    expect(find.text('Food Safety AI'), findsOneWidget);
  });
}
