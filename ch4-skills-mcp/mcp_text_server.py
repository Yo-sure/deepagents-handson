"""Ch4 — 두 번째 MCP 서버(텍스트 유틸). 멀티서버 데모용.

inbox 서버가 '지식 조회'를 노출한다면, 이 서버는 '텍스트 처리'를 노출한다. 서로 다른
관심사를 별도 MCP 서버로 두고, 클라이언트(MultiServerMCPClient) 하나가 둘을 함께 붙인다.
inbox 서버와 코드 구조는 같다 — FastMCP + @mcp.tool() + mcp.run(). 실행 규약도 동일.

실행:
    uv run python3 ch4-skills-mcp/mcp_text_server.py            # stdio(기본)
    (보통은 직접 실행하지 않고, mcp_multi_client.py가 subprocess로 띄운다)
"""

from __future__ import annotations

import sys

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("text-mcp-server")


@mcp.tool()
def word_count(text: str) -> str:
    """공백 기준 단어 수와 글자 수를 센다."""
    words = len(text.split())
    chars = len(text)
    return f"단어 {words}개 · 글자 {chars}자"


@mcp.tool()
def brief_headline(text: str) -> str:
    """텍스트 첫 줄을 브리프 제목 후보로 다듬는다(앞뒤 공백·마크다운 헤더 기호 제거)."""
    first = next((ln.strip().lstrip("# ").strip() for ln in text.splitlines() if ln.strip()), "")
    return first[:60]


if __name__ == "__main__":
    if "--list" in sys.argv:
        import asyncio

        for t in asyncio.run(mcp.list_tools()):
            print(f"  {t.name} — {(t.description or '').splitlines()[0]}")
    else:
        mcp.run()  # stdio transport
