from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt

class TelaCarregamento(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Carregando...")
        self.setFixedSize(250, 100)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)

        layout = QVBoxLayout()
        self.label = QLabel("Carregando...")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)
        self.setLayout(layout)
