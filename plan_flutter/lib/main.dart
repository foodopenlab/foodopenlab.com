import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  SystemChrome.setSystemUIOverlayStyle(
    const SystemUiOverlayStyle(
      statusBarColor: Colors.transparent,
      statusBarIconBrightness: Brightness.dark,
    ),
  );
  runApp(const FoodOpenLabApp());
}

/// watcher.www 랜딩(에메랄드 primary)과 맞춘 팔레트.
abstract final class LandingColors {
  static const primary = Color(0xFF16A34A);
  static const primaryLight = Color(0xFFDCFCE7);
  static const foreground = Color(0xFF171717);
  static const muted = Color(0xFF737373);
  static const border = Color(0xFFE5E5E5);
  static const card = Color(0xFFFFFFFF);
  static const secondaryBg = Color(0xFFF5F5F5);
  static const amber = Color(0xFFF59E0B);
}

class FoodOpenLabApp extends StatelessWidget {
  const FoodOpenLabApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'HACCP Monitor AI',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: LandingColors.primary,
          primary: LandingColors.primary,
          surface: Colors.white,
          brightness: Brightness.light,
        ),
        scaffoldBackgroundColor: Colors.white,
        fontFamily: 'Roboto',
      ),
      home: const IntroPage(),
    );
  }
}

class IntroPage extends StatelessWidget {
  const IntroPage({super.key});

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      body: SafeArea(
        child: CustomScrollView(
          slivers: [
            SliverToBoxAdapter(child: _HeroSection()),
            SliverToBoxAdapter(child: _InsightsSection()),
            SliverToBoxAdapter(child: _LogosSection()),
            SliverToBoxAdapter(child: _FooterSection()),
          ],
        ),
      ),
    );
  }
}

class _HeroSection extends StatelessWidget {
  const _HeroSection();

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        Positioned(
          top: -80,
          left: 0,
          right: 0,
          child: Center(
            child: Container(
              width: 360,
              height: 280,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: LandingColors.primary.withValues(alpha: 0.1),
                boxShadow: [
                  BoxShadow(
                    color: LandingColors.primary.withValues(alpha: 0.08),
                    blurRadius: 80,
                    spreadRadius: 40,
                  ),
                ],
              ),
            ),
          ),
        ),
        Padding(
          padding: const EdgeInsets.fromLTRB(20, 24, 20, 32),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: const [
              _ApiBadge(),
              SizedBox(height: 20),
              _HeroTitle(),
              SizedBox(height: 16),
              _HeroSubtitle(),
              SizedBox(height: 24),
              _LandingChatCard(),
              SizedBox(height: 20),
              _FoodPoisoningStatsPanel(),
            ],
          ),
        ),
      ],
    );
  }
}

class _ApiBadge extends StatelessWidget {
  const _ApiBadge();

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: LandingColors.secondaryBg,
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: LandingColors.border),
      ),
      child: const Text(
        '식품안전나라 공공 API 연동',
        style: TextStyle(
          fontSize: 12,
          fontWeight: FontWeight.w600,
          color: LandingColors.muted,
        ),
      ),
    );
  }
}

class _HeroTitle extends StatelessWidget {
  const _HeroTitle();

  @override
  Widget build(BuildContext context) {
    const base = TextStyle(
      fontSize: 32,
      fontWeight: FontWeight.w700,
      height: 1.25,
      letterSpacing: -0.5,
      color: LandingColors.foreground,
    );
    const accent = TextStyle(
      fontSize: 32,
      fontWeight: FontWeight.w700,
      height: 1.25,
      letterSpacing: -0.5,
      color: LandingColors.primary,
    );

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: const [
        Text('위해식품 회수 정보를', style: base),
        Text.rich(
          TextSpan(
            children: [
              TextSpan(text: 'AI가 ', style: accent),
              TextSpan(text: '실시간 모니터링', style: accent),
              TextSpan(text: ' 합니다.', style: base),
            ],
          ),
        ),
      ],
    );
  }
}

