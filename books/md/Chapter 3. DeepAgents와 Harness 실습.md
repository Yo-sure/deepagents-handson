---
layout: page
title: Ch3 · DeepAgents 하네스
sidebar: false
aside: false
pageClass: lec-page
---

<div class="lec">
<div class="deck">

<section class="slide hero">
<div>
<div class="eyebrow">Chapter 3 · DeepAgents 하네스</div>

# 나눠서,<br>동시에 조사한다

<p class="lead">정규화된 레코드 열 건이 손에 있습니다. 이제 서로 맞대 봐야 합니다. 카드 명세서의 거래마다 영수증이 있나, 은행 입출금은 계약과 이어지나.<br>
한 사람이 순서대로 보면 느립니다. 조사 주제를 나눠 서브에이전트가 동시에 돕니다. 그 계획과 파일을 하네스가 관리합니다.</p>

<div class="kicker">
<div class="metric"><span class="num">65</span><strong>분</strong><span>이론 22 · 핸즈온 43</span></div>
<div class="metric"><span class="num">3</span><strong>번째 부품</strong><span>research_orchestrator.py</span></div>
<div class="metric"><span class="num">1</span><strong>구멍 발견</strong><span>영수증 없는 89,000원</span></div>
</div>
</div>

<div class="board">
<div class="board-header"><span>이 챕터가 끝나면</span><span class="status-pill">산출물</span></div>
<div class="stack">
<div class="row"><div class="code">1</div><div class="copy"><strong>fan-out 조사</strong><p>주제를 나눠 서브에이전트가 동시에 대사</p></div><div class="store">병렬</div></div>
<div class="row"><div class="code">2</div><div class="copy"><strong>research_notes/</strong><p>긴 중간 결과를 컨텍스트 밖 파일로 퇴피</p></div><div class="store">파일</div></div>
<div class="row"><div class="code">3</div><div class="copy"><strong>brief_draft.md</strong><p>짚을 점을 모은 브리프 초안</p></div><div class="store">종합</div></div>
</div>
</div>
</section>

<section class="slide">
<div class="section-head">
<div>
<div class="eyebrow">1 · 위로 한 칸</div>

## StateGraph로는 버거운 일

</div>
<p class="section-note">Ch2의 StateGraph는 단계를 우리가 다 그렸습니다. 노드와 엣지를 직접 이었습니다. 조사처럼 무엇을 몇 갈래로 볼지 미리 모르는 일에는 그 방식이 버겁습니다.<br>
하네스는 그 위층입니다. 계획을 세우고, 일을 나눠 위임하고, 긴 결과를 파일로 빼는 일을 알아서 합니다.</p>
</div>

<div class="grid-2">
<div class="panel"><div class="panel-head"><strong>Runtime — StateGraph</strong><span>Ch2</span></div><div class="panel-body"><div class="list">
<p>단계가 정해진 흐름에 맞습니다</p>
<p>분기·재시도를 손으로 그립니다</p>
<p>조사 갈래가 늘면 그래프가 복잡해집니다</p>
</div></div></div>
<div class="panel"><div class="panel-head"><strong>Harness — DeepAgents</strong><span>Ch3</span></div><div class="panel-body"><div class="list">
<p>계획·위임·파일 관리를 기본 제공</p>
<p>주제를 서브에이전트로 나눠 동시 처리</p>
<p>모델은 그대로인데 할 수 있는 일이 커집니다</p>
</div></div></div>
</div>

<p class="section-note" style="margin-top:16px">LangChain은 같은 모델·런타임에 이 하네스만 더해 Terminal-Bench 52.8%를 66.5%로 올렸습니다. Ch1에서 본 "순위를 가르는 건 모델이 아니라 하네스"가 여기서 코드로 드러납니다.</p>
</section>

<section class="slide">
<div class="section-head">
<div>
<div class="eyebrow">2 · 한 줄</div>

## create_deep_agent의 기본 장비

</div>
<p class="section-note">하네스 에이전트는 한 줄로 만듭니다. 만들면 도구 몇 개가 기본으로 따라옵니다. 계획을 적는 도구, 일을 위임하는 도구, 파일을 읽고 쓰는 도구입니다.<br>
우리는 여기에 조사용 도구만 얹습니다. 레코드를 요약하는 도구, 노트를 저장하는 도구.</p>
</div>

```python
from deepagents import create_deep_agent

agent = create_deep_agent(
    model="openai:google/gemini-3.5-flash",
    tools=[list_records, write_note],   # 우리가 얹는 조사 도구
    system_prompt="너는 인박스 리서치 애널리스트다 ...",
)
# 기본 장비: write_todos(계획) · task(서브에이전트 위임) · 파일시스템(read/write/ls)
```

