# ejercicio_13_filtros_snapchat.py
# pip install opencv-contrib-python numpy PyQt6 mediapipe

import sys
import cv2
import mediapipe as mp
import numpy as np
import math
import time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton, QGroupBox,
                             QListWidget, QListWidgetItem, QSlider, QCheckBox,
                             QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt, QTimer, QDateTime
from PyQt6.QtGui import QImage, QPixmap

# ── Detector facial ─────────────────────────────────────────────────────────
INDICES = {
    "ojo_izq_ext":33,"ojo_der_ext":362,
    "nariz":1,"boca_izq":61,"boca_der":291,"boca_sup":0,"boca_inf":17,
    "frente_izq":10,"frente_der":338,"menton":152,
}

def crear_gafas():
    img = np.zeros((100,300,4),dtype=np.uint8)
    cv2.rectangle(img,(10,30),(120,70),(20,20,20,220),-1)
    cv2.rectangle(img,(130,30),(240,70),(20,20,20,220),-1)
    cv2.rectangle(img,(120,45),(130,55),(20,20,20,255),-1)
    cv2.line(img,(10,50),(0,65),(20,20,20,255),4)
    cv2.line(img,(240,50),(299,65),(20,20,20,255),4)
    cv2.ellipse(img,(50,42),(12,6),30,0,180,(200,200,255,70),-1)
    cv2.ellipse(img,(170,42),(12,6),30,0,180,(200,200,255,70),-1)
    return img

def crear_sombrero():
    img = np.zeros((180,300,4),dtype=np.uint8)
    cv2.ellipse(img,(150,130),(140,30),0,0,360,(30,20,10,255),-1)
    cv2.rectangle(img,(90,20),(210,130),(30,20,10,255),-1)
    cv2.rectangle(img,(90,105),(210,120),(0,30,200,255),-1)
    return img

def crear_bigote():
    img = np.zeros((60,150,4),dtype=np.uint8)
    cv2.ellipse(img,(40,30),(25,12),0,0,360,(0,0,0,255),-1)
    cv2.ellipse(img,(110,30),(25,12),0,0,360,(0,0,0,255),-1)
    return img

def superponer(fondo, overlay, pos):
    x,y = pos; h,w = overlay.shape[:2]
    if x<0 or y<0 or x+w>fondo.shape[1] or y+h>fondo.shape[0]: return fondo
    if overlay.shape[2]==4:
        alpha = overlay[:,:,3:4]/255.0
        roi = fondo[y:y+h,x:x+w]
        fondo[y:y+h,x:x+w] = (roi*(1-alpha)+overlay[:,:,:3]*alpha).astype(np.uint8)
    return fondo

GAFAS = crear_gafas(); SOMBRERO = crear_sombrero(); BIGOTE = crear_bigote()

