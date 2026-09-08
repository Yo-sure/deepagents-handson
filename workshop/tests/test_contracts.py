import asyncio
import json
import pytest
from course.langchain_lab import run
from course.graph_lab import approval_demo
from course.harness_lab import bounded_refine
from course.mcp_lab import create_ticket, query, PROTOCOL
from course.a2a_lab import accept_result, delegate
from course.processes import server
from exercises import solutions, student
from exercises.check import evaluate
from tests.model_stub import ToolCallingStub


def test_cli_runs_real_path_without_mode_selection(monkeypatch, tmp_path):
    import sys
    from course import cli, langchain_lab

    calls = []

    def capture(topic):
        calls.append(topic)
        return {"trace": []}

    monkeypatch.setattr(langchain_lab, "run", capture)
    monkeypatch.setattr(cli, "ROOT", tmp_path)
    monkeypatch.setattr(sys, "argv", ["course.cli", "langchain"])
    cli.main()
    assert calls == ["정산"]
    assert (tmp_path / "runs" / "langchain.json").is_file()


def test_cli_rejects_removed_mode_option(monkeypatch):
    import sys
    from course import cli

    monkeypatch.setattr(sys, "argv", ["course.cli", "langchain", "--mode", "fixed"])
    with pytest.raises(SystemExit) as error:
        cli.main()
    assert error.value.code == 2


def test_langchain_tool_cycle_with_injected_model():
    trace = run(model=ToolCallingStub())["trace"]
    assert [m["role"] for m in trace] == ["human", "ai", "tool", "ai"]
    assert trace[1]["tool_calls"][0]["args"] == {"topic": "정산"}
    assert "P-01" in trace[-1]["content"]


def test_unknown_policy_does_not_invent_team():
    trace = run("모름", model=ToolCallingStub())["trace"]
    assert json.loads(trace[2]["content"])["found"] is False
    assert "재무지원팀" not in trace[-1]["content"]


@pytest.mark.parametrize(
    "decision,expected",
    [("approve", "approved"), ("reject", "held"), ("", "held"), ("APPROVE", "held")],
)
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
    assert (
        bounded_refine("초안", "정산", lambda *_: "재무지원팀 P-01", 2)["status"]
        == "passed"
    )


def test_ticket_conflict_and_repeat(tmp_path):
    db = tmp_path / "ticket.sqlite"
    first = create_ticket(db, "op-1", "문의")
    again = create_ticket(db, "op-1", "문의")
    assert first["ticket_id"] == again["ticket_id"] and again["created"] is False
    with pytest.raises(ValueError):
        create_ticket(db, "op-1", "다른문의")


def test_a2a_rejects_stale_or_missing_result():
    assert (
        accept_result(
            "completed", {"request_id": "x", "version": 1, "passed": True}, "x", 2
        )
        == "held"
    )
    assert accept_result("working", None, "x", 1) == "pending"
    assert accept_result("completed", None, "x", 1) == "held"


@pytest.mark.parametrize("lab", ["langchain", "graph", "harness", "mcp", "a2a"])
def test_reference_passes_and_starter_fails(lab):
    assert all(ok for _, ok, _ in evaluate(solutions, lab))
    assert any(not ok for _, ok, _ in evaluate(student, lab))


def test_mcp_http_independent_clients_and_restart(tmp_path):
    from mcp.client import Client

    db = tmp_path / "ticket.sqlite"

    async def submit(url):
        async with Client(url + "/mcp", mode=PROTOCOL) as client:
            result = await client.call_tool(
                "submit_ticket", {"business_key": "same-op", "content": "정산문의"}
            )
            assert not result.is_error
            return json.loads(result.content[0].text)

    with server("course.mcp_lab", "--db", db) as url:
        first = asyncio.run(submit(url))
        assert "lookup_policy" in asyncio.run(query(url + "/mcp", "계정"))["tools"]
    with server("course.mcp_lab", "--db", db) as url:
        repeated = asyncio.run(submit(url))
    assert first["ticket_id"] == repeated["ticket_id"] and repeated["created"] is False


