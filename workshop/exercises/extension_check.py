"""확장 계약 검사: python -m exercises.extension_check LAB [--solution]."""
import argparse
from course.common import POLICIES


def evaluate(module, lab):
    if lab == "langchain":
        policy = POLICIES["정산"]
        return [module.evidence_matches("재무지원팀 P-01", policy) is True,
                module.evidence_matches("재무지원팀 P-99", policy) is False,
                module.evidence_matches("재무지원팀 P-01 P-99", policy) is False]
    if lab == "graph":
        return [module.approval_matrix() == {"approve": "approved", "reject": "held", "": "held", "approv": "held"}]
    if lab == "harness":
        result = module.refine_without_stall("초안", "정산", lambda text, feedback: text, 3)
        good = module.refine_without_stall("재무지원팀 P-01", "정산", lambda *_: "오류", 0)
        return [result["status"] == "stalled", len(result["history"]) == 2, good["status"] == "passed"]
    if lab == "mcp":
        result = module.ticket_restart()
        return [result["first"]["data"]["created"] is True,
                result["again"]["data"]["created"] is False,
                result["first"]["data"]["ticket_id"] == result["again"]["data"]["ticket_id"],
                result["conflict"]["error"] is True]
    if lab == "a2a":
        artifact = {"request_id": "req-1", "version": 2, "passed": True}
        return [module.review_version("completed", artifact, "req-1", 2) == "accepted",
                module.review_version("completed", artifact, "req-1", 3) == "held",
                module.review_version("completed", artifact, "req-2", 2) == "held",
                module.review_version("working", None, "req-1", 2) == "pending"]
    raise ValueError(lab)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("lab", choices=["langchain", "graph", "harness", "mcp", "a2a"])
    parser.add_argument("--solution", action="store_true")
    args = parser.parse_args()
    from . import extensions, extension_solutions
    try:
        results = evaluate(extension_solutions if args.solution else extensions, args.lab)
        print(["PASS" if ok else "FAIL" for ok in results])
        raise SystemExit(0 if all(results) else 1)
    except (KeyError, TypeError, ValueError) as error:
        print(f"FAIL: 확장 반환 계약 확인 ({type(error).__name__})")
        raise SystemExit(1)
