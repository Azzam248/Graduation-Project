import sys
from calendar import day_name

from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QPushButton,
                             QVBoxLayout, QHBoxLayout, QMessageBox, QDateEdit,
                             QGroupBox, QGridLayout, QTabWidget, QFormLayout,
                             QFrame, QScrollArea)
from PyQt5.QtCore import QDate, Qt

import mysql.connector
from PyQt5.QtGui import QGuiApplication

class DatabaseApp(QWidget):
    def __init__(self, username, user_id):
        super().__init__()
        self.username = username
        self.user_id = user_id
        self.user_data = {}
        self.capture_face = None
        from login import capture_face
        self.capture_face = capture_face

        self.initUI()
        self.initDB()
        self.load_user_data()

    def initUI(self):
        # Set up the UI


        self.setWindowTitle('User Profile')
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("""
            QWidget {
                font-family: Arial;
                font-size: 12px;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        self.center_window()

        # Main layout
        main_layout = QVBoxLayout()

        # Header
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: #4a90e2; padding: 10px;")
        header_frame.setMinimumHeight(60)
        header_layout = QHBoxLayout(header_frame)

        title_label = QLabel(f"Profile Management")
        title_label.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title_label)

        back_button = QPushButton("Back to Dashboard")
        back_button.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: black;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """)
        back_button.clicked.connect(self.go_back_to_dashboard)
        header_layout.addWidget(back_button, alignment=Qt.AlignRight)

        main_layout.addWidget(header_frame)

        # Create tabs
        tab_widget = QTabWidget()

        # Profile Info Tab
        profile_tab = QWidget()
        profile_layout = QVBoxLayout(profile_tab)

        # User info display
        info_group = QGroupBox("User Information")
        info_layout = QFormLayout()

        self.info_username = QLabel("")
        self.info_phone = QLabel("")
        self.info_city = QLabel("")
        self.info_birthday = QLabel("")

        info_layout.addRow(QLabel("Username:"), self.info_username)
        info_layout.addRow(QLabel("Phone:"), self.info_phone)
        info_layout.addRow(QLabel("City:"), self.info_city)
        info_layout.addRow(QLabel("Birthday:"), self.info_birthday)
        self.setStyleSheet("""
            QLabel {
              font-size: 16px;
                font-weight: bold;
                color: #333;
                 background-color: #f0f0f0;
                 padding: 5px;
                 border-radius: 5px;
                  color: black;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
                  
                  
                   
                 
   


            }
            """)

        info_group.setLayout(info_layout)
        profile_layout.addWidget(info_group)

        # Edit Profile Tab
        edit_tab = QWidget()
        edit_layout = QVBoxLayout(edit_tab)

        # Edit profile form
        edit_form = QGroupBox("Edit Profile")
        edit_form_layout = QFormLayout()

        self.phone_input = QLineEdit()
        self.city_input = QLineEdit()
        self.birthday_input = QDateEdit()
        self.birthday_input.setDisplayFormat("yyyy-MM-dd")
        self.birthday_input.setCalendarPopup(True)

        edit_form_layout.addRow(QLabel("Phone Number:"), self.phone_input)
        edit_form_layout.addRow(QLabel("City:"), self.city_input)
        edit_form_layout.addRow(QLabel("Birthday:"), self.birthday_input)

        update_button = QPushButton("Update Profile")
        update_button.setStyleSheet("""
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #357ab7;
            }
        """)
        update_button.clicked.connect(self.update_user_data)

        edit_form_layout.addRow("", update_button)
        edit_form.setLayout(edit_form_layout)
        edit_layout.addWidget(edit_form)

        # Account Security Tab
        security_tab = QWidget()
        security_layout = QVBoxLayout(security_tab)

        # Username change
        username_group = QGroupBox("Change Username")
        username_layout = QFormLayout()

        self.new_username = QLineEdit()
        change_username_button = QPushButton("Change Username")
        change_username_button.setStyleSheet("""
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #357ab7;
            }
        """)
        change_username_button.clicked.connect(self.change_username)

        username_layout.addRow(QLabel("New Username:"), self.new_username)
        username_layout.addRow("", change_username_button)
        username_group.setLayout(username_layout)
        security_layout.addWidget(username_group)

        # Password reset
        password_group = QGroupBox("Reset Password")
        password_layout = QFormLayout()

        self.current_password = QLineEdit()
        self.current_password.setEchoMode(QLineEdit.Password)
        self.new_password = QLineEdit()
        self.new_password.setEchoMode(QLineEdit.Password)
        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.Password)

        reset_password_button = QPushButton("Reset Password")
        reset_password_button.setStyleSheet("""
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #357ab7;
            }
        """)
        reset_password_button.clicked.connect(self.reset_password)

        password_layout.addRow(QLabel("Current Password:"), self.current_password)
        password_layout.addRow(QLabel("New Password:"), self.new_password)
        password_layout.addRow(QLabel("Confirm Password:"), self.confirm_password)
        password_layout.addRow("", reset_password_button)
        password_group.setLayout(password_layout)
        security_layout.addWidget(password_group)

        # Face Recognition Tab
        face_tab = QWidget()
        face_layout = QVBoxLayout(face_tab)

        face_group = QGroupBox("Face Recognition")
        face_group_layout = QVBoxLayout()

        face_info = QLabel("Set up facial recognition for quicker login")
        face_info.setStyleSheet("margin-bottom: 15px;")

        self.face_login_button = QPushButton('Setup Face Login')
        self.face_login_button.setStyleSheet("""
            QPushButton {
                background-color: #4267B2;  /* Facebook blue */
                color: white;
                border: none;
                border-radius: 5px;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #365899;  /* Darker blue on hover */
            }
            QPushButton:pressed {
                background-color: #2d4373;  /* Even darker when clicked */
            }
        """)
        self.face_login_button.clicked.connect(lambda: self.capture_face(self.username))

        face_group_layout.addWidget(face_info)
        face_group_layout.addWidget(self.face_login_button, alignment=Qt.AlignCenter)
        face_group_layout.addStretch()

        face_group.setLayout(face_group_layout)
        face_layout.addWidget(face_group)

        # Add tabs to widget
        tab_widget.addTab(profile_tab, "Profile Info")
        tab_widget.addTab(edit_tab, "Edit Profile")
        tab_widget.addTab(security_tab, "Account Security")
        tab_widget.addTab(face_tab, "Face Login")

        main_layout.addWidget(tab_widget)

        self.setLayout(main_layout)


    def center_window(self):
        screen = QGuiApplication.primaryScreen()  # Get primary screen
        screen_geometry = screen.geometry()  # Get screen dimensions
        window_geometry = self.frameGeometry()  # Get window dimensions
        window_geometry.moveCenter(screen_geometry.center())  # Move window to center
        self.move(window_geometry.topLeft())  # Set new position

    def initDB(self):
        # Connect to MySQL database
        try:
            self.conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="root",
                database="filestoragedb"
            )
            self.cursor = self.conn.cursor(dictionary=True)
        except mysql.connector.Error as e:
            QMessageBox.critical(self, 'Database Error', f'Failed to connect to MySQL: {e}')

    def load_user_data(self):
        try:
            # Fetch user data
            self.cursor.execute('''
                SELECT UserName, PhoneNum, City, Birthday
                FROM user 
                WHERE UserID = %s
            ''', (self.user_id,))

            result = self.cursor.fetchone()

            if result:
                self.user_data = result
                # Update display labels
                self.info_username.setText(result.get('UserName', ''))
                self.info_phone.setText(result.get('PhoneNum', ''))
                self.info_city.setText(result.get('City', ''))

                # Format birthday if available
                birthday = result.get('Birthday')
                if birthday:
                    self.info_birthday.setText(birthday.strftime('%Y-%m-%d'))
                    # Set the date in the date edit
                    self.birthday_input.setDate(QDate(birthday.year, birthday.month, birthday.day))

                # Fill the edit fields
                self.phone_input.setText(result.get('PhoneNum', ''))
                self.city_input.setText(result.get('City', ''))

        except mysql.connector.Error as e:
            QMessageBox.critical(self, 'Database Error', f'Failed to load user data: {e}')

    def update_user_data(self):
        phone = self.phone_input.text()
        city = self.city_input.text()
        birthday = self.birthday_input.date().toString("yyyy-MM-dd")

        try:
            self.cursor.execute('''
                UPDATE user 
                SET PhoneNum = %s, City = %s, Birthday = %s 
                WHERE UserID = %s
            ''', (phone, city, birthday, self.user_id))

            self.conn.commit()
            QMessageBox.information(self, 'Success', 'Profile updated successfully!')
            self.load_user_data()  # Refresh displayed data

        except mysql.connector.Error as e:
            QMessageBox.critical(self, 'Error', f'An error occurred updating profile: {e}')

    def change_username(self):
        new_username = self.new_username.text()
        min_username_length = 4
        max_username_length = 20

        if not (min_username_length <= len(new_username) <= max_username_length):
            QMessageBox.warning(self,'input error',
                f"Username must be between 4 to 16 characters")
            return

        if not new_username:
            QMessageBox.warning(self, 'Input Error', 'Please enter a new username')
            return

        try:
            # Check if username already exists
            self.cursor.execute('''
                SELECT COUNT(*) as count
                FROM user
                WHERE UserName = %s AND UserID != %s
            ''', (new_username, self.user_id))

            result = self.cursor.fetchone()

            if result['count'] > 0:
                QMessageBox.warning(self, 'Username Error', 'This username is already taken')
                return

            # Update username
            self.cursor.execute('''
                UPDATE user
                SET UserName = %s
                WHERE UserID = %s
            ''', (new_username, self.user_id))

            self.conn.commit()
            self.username = new_username
            QMessageBox.information(self, 'Success', 'Username changed successfully!')
            self.new_username.clear()
            self.load_user_data()

        except mysql.connector.Error as e:
            QMessageBox.critical(self, 'Error', f'An error occurred changing username: {e}')

    def reset_password(self):
        current_pwd = self.current_password.text()
        new_pwd = self.new_password.text()
        confirm_pwd = self.confirm_password.text()
        min_password_length = 6
        max_password_length = 30

        if not current_pwd or not new_pwd or not confirm_pwd:
            QMessageBox.warning(self, 'Input Error', 'Please fill in all password fields')
            return

        if new_pwd != confirm_pwd:
            QMessageBox.warning(self, 'Password Error', 'New passwords do not match')
            return

        if not (min_password_length <= len(new_pwd) <= max_password_length):
            QMessageBox.warning(self, 'Input Error', 'password must be between 6 to 30 characters')
            return

        try:
            # Verify current password
            self.cursor.execute('''
                SELECT Password
                FROM user
                WHERE UserID = %s
            ''', (self.user_id,))

            result = self.cursor.fetchone()

            if result and result['Password'] != current_pwd:
                QMessageBox.warning(self, 'Password Error', 'Current password is incorrect')
                return

            # Update password
            self.cursor.execute('''
                UPDATE user
                SET Password = %s
                WHERE UserID = %s
            ''', (new_pwd, self.user_id))

            self.conn.commit()
            QMessageBox.information(self, 'Success', 'Password reset successfully!')

            # Clear password fields
            self.current_password.clear()
            self.new_password.clear()
            self.confirm_password.clear()

        except mysql.connector.Error as e:
            QMessageBox.critical(self, 'Error', f'An error occurred resetting password: {e}')

    def go_back_to_dashboard(self):
        # Import here to avoid circular import
        from login import Dashboard
        self.dashboard = Dashboard(self.username, self.user_id)
        self.dashboard.show()
        self.close()

    def closeEvent(self, event):
        # Close the database connection when the application is closed
        if hasattr(self, 'conn') and self.conn.is_connected():
            self.cursor.close()
            self.conn.close()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DatabaseApp()
    ex.show()
    sys.exit(app.exec_())
