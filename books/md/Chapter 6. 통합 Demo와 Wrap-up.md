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

<p class="lead">앞 다섯 챕터에서 부품을 따로 만들어 봤습니다. 이 챕터에서는 새로 짜지 않습니다.<br>
부품을 끼워, 메일 봉투 한 통이 분류부터 검증까지 한 번에 흐르는 엔드투엔드를 배선합니다.</p>

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

<p class="section-note" style="margin-top:16px">분류 모델을 더 좋은 것으로 바꿔도, 검증자를 다른 팀 것으로 바꿔도 배선은 그대로입니다. 계약이 경계를 지켜 줍니다.</p>
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
<div class="flow-step"><small>Ch3</small><strong>fan-out 대사 3갈래</strong><p>카드·은행 명세서↔영수증 대사 + 지출 집계 → research_notes/</p></div>
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

<div class="grid-2" style="margin-top:16px">
<div class="panel"><div class="panel-head"><strong>왜 import만으로 되나</strong></div><div class="panel-body"><div class="list">
<p>각 단계가 돌려준 산출물(classified·notes·knowledge_base)을 다음 단계가 디렉터리 규약으로 집어 옵니다.</p>
<p>그래서 함수끼리 인자를 길게 주고받지 않아도 됩니다 — 파일이 계약입니다.</p>
</div></div></div>
<div class="panel"><div class="panel-head"><strong>한 군데만 실선, 나머지는 목</strong></div><div class="panel-body"><div class="list">
<p>봉투(메일)는 목, 검증(A2A)·파일(MCP)은 실선. 외부통합을 둘로 묶어 8시간에 소화합니다.</p>
<p><code>--a2a</code>를 빼면 검증도 목으로 돌아 키 없이 끝까지 돕니다.</p>
</div></div></div>
</div>

<div class="board" style="margin-top:18px">
<div class="board-header"><span>실행</span><span class="status-pill">터미널</span></div>
<div class="stack">
<div class="row"><div class="code">a</div><div class="copy"><strong>전 구간 — 오프라인</strong><p><code>uv run python3 ch6-integration/analyst_app.py --mock</code><br><span style="color:var(--muted)">성공 기준: <code>[1/6]</code>~<code>[6/6]</code>이 차례로 찍히고 <code>workspace/verified_brief.md</code>가 PASS로 끝난다.</span></p></div><div class="store">엔드투엔드</div></div>
<div class="row"><div class="code">b</div><div class="copy"><strong>검증만 실제 A2A</strong><p><code>uv run python3 ch6-integration/analyst_app.py --mock --a2a</code><br><span style="color:var(--muted)">성공 기준: [5/6]에서 <code>Agent Card</code>가 조회되고 실제 서버와 통신한다.</span></p></div><div class="store">A2A</div></div>
<div class="row"><div class="code">c</div><div class="copy"><strong>최종 산출물 열기</strong><p><code>cat workspace/verified_brief.md</code><br><span style="color:var(--muted)">성공 기준: 브리프 + 외부 검증 도장(PASS)이 한 파일에.</span></p></div><div class="store">완성</div></div>
</div>
</div>

<div class="panel" style="margin-top:18px">
<div class="panel-head"><strong>출력 — 한 줄기로 흐른 결과</strong><span>실제 stdout · 들여쓰기 줄은 각 모듈이 찍는다</span></div>
<div class="panel-body">

```text
[1/6] 분류·정규화 (Ch2 intake_graph)
  ▶ receipt_starbucks.png
    [classify] 스타벅스 강남R점 · 11,500원 · 신뢰도 1.00
    [verify] 통과  →  [persist] classified/receipt_starbucks.json
  ... (고액 2건 invoice_photo·contract_freelance는 ⏸ interrupt 후 자동 승인) ...
[2/6] fan-out 교차 조사 (Ch3 research_orchestrator)
  [plan] write_todos → card_reconcile / bank_reconcile / spend_summary
  [task] card_reconcile → research_notes/card_reconcile.md
  [task] bank_reconcile → research_notes/bank_reconcile.md
  [task] spend_summary  → research_notes/spend_summary.md
  [synthesize] → workspace/brief_draft.md
[3/6] OKF 지식 적재 (Ch4 okf_store)
  지식 항목 12개
[4/6] 브리프 작성 (Ch4 brief_skill 절차)
  → workspace/brief.md
[5/6] 외부 검증 (Ch5 A2A)
  → workspace/verified_brief.md
[6/6] 완료

분류 10건 · 조사 3갈래
최종 산출물: workspace/verified_brief.md
```

</div>
</div>

<div class="ask" style="margin-top:18px"><strong>직접 해보기.</strong> 한 단계를 일부러 빼면(예: <code>run_okf()</code> 주석) 다음 단계가 어떻게 될까요? 그리고 <code>workspace/</code>를 지우고 다시 돌리면?</div>

