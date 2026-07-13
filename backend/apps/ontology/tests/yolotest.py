"""YOLO hello world: run pretrained YOLOv8n on ultralytics' sample image and show the result."""

from ultralytics import YOLO
from ultralytics.utils import ASSETS

model = YOLO("yolov8n.pt")
results = model(ASSETS / "bus.jpg")

for result in results:
    result.show()
    result.save(filename="yolo_hello_world_result.jpg")
