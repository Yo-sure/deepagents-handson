"""의도적으로 부족한 초기 구현입니다. 각 함수는 독립적인 개인 과제입니다.

문제와 입력·출력 계약은 교재에 있습니다. 아래 다섯 함수를 한꺼번에 고치지 않습니다.
"""


#pragma region langchain
def answer_from_policy(data: dict) -> str:
    """조회 실패에도 완료라고 답하는 초기 구현을 고칩니다."""
    return "확인 완료"
#pragma endregion langchain


#pragma region graph
def route_inquiry(state: dict) -> str:
    """정책만 있고 회신 대상은 없어도 draft로 가는 초기 구현입니다."""
    return "draft" if state.get("policy_id") else "ask"
#pragma endregion graph


#pragma region loop
def loop_action(passed: bool, revisions: int, limit: int) -> str:
    """검토 성공과 수정 상한을 구분하지 않는 초기 구현입니다."""
    return "revise"
#pragma endregion loop


#pragma region mcp
def team_for_topic(topic: str, policies: dict) -> dict:
    """입력 주제와 관계없이 첫 정책의 팀을 돌려주는 초기 구현입니다."""
    policy = next(iter(policies.values()))
    return {"found": True, "team": policy["team"]}
#pragma endregion mcp


#pragma region a2a
def review_decision(state: str, artifact: dict | None) -> str:
    """접수·진행을 완료로 오인하는 초기 구현입니다."""
    return "accepted"
#pragma endregion a2a
