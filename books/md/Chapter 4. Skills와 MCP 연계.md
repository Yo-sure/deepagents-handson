---
layout: page
title: Ch4 · Skills · MCP · 지식
sidebar: false
aside: false
pageClass: lec-page
---

<div class="lec">
<div class="deck">

<section class="slide hero">
<div>
<div class="eyebrow">Chapter 4 · Skills · MCP · 지식 레이어</div>

# 능력을 붙이고,<br>지식을 남긴다

<p class="lead">조사 결과가 노트로 흩어져 있습니다. 이걸 다음 달에도 쓰려면 절차는 Skill로, 연결은 MCP로, 지식은 표준 형식으로 묶어야 합니다.<br>
이 챕터에서 브리프 쓰는 절차를 SKILL.md로 정의하고, 파일과 메일을 MCP 한 겹으로 표준화하고, 조사 결과를 OKF 지식으로 적재합니다.</p>

<div class="kicker">
<div class="metric"><span class="num">80</span><strong>분</strong><span>이론 30 · 핸즈온 50</span></div>
<div class="metric"><span class="num">3</span><strong>겹의 능력</strong><span>Skill · MCP · OKF</span></div>
<div class="metric"><span class="num">12</span><strong>지식 항목</strong><span>knowledge_base/*.md</span></div>
</div>
</div>

<div class="board">
<div class="board-header"><span>이 챕터가 끝나면</span><span class="status-pill">산출물</span></div>
<div class="stack">
<div class="row"><div class="code">1</div><div class="copy"><strong>brief_skill/</strong><p>SKILL.md(점진 공개) + 얇은 plugin 템플릿</p></div><div class="store">절차</div></div>
<div class="row"><div class="code">2</div><div class="copy"><strong>MCP 인박스 서버</strong><p>파일[실선] · 메일[목]을 도구로 노출</p></div><div class="store">연결</div></div>
<div class="row"><div class="code">3</div><div class="copy"><strong>OKF 지식베이스</strong><p>거래처·구독·확인필요를 표준 항목으로</p></div><div class="store">지식</div></div>
</div>
</div>
</section>

<section class="slide">
<div class="section-head">
<div>
<div class="eyebrow">1 · 절차</div>

## SKILL.md — 점진 공개

</div>
<p class="section-note">Skill은 에이전트에게 절차적 지식을 주는 마크다운 파일입니다. 앞머리에 이름과 설명을 달고, 본문에 방법을 적습니다.<br>
핵심은 <strong>3단계 점진 공개</strong>입니다. ① 시작 시 모든 Skill의 <code>name·description</code>만 시스템 프롬프트에 올라갑니다(항상 켜지지만 쌉니다). ② description이 작업과 맞으면 그때 <strong>SKILL.md 본문</strong>을 읽습니다. ③ <code>reference/*.md</code>·스크립트는 본문이 가리킬 때만 펼칩니다. 그래서 <em>description 한 줄이 호출 여부를 정하는 가장 중요한 필드</em>입니다.</p>
</div>

<div class="grid-3">
<div class="panel"><div class="panel-head"><strong>1단계 — 메타</strong><span>name · description</span></div><div class="panel-body"><div class="list">
<p>언제 이 Skill을 쓰는지 한 줄로</p>
<p>에이전트는 이것만 보고 호출을 판단합니다</p>
</div></div></div>
<div class="panel"><div class="panel-head"><strong>2단계 — 본문</strong><span>SKILL.md 절차</span></div><div class="panel-body"><div class="list">
<p>입력·절차·출력 형식·톤</p>
<p>호출이 정해지면 이때 읽습니다</p>
</div></div></div>
<div class="panel"><div class="panel-head"><strong>3단계 — 참조</strong><span>reference/*.md</span></div><div class="panel-body"><div class="list">
<p>세부 형식·예시는 따로 둡니다</p>
<p>실제로 쓸 때만 펼쳐 봅니다</p>
</div></div></div>
</div>

```markdown
---
name: inbox-brief
description: 분류 레코드·OKF 지식·조사 노트를 모아 월간 브리프를 작성한다.
  "이번 달 인박스 정리", "지출 브리프"를 요청할 때 쓴다.
version: 0.1.0
---
# 인박스 브리프 작성
## 입력 ... ## 절차 ... ## 출력 형식 → reference/brief_format.md (필요할 때만)
```
</section>

<section class="slide">
<div class="section-head">
<div>
<div class="eyebrow">2 · 패키징</div>

## plugin은 얇게

</div>
<p class="section-note">Skill 하나를 배포 단위로 묶으면 plugin입니다. 이 과정에서는 얇게 갑니다. 매니페스트 한 장으로 이름·버전·어떤 Skill을 담는지만 선언합니다.<br>
무게는 SKILL.md와 MCP, OKF에 둡니다. 패키징은 그것들을 담는 봉투입니다.</p>
</div>

<div class="panel">
<div class="panel-head"><strong>brief_skill/plugin.json</strong><span>얇은 매니페스트</span></div>
<div class="panel-body">

```json
{
  "name": "inbox-brief",
  "version": "0.1.0",
  "description": "인박스 리서치 애널리스트의 월간 브리프 작성 스킬",
  "skills": ["./SKILL.md"],
  "tags": ["inbox", "brief", "okf"]
}
```

</div>
</div>

<div class="board" style="margin-top:18px">
<div class="board-header"><span>brief_skill/ 구성</span><span class="status-pill">디렉터리</span></div>
<div class="panel-body"><div class="list">
<p><code>SKILL.md</code> — 절차(1·2단계) · <code>reference/brief_format.md</code> — 세부 형식(3단계)</p>
<p><code>plugin.json</code> — 배포 매니페스트. 세 파일이 한 봉투에 들어가 재사용됩니다.</p>
</div></div>
</div>
</section>

<section class="slide">
<div class="section-head">
<div>
<div class="eyebrow">3 · 연결</div>

## MCP — 파일은 실선, 메일은 목

</div>
<p class="section-note">MCP는 에이전트가 외부에 닿는 통로를 표준화합니다. 이 과정의 외부 연결은 둘로 고정합니다. 파일은 진짜로 잇고, 메일은 목으로 둡니다.<br>
도구 이름과 docstring이 곧 모델이 보는 설명입니다. 모델은 그걸 읽고 어떤 도구를 부를지 정합니다.</p>
</div>

<div class="grid-2">
<div class="panel"><div class="panel-head"><strong>파일 [실선]</strong><span>진짜 연결</span></div><div class="panel-body"><div class="list">
<p><code>list_classified</code> · <code>read_record</code> — classified/ 실제 읽기</p>
<p><code>search_knowledge</code> — OKF 항목을 type으로 조회</p>
</div></div></div>
<div class="panel"><div class="panel-head"><strong>메일 [목]</strong><span>재현 가능</span></div><div class="panel-body"><div class="list">
<p><code>fetch_inbox</code> — 이번 달 봉투 목록(목 데이터)</p>
<p>외부 메일 서버 없이 누구나 같은 결과</p>
</div></div></div>
</div>

<div class="board" style="margin-top:18px">
<div class="board-header"><span>MCP 세 가지 기본 요소</span><span class="status-pill">primitives</span></div>
<div class="panel-body"><div class="list">
<p><strong>Tool</strong> — 모델이 자율로 호출(부수효과 가능) · <strong>Resource</strong> — 클라이언트가 읽어가는 읽기전용 데이터 · <strong>Prompt</strong> — 사용자가 트리거하는 템플릿</p>
<p>전송은 stdio(로컬, 에이전트가 subprocess로 붙음) 또는 HTTP 스트리밍(원격). 이 실습은 stdio입니다.</p>
</div></div>
</div>

<div class="ask" style="margin-top:18px"><strong>판단해 보기.</strong> 우리 서버에서 <code>fetch_inbox</code>는 <code>@mcp.tool()</code>인데 <code>inbox_stats</code>는 <code>@mcp.resource("inbox://stats")</code>입니다. 왜 통계는 Tool이 아니라 Resource로 노출했을까요?</div>

<details>
<summary>정답 확인</summary>
<div class="reveal">
<p>Tool은 <em>모델이 자율로</em> 호출합니다 — 부수효과가 있을 수 있는 "행동". Resource는 <em>클라이언트(호스트)가</em> 읽어가는 읽기전용 컨텍스트입니다. 인박스 통계는 부작용 없는 순수 읽기라 Resource가 맞고, 봉투를 "가져오는" <code>fetch_inbox</code>는 호출 시점을 모델이 정하므로 Tool입니다.</p>
<p>판단 기준 한 줄: <strong>"누가 언제 쓸지를 모델이 정하나(Tool), 호스트가 정하나(Resource), 사람이 정하나(Prompt)?"</strong> MCP는 이 세 통제 평면으로 나뉩니다.</p>
</div>
</details>
</section>

<section class="slide">
<div class="section-head">
<div>
<div class="eyebrow">4 · 지식</div>

## OKF — 사람도 읽고 에이전트도 읽는다

</div>
<p class="section-note">노트는 이번 달용 메모입니다. 다음 달에도 쓰려면 표준 형식으로 쌓아야 합니다. OKF(Open Knowledge Format)는 Google Cloud가 2026-06 공개한 벤더 중립 표준으로, 압축도 런타임도 없이 <strong>YAML 프런트매터를 단 마크다운 파일</strong>이 곧 지식 항목입니다. 강제하는 건 <code>type</code> 하나뿐입니다(나머지 <code>title·description·tags</code>는 선택).<br>
조사에서 세 종류의 지식을 뽑습니다 — 거래처, 구독, 확인 필요. 영수증 없는 89,000원이 gap 항목으로 남습니다.</p>
</div>

<div class="panel">
<div class="panel-head"><strong>knowledge_base/gap-쿠팡-주.md</strong><span>OKF 항목 — type 필수</span></div>
<div class="panel-body">

```markdown
---
type: gap
name: 쿠팡(주)
schema_version: okf/0.1
amount: 89000
---
# 쿠팡(주)
- 카드 명세서 89,000원 — 대응 영수증 없음
- 확인 필요: 영수증 분실 또는 미수령
```

</div>
</div>

<p class="section-note" style="margin-top:16px">Ch3 조사가 찾은 틈이 여기서 영속적인 지식 항목이 됩니다. 다음 달 인박스를 볼 때 이 지식베이스를 먼저 참조하면 같은 구독·같은 거래처를 다시 분석하지 않아도 됩니다.</p>

<div class="board" style="margin-top:18px">
<div class="board-header"><span>넷을 언제 쓰나 — 결정 경계</span><span class="status-pill">정리</span></div>
<div class="panel-body"><div class="list">
<p><strong>MCP 도구/리소스</strong> — 에이전트를 <em>외부 시스템</em>(파일·메일·DB)에 잇는 표준 통로. 한 번 꽂으면 어느 호스트에서나 같은 인터페이스. <em>연결</em>의 문제.</p>
<p><strong>Skill</strong> — 에이전트에게 <em>절차적 지식</em>("브리프는 이렇게 쓴다")을 주는 SKILL.md+스크립트. 모델이 description을 보고 스스로 펼친다. <em>방법</em>의 문제.</p>
<p><strong>OKF</strong> — 다음 달에도 재사용할 <em>사실 지식</em>(거래처·구독·확인필요)을 표준 마크다운으로 적재. <em>기억</em>의 문제.</p>
<p>한 문장: <strong>MCP=어디에 닿나 · Skill=어떻게 하나 · OKF=무엇을 기억하나.</strong></p>
</div></div>
</div>
</section>

<section class="slide">
<div class="section-head">
<div>
<div class="eyebrow">핸즈온 ① · 코드 정독</div>

## OKF 항목 하나가 만들어지는 법

</div>
<p class="section-note">OKF 항목은 YAML 머리말 + 마크다운 본문입니다. 코드는 레코드에서 값을 뽑아 이 틀에 끼웁니다. 표준이 강제하는 건 <code>type</code>뿐이고, 우리는 거기에 도메인 필드(<code>name·amount</code>)와 버전 표기(<code>schema_version</code>)를 <strong>덧붙였습니다</strong> — 표준은 이런 확장을 허용합니다. 표준 필드와 우리 확장을 구분해서 보세요.</p>
</div>

<div class="panel">
<div class="panel-head"><strong>ch4-skills-mcp/okf_store.py — okf_entry</strong><span>지식 항목 직렬화</span></div>
<div class="panel-body">

```python
def okf_entry(type_: str, name: str, body_lines: list[str], **meta) -> str:
    fm = [f"type: {type_}", f"name: {name}", f"schema_version: {OKF_VERSION}"]  # type 필수
    fm += [f"{k}: {v}" for k, v in meta.items()]
    front = "\n".join(fm)
    body = "\n".join(body_lines)
    return f"---\n{front}\n---\n\n# {name}\n\n{body}\n"   # 프런트매터 + 본문

# 카드 대사에서 영수증 없는 줄을 gap/subscription 항목으로:
if amt < 30000:
    out[f"subscription-{slug(item.name)}"] = okf_entry("subscription", item.name, [...])
else:
    out[f"gap-{slug(item.name)}"] = okf_entry("gap", item.name, [...])   # 쿠팡 89,000 → gap
```

</div>
</div>

<div class="panel" style="margin-top:16px">
<div class="panel-head"><strong>ch4-skills-mcp/mcp_inbox_server.py — 도구·리소스 등록</strong><span>FastMCP 데코레이터</span></div>
<div class="panel-body">

```python
mcp = FastMCP("inbox-mcp-server")

@mcp.tool()                              # 함수명=도구명, docstring=설명, name:str=입력 스키마
def read_record(name: str) -> str:
    """분류 레코드 하나를 읽어 JSON 문자열로 돌려준다. [실선 — 실제 파일]"""
    ...

@mcp.resource("inbox://stats")           # Tool이 아니라 Resource — 읽기전용 컨텍스트
def inbox_stats() -> str:
    """인박스 통계(읽기 전용 리소스)."""
    ...

if __name__ == "__main__":
    mcp.run()                            # 인자 없으면 stdio 전송 — 에이전트가 subprocess로 붙는다
```

</div>
</div>

<div class="grid-2" style="margin-top:16px">
<div class="panel"><div class="panel-head"><strong>MCP 도구는 어떻게 노출되나</strong></div><div class="panel-body"><div class="list">
<p><code>@mcp.tool()</code>를 붙이면 함수가 도구가 됩니다. 함수 이름이 도구 이름, docstring이 설명, 타입힌트가 입력 스키마입니다.</p>
<p>모델은 그 docstring을 읽고 어떤 도구를 부를지 정합니다 — 그래서 설명을 또렷이 씁니다.</p>
</div></div></div>
<div class="panel"><div class="panel-head"><strong>점진 공개는 어디서 작동하나</strong></div><div class="panel-body"><div class="list">
<p>① <code>name·description</code>만 늘 시스템 프롬프트에. ② 맞으면 SKILL.md 본문. ③ <code>reference/brief_format.md</code>는 본문이 가리킬 때만.</p>
<p>토큰을 단계로 나눠 쓰는 셈입니다 — Skill이 100개여도 평소엔 description 100줄만 올라갑니다.</p>
</div></div></div>
</div>
</section>

<section class="slide">
<div class="section-head">
<div>
<div class="eyebrow">핸즈온 ② · 단계별 실행</div>

## 지식·연결·절차를 묶는다

</div>
<p class="section-note">세 산출물을 각각 돌려 보고 결과를 확인합니다. 이게 Ch6 캡스톤에서 그대로 배선됩니다.</p>
</div>

<div class="stack">
<div class="row"><div class="code">1</div><div class="copy"><strong>OKF 지식 적재</strong><p><code>uv run python3 ch4-skills-mcp/okf_store.py</code><br><span style="color:var(--muted)">성공 기준: <code>OKF 항목 12개 적재</code> + <code>knowledge_base/gap-쿠팡-주.md</code> 생성.</span></p></div><div class="store">지식</div></div>
<div class="row"><div class="code">2</div><div class="copy"><strong>MCP 서버 도구 점검</strong><p><code>uv run python3 ch4-skills-mcp/mcp_inbox_server.py --list</code><br><span style="color:var(--muted)">성공 기준: 도구 4개([실선] 3 + [목] 1)가 이름·설명과 함께 나온다.</span></p></div><div class="store">연결</div></div>
<div class="row"><div class="code">3</div><div class="copy"><strong>Skill·지식 열어 보기</strong><p><code>cat workspace/knowledge_base/gap-쿠팡-주.md</code> · <code>cat ch4-skills-mcp/brief_skill/SKILL.md</code><br><span style="color:var(--muted)">성공 기준: gap 항목에 <code>type: gap</code> 머리말, SKILL.md에 name·description.</span></p></div><div class="store">절차</div></div>
</div>

<div class="panel" style="margin-top:18px">
<div class="panel-head"><strong>출력 — 적재된 지식 항목</strong><span>okf_store.py</span></div>
<div class="panel-body">

```text
▶ OKF 항목 12개 적재 → workspace/knowledge_base
  [gap         ] gap-쿠팡-주.md
  [subscription] subscription-넷플릭스.md
  [merchant    ] merchant-스타벅스-강남r점.md
  ...
```

</div>
</div>

<div class="ask" style="margin-top:18px"><strong>직접 해보기.</strong> <code>okf_store.py</code>에서 구독 판정 기준 <code>amt &lt; 30000</code>을 <code>50000</code>으로 올리면 어떤 항목이 gap에서 subscription으로 바뀔까요?</div>

<details>
<summary>관찰 포인트</summary>
<div class="reveal">
<p>쿠팡 89,000원은 여전히 gap입니다(5만 초과). 다만 만약 3만~5만 사이 결제가 있었다면 그게 subscription으로 재분류됩니다. 기준 하나가 "이건 구독이다 vs 확인이 필요하다"의 판단을 가릅니다.</p>
<p>실무에서는 이런 임계값을 도메인 전문가가 정합니다. <code>30000</code>이 "구독이냐 확인이냐"를 가르는 정책 그 자체 — 코드 한 줄에 회계 판단이 박혀 있다는 뜻입니다.</p>
</div>
</details>
</section>

<section class="slide">
<div class="section-head">
<div>
<div class="eyebrow">핸즈온 ③ · 트러블슈팅</div>

## 막히면 여기부터

</div>
<p class="section-note">MCP·OKF는 대부분 입력 디렉터리나 의존성 문제입니다.</p>
</div>

<div class="grid-2">
<div class="panel"><div class="panel-head"><strong>지식이 비어 있음</strong><span>입력</span></div><div class="panel-body"><div class="list">
<p>okf_store는 classified 레코드가 필요합니다. Ch2·Ch3을 먼저 돌렸는지 확인하세요(없으면 gold 보충).</p>
</div></div></div>
<div class="panel"><div class="panel-head"><strong>MCP 도구가 안 뜸</strong><span>점검</span></div><div class="panel-body"><div class="list">
<p><code>--list</code> 없이 실행하면 stdio 서버로 대기합니다(정상). 도구 목록만 보려면 <code>--list</code>를 붙입니다.</p>
</div></div></div>
<div class="panel"><div class="panel-head"><strong>search_knowledge 빈 결과</strong><span>type</span></div><div class="panel-body"><div class="list">
<p>type 철자가 항목의 <code>type:</code>와 정확히 같아야 합니다(gap·subscription·merchant).</p>
</div></div></div>
<div class="panel"><div class="panel-head"><strong>mcp import 에러</strong><span>의존성</span></div><div class="panel-body"><div class="list">
<p><code>mcp[cli]</code>가 설치돼 있어야 합니다. <code>uv sync</code>로 의존성을 맞춥니다.</p>
</div></div></div>
</div>
</section>

<section class="slide">
<div class="section-head">
<div>
<div class="eyebrow">마무리</div>

## 다음 — 밖에 검증을 맡긴다

</div>
<p class="section-note">이제 절차·연결·지식이 갖춰졌습니다. 브리프를 쓸 수 있습니다. 다만 내가 쓴 브리프를 내가 검증하면 한쪽으로 치우칩니다.<br>
Ch5에서는 브리프를 외부 검증 에이전트에 A2A로 보냅니다. 다른 프로세스, 다른 팀의 에이전트가 서명된 카드로 응답합니다.</p>
</div>

<div class="grid-3">
<div class="panel"><div class="panel-head"><strong>지금 손에 든 것</strong></div><div class="panel-body"><div class="list">
<p>brief_skill · MCP 서버 · OKF 지식</p>
<p>knowledge_base 12항목</p>
</div></div></div>
<div class="panel"><div class="panel-head"><strong>Ch5에서 할 것</strong></div><div class="panel-body"><div class="list">
<p>A2A 서명 Agent Card · SendMessage</p>
<p>외부 검증 → verified_brief.md</p>
</div></div></div>
<div class="panel"><div class="panel-head"><strong>최종 목적지</strong></div><div class="panel-body"><div class="list">
<p>인박스 한 통 → 검증된 브리프</p>
<p>Ch6 통합 캡스톤</p>
</div></div></div>
</div>

<div class="board" style="margin-top:18px">
<div class="board-header"><span>참고 자료</span><span class="status-pill">출처</span></div>
<div class="panel-body"><div class="list">
<p><a href="https://modelcontextprotocol.io/">Model Context Protocol</a> · <a href="https://agentskills.io/">Agent Skills(오픈 표준)</a></p>
<p><a href="https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf">Open Knowledge Format v0.1 — Google Cloud</a> · <a href="https://anthropic.skilljar.com/">Anthropic Academy — Agent Skills</a></p>
</div></div>
</div>
</section>


<nav class="chapnav">
<div class="board" style="margin-top:8px">
<div style="display:grid;grid-template-columns:1fr auto 1fr;gap:14px;align-items:center">
<a href="/chapters/chapter-3" style="color:inherit;text-decoration:none;font-weight:900;font-size:14px">← Ch3 · DeepAgents 하네스</a>
<a href="/toc" style="color:var(--forest);text-decoration:none;font-weight:900;font-size:13px;background:rgba(148,210,189,.3);border:1px solid rgba(15,118,110,.24);border-radius:99px;padding:7px 16px">목차</a>
<a href="/chapters/chapter-5" style="color:inherit;text-decoration:none;font-weight:900;font-size:14px;text-align:right">Ch5 · A2A 역할 분리 →</a>
</div>
</div>
</nav>

</div>
</div>
