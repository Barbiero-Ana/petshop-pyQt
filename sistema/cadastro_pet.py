from PyQt6.QtWidgets import (
    QDialog, QFileDialog, QMessageBox,
    QWidget, QLabel, QHBoxLayout, QListView, QVBoxLayout
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from PyQt6 import uic
from data import inserir_pet
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
    def __init__(self, nome, idade, raca, foto_path):
        super().__init__()

        layout = QHBoxLayout()
        self.setLayout(layout)

        label_foto = QLabel()
        if foto_path and os.path.exists(foto_path):
            pixmap = QPixmap(foto_path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(100, 100, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio)
                label_foto.setPixmap(pixmap)
            else:
                label_foto.setText("Imagem inválida")
        else:
            label_foto.setText("Sem foto")

        label_info = QLabel(f"🐾 Nome: {nome}\n📅 Idade: {idade}\n🐶 Raça: {raca}")

        layout.addWidget(label_foto)
        layout.addWidget(label_info)




class PetCard(QWidget):
    def __init__(self, nome, idade, raca, foto):
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.label_nome = QLabel(f"Nome: {nome}")
        self.label_idade = QLabel(f"Idade: {idade}")
        self.label_raca = QLabel(f"Raça: {raca}")
        layout.addWidget(self.label_nome)
        layout.addWidget(self.label_idade)
        layout.addWidget(self.label_raca)

        # Se tiver caminho da foto e a foto existir, exibe a imagem
        if foto:
            try:
                pixmap = QPixmap(foto)
                if not pixmap.isNull():
                    self.label_foto = QLabel()
                    self.label_foto.setPixmap(pixmap.scaledToWidth(100))
                    layout.addWidget(self.label_foto)
            except Exception as e:
                print("Erro ao carregar foto do pet:", e)
