from dataclasses import dataclass, field, asdict
from typing import List


@dataclass
class FinLayerData:
    material: str = "Carbon Fiber"
    E: float = 70e9                # Young's Modulus, Pa
    G: float = 5e9                 # Shear Modulus, Pa
    thickness: float = 0.003       # meters
    root_chord: float = 0.2        # meters
    height: float = 0.1            # meters
    sweep_length: float = 0.05     # meters
    tip_chord: float = 0.06        # meters
    density: float = 1600          # kg/m^3
    poisson_ratio: float = 0.3     # dimensionless

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(data):
        return FinLayerData(
            material=data.get("material", "Carbon Fiber"),
            E=data.get("E", 70e9),
            G=data.get("G", 5e9),
            thickness=data.get("thickness", 0.003),
            root_chord=data.get("root_chord", 0.2),
            tip_chord=data.get("tip_chord", 0.06),
            density=data.get("density", 1600),
            poisson_ratio=data.get("poisson_ratio", 0.3)
        )


@dataclass
class FinConfig:
    body_tube_od: float = 0.08     # meters
    num_fins: int = 4
    core: FinLayerData = field(default_factory=FinLayerData)
    layers: List[FinLayerData] = field(default_factory=list)

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