class _HeroSubtitle extends StatelessWidget {
  const _HeroSubtitle();

  @override
  Widget build(BuildContext context) {
    return const Text(
      '원료명을 입력하면 HACCP 관리점까지 자동으로 분석해드립니다.',
      style: TextStyle(
        fontSize: 16,
        height: 1.6,
        color: LandingColors.muted,
      ),
    );
  }
}

class _LandingChatCard extends StatefulWidget {
  const _LandingChatCard();

  @override
  State<_LandingChatCard> createState() => _LandingChatCardState();
}

class _LandingChatCardState extends State<_LandingChatCard> {
  final _controller = TextEditingController();
  final _messages = <_ChatMessage>[
    const _ChatMessage(
      role: _ChatRole.assistant,
      text:
          '안녕하세요. 원료명을 입력하시면 회수·HACCP 관련 정보를 안내해 드립니다.\n(앱 인트로 — 네이티브 UI, API 연동은 추후)',
    ),
  ];
  bool _sending = false;

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  Future<void> _send() async {
    final text = _controller.text.trim();
    if (text.isEmpty || _sending) return;

    setState(() {
      _messages.add(_ChatMessage(role: _ChatRole.user, text: text));
      _controller.clear();
      _sending = true;
    });

    await Future<void>.delayed(const Duration(milliseconds: 400));

    if (!mounted) return;
    setState(() {
      _messages.add(
        _ChatMessage(
          role: _ChatRole.assistant,
          text:
              '「$text」에 대한 분석은 대시보드·채팅 화면에서 제공될 예정입니다. 지금은 인트로 미리보기입니다.',
        ),
      );
      _sending = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return DecoratedBox(
      decoration: BoxDecoration(
        color: LandingColors.card,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: LandingColors.border),
        boxShadow: [
          BoxShadow(
            color: LandingColors.primary.withValues(alpha: 0.06),
            blurRadius: 24,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 14, 16, 12),
            child: Row(
              children: [
                Container(
                  width: 8,
                  height: 8,
                  decoration: const BoxDecoration(
                    color: LandingColors.primary,
                    shape: BoxShape.circle,
                  ),
                ),
                const SizedBox(width: 8),
                const Text(
                  'Food Safety AI',
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                    color: LandingColors.foreground,
                  ),
                ),
              ],
            ),
          ),
          const Divider(height: 1, color: LandingColors.border),
          ConstrainedBox(
            constraints: const BoxConstraints(maxHeight: 200),
            child: ListView.separated(
              padding: const EdgeInsets.all(16),
              shrinkWrap: true,
              itemCount: _messages.length,
              separatorBuilder: (_, _) => const SizedBox(height: 12),
              itemBuilder: (context, index) {
                final msg = _messages[index];
                final isUser = msg.role == _ChatRole.user;
                return Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisAlignment:
                      isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
                  children: [
                    if (!isUser) ...[
                      _ChatAvatar(icon: Icons.smart_toy_outlined),
                      const SizedBox(width: 10),
                    ],
                    Flexible(
                      child: Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 12,
                          vertical: 10,
                        ),
                        decoration: BoxDecoration(
                          color: isUser
                              ? LandingColors.primary
                              : LandingColors.secondaryBg,
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Text(
                          msg.text,
                          style: TextStyle(
                            fontSize: 13,
                            height: 1.45,
                            color: isUser
                                ? Colors.white
                                : LandingColors.foreground,
                          ),
                        ),
                      ),
                    ),
                    if (isUser) ...[
                      const SizedBox(width: 10),
                      _ChatAvatar(icon: Icons.person_outline),
                    ],
                  ],
                );
              },
            ),
          ),
          if (_sending)
            const Padding(
              padding: EdgeInsets.only(left: 16, bottom: 8),
              child: Align(
                alignment: Alignment.centerLeft,
                child: SizedBox(
                  width: 18,
                  height: 18,
                  child: CircularProgressIndicator(strokeWidth: 2),
                ),
              ),
            ),
          Padding(
            padding: const EdgeInsets.fromLTRB(12, 0, 12, 12),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _controller,
                    textInputAction: TextInputAction.send,
                    onSubmitted: (_) => _send(),
                    decoration: InputDecoration(
                      hintText: '원료명 입력...',
                      hintStyle: const TextStyle(color: LandingColors.muted),
                      filled: true,
                      fillColor: LandingColors.secondaryBg,
                      contentPadding: const EdgeInsets.symmetric(
                        horizontal: 14,
                        vertical: 12,
                      ),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: const BorderSide(color: LandingColors.border),
                      ),
                      enabledBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: const BorderSide(color: LandingColors.border),
                      ),
                      focusedBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: const BorderSide(
                          color: LandingColors.primary,
                          width: 1.5,
                        ),
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                Material(
                  color: LandingColors.primary,
                  borderRadius: BorderRadius.circular(12),
                  child: InkWell(
                    onTap: _sending ? null : _send,
                    borderRadius: BorderRadius.circular(12),
                    child: const SizedBox(
                      width: 48,
                      height: 48,
                      child: Icon(Icons.send_rounded, color: Colors.white, size: 22),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _ChatAvatar extends StatelessWidget {
  const _ChatAvatar({required this.icon});

  final IconData icon;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 32,
      height: 32,
      decoration: BoxDecoration(
        color: LandingColors.primaryLight,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Icon(icon, size: 18, color: LandingColors.primary),
    );
  }
}

enum _ChatRole { user, assistant }

class _ChatMessage {
  const _ChatMessage({required this.role, required this.text});

  final _ChatRole role;
  final String text;
}

class _FoodPoisoningStatsPanel extends StatelessWidget {
  const _FoodPoisoningStatsPanel();

  static const _rows = [
    (year: '2023', incidents: 1240, patients: 18500),
    (year: '2022', incidents: 1180, patients: 17200),
    (year: '2021', incidents: 1050, patients: 15800),
    (year: '2020', incidents: 980, patients: 14100),
  ];

  @override
  Widget build(BuildContext context) {
    final maxIncidents = _rows.map((r) => r.incidents).reduce((a, b) => a > b ? a : b);
    final latest = _rows.first;

    return DecoratedBox(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: LandingColors.primary.withValues(alpha: 0.15)),
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            LandingColors.card,
            LandingColors.card.withValues(alpha: 0.9),
            LandingColors.primaryLight.withValues(alpha: 0.35),
          ],
        ),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  width: 40,
                  height: 40,
                  decoration: BoxDecoration(
                    color: LandingColors.primaryLight,
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: const Icon(Icons.bar_chart_rounded, color: LandingColors.primary),
                ),
                const SizedBox(width: 12),
                const Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '식중독 통계',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                          color: LandingColors.foreground,
                        ),
                      ),
                      Text(
                        '식의약 안전정보원 · 연도별 발생·환자 수',
                        style: TextStyle(fontSize: 13, color: LandingColors.muted),
                      ),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                  decoration: BoxDecoration(
                    color: LandingColors.primaryLight,
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(
                      color: LandingColors.primary.withValues(alpha: 0.2),
                    ),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      Text(
                        '최근(${latest.year})',
                        style: TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.w600,
                          color: LandingColors.primary,
                        ),
                      ),
                      Text(
                        '${_formatCount(latest.incidents)}건 · ${_formatCount(latest.patients)}명',
                        style: const TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.w600,
                          color: LandingColors.foreground,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            LayoutBuilder(
              builder: (context, constraints) {
                final wide = constraints.maxWidth > 400;
                return GridView.count(
                  crossAxisCount: wide ? 4 : 2,
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  mainAxisSpacing: 10,
                  crossAxisSpacing: 10,
                  childAspectRatio: wide ? 0.85 : 1.1,
                  children: [
                    for (final row in _rows)
                      _YearStatTile(
                        year: row.year,
                        incidents: row.incidents,
                        patients: row.patients,
                        barPct: row.incidents / maxIncidents,
                      ),
                  ],
                );
              },
            ),
          ],
        ),
      ),
    );
  }

  static String _formatCount(int n) {
    return n.toString().replaceAllMapped(
      RegExp(r'(\d)(?=(\d{3})+(?!\d))'),
      (m) => '${m[1]},',
    );
  }
}

