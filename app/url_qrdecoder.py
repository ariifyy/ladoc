# url_qrdecoder.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

class QRDecoderPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("QR Decoder Tool"))
        # Add your UI widgets here
        self.setLayout(layout)
