from __future__ import annotations

import logging
from html.parser import HTMLParser
from urllib.parse import urldefrag, urljoin

import httpx

from ontology.app.dtos.web_dto import FetchedPage
from ontology.app.ports.output.web_fetcher_port import IWebFetcherPort

logger = logging.getLogger(__name__)

_USER_AGENT = "Mozilla/5.0 (compatible; FoodOpenLabBot/1.0; +ontology-crawler)"
_TIMEOUT_SECONDS = 10.0
_SKIP_TAGS = {"script", "style", "noscript", "template"}


class HttpxWebFetcherAdapter(IWebFetcherPort):
    """httpx로 페이지를 받고 stdlib html.parser로 링크·텍스트를 추출한다.

    외부 파싱 라이브러리(bs4/lxml) 의존 없이 표준 라이브러리만 사용한다.
    """

    def __init__(self, timeout: float = _TIMEOUT_SECONDS) -> None:
        self._timeout = timeout

    async def fetch(self, url: str) -> FetchedPage:
        try:
            async with httpx.AsyncClient(
                follow_redirects=True,
                timeout=self._timeout,
                headers={"User-Agent": _USER_AGENT},
            ) as client:
                resp = await client.get(url)
        except httpx.HTTPError as exc:
            logger.warning("[HttpxWebFetcherAdapter] 페치 실패 url=%s err=%s", url, exc)
            return FetchedPage(url=url, status_code=0)

        content_type = resp.headers.get("content-type", "").lower()
        if resp.status_code != 200 or "html" not in content_type:
            return FetchedPage(url=url, status_code=resp.status_code)

        parser = _PageParser(str(resp.url))
        try:
            parser.feed(resp.text)
        except Exception as exc:  # 깨진 HTML 등 파싱 실패는 빈 결과로 처리
            logger.warning("[HttpxWebFetcherAdapter] 파싱 실패 url=%s err=%s", url, exc)
            return FetchedPage(url=url, status_code=resp.status_code)

        return FetchedPage(
            url=url,
            status_code=resp.status_code,
            title=parser.title.strip(),
            text=parser.text,
            links=parser.links,
        )


class _PageParser(HTMLParser):
    """<a href> 링크(절대경로)·<title>·본문 텍스트를 수집한다."""

    def __init__(self, base_url: str) -> None:
        super().__init__(convert_charrefs=True)
        self._base_url = base_url
        self._links: list[str] = []
        self._title_parts: list[str] = []
        self._text_parts: list[str] = []
        self._skip_depth = 0
        self._in_title = False

    @property
    def title(self) -> str:
        return " ".join(self._title_parts)

    @property
    def text(self) -> str:
        return " ".join(self._text_parts)

    @property
    def links(self) -> tuple[str, ...]:
        # 중복 제거(입력 순서 보존) + http(s)만 유지.
        deduped = dict.fromkeys(
            link for link in self._links if link.startswith(("http://", "https://"))
        )
        return tuple(deduped)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in _SKIP_TAGS:
            self._skip_depth += 1
        elif tag == "title":
            self._in_title = True
        elif tag == "a":
            for key, value in attrs:
                if key == "href" and value:
                    absolute = urldefrag(urljoin(self._base_url, value)).url
                    self._links.append(absolute)

    def handle_endtag(self, tag: str) -> None:
        if tag in _SKIP_TAGS and self._skip_depth > 0:
            self._skip_depth -= 1
        elif tag == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        stripped = data.strip()
        if not stripped:
            return
        if self._in_title:
            self._title_parts.append(stripped)
        else:
            self._text_parts.append(stripped)
