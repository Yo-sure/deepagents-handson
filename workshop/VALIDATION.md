# 실행 검증 기록

검증일: 2026-09-06. WSL Ubuntu 24.04, Python 3.12, 별도 가상환경과 `uv.lock`을 사용했습니다.

| 항목 | 결과 |
|---|---|
|자동 검사|27개 통과 (`uv run --locked pytest -q`)|
|LangChain 고정 모델|실제 모델 요청→도구 실행→답변 메시지 순서 확인|
|LangGraph|정상·정보 부족 분기, 같은 프로세스 승인 재개 확인|
|DeepAgents|fixed 및 live 실행 확인. live에서 Skill read_file→정책 조회→답변 관찰|
|MCP|별도 HTTP 서버 호출·재시작·같은 업무 키 재사용 확인|
|A2A|별도 HTTP 검토, 완료와 artifact 통과 여부 구분 확인|
|통합|정산·계정 accepted, 없는 정책·빈 회신 대상 ask, 정책 기준 불일치 held|
|기본/확장 과제|시작 코드 오류 검출 및 기준 풀이 통과|
|실제 LLM|LangChain·DeepAgents·통합 live 실행 통과. 통합 A2A 모델 검토 포함. 입력별 품질 평가는 별도 필요|

검증 시 잠긴 주요 버전은 LangChain 1.4.0, LangGraph 1.2.11, DeepAgents 0.7.13, MCP 2.1.1, A2A SDK 1.1.2입니다. 전체 의존성은 `uv.lock`을 기준으로 합니다. 이 기록은 학습용 예제의 확인 범위이며 운영 성능·보안·자연어 정확성을 보증하지 않습니다.
