from PyQt6.QtWidgets import QDialog, QMessageBox, QLineEdit  
from PyQt6 import uic
import hashlib
from data import atualizar_senha_temporaria

class DialogTrocaSenha(QDialog):
    def __init__(self, email):
        super().__init__()
        uic.loadUi("telas/dialog/troca_senha.ui", self)

        self.lineEditNovaSenha.setEchoMode(QLineEdit.EchoMode.Password) 
        self.email = email
        self.setWindowTitle("Nova Senha Obrigatória")

        self.btnConfirmar.clicked.connect(self.trocar_senha)

    def trocar_senha(self):
        nova = self.lineEditNovaSenha.text().strip()
        if not nova or len(nova) < 6:
            QMessageBox.warning(self, "Erro", "A senha deve ter ao menos 6 caracteres.")
            return

        senha_hash = hashlib.sha256(nova.encode()).hexdigest()
        atualizar_senha_temporaria(self.email, senha_hash)
        QMessageBox.information(self, "Sucesso", "Senha atualizada com sucesso.")
        self.accept()
