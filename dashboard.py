from PyQt5.QtWidgets import (QMainWindow, QWidget, QLabel, QPushButton,
                             QVBoxLayout, QHBoxLayout, QFrame, QGridLayout, QStatusBar,QApplication,QDialog)
from PyQt5.QtCore import Qt, QSize, QThread, pyqtSignal
import sys
import time

from upload_module import UploadWindow
from PyQt5.QtGui import QGuiApplication
from help import Help1




class Dashboard(QMainWindow):
    """
    Dashboard window displayed after successful login.
    Provides access to various features of the application.
    """

    def __init__(self, username,user_id):
        super().__init__()
        self.username = username
        self.user_id = user_id


        self.upload_window = None
        self.upload_button = QPushButton("Upload Files")
        self.upload_button.clicked.connect(self.open_files)

        self.initUI()

    def initUI(self):
        """Initialize the user interface components"""
        self.setWindowTitle("User Dashboard")
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
        header_frame.setMinimumHeight(100)
        header_layout = QHBoxLayout(header_frame)

        welcome_label = QLabel(f"Welcome, {self.username}!")
        welcome_label.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        header_layout.addWidget(welcome_label)

        logout_button = self.create_button("Logout", False)
        logout_button.setMaximumWidth(120)
        logout_button.clicked.connect(self.logout)
        header_layout.addWidget(logout_button, alignment=Qt.AlignRight)

        main_layout.addWidget(header_frame)

        # Content area
        content_frame = QFrame()
        content_frame.setStyleSheet("background-color: white;")
        content_layout = QVBoxLayout(content_frame)

        # Info label
        info_label = QLabel("Your secure dashboard")
        info_label.setStyleSheet("font-size: 18px; margin: 20px 0;")
        content_layout.addWidget(info_label, alignment=Qt.AlignCenter)

        # Grid of feature buttons
        features_grid = QGridLayout()

        features = [
            ("Files", self.open_files),
            ("Profile", self.open_profile),
            ("Settings", self.open_settings),
            ("Help", self.open_help)
        ]

        row, col = 0, 0
        for feature_name, feature_func in features:
            feature_button = QPushButton(feature_name)
            feature_button.setMinimumSize(QSize(150, 150))
            feature_button.clicked.connect(feature_func)
            feature_button.setStyleSheet("""
                QPushButton {
                    background-color: #f8f8f8;
                    border: 1px solid #ddd;
                    border-radius: 10px;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #e8e8e8;
                    border: 1px solid #ccc;
                }
            """)
            features_grid.addWidget(feature_button, row, col)

            col += 1
            if col > 1:
                col = 0
                row += 1

        content_layout.addLayout(features_grid)
        content_layout.addStretch()

        main_layout.addWidget(content_frame)

        # Status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Logged in successfully")

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

    def logout(self):
        """Handle logout - close dashboard and reopen login window"""
        self.close()
        # We need to import here to avoid circular import
        from login import LoginApp
        self.login_app = LoginApp()
        self.login_app.show()

    # Placeholder functions for dashboard features
    def open_files(self):

        self.upload_window1 = UploadWindow(self.username, self.user_id)
        self.upload_window1.show()
        self.close()

    def open_profile(self):

        from profile import DatabaseApp

        self.database_window = DatabaseApp(self.username, self.user_id)
        self.database_window.show()
        self.close()





    def open_settings(self ):
        from settings import SettingsWindow

        self.settings_window = SettingsWindow(self.username, self.user_id)
        self.settings_window.show()
        self.close()

    def open_help(self):

        self.help_window = Help1(self.username, self.user_id)
        self.help_window.show()
        self.close()





