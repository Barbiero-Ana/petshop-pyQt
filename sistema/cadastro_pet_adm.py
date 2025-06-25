from PyQt6.QtWidgets import QDialog, QMessageBox, QFileDialog, QListWidget, QListWidgetItem
from PyQt6.QtGui import QPixmap
from PyQt6 import uic
from data import inserir_pet, buscar_usuarios_email_nome
from PyQt6.QtCore import Qt

class DialogCadastroPet(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("telas/dialog/cadastro_pet_adm.ui", self)

        self.foto_path = None

        # Botões
        self.btnSelecionarFoto.clicked.connect(self.selecionar_foto)
        self.checkBoxSemDono.stateChanged.connect(self.toggle_dono_input)
        self.lineEditDono.textChanged.connect(self.atualizar_lista_usuarios)
        self.btnConfirmar.clicked.connect(self.confirmar)
        self.btnCancelar.clicked.connect(self.reject)

        # Lista para mostrar usuários (dono)
        self.listWidgetUsuarios.itemClicked.connect(self.selecionar_usuario_lista)

        self.toggle_dono_input()

    def toggle_dono_input(self):
        sem_dono = self.checkBoxSemDono.isChecked()
        self.lineEditDono.setEnabled(not sem_dono)
        self.listWidgetUsuarios.setEnabled(not sem_dono)
        if sem_dono:
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

    def selecionar_foto(self):
        caminho, _ = QFileDialog.getOpenFileName(self, "Selecionar foto do pet", filter="Imagens (*.png *.jpg *.jpeg *.bmp *.gif)")
        if caminho:
            pixmap = QPixmap(caminho)
            if pixmap.isNull():
                QMessageBox.warning(self, "Erro", "Arquivo inválido.")
                return
            self.labelFoto.setPixmap(pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio))
            self.foto_path = caminho

    def confirmar(self):
        nome = self.lineEditNomePet.text().strip()
        raca = self.lineEditRaca.text().strip()
        sexo = self.comboBoxSexo.currentText()
        sem_dono = self.checkBoxSemDono.isChecked()
        dono_email = self.lineEditDono.text().strip() if not sem_dono else None

        if not nome:
            QMessageBox.warning(self, "Erro", "Informe o nome do pet.")
            return
        if not raca:
            QMessageBox.warning(self, "Erro", "Informe a raça do pet.")
            return
        if sexo not in ("Masculino", "Feminino"):
            QMessageBox.warning(self, "Erro", "Informe o sexo do pet.")
            return
        if not sem_dono and not dono_email:
            QMessageBox.warning(self, "Erro", "Informe o dono ou marque como sem dono.")
            return

        try:
            inserir_pet(dono_email, nome, "N/D", raca, sexo, self.foto_path)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao salvar pet: {e}")
            return

        QMessageBox.information(self, "Sucesso", "Pet cadastrado com sucesso!")
        self.accept()
