from kis_api import KisApi
import pprint

def check_balance():
    kis = KisApi()
    print("Fetching account balance...")
    
    # get_balance returns output2 which is a list containing valid info
    balance_info = kis.get_balance()
    
    if balance_info:
        # Usually it returns a list with one item
        if isinstance(balance_info, list) and len(balance_info) > 0:
            info = balance_info[0]
            print("\n" + "="*40)
            print(" [계좌 잔고 조회 결과]")
            print("="*40)
            print(f" 예수금총액 (dnca_tot_amt): {info.get('dnca_tot_amt', '0')} 원")
            print(f" 익일정산금 (nxdy_excc_amt): {info.get('nxdy_excc_amt', '0')} 원")
            print(f" 가수도정산금 (prvs_rcdl_excc_amt): {info.get('prvs_rcdl_excc_amt', '0')} 원")
            print(f" 자산평가총액 (tot_evlu_mamt): {info.get('tot_evlu_mamt', '0')} 원")
            print(f" 유가평가총액 (nass_amt): {info.get('nass_amt', '0')} 원")
            print("="*40)
        else:
             print("잔고 정보가 비어있습니다.")
             pprint.pprint(balance_info)
    else:
        print("잔고 조회 실패")

if __name__ == "__main__":
    check_balance()
