import asyncio
import json
from pathlib import Path
import pytest
from course.common import lookup_policy
from course.langchain_lab import run
from course.graph_lab import build_graph, approval_demo
from course.harness_lab import bounded_refine, fixed_revision
from course.mcp_lab import create_ticket, query, PROTOCOL
from course.a2a_lab import accept_result, delegate
from course.processes import server
from exercises import solutions, student
from exercises.check import evaluate


def test_real_langchain_fixed_tool_cycle():
    trace = run()["trace"]
    assert [m["role"] for m in trace] == ["human", "ai", "tool", "ai"]
    assert trace[1]["tool_calls"][0]["args"] == {"topic": "정산"}
    assert "P-01" in trace[-1]["content"]


def test_unknown_policy_does_not_invent_team():
    trace = run("모름")["trace"]
    assert json.loads(trace[2]["content"])["found"] is False
    assert "재무지원팀" not in trace[-1]["content"]


@pytest.mark.parametrize("decision,expected", [("approve","approved"),("reject","held"),("","held"),("APPROVE","held")])
def test_approval_fails_closed(decision, expected):
    result = approval_demo(decision)
    assert result["paused"] and result["decision"] == expected


def test_loop_pass_does_not_revise():
    def forbidden(*args):
        raise AssertionError("성공 후 수정하면 안 됩니다.")
    assert len(bounded_refine("재무지원팀 P-01", "정산", forbidden)["history"]) == 1


def test_loop_feedback_and_bound():
    seen = []
    def fail_again(draft, feedback):
        seen.append(feedback)
        return draft
    result = bounded_refine("초안", "정산", fail_again, 2)
    assert result["status"] == "held" and len(seen) == 2 and all(seen)
    assert len(result["history"]) == 3
    assert bounded_refine("초안", "정산", fixed_revision, 2)["status"] == "passed"


def test_ticket_conflict_and_repeat(tmp_path):
    db = tmp_path / "ticket.sqlite"
    first = create_ticket(db, "op-1", "문의")
    again = create_ticket(db, "op-1", "문의")
    assert first["ticket_id"] == again["ticket_id"] and again["created"] is False
    with pytest.raises(ValueError):
        create_ticket(db, "op-1", "다른문의")


def test_a2a_rejects_stale_or_missing_result():
    assert accept_result("completed", {"request_id":"x","version":1,"passed":True}, "x", 2) == "held"
    assert accept_result("working", None, "x", 1) == "pending"
    assert accept_result("completed", None, "x", 1) == "held"


@pytest.mark.parametrize("lab", ["langchain","graph","harness","mcp","a2a"])
def test_reference_passes_and_starter_fails(lab):
    assert all(ok for _,ok,_ in evaluate(solutions,lab))
    assert any(not ok for _,ok,_ in evaluate(student,lab))


def test_mcp_http_independent_clients_and_restart(tmp_path):
    from mcp.client import Client
    db = tmp_path / "ticket.sqlite"
    async def submit(url):
        async with Client(url+"/mcp",mode=PROTOCOL) as client:
            result = await client.call_tool("submit_ticket", {"business_key":"same-op","content":"정산문의"})
            assert not result.is_error
            return json.loads(result.content[0].text)
    with server("course.mcp_lab","--db",db) as url:
        first = asyncio.run(submit(url))
        assert "lookup_policy" in asyncio.run(query(url+"/mcp","계정"))["tools"]
    with server("course.mcp_lab","--db",db) as url:
        repeated = asyncio.run(submit(url))
    assert first["ticket_id"] == repeated["ticket_id"] and repeated["created"] is False


def test_a2a_actual_http_result():
    with server("course.a2a_lab") as url:
        good = asyncio.run(delegate(url,{"request_id":"q-1","version":1,"topic":"정산","draft":"재무지원팀 P-01"}))
        bad = asyncio.run(delegate(url,{"request_id":"q-2","version":1,"topic":"정산","draft":"완료"}))
    assert good["state"] == "completed" and good["decision"] == "accepted"
    assert bad["state"] == "completed" and bad["decision"] == "held"
@pytest.mark.parametrize("topic,contact,decision", [("정산", "x", "accepted"), ("계정", "x", "accepted"), ("기타", "x", "ask"), ("정산", "", "ask")])
def test_integration_propagates_remote_policy(topic, contact, decision):
    from course.integration import run
    result = run(topic, contact)
    assert result["decision"] == decision
    if decision == "accepted":
        assert result["policy"]["policy"]["id"] in result["loop"]["draft"]
        assert result["review"]["artifact"]["passed"] is True
