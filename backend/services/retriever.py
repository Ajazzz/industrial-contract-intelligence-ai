import os
import time
import cohere
import numpy as np
from backend.services.query_analyzer import analyze_query

from pinecone import Pinecone
from rank_bm25 import BM25Okapi
from backend.services.language_detector import (
    detect_language
)

# ─────────────────────────────────────────────
# INIT CLIENTS
# ─────────────────────────────────────────────
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

if not COHERE_API_KEY:
    raise ValueError("COHERE_API_KEY missing")

co = cohere.Client(COHERE_API_KEY)

pc = Pinecone(
    api_key=os.getenv("PINECONE_API_KEY")
)

index_name = os.getenv("INDEX_NAME")

index = pc.Index(index_name)

# ─────────────────────────────────────────────
# EMBEDDING
# ─────────────────────────────────────────────
def embed_query(query: str):

    response = co.embed(
        texts=[query],
        model="embed-multilingual-v3.0",
        input_type="search_query",
        embedding_types=["float"]
    )

    return response.embeddings.float[0]

# ─────────────────────────────────────────────
# QUERY ANALYSIS
# ─────────────────────────────────────────────
def analyze_metadata_boost(query):

    query_lower = query.lower()

    analysis = {
        "boost_formula": False,
        "boost_tables": False,
        "service_type": None
    }

    # FORMULA INTENT
    formula_keywords = [
        "formula",
        "calculation",
        "escalation",
        "adjustment",
        "percentage",
        "rate revision"
    ]

    if any(
        k in query_lower
        for k in formula_keywords
    ):
        analysis["boost_formula"] = True

    # TABLE INTENT
    table_keywords = [
        "invoice",
        "schedule",
        "table",
        "pricing",
        "rate card"
    ]

    if any(
        k in query_lower
        for k in table_keywords
    ):
        analysis["boost_tables"] = True

    # SERVICE TYPE DETECTION
    if "diesel" in query_lower:
        analysis["service_type"] = (
            "fuel_escalation"
        )

    elif "slag" in query_lower:
        analysis["service_type"] = (
            "slag_handling"
        )

    elif "excavation" in query_lower:
        analysis["service_type"] = (
            "excavation"
        )

    elif "waste" in query_lower:
        analysis["service_type"] = (
            "waste_management"
        )

    return analysis

# ─────────────────────────────────────────────
# VECTOR SEARCH
# ─────────────────────────────────────────────
def vector_search(query,language=None, contract_id=None,top_k=20):

    start_time = time.time()

    query_embedding = embed_query(query)
    

    
    
    
    # results = index.query(
    # vector=query_embedding,
    # top_k=top_k,
    # include_metadata=True
    # )
    
    
    query_params = {

    "vector": query_embedding,

    "top_k": top_k,

    "include_metadata": True

            }
            
    filters = {}
            
    if language:
    
        filters["language"] = {
            "$eq": language
        }
    
    if contract_id:
    
        filters["contract_id"] = {
            "$eq": contract_id
        }
    
    if filters:
    
        query_params["filter"] = filters
    
    results = index.query(
        **query_params
    )
        
    docs = []

    for match in results.get("matches", []):

        metadata = match.get(
            "metadata",
            {}
        ) or {}

        docs.append({
            "content": metadata.get(
                "text",
                ""
            ),

            "metadata": {
                "source": metadata.get(
                    "source",
                    "Unknown"
                ),

                "page": metadata.get(
                    "page",
                    1
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
                ),

                "dense_score": float(
                    match.get("score", 0)
                ),
                
                "contract_id": metadata.get(
                    "contract_id",
                    "Unknown"
                ),
                
                "contract_name": metadata.get(
                    "contract_name",
                    "Unknown Contract"
                ),
                
                "customer": metadata.get(
                    "customer",
                    "Unknown"
                ),
                
                "language": metadata.get(
                    "language",
                    "Unknown"
                ),
                
                "country": metadata.get(
                    "country",
                    "Unknown"
                ),
            }
        })

    latency_ms = round(
        (time.time() - start_time) * 1000,
        2
    )

    return docs, latency_ms