<div class="grid-3">
<div class="panel"><div class="panel-head"><strong>write_todos</strong><span>계획</span></div><div class="panel-body"><div class="list">
<p>무엇을 조사할지 먼저 목록으로 적습니다</p>
<p>계획-실행-점검 루프를 강제합니다</p>
</div></div></div>
<div class="panel"><div class="panel-head"><strong>task</strong><span>위임</span></div><div class="panel-body"><div class="list">
<p>주제 하나를 하위 에이전트에 맡깁니다</p>
<p>여러 개를 동시에 돌려 fan-out 합니다</p>
</div></div></div>
<div class="panel"><div class="panel-head"><strong>filesystem</strong><span>퇴피</span></div><div class="panel-body"><div class="list">
<p>긴 결과를 컨텍스트 밖 파일로 뺍니다</p>
<p>윈도우가 가득 차는 문제를 피합니다</p>
</div></div></div>
</div>
</section>

<section class="slide">
<div class="section-head">
<div>
<div class="eyebrow">3 · fan-out</div>

## 주제를 나눠 동시에

</div>
<p class="section-note">조사를 세 갈래로 나눕니다. 카드 대사, 은행 대사, 지출 요약. 서로 독립이라 동시에 돌 수 있습니다.<br>
각 갈래가 끝나면 결과를 research_notes 아래 제 파일로 떨굽니다. 한 갈래의 긴 출력이 다른 갈래의 맥락을 밀어내지 않습니다.</p>
</div>

<div class="flow" style="grid-template-columns:repeat(3,minmax(0,1fr))">
<div class="flow-step"><small>thread 1</small><strong>카드 대사</strong><p>명세서 거래줄 ↔ 개별 영수증을 맞춰 빈 줄을 찾는다</p></div>
<div class="flow-step"><small>thread 2</small><strong>은행 대사</strong><p>입출금 ↔ 계약·세금계산서·카드를 잇는다</p></div>
<div class="flow-step"><small>thread 3</small><strong>지출 요약</strong><p>영수증을 식비·교통·생활로 모은다</p></div>
</div>

<div class="board" style="margin-top:18px">
<div class="board-header"><span>왜 나누면 빠른가</span><span class="status-pill">독립 작업</span></div>
<div class="panel-body"><div class="list">
<p>세 조사는 서로의 결과를 기다리지 않습니다. 그래서 순서대로가 아니라 한꺼번에 돌립니다.</p>
<p>실습 코드는 mock에서도 스레드로 동시에 실행해 fan-out을 그대로 보여 줍니다. 키가 있으면 같은 일을 서브에이전트가 맡습니다.</p>
</div></div>
</div>
</section>

<section class="slide">
<div class="section-head">
<div>
<div class="eyebrow">4 · 발견</div>

## 영수증 없는 89,000원

</div>
<p class="section-note">카드 대사가 흥미로운 걸 찾습니다. 명세서에는 일곱 줄이 있는데 영수증은 다섯 장뿐입니다. 두 줄이 비어 있습니다.<br>
쿠팡 89,000원에는 영수증이 없습니다. 넷플릭스 17,000원도 없습니다. 하나는 분실 또는 미수령, 하나는 구독으로 추정됩니다. 이게 조사가 내놓는 실제 결과입니다.</p>
</div>

<div class="panel">
<div class="panel-head"><strong>research_notes/card_reconcile.md</strong><span>fan-out 한 갈래의 산출</span></div>
<div class="panel-body">

```text
# 카드 명세서 대사 — 신한카드 (205,900원)
- ✅ 스타벅스 강남R점 11,500원 ↔ 영수증 「스타벅스 강남R점」
- ✅ GS25 역삼점 8,400원 ↔ 영수증 「GS25 역삼점」
- ✅ 카카오T 택시 14,300원 ↔ 영수증 「카카오T 택시」
- ✅ 광화문 국밥 27,000원 ↔ 영수증 「광화문 국밥」
- ⚠️ 쿠팡(주) 89,000원 — 매칭 영수증 없음
- ✅ 올리브영 강남본점 38,700원 ↔ 영수증 「올리브영 강남본점」
- ⚠️ 넷플릭스 17,000원 — 매칭 영수증 없음
```

</div>
</div>

<p class="section-note" style="margin-top:16px">Ch0에서 문서를 서로 연결해 둔 설계가 여기서 결실을 맺습니다. 카드 명세서와 영수증이 일부러 어긋나게 만들어졌고, 조사가 그 틈을 정확히 집어냅니다.</p>
</section>

<section class="slide">
<div class="section-head">
<div>
<div class="eyebrow">핸즈온 · 43분</div>

## 직접 돌린다 — research_orchestrator.py

</div>
<p class="section-note">Ch2가 떨군 classified 레코드를 읽어 세 갈래로 조사합니다. 키가 없으면 <code>--mock</code>으로 결정론적 대사를 돌려 같은 노트와 브리프를 만듭니다.<br>
끝나면 research_notes에 세 개의 노트가, workspace에 brief_draft.md가 생깁니다.</p>
</div>

