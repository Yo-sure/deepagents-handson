"""학습용 서버 기동·종료. 자신이 시작한 프로세스만 정리합니다."""

import contextlib
import socket
import subprocess
import sys
import time


@contextlib.contextmanager
def server(module: str, *args):
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    process = subprocess.Popen(
        [sys.executable, "-m", module, "--port", str(port), *map(str, args)]
    )
    try:
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            if process.poll() is not None:
                raise RuntimeError(f"{module} 서버 종료: {process.returncode}")
            with socket.socket() as connection:
                if connection.connect_ex(("127.0.0.1", port)) == 0:
                    break
            time.sleep(0.1)
        else:
            raise TimeoutError("서버 시작 시간이 초과됐습니다.")
        yield f"http://127.0.0.1:{port}"
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
