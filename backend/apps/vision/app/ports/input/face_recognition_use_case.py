from abc import ABC, abstractmethod

from vision.app.dtos.face_recognition_dto import (
    FaceRecognitionResult,
    FaceRecognizeQuery,
    FaceTrainCommand,
    FaceTrainResult,
)


class IFaceRecognitionUseCase(ABC):
    @abstractmethod
    def train(self, command: FaceTrainCommand) -> FaceTrainResult: ...

    @abstractmethod
    def recognize(self, query: FaceRecognizeQuery) -> FaceRecognitionResult: ...
