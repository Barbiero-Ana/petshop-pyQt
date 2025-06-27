from PyQt6.QtWidgets import QDialog, QMessageBox, QLabel, QVBoxLayout, QPushButton
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from PyQt6 import uic
from data import buscar_pets_usuario
import os

class DialogInfoPet(QDialog):
    def __init__(self, pet, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Informações do Pet - {pet[1]}")

        id_pet, nome, idade, raca, foto = pet

        layout = QVBoxLayout(self)

        label_nome = QLabel(f"<b>Nome:</b> {nome}")
        label_idade = QLabel(f"<b>Idade:</b> {idade}")
        label_raca = QLabel(f"<b>Raça:</b> {raca}")

        layout.addWidget(label_nome)
        layout.addWidget(label_idade)
        layout.addWidget(label_raca)

        if foto and os.path.exists(foto):
            pixmap = QPixmap(foto)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(250, 250, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                label_foto = QLabel()
                label_foto.setPixmap(pixmap)
                label_foto.setAlignment(Qt.AlignmentFlag.AlignCenter)
                layout.addWidget(label_foto)

        btn_ok = QPushButton("Fechar")
        btn_ok.clicked.connect(self.accept)
        layout.addWidget(btn_ok)

class DialogListaPets(QDialog):
    def __init__(self, email_usuario):
        super().__init__()
        uic.loadUi('telas/dialog/list_pets.ui', self)  

        self.email_usuario = email_usuario
        self.listaPets.itemClicked.connect(self.exibir_info_pet)

        self.carregar_pets()

    def carregar_pets(self):
        self.listaPets.clear()
        pets = buscar_pets_usuario(self.email_usuario)
        if not pets:
            self.listaPets.addItem("Nenhum pet cadastrado.")
            self.listaPets.setEnabled(False)
        else:
            self.listaPets.setEnabled(True)
            for pet in pets:
                id_pet, nome, idade, raca, foto = pet
                self.listaPets.addItem(nome)

    def exibir_info_pet(self, item):
        nome_selecionado = item.text()
        pets = buscar_pets_usuario(self.email_usuario)
        pet_info = next((p for p in pets if p[1] == nome_selecionado), None)
        if pet_info:
            dialog = DialogInfoPet(pet_info, self)
            dialog.exec()
        else:
            QMessageBox.warning(self, "Aviso", "Informações do pet não encontradas.")
