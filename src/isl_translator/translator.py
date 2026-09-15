"""Controlled multilingual sentence generation using Google's current GenAI SDK."""
from __future__ import annotations

import re
from functools import lru_cache

from .vocabulary import LANGUAGE_NAMES, SUPPORTED_CLASSES, localize_signs, validate_language


class TranslationError(RuntimeError):
    pass


@lru_cache(maxsize=64)
def _fallback_sentence(sequence_key: tuple[str, ...], language: str) -> str:
    words = localize_signs(list(sequence_key), language)
    if not words:
        return "No signs detected."
    if language == "en":
        patterns = {
            ("What", "Eat"): "What should I eat?",
            ("When", "Eat"): "When will we eat?",
            ("What", "Love"): "What do you love?",
            ("I", "Like", "Home"): "I like home.",
            ("I", "Love", "Home"): "I love home.",
            ("I", "Home", "Bye"): "I am going home, bye.",
            ("I", "Request", "Stop"): "I request you to stop.",
        }
        return patterns.get(sequence_key, " ".join(words).strip().capitalize() + ".")
    return " ".join(words).strip()


def _clean_response(text: str, language: str, max_chars: int = 500) -> str:
    text = re.sub(r"\s+", " ", text or "").strip().strip('"')
    if not text:
        raise TranslationError("The language model returned an empty response")
    if len(text) > max_chars:
        text = text[:max_chars].rsplit(" ", 1)[0] + "…"
    return text


class SentenceTranslator:
    def __init__(self, api_key: str | None, model_name: str = "gemini-2.5-flash", max_chars: int = 500) -> None:
        self.api_key = api_key
        self.model_name = model_name
        self.max_chars = max(50, int(max_chars))
        self._client = None
        if api_key:
            try:
                from google import genai
                self._client = genai.Client(api_key=api_key)
            except Exception as exc:
                raise TranslationError(f"Google GenAI SDK initialization failed: {exc}") from exc

    @property
    def available(self) -> bool:
        return self._client is not None

    def translate(self, signs: list[str], language: str) -> str:
        language = validate_language(language)
        cleaned = self._normalize_sequence(signs)
        if not cleaned:
            return "No signs detected."
        if not self._client:
            return _fallback_sentence(tuple(cleaned), language)

        localized = localize_signs(cleaned, language)
        prompt = self._build_prompt(cleaned, localized, language)
        try:
            response = self._client.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )
            return _clean_response(response.text, language, self.max_chars)
        except Exception as exc:
            # The app remains useful even when the network/LLM is unavailable.
            fallback = _fallback_sentence(tuple(cleaned), language)
            if fallback:
                return fallback
            raise TranslationError(f"Translation request failed: {exc}") from exc

    @staticmethod
    def _normalize_sequence(signs: list[str]) -> list[str]:
        allowed = set(SUPPORTED_CLASSES)
        result: list[str] = []
        for sign in signs[:5]:
            if not isinstance(sign, str):
                continue
            sign = sign.strip()
            if sign in allowed and (not result or result[-1] != sign):
                result.append(sign)
        return result

    def _build_prompt(self, signs: list[str], localized: list[str], language: str) -> str:
        language_name = LANGUAGE_NAMES[language]
        return f"""You are a constrained sentence-realization engine for an Indian Sign Language prototype.

Recognized sign sequence (do not add new semantic concepts): {signs}
Localized sign tokens in {language_name}: {localized}

Rules:
1. Preserve the meaning and order of the recognized signs as much as the target language grammar allows.
2. Do not invent people, places, events, causes, medical advice, or facts that are not represented by the signs.
3. Prefer a short natural sentence. If the sequence is fragmentary, produce a concise natural fragment rather than guessing.
4. Output only {language_name} text in its native script where applicable; no explanation, quotation marks, labels, or transliteration.
5. The recognized vocabulary is limited. Do not introduce a new semantic word merely to make the sentence sound richer.

Return exactly one sentence or short phrase."""
