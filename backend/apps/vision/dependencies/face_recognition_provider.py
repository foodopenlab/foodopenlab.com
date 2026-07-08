from vision.adapter.outbound.detectors.ultralytics_face_recognizer_adapter import UltralyticsFaceRecognizerAdapter
from vision.adapter.outbound.repositories.local_yolo_face_dataset_repository import LocalYoloFaceDatasetRepository
from vision.app.ports.input.face_recognition_use_case import IFaceRecognitionUseCase
from vision.app.ports.output.face_dataset_port import IFaceDatasetPort
from vision.app.ports.output.face_recognizer_port import IFaceRecognizerPort
from vision.app.use_cases.face_recognition_interactor import FaceRecognitionInteractor


def get_face_dataset_port() -> IFaceDatasetPort:
    return LocalYoloFaceDatasetRepository()


def get_face_recognizer_port() -> IFaceRecognizerPort:
    return UltralyticsFaceRecognizerAdapter()


def get_face_recognition_use_case() -> IFaceRecognitionUseCase:
    return FaceRecognitionInteractor(
        dataset_port=get_face_dataset_port(),
        recognizer_port=get_face_recognizer_port(),
    )
