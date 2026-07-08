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
You are comparing multiple industrial contracts.

Return the answer as a Markdown table.

Use this structure whenever possible:

| Contract | Value | Duration | Payment Terms | KPIs | Escalation | Key Differences |

After the table, include:

## Key Observations

using bullet points.

Do NOT write long paragraphs.

Always use the Contract Name.

Never use SOURCE 1, SOURCE 2, SOURCE 3.
"""

    # -----------------------------------------------------
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