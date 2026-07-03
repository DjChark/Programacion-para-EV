# ejercicio_01_canales_rgb.py
# pip install opencv-contrib-python numpy PyQt6

import sys
import cv2
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QSlider, QPushButton,
                             QFileDialog, QGroupBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap


class InspectorImagen(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🔍 Inspector de Imagen – Capítulo 1")
        self.setGeometry(100, 100, 1200, 700)
        self.imagen_original = None
        self.imagen_procesada = None
        self.brillo = 0
        self.contraste = 1.0
        self.saturacion = 1.0
        self.canal_activo = 4  # 4 = imagen completa
        self.setup_ui()
        self.timer = QTimer()
        self.timer.timeout.connect(self.mostrar_imagen)
        self.timer.start(50)

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)

        self.label_imagen = QLabel("Carga una imagen para empezar")
        self.label_imagen.setMinimumSize(800, 600)
        self.label_imagen.setStyleSheet("border:2px solid #333; background:#222; color:white;")
        self.label_imagen.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label_imagen, 3)

        panel = QWidget(); panel.setMaximumWidth(350)
        lc = QVBoxLayout(panel)

        g1 = QGroupBox("📁 Cargar Imagen"); v1 = QVBoxLayout()
        btn = QPushButton("Seleccionar imagen...")
        btn.clicked.connect(self.cargar_imagen); v1.addWidget(btn)
        self.info_label = QLabel("Sin imagen"); v1.addWidget(self.info_label)
        g1.setLayout(v1); lc.addWidget(g1)

        g_canal = QGroupBox("🎨 Canal (teclado 1-4)"); v_canal = QVBoxLayout()
        for txt, key in [("1 – Solo Azul","1"),("2 – Solo Verde","2"),
                          ("3 – Solo Rojo","3"),("4 – Imagen completa","4")]:
            btn_c = QPushButton(txt)
            btn_c.clicked.connect(lambda _, k=key: self.cambiar_canal(k))
            v_canal.addWidget(btn_c)
        g_canal.setLayout(v_canal); lc.addWidget(g_canal)

        g2 = QGroupBox("🎛️ Ajustes"); v2 = QVBoxLayout()
        for nombre, attr, rng, val in [("Brillo","brillo",(-100,100),0),
                                        ("Contraste","contraste",(0,200),100),
                                        ("Saturación","saturacion",(0,200),100)]:
            v2.addWidget(QLabel(nombre+":"))
            sl = QSlider(Qt.Orientation.Horizontal)
            sl.setRange(*rng); sl.setValue(val)
            sl.valueChanged.connect(lambda v, a=attr, r=rng: self._set(a, v, r))
            v2.addWidget(sl)
        g2.setLayout(v2); lc.addWidget(g2)

        g3 = QGroupBox("📊 Info Técnica"); v3 = QVBoxLayout()
        self.tec_label = QLabel("Sin datos"); v3.addWidget(self.tec_label)
        g3.setLayout(v3); lc.addWidget(g3)

        lc.addStretch(); layout.addWidget(panel, 1)

    def _set(self, attr, val, rng):
        if rng == (-100, 100):
            setattr(self, attr, val)
        else:
            setattr(self, attr, val / 100.0)
        self.procesar()

    def cambiar_canal(self, key):
        self.canal_activo = int(key) - 1 if key in "123" else 4
        self.procesar()

    def keyPressEvent(self, event):
        tecla = event.text()
        if tecla in "1234":
            self.cambiar_canal(tecla)

    def cargar_imagen(self):
        archivo, _ = QFileDialog.getOpenFileName(self, "Seleccionar", "",
                                                  "Imágenes (*.png *.jpg *.jpeg *.bmp)")
        if archivo:
            self.imagen_original = cv2.imread(archivo)
            if self.imagen_original is not None:
                h, w = self.imagen_original.shape[:2]
                kb = self.imagen_original.nbytes / 1024
                self.info_label.setText(f"✅ {archivo.split('/')[-1]}")
                self.tec_label.setText(f"{w}x{h} px\nCanales: 3\n{kb:.1f} KB\nBGR (OpenCV)")
                self.procesar()

    def procesar(self):
        if self.imagen_original is None:
            return
        img = cv2.convertScaleAbs(self.imagen_original,
                                   alpha=self.contraste, beta=self.brillo)
        if self.saturacion != 1.0:
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
            hsv[:, :, 1] = np.clip(hsv[:, :, 1] * self.saturacion, 0, 255)
            img = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
        # Aplicar canal
        if self.canal_activo in [0, 1, 2]:
            canal_img = np.zeros_like(img)
            canal_img[:, :, self.canal_activo] = img[:, :, self.canal_activo]
            nombres = {0: "AZUL", 1: "VERDE", 2: "ROJO"}
            cv2.putText(canal_img, f"Canal: {nombres[self.canal_activo]}",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
            img = canal_img
        self.imagen_procesada = img
        self.mostrar_imagen()

    def mostrar_imagen(self):
        if self.imagen_procesada is None:
            return
        rgb = cv2.cvtColor(self.imagen_procesada, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qt_img = QImage(rgb.data, w, h, ch*w, QImage.Format.Format_RGB888)
        pix = QPixmap.fromImage(qt_img).scaled(
            self.label_imagen.size(), Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation)
        self.label_imagen.setPixmap(pix)


def main():
    app = QApplication(sys.argv)
    v = InspectorImagen(); v.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()