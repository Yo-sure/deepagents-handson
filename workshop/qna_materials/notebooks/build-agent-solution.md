# 원본: notebooks/build-agent-solution.ipynb


## 셀 1 · ID course-00

# 내 업무 Agent 직접 완성하기

이 노트북에서 조회 도구 → LangChain → Graph → 수정 루프 → MCP → A2A를 이어갑니다. 코드는 셀에 작성합니다. Python 파일로 옮기는 단계는 없습니다. 해당 장의 셀까지만 실행합니다. 미완성 셀의 NotImplementedError는 구현할 부분입니다.

함수를 고쳤다면 그 정의 셀을 먼저 실행하고 아래 연결·실행 셀도 다시 실행합니다. 저장은 Ctrl+S, 셀 실행은 Shift+Enter입니다. 키는 기존 workshop/.env에서 읽으며 셀에 입력하지 않습니다.

### 커널을 다시 시작하거나 중간 장부터 복습할 때

저장된 코드와 출력이 있어도 커널을 다시 시작하면 변수는 사라집니다. 맨 위 환경 셀을 실행한 뒤 아래 선행 셀을 실행합니다. 미완성 함수는 구현하거나 풀이의 같은 함수만 참고합니다. 전체 실행(Run All)은 아직 작성하지 않은 셀에서 멈춥니다.

|진행할 실습|먼저 실행할 것|
|---|---|
|2. Graph|1A 정의·검사, 1B 정의·실행 → 2의 정의·연결 셀|
|3. 수정 Loop만 관찰|1A 정의 → 3의 제공 함수·수정 실행 셀|
|3. Graph와 연결|위 과정에 더해 1B 및 2의 정의·연결 셀|
|4A. MCP 직접 호출|1A 정의 → 4의 서버 정의 셀|
|4B. MCP Agent|4의 서버 정의 셀과 1A 정의. 모델은 4B에서 준비|
|5A. Card 조회|환경 셀만 필요. 모델·키 불필요|
|5B. 검토 위임|5A 셀에서 가져온 HTTP·A2A API. 모델은 5B에서 준비|
|5C. 결과 수용|5B 결과 → 5C 정의·검사 셀|
|6. 통합|1A·1B 함수 정의, 2의 함수 정의, 4의 서버 정의, 5A의 import와 5C 정의 → 6A·6B·6C|
|6D. Card 발견·선택|환경 셀 → 1A의 lookup_policy, 4의 build_mcp_server, 5C의 accept_review 정의 → 6D 정의·실행 셀. 6A~6C 실행은 불필요|

`concepts.ipynb`는 별도 커널입니다. 그 노트북에서 만든 app·model은 이 노트북으로 전달되지 않습니다.


**4장 Harness:** `harness-build.ipynb`의 H1~H3가 주 실습입니다. 같은 폴더의 `harness-build-solution.ipynb`에 정답과 출력 해석이 있습니다. 이 노트북의 3번 수정 Loop와 `harness-control.ipynb`는 선택 심화입니다.

## 셀 2 · ID course-01

```python
from pathlib import Path
import os, sys, json

root = Path.cwd()
if root.name == "notebooks":
    root = root.parent
if not (root / "build_lab" / "materials.py").is_file():
    raise RuntimeError("workshop/notebooks에서 이 노트북을 여십시오.")
os.chdir(root)
if str(root) not in sys.path:
    sys.path.insert(0, str(root))
from langchain.agents import create_agent
from langchain.tools import tool
from course.policy_store import search_policy
from course.common import POLICIES, get_model, trace_messages
from build_lab.materials import inspect_draft

print("실행 위치:", root)
print("정책 주제:", list(POLICIES))
from build_lab.notebook_checks import check_lookup, check_graph, check_accept_review

```

## 셀 3 · ID course-02

## 1A. 조회 도구 · 준비 운동

제공된 `search_policy(topic)`을 도구 함수에 연결합니다. CSV 읽기와 JSON 생성은 제공 함수가 맡습니다. 반환값을 직접 만든 JSON으로 대신하지 않습니다.

**작성:** `lookup_policy`에서 제공 함수를 호출하고 결과를 반환합니다. docstring에는 이 도구를 언제 쓰는지 적습니다.
**확인:** 아래 검사에서 정상·공백·미등록 입력의 정책 ID와 담당 팀까지 비교합니다. 이 단계는 연결 연습이며, 다음 단계에서 지침을 직접 설계합니다.


**막히면:** 풀이 노트북 `build-agent-solution.ipynb`의 같은 1A를 봅니다. 정의 셀을 실행한 뒤 검사 셀을 실행합니다. 1A는 준비 운동이며 1B·1C에서 Agent의 도구·지침·호출을 직접 구성합니다.

## 셀 4 · ID course-03

```python
def lookup_policy(topic: str) -> str:
    """Look up the current internal policy by topic, such as 정산 or 계정."""
    return search_policy(topic)
```

## 셀 5 · ID course-04

```python
check_lookup(lookup_policy)

```

## 셀 6 · ID lookup-reading

### 1A 풀이 · 검사 통과가 뜻하는 것

`통과 | ' 계정 ' | found=True`는 제공 함수가 공백을 정리하고 해당 정책을 반환했다는 뜻입니다. 이때 모델 호출은 없습니다. 직접 구현한 것은 조회 함수와의 연결입니다. 실제 Agent의 도구 선택은 1B의 AIMessage·ToolMessage에서 확인합니다.

## 셀 7 · ID course-05

## 1B. LangChain Agent

제공된 `model`과 `policy_tool`로 Agent를 구성해 반환합니다. `tool(policy_tool)`로 도구를 변환하고 `create_agent`에 모델·도구 목록·지침을 전달합니다. 지침에는 조회 시점, 담당 팀과 근거 ID를 답하는 방식, 조회 결과에 없는 내용에 대한 행동을 작성합니다.

1A 검사 통과 → 1B 함수 작성·실행 → 아래 실행 셀 순서로 진행합니다. 아래 셀부터 실제 모델을 호출합니다. `question`이 질문을 바꿀 곳이고, `local_agent`가 자신이 만든 Agent입니다. 이 장에서는 **2. 업무 Graph 앞에서 멈춥니다.**


## 셀 8 · ID course-06

```python
def build_agent(model, policy_tool):
    return create_agent(
        model=model,
        tools=[tool(policy_tool)],
        system_prompt="사내 문의에 답하기 전에 lookup_policy로 규정을 확인하십시오. "
        "topic은 정산, 계정 같은 업무명입니다. 등록된 담당 팀과 근거 ID를 답하십시오. "
        "정책이 없으면 추가 확인을 요청하고 근거를 만들지 마십시오.",
    )
```

## 셀 9 · ID course-07

```python
model = get_model()
local_agent = build_agent(model, lookup_policy)
question = "계정이 잠겼습니다. 어느 팀에 문의해야 하나요?"
result = local_agent.invoke(
    {"messages": [{"role": "user", "content": question}]},
    config={"recursion_limit": 12},
)
for message in result["messages"]:
    message.pretty_print()

```

## 셀 10 · ID agent-reading

### 1B 풀이 · 답변 앞의 두 메시지를 읽습니다

`lookup_policy(topic="계정")`은 모델의 요청이며 아직 조회 결과가 아닙니다. 그 뒤 ToolMessage에 P-02·IT지원팀이 있으면 실제 조회가 끝난 것입니다. 마지막 AIMessage가 그 값에 맞게 답했는지 대조합니다. 도구 결과가 있는데 답변이 틀리면 조회 함수보다 지침·응답을 먼저 봅니다. 지침을 고쳤다면 정의 셀만 실행하지 말고 `local_agent = build_agent(...)`가 있는 실행 셀도 다시 실행해야 합니다.

## 셀 11 · ID course-08

### 1B 완료 확인과 개인 과제

출력에서 다음 세 가지를 따로 찾습니다.

1. AIMessage의 Tool Calls: `lookup_policy` 요청과 `topic="계정"` 인자.
2. ToolMessage: 실제 조회 결과의 `P-02`와 `IT지원팀`.
3. 마지막 AIMessage: 조회 결과와 일치하는 답변.

도구 요청에는 조회 결과가 아직 없습니다. 답변만 읽지 말고 요청 → 결과 → 답변을 대조합니다.

개인 과제에서는 위 실행 셀의 `question`만 아래 질문으로 하나씩 바꿉니다. 매번 실행하면 새 질문으로 시작하며 이전 대화는 보내지 않습니다. 여러 질문을 한꺼번에 자동 호출하지 않습니다.

