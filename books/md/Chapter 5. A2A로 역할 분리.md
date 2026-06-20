---
layout: page
title: Ch5 · A2A 역할 분리
sidebar: false
aside: false
pageClass: lec-page
---

<div class="lec">
<div class="deck">

<section class="slide hero">
<div>
<div class="eyebrow">Chapter 5 · A2A 역할 분리</div>

# 밖에,<br>검증을 맡긴다

<p class="lead">브리프를 쓴 에이전트가 자기 브리프를 검증하면, 빠뜨린 항목도 "다 짚었다"고 확신합니다 — 같은 사각을 공유하니까.<br>
이 챕터에서 브리프를 외부 검증 에이전트에 A2A로 보냅니다. 그 에이전트는 서명 가능한 Agent Card로 자신을 밝히고, 원본 레코드를 독립으로 다시 계산해 PASS/FAIL을 답합니다.</p>

<div class="kicker">
<div class="metric"><span class="num">70</span><strong>분</strong><span>이론 34 · 핸즈온 33</span><span class="clk">예상 15:00–16:10 · 앞 ☕10분</span></div>
<div class="metric"><span class="num">5</span><strong>번째 모듈</strong><span>a2a_verify.py</span></div>
<div class="metric"><span class="num">1</span><strong>검증된 브리프</strong><span>verified_brief.md</span></div>
</div>
</div>

<div class="board">
<div class="board-header"><span>이 챕터가 끝나면</span><span class="status-pill">산출물</span></div>
<div class="stack">
<div class="row"><div class="code">1</div><div class="copy"><strong>Agent Card 조회</strong><p>well-known 경로에서 상대 에이전트의 자기소개</p></div><div class="store">신원</div></div>
<div class="row"><div class="code">2</div><div class="copy"><strong>SendMessage</strong><p>브리프를 보내고 Task 라이프사이클로 결과</p></div><div class="store">통신</div></div>
<div class="row"><div class="code">3</div><div class="copy"><strong>verified_brief.md</strong><p>외부 검증을 거친 최종 브리프</p></div><div class="store">검증</div></div>
</div>
</div>
</section>

<section class="slide">
<div class="section-head">
<div>
<div class="eyebrow">1 · 경계 · 9분</div>

## 서브에이전트와 무엇이 다른가

</div>
<p class="section-note">Ch3의 서브에이전트는 같은 프로세스 안에서 일을 나눴습니다. 내가 만든 에이전트가 내 함수를 부르는 구조입니다.<br>
A2A는 그 경계를 넘습니다. 상대는 다른 프로세스, 어쩌면 다른 팀이 운영하는 에이전트입니다. 내가 그 내부를 모르고도 카드와 메시지로 협업합니다.</p>
</div>

<div class="grid-2">
<div class="panel"><div class="panel-head"><strong>서브에이전트 — 인프로세스</strong><span>Ch3</span></div><div class="panel-body"><div class="list">
<p>같은 프로세스, 내가 만든 도구를 위임</p>
<p>내부를 다 알고 직접 호출합니다</p>
<p>fan-out으로 내 일을 나누는 데 맞습니다</p>
</div></div></div>
<div class="panel"><div class="panel-head"><strong>A2A — 프로세스·팀 경계</strong><span>Ch5</span></div><div class="panel-body"><div class="list">
<p>다른 프로세스, 다른 팀의 에이전트</p>
<p>내부를 몰라도 카드와 메시지로 협업</p>
<p>외부 검증·외부 서비스 호출에 맞습니다</p>
</div></div></div>
</div>

<p class="section-note" style="margin-top:16px">검증을 같은 프로세스 안에서 하면 결국 내 코드가 내 코드를 봅니다. 독립성이 없습니다. 검증자를 프로세스 밖으로 빼야 외부 관점이 생깁니다. 그래서 A2A를 씁니다.</p>

<div class="board" style="margin-top:18px">
<div class="board-header"><span>위임의 세 고도 — 무엇을 물려받나</span><span class="status-pill">컨텍스트 상속</span></div>
<div class="panel-body">

