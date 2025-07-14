# password_haveibeenpwned.py
import hashlib
import requests
from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QHBoxLayout
)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt

class HaveIBeenPwnedWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        # --- Title ---
        title = QLabel("Check Password Breach Status")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # --- Subtitle ---
        subtitle = QLabel("Enter a password below to check against known breaches:")
        subtitle.setFont(QFont("Arial", 12))
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        # --- Input (centered with fixed width) ---
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password here")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedWidth(300)  # Narrower input
        self.password_input.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.password_input, alignment=Qt.AlignCenter)

        # --- Toggle Button ---
        self.toggle_button = QPushButton("Show / Hide Password")
        self.toggle_button.clicked.connect(self.toggle_password_visibility)
        self.toggle_button.setFixedWidth(200)
        layout.addWidget(self.toggle_button, alignment=Qt.AlignCenter)

        # --- Submit Button ---
        submit_button = QPushButton("Check Breach")
        submit_button.clicked.connect(self.check_breach)
        submit_button.setFixedWidth(200)
        layout.addWidget(submit_button, alignment=Qt.AlignCenter)

        # --- Result Label ---
        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setWordWrap(True)
        self.result_label.setFont(QFont("Arial", 11))
        layout.addWidget(self.result_label)

        self.setLayout(layout)

    def toggle_password_visibility(self):
        if self.password_input.echoMode() == QLineEdit.Password:
            self.password_input.setEchoMode(QLineEdit.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.Password)

    def check_breach(self):
        password = self.password_input.text().strip()
        if not password:
            self.result_label.setStyleSheet("color: orange; font-weight: bold;")
            self.result_label.setText("Please enter a password.")
            return


        sha1 = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
        prefix, suffix = sha1[:5], sha1[5:]
        url = f"https://api.pwnedpasswords.com/range/{prefix}"

        try:
            response = requests.get(url)
            if response.status_code != 200:
                self.result_label.setStyleSheet("color: black;")
                self.result_label.setText("Something went wrong. Please try again later.")
                return

            hashes = (line.split(":") for line in response.text.splitlines())
            for h, count in hashes:
                if h == suffix:
                    self.result_label.setStyleSheet("color: red; font-weight: bold;")
                    self.result_label.setText(f"Password found {count} times in breaches!")
                    return

            self.result_label.setStyleSheet("color: green; font-weight: bold;")
            self.result_label.setText("No breaches found. Your password is safe.")
        except Exception as e:
            self.result_label.setStyleSheet("color: black;")
            self.result_label.setText(f"Error: {str(e)}")