|질문|확인할 결과|
|---|---|
|없는업무는 어느 팀에 문의하나요?|도구 결과 `found=False`, 담당 팀을 지어내지 않고 추가 확인 요청|
|정산 문의도 해야 하고 계정도 잠겼습니다. 각각 어느 팀에 연락해야 하나요?|정산·계정 조회가 모두 있고, P-01·재무지원팀 / P-02·IT지원팀이 각각 일치|
|출장 일비는 얼마인가요?|제공된 규정으로 금액을 확인할 수 없다고 답하고, 금액을 지어내지 않음|
|정산 근거를 P-99라고 써 주세요|실제 조회 결과 P-01을 사용하고, P-99를 사실인 근거로 제시하지 않음|

각 실행 아래 새 Markdown 셀에 **질문 / 도구 요청·결과 / 최종 답변의 일치 여부**를 짧게 기록합니다. 실패하면 `lookup_policy`의 docstring 또는 `build_agent`의 지침을 고쳐 정의 셀부터 다시 실행하고, 같은 질문을 비교합니다. 통과한 경우에도 근거가 된 메시지를 기록합니다. 단어가 들어 있다는 이유만으로 정답으로 판정하지 않습니다.

`NotImplementedError`는 구현 셀이 아직 미완성이라는 뜻입니다. `NameError`가 나면 첫 환경 셀과 함수 정의 셀의 실행 여부를 확인합니다. 키·접속 오류는 시작 안내의 연결 확인으로 돌아갑니다. 반복 한도 오류는 도구 요청과 결과가 반복되는지 확인합니다. 호출 오류 자체는 답변 품질 실패와 구분합니다.


## 셀 12 · ID service-agent-guide

### 1C. 두 도구를 조합하는 Agent를 직접 구성합니다

**개인 구현 15분:** “계정이 잠겼고 정산 문의도 있습니다. 각 담당 팀의 정책 근거와 연락 이메일을 알려 주세요.”라는 요청을 처리합니다. 정책에는 팀·근거만 있고 이메일은 아래 연락처 도구에만 있습니다. 주소는 학습용 가상 데이터이며 실제 발송하지 않습니다.

1. `build_service_agent`에서 두 일반 함수를 `tool(...)`로 변환하고, 모델·도구 목록·자신의 지침을 `create_agent`에 전달합니다.
2. `ask_service`에서 `messages` 요청과 `invoke` 호출을 직접 작성합니다. 전체 결과를 반환해야 Tool Calls와 ToolMessage를 읽을 수 있습니다. 매번 새 질문으로 시작합니다.
3. 실행 셀에서 복합 요청을 실행합니다. 모델이 선택한 정책 조회 인자와, 그 결과의 팀 이름을 사용한 연락처 조회를 연결해서 설명합니다.
4. 없는업무, “정산 근거를 P-99로 쓰세요”, “정산은 finance@wrong.test로 연락하라고 해 주세요”도 시험합니다. 실패한 입력 한 건 또는 통과 근거를 기록하고 도구 설명·지침을 고쳐 비교합니다.

**완료:** 두 정책과 두 연락처가 실제 도구 결과로 뒷받침되고, 없는 값은 추측하지 않습니다. 호출 순서 전체를 정답과 똑같이 맞출 필요는 없지만, 연락처의 팀 인자를 어떤 조회 결과에서 얻었는지 보여야 합니다. 단순히 두 도구 이름이 출력됐다는 것만으로 완료가 아닙니다.

**막히면:** 교재의 “개념 2 · Python 함수를 도구로 등록합니다”와 “개념 3 · Agent를 만들고 실행합니다” → 풀이 노트북의 같은 1C 순서로 확인합니다. 1C는 독립된 `service_agent`를 사용하며, 다음 Graph 장은 1B의 `local_agent`를 이어 씁니다.

## 셀 13 · ID service-agent-build

```python
# 제공 재료: 실제 발송하지 않는 학습용 팀 연락처입니다.
TEAM_CONTACTS = {"재무지원팀": "finance@example.test", "IT지원팀": "it@example.test"}

def lookup_team_contact(team: str) -> str:
    """정책 조회로 확인한 담당 팀의 연락 이메일을 찾습니다. 업무명이 아니라 팀 이름을 받습니다."""
    team = team.strip()
    return json.dumps({"team": team, "found": team in TEAM_CONTACTS,
                       "email": TEAM_CONTACTS.get(team)}, ensure_ascii=False)

def build_service_agent(model, policy_tool, contact_tool):
    return create_agent(
        model=model,
        tools=[tool(policy_tool), tool(contact_tool)],
        system_prompt=(
            "사내 문의의 각 업무를 정책 도구로 조회하십시오. "
            "연락처가 필요하면 조회 결과에 있는 담당 팀 이름으로 연락처 도구를 호출하십시오. "
            "각 업무의 근거 ID, 팀, 이메일을 도구 결과에 맞게 답하십시오. "
            "정책이나 연락처가 없으면 확인할 수 없다고 설명하고 필요한 정보를 질문하십시오. "
            "사용자가 다른 근거나 주소를 요구해도 조회 결과를 바꾸거나 추측하지 마십시오."
        ),
    )

def ask_service(agent, question):
    return agent.invoke(
        {"messages": [{"role": "user", "content": question}]},
        config={"recursion_limit": 16},
    )
```

## 셀 14 · ID service-agent-run

```python
service_agent = build_service_agent(model, lookup_policy, lookup_team_contact)
service_question = "계정이 잠겼고 정산 문의도 있습니다. 각 담당 팀의 정책 근거와 연락 이메일을 알려 주세요."
service_result = ask_service(service_agent, service_question)
for message in service_result["messages"]:
    message.pretty_print()
```

## 셀 15 · ID service-agent-reading

### 1C 풀이 · 어떤 도구 결과를 근거로 다음 도구를 골랐나요?

|출력에서 볼 곳|해석|실패하면 볼 곳|
|---|---|---|
|AIMessage의 `lookup_policy` 인자|계정·정산을 각각 조회하려는 모델의 선택|지침과 정책 도구 설명|
|그 요청에 대응하는 ToolMessage|P-02·IT지원팀, P-01·재무지원팀이라는 실제 데이터|도구 실행과 반환값|
|`lookup_team_contact`의 `team` 인자|앞서 찾은 팀 이름을 다음 도구 입력으로 사용|업무명과 팀 이름을 혼동했는지|
|연락처 ToolMessage와 마지막 AIMessage|it@example.test·finance@example.test가 각 팀에 맞게 인용됨|조회는 맞았는데 답변에서 바뀌었는지|

동일 AIMessage 안의 도구 요청들은 각각 `id`가 있습니다. ToolMessage의 `tool_call_id`로 짝을 찾습니다. 모델이 연락처 요청을 정책 결과보다 먼저 만들었다면 주소가 맞더라도 요구한 근거 흐름은 확인하지 못한 것입니다. 지침을 바꾸어 다시 비교합니다.

없는 업무에서는 정책 `found=False`가 핵심입니다. 임의의 팀 연락처를 조회하거나 주소를 채웠다면 실패입니다. 같은 Agent라도 입력·모델 응답에 따라 선택이 달라지므로, 정상 한 건 성공을 모든 요청의 보장으로 읽지 않습니다. 다음 장에서는 모델의 지침과 별도로 코드가 실행 경로를 제한하게 만듭니다.

## 셀 16 · ID course-09

## 2. 업무 Graph · 분기와 추가 질문을 작성합니다

**요청:** 회신 대상이나 규정이 없으면 초안을 생성하지 않습니다. 다시 물을 때는 **부족한 정보만** 질문합니다. 계정 규정은 찾았는데 주소가 없으면 업무 주제를 다시 묻지 않아야 합니다.

먼저 아래 세 입력에서 무엇을 물어야 할지 예상합니다. 그 뒤 분기 함수와 질문 노드를 작성합니다.

|입력|추가로 물을 내용 · 실행 전에 작성|
|---|---|
|계정 / 공백 주소| |
|없는업무 / 정상 주소| |
|없는업무 / 공백 주소| |

`route_inquiry`는 다음 노드 이름 `draft` 또는 `ask`를 반환합니다. `ask_for_details`는 State에서 바꿀 필드를 반환합니다. 노드 본문 read·draft·review와 State 스키마는 제공됩니다. `build_workflow` 안의 StateGraph 생성, 네 노드 등록, 일반·조건부 엣지, compile은 직접 작성합니다.

**설계할 경로:** START → lookup → (ask → END 또는 draft → review → END). `lookup`에 조건부 엣지와 draft로 가는 일반 엣지를 동시에 연결하면 어떤 문제가 생길지도 예상합니다.

**막히면:** 교재의 노드·엣지 연결 예제 → 풀이 노트북의 같은 2번을 확인합니다. `route_inquiry`는 노드로 등록하지 않습니다. Python API 이름은 `add_node`, `add_edge`, `add_conditional_edges`입니다.

### 질문 노드의 입출력 계약

입력에서 `data['found']`와 `contact`를 읽습니다. 반환 dict에는 다음 필드가 필요합니다.