<div class="grid-3">
<div class="panel"><div class="panel-head"><strong>일반 서브에이전트</strong><span>Ch3 · 인프로세스</span></div><div class="panel-body"><div class="list">
<p>부모 대화의 <strong>압축 요약</strong>만 상속</p>
<p>격리된 컨텍스트·단발 결과 — 싸고 백그라운드 가능, 디테일은 뭉개질 수 있음</p>
</div></div></div>
<div class="panel"><div class="panel-head"><strong>FORK</strong><span>Anthropic 2026 · 인프로세스</span></div><div class="panel-body"><div class="list">
<p><strong>전체 컨텍스트</strong>를 무손실 상속(캐시 할인가)</p>
<p>요약으로 잃기 쉬운 맥락 보존용. 단, 현재 <em>인터랙티브 전용</em> — 백그라운드 포크는 아직 미제공</p>
</div></div></div>
<div class="panel"><div class="panel-head"><strong>A2A</strong><span>Ch5 · 프로세스 밖</span></div><div class="panel-body"><div class="list">
<p>컨텍스트를 <strong>공유 안 함</strong>(불투명)</p>
<p>AgentCard(계약) + Task(생명주기) + 메시지로만 협업. 내부·도구·메모리 비공개</p>
</div></div></div>
</div>

<p class="section-note" style="margin-top:12px"><strong>고르는 기준</strong>: 내가 양쪽을 다 소유하고 도구·메모리를 싸게 나눠 쓰고 싶다 → 인프로세스(요약이면 일반 서브에이전트, 전체 맥락이 필요하면 FORK). 상대가 <em>다른 소유자·벤더·언어·신뢰 영역</em>이다 → A2A. 세 가지는 경쟁이 아니라 <em>같은 "위임"의 다른 고도</em>입니다.</p>

</div>
</div>

<div class="ask" style="margin-top:18px"><strong>생각해보기.</strong> Ch4에서 붙인 MCP와 이번 A2A는 뭐가 다를까요? 둘 다 "외부와 통신"인데.</div>

<details>
<summary>정답 확인</summary>
<div class="reveal">
<p><strong>MCP는 에이전트→도구</strong>입니다. 내 에이전트가 파일·DB·API 같은 <em>도구</em>를 끌어다 씁니다(Ch4 지식 베이스). <strong>A2A는 에이전트↔에이전트</strong>입니다. 상대도 자율로 판단하는 동급(peer) 에이전트라, 내가 그 내부를 모릅니다. <span style="color:var(--muted)">(A2A는 2025-04 구글이 발표한 뒤 Linux Foundation에 기증됐고, 지금은 MCP와 함께 AAIF에서 관리됩니다 — 발표와 기증은 시점이 다릅니다.)</span></p>
<p>그래서 MCP엔 "도구 목록"이, A2A엔 "Agent Card(상대의 자기소개)"가 있습니다. 둘은 경쟁이 아니라 보완 — 한 시스템이 MCP로 도구를 쓰면서 A2A로 다른 에이전트와 협업합니다.</p>
</div>
</details>

<div class="board" style="margin-top:18px">
<div class="board-header"><span>REST 한 번이면 되는데 왜 A2A인가</span><span class="status-pill">한 걸음 더</span></div>
<div class="panel-body"><div class="list">
<p>"검증 요청 보내고 결과 받기"는 REST 한 번이면 됩니다. A2A가 사는 건 그 한 번으로 안 끝나는 일에서입니다 — ① <strong>멀티턴</strong>: 상대가 작업 도중 <code>input-required</code>(추가 정보)·<code>auth-required</code>(인증)로 되묻고 이어감 · ② <strong>장기 Task</strong>: 몇 분~몇 시간 걸리는 작업을 <code>submitted→working→completed</code> 상태로 추적, 끊겨도 폴링·웹훅으로 재개 · ③ <strong>능력 협상</strong>: 상대가 Agent Card의 <code>skills</code>를 자율로 골라 처리.</p>
<p>그래서 A2A는 <em>도구 호출</em>이 아니라 <em>맡긴 일의 생애주기</em>를 표준화합니다. 우리 실습은 가장 단순한 <strong>블로킹 1왕복</strong>이라 이 중 일부만 씁니다 — 천장은 훨씬 높습니다.</p>
<p class="section-note" style="margin-top:6px">위상도 정리됐습니다 — A2A는 <strong>v1.0</strong>에 이르렀고 Linux Foundation 산하 중립 거버넌스(MCP·AGENTS.md 등과 함께)로 옮겨가, Python·JS·Java·Go·.NET 다섯 SDK로 구현됩니다. 카드를 서명하는 <strong>Signed Agent Card</strong>가 정식 항목이 된 것도 이 흐름인데, 바로 그 신원·서명이 다음 절에서 우리가 만질 부분입니다.</p>

