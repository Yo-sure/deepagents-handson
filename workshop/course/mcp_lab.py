"""MCP 2.x HTTP 서버. 상태는 SQLite에, 요청은 독립적으로 처리합니다."""

import sqlite3
from pathlib import Path
from mcp.server.mcpserver import MCPServer
from mcp.client import Client
from .common import lookup_policy

PROTOCOL = "2026-07-28"


# region ticket
def create_ticket(db: Path, business_key: str, content: str) -> dict:
    if not business_key.strip() or not content.strip():
        raise ValueError("업무 키와 내용을 입력하십시오.")
    with sqlite3.connect(db) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS ticket (id INTEGER PRIMARY KEY, business_key TEXT UNIQUE, content TEXT)"
        )
        conn.execute("BEGIN IMMEDIATE")
        existing = conn.execute(
            "SELECT id, content FROM ticket WHERE business_key=?", (business_key,)
        ).fetchone()
        if existing:
            if existing[1] != content:
                raise ValueError("같은 업무 키에 다른 내용이 전달됐습니다.")
            return {"ticket_id": existing[0], "created": False}
        cursor = conn.execute(
            "INSERT INTO ticket(business_key, content) VALUES (?, ?)",
            (business_key, content),
        )
        return {"ticket_id": cursor.lastrowid, "created": True}


# endregion ticket


# region server
def make_server(db: Path):
    server = MCPServer("업무 정책 도구")
    server.tool()(lookup_policy)

    @server.tool()
    def submit_ticket(business_key: str, content: str) -> dict:
        """Create a local practice ticket; reuse the same key for the same operation."""
        return create_ticket(db, business_key, content)

    return server


# endregion server


# region client
async def query(url: str, topic: str):
    async with Client(url, mode=PROTOCOL) as client:
        catalog = await client.list_tools()
        result = await client.call_tool("lookup_policy", {"topic": topic})
        if result.is_error:
            raise RuntimeError("도구 실행 실패")
        return {
            "protocol": PROTOCOL,
            "tools": [t.name for t in catalog.tools],
            "result": result.model_dump(mode="json"),
        }


# endregion client


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=9710)
    parser.add_argument("--db", type=Path, required=True)
    args = parser.parse_args()
    args.db.parent.mkdir(parents=True, exist_ok=True)
    make_server(args.db).run(
        transport="streamable-http",
        host="127.0.0.1",
        port=args.port,
        stateless_http=True,
        json_response=True,
    )
