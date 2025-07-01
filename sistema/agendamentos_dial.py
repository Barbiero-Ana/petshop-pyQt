from PyQt6.QtWidgets import (
    QDialog, QMessageBox, QComboBox, QTimeEdit, QPushButton, QLabel
)
from PyQt6 import uic
from PyQt6.QtCore import QDate, QTime

from data import (
    buscar_todos_pets_com_id,
    buscar_todos_usuarios,
    buscar_funcionarios_veterinarios,
    inserir_consulta
)
from emails import enviar_email_confirmacao_consulta


class DialogAgendarConsulta(QDialog):
    def __init__(self, data_selecionada: QDate):
        super().__init__()
        uic.loadUi('telas/agendar_consultas.ui', self)

        # Widgets
        self.comboPet = self.findChild(QComboBox, 'comboBox')
        self.comboDono = self.findChild(QComboBox, 'comboBox_5')
        self.comboVeterinario = self.findChild(QComboBox, 'comboBox_2')
        self.comboCategoria = self.findChild(QComboBox, 'comboBox_3')
        self.comboProcedimentos = self.findChild(QComboBox, 'comboBox_4')
        self.timeEdit = self.findChild(QTimeEdit, 'timeEdit')
        self.btnConfirmar = self.findChild(QPushButton, 'pushButton')
        self.btnCancelar = self.findChild(QPushButton, 'pushButton_2')
        self.lblDataConsulta = self.findChild(QLabel, 'valorDataConsulta')

        # Dados
        self.pets_dict = {
            f"{nome} ({raca})": pid
            for pid, nome, raca in buscar_todos_pets_com_id()
        }
        self.comboPet.addItems(self.pets_dict.keys())

        self.usuarios_dict = {
            f"{pnome} {snome} ({email})": email
            for _, pnome, snome, email in buscar_todos_usuarios()
        }
        self.comboDono.addItems(self.usuarios_dict.keys())

        self.vets_dict = {
            f"{nome} - {especialidade} (CRMV: {crvet})": vid
            for vid, nome, _, _, _, crvet, especialidade in buscar_funcionarios_veterinarios(completo=True)
        }
        self.comboVeterinario.addItems(self.vets_dict.keys())

        # Data e hora
        self.data_selecionada = data_selecionada
        if self.lblDataConsulta:
            self.lblDataConsulta.setText(self.data_selecionada.toString("dd/MM/yyyy"))
        self.timeEdit.setTime(QTime.currentTime())

        self.procedimentos_por_categoria = {
        "Exames": [
            "Exame de sangue completo",
            "Raio-X abdominal",
            "Raio-X torácico",
            "Ultrassonografia abdominal",
            "Ultrassonografia gestacional",
            "Eletrocardiograma",
            "Exame de urina",
            "Exame de fezes"
        ],
        "Vacinas": [
            "Vacina V10 (cães)",
            "Vacina antirrábica",
            "Vacina múltipla (gatos)",
            "Vacina contra leishmaniose",
            "Vacina contra giárdia"
        ],
        "Consulta Geral": [
            "Avaliação clínica completa",
            "Consulta de retorno",
            "Consulta pré-cirúrgica",
            "Consulta pós-operatória",
            "Consulta nutricional",
            "Consulta de filhotes",
            "Orientações comportamentais"
        ],
        "Cirurgias": [
            "Castração (macho/fêmea)",
            "Retirada de tumor",
            "Correção de hérnia",
            "Cirurgia ortopédica",
            "Extração dentária",
            "Cesárea",
            "Amputação terapêutica"
        ],
        "Odontologia": [
            "Limpeza dental (profilaxia)",
            "Extração dentária",
            "Tratamento de canal",
            "Raspagem de tártaro"
        ],
        "Dermatologia": [
            "Avaliação de lesões de pele",
            "Exame de fungos",
            "Tratamento de alergias",
            "Banho terapêutico"
        ],
        "Oftalmologia": [
            "Exame oftalmológico completo",
            "Teste do olho seco",
            "Retirada de corpo estranho",
            "Cirurgia de pálpebra"
        ],
        "Ortopedia": [
            "Avaliação ortopédica",
            "Raio-X ortopédico",
            "Imobilização de membro",
            "Cirurgia de fratura"
        ]
    }

        self.comboCategoria.addItems(self.procedimentos_por_categoria.keys())
        self.comboCategoria.currentIndexChanged.connect(self.atualizar_procedimentos)
        self.atualizar_procedimentos()  
        self.btnConfirmar.clicked.connect(self.confirmar)
        self.btnCancelar.clicked.connect(self.reject)

    def atualizar_procedimentos(self):
        categoria = self.comboCategoria.currentText()
        procedimentos = self.procedimentos_por_categoria.get(categoria, [])
        self.comboProcedimentos.clear()
        self.comboProcedimentos.addItems(procedimentos)

    def confirmar(self):
        pet_nome_completo = self.comboPet.currentText()
        pet_id = self.pets_dict.get(pet_nome_completo)
        pet_nome = pet_nome_completo.split(" (")[0]

        dono_email = self.usuarios_dict.get(self.comboDono.currentText())

        vet_str = self.comboVeterinario.currentText()
        vet_id = self.vets_dict.get(vet_str)
        nome_vet = vet_str.split(" - ")[0]

        data_consulta = self.data_selecionada.toString("yyyy-MM-dd")
        hora_consulta = self.timeEdit.time().toString("HH:mm")

        try:
            inserir_consulta(pet_id, dono_email, vet_id, data_consulta, hora_consulta)

            enviar_email_confirmacao_consulta(
                destinatario=dono_email,
                nome_pet=pet_nome,
                data=data_consulta,
                hora=hora_consulta,
                nome_vet=nome_vet
            )

            QMessageBox.information(self, "Sucesso", "Consulta agendada com sucesso e email enviado.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao agendar consulta:\n{str(e)}")
