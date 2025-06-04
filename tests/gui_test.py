import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QFormLayout, QLineEdit, QPushButton, QListWidget, QListWidgetItem,
    QMenuBar, QMenu, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QKeyEvent
from PyQt6.QtCore import QTimer

from time import time



class FinSolverMainWindow(QMainWindow):
    def __init__(self):
        self.last_delete_time = 0
        super().__init__()
        self.setWindowTitle("FinSolver – Fin Flutter Analysis")
        self.setGeometry(100, 100, 1000, 600)
        self.user_clicked_add = False
        self.layers = []  # Store data for each layer
        self.deletion_lock = False
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

        self.visual_label = QLabel("[Layup Visualization Placeholder]")
        self.visual_label.setFrameShape(QFrame.Shape.Box)
        self.visual_label.setMinimumHeight(300)
        self.visual_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.editor_panel.addWidget(self.editor_widget)
        self.editor_panel.addWidget(self.delete_button)
        self.editor_panel.addWidget(self.visual_label)

        right_widget = QWidget()
        right_widget.setLayout(self.editor_panel)

        main_layout.addWidget(self.nav_list, 1)
        main_layout.addWidget(right_widget, 3)

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
                if now - self.last_delete_time > 0.3:  # 300ms lockout
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
            self.editor_form.addRow("Body Tube OD (mm):", QLineEdit("80"))
            self.editor_form.addRow("Number of Fins:", QLineEdit("4"))
            self.delete_button.hide()

        elif name == "Core Layer":
            self.editor_form.addRow("Material:", QLineEdit("Carbon Fiber"))
            self.editor_form.addRow("Young's Modulus (GPa):", QLineEdit("70"))
            self.editor_form.addRow("Shear Modulus (GPa):", QLineEdit("5"))
            self.editor_form.addRow("Thickness (mm):", QLineEdit("3"))
            self.editor_form.addRow("Root Chord (mm):", QLineEdit("200"))
            self.editor_form.addRow("Tip Chord (mm):", QLineEdit("60"))
            self.delete_button.hide()

        elif name.startswith("Layer"):
            index = self.get_layer_index(name)
            if index is not None and 0 <= index < len(self.layers):
                layer = self.layers[index]
                self.editor_form.addRow("Material:", QLineEdit(layer.get("material", "")))
                self.editor_form.addRow("Young's Modulus (GPa):", QLineEdit(str(layer.get("E", ""))))
                self.editor_form.addRow("Shear Modulus (GPa):", QLineEdit(str(layer.get("G", ""))))
                self.editor_form.addRow("Thickness (mm):", QLineEdit(str(layer.get("thickness", ""))))
                self.editor_form.addRow("Root Chord (mm):", QLineEdit(str(layer.get("root_chord", ""))))
                self.editor_form.addRow("Tip Chord (mm):", QLineEdit(str(layer.get("tip_chord", ""))))
            self.delete_button.show()
        else:
            self.delete_button.hide()

    def get_layer_index(self, name):
        try:
            return int(name.replace("Layer ", "")) - 1
        except ValueError:
            return None

    def add_new_layer(self):
        new_layer = {
            "material": "Carbon Fiber",
            "E": 70,
            "G": 5,
            "thickness": 3,
            "root_chord": 200,
            "tip_chord": 60
        }
        self.layers.append(new_layer)
        new_item = QListWidgetItem(f"Layer {len(self.layers)}")
        insert_index = self.nav_list.row(self.add_layer_item)
        self.nav_list.insertItem(insert_index, new_item)
        self.nav_list.setCurrentItem(new_item)

    def delete_selected_layer(self):
        current_item = self.nav_list.currentItem()
        if current_item and current_item.text().startswith("Layer"):
            index = self.get_layer_index(current_item.text())
            if index is not None and 0 <= index < len(self.layers):
                del self.layers[index]
                self.nav_list.takeItem(self.nav_list.row(current_item))
                self.renumber_layers()

                def update_selection():
                    if self.layers:
                        self.nav_list.setCurrentRow(2 + min(index, len(self.layers) - 1))
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
