import os
import json
import time

from groq import Groq

from backend.services.retriever import hybrid_retrieve

# ─────────────────────────────────────────────
# INIT GROQ
# ─────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY missing")

client = Groq(api_key=GROQ_API_KEY)

MODEL_NAME = "llama-3.3-70b-versatile"

# ─────────────────────────────────────────────
# BUILD CONTEXT
# ─────────────────────────────────────────────
def build_context(docs):

    context_parts = []

    for i, d in enumerate(docs):

        metadata = d.get("metadata", {})

        source = metadata.get("source", "Unknown")

        page = metadata.get("page", 1)

        section = metadata.get("section", "GENERAL")

        service_type = metadata.get(
            "service_type",
            "general"
        )

        contains_formula = metadata.get(
            "contains_formula",
            False
        )

        contains_table = metadata.get(
            "contains_table",
            False
        )

        content = d.get("content", "").strip()

        if not content:
            continue

        context_parts.append(
            f"""
SOURCE {i+1}

Document: {source}
Page: {page}
Section: {section}
Service Type: {service_type}
Contains Formula: {contains_formula}
Contains Table: {contains_table}

CONTENT:
{content}
"""
        )

    return "\n\n".join(context_parts)

# ─────────────────────────────────────────────
# FORMAT SOURCES
# ─────────────────────────────────────────────
def format_sources(docs):

    formatted_sources = []

    for idx, d in enumerate(docs):

        metadata = d.get("metadata", {})

        formatted_sources.append({
            "id": str(idx + 1),

            "documentId": metadata.get(
                "source",
                "Unknown"
            ),

            "documentTitle": metadata.get(
                "source",
                "Unknown"
            ),

            "content": d.get("content", ""),

            "pageNumber": metadata.get(
                "page",
                1
            ),

            "section": metadata.get(
                "section",
                "GENERAL"
            ),

            "similarityScore": round(
                metadata.get(
                    "dense_score",
                    0
                ),
                5
            ),

            "rerankScore": round(
                metadata.get(
                    "rerank_score",
                    0
                ),
                5
            ),

            "chunkType": "contract_clause",

            "metadata": {
                "source": metadata.get(
                    "source",
                    "Unknown"
                ),

                "section": metadata.get(
                    "section",
                    "GENERAL"
                ),

                "document_type": metadata.get(
                    "document_type",
                    "industrial_contract"
                ),

                "service_type": metadata.get(
                    "service_type",
                    "general"
                ),

                "contains_formula": metadata.get(
                    "contains_formula",
                    False
                ),

                "contains_table": metadata.get(
                    "contains_table",
                    False
                )
            },

            "citations": [
                {
                    "id": f"cite-{idx+1}",

                    "text": metadata.get(
                        "source",
                        "Unknown"
                    ),

                    "location": (
                        f"Page "
                        f"{metadata.get('page', 1)}"
                    ),

                    "confidence": round(
                        metadata.get(
                            "rerank_score",
                            0.9
                        ),
                        3
                    )
                }
            ]
        })

    return formatted_sources

# ─────────────────────────────────────────────
# QUERY ANALYSIS
# ─────────────────────────────────────────────
def build_query_analysis(query: str):

    query_lower = query.lower()

    entities = []

    filters = {}

    # ENTITY DETECTION
    keywords = [
        "diesel",
        "excavation",
        "slag",
        "invoice",
        "kpi",
        "sla",
        "escalation",
        "penalty",
        "equipment",
        "cpi",
        "fuel"
    ]

    for keyword in keywords:

        if keyword in query_lower:
            entities.append(keyword)

    # FILTER DETECTION
    if "diesel" in query_lower:
        filters["service_type"] = "fuel_escalation"

    elif "slag" in query_lower:
        filters["service_type"] = "slag_handling"

    elif "excavation" in query_lower:
        filters["service_type"] = "excavation"

    retrieval_strategy = (
        "hybrid_clause_rerank"
    )

    return {
        "intent": (
            "industrial_contract_analysis"
        ),

        "entities": entities,

        "filters": filters,

        "expandedQueries": [
            query,
            f"contract clause related to {query}",
            f"commercial escalation details for {query}",
            f"industrial operations context for {query}"
        ],

        "retrievalStrategy": retrieval_strategy
    }