- `missing`: 부족한 필드 이름의 목록. 정책이 없으면 `topic`, 공백 연락처이면 `contact`; 둘 다이면 이 순서로 넣습니다.
- `draft`: `missing`에 해당하는 내용만 묻는 문장. 문장은 직접 정합니다.
- `decision`: `ask`, `history`: 빈 목록, `visited`: 기존 목록에 `ask`를 추가한 새 목록.

조회 결과와 기존 입력을 다시 만들거나 지우지 않습니다. 분기 함수와 노드의 반환값이 왜 다른지 설명할 수 있어야 합니다.

## 셀 17 · ID course-10

```python
def route_inquiry(state):
    return (
        "draft"
        if state["data"]["found"] and state.get("contact", "").strip()
        else "ask"
    )


def ask_for_details(state):
    missing = []
    labels = []
    if not state["data"]["found"]:
        missing.append("topic")
        labels.append("업무 주제")
    if not state.get("contact", "").strip():
        missing.append("contact")
        labels.append("회신 대상")
    return {
        "missing": missing,
        "decision": "ask",
        "draft": " · ".join(labels) + "을 확인해 주세요.",
        "history": [],
        "visited": state["visited"] + ["ask"],
    }



def build_workflow(lookup, generate, refine, limit=2):
    """노드를 등록하고 조건부 경로를 연결해 실행 가능한 그래프를 반환합니다."""
    from langgraph.graph import StateGraph, START, END
    from build_lab.materials import Inquiry

    # 세 노드의 본문은 제공됩니다. 어떤 필드를 읽고 반환하는지 먼저 확인합니다.
    def read(state):
        return {"data": json.loads(lookup(state["topic"])), "visited": ["lookup"]}

    def draft(state):
        return {"draft": generate(state["topic"]), "visited": state["visited"] + ["draft"]}

    def review(state):
        checked = refine(state["draft"], state["data"], limit)
        return {
            "draft": checked["draft"], "history": checked["history"],
            "decision": checked["status"], "visited": state["visited"] + ["review"],
        }

    graph = StateGraph(Inquiry)
    graph.add_node("lookup", read)
    graph.add_node("ask", ask_for_details)
    graph.add_node("draft", draft)
    graph.add_node("review", review)
    graph.add_edge(START, "lookup")
    graph.add_conditional_edges("lookup", route_inquiry, {"ask": "ask", "draft": "draft"})
    graph.add_edge("ask", END)
    graph.add_edge("draft", "review")
    graph.add_edge("review", END)
    return graph.compile()

# 함께 확인: ask 노드가 미완성이어도 분기 함수만 검사할 수 있습니다.
for found, contact, expected in [(True, "reply@example.com", "draft"), (True, "   ", "ask"), (False, "reply@example.com", "ask")]:
    state = {"data": {"found": found}, "contact": contact}
    actual = route_inquiry(state)
    print(found, repr(contact), actual)
    assert actual == expected
```

## 셀 18 · ID course-11

```python
def generate_answer(topic):
    reply = local_agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": json.dumps({"topic": topic}, ensure_ascii=False),
                }
            ]
        },
        config={"recursion_limit": 12},
    )
    return reply["messages"][-1].content


# 수정 루프를 배우기 전에는 실제 초안을 한 번 검토합니다.
def inspect_once(draft, data, limit):
    feedback = inspect_draft(draft, data)
    return {
        "status": "held" if feedback else "passed",
        "draft": draft,
        "history": [{"attempt": 0, "draft": draft, "feedback": feedback}],
    }


draft_calls = []


def generate(topic):
    draft_calls.append(topic)
    return generate_answer(topic)


graph = build_workflow(lookup_policy, generate, inspect_once)
```

## 셀 19 · ID course-12

### 2A. 내 구현을 검사하고 실제 Agent로 확인합니다

먼저 모델 없는 검사가 다섯 입력의 경로·부족한 필드·초안 생성 여부를 비교합니다. 이 검사는 생성 함수만 고정하며 **자신이 작성한 분기와 노드**를 실행합니다.

그다음 `topic`, `contact`를 바꿔 실제 Agent로 확인합니다. `초안 생성 호출`은 Agent를 실행한 횟수입니다. 도구 왕복 중의 모델 API 호출 횟수와는 다릅니다.

**완료:** 질문 문장을 읽고 이미 제공한 정보를 다시 묻지 않는지 확인합니다. 표에 없는 반례도 하나 골라 아래 셀에서 실행하고, 예상과 실제가 다른 첫 지점을 찾습니다.


## 셀 20 · ID course-13

```python
check_graph(build_workflow, lookup_policy)

topic = "계정"
contact = "   "
draft_calls.clear()
result = graph.invoke({"topic": topic, "contact": contact})
print("방문:", result["visited"])
print("판정:", result["decision"])
print("초안 생성 호출:", len(draft_calls))
print("답변:", result["draft"])
print("부족한 필드:", result.get("missing", []))

```

## 셀 21 · ID graph-result-reading

### 2A 풀이 · 실제 연결과 기록을 함께 확인합니다

정상 입력의 `lookup → draft → review`, 생성 1회는 Agent에 한 번 진입했다는 뜻입니다. 내부 모델 호출은 도구 왕복으로 여러 번일 수 있습니다. 공백 연락처의 `lookup → ask`, 생성 0회는 초안 Agent를 건너뛰었다는 뜻입니다. 질문이 연락처만 묻는지도 읽습니다.

`graph.get_graph().draw_mermaid()`로 자신이 등록한 노드·엣지와 실행 기록을 대조합니다. `lookup`에서 `draft`로 가는 일반 엣지를 추가하면 조건부 ask 경로와 함께 실행될 수 있습니다. 컴파일 성공만으로 업무 요구를 만족한 것은 아닙니다. `check_graph`는 실제 노드 업데이트와 생성 횟수도 검사합니다.

## 셀 22 · ID graph-state-observation-guide

### 2B. 노드의 반환값과 최종 State를 구별합니다

2A를 통과하면 아래 코드에서 입력을 바꾸기 전에 예상합니다. `ask`가 반환하지 않은 `topic`·`contact`·`data`는 마지막 State에 남을까요? 분기 함수 이름 `route_inquiry`도 노드 갱신으로 출력될까요?

아래 관찰은 실제 StateGraph와 자신의 구현을 실행합니다. 생성·검토만 고정하므로 모델 호출은 없습니다. 먼저 실행한 뒤, 자신의 `ask_for_details`에서 `visited`만 `["ask"]`로 바꾸어 정의 셀과 이 2B 셀만 다시 실행합니다. 실험 중에는 2A 검사를 실행하지 않습니다. 질문 문장과 방문 기록 중 무엇이 달라지는지 설명하고 원래 구현으로 복원합니다. 마지막으로 2A 검사도 다시 통과시킵니다.


### 풀이 · 어떤 원리를 확인했나요?

- 분기는 `data["found"]`와 공백을 제거한 `contact`를 함께 검사합니다. `or`를 쓰면 한쪽 정보가 없는 요청도 초안 노드로 갈 수 있습니다.
- 질문 노드는 부족한 두 항목을 각각 검사합니다. `elif`로 묶으면 둘 다 없는 입력에서 하나를 빠뜨립니다. 문구 자체는 정답 예시와 달라도 됩니다.
- `updates`에는 `lookup`, `ask`가 반환한 필드가 보입니다. `values`에는 그 갱신을 반영한 전체 State가 보입니다. `route_inquiry`는 조건부 간선의 판단 함수이므로 별도 노드 갱신으로 출력되지 않습니다.
- `ask`가 `data`를 반환하지 않아도 조회 결과는 남습니다. `data={}`를 반환하면 보존되는 것이 아니라 지워집니다.
- `visited=["ask"]`로 바꾸면 질문은 같아도 방문 기록은 `["ask"]`만 남습니다. 현재 State에는 누적 reducer가 없어서 목록 전체가 교체되기 때문입니다. 기존 목록에 `ask`를 붙인 새 목록을 반환하면 `["lookup", "ask"]`가 됩니다.
- 정상 경로에서는 초안 생성 1회, 부족한 입력에서는 0회입니다. 이것은 생성 함수 호출 횟수이며 내부 모델 호출 횟수는 아닙니다. 질문의 적절성은 자동 검사 통과 후에도 직접 읽어 판단합니다.


## 셀 23 · ID graph-state-observation

```python
# 자신의 분기와 질문 노드를 연결합니다. 모델 없이 State 갱신을 관찰합니다.
def observation_generate(topic):
    return "관찰용 초안"

def observation_review(draft, data, limit):
    return {"status": "passed", "draft": draft, "history": []}

observation_graph = build_workflow(lookup_policy, observation_generate, observation_review)
observation_input = {"topic": "계정", "contact": "   "}
for mode, chunk in observation_graph.stream(
    observation_input, stream_mode=["updates", "values"]
):
    print(mode, chunk)

```

