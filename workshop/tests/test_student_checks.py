"""학습자에게 제공하는 완료 검사가 실제로 잘못된 구현을 찾아내는지 확인합니다."""

import json

import pytest

from build_lab import guided, reference
from build_lab.notebook_checks import check_accept_review, check_graph, check_lookup


def workflow_with(router=None, ask_node=None):
    """동일한 실행 구조에서 학습자가 작성한 두 함수만 교체합니다."""

    def build(lookup, generate, refine, limit=2):
        return guided.build_workflow(
            lookup,
            generate,
            refine,
            limit,
            router=router or reference.route_inquiry,
            ask_node=ask_node or reference.ask_for_details,
        )

    return build


def test_reference_implementations_pass_student_checks():
    check_lookup(reference.lookup_policy)
    check_graph(workflow_with(), reference.lookup_policy)
    check_accept_review(reference.accept_review)


@pytest.mark.parametrize("field,value", [("id", "P-99"), ("team", "잘못된 팀")])
def test_lookup_check_rejects_wrong_policy_contents(field, value):
    def lookup(topic):
        result = json.loads(reference.lookup_policy(topic))
        if result["found"]:
            result["policy"][field] = value
        return json.dumps(result, ensure_ascii=False)

    with pytest.raises(AssertionError, match=r"\S"):
        check_lookup(lookup)


def test_graph_check_rejects_whitespace_contact_as_present():
    def route(state):
        return "draft" if state["data"]["found"] and state.get("contact") else "ask"

    with pytest.raises(AssertionError, match=r"\S"):
        check_graph(workflow_with(router=route), reference.lookup_policy)


def test_graph_check_rejects_requesting_already_known_fields():
    def ask(state):
        result = reference.ask_for_details(state)
        result["missing"] = ["topic", "contact"]
        return result

    with pytest.raises(AssertionError, match=r"\S"):
        check_graph(workflow_with(ask_node=ask), reference.lookup_policy)


def test_accept_check_rejects_ignoring_review_failure():
    def accept(state, artifact, request_id, version):
        if isinstance(artifact, dict):
            artifact = {**artifact, "passed": True}
        return reference.accept_review(state, artifact, request_id, version)

    with pytest.raises(AssertionError, match=r"\S"):
        check_accept_review(accept)


def test_accept_check_rejects_truthy_string_as_passed():
    def accept(state, artifact, request_id, version):
        if isinstance(artifact, dict):
            artifact = {**artifact, "passed": bool(artifact.get("passed"))}
        return reference.accept_review(state, artifact, request_id, version)

    with pytest.raises(AssertionError, match=r"\S"):
        check_accept_review(accept)


def test_accept_check_rejects_boolean_version_as_integer():
    def accept(state, artifact, request_id, version):
        if isinstance(version, bool):
            version = int(version)
        if isinstance(artifact, dict) and isinstance(artifact.get("version"), bool):
            artifact = {**artifact, "version": int(artifact["version"])}
        return reference.accept_review(state, artifact, request_id, version)

    with pytest.raises(AssertionError, match=r"\S"):
        check_accept_review(accept)
