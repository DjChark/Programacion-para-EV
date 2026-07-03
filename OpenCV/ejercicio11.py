# ejercicio_11_cubo_ar_interactivo.py
# pip install opencv-contrib-python numpy PyQt6 mediapipe

import sys
import cv2
import cv2.aruco as aruco
import numpy as np
import mediapipe as mp
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton, QGroupBox,
                             QSlider, QComboBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap

TAM_M = 0.05; LADO = 0.03

CUBO_3D = np.float32([
    [-LADO/2,-LADO/2,0],[LADO/2,-LADO/2,0],[LADO/2,LADO/2,0],[-LADO/2,LADO/2,0],
    [-LADO/2,-LADO/2,-LADO],[LADO/2,-LADO/2,-LADO],[LADO/2,LADO/2,-LADO],[-LADO/2,LADO/2,-LADO]
])
ARISTAS = [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)]
CARAS   = [[0,1,2,3],[4,5,6,7],[0,1,5,4],[2,3,7,6],[1,2,6,5],[0,3,7,4]]

OBJ_PTS = np.float32([[0,0,0],[TAM_M,0,0],[TAM_M,TAM_M,0],[0,TAM_M,0]])

class CuboARInteractivo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎲 Cubo AR Interactivo – Capítulo 11")
        self.setGeometry(100,100,1400,800)
        self.diccionario = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)
        self.detector = aruco.ArucoDetector(self.diccionario, aruco.DetectorParameters())
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
        self.rot_y = 0; self.rot_x = 0; self.rot_auto = True
        self.modo_color = "solido"; self.color = (0,255,0)
        self.cam_matrix = None
        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer(); self.timer.timeout.connect(self.actualizar); self.timer.start(30)
        self.setup_ui()

    def setup_ui(self):
        central = QWidget(); self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        self.lbl_video = QLabel()
        self.lbl_video.setMinimumSize(800,600)
        self.lbl_video.setStyleSheet("background:#111; border:2px solid #555;")
        self.lbl_video.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_video, 3)

        pc = QWidget(); pc.setMaximumWidth(350); lc = QVBoxLayout(pc)

        g1 = QGroupBox("🔄 Rotación"); v1 = QVBoxLayout()
        btn_auto = QPushButton("Auto/Manual"); btn_auto.setCheckable(True); btn_auto.setChecked(True)
        btn_auto.toggled.connect(lambda v: setattr(self,'rot_auto',v)); v1.addWidget(btn_auto)
        for lbl, attr in [("Rot X:","rot_x"),("Rot Y:","rot_y")]:
            v1.addWidget(QLabel(lbl))
            sl = QSlider(Qt.Orientation.Horizontal); sl.setRange(-180,180)
            sl.valueChanged.connect(lambda v, a=attr: setattr(self,a,v)); v1.addWidget(sl)
        g1.setLayout(v1); lc.addWidget(g1)

        g2 = QGroupBox("🎨 Color"); v2 = QVBoxLayout()
        self.combo_color = QComboBox()
        self.combo_color.addItems(["solido","arcoiris","por cara"])
        self.combo_color.currentTextChanged.connect(lambda v: setattr(self,'modo_color',v))
        v2.addWidget(self.combo_color); g2.setLayout(v2); lc.addWidget(g2)

        g3 = QGroupBox("ℹ️ Gestos"); v3 = QVBoxLayout()
        v3.addWidget(QLabel("✌️ Paz → modo arcoíris\n✋ Abierta → color sólido"))
        g3.setLayout(v3); lc.addWidget(g3)
        lc.addStretch(); layout.addWidget(pc, 1)

    def detectar_gesto(self, lm):
        i = lm.landmark[8].y < lm.landmark[6].y
        m = lm.landmark[12].y < lm.landmark[10].y
        a = lm.landmark[16].y < lm.landmark[14].y
        mn = lm.landmark[20].y < lm.landmark[18].y
        if i and m and a and mn: return "abierta"
        if i and m: return "paz"
        return "none"

    def dibujar_cubo(self, frame, imgpts):
        pts = np.int32(imgpts).reshape(-1,2)
        colores_cara = [(255,0,0),(0,255,0),(0,0,255),(255,255,0),(255,0,255),(0,255,255)]
        for i, cara in enumerate(CARAS):
            c_pts = np.array([pts[j] for j in cara])
            if self.modo_color == "arcoiris":
                color = colores_cara[i]
            elif self.modo_color == "por cara":
                color = (50+i*40, 100+i*20, 150+i*30)
            else:
                color = self.color
            overlay = frame.copy()
            cv2.fillPoly(overlay,[c_pts],color)
            cv2.addWeighted(overlay,0.3,frame,0.7,0,frame)
        for a,b in ARISTAS:
            cv2.line(frame,tuple(pts[a]),tuple(pts[b]),(255,255,255),2)

    def actualizar(self):
        ret, frame = self.cap.read()
        if not ret: return
        h, w = frame.shape[:2]
        if self.cam_matrix is None:
            focal = max(w,h)
            self.cam_matrix = np.array([[focal,0,w/2],[0,focal,h/2],[0,0,1]],dtype=np.float32)
            self.dist = np.zeros((4,1),dtype=np.float32)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res_h = self.hands.process(rgb)
        if res_h.multi_hand_landmarks:
            for hl in res_h.multi_hand_landmarks:
                gesto = self.detectar_gesto(hl)
                if gesto == "paz": self.modo_color = "arcoiris"; self.combo_color.setCurrentText("arcoiris")
                elif gesto == "abierta": self.modo_color = "solido"; self.combo_color.setCurrentText("solido")
                mp.solutions.drawing_utils.draw_landmarks(frame,hl,self.mp_hands.HAND_CONNECTIONS)
        esq, ids, _ = self.detector.detectMarkers(frame)
        if ids is not None:
            aruco.drawDetectedMarkers(frame,esq,ids)
            for i in range(len(ids)):
                ok, rvec, tvec = cv2.solvePnP(OBJ_PTS, esq[i][0], self.cam_matrix, self.dist)
                if ok:
                    if self.rot_auto: self.rot_y = (self.rot_y+2)%360
                    R_extra,_ = cv2.Rodrigues(np.array([self.rot_x*np.pi/180, self.rot_y*np.pi/180, 0.0]))
                    cubo_rot = np.dot(CUBO_3D, R_extra.T)
                    imgpts,_ = cv2.projectPoints(cubo_rot, rvec, tvec, self.cam_matrix, self.dist)
                    self.dibujar_cubo(frame, imgpts)
                    cv2.drawFrameAxes(frame, self.cam_matrix, self.dist, rvec, tvec, 0.03)
        rgb2 = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB); h2,w2,ch = rgb2.shape
        qt_img = QImage(rgb2.data,w2,h2,ch*w2,QImage.Format.Format_RGB888)
        pix = QPixmap.fromImage(qt_img).scaled(self.lbl_video.size(),
              Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation)
        self.lbl_video.setPixmap(pix)

    def closeEvent(self, event): self.cap.release(); self.hands.close(); event.accept()

def main():
    app = QApplication(sys.argv); v = CuboARInteractivo(); v.show(); sys.exit(app.exec())

if __name__ == "__main__": main()