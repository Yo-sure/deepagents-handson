"""Ch4 산출물 — MCP 서버를 실제 stdio 클라이언트로 붙여 호출한다.

서버 쪽 `mcp_inbox_server.py`가 도구를 노출하고, 이 파일은 에이전트/호스트 쪽에서
일어나는 일을 최소형으로 보여 준다. stdio subprocess로 서버를 띄우고, MCP 도구를
LangChain Tool 객체로 감싼 뒤 `search_knowledge`를 호출한다.

실행:
    uv run python3 ch4-skills-mcp/mcp_client_demo.py
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

from langchain_mcp_adapters.tools import load_mcp_tools
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parents[1]


async def run_client() -> None:
    server = StdioServerParameters(
        command=sys.executable,
        args=[str(ROOT / "ch4-skills-mcp" / "mcp_inbox_server.py")],
        cwd=str(ROOT),
    )
    with open(os.devnull, "w", encoding="utf-8") as errlog:
        async with stdio_client(server, errlog=errlog) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # 공식 MCP 세션에서 LangChain 도구로 변환한다. 모델은 이 도구 목록만 보면 되고,
                # adapter가 실제 stdio tools/call 왕복을 맡는다.
                tools = await load_mcp_tools(session)
                print("MCP client 연결 완료 — LangChain 도구로 로드:")
                for tool in tools:
                    print(f"  - {tool.name}: {tool.description.splitlines()[0]}")

                search = next(t for t in tools if t.name == "search_knowledge")
                result = await search.ainvoke({"type": "gap"})
                if isinstance(result, list) and result and isinstance(result[0], dict):
                    text = result[0].get("text", "")
                else:
                    text = str(result)
                preview = text.strip().splitlines()[:12]
                print("\nsearch_knowledge(type='gap') 결과 미리보기:")
                for line in preview:
                    print(line)


def main() -> None:
    asyncio.run(run_client())


if __name__ == "__main__":
    main()
