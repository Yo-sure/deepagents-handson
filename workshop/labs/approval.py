"""중단된 초안을 읽고 터미널에서 승인 또는 거절합니다. 모델 호출은 없습니다."""
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command
from course.graph_lab import InquiryState, review

#pragma region setup
graph = StateGraph(InquiryState)
graph.add_node("review", review)
graph.add_edge(START, "review")
graph.add_edge("review", END)
app = graph.compile(checkpointer=InMemorySaver())
config = {"configurable": {"thread_id": "approval-example"}}
#pragma endregion setup

#pragma region pause
paused = app.invoke({"answer": "재무지원팀에 정산 문의를 전달합니다."}, config)
print("승인 요청:", paused["__interrupt__"][0].value)
print("중단 중:", bool(paused.get("__interrupt__")))
#pragma endregion pause

#pragma region resume
decision = input("approve 또는 reject를 입력하세요: ").strip()
while decision not in {"approve", "reject"}:
    decision = input("approve 또는 reject만 입력하세요: ").strip()
resumed = app.invoke(Command(resume=decision), config)
print("결정:", resumed["decision"])
print("남은 실행:", app.get_state(config).next)
#pragma endregion resume
