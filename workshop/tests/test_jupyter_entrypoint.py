"""교재의 시작 명령으로 노트북과 Skill 파일에 모두 접근할 수 있어야 합니다."""
import json
import os
from pathlib import Path
import secrets
import shlex
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request


ROOT = Path(__file__).resolve().parents[1]


def test_documented_jupyter_command_exposes_workshop_files(tmp_path):
    command = next(line for line in (ROOT / 'README.md').read_text(encoding='utf-8').splitlines()
                   if line.startswith('.venv/bin/jupyter lab '))
    assert command in (ROOT / 'setup.sh').read_text(encoding='utf-8')
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    token = secrets.token_urlsafe(24)
    args = [sys.executable, '-m', 'jupyterlab', *shlex.split(command)[2:],
            '--no-browser', f'--port={port}', '--ServerApp.port_retries=0',
            f'--IdentityProvider.token={token}']
    env = {**os.environ, 'JUPYTER_RUNTIME_DIR': str(tmp_path / 'runtime')}
    server = subprocess.Popen(args, cwd=ROOT, env=env,
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    def get(path):
        request = urllib.request.Request(f'http://127.0.0.1:{port}/api/contents/{path}',
                                         headers={'Authorization': 'token ' + token})
        with urllib.request.urlopen(request, timeout=2) as response:
            return json.load(response)
    try:
        deadline = time.monotonic() + 30
        while True:
            assert server.poll() is None, 'JupyterLab 시작 실패'
            try:
                notebook = get('notebooks/orientation.ipynb')
                break
            except urllib.error.URLError:
                if time.monotonic() >= deadline:
                    raise
                time.sleep(0.2)
        assert notebook['type'] == 'notebook'
        skill = get('skills/policy-answer/SKILL.md')
        assert skill['type'] == 'file'
        assert 'policy-answer' in skill['content']
    finally:
        server.terminate()
        try:
            server.wait(timeout=10)
        except subprocess.TimeoutExpired:
            server.kill()
            server.wait(timeout=5)
