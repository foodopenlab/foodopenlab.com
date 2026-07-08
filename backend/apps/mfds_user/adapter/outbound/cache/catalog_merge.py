"""?�품?�전 catalog 병합 ??기존 ?�?�본 ?��??�규�?추�?, ?�일 �?중복 ?�??방�?."""

import json
from dataclasses import dataclass
from typing import Callable, Tuple, List, Dict

@dataclass(frozen=True)
class CatalogMergeStats:
    added: int = 0
    updated: int = 0
    skipped: int = 0

    @property
    def touched(self) -> int:
        return self.added + self.updated

def item_fingerprint(item: dict, *, fields: Tuple[str, ...]) -> str:
    payload = {k: str(item.get(k) or "").strip() for k in fields}
    return json.dumps(payload, sort_keys=True, ensure_ascii=False)

def merge_catalog_maps(
    baseline: Dict[str, dict],
    incoming: List[dict],
    key_fn: Callable[[dict], str],
    *,
    fields: Tuple[str, ...],
) -> Tuple[Dict[str, dict], CatalogMergeStats]:
    added = 0
    updated = 0
    skipped = 0
    for item in incoming:
        key = key_fn(item)
        if not key:
            continue
        fp = item_fingerprint(item, fields=fields)
        existing = baseline.get(key)
        if existing is None:
            baseline[key] = item
            added += 1
            continue
        if item_fingerprint(existing, fields=fields) == fp:
            skipped += 1
            continue
        baseline[key] = item
        updated += 1
    return baseline, CatalogMergeStats(added=added, updated=updated, skipped=skipped)

def raw_json_fingerprint(raw: dict) -> str:
    return json.dumps(raw, sort_keys=True, ensure_ascii=False, default=str)