# ─────────────────────────────────────────────
# BUILD PROMPT
# ─────────────────────────────────────────────
def build_prompt(query, context):

    return f"""
You are a senior industrial contracts analyst
specialized in:

- steel plant operations
- industrial service agreements
- diesel escalation mechanisms
- KPI/SLA analysis
- excavation contracts
- slag handling operations
- commercial contract reviews
- invoice escalation analysis
- industrial pricing models

You are assisting operations, procurement,
commercial, and finance teams.

IMPORTANT RULES:

1. Answer ONLY using the provided context.

2. Do NOT hallucinate or invent clauses.

3. If information is missing, say:
"I could not find that information in the documents."

4. When formulas exist:
- explain them clearly
- describe escalation logic
- explain business impact

5. When tables exist:
- summarize operational insights
- explain rate changes
- explain KPI implications

6. Prefer:
- structured explanations
- bullet points
- clause references
- operational reasoning

7. If the question relates to:
- diesel escalation
- CPI adjustments
- KPI penalties
- invoice deductions
- equipment utilization

then explain:
- trigger conditions
- escalation applicability
- operational impact
- commercial implications

CONTEXT:
{context}

QUESTION:
{query}
"""

# ─────────────────────────────────────────────
# NON-STREAMING PIPELINE
# ─────────────────────────────────────────────
def run_rag_pipeline(query: str):

    total_start = time.time()

    # RETRIEVAL
    retrieval_result = hybrid_retrieve(query)

    docs = retrieval_result["documents"]

    retrieval_debug = retrieval_result[
        "retrieval_debug"
    ]

    retrieval_latency = retrieval_result[
        "latency"
    ]

    # CONTEXT
    context = build_context(docs)

    # PROMPT
    prompt = build_prompt(query, context)

    generation_start = time.time()

    response = client.chat.completions.create(
        model=MODEL_NAME,
        temperature=0,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
    )

    answer = (
        response
        .choices[0]
        .message
        .content
        .strip()
    )

    total_latency = round(
        (time.time() - total_start) * 1000,
        2
    )

    return {
        "answer": answer,

        "sources": format_sources(docs),

        "queryAnalysis": (
            build_query_analysis(query)
        ),

        "retrievalDebug": {
            "hybridSearchUsed": True,

            "bm25Hits": len(
                retrieval_debug.get(
                    "bm25_results",
                    []
                )
            ),

            "denseHits": len(
                retrieval_debug.get(
                    "vector_results",
                    []
                )
            ),

            "rerankingApplied": True,

            "contextCompressed": False,

            "totalChunksRetrieved": len(
                retrieval_debug.get(
                    "vector_results",
                    []
                )
            ),

            "finalChunksUsed": len(docs),

            "retrievalTimeMs": retrieval_latency.get(
                "retrieval_total_ms",
                0
            ),

            "embeddingModel":
                "embed-english-v3.0",

            "rerankModel":
                "rerank-english-v3.0"
        },

        "latencyMs": total_latency,

        "tokensUsed": len(answer.split()),

        "confidenceScore": 0.94
    }

# ─────────────────────────────────────────────
# STREAMING PIPELINE
# ─────────────────────────────────────────────
def stream_rag_pipeline(query: str):

    total_start = time.time()

    retrieval_result = hybrid_retrieve(query)

    docs = retrieval_result["documents"]

    retrieval_debug = retrieval_result[
        "retrieval_debug"
    ]

    retrieval_latency = retrieval_result[
        "latency"
    ]

    context = build_context(docs)

    prompt = build_prompt(query, context)

    stream = client.chat.completions.create(
        model=MODEL_NAME,
        temperature=0,
        stream=True,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
    )

    full_answer = ""

    for chunk in stream:

        delta = chunk.choices[0].delta.content

        if not delta:
            continue

        full_answer += delta

        payload = {
            "type": "token",
            "content": delta
        }

        yield (
            f"data: "
            f"{json.dumps(payload)}\n\n"
        )

    total_latency = round(
        (time.time() - total_start) * 1000,
        2
    )

    meta_payload = {
        "type": "meta",

        "meta": {
            "sources": format_sources(docs),

            "queryAnalysis":
                build_query_analysis(query),

            "retrievalDebug": {
                "hybridSearchUsed": True,

                "bm25Hits": len(
                    retrieval_debug.get(
                        "bm25_results",
                        []
                    )
                ),

                "denseHits": len(
                    retrieval_debug.get(
                        "vector_results",
                        []
                    )
                ),

                "rerankingApplied": True,

                "contextCompressed": False,

                "totalChunksRetrieved": len(
                    retrieval_debug.get(
                        "vector_results",
                        []
                    )
                ),

                "finalChunksUsed": len(docs),

                "retrievalTimeMs":
                    retrieval_latency.get(
                        "retrieval_total_ms",
                        0
                    ),

                "embeddingModel":
                    "embed-english-v3.0",

                "rerankModel":
                    "rerank-english-v3.0"
            },

            "latencyMs": total_latency,

            "tokensUsed":
                len(full_answer.split()),

            "confidenceScore": 0.94
        }
    }

    yield (
        f"data: "
        f"{json.dumps(meta_payload)}\n\n"
    )

    yield "data: [DONE]\n\n"