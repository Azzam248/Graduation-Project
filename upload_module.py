import os
import sys
import mimetypes
import random
import time
import datetime
import json
import secrets
from encryption_options_window import EncryptionOptionsWindow
from PyQt5.QtWidgets import QListWidgetItem
from encrypt_window import EncryptHelper
from decrypt_window import DecryptWindow
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QFileDialog, QMessageBox, QListWidget, QLabel, QHBoxLayout
)
from PyQt5.QtCore import Qt

import boto3
import mysql.connector
from mysql.connector import Error


class UploadWindow(QWidget):

    def __init__(self, username, user_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle("File Storage")
        self.s3_bucket = "storagebh10"
        self.selected_file = None
        self.s3_client = boto3.client('s3')

        self.db_connection = None
        self.username = username
        self.user_id = user_id

        self.connect_to_database()
        self.setMinimumSize(700, 600)
        self.setStyleSheet("""/* your stylesheet here */""")
        self.init_ui()

    def connect_to_database(self):
        try:
            self.db_connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="root",
                database="filestoragedb"
            )
            print("Connected to MySQL database")
        except Error as e:
            print(f"Error connecting to MySQL database: {e}")
            QMessageBox.critical(self, "Database Error", f"Could not connect to the database: {e}")

    def init_ui(self):
        # إعداد التخطيط الرئيسي
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)  # مسافات بين الأقسام
        main_layout.setContentsMargins(20, 20, 20, 20)  # هوامش حول التخطيط

        # عنوان البرنامج
        title_label = QLabel("File Storage Manager")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2d3436;
            margin-bottom: 20px;
        """)
        main_layout.addWidget(title_label)

        # قسم الأزرار
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        # زر اختيار الملف
        self.select_button = QPushButton("Select File")
        self.select_button.setStyleSheet("""
            QPushButton {
                background-color: #dfe6e9;
                color: #2d3436;
                border: 1px solid #b2bec3;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #b2bec3;
            }
            QPushButton:pressed {
                background-color: #636e72;
                color: white;
            }
        """)
        self.select_button.clicked.connect(self.select_file)
        button_layout.addWidget(self.select_button)

        # زر رفع الملف
        self.upload_button = QPushButton("Upload File")
        self.upload_button.setStyleSheet("""
            QPushButton {
                background-color: #dfe6e9;
                color: #2d3436;
                border: 1px solid #b2bec3;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #b2bec3;
            }
            QPushButton:pressed {
                background-color: #636e72;
                color: white;
            }
        """)
        self.upload_button.clicked.connect(self.upload_file)
        button_layout.addWidget(self.upload_button)

        # زر تحديث قائمة الملفات
        self.refresh_button = QPushButton("Refresh Files List")
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #dfe6e9;
                color: #2d3436;
                border: 1px solid #b2bec3;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #b2bec3;
            }
            QPushButton:pressed {
                background-color: #636e72;
                color: white;
            }
        """)
        self.refresh_button.clicked.connect(self.load_uploaded_files)
        button_layout.addWidget(self.refresh_button)

        # زر حذف الملف
        self.delete_button = QPushButton("Delete File")
        self.delete_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: 1px solid #c0392b;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        self.delete_button.clicked.connect(self.delete_file)
        button_layout.addWidget(self.delete_button)

        main_layout.addLayout(button_layout)

        # قسم الملفات المرفوعة
        uploaded_label = QLabel("Uploaded Files")
        uploaded_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2d3436;")
        main_layout.addWidget(uploaded_label)

        self.uploaded_files_list = QListWidget()
        self.uploaded_files_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #b2bec3;
                border-radius: 8px;
                padding: 10px;
                background-color: #f5f6fa;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: #74b9ff;
                color: white;
            }
        """)
        self.uploaded_files_list.setSelectionMode(QListWidget.MultiSelection)
        main_layout.addWidget(self.uploaded_files_list)

        # قسم الملفات المفكوكة
        decrypted_label = QLabel("Decrypted Files")
        decrypted_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2d3436;")
        main_layout.addWidget(decrypted_label)

        self.decrypted_files_list = QListWidget()
        self.decrypted_files_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #b2bec3;
                border-radius: 8px;
                padding: 10px;
                background-color: #f5f6fa;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: #55efc4;
                color: white;
            }
        """)
        main_layout.addWidget(self.decrypted_files_list)

        # زر فتح الملف
        self.open_button = QPushButton("Open")
        self.open_button.setStyleSheet("""
            QPushButton {
                background-color: #dfe6e9;
                color: #2d3436;
                border: 1px solid #b2bec3;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #b2bec3;
            }
            QPushButton:pressed {
                background-color: #636e72;
                color: white;
            }
        """)
        self.open_button.clicked.connect(self.open_file)
        main_layout.addWidget(self.open_button)

        # إعداد التخطيط
        self.setLayout(main_layout)
        self.load_uploaded_files()

    def select_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select a File", "", "All Files (*)", options=options
        )
        if file_path:
            self.selected_file = file_path

    def upload_file(self):
        if not self.selected_file:
            QMessageBox.warning(self, "Warning", "Please select a file first!")
            return

        if not self.user_id:
            QMessageBox.warning(self, "Warning", "You must be logged in to upload files.")
            return

        self.encryption_window = EncryptionOptionsWindow(
            self.selected_file,
            self.username,
            self.user_id,
            self.s3_client,
            self.s3_bucket,
            self.db_connection
        )
        self.encryption_window.show()

    def load_uploaded_files(self):
        self.uploaded_files_list.clear()
        self.decrypted_files_list.clear()

        if not self.user_id:
            self.uploaded_files_list.addItem("Please log in to view your files")
            return

        # ✅ قراءة الملفات المفكوكة من JSON هنا داخل الدالة
        decrypted_names = []
        if os.path.exists("decrypted_files.json"):
            with open("decrypted_files.json", "r") as f:
                decrypted_names = json.load(f)

        try:
            user_prefix = f"user_{self.user_id}/"
            response = self.s3_client.list_objects_v2(
                Bucket=self.s3_bucket,
                Prefix=user_prefix
            )

            user_files = []

            if 'Contents' in response:
                for obj in response['Contents']:
                    file_key = obj['Key']
                    file_name = os.path.basename(file_key)

                    ext = os.path.splitext(file_name)[1]
                    file_type = EncryptHelper.get_file_type_from_extension(ext).upper()

                    item = QListWidgetItem(f"{file_name} ({file_type})")
                    item.setData(Qt.UserRole, file_key)

                    # ✅ أضف دائمًا إلى قائمة المشفرات
                    self.uploaded_files_list.addItem(item)

                    # ✅ إذا كان من المفكوكين حسب JSON، أضفه
                    if file_name.replace("enc_", "") in decrypted_names:
                        self.decrypted_files_list.addItem(QListWidgetItem(f"{file_name} (Decrypted)")) 
            else:
                self.uploaded_files_list.addItem("You haven't uploaded any files yet.")

        except Exception as e:
            self.uploaded_files_list.addItem(f"Error loading files: {str(e)[:50]}")

    def delete_file(self):
        selected_items = self.uploaded_files_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select one or more files to delete.")
            return

        # تأكيد الحذف
        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete {len(selected_items)} file(s)?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            for item in selected_items:
                try:
                    # استرجاع مفتاح الملف من خاصية UserRole
                    file_key = item.data(Qt.UserRole)
                    if not file_key:
                        QMessageBox.critical(self, "Error", "Could not retrieve the file key.")
                        continue

                    print(f"Deleting file with key: {file_key}")

                    # حذف الملف من S3
                    self.s3_client.delete_object(Bucket=self.s3_bucket, Key=file_key)

                    # حذف الملف من القائمة
                    self.uploaded_files_list.takeItem(self.uploaded_files_list.row(item))

                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to delete file '{file_key}' from S3: {str(e)}")

            QMessageBox.information(self, "Success", "Selected files deleted successfully.")

    def open_file(self):
        selected_item = self.uploaded_files_list.currentItem()
        if selected_item:
            filename = selected_item.text().split(" (")[0]
            self.decrypt_window = DecryptWindow(
                filename=filename,
                username=self.username,
                user_id=self.user_id,
                s3_client=self.s3_client,
                s3_bucket=self.s3_bucket,
                db_connection=self.db_connection,
                uploaded_list=self.uploaded_files_list,
                decrypted_list=self.decrypted_files_list
            )
        else:
            QMessageBox.warning(self, "تنبيه", "يرجى اختيار ملف من قائمة الملفات المشفرة.")

    def closeEvent(self, event):
        if self.db_connection and self.db_connection.is_connected():
            self.db_connection.close()
        event.accept()
