# pip install opencv-contrib-python numpy PyQt6
#
# NUEVO: el marcador ArUco se muestra DENTRO de la app.
# Solo tienes que apuntar la cámara a la imagen del marcador que aparece
# en el panel derecho de esta misma ventana.

import sys
import os
import cv2
import cv2.aruco as aruco
import numpy as np
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton, QGroupBox,
                             QLineEdit, QMessageBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap


class TarjetaAR(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📇 Tarjeta de Presentación AR – Capítulo 9")
        self.setGeometry(100, 100, 1400, 820)

        self.diccionario = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)
        self.detector    = aruco.ArucoDetector(self.diccionario, aruco.DetectorParameters())

        # Datos de las tarjetas
        self.info_tarjetas = {
            0: {"nombre": "Ana García",   "cargo": "Ingeniera AR",
                "empresa": "TechVision",  "email": "ana@techvision.com",
                "telefono": "+52 123 456 789", "color": (255, 100, 0)},
            1: {"nombre": "Carlos López", "cargo": "Desarrollador Senior",
                "empresa": "AR Solutions","email": "carlos@arsolutions.com",
                "telefono": "+52 987 654 321", "color": (0, 200, 100)},
        }

        # Generar marcadores en disco (para imprimir si quieres)
        carpeta = os.path.dirname(os.path.abspath(__file__))
        for i in range(2):
            m = np.zeros((400, 400), dtype=np.uint8)
            aruco.generateImageMarker(self.diccionario, i, 400, m, 1)
            ruta = os.path.join(carpeta, f"marcador_{i}.png")
            cv2.imwrite(ruta, m)
        print(f"✅ Marcadores guardados en: {carpeta}")

        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar)
        self.timer.start(30)

        self.id_actual = 0        # marcador que se muestra en el panel
        self.setup_ui()
        self.actualizar_panel_marcador()

    # ── Construcción de UI ───────────────────────────────────────────
    def setup_ui(self):
        central = QWidget(); self.setCentralWidget(central)
        layout  = QHBoxLayout(central)

        # Panel izquierdo: video
        self.lbl_video = QLabel()
        self.lbl_video.setMinimumSize(780, 600)
        self.lbl_video.setStyleSheet("background:#111; border:2px solid #555;")
        self.lbl_video.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_video, 3)

        # Panel derecho
        pe = QWidget(); pe.setMaximumWidth(420)
        lc = QVBoxLayout(pe)

        # ── Instrucción principal ───────────────────────────────────
        g0 = QGroupBox("📌 QUÉ TIENES QUE HACER")
        v0 = QVBoxLayout()
        instruccion = QLabel(
            "👇 APUNTA LA CÁMARA HACIA\n"
            "    ESTE CUADRADO DE ABAJO\n\n"
            "El cuadrado blanco/negro de abajo\n"
            "ES el marcador ArUco.\n"
            "Acerca la cámara a él y verás\n"
            "la tarjeta flotando encima."
        )
        instruccion.setStyleSheet(
            "font-size:14px; font-weight:bold; color:#cc6600;"
            "background:#fff3e0; padding:8px; border-radius:4px;")
        v0.addWidget(instruccion)
        g0.setLayout(v0); lc.addWidget(g0)

        # ── Selector de marcador ────────────────────────────────────
        g1 = QGroupBox("🎯 Elige qué marcador mostrar")
        v1 = QVBoxLayout()
        self.lbl_id = QLabel("Marcador ID: 0  →  'Ana García'")
        self.lbl_id.setStyleSheet("font-weight:bold;")
        hl = QHBoxLayout()
        btn_m = QPushButton("◀ Anterior"); btn_m.clicked.connect(lambda: self.cambiar_id(-1))
        btn_p = QPushButton("Siguiente ▶"); btn_p.clicked.connect(lambda: self.cambiar_id(1))
        hl.addWidget(btn_m); hl.addWidget(btn_p)
        v1.addWidget(self.lbl_id)
        v1.addLayout(hl)
        g1.setLayout(v1); lc.addWidget(g1)

        # ── IMAGEN DEL MARCADOR (lo más importante) ─────────────────
        g_marker = QGroupBox("👇 MUESTRA ESTO A LA CÁMARA")
        g_marker.setStyleSheet("QGroupBox{font-weight:bold; color:#cc0000; font-size:14px;}")
        v_m = QVBoxLayout()
        self.lbl_marcador = QLabel()
        self.lbl_marcador.setFixedSize(300, 300)
        self.lbl_marcador.setStyleSheet("border:4px solid #cc0000; background:white;")
        self.lbl_marcador.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v_m.addWidget(self.lbl_marcador, alignment=Qt.AlignmentFlag.AlignCenter)
        g_marker.setLayout(v_m); lc.addWidget(g_marker)

        # ── Estado ──────────────────────────────────────────────────
        self.lbl_status = QLabel("⏳ Apunta la cámara al cuadrado de arriba")
        self.lbl_status.setStyleSheet("color:#555; padding:4px; font-size:12px;")
        lc.addWidget(self.lbl_status)

        # ── Editar tarjeta ──────────────────────────────────────────
        g2 = QGroupBox("✏️ Editar datos de la tarjeta")
        v2 = QVBoxLayout()
        self.inputs = {}
        for campo in ["nombre", "cargo", "empresa", "email", "telefono"]:
            v2.addWidget(QLabel(campo.capitalize() + ":"))
            inp = QLineEdit(); inp.textChanged.connect(self.guardar_cambios)
            v2.addWidget(inp); self.inputs[campo] = inp
        g2.setLayout(v2); lc.addWidget(g2)
        lc.addStretch()
        layout.addWidget(pe, 1)
        self.cargar_info_actual()

    def actualizar_panel_marcador(self):
        """Muestra el marcador ArUco como imagen dentro del panel."""
        m = np.zeros((400, 400), dtype=np.uint8)
        aruco.generateImageMarker(self.diccionario, self.id_actual, 400, m, 1)
        # Convertir a QPixmap
        qimg = QImage(m.data, 400, 400, 400, QImage.Format.Format_Grayscale8)
        pix  = QPixmap.fromImage(qimg).scaled(
            290, 290, Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation)
        self.lbl_marcador.setPixmap(pix)
        nombre = self.info_tarjetas.get(self.id_actual, {}).get("nombre", f"ID {self.id_actual}")
        self.lbl_id.setText(f"Marcador ID: {self.id_actual}  →  '{nombre}'")

    def cambiar_id(self, delta):
        nuevo = self.id_actual + delta
        if 0 <= nuevo <= 9:
            self.id_actual = nuevo
            self.actualizar_panel_marcador()
            self.cargar_info_actual()

    def cargar_info_actual(self):
        info = self.info_tarjetas.get(self.id_actual, {})
        for campo, inp in self.inputs.items():
            inp.blockSignals(True)
            inp.setText(info.get(campo, ""))
            inp.blockSignals(False)

    def guardar_cambios(self):
        if self.id_actual not in self.info_tarjetas:
            self.info_tarjetas[self.id_actual] = {"color": (0, 200, 100)}
        for campo, inp in self.inputs.items():
            self.info_tarjetas[self.id_actual][campo] = inp.text()

    # ── Dibujar tarjeta sobre el marcador ───────────────────────────
    def dibujar_tarjeta(self, frame, info, esquinas):
        pts = esquinas[0].astype(int)
        x1, y1 = pts[:, 0].min(), pts[:, 1].min()
        x2, y2 = pts[:, 0].max(), pts[:, 1].max()
        pad = max((x2 - x1) // 2, 30)
        bx1 = max(0, x1 - pad);   bx2 = min(frame.shape[1], x2 + pad)
        by1 = max(0, y1 - pad);   by2 = min(frame.shape[0], y2 + pad * 2)
        overlay = frame.copy()
        color   = info.get("color", (0, 200, 100))
        cv2.rectangle(overlay, (bx1, by1), (bx2, by2), color, -1)
        cv2.addWeighted(overlay, 0.35, frame, 0.65, 0, frame)
        cv2.rectangle(frame, (bx1, by1), (bx2, by2), color, 3)
        campos = [("nombre","📇"),("cargo","👔"),("empresa","🏢"),
                  ("email","📧"),("telefono","📞")]
        for i, (campo, icono) in enumerate(campos):
            txt = f"{icono} {info.get(campo,'')}"
            cv2.putText(frame, txt, (bx1 + 10, by1 + 30 + i * 28),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)

    # ── Loop de cámara ───────────────────────────────────────────────
    def actualizar(self):
        ret, frame = self.cap.read()
        if not ret: return
        esq, ids, _ = self.detector.detectMarkers(frame)
        if ids is not None:
            aruco.drawDetectedMarkers(frame, esq, ids)
            for i, mid in enumerate(ids.flatten()):
                if mid in self.info_tarjetas:
                    self.dibujar_tarjeta(frame, self.info_tarjetas[mid], esq[i])
            self.lbl_status.setText(f"✅ Marcador detectado: ID {list(ids.flatten())}")
        else:
            self.lbl_status.setText("⏳ Apunta la cámara al cuadrado del panel derecho")
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qt = QImage(rgb.data, w, h, ch*w, QImage.Format.Format_RGB888)
        pix = QPixmap.fromImage(qt).scaled(
            self.lbl_video.size(), Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation)
        self.lbl_video.setPixmap(pix)

    def closeEvent(self, event):
        self.cap.release(); event.accept()


def main():
    app = QApplication(sys.argv)
    v = TarjetaAR(); v.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()