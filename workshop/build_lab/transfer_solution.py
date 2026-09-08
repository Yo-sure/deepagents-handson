"""독립 변경 과제의 풀이. 학생 결과를 기록한 뒤 비교합니다."""

import json
from .materials import POLICIES
from .reference import (
    build_agent,
    route_inquiry,
    build_workflow,
    refine_answer,
    build_mcp_server,
    accept_review,
)


def lookup_policy(topic: str) -> str:
    """Look up a policy by topic; 로그인 means 계정 and 비용 means 정산."""
    cleaned = topic.strip()
    canonical = {"로그인": "계정", "비용": "정산"}.get(cleaned, cleaned)
    policy = POLICIES.get(canonical)
    return json.dumps(
        {"found": policy is not None, "topic": canonical, "policy": policy},
        ensure_ascii=False,
    )


if __name__ == "__main__":
    from .runner import main
    from . import transfer_solution

    main(transfer_solution)

# 개발용 runner가 모듈의 구현 함수들을 호출합니다.
__all__ = [
    "lookup_policy",
    "build_agent",
    "route_inquiry",
    "build_workflow",
    "refine_answer",
    "build_mcp_server",
    "accept_review",
]
