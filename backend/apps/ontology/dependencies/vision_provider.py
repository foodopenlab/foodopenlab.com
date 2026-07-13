from fastapi import Depends

from ontology.adapter.outbound.repositories.vision_repository import VisionRepository
from ontology.app.ports.input.vision_use_case import IVisionUseCase
from ontology.app.ports.output.vision_port import IVisionPort
from ontology.app.use_cases.vision_interactor import VisionInteractor


def get_vision_port() -> IVisionPort:
    return VisionRepository()


def get_vision_use_case(
    port: IVisionPort = Depends(get_vision_port),
) -> IVisionUseCase:
    return VisionInteractor(port=port)
