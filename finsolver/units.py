# finsolver/units.py

# Shared unit dictionaries
UNIT_FACTORS = {
    "length": {
        "mm": 1e-3,
        "cm": 1e-2,
        "m": 1.0,
        "in": 0.0254,
        "ft": 0.3048,
    },
    "modulus": {
        "GPa": 1e9,
        "MPa": 1e6,
    }
}

# Flatten all units for reverse lookup
ALL_UNITS = {**UNIT_FACTORS["length"], **UNIT_FACTORS["modulus"]}


def convert_to_si(value: float, from_unit: str) -> float:
    """
    Convert a value to SI units using the shared unit dictionary.
    """
    if from_unit not in ALL_UNITS:
        raise ValueError(f"Unsupported or unknown unit: {from_unit}")
    return value * ALL_UNITS[from_unit]


def convert_from_si(value: float, to_unit: str) -> float:
    """
    Convert a value from SI units using the shared unit dictionary.
    """
    if to_unit not in ALL_UNITS:
        raise ValueError(f"Unsupported or unknown unit: {to_unit}")
    return value / ALL_UNITS[to_unit]
