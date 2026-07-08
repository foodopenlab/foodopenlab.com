#!/usr/bin/env python3
"""
validate-harness.py — Star Topology Harness Validator
위치: com.auditor/scripts/validate-harness.py
실행: python scripts/validate-harness.py  (com.auditor/ 루트에서)

검증 항목:
  [1] Spoke → Spoke 직접 import 위반
  [2] _docs/ MD Frontmatter (type, domain, links) 누락
  [3] 고립 노드 탐지 (star_craft 미연결 spoke MD)
  [4] Hub(star_craft) 내 순환 참조
"""

import re
import sys
from pathlib import Path
from typing import NamedTuple

# Windows cp949 터미널에서 UTF-8 출력 강제
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ── 토폴로지 정의 ──────────────────────────────────────────────────────────────
HUB = "ontology"
SPOKES = {
    "titanic",
    "siliconvalley",
    "mfds_user",
    "mfds_admin",
    "imitation_game",
    "inception",
    "social_network",
    "braindead",
}
ALL_DOMAINS = SPOKES | {HUB}

# ── 경로 ──────────────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent
ROOT = SCRIPT_DIR.parent          # com.auditor/
APPS = ROOT / "apps"

# ── ANSI 컬러 (NO_COLOR 환경변수 또는 비-TTY면 비활성) ────────────────────────
import os
_USE_COLOR = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None

def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m" if _USE_COLOR else text

RED    = lambda t: _c("31", t)
GREEN  = lambda t: _c("32", t)
YELLOW = lambda t: _c("33", t)
BOLD   = lambda t: _c("1",  t)
DIM    = lambda t: _c("2",  t)


# ── 결과 집계 ─────────────────────────────────────────────────────────────────
class Report(NamedTuple):
    errors: list[str]
    warnings: list[str]


def _section(title: str) -> None:
    print(f"\n{BOLD('-' * 60)}")
    print(BOLD(f"  {title}"))
    print(BOLD('-' * 60))


# ══════════════════════════════════════════════════════════════════════════════
# [1] Spoke → Spoke 직접 import 위반
# ══════════════════════════════════════════════════════════════════════════════
# spoke 모듈 내에서 다른 spoke 이름을 import하는 패턴을 탐지한다.
# 예: siliconvalley/ 안에서 `from titanic.xxx import yyy` → 위반

_IMPORT_RE = re.compile(
    r"^\s*(?:from|import)\s+({domains})\b".format(
        domains="|".join(re.escape(s) for s in SPOKES)
    ),
    re.MULTILINE,
)


def check_spoke_imports() -> Report:
    errors: list[str] = []

    for spoke in SPOKES:
        spoke_dir = APPS / spoke
        if not spoke_dir.exists():
            continue

        for py_file in spoke_dir.rglob("*.py"):
            if "__pycache__" in py_file.parts:
                continue

            source = py_file.read_text(encoding="utf-8", errors="replace")
            for match in _IMPORT_RE.finditer(source):
                imported = match.group(1)
                if imported == spoke:
                    continue  # 자기 자신 참조는 허용

                line_no = source[: match.start()].count("\n") + 1
                rel = py_file.relative_to(ROOT)
                errors.append(
                    f"  {RED('VIOLATION')}  {rel}:{line_no}\n"
                    f"            spoke `{spoke}` → spoke `{imported}` 직접 참조"
                )

    return Report(errors, [])


# ══════════════════════════════════════════════════════════════════════════════
# [2] MD Frontmatter 검증
# ══════════════════════════════════════════════════════════════════════════════
# _docs/*.md 파일의 YAML frontmatter에서 type/domain/links 필드를 검사한다.
# 현재 MD에 frontmatter가 없는 경우 WARNING으로만 처리한다(점진적 도입).

_FM_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)
_FIELD_RE = re.compile(r"^(\w+)\s*:\s*(.+)$", re.MULTILINE)
_LIST_ITEM_RE = re.compile(r"^\s+-\s+(\S+)", re.MULTILINE)


