# ejercicio14_v3.py
# pip install opencv-contrib-python numpy PyQt6
# Los marcadores ArUco se muestran DENTRO de la app.
# Pestaña "Marcadores" → elige uno → apunta la cámara a ese cuadrado.

import sys
import os
import cv2
import cv2.aruco as aruco
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton, QGroupBox,
                             QTabWidget, QTextEdit, QMessageBox, QGridLayout,
                             QScrollArea)
from PyQt6.QtCore import Qt, QTimer, QDateTime
from PyQt6.QtGui import QImage, QPixmap, QFont


def crear_contenido(id_m):
    colores = [(255,80,0),(0,180,100),(0,80,255),(200,0,200)]
    c = colores[id_m % len(colores)]
    img = np.zeros((200,350,4), dtype=np.uint8)
    img[:,:,:3] = c; img[:,:,3] = 170
    textos = {
        0: ["=== PORTADA ===","Libro AR Interactivo","Capitulo 0"],
        1: ["=== PORTADA ===","Bienvenido al libro","ID: 1"],
        2: ["CAP 1: ANIMALES","Leon | Tigre | Aguila","ID: 2"],
        3: ["CAP 1: ANIMALES","Perro | Gato | Pez","ID: 3"],
        4: ["CAP 2: VEHICULOS","Auto | Avion | Barco","ID: 4"],
        5: ["CAP 2: VEHICULOS","Tren | Moto | Bus","ID: 5"],
        6: ["CAP 3: NATURALEZA","Rios | Montanas","ID: 6"],
        7: ["CAP 3: NATURALEZA","Flores | Arboles","ID: 7"],
    }
    for i, t in enumerate(textos.get(id_m, [f"Pagina {id_m+1}","","ID: "+str(id_m)])):
        cv2.putText(img, t, (12, 55+i*52), cv2.FONT_HERSHEY_SIMPLEX, 0.65,
                    (255,255,255,255), 2)
    return img


