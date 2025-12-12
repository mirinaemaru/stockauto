# 프로젝트 디렉토리 구조 정의

이 문서는 `StockAutoTrader` 프로젝트의 폴더 및 파일 구조를 정의합니다.

## 디렉토리 구조 (Tree)

```
stockauto/
├── main.py                 # 프로그램 진입점 (Entry Point)
├── config.py               # 일반 설정 파일
├── secrets.py              # 중요 보안 설정 (API Key 등)
├── auth.py                 # 인증 토큰 관리
├── requirements.txt        # 의존성 패키지
├── README.md               # 프로젝트 설명
├── core/                   # 핵심 로직
│   ├── __init__.py
│   ├── kis.py              # 한국투자증권(KIS) API 연동
│   ├── strategy.py         # 매매 전략
│   ├── trader.py           # 매매 실행 및 계좌 관리
│   └── data_manager.py     # 데이터 관리
├── ui/                     # 사용자 인터페이스
│   ├── __init__.py
│   ├── main_window.py      # 메인 UI
│   └── login_window.py     # 로그인 UI
├── utils/                  # 유틸리티
│   ├── __init__.py
│   ├── logger.py           # 로깅
│   └── helper.py           # 헬퍼 함수
├── db/                     # 데이터베이스
│   ├── __init__.py
│   ├── database.py         # DB 연결 관리
│   └── schema.sql          # DB 스키마
├── md/                     # 프로젝트 문서
│   ├── structure.md        # 구조 정의 (본 파일)
│   ├── requirements.md     # 요구사항
│   ├── batch_job.md        # 배치 작업 가이드
│   └── table_description.md # DB 테이블 명세
├── logs/                   # 로그 저장소
└── [Scripts & Tools]       # 배치 및 테스트 스크립트
    ├── batch_scheduler.py      # 스케줄러
    ├── daily_trading_batch.py  # 일일 자동 매매 배치
    ├── batch_update_stocks.py  # 종목 업데이트 배치
    ├── init_db.py              # DB 초기화
    ├── kis_api.py              # KIS API 테스트
    ├── trade.py                # 매매 테스트
    ├── verify_trade.py         # 매매 검증
    ├── check_history.py        # 이력 확인
    └── ... (기타 유지보수 스크립트)
```

## 주요 파일 설명

### Root Directory
- **`main.py`**: PyQt 애플리케이션을 실행합니다.
- **`secrets.py`**: API Key, Secret, 계정정보 등 민감 정보를 담고 있습니다.
- **`auth.py`**: 한국투자증권 API 토큰 발급 및 갱신을 담당합니다.
- **`batch_scheduler.py`**: 정해진 시간에 자동 매매 작업을 수행하도록 스케줄링합니다.

### `core/`
- **`kis.py`**: 한국투자증권 REST API와 연동하여 시세 조회, 주문 전송 등을 수행합니다. (구 `kiwoom.py` 대체)
- **`strategy.py`**: 매매 전략 로직을 구현합니다.
- **`trader.py`**: 전략에 따라 매매를 실행하고 결과를 처리합니다.

### `ui/`
- **`main_window.py`**: 메인 대시보드 화면입니다.
- **`login_window.py`**: 프로그램 시작 시 계정 정보를 입력받거나 로그인을 수행합니다.

### `db/`
- **`database.py`**: DB 연결 및 쿼리 실행을 담당합니다. (MariaDB/MySQL)
- **`schema.sql`**: 테이블 생성 스키마입니다.

### `md/`
- **`structure.md`**: 프로젝트 구조 문서입니다.
- **`batch_job.md`**: 배치 작업에 대한 설명입니다.
- **`table_description.md`**: 데이터베이스 테이블 명세서입니다.