# ─────────────────────────────────────────────
# BM25 SEARCH
# ─────────────────────────────────────────────
def bm25_search(
    query,
    vector_docs,
    top_k=15
):

    start_time = time.time()

    corpus = [
        doc["content"]
        for doc in vector_docs
    ]

    tokenized_corpus = [
        doc.split(" ")
        for doc in corpus
    ]

    bm25 = BM25Okapi(tokenized_corpus)

    tokenized_query = query.split(" ")

    scores = bm25.get_scores(
        tokenized_query
    )

    ranked_indices = np.argsort(scores)[::-1]

    bm25_docs = []

    for idx in ranked_indices:

        doc = vector_docs[idx]

        doc["metadata"]["bm25_score"] = (
            float(scores[idx])
        )

        bm25_docs.append(doc)

    latency_ms = round(
        (time.time() - start_time) * 1000,
        2
    )

    return bm25_docs[:top_k], latency_ms

# ─────────────────────────────────────────────
# METADATA BOOSTING
# ─────────────────────────────────────────────
def apply_metadata_boosting(
    query_analysis,
    docs
):

    boosted_docs = []

    for doc in docs:

        metadata = doc["metadata"]

        boost = 0

        # FORMULA BOOST
        if (
            query_analysis["boost_formula"]
            and metadata.get(
                "contains_formula",
                False
            )
        ):
            boost += 0.12

        # TABLE BOOST
        if (
            query_analysis["boost_tables"]
            and metadata.get(
                "contains_table",
                False
            )
        ):
            boost += 0.08

        # SERVICE TYPE BOOST
        if (
            query_analysis["service_type"]
            and metadata.get(
                "service_type"
            )
            ==
            query_analysis["service_type"]
        ):
            boost += 0.15

        metadata["boost_score"] = boost

        metadata["hybrid_score"] = (
            metadata.get("dense_score", 0)
            +
            metadata.get("bm25_score", 0) * 0.01
            +
            boost
        )

        boosted_docs.append(doc)

    boosted_docs.sort(
        key=lambda x:
        x["metadata"]["hybrid_score"],
        reverse=True
    )

    return boosted_docs

# ─────────────────────────────────────────────
# RERANK
# ─────────────────────────────────────────────
def rerank_documents(
    query,
    docs,
    top_k=7
):

    start_time = time.time()

    documents = [
        d["content"]
        for d in docs
    ]

    response = co.rerank(
        query=query,
        documents=documents,
        model="rerank-multilingual-v3.0",
        top_n=top_k
    )
    

    reranked_docs = []

    for result in response.results:

        original_doc = docs[result.index]

        original_doc["metadata"][
            "rerank_score"
        ] = float(
            result.relevance_score
        )

        reranked_docs.append(
            original_doc
        )

    latency_ms = round(
        (time.time() - start_time) * 1000,
        2
    )

    return reranked_docs, latency_ms

# ─────────────────────────────────────────────
# FORMAT DEBUG RESULTS
# ─────────────────────────────────────────────
def format_debug_results(
    docs,
    score_key
):

    formatted = []

    for doc in docs:

        metadata = doc.get(
            "metadata",
            {}
        )

        formatted.append({
            "source": metadata.get(
                "source",
                "Unknown"
            ),

            "page": metadata.get(
                "page",
                1
            ),

            "section": metadata.get(
                "section",
                "GENERAL"
            ),

            "score": round(
                metadata.get(
                    score_key,
                    0
                ),
                5
            ),

            "service_type": metadata.get(
                "service_type",
                "general"
            ),

            "contains_formula":
                metadata.get(
                    "contains_formula",
                    False
                ),

            "contains_table":
                metadata.get(
                    "contains_table",
                    False
                ),

            "snippet":
                doc.get(
                    "content",
                    ""
                )[:300]
        })

    return formatted