```mermaid
stateDiagram-v2
    [*] --> submitted
    submitted --> working
    working --> input_required: 추가 정보 필요
    working --> auth_required: 인증 필요
    input_required --> working: 사람이 응답
    auth_required --> working: 인증 완료
    working --> completed
    completed --> [*]
    note right of input_required: REST 한 번으론<br/>표현 못 하는 구간
```

</div></div>
</div>
</section>

<section class="slide">
<div class="section-head">
<div>
<div class="eyebrow">2 · 신원 · 7분</div>

## Agent Card — 서명 가능한 자기소개

</div>
<p class="section-note">A2A 에이전트는 자신을 well-known 경로에 카드로 밝힙니다. 이름, 버전, 무슨 기술(skill)을 제공하는지, 어디로 보내야 하는지가 담깁니다.<br>
상대를 부르기 전에 이 카드를 먼저 읽습니다. 카드를 찾는 길은 셋입니다 — <strong>well-known URI</strong>(도메인의 <code>/.well-known/agent-card.json</code>, 우리가 쓰는 가장 단순한 길) · <strong>레지스트리</strong>(중앙 목록에서 능력으로 검색) · <strong>직접 설정</strong>(URL을 하드코딩). 누구인지 확인하고 통신을 시작합니다. A2A 스펙(현재 v1.0 GA)은 카드를 <strong>JWS</strong>(<em>JSON Web Signature, RFC 7515</em>)로 서명할 수 있게 합니다(0.3.0에서 도입). 서명은 카드가 변조되지 않았고 서명자가 그 키를 가졌음을 증명합니다. 다만 그 키를 누구 것으로 믿을지는 공개키 배포·도메인 바인딩 같은 별도 신뢰 설정의 문제라, 서명만으로 신원이 보장되진 않습니다.</p>
<p class="section-note" style="margin-top:14px"><strong>신뢰 경계가 다르면 위험도 따라옵니다.</strong> A2A는 <em>대화 방식</em>을 표준화할 뿐, 누가 누구를 부르는지의 <em>제어</em>는 호출자 몫으로 남습니다. 그래서 외부 에이전트로 엮을 때 두 가지를 직접 막아야 합니다 — ① <strong>순환 호출</strong>: A와 B가 서로를 부르며 도는 걸 프로토콜이 대신 끊어 주지 않으니 hop 수 제한·Task 타임아웃·완료(REJECTED) 재진입 거부를 둡니다. ② <strong>카드 스푸핑·프롬프트 인젝션</strong>: 카드나 메시지 본문이 악의적일 수 있어, 서명 검증만으로 끝이 아니라 받은 지시를 그대로 신뢰하지 않는 경계가 필요합니다. 이 실습은 같은 소유자의 로컬 에이전트라 위험이 약하지만, 다른 벤더를 붙이는 순간 1순위 고려사항이 됩니다.</p>
</div>

<div class="panel">
<div class="panel-head"><strong>GET /.well-known/agent-card.json</strong><span>검증 에이전트의 자기소개</span></div>
<div class="panel-body">

```json
{
  "name": "세무·정합성 검증 에이전트",
  "description": "제출된 인박스 브리프를 분류 레코드와 대사해 누락·불일치를 검증한다.",
  "supportedInterfaces": [{ "url": "http://localhost:9610",
                            "protocolBinding": "JSONRPC", "protocolVersion": "1.0" }],
  "version": "1.0.0",
  "capabilities": { "streaming": false },
  "defaultInputModes": ["text/plain"],
  "defaultOutputModes": ["text/plain"],
  "skills": [{ "id": "verify-brief", "name": "브리프 검증",
              "description": "브리프의 '짚을 점'이 실제 레코드와 맞는지 독립 재계산으로 확인한다.",
              "tags": ["verify", "reconcile", "audit"],
              "examples": ["이 브리프를 검증해줘", "짚을 점이 빠지지 않았는지 확인"] }]
}
```

</div>
</div>

<p class="section-note" style="margin-top:16px">위 JSON은 <code>AgentCard</code> 타입을 직렬화한 결과입니다. 코드에선 <code>AgentCard(...)</code>로 만들어 스키마를 맞추고, JSON을 손으로 쓰지 않습니다.</p>
</section>

<section class="slide">
<div class="section-head">
<div>
<div class="eyebrow">3 · 통신 · 10분</div>

## SendMessage와 Task 라이프사이클

</div>
<p class="section-note">카드를 읽었으면 메시지를 보냅니다. 클라이언트가 <code>send_message</code>로 브리프를 싣고, 서버는 그 일을 하나의 Task로 받아 상태를 단계별로 올립니다.<br>
제출됨에서 작업 중으로, 결과를 아티팩트로 붙이고 완료로 닫습니다. 클라이언트는 그 마지막 결과를 읽습니다.</p>
</div>

