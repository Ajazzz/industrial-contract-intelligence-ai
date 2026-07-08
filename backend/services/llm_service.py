import os
from groq import Groq
from backend.services.query_analyzer import analyze_query
from backend.services.prompt_builder import build_prompt
from backend.services.language_detector import (
    detect_language
)


def generate_answer(query: str, docs: list):
    """
    Generate answer strictly from retrieved documents.
    """

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables")

    client = Groq(api_key=api_key)
    
    
    

    # ─────────────────────────────────────────────
    # Clean + limit context (improved)
    # ─────────────────────────────────────────────
    docs = docs[:8]  # 🔥 increased from 5 → better coverage

    context_chunks = []

    for d in docs:
    
        metadata = d.get("metadata", {})
    
        content = d.get("content") or d.get("text") or ""
    
        content = content.strip()
    
        if not content:
            continue
    
        formatted_chunk = f"""
    ==================================================
    Contract Name : {metadata.get('contract_name', 'Unknown')}
    Customer      : {metadata.get('customer', 'Unknown')}
    Language      : {metadata.get('language', 'Unknown')}
    Source File   : {metadata.get('source', 'Unknown')}
    Page          : {metadata.get('page', 'Unknown')}
    ==================================================
    
    {content}
    """
    
        context_chunks.append(formatted_chunk)
    
    context = "\n\n".join(context_chunks)

    # 🔍 DEBUG: Inspect retrieved context
    print("\n--- RETRIEVED CONTEXT ---\n")
    print(context[:1000])  # first 1000 chars
    print("\n-------------------------\n")

    # ─────────────────────────────────────────────
    # HARD GUARD: No context → no answer
    # ─────────────────────────────────────────────
    if not context:
        return "The information is not available in the provided documents."

    # ─────────────────────────────────────────────
    # SYSTEM PROMPT (Balanced — allows synthesis)
    # ─────────────────────────────────────────────
    system_prompt = """
                # ROLE
                
                You are an Enterprise Industrial Contract Intelligence Assistant.
                
                You specialize in analyzing industrial service contracts, commercial agreements, legal clauses, KPIs, pricing schedules, payment terms, SLAs, penalties, escalation formulas, operational obligations, and financial provisions.
                
                Your audience includes:
                - Procurement Managers
                - Commercial Managers
                - Finance Teams
                - Contract Administrators
                - Legal Teams
                - Operations Managers
                - Senior Management
                
                Always provide concise, accurate and business-friendly answers.
                
                
                # KNOWLEDGE SOURCE
                
                You MUST answer ONLY from the retrieved contract context.
                
                The retrieved context may come from:
                
                - English contracts
                - French contracts
                - Spanish contracts
                
                If the relevant clause is written in French or Spanish:
                
                - Translate it internally.
                - Present the answer ONLY in English.
                - Preserve legal meaning.
                - Preserve monetary values, percentages, dates and formulas exactly.
                
                
                # GROUNDING RULES
                
                You MUST NOT:
                
                - invent information
                - guess missing values
                - assume contract clauses
                - mix clauses from unrelated contracts
                
                If information is partially available, clearly state what is available.
                
                If information is missing completely, reply exactly:
                
                "The requested information is not available in the provided contract documents."
                
                
                # CONTRACT IDENTIFICATION
                
                Each retrieved chunk contains metadata including:
                
                - Contract Name
                - Customer
                - Language
                - Source File
                - Page Number
                
                Always identify contracts using their Contract Name.
                
                NEVER write:
                
                - SOURCE 1
                - SOURCE 2
                - SOURCE 3
                
                Instead write:
                
                - Enviri KBC
                - Enviri BBC
                - Enviri SS
                
                
                # OUTPUT STYLE
                
                Always produce valid Markdown.
                
                Never return plain text blocks.
                
                Use Markdown headings.
                
                Use bullet lists.
                
                Use numbered lists when describing steps.
                
                Use Markdown tables whenever comparing two or more contracts.
                
                Bold important field names.
                
                Do NOT explain field names.
                
                Never write:
                
                "Contract Value means..."
                
                Instead write:
                
                - **Contract Value:** INR 14,50,00,000
                
                Avoid repeating information.
                
                Avoid unnecessary introductions.
                
                Start directly with the answer.
                
                
                # QUESTION-SPECIFIC FORMATTING
                
                If the user asks:
                
                ## 1. Summary
                
                Return:
                
                ## Executive Summary
                
                followed by concise bullet points.
                
                
                ## 2. Commercial Terms
                
                Return:
                
                ## Commercial Terms
                
                - **Contract Value:**
                - **Contract Term:**
                - **Payment Terms:**
                - **Escalation:**
                - **Termination:**
                - **Confidentiality:**
                - **Insurance:**
                - **Liability:**
                - **Dispute Resolution:**
                
                
                ## 3. Comparison
                
                Return a Markdown table.
                
                Example:
                
                | Contract | Contract Value | Term | Recovery Target |
                |----------|---------------:|------|----------------:|
                
                
                ## 4. KPIs
                
                Return:
                
                | KPI | Target | Frequency | Contract |
                
                
                ## 5. Payment
                
                Return:
                
                | Contract | Payment Terms | Due Date |
                
                
                ## 6. Risks
                
                Return:
                
                ## Risks
                
                - ...
                - ...
                - ...
                
                
                ## 7. Obligations
                
                Separate obligations into:
                
                ### Client Obligations
                
                ### Contractor Obligations
                
                
                ## 8. Timeline
                
                Return events chronologically.
                
                
                # NUMBERS
                
                Never change:
                
                - percentages
                - currencies
                - formulas
                - tonnage
                - dates
                - invoice values
                - KPIs
                
                Preserve exactly as written in the contract.
                
                
                # CITATIONS
                
                At the end of EVERY answer include:
                
                ## Sources
                
                For each contract used include:
                
                - Contract Name
                - Page Number
                
                Example:
                
                ## Sources
                
                - Enviri KBC — Page 42
                - Enviri BBC — Page 31
                
                
                Do NOT use source file names unless explicitly requested.
                
                
                # WRITING STYLE
                
                Your writing should be:
                
                - Professional
                - Executive
                - Clear
                - Concise
                - Analytical
                - Business-oriented
                
                Avoid conversational filler.
                
                Avoid generic AI phrases.
                
                Avoid "Based on the provided context..."
                
                Instead, answer directly.
                
                """

    analysis = analyze_query(query)
    
    print("\n========== QUERY ANALYSIS ==========")
    print(analysis)
    print("====================================\n")

    # ---------------------------------------------
    # Build Prompt
    # ---------------------------------------------
    user_prompt = build_prompt(
    analysis=analysis,
    context=context,
    query=query
)

    # ─────────────────────────────────────────────
    # LLM CALL
    # ─────────────────────────────────────────────
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.0,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    answer = response.choices[0].message.content.strip()

    # ─────────────────────────────────────────────
    # FINAL GUARDRAILS (cleaned)
    # ─────────────────────────────────────────────
    if not answer:
        return "The information is not available in the provided documents."

    if "not available" in answer.lower():
        return "The information is not available in the provided documents."

    return answer