from PyQt6.QtWidgets import QApplication, QWidget, QCheckBox, QLineEdit, QVBoxLayout
from PyQt6.QtCore import Qt
import sys

class TestWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.checkbox = QCheckBox("Veterinário")
        self.lineedit = QLineEdit()
        self.lineedit.setEnabled(False)
        self.lineedit.setReadOnly(True)

        layout = QVBoxLayout(self)
        layout.addWidget(self.checkbox)
        layout.addWidget(self.lineedit)

        self.checkbox.stateChanged.connect(self.toggle_lineedit)

    def toggle_lineedit(self, state):
        if state == Qt.Checked:
            self.lineedit.setEnabled(True)
            self.lineedit.setReadOnly(False)
            self.lineedit.setFocus()
        else:
            self.lineedit.setEnabled(False)
            self.lineedit.setReadOnly(True)
            self.lineedit.clear()

app = QApplication(sys.argv)
w = TestWidget()
w.show()
sys.exit(app.exec())
