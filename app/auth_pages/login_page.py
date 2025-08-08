import sqlite3
import bcrypt
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtWidgets import QCheckBox

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QFrame, QSizePolicy, QSpacerItem
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from lib.utilities.db_connection import get_db_path


class LoginPage(QWidget):
    def __init__(self, switch_to_signup, open_homepage):
        super().__init__()
        self.switch_to_signup = switch_to_signup
        self.open_homepage = open_homepage
        self.init_ui()

       
        self.settings = QSettings("LADOC", "App")
        

    def init_ui(self):
        # Outer layout to center everything
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        # Spacer above
        outer_layout.addStretch(1)

        # Container for all login elements
        container = QWidget()
        container.setMaximumWidth(1000)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(20)

        # Title
        title = QLabel("Like a Deck of Cards")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Inter", 25, QFont.Bold))
        container_layout.addWidget(title, alignment=Qt.AlignHCenter)

        # Spacer between title and login form
        spacer = QSpacerItem(0, 20)  # Adjust the height here
        container_layout.addItem(spacer)

        # Login Form Card
        form_card = QFrame()
        form_card.setObjectName("AuthCard")

        form_layout = QVBoxLayout(form_card)
        form_layout.setAlignment(Qt.AlignTop)
        form_layout.setSpacing(12)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setFont(QFont("Inter", 10))
        self.username_input.returnPressed.connect(self.login)

        password_layout = QHBoxLayout()
        password_layout.setSpacing(5)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFont(QFont("Inter", 10))
        self.password_input.returnPressed.connect(self.login)

        self.toggle_password_btn = QPushButton("Show")
        self.toggle_password_btn.setCheckable(True)
        self.toggle_password_btn.setFixedWidth(60)
        self.toggle_password_btn.setMaximumHeight(45)
        self.toggle_password_btn.setFont(QFont("Inter", 16)) 
        self.toggle_password_btn.setStyleSheet("""
            QPushButton {
                padding: 7px;
                font-size: 14px;
                border-radius: 8px;
            }
        """)
        self.toggle_password_btn.clicked.connect(self.toggle_password_visibility)

        password_layout.addWidget(self.password_input)
        password_layout.addWidget(self.toggle_password_btn)

        # add username first
        form_layout.addWidget(self.username_input)

        # password row (already contains password field + Show/Hide)
        form_layout.addLayout(password_layout)

        # Keep me signed in
        self.remember_cb = QCheckBox("Keep me signed in")
        self.remember_cb.setChecked(False)
        self.remember_cb.setFont(QFont("Inter", 9))
        self.remember_cb.setStyleSheet("background: transparent;")
        form_layout.addWidget(self.remember_cb)

        # Login button (with styling + click handler)
        login_btn = QPushButton("Login")
        login_btn.setObjectName("LoginButton")
        login_btn.setFont(QFont("Inter", 11, QFont.Medium))
        login_btn.clicked.connect(self.login)
        form_layout.addWidget(login_btn)

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
        or_label.setStyleSheet("color: #bbbbbb; font-size: 20px; padding: 0px; margin: 0px;")

        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setFixedHeight(1)
        line2.setStyleSheet("background-color: #888888; border: none;")
        line2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        divider_layout.addWidget(line1)
        divider_layout.addWidget(or_label)
        divider_layout.addWidget(line2)

        container_layout.addWidget(divider_widget)

        # Create Account Button
        create_account_btn = QPushButton("Don't have an account? Sign Up")
        create_account_btn.setObjectName("CreateAccountButton")
        create_account_btn.setFont(QFont("Inter", 16, QFont.Medium))
        create_account_btn.clicked.connect(self.switch_to_signup)
        container_layout.addWidget(create_account_btn, alignment=Qt.AlignCenter)

        # Add container to outer layout
        outer_layout.addWidget(container, alignment=Qt.AlignHCenter | Qt.AlignVCenter)

        # Spacer below
        outer_layout.addStretch(1)

    def toggle_password_visibility(self):
        if self.toggle_password_btn.isChecked():
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.toggle_password_btn.setText("Hide")
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.toggle_password_btn.setText("Show")

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Input Error", "Please enter both username and password.")
            return

        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT id, username, password FROM users WHERE username = ?", (username,))
            result = cursor.fetchone()

            if result:
                user_id, username_db, hashed_pw = result
                if bcrypt.checkpw(password.encode(), hashed_pw.encode()):
                    QMessageBox.information(self, "Login Successful", f"Welcome, {username_db}!")
                    self.save_session(user_id, username_db)  # NEW
                    self.open_homepage(user_id, username_db)
                else:
                    QMessageBox.critical(self, "Login Failed", "Invalid username or password.")
            else:
                QMessageBox.critical(self, "Login Failed", "Invalid username or password.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Something went wrong:\n{str(e)}")
        finally:
            conn.close()

    

    
    def save_session(self, user_id: int, username: str):
        """Save or clear session based on checkbox."""
        if getattr(self, "remember_cb", None) and self.remember_cb.isChecked(): 
           self.settings.setValue("auth/remember", True)
           self.settings.setValue("auth/user_id", user_id)
           self.settings.setValue("auth/username", username)
        else:
           print("DEBUG: Clearing session") 
           self.settings.setValue("auth/remember", False)
           self.settings.remove("auth/user_id")
           self.settings.remove("auth/username")

    def try_auto_login(self):
        if self.settings.value("auth/remember", False, type=bool):
            uid = self.settings.value("auth/user_id", type=int)
            uname = self.settings.value("auth/username", type=str)

            row = None
            try:
                conn = sqlite3.connect(get_db_path())
                cur = conn.cursor()
                cur.execute("SELECT id, username FROM users WHERE id = ?", (uid,))
                row = cur.fetchone()
                conn.close()
            except Exception:
                pass

            if row:
                self.open_homepage(uid, uname or row[1])
                return True  # ✅ Auto-login successful

        return False  # ❌ Auto-login failed