from PyQt6 import QtCore, QtWidgets, uic
from PyQt6.QtWidgets import QMainWindow, QDialog, QMessageBox
import hashlib
import re
from sistema.cadastro_pet_adm import DialogCadastroPet
from data import (
    buscar_pets_com_dono,
    inserir_usuario,
    inserir_funcionario,
    buscar_usuario_por_email
)
from emails import gerar_senha_aleatoria, enviar_email_senha
from sistema.petcard_adm import PetCardAdm
from sistema.eventos_agenda import TelaEventosAgenda


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

        self.labelCRVET.setVisible(True)
        self.lineEditCRVET.setVisible(True)

        # Começa desabilitado e readonly
        self.lineEditCRVET.setEnabled(False)
        self.lineEditCRVET.setReadOnly(True)

        self.labelCRVETObrigatorio.setVisible(False)

        # Conecta checkbox para habilitar/desabilitar CRVET
        self.checkBoxVeterinario.stateChanged.connect(self.toggle_crvet)
        self.lineEditCRVET.textChanged.connect(self.validar_crvet)

    def toggle_crvet(self, state):
        print(f"Toggle state: {state}")
        if state == 2:  # QtCore.Qt.CheckState.Checked é 2
            self.lineEditCRVET.setEnabled(True)
            self.lineEditCRVET.setReadOnly(False)
            self.lineEditCRVET.setFocus()
            print(f"CRVET enabled={self.lineEditCRVET.isEnabled()}, readonly={self.lineEditCRVET.isReadOnly()}")
        else:
            self.lineEditCRVET.setEnabled(False)
            self.lineEditCRVET.setReadOnly(True)
            self.lineEditCRVET.clear()
            self.labelCRVETObrigatorio.setVisible(False)
            self.set_lineedit_border(self.lineEditCRVET, valid=True)
            print(f"CRVET disabled={self.lineEditCRVET.isEnabled()}, readonly={self.lineEditCRVET.isReadOnly()}")





    def validar_crvet(self, texto):
        if not self.lineEditCRVET.isEnabled():
            return
        padrao = r'^[A-Za-z0-9]{5,}$'  
        if re.fullmatch(padrao, texto):
            self.labelCRVETObrigatorio.setVisible(False)
            self.set_lineedit_border(self.lineEditCRVET, valid=True)
        else:
            self.labelCRVETObrigatorio.setVisible(True)
            self.set_lineedit_border(self.lineEditCRVET, valid=False)

    def set_lineedit_border(self, lineedit, valid=True):
        if valid:
            lineedit.setStyleSheet("border: 1px solid green;")
        else:
            lineedit.setStyleSheet("border: 1px solid red;")


