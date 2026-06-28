from queue import Queue

from PyQt6.QtCore import QPoint, Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QLabel, QLineEdit, QMainWindow, QPushButton,
    QTextEdit, QVBoxLayout, QWidget
)


# ── Worker Thread ────────────────────────────────────────────────────────────

class AgentWorker(QThread):
    message = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.command_queue = Queue()

    def send_command(self, cmd):
        self.command_queue.put(cmd)

    def run(self):
        import controller as controller_module
        self.message.emit("Worker started.")

        while True:
            cmd = self.command_queue.get()
            try:
                results = controller_module.execute_raw_command(cmd)
            except Exception as exc:
                self.message.emit(f"Worker error: {exc}")
                continue

            if not results:
                self.message.emit("No action could be parsed from that command.")
                continue

            for result in results:
                action = result.get("action") or "command"
                if result.get("success"):
                    self.message.emit(f"{action} completed.")
                else:
                    reason = result.get("reason", "Unknown error")
                    self.message.emit(f"{action} failed: {reason}")


# ── Floating Console Widget ──────────────────────────────────────────────────

class FloatingConsole(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.drag_position = QPoint()

    def mousePressEvent(self, event):
        self.drag_position = event.pos()

    def mouseMoveEvent(self, event):
        self.move(self.pos() + event.pos() - self.drag_position)

    def mouseDoubleClickEvent(self, event):
        self.parent().parent().close_console()


# ── Main Window ──────────────────────────────────────────────────────────────

class AgentDeskWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AgentDesk")
        self.setMinimumSize(700, 500)
        self.setup_ui()
        self._start_worker()

    # ── Setup ────────────────────────────────────────────────────────────────

    def setup_ui(self):
        self.central = QWidget()
        self.central.setStyleSheet("background-color: #071424;")
        self.setCentralWidget(self.central)

        layout = QVBoxLayout(self.central)
        layout.addWidget(self._build_face_label())

        self._build_console()
        self._build_manas_icon()

        self.console.hide()

    def _build_face_label(self):
        self.face_label = QLabel("●")
        self.face_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.face_label.setStyleSheet("color: white; font-size: 120px;")
        return self.face_label

    def _build_console(self):
        self.console = FloatingConsole(self.central)
        self.console.setStyleSheet("background-color: #071430; border-radius: 10px;")
        self.console.move(50, 500)
        self.console.resize(500, 350)

        layout = QVBoxLayout(self.console)

        title = QLabel("MANAS CONSOLE")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.append("Welcome to Manas! How may I assist you today?")
        layout.addWidget(self.log)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type a command...")
        self.input_field.returnPressed.connect(self.send_command)
        layout.addWidget(self.input_field)

        self.send_btn = QPushButton("RUN")
        self.send_btn.clicked.connect(self.send_command)
        layout.addWidget(self.send_btn)

    def _build_manas_icon(self):
        self.manas_icon = QPushButton("●", self.central)
        self.manas_icon.resize(50, 50)
        self.manas_icon.move(20, 800)
        self.manas_icon.clicked.connect(self.open_console)

    def _start_worker(self):
        self.worker = AgentWorker()
        self.worker.message.connect(self.log.append)
        self.worker.start()

    # ── Console Visibility ───────────────────────────────────────────────────

    def open_console(self):
        self.manas_icon.hide()
        self.console.show()

    def close_console(self):
        self.console.hide()
        self.manas_icon.show()

    # ── Command Handling ─────────────────────────────────────────────────────

    def send_command(self):
        cmd = self.input_field.text().strip()
        if not cmd:
            return
        self.log.append(cmd)
        self.worker.send_command(cmd)
        self.input_field.clear()