<div class="board">
<div class="board-header"><span>실행</span><span class="status-pill">터미널</span></div>
<div class="stack">
<div class="row"><div class="code">1</div><div class="copy"><strong>먼저 — Ch2 적재(없으면)</strong><p><code>uv run python3 ch2-langgraph-agent/intake_graph.py --mock</code></p></div><div class="store">classified</div></div>
<div class="row"><div class="code">2</div><div class="copy"><strong>fan-out 조사</strong><p><code>uv run python3 ch3-deepagents/research_orchestrator.py --mock</code></p></div><div class="store">노트 3</div></div>
</div>
</div>

<div class="panel" style="margin-top:18px">
<div class="panel-head"><strong>출력 — 동시에 돌고 종합된다</strong><span>brief_draft.md</span></div>
<div class="panel-body">

```text
▶ 조사 대상 10건
  [plan] write_todos → card_reconcile / bank_reconcile / spend_summary
  [task] bank_reconcile → research_notes/bank_reconcile.md
  [task] card_reconcile → research_notes/card_reconcile.md
  [task] spend_summary → research_notes/spend_summary.md
  [synthesize] → workspace/brief_draft.md

## 짚어야 할 것
- ⚠️ 쿠팡(주) 89,000원 — 매칭 영수증 없음
- ⚠️ 넷플릭스 17,000원 — 매칭 영수증 없음
- ⚠️ 월세 이체 -650,000원(출금) — 대응 문서 없음
```

</div>
</div>

<p class="section-note" style="margin-top:16px">전체 파일은 <code>ch3-deepagents/research_orchestrator.py</code>. mock은 스레드 동시 실행으로 fan-out을, 키가 있으면 <code>create_deep_agent</code>가 서브에이전트로 같은 조사를 맡습니다.</p>
</section>

<section class="slide">
<div class="section-head">
<div>
<div class="eyebrow">마무리</div>

## 다음 — 조사를 지식으로 남긴다

</div>
<p class="section-note">조사가 끝나 노트와 초안이 생겼습니다. 다만 노트는 흩어진 메모입니다. 다음 달 인박스에도 다시 쓰려면 표준 형식으로 쌓아 둬야 합니다.<br>
Ch4에서는 이 결과를 OKF 지식 항목으로 적재하고, 브리프 쓰는 절차를 Skill로 묶고, 파일과 메일을 MCP로 연결합니다.</p>
</div>

<div class="grid-3">
<div class="panel"><div class="panel-head"><strong>지금 손에 든 것</strong></div><div class="panel-body"><div class="list">
<p>fan-out 조사 오케스트레이터</p>
<p>research_notes 3건 · brief_draft.md</p>
</div></div></div>
<div class="panel"><div class="panel-head"><strong>Ch4에서 할 것</strong></div><div class="panel-body"><div class="list">
<p>SKILL.md · MCP 파일/메일</p>
<p>OKF 지식 적재 · plugin 패키징</p>
</div></div></div>
<div class="panel"><div class="panel-head"><strong>최종 목적지</strong></div><div class="panel-body"><div class="list">
<p>인박스 한 통 → 검증된 브리프</p>
<p>Ch6 통합 캡스톤</p>
</div></div></div>
</div>

<div class="board" style="margin-top:18px">
<div class="board-header"><span>참고 자료</span><span class="status-pill">출처</span></div>
<div class="panel-body"><div class="list">
<p><a href="https://blog.langchain.com/deep-agents/">LangChain Deep Agents</a> · <a href="https://github.com/langchain-ai/deepagents">deepagents 0.6</a></p>
<p><a href="https://www.anthropic.com/engineering/building-effective-agents">Anthropic — Orchestrator-Worker</a> · <a href="https://martinfowler.com/articles/exploring-gen-ai/harness-engineering.html">Harness Engineering</a></p>
</div></div>
</div>
</section>


<nav class="chapnav">
<div class="board" style="margin-top:8px">
<div style="display:grid;grid-template-columns:1fr auto 1fr;gap:14px;align-items:center">
<a href="/chapters/chapter-2" style="color:inherit;text-decoration:none;font-weight:900;font-size:14px">← Ch2 · LangGraph 하네스</a>
<a href="/toc" style="color:var(--forest);text-decoration:none;font-weight:900;font-size:13px;background:rgba(148,210,189,.3);border:1px solid rgba(15,118,110,.24);border-radius:99px;padding:7px 16px">목차</a>
<a href="/chapters/chapter-4" style="color:inherit;text-decoration:none;font-weight:900;font-size:14px;text-align:right">Ch4 · Skills · MCP · 지식 →</a>
</div>
</div>
</nav>

</div>
</div>
