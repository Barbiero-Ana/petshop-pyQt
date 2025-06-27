from PyQt6.QtWidgets import QDialog, QVBoxLayout
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl

class DialogLocalizacao(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Localização - Cyber Edux")
        self.resize(800, 600)

        layout = QVBoxLayout(self)
        self.webview = QWebEngineView()
        layout.addWidget(self.webview)

        url_google = (
            "https://www.google.com/maps/place/Cyber+Edux+Educação+e+Treinamentos+Ltda./"
            "@-15.5935651,-56.1042916,17z/data=!3m1!4b1!4m6!3m5!1s0x939db13cb0ba0959:0xedfa42932c6e197f!"
            "8m2!3d-15.5935651!4d-56.1017113!16s%2Fg%2F11v59c3b17?entry=ttu&g_ep=EgoyMDI1MDYyMy4yIKXMDSoASAFQAw%3D%3D"
        )

        self.webview.load(QUrl(url_google))
