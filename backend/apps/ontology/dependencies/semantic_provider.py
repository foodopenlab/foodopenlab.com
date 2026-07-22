from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from matrix.grid_oracle_database_manager import get_db

from ontology.adapter.outbound.llm.exaone_intent_classifier_adapter import ExaoneIntentClassifierAdapter
from ontology.adapter.outbound.llm.gemini_adapter import GeminiAdapter
from ontology.adapter.outbound.rag.law_rag_adapter import LawRagAdapter
from ontology.adapter.outbound.search.law_search_adapter import LawSearchAdapter
from ontology.adapter.outbound.repositories.semantic_audit_log_repository import SemanticAuditLogRepository
from ontology.app.ports.input.semantic_use_case import ISemanticUseCase
from ontology.app.ports.output.audit_log_port import IAuditLogPort
from ontology.app.ports.output.gemini_port import IGeminiPort
from ontology.app.ports.output.intent_classifier_port import IIntentClassifierPort
from ontology.app.ports.output.rag_port import IRagPort
from ontology.app.ports.output.search_port import ISearchPort
from ontology.app.use_cases.semantic_interactor import SemanticInteractor


def get_intent_classifier() -> IIntentClassifierPort:
    return ExaoneIntentClassifierAdapter()


def get_gemini_port() -> IGeminiPort:
    return GeminiAdapter()


def get_rag_port(db: AsyncSession = Depends(get_db)) -> IRagPort:
    return LawRagAdapter(db)


def get_search_port(db: AsyncSession = Depends(get_db)) -> ISearchPort:
    return LawSearchAdapter(db)


def get_audit_log_port(db: AsyncSession = Depends(get_db)) -> IAuditLogPort:
    return SemanticAuditLogRepository(db)


def get_semantic_use_case(
    classifier: IIntentClassifierPort = Depends(get_intent_classifier),
    gemini: IGeminiPort = Depends(get_gemini_port),
    rag: IRagPort = Depends(get_rag_port),
    search: ISearchPort = Depends(get_search_port),
    audit_log: IAuditLogPort = Depends(get_audit_log_port),
) -> ISemanticUseCase:
    return SemanticInteractor(
        classifier=classifier,
        gemini=gemini,
        rag=rag,
        search=search,
        audit_log=audit_log,
    )
