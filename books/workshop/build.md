---
layout: page
title: 내 업무 Agent 직접 완성하기
sidebar: false
aside: false
pageClass: lec-page
---
<div class="lec workshop-edition"><div class="deck">
<section class="slide">
<div class="eyebrow">개인 구현 · LangChain부터 원격 검토까지</div>

# 내 업무 Agent를 직접 완성합니다

문의가 들어오면 규정을 조회하고 답변을 작성합니다. 회신 대상이 없으면 먼저 질문하고, 초안이 기준을 놓치면 제한된 횟수 안에서 수정합니다. 마지막에는 별도 서버의 검토 결과를 읽어 수용 여부를 결정합니다. 실제 메일은 보내지 않습니다.

각 모듈에서 배운 개념을 같은 프로젝트에 차례로 적용합니다. 작은 함수 수정 문제는 막힐 때 사용하는 준비 문제입니다. 준비 문제의 PASS만으로 프로젝트를 완성했다고 판단하지 않습니다.

파일 방식에서는 `workshop/build_lab/student.py`의 도구·Agent·업무 분기·MCP 공개·A2A 수용의 다섯 부분을 작성합니다. 그래프 조립과 수정 루프는 제공 구조를 읽고 사용합니다. 초보자는 힌트와 API 재료를 사용하고, 익숙한 사람은 힌트 없이 구현한 뒤 새로운 실패 사례를 추가합니다. 핵심 개념과 완료 조건은 같습니다.

|제공하는 것|직접 만드는 것|
|---|---|
|규정 데이터, 모델 연결, 실행 기록 저장|조회 도구와 Agent 구성|
|State, 노드·간선으로 구성한 그래프|정책·회신 대상에 따른 업무 분기|
|학습용 검토 함수·수정 루프·모델 수정 함수|실패 이유·종료 조건을 읽고 하네스 활용 활동지 작성|
|HTTP 서버 실행·종료, A2A SDK 수신 코드|MCP 도구 등록과 원격 결과 수용 조건|

풀이 파일은 `build_lab/reference.py`입니다. 자신의 첫 구현과 실패를 기록한 뒤 풀이 시간에 비교합니다. import와 함수 인자는 제공되어 있으며, `NotImplementedError` 자리를 구현으로 바꿉니다.
</section>
<nav class="lesson-nav" aria-label="학습 단계"><a href="#materials">01 재료</a><a href="#langchain">02 Agent</a><a href="#graph">03 Graph</a><a href="#loop">04 Loop</a><a href="#protocols">05 연결</a><a href="#finish">06 완성</a></nav>
<section class="slide" id="materials">

<aside class="teacher-aside"><strong>강사의 한마디</strong><p>검사는 정답 파일을 찾는 절차가 아니라 내가 작성한 함수의 동작을 확인하는 도구입니다. 예상과 다른 입력 하나를 찾으면 고칠 지점이 선명해집니다.</p></aside>


## 재료를 먼저 읽습니다

정책 정본은 `course/common.py`의 `POLICIES`입니다. `build_lab/materials.py`는 이를 가져오며 State와 검토 기준을 정의합니다. 정책은 학습용 데이터이며 실제 회사 규정이 아닙니다. `inspect_draft`는 ID 일치와 팀 이름을 검사합니다. 사실성·문체·모든 업무 규칙을 평가하는 함수는 아닙니다.

통합 실행의 `topic`은 이미 분류된 업무 키입니다. `계정`과 `계정이 잠겼어요`는 다른 입력입니다. 자연어 문의에서 업무 키를 추출하는 분류 단계는 이번 통합에 포함하지 않습니다. LangChain의 자연어 시연과 범위를 구분합니다.

|State 필드|누가 준비하는가|읽는 시점|
|---|---|---|
|topic, contact|호출자|실행 시작|
|data|조회 노드|분기와 검토|
|draft, history, decision, visited|실행한 노드|결과 해석|

|입력|정책|예상 행동|
|---|---|---|
|정산 / 정상 회신 대상|P-01, 재무지원팀|조회하고 초안 작성|
|계정 / 정상 회신 대상|P-02, IT지원팀|다른 근거로 초안 작성|
|정산 / 공백 회신 대상|P-01|모델을 호출하지 않고 질문|
|없는업무 / 정상 회신 대상|없음|규정을 만들어 내지 않고 질문|

### 주피터로 진행하는 경우

환경 준비를 마친 `workshop` 폴더에서 실행합니다. 파일 실습은 주피터를 설치하지 않아도 됩니다.

