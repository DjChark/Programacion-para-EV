# ejercicio_12_camara_calibrada.py
# pip install opencv-contrib-python numpy PyQt6

import sys
import cv2
import cv2.aruco as aruco
import numpy as np
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton, QGroupBox,
                             QFileDialog, QMessageBox, QComboBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap


class CamaraCalibrada(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📷 Cámara Calibrada – Capítulo 12")
        self.setGeometry(100,100,1400,800)
        self.cam_matrix = None; self.dist = None; self.usar_calibracion = False
        self.modo = "lado_a_lado"; self.frame_orig = None; self.frame_corr = None
        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer(); self.timer.timeout.connect(self.actualizar); self.timer.start(30)
        self.setup_ui()

    def setup_ui(self):
        central = QWidget(); self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        self.lbl_video = QLabel()
        self.lbl_video.setMinimumSize(900,600)
        self.lbl_video.setStyleSheet("background:#111; border:2px solid #444;")
        self.lbl_video.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_video, 3)

        pc = QWidget(); pc.setMaximumWidth(350); lc = QVBoxLayout(pc)

        g1 = QGroupBox("📂 Calibración"); v1 = QVBoxLayout()
        btn_l = QPushButton("Cargar parámetros (NPZ/JSON)"); btn_l.clicked.connect(self.cargar); v1.addWidget(btn_l)
        self.lbl_estado = QLabel("❌ No calibrada")
        self.lbl_estado.setStyleSheet("color:red; font-weight:bold;"); v1.addWidget(self.lbl_estado)
        g1.setLayout(v1); lc.addWidget(g1)

        g2 = QGroupBox("👁️ Visualización"); v2 = QVBoxLayout()
        self.combo_modo = QComboBox()
        self.combo_modo.addItems(["lado_a_lado","deslizante"])
        self.combo_modo.currentTextChanged.connect(lambda v: setattr(self,'modo',v))
        v2.addWidget(self.combo_modo)
        btn_act = QPushButton("🔧 Activar/Desactivar corrección")
        btn_act.setCheckable(True); btn_act.toggled.connect(self.toggle)
        v2.addWidget(btn_act); g2.setLayout(v2); lc.addWidget(g2)

        g3 = QGroupBox("ℹ️ Parámetros"); v3 = QVBoxLayout()
        self.info_text = QLabel("Sin datos"); v3.addWidget(self.info_text)
        g3.setLayout(v3); lc.addWidget(g3)

        g4 = QGroupBox("📝 Cómo calibrar"); v4 = QVBoxLayout()
        v4.addWidget(QLabel("1. Imprime un tablero de ajedrez\n2. Usa cv2.findChessboardCorners\n"
                             "3. Guarda con np.savez('cal.npz',\n   matriz_camara=M, dist_coefs=D)\n"
                             "4. Carga aquí el archivo .npz"))
        g4.setLayout(v4); lc.addWidget(g4)
        lc.addStretch(); layout.addWidget(pc, 1)

    def cargar(self):
        f,_ = QFileDialog.getOpenFileName(self,"Cargar","","NPZ (*.npz);;JSON (*.json)")
        if not f: return
        try:
            if f.endswith('.npz'):
                datos = np.load(f)
                self.cam_matrix = datos['matriz_camara']
                self.dist = datos['dist_coefs']
            else:
                with open(f,'r') as fp: datos = json.load(fp)
                self.cam_matrix = np.array(datos['matriz_camara'])
                self.dist = np.array(datos['dist_coefs'])
            self.lbl_estado.setText("✅ Calibrada"); self.lbl_estado.setStyleSheet("color:green; font-weight:bold;")
            fx,fy = self.cam_matrix[0,0], self.cam_matrix[1,1]
            k1 = self.dist.ravel()[0]
            self.info_text.setText(f"fx:{fx:.1f} fy:{fy:.1f}\nk1:{k1:.3f}")
            QMessageBox.information(self,"Éxito","Parámetros cargados.")
        except Exception as e:
            QMessageBox.critical(self,"Error",str(e))

    def toggle(self, act):
        self.usar_calibracion = act and self.cam_matrix is not None
        if act and self.cam_matrix is None:
            QMessageBox.warning(self,"Atención","Carga primero los parámetros.")

    def corregir(self, frame):
        if not self.usar_calibracion or self.cam_matrix is None: return frame
        h,w = frame.shape[:2]
        nueva_matrix, roi = cv2.getOptimalNewCameraMatrix(self.cam_matrix,self.dist,(w,h),1,(w,h))
        corr = cv2.undistort(frame,self.cam_matrix,self.dist,None,nueva_matrix)
        x,y,rw,rh = roi
        return corr[y:y+rh,x:x+rw] if all([rw,rh]) else corr

    def actualizar(self):
        ret, frame = self.cap.read()
        if not ret: return
        self.frame_orig = frame.copy()
        if self.usar_calibracion:
            self.frame_corr = self.corregir(frame)
            if self.modo == "lado_a_lado":
                fc = cv2.resize(self.frame_corr,(frame.shape[1],frame.shape[0]))
                mostrar = np.hstack([frame,fc])
                cv2.putText(mostrar,"ORIGINAL",(10,30),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)
                cv2.putText(mostrar,"CORREGIDA",(frame.shape[1]+10,30),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2)
            else:
                fc = cv2.resize(self.frame_corr,(frame.shape[1],frame.shape[0]))
                mid = frame.shape[1]//2
                mostrar = frame.copy(); mostrar[:,mid:] = fc[:,mid:]
                cv2.line(mostrar,(mid,0),(mid,frame.shape[0]),(255,255,255),3)
        else:
            mostrar = frame; cv2.putText(mostrar,"SIN CALIBRAR",(10,30),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)
        rgb = cv2.cvtColor(mostrar, cv2.COLOR_BGR2RGB); h,w,ch = rgb.shape
        qt_img = QImage(rgb.data,w,h,ch*w,QImage.Format.Format_RGB888)
        pix = QPixmap.fromImage(qt_img).scaled(self.lbl_video.size(),
              Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation)
        self.lbl_video.setPixmap(pix)

    def closeEvent(self, event): self.cap.release(); event.accept()

def main():
    app = QApplication(sys.argv); v = CamaraCalibrada(); v.show(); sys.exit(app.exec())

if __name__ == "__main__": main()