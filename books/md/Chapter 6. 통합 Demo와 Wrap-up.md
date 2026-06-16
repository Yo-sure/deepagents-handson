---
layout: page
title: Ch6 · 통합 캡스톤
sidebar: false
aside: false
pageClass: lec-page
---

<div class="lec">
<div class="deck">

<section class="slide hero">
<div>
<div class="eyebrow">Chapter 6 · 통합 캡스톤 · Wrap-up</div>

# 부품을,<br>한 줄기로 잇는다

<p class="lead">여섯 개의 부품을 따로 만들어 봤습니다. 추출, 적재, 조사, 지식, 브리프, 외부 검증.<br>
이 챕터에서는 새로 짜지 않습니다. 부품을 끼워 메일 봉투 한 통이 분류부터 검증까지 한 번에 흐르는 엔드투엔드를 배선합니다.</p>

<div class="kicker">
<div class="metric"><span class="num">90</span><strong>분</strong><span>이론 15 · 핸즈온 75</span></div>
<div class="metric"><span class="num">6</span><strong>부품 배선</strong><span>analyst_app.py</span></div>
<div class="metric"><span class="num">1</span><strong>검증된 브리프</strong><span>verified_brief.md</span></div>
</div>
</div>

<div class="board">
<div class="board-header"><span>이 챕터가 끝나면</span><span class="status-pill">완성</span></div>
<div class="stack">
<div class="row"><div class="code">1</div><div class="copy"><strong>엔드투엔드 1회</strong><p>봉투 → 분류 → 조사 → 지식 → 브리프 → 검증</p></div><div class="store">전체</div></div>
<div class="row"><div class="code">2</div><div class="copy"><strong>부품 배선의 원리</strong><p>계약을 재사용해 새로 짜지 않는다</p></div><div class="store">조립</div></div>
<div class="row"><div class="code">3</div><div class="copy"><strong>적용 메모</strong><p>내 일에 가져갈 씨앗 정리</p></div><div class="store">전이</div></div>
</div>
</div>
</section>

<section class="slide">
<div class="section-head">
<div>
<div class="eyebrow">1 · 원리</div>

## 새로 짜지 않는다

</div>
<p class="section-note">캡스톤의 핵심은 절제입니다. 각 챕터의 모듈을 import 해 그 함수를 부릅니다. analyst_app.py에는 새 로직이 거의 없습니다.<br>
이게 가능한 이유는 처음부터 계약을 맞춰 뒀기 때문입니다. 모두 RecordV1을 주고받고, 같은 디렉터리 규약을 씁니다. 부품을 갈아끼워도 계약은 그대로입니다.</p>
</div>

<div class="grid-2">
<div class="panel"><div class="panel-head"><strong>계약 — RecordV1</strong><span>Ch0에서 못박음</span></div><div class="panel-body"><div class="list">
<p>추출도 조사도 검증도 같은 레코드를 봅니다</p>
<p>중간에 포맷이 바뀌지 않아 배선이 단순합니다</p>
</div></div></div>
<div class="panel"><div class="panel-head"><strong>규약 — 디렉터리</strong><span>workspace/ 단계별</span></div><div class="panel-body"><div class="list">
<p>classified → research_notes → knowledge_base → brief → verified</p>
<p>한 단계의 출력이 다음 단계의 입력입니다</p>
</div></div></div>
</div>

<p class="section-note" style="margin-top:16px">분류 모델을 더 좋은 것으로 바꿔도, 검증자를 다른 팀 것으로 바꿔도 배선은 그대로입니다. 계약이 경계를 지켜 줍니다. 이게 8시간 동안 부품을 따로 만든 이유입니다.</p>
</section>

<section class="slide">
<div class="section-head">
<div>
<div class="eyebrow">2 · 흐름</div>

## 봉투 한 통이 흐르는 길

</div>
<p class="section-note">메일 봉투가 도착하면 여섯 단계를 지납니다. 앞 다섯은 한 프로세스 안에서, 마지막 검증은 프로세스 경계를 넘어 A2A로 나갑니다.<br>
각 단계 옆에 그 일을 맡은 챕터를 적었습니다.</p>
</div>

