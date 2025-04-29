import os
import re
import datetime
from Crypto.Cipher import AES, Blowfish
from Crypto.Random import get_random_bytes
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from mysql.connector import Error

# ✅ دالة لترتيب أسماء الملفات
def normalize_filename(filename):
    filename = filename.strip().replace(' ', '_')
    filename = re.sub(r'[^A-Za-z0-9_.-]', '', filename)
    return filename

class EncryptHelper:

    @staticmethod
    def pad_data(data, block_size):
        pad_len = block_size - len(data) % block_size
        return data + bytes([pad_len] * pad_len)

    @staticmethod
    def get_file_type_from_extension(ext):
        ext = ext.lower()
        if ext in ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.tif', '.webp', '.ico', '.heic']:
            return "image"
        elif ext in ['.mp4', '.avi', '.mov', '.wmv', '.mkv', '.flv', '.webm', '.3gp', '.mpeg', '.mpg']:
            return "video"
        else:
            return "file"

    @staticmethod
    def encrypt_file(file_path, encryption_type, username, user_id, s3_client, s3_bucket, db_connection):
        with open(file_path, 'rb') as f:
            plaintext = f.read()

        file_name = os.path.basename(file_path)
        file_ext = os.path.splitext(file_name)[1].lower()

        # ✅ استخدام normalize_filename لحماية اسم الملف
        encrypted_filename = normalize_filename(f"enc_{file_name}")
        encrypted_path = os.path.join("temp", encrypted_filename)
        os.makedirs("temp", exist_ok=True)

        if encryption_type == "ChaCha20":
            key = ChaCha20Poly1305.generate_key()
            iv = os.urandom(12)
            cipher = ChaCha20Poly1305(key)
            ciphertext = cipher.encrypt(iv, plaintext, None)

            # تحقق من نجاح فك التشفير محليًا قبل الحفظ
            try:
                test_cipher = ChaCha20Poly1305(key)
                _ = test_cipher.decrypt(iv, ciphertext, None)
                print("✅ Local ChaCha20 decryption passed.")
            except Exception as e:
                raise ValueError(f"❌ Local ChaCha20 decryption failed: {repr(e)}")

        elif encryption_type == "AES":
            key = get_random_bytes(16)
            iv = get_random_bytes(16)
            cipher = AES.new(key, AES.MODE_CBC, iv)
            padded = EncryptHelper.pad_data(plaintext, 16)
            ciphertext = cipher.encrypt(padded)

        elif encryption_type == "Blowfish":
            key = get_random_bytes(16)
            iv = get_random_bytes(8)
            cipher = Blowfish.new(key, Blowfish.MODE_CBC, iv)
            padded = EncryptHelper.pad_data(plaintext, 8)
            ciphertext = cipher.encrypt(padded)

        else:
            raise ValueError("Unsupported encryption type")

        with open(encrypted_path, 'wb') as f:
            f.write(ciphertext)

        # ✅ تأكد من أن الملف انكتب بشكل صحيح
        if os.path.getsize(encrypted_path) != len(ciphertext):
            raise ValueError("❌ Size mismatch: File was not written correctly.")

        # ✅ رفع الملف إلى S3 بعد نجاح كل شيء
        s3_key = f"user_{user_id}/{encrypted_filename}"
        s3_client.upload_file(encrypted_path, s3_bucket, s3_key)

        # ✅ تسجيل معلومات التشفير في قاعدة البيانات
        try:
            cursor = db_connection.cursor()
            cursor.execute(
                "INSERT INTO encryptionmethod (EncryptionType, EncryptionKey, IV) VALUES (%s, %s, %s)",
                (encryption_type, key.hex(), iv.hex())
            )
            encryption_id = cursor.lastrowid

            file_type = EncryptHelper.get_file_type_from_extension(file_ext)
            upload_date = datetime.datetime.now()

            if file_type == "image":
                cursor.execute(
                    "INSERT INTO image (UserID, ImageName, EncryptionID, OriginalName, UploadDate) VALUES (%s, %s, %s, %s, %s)",
                    (user_id, encrypted_filename, encryption_id, file_name, upload_date)
                )
            elif file_type == "video":
                cursor.execute(
                    "INSERT INTO video (UserID, VideoName, EncryptionID, OriginalName, UploadDate) VALUES (%s, %s, %s, %s, %s)",
                    (user_id, encrypted_filename, encryption_id, file_name, upload_date)
                )
            else:
                cursor.execute(
                    "INSERT INTO file (UserID, FileName, EncryptionID, OriginalName, UploadDate) VALUES (%s, %s, %s, %s, %s)",
                    (user_id, encrypted_filename, encryption_id, file_name, upload_date)
                )

            db_connection.commit()
            cursor.close()

        except Error as e:
            raise Exception(f"Database error: {str(e)}")

        finally:
            if os.path.exists(encrypted_path):
                os.remove(encrypted_path)

        print(f"[ENCRYPT ✅] {file_name} encrypted and uploaded as {encrypted_filename}")
