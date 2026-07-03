# ejercicio16_corregido_v2.py
# pip install opencv-contrib-python numpy PyQt6 mediapipe
#
# FIX v2: el error "Can't parse 'center'" ocurría porque MediaPipe devuelve
# coordenadas como numpy.float32, y cv2.circle necesita int de Python puro.
# También se usaban dimensiones fijas (1280x720) que no coincidían con la
# cámara real. Ahora se usan las dimensiones reales del frame.

import sys
import cv2
import numpy as np
import random
import time
import json
import os
import traceback
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QStackedWidget, QInputDialog, QMessageBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap

import mediapipe as mp
try:
    mp_hands_module = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils
except AttributeError:
    from mediapipe.python.solutions import hands as mp_hands_module
    from mediapipe.python.solutions import drawing_utils as mp_drawing

COLORES = {'bueno': (0, 200, 0), 'malo': (0, 0, 200), 'especial': (0, 200, 200)}


class MotorJuego:
    def __init__(self):
        self.hands = mp_hands_module.Hands(
            max_num_hands=1, min_detection_confidence=0.7)
        # FIX: usamos 640x480 como base; se ajusta al frame real al detectar
        self.ancho = 640
        self.alto = 480
        self.puntos = 0
        self.vidas = 3
        self.nivel = 1
        self.objetos = []
        self.velocidad_base = 5
        self.ultima_pos = None
        self.tiempo_inicio = time.time()

    def crear_objeto(self):
        tipo = random.choices(['bueno', 'malo', 'especial'], weights=[5, 3, 1])[0]
        self.objetos.append({
            'x': random.randint(50, self.ancho - 50),
            'y': 50,
            'tipo': tipo,
            'radio': 30 if tipo == 'especial' else 20,
            'puntos': 10 if tipo == 'bueno' else -10 if tipo == 'malo' else 50,
            'velocidad': self.velocidad_base * (2.0 if tipo == 'malo' else 1.0)
        })

    def actualizar(self):
        vivos = []
        for o in self.objetos:
            o['y'] += o['velocidad']
            if o['y'] < self.alto + 50:
                vivos.append(o)
            elif o['tipo'] == 'bueno':
                self.puntos = max(0, self.puntos - 2)
        self.objetos = vivos
        if len(self.objetos) < 8 + self.nivel * 2 and random.random() < 0.03:
            self.crear_objeto()
        nuevo_nivel = self.puntos // 100 + 1
        if nuevo_nivel > self.nivel:
            self.nivel = nuevo_nivel
            self.velocidad_base = 5 + (self.nivel - 1) * 1.5

    def detectar_mano(self, frame):
        # FIX: tomamos dimensiones REALES del frame en vez de valores fijos
        h_real, w_real = frame.shape[:2]
        self.ancho = w_real
        self.alto  = h_real

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = self.hands.process(rgb)
        pos = None

        if res.multi_hand_landmarks:
            lm = res.multi_hand_landmarks[0]
            # FIX: conversión explícita float → Python int puro
            px = int(float(lm.landmark[0].x) * w_real)
            py = int(float(lm.landmark[0].y) * h_real)
            # Clamp para que nunca se salga del frame
            px = max(0, min(px, w_real - 1))
            py = max(0, min(py, h_real - 1))
            pos = (px, py)
            self.ultima_pos = pos
            mp_drawing.draw_landmarks(frame, lm, mp_hands_module.HAND_CONNECTIONS)

        return frame, pos

    def verificar_colisiones(self, pos):
        if not pos:
            return
        mx, my = pos
        restantes = []
        for o in self.objetos:
            dist = np.sqrt((mx - o['x'])**2 + (my - o['y'])**2)
            if dist < o['radio'] + 35:
                self.puntos = max(0, self.puntos + o['puntos'])
                if o['tipo'] == 'malo':
                    self.vidas -= 1
            else:
                restantes.append(o)
        self.objetos = restantes

    def dibujar(self, frame):
        for o in self.objetos:
            # FIX: coords siempre como int puro
            cx, cy = int(o['x']), int(o['y'])
            cv2.circle(frame, (cx, cy), int(o['radio']), COLORES[o['tipo']], -1)
            cv2.circle(frame, (cx, cy), int(o['radio']), (255, 255, 255), 2)
            cv2.putText(frame, str(o['puntos']), (cx - 10, cy - 22),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)

        cv2.rectangle(frame, (0, 0), (260, 120), (0, 0, 0), -1)
        cv2.putText(frame, f"Pts:{self.puntos}",  (10, 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(frame, f"Vidas:{self.vidas}", (10, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (0, 255, 0) if self.vidas > 1 else (0, 0, 255), 2)
        cv2.putText(frame, f"Nivel:{self.nivel}", (10, 105),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
        return frame

    def cerrar(self):
        self.hands.close()


class ARCatcherApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎮 AR Catcher – Capítulo 16 (v2)")
        self.setGeometry(100, 100, 1300, 800)
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        self.motor = None
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.frame_juego)
        self._build_menu()
        self._build_juego()
        self._build_ranking()
        self.stack.setCurrentIndex(0)

    # ── Pantalla menú ────────────────────────────────────────────────
    def _build_menu(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)

        t = QLabel("🎮 AR CATCHER")
        t.setStyleSheet("font-size:48px; font-weight:bold; color:#4CAF50;")
        t.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(t)

        s = QLabel("Mueve tu mano para atrapar los círculos")
        s.setStyleSheet("font-size:18px; color:#888;")
        s.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(s)

        for txt, fn, color in [
            ("🎯 JUGAR",   self.iniciar_juego, "#4CAF50"),
            ("🏆 RANKING", lambda: self.stack.setCurrentIndex(2), "#2196F3"),
            ("❌ SALIR",   QApplication.quit, "#f44336")
        ]:
            b = QPushButton(txt)
            b.setStyleSheet(
                f"font-size:22px; padding:15px; background:{color}; color:white;"
                f" border-radius:10px; min-width:280px; margin:8px;")
            b.clicked.connect(fn)
            lay.addWidget(b)

        reglas = QLabel(
            "🟢 Verde  → +10 puntos\n"
            "🔴 Rojo   → −10 puntos y −1 vida\n"
            "🟡 Amarillo → +50 puntos\n"
            "Cada 100 puntos subes de nivel y los objetos van más rápido"
        )
        reglas.setStyleSheet("font-size:14px; color:#aaa; margin-top:20px;")
        reglas.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(reglas)
        self.stack.addWidget(w)

    # ── Pantalla juego ───────────────────────────────────────────────
    def _build_juego(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        self.lbl_video = QLabel()
        self.lbl_video.setMinimumSize(1000, 600)
        self.lbl_video.setStyleSheet("border:2px solid #333; background:#111;")
        self.lbl_video.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self.lbl_video)
        hl = QHBoxLayout()
        b1 = QPushButton("🏠 Menú");     b1.clicked.connect(self.volver_menu); hl.addWidget(b1)
        b2 = QPushButton("🔄 Reiniciar"); b2.clicked.connect(self.reiniciar);   hl.addWidget(b2)
        lay.addLayout(hl)
        self.stack.addWidget(w)

    # ── Pantalla ranking ─────────────────────────────────────────────
    def _build_ranking(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        t = QLabel("🏆 RANKING")
        t.setStyleSheet("font-size:32px; font-weight:bold; color:#FFD700;")
        t.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(t)
        self.tabla_rank = QTableWidget()
        self.tabla_rank.setColumnCount(4)
        self.tabla_rank.setHorizontalHeaderLabels(["Pos", "Nombre", "Puntos", "Nivel"])
        self.tabla_rank.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        lay.addWidget(self.tabla_rank)
        b = QPushButton("◀ Volver al menú")
        b.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        lay.addWidget(b)
        self.stack.addWidget(w)

    # ── Lógica ──────────────────────────────────────────────────────
    def iniciar_juego(self):
        try:
            self.motor = MotorJuego()
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                raise RuntimeError(
                    "No se pudo abrir la cámara.\n"
                    "Cierra otras apps que usen la cámara (Teams, Zoom, etc).")
            self.stack.setCurrentIndex(1)
            self.timer.start(30)
        except Exception as e:
            QMessageBox.critical(self, "Error al iniciar",
                f"{e}\n\n{traceback.format_exc()[-400:]}")
            self.volver_menu()

    def volver_menu(self):
        self.timer.stop()
        if self.cap:
            self.cap.release(); self.cap = None
        if self.motor:
            self.motor.cerrar(); self.motor = None
        self.stack.setCurrentIndex(0)

    def reiniciar(self):
        if self.motor:
            self.motor.cerrar()
        self.motor = MotorJuego()

    def frame_juego(self):
        if not self.motor or not self.cap:
            return
        try:
            ret, frame = self.cap.read()
            if not ret:
                return
            frame, pos = self.motor.detectar_mano(frame)
            self.motor.actualizar()
            self.motor.verificar_colisiones(pos)
            frame = self.motor.dibujar(frame)

            if pos:
                # FIX: pos ya viene como (int, int) puro desde detectar_mano
                cv2.circle(frame, pos, 35, (255, 255, 255), 3)

            if self.motor.vidas <= 0:
                self.timer.stop()
                self.game_over()
                return

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            qt_img = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
            pix = QPixmap.fromImage(qt_img).scaled(
                self.lbl_video.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation)
            self.lbl_video.setPixmap(pix)

        except Exception as e:
            self.timer.stop()
            QMessageBox.critical(self, "Error durante el juego", str(e))
            self.volver_menu()

    def game_over(self):
        puntos = self.motor.puntos
        nivel  = self.motor.nivel
        nombre, ok = QInputDialog.getText(
            self, "💀 Game Over!",
            f"Puntuación: {puntos}  |  Nivel: {nivel}\n\nEscribe tu nombre:")
        ranking = []
        if os.path.exists('ranking.json'):
            with open('ranking.json', 'r') as f:
                ranking = json.load(f)
        if ok and nombre:
            ranking.append({"nombre": nombre, "puntos": puntos, "nivel": nivel})
            ranking.sort(key=lambda x: x['puntos'], reverse=True)
            ranking = ranking[:10]
            with open('ranking.json', 'w') as f:
                json.dump(ranking, f, indent=2)
        self._actualizar_ranking(ranking)
        self.volver_menu()

    def _actualizar_ranking(self, ranking):
        if not ranking and os.path.exists('ranking.json'):
            with open('ranking.json', 'r') as f:
                ranking = json.load(f)
        self.tabla_rank.setRowCount(len(ranking))
        for i, e in enumerate(ranking):
            for j, v in enumerate([str(i+1), e['nombre'],
                                    str(e['puntos']), str(e['nivel'])]):
                self.tabla_rank.setItem(i, j, QTableWidgetItem(v))

    def closeEvent(self, event):
        self.timer.stop()
        if self.cap:
            self.cap.release()
        if self.motor:
            self.motor.cerrar()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    v = ARCatcherApp()
    v.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
