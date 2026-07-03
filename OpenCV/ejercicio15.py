# ejercicio_15_probador_virtual.py
# pip install opencv-contrib-python numpy PyQt6 mediapipe

import sys
import cv2
import mediapipe as mp
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton, QGroupBox,
                             QScrollArea, QGridLayout, QMessageBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap

# Mapeo exacto de los índices de landmarks
INDICES = {
    "ojo_izq": 33, "ojo_der": 362, "nariz": 1, "boca_izq": 61, "boca_der": 291,
    "boca_sup": 0, "frente": 10, "hombro_izq": 11, "hombro_der": 12, "menton": 152
}

def superponer(fondo, overlay, pos):
    x, y = pos
    h, w = overlay.shape[:2]
    # Control de límites de pantalla para evitar desbordes de matriz
    if x < 0 or y < 0 or x + w > fondo.shape[1] or y + h > fondo.shape[0]: 
        return fondo
    if overlay.shape[2] == 4:
        alpha = overlay[:, :, 3:4] / 255.0
        roi = fondo[y:y+h, x:x+w]
        fondo[y:y+h, x:x+w] = (roi * (1 - alpha) + overlay[:, :, :3] * alpha).astype(np.uint8)
    return fondo

# Funciones generadoras de los assets vectoriales/gráficos procedimentales
def mk_gafas():
    img = np.zeros((100, 280, 4), dtype=np.uint8)
    cv2.rectangle(img, (10, 30), (110, 70), (20, 20, 20, 230), -1)
    cv2.rectangle(img, (140, 30), (240, 70), (20, 20, 20, 230), -1)
    cv2.rectangle(img, (110, 45), (140, 55), (20, 20, 20, 255), -1)
    return img

def mk_sombrero():
    img = np.zeros((180, 300, 4), dtype=np.uint8)
    cv2.ellipse(img, (150, 130), (140, 30), 0, 0, 360, (15, 15, 15, 255), -1) # Ala
    cv2.rectangle(img, (75, 20), (225, 120), (15, 15, 15, 255), -1)          # Copa
    cv2.rectangle(img, (75, 100), (225, 120), (0, 0, 220, 255), -1)          # Cinta roja
    return img

def mk_corbata():
    img = np.zeros((240, 100, 4), dtype=np.uint8)
    pts_nudo = np.array([[35, 10], [65, 10], [55, 40], [45, 40]], np.int32)
    cv2.fillPoly(img, [pts_nudo], (0, 0, 180, 255))
    pts_cuerpo = np.array([[45, 40], [55, 40], [70, 200], [50, 230], [30, 200]], np.int32)
    cv2.fillPoly(img, [pts_cuerpo], (0, 0, 180, 255))
    return img

def mk_bigote():
    img = np.zeros((60, 160, 4), dtype=np.uint8)
    cv2.ellipse(img, (45, 30), (35, 15), 0, 0, 360, (10, 10, 10, 255), -1)
    cv2.ellipse(img, (115, 30), (35, 15), 0, 0, 360, (10, 10, 10, 255), -1)
    return img

CATALOGO_IMGS = {"gafas": mk_gafas(), "sombrero": mk_sombrero(), "corbata": mk_corbata(), "bigote": mk_bigote()}

CATALOGO_ITEMS = [
    ("😎 Gafas de Sol", "gafas"),
    ("🎩 Sombrero de Copa", "sombrero"),
    ("👔 Corbata Elegante", "corbata"),
    ("👨 Bigote Clásico", "bigote"),
]

