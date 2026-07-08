from mcp.server.fastmcp import FastMCP

mcp = FastMCP("파이퍼 디네시 대시")


@mcp.tool()
async def introduce_myself() -> str:
    """대시보드 담당 자기소개"""
    return "안녕하세요, 파이퍼 디네시입니다. 대시보드 담당입니다."


@mcp.tool()
async def get_dashboard_status() -> str:
    """대시보드 현황 조회"""
    return (
        "대시보드 담당 디네시입니다. "
        "현재 실시간 사용자 수: 12,847명 / 오늘 요청 처리량: 4.2M / 오류율: 0.03%입니다."
    )


@mcp.tool()
async def visualize_kpi(metric: str) -> str:
    """KPI 시각화 (metric: 조회할 지표명)"""
    return (
        f"대시보드 담당 디네시입니다. "
        f"'{metric}' 지표를 시각화했습니다. 차트 데이터가 준비되었으니 대시보드에서 확인하세요."
    )


@mcp.tool()
async def run_data_analysis(dataset: str) -> str:
    """데이터 분석 실행 (dataset: 분석 대상 데이터셋명)"""
    return (
        f"대시보드 담당 디네시입니다. "
        f"'{dataset}' 데이터셋 분석을 완료했습니다. 트렌드 리포트와 이상값 탐지 결과를 제공합니다."
    )
