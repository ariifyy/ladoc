import sys
import hashlib
import requests
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QFileDialog, QHBoxLayout, QMessageBox,
    QApplication, QFrame, QScrollArea
)


class FileDropLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.parent().load_file()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path:
                self.parent().scan_file(file_path)


class VirusTotalScanner(QWidget):
    def __init__(self, user_id, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.api_key = "d274dafa9ff2a0472544fe895f2264f9445116f33632266f752e2dee1a7645a4"

        # Upload label (click + drag/drop)
        self.file_label = FileDropLabel(self)
        self.file_label.setText("Drag and drop a file or click to upload")
        self.file_label.setAlignment(Qt.AlignCenter)
        self.file_label.setFont(QFont("Inter", 12))
        self.file_label.setStyleSheet("border: 2px dashed gray; padding: 2rem;")
        self.file_label.setFixedHeight(250)

        # Result display elements
        self.result_browser = QLabel()
        self.result_browser.setFont(QFont("Inter", 12))
        self.result_browser.setWordWrap(True)
        self.result_browser.setTextInteractionFlags(Qt.TextSelectableByMouse)

        self.result_detail = QLabel()
        self.result_detail.setFont(QFont("Inter", 12))
        self.result_detail.setWordWrap(True)
        self.result_detail.setTextInteractionFlags(Qt.TextSelectableByMouse)

        # Box to hold the result content
        self.result_box = QFrame()
        self.result_box.setStyleSheet("""
            background-color: #3A3A3A;
            border: 1px solid gray;
            border-radius: 5px;
            padding: 10px;
        """)
        result_layout = QVBoxLayout()
        result_layout.addWidget(self.result_browser)
        result_layout.addWidget(self.result_detail)
        self.result_box.setLayout(result_layout)

        # Scroll area for results
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFixedHeight(200)
        self.scroll_area.setStyleSheet("border: none;")
        self.scroll_area.setWidget(self.result_box)

        # Buttons
        self.upload_button = QPushButton("Browse File")
        self.upload_button.setFont(QFont("Inter", 12))
        self.upload_button.setFixedHeight(50)
        self.upload_button.clicked.connect(self.load_file)

        self.rescan_button = QPushButton("Scan Another File")
        self.rescan_button.setFont(QFont("Inter", 12))
        self.rescan_button.setFixedHeight(50)
        self.rescan_button.clicked.connect(self.clear_result)
        self.rescan_button.setVisible(False)

        # Main layout
        layout = QVBoxLayout()
        layout.addWidget(self.file_label)
        layout.addWidget(self.scroll_area)

        button_row = QHBoxLayout()
        button_row.addWidget(self.upload_button)
        button_row.addWidget(self.rescan_button)
        layout.addLayout(button_row)

        self.setLayout(layout)

    def load_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open File", "")
        if file_name:
            self.scan_file(file_name)

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
                stats = data['data']['attributes']['last_analysis_stats']
                malicious_count = stats['malicious']
                total_count = sum(stats.values())
                self.result_browser.setText(
                    f"<b>VirusTotal Scan Result:</b>\nMalicious: {malicious_count} / {total_count}"
                )

                if malicious_count == 0:
                    self.result_detail.setText("✅ No malicious detections found.")
                elif malicious_count <= 2:
                    self.result_detail.setText("⚠️ Low Risk")
                elif malicious_count <= 5:
                    self.result_detail.setText("⚠️ Medium Risk")
                else:
                    self.result_detail.setText("🚨 High Risk")
            else:
                self.result_browser.setText(
                    f"File not found in VirusTotal DB. You may upload it for scanning.\n\n"
                    f"Status Code: {response.status_code}\n{response.text}"
                )
                self.result_detail.setText("Need to upload the file in VirusTotal website.")


        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to scan file:\n{str(e)}")

        self.rescan_button.setVisible(True)

    def clear_result(self):
        self.result_browser.clear()
        self.result_detail.clear()
        self.rescan_button.setVisible(False)
        self.file_label.setText("Drag and drop a file or click to upload")

