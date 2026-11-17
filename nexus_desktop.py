#!/usr/bin/env python3
"""NEXUS OS 1.1 desktop prototype.

Minimal desktop shell, cinematic startup screen, system overview, and optional
local text assistant backed by an Ollama server on localhost.
"""
import json
import shutil
import subprocess
import sys
import urllib.request
import urllib.error

import psutil
from PySide6.QtCore import Qt, QTimer, QThread, Signal, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QColor
from PySide6.QtWidgets import (
    QApplication, QWidget, QMainWindow, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QStackedWidget, QFrame, QTextEdit, QLineEdit, QComboBox,
    QProgressBar, QGraphicsOpacityEffect, QMessageBox
)

BG = "#080D18"
SURFACE = "#101A2B"
SURFACE_2 = "#16243B"
BORDER = "#263B5B"
BLUE = "#43BFFF"
VIOLET = "#A77BFF"
TEXT = "#ECF4FF"
MUTED = "#93A6C2"

APP_STYLE = f"""
QWidget {{ background:{BG}; color:{TEXT}; font-family:'Inter','Noto Sans',sans-serif; }}
QFrame#panel {{ background:{SURFACE}; border:1px solid {BORDER}; border-radius:15px; }}
QLabel#muted {{ color:{MUTED}; }}
QLabel#eyebrow {{ color:{BLUE}; font-size:11px; font-weight:700; letter-spacing:2px; }}
QLabel#bigValue {{ color:{TEXT}; font-size:26px; font-weight:700; }}
QPushButton {{ background:{SURFACE_2}; color:{TEXT}; border:1px solid {BORDER};
  border-radius:9px; padding:10px 14px; text-align:left; }}
QPushButton:hover {{ border:1px solid {VIOLET}; background:#1B2B47; }}
QPushButton:checked {{ background:#1C3554; border:1px solid {BLUE}; color:white; }}
QLineEdit, QTextEdit, QComboBox {{ background:#0B1423; color:{TEXT}; border:1px solid {BORDER};
  border-radius:9px; padding:10px; selection-background-color:#315A8A; }}
QProgressBar {{ background:#0B1423; border:0; border-radius:4px; height:7px; text-align:center; }}
QProgressBar::chunk {{ background:{BLUE}; border-radius:4px; }}
"""

def panel():
    f = QFrame()
    f.setObjectName("panel")
    return f

class Startup(QWidget):
    """Short cinematic splash; deliberately avoids delaying boot excessively."""
    finished = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.SplashScreen | Qt.WindowType.FramelessWindowHint)
        self.setFixedSize(520, 300)
        self.setStyleSheet(f"QWidget{{background:{BG};border:1px solid {BORDER};border-radius:20px;}}")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(38, 32, 38, 30)
        layout.addStretch()
        logo = QLabel("N")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet(f"color:{BLUE};font-size:68px;font-weight:800;border:0;")
        title = QLabel("N E X U S")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"color:{TEXT};font-size:25px;font-weight:700;letter-spacing:7px;border:0;")
        subtitle = QLabel("INTELLIGENCE, WITHOUT COMPROMISE")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet(f"color:{MUTED};font-size:10px;letter-spacing:2px;border:0;")
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(5)
        self.status = QLabel("INITIALIZING NEXUS SERVICES")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status.setStyleSheet(f"color:{BLUE};font-size:10px;letter-spacing:1px;border:0;")
        layout.addStretch()
        layout.addWidget(logo)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(26)
        layout.addWidget(self.progress)
        layout.addWidget(self.status)
        layout.addStretch()
        self.value = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.advance)
        self.timer.start(28)

    def advance(self):
        self.value = min(100, self.value + 2)
        self.progress.setValue(self.value)
        if self.value == 35:
            self.status.setText("LOADING DESKTOP")
        elif self.value == 70:
            self.status.setText("STARTING LOCAL SERVICES")
        elif self.value == 100:
            self.timer.stop()
            self.status.setText("WELCOME")
            QTimer.singleShot(250, self.finished.emit)

