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

처음에는 조회 함수와 Agent 구성을 만들고, 다음 수업에서 분기와 서버 연결을 추가합니다. 현재 수업의 단계만 진행한 뒤 해당 장의 풀이로 돌아옵니다.

<details class="instructor-note"><summary>강사용 예상 시간 · 본 수업에 포함</summary>

이 페이지는 각 수업의 구현 시간에 나누어 사용합니다. 예상 구현·연결 시간은 첫 파일·재료 안내를 포함해 LangChain 30분, LangGraph 30분, MCP 30분, A2A 20분이며 각 세션 배정에 포함됩니다. 전체를 한 번에 진행하는 별도 세션이 아닙니다.

</details>

</section>
<section class="slide" id="first-code">

## 첫 구현: 파일을 열고 작성할 함수를 찾습니다

<p class="section-time">예상 2분 · 해당 수업 시간에 포함</p>

LangChain 장의 개념 설명을 마친 뒤 진행합니다. 먼저 편집기에서 압축을 푼 `workshop` 폴더의 `build_lab/student.py`를 엽니다. 오늘 직접 수정할 파일입니다.

1. `def lookup_policy`를 찾습니다. 제공된 search_policy를 호출하도록 작성하고, 도구의 용도를 docstring으로 설명합니다.
2. 함수 안의 `raise NotImplementedError(...)`는 아직 구현하지 않았다는 표시입니다. 이 줄을 지우고 자신의 코드를 작성합니다. 함수 이름과 인자는 그대로 둡니다.
3. 아래 재료를 읽고 함수를 완성한 뒤, 바로 아래 실행 명령을 실행합니다. 아직 다른 함수는 수정하지 않습니다.

`build_lab/reference.py`는 풀이입니다. 먼저 자신의 코드를 실행해 본 뒤 막힌 부분이나 풀이를 비교할 때 엽니다.

</section>
<section class="slide" id="materials">

<aside class="teacher-aside"><strong>강사의 한마디</strong><p>검사는 정답 파일을 찾는 절차가 아니라 내가 작성한 함수의 동작을 확인하는 도구입니다. 예상과 다른 입력 하나를 찾으면 고칠 지점이 선명해집니다.</p></aside>


## 재료를 먼저 읽습니다

<p class="section-time">예상 3분 · 해당 수업 시간에 포함</p>

정책 데이터는 제공된 `data/policies.csv`에 있습니다. `course/policy_store.py`의 `search_policy(topic)`이 파일 읽기·공백 처리·결과 JSON 생성을 맡습니다. 학습자는 CSV 파서나 JSON 조립 코드를 작성하지 않습니다.

|업무명|정책 ID|담당 팀|
|---|---|---|
|정산|P-01|재무지원팀|
|계정|P-02|IT지원팀|

먼저 CSV의 두 행을 읽습니다. 실습에서는 이 데이터 접근 함수를 감싸 모델에게 보여줄 조회 도구를 만들고, Agent에 연결합니다. 원본 CSV를 바꾸면 조회 결과도 달라집니다. 기본 실습은 제공된 두 행으로 진행합니다.

수업은 VS Code와 Python 파일로 진행합니다. `build_lab/student.py`에 구현하고 `labs/`의 실행 파일에서 질문·입력값을 바꿉니다. 노트북으로 옮기는 단계는 없습니다.
</section>
<section class="slide" id="langchain">

## 1. 조회 도구와 Agent 구성

실행 파일은 `labs/langchain.py`입니다. `question`을 수정하면 모델에 보내는 질문이 바뀝니다. 조회 예측 → 실행 → messages 목록 읽기 순서로 진행합니다.

<p class="section-time">예상 25분 · 해당 수업 시간에 포함</p>

|이번에 할 일|구체적인 작업|
|---|---|
|수정 파일|`build_lab/student.py`|
|구현 함수|`lookup_policy`: 제공 조회 함수 연결. `build_agent`: 도구 변환·모델 연결·지침 작성|
|제공되는 것|CSV 데이터, `search_policy`, 모델 설정, 실행 파일|
|실행 순서|아래 조회 실행으로 두 정책과 미등록 업무 확인 → Agent 실행으로 실제 도구 호출 확인|
|완료 모습|계정 문의에서 도구 결과 P-02·IT지원팀을 읽고 답함. 미등록 업무에는 담당 팀을 지어내지 않음|