def _parse_frontmatter(text: str) -> dict | None:
    m = _FM_RE.match(text)
    if not m:
        return None
    body = m.group(1)
    fields: dict = {}
    for fm in _FIELD_RE.finditer(body):
        key, val = fm.group(1).strip(), fm.group(2).strip()
        fields[key] = val
    # links 는 리스트
    links_match = re.search(r"^links\s*:\s*\n((?:\s+-\s+\S+\n?)+)", body, re.MULTILINE)
    if links_match:
        fields["links"] = _LIST_ITEM_RE.findall(links_match.group(1))
    return fields


def _collect_docs() -> list[Path]:
    docs: list[Path] = []
    # com.auditor/_docs/
    backend_docs = ROOT / "_docs"
    if backend_docs.exists():
        docs.extend(backend_docs.rglob("*.md"))
    # apps/{domain}/_docs/
    for domain in ALL_DOMAINS:
        app_docs = APPS / domain / "_docs"
        if app_docs.exists():
            docs.extend(app_docs.rglob("*.md"))
    return docs


def check_md_frontmatter() -> Report:
    errors: list[str] = []
    warnings: list[str] = []

    for md_file in _collect_docs():
        rel = md_file.relative_to(ROOT)
        text = md_file.read_text(encoding="utf-8", errors="replace")
        fm = _parse_frontmatter(text)

        if fm is None:
            warnings.append(
                f"  {YELLOW('NO-FM')}    {rel}\n"
                f"            frontmatter 없음 — type/domain/links 추가 권장"
            )
            continue

        node_type = fm.get("type", "").strip()
        domain    = fm.get("domain", "").strip()
        links     = fm.get("links", [])

        # 필수 필드 검사
        missing = [f for f in ("type", "domain", "links") if f not in fm]
        if missing:
            errors.append(
                f"  {RED('MISSING')}   {rel}\n"
                f"            필수 필드 누락: {', '.join(missing)}"
            )
            continue

        if node_type not in ("hub", "spoke"):
            errors.append(
                f"  {RED('INVALID')}   {rel}\n"
                f"            type=`{node_type}` — hub 또는 spoke 만 허용"
            )

        # hub 는 star_craft 전용
        if node_type == "hub" and domain != HUB:
            errors.append(
                f"  {RED('INVALID')}   {rel}\n"
                f"            type=hub 이지만 domain=`{domain}` (star_craft 만 허용)"
            )

        # spoke 는 links 에 star_craft 포함 필수
        if node_type == "spoke":
            if HUB not in links:
                errors.append(
                    f"  {RED('ISOLATED')}  {rel}\n"
                    f"            spoke links 에 `{HUB}` 미포함"
                )
            # spoke → spoke 링크 금지
            illegal_links = [lk for lk in links if lk in SPOKES and lk != domain]
            for lk in illegal_links:
                errors.append(
                    f"  {RED('VIOLATION')}  {rel}\n"
                    f"            spoke links 에 타 spoke `{lk}` 직접 기재 금지"
                )

    return Report(errors, warnings)


# ══════════════════════════════════════════════════════════════════════════════
# [3] 고립 노드 탐지
# ══════════════════════════════════════════════════════════════════════════════
# frontmatter 가 있는 MD 중 hub 와 연결되지 않은 노드를 추가 경고한다.
# (check_md_frontmatter 에서 이미 개별 처리 — 여기서는 요약 통계용)

def check_isolated_nodes() -> Report:
    warnings: list[str] = []

    for md_file in _collect_docs():
        rel = md_file.relative_to(ROOT)
        text = md_file.read_text(encoding="utf-8", errors="replace")
        fm = _parse_frontmatter(text)

        if fm is None:
            continue
        if fm.get("type") != "spoke":
            continue

        links = fm.get("links", [])
        if HUB not in links:
            warnings.append(
                f"  {YELLOW('ISOLATED')}  {rel}\n"
                f"            hub `{HUB}` 와 미연결 spoke 노드"
            )

    return Report([], warnings)


# ══════════════════════════════════════════════════════════════════════════════
# [4] Hub(star_craft) 내 순환 참조 탐지
# ══════════════════════════════════════════════════════════════════════════════
# star_craft/ 내 Python 파일들의 import 그래프를 구성하고 DFS 로 cycle 탐지.

