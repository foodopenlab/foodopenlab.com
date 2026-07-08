"""KISTI ScienceON API Gateway — 토큰 발급 + 국내 논문(ARTI) 검색."""
from __future__ import annotations

import base64
import html
import json
import logging
import os
import re
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)


def _load_aes():
    try:
        from Crypto.Cipher import AES  # type: ignore[import-untyped]

        return AES
    except ImportError as exc:
        raise ImportError(
            "ScienceON 연동에 pycryptodome 패키지가 필요합니다. "
            "pip install pycryptodome (또는 requirements.txt 설치)"
        ) from exc

TOKEN_URL = "https://apigateway.kisti.re.kr/tokenrequest.do"
API_URL = "https://apigateway.kisti.re.kr/openapicall.do"
DOMESTIC_CN_PREFIX = "JAKO"
_SCIENCEON_AES_IV = "jvHJ1EFA0IXBrxxz"
_FOOD_HINTS = ("육", "식품", "푸드", "고기", "소시지", "햄", "베이컨", "배양", "조리", "섭취")
_GENERIC_TERMS = frozenset({"기계", "용기", "포장"})


@dataclass
class _TokenCache:
    access_token: str = ""
    refresh_token: str = ""
    access_expires_at: datetime | None = None


_token_cache = _TokenCache()


def _cfg(name: str) -> str:
    return (os.getenv(name) or "").strip()


def _pkcs7_pad(text: str, block_size: int = 16) -> str:
    pad_len = block_size - (len(text) % block_size)
    return text + (chr(pad_len) * pad_len)


def _aes_encrypt_accounts(payload: dict[str, str], api_key: str) -> str:
    """KISTI ScienceON API Gateway 공식 샘플(kisti-mcp)과 동일한 CBC 암호화."""
    AES = _load_aes()
    raw = json.dumps(payload, separators=(",", ":"))
    cipher = AES.new(
        api_key.encode("utf-8"),
        AES.MODE_CBC,
        _SCIENCEON_AES_IV.encode("utf-8"),
    )
    encrypted = cipher.encrypt(_pkcs7_pad(raw).encode("utf-8"))
    encoded = base64.urlsafe_b64encode(encrypted).decode("utf-8")
    return urllib.parse.quote(encoded)


def _token_datetime() -> str:
    return "".join(re.findall(r"\d", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))


def _http_get(url: str, timeout: int = 20) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read()


def _parse_token_response(body: bytes) -> dict[str, Any]:
    text = body.decode("utf-8", errors="replace").strip()
    if text.startswith("{"):
        return json.loads(text)
    root = ET.fromstring(body)
    err = root.findtext(".//errorMessage") or root.findtext(".//message")
    if err:
        raise RuntimeError(err)
    raise RuntimeError("Unexpected token response format")


def _request_access_token() -> str:
    client_id = _cfg("SCIENCEON_CLIENT_ID")
    api_key = _cfg("SCIENCEON_API_KEY")
    mac = _cfg("SCIENCEON_MAC_ADDRESS")

    if not client_id or not api_key or not mac:
        raise RuntimeError(
            "SCIENCEON_CLIENT_ID, SCIENCEON_API_KEY, SCIENCEON_MAC_ADDRESS 가 필요합니다."
        )
    if len(api_key) != 32:
        raise RuntimeError("SCIENCEON_API_KEY 는 32자리여야 합니다.")

    accounts = _aes_encrypt_accounts(
        {"datetime": _token_datetime(), "mac_address": mac},
        api_key,
    )
    url = f"{TOKEN_URL}?client_id={urllib.parse.quote(client_id)}&accounts={accounts}"
    data = _parse_token_response(_http_get(url))
    if "access_token" not in data:
        raise RuntimeError(data.get("errorMessage") or data.get("message") or str(data))

    _token_cache.access_token = data["access_token"]
    _token_cache.refresh_token = data.get("refresh_token", "")
    _token_cache.access_expires_at = datetime.now() + timedelta(hours=1, minutes=50)
    return _token_cache.access_token


