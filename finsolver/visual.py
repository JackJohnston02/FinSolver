# finsolver/visual.py

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
        self.selected_layer_index = -1  # -1 for none, 0 for core, 1+ for additional layers

    def set_selected_layer(self, index: int):
        self.selected_layer_index = index
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), Qt.GlobalColor.white)

        config = self.config
        scale = 1000

        origin_x = self.width() // 2
        origin_y = self.height() // 2
        y_offset = 0

        def draw_layer(config: float, layer: FinLayerData, offset_y: float, is_selected: bool, scale: float):
            scale = 1000
            root = -layer.root_chord * 1000
            tip = -layer.tip_chord * 1000
            height = layer.height * 1000
            sweep = -layer.sweep_length * 1000
            thickness = -layer.thickness * 1000

            n_fins = config.num_fins
            print("number of fins!", n_fins)

            core_thickness = config.core.thickness

            body_tube_od = config.body_tube_od

            body_tube_arc = (((np.pi * body_tube_od) - (n_fins * core_thickness))/n_fins ) *1000

            


            points = [
                QPointF(origin_x - body_tube_arc/2 - height, origin_y + root / 2 - sweep),
                QPointF(origin_x - body_tube_arc/2, origin_y + root / 2),
                QPointF(origin_x + body_tube_arc/2, origin_y + root / 2),
                QPointF(origin_x + body_tube_arc/2 + height, origin_y + root / 2 - sweep),
                QPointF(origin_x + body_tube_arc/2 + height, origin_y + root / 2 - sweep - tip),
                                QPointF(origin_x + body_tube_arc/2, origin_y - root / 2),
                QPointF(origin_x - body_tube_arc/2, origin_y - root / 2),
                QPointF(origin_x - body_tube_arc/2 - height, origin_y + root / 2 - sweep - tip)

            ]


            
            poly = QPolygonF(points)
            if is_selected:
                brush_color = QColor(100, 160, 255)  # Highlighted blue
            else:
                brush_color = QColor(255, 255, 255)  # Plain white

            painter.setBrush(brush_color)
            painter.setPen(QPen(Qt.GlobalColor.black, 1))
            painter.drawPolygon(poly)

        # Draw core
        draw_layer(config, self.config.core, y_offset, self.selected_layer_index == 0, scale)

        # Draw additional layers
        for idx, layer in enumerate(self.config.layers):
            y_offset += layer.thickness * 1000
            draw_layer(config, layer, y_offset, self.selected_layer_index == idx + 1, scale)
