import fitz
import pytesseract

from PIL import Image

# ─────────────────────────────────────────────
# CHECK IF PAGE IS SCANNED
# ─────────────────────────────────────────────
def is_scanned_page(page):

    text = page.get_text().strip()

    # If very little extractable text
    # likely scanned image
    return len(text) < 50

# ─────────────────────────────────────────────
# DETECT TABLE-HEAVY PAGE
# ─────────────────────────────────────────────
def is_table_heavy(text):

    indicators = [
        "|",
        "Table",
        "Annexure",
        "Equipment/System",
        "Details",
        "Qty",
        "Amount",
        "Rate",
        "Total"
    ]

    matches = sum(
        1 for i in indicators
        if i.lower() in text.lower()
    )

    return matches >= 2

# ─────────────────────────────────────────────
# OCR PAGE
# ─────────────────────────────────────────────
def extract_ocr_text(page):

    pix = page.get_pixmap()

    img = Image.frombytes(
        "RGB",
        [pix.width, pix.height],
        pix.samples
    )

    text = pytesseract.image_to_string(img)

    return text

# ─────────────────────────────────────────────
# CLASSIFY PAGE
# ─────────────────────────────────────────────
def classify_page(page):

    scanned = is_scanned_page(page)

    if scanned:

        text = extract_ocr_text(page)

    else:

        text = page.get_text()

    page_type = "general"

    if is_table_heavy(text):

        page_type = "table_heavy"

    elif "scope of work" in text.lower():

        page_type = "scope_of_work"

    elif "eligibility" in text.lower():

        page_type = "eligibility"

    elif "kpi" in text.lower():

        page_type = "kpi_section"

    elif "annexure" in text.lower():

        page_type = "annexure"

    return {

        "scanned": scanned,

        "page_type": page_type,

        "text": text
    }

# ─────────────────────────────────────────────
# CLASSIFY ENTIRE DOCUMENT
# ─────────────────────────────────────────────
def classify_document(pdf_path):

    doc = fitz.open(pdf_path)

    results = []

    for page_num, page in enumerate(doc):

        classification = classify_page(page)

        classification["page"] = page_num + 1

        results.append(classification)

    return results