"""ScienceON API Gateway 연결 스모크 테스트.

Usage (com.auditor/):
  python tools/run_scienceon_smoke.py
  python tools/run_scienceon_smoke.py --keyword 식품안전

Docker:
  docker exec fastapi_backend pip install -q pycryptodome
  docker exec fastapi_backend python tools/run_scienceon_smoke.py
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_BACKEND = Path(__file__).resolve().parents[1]
for p in (_BACKEND / "core", _BACKEND / "apps"):
    if p.is_dir() and str(p) not in sys.path:
        sys.path.insert(0, str(p))


def main() -> None:
    parser = argparse.ArgumentParser(description="ScienceON API smoke test")
    parser.add_argument("--keyword", default="식품", help="검색 키워드")
    args = parser.parse_args()

    from mfds_user.adapter.outbound.external_api.scienceon_gateway_client import (
        get_access_token,
        search_domestic_articles,
    )

    print("1) Token...")
    token = get_access_token()
    print(f"   OK access_token={token[:12]}...")

    print(f"2) Search domestic articles (keyword={args.keyword!r})...")
    records = search_domestic_articles([args.keyword], row_count=5)
    print(f"   count={len(records)}")
    for i, rec in enumerate(records, 1):
        print(f"   [{i}] {rec.get('title', '')[:80]}")
        print(f"       cn={rec.get('cn')} source={rec.get('source')}")


if __name__ == "__main__":
    main()
