import sys
from PyQt5.QtWidgets import (QMainWindow, QLabel, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QTextEdit, QTabWidget,
                             QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class MainWindow(QMainWindow):
    def __init__(self, kis_client=None):
        super().__init__()
        self.kis_client = kis_client
        self.setWindowTitle("StockAutoTrader - 한국투자증권")
        self.setGeometry(100, 100, 1200, 800)
        self.init_ui()
        
    def init_ui(self):
        """Initialize the main UI"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QLabel {
                font-size: 12px;
            }
            QPushButton {
                padding: 8px 16px;
                background-color: #0066cc;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0052a3;
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Stock Auto Trader")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Connection status
        self.status_label = QLabel("연결 상태: 로그인 필요")
        self.status_label.setStyleSheet("color: #cc0000; font-weight: bold;")
        header_layout.addWidget(self.status_label)
        
        main_layout.addLayout(header_layout)
        
        # Tab Widget
        self.tabs = QTabWidget()
        
        # Dashboard Tab
        dashboard_tab = QWidget()
        dashboard_layout = QVBoxLayout()
        
        # Balance Info Section
        balance_group = QGroupBox("계좌 현황")
        balance_layout = QHBoxLayout()
        
        self.total_asset_label = QLabel("총 평가금액: - 원")
        self.total_asset_label.setFont(QFont("Arial", 12, QFont.Bold))
        balance_layout.addWidget(self.total_asset_label)
        
        self.deposit_label = QLabel("예수금: - 원")
        balance_layout.addWidget(self.deposit_label)
        
        self.profit_label = QLabel("손익: - 원 (-%)")
        balance_layout.addWidget(self.profit_label)
        
        refresh_btn = QPushButton("새로고침")
        refresh_btn.setFixedWidth(80)
        refresh_btn.clicked.connect(self.refresh_balance)
        balance_layout.addWidget(refresh_btn)
        
        balance_group.setLayout(balance_layout)
        dashboard_layout.addWidget(balance_group)
        
        # Holdings Table
        holdings_group = QGroupBox("보유 종목")
        holdings_layout = QVBoxLayout()
        
        self.holdings_table = QTableWidget()
        self.holdings_table.setColumnCount(5)
        self.holdings_table.setHorizontalHeaderLabels(["종목명", "보유수량", "매입가", "현재가", "수익률"])
        self.holdings_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        holdings_layout.addWidget(self.holdings_table)
        
        holdings_group.setLayout(holdings_layout)
        dashboard_layout.addWidget(holdings_group)

        # Log Section
        log_group = QGroupBox("시스템 로그")
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        dashboard_layout.addWidget(log_group)
        
        dashboard_tab.setLayout(dashboard_layout)
        self.tabs.addTab(dashboard_tab, "대시보드")
        
        # Trading Tab (placeholder)
        trading_tab = QWidget()
        trading_layout = QVBoxLayout()
        trading_label = QLabel("매매 기능 (개발 예정)")
        trading_label.setAlignment(Qt.AlignCenter)
        trading_layout.addWidget(trading_label)
        trading_tab.setLayout(trading_layout)
        self.tabs.addTab(trading_tab, "매매")
        
        main_layout.addWidget(self.tabs)
        
        # Update status if logged in
        if self.kis_client and self.kis_client.access_token:
            self.update_login_status(True)
            self.add_log("한국투자증권 API에 연결되었습니다.")
            self.refresh_balance() # Auto refresh on login
        else:
            self.add_log("로그인이 필요합니다.")
            
    def refresh_balance(self):
        """Refresh account balance and holdings"""
        if not self.kis_client or not self.kis_client.access_token:
            return

        self.add_log("계좌 잔고 조회 중...")
        data = self.kis_client.get_balance()
        
        if data and data['rt_cd'] == '0':
            output1 = data['output1'] # 보유 종목 리스트
            output2 = data['output2'][0] # 계좌 잔고 상세
            
            # Update Balance Labels
            total_amt = int(output2['tot_evlu_amt'])
            deposit = int(output2['dnca_tot_amt'])
            profit = int(output2['evlu_pfls_smtl_amt'])
            
            self.total_asset_label.setText(f"총 평가금액: {total_amt:,} 원")
            self.deposit_label.setText(f"예수금: {deposit:,} 원")
            
            profit_color = "red" if profit > 0 else "blue" if profit < 0 else "black"
            self.profit_label.setText(f"손익: {profit:,} 원")
            self.profit_label.setStyleSheet(f"color: {profit_color}")
            
            # Update Holdings Table
            self.holdings_table.setRowCount(0)
            for item in output1:
                row = self.holdings_table.rowCount()
                self.holdings_table.insertRow(row)
                
                name = item['prdt_name']
                qty = int(item['hldg_qty'])
                buy_price = float(item['pchs_avg_pric'])
                curr_price = int(item['prpr'])
                rate = float(item['evlu_pfls_rt'])
                
                self.holdings_table.setItem(row, 0, QTableWidgetItem(name))
                self.holdings_table.setItem(row, 1, QTableWidgetItem(f"{qty:,}"))
                self.holdings_table.setItem(row, 2, QTableWidgetItem(f"{buy_price:,.0f}"))
                self.holdings_table.setItem(row, 3, QTableWidgetItem(f"{curr_price:,}"))
                
                rate_item = QTableWidgetItem(f"{rate:.2f}%")
                if rate > 0:
                    rate_item.setForeground(Qt.red)
                elif rate < 0:
                    rate_item.setForeground(Qt.blue)
                self.holdings_table.setItem(row, 4, rate_item)
                
            self.add_log("계좌 잔고 갱신 완료")
        else:
            self.add_log("계좌 잔고 조회 실패")
    
    def update_login_status(self, is_logged_in):
        """Update the login status display"""
        if is_logged_in:
            self.status_label.setText("연결 상태: 연결됨")
            self.status_label.setStyleSheet("color: #00cc00; font-weight: bold;")
        else:
            self.status_label.setText("연결 상태: 로그인 필요")
            self.status_label.setStyleSheet("color: #cc0000; font-weight: bold;")
    
    def add_log(self, message):
        """Add a log message to the log text area"""
        self.log_text.append(f"[LOG] {message}")
