import hashlib
import sqlite3
import requests
import sip  # type: ignore

from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QObject
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit,
    QMessageBox, QHBoxLayout, QFrame
)

from .crypto_utils import get_fernet
from .utilities.db_connection import get_db_path

class PasswordScanWorker(QObject):
    finished = pyqtSignal(str)

    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self._running = True

    def stop(self):
        self._running = False

    def run(self):
        try:
            rows = self._get_decrypted_passwords()
            if not rows:
                self.finished.emit("No saved passwords to scan.")
                return

            breached = self._check_passwords(rows)
            msg = (
                "Breached passwords found:\n" + "\n".join(breached)
                if breached else "All saved passwords appear safe."
            )
            self.finished.emit(msg)

        except Exception as e:
            self.finished.emit(f"Error: {str(e)}")

    def _get_decrypted_passwords(self):
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute("SELECT site, password FROM user_passwords WHERE user_id = ?", (self.user_id,))
        encrypted_rows = cursor.fetchall()
        conn.close()

        fernet = get_fernet()
        decrypted = []
        for site, pwd in encrypted_rows:
            try:
                password = fernet.decrypt(pwd.encode()).decode()
                decrypted.append((site, password))
            except Exception:
                continue
        return decrypted

    def _check_passwords(self, rows):
        breached = []
        for site, pwd in rows:
            if not self._running:
                break
            count = self._check_password_breach(pwd)
            if count > 0:
                breached.append(f"{site}: {count} times")
        return breached

    def _check_password_breach(self, password):
        sha1 = hashlib.sha1(password.encode()).hexdigest().upper()
        prefix, suffix = sha1[:5], sha1[5:]
        try:
            resp = requests.get(f"https://api.pwnedpasswords.com/range/{prefix}")
            if resp.status_code != 200:
                return -1
            return next((int(count) for h, count in (line.split(":") for line in resp.text.splitlines()) if h == suffix), 0)
        except Exception:
            return -1


class WeeklyChecker(QWidget):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.timer = None
        self.scan_thread = None
        self.worker = None
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        title = QLabel("Your passwords to be scanned:")
        title.setFont(QFont("Inter", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        self.password_layout = QVBoxLayout()
        self.populate_passwords(self.password_layout)
        main_layout.addLayout(self.password_layout)

        # Bottom layout to hold the Start Schedule button at the bottom left
        bottom_layout = QHBoxLayout()
        bottom_layout.setAlignment(Qt.AlignLeft)

        self.scheduled_btn = QPushButton("Start Schedule")
        self.scheduled_btn.setCheckable(True)
        self.scheduled_btn.setFont(QFont("Inter", 10))
        self.scheduled_btn.setFixedSize(210, 50)  # Small size
        self.scheduled_btn.clicked.connect(self.toggle_scheduled_scan)
        bottom_layout.addWidget(self.scheduled_btn)

        # Add stretch to push button to the bottom
        main_layout.addStretch()
        main_layout.addLayout(bottom_layout)

        self.setLayout(main_layout)

    def populate_passwords(self, layout):
        try:
            conn = sqlite3.connect(get_db_path())
            cursor = conn.cursor()
            cursor.execute("SELECT site, password FROM user_passwords WHERE user_id = ?", (self.user_id,))
            rows = cursor.fetchall()
            conn.close()

            if not rows:
                layout.addWidget(self._label("No saved passwords."))
                return

            fernet = get_fernet()
            for site, encrypted_pwd in rows:
                try:
                    pwd = fernet.decrypt(encrypted_pwd.encode()).decode()
                    layout.addWidget(self.password_row(site, pwd))
                    layout.addWidget(self.divider())
                except Exception:
                    continue

        except Exception as e:
            QMessageBox.critical(self, "Error", f"DB Error: {str(e)}")

    def _label(self, text):
        label = QLabel(text)
        label.setAlignment(Qt.AlignCenter)
        return label

    def divider(self):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        return line

    def password_row(self, site, pwd):
        layout = QHBoxLayout()

        site_label = QLabel(f"{site}:")
        pwd_field = QLineEdit(pwd)
        pwd_field.setEchoMode(QLineEdit.Password)
        pwd_field.setReadOnly(True)

        toggle_btn = QPushButton("Show")
        toggle_btn.setCheckable(True)
        toggle_btn.clicked.connect(lambda checked: self.toggle_password(checked, pwd_field, toggle_btn))

        layout.addWidget(site_label)
        layout.addWidget(pwd_field)
        layout.addWidget(toggle_btn)

        # Grey background container
        container = QWidget()
        container.setLayout(layout)
        container.setStyleSheet("background-color: #3A3A3A; padding: 5px; border-radius: 4px;")
        return container

    def toggle_password(self, checked, field, btn):
        field.setEchoMode(QLineEdit.Normal if checked else QLineEdit.Password)
        btn.setText("Hide" if checked else "Show")

    def toggle_scheduled_scan(self, checked):
        self.scheduled_btn.setText("Stop Schedule" if checked else "Start Schedule")
        self.start_timer() if checked else self.stop_timer()

    def start_timer(self):
        if not self.timer:
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.run_scan)
            self.timer.start(5000)  # Replace with weekly interval in real use

    def run_scan(self):
        if self.scan_thread and self.scan_thread.isRunning():
            return

        self.scan_thread = QThread()
        self.worker = PasswordScanWorker(self.user_id)
        self.worker.moveToThread(self.scan_thread)

        self.scan_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.scan_complete)
        self.worker.finished.connect(self.worker.deleteLater)
        self.scan_thread.finished.connect(self.scan_thread.deleteLater)

        self.scan_thread.start()

    def scan_complete(self, msg):
        QMessageBox.information(self, "Weekly Scan Result", msg)

    def stop_timer(self):
        if self.timer:
            self.timer.stop()
            self.timer = None

        if self.worker and not sip.isdeleted(self.worker):
            self.worker.stop()
            self.worker = None

        if self.scan_thread and self.scan_thread.isRunning():
            self.scan_thread.quit()
            self.scan_thread.wait()
            self.scan_thread = None
