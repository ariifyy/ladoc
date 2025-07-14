import sys
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class TitlePage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Welcome")
        self.setGeometry(200, 200, 400, 200)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        layout.addStretch(1)

        title_label = QLabel("Password Breach Checker")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 20, QFont.Bold))
        layout.addWidget(title_label)

        #Buttons horizontally aligned
        button_row = QHBoxLayout()

        # Add stretch to left
        button_row.addStretch(1)

        #Check password breack
        start_button = QPushButton("Check Password")
        start_button.setFont(QFont("Arial", 14))
        start_button.setFixedSize(300, 40)
        start_button.clicked.connect(self.open_main_checker)
        button_row.addWidget(start_button)

        # Spacing between buttons
        button_row.addSpacing(20)

        #Change password
        change_password = QPushButton("Change Password")
        change_password.setFont(QFont("Arial", 14))
        change_password.setFixedSize(300, 40)
        change_password.clicked.connect(self.open_change_password)
        button_row.addWidget(change_password)

        # Add stretch to right
        button_row.addStretch(1)

        layout.addLayout(button_row)

        #Vertical centering
        layout.addStretch(1)

        self.setLayout(layout)

    def open_main_checker(self):
        subprocess.Popen([sys.executable, "v4.py"])
        self.close()

    def open_change_password(self):
        subprocess.Popen([sys.executable, "change_password.py"])
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TitlePage()
    window.show()
    sys.exit(app.exec_())
