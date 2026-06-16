---
layout: page
title: Ch1 · 에이전트 패러다임
sidebar: false
aside: false
pageClass: lec-page
---

<div class="lec">
<div class="deck">

<section class="slide hero">
<div>
<div class="eyebrow">Chapter 1 · 에이전트 패러다임</div>

# 영수증을 읽고,<br>판단하게 만든다

<p class="lead">애널리스트의 첫 일은 문서를 읽어 숫자로 바꾸는 것입니다. 이 챕터에서는 영수증 이미지 한 장을 모델에 보여 주고 RecordV1 구조로 뽑아냅니다.<br>
그 과정에서 LLM이 왜 혼자서는 부족한지, 에이전트가 무엇을 더하는지를 손으로 확인합니다.</p>

<div class="kicker">
<div class="metric"><span class="num">45</span><strong>분</strong><span>이론 25 · 핸즈온 20</span></div>
<div class="metric"><span class="num">4</span><strong>한계</strong><span>LLM이 에이전트를 부르는 이유</span></div>
<div class="metric"><span class="num">1</span><strong>첫 부품</strong><span>classify_one.py</span></div>
</div>
</div>

<div class="board">
<div class="board-header"><span>이 챕터가 끝나면</span><span class="status-pill">산출물</span></div>
<div class="stack">
<div class="row"><div class="code">1</div><div class="copy"><strong>영수증 → RecordV1</strong><p>이미지 한 장을 읽어 판매처·금액·항목으로 구조화</p></div><div class="store">추출</div></div>
<div class="row"><div class="code">2</div><div class="copy"><strong>단발 vs ReAct</strong><p>합계를 스스로 검증하는 루프가 왜 필요한지 비교</p></div><div class="store">루프</div></div>
<div class="row"><div class="code">3</div><div class="copy"><strong>모델 비교표</strong><p>같은 영수증을 모델 3종에 물어 정확도·비용을 잰다</p></div><div class="store">선택</div></div>
</div>
</div>
</section>

<section class="slide">
<div class="section-head">
<div>
<div class="eyebrow">0 · 지금</div>

## 순위를 가르는 건 모델이 아니다

</div>
<p class="section-note">SWE-bench Verified는 실제 GitHub 이슈를 주고 코드를 고쳐 테스트를 통과시키는 벤치마크입니다. 1년 전 70%대였던 상위권이 지금은 90% 안팎에 몰려 있습니다.<br>
모델 단독 점수가 비슷해지면서 무게중심이 옮겨 갔습니다. 같은 모델이라도 어떤 실행 환경으로 감싸느냐가 결과를 가릅니다.</p>
</div>

<div class="grid-2">
<div class="panel"><div class="panel-head"><strong>성능은 평평해졌다</strong><span>SWE-bench Verified · 2026 중반</span></div><div class="panel-body"><div class="list">
<p>Fable 5 약 95% · Opus 4.8 88.6% · GPT-5.5 약 88.7%</p>
<p>Gemini 3.5 Flash 약 81% — 저비용인데도 상위권에 근접</p>
<p>상위 모델 사이 격차가 한 자릿수로 좁아졌습니다</p>
</div></div></div>
<div class="panel"><div class="panel-head"><strong>그래서 하네스다</strong><span>이 과정의 무게중심</span></div><div class="panel-body"><div class="list">
<p>LangChain은 모델(GPT-5.2-Codex)을 고정한 채 하네스만 손봐 Terminal-Bench 2.0을 52.8%→66.5%로 올렸습니다(Top 30 → Top 5).</p>
<p>가장 흔한 실패가 "코드를 쓰고 자기 코드를 다시 보고 괜찮다며 멈추는" 것이었고, <strong>종료 전 검증을 강제</strong>하자 13.7점이 올랐습니다.</p>
<p>오늘 우리가 ReAct 검산 루프로 손에 익힐 바로 그 패턴입니다.</p>
</div></div></div>
</div>

