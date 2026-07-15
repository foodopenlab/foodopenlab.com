from fastapi import APIRouter, Depends, HTTPException, Request, status

from ontology.adapter.inbound.api.schemas.gateway_schema import GatewayAskRequest, GatewayAskResponse
from ontology.app.dtos.gateway_dto import GatewayQuery
from ontology.app.ports.input.gateway_use_case import IGatewayUseCase
from ontology.dependencies.gateway_provider import get_gateway_use_case
from ontology.dependencies.rate_limit import enforce_rate_limit

router = APIRouter(prefix="/gateway", tags=["gateway"])


@router.get("/myself")
async def introduce_myself() -> dict:
    return {"id": 0, "name": "gateway"}


@router.post("/ask", response_model=GatewayAskResponse, dependencies=[Depends(enforce_rate_limit)])
async def ask(
    body: GatewayAskRequest,
    request: Request,
    use_case: IGatewayUseCase = Depends(get_gateway_use_case),
) -> GatewayAskResponse:
    client_ip = request.client.host if request.client else None
    try:
        result = await use_case.ask(GatewayQuery(question=body.question, client_ip=client_ip))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return GatewayAskResponse(
        answer=result.answer,
        destination=result.destination,
        blocked=result.blocked,
    )
