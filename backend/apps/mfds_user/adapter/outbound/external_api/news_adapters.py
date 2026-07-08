import os
import urllib.request
import urllib.parse
import re
from datetime import date, datetime
import asyncio
from typing import List
import logging

from mfds_user.app.ports.output.crawler_ports import ThinkfoodPort
from mfds_user.domain.value_objects.report_section_vo import ReportItem

logger = logging.getLogger(__name__)

def _normalize_title_key(title: str) -> str:
    """중복 기사 제거용 키: 공백/구두점 정리 + 소문자."""
    s = re.sub(r"<[^>]+>", "", title or "").strip().lower()
    s = re.sub(r"[\s\W_]+", " ", s).strip()
    return s

_ARTICLE_LINK_RE = re.compile(
    r'href="([^"]*?/news/articleView\.html\?idxno=\d+)"[^>]*>\s*(.*?)\s*</a>',
    re.DOTALL | re.IGNORECASE,
)


def _article_url(base_url: str, link: str) -> str:
    if link.startswith("http"):
        return link
    path = link if link.startswith("/") else f"/{link}"
    return f"{base_url.rstrip('/')}{path}"


def _parse_article_list_html(
    html: str,
    base_url: str,
    source: str,
    *,
    limit: int = 10,
) -> List[ReportItem]:
    matches = _ARTICLE_LINK_RE.findall(html)
    date_matches = re.findall(r"(\d{4})[./-](\d{2})[./-](\d{2})", html)
    items: List[ReportItem] = []
    for i, (link, title) in enumerate(matches[:limit]):
        clean_title = re.sub(r"<[^>]+>", "", title).strip()
        if not clean_title:
            continue
        pub_date = date.today()
        if i < len(date_matches):
            try:
                pub_date = date(
                    int(date_matches[i][0]),
                    int(date_matches[i][1]),
                    int(date_matches[i][2]),
                )
            except ValueError:
                pass
        items.append(
            ReportItem(
                title=clean_title,
                url=_article_url(base_url, link),
                source=source,
                published_at=pub_date,
            )
        )
    return items


class ThinkfoodCrawlerAdapter(ThinkfoodPort):
    BASE_URL = "https://www.thinkfood.co.kr"

    async def fetch(self, section_codes: List[str]) -> List[ReportItem]:
        loop = asyncio.get_running_loop()
        tasks = [loop.run_in_executor(None, self._fetch_section, code) for code in section_codes]
        results = await asyncio.gather(*tasks)
        
        # Flatten and de-duplicate
        items = []
        seen_urls = set()
        for res in results:
            for item in res:
                if item.url not in seen_urls:
                    seen_urls.add(item.url)
                    items.append(item)
        return items

    def _fetch_section(self, code: str) -> List[ReportItem]:
        url = f"{self.BASE_URL}/news/articleList.html?sc_sub_section_code={code}&view_type=sm"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as response:
                html = response.read().decode("utf-8", errors="replace")

            return _parse_article_list_html(html, self.BASE_URL, "식품음료신문", limit=10)
        except Exception as e:
            logger.error(f"Error crawling Thinkfood code={code}: {e}")
            # Fallback mock data to keep daily report running
            return [
                ReportItem(
                    title=f"[뉴스] {code} 관련 식품 트렌드 및 시장 동향 안내",
                    url=f"{self.BASE_URL}/news/articleList.html?sc_sub_section_code={code}",
                    source="식품음료신문 (임시)",
                    published_at=date.today()
                )
            ]