```bash
uv sync --locked --group notebook
uv run --locked --group notebook jupyter lab notebooks/build-agent.ipynb
```

터미널에 표시된 로컬 주소를 열고 Python 3 커널에서 첫 환경 확인 셀을 실행합니다. 키는 기존 `.env`에서 읽습니다. 노트북에 키를 붙여 넣지 않습니다.

노트북에서는 조회·Agent·분기를 셀에서 작성하고 제공 그래프·루프를 실행해 관찰합니다. 완료한 함수를 `build_lab/student.py`의 같은 이름으로 옮겨 MCP·A2A 파일 실습을 이어갑니다. 셀을 바꿔도 Python 파일은 자동으로 바뀌지 않습니다.

옮긴 직후 아래 명령으로 파일의 세 구현을 확인합니다. 실패가 나오면 노트북 셀이 아니라 `build_lab/student.py`를 확인합니다.

```bash
uv run pytest tests/test_build_lab.py --build-student -q -k "lookup or agent or graph"
```

함수 셀을 수정하면 해당 셀과 아래 실행 셀을 다시 실행합니다. 마지막에는 커널을 재시작하고 처음부터 실행하여 오래된 함수가 남아 우연히 성공한 것은 아닌지 확인합니다. `build-agent-solution.ipynb`는 별도 풀이입니다.
</section>
<section class="slide" id="langchain">

## 1. 조회 도구와 Agent 구성 · 함께 15분 + 개인 15분

모델 없이 도구부터 만듭니다. `lookup_policy(topic)`는 공백을 제거한 주제로 정책을 찾고 JSON **문자열**을 반환합니다. 계정의 반환값을 파싱하면 다음 객체가 됩니다.

```json
{
  "found": true,
  "topic": "계정",
  "policy": {
    "id": "P-02",
    "team": "IT지원팀",
    "rule": "계정 잠금은 IT지원팀에 문의합니다."
  }
}
```

없는 정책은 found=false, policy=null입니다. topic은 정리한 입력을 유지합니다. API 재료는 `dict.get`, `str.strip`, `json.dumps(..., ensure_ascii=False)`입니다. docstring은 모델에게 도구 용도를 설명하므로 삭제하지 않습니다.

<<< ../../workshop/build_lab/student.py#lookup{python}

```bash
uv run pytest tests/test_build_lab.py --build-student -q -k lookup
```

이어서 `build_agent(model, policy_tool)`을 구현합니다. `create_agent(model=..., tools=[...], system_prompt=...)`로 구성한 Agent를 반환합니다. 생성 함수 안에서 실행까지 하지 않습니다. model과 policy_tool을 인자로 받는 이유도 설명합니다.

<<< ../../workshop/build_lab/student.py#agent{python}

지침에는 조회 시점, 담당 팀·근거 ID, 정책이 없을 때의 행동을 작성합니다. 정답 문장 자체를 지침에 넣지는 않습니다.

<div class="command-purpose">내 구현 실행</div>

```bash
uv run python -m build_lab.runner agent --topic 계정
```

**완료 기준:** 실제 기록에 학생 도구의 요청·실행·결과가 남고, P-02와 IT지원팀을 근거로 답합니다. 없는업무도 실행합니다. 답변이 매번 같다고 가정하지 않습니다.

도구가 맞는데 답변 ID가 다르면 어느 층의 실패인가요? 지침을 바꾼 실행과 코드를 바꾼 실행의 차이를 기록합니다. create_agent의 도구 호출 루프와 다음 단계의 업무 그래프를 구분합니다.

<details><summary>막힐 때 읽는 힌트</summary>

정책을 조회한 다음 found를 계산합니다. 없는 정책을 빈 문자열로 바꾸지 않습니다. tools에는 함수의 실행 결과가 아닌 함수 자체를 전달합니다. 도구를 직접 실행한 결과와 ToolMessage를 비교합니다.

</details>
</section>
<section class="slide" id="graph">

## 2. 그래프를 읽고 업무 분기를 구현합니다 · 함께 20분 + 개인 20분

Inquiry의 입력은 topic과 contact입니다. `guided.py`의 노드와 간선을 읽고 다음 경로를 그립니다. 공통 과제는 `student.py`의 `route_inquiry(state)`를 작성하는 것입니다. 정책이 있고 회신 대상이 공백이 아닐 때 draft, 그 외에는 ask를 반환합니다. `build_workflow`가 이 함수를 제공 그래프에 연결합니다.

```text
START → lookup → [정책 있음 AND 회신 대상이 공백 아님]
                  참 → draft → review → END
                  거짓 → ask → END
```

