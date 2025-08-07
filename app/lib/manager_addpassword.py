from PyQt5.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QComboBox, QDateEdit, QTreeWidget,
    QTreeWidgetItem, QLabel, QDialogButtonBox, QPushButton, QHBoxLayout,
    QVBoxLayout, QWidget, QMessageBox, QCheckBox, QSpinBox, QTextEdit
)
from PyQt5.QtCore import Qt, QDate
import random
import string


class AddPasswordDialog(QDialog):
    MAX_PASSWORD_LENGTH = 64  # Maximum allowed length

    def __init__(self, folders, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Password")
        self.setMinimumWidth(600)
        self.setMinimumHeight(550)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        main_layout.addLayout(form_layout)

        # Title, Username, Password, Site fields
        self.title_edit = QLineEdit()
        self.username_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.site_edit = QLineEdit()

        form_layout.addRow("Title*:", self.title_edit)
        form_layout.addRow("Username:", self.username_edit)

        # Password row: line edit + show/hide button + generate button
        pw_row_widget = QWidget()
        pw_row_layout = QHBoxLayout(pw_row_widget)
        pw_row_layout.setContentsMargins(0, 0, 0, 0)
        pw_row_layout.setSpacing(8)

        pw_row_layout.addWidget(self.password_edit)

        self.toggle_password_btn = QPushButton("Show")
        self.toggle_password_btn.setCheckable(True)
        self.toggle_password_btn.clicked.connect(self.toggle_password_visibility)
        pw_row_layout.addWidget(self.toggle_password_btn)

        self.generate_password_btn = QPushButton("Generate")
        self.generate_password_btn.clicked.connect(self.open_generate_password_options)
        pw_row_layout.addWidget(self.generate_password_btn)

        form_layout.addRow("Password*:", pw_row_widget)
        form_layout.addRow("Site:", self.site_edit)

        self.notes_edit = QTextEdit()
        self.notes_edit.setFixedHeight(80)
        form_layout.addRow("Notes:", self.notes_edit)

        # Expiry options
        self.expiry_combo = QComboBox()
        self.expiry_combo.addItems(["No Expiry", "3 Months", "6 Months", "12 Months", "Custom Date"])
        self.expiry_combo.currentTextChanged.connect(self.on_expiry_option_changed)

        self.custom_date_edit = QDateEdit()
        self.custom_date_edit.setCalendarPopup(True)
        self.custom_date_edit.setDate(QDate.currentDate())
        self.custom_date_edit.setEnabled(False)

        form_layout.addRow("Expiry Option:", self.expiry_combo)
        form_layout.addRow("Custom Expiry Date:", self.custom_date_edit)

        # Folder tree
        main_layout.addSpacing(15)
        main_layout.addWidget(QLabel("Select Folder:"))

        self.folder_tree = QTreeWidget()
        self.folder_tree.setHeaderHidden(True)
        self.folder_tree.setMinimumHeight(160)
        main_layout.addWidget(self.folder_tree)

        self._build_folder_tree(folders)
        self.folder_tree.setCurrentItem(self.folder_tree.topLevelItem(0))

        # Dialog buttons
        main_layout.addSpacing(10)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=self)
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        main_layout.addWidget(buttons)

        # Create generate password options dialog but don't show yet
        self.gen_pw_dialog = None

    def toggle_password_visibility(self):
        if self.toggle_password_btn.isChecked():
            self.password_edit.setEchoMode(QLineEdit.Normal)
            self.toggle_password_btn.setText("Hide")
        else:
            self.password_edit.setEchoMode(QLineEdit.Password)
            self.toggle_password_btn.setText("Show")

    def validate_and_accept(self):
        title = self.title_edit.text().strip()
        password = self.password_edit.text()
        notes = self.notes_edit.toPlainText()

        if not title or not password:
            QMessageBox.warning(self, "Missing Fields", "Title and Password are required.")
            return

        if len(password) > self.MAX_PASSWORD_LENGTH:
            QMessageBox.warning(
                self,
                "Password Too Long",
                f"Password cannot exceed {self.MAX_PASSWORD_LENGTH} characters."
            )
            return

        if len(notes) > 200:
            QMessageBox.warning(self, "Notes Too Long", "Notes cannot exceed 200 characters.")
            return

        self.accept()


    def on_expiry_option_changed(self, text):
        self.custom_date_edit.setEnabled(text == "Custom Date")

    def _build_folder_tree(self, folders):
        id_to_item = {}
        root = QTreeWidgetItem(["All Passwords"])
        root.setData(0, Qt.UserRole, None)
        root.setExpanded(True)
        self.folder_tree.addTopLevelItem(root)
        id_to_item[None] = root

        for folder_id, name, parent_id in folders:
            parent_item = id_to_item.get(parent_id, root)
            item = QTreeWidgetItem([name])
            item.setData(0, Qt.UserRole, folder_id)
            parent_item.addChild(item)
            id_to_item[folder_id] = item

    def get_selected_folder_path(self):
        item = self.folder_tree.currentItem()
        if not item:
            return None
        names = []
        while item and item.data(0, Qt.UserRole) is not None:
            names.insert(0, item.text(0))
            item = item.parent()
        return "/".join(names) if names else None

    def get_data(self):
        expiry_date = None
        selected_option = self.expiry_combo.currentText()
        today = QDate.currentDate()

        if selected_option == "3 Months":
            expiry_date = today.addMonths(3)
        elif selected_option == "6 Months":
            expiry_date = today.addMonths(6)
        elif selected_option == "12 Months":
            expiry_date = today.addMonths(12)
        elif selected_option == "Custom Date":
            expiry_date = self.custom_date_edit.date()

        expiry_str = expiry_date.toString("yyyy-MM-dd") if expiry_date else None

        return {
            "title": self.title_edit.text(),
            "username": self.username_edit.text(),
            "password": self.password_edit.text(),
            "site": self.site_edit.text(),
            "notes": self.notes_edit.toPlainText(),
            "folder_path": self.get_selected_folder_path(),
            "password_expiry": expiry_str,
        }

    def open_generate_password_options(self):
        if self.gen_pw_dialog is None:
            self.gen_pw_dialog = GeneratePasswordDialog(self.MAX_PASSWORD_LENGTH, self)
            self.gen_pw_dialog.password_generated.connect(self.set_generated_password)
        self.gen_pw_dialog.show()
        self.gen_pw_dialog.raise_()
        self.gen_pw_dialog.activateWindow()

    def set_generated_password(self, pw):
        self.password_edit.setText(pw)