class _YearStatTile extends StatelessWidget {
  const _YearStatTile({
    required this.year,
    required this.incidents,
    required this.patients,
    required this.barPct,
  });

  final String year;
  final int incidents;
  final int patients;
  final double barPct;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.7),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: LandingColors.border.withValues(alpha: 0.8)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                '$year년',
                style: const TextStyle(
                  fontWeight: FontWeight.w600,
                  color: LandingColors.foreground,
                ),
              ),
              Text(
                '${(barPct * 100).round()}%',
                style: const TextStyle(fontSize: 11, color: LandingColors.muted),
              ),
            ],
          ),
          const SizedBox(height: 8),
          ClipRRect(
            borderRadius: BorderRadius.circular(999),
            child: LinearProgressIndicator(
              value: barPct,
              minHeight: 6,
              backgroundColor: LandingColors.secondaryBg,
              color: LandingColors.primary.withValues(alpha: 0.85),
            ),
          ),
          const Spacer(),
          Row(
            children: [
              const Icon(Icons.show_chart, size: 14, color: LandingColors.amber),
              const SizedBox(width: 4),
              Text(
                '발생 $incidents건',
                style: const TextStyle(fontSize: 12, color: LandingColors.foreground),
              ),
            ],
          ),
          const SizedBox(height: 2),
          Row(
            children: [
              const Icon(Icons.people_outline, size: 14, color: LandingColors.muted),
              const SizedBox(width: 4),
              Text(
                '환자 $patients명',
                style: const TextStyle(fontSize: 12, color: LandingColors.muted),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _InsightsSection extends StatelessWidget {
  const _InsightsSection();

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 0, 20, 28),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: const [
          Text(
            '최신 식품안전 정보',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w700,
              color: LandingColors.foreground,
            ),
          ),
          SizedBox(height: 12),
          _InsightPanel(
            icon: Icons.warning_amber_rounded,
            title: '최근 회수·판매중지',
            subtitle: '식품안전나라 공개 데이터',
            items: [
              _InsightRow(
                headline: '대두 단백가수분해물',
                meta: '이물 혼입 · 2025-06-10',
                badge: '2등급',
              ),
              _InsightRow(
                headline: '냉동 만두',
                meta: '미생물 기준 부적합 · 2025-06-08',
                badge: '3등급',
              ),
            ],
          ),
          SizedBox(height: 12),
          _InsightPanel(
            icon: Icons.gavel_outlined,
            title: '최근 행정처분',
            subtitle: '식품안전나라',
            items: [
              _InsightRow(
                headline: '○○식품(주)',
                meta: '영업정지 15일 · 위생관리',
                badge: '처분',
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _InsightPanel extends StatelessWidget {
  const _InsightPanel({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.items,
  });

  final IconData icon;
  final String title;
  final String subtitle;
  final List<_InsightRow> items;

  @override
  Widget build(BuildContext context) {
    return DecoratedBox(
      decoration: BoxDecoration(
        color: LandingColors.card,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: LandingColors.border),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(icon, size: 20, color: LandingColors.primary),
                const SizedBox(width: 8),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        title,
                        style: const TextStyle(
                          fontWeight: FontWeight.w600,
                          color: LandingColors.foreground,
                        ),
                      ),
                      Text(
                        subtitle,
                        style: const TextStyle(fontSize: 12, color: LandingColors.muted),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            for (var i = 0; i < items.length; i++) ...[
              if (i > 0) const Divider(height: 20, color: LandingColors.border),
              items[i],
            ],
          ],
        ),
      ),
    );
  }
}

class _InsightRow extends StatelessWidget {
  const _InsightRow({
    required this.headline,
    required this.meta,
    required this.badge,
  });

  final String headline;
  final String meta;
  final String badge;

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                headline,
                style: const TextStyle(
                  fontWeight: FontWeight.w600,
                  fontSize: 14,
                  color: LandingColors.foreground,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                meta,
                style: const TextStyle(fontSize: 12, color: LandingColors.muted),
              ),
            ],
          ),
        ),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          decoration: BoxDecoration(
            color: LandingColors.primaryLight,
            borderRadius: BorderRadius.circular(6),
          ),
          child: Text(
            badge,
            style: const TextStyle(
              fontSize: 11,
              fontWeight: FontWeight.w600,
              color: LandingColors.primary,
            ),
          ),
        ),
      ],
    );
  }
}

