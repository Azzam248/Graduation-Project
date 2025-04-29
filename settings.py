from PyQt5.QtWidgets import (QMainWindow, QWidget, QLabel, QPushButton,
                             QVBoxLayout, QHBoxLayout, QFrame, QLineEdit,
                             QMessageBox, QApplication, QProgressDialog,QTextEdit,QTableWidgetItem,QFormLayout,
                             QTabWidget,QComboBox,QTableWidget,QHeaderView)
from PyQt5.QtCore import Qt
import boto3
import os
import mysql.connector
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QGuiApplication
import json

import sys
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QDialog, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt, QThread, pyqtSignal






class SettingsWindow(QMainWindow):
    """
    Settings window that allows users to customize application settings
    and manage their account, including account deletion.
    """

    def __init__(self, username, user_id):
        super().__init__()
        self.username = username
        self.user_id = user_id

        # Initialize counters
        self.file_count = 0
        self.image_count = 0
        self.video_count = 0

        # Initialize database connection
        self.db_connection = None
        self.connect_to_database()

        # Initialize S3 client
        from upload_module import UploadWindow

        # Then in your __init__ method:
        self.s3_client = None
        self.s3_bucket = None
        upload_instance = UploadWindow(self.username, self.user_id)
        self.s3_client = upload_instance.s3_client
        self.s3_bucket = upload_instance.s3_bucket

        self.initUI()



    def connect_to_database(self):
        """Connect to MySQL database"""
        try:
            self.db_connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="root",
                database="filestoragedb"
            )
            return True
        except Exception as e:
            print(f"Error connecting to database: {str(e)}")
            self.db_connection = None
            return False

    def initUI(self):
        """Initialize the user interface components"""
        self.setWindowTitle("User Settings")
        self.setGeometry(100, 100, 800, 600)
        self.center_window()

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)

        # Header
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: #4a90e2;")
        header_frame.setMinimumHeight(80)
        header_layout = QHBoxLayout(header_frame)

        title_label = QLabel("Settings")
        title_label.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        header_layout.addWidget(title_label)

        back_button = self.create_button("Back to Dashboard", False)
        back_button.setMaximumWidth(150)
        back_button.clicked.connect(self.go_back_to_dashboard)
        header_layout.addWidget(back_button, alignment=Qt.AlignRight)

        main_layout.addWidget(header_frame)

        # Content area
        content_frame = QFrame()
        content_frame.setStyleSheet("background-color: white;")
        content_layout = QVBoxLayout(content_frame)

        # Settings sections
        section_label = QLabel("Account Settings")
        section_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-top: 20px;")
        content_layout.addWidget(section_label)

        # Create tab widget 5C6AC4 #f0f0f0
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
                    QTabWidget::pane {
                        border: 1px solid #cccccc;
                        background: white;
                        border-radius: 3px;
                    }
                    QTabBar::tab {
                        background: #f0f0f0;
                        border: 1px solid #cccccc;
                        border-bottom: none;
                        border-top-left-radius: 4px;
                        border-top-right-radius: 4px;
                        padding: 8px 12px;
                        margin-right: 2px;
                    }
                    QTabBar::tab:selected {
                        background: white;
                        border-bottom: 1px solid white;
                    }
                    QTabBar::tab:hover {
                        background: #e0e0e0;
                    }
                """)

        # First tab - Account Settings (includes both data management and danger zone)
        account_tab = QWidget()
        account_tab_layout = QVBoxLayout(account_tab)

        # Data management section
        data_frame = QFrame()
        data_frame.setStyleSheet("background-color: #f8f8ff; border: 1px solid #ccccff; border-radius: 5px;")
        data_layout = QVBoxLayout(data_frame)

        data_label = QLabel("Data Management")
        data_label.setStyleSheet("color: #4a4a8a; font-size: 16px; font-weight: bold;")
        data_layout.addWidget(data_label)

        # Display user data statistics
        self.update_data_stats()
        self.data_stats_label = QLabel(
            f"Your uploads: {self.file_count} files, {self.image_count} images, {self.video_count} videos")
        self.data_stats_label.setStyleSheet("color: #333; margin: 5px 0;")
        data_layout.addWidget(self.data_stats_label)

        # Button to delete all files
        delete_files_button = QPushButton("Delete All My Uploads")
        delete_files_button.setStyleSheet("""
                    QPushButton {
                        background-color: #ff6600;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        padding: 8px 16px;
                        font-size: 14px;
                        font-weight: bold;
                        max-width: 200px;
                    }
                    QPushButton:hover {
                        background-color: #e55c00;
                    }
                """)
        delete_files_button.clicked.connect(self.confirm_delete_files)
        data_layout.addWidget(delete_files_button)

        account_tab_layout.addWidget(data_frame)
        account_tab_layout.addSpacing(20)

        # Danger zone
        danger_frame = QFrame()
        danger_frame.setStyleSheet("background-color: #fff8f8; border: 1px solid #ffcccc; border-radius: 5px;")
        danger_layout = QVBoxLayout(danger_frame)

        danger_label = QLabel("Danger Zone")
        danger_label.setStyleSheet("color: #cc0000; font-size: 16px; font-weight: bold;")
        danger_layout.addWidget(danger_label)

        delete_description = QLabel(
            "Permanently delete your account and all associated data. This action cannot be undone.")
        delete_description.setStyleSheet("color: #333; margin-bottom: 10px;")
        delete_description.setWordWrap(True)
        danger_layout.addWidget(delete_description)

        delete_button = QPushButton("Delete Account")
        delete_button.setStyleSheet("""
                    QPushButton {
                        background-color: #cc0000;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        padding: 8px 16px;
                        font-size: 14px;
                        font-weight: bold;
                        max-width: 200px;
                    }
                    QPushButton:hover {
                        background-color: #aa0000;
                    }
                """)
        delete_button.clicked.connect(self.confirm_delete_account)
        danger_layout.addWidget(delete_button)

        account_tab_layout.addWidget(danger_frame)
        account_tab_layout.addStretch()

        # Second tab - Premium Requests
        requests_tab = QWidget()
        requests_layout = QVBoxLayout(requests_tab)

        requests_section_label = QLabel("Premium Access Requests")
        requests_section_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #444;")
        requests_layout.addWidget(requests_section_label)

        # Request form
        request_form_frame = QFrame()
        request_form_frame.setStyleSheet(
            "background-color: #f5f5f5; border: 1px solid #ddd; border-radius: 5px; padding: 10px;")
        request_form_layout = QFormLayout(request_form_frame)

        # Justification text area
        justification_text = QTextEdit()
        justification_text.setPlaceholderText("Explain why you need this premium feature...")
        justification_text.setMinimumHeight(100)
        request_form_layout.addRow("Justification:", justification_text)

        # Submit button
        submit_request_button = QPushButton("Submit Request")
        submit_request_button.setStyleSheet("""
                    QPushButton {
                        background-color: #4a90e2;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        padding: 8px 16px;
                        font-size: 14px;
                        font-weight: bold;
                        max-width: 200px;
                    }
                    QPushButton:hover {
                        background-color: #3a80d2;
                    }
                """)
        submit_request_button.clicked.connect(self.submit_premium_request)

        request_form_layout.addRow("", submit_request_button)
        requests_layout.addWidget(request_form_frame)




        requests_layout.addStretch()

        # Add tabs to the tab widget
        tab_widget.addTab(account_tab, "Account Settings")
        tab_widget.addTab(requests_tab, "Premium Requests")

        # Add the tab widget to the content layout
        content_layout.addWidget(tab_widget)
        content_layout.addStretch()

        main_layout.addWidget(content_frame)

    def center_window(self):
        screen = QGuiApplication.primaryScreen()  # Get primary screen
        screen_geometry = screen.geometry()  # Get screen dimensions
        window_geometry = self.frameGeometry()  # Get window dimensions
        window_geometry.moveCenter(screen_geometry.center())  # Move window to center
        self.move(window_geometry.topLeft())  # Set new position

    def create_button(self, text, primary=True):
        """Create a styled button with consistent appearance"""
        button = QPushButton(text)
        button.setMinimumHeight(40)
        if primary:
            button.setStyleSheet("""
                QPushButton {
                    background-color: #4a90e2;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 8px 16px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #357ab7;
                }
                QPushButton:pressed {
                    background-color: #2a5885;
                }
            """)
        else:
            button.setStyleSheet("""
                QPushButton {
                    background-color: #f0f0f0;
                    color: #333;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    padding: 8px 16px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
                QPushButton:pressed {
                    background-color: #d0d0d0;
                }
            """)
        return button

    def submit_premium_request(self):
        """
        Submit a request for premium access.
        This function adds the current user to the access_requests.json file.
        """
        try:
            # Get current username
            username = self.username  # Assuming self.username contains the current user's username

            # Load existing access requests or create if doesn't exist
            access_requests = {}
            try:
                with open("access_requests.json", "r") as file:
                    access_requests = json.load(file)
            except FileNotFoundError:
                # File doesn't exist yet, will create it
                pass

            # Check if user already has a pending request
            if username in access_requests and access_requests[username]:
                QMessageBox.information(
                    self,
                    "Request Already Submitted",
                    "You already have a pending premium access request. Please wait for admin approval.",
                    QMessageBox.Ok
                )
                return

            # Check if user already has premium access
            try:
                with open("premium_access.json", "r") as file:
                    premium_users = json.load(file)
                    if username in premium_users and premium_users[username]:
                        QMessageBox.information(
                            self,
                            "Already Premium",
                            "You already have premium access!",
                            QMessageBox.Ok
                        )
                        return
            except FileNotFoundError:
                # Premium file doesn't exist, so user definitely doesn't have premium
                pass

            # Add the request
            access_requests[username] = True

            # Save back to file
            with open("access_requests.json", "w") as file:
                json.dump(access_requests, file, indent=4)

            # Show confirmation to user
            QMessageBox.information(
                self,
                "Request Submitted",
                "Your premium access request has been submitted successfully.\n"
                "An administrator will review your request soon.",
                QMessageBox.Ok
            )

            # Update UI to show pending request status if needed
            # For example, you might disable the request button and show a "pending" label
            if hasattr(self, 'submit_request_button'):
                self.submit_request_button.setEnabled(False)
                self.submit_request_button.setText("Request Pending")
                self.submit_request_button.setStyleSheet(
                    "background-color: #ffc107; color: black; border-radius: 5px; padding: 8px;"
                )

            # If you have a status label, update it
            if hasattr(self, 'premium_status_label'):
                self.premium_status_label.setText("Premium Request: Pending")
                self.premium_status_label.setStyleSheet("color: #856404; font-weight: bold;")

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to submit premium request: {str(e)}",
                QMessageBox.Ok
            )


    def confirm_delete_account(self):
        """Show confirmation dialog for account deletion"""
        dialog = QMessageBox(self)
        dialog.setWindowTitle("Confirm Account Deletion")
        dialog.setText("This action will permanently delete your account and all associated data.")
        dialog.setInformativeText("Type DELETE in the field below to confirm:")

        # Create input field for verification
        text_input = QLineEdit()
        text_input.setPlaceholderText("Type DELETE to confirm")

        # Add input field to the dialog
        layout = dialog.layout()
        layout.addWidget(text_input, 1, 1)

        dialog.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        dialog.setDefaultButton(QMessageBox.Cancel)

        # Connect the textChanged signal to enable/disable the OK button
        ok_button = dialog.button(QMessageBox.Ok)
        ok_button.setEnabled(False)
        ok_button.setText("Delete Account")
        ok_button.setStyleSheet("background-color: #cc0000; color: white;")

        def validate():
            ok_button.setEnabled(text_input.text() == "DELETE")

        text_input.textChanged.connect(validate)

        result = dialog.exec_()

        if result == QMessageBox.Ok and text_input.text() == "DELETE":
            self.delete_account()

    def delete_account(self):
        """Delete the user account and all related data from both S3 and the MySQL database"""
        try:
            # First delete all user files (this handles both database and S3)
            self.delete_all_files()

            # Connect to database if not connected
            if not self.db_connection or not self.db_connection.is_connected():
                self.connect_to_database()
                if not self.db_connection or not self.db_connection.is_connected():
                    QMessageBox.critical(self, "Database Error", "Could not connect to the database.")
                    return

            cursor = self.db_connection.cursor()

            # Delete the user account
            cursor.execute("DELETE FROM user WHERE UserID = %s", (self.user_id,))

            # Commit changes and close cursor
            self.db_connection.commit()
            cursor.close()

            # Show success message
            QMessageBox.information(self, "Account Deleted",
                                    "Your account and all associated data have been permanently deleted.")

            # Return to login screen
            self.logout()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete account: {str(e)}")

    def logout(self):
        """Handle logout - close settings window and reopen login window"""
        self.close()
        # Import here to avoid circular import
        from login import LoginApp
        self.login_app = LoginApp()
        self.login_app.show()

    def update_data_stats(self):
        """Get current statistics about user uploads"""
        try:
            if not self.db_connection or not self.db_connection.is_connected():
                self.connect_to_database()
                if not self.db_connection or not self.db_connection.is_connected():
                    print("Could not connect to database to update stats")
                    return

            cursor = self.db_connection.cursor()

            # Get file counts - using correct table names from the upload module
            cursor.execute("SELECT COUNT(*) FROM file WHERE UserID = %s", (self.user_id,))
            self.file_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM image WHERE UserID = %s", (self.user_id,))
            self.image_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM video WHERE UserID = %s", (self.user_id,))
            self.video_count = cursor.fetchone()[0]

            cursor.close()

        except Exception as e:
            print(f"Error getting data stats: {str(e)}")
            self.file_count = 0
            self.image_count = 0
            self.video_count = 0

    def confirm_delete_files(self):
        """Show confirmation dialog for deleting all user files"""
        dialog = QMessageBox(self)
        dialog.setWindowTitle("Confirm Delete All Uploads")
        dialog.setText(
            f"This will permanently delete all your {self.file_count} files, {self.image_count} images, and {self.video_count} videos.")
        dialog.setInformativeText("Type DELETE in the field below to confirm:")

        # Create input field for verification
        text_input = QLineEdit()
        text_input.setPlaceholderText("Type DELETE to confirm")

        # Add input field to the dialog
        layout = dialog.layout()
        layout.addWidget(text_input, 1, 1)

        dialog.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        dialog.setDefaultButton(QMessageBox.Cancel)

        # Connect the textChanged signal to enable/disable the OK button
        ok_button = dialog.button(QMessageBox.Ok)
        ok_button.setEnabled(False)
        ok_button.setText("Delete All Files")
        ok_button.setStyleSheet("background-color: #ff6600; color: white;")

        def validate():
            ok_button.setEnabled(text_input.text() == "DELETE")

        text_input.textChanged.connect(validate)

        result = dialog.exec_()

        if result == QMessageBox.Ok and text_input.text() == "DELETE":
            self.delete_all_files()

    def delete_all_files(self):
        """Delete all files, images and videos associated with the current user from both S3 and MySQL database"""
        try:
            # Create progress dialog
            progress = QProgressDialog("Deleting user files...", "Cancel", 0, 6, self)
            progress.setWindowTitle("Deleting Files")
            progress.setWindowModality(Qt.WindowModal)
            progress.show()

            # Connect to database if not connected
            if not self.db_connection or not self.db_connection.is_connected():
                self.connect_to_database()
                if not self.db_connection or not self.db_connection.is_connected():
                    QMessageBox.critical(self, "Database Error", "Could not connect to the database.")
                    progress.cancel()
                    return

            cursor = self.db_connection.cursor()

            # Step 1: Get list of files from database before deleting
            progress.setValue(0)
            progress.setLabelText("Finding files to delete from S3...")

            # Get file names from the file table
            cursor.execute("SELECT FileName FROM file WHERE UserID = %s", (self.user_id,))
            file_records = cursor.fetchall()

            # Step 2: Delete files from S3
            progress.setValue(1)
            progress.setLabelText("Deleting files from cloud storage...")

            if self.s3_client:
                try:
                    # List all objects in the user's folder
                    user_prefix = f"user_{self.user_id}/"
                    response = self.s3_client.list_objects_v2(
                        Bucket=self.s3_bucket,
                        Prefix=user_prefix
                    )

                    # Delete each object
                    if 'Contents' in response:
                        for obj in response['Contents']:
                            self.s3_client.delete_object(
                                Bucket=self.s3_bucket,
                                Key=obj['Key']
                            )

                        # If there are more objects (pagination)
                        while response.get('IsTruncated', False):
                            response = self.s3_client.list_objects_v2(
                                Bucket=self.s3_bucket,
                                Prefix=user_prefix,
                                ContinuationToken=response['NextContinuationToken']
                            )

                            if 'Contents' in response:
                                for obj in response['Contents']:
                                    self.s3_client.delete_object(
                                        Bucket=self.s3_bucket,
                                        Key=obj['Key']
                                    )
                except Exception as e:
                    print(f"Error deleting from S3: {str(e)}")
                    # Continue with database deletion even if S3 deletion fails

            # Step 3-5: Delete from database tables
            progress.setValue(2)
            progress.setLabelText("Deleting file records from database...")
            cursor.execute("DELETE FROM file WHERE UserID = %s", (self.user_id,))

            progress.setValue(3)
            progress.setLabelText("Deleting image records from database...")
            cursor.execute("DELETE FROM image WHERE UserID = %s", (self.user_id,))

            progress.setValue(4)
            progress.setLabelText("Deleting video records from database...")
            cursor.execute("DELETE FROM video WHERE UserID = %s", (self.user_id,))

            # Step 6: Commit changes and close cursor
            progress.setValue(5)
            progress.setLabelText("Finalizing changes...")
            self.db_connection.commit()
            cursor.close()
            progress.setValue(6)

            # Update the statistics
            self.update_data_stats()
            self.data_stats_label.setText(
                f"Your uploads: {self.file_count} files, {self.image_count} images, {self.video_count} videos")

            # Show success message
            QMessageBox.information(self, "Files Deleted",
                                    "All your uploaded files, images, and videos have been deleted from the cloud storage.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete files: {str(e)}")

    def go_back_to_dashboard(self):
        """Return to the dashboard"""
        from dashboard import Dashboard
        self.dashboard = Dashboard(self.username, self.user_id)
        self.dashboard.show()
        self.close()