<div class="board" style="margin-top:18px">
<div class="board-header"><span>사례 — 20B 오픈 모델이 하네스로 프런티어를 이긴다</span><span class="status-pill">Harness-1 · 2026-06</span></div>
<div class="panel-body"><div class="list">
<p>UIUC·UC버클리·Chroma는 <strong>gpt-oss-20B</strong> 위에 "상태 기반 검색 하네스"를 얹어 <strong>Harness-1</strong>을 만들었습니다. 모델은 검색·추론에만 집중하고, 기억·기록은 하네스가 떠맡습니다(인지 부하의 외주).</p>
<p>큐레이션 리콜 0.730으로 GPT-5.4·Claude Sonnet 4.6·Kimi-K2.5를 능가했습니다(Opus 4.6만 근소 우위). 학습에 없던 벤치에서 +17점 — 하네스가 가르친 검색 습관이 옮겨 갑니다. 학습 데이터는 4,400건뿐이었습니다.</p>
<p>20B 모델이 프런티어급을 이기는 건 모델이 더 똑똑해서가 아니라 <strong>하네스 설계</strong> 때문입니다. 이 과정의 Ch2 체크포인터·Ch3 파일 퇴피가 정확히 그 "기록의 외주"입니다.</p>
</div></div>
</div>

<p class="section-note" style="margin-top:18px">Karpathy는 2025년을 영어만으로 프로그램을 짜는 임계점을 넘은 해로 평가했습니다. 코딩에서 시작된 이 변화는 영수증 분류, 문서 정리 같은 일반 업무로 번지는 중입니다. 우리가 만들 애널리스트가 정확히 그 자리에 있습니다.</p>
</section>

<section class="slide">
<div class="section-head">
<div>
<div class="eyebrow">1 · 한계</div>

## LLM은 다음 토큰을 예측할 뿐

</div>
<p class="section-note">LLM의 동작은 한 문장으로 줄어듭니다. 지금까지의 텍스트를 보고 다음 토큰을 예측합니다.<br>
사실을 알고 답하는 게 아니라 통계 패턴을 따라갑니다. 여기서 네 가지 한계가 곧바로 나오고, 이 넷이 에이전트의 존재 이유입니다.</p>
</div>

<div class="grid-4">
<div class="panel"><div class="panel-head"><strong>Stateless</strong><span>기억이 없다</span></div><div class="panel-body"><div class="list">
<p>매 요청마다 맥락을 다시 넣어야 합니다</p>
<p><span class="badge blue">Ch2</span> Checkpointer로 세션 유지</p>
</div></div></div>
<div class="panel"><div class="panel-head"><strong>Context Window</strong><span>한 번에 담는 양 제한</span></div><div class="panel-body"><div class="list">
<p>문서 10건을 한 프롬프트에 다 못 넣습니다</p>
<p><span class="badge blue">Ch3·4</span> 파일시스템 퇴피·점진 로딩</p>
</div></div></div>
<div class="panel"><div class="panel-head"><strong>Hallucination</strong><span>패턴 ≠ 현실</span></div><div class="panel-body"><div class="list">
<p>그럴듯하지만 틀린 값을 자신 있게 냅니다</p>
<p><span class="badge blue">Ch2·5</span> Tool로 조회·검증</p>
</div></div></div>
<div class="panel"><div class="panel-head"><strong>Knowledge Cutoff</strong><span>학습 이후를 모름</span></div><div class="panel-body"><div class="list">
<p>이번 달 영수증은 가중치에 없습니다</p>
<p><span class="badge blue">Ch4</span> 외부 데이터 연결</p>
</div></div></div>
</div>

<div class="board" style="margin-top:18px">
<div class="board-header"><span>환각은 버그가 아니라 채점의 산물</span><span class="status-pill">왜 검증이 필요한가</span></div>
<div class="panel-body"><div class="list">
<p>Kalai 외(2025)는 이진 채점 벤치마크가 "자신 있는 추측"을 보상해서 환각이 남는다고 봅니다. 모르면 0점이니 모델은 일단 찍습니다.</p>
<p>그래서 프로덕션 에이전트는 Tool로 실제 값을 조회하고, 답을 보류할 줄 알고, 결과를 한 번 더 검증합니다. 이 챕터의 ReAct 합계 검증이 그 가장 작은 형태입니다.</p>
</div></div>
</div>

<div class="ask"><strong>생각해보기 (30초).</strong> LLM이 "다음 토큰 예측기"라면, "오늘 달러·원 환율 알려줘"에 정확히 답할 수 있을까요? 답하거나 못 답한다면 그 이유는 위 네 한계 중 무엇일까요?</div>

<details>
<summary>정답 확인</summary>
<div class="reveal">
<p>답할 수 없습니다. 가중치에는 학습 시점까지의 통계 패턴만 들어 있어 <strong>실시간 값(환율·주가·내 영수증)</strong>에 닿을 길이 없습니다. 이건 4번 Knowledge Cutoff이자 3번 Hallucination의 뿌리입니다.</p>
<p>그럼에도 모델은 "모릅니다" 대신 그럴듯한 숫자를 자신 있게 내놓곤 합니다. 그래서 Tool로 실제 환율 API를 붙여 주는 에이전트가 필요합니다. 우리 실습에서는 같은 원리를 영수증 합계 검증으로 체험합니다.</p>
</div>
</details>
</section>

