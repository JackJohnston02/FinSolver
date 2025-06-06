[1mdiff --git a/finsolver/config.py b/finsolver/config.py[m
[1mindex ce12bf6..64d7a87 100644[m
[1m--- a/finsolver/config.py[m
[1m+++ b/finsolver/config.py[m
[36m@@ -4,57 +4,88 @@[m [mfrom typing import List[m
 [m
 @dataclass[m
 class FinLayerData:[m
[31m-    material: str = "Carbon Fiber"[m
[31m-    E: float = 70e9[m
[31m-    G: float = 5e9[m
[31m-    thickness: float = 0.003[m
[32m+[m[32m    material: str = "Plywood"            # Realistic default core material[m
[32m+[m[32m    E: float = 4e9                       # Young's modulus for birch plywood[m
[32m+[m[32m    G: float = 1.5e9                    # Shear modulus estimate[m
[32m+[m[32m    thickness: float = 0.003             # 3 mm thick core[m
     root_chord: float = 0.2[m
[31m-    tip_chord: float = 0.06[m
[32m+[m[32m    tip_chord: float = 0.1[m
     height: float = 0.1[m
     sweep_length: float = 0.05[m
[31m-    density: float = 1600.0[m
[32m+[m[32m    density: float = 700.0               # Plywood density[m
     poisson_ratio: float = 0.3[m
     instep_enabled: bool = False[m
     instep_value: float = 0.0[m
 [m
[31m-[m
     def to_dict(self):[m
         return asdict(self)[m
 [m
     @staticmethod[m
     def from_dict(data):[m
         return FinLayerData([m
[31m-            material=data.get("material", "Carbon Fiber"),[m
[31m-            E=data.get("E", 70e9),[m
[31m-            G=data.get("G", 5e9),[m
[32m+[m[32m            material=data.get("material", "Plywood"),[m
[32m+[m[32m            E=data.get("E", 8000e6),[m
[32m+[m[32m            G=data.get("G", 4e9),[m
             thickness=data.get("thickness", 0.003),[m
             root_chord=data.get("root_chord", 0.2),[m
[31m-            tip_chord=data.get("tip_chord", 0.06),[m
[31m-            density=data.get("density", 1600),[m
[32m+[m[32m            tip_chord=data.get("tip_chord", 0.1),[m
[32m+[m[32m            height=data.get("height", 0.1),[m
[32m+[m[32m            sweep_length=data.get("sweep_length", 0.05),[m
[32m+[m[32m            density=data.get("density", 700.0),[m
[32m+[m[32m            poisson_ratio=data.get("poisson_ratio", 0.3),[m
[32m+[m[32m            instep_enabled=data.get("instep_enabled", False),[m
[32m+[m[32m            instep_value=data.get("instep_value", 0.0)[m
[32m+[m[32m        )[m
[32m+[m
[32m+[m
[32m+[m[32m@dataclass[m
[32m+[m[32mclass FilletMaterial:[m
[32m+[m[32m    material: str = "Epoxy"[m
[32m+[m[32m    density: float = 1200.0[m
[32m+[m[32m    E: float = 2e9[m
[32m+[m[32m    G: float = 1e9[m
[32m+[m[32m    poisson_ratio: float = 0.3[m
[32m+[m
[32m+[m[32m    def to_dict(self):[m
[32m+[m[32m        return asdict(self)[m
[32m+[m
[32m+[m[32m    @staticmethod[m
[32m+[m[32m    def from_dict(data):[m
[32m+[m[32m        return FilletMaterial([m
[32m+[m[32m            material=data.get("material", "Epoxy"),[m
[32m+[m[32m            density=data.get("density", 1200.0),[m
[32m+[m[32m            E=data.get("E", 2e9),[m
[32m+[m[32m            G=data.get("G", 1e9),[m
             poisson_ratio=data.get("poisson_ratio", 0.3)[m
         )[m
 [m
 [m
 @dataclass[m
 class FinConfig:[m
[31m-    body_tube_od: float = 0.08     # meters[m
[32m+[m[32m    body_tube_od: float = 0.08[m
[32m+[m[32m    fillet_radius: float = 0.02[m
     num_fins: int = 4[m
     core: FinLayerData = field(default_factory=FinLayerData)[m
     layers: List[FinLayerData] = field(default_factory=list)[m
[32m+[m[32m    fillet: FilletMaterial = field(default_factory=FilletMaterial)[m
 [m
     def to_dict(self):[m
         return {[m
             "body_tube_od": self.body_tube_od,[m
[32m+[m[32m            "fillet_radius": self.fillet_radius,[m
             "num_fins": self.num_fins,[m
             "core": self.core.to_dict(),[m
[31m-            "layers": [layer.to_dict() for layer in self.layers][m
[32m+[m[32m            "layers": [layer.to_dict() for layer in self.layers],[m
[32m+[m[32m            "fillet": self.fillet.to_dict()[m
         }[m
 [m
     @staticmethod[m
     def from_dict(data):[m
         return FinConfig([m
             body_tube_od=data.get("body_tube_od", 0.08),[m
[32m+[m[32m            fillet_radius=data.get("fillet_radius", 0.02),[m
             num_fins=data.get("num_fins", 4),[m
             core=FinLayerData.from_dict(data.get("core", {})),[m
[31m-            layers=[FinLayerData.from_dict(l) for l in data.get("layers", [])][m
[32m+[m[32m            layers=[FinLayerData.from_dict(l) for l in data.get("layers", [])],[m
[32m+[m[32m            fillet=FilletMaterial.from_dict(data.get("fillet", {}))[m
         )[m
[1mdiff --git a/finsolver/gui.py b/finsolver/gui.py[m
[1mindex 9c72224..19fe9de 100644[m
[1m--- a/finsolver/gui.py[m
[1m+++ b/finsolver/gui.py[m
[36m@@ -12,7 +12,7 @@[m [mfrom time import time[m
 from finsolver.config import FinConfig, FinLayerData[m
 from finsolver.units import convert_to_si, convert_from_si[m
 from finsolver.visual import FinCrossSectionView[m
[31m-[m
[32m+[m[32mfrom finsolver.flutter_analysis import calculate_flutter[m
 [m
 from PyQt6.QtWidgets import QFileDialog[m
 import json[m
[36m@@ -264,8 +264,18 @@[m [mclass FinSolverMainWindow(QMainWindow):[m
             self.editor_form.removeRow(0)[m
 [m
         if name == "General Settings":[m
[32m+[m[32m            # Subtitle for Geometry[m
[32m+[m[32m            subtitle_geometry = QLabel("Geometry:")[m
[32m+[m[32m            subtitle_geometry.setStyleSheet("font-weight: bold; margin-top: 10px; margin-left: -4px;")[m
[32m+[m[32m            self.editor_form.addRow(subtitle_geometry)[m
[32m+[m
             self.editor_form.addRow("Body Tube OD:", self.make_input_with_units([m
                 self.config.body_tube_od, ["mm", "cm", "in", "m"], "mm", lambda val: setattr(self.config, "body_tube_od", val)))[m
[32m+[m[41m            [m
[32m+[m[32m            self.editor_form.addRow("Fillet Radius:", self.make_input_with_units([m
[32m+[m[32m                self.config.fillet_radius, ["mm", "cm", "in", "m"], "mm", lambda val: setattr(self.config, "fillet_radius", val)))[m
[32m+[m[41m            [m
[32m+[m[41m            [m
             num_fins_input = QLineEdit(str(self.config.num_fins))[m
             num_fins_input.editingFinished.connect(lambda: ([m
                 setattr(self.config, "num_fins", int(num_fins_input.text())),[m
[36m@@ -274,6 +284,18 @@[m [mclass FinSolverMainWindow(QMainWindow):[m
             self.editor_form.addRow("Number of Fins:", num_fins_input)[m
             self.delete_button.hide()[m
 [m
[32m+[m[32m            subtitle_geometry = QLabel("Fillet Properties:")[m
[32m+[m[32m            subtitle_geometry.setStyleSheet("font-weight: bold; margin-top: 10px; margin-left: -4px;")[m
[32m+[m[32m            self.editor_form.addRow(subtitle_geometry)[m
[32m+[m[41m            [m
[32m+[m[32m            self.editor_form.addRow("Material:", QLineEdit(self.config.fillet.material))[m
[32m+[m[32m            self.editor_form.addRow("Density:", self.make_input_with_units(self.config.fillet.density, ["kg/m³"], "kg/m³", lambda val: setattr(self.config.fillet, "density", val)))[m
[32m+[m[32m            self.editor_form.addRow("Young's Modulus:", self.make_input_with_units(self.config.fillet.E, ["GPa", "MPa"], "GPa", lambda val: setattr(self.config.fillet, "E", val)))[m
[32m+[m[32m            self.editor_form.addRow("Shear Modulus:", self.make_input_with_units(self.config.fillet.G, ["GPa", "MPa"], "GPa", lambda val: setattr(self.config.fillet, "G", val)))[m
[32m+[m[32m            self.editor_form.addRow("Poisson's Ratio:", QLineEdit(str(self.config.fillet.poisson_ratio)))[m
[32m+[m
[32m+[m
[32m+[m
         elif name == "Core Layer":[m
             core = self.config.core[m
 [m
[36m@@ -295,9 +317,10 @@[m [mclass FinSolverMainWindow(QMainWindow):[m
 [m
             self.editor_form.addRow("Material:", QLineEdit(core.material))[m
 [m
[32m+[m[32m            self.editor_form.addRow("Density:", self.make_input_with_units(core.density, ["kg/m³"], "kg/m³", lambda val: setattr(core, "density", val)))[m
             self.editor_form.addRow("Young's Modulus:", self.make_input_with_units(core.E, ["GPa", "MPa"], "GPa", lambda val: setattr(core, "E", val)))[m
             self.editor_form.addRow("Shear Modulus:", self.make_input_with_units(core.G, ["GPa", "MPa"], "GPa", lambda val: setattr(core, "G", val)))[m
[31m-            self.editor_form.addRow("Density:", self.make_input_with_units(core.density, ["kg/m³"], "kg/m³", lambda val: setattr(core, "density", val)))[m
[32m+[m
             self.editor_form.addRow("Poisson's Ratio:", QLineEdit(str(core.poisson_ratio)))[m
 [m
             self.delete_button.hide()[m
[36m@@ -420,10 +443,10 @@[m [mclass FinSolverMainWindow(QMainWindow):[m
                 mat_title.setStyleSheet("font-weight: bold; margin-top: 10px; margin-left: -4px;")[m
                 self.editor_form.addRow(mat_title)[m
 [m
[32m+[m[32m                self.editor_form.addRow("Density:", self.make_input_with_units(layer.density, ["kg/m³"], "kg/m³", lambda val: setattr(layer, "density", val)))[m
                 self.editor_form.addRow("Material:", QLineEdit(layer.material))[m
                 self.editor_form.addRow("Young's Modulus:", self.make_input_with_units(layer.E, ["GPa", "MPa"], "GPa", lambda val: setattr(layer, "E", val)))[m
                 self.editor_form.addRow("Shear Modulus:", self.make_input_with_units(layer.G, ["GPa", "MPa"], "GPa", lambda val: setattr(layer, "G", val)))[m
[31m-                self.editor_form.addRow("Density:", self.make_input_with_units(layer.density, ["kg/m³"], "kg/m³", lambda val: setattr(layer, "density", val)))[m
                 self.editor_form.addRow("Poisson's Ratio:", QLineEdit(str(layer.poisson_ratio)))[m
 [m
                 self.delete_button.show()[m
[36m@@ -492,18 +515,22 @@[m [mclass FinSolverMainWindow(QMainWindow):[m
                 count += 1[m
 [m
     def run_simulation(self):[m
[31m-        QMessageBox.information(self, "Simulation", "Flutter analysis would run here.")[m
[32m+[m[32m        try:[m
[32m+[m[32m            result_summary = calculate_flutter(self.config)[m
[32m+[m[32m            QMessageBox.information(self, "Flutter Simulation", result_summary)[m
[32m+[m[32m        except Exception as e:[m
[32m+[m[32m            QMessageBox.critical(self, "Simulation Error", f"An error occurred:\n{str(e)}")[m
 [m
     def apply_instep_geometry(self, layer_index: int):[m
         print(f"[DEBUG] apply_instep_geometry called for layer {layer_index}")[m
         """Apply geometry from the previous layer with the given instep offset."""[m
[31m-       [m
[32m+[m
         current_layer = self.config.layers[layer_index][m
[31m-       [m
[32m+[m
         if layer_index == 0:[m
             prev_layer = self.config.core[m
         else:[m
[31m-            prev_layer = prev_layer = self.config.layers[layer_index - 1][m
[32m+[m[32m            prev_layer = self.config.layers[layer_index - 1][m
 [m
         offset = current_layer.instep_value[m
 [m
[36m@@ -513,12 +540,10 @@[m [mclass FinSolverMainWindow(QMainWindow):[m
         current_layer.height = max(prev_layer.height - offset, 0)[m
         current_layer.sweep_length = max(prev_layer.sweep_length - offset, 0)[m
 [m
[31m-[m
[31m-[m
[31m-[m
         print(f"[INFO] Instep geometry applied to Layer {layer_index + 1}")[m
 [m
 [m
[32m+[m
 if __name__ == '__main__':[m
     app = QApplication(sys.argv)[m
     window = FinSolverMainWindow()[m
