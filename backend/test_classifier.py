import os

from backend.services.document_classifier import (
    classify_document
)

# ─────────────────────────────────────────────
# TEST PDF
# ─────────────────────────────────────────────
BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DATA_DIR = os.path.join(
    BASE_DIR,
    "rag",
    "data"
)

pdf_files = [
    f for f in os.listdir(DATA_DIR)
    if f.lower().endswith(".pdf")
]

print(f"\nFound {len(pdf_files)} PDFs\n")

for pdf_file in pdf_files:

    pdf_path = os.path.join(
        DATA_DIR,
        pdf_file
    )

    print("=" * 60)
    print(f"PDF: {pdf_file}")
    print("=" * 60)

    results = classify_document(
        pdf_path
    )

    for r in results:

        print(
            f"Page {r['page']} | "
            f"Scanned: {r['scanned']} | "
            f"Type: {r['page_type']}"
        )