class LibroAR(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(" Libro AR Interactivo – Capítulo 14")
        self.setGeometry(100, 100, 1440, 860)

        self.diccionario = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)
        self.detector    = aruco.ArucoDetector(self.diccionario, aruco.DetectorParameters())
        self.contenidos  = {i: crear_contenido(i) for i in range(8)}

        # Guardar marcadores en disco
        carpeta = os.path.dirname(os.path.abspath(__file__))
        for i in range(8):
            m = np.zeros((400,400), dtype=np.uint8)
            aruco.generateImageMarker(self.diccionario, i, 400, m, 1)
            cv2.imwrite(os.path.join(carpeta, f"marcador_{i}.png"), m)
        print(f" Marcadores guardados en: {carpeta}")

        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar)
        self.timer.start(30)

        self.ultimo_frame      = None
        self.marcadores_vistos = set()
        self.id_panel          = 0   # marcador que se muestra en el panel
        self.setup_ui()
        self.actualizar_panel_marcador()

    # ────────────────────────────────────────────────────────────────
    def setup_ui(self):
        central = QWidget(); self.setCentralWidget(central)
        layout  = QHBoxLayout(central)

        # Video
        pv = QWidget(); lv = QVBoxLayout(pv)
        self.lbl_video = QLabel()
        self.lbl_video.setMinimumSize(880, 650)
        self.lbl_video.setStyleSheet("background:#0a0a0a; border:3px solid #333;")
        self.lbl_video.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lv.addWidget(self.lbl_video)
        self.lbl_status = QLabel("⏳ Apunta la cámara al marcador del panel derecho")
        self.lbl_status.setStyleSheet("font-size:13px; color:#aaa; padding:4px;")
        lv.addWidget(self.lbl_status)
        layout.addWidget(pv, 3)

        # Panel derecho
        pc = QWidget(); pc.setMaximumWidth(410); lc = QVBoxLayout(pc)
        titulo = QLabel("LIBRO AR")
        titulo.setFont(QFont("Arial",16,QFont.Weight.Bold))
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("color:#4CAF50; padding:8px;")
        lc.addWidget(titulo)

        tabs = QTabWidget()

        # ── Pestaña 1: MARCADORES (la más importante) ───────────────
        tab_m = QWidget(); v_m = QVBoxLayout(tab_m)

        ins = QLabel(
            " Apunta la cámara\n"
            "    AL CUADRADO DE ABAJO\n"
            "Ese cuadrado ES el marcador.\n"
            "Verás el contenido del libro\n"
            "aparecer sobre él."
        )
        ins.setStyleSheet(
            "font-size:13px;font-weight:bold;color:#4a4400;"
            "background:#fffde7;padding:8px;border-radius:4px;")
        v_m.addWidget(ins)

        # Imagen grande del marcador
        gm = QGroupBox(" MUESTRA ESTO A LA CÁMARA")
        gm.setStyleSheet("QGroupBox{font-weight:bold;color:#cc0000;font-size:13px;}")
        vm2 = QVBoxLayout()
        self.lbl_marcador = QLabel()
        self.lbl_marcador.setFixedSize(270, 270)
        self.lbl_marcador.setStyleSheet("border:4px solid #cc0000; background:white;")
        self.lbl_marcador.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vm2.addWidget(self.lbl_marcador, alignment=Qt.AlignmentFlag.AlignCenter)
        self.lbl_cual = QLabel("Marcador ID 0  →  Portada")
        self.lbl_cual.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_cual.setStyleSheet("font-size:11px; color:#555;")
        vm2.addWidget(self.lbl_cual)
        gm.setLayout(vm2); v_m.addWidget(gm)

        # Botones para elegir qué marcador mostrar
        v_m.addWidget(QLabel("Elige qué marcador ver:"))
        grid_btns = QWidget(); g_lay = QGridLayout(grid_btns)
        info_ids = {0:"Portada",1:"Portada",2:"Animales",3:"Animales",
                    4:"Vehículos",5:"Vehículos",6:"Naturaleza",7:"Naturaleza"}
        for i in range(8):
            b = QPushButton(f"ID {i}\n{info_ids[i]}")
            b.setStyleSheet("padding:4px; font-size:11px;")
            b.clicked.connect(lambda _, x=i: self.mostrar_marcador(x))
            g_lay.addWidget(b, i//4, i%4)
        v_m.addWidget(grid_btns)
        v_m.addStretch()
        tabs.addTab(tab_m, " Marcadores")

        # ── Pestaña 2: Estadísticas ─────────────────────────────────
        tab_s = QWidget(); vs = QVBoxLayout(tab_s)
        self.lbl_stats = QLabel("Esperando...")
        self.lbl_stats.setStyleSheet("font-size:13px;")
        vs.addWidget(self.lbl_stats)
        vs.addStretch()
        tabs.addTab(tab_s, " Stats")

        # ── Pestaña 3: Ayuda ────────────────────────────────────────
        tab_a = QWidget(); va = QVBoxLayout(tab_a)
        ayuda = QTextEdit(); ayuda.setReadOnly(True)
        ayuda.setText(
            "PASO A PASO:\n\n"
            "1. Ve a la pestaña 'Marcadores' (la primera)\n\n"
            "2. Verás un cuadrado negro y blanco\n"
            "   en el panel de la derecha.\n"
            "   ESE cuadrado es el marcador ArUco.\n\n"
            "3. Apunta la cámara de tu PC hacia\n"
            "   ese cuadrado (acerca la cámara\n"
            "   a la pantalla si es necesario).\n\n"
            "4. Cuando lo detecte, verás texto\n"
            "   de colores flotando sobre él.\n\n"
            "5. Usa los botones ID 0 al ID 7 para\n"
            "   cambiar de marcador y ver distintos\n"
            "   contenidos del libro.\n\n"
            "CONSEJO: imprime alguno de los archivos\n"
            "marcador_0.png ... marcador_7.png para\n"
            "una demo más cómoda con tu profe."
        )
        va.addWidget(ayuda)
        tabs.addTab(tab_a, " Ayuda")

        lc.addWidget(tabs)

        btn_cap = QPushButton(" Capturar pantalla")
        btn_cap.clicked.connect(self.capturar)
        btn_cap.setStyleSheet("padding:8px; font-size:13px;")
        lc.addWidget(btn_cap)
        lc.addStretch()
        layout.addWidget(pc, 1)

    def mostrar_marcador(self, id_m):
        """Dibuja el marcador en el panel para que el usuario sepa qué mostrar a la cámara."""
        self.id_panel = id_m
        m = np.zeros((400,400), dtype=np.uint8)
        aruco.generateImageMarker(self.diccionario, id_m, 400, m, 1)
        qimg = QImage(m.data, 400, 400, 400, QImage.Format.Format_Grayscale8)
        pix  = QPixmap.fromImage(qimg).scaled(
            260, 260, Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation)
        self.lbl_marcador.setPixmap(pix)
        info_ids = {0:"Portada",1:"Portada",2:"Animales",3:"Animales",
                    4:"Vehículos",5:"Vehículos",6:"Naturaleza",7:"Naturaleza"}
        self.lbl_cual.setText(f"Marcador ID {id_m}  →  {info_ids.get(id_m,'')}")

    def actualizar_panel_marcador(self):
        self.mostrar_marcador(self.id_panel)

    def superponer(self, frame, overlay, esquina):
        h_o, w_o = overlay.shape[:2]
        src = np.float32([[0,0],[w_o,0],[w_o,h_o],[0,h_o]])
        dst = esquina.astype(np.float32)
        M, _ = cv2.findHomography(src, dst)
        if M is None: return frame
        warped = cv2.warpPerspective(overlay, M, (frame.shape[1], frame.shape[0]))
        if overlay.shape[2] == 4:
            alpha = warped[:,:,3:4]/255.0
            for c in range(3):
                frame[:,:,c] = (frame[:,:,c]*(1-alpha[:,:,0]) +
                                warped[:,:,c]*alpha[:,:,0]).astype(np.uint8)
        return frame

    def actualizar(self):
        ret, frame = self.cap.read()
        if not ret: return
        self.ultimo_frame = frame.copy()
        esq, ids, _ = self.detector.detectMarkers(frame)
        n = 0
        if ids is not None:
            aruco.drawDetectedMarkers(frame, esq, ids)
            n = len(ids)
            for i, mid in enumerate(ids.flatten()):
                self.marcadores_vistos.add(int(mid))
                if mid in self.contenidos:
                    self.superponer(frame, self.contenidos[mid], esq[i][0])
                cx = int(esq[i][0][:,0].mean())
                cy = int(esq[i][0][:,1].mean())
                cv2.putText(frame, f"ID:{mid}", (cx-20, cy+5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,0), 2)

        self.lbl_stats.setText(
            f"Detectados ahora: {n}\n"
            f"Distintos escaneados: {len(self.marcadores_vistos)}\n"
            f"IDs vistos: {sorted(self.marcadores_vistos)}")
        self.lbl_status.setText(
            f" Marcador detectado: {list(ids.flatten())}" if n > 0
            else " Apunta la cámara al cuadrado del panel derecho ↗")

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qt = QImage(rgb.data, w, h, ch*w, QImage.Format.Format_RGB888)
        pix = QPixmap.fromImage(qt).scaled(
            self.lbl_video.size(), Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation)
        self.lbl_video.setPixmap(pix)

    def capturar(self):
        if self.ultimo_frame is not None:
            ts = QDateTime.currentDateTime().toString("yyyyMMdd_hhmmss")
            nombre = f"libro_ar_{ts}.png"
            cv2.imwrite(nombre, self.ultimo_frame)
            QMessageBox.information(self,"Guardado", f"Capturado: {nombre}")

    def closeEvent(self, event): self.cap.release(); event.accept()


def main():
    app = QApplication(sys.argv); app.setStyle("Fusion")
    v = LibroAR(); v.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()