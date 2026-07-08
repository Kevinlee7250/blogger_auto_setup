# 🚀 Blogger Auto Setup

**구글 애드센스 승인 조건에 최적화된 블로그 초기 세팅 자동화 파이프라인**

Claude AI + Blogger API + Google OAuth를 결합해 애드센스 승인에 필요한 모든 초기 세팅을 자동화하고, 웹 대시보드로 어디서든 관리합니다.

---

## ✨ 기능

| 기능 | 설명 |
|------|------|
| **STEP 1** | 블로그 연결 확인 (Google OAuth, 블로그 정보 조회) |
| **STEP 2** | 반응형 CSS 테마 자동 생성 & 적용 가이드 |
| **STEP 3** | Claude AI로 필수 4개 페이지 자동 생성 & 발행 |
| **웹 대시보드** | 실시간 로그 · 블로그 통계 · 파이프라인 원클릭 실행 |
| **GitHub Actions** | 브라우저에서 직접 파이프라인 원격 실행 |

---

## 🗂 프로젝트 구조

```
blogger_auto_setup/
├── app.py                  # Flask 대시보드 서버
├── main.py                 # 파이프라인 CLI 실행
├── config.py               # 환경변수 로더
├── auth.py                 # Google OAuth 인증
├── step1_verify.py         # STEP 1: 블로그 연결 확인
├── step2_theme.py          # STEP 2: CSS 테마 생성
├── step3_pages.py          # STEP 3: 필수 페이지 생성
├── templates/
│   └── dashboard.html      # 대시보드 UI
├── requirements.txt
├── .env.example            # 환경변수 템플릿
├── Procfile                # Railway/Heroku 배포용
└── .github/
    └── workflows/
        └── blogger_setup.yml   # GitHub Actions 워크플로우
```

---

## ⚡ 빠른 시작

### 1. 저장소 클론

```bash
git clone https://github.com/YOUR_USERNAME/blogger_auto_setup.git
cd blogger_auto_setup
```

### 2. 패키지 설치

```bash
pip install -r requirements.txt
```

### 3. 환경변수 설정

```bash
cp .env.example .env
# .env 파일을 열어 값 입력
```

```env
BLOG_ID=1234567890          # Blogger 블로그 ID
ANTHROPIC_API_KEY=sk-ant-...
BLOG_NAME=내 AI 블로그
BLOG_DESCRIPTION=AI/IT 최신 트렌드
BLOG_NICHE=AI/IT
BLOG_AUTHOR_NAME=홍길동
BLOG_EMAIL=myemail@gmail.com
BLOG_URL=https://my-blog.blogspot.com
```

> **BLOG_ID 찾는 법:** Blogger 관리자 → URL에서 `blogId=` 뒤 숫자

### 4. Google OAuth 설정

1. [Google Cloud Console](https://console.cloud.google.com) → 새 프로젝트 생성
2. **APIs & Services** → **Library** → `Blogger API v3` 활성화
3. **OAuth consent screen** 설정 (External, 본인 이메일 추가)
4. **Credentials** → **Create OAuth 2.0 Client ID** (Desktop App 선택)
5. JSON 다운로드 → `credentials.json`으로 저장 (프로젝트 루트)

### 5. 대시보드 실행

```bash
python app.py
```

브라우저에서 → **http://localhost:5000** 접속

처음 실행 시 브라우저가 열려 Google 로그인 요청 → 승인 후 자동 인증 완료

---

## 🖥 대시보드 사용법

![대시보드 레이아웃]

| 섹션 | 기능 |
|------|------|
| **상단 통계** | 게시물 수 · 페이지 수 · 파이프라인 진행률 · 마지막 업데이트 |
| **파이프라인 카드** | STEP 1~3 개별 실행 또는 "전체 실행" 원클릭 |
| **페이지 관리** | 발행된 페이지 목록 조회 · URL 방문 · 삭제 |
| **실시간 로그** | 파이프라인 실행 출력 실시간 스트리밍 |

---

## 🌐 GitHub Actions (원격 실행)

브라우저에서 GitHub를 통해 어디서든 파이프라인을 실행할 수 있습니다.

### GitHub Secrets 설정

저장소 → **Settings → Secrets and variables → Actions** 에서 아래를 추가:

| Secret | 값 |
|--------|---|
| `BLOG_ID` | Blogger 블로그 ID |
| `ANTHROPIC_API_KEY` | Anthropic API 키 |
| `GOOGLE_CREDENTIALS_B64` | credentials.json을 Base64 인코딩한 값 |
| `GOOGLE_TOKEN_B64` | token.pickle을 Base64 인코딩한 값 |

#### Base64 인코딩 방법 (로컬에서 최초 1회 OAuth 실행 후):

```bash
# credentials.json 인코딩
python -c "import base64; print(base64.b64encode(open('credentials.json','rb').read()).decode())"

# token.pickle 인코딩 (python app.py 실행 후 생성됨)
python -c "import base64; print(base64.b64encode(open('token.pickle','rb').read()).decode())"
```

### GitHub Variables 설정 (Settings → Variables)

| Variable | 값 |
|----------|---|
| `BLOG_NAME` | 블로그 이름 |
| `BLOG_DESCRIPTION` | 블로그 설명 |
| `BLOG_EMAIL` | 운영자 이메일 |
| `BLOG_URL` | 블로그 URL |
| `BLOG_NICHE` | 블로그 주제 |
| `BLOG_AUTHOR_NAME` | 운영자 이름 |

### 워크플로우 실행

1. GitHub 저장소 → **Actions** 탭
2. **Blogger Setup Pipeline** 선택
3. **Run workflow** → 실행할 스텝 선택 → 실행

---

## ☁️ Railway 배포 (선택사항)

대시보드를 클라우드에 배포해 외부에서 접근 가능하게 합니다.

```bash
# Railway CLI 설치
npm install -g @railway/cli

# 로그인 & 배포
railway login
railway init
railway up
```

Railway 환경변수 설정: Dashboard → Variables → 위 `.env` 값 입력

> ⚠️ **보안 주의:** 배포 시 기본 인증(Basic Auth)을 추가하거나 IP 제한을 설정하세요.

---

## 🔑 API 키 취득 가이드

| API | 취득 방법 |
|-----|---------|
| **Anthropic API** | https://console.anthropic.com → API Keys |
| **Google OAuth** | https://console.cloud.google.com → Credentials |
| **Blogger ID** | https://www.blogger.com → 블로그 선택 → URL의 `blogId=` 값 |

---

## 📅 다음 개발 예정 (STEP 4~6)

- **STEP 4**: 네이버 DataLab API로 키워드 트렌드 자동 수집
- **STEP 5**: Claude AI로 SEO 최적화 글 자동 생성 & Blogger 발행
- **STEP 6**: 트래픽 모니터링 & 애드센스 신청 자동 알림

---

## 📄 라이선스

MIT License — 개인 학습 및 상업적 사용 가능