|노드|사용하는 재료|반환하는 State 변경|
|---|---|---|
|lookup|json.loads(lookup(state['topic']))|data, visited=['lookup']|
|ask|추가 확인 문장|decision='ask', draft, history=[], visited에 ask 추가|
|draft|generate(state['topic'])|draft, visited에 draft 추가|
|review|refine(state['draft'], state['data'], limit)|draft, history, decision=status, visited에 review 추가|

노드는 바꿀 필드만 반환합니다. visited는 자동 누적 reducer가 없으므로 기존 목록에 이름을 더한 새 목록을 반환합니다. 병렬 노드가 같은 필드를 쓰는 문제는 이 직렬 그래프의 범위를 벗어납니다.

코드를 읽을 때 `StateGraph(Inquiry)`는 상태 형식, add_node는 단계 등록, add_edge는 연결, add_conditional_edges는 조건 분기, compile은 실행할 그래프 생성으로 해석합니다. 조건 함수의 재료는 `state['data']['found']`와 `state.get('contact', '').strip()`입니다. 전체 그래프를 새로 구성하는 것은 선택 심화입니다.

<div class="command-purpose">내 구현 실행</div>

```bash
uv run pytest tests/test_build_lab.py --build-student -q -k graph
uv run python -m build_lab.runner graph --topic 정산 --contact "   "
uv run python -m build_lab.runner graph --topic 계정 --contact user@example.test
```

graph 단계는 제공 검토 함수로 한 번만 검사합니다. 제공 수정 루프는 다음 단계에서 연결해 관찰합니다. 공백 입력은 trace가 비어 있고 visited가 lookup→ask여야 합니다. 정상 입력은 lookup→draft→review를 거칩니다.

**완료 기준:** 결과 문자열뿐 아니라 실제 모델·수정 함수가 호출되지 않아야 하는 경로를 설명합니다. 검사는 compile된 그래프를 실행해 호출 횟수와 방문 경로를 확인합니다.

**변경 요청:** 연락처를 조회 전에 검사하면 무엇이 달라질까요? 조회 횟수와 질문에 사용할 수 있는 정보의 차이를 설명합니다. 익숙한 사람은 해당 경로를 별도로 구현합니다.
</section>
<section class="slide" id="loop">

## 3. 제공 루프를 관찰하고 하네스 활용을 설명합니다

공통 과정에서는 student.py의 refine_answer를 그대로 둡니다. 이 함수가 guided.py의 제공 루프를 호출합니다. 모델이 만든 초안을 검사하고 실제 수정 입력으로 무엇을 전달하는지 읽습니다.

<div class="command-purpose">내 구현 실행</div>

```bash
uv run python -m build_lab.runner workflow --topic 계정
```

최초 답변이 이미 통과하면 수정은 0회입니다. 노트북의 '확인 완료' 초안 관찰 또는 Harness 모듈의 revisions 예제를 실행하여 실제 피드백과 다음 초안도 비교합니다. 같은 문자열 반복, 예산 0, 마지막 수정 성공의 예상 결과를 먼저 말합니다.