class _LogosSection extends StatelessWidget {
  const _LogosSection();

  @override
  Widget build(BuildContext context) {
    return DecoratedBox(
      decoration: BoxDecoration(
        color: LandingColors.secondaryBg.withValues(alpha: 0.65),
        border: const Border(
          top: BorderSide(color: LandingColors.border),
          bottom: BorderSide(color: LandingColors.border),
        ),
      ),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 28),
        child: Column(
          children: [
            const Text(
              '신뢰할 수 있는 데이터 소스',
              style: TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.w500,
                color: LandingColors.muted,
              ),
            ),
            const SizedBox(height: 16),
            Wrap(
              alignment: WrapAlignment.center,
              spacing: 10,
              runSpacing: 10,
              children: const [
                _SourceChip(icon: Icons.storage_outlined, label: '식품안전나라 공공API'),
                _SourceChip(icon: Icons.verified_outlined, label: 'HACCP 기준점 DB'),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _SourceChip extends StatelessWidget {
  const _SourceChip({required this.icon, required this.label});

  final IconData icon;
  final String label;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      decoration: BoxDecoration(
        color: LandingColors.card,
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: LandingColors.border),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 16, color: LandingColors.primary),
          const SizedBox(width: 8),
          Text(
            label,
            style: const TextStyle(fontSize: 13, color: LandingColors.muted),
          ),
        ],
      ),
    );
  }
}

