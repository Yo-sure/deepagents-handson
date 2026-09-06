"""개인 과제 기준 풀이. 유일한 정답 코드 형태를 의미하지 않습니다."""


def answer_from_policy(data):
    policy = data.get("policy")
    if not data.get("found") or not policy:
        return "등록된 규정이 없어 추가 확인이 필요합니다."
    return f"{policy['team']}에 문의합니다. [근거: {policy['id']}]"


def route_inquiry(state):
    return "draft" if state.get("policy_id") and state.get("contact") else "ask"


def loop_action(passed, revisions, limit):
    if passed:
        return "finish"
    return "hold" if revisions >= limit else "revise"


def team_for_topic(topic, policies):
    policy = policies.get(topic)
    return {"found": bool(policy), "team": policy["team"] if policy else None}


def review_decision(state, artifact):
    if state in {"working", "submitted"}:
        return "pending"
    if state != "completed" or not artifact or artifact.get("passed") is not True:
        return "held"
    return "accepted"
