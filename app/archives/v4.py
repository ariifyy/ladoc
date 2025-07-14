import sys
import subprocess
import re
import secrets
import string
import requests
import hashlib
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QSizePolicy
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class PasswordCheckerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Password Strength & Breach Checker")
        self.setMinimumSize(400, 300)
        self.setup_ui()

    def setup_ui(self):
        self.layout = QVBoxLayout()

        #Back Button with arrow
        back_button = QPushButton("⬅ Home")
        back_button.setFont(QFont("Arial", 12))
        back_button.setFixedWidth(120)
        back_button.clicked.connect(self.go_back)
        self.layout.addWidget(back_button, alignment=Qt.AlignLeft)

        # Instruction Label
        self.label = QLabel("Enter your password:")
        self.label.setFont(QFont("Arial", 14))
        self.layout.addWidget(self.label)

        # Password Input + Show Toggle
        password_layout = QHBoxLayout()
        self.entry = QLineEdit()
        self.entry.setEchoMode(QLineEdit.Password)
        self.entry.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.show_button = QPushButton("Show")
        self.show_button.setCheckable(True)
        self.show_button.toggled.connect(self.toggle_password)
        password_layout.addWidget(self.entry)
        password_layout.addWidget(self.show_button)

        self.layout.addLayout(password_layout)

        # Password Strength Label
        self.strength_label = QLabel("")
        self.strength_label.setFont(QFont("Arial", 10))
        self.strength_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.strength_label)

        # Buttons: Check Strength, Suggest Password, Check Breach
        button_layout = QHBoxLayout()
        
        self.check_breach_button = QPushButton("Check Breach with API")
        self.check_breach_button.clicked.connect(self.check_password_breach)
        button_layout.addWidget(self.check_breach_button)


        # Breach Result Label
        self.breach_result_label = QLabel("")
        self.breach_result_label.setAlignment(Qt.AlignCenter)
        self.breach_result_label.setFont(QFont("Arial", 10))
        self.layout.addWidget(self.breach_result_label)
        self.layout.addLayout(button_layout)

        self.setLayout(self.layout)

    def go_back(self):
        subprocess.Popen([sys.executable, "startpage.py"])
        self.close()

    def toggle_password(self, checked):
        if checked:
            self.entry.setEchoMode(QLineEdit.Normal)
            self.show_button.setText("Hide")
        else:
            self.entry.setEchoMode(QLineEdit.Password)
            self.show_button.setText("Show")

    def check_password_breach(self):
        password = self.entry.text()
        if not password:
            self.breach_result_label.setText("Please enter a password.")
            self.breach_result_label.setStyleSheet("color: orange;")
            return

        sha1password = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
        prefix = sha1password[:5]
        suffix = sha1password[5:]
        url = f"https://api.pwnedpasswords.com/range/{prefix}"

        try:
            response = requests.get(url)
            if response.status_code != 200:
                self.breach_result_label.setText("Error reaching API.")
                self.breach_result_label.setStyleSheet("color: orange;")
                return

            hashes = (line.split(':') for line in response.text.splitlines())
            found = any(suffix == hash_suffix for hash_suffix, count in hashes)

            if found:
                self.breach_result_label.setText("⚠️ Password has been breached!")
                self.breach_result_label.setStyleSheet("color: red;")
                # Prevent adding multiple buttons

                if not hasattr(self, 'change_password_button'):
                    self.change_password_button = QPushButton("Change Password")
                    self.change_password_button.setFont(QFont("Arial", 12))
                    self.change_password_button.setFixedWidth(300)
                    self.change_password_button.clicked.connect(self.open_change_password)
                    self.layout.addWidget(self.change_password_button, alignment=Qt.AlignCenter)
                
            else:
                self.breach_result_label.setText("✅ Password is safe.")
                self.breach_result_label.setStyleSheet("color: green;")

        except requests.RequestException:
            self.breach_result_label.setText("Network error.")
            self.breach_result_label.setStyleSheet("color: red;")

    def open_change_password(self):
        subprocess.Popen([sys.executable, "change_password.py"])
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PasswordCheckerApp()
    window.show()
    sys.exit(app.exec_())
