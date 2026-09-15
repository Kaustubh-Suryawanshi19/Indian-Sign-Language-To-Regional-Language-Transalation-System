"""Flask web application for the local ISL interpreter.

Important: this web demo intentionally uses the camera attached to the machine
running Flask. A production remote deployment should use browser camera capture
(WebRTC/WebSocket) instead of cv2.VideoCapture(0) on the server.
"""
from __future__ import annotations

import logging
import sys
import threading
import time
from pathlib import Path

from flask import Flask, Response, jsonify, render_template, request
from flask_cors import CORS
import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.isl_translator.config import SETTINGS, STATIC_IMAGE  # noqa: E402
from src.isl_translator.service import DetectionService  # noqa: E402
from src.isl_translator.translator import SentenceTranslator  # noqa: E402
from src.isl_translator.vocabulary import LANGUAGE_NAMES, localize_signs, validate_language  # noqa: E402


logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("isl-web")

app = Flask(__name__, template_folder=str(Path(__file__).parent / "templates"), static_folder=str(Path(__file__).parent / "static"))
app.config.update(MAX_CONTENT_LENGTH=16 * 1024)
CORS(app, resources={r"/api/*": {"origins": ["http://127.0.0.1:5000", "http://localhost:5000"]}})

service = DetectionService()
translator = SentenceTranslator(SETTINGS.gemini_api_key, SETTINGS.gemini_model, SETTINGS.max_translation_chars)
translation_lock = threading.Lock()


def placeholder_frame() -> np.ndarray:
    if STATIC_IMAGE.exists():
        image = cv2.imread(str(STATIC_IMAGE))
        if image is not None:
            return image
    image = np.zeros((480, 800, 3), dtype=np.uint8)
    cv2.putText(image, "Camera inactive", (45, 245), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
    return image


def frame_stream():
    while True:
        snapshot = service.snapshot()
        frame = snapshot.frame if snapshot.frame is not None else placeholder_frame()
        ok, encoded = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
        if not ok:
            time.sleep(0.05)
            continue
        yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + encoded.tobytes() + b"\r\n"
        time.sleep(0.03)


@app.get("/health")
def health():
    return jsonify({
        "status": "ok",
        "model_exists": SETTINGS.model_path.exists(),
        "gemini_available": translator.available,
        "camera_active": service.snapshot().active,
    })


@app.post("/api/toggle_detection")
def toggle_detection():
    try:
        snapshot = service.snapshot()
        if snapshot.active:
            service.stop()
        else:
            service.start()
        current = service.snapshot()
        return jsonify({"status": "success", "detection_active": current.active})
    except Exception as exc:
        logger.exception("Unable to toggle detection")
        return jsonify({"error": "Unable to change detection state"}), 500


# Backward-compatible endpoint used by the existing frontend.
@app.post("/toggle_detection")
def toggle_detection_legacy():
    return toggle_detection()


@app.get("/video_feed")
def video_feed():
    return Response(frame_stream(), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.get("/api/process")
def process_api():
    snapshot = service.snapshot()
    return jsonify({
        "status": "success",
        "sequence": snapshot.sequence,
        "detection_active": snapshot.active,
        "error": snapshot.error,
    })


@app.get("/process")
def process_legacy():
    return process_api()


def _validate_sign_payload(data):
    if not isinstance(data, dict):
        raise ValueError("JSON body must be an object")
    signs = data.get("signs")
    language = validate_language(str(data.get("lang", "en")))
    if not isinstance(signs, list):
        raise ValueError("signs must be a list")
    if not 1 <= len(signs) <= SETTINGS.max_signs:
        raise ValueError(f"signs must contain 1 to {SETTINGS.max_signs} items")
    if not all(isinstance(sign, str) for sign in signs):
        raise ValueError("Every sign must be a string")
    return signs, language


@app.post("/api/translate")
def translate_api():
    try:
        signs, language = _validate_sign_payload(request.get_json(silent=True))
        # Serialize LLM requests to avoid overlapping quota-consuming calls in this local demo.
        with translation_lock:
            translation = translator.translate(signs, language)
        return jsonify({
            "status": "success",
            "translation": translation,
            "language": LANGUAGE_NAMES[language],
            "localized_tokens": localize_signs(signs, language),
            "method": "gemini" if translator.available else "deterministic-fallback",
        })
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception:
        logger.exception("Translation failed")
        return jsonify({"error": "Translation failed"}), 502


@app.post("/translate")
def translate_legacy():
    return translate_api()


@app.post("/api/reset")
def reset_api():
    service.reset()
    return jsonify({"status": "reset", "message": "Detection history cleared"})


@app.post("/reset")
def reset_legacy():
    return reset_api()


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/core_app")
def core_app():
    return render_template("core_app.html")


@app.get("/yolo")
def yolo():
    return render_template("yolo.html")


@app.get("/team")
def team():
    return render_template("team.html")


@app.get("/llm")
def llm():
    return render_template("llm.html")


@app.get("/api")
def api_docs():
    return render_template("api.html")


@app.errorhandler(404)
def not_found(_error):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(_error):
    return render_template("500.html"), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False, threaded=True)