<div class="panel">
<div class="panel-head"><strong>Task 상태머신 — 정상 경로와 갈림길</strong><span>submitted → working → completed</span></div>
<div class="panel-body">

```mermaid
stateDiagram-v2
    [*] --> submitted
    submitted --> working
    working --> completed: artifact 첨부
    completed --> [*]
    submitted --> rejected
    working --> failed
    working --> canceled
    working --> input_required: 추가 입력 필요
    working --> auth_required: 인증 필요
```

</div>
</div>

<<< ../../ch5-a2a/a2a_verify.py#a2a-client{python}

<p class="section-note" style="margin-top:16px">함정 둘. ① <code>message_id</code>를 빼면 서버가 메시지를 식별 못 해 거절합니다. ② <code>send_message</code> 스트림은 응답을 <strong>튜플</strong>로 흘려보내므로 <code>resp[0]</code>로 벗겨 읽습니다. 그 안의 <code>StreamResponse</code>는 <strong>oneof</strong>(task·message·status_update·artifact_update 중 하나만 설정)라, 설정된 필드만 골라 읽어야 합니다.</p>

<p class="section-note" style="margin-top:12px"><code>HasField</code>를 그냥 부르면 안 됩니다 — 미설정·스칼라 oneof 필드에선 예외(<code>ValueError</code>/<code>AttributeError</code>)를 던지기 때문에, 아래처럼 <code>_has()</code>로 감싸 안전하게 검사한 뒤 설정된 필드에서만 텍스트를 모읍니다.</p>

<<< ../../ch5-a2a/a2a_verify.py#a2a-stream{python}

<div class="panel" style="margin-top:16px">
<div class="panel-head"><strong>한 번의 검증 왕복</strong><span>카드 조회 → 전송 → 결과 수신</span></div>
<div class="panel-body">

```mermaid
sequenceDiagram
    participant C as Client · 브리프 작성자
    participant V as Verifier · 외부 검증
    C->>V: GET /.well-known/agent-card.json
    V-->>C: Agent Card (skill · endpoint)
    C->>V: send_message(브리프) — Task submitted
    V->>V: 원본 레코드로 독립 재계산 (working)
    V-->>C: artifact PASS / NEEDS_REVISION — completed
```

</div>
</div>

<div class="board" style="margin-top:18px">
<div class="board-header"><span>A2A 한눈에 — 바인딩·통신·상태</span><span class="status-pill">레퍼런스</span></div>
<div class="panel-body">

<div class="matrix" style="grid-template-columns:88px repeat(3,minmax(0,1fr))">
<div class="cell head">바인딩</div>
<div class="cell head">JSON-RPC</div>
<div class="cell head">gRPC</div>
<div class="cell head">REST</div>
<div class="cell axis">형식</div>
<div class="cell">JSON over HTTP</div>
<div class="cell">protobuf</div>
<div class="cell">HTTP + JSON</div>
<div class="cell axis">강점</div>
<div class="cell active">양방향 · 기본</div>
<div class="cell">고성능 스트리밍</div>
<div class="cell">curl 호환</div>
<div class="cell axis">적합</div>
<div class="cell active">범용 · 이 실습</div>
<div class="cell">내부 고throughput</div>
<div class="cell">간단한 통합</div>
</div>

<div class="legend">
<span class="lpill"><span class="ldot"></span>이 실습이 쓰는 길</span>
<span class="lpill"><span class="ldot blue"></span>대안 바인딩</span>
</div>

