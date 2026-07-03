# ejercicio_04_escaner_documentos.py
# pip install opencv-contrib-python numpy PyQt6

import sys
import cv2
import numpy as np
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton, QGroupBox,
                             QSlider, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap, QAction


class EscanerDocumentos(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📄 Escáner de Documentos – Capítulo 4")
        self.setGeometry(100, 100, 1400, 800)
        self.imagen_original = None
        self.imagen_procesada = None
        self.setup_ui(); self.setup_menu()

    def setup_ui(self):
        central = QWidget(); self.setCentralWidget(central)
        layout = QHBoxLayout(central)

        pi = QWidget(); li = QVBoxLayout(pi)
        li.addWidget(QLabel("📸 Original:"))
        self.lbl_orig = QLabel("Sin imagen")
        self.lbl_orig.setMinimumSize(500,380)
        self.lbl_orig.setStyleSheet("border:1px solid #555; background:#111; color:white;")
        self.lbl_orig.setAlignment(Qt.AlignmentFlag.AlignCenter)
        li.addWidget(self.lbl_orig)
        li.addWidget(QLabel("✨ Enderezada:"))
        self.lbl_proc = QLabel("Sin resultado")
        self.lbl_proc.setMinimumSize(500,380)
        self.lbl_proc.setStyleSheet("border:1px solid #555; background:#111; color:white;")
        self.lbl_proc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        li.addWidget(self.lbl_proc); layout.addWidget(pi, 3)

        pc = QWidget(); pc.setMaximumWidth(300); lc = QVBoxLayout(pc)

        g1 = QGroupBox("📁 Cargar"); v1 = QVBoxLayout()
        btn_f = QPushButton("Seleccionar imagen..."); btn_f.clicked.connect(self.cargar_imagen); v1.addWidget(btn_f)
        btn_cam = QPushButton("📷 Captura webcam"); btn_cam.clicked.connect(self.captura_webcam); v1.addWidget(btn_cam)
        g1.setLayout(v1); lc.addWidget(g1)

        g2 = QGroupBox("⚙️ Canny"); v2 = QVBoxLayout()
        self.sl_c1 = QSlider(Qt.Orientation.Horizontal); self.sl_c1.setRange(0,255); self.sl_c1.setValue(50)
        self.sl_c2 = QSlider(Qt.Orientation.Horizontal); self.sl_c2.setRange(0,255); self.sl_c2.setValue(150)
        self.sl_c1.valueChanged.connect(self.escanear); self.sl_c2.valueChanged.connect(self.escanear)
        v2.addWidget(QLabel("Umbral 1:")); v2.addWidget(self.sl_c1)
        v2.addWidget(QLabel("Umbral 2:")); v2.addWidget(self.sl_c2)
        g2.setLayout(v2); lc.addWidget(g2)

        g3 = QGroupBox("💾 Acciones"); v3 = QVBoxLayout()
        for txt, fn in [("🔄 Escanear",self.escanear),("✨ Mejorar",self.mejorar),("💾 Guardar",self.guardar)]:
            btn = QPushButton(txt); btn.clicked.connect(fn); v3.addWidget(btn)
        g3.setLayout(v3); lc.addWidget(g3)
        lc.addStretch(); layout.addWidget(pc, 1)

    def setup_menu(self):
        mb = self.menuBar(); fm = mb.addMenu("&Archivo")
        for txt, fn in [("&Abrir",self.cargar_imagen),("&Guardar",self.guardar),("&Salir",self.close)]:
            a = QAction(txt, self); a.triggered.connect(fn); fm.addAction(a)

    def cargar_imagen(self):
        f,_ = QFileDialog.getOpenFileName(self,"Seleccionar","","Imágenes (*.png *.jpg *.jpeg *.bmp)")
        if f:
            self.imagen_original = cv2.imread(f)
            if self.imagen_original is not None:
                self.mostrar(self.imagen_original, self.lbl_orig); self.escanear()

    def captura_webcam(self):
        cap = cv2.VideoCapture(0); ret, frame = cap.read(); cap.release()
        if ret:
            self.imagen_original = frame
            self.mostrar(frame, self.lbl_orig); self.escanear()

    def ordenar_puntos(self, pts):
        pts = pts.reshape(4,2); s = pts.sum(axis=1); d = np.diff(pts,axis=1)
        ordered = np.zeros((4,2),dtype=np.float32)
        ordered[0]=pts[np.argmin(s)]; ordered[2]=pts[np.argmax(s)]
        ordered[1]=pts[np.argmin(d)]; ordered[3]=pts[np.argmax(d)]
        return ordered

    def escanear(self):
        if self.imagen_original is None: return
        gris = cv2.GaussianBlur(cv2.cvtColor(self.imagen_original,cv2.COLOR_BGR2GRAY),(5,5),0)
        bordes = cv2.Canny(gris, self.sl_c1.value(), self.sl_c2.value())
        k = np.ones((5,5),np.uint8)
        bordes = cv2.morphologyEx(bordes, cv2.MORPH_CLOSE, k)
        cnts,_ = cv2.findContours(bordes,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        if not cnts: return
        cnt = max(cnts, key=cv2.contourArea)
        peri = cv2.arcLength(cnt,True)
        aprox = cv2.approxPolyDP(cnt, 0.02*peri, True)
        if len(aprox) != 4:
            QMessageBox.warning(self,"Aviso","No se detectó un rectángulo claro."); return
        pts = self.ordenar_puntos(aprox)
        tl,tr,br,bl = pts
        w = max(int(np.linalg.norm(tr-tl)), int(np.linalg.norm(br-bl)))
        h = max(int(np.linalg.norm(tr-br)), int(np.linalg.norm(tl-bl)))
        dst = np.array([[0,0],[w-1,0],[w-1,h-1],[0,h-1]],dtype=np.float32)
        M = cv2.getPerspectiveTransform(pts,dst)
        self.imagen_procesada = cv2.warpPerspective(self.imagen_original,M,(w,h))
        self.mostrar(self.imagen_procesada, self.lbl_proc)

    def mejorar(self):
        if self.imagen_procesada is None: return
        gris = cv2.cvtColor(self.imagen_procesada,cv2.COLOR_BGR2GRAY)
        mejor = cv2.adaptiveThreshold(gris,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)
        self.imagen_procesada = cv2.cvtColor(mejor,cv2.COLOR_GRAY2BGR)
        self.mostrar(self.imagen_procesada, self.lbl_proc)

    def guardar(self):
        if self.imagen_procesada is None: return
        nombre = f"escaner_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        cv2.imwrite(nombre, self.imagen_procesada)
        QMessageBox.information(self,"Guardado",f"Guardado como: {nombre}")

    def mostrar(self, img, label):
        rgb = cv2.cvtColor(img,cv2.COLOR_BGR2RGB); h,w,ch = rgb.shape
        qt_img = QImage(rgb.data,w,h,ch*w,QImage.Format.Format_RGB888)
        pix = QPixmap.fromImage(qt_img).scaled(label.size(),
              Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation)
        label.setPixmap(pix)

def main():
    app = QApplication(sys.argv); v = EscanerDocumentos(); v.show(); sys.exit(app.exec())

if __name__ == "__main__": main()