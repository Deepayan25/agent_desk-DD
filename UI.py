from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QLineEdit, QMainWindow, QPushButton, QTextEdit, QVBoxLayout, QWidget


class AgentWorker(QThread):
    message = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        from queue import Queue

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


class AgentDeskWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AgentDesk")
        self.setMinimumSize(700, 500)
        self.setup_ui()
        self.worker = AgentWorker()
        self.worker.message.connect(self.log.append)
        self.worker.start()

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        layout.addWidget(self.log)
        self.log.append("Welcome to manas! how may I assist you today?")

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type a command...")
        layout.addWidget(self.input_field)

        self.send_btn = QPushButton("RUN")
        self.input_field.returnPressed.connect(self.send_command)
        layout.addWidget(self.send_btn)
        self.send_btn.clicked.connect(self.send_command)

    def send_command(self):
        cmd = self.input_field.text().strip()
        if not cmd:
            return

        self.log.append(cmd)
        self.worker.send_command(cmd)
        self.input_field.clear()