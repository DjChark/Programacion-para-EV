# ejercicio_06_malla_facial.py
# pip install opencv-contrib-python numpy PyQt6 mediapipe==0.10.14

import sys
import cv2
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton, QGroupBox,
                             QSlider, QComboBox, QColorDialog)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap, QColor

# --- NUEVOS IMPORTS SEGÚN LA IMAGEN ---
import mediapipe as mp
from mediapipe.python.solutions import face_mesh as mp_face_mesh
from mediapipe.python.solutions import drawing_utils as mp_draw
from mediapipe.python.solutions import drawing_styles as mp_styles


class MallaFacialArtistica(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎨 Malla Facial Artística – Capítulo 6")
        self.setGeometry(100, 100, 1300, 800)
        
        # --- NUEVA INICIALIZACIÓN SEGÚN LA IMAGEN ---
        self.face_mesh = mp_face_mesh.FaceMesh(
            max_num_faces=2, 
            refine_landmarks=True,
            min_detection_confidence=0.5, 
            min_tracking_confidence=0.5
        )
        
        self.estilo = "contorno"
        self.color = (0, 255, 0)
        self.grosor = 1
        self.efecto_arcoiris = False
        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar)
        self.timer.start(30)
        self.setup_ui()

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        
        pv = QWidget()
        lv = QVBoxLayout(pv)
        self.label_video = QLabel()
        self.label_video.setMinimumSize(800, 600)
        self.label_video.setStyleSheet("border:2px solid #333; background:#111;")
        self.label_video.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lv.addWidget(self.label_video)
        
        self.expr_label = QLabel("😐 Expresión: --")
        self.expr_label.setStyleSheet("font-size:16px; font-weight:bold;")
        lv.addWidget(self.expr_label)
        layout.addWidget(pv, 3)

        pc = QWidget()
        pc.setMaximumWidth(350)
        lc = QVBoxLayout(pc)

        g1 = QGroupBox("🎭 Estilo")
        v1 = QVBoxLayout()
        self.combo = QComboBox()
        self.combo.addItems(["contorno", "puntos", "malla_completa", "solo_ojos", "solo_boca"])
        self.combo.currentTextChanged.connect(lambda v: setattr(self, 'estilo', v))
        v1.addWidget(self.combo)
        g1.setLayout(v1)
        lc.addWidget(g1)

        g2 = QGroupBox("🎨 Color")
        v2 = QVBoxLayout()
        btn_c = QPushButton("Seleccionar color")
        btn_c.clicked.connect(self.seleccionar_color)
        v2.addWidget(btn_c)
        btn_arc = QPushButton("🌈 Arcoíris")
        btn_arc.setCheckable(True)
        btn_arc.toggled.connect(lambda v: setattr(self, 'efecto_arcoiris', v))
        v2.addWidget(btn_arc)
        g2.setLayout(v2)
        lc.addWidget(g2)

        g3 = QGroupBox("✏️ Grosor")
        v3 = QVBoxLayout()
        sl = QSlider(Qt.Orientation.Horizontal)
        sl.setRange(1, 5)
        sl.setValue(1)
        sl.valueChanged.connect(lambda v: setattr(self, 'grosor', v))
        v3.addWidget(sl)
        g3.setLayout(v3)
        lc.addWidget(g3)

        g4 = QGroupBox("ℹ️ Detección")
        v4 = QVBoxLayout()
        self.info_label = QLabel("Sin rostro")
        v4.addWidget(self.info_label)
        g4.setLayout(v4)
        lc.addWidget(g4)
        
        lc.addStretch()
        layout.addWidget(pc, 1)

    def seleccionar_color(self):
        c = QColorDialog.getColor()
        if c.isValid(): 
            self.color = (c.blue(), c.green(), c.red())

    def actualizar(self):
        ret, frame = self.cap.read()
        if not ret: return
        
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = self.face_mesh.process(rgb)
        h, w = frame.shape[:2]
        
        if res.multi_face_landmarks:
            for lm in res.multi_face_landmarks:
                if self.estilo == "malla_completa":
                    # --- NUEVO USO DE ALIAS SEGÚN LA IMAGEN ---
                    mp_draw.draw_landmarks(
                        frame, 
                        lm, 
                        mp_face_mesh.FACEMESH_TESSELATION,
                        landmark_drawing_spec=None,
                        connection_drawing_spec=mp_styles.get_default_face_mesh_tesselation_style()
                    )
                elif self.estilo == "puntos":
                    for punto in lm.landmark:
                        x2, y2 = int(punto.x*w), int(punto.y*h)
                        c = (x2%255, y2%255, (x2+y2)%255) if self.efecto_arcoiris else self.color
                        cv2.circle(frame, (x2, y2), self.grosor, c, -1)
                elif self.estilo == "contorno":
                    indices = [10,338,297,332,284,251,389,356,454,323,361,288,
                               397,365,379,378,400,377,152,148,176,149,150,136,172,58,132,93,234,127,162,21,54,103,67,109]
                    pts = [(int(lm.landmark[i].x*w), int(lm.landmark[i].y*h)) for i in indices]
                    for i in range(len(pts)-1): 
                        cv2.line(frame, pts[i], pts[i+1], self.color, self.grosor)
                elif self.estilo == "solo_ojos":
                    for idx in [33,133,157,158,159,160,161,173,362,263,387,388,389,390,391,398]:
                        x2, y2 = int(lm.landmark[idx].x*w), int(lm.landmark[idx].y*h)
                        cv2.circle(frame, (x2, y2), 2, self.color, -1)
                elif self.estilo == "solo_boca":
                    for idx in [61,146,91,181,84,17,314,405,321,375]:
                        x2, y2 = int(lm.landmark[idx].x*w), int(lm.landmark[idx].y*h)
                        cv2.circle(frame, (x2, y2), 2, self.color, -1)
            
            self.info_label.setText(f"Puntos: {len(lm.landmark)}\nEstilo: {self.estilo}")
        else:
            self.info_label.setText("No se detectó rostro")
            
        rgb2 = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h2, w2, ch = rgb2.shape
        qt_img = QImage(rgb2.data, w2, h2, ch*w2, QImage.Format.Format_RGB888)
        pix = QPixmap.fromImage(qt_img).scaled(self.label_video.size(),
              Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.label_video.setPixmap(pix)

    def closeEvent(self, event): 
        self.cap.release()
        self.face_mesh.close()
        event.accept()

def main():
    app = QApplication(sys.argv)
    v = MallaFacialArtistica()
    v.show()
    sys.exit(app.exec())

if __name__ == "__main__": 
    main()