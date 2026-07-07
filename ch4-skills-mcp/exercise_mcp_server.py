"""Ch4 실습 A — MCP 서버를 직접 세운다 (빈칸 채우기).

FastMCP로 '도구를 노출하는 서버'를 스캐폴드에서 완성한다. 핵심은 하나 — 함수에
`@mcp.tool()`을 달면 그 함수가 곧 MCP 도구(클라이언트가 tools/list로 발견)가 된다.
채울 칸은 둘:

  ① greet 함수를 도구로 노출하는 데코레이터 한 줄
  ② 두 번째 도구(word_count)를 통째로 — 데코레이터 + 함수

키·네트워크 불필요. 등록된 도구를 세어 자가점검한다:

    uv run python3 ch4-skills-mcp/exercise_mcp_server.py --list   # ✅ 2/2 면 서버 완성
    uv run python3 ch4-skills-mcp/exercise_mcp_server.py          # (완성 후) stdio 서버로 대기

막히면 정답: mcp_text_server.py (같은 FastMCP + @mcp.tool() 구조).
"""

from __future__ import annotations

import sys

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("exercise-mcp-server")


# ── 빈칸 ① : 아래 greet 함수를 '도구'로 노출하세요. ─────────────────
# TODO ①: 함수 바로 위에 데코레이터 한 줄을 다세요.  (힌트: @mcp.tool())
def greet(name: str) -> str:
    """이름을 받아 인사말을 돌려준다."""
    return f"안녕하세요, {name}님"


# ── 빈칸 ② : 두 번째 도구를 통째로 만드세요. ───────────────────────
# TODO ②: word_count(text: str) -> str 를 @mcp.tool()로 만들어
#         "단어 N개"를 돌려주세요.  (힌트: len(text.split()))
#   @mcp.tool()
#   def word_count(text: str) -> str:
#       """공백 기준 단어 수를 센다."""
#       return f"단어 {len(text.split())}개"


# 여기가 서버를 stdio로 띄우는 자리다(이미 채워져 있음). 위 두 도구를 노출해 대기한다.
def _serve() -> None:
    mcp.run()  # stdio transport — 클라이언트가 subprocess로 붙는다


def _check() -> None:
    import asyncio

    names = {t.name for t in asyncio.run(mcp.list_tools())}
    need = ["greet", "word_count"]
    for n in need:
        print(f"  {'✅' if n in names else '⬜'} {n} 도구")
    done = sum(n in names for n in need)
    print(f"\n결과: {done}/{len(need)}" + ("  🎉 서버 완성! (--list 없이 실행하면 서버가 뜹니다)"
                                           if done == len(need) else "  — 빈칸을 채우세요 (정답: mcp_text_server.py)"))


if __name__ == "__main__":
    if "--list" in sys.argv or "--check" in sys.argv:
        _check()
    else:
        _serve()