# ─────────────────────────────────────────────
# HYBRID RETRIEVAL
# ─────────────────────────────────────────────
def hybrid_retrieve(
    query: str,
    top_k: int = 7
):

    retrieval_start = time.time()
    query_language = detect_language(
    query
    )
    
    print( f"Query language: " f"{query_language}"
    )

    # -----------------------------------------
    # QUERY ANALYSIS
    # -----------------------------------------
    query_analysis = analyze_query(query)
    
    print("Query Analysis:", query_analysis)
    
    # -----------------------------------------
    # METADATA BOOST ANALYSIS
    # -----------------------------------------
    metadata_analysis = analyze_metadata_boost(query)
    
    print("Metadata Analysis:", metadata_analysis)
    
    # print(analyze_query)
    # print(analyze_query.__code__.co_filename)
    # print(type(query_analysis))
    # print(query_analysis)
    
    # print("Function being called:", analyze_query.__module__)
    # print("Type:", type(query_analysis))
    # print("Value:", query_analysis)

    # ─────────────────────────────────────────
    # STEP 1 — VECTOR SEARCH
    # ─────────────────────────────────────────
    
    if query_analysis.compare_all:

        print("\nUsing Comparison Retrieval...\n")

        vector_docs, vector_latency = comparison_vector_search(
    
            query=query,
    
            contract_ids=query_analysis.contracts
    
        )

    else:
    
        vector_docs, vector_latency = vector_search(
    
            query=query,
    
            top_k=25
    
        )

    # ─────────────────────────────────────────
    # STEP 2 — BM25 SEARCH
    # ─────────────────────────────────────────
    bm25_docs, bm25_latency = (
        bm25_search(
            query,
            vector_docs,
            top_k=20
        )
    )

    # ─────────────────────────────────────────
    # STEP 3 — METADATA BOOSTING
    # ─────────────────────────────────────────
    boosted_docs = (
        apply_metadata_boosting(
            metadata_analysis,
            bm25_docs
        )
    )

    # ─────────────────────────────────────────
    # STEP 4 — RERANK
    # ─────────────────────────────────────────
    reranked_docs, rerank_latency = (
        rerank_documents(
            query,
            boosted_docs,
            top_k=top_k
        )
    )

    total_latency = round(
        (
            time.time()
            -
            retrieval_start
        ) * 1000,
        2
    )

    # ─────────────────────────────────────────
    # DEBUG PAYLOAD
    # ─────────────────────────────────────────
    retrieval_debug = {

        "vector_results":
            format_debug_results(
                vector_docs,
                "dense_score"
            ),

        "bm25_results":
            format_debug_results(
                bm25_docs,
                "bm25_score"
            ),

        "reranked_results":
            format_debug_results(
                reranked_docs,
                "rerank_score"
            )
    }

    # ─────────────────────────────────────────
    # LATENCY
    # ─────────────────────────────────────────
    latency = {

        "vector_search_ms":
            vector_latency,

        "bm25_ms":
            bm25_latency,

        "rerank_ms":
            rerank_latency,

        "retrieval_total_ms":
            total_latency
            
            
    }
        
        
    print("\n========== Retrieved Documents ==========")

    for i, doc in enumerate(reranked_docs, 1):

        md = doc.get("metadata", {})

        print(
            f"{i}. "
            f"{md.get('contract_name')} | "
            f"{md.get('language')} | "
            f"Page {md.get('page')}"
        )

    print("=========================================\n")

    return {
        "documents": reranked_docs,
        "retrieval_debug": retrieval_debug,
        "latency": latency
    }


def comparison_vector_search(query, contract_ids):

    

    all_docs = []

    total_latency = 0

    for contract_id in contract_ids:

        docs, latency = vector_search(

            query=query,

            contract_id=contract_id,

            top_k=5

        )

        total_latency += latency

        print(
            f"Retrieved {len(docs)} chunks from {contract_id}"
        )

        all_docs.extend(docs)

    print(
        f"\nTotal comparison chunks: {len(all_docs)}\n"
    )

    return all_docs, total_latency


def comparison_retrieve(query, contracts):

    all_docs = []

    for contract in contracts:

        print(f"Retrieving contract: {contract}")

        query_embedding = embed_query(query)

        results = index.query(
            vector=query_embedding,
            top_k=5,
            include_metadata=True,
            filter={
                "contract_name": {
                    "$eq": contract
                }
            }
        )
        print("Calling Pinecone...")
        print("Pinecone finished")

        for match in results.get("matches", []):

            metadata = match.get("metadata", {}) or {}

            all_docs.append({

                "content": metadata.get("text", ""),

                "metadata": metadata

            })

    return all_docs


