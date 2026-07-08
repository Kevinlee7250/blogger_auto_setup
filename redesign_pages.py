"""
redesign_pages.py — 4개 필수 페이지 AI/Tech 다크 테마 디자인 리뉴얼

블로그 주제(AI/IT 정보)에 맞는 다크 모드 테마로 기존 4개 페이지를 업데이트합니다.
"""

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import config
from auth import get_blogger_service
from datetime import datetime

# ── 공통 디자인 시스템 ─────────────────────────────────────────────
BASE_CSS = """
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap" rel="stylesheet">
<style>
.ai-page-wrap *{box-sizing:border-box;margin:0;padding:0}
.ai-page-wrap{font-family:'Noto Sans KR',sans-serif;background:#0d1117;color:#e6edf3;
  min-height:100vh;padding-bottom:60px;line-height:1.8}

/* ─ 히어로 ─ */
.ai-hero{padding:60px 24px 48px;text-align:center;position:relative;overflow:hidden}
.ai-hero::before{content:'';position:absolute;inset:0;
  background:linear-gradient(135deg,#0d1117 0%,#1a1f35 50%,#0d1117 100%);z-index:0}
.ai-hero::after{content:'';position:absolute;inset:0;
  background:radial-gradient(ellipse at 50% 0%,rgba(59,130,246,.18) 0%,transparent 70%);z-index:0}
.ai-hero-inner{position:relative;z-index:1;max-width:720px;margin:0 auto}
.ai-hero-icon{width:72px;height:72px;border-radius:20px;margin:0 auto 20px;
  display:flex;align-items:center;justify-content:center;font-size:34px}
.ai-hero h1{font-size:clamp(24px,4vw,36px);font-weight:700;letter-spacing:-.5px;
  background:linear-gradient(135deg,#e6edf3 30%,#3B82F6);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.ai-hero p{color:#8b949e;font-size:15px;margin-top:12px}
.ai-badge{display:inline-flex;align-items:center;gap:6px;
  background:rgba(59,130,246,.12);border:1px solid rgba(59,130,246,.3);
  color:#3B82F6;border-radius:20px;padding:4px 14px;font-size:13px;font-weight:500;
  margin-bottom:20px}

/* ─ 컨텐츠 ─ */
.ai-content{max-width:760px;margin:0 auto;padding:0 20px}
.ai-card{background:#161b22;border:1px solid #21262d;border-radius:16px;
  padding:28px 32px;margin-bottom:20px;transition:border-color .2s}
.ai-card:hover{border-color:#30363d}
.ai-card-header{display:flex;align-items:center;gap:12px;margin-bottom:16px}
.ai-card-icon{font-size:22px;width:44px;height:44px;border-radius:12px;
  display:flex;align-items:center;justify-content:center;flex-shrink:0}
.ai-card h2{font-size:17px;font-weight:600;color:#e6edf3}
.ai-card h3{font-size:15px;font-weight:600;color:#c9d1d9;margin:16px 0 8px}
.ai-card p{color:#8b949e;font-size:14px;line-height:1.85}
.ai-card ul{color:#8b949e;font-size:14px;line-height:2;padding-left:20px}
.ai-card ul li{margin-bottom:2px}
.ai-card ul li::marker{color:#3B82F6}
.ai-card a{color:#3B82F6;text-decoration:none}
.ai-card a:hover{text-decoration:underline}

/* ─ 하이라이트 박스 ─ */
.ai-highlight{background:rgba(59,130,246,.08);border:1px solid rgba(59,130,246,.2);
  border-radius:12px;padding:16px 20px;margin:14px 0}
.ai-highlight.cyan{background:rgba(6,182,212,.08);border-color:rgba(6,182,212,.2)}
.ai-highlight.green{background:rgba(16,185,129,.08);border-color:rgba(16,185,129,.2)}
.ai-highlight.yellow{background:rgba(245,158,11,.08);border-color:rgba(245,158,11,.2)}
.ai-highlight.purple{background:rgba(139,92,246,.08);border-color:rgba(139,92,246,.2)}
.ai-highlight p,.ai-highlight li{color:#c9d1d9!important}

/* ─ 태그/뱃지 ─ */
.ai-tags{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px}
.ai-tag{background:#21262d;border:1px solid #30363d;color:#8b949e;
  border-radius:8px;padding:4px 12px;font-size:13px}
.ai-tag.blue{background:rgba(59,130,246,.1);border-color:rgba(59,130,246,.25);color:#60a5fa}
.ai-tag.cyan{background:rgba(6,182,212,.1);border-color:rgba(6,182,212,.25);color:#22d3ee}
.ai-tag.purple{background:rgba(139,92,246,.1);border-color:rgba(139,92,246,.25);color:#a78bfa}
.ai-tag.green{background:rgba(16,185,129,.1);border-color:rgba(16,185,129,.25);color:#34d399}

/* ─ CTA 버튼 ─ */
.ai-cta{display:inline-flex;align-items:center;gap:8px;
  background:linear-gradient(135deg,#3B82F6,#06B6D4);
  color:#fff;border-radius:10px;padding:12px 24px;font-size:14px;font-weight:600;
  text-decoration:none!important;margin-top:8px;border:none;cursor:pointer}

/* ─ 구분선 ─ */
.ai-divider{border:none;border-top:1px solid #21262d;margin:4px 0 16px}

/* ─ 푸터 ─ */
.ai-footer{text-align:center;margin-top:40px;color:#484f58;font-size:13px}
</style>
"""