<details>
<summary>관찰 포인트</summary>
<div class="reveal">
<p>okf를 빼면 brief의 "짚을 점"이 비거나 줄어듭니다. 브리프가 knowledge_base의 gap·subscription을 읽어 채우기 때문입니다. 한 부품을 빼면 그 부품의 산출물에 기대던 다음 단계가 티 나게 빈약해집니다 — 계약으로 이어져 있다는 증거입니다.</p>
<p><code>workspace/</code>를 지우고 다시 돌리면 처음부터 똑같이 재생됩니다. 입력(sample_inbox)과 코드만 커밋돼 있으면 누가 돌려도 같은 산출물이 나옵니다 — 감사 가능하다는 뜻입니다.</p>
</div>
</details>

<div class="ask" style="margin-top:14px"><strong>한 건을 끝까지 따라가기.</strong> 카드 명세서에만 있고 영수증이 없는 결제 한 줄(예: 쿠팡)을 골라, 그 항목이 ① classified ② research_notes ③ knowledge_base ④ brief ⑤ verified_brief 다섯 산출물에서 각각 어떤 모양으로 나타나는지 추적하세요.</div>

<details>
<summary>추적 답</summary>
<div class="reveal">
<p>① <strong>classified/</strong> — 카드 명세서 RecordV1의 <code>항목[]</code> 한 줄(이름·금액). ② <strong>research_notes/card_reconcile.md</strong> — 대응 영수증이 없어 ⚠️ 줄로 표시. ③ <strong>knowledge_base/</strong> — 3만원 미만이면 <code>type: subscription</code>, 이상이면 <code>type: gap</code> 항목으로 적재. ④ <strong>brief.md</strong> — write_brief가 그 프런트매터를 읽어 "짚을 점"에 <code>(gap) 쿠팡(주)</code> 한 줄로. ⑤ <strong>verified_brief.md</strong> — 검증자가 영수증 없는 거래를 <em>독립으로 다시 세서</em> 브리프가 그 항목을 포함하는지 대조 → 모두 짚었으면 PASS. 한 줄의 데이터가 다섯 번 모양을 바꾸지만 계약(이름·금액)은 끝까지 보존됩니다.</p>
</div>
</details>

<div class="board" style="margin-top:18px">
<div class="board-header"><span>막히면</span><span class="status-pill">트러블슈팅</span></div>
<div class="stack">
<div class="row"><div class="code">!</div><div class="copy"><strong>ModuleNotFoundError: intake_graph</strong><p>레포 루트에서 <code>uv run</code> 하세요. analyst_app이 <code>sys.path</code>에 ch1~5를 끼우는데 cwd 기준이라 다른 폴더에서 돌리면 깨집니다.</p></div><div class="store">경로</div></div>
<div class="row"><div class="code">!</div><div class="copy"><strong>[5/6]에서 멈춤(--a2a)</strong><p><code>--a2a</code>는 9610 포트에 verifier_agent를 띄웁니다. 포트 점유 시 기동 실패 — 이전 프로세스를 끄거나 <code>--a2a</code> 없이 목으로 돌립니다.</p></div><div class="store">A2A</div></div>
<div class="row"><div class="code">!</div><div class="copy"><strong>verified_brief가 NEEDS_REVISION</strong><p>버그 아님 — 브리프가 gap을 빠뜨리면 검증자가 정직하게 반려합니다. brief.md "짚을 점"과 verified_brief의 "독립 재계산"을 비교하세요.</p></div><div class="store">정상</div></div>
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

<div class="board" style="margin-top:18px">
<div class="board-header"><span>하루를 관통한 축 — 3계층</span><span class="status-pill">멘탈 모델</span></div>
<div class="panel-body">
<div class="flow" style="grid-template-columns:repeat(3,minmax(0,1fr))">
<div class="flow-step"><small>Framework</small><strong>LangChain</strong><p>LLM·도구 연결 — "도구 상자" <span class="badge">Ch2</span></p></div>
<div class="flow-step"><small>Runtime</small><strong>LangGraph</strong><p>상태·분기·체크포인트 — "작업 공정표" <span class="badge">Ch2</span></p></div>
<div class="flow-step"><small>Harness</small><strong>DeepAgents</strong><p>계획·파일·서브에이전트 — "현장 관리자" <span class="badge">Ch3</span></p></div>
</div>
<p style="margin-top:8px">그 위에 Skills(절차)·MCP(연결)·A2A(협업)를 얹어 검증된 브리프까지. 위 여덟 역량은 전부 이 축의 어느 칸에 속합니다.</p>
</div>
</div>
</section>

<section class="slide">
<div class="section-head">
<div>
<div class="eyebrow">현실</div>

## 데모와 프로덕션 사이

</div>
<p class="section-note">이 캡스톤은 결정론적 목으로 끝까지 돕니다. 학습엔 좋지만, 실선으로 바꾸면 새 문제가 생깁니다. 무엇이 깨질지 미리 압니다.</p>
</div>

