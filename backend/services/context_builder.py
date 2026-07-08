def build_context(docs):

    context_parts = []

    for d in docs:

        metadata = d.get("metadata", {})

        content = d.get("content", "").strip()

        if not content:
            continue

        context_parts.append(

f"""
==================================================

Contract Name : {metadata.get("contract_name", "Unknown")}

Customer      : {metadata.get("customer", "Unknown")}

Language      : {metadata.get("language", "Unknown")}

Source File   : {metadata.get("source", "Unknown")}

Page          : {metadata.get("page", 1)}

Section       : {metadata.get("section", "GENERAL")}

Service Type  : {metadata.get("service_type", "general")}

==================================================

{content}
"""
        )

    return "\n\n".join(context_parts)