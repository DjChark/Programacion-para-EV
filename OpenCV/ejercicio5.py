# ejercicio5.py
# pip install opencv-contrib-python numpy PyQt6

import sys
import cv2
import numpy as np
import json
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton, QListWidget, 
                             QGroupBox, QMessageBox, QInputDialog)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap

class DetectorAsistencia(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("👁️ Detector de Asistencia con Haar Cascade – Capítulo 5")
        self.setGeometry(100, 100, 1200, 750)
        
        # Clasificador de OpenCV
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Archivo JSON vacío por defecto
        self.ruta_json = "personas.json"
        self.db_personas = self.cargar_json()
        
        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar)
        self.timer.start(30)
        
        # Variables de control seguras
        self.ultimo_rostro_visto = None 
        self.asistencia_del_dia = set()
        
        self.setup_ui()

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        
        # Video
        self.lbl_video = QLabel()
        self.lbl_video.setMinimumSize(800, 600)
        self.lbl_video.setStyleSheet("background:#1a1a1a; border:2px solid #333;")
        self.lbl_video.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_video, 3)
        
        # Panel de Controles
        panel = QWidget()
        panel.setFixedWidth(340)
        v_panel = QVBoxLayout(panel)
        
        # Alerta visual > 2 personas
        self.lbl_alerta = QLabel("Estado: Inicializando")
        self.lbl_alerta.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_alerta.setStyleSheet("background: #4CAF50; color: white; font-weight: bold; padding: 10px; border-radius: 5px; font-size: 14px;")
        v_panel.addWidget(self.lbl_alerta)
        
        # Lista en UI
        g1 = QGroupBox("📋 Registro de Asistencia en Vivo")
        v1 = QVBoxLayout()
        self.lista_asistencia_ui = QListWidget()
        v1.addWidget(self.lista_asistencia_ui)
        g1.setLayout(v1)
        v_panel.addWidget(g1)
        
        # Botones
        g_controles = QGroupBox("🕹️ Controles de Base de Datos")
        v_c = QVBoxLayout()
        
        btn_reg = QPushButton("➕ Registrar Persona")
        btn_reg.clicked.connect(self.registrar_persona)
        btn_reg.setStyleSheet("padding: 10px; background: #2196F3; color: white; font-weight: bold; font-size: 13px;")
        v_c.addWidget(btn_reg)
        
        btn_elim = QPushButton("🗑️ Eliminar de BD")
        btn_elim.clicked.connect(self.eliminar_persona)
        btn_elim.setStyleSheet("padding: 10px; background: #e53935; color: white; font-size: 13px;")
        v_c.addWidget(btn_elim)
        
        btn_save = QPushButton("💾 Guardar JSON")
        btn_save.clicked.connect(self.guardar_json)
        btn_save.setStyleSheet("padding: 10px; background: #4CAF50; color: white; font-weight: bold; font-size: 13px;")
        v_c.addWidget(btn_save)
        
        g_controles.setLayout(v_c)
        v_panel.addWidget(g_controles)
        
        layout.addWidget(panel, 1)

    def cargar_json(self):
        # Inicia completamente vacío como lo pediste
        if os.path.exists(self.ruta_json):
            try:
                with open(self.ruta_json, 'r') as f:
                    data = json.load(f)
                    return data if isinstance(data, dict) else {}
            except:
                return {}
        return {}

    def guardar_json(self):
        with open(self.ruta_json, 'w') as f:
            json.dump(self.db_personas, f, indent=4)
        QMessageBox.information(self, "Guardado", "¡Base de datos personas.json guardada!")

    def registrar_persona(self):
        # PASO CRÍTICO: Detener el timer para que la cámara no tumbe la ventana emergente
        self.timer.stop()
        
        if self.ultimo_rostro_visto is None:
            QMessageBox.warning(self, "Error", "No se detecta ningún rostro en la cámara.")
            self.timer.start(30) # Reactivar
            return
        
        nombre, ok = QInputDialog.getText(self, "Nuevo Registro", "Ingresa el nombre de la persona:")
        if ok and nombre.strip():
            nombre_limpio = nombre.strip()
            # Guardamos las dimensiones exactas (w, h) exigidas por la ficha
            self.db_personas[nombre_limpio] = {
                "w": int(self.ultimo_rostro_visto[0]),
                "h": int(self.ultimo_rostro_visto[1])
            }
            # Guardado inmediato para evitar pérdidas
            with open(self.ruta_json, 'w') as f:
                json.dump(self.db_personas, f, indent=4)
                
            QMessageBox.information(self, "Éxito", f"Registrado correctamente: {nombre_limpio}")
        
        # Reactivar el procesamiento de la cámara de forma segura
        self.timer.start(30)

    def eliminar_persona(self):
        self.timer.stop()
        if not self.db_personas:
            QMessageBox.information(self, "Base de Datos", "No hay nadie registrado actualmente.")
            self.timer.start(30)
            return
        
        nombres = list(self.db_personas.keys())
        nombre, ok = QInputDialog.getItem(self, "Eliminar", "Selecciona a quién deseas eliminar:", nombres, 0, False)
        if ok and nombre in self.db_personas:
            del self.db_personas[nombre]
            if nombre in self.asistencia_del_dia:
                self.asistencia_del_dia.remove(nombre)
                self.lista_asistencia_ui.clear()
                self.lista_asistencia_ui.addItems(list(self.asistencia_del_dia))
            
            with open(self.ruta_json, 'w') as f:
                json.dump(self.db_personas, f, indent=4)
                
            QMessageBox.information(self, "Eliminado", f"Se eliminó a {nombre} del sistema.")
            
        self.timer.start(30)

    def actualizar(self):
        ret, frame = self.cap.read()
        if not ret: return
        frame = cv2.flip(frame, 1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rostros = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        num_personas = len(rostros)
        
        # Alerta condicional si detecta más de 2 personas en pantalla
        if num_personas > 2:
            self.lbl_alerta.setText(f"⚠️ ¡ALERTA! {num_personas} PERSONAS EN DETECCIÓN")
            self.lbl_alerta.setStyleSheet("background: #d32f2f; color: white; font-weight: bold; padding: 10px; border-radius: 5px; font-size: 14px;")
        else:
            self.lbl_alerta.setText("Estado: Normal")
            self.lbl_alerta.setStyleSheet("background: #388E3C; color: white; font-weight: bold; padding: 10px; border-radius: 5px; font-size: 14px;")

        self.ultimo_rostro_visto = None 
        lista_registrados = list(self.db_personas.keys())
        
        for idx, (x, y, w, h) in enumerate(rostros):
            # Guardamos las dimensiones del rostro actual en el ciclo
            self.ultimo_rostro_visto = (w, h)
            
            # Si el índice actual tiene un nombre registrado en el JSON lo asocia, si no es Desconocido
            if idx < len(lista_registrados):
                nombre_identificado = lista_registrados[idx]
                color_cuadro = (0, 255, 0) # Verde
            else:
                nombre_identificado = "Desconocido"
                color_cuadro = (0, 0, 255) # Rojo
                
            cv2.rectangle(frame, (x, y), (x + w, y + h), color_cuadro, 2)
            cv2.putText(frame, nombre_identificado, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color_cuadro, 2)
            
            # Tomar asistencia automática en el widget si es reconocido
            if nombre_identificado != "Desconocido" and nombre_identificado not in self.asistencia_del_dia:
                self.asistencia_del_dia.add(nombre_identificado)
                self.lista_asistencia_ui.addItem(nombre_identificado)
                
        # Mostrar video en PyQt6
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB); h_f, w_f, ch = rgb.shape
        qt_img = QImage(rgb.data, w_f, h_f, ch * w_f, QImage.Format.Format_RGB888)
        pix = QPixmap.fromImage(qt_img).scaled(self.lbl_video.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.lbl_video.setPixmap(pix)

    def closeEvent(self, event):
        self.cap.release()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    v = DetectorAsistencia()
    v.show()
    sys.exit(app.exec())