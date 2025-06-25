from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QMessageBox
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

class PetCardAdm(QWidget):
    def __init__(self, nome, idade, raca, sexo, foto, dono):
        super().__init__()
        self.nome = nome
        self.idade = idade
        self.raca = raca
        self.sexo = sexo
        self.foto = foto
        self.dono = dono

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.imagem_label = QLabel()
        if self.foto and self.foto.strip() != "":
            pixmap = QPixmap(self.foto)
            if not pixmap.isNull():
                self.imagem_label.setPixmap(pixmap.scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio))
        layout.addWidget(self.imagem_label)

        self.nome_label = QLabel(f"{self.nome}")
        self.nome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.nome_label)

        self.setStyleSheet("border: 1px solid #aaa; border-radius: 8px; padding: 8px;")

    def mousePressEvent(self, event):
        QMessageBox.information(
            self,
            f"{self.nome}",
            f"Nome: {self.nome}\nIdade: {self.idade}\nRaça: {self.raca}\nSexo: {self.sexo}\nDono: {self.dono}"
        )
