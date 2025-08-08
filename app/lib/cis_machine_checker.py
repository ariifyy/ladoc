import os
import subprocess
import ctypes
import sys

from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout,
    QMessageBox, QApplication
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt



class CISLauncher(QWidget):
    def __init__(self):
        super().__init__()
        self.cis_script = None  # Path to the .bat file
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Like a Deck of Cards")
        layout = QVBoxLayout()

        # Title
        title = QLabel("Apply CIS Windows Hardening")
        title.setFont(QFont("Inter", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Warning
        warning = QLabel("⚠️ Please ensure only one `.bat` file is in the CIS folder.")
        warning.setFont(QFont("Inter", 10))
        warning.setAlignment(Qt.AlignCenter)
        warning.setStyleSheet("color: orange;")
        layout.addWidget(warning)

        # Description
        desc = QLabel("Click a button below to run the CIS security-hardening script "
                      "or open its folder.\nRequires administrator privileges.")
        desc.setFont(QFont("Inter", 11))
        desc.setAlignment(Qt.AlignCenter)
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Buttons
        run_button = QPushButton("Run CIS Script")
        run_button.setFont(QFont("Inter", 12, QFont.Bold))
        run_button.setToolTip("Runs the .bat file inside the CIS folder")
        run_button.clicked.connect(self.run_cis_script)
        run_button.setFixedWidth(300)
        run_button.setStyleSheet("padding: 10px;")
        layout.addWidget(run_button, alignment=Qt.AlignCenter)

        open_folder_button = QPushButton("Open Script Folder")
        open_folder_button.setFont(QFont("Inter", 12))
        open_folder_button.setToolTip("Opens the CIS script folder")
        open_folder_button.clicked.connect(self.open_script_folder)
        open_folder_button.setFixedWidth(300)
        open_folder_button.setStyleSheet("padding: 10px;")
        layout.addWidget(open_folder_button, alignment=Qt.AlignCenter)

        # Footer
        self.footer_label = QLabel()
        self.footer_label.setFont(QFont("Inter", 9))
        self.footer_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.footer_label)

        self.setLayout(layout)
        self.setMinimumWidth(400)

        # Locate the script
        self.locate_script()

    def locate_script(self):
        """Locate the .bat file in the CIS directory and update footer label."""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        cis_dir = os.path.join(base_dir, "CIS")

        if not os.path.isdir(cis_dir):
            self.footer_label.setText("❌ CIS folder not found.")
            return

        bat_files = [f for f in os.listdir(cis_dir) if f.lower().endswith(".bat")]

        if len(bat_files) == 1:
            self.cis_script = os.path.join(cis_dir, bat_files[0])
            self.footer_label.setText(f"✅ Script Found: {bat_files[0]}")
        elif len(bat_files) == 0:
            self.footer_label.setText("❌ No .bat script found in CIS folder.")
        else:
            self.footer_label.setText("⚠️ Multiple .bat files found in CIS folder.")

    def run_cis_script(self):
        if not self.cis_script or not os.path.isfile(self.cis_script):
            QMessageBox.critical(self, "Error", "Valid CIS script not found.")
            return

        try:
            # Request administrator privileges and run the .bat script
            ret = ctypes.windll.shell32.ShellExecuteW(
                None, "runas", "cmd.exe", f'/c "{self.cis_script}"', None, 1
            )
            if ret <= 32:
                QMessageBox.critical(self, "Error", "Failed to launch script with admin privileges.")
            else:
                QMessageBox.information(self, "Success", "CIS hardening script launched with admin privileges.")
        except Exception as e:
            QMessageBox.critical(self, "Exception", f"An error occurred:\n{str(e)}")


    def open_script_folder(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        cis_folder = os.path.join(base_dir, "CIS")
        if os.path.isdir(cis_folder):
            try:
                os.startfile(cis_folder)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not open folder:\n{str(e)}")
        else:
            QMessageBox.critical(self, "Error", "CIS folder does not exist.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CISLauncher()
    window.show()
    sys.exit(app.exec_())