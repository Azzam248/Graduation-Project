import sys
import mysql.connector
import json
import os
from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
                             QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
                             QMainWindow, QStatusBar, QApplication)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor,QGuiApplication


class AdminPanel(QMainWindow):
    def __init__(self, admin_username):
        super().__init__()
        self.admin_username = admin_username
        self.initUI()
        self.loadUsers()

    def initUI(self):
        self.setWindowTitle("Admin Control Panel")
        self.setGeometry(100, 100, 800, 600)
        self.setFixedSize(800, 600)
        self.center_window()
        self.setStyleSheet("background-color: #f0f0f0;")

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header_layout = QHBoxLayout()

        title_label = QLabel("Admin Control Panel")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        header_layout.addWidget(title_label)

        admin_info = QLabel(f"Logged in as: {self.admin_username}")
        admin_info.setStyleSheet("font-size: 14px; color: #555; font-style: italic;")
        admin_info.setAlignment(Qt.AlignVCenter)
        header_layout.addWidget(admin_info)

        main_layout.addLayout(header_layout)

        

        # User Management Section
        user_section_label = QLabel("User Management")
        user_section_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #444;")
        main_layout.addWidget(user_section_label)

        # User Table
        self.user_table = QTableWidget()
        self.user_table.setColumnCount(5)  # Changed to 5 columns
        self.user_table.setHorizontalHeaderLabels(
            ["Username", "User ID", "Premium Status", "Access Request", "Actions"])
        self.user_table.horizontalHeader().setStretchLastSection(True)
        # Resize the columns to fit
        self.user_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.user_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.user_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.user_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.user_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #f8f8f8;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            QHeaderView::section {
                background-color: #4a90e2;
                color: white;
                padding: 6px;
                border: none;
                font-weight: bold;
            }
        """)
        self.user_table.setAlternatingRowColors(True)  # Makes it easier to read throughout the table
        main_layout.addWidget(self.user_table)

        # Button layout for actions
        button_layout = QHBoxLayout()

        self.refresh_button = QPushButton("Refresh Users")
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 15px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.refresh_button.clicked.connect(self.loadUsers)
        button_layout.addWidget(self.refresh_button)

        self.logout_button = QPushButton("Logout")
        self.logout_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 15px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        self.logout_button.clicked.connect(self.logout)
        button_layout.addWidget(self.logout_button)

        main_layout.addLayout(button_layout)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")


    def center_window(self):
        screen = QGuiApplication.primaryScreen()  # Get primary screen
        screen_geometry = screen.geometry()  # Get screen dimensions
        window_geometry = self.frameGeometry()  # Get window dimensions
        window_geometry.moveCenter(screen_geometry.center())  # Move window to center
        self.move(window_geometry.topLeft())  # Set new position

    def loadUsers(self):
        try:
            # Connect to database
            conn = mysql.connector.connect(host="localhost", user="root", password="root",
                                           database="filestoragedb")
            cursor = conn.cursor()

            # Get all users
            cursor.execute("SELECT UserName, UserID FROM user ORDER BY UserName")
            users = cursor.fetchall()

            # Load premium status from JSON
            premium_users = {}
            try:
                with open("premium_access.json", "r") as file:
                    premium_users = json.load(file)
            except FileNotFoundError:
                premium_users = {}

            # Load access requests from JSON
            access_requests = {}
            try:
                with open("access_requests.json", "r") as file:
                    access_requests = json.load(file)
            except FileNotFoundError:
                access_requests = {}

            # Set up table
            self.user_table.setRowCount(len(users))

            for row, (username, user_id) in enumerate(users):
                # Username
                username_item = QTableWidgetItem(username)
                username_item.setFlags(username_item.flags() & ~Qt.ItemIsEditable)  # Make read-only
                self.user_table.setItem(row, 0, username_item)

                # User ID
                user_id_item = QTableWidgetItem(
                    str(user_id))  # Converts user_id to a string because QTableWidgetItem only accepts strings.
                user_id_item.setFlags(user_id_item.flags() & ~Qt.ItemIsEditable)  # Make read-only
                self.user_table.setItem(row, 1, user_id_item)

                # Premium Status
                is_premium = premium_users.get(username, False)
                premium_status = "Premium" if is_premium else "Standard"  # if it's true return Premium otherwise Standard
                status_item = QTableWidgetItem(premium_status)
                status_item.setTextAlignment(Qt.AlignCenter)
                status_item.setFlags(status_item.flags() & ~Qt.ItemIsEditable)  # Make read-only
                if is_premium:
                    status_item.setBackground(QColor(230, 250, 230))  # Light green background
                    status_item.setForeground(QColor(0, 130, 0))  # Dark green text
                self.user_table.setItem(row, 2, status_item)

                # Access Request Status
                has_request = access_requests.get(username, False)
                request_status = "Requested" if has_request else "None"
                request_item = QTableWidgetItem(request_status)
                request_item.setTextAlignment(Qt.AlignCenter)
                request_item.setFlags(request_item.flags() & ~Qt.ItemIsEditable)  # Make read-only
                if has_request:
                    request_item.setBackground(QColor(255, 243, 205))  # Light yellow background
                    request_item.setForeground(QColor(176, 132, 0))  # Dark yellow/orange text
                self.user_table.setItem(row, 3, request_item)

                # Actions cell with buttons
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(4, 4, 4, 4)
                actions_layout.setSpacing(4)

                # Toggle premium button
                toggle_premium_btn = QPushButton("Premium On" if is_premium else "Premium Off")
                toggle_premium_btn.setStyleSheet(
                    "background-color: #28a745; color: white; border-radius: 3px; padding: 4px;" if is_premium
                    else "background-color: #6c757d; color: white; border-radius: 3px; padding: 4px;"
                )
                toggle_premium_btn.clicked.connect(
                    lambda checked, u=username, p=is_premium: self.togglePremium(u,
                                                                                 not p))  # checked is Boolean value T or F
                actions_layout.addWidget(toggle_premium_btn)

                # Clear request button (only visible if there's a request)
                if has_request:
                    clear_request_btn = QPushButton("Clear Request")
                    clear_request_btn.setStyleSheet(
                        "background-color: #ffc107; color: black; border-radius: 3px; padding: 4px;")
                    clear_request_btn.clicked.connect(lambda checked, u=username: self.clearAccessRequest(u))
                    actions_layout.addWidget(clear_request_btn)

                # Delete user button
                delete_btn = QPushButton("Delete")
                delete_btn.setStyleSheet("background-color: #dc3545; color: white; border-radius: 3px; padding: 4px;")
                delete_btn.clicked.connect(lambda checked, u=username: self.deleteUser(u))
                actions_layout.addWidget(delete_btn)

                actions_layout.setAlignment(Qt.AlignCenter)
                actions_widget.setLayout(actions_layout)
                self.user_table.setCellWidget(row, 4, actions_widget)  # Now in column 4 (fifth column)

            conn.close()
            self.status_bar.showMessage(f"Loaded {len(users)} users")

        except mysql.connector.Error as err:
            self.status_bar.showMessage(f"Database error: {err}")
            QMessageBox.critical(self, "Database Error", f"Failed to load users: {err}")

    def togglePremium(self, username, new_premium_status):
        try:
            # Load existing premium data
            try:
                with open("premium_access.json", "r") as file:
                    premium_data = json.load(file)
            except FileNotFoundError:
                premium_data = {}

            # Update premium status
            premium_data[username] = new_premium_status

            # Save back to JSON
            with open("premium_access.json", "w") as file:
                json.dump(premium_data, file, indent=4)

            # If premium is granted, clear any access request
            if new_premium_status:
                self.clearAccessRequest(username)

            # Reload user list to reflect changes
            self.loadUsers()

            status_text = "Premium access granted" if new_premium_status else "Premium access revoked"
            self.status_bar.showMessage(f"{status_text} for {username}")

        except Exception as e:
            self.status_bar.showMessage(f"Error updating premium status: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to update premium status: {str(e)}")

    def clearAccessRequest(self, username):
        try:
            # Load existing access request data
            try:
                with open("access_requests.json", "r") as file:
                    access_data = json.load(file)
            except FileNotFoundError:
                access_data = {}

            # Remove the access request
            if username in access_data:
                del access_data[username]

                # Save back to JSON
                with open("access_requests.json", "w") as file:
                    json.dump(access_data, file, indent=4)

                # Reload user list to reflect changes
                self.loadUsers()

                self.status_bar.showMessage(f"Access request cleared for {username}")
        except Exception as e:
            self.status_bar.showMessage(f"Error clearing access request: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to clear access request: {str(e)}")

    def deleteUser(self, username):
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete user '{username}'?\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                # Connect to database
                conn = mysql.connector.connect(host="localhost", user="root", password="root",
                                               database="filestoragedb")
                cursor = conn.cursor()
                cursor.execute("SELECT UserID FROM user WHERE UserName = %s", (username,))
                user_id_result = cursor.fetchone()

                if not user_id_result:
                    self.status_bar.showMessage(f"User '{username}' not found")
                    return

                user_id = user_id_result[0]

                # Use the existing settings window to handle file deletion
                from settings import SettingsWindow
                settings_instance = SettingsWindow(username, user_id)
                settings_instance.delete_all_files()

                # Delete user
                cursor.execute("DELETE FROM user WHERE UserName = %s", (username,))
                conn.commit()

                # Also remove from premium_access.json if present
                try:
                    with open("premium_access.json", "r") as file:
                        premium_data = json.load(file)

                    if username in premium_data:
                        del premium_data[username]

                        with open("premium_access.json", "w") as file:
                            json.dump(premium_data, file, indent=4)
                except FileNotFoundError:
                    pass  # File doesn't exist, no need to update

                # Also remove from access_requests.json if present
                try:
                    with open("access_requests.json", "r") as file:
                        access_data = json.load(file)

                    if username in access_data:
                        del access_data[username]

                        with open("access_requests.json", "w") as file:
                            json.dump(access_data, file, indent=4)
                except FileNotFoundError:
                    pass  # File doesn't exist, no need to update

                conn.close()

                # Reload user list
                self.loadUsers()
                self.status_bar.showMessage(f"User '{username}' deleted successfully")

            except mysql.connector.Error as err:
                self.status_bar.showMessage(f"Database error: {err}")
                QMessageBox.critical(self, "Database Error", f"Failed to delete user: {err}")

    def logout(self):
        reply = QMessageBox.question(
            self,
            "Confirm Logout",
            "Are you sure you want to logout?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            from login import LoginApp
            self.login_window = LoginApp()
            self.login_window.show()
            self.close()


# For testing purposes
if __name__ == "__main__":
    app = QApplication(sys.argv)
    admin_panel = AdminPanel("admin")
    admin_panel.show()
    sys.exit(app.exec_())