<div class="grid-2">
<div class="panel"><div class="panel-head"><strong>지금은 목이라 숨은 것</strong></div><div class="panel-body"><div class="list">
<p><strong>추출 비결정성</strong> — <code>--mock</code>은 gold를 베껴 100% 재현됩니다. 실모델 멀티모달은 신뢰도가 흔들리고 같은 영수증도 매번 달라져, 신뢰도 임계 HITL 멈춤(Ch2)이 진짜 안전장치가 됩니다.</p>
<p><strong>fan-out 비용·실패</strong> — 세 갈래가 실제 LLM 호출이면 토큰·지연·부분 실패가 곱해집니다. 한 갈래가 죽어도 나머지가 끝나게(부분 산출 허용) 설계해야 합니다.</p>
</div></div></div>
<div class="panel"><div class="panel-head"><strong>경계를 넘을 때</strong></div><div class="panel-body"><div class="list">
<p><strong>A2A 검증자 신뢰</strong> — 외부 에이전트의 PASS도 결국 하나의 판단입니다. Agent Card 서명·결과 재현 로그를 남겨야 "도장"이 감사 가능해집니다.</p>
<p><strong>상태·재현</strong> — workspace를 지워도 복원되는 건 입력이 커밋돼 있어서입니다. 실선 메일·DB에선 입력이 흐르므로 체크포인터(SQLite·Postgres)와 멱등 적재가 필요합니다.</p>
</div></div></div>
</div>

<div class="board" style="margin-top:18px">
<div class="board-header"><span>오늘 실습 → 프로덕션</span><span class="status-pill">바뀌는 것</span></div>
<div class="panel-body">

| 항목 | 오늘 실습 | 프로덕션 |
|---|---|---|
| Checkpointer | InMemorySaver | Postgres/SQLite |
| MCP 전송 | stdio(subprocess) | Streamable HTTP |
| A2A | localhost:9610 | 서비스 디스커버리(k8s) |
| 모니터링 | 콘솔 로그 | LangSmith/LangFuse |
| 인증 | 없음 | OAuth2 / API Key |
| 스케줄링 | 수동 실행 | Celery / Cloud Scheduler |

</div>
</div>

<div class="board" style="margin-top:18px">
<div class="board-header"><span>평가 최소 프레임 — "돌았다"를 넘어</span><span class="status-pill">측정자</span></div>
<div class="panel-body">

| 지표 | 정의 | 목표 예시 |
|---|---|---|
| 작업 완료율 | 요청 작업을 끝낸 비율 | 90%+ |
| 도구 호출 정확도 | 올바른 도구·인자 선택 | 95%+ |
| 환각률 | 근거 없는 응답 비율 | ≤5% |
| 건당 지연 | 요청당 평균 처리 시간 | ≤5초 |
| 건당 비용 | 요청당 평균 토큰·비용 | 예산 내 |

</div>
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
<p><strong>평가·관측</strong> — "돌았다"를 넘어 산출물 품질을 자동 채점(LLM-as-judge·골든셋)하고 단계별 토큰·지연·실패율을 추적해야 회귀를 잡습니다(<a href="https://docs.smith.langchain.com/">LangSmith</a> 류 트레이싱).</p>
<p><strong>워크플로 vs 에이전트 규율</strong> — 이 파이프라인은 대부분 워크플로(고정 단계)이고 자율 루프는 Ch3 한 곳뿐. 단계가 정해졌으면 자율성을 일부러 줄이는 게 더 싸고 안정적입니다.</p>
</div></div></div>
</div>

<div class="board" style="margin-top:18px">
<div class="board-header"><span>오늘의 한 줄</span><span class="status-pill">정리</span></div>
<div class="panel-body"><div class="list">
<p>LLM만으론 부족 → <strong>Agent</strong>. Agent만으론 부족 → <strong>Harness</strong>. Harness만으론 부족 → <strong>Skills·MCP·A2A 생태계</strong>. 오늘 이 사다리를 아래에서 위로 직접 밟았습니다.</p>
<p style="font-weight:800">"에이전트 개발은 LLM을 호출하는 게 아니라, LLM이 효과적으로 일할 환경(Harness)을 설계하는 것이다."</p>
</div></div>
</div>

<div class="board" style="margin-top:18px">
<div class="board-header"><span>참고 자료</span><span class="status-pill">출처</span></div>
<div class="panel-body"><div class="list">
<p><a href="https://www.anthropic.com/engineering/building-effective-agents">Anthropic — Building Effective Agents</a> · <a href="https://blog.langchain.com/deep-agents/">LangChain Deep Agents</a></p>
<p><a href="https://modelcontextprotocol.io/">MCP</a> · <a href="https://a2a-protocol.org/">A2A</a> · <a href="https://agentskills.io/">Agent Skills</a> · <a href="https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf">OKF — Google Cloud</a></p>
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
