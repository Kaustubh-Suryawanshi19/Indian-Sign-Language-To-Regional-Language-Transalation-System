import unittest

from src.isl_translator.temporal import TemporalSignBuffer
from src.isl_translator.translator import SentenceTranslator
from src.isl_translator.vocabulary import localize_signs, validate_language


class VocabularyTests(unittest.TestCase):
    def test_localization(self):
        self.assertEqual(localize_signs(["I", "Home"], "mr"), ["मी", "घर"])

    def test_unknown_language_defaults_to_english(self):
        self.assertEqual(validate_language("xx"), "en")


class TemporalTests(unittest.TestCase):
    def test_confidence_weighted_vote(self):
        buffer = TemporalSignBuffer(interval=0, max_signs=5, min_votes=2)
        buffer.add("Home", 0.9)
        buffer.add("Home", 0.8)
        buffer.add("Cough", 0.99)
        buffer.commit()
        self.assertEqual(buffer.snapshot(), ["Home"])

    def test_duplicate_commits_are_suppressed(self):
        buffer = TemporalSignBuffer(interval=0, max_signs=5, min_votes=1)
        buffer.add("Home", 1.0)
        buffer.commit()
        buffer.add("Home", 1.0)
        buffer.commit()
        self.assertEqual(buffer.snapshot(), ["Home"])


class TranslatorTests(unittest.TestCase):
    def test_deterministic_fallback(self):
        translator = SentenceTranslator(None)
        self.assertEqual(translator.translate(["I", "Love", "Home"], "en"), "I love home.")

    def test_empty_sequence(self):
        translator = SentenceTranslator(None)
        self.assertEqual(translator.translate([], "en"), "No signs detected.")


if __name__ == "__main__":
    unittest.main()