# ══════════════════════════════════════════════════════════════════
# 1. 개인정보처리방침 (Privacy Policy)
# ══════════════════════════════════════════════════════════════════
def html_privacy(blog_name, blog_email, blog_url, date):
    return BASE_CSS + f"""
<div class="ai-page-wrap">

  <!-- 히어로 -->
  <div class="ai-hero">
    <div class="ai-hero-inner">
      <div class="ai-badge">📋 법적 고지</div>
      <div class="ai-hero-icon" style="background:rgba(59,130,246,.15);border:1px solid rgba(59,130,246,.3)">🔒</div>
      <h1>개인정보처리방침</h1>
      <p>Privacy Policy · 최종 업데이트: {date}</p>
    </div>
  </div>

  <div class="ai-content">

    <!-- 개요 -->
    <div class="ai-card">
      <div class="ai-card-header">
        <div class="ai-card-icon" style="background:rgba(59,130,246,.12)">📌</div>
        <h2>개요</h2>
      </div>
      <p><strong style="color:#c9d1d9">{blog_name}</strong>은 방문자의 개인정보를 소중히 여기며, 관련 법령에 따라 개인정보를 보호합니다.<br>
      본 방침은 블로그 이용 시 수집되는 정보와 그 처리 방법을 안내합니다.</p>
    </div>

    <!-- 수집 항목 -->
    <div class="ai-card">
      <div class="ai-card-header">
        <div class="ai-card-icon" style="background:rgba(6,182,212,.12)">📊</div>
        <h2>수집하는 정보</h2>
      </div>
      <div class="ai-highlight cyan">
        <p>본 블로그는 회원가입 없이 이용 가능하며, 아래 정보만 자동으로 수집됩니다.</p>
      </div>
      <h3>자동 수집 정보</h3>
      <ul>
        <li>방문 일시 및 페이지 열람 기록</li>
        <li>브라우저 종류 및 운영체제 정보</li>
        <li>IP 주소 (익명화 처리됨)</li>
        <li>쿠키 및 유사 추적 기술</li>
        <li>유입 경로 (검색어, 참조 URL 등)</li>
      </ul>
    </div>

    <!-- Google Analytics -->
    <div class="ai-card">
      <div class="ai-card-header">
        <div class="ai-card-icon" style="background:rgba(139,92,246,.12)">📈</div>
        <h2>Google Analytics 사용</h2>
      </div>
      <p>본 블로그는 <strong style="color:#a78bfa">Google Analytics 4</strong>를 사용하여 트래픽 및 사용 패턴을 분석합니다.</p>
      <div class="ai-highlight purple" style="margin-top:14px">
        <ul>
          <li>Google Analytics는 쿠키를 통해 익명화된 데이터를 수집합니다</li>
          <li>수집된 데이터는 통계 목적으로만 활용되며 개인 식별에 사용되지 않습니다</li>
          <li>Google의 데이터 처리 방식: <a href="https://policies.google.com/privacy" style="color:#a78bfa">Google 개인정보처리방침</a></li>
        </ul>
      </div>
      <div class="ai-tags" style="margin-top:14px">
        <span class="ai-tag purple">익명 데이터</span>
        <span class="ai-tag purple">쿠키 사용</span>
        <span class="ai-tag purple">Google 처리</span>
      </div>
    </div>

    <!-- Google AdSense -->
    <div class="ai-card">
      <div class="ai-card-header">
        <div class="ai-card-icon" style="background:rgba(245,158,11,.12)">💰</div>
        <h2>Google AdSense 광고</h2>
      </div>
      <p>본 블로그는 <strong style="color:#fbbf24">Google AdSense</strong>를 통해 맞춤형 광고를 제공합니다.</p>
      <div class="ai-highlight yellow" style="margin-top:14px">
        <ul>
          <li>Google은 쿠키를 사용하여 이전 방문 기록 기반의 광고를 표시합니다</li>
          <li>광고 개인화는 Google 계정 설정에서 비활성화 가능합니다</li>
          <li>제3자 광고 쿠키 관련: <a href="https://www.google.com/settings/ads" style="color:#fbbf24">광고 설정 관리</a></li>
        </ul>
      </div>
    </div>

    <!-- 쿠키 -->
    <div class="ai-card">
      <div class="ai-card-header">
        <div class="ai-card-icon" style="background:rgba(16,185,129,.12)">🍪</div>
        <h2>쿠키 사용 안내</h2>
      </div>
      <p>본 블로그는 서비스 품질 향상을 위해 쿠키를 사용합니다. 브라우저 설정에서 쿠키를 비활성화할 수 있으나, 일부 기능이 제한될 수 있습니다.</p>
      <h3>쿠키 비활성화 방법</h3>
      <ul>
        <li>Chrome: 설정 → 개인정보 및 보안 → 쿠키</li>
        <li>Firefox: 설정 → 개인정보 및 보안 → 쿠키</li>
        <li>Safari: 환경설정 → 개인정보 보호</li>
      </ul>
    </div>

    <!-- 제3자 링크 -->
    <div class="ai-card">
      <div class="ai-card-header">
        <div class="ai-card-icon" style="background:rgba(59,130,246,.12)">🔗</div>
        <h2>외부 링크 면책</h2>
      </div>
      <p>본 블로그에는 외부 사이트로의 링크가 포함될 수 있습니다. 외부 사이트의 개인정보처리방침 및 콘텐츠에 대해 본 블로그는 책임을 지지 않습니다.</p>
    </div>

    <!-- 연락처 -->
    <div class="ai-card">
      <div class="ai-card-header">
        <div class="ai-card-icon" style="background:rgba(6,182,212,.12)">✉️</div>
        <h2>개인정보 보호 책임자</h2>
      </div>
      <div class="ai-highlight cyan">
        <p>개인정보 처리에 관한 문의사항은 아래로 연락해 주세요.</p>
        <p style="margin-top:10px"><strong style="color:#22d3ee">이메일:</strong> <a href="mailto:{blog_email}" style="color:#22d3ee">{blog_email}</a></p>
        <p><strong style="color:#22d3ee">블로그:</strong> <a href="{blog_url}" style="color:#22d3ee">{blog_url}</a></p>
      </div>
    </div>

    <!-- 변경 안내 -->
    <div class="ai-card">
      <div class="ai-card-header">
        <div class="ai-card-icon" style="background:rgba(139,92,246,.12)">📅</div>
        <h2>방침 변경 안내</h2>
      </div>
      <p>본 방침은 법령 변경 또는 서비스 개선에 따라 업데이트될 수 있습니다. 중요한 변경 사항은 블로그 게시물을 통해 사전 공지합니다.</p>
      <div class="ai-tags" style="margin-top:12px">
        <span class="ai-tag blue">시행일: {date}</span>
        <span class="ai-tag blue">개인정보보호법 준수</span>
      </div>
    </div>

    <div class="ai-footer">
      © {datetime.now().year} {blog_name} · All rights reserved · <a href="{blog_url}" style="color:#484f58">{blog_url}</a>
    </div>
  </div>
</div>
"""


