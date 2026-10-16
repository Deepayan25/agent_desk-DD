from queue import Queue

from PyQt6.QtCore import QPoint, Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QLabel, QLineEdit, QMainWindow, QPushButton,
    QTextEdit, QVBoxLayout, QWidget
)


# ── Worker Thread ────────────────────────────────────────────────────────────

class AgentWorker(QThread):
    message = pyqtSignal(str)
    ask_user = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.command_queue = Queue()
        self.response_queue = Queue()

    def send_command(self, cmd):
        self.command_queue.put(cmd)

    def send_response(self, reply):
        self.response_queue.put(reply)

    def run(self):
        import executor as execution_module
        self.message.emit("Worker started.")

        while True:
            cmd = self.command_queue.get()
            try:
                results = execution_module.execution_workflow(cmd)
            except Exception as exc:
                self.message.emit(f"Worker error: {exc}")
                continue

            if not results:
                self.message.emit("No action could be parsed from that command.")
                continue

            if results[-1].get("waiting_for_user"):
                failure = results[-1].get("failure", {})
                action = failure.get("action", "Action")
                reason = failure.get("reason", "Unknown error")

                self.message.emit(f"{action} failed: {reason}")
                self.message.emit("Waiting for user decision...")
                continue

            if results[-1].get("success"):
                self.message.emit("Done.")

                if self._should_enter_browser_loop(cmd):
                    self._fake_browser_loop(cmd)
            else:
                reason = results[-1].get("reason", "Unknown error")
                self.message.emit(f"Failed: {reason}")

    def _should_enter_browser_loop(self, cmd):
        return cmd.strip().lower().startswith("open")

    def _fake_browser_loop(self, cmd):
        import actions

        while True:
            self.ask_user.emit("what to do, sir?")
            reply = self.response_queue.get()

            if reply.lower().strip() in ("done", "thanks"):
                self.message.emit("okay, back to normal.")
                return

            # Parse reply: first word is action, rest is the query
            parts = reply.strip().split(maxsplit=1)
            action = parts[0].lower()
            query = parts[1] if len(parts) > 1 else ""

            handler = actions.actions.get(action)
            if handler is None:
                self.message.emit(f"I don't know how to '{action}', sir.")
                continue

            try:
                result = handler(query)
            except Exception as e:
                self.message.emit(f"'{action}' failed: {e}")
                continue

            if result and result.get("success"):
                self.message.emit(f"{action} done.")
            else:
                reason = (result or {}).get("reason", "unknown error")
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
        self.expecting_reply = False 
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
        self.worker.message.connect(self._on_worker_message)
        self.worker.ask_user.connect(self._on_worker_ask)
        self.worker.start()

    def _on_worker_message(self, text):
        self.log.append(text)

    def _on_worker_ask(self, question):
        self.expecting_reply = True
        self.log.append(question)
        self.input_field.setPlaceholderText("reply...")
        self.input_field.setFocus()

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
        self.log.append(f"> {cmd}")
        self.input_field.clear()

        if getattr(self, "expecting_reply", False):
            self.worker.send_response(cmd)
            self.expecting_reply = False
            self.input_field.setPlaceholderText("Type a command...")
        else:
            self.worker.send_command(cmd)