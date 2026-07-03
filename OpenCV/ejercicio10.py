# pip install opencv-contrib-python numpy PyQt6#
# El marcador ArUco se muestra DENTRO de la app.
# Apunta la cámara a la imagen del marcador que aparece en el panel derecho.

import sys
import os
import cv2
import cv2.aruco as aruco
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton, QGroupBox,
                             QListWidget, QSlider, QCheckBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap


def crear_marco_neon():
    img = np.zeros((400, 400, 4), dtype=np.uint8)
    for i, c in enumerate([(0,255,255,255),(255,0,255,255),(255,255,0,255)]):
        d = i * 6
        cv2.rectangle(img,(50+d,50+d),(350-d,350-d),c,2)
    return img

def crear_marco_flores():
    img = np.zeros((400, 400, 4), dtype=np.uint8)
    for x, y, c in [(50,50,(255,192,203,200)),(350,50,(255,255,0,200)),
                    (350,350,(173,216,230,200)),(50,350,(255,182,193,200))]:
        cv2.circle(img, (x,y), 45, c, -1)
    cv2.rectangle(img,(20,20),(380,380),(255,255,255,200),4)
    return img

def crear_marco_geometrico():
    img = np.zeros((400, 400, 4), dtype=np.uint8)
    for i in range(0,400,40):
        for j in range(0,400,40):
            pts = np.array([[i,j],[i+40,j],[i+20,j+20]],np.int32).reshape(-1,1,2)
            c = (0,255,0,100) if (i+j)%80==0 else (255,0,0,100)
            cv2.fillPoly(img,[pts],c)
    cv2.rectangle(img,(10,10),(390,390),(255,255,255,255),5)
    return img