<div class="grid" style="grid-template-columns:1fr 1fr;gap:12px;margin-top:14px">
<div class="panel"><div class="panel-head"><strong>블로킹</strong><span>즉답</span></div><div class="panel-body"><div class="list"><p><code>message/send</code>에 <code>returnImmediately=false</code> — 완료까지 한 연결로 기다려 결과를 한 번에 받는다(우리 실습)</p></div></div></div>
<div class="panel"><div class="panel-head"><strong>폴링</strong><span>tasks/get</span></div><div class="panel-body"><div class="list"><p>즉시 Task <code>id</code>만 받고, <code>tasks/get</code>으로 상태를 주기적으로 물어 완료를 기다린다(장기 작업)</p></div></div></div>
<div class="panel"><div class="panel-head"><strong>스트리밍</strong><span>SSE</span></div><div class="panel-body"><div class="list"><p>Server-Sent Events로 진행·부분 결과를 실시간으로 흘려받는다</p></div></div></div>
<div class="panel"><div class="panel-head"><strong>웹훅</strong><span>pushNotification</span></div><div class="panel-body"><div class="list"><p>완료 시 상대가 내 콜백 URL로 POST — 연결을 붙들 필요 없이 통지받는다</p></div></div></div>
</div>
<p class="section-note" style="margin-top:10px">같은 <code>message/send</code>가 <code>returnImmediately</code> 토글 하나로 블로킹↔폴링을 오갑니다. 작업이 길수록 폴링·스트리밍·웹훅으로 올라갑니다 — 우리는 1왕복이라 블로킹으로 충분합니다.</p>
<div class="list" style="margin-top:12px">
<p><strong>Task 상태</strong> — <code>submitted→working→completed</code>가 정상 경로. 그 외 <strong>failed·canceled·rejected·input-required·auth-required</strong>로 끝나거나 멈춥니다(위 상태머신).</p>
<p><strong>메시지의 콘텐츠 단위는 Part</strong> — 한 메시지/아티팩트는 <code>TextPart</code>(글)·<code>FilePart</code>(파일)·<code>DataPart</code>(구조화 JSON)의 묶음입니다. 우리는 브리프를 <code>TextPart</code> 하나로 보내지만, 이 구조라 텍스트+이미지+JSON을 한 메시지에 실어 보내는 멀티모달이 가능합니다.</p>
</div>
</div>
</div>
</section>

<section class="slide">
<div class="section-head">
<div>
<div class="eyebrow">4 · 제공 모듈 · 8분</div>

## 검증자는 독립으로 다시 센다

</div>
<p class="section-note">검증 에이전트는 과정에서 제공 모듈로 주어집니다. 재현성을 위해 모델 없이 규칙으로 동작합니다.<br>
핵심은 독립 재계산입니다. 브리프의 문장을 믿지 않고, 분류 레코드에서 영수증 없는 거래를 처음부터 다시 셉니다. 그 결과와 브리프가 맞는지 봅니다.</p>
</div>

<div class="panel">
<div class="panel-head"><strong>verifier_agent.py — verify_brief</strong><span>편향 없는 재계산</span></div>
<div class="panel-body">

<<< ../../ch5-a2a/verifier_agent.py#verify-brief{python}

</div>
</div>

<p class="section-note" style="margin-top:16px">검증자가 다시 세어도 쿠팡 89,000원과 넷플릭스 17,000원이 나옵니다. 브리프가 둘 다 짚었으면 통과입니다. 검증자는 내 코드를 신뢰하지 않고 데이터를 봅니다.</p>

<p class="section-note" style="margin-top:10px"><strong>한 발 더.</strong> 여기서 '영수증 없는 거래'를 골라내는 재계산은 금액 대조라 독립성이 높지만, 브리프가 그걸 <em>짚었는지</em>를 보는 건 상호명 부분문자열 매칭(<code>name.split("(")[0] not in brief_text</code>)입니다. 동의어·오타·금액 누락은 못 잡습니다. 실무 검증자는 여기서 금액·날짜 교차대조나 LLM 판정으로 검증을 보강합니다.</p>

<div class="board" style="margin-top:18px">
<div class="board-header"><span>왜 독립 검증인가</span><span class="status-pill">설계 근거</span></div>
<div class="panel-body"><div class="list">
<p>Ch1에서 봤듯, 평가가 "모름"보다 <strong>자신 있는 추측을 보상</strong>해 모델이 단정하는 습관이 남습니다(Kalai). 브리프를 쓴 모델에게 "맞아?"라고 다시 물으면, 같은 가정·같은 사각을 공유해 자기 누락을 잘 못 봅니다.</p>
<p>그래서 검증자는 <strong>브리프 문장을 입력으로 받지 않고</strong> 원본 레코드에서 처음부터 다시 셉니다. 판정 기준이 "내가 쓴 글"이 아니라 "데이터"라, 글쓴이의 사각이 그대로 드러납니다. 프로세스를 분리(A2A)하는 건 이 독립성을 코드 수준에서 강제하는 장치입니다.</p>

```mermaid
flowchart TB
    B["📄 브리프(작성자)"]
    B -->|"자기검증: 같은 가정·같은 사각"| SELF["🙈 자기 누락을 못 봄"]
    REC["🗂 원본 레코드"] -->|"독립 재계산"| EXT["🔍 외부 검증자(A2A)"]
    B -.브리프와 대조.-> EXT
    EXT -->|"데이터 기준 판정"| OUT["✅ PASS / ⚠️ 누락 드러남"]
    style SELF fill:#fde8e8,stroke:#c0392b
    style OUT fill:#e8f5e9,stroke:#0f766e
```

