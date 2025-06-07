from dataclasses import dataclass, field
from typing import List

@dataclass
class GeneralSettings:
    body_tube_od: float = 0.08  # meters
    number_of_fins: int = 4

@dataclass
class Layer:
    material: str = "Carbon Fiber"
    E: float = 70e9             # Young's Modulus, Pa
    G: float = 5e9              # Shear Modulus, Pa
    thickness: float = 0.003    # meters
    root_chord: float = 0.2     # meters
    tip_chord: float = 0.06     # meters
    height: float = 0.06        # meters
    density: float = 1600       # kg/m^3
    poisson_ratio: float = 0.3  # dimensionless

@dataclass
class FinConfig:
    general: GeneralSettings = GeneralSettings()
    core_layer: Layer = Layer()
    additional_layers: List[Layer] = field(default_factory=list)
