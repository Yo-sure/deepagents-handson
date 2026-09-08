"""제공 조회 함수를 연결한 결과를 확인합니다."""
from build_lab.student import lookup_policy

for topic in ["정산", " 계정 ", "없는업무"]:
    print(topic, lookup_policy(topic))
