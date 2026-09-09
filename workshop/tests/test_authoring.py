"""직접 작성 실습의 연결과 종료 조건을 실제 프레임워크에서 검증합니다."""
import json
from pathlib import Path

import pytest
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain.agents import create_agent
from langchain.tools import tool

from course.policy_store import search_policy
from build_lab.materials import inspect_draft
from tests.model_stub import ToolCallingStub

ROOT = Path(__file__).resolve().parents[1]


def source(name, identifier):
    notebook = json.loads((ROOT / "notebooks" / name).read_text(encoding="utf-8"))
    return "".join(next(c for c in notebook["cells"] if c.get("id") == identifier)["source"])


class ServiceModel(ToolCallingStub):
    def _generate(self, messages, **kwargs):
        results = [m for m in messages if isinstance(m, ToolMessage)]
        if not results:
            calls = [{"name": "lookup_policy", "args": {"topic": topic}, "id": topic}
                     for topic in ["계정", "정산"]]
        elif results[-1].name == "lookup_policy":
            calls = [{"name": "lookup_team_contact", "args": {"team": json.loads(m.content)["policy"]["team"]},
                      "id": "contact-" + str(i)} for i, m in enumerate(results)]
        else:
            answer = " ".join(json.loads(m.content)["email"] for m in results if m.name == "lookup_team_contact")
            return ChatResult(generations=[ChatGeneration(message=AIMessage(content=answer))])
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content="", tool_calls=calls))])


def test_authored_service_composes_real_tools():
    ns = {"json": json, "tool": tool, "create_agent": create_agent, "search_policy": search_policy}
    for identifier in ["course-03", "service-agent-build"]:
        exec(source("build-agent-solution.ipynb", identifier), ns)
    agent = ns["build_service_agent"](ServiceModel(), ns["lookup_policy"], ns["lookup_team_contact"])
    result = ns["ask_service"](agent, "계정과 정산 연락처")
    assert {m.name for m in result["messages"] if m.type == "tool"} == {"lookup_policy", "lookup_team_contact"}
    assert "it@example.test" in result["messages"][-1].content
    assert "finance@example.test" in result["messages"][-1].content


@pytest.mark.parametrize("limit,fixed,attempts,passed", [(0, False, 0, False), (2, False, 2, False), (2, True, 1, True)])
def test_authored_retry_uses_business_budget(limit, fixed, attempts, passed):
    ns = {"inspect_draft": inspect_draft}
    exec(source("build-agent-solution.ipynb", "retry-graph-build"), ns)
    calls = []
    def revise(draft, feedback):
        calls.append(feedback)
        return "IT지원팀 P-02" if fixed else draft
    graph = ns["build_retry_graph"](revise, limit)
    result = graph.invoke({"draft": "잘못된 초안", "data": json.loads(search_policy("계정")),
                           "attempts": 0, "visited": []})
    assert result["attempts"] == len(calls) == attempts
    assert (not result["feedback"]) == passed
    assert result["visited"] == ["review"] + ["revise", "review"] * attempts


class SkillModel(ToolCallingStub):
    def _generate(self, messages, **kwargs):
        results = [m for m in messages if isinstance(m, ToolMessage)]
        if not results:
            call = {"name": "read_file", "args": {"file_path": "/skills/my-policy/SKILL.md"}, "id": "read"}
        elif results[-1].name == "read_file":
            assert "lookup_policy" in results[-1].content
            call = {"name": "lookup_policy", "args": {"topic": "계정"}, "id": "policy"}
        else:
            return super()._generate(messages, **kwargs)
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content="", tool_calls=[call]))])


def test_authored_harness_reads_written_skill(tmp_path):
    from deepagents import create_deep_agent
    from deepagents.backends import FilesystemBackend
    from course.common import lookup_policy
    ns = {"root": tmp_path, "create_deep_agent": create_deep_agent, "FilesystemBackend": FilesystemBackend}
    for identifier in ["h1-skill", "h2-build"]:
        exec(source("harness-build-solution.ipynb", identifier), ns)
    agent = ns["build_harness"](SkillModel(), lookup_policy, ns["workspace"])
    result = ns["run_harness"](agent, "계정 담당 팀과 근거")
    results = [m for m in result["messages"] if m.type == "tool"]
    assert [m.name for m in results] == ["read_file", "lookup_policy"]
    assert "P-02" in result["messages"][-1].content
