# 테이블 정의

이 문서는 `StockAutoTrader` 프로젝트의 데이터베이스 테이블 구조를 정의합니다.

## 1. auto_stock (자동매매 대상 종목)
자동매매 대상으로 선정된 종목을 관리하는 테이블입니다.

| 컬럼명 | 타입 | Nullable | Default | 설명 |
|---|---|---|---|---|
| stock_no | VARCHAR(20) | N | - | 종목코드 (PK) |
| use_yn | CHAR(1) | Y | 'Y' | 사용여부 |
| gubun | VARCHAR(20) | Y | - | 구분 |
| created_at | DATETIME | Y | CURRENT_TIMESTAMP | 생성일 |
| created_by | VARCHAR(50) | Y | - | 생성자 |
| updated_at | DATETIME | Y | ON UPDATE | 수정일 |
| updated_by | VARCHAR(50) | Y | - | 수정자 |

## 2. trading_history (매매 이력)
자동매매 시스템의 매수/매도 실행 이력을 저장하는 테이블입니다.

| 컬럼명 | 타입 | Nullable | Default | 설명 |
|---|---|---|---|---|
| id | INT | N | AUTO_INCREMENT | ID (PK) |
| stock_no | VARCHAR(20) | N | - | 종목코드 |
| order_type | VARCHAR(10) | N | - | 주문구분(BUY/SELL) |
| qty | INT | N | - | 주문수량 |
| order_price | INT | Y | 0 | 주문가격(0:시장가) |
| order_time | DATETIME | Y | CURRENT_TIMESTAMP | 주문시간 |
| result_code | VARCHAR(20) | Y | - | 결과코드 |
| result_msg | VARCHAR(255) | Y | - | 결과메시지 |
| unit_price | INT | Y | 0 | 매수/매도 단가 |
| total_price | INT | Y | 0 | 총 금액 |
| profit_loss | INT | Y | 0 | 손익 |

## 3. stock (종목 정보)
전체 종목 정보 및 배치 작업을 통해 업데이트된 거래금액 정보를 저장하는 테이블입니다.

| 컬럼명 | 타입 | Nullable | Default | 설명 |
|---|---|---|---|---|
| code | VARCHAR(20) | N | - | 종목코드 (PK) |
| name | VARCHAR(100) | Y | - | 종목명 |
| gubun | VARCHAR(20) | Y | - | 구분 |
| use_yn | CHAR(1) | Y | 'N' | 사용여부 |
| trade_amount | BIGINT | Y | 0 | 거래금액 |
| updated_at | DATETIME | Y | ON UPDATE | 업데이트시간 |
