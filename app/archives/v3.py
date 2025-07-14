#imports & libraries
import sys
import requests
import hashlib
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout
)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt

class PasswordChecker(QWidget):
    def __init__(self):
        #set up window
        super().__init__()
        self.setWindowTitle("Password Breach Checker")
        self.setFixedSize(300, 200)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        #label widget for instructions
        self.label = QLabel("Enter your password:")
        self.label.setFont(QFont("Arial", 10))
        layout.addWidget(self.label)

        #text entry widget for user password input
        self.entry = QLineEdit()
        self.entry.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.entry)

        #button widget to trigger password check
        self.button = QPushButton("Check Password")
        self.button.clicked.connect(self.check_password)
        layout.addWidget(self.button)

        #label widget to display password check result
        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setFont(QFont("Arial", 10))
        layout.addWidget(self.result_label)

        self.setLayout(layout)

    def check_password(self):
        #get password securely
        password = self.entry.text()
        sha1password = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
        prefix = sha1password[:5]
        suffix = sha1password[5:]

        #check password with API
        url = f"https://api.pwnedpasswords.com/range/{prefix}"
        res = requests.get(url)

        #results output
        if suffix in res.text:
            self.result_label.setText("Password has been breached!")
            self.result_label.setStyleSheet("color: red;")
        else:
            self.result_label.setText("Password is safe!")
            self.result_label.setStyleSheet("color: green;")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PasswordChecker()
    window.show()
    sys.exit(app.exec_())
