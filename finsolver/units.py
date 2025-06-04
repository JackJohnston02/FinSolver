length_units = {
    "mm": 1e-3,
    "cm": 1e-2,
    "m": 1.0,
    "in": 0.0254,
    "ft": 0.3048,
}

modulus_units = {
    "GPa": 1e9,
    "MPa": 1e6,
}

density_units = {
    "kg/m³": 1.0,
}

def convert_to_si(value: float, from_unit: str) -> float:
    if from_unit in length_units:
        return value * length_units[from_unit]
    elif from_unit in modulus_units:
        return value * modulus_units[from_unit]
    elif from_unit in density_units:
        return value * density_units[from_unit]
    else:
        raise ValueError(f"Unsupported or unknown unit: {from_unit}")

def convert_from_si(value: float, to_unit: str) -> float:
    if to_unit in length_units:
        return value / length_units[to_unit]
    elif to_unit in modulus_units:
        return value / modulus_units[to_unit]
    elif to_unit in density_units:
        return value / density_units[to_unit]
    else:
        raise ValueError(f"Unsupported or unknown unit: {to_unit}")
