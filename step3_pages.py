"""
step3_pages.py - STEP 3: 필수 페이지 4개 자동 생성 & 발행

Claude API로 페이지 HTML 콘텐츠 생성 후 Blogger Pages API로 발행합니다.
생성 페이지: Privacy Policy / About / Contact / Disclaimer

중복 방지: 이미 같은 제목의 페이지가 있으면 건너뜁니다.
"""

import sys
import io
# Windows cp949 환경에서 유니코드 출력을 위해 UTF-8 강제 설정
if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'buffer'):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import time
import anthropic
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from auth import get_blogger_service
import config

console = Console(legacy_windows=False)


# ─────────────────────────────────────────────────────────────
# Claude API 프롬프트 정의
# ─────────────────────────────────────────────────────────────

PROMPTS = {
    "privacy_policy": {
        "title": "개인정보처리방침 (Privacy Policy)",
        "prompt": """
당신은 전문 웹 콘텐츠 작가입니다.
아래 정보를 바탕으로 한국 블로그용 개인정보처리방침 페이지를 HTML로 작성해주세요.

블로그 정보:
- 블로그명: {blog_name}
- 운영자 이메일: {blog_email}
- 블로그 URL: {blog_url}
- 작성일: {date}

필수 포함 항목:
1. 수집하는 개인정보 항목 (방문 기록, 쿠키 등)
2. 개인정보 수집 목적
3. Google Analytics 사용 안내 (분석 도구)
4. Google AdSense 쿠키 및 광고 안내
5. 제3자 링크 면책 조항
6. 개인정보 보호 책임자 및 연락처
7. 정책 변경 안내

작성 조건:
- 한국어로 작성
- 한국 개인정보보호법(PIPA) 기준 준수
- 전문적이고 신뢰감 있는 톤
- 완전한 HTML 콘텐츠 (body 내용만, html/body 태그 제외)
- h2, h3, p, ul 태그 사용
- 인라인 스타일로 가독성 향상
""",
    },

    "about": {
        "title": "블로그 소개 (About)",
        "prompt": """
당신은 친근하고 전문적인 블로그 작가입니다.
아래 정보를 바탕으로 블로그 소개(About) 페이지를 HTML로 작성해주세요.

블로그 정보:
- 블로그명: {blog_name}
- 블로그 주제: {blog_niche}
- 블로그 설명: {blog_description}
- 운영자: {author_name}
- 블로그 URL: {blog_url}

필수 포함 항목:
1. 블로그 운영 목적 및 미션
2. 주요 다루는 주제 (ChatGPT, Claude, Gemini, AI 자동화, 생산성 도구 등)
3. 독자에게 전달하는 가치 (AI 도구를 쉽게 배울 수 있는 곳)
4. 운영자 간략 소개
5. 독자에게 보내는 메시지 (구독/즐겨찾기 안내)

작성 조건:
- 한국어로 작성
- 따뜻하고 전문적인 톤 (딱딱하지 않게)
- 완전한 HTML 콘텐츠 (body 내용만)
- h2, h3, p, ul 태그와 이모지 적절히 활용
- 독자 친화적으로 2인칭("여러분") 사용
""",
    },

    "contact": {
        "title": "연락처 (Contact)",
        "prompt": """
당신은 웹 콘텐츠 전문가입니다.
아래 정보를 바탕으로 블로그 연락처(Contact) 페이지를 HTML로 작성해주세요.

블로그 정보:
- 블로그명: {blog_name}
- 운영자 이메일: {blog_email}
- 운영자: {author_name}

필수 포함 항목:
1. 연락처 안내 헤딩 및 소개 문구
2. 이메일 연락 안내 ({blog_email})
3. 이메일 문의 가능한 내용 (협업 문의, 오류 제보, 피드백 등)
4. Google Forms 문의 양식 안내 섹션 (실제 embed 없이 안내 텍스트만)
5. 답변 소요 시간 안내 (영업일 기준 1~3일)
6. 광고/협찬 문의 안내

작성 조건:
- 한국어로 작성
- 친근하고 정중한 톤
- 완전한 HTML 콘텐츠 (body 내용만)
- h2, p 태그 사용
- 이메일 주소는 <a href="mailto:{blog_email}"> 태그로 처리
""",
    },

    "disclaimer": {
        "title": "면책 조항 (Disclaimer)",
        "prompt": """
당신은 법률 문서 전문 콘텐츠 작가입니다.
아래 정보를 바탕으로 블로그 면책 조항(Disclaimer) 페이지를 HTML로 작성해주세요.

블로그 정보:
- 블로그명: {blog_name}
- 블로그 주제: {blog_niche}
- 운영자 이메일: {blog_email}
- 작성일: {date}

필수 포함 항목:
1. 정보의 정확성 면책 (AI/IT 정보는 빠르게 변하므로 최신 정보 확인 권고)
2. 광고 및 제휴 마케팅 안내 (Google AdSense 광고 포함)
3. 외부 링크 면책 (제3자 사이트 내용에 대한 책임 없음)
4. 투자/금융 조언 아님 안내 (해당 시)
5. 저작권 안내 (블로그 콘텐츠 무단 복제 금지)
6. 이용자 책임 안내
7. 문의 연락처

작성 조건:
- 한국어로 작성
- 전문적이고 명확한 법적 톤
- 완전한 HTML 콘텐츠 (body 내용만)
- h2, h3, p 태그 사용
- 날짜 표기 포함
""",
    },
}


# ─────────────────────────────────────────────────────────────
# 핵심 함수들
# ─────────────────────────────────────────────────────────────

def get_existing_page_titles(service):
    """이미 발행된 페이지 제목 목록 반환 (중복 방지)"""
    try:
        resp = service.pages().list(
            blogId=config.BLOG_ID,
            status="LIVE"
        ).execute()
        return [p["title"] for p in resp.get("items", [])]
    except Exception:
        return []


