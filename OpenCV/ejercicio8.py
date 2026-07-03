# ejercicio_08_contador_ejercicios.py
# pip install opencv-contrib-python numpy PyQt6 mediapipe

import sys
import cv2
import mediapipe as mp
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton, QGroupBox,
                             QComboBox, QProgressBar)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap


def calcular_angulo(a, b, c, lm, w, h):
    pa = np.array([lm[a].x*w, lm[a].y*h])
    pb = np.array([lm[b].x*w, lm[b].y*h])
    pc = np.array([lm[c].x*w, lm[c].y*h])
    ba, bc = pa-pb, pc-pb
    cos_a = np.dot(ba,bc)/(np.linalg.norm(ba)*np.linalg.norm(bc)+1e-6)
    return float(np.degrees(np.arccos(np.clip(cos_a,-1,1))))


class ContadorEjercicios(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("💪 Contador de Ejercicios – Capítulo 8")
        self.setGeometry(100, 100, 1300, 800)
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer(); self.timer.timeout.connect(self.actualizar); self.timer.start(30)
        self.ejercicio = "sentadilla"; self.contador = 0; self.etapa = "arriba"
        self.historial = []
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

        g1 = QGroupBox("🏋️ Ejercicio"); v1 = QVBoxLayout()
        self.combo = QComboBox(); self.combo.addItems(["sentadilla","flexion","abdominal"])
        self.combo.currentTextChanged.connect(self.cambiar_ejercicio)
        v1.addWidget(self.combo); g1.setLayout(v1); lc.addWidget(g1)

        g2 = QGroupBox("📊 Progreso"); v2 = QVBoxLayout()
        self.lbl_contador = QLabel("0")
        self.lbl_contador.setStyleSheet("font-size:72px; font-weight:bold; color:#4CAF50;")
        self.lbl_contador.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v2.addWidget(self.lbl_contador)
        self.progress = QProgressBar(); self.progress.setRange(0,100); self.progress.setValue(0)
        v2.addWidget(self.progress); g2.setLayout(v2); lc.addWidget(g2)

        g3 = QGroupBox("📋 Estado"); v3 = QVBoxLayout()
        self.lbl_etapa = QLabel("Fase: Arriba")
        self.lbl_angulo = QLabel("Ángulo: --°")
        self.lbl_feedback = QLabel("¡Buena forma!")
        self.lbl_feedback.setStyleSheet("color:#4CAF50;")
        for w in [self.lbl_etapa, self.lbl_angulo, self.lbl_feedback]: v3.addWidget(w)
        g3.setLayout(v3); lc.addWidget(g3)

        btn_r = QPushButton("🔄 Reiniciar"); btn_r.clicked.connect(self.reiniciar); lc.addWidget(btn_r)
        lc.addStretch(); layout.addWidget(pc, 1)

    def cambiar_ejercicio(self, e): self.ejercicio = e; self.reiniciar()

    def reiniciar(self): self.contador = 0; self.etapa = "arriba"; self.lbl_contador.setText("0")

    def actualizar(self):
        ret, frame = self.cap.read()
        if not ret: return
        h, w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = self.pose.process(rgb)
        angulo = None
        if res.pose_landmarks:
            lm = res.pose_landmarks.landmark
            mp.solutions.drawing_utils.draw_landmarks(frame, res.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
            if self.ejercicio == "sentadilla":
                angulo = calcular_angulo(23,25,27,lm,w,h)
                for idx in [23,25,27]:
                    cv2.circle(frame,(int(lm[idx].x*w),int(lm[idx].y*h)),8,(255,0,0),-1)
            elif self.ejercicio == "flexion":
                angulo = calcular_angulo(11,13,15,lm,w,h)
                for idx in [11,13,15]:
                    cv2.circle(frame,(int(lm[idx].x*w),int(lm[idx].y*h)),8,(255,0,0),-1)
            else:
                angulo = calcular_angulo(11,23,25,lm,w,h)
                for idx in [11,23,25]:
                    cv2.circle(frame,(int(lm[idx].x*w),int(lm[idx].y*h)),8,(255,0,0),-1)
            if angulo < 90 and self.etapa == "arriba":
                self.etapa = "abajo"; self.lbl_feedback.setText("⬇️ Baja...")
            elif angulo > 160 and self.etapa == "abajo":
                self.etapa = "arriba"; self.contador += 1
                self.lbl_feedback.setText("✅ ¡Bien hecho!"); print(f"Rep #{self.contador}")
            self.lbl_etapa.setText(f"Fase: {self.etapa.capitalize()}")
            self.lbl_angulo.setText(f"Ángulo: {angulo:.1f}°")
            self.lbl_contador.setText(str(self.contador))
            self.progress.setValue(self.contador % 100)
            cv2.putText(frame,f"{angulo:.1f}",(10,40),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2)
        rgb2 = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB); h2,w2,ch = rgb2.shape
        qt_img = QImage(rgb2.data,w2,h2,ch*w2,QImage.Format.Format_RGB888)
        pix = QPixmap.fromImage(qt_img).scaled(self.label_video.size(),
              Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation)
        self.label_video.setPixmap(pix)

    def closeEvent(self, event): self.cap.release(); self.pose.close(); event.accept()

def main():
    app = QApplication(sys.argv); v = ContadorEjercicios(); v.show(); sys.exit(app.exec())

if __name__ == "__main__": main()