# ══════════════════════════════════════════════════════════════════
# 2. 블로그 소개 (About)
# ══════════════════════════════════════════════════════════════════
def html_about(blog_name, blog_niche, blog_description, author_name, blog_url):
    return BASE_CSS + f"""
<div class="ai-page-wrap">

  <!-- 히어로 -->
  <div class="ai-hero">
    <div class="ai-hero-inner">
      <div class="ai-badge">🤖 About Us</div>
      <div class="ai-hero-icon" style="background:linear-gradient(135deg,rgba(139,92,246,.2),rgba(59,130,246,.2));border:1px solid rgba(139,92,246,.3)">🧠</div>
      <h1 style="background:linear-gradient(135deg,#e6edf3 30%,#a78bfa);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text">{blog_name}</h1>
      <p>{blog_description}</p>
    </div>
  </div>

  <div class="ai-content">

    <!-- 미션 -->
    <div class="ai-card">
      <div class="ai-card-header">
        <div class="ai-card-icon" style="background:rgba(139,92,246,.12)">🎯</div>
        <h2>블로그 미션</h2>
      </div>
      <div class="ai-highlight purple">
        <p style="font-size:15px;font-weight:500;color:#c9d1d9;line-height:1.7">
          "AI 기술을 모두가 쉽게 이해하고 활용할 수 있도록 —<br>
          복잡한 기술을 실용적인 가이드로 변환합니다."
        </p>
      </div>
      <p style="margin-top:14px">AI가 빠르게 발전하는 시대, 어디서부터 시작해야 할지 막막하신가요? <strong style="color:#c9d1d9">{blog_name}</strong>은 ChatGPT, Claude, Gemini 등 최신 AI 도구를 처음 접하는 분들도 바로 활용할 수 있도록 실용적인 가이드를 제공합니다.</p>
    </div>

    <!-- 주요 주제 -->
    <div class="ai-card">
      <div class="ai-card-header">
        <div class="ai-card-icon" style="background:rgba(6,182,212,.12)">⚡</div>
        <h2>다루는 주제</h2>
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:4px">
        <div class="ai-highlight cyan" style="margin:0">
          <p style="font-weight:600;color:#22d3ee;font-size:13px;margin-bottom:6px">🤖 AI 어시스턴트</p>
          <p style="font-size:13px">ChatGPT · Claude · Gemini<br>Copilot · Perplexity</p>
        </div>
        <div class="ai-highlight purple" style="margin:0">
          <p style="font-weight:600;color:#a78bfa;font-size:13px;margin-bottom:6px">⚙️ AI 자동화</p>
          <p style="font-size:13px">업무 자동화 · 프롬프트<br>Zapier · Make · n8n</p>
        </div>
        <div class="ai-highlight" style="margin:0">
          <p style="font-weight:600;color:#60a5fa;font-size:13px;margin-bottom:6px">🛠️ AI 개발 도구</p>
          <p style="font-size:13px">Cursor · GitHub Copilot<br>v0 · Replit</p>
        </div>
        <div class="ai-highlight green" style="margin:0">
          <p style="font-weight:600;color:#34d399;font-size:13px;margin-bottom:6px">📈 생산성 향상</p>
          <p style="font-size:13px">실전 활용 팁<br>업무 효율화 사례</p>
        </div>
      </div>
    </div>

    <!-- 블로그 가치 -->
    <div class="ai-card">
      <div class="ai-card-header">
        <div class="ai-card-icon" style="background:rgba(16,185,129,.12)">✨</div>
        <h2>여러분이 얻을 수 있는 것</h2>
      </div>
      <ul style="list-style:none;padding:0">
        <li style="padding:10px 0;border-bottom:1px solid #21262d;color:#c9d1d9;font-size:14px">
          <span style="color:#34d399;margin-right:10px">✅</span> 따라하기 쉬운 <strong>단계별 AI 활용 가이드</strong>
        </li>
        <li style="padding:10px 0;border-bottom:1px solid #21262d;color:#c9d1d9;font-size:14px">
          <span style="color:#34d399;margin-right:10px">✅</span> 최신 AI 도구 <strong>비교 분석 및 추천</strong>
        </li>
        <li style="padding:10px 0;border-bottom:1px solid #21262d;color:#c9d1d9;font-size:14px">
          <span style="color:#34d399;margin-right:10px">✅</span> 실무에서 바로 쓸 수 있는 <strong>프롬프트 모음</strong>
        </li>
        <li style="padding:10px 0;color:#c9d1d9;font-size:14px">
          <span style="color:#34d399;margin-right:10px">✅</span> AI 업계 <strong>최신 뉴스 및 트렌드</strong>
        </li>
      </ul>
    </div>

    <!-- 운영자 소개 -->
    <div class="ai-card">
      <div class="ai-card-header">
        <div class="ai-card-icon" style="background:rgba(59,130,246,.12)">👤</div>
        <h2>운영자 소개</h2>
      </div>
      <div style="display:flex;align-items:flex-start;gap:16px">
        <div style="width:56px;height:56px;border-radius:16px;background:linear-gradient(135deg,#3B82F6,#8B5CF6);
          display:flex;align-items:center;justify-content:center;font-size:24px;flex-shrink:0">🤖</div>
        <div>
          <p style="font-weight:700;color:#e6edf3;font-size:15px">{author_name}</p>
          <p style="color:#8b949e;font-size:13px;margin-top:4px">AI/IT 분야 콘텐츠 크리에이터</p>
          <p style="color:#8b949e;font-size:14px;margin-top:10px">AI 기술을 직접 활용하며 얻은 실전 경험을 바탕으로, 누구나 AI를 일상과 업무에 적용할 수 있도록 콘텐츠를 제작합니다.</p>
        </div>
      </div>
    </div>

    <!-- CTA -->
    <div class="ai-card" style="text-align:center;background:linear-gradient(135deg,#0d1117,#1a1f35);border-color:#30363d">
      <p style="font-size:16px;font-weight:600;color:#e6edf3;margin-bottom:8px">함께 AI 시대를 열어가요 🚀</p>
      <p style="color:#8b949e;font-size:14px;margin-bottom:20px">구독하고 최신 AI 활용 팁을 가장 먼저 받아보세요</p>
      <div class="ai-tags" style="justify-content:center">
        <span class="ai-tag blue">매주 새 글 업데이트</span>
        <span class="ai-tag cyan">무료 구독</span>
        <span class="ai-tag purple">실전 가이드</span>
      </div>
    </div>

    <div class="ai-footer">
      © {datetime.now().year} {blog_name} · <a href="{blog_url}" style="color:#484f58">{blog_url}</a>
    </div>
  </div>
</div>
"""


