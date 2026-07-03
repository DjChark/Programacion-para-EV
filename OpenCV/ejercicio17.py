# ejercicio_17_dashboard_performance.py
# pip install opencv-contrib-python numpy PyQt6 mediapipe psutil

import sys
import cv2
import numpy as np
import time
import psutil
from collections import deque
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton, QGroupBox,
                             QGridLayout, QProgressBar, QCheckBox, QSpinBox,
                             QTabWidget)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap, QPainter, QColor, QPen

# --- NUEVOS IMPORTS DE MEDIAPIPE ---
import mediapipe as mp
from mediapipe.python.solutions import hands as mp_hands
from mediapipe.python.solutions import drawing_utils as mp_draw


# ── Hilo de captura ───────────────────────────────────────────────────────
class CapturaThread(QThread):
    frame_listo = pyqtSignal(object)
    def __init__(self):
        super().__init__()
        self.running=True
        self.cap=cv2.VideoCapture(0)
    def run(self):
        while self.running:
            ret,frame = self.cap.read()
            if ret: self.frame_listo.emit(frame)
            else: self.msleep(5)
    def stop(self): 
        self.running=False
        self.wait()
        self.cap.release()


# ── Hilo de procesamiento MediaPipe ──────────────────────────────────────
class ProcThread(QThread):
    resultado_listo = pyqtSignal(object, object, float)
    def __init__(self):
        super().__init__()
        self.running=True
        self.frame=None
        # --- INICIALIZACIÓN ACTUALIZADA ---
        self.hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.5)
        
    def set_frame(self, f): self.frame=f
    
    def run(self):
        while self.running:
            if self.frame is not None:
                t0=time.perf_counter()
                small=cv2.resize(self.frame,(640,360))
                rgb=cv2.cvtColor(small,cv2.COLOR_BGR2RGB)
                res=self.hands.process(rgb)
                latencia=(time.perf_counter()-t0)*1000
                self.resultado_listo.emit(self.frame.copy(),res,latencia)
                self.frame=None
            self.msleep(8)
            
    def stop(self): 
        self.running=False
        self.wait()
        self.hands.close()


