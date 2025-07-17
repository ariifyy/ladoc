from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QMessageBox, QHBoxLayout
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QObject
import sqlite3
import hashlib
import requests
import time


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
            conn = sqlite3.connect("LADOC.db")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT site, password FROM user_passwords WHERE user_id = ?
            """, (self.user_id,))
            rows = cursor.fetchall()
            conn.close()

            if not rows:
                self.finished.emit("No saved passwords to scan.")
                return

            breached = []
            for site, pwd in rows:
                if not self._running:
                    return
                count = self.check_password_breach(pwd)
                if count > 0:
                    breached.append(f"{site}: {count} times")

            if breached:
                msg = "Breached passwords found:\n" + "\n".join(breached)
            else:
                msg = "All saved passwords appear safe."

            self.finished.emit(msg)

        except Exception as e:
            self.finished.emit(f"Error: {str(e)}")

    def check_password_breach(self, password):
        sha1 = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
        prefix, suffix = sha1[:5], sha1[5:]
        url = f"https://api.pwnedpasswords.com/range/{prefix}"
        try:
            resp = requests.get(url)
            if resp.status_code != 200:
                return -1
            hashes = (line.split(":") for line in resp.text.splitlines())
            for h, count in hashes:
                if h == suffix:
                    return int(count)
            return 0
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
        layout = QVBoxLayout()

        # Title
        title = QLabel("Weekly Password Checker")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Scheduled Scan Toggle
        self.scheduled_btn = QPushButton("Enable Scheduled Scan")
        self.scheduled_btn.setCheckable(True)
        self.scheduled_btn.clicked.connect(self.toggle_scheduled_scan)
        layout.addWidget(self.scheduled_btn)

        # Password List
        try:
            conn = sqlite3.connect("LADOC.db")
            cursor = conn.cursor()
            cursor.execute("SELECT site, password FROM user_passwords WHERE user_id = ?", (self.user_id,))
            rows = cursor.fetchall()
            conn.close()

            if not rows:
                no_data = QLabel("No saved passwords.")
                no_data.setAlignment(Qt.AlignCenter)
                layout.addWidget(no_data)
            else:
                for site, pwd in rows:
                    entry_layout = QHBoxLayout()

                    site_label = QLabel(f"{site}:")
                    pwd_field = QLineEdit(pwd)
                    pwd_field.setEchoMode(QLineEdit.Password)
                    pwd_field.setReadOnly(True)
                    toggle_btn = QPushButton("Show")
                    toggle_btn.setCheckable(True)

                    toggle_btn.clicked.connect(
                        lambda checked, field=pwd_field, btn=toggle_btn: self.toggle_password(checked, field, btn)
                    )

                    entry_layout.addWidget(site_label)
                    entry_layout.addWidget(pwd_field)
                    entry_layout.addWidget(toggle_btn)

                    layout.addLayout(entry_layout)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"DB Error: {str(e)}")

        self.setLayout(layout)

    def toggle_password(self, checked, field, btn):
        if checked:
            field.setEchoMode(QLineEdit.Normal)
            btn.setText("Hide")
        else:
            field.setEchoMode(QLineEdit.Password)
            btn.setText("Show")

    def toggle_scheduled_scan(self):
        if self.scheduled_btn.isChecked():
            self.scheduled_btn.setText("Disable Scheduled Scan")
            self.start_timer()
        else:
            self.scheduled_btn.setText("Enable Scheduled Scan")
            self.stop_timer()

    def start_timer(self):
        if not self.timer:
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.run_scan)
            self.timer.start(5000)  # For demo: 5s → replace with 7*24*3600*1000 for weekly

    def stop_timer(self):
        if self.timer:
            self.timer.stop()
            self.timer = None
        if self.worker:
            self.worker.stop()
        if self.scan_thread:
            self.scan_thread.quit()
            self.scan_thread.wait()

    def run_scan(self):
        self.scan_thread = QThread()
        self.worker = PasswordScanWorker(self.user_id)
        self.worker.moveToThread(self.scan_thread)

        self.scan_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.scan_complete)
        self.worker.finished.connect(self.scan_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.scan_thread.finished.connect(self.scan_thread.deleteLater)

        self.scan_thread.start()

    def scan_complete(self, msg):
        QMessageBox.information(self, "Weekly Scan Result", msg)
