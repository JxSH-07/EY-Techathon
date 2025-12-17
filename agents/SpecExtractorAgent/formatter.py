def build_single_line_input(specs: dict) -> str:
    parts = []

    if specs.get("core_count"):
        parts.append(f"{specs['core_count']} core")

    if specs.get("cross_section_sqmm"):
        parts.append(f"{specs['cross_section_sqmm']} sqmm")

    if specs.get("conductor_material") != "UNKNOWN":
        parts.append(specs["conductor_material"].lower())

    if specs.get("cable_type") != "UNKNOWN":
        parts.append(specs["cable_type"].lower())
    elif specs.get("armouring") == "Yes":
        parts.append("armoured")


    if specs.get("armouring_material") != "UNKNOWN":
        parts.append(specs["armouring_material"].lower())

    if specs.get("insulation_type") != "UNKNOWN":
        parts.append(f"{specs['insulation_type']} insulated")

    if specs.get("outer_sheath") != "UNKNOWN":
        parts.append(f"{specs['outer_sheath']} sheathed")

    if specs.get("standard") != "UNKNOWN":
        parts.append(f"as per {specs['standard']}")

    if specs.get("voltage_grade") != "UNKNOWN":
        parts.append(f"{specs['voltage_grade']} grade")

    return " ".join(parts)
