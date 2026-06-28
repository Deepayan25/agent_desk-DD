import sys
from PyQt6.QtWidgets import QApplication
from UI import AgentDeskWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    window = AgentDeskWindow()
    window.showMaximized()
    sys.exit(app.exec())