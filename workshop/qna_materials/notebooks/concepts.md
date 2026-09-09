# 원본: notebooks/concepts.ipynb


## 셀 1 · ID concept-00

# 개념 코드 실행

각 절의 코드를 셀에서 실행합니다. 첫 환경 셀을 실행한 뒤 필요한 절로 이동합니다. 주 구현 과제는 build-agent.ipynb에서 진행합니다.

## 셀 2 · ID concept-01

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
print("실행 위치:", root)

from course.common import get_model
```

## 셀 3 · ID concept-02

## 도구 입력 조건

## 셀 4 · ID concept-03

```python
from typing import Literal
from pydantic import BaseModel, Field, ValidationError
from langchain.tools import tool


class TeamInput(BaseModel):
    topic: Literal["정산", "계정"] = Field(description="담당 팀을 찾을 업무명")


@tool(
    "lookup_team",
    description="정산 또는 계정 업무의 담당 팀을 찾습니다. 다른 업무는 지원하지 않습니다.",
    args_schema=TeamInput,
)
def find_team(topic: str) -> str:
    return {"정산": "재무지원팀", "계정": "IT지원팀"}[topic]


print(find_team.name)  # lookup_team
print(find_team.description)
print(find_team.args)
print(find_team.invoke({"topic": "정산"}))  # 재무지원팀

try:
    print(find_team.invoke({"topic": "휴가"}))
except ValidationError:
    print("입력 오류: 정산 또는 계정만 조회할 수 있습니다.")
```

## 셀 5 · ID concept-04

## 도구의 content와 artifact

## 셀 6 · ID concept-05

```python
"""모델에 보낼 내용과 프로그램이 사용할 원본을 나눕니다."""
from langchain.tools import tool


@tool(response_format="content_and_artifact")
def lookup_record() -> tuple[str, dict]:
    """정산 담당 팀과 정책 원본을 조회합니다."""
    return "정산 담당은 재무지원팀입니다.", {"id": "P-01", "team": "재무지원팀"}


message = lookup_record.invoke(
    {"name": "lookup_record", "args": {}, "id": "call_1", "type": "tool_call"}
)
print(message.content)
print(message.artifact)
```

## 셀 7 · ID concept-06

## State의 교체와 누적

앞의 `visited`를 같은 `lookup → draft` 경로에서 비교합니다. State 선언과 노드 반환값 중 하나만 바꾸면 기록이 사라지거나 중복됩니다. 네 출력의 차이를 예상한 뒤 실행합니다.


## 셀 8 · ID concept-07

```python
"""같은 visited 필드의 교체·누적을 실제 그래프로 비교합니다. 모델 호출은 없습니다."""
from operator import add
from typing import Annotated, TypedDict
from langchain.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages


class ReplaceState(TypedDict):
    visited: list[str]


class AppendState(TypedDict):
    visited: Annotated[list[str], add]


def compare_visits(schema, return_full_history):
    def lookup(state):
        return {"visited": ["lookup"]}

    def draft(state):
        if return_full_history:
            return {"visited": state["visited"] + ["draft"]}
        return {"visited": ["draft"]}

    graph = StateGraph(schema)
    graph.add_node("lookup", lookup)
    graph.add_node("draft", draft)
    graph.add_edge(START, "lookup")
    graph.add_edge("lookup", "draft")
    graph.add_edge("draft", END)
    return graph.compile().invoke({"visited": []})["visited"]


cases = [
    ("교체 + 전체 목록", ReplaceState, True, ["lookup", "draft"]),
    ("add + 새 항목", AppendState, False, ["lookup", "draft"]),
    ("교체 + 새 항목: 기록 소실", ReplaceState, False, ["draft"]),
    ("add + 전체 목록: 중복", AppendState, True, ["lookup", "lookup", "draft"]),
]
for label, schema, full_history, expected in cases:
    observed = compare_visits(schema, full_history)
    print(label, "→", observed)
    assert observed == expected

messages = [HumanMessage(content="계정 담당 팀은?", id="q1")]
messages = add_messages(messages, [AIMessage(content="지원팀입니다.", id="a1")])
# 검토자가 기존 답변을 수정하여 같은 ID로 전달합니다.
messages = add_messages(messages, [AIMessage(content="IT지원팀입니다.", id="a1")])
print([(m.id, m.content) for m in messages])
# 스트리밍 호출 없이 만든 두 조각으로 누적과 교체를 비교합니다.
from langchain.messages import AIMessageChunk

first_chunk = AIMessageChunk(content="IT", id="stream-1")
next_chunk = AIMessageChunk(content="지원팀입니다.", id="stream-1")
combined = first_chunk + next_chunk
print("청크 합산:", combined.content)
assert combined.content == "IT지원팀입니다."

history = add_messages([], [first_chunk])
history = add_messages(history, [next_chunk])
print("같은 ID로 이력 갱신:", history[0].content)
assert len(history) == 1 and history[0].content == "지원팀입니다."
# 전체 답변을 반영하려면 먼저 누적한 결과를 전달합니다.
history = add_messages(history, [combined])
assert history[0].content == "IT지원팀입니다."