_HUB_IMPORT_RE = re.compile(
    r"^\s*(?:from|import)\s+(ontology(?:\.\S+)?)",
    re.MULTILINE,
)


def _module_name(py_file: Path, base: Path) -> str:
    rel = py_file.with_suffix("").relative_to(base)
    return "ontology." + ".".join(rel.parts)


def _build_hub_graph() -> dict[str, set[str]]:
    hub_dir = APPS / HUB
    graph: dict[str, set[str]] = {}

    if not hub_dir.exists():
        return graph

    py_files = [f for f in hub_dir.rglob("*.py") if "__pycache__" not in f.parts]
    for py_file in py_files:
        mod = _module_name(py_file, APPS)
        graph.setdefault(mod, set())
        source = py_file.read_text(encoding="utf-8", errors="replace")
        for match in _HUB_IMPORT_RE.finditer(source):
            imported = match.group(1).strip()
            if imported != mod:
                graph[mod].add(imported)

    return graph


def _find_cycle(graph: dict[str, set[str]]) -> list[str] | None:
    visited: set[str] = set()
    path: list[str] = []

    def dfs(node: str) -> list[str] | None:
        if node in path:
            cycle_start = path.index(node)
            return path[cycle_start:] + [node]
        if node in visited:
            return None
        visited.add(node)
        path.append(node)
        for neighbor in graph.get(node, set()):
            result = dfs(neighbor)
            if result:
                return result
        path.pop()
        return None

    for node in graph:
        if node not in visited:
            result = dfs(node)
            if result:
                return result
    return None


def check_hub_circular() -> Report:
    errors: list[str] = []
    warnings: list[str] = []

    hub_dir = APPS / HUB
    if not hub_dir.exists():
        warnings.append(f"  {YELLOW('SKIP')}      apps/{HUB}/ 미존재 — hub 미구현")
        return Report(errors, warnings)

    py_files = [f for f in hub_dir.rglob("*.py") if "__pycache__" not in f.parts]
    if not py_files:
        warnings.append(f"  {YELLOW('SKIP')}      apps/{HUB}/ Python 파일 없음 — 검사 생략")
        return Report(errors, warnings)

    graph = _build_hub_graph()
    cycle = _find_cycle(graph)

    if cycle:
        chain = " → ".join(cycle)
        errors.append(
            f"  {RED('CYCLE')}     hub 내 순환 참조 발견\n"
            f"            {chain}"
        )

    return Report(errors, warnings)


# ══════════════════════════════════════════════════════════════════════════════
# 메인
# ══════════════════════════════════════════════════════════════════════════════

def main() -> int:
    print(BOLD("\n[*] Star Topology Harness Validator"))
    print(DIM(f"   root: {ROOT}"))
    print(DIM(f"   hub : {HUB}  |  spokes: {len(SPOKES)}개"))

    checks = [
        ("[1] Spoke → Spoke import 위반",  check_spoke_imports),
        ("[2] MD Frontmatter 검증",         check_md_frontmatter),
        ("[3] 고립 노드 탐지",               check_isolated_nodes),
        ("[4] Hub 순환 참조 탐지",           check_hub_circular),
    ]

    total_errors   = 0
    total_warnings = 0

    for title, fn in checks:
        _section(title)
        report = fn()

        if report.errors:
            for msg in report.errors:
                print(msg)
            total_errors += len(report.errors)
        if report.warnings:
            for msg in report.warnings:
                print(msg)
            total_warnings += len(report.warnings)

        if not report.errors and not report.warnings:
            print(f"  {GREEN('PASS')}      이상 없음")

    # ── 최종 요약 ────────────────────────────────────────────────────────────
    _section("Summary")
    if total_errors == 0 and total_warnings == 0:
        print(f"  {GREEN('ALL CLEAR')}  위반 없음, 경고 없음")
        return 0

    if total_errors > 0:
        print(f"  {RED('ERRORS')}    {total_errors}건  ← CI 블로킹 대상")
    if total_warnings > 0:
        print(f"  {YELLOW('WARNINGS')}  {total_warnings}건  ← 점진적 개선 권장")
    print()

    return 1 if total_errors > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
