import re
from collections import defaultdict


def build_dynamic_comparison_table(docs):

    contracts = defaultdict(dict)

    for doc in docs:

        metadata = doc.get("metadata", {})
        text = doc.get("content", "")

        contract = metadata.get(
            "contract_name",
            "Unknown Contract"
        )

        contracts[contract]["Customer"] = metadata.get(
            "customer",
            "Not specified"
        )

        contracts[contract]["Language"] = metadata.get(
            "language",
            "Not specified"
        )

        # ----------------------------
        # Contract Value
        # ----------------------------

        if "Value" not in contracts[contract]:

            value = extract_contract_value(text)

            if value:
                contracts[contract]["Value"] = value

        # ----------------------------
        # Duration
        # ----------------------------

        if "Duration" not in contracts[contract]:

            duration = extract_duration(text)

            if duration:
                contracts[contract]["Duration"] = duration

    return generate_markdown_table(contracts)


def extract_contract_value(text):

    patterns = [

        r"(EUR\s?[\d,\.]+)",

        r"(INR\s?[\d,\.]+)"

    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            return match.group(1)

    return "Not specified"


def extract_duration(text):

    match = re.search(

        r"(\d+)\s+year",

        text,

        re.IGNORECASE

    )

    if match:

        return match.group(0)

    return "Not specified"

def generate_markdown_table(contracts):

    headers = [

        "Contract",

        "Customer",

        "Language",

        "Value",

        "Duration"

    ]

    table = []

    table.append(
        "| " + " | ".join(headers) + " |"
    )

    table.append(
        "|" + "|".join(["---"] * len(headers)) + "|"
    )

    for contract, values in contracts.items():

        row = [

            contract,

            values.get(
                "Customer",
                "Not specified"
            ),

            values.get(
                "Language",
                "Not specified"
            ),

            values.get(
                "Value",
                "Not specified"
            ),

            values.get(
                "Duration",
                "Not specified"
            )

        ]

        table.append(

            "| " + " | ".join(row) + " |"

        )

    return "\n".join(table)