from PyQt6.QtWidgets import QMainWindow, QMessageBox, QDialog
from PyQt6 import uic
from PyQt6.QtCore import QStringListModel
from data import buscar_consultas, excluir_consulta_por_id
from sistema.agendamentos_dial import DialogAgendarConsulta
from PyQt6.QtCore import QDate 

class TelaEventosAgenda(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('telas/pagina_eventos_agenda.ui', self)

        self.voltar.clicked.connect(self.close)
        self.addevento.clicked.connect(self.adicionar_evento)
        self.agendarconsulta.clicked.connect(self.abrir_dialog_consulta)
        self.excluirevento.clicked.connect(self.excluir_evento)
        self.att.clicked.connect(self.atualizar_eventos)

        self.eventos = []
        self.consultas = []

        self.modelo_eventos = QStringListModel()
        self.listView.setModel(self.modelo_eventos)
        self.atualizar_eventos()

    def adicionar_evento(self):
        data = self.calendarWidget.selectedDate().toString("dd/MM/yyyy")
        texto = f"Evento em {data}"
        self.eventos.append(texto)
        self.atualizar_eventos()
        QMessageBox.information(self, "Evento Adicionado", f"{texto}")

    def abrir_dialog_consulta(self):
        data = self.calendarWidget.selectedDate()  
        dialog = DialogAgendarConsulta(data)       
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.atualizar_eventos()


    def excluir_evento(self):
        index = self.listView.currentIndex().row()
        total = len(self.eventos) + len(self.consultas)
        if index < 0 or index >= total:
            QMessageBox.warning(self, "Erro", "Selecione algo para excluir.")
            return

        if index < len(self.eventos):
            evento = self.eventos.pop(index)
            QMessageBox.information(self, "Removido", f"{evento}")
        else:
            cidx = index - len(self.eventos)
            consulta = self.consultas[cidx]
            excluir_consulta_por_id(consulta[0])
            self.consultas.pop(cidx)
            QMessageBox.information(self, "Removido", "Consulta removida.")

        self.atualizar_eventos()

    def atualizar_eventos(self):
        self.consultas = buscar_consultas()
        lista = self.eventos.copy()

        for c in self.consultas:
            texto = f"{c[10]} às {c[11]} - {c[1]} com {c[6]}"
            lista.append(texto)

        self.modelo_eventos.setStringList(lista)