def generate_page_content(client, page_key: str) -> str:
    """Claude API로 페이지 HTML 콘텐츠 생성"""
    from datetime import datetime

    page_config = PROMPTS[page_key]
    prompt = page_config["prompt"].format(
        blog_name    = config.BLOG_NAME,
        blog_niche   = config.BLOG_NICHE,
        blog_description = config.BLOG_DESCRIPTION,
        author_name  = config.BLOG_AUTHOR_NAME,
        blog_email   = config.BLOG_EMAIL or "contact@your-blog.com",
        blog_url     = config.BLOG_URL or "https://your-blog.com",
        date         = datetime.now().strftime("%Y년 %m월 %d일"),
    )

    message = client.messages.create(
        model   = "claude-haiku-4-5-20251001",
        max_tokens = 2000,
        messages = [{"role": "user", "content": prompt}]
    )
    return message.content[0].text


def publish_page(service, title: str, html_content: str) -> dict:
    """Blogger Pages API로 페이지 발행"""
    # HTML 래핑: 한국어 폰트 임포트 + 기본 스타일
    full_html = f"""
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap" rel="stylesheet">
<div style="max-width:760px; margin:0 auto; padding:24px 16px;
            font-family:'Noto Sans KR',sans-serif; line-height:1.85; color:#1e293b;">
{html_content}
</div>
"""
    body = {
        "kind":    "blogger#page",
        "title":   title,
        "content": full_html,
        "status":  "LIVE",
    }
    result = service.pages().insert(
        blogId = config.BLOG_ID,
        body   = body
    ).execute()
    return result


# ─────────────────────────────────────────────────────────────
# 메인 실행
# ─────────────────────────────────────────────────────────────

def run(service=None):
    console.rule("[bold blue]STEP 3 - 필수 페이지 자동 생성 & 발행")

    if service is None:
        service = get_blogger_service()

    # ── Anthropic 클라이언트 초기화 ──
    if not config.ANTHROPIC_API_KEY:
        console.print("[red]❌ ANTHROPIC_API_KEY 가 설정되지 않았습니다. .env 파일을 확인하세요.[/red]")
        return

    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY, timeout=60)

    # ── 기발행 페이지 확인 (중복 방지) ──
    console.print("\n[yellow]▶ 기발행 페이지 목록 조회 중...[/yellow]")
    existing_titles = get_existing_page_titles(service)
    if existing_titles:
        console.print(f"[dim]기발행 페이지: {', '.join(existing_titles)}[/dim]")

    results = {"success": [], "skipped": [], "failed": []}

    for page_key in config.REQUIRED_PAGES:
        page_title = PROMPTS[page_key]["title"]

        console.print(f"\n[bold cyan]── {page_title} ──[/bold cyan]")

        # ── 중복 체크 ──
        if page_title in existing_titles:
            console.print(f"[yellow]⏭  이미 존재 → 건너뜀[/yellow]")
            results["skipped"].append(page_title)
            continue

        # ── Claude API로 콘텐츠 생성 ──
        console.print("[yellow]  ① Claude API로 콘텐츠 생성 중...[/yellow]", end="")
        try:
            html_content = generate_page_content(client, page_key)
            console.print(" [green]완료[/green]")
        except Exception as e:
            console.print(f"\n  [red]❌ 콘텐츠 생성 실패: {e}[/red]")
            results["failed"].append(page_title)
            continue

        # ── Blogger API로 발행 ──
        console.print("[yellow]  ② Blogger에 페이지 발행 중...[/yellow]", end="")
        try:
            published = publish_page(service, page_title, html_content)
            page_url  = published.get("url", "URL 미확인")
            console.print(f" [green]완료[/green]")
            console.print(f"     🔗 {page_url}")
            results["success"].append({"title": page_title, "url": page_url})
        except Exception as e:
            console.print(f"\n  [red]❌ 발행 실패: {e}[/red]")
            results["failed"].append(page_title)
            continue

        # API 과호출 방지 (1초 대기)
        time.sleep(1)

    # ── 결과 요약 ──
    console.print()
    summary_lines = [f"[bold]📊 페이지 생성 결과[/bold]\n"]
    if results["success"]:
        summary_lines.append("[green]✅ 생성 완료:[/green]")
        for item in results["success"]:
            summary_lines.append(f"   • {item['title']}")
            summary_lines.append(f"     {item['url']}")
    if results["skipped"]:
        summary_lines.append("\n[yellow]⏭  건너뜀 (이미 존재):[/yellow]")
        for t in results["skipped"]:
            summary_lines.append(f"   • {t}")
    if results["failed"]:
        summary_lines.append("\n[red]❌ 실패:[/red]")
        for t in results["failed"]:
            summary_lines.append(f"   • {t}")

    console.print(Panel("\n".join(summary_lines), border_style="green"))

    # ── 후속 작업 안내 ──
    console.print(Panel(
        "페이지 생성 후 Blogger에서 아래를 확인하세요:\n\n"
        "□ 각 페이지가 정상 발행되었는지 확인\n"
        "□ 블로그 헤더/푸터 메뉴에 4개 페이지 링크 추가\n"
        "   (Blogger → 레이아웃 → 페이지 가젯 → 수정)\n"
        "□ 각 페이지 URL을 복사해서 메뉴에 직접 링크 추가\n"
        "□ 모바일에서 페이지 링크 동작 확인",
        title="📋 후속 작업 가이드",
        border_style="cyan"
    ))

    console.print(Panel("[bold green]✅ STEP 3 완료 — 필수 페이지 발행됨[/bold green]", expand=False))
    return results


if __name__ == "__main__":
    config.validate()
    run()
