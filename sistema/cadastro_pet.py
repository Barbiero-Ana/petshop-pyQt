from PyQt6.QtWidgets import (
    QDialog, QFileDialog, QMessageBox,
    QWidget, QLabel, QVBoxLayout, QListView
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from PyQt6 import uic
from data import inserir_pet, buscar_pets_usuario
import os
import requests

class DialogAddPet(QDialog):
    def __init__(self, email_usuario):
        super().__init__()
        uic.loadUi("telas/cadastro_pet.ui", self)

        self.email_usuario = email_usuario
        self.foto_path = ""

        self.selecionarFotoButton.clicked.connect(self.selecionar_foto)
        self.confirmarButton.clicked.connect(self.confirmar)
        self.cancelarButton.clicked.connect(self.reject)

        # Configuração da ComboBox de raças com QListView e scroll estilizado
        self.racaPetInput.setView(QListView())
        self.racaPetInput.view().setStyleSheet("""
            QScrollBar:vertical {
                background: #f0f0f0;
                width: 12px;
                margin: 0px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #483AA0;
                min-height: 20px;
                border-radius: 6px;
            }
        """)

        # Permitir drag & drop na label de foto
        self.fotoPreview.setAcceptDrops(True)
        self.fotoPreview.installEventFilter(self)

        # Atualizar raças ao mudar espécie
        self.especiePetInput.currentIndexChanged.connect(self.atualizar_racas)
        self.atualizar_racas()

    def eventFilter(self, obj, event):
        if obj == self.fotoPreview:
            if event.type() == event.Type.DragEnter:
                if event.mimeData().hasUrls():
                    event.accept()
                    return True
            elif event.type() == event.Type.Drop:
                urls = event.mimeData().urls()
                if urls:
                    path = urls[0].toLocalFile()
                    if path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                        self.set_foto(path)
                    else:
                        self.mostrar_msg_erro("Arquivo inválido", "Por favor, selecione uma imagem válida.")
                return True
        return super().eventFilter(obj, event)

    def selecionar_foto(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilters(["Imagens (*.png *.jpg *.jpeg *.bmp *.gif)"])
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                self.set_foto(selected_files[0])

    def set_foto(self, path):
        pixmap = QPixmap(path)
        if pixmap.isNull():
            self.mostrar_msg_erro("Erro", "Não foi possível carregar a imagem.")
            return
        pixmap = pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.fotoPreview.setPixmap(pixmap)
        self.foto_path = path

    def atualizar_racas(self):
        especie = self.especiePetInput.currentText()
        self.racaPetInput.clear()

        if especie == "Cachorro":
            racas = self.buscar_racas_cachorro()
        elif especie == "Gato":
            racas = self.buscar_racas_gato()
        else:
            racas = []

        self.racaPetInput.addItems(racas)

    def buscar_racas_cachorro(self):
        try:
            response = requests.get("https://api.thedogapi.com/v1/breeds")
            response.raise_for_status()
            dados = response.json()
            racas = [r["name"] for r in dados]
            return racas
        except Exception as e:
            self.mostrar_msg_erro("Erro API", f"Erro ao buscar raças de cachorro: {e}")
            return []

    def buscar_racas_gato(self):
        try:
            response = requests.get("https://api.thecatapi.com/v1/breeds")
            response.raise_for_status()
            dados = response.json()
            racas = [r["name"] for r in dados]
            return racas
        except Exception as e:
            self.mostrar_msg_erro("Erro API", f"Erro ao buscar raças de gato: {e}")
            return []

    def mostrar_msg_erro(self, titulo, texto):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle(titulo)
        msg.setText(texto)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: white;
                color: black;
            }
            QLabel {
                color: black;
            }
            QPushButton {
                background-color: #483AA0;
                color: white;
                border-radius: 6px;
                padding: 6px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #0E2148;
            }
        """)
        msg.exec()

    def confirmar(self):
        nome = self.nomePetInput.text().strip()
        idade = self.idadePetInput.text().strip()
        raca = self.racaPetInput.currentText()
        sexo = self.sexoPetInput.currentText()
        foto = self.foto_path

        if not nome:
            self.mostrar_msg_erro("Erro", "Informe o nome do pet.")
            return
        if not idade or not idade.isdigit() or int(idade) <= 0:
            self.mostrar_msg_erro("Erro", "Informe uma idade válida (número inteiro positivo).")
            return
        if not raca:
            self.mostrar_msg_erro("Erro", "Informe a raça do pet.")
            return
        if sexo not in ['Macho', 'Fêmea']:
            self.mostrar_msg_erro("Erro", "Informe o sexo do pet.")
            return

        try:
            inserir_pet(self.email_usuario, nome, idade, raca, sexo, foto)
        except Exception as e:
            self.mostrar_msg_erro("Erro ao salvar", f"Erro ao salvar pet: {e}")
            return

        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("Sucesso")
        msg.setText("Pet cadastrado com sucesso!")
        msg.setStyleSheet("""
            QMessageBox {
                background-color: white;
                color: black;
            }
            QLabel {
                color: black;
            }
            QPushButton {
                background-color: #483AA0;
                color: white;
                border-radius: 6px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #0E2148;
            }
        """)
        msg.exec()
        self.accept()

class PetCard(QWidget):
    def __init__(self, nome, idade, raca, foto):
        super().__init__()

        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        self.setLayout(layout)

        self.label_foto = QLabel()
        if foto and os.path.exists(foto):
            pixmap = QPixmap(foto)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(140, 140, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.label_foto.setPixmap(pixmap)
            else:
                self.label_foto.setText("Imagem inválida")
        else:
            self.label_foto.setText("Sem foto")

        self.label_foto.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label_foto)

        self.label_nome = QLabel(nome)
        self.label_nome.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_nome.setStyleSheet("font-weight: bold; font-size: 16pt; color: #483AA0;")
        layout.addWidget(self.label_nome)

        self.label_idade = QLabel(f"Idade: {idade}")
        self.label_idade.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_idade.setStyleSheet("font-size: 13pt;")
        layout.addWidget(self.label_idade)

        self.label_raca = QLabel(f"Raça: {raca}")
        self.label_raca.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_raca.setStyleSheet("font-size: 13pt;")
        layout.addWidget(self.label_raca)

        self.setStyleSheet("""
            QWidget {
                border: 2px solid #483AA0;
                border-radius: 15px;
                background-color: #f0f0ff;
                max-width: 180px;
                min-width: 160px;
                min-height: 260px;
            }
        """)
