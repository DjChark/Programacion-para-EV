# ejercicio18_corregido.py
# pip install pyinstaller opencv-contrib-python numpy PyQt6 mediapipe

import sys
import os
import platform
import subprocess
import shutil
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton, QGroupBox,
                             QComboBox, QTextEdit, QFileDialog, QMessageBox,
                             QRadioButton, QButtonGroup, QProgressBar)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont


class EmpaquetadorThread(QThread):
    """Hilo separado para que la interfaz no se congele mientras empaqueta."""
    log = pyqtSignal(str)
    terminado = pyqtSignal(bool, str)

    def __init__(self, script, nombre, modo):
        super().__init__()
        self.script = script; self.nombre = nombre; self.modo = modo

    def run(self):
        try:
            self.log.emit(f" Iniciando empaquetado de '{self.nombre}'...")
            self.log.emit(f"   Script: {self.script}")
            self.log.emit(f"   Modo: {self.modo}\n")

            args = [
                sys.executable, "-m", "PyInstaller",
                self.script,
                f"--name={self.nombre}",
                "--noconfirm",
                "--clean",
                "--windowed",
                f"--{'onefile' if self.modo == 'onefile' else 'onedir'}",
                "--hidden-import=cv2",
                "--hidden-import=numpy",
                "--hidden-import=PyQt6",
            ]

            # Añadir hidden imports de mediapipe si el script lo usa
            with open(self.script, 'r', encoding='utf-8', errors='ignore') as f:
                contenido = f.read()
            if 'mediapipe' in contenido:
                args += ["--hidden-import=mediapipe",
                         "--hidden-import=mediapipe.python.solutions",
                         "--hidden-import=google.protobuf"]
                self.log.emit(" MediaPipe detectado – añadiendo hidden imports...\n")

            self.log.emit("⚙️ Ejecutando PyInstaller...\n")
            proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    text=True, encoding='utf-8', errors='replace')
            for linea in proc.stdout:
                self.log.emit(linea.rstrip())
            proc.wait()

            if proc.returncode == 0:
                ruta = os.path.join("dist", self.nombre)
                self.terminado.emit(True, ruta)
            else:
                self.terminado.emit(False, "PyInstaller terminó con errores (ver log arriba)")
        except Exception as e:
            self.terminado.emit(False, str(e))