공통 개인 활동은 [Loop·Graph Engineering의 실제 담론과 활용](./engineering#task)의 작업 정의입니다. Codex·Claude Code에 무엇을 읽히고, 어디를 고치게 하고, 어떤 검증 결과로 다음 행동을 판단할지 작성합니다. 코딩 에이전트 계정이 없으면 활동지와 비교 시연으로 진행합니다. 업무 수정 루프와 코딩 하네스의 반복은 제어 대상이 다릅니다.

<details><summary>선택 심화: 수정 루프를 직접 구현하기</summary>

### 구현 계약

`refine_answer(draft, data, revise, limit)`은 status, draft, history를 반환합니다. revise는 실제 모델을 호출하는 제공 함수입니다. 학생은 호출 시점과 넘길 피드백을 결정합니다. 이 심화를 선택한 경우에만 제공 루프 호출 대신 직접 작성합니다.

|조건|요구한 행동|
|---|---|
|검토 통과|passed, 수정하지 않음|
|직전과 같은 실패 초안|stalled, 추가 수정하지 않음|
|수정 예산 소진|held, 추가 수정하지 않음|
|그 외 실패|현재 draft와 feedback으로 revise 호출|

history 항목은 `{'attempt': 0, 'draft': '초안', 'feedback': [...]}`입니다. 최초 검토도 남기므로 수정 상한 2에서 검토는 최대 3회입니다. 상한은 0~5 정수이며 불리언도 거부합니다. 그 외 값은 ValueError입니다.

성공→정체→예산 순서가 마지막 수정에서 성공한 경우에 어떤 차이를 만드는지 설명합니다. 이후 range(limit + 1), inspect_draft, 이전 history 항목, revise 호출을 조합합니다.

<div class="command-purpose">내 구현 실행</div>

```bash
uv run pytest tests/test_build_lab.py --build-student -q -k loop
uv run python -m build_lab.runner workflow --topic 계정
```

**부족한 초안을 직접 넣습니다.** 노트북에서는 '확인 완료'를 초기 draft로 전달하고 feedback이 다음 모델 입력으로 넘어가는지 봅니다. 최초 답변이 이미 통과한 실행만으로 수정 경로를 확인했다고 할 수 없습니다.

**검토의 한계:** 'IT지원팀 P-02가 맞는지는 모릅니다'도 이름·ID 검사에는 통과할 수 있습니다. 직접 반례를 만들고 자동 검사와 사람이 읽는 판단을 구분합니다. 기준을 보완한다면 어떤 오탐을 새로 만들지도 적습니다.

DeepAgents와 비교할 때에는 이 수동 루프가 자동으로 프레임워크에 들어간다고 설명하지 않습니다. 상태·도구·수정 예산 중 프레임워크가 제공하는 것과 업무 코드가 책임지는 것을 나눕니다.

</details>
</section>
<section class="slide" id="protocols">

## 4. 내가 만든 도구를 MCP로 공개합니다

MCP 모듈 실습 시간에 진행합니다. `build_mcp_server(policy_tool)`에서 MCPServer를 생성하고 `server.tool()(policy_tool)`로 학생 조회 함수를 등록한 뒤 서버를 반환합니다.

<div class="command-purpose">내 구현 실행</div>

```bash
uv run pytest tests/test_build_lab.py --build-student -q -k mcp
uv run python -m build_lab.runner mcp --topic 계정
```

처음에는 미구현 함수를 가리키는 NotImplementedError가 나옵니다. 설치 실패와 구분합니다. 첫 검사는 SDK 내부 경로입니다. 두 번째는 학생 서버를 별도 프로세스로 띄워 실제 HTTP로 목록과 결과를 가져옵니다. 서버 기동·종료는 제공 실행기가 맡습니다. 함수 반환값과 HTTP 응답의 content 포장을 비교합니다.

도구 설명을 지우거나 인자 이름을 바꾸면 client 계약은 어떻게 달라질까요? 기본 구현 후 MCP 모듈의 재시작·업무 키 실험을 이어갑니다. Stateless의 의미를 업무 데이터 삭제로 해석하지 않습니다.

## 5. 원격 검토를 받아도 바로 승인하지 않습니다

A2A 모듈 실습 시간에 `accept_review(state, artifact, request_id, version)`을 구현합니다. submitted·working은 pending입니다. completed 외의 종료 상태는 held입니다. completed이면 요청 ID, 양의 정수 버전, artifact 버전 일치, passed is True를 확인한 경우만 accepted입니다. 빈 요청 ID와 bool 버전은 거부합니다.

<div class="command-purpose">내 구현 실행</div>

```bash
uv run pytest tests/test_build_lab.py --build-student -q -k a2a
uv run python -m build_lab.runner complete --topic 계정
```

완성 실행은 **학생 MCP 조회 → 제공 Graph와 학생 분기 → 학생 LangChain Agent → 제공 수정 루프 → 제공 A2A 서버 → 학생 수용 판단**입니다. 선택 심화에서 그래프·루프를 교체했다면 그 구현이 연결됩니다. 모델과 서버는 실제로 실행합니다. 검토가 통과하지 않으면 그 이유를 읽고 보류합니다.

A2A 수신부와 검토 서버는 제공 코드입니다. 서버를 처음부터 구현했다고 말하지 않습니다. A2A 모듈의 executor·Task·Artifact 설명과 대조합니다. ACP는 연결 대상과 규약의 차이를 설명하는 범위입니다.
</section>
<section class="slide" id="finish">

## 완성의 증거를 남깁니다

<details class="instructor-note"><summary>강사용 진행 노트 · 실습 도움</summary>

입력과 반환 계약을 읽고 한 함수를 직접 완성하도록 돕습니다. 앞 단계가 막히면 학생 파일을 보관한 뒤 필요한 함수만 보완합니다. 모든 코드를 풀이로 교체하거나 별도 보고서를 작성하게 하지 않습니다.

</details>

```bash
uv run pytest tests/test_build_lab.py --build-student -q
```

`--build-student`를 빼면 기준 풀이 검사입니다. 학생 구현을 검증할 때는 이 옵션을 유지합니다. 테스트의 모델 대역은 tests에만 있으며 runner의 실제 실행을 대체하지 않습니다. 자신의 코드에서 정상·추가 확인·보류가 각각 어떤 조건으로 결정되는지 확인합니다. 실행마다 runs/build-단계-고유값.json으로 따로 저장합니다. 실제 문장을 읽고 근거와 대조합니다.

풀이 시간에는 reference.py를 열어 노드 경계, 조건 순서, 도구 인자, 수용 계약을 비교합니다.

보류 기록은 학생의 수용 함수에 **이전 버전의 결과**를 넣어 확인할 수 있습니다. 다음 입력은 실제 서버의 응답 로그가 아닌, 계약 확인을 위해 직접 구성한 반례입니다. 현재 요청 버전은 2인데 결과 버전은 1이므로 `held`가 기대 결과입니다. 출력과 예상한 보류 이유를 비교합니다.

```bash
uv run python -c "from build_lab.student import accept_review; print(accept_review('completed', {'request_id': 'case-1', 'version': 1, 'passed': True}, 'case-1', 2))"
```

이 결과를 실제 모델·MCP·A2A를 연결한 정상 실행 결과와 비교합니다. 의도한 실패를 얻으려고 모델이 틀릴 때까지 재호출하지 않습니다.

다음은 기준 풀이의 통합 실행이며 학생 구현의 성공을 의미하지 않습니다.

```bash
uv run python -m build_lab.reference complete --topic 계정
```

### 마친 뒤 설명할 수 있어야 하는 것

통합 시간에는 [업무 별칭을 추가하는 독립 변경](./wrap#practice)까지 수행합니다. 새 요구를 보고 수정 위치를 고르고, 변경 전 실패와 기존 동작의 유지 여부를 확인합니다. 다섯 구현의 계약을 그대로 옮기는 것과 새로운 요구에 맞게 재조합하는 것을 따로 평가합니다.

핵심은 도구·LangChain Agent·업무 분기를 직접 만들고 실행 흐름을 설명하는 능력입니다. 그래프·루프 구조의 전체 작성은 선택 심화이고, Loop·Graph Engineering은 실제 담론을 읽고 반복 작업과 여러 역할을 조직하는 설계 판단까지 다룹니다. MCP 도구 공개와 A2A 결과 수용도 직접 연결합니다. 장기 메모리, 장애 후 복구, 운영 인증, 분산 재시도까지 하루에 숙련하는 과정은 아닙니다. HITL·Skills·DeepAgents는 개념과 제공 예제를 비교하고 구현 심화는 별도 과제로 이어갑니다.

### 더 연습하려면

- [LangChain Academy](https://academy.langchain.com/courses/intro-to-langgraph): 단순 그래프부터 체인·라우터·Agent·메모리까지 순서대로 연습할 수 있습니다.
- [LangGraph 101](https://github.com/langchain-ai/langgraph-101): 기본 노트북과 심화 패턴을 골라 실습할 수 있습니다.
- [환경·과제 설계](https://www.langchain.com/blog/building-agent-environments-and-tasks): 자신의 업무로 과제를 만들 때 입력·환경·판정 기준을 정하는 방법을 읽습니다.

외부 실습을 실행할 때는 해당 자료의 의존성과 설치 안내를 확인합니다.
</section>

<section class="slide" id="recovery">

## 앞 단계에서 막혔을 때

현재 student.py를 다른 이름으로 복사해 보존합니다. 배포 ZIP의 README에 있는 복귀 표를 보고, reference.py에서 미완료인 앞 단계 함수만 같은 이름으로 옮깁니다. 파일 전체를 덮어쓰지 않습니다. 제공받은 함수와 직접 작성한 함수를 직접 작성한 함수와 구분합니다.

|진행할 단계|먼저 필요한 함수|
|---|---|
|Graph|lookup_policy, build_agent|
|수정 루프 관찰|위 두 함수와 route_inquiry|
|MCP|lookup_policy|
|A2A 통합|lookup_policy, build_agent, route_inquiry, build_mcp_server|

해당 단계의 검사 명령으로 재개합니다. 완성 예제를 관찰한 것만으로 학생 프로젝트 구현을 완료했다고 표시하지 않습니다.
</section>

<nav class="chapnav"><a href="../toc">전체 목차</a></nav>
</div></div>
