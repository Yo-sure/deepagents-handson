원본: build_lab/reference.py

```python
"""풀이 시간에 읽는 구현. 학생 파일과 별개입니다."""

import json
from langchain.agents import create_agent
from langchain.tools import tool
from langgraph.graph import StateGraph, START, END
from mcp.server.mcpserver import MCPServer
from course.policy_store import search_policy
from .materials import Inquiry, inspect_draft


def lookup_policy(topic: str) -> str:
    """Look up the current internal policy by topic, such as 정산 or 계정."""
    return search_policy(topic)


def build_agent(model, policy_tool):
    return create_agent(
        model=model,
        tools=[tool(policy_tool)],
        system_prompt="사내 문의에 답하기 전에 lookup_policy로 규정을 확인하십시오. "
        "topic은 정산, 계정 같은 업무명입니다. 등록된 담당 팀과 근거 ID를 답하십시오. "
        "정책이 없으면 추가 확인을 요청하고 근거를 만들지 마십시오.",
    )


def route_inquiry(state):
    return (
        "draft"
        if state["data"]["found"] and state.get("contact", "").strip()
        else "ask"
    )


def ask_for_details(state):
    missing = []
    labels = []
    if not state["data"]["found"]:
        missing.append("topic")
        labels.append("업무 주제")
    if not state.get("contact", "").strip():
        missing.append("contact")
        labels.append("회신 대상")
    return {
        "missing": missing,
        "decision": "ask",
        "draft": " · ".join(labels) + "을 확인해 주세요.",
        "history": [],
        "visited": state["visited"] + ["ask"],
    }


def build_workflow(lookup, generate, refine, limit=2):
    def read(state):
        return {"data": json.loads(lookup(state["topic"])), "visited": ["lookup"]}

    def route(state):
        return route_inquiry(state)

    def ask(state):
        return ask_for_details(state)

    def draft(state):
        return {
            "draft": generate(state["topic"]),
            "visited": state["visited"] + ["draft"],
        }

    def review(state):
        result = refine(state["draft"], state["data"], limit)
        return {
            "draft": result["draft"],
            "history": result["history"],
            "decision": result["status"],
            "visited": state["visited"] + ["review"],
        }

    graph = StateGraph(Inquiry)
    for name, node in [
        ("lookup", read),
        ("ask", ask),
        ("draft", draft),
        ("review", review),
    ]:
        graph.add_node(name, node)
    graph.add_edge(START, "lookup")
    graph.add_conditional_edges("lookup", route, {"ask": "ask", "draft": "draft"})
    graph.add_edge("ask", END)
    graph.add_edge("draft", "review")
    graph.add_edge("review", END)
    return graph.compile()


def refine_answer(draft, data, revise, limit=2):
    if type(limit) is not int or not 0 <= limit <= 5:
        raise ValueError("수정 상한은 0~5 정수입니다.")
    history = []
    for attempt in range(limit + 1):
        feedback = inspect_draft(draft, data)
        history.append({"attempt": attempt, "draft": draft, "feedback": feedback})
        if not feedback:
            return {"status": "passed", "draft": draft, "history": history}
        if len(history) > 1 and history[-2]["draft"] == draft:
            return {"status": "stalled", "draft": draft, "history": history}
        if attempt == limit:
            return {"status": "held", "draft": draft, "history": history}
        draft = revise(draft, feedback)


def build_mcp_server(policy_tool):
    app = MCPServer("직접 만든 정책 도구")
    app.tool()(policy_tool)
    return app


def accept_review(state, artifact, request_id, version):
    if state in {"submitted", "working"}:
        return "pending"
    if state != "completed" or not isinstance(artifact, dict):
        return "held"
    if not isinstance(request_id, str) or not request_id.strip():
        return "held"
    if (
        type(version) is not int
        or version < 1
        or type(artifact.get("version")) is not int
    ):
        return "held"
    if artifact.get("request_id") != request_id or artifact.get("version") != version:
        return "held"
    return "accepted" if artifact.get("passed") is True else "held"


if __name__ == "__main__":
    from .runner import main
    from . import reference

    main(reference)

```
