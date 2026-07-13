from backend.services.query_analyzer import QueryAnalysis


def build_prompt(
    analysis: QueryAnalysis,
    context: str,
    query: str
) -> str:

    instruction = ""

    # -----------------------------------------------------
    # COMPARISON
    # -----------------------------------------------------
    if analysis.intent == "comparison":

        instruction = """
You are an Enterprise Contract Analyst specializing in industrial service contracts.

Use ONLY the provided context.

Do NOT guess, infer, or fabricate information.

If information is unavailable, write:
"Not specified".

IMPORTANT:

Always answer in English.

Even if the retrieved documents are written in French or Spanish,
translate the relevant information into fluent English.

Do not return the original French or Spanish text unless the user explicitly asks for it.

Your task is to compare ALL retrieved contracts.

Instructions:

1. First identify every contract present in the retrieved context.

2. Determine the business attributes that are common across two or more contracts.

3. Compare ONLY those attributes.

4. Do NOT compare attributes that appear in only one contract.

5. If the comparison contains structured information (for example Value, Duration, Escalation, Payment Terms, Governing Law, Equipment, KPIs), present it as a Markdown table.

6. If the information is descriptive or qualitative, use headings and bullet points instead of forcing a table.

7. Do NOT create empty columns or unnecessary rows.

8. Keep every comparison concise and business-focused.

After the comparison, include:

## Key Observations

Provide 3–5 concise bullet points covering:
- Major similarities
- Major differences
- Commercial impact
- Operational impact (if applicable)

Never include information that is not supported by the retrieved context.
"""    # -----------------------------------------------------
    # COMMERCIAL TERMS
    # -----------------------------------------------------
    elif analysis.intent == "commercial_terms":

        instruction = """
Return:

## Commercial Terms

Use bullet points.

Example:

- **Contract Value:**
- **Contract Term:**
- **Payment Terms:**
- **Escalation:**
- **Termination:**
- **Insurance:**
- **Confidentiality:**
"""

    # -----------------------------------------------------
    # PAYMENT
    # -----------------------------------------------------
    elif analysis.intent == "payment":

        instruction = """
Return the payment information as a Markdown table.

| Contract | Payment Terms | Due Date | Currency |
"""

    # -----------------------------------------------------
    # KPI
    # -----------------------------------------------------
    elif analysis.intent == "kpi":

        instruction = """
Return KPIs using a Markdown table.

| KPI | Target | Frequency | Contract |
"""

    # -----------------------------------------------------
    # SUMMARY
    # -----------------------------------------------------
    elif analysis.intent == "summary":

        instruction = """
Return:

## Executive Summary

Followed by concise bullet points.

Maximum 10 bullets.
"""

    # -----------------------------------------------------
    # DEFAULT
    # -----------------------------------------------------
    else:

        instruction = """
Answer clearly using Markdown.

Use headings and bullet points whenever appropriate.
"""

    return f"""
{instruction}

--------------------------------------------------

CONTEXT

{context}

--------------------------------------------------

QUESTION

{query}

--------------------------------------------------

ANSWER
"""