"""
main.py - 블로그 초기 세팅 자동화 파이프라인 (STEP 1~3)

실행 순서:
  STEP 1: 블로그 연결 확인 & 기본 정보 리포트
  STEP 2: 커스텀 CSS 생성 & 테마 적용
  STEP 3: 필수 페이지 4개 자동 생성 & 발행

사전 준비:
  1. pip install -r requirements.txt
  2. .env.example → .env 복사 후 값 설정
  3. Google Cloud Console에서 credentials.json 다운로드
"""

import sys
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
import config

console = Console()


def print_banner():
    console.print()
    console.print(Panel(
        "[bold blue]구글 블로그 초기 세팅 자동화 파이프라인[/bold blue]\n"
        "[dim]STEP 1: 연결 확인  →  STEP 2: 테마 CSS  →  STEP 3: 필수 페이지 생성[/dim]\n\n"
        f"[cyan]블로그명:[/cyan] {config.BLOG_NAME}\n"
        f"[cyan]블로그 ID:[/cyan] {config.BLOG_ID}\n"
        f"[cyan]니치:[/cyan] {config.BLOG_NICHE}",
        title="🚀 Blogger Auto Setup v1.0",
        border_style="blue"
    ))
    console.print()


def main():
    print_banner()

    # ── 환경 변수 검증 ──
    try:
        config.validate()
    except EnvironmentError as e:
        console.print(f"[red]{e}[/red]")
        sys.exit(1)

    # ── STEP 1: 블로그 연결 확인 ──
    from step1_verify import run as step1
    service = step1()
    if service is None:
        console.print("[red]❌ STEP 1 실패. 설정을 확인 후 재실행하세요.[/red]")
        sys.exit(1)

    console.print()

    # ── STEP 2: 테마 CSS 적용 ──
    from step2_theme import run as step2
    step2(service)

    console.print()

    # ── STEP 3: 필수 페이지 생성 ──
    from step3_pages import run as step3
    results = step3(service)

    # ── 최종 완료 메시지 ──
    console.print()
    console.print(Rule("[bold green]🎉 전체 파이프라인 완료[/bold green]"))
    console.print()
    console.print(Panel(
        "[bold]다음 단계 (수동 작업):[/bold]\n\n"
        "□ Blogger 대시보드에서 커스텀 도메인 연결 확인\n"
        "□ HTTPS 강제 리디렉션 ON 확인\n"
        "□ 헤더 메뉴에 생성된 4개 페이지 링크 추가\n"
        "□ Google Search Console 블로그 등록\n"
        "□ Sitemap 제출: [cyan]your-blog.com/sitemap.xml[/cyan]\n"
        "□ Google Analytics 4 연동 코드 삽입\n\n"
        "[bold]이후 개발 예정 파이프라인:[/bold]\n"
        "• STEP 4: 키워드 수집 자동화 (네이버 DataLab API)\n"
        "• STEP 5: AI 콘텐츠 생성 & 자동 발행 (Claude API + Blogger Posts API)\n"
        "• STEP 6: 트래픽 모니터링 & AdSense 신청 알림",
        title="📋 완료 후 체크리스트",
        border_style="green"
    ))


if __name__ == "__main__":
    main()
