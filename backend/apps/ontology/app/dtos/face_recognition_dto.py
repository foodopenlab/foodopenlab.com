from dataclasses import dataclass, field


@dataclass
class FaceTrainCommand:
    base_model: str = "yolo11n-cls.pt"
    epochs: int = 30
    batch: int = 16
    imgsz: int = 224
    device: str = "0"  # GPU 인덱스("0") 또는 "cpu"


@dataclass
class FaceTrainResult:
    best_weights_path: str
    epochs_completed: int
    save_dir: str
    class_names: list[str] = field(default_factory=list)


@dataclass
class FaceRecognizeQuery:
    image_path: str
    weights_path: str
    device: str = "0"
    top_k: int = 3


@dataclass
class FacePrediction:
    label: str
    confidence: float


@dataclass
class FaceRecognitionResult:
    image_path: str
    top: FacePrediction
    candidates: list[FacePrediction] = field(default_factory=list)
