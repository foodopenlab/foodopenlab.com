from siliconvalley.app.ports.input.piper_hendricks_ceo_use_case import HendricksCeoUseCase
from siliconvalley.app.use_case.piper_hendricks_ceo_interactor import HendricksCeoInteractor


def get_hendricks_use_case() -> HendricksCeoUseCase:
    return HendricksCeoInteractor()