class DashboardPerformance(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📊 Dashboard de Performance – Capítulo 17")
        self.setGeometry(100,100,1400,800)
        self.hist_fps   = deque(maxlen=100)
        self.hist_cpu   = deque(maxlen=100)
        self.hist_lat   = deque(maxlen=100)
        self.hist_mem   = deque(maxlen=100)
        self.proc       = psutil.Process()
        self.t_ultimo   = time.perf_counter()
        self.mostrar_graficos = True

        self.captura  = CapturaThread()
        self.proceso  = ProcThread()
        self.captura.frame_listo.connect(self.proceso.set_frame)
        self.proceso.resultado_listo.connect(self.on_resultado)
        self.captura.start()
        self.proceso.start()

        self.timer_metricas = QTimer()
        self.timer_metricas.timeout.connect(self.actualizar_metricas)
        self.timer_metricas.start(500)
        self.setup_ui()

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)

        # Video
        pv = QWidget()
        lv = QVBoxLayout(pv)
        self.lbl_video = QLabel()
        self.lbl_video.setMinimumSize(700,500)
        self.lbl_video.setStyleSheet("background:#111; border:2px solid #444;")
        self.lbl_video.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lv.addWidget(self.lbl_video)
        self.lbl_gesto = QLabel("Gesto: --")
        self.lbl_gesto.setStyleSheet("font-size:14px; padding:4px;")
        lv.addWidget(self.lbl_gesto)
        layout.addWidget(pv, 3)

        # Panel métricas
        pc = QWidget()
        pc.setMaximumWidth(420)
        lc = QVBoxLayout(pc)
        lc.addWidget(QLabel("📊 MONITOR EN TIEMPO REAL"))

        grid = QGridLayout()
        self.lbl_fps = QLabel("0")
        self.pb_fps = QProgressBar()
        self.pb_fps.setRange(0,60)
        
        self.lbl_cpu = QLabel("0%")
        self.pb_cpu = QProgressBar()
        self.pb_cpu.setRange(0,100)
        
        self.lbl_lat = QLabel("0ms")
        self.pb_lat = QProgressBar()
        self.pb_lat.setRange(0,200)
        
        self.lbl_mem = QLabel("0MB")
        self.pb_mem = QProgressBar()
        self.pb_mem.setRange(0,500)
        
        for i,(titulo,lbl,pb) in enumerate([("🎮 FPS",self.lbl_fps,self.pb_fps),
                                            ("⚙️ CPU",self.lbl_cpu,self.pb_cpu),
                                            ("⏱️ Latencia",self.lbl_lat,self.pb_lat),
                                            ("💾 Memoria",self.lbl_mem,self.pb_mem)]):
            g=QGroupBox(titulo)
            v=QVBoxLayout()
            lbl.setStyleSheet("font-size:22px; font-weight:bold;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            v.addWidget(lbl)
            v.addWidget(pb)
            g.setLayout(v)
            grid.addWidget(g, i//2, i%2)
        lc.addLayout(grid)

        # Gráfico
        self.canvas = QLabel()
        self.canvas.setMinimumHeight(200)
        self.canvas.setStyleSheet("background:#1e1e1e; border:1px solid #444;")
        lc.addWidget(self.canvas)

        # Controles
        hl = QHBoxLayout()
        cb = QCheckBox("Mostrar gráfico")
        cb.setChecked(True)
        cb.toggled.connect(lambda v: setattr(self,'mostrar_graficos',v))
        hl.addWidget(cb)
        btn_r = QPushButton("🔄 Reset")
        btn_r.clicked.connect(self.reset)
        hl.addWidget(btn_r)
        lc.addLayout(hl)
        lc.addStretch()
        layout.addWidget(pc, 1)

    def on_resultado(self, frame, res, latencia):
        self.hist_lat.append(latencia)
        t_ahora = time.perf_counter()
        fps = 1.0/(t_ahora - self.t_ultimo + 1e-6)
        self.t_ultimo = t_ahora
        self.hist_fps.append(fps)
        h,w = frame.shape[:2]
        
        if res.multi_hand_landmarks:
            for hl in res.multi_hand_landmarks:
                # --- DIBUJO ACTUALIZADO ---
                mp_draw.draw_landmarks(frame, hl, mp_hands.HAND_CONNECTIONS)
            self.lbl_gesto.setText("✋ Mano detectada")
        else: 
            self.lbl_gesto.setText("Gesto: --")
            
        rgb = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        h2,w2,ch=rgb.shape
        qt_img = QImage(rgb.data,w2,h2,ch*w2,QImage.Format.Format_RGB888)
        pix = QPixmap.fromImage(qt_img).scaled(self.lbl_video.size(),
              Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation)
        self.lbl_video.setPixmap(pix)

    def actualizar_metricas(self):
        cpu = self.proc.cpu_percent()
        mem = self.proc.memory_info().rss/1024/1024
        self.hist_cpu.append(cpu)
        self.hist_mem.append(mem)
        fps = self.hist_fps[-1] if self.hist_fps else 0
        lat = self.hist_lat[-1] if self.hist_lat else 0
        self.lbl_fps.setText(f"{fps:.1f}"); self.pb_fps.setValue(min(60,int(fps)))
        self.lbl_cpu.setText(f"{cpu:.1f}%"); self.pb_cpu.setValue(int(cpu))
        self.lbl_lat.setText(f"{lat:.1f}ms"); self.pb_lat.setValue(min(200,int(lat)))
        self.lbl_mem.setText(f"{mem:.1f}MB"); self.pb_mem.setValue(min(500,int(mem)))
        if self.mostrar_graficos: self.dibujar_grafico()

    def dibujar_grafico(self):
        pix = QPixmap(self.canvas.width() or 400, self.canvas.height() or 200)
        pix.fill(QColor(30,30,30))
        p = QPainter(pix)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        W,H = pix.width(),pix.height()
        p.setPen(QPen(QColor(60,60,60),1))
        
        for x in range(0,W,50): p.drawLine(x,0,x,H)
        for y in range(0,H,40): p.drawLine(0,y,W,y)
        
        def linea(datos, color):
            if len(datos)<2: return
            mx = max(datos) or 1
            pts = [(int(i/len(datos)*W),int(H-(v/mx)*(H-20)-10)) for i,v in enumerate(datos)]
            p.setPen(QPen(color,2))
            for i in range(len(pts)-1): p.drawLine(pts[i][0],pts[i][1],pts[i+1][0],pts[i+1][1])
            
        linea(list(self.hist_fps),QColor(0,255,0))
        linea(list(self.hist_cpu),QColor(255,80,80))
        linea(list(self.hist_lat),QColor(255,200,0))
        p.end()
        self.canvas.setPixmap(pix)

    def reset(self):
        for d in [self.hist_fps,self.hist_cpu,self.hist_lat,self.hist_mem]: d.clear()

    def closeEvent(self, event):
        self.captura.stop()
        self.proceso.stop()
        event.accept()

def main():
    app = QApplication(sys.argv)
    v = DashboardPerformance()
    v.show()
    sys.exit(app.exec())

if __name__ == "__main__": 
    main()