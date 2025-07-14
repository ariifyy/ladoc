import sys, os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget, QWidget, QVBoxLayout, QLabel,
    QPushButton, QHBoxLayout, QSizePolicy, QScrollArea, QFrame
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QPropertyAnimation

from fonts import load_inter_fonts  # Make sure this file exists
from themes import dark_theme, light_theme
from auth_pages.login_page import LoginPage
from auth_pages.signup_page import SignupPage
from password_manager import PasswordManagerWidget
from password_haveibeenpwned import HaveIBeenPwnedWidget
from password_checkstrength import PasswordStrengthWidget
from password_recommend import PasswordGeneratorWidget
from cis_machine_checker import CISLauncher


from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Like a Deck of Cards")
        self.resize(1200, 720)

        # Center the window on the screen using QScreen
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        window_geometry = self.frameGeometry()
        window_geometry.moveCenter(screen_geometry.center())
        self.move(window_geometry.topLeft())


        self.current_theme = "dark"
        self.themes = {"dark": dark_theme, "light": light_theme}
        self.apply_stylesheet()

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.login_page = LoginPage(self.show_signup, self.show_homepage)
        self.signup_page = SignupPage(self.show_login)

        self.stack.addWidget(self.login_page)
        self.stack.addWidget(self.signup_page)
        self.stack.setCurrentWidget(self.login_page)

    def apply_stylesheet(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        qss_path = os.path.join(base_dir, "style.qss")
        with open(qss_path, "r") as f:
            qss_template = f.read()
        themed_qss = qss_template % self.themes[self.current_theme]
        self.setStyleSheet(themed_qss)

    def toggle_theme(self):
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        self.apply_stylesheet()

    def setup_tool_home(self, user_id, username):
        self.tool_home = LADCOClandingpage(user_id, username, parent=self)
        self.stack.addWidget(self.tool_home)
        self.stack.setCurrentWidget(self.tool_home)

    def show_signup(self):
        self.stack.setCurrentWidget(self.signup_page)

    def show_login(self):
        self.stack.setCurrentWidget(self.login_page)

    def show_homepage(self, user_id, username):
        self.setup_tool_home(user_id, username)


class CollapsibleSection(QWidget):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.toggle_button = QPushButton(title)
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(False)
        self.toggle_button.setObjectName("SidebarButton")

        self.content_area = QWidget()
        self.content_area.setMaximumHeight(0)
        self.content_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.toggle_button.clicked.connect(self.toggle)

        layout = QVBoxLayout(self)
        layout.addWidget(self.toggle_button)
        layout.addWidget(self.content_area)
        layout.setContentsMargins(0, 0, 0, 0)

        self.toggle_animation = QPropertyAnimation(self.content_area, b"maximumHeight")
        self.toggle_animation.setDuration(200)

    def toggle(self):
        content_height = self.content_area.sizeHint().height()
        if self.toggle_button.isChecked():
            self.toggle_animation.setStartValue(0)
            self.toggle_animation.setEndValue(content_height)
        else:
            self.toggle_animation.setStartValue(content_height)
            self.toggle_animation.setEndValue(0)
        self.toggle_animation.start()

    def add_widget(self, widget):
        content_layout = self.content_area.layout()
        if not content_layout:
            content_layout = QVBoxLayout()
            content_layout.setContentsMargins(10, 0, 0, 0)
            self.content_area.setLayout(content_layout)
        content_layout.addWidget(widget)


class LADCOClandingpage(QWidget):
    def __init__(self, user_id, username, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.username = username

        self.main_layout = QHBoxLayout()
        self.setLayout(self.main_layout)

        self.sidebar = self.build_sidebar()
        self.main_content = QVBoxLayout()

        self.content_widget = QWidget()
        self.content_widget.setLayout(self.main_content)
        self.content_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.content_widget)

        self.show_home_page()

    def build_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(220)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)

        content = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        title = QLabel("LADOC")
        title.setObjectName("SidebarTitle")
        layout.addWidget(title)

        self.add_sidebar_button(layout, "Home", self.show_home_page)

        pw_section = CollapsibleSection("Password Tools")
        pw_section.add_widget(self.make_action_button("HaveIBeenPwned", self.show_breach_checker))
        pw_section.add_widget(self.make_action_button("Strength Checker", self.show_strength_checker))
        pw_section.add_widget(self.make_action_button("Password Generator", self.show_password_generator))
        pw_section.add_widget(self.make_action_button("Password Manager", self.show_password_manager))
        layout.addWidget(pw_section)

        cis_section = CollapsibleSection("CIS Tools")
        cis_section.add_widget(self.make_action_button("CIS Hardening", self.show_cis_launcher))
        layout.addWidget(cis_section)

        settings_section = CollapsibleSection("Settings")
        settings_section.add_widget(self.make_action_button("Toggle Theme", self.toggle_theme))
        layout.addWidget(settings_section)

        content.setLayout(layout)
        scroll_area.setWidget(content)

        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(12, 12, 12, 12)
        sidebar_layout.setSpacing(0)
        sidebar_layout.addWidget(scroll_area)
        sidebar.setLayout(sidebar_layout)

        return sidebar

    def add_sidebar_button(self, layout, label, callback):
        btn = QPushButton(label)
        btn.setObjectName("SidebarButton")
        btn.clicked.connect(callback)
        layout.addWidget(btn)

    def make_action_button(self, text, callback):
        btn = QPushButton(text)
        btn.setObjectName("SidebarButton")
        btn.clicked.connect(callback)
        return btn

    def toggle_theme(self):
        main_window = self.parentWidget().window()
        if hasattr(main_window, 'toggle_theme'):
            main_window.toggle_theme()

    def clear_main_content(self):
        while self.main_content.count():
            child = self.main_content.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def show_home_page(self):
        self.clear_main_content()

        welcome = QLabel(f"Welcome, {self.username}!")
        welcome.setObjectName("WelcomeHeading")
        welcome.setAlignment(Qt.AlignCenter)

        subtitle = QLabel("Select a tool from the menu to begin")
        subtitle.setObjectName("WelcomeSubheading")
        subtitle.setAlignment(Qt.AlignCenter)

        self.main_content.addStretch(1)
        self.main_content.addWidget(welcome)
        self.main_content.addWidget(subtitle)
        self.main_content.addStretch(1)

    def show_breach_checker(self):
        self.clear_main_content()
        self.main_content.addWidget(HaveIBeenPwnedWidget())

    def show_strength_checker(self):
        self.clear_main_content()
        self.main_content.addWidget(PasswordStrengthWidget())

    def show_password_generator(self):
        self.clear_main_content()
        self.main_content.addWidget(PasswordGeneratorWidget())

    def show_password_manager(self):
        self.clear_main_content()
        self.main_content.addWidget(PasswordManagerWidget(self.user_id))

    def show_cis_launcher(self):
        self.clear_main_content()
        self.main_content.addWidget(CISLauncher())


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Load and apply Inter font globally
    font_families = load_inter_fonts()
    if any("Inter" in family for family in font_families):
        app.setFont(QFont("Inter", 10))

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
