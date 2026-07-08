"""
app.py - Blogger Auto Setup 웹 대시보드

Flask 기반 대시보드로 블로그 초기 세팅 파이프라인을 관리합니다.
실행: python app.py
접속: http://localhost:5000
"""

import re
import os
import sys
import io
import json

# Windows cp949 환경 UTF-8 강제 설정
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import time
import queue
import threading
import subprocess
from pathlib import Path
from datetime import datetime
from flask import Flask, jsonify, render_template, request, Response
from flask_cors import CORS
import config

# .env 파일 경로
ENV_PATH = Path(__file__).parent / '.env'

# 알려진 키 메타데이터 (라벨, 설명, 민감 여부)
ENV_KEY_META = {
    'BLOG_ID':           {'label': '블로그 ID',        'desc': 'Blogger 블로그 고유 ID (URL에서 확인)',       'sensitive': False, 'required': True},
    'ANTHROPIC_API_KEY': {'label': 'Anthropic API 키', 'desc': 'Claude AI API 키 — STEP 3 페이지 생성에 사용', 'sensitive': True,  'required': True},
    'BLOG_NAME':         {'label': '블로그명',          'desc': '블로그 이름',                                'sensitive': False, 'required': False},
    'BLOG_DESCRIPTION':  {'label': '블로그 설명',       'desc': '블로그 소개 문구 (About 페이지에 반영)',       'sensitive': False, 'required': False},
    'BLOG_NICHE':        {'label': '블로그 니치',       'desc': '블로그 주제/카테고리',                        'sensitive': False, 'required': False},
    'BLOG_AUTHOR_NAME':  {'label': '운영자명',          'desc': '블로그 운영자 이름',                          'sensitive': False, 'required': False},
    'BLOG_EMAIL':        {'label': '이메일',            'desc': '문의 이메일 주소 (Contact 페이지에 반영)',     'sensitive': False, 'required': False},
    'BLOG_URL':          {'label': '블로그 URL',        'desc': '블로그 주소 (https://xxx.blogspot.com)',      'sensitive': False, 'required': False},
}

app = Flask(__name__)
CORS(app)
app.config['JSON_AS_ASCII'] = False   # 한국어 JSON 인코딩 지원

# ── 전역 상태 ──────────────────────────────────────────────────
log_queue = queue.Queue(maxsize=500)

pipeline_status = {
    'step1': {'status': 'idle', 'last_run': None},
    'step2': {'status': 'idle', 'last_run': None},
    'step3': {'status': 'idle', 'last_run': None},
}

STEP_FILES = {
    'step1': 'step1_verify.py',
    'step2': 'step2_theme.py',
    'step3': 'step3_pages.py',
}

STEP_NAMES = {
    'step1': '블로그 연결 확인',
    'step2': '커스텀 CSS 테마 적용',
    'step3': '필수 페이지 자동 생성',
}


# ─────────────────────────────────────────────────────────────
# 유틸리티
# ─────────────────────────────────────────────────────────────

def strip_ansi(text: str) -> str:
    """터미널 ANSI 색상 코드 제거"""
    return re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])').sub('', text)


def add_log(level: str, message: str):
    """로그 큐에 항목 추가 (overflow 시 무시)"""
    try:
        log_queue.put_nowait({
            'type': 'log',
            'time': datetime.now().strftime('%H:%M:%S'),
            'level': level,   # info | success | error | output
            'msg': message,
        })
    except queue.Full:
        pass


def execute_step(step: str):
    """
    지정된 스텝을 서브프로세스로 실행.
    stdout/stderr를 실시간으로 log_queue로 전달.
    """
    pipeline_status[step]['status'] = 'running'
    add_log('info', f'▶ {STEP_NAMES[step]} 시작')

    try:
        import os
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        env['PYTHONUTF8'] = '1'

        proc = subprocess.Popen(
            [sys.executable, STEP_FILES[step]],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace',
            bufsize=1,
            env=env,
        )
        # 실시간 출력 스트리밍
        for line in iter(proc.stdout.readline, ''):
            clean = strip_ansi(line.rstrip())
            if clean:
                add_log('output', clean)
        proc.wait()

        if proc.returncode == 0:
            pipeline_status[step]['status'] = 'success'
            add_log('success', f'✅ {STEP_NAMES[step]} 완료')
        else:
            pipeline_status[step]['status'] = 'failed'
            add_log('error', f'❌ {STEP_NAMES[step]} 실패 (종료코드: {proc.returncode})')

    except FileNotFoundError:
        pipeline_status[step]['status'] = 'failed'
        add_log('error', f'❌ {STEP_FILES[step]} 파일을 찾을 수 없습니다')
    except Exception as e:
        pipeline_status[step]['status'] = 'failed'
        add_log('error', f'❌ 오류 발생: {e}')

    pipeline_status[step]['last_run'] = datetime.now().strftime('%Y-%m-%d %H:%M')


