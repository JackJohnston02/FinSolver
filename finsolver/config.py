# finsolver/config.py

from dataclasses import dataclass, field
from typing import List


@dataclass
class FinLayerData:
    material: str = "Carbon Fiber"
    E: float = 70e9             # Young's modulus in Pascals (Pa)
    G: float = 5e9              # Shear modulus in Pascals (Pa)
    thickness: float = 0.003    # Thickness in meters (m)
    root_chord: float = 0.2     # Root chord in meters (m)
    tip_chord: float = 0.06     # Tip chord in meters (m)


@dataclass
class FinConfig:
    body_tube_od: float = 0.08  # Body tube outer diameter in meters (m)
    num_fins: int = 4
    core: FinLayerData = field(default_factory=FinLayerData)
    layers: List[FinLayerData] = field(default_factory=list)