<section class="slide">
<div class="section-head">
<div>
<div class="eyebrow">1.5 · 들여다보기</div>

## "예측"을 눈으로 — logprobs와 temperature

</div>
<p class="section-note">"다음 토큰 예측기"가 추상이 아니라는 걸 짧게 확인합니다. <code>logprobs</code>로 모델이 토큰을 어떤 확률로 고르는지 보고, <code>temperature</code>로 그 선택이 얼마나 흔들리는지 봅니다.</p>
</div>

<div class="grid-2">
<div class="panel"><div class="panel-head"><strong>logprobs — 확신의 정체</strong><span>토큰 확률 분포</span></div><div class="panel-body"><div class="list">
<p>분류처럼 답이 또렷하면 한 토큰에 확률이 몰립니다(예: '식비' 98.6%).</p>
<p>애매하면 후보로 퍼집니다. 그래도 모델은 늘 최상위를 골라 답합니다 — "모르겠다"가 기본이 아닙니다. 이게 Kalai의 "자신 있는 추측".</p>
</div></div></div>
<div class="panel"><div class="panel-head"><strong>temperature — 왜 0인가</strong><span>추출의 재현성</span></div><div class="panel-body"><div class="list">
<p>온도가 0이면 늘 최상위 토큰, 높을수록 아래 후보도 뽑힙니다.</p>
<p>같은 영수증 → 같은 RecordV1이어야 하니 <code>classify_one</code>은 <code>temperature=0</code>. 창의가 필요한 글쓰기에서만 온도를 올립니다.</p>
</div></div></div>
</div>

<div class="board" style="margin-top:18px">
<div class="board-header"><span>직접 관찰</span><span class="status-pill">노트북</span></div>
<div class="panel-body"><div class="list">
<p>VSCode에서 <code>ch1-llm-basics/llm_internals.ipynb</code>를 열고 커널을 <code>.venv</code>로 맞춘 뒤 셀을 차례로 실행합니다. 실험1(logprobs)·실험2(temperature) 두 개입니다.</p>
<p>logprobs는 OpenAI 계열에서만 노출돼 <code>openai/gpt-4o-mini</code>로 관찰합니다. 확신해도 정답 보장이 아니라는 점, 추출은 0으로 고정한다는 점이 손에 잡힙니다.</p>
</div></div>
</div>
</section>

<section class="slide">
<div class="section-head">
<div>
<div class="eyebrow">2 · 루프</div>

## 에이전트는 한 번에 답하지 않는다

</div>
<p class="section-note">2022년 ReAct(Yao 외)가 제시한 구조가 지금 에이전트 루프의 기초입니다. 핵심은 <strong>모델이</strong> 추론하고, 도구를 부를지 스스로 정하고, 결과를 보고 다음을 판단한다는 점입니다.<br>
영수증으로 옮기면 이렇습니다. 모델이 항목을 뽑은 뒤 검산 도구를 직접 불러 확인하고, 어긋나면 스스로 다시 읽습니다. 이 되돌아가는 고리가 ReAct입니다.</p>
</div>

```mermaid
flowchart LR
    T["🧠 Thought<br/>합계를 검산해야겠다"] --> A["⚡ Action<br/>check_receipt_sum 호출"]
    A --> O["👁 Observation<br/>항목합 8,400 = 총액 8,400"]
    O --> Q{일치하나?}
    Q -- 아니오 --> T
    Q -- 예 --> F["✅ 최종 RecordV1"]
    style T fill:#fff3e0,stroke:#e09f3e
    style A fill:#e3f2fd,stroke:#315f9c
    style O fill:#e8f5e9,stroke:#0f766e
    style F fill:#f3e5f5,stroke:#6b4fa3
```

<div class="board" style="margin-top:18px">
<div class="board-header"><span>도구는 모델이 직접 실행하지 않는다</span><span class="status-pill">Tool Use의 실제</span></div>
<div class="panel-body"><div class="list">
<p>모델은 함수를 실행하는 대신 "이 함수를 이 인자로 부르라"는 구조화된 호출(<code>tool_calls</code>)을 냅니다. 런타임이 그걸 읽어 실제 함수를 돌리고 결과를 <code>ToolMessage</code>로 되돌려 줍니다.</p>
<p>그래서 Action은 모델이 낸 <code>tool_calls</code>, Observation은 런타임이 돌려준 <code>ToolMessage</code>입니다. 무엇을·언제 부를지는 모델이 정합니다 — 이게 단순 재시도 루프와 ReAct를 가르는 선입니다.</p>
</div></div>
</div>
</section>

