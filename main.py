import sys
from PyQt6.QtWidgets import QApplication
from UI import AgentDeskWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    window = AgentDeskWindow()
    window.show()
    sys.exit(app.exec())