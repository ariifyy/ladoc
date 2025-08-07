from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QMessageBox, QHBoxLayout
from PyQt5.QtCore import pyqtSignal

class EditFolderDialog(QDialog):
    folder_deleted = pyqtSignal()

    def __init__(self, folder_id, folder_name, parent=None):
        super().__init__(parent)
        self.folder_id = folder_id
        self.setWindowTitle("Edit Folder")
        self.init_ui(folder_name)

    def init_ui(self, folder_name):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.name_edit = QLineEdit(folder_name)
        form_layout.addRow("Folder Name:", self.name_edit)

        layout.addLayout(form_layout)

        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.delete_btn = QPushButton("Delete Folder")
        self.cancel_btn = QPushButton("Cancel")

        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addWidget(self.cancel_btn)

        layout.addLayout(btn_layout)

        self.save_btn.clicked.connect(self.save)
        self.delete_btn.clicked.connect(self.delete)
        self.cancel_btn.clicked.connect(self.reject)

    def save(self):
        new_name = self.name_edit.text().strip()
        if not new_name:
            QMessageBox.warning(self, "Invalid Name", "Folder name cannot be empty.")
            return
        self.accept()

    def delete(self):
        confirm = QMessageBox.question(
            self, "Confirm Delete", 
            "Are you sure you want to delete this folder? Password in this folder will not be deleted.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            self.folder_deleted.emit()
            self.accept()

    def get_new_name(self):
        return self.name_edit.text().strip()