<section class="slide">
<div class="section-head">
<div>
<div class="eyebrow">3 · 절제</div>

## 에이전트는 마지막 수단

</div>
<p class="section-note">Anthropic은 가장 단순하고 신뢰할 수 있는 구현을 먼저 쓰라고 강조합니다. 실행 흐름이 코드로 정해지는 워크플로와, 모델이 자율로 지휘하는 에이전트를 구분합니다.<br>
에이전트는 매 호출마다 시스템 프롬프트와 기록을 다시 보내므로 같은 일을 워크플로로 할 때보다 토큰이 몇 배 듭니다. 충분한 문제에 굳이 에이전트를 쓰지 않습니다.</p>
</div>

<div class="grid-2">
<div class="panel"><div class="panel-head"><strong>워크플로 — 흐름을 코드로 고정</strong><span>예측 가능·저비용</span></div><div class="panel-body"><div class="list">
<p>단일 호출 — "이 영수증 한 장을 구조화"</p>
<p>체이닝 — "분류 → 정규화 → 적재" 순서 고정</p>
<p>라우팅 — 문서 유형에 따라 다른 처리</p>
</div></div></div>
<div class="panel"><div class="panel-head"><strong>에이전트 — 모델이 자율 지휘</strong><span>유연·고비용</span></div><div class="panel-body"><div class="list">
<p>분해 — "이 인박스를 알아서 분석해 브리프로"</p>
<p>사전에 정해지지 않은 판단과 도구 선택이 필요할 때</p>
<p><span class="badge amber">Ch3</span> fan-out 조사에서 실측해 봅니다</p>
</div></div></div>
</div>

<p class="section-note" style="margin-top:18px">이 과정의 파이프라인은 대부분 워크플로입니다. 분류·정규화는 흐름이 정해져 있습니다. 에이전트가 빛나는 곳은 "여러 문서를 나눠 조사하고 교차 검산"하는 Ch3 한 구간입니다. 도구를 고를 때 이 구분이 첫 질문이 됩니다.</p>

<div class="ask"><strong>빠른 판단 연습 (2분).</strong> 다음 셋은 워크플로(단일 호출·체이닝·라우팅)일까요, 에이전트일까요?<br>
① 영수증 한 장을 RecordV1로 구조화 &nbsp;② 문서가 영수증인지 명세서인지에 따라 다른 처리로 분기 &nbsp;③ "이 인박스를 알아서 조사해 브리프로 정리"</div>

<details>
<summary>정답 확인</summary>
<div class="reveal">
<p>① <strong>단일 호출</strong> — 입력 하나 → 출력 하나. 반복도 도구도 필요 없습니다(Ch1 classify_one의 단발 모드).</p>
<p>② <strong>라우팅</strong> — 입력 종류에 따라 길이 갈릴 뿐, 각 길은 미리 정해져 있습니다.</p>
<p>③ <strong>에이전트</strong> — 몇 갈래로 볼지, 무슨 도구를 쓸지 사전에 못 박을 수 없습니다. 모델이 계획하고 반복합니다(Ch3 fan-out).</p>
<p>실무에서는 대부분 ①②로 충분합니다. ③이 정말 필요할 때만 비용을 감수하고 에이전트를 씁니다.</p>
</div>
</details>
</section>

<section class="slide">
<div class="section-head">
<div>
<div class="eyebrow">4 · 모델</div>

## 제일 똑똑한 모델이 정답은 아니다

</div>
<p class="section-note">에이전트의 두뇌는 모델입니다. 다만 가장 비싼 모델을 항상 쓰는 건 속도와 비용에서 손해입니다.<br>
역량과 단가로 세 자리를 잡아 두고 작업에 맞춰 올리고 내립니다. 분류·라우팅은 싼 모델로, 본 작업은 균형 모델로, 막히는 난제만 최상위로 올립니다.</p>
</div>

<div class="panel">
<div class="panel-head"><strong>2026년 중반 모델 자리표</strong><span>단가 = 입력/출력 · 1M 토큰 · 게이트웨이마다 다름</span></div>
<div class="panel-body">

