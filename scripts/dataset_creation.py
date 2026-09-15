"""Simple webcam dataset collector.

Images are written under datasets/raw/<class-name>/ and are intentionally
separate from YOLO labels. Annotate the captured images with your chosen
annotation tool before training.
"""
from __future__ import annotations

import re
from pathlib import Path

import cv2

ROOT = Path(__file__).resolve().parent
OUTPUT_ROOT = ROOT / "datasets" / "raw"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}


def safe_name(name: str) -> str:
    value = re.sub(r"[^A-Za-z0-9 _-]+", "", name).strip()
    value = re.sub(r"\s+", "-", value)
    if not value:
        raise ValueError("Class name must contain at least one letter or number")
    return value


def capture_class(class_name: str, count: int = 100, camera_index: int = 0) -> None:
    class_dir = OUTPUT_ROOT / safe_name(class_name)
    class_dir.mkdir(parents=True, exist_ok=True)
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open camera index {camera_index}")

    print("Press SPACE to capture, Q to stop.")
    saved = len(list(class_dir.glob("*.jpg")))
    try:
        while saved < count:
            ok, frame = cap.read()
            if not ok:
                continue
            cv2.putText(frame, f"{class_name} | {saved}/{count}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow("ISL Dataset Collector", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            if key == 32:
                path = class_dir / f"{safe_name(class_name)}_{saved + 1:05d}.jpg"
                if cv2.imwrite(str(path), frame):
                    saved += 1
                    print(f"Saved {path}")
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    name = input("Gesture/class name: ").strip()
    amount = int(input("Images to capture [100]: ") or "100")
    capture_class(name, amount)
