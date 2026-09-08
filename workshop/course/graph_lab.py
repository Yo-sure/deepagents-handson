"""모듈 2: State를 갱신하고 정보가 부족하면 질문으로 분기합니다."""
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command
from .common import POLICIES


#pragma region state
class InquiryState(TypedDict, total=False):
    topic: str
    contact: str
    policy_id: str
    answer: str
    decision: str
    visited: list[str]
#pragma endregion state


#pragma region lookup
def lookup(state: InquiryState) -> dict:
    policy = POLICIES.get(state["topic"])
    return {"policy_id": policy["id"] if policy else "", "visited": ["lookup"]}
#pragma endregion lookup


#pragma region route
def route(state: InquiryState) -> str:
    return "draft" if state.get("contact") and state.get("policy_id") else "ask"
#pragma endregion route


#pragma region draft
def draft(state):
    return {"answer": POLICIES[state["topic"]]["rule"], "decision": "draft",
            "visited": state["visited"] + ["draft"]}
#pragma endregion draft


#pragma region ask
def ask(state):
    return {"answer": "업무 주제와 회신 대상을 확인해 주세요.", "decision": "ask",
            "visited": state["visited"] + ["ask"]}
#pragma endregion ask


#pragma region graph
def build_graph(router=route, lookup_node=lookup, draft_node=draft):
    graph = StateGraph(InquiryState)
    graph.add_node("lookup", lookup_node)
    graph.add_node("draft", draft_node)
    graph.add_node("ask", ask)
    graph.add_edge(START, "lookup")
    graph.add_conditional_edges("lookup", router, {"draft": "draft", "ask": "ask"})
    graph.add_edge("draft", END)
    graph.add_edge("ask", END)
    return graph.compile()
#pragma endregion graph


#pragma region approval
#pragma region review
def review(state):
    decision = interrupt({"proposal": state["answer"], "choices": ["approve", "reject"]})
    return {"decision": "approved" if decision == "approve" else "held"}
#pragma endregion review


def approval_demo(decision="approve"):
    graph = StateGraph(InquiryState)
    graph.add_node("review", review)
    graph.add_edge(START, "review")
    graph.add_edge("review", END)
    app = graph.compile(checkpointer=InMemorySaver())
    config = {"configurable": {"thread_id": "approval-example"}}
    paused = app.invoke({"answer": "재무지원팀에 정산 문의를 전달합니다."}, config)
    resumed = app.invoke(Command(resume=decision), config)
    return {"paused": bool(paused.get("__interrupt__")), "decision": resumed["decision"],
            "storage": "같은 프로세스의 메모리. 프로세스 재시작 복구가 아닙니다."}
#pragma endregion approval