class FiltrosSnapchat(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎭 Filtros SnapAR – Capítulo 13")
        self.setGeometry(100,100,1400,800)
        self.mp_face = mp.solutions.face_mesh
        self.face_mesh = self.mp_face.FaceMesh(refine_landmarks=True,
                                                min_detection_confidence=0.5,min_tracking_confidence=0.5)
        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer(); self.timer.timeout.connect(self.actualizar); self.timer.start(30)
        self.filtro = "gafas"; self.ultimo_frame = None
        self.grabando = False; self.video_writer = None
        self.setup_ui()

    def setup_ui(self):
        central = QWidget(); self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        pv = QWidget(); lv = QVBoxLayout(pv)
        self.lbl_video = QLabel()
        self.lbl_video.setMinimumSize(900,600)
        self.lbl_video.setStyleSheet("border:3px solid #444; background:#111;")
        self.lbl_video.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lv.addWidget(self.lbl_video)
        tb = QHBoxLayout()
        for txt, fn in [("📸 Capturar",self.capturar),("⏺️ Grabar",self.toggle_grabar)]:
            b = QPushButton(txt); b.clicked.connect(fn); tb.addWidget(b)
        self.btn_grabar = [w for w in tb.children() if isinstance(w,QPushButton)]
        lv.addLayout(tb); layout.addWidget(pv, 3)

        pc = QWidget(); pc.setMaximumWidth(350); lc = QVBoxLayout(pc)
        titulo = QLabel("🎨 GALERÍA DE FILTROS")
        titulo.setStyleSheet("font-size:18px; font-weight:bold; padding:10px;")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter); lc.addWidget(titulo)
        self.lista = QListWidget()
        filtros = [("😎 Gafas","gafas"),("🎩 Sombrero","sombrero"),("👨 Bigote","bigote"),
                   ("😎+🎩 Gafas+Sombrero","gafas_sombrero"),("Todos","todos")]
        for nombre, fid in filtros:
            item = QListWidgetItem(nombre); item.setData(Qt.ItemDataRole.UserRole,fid); self.lista.addItem(item)
        self.lista.currentItemChanged.connect(lambda c,p: setattr(self,'filtro',c.data(Qt.ItemDataRole.UserRole)) if c else None)
        lc.addWidget(self.lista)
        g_stats = QGroupBox("📊 Info"); v_s = QVBoxLayout()
        self.stats_label = QLabel("FPS: --\nFiltro activo: --"); v_s.addWidget(self.stats_label)
        g_stats.setLayout(v_s); lc.addWidget(g_stats)
        lc.addStretch(); layout.addWidget(pc, 1)
        self.lista.setCurrentRow(0)

    def aplicar_filtros(self, frame, lm, h, w):
        def pt(name): idx=INDICES[name]; return int(lm.landmark[idx].x*w),int(lm.landmark[idx].y*h)
        oi,od = pt("ojo_izq_ext"), pt("ojo_der_ext")
        fi,fd = pt("frente_izq"), pt("frente_der")
        na,bi,bd,bs = pt("nariz"), pt("boca_izq"), pt("boca_der"), pt("boca_sup")
        ancho_ojos = max(abs(od[0]-oi[0]),30)
        # Gafas
        if self.filtro in ["gafas","gafas_sombrero","todos"]:
            cx=(oi[0]+od[0])//2; cy=(oi[1]+od[1])//2
            aw=int(ancho_ojos*2.8); ah=max(int(aw*0.35),20)
            g=cv2.resize(GAFAS,(aw,ah)); superponer(frame,g,(cx-aw//2,cy-ah//2-10))
        # Sombrero
        if self.filtro in ["sombrero","gafas_sombrero","todos"]:
            cx=(fi[0]+fd[0])//2; aw=int(abs(fd[0]-fi[0])*2.0); ah=int(aw*0.65)
            s=cv2.resize(SOMBRERO,(max(aw,10),max(ah,10))); superponer(frame,s,(cx-aw//2,fi[1]-ah+30))
        # Bigote
        if self.filtro in ["bigote","todos"]:
            cx=na[0]; cy=(na[1]+bs[1])//2
            aw=max(int(abs(bd[0]-bi[0])*1.2),30); ah=max(aw//2,15)
            b=cv2.resize(BIGOTE,(aw,ah)); superponer(frame,b,(cx-aw//2,cy-ah//2))
        return frame

    def actualizar(self):
        ret, frame = self.cap.read()
        if not ret: return
        self.ultimo_frame = frame.copy()
        h,w = frame.shape[:2]
        rgb = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        res = self.face_mesh.process(rgb)
        if res.multi_face_landmarks:
            for lm in res.multi_face_landmarks:
                frame = self.aplicar_filtros(frame,lm,h,w)
        self.stats_label.setText(f"FPS: 30\nFiltro: {self.filtro}")
        if self.grabando and self.video_writer: self.video_writer.write(frame)
        cv2.putText(frame,f"Filtro: {self.filtro}",(10,30),cv2.FONT_HERSHEY_SIMPLEX,0.7,(255,255,255),2)
        rgb2 = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB); h2,w2,ch = rgb2.shape
        qt_img = QImage(rgb2.data,w2,h2,ch*w2,QImage.Format.Format_RGB888)
        pix = QPixmap.fromImage(qt_img).scaled(self.lbl_video.size(),
              Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation)
        self.lbl_video.setPixmap(pix)

    def capturar(self):
        if self.ultimo_frame is not None:
            ts = QDateTime.currentDateTime().toString("yyyyMMdd_hhmmss")
            nombre = f"filtro_{self.filtro}_{ts}.png"
            cv2.imwrite(nombre, self.ultimo_frame)
            QMessageBox.information(self,"Guardado",f"Foto guardada: {nombre}")

    def toggle_grabar(self):
        if not self.grabando:
            ts = QDateTime.currentDateTime().toString("yyyyMMdd_hhmmss")
            nombre = f"video_{self.filtro}_{ts}.avi"
            cap = self.cap; fw=int(cap.get(3)); fh=int(cap.get(4))
            self.video_writer = cv2.VideoWriter(nombre, cv2.VideoWriter_fourcc(*'XVID'), 20.0, (fw,fh))
            self.grabando = True; print(f"⏺️ Grabando: {nombre}")
        else:
            if self.video_writer: self.video_writer.release()
            self.grabando = False; print("⏹️ Grabación detenida")

    def closeEvent(self, event):
        if self.grabando and self.video_writer: self.video_writer.release()
        self.cap.release(); self.face_mesh.close(); event.accept()

def main():
    app = QApplication(sys.argv); app.setStyle('Fusion')
    v = FiltrosSnapchat(); v.show(); sys.exit(app.exec())

if __name__ == "__main__": main()