from fastapi import Depends

from mfds_user.adapter.outbound.external_api.regulation_api_adapter import RegulationApiAdapter
from mfds_user.app.ports.input.regulation_use_case import RegulationUseCase
from mfds_user.app.use_cases.regulation_interactor import RegulationInteractor


def get_regulation_api_adapter() -> RegulationApiAdapter:
    return RegulationApiAdapter()


def get_regulation_use_case(
    regulation_api_adapter: RegulationApiAdapter = Depends(get_regulation_api_adapter),
) -> RegulationUseCase:
    return RegulationInteractor(regulation_api_adapter=regulation_api_adapter)
