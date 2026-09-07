"""모듈 1: 모델의 요청과 실제 도구 실행을 구분합니다."""
import json
from langchain.agents import create_agent
from .common import get_model, lookup_policy, trace_messages


#pragma region agent
def run(topic: str = "정산", policy_tool=lookup_policy, *, model=None, question: str | None = None) -> dict:
    model = model if model is not None else get_model()
    agent = create_agent(
        model=model,
        tools=[policy_tool],
        system_prompt="입력의 topic 또는 자연어 문의에 필요한 사내 규정을 도구로 확인하십시오. "
                      "여러 업무가 포함되면 각각 조회하십시오. 도구의 topic은 짧은 업무명이며 "
                      "등록된 예시는 정산과 계정입니다. 조회하지 않은 근거를 만들지 마십시오. "
                      "규정이 있으면 담당 팀과 근거 ID를 답하고, 없으면 확인 필요라고 답하십시오.",
    )
    result = agent.invoke(
        {"messages": [{
            "role": "user",
            "content": question if question is not None else json.dumps({"topic": topic}, ensure_ascii=False),
        }]},
        config={"recursion_limit": 12},
    )
    return {"trace": trace_messages(result["messages"])}
#pragma endregion agent
