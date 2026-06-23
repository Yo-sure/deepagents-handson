"""Ch4 산출물 — 인박스를 MCP 서버로 노출한다.

에이전트가 파일과 메일에 닿는 통로를 MCP 한 겹으로 표준화한다. 이 과정의 외부 연결은
둘로 고정한다.
  - 파일 [실선] : classified/·knowledge_base/ 를 실제로 읽는다. 실제 연결.
  - 메일 [목]   : 샘플 메일 목록은 목 데이터. 외부 메일 서버 없이 재현된다.

FastMCP 데코레이터 규칙
  - 함수 이름 → Tool 이름, docstring → 설명(LLM이 보고 호출 판단), 타입힌트 → 입력 스키마.

실행(stdio 대기 — 에이전트가 subprocess로 붙는다):
    uv run python3 ch4-skills-mcp/mcp_inbox_server.py
도구 목록만 점검:
    uv run python3 ch4-skills-mcp/mcp_inbox_server.py --list
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analyst.paths import CLASSIFIED, KNOWLEDGE_BASE

mcp = FastMCP("inbox-mcp-server")
SAFE_RECORD = re.compile(r"^[A-Za-z0-9_.-]+\.json$")

# 샘플 메일 목록(목) — 외부 메일 서버 대신 이번 달 인박스에 도착한 문서 목록.
MOCK_ENVELOPE = [
    {"id": 1, "from": "scan@home", "subject": "영수증 스캔 5건", "kind": "receipt"},
    {"id": 2, "from": "신한카드", "subject": "5월 카드 명세서", "kind": "statement"},
    {"id": 3, "from": "카카오뱅크", "subject": "5월 거래내역", "kind": "statement"},
    {"id": 4, "from": "에이비씨컴퍼니", "subject": "용역 계약서", "kind": "contract"},
]


# ── 파일 [실선] ──────────────────────────────────────────────────


@mcp.tool()
def list_classified() -> str:
    """분류된 레코드(classified/*.json) 목록을 돌려준다. [실선 — 실제 파일]"""
    if not CLASSIFIED.exists():
        return "classified/ 가 비어 있습니다. 먼저 Ch2 intake_graph를 실행하세요."
    files = sorted(CLASSIFIED.glob("*.json"))
    return "\n".join(f.name for f in files) or "(없음)"


@mcp.tool()
def read_record(name: str) -> str:
    """분류 레코드 하나를 읽어 JSON 문자열로 돌려준다. [실선 — 실제 파일]

    Args:
        name: classified 안 파일명(예: receipt_starbucks.json)
    """
    if Path(name).name != name or not SAFE_RECORD.fullmatch(name):
        return f"잘못된 레코드 이름: {name}"
    path = (CLASSIFIED / name).resolve()
    try:
        path.relative_to(CLASSIFIED.resolve())
    except ValueError:
        return f"잘못된 레코드 이름: {name}"
    if not path.exists():
        return f"없는 레코드: {name}"
    return path.read_text(encoding="utf-8")


@mcp.tool()
def search_knowledge(type: str = "gap") -> str:
    """OKF 지식 항목을 type으로 찾는다. [실선 — 실제 파일]

    Args:
        type: gap · subscription · merchant 중 하나
    """
    if not KNOWLEDGE_BASE.exists():
        return "knowledge_base/ 가 비어 있습니다. 먼저 Ch4 okf_store를 실행하세요."
    hits = [p.read_text(encoding="utf-8") for p in sorted(KNOWLEDGE_BASE.glob("*.md"))
            if f"type: {type}" in p.read_text(encoding="utf-8")]
    return "\n\n---\n\n".join(hits) or f"type={type} 항목 없음"


# ── 메일 [목] ────────────────────────────────────────────────────


@mcp.tool()
def fetch_inbox() -> str:
    """이번 달 샘플 메일 목록을 돌려준다. [목 — 외부 메일 서버 없이 재현]"""
    lines = [f"  [{e['id']}] {e['from']} — {e['subject']} ({e['kind']})" for e in MOCK_ENVELOPE]
    return "이번 달 샘플 메일:\n" + "\n".join(lines)


@mcp.resource("inbox://stats")
def inbox_stats() -> str:
    """인박스 통계(읽기 전용 리소스)."""
    n = len(list(CLASSIFIED.glob("*.json"))) if CLASSIFIED.exists() else 0
    return json.dumps({"classified": n, "envelope": len(MOCK_ENVELOPE)}, ensure_ascii=False)


def _list_tools() -> None:
    """등록된 도구를 출력한다(stdio 없이 점검용)."""
    import asyncio

    tools = asyncio.run(mcp.list_tools())
    print(f"inbox-mcp-server 도구 {len(tools)}개:")
    for t in tools:
        tag = "[실선]" if t.name != "fetch_inbox" else "[목]"
        print(f"  {tag} {t.name} — {(t.description or '').splitlines()[0]}")


def _show_protocol() -> None:
    """MCP가 stdio 위에서 실제로 주고받는 JSON-RPC를 그대로 보여 준다(점검용).

    envelope는 직접 짜지만, 안에 든 inputSchema와 tools/call 결과는 진짜 서버에서
    뽑는다 — 즉 에이전트가 이 서버와 stdio로 나누는 대화와 같은 내용이다.
    """
    import asyncio

    print("MCP 통신 = stdio(표준입출력) 위 JSON-RPC 2.0 — 한 줄에 한 메시지.")
    print("에이전트가 이 서버를 subprocess로 띄우고 다음 순서로 말한다:")
    print("  ① initialize → ② notifications/initialized → ③ tools/list(발견) → ④ tools/call(실행)\n")

    tools = asyncio.run(mcp.list_tools())
    one = next(t for t in tools if t.name == "search_knowledge")
    list_resp = {
        "jsonrpc": "2.0", "id": 1,
        "result": {"tools": [{
            "name": one.name,
            "description": (one.description or "").splitlines()[0],
            "inputSchema": one.inputSchema,  # 타입힌트에서 자동 생성된 진짜 스키마
        }]},
    }
    print("③ tools/list 응답 — 도구 이름·설명·inputSchema(타입힌트→JSON Schema). 발췌 1개:")
    print(json.dumps(list_resp, ensure_ascii=False, indent=2))

    call_req = {
        "jsonrpc": "2.0", "id": 2, "method": "tools/call",
        "params": {"name": "search_knowledge", "arguments": {"type": "gap"}},
    }
    content, _raw = asyncio.run(mcp.call_tool("search_knowledge", {"type": "gap"}))
    text = content[0].text if content else ""
    call_resp = {
        "jsonrpc": "2.0", "id": 2,
        "result": {"content": [{"type": "text", "text": text}], "isError": False},
    }
    print("\n④ tools/call 요청(모델이 이 도구를 부르기로 결정 → 어댑터가 보냄):")
    print(json.dumps(call_req, ensure_ascii=False, indent=2))
    print("\n④ tools/call 응답(서버가 함수를 실행해 돌려준 결과):")
    print(json.dumps(call_resp, ensure_ascii=False, indent=2))
    print("\n에이전트 쪽: langchain-mcp-adapters가 각 MCP 도구를 LangChain 도구로 감싼다.")
    print("모델이 그 도구를 부르면 위 tools/call을 stdio로 보내고, 결과를 ToolMessage로 받는다.")


if __name__ == "__main__":
    if "--list" in sys.argv:
        _list_tools()
    elif "--protocol" in sys.argv:
        _show_protocol()
    else:
        mcp.run()  # stdio transport
