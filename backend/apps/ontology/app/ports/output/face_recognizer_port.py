from abc import ABC, abstractmethod

from ontology.app.dtos.face_recognition_dto import (
    FaceRecognitionResult,
    FaceRecognizeQuery,
    FaceTrainCommand,
    FaceTrainResult,
)


class IFaceRecognizerPort(ABC):
    """YOLO 엔진(학습·추론) Driven Port. 구현체(ultralytics 등)를 교체해도 UseCase는 불변."""

    @abstractmethod
    def train(self, dataset_root: str, command: FaceTrainCommand) -> FaceTrainResult:
        """데이터셋 루트로 얼굴 인식 모델을 파인튜닝하고 결과를 반환한다."""
        ...

    @abstractmethod
    def recognize(self, query: FaceRecognizeQuery) -> FaceRecognitionResult:
        """학습된 가중치로 이미지 속 얼굴이 누구인지 추론한다."""
        ...
