from siliconvalley.app.ports.input.piper_gilfoyle_sys_use_case import GilfoyleSysUseCase
from siliconvalley.app.use_case.piper_gilfoyle_sys_interactor import GilfoyleSysInteractor


def get_gilfoyle_use_case() -> GilfoyleSysUseCase:
    return GilfoyleSysInteractor()
