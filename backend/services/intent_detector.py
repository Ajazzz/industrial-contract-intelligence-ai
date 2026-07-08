import re


def detect_intent(query: str) -> str:

    q = query.lower()

    # Comparison
    if any(word in q for word in [
        "compare",
        "comparison",
        "difference",
        "differences",
        "vs",
        "versus",
        "across",
        "between"
    ]):
        return "comparison"

    # Executive Summary
    if any(word in q for word in [
        "summary",
        "summarize",
        "overview",
        "executive summary"
    ]):
        return "summary"

    # Commercial Terms
    if any(word in q for word in [
        "commercial",
        "commercial terms",
        "contract value",
        "contract term"
    ]):
        return "commercial_terms"

    # Payment
    if any(word in q for word in [
        "payment",
        "invoice",
        "billing",
        "payable",
        "payment terms"
    ]):
        return "payment"

    # KPI
    if any(word in q for word in [
        "kpi",
        "sla",
        "target",
        "recovery",
        "performance"
    ]):
        return "kpi"

    # Escalation
    if any(word in q for word in [
        "escalation",
        "cpi",
        "wpi",
        "diesel",
        "price adjustment"
    ]):
        return "escalation"

    # Obligations
    if any(word in q for word in [
        "obligation",
        "responsibility",
        "shall",
        "contractor",
        "client"
    ]):
        return "obligations"

    # Penalties
    if any(word in q for word in [
        "penalty",
        "liquidated damages",
        "deduction",
        "fine"
    ]):
        return "penalties"

    # Risk
    if any(word in q for word in [
        "risk",
        "liability",
        "indemnity",
        "insurance"
    ]):
        return "risk"

    # Timeline
    if any(word in q for word in [
        "timeline",
        "schedule",
        "duration",
        "expiry",
        "expiration"
    ]):
        return "timeline"

    return "general"