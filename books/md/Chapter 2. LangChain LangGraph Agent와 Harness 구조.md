---
layout: page
title: Ch2 · LangGraph 하네스
sidebar: false
aside: false
pageClass: lec-page
---

<div class="lec">
<div class="deck">

<section class="slide hero">
<div>
<div class="eyebrow">Chapter 2 · LangGraph 하네스</div>

# 흐름을 그래프로<br>묶는다

<p class="lead">Ch1의 단발 추출은 한 장을 읽고 끝났습니다. 인박스에는 열 건이 들어옵니다.<br>
이 챕터에서는 분류와 정규화를 상태·재시도·중단점이 있는 파이프라인으로 묶습니다. 고액이나 저신뢰 건은 자동으로 통과시키지 않고 사람에게 멈춰 묻습니다.</p>

<div class="kicker">
<div class="metric"><span class="num">70</span><strong>분</strong><span>이론 30 · 핸즈온 40</span></div>
<div class="metric"><span class="num">2</span><strong>번째 부품</strong><span>intake_graph.py</span></div>
<div class="metric"><span class="num">10</span><strong>건 적재</strong><span>classified/*.json</span></div>
</div>
</div>

<div class="board">
<div class="board-header"><span>이 챕터가 끝나면</span><span class="status-pill">산출물</span></div>
<div class="stack">
<div class="row"><div class="code">1</div><div class="copy"><strong>분류·정규화 StateGraph</strong><p>classify → verify → review → persist 흐름</p></div><div class="store">그래프</div></div>
<div class="row"><div class="code">2</div><div class="copy"><strong>checkpointer 재개</strong><p>멈춘 자리에서 같은 thread로 이어 실행</p></div><div class="store">상태</div></div>
<div class="row"><div class="code">3</div><div class="copy"><strong>interrupt() HITL</strong><p>고액·저신뢰 건은 사람 승인 후 적재</p></div><div class="store">멈춤</div></div>
</div>
</div>
</section>

<section class="slide">
<div class="section-head">
<div>
<div class="eyebrow">1 · 두 갈래</div>

## create_agent와 StateGraph

</div>
<p class="section-note">LangChain 1.0의 <code>create_agent</code>는 표준 ReAct 루프를 한 줄로 만듭니다. 모델이 도구를 알아서 고르고 반복합니다.<br>
우리 적재 흐름은 순서가 정해져 있습니다. 분류한 다음 검증하고, 고액이면 멈추고, 끝나면 적재합니다. 이렇게 흐름을 직접 그릴 때는 StateGraph가 맞습니다.</p>
</div>

<div class="grid-2">
<div class="panel"><div class="panel-head"><strong>create_agent — 자율 루프</strong><span>langchain.agents</span></div><div class="panel-body"><div class="list">
<p>한 줄로 ReAct 에이전트를 만듭니다</p>
<p>도구 선택과 반복을 모델이 정합니다</p>
<p>표준 루프로 충분할 때 가볍게 씁니다</p>
</div></div></div>
<div class="panel"><div class="panel-head"><strong>StateGraph — 명시한 흐름</strong><span>langgraph.graph</span></div><div class="panel-body"><div class="list">
<p>노드와 엣지로 단계를 직접 그립니다</p>
<p>분기·재시도·중단점을 내가 통제합니다</p>
<p>적재 파이프라인처럼 순서가 있는 일에 맞습니다</p>
</div></div></div>
</div>

```python
# create_agent — 표준 ReAct는 한 줄
from langchain.agents import create_agent
agent = create_agent("openai:google/gemini-3.5-flash", tools=[...])

# 내부는 우리가 손으로 짤 StateGraph와 같은 구조다.
# 흐름을 통제하고 싶으면 그 그래프를 직접 그린다 ↓
```

<p class="section-note" style="margin-top:16px"><code>create_agent</code>는 LangGraph 1.0 이전의 <code>create_react_agent</code>를 대체했습니다. 둘 다 같은 <code>CompiledStateGraph</code>를 돌려줍니다. 차이는 자유도입니다.</p>
</section>

<section class="slide">
<div class="section-head">
<div>
<div class="eyebrow">2 · 해부</div>

## 노드 · 엣지 · 상태

</div>
<p class="section-note">StateGraph는 세 가지로 이뤄집니다. 상태는 노드 사이를 흐르는 데이터, 노드는 그 상태를 받아 갱신하는 함수, 엣지는 다음에 어디로 갈지입니다.<br>
적재 파이프라인의 상태는 문서 한 장의 처리 맥락입니다. 어떤 문서인지, 추출한 레코드, 재시도 횟수, 검토 사유를 담습니다.</p>
</div>

```python
class IntakeState(TypedDict, total=False):
    doc: str        # sample_inbox 파일명
    record: dict    # 추출한 RecordV1 (노드 사이로 운반)
    retries: int    # 재분류 횟수
    flagged: str    # 사람 검토 사유("" 면 자동 통과)
    sum_ok: bool    # 영수증 합계 검증 결과(분기용)
```

<div class="flow">
<div class="flow-step"><small>classify</small><strong>추출</strong><p>Ch1 부품을 그대로 불러 영수증→RecordV1</p></div>
<div class="flow-step"><small>verify</small><strong>검증·플래그</strong><p>합계를 보고, 고액·저신뢰면 표시</p></div>
<div class="flow-step"><small>review</small><strong>사람 확인</strong><p>플래그가 있으면 interrupt()로 멈춤</p></div>
<div class="flow-step"><small>persist</small><strong>적재</strong><p>classified/&lt;문서&gt;.json 으로 떨군다</p></div>
</div>

<p class="section-note" style="margin-top:16px">classify는 Ch1의 <code>extract</code>를 그대로 부릅니다. 부품을 갈아끼우고 계약은 재사용한다는 원칙이 여기서 처음 작동합니다.</p>
</section>

<section class="slide">
<div class="section-head">
<div>
<div class="eyebrow">3 · 분기</div>

## 검증이 틀리면 되돌린다

</div>
<p class="section-note">verify가 영수증 합계를 봅니다. 항목 금액에 수량을 곱해 더한 값이 총액과 어긋나면 잘못 읽은 것입니다.<br>
이때 조건부 엣지가 흐름을 classify로 되돌립니다. 상한까지 다시 읽고, 그래도 안 맞으면 검토 큐로 넘겨 일단 적재합니다.</p>
</div>

```python
def after_verify(state: IntakeState) -> str:
    if state.get("sum_ok", True) is False:          # 합계 불일치
        if state["retries"] < MAX_RETRY:
            return "retry"                          # classify로 되돌림
        return "persist"                            # 상한 도달 — 검토 큐로
    return "review" if state["flagged"] else "persist"

g.add_conditional_edges("verify", after_verify,
                        {"retry": "retry", "review": "review", "persist": "persist"})
```

<div class="board" style="margin-top:18px">
<div class="board-header"><span>재시도는 무한 루프가 아니다</span><span class="status-pill">상한</span></div>
<div class="panel-body"><div class="list">
<p>같은 실패를 계속 반복하면 비용만 듭니다. <code>MAX_RETRY</code>로 두 번까지만 되돌리고, 넘으면 사람이 볼 큐로 보냅니다.</p>
<p>모델이 매번 다른 답을 줄 수 있으니 재시도는 의미가 있습니다. 다만 한계를 정해 두는 게 하네스의 일입니다.</p>
</div></div>
</div>
</section>

<section class="slide">
<div class="section-head">
<div>
<div class="eyebrow">4 · 상태</div>

## checkpointer가 자리를 기억한다

</div>
<p class="section-note">interrupt로 멈추면 그 순간의 상태를 어딘가 저장해야 재개할 수 있습니다. 그 일을 checkpointer가 합니다.<br>
<code>thread_id</code>로 실행을 구분합니다. 같은 thread로 다시 부르면 멈춘 자리부터 이어집니다. 다른 thread면 새 실행입니다.</p>
</div>

```python
graph = g.compile(checkpointer=InMemorySaver())
config = {"configurable": {"thread_id": f"intake-{doc}"}}

result = graph.invoke(state, config=config)     # review에서 멈춤
# ... 사람의 결정을 받은 뒤 ...
graph.invoke(Command(resume="approve"), config=config)  # 같은 자리에서 재개
```

<div class="board" style="margin-top:18px">
<div class="board-header"><span>왜 메모리에 저장하나</span><span class="status-pill">InMemorySaver</span></div>
<div class="panel-body"><div class="list">
<p>이 실습은 한 프로세스 안에서 멈췄다 재개하므로 메모리 체크포인터로 충분합니다.</p>
<p>프로덕션에서는 같은 자리에 SQLite·Postgres 체크포인터를 끼웁니다. 그래프 코드는 그대로 두고 저장소만 바꿉니다. 이것도 부품 교체입니다.</p>
</div></div>
</div>
</section>

<section class="slide">
<div class="section-head">
<div>
<div class="eyebrow">5 · 멈춤</div>

## 자동으로 넘기지 않는 것들

</div>
<p class="section-note">분류가 늘 맞지는 않습니다. 금액이 크거나 모델이 확신하지 못한 건을 자동으로 적재하면 틀린 데이터가 조용히 쌓입니다.<br>
그래서 review 노드에서 interrupt()로 멈춰 사람에게 묻습니다. 승인하면 적재하고, 반려하면 보류합니다.</p>
</div>

```python
def review(state: IntakeState) -> dict:
    decision = interrupt({                  # 여기서 실행이 멈춘다
        "사유": state["flagged"],           # 고액 / 저신뢰
        "판매처": state["record"]["판매처"],
        "금액": state["record"]["금액"],
        "질문": "이 분류를 그대로 적재할까요? (approve / reject)",
    })
    return {"flagged": "" if decision != "reject" else "rejected"}
```

<div class="grid-2">
<div class="panel"><div class="panel-head"><strong>멈추는 기준</strong><span>이 실습의 임계값</span></div><div class="panel-body"><div class="list">
<p>고액 — 총액 1,000,000원 이상</p>
<p>저신뢰 — 추출 신뢰도 0.7 미만</p>
</div></div></div>
<div class="panel"><div class="panel-head"><strong>실제로 멈추는 건</strong><span>sample_inbox</span></div><div class="panel-body"><div class="list">
<p>세금계산서 1,650,000원 · 용역 계약 3,000,000원</p>
<p>나머지 8건은 기준 아래라 자동 적재됩니다</p>
</div></div></div>
</div>

<div class="ask"><strong>생각해보기.</strong> 만약 <code>compile()</code>에 checkpointer를 빼면 interrupt가 동작할까요? 그리고 같은 <code>thread_id</code>로 다시 부르면 무슨 일이 일어날까요?</div>

<details>
<summary>정답 확인</summary>
<div class="reveal">
<p>checkpointer 없이는 interrupt가 동작하지 않습니다. 멈춘 순간의 상태를 저장할 곳이 없으니 재개 지점을 잃습니다. 그래서 HITL에는 checkpointer가 필수입니다.</p>
<p>같은 <code>thread_id</code>로 다시 부르면 저장된 그 자리부터 이어집니다. <code>Command(resume="approve")</code>가 멈춘 review 노드로 결정을 흘려보내 다음 단계(persist)로 넘어갑니다. 다른 thread_id면 처음부터 새 실행입니다.</p>
</div>
</details>
</section>

<section class="slide">
<div class="section-head">
<div>
<div class="eyebrow">핸즈온 ① · 코드 정독</div>

## 그래프를 손으로 엮는다

</div>
<p class="section-note">노드 다섯 개를 엣지로 잇습니다. 한 줄씩 읽으면 분류 흐름이 그대로 그림으로 보입니다. 분기 하나(verify 다음)만 조건부고 나머지는 직선입니다.</p>
</div>

<div class="panel">
<div class="panel-head"><strong>ch2-langgraph-agent/intake_graph.py — build_graph</strong><span>노드·엣지·체크포인터</span></div>
<div class="panel-body">

```python
def build_graph():
    g = StateGraph(IntakeState)
    g.add_node("classify", classify)     # 추출(Ch1 부품)
    g.add_node("verify", verify)         # 합계·플래그
    g.add_node("retry", bump_retry)      # 재분류 카운터
    g.add_node("review", review)         # interrupt() 멈춤
    g.add_node("persist", persist)       # classified/ 적재
    g.add_edge(START, "classify")
    g.add_edge("classify", "verify")
    g.add_conditional_edges("verify", after_verify,          # ← 유일한 분기
                            {"retry": "retry", "review": "review", "persist": "persist"})
    g.add_edge("retry", "classify")      # 재시도는 classify로 되돌림
    g.add_edge("review", "persist")
    g.add_edge("persist", END)
    return g.compile(checkpointer=InMemorySaver())            # ← interrupt에 필수
```

</div>
</div>

<div class="grid-2" style="margin-top:16px">
<div class="panel"><div class="panel-head"><strong>직선 엣지 vs 조건부 엣지</strong></div><div class="panel-body"><div class="list">
<p><code>add_edge(A, B)</code> — 늘 A 다음 B. 분류→검증처럼 정해진 길.</p>
<p><code>add_conditional_edges(verify, after_verify, {...})</code> — <code>after_verify</code>가 돌려준 문자열로 다음 노드를 고릅니다.</p>
</div></div></div>
<div class="panel"><div class="panel-head"><strong>after_verify가 고르는 세 길</strong></div><div class="panel-body"><div class="list">
<p>합계 불일치 → <code>retry</code>(상한 전), 플래그 있음 → <code>review</code>, 그 외 → <code>persist</code>.</p>
<p>흐름 제어가 데이터(state)에 따라 코드로 결정됩니다.</p>
</div></div></div>
</div>
</section>

<section class="slide">
<div class="section-head">
<div>
<div class="eyebrow">핸즈온 ② · 단계별 실행</div>

## 흘려보내고 멈춤을 본다

</div>
<p class="section-note">전체를 한 번 흘리고, 고액 한 건만 따로 돌려 interrupt를 눈으로 보고, 반려도 해 봅니다. 각 단계의 성공 기준을 확인하세요.</p>
</div>

<div class="stack">
<div class="row"><div class="code">1</div><div class="copy"><strong>전체 적재 — 자동 승인</strong><p><code>uv run python3 ch2-langgraph-agent/intake_graph.py --mock</code><br><span style="color:var(--muted)">성공 기준: 10건이 흐르고 고액 2건에서 ⏸ interrupt가 뜬 뒤 승인되어 <code>workspace/classified/</code>에 JSON 10개.</span></p></div><div class="store">10건</div></div>
<div class="row"><div class="code">2</div><div class="copy"><strong>한 건만 — 멈춤 관찰</strong><p><code>... --mock --doc invoice_photo.png</code><br><span style="color:var(--muted)">성공 기준: <code>⏸ interrupt — 고액(1,650,000원)</code> 줄이 보이고 review→persist로 이어진다.</span></p></div><div class="store">interrupt</div></div>
<div class="row"><div class="code">3</div><div class="copy"><strong>검토건 반려</strong><p><code>... --mock --reject-flagged</code><br><span style="color:var(--muted)">성공 기준: 고액 건이 <code>[review] 반려 — 적재 보류</code>로 빠지고 그 JSON은 안 생긴다.</span></p></div><div class="store">보류</div></div>
</div>

<div class="panel" style="margin-top:18px">
<div class="panel-head"><strong>출력 — 고액 건에서 멈췄다 재개</strong><span>invoice_photo.png</span></div>
<div class="panel-body">

```text
▶ invoice_photo.png
  [classify] 디자인스튜디오 레이 · 1,650,000원 · 신뢰도 1.00
  [verify] 통과 · 검토 필요: 고액(1,650,000원)
  ⏸ interrupt — 고액(1,650,000원) · 디자인스튜디오 레이 1,650,000원 → 자동 결정 'approve'
  [review] 승인 — 적재 진행
  [persist] → workspace/classified/invoice_photo.json
```

</div>
</div>

<div class="ask" style="margin-top:18px"><strong>직접 해보기.</strong> <code>HIGH_VALUE</code> 임계값을 <code>10000</code>으로 낮춰 보세요. interrupt가 몇 건에서 걸릴까요? 반대로 <code>5000000</code>으로 올리면?</div>

<details>
<summary>관찰 포인트</summary>
<div class="reveal">
<p><code>10000</code>으로 낮추면 대부분의 영수증·명세서가 고액으로 걸려 interrupt가 쏟아집니다. 사람이 일일이 승인해야 하니 자동화 효과가 사라집니다.</p>
<p><code>5000000</code>으로 올리면 아무것도 안 걸려 전부 자동 적재됩니다. 틀린 분류도 그냥 통과합니다. 임계값은 "자동화 vs 안전"의 손잡이입니다. 도메인에 맞게 잡는 게 설계입니다.</p>
</div>
</details>
</section>

<section class="slide">
<div class="section-head">
<div>
<div class="eyebrow">핸즈온 ③ · 트러블슈팅</div>

## 막히면 여기부터

</div>
<p class="section-note">그래프가 안 도는 대부분은 분기 함수나 상태 키 문제입니다.</p>
</div>

<div class="grid-2">
<div class="panel"><div class="panel-head"><strong>interrupt가 안 걸림</strong><span>HITL</span></div><div class="panel-body"><div class="list">
<p><code>compile(checkpointer=...)</code>를 빠뜨렸거나, 고액·저신뢰 기준에 걸리는 문서가 없습니다. <code>--doc invoice_photo.png</code>로 확인하세요.</p>
</div></div></div>
<div class="panel"><div class="panel-head"><strong>KeyError: state 키</strong><span>상태</span></div><div class="panel-body"><div class="list">
<p>노드가 돌려준 dict의 키가 <code>IntakeState</code>에 없으면 무시되거나 깨집니다. TypedDict에 필드를 선언했는지 봅니다.</p>
</div></div></div>
<div class="panel"><div class="panel-head"><strong>분기에서 멈춤</strong><span>조건부 엣지</span></div><div class="panel-body"><div class="list">
<p><code>after_verify</code>가 돌려준 문자열이 매핑 dict의 키와 정확히 같아야 합니다. 오타면 그래프가 갈 곳을 잃습니다.</p>
</div></div></div>
<div class="panel"><div class="panel-head"><strong>재개가 안 됨</strong><span>thread_id</span></div><div class="panel-body"><div class="list">
<p>재개할 때 처음과 <strong>같은</strong> <code>thread_id</code>를 써야 멈춘 자리를 찾습니다. 매번 새로 만들면 처음부터 돕니다.</p>
</div></div></div>
</div>

<p class="section-note" style="margin-top:16px">전체 실행 파일은 <code>ch2-langgraph-agent/intake_graph.py</code>. classify는 Ch1의 <code>extract</code>를 import해 그대로 씁니다 — 부품 교체·계약 재사용의 첫 작동입니다.</p>
</section>

<section class="slide">
<div class="section-head">
<div>
<div class="eyebrow">마무리</div>

## 다음 — 한 장씩 말고, 한꺼번에

</div>
<p class="section-note">이제 인박스가 정규화된 레코드 열 건으로 정리됐습니다. StateGraph는 흐름을 또렷이 통제하지만 단계를 우리가 다 그려야 합니다.<br>
Ch3에서는 한 단계 위로 올라갑니다. 여러 문서를 서브에이전트가 나눠 동시에 조사하고, 그 계획과 파일을 하네스가 알아서 관리합니다.</p>
</div>

<div class="grid-3">
<div class="panel"><div class="panel-head"><strong>지금 손에 든 것</strong></div><div class="panel-body"><div class="list">
<p>분류·정규화 파이프라인</p>
<p>classified/ 열 건 · 재시도 · HITL</p>
</div></div></div>
<div class="panel"><div class="panel-head"><strong>Ch3에서 할 것</strong></div><div class="panel-body"><div class="list">
<p>DeepAgents fan-out 동시 조사</p>
<p>write_todos · 파일시스템 퇴피</p>
</div></div></div>
<div class="panel"><div class="panel-head"><strong>최종 목적지</strong></div><div class="panel-body"><div class="list">
<p>인박스 한 통 → 검증된 브리프</p>
<p>Ch6 통합 캡스톤</p>
</div></div></div>
</div>

<div class="board" style="margin-top:18px">
<div class="board-header"><span>참고 자료</span><span class="status-pill">출처</span></div>
<div class="panel-body"><div class="list">
<p><a href="https://langchain-ai.github.io/langgraph/">LangGraph 문서</a> · <a href="https://langchain-ai.github.io/langgraph/how-tos/human_in_the_loop/">Human-in-the-loop (interrupt)</a></p>
<p><a href="https://python.langchain.com/docs/concepts/agents/">LangChain create_agent</a> · <a href="https://langchain-ai.github.io/langgraph/concepts/persistence/">Checkpointer·Persistence</a></p>
</div></div>
</div>
</section>


<nav class="chapnav">
<div class="board" style="margin-top:8px">
<div style="display:grid;grid-template-columns:1fr auto 1fr;gap:14px;align-items:center">
<a href="/chapters/chapter-1" style="color:inherit;text-decoration:none;font-weight:900;font-size:14px">← Ch1 · 에이전트 패러다임</a>
<a href="/toc" style="color:var(--forest);text-decoration:none;font-weight:900;font-size:13px;background:rgba(148,210,189,.3);border:1px solid rgba(15,118,110,.24);border-radius:99px;padding:7px 16px">목차</a>
<a href="/chapters/chapter-3" style="color:inherit;text-decoration:none;font-weight:900;font-size:14px;text-align:right">Ch3 · DeepAgents 하네스 →</a>
</div>
</div>
</nav>

</div>
</div>
