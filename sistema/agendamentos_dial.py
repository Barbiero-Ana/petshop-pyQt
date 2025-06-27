from PyQt6.QtWidgets import QDialog, QMessageBox
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
    def __init__(self):
        super().__init__()
        uic.loadUi('telas/dialog/agendamento_consultas.ui', self)


        self.pets_dict = {f"{nome} ({raca})": pid for pid, nome, raca in buscar_todos_pets_com_id()}
        self.comboPet.addItems(self.pets_dict.keys())

        self.usuarios_dict = {f"{pnome} {snome} ({email})": email for _, pnome, snome, email in buscar_todos_usuarios()}
        self.comboDono.addItems(self.usuarios_dict.keys())

        self.vets_dict = {
            f"{nome} - {especialidade} (CRMV: {crvet})": vid
            for vid, nome, _, _, _, crvet, especialidade in buscar_funcionarios_veterinarios(completo=True)
        }
        self.comboVeterinario.addItems(self.vets_dict.keys())

        self.dateEdit.setDate(QDate.currentDate())
        self.timeEdit.setTime(QTime.currentTime())

        self.btnConfirmar.clicked.connect(self.confirmar)

    def confirmar(self):
        pet_nome_completo = self.comboPet.currentText()
        pet_id = self.pets_dict.get(pet_nome_completo)

        dono_email = self.usuarios_dict.get(self.comboDono.currentText())

        vet_str = self.comboVeterinario.currentText()
        vet_id = self.vets_dict.get(vet_str)

        data_consulta = self.dateEdit.date().toString("yyyy-MM-dd")
        hora_consulta = self.timeEdit.time().toString("HH:mm")

        nome_vet = vet_str.split(" - ")[0]

        pet_nome = pet_nome_completo.split(" (")[0]

        try:
            inserir_consulta(pet_id, dono_email, vet_id, data_consulta, hora_consulta)

            # Envia email de confirmação
            enviar_email_confirmacao_consulta(
                destinatario=dono_email,
                nome_pet=pet_nome,
                data=data_consulta,
                hora=hora_consulta,
                nome_vet=nome_vet
            )

            QMessageBox.information(self, "Sucesso", "Consulta agendada e email enviado.")
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao agendar consulta: {e}")
