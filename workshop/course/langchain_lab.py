"""모듈 1: 모델의 요청과 실제 도구 실행을 구분합니다."""
import json
from langchain.agents import create_agent
from .common import get_model, lookup_policy, trace_messages


#pragma region agent
def run(topic: str = "정산", mode: str = "fixed", policy_tool=lookup_policy) -> dict:
    model = get_model(mode)
    agent = create_agent(
        model=model,
        tools=[policy_tool],
        system_prompt="입력의 topic에 해당하는 사내 규정을 도구로 확인하십시오. "
                      "규정이 있으면 담당 팀과 근거 ID를 답하고, 없으면 확인 필요라고 답하십시오.",
    )
    result = agent.invoke(
        {"messages": [{"role": "user", "content": json.dumps({"topic": topic}, ensure_ascii=False)}]},
        config={"recursion_limit": 12},
    )
    return {"mode": mode, "trace": trace_messages(result["messages"])}
#pragma endregion agent
