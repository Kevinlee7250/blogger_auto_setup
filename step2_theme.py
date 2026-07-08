"""
step2_theme.py - STEP 2: 커스텀 CSS 생성 & 블로그 테마에 적용

Blogger API v3는 테마 XML 직접 교체를 공식 지원하지 않습니다.
이 스크립트는 두 가지 방법으로 CSS를 적용합니다.

방법 A (자동): Blogger API → 테마 XML 다운로드 → CSS 주입 → 재업로드
방법 B (수동 가이드): CSS 파일 생성 후 적용 방법 안내
"""

import json
import re
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from auth import get_blogger_service
import config

console = Console()

# ── AdSense 승인 최적화 CSS ──────────────────────────────────
CUSTOM_CSS = """
/* ════════════════════════════════════════
   AdSense 승인 최적화 커스텀 CSS
   블로그: {blog_name}
   생성: {date}
════════════════════════════════════════ */

/* ── 기본 폰트 & 색상 ── */
body {{
  font-family: 'Noto Sans KR', 'Apple SD Gothic Neo', sans-serif;
  font-size: 17px;
  line-height: 1.85;
  color: #1e293b;
  background: #ffffff;
}}

/* ── 최대 너비 중앙 정렬 ── */
.main-wrapper, .content-wrapper {{
  max-width: 820px;
  margin: 0 auto;
  padding: 0 16px;
}}

/* ── 헤더 ── */
header, #header {{
  border-bottom: 3px solid #2563eb;
  padding: 20px 0;
  margin-bottom: 32px;
}}
header h1, #header h1 {{
  font-size: 24px;
  font-weight: 700;
  color: #1e3a5f;
}}
header p.description, .header-desc {{
  font-size: 14px;
  color: #64748b;
  margin-top: 4px;
}}

/* ── 네비게이션 ── */
nav, .tabs {{
  background: #1e3a5f;
  padding: 0 12px;
  border-radius: 4px;
  margin-bottom: 24px;
}}
nav a, .tabs a {{
  display: inline-block;
  color: #ffffff !important;
  padding: 10px 16px;
  font-size: 14px;
  font-weight: 600;
  text-decoration: none !important;
  transition: background 0.2s;
}}
nav a:hover, .tabs a:hover {{
  background: rgba(255,255,255,0.15);
  border-radius: 4px;
}}

/* ── 게시물 카드 ── */
.post-outer {{
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 28px 32px;
  margin-bottom: 28px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
  transition: box-shadow 0.2s;
}}
.post-outer:hover {{
  box-shadow: 0 4px 16px rgba(0,0,0,0.10);
}}

/* ── 게시물 제목 ── */
.post-title a {{
  font-size: 22px;
  font-weight: 700;
  color: #1e3a5f !important;
  text-decoration: none !important;
  line-height: 1.4;
}}
.post-title a:hover {{
  color: #2563eb !important;
}}

/* ── 메타 정보 (날짜, 작성자) ── */
.post-header .date-header, .post-header-line-1 {{
  font-size: 13px;
  color: #94a3b8;
  margin-bottom: 8px;
}}

/* ── 본문 ── */
.post-body {{
  font-size: 17px;
  line-height: 1.9;
  color: #334155;
}}
.post-body h2 {{
  font-size: 20px;
  font-weight: 700;
  color: #1e3a5f;
  border-left: 4px solid #2563eb;
  padding-left: 12px;
  margin: 32px 0 16px;
}}
.post-body h3 {{
  font-size: 17px;
  font-weight: 700;
  color: #334155;
  margin: 24px 0 12px;
}}
.post-body a {{
  color: #2563eb;
  text-decoration: underline;
}}
.post-body img {{
  max-width: 100%;
  height: auto;
  border-radius: 6px;
  margin: 16px auto;
  display: block;
}}

/* ── 코드 블록 ── */
.post-body pre, .post-body code {{
  background: #f1f5f9;
  border-radius: 6px;
  padding: 2px 6px;
  font-size: 15px;
  font-family: 'Courier New', monospace;
}}
.post-body pre {{
  padding: 16px 20px;
  overflow-x: auto;
  border-left: 3px solid #2563eb;
}}

/* ── 태그 ── */
.post-labels a {{
  display: inline-block;
  background: #dbeafe;
  color: #1d4ed8;
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 13px;
  text-decoration: none !important;
  margin: 2px;
}}

/* ── 페이지네이션 ── */
.blog-pager {{
  text-align: center;
  margin: 32px 0;
}}
.blog-pager a {{
  display: inline-block;
  background: #2563eb;
  color: #fff !important;
  padding: 10px 24px;
  border-radius: 6px;
  text-decoration: none !important;
  font-weight: 600;
  margin: 0 6px;
}}

/* ── 사이드바 ── */
.sidebar-container {{
  font-size: 15px;
}}
.widget-content, .sidebar .widget {{
  margin-bottom: 24px;
}}
.widget h2 {{
  font-size: 16px;
  font-weight: 700;
  color: #1e3a5f;
  border-bottom: 2px solid #2563eb;
  padding-bottom: 8px;
  margin-bottom: 14px;
}}

/* ── 푸터 ── */
footer, #footer {{
  background: #1e3a5f;
  color: #cbd5e1;
  text-align: center;
  padding: 24px 16px;
  font-size: 13px;
  margin-top: 48px;
}}
footer a {{
  color: #93c5fd !important;
  text-decoration: none;
  margin: 0 8px;
}}

/* ── 모바일 반응형 ── */
@media (max-width: 768px) {{
  body {{ font-size: 15px; }}
  .post-outer {{ padding: 20px 16px; }}
  .post-title a {{ font-size: 18px; }}
  .main-wrapper {{ padding: 0 12px; }}
}}

/* ── AdSense 광고 영역 최적화 ── */
.ad-wrapper {{
  text-align: center;
  margin: 24px 0;
  overflow: hidden;
}}
"""