<div class="flow" style="grid-template-columns:repeat(3,minmax(0,1fr))">
<div class="flow-step"><small>Ch2</small><strong>분류·정규화</strong><p>봉투의 문서를 RecordV1로 → classified/</p></div>
<div class="flow-step"><small>Ch3</small><strong>fan-out 조사</strong><p>나눠 대사 → research_notes/ · brief_draft</p></div>
<div class="flow-step"><small>Ch4</small><strong>OKF 적재</strong><p>거래처·구독·gap → knowledge_base/</p></div>
<div class="flow-step"><small>Ch4</small><strong>브리프</strong><p>지식을 모아 한 장 → brief.md</p></div>
<div class="flow-step"><small>Ch5</small><strong>A2A 검증</strong><p>외부 에이전트에 제출 → verified_brief.md</p></div>
<div class="flow-step"><small>완료</small><strong>최종 산출</strong><p>검증 도장이 찍힌 브리프</p></div>
</div>
</section>

<section class="slide">
<div class="section-head">
<div>
<div class="eyebrow">핸즈온 · 75분</div>

## 직접 배선한다 — analyst_app.py

</div>
<p class="section-note">전 구간을 한 번에 흘립니다. <code>--mock</code>은 키 없이 끝까지 돌리고, <code>--a2a</code>를 더하면 검증 단계만 실제 A2A 서버를 띄워 통신합니다.<br>
각 단계가 앞서 만든 모듈을 그대로 부릅니다. 코드를 열어 보면 import와 호출이 대부분입니다.</p>
</div>

<div class="panel">
<div class="panel-head"><strong>analyst_app.py — 배선의 모양</strong><span>새 로직 없이 부품 호출</span></div>
<div class="panel-body">

```python
run_intake(mock)          # Ch2 — 봉투 문서 → classified/
ctx = run_research()      # Ch3 — fan-out → research_notes/ + brief_draft
run_okf()                 # Ch4 — OKF 지식 적재 → knowledge_base/
write_brief()             # Ch4 — 지식 모아 brief.md
run_verify(use_a2a)       # Ch5 — A2A 외부 검증 → verified_brief.md
```

</div>
</div>

<div class="board" style="margin-top:18px">
<div class="board-header"><span>실행</span><span class="status-pill">터미널</span></div>
<div class="stack">
<div class="row"><div class="code">a</div><div class="copy"><strong>전 구간 — 오프라인</strong><p><code>uv run python3 ch6-integration/analyst_app.py --mock</code></p></div><div class="store">엔드투엔드</div></div>
<div class="row"><div class="code">b</div><div class="copy"><strong>검증만 실제 A2A</strong><p><code>uv run python3 ch6-integration/analyst_app.py --mock --a2a</code></p></div><div class="store">A2A</div></div>
</div>
</div>

<div class="panel" style="margin-top:18px">
<div class="panel-head"><strong>출력 — 한 줄기로 흐른 결과</strong><span>analyst_app.py</span></div>
<div class="panel-body">

```text
[1/6] 분류·정규화 (Ch2 intake_graph)        → classified 10건
[2/6] fan-out 교차 조사 (Ch3)               → research_notes 3갈래
[3/6] OKF 지식 적재 (Ch4 okf_store)         → 지식 항목 12개
[4/6] 브리프 작성 (Ch4 brief_skill)         → brief.md
[5/6] 외부 검증 (Ch5 A2A)                   → verified_brief.md (PASS)
[6/6] 완료
```

</div>
</div>
</section>

<section class="slide">
<div class="section-head">
<div>
<div class="eyebrow">Wrap-up</div>

## 8시간이 남긴 것

</div>
<p class="section-note">하나의 인박스를 끝까지 처리하며 여덟 역량을 손으로 익혔습니다. 각 역량이 어느 부품에서 처음 나왔는지 돌아봅니다.</p>
</div>

