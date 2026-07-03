# ejercicio_07_pintura_dedos.py
# pip install opencv-contrib-python numpy PyQt6 mediapipe

import sys
import cv2
import mediapipe as mp
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton, QGroupBox,
                             QSlider, QColorDialog, QSpinBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap


class PinturaDedos(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🖌️ Pintura con Dedos – Capítulo 7")
        self.setGeometry(100, 100, 1400, 800)
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(max_num_hands=1,
                                          min_detection_confidence=0.7, min_tracking_confidence=0.5)
        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer(); self.timer.timeout.connect(self.actualizar); self.timer.start(30)
        self.lienzo = None; self.ultima_pos = None
        self.color_actual = (0,255,0); self.grosor = 5; self.modo_borrador = False
        self.setup_ui()

    def setup_ui(self):
        central = QWidget(); self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        pv = QWidget(); lv = QVBoxLayout(pv)
        self.label_video = QLabel()
        self.label_video.setMinimumSize(800,600)
        self.label_video.setStyleSheet("border:2px solid #333; background:#111;")
        self.label_video.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lv.addWidget(self.label_video); layout.addWidget(pv, 3)

        pc = QWidget(); pc.setMaximumWidth(350); lc = QVBoxLayout(pc)

        g1 = QGroupBox("🎨 Color"); v1 = QVBoxLayout()
        btn_c = QPushButton("Seleccionar color"); btn_c.clicked.connect(self.seleccionar_color); v1.addWidget(btn_c)
        btn_b = QPushButton("🧼 Borrador"); btn_b.setCheckable(True)
        btn_b.toggled.connect(lambda v: setattr(self,'modo_borrador',v)); v1.addWidget(btn_b)
        g1.setLayout(v1); lc.addWidget(g1)

        g2 = QGroupBox("✏️ Grosor"); v2 = QVBoxLayout()
        sp = QSpinBox(); sp.setRange(1,20); sp.setValue(5)
        sp.valueChanged.connect(lambda v: setattr(self,'grosor',v))
        v2.addWidget(sp); g2.setLayout(v2); lc.addWidget(g2)

        g3 = QGroupBox("💾 Acciones"); v3 = QVBoxLayout()
        btn_l = QPushButton("🧹 Limpiar lienzo"); btn_l.clicked.connect(self.limpiar); v3.addWidget(btn_l)
        btn_s = QPushButton("💾 Guardar dibujo"); btn_s.clicked.connect(self.guardar); v3.addWidget(btn_s)
        g3.setLayout(v3); lc.addWidget(g3)

        g4 = QGroupBox("📖 Instrucciones"); v4 = QVBoxLayout()
        v4.addWidget(QLabel("☝️ Índice solo → Dibuja\n✌️ Índice+Medio → Borra\n✋ Mano abierta → Limpia"))
        g4.setLayout(v4); lc.addWidget(g4)
        lc.addStretch(); layout.addWidget(pc, 1)

    def seleccionar_color(self):
        c = QColorDialog.getColor()
        if c.isValid(): self.color_actual = (c.blue(), c.green(), c.red())

    def limpiar(self):
        if self.lienzo is not None: self.lienzo[:] = 0

    def guardar(self):
        if self.lienzo is not None: cv2.imwrite("dibujo_dedos.png", self.lienzo); print("💾 Guardado: dibujo_dedos.png")

    def detectar_gesto(self, lm):
        p_idx = lm.landmark[8]; n_idx = lm.landmark[6]
        p_med = lm.landmark[12]; n_med = lm.landmark[10]
        p_anu = lm.landmark[16]; n_anu = lm.landmark[14]
        p_men = lm.landmark[20]; n_men = lm.landmark[18]
        idx = p_idx.y < n_idx.y; med = p_med.y < n_med.y
        anu = p_anu.y < n_anu.y; men = p_men.y < n_men.y
        if idx and med and anu and men: return "limpiar"
        if idx and not med: return "dibujar"
        if idx and med: return "borrar"
        return "ninguno"

    def actualizar(self):
        ret, frame = self.cap.read()
        if not ret: return
        if self.lienzo is None or self.lienzo.shape != frame.shape:
            self.lienzo = np.zeros_like(frame)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = self.hands.process(rgb)
        h, w = frame.shape[:2]; gesto = "ninguno"
        if res.multi_hand_landmarks:
            for hl in res.multi_hand_landmarks:
                gesto = self.detectar_gesto(hl)
                idx_tip = hl.landmark[8]
                pos = (int(idx_tip.x*w), int(idx_tip.y*h))
                if gesto == "dibujar" and not self.modo_borrador:
                    if self.ultima_pos: cv2.line(self.lienzo, self.ultima_pos, pos, self.color_actual, self.grosor)
                    cv2.circle(self.lienzo, pos, self.grosor//2, self.color_actual, -1)
                    self.ultima_pos = pos
                elif gesto == "borrar" or self.modo_borrador:
                    cv2.circle(self.lienzo, pos, self.grosor*2, (0,0,0), -1); self.ultima_pos = pos
                elif gesto == "limpiar":
                    self.lienzo[:] = 0; self.ultima_pos = None
                else: self.ultima_pos = None
                mp.solutions.drawing_utils.draw_landmarks(frame, hl, self.mp_hands.HAND_CONNECTIONS)
        else: self.ultima_pos = None
        resultado = cv2.addWeighted(frame, 0.6, self.lienzo, 0.4, 0)
        cv2.putText(resultado, f"Gesto: {gesto}", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.color_actual, 2)
        rgb2 = cv2.cvtColor(resultado, cv2.COLOR_BGR2RGB); h2,w2,ch = rgb2.shape
        qt_img = QImage(rgb2.data,w2,h2,ch*w2,QImage.Format.Format_RGB888)
        pix = QPixmap.fromImage(qt_img).scaled(self.label_video.size(),
              Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation)
        self.label_video.setPixmap(pix)

    def closeEvent(self, event): self.cap.release(); self.hands.close(); event.accept()

def main():
    app = QApplication(sys.argv); v = PinturaDedos(); v.show(); sys.exit(app.exec())

if __name__ == "__main__": main()