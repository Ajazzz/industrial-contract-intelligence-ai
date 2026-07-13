from langdetect import detect

# --------------------------------------------------
# Legal / Industrial Business Terms
# These are commonly used in English contracts,
# even if they originate from French or Latin.
# --------------------------------------------------
LEGAL_ENGLISH_TERMS = {

    "force majeure",

    "de facto",

    "per se",

    "bona fide",

    "prima facie",

    "governing law",

    "payment terms",

    "commercial terms",

    "scope of work",

    "liquidated damages",

    "contract value",

    "contract term",

    "termination",

    "renewal",

    "escalation",

    "price variation",

    "invoice",

    "billing",

    "penalty",

    "kpi",

    "sla",

    "cpi",

    "wpi",

    "fuel escalation",

    "diesel escalation",

    "slag",

    "slag handling"
}


def detect_language(text: str) -> str:
    """
    Detect the language of the user's query.

    Rules:
    1. Empty query -> English
    2. Common legal/business terms -> English
    3. Very short queries (<=2 words) -> English
    4. Otherwise use langdetect
    """

    if not text:
        return "en"

    text = text.strip().lower()

    # ------------------------------------------
    # Common legal/business terminology
    # ------------------------------------------
    if text in LEGAL_ENGLISH_TERMS:
        return "en"

    # ------------------------------------------
    # Very short queries are assumed to be English.
    # This avoids incorrect detection such as:
    # "force majeure" -> fr
    # "termination" -> fr
    # "payment terms" -> es
    # ------------------------------------------
    if len(text.split()) <= 2:
        return "en"

    # ------------------------------------------
    # Automatic Language Detection
    # ------------------------------------------
    try:

        lang = detect(text)

        if lang.startswith("fr"):
            return "fr"

        elif lang.startswith("es"):
            return "es"

        else:
            return "en"

    except Exception:

        return "en"