제공 함수부터 호출해 반환값을 확인합니다. 아래 명령은 모델 없이 실행되며, 계정의 담당 팀과 정책 ID를 출력합니다.

```bash
uv run python -c "from course.policy_store import search_policy; print(search_policy('계정'))"
```

결과의 `policy`에서 `P-02`와 `IT지원팀`을 찾습니다. 없는 업무는 `found=false`, `policy=null`로 돌아옵니다. **이 결과 JSON은 제공 함수가 만듭니다. 학습자가 옮겨 적거나 조립할 데이터가 아닙니다.**

이제 `lookup_policy(topic)` 안에서 `search_policy(topic)`을 호출하고 결과를 그대로 반환합니다. docstring에는 언제 이 도구를 쓰는지와 어떤 업무명을 받는지 설명합니다. 제공 함수는 데이터 접근을, 작성할 함수는 모델에 공개할 도구의 역할을 맡습니다.

<<< ../../workshop/build_lab/student.py#lookup{python}

작성한 파일을 저장하고 아래 명령으로 실행합니다. `labs/lookup.py`의 세 입력과 출력 결과를 비교합니다. 아직 뒤 단계 함수는 미완성이어도 됩니다.

<div class="command-purpose">내 조회 함수 실행</div>

```bash
uv run python -m labs.lookup
```



정산·계정의 담당 팀과 없는 업무의 결과를 확인했으면 이어서 `build_agent(model, policy_tool)`을 구현합니다. 먼저 `tool(policy_tool)`로 LangChain 도구 객체를 만들고 `tools` 목록에 넣습니다. `create_agent(model=..., tools=[...], system_prompt=...)`로 구성한 Agent를 반환합니다. 생성 함수 안에서 실행까지 하지 않습니다. 다른 모델이나 조회 도구를 연결하려면 어디를 바꾸면 될까요? 함수 안에 고정하지 않고 model과 policy_tool을 인자로 받는 이유를 생각해 봅니다.

<<< ../../workshop/build_lab/student.py#agent{python}

지침에는 조회 시점, 담당 팀·근거 ID, 정책이 없을 때의 행동을 작성합니다. 정답 문장 자체를 지침에 넣지는 않습니다.

<div class="command-purpose">내 구현 실행</div>

```bash
uv run python -m labs.langchain
```

**완료 기준:** 실제 기록에 학생 도구의 요청·실행·결과가 남고, P-02와 IT지원팀을 근거로 답합니다. 없는업무도 실행합니다. 답변이 매번 같다고 가정하지 않습니다.

도구는 P-02를 반환했는데 최종 답변은 P-01이라고 합니다. 조회 함수와 모델의 답변 중 어디에서 처음 달라졌나요? 지침을 바꿨을 때와 코드를 바꿨을 때 각각 어떤 결과가 달라지는지 비교합니다. create_agent의 도구 호출 루프와 다음 단계의 업무 그래프를 구분합니다.

<details><summary>막힐 때 읽는 힌트</summary>

조회 함수는 `search_policy`의 반환값을 그대로 돌려줍니다. Agent의 tools에는 `tool(policy_tool)`로 만든 도구 객체를 넣습니다. 도구를 직접 실행한 결과와 ToolMessage를 비교합니다.

</details>

