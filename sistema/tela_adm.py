from PyQt6 import QtCore, QtWidgets, uic
from PyQt6.QtWidgets import (
    QMainWindow, QDialog, QMessageBox, QListWidget, QVBoxLayout, QPushButton, QHBoxLayout
)
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

        self.lineEditCRVET.setEnabled(False)
        self.lineEditCRVET.setReadOnly(True)

        self.labelCRVETObrigatorio.setVisible(False)

        # conecta o checkbox
        self.checkBoxVeterinario.stateChanged.connect(self.toggle_crvet)
        self.lineEditCRVET.textChanged.connect(self.validar_crvet)

        self.btnConfirmar.clicked.connect(self.confirmar_cadastro)

    def toggle_crvet(self, state):
        # state: 2 = Checked, 0 = Unchecked
        if state == 2:
            self.lineEditCRVET.setEnabled(True)
            self.lineEditCRVET.setReadOnly(False)
            self.lineEditCRVET.setFocus()
        else:
            self.lineEditCRVET.setEnabled(False)
            self.lineEditCRVET.setReadOnly(True)
            self.lineEditCRVET.clear()
            self.labelCRVETObrigatorio.setVisible(False)
            self.set_lineedit_border(self.lineEditCRVET, valid=True)

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

    def confirmar_cadastro(self):
        nome_completo = self.lineEditNomeCompleto.text().strip()
        email = self.lineEditEmail.text().strip()
        is_veterinario = self.checkBoxVeterinario.isChecked()
        crvet = self.lineEditCRVET.text().strip()

        if not nome_completo:
            QMessageBox.warning(self, "Erro", "Nome completo é obrigatório.")
            return
        if not email:
            QMessageBox.warning(self, "Erro", "Email é obrigatório.")
            return

        # Validação CRVET 
        if is_veterinario:
            if not crvet:
                self.labelCRVETObrigatorio.setVisible(True)
                self.lineEditCRVET.setFocus()
                return
            if not re.fullmatch(r'[A-Za-z0-9]{5,}', crvet):
                QMessageBox.warning(
                    self,
                    "Erro",
                    "CRVET inválido. Deve conter ao menos 5 caracteres alfanuméricos."
                )
                self.lineEditCRVET.setFocus()
                return
            self.labelCRVETObrigatorio.setVisible(False)

        # fecha se tudo ok
        self.accept()


