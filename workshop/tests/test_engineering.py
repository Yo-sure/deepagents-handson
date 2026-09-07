"""코딩 에이전트 과제의 결함 검출과 실제 학생 코드 연결을 확인합니다."""
import pytest
from exercises import student, extensions, extension_solutions, project
from exercises.engineering_check import evaluate
from course import integration
from course.processes import server
from .model_stub import ToolCallingStub


def corrected_router(state):
    return 'draft' if state.get('policy_id') and state.get('contact', '').strip() else 'ask'


def test_engineering_starter_exposes_distinct_failures():
    results = evaluate(student.route_inquiry, extensions.refine_without_stall)
    assert sum(not ok for _, ok in results) >= 4


def test_engineering_reference_preserves_baseline_and_stops_stall():
    assert all(ok for _, ok in evaluate(corrected_router, extension_solutions.refine_without_stall))


@pytest.mark.parametrize('contact,expected', [('   ', 'ask'), ('user', 'accepted')])
def test_student_project_uses_edited_graph_and_loop(monkeypatch, contact, expected):
    calls = []
    def refiner(*args):
        calls.append('student-refiner')
        return extension_solutions.refine_without_stall(*args)
    monkeypatch.setattr(student, 'route_inquiry', corrected_router)
    monkeypatch.setattr(extensions, 'refine_without_stall', refiner)
    monkeypatch.setattr(integration, 'server', lambda module, *args: server('tests.a2a_server' if module == 'course.a2a_lab' else module, *args))
    result = project.run(contact=contact, model=ToolCallingStub())
    assert result['decision'] == expected
    assert calls == ([] if expected == 'ask' else ['student-refiner'])
    if expected == 'ask':
        assert 'langchain' not in result and 'review' not in result


def test_engineering_rejects_status_only_implementation():
    def incomplete(draft, topic, revise, limit=2):
        result = extension_solutions.refine_without_stall(draft, topic, revise, limit)
        return {'status': result['status']}
    results = evaluate(corrected_router, incomplete)
    assert any(not ok for _, ok in results)
    assert any('기록' in label and not ok for label, ok in results)
