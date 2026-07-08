"""
app.py - Blogger Auto Setup 웹 대시보드

Flask 기반 대시보드로 블로그 초기 세팅 파이프라인을 관리합니다.
실행: python app.py
접속: http://localhost:5000
"""

import re
import sys
import json
import time
import queue
import threading
import subprocess
from datetime import datetime
from flask import Flask, jsonify, render_template, request, Response
from flask_cors import CORS
import config

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
        proc = subprocess.Popen(
            [sys.executable, STEP_FILES[step]],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace',
            bufsize=1,
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
