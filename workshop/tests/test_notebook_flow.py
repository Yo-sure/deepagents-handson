"""배포 노트북의 실제 셀을 커널과 HTTP 서버에서 실행합니다. 모델만 대체합니다."""

import ast
from pathlib import Path

import pytest

nbformat = pytest.importorskip("nbformat")
NotebookClient = pytest.importorskip("nbclient").NotebookClient
ROOT = Path(__file__).resolve().parents[1]

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
def test_solution_notebook_end_to_end(alias):
    notebook = nbformat.read(
        ROOT / "notebooks/build-agent-solution.ipynb", as_version=4
    )
    cells = []
    for cell in notebook.cells:
        if cell.cell_type != "code":
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
