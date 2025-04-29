import sys
import cv2
import mysql.connector
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QPushButton,
                             QVBoxLayout, QHBoxLayout, QMessageBox, QFrame, QMainWindow)


from PyQt5.QtCore import Qt
from dashboard import Dashboard  # Import the Dashboard class from dashboard.py
import json
from PyQt5.QtGui import QGuiApplication
# Database Setup
def init_db():
    conn = mysql.connector.connect(host="localhost", user="root", password="root",
                                   database="filestoragedb")
    cursor = conn.cursor()

    conn.commit()
    conn.close()


# Face Recognition Functions

def capture_face(username):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    cap = cv2.VideoCapture(0)

    # Create window with instructions
    cv2.namedWindow("Capture Face", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Capture Face", 640, 480)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        # Draw rectangle and instructions
        cv2.putText(frame, "Position your face in the frame and press SPACE", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, "Press Q to cancel", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        for (x, y, w, h) in faces:
            # Draw rectangle around detected face
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        cv2.imshow("Capture Face", frame)
        key = cv2.waitKey(1) & 0xFF

        # Space key to capture
        if key == 32 and len(faces) > 0:
            for (x, y, w, h) in faces:
                face = frame[y:y + h, x:x + w]

                # Convert the face image to binary data
                _, img_encoded = cv2.imencode('.jpg', face)
                img_binary = img_encoded.tobytes()

                # Save binary data in the database
                conn = mysql.connector.connect(host="localhost", user="root", password="root",
                                               database="filestoragedb")
                cursor = conn.cursor()
                cursor.execute("UPDATE user SET ProfileImage=%s WHERE UserName=%s", (img_binary, username))
                conn.commit()
                conn.close()

                cap.release()
                cv2.destroyAllWindows()
                return "Face captured and saved in the database."

        # Q key to quit
        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return None


def recognize_face():
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open camera.")
        return None

    # Create window with instructions
    cv2.namedWindow("Face Recognition", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Face Recognition", 640, 480)

    # Retrieve stored faces from the database
    try:
        conn = mysql.connector.connect(host="localhost", user="root", password="root",
                                       database="filestoragedb")
        cursor = conn.cursor()
        cursor.execute("SELECT UserName, UserID, ProfileImage FROM user WHERE ProfileImage IS NOT NULL")
        users = cursor.fetchall()
        conn.close()

        if not users:
            print("No users with face data found in the database.")
            cap.release()
            cv2.destroyAllWindows()
            return None
    except mysql.connector.Error as err:
        print(f"Database error when retrieving faces: {err}")
        cap.release()
        cv2.destroyAllWindows()
        return None

    attempts = 0
    max_attempts = 100  # About 5 seconds at 6 FPS

    # Make sure temp directories exist
    temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp")
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    temp_path = os.path.join(temp_dir, "temp_face.jpg")
    stored_face_path = os.path.join(temp_dir, "temp_stored_face.jpg")

    while attempts < max_attempts:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame from camera.")
            break

        attempts += 1
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        # Add instructions
        cv2.putText(frame, "Looking for your face...", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"Attempt {attempts}/{max_attempts}", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        for (x, y, w, h) in faces:
            # Draw rectangle around detected face
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

            face = frame[y:y + h, x:x + w]
            try:
                # Save current face to temp file
                cv2.imwrite(temp_path, face)

                # Compare with stored faces
                for username, user_id, profile_image in users:
                    if profile_image is not None:
                        # Save the binary data to a temporary file
                        with open(stored_face_path, "wb") as file:
                            file.write(profile_image)

                        stored_face = cv2.imread(stored_face_path)
                        if stored_face is not None:
                            # Resize both images to the same dimensions for comparison
                            try:
                                stored_face_resized = cv2.resize(stored_face, (face.shape[1], face.shape[0]))

                                # Convert both to grayscale for better comparison
                                gray_face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
                                gray_stored = cv2.cvtColor(stored_face_resized, cv2.COLOR_BGR2GRAY)

                                # Calculate the Mean Squared Error (MSE) between the two images
                                diff = cv2.absdiff(gray_face, gray_stored)
                                mse = (diff ** 2).mean()

                                print(f"MSE for user {username}: {mse}")

                                # If MSE is below a threshold, consider it a match
                                # Using a higher threshold for better matching
                                if mse < 8000:  # Increased from 5000
                                    print(f"Face recognized for user: {username}")
                                    cap.release()
                                    cv2.destroyAllWindows()

                                    # Clean up temp files
                                    try:
                                        if os.path.exists(temp_path):
                                            os.remove(temp_path)
                                        if os.path.exists(stored_face_path):
                                            os.remove(stored_face_path)
                                    except Exception as e:
                                        print(f"Error removing temp files: {e}")

                                    return username, user_id
                            except Exception as e:
                                print(f"Error comparing faces: {e}")
                                continue
            except Exception as e:
                print(f"Error processing face: {e}")
                continue

        cv2.imshow("Face Recognition", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Face recognition process cancelled by user.")
            break

    cap.release()
    cv2.destroyAllWindows()

    # Clean up temp files
    try:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        if os.path.exists(stored_face_path):
            os.remove(stored_face_path)
    except Exception as e:
        print(f"Error removing temp files: {e}")

    print("Face not recognized.")
    return None


# Styled Components
class StyledLineEdit(QLineEdit):
    def __init__(self, placeholder=""):
        super().__init__()
        self.setPlaceholderText(placeholder)
        self.setMinimumHeight(40)
        self.setStyleSheet("""
            QLineEdit {
                border: 2px solid #ccc;
                border-radius: 5px;
                padding: 5px 10px;
                background-color: #f8f8f8;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #4a90e2;
                background-color: white;
            }
        """)



class StyledButton(QPushButton):
    def __init__(self, text, primary=True):
        super().__init__(text)
        self.setMinimumHeight(40)
        if primary:
            self.setStyleSheet("""
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
            self.setStyleSheet("""
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


class PasswordResetWindow(QWidget):
    def __init__(self, username, user_id):
        super().__init__()
        self.username = username
        self.user_id = user_id
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Reset Password")
        self.setGeometry(300, 300, 400, 300)
        self.center_window()

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)

        # Title
        title_label = QLabel(f"Reset Password for {self.username}")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 15px;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # New password field
        new_password_label = QLabel("New Password:")
        new_password_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.new_password_input = StyledLineEdit("Enter new password")
        self.new_password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(new_password_label)
        layout.addWidget(self.new_password_input)

        # Confirm password field
        confirm_password_label = QLabel("Confirm Password:")
        confirm_password_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.confirm_password_input = StyledLineEdit("Confirm new password")
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(confirm_password_label)
        layout.addWidget(self.confirm_password_input)

        # Reset button
        self.reset_button = StyledButton("Reset Password")
        self.reset_button.clicked.connect(self.reset_password)
        layout.addWidget(self.reset_button)

        # Cancel button
        self.cancel_button = StyledButton("Cancel", False)
        self.cancel_button.clicked.connect(self.close)
        layout.addWidget(self.cancel_button)

        # Status message
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #d9534f; font-size: 14px; min-height: 20px;")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def center_window(self):
        screen = QGuiApplication.primaryScreen()
        screen_geometry = screen.geometry()
        window_geometry = self.frameGeometry()
        window_geometry.moveCenter(screen_geometry.center())
        self.move(window_geometry.topLeft())

    def reset_password(self):
        new_password = self.new_password_input.text()
        confirm_password = self.confirm_password_input.text()

        min_password_length = 6
        max_password_length = 30

        if not (min_password_length <= len(new_password) <= max_password_length):
            QMessageBox.warning(self, 'Input Error', 'password must be between 6 to 30 characters')
            return

        # Validate input
        if not new_password or not confirm_password:
            self.status_label.setText("Please fill in all fields")
            return

        if new_password != confirm_password:
            self.status_label.setText("Passwords do not match")
            return

        # Update password in database
        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="root",
                                           database="filestoragedb")
            cursor = conn.cursor()
            cursor.execute("UPDATE user SET Password=%s WHERE UserID=%s", (new_password, self.user_id))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Success", "Password reset successfully!")
            self.close()

        except mysql.connector.Error as err:
            self.status_label.setText(f"Database error: {err}")

# Main Login UI
class LoginApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("File Manager")
        self.setGeometry(100, 100, 500, 600)
        self.center_window()

        self.setStyleSheet("background-color: #f0f0f0;")


        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(40, 40, 40, 40)

        # App title
        title_label = QLabel("Secure Login")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #333; margin-bottom: 20px;")
        main_layout.addWidget(title_label)

        # Login form
        form_frame = QFrame()
        form_frame.setStyleSheet("""
                    QFrame {
                        background-color: white;
                        border-radius: 10px;
                        padding: 20px;
                    }
                """)
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(15)

        # Username field
        username_label = QLabel("Username")
        username_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.username_input = StyledLineEdit("Enter your username")
        form_layout.addWidget(username_label)
        form_layout.addWidget(self.username_input)

        # Password field
        password_label = QLabel("Password")
        password_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.password_input = StyledLineEdit("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password_input)

        # Login button
        self.login_button = StyledButton("Login")
        self.login_button.clicked.connect(self.login)
        form_layout.addWidget(self.login_button)

        # Register button
        self.register_button = StyledButton("Register", False)
        self.register_button.clicked.connect(self.register)
        form_layout.addWidget(self.register_button)

        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setFrameShadow(QFrame.Sunken)
        divider.setStyleSheet("background-color: #ddd;")
        form_layout.addWidget(divider)

        # Face login button
        face_login_layout = QHBoxLayout()
        face_login_label = QLabel("Or login with:")
        face_login_label.setStyleSheet("font-size: 14px;")
        face_login_layout.addWidget(face_login_label)

        self.face_login_button = StyledButton("Face Recognition", False)
        self.face_login_button.setStyleSheet("""
            QPushButton {
                background-color: #4267B2;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #365899;
            }
        """)
        self.face_login_button.clicked.connect(self.face_login)
        face_login_layout.addWidget(self.face_login_button)

        form_layout.addLayout(face_login_layout)

        main_layout.addWidget(form_frame)

        #NEW
        forgot_layout = QHBoxLayout()
        forgot_layout.addStretch()

        # Create the forgot password button
        self.forgot_button = QPushButton("Forgot Password?")
        self.forgot_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #4a90e2;
                border: none;
                font-size: 13px;
                text-decoration: underline;
            }
            QPushButton:hover {
                color: #357ab7;
            }
        """)
        self.forgot_button.setCursor(Qt.PointingHandCursor)
        self.forgot_button.clicked.connect(self.forgot_password)
        forgot_layout.addWidget(self.forgot_button)

        # Add the horizontal layout to the form layout
        form_layout.addLayout(forgot_layout)

        # Status messages
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #d9534f; font-size: 14px; min-height: 20px;")
        self.status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_label)

    def open_dashboard(self, username, user_id):
        self.dashboard = Dashboard(username, user_id)
        self.dashboard.show()
        self.close()

    def center_window(self):
        screen = QGuiApplication.primaryScreen()  # Get primary screen
        screen_geometry = screen.geometry()  # Get screen dimensions
        window_geometry = self.frameGeometry()  # Get window dimensions
        window_geometry.moveCenter(screen_geometry.center())  # Move window to center
        self.move(window_geometry.topLeft())  # Set new position

    def update_premium_access(username, is_premium):
        try:
            # Load existing premium access data
            with open("premium_access.json", "r") as file:
                premium_data = json.load(file)
        except FileNotFoundError:
            premium_data = {}  # Create a new dictionary if file doesn't exist

        # Update the user's premium status
        premium_data[username] = is_premium

        # Save the updated data back to JSON
        with open("premium_access.json", "w") as file:
            json.dump(premium_data, file, indent=4)

        print(f"Premium status updated for '{username}': {is_premium}")


    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            self.status_label.setText("Please enter both username and password")
            return

        if username == "admin" and password == "helloworld":
            self.status_label.setText("")
            # Open admin panel
            from admin_panel import AdminPanel
            self.admin_panel = AdminPanel("admin")
            self.admin_panel.show()
            self.close()
            return  # Exit the function after opening admin panel

            # Regular user login
        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="root",
                                           database="filestoragedb")
            cursor = conn.cursor()

            cursor.execute("SELECT Password, UserID FROM user WHERE UserName=%s", (username,))
            user = cursor.fetchone()
            conn.close()

            if user and user[0] == password:
                self.status_label.setText("")
                user_id = user[1]
                self.open_dashboard(username, user_id)
            else:
                self.status_label.setText("Invalid username or password")
        except mysql.connector.Error as err:
            self.status_label.setText(f"Database error: {err}")

        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="root",
                                           database="filestoragedb")
            cursor = conn.cursor()

            cursor.execute("SELECT  Password, UserID FROM user WHERE UserName=%s", (username,))
            user = cursor.fetchone()
            conn.close()

            if user and user[0] == password:
                self.status_label.setText("")
                user_id = user[1]
                self.open_dashboard(username, user_id)
            else:
                self.status_label.setText("Invalid username or password")
        except mysql.connector.Error as err:
            self.status_label.setText(f"Database error: {err}")

    def register(self):
        username = self.username_input.text()
        password = self.password_input.text()

        # Define constraints
        min_username_length = 4
        max_username_length = 20
        min_password_length = 6
        max_password_length = 30

        # Validate username length
        if not (min_username_length <= len(username) <= max_username_length):
            self.status_label.setText(
                f"Username must be between {min_username_length}-{max_username_length} characters")
            return

        # Validate password length
        if not (min_password_length <= len(password) <= max_password_length):
            self.status_label.setText(
                f"Password must be between {min_password_length}-{max_password_length} characters")
            return

        if not username or not password:
            self.status_label.setText("Please enter both username and password")
            return

        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="root",
                                           database="filestoragedb")
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM user WHERE UserName = %s", (username,))
            result = cursor.fetchone()

            if result[0] > 0:
                self.status_label.setText("Username already exists. Please choose a different one.")
                return  # Exit the function

            cursor.execute("INSERT INTO user (UserName, Password) VALUES (%s, %s)", (username, password))
            conn.commit()

            LoginApp.update_premium_access(username, False)




            # Ask user if they want to add face recognition
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Face Recognition")
            msg_box.setText("Registration successful! Would you like to add face recognition for quicker login?")
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            response = msg_box.exec_()

            if response == QMessageBox.Yes:
                face_path = capture_face(username)
                if face_path:

                    self.status_label.setText("Registration with face complete!")

                else:
                    self.status_label.setText("Registration successful, but face capture was cancelled")
            else:
                self.status_label.setText("Registration successful!")

        except mysql.connector.Error as err:
            if err.errno == 1062:  # Duplicate entry error
                self.status_label.setText("Username already exists")
            else:
                self.status_label.setText(f"Registration error: {err}")
        finally:
            conn.close()

    def face_login(self):

        self.status_label.setText("Looking for your face...")
        result = recognize_face()

        if result:
            username, user_id = result
            self.status_label.setText("Face recognized!")
            self.open_dashboard(username, user_id)
        else:
            self.status_label.setText("Face not recognized or process cancelled")

    def forgot_password(self):
        self.status_label.setText("Please look at the camera for verification...")
        result = recognize_face()

        if result:
            username, user_id = result
            self.status_label.setText("Face recognized! Opening password reset window...")
            self.reset_window = PasswordResetWindow(username, user_id)
            self.reset_window.show()
        else:
            self.status_label.setText("Face not recognized or process cancelled")






# Main execution
if __name__ == "__main__":
    try:
        init_db()
        app = QApplication(sys.argv)
        app.setStyle('Fusion')  # Use Fusion style for a modern look
        window = LoginApp()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Error starting application: {e}")