# ══════════════════════════════════════════════════════════════════
# 3. 연락처 (Contact)
# ══════════════════════════════════════════════════════════════════
def html_contact(blog_name, blog_email, author_name):
    return BASE_CSS + f"""
<div class="ai-page-wrap">

  <!-- 히어로 -->
  <div class="ai-hero">
    <div class="ai-hero-inner">
      <div class="ai-badge">💬 Contact</div>
      <div class="ai-hero-icon" style="background:rgba(6,182,212,.15);border:1px solid rgba(6,182,212,.3)">✉️</div>
      <h1 style="background:linear-gradient(135deg,#e6edf3 30%,#06B6D4);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text">연락처</h1>
      <p>궁금한 점이 있으신가요? 언제든지 연락해 주세요.</p>
    </div>
  </div>

  <div class="ai-content">

    <!-- 이메일 연락 -->
    <div class="ai-card" style="border-color:rgba(6,182,212,.3)">
      <div class="ai-card-header">
        <div class="ai-card-icon" style="background:rgba(6,182,212,.12)">📧</div>
        <h2>이메일 문의</h2>
      </div>
      <p>가장 빠른 연락 방법은 이메일입니다. 아래 주소로 문의해 주시면 성심껏 답변해 드리겠습니다.</p>
      <div class="ai-highlight cyan" style="margin-top:16px;text-align:center">
        <a href="mailto:{blog_email}" style="color:#22d3ee;font-size:18px;font-weight:600;text-decoration:none">
          📩 {blog_email}
        </a>
      </div>
      <div class="ai-tags" style="margin-top:14px">
        <span class="ai-tag cyan">영업일 1~3일 내 답변</span>
        <span class="ai-tag cyan">한국어 문의 가능</span>
      </div>
    </div>

    <!-- 문의 가능 내용 -->
    <div class="ai-card">
      <div class="ai-card-header">
        <div class="ai-card-icon" style="background:rgba(59,130,246,.12)">💡</div>
        <h2>문의 가능한 내용</h2>
      </div>
      <ul style="list-style:none;padding:0">
        <li style="padding:12px 0;border-bottom:1px solid #21262d;color:#c9d1d9;font-size:14px">
          <span style="color:#22d3ee;margin-right:10px;font-size:16px">🤝</span>
          <strong>협업 · 기고 제안</strong>
          <p style="color:#8b949e;font-size:13px;margin-top:4px;margin-left:26px">공동 프로젝트, 게스트 포스트, 콘텐츠 협업 관련 제안</p>
        </li>
        <li style="padding:12px 0;border-bottom:1px solid #21262d;color:#c9d1d9;font-size:14px">
          <span style="color:#22d3ee;margin-right:10px;font-size:16px">🐛</span>
          <strong>오류 제보</strong>
          <p style="color:#8b949e;font-size:13px;margin-top:4px;margin-left:26px">게시물 내 정보 오류, 링크 오류, 기술적 문제 제보</p>
        </li>
        <li style="padding:12px 0;border-bottom:1px solid #21262d;color:#c9d1d9;font-size:14px">
          <span style="color:#22d3ee;margin-right:10px;font-size:16px">💬</span>
          <strong>피드백 · 의견</strong>
          <p style="color:#8b949e;font-size:13px;margin-top:4px;margin-left:26px">콘텐츠 개선 제안, 다루었으면 하는 주제 요청</p>
        </li>
        <li style="padding:12px 0;color:#c9d1d9;font-size:14px">
          <span style="color:#22d3ee;margin-right:10px;font-size:16px">📢</span>
          <strong>광고 · 협찬 문의</strong>
          <p style="color:#8b949e;font-size:13px;margin-top:4px;margin-left:26px">제품/서비스 리뷰, 스폰서십, 배너 광고 등 제안</p>
        </li>
      </ul>
    </div>

    <!-- 답변 안내 -->
    <div class="ai-card">
      <div class="ai-card-header">
        <div class="ai-card-icon" style="background:rgba(16,185,129,.12)">⏱️</div>
        <h2>답변 안내</h2>
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
        <div class="ai-highlight green" style="margin:0;text-align:center">
          <p style="font-size:24px;font-weight:700;color:#34d399">1~3일</p>
          <p style="font-size:13px;color:#8b949e;margin-top:4px">일반 문의<br>영업일 기준</p>
        </div>
        <div class="ai-highlight" style="margin:0;text-align:center">
          <p style="font-size:24px;font-weight:700;color:#60a5fa">3~5일</p>
          <p style="font-size:13px;color:#8b949e;margin-top:4px">협업·광고 제안<br>영업일 기준</p>
        </div>
      </div>
      <p style="margin-top:14px;font-size:13px;color:#8b949e">
        ※ 스팸성 메일, 광고 목적의 무분별한 문의는 회신이 어렵습니다.<br>
        ※ 주말·공휴일 문의는 익일 영업일부터 처리됩니다.
      </p>
    </div>

    <!-- 광고 협찬 -->
    <div class="ai-card" style="border-color:rgba(245,158,11,.3)">
      <div class="ai-card-header">
        <div class="ai-card-icon" style="background:rgba(245,158,11,.12)">💎</div>
        <h2>광고 · 협찬 문의</h2>
      </div>
      <p style="font-size:14px;color:#8b949e">AI/IT 분야의 제품 또는 서비스 홍보를 원하신다면 아래 내용을 포함하여 이메일로 연락해 주세요.</p>
      <div class="ai-highlight yellow" style="margin-top:14px">
        <ul>
          <li>회사명 및 담당자명</li>
          <li>홍보하려는 제품/서비스 소개</li>
          <li>희망 게재 형태 (리뷰, 배너, 기획 기사 등)</li>
          <li>예산 범위 및 게재 기간</li>
        </ul>
      </div>
    </div>

    <div class="ai-footer">
      © {datetime.now().year} {blog_name} · {author_name}
    </div>
  </div>
</div>
"""


