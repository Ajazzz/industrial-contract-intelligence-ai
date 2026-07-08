from collections import defaultdict


def group_documents_by_contract(docs):
    """
    Group retrieved documents by contract name.
    """

    grouped = defaultdict(list)

    for doc in docs:

        metadata = doc.get("metadata", {})

        contract = metadata.get(
            "contract_name",
            metadata.get("source", "Unknown Contract")
        )

        grouped[contract].append(doc)

    return grouped


def build_comparison_context(grouped_docs):
    """
    Build an LLM-friendly context for comparing contracts.
    """

    sections = []

    for contract_name, docs in grouped_docs.items():

        section = [
            "=" * 60,
            f"CONTRACT: {contract_name}",
            "=" * 60,
            ""
        ]

        seen = set()

        for doc in docs:

            text = doc.get("content", "").strip()

            if not text:
                continue

            if text in seen:
                continue

            seen.add(text)

            metadata = doc.get("metadata", {})

            section.append(
                f"[Page {metadata.get('page', '?')}]"
            )

            section.append(text)

            section.append("")

        sections.append("\n".join(section))

    return "\n\n".join(sections)