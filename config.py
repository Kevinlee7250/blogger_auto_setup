"""
config.py - 환경 변수 로더
.env 파일에서 설정값을 불러옵니다.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── Blogger 설정 ────────────────────────────
BLOG_ID           = os.getenv("BLOG_ID", "")
BLOG_NAME         = os.getenv("BLOG_NAME", "AI 도구 활용 가이드")
BLOG_DESCRIPTION  = os.getenv("BLOG_DESCRIPTION", "AI 도구와 IT 기술을 쉽게 활용하는 방법을 소개합니다.")
BLOG_NICHE        = os.getenv("BLOG_NICHE", "AI/IT 정보")
BLOG_AUTHOR_NAME  = os.getenv("BLOG_AUTHOR_NAME", "블로그 관리자")
BLOG_EMAIL        = os.getenv("BLOG_EMAIL", "")
BLOG_URL          = os.getenv("BLOG_URL", "")

# ── Anthropic API 설정 ──────────────────────
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# ── Google OAuth 스코프 ──────────────────────
BLOGGER_SCOPES = ["https://www.googleapis.com/auth/blogger"]

# ── 필수 페이지 정의 ──────────────────────────
REQUIRED_PAGES = ["privacy_policy", "about", "contact", "disclaimer"]

def validate():
    """필수 환경 변수 확인"""
    errors = []
    if not BLOG_ID:
        errors.append("BLOG_ID 가 설정되지 않았습니다.")
    if not ANTHROPIC_API_KEY:
        errors.append("ANTHROPIC_API_KEY 가 설정되지 않았습니다.")
    if errors:
        raise EnvironmentError("\n".join(["[설정 오류]"] + errors +
            ["\n.env 파일을 확인하세요. (.env.example 참고)"]))
