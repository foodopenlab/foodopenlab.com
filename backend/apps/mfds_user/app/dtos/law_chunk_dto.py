from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LawChunkHit:
    law_nm: str
    article_no: str
    article_title: str
    content: str
    source_type: str
    similarity: float
