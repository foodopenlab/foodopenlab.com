"""일일 브리핑 리포트 수동 생성(개발·운영 예외).

스케줄러(10:30) · POST /admin/reports/generate 와 달리
**당일 가입 전문가도 포함**해 즉시 1회 생성합니다. 정규 배치 규칙은 변경하지 않습니다.

Usage (repo root, .venv 활성화 권장):
  python com.auditor/tools/run_daily_report_generate.py
  python com.auditor/tools/run_daily_report_generate.py --email expert@example.com

Usage (com.auditor/):
  python tools/run_daily_report_generate.py

Docker (WORKDIR /app):
  docker exec fastapi_backend python tools/run_daily_report_generate.py
  docker exec fastapi_backend python tools/run_daily_report_generate.py --email user@example.com --force
"""
from __future__ import annotations

import argparse
import asyncio
import logging
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from pathlib import Path

_BACKEND = Path(__file__).resolve().parents[1]
for p in (_BACKEND / "core", _BACKEND / "apps"):
    if p.is_dir() and str(p) not in sys.path:
        sys.path.insert(0, str(p))


async def main() -> None:
    parser = argparse.ArgumentParser(description="일일 브리핑 리포트 수동 생성")
    parser.add_argument(
        "--email",
        help="지정 전문가 이메일만 생성 (미지정 시 업종 설정된 전문가 전원)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="오늘 리포트가 이미 있어도 삭제 후 재생성 (테스트·수동 갱신용)",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stdout,
    )

    from matrix.grid_keymaker_secret_manager import get_keymaker
    from matrix.grid_oracle_database_manager import (
        async_session_factory,
        dispose_engine,
        init_engine,
    )
    from mfds_user.adapter.outbound.pg.auth_pg_repository import AuthPgRepository
    from mfds_user.adapter.outbound.pg.industry_pg_repository import IndustryPgRepository
    from mfds_user.dependencies.daily_report import build_daily_report_use_case
    from mfds_user.adapter.outbound.pg.daily_report_pg_repository import DailyReportPgRepository
    from datetime import date

    get_keymaker().load_env()
    init_engine()
    if async_session_factory is None:
        raise SystemExit("DATABASE_URL 미설정 — com.auditor/.env 확인")

    target_email = (args.email or "").strip().lower()
    success, fail, skipped = 0, 0, 0

    print("Starting manual daily report generation (includes today signups)...")

    async with async_session_factory() as session:
        auth_repo = AuthPgRepository(session)
        industry_repo = IndustryPgRepository(session)
        report_uc = build_daily_report_use_case(session)
        report_repo = DailyReportPgRepository(session)

        users = await auth_repo.find_all_active()
        if target_email:
            users = [u for u in users if u.email.lower() == target_email]
            if not users:
                raise SystemExit(f"전문가를 찾을 수 없습니다: {args.email}")

        for user in users:
            industries = await industry_repo.find_by_user(user.id)
            if not industries:
                print(f"SKIP {user.email}: 업종 미설정")
                skipped += 1
                continue

            print(f"GENERATE {user.email} (selections={len(industries)}) ...")
            try:
                if args.force:
                    removed = await report_repo.delete_by_user_and_date(user.id, date.today())
                    if removed:
                        print(f"  FORCE: deleted existing report for {date.today()}")
                report = await report_uc.generate(user.id)
                print(
                    f"OK {user.email} id={report.id} date={report.report_date} "
                    f"preview={report.summary_preview[:100]!r}"
                )
                success += 1
            except Exception as exc:
                print(f"FAIL {user.email}: {exc}")
                fail += 1
                logging.exception("report generation failed")

    await dispose_engine()

    print(
        f"Done. success={success} fail={fail} skipped={skipped} "
        f"total_targets={success + fail + skipped}"
    )
    if fail:
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())
