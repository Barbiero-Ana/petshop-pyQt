import sys
from PyQt6.QtWidgets import QApplication, QDialog, QCheckBox, QLineEdit, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt
import re

class TestDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Teste CRVET")

        self.checkbox = QCheckBox("Veterinário", self)
        self.lineEditCRVET = QLineEdit(self)
        self.labelObrigatorio = QLabel("* Campo obrigatório", self)
        self.labelObrigatorio.setStyleSheet("color: red")
        self.labelObrigatorio.setVisible(False)

        # Começa em readOnly = True para bloquear digitação, mas ENABLED para poder focar
        self.lineEditCRVET.setReadOnly(True)

        layout = QVBoxLayout(self)
        layout.addWidget(self.checkbox)
        layout.addWidget(self.lineEditCRVET)
        layout.addWidget(self.labelObrigatorio)

        self.checkbox.stateChanged.connect(self.toggle_crvet)
        self.lineEditCRVET.textChanged.connect(self.validar_crvet)

    def toggle_crvet(self, state):
        is_checked = state == Qt.CheckState.Checked
        # Aqui só alterna readOnly, NÃO desabilita o campo (nunca usar setEnabled False!)
        self.lineEditCRVET.setReadOnly(not is_checked)
        if not is_checked:
            self.lineEditCRVET.clear()
            self.labelObrigatorio.setVisible(False)
            self.lineEditCRVET.setStyleSheet("")

    def validar_crvet(self, text):
        # Só valida se o campo estiver editável
        if self.lineEditCRVET.isReadOnly():
            return

        padrao = r'^[A-Za-z0-9]{5,}$'
        if re.fullmatch(padrao, text):
            self.labelObrigatorio.setVisible(False)
            self.lineEditCRVET.setStyleSheet("border: 1px solid green;")
        else:
            self.labelObrigatorio.setVisible(True)
            self.lineEditCRVET.setStyleSheet("border: 1px solid red;")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dlg = TestDialog()
    dlg.show()
    sys.exit(app.exec())
