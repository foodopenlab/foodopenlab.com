import logging

from ontology.app.dtos.face_recognition_dto import (
    FaceRecognitionResult,
    FaceRecognizeQuery,
    FaceTrainCommand,
    FaceTrainResult,
)
from ontology.app.ports.input.face_recognition_use_case import IFaceRecognitionUseCase
from ontology.app.ports.output.face_dataset_port import IFaceDatasetPort
from ontology.app.ports.output.face_recognizer_port import IFaceRecognizerPort

logger = logging.getLogger(__name__)


class FaceRecognitionInteractor(IFaceRecognitionUseCase):
    """얼굴 인식 오케스트레이터. 데이터셋 포트에서 경로를 받아 인식 포트에 학습/추론을 위임한다.

    ultralytics 를 직접 import하지 않으므로(§12 경계 규칙) 학습 엔진·데이터 소스를
    각각 어댑터 교체만으로 바꿀 수 있다.
    """

    def __init__(self, dataset_port: IFaceDatasetPort, recognizer_port: IFaceRecognizerPort) -> None:
        self._dataset_port = dataset_port
        self._recognizer_port = recognizer_port

    def train(self, command: FaceTrainCommand) -> FaceTrainResult:
        dataset_root = self._dataset_port.get_dataset_root()
        logger.info("[FaceRecognition] train | dataset=%s model=%s epochs=%d", dataset_root, command.base_model, command.epochs)
        return self._recognizer_port.train(dataset_root, command)

    def recognize(self, query: FaceRecognizeQuery) -> FaceRecognitionResult:
        logger.info("[FaceRecognition] recognize | image=%s weights=%s", query.image_path, query.weights_path)
        return self._recognizer_port.recognize(query)