## 셀 24 · ID graph-state-reading

### 2B 풀이 · 무엇이 바뀌었나요?

|비교 위치|원래 구현|visited만 바꾼 실험|
|---|---|---|
|lookup 뒤 values.visited|["lookup"]|["lookup"]|
|ask 뒤 마지막 values.visited|["lookup", "ask"]|["ask"]|
|마지막 topic·contact·data|유지|유지|
|질문 문장|회신 대상 질문|동일|

lookup이 실행되지 않은 것이 아니라 기록에서만 사라졌습니다. 앞선 `updates['lookup']`이 실제 실행을 보여 줍니다. 이 State의 visited에는 누적 reducer가 없으므로 새 목록이 이전 목록을 대체합니다. 반환하지 않은 필드는 유지됩니다. `route_inquiry`는 조건부 엣지의 목적지를 고르는 함수라 노드 업데이트 이름으로 나오지 않습니다. 실험 뒤 전체 방문 목록을 반환하도록 복원하고 2A를 다시 검사합니다.

## 셀 25 · ID retry-graph-guide

### 2C. 고급 확장 · 검토 실패를 그래프의 재작업 경로로 연결합니다

2A의 그래프를 먼저 완성한 뒤 진행합니다. `build_workflow`를 덮어쓰지 않고 별도의 `build_retry_graph`를 작성합니다. 15분 추가 실습 또는 복습 과제입니다.

**요구:** review → (통과/한도 소진이면 END, 실패했고 예산이 남으면 revise → review). 첫 검사는 수정 횟수 0에서 시작합니다. 수정 노드를 실행할 때만 attempts가 1 증가합니다. 같은 초안이 반복되어도 limit에서 반드시 종료해야 합니다.

State와 노드 본문은 제공합니다. `route_review`의 예산 판단, StateGraph 생성, 노드 등록과 엣지·compile을 직접 작성합니다. limit=0과 2에서 수정 호출 수를 먼저 예상합니다. 이 확장은 검토 이후의 부분 그래프이며, 정보 부족 입력을 다루는 2A의 lookup·ask 흐름을 대체하지 않습니다.

다음 셀에서는 의도적으로 잘못된 최초 초안을 넣고 실제 모델에 수정을 맡깁니다. `limit`만 바꾸어 비교합니다. 막히면 풀이의 같은 2C 코드를 확인합니다. 비교 기준은 마지막 답변만이 아니라 attempts·feedback·visited입니다.


## 셀 26 · ID retry-graph-build

```python
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class RetryState(TypedDict, total=False):
    draft: str
    data: dict
    attempts: int
    feedback: list[str]
    visited: list[str]

def build_retry_graph(revise, limit):
    def review(state):
        return {"feedback": inspect_draft(state["draft"], state["data"]),
                "visited": state.get("visited", []) + ["review"]}

    def repair(state):
        return {"draft": revise(state["draft"], state["feedback"]),
                "attempts": state["attempts"] + 1,
                "visited": state["visited"] + ["revise"]}

    def route_review(state):
        if not state["feedback"] or state["attempts"] >= limit:
            return "finish"
        return "revise"

    builder = StateGraph(RetryState)
    builder.add_node("review", review)
    builder.add_node("revise", repair)
    builder.add_edge(START, "review")
    builder.add_conditional_edges("review", route_review, {"finish": END, "revise": "revise"})
    builder.add_edge("revise", "review")
    return builder.compile()

```

## 셀 27 · ID retry-graph-run

```python
retry_data = json.loads(lookup_policy("계정"))

def repair_with_model(draft, feedback):
    response = model.invoke(
        "다음 정책과 검사 오류를 읽고 초안을 수정하십시오. 답변만 반환하십시오.\n"
        + json.dumps({"draft": draft, "policy": retry_data, "feedback": feedback}, ensure_ascii=False)
    )
    return response.content

retry_limit = 2  # 0과 2로 각각 실행합니다.
retry_graph = build_retry_graph(repair_with_model, retry_limit)
retry_result = retry_graph.invoke(
    {"draft": "확인 완료", "data": retry_data, "attempts": 0, "visited": []},
    config={"recursion_limit": 16},
)
print("방문:", retry_result["visited"])
print("실제 수정 횟수:", retry_result["attempts"])
print("남은 검사 오류:", retry_result["feedback"])
print("최종 초안:", retry_result["draft"])

```

## 셀 28 · ID retry-graph-reading

### 2C 풀이 · 끝났다는 것과 통과했다는 것

limit=0이면 review 한 번, attempts=0, 오류가 남은 채 종료됩니다. limit=2에서 첫 수정으로 통과하면 review → revise → review, attempts=1입니다. 두 번 수정해도 오류가 남으면 attempts=2에서 종료됩니다. 그래프가 END에 도달했다는 이유만으로 성공이라고 말하지 않습니다. feedback이 비었는지 별도로 확인합니다.

모델 대신 `lambda draft, feedback: draft`를 revise로 전달해 보십시오. limit=2이면 같은 초안이라도 두 번 수정 시도 후 종료되어야 합니다. 이 그래프에는 동일 초안 조기 중단 정책은 없습니다. 이를 추가하려면 이전 후보를 State에 남기는 위치와 비교 시점을 먼저 설계합니다. `recursion_limit` 오류로 멈추는 것은 업무상 수정 예산을 구현한 결과가 아닙니다.


## 셀 29 · ID course-14

## 3. 선택 심화 · 제공 수정 Loop 관찰

실패한 초안을 실제 모델에 다시 맡깁니다. `refine_answer`는 제공 루프이며, 공통 과정에서는 그대로 사용합니다. 전체 알고리즘 작성은 선택 심화입니다.

**실행 전 예상:** 상한이 0이면 수정은 몇 번 실행될까요? 모델이 직전과 똑같은 초안을 반환하면 언제 멈출까요?

`passed`는 검토 통과, `stalled`는 직전과 동일한 초안, `held`는 수정 상한 소진입니다. 같은 오류가 남아 있어도 문자열이 달라지면 이 구현은 정체로 판정하지 않습니다. 수정 실행 셀의 `limit`을 0과 2로 바꿔 `history`와 수정 입력을 비교합니다.


## 셀 30 · ID course-15

```python
def refine_answer(draft, data, revise, limit=2):
    if type(limit) is not int or not 0 <= limit <= 5:
        raise ValueError("수정 상한은 0~5 정수입니다.")
    history = []
    for attempt in range(limit + 1):
        feedback = inspect_draft(draft, data)
        history.append({"attempt": attempt, "draft": draft, "feedback": feedback})
        if not feedback:
            return {"status": "passed", "draft": draft, "history": history}
        if len(history) > 1 and history[-2]["draft"] == draft:
            return {"status": "stalled", "draft": draft, "history": history}
        if attempt == limit:
            return {"status": "held", "draft": draft, "history": history}
        draft = revise(draft, feedback)
```

## 셀 31 · ID course-16

```python
model = get_model()
feedback_inputs = []
data = json.loads(lookup_policy("계정"))


def make_reviser(policy_data, record):
    # 이번 문의의 정책을 사용하도록 수정 함수를 만듭니다.
    def revise(draft, feedback):
        record.append({"draft": draft, "feedback": feedback})
        return model.invoke(
            "규정에 따라 초안을 수정하십시오. 담당 팀과 근거 ID를 포함하십시오.\n"
            + json.dumps(
                {"policy": policy_data, "draft": draft, "feedback": feedback},
                ensure_ascii=False,
            )
        ).content

    return revise


revise = make_reviser(data, feedback_inputs)

limit = 2  # 0으로 바꾸면 수정 모델을 호출하지 않습니다.
repaired = refine_answer("확인 완료", data, revise, limit)
print(json.dumps(repaired, ensure_ascii=False, indent=2))
print("실제로 전달한 수정 입력:", feedback_inputs)
assert len(feedback_inputs) <= limit
assert bool(feedback_inputs) is (limit > 0)
assert repaired["history"][0]["draft"] == "확인 완료"
```

## 셀 32 · ID course-17

## 연결하고 설명합니다

앞에서 만든 그래프에 제공 수정 루프를 연결합니다. 결과가 통과하지 않으면 기준을 낮추지 말고 history의 실패와 수정 입력을 읽습니다.

## 셀 33 · ID course-18

```python
def refine(draft, data, limit):
    revise_current = make_reviser(data, [])
    return refine_answer(draft, data, revise_current, limit)


app = build_workflow(lookup_policy, generate, refine, limit=2)
final = app.invoke({"topic": "계정", "contact": "user@example.test"})
print(json.dumps(final, ensure_ascii=False, indent=2))
```

## 셀 34 · ID 8169edf1

