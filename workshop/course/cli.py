"""실행: uv run python -m course.cli langchain"""

import argparse
import asyncio
import json
import tempfile
from pathlib import Path
from .common import ROOT, POLICIES


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "lab",
        choices=[
            "langchain",
            "graph",
            "approval",
            "harness",
            "deepagent",
            "mcp",
            "a2a",
            "all",
        ],
    )
    parser.add_argument("--topic", default="정산")
    parser.add_argument("--question", help="LangChain 예제에 전달할 자연어 문의")
    parser.add_argument("--contact", default="requester@example.test")
    parser.add_argument("--decision", default="approve")
    parser.add_argument("--revisions", type=int, default=2)
    args = parser.parse_args()
    if args.question is not None and args.lab != "langchain":
        parser.error("--question은 langchain 실습에서 사용합니다.")
    from .langchain_lab import run
    from .graph_lab import build_graph, approval_demo
    from .harness_lab import bounded_refine, revise_draft, run_deep_agent
    from .mcp_lab import query
    from .a2a_lab import delegate
    from .processes import server

    labs = (
        [args.lab]
        if args.lab != "all"
        else ["langchain", "graph", "approval", "harness", "deepagent", "mcp", "a2a"]
    )
    results = {}
    for lab in labs:
        if lab == "langchain":
            result = (
                run(args.topic, question=args.question)
                if args.question is not None
                else run(args.topic)
            )
        elif lab == "graph":
            result = build_graph().invoke(
                {"topic": args.topic, "contact": args.contact}
            )
        elif lab == "approval":
            result = approval_demo(args.decision)
        elif lab == "harness":
            result = bounded_refine(
                "담당 팀을 확인합니다.",
                args.topic,
                lambda draft, feedback: revise_draft(draft, feedback, args.topic),
                args.revisions,
            )
        elif lab == "deepagent":
            result = run_deep_agent(args.topic)
        elif lab == "mcp":
            with (
                tempfile.TemporaryDirectory() as temp,
                server("course.mcp_lab", "--db", Path(temp) / "tickets.sqlite") as url,
            ):
                result = asyncio.run(query(url + "/mcp", args.topic))
        else:
            with server("course.a2a_lab") as url:
                policy = POLICIES.get(args.topic)
                draft = (
                    f"{policy['rule']} [{policy['id']}]"
                    if policy
                    else "추가 확인이 필요합니다."
                )
                result = asyncio.run(
                    delegate(
                        url,
                        {
                            "request_id": "inquiry-1",
                            "version": 1,
                            "topic": args.topic,
                            "draft": draft,
                        },
                    )
                )
        results[lab] = result
        print(json.dumps({lab: result}, ensure_ascii=False, indent=2))
    output = ROOT / "runs"
    output.mkdir(exist_ok=True)
    (output / f"{args.lab}.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"결과: runs/{args.lab}.json")


if __name__ == "__main__":
    main()
