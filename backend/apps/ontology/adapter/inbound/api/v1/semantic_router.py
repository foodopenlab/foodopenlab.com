from fastapi import APIRouter, Depends, HTTPException, Request, status

from ontology.adapter.inbound.api.schemas.semantic_schema import SemanticAskRequest, SemanticAskResponse
from ontology.app.dtos.semantic_dto import SemanticQuery
from ontology.app.ports.input.semantic_use_case import ISemanticUseCase
from ontology.dependencies.semantic_provider import get_semantic_use_case
from ontology.dependencies.rate_limit import enforce_rate_limit

router = APIRouter(prefix="/semantic", tags=["semantic"])


@router.get("/myself")
async def introduce_myself() -> dict:
    return {"id": 0, "name": "semantic"}


@router.post("/ask", response_model=SemanticAskResponse, dependencies=[Depends(enforce_rate_limit)])
async def ask(
    body: SemanticAskRequest,
    request: Request,
    use_case: ISemanticUseCase = Depends(get_semantic_use_case),
) -> SemanticAskResponse:
    client_ip = request.client.host if request.client else None
    try:
        result = await use_case.ask(SemanticQuery(question=body.question, client_ip=client_ip))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return SemanticAskResponse(
        answer=result.answer,
        destination=result.destination,
        blocked=result.blocked,
    )
