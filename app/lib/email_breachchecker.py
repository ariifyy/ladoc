from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout,
    QLineEdit, QPushButton, QTextEdit
)

from PyQt5.QtGui import QFont
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
        title_label.setFont(QFont("Inter", 16, QFont.Bold))
        layout.addWidget(title_label)

        # Input field
        self.email_input = QLineEdit()
        layout.addWidget(self.email_input)

        # Button
        check_button = QPushButton("Check Email")
        check_button.setFont(QFont("Inter", 12))
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
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                breaches = data.get("breaches", [])

                # Flatten the nested list and remove duplicates
                flat_breaches = list(set(item for sublist in breaches for item in sublist))

                if flat_breaches:
                    breach_text = "\n".join(flat_breaches)
                    count = len(flat_breaches)
                    self.result_box.setText(f"🚨 {count} Breach(es) found:\n{breach_text}")
                else:
                    self.result_box.setText(f"✅ No breaches found for {email}.")
            else:
                self.result_box.setText(f"❌ Error: {response.status_code} - {response.reason}")
        except requests.exceptions.Timeout:
            self.result_box.setText("❌ Error: Request timed out.")
        except requests.exceptions.RequestException as e:
            self.result_box.setText(f"❌ Request Error: {str(e)}")
        except Exception as e:
            self.result_box.setText(f"❌ Unexpected Error: {str(e)}")

