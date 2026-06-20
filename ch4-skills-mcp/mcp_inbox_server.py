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


if __name__ == "__main__":
    if "--list" in sys.argv:
        _list_tools()
    else:
        mcp.run()  # stdio transport
