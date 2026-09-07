"""학생이 구현한 분기와 수정 루프를 실제 통합 실행에 연결합니다."""
import argparse
import json
from course.common import ROOT
from course.integration import run as run_integration
from . import student, extensions


def run(topic='정산', contact='requester@example.test', *, model=None):
    return run_integration(topic, contact, model=model,
        router=student.route_inquiry, refiner=extensions.refine_without_stall)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--topic', default='정산')
    parser.add_argument('--contact', default='requester@example.test')
    args = parser.parse_args()
    result = run(args.topic, args.contact)
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    (ROOT / 'runs').mkdir(exist_ok=True)
    (ROOT / 'runs' / 'project.json').write_text(rendered, encoding='utf-8')
    print(rendered)
