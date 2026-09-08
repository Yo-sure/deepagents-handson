"""입력값을 수정한 뒤 이 파일을 실행합니다. 서버 수명 관리는 제공 코드가 맡습니다."""
from pprint import pprint
from build_lab import student
from build_lab.runner import run

topic = "계정"
contact = "user@example.test"
result = run(student, stage="mcp", topic=topic, contact=contact)
pprint(result, sort_dicts=False)