[수업으로 돌아가기: LangChain 풀이](./langchain#solution)

</section>
<section class="slide" id="graph">

## 2. 그래프를 읽고 업무 분기를 구현합니다

<p class="section-time">예상 30분 · 해당 수업 시간에 포함</p>

**이번 과제는 `route_inquiry` 한 함수를 완성하는 것입니다.** 앞 개념의 `course/graph_lab.py`는 읽는 예제이고, 직접 수정할 파일은 `build_lab/student.py`입니다.

1. `route_inquiry(state)`의 `raise NotImplementedError(...)`를 자신의 조건문으로 바꿉니다.
2. `state['data']['found']`가 참이고 `contact`가 공백이 아닐 때 `"draft"`, 나머지는 `"ask"`를 반환합니다.
3. `labs/graph.py`에서 아래 입력을 하나씩 설정하고 실행합니다.

```bash
uv run python -m labs.graph
```

|topic / contact|터미널에서 확인할 `state.visited`|성공 판단|
|---|---|---|
|계정 / 정상 주소|`['lookup', 'draft', 'review']`|초안 생성과 검토로 진입함|
|계정 / 빈 문자열|`['lookup', 'ask']`|`state.decision='ask'`, `trace=[]`|
|계정 / 공백 세 칸|`['lookup', 'ask']`|공백도 정보 부족으로 처리함|
|없는업무 / 정상 주소|`['lookup', 'ask']`|규정이 없으면 모델을 호출하지 않음|

**네 입력이 모두 기대 경로로 가면 분기 구현 완료입니다.** 정상 경로에서 검토 결과가 `held`라면 `state.history`의 이유와 초안을 확인합니다. 모델 인증·네트워크 오류는 성공 결과가 아니므로 해결 후 다시 실행합니다. 그래프 조립과 조회·초안·검토 노드는 제공됩니다.



LangGraph 장에서 State·노드·분기를 배운 뒤 진행합니다. 여기서는 `build_lab/materials.py`의 `Inquiry`가 이 프로그램의 상태 형식입니다. `topic`은 업무명, `contact`는 회신 대상, `data`는 조회 결과, `draft`는 답변 초안입니다. `history`는 검토 이력, `decision`은 처리 결과, `visited`는 지나간 노드입니다.

`guided.py`의 `build_workflow`가 작성한 분기 함수를 다음 그래프에 연결합니다. 아래 표에서 각 노드가 어떤 State를 반환하는지 확인합니다.

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

uv run python -m labs.graph
```

`labs/graph.py`에서 `contact`를 `"   "`로 바꿔 실행한 뒤 원래 주소로 되돌려 비교합니다. `topic`도 같은 파일에서 수정합니다. graph 단계는 제공 검토 함수로 한 번만 검사합니다. 제공 수정 루프는 다음 단계에서 연결해 관찰합니다. 공백 입력은 trace가 비어 있고 visited가 lookup→ask여야 합니다. 정상 입력은 lookup→draft→review를 거칩니다.

**완료 기준:** 결과 문자열뿐 아니라 실제 모델·수정 함수가 호출되지 않아야 하는 경로를 설명합니다. 검사는 compile된 그래프를 실행해 호출 횟수와 방문 경로를 확인합니다.

**변경 요청:** 답장 주소가 없는 문의는 규정 조회 전에 바로 주소부터 묻도록 바꾼다고 가정합니다. 조회를 한 번 줄일 수 있을까요? 대신 규정에 대한 어떤 안내를 아직 할 수 없을까요? 여유가 있으면 분기 위치를 옮겨 실행해 봅니다.

[수업으로 돌아가기: LangGraph 풀이](./graph#solution)

</section>

<section class="slide" id="loop">

## 3. 제공 루프를 관찰하고 하네스 활용을 설명합니다

<p class="section-time">예상 10분 · 해당 수업 시간에 포함</p>

공통 과정에서는 student.py의 refine_answer를 그대로 둡니다. 이 함수가 guided.py의 제공 루프를 호출합니다. 모델이 만든 초안을 검사하고 실제 수정 입력으로 무엇을 전달하는지 읽습니다.

<div class="command-purpose">내 구현 실행</div>

```bash
uv run python -m labs.harness
```

최초 답변이 이미 통과하면 수정은 0회입니다. Harness 모듈의 revisions 예제를 실행하여 실제 피드백과 다음 초안도 비교합니다. 같은 문자열 반복, 예산 0, 마지막 수정 성공의 예상 결과를 먼저 말합니다.

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

uv run python -m labs.harness
```

**부족한 초안을 직접 넣습니다.** 직접 구현한 `refine_answer`에 '확인 완료'를 초기 draft로 전달하고 feedback이 다음 모델 입력으로 넘어가는지 봅니다. 최초 답변이 이미 통과한 실행만으로 수정 경로를 확인했다고 할 수 없습니다.

**검토의 한계:** 'IT지원팀 P-02가 맞는지는 모릅니다'도 이름·ID 검사에는 통과할 수 있습니다. 직접 반례를 만들고 자동 검사와 사람이 읽는 판단을 구분합니다. 기준을 보완한다면 어떤 오탐을 새로 만들지도 적습니다.

DeepAgents와 비교할 때에는 이 수동 루프가 자동으로 프레임워크에 들어간다고 설명하지 않습니다. 상태·도구·수정 예산 중 프레임워크가 제공하는 것과 업무 코드가 책임지는 것을 나눕니다.

</details>

[수업으로 돌아가기: Harness 풀이](./harness#solution)

</section>
<section class="slide" id="protocols">

## 4. 내가 만든 도구를 MCP로 공개합니다

<p class="section-time">예상 30분 · 해당 수업 시간에 포함</p>

|이번에 할 일|구체적인 작업|
|---|---|
|수정 파일·함수|`build_lab/student.py`의 `build_mcp_server(policy_tool)`|
|구현할 것|MCPServer 생성 → 받은 함수를 도구로 등록 → 서버 반환|
|제공되는 것|앞 장의 조회 함수, HTTP 서버 기동·종료, 클라이언트|
|실행|`labs/mcp.py`의 topic을 계정으로 설정하고 아래 명령 실행|
|완료 모습|`transport`의 도구 목록에 lookup_policy가 보이고, `data.policy`에 P-02·IT지원팀이 있음. 없는업무는 found=False|



MCP 모듈 실습 시간에 진행합니다. `build_mcp_server(policy_tool)`에서 MCPServer를 생성하고 `server.tool()(policy_tool)`로 학생 조회 함수를 등록한 뒤 서버를 반환합니다.

<div class="command-purpose">내 구현 실행</div>

```bash

uv run python -m labs.mcp
```

처음에는 미구현 함수를 가리키는 NotImplementedError가 나옵니다. 설치 실패와 구분합니다. 이 실행은 학생 서버를 별도 프로세스로 띄워 실제 HTTP로 목록과 결과를 가져옵니다. 서버 기동·종료는 제공 실행기가 맡습니다. 함수 반환값과 HTTP 응답의 content 포장을 비교합니다.

도구의 인자 이름을 topic에서 category로 바꿨습니다. 클라이언트가 여전히 topic을 보내면 호출이 될까요? 서버가 받는 이름과 클라이언트가 보내는 이름을 비교합니다. 기본 구현 후 MCP 모듈의 재시작·업무 키 실험을 이어갑니다. Stateless의 의미를 업무 데이터 삭제로 해석하지 않습니다.

[수업으로 돌아가기: MCP 풀이](./mcp#solution)

</section>
<section class="slide" id="a2a">

## 5. 원격 검토를 받아도 바로 승인하지 않습니다

<p class="section-time">예상 20분 · 해당 수업 시간에 포함</p>

|이번에 할 일|구체적인 작업|
|---|---|
|수정 파일·함수|`build_lab/student.py`의 `accept_review`|
|구현할 것|작업 상태·요청 ID·버전·통과 여부를 검사해 pending / held / accepted 반환|
|제공되는 것|원격 검토 서버와 클라이언트, 앞 장에서 연결한 Agent|
|실행|아래 `labs.a2a` 명령으로 실제 통합 실행|
|완료 모습|현재 요청의 검토가 completed이고 ID·버전·passed가 모두 맞으면 `review.decision='accepted'`. 이전 버전 결과는 held|

반례는 터미널 명령을 더 조합하지 않고 자신의 함수를 직접 호출해 확인합니다. 다음 코드를 `labs/review_cases.py`에 저장하고 `uv run python -m labs.review_cases`로 실행합니다.

```python
from build_lab.student import accept_review

artifact = {"request_id": "case-1", "version": 1, "passed": True}
print(accept_review("working", artifact, "case-1", 1))    # pending
print(accept_review("completed", artifact, "case-1", 1))  # accepted
print(accept_review("completed", artifact, "case-1", 2))  # held
print(accept_review("completed", artifact, "other", 1))   # held
```



A2A 모듈 실습 시간에 `accept_review(state, artifact, request_id, version)`을 구현합니다. submitted·working은 pending입니다. completed 외의 종료 상태는 held입니다. completed이면 요청 ID, 양의 정수 버전, artifact 버전 일치, passed is True를 확인한 경우만 accepted입니다. 빈 요청 ID와 bool 버전은 거부합니다.

<div class="command-purpose">내 구현 실행</div>

```bash

uv run python -m labs.a2a
```

완성 실행은 **학생 MCP 조회 → 제공 Graph와 학생 분기 → 학생 LangChain Agent → 제공 수정 루프 → 제공 A2A 서버 → 학생 수용 판단**입니다. 선택 심화에서 그래프·루프를 교체했다면 그 구현이 연결됩니다. 모델과 서버는 실제로 실행합니다. 검토가 통과하지 않으면 그 이유를 읽고 보류합니다.

A2A 수신부와 검토 서버는 제공 코드입니다. 서버를 처음부터 구현했다고 말하지 않습니다. A2A 모듈의 executor·Task·Artifact 설명과 대조합니다. ACP는 연결 대상과 규약의 차이를 설명하는 범위입니다.

[수업으로 돌아가기: A2A 풀이](./a2a#solution)

</section>
<section class="slide" id="finish">

## 전체 실행 결과를 확인합니다

<p class="section-time">예상 10분 · 해당 수업 시간에 포함</p>

<details class="instructor-note"><summary>강사용 진행 노트 · 실습 도움</summary>

입력과 반환 계약을 읽고 한 함수를 직접 완성하도록 돕습니다. 앞 단계가 막히면 학생 파일을 보관한 뒤 필요한 함수만 보완합니다. 모든 코드를 풀이로 교체하거나 별도 보고서를 작성하게 하지 않습니다.

</details>



자동 회귀 검사는 개발용 tests에 있습니다. 수업에서는 실행 파일의 입력을 바꾸고 자신의 코드가 반환한 결과를 확인합니다. 자신의 코드에서 정상·추가 확인·보류가 각각 어떤 조건으로 결정되는지 확인합니다. 결과는 터미널에 출력됩니다. 실제 문장을 읽고 근거와 대조합니다.

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
<aside class="discussion-prompt"><strong>생각거리 · 여유가 있으면 +3분</strong><p>정산과 계정 검사는 모두 통과했습니다. 하지만 코드에는 “정산이면 재무지원팀, 나머지는 IT지원팀”이라고 적혀 있습니다.<br><br><strong>“없는업무”를 넣으면 어떤 답이 나올까요?</strong> 이 문제를 잡으려면 검사에 어떤 입력을 추가해야 할까요?</p></aside>

<details class="instructor-note"><summary>강사용 토론 길잡이</summary>

없는 업무도 IT지원팀이라고 답하게 됩니다. 미등록 업무에서 found=false와 policy=null이 나오는지 검사합니다. 기존 정상 입력도 유지해야 합니다.

한 답을 빨리 받기보다, 반대 선택이 더 나아지는 조건을 하나 더 묻습니다. 별도 기록이나 제출은 요구하지 않습니다. 기본 배정에 추가하는 선택 활동이므로 다음 섹션의 시간을 조절합니다.

</details>

</section>

<section class="slide" id="recovery">

## 앞 단계에서 막혔을 때

<p class="section-time">필요할 때 약 3분 · 다음 활동에서 조절</p>

앞 단계 구현이 끝나지 않아 다음 실습을 실행할 수 없을 때 사용합니다. 먼저 `build_lab/student.py`를 `student-backup.py`로 복사해 자신의 작업을 보관합니다. 아래 표에서 필요한 함수를 확인하고, `build_lab/reference.py`의 같은 이름 함수로 미완료 함수만 교체합니다. 파일 전체를 덮어쓰거나 현재 배우는 단계의 함수까지 교체하지 않습니다.

|진행할 단계|먼저 필요한 함수|
|---|---|
|Graph|lookup_policy, build_agent|
|수정 루프 관찰|위 두 함수와 route_inquiry|
|MCP|lookup_policy|
|A2A 통합|lookup_policy, build_agent, route_inquiry, build_mcp_server|

필요한 함수를 보완했다면 원래 진행하던 실습으로 돌아가 해당 단계의 실행 명령을 실행합니다. 직접 작성하다 막힌 부분은 보관한 파일과 풀이를 비교하며 다시 살펴봅니다.
</section>

<nav class="chapnav"><a href="../toc">전체 목차</a></nav>
</div></div>