</div></div>
</div>
</section>

<section class="slide">
<div class="section-head">
<div>
<div class="eyebrow">핸즈온 ① · 코드 정독 · 8분</div>

## 서버가 요청을 받는 자리

</div>
<p class="section-note">A2A 서버의 핵심은 <code>AgentExecutor.execute</code> 하나입니다. 들어온 메시지에서 브리프를 꺼내 검증하고, Task로 결과를 돌려줍니다. 중요한 규칙은 하나입니다. 상태를 갱신하기 전에 Task를 먼저 등록해야 합니다.</p>
</div>

<div class="panel">
<div class="panel-head"><strong>ch5-a2a/verifier_agent.py — execute</strong><span>요청 → 검증 → 결과</span></div>
<div class="panel-body">

<<< ../../ch5-a2a/verifier_agent.py#execute{python}

<p class="section-note" style="margin-top:12px">읽는 순서 — <strong>①</strong> <code>get_user_input()</code>로 들어온 브리프 텍스트 → <strong>②</strong> <code>verify_brief</code>로 독립 재계산 → <strong>③</strong> <code>enqueue_event(Task(...))</code>로 <em>상태 갱신 전에 Task를 먼저 등록</em>(A2A 규칙) → <code>start_work → add_artifact(verdict) → complete</code>로 상태를 단계로 올립니다.</p>

</div>
</div>

<div class="grid-2" style="margin-top:16px">
<div class="panel"><div class="panel-head"><strong>a2a-sdk 1.1.0 서버 골격</strong></div><div class="panel-body"><div class="list">
<p><code>AgentExecutor</code> 구현 → <code>DefaultRequestHandler</code>(+Card·TaskStore) → <code>create_*_routes</code> → Starlette → uvicorn.</p>
<p>이 순서가 a2a-sdk 1.1.0 서버의 표준 골격입니다.</p>
</div></div></div>
<div class="panel"><div class="panel-head"><strong>왜 Task를 먼저 등록하나</strong></div><div class="panel-body"><div class="list">
<p>A2A는 "Task 없이 상태 갱신 먼저"를 금지합니다. 클라이언트가 추적할 대상이 없기 때문입니다.</p>
<p>순서를 어기면 <code>InvalidAgentResponseError</code>가 납니다. 실습에서 직접 확인할 오류입니다.</p>
</div></div></div>
</div>

<div class="cue solve" style="margin-top:18px">
<div class="cue-head"><span class="cue-label">✏️ 깨뜨려 보기 — 코드 수정</span><span class="cue-time">~5분</span></div>
<div class="cue-body">규칙을 직접 어겨 봅니다. <code>verifier_agent.py</code>의 <code>execute</code>에서 <strong>③ <code>enqueue_event(Task(...))</code> 블록을 주석 처리</strong>한 뒤, 핸즈온 ②로 서버를 띄워 검증을 보내세요. 다음 줄 <code>updater.start_work(...)</code>가 <em>등록되지 않은</em> Task를 갱신하려다 <code>InvalidAgentResponseError</code>로 막힙니다. 에러를 확인한 뒤 주석을 풀어 되돌리세요. 이 실습은 "상태 갱신 전 Task 등록" 규칙의 필요성을 보여 줍니다.</div>
</div>
</section>

<section class="slide">
<div class="section-head">
<div>
<div class="eyebrow">핸즈온 ② · 단계별 실행 · 20분</div>

## 띄우고, 보내고, 받는다

</div>
<p class="section-note">한 번에 자동 기동해 통신하거나, 서버를 따로 띄워 두고 보냅니다. 네트워크 없이 구조만 보려면 mock입니다.</p>
</div>

