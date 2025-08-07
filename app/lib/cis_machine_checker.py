import os
import subprocess
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout,
    QMessageBox, QApplication
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import sys


class CISLauncher(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Like a Deck of Cards")
        layout = QVBoxLayout()

        # Title
        title = QLabel("Apply CIS Windows Hardening")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Instruction Label
        desc = QLabel("Click a button below to run the CIS security-hardening script "
                      "or open its folder.\nRequires administrator privileges.")
        desc.setFont(QFont("Arial", 11))
        desc.setAlignment(Qt.AlignCenter)
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Run Script Button
        run_button = QPushButton("Run CIS Script")
        run_button.setFont(QFont("Arial", 12, QFont.Bold))
        run_button.setToolTip("Runs cis_hardening.bat to apply CIS security policies")
        run_button.clicked.connect(self.run_cis_script)
        run_button.setFixedWidth(200)
        run_button.setStyleSheet("padding: 10px;")
        layout.addWidget(run_button, alignment=Qt.AlignCenter)

        # Open Folder Button
        open_folder_button = QPushButton("Open Script Folder")
        open_folder_button.setFont(QFont("Arial", 12))
        open_folder_button.setToolTip("Opens the folder containing cis_hardening.bat")
        open_folder_button.clicked.connect(self.open_script_folder)
        open_folder_button.setFixedWidth(200)
        open_folder_button.setStyleSheet("padding: 10px;")
        layout.addWidget(open_folder_button, alignment=Qt.AlignCenter)

        # Footer Label
        footer = QLabel("Script: cis_hardening.bat")
        footer.setFont(QFont("Arial", 9))
        footer.setAlignment(Qt.AlignCenter)
        layout.addWidget(footer)

        self.setLayout(layout)
        self.setMinimumWidth(400)

    def run_cis_script(self):
        script_path = os.path.join(os.path.dirname(__file__), "cis_hardening.bat")
        if not os.path.isfile(script_path):
            QMessageBox.critical(self, "Error", "Could not find cis_hardening.bat in the current directory.")
            return

        try:
            result = subprocess.run(
                ['cmd', '/c', script_path],
                capture_output=True,
                text=True,
                shell=True
            )

            if result.returncode == 0:
                QMessageBox.information(self, "Success", "CIS hardening script ran successfully.")
            else:
                QMessageBox.warning(self, "Script Error",
                                    f"The script exited with code {result.returncode}.\n\n{result.stderr}")
        except Exception as e:
            QMessageBox.critical(self, "Exception", f"An unexpected error occurred:\n{str(e)}")

    def open_script_folder(self):
        folder_path = os.path.dirname(os.path.abspath(__file__))
        if os.path.isdir(folder_path):
            try:
                os.startfile(folder_path)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not open folder:\n{str(e)}")
        else:
            QMessageBox.critical(self, "Error", "Folder does not exist.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CISLauncher()
    window.show()
    sys.exit(app.exec_())
