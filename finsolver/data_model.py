from dataclasses import dataclass, field
from typing import List

@dataclass
class GeneralSettings:
    body_tube_od: float = 0.08  # meters
    number_of_fins: int = 4

@dataclass
class Layer:
    material: str
    E: float               # Pa
    G: float               # Pa
    thickness: float       # m
    root_chord: float      # m
    tip_chord: float       # m

@dataclass
class FinConfig:
    general: GeneralSettings = GeneralSettings()
    core_layer: Layer = Layer("Carbon Fiber", 70e9, 5e9, 0.003, 0.2, 0.06)
    additional_layers: List[Layer] = field(default_factory=list)
