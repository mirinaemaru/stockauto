CREATE TABLE IF NOT EXISTS auto_stock (
    stock_no VARCHAR(20) NOT NULL PRIMARY KEY COMMENT '종목코드',
    use_yn CHAR(1) DEFAULT 'Y' COMMENT '사용여부',
    gubun VARCHAR(20) COMMENT '구분',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '생성일',
    created_by VARCHAR(50) COMMENT '생성자',
    updated_at DATETIME ON UPDATE CURRENT_TIMESTAMP COMMENT '수정일',
    updated_by VARCHAR(50) COMMENT '수정자'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='자동매매 대상 종목';

CREATE TABLE IF NOT EXISTS trading_history (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'ID',
    stock_no VARCHAR(20) NOT NULL COMMENT '종목코드',
    order_type VARCHAR(10) NOT NULL COMMENT '주문구분(BUY/SELL)',
    qty INT NOT NULL COMMENT '주문수량',
    order_price INT DEFAULT 0 COMMENT '주문가격(0:시장가)',
    order_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '주문시간',
    result_code VARCHAR(20) COMMENT '결과코드',
    result_msg VARCHAR(255) COMMENT '결과메시지',
    unit_price INT DEFAULT 0 COMMENT '매수/매도 단가',
    total_price INT DEFAULT 0 COMMENT '총 금액',
    profit_loss INT DEFAULT 0 COMMENT '손익'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='매매 이력';

CREATE TABLE IF NOT EXISTS stock (
    stock_no VARCHAR(20) PRIMARY KEY COMMENT '종목코드',
    stock_name VARCHAR(100) COMMENT '종목명',
    use_yn CHAR(1) DEFAULT 'N' COMMENT '사용여부',
    trade_amount BIGINT DEFAULT 0 COMMENT '거래금액',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '업데이트시간'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='종목 정보';

CREATE TABLE IF NOT EXISTS stock_price_info (
    basDt VARCHAR(8) NOT NULL COMMENT '기준 일자 (YYYYMMDD)',
    srtnCd VARCHAR(9) NOT NULL COMMENT '단축코드 (종목코드)',
    isinCd VARCHAR(12) DEFAULT NULL COMMENT 'ISIN코드',
    itmsNm VARCHAR(120) DEFAULT NULL COMMENT '종목명',
    mrktCtg VARCHAR(40) NOT NULL COMMENT '시장구분 (KOSPI/KOSDAQ/KONEX)',
    clpr BIGINT DEFAULT NULL COMMENT '종가',
    vs INT DEFAULT NULL COMMENT '대비 (전일 대비 등락)',
    fltRt DECIMAL(11,2) DEFAULT NULL COMMENT '등락률 (전일 대비 등락 비율)',
    mkp BIGINT DEFAULT NULL COMMENT '시가',
    hipr BIGINT DEFAULT NULL COMMENT '고가',
    lopr BIGINT DEFAULT NULL COMMENT '저가',
    trqu BIGINT DEFAULT NULL COMMENT '거래량 (체결수량의 누적 합계)',
    trPrc BIGINT DEFAULT NULL COMMENT '거래대금 (체결가격 * 체결수량의 누적 합계)',
    lstgStCnt BIGINT DEFAULT NULL COMMENT '상장주식수',
    mrktTotAmt BIGINT DEFAULT NULL COMMENT '시가총액 (종가 * 상장주식수)',
    PRIMARY KEY (basDt, srtnCd, mrktCtg)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='일별 주가 정보';
