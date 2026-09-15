"""Desktop application for real-time ISL detection and multilingual sentence generation.

Run from the repository root:
    python app.py

Set GEMINI_API_KEY in .env to enable LLM sentence generation. The app has a
local deterministic fallback when no key is configured.
"""
from __future__ import annotations

import sys
import threading
import time

import cv2
import numpy as np
from PyQt5.QtCore import QThread, Qt, pyqtSignal
from PyQt5.QtGui import QFont, QFontDatabase, QImage, QPixmap
from PyQt5.QtWidgets import (
    QApplication, QComboBox, QFrame, QGroupBox, QHBoxLayout, QLabel,
    QMainWindow, QPushButton, QVBoxLayout, QWidget,
)

from src.isl_translator.config import FONT_PATHS, SETTINGS
from src.isl_translator.detector import SignDetector, open_camera
from src.isl_translator.temporal import TemporalSignBuffer
from src.isl_translator.translator import SentenceTranslator
from src.isl_translator.vocabulary import LANGUAGE_NAMES, localize_signs


class GeminiThread(QThread):
    finished_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)

    def __init__(self, translator: SentenceTranslator, signs: list[str], language: str):
        super().__init__()
        self.translator = translator
        self.signs = signs
        self.language = language

    def run(self) -> None:
        try:
            self.finished_signal.emit(self.translator.translate(self.signs, self.language))
        except Exception as exc:
            self.error_signal.emit(str(exc))


class VideoThread(QThread):
    frame_signal = pyqtSignal(np.ndarray)
    signs_signal = pyqtSignal(list)
    error_signal = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        self._stop_event = threading.Event()
        self._language = "en"
        self._language_lock = threading.Lock()
        self._buffer_lock = threading.Lock()
        self.detector = None
        self.buffer = TemporalSignBuffer(
            SETTINGS.analysis_interval, SETTINGS.max_signs, SETTINGS.min_votes
        )

    def set_language(self, language: str) -> None:
        with self._language_lock:
            self._language = language

    def get_language(self) -> str:
        with self._language_lock:
            return self._language

    def clear_history(self) -> None:
        with self._buffer_lock:
            self.buffer.reset()
        self.signs_signal.emit([])

    def stop(self) -> None:
        self._stop_event.set()
        if self.isRunning():
            self.wait(3000)

    def run(self) -> None:
        camera = None
        try:
            self.detector = SignDetector(SETTINGS.model_path, SETTINGS.confidence_threshold)
            camera = open_camera(SETTINGS.camera_index)
            frame_period = 1.0 / SETTINGS.target_fps
            last_detection = 0.0

            while not self._stop_event.is_set():
                started = time.monotonic()
                ok, frame = camera.read()
                if not ok:
                    self.error_signal.emit("Could not read a frame from the webcam.")
                    time.sleep(0.1)
                    continue

                now = time.monotonic()
                if now - last_detection >= SETTINGS.detection_interval:
                    annotated, detections = self.detector.predict(frame)
                    last_detection = now
                    with self._buffer_lock:
                        for detection in detections:
                            self.buffer.add(detection.label, detection.confidence)
                        self.buffer.commit(now)
                        sequence = self.buffer.snapshot()
                    self.frame_signal.emit(annotated)
                    self.signs_signal.emit(sequence)
                else:
                    self.frame_signal.emit(frame)

                elapsed = time.monotonic() - started
                if elapsed < frame_period:
                    time.sleep(frame_period - elapsed)
        except Exception as exc:
            self.error_signal.emit(str(exc))
        finally:
            if camera is not None:
                camera.release()

