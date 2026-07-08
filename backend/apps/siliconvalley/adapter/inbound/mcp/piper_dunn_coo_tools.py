from mcp.server.fastmcp import FastMCP

mcp = FastMCP("파이퍼 던 COO")


@mcp.tool()
async def introduce_myself() -> str:
    """COO 자기소개"""
    return "안녕하세요, 파이퍼 던 COO입니다."


@mcp.tool()
async def get_operations_report() -> str:
    """운영 현황 보고"""
    return (
        "COO 던입니다. 이번 주 운영 현황을 보고합니다. "
        "서비스 가동률 99.97% / 고객 지원 처리율 98.2% / 주요 OKR 달성률 87%입니다."
    )


@mcp.tool()
async def schedule_meeting(participants: str, agenda: str) -> str:
    """팀 회의 일정 조율 (participants: 참석자 목록, agenda: 안건)"""
    return (
        f"COO 던입니다. {participants} 참석자를 포함한 회의를 일정에 등록했습니다. "
        f"안건: {agenda}. 캘린더 초대장을 발송하겠습니다."
    )


@mcp.tool()
async def coordinate_partnership(partner: str) -> str:
    """파트너십 조율 (partner: 협력사명)"""
    return (
        f"COO 던입니다. '{partner}'와의 파트너십 협의를 조율하겠습니다. "
        "계약 조건 검토 및 킥오프 미팅 일정을 진행하겠습니다."
    )