class _FooterSection extends StatelessWidget {
  const _FooterSection();

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 28, 20, 32),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                width: 36,
                height: 36,
                decoration: BoxDecoration(
                  color: LandingColors.primary,
                  borderRadius: BorderRadius.circular(10),
                ),
                child: const Icon(Icons.shield_outlined, color: Colors.white, size: 20),
              ),
              const SizedBox(width: 10),
              const Text(
                'HACCP Monitor AI',
                style: TextStyle(
                  fontSize: 17,
                  fontWeight: FontWeight.w600,
                  color: LandingColors.foreground,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Wrap(
            alignment: WrapAlignment.center,
            spacing: 16,
            runSpacing: 8,
            children: const [
              _FooterLink('서비스 소개'),
              _FooterLink('개인정보처리방침'),
              _FooterLink('이용약관'),
              _FooterLink('문의하기'),
            ],
          ),
          const SizedBox(height: 16),
          const Text(
            '© 2025 HACCP Monitor AI',
            style: TextStyle(fontSize: 13, color: LandingColors.muted),
          ),
        ],
      ),
    );
  }
}

class _FooterLink extends StatelessWidget {
  const _FooterLink(this.label);

  final String label;

  @override
  Widget build(BuildContext context) {
    return Text(
      label,
      style: const TextStyle(fontSize: 13, color: LandingColors.muted),
    );
  }
}
