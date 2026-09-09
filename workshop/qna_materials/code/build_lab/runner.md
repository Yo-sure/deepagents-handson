원본: build_lab/runner.py

```python
"""실제 모델·서버 연결과 출력 저장을 담당하는 제공 실행기입니다."""

import argparse
import asyncio
import json
import uuid
from course.common import ROOT, get_model, trace_messages
from course.processes import server
from .materials import inspect_draft


def run(
    impl,
    stage="workflow",
    topic="정산",
    contact="user@example.test",
    limit=2,
    model=None,
):
    remote = stage in {"mcp", "complete"}
    if remote:
        from course.mcp_lab import query

        with server("build_lab.serve", "--implementation", impl.__name__) as url:
            wire = asyncio.run(query(url + "/mcp", topic))
        data = json.loads(wire["result"]["content"][0]["text"])
        if stage == "mcp":
            return {"transport": wire, "data": data}
        snapshot_topics = {topic.strip(), data["topic"]}

        def lookup_policy(topic: str) -> str:
            """Read the policy snapshot fetched from the student's MCP server."""
            return json.dumps(
                data
                if topic.strip() in snapshot_topics
                else {"found": False, "topic": topic, "policy": None},
                ensure_ascii=False,
            )

        lookup = lookup_policy
    else:
        lookup = impl.lookup_policy
    traces = []

    def generate(topic):
        nonlocal model
        if model is None:
            model = get_model()
        agent = impl.build_agent(model, lookup)
        result = agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": json.dumps({"topic": topic}, ensure_ascii=False),
                    }
                ]
            },
            config={"recursion_limit": 12},
        )
        traces.extend(trace_messages(result["messages"]))
        return result["messages"][-1].content

    def revise(draft, feedback):
        response = model.invoke(
            "조회 규정을 근거로 한국어 초안을 수정하십시오.\n"
            + json.dumps(
                {
                    "policy": json.loads(lookup(topic)),
                    "draft": draft,
                    "feedback": feedback,
                },
                ensure_ascii=False,
            )
        )
        return response.content

    def refine(draft, data, limit):
        if stage == "graph":
            issues = inspect_draft(draft, data)
            return {
                "status": "held" if issues else "passed",
                "draft": draft,
                "history": [{"attempt": 0, "draft": draft, "feedback": issues}],
            }
        return impl.refine_answer(draft, data, revise, limit)

    if stage == "agent":
        return {"draft": generate(topic), "trace": traces}
    graph = impl.build_workflow(lookup, generate, refine, limit)
    state = graph.invoke({"topic": topic, "contact": contact})
    result = {"state": state, "trace": traces}
    if stage == "complete" and state["decision"] == "passed":
        from course.a2a_lab import delegate

        payload = {
            "topic": state["data"]["topic"],
            "draft": state["draft"],
            "request_id": str(uuid.uuid4()),
            "version": 1,
        }
        with server("course.a2a_lab") as url:
            review = asyncio.run(delegate(url, payload))
        # SDK 수신은 제공 코드, 최종 수용 결정은 학생 코드가 담당합니다.
        review["decision"] = impl.accept_review(
            review["state"],
            review["artifact"],
            payload["request_id"],
            payload["version"],
        )
        result["review"] = review
    return result


def main(impl=None):
    if impl is None:
        from . import student as impl
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "stage", choices=["agent", "graph", "workflow", "mcp", "complete"]
    )
    parser.add_argument("--topic", default="정산")
    parser.add_argument("--contact", default="user@example.test")
    parser.add_argument("--limit", type=int, choices=range(6), default=2)
    args = parser.parse_args()
    try:
        output = run(impl, args.stage, args.topic, args.contact, args.limit)
    except NotImplementedError as error:
        parser.exit(1, str(error) + "\n")
    target = (
        ROOT / "runs" / ("build-" + args.stage + "-" + uuid.uuid4().hex[:8] + ".json")
    )
    target.parent.mkdir(exist_ok=True)
    target.write_text(
        json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(target.read_text(encoding="utf-8"))
    print(f"기록: {target}")


if __name__ == "__main__":
    main()

```
