import os
import urllib.request
import urllib.parse
import re
from datetime import date, datetime
import asyncio
from typing import List
import logging

from mfds_user.app.ports.output.crawler_ports import MfdsPressPort, FoodStatsPort, RecallReportPort
from mfds_user.domain.value_objects.report_section_vo import ReportItem
from mfds_user.app.ports.output.recall_repository import RecallRepositoryPort
from mfds_user.adapter.outbound.cache.mfds_silence import is_mfds_silenced

logger = logging.getLogger(__name__)


def _coerce_report_date(value: date | datetime | str | None) -> date:
    if not value:
        return date.today()
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value[:10])
        except ValueError:
            return date.today()
    return date.today()


class MfdsPressAdapter(MfdsPressPort):
    BASE_URL = "https://www.mfds.go.kr/brd/m_99/list.do"

    async def fetch(self, keywords: List[str]) -> List[ReportItem]:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._fetch_sync, keywords)

    def _fetch_sync(self, keywords: List[str]) -> List[ReportItem]:
        if is_mfds_silenced():
            logger.warning("MFDS press crawl SKIPPED (silenced)")
            return []
        try:
            req = urllib.request.Request(self.BASE_URL, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as response:
                html = response.read().decode("utf-8", errors="replace")

            # Extract view links and titles
            # Example: href="/brd/m_99/view.do?seq=48425&amp;srchFr=&amp;srchTo=..." title="식약처, ..."
            # or standard td elements
            matches = re.findall(r'href="(/brd/m_99/view\.do\?seq=\d+[^"]*)"[^>]*>(.*?)</a>', html, re.DOTALL)
            date_matches = re.findall(r'(\d{4})-\d{2}-\d{2}', html)

            items = []
            for i, (link, title) in enumerate(matches[:15]):
                clean_title = re.sub(r'<[^>]+>', '', title).strip()
                if not clean_title:
                    continue

                # Filter by keyword if provided
                if keywords and not any(kw in clean_title for kw in keywords):
                    continue

                pub_date = date.today()
                if i < len(date_matches):
                    try:
                        parts = date_matches[i].split("-")
                        pub_date = date(int(parts[0]), int(parts[1]), int(parts[2]))
                    except (ValueError, IndexError):
                        pass

                # Clean link ampersands
                clean_link = link.replace("&amp;", "&")
                items.append(ReportItem(
                    title=clean_title,
                    url=f"https://www.mfds.go.kr{clean_link}",
                    source="식품의약품안전처",
                    published_at=pub_date
                ))

            # If keyword filter left nothing, return top 3 general press releases
            if not items and matches:
                for i, (link, title) in enumerate(matches[:3]):
                    clean_title = re.sub(r'<[^>]+>', '', title).strip()
                    pub_date = date.today()
                    if i < len(date_matches):
                        try:
                            parts = date_matches[i].split("-")
                            pub_date = date(int(parts[0]), int(parts[1]), int(parts[2]))
                        except (ValueError, IndexError):
                            pass
                    clean_link = link.replace("&amp;", "&")
                    items.append(ReportItem(
                        title=clean_title,
                        url=f"https://www.mfds.go.kr{clean_link}",
                        source="식품의약품안전처",
                        published_at=pub_date
                    ))
            return items
        except Exception as e:
            logger.error(f"Error crawling MFDS press releases: {e}")
            return [
                ReportItem(
                    title="식약처 식품 안전 및 위생 관리 감독 기준 강화 동향",
                    url="https://www.mfds.go.kr/brd/m_99/list.do",
                    source="식약처",
                    published_at=date.today()
                )
            ]

class FisNewsletterCrawlerAdapter(FoodStatsPort):
    BASE_URL = "https://www.atfis.or.kr"
    NEWSLETTER_PATH = "/article/newsletter/list.do"

    async def fetch(self, keywords: List[str]) -> List[ReportItem]:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._fetch_sync, keywords)

    def _fetch_sync(self, keywords: List[str]) -> List[ReportItem]:
        url = f"{self.BASE_URL}{self.NEWSLETTER_PATH}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as response:
                html = response.read().decode("utf-8", errors="replace")

            # Match links and titles in newsletter list
            matches = re.findall(r'href="(/article/newsletter/view\.do\?seq=\d+[^"]*)"[^>]*>(.*?)</a>', html, re.DOTALL)
            date_matches = re.findall(r'(\d{4})[.-](\d{2})[.-](\d{2})', html)

            items = []
            for i, (link, title) in enumerate(matches[:5]):
                clean_title = re.sub(r'<[^>]+>', '', title).strip()
                if not clean_title:
                    continue

                pub_date = date.today()
                if i < len(date_matches):
                    try:
                        pub_date = date(int(date_matches[i][0]), int(date_matches[i][1]), int(date_matches[i][2]))
                    except (ValueError, IndexError):
                        pass

                clean_link = link.replace("&amp;", "&")
                items.append(ReportItem(
                    title=clean_title,
                    url=f"{self.BASE_URL}{clean_link}",
                    source="aT 식품산업통계정보 뉴스레터",
                    published_at=pub_date
                ))

            # Filter by keywords if matching
            matched_items = []
            if keywords:
                for item in items:
                    if any(kw in item.title for kw in keywords):
                        matched_items.append(item)
            
            return matched_items if matched_items else items[:1]
        except Exception as e:
            logger.error(f"Error crawling FIS Newsletters: {e}")
            return [
                ReportItem(
                    title="FIS 식품산업통계정보 국내 주요 가공식품 시장 트렌드 뉴스레터",
                    url=f"{self.BASE_URL}{self.NEWSLETTER_PATH}",
                    source="FIS 식품산업통계정보",
                    published_at=date.today()
                )
            ]

class RecallReportAdapter(RecallReportPort):
    def __init__(self, recall_repo: RecallRepositoryPort) -> None:
        self.recall_repo = recall_repo

    async def fetch(self, keywords: List[str]) -> List[ReportItem]:
        tasks = []
        for kw in (keywords or [])[:5]:
            tasks.append(self.recall_repo.get_latest_by_food_type(kw, limit=3))

        results = await asyncio.gather(*tasks) if tasks else []

        seen_ids: set[str] = set()
        items: list[ReportItem] = []
        for res_list in results:
            for r in res_list:
                if r.id in seen_ids:
                    continue
                seen_ids.add(r.id)
                items.append(
                    ReportItem(
                        title=f"{r.product_name} - {r.recall_reason}",
                        # 프론트 라우트로 연결 (배포/로컬 공통)
                        url=f"/recalls/{r.id}",
                        source=f"{r.manufacturer} ({r.food_type})",
                        published_at=_coerce_report_date(r.registered_at),
                    )
                )

        # 키워드 매칭이 약하면 최신 회수가 과거로 밀릴 수 있으니, 최신 전체를 최소로 섞어준다.
        if not items:
            latest = await self.recall_repo.get_list(page=1, size=5)
            for r in latest:
                if r.id in seen_ids:
                    continue
                seen_ids.add(r.id)
                items.append(
                    ReportItem(
                        title=f"{r.product_name} - {r.recall_reason}",
                        url=f"/recalls/{r.id}",
                        source=f"{r.manufacturer} ({r.food_type})",
                        published_at=_coerce_report_date(r.registered_at),
                    )
                )

        items.sort(key=lambda x: x.published_at, reverse=True)
        return items[:5]
