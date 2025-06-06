from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPen, QPolygonF
from PyQt6.QtCore import Qt, QPointF
from finsolver.config import FinLayerData
import numpy as np

class FinCrossSectionView(QWidget):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setMinimumHeight(300)
        self.selected_layer_index = -1  # -1 = none, 0 = core, 1+ = user layers

    def set_selected_layer(self, index: int):
        self.selected_layer_index = index
        self.update()

    def set_config(self, config):
        self.config = config
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), Qt.GlobalColor.white)

        origin_x = self.width() // 2
        origin_y = self.height() // 2
        y_offset = 0

        def draw_layer(layer: FinLayerData, is_selected: bool, y_offset: float):
            root = -layer.root_chord * 1000
            tip = -layer.tip_chord * 1000
            height = layer.height * 1000
            sweep = -layer.sweep_length * 1000
            thickness = -layer.thickness * 1000

            n_fins = self.config.num_fins
            core_thickness = self.config.core.thickness
            body_tube_od = self.config.body_tube_od

            body_tube_arc = ((np.pi * body_tube_od - n_fins * core_thickness) / n_fins) * 1000

            # Create polygon points
            points = [
                QPointF(origin_x - body_tube_arc / 2 - height, origin_y + root / 2 - sweep + y_offset),
                QPointF(origin_x - body_tube_arc / 2, origin_y + root / 2 + y_offset),
                QPointF(origin_x + body_tube_arc / 2, origin_y + root / 2 + y_offset),
                QPointF(origin_x + body_tube_arc / 2 + height, origin_y + root / 2 - sweep + y_offset),
                QPointF(origin_x + body_tube_arc / 2 + height, origin_y + root / 2 - sweep - tip + y_offset),
                QPointF(origin_x + body_tube_arc / 2, origin_y - root / 2 + y_offset),
                QPointF(origin_x - body_tube_arc / 2, origin_y - root / 2 + y_offset),
                QPointF(origin_x - body_tube_arc / 2 - height, origin_y + root / 2 - sweep - tip + y_offset)
            ]

            poly = QPolygonF(points)
            brush_color = QColor(100, 160, 255) if is_selected else QColor(255, 255, 255)

            painter.setBrush(brush_color)
            painter.setPen(QPen(Qt.GlobalColor.black, 1))
            painter.drawPolygon(poly)

        # Draw core layer
        draw_layer(self.config.core, self.selected_layer_index == 0, y_offset)

        # Draw additional layers
        for i, layer in enumerate(self.config.layers):
            draw_layer(layer, self.selected_layer_index == i + 1, y_offset)
