from collections import defaultdict


def build_context(docs):

    context = []

    for doc in docs:

        text = doc.get("content", "").strip()

        if text:

            context.append(text)

    return "\n\n".join(context)


def build_comparison_context(docs):

    grouped = defaultdict(list)

    for doc in docs:

        metadata = doc.get("metadata", {})

        contract = metadata.get(
            "contract_name",
            "Unknown Contract"
        )

        grouped[contract].append(
            doc.get("content", "")
        )

    sections = []

    for contract, chunks in grouped.items():

        sections.append(
            f"""
=================================================
CONTRACT : {contract}
=================================================

{chr(10).join(chunks)}
"""
        )

    return "\n\n".join(sections)