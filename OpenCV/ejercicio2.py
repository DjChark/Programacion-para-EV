# ejercicio_02_color_magico.py
# pip install opencv-contrib-python numpy PyQt6

import sys
import cv2
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QSlider, QGroupBox, QComboBox,
                             QPushButton)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap


class SelectorColorMagico(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎬 Selector de Color Mágico – Capítulo 2")
        self.setGeometry(100, 100, 1300, 800)
        self.h_min, self.h_max = 40, 80
        self.s_min, self.s_max = 100, 255
        self.v_min, self.v_max = 100, 255
        self.presets = {
            "Personalizado": (0,179,0,255,0,255),
            "Rojo":          (0,10,100,255,100,255),
            "Verde":         (40,80,100,255,100,255),
            "Azul":          (100,130,100,255,100,255),
            "Amarillo":      (20,30,100,255,100,255),
            "Naranja":       (5,15,100,255,100,255),
        }
        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar)
        self.timer.start(30)
        self.setup_ui()

    def setup_ui(self):
        central = QWidget(); self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        self.label_video = QLabel()
        self.label_video.setMinimumSize(800, 600)
        self.label_video.setStyleSheet("background:#111; border:2px solid #444;")
        self.label_video.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label_video, 3)

        panel = QWidget(); panel.setMaximumWidth(380)
        lc = QVBoxLayout(panel)

        g1 = QGroupBox("🎨 Colores Predefinidos"); v1 = QVBoxLayout()
        self.combo = QComboBox(); self.combo.addItems(self.presets.keys())
        self.combo.currentTextChanged.connect(self.cargar_preset)
        v1.addWidget(self.combo); g1.setLayout(v1); lc.addWidget(g1)

        g2 = QGroupBox("🎚️ Control Manual HSV"); v2 = QVBoxLayout()
        self.sliders = {}
        datos = [("H Min",0,179,self.h_min,"h_min"),("H Max",0,179,self.h_max,"h_max"),
                 ("S Min",0,255,self.s_min,"s_min"),("S Max",0,255,self.s_max,"s_max"),
                 ("V Min",0,255,self.v_min,"v_min"),("V Max",0,255,self.v_max,"v_max")]
        for label, mn, mx, val, attr in datos:
            v2.addWidget(QLabel(label+":"))
            sl = QSlider(Qt.Orientation.Horizontal)
            sl.setRange(mn, mx); sl.setValue(val)
            sl.valueChanged.connect(lambda v, a=attr: setattr(self, a, v))
            v2.addWidget(sl); self.sliders[attr] = sl
        g2.setLayout(v2); lc.addWidget(g2)

        g3 = QGroupBox("ℹ️ Rango HSV"); v3 = QVBoxLayout()
        self.info_rango = QLabel("H:[40,80]\nS:[100,255]\nV:[100,255]")
        v3.addWidget(self.info_rango); g3.setLayout(v3); lc.addWidget(g3)

        btn = QPushButton("📸 Guardar instantánea")
        btn.clicked.connect(self.guardar); lc.addWidget(btn)
        lc.addStretch(); layout.addWidget(panel, 1)

    def cargar_preset(self, nombre):
        if nombre in self.presets:
            vals = self.presets[nombre]
            keys = ["h_min","h_max","s_min","s_max","v_min","v_max"]
            for k, v in zip(keys, vals):
                setattr(self, k, v); self.sliders[k].setValue(v)

    def guardar(self):
        if hasattr(self, 'ultimo_frame'):
            cv2.imwrite("captura_cine.png", self.ultimo_frame)
            print("📸 Guardado: captura_cine.png")

    def actualizar(self):
        ret, frame = self.cap.read()
        if not ret: return
        self.ultimo_frame = frame.copy()
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower = np.array([self.h_min, self.s_min, self.v_min])
        upper = np.array([self.h_max, self.s_max, self.v_max])
        mascara = cv2.inRange(hsv, lower, upper)
        k = np.ones((5,5), np.uint8)
        mascara = cv2.morphologyEx(mascara, cv2.MORPH_OPEN, k)
        mascara = cv2.morphologyEx(mascara, cv2.MORPH_CLOSE, k)
        mascara = cv2.GaussianBlur(mascara, (5,5), 0)
        gris = cv2.cvtColor(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2BGR)
        m = cv2.cvtColor(mascara, cv2.COLOR_GRAY2BGR) / 255.0
        resultado = (frame * m + gris * (1 - m)).astype(np.uint8)
        self.info_rango.setText(f"H:[{self.h_min},{self.h_max}]\n"
                                 f"S:[{self.s_min},{self.s_max}]\n"
                                 f"V:[{self.v_min},{self.v_max}]")
        rgb = cv2.cvtColor(resultado, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qt_img = QImage(rgb.data, w, h, ch*w, QImage.Format.Format_RGB888)
        pix = QPixmap.fromImage(qt_img).scaled(self.label_video.size(),
              Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.label_video.setPixmap(pix)

    def closeEvent(self, event):
        self.cap.release(); event.accept()


def main():
    app = QApplication(sys.argv)
    v = SelectorColorMagico(); v.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()