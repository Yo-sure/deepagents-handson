"""독립 변경 과제: 별칭 정규화와 기존 조회 계약을 함께 검사합니다."""

import json
import pytest


@pytest.fixture
def lookup(request):
    if request.config.getoption("--build-student"):
        from build_lab.student import lookup_policy
    else:
        from build_lab.transfer_solution import lookup_policy
    return lookup_policy


@pytest.mark.parametrize(
    "raw,canonical,policy_id",
    [
        ("로그인", "계정", "P-02"),
        (" 비용 ", "정산", "P-01"),
        ("계정", "계정", "P-02"),
        (" 정산 ", "정산", "P-01"),
        ("로그인 장애", "로그인 장애", None),
        ("비용 취소", "비용 취소", None),
        ("없는업무", "없는업무", None),
        (" ", "", None),
    ],
)
def test_alias_contract(lookup, raw, canonical, policy_id):
    data = json.loads(lookup(raw))
    assert data["topic"] == canonical
    assert data["found"] is (policy_id is not None)
    if policy_id is None:
        assert data["policy"] is None
    else:
        assert data["policy"]["id"] == policy_id


def test_lookup_does_not_rewrite_shared_policy(lookup):
    from copy import deepcopy
    from build_lab.materials import POLICIES

    before = deepcopy(POLICIES)
    lookup("로그인")
    lookup("비용")
    assert POLICIES == before


def test_transfer_complete_uses_canonical_review_topic(request, monkeypatch):
    from build_lab import transfer_solution, student
    from build_lab import runner
    from course import a2a_lab
    from contextlib import contextmanager
    from tests.model_stub import ToolCallingStub

    original_server = runner.server

    @contextmanager
    def local_server(module, *args):
        if module == "course.a2a_lab":
            yield "http://test-only.invalid"
        else:
            with original_server(module, *args) as url:
                yield url

    async def review(url, payload):
        assert payload["topic"] == "계정"
        return {
            "state": "completed",
            "artifact": {
                "request_id": payload["request_id"],
                "version": payload["version"],
                "passed": True,
            },
        }

    monkeypatch.setattr(runner, "server", local_server)
    monkeypatch.setattr(a2a_lab, "delegate", review)
    impl = student if request.config.getoption("--build-student") else transfer_solution
    result = runner.run(impl, stage="complete", topic="로그인", model=ToolCallingStub())
    assert result["state"]["data"]["topic"] == "계정"
    assert result["state"]["decision"] == "passed"
    assert result["review"]["decision"] == "accepted"