| 자리 | 대표 모델 (ID) | 강점 | 대략 단가 | 쓰는 곳 |
|---|---|---|---|---|
| 프런티어급 | Fable 5 (`claude-fable-5`) | 최상위 추론·장기 코딩 (~95%) | ~$10 / ~$50 | 막판 난제 |
| 범용 주력 | Opus 4.8 (`claude-opus-4-8`) | 균형 잡힌 고성능 (88.6%) | ~$5 / ~$25 | 비교·심화 |
| 범용 주력 | GPT-5.5 (`gpt-5.5`) | 강한 범용 추론 (~88.7%) | ~$5 / ~$30 | 비교축 |
| 범용 주력 | **Gemini 3.5 Flash** (`google/gemini-3.5-flash`) | 빠르고 저렴 (~81%) | ~$1.5 / ~$9 | **이 과정 기본** |
| 경량 | Haiku 4.5 (`claude-haiku-4-5`) | 분류·대량 처리 | 최저가대 | 라우터·서브에이전트 |

</div>
</div>

<div class="board" style="margin-top:18px">
<div class="board-header"><span>기본값은 Gemini 3.5 Flash</span><span class="status-pill">실무 휴리스틱</span></div>
<div class="panel-body"><div class="list">
<p>저렴하고 빨라 8시간 내내 반복 실습에 맞습니다. 비교가 필요한 대목에서만 Opus 4.8로 올립니다.</p>
<p>점수 5%를 더 얻으려고 비용을 3배 쓰는 건 대개 손해입니다. 그래서 한 모델로 통일하지 않고 자리를 섞습니다. 이 챕터 끝의 비교표가 그 감각을 데이터로 줍니다.</p>
</div></div>
</div>
</section>

<section class="slide">
<div class="section-head">
<div>
<div class="eyebrow">5 · 3계층</div>

## Framework → Runtime → Harness

</div>
<p class="section-note">ReAct 루프는 강력하지만 프로덕션에서 또 막힙니다. 컨텍스트가 차고, 장기 실행이 어렵고, 실패 후 재시작 지점이 모호합니다.<br>
그래서 기술이 세 계층으로 자랐습니다. 오늘 하루가 이 세 계층을 아래에서 위로 직접 밟는 길입니다.</p>
</div>

<div class="flow" style="grid-template-columns:repeat(3,minmax(0,1fr))">
<div class="flow-step"><small>Framework</small><strong>LangChain</strong><p>LLM과 도구를 연결하고 기본 체이닝. 도구 상자에 해당합니다. <span class="badge">Ch2</span></p></div>
<div class="flow-step"><small>Runtime</small><strong>LangGraph</strong><p>상태·순환·조건부 분기를 그래프로. 작업 공정표에 해당합니다. <span class="badge">Ch2</span></p></div>
<div class="flow-step"><small>Harness</small><strong>DeepAgents</strong><p>계획·파일시스템·서브에이전트로 실행 전체를 관리. <span class="badge">Ch3</span></p></div>
</div>

<p class="section-note" style="margin-top:18px">이 3계층은 LangChain 생태계에서 자주 쓰는 설명 틀이고 업계 단일 표준은 아닙니다. 다른 프레임워크는 경계를 다르게 둡니다. 이 과정이 이 스택을 고른 이유는 세 역할이 또렷이 나뉘어 따로 배우기 좋기 때문입니다.</p>
</section>

<section class="slide">
<div class="section-head">
<div>
<div class="eyebrow">핸즈온 ① · 코드 정독</div>

## 멀티모달 호출을 뜯어본다

</div>
<p class="section-note">영수증 이미지 한 장을 모델에 보여 주고 RecordV1로 받습니다. 먼저 호출의 모양을 한 줄씩 읽습니다. 텍스트 프롬프트와 이미지를 <strong>한 메시지에 함께</strong> 실어 보내는 게 핵심입니다.</p>
</div>

```python
key = os.environ["OPENROUTER_API_KEY"]          # ① 키는 .env에서 (코드에 안 박는다)
llm = ChatOpenAI(model="google/gemini-3.5-flash",
                 base_url="https://openrouter.ai/api/v1",
                 api_key=key, temperature=0)     # ② temperature=0 — 추출은 매번 같아야 한다

prompt = EXTRACT_PROMPT.format(schema=schema_json(), source_path=...)  # ③ RecordV1 스키마를 지시에 끼움
msg = llm.invoke([{
    "role": "user",
    "content": [
        {"type": "text", "text": prompt},                       # ④ 무엇을 뽑을지
        {"type": "image_url", "image_url": {"url": data_url}},   # ⑤ 영수증 이미지(base64 data URL)
    ],
}])
record = RecordV1.model_validate_json(strip_fences(msg.content))  # ⑥ 받은 JSON을 계약으로 검증
```

