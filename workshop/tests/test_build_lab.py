"""반환 표가 아니라 학생의 도구·컴파일된 그래프·실행 경로를 검사합니다."""

import asyncio
import json
import pytest
from langgraph.graph.state import CompiledStateGraph
from build_lab.materials import inspect_draft


@pytest.fixture
def impl(request):
    if request.config.getoption("--build-student"):
        from build_lab import student

        return student
    from build_lab import reference

    return reference


@pytest.mark.parametrize(
    "topic,expected",
    [("정산", "P-01"), (" 계정 ", "P-02"), ("없는업무", None), ("", None)],
)
def test_lookup(impl, topic, expected):
    data = json.loads(impl.lookup_policy(topic))
    assert data["topic"] == topic.strip()
    assert data["found"] is (expected is not None)
    assert (data["policy"]["id"] if data["policy"] else None) == expected


def test_agent(impl):
    from tests.model_stub import ToolCallingStub

    agent = impl.build_agent(ToolCallingStub(), impl.lookup_policy)
    messages = agent.invoke(
        {"messages": [{"role": "user", "content": '{"topic":"계정"}'}]}
    )["messages"]
    assert any(m.type == "tool" for m in messages)
    assert "P-02" in messages[-1].content


@pytest.mark.parametrize(
    "topic,contact,expected",
    [("계정", "user", "passed"), ("정산", "   ", "ask"), ("없는업무", "user", "ask")],
)
def test_graph(impl, topic, contact, expected):
    calls = []

    def generate(topic):
        calls.append("generate")
        return "IT지원팀 P-02"

    def refine(draft, data, limit):
        calls.append("refine")
        return {
            "draft": draft,
            "status": "passed",
            "history": [{"attempt": 0, "draft": draft, "feedback": []}],
        }

    graph = impl.build_workflow(impl.lookup_policy, generate, refine)
    assert isinstance(graph, CompiledStateGraph)
    result = graph.invoke({"topic": topic, "contact": contact})
    assert result["decision"] == expected
    assert calls == (["generate", "refine"] if expected == "passed" else [])
    assert result["visited"] == (
        ["lookup", "draft", "review"] if expected == "passed" else ["lookup", "ask"]
    )


@pytest.mark.parametrize(
    "kind,limit,status,count",
    [
        ("good", 0, "passed", 0),
        ("bad", 0, "held", 0),
        ("same", 3, "stalled", 1),
        ("repair", 1, "passed", 1),
        ("change", 2, "held", 2),
    ],
)
def test_loop(impl, kind, limit, status, count):
    data = json.loads(impl.lookup_policy("정산"))
    calls = []

    def revise(text, feedback):
        assert feedback == inspect_draft(text, data)
        calls.append(text)
        return (
            "재무지원팀 P-01"
            if kind == "repair"
            else text + "!"
            if kind == "change"
            else text
        )

    first = "재무지원팀 P-01" if kind == "good" else "초안"
    result = impl.refine_answer(first, data, revise, limit)
    assert result["status"] == status
    assert len(calls) == count
    assert len(result["history"]) == count + 1
    assert result["history"][0]["draft"] == first
    assert result["draft"] == result["history"][-1]["draft"]
    for entry in result["history"]:
        assert entry["feedback"] == inspect_draft(entry["draft"], data)


@pytest.mark.parametrize("limit", [-1, 6, True])
def test_loop_invalid_limit(impl, limit):
    with pytest.raises(ValueError):
        impl.refine_answer("초안", {}, lambda *_: "", limit)


def test_mcp(impl):
    from mcp.client import Client
    from course.mcp_lab import PROTOCOL

    async def check():
        async with Client(
            impl.build_mcp_server(impl.lookup_policy), mode=PROTOCOL
        ) as client:
            tools = await client.list_tools()
            assert "lookup_policy" in [tool.name for tool in tools.tools]
            result = await client.call_tool("lookup_policy", {"topic": "계정"})
            assert not result.is_error
            assert json.loads(result.content[0].text)["policy"]["id"] == "P-02"

    asyncio.run(check())


@pytest.mark.parametrize(
    "state,artifact,expected",
    [
        ("working", None, "pending"),
        ("failed", None, "held"),
        ("completed", {"request_id": "r1", "version": 2, "passed": True}, "accepted"),
        ("completed", {"request_id": "r1", "version": 1, "passed": True}, "held"),
        ("completed", {"request_id": "r2", "version": 2, "passed": True}, "held"),
        ("completed", {"request_id": "r1", "version": 2, "passed": "true"}, "held"),
    ],
)
def test_a2a(impl, state, artifact, expected):
    assert impl.accept_review(state, artifact, "r1", 2) == expected


@pytest.mark.parametrize(
    "request_id,version,artifact",
    [
        ("", 2, {"request_id": "", "version": 2, "passed": True}),
        ("r1", True, {"request_id": "r1", "version": True, "passed": True}),
        ("r1", 0, {"request_id": "r1", "version": 0, "passed": True}),
        ("r1", 2, {"request_id": "r1", "version": "2", "passed": True}),
        ("r1", 2, None),
    ],
)
def test_a2a_invalid_contract(impl, request_id, version, artifact):
    assert impl.accept_review("completed", artifact, request_id, version) == "held"
