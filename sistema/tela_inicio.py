from PyQt6.QtWidgets import QMainWindow, QLabel, QPushButton, QDialog, QVBoxLayout, QListWidget
from PyQt6 import uic
from data import (
    buscar_pets_usuario, criar_tabela_pets, buscar_nome_usuario, buscar_todos_funcionarios
)
from sistema.cadastro_pet import DialogAddPet
from sistema.listar_pets import DialogListaPets, DialogInfoPet 
from sistema.eventos_agenda import TelaEventosAgenda
from PyQt6.QtWidgets import QGridLayout
from sistema.localizacao import DialogLocalizacao

class DialogListaProfissionais(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Profissionais Cadastrados")
        self.resize(400, 300)

        layout = QVBoxLayout(self)
        self.lista_funcionarios = QListWidget()
        layout.addWidget(self.lista_funcionarios)

        btnFechar = QPushButton("Fechar")
        btnFechar.clicked.connect(self.close)
        layout.addWidget(btnFechar)

        self.carregar_profissionais()

    def carregar_profissionais(self):
        profissionais = buscar_todos_funcionarios()
        self.lista_funcionarios.clear()

        if not profissionais:
            self.lista_funcionarios.addItem("Nenhum profissional cadastrado.")
            return

        for func in profissionais:
            
            id_, nome_completo, idade, genero, email, telefone, especialidade, is_veterinario, crvet = func
            tipo = "Veterinário" if is_veterinario else "Funcionário"
            self.lista_funcionarios.addItem(f"{nome_completo} ({tipo}) - {especialidade} - {email}")

class TelaInicio(QMainWindow):
    def __init__(self, email_usuario):
        super().__init__()
        uic.loadUi('telas/pagina_inicio_usuario.ui', self)

        self.email_usuario = email_usuario
        criar_tabela_pets()

        nome_completo = buscar_nome_usuario(self.email_usuario)
        primeiro_nome = nome_completo.split()[0] if nome_completo else "Usuário"
        self.welcomeLabel.setText(f"Seja bem-vindo(a), {primeiro_nome}!")

        self.addpets.clicked.connect(self.abrir_dialog_add_pet)
        self.localizacaobutton.clicked.connect(self.abrir_localizacao)
        self.pushButton_4.clicked.connect(self.fechar_sessao)
        self.pushButton.clicked.connect(self.abrir_dialog_lista_pets)
        self.eventosbutton.clicked.connect(self.abrir_agenda)
        self.profissionalbutton.clicked.connect(self.abrir_dialog_profissionais)

        self.pets_layout = self.findChild(QGridLayout, 'gridLayout')
        self.carregar_pets()

    def abrir_localizacao(self):
        dialog = DialogLocalizacao(self)
        dialog.exec()

    def abrir_agenda(self):
        self.tela_agenda = TelaEventosAgenda(self)
        self.tela_agenda.show()

    def abrir_dialog_profissionais(self):
        dialog = DialogListaProfissionais(self)
        dialog.exec()

    def carregar_pets(self):
        layout = self.pets_layout
        if layout is None:
            print("Erro: gridLayout não encontrado na UI")
            return

        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        pets = buscar_pets_usuario(self.email_usuario)
        if not pets:
            label = QLabel("Nenhum pet cadastrado ainda.")
            layout.addWidget(label, 0, 0)
        else:
            for index, pet in enumerate(pets):
                id_pet, nome, idade, raca, foto = pet
                btn = QPushButton(nome)
                btn.clicked.connect(lambda checked, p=pet: self.mostrar_info_pet(p))
                layout.addWidget(btn, index // 3, index % 3)

    def mostrar_info_pet(self, pet):
        dialog = DialogInfoPet(pet, self)
        dialog.exec()

    def abrir_dialog_add_pet(self):
        dialog = DialogAddPet(self.email_usuario)
        if dialog.exec():
            self.carregar_pets()

    def abrir_dialog_lista_pets(self):
        dialog = DialogListaPets(self.email_usuario)
        dialog.exec()

    def fechar_sessao(self):
        from sistema.login import TelaLogin  # Evita import circular
        self.login_window = TelaLogin()
        self.login_window.show()
        self.close()
