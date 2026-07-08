from fastapi import Depends

from mfds_user.adapter.outbound.supplier.supplier_public_api_adapter import SupplierPublicApiAdapter
from mfds_user.app.ports.input.supplier_use_case import SupplierUseCase
from mfds_user.app.ports.output.enforcement_repository import EnforcementRepositoryPort
from mfds_user.app.ports.output.haccp_repository import HaccpRepositoryPort
from mfds_user.app.ports.output.recall_repository import RecallRepositoryPort
from mfds_user.app.ports.output.supplier_ports import SupplierPublicApiPort
from mfds_user.app.use_cases.supplier_interactor import SupplierInteractor
from mfds_user.dependencies.enforcement import get_enforcement_repository
from mfds_user.dependencies.haccp import get_haccp_repository
from mfds_user.dependencies.recall import get_recall_repository


def get_supplier_public_api_adapter() -> SupplierPublicApiPort:
    return SupplierPublicApiAdapter()


def get_supplier_use_case(
    recall_repository: RecallRepositoryPort = Depends(get_recall_repository),
    enforcement_repository: EnforcementRepositoryPort = Depends(get_enforcement_repository),
    haccp_repository: HaccpRepositoryPort = Depends(get_haccp_repository),
    supplier_public_api: SupplierPublicApiPort = Depends(get_supplier_public_api_adapter),
) -> SupplierUseCase:
    return SupplierInteractor(
        recall_repository=recall_repository,
        enforcement_repository=enforcement_repository,
        haccp_repository=haccp_repository,
        supplier_public_api=supplier_public_api,
    )
