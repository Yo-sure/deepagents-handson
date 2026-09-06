"""모듈 3: 검토 피드백과 제한된 수정. 검증기는 학습용 규칙입니다."""
from collections.abc import Callable
from .common import POLICIES, ROOT, get_model, lookup_policy, trace_messages


def verify(text: str, topic: str) -> list[str]:
    policy = POLICIES.get(topic)
    if not policy:
        return ["등록된 정책이 없습니다. 추가 확인이 필요합니다."]
    errors = []
    if policy["id"] not in text:
        errors.append(f"근거 ID {policy['id']}가 없습니다.")
    if policy["team"] not in text:
        errors.append(f"담당 팀 {policy['team']}가 없습니다.")
    return errors


#pragma region loop
def bounded_refine(draft: str, topic: str, revise: Callable, max_revisions: int = 2) -> dict:
    if not 0 <= max_revisions <= 5:
        raise ValueError("수정 상한은 0~5입니다.")
    history = []
    for attempt in range(max_revisions + 1):
        feedback = verify(draft, topic)
        history.append({"attempt": attempt, "draft": draft, "feedback": feedback})
        if not feedback:
            return {"status": "passed", "draft": draft, "history": history}
        if attempt == max_revisions:
            return {"status": "held", "draft": draft, "history": history}
        draft = revise(draft, feedback)
    raise AssertionError("도달하지 않는 경로")
#pragma endregion loop


def fixed_revision(draft, feedback, topic="정산"):
    policy = POLICIES.get(topic)
    if policy is None:
        return "등록된 정책이 없어 추가 확인이 필요합니다."
    return f"{policy['rule']} [근거: {policy['id']}]"


#pragma region deepagent
def run_deep_agent(topic="정산", mode="fixed"):
    import json
    from deepagents import create_deep_agent
    from deepagents.backends import FilesystemBackend
    agent = create_deep_agent(
        model=get_model(mode), tools=[lookup_policy],
        backend=FilesystemBackend(root_dir=str(ROOT / "skills"), virtual_mode=True),
        skills=["/"],
        system_prompt="업무 규정 조회 Agent입니다. 해당 skill의 지침에 따라 근거 ID와 담당 팀을 답하십시오. "
                      "정책 확인에는 lookup_policy를 사용하십시오. 파일을 수정하지 마십시오.",
    )
    result = agent.invoke({"messages": [{"role": "user", "content": json.dumps({"topic": topic}, ensure_ascii=False)}]},
                          config={"recursion_limit": 20})
    return {"mode": mode, "trace": trace_messages(result["messages"]),
            "skill_mode": "fixed 모델은 Skill 선택을 판단하지 않습니다." if mode == "fixed" else "live 선택 기록을 확인하십시오."}
#pragma endregion deepagent
