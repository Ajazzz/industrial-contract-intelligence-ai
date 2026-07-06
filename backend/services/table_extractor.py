import pdfplumber

# ─────────────────────────────────────────────
# EXTRACT TABLES FROM PDF
# ─────────────────────────────────────────────
def extract_tables_from_pdf(pdf_path):

    extracted_tables = []

    with pdfplumber.open(pdf_path) as pdf:

        for page_num, page in enumerate(pdf.pages):

            tables = page.extract_tables()

            if not tables:
                continue

            for table_idx, table in enumerate(tables):

                if not table:
                    continue

                headers = table[0]

                rows = table[1:]

                structured_rows = []

                for row in rows:

                    if not row:
                        continue

                    row_data = {}

                    for h, v in zip(headers, row):

                        if not h:
                            continue

                        row_data[
                            str(h).strip()
                        ] = (
                            str(v).strip()
                            if v else ""
                        )

                    structured_rows.append(
                        row_data
                    )

                extracted_tables.append({

                    "page": page_num + 1,

                    "table_index": table_idx,

                    "headers": headers,

                    "rows": structured_rows
                })

    return extracted_tables