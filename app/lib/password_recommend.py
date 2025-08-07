import random
import string
from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QPushButton,
    QCheckBox, QSpinBox, QMessageBox, QApplication
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


class PasswordGeneratorWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Title
        title = QLabel("Random Password Generator")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Password length selector
        length_layout = QHBoxLayout()
        length_label = QLabel("Password Length:")
        length_label.setFont(QFont("Arial", 11))
        length_layout.addWidget(length_label)

        self.length_spin = QSpinBox()
        self.length_spin.setRange(4, 64)
        self.length_spin.setValue(12)
        length_layout.addWidget(self.length_spin)

        layout.addLayout(length_layout)

        # Character set checkboxes
        self.lowercase_cb = QCheckBox("Include lowercase (a-z)")
        self.lowercase_cb.setChecked(True)
        layout.addWidget(self.lowercase_cb)

        self.uppercase_cb = QCheckBox("Include uppercase (A-Z)")
        self.uppercase_cb.setChecked(True)
        layout.addWidget(self.uppercase_cb)

        self.digits_cb = QCheckBox("Include digits (0-9)")
        self.digits_cb.setChecked(True)
        layout.addWidget(self.digits_cb)

        self.symbols_cb = QCheckBox("Include symbols (!@#$%)")
        self.symbols_cb.setChecked(True)
        layout.addWidget(self.symbols_cb)

        # Easy-to-remember checkbox
        self.easy_remember_cb = QCheckBox("Easy-to-remember password (pronounceable)")
        self.easy_remember_cb.setChecked(False)
        layout.addWidget(self.easy_remember_cb)

        # Generated password display
        self.password_output = QLineEdit()
        self.password_output.setReadOnly(True)
        self.password_output.setPlaceholderText("Your generated password will appear here")
        self.password_output.setMinimumWidth(300)
        layout.addWidget(self.password_output)

        # Buttons: Generate + Copy
        buttons_layout = QHBoxLayout()

        self.generate_btn = QPushButton("Generate")
        self.generate_btn.clicked.connect(self.generate_password)
        buttons_layout.addWidget(self.generate_btn)

        self.copy_btn = QPushButton("Copy to Clipboard")
        self.copy_btn.clicked.connect(self.copy_to_clipboard)
        buttons_layout.addWidget(self.copy_btn)

        layout.addLayout(buttons_layout)

        self.setLayout(layout)

    def generate_password(self):
        length = self.length_spin.value()
        use_lower = self.lowercase_cb.isChecked()
        use_upper = self.uppercase_cb.isChecked()
        use_digits = self.digits_cb.isChecked()
        use_symbols = self.symbols_cb.isChecked()
        easy_remember = self.easy_remember_cb.isChecked()

        if not (use_lower or use_upper or use_digits or use_symbols):
            QMessageBox.warning(self, "Input Error", "Please select at least one character set.")
            return

        if easy_remember:
            pwd = self.generate_pronounceable(length)
        else:
            pwd = self.generate_random(length, use_lower, use_upper, use_digits, use_symbols)

        self.password_output.setText(pwd)

        # Reset copy button state whenever new password is generated
        self.copy_btn.setEnabled(True)
        self.copy_btn.setText("Copy to Clipboard")

    def generate_random(self, length, use_lower, use_upper, use_digits, use_symbols):
        charset = ""
        if use_lower:
            charset += string.ascii_lowercase
        if use_upper:
            charset += string.ascii_uppercase
        if use_digits:
            charset += string.digits
        if use_symbols:
            charset += "!@#$%^&*()-_=+[]{}|;:,.<>?/~`"

        if not charset:
            return ""

        # Make sure password contains at least one character from each selected set
        password_chars = []

        if use_lower:
            password_chars.append(random.choice(string.ascii_lowercase))
        if use_upper:
            password_chars.append(random.choice(string.ascii_uppercase))
        if use_digits:
            password_chars.append(random.choice(string.digits))
        if use_symbols:
            password_chars.append(random.choice("!@#$%^&*()-_=+[]{}|;:,.<>?/~`"))

        # Fill the rest of password length with random chars from charset
        remaining_length = length - len(password_chars)
        password_chars.extend(random.choices(charset, k=remaining_length))

        # Shuffle the result
        random.shuffle(password_chars)

        return "".join(password_chars)

    def generate_pronounceable(self, length):
        # Very simple pronounceable password generator (consonant-vowel alternating)
        vowels = "aeiou"
        consonants = "bcdfghjklmnpqrstvwxyz"

        pwd = []
        # Start with consonant or vowel randomly
        use_consonant = random.choice([True, False])

        while len(pwd) < length:
            if use_consonant:
                pwd.append(random.choice(consonants))
            else:
                pwd.append(random.choice(vowels))
            use_consonant = not use_consonant

        return "".join(pwd)[:length]

    def copy_to_clipboard(self):
        pwd = self.password_output.text()
        if not pwd:
            # If no password, silently do nothing
            return
        clipboard = QApplication.clipboard()
        clipboard.setText(pwd)

        # Change button appearance and text
        self.copy_btn.setText("Copied!")
        self.copy_btn.setEnabled(False)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = PasswordGeneratorWidget()
    window.show()
    sys.exit(app.exec_())
