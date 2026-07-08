from mcp.server.fastmcp import FastMCP

mcp = FastMCP("파이퍼 헨드릭스 CEO")


@mcp.tool()
async def introduce_myself() -> str:
    """CEO 자기소개"""
    return "안녕하세요, 파이퍼 헨드릭스 CEO입니다."


@mcp.tool()
async def get_company_vision() -> str:
    """회사 비전 및 전략 방향 제시"""
    return "파이퍼의 비전은 중간 단계 없는 완전한 탈중앙화 인터넷을 구축하는 것입니다. CEO로서 기술 혁신과 팀 역량을 통해 이를 실현합니다."


@mcp.tool()
async def make_strategic_decision(topic: str) -> str:
    """주요 전략적 의사결정 (topic: 결정할 안건)"""
    return f"CEO 헨드릭스입니다. '{topic}'에 대해 기술적 우수성과 팀 합의를 바탕으로 전략적 결정을 내리겠습니다."


@mcp.tool()
async def review_team_performance() -> str:
    """팀 전체 성과 검토"""
    return (
        "CEO로서 팀 성과를 검토합니다. "
        "길포일(시스템), 다이내시(개발), 빅헤드(HR 지원), 던(COO)의 협력 아래 목표를 달성 중입니다."
    )
