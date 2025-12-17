from .extractor import extract_canonical_specs
from .formatter import build_single_line_input

def run_spec_extractor_agent(sales_agent_output: dict) -> dict:
    structured = sales_agent_output.get("technical_specifications_structured", {})
    raw_text = sales_agent_output.get("technical_specifications", "")

    canonical_specs = extract_canonical_specs(structured, raw_text)
    single_line = build_single_line_input(canonical_specs)

    confidence = 1.0
    penalties = {
        "conductor_material": 0.1,
        "standard": 0.15,
        "insulation_type": 0.05,
        "voltage_grade": 0.05
    }

    for field, penalty in penalties.items():
        if canonical_specs.get(field) in ["UNKNOWN", None]:
            confidence -= penalty

    confidence = max(confidence, 0.5)

    return {
        "canonical_specs": canonical_specs,
        "tender_input_line": single_line,
        "spec_confidence": round(confidence, 2)
    }


# Optional local test
if __name__ == "__main__":
    sample_sales_output = {
        "technical_specifications_structured": {
            "Conformity of the specification for XLPE cable": "as per IS:7098",
            "Cables suitable for use in mines": "No",
            "Cables suitable for use in low temperature applications": "No",
            "Classification of cables for improved fire performace category": "01",
            "Nominal Area of Conductor (in Sq mm)": "185",
            "Number of core (in Nos)": "4",
            "Material of conductor": "Material",
            "Type of inner sheath": "Type",
            "Type of cable": "Type of cable Armoured cable Material of armouring Galvanized steel formed wire Type of armouring Single wire OUTER SHEATH Type of outer sheath PVC",
            "Material of armouring": "Material of armouring Galvanized steel formed wire Type of armouring Single wire OUTER SHEATH Type of outer sheath PVC",
            "Type of armouring": "Type of armouring Single wire OUTER SHEATH Type of outer sheath PVC",
            "Type of outer sheath": "Type",
            "Type of sequential marking on cable": "Type of sequential marking on cable Screen printing on cable PACKING AND MARKING Cable wound on ISI Marked Wooden drum Standard length of cable on drum",
            "Cable wound on": "C",
            "Standard length of cable on drum (in m)": "500"
        },
    }

    output = run_spec_extractor_agent(sample_sales_output)
    print(output)
