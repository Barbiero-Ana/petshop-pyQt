import sys
from PyQt6.QtWidgets import QApplication
from sistema.login import TelaLogin
from data import criar_tabela_usuarios, criar_tabela_pets, criar_usuario_admin_padrao

if __name__ == '__main__':

    criar_tabela_usuarios()
    criar_tabela_pets()
    criar_usuario_admin_padrao()

    app = QApplication(sys.argv)  
    janela = TelaLogin()
    janela.show()
    sys.exit(app.exec())           