from dataclasses import dataclass, field, asdict
from typing import List


@dataclass
class FinLayerData:
    material: str = "Plywood"            # Realistic default core material
    E: float = 4e9                       # Young's modulus for birch plywood
    G: float = 1.5e9                    # Shear modulus estimate
    thickness: float = 0.003             # 3 mm thick core
    root_chord: float = 0.2
    tip_chord: float = 0.1
    height: float = 0.1
    sweep_length: float = 0.05
    density: float = 700.0               # Plywood density
    poisson_ratio: float = 0.3
    instep_enabled: bool = False
    instep_value: float = 0.0

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(data):
        return FinLayerData(
            material=data.get("material", "Plywood"),
            E=data.get("E", 8000e6),
            G=data.get("G", 4e9),
            thickness=data.get("thickness", 0.003),
            root_chord=data.get("root_chord", 0.2),
            tip_chord=data.get("tip_chord", 0.1),
            height=data.get("height", 0.1),
            sweep_length=data.get("sweep_length", 0.05),
            density=data.get("density", 700.0),
            poisson_ratio=data.get("poisson_ratio", 0.3),
            instep_enabled=data.get("instep_enabled", False),
            instep_value=data.get("instep_value", 0.0)
        )


@dataclass
class FilletMaterial:
    material: str = "Epoxy"
    density: float = 1200.0
    E: float = 2e9
    G: float = 1e9
    poisson_ratio: float = 0.3

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(data):
        return FilletMaterial(
            material=data.get("material", "Epoxy"),
            density=data.get("density", 1200.0),
            E=data.get("E", 2e9),
            G=data.get("G", 1e9),
            poisson_ratio=data.get("poisson_ratio", 0.3)
        )


@dataclass
class FinConfig:
    body_tube_od: float = 0.08
    fillet_radius: float = 0.02
    num_fins: int = 4
    core: FinLayerData = field(default_factory=FinLayerData)
    layers: List[FinLayerData] = field(default_factory=list)
    fillet: FilletMaterial = field(default_factory=FilletMaterial)

    def to_dict(self):
        return {
            "body_tube_od": self.body_tube_od,
            "fillet_radius": self.fillet_radius,
            "num_fins": self.num_fins,
            "core": self.core.to_dict(),
            "layers": [layer.to_dict() for layer in self.layers],
            "fillet": self.fillet.to_dict()
        }

    @staticmethod
    def from_dict(data):
        return FinConfig(
            body_tube_od=data.get("body_tube_od", 0.08),
            fillet_radius=data.get("fillet_radius", 0.02),
            num_fins=data.get("num_fins", 4),
            core=FinLayerData.from_dict(data.get("core", {})),
            layers=[FinLayerData.from_dict(l) for l in data.get("layers", [])],
            fillet=FilletMaterial.from_dict(data.get("fillet", {}))
        )