# ══════════════════════════════════════════════════════════════════
# 4. 면책 조항 (Disclaimer)
# ══════════════════════════════════════════════════════════════════
def html_disclaimer(blog_name, blog_niche, blog_email, date):
    return BASE_CSS + f"""
<div class="ai-page-wrap">

  <!-- 히어로 -->
  <div class="ai-hero">
    <div class="ai-hero-inner">
      <div class="ai-badge">⚖️ 법적 고지</div>
      <div class="ai-hero-icon" style="background:rgba(245,158,11,.15);border:1px solid rgba(245,158,11,.3)">📜</div>
      <h1 style="background:linear-gradient(135deg,#e6edf3 30%,#F59E0B);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text">면책 조항</h1>
      <p>Disclaimer · 최종 업데이트: {date}</p>
    </div>
  </div>

  <div class="ai-content">

    <!-- 정보 정확성 -->
    <div class="ai-card">
      <div class="ai-card-header">
        <div class="ai-card-icon" style="background:rgba(245,158,11,.12)">⚠️</div>
        <h2>정보 정확성 면책</h2>
      </div>
      <p>본 블로그에서 제공하는 <strong style="color:#c9d1d9">{blog_niche}</strong> 관련 정보는 작성 시점의 내용을 기반으로 합니다.</p>
      <div class="ai-highlight yellow" style="margin-top:14px">
        <ul>
          <li>AI/IT 분야는 빠르게 발전하므로 최신 정보와 다를 수 있습니다</li>
          <li>중요한 결정 시 공식 문서 및 최신 자료를 반드시 확인하세요</li>
          <li>본 블로그의 정보 활용으로 발생한 손해에 대해 책임지지 않습니다</li>
        </ul>
      </div>
      <div class="ai-tags" style="margin-top:12px">
        <span class="ai-tag" style="border-color:rgba(245,158,11,.3);color:#fbbf24;background:rgba(245,158,11,.08)">정보 최신 여부 확인 권고</span>
      </div>
    </div>

    <!-- 광고 면책 -->
    <div class="ai-card">
      <div class="ai-card-header">
        <div class="ai-card-icon" style="background:rgba(59,130,246,.12)">💰</div>
        <h2>광고 및 제휴 마케팅</h2>
      </div>
      <p>본 블로그는 <strong style="color:#c9d1d9">Google AdSense</strong>를 통한 광고를 게재합니다.</p>
      <div class="ai-highlight" style="margin-top:14px">
        <ul>
          <li>광고 수익은 블로그 운영 및 콘텐츠 제작 비용으로 사용됩니다</li>
          <li>광고 내용은 Google이 자동으로 결정하며, 본 블로그가 특정 광고주를 지지함을 의미하지 않습니다</li>
          <li>제품 리뷰 시 유료 협찬이 포함된 경우 해당 게시물에 별도 표기합니다</li>
        </ul>
      </div>
    </div>

    <!-- 외부 링크 -->
    <div class="ai-card">
      <div class="ai-card-header">
        <div class="ai-card-icon" style="background:rgba(6,182,212,.12)">🔗</div>
        <h2>외부 링크 면책</h2>
      </div>
      <p>본 블로그의 게시물에는 외부 웹사이트로의 링크가 포함될 수 있습니다.</p>
      <div class="ai-highlight cyan" style="margin-top:14px">
        <ul>
          <li>외부 사이트의 콘텐츠, 개인정보처리방침, 서비스에 대해 본 블로그는 책임을 지지 않습니다</li>
          <li>외부 링크 클릭은 해당 사이트의 이용 약관에 동의하는 것입니다</li>
          <li>외부 링크 접속 전 해당 사이트의 신뢰성을 직접 확인하시기 바랍니다</li>
        </ul>
      </div>
    </div>

    <!-- 저작권 -->
    <div class="ai-card">
      <div class="ai-card-header">
        <div class="ai-card-icon" style="background:rgba(139,92,246,.12)">©️</div>
        <h2>저작권 안내</h2>
      </div>
      <p>본 블로그의 모든 콘텐츠(텍스트, 이미지, 동영상 등)는 저작권법의 보호를 받습니다.</p>
      <div class="ai-highlight purple" style="margin-top:14px">
        <ul>
          <li>콘텐츠의 무단 복제, 배포, 상업적 이용을 금지합니다</li>
          <li>인용 시 반드시 출처(<strong style="color:#a78bfa">{blog_name}</strong>)를 명시하고 원문 링크를 포함해야 합니다</li>
          <li>공유 또는 협업 요청은 이메일로 사전 문의해 주세요</li>
        </ul>
      </div>
    </div>

    <!-- 이용자 책임 -->
    <div class="ai-card">
      <div class="ai-card-header">
        <div class="ai-card-icon" style="background:rgba(16,185,129,.12)">👤</div>
        <h2>이용자 책임</h2>
      </div>
      <p>본 블로그의 정보를 활용하여 내리는 모든 결정과 그에 따른 결과는 이용자 본인에게 있습니다. 제공되는 정보는 일반적인 참고 목적이며, 전문적인 법률·의료·금융 조언을 대체하지 않습니다.</p>
    </div>

    <!-- 문의 -->
    <div class="ai-card" style="border-color:rgba(245,158,11,.3)">
      <div class="ai-card-header">
        <div class="ai-card-icon" style="background:rgba(245,158,11,.12)">✉️</div>
        <h2>문의</h2>
      </div>
      <p>면책 조항 관련 문의 또는 저작권 침해 신고는 아래 이메일로 연락해 주세요.</p>
      <div class="ai-highlight yellow" style="margin-top:12px;text-align:center">
        <a href="mailto:{blog_email}" style="color:#fbbf24;font-size:16px;font-weight:600;text-decoration:none">
          📩 {blog_email}
        </a>
      </div>
    </div>

    <div class="ai-footer">
      © {datetime.now().year} {blog_name} · 시행일: {date}
    </div>
  </div>
</div>
"""


