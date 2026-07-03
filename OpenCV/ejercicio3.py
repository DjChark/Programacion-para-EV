# ejercicio_03_detector_figuras.py
# pip install opencv-contrib-python numpy PyQt6

import sys
import cv2
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QSlider, QGroupBox, QCheckBox,
                             QTableWidget, QTableWidgetItem, QHeaderView, QPushButton)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap

FORMAS   = ["Triángulo","Cuadrado","Rectángulo","Círculo","Pentágono","Hexágono","Desconocido"]
COLORES  = {"Triángulo":(0,255,0),"Cuadrado":(255,0,0),"Rectángulo":(255,255,0),
             "Círculo":(0,0,255),"Pentágono":(255,0,255),"Hexágono":(0,255,255),"Desconocido":(128,128,128)}

def detectar_forma(cnt):
    peri  = cv2.arcLength(cnt, True)
    aprox = cv2.approxPolyDP(cnt, 0.04*peri, True)
    v = len(aprox)
    if v == 3: return "Triángulo"
    if v == 4:
        x,y,w,h = cv2.boundingRect(aprox)
        return "Cuadrado" if 0.95 <= w/float(h) <= 1.05 else "Rectángulo"
    if v == 5: return "Pentágono"
    if v == 6: return "Hexágono"
    if v > 6:
        area = cv2.contourArea(cnt)
        (_,_), r = cv2.minEnclosingCircle(cnt)
        if r > 0 and abs(area - np.pi*r**2)/(np.pi*r**2) < 0.2: return "Círculo"
    return "Desconocido"

class DetectorFiguras(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📐 Detector de Figuras – Capítulo 3")
        self.setGeometry(100,100,1400,800)
        self.canny1 = 50; self.canny2 = 150; self.min_area = 500
        self.mostrar_bordes = False
        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer(); self.timer.timeout.connect(self.actualizar); self.timer.start(30)
        self.setup_ui()

    def setup_ui(self):
        central = QWidget(); self.setCentralWidget(central)
        layout = QHBoxLayout(central)

        pv = QWidget(); lv = QVBoxLayout(pv)
        self.label_video = QLabel()
        self.label_video.setMinimumSize(900,600)
        self.label_video.setStyleSheet("border:2px solid #333; background:#111;")
        self.label_video.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lv.addWidget(self.label_video)
        cb = QCheckBox("Mostrar bordes Canny")
        cb.stateChanged.connect(lambda v: setattr(self,'mostrar_bordes',bool(v)))
        lv.addWidget(cb); layout.addWidget(pv, 3)

        pc = QWidget(); pc.setMaximumWidth(350); lc = QVBoxLayout(pc)

        g1 = QGroupBox("🎚️ Parámetros Canny"); v1 = QVBoxLayout()
        for lbl, attr, val in [("Umbral 1","canny1",50),("Umbral 2","canny2",150)]:
            v1.addWidget(QLabel(lbl+":"))
            sl = QSlider(Qt.Orientation.Horizontal); sl.setRange(0,255); sl.setValue(val)
            sl.valueChanged.connect(lambda v, a=attr: setattr(self,a,v))
            v1.addWidget(sl)
        g1.setLayout(v1); lc.addWidget(g1)

        g2 = QGroupBox("📏 Área mínima"); v2 = QVBoxLayout()
        sl_a = QSlider(Qt.Orientation.Horizontal); sl_a.setRange(100,5000); sl_a.setValue(500)
        self.lbl_area = QLabel("500 px²")
        sl_a.valueChanged.connect(lambda v: (setattr(self,'min_area',v), self.lbl_area.setText(f"{v} px²")))
        v2.addWidget(sl_a); v2.addWidget(self.lbl_area)
        g2.setLayout(v2); lc.addWidget(g2)

        g3 = QGroupBox("📊 Conteo de formas"); v3 = QVBoxLayout()
        self.tabla = QTableWidget(len(FORMAS),2)
        self.tabla.setHorizontalHeaderLabels(["Forma","N"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        for i,f in enumerate(FORMAS):
            self.tabla.setItem(i,0,QTableWidgetItem(f)); self.tabla.setItem(i,1,QTableWidgetItem("0"))
        v3.addWidget(self.tabla)
        btn_r = QPushButton("🔄 Reiniciar")
        btn_r.clicked.connect(lambda: [self.tabla.setItem(i,1,QTableWidgetItem("0")) for i in range(len(FORMAS))])
        v3.addWidget(btn_r); g3.setLayout(v3); lc.addWidget(g3)
        lc.addStretch(); layout.addWidget(pc,1)

    def actualizar(self):
        ret, frame = self.cap.read()
        if not ret: return
        gris = cv2.GaussianBlur(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY),(5,5),0)
        bordes = cv2.Canny(gris, self.canny1, self.canny2)
        cnts,_ = cv2.findContours(bordes, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        conteo = {f:0 for f in FORMAS}
        for cnt in cnts:
            if cv2.contourArea(cnt) < self.min_area: continue
            forma = detectar_forma(cnt); conteo[forma] += 1
            cv2.drawContours(frame,[cnt],-1,COLORES[forma],2)
            M = cv2.moments(cnt)
            if M["m00"] != 0:
                cx,cy = int(M["m10"]/M["m00"]),int(M["m01"]/M["m00"])
                cv2.putText(frame,forma,(cx-30,cy),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,255,255),1)
        for i,f in enumerate(FORMAS):
            self.tabla.setItem(i,1,QTableWidgetItem(str(conteo[f])))
        mostrar = cv2.cvtColor(bordes,cv2.COLOR_GRAY2BGR) if self.mostrar_bordes else frame
        rgb = cv2.cvtColor(mostrar,cv2.COLOR_BGR2RGB)
        h,w,ch = rgb.shape
        qt_img = QImage(rgb.data,w,h,ch*w,QImage.Format.Format_RGB888)
        pix = QPixmap.fromImage(qt_img).scaled(self.label_video.size(),
              Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation)
        self.label_video.setPixmap(pix)

    def closeEvent(self, event): self.cap.release(); event.accept()

def main():
    app = QApplication(sys.argv); v = DetectorFiguras(); v.show(); sys.exit(app.exec())

if __name__ == "__main__": main()