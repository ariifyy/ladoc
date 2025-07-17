# email_breachchecker.py

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt

class EmailBreachChecker(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout()
        label = QLabel("Email Breach Checker Page")
        label.setAlignment(Qt.AlignCenter)

        layout.addWidget(label)
        self.setLayout(layout)


###use xposedornot api for this
###xposedornot api has a limit of 10 requests per hour per ip