class MarcoFotoAR(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🖼️ Marco de Foto AR – Capítulo 10")
        self.setGeometry(100, 100, 1400, 820)

        self.diccionario = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)
        self.detector    = aruco.ArucoDetector(self.diccionario, aruco.DetectorParameters())
        self.catalogo    = {"Marco Neón":crear_marco_neon(),
                            "Marco Flores":crear_marco_flores(),
                            "Marco Geométrico":crear_marco_geometrico()}
        self.imagen_actual = crear_marco_neon()
        self.escala = 1.0
        self.borde  = True

        # Guardar marcadores en disco
        carpeta = os.path.dirname(os.path.abspath(__file__))
        for i in range(4):
            m = np.zeros((400,400),dtype=np.uint8)
            aruco.generateImageMarker(self.diccionario, i, 400, m, 1)
            cv2.imwrite(os.path.join(carpeta, f"marcador_{i}.png"), m)
        print(f" Marcadores guardados en: {carpeta}")

        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar)
        self.timer.start(30)
        self.setup_ui()

    def setup_ui(self):
        central = QWidget(); self.setCentralWidget(central)
        layout  = QHBoxLayout(central)

        # Panel video (izquierda)
        self.lbl_video = QLabel()
        self.lbl_video.setMinimumSize(780, 600)
        self.lbl_video.setStyleSheet("background:#111; border:2px solid #555;")
        self.lbl_video.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_video, 3)

        # Panel derecho
        pc = QWidget(); pc.setMaximumWidth(420)
        lc = QVBoxLayout(pc)

        # ── Instrucción ─────────────────────────────────────────────
        g0 = QGroupBox(" QUÉ TIENES QUE HACER")
        v0 = QVBoxLayout()
        ins = QLabel(
            "👇 APUNTA LA CÁMARA HACIA\n"
            "    EL CUADRADO NEGRO/BLANCO\n"
            "    QUE APARECE ABAJO\n\n"
            "Ese cuadrado ES el marcador ArUco.\n"
            "Cuando la cámara lo vea, el marco\n"
            "decorativo aparecerá sobre él."
        )
        ins.setStyleSheet(
            "font-size:14px; font-weight:bold; color:#004d00;"
            "background:#e8f5e9; padding:8px; border-radius:4px;")
        v0.addWidget(ins); g0.setLayout(v0); lc.addWidget(g0)

        # ── IMAGEN DEL MARCADOR ─────────────────────────────────────
        g_m = QGroupBox("👇 MUESTRA ESTO A LA CÁMARA")
        g_m.setStyleSheet("QGroupBox{font-weight:bold;color:#cc0000;font-size:14px;}")
        v_m = QVBoxLayout()
        self.lbl_marcador = QLabel()
        self.lbl_marcador.setFixedSize(280, 280)
        self.lbl_marcador.setStyleSheet("border:4px solid #cc0000; background:white;")
        self.lbl_marcador.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v_m.addWidget(self.lbl_marcador, alignment=Qt.AlignmentFlag.AlignCenter)
        self.lbl_id_marker = QLabel("Mostrando: Marcador ID 0")
        self.lbl_id_marker.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_id_marker.setStyleSheet("font-size:12px; color:#555;")
        v_m.addWidget(self.lbl_id_marker)
        hl_btn = QHBoxLayout()
        for i in range(4):
            b = QPushButton(f"ID {i}"); b.clicked.connect(lambda _, x=i: self.mostrar_marcador(x))
            hl_btn.addWidget(b)
        v_m.addLayout(hl_btn)
        g_m.setLayout(v_m); lc.addWidget(g_m)

        # ── Estado ──────────────────────────────────────────────────
        self.lbl_status = QLabel(" Buscando marcador...")
        self.lbl_status.setStyleSheet("color:#555; font-size:12px; padding:4px;")
        lc.addWidget(self.lbl_status)

        # ── Catálogo de marcos ───────────────────────────────────────
        g1 = QGroupBox("🖼️ Elige el marco decorativo")
        v1 = QVBoxLayout()
        self.lista = QListWidget()
        for nombre in self.catalogo: self.lista.addItem(nombre)
        self.lista.currentTextChanged.connect(self.seleccionar_marco)
        self.lista.setCurrentRow(0)
        v1.addWidget(self.lista)
        g1.setLayout(v1); lc.addWidget(g1)

        # ── Ajustes ─────────────────────────────────────────────────
        g2 = QGroupBox(" Ajustes"); v2 = QVBoxLayout()
        v2.addWidget(QLabel("Escala del marco:"))
        sl = QSlider(Qt.Orientation.Horizontal); sl.setRange(50,200); sl.setValue(100)
        sl.valueChanged.connect(lambda v: setattr(self,'escala',v/100))
        v2.addWidget(sl)
        cb = QCheckBox("Borde dorado"); cb.setChecked(True)
        cb.stateChanged.connect(lambda v: setattr(self,'borde',bool(v)))
        v2.addWidget(cb)
        g2.setLayout(v2); lc.addWidget(g2)
        lc.addStretch(); layout.addWidget(pc, 1)

        # Mostrar el marcador 0 al iniciar
        self.mostrar_marcador(0)

    def mostrar_marcador(self, id_m):
        """Dibuja el marcador ArUco en el panel para que el usuario lo muestre a la cámara."""
        m = np.zeros((400,400), dtype=np.uint8)
        aruco.generateImageMarker(self.diccionario, id_m, 400, m, 1)
        qimg = QImage(m.data, 400, 400, 400, QImage.Format.Format_Grayscale8)
        pix  = QPixmap.fromImage(qimg).scaled(
            270, 270, Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation)
        self.lbl_marcador.setPixmap(pix)
        self.lbl_id_marker.setText(f"Mostrando: Marcador ID {id_m}")

    def seleccionar_marco(self, nombre):
        if nombre in self.catalogo:
            self.imagen_actual = self.catalogo[nombre].copy()

    def superponer(self, frame, img, esquina):
        h_o, w_o = img.shape[:2]
        src = np.float32([[0,0],[w_o,0],[w_o,h_o],[0,h_o]])
        dst = esquina.astype(np.float32)
        M, _ = cv2.findHomography(src, dst)
        if M is None: return frame
        warped = cv2.warpPerspective(img, M, (frame.shape[1], frame.shape[0]))
        if img.shape[2] == 4:
            alpha = warped[:,:,3:4]/255.0
            for c in range(3):
                frame[:,:,c] = (frame[:,:,c]*(1-alpha[:,:,0]) +
                                warped[:,:,c]*alpha[:,:,0]).astype(np.uint8)
        return frame

    def actualizar(self):
        ret, frame = self.cap.read()
        if not ret: return
        esq, ids, _ = self.detector.detectMarkers(frame)
        if ids is not None and self.imagen_actual is not None:
            aruco.drawDetectedMarkers(frame, esq, ids)
            aw = max(int(self.imagen_actual.shape[1]*self.escala),10)
            ah = max(int(self.imagen_actual.shape[0]*self.escala),10)
            img_ajustada = cv2.resize(self.imagen_actual,(aw,ah))
            frame = self.superponer(frame, img_ajustada, esq[0][0])
            if self.borde:
                cv2.polylines(frame,[esq[0][0].astype(int)],True,(255,215,0),3)
            self.lbl_status.setText(f" Marcador detectado: ID {list(ids.flatten())}")
        else:
            self.lbl_status.setText(" Apunta la cámara al cuadrado del panel derecho ↗")
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qt = QImage(rgb.data, w, h, ch*w, QImage.Format.Format_RGB888)
        pix = QPixmap.fromImage(qt).scaled(
            self.lbl_video.size(), Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation)
        self.lbl_video.setPixmap(pix)

    def closeEvent(self, event): self.cap.release(); event.accept()


def main():
    app = QApplication(sys.argv)
    v = MarcoFotoAR(); v.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()