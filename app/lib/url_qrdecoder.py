import re, requests, webbrowser, base64, time
from urllib.parse import urlparse
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTextBrowser, QFileDialog, QMessageBox, QFrame, QApplication
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PIL import Image
from pyzbar.pyzbar import decode


class ClickableLabel(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked()

    def clicked(self):
        pass


class QRDecoderPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.initUI()
        self.vt_api_key = "afaf6bde567fcd2cef97466d41f408fbbb89e24a53cad5ea53afbe529f103604"

    def initUI(self):
        layout = QVBoxLayout()

        # --- Top Row: URL Entry and Analyze ---
        top_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter URL or decode from QR...")
        top_layout.addWidget(self.url_input)

        self.browse_btn = QPushButton("Browse")
        self.browse_btn.clicked.connect(self.open_file)
        top_layout.addWidget(self.browse_btn)

        self.analyze_btn = QPushButton("Analyze")
        self.analyze_btn.clicked.connect(self.handle_analysis)
        top_layout.addWidget(self.analyze_btn)

        layout.addLayout(top_layout)

        # --- Drag and Drop QR Image ---
        self.drop_label = ClickableLabel("Drag & drop QR code image here")
        self.drop_label.clicked = self.open_file
        self.drop_label.setAlignment(Qt.AlignCenter)
        self.drop_label.setStyleSheet("border: 2px dashed gray; padding: 20px;")
        layout.addWidget(self.drop_label)

        # --- Utility Buttons: CheckShortURL Only ---
        utility_layout = QHBoxLayout()
        
        self.vt_btn = QPushButton("Scan with VirusTotal")
        self.vt_btn.clicked.connect(self.scan_with_virustotal)
        utility_layout.addWidget(self.vt_btn)

        self.shorturl_btn = QPushButton("Unshorten a link")
        self.shorturl_btn.clicked.connect(self.open_checkshorturl)
        utility_layout.addWidget(self.shorturl_btn)

        layout.addLayout(utility_layout)

        self.output = QTextBrowser()
        layout.addWidget(self.output)

        self.setLayout(layout)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.lower().endswith((".png", ".jpg", ".jpeg")):
                self.decode_qr_image(file_path)
                return

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open QR Code Image", "", "Images (*.png *.jpg *.jpeg)"
        )
        if file_path:
            self.decode_qr_image(file_path)

    def decode_qr_image(self, file_path):
        try:
            image = Image.open(file_path)
            decoded_objects = decode(image)
            if decoded_objects:
                qr_data = decoded_objects[0].data.decode("utf-8")
                self.url_input.setText(qr_data)
            else:
                QMessageBox.warning(self, "QR Decode Error", "No QR code found in the image.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to decode image:\n{str(e)}")

    def handle_analysis(self):
        url = self.url_input.text().strip()
        self.output.clear()

        if not url:
            self.output.setText("No URL found to analyze.")
            return

        if not self.is_valid_url(url):
            self.output.setText(
                "Invalid URL format. Please enter a valid URL starting with http:// or https://.\n"
                "If you're sure the link is correct, proceed with caution as it may be suspicious."
            )
            return

        self.output.setHtml(f"<em>Analyzing {url}...</em>")
        results = self.analyze_url(url)
        self.display_results(url, results)

    def is_valid_url(self, url):
        try:
            parsed = urlparse(url)
            return parsed.scheme in ["http", "https"] and bool(parsed.netloc)
        except:
            return False

    def analyze_url(self, url):
        results = []
        parsed = urlparse(url)
        hostname = parsed.hostname or ""

        if url.startswith("https://"):
            results.append(("Uses HTTPS", "pass", "Uses secure HTTPS protocol."))
        elif url.startswith("http://"):
            results.append(("Uses HTTP", "warn", "Uses insecure HTTP protocol."))

        # Fix IP regex pattern (raw string with single \d)
        ip_like_pattern = re.compile(
            r"\b((25[0-5]|2[0-4]\d|1\d\d|\d\d?)\.){3}(25[0-5]|2[0-4]\d|1\d\d|\d\d?)\b"
        )
        if self.is_valid_ipv4(hostname) or ip_like_pattern.fullmatch(hostname):
            results.append((
                "IP Address in Hostname", "warn",
                "IP address detected in URL hostname. IP-based URLs might be suspicious or unsafe."
            ))
        else:
            results.append(("Domain Format", "pass", "No IP-like patterns detected in hostname."))

        parts = hostname.split(".")
        if self.is_valid_ipv4(hostname):
            results.append(("TLD Check Skipped", "pass", f"Skipped TLD check for IP address: {hostname}"))
        elif len(parts) >= 2:
            tld = parts[-1].lower()
            common_tlds = ["com", "org", "net", "edu", "gov", "sg", "io"]
            if tld not in common_tlds:
                results.append(("Unusual Top-Level Domain", "warn", f"Domain ends in .{tld}, which is uncommon."))
            else:
                results.append(("Recognized Top-Level Domain", "pass", f"Domain ends in .{tld}, a common TLD."))
        else:
            results.append(("TLD Parsing Error", "warn", "Unable to extract TLD."))

        if self.is_valid_ipv4(hostname):
            results.append(("Subdomain Structure", "pass", f"The URL uses a direct IP address: {hostname}"))
        else:
            cleaned_subdomains = self.clean_subdomains(hostname)
            sub_count = len(cleaned_subdomains)
            if sub_count >= 4:
                status, note = "fail", "Many nested subdomains detected."
            elif sub_count >= 2:
                status, note = "warn", "Multiple subdomains found."
            else:
                status, note = "pass", "Subdomain structure appears normal."

            results.append((
                "Subdomain Structure", status,
                f"Detected {sub_count} subdomain level(s).<br>"
                f"Subdomain: {'.'.join(cleaned_subdomains) or '(none)'}<br>"
                f"Main domain: {'.'.join(parts[-2:])}<br>{note}"
            ))

        known_shorteners = [
            "bit.ly", "tinyurl.com", "t.co", "goo.gl", "rebrand.ly",
            "ow.ly", "is.gd", "buff.ly", "shorte.st", "bl.ink"
        ]
        if hostname.lower() in known_shorteners:
            try:
                r = requests.get(f"https://unshorten.me/json/{url}", timeout=5)
                expanded = r.json().get("resolved_url", "(could not resolve)")
            except:
                expanded = "(error expanding URL)"
            results.append(("URL Shortener detected", "warn", f"Shortened domain: {hostname}<br>Expanded: {expanded}"))
        else:
            results.append(("No URL shortener", "pass", "URL does not use a known shortener."))

        phishing_keywords = [
            "login", "verify", "account", "secure", "bank", "webscr", "signin", "redirect",
            "update", "confirm", "validate", "activate", "pay", "password", "wp-admin", "win", "download"
        ]
        lower_url = url.lower()
        found = [kw for kw in phishing_keywords if kw in lower_url]
        if found:
            results.append(("Phishing Keywords", "warn", f"Suspicious keywords found: {', '.join(found)}"))
        else:
            results.append(("No Phishing Keywords", "pass", "No suspicious keywords in URL."))

        return results

    def is_valid_ipv4(self, ip):
        parts = ip.split('.')
        return len(parts) == 4 and all(part.isdigit() and 0 <= int(part) <= 255 for part in parts)

    def clean_subdomains(self, hostname):
        parts = hostname.split(".")
        subdomains = parts[:-2] if len(parts) >= 2 else []
        cleaned = []
        i = 0
        while i < len(subdomains):
            candidate = ".".join(subdomains[i:i+4])
            if self.is_valid_ipv4(candidate):
                cleaned.append(candidate)
                i += 4
            else:
                cleaned.append(subdomains[i])
                i += 1
        return cleaned

    def display_results(self, url, results):
        html = f"<div style='margin-bottom: 1em;'><strong>Analyzing:</strong> {url}</div>"
        color_map = {
            "pass": "limegreen",
            "warn": "orange",
            "fail": "red"
        }

        for name, status, message in results:
            color = color_map.get(status, "gray")
            html += f"<div style='margin-bottom: 0.5em;'>"
            html += f"<b style='color:{color}'>{name}</b><br>{message}</div>"

        self.output.setHtml(html)

    def open_checkshorturl(self):
        webbrowser.open("https://checkshorturl.com")


    def scan_with_virustotal(self):
        url = self.url_input.text().strip()
        self.output.clear()

        if not url:
            QMessageBox.warning(self, "No URL", "Please enter a URL to scan.")
            return

        try:
            headers = {
                "x-apikey": self.vt_api_key
            }

            self.output.setHtml(f"<b>VirusTotal Scan Results:</b><br><em>Submitting and scanning URL...</em>")
            QApplication.processEvents()

            # Submit URL for scanning
            data = {"url": url}
            submit_resp = requests.post("https://www.virustotal.com/api/v3/urls", headers=headers, data=data)
            if submit_resp.status_code != 200:
                self.output.setHtml(f"<b>VirusTotal Scan Results:</b><br><span style='color:red;'>Failed to submit URL: {submit_resp.text}</span>")
                return

            # Encode the URL to get its scan ID
            url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")

            # Wait and fetch the analysis
            self.output.setHtml(f"<b>VirusTotal Scan Results:</b><br><em>Waiting for results...</em>")
            QApplication.processEvents()
            time.sleep(5)

            analysis_url = f"https://www.virustotal.com/api/v3/urls/{url_id}"
            result_resp = requests.get(analysis_url, headers=headers)
            if result_resp.status_code != 200:
                self.output.setHtml(f"<b>VirusTotal Scan Results:</b><br><span style='color:red;'>Failed to retrieve results: {result_resp.text}</span>")
                return

            result_data = result_resp.json()
            stats = result_data.get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
            total = sum(stats.values())
            malicious = stats.get("malicious", 0)
            suspicious = stats.get("suspicious", 0)
            harmless = stats.get("harmless", 0)
            undetected = stats.get("undetected", 0)
            timeout = stats.get("timeout", 0)

            score = malicious + suspicious

            # Basic rating
            if malicious > 0:
                rating = f"<span style='color:red;'><b>High Risk</b></span>"
            elif suspicious > 0:
                rating = f"<span style='color:orange;'><b>Potentially Suspicious</b></span>"
            elif harmless > 0 and malicious == 0 and suspicious == 0:
                rating = f"<span style='color:green;'><b>Likely Safe</b></span>"
            else:
                rating = f"<b>Unknown</b>"

            summary_html = f"""
            <b>VirusTotal Scan Summary:</b><br>
            <b>Risk Rating:</b> {rating}<br>
            <ul>
                <li><b>Malicious:</b> {malicious}</li>
                <li><b>Suspicious:</b> {suspicious}</li>
                <li><b>Harmless:</b> {harmless}</li>
                <li><b>Undetected:</b> {undetected}</li>
                <li><b>Timeout:</b> {timeout}</li>
            </ul>
            """


            self.output.setHtml(summary_html)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred:\n{str(e)}")
