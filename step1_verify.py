"""
step1_verify.py - STEP 1: 블로그 연결 확인 & 기본 정보 리포트

수행 작업:
  - Google OAuth 인증 테스트
  - 블로그 존재 확인 (ID 유효성)
  - 블로그 기본 정보 출력 (이름, URL, 게시물 수, 페이지 수)
  - 현재 기발행된 페이지 목록 확인
  - 설정 미비 항목 경고
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from auth import get_blogger_service
import config

console = Console()


def run():
    console.rule("[bold blue]STEP 1 — 블로그 연결 확인")

    # ── 1. OAuth 인증 ──────────────────────────────────────────
    console.print("\n[yellow]▶ Google OAuth 인증 중...[/yellow]")
    try:
        service = get_blogger_service()
        console.print("[green]✅ 인증 성공[/green]")
    except FileNotFoundError as e:
        console.print(f"[red]{e}[/red]")
        return None
    except Exception as e:
        console.print(f"[red]❌ 인증 실패: {e}[/red]")
        return None

    # ── 2. 블로그 정보 조회 ────────────────────────────────────
    console.print(f"\n[yellow]▶ 블로그 ID [{config.BLOG_ID}] 확인 중...[/yellow]")
    try:
        blog = service.blogs().get(blogId=config.BLOG_ID).execute()
    except Exception as e:
        console.print(f"[red]❌ 블로그를 찾을 수 없습니다: {e}[/red]")
        console.print("[dim].env 파일의 BLOG_ID 를 확인하세요.[/dim]")
        return None

    # ── 3. 블로그 기본 정보 출력 ──────────────────────────────
    console.print()
    info_table = Table(title="📊 블로그 현황", box=box.ROUNDED, show_header=False)
    info_table.add_column("항목", style="cyan", width=18)
    info_table.add_column("값",   style="white")

    info_table.add_row("블로그 이름",   blog.get("name", "미설정"))
    info_table.add_row("블로그 URL",    blog.get("url", "미설정"))
    info_table.add_row("블로그 ID",     blog.get("id", ""))
    info_table.add_row("게시물 수",     str(blog.get("posts", {}).get("totalItems", 0)))
    info_table.add_row("페이지 수",     str(blog.get("pages", {}).get("totalItems", 0)))
    info_table.add_row("생성 일시",     blog.get("published", "")[:10])
    info_table.add_row("업데이트",      blog.get("updated", "")[:10])
    console.print(info_table)

    # ── 4. 기발행 페이지 목록 확인 ───────────────────────────
    console.print("\n[yellow]▶ 기발행 페이지 확인 중...[/yellow]")
    try:
        pages_resp = service.pages().list(blogId=config.BLOG_ID, status="LIVE").execute()
        existing_pages = pages_resp.get("items", [])
    except Exception:
        existing_pages = []

    if existing_pages:
        page_table = Table(title="📄 현재 페이지 목록", box=box.SIMPLE)
        page_table.add_column("제목",   style="green")
        page_table.add_column("URL",    style="dim")
        page_table.add_column("발행일", style="cyan", width=12)
        for pg in existing_pages:
            page_table.add_row(
                pg.get("title", ""),
                pg.get("url", ""),
                pg.get("published", "")[:10]
            )
        console.print(page_table)
    else:
        console.print("[dim]발행된 페이지 없음 → Step 3에서 자동 생성됩니다.[/dim]")

    # ── 5. 설정 검증 경고 ────────────────────────────────────
    warnings = []
    if not config.BLOG_EMAIL:
        warnings.append("BLOG_EMAIL 미설정 → Contact 페이지에 이메일 없이 생성됩니다.")
    if not config.BLOG_URL:
        warnings.append("BLOG_URL 미설정 → Privacy Policy URL 항목이 비어있습니다.")
    if not config.ANTHROPIC_API_KEY:
        warnings.append("ANTHROPIC_API_KEY 미설정 → Step 3 실행 불가.")

    if warnings:
        console.print()
        for w in warnings:
            console.print(f"[yellow]⚠️  {w}[/yellow]")

    console.print(Panel("[bold green]✅ STEP 1 완료 — 블로그 연결 확인됨[/bold green]", expand=False))
    return service


if __name__ == "__main__":
    config.validate()
    run()
