from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout,
    QLineEdit, QPushButton, QTextEdit
)
from PyQt5.QtCore import Qt
import requests

class EmailBreachChecker(QWidget):
    """
    A QWidget that allows the user to check if an email has been breached,
    using the XposedOrNot API. Built for desktop version of the app.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Email Breach Checker")

        layout = QVBoxLayout()

        # Title
        title_label = QLabel("Enter your email to check for breaches:")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Input field
        self.email_input = QLineEdit()
        layout.addWidget(self.email_input)

        # Button
        check_button = QPushButton("Check Email")
        check_button.clicked.connect(self.check_email)
        layout.addWidget(check_button)

        # Results display
        self.result_box = QTextEdit()
        self.result_box.setReadOnly(True)
        layout.addWidget(self.result_box)

        self.setLayout(layout)

    def check_email(self):
        """
        Sends a GET request to XposedOrNot API with the given email.
        Displays the breach status in the result box.
        """

        email = self.email_input.text().strip()
        if not email:
            self.result_box.setText("⚠️ Please enter an email address.")
            return

        self.result_box.setText("🔎 Checking...")
        try:
            url = f"https://api.xposedornot.com/v1/check-email/{email}"
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                if data.get("breaches"):
                    breaches = "\n".join(data["breaches"])
                    self.result_box.setText(f"🚨 Breaches found:\n{breaches}")
                else:
                    self.result_box.setText(f"✅ No breaches found for {email}.")
            else:
                self.result_box.setText(f"❌ Error: {response.status_code}")
        except Exception as e:
            self.result_box.setText(f"❌ Exception: {str(e)}")