# ══════════════════════════════════════════════════════════════════
# 메인 실행
# ══════════════════════════════════════════════════════════════════
def main():
    print("=" * 60)
    print("페이지 디자인 리뉴얼 시작", flush=True)
    print("=" * 60)

    service = get_blogger_service()
    date = datetime.now().strftime("%Y년 %m월 %d일")

    # 기존 페이지 ID 조회
    resp = service.pages().list(blogId=config.BLOG_ID, status="LIVE").execute()
    page_id_map = {p["title"]: p["id"] for p in resp.get("items", [])}
    print(f"발행된 페이지: {list(page_id_map.keys())}", flush=True)

    # 업데이트 대상 정의
    pages = [
        {
            "title": "개인정보처리방침 (Privacy Policy)",
            "html": html_privacy(
                config.BLOG_NAME, config.BLOG_EMAIL,
                config.BLOG_URL, date
            ),
        },
        {
            "title": "블로그 소개 (About)",
            "html": html_about(
                config.BLOG_NAME, config.BLOG_NICHE,
                config.BLOG_DESCRIPTION, config.BLOG_AUTHOR_NAME,
                config.BLOG_URL
            ),
        },
        {
            "title": "연락처 (Contact)",
            "html": html_contact(
                config.BLOG_NAME, config.BLOG_EMAIL,
                config.BLOG_AUTHOR_NAME
            ),
        },
        {
            "title": "면책 조항 (Disclaimer)",
            "html": html_disclaimer(
                config.BLOG_NAME, config.BLOG_NICHE,
                config.BLOG_EMAIL, date
            ),
        },
    ]

    success, failed = [], []

    for page in pages:
        title = page["title"]
        print(f"\n[{title}]", flush=True)

        page_id = page_id_map.get(title)
        if not page_id:
            print(f"  -> 페이지 ID를 찾을 수 없음. 건너뜀.", flush=True)
            failed.append(title)
            continue

        try:
            service.pages().update(
                blogId=config.BLOG_ID,
                pageId=page_id,
                body={
                    "id":      page_id,
                    "title":   title,
                    "content": page["html"],
                    "status":  "LIVE",
                }
            ).execute()
            print(f"  -> 업데이트 완료 ✓", flush=True)
            success.append(title)
        except Exception as e:
            print(f"  -> 오류: {e}", flush=True)
            failed.append(title)

    print("\n" + "=" * 60, flush=True)
    print(f"완료: {len(success)}개 / 실패: {len(failed)}개", flush=True)
    if success:
        for t in success:
            print(f"  OK  {t}", flush=True)
    if failed:
        for t in failed:
            print(f"  FAIL  {t}", flush=True)
    print("=" * 60, flush=True)


if __name__ == "__main__":
    main()
