"""구현에 필요한 데이터·상태·검토 기준. 모델 응답을 대신하지 않습니다."""

import re
from typing import TypedDict
from course.common import POLICIES, get_model, trace_messages

# 기존 개발용 실행기의 공개 재료 인터페이스입니다.
__all__ = ["POLICIES", "get_model", "trace_messages", "Inquiry", "inspect_draft"]


class Inquiry(TypedDict, total=False):
    topic: str
    contact: str
    data: dict
    draft: str
    decision: str
    history: list[dict]
    visited: list[str]
    missing: list[str]


def inspect_draft(text, data):
    policy = data.get("policy")
    if not data.get("found") or not policy:
        return ["등록된 정책이 없습니다."]
    issues = []
    if set(re.findall(r"P-\d+", text)) != {policy["id"]}:
        issues.append("근거 ID를 조회 결과와 일치시키십시오.")
    if policy["team"] not in text:
        issues.append("담당 팀을 포함하십시오.")
    return issues