class ProbadorVirtual(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("👗 Probador Virtual – Capítulo 15")
        self.setGeometry(100, 100, 1400, 800)
        
        self.mp_face = mp.solutions.face_mesh
        self.face_mesh = self.mp_face.FaceMesh(refine_landmarks=True, min_detection_confidence=0.6, min_tracking_confidence=0.6)
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(min_detection_confidence=0.6, min_tracking_confidence=0.6)
        
        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer(); self.timer.timeout.connect(self.actualizar); self.timer.start(30)
        self.objeto_activo = "gafas"
        self.ultimo_frame = None
        self.setup_ui()

    def setup_ui(self):
        central = QWidget(); self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        
        pv = QWidget(); lv = QVBoxLayout(pv)
        self.lbl_video = QLabel()
        self.lbl_video.setMinimumSize(850, 650)
        self.lbl_video.setStyleSheet("border:3px solid #444; background:#000;")
        self.lbl_video.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lv.addWidget(self.lbl_video); layout.addWidget(pv, 3)

        pc = QWidget(); pc.setMaximumWidth(380); lc = QVBoxLayout(pc)
        titulo = QLabel("🛍️ PROBADOR AR VIRTUAL")
        titulo.setStyleSheet("font-size:18px; font-weight:bold; color: #2196F3; padding:10px;")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter); lc.addWidget(titulo)

        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        wcat = QWidget(); self.grid = QGridLayout(wcat)
        for idx, (nombre, tipo) in enumerate(CATALOGO_ITEMS):
            btn = QPushButton(nombre)
            btn.setStyleSheet("padding:12px; font-size:14px; font-weight:500;")
            btn.clicked.connect(lambda _, t=tipo: self.seleccionar(t))
            self.grid.addWidget(btn, idx, 0)
        scroll.setWidget(wcat); lc.addWidget(scroll)

        g_prev = QGroupBox("Prenda en Vista"); v_p = QVBoxLayout()
        self.lbl_activo = QLabel("Accesorio: Gafas de Sol")
        self.lbl_activo.setStyleSheet("font-size:14px; font-weight:bold;")
        v_p.addWidget(self.lbl_activo); g_prev.setLayout(v_p); lc.addWidget(g_prev)

        btn_foto = QPushButton("📸 Capturar Outfit")
        btn_foto.clicked.connect(self.tomar_foto)
        btn_foto.setStyleSheet("padding:12px; font-size:14px; background:#4CAF50; color:white; font-weight:bold;")
        lc.addWidget(btn_foto); lc.addStretch(); layout.addWidget(pc, 1)

    def seleccionar(self, tipo):
        self.objeto_activo = tipo
        self.lbl_activo.setText(f"Accesorio: {tipo.capitalize()}")

    def tomar_foto(self):
        if self.ultimo_frame is not None:
            cv2.imwrite("captura_outfit.png", self.ultimo_frame)
            QMessageBox.information(self, "Outfit Guardado", "Se ha guardado tu foto como: captura_outfit.png")

    def aplicar_objeto(self, frame, lm_face, lm_pose, h, w):
        def fp(name):
            idx = INDICES[name]
            lm = lm_face.landmark[idx]
            return int(lm.x * w), int(lm.y * h)
            
        def pp(name):
            if not lm_pose: return None
            idx = INDICES[name]
            lm = lm_pose.landmark[idx]
            return int(lm.x * w), int(lm.y * h)

        oi = fp("ojo_izq"); od = fp("ojo_der"); na = fp("nariz")
        fi = fp("frente"); bi = fp("boca_izq"); bd = fp("boca_der"); bs = fp("boca_sup")
        hi = pp("hombro_izq"); hd = pp("hombro_der")

        # 1. LÓGICA GAFAS
        if self.objeto_activo == "gafas" and oi and od:
            cx, cy = (oi[0] + od[0]) // 2, (oi[1] + od[1]) // 2
            aw = int(abs(od[0] - oi[0]) * 3.0)
            ah = int(aw * 0.35)
            if aw > 10 and ah > 10:
                g = cv2.resize(CATALOGO_IMGS["gafas"], (aw, ah))
                superponer(frame, g, (cx - aw // 2, cy - ah // 2))

        # 2. LÓGICA SOMBRERO
        elif self.objeto_activo == "sombrero" and fi and oi and od:
            cx = fi[0]
            aw = int(abs(od[0] - oi[0]) * 4.5)
            ah = int(aw * 0.6)
            if aw > 10 and ah > 10:
                s = cv2.resize(CATALOGO_IMGS["sombrero"], (aw, ah))
                superponer(frame, s, (cx - aw // 2, fi[1] - ah + 15))

        # 3. LÓGICA CORBATA (Usa Pose Landmarks de hombros)
        elif self.objeto_activo == "corbata" and hi and hd:
            cx = (hi[0] + hd[0]) // 2
            cy = (hi[1] + hd[1]) // 2
            aw = int(abs(hd[0] - hi[0]) * 0.35)
            ah = int(aw * 2.4)
            if aw > 10 and ah > 10:
                c = cv2.resize(CATALOGO_IMGS["corbata"], (aw, ah))
                superponer(frame, c, (cx - aw // 2, cy - 10))

        # 4. LÓGICA BIGOTE
        elif self.objeto_activo == "bigote" and na and bi and bd and bs:
            cx = na[0]
            cy = (na[1] + bs[1]) // 2
            aw = int(abs(bd[0] - bi[0]) * 1.5)
            ah = int(aw * 0.4)
            if aw > 10 and ah > 10:
                b = cv2.resize(CATALOGO_IMGS["bigote"], (aw, ah))
                superponer(frame, b, (cx - aw // 2, cy - ah // 3))

        return frame

    def actualizar(self):
        ret, frame = self.cap.read()
        if not ret: return
        frame = cv2.flip(frame, 1) # Efecto Espejo
        h, w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        res_f = self.face_mesh.process(rgb)
        res_p = self.pose.process(rgb)
        
        if res_f.multi_face_landmarks:
            lm_pose = res_p.pose_landmarks if res_p.pose_landmarks else None
            for lm_face in res_f.multi_face_landmarks:
                frame = self.aplicar_objeto(frame, lm_face, lm_pose, h, w)
                
        self.ultimo_frame = frame.copy()
        
        rgb2 = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB); h2, w2, ch = rgb2.shape
        qt_img = QImage(rgb2.data, w2, h2, ch * w2, QImage.Format.Format_RGB888)
        pix = QPixmap.fromImage(qt_img).scaled(self.lbl_video.size(),
                                              Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.lbl_video.setPixmap(pix)

    def closeEvent(self, event):
        self.cap.release()
        self.face_mesh.close()
        self.pose.close()
        event.accept()

def main():
    app = QApplication(sys.argv)
    v = ProbadorVirtual()
    v.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()