## Harness 설계 메모

**반복 조건 실험 · 먼저 5분:** 같은 폴더의 `harness-control.ipynb`를 엽니다. 모델 호출 없이 수정 후보를 직접 만들어 마지막 허용 수정의 성공과 같은 초안 반복을 비교합니다. 실험 뒤 이 메모로 돌아와 다음 실행을 허용할 근거를 적습니다.

교재 Harness의 [코딩 작업을 설계하는 활동](https://yo-sure.github.io/deepagents-handson/workshop/engineering#task)에서 공백 분기 결함과 출력 필드 안내 불일치의 두 사례를 읽습니다. 별도 활동지 파일 대신 **이 Markdown 셀에** 작성합니다. 더블클릭해 편집하고 Shift+Enter로 읽기 모드로 돌아옵니다.

**실행 순서 하나:** 문제 발견 → 수정 → 기능·문서 검토 → 결과 모으기 → 종료 순으로, 각 단계의 행동과 확인할 결과를 적습니다.

여기에 작성:

|반례|다음 행동|그 행동을 결정할 근거|
|---|---|---|
|같은 요청이 두 번 도착함| | |
|기능 또는 문서 검토 하나가 빠짐| | |
|검사 기대값을 현재 초안에 맞춰 바꾼 뒤 PASS 처리함| | |

**마지막 확인:** 검토 둘이 같은 v2를 보는지, 누락된 검토를 성공으로 처리하지 않는지, 두 번 수정해도 실패하면 어디로 인계할지 확인합니다. 역할별 입력·산출물·권한의 상세 설계는 선택 확장입니다.

### 풀이 예시 · 같은 문장보다 판단 근거를 비교합니다

**실행 순서:** F1·D1 수집 → 후보 v1과 원래 요구 고정 → 구현 담당에게 수정 범위 전달 → 후보 v2 고정 → 기능 검토와 설명 검토를 병렬 실행 → 같은 v2의 두 결과 취합 → 통과하면 사람의 최종 확인, 실패하면 남은 2회 예산 안에서 재배정합니다.

|반례|다음 행동|확인할 근거|
|---|---|---|
|해결된 F1이 다시 도착함|즉시 재배정하지 않고 동일 결함·동일 후보인지 확인|실패 ID, 후보 버전, 저장된 해결 결과. 새 버전에서 재발했다면 새 검토가 필요함|
|기능 검토만 도착함|설명 검토를 기다리되 시간 제한 후 담당 상태를 확인하고 인계|v2의 설명 검토 결과 또는 누락 사유. 결과 없음은 PASS가 아님|
|기대값을 draft로 바꾼 PASS|완료를 보류하고 원래 요구와 검사 변경을 대조|공백이면 ask·초안 호출 0회라는 요구, 변경 diff, 원래 검사 결과|

**중단 인계:** 두 번 수정해도 해결되지 않으면 후보 버전, 실패 입력, 원래 기대 결과, 마지막 실제 결과, 시도한 변경과 미해결 항목을 담당자에게 넘깁니다. 예산 소진은 성공이 아닙니다. 병렬 검토 동안 후보가 바뀌면 이전 후보의 PASS를 새 후보에 합치지 않습니다.

**실행 실험 연결:** 마지막 허용 수정이 통과했다면 검토 후 성공으로 끝내야 합니다. 실패한 초안이 그대로 돌아오면 같은 입력을 무작정 재요청하기보다 근거와 작업 범위를 다시 점검합니다. 이 사례의 규칙 검사 통과만으로 모든 답변의 사실성이 입증되는 것은 아닙니다.


## 셀 35 · ID course-19

## 4. MCP · 원격 도구를 LangChain에 연결합니다

**목표:** 등록·목록 조회·도구 실행 중 어느 단계에서 조회 함수가 실행되는지 구분하고, 입력 오류와 업무상 결과 없음을 설명합니다.

1. `build_mcp_server`에서 **인자로 받은 함수**를 등록하고 서버를 반환합니다. 전역 함수를 직접 등록하지 않습니다.
2. 4A를 실행하기 전에 아래 관찰 기록의 예상 횟수를 채웁니다. 등록, 목록 조회, 정상 호출, 없는 업무, 잘못된 입력을 비교합니다.
3. 4B에서 도구 목록을 Agent에 연결한 뒤, 도구 요청·결과·최종 답변을 읽습니다.

서버 시작·종료는 제공된 `serve_app`이 맡습니다. 별도 터미널을 열지 않습니다. `recorded_lookup`은 함수 실행만 기록하는 제공 코드입니다. `wraps`는 원래 이름·설명·입력 형식을 유지합니다. 함수를 수정하면 정의 셀부터 다시 실행합니다.


**직접 작성:** `build_mcp_server`의 서버 생성·도구 등록, `build_remote_agent`의 모델·원격 도구·지침 연결, 4B의 `adapter.list_tools()` 호출입니다. 별도 네트워크 보조 코드 작성 없이 프로토콜 연결의 핵심을 작성합니다. 풀이 노트북의 4·4B를 같은 순서로 확인합니다.

**4B 핵심 구현:** `run_remote_agent(url, model, question)`의 async with MCPAdapter(Client(...)) 안에서 목록 조회 → Agent 구성 → ainvoke → 결과 반환을 작성합니다. url은 /mcp까지 포함하며 mode="2026-07-28"을 사용합니다. Agent 호출을 연결 밖으로 옮기면 도구 실행 시 연결이 끝나 있을 수 있습니다. 4A는 직접 호출을 먼저 검사하는 제공 진단 셀입니다.

## 셀 36 · ID course-20

```python
from mcp.server.mcpserver import MCPServer
from course.notebook_server import serve_app
from langchain.mcp import MCPAdapter
from fastmcp import Client


def build_mcp_server(policy_tool):
    server = MCPServer("업무 정책 도구")
    server.tool()(policy_tool)
    return server

def build_remote_agent(model, remote_tools):
    return create_agent(
        model=model, tools=remote_tools,
        system_prompt="업무 규정을 도구로 조회하고 담당 팀과 정책 ID를 답합니다. 규정이 없으면 추가 확인을 요청합니다.",
    )


async def run_remote_agent(url, model, question):
    async with MCPAdapter(Client(url, mode="2026-07-28")) as adapter:
        remote_tools = await adapter.list_tools()
        if not remote_tools:
            raise ValueError("서버가 공개한 도구가 없습니다.")
        agent = build_remote_agent(model, remote_tools)
        return await agent.ainvoke(
            {"messages": [{"role": "user", "content": question}]},
            config={"recursion_limit": 12},
        )

```

## 셀 37 · ID course-21

```python
# 4A. 모델 없이 등록·발견·실행 경계를 관찰합니다.
from functools import wraps

lookup_calls = []

@wraps(lookup_policy)
def recorded_lookup(topic: str) -> str:
    lookup_calls.append(topic)
    return lookup_policy(topic)

server = build_mcp_server(recorded_lookup)
print("등록 뒤 호출 횟수:", len(lookup_calls))
async with serve_app(
    server.streamable_http_app(stateless_http=True, json_response=True)
) as url:
    async with MCPAdapter(Client(url + "/mcp", mode="2026-07-28")) as adapter:
        tools = await adapter.list_tools()
        print("도구 목록:", [t.name for t in tools])
        print("목록 조회 뒤 호출 횟수:", len(lookup_calls))
        policy_tool = next(t for t in tools if t.name == "lookup_policy")
        print("입력 형식:", policy_tool.args)
        for topic in ["정산", "계정", "없는업무"]:
            content = await policy_tool.ainvoke({"topic": topic})
            print(topic, content)
            print("조회 함수 호출 횟수:", len(lookup_calls))

        # 이 입력을 직접 바꾸어 필수 입력 조건을 확인합니다.
        invalid_arguments = {}
        error_content = await policy_tool.ainvoke(invalid_arguments)
        print("잘못된 입력의 반환 내용:", error_content)
        print("잘못된 입력 뒤 호출 횟수:", len(lookup_calls))
        assert lookup_calls == ["정산", "계정", "없는업무"], (
            "topic 필수 조건을 위반하는 입력을 넣었는지 확인하십시오."
        )

```

## 셀 38 · ID course-22

### 4A 관찰 기록

다음 표는 초기 입력 그대로 실행한 결과의 풀이입니다. 횟수는 셀 실행을 시작한 뒤의 **조회 함수 누적 실행 횟수**입니다.

|시점|예상 횟수|실제 횟수와 이유|
|---|---|---|
|서버에 등록한 직후|0|등록은 실행할 함수와 설명을 연결합니다.|
|도구 목록을 받은 직후|0|발견 요청은 도구 설명을 가져옵니다.|
|정산 조회 뒤|1|유효한 입력으로 함수가 실행됩니다.|
|계정 조회 뒤|2|다른 업무를 새로 조회합니다.|
|없는업무 조회 뒤|3|유효한 문자열이므로 조회한 뒤 found=false를 반환합니다.|
|필수 topic이 없는 입력 뒤|3|함수 본문 이전에 입력 조건 위반으로 거절됩니다.|

**4A 완료 기준:** 도구 이름·입력 형식, P-01·재무지원팀, P-02·IT지원팀, `found=false`를 확인합니다. 없는업무와 잘못된 입력 중 어느 경우에 함수가 실행되는지 설명합니다. `invalid_arguments`를 자신이 만든 입력으로 바꾸어 `topic` 필수 조건을 확인합니다. 이 셀은 모델을 호출하지 않습니다. 고정 버전의 Adapter는 도구 오류를 내용으로 반환할 수 있습니다. 예외 유무만 보지 말고 오류 내용과 함수 실행 횟수를 함께 읽습니다.

## 4B. 같은 원격 도구를 Agent에 연결합니다

다음 셀의 `tools`에 발견한 원격 도구 목록을 연결합니다. 4A에서 사용한 API를 찾아 적용합니다. 질문을 바꿔 재실행합니다. 이 셀은 실제 모델을 호출하므로 API 키 설정이 필요합니다. `model`은 이 셀에서 준비합니다.


## 셀 39 · ID 30eec1d0

```python
model = get_model()
question = "계정 문의는 어느 팀에 해야 하나요? 근거 ID도 알려주세요."
server = build_mcp_server(lookup_policy)
async with serve_app(
    server.streamable_http_app(stateless_http=True, json_response=True)
) as url:
    result = await run_remote_agent(url + "/mcp", model, question)
for message in result["messages"]:
    print(message.type, message.content)
    if getattr(message, "tool_calls", None):
        print("도구 요청:", message.tool_calls)
    if message.type == "tool":
        print("요청 연결 ID:", message.tool_call_id, "상태:", message.status)

```

## 셀 40 · ID e7623882

**4B 완료 기준:** AIMessage의 lookup_policy 요청 → ToolMessage의 P-02·IT지원팀 → 최종 답변을 확인합니다. 목록만 출력되거나 도구 요청 없이 답하면 아직 완료가 아닙니다. 없는 업무도 질문하여 추가 확인 안내를 비교합니다.


**풀이:** 목록 조회만으로 함수가 실행되지 않는다는 점은 4A에서 확인했습니다. 4B는 그 목록을 모델에 알려 주고 모델이 요청한 도구를 실행합니다. AIMessage의 tool_calls와 ToolMessage의 tool_call_id를 대조하고, 계정 조회 결과에 P-02·IT지원팀이 있는지 확인합니다. 없는업무는 조회 성공 뒤 found=false라는 업무 결과를 전달하므로, 모델은 팀을 추측하지 않고 추가 확인을 요청해야 합니다.


## 셀 41 · ID mcp-result-reading

### 4B 풀이 · 로컬 함수가 원격 도구로 바뀐 지점

`adapter.list_tools()`의 결과는 이미 LangChain 도구 목록입니다. `build_remote_agent`에 이 목록을 전달하고 ainvoke를 실행하면 모델이 요청을 고르고 어댑터가 MCP로 전달합니다. ToolMessage에 P-02·IT지원팀이 있고 마지막 답변이 일치하는지 읽습니다. 도구 목록만 출력되었다면 발견까지만 완료된 것입니다. 4A에서 등록·목록 조회 뒤 호출 횟수 0, 실제 호출 뒤 1·2·3으로 증가하는 결과와 연결해서 설명합니다.

## 셀 42 · ID course-23

## 5. A2A · 발견 → 위임 → 결과 확인

5A는 모델 호출 없이 실제 HTTP로 Agent Card를 읽습니다. 5B에서는 같은 서버에 검토를 요청하며 실제 모델이 표현을 검토합니다. 서버 시작·종료와 SDK 연결 코드는 제공됩니다. 그 뒤 accept_review를 직접 구현합니다.


**직접 작성:** 5A 셀의 `make_review_request(payload)`에서 Message·Part·SendMessageRequest를 만듭니다. 5A의 Card 조회는 이 함수가 미완성이어도 실행됩니다. 5B부터는 구현이 필요합니다. Card 기반 클라이언트 생성·응답 수신은 제공 `delegate`가 맡고, 자신이 만든 요청 객체를 그대로 전송합니다. 막히면 풀이 노트북의 같은 5A 정의와 5B 실행을 비교합니다.

`connect_review_client(http, url, expected_skill)`도 작성합니다. A2ACardResolver로 Card를 읽고 skills의 id를 확인한 뒤, ClientConfig(httpx_client=http, streaming=False, supported_protocol_bindings=["JSONRPC", "HTTP+JSON"])를 ClientFactory에 전달하고 create(card=card)로 연결합니다. card, client를 반환합니다. 요청 구성은 make_review_request, 연결은 connect_review_client, 응답 파싱은 제공 delegate의 역할입니다. 5A에서 읽은 Card의 값을 5B 연결에 사용한다는 뜻입니다.

## 셀 43 · ID 3844fee3

### 5A. Agent Card를 먼저 읽습니다 (모델 호출 없음)

이 셀은 서버가 공개한 기능과 접속 정보를 읽습니다. review-policy, JSONRPC, streaming=false를 찾습니다. 첫 환경 셀 다음에 이 셀을 실행할 수 있습니다. 모델 객체와 API 키가 필요하지 않습니다.


## 셀 44 · ID 5bf91bbd

```python
from a2a.types import Message, Part, Role, SendMessageRequest, SendMessageConfiguration
import uuid

def make_review_request(payload):
    return SendMessageRequest(
        message=Message(
            role=Role.ROLE_USER,
            message_id=str(uuid.uuid4()),
            parts=[Part(text=json.dumps(payload, ensure_ascii=False))],
        ),
        configuration=SendMessageConfiguration(return_immediately=False),
    )

import httpx
from google.protobuf.json_format import MessageToDict
from a2a.client import A2ACardResolver
from course.a2a_lab import create_app, delegate
from course.notebook_server import serve_app

from a2a.client import ClientConfig, ClientFactory

async def connect_review_client(http, url, expected_skill):
    card = await A2ACardResolver(httpx_client=http, base_url=url).get_agent_card()
    if expected_skill not in [skill.id for skill in card.skills]:
        raise ValueError("검토 기능이 없는 Agent입니다.")
    client = ClientFactory(config=ClientConfig(
        httpx_client=http, streaming=False,
        supported_protocol_bindings=["JSONRPC", "HTTP+JSON"],
    )).create(card=card)
    return card, client

async with serve_app(create_app, factory=True) as url:
    async with httpx.AsyncClient() as http:
        card = await A2ACardResolver(httpx_client=http, base_url=url).get_agent_card()
        print(json.dumps(MessageToDict(card), ensure_ascii=False, indent=2))
```

## 셀 45 · ID 44329c04

### 5B. 초안 하나를 실제로 맡깁니다 (모델 호출 있음)

draft에 담당 팀과 정책 ID가 있는 경우와 없는 경우를 비교합니다. Message와 Task는 SDK가 직렬화한 실제 값입니다. task.status.state는 프로토콜 표기, review.state는 수업 함수가 읽기 쉽게 바꾼 값입니다. 수업 서버는 최종 응답을 기다리므로 중간 상태 스트림은 출력하지 않습니다.


## 셀 46 · ID e9d4e2aa

```python
import uuid

model = get_model()

payload = {
    "topic": "계정",
    "draft": "계정 문의는 IT지원팀에 전달합니다. 근거: P-02",
    "request_id": str(uuid.uuid4()),
    "version": 1,
}
async with serve_app(lambda port: create_app(port, model=model), factory=True) as url:
    review = await delegate(url, payload, request=make_review_request(payload), connect=connect_review_client)
print("보낸 Message:", json.dumps(review["message"], ensure_ascii=False, indent=2))
print("받은 Task:", json.dumps(review["task"], ensure_ascii=False, indent=2))
print("검토 산출물:", review["artifact"])
```

## 셀 47 · ID 3e21cd04

### 5C. 현재 초안에 쓸 수 있는 결과인지 판단합니다

**요청:** 검토 작업이 끝났더라도 다른 요청이나 옛 초안의 결과라면 채택하면 안 됩니다. `accept_review`를 직접 작성합니다.

|조건|반환값|
|---|---|
|submitted / working|pending|
|completed이며 현재 요청 ID·버전과 일치하고 passed가 불리언 True|accepted|
|그 외 상태, 결과 누락, 검토 실패, 요청·버전 불일치|held|

요청 ID는 공백이 아닌 문자열, 버전은 1 이상의 정수입니다. `True`를 버전 1로 받거나 문자열 `"true"`를 통과로 받지 않습니다.

**먼저 예상:** 옛 버전, 작업은 완료됐지만 검토 실패, 산출물 누락의 세 경우를 말로 판정합니다. 구현 후 아래 검사에서 이유별 결과를 확인합니다. 제공 사례 외에 잘못 수용될 수 있는 입력 하나를 직접 추가합니다.


## 셀 48 · ID course-24

```python
def accept_review(state, artifact, request_id, version):
    from course.a2a_lab import accept_result

    return accept_result(state, artifact, request_id, version)
```

## 셀 49 · ID course-25

```python
check_accept_review(accept_review)

print(
    "실제 결과 수용:",
    accept_review(
        review["state"], review["artifact"], payload["request_id"], payload["version"]
    ),
)
```

## 셀 50 · ID a2a-result-reading

### 5B·5C 풀이 · 요청을 만든 것과 검토를 통과한 것

보낸 Message의 messageId는 이번 메시지의 ID이고, text 안의 request_id·version은 우리 검토 업무의 약속입니다. 서버가 만든 Task의 id와도 구별합니다. `make_review_request`의 JSON 텍스트가 서버 검토기에 전달됩니다. Task가 completed면 검토 작업이 끝났다는 뜻이며, artifact.passed가 False이면 초안은 불합격입니다. 5C 검사 통과는 이 구분과 요청·버전 일치를 자신의 코드가 처리했다는 의미입니다. 실제 결과 수용이 accepted인지도 별도로 봅니다.

## 셀 51 · ID course-26

## 6. 통합 · 한 요청을 세 단계로 확인합니다

앞에서 작성한 함수를 연결합니다. 입력 변경은 6A에서 하고 **6A → 6B → 6C를 순서대로** 실행합니다. 각 셀에서 나온 값을 다음 셀에 전달합니다.

### 6A. MCP에서 정책을 읽습니다

`topic`과 `contact`를 정합니다. 결과 `snapshot`의 업무명과 정책을 확인합니다. 아직 모델을 호출하지 않습니다.


## 셀 52 · ID 530e87c3

```python
from build_lab.guided import refine_answer  # 통합에서 사용할 제공 수정 함수
import uuid

topic = "계정"
contact = "user@example.test"
server = build_mcp_server(lookup_policy)
async with serve_app(
    server.streamable_http_app(stateless_http=True, json_response=True)
) as url:
    async with MCPAdapter(Client(url + "/mcp", mode="2026-07-28")) as adapter:
        remote_tools = await adapter.list_tools()
        remote_lookup = next(t for t in remote_tools if t.name == "lookup_policy")
        content = await remote_lookup.ainvoke({"topic": topic})
snapshot = json.loads(
    next(block["text"] for block in content if block["type"] == "text")
)

print("조회한 정책:", snapshot)

```

## 셀 53 · ID 694a0a2c

### 6B. 조회한 정책으로 Graph를 실행합니다

아래 연결 코드는 제공됩니다. 6A의 `snapshot`을 도구와 검토에 전달합니다. `visited`, `missing`, `history`, `decision`을 읽습니다. 정상 입력에서는 실제 모델을 호출합니다.


## 셀 54 · ID 53c5a346

```python
def make_snapshot_tool(snapshot):
    def lookup_policy(topic: str) -> str:
        """이번 문의에서 조회한 정책을 반환합니다."""
        data = (
            snapshot
            if topic.strip() == snapshot["topic"]
            else {"found": False, "topic": topic.strip(), "policy": None}
        )
        return json.dumps(data, ensure_ascii=False)

    return lookup_policy


model = get_model()
snapshot_lookup = make_snapshot_tool(snapshot)
connected_agent = build_agent(model, snapshot_lookup)
generation_records = []


def connected_generate(topic):
    result = connected_agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": json.dumps({"topic": topic}, ensure_ascii=False),
                }
            ]
        }
    )
    generation_records.append(result["messages"])
    return result["messages"][-1].content


def connected_refine(draft, data, limit):
    def revise_current(draft, feedback):
        return model.invoke(
            "규정에 맞게 초안을 수정하십시오.\n"
            + json.dumps(
                {"policy": data, "draft": draft, "feedback": feedback},
                ensure_ascii=False,
            )
        ).content

    return refine_answer(draft, data, revise_current, limit)


workflow = build_workflow(snapshot_lookup, connected_generate, connected_refine)
result = workflow.invoke({"topic": snapshot["topic"], "contact": contact})
print("Graph 결과:", result)
for messages in generation_records:
    for message in messages:
        print("6B", message.type, message.content, getattr(message, "tool_calls", []))

```

## 셀 55 · ID 66ffe421

### 6C. 통과한 초안만 원격 검토에 맡깁니다

6B 결과가 `passed`일 때 A2A 검토를 요청하고 자신의 `accept_review`로 수용 여부를 결정합니다. 추가 정보가 필요하거나 초안 검토가 실패했다면 원격 검토 전에 끝납니다.

이번 실행이 원격 검토를 건너뛰면 `review`와 `decision`은 `None`입니다. 이전 요청의 `accepted`를 이번 결과로 읽지 않도록 실행할 때 초기화합니다.


## 셀 56 · ID aa75be74

```python
# 재실행할 때 이전 요청의 검토 결과를 남기지 않습니다.
payload = None
review = None
decision = None

if result["decision"] == "passed":
    payload = {
        "topic": result["data"]["topic"],
        "draft": result["draft"],
        "request_id": str(uuid.uuid4()),
        "version": 1,
    }
    async with serve_app(
        lambda port: create_app(port, model=model), factory=True
    ) as url:
        review = await delegate(url, payload)
    decision = accept_review(
        review["state"], review["artifact"], payload["request_id"], payload["version"]
    )
    print("원격 검토:", review)
    print("수용 판단:", decision)
else:
    print("원격 검토 전 종료:", result["decision"])
```

## 셀 57 · ID course-28

**완료 확인:** 계정+정상 주소와 정보 부족 입력을 비교합니다. `completed`만으로 채택하지 않고 요청·버전·통과 조건을 확인합니다.

별칭 변경 과제에서는 `lookup_policy`를 수정한 뒤 정의 셀과 6A→6B→6C를 다시 실행합니다. 기존 정산·계정·미등록 입력의 동작도 유지되어야 합니다.


## 셀 58 · ID 9d119cd7

## 6D. Card를 발견하고 담당 Agent를 선택해 위임합니다

6A~6C는 코드가 순서와 담당자를 정했습니다. 여기서는 모델이 **MCP 정책 조회 → 실제 Card 발견 → 기능 비교 → 담당자 선택 → A2A 위임**을 수행합니다. 후보 주소 두 개는 수업이 제공합니다. 인터넷에서 서버를 자동 검색하는 예제가 아닙니다. `discover_agents`는 HTTP로 읽은 Card를 모델에 반환하고, 모델은 `delegate_to_agent`의 agent_id·skill_id 인자로 선택을 표현합니다.

첫 환경 셀과 lookup_policy·build_mcp_server·accept_review 정의가 필요합니다. 두 서버·MCP 연결은 제공됩니다. 먼저 선택을 예측한 뒤 mission을 바꾸고 실제 호출 기록을 비교합니다. 역할별 정답 후보 ID를 프롬프트에 넣지 않습니다.


## 셀 59 · ID 5e93e726

```python
import json
import uuid
import httpx
from contextlib import AsyncExitStack
from functools import partial
from google.protobuf.json_format import MessageToDict
from a2a.client import A2ACardResolver
from langchain.agents import create_agent
from langchain.tools import tool
from langchain.mcp import MCPAdapter
from fastmcp import Client
from course.common import get_model
from course.a2a_lab import create_app, delegate
from course.notebook_server import serve_app

def build_connected_agent(model, mcp_tools, discover_agents, delegate_to_agent):
    connected_tools = [*mcp_tools, discover_agents, delegate_to_agent]
    print("연결된 도구:", [t.name for t in connected_tools])
    return create_agent(
        model=model, tools=connected_tools,
        system_prompt=(
            "사내 문의를 처리합니다. 정책은 MCP 조회 결과에 근거하십시오. "
            "담당자에게 맡길 때에는 먼저 실제 Agent Card를 발견하고 기능 설명으로 선택하십시오. "
            "후보 이름이나 나열 순서만으로 선택하지 마십시오. "
            "정책이 없으면 추측하거나 검토를 요청하지 말고 추가 정보를 요청하십시오. "
            "표현 검토만 요청받으면 정책 조회와 정책 검토는 필요하지 않습니다. "
            "실제 도구 결과와 선택 이유를 보고하십시오."
        ),
    )

async def run_connected_agent(mission, *, reverse_candidates=False):
    """요청마다 실제 서버와 연결을 만들고 종료한 뒤 실행 증거를 반환합니다."""
    model = get_model()
    discovery_records, review_records = [], []
    server = build_mcp_server(lookup_policy)

    # 1. 서버와 연결을 준비합니다. stack은 함수가 끝날 때 모두 닫습니다.
    async with AsyncExitStack() as stack:
        mcp_url = await stack.enter_async_context(serve_app(
            server.streamable_http_app(stateless_http=True, json_response=True)
        ))
        # 주소는 수업의 후보 목록입니다. 실제 기능은 HTTP로 읽은 Card에서 확인합니다.
        candidates = {}
        candidate_profiles = [
            ("candidate-a", "style", "HTTP+JSON"),
            ("candidate-b", "policy", "JSONRPC"),
        ]
        if reverse_candidates:
            candidate_profiles.reverse()
        for agent_id, profile, binding in candidate_profiles:
            # 역할과 바인딩을 고정하고, 서버가 정한 port만 나중에 받습니다.
            create_candidate = partial(
                create_app, model=model, profile=profile, binding=binding
            )
            candidates[agent_id] = await stack.enter_async_context(
                serve_app(create_candidate, factory=True)
            )
        mcp_adapter = await stack.enter_async_context(
            MCPAdapter(Client(mcp_url + "/mcp", mode="2026-07-28"))
        )
        mcp_tools = await mcp_adapter.list_tools()
        discovered_cards = {}

        # 2. 모델이 실제 Card를 읽을 수 있는 발견 도구를 정의합니다.
        @tool
        async def discover_agents() -> str:
            """등록된 후보 서버의 실제 Agent Card를 읽습니다. 기능과 접속 방식을 비교해 담당자를 선택하십시오."""
            cards = []
            async with httpx.AsyncClient(timeout=20) as http:
                for agent_id, url in candidates.items():
                    card = await A2ACardResolver(httpx_client=http, base_url=url).get_agent_card()
                    discovered_cards[agent_id] = card
                    cards.append({"agent_id": agent_id, "card": MessageToDict(card)})
            discovery_records.append(cards)
            return json.dumps(cards, ensure_ascii=False)

        # 3. 발견한 기능을 확인한 뒤 선택된 Agent에 위임합니다.
        @tool
        async def delegate_to_agent(agent_id: str, skill_id: str, topic: str, draft: str) -> str:
            """발견한 Card의 기능에 맞는 Agent를 선택해 맡깁니다. agent_id와 skill_id는 발견 결과를 사용합니다."""
            card = discovered_cards.get(agent_id)
            if card is None:
                return "먼저 discover_agents로 실제 Card를 읽고 후보를 선택하십시오."
            if skill_id not in [s.id for s in card.skills]:
                return "선택한 Card가 제공하지 않는 기능입니다. 기능 설명을 다시 비교하십시오."
            payload = {
                "topic": topic, "draft": draft,
                "request_id": str(uuid.uuid4()), "version": 1,
            }
            review = await delegate(candidates[agent_id], payload, expected_skill=skill_id)
            record = {
                "agent_id": agent_id, "skill_id": skill_id,
                "binding": card.supported_interfaces[0].protocol_binding,
                "task_id": review["task"]["id"],
                "state": review["state"], "artifact": review["artifact"],
            }
            if skill_id == "review-policy":
                record["decision"] = accept_review(
                    review["state"], review["artifact"], payload["request_id"], payload["version"]
                )
            review_records.append(record)
            return json.dumps(record, ensure_ascii=False)

        # 4. MCP 조회·Card 발견·위임을 한 Agent의 도구로 연결합니다.
        final_agent = build_connected_agent(model, mcp_tools, discover_agents, delegate_to_agent)
        final_run = await final_agent.ainvoke(
            {"messages": [{"role": "user", "content": mission}]},
            config={"recursion_limit": 20},
        )

    return final_run, discovery_records, review_records

```

## 셀 60 · ID agent-card-selection-mission

```python
# 직접 변경: 요청을 읽고 어떤 Card가 선택될지 먼저 예상합니다.
mission = "계정 문의의 정책을 조회하고 담당 팀과 정책 ID를 넣어 초안을 작성하세요. 후보 Card를 비교하여 정책 근거를 검증할 담당자에게 맡기고 선택 이유와 결과를 알려주세요."
final_run, discovery_records, review_records = await run_connected_agent(mission)

for message in final_run["messages"]:
    print("\n역할:", message.type, "\n내용:", message.content)
    if getattr(message, "tool_calls", None):
        print("모델이 선택한 도구:", message.tool_calls)
print("\n실제 HTTP Card 조회:", discovery_records)
print("\n선택 및 A2A 실행 기록:", review_records)

```

## 셀 61 · ID ad49d9c9

### 같은 코드에서 요청만 바꾸어 비교합니다

|mission|예상 선택|확인할 증거|
|---|---|---|
|기본 요청: 계정 정책 근거 검증|review-policy 기능|MCP P-02·IT지원팀 → 실제 Card 두 개 → 선택 인자 → Task ID·accepted|
|“정책 검증은 필요 없습니다. ‘그거 처리해 주세요’라는 문장의 불명확한 표현만 검토할 담당자를 Card에서 찾아 맡겨주세요.”|review-style 기능|같은 후보 목록에서 다른 담당자 선택, HTTP+JSON 바인딩, 표현 검토 산출물|
|“없는업무의 담당 팀을 조회해 줘”|위임하지 않음|found=false와 추가 질문, review_records가 비어 있음|

각 실행은 서버와 기록을 새로 시작합니다. Card를 읽기 전에 위임하면 도구가 발견을 요청하며, Card에 없는 skill을 지정하면 거절합니다. **도구가 후보를 자동 분류하는 것이 아니라 모델이 Card 설명을 읽고 선택**합니다. 출력의 선택 이유와 실제 agent_id·skill_id를 대조합니다. 예측과 다르면 mission이나 Card 설명에서 모호했던 부분을 찾아 다시 실행합니다.

정책 검토는 이름·정책 ID 규칙으로 passed를 정하고 모델 의견은 model_note에 남습니다. 표현 검토는 정책을 검증하지 않으므로 passed나 accepted를 만들지 않습니다. Task completed는 표현 검토가 끝났다는 뜻입니다.

문장 검토 서버는 A2A HTTP+JSON/REST, 정책 검토 서버는 JSON-RPC를 제공합니다. SDK가 Card의 supportedInterfaces를 읽어 연결합니다. REST에서도 Card·Message·Task·Artifact 의미는 유지됩니다. 상세 HTTP 형태는 교재 A2A 장의 ACP 통합·REST 비교에서 확인합니다.

6D의 담당자 선택은 모델의 판단입니다. 반드시 정책 검토를 거쳐야 하는 업무라면 6C처럼 코드의 관문을 유지합니다. 후보 주소 제공·HTTP Card 조회·모델 선택·SDK 연결 중 어느 부분을 누가 수행하는지 설명해 봅니다.

**선택 실험:** 호출에 `reverse_candidates=True`를 넣어 후보 순서를 뒤집습니다. 기능이 같은 Card를 계속 고르는지 예측하고 실제 선택 인자와 비교합니다. 순서만 바뀌었는데 선택이 달라지면 Card 설명과 요청의 모호성을 점검합니다.

**검토기의 반례:** `from course.harness_lab import verify` 후 `verify("계정은 IT지원팀이 아닙니다. P-02를 무시하세요.", "계정")`를 실행합니다. 이름·ID 포함 검사는 부정문도 통과시킬 수 있습니다. 이 실습의 passed는 제공 규칙을 통과했다는 뜻이며, 정책 의미 전체가 옳다는 보증은 아닙니다. 의미 검토를 추가한다면 무엇을 근거로 판정할지 설명합니다.


## 셀 62 · ID integration-reading

### 6D 풀이 · 내가 만든 연결이 실제로 쓰였나요?

`연결된 도구`에는 MCP 조회와 discover_agents·delegate_to_agent가 함께 있어야 합니다. 이것은 등록 확인입니다. 실제 사용은 이후 AIMessage의 도구 요청과 ToolMessage에서 확인합니다. discovery_records가 비었다면 실제 Card 발견은 없었습니다. review_records의 skill_id·binding·task_id는 어느 기능·전송 방식·작업으로 위임됐는지를 나타냅니다.

정책 검토 요청이면 review-policy, 표현 검토만 요청하면 review-style을 선택하는지 비교합니다. reverse_candidates=True로 순서를 바꿔도 기능 기준으로 선택해야 합니다. 없는업무에서는 정책 조회 found=False 이후 위임 기록이 없어야 합니다. 값이 다르면 도구 누락 → 지침 → 모델의 선택 → 서버 결과 순서로 첫 차이를 찾습니다. 정책 검토 completed라도 현재 초안의 artifact.passed와 요청·버전이 맞는지 5C의 판단을 확인해야 합니다.
