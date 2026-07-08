"""
auth.py - Google OAuth 2.0 인증 & Blogger API 클라이언트 생성

사전 준비:
  1. Google Cloud Console (console.cloud.google.com) 접속
  2. 새 프로젝트 생성 → "Blogger API v3" 활성화
  3. 사용자 인증 정보 → OAuth 2.0 클라이언트 ID 생성 (데스크톱 앱)
  4. credentials.json 다운로드 → 이 파일과 같은 폴더에 저장
"""

import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from config import BLOGGER_SCOPES

TOKEN_FILE       = "token.pickle"
CREDENTIALS_FILE = "credentials.json"


def get_blogger_service():
    """
    Google OAuth 인증 후 Blogger API 서비스 객체를 반환합니다.
    최초 실행 시 브라우저 인증 창이 열립니다.
    이후 실행에서는 저장된 토큰을 재사용합니다.
    """
    creds = None

    # ── 저장된 토큰 불러오기 ──
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as f:
            creds = pickle.load(f)

    # ── 토큰 만료 시 갱신 ──
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except Exception:
            creds = None  # 갱신 실패 시 재인증

    # ── 신규 인증 ──
    if not creds or not creds.valid:
        if not os.path.exists(CREDENTIALS_FILE):
            raise FileNotFoundError(
                f"[오류] {CREDENTIALS_FILE} 파일이 없습니다.\n"
                "Google Cloud Console에서 OAuth 2.0 클라이언트 ID를 생성 후\n"
                "credentials.json 을 이 폴더에 저장하세요."
            )
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, BLOGGER_SCOPES)
        creds = flow.run_local_server(port=0)

        # 토큰 저장 (다음 실행에서 재사용)
        with open(TOKEN_FILE, "wb") as f:
            pickle.dump(creds, f)

    service = build("blogger", "v3", credentials=creds)
    return service