class TelaInicioAdm(QMainWindow):
    def __init__(self, email_usuario, login_window=None):
        super().__init__()
        uic.loadUi('telas/pagina_inicio_adm.ui', self)
        self.email_usuario = email_usuario
        self.setWindowTitle("Painel do Administrador")
        self.login_window = login_window

        self.agendabutton.clicked.connect(self.abrir_agenda)
        self.profissionalbutton.clicked.connect(self.abrir_dialog_cadastro_funcionario)
        self.localizacaobutton.clicked.connect(self.abrir_dialog_escolha_cadastro)
        self.pushButton_5.clicked.connect(self.abrir_configuracoes)
        self.pushButton.clicked.connect(self.abrir_consultas)
        self.pushButton_4.clicked.connect(self.sair)

        self.btnBuscar.clicked.connect(self.buscar_pets)
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
        msg.setWindowTitle("Gerenciar")
        msg.setText("O que deseja fazer?")
        botao_cadastrar_usuario = msg.addButton("Cadastrar Usuário", QMessageBox.ButtonRole.ActionRole)
        botao_cadastrar_pet = msg.addButton("Cadastrar Pet", QMessageBox.ButtonRole.ActionRole)
        botao_excluir_usuario = msg.addButton("Excluir Usuário", QMessageBox.ButtonRole.ActionRole)
        botao_excluir_pet = msg.addButton("Excluir Pet", QMessageBox.ButtonRole.ActionRole)
        msg.addButton(QMessageBox.StandardButton.Cancel)

        msg.exec()

        botao = msg.clickedButton()
        if botao == botao_cadastrar_usuario:
            self.abrir_dialog_cadastro_usuario()
        elif botao == botao_cadastrar_pet:
            self.abrir_dialog_cadastro_pet()
        elif botao == botao_excluir_usuario:
            self.excluir_usuario()
        elif botao == botao_excluir_pet:
            self.excluir_pet()

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

            if is_veterinario:
                if not crvet:
                    dialog.labelCRVETObrigatorio.setVisible(True)
                    dialog.lineEditCRVET.setFocus()
                    return
                if not re.fullmatch(r'[A-Za-z0-9]{5,}', crvet):
                    QMessageBox.warning(
                        self,
                        "Erro",
                        "CRMVET inválido. Deve conter ao menos 5 caracteres alfanuméricos."
                    )
                    dialog.lineEditCRVET.setFocus()
                    return
                dialog.labelCRVETObrigatorio.setVisible(False)
            else:
                crvet = ""

            if buscar_usuario_por_email(email):
                QMessageBox.warning(self, "Erro", "Já existe um usuário cadastrado com este email.")
                return

            try:
                inserir_funcionario(
                    nome_completo, idade, genero, email, telefone,
                    especialidade, is_veterinario, crvet
                )
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
        self.tela_agenda = TelaEventosAgenda(self)
        self.tela_agenda.show()

    def sair(self):
        if self.login_window:
            self.login_window.show()
        self.close()

    def excluir_usuario(self):
        from data import buscar_todos_usuarios, excluir_usuario_por_id

        usuarios = buscar_todos_usuarios()
        if not usuarios:
            QMessageBox.information(self, "Aviso", "Nenhum usuário cadastrado.")
            return

        lista_exibicao = [f"{usuario_id} - {primeiro} {sobrenome} ({email})"
                          for usuario_id, primeiro, sobrenome, email in usuarios]

        item_selecionado, ok = QtWidgets.QInputDialog.getItem(
            self, "Excluir Usuário", "Selecione o usuário para excluir:",
            lista_exibicao, 0, False
        )

        if ok and item_selecionado:
            usuario_id = int(item_selecionado.split(" - ")[0])
            confirm = QMessageBox.question(
                self, "Confirmar Exclusão",
                f"Deseja realmente excluir o usuário de ID {usuario_id}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if confirm == QMessageBox.StandardButton.Yes:
                try:
                    excluir_usuario_por_id(usuario_id)
                    QMessageBox.information(self, "Sucesso", "Usuário excluído com sucesso.")
                except Exception as e:
                    QMessageBox.critical(self, "Erro", f"Erro ao excluir usuário: {e}")

    def excluir_pet(self):
        from data import buscar_todos_pets_com_id, excluir_pet_por_id

        pets = buscar_todos_pets_com_id()
        if not pets:
            QMessageBox.information(self, "Aviso", "Nenhum pet cadastrado.")
            return

        lista_exibicao = [f"{pet_id} - {nome} ({raca})" for pet_id, nome, raca in pets]

        item_selecionado, ok = QtWidgets.QInputDialog.getItem(
            self, "Excluir Pet", "Selecione o pet para excluir:",
            lista_exibicao, 0, False
        )

        if ok and item_selecionado:
            pet_id = int(item_selecionado.split(" - ")[0])
            confirm = QMessageBox.question(
                self, "Confirmar Exclusão",
                f"Deseja realmente excluir o pet de ID {pet_id}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if confirm == QMessageBox.StandardButton.Yes:
                try:
                    excluir_pet_por_id(pet_id)
                    QMessageBox.information(self, "Sucesso", "Pet excluído com sucesso.")
                    self.carregar_pets()
                except Exception as e:
                    QMessageBox.critical(self, "Erro", f"Erro ao excluir pet: {e}")