<div class="grid-2">
<div class="panel"><div class="panel-head"><strong>왜 이렇게 쓰나 — ②③⑥</strong><span>설계 결정</span></div><div class="panel-body"><div class="list">
<p><strong>② temperature=0</strong> — 같은 영수증은 늘 같은 값으로 읽혀야 합니다. 창의성은 분류의 적입니다.</p>
<p><strong>③ 스키마를 프롬프트에</strong> — 모델이 RecordV1 한글 키(판매처·금액…)에 맞춰 JSON을 내도록 형식을 못 박습니다.</p>
<p><strong>⑥ model_validate_json</strong> — 모델 출력을 믿지 않고 계약으로 검증합니다. 필드가 빠지거나 타입이 틀리면 여기서 걸립니다.</p>
</div></div></div>
<div class="panel"><div class="panel-head"><strong>두 가지 함정 — ④⑤⑥</strong><span>자주 막히는 곳</span></div><div class="panel-body"><div class="list">
<p>이미지는 <code>data:image/png;base64,...</code> 형태의 data URL로 넣습니다. 경로 문자열이 아닙니다.</p>
<p>모델이 <code>```json … ```</code> 울타리를 붙여 답할 때가 있어 <code>strip_fences</code>로 벗긴 뒤 파싱합니다.</p>
</div></div></div>
</div>
</section>

<section class="slide">
<div class="section-head">
<div>
<div class="eyebrow">핸즈온 ② · 코드 정독</div>

## 합계를 스스로 검증한다 — ReAct

</div>
<p class="section-note">진짜 ReAct는 우리가 검증 함수를 부르는 게 아닙니다. <strong>모델이</strong> 추론 끝에 도구 호출을 결정하고(Action), 그 결과를 보고(Observation), 다음 행동을 정합니다. 모델에 <code>check_receipt_sum</code> 도구를 쥐여 주고 루프를 돌립니다.</p>
</div>

<div class="panel">
<div class="panel-head"><strong>ch1-llm-basics/classify_one.py</strong><span>모델이 도구를 직접 호출하는 ReAct 루프</span></div>
<div class="panel-body">

```python
@tool
def check_receipt_sum(items: list[dict], total: float) -> str:
    """영수증 항목 합계가 총액과 맞는지 검산한다. 추출 직후 반드시 호출하라."""
    s = sum((it.get("amount") or 0) * (it.get("qty") or 1)
            for it in items if (it.get("amount") or 0) > 0)
    ok = abs(s - total) < 1.0
    return f"항목합={s:,.0f} 총액={total:,.0f} → " + ("일치" if ok else "불일치. 다시 보라")

def extract_react(doc, model, max_steps=5):
    llm = ChatOpenAI(model=model, ...).bind_tools([check_receipt_sum])  # 도구를 쥐여 준다
    messages = [SystemMessage(REACT_SYSTEM), HumanMessage([text, image])]
    for _ in range(max_steps):
        ai = llm.invoke(messages); messages.append(ai)
        if ai.tool_calls:                              # Action — 모델이 호출을 결정
            for tc in ai.tool_calls:
                obs = check_receipt_sum.invoke(tc["args"])   # 런타임이 실제 실행
                print(f"  [Observation] {obs}")
                messages.append(ToolMessage(obs, tool_call_id=tc["id"]))
            continue                                   # 관측을 들고 다시 모델에게
        return RecordV1.model_validate_json(strip_fences(ai.content))  # 도구 안 부름 = 최종
```

</div>
</div>

<div class="grid-3" style="margin-top:16px">
<div class="panel"><div class="panel-head"><strong>무엇이 ReAct인가</strong></div><div class="panel-body"><div class="list">
<p>도구 선택을 <strong>모델이</strong> 합니다. <code>tool_calls</code>가 Action, <code>ToolMessage</code>가 Observation입니다.</p>
</div></div></div>
<div class="panel"><div class="panel-head"><strong>단발과 무엇이 다른가</strong></div><div class="panel-body"><div class="list">
<p>단발은 한 번 뱉고 끝. ReAct는 검산이 불일치면 모델이 스스로 다시 읽어 고칩니다.</p>
</div></div></div>
<div class="panel"><div class="panel-head"><strong>왜 max_steps</strong></div><div class="panel-body"><div class="list">
<p>모델이 도구를 무한 반복하지 않도록 상한을 둡니다. 한계 설정이 하네스의 일입니다.</p>
</div></div></div>
</div>
</section>

