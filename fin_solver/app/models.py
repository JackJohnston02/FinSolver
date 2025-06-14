from dataclasses import dataclass, field
from typing import Any, Optional, List


@dataclass
class Parameter:
    name: str
    value: Any
    units: Optional[str] = ""
    tooltip: Optional[str] = None
    min: Optional[float] = None
    max: Optional[float] = None
    step: Optional[float] = None


# ─── General Parameters ─────────────────────────────
@dataclass
class GeneralParameters:
    config_name: Parameter = Parameter(
        name="Configuration Name",
        value="Default Fin Config",
        tooltip="Give this configuration a name for saving/exporting"
    )


# ─── Geometry: Trapezoidal Fin ─────────────────────
@dataclass
class Trapezoid:
    base: Parameter = Parameter(
        name="Base Width",
        value=0.1,
        units="m",
        tooltip="Width of the base of the trapezoidal fin",
        min=0.01,
        step=0.005
    )
    top: Parameter = Parameter(
        name="Top Width",
        value=0.05,
        units="m",
        tooltip="Width of the top edge",
        min=0.01,
        step=0.005
    )
    height: Parameter = Parameter(
        name="Height",
        value=0.15,
        units="m",
        tooltip="Height (length) of the fin from base to top",
        min=0.01,
        step=0.005
    )


# ─── Isotropic Material Model ───────────────────────
@dataclass
class IsotropicMaterial:
    name: Parameter = Parameter(
        name="Material Name",
        value="Aluminium",
        tooltip="Name or ID of the material"
    )
    G: Parameter = Parameter(
        name="Shear Modulus (G)",
        value=27e9,
        units="Pa",
        tooltip="Shear modulus of the material",
        min=1e9,
        step=1e9
    )
    rho: Parameter = Parameter(
        name="Density (ρ)",
        value=2700,
        units="kg/m³",
        tooltip="Density of the material",
        min=500,
        step=50
    )


# ─── Core Object ────────────────────────────────────
@dataclass
class Core:
    name: str = "Core Fin Section"
    geometry: Trapezoid = Trapezoid()
    material: IsotropicMaterial = IsotropicMaterial()


# ─── Layer (same structure as Core, but for add-ons) ─
@dataclass
class Layer:
    name: str = "Layer"
    instep_from_previous_layer: bool = False
    geometry: Trapezoid = Trapezoid()
    material: IsotropicMaterial = IsotropicMaterial()


# ─── Top-Level Configuration ───────────────────────
@dataclass
class Config:
    general_parameters: GeneralParameters = GeneralParameters()
    core: Core = Core()
    layers: List[Layer] = field(default_factory=list)
