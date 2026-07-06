from langdetect import detect

def detect_language(text):

    try:

        lang = detect(text)

        if lang.startswith("fr"):
            return "fr"

        elif lang.startswith("es"):
            return "es"

        else:
            return "en"

    except:
        return "en"