<section class="slide">
<div class="section-head">
<div>
<div class="eyebrow">핸즈온 ③ · 단계별 실행</div>

## 돌리고, 관찰하고, 바꿔 본다

</div>
<p class="section-note">키 없이 파이프라인부터 확인하고, 키를 넣어 실제 추출을 본 뒤, 모델을 비교합니다. 각 단계마다 무엇이 보이면 성공인지 적었습니다.</p>
</div>

<div class="stack">
<div class="row"><div class="code">1</div><div class="copy"><strong>키 없이 — 파이프라인 확인</strong><p><code>uv run python3 ch1-llm-basics/classify_one.py --doc receipt_starbucks.png --mock</code><br><span style="color:var(--muted)">성공 기준: 판매처·금액·항목이 든 RecordV1 JSON이 한글 키로 출력된다.</span></p></div><div class="store">mock</div></div>
<div class="row"><div class="code">2</div><div class="copy"><strong>키 넣고 — ReAct 추출</strong><p><code>uv run python3 ch1-llm-basics/classify_one.py --doc receipt_gs25.png --react</code><br><span style="color:var(--muted)">성공 기준: <code>[Action] check_receipt_sum 호출</code> → <code>[Observation] 항목합=8,400원 총액=8,400원 → 일치</code> → <code>[Final]</code>, "정확도 100%". 모델이 도구를 스스로 부른 것.</span></p></div><div class="store">실호출</div></div>
<div class="row"><div class="code">3</div><div class="copy"><strong>모델 3종 비교</strong><p><code>uv run python3 ch1-llm-basics/classify_one.py --doc receipt_gs25.png --compare</code><br><span style="color:var(--muted)">성공 기준: 세 모델의 정확도가 표로 나온다(비용 감각의 출발점).</span></p></div><div class="store">선택</div></div>
</div>

<div class="ask" style="margin-top:18px"><strong>직접 해보기.</strong> ① <code>--doc invoice_photo.png</code>로 바꿔 명세서를 뽑아 보세요(영수증이 아니라 합계 검증을 건너뜁니다). ② <code>verify_total</code>의 허용 오차 <code>1.0</code>을 <code>0.0</code>으로 바꾸면 어떤 영수증이 불일치로 떨어질까요?</div>

<details>
<summary>관찰 포인트</summary>
<div class="reveal">
<p>① 명세서는 <code>doc_type</code>이 영수증이 아니라 <code>extract_react</code>가 검증 루프를 건너뛰고 바로 반환합니다. 합계 규칙이 다른 문서를 억지로 검증하지 않는다는 설계가 코드로 보입니다.</p>
<p>② 모델이 항목을 살짝 다르게 읽으면 1원 단위 오차가 생길 수 있습니다. 허용 오차는 "얼마나 깐깐하게 볼까"의 손잡이입니다. 너무 0에 가까우면 정상도 불일치로 떨어지고, 너무 크면 진짜 오류를 놓칩니다.</p>
</div>
</details>
</section>

<section class="slide">
<div class="section-head">
<div>
<div class="eyebrow">핸즈온 ④ · 트러블슈팅</div>

## 막히면 여기부터

</div>
<p class="section-note">실호출에서 자주 만나는 네 가지입니다. 대부분 키·슬러그·네트워크 셋 중 하나입니다.</p>
</div>

<div class="grid-2">
<div class="panel"><div class="panel-head"><strong>401 Unauthorized</strong><span>인증</span></div><div class="panel-body"><div class="list">
<p><code>.env</code>의 <code>OPENROUTER_API_KEY</code>가 비었거나 <code>sk-or-...</code> placeholder 그대로입니다. 실제 키로 채웠는지 확인합니다.</p>
</div></div></div>
<div class="panel"><div class="panel-head"><strong>404 Model not found</strong><span>슬러그</span></div><div class="panel-body"><div class="list">
<p>모델 슬러그 오타입니다. <code>google/gemini-3.5-flash</code>처럼 제공자/모델 형태가 맞는지 봅니다.</p>
</div></div></div>
<div class="panel"><div class="panel-head"><strong>JSON 파싱 오류</strong><span>출력 형식</span></div><div class="panel-body"><div class="list">
<p>모델이 설명 문장을 덧붙였을 수 있습니다. <code>strip_fences</code>가 울타리는 벗기지만, 프롬프트에 "JSON만 출력"을 더 강하게 둘 수도 있습니다.</p>
</div></div></div>
<div class="panel"><div class="panel-head"><strong>빈 응답 · 타임아웃</strong><span>네트워크</span></div><div class="panel-body"><div class="list">
<p>네트워크나 게이트웨이 일시 문제입니다. 잠시 후 재시도하거나 <code>--mock</code>으로 흐름만 먼저 확인합니다.</p>
</div></div></div>
</div>