<div class="grid-4">
<div class="panel"><div class="panel-head"><strong>멀티모달</strong><span>Ch1</span></div><div class="panel-body"><div class="list"><p>영수증 이미지 → RecordV1</p></div></div></div>
<div class="panel"><div class="panel-head"><strong>멀티에이전트</strong><span>Ch2·3</span></div><div class="panel-body"><div class="list"><p>직렬 파이프라인 · fan-out</p></div></div></div>
<div class="panel"><div class="panel-head"><strong>하네스 루프</strong><span>Ch3</span></div><div class="panel-body"><div class="list"><p>계획·위임·파일 퇴피</p></div></div></div>
<div class="panel"><div class="panel-head"><strong>MCP</strong><span>Ch4</span></div><div class="panel-body"><div class="list"><p>파일[실선]·메일[목]</p></div></div></div>
<div class="panel"><div class="panel-head"><strong>Skill</strong><span>Ch4</span></div><div class="panel-body"><div class="list"><p>SKILL.md 점진 공개</p></div></div></div>
<div class="panel"><div class="panel-head"><strong>Plugin · OKF</strong><span>Ch4</span></div><div class="panel-body"><div class="list"><p>얇은 패키징 · 표준 지식</p></div></div></div>
<div class="panel"><div class="panel-head"><strong>HITL</strong><span>Ch2</span></div><div class="panel-body"><div class="list"><p>고액·저신뢰 멈춤</p></div></div></div>
<div class="panel"><div class="panel-head"><strong>A2A</strong><span>Ch5</span></div><div class="panel-body"><div class="list"><p>프로세스·팀 경계 검증</p></div></div></div>
</div>
</section>

<section class="slide">
<div class="section-head">
<div>
<div class="eyebrow">전이</div>

## 내 일에 가져갈 씨앗

</div>
<p class="section-note">이 애널리스트는 인박스를 다뤘지만 골격은 어디에나 맞습니다. 입력을 계약으로 정규화하고, 나눠 조사하고, 지식으로 쌓고, 외부에 검증을 맡기는 흐름입니다.<br>
여러분의 문서 더미가 계약서든 로그든 논문이든, 부품을 갈아끼우면 같은 골격이 돕니다.</p>
</div>

<div class="grid-3">
<div class="panel"><div class="panel-head"><strong>바꿀 것</strong><span>부품</span></div><div class="panel-body"><div class="list">
<p>RecordV1 필드를 내 도메인에 맞게</p>
<p>조사 주제(reconcile 함수)를 내 질문으로</p>
</div></div></div>
<div class="panel"><div class="panel-head"><strong>그대로 둘 것</strong><span>골격</span></div><div class="panel-body"><div class="list">
<p>계약 중심 배선 · 디렉터리 규약</p>
<p>HITL 멈춤 · 외부 검증 경계</p>
</div></div></div>
<div class="panel"><div class="panel-head"><strong>더 볼 것</strong><span>다음</span></div><div class="panel-body"><div class="list">
<p>체크포인터를 SQLite·Postgres로</p>
<p>메일 목을 실제 IMAP·MCP로</p>
</div></div></div>
</div>

<div class="board" style="margin-top:18px">
<div class="board-header"><span>참고 자료</span><span class="status-pill">출처</span></div>
<div class="panel-body"><div class="list">
<p><a href="https://www.anthropic.com/engineering/building-effective-agents">Anthropic — Building Effective Agents</a> · <a href="https://blog.langchain.com/deep-agents/">LangChain Deep Agents</a></p>
<p><a href="https://modelcontextprotocol.io/">MCP</a> · <a href="https://a2a-protocol.org/">A2A</a> · <a href="https://agentskills.io/">Agent Skills</a> · <a href="https://github.com/google/open-knowledge-format">OKF</a></p>
</div></div>
</div>
</section>


<nav class="chapnav">
<div class="board" style="margin-top:8px">
<div style="display:grid;grid-template-columns:1fr auto 1fr;gap:14px;align-items:center">
<a href="/chapters/chapter-5" style="color:inherit;text-decoration:none;font-weight:900;font-size:14px">← Ch5 · A2A 역할 분리</a>
<a href="/toc" style="color:var(--forest);text-decoration:none;font-weight:900;font-size:13px;background:rgba(148,210,189,.3);border:1px solid rgba(15,118,110,.24);border-radius:99px;padding:7px 16px">목차</a>
<span></span>
</div>
</div>
</nav>

</div>
</div>
