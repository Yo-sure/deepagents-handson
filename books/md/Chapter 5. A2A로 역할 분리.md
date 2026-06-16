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

<p class="lead">브리프를 내가 쓰고 내가 검증하면 한쪽으로 치우칩니다. 다른 프로세스, 다른 팀의 에이전트에 맡겨야 합니다.<br>
이 챕터에서 브리프를 외부 검증 에이전트에 A2A로 보냅니다. 그 에이전트는 서명 가능한 Agent Card로 자신을 밝히고, 레코드를 독립으로 다시 계산해 답합니다.</p>

<div class="kicker">
<div class="metric"><span class="num">70</span><strong>분</strong><span>이론 28 · 핸즈온 42</span></div>
<div class="metric"><span class="num">5</span><strong>번째 부품</strong><span>a2a_verify.py</span></div>
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
<div class="eyebrow">1 · 경계</div>

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

<p class="section-note" style="margin-top:16px">검증을 같은 프로세스 안에서 하면 결국 내 코드가 내 코드를 봅니다. 독립성이 없습니다. 검증자를 프로세스 밖으로 빼야 진짜 외부 시각이 됩니다. 그래서 A2A를 씁니다.</p>
</section>

<section class="slide">
<div class="section-head">
<div>
<div class="eyebrow">2 · 신원</div>

## Agent Card — 서명 가능한 자기소개

</div>
<p class="section-note">A2A 에이전트는 자신을 well-known 경로에 카드로 밝힙니다. 이름, 버전, 무슨 기술(skill)을 제공하는지, 어디로 보내야 하는지가 담깁니다.<br>
상대를 부르기 전에 이 카드를 먼저 읽습니다. 누구인지 확인하고 통신을 시작합니다. v1.0 GA부터 카드에 서명을 붙여 출처를 검증할 수 있습니다.</p>
</div>

<div class="panel">
<div class="panel-head"><strong>GET /.well-known/agent-card.json</strong><span>검증 에이전트의 자기소개</span></div>
<div class="panel-body">

```json
{
  "name": "세무·정합성 검증 에이전트",
  "version": "1.0.0",
  "capabilities": { "streaming": false },
  "supportedInterfaces": [{ "url": "http://localhost:9610", "protocolBinding": "JSONRPC" }],
  "skills": [{ "id": "verify-brief", "name": "브리프 검증",
              "description": "브리프의 짚을 점이 실제 레코드와 맞는지 독립 재계산으로 확인" }]
}
```

</div>
</div>

<p class="section-note" style="margin-top:16px">카드는 a2a-sdk의 <code>AgentCard</code> 타입으로 만들어 스키마에 맞춥니다. 직접 JSON을 손으로 쓰지 않습니다.</p>
</section>

<section class="slide">
<div class="section-head">
<div>
<div class="eyebrow">3 · 통신</div>

## SendMessage와 Task 라이프사이클

</div>
<p class="section-note">카드를 읽었으면 메시지를 보냅니다. 클라이언트가 <code>send_message</code>로 브리프를 싣고, 서버는 그 일을 하나의 Task로 받아 상태를 단계별로 올립니다.<br>
제출됨에서 작업 중으로, 결과를 아티팩트로 붙이고 완료로 닫습니다. 클라이언트는 그 마지막 결과를 읽습니다.</p>
</div>

<div class="flow">
<div class="flow-step"><small>submitted</small><strong>접수</strong><p>서버가 Task를 먼저 등록한다</p></div>
<div class="flow-step"><small>working</small><strong>작업 중</strong><p>레코드를 불러 대사하는 중</p></div>
<div class="flow-step"><small>artifact</small><strong>결과 첨부</strong><p>검증 결과를 아티팩트로 붙인다</p></div>
<div class="flow-step"><small>completed</small><strong>완료</strong><p>클라이언트가 결과를 읽는다</p></div>
</div>

```python
# 클라이언트 — Agent Card 조회 후 SendMessage
card = await A2ACardResolver(httpx_client=http, base_url=URL).get_agent_card()
client = ClientFactory(config=ClientConfig(httpx_client=http, streaming=False)).create(card=card)
req = SendMessageRequest(message=Message(role=Role.ROLE_USER, parts=[Part(text=brief)]))
async for resp in client.send_message(request=req):
    ...  # Task 완료 시 아티팩트에서 검증 결과를 읽는다
```
</section>

<section class="slide">
<div class="section-head">
<div>
<div class="eyebrow">4 · 제공 모듈</div>

## 검증자는 독립으로 다시 센다

</div>
<p class="section-note">검증 에이전트는 과정에서 제공 모듈로 주어집니다. 재현성을 위해 모델 없이 규칙으로 동작합니다.<br>
핵심은 독립 재계산입니다. 브리프의 문장을 믿지 않고, 분류 레코드에서 영수증 없는 거래를 처음부터 다시 셉니다. 그 결과와 브리프가 맞는지 봅니다.</p>
</div>

<div class="panel">
<div class="panel-head"><strong>verifier_agent.py — verify_brief</strong><span>편향 없는 재계산</span></div>
<div class="panel-body">

