import json
import logging
import re
from typing import Any, Optional, List
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode, unquote
from urllib.request import urlopen

from matrix.external_api_budget import consume_external_api_unit_or_raise
from matrix.grid_keymaker_secret_manager import get_keymaker

logger = logging.getLogger(__name__)

HACCP_URL = "http://apis.data.go.kr/B553748/CertImgListService/getCertImgListService"

def _http_json(url: str) -> Optional[Any]:
    try:
        consume_external_api_unit_or_raise(units=1, label="phase3.data.go.kr")
        with urlopen(url, timeout=25) as resp:
            return json.loads(resp.read().decode("utf-8", errors="replace"))
    except (HTTPError, URLError, OSError, json.JSONDecodeError) as e:
        logger.warning("HACCP HTTP/JSON fetch failed: %s", e)
        return None

def _split_csv(s: str | None) -> List[str]:
    if not s or not str(s).strip():
        return []
    return [p.strip() for p in re.split(r"[,;]", str(s)) if p.strip()]

def fetch_haccp_product_info(prdlst_report_no: Optional[str], product_name: Optional[str]) -> dict:
    key = get_keymaker().get_secret("HACCP_PRODUCT_API_KEY")
    if not key:
        return {"found": False}

    pr = (prdlst_report_no or "").strip()
    pn = (product_name or "").strip()
    if not pr and not pn:
        return {"found": False}

    params: dict[str, str] = {
        "serviceKey": unquote(key) if "%" in key else key,
        "returnType": "json",
        "numOfRows": "10",
        "pageNo": "1",
    }
    if pr:
        params["prdlstReportNo"] = pr
    if pn and not pr:
        params["prdlstNm"] = pn

    q = urlencode(params, safe=":/+(),", quote_via=quote)
    url = f"{HACCP_URL}?{q}"
    data = _http_json(url)
    if not data:
        return {"found": False, "prdlst_report_no": pr}

    try:
        body = (data.get("response") or {}).get("body") or {}
        total = int(body.get("totalCount") or 0)
        if total < 1:
            return {"found": False, "prdlst_report_no": pr}

        items = body.get("items") or {}
        raw_item = items.get("item")
        if raw_item is None:
            return {"found": False, "prdlst_report_no": pr}
        rows: list[dict[str, Any]] = raw_item if isinstance(raw_item, list) else [raw_item]
        it = rows[0]

        rawmtrl = _split_csv(it.get("rawmtrl"))
        allergy = _split_csv(it.get("allergy"))
        imgs: list[str] = []
        for k in ("imgurl1", "imgurl2"):
            u = it.get(k)
            if isinstance(u, str) and u.strip().startswith("http"):
                imgs.append(u.strip())

        return {
            "found": True,
            "prdlst_report_no": str(it.get("prdlstReportNo") or pr),
            "product_name": it.get("prdlstNm"),
            "manufacturer": it.get("manufacture"),
            "raw_materials": rawmtrl,
            "allergens": allergy,
            "nutrient_info": it.get("nutrient"),
            "image_urls": imgs,
            "barcode": it.get("barcode"),
        }
    except (TypeError, KeyError, ValueError) as e:
        logger.warning("HACCP response parsing failed: %s", e)
        return {"found": False, "prdlst_report_no": pr}