<div class="board" style="margin-top:18px">
<div class="board-header"><span>이 챕터에서 손에 든 것</span><span class="status-pill">체크</span></div>
<div class="panel-body"><div class="list">
<p>영수증 이미지 → RecordV1 추출기 · 단발과 ReAct의 차이 · 모델 3종의 정확도 감각</p>
<p>전체 실행 파일은 <code>ch1-llm-basics/classify_one.py</code> 하나에 추출·검증·채점·비교가 다 들어 있습니다.</p>
</div></div>
</div>
</section>

<section class="slide">
<div class="section-head">
<div>
<div class="eyebrow">마무리</div>

## 다음 — 흐름을 그래프로 묶는다

</div>
<p class="section-note">영수증 한 장을 RecordV1로 읽는 부품이 생겼습니다. 다음은 문서 더미 전체를 분류하고 정규화하는 흐름입니다.<br>
Ch2에서 LangGraph로 이 단발 추출을 상태·재시도·중단점이 있는 파이프라인으로 묶습니다. 고액이나 저신뢰 건은 사람에게 멈춰 묻습니다.</p>
</div>

<div class="grid-3">
<div class="panel"><div class="panel-head"><strong>지금 손에 든 것</strong></div><div class="panel-body"><div class="list">
<p>영수증 → RecordV1 추출기</p>
<p>단발 vs ReAct · 모델 비교 감각</p>
</div></div></div>
<div class="panel"><div class="panel-head"><strong>Ch2에서 할 것</strong></div><div class="panel-body"><div class="list">
<p>분류·정규화 StateGraph</p>
<p>checkpointer 재개 · interrupt() HITL</p>
</div></div></div>
<div class="panel"><div class="panel-head"><strong>최종 목적지</strong></div><div class="panel-body"><div class="list">
<p>인박스 한 통 → 검증된 브리프</p>
<p>Ch6 통합 캡스톤</p>
</div></div></div>
</div>

<div class="board" style="margin-top:18px">
<div class="board-header"><span>참고 자료</span><span class="status-pill">출처</span></div>
<div class="panel-body"><div class="list">
<p><a href="https://arxiv.org/abs/2210.03629">ReAct (Yao 외, 2022)</a> · <a href="https://www.anthropic.com/engineering/building-effective-agents">Anthropic — Building Effective Agents</a></p>
<p><a href="https://arxiv.org/abs/2509.04664">Why Language Models Hallucinate (Kalai 외, 2025)</a> · <a href="https://llm-stats.com/benchmarks/swe-bench-verified">llm-stats.com — SWE-bench Verified</a></p>
<p><a href="https://blog.langchain.com/improving-deep-agents-with-harness-engineering/">LangChain — Improving Deep Agents with Harness Engineering</a> (Terminal-Bench 2.0 52.8→66.5) · <a href="https://martinfowler.com/articles/exploring-gen-ai/harness-engineering.html">Fowler — Harness Engineering</a></p>
<p><strong>하네스 사례</strong> — <a href="https://arxiv.org/abs/2606.02373">Harness-1: Reinforcement Learning for Search (UIUC·UC Berkeley·Chroma, 2026)</a></p>
</div></div>
</div>
</section>


<nav class="chapnav">
<div class="board" style="margin-top:8px">
<div style="display:grid;grid-template-columns:1fr auto 1fr;gap:14px;align-items:center">
<a href="/chapters/chapter-0" style="color:inherit;text-decoration:none;font-weight:900;font-size:14px">← Ch0 · 환경 셋업</a>
<a href="/toc" style="color:var(--forest);text-decoration:none;font-weight:900;font-size:13px;background:rgba(148,210,189,.3);border:1px solid rgba(15,118,110,.24);border-radius:99px;padding:7px 16px">목차</a>
<a href="/chapters/chapter-2" style="color:inherit;text-decoration:none;font-weight:900;font-size:14px;text-align:right">Ch2 · LangGraph 하네스 →</a>
</div>
</div>
</nav>

</div>
</div>
