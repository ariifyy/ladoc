from PyQt5.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QComboBox, QDateEdit, QTreeWidget,
    QTreeWidgetItem, QLabel, QDialogButtonBox, QPushButton, QHBoxLayout,
    QVBoxLayout, QWidget, QTextEdit, QMessageBox
)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
import sqlite3

from .manager_addpassword import GeneratePasswordDialog



class EditPasswordDialog(QDialog):
    password_deleted = pyqtSignal()

    def __init__(self, folders, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Password")
        self.setMinimumWidth(600) 
        self.setMinimumHeight(550) 

        self.entry_id = None  # Store the password entry ID here

        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        main_layout.addLayout(form_layout)

        self.title_edit = QLineEdit()
        self.username_edit = QLineEdit()

        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)

        self.site_edit = QLineEdit()
        self.notes_edit = QTextEdit()
        self.notes_edit.setFixedHeight(80)

        pw_widget = QWidget()
        pw_layout = QHBoxLayout(pw_widget)
        pw_layout.setContentsMargins(0, 0, 0, 0)
        pw_layout.setSpacing(8)
        pw_layout.addWidget(self.password_edit)

        self.toggle_password_btn = QPushButton("Show")
        self.toggle_password_btn.setCheckable(True)
        self.toggle_password_btn.clicked.connect(self.toggle_password_visibility)
        pw_layout.addWidget(self.toggle_password_btn)

        self.generate_password_btn = QPushButton("Generate")
        self.generate_password_btn.clicked.connect(self.open_generate_password_options)
        pw_layout.addWidget(self.generate_password_btn)

        form_layout.addRow("Title*:", self.title_edit)
        form_layout.addRow("Username:", self.username_edit)
        form_layout.addRow("Password*:", pw_widget)
        form_layout.addRow("Site:", self.site_edit)
        
        form_layout.addRow("Notes:", self.notes_edit)
        self.notes_edit.setPlaceholderText("Notes (max 200 characters)...")


        self.expiry_combo = QComboBox()
        self.expiry_combo.addItems(["No Expiry", "3 Months", "6 Months", "12 Months", "Custom Date"])
        self.expiry_combo.currentTextChanged.connect(self.on_expiry_option_changed)

        self.custom_date_edit = QDateEdit()
        self.custom_date_edit.setCalendarPopup(True)
        self.custom_date_edit.setDate(QDate.currentDate())
        self.custom_date_edit.setEnabled(False)

        form_layout.addRow("Expiry Option:", self.expiry_combo)
        form_layout.addRow("Custom Expiry Date:", self.custom_date_edit)

        self.folder_tree = QTreeWidget()
        self.folder_tree.setHeaderHidden(True)
        self.folder_tree.setMaximumHeight(150)
        main_layout.addWidget(QLabel("Select Folder:"))
        main_layout.addWidget(self.folder_tree)

        self._build_folder_tree(folders)
        self.folder_tree.setCurrentItem(self.folder_tree.topLevelItem(0))

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=self)
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        main_layout.addWidget(buttons)

        self.delete_btn = QPushButton("Delete Password")
        self.delete_btn.setObjectName("DeleteAccountButton")
        self.delete_btn.clicked.connect(self.on_delete_clicked)
        main_layout.addWidget(self.delete_btn)

        # Generate Password Dialog instance (lazy init)
        self.gen_pw_dialog = None

    def open_generate_password_options(self):
        if self.gen_pw_dialog is None:
            self.gen_pw_dialog = GeneratePasswordDialog(64, self)
            self.gen_pw_dialog.password_generated.connect(self.set_generated_password)
        self.gen_pw_dialog.show()
        self.gen_pw_dialog.raise_()
        self.gen_pw_dialog.activateWindow()

    def set_generated_password(self, pw):
        self.password_edit.setText(pw)
        if not self.toggle_password_btn.isChecked():
            self.password_edit.setEchoMode(QLineEdit.Password)

    def set_entry_id(self, entry_id):
        self.entry_id = entry_id

    def validate_and_accept(self):
        if not self.title_edit.text().strip() or not self.password_edit.text().strip():
            QMessageBox.warning(self, "Missing Fields", "Title and Password are required.")
            return  # Don’t close the dialog
        
        notes = self.notes_edit.toPlainText()
        if len(notes) > 200:
            QMessageBox.warning(self, "Notes Too Long", "Notes cannot exceed 200 characters.")
            return  # Don’t close the dialog
        
        self.accept()


    def toggle_password_visibility(self):
        if self.toggle_password_btn.isChecked():
            self.password_edit.setEchoMode(QLineEdit.Normal)
            self.toggle_password_btn.setText("Hide")
        else:
            self.password_edit.setEchoMode(QLineEdit.Password)
            self.toggle_password_btn.setText("Show")

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

    def on_expiry_option_changed(self, text):
        self.custom_date_edit.setEnabled(text == "Custom Date")

    def get_selected_folder_path(self):
        item = self.folder_tree.currentItem()
        if not item:
            return None
        names = []
        while item and item.data(0, Qt.UserRole) is not None:
            names.insert(0, item.text(0))
            item = item.parent()
        return "/".join(names) if names else None

    def set_data(self, data):
        # data keys: title, username, password, site, notes, password_expiry, folder_path
        self.title_edit.setText(data.get("title", ""))
        self.username_edit.setText(data.get("username", ""))
        self.password_edit.setText(data.get("password", ""))
        self.site_edit.setText(data.get("site", ""))
        self.notes_edit.setPlainText(data.get("notes", ""))

        expiry = data.get("password_expiry")
        if expiry:
            if expiry == "":
                self.expiry_combo.setCurrentText("No Expiry")
                self.custom_date_edit.setEnabled(False)
            else:
                date_obj = QDate.fromString(expiry, "yyyy-MM-dd")
                if not date_obj.isValid():
                    self.expiry_combo.setCurrentText("No Expiry")
                    self.custom_date_edit.setEnabled(False)
                else:
                    today = QDate.currentDate()
                    diff_months = (today.year() - date_obj.year()) * 12 + (today.month() - date_obj.month())
                    if diff_months == -3:
                        self.expiry_combo.setCurrentText("3 Months")
                    elif diff_months == -6:
                        self.expiry_combo.setCurrentText("6 Months")
                    elif diff_months == -12:
                        self.expiry_combo.setCurrentText("12 Months")
                    else:
                        self.expiry_combo.setCurrentText("Custom Date")
                        self.custom_date_edit.setEnabled(True)
                        self.custom_date_edit.setDate(date_obj)
        else:
            self.expiry_combo.setCurrentText("No Expiry")
            self.custom_date_edit.setEnabled(False)

        def find_folder_item(item):
            if self.get_folder_path_from_item(item) == data.get("folder_path"):
                return item
            for i in range(item.childCount()):
                found = find_folder_item(item.child(i))
                if found:
                    return found
            return None

        root = self.folder_tree.topLevelItem(0)
        match = find_folder_item(root)
        if match:
            self.folder_tree.setCurrentItem(match)

    def get_folder_path_from_item(self, item):
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

    def on_delete_clicked(self):
        reply = QMessageBox.question(
            self, "Confirm Delete",
            "Are you sure you want to delete this password entry?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            if self.entry_id is None:
                QMessageBox.critical(self, "Error", "No password entry ID set.")
                return
            try:
                conn = sqlite3.connect("LADOC.db")
                cursor = conn.cursor()
                cursor.execute("DELETE FROM user_passwords WHERE id = ?", (self.entry_id,))
                conn.commit()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete password: {e}")
                return
            finally:
                conn.close()

            self.password_deleted.emit()
