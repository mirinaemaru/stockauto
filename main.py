import sys
import platform
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow
from ui.login_window import LoginWindow
from core.kis import KISClient

def main():
    print(f"Starting StockAutoTrader on {platform.system()}...")
    
    app = QApplication(sys.argv)
    
    # Initialize KIS Client
    kis = KISClient()
    print("Initializing KIS Client...")
    
    # Show login window
    login_window = LoginWindow(kis)
    
    if login_window.exec_() == LoginWindow.Accepted:
        # Login successful, show main window
        main_window = MainWindow(kis)
        main_window.show()
        sys.exit(app.exec_())
    else:
        # Login cancelled
        print("Login cancelled by user.")
        sys.exit(0)

if __name__ == "__main__":
    main()
