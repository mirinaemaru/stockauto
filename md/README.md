# StockAutoTrader

한국투자증권(KIS) Open API를 활용한 주식 자동매매 프로그램입니다.
기존 키움증권(Windows 전용)에서 한국투자증권(REST API)으로 변경하여 **Mac, Windows, Linux 등 모든 운영체제에서 실행 가능**합니다.

## 시스템 요구사항

- **운영체제**: Windows, macOS, Linux (Python 3.x 지원 환경)
- **필수 계정**: 한국투자증권 계좌 및 Open API 신청 (App Key 발급)

## 설치 및 설정

1. 의존성 설치
   ```bash
   pip install -r requirements.txt
   ```

2. API 키 설정
   `secrets.py` 파일을 생성하고 본인의 API 정보를 입력하세요.
   ```python
   # secrets.py
   APP_KEY = "your_app_key"
   APP_SECRET = "your_app_secret"
   ACCOUNT_NO = "12345678-01"
   ```

3. 프로그램 실행
   ```bash
   python main.py
   ```
