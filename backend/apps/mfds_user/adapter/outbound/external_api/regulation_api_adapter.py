import os
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, date
import asyncio
from typing import List, Optional
import logging

from mfds_user.app.ports.output.regulation_api_port import RegulationApiPort
from mfds_user.domain.entities.regulation_entity import Regulation
from mfds_user.domain.value_objects.regulation_vo import LawType
from mfds_user.domain.value_objects.report_section_vo import ReportItem

logger = logging.getLogger(__name__)

class RegulationApiAdapter(RegulationApiPort):
    def __init__(self) -> None:
        self.api_key = os.getenv("LAW_API_KEY")

    def _parse_xml_date(self, date_str: Optional[str]) -> Optional[date]:
        if not date_str:
            return None
        date_str = date_str.strip()
        if len(date_str) == 8:
            try:
                return datetime.strptime(date_str, "%Y%m%d").date()
            except Exception:
                pass
        return None

    def _fetch_from_api_sync(self, target: str, query: str) -> List[Regulation]:
        if not self.api_key:
            logger.warning("LAW_API_KEY is not set - returning empty results")
            return []

        # Law API endpoint
        params = {
            "OC": self.api_key,
            "target": target,
            "query": query,
            "type": "XML"
        }
        url = f"http://www.law.go.kr/DRF/lawSearch.do?{urllib.parse.urlencode(params)}"
        
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as response:
                xml_data = response.read()
                
            root = ET.fromstring(xml_data)
            
            regulations = []
            if target == "law":
                # Parse laws
                for item in root.findall(".//law"):
                    law_id = item.findtext("법령일련번호", "")
                    title = item.findtext("법령명한글", "")
                    change_type = item.findtext("제개정구분명", "")
                    prom_date_str = item.findtext("공포일자", "")
                    prom_no = item.findtext("공포번호", "")
                    enf_date_str = item.findtext("시행일자", "")
                    source = item.findtext("소관부처명", "")
                    link = item.findtext("법령상세링크", "")
                    
                    if not law_id or not title:
                        continue
                        
                    url = f"https://www.law.go.kr{link}" if link.startswith("/") else link
                    
                    regulations.append(Regulation(
                        law_id=law_id,
                        title=title,
                        law_type=LawType.LAW,
                        change_type=change_type,
                        promulgation_date=self._parse_xml_date(prom_date_str),
                        promulgation_no=prom_no,
                        enforcement_date=self._parse_xml_date(enf_date_str),
                        source=source,
                        url=url
                    ))
            elif target == "admrul":
                # Parse administrative rules
                for item in root.findall(".//admrul"):
                    law_id = item.findtext("행정규칙일련번호", "")
                    title = item.findtext("행정규칙명", "")
                    change_type = item.findtext("제개정구분명", "")
                    prom_date_str = item.findtext("공포일자", "")
                    prom_no = item.findtext("공포번호", "")
                    enf_date_str = item.findtext("시행일자", "")
                    source = item.findtext("소관부처명", "")
                    link = item.findtext("행정규칙상세링크", "")
                    
                    if not law_id or not title:
                        continue
                        
                    url = f"https://www.law.go.kr{link}" if link.startswith("/") else link
                    
                    regulations.append(Regulation(
                        law_id=law_id,
                        title=title,
                        law_type=LawType.ADMRUL,
                        change_type=change_type,
                        promulgation_date=self._parse_xml_date(prom_date_str),
                        promulgation_no=prom_no,
                        enforcement_date=self._parse_xml_date(enf_date_str),
                        source=source,
                        url=url
                    ))
            return regulations
        except Exception as e:
            logger.error(f"Error fetching from Law API target={target}: {e}")
            return []

    async def search_regulations(self, query: str) -> List[Regulation]:
        loop = asyncio.get_running_loop()
        laws_task = loop.run_in_executor(None, self._fetch_from_api_sync, "law", query)
        admruls_task = loop.run_in_executor(None, self._fetch_from_api_sync, "admrul", query)
        
        laws, admruls = await asyncio.gather(laws_task, admruls_task)
        
        merged = laws + admruls
        merged.sort(key=lambda r: r.enforcement_date or date.min, reverse=True)
        return merged

    async def fetch(self, keywords: List[str]) -> List[ReportItem]:
        if not keywords:
            return []
            
        tasks = []
        for kw in keywords[:3]:
            tasks.append(self.search_regulations(kw))
            
        results = await asyncio.gather(*tasks)
        
        seen_ids = set()
        items = []
        for res_list in results:
            for reg in res_list:
                if reg.law_id not in seen_ids:
                    seen_ids.add(reg.law_id)
                    items.append(ReportItem(
                        title=reg.title,
                        url=reg.url,
                        source=reg.source or "법제처",
                        published_at=reg.enforcement_date or date.today()
                    ))
                    
        items.sort(key=lambda x: x.published_at, reverse=True)
        return items
