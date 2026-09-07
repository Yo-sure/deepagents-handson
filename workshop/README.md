# AI Agent 개발 실습 — 2026.09-rc1

이 ZIP의 실행 위치는 workshop 폴더입니다. 공통 주 실습은 build_lab/student.py입니다. 도구·Agent·업무 분기·MCP 공개·A2A 수용을 직접 구현합니다. 그래프 조립·수정 루프는 guided.py의 제공 구조를 읽고 활용합니다. 전체 재구현은 선택 심화입니다.

## 준비와 첫 실행

WSL Ubuntu 24.04와 Python 3.12를 기준으로 검증합니다. Python의 함수·dict·조건문·import를 읽는 수준을 전제로 합니다. Linux·Git 자체를 배우는 과정은 아니며, 자료는 ZIP으로 받으면 됩니다. 수업은 강사 소개·설문 리뷰 10분 후 환경설정을 함께 진행합니다. 이미 설치했다면 실행 위치와 첫 모델 호출까지 확인합니다.

```bash
uv sync --locked --python 3.12
cp .env.example .env
```

.env를 편집하여 발급받은 OPENROUTER_API_KEY를 입력합니다. 키는 코드·노트북·실행 기록에 넣지 않습니다. 실제 모델 연결을 확인합니다.

```bash
uv run --locked python -m course.cli langchain --topic 정산
```

키·네트워크·모델 접근 오류가 발생하면 오류 원인을 해결한 뒤 재실행합니다. 실제 모델의 도구 요청과 tool 반환, 최종 답변이 있는지 읽습니다.

## 재료와 구현 순서

build_lab/materials.py의 정책 표와 Inquiry를 먼저 읽습니다. provided guided.py는 공통 과정의 완성 구조입니다. 학생 파일의 NotImplementedError 자리를 다음 계약에 맞게 작성합니다.

|단계|작성할 함수|입출력·완료 기준|
|---|---|---|
|1A|lookup_policy(topic)|공백 제거 후 조회. JSON 문자열에 found/topic/policy. 없는 정책은 false/null.|
|1B|build_agent(model, policy_tool)|create_agent의 model/tools/system_prompt를 지정하고 Agent 반환. 실제 조회 후 근거 ID·팀을 답하도록 지침 작성.|
|2|route_inquiry(state)|state['data']['found']와 contact.strip()이 모두 충족되면 draft, 아니면 ask.|
|3|제공 루프 관찰|guided.py의 성공·정체·예산 조건과 실제 history 읽기. 직접 작성은 선택 심화.|
|4|build_mcp_server(policy_tool)|MCPServer 생성, tool()(policy_tool)로 등록, 서버 반환.|
|5|accept_review(state, artifact, request_id, version)|진행이면 pending, completed에서 요청 ID·양의 정수 버전·artifact 일치·passed is True일 때만 accepted, 나머지 held. 빈 ID·bool 버전 거부.|

검사는 단계별로 실행합니다. -k 뒤에는 lookup, agent, graph, loop, mcp, a2a 중 현재 단계를 넣습니다.

```bash
uv run --locked pytest tests/test_build_lab.py --build-student -q -k lookup
```

처음에는 NotImplementedError로 실패합니다. 미구현 부분을 알려주는 것이며 설치 오류가 아닙니다. --build-student를 빼면 기준 풀이 검사이므로 자신의 구현을 검사할 때 유지합니다.

실제 모델·프로토콜 실행은 다음 명령입니다. 앞 단계가 준비된 뒤 필요한 단계만 실행합니다.

```bash
uv run --locked python -m build_lab.runner agent --topic 계정
uv run --locked python -m build_lab.runner graph --topic 정산 --contact "   "
uv run --locked python -m build_lab.runner workflow --topic 계정
uv run --locked python -m build_lab.runner mcp --topic 계정
uv run --locked python -m build_lab.runner complete --topic 계정
```

완성 실행은 학생 도구·Agent·분기·수용 판단을 제공 그래프·루프·A2A 서버에 연결합니다. 공백 문의에서는 모델을 호출하지 않고 ask로 끝나야 합니다. 정상 요청이 검토를 통과하지 못하면 history와 feedback을 읽습니다. 실행 기록은 runs/build-단계-고유값.json으로 저장됩니다.

## 앞 단계에서 막힌 경우

현재 과제까지 포기할 필요는 없습니다. 다만 주 실습은 앞 단계 함수에 의존합니다. student.py를 다른 이름으로 복사해 자신의 작업을 보관한 뒤, **미완성인 앞 단계 함수만** reference.py의 같은 함수 정의로 교체합니다. 현재 풀어야 할 함수는 그대로 둡니다. 제공받은 함수는 직접 작성한 함수와 구분합니다.

