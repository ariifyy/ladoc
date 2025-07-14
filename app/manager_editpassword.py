from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QTextEdit,
    QPushButton, QComboBox, QDateEdit, QMessageBox, QCheckBox
)
from PyQt5.QtCore import QDate


class EditPasswordDialog(QDialog):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Password")
        self.setMinimumWidth(400)

        layout = QVBoxLayout()
        form = QFormLayout()

        self.title_input = QLineEdit(data["title"])
        self.username_input = QLineEdit(data["username"])
        self.password_input = QLineEdit(data["password"])
        self.password_input.setEchoMode(QLineEdit.Password)

        self.show_password_cb = QCheckBox("Show Password")
        self.show_password_cb.toggled.connect(
            lambda checked: self.password_input.setEchoMode(
                QLineEdit.Normal if checked else QLineEdit.Password
            )
        )

        self.site_input = QLineEdit(data["site"])
        self.notes_input = QTextEdit(data["notes"])
        self.folder_input = QLineEdit(data["folder_path"] or "")

        self.expiry_combo = QComboBox()
        self.expiry_combo.addItems(["No Expiry", "3 months", "6 months", "Custom Date"])

        self.expiry_date = QDateEdit()
        self.expiry_date.setCalendarPopup(True)
        self.expiry_date.setEnabled(False)

        if data["password_expiry"]:
            self.expiry_date.setDate(QDate.fromString(data["password_expiry"], "yyyy-MM-dd"))
            self.expiry_combo.setCurrentText("Custom Date")
            self.expiry_date.setEnabled(True)
        else:
            self.expiry_combo.setCurrentText("No Expiry")

        self.expiry_combo.currentIndexChanged.connect(self.toggle_expiry_date)

        form.addRow("Title*", self.title_input)
        form.addRow("Username", self.username_input)
        form.addRow("Password*", self.password_input)
        form.addRow("", self.show_password_cb)
        form.addRow("Site", self.site_input)
        form.addRow("Notes", self.notes_input)
        form.addRow("Folder Path", self.folder_input)
        form.addRow("Expiry", self.expiry_combo)
        form.addRow("Custom Date", self.expiry_date)

        layout.addLayout(form)

        self.save_btn = QPushButton("Update")
        self.save_btn.clicked.connect(self.validate_and_accept)
        layout.addWidget(self.save_btn)

        self.setLayout(layout)

    def toggle_expiry_date(self, index):
        self.expiry_date.setEnabled(self.expiry_combo.currentText() == "Custom Date")

    def validate_and_accept(self):
        if not self.title_input.text().strip() or not self.password_input.text().strip():
            QMessageBox.warning(self, "Missing Fields", "Title and Password are required.")
            return
        self.accept()

    def get_data(self):
        expiry = None
        if self.expiry_combo.currentText() == "3 months":
            expiry = QDate.currentDate().addMonths(3).toString("yyyy-MM-dd")
        elif self.expiry_combo.currentText() == "6 months":
            expiry = QDate.currentDate().addMonths(6).toString("yyyy-MM-dd")
        elif self.expiry_combo.currentText() == "Custom Date":
            expiry = self.expiry_date.date().toString("yyyy-MM-dd")

        return {
            "title": self.title_input.text(),
            "username": self.username_input.text(),
            "password": self.password_input.text(),
            "site": self.site_input.text(),
            "notes": self.notes_input.toPlainText(),
            "folder_path": self.folder_input.text(),
            "password_expiry": expiry
        }
