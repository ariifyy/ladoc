import sys
import hashlib
import requests
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QFileDialog, QHBoxLayout, QTextBrowser, QMessageBox, QApplication
)

class VirusTotalScanner(QWidget):
    def __init__(self, user_id, parent=None):
        super().__init__(parent)
        self.user_id = user_id

        self.api_key = "d274dafa9ff2a0472544fe895f2264f9445116f33632266f752e2dee1a7645a4"

        self.file_label = QLabel("Drag and drop a file or click to upload")
        self.file_label.setAlignment(Qt.AlignCenter)
        self.file_label.setStyleSheet("border: 2px dashed gray; padding: 2rem;")
        self.file_label.setFixedHeight(250)

        self.result_browser = QTextBrowser()

        self.upload_button = QPushButton("Browse File")
        self.upload_button.clicked.connect(self.load_file)

        self.rescan_button = QPushButton("Scan Another File")
        self.rescan_button.clicked.connect(self.clear_result)
        self.rescan_button.setVisible(False)

        layout = QVBoxLayout()
        layout.addWidget(self.file_label)
        layout.addWidget(self.result_browser)

        button_row = QHBoxLayout()
        button_row.addWidget(self.upload_button)
        button_row.addWidget(self.rescan_button)
        layout.addLayout(button_row)

        self.setLayout(layout)

    def load_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open File", "")
        if file_name:
            self.scan_file(file_name)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path:
                self.scan_file(file_path)

    def scan_file(self, path):
        self.clear_result()
        try:
            with open(path, "rb") as f:
                file_data = f.read()
                file_hash = hashlib.sha256(file_data).hexdigest()

            self.file_label.setText(f"Selected File:\n{path}")

            headers = {
                "accept": "application/json",
                "x-apikey": self.api_key
            }
            url = f"https://www.virustotal.com/api/v3/files/{file_hash}"
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                malicious_count = data['data']['attributes']['last_analysis_stats']['malicious']
                total_count = sum(data['data']['attributes']['last_analysis_stats'].values())
                self.result_browser.setText(f"VirusTotal Scan Result:\nMalicious: {malicious_count} / {total_count}")
            else:
                self.result_browser.setText(f"File not found in VirusTotal DB. You may upload it for scanning.\nStatus Code: {response.status_code}\n{response.text}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to scan file: {str(e)}")

        self.rescan_button.setVisible(True)

    def clear_result(self):
        self.result_browser.clear()
        self.rescan_button.setVisible(False)
        self.file_label.setText("Drag and drop a file or click to upload")

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = VirusTotalScanner()
#     window.resize(600, 500)
#     window.show()
#     sys.exit(app.exec_())