class OllamaWorker(QThread):
    completed = Signal(str)
    failed = Signal(str)

    def __init__(self, model, messages):
        super().__init__()
        self.model = model
        self.messages = messages

    def run(self):
        payload = json.dumps({
            "model": self.model,
            "messages": self.messages,
            "stream": False
        }).encode("utf-8")
        request = urllib.request.Request(
            "http://127.0.0.1:11434/api/chat",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                data = json.loads(response.read().decode("utf-8"))
            answer = data.get("message", {}).get("content", "").strip()
            self.completed.emit(answer or "The local model returned an empty response.")
        except urllib.error.URLError as exc:
            self.failed.emit(
                "Can't reach Ollama at http://127.0.0.1:11434. "
                "Start Ollama and download a model first. Details: " + str(exc)
            )
        except Exception as exc:
            self.failed.emit("Local AI request failed: " + str(exc))

class ChatPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        heading = QLabel("NEXUS AI")
        heading.setStyleSheet(f"font-size:28px;font-weight:700;color:{TEXT};")
        desc = QLabel("Private, local text assistant · powered by Ollama")
        desc.setObjectName("muted")
        self.model = QComboBox()
        self.model.setEditable(True)
        self.model.addItems(["llama3.2:3b", "qwen2.5:7b", "mistral:7b"])
        self.model.setToolTip("Enter the exact model name installed in Ollama.")
        self.chat = QTextEdit()
        self.chat.setReadOnly(True)
        self.chat.setPlaceholderText("Your conversation will appear here.")
        self.chat.append("NEXUS AI  /  LOCAL SESSION\nChoose an installed model and ask a question.")
        controls = QHBoxLayout()
        self.prompt = QLineEdit()
        self.prompt.setPlaceholderText("Message your local assistant…")
        self.send = QPushButton("Send")
        self.send.clicked.connect(self.send_message)
        self.prompt.returnPressed.connect(self.send_message)
        controls.addWidget(self.prompt, 1)
        controls.addWidget(self.send)
        hint = QLabel("Your prompt is sent to the Ollama service on this computer (localhost).")
        hint.setObjectName("muted")
        layout.addWidget(heading)
        layout.addWidget(desc)
        layout.addWidget(self.model)
        layout.addWidget(self.chat, 1)
        layout.addLayout(controls)
        layout.addWidget(hint)
        self.history = []
        self.worker = None

    def send_message(self):
        text = self.prompt.text().strip()
        if not text or (self.worker and self.worker.isRunning()):
            return
        model = self.model.currentText().strip()
        if not model:
            self.chat.append("\nNEXUS: Enter a local model name.")
            return
        self.prompt.clear()
        self.chat.append(f"\nYOU\n{text}")
        self.history.append({"role": "user", "content": text})
        self.send.setEnabled(False)
        self.send.setText("Thinking…")
        self.worker = OllamaWorker(model, list(self.history))
        self.worker.completed.connect(self.on_answer)
        self.worker.failed.connect(self.on_error)
        self.worker.start()

    def on_answer(self, answer):
        self.chat.append(f"\nNEXUS AI\n{answer}")
        self.history.append({"role": "assistant", "content": answer})
        self.finish_request()

    def on_error(self, message):
        self.chat.append(f"\nLOCAL AI STATUS\n{message}")
        # Keep failed prompt out of conversation history so it can be retried.
        if self.history and self.history[-1]["role"] == "user":
            self.history.pop()
        self.finish_request()

    def finish_request(self):
        self.send.setEnabled(True)
        self.send.setText("Send")
        self.prompt.setFocus()

class StatCard(QFrame):
    def __init__(self, title):
        super().__init__()
        self.setObjectName("panel")
        lay = QVBoxLayout(self)
        name = QLabel(title.upper())
        name.setObjectName("eyebrow")
        self.value = QLabel("--")
        self.value.setObjectName("bigValue")
        self.detail = QLabel("")
        self.detail.setObjectName("muted")
        lay.addWidget(name)
        lay.addWidget(self.value)
        lay.addWidget(self.detail)

class HomePage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        hello = QLabel("Good evening.")
        hello.setStyleSheet("font-size:30px;font-weight:700;")
        sub = QLabel("Your system. Your control. Your space.")
        sub.setObjectName("muted")
        layout.addWidget(hello)
        layout.addWidget(sub)
        row = QHBoxLayout()
        self.cpu = StatCard("Processor")
        self.memory = StatCard("Memory")
        self.disk = StatCard("Storage")
        row.addWidget(self.cpu)
        row.addWidget(self.memory)
        row.addWidget(self.disk)
        layout.addLayout(row)
        hero = panel()
        hl = QVBoxLayout(hero)
        tag = QLabel("NEXUS OS  /  1.1 DEVELOPMENT")
        tag.setObjectName("eyebrow")
        title = QLabel("A quieter kind of power.")
        title.setStyleSheet(f"font-size:24px;font-weight:700;color:{TEXT};")
        body = QLabel("Minimal by design. Capable by default. Local-first intelligence.")
        body.setObjectName("muted")
        hl.addWidget(tag)
        hl.addWidget(title)
        hl.addWidget(body)
        hl.addStretch()
        layout.addWidget(hero, 1)
        self.refresh()

    def refresh(self):
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        self.cpu.value.setText(f"{cpu:.0f}%")
        self.cpu.detail.setText(f"{psutil.cpu_count(logical=True)} logical threads")
        self.memory.value.setText(f"{mem.percent:.0f}%")
        self.memory.detail.setText(f"{mem.used / 1024**3:.1f} / {mem.total / 1024**3:.1f} GiB")
        self.disk.value.setText(f"{disk.percent:.0f}%")
        self.disk.detail.setText(f"{disk.used / 1024**3:.0f} / {disk.total / 1024**3:.0f} GiB")

class SystemPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        title = QLabel("System")
        title.setStyleSheet("font-size:28px;font-weight:700;")
        layout.addWidget(title)
        info = panel()
        il = QVBoxLayout(info)
        self.info = QLabel()
        self.info.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.info.setWordWrap(True)
        il.addWidget(self.info)
        layout.addWidget(info)
        layout.addStretch()
        self.refresh()

    def refresh(self):
        self.info.setText(
            f"Operating system: {sys.platform}\n"
            f"Python: {sys.version.split()[0]}\n"
            f"Logical CPU threads: {psutil.cpu_count(logical=True)}\n"
            f"Physical CPU cores: {psutil.cpu_count(logical=False)}\n"
            f"Boot time: {psutil.boot_time():.0f} (Unix timestamp)\n\n"
            "Hardware sensors and GPU telemetry are planned for a later milestone."
        )

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NEXUS OS")
        self.resize(1120, 720)
        root = QWidget()
        self.setCentralWidget(root)
        layout = QHBoxLayout(root)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(14)

        sidebar = QFrame()
        sidebar.setObjectName("panel")
        sidebar.setFixedWidth(205)
        side = QVBoxLayout(sidebar)
        logo = QLabel("NEXUS")
        logo.setStyleSheet(f"font-size:22px;font-weight:800;color:{BLUE};letter-spacing:3px;")
        edition = QLabel("OS  /  1.1")
        edition.setObjectName("muted")
        side.addWidget(logo)
        side.addWidget(edition)
        side.addSpacing(28)
        self.stack = QStackedWidget()
        self.pages = [HomePage(), ChatPage(), SystemPage()]
        self.buttons = []
        for i, (name, page) in enumerate(zip(("Overview", "NEXUS AI", "System"), self.pages)):
            btn = QPushButton(name)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked=False, idx=i: self.navigate(idx))
            side.addWidget(btn)
            self.buttons.append(btn)
            self.stack.addWidget(page)
        side.addStretch()
        local = QLabel("LOCAL-FIRST\nNo mandatory cloud services")
        local.setObjectName("muted")
        side.addWidget(local)
        layout.addWidget(sidebar)
        layout.addWidget(self.stack, 1)
        self.navigate(0)
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh)
        self.refresh_timer.start(2500)

    def navigate(self, index):
        self.stack.setCurrentIndex(index)
        for i, button in enumerate(self.buttons):
            button.setChecked(i == index)

    def refresh(self):
        self.pages[0].refresh()
        self.pages[2].refresh()

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("NEXUS OS")
    app.setStyleSheet(APP_STYLE)
    splash = Startup()
    splash.show()
    window = MainWindow()
    def reveal():
        window.show()
        effect = QGraphicsOpacityEffect(window)
        window.setGraphicsEffect(effect)
        anim = QPropertyAnimation(effect, b"opacity", window)
        anim.setDuration(550)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.start()
        window._fade_animation = anim
        splash.close()
    splash.finished.connect(reveal)
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
