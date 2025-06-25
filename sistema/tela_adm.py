from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import QMainWindow, QDialog, QMessageBox
from PyQt6 import uic
import hashlib
from sistema.cadastro_pet_adm import DialogCadastroPet

from data import (
    buscar_pets_com_dono,
    inserir_usuario,
    inserir_funcionario,
    buscar_usuario_por_email
)

from emails import gerar_senha_aleatoria, enviar_email_senha
from sistema.petcard_adm import PetCardAdm


class DialogCadastroUsuario(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('telas/dialog/cadastro_user_adm.ui', self)
        self.lineEditTelefone.setInputMask('(00)00000-0000;_')
        self.btnConfirmar.clicked.connect(self.accept)


class DialogCadastroFuncionario(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('telas/dialog/cadastro_funcionario_adm.ui', self)
        self.lineEditTelefone.setInputMask('(00)00000-0000;_')

        # Esconder campos CRVET inicialmente com hide()
        for widget in [self.labelCRVET, self.lineEditCRVET]:
            widget.hide()

        self.labelCRVETObrigatorio.setVisible(False)  # Esconde label de aviso inicialmente

        # Conectar checkbox para mostrar/esconder campo CRVET
        self.checkBoxVeterinario.stateChanged.connect(self.toggle_crvet)
        self.btnConfirmar.clicked.connect(self.accept)


    def toggle_crvet(self, state):
        mostrar = state == QtCore.Qt.CheckState.Checked
        for widget in [self.labelCRVET, self.lineEditCRVET]:
            if mostrar:
                widget.show()
            else:
                widget.hide()
        self.adjustSize()




class TelaInicioAdm(QMainWindow):
    def __init__(self, email_usuario, login_window=None):
        super().__init__()
        uic.loadUi('telas/pagina_inicio_adm.ui', self)
        self.email_usuario = email_usuario
        self.setWindowTitle("Painel do Administrador")
        self.login_window = login_window

        # Botões do menu lateral
        self.agendabutton.clicked.connect(self.abrir_agenda)
        self.profissionalbutton.clicked.connect(self.abrir_dialog_cadastro_funcionario)
        self.localizacaobutton.clicked.connect(self.abrir_dialog_escolha_cadastro)
        self.eventosbutton.clicked.connect(self.abrir_eventos)
        self.pushButton_5.clicked.connect(self.abrir_configuracoes)
        self.pushButton.clicked.connect(self.abrir_consultas)
        self.pushButton_4.clicked.connect(self.sair)

        # Botão de busca
        self.btnBuscar.clicked.connect(self.buscar_pets)
        # Carregar pets inicialmente
        self.carregar_pets()

    def carregar_pets(self, filtro=None):
        layout = self.gridLayout
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        pets = buscar_pets_com_dono(filtro)
        colunas = 3

        for index, (id_, nome, idade, raca, sexo, foto, dono_nome) in enumerate(pets):
            card = PetCardAdm(nome, idade, raca, sexo, foto, dono_nome)
            linha = index // colunas
            coluna = index % colunas
            layout.addWidget(card, linha, coluna)

    def buscar_pets(self):
        texto = self.campoBusca.text().strip()
        self.carregar_pets(filtro=texto if texto else None)

    def abrir_dialog_escolha_cadastro(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Cadastrar")
        msg.setText("O que deseja cadastrar?")
        botao_usuario = msg.addButton("Usuário", QMessageBox.ButtonRole.AcceptRole)
        botao_pet = msg.addButton("Pet", QMessageBox.ButtonRole.AcceptRole)
        msg.addButton(QMessageBox.StandardButton.Cancel)

        msg.exec()

        botao_clicado = msg.clickedButton()
        if botao_clicado == botao_usuario:
            self.abrir_dialog_cadastro_usuario()
        elif botao_clicado == botao_pet:
            self.abrir_dialog_cadastro_pet()

    def abrir_dialog_cadastro_usuario(self):
        dialog = DialogCadastroUsuario()
        if dialog.exec() == QDialog.DialogCode.Accepted:
            nome = dialog.lineEditNome.text().strip()
            sobrenome = dialog.lineEditSobrenome.text().strip()
            telefone = dialog.lineEditTelefone.text().strip()
            genero = dialog.comboBoxGenero.currentText()
            email = dialog.lineEditEmail.text().strip()

            if not nome or not email:
                QMessageBox.warning(self, "Erro", "Nome e email são obrigatórios.")
                return

            if buscar_usuario_por_email(email):
                QMessageBox.warning(self, "Erro", "Já existe um usuário cadastrado com este email.")
                return

            senha_temp = gerar_senha_aleatoria()
            senha_hash = hashlib.sha256(senha_temp.encode()).hexdigest()

            try:
                inserir_usuario(
                    nome, sobrenome, telefone, genero, email, senha_hash,
                    tipo_usuario='paciente', is_admin=0, senha_temporaria=1
                )
                enviar_email_senha(email, senha_temp)
                QMessageBox.information(self, "Sucesso", f"Usuário cadastrado e email enviado para {email}")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao cadastrar usuário: {e}")

    def abrir_dialog_cadastro_funcionario(self):
        dialog = DialogCadastroFuncionario()
        if dialog.exec() == QDialog.DialogCode.Accepted:
            nome_completo = dialog.lineEditNomeCompleto.text().strip()
            idade = dialog.spinBoxIdade.value()
            genero = dialog.comboBoxGenero.currentText()
            email = dialog.lineEditEmail.text().strip()
            telefone = dialog.lineEditTelefone.text().strip()
            especialidade = dialog.lineEditEspecialidade.text().strip()
            is_veterinario = dialog.checkBoxVeterinario.isChecked()
            crvet = dialog.lineEditCRVET.text().strip()

            if not nome_completo or not email:
                QMessageBox.warning(self, "Erro", "Nome completo e email são obrigatórios.")
                return

            if is_veterinario and not crvet:
                print("CRVET vazio e veterinário marcado: mostrando label de aviso")
                dialog.labelCRVETObrigatorio.setVisible(True)
                dialog.lineEditCRVET.setFocus()
                return
            else:
                dialog.labelCRVETObrigatorio.setVisible(False)


            if buscar_usuario_por_email(email):
                QMessageBox.warning(self, "Erro", "Já existe um usuário cadastrado com este email.")
                return

            try:
                inserir_funcionario(nome_completo, idade, genero, email, especialidade, crvet)
                QMessageBox.information(self, "Sucesso", f"Funcionário cadastrado: {nome_completo}")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao cadastrar funcionário: {e}")

    def abrir_dialog_cadastro_pet(self):
        dialog = DialogCadastroPet()
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.carregar_pets()

    def abrir_agenda(self):
        print("Abrir tela de Agenda")

    def abrir_eventos(self):
        print("Abrir tela de Eventos")

    def abrir_configuracoes(self):
        print("Abrir tela de Configurações")

    def abrir_consultas(self):
        print("Abrir tela de Consultas")

    def sair(self):
        if self.login_window:
            self.login_window.show()
        self.close()
