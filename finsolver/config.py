# finsolver/config.py

from dataclasses import dataclass, field, asdict
from typing import List


@dataclass
class FinLayerData:
    material: str = "Carbon Fiber"
    E: float = 70e9
    G: float = 5e9
    thickness: float = 0.003
    root_chord: float = 0.2
    tip_chord: float = 0.06

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(data):
        return FinLayerData(**data)


@dataclass
class FinConfig:
    body_tube_od: float = 0.08
    num_fins: int = 4
    core: FinLayerData = field(default_factory=FinLayerData)
    layers: list[FinLayerData] = field(default_factory=list)

    def to_dict(self):
        return {
            "body_tube_od": self.body_tube_od,
            "num_fins": self.num_fins,
            "core": self.core.to_dict(),
            "layers": [layer.to_dict() for layer in self.layers]
        }

    @staticmethod
    def from_dict(data):
        return FinConfig(
            body_tube_od=data.get("body_tube_od", 0.08),
            num_fins=data.get("num_fins", 4),
            core=FinLayerData.from_dict(data.get("core", {})),
            layers=[FinLayerData.from_dict(l) for l in data.get("layers", [])]
        )