class EmpaquetadorAR(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(" Empaquetador Profesional AR – Capítulo 18")
        self.setGeometry(100, 100, 900, 750)
        self.hilo = None
        self.setup_ui()

    def setup_ui(self):
        central = QWidget(); self.setCentralWidget(central)
        layout = QVBoxLayout(central); layout.setSpacing(12)

        titulo = QLabel("📦 EMPAQUETADOR DE APPS AR")
        titulo.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("color:#4CAF50; padding:12px;")
        layout.addWidget(titulo)

        layout.addWidget(QLabel(
            "Este ejercicio convierte cualquiera de tus scripts Python en un\n"
            "archivo .exe (Windows) que se puede ejecutar sin tener Python instalado.",
            alignment=Qt.AlignmentFlag.AlignCenter
        ))

        # ── Selección de script ──────────────────────────────────────
        g1 = QGroupBox("1️  Selecciona el script a empaquetar")
        v1 = QVBoxLayout()
        self.combo_scripts = QComboBox()

        # Detectar ejercicios disponibles en la carpeta actual
        scripts_disponibles = []
        for f in sorted(os.listdir(".")):
            if f.endswith(".py") and "ejercicio" in f.lower() and "18" not in f:
                scripts_disponibles.append(f)

        if scripts_disponibles:
            self.combo_scripts.addItems(scripts_disponibles)
        else:
            self.combo_scripts.addItem("(no se encontraron ejercicios en esta carpeta)")

        v1.addWidget(self.combo_scripts)
        btn_sel = QPushButton(" Seleccionar otro archivo .py...")
        btn_sel.clicked.connect(self.seleccionar_archivo); v1.addWidget(btn_sel)
        g1.setLayout(v1); layout.addWidget(g1)

        # ── Modo de empaquetado ──────────────────────────────────────
        g2 = QGroupBox("2️  Modo de empaquetado")
        v2 = QVBoxLayout()
        self.radio_onefile = QRadioButton(
            "Un solo archivo .exe — más fácil de compartir, "
            "tarda más en arrancar la primera vez")
        self.radio_onedir = QRadioButton(
            "Carpeta con ejecutable — arranca más rápido, "
            "pero tienes que compartir toda la carpeta")
        self.radio_onefile.setChecked(True)
        grupo = QButtonGroup(self); grupo.addButton(self.radio_onefile); grupo.addButton(self.radio_onedir)
        v2.addWidget(self.radio_onefile); v2.addWidget(self.radio_onedir)
        g2.setLayout(v2); layout.addWidget(g2)

        # ── Botón empaquetar ─────────────────────────────────────────
        self.btn_empaquetar = QPushButton(" EMPAQUETAR AHORA")
        self.btn_empaquetar.setStyleSheet(
            "font-size:16px; padding:14px; background:#4CAF50; color:white; border-radius:8px;")
        self.btn_empaquetar.clicked.connect(self.empaquetar)
        layout.addWidget(self.btn_empaquetar)

        # Barra de progreso (indeterminada mientras trabaja)
        self.progress = QProgressBar(); self.progress.setRange(0, 0)  # indeterminada
        self.progress.setVisible(False); layout.addWidget(self.progress)

        # ── Log de salida ────────────────────────────────────────────
        g3 = QGroupBox(" Progreso del empaquetado")
        v3 = QVBoxLayout()
        self.log_text = QTextEdit(); self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 9))
        self.log_text.setMinimumHeight(220)
        self.log_text.setPlaceholderText("El log del empaquetado aparecerá aquí...")
        v3.addWidget(self.log_text)
        g3.setLayout(v3); layout.addWidget(g3)

        self.lbl_resultado = QLabel("")
        self.lbl_resultado.setStyleSheet("font-size:13px; padding:6px;")
        layout.addWidget(self.lbl_resultado)

    def seleccionar_archivo(self):
        f, _ = QFileDialog.getOpenFileName(self, "Seleccionar script", "", "Python (*.py)")
        if f:
            self.combo_scripts.insertItem(0, f)
            self.combo_scripts.setCurrentIndex(0)

    def empaquetar(self):
        script = self.combo_scripts.currentText()
        if not os.path.exists(script):
            QMessageBox.warning(self, "Archivo no encontrado",
                f"No se encontró: {script}\nAsegúrate de que esté en la misma carpeta.")
            return

        if self.hilo and self.hilo.isRunning():
            QMessageBox.information(self, "En proceso", "Ya hay un empaquetado en curso.")
            return

        nombre = os.path.splitext(os.path.basename(script))[0]
        modo = "onefile" if self.radio_onefile.isChecked() else "onedir"

        self.log_text.clear()
        self.btn_empaquetar.setEnabled(False)
        self.btn_empaquetar.setText("⏳ Empaquetando... (puede tardar 2-5 minutos)")
        self.progress.setVisible(True)
        self.lbl_resultado.setText("")

        self.hilo = EmpaquetadorThread(script, nombre, modo)
        self.hilo.log.connect(self.agregar_log)
        self.hilo.terminado.connect(self.on_terminado)
        self.hilo.start()

    def agregar_log(self, linea):
        self.log_text.append(linea)
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum())

    def on_terminado(self, exito, ruta):
        self.progress.setVisible(False)
        self.btn_empaquetar.setEnabled(True)
        self.btn_empaquetar.setText(" EMPAQUETAR AHORA")

        if exito:
            self.lbl_resultado.setText(f"¡Empaquetado exitoso! Ejecutable en: dist/{ruta}")
            self.lbl_resultado.setStyleSheet("color:green; font-size:13px; padding:6px;")
            resp = QMessageBox.question(self, "Listo",
                f"El ejecutable fue creado en:\n{ruta}\n\n"
                "¿Abrir la carpeta dist/ en el Explorador de Windows?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if resp == QMessageBox.StandardButton.Yes:
                import subprocess
                subprocess.Popen(["explorer", "dist"])
        else:
            self.lbl_resultado.setText(f" Error: {ruta}")
            self.lbl_resultado.setStyleSheet("color:red; font-size:13px; padding:6px;")
            QMessageBox.critical(self, "Error",
                f"El empaquetado falló:\n{ruta}\n\nRevisa el log para más detalles.\n\n"
                "Tip: si el error menciona 'mediapipe', instala:\n"
                "py -3.11 -m pip install mediapipe==0.9.3.3")


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    v = EmpaquetadorAR()
    v.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
