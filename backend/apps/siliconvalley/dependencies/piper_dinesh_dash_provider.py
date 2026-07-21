from siliconvalley.app.ports.input.piper_dinesh_dash_use_case import DineshDashUseCase
from siliconvalley.app.use_case.piper_dinesh_dash_interactor import DineshDashInteractor


def get_dinesh_use_case() -> DineshDashUseCase:
    return DineshDashInteractor()
