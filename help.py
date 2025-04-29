from PyQt5.QtWidgets import (QGroupBox, QWidget, QLabel, QVBoxLayout,
                             QScrollArea, QPushButton, QHBoxLayout, QFrame,QSizePolicy,QSpacerItem)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QGuiApplication,QFont,QIcon

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                             QLabel, QPushButton, QFrame, QSpacerItem,
                             QSizePolicy, QScrollArea)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                             QLabel, QPushButton, QFrame, QSpacerItem,
                             QSizePolicy, QScrollArea)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon


class Help1(QWidget):
    def __init__(self, username, user_id):
        super().__init__()
        self.username = username
        self.user_id = user_id
        self.initUI()

    def initUI(self):
        # Set up the UI
        self.setWindowTitle('Help')
        self.setGeometry(100, 100, 800, 600)

        # Style sheet to match the screenshot exactly
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12px;
                background-color: white;
                color: #333;
            }
            QFrame#leftSidebar {
                background-color: #4b89dc;
                min-width: 12px;
            }
            QFrame#headerFrame {
                background-color: #4b89dc;
            }
            QPushButton#logoutBtn {
                background-color: white;
                color: #333;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton#backBtn {
                background-color: #4b89dc;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                text-align: left;
            }
            QGroupBox {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 10px;
                margin-top: 0px;
            }
            QLabel#titleLabel {
                font-size: 18px;
                font-weight: bold;
                color: #333;
            }
            QLabel#categoryLabel {
                font-weight: bold;
                font-size: 13px;
                margin-bottom: 5px;
            }
            QFrame#statusBar {
                background-color: #f0f0f0;
                color: #333;
                min-height: 25px;
            }
        """)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Top section with blue header
        top_section = QHBoxLayout()

        # Left sidebar (blue bar)
        left_sidebar = QFrame()
        left_sidebar.setObjectName("leftSidebar")

        # Header area
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_frame.setMinimumHeight(70)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 0, 20, 0)

        # Add logout button at the right side of the header
        logout_btn = QPushButton("Back to dashboard")
        logout_btn.setObjectName("logoutBtn")
        logout_btn.setMinimumWidth(80)
        header_layout.addStretch()
        header_layout.addWidget(logout_btn,alignment=Qt.AlignRight)
        logout_btn.clicked.connect(self.back_to_dashboard)

        top_section.addWidget(left_sidebar)
        top_section.addWidget(header_frame, 1)

        main_layout.addLayout(top_section)

        # Content area
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 15, 20, 15)
        content_layout.setSpacing(15)

        # Back to Dashboard button


        # Title label
        title_label = QLabel("Help ")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(title_label)
        content_layout.addSpacing(10)

        # Main content grid - 2x2 layout
        grid_layout = QHBoxLayout()
        grid_layout.setSpacing(15)

        # Left column
        left_column = QVBoxLayout()
        left_column.setSpacing(15)

        # Students section
        students_layout = QVBoxLayout()
        students_label = QLabel("Students")
        students_label.setObjectName("categoryLabel")
        students_layout.addWidget(students_label)

        students_group = QGroupBox()
        students_group.setStyleSheet("QGroupBox { padding-top: 5px; }")
        students_inner_layout = QVBoxLayout(students_group)
        students_inner_layout.setSpacing(10)

        student_names = [
            "Ryan alroumi",
            "Azzam Alfahad",
            "Mohammed Aldakheel",
            
        ]

        for name in student_names:
            student_label = QLabel(f"• {name}")
            student_label.setStyleSheet("color: #333;")
            students_inner_layout.addWidget(student_label)

        students_inner_layout.addStretch()
        students_layout.addWidget(students_group)
        left_column.addLayout(students_layout)

        # Resources section
        resources_layout = QVBoxLayout()
        resources_label = QLabel("Resources")
        resources_label.setObjectName("categoryLabel")
        resources_layout.addWidget(resources_label)

        resources_group = QGroupBox()
        resources_group.setStyleSheet("QGroupBox { padding-top: 5px; }")
        resources_inner_layout = QVBoxLayout(resources_group)
        resources_inner_layout.setSpacing(10)

        resources = [
            ("Info", " <a href='https://docs.google.com/document/d/1EoQnxMbFQGa7jwbMIuHPLNPjg_ei-nJh/edit?usp=sharing&ouid=101071236718864234870&rtpof=true&sd=true'>comprehensive documentation</a>"),
            ("FAQs", "Find answers to common questions"),

        ]

        for title, desc in resources:
            resource_layout = QHBoxLayout()

            title_label = QLabel(f"• <b>{title}</b>")
            resource_layout.addWidget(title_label)
            resource_layout.addSpacing(5)

            dash_label = QLabel("-")
            resource_layout.addWidget(dash_label)
            resource_layout.addSpacing(5)

            desc_label = QLabel(desc)
            desc_label = QLabel(f"{desc} <a href='https://drive.google.com/file/d/1wHClt9RS6EpR_8rOrcOyLrpEc5cBXhdN/view?usp=sharing'>[PDF]</a>")
            desc_label.setOpenExternalLinks(True)

            resource_layout.addWidget(desc_label)
            resource_layout.addStretch()

            resource_widget = QWidget()
            resource_widget.setLayout(resource_layout)
            resources_inner_layout.addWidget(resource_widget)

        resources_inner_layout.addStretch()
        resources_layout.addWidget(resources_group)
        left_column.addLayout(resources_layout)

        # Right column
        right_column = QVBoxLayout()
        right_column.setSpacing(15)

        # Supervisors section
        supervisors_layout = QVBoxLayout()
        supervisors_label = QLabel("Supervisors")
        supervisors_label.setObjectName("categoryLabel")
        supervisors_layout.addWidget(supervisors_label)

        supervisors_group = QGroupBox()
        supervisors_group.setStyleSheet("QGroupBox { padding-top: 5px; }")
        supervisors_inner_layout = QVBoxLayout(supervisors_group)
        supervisors_inner_layout.setSpacing(10)

        supervisors = [
            ("Dr. Wael Khedr", "w.slem@mu.edu.sa"),
            ("Dr. Adel Thaljaoui", "adel.t@mu.edu.sa"),

        ]

        for name, email in supervisors:
            supervisor_label = QLabel(f"• {name} <a href='mailto:{email}'>[Contact]</a>")

            supervisor_label.setTextInteractionFlags(Qt.TextBrowserInteraction)
            supervisor_label.setOpenExternalLinks(True)

            supervisors_inner_layout.addWidget(supervisor_label)

        supervisors_inner_layout.addStretch()
        supervisors_layout.addWidget(supervisors_group)
        right_column.addLayout(supervisors_layout)




        # Add columns to grid
        grid_layout.addLayout(left_column)
        grid_layout.addLayout(right_column)

        content_layout.addLayout(grid_layout)
        main_layout.addWidget(content_widget)



        self.setLayout(main_layout)


    def back_to_dashboard(self):
        from dashboard import Dashboard  # Import here to avoid circular imports
        self.dashboard = Dashboard(self.username, self.user_id)
        self.dashboard.show()
        self.close()




    def center_window(self):
        """Centers the window on the screen"""
        screen = QGuiApplication.primaryScreen()  # Get primary screen
        screen_geometry = screen.geometry()  # Get screen dimensions
        window_geometry = self.frameGeometry()  # Get window dimensions
        window_geometry.moveCenter(screen_geometry.center())  # Move window to center
        self.move(window_geometry.topLeft())  # Set new position

