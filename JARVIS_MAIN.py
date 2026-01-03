import sys
import time
import os
import threading
import speech_recognition as sr
import pyttsx3
import pywhatkit
import webbrowser
from PyQt5.QtWidgets import (
    QWidget, QApplication, QLabel, QPushButton,
    QTextEdit, QFrame
)
from PyQt5.QtGui import (
    QPainter, QColor, QPen, QBrush, QFont,
    QRadialGradient, QLinearGradient, QConicalGradient
)
from PyQt5.QtCore import Qt, QTimer, QPoint, pyqtSignal, QObject, QRect

# ---------------- VOICE ----------------
def speak(text):
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 160)
        engine.say(text)
        engine.runAndWait()
    except:
        pass


# ---------------- APP OPENER ----------------
def open_app_logic(app_name):
    app_name = app_name.lower()
    paths = [
        os.path.join(os.environ["ProgramData"], "Microsoft", "Windows", "Start Menu", "Programs"),
        os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs")
    ]

    for path in paths:
        for root, _, files in os.walk(path):
            for file in files:
                if file.lower().endswith(".lnk") and app_name in file.lower():
                    try:
                        os.startfile(os.path.join(root, file))
                        return True
                    except: pass
    return False


# ---------------- BRAIN (Renamed from Worker) ----------------
class Brain(QObject):
    update_log = pyqtSignal(str, str)
    update_status = pyqtSignal(str)

    def run(self):
        time.sleep(1)
        self.update_log.emit("JARVIS", "Systems Online.")
        speak("System online.")

        while True:
            self.update_status.emit("LISTENING...")
            query = self.take_command()
            if query == "none":
                continue
            self.execute_query(query)

    def take_command(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            r.pause_threshold = 1.2
            r.energy_threshold = 300
            r.adjust_for_ambient_noise(source, duration=0.5)

            try:
                audio = r.listen(source, timeout=8)
                self.update_status.emit("PROCESSING...")
                query = r.recognize_google(audio, language='en-in')
                self.update_log.emit("USER", query)
                return query.lower()
            except:
                return "none"

    def execute_query(self, query):
        if "open" in query:
            app = query.replace("open", "").strip()
            self.update_log.emit("JARVIS", f"Opening {app}")
            speak(f"Opening {app}")
            if not open_app_logic(app):
                self.update_log.emit("ERROR", "App not found")
                speak("I didn't find that app")

        elif "play" in query:
            song = query.replace("play", "").strip()
            self.update_log.emit("JARVIS", f"Playing {song}")
            speak(f"Playing {song}")
            pywhatkit.playonyt(song)

        elif "search" in query:
            topic = query.replace("search", "").strip()
            self.update_log.emit("JARVIS", f"Searching {topic}")
            speak(f"Searching {topic}")
            webbrowser.open(f"https://www.google.com/search?q={topic}")

        elif "exit" in query or "stop" in query:
            speak("Goodbye.")
            os._exit(0)


# ---------------- HUD ----------------
class HUD(QWidget):  
    def __init__(self):
        super().__init__()
        self.resize(950, 550)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.angle = 0
        self.pulse = 0
        self.growing = True
        self.is_maximized = False

        self.initUI()

        # Threading Start
        self.thread = threading.Thread(target=self.start_brain, daemon=True)
        self.thread.start()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(30)

    def start_brain(self):
        self.brain = Brain() 
        self.brain.update_log.connect(self.add_log)
        self.brain.update_status.connect(self.update_status_text)
        self.brain.run()

    def initUI(self):
        # ---- BUTTONS ----
        self.btn_close = QPushButton("✖", self)
        self.btn_max = QPushButton("□", self)
        self.btn_min = QPushButton("➖", self)

        for btn in (self.btn_close, self.btn_max, self.btn_min):
            btn.setFixedSize(30, 30)
            btn.setStyleSheet(
                "color:white;border:2px solid cyan;border-radius:10px;background:rgba(0,0,0,100)"
            )

        self.btn_close.clicked.connect(self.close)
        self.btn_max.clicked.connect(self.toggle_fullscreen)
        self.btn_min.clicked.connect(self.showMinimized)

        # ---- TERMINAL ----
        self.terminal_frame = QFrame(self)
        self.terminal_frame.setStyleSheet("""
            background-color: rgba(15, 5, 20, 220);
            border-left: 3px solid #00ffff;
            border-radius: 5px;
        """)

        self.log_box = QTextEdit(self.terminal_frame)
        self.log_box.setReadOnly(True)
        self.log_box.setStyleSheet(
            "border:none;background:transparent;color:#e0b0ff;font-family:Consolas;font-size:11px;"
        )

        self.status_lbl = QLabel("SYSTEM READY", self)
        self.status_lbl.setStyleSheet(
            "color:#be00ff;font-size:13px;font-weight:bold;letter-spacing:2px;"
        )

        self.update_positions()

    def toggle_fullscreen(self):
        if self.is_maximized:
            self.showNormal()
        else:
            self.showMaximized()
        self.is_maximized = not self.is_maximized
        QTimer.singleShot(100, self.update_positions)

    def update_positions(self):
        w, h = self.width(), self.height()

        self.btn_close.move(w - 40, 10)
        self.btn_max.move(w - 80, 10)
        self.btn_min.move(w - 120, 10)

        # Terminal Positions
        self.terminal_frame.setGeometry(20, h - 220, 330, 200)
        self.log_box.setGeometry(10, 10, 310, 180)
        self.status_lbl.move(25, h - 250)

    def resizeEvent(self, event):
        self.update_positions()
        super().resizeEvent(event)

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def add_log(self, speaker, text):
        color = "#be00ff" if speaker == "JARVIS" else "#ffffff"
        self.log_box.append(
            f"<span style='color:{color}; font-weight:bold'>{speaker}:</span> {text}"
        )

    def update_status_text(self, text):
        self.status_lbl.setText(text)

    def animate(self):
        self.angle = (self.angle + 2) % 360
        self.pulse += 0.01 if self.growing else -0.01
        if self.pulse >= 1 or self.pulse <= 0:
            self.growing = not self.growing
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 1. Background
        bg = QLinearGradient(0, 0, self.width(), self.height())
        bg.setColorAt(0, QColor(25, 5, 35))
        bg.setColorAt(1, QColor(5, 0, 10))
        painter.setBrush(bg)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 15, 15)

        # 2. Circles
        center = QPoint(self.width() // 2, self.height() // 2)
        radius = 110

        pen = QPen(QColor(0, 255, 255), 2)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(center, radius + 25, radius + 25)

        conical = QConicalGradient(center, self.angle)
        conical.setColorAt(0, QColor(190, 0, 255))
        conical.setColorAt(0.3, Qt.transparent)
        painter.setPen(QPen(QBrush(conical), 5))
        painter.drawEllipse(center, radius, radius)

        inner = radius - 50 + (self.pulse * 30)
        glow = QRadialGradient(center, inner)
        glow.setColorAt(0, QColor(0, 255, 255))
        glow.setColorAt(1, Qt.transparent)
        painter.setBrush(glow)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(center, inner, inner)
        
        # 3. ROBOTIC & GRADIENT TEXT DRAWING
        
        # Position Setup
        text_y = (self.height() // 2) - 260
        text_rect = QRect(0, text_y, self.width(), 100)

        # Font Setup
        font = QFont("Consolas", 48) 
        font.setBold(True)
        font.setLetterSpacing(QFont.AbsoluteSpacing, 8) 
        painter.setFont(font)

        # Gradient Color Setup
        gradient = QLinearGradient(text_rect.topLeft(), text_rect.topRight())
        gradient.setColorAt(0.3, QColor(0, 229, 255))  # Cyan start
        gradient.setColorAt(0.7, QColor(190, 0, 255))  # Purple end
        
        pen = QPen(QBrush(gradient), 1)
        painter.setPen(pen)

        # Draw
        painter.drawText(text_rect, Qt.AlignCenter, "J A R V I S")

# ---------------- RUN ----------------
if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app = QApplication(sys.argv)
    window = HUD()   # <--- YAHAN CHANGE HUA HAI
    window.show()
    sys.exit(app.exec_())