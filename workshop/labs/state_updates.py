"""State 병합 규칙을 모델 호출 없이 비교합니다."""
from operator import add
from typing import Annotated, TypedDict
from langchain.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

class State(TypedDict):
    latest: list[str]
    history: Annotated[list[str], add]


def first(state):
    return {"latest": ["조회"], "history": ["조회"]}


def second(state):
    return {"latest": ["초안"], "history": ["초안"]}


graph = StateGraph(State)
graph.add_node("first", first)
graph.add_node("second", second)
graph.add_edge(START, "first")
graph.add_edge("first", "second")
graph.add_edge("second", END)
app = graph.compile()
print(app.invoke({"latest": [], "history": []}))

messages = [HumanMessage(content="계정 담당 팀은?", id="q1")]
messages = add_messages(messages, [AIMessage(content="확인 중입니다.", id="a1")])
messages = add_messages(messages, [AIMessage(content="IT지원팀입니다.", id="a1")])
print([(m.id, m.content) for m in messages])
