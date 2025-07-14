import math
from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QVBoxLayout, QProgressBar, QPushButton,
    QHBoxLayout, QSizePolicy, QToolButton, QMessageBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


class PasswordStrengthWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Title
        title = QLabel("Password Strength Checker")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Horizontal layout for password input + show/hide button
        input_layout = QHBoxLayout()

        # Password input
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password here")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumWidth(250)
        input_layout.addWidget(self.password_input)

        # Show/Hide toggle button
        self.toggle_button = QPushButton("Show")
        self.toggle_button.setCheckable(True)
        self.toggle_button.setFixedWidth(60)
        self.toggle_button.clicked.connect(self.toggle_password_visibility)
        input_layout.addWidget(self.toggle_button)

        layout.addLayout(input_layout)

        # Horizontal layout for entropy label, progress bar, and help button
        entropy_layout = QHBoxLayout()
        entropy_layout.setAlignment(Qt.AlignCenter)

        # Label for "Password Entropy"
        entropy_label = QLabel("Password Entropy:")
        entropy_label.setFont(QFont("Arial", 11))
        entropy_layout.addWidget(entropy_label)

        # Strength meter (progress bar)
        self.strength_bar = QProgressBar()
        self.strength_bar.setRange(0, 100)
        self.strength_bar.setTextVisible(False)
        self.strength_bar.setMaximumWidth(300)
        self.strength_bar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        entropy_layout.addWidget(self.strength_bar)

        # Help button
        help_button = QToolButton()
        help_button.setText("?")
        help_button.setToolTip("Click to learn more about password entropy.")
        help_button.setFixedSize(20, 20)
        help_button.clicked.connect(self.show_entropy_info)
        help_button.setStyleSheet("""
            QToolButton {
                border: 1px solid #888;
                border-radius: 10px;
                background-color: #3d85c6;
                color: white;
                font-weight: bold;
            }
            QToolButton:hover {
                background-color: #559bd6;
            }
        """)
        entropy_layout.addWidget(help_button)

        layout.addLayout(entropy_layout)

        # Strength label
        self.strength_label = QLabel("")
        self.strength_label.setAlignment(Qt.AlignCenter)
        self.strength_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.strength_label.setMaximumWidth(300)
        self.strength_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        layout.addWidget(self.strength_label, alignment=Qt.AlignCenter)

        # Tips label for dynamic feedback
        self.tips_label = QLabel("")
        self.tips_label.setWordWrap(True)
        self.tips_label.setFont(QFont("Arial", 10))
        self.tips_label.setStyleSheet("color: #000000;")  # Accent color
        self.tips_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.tips_label)

        self.password_input.textChanged.connect(self.evaluate_strength)

        self.setLayout(layout)

    def toggle_password_visibility(self):
        if self.toggle_button.isChecked():
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.toggle_button.setText("Hide")
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.toggle_button.setText("Show")

    def evaluate_strength(self):
        password = self.password_input.text()
        if not password:
            self.strength_bar.setValue(0)
            self.strength_label.setText("")
            self.tips_label.setText("")
            return

        entropy = self.calculate_entropy(password)
        score = min(int(entropy), 100)  # cap at 100 for progress bar

        # Update progress bar
        self.strength_bar.setValue(score)

        # Set color and text based on score
        if score < 30:
            self.set_bar_color("red")
            self.strength_label.setText("Weak")
        elif score < 60:
            self.set_bar_color("orange")
            self.strength_label.setText("Moderate")
        elif score < 80:
            self.set_bar_color("yellowgreen")
            self.strength_label.setText("Strong")
        else:
            self.set_bar_color("green")
            self.strength_label.setText("Very Strong")

        # Update tips dynamically
        tips = []
        if len(password) < 8:
            tips.append("Use at least 8 characters.")
        if not any(c.islower() for c in password):
            tips.append("Include lowercase letters.")
        if not any(c.isupper() for c in password):
            tips.append("Include uppercase letters.")
        if not any(c.isdigit() for c in password):
            tips.append("Include numbers.")
        if not any(not c.isalnum() for c in password):
            tips.append("Include special characters (e.g. !@#$%).")

        if tips:
            self.tips_label.setText("Tips to improve your password:\n- " + "\n- ".join(tips))
        else:
            self.tips_label.setText("Great! Your password looks strong.")

    def calculate_entropy(self, password):
        charset = 0
        if any(c.islower() for c in password):
            charset += 26
        if any(c.isupper() for c in password):
            charset += 26
        if any(c.isdigit() for c in password):
            charset += 10
        if any(not c.isalnum() for c in password):
            charset += 32

        if charset == 0:
            return 0

        entropy = len(password) * math.log2(charset)
        return entropy

    def set_bar_color(self, color):
        style = f"""
            QProgressBar::chunk {{
                background-color: {color};
            }}
            QProgressBar {{
                border: 1px solid grey;
                border-radius: 5px;
                text-align: center;
            }}
        """
        self.strength_bar.setStyleSheet(style)

    def show_entropy_info(self):
        QMessageBox.information(
            self,
            "What is Password Entropy?",
            (
                "Password entropy is a measure of how unpredictable or complex a password is.\n\n"
                "It is calculated based on the length and variety of characters used "
                "(lowercase, uppercase, numbers, and symbols).\n\n"
                "Higher entropy = more secure password.\n\n"
                "Tips for high entropy:\n"
                "- Use longer passwords\n"
                "- Mix character types\n"
                "- Avoid common or guessable patterns"
            )
        )