```

## 셀 9 · ID concept-08

## 중단과 재개

첫 셀로 그래프를 준비하고 두 번째 셀에서 중단합니다. 승인 요청을 읽은 뒤 세 번째 셀의 decision을 approve 또는 reject로 정해 실행합니다. 다시 비교하려면 준비 셀부터 실행합니다.

## 셀 10 · ID concept-09

```python
from langgraph.graph import StateGraph, START, END
from course.graph_lab import InquiryState, review
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

graph = StateGraph(InquiryState)
graph.add_node("review", review)
graph.add_edge(START, "review")
graph.add_edge("review", END)
app = graph.compile(checkpointer=InMemorySaver())
config = {"configurable": {"thread_id": "approval-example"}}
```

## 셀 11 · ID concept-10

```python
paused = app.invoke({"answer": "재무지원팀에 정산 문의를 전달합니다."}, config)
print(paused["__interrupt__"][0].value)
```

## 셀 12 · ID concept-11

```python
decision = "approve"
assert decision in {"approve", "reject"}
resumed = app.invoke(Command(resume=decision), config)
print(resumed["decision"])
print(app.get_state(config).next)
```

## 셀 13 · ID dda16aa1

## Skill · 문서 확인과 실제 사용 확인

공통 실습에서는 맨 위 환경 셀을 실행한 뒤, 아래 두 코드 셀로 문서와 실제 사용 기록을 확인합니다. 첫 셀은 모델 없이 skills/policy-answer/SKILL.md를 읽습니다. 다음 모델 셀은 제공된 문서를 그대로 사용해 없는업무의 답변과 문서 읽기 기록을 보여 줍니다. 다른 개념 셀을 전부 실행할 필요는 없습니다. API 키가 필요하며 모델 셀을 실행할 때마다 호출 비용이 발생합니다.


## 셀 14 · ID 352c9953

```python
skill_path = root / "skills" / "policy-answer" / "SKILL.md"
print(skill_path.read_text(encoding="utf-8"))
```

## 셀 15 · ID 521ec837

**공통 완료 기준:** 아래 셀에서 문서 읽기 도구의 요청·결과와 답변을 함께 확인합니다. 좋은 답변만으로 Skill 사용을 추정하지 않습니다.

**선택 비교:** 먼저 아래 셀을 실행하고 수정 전 답변과 read_file 기록을 메모에 복사합니다. 그다음 Jupyter 파일 탐색기 상단 경로 맨 왼쪽의 폴더 아이콘을 눌러 최상위로 이동하고 skills → policy-answer → SKILL.md를 열어, 규정이 없을 때 업무명을 다시 묻도록 절차 한 줄을 구체화하고 저장합니다. topic을 그대로 두고 아래 모델 셀을 다시 실행하여 수정 전후를 비교합니다. 정산·계정 입력 비교는 그 뒤에 진행합니다. 끝나면 바꾼 문장을 원래대로 복원하고 저장합니다.


## 셀 16 · ID 450fd074

```python
from course.harness_lab import run_deep_agent

topic = "없는업무"  # 정산·계정도 비교합니다.
observed = run_deep_agent(topic, model=get_model())
print(json.dumps(observed, ensure_ascii=False, indent=2))
```

## 셀 17 · ID 7a6e4288

## 그래프 경로 비교

모델 호출이 없습니다. 두 입력의 visited가 lookup→draft, lookup→ask인지 비교합니다.

## 셀 18 · ID 88e39c6a

```python
from course.graph_lab import build_graph

app = build_graph()
for contact in ["user@example.test", ""]:
    print(app.invoke({"topic": "정산", "contact": contact}))
```

## 셀 19 · ID response-lab-title

## 모델 응답과 토큰 비교

선택 실습입니다. 맨 위 환경 확인 셀을 먼저 실행합니다. 아래 코드 셀은 각각 실제 모델을 한 번 호출하므로 키 설정이 필요합니다. 먼저 한 문장 지시문의 결과를 확인합니다.

## 셀 20 · ID response-lab-short

```python
from course.common import get_model
from langchain.messages import SystemMessage, HumanMessage

model = get_model()
question = "LangChain은 무엇인가요?"
short_response = model.invoke([
    SystemMessage(content="한국어로 한 문장만 답합니다."),
    HumanMessage(content=question),
])
print("답변:", short_response.content)
print("토큰 사용량:", short_response.usage_metadata)
print("종료 이유:", short_response.response_metadata.get("finish_reason"))

```

## 셀 21 · ID response-lab-compare

첫 코드 셀이 성공한 뒤 다음 셀을 실행합니다. 질문을 유지하고 지시문만 다섯 문장으로 바꿉니다. 두 응답의 내용·입력 토큰·출력 토큰·종료 이유를 비교합니다. 특정 숫자나 토큰 증가를 정답으로 요구하지 않습니다. 사용량이 None이면 미제공이며 0이 아닙니다.

## 셀 22 · ID response-lab-long

```python
long_response = model.invoke([
    SystemMessage(content="한국어로 다섯 문장 답합니다."),
    HumanMessage(content=question),
])
for label, response in [("한 문장 지시", short_response), ("다섯 문장 지시", long_response)]:
    print(label)
    print("답변:", response.content)
    print("토큰 사용량:", response.usage_metadata)
    print("종료 이유:", response.response_metadata.get("finish_reason"))
    print()

```