import sqlite3, os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit,
    QTreeWidget, QTreeWidgetItem, QListWidget, QListWidgetItem,
    QSplitter, QInputDialog, QMessageBox, QDialog, QFormLayout,
    QDialogButtonBox, QComboBox, QDateEdit, QTextEdit
)
from PyQt5.QtCore import Qt, QDate, QTimer
from datetime import datetime, timedelta
from .crypto_utils import get_fernet
from .manager_addpassword import AddPasswordDialog
from .manager_editpassword import EditPasswordDialog
from .manager_addfolder import AddFolderDialog
from .manager_editfolder import EditFolderDialog
from .utilities.db_connection import get_db_path

MAX_DEPTH = 3


class PasswordManagerWidget(QWidget):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.selected_folder = None
        self.search_query = ""
        self.init_ui()
        self.load_common_passwords()
        self.load_folders()
        self.load_passwords()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Search by title or username...")
        self.search_field.textChanged.connect(self.on_search_text_changed)
        main_layout.addWidget(self.search_field)

        splitter = QSplitter(Qt.Horizontal)
        
        # Folders section with title
        folders_container = QWidget()
        folders_layout = QVBoxLayout(folders_container)
        folders_layout.setContentsMargins(0, 0, 0, 0)
        folders_layout.setSpacing(5)
        
        folders_title = QLabel("Folders")
        folders_title.setObjectName("SectionTitle")
        folders_layout.addWidget(folders_title)
        
        self.folder_tree = QTreeWidget()
        self.folder_tree.setHeaderHidden(True)
        self.folder_tree.itemClicked.connect(self.on_folder_selected)
        folders_layout.addWidget(self.folder_tree)
        
        # Passwords section with title
        passwords_container = QWidget()
        passwords_layout = QVBoxLayout(passwords_container)
        passwords_layout.setContentsMargins(0, 0, 0, 0)
        passwords_layout.setSpacing(5)
        
        passwords_title = QLabel("Passwords")
        passwords_title.setObjectName("SectionTitle")
        passwords_layout.addWidget(passwords_title)
        
        self.password_list = QListWidget()
        self.password_list.itemClicked.connect(self.on_password_selected)
        passwords_layout.addWidget(self.password_list)

        splitter.addWidget(folders_container)
        splitter.addWidget(passwords_container)
        splitter.setSizes([200, 400])

        main_layout.addWidget(splitter)

        # Bottom Resizable Section 
        bottom_splitter = QSplitter(Qt.Horizontal)

        # Password details section with title
        details_container = QWidget()
        details_layout = QVBoxLayout(details_container)
        details_layout.setContentsMargins(0, 0, 0, 0)
        details_layout.setSpacing(5)
        
        details_title = QLabel("Details")
        details_title.setObjectName("SectionTitle")
        details_layout.addWidget(details_title)

        # Replace QLabel with QTextEdit for better text handling
        self.details_text = QTextEdit()
        self.details_text.setPlainText("Select a password to see details")
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(200)  # Set a reasonable max height
        self.details_text.setMinimumHeight(100)  # Set a minimum height
        self.details_text.setStyleSheet("border: 1px solid #ccc; padding: 8px;")

        self.show_password_btn = QPushButton("Show Password")
        self.show_password_btn.setVisible(False)
        self.show_password_btn.clicked.connect(self.toggle_password_visibility)

        details_layout.addWidget(self.details_text)
        details_layout.addWidget(self.show_password_btn)
        details_layout.addStretch()

        #  Health Dashboard section with title
        health_container = QWidget()
        health_layout = QVBoxLayout(health_container)
        health_layout.setContentsMargins(0, 0, 0, 0)
        health_layout.setSpacing(5)
        
        health_title = QLabel("Health Dashboard")
        health_title.setObjectName("SectionTitle")
        health_layout.addWidget(health_title)

        self.health_dashboard_label = QLabel("")
        self.health_dashboard_label.setWordWrap(True)
        self.health_dashboard_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.health_dashboard_label.setStyleSheet("border: 1px solid #ccc; padding: 8px;")

        health_layout.addWidget(self.health_dashboard_label)
        health_layout.addStretch()

        bottom_splitter.addWidget(details_container)
        bottom_splitter.addWidget(health_container)
        bottom_splitter.setSizes([600, 300])  # initial ratio
        bottom_splitter.setStretchFactor(0, 3)
        bottom_splitter.setStretchFactor(1, 2)

        main_layout.addWidget(bottom_splitter)

        btn_layout = QHBoxLayout()
        self.add_folder_btn = QPushButton("Add Folder")
        self.add_folder_btn.clicked.connect(self.add_folder)

        self.edit_folder_btn = QPushButton("Edit Folder")
        self.edit_folder_btn.setEnabled(False)
        self.edit_folder_btn.clicked.connect(self.edit_folder)

        self.add_password_btn = QPushButton("Add Password")
        self.add_password_btn.clicked.connect(self.add_password)

        self.edit_password_btn = QPushButton("Edit Password")
        self.edit_password_btn.clicked.connect(self.edit_password)
        self.edit_password_btn.setEnabled(False)

        btn_layout.addWidget(self.add_folder_btn)
        btn_layout.addWidget(self.edit_folder_btn)
        btn_layout.addWidget(self.add_password_btn)
        btn_layout.addWidget(self.edit_password_btn)
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)

    def format_notes_with_line_breaks(self, notes):
        """Format notes with proper line breaks for better readability"""
        if not notes:
            return ""
        
        # Split by existing newlines first
        lines = notes.split('\n')
        formatted_lines = []
        
        for line in lines:
            # If line is longer than 60 characters, break it at word boundaries
            if len(line) <= 60:
                formatted_lines.append(line)
            else:
                words = line.split()
                current_line = ""
                
                for word in words:
                    # If adding this word would exceed 60 characters, start a new line
                    if len(current_line + " " + word) > 60 and current_line:
                        formatted_lines.append(current_line.strip())
                        current_line = word
                    else:
                        current_line += (" " + word) if current_line else word
                
                # Add the last line if there's content
                if current_line:
                    formatted_lines.append(current_line.strip())
        
        return '\n'.join(formatted_lines)

    def on_search_text_changed(self, text):
        self.search_query = text.strip().lower()
        self.load_passwords()

    def load_folders(self):
        self.folder_tree.clear()
        root = QTreeWidgetItem(["All Passwords"])
        root.setData(0, Qt.UserRole, None)
        root.setExpanded(True)
        self.folder_tree.addTopLevelItem(root)

        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, parent_id FROM users_folders WHERE user_id = ?", (self.user_id,))
        folders = cursor.fetchall()
        conn.close()

        id_to_item = {None: root}
        for folder_id, name, parent_id in folders:
            parent_item = id_to_item.get(parent_id, root)
            item = QTreeWidgetItem([name])
            item.setData(0, Qt.UserRole, folder_id)
            parent_item.addChild(item)
            id_to_item[folder_id] = item

    def load_passwords(self):
        self.load_common_passwords()
        self.password_list.clear()

        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()

        if self.selected_folder is None:
            cursor.execute("SELECT id, title, username, password FROM user_passwords WHERE user_id = ?", (self.user_id,))
        else:
            folder_item = self.get_folder_item_by_id(self.selected_folder)
            if not folder_item:
                self.password_list.clear()
                conn.close()
                return
            folder_path = self.build_folder_path(folder_item)
            cursor.execute(
                """
                SELECT id, title, username, password FROM user_passwords 
                WHERE user_id = ? AND (folder_path = ? OR folder_path LIKE ?)
                """,
                (self.user_id, folder_path, folder_path + "/%")
            )
        rows = cursor.fetchall()
        conn.close()

        # Decrypt passwords and track reuse and common passwords
        fernet = get_fernet()
        decrypted_passwords = []
        for entry_id, title, username, encrypted_password in rows:
            try:
                password = fernet.decrypt(encrypted_password.encode()).decode()
                decrypted_passwords.append((entry_id, title, username, password))
            except Exception:
                continue  # skip entry if decryption fails

        # Count reuse: password -> count
        password_counts = {}
        for _, _, _, pwd in decrypted_passwords:
            if pwd is not None:
                password_counts[pwd] = password_counts.get(pwd, 0) + 1

        # Fill QListWidget and mark reused/common passwords in the list
        for entry_id, title, username, pwd in decrypted_passwords:
            if self.search_query:
                combined = f"{title} {username}".lower()
                if self.search_query not in combined:
                    continue

            display_text = f"{title} ({username})"
            reused = pwd and password_counts.get(pwd, 0) > 1
            common = pwd and pwd.lower() in self.common_passwords

            if reused and common:
                display_text += " [REUSED, 10K]"
            elif reused:
                display_text += " [REUSED]"
            elif common:
                display_text += " [10K]"

            item = QListWidgetItem(display_text)
            item.setData(Qt.UserRole, entry_id)
            self.password_list.addItem(item)

        # Update health dashboard label
        total_passwords = len(decrypted_passwords)
        reused_passwords_count = sum(1 for p in password_counts.values() if p > 1)
        common_passwords_count = sum(1 for _, _, _, p in decrypted_passwords if p.lower() in self.common_passwords)

        health_msg = f"Total Passwords: {total_passwords}<br>" \
                    f"Reused Passwords: {reused_passwords_count}<br>" \
                    f"Top 10K Used Passwords: {common_passwords_count}"

        self.health_dashboard_label.setText(health_msg)

    def get_folder_item_by_id(self, folder_id):
        def traverse(item):
            if item.data(0, Qt.UserRole) == folder_id:
                return item
            for i in range(item.childCount()):
                res = traverse(item.child(i))
                if res:
                    return res
            return None

        for i in range(self.folder_tree.topLevelItemCount()):
            found = traverse(self.folder_tree.topLevelItem(i))
            if found:
                return found
        return None

    def build_folder_path(self, item):
        names = []
        while item and item.data(0, Qt.UserRole) is not None:
            names.insert(0, item.text(0))
            item = item.parent()
        return "/".join(names)

    def on_folder_selected(self, item):
        self.selected_folder = item.data(0, Qt.UserRole)
        self.load_passwords()
        self.details_text.setPlainText("Select a password to see details")
        self.edit_folder_btn.setEnabled(self.selected_folder is not None)

    def edit_folder(self):
        if self.selected_folder is None:
            QMessageBox.warning(self, "No folder selected", "Please select a folder to edit.")
            return

        # Get current folder item and name
        folder_item = self.get_folder_item_by_id(self.selected_folder)
        if not folder_item:
            QMessageBox.warning(self, "Error", "Folder not found.")
            return

        current_name = folder_item.text(0)

        dialog = EditFolderDialog(self.selected_folder, current_name, self)

        def handle_folder_deleted():
            # Delete folder and all passwords in it from DB
            conn = sqlite3.connect(get_db_path())
            cursor = conn.cursor()

            folder_path = self.build_folder_path(folder_item)

            # Move passwords in this folder and subfolders to root (no folder)
            cursor.execute(
                """
                UPDATE user_passwords 
                SET folder_path = NULL 
                WHERE user_id = ? AND (folder_path = ? OR folder_path LIKE ?)
                """,
                (self.user_id, folder_path, folder_path + "/%")
            )

            # Delete the folder itself
            cursor.execute("DELETE FROM users_folders WHERE id = ?", (self.selected_folder,))

            conn.commit()
            conn.close()

            self.selected_folder = None
            self.load_folders()
            self.load_passwords()
            self.details_text.setPlainText("Select a password to see details")
            self.edit_folder_btn.setEnabled(False)

        dialog.folder_deleted.connect(handle_folder_deleted)

        if dialog.exec_() == QDialog.Accepted:
            new_name = dialog.get_new_name()
            if new_name != current_name:
                # Rename folder in DB
                conn = sqlite3.connect(get_db_path())
                cursor = conn.cursor()

                # Update folder name
                cursor.execute("UPDATE users_folders SET name = ? WHERE id = ?", (new_name, self.selected_folder))

                # Also update folder_path of all passwords inside this folder and its subfolders
                old_path = self.build_folder_path(folder_item)
                new_path = old_path.rsplit("/", 1)[0]  # Get parent path or empty
                if new_path:
                    new_path = new_path + "/" + new_name
                else:
                    new_path = new_name

                # Get all folders under this folder (to update their paths too)
                cursor.execute("SELECT id, name, parent_id FROM users_folders WHERE user_id = ?", (self.user_id,))
                folders = cursor.fetchall()

                def get_full_path(folder_id, folder_map):
                    parts = []
                    while folder_id:
                        name = folder_map[folder_id]['name']
                        parts.insert(0, name)
                        folder_id = folder_map[folder_id]['parent_id']
                    return "/".join(parts)

                # Build a map for folders
                folder_map = {f[0]: {'name': f[1], 'parent_id': f[2]} for f in folders}

                # Find all descendant folder ids of self.selected_folder
                descendants = []

                def find_descendants(fid):
                    for f in folders:
                        if f[2] == fid:
                            descendants.append(f[0])
                            find_descendants(f[0])

                find_descendants(self.selected_folder)

                # Update folder_path for passwords in this folder and all descendants
                # Because we only renamed this one folder, we need to update paths that start with old_path

                cursor.execute(
                    "SELECT id, folder_path FROM user_passwords WHERE user_id = ? AND (folder_path = ? OR folder_path LIKE ?)",
                    (self.user_id, old_path, old_path + "/%")
                )
                pw_rows = cursor.fetchall()

                for pw_id, fp in pw_rows:
                    if fp == old_path:
                        new_fp = new_path
                    else:
                        # Replace old_path prefix with new_path
                        new_fp = fp.replace(old_path + "/", new_path + "/")
                    cursor.execute(
                        "UPDATE user_passwords SET folder_path = ? WHERE id = ?", (new_fp, pw_id)
                    )

                conn.commit()
                conn.close()

                self.load_folders()
                self.load_passwords()

    def on_password_selected(self, item):
        self.edit_password_btn.setEnabled(True)
        entry_id = item.data(Qt.UserRole)
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute("SELECT title, username, password, site, notes, password_expiry FROM user_passwords WHERE id = ?", (entry_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            title, username, encrypted_password, site, notes, expiry = row

            try:
                fernet = get_fernet()
                password = fernet.decrypt(encrypted_password.encode()).decode()
            except Exception:
                password = "[Unable to decrypt]"

            expiry_str = expiry if expiry else "N/A"
            
            # Format notes with line breaks
            formatted_notes = self.format_notes_with_line_breaks(notes) if notes else ""

            details_visible = f"""Title: {title}
            Username: {username}
            Password: {password}
            Site: {site}
            Expiry Date: {expiry_str}

            Notes:
            {formatted_notes}"""

            censor = "*" * len(password)
            details_hidden = details_visible.replace(f"Password: {password}", f"Password: {censor}")

            self._current_password = password
            self._raw_password_details = details_visible
            self._is_password_visible = False

            self.show_password_btn.setVisible(True)
            self.show_password_btn.setText("Show Password")
            self.details_text.setPlainText(details_hidden)

        else:
            self.details_text.setPlainText("No details found.")

    def get_folder_depth(self, folder_item):
        depth = 0
        while folder_item and folder_item.data(0, Qt.UserRole) is not None:
            depth += 1
            folder_item = folder_item.parent()
        return depth

    def add_folder(self):
        selected = self.folder_tree.currentItem()
        if not selected:
            QMessageBox.warning(self, "No folder selected", "Please select a folder to add the new folder under.")
            return

        depth = self.get_folder_depth(selected)
        if depth >= MAX_DEPTH:
            QMessageBox.warning(self, "Limit Reached", f"Too many subfolders created! Maximum depth: {MAX_DEPTH}.")
            return

        dialog = AddFolderDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            name = dialog.get_folder_name()
            parent_id = selected.data(0, Qt.UserRole)

            conn = sqlite3.connect(get_db_path())
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users_folders (user_id, name, parent_id) VALUES (?, ?, ?)",
                (self.user_id, name, parent_id)
            )
            conn.commit()
            conn.close()

            self.load_folders()

    def add_password(self):
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, parent_id FROM users_folders WHERE user_id = ?", (self.user_id,))
        folders = cursor.fetchall()
        conn.close()

        dialog = AddPasswordDialog(folders, self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if not data["title"] or not data["password"]:
                QMessageBox.warning(self, "Missing Fields", "Title and Password are required.")
                return

            fernet = get_fernet()
            encrypted_password = fernet.encrypt(data["password"].encode()).decode()

            conn = sqlite3.connect(get_db_path())
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO user_passwords (user_id, title, username, password, site, notes, folder_path, password_expiry)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    self.user_id, data["title"], data["username"],
                    encrypted_password, data["site"], data["notes"],
                    data["folder_path"], data["password_expiry"]
                )
            )
            conn.commit()
            conn.close()
            self.load_passwords()

    def edit_password(self):
        selected_item = self.password_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "No selection", "Please select a password to edit.")
            return

        entry_id = selected_item.data(Qt.UserRole)

        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute(
            "SELECT title, username, password, site, notes, password_expiry, folder_path FROM user_passwords WHERE id = ?",
            (entry_id,)
        )
        row = cursor.fetchone()
        conn.close()

        if not row:
            QMessageBox.warning(self, "Error", "Password entry not found.")
            return

        title, username, encrypted_password, site, notes, expiry, folder_path = row

        try:
            fernet = get_fernet()
            decrypted_password = fernet.decrypt(encrypted_password.encode()).decode()
        except Exception:
            decrypted_password = ""

        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, parent_id FROM users_folders WHERE user_id = ?", (self.user_id,))
        folders = cursor.fetchall()
        conn.close()

        dialog = EditPasswordDialog(folders, self)

        dialog.set_data({
            "title": title,
            "username": username,
            "password": decrypted_password,
            "site": site,
            "notes": notes,
            "password_expiry": expiry,
            "folder_path": folder_path,
        })
        dialog.set_entry_id(entry_id)

        def on_password_deleted():
            self.load_passwords()
            self.details_text.setPlainText("Select a password to see details")
            self.edit_password_btn.setEnabled(False)
            # Close dialog after short delay to avoid crashes
            QTimer.singleShot(100, dialog.accept)

        dialog.password_deleted.connect(on_password_deleted)

        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if not data["title"] or not data["password"]:
                QMessageBox.warning(self, "Missing Fields", "Title and Password are required.")
                return

            encrypted_password = fernet.encrypt(data["password"].encode()).decode()

            conn = sqlite3.connect(get_db_path())
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE user_passwords
                SET title = ?, username = ?, password = ?, site = ?, notes = ?, password_expiry = ?, folder_path = ?
                WHERE id = ?
                """,
                (
                    data["title"], data["username"], encrypted_password,
                    data["site"], data["notes"], data["password_expiry"],
                    data["folder_path"], entry_id
                )
            )
            conn.commit()
            conn.close()

            self.load_passwords()

            # Refresh the details panel for the updated password
            updated_item = None
            for i in range(self.password_list.count()):
                item = self.password_list.item(i)
                if item.data(Qt.UserRole) == entry_id:
                    updated_item = item
                    break

            if updated_item:
                self.on_password_selected(updated_item)

    def toggle_password_visibility(self):
        self._is_password_visible = not self._is_password_visible
        if self._is_password_visible:
            self.details_text.setPlainText(self._raw_password_details)
            self.show_password_btn.setText("Hide Password")
        else:
            censor = "*" * len(self._current_password)
            hidden = self._raw_password_details.replace(
                f"Password: {self._current_password}", f"Password: {censor}"
            )
            self.details_text.setPlainText(hidden)
            self.show_password_btn.setText("Show Password")

    def load_common_passwords(self):
        self.common_passwords = set()
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            filepath = os.path.join(base_dir, "../assets/top10k.txt") 
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    pwd = line.strip().lower()
                    if pwd:
                        self.common_passwords.add(pwd)
        except Exception as e:
            print(f"Error loading common passwords: {e}")
            self.common_passwords = set()