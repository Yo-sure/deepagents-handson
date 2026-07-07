"""Ch4 — 멀티서버 MCP 클라이언트(LangChain). 서버 여럿을 한 클라이언트로 붙인다.

langchain-mcp-adapters의 MultiServerMCPClient는 여러 MCP 서버를 하나의 연결 dict로 받아,
각 서버의 도구를 LangChain 도구(BaseTool)로 감싸 한 목록으로 돌려준다. 서버가 stdio든
HTTP든 클라이언트 코드는 같다 — 연결 dict의 transport만 바꾸면 된다.

실행:
    uv run python3 ch4-skills-mcp/mcp_multi_client.py           # inbox·text 둘 다 stdio(자립 실행)
    uv run python3 ch4-skills-mcp/mcp_multi_client.py --http    # inbox를 HTTP로 연결
        (--http는 다른 터미널에서 먼저: uv run python3 ch4-skills-mcp/mcp_inbox_server.py --http)
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from langchain_mcp_adapters.client import MultiServerMCPClient

REPO = Path(__file__).resolve().parents[1]
HTTP_URL = "http://127.0.0.1:8848/mcp"


def stdio(server_file: str) -> dict:
    """이 .venv 인터프리터로 서버를 subprocess로 띄우는 stdio 연결(클라이언트가 직접 실행)."""
    return {
        "transport": "stdio",
        "command": sys.executable,
        "args": [str(REPO / "ch4-skills-mcp" / server_file)],
        "cwd": str(REPO),
    }


#pragma region multi-client
async def main(use_http: bool) -> None:
    # 서버 둘을 한 dict로. inbox는 stdio 또는 HTTP, text는 stdio. transport만 다르고 나머지는 같다.
    inbox_conn = {"transport": "streamable_http", "url": HTTP_URL} if use_http else stdio("mcp_inbox_server.py")
    client = MultiServerMCPClient(
        {
            "inbox": inbox_conn,                    # 지식 조회 서버
            "text": stdio("mcp_text_server.py"),    # 텍스트 유틸 서버
        },
        tool_name_prefix=True,                      # 서버명 접두사로 이름 충돌 방지
    )
    tools = await client.get_tools()                # 두 서버의 도구를 LangChain 도구로 한 목록에
    itport = "HTTP" if use_http else "stdio"
    print(f"두 MCP 서버에서 모은 도구 {len(tools)}개  (inbox={itport}, text=stdio):")
    for t in tools:
        print(f"  • {t.name} — {(t.description or '').splitlines()[0]}")

    # 각 서버 도구를 하나씩 실제 호출 — 클라이언트는 어느 서버·transport인지 몰라도 똑같이 부른다.
    wc = next((t for t in tools if t.name.endswith("word_count")), None)
    if wc:
        out = await wc.ainvoke({"text": "이번 달 인박스 브리프 초안"})
        print(f"\n[text 서버] {wc.name} → {out}")
#pragma endregion multi-client


if __name__ == "__main__":
    asyncio.run(main("--http" in sys.argv))
