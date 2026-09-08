"""학생 구현과 기준 풀이의 동작 계약을 검사합니다."""

import argparse
import asyncio
import json
from course.common import POLICIES, lookup_policy
from course.graph_lab import build_graph


def evaluate(module, lab):
    checks = []

    def check(label, fn):
        try:
            ok = bool(fn())
            checks.append((label, ok, ""))
        except Exception as error:
            checks.append((label, False, type(error).__name__))

    if lab == "langchain":
        check(
            "조회 성공: 팀과 근거",
            lambda: all(
                s in module.answer_from_policy(json.loads(lookup_policy("정산")))
                for s in ["재무지원팀", "P-01"]
            ),
        )
        check(
            "없는 규정: 추가 확인",
            lambda: (
                "확인"
                in module.answer_from_policy(json.loads(lookup_policy("없는업무")))
                and "완료"
                not in module.answer_from_policy(json.loads(lookup_policy("없는업무")))
            ),
        )
        check(
            "다른 정책도 일반화",
            lambda: (
                "P-02" in module.answer_from_policy(json.loads(lookup_policy("계정")))
            ),
        )
    elif lab == "graph":
        for topic, contact, expected in [
            ("정산", "user", "draft"),
            ("정산", "", "ask"),
            ("없음", "user", "ask"),
        ]:
            check(
                f"{topic}/{contact or '회신대상없음'} → {expected}",
                lambda t=topic, c=contact, e=expected: (
                    build_graph(module.route_inquiry).invoke(
                        {"topic": t, "contact": c}
                    )["decision"]
                    == e
                ),
            )
    elif lab == "harness":
        for passed, count, limit, expected in [
            (True, 0, 2, "finish"),
            (False, 0, 2, "revise"),
            (False, 2, 2, "hold"),
            (True, 2, 2, "finish"),
            (False, 0, 0, "hold"),
        ]:
            check(
                f"pass={passed}, 수정={count}/{limit} → {expected}",
                lambda p=passed, c=count, l=limit, e=expected: (
                    module.loop_action(p, c, l) == e
                ),
            )
    elif lab == "mcp":
        from mcp.server.mcpserver import MCPServer
        from mcp.client import Client
        from course.mcp_lab import PROTOCOL

        server = MCPServer("학생 도구 검사")

        @server.tool()
        def team(topic: str) -> dict:
            """Find the responsible team for the given topic."""
            return module.team_for_topic(topic, POLICIES)

        async def call(topic):
            async with Client(server, mode=PROTOCOL) as client:
                result = await client.call_tool("team", {"topic": topic})
                return json.loads(result.content[0].text)

        for topic, expected in [
            ("정산", "재무지원팀"),
            ("계정", "IT지원팀"),
            ("없음", None),
        ]:
            check(
                f"MCP 호출: {topic}",
                lambda t=topic, e=expected: (
                    asyncio.run(call(t)) == {"found": e is not None, "team": e}
                ),
            )
    elif lab == "a2a":
        for state, artifact, expected in [
            ("submitted", None, "pending"),
            ("working", None, "pending"),
            ("completed", {"passed": True}, "accepted"),
            ("failed", None, "held"),
            ("completed", None, "held"),
            ("completed", {"passed": False}, "held"),
            ("completed", {"passed": "false"}, "held"),
            ("completed", {"passed": "true"}, "held"),
        ]:
            check(
                f"{state}/{artifact} → {expected}",
                lambda s=state, a=artifact, e=expected: (
                    module.review_decision(s, a) == e
                ),
            )
    return checks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("lab", choices=["langchain", "graph", "harness", "mcp", "a2a"])
    parser.add_argument("--solution", action="store_true")
    args = parser.parse_args()
    from . import solutions, student

    checks = evaluate(solutions if args.solution else student, args.lab)
    print(
        "기준 풀이 검사"
        if args.solution
        else "학생 코드 검사 (초기에는 실패가 정상입니다.)"
    )
    for label, ok, error in checks:
        print(f"{'PASS' if ok else 'FAIL'} {label} {error}")
    raise SystemExit(0 if checks and all(ok for _, ok, _ in checks) else 1)


if __name__ == "__main__":
    main()