```python
def verify_brief(brief_text: str) -> tuple[bool, list[str]]:
    records = load_records()                       # 레코드를 직접 읽는다
    receipts = by_type(records, "영수증")
    card = next(r for r in by_type(records, "명세서") if "카드" in r.merchant)
    real_gaps = [(i.name, i.amount or 0) for i in card.items
                 if not any(abs(r.total - (i.amount or 0)) < 1 for r in receipts)]
    missing = [n for n, _ in real_gaps if n.split("(")[0] not in brief_text]
    return (not missing), [...]                    # 브리프가 빠뜨린 게 있나
```

</div>
</div>

<p class="section-note" style="margin-top:16px">검증자가 다시 세어도 쿠팡 89,000원과 넷플릭스 17,000원이 나옵니다. 브리프가 둘 다 짚었으면 통과입니다. 검증자는 내 코드를 신뢰하지 않고 데이터를 봅니다.</p>
</section>

<section class="slide">
<div class="section-head">
<div>
<div class="eyebrow">핸즈온 · 42분</div>

## 직접 검증받는다 — a2a_verify.py

</div>
<p class="section-note">검증 에이전트를 띄우고 브리프를 보냅니다. <code>--serve</code>는 검증 에이전트를 자동으로 기동한 뒤 통신합니다. <code>--mock</code>은 네트워크 없이 같은 결과를 냅니다.<br>
끝나면 브리프 끝에 외부 검증 도장이 찍힌 verified_brief.md가 생깁니다.</p>
</div>

<div class="board">
<div class="board-header"><span>실행</span><span class="status-pill">터미널</span></div>
<div class="stack">
<div class="row"><div class="code">a</div><div class="copy"><strong>한 번에 — 에이전트 자동 기동 + 검증</strong><p><code>uv run python3 ch5-a2a/a2a_verify.py --serve</code></p></div><div class="store">A2A</div></div>
<div class="row"><div class="code">b</div><div class="copy"><strong>따로 — 검증 에이전트 먼저 띄우고</strong><p><code>uv run python3 ch5-a2a/verifier_agent.py</code> (다른 터미널)</p></div><div class="store">서버</div></div>
<div class="row"><div class="code">c</div><div class="copy"><strong>오프라인 — 네트워크 없이</strong><p><code>uv run python3 ch5-a2a/a2a_verify.py --mock</code></p></div><div class="store">목</div></div>
</div>
</div>

<div class="panel" style="margin-top:18px">
<div class="panel-head"><strong>출력 — A2A로 받은 검증 결과</strong><span>verified_brief.md 끝부분</span></div>
<div class="panel-body">

```text
▶ 브리프 제출 → 외부 검증 에이전트
  Agent Card: 세무·정합성 검증 에이전트 (skill: verify-brief)
  검증 결과 수신 (A2A)

## 외부 검증 결과 — PASS
- 독립 재계산: 영수증 없는 거래 2건 (쿠팡(주) 89,000원, 넷플릭스 17,000원)
- 브리프가 빠짐 없이 모두 짚었습니다 — 검증 통과
```

</div>
</div>
</section>

<section class="slide">
<div class="section-head">
<div>
<div class="eyebrow">마무리</div>

## 다음 — 전부 한 줄기로 잇는다

</div>
<p class="section-note">이제 부품이 다 모였습니다. 추출, 적재, 조사, 지식, 브리프, 외부 검증. 각각 따로 돌려 봤습니다.<br>
Ch6에서는 이걸 하나로 잇습니다. 메일 봉투가 도착하면 분류부터 검증까지 한 번에 흐르는 엔드투엔드를 배선합니다. 새로 짜지 않고 부품을 끼웁니다.</p>
</div>

<div class="grid-3">
<div class="panel"><div class="panel-head"><strong>지금 손에 든 것</strong></div><div class="panel-body"><div class="list">
<p>A2A 외부 검증 클라이언트·제공 모듈</p>
<p>verified_brief.md</p>
</div></div></div>
<div class="panel"><div class="panel-head"><strong>Ch6에서 할 것</strong></div><div class="panel-body"><div class="list">
<p>봉투(목)→분류→조사→지식→브리프→검증</p>
<p>부품 배선 · 엔드투엔드 1회</p>
</div></div></div>
<div class="panel"><div class="panel-head"><strong>최종 목적지</strong></div><div class="panel-body"><div class="list">
<p>인박스 한 통 → 검증된 브리프</p>
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
<a href="/chapters/chapter-4" style="color:inherit;text-decoration:none;font-weight:900;font-size:14px">← Ch4 · Skills · MCP · 지식</a>
<a href="/toc" style="color:var(--forest);text-decoration:none;font-weight:900;font-size:13px;background:rgba(148,210,189,.3);border:1px solid rgba(15,118,110,.24);border-radius:99px;padding:7px 16px">목차</a>
<a href="/chapters/chapter-6" style="color:inherit;text-decoration:none;font-weight:900;font-size:14px;text-align:right">Ch6 · 통합 캡스톤 →</a>
</div>
</div>
</nav>

</div>
</div>
