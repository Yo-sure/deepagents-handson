"""실행: uv run python -m course.cli langchain --mode fixed"""
import argparse
import asyncio
import json
import tempfile
from pathlib import Path
from .common import ROOT, POLICIES


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("lab", choices=["langchain", "graph", "approval", "harness", "deepagent", "mcp", "a2a", "all"])
    parser.add_argument("--mode", choices=["fixed", "live"], default="fixed")
    parser.add_argument("--topic", default="정산")
    parser.add_argument("--contact", default="requester@example.test")
    parser.add_argument("--decision", default="approve")
    parser.add_argument("--revisions", type=int, default=2)
    args = parser.parse_args()
    from .langchain_lab import run
    from .graph_lab import build_graph, approval_demo
    from .harness_lab import bounded_refine, fixed_revision, run_deep_agent
    from .mcp_lab import query
    from .a2a_lab import delegate
    from .processes import server
    labs = [args.lab] if args.lab != "all" else ["langchain", "graph", "approval", "harness", "deepagent", "mcp", "a2a"]
    results = {}
    for lab in labs:
        if lab == "langchain":
            result = run(args.topic, args.mode)
        elif lab == "graph":
            result = build_graph().invoke({"topic": args.topic, "contact": args.contact})
        elif lab == "approval":
            result = approval_demo(args.decision)
        elif lab == "harness":
            result = bounded_refine("담당 팀을 확인합니다.", args.topic,
                                    lambda draft, feedback: fixed_revision(draft, feedback, args.topic), args.revisions)
            result["mode"] = "결정론 수정 함수. LLM 수정은 확장 과제입니다."
        elif lab == "deepagent":
            result = run_deep_agent(args.topic, args.mode)
        elif lab == "mcp":
            with tempfile.TemporaryDirectory() as temp, server("course.mcp_lab", "--db", Path(temp) / "tickets.sqlite") as url:
                result = asyncio.run(query(url + "/mcp", args.topic))
        else:
            with server("course.a2a_lab", "--mode", args.mode) as url:
                policy = POLICIES.get(args.topic)
                draft = f"{policy['rule']} [{policy['id']}]" if policy else "추가 확인이 필요합니다."
                result = asyncio.run(delegate(url, {"request_id": "inquiry-1", "version": 1, "topic": args.topic,
                    "draft": draft}))
        results[lab] = result
        print(json.dumps({lab: result}, ensure_ascii=False, indent=2))
    output = ROOT / "runs"
    output.mkdir(exist_ok=True)
    (output / f"{args.lab}-{args.mode}.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"결과: runs/{args.lab}-{args.mode}.json")


if __name__ == "__main__":
    main()
