"""Real-time camera service shared by the Flask application."""
from __future__ import annotations

import threading
import time
from dataclasses import dataclass

import cv2
import numpy as np

from .config import SETTINGS
from .detector import SignDetector, open_camera
from .temporal import TemporalSignBuffer


@dataclass
class ServiceSnapshot:
    active: bool
    sequence: list[str]
    frame: np.ndarray | None
    error: str | None


class DetectionService:
    def __init__(self) -> None:
        self.detector = None
        self.buffer = TemporalSignBuffer(SETTINGS.analysis_interval, SETTINGS.max_signs, SETTINGS.min_votes)
        self.lock = threading.RLock()
        self._stop = threading.Event()
        self._active = False
        self._thread: threading.Thread | None = None
        self._camera = None
        self._frame: np.ndarray | None = None
        self._error: str | None = None
        self._last_detection = 0.0

    def start(self) -> None:
        with self.lock:
            if self._active:
                return
            if self.detector is None:
                self.detector = SignDetector(SETTINGS.model_path, SETTINGS.confidence_threshold)
            self._active = True
            self._error = None
            self.buffer.reset()
            self._stop.clear()
            self._thread = threading.Thread(target=self._run, name="isl-camera", daemon=True)
            self._thread.start()

    def stop(self, clear: bool = True) -> None:
        with self.lock:
            self._active = False
            if clear:
                self.buffer.reset()
        self._stop.set()
        if self._camera is not None:
            self._camera.release()
            self._camera = None
        thread = self._thread
        if thread and thread.is_alive() and thread is not threading.current_thread():
            thread.join(timeout=2.0)

    def reset(self) -> None:
        with self.lock:
            self.buffer.reset()
            self._error = None

    def snapshot(self) -> ServiceSnapshot:
        with self.lock:
            return ServiceSnapshot(
                active=self._active,
                sequence=self.buffer.snapshot(),
                frame=self._frame.copy() if self._frame is not None else None,
                error=self._error,
            )

    def _run(self) -> None:
        try:
            self._camera = open_camera(SETTINGS.camera_index)
            frame_period = 1.0 / SETTINGS.target_fps
            while not self._stop.is_set():
                started = time.monotonic()
                ok, frame = self._camera.read()
                if not ok:
                    self._set_error("Camera frame could not be read")
                    time.sleep(0.1)
                    continue

                now = time.monotonic()
                if now - self._last_detection >= SETTINGS.detection_interval:
                    annotated, detections = self.detector.predict(frame)
                    self._last_detection = now
                    with self.lock:
                        for detection in detections:
                            self.buffer.add(detection.label, detection.confidence)
                        self.buffer.commit(now)
                        self._frame = annotated
                else:
                    with self.lock:
                        if self._frame is None:
                            self._frame = frame

                elapsed = time.monotonic() - started
                if elapsed < frame_period:
                    time.sleep(frame_period - elapsed)
        except Exception as exc:
            self._set_error(str(exc))
        finally:
            if self._camera is not None:
                self._camera.release()
                self._camera = None

    def _set_error(self, message: str) -> None:
        with self.lock:
            self._error = message
            self._active = False