from PyQt5.QtCore import pyqtSignal


class GeneratePasswordDialog(QDialog):
    password_generated = pyqtSignal(str)

    def __init__(self, max_length, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Generate Password")
        self.setMinimumWidth(400)
        self.max_length = max_length

        layout = QFormLayout(self)

        # Password length spinbox
        self.length_spin = QSpinBox()
        self.length_spin.setRange(4, max_length)
        self.length_spin.setValue(16)
        layout.addRow("Password Length:", self.length_spin)

        # Checkboxes for character sets
        self.include_upper = QCheckBox("Include Uppercase (A-Z)")
        self.include_upper.setChecked(True)
        layout.addRow(self.include_upper)

        self.include_lower = QCheckBox("Include Lowercase (a-z)")
        self.include_lower.setChecked(True)
        layout.addRow(self.include_lower)

        self.include_digits = QCheckBox("Include Digits (0-9)")
        self.include_digits.setChecked(True)
        layout.addRow(self.include_digits)

        self.include_symbols = QCheckBox("Include Symbols (!@#$...)")
        self.include_symbols.setChecked(True)
        layout.addRow(self.include_symbols)

        # Buttons
        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.generate_password)
        btn_box.rejected.connect(self.reject)
        layout.addRow(btn_box)

    def generate_password(self):
        length = self.length_spin.value()
        char_pools = ""

        if self.include_upper.isChecked():
            char_pools += string.ascii_uppercase
        if self.include_lower.isChecked():
            char_pools += string.ascii_lowercase
        if self.include_digits.isChecked():
            char_pools += string.digits
        if self.include_symbols.isChecked():
            char_pools += "!@#$%^&*()-_=+[]{}|;:,.<>?/"

        if not char_pools:
            QMessageBox.warning(self, "Invalid Selection", "Select at least one character type.")
            return

        # Generate a random password
        password = "".join(random.choice(char_pools) for _ in range(length))
        self.password_generated.emit(password)
        self.accept()
