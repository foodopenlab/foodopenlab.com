from siliconvalley.app.ports.input.piper_bighetti_hr_use_case import BighettiHrUseCase
from siliconvalley.app.use_case.piper_bighetti_hr_interactor import BighettiHrInteractor


def get_bighetti_use_case() -> BighettiHrUseCase:
    return BighettiHrInteractor()
