import os
import re
import urllib.request
import urllib.parse
import json
from datetime import date, timedelta
import asyncio
from typing import List
import logging

from mfds_user.app.ports.output.crawler_ports import ResearchPort
from mfds_user.domain.value_objects.report_section_vo import ReportItem
from mfds_user.adapter.outbound.external_api.scienceon_gateway_client import (
    records_to_report_items,
    search_domestic_articles,
)

logger = logging.getLogger(__name__)

class PubMedAdapter(ResearchPort):
    BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

    def __init__(self) -> None:
        self.api_key = os.getenv("NCBI_API_KEY")

    async def fetch(self, keywords: List[str], days_back: int = 30) -> List[ReportItem]:
        if not keywords:
            return []
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._fetch_sync, keywords, days_back)

    def _fetch_sync(self, keywords: List[str], days_back: int) -> List[ReportItem]:
        if not self.api_key:
            logger.warning("NCBI_API_KEY is not set - returning empty PubMed results")
            return []

        try:
            # Build search query
            # Escape keywords
            query_kws = " OR ".join(f'"{kw}"' for kw in keywords[:5])
            query = f'({query_kws}) AND ("last {days_back} days"[PDat]) AND (food[MeSH Terms] OR food safety[MeSH Terms])'
            
            params = {
                "db": "pubmed",
                "term": query,
                "retmax": "5",
                "sort": "pub date",
                "api_key": self.api_key,
                "retmode": "json"
            }
            url = f"{self.BASE}/esearch.fcgi?{urllib.parse.urlencode(params)}"
            
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as response:
                search_res = json.loads(response.read().decode("utf-8"))

            pmids = search_res.get("esearchresult", {}).get("idlist", [])
            if not pmids:
                return []

            # 2. Get summaries
            summary_params = {
                "db": "pubmed",
                "id": ",".join(pmids),
                "api_key": self.api_key,
                "retmode": "json"
            }
            summary_url = f"{self.BASE}/esummary.fcgi?{urllib.parse.urlencode(summary_params)}"
            
            req_sum = urllib.request.Request(summary_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req_sum, timeout=10) as response:
                summary_res = json.loads(response.read().decode("utf-8"))

            items = []
            results = summary_res.get("result", {})
            for pmid in pmids:
                item = results.get(pmid)
                if not item:
                    continue
                
                title = item.get("title", "")
                pub_date_str = item.get("pubdate", "")
                
                # Try parsing pubdate, e.g. "2026 Jun 01" or "2026-06-01"
                pub_date = date.today()
                match = re.search(r'(\d{4})', pub_date_str)
                if match:
                    try:
                        pub_date = date(int(match.group(1)), 1, 1)
                    except ValueError:
                        pass
                
                items.append(ReportItem(
                    title=title,
                    url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                    source="PubMed",
                    published_at=pub_date
                ))
            return items
        except Exception as e:
            logger.error(f"Error fetching from PubMed: {e}")
            return []

class ScienceOnAdapter(ResearchPort):
    def __init__(self) -> None:
        self.api_key = os.getenv("SCIENCEON_API_KEY")
        self.client_id = os.getenv("SCIENCEON_CLIENT_ID")
        self.mac_address = os.getenv("SCIENCEON_MAC_ADDRESS")

    async def fetch(self, keywords: List[str], days_back: int = 30) -> List[ReportItem]:
        if not keywords:
            return []
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._fetch_sync, keywords, days_back)

    def _fetch_sync(self, keywords: List[str], days_back: int) -> List[ReportItem]:
        if not self.api_key or not self.client_id or not self.mac_address:
            logger.warning(
                "ScienceON env incomplete (SCIENCEON_API_KEY/CLIENT_ID/MAC_ADDRESS) — skipping"
            )
            return []

        try:
            # ScienceON은 발행연도만 제공 → 일 단위 days_back 대신 최근 연도 기준 필터
            min_year = date.today().year - (1 if days_back <= 365 else 2)
            records = search_domestic_articles(
                keywords,
                row_count=5,
                min_pub_year=min_year,
            )
            items: List[ReportItem] = []
            for title, url, source, pub_date in records_to_report_items(records):
                items.append(
                    ReportItem(
                        title=title,
                        url=url,
                        source=source,
                        published_at=pub_date,
                    )
                )
            logger.info("ScienceON domestic articles fetched: count=%s", len(items))
            return items
        except Exception as e:
            logger.error(f"Error fetching from ScienceON: {e}")
            return []

class CompositeResearchAdapter(ResearchPort):
    def __init__(self, pubmed: PubMedAdapter, scienceon: ScienceOnAdapter) -> None:
        self.pubmed = pubmed
        self.scienceon = scienceon

    async def fetch(self, keywords: List[str], days_back: int = 30) -> List[ReportItem]:
        # Fetch concurrently
        pubmed_task = self.pubmed.fetch(keywords, days_back)
        scienceon_task = self.scienceon.fetch(keywords, days_back)
        
        pubmed_res, scienceon_res = await asyncio.gather(pubmed_task, scienceon_task)

        # 국내(ScienceON) · 해외(PubMed) 균형 — PubMed만 5건 채우는 것 방지
        merged = scienceon_res[:3] + pubmed_res[:3]
        
        # If both are empty, return 1 dummy research item so the section is not completely blank
        if not merged:
            merged.append(ReportItem(
                title="식품 안전 예방 통제 시스템 연구 동향 (임시)",
                url="https://pubmed.ncbi.nlm.nih.gov/",
                source="PubMed",
                published_at=date.today()
            ))
            
        merged.sort(key=lambda x: x.published_at, reverse=True)
        return merged[:5]
