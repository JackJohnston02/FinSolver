import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QFormLayout, QLineEdit, QPushButton, QListWidget, QListWidgetItem,
    QMenuBar, QMenu, QFrame, QMessageBox, QComboBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QKeyEvent
from time import time
from finsolver.config import FinConfig, FinLayerData
from finsolver.units import convert_to_si


class FinSolverMainWindow(QMainWindow):
    def __init__(self):
        self.last_delete_time = 0
        super().__init__()
        self.setWindowTitle("FinSolver – Fin Flutter Analysis")
        self.setGeometry(100, 100, 1000, 600)
        self.user_clicked_add = False
        self.config = FinConfig()
        self.init_ui()

    def init_ui(self):
        self.init_menu()

        main_widget = QWidget()
        main_layout = QHBoxLayout()

        self.nav_list = QListWidget()
        self.general_item = QListWidgetItem("General Settings")
        self.core_item = QListWidgetItem("Core Layer")
        self.add_layer_item = QListWidgetItem("+ Add Layer")

        self.nav_list.addItem(self.general_item)
        self.nav_list.addItem(self.core_item)
        self.nav_list.addItem(self.add_layer_item)
        self.nav_list.currentItemChanged.connect(self.display_editor)
        self.nav_list.viewport().installEventFilter(self)
        self.nav_list.installEventFilter(self)

        self.editor_panel = QVBoxLayout()
        self.editor_form = QFormLayout()
        self.editor_widget = QWidget()
        self.editor_widget.setLayout(self.editor_form)

        self.delete_button = QPushButton("Delete This Layer")
        self.delete_button.clicked.connect(self.delete_selected_layer)
        self.delete_button.hide()

        self.editor_panel.addWidget(self.editor_widget)
        self.editor_panel.addWidget(self.delete_button)

        left_side = QHBoxLayout()
        left_side.addWidget(self.nav_list)

        editor_container = QWidget()
        editor_container.setLayout(self.editor_panel)
        left_side.addWidget(editor_container)

        left_widget = QWidget()
        left_widget.setLayout(left_side)

        self.visual_label = QLabel("[Layup Visualization Placeholder]")
        self.visual_label.setFrameShape(QFrame.Shape.Box)
        self.visual_label.setMinimumHeight(300)
        self.visual_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        visual_widget = QWidget()
        visual_layout = QVBoxLayout()
        visual_layout.addWidget(self.visual_label)
        visual_widget.setLayout(visual_layout)

        main_layout.addWidget(left_widget, 2)
        main_layout.addWidget(visual_widget, 2)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        self.display_editor(self.nav_list.currentItem())

    def eventFilter(self, source, event):
        if source == self.nav_list.viewport() and event.type() == event.Type.MouseButtonPress:
            item = self.nav_list.itemAt(event.pos())
            if item == self.add_layer_item:
                self.user_clicked_add = True
        elif source == self.nav_list and isinstance(event, QKeyEvent):
            if event.key() == Qt.Key.Key_Delete:
                now = time()
                if now - self.last_delete_time > 0.3:
                    self.last_delete_time = now
                    self.delete_selected_layer()
                return True
        return super().eventFilter(source, event)

    def init_menu(self):
        menubar = self.menuBar()
        menubar.addMenu("File")
        menubar.addMenu("Properties")
        run_menu = menubar.addMenu("Run")
        run_action = QAction("Run Simulation", self)
        run_action.triggered.connect(self.run_simulation)
        run_menu.addAction(run_action)

    def make_input_with_units(self, value, units_list, default_unit, setter):
        container = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        input_field = QLineEdit(str(value))
        unit_box = QComboBox()
        unit_box.addItems(units_list)
        unit_box.setCurrentText(default_unit)

        def on_change():
            try:
                val = float(input_field.text())
                si_val = convert_to_si(val, unit_box.currentText())
                setter(si_val)
            except ValueError:
                pass

        input_field.editingFinished.connect(on_change)
        unit_box.activated.connect(lambda _: on_change())

        layout.addWidget(input_field)
        layout.addWidget(unit_box)
        container.setLayout(layout)
        return container

    def display_editor(self, current, previous=None):
        if not current:
            return

        name = current.text()
        print(f"Selected: {name}")

        if name == "+ Add Layer":
            if self.user_clicked_add:
                self.add_new_layer()
            self.user_clicked_add = False
            return

        while self.editor_form.rowCount():
            self.editor_form.removeRow(0)

        if name == "General Settings":
            self.editor_form.addRow("Body Tube OD:", self.make_input_with_units(
                self.config.body_tube_od, ["mm", "cm", "in", "m"], "mm", lambda val: setattr(self.config, "body_tube_od", val)))
            self.editor_form.addRow("Number of Fins:", QLineEdit(str(self.config.num_fins)))
            self.delete_button.hide()

        elif name == "Core Layer":
            core = self.config.core
            self.editor_form.addRow("Material:", QLineEdit(core.material))
            self.editor_form.addRow("Young's Modulus:", self.make_input_with_units(core.E, ["GPa", "MPa"], "GPa", lambda val: setattr(core, "E", val)))
            self.editor_form.addRow("Shear Modulus:", self.make_input_with_units(core.G, ["GPa", "MPa"], "GPa", lambda val: setattr(core, "G", val)))
            self.editor_form.addRow("Thickness:", self.make_input_with_units(core.thickness, ["mm", "cm", "in", "m"], "mm", lambda val: setattr(core, "thickness", val)))
            self.editor_form.addRow("Root Chord:", self.make_input_with_units(core.root_chord, ["mm", "cm", "in", "m"], "mm", lambda val: setattr(core, "root_chord", val)))
            self.editor_form.addRow("Tip Chord:", self.make_input_with_units(core.tip_chord, ["mm", "cm", "in", "m"], "mm", lambda val: setattr(core, "tip_chord", val)))
            self.delete_button.hide()

        elif name.startswith("Layer"):
            index = self.get_layer_index(name)
            if index is not None and 0 <= index < len(self.config.layers):
                layer = self.config.layers[index]
                self.editor_form.addRow("Material:", QLineEdit(layer.material))
                self.editor_form.addRow("Young's Modulus:", self.make_input_with_units(layer.E, ["GPa", "MPa"], "GPa", lambda val: setattr(layer, "E", val)))
                self.editor_form.addRow("Shear Modulus:", self.make_input_with_units(layer.G, ["GPa", "MPa"], "GPa", lambda val: setattr(layer, "G", val)))
                self.editor_form.addRow("Thickness:", self.make_input_with_units(layer.thickness, ["mm", "cm", "in", "m"], "mm", lambda val: setattr(layer, "thickness", val)))
                self.editor_form.addRow("Root Chord:", self.make_input_with_units(layer.root_chord, ["mm", "cm", "in", "m"], "mm", lambda val: setattr(layer, "root_chord", val)))
                self.editor_form.addRow("Tip Chord:", self.make_input_with_units(layer.tip_chord, ["mm", "cm", "in", "m"], "mm", lambda val: setattr(layer, "tip_chord", val)))
            self.delete_button.show()
        else:
            self.delete_button.hide()

    def get_layer_index(self, name):
        try:
            return int(name.replace("Layer ", "")) - 1
        except ValueError:
            return None

    def add_new_layer(self):
        self.config.layers.append(FinLayerData())
        new_item = QListWidgetItem(f"Layer {len(self.config.layers)}")
        insert_index = self.nav_list.row(self.add_layer_item)
        self.nav_list.insertItem(insert_index, new_item)
        self.nav_list.setCurrentItem(new_item)

    def delete_selected_layer(self):
        current_item = self.nav_list.currentItem()
        if current_item and current_item.text().startswith("Layer"):
            index = self.get_layer_index(current_item.text())
            if index is not None and 0 <= index < len(self.config.layers):
                del self.config.layers[index]
                self.nav_list.takeItem(self.nav_list.row(current_item))
                self.renumber_layers()

                def update_selection():
                    if self.config.layers:
                        self.nav_list.setCurrentRow(2 + min(index, len(self.config.layers) - 1))
                    else:
                        self.nav_list.setCurrentItem(self.general_item)

                QTimer.singleShot(0, update_selection)

    def renumber_layers(self):
        count = 1
        for i in range(self.nav_list.count()):
            item = self.nav_list.item(i)
            if item.text().startswith("Layer"):
                item.setText(f"Layer {count}")
                count += 1

    def run_simulation(self):
        QMessageBox.information(self, "Simulation", "Flutter analysis would run here.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FinSolverMainWindow()
    window.show()
    sys.exit(app.exec())
