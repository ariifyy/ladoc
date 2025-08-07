import sqlite3

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QMessageBox, QSpacerItem,
    QSizePolicy
)
from PyQt5.QtCore import Qt
from .utilities.db_connection import get_db_path 
import sqlite3

class AccountPage(QWidget):
    def __init__(self, username, user_id, parent=None):
        super().__init__(parent)
        self.username = username
        self.user_id = user_id

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

        title = QLabel("Account Settings")
        title.setObjectName("WelcomeHeading")
        layout.addWidget(title)

        username_label = QLabel(f"Username: {self.username}")
        layout.addWidget(username_label)

        layout.addSpacing(20)
        layout.addWidget(QLabel("Change Password"))

        self.old_password_input = QLineEdit()
        self.old_password_input.setPlaceholderText("Current Password")
        self.old_password_input.setEchoMode(QLineEdit.Password)

        self.new_password_input = QLineEdit()
        self.new_password_input.setPlaceholderText("New Password")
        self.new_password_input.setEchoMode(QLineEdit.Password)

        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Confirm New Password")
        self.confirm_password_input.setEchoMode(QLineEdit.Password)

        layout.addWidget(self.old_password_input)
        layout.addWidget(self.new_password_input)
        layout.addWidget(self.confirm_password_input)

        change_password_btn = QPushButton("Change Password")
        change_password_btn.clicked.connect(self.change_password)
        layout.addWidget(change_password_btn)

        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # === Delete Account Button ===
        delete_account_btn = QPushButton("Delete Account")
        delete_account_btn.setObjectName("DeleteAccountButton")
        delete_account_btn.clicked.connect(self.confirm_delete_account)
        layout.addWidget(delete_account_btn)

    def change_password(self):
        old = self.old_password_input.text()
        new = self.new_password_input.text()
        confirm = self.confirm_password_input.text()

        if new != confirm:
            QMessageBox.warning(self, "Error", "New passwords do not match.")
            return

        QMessageBox.information(self, "Success", "Password changed (demo only).")
        self.old_password_input.clear()
        self.new_password_input.clear()
        self.confirm_password_input.clear()

    def confirm_delete_account(self):
        reply = QMessageBox.question(
            self,
            "Delete Account",
            "Are you sure you want to permanently delete your account? This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.delete_account()

    def delete_account(self):
        try:
            conn = sqlite3.connect(get_db_path())
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM user_passwords WHERE user_id = ?", (self.user_id,))
            cursor.execute("DELETE FROM users_folders WHERE user_id = ?", (self.user_id,))
            cursor.execute("DELETE FROM users WHERE id = ?", (self.user_id,))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Account Deleted", "Your account has been successfully deleted.")

            main_window = self.window()
            if hasattr(main_window, 'show_login'):
                main_window.stack.setCurrentWidget(main_window.login_page)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete account: {e}")
