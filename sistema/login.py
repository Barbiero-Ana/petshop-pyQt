from PyQt6.QtWidgets import QMainWindow, QMessageBox, QDialog
from PyQt6 import uic, QtCore
from acesso import logar_usuario
from carregamento import TelaCarregamento
from sistema.tela_inicio import TelaInicio
from sistema.tela_adm import TelaInicioAdm
from sistema.cadastro import TelaCadastro
from trocar_senha import DialogTrocaSenha  
from data import verificar_usuario  


class TelaLogin(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('telas/pagina_login_petshop.ui', self)

        self.acessarbutton.clicked.connect(self.tentar_logar)
        self.cadastrarlabel.clicked.connect(self.ir_para_tela_cadastro)

    def tentar_logar(self):
        email = self.emailuser.text()
        senha = self.passworduser.text()

        self.tela_carregando = TelaCarregamento()
        self.tela_carregando.show()
        QtCore.QTimer.singleShot(1500, lambda: self.processar_login(email, senha))

    def processar_login(self, email, senha):
        sucesso, msg, is_admin = logar_usuario(email, senha)
        self.tela_carregando.close()

        if sucesso:
            resultado = verificar_usuario(email)
            if resultado and resultado[1]:  
                dialog = DialogTrocaSenha(email)
                if dialog.exec() != QDialog.DialogCode.Accepted:
                    QMessageBox.warning(self, "Atenção", "Você deve trocar a senha para continuar.")
                    return

            QMessageBox.information(self, "Sucesso", msg)
            if is_admin:
                self.tela_inicio_adm = TelaInicioAdm(email, login_window=self)  
                self.tela_inicio_adm.show()
            else:
                self.tela_inicio = TelaInicio(email)
                self.tela_inicio.show()
            self.close()
        else:
            QMessageBox.warning(self, "Erro", msg)

    def ir_para_tela_cadastro(self):
        self.tela_cadastro = TelaCadastro()
        self.tela_cadastro.show()
        self.close()