class MainWindow(QMainWindow):
    COLORS = {
        "primary": "#2A3F54", "secondary": "#1ABB9C", "accent": "#3498DB",
        "background": "#F7F9FC", "text": "#2C3E50", "success": "#27AE60",
        "danger": "#E74C3C",
    }

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("ISL Regional Language Interpreter")
        self.setMinimumSize(1100, 700)
        self.current_lang = "en"
        self.detected_signs: list[str] = []
        self.is_translating = False
        self.translation_thread: GeminiThread | None = None
        self.translator = SentenceTranslator(SETTINGS.gemini_api_key, SETTINGS.gemini_model)
        self._build_ui()

        self.video_thread = VideoThread()
        self.video_thread.frame_signal.connect(self.update_image)
        self.video_thread.signs_signal.connect(self.update_detected_signs)
        self.video_thread.error_signal.connect(self.show_runtime_error)
        self.video_thread.set_language(self.current_lang)
        self.video_thread.start()

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        header = QLabel("Indian Sign Language Interpreter")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet(
            f"background:{self.COLORS['primary']};color:white;font-size:24px;font-weight:bold;padding:18px;border-radius:10px;"
        )
        layout.addWidget(header)

        content = QHBoxLayout()
        content.setSpacing(15)
        layout.addLayout(content, 1)

        video_panel = QFrame()
        video_panel.setStyleSheet(f"background:{self.COLORS['background']};border:2px solid {self.COLORS['primary']};border-radius:10px;")
        video_layout = QVBoxLayout(video_panel)
        self.video_label = QLabel("Starting camera…")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setMinimumSize(760, 500)
        video_layout.addWidget(self.video_label)
        content.addWidget(video_panel, 7)

        control = QFrame()
        control.setStyleSheet("background:white;border:2px solid #2A3F54;border-radius:10px;")
        controls = QVBoxLayout(control)
        controls.setContentsMargins(18, 18, 18, 18)

        self.status = QLabel("● Starting")
        self.status.setStyleSheet(f"color:{self.COLORS['success']};font-weight:bold;font-size:16px;")
        controls.addWidget(self.status)

        group = QGroupBox("Detected signs")
        group_layout = QVBoxLayout(group)
        self.signs_display = QLabel("Waiting for signs…")
        self.signs_display.setAlignment(Qt.AlignCenter)
        self.signs_display.setWordWrap(True)
        self.signs_display.setMinimumHeight(130)
        group_layout.addWidget(self.signs_display)
        controls.addWidget(group)

        settings = QGroupBox("Settings")
        settings_layout = QVBoxLayout(settings)
        self.language_combo = QComboBox()
        for code, name in LANGUAGE_NAMES.items():
            self.language_combo.addItem(name, code)
        self.language_combo.currentIndexChanged.connect(self.change_language)
        settings_layout.addWidget(QLabel("Target language"))
        settings_layout.addWidget(self.language_combo)
        controls.addWidget(settings)

        self.translate_button = QPushButton("Translate Sentence")
        self.translate_button.clicked.connect(self.translate_sentence)
        controls.addWidget(self.translate_button)

        reset_button = QPushButton("Reset Sequence")
        reset_button.clicked.connect(self.reset_sequence)
        controls.addWidget(reset_button)

        exit_button = QPushButton("Exit")
        exit_button.clicked.connect(self.close)
        controls.addWidget(exit_button)
        controls.addStretch(1)
        content.addWidget(control, 3)

        self._load_fonts()

    def _load_fonts(self) -> None:
        self.font_ids = {}
        for code, path in FONT_PATHS.items():
            if path.exists():
                font_id = QFontDatabase.addApplicationFont(str(path))
                if font_id != -1:
                    self.font_ids[code] = font_id

    def change_language(self) -> None:
        self.current_lang = self.language_combo.currentData() or "en"
        self.video_thread.set_language(self.current_lang)
        self.reset_sequence()
        font_id = self.font_ids.get(self.current_lang)
        if font_id is not None:
            families = QFontDatabase.applicationFontFamilies(font_id)
            if families:
                self.signs_display.setFont(QFont(families[0], 16))

    def update_image(self, frame: np.ndarray) -> None:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, channels = rgb.shape
        image = QImage(rgb.data, w, h, channels * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(image).scaled(
            self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.video_label.setPixmap(pixmap)

    def update_detected_signs(self, signs: list[str]) -> None:
        if self.is_translating:
            return
        self.detected_signs = list(signs)
        localized = localize_signs(self.detected_signs, self.current_lang)
        self.signs_display.setText("\n".join(localized) if localized else "Waiting for signs…")
        self.status.setText(f"● Detected: {' → '.join(localized)}" if localized else "● Waiting for signs")

    def translate_sentence(self) -> None:
        if self.is_translating or not self.detected_signs:
            return
        snapshot = list(self.detected_signs)
        self.is_translating = True
        self.translate_button.setEnabled(False)
        self.status.setText("● Generating sentence…")
        self.signs_display.setText("Translating…")
        self.translation_thread = GeminiThread(self.translator, snapshot, self.current_lang)
        self.translation_thread.finished_signal.connect(self.handle_translation_result)
        self.translation_thread.error_signal.connect(self.handle_translation_error)
        self.translation_thread.start()

    def handle_translation_result(self, text: str) -> None:
        self.signs_display.setText(text)
        self.status.setText("● Translation complete")
        self.is_translating = False
        self.translate_button.setEnabled(True)

    def handle_translation_error(self, message: str) -> None:
        self.signs_display.setText(f"Translation unavailable: {message}")
        self.status.setText("● Translation failed")
        self.is_translating = False
        self.translate_button.setEnabled(True)

    def reset_sequence(self) -> None:
        self.video_thread.clear_history()
        self.detected_signs = []
        self.signs_display.setText("Waiting for signs…")

    def show_runtime_error(self, message: str) -> None:
        self.status.setText("● Camera/model error")
        self.video_label.setText(message)
        if not self.isVisible():
            return

    def closeEvent(self, event) -> None:
        self.video_thread.stop()
        if self.translation_thread and self.translation_thread.isRunning():
            self.translation_thread.wait(3000)
        event.accept()


def main() -> int:
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
