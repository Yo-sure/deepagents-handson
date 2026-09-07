"""확장 참고 풀이. 아래 조건은 학습용이며 운영 환경 전체 검증은 아닙니다."""
import asyncio
import json
import tempfile
from pathlib import Path
from course.harness_lab import verify
from course.graph_lab import approval_demo
from course.mcp_lab import PROTOCOL
from course.processes import server


def evidence_matches(answer, policy):
    import re
    ids = set(re.findall(r"P-\d+", answer))
    return ids == {policy["id"]} and policy["team"] in answer


def approval_matrix():
    return {value: approval_demo(value)["decision"] for value in ["approve", "reject", "", "approv"]}


def refine_without_stall(draft, topic, revise, limit=2):
    if not 0 <= limit <= 5:
        raise ValueError("수정 상한은 0~5입니다.")
    history = []
    for attempt in range(limit + 1):
        feedback = verify(draft, topic)
        history.append({"attempt": attempt, "draft": draft, "feedback": feedback})
        if not feedback:
            return {"status": "passed", "draft": draft, "history": history}
        if len(history) > 1 and history[-2]["draft"] == draft:
            return {"status": "stalled", "draft": draft, "history": history}
        if attempt == limit:
            return {"status": "held", "draft": draft, "history": history}
        draft = revise(draft, feedback)


def ticket_restart():
    from mcp.client import Client
    async def call(url, content):
        async with Client(url + "/mcp", mode=PROTOCOL) as client:
            result = await client.call_tool("submit_ticket", {"business_key": "operation-1", "content": content})
            data = None if result.is_error else json.loads(result.content[0].text)
            return {"error": result.is_error, "data": data}
    with tempfile.TemporaryDirectory() as temp:
        db = Path(temp) / "tickets.sqlite"
        with server("course.mcp_lab", "--db", db) as url:
            first = asyncio.run(call(url, "정산 문의"))
        with server("course.mcp_lab", "--db", db) as url:
            again = asyncio.run(call(url, "정산 문의"))
            conflict = asyncio.run(call(url, "다른 내용"))
        return {"first": first, "again": again, "conflict": conflict}


def review_version(state, artifact, request_id, version):
    if state in {"submitted", "working"}:
        return "pending"
    if state != "completed" or not isinstance(artifact, dict):
        return "held"
    if not isinstance(request_id, str) or not request_id.strip():
        return "held"
    if type(version) is not int or version < 1 or type(artifact.get("version")) is not int:
        return "held"
    if artifact.get("request_id") != request_id or artifact.get("version") != version:
        return "held"
    return "accepted" if artifact.get("passed") is True else "held"
