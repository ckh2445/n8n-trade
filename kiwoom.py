import requests
import json
import os
from dotenv import load_dotenv
from typing import Dict, List, Any

import requests
import json
import os
from dotenv import load_dotenv
from typing import Dict, Any


class HttpClient:
    """HTTP 요청을 처리하는 클라이언트 추상화"""

    @staticmethod
    def post(url: str, headers: Dict[str, str], data: Any) -> requests.Response:
        return requests.post(url, headers=headers, json=data)


class KiwoomAPI:
    def __init__(self, appkey: str, secretkey: str, host: str = 'https://api.kiwoom.com',
                 client: HttpClient = HttpClient()) -> None:
        """
        KiwoomAPI 초기화
        :param appkey: 키움 앱키
        :param secretkey: 키움 시크릿키
        :param host: API 기본 호스트 URL
        :param client: HTTP 클라이언트
        """
        self.appkey = appkey
        self.secretkey = secretkey
        self.host = host
        self.client = client

    def _build_headers(self, token: str = None, cont_yn: str = 'N', next_key: str = '', api_id: str = '') -> Dict[
        str, str]:
        """API 요청에 필요한 헤더 생성"""
        headers = {'Content-Type': 'application/json;charset=UTF-8'}
        if token:
            headers['authorization'] = f'Bearer {token}'
        if cont_yn:
            headers['cont-yn'] = cont_yn
        if next_key:
            headers['next-key'] = next_key
        if api_id:
            headers['api-id'] = api_id
        return headers

    def _build_params(self) -> Dict[str, str]:
        """API 요청에 필요한 파라미터 생성"""
        return {
            'grant_type': 'client_credentials',
            'appkey': self.appkey,
            'secretkey': self.secretkey,
        }

    def request_access_token(self) -> str:
        """
        접근 토큰 발급 요청
        :return: 발급된 접근 토큰
        """
        url = f"{self.host}/oauth2/token"
        headers = self._build_headers()
        params = self._build_params()

        response = self.client.post(url, headers, params)
        response_data = response.json()

        token = response_data.get('token')
        if not token:
            raise ValueError("응답에 token이 포함되지 않았습니다.")
        return token

    def request_market_data(self, token: str, data: Dict[str, Any], cont_yn: str = 'N', next_key: str = '') -> list[
        dict[str, Any]]:
        """
        호가잔량상위요청
        :param token: 접근 토큰
        :param data: 요청 데이터
        :param cont_yn: 연속조회 여부
        :param next_key: 연속조회 키
        :return: API 응답 데이터
        """
        url = f"{self.host}/api/dostk/rkinfo"
        headers = self._build_headers(token, cont_yn, next_key, api_id='ka10032')

        response = self.client.post(url, headers, data)
        #self._handle_response(response)

        data = response.json()
        # 보통 응답 바디 키는 문서의 리스트 항목(예: trde_prica_upper)에 담겨옴
        items = data.get("trde_prica_upper", [])  # 문서의 항목명 참고
        top10 = items[:20]
        return [
            {
                "현재순위": it.get("now_rank"),
                "종목코드": it.get("stk_cd"),
                "종목명": it.get("stk_nm"),
                "현재가격": it.get("cur_prc"),
                "전일대비": it.get("pred_pre"),
                "전일대비기호": it.get("pred_pre_sig"),
                "등락률": it.get("flu_rt"),
            }
            for it in top10
        ]

    @staticmethod
    def _handle_response(response: requests.Response) -> None:
        """
        API 응답 처리
        :param response: 요청 결과 Response 객체
        """
        print('Code:', response.status_code)
        print('Header:', json.dumps(
            {key: response.headers.get(key) for key in ['next-key', 'cont-yn', 'api-id']},
            indent=4, ensure_ascii=False
        ))
        print('Body:', json.dumps(response.json(), indent=4, ensure_ascii=False))


if __name__ == '__main__':
    load_dotenv()  # .env 파일에서 환경 변수 로드
    appkey = os.getenv('KIWOOM_APPKEY')  # .env 파일에 저장된 앱키
    secretkey = os.getenv('KIWOOM_SECRETKEY')  # .env 파일에 저장된 시크릿키

    kiwoom_api = KiwoomAPI(appkey=appkey, secretkey=secretkey)
    token = kiwoom_api.request_access_token()

    params = {
        "mrkt_tp": '000',  # 000: 전체
        "mang_stk_incls": "0",  # 1=관리종목 미포함
        "stex_tp": '3'  # 3: 통합
    }

    market_data = kiwoom_api.request_market_data(token=token, data=params)

    print(json.dumps(market_data, indent=4, ensure_ascii=False))
