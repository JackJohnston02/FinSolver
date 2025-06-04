# finsolver/units.py

def convert_to_si(value: float, from_unit: str) -> float:
    """
    Convert a given value to SI units based on the unit type.

    Parameters:
    - value: The numeric value to convert.
    - from_unit: The unit of the input value (e.g., 'mm', 'GPa').

    Returns:
    - The value converted to SI units (meters or Pascals).

    Raises:
    - ValueError: If the unit is unsupported.
    """
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

    if from_unit in length_units:
        return value * length_units[from_unit]
    elif from_unit in modulus_units:
        return value * modulus_units[from_unit]
    else:
        raise ValueError(f"Unsupported or unknown unit: {from_unit}")

