"""Supported vocabulary and deterministic word-level localization."""

LANGUAGE_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "mr": "Marathi",
    "pa": "Punjabi",
    "ta": "Tamil",
}

TRANSLATION_MAP = {
    "en": {
        **{str(i): str(i) for i in (0, 1, 2, 3, 4, 5, 6, 8, 9)},
        "Band Aid": "Band Aid", "Bye": "Bye", "Cough": "Cough", "Eat": "Eat",
        "Home": "Home", "I": "I", "Like": "Like", "Love": "Love",
        "Request": "Request", "Stop": "Stop", "What": "What", "When": "When",
    },
    "hi": {
        **dict(zip([str(i) for i in (0, 1, 2, 3, 4, 5, 6, 8, 9)], "०१२३४५६८९")),
        "Band Aid": "बैंड एड", "Bye": "अलविदा", "Cough": "खांसी", "Eat": "खाना",
        "Home": "घर", "I": "मैं", "Like": "पसंद", "Love": "प्यार", "Request": "निवेदन",
        "Stop": "रुकें", "What": "क्या", "When": "कब",
    },
    "mr": {
        **dict(zip([str(i) for i in (0, 1, 2, 3, 4, 5, 6, 8, 9)], "०१२३४५६८९")),
        "Band Aid": "बँड एड", "Bye": "निरोप", "Cough": "खोकला", "Eat": "खाणे",
        "Home": "घर", "I": "मी", "Like": "आवड", "Love": "प्रेम", "Request": "विनंती",
        "Stop": "थांबा", "What": "काय", "When": "केव्हा",
    },
    "pa": {
        **dict(zip([str(i) for i in (0, 1, 2, 3, 4, 5, 6, 8, 9)], "੦੧੨੩੪੫੬੮੯")),
        "Band Aid": "ਬੈਂਡ ਐਡ", "Bye": "ਅਲਵਿਦਾ", "Cough": "ਖੰਘ", "Eat": "ਖਾਣਾ",
        "Home": "ਘਰ", "I": "ਮੈਂ", "Like": "ਪਸੰਦ", "Love": "ਪਿਆਰ", "Request": "ਬੇਨਤੀ",
        "Stop": "ਰੁਕੋ", "What": "ਕੀ", "When": "ਕਦੋਂ",
    },
    "ta": {
        **dict(zip([str(i) for i in (0, 1, 2, 3, 4, 5, 6, 8, 9)], "௦௧௨௩௪௫௬௮௯")),
        "Band Aid": "கட்டு மருந்து", "Bye": "சென்று வருகிறேன்", "Cough": "இருமல்", "Eat": "சாப்பிடு",
        "Home": "வீடு", "I": "நான்", "Like": "விரும்பு", "Love": "காதல்", "Request": "கோரிக்கை",
        "Stop": "நிறுத்து", "What": "என்ன", "When": "எப்போது",
    },
}

SUPPORTED_CLASSES = tuple(TRANSLATION_MAP["en"].keys())


def localize_signs(signs: list[str], language: str) -> list[str]:
    mapping = TRANSLATION_MAP.get(language, TRANSLATION_MAP["en"])
    return [mapping.get(sign, sign) for sign in signs]


def validate_language(language: str) -> str:
    return language if language in LANGUAGE_NAMES else "en"
