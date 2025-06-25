from PyQt6.QtWidgets import (
    QDialog, QFileDialog, QMessageBox, QListWidgetItem, QListView
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from PyQt6 import uic
from data import inserir_pet, buscar_usuarios_email_nome
import requests


class DialogCadastroPet(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("telas/dialog/cadastro_pet_adm.ui", self)

        self.foto_path = ""

        # Conexões
        self.btnSelecionarFoto.clicked.connect(self.selecionar_foto)
        self.btnConfirmar.clicked.connect(self.confirmar)
        self.btnCancelar.clicked.connect(self.reject)

        self.checkBoxSemDono.stateChanged.connect(self.toggle_dono_input)
        self.lineEditDono.textChanged.connect(self.atualizar_lista_usuarios)
        self.listWidgetUsuarios.itemClicked.connect(self.selecionar_usuario_lista)

        self.especiePetInput.setView(QListView())
        self.especiePetInput.currentIndexChanged.connect(self.atualizar_racas)
        self.atualizar_racas()

        # Drag & Drop
        self.fotoPreview.setAcceptDrops(True)
        self.fotoPreview.installEventFilter(self)

        self.toggle_dono_input()

    def toggle_dono_input(self):
        ativo = not self.checkBoxSemDono.isChecked()
        self.lineEditDono.setEnabled(ativo)
        self.listWidgetUsuarios.setEnabled(ativo)
        if not ativo:
            self.lineEditDono.clear()
            self.listWidgetUsuarios.clear()

    def atualizar_lista_usuarios(self):
        termo = self.lineEditDono.text().strip()
        self.listWidgetUsuarios.clear()
        if termo:
            resultados = buscar_usuarios_email_nome(termo)
            for email, nome in resultados:
                item = QListWidgetItem(f"{nome} <{email}>")
                item.setData(Qt.ItemDataRole.UserRole, email)
                self.listWidgetUsuarios.addItem(item)

    def selecionar_usuario_lista(self, item):
        email = item.data(Qt.ItemDataRole.UserRole)
        self.lineEditDono.setText(email)

    def eventFilter(self, obj, event):
        if obj == self.fotoPreview:
            if event.type() == event.Type.DragEnter and event.mimeData().hasUrls():
                event.accept()
                return True
            elif event.type() == event.Type.Drop:
                path = event.mimeData().urls()[0].toLocalFile()
                if path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                    self.set_foto(path)
                else:
                    self.mostrar_erro("Formato inválido", "Por favor, selecione uma imagem.")
                return True
        return super().eventFilter(obj, event)

    def selecionar_foto(self):
        caminho, _ = QFileDialog.getOpenFileName(self, "Selecionar Foto", filter="Imagens (*.png *.jpg *.jpeg *.bmp *.gif)")
        if caminho:
            self.set_foto(caminho)

    def set_foto(self, path):
        pixmap = QPixmap(path)
        if not pixmap.isNull():
            self.fotoPreview.setPixmap(pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio))
            self.foto_path = path
        else:
            self.mostrar_erro("Erro", "Imagem inválida")

    def atualizar_racas(self):
        especie = self.especiePetInput.currentText()
        self.racaPetInput.clear()
        racas = []

        try:
            if especie == "Cachorro":
                racas = [r["name"] for r in requests.get("https://api.thedogapi.com/v1/breeds").json()]
            elif especie == "Gato":
                racas = [r["name"] for r in requests.get("https://api.thecatapi.com/v1/breeds").json()]
        except Exception as e:
            self.mostrar_erro("Erro API", f"Não foi possível carregar raças: {e}")

        self.racaPetInput.addItems(racas)

    def mostrar_erro(self, titulo, mensagem):
        QMessageBox.warning(self, titulo, mensagem)

    def confirmar(self):
        nome = self.lineEditNomePet.text().strip()
        idade = self.lineEditIdade.text().strip()
        raca = self.racaPetInput.currentText().strip()
        sexo = self.sexoPetInput.currentText()
        dono = None if self.checkBoxSemDono.isChecked() else self.lineEditDono.text().strip()

        if not nome:
            self.mostrar_erro("Erro", "Informe o nome.")
            return
        if not idade.isdigit() or int(idade) <= 0:
            self.mostrar_erro("Erro", "Informe uma idade válida.")
            return
        if not raca:
            self.mostrar_erro("Erro", "Informe a raça.")
            return
        if sexo not in ["Macho", "Fêmea"]:
            self.mostrar_erro("Erro", "Informe o sexo.")
            return
        if not self.checkBoxSemDono.isChecked() and not dono:
            self.mostrar_erro("Erro", "Informe o dono ou marque 'sem dono'.")
            return

        try:
            inserir_pet(dono, nome, idade, raca, sexo, self.foto_path)
        except Exception as e:
            self.mostrar_erro("Erro", f"Falha ao salvar pet: {e}")
            return

        QMessageBox.information(self, "Sucesso", "Pet cadastrado com sucesso!")
        self.accept()
