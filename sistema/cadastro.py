from PyQt6.QtWidgets import QMainWindow, QMessageBox, QLabel
from PyQt6 import uic
from acesso import cadastrar_usuario
from data import criar_tabela_usuarios
from clickablelabel import ClickableLabel
from PyQt6.QtCore import Qt

class TelaCadastro(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('telas/pagina_cadastro_petshop.ui', self)
        criar_tabela_usuarios()  

        label_antigo = self.findChild(QLabel, "loginlabel")
        if label_antigo:
            self.loginlabel = ClickableLabel(label_antigo.parent())
            self.loginlabel.setText(label_antigo.text())
            self.loginlabel.setGeometry(label_antigo.geometry())
            self.loginlabel.setStyleSheet(label_antigo.styleSheet())
            self.loginlabel.setCursor(label_antigo.cursor())
            self.loginlabel.show()
            label_antigo.hide()
            self.loginlabel.clicked.connect(self.voltar_para_login)
        else:
            print("Label 'loginlabel' não encontrado na UI!")

        self.cadastrobotao.clicked.connect(self.realizar_cadastro)
        self.telefone.textChanged.connect(self.formatar_telefone)
        self._ignore_telefone_change = False  

    def realizar_cadastro(self):
        senha = self.senhacadastro.text()
        repetir = self.repetirsenha.text()
        if senha != repetir:
            QMessageBox.warning(self, "Erro", "As senhas não conferem.")
            return

        dados = {
            'primeironome': self.primeironome.text(),
            'sobrenome': self.sobrenome.text(),
            'telefone': self.telefone.text(),
            'genero': self.generoselection.currentText(),
            'email': self.emailcadastro.text(),
            'senha': senha,
            'repetirsenha': repetir
        }
        sucesso, msg = cadastrar_usuario(dados)
        if sucesso:
            QMessageBox.information(self, "Sucesso", msg)
            self.voltar_para_login()
        else:
            QMessageBox.warning(self, "Erro", msg)

    def voltar_para_login(self):
        from sistema.login import TelaLogin  # evita import circular
        self.tela_login = TelaLogin()
        self.tela_login.show()
        self.close()

    def formatar_telefone(self):
        if self._ignore_telefone_change:
            return
        texto = self.telefone.text()

        # Remove tudo que não for número
        numeros = ''.join(filter(str.isdigit, texto))

        # Limita a 11 dígitos (DDD + telefone)
        if len(numeros) > 11:
            numeros = numeros[:11]

        # Formatação dinâmica do telefone
        if len(numeros) == 0:
            texto_formatado = ""
        elif len(numeros) <= 2:
            texto_formatado = f"({numeros}"
        elif len(numeros) <= 6:
            texto_formatado = f"({numeros[:2]}){numeros[2:]}"
        elif len(numeros) <= 10:
            texto_formatado = f"({numeros[:2]}){numeros[2:6]}-{numeros[6:]}"
        else:
            # 11 dígitos: (XX)XXXXX-XXXX
            texto_formatado = f"({numeros[:2]}){numeros[2:7]}-{numeros[7:]}"

        self._ignore_telefone_change = True
        self.telefone.setText(texto_formatado)
        self._ignore_telefone_change = False
