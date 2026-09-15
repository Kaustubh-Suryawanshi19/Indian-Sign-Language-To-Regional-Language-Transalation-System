"""YOLO inference wrapper with confidence filtering and reusable frame processing."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
from ultralytics import YOLO


@dataclass(frozen=True)
class Detection:
    label: str
    confidence: float
    box: tuple[int, int, int, int]


class SignDetector:
    def __init__(self, model_path: str | Path, confidence_threshold: float = 0.60) -> None:
        path = Path(model_path).expanduser().resolve()
        if not path.exists():
            raise FileNotFoundError(f"YOLO weights not found: {path}")
        self.model = YOLO(str(path))
        self.confidence_threshold = confidence_threshold

    @property
    def names(self):
        return self.model.names

    def predict(self, frame: np.ndarray) -> tuple[np.ndarray, list[Detection]]:
        results = self.model.predict(frame, conf=self.confidence_threshold, verbose=False)
        result = results[0]
        detections: list[Detection] = []
        boxes = result.boxes
        if boxes is not None:
            xyxy = boxes.xyxy.detach().cpu().numpy()
            classes = boxes.cls.detach().cpu().numpy().astype(int)
            confidences = boxes.conf.detach().cpu().numpy()
            for box, cls_id, confidence in zip(xyxy, classes, confidences):
                label = self.model.names[int(cls_id)]
                detections.append(
                    Detection(label, float(confidence), tuple(map(int, box)))
                )
        annotated = result.plot()
        return annotated, detections


def open_camera(index: int) -> cv2.VideoCapture:
    cap = cv2.VideoCapture(index)
    if not cap.isOpened():
        cap.release()
        raise RuntimeError(f"Could not open camera index {index}")
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    return cap
