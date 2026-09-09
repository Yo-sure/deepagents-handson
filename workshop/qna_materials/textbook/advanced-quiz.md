원본: books/workshop/advanced-quiz.md

---
layout: page
title: 심화 문제 · 실행을 예측하고 설계를 설명합니다
sidebar: false
aside: false
pageClass: lec-page
---

<div class="lec workshop-edition"><div class="deck">
<section class="slide">
<div class="eyebrow">선택 심화 · 수업 뒤 독립 풀이</div>

# 심화 문제 · 실행을 예측하고 설계를 설명합니다

API 이름을 기억하는 대신 코드를 완성하고, 실패한 실행을 설명하고, 요구에 맞는 구조를 선택합니다. 1일 수업에 추가로 배정된 시간이 아닙니다. 관심 있는 문항부터 골라 풉니다. 실제 인증시험을 복제한 문제가 아니라 이 교재를 위해 만든 문항입니다.

각 문항의 답을 노트북의 새 Markdown 셀이나 자신의 메모에 적은 뒤 해설을 펼칩니다. 코드 문항은 별도 코드 셀에서 실행할 수 있습니다. 웹페이지에는 답이 저장되지 않습니다. 함수 이름과 문장 표현이 달라도 조건과 근거를 만족하면 타당한 답입니다.

문항별 채점 기준은 각 1점, 총 3점입니다. 10문항 합계 30점은 복습 기록용이며 합격 기준이나 숙련도 인증이 아닙니다. 대표 오답의 이유를 설명하고 반례를 직접 만들 수 있는지도 확인합니다.

