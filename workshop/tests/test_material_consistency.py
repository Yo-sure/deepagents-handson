"""제공 실행 코드와 학생·풀이 계약이 설명 없이 달라지는 회귀를 검사합니다."""
import ast
import json
from pathlib import Path
import pytest
from build_lab.materials import inspect_draft
from build_lab.guided import refine_answer
from course.common import lookup_policy

ROOT = Path(__file__).resolve().parents[1]
EXERCISES = {
    "build-agent": {"course-03", "course-06", "service-agent-build", "course-10",
                    "retry-graph-build", "course-20", "a1f3f0e3", "course-24", "59d04070"},
    "harness-build": {"h1-skill", "h2-build"},
}

def cells(name):
    return json.loads((ROOT / f"notebooks/{name}.ipynb").read_text(encoding="utf-8"))["cells"]

def tree(cell):
    return ast.parse("".join(cell["source"]))

@pytest.mark.parametrize("name", EXERCISES)
def test_provided_cells_match_and_exercise_signatures_agree(name):
    student = [c for c in cells(name) if c["cell_type"] == "code"]
    solution = [c for c in cells(name + "-solution") if c["cell_type"] == "code"]
    assert len(student) == len(solution)
    for left, right in zip(student, solution):
        if left["id"] not in EXERCISES[name]:
            assert ast.dump(tree(left)) == ast.dump(tree(right)), left["id"]
        else:
            def signatures(cell):
                return [(n.name, ast.dump(n.args)) for n in tree(cell).body
                        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
            assert signatures(left) == signatures(right), left["id"]
            if left["id"] == "h1-skill":
                assignment = tree(right).body[0]
                assert ast.literal_eval(assignment.value).strip()
            else:
                assert "NotImplementedError" not in "".join(right["source"]), right["id"]

@pytest.mark.parametrize("name", ["build-agent", "build-agent-solution"])
@pytest.mark.parametrize("mode,limit", [("same",0),("same",2),("change",2),("pass",2),("last",2)])
def test_notebook_loop_matches_shared_loop(name, mode, limit):
    cell = next(c for c in cells(name) if c.get("id") == "course-15")
    namespace = {"inspect_draft": inspect_draft}
    exec(compile(tree(cell), "notebook-loop", "exec"), namespace)
    data = json.loads(lookup_policy("계정"))
    def run(fn):
        calls=[]
        def revise(draft, feedback):
            calls.append((draft, feedback))
            if mode == "pass" or (mode == "last" and len(calls)==2):
                return "IT지원팀 P-02"
            return draft if mode == "same" else draft + " 수정"
        return fn("확인 완료", data, revise, limit), calls
    assert run(namespace["refine_answer"]) == run(refine_answer)


def test_a2a_solution_shows_acceptance_conditions():
    cell=next(c for c in cells("build-agent-solution") if c.get("id")=="course-24")
    body=tree(cell)
    assert any(isinstance(n,ast.If) for n in ast.walk(body))
    assert not any(isinstance(n,ast.ImportFrom) and n.module=="course.a2a_lab" for n in ast.walk(body))
