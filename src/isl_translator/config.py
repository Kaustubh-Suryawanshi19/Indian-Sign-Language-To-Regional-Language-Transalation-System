"""Central configuration for the ISL translation application."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

PACKAGE_DIR = Path(__file__).resolve().parent
SRC_DIR = PACKAGE_DIR.parent
PROJECT_ROOT = SRC_DIR.parent

load_dotenv(PROJECT_ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    model_path: Path = Path(os.getenv("MODEL_PATH", "models/isl_yolov8m.pt"))
    # Resolve relative paths against the repository, not the caller's current directory.
    def __post_init__(self) -> None:
        path = self.model_path.expanduser()
        if not path.is_absolute():
            path = PROJECT_ROOT / path
        object.__setattr__(self, "model_path", path.resolve())
    camera_index: int = int(os.getenv("CAMERA_INDEX", "0"))
    confidence_threshold: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.60"))
    max_signs: int = int(os.getenv("MAX_SIGNS", "5"))
    analysis_interval: float = float(os.getenv("ANALYSIS_INTERVAL", "1.0"))
    min_votes: int = int(os.getenv("MIN_VOTES", "2"))
    target_fps: float = float(os.getenv("TARGET_FPS", "8"))
    detection_interval: float = float(os.getenv("DETECTION_INTERVAL", "0.20"))
    gemini_api_key: str | None = os.getenv("GEMINI_API_KEY")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    max_translation_chars: int = int(os.getenv("MAX_TRANSLATION_CHARS", "500"))

    def validate(self) -> None:
        if not 0.0 <= self.confidence_threshold <= 1.0:
            raise ValueError("CONFIDENCE_THRESHOLD must be between 0 and 1")
        if self.max_signs < 1:
            raise ValueError("MAX_SIGNS must be >= 1")
        if self.analysis_interval <= 0 or self.detection_interval <= 0:
            raise ValueError("Analysis/detection intervals must be positive")
        if self.target_fps <= 0:
            raise ValueError("TARGET_FPS must be positive")


SETTINGS = Settings()
SETTINGS.validate()

FONT_PATHS = {
    "hi": PROJECT_ROOT / "assets" / "fonts" / "NotoSansDevanagari-Regular.ttf",
    "mr": PROJECT_ROOT / "assets" / "fonts" / "NotoSansDevanagari-Regular.ttf",
    "pa": PROJECT_ROOT / "assets" / "fonts" / "NotoSansGurmukhi-Regular.ttf",
    "ta": PROJECT_ROOT / "assets" / "fonts" / "NotoSansTamil-Regular.ttf",
}

STATIC_IMAGE = PROJECT_ROOT / "web_app" / "static" / "images" / "impact-ai-sign-language-translators-4k.png"
