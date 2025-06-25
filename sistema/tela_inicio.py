from PyQt6.QtWidgets import (
    QMainWindow, QLabel, QScrollArea, QWidget, QHBoxLayout
)
from PyQt6 import uic
from data import buscar_pets_usuario, criar_tabela_pets, buscar_nome_usuario
from sistema.cadastro_pet import DialogAddPet, PetCard  # Vamos usar seu PetCard real

class TelaInicio(QMainWindow):
    def __init__(self, email_usuario):
        super().__init__()
        uic.loadUi('telas/pagina_inicio_usuario.ui', self)

        self.email_usuario = email_usuario
        criar_tabela_pets()

        # Saudações personalizadas
        nome_completo = buscar_nome_usuario(self.email_usuario)
        primeiro_nome = nome_completo.split()[0]
        self.welcomeLabel.setText(f"Seja bem-vindo(a), {primeiro_nome}!")

        # Botão de adicionar pet
        self.addpets.clicked.connect(self.abrir_dialog_add_pet)

        # Botão de sair
        self.pushButton_4.clicked.connect(self.fechar_sessao)

        # Scroll area e widget de conteúdo
        self.scrollArea = self.findChild(QScrollArea, 'scrollArea')
        self.scroll_content = self.scrollArea.findChild(QWidget, 'scrollAreaWidgetContents')
        self.widget_conteudo = self.scroll_content.findChild(QWidget, 'widget')

        # Cria e associa um layout horizontal explicitamente no widget_conteudo
        self.pets_layout = QHBoxLayout()
        self.widget_conteudo.setLayout(self.pets_layout)

        self.carregar_pets()

    def carregar_pets(self):
        # Limpa o layout
        while self.pets_layout.count():
            item = self.pets_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        pets = buscar_pets_usuario(self.email_usuario)
        if not pets:
            label = QLabel("Nenhum pet cadastrado ainda.")
            self.pets_layout.addWidget(label)
        else:
            for pet in pets:
                id_pet, nome, idade, raca, foto = pet
                pet_card = PetCard(nome, idade, raca, foto)
                self.pets_layout.addWidget(pet_card)

        self.widget_conteudo.adjustSize()
        self.scrollArea.widget().adjustSize()
        self.scrollArea.update()

    def abrir_dialog_add_pet(self):
        dialog = DialogAddPet(self.email_usuario)
        if dialog.exec():
            self.carregar_pets()

    def fechar_sessao(self):
        from sistema.login import TelaLogin  # Evita import circular
        self.login_window = TelaLogin()
        self.login_window.show()
        self.close()
