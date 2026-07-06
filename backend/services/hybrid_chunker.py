import re

# ─────────────────────────────────────────────
# RECURSIVE CHUNKING
# ─────────────────────────────────────────────
def recursive_chunk(
    text,
    chunk_size=350,
    overlap=60
):

    words = text.split()

    chunks = []

    start = 0

    while start < len(words):

        end = start + chunk_size

        chunk = " ".join(
            words[start:end]
        )

        chunks.append(chunk)

        start += (
            chunk_size - overlap
        )

    return chunks

# ─────────────────────────────────────────────
# CLAUSE CHUNKER
# ─────────────────────────────────────────────
def chunk_clause_page(
    text,
    page_num,
    page_type
):

    clauses = re.split(
        r"\n\s*\d+\.",
        text
    )

    results = []

    for clause in clauses:

        clause = clause.strip()

        if not clause:
            continue

        results.append({

            "chunk_type": "clause",

            "page_type": page_type,

            "page": page_num,

            "text":
                f"SECTION TYPE: {page_type}\n\n"
                f"{clause}"
        })

    return results

# ─────────────────────────────────────────────
# TABLE CHUNKER
# ─────────────────────────────────────────────
def chunk_table_page(
    text,
    page_num,
    page_type
):

    chunks = recursive_chunk(
        text,
        chunk_size=250,
        overlap=40
    )

    results = []

    for c in chunks:

        results.append({

            "chunk_type": "table",

            "page_type": page_type,

            "page": page_num,

            "text":
                f"TABLE SECTION\n"
                f"PAGE TYPE: {page_type}\n\n"
                f"{c}"
        })

    return results

# ─────────────────────────────────────────────
# SEMANTIC CHUNKER
# ─────────────────────────────────────────────
def chunk_semantic_page(
    text,
    page_num,
    page_type
):

    chunks = recursive_chunk(
        text,
        chunk_size=400,
        overlap=80
    )

    results = []

    for c in chunks:

        results.append({

            "chunk_type": "semantic",

            "page_type": page_type,

            "page": page_num,

            "text":
                f"SECTION TYPE: {page_type}\n\n"
                f"{c}"
        })

    return results

# ─────────────────────────────────────────────
# MASTER HYBRID CHUNKER
# ─────────────────────────────────────────────
def hybrid_chunk_page(
    page_data
):

    text = page_data["text"]

    page_num = page_data["page"]

    page_type = page_data["page_type"]

    if page_type == "table_heavy":

        return chunk_table_page(
            text,
            page_num,
            page_type
        )

    elif page_type in [

        "eligibility",

        "annexure"

    ]:

        return chunk_clause_page(
            text,
            page_num,
            page_type
        )

    else:

        return chunk_semantic_page(
            text,
            page_num,
            page_type
        )