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

처음에는 조회 함수와 Agent 구성을 만들고, 다음 수업에서 분기와 서버 연결을 추가합니다. 노트북에서 현재 수업의 번호까지만 진행하고 교재의 풀이를 비교합니다.

<details class="instructor-note"><summary>강사용 예상 시간 · 본 수업에 포함</summary>

이 페이지는 각 수업의 구현 시간에 나누어 사용합니다. 예상 구현·연결 시간은 첫 파일·재료 안내를 포함해 LangChain 30분, LangGraph 30분, MCP 30분, A2A 20분이며 각 세션 배정에 포함됩니다. 전체를 한 번에 진행하는 별도 세션이 아닙니다.

</details>

</section>
<section class="slide" id="first-code">

## 실습 노트북을 엽니다

환경설정에서 실행한 JupyterLab에서 `notebooks/build-agent.ipynb`를 엽니다. **코드는 이 노트북의 셀에 작성합니다.** 첫 환경 확인 셀부터 Shift+Enter로 실행하고, 현재 수업의 번호까지 진행합니다.

함수 정의 셀의 `raise NotImplementedError(...)`를 자신의 구현으로 바꿉니다. 함수를 수정하면 정의 셀을 실행한 뒤 아래 연결·실행 셀도 다시 실행합니다. Python 파일로 복사하지 않습니다. 풀이 시간에는 `build-agent-solution.ipynb`의 같은 번호를 비교합니다.

</section>
<section class="slide" id="materials">

## 제공되는 재료

`data/policies.csv`의 정산은 P-01·재무지원팀, 계정은 P-02·IT지원팀입니다. `search_policy(topic)`이 CSV 읽기와 결과 생성을 맡습니다. 노트북 첫 셀에서 가져오므로 데이터 파서를 작성할 필요는 없습니다.

</section>
<section class="slide" id="langchain">

## 1. 조회 도구와 Agent 구성

|노트북에서 할 일|완료 확인|
|---|---|
|1A의 lookup_policy에 search_policy 연결|바로 아래 셀에서 정산·계정 조회, 없는업무 found=False|
|1B의 build_agent에서 tool 변환과 create_agent 구성|모델·도구·지침을 넣어 Agent 반환|
|다음 실행 셀에서 질문 전달|도구 요청·결과·최종 답변에서 P-02·IT지원팀 확인|

docstring에는 도구가 언제 필요한지 설명합니다. 지침에는 조회 시점과 정책이 없을 때의 행동을 작성합니다. 질문을 없는업무로 바꾸어 담당 팀을 추측하지 않는지 확인합니다. 출력은 실행한 셀 바로 아래에 남습니다.

</section>
<section class="slide" id="graph">

## 2. 노트북에서 업무 분기를 구현합니다

**`build-agent.ipynb`의 ‘2. 업무 Graph’로 이동합니다.** 앞 장의 조회·Agent 셀을 실행한 같은 커널에서 이어갑니다.

1. `route_inquiry` 셀을 완성합니다. 정책이 있고 회신 대상이 공백이 아니면 `"draft"`, 그 외에는 `"ask"`를 반환합니다.
2. 정의 셀을 실행한 뒤 다음 연결 셀을 실행합니다. 제공 `build_workflow`가 자신의 함수를 그래프에 연결합니다.
3. **‘2A. 실행 입력과 성공 기준’** 아래 셀의 `topic`과 `contact`를 바꿔 Shift+Enter로 실행합니다.

```python
topic = "계정"
contact = "   "
model_calls.clear()
result = graph.invoke({"topic": topic, "contact": contact})
print("방문:", result["visited"])
print("판정:", result["decision"])
print("모델 호출:", len(model_calls))
print("답변:", result["draft"])
```

|topic / contact|기대 방문 경로|완료 확인|
|---|---|---|
|계정 / 정상 주소|lookup → draft → review|초안 생성과 검토 실행|
|계정 / 빈 문자열|lookup → ask|판정 ask, 모델 호출 0|
|계정 / 공백 세 칸|lookup → ask|공백도 정보 부족으로 판단|
|없는업무 / 정상 주소|lookup → ask|규정이 없으면 모델 호출 0|

네 입력이 기대 경로로 가면 분기 구현 완료입니다. 정상 경로에서 검토가 held이면 `result['history']`의 실패 이유를 읽습니다. API 오류로 셀이 실패했다면 연결 문제를 해결하고 다시 실행합니다.