|진행할 단계|준비돼 있어야 하는 앞 단계 함수|
|---|---|
|Graph|lookup_policy, build_agent|
|Loop 관찰|lookup_policy, build_agent, route_inquiry|
|MCP|lookup_policy|
|A2A/전체 연결|lookup_policy, build_agent, route_inquiry, build_mcp_server|

reference.py의 함수 내용을 복사하고 필요한 import는 학생 파일에 이미 제공된 것을 사용합니다. 파일 전체를 덮어쓰지 않습니다. provided build_workflow/refine_answer는 그대로 둡니다. 교재 시연을 먼저 보는 경우 course의 완성 예제는 학생 파일과 독립적으로 실행됩니다.

## 주피터 선택 경로

```bash
uv sync --locked --group notebook
uv run --locked --group notebook jupyter lab notebooks/build-agent.ipynb
```

터미널에 표시된 로컬 주소에서 Python 3 커널을 사용합니다. 핵심 함수는 셀에서 작성하고 제공 그래프·루프를 관찰합니다. 함수 수정 후 아래 실행 셀을 다시 실행하고 마지막에는 커널 재시작 후 전체 실행합니다. 별도 풀이 노트북은 build-agent-solution.ipynb입니다.

작성한 lookup_policy/build_agent/route_inquiry 함수만 student.py의 같은 함수에 옮깁니다. 제공 그래프·루프의 파일 코드는 그대로 둡니다. 노트북 셀이 자동으로 파일을 바꾸지는 않습니다. 이후 MCP·A2A 파일 실습을 이어갑니다.

## Harness 활용 활동과 결과 비교

build_lab/HARNESS_WORKSHEET.md에서 반복 작업의 시작·선택·종료 조건과 역할별 의존성·산출물 계약을 작성합니다. 코딩 하네스 계정이 있으면 설계를 검토받고, 없으면 동일한 사례 풀이로 판단 기준을 설명합니다. 이미 올바른 코드라면 불필요하게 고치지 않고 검증 근거를 남깁니다.

```bash
uv run --locked pytest tests/test_build_lab.py --build-student -q
```

완료 기록은 자신의 구현, 정상·추가 확인·보류 사례, 직접 만든 반례, 확인하지 못한 한계입니다. 테스트의 모델 대역은 tests에만 있으며 실제 실행을 대신하지 않습니다. 제공 함수를 사용한 부분도 명시합니다. exercises는 준비 문제/추가 심화이며 주 실습과 모두 중복 수행하지 않습니다.

자료 구성은 RELEASE.md, 실행 환경과 검사 범위는 VALIDATION.md를 읽습니다.

## 통합 시간의 독립 변경

웹 교재 wrap의 새 요구에 따라 로그인→계정, 비용→정산 별칭을 지원합니다. 정책 원본·기존 함수 인자·반환 구조를 유지하며 명시되지 않은 문장을 추측해 분류하지 않습니다. 반환 topic은 정규 업무명이어야 합니다. 변경 전 실패와 변경 후 결과를 기록합니다.

```bash
uv run pytest tests/test_transfer.py --build-student -q
uv run pytest tests/test_build_lab.py --build-student -q
uv run python -m build_lab.runner complete --topic 로그인
```

transfer_solution.py는 별도 풀이입니다. 실제 모델 실행은 마지막 명령이며 tests의 모델 대역과 구분합니다. 노트북에서 옮긴 함수를 파일에서 변경하므로 이후 노트북의 이전 함수를 다시 복사하지 않습니다.

활동지의 F1/D1 사례로 다음 작업을 고르는 반복과 역할·의존성·검증 구조를 설계합니다. 실제 자동화를 등록하거나 전체 그래프 런타임을 구현하는 과제는 아닙니다. 기존 업무 분기와 초안 수정 코드는 이 업계 용어의 전체 구현이 아닙니다.

## 검사 파일의 용도

- 필수: `tests/test_build_lab.py --build-student`로 현재 구현을 검사합니다. 통합 변경 과제에서는 `tests/test_transfer.py --build-student`도 실행합니다.
- 선택: `uv run --locked pytest -q`는 제공 예제와 기준 풀이 전체를 검사합니다. 자신의 구현 완료를 뜻하지 않습니다.
- `tests/model_stub.py`와 테스트 서버는 자동 검사의 보조 코드입니다. 학습자가 수정할 파일이 아니며 실제 모델 실행에는 사용하지 않습니다.
