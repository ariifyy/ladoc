import sys
import re
import secrets
import string
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout
)
from PyQt5.QtGui import QFont

class PasswordRecommender(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Password Strength Checker")
        self.setFixedSize(350, 200)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Label and input for password
        self.label = QLabel("Enter your password:")
        self.label.setFont(QFont("Arial", 10))
        layout.addWidget(self.label)

        self.password_input = QLineEdit()
        layout.addWidget(self.password_input)

        # Button to check strength
        self.check_button = QPushButton("Check Strength")
        self.check_button.clicked.connect(self.check_strength)
        layout.addWidget(self.check_button)

        # Button to suggest password
        self.suggest_button = QPushButton("Suggest Strong Password")
        self.suggest_button.clicked.connect(self.suggest_password)
        layout.addWidget(self.suggest_button)

        # Label to display result
        self.result_label = QLabel("")
        layout.addWidget(self.result_label)

        self.setLayout(layout)

    def check_strength(self):
        password = self.password_input.text()
        if len(password) < 12:
            strength = "Weak: Too short"
        elif not re.search("[A-Z]", password):
            strength = "Weak: Add uppercase"
        elif not re.search("[a-z]", password):
            strength = "Weak: Add lowercase"
        elif not re.search("[0-9]", password):
            strength = "Weak: Add numbers"
        elif not re.search("[^A-Za-z0-9]", password):
            strength = "Weak: Add symbols"
        else:
            strength = "Strong password ✅"
        self.result_label.setText(strength)

    def suggest_password(self):
        characters = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(secrets.choice(characters) for _ in range(14))
        self.password_input.setText(password)
        self.result_label.setText("Suggested strong password above ↑")

# Run the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PasswordRecommender()
    window.show()
    sys.exit(app.exec_())