# ─────────────────────────────────────────────────────────────
# 라우트: 메인 대시보드
# ─────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('dashboard.html',
        blog_name=config.BLOG_NAME or '내 블로그',
        blog_url=config.BLOG_URL or '#',
        blog_niche=config.BLOG_NICHE or '',
    )


# ─────────────────────────────────────────────────────────────
# API: 블로그 통계
# ─────────────────────────────────────────────────────────────

@app.route('/api/stats')
def api_stats():
    try:
        from auth import get_blogger_service
        service = get_blogger_service()
        blog = service.blogs().get(blogId=config.BLOG_ID).execute()
        return jsonify({
            'ok': True,
            'name':    blog.get('name', ''),
            'url':     blog.get('url', ''),
            'posts':   int(blog.get('posts', {}).get('totalItems', 0)),
            'pages':   int(blog.get('pages', {}).get('totalItems', 0)),
            'updated': blog.get('updated', '')[:10],
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)})


# ─────────────────────────────────────────────────────────────
# API: 페이지 목록
# ─────────────────────────────────────────────────────────────

@app.route('/api/pages')
def api_pages():
    try:
        from auth import get_blogger_service
        service = get_blogger_service()
        resp = service.pages().list(blogId=config.BLOG_ID, status='LIVE').execute()
        pages = [
            {
                'id':        p['id'],
                'title':     p.get('title', ''),
                'url':       p.get('url', ''),
                'published': p.get('published', '')[:10],
            }
            for p in resp.get('items', [])
        ]
        return jsonify({'ok': True, 'pages': pages})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)})


# ─────────────────────────────────────────────────────────────
# API: 페이지 삭제
# ─────────────────────────────────────────────────────────────

@app.route('/api/pages/<page_id>', methods=['DELETE'])
def api_delete_page(page_id):
    try:
        from auth import get_blogger_service
        service = get_blogger_service()
        service.pages().delete(blogId=config.BLOG_ID, pageId=page_id).execute()
        add_log('success', f'페이지 삭제 완료 (ID: {page_id})')
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)})


# ─────────────────────────────────────────────────────────────
# API: 파이프라인 스텝 개별 실행
# ─────────────────────────────────────────────────────────────

@app.route('/api/run/<step>', methods=['POST'])
def api_run_step(step):
    if step not in STEP_FILES:
        return jsonify({'ok': False, 'error': '알 수 없는 스텝입니다'}), 400

    if pipeline_status[step]['status'] == 'running':
        return jsonify({'ok': False, 'error': '이미 실행 중입니다'}), 409

    t = threading.Thread(target=execute_step, args=(step,), daemon=True)
    t.start()
    return jsonify({'ok': True})


# ─────────────────────────────────────────────────────────────
# API: 전체 파이프라인 실행 (1 → 2 → 3 순서)
# ─────────────────────────────────────────────────────────────

@app.route('/api/run/all', methods=['POST'])
def api_run_all():
    if any(s['status'] == 'running' for s in pipeline_status.values()):
        return jsonify({'ok': False, 'error': '이미 실행 중인 스텝이 있습니다'}), 409

    def run_all():
        for step in ['step1', 'step2', 'step3']:
            execute_step(step)
            if pipeline_status[step]['status'] == 'failed':
                add_log('error', f'⚠️ {step} 실패로 인해 파이프라인 중단')
                break
            time.sleep(1)  # 스텝 간 딜레이

    t = threading.Thread(target=run_all, daemon=True)
    t.start()
    return jsonify({'ok': True})


# ─────────────────────────────────────────────────────────────
# API: 파이프라인 상태 조회
# ─────────────────────────────────────────────────────────────

@app.route('/api/status')
def api_status():
    return jsonify(pipeline_status)


# ─────────────────────────────────────────────────────────────
# API: 실시간 로그 스트리밍 (Server-Sent Events)
# ─────────────────────────────────────────────────────────────

@app.route('/api/logs/stream')
def api_log_stream():
    def generate():
        # 초기 연결 확인 메시지
        yield f"data: {json.dumps({'type': 'connected', 'level': 'info', 'msg': '✅ 로그 스트림 연결됨', 'time': datetime.now().strftime('%H:%M:%S')}, ensure_ascii=False)}\n\n"

        while True:
            try:
                log = log_queue.get(timeout=25)
                yield f"data: {json.dumps(log, ensure_ascii=False)}\n\n"
            except queue.Empty:
                # 연결 유지용 ping
                yield f"data: {json.dumps({'type': 'ping'})}\n\n"

    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive',
        }
    )


# ─────────────────────────────────────────────────────────────
# API: 로그 초기화
# ─────────────────────────────────────────────────────────────

@app.route('/api/logs/clear', methods=['POST'])
def api_clear_logs():
    while not log_queue.empty():
        try:
            log_queue.get_nowait()
        except queue.Empty:
            break
    return jsonify({'ok': True})


