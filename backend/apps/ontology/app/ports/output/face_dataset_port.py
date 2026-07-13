from abc import ABC, abstractmethod


class IFaceDatasetPort(ABC):
    @abstractmethod
    def get_dataset_root(self) -> str:
        """YOLO 분류 학습용 데이터셋 루트 경로를 반환한다.

        루트 하위에 train/ · val/ 이 있고, 각 split 안에 클래스(인물)별 폴더가 있어야 한다.
        데이터가 로컬/S3/DB 어디서 오든 이 포트만 구현하면 학습 로직은 바뀌지 않는다.
        """
        ...
