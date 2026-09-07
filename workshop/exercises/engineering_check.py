"""코딩 에이전트와 설계 변경을 검증하는 과제입니다."""
import argparse
from course.graph_lab import build_graph
from course.harness_lab import verify


def evaluate(router, refiner):
    results = []
    for contact, expected in [('user', 'draft'), ('', 'ask'), ('   ', 'ask'), ('\t', 'ask')]:
        actual = build_graph(router=router).invoke({'topic':'정산', 'contact':contact})
        results.append((f'회신 대상 {contact!r}: {expected}', actual['decision'] == expected))
    missing = build_graph(router=router).invoke({'topic':'없는업무', 'contact':'user'})
    results.append(('없는 정책은 추가 확인', missing['decision'] == 'ask'))

    # 이 콜백은 모델 응답을 흉내 내지 않습니다. 주입한 수정 함수의 호출 횟수를 검사합니다.
    calls = []
    def unchanged(text, feedback):
        calls.append(feedback)
        return text
    stalled = refiner('초안', '정산', unchanged, 3)
    results.append(('같은 실패 초안은 stalled', stalled['status'] == 'stalled'))
    results.append(('정체 이후에는 다시 수정하지 않음', len(calls) == 1))
    results.append(('수정 함수에 구체적인 실패 이유 전달', bool(calls) and all(feedback == verify('초안', '정산') for feedback in calls)))
    calls.clear()
    good = refiner('재무지원팀 P-01', '정산', unchanged, 0)
    results.append(('최초 성공은 수정 없이 passed', good['status'] == 'passed' and not calls))
    held = refiner('초안', '정산', unchanged, 0)
    results.append(('예산 0의 실패는 수정 없이 held', held['status'] == 'held' and not calls))
    results.append(('성공 초안과 검토 기록을 보존', good.get('draft') == '재무지원팀 P-01' and good.get('history') == [{'attempt': 0, 'draft': '재무지원팀 P-01', 'feedback': []}]))
    results.append(('정체 시 실제 두 검토 기록을 보존', stalled.get('draft') == '초안' and stalled.get('history') == [{'attempt': i, 'draft': '초안', 'feedback': verify('초안', '정산')} for i in range(2)]))
    changed = []
    def keep_changing(text, feedback):
        changed.append(feedback)
        return text + '!'
    budget = refiner('초안', '정산', keep_changing, 2)
    results.append(('바뀌어도 계속 실패하면 예산에서 보류', budget.get('status') == 'held' and len(changed) == 2 and budget.get('draft') == '초안!!'))
    results.append(('예산 소진까지 실제 검토 이력 보존', budget.get('history') == [{'attempt': i, 'draft': '초안' + '!' * i, 'feedback': verify('초안' + '!' * i, '정산')} for i in range(3)]))
    repaired = []
    def repair(text, feedback):
        repaired.append(feedback)
        return '담당 팀 확인 중' if len(repaired) == 1 else '재무지원팀 P-01'
    success = refiner('초안', '정산', repair, 2)
    results.append(('마지막 허용 수정에서 성공하면 passed', success.get('status') == 'passed' and success.get('draft') == '재무지원팀 P-01' and len(repaired) == 2))
    results.append(('각 수정에 해당 초안의 피드백 전달', repaired == [verify('초안', '정산'), verify('담당 팀 확인 중', '정산')]))
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    from . import student, extensions
    try:
        results = evaluate(student.route_inquiry, extensions.refine_without_stall)
        for label, ok in results:
            print(f"{'PASS' if ok else 'FAIL'} {label}")
        raise SystemExit(0 if all(ok for _, ok in results) else 1)
    except (KeyError, TypeError, ValueError) as error:
        print(f'FAIL: 함수의 반환 계약을 확인하십시오 ({type(error).__name__})')
        raise SystemExit(1)


if __name__ == '__main__':
    main()
