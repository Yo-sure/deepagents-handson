"""Card discovery and both A2A bindings use real HTTP; only model decisions are scripted."""
import json

import nbformat
import pytest
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult

from tests.model_stub import ToolCallingStub
from tests.test_notebook_flow import ROOT, build_cell, completed_student, execute


class DiscoveryModel(ToolCallingStub):
    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        last = messages[-1]
        human = next(m.content for m in reversed(messages) if m.type == "human")
        # The remote Agent's inner model reviews prose without calling any tools.
        if "표현상 불명확한 점을 한 문장" in human:
            reply = AIMessage(content="대상과 처리 기한을 구체적으로 쓰십시오.")
            return ChatResult(generations=[ChatGeneration(message=reply)])
        style = "표현" in human and "정책" not in human
        unknown = "없는업무" in human

        def call(name, args):
            return AIMessage(content="", tool_calls=[{
                "name": name, "args": args, "id": f"test-{name}", "type": "tool_call",
            }])

        if not isinstance(last, ToolMessage):
            reply = call("discover_agents", {}) if style else call(
                "lookup_policy", {"topic": "없는업무" if unknown else "계정"}
            )
        elif last.name == "lookup_policy":
            content = last.content
            if isinstance(content, list):
                content = "".join(block["text"] for block in content if block["type"] == "text")
            data = json.loads(content)
            reply = call("discover_agents", {}) if data["found"] else AIMessage(
                content="등록된 규정이 없습니다. 업무명을 알려주십시오."
            )
        elif last.name == "discover_agents":
            cards = json.loads(last.content)
            # Use returned Card descriptions, never candidate ordering or IDs.
            phrase = "문장의" if style else "정책 ID"
            chosen = next(entry for entry in cards if phrase in entry["card"]["description"])
            skill = chosen["card"]["skills"][0]["id"]
            reply = call("delegate_to_agent", {
                "agent_id": chosen["agent_id"], "skill_id": skill, "topic": "계정",
                "draft": "그거 처리해 주세요" if style else "계정 문의는 IT지원팀입니다. 근거 P-02",
            })
        elif last.name == "delegate_to_agent":
            reply = AIMessage(content="실제 검토 결과를 받았습니다.")
        else:
            raise AssertionError(f"Unexpected tool result: {last.name}")
        return ChatResult(generations=[ChatGeneration(message=reply)])


@pytest.mark.parametrize("edition", ["student", "solution"])
@pytest.mark.parametrize("scenario", ["policy", "style", "unknown"])
def test_discovery_selects_from_real_cards_and_dispatches(scenario, edition):
    notebook = completed_student() if edition == "student" else nbformat.read(
        ROOT / "notebooks/build-agent-solution.ipynb", as_version=4
    )
    cells = [build_cell(notebook, 1), nbformat.v4.new_code_cell("""
from tests.test_discovery_flow import DiscoveryModel
import course.common
course.common.get_model = lambda: DiscoveryModel()
""")]
    cells.extend(build_cell(notebook, i) for i in [3, 21, 32, 42])
    mission = {"policy": "계정 정책 검토", "style": "표현만 검토", "unknown": "없는업무 조회"}[scenario]
    cells.append(nbformat.v4.new_code_cell(f"scenario = {scenario!r}\nmission = {mission!r}\n" + """
previous_task = None
for reverse in [False, True]:
    run, discovery, reviews = await run_connected_agent(mission, reverse_candidates=reverse)
    names = [call["name"] for message in run["messages"]
             for call in getattr(message, "tool_calls", [])]
    if scenario == "unknown":
        assert names == ["lookup_policy"], names
        assert not discovery and not reviews
        assert "규정이 없습니다" in run["messages"][-1].content
        continue
    assert names.count("discover_agents") == names.count("delegate_to_agent") == 1
    assert len(discovery) == 1 and len(discovery[0]) == 2
    assert len(reviews) == 1
    record = reviews[0]
    assert record["state"] == "completed" and record["task_id"]
    assert record["task_id"] != previous_task
    previous_task = record["task_id"]
    expected_id = "candidate-a" if scenario == "style" else "candidate-b"
    assert record["agent_id"] == expected_id
    assert record["skill_id"] == ("review-style" if scenario == "style" else "review-policy")
    assert record["binding"] == ("HTTP+JSON" if scenario == "style" else "JSONRPC")
    assert record["artifact"]["model_note"]
    if scenario == "style":
        assert "lookup_policy" not in names
        assert "passed" not in record["artifact"] and "decision" not in record
    else:
        assert names[0] == "lookup_policy"
        assert record["decision"] == "accepted" and record["artifact"]["passed"] is True
"""))
    execute(cells)


@pytest.mark.parametrize("edition", ["student", "solution"])
def test_graph_observation_runs_with_intentionally_replaced_history(edition):
    notebook = completed_student() if edition == "student" else nbformat.read(
        ROOT / "notebooks/build-agent-solution.ipynb", as_version=4
    )
    observation = next(cell for cell in notebook.cells if cell.cell_type == "code"
                       and "observation_graph.stream" in cell.source)
    assert "check_graph(" not in observation.source
    cells = [build_cell(notebook, i) for i in [1, 3, 10]]
    cells.append(nbformat.v4.new_code_cell("""
original_ask = ask_for_details

def ask_for_details(state):
    result = original_ask(state)
    result["visited"] = ["ask"]
    return result
"""))
    cells.append(observation)
    cells.append(nbformat.v4.new_code_cell("""
observed = observation_graph.invoke(observation_input)
assert observed["visited"] == ["ask"]
assert observed["data"]["found"] is True
assert observed["topic"] == "계정" and observed["decision"] == "ask"
"""))
    execute(cells)
