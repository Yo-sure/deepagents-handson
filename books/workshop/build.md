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

각 모듈에서 배운 개념을 같은 프로젝트에 차례로 적용합니다. 교재의 작은 실행 예제는 원리를 확인하는 용도입니다. 본 실습의 완료 여부는 노트북에서 자신의 구현과 반례를 실행해 판단합니다.

처음에는 조회 함수와 Agent 구성을 만들고, 다음 수업에서 분기와 서버 연결을 추가합니다. 노트북에서 현재 수업의 번호까지만 진행하고 교재의 풀이를 비교합니다.

## 지금 진행할 실습을 찾습니다

별도 과제를 처음부터 시작하는 페이지가 아닙니다. 수업 중에는 각 장의 실습을 따라가고, 여기서는 놓친 단계와 완료 결과를 다시 찾습니다. 아래 표에서 파일명과 절 번호를 함께 확인합니다. Harness 주 실습은 별도 노트북입니다.

|수업|실행·작성 위치|넘어가기 전 확인|
|---|---|---|
|[환경 준비](./start#learning-goals)·[입문](./agent#learning-goals)|orientation.ipynb|환경 확인, 도구 요청·결과·최종 답변 구분|
|[LangChain](./langchain#learning-goals)|build-agent.ipynb 1A·1B·1C|정상 두 업무와 미등록 업무, 도구 연결|
|[LangGraph](./graph#learning-goals)|2·2A / concepts.ipynb|분기·추가 질문 노드, 방문 경로·초안 생성 호출, 중단·재개|
|[Harness](./harness#learning-goals)|harness-build.ipynb H1~H3|Skill 작성·DeepAgents 구성·실제 호출과 문서 읽기|
|[MCP](./mcp#learning-goals)|4A·4B|원격 조회와 Agent 도구 호출|
|[A2A](./a2a#learning-goals)|5A·5B·5C|Card·Task·Artifact와 수용 반례|
|[통합·복습](./wrap#learning-goals)|6A~6D / 퀴즈는 복습|6C 기준 실행과 6D의 정책·표현 검토 선택 비교|

첫 환경 셀을 실행한 뒤 필요한 앞 단계의 정의·연결 셀을 순서대로 실행합니다. 정의를 수정했다면 그 아래 연결 셀도 다시 실행합니다. 막힌 앞 단계는 [보완 안내](#recovery)를 따르고, 풀이 노트북의 같은 번호와 비교합니다.



</section>
<section class="slide" id="first-code">

## 실습 노트북을 엽니다

환경설정에서 실행한 JupyterLab에서 `notebooks/build-agent.ipynb`를 엽니다. <strong><mark class="key-point">코드는 이 노트북의 셀에 작성합니다.</mark></strong> 첫 환경 확인 셀부터 Shift+Enter로 실행하고, 현재 수업의 번호까지 진행합니다.

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
|1C의 build_service_agent·ask_service 작성|두 도구 등록과 messages·invoke 직접 작성, 정책 결과로 연락처 조회|
|다음 실행 셀에서 질문 전달|요청의 계정 인자 → 도구 결과 P-02·IT지원팀 → 마지막 답변의 일치 확인|

docstring에는 도구가 언제 필요한지 설명합니다. 지침에는 조회 시점과 정책이 없을 때의 행동을 작성합니다. 질문을 없는업무로 바꾸어 담당 팀을 추측하지 않는지 확인합니다. 출력은 실행한 셀 바로 아래에 남습니다.

</section>
<section class="slide" id="graph">

## 2. 노트북에서 업무 분기를 구현합니다

**`build-agent.ipynb`의 ‘2. 업무 Graph’로 이동합니다.** 앞 장의 조회·Agent 셀을 실행한 같은 커널에서 이어갑니다.

함께 하는 시간에는 `route_inquiry`만 작성하고 아래 세 입력을 함수에 직접 넣어 경로를 확인합니다. `ask_for_details`가 미완성이므로 아직 2A 그래프 검사는 실행하지 않습니다. 개인 시간에 질문 노드와 그래프 등록·연결을 완성한 뒤 정의·연결 셀 → 2A 검사 → 2B 관찰 순서로 진행합니다. 2C 재작업 그래프는 고급 확장입니다.

```python
for found, contact in [(True, "user@example.test"), (True, "   "), (False, "user@example.test")]:
    state = {"data": {"found": found}, "contact": contact}
    print(found, repr(contact), route_inquiry(state))
# 기대 경로: draft, ask, ask
```

1. `route_inquiry` 셀을 완성합니다. 정책이 있고 회신 대상이 공백이 아니면 `"draft"`, 그 외에는 `"ask"`를 반환합니다.
2. `ask_for_details` 노드를 작성합니다. 정책을 찾지 못했으면 업무 주제, 회신 대상이 비었으면 회신 대상을 묻습니다. 둘 다 없으면 둘 다 묻고, 이미 있는 정보는 다시 묻지 않습니다.
3. `build_workflow` 안에서 StateGraph(Inquiry)를 만들고 네 add_node, START·END와 add_edge, lookup의 add_conditional_edges, compile을 직접 작성합니다. 정의 셀과 실행 연결 셀을 차례로 실행합니다.
4. **‘2A. 내 구현을 검사하고 실제 Agent로 확인합니다’** 아래 셀의 `topic`과 `contact`를 바꿔 Shift+Enter로 실행합니다.

```python
topic = "계정"
contact = "   "
draft_calls.clear()
result = graph.invoke({"topic": topic, "contact": contact})
print("방문:", result["visited"])
print("판정:", result["decision"])
print("초안 생성 호출:", len(draft_calls))
print("답변:", result["draft"])
```

|topic / contact|기대 방문 경로|완료 확인|
|---|---|---|
|계정 / 정상 주소|lookup → draft → review|초안 생성과 검토 실행|
|계정 / 빈 문자열|lookup → ask|판정 ask, 초안 생성 호출 0|
|계정 / 공백 세 칸|lookup → ask|공백도 정보 부족으로 판단|
|없는업무 / 정상 주소|lookup → ask|규정이 없으면 초안 생성 호출 0|

먼저 제공 `check_graph(build_workflow, lookup_policy)` 검사로 모델 없이 경로와 `missing`을 확인합니다. 이어 네 실제 입력의 경로와 추가 질문을 비교합니다. `draft_calls`는 초안 생성 함수의 호출 기록이며, Agent 내부의 모델 API 호출 횟수는 아닙니다. 정상 경로에서 검토가 held이면 `result['history']`의 실패 이유를 읽습니다. API 오류로 셀이 실패했다면 연결 문제를 해결하고 다시 실행합니다.

별도 2B 관찰 셀의 코드는 생성·검토를 고정하고 자신의 그래프를 실행합니다. `updates`(각 노드의 반환값)와 `values`(반영된 전체 State)를 비교합니다. 개인 과제에서 `visited`를 바꾸어 비교할 때는 2A 검사 대신 2B 관찰 셀을 실행합니다. 변경을 복원한 뒤 2A 검사도 다시 통과시킵니다.

노트북의 State는 `Inquiry`입니다. `data`는 조회 결과, `draft`는 답변 또는 추가 질문, `visited`는 방문 이력입니다. 조회·초안·검토 노드의 본문은 제공하며, `route_inquiry`·`ask_for_details`·노드 등록·엣지 연결은 직접 작성합니다.

질문 노드는 바꿀 필드만 반환합니다: `decision="ask"`, 부족한 정보 목록 `missing`, 그 목록으로 만든 질문 `draft`, 빈 `history`, 기존 방문 기록 뒤에 `"ask"`를 붙인 `visited`입니다. `missing`에는 정책이 없으면 `"topic"`, 회신 대상이 비었으면 `"contact"`를 순서대로 넣습니다. `topic`·`contact`·`data`는 그대로 남겨야 합니다. **미등록 업무와 공백 연락처가 동시에 들어오면 무엇을 물을지 먼저 예상한 뒤**, 자신이 고른 반례도 하나 추가해 실행합니다. 기본 그래프 조립은 필수입니다. 2C의 검토·수정 순환 그래프는 고급 확장입니다.

</section>

<section class="slide" id="loop">

## 3. 제공 수정 루프를 관찰합니다

노트북의 ‘3. 제공 수정 Loop 관찰’ 셀들을 실행합니다. `refine_answer`는 제공 루프를 연결합니다. 다음 셀의 초기 초안 ‘확인 완료’를 실제 모델이 수정하는 과정을 봅니다.

`history`에서 실패 이유와 다음 초안을 비교합니다. 통과하면 passed, 수정한 초안이 직전 초안과 동일하면 stalled, 수정 횟수를 다 쓰면 held입니다. 4장 공통 실습은 `harness-build.ipynb` H1~H3의 DeepAgents 직접 구성입니다. 이 수정 Loop와 설계 메모는 선택 심화입니다. 추가로 구현을 읽으려면 Jupyter 파일 탐색기에서 `build_lab/guided.py`의 `refine_answer`를 엽니다. 성공 → 같은 초안 반복 → 상한 소진 순서와 `range(limit + 1)`을 찾아 마지막 허용 수정의 성공을 설명합니다. 이는 제공 구현을 읽는 활동이며 별도 구현 과제가 아닙니다.

</section>
<section class="slide" id="protocols">

## 4. 노트북의 조회 함수를 MCP로 공개합니다

노트북 ‘4. MCP’에서 `build_mcp_server`를 작성합니다. 받은 조회 함수를 등록하고 서버를 반환합니다. **4A는 모델 없이**, **4B는 실제 모델을 연결해** 실행합니다.

1. 4A에서 도구 목록·입력 형식과 정산·계정·없는업무의 결과를 확인합니다. 제공 셀이 HTTP 서버를 시작하고 종료합니다.
2. `build_remote_agent`와 `run_remote_agent`를 작성합니다. MCPAdapter(Client(...))의 async with 안에서 list_tools → Agent 구성 → ainvoke → 전체 결과 반환을 연결합니다. url은 /mcp까지 포함합니다.
3. 셀을 실행하여 모델의 조회 요청, 도구 결과, 최종 답변을 차례로 읽습니다.

**완료 기준:** 4A에서 P-01·재무지원팀, P-02·IT지원팀, found=false가 각각 나옵니다. 4B에서는 실제 도구 요청과 결과를 거쳐 계정 담당 팀과 P-02를 답합니다. 별도 서버 터미널이나 Python 파일 복사는 필요하지 않습니다.

</section>
<section class="slide" id="a2a">

## 5. 원격 검토 수용 조건을 구현합니다

노트북 ‘5. A2A’에서 다음 세 단계를 진행합니다.

1. **5A — 발견:** 실제 HTTP로 Agent Card를 읽고 `review-policy`, JSONRPC, streaming=false를 찾습니다. 모델 호출은 없습니다.
2. **5B — 위임:** 5A 정의 셀의 `make_review_request`와 `connect_review_client`를 작성합니다. Message·Part·SendMessageRequest를 구성하고, Card의 기능을 확인하여 ClientFactory로 연결합니다. `draft`를 바꿔 검토를 요청합니다. 보낸 Message와 받은 Task·Artifact를 읽습니다. 이 셀은 실제 모델을 호출합니다.
3. **5C — 수용:** `accept_review`를 구현합니다. submitted·working은 pending, completed 외 상태는 held입니다. 완료된 결과의 요청 ID·양의 정수 버전·passed가 모두 맞아야 accepted입니다. 불리언 버전과 빈 ID도 거절합니다.

**완료 기준:** Card에서 기능을 찾고, 실제 Task ID와 산출물을 확인하며, 5C 검사는 13개 상태·결과 반례를 비교하여 실패한 이유를 표시합니다. 정상 초안의 실제 결과는 accepted, 팀·정책 ID를 지운 초안은 completed여도 held입니다. 이후 ‘6. 통합’의 6A → 6B → 6C 셀에서 조회·Graph·원격 검토를 차례로 연결합니다.

</section>
<section class="slide" id="finish">

## 전체 실행 결과를 확인합니다

<p class="section-time">통합 장의 기준 실행 7분·Agent 선택 실습 16분에 포함</p>





자동 회귀 검사는 개발용 tests에 있습니다. 수업에서는 노트북 셀의 입력을 바꾸고 자신의 코드가 반환한 결과를 확인합니다. 자신의 코드에서 <mark class="key-point">정상·추가 확인·보류가 각각 어떤 조건으로 결정되는지 확인합니다.</mark> 결과는 노트북 셀 아래에 출력됩니다. 실제 문장을 읽고 근거와 대조합니다.

풀이 시간에는 `build-agent-solution.ipynb`의 같은 번호를 열어 노드 경계, 조건 순서, 도구 인자, 수용 계약을 비교합니다.

보류 결과는 노트북 5번의 반례 셀에서 확인합니다. 통합 결과와 비교한 뒤 풀이 노트북의 같은 번호를 읽습니다.

### 마친 뒤 설명할 수 있어야 하는 것

통합 시간에는 [한 Agent에 MCP·A2A를 연결하는 6D 실습](./wrap#practice)을 수행합니다. 정책 검토와 표현 검토 요청에서 담당자 선택과 원격 검토 기록을 비교합니다. 미등록 문의는 선택 복습입니다. 별칭 변경은 수업 뒤 선택 복습으로 이어갑니다.

핵심은 도구·LangChain Agent·업무 분기를 직접 만들고 실행 흐름을 설명하는 능력입니다. 그래프 연결은 직접 작성하고, 수정 Loop 제공 구현은 추가로 읽을 수 있으며, Loop·Graph Engineering은 실제 담론을 읽고 반복 작업과 여러 역할을 조직하는 설계 판단까지 다룹니다. MCP 도구 공개와 A2A 결과 수용도 직접 연결합니다. 장기 메모리, 장애 후 복구, 운영 인증, 분산 재시도까지 하루에 숙련하는 과정은 아닙니다. DeepAgents·Skill은 harness-build.ipynb에서 직접 구성·실행합니다. HITL은 제공 예제를 비교하고 구현 심화는 별도 과제로 이어갑니다.

### 더 연습하려면

- [LangChain Academy](https://academy.langchain.com/courses/intro-to-langgraph): 단순 그래프부터 체인·라우터·Agent·메모리까지 순서대로 연습할 수 있습니다.
- [LangGraph 101](https://github.com/langchain-ai/langgraph-101): 기본 노트북과 심화 패턴을 골라 실습할 수 있습니다.
- [환경·과제 설계](https://www.langchain.com/blog/building-agent-environments-and-tasks): 자신의 업무로 과제를 만들 때 입력·환경·판정 기준을 정하는 방법을 읽습니다.

외부 실습을 실행할 때는 해당 자료의 의존성과 설치 안내를 확인합니다.
<aside class="discussion-prompt"><strong>생각거리 · 여유가 있으면 +3분</strong><p>정산과 계정 검사는 모두 통과했습니다. 하지만 코드에는 “정산이면 재무지원팀, 나머지는 IT지원팀”이라고 적혀 있습니다.<br><br><strong>“없는업무”를 넣으면 어떤 답이 나올까요?</strong> 이 문제를 잡으려면 검사에 어떤 입력을 추가해야 할까요?</p></aside>



</section>

<section class="slide" id="recovery">

## 앞 단계에서 막혔을 때

<p class="section-time">필요할 때 약 3분 · 다음 활동에서 조절</p>

앞 단계 구현이 끝나지 않아 다음 실습을 실행할 수 없을 때 사용합니다. 먼저 Jupyter의 파일 복제 기능으로 자신의 노트북을 보관합니다. 아래 표에서 필요한 함수를 확인하고 `build-agent-solution.ipynb`의 같은 이름 정의 셀로 미완료 함수만 보완합니다. 현재 배우는 단계의 함수까지 교체하지 않습니다.

커널을 다시 시작했다면 저장된 출력만으로 이어갈 수 없습니다. 노트북 첫머리의 **커널을 다시 시작하거나 중간 장부터 복습할 때** 표에서 선행 셀을 확인합니다. 함수 정의뿐 아니라 객체를 만드는 연결 셀도 실행해야 합니다.

|진행할 단계|먼저 필요한 함수·실행|
|---|---|
|Graph|1A·1B 정의와 실행 → 2의 정의·연결 셀|
|수정 루프만 관찰|1A 정의 → 3의 제공 함수·수정 실행 셀|
|MCP|1A 정의 → 4의 서버 정의. 모델은 4B에서 준비|
|A2A Card·위임|환경 셀 → 5A → 5B. Card 조회에는 모델·키 불필요|
|통합|1A·1B, 2, build_mcp_server, accept_review의 정의와 5A의 import → 6A·6B·6C|

필요한 함수를 보완했다면 원래 진행하던 실습으로 돌아가 정의 셀과 해당 단계의 연결·실행 셀을 순서대로 실행합니다. 직접 작성하다 막힌 부분은 보관한 파일과 풀이를 비교하며 다시 살펴봅니다.
</section>

<nav class="chapnav"><a href="../toc">전체 목차</a></nav>
</div></div>
