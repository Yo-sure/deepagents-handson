"""학생이 작성한 함수를 검사합니다. 모델이나 외부 서버를 호출하지 않습니다."""

import json
from course.policy_store import load_policies


def check_lookup(lookup):
    policies = load_policies()
    for topic in ["정산", " 계정 ", "없는업무"]:
        data = json.loads(lookup(topic))
        name = topic.strip()
        expected = {
            "found": name in policies,
            "topic": name,
            "policy": policies.get(name),
        }
        assert data == expected, (
            f"{topic!r}: 조회 결과가 다릅니다. 기대={expected}, 실제={data}"
        )
        print(f"통과 | {topic!r} | found={data['found']}")


def check_graph(build_workflow, lookup):
    """생성/검토 함수만 고정해 분기와 노드 갱신을 검사합니다."""
    calls = []

    def generate(topic):
        calls.append(topic)
        return "검사용 초안"

    def review(draft, data, limit):
        return {"status": "passed", "draft": draft, "history": []}

    app = build_workflow(lookup, generate, review)
    cases = [
        ("계정", "user@example.test", []),
        ("계정", "", ["contact"]),
        ("계정", "   ", ["contact"]),
        ("없는업무", "user@example.test", ["topic"]),
        ("없는업무", "   ", ["topic", "contact"]),
    ]
    for topic, contact, missing in cases:
        calls.clear()
        result = app.invoke({"topic": topic, "contact": contact})
        label = f"topic={topic!r}, contact={contact!r}"
        expected_path = ["lookup", "ask"] if missing else ["lookup", "draft", "review"]
        assert result["visited"] == expected_path, (
            f"{label}: 방문 경로 {result['visited']}"
        )
        assert len(calls) == (0 if missing else 1), (
            f"{label}: 초안 생성 호출 {len(calls)}"
        )
        assert result["topic"] == topic and result["contact"] == contact, (
            f"{label}: 입력 State를 바꾸었습니다."
        )
        if missing:
            assert result.get("missing") == missing, (
                f"{label}: missing 기대={missing}, 실제={result.get('missing')}"
            )
            assert result["decision"] == "ask" and result["history"] == [], (
                f"{label}: ask의 판정·검토 기록을 확인하십시오."
            )
            assert isinstance(result["draft"], str) and result["draft"].strip(), (
                f"{label}: 질문 문장이 비었습니다."
            )
        print(f"통과 | {label} | {' → '.join(result['visited'])} | 생성 {len(calls)}회")
    print("질문 내용은 직접 읽고, 이미 아는 정보를 다시 묻지 않는지 확인하십시오.")


def check_accept_review(accept):
    good = {"request_id": "case-1", "version": 1, "passed": True}
    cases = [
        ("처리 중", "working", good, "case-1", 1, "pending"),
        ("접수됨", "submitted", None, "case-1", 1, "pending"),
        ("현재 초안 통과", "completed", good, "case-1", 1, "accepted"),
        ("옛 버전", "completed", good, "case-1", 2, "held"),
        ("다른 요청", "completed", good, "other", 1, "held"),
        ("검토 실패", "completed", {**good, "passed": False}, "case-1", 1, "held"),
        ("문자열 true", "completed", {**good, "passed": "true"}, "case-1", 1, "held"),
        ("산출물 누락", "completed", None, "case-1", 1, "held"),
        ("불리언 입력 버전", "completed", good, "case-1", True, "held"),
        (
            "불리언 결과 버전",
            "completed",
            {**good, "version": True},
            "case-1",
            1,
            "held",
        ),
        ("0 버전", "completed", {**good, "version": 0}, "case-1", 0, "held"),
        ("빈 요청 ID", "completed", {**good, "request_id": ""}, "", 1, "held"),
        ("작업 실패", "failed", good, "case-1", 1, "held"),
    ]
    for label, state, artifact, request_id, version, expected in cases:
        actual = accept(state, artifact, request_id, version)
        assert actual == expected, f"{label}: 기대={expected}, 실제={actual}"
        print(f"통과 | {label} | {actual}")
