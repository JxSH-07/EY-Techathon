# agents/SpecExtractorAgent/extractor.py

import json
from openai import OpenAI
from .prompt import SPEC_EXTRACTION_PROMPT
from .schema import CANONICAL_SCHEMA

client = OpenAI()

def _enforce_schema_defaults(llm_output: dict) -> dict:
    """
    Ensures all canonical schema keys exist.
    Missing or empty values are set to 'UNKNOWN'.
    """
    normalized = {}

    for key in CANONICAL_SCHEMA:
        value = llm_output.get(key)

        if value is None or value == "" or value == "null":
            normalized[key] = "UNKNOWN"
        else:
            normalized[key] = value

    return normalized


def extract_canonical_specs(structured_specs: dict, raw_text: str) -> dict:
    """
    Uses LLM to clean, deduplicate and normalize cable specifications
    """

    input_payload = {
        "structured_specs": structured_specs,
        "raw_text": raw_text
    }

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {"role": "system", "content": SPEC_EXTRACTION_PROMPT},
            {"role": "user", "content": json.dumps(input_payload)}
        ]
    )

    content = response.choices[0].message.content.strip()

    try:
        llm_output = json.loads(content)
    except json.JSONDecodeError:
        raise ValueError("LLM returned invalid JSON")

    # 🔒 Agentic safety guarantee
    canonical_specs = _enforce_schema_defaults(llm_output)

    return canonical_specs
