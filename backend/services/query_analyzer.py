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

    q = query.lower()

    contracts = []

    # -----------------------------------------
    # CONTRACT DETECTION
    # -----------------------------------------

    if "kbc" in q:
        contracts.append("Enviri KBC")

    if "bbc" in q:
        contracts.append("Enviri BBC")

    if "ss" in q:
        contracts.append("Enviri SS")

    compare_all = False

    if (
        "all contracts" in q
        or "all three" in q
        or "compare all" in q
    ):

        compare_all = True

        contracts = [
            "Enviri KBC",
            "Enviri BBC",
            "Enviri SS"
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

    return QueryAnalysis(

        intent=intent,

        topic=topic,

        contracts=contracts,

        compare_all=compare_all,

        output_format=output_format
    )