from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox, QGroupBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

class LoginWindow(QDialog):
    login_success = pyqtSignal(object)  # Emit KISClient on success
    
    def __init__(self, kis_client):
        super().__init__()
        self.kis_client = kis_client
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("한국투자증권 API 로그인")
        self.setGeometry(200, 200, 500, 400)
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: white;
            }
            QPushButton {
                padding: 10px;
                background-color: #0066cc;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0052a3;
            }
            QPushButton:pressed {
                background-color: #003d7a;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Title
        title = QLabel("한국투자증권 Open API")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # API Credentials Group
        cred_group = QGroupBox("API 인증 정보")
        cred_layout = QVBoxLayout()
        
        # App Key
        self.app_key_label = QLabel("App Key:")
        self.app_key_input = QLineEdit()
        self.app_key_input.setPlaceholderText("App Key를 입력하세요")
        cred_layout.addWidget(self.app_key_label)
        cred_layout.addWidget(self.app_key_input)
        
        # App Secret
        self.app_secret_label = QLabel("App Secret:")
        self.app_secret_input = QLineEdit()
        self.app_secret_input.setPlaceholderText("App Secret을 입력하세요")
        self.app_secret_input.setEchoMode(QLineEdit.Password)
        cred_layout.addWidget(self.app_secret_label)
        cred_layout.addWidget(self.app_secret_input)
        
        # Account Number
        self.account_label = QLabel("계좌번호:")
        self.account_input = QLineEdit()
        self.account_input.setPlaceholderText("계좌번호 (예: 12345678-01)")
        cred_layout.addWidget(self.account_label)
        cred_layout.addWidget(self.account_input)
        
        cred_group.setLayout(cred_layout)
        layout.addWidget(cred_group)
        
        # Status Label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #666666; font-style: italic;")
        layout.addWidget(self.status_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.login_button = QPushButton("로그인")
        self.login_button.clicked.connect(self.handle_login)
        
        self.demo_button = QPushButton("데모 모드 (체험)")
        self.demo_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.demo_button.clicked.connect(self.handle_demo_login)

        self.cancel_button = QPushButton("취소")
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #999999;
            }
            QPushButton:hover {
                background-color: #777777;
            }
        """)
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.demo_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        self.setLayout(layout)
        
        # Load saved credentials if available
        self.load_credentials()
        
    def load_credentials(self):
        """Load credentials from secrets.py if available"""
        try:
            from secrets import APP_KEY, APP_SECRET, ACCOUNT_NO
            if APP_KEY and APP_KEY != "YOUR_APP_KEY_HERE":
                self.app_key_input.setText(APP_KEY)
            if APP_SECRET and APP_SECRET != "YOUR_APP_SECRET_HERE":
                self.app_secret_input.setText(APP_SECRET)
            if ACCOUNT_NO and ACCOUNT_NO != "YOUR_ACCOUNT_NO_HERE":
                self.account_input.setText(ACCOUNT_NO)
            self.status_label.setText("secrets.py에서 정보를 불러왔습니다.")
        except ImportError:
            self.status_label.setText("secrets.py 파일이 없습니다. 직접 입력해주세요.")
        except Exception as e:
            self.status_label.setText(f"정보 로드 실패: {str(e)}")
            
    def handle_demo_login(self):
        """Handle demo login button click"""
        self.kis_client.is_demo = True
        self.kis_client.get_access_token() # Set dummy token
        QMessageBox.information(self, "데모 모드", "데모 모드로 로그인합니다.\n실제 거래는 불가능하며 가상의 데이터가 표시됩니다.")
        self.login_success.emit(self.kis_client)
        self.accept()
    
    def handle_login(self):
        """Handle login button click"""
        app_key = self.app_key_input.text().strip()
        app_secret = self.app_secret_input.text().strip()
        account_no = self.account_input.text().strip()
        
        # Validation
        if not app_key or not app_secret or not account_no:
            QMessageBox.warning(self, "입력 오류", "모든 필드를 입력해주세요.")
            return
        
        # Update KIS client credentials
        self.kis_client.app_key = app_key
        self.kis_client.app_secret = app_secret
        self.kis_client.account_no = account_no
        
        # Attempt to get access token
        self.status_label.setText("로그인 중...")
        self.login_button.setEnabled(False)
        
        try:
            success = self.kis_client.get_access_token()
            if success:
                QMessageBox.information(self, "로그인 성공", "한국투자증권 API에 성공적으로 연결되었습니다.")
                self.login_success.emit(self.kis_client)
                self.accept()
            else:
                QMessageBox.critical(self, "로그인 실패", "API 인증에 실패했습니다.\n입력 정보를 확인해주세요.")
                self.status_label.setText("로그인 실패")
        except Exception as e:
            QMessageBox.critical(self, "오류", f"로그인 중 오류 발생:\n{str(e)}")
            self.status_label.setText("오류 발생")
        finally:
            self.login_button.setEnabled(True)
