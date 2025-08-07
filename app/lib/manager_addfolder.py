from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QHBoxLayout, QMessageBox

class AddFolderDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Folder")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.name_edit = QLineEdit()
        form_layout.addRow("Folder Name:", self.name_edit)

        layout.addLayout(form_layout)

        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add")
        self.cancel_btn = QPushButton("Cancel")

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.cancel_btn)

        layout.addLayout(btn_layout)

        self.add_btn.clicked.connect(self.on_add)
        self.cancel_btn.clicked.connect(self.reject)

    def on_add(self):
        folder_name = self.name_edit.text().strip()
        if not folder_name:
            QMessageBox.warning(self, "Invalid Input", "Folder name cannot be empty.")
            return
        self.accept()

    def get_folder_name(self):
        return self.name_edit.text().strip()
