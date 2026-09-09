"""배포 노트북의 실제 셀을 커널과 HTTP 서버에서 실행합니다. 모델만 대체합니다."""

import ast
from pathlib import Path

import pytest

nbformat = pytest.importorskip("nbformat")
NotebookClient = pytest.importorskip("nbclient").NotebookClient
ROOT = Path(__file__).resolve().parents[1]

# Original lesson positions map to stable notebook cell IDs, so inserted lesson cells
# do not silently change which exercise this regression suite executes.
BUILD_CELL_IDS = {
    1: ('course-01',),
    3: ('course-03',),
    4: ('course-04',),
    6: ('course-06',),
    7: ('course-07',),
    10: ('course-10',),
    11: ('course-11',),
    13: ('course-13',),
    15: ('course-15',),
    16: ('course-16',),
    21: ('course-20',),
    22: ('course-21',),
    24: ('4207486b', '30eec1d0'),
    28: ('a1f3f0e3', '5bf91bbd'),
    30: ('3279cf50', 'e9d4e2aa'),
    32: ('course-24',),
    33: ('course-25',),
    35: ('e25a29d2', '530e87c3'),
    37: ('5e0a2dbb', '53c5a346'),
    39: ('acb8fca3', 'aa75be74'),
    42: ('59d04070', '5e93e726'),
}


def build_cell(notebook, lesson_index):
    identifiers = BUILD_CELL_IDS[lesson_index]
    return next(cell for cell in notebook.cells if cell.id in identifiers)


MODEL_SETUP = """
from tests.model_stub import ToolCallingStub
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from course.common import POLICIES

class NotebookModel(ToolCallingStub):
    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        last = messages[-1]
        if not isinstance(last, ToolMessage):
            text = last.content
            if "수정" in text:
                topic = "계정" if "P-02" in text else "정산"
                policy = POLICIES[topic]
                return ChatResult(generations=[ChatGeneration(message=AIMessage(content=policy["team"] + " " + policy["id"]))])
            if "표현상" not in text:
                topic = "계정" if "계정" in text else "없는업무" if "없는업무" in text else "정산"
                messages = [*messages[:-1], HumanMessage(content=json.dumps({"topic": topic}))]
        return super()._generate(messages, stop=stop, run_manager=run_manager, **kwargs)

def get_model():
    return NotebookModel()

import course.common
course.common.get_model = get_model
"""


def execute(cells):
    notebook = nbformat.v4.new_notebook(cells=cells)
    return NotebookClient(
        notebook,
        timeout=90,
        kernel_name="python3",
        resources={"metadata": {"path": str(ROOT)}},
    ).execute()


def test_notebook_syntax_and_clean_outputs():
    for path in (ROOT / "notebooks").glob("*.ipynb"):
        notebook = nbformat.read(path, as_version=4)
        nbformat.validate(notebook)
        for cell in notebook.cells:
            if cell.cell_type == "code":
                assert not cell.outputs and cell.execution_count is None
                compile(
                    cell.source, str(path), "exec", flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT
                )


@pytest.mark.parametrize("alias", [False, True])
@pytest.mark.parametrize("edition", ["solution", "student"])
def test_solution_notebook_end_to_end(alias, edition):
    notebook = nbformat.read(
        ROOT / "notebooks/build-agent-solution.ipynb", as_version=4
    )
    if edition == "student":
        notebook = completed_student()
    cells = []
    for cell in notebook.cells:
        if cell.cell_type != "code":
            continue
        # 6D has a separate model-driven discovery suite with real Card/Task assertions.
        if "await run_connected_agent(mission)" in cell.source:
            continue
        if alias and "snapshot_topics" in cell.source:
            raise AssertionError("옛 snapshot 구현이 남아 있습니다.")
        if alias and "snapshot =" in cell.source:
            cells.append(
                nbformat.v4.new_code_cell(
                    "from build_lab.transfer_solution import lookup_policy"
                )
            )
            cell.source = cell.source.replace('topic = "계정"', 'topic = "로그인"')
        cells.append(cell)
        if "root = Path.cwd()" in cell.source:
            cells.append(nbformat.v4.new_code_cell(MODEL_SETUP))
    cells.append(
        nbformat.v4.new_code_cell("""
assert result["data"]["topic"] == "계정"
assert result["visited"] == ["lookup", "draft", "review"]
assert review["artifact"]["passed"] is True
assert decision == "accepted"
assert payload["topic"] == "계정"
# MCP 서버가 종료된 뒤에도 앞 장의 로컬 Agent를 다시 사용할 수 있습니다.
assert "P-01" in generate_answer("정산")
# 계정 예제를 실행한 커널에서 정산으로 바꾸면 새 정책으로 수정해야 합니다.
changed = refine("확인 완료", json.loads(lookup_policy("정산")), 2)
assert changed["status"] == "passed"
assert "P-01" in changed["draft"] and "P-02" not in changed["draft"]
""")
    )
    execute(cells)


def test_orientation_notebook():
    notebook = nbformat.read(ROOT / "notebooks/orientation.ipynb", as_version=4)
    cells = [cell for cell in notebook.cells if cell.cell_type == "code"]
    cells.insert(1, nbformat.v4.new_code_cell("import json\n" + MODEL_SETUP))
    cells.append(
        nbformat.v4.new_code_cell('assert "P-01" in result["messages"][-1].content')
    )
    execute(cells)


