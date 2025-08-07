# auth_pages/signup_page.py

import re
import sqlite3, bcrypt
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QFrame, QSizePolicy, QSpacerItem
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


class SignupPage(QWidget):
    def __init__(self, switch_to_login):
        super().__init__()
        self.switch_to_login = switch_to_login
        self.init_ui()

    def init_ui(self):
        # Outer layout to center everything
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        # Spacer above
        outer_layout.addStretch(1)

        # Container for all signup elements
        container = QWidget()
        container.setMaximumWidth(500)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(20)

        # Title
        title = QLabel("Like a Deck of Cards")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Inter", 25, QFont.DemiBold))
        container_layout.addWidget(title, alignment=Qt.AlignHCenter)

        # Spacer between title and signup form
        spacer = QSpacerItem(0, 20)
        container_layout.addItem(spacer)

        # Signup Form Card
        form_card = QFrame()
        form_card.setObjectName("AuthCard")

        form_layout = QVBoxLayout(form_card)
        form_layout.setAlignment(Qt.AlignTop)
        form_layout.setSpacing(12)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setFont(QFont("Inter", 10))

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        self.email_input.setFont(QFont("Inter", 10))
        self.email_input.returnPressed.connect(self.register_user)


        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFont(QFont("Inter", 10))
        self.password_input.returnPressed.connect(self.register_user)


        register_btn = QPushButton("Sign Up")
        register_btn.setObjectName("LoginButton")  # Reuse style
        register_btn.setFont(QFont("Inter", 11, QFont.Medium))
        register_btn.clicked.connect(self.register_user)
        self.username_input.returnPressed.connect(self.register_user)

        form_layout.addWidget(self.username_input)
        form_layout.addWidget(self.email_input)
        form_layout.addWidget(self.password_input)
        form_layout.addWidget(register_btn)

        container_layout.addWidget(form_card, alignment=Qt.AlignHCenter)

        # OR Divider
        divider_widget = QWidget()
        divider_layout = QHBoxLayout(divider_widget)
        divider_layout.setSpacing(6)
        divider_layout.setContentsMargins(0, 0, 0, 0)

        line1 = QFrame()
        line1.setFrameShape(QFrame.HLine)
        line1.setFixedHeight(1)
        line1.setStyleSheet("background-color: #888888; border: none;")
        line1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        or_label = QLabel("OR")
        or_label.setAlignment(Qt.AlignCenter)
        or_label.setFont(QFont("Inter", 10))
        or_label.setStyleSheet("color: #bbbbbb; font-size: 11px; padding: 0px; margin: 0px;")

        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setFixedHeight(1)
        line2.setStyleSheet("background-color: #888888; border: none;")
        line2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        divider_layout.addWidget(line1)
        divider_layout.addWidget(or_label)
        divider_layout.addWidget(line2)

        container_layout.addWidget(divider_widget)

        # Login Button
        back_to_login_btn = QPushButton("Already have an account? Sign In.")
        back_to_login_btn.setObjectName("CreateAccountButton")
        back_to_login_btn.setFont(QFont("Inter", 11, QFont.Medium))
        back_to_login_btn.clicked.connect(self.switch_to_login)
        container_layout.addWidget(back_to_login_btn, alignment=Qt.AlignCenter)

        # Add container to outer layout
        outer_layout.addWidget(container, alignment=Qt.AlignHCenter | Qt.AlignVCenter)

        # Spacer below
        outer_layout.addStretch(1)

    def register_user(self):
        username = self.username_input.text()
        email = self.email_input.text()
        password = self.password_input.text()
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{12,}$'

        if not username or not email or not password:
            QMessageBox.warning(self, "Missing Info", "Please fill in all fields.")
            return
        
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            QMessageBox.warning(self, "Invalid Email", "Please enter a valid email address.")
            return
        
        if not re.match(pattern, password):
            QMessageBox.warning(
                self, "Weak Password", 
                "Password must be at least 12 characters long and include:\n"
                "- Uppercase and lowercase letters\n"
                "- A digit\n"
                "- A special character"
            )
            return

        conn = sqlite3.connect("LADOC.db")
        cursor = conn.cursor()
        try:
            hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                (username, email, hashed_pw))
            conn.commit()
            QMessageBox.information(self, "Success", "Account created successfully!")
            self.switch_to_login()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "Username or email already exists.")
        finally:
            conn.close()
