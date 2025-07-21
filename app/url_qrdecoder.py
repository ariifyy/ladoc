import sys
import cv2
import threading
from PyQt5.QtCore import Qt, QMimeData, QTimer, QUrl
from PyQt5.QtGui import QPixmap, QImage, QDragEnterEvent, QDropEvent, QDesktopServices
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog,
    QHBoxLayout, QTextBrowser, QMessageBox
)
from pyzbar.pyzbar import decode
from PIL import Image


class QRDecoderPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

        self.camera_active = False
        self.capture = None

        self.image_label = QLabel("Drag and drop an image or click to upload")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("border: 2px dashed gray; padding: 2rem;")
        self.image_label.setFixedHeight(250)

        self.result_browser = QTextBrowser()
        self.result_browser.setOpenExternalLinks(True)

        self.upload_button = QPushButton("Browse File")
        self.upload_button.clicked.connect(self.load_image)

        self.start_camera_button = QPushButton("Start Camera Scan")
        self.start_camera_button.clicked.connect(self.toggle_camera)

        self.rescan_button = QPushButton("Scan Again")
        self.rescan_button.clicked.connect(self.clear_result)
        self.rescan_button.setVisible(False)

        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        layout.addWidget(self.result_browser)

        button_row = QHBoxLayout()
        button_row.addWidget(self.upload_button)
        button_row.addWidget(self.start_camera_button)
        button_row.addWidget(self.rescan_button)
        layout.addLayout(button_row)

        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.process_camera_frame)

    def load_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
        if file_name:
            self.process_image(file_name)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path:
                self.process_image(file_path)

    def process_image(self, path):
        self.clear_result()
        image = Image.open(path)
        decoded_objects = decode(image)

        if decoded_objects:
            for obj in decoded_objects:
                data = obj.data.decode("utf-8")
                self.show_result(data)
        else:
            self.result_browser.setText("No QR code found in the image.")

        pixmap = QPixmap(path).scaledToHeight(250, Qt.SmoothTransformation)
        self.image_label.setPixmap(pixmap)

    def toggle_camera(self):
        if self.camera_active:
            self.stop_camera()
        else:
            self.start_camera()

    def start_camera(self):
        self.capture = cv2.VideoCapture(0)
        if not self.capture.isOpened():
            QMessageBox.warning(self, "Camera Error", "Unable to access the camera.")
            return

        self.camera_active = True
        self.timer.start(30)
        self.start_camera_button.setText("Stop Camera")
        self.rescan_button.setVisible(False)

    def stop_camera(self):
        self.timer.stop()
        if self.capture:
            self.capture.release()
        self.camera_active = False
        self.start_camera_button.setText("Start Camera Scan")

    def process_camera_frame(self):
        if not self.capture:
            return

        ret, frame = self.capture.read()
        if not ret:
            return

        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, channel = rgb_image.shape
        bytes_per_line = channel * width
        q_image = QImage(rgb_image.data, width, height, bytes_per_line, QImage.Format_RGB888)
        self.image_label.setPixmap(QPixmap.fromImage(q_image).scaledToHeight(250, Qt.SmoothTransformation))

        decoded_objects = decode(frame)
        if decoded_objects:
            self.timer.stop()
            for obj in decoded_objects:
                data = obj.data.decode("utf-8")
                self.show_result(data)
                break  # Only handle one result per scan
            self.rescan_button.setVisible(True)

    def show_result(self, data):
        if data.startswith("http"):
            self.result_browser.setHtml(f"<strong>QR Code Content:</strong><br><a href='{data}'>{data}</a>")
        else:
            self.result_browser.setHtml(f"<strong>QR Code Content:</strong><br>{data}")

    def clear_result(self):
        self.result_browser.clear()
        self.rescan_button.setVisible(False)
        if not self.camera_active:
            self.image_label.setText("Drag and drop an image or click to upload")


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = QRDecoderPage()
    window.resize(600, 500)
    window.show()
    sys.exit(app.exec_())