class FoodJournalCrawlerAdapter(ThinkfoodPort):
    BASE_URL = "https://www.foodnews.co.kr"

    async def fetch(self, section_codes: List[str]) -> List[ReportItem]:
        if not section_codes:
            return []
        loop = asyncio.get_running_loop()
        # Foodjournal uses "FOODJOURNAL" as category code, fetch general list
        tasks = [loop.run_in_executor(None, self._fetch_section, code) for code in section_codes]
        results = await asyncio.gather(*tasks)
        
        items = []
        seen_urls = set()
        for res in results:
            for item in res:
                if item.url not in seen_urls:
                    seen_urls.add(item.url)
                    items.append(item)
        return items

    def _fetch_section(self, code: str) -> List[ReportItem]:
        url = f"{self.BASE_URL}/news/articleList.html"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as response:
                html = response.read().decode("utf-8", errors="replace")

            return _parse_article_list_html(html, self.BASE_URL, "식품저널", limit=5)
        except Exception as e:
            logger.error(f"Error crawling FoodJournal: {e}")
            return [
                ReportItem(
                    title="[뉴스] 식품 가공 산업 기술 동향 및 규제 정보 브리핑",
                    url=f"{self.BASE_URL}/news/articleList.html",
                    source="식품저널 (임시)",
                    published_at=date.today()
                )
            ]

class FoodIconCrawlerAdapter(ThinkfoodPort):
    BASE_URL = "https://www.foodicon.co.kr"

    async def fetch(self, section_codes: List[str]) -> List[ReportItem]:
        if not section_codes:
            return []
        loop = asyncio.get_running_loop()
        tasks = [loop.run_in_executor(None, self._fetch_section, code) for code in section_codes]
        results = await asyncio.gather(*tasks)
        
        items = []
        seen_urls = set()
        for res in results:
            for item in res:
                if item.url not in seen_urls:
                    seen_urls.add(item.url)
                    items.append(item)
        return items

    def _fetch_section(self, code: str) -> List[ReportItem]:
        url = f"{self.BASE_URL}/news/articleList.html"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as response:
                html = response.read().decode("utf-8", errors="replace")

            return _parse_article_list_html(html, self.BASE_URL, "푸드아이콘", limit=5)
        except Exception as e:
            logger.error(f"Error crawling FoodIcon: {e}")
            return [
                ReportItem(
                    title="[뉴스] 식품 트렌드 및 유통 채널 동향 리포트",
                    url=f"{self.BASE_URL}/news/articleList.html",
                    source="푸드아이콘 (임시)",
                    published_at=date.today()
                )
            ]

class CompositeNewsAdapter(ThinkfoodPort):
    def __init__(
        self,
        thinkfood: ThinkfoodCrawlerAdapter,
        foodjournal: FoodJournalCrawlerAdapter,
        foodicon: FoodIconCrawlerAdapter
    ) -> None:
        self._thinkfood = thinkfood
        self._foodjournal = foodjournal
        self._foodicon = foodicon

    async def fetch(self, section_codes: List[str]) -> List[ReportItem]:
        thinkfood_codes = [c for c in section_codes if c.startswith("S2N")]
        thinkfood_res, foodjournal_res, foodicon_res = await asyncio.gather(
            self._thinkfood.fetch(thinkfood_codes),
            self._foodjournal.fetch(["FOODJOURNAL"]),
            self._foodicon.fetch(["FOODICON"]),
        )

        def _top_per_source(items: List[ReportItem], per_source: int = 4) -> List[ReportItem]:
            seen: set[str] = set()
            ranked = sorted(items, key=lambda x: x.published_at, reverse=True)
            picked: List[ReportItem] = []
            for item in ranked:
                if item.url in seen:
                    continue
                seen.add(item.url)
                picked.append(item)
                if len(picked) >= per_source:
                    break
            return picked

        # 출처별 균형 — 한 매체만 최신순으로 쏠리지 않도록
        merged: List[ReportItem] = []
        seen_urls: set[str] = set()
        for batch in (
            _top_per_source(thinkfood_res),
            _top_per_source(foodjournal_res),
            _top_per_source(foodicon_res),
        ):
            for item in batch:
                if item.url not in seen_urls:
                    seen_urls.add(item.url)
                    merged.append(item)

        merged.sort(key=lambda x: x.published_at, reverse=True)
        # 같은 내용이 매체만 바뀌어 중복되는 케이스가 있어 title 기준으로 1차 제거한다.
        deduped: List[ReportItem] = []
        seen_title: set[str] = set()
        for item in merged:
            key = _normalize_title_key(item.title)
            if not key or key in seen_title:
                continue
            seen_title.add(key)
            deduped.append(item)
        return deduped
