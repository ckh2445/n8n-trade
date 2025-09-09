import requests
import json
import os
from dotenv import load_dotenv
from typing import Dict


class KiwoomAPI:
    def __init__(self, appkey: str, secretkey: str, host: str = 'https://api.kiwoom.com') -> None:
        """
        KiwoomAPI 초기화
        :param appkey: 키움 앱키
        :param secretkey: 키움 시크릿키
        :param host: API 기본 호스트 URL
        """
        self.appkey = appkey
        self.secretkey = secretkey
        self.host = host

    def _build_headers(self) -> Dict[str, str]:
        """API 요청에 필요한 헤더 생성"""
        return {
            'Content-Type': 'application/json;charset=UTF-8',
        }

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

        response = requests.post(url, headers=headers, json=params)

        # 응답 JSON에서 access_token 추출
        token = response.json().get('token')
        if not token:
            raise ValueError("access_token이 응답에 포함되지 않았습니다.")
        return token

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
    access_token = kiwoom_api.request_access_token()
    print("Access Token:", access_token)

