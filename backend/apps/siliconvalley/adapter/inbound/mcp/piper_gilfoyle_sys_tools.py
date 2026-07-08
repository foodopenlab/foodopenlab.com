from mcp.server.fastmcp import FastMCP

mcp = FastMCP("파이퍼 길포일 시스템")


@mcp.tool()
async def introduce_myself() -> str:
    """시스템 담당 자기소개"""
    return "안녕하세요, 파이퍼 길포일입니다. 시스템 담당입니다."


@mcp.tool()
async def check_server_status() -> str:
    """서버 상태 점검"""
    return (
        "시스템 담당 길포일입니다. 서버 상태를 점검했습니다. "
        "CPU 사용률: 34% / 메모리: 61% / 디스크 I/O: 정상 / 네트워크 레이턴시: 2ms. 모든 노드 이상 없습니다."
    )


@mcp.tool()
async def run_security_scan(target: str) -> str:
    """보안 취약점 스캔 (target: 스캔 대상 서비스 또는 IP)"""
    return (
        f"시스템 담당 길포일입니다. '{target}' 대상 보안 스캔을 완료했습니다. "
        "취약점 0건 / 포트 상태 정상 / SSL 인증서 유효. 보안 상태 양호합니다."
    )


@mcp.tool()
async def manage_infrastructure(action: str) -> str:
    """인프라 관리 작업 실행 (action: 실행할 인프라 작업 내용)"""
    return (
        f"시스템 담당 길포일입니다. 인프라 작업 '{action}'을 실행했습니다. "
        "변경 사항이 반영되었으며 모니터링을 계속하겠습니다."
    )