@pytest.mark.parametrize(
    "indices", [[1, 3], [1, 5], [1, 7], [1, 9, 10, 11], [1, 13], [1, 17]]
)
def test_concept_sections_run_independently(indices):
    notebook = nbformat.read(ROOT / "notebooks/concepts.ipynb", as_version=4)
    execute([notebook.cells[i] for i in indices])


def test_student_langchain_cells_and_textbook_followup():
    """1A・1B만 완성한 새 커널에서 교재의 추가 질문까지 실행합니다."""
    import re

    student = nbformat.read(ROOT / "notebooks/build-agent.ipynb", as_version=4)
    solution = nbformat.read(ROOT / "notebooks/build-agent-solution.ipynb", as_version=4)
    chapter = ROOT.parent / "books/workshop/langchain.md"
    if not chapter.is_file():
        pytest.skip("배포 ZIP에는 교재 원문이 포함되지 않습니다.")
    section = chapter.read_text(encoding="utf-8").split(
        "### 질문을 바꾸고 메시지를 읽습니다", 1
    )[1]
    example = re.search(r"```python\n(.*?)```", section, re.S).group(1)
    cells = [build_cell(student, 1), nbformat.v4.new_code_cell(MODEL_SETUP)]
    for index in [3, 4, 6, 7]:
        cells.append(build_cell(solution, index) if index in [3, 6] else build_cell(student, index))
    cells.append(nbformat.v4.new_code_cell("""
assert result["messages"][-1].type == "ai"
assert "P-02" in result["messages"][-1].content
assert any(m.type == "tool" for m in result["messages"])
"""))
    cells.append(nbformat.v4.new_code_cell(example))
    cells.append(nbformat.v4.new_code_cell("""
assert any(m.type == "tool" for m in result["messages"])
assert result["messages"][-1].content
"""))
    execute(cells)


def completed_student():
    """학생용 제공 셀을 유지하고 지정된 구현 부분만 완성합니다."""
    student = nbformat.read(ROOT / "notebooks/build-agent.ipynb", as_version=4)
    solution = nbformat.read(ROOT / "notebooks/build-agent-solution.ipynb", as_version=4)
    for index in [3, 6, 10, 21, 32]:
        build_cell(student, index).source = build_cell(solution, index).source
    build_cell(student, 24).source = build_cell(student, 24).source.replace(
        "tools = []  # TODO: adapter에서 도구 목록을 받아 연결합니다.",
        "tools = await adapter.list_tools()",
    )
    return student


@pytest.mark.parametrize("section,indices,assertion", [
    ("graph", [3, 6, 7, 10, 11, 13], 'assert result["decision"] == "ask" and not draft_calls'),
    ("loop", [3, 15, 16], 'assert repaired["status"] == "passed"'),
    ("mcp", [3, 21, 22, 24], 'assert any(m.type == "tool" for m in result["messages"])'),
    ("a2a", [28, 30, 32, 33], 'assert review["artifact"]["passed"] is True'),
    ("integration", [3, 6, 10, 15, 21, 28, 32, 35, 37, 39], 'assert decision == "accepted"'),
])
def test_student_sections_from_fresh_kernel(section, indices, assertion):
    notebook = completed_student()
    cells = [build_cell(notebook, 1), nbformat.v4.new_code_cell(MODEL_SETUP)]
    cells.extend(build_cell(notebook, i) for i in indices)
    cells.append(nbformat.v4.new_code_cell(assertion))
    execute(cells)


def test_card_and_mcp_without_model_setup():
    notebook = completed_student()
    cells = [build_cell(notebook, 1), nbformat.v4.new_code_cell("""
def forbid_model():
    raise AssertionError("모델 없는 실습에서 모델 설정을 요청했습니다.")
import course.common
course.common.get_model = forbid_model
get_model = forbid_model
""")]
    cells.extend(build_cell(notebook, i) for i in [3, 21, 22, 28])
    cells.append(nbformat.v4.new_code_cell('assert card.skills[0].id == "review-policy"'))
    execute(cells)


def test_unfinished_mcp_connection_stops_before_model_call():
    from nbclient.exceptions import CellExecutionError

    notebook = completed_student()
    original = nbformat.read(ROOT / "notebooks/build-agent.ipynb", as_version=4)
    cells = [build_cell(notebook, 1), nbformat.v4.new_code_cell(MODEL_SETUP)]
    cells.extend(build_cell(notebook, i) for i in [3, 21])
    cells.append(build_cell(original, 24))
    with pytest.raises(CellExecutionError, match="4B: await adapter.list_tools"):
        execute(cells)


@pytest.mark.parametrize("decision,expected", [("approve", "approved"), ("reject", "held")])
def test_approval_decisions_from_fresh_kernel(decision, expected):
    notebook = nbformat.read(ROOT / "notebooks/concepts.ipynb", as_version=4)
    notebook.cells[11].source = notebook.cells[11].source.replace('decision = "approve"', f'decision = "{decision}"')
    cells = [notebook.cells[i] for i in [1, 9, 10, 11]]
    cells.append(nbformat.v4.new_code_cell(f'assert resumed["decision"] == "{expected}"; assert app.get_state(config).next == ()'))
    execute(cells)
