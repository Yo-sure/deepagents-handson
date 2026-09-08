"""질문을 바꾸고 다시 실행하며 메시지 목록을 읽습니다."""
from build_lab.student import lookup_policy, build_agent
from course.common import get_model

question = "계정은 어느 팀에 문의하나요?"
agent = build_agent(get_model(), lookup_policy)
result = agent.invoke({"messages": [{"role": "user", "content": question}]})
for index, message in enumerate(result["messages"]):
    print(f"\nmessages[{index}] · {type(message).__name__}")
    print(message.content)
    if getattr(message, "tool_calls", None):
        print("tool_calls:", message.tool_calls)
    if getattr(message, "tool_call_id", None):
        print("tool_call_id:", message.tool_call_id)