|유형|문항|
|---|---|
|코드 일부 완성|[1. 생성 전 분기](#q1), [4. 수정 예산](#q4), [7. 검토 수용](#q7)|
|실행 결과 추론|[2. 기록 병합](#q2), [3. 승인 재개](#q3), [5. MCP 실행 경계](#q5)|
|설계 판단|[6. 다음 실행의 문맥](#q6), [8. Card와 업무 계약](#q8), [9. 연결 방식 선택](#q9), [10. 병렬 검토](#q10)|

예제는 교재의 고정 환경과 계약을 따릅니다. MCP는 2026-07-28 명세, A2A는 v1이며, `accepted/held/pending`은 프로토콜 상태가 아닌 수업의 업무 판정입니다. 문항의 간단한 Python 함수는 별도 모델이나 서버 없이 풀 수 있습니다.

</section>
<section class="slide" id="q1">

## 1. 생성 전에 무엇을 확인할까요?

**코드 일부 완성.** 앞선 조회 결과를 재사용하려는데 다른 업무의 결과가 섞였습니다. 조건부 간선의 라우팅 함수 `choose_path`를 작성합니다. 반환값은 같은 이름의 `lookup`·`draft`·`ask` 노드에 연결됩니다. `state["topic"]`은 현재 요청의 업무이고 `state["data"]["topic"]`은 조회한 업무입니다. 두 값은 정규화된 문자열이며, `found`는 bool, `contact`는 문자열 또는 누락이라고 가정합니다.

- 조회한 업무가 현재 요청과 다르면 `found` 값과 관계없이 `lookup`에서 다시 조회합니다.
- 업무가 일치하고 정책을 찾았으며 회신 대상이 공백이 아닐 때만 `draft`로 갑니다.
- 업무가 일치하지만 정책이나 회신 대상이 부족하면 `ask`로 갑니다.

```python
def choose_path(state):
    # 여기에 작성: "lookup", "draft", "ask" 중 하나 반환
    raise NotImplementedError

cases = [
    ({"topic": "정산", "data": {"topic": "정산", "found": True},
      "contact": "user@example.test"}, "draft"),
    ({"topic": "정산", "data": {"topic": "정산", "found": True},
      "contact": "   "}, "ask"),
    ({"topic": "정산", "data": {"topic": "정산", "found": False},
      "contact": "user@example.test"}, "ask"),
    ({"topic": "정산", "data": {"topic": "정산", "found": True}}, "ask"),
    ({"topic": "정산", "data": {"topic": "계정", "found": True},
      "contact": "user@example.test"}, "lookup"),
    ({"topic": "정산", "data": {"topic": "계정", "found": False},
      "contact": "user@example.test"}, "lookup"),
]
for state, expected in cases:
    assert choose_path(state) == expected
```

마지막 입력에서 바로 `ask`로 가면 어떤 결론을 너무 일찍 내리는지 설명합니다. 다시 조회한 결과에도 업무명이 계속 잘못 들어 있다면, 무한 재조회를 막기 위해 호출자에 어떤 중단 조건을 둘지도 제안합니다.

모델 지침에 같은 조건을 적었더라도 이 분기를 유지할 이유가 있는지 덧붙입니다.

<details><summary>해설 · 구현 예와 채점 기준</summary>

```python
def choose_path(state):
    if state["data"]["topic"] != state["topic"]:
        return "lookup"
    has_policy = state["data"]["found"]
    has_contact = bool(state.get("contact", "").strip())
    return "draft" if has_policy and has_contact else "ask"
```

조건부 간선의 라우팅 함수는 다음 경로를 고릅니다. 다른 업무에서 정책을 못 찾았다는 결과는 현재 업무에도 정책이 없다는 근거가 아닙니다. 현재 업무를 재조회하고 판단해야 합니다. 재조회 상한을 정하고, 상한 뒤에도 업무가 불일치하면 오류를 기록하고 중단하는 제어가 필요합니다. 부족한 정보와 질문 문장을 State에 저장하는 일은 `ask` 노드가 맡습니다. 생성 전에 코드로 조건을 검사하면 모델이 지침을 놓쳐도 그 경로에서는 초안 생성 함수를 실행하지 않습니다. 입력 타입 검증은 별도 경계이며, 이 함수가 이메일 주소의 실재 여부를 검증하는 것은 아닙니다.

**채점:** 여섯 입력의 경로와 업무 일치 검사 우선순위 1점; 다른 업무의 실패를 현재 업무의 부재로 해석하지 않는 이유와 재조회 중단 조건 1점; 지침과 실행 관문·State 갱신의 차이 설명 1점. `if`를 나누거나 조기 반환해도 동일하게 채점합니다.

**대표 오답:** `if contact`만 검사하면 공백 세 칸도 참입니다. 정책이 없을 때 임의로 `draft`를 선택하면 모델에 추측을 맡기게 됩니다.

근거: [LangGraph 조건 간선](https://docs.langchain.com/oss/python/langgraph/graph-api#conditional-edges), [워크플로와 Agent의 제어 차이](https://www.anthropic.com/engineering/building-effective-agents).

</details>
</section>
<section class="slide" id="q2">

## 2. 같은 방문 기록이 왜 두 번 남을까요?

**실행 결과 추론.** 조회가 끝난 직후 `visited=["lookup"]`입니다. 순차 실행되는 다음 노드가 아래 값을 반환합니다.

```python
update = {"visited": ["lookup", "draft"]}
```

필드의 규칙이 기본 교체일 때와 `Annotated[list[str], add]`일 때 최종 목록을 각각 적습니다. 이어 누적 reducer를 유지하면서 노드만 고치는 방법을 제시합니다. `topic`이 이번 반환에 없으면 사라지는지도 설명합니다.

<details><summary>해설 · 결과와 채점 기준</summary>

기본 교체이면 `["lookup", "draft"]`, `add`이면 `["lookup", "lookup", "draft"]`입니다. 누적 reducer를 유지하려면 노드는 `{"visited": ["draft"]}`처럼 이번 기록만 반환합니다. 반환하지 않은 `topic`은 기존 State에 남습니다.

다른 타당한 설계는 reducer를 제거하고 기존 목록을 직접 붙여 반환하는 방식입니다. 다만 문제의 “reducer 유지” 조건을 만족하는 답과는 구별합니다. 스키마만 바꾸고 노드 반환을 그대로 두면 누적 책임이 중복됩니다.

**채점:** 두 출력 정확히 예측 1점; 새 항목만 반환하도록 수정 1점; 누락 필드 보존과 필드별 병합 설명 1점.

**대표 오답:** “리스트이므로 자동으로 중복 제거된다.” `add`는 리스트를 연결하며 항목의 의미나 중복을 판정하지 않습니다. 실제 방문 순서가 중요하면 단순 집합 변환도 적절하지 않을 수 있습니다.

근거: [LangGraph Reducers](https://docs.langchain.com/oss/python/langgraph/graph-api#reducers).

</details>
</section>
<section class="slide" id="q3">

## 3. 승인을 눌렀는데 외부 기록이 두 번 생성됩니다

**실행 결과 추론.** 아래 노드에 checkpointer가 연결되어 있고 최초 실행은 `interrupt`에서 멈춥니다. 같은 저장소·thread ID로 한 번 재개하며, 다른 재시도는 없다고 가정합니다. `create_ticket`은 호출마다 외부 티켓을 새로 만듭니다. 설명용 코드이며 외부 서비스를 실행하지 않습니다.

```python
from langgraph.types import interrupt

def approval(state):
    ticket_id = create_ticket(state["draft"])
    approved = interrupt({"ticket_id": ticket_id})
    return {"approved": approved, "ticket_id": ticket_id}
```

최초 중단까지와 한 번 재개한 뒤의 티켓 생성 횟수를 적습니다. 승인 전에 티켓 생성 자체가 허용되지 않는 요구라면 어떻게 나눌까요? 승인 후 처리 노드에서 장애가 나도 중복 생성을 막을 방법을 덧붙입니다.

<details><summary>해설 · 재실행 범위와 채점 기준</summary>

최초 중단까지 1회, 한 번 재개한 뒤 누적 2회입니다. 재개할 때 중단된 노드를 처음부터 실행하므로 `interrupt` 앞의 외부 작업도 다시 수행합니다. 지역 변수의 실행 위치를 보존하여 다음 줄부터 이어가는 방식이 아닙니다.

초안 준비 → 승인 전용 노드 → 승인 분기 → 티켓 생성 노드로 나눌 수 있습니다. 승인 요청에는 초안 ID·버전 등 판단 대상을 담습니다. 생성 노드도 장애로 재시도될 수 있으므로 외부 서비스의 idempotency key나 작업 ID의 유일성 제약을 이용합니다. 단순히 저장소를 확인한 뒤 생성하는 것만으로는 충분하지 않습니다. 외부 생성 성공 직후 결과 저장 전에 장애가 나도 중복을 막으려면, 같은 키의 생성 요청을 외부 서비스가 원자적으로 중복 제거하거나 생성 결과를 동일한 키로 다시 조회할 수 있어야 합니다.

**채점:** 1회/누적2회 예측 1점; 승인 이전 부작용 제거 1점; 생성 단계의 재시도와 중복 방지를 별도로 설명 1점.

**대표 오답:** “checkpointer가 있으므로 외부 API도 정확히 한 번 실행된다.” 그래프 상태 저장과 외부 시스템의 트랜잭션은 같은 보장이 아닙니다.

근거: [LangGraph Interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts).

</details>
</section>
<section class="slide" id="q4">

## 4. 마지막 허용 수정에서 성공했습니다

**코드 일부 완성.** `check(draft)`는 실패 이유 목록을 반환하고 성공이면 빈 목록을 반환합니다. `revise(draft, feedback)`는 수정 초안을 반환합니다. 수정 상한은 0 이상의 정수라고 가정합니다. 다음 함수의 TODO 부분을 구현합니다. 전체 함수에서 수정은 최대 `limit`회이며, 마지막 수정본도 검사해야 합니다. 이 문항에서는 정체 판정을 생략합니다.

```python
def improve(draft, check, revise, limit):
    for attempt in range(limit + 1):
        feedback = check(draft)
        # TODO: 성공이면 ("passed", draft) 반환
        # TODO: 실패이고 예산을 소진했으면 ("held", draft) 반환
        # TODO: 남은 예산으로 수정
    raise AssertionError("도달하면 안 되는 지점")
```

반례를 만듭니다: 상한0에서 최초 성공, 상한0에서 최초 실패, 상한2의 마지막 수정에서 성공, 상한2를 모두 써도 실패. 각 경우의 수정 횟수와 검사 횟수도 적습니다.

<details><summary>해설 · 구현 예와 채점 기준</summary>

```python
def improve(draft, check, revise, limit):
    for attempt in range(limit + 1):
        feedback = check(draft)
        if not feedback:
            return "passed", draft
        if attempt == limit:
            return "held", draft
        draft = revise(draft, feedback)
```

네 경우의 수정/검사 횟수는 각각 0/1, 0/1, 2/3, 2/3입니다. 성공을 먼저 검사해야 마지막 허용 수정의 성공을 `held`로 덮지 않습니다. `while`과 별도 수정 카운터로 구현해도 같은 계약이면 타당합니다.

**채점:** 성공·예산 순서 1점; 최대 수정 횟수 준수 1점; 네 반례와 검사 횟수 설명 1점.

**대표 오답:** `range(limit)`만 돌고 바로 보류하면 마지막 수정본을 검사하지 않을 수 있습니다. 프롬프트에 “두 번만 수정”이라고 적는 것도 이 호출자 코드의 상한을 대신하지 않습니다.

이 순서는 수업의 `build_lab/guided.py`에 있는 수정 정책입니다. 아래 출처는 평가·수정 반복의 설계 배경이며 위 카운터 구현을 규정하는 표준은 아닙니다. [Anthropic 평가자·최적화자 패턴](https://www.anthropic.com/engineering/building-effective-agents).

</details>
</section>
<section class="slide" id="q5">

## 5. 도구 오류와 조회 결과 없음은 같은 실패일까요?

**실행 결과 추론.** `lookup_policy(topic: str)`는 미등록 업무에도 `found=false`를 정상 반환합니다. `topic`은 필수 필드입니다. 함수 실행 기록은 처음에 비어 있습니다. 수업 4A와 같이 아래 단계를 순서대로 수행합니다.

|단계|조작|
|---|---|
|A|함수를 MCP 서버의 도구로 등록|
|B|`tools/list` 요청|
|C|`tools/call`, 인자 `{"topic": "없는업무"}`|
|D|`tools/call`, 인자 `{}`|

각 단계 뒤 함수의 누적 실행 횟수를 적습니다. C와 D가 모델에 전달될 때 구별해야 할 정보는 무엇인가요? Python 예외가 없었다는 이유만으로 성공으로 기록해도 될까요?

<details><summary>해설 · 경계와 채점 기준</summary>

수업 서버의 입력 검증을 기준으로 누적 횟수는 0, 0, 1, 1입니다. 등록과 목록 조회는 업무 함수를 실행하지 않습니다. 미등록 업무는 유효한 요청을 실행한 결과이고, 필수 입력 누락은 함수 본문 전에 거절됩니다.

C에는 `found=false`가 있으므로 추가 업무 정보를 요청합니다. D에는 입력 오류가 있으므로 요청 인자를 고칩니다. 고정 환경의 MCPAdapter는 도구 오류를 내용으로 반환할 수 있고, Agent 경로에서는 ToolMessage의 오류 상태도 확인합니다. 예외 유무·최종 답변만 보지 말고 오류 내용, 메시지 상태, 실제 함수 실행 기록을 함께 읽습니다.

**채점:** 누적0/0/1/1 예측 1점; 업무상 결과 없음과 입력 오류 구별 1점; 호출 경로에 맞는 오류 증거 설명 1점.

**대표 오답:** “둘 다 결과가 없으므로 같은 인자로 재시도한다.” C에는 정책을 추측하지 않는 후속 질문이 필요하고, D에는 빠진 인자를 보완해야 합니다.

근거: [MCP 2026-07-28 Tools](https://modelcontextprotocol.io/specification/2026-07-28/server/tools). Python 포장 방식은 수업의 고정 SDK·Adapter 구현을 따릅니다.

</details>
</section>
<section class="slide" id="q6">

## 6. 다음 실행에 무엇을 남길까요?

**설계 판단.** 긴 코드 수정 작업의 현재 기록입니다.

- 요구: 공백 회신 대상이면 생성하지 않아야 합니다.
- 후보 버전: v3. 공백 입력에서 아직 생성 함수가 1회 호출됩니다.
- 변경 파일: `router.py`. 마지막 테스트 명령과 실패 입력을 보관했습니다.
- 이미 성공한 설치 로그 2,000줄과 과거 v1·v2의 전체 대화가 있습니다.
- 다음 모델 호출의 문맥을 줄여야 합니다.

다음 실행에 바로 전달할 정보와, 외부에 보관하고 필요할 때 다시 읽을 정보를 나눕니다. 항목 수보다 각 정보가 다음 판단에 필요한 이유를 설명합니다. 단순 요약이 잘못된 완료 판정을 만들지 않도록 무엇을 그대로 남길까요?

<details><summary>해설 · 가능한 설계와 채점 기준</summary>

예를 들어 현재 요구·완료 조건, v3 식별자와 변경 파일, 재현 입력·테스트 명령, 실제 실패 결과를 바로 전달합니다. 설치 전체 로그와 과거 대화는 경로·검색 단서를 남겨 외부 보관합니다. 다음 행동에 필요한 코드 조각을 바로 전달하고 일부 기록을 필요시 조회하는 구성도 가능합니다.

실패를 “대체로 통과”로 요약하지 않고 `공백 입력 → 생성 1회, 기대 0회`라는 근거를 유지합니다. 검증한 버전과 미완료 항목도 남깁니다. 어떤 정보를 줄였는지와 왜 다시 찾을 수 있는지를 설명하는 것이 핵심입니다.

**채점:** 다음 결정에 필요한 근거 선택 1점; 외부 보관 자료의 재조회 경로 1점; 실패·버전·완료 기준 왜곡 방지 1점. 해설과 같은 항목 구성을 고를 필요는 없습니다.

**대표 오답:** “토큰 절약을 위해 모든 도구 결과를 삭제한다.” 실패 입력과 관찰 결과까지 없어지면 다음 Agent가 이미 확인한 오류를 반복하거나 완료를 추측할 수 있습니다.

근거: [Anthropic Context Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents).

</details>
</section>
<section class="slide" id="q7">

## 7. 완료된 검토를 지금 적용해도 될까요?

**코드 일부 완성.** 수업의 정규화된 `state`를 받습니다. submitted·working은 `pending`, completed가 아닌 나머지는 `held`입니다. completed이고 현재 요청 ID·버전이 일치하며 `passed is True`일 때만 `accepted`입니다. 현재 요청 ID는 공백 아닌 문자열, 버전은 1 이상의 정수여야 합니다.

```python
def accept_review(state, artifact, request_id, version):
    # 여기에 작성
    raise NotImplementedError

cases = [
    ("working", None, "r1", 2, "pending"),
    ("completed", {"request_id": "r1", "version": 2, "passed": True}, "r1", 2, "accepted"),
    ("completed", {"request_id": "r1", "version": 1, "passed": True}, "r1", 2, "held"),
    ("completed", {"request_id": "r2", "version": 2, "passed": True}, "r1", 2, "held"),
    ("completed", None, "r1", 2, "held"),
    ("completed", {"request_id": "r1", "version": True, "passed": True}, "r1", 1, "held"),
    ("completed", {"request_id": "r1", "version": 2, "passed": "true"}, "r1", 2, "held"),
]
for state, artifact, request_id, version, expected in cases:
    assert accept_review(state, artifact, request_id, version) == expected
```

입력이 공백 ID, 현재 버전이 잘못된 타입, 상태가 failed인 반례도 추가합니다.

**요청 이후 초안이 바뀐 상황도 판단합니다.** v2를 검토에 맡긴 뒤 사용자가 초안을 수정하여 현재 후보는 v3입니다. 아래 두 호출의 출력과, 현재 후보를 승인할 때 사용할 호출을 설명합니다.

```python
sent = {"request_id": "r1", "version": 2}
current = {"request_id": "r1", "version": 3}
review = {"request_id": "r1", "version": 2, "passed": True}
print(accept_review("completed", review, sent["request_id"], sent["version"]))
print(accept_review("completed", review, current["request_id"], current["version"]))
```

현재 버전을 확인한 직후 실제 승인 상태를 저장하기 전에 후보가 다시 바뀔 수도 있다면, 어떤 조건으로 갱신을 허용할까요?


<details><summary>해설 · 구현 예와 채점 기준</summary>

```python
def accept_review(state, artifact, request_id, version):
    if state in {"submitted", "working"}:
        return "pending"
    if state != "completed" or not isinstance(artifact, dict):
        return "held"
    if not isinstance(request_id, str) or not request_id.strip():
        return "held"
    if type(version) is not int or version < 1:
        return "held"
    if type(artifact.get("version")) is not int:
        return "held"
    matches = (
        artifact.get("request_id") == request_id
        and artifact.get("version") == version
        and artifact.get("passed") is True
    )
    return "accepted" if matches else "held"
```

두 호출은 각각 accepted와 held입니다. 첫 호출은 v2의 검토가 v2에 맞는다는 사실만 확인하므로 현재 v3의 승인 근거가 되지 않습니다. 채택을 결정하는 호출에는 현재 후보의 요청 ID·버전을 전달해야 합니다. 전송 당시 값은 응답을 어떤 요청과 연결할지 추적하는 데 쓰되 현재 후보를 대신하지 않습니다.

검사와 결과 적용 사이에도 후보가 바뀔 수 있다면, 적용 시점에 기대 버전이 여전히 같은지 원자적으로 비교하고 일치할 때만 승인 상태를 갱신합니다. 그렇지 않으면 이전 검토를 현재 초안에 붙일 수 있습니다. 후보를 검토 중 수정하지 못하게 고정하는 설계도 타당하며, 그 제약을 명시해야 합니다.

유효성 검사를 보조 함수로 나눠도 타당합니다. 입력 형식에 관한 보조 함정으로, Python에서는 `True == 1`이므로 값 비교만 하면 불리언 버전을 받아들일 수 있습니다.

**채점:** 상태·요청·버전·통과 조건을 구현 1점; 전송 당시 값과 현재 후보 값으로 호출한 결과 및 의미 구별 1점; 검사 후 적용 전 변경까지 고려한 승인 관문 설계 1점.

**대표 오답:** `if artifact["passed"]`는 문자열 `"true"`도 참으로 처리합니다. Task ID가 있다는 사실만으로 현재 요청의 산출물이라고 판단하는 것도 부족합니다.

근거: [A2A Task 생애주기](https://a2a-protocol.org/latest/topics/life-of-a-task/). 수용 함수의 ID·버전 조건은 우리 업무 계약이며 A2A 표준이 대신 정의하지 않습니다.

</details>
</section>
<section class="slide" id="q8">

## 8. Card를 발견했으면 곧바로 아무 Agent에나 연결할 수 있을까요?

**설계 판단.** 6D가 두 Card를 발견했습니다. A는 정책 근거를 검토하며 JSON-RPC, B는 불명확한 표현을 검토하며 HTTP+JSON을 제공합니다. 사용자는 “정책 검증 없이 이 문장의 표현만 검토”를 요청했습니다.

담당자, 선택 근거, 실제 요청을 만드는 구성요소를 설명합니다. 이어 새로운 C의 Card가 `text/plain`만 알려 주었는데 서버는 별도 JSON 필드를 요구한다면 무엇이 더 필요할까요? 수업의 `skill_id`와 A2A Message의 관계도 설명합니다.

<details><summary>해설 · 선택과 계약의 구분</summary>

B를 선택합니다. 기능 설명이 요청과 맞기 때문이며 REST이기 때문은 아닙니다. 모델이 도구 인자로 선택을 표현하고, 도구·SDK가 Card의 지원 바인딩에 맞춰 Message를 전송합니다.

C와는 업무 입력의 의미와 구조를 추가로 합의해야 합니다. 미디어 형식만으로 필수 업무 필드가 모두 정해지는 것은 아닙니다. 문서·예제나 합의한 schema를 확보하거나, 상대가 이해하는 자연어 요청을 사용하도록 계약을 바꿀 수 있습니다. 수업의 `skill_id`는 Card 기능을 검사하는 도구 인자이지 SendMessage의 표준 라우팅 필드가 아닙니다.

**채점:** 기능으로 B 선택 1점; 모델 선택과 SDK 통신 구별 1점; Card와 업무 입력 계약·skill_id 범위 설명 1점.

**대표 오답:** “HTTP+JSON이면 일반 API이므로 A2A가 아니다.” 바인딩이 달라도 A2A의 Message·Task 의미를 따를 수 있습니다. “Card에 skills가 있으므로 MCP inputSchema도 있다” 역시 다른 계약을 혼동한 답입니다.

근거: [A2A AgentSkill](https://a2a-protocol.org/latest/specification/#445-agentskill), [발견 전략](https://a2a-protocol.org/latest/topics/agent-discovery/), [바인딩 대응](https://a2a-protocol.org/latest/specification/#53-method-mapping-reference).

</details>
</section>
<section class="slide" id="q9">

## 9. 함수·MCP·A2A 중 무엇을 고를까요?

**설계 판단.** 아래 두 요구에 각각 연결 방식을 제안하고, 다른 선택이 더 나아지는 조건을 한 가지씩 적습니다.

1. 같은 Python 앱 안의 담당 팀 조회 함수를 한 곳에서만 사용합니다. 다른 Host에 공개할 계획이 없습니다.
2. 별도 팀이 운영하는 검토 시스템에 초안을 맡깁니다. 추가 질문과 작업 상태, 검토서를 서로 다른 클라이언트가 같은 형식으로 다뤄야 합니다.

두 번째 요구가 “여러 Host가 동일한 조회 도구를 찾고 실행한다”로 바뀌면 제안은 어떻게 달라질까요?

<details><summary>해설 · 조건에 따른 대안과 채점 기준</summary>

첫 요구는 직접 함수 호출로 충분할 수 있습니다. 여러 Host가 같은 기능 설명·입력 형식으로 발견하고 호출해야 한다면 MCP가 유리해질 수 있습니다. 두 번째 요구는 작업·메시지·산출물 계약을 공유하려는 A2A의 목적과 맞습니다. 다만 이미 합의한 HTTP 업무 API가 요구를 충족하고 연결 상대가 제한되어 있다면 그것을 유지하는 선택도 타당합니다.

요구가 공통 조회 도구 발견·실행으로 바뀌면 MCP를 우선 검토합니다. 모델 존재 여부, 원격 여부, 오래 걸리는지 하나만으로 결정하지 않습니다. 새 프로토콜 도입에 따른 주소·인증·오류 처리와 운영 비용도 비교합니다.

**채점:** 요구와 연결 방식의 이유 대응 1점; 타당한 대안의 조건 제시 1점; 요구 변경에 따른 재판단과 비용 설명 1점. 제품 이름 하나만 정답으로 채점하지 않습니다.

**대표 오답:** “Agent가 있으니 항상 A2A.” MCP 도구 뒤에 모델이 있을 수도 있고, Agent 내부에서 일반 함수를 호출할 수도 있습니다.

근거: [A2A와 MCP](https://a2a-protocol.org/latest/topics/a2a-and-mcp/), [MCP Tools](https://modelcontextprotocol.io/specification/2026-07-28/server/tools).

</details>
</section>
<section class="slide" id="q10">

## 10. 두 검토자가 동시에 통과했는데 최종 승인을 보류해야 합니다

**설계 판단.** 기능 검토자는 v4를 통과시켰습니다. 문서 검토자는 v3를 통과시켰습니다. 둘의 응답은 모두 completed이며 현재 후보는 v4입니다. 한 검토가 느리다고 먼저 온 결과만으로 승인하라는 요구도 있습니다.

이 업무는 같은 후보 버전에 대한 두 검토가 모두 필수입니다. 무엇을 병렬로 실행하고 어디에서 기다릴지 설계합니다. 결과를 저장할 필드와 승인 조건을 제안하고, 재검토가 필요한 범위를 설명합니다. 하나의 `passed` 필드에 두 노드가 쓰는 방법은 어떤 문제가 있나요?

<details><summary>해설 · 합류 조건과 채점 기준</summary>

동일한 v4 후보를 고정하여 기능·문서 검토를 병렬로 실행하고, 최종 승인 노드에서 두 결과가 모두 도착했는지 확인합니다. 예를 들어 `functional_review`와 `document_review`에 요청 ID·버전·상태·판정을 별도로 저장합니다. 현재 결과에서는 v3 문서 검토를 승인 근거로 쓰지 않으며 v4 문서 검토가 필요합니다.

기능 검토 결과를 재사용하려면 v4 산출물이 실제로 변경되지 않았고 검토 근거도 여전히 유효해야 합니다. 변경이 있었다면 영향 범위에 맞춰 다시 검토합니다. 같은 기본 교체 필드에 병렬 갱신을 보내면 LangGraph에서 충돌할 수 있습니다. reducer로 결과를 모으더라도 버전과 필수 검토 충족 여부는 별도로 판단해야 합니다. 역할별 키를 쓰거나 역할 ID를 키로 모으는 명시적 병합도 타당합니다.

**채점:** 병렬 실행과 필수 합류 구별 1점; 역할·요청·버전별 결과 계약 1점; 재검토 범위와 병합/승인 차이 설명 1점.

**대표 오답:** “모두 completed이므로 승인.” 완료 상태는 대상 버전 일치나 업무 통과를 보장하지 않습니다. “먼저 통과한 한 명만 사용”은 두 검토 필수라는 요구를 바꾼 것입니다.

근거: [LangGraph State와 Reducers](https://docs.langchain.com/oss/python/langgraph/graph-api#reducers), [A2A Task 생애주기](https://a2a-protocol.org/latest/topics/life-of-a-task/).

</details>
</section>
<section class="slide">

## 다시 풀 때 확인할 것

낮은 점수의 문항 하나를 골라 대표 오답이 실제로 실패하는 입력을 만듭니다. 해설을 외우기보다 왜 그 입력에서 판단이 달라지는지 자신의 실행 기록이나 설계 조건으로 설명합니다.

[통합·정리로 돌아가기](./wrap) · [실습 전체 흐름](./build)

</section>
</div></div>