<div class="stack">
<div class="row"><div class="code">0</div><div class="copy"><strong>먼저 — 검증할 브리프를 만들어 둔다(Ch3)</strong><p><code>uv run python3 ch3-deepagents/research_orchestrator.py --mock</code><br><span style="color:var(--muted)">성공 기준: <code>workspace/brief_draft.md</code> 생성(키 없이 보장). Ch4의 키 있는 <code>skill_agent.py --run</code>으로 <code>brief.md</code>를 만들어 뒀다면 Ch5가 그걸 우선 보내고, 없으면 이 <code>brief_draft.md</code>로 fallback합니다. (<code>okf_store.py</code>는 브리프가 아니라 <code>knowledge_base/</code>를 적재하므로 검증 선행으로는 선택입니다.)</span></p></div><div class="store">선행</div></div>
<div class="row"><div class="code">a</div><div class="copy"><strong>한 번에 — 자동 기동 + 검증</strong><p><code>uv run python3 ch5-a2a/a2a_verify.py --serve</code><br><span style="color:var(--muted)">성공 기준: <code>Agent Card: 세무·정합성 검증 에이전트</code> → <code>검증 결과 수신 (A2A)</code> → verified_brief.md.</span></p></div><div class="store">A2A</div></div>
<div class="row"><div class="code">b</div><div class="copy"><strong>따로 — 서버 먼저(다른 터미널)</strong><p><code>uv run python3 ch5-a2a/verifier_agent.py</code> 후 <code>uv run python3 ch5-a2a/a2a_verify.py</code><br><span style="color:var(--muted)">성공 기준: 브라우저로 <code>localhost:9610/.well-known/agent-card.json</code> 카드가 보인다.</span></p></div><div class="store">서버</div></div>
<div class="row"><div class="code">c</div><div class="copy"><strong>오프라인 — 네트워크 없이</strong><p><code>uv run python3 ch5-a2a/a2a_verify.py --mock</code><br><span style="color:var(--muted)">성공 기준: 같은 PASS 결과가 네트워크 없이 나온다.</span></p></div><div class="store">목</div></div>
</div>

<div class="cue do">
<div class="cue-head"><span class="cue-label">✋ 직접 해보기</span><span class="cue-time">~5분</span></div>
<div class="cue-body">검증 에이전트(A2A 서버)를 띄우고 클라이언트가 브리프를 보냅니다. <code>b</code> 방식으로 다른 터미널에서 <code>verifier_agent.py</code>를 먼저 올린 뒤 <code>a2a_verify.py</code>를 실행하세요. 두 프로세스가 HTTP로 연결되는지가 핵심입니다.</div>
</div>

<div class="cue wait">
<div class="cue-head"><span class="cue-label">⏳ 기다렸다 확인</span><span class="cue-time">~2분</span></div>
<div class="cue-body">클라이언트가 서버의 HTTP 응답을 기다립니다. 검증 결과 아티팩트가 돌아오면 <code>검증 결과 수신 (A2A)</code>과 함께 판정이 <code>PASS</code>인지 <code>NEEDS_REVISION</code>인지 확인하세요. 아래 출력의 마지막 두 줄이 그 응답입니다.</div>
</div>

<div class="panel" style="margin-top:18px">
<div class="panel-head"><strong>출력 — A2A로 받은 검증 결과</strong><span>verified_brief.md 끝부분</span></div>
<div class="panel-body">

```text
▶ 브리프 제출 → 외부 검증 에이전트
  Agent Card: 세무·정합성 검증 에이전트 (skill: verify-brief)
  검증 결과 수신 (A2A)

## 외부 검증 결과 — PASS
검증 주체: 세무·정합성 검증 에이전트 (A2A)

- 독립 재계산: 영수증 없는 거래 2건 (쿠팡(주) 89,000원, 넷플릭스 17,000원)
- 브리프가 빠짐 없이 모두 짚었습니다 — 검증 통과
```

</div>
</div>

<div class="cue solve" style="margin-top:18px">
<div class="cue-head"><span class="cue-label">✏️ 풀어보기</span><span class="cue-time">~5분</span></div>
<div class="cue-body">만약 브리프에서 "쿠팡" 줄을 일부러 지우고 검증을 보내면 결과가 어떻게 바뀔까요? 실제로 지운 뒤 다시 보내고 결과를 확인해 보세요.</div>
</div>

<details>
<summary>정답 확인</summary>
<div class="reveal">
<p><code>NEEDS_REVISION</code>이 돌아옵니다. 검증자는 브리프 문장을 믿지 않고 레코드에서 직접 다시 세기 때문에, 쿠팡 89,000원이 빠진 걸 잡아냅니다("브리프가 누락한 항목: 쿠팡").</p>
<p>외부 검증의 목적은 작성한 문장이 아니라 원천 데이터를 기준으로 다시 판정하는 것입니다. 그래서 브리프의 누락이 드러납니다. 같은 프로세스 안에서 자기 검증을 하면 이 분리가 약해집니다.</p>
</div>
</details>
</section>

<section class="slide">
<div class="section-head">
<div>
<div class="eyebrow">핸즈온 ③ · 트러블슈팅 · 참고</div>

