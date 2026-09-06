"""MCP 조회 결과를 그래프·초안·검증·A2A 검토에 전달하는 통합 예제입니다."""
import argparse
import asyncio
import json
import tempfile
import uuid
from pathlib import Path
from .common import ROOT, POLICIES, get_model
from .mcp_lab import query
from .a2a_lab import delegate
from .graph_lab import build_graph
from .langchain_lab import run as draft_answer
from .harness_lab import bounded_refine
from .processes import server


def run(topic="정산", contact="requester@example.test", mode="fixed"):
    with tempfile.TemporaryDirectory() as temp:
        with server("course.mcp_lab", "--db", Path(temp) / "tickets.sqlite") as url:
            remote = asyncio.run(query(url + "/mcp", topic))
    policy_data = json.loads(remote["result"]["structured_content"]["result"])
    policy = policy_data["policy"]

    # 현재 검토 서버는 배포에 포함된 정책 fixture로 검사합니다.
    # 원격 조회 정책과 검토 기준이 다르면 같은 기준인 것처럼 진행하지 않습니다.
    if policy != POLICIES.get(topic):
        return {"mode": mode, "policy": policy_data, "decision": "held",
                "reason": "policy_snapshot_mismatch"}

    def remote_lookup(state):
        return {"policy_id": policy["id"] if policy else "", "visited": ["lookup"]}

    def ready(state):
        return {"decision": "draft", "visited": state["visited"] + ["draft"]}

    state = build_graph(lookup_node=remote_lookup, draft_node=ready).invoke(
        {"topic": topic, "contact": contact})
    output = {"mode": mode, "policy": policy_data, "graph": state}
    if state["decision"] == "ask":
        return {**output, "decision": "ask"}

    def lookup_policy(topic: str) -> str:
        """Read the policy snapshot obtained from the MCP server for this request."""
        data = policy_data if topic == policy_data["topic"] else {"found": False, "policy": None, "topic": topic}
        return json.dumps(data, ensure_ascii=False)

    generated = draft_answer(topic, mode, policy_tool=lookup_policy)
    draft = generated["trace"][-1]["content"]

    def revise(text, feedback):
        if mode == "fixed":
            return f"{policy['rule']} [근거: {policy['id']}]"
        response = get_model("live").invoke(
            "규정을 근거로 초안을 수정하십시오. 담당 팀과 근거 ID를 포함하십시오.\n" +
            json.dumps({"policy": policy, "draft": text, "feedback": feedback}, ensure_ascii=False))
        return response.content

    refined = bounded_refine(draft, topic, revise)
    output.update({"langchain": generated, "loop": refined})
    if refined["status"] != "passed":
        return {**output, "decision": "held"}
    payload = {"topic": topic, "draft": refined["draft"], "request_id": str(uuid.uuid4()), "version": 1}
    with server("course.a2a_lab", "--mode", mode) as url:
        reviewed = asyncio.run(delegate(url, payload))
    return {**output, "review": reviewed, "decision": reviewed["decision"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", default="정산")
    parser.add_argument("--contact", default="requester@example.test")
    parser.add_argument("--mode", choices=["fixed", "live"], default="fixed")
    args = parser.parse_args()
    result = run(args.topic, args.contact, args.mode)
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    (ROOT / "runs").mkdir(exist_ok=True)
    (ROOT / "runs" / f"integration-{args.mode}.json").write_text(rendered, encoding="utf-8")
    print(rendered)
