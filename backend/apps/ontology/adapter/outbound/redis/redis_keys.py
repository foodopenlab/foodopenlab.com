"""크롤/스크랩 파이프라인이 쓰는 Redis 키 스키마 (SSOT).

값을 바꿀 땐 시드/키워드 주입 스크립트도 함께 맞춘다.
"""

# 크롤러가 소비하는 시드 웹사이트 큐 (LIST, RPUSH 로 주입 → LPOP 로 소비)
CRAWLER_TARGETS = "ontology:crawler:targets"

# 크롤러·스크래퍼 공용 키워드 (SET, SADD 로 주입)
CRAWLER_KEYWORDS = "ontology:crawler:keywords"

# 크롤러 → 스크래퍼로 넘기는 URL 작업 큐 (LIST)
SCRAPER_QUEUE = "ontology:scraper:queue"