## 막히면 여기부터

</div>
<p class="section-note">A2A는 대부분 포트·기동 타이밍·응답 순서 문제입니다.</p>
</div>

<div class="grid-2">
<div class="panel"><div class="panel-head"><strong>Connection refused</strong><span>기동</span></div><div class="panel-body"><div class="list">
<p>검증 에이전트가 아직 안 떴습니다. <code>--serve</code>는 기동을 기다렸다 보내지만, 따로 띄울 땐 서버가 먼저 올라온 뒤 클라이언트를 실행하세요.</p>
</div></div></div>
<div class="panel"><div class="panel-head"><strong>포트 9610 사용 중</strong><span>포트</span></div><div class="panel-body"><div class="list">
<p>이전 서버가 안 죽었습니다. 실행 중인 <code>verifier_agent.py</code> 프로세스를 Ctrl-C로 종료한 뒤 다시 띄웁니다.</p>
</div></div></div>
<div class="panel"><div class="panel-head"><strong>InvalidAgentResponseError</strong><span>응답 순서</span></div><div class="panel-body"><div class="list">
<p>상태 갱신 전에 Task를 먼저 enqueue해야 합니다(executor 순서). 고치면 클라이언트에 <code>검증 결과 수신 (A2A)</code>이 정상 출력됩니다.</p>
</div></div></div>
<div class="panel"><div class="panel-head"><strong>카드 조회 실패</strong><span>well-known</span></div><div class="panel-body"><div class="list">
<p><code>/.well-known/agent-card.json</code>이 200인지 브라우저로 먼저 확인합니다. 안 뜨면 서버가 안 올라온 겁니다.</p>
</div></div></div>
</div>
</section>

<section class="slide">
<div class="section-head">
<div>
<div class="eyebrow">마무리 · 3분</div>

## 다음 — 하나의 파이프라인으로 묶는다

</div>
<p class="section-note">이제 필요한 모듈이 모였습니다. 추출, 적재, 조사, 지식, 브리프, 외부 검증을 각각 따로 돌려 봤습니다.<br>
Ch6에서는 이 모듈들을 하나로 묶습니다. 샘플 메일 입력이 들어오면 분류부터 검증까지 이어지는 엔드투엔드를 배선합니다. 새로 짜지 않고 기존 모듈을 연결합니다.</p>
</div>

<div class="grid-3">
<div class="panel"><div class="panel-head"><strong>이번 챕터 결과</strong></div><div class="panel-body"><div class="list">
<p>A2A 외부 검증 클라이언트·제공 모듈</p>
<p>verified_brief.md</p>
</div></div></div>
<div class="panel"><div class="panel-head"><strong>Ch6에서 할 것</strong></div><div class="panel-body"><div class="list">
<p>샘플 메일(목)→분류→조사→지식→브리프→검증</p>
<p>모듈 배선 · 엔드투엔드 1회</p>
</div></div></div>
<div class="panel"><div class="panel-head"><strong>최종 목적지</strong></div><div class="panel-body"><div class="list">
<p>인박스 입력 → 검증된 브리프</p>
<p>Ch6 통합 캡스톤</p>
</div></div></div>
</div>

<div class="board" style="margin-top:18px">
<div class="board-header"><span>참고 자료</span><span class="status-pill">출처</span></div>
<div class="panel-body"><div class="list">
<p><a href="https://a2a-protocol.org/">A2A Protocol</a> · <a href="https://github.com/a2aproject/a2a-python">a2a-python SDK</a></p>
<p><a href="https://a2a-protocol.org/latest/specification/">A2A 명세 — Agent Card · message/send · Task</a></p>
</div></div>
</div>
</section>


<nav class="chapnav">
<div class="board" style="margin-top:8px">
<div style="display:grid;grid-template-columns:1fr auto 1fr;gap:14px;align-items:center">
<a href="/deepagents-handson/chapters/chapter-4" style="color:inherit;text-decoration:none;font-weight:900;font-size:14px">← Ch4 · Skills · MCP · 지식</a>
<a href="/deepagents-handson/toc" style="color:var(--forest);text-decoration:none;font-weight:900;font-size:13px;background:rgba(148,210,189,.3);border:1px solid rgba(15,118,110,.24);border-radius:99px;padding:7px 16px">목차</a>
<a href="/deepagents-handson/chapters/chapter-6" style="color:inherit;text-decoration:none;font-weight:900;font-size:14px;text-align:right">Ch6 · 통합 캡스톤 →</a>
</div>
</div>
</nav>

</div>
</div>
