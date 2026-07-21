from siliconvalley.app.ports.input.piper_dunn_coo_use_case import DunnCooUseCase
from siliconvalley.app.use_case.piper_dunn_coo_interactor import DunnCooInteractor


def get_dunn_use_case() -> DunnCooUseCase:
    return DunnCooInteractor()