def _refresh_access_token() -> str:
    client_id = _cfg("SCIENCEON_CLIENT_ID")
    refresh = _token_cache.refresh_token
    if not client_id or not refresh:
        return _request_access_token()

    url = (
        f"{TOKEN_URL}?refresh_token={urllib.parse.quote(refresh)}"
        f"&client_id={urllib.parse.quote(client_id)}"
    )
    try:
        data = _parse_token_response(_http_get(url))
    except Exception:
        logger.warning("ScienceON refresh token failed — reissuing access token")
        return _request_access_token()

    if "access_token" not in data:
        return _request_access_token()

    _token_cache.access_token = data["access_token"]
    _token_cache.refresh_token = data.get("refresh_token", refresh)
    _token_cache.access_expires_at = datetime.now() + timedelta(hours=1, minutes=50)
    return _token_cache.access_token


def get_access_token() -> str:
    if (
        _token_cache.access_token
        and _token_cache.access_expires_at
        and datetime.now() < _token_cache.access_expires_at
    ):
        return _token_cache.access_token
    if _token_cache.refresh_token:
        return _refresh_access_token()
    return _request_access_token()


def _parse_year(value: str) -> date:
    digits = "".join(ch for ch in value if ch.isdigit())
    if len(digits) >= 4:
        try:
            return date(int(digits[:4]), 1, 1)
        except ValueError:
            pass
    return date.today()


def _parse_records(xml_bytes: bytes) -> list[dict[str, str]]:
    root = ET.fromstring(xml_bytes)
    status_code = root.findtext(".//statusCode")
    if status_code and status_code != "200":
        err_code = (root.findtext(".//errorCode") or "").strip()
        err = root.findtext(".//errorMessage") or root.findtext(".//message") or status_code
        raise RuntimeError(f"{err_code}: {err}" if err_code else err)

    records: list[dict[str, str]] = []
    for record in root.findall(".//record"):
        fields: dict[str, str] = {}
        for item in record.findall("item"):
            code = item.get("metaCode") or item.get("metacode") or ""
            text = (item.text or "").strip()
            if code and text:
                fields[code] = text
        if fields:
            records.append(fields)
    return records


def _fetch_search_records(
    token: str,
    client_id: str,
    search_json: str,
    row: str,
    *,
    _retried: bool = False,
) -> list[dict[str, str]]:
    url = (
        f"{API_URL}?client_id={client_id}&token={token}"
        f"&version=1.0&action=search&target=ARTI"
        f"&searchQuery={urllib.parse.quote(search_json)}"
        f"&sortField=pubyear&sortBy=desc"
        f"&curPage=1&rowCount={row}"
    )
    try:
        return _parse_records(_http_get(url))
    except RuntimeError as exc:
        msg = str(exc)
        if any(token in msg for token in ("E4103", "E4101", "Token", "토큰", "Unauthorized")):
            _token_cache.access_expires_at = None
            new_token = get_access_token()
            url = (
                f"{API_URL}?client_id={client_id}&token={new_token}"
                f"&version=1.0&action=search&target=ARTI"
                f"&searchQuery={urllib.parse.quote(search_json)}"
                f"&sortField=pubyear&sortBy=desc"
                f"&curPage=1&rowCount={row}"
            )
            return _parse_records(_http_get(url))
        raise
    except urllib.error.HTTPError as exc:
        if exc.code in (401, 403) and not _retried:
            _token_cache.access_expires_at = None
            new_token = get_access_token()
            return _fetch_search_records(
                new_token, client_id, search_json, row, _retried=True
            )
        raise


def _keyword_priority(keyword: str) -> tuple[int, str]:
    """식품 도메인 키워드를 먼저, 지나치게 넓은 단어는 뒤로."""
    if any(hint in keyword for hint in _FOOD_HINTS):
        return (0, keyword)
    if keyword in _GENERIC_TERMS:
        return (2, keyword)
    return (1, keyword)


