from mcp.server.fastmcp import FastMCP

mcp = FastMCP("파이퍼 빅헤티 HR")


@mcp.tool()
async def introduce_myself() -> str:
    """HR 담당 자기소개"""
    return "안녕하세요, 파이퍼 빅헤티 HR입니다."


@mcp.tool()
async def post_job_opening(position: str) -> str:
    """채용 공고 등록 (position: 채용 직무명)"""
    return f"HR 빅헤티입니다. '{position}' 포지션 채용 공고를 등록했습니다. 지원자 검토를 시작하겠습니다."


@mcp.tool()
async def onboard_new_employee(name: str) -> str:
    """신규 입사자 온보딩 (name: 입사자 이름)"""
    return (
        f"HR 빅헤티입니다. '{name}' 님의 온보딩을 시작합니다. "
        "사원증 발급, 장비 세팅, 팀 소개 일정을 안내해 드리겠습니다."
    )


@mcp.tool()
async def get_welfare_benefits() -> str:
    """복지 혜택 안내"""
    return (
        "파이퍼의 복지 혜택을 안내합니다. "
        "유연 근무제, 교육비 지원, 건강검진, 점심 제공 등이 포함됩니다. "
        "자세한 내용은 HR 빅헤티에게 문의하세요."
    )
