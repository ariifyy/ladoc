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
        layout = QVBoxLayout()

        #Back Button with arrow
        back_button = QPushButton("⬅ Home")
        back_button.setFont(QFont("Arial", 12))
        back_button.setFixedWidth(120)
        back_button.clicked.connect(self.go_back)
        layout.addWidget(back_button, alignment=Qt.AlignLeft)

        # Instruction Label
        self.label = QLabel("Enter your password:")
        self.label.setFont(QFont("Arial", 14))
        layout.addWidget(self.label)

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

        layout.addLayout(password_layout)

        # Password Strength Label
        self.strength_label = QLabel("")
        self.strength_label.setFont(QFont("Arial", 10))
        self.strength_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.strength_label)

        # Buttons: Check Strength, Suggest Password, Check Breach
        button_layout = QHBoxLayout()

        self.check_strength_button = QPushButton("Check your Password's Strength")
        self.check_strength_button.clicked.connect(self.check_strength)
        button_layout.addWidget(self.check_strength_button)

        self.suggest_button = QPushButton("Suggest Password")
        self.suggest_button.clicked.connect(self.suggest_password)
        button_layout.addWidget(self.suggest_button)

        layout.addLayout(button_layout)

        # Breach Result Label
        self.breach_result_label = QLabel("")
        self.breach_result_label.setAlignment(Qt.AlignCenter)
        self.breach_result_label.setFont(QFont("Arial", 10))
        layout.addWidget(self.breach_result_label)

        self.setLayout(layout)

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

    def check_strength(self):
        password = self.entry.text()
        strength = self.evaluate_strength(password)
        self.strength_label.setText(strength)
        self.strength_label.setStyleSheet("color: red;" if "Weaknesses" in strength else "color: green;")

    def evaluate_strength(self, password):
        suggestions = []

        if len(password) < 12:
            suggestions.append("• Make it at least 12 characters long")
        
        if not re.search(r"[A-Z]", password):
            suggestions.append("• Add at least one uppercase letter (A-Z)")
        
        if not re.search(r"[a-z]", password):
            suggestions.append("• Add at least one lowercase letter (a-z)")
        
        if not re.search(r"[0-9]", password):
            suggestions.append("• Add at least one digit (0-9)")
        
        if not re.search(r"[^\w\s]", password):
            suggestions.append("• Add at least one special character (!@#$ etc.)")

        if suggestions:
            return "Password Weaknesses:\n" + "\n".join(suggestions)
        else:
            return "Strong password ✅"

    def suggest_password(self):
        characters = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(secrets.choice(characters) for _ in range(16))
        self.entry.setText(password)
        self.strength_label.setText("Suggested strong password above")
        self.breach_result_label.setText("")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PasswordCheckerApp()
    window.show()
    sys.exit(app.exec_())
