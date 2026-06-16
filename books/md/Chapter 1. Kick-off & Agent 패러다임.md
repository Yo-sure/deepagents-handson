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
<p>LangChain은 같은 모델에 하네스만 더해 Terminal-Bench 52.8%→66.5%로 올렸습니다</p>
<p>모델을 바꾼 게 아니라 실행을 감싸는 방법을 바꿨습니다</p>
<p>오늘 8시간의 절반이 이 "감싸는 법"입니다</p>
</div></div></div>
</div>

<p class="section-note" style="margin-top:18px">Karpathy는 2025년을 영어만으로 프로그램을 짜는 임계점을 넘은 해로 평가했습니다. 코딩에서 시작된 이 변화는 메일 분류, 문서 정리 같은 일반 업무로 번지는 중입니다. 우리가 만들 애널리스트가 정확히 그 자리에 있습니다.</p>
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
</section>

<section class="slide">
<div class="section-head">
<div>
<div class="eyebrow">2 · 루프</div>

## 에이전트는 한 번에 답하지 않는다

</div>
<p class="section-note">2022년 ReAct(Yao 외)가 제시한 구조가 지금 에이전트 루프의 기초입니다. 답을 한 번에 내지 않고 생각·행동·관찰을 반복합니다.<br>
영수증으로 옮기면 이렇습니다. 합계가 맞는지 항목을 더해 보고, 어긋나면 다시 읽습니다.</p>
</div>

<div class="flow">
<div class="flow-step"><small>Thought</small><strong>무엇을 할지 판단</strong><p>"항목 금액을 더해 총액과 맞는지 봐야겠다"</p></div>
<div class="flow-step"><small>Action</small><strong>도구를 호출</strong><p><code>verify_total(record)</code> — 항목 합계를 계산</p></div>
<div class="flow-step"><small>Observation</small><strong>결과를 관찰</strong><p>"항목합 11,500 · 총액 11,500 → 일치"</p></div>
<div class="flow-step"><small>반복 · 종료</small><strong>충분하면 종료</strong><p>맞으면 확정, 어긋나면 다시 Thought로</p></div>
</div>

<div class="board" style="margin-top:18px">
<div class="board-header"><span>도구는 모델이 직접 실행하지 않는다</span><span class="status-pill">Tool Use의 실제</span></div>
<div class="panel-body"><div class="list">
<p>모델은 함수를 실행하는 대신 "이 함수를 이 인자로 부르라"는 구조화된 호출을 텍스트로 냅니다. 런타임이 그걸 읽어 실제 함수를 돌리고 결과를 다시 넘깁니다.</p>
<p>실습에서 Thought는 도구 호출 직전 맥락, Action은 <code>tool_calls</code> 이벤트, Observation은 그 반환값으로 드러납니다.</p>
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
<div class="eyebrow">핸즈온 · 20분</div>

## 첫 부품 — classify_one.py

</div>
<p class="section-note">영수증 이미지 한 장을 모델에 보여 주고 RecordV1로 받습니다. 호출의 모양부터 봅니다. 텍스트 프롬프트와 이미지를 한 메시지에 함께 실어 보냅니다.<br>
키가 없으면 <code>--mock</code>으로 gold 값을 적재해 파이프라인을 끝까지 돌려 볼 수 있습니다.</p>
</div>

```python
# 멀티모달 호출의 모양 — 텍스트 + 이미지를 한 메시지에
msg = llm.invoke([{
    "role": "user",
    "content": [
        {"type": "text", "text": prompt},                       # RecordV1 스키마를 끼운 지시
        {"type": "image_url", "image_url": {"url": data_url}},   # 영수증 이미지(base64)
    ],
}])
record = RecordV1.model_validate_json(strip_fences(msg.content))  # 계약으로 검증
```

<div class="grid-2">
<div class="panel"><div class="panel-head"><strong>단발 — extract_singleshot</strong><span>한 번 호출, 빠르다</span></div><div class="panel-body"><div class="list">
<p>이미지를 한 번 보여 주고 JSON을 받습니다</p>
<p>합계가 틀려도 그대로 통과합니다</p>
</div></div></div>
<div class="panel"><div class="panel-head"><strong>ReAct — extract_react</strong><span>합계를 스스로 검증</span></div><div class="panel-body"><div class="list">
<p>추출 후 <code>verify_total</code>로 항목합을 계산합니다</p>
<p>총액과 어긋나면 한 번 더 읽어 보정합니다</p>
</div></div></div>
</div>

<div class="panel" style="margin-top:18px">
<div class="panel-head"><strong>ch1-llm-basics/classify_one.py</strong><span>합계 검증 루프 — ReAct를 가장 작게</span></div>
<div class="panel-body">

```python
def verify_total(rec: RecordV1) -> tuple[bool, float]:
    """Action — 항목 합계가 총액과 맞는지 계산한다(Observation 생성)."""
    item_sum = sum((i.amount or 0) * (i.qty or 1) for i in rec.items if (i.amount or 0) > 0)
    return abs(item_sum - rec.total) < 1.0, item_sum


def extract_react(doc: str, model: str, max_loops: int = 2) -> RecordV1:
    """추출 → 합계 검증 → 어긋나면 다시 추출. ReAct 한 바퀴를 직접 돈다."""
    rec = extract_singleshot(doc, model)
    if rec.doc_type != DocType.receipt.value:
        return rec
    for loop in range(max_loops):
        ok, item_sum = verify_total(rec)
        print(f"  [Observation] 항목합={item_sum:,.0f} / 총액={rec.total:,.0f}"
              f" → {'일치' if ok else '불일치'}")
        if ok:
            break
        print("  [Thought] 합계가 안 맞는다. 항목을 다시 읽어 보정한다.")
        rec = extract_singleshot(doc, model)
    return rec
```

<p style="margin-top:12px;color:var(--muted);font-size:13px">전체 실행 파일은 <code>ch1-llm-basics/classify_one.py</code>. 단발 추출·채점·모델 비교까지 한 파일에 들어 있습니다.</p>

</div>
</div>

<div class="board" style="margin-top:18px">
<div class="board-header"><span>직접 실행</span><span class="status-pill">터미널</span></div>
<div class="stack">
<div class="row"><div class="code">m</div><div class="copy"><strong>키 없이 — 파이프라인 확인</strong><p><code>uv run python3 ch1-llm-basics/classify_one.py --doc receipt_starbucks.png --mock</code></p></div><div class="store">mock</div></div>
<div class="row"><div class="code">r</div><div class="copy"><strong>키 넣고 — ReAct 추출</strong><p><code>uv run python3 ch1-llm-basics/classify_one.py --doc receipt_gs25.png --react</code></p></div><div class="store">실호출</div></div>
<div class="row"><div class="code">c</div><div class="copy"><strong>모델 3종 비교표</strong><p><code>uv run python3 ch1-llm-basics/classify_one.py --doc receipt_gs25.png --compare</code></p></div><div class="store">선택</div></div>
</div>
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
<p><a href="https://blog.langchain.com/deep-agents/">LangChain Deep Agents</a> — Terminal-Bench 수치 · <a href="https://martinfowler.com/articles/exploring-gen-ai/harness-engineering.html">Fowler — Harness Engineering</a></p>
</div></div>
</div>
</section>

</div>
</div>