class DialogVisualizarFuncionarios(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Funcionários Cadastrados")
        self.resize(600, 400)

        self.layout = QVBoxLayout(self)

        self.lista_funcionarios = QListWidget()
        self.layout.addWidget(self.lista_funcionarios)

        btn_layout = QHBoxLayout()
        self.btn_editar = QPushButton("Editar")
        self.btn_excluir = QPushButton("Excluir")
        self.btn_fechar = QPushButton("Fechar")
        btn_layout.addWidget(self.btn_editar)
        btn_layout.addWidget(self.btn_excluir)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_fechar)
        self.layout.addLayout(btn_layout)

        self.funcionarios = []

        self.carregar_funcionarios()

        self.btn_editar.clicked.connect(self.editar_funcionario)
        self.btn_excluir.clicked.connect(self.excluir_funcionario)
        self.btn_fechar.clicked.connect(self.close)

    def carregar_funcionarios(self):
        from data import buscar_todos_funcionarios

        self.funcionarios = buscar_todos_funcionarios()
        self.lista_funcionarios.clear()

        if not self.funcionarios:
            self.lista_funcionarios.addItem("Nenhum funcionário cadastrado.")
            self.btn_editar.setEnabled(False)
            self.btn_excluir.setEnabled(False)
            return

        self.btn_editar.setEnabled(True)
        self.btn_excluir.setEnabled(True)

        for func in self.funcionarios:
            id_, nome_completo, idade, genero, email, telefone, especialidade, is_veterinario, crvet = func
            vet_str = "Veterinário" if is_veterinario else "Funcionário"
            self.lista_funcionarios.addItem(f"{id_} - {nome_completo} ({vet_str}) - {email}")

    def get_funcionario_selecionado(self):
        idx = self.lista_funcionarios.currentRow()
        if idx < 0 or idx >= len(self.funcionarios):
            return None
        return self.funcionarios[idx]

    def editar_funcionario(self):
        func = self.get_funcionario_selecionado()
        if not func:
            QMessageBox.warning(self, "Aviso", "Selecione um funcionário para editar.")
            return

        id_, nome_completo, idade, genero, email, telefone, especialidade, is_veterinario, crvet = func

        dialog = DialogCadastroFuncionario()
        dialog.setWindowTitle(f"Editar Funcionário: {nome_completo}")

        dialog.lineEditNomeCompleto.setText(nome_completo)
        dialog.spinBoxIdade.setValue(idade)
        index_genero = dialog.comboBoxGenero.findText(genero)
        if index_genero >= 0:
            dialog.comboBoxGenero.setCurrentIndex(index_genero)
        dialog.lineEditEmail.setText(email)
        dialog.lineEditTelefone.setText(telefone)
        dialog.lineEditEspecialidade.setText(especialidade)
        dialog.checkBoxVeterinario.setChecked(bool(is_veterinario))

        if is_veterinario:
            dialog.lineEditCRVET.setEnabled(True)
            dialog.lineEditCRVET.setReadOnly(False)
            dialog.lineEditCRVET.setText(crvet)
            dialog.labelCRVETObrigatorio.setVisible(False)
        else:
            dialog.lineEditCRVET.setEnabled(False)
            dialog.lineEditCRVET.setReadOnly(True)
            dialog.lineEditCRVET.clear()
            dialog.labelCRVETObrigatorio.setVisible(False)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            novo_nome = dialog.lineEditNomeCompleto.text().strip()
            nova_idade = dialog.spinBoxIdade.value()
            novo_genero = dialog.comboBoxGenero.currentText()
            novo_email = dialog.lineEditEmail.text().strip()
            novo_telefone = dialog.lineEditTelefone.text().strip()
            nova_especialidade = dialog.lineEditEspecialidade.text().strip()
            novo_is_veterinario = dialog.checkBoxVeterinario.isChecked()
            novo_crvet = dialog.lineEditCRVET.text().strip()

            if not novo_nome or not novo_email:
                QMessageBox.warning(self, "Erro", "Nome completo e email são obrigatórios.")
                return

            if novo_is_veterinario:
                if not novo_crvet:
                    dialog.labelCRVETObrigatorio.setVisible(True)
                    dialog.lineEditCRVET.setFocus()
                    return
                if not re.fullmatch(r'[A-Za-z0-9]{5,}', novo_crvet):
                    QMessageBox.warning(
                        self,
                        "Erro",
                        "CRVET inválido. Deve conter ao menos 5 caracteres alfanuméricos."
                    )
                    dialog.lineEditCRVET.setFocus()
                    return
                dialog.labelCRVETObrigatorio.setVisible(False)
            else:
                novo_crvet = ""

            try:
                from data import atualizar_funcionario
                atualizar_funcionario(
                    id_, novo_nome, nova_idade, novo_genero, novo_email,
                    novo_telefone, nova_especialidade, novo_is_veterinario, novo_crvet
                )
                QMessageBox.information(self, "Sucesso", "Funcionário atualizado com sucesso.")
                self.carregar_funcionarios()
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao atualizar funcionário: {e}")

    def excluir_funcionario(self):
        func = self.get_funcionario_selecionado()
        if not func:
            QMessageBox.warning(self, "Aviso", "Selecione um funcionário para excluir.")
            return

        id_, nome_completo, *_ = func

        confirm = QMessageBox.question(
            self,
            "Confirmar Exclusão",
            f"Deseja realmente excluir o funcionário '{nome_completo}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            try:
                from data import excluir_funcionario_por_id
                excluir_funcionario_por_id(id_)
                QMessageBox.information(self, "Sucesso", "Funcionário excluído com sucesso.")
                self.carregar_funcionarios()
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao excluir funcionário: {e}")


class TelaInicioAdm(QMainWindow):
    def __init__(self, email_usuario, login_window=None):
        super().__init__()
        uic.loadUi('telas/pagina_inicio_adm.ui', self)
        self.email_usuario = email_usuario
        self.setWindowTitle("Painel do Administrador")
        self.login_window = login_window

        self.agendabutton.clicked.connect(self.abrir_agenda)
        self.profissionalbutton.clicked.connect(self.abrir_dialog_funcionario_opcoes)
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
            senha_temp = gerar_senha_aleatoria()
            print(f"Senha temporária gerada para {email}: {senha_temp}")  # DEBUG
            senha_hash = hashlib.sha256(senha_temp.encode()).hexdigest()

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

    def abrir_dialog_funcionario_opcoes(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Funcionários")
        msg.setText("O que deseja fazer?")
        botao_cadastrar = msg.addButton("Cadastrar Funcionário", QMessageBox.ButtonRole.ActionRole)
        botao_visualizar = msg.addButton("Visualizar Funcionários", QMessageBox.ButtonRole.ActionRole)
        msg.addButton(QMessageBox.StandardButton.Cancel)

        msg.exec()

        botao = msg.clickedButton()
        if botao == botao_cadastrar:
            self.abrir_dialog_cadastro_funcionario()
        elif botao == botao_visualizar:
            self.abrir_dialog_visualizar_funcionarios()

    def abrir_dialog_visualizar_funcionarios(self):
        dialog = DialogVisualizarFuncionarios(self)
        dialog.exec()

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
