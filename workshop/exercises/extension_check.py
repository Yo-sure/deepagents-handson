"""확장 계약 검사: python -m exercises.extension_check LAB [--solution]."""

import argparse
from course.common import POLICIES


def evaluate(module, lab):
    if lab == "langchain":
        policy = POLICIES["정산"]
        return [
            module.evidence_matches("재무지원팀 P-01", policy) is True,
            module.evidence_matches("재무지원팀 P-99", policy) is False,
            module.evidence_matches("재무지원팀 P-01 P-99", policy) is False,
        ]
    if lab == "graph":
        return [
            module.approval_matrix()
            == {"approve": "approved", "reject": "held", "": "held", "approv": "held"}
        ]
    if lab == "harness":
        result = module.refine_without_stall(
            "초안", "정산", lambda text, feedback: text, 3
        )
        good = module.refine_without_stall(
            "재무지원팀 P-01", "정산", lambda *_: "오류", 0
        )
        return [
            result["status"] == "stalled",
            len(result["history"]) == 2,
            good["status"] == "passed",
        ]
    if lab == "mcp":
        result = module.ticket_restart()
        return [
            result["first"]["data"]["created"] is True,
            result["again"]["data"]["created"] is False,
            result["first"]["data"]["ticket_id"]
            == result["again"]["data"]["ticket_id"],
            result["conflict"]["error"] is True,
        ]
    if lab == "a2a":
        artifact = {"request_id": "req-1", "version": 2, "passed": True}
        return [
            module.review_version("completed", artifact, "req-1", 2) == "accepted",
            module.review_version("completed", artifact, "req-1", 3) == "held",
            module.review_version("completed", artifact, "req-2", 2) == "held",
            module.review_version("working", None, "req-1", 2) == "pending",
            module.review_version("completed", None, "req-1", 2) == "held",
            module.review_version(
                "completed", {**artifact, "passed": "true"}, "req-1", 2
            )
            == "held",
            module.review_version(
                "completed", {**artifact, "version": True}, "req-1", 1
            )
            == "held",
            module.review_version("failed", artifact, "req-1", 2) == "held",
        ]
    raise ValueError(lab)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("lab", choices=["langchain", "graph", "harness", "mcp", "a2a"])
    parser.add_argument("--solution", action="store_true")
    args = parser.parse_args()
    from . import extensions, extension_solutions

    try:
        print(
            "기준 풀이의 반환값 검사 — 학생 구현의 통과를 의미하지 않습니다."
            if args.solution
            else "학생 구현의 반환값 검사"
        )
        results = evaluate(
            extension_solutions if args.solution else extensions, args.lab
        )
        labels = {
            "langchain": [
                "정상 ID와 담당 팀",
                "잘못된 ID 거부",
                "정상·오류 ID 혼합 거부",
            ],
            "graph": ["승인·거부·빈 입력·오타의 반환값 계약"],
            "harness": [
                "같은 실패 초안은 정체",
                "첫 수정 이후 두 번 검토",
                "처음부터 성공하면 수정하지 않음",
            ],
            "mcp": [
                "최초 요청은 신규 생성",
                "재시작 후 같은 요청은 재사용",
                "재시작 전후 동일 티켓",
                "같은 키에 다른 내용은 오류",
            ],
            "a2a": [
                "현재 요청과 버전은 수락",
                "지난 버전 보류",
                "다른 요청 보류",
                "진행 중은 대기",
                "산출물 누락 보류",
                "문자열 true는 보류",
                "불리언 버전은 보류",
                "실패 상태의 산출물 보류",
            ],
        }
        for label, ok in zip(labels[args.lab], results, strict=True):
            print(f"{'PASS' if ok else 'FAIL'} {label}")
        raise SystemExit(0 if all(results) else 1)
    except (KeyError, TypeError, ValueError) as error:
        if isinstance(error, KeyError):
            print(f"FAIL: 반환값에 필요한 항목이 없습니다: {error.args[0]}")
            if args.lab == "mcp":
                print(
                    "ticket_restart()의 반환값에 first, again, conflict가 필요합니다. 각 호출은 error와 data를 담습니다."
                )
        else:
            print(f"FAIL: 확장 반환 계약 확인 ({type(error).__name__})")
        raise SystemExit(1)
