from dataclasses import dataclass
from typing import List
import re


@dataclass
class QueryAnalysis:

    intent: str

    topic: str

    contracts: List[str]

    compare_all: bool

    output_format: str


def analyze_query(query: str) -> QueryAnalysis:
    
    print(">>> NEW QUERY ANALYZER IS RUNNING <<<")

    q = query.lower()

    contracts = []

    # -----------------------------------------
    # CONTRACT DETECTION
    # -----------------------------------------

    if "kbc" in q:
        contracts.append("enviri_kbc")

    if "bbc" in q:
        contracts.append("enviri_bbc")
    
    if "ss" in q:
        contracts.append("enviri_ss")

    compare_all = False

    if (
        "all contracts" in q
        or "all three" in q
        or "compare all" in q
        
        or "all contract" in q
        or "every contract" in q
        or "across all contracts" in q
        or "all agreements" in q
        or "across all agreements" in q
        or "Compare all contracts" in q
    ):

        compare_all = True

        contracts = [
            "enviri_kbc",
        "enviri_bbc",
        "enviri_ss"
]

    # -----------------------------------------
    # INTENT
    # -----------------------------------------

    intent = "general"

    if any(word in q for word in [
        "compare",
        "difference",
        "differences",
        "vs",
        "versus",
        "between",
        "across"
    ]):

        intent = "comparison"

    elif any(word in q for word in [
        "summary",
        "summarize",
        "summarise",
        "overview"
    ]):

        intent = "summary"

    elif any(word in q for word in [
        "payment",
        "invoice",
        "billing"
    ]):

        intent = "payment"

    elif any(word in q for word in [
        "kpi",
        "target",
        "performance"
    ]):

        intent = "kpi"

    elif any(word in q for word in [
        "commercial"
    ]):

        intent = "commercial_terms"

    # -----------------------------------------
    # TOPIC
    # -----------------------------------------

    topic = "general"

    if "metal recovery" in q:

        topic = "metal_recovery"

    elif "payment" in q:

        topic = "payment"

    elif "escalation" in q:

        topic = "escalation"

    elif "termination" in q:

        topic = "termination"

    elif "risk" in q:

        topic = "risk"

    # -----------------------------------------
    # OUTPUT FORMAT
    # -----------------------------------------

    output_format = "paragraph"

    if intent == "comparison":

        output_format = "table"

    elif intent in [

        "payment",

        "commercial_terms",

        "kpi"

    ]:

        output_format = "bullet"

    elif intent == "summary":

        output_format = "summary"

    result = QueryAnalysis(
    intent=intent,
    topic=topic,
    contracts=contracts,
    compare_all=compare_all,
    output_format=output_format
    )
    
    print("RETURNING FROM QUERY_ANALYZER:", result)
    print("RETURN TYPE:", type(result))
    
    return result