def test_a2a_actual_http_result():
    with server("tests.a2a_server") as url:
        good = asyncio.run(
            delegate(
                url,
                {
                    "request_id": "q-1",
                    "version": 1,
                    "topic": "정산",
                    "draft": "재무지원팀 P-01",
                },
            )
        )
        bad = asyncio.run(
            delegate(
                url,
                {"request_id": "q-2", "version": 1, "topic": "정산", "draft": "완료"},
            )
        )
    assert good["state"] == "completed" and good["decision"] == "accepted"
    assert bad["state"] == "completed" and bad["decision"] == "held"


@pytest.mark.parametrize(
    "topic,contact,decision",
    [
        ("정산", "x", "accepted"),
        ("계정", "x", "accepted"),
        ("기타", "x", "ask"),
        ("정산", "", "ask"),
    ],
)
def test_integration_propagates_remote_policy(topic, contact, decision, monkeypatch):
    from course import integration

    real_server = server
    monkeypatch.setattr(
        integration,
        "server",
        lambda module, *args: real_server(
            "tests.a2a_server" if module == "course.a2a_lab" else module, *args
        ),
    )
    result = integration.run(topic, contact, model=ToolCallingStub())
    assert result["decision"] == decision
    if decision == "accepted":
        assert result["policy"]["policy"]["id"] in result["loop"]["draft"]
        assert result["review"]["artifact"]["passed"] is True


@pytest.mark.parametrize("lab", ["langchain", "graph", "harness", "mcp", "a2a"])
def test_extension_reference_and_starter(lab):
    from exercises import extension_solutions, extensions
    from exercises.extension_check import evaluate as extension_evaluate

    assert all(extension_evaluate(extension_solutions, lab))
    try:
        assert not all(extension_evaluate(extensions, lab))
    except KeyError:
        pass


def test_integration_holds_mismatched_policy(monkeypatch):
    from course import integration

    async def changed_policy(url, topic):
        data = {
            "found": True,
            "topic": topic,
            "policy": {"id": "P-03", "team": "변경팀", "rule": "새 규정"},
        }
        return {"result": {"structured_content": {"result": json.dumps(data)}}}

    monkeypatch.setattr(integration, "query", changed_policy)
    result = integration.run(model=ToolCallingStub())
    assert result["decision"] == "held"
    assert result["reason"] == "policy_snapshot_mismatch"


@pytest.mark.parametrize(
    "topic,expected", [("정산", "P-01"), ("계정", "P-02"), ("모름", "확인")]
)
def test_new_langchain_mcp_adapter(topic, expected):
    from course.mcp_agent_lab import run

    result = run(topic, model=ToolCallingStub())
    assert result["tools"] == ["lookup_policy"]
    assert [message["role"] for message in result["trace"]] == [
        "human",
        "ai",
        "tool",
        "ai",
    ]
    assert expected in result["trace"][-1]["content"]


def test_revision_passes_draft_and_feedback_to_model():
    from types import SimpleNamespace
    from course.harness_lab import revise_draft

    class Recorder:
        def invoke(self, prompt):
            self.prompt = prompt
            return SimpleNamespace(content="수정된 초안")

    model = Recorder()
    assert revise_draft("원래 초안", ["담당 팀 누락"], model=model) == "수정된 초안"
    assert all(value in model.prompt for value in ["원래 초안", "담당 팀 누락", "P-01"])


def test_model_connection_failure_is_not_replaced_with_success():
    from course.langchain_lab import run

    class UnavailableModel(ToolCallingStub):
        def _generate(self, *args, **kwargs):
            raise ConnectionError("unavailable")

    with pytest.raises(ConnectionError):
        run(model=UnavailableModel())


def test_natural_question_is_forwarded_without_topic_replacement():
    from course.langchain_lab import run

    question = "정산 문의와 계정 문의가 함께 있습니다."
    result = run(question=question, model=ToolCallingStub())
    assert result["trace"][0]["content"] == question


@pytest.mark.parametrize(
    "artifact",
    [
        {"request_id": "x", "version": True, "passed": True},
        {"request_id": "x", "version": "1", "passed": True},
        {"request_id": "x", "version": 1, "passed": "true"},
        None,
    ],
)
def test_a2a_rejects_ambiguous_artifact_types(artifact):
    assert accept_result("completed", artifact, "x", 1) == "held"