def _search_term_for_keyword(keyword: str) -> str:
    """기계·용기 등은 식품 맥락을 붙여 검색."""
    if keyword in _GENERIC_TERMS:
        return f"식품 {keyword}"
    return keyword


def _build_search_terms(keywords: list[str], *, max_terms: int = 4) -> list[str]:
    """API 호출·429 방지를 위해 우선순위 상위 N개 + 식품 폴백만 사용."""
    ordered = sorted({(kw or "").strip() for kw in keywords if (kw or "").strip()}, key=_keyword_priority)
    terms: list[str] = []
    for kw in ordered:
        if len(terms) >= max_terms:
            break
        term = _search_term_for_keyword(kw)
        if term not in terms:
            terms.append(term)
    for fallback in ("식품",):
        if fallback not in terms:
            terms.append(fallback)
            break
    return terms


def _records_to_domestic_items(
    records: list[dict[str, str]],
    *,
    year_floor: int,
    row_count: int,
    seen_cns: set[str],
    items: list[dict[str, str]],
) -> None:
    """JAKO·발행연도 필터 후 items에 병합(중복 CN 제외)."""
    for rec in records:
        cn_id = (rec.get("CN") or "").strip()
        if not cn_id.startswith(DOMESTIC_CN_PREFIX) or cn_id in seen_cns:
            continue
        title = html.unescape(rec.get("Title") or rec.get("TI") or "")
        if not title:
            continue
        pubyear = rec.get("Pubyear") or rec.get("PubYear") or rec.get("PY") or ""
        pub_year_num = _parse_year(pubyear).year
        if pub_year_num < year_floor:
            continue
        seen_cns.add(cn_id)
        items.append(
            {
                "title": title,
                "cn": cn_id,
                "url": f"https://scienceon.kisti.re.kr/srch/selectPORSrchArticle.do?cn={cn_id}",
                "pubyear": pubyear,
                "source": "ScienceON",
            }
        )
        if len(items) >= row_count:
            break


def search_domestic_articles(
    keywords: list[str],
    row_count: int = 5,
    *,
    min_pub_year: int | None = None,
) -> list[dict[str, str]]:
    """국내 논문(JAKO) 검색. 반환: title, cn, url, pubyear, source."""
    client_id = _cfg("SCIENCEON_CLIENT_ID")
    if not client_id or not _cfg("SCIENCEON_API_KEY"):
        return []

    year_floor = min_pub_year if min_pub_year is not None else date.today().year - 2
    fetch_count = str(min(max(row_count * 4, row_count), 20))

    # 업종 키워드를 개별 검색 후 병합 (식품 관련 키워드 우선)
    search_terms = _build_search_terms(keywords)
    # 한 번에 row_count를 채울 수 있도록 첫 호출은 넉넉히 요청
    first_fetch = str(min(max(row_count * 4, row_count), 20))
    later_fetch = str(min(max(row_count * 2, row_count), 10))

    token = get_access_token()
    items: list[dict[str, str]] = []
    seen_cns: set[str] = set()

    for idx, term in enumerate(search_terms):
        if len(items) >= row_count:
            break
        search_json = json.dumps({"BI": term}, ensure_ascii=False)
        batch_size = first_fetch if idx == 0 else later_fetch
        try:
            records = _fetch_search_records(token, client_id, search_json, batch_size)
        except urllib.error.HTTPError as exc:
            if exc.code == 429:
                logger.warning("ScienceON rate limit (429) on term=%r — stopping early", term)
                break
            raise
        _records_to_domestic_items(
            records,
            year_floor=year_floor,
            row_count=row_count,
            seen_cns=seen_cns,
            items=items,
        )

    return items


def records_to_report_items(records: list[dict[str, str]]) -> list[tuple[str, str, str, date]]:
    out: list[tuple[str, str, str, date]] = []
    for rec in records:
        out.append(
            (
                rec["title"],
                rec["url"],
                rec.get("source", "ScienceON"),
                _parse_year(rec.get("pubyear", "")),
            )
        )
    return out
