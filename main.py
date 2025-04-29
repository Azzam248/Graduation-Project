import sys
from PyQt5.QtWidgets import QApplication
from login import LoginApp, init_db

if __name__ == "__main__":
    try:
        # Initialize database
        init_db()

        # Create and run application
        app = QApplication(sys.argv)
        app.setStyle('Fusion')  # Use Fusion style for a modern look

        # Show login window
        window = LoginApp()
        window.show()

        # Start application event loop
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Error starting application: {e}")
