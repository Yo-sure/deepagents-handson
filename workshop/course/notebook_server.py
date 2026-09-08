"""노트북에서 만든 ASGI 서버를 셀 실행 동안만 제공합니다."""
from contextlib import asynccontextmanager
import asyncio
import socket
import uvicorn

@asynccontextmanager
async def serve_app(app, *, factory=False):
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    if factory:
        app = app(port)
    server = uvicorn.Server(uvicorn.Config(app, log_level="error"))
    task = asyncio.create_task(server.serve(sockets=[sock]))
    try:
        async with asyncio.timeout(10):
            while not server.started:
                if task.done():
                    await task
                    raise RuntimeError("서버가 시작되기 전에 종료됐습니다.")
                await asyncio.sleep(0.02)
        yield f"http://127.0.0.1:{port}"
    finally:
        server.should_exit = True
        try:
            await asyncio.wait_for(asyncio.shield(task), timeout=10)
        except TimeoutError:
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)
        finally:
            sock.close()
