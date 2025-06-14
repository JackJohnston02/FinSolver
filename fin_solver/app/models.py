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


# ─── General Parameters ──────────────────────────
@dataclass
class GeneralParameters:
    config_name: Parameter = field(default_factory=lambda: Parameter(
        name="Configuration Name",
        value="Default Fin Config",
        tooltip="Give this configuration a name for saving/exporting"
    ))

    number_of_fins: Parameter = field(default_factory=lambda: Parameter(
        name="Number of Fins",
        value=3,
        tooltip="How many fins are evenly spaced around the rocket body",
        min=1,
        max=12,
        step=1
    ))

    body_tube_OD: Parameter = field(default_factory=lambda: Parameter(
        name="Body Tube Outer Diameter",
        value=0.1,
        units="m",
        tooltip="Outer diameter of the rocket body tube",
        min=0.01,
        max=1.0,
        step=0.005
    ))


# ─── Geometry: Trapezoidal Fin ────────────────
@dataclass
class Trapezoid:
    root_chord: Parameter = field(default_factory=lambda: Parameter(
        name="Root Chord",
        value=0.1,
        units="m",
        tooltip="Root Chord of the trapezoidal fin",
        min=0.01,
        step=0.005
    ))
    tip_chord: Parameter = field(default_factory=lambda: Parameter(
        name="Tip Chord",
        value=0.05,
        units="m",
        tooltip="Tip Chord length of the trapezoidal fin",
        min=0.01,
        step=0.005
    ))
    height: Parameter = field(default_factory=lambda: Parameter(
        name="Height",
        value=0.15,
        units="m",
        tooltip="Height (length) of the fin from root to tip",
        min=0.01,
        step=0.005
    ))
    sweep_length: Parameter = field(default_factory=lambda: Parameter(
        name="Sweep Length",
        value=0.15,
        units="m",
        tooltip="TODO",
        min=0.0,
        max=10.0,
        step=0.001
    ))
    thickness: Parameter = field(default_factory=lambda: Parameter(
        name="Thickness",
        value=0.001,
        units="m",
        tooltip="TODO",
        min=0.0001,
        max=10.00,
        step=0.001
    ))


# ─── Isotropic Material Model ───────────────
@dataclass
class IsotropicMaterial:
    name: Parameter = field(default_factory=lambda: Parameter(
        name="Material Name",
        value="Aluminium",
        tooltip="Name or ID of the material"
    ))
    G: Parameter = field(default_factory=lambda: Parameter(
        name="Shear Modulus (G)",
        value=27e9,
        units="Pa",
        tooltip="Shear modulus of the material",
        min=1e9,
        step=1e9
    ))
    rho: Parameter = field(default_factory=lambda: Parameter(
        name="Density (ρ)",
        value=2700,
        units="kg/m³",
        tooltip="Density of the material",
        min=500,
        step=50
    ))


# ─── Core Object ───────────────────────
@dataclass
class Core:
    name: str = "Core Fin Section"
    geometry: Trapezoid = field(default_factory=Trapezoid)
    material: IsotropicMaterial = field(default_factory=IsotropicMaterial)


# ─── Layer (same structure as Core, but for add-ons) ──────────────
@dataclass
class Layer:
    name: str = "Layer"
    instep_from_previous_layer: bool = False
    instep_distance: Parameter = field(default_factory=lambda: Parameter(
        name="Instep Distance",
        value=0.0,
        units="m",
        tooltip="Distance to instep this layer from the layer below",
        min=0.0,
        step=0.001
    ))
    geometry: Trapezoid = field(default_factory=Trapezoid)
    material: IsotropicMaterial = field(default_factory=IsotropicMaterial)

    def apply_instep(self, base_geometry: Trapezoid):
        """
        Updates this layer's geometry based on the given base layer geometry,
        reducing root and tip chord by 2× instep distance.
        """
        d = self.instep_distance.value
        self.geometry.root_chord.value = max(0.0, base_geometry.root_chord.value - 2 * d)
        self.geometry.tip_chord.value = max(0.0, base_geometry.tip_chord.value - 2 * d)
        self.geometry.height.value = base_geometry.height.value
        self.geometry.sweep_length.value = base_geometry.sweep_length.value


# ─── Top-Level Configuration ───────────────
@dataclass
class Config:
    general_parameters: GeneralParameters = field(default_factory=GeneralParameters)
    core: Core = field(default_factory=Core)
    layers: List[Layer] = field(default_factory=list)
