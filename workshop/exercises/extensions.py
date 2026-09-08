"""확장 과제 시작점. 기존 제공 코드를 수정하지 않고 이 파일에서 구현합니다."""


def evidence_matches(answer, policy):
    return True


def approval_matrix():
    return {}


def refine_without_stall(draft, topic, revise, limit=2):
    from course.harness_lab import bounded_refine

    return bounded_refine(draft, topic, revise, limit)


def ticket_restart():
    return {}


def review_version(state, artifact, request_id, version):
    return "accepted"