노트북의 State는 `Inquiry`입니다. `data`는 조회 결과, `draft`는 초안, `visited`는 방문 이력입니다. 조회·초안·검토 노드는 제공되며, 이번에 구현하는 함수는 `route_inquiry`입니다. 전체 그래프 조립은 선택 심화입니다.

</section>

<section class="slide" id="loop">

## 3. 제공 수정 루프를 관찰합니다

노트북의 ‘3. 제공 수정 Loop 관찰’ 셀들을 실행합니다. `refine_answer`는 제공 루프를 연결합니다. 다음 셀의 초기 초안 ‘확인 완료’를 실제 모델이 수정하는 과정을 봅니다.

`history`에서 실패 이유와 다음 초안을 비교합니다. 통과하면 passed, 같은 실패가 반복되면 stalled, 수정 횟수를 다 쓰면 held입니다. 전체 루프 직접 구현은 선택 심화이며, 공통 활동은 Harness 장의 설계 메모입니다.

</section>
<section class="slide" id="protocols">

## 4. 노트북의 조회 함수를 MCP로 공개합니다

노트북 ‘4. MCP’에서 `build_mcp_server`를 작성합니다. 받은 조회 함수를 등록하고 서버를 반환합니다. **4A는 모델 없이**, **4B는 실제 모델을 연결해** 실행합니다.

1. 4A에서 도구 목록·입력 형식과 정산·계정·없는업무의 결과를 확인합니다. 제공 셀이 HTTP 서버를 시작하고 종료합니다.
2. 4B의 빈 `tools` 목록을 `await adapter.list_tools()`로 바꿉니다. 이 목록이 `create_agent(..., tools=tools)`에 전달됩니다.
3. 셀을 실행하여 모델의 조회 요청, 도구 결과, 최종 답변을 차례로 읽습니다.

**완료 기준:** 4A에서 P-01·재무지원팀, P-02·IT지원팀, found=false가 각각 나옵니다. 4B에서는 실제 도구 요청과 결과를 거쳐 계정 담당 팀과 P-02를 답합니다. 별도 서버 터미널이나 Python 파일 복사는 필요하지 않습니다.

</section>
<section class="slide" id="a2a">

## 5. 원격 검토 수용 조건을 구현합니다

노트북 ‘5. A2A’에서 다음 세 단계를 진행합니다.

1. **5A — 발견:** 실제 HTTP로 Agent Card를 읽고 `review-policy`, JSONRPC, streaming=false를 찾습니다. 모델 호출은 없습니다.
2. **5B — 위임:** `draft`를 바꿔 검토를 요청합니다. 보낸 Message와 받은 Task·Artifact를 읽습니다. 이 셀은 실제 모델을 호출합니다.
3. **5C — 수용:** `accept_review`를 구현합니다. submitted·working은 pending, completed 외 상태는 held입니다. 완료된 결과의 요청 ID·양의 정수 버전·passed가 모두 맞아야 accepted입니다. 불리언 버전과 빈 ID도 거절합니다.

**완료 기준:** Card에서 기능을 찾고, 실제 Task ID와 산출물을 확인하며, 반례 셀은 pending·accepted·held·held를 출력합니다. 정상 초안의 실제 결과는 accepted, 팀·정책 ID를 지운 초안은 completed여도 held입니다. 이후 ‘6. 통합’에서 전체 흐름을 연결합니다.

</section>
<section class="slide" id="finish">

## 전체 실행 결과를 확인합니다

<p class="section-time">예상 10분 · 해당 수업 시간에 포함</p>

<details class="instructor-note"><summary>강사용 진행 노트 · 실습 도움</summary>

입력과 반환 계약을 읽고 한 함수를 직접 완성하도록 돕습니다. 앞 단계가 막히면 학생 파일을 보관한 뒤 필요한 함수만 보완합니다. 모든 코드를 풀이로 교체하거나 별도 보고서를 작성하게 하지 않습니다.

</details>



자동 회귀 검사는 개발용 tests에 있습니다. 수업에서는 실행 파일의 입력을 바꾸고 자신의 코드가 반환한 결과를 확인합니다. 자신의 코드에서 정상·추가 확인·보류가 각각 어떤 조건으로 결정되는지 확인합니다. 결과는 노트북 셀 아래에 출력됩니다. 실제 문장을 읽고 근거와 대조합니다.

풀이 시간에는 reference.py를 열어 노드 경계, 조건 순서, 도구 인자, 수용 계약을 비교합니다.

보류 결과는 노트북 5번의 반례 셀에서 확인합니다. 통합 결과와 비교한 뒤 풀이 노트북의 같은 번호를 읽습니다.

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