# ─────────────────────────────────────────────────────────────
# .env 파일 파서 유틸리티
# ─────────────────────────────────────────────────────────────

def parse_env_file():
    """
    .env 파일을 파싱하여 줄 단위 구조 반환.
    [{'type': 'comment'|'blank'|'kv', 'content': ..., 'key': ..., 'value': ...}]
    """
    entries = []
    if not ENV_PATH.exists():
        return entries
    with open(ENV_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n\r')
            if not line:
                entries.append({'type': 'blank', 'content': ''})
            elif line.startswith('#'):
                entries.append({'type': 'comment', 'content': line})
            elif '=' in line:
                key, _, value = line.partition('=')
                entries.append({'type': 'kv', 'key': key.strip(), 'value': value.strip()})
            else:
                entries.append({'type': 'comment', 'content': line})
    return entries


def write_env_file(entries):
    """파싱된 구조를 .env 파일로 직렬화"""
    lines = []
    for e in entries:
        if e['type'] == 'kv':
            lines.append(f"{e['key']}={e['value']}")
        else:
            lines.append(e.get('content', ''))
    with open(ENV_PATH, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines) + '\n')


def reload_config():
    """변경된 .env 를 config 모듈에 즉시 반영"""
    from dotenv import load_dotenv
    load_dotenv(ENV_PATH, override=True)
    import importlib
    importlib.reload(config)


# ─────────────────────────────────────────────────────────────
# API: 환경설정 조회
# ─────────────────────────────────────────────────────────────

@app.route('/api/config')
def api_config_get():
    entries = parse_env_file()
    result = []
    for e in entries:
        if e['type'] != 'kv':
            continue
        key = e['key']
        value = e['value']
        meta = ENV_KEY_META.get(key, {})
        # 민감한 키는 마스킹 (앞 8자만 노출)
        masked = meta.get('sensitive', False)
        display_value = (value[:8] + '…' + value[-4:]) if (masked and len(value) > 12) else value
        result.append({
            'key':      key,
            'value':    value,          # 실제 값 (저장 시 사용)
            'display':  display_value,  # UI 표시용
            'label':    meta.get('label', key),
            'desc':     meta.get('desc', ''),
            'sensitive': masked,
            'required': meta.get('required', False),
        })
    return jsonify({'ok': True, 'config': result})


# ─────────────────────────────────────────────────────────────
# API: 환경설정 저장 (단일 키 추가 또는 수정)
# ─────────────────────────────────────────────────────────────

@app.route('/api/config', methods=['POST'])
def api_config_set():
    body = request.get_json()
    if not body or 'key' not in body or 'value' not in body:
        return jsonify({'ok': False, 'error': '키와 값이 필요합니다'}), 400

    key   = body['key'].strip().upper().replace(' ', '_')
    value = body['value'].strip()

    if not key:
        return jsonify({'ok': False, 'error': '키 이름이 비어 있습니다'}), 400

    entries = parse_env_file()
    updated = False
    for e in entries:
        if e['type'] == 'kv' and e['key'] == key:
            e['value'] = value
            updated = True
            break

    if not updated:
        # 새 키 추가 (파일 끝에)
        entries.append({'type': 'kv', 'key': key, 'value': value})

    write_env_file(entries)
    reload_config()
    add_log('success', f'⚙️ 설정 저장: {key}')
    return jsonify({'ok': True, 'created': not updated})


# ─────────────────────────────────────────────────────────────
# API: 환경설정 삭제
# ─────────────────────────────────────────────────────────────

@app.route('/api/config/<key>', methods=['DELETE'])
def api_config_delete(key):
    key = key.upper()
    entries = parse_env_file()
    before = len([e for e in entries if e['type'] == 'kv'])
    entries = [e for e in entries if not (e['type'] == 'kv' and e['key'] == key)]
    after = len([e for e in entries if e['type'] == 'kv'])

    if before == after:
        return jsonify({'ok': False, 'error': f'{key} 키를 찾을 수 없습니다'}), 404

    write_env_file(entries)
    reload_config()
    add_log('info', f'⚙️ 설정 삭제: {key}')
    return jsonify({'ok': True})


# ─────────────────────────────────────────────────────────────
# 실행 진입점
# ─────────────────────────────────────────────────────────────

if __name__ == '__main__':
    try:
        config.validate()
        print(f"✅ 설정 확인 완료 | 블로그: {config.BLOG_NAME}")
    except EnvironmentError as e:
        print(f"⚠️  {e}")
        print("일부 기능이 제한될 수 있습니다. .env 파일을 확인하세요.")

    print("\n" + "="*50)
    print("🚀 Blogger Auto Setup 대시보드 시작")
    print("   접속: http://localhost:5000")
    print("="*50 + "\n")

    app.run(
        debug=False,      # 운영 환경에서는 False
        host='0.0.0.0',  # 외부 접근 허용 (Railway 배포 시 필요)
        port=5000,
        threaded=True,    # SSE 스트리밍을 위해 필수
    )