def generate_css_file():
    """커스텀 CSS 파일 생성"""
    css_content = CUSTOM_CSS.format(
        blog_name=config.BLOG_NAME,
        date=datetime.now().strftime("%Y-%m-%d")
    )
    with open("custom_theme.css", "w", encoding="utf-8") as f:
        f.write(css_content)
    return css_content


def inject_css_to_template(service, css_content):
    """
    Blogger API를 통해 현재 테마 XML에 CSS 주입 시도.
    API 지원 여부에 따라 자동/수동 처리로 분기.
    """
    blog_id = config.BLOG_ID

    # ── 현재 테마 XML 조회 시도 ──
    try:
        template = service.blogs().get(
            blogId=blog_id,
            fields="id,name"  # 테마 엔드포인트 테스트
        ).execute()

        # blogger v3 비공개 template 엔드포인트 시도
        import googleapiclient.discovery as gd
        raw = service._http.request(
            f"https://www.googleapis.com/blogger/v3/blogs/{blog_id}/template",
            method="GET"
        )
        import json as _json
        status, body = raw
        if hasattr(status, 'status') and str(status.status) == "200":
            theme_data = _json.loads(body)
            theme_xml  = theme_data.get("template", "")

            # ── CSS 주입: <b:skin> 태그 안에 삽입 ──
            css_tag = f"\n/* === Custom CSS === */\n{css_content}\n"
            if "<b:skin>" in theme_xml:
                theme_xml = theme_xml.replace(
                    "</b:skin>",
                    css_tag + "</b:skin>"
                )
            elif "]]></b:skin>" in theme_xml:
                theme_xml = theme_xml.replace(
                    "]]></b:skin>",
                    css_tag + "]]></b:skin>"
                )

            # ── 업데이트 PUT 요청 ──
            service._http.request(
                f"https://www.googleapis.com/blogger/v3/blogs/{blog_id}/template",
                method="PUT",
                body=_json.dumps({"template": theme_xml}),
                headers={"Content-Type": "application/json"}
            )
            return True

    except Exception:
        pass

    return False  # 자동 주입 실패 → 수동 가이드로 폴백


def run(service=None):
    console.rule("[bold blue]STEP 2 — 커스텀 CSS 테마 적용")

    if service is None:
        service = get_blogger_service()

    # ── CSS 파일 생성 ──
    console.print("\n[yellow]▶ AdSense 최적화 CSS 생성 중...[/yellow]")
    css_content = generate_css_file()
    console.print("[green]✅ custom_theme.css 생성 완료[/green]")

    # ── 자동 주입 시도 ──
    console.print("[yellow]▶ 블로그 테마에 CSS 자동 주입 시도 중...[/yellow]")
    success = inject_css_to_template(service, css_content)

    if success:
        console.print("[green]✅ CSS 자동 주입 성공![/green]")
    else:
        # ── 수동 적용 가이드 ──
        console.print("[yellow]ℹ️  자동 주입 미지원 → 아래 수동 적용 가이드를 따라주세요.[/yellow]")
        console.print()
        console.print(Panel(
            "[bold]📋 수동 CSS 적용 방법 (1분 소요)[/bold]\n\n"
            "1. [cyan]https://www.blogger.com[/cyan] 접속 → 해당 블로그 선택\n"
            "2. 왼쪽 메뉴 → [bold]테마[/bold] 클릭\n"
            "3. 오른쪽 상단 [bold]맞춤설정[/bold] 클릭\n"
            "4. 하단 [bold]고급[/bold] → [bold]CSS 추가[/bold] 선택\n"
            "5. 생성된 [cyan]custom_theme.css[/cyan] 파일의 내용을 전체 붙여넣기\n"
            "6. [bold]블로그에 적용[/bold] 클릭\n\n"
            "[dim]또는: 테마 → 수정(연필 아이콘) → HTML 편집 → </b:skin> 바로 앞에 CSS 붙여넣기[/dim]",
            title="수동 테마 적용 가이드",
            border_style="yellow"
        ))

    # ── 반응형 확인 체크리스트 ──
    console.print()
    console.print(Panel(
        "CSS 적용 후 아래 항목을 확인하세요:\n\n"
        "□ Chrome DevTools (F12) → 모바일 뷰(320px) 정상 표시\n"
        "□ 폰트가 한국어로 잘 표시되는지 확인\n"
        "□ 네비게이션 메뉴 링크 동작 확인\n"
        "□ PageSpeed Insights → 모바일 점수 60점 이상 확인\n"
        "   [dim]https://pagespeed.web.dev[/dim]",
        title="✅ 적용 후 확인사항",
        border_style="green"
    ))

    console.print(Panel("[bold green]✅ STEP 2 완료 — CSS 준비됨[/bold green]", expand=False))
    return service


if __name__ == "__main__":
    config.validate()
    run()
