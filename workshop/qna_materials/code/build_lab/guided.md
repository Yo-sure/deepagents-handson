원본: build_lab/guided.py

```python
"""공통 과정에서 읽고 활용하는 실행 구조. 전체 재구현은 선택 심화입니다."""

import json
from langgraph.graph import StateGraph, START, END
from .materials import Inquiry, inspect_draft


def build_workflow(lookup, generate, refine, limit=2, router=None, ask_node=None):
    def read(state):
        return {"data": json.loads(lookup(state["topic"])), "visited": ["lookup"]}

    def default_route(state):
        return (
            "draft"
            if state["data"]["found"] and state.get("contact", "").strip()
            else "ask"
        )

    def default_ask(state):
        return {
            "decision": "ask",
            "draft": "업무 주제와 회신 대상을 확인해 주세요.",
            "history": [],
            "visited": state["visited"] + ["ask"],
        }

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
    # 노트북에서 전달한 분기 함수와 질문 노드를 직접 연결합니다.
    question_node = ask_node if ask_node is not None else default_ask
    route_after_lookup = router if router is not None else default_route
    graph.add_node("lookup", read)
    graph.add_node("ask", question_node)
    graph.add_node("draft", draft)
    graph.add_node("review", review)
    graph.add_edge(START, "lookup")
    graph.add_conditional_edges(
        "lookup", route_after_lookup, {"ask": "ask", "draft": "draft"}
    )
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

```
