"""
Chapter 2 - Step 4: 간단한 Long-Running Agent

"이걸 직접 만들면 왜 어려운가?" 를 체험합니다.
- 컨텍스트 윈도우 한계 → 파일시스템에 상태 저장
- Planning → 작업 목록 수동 관리
- 진행 상황 추적을 직접 구현
- 핵심 교훈: "이걸 매번 직접 만들기 힘들다 → Ch3 DeepAgents가 해결!"
"""

import json
import os
import time
from pathlib import Path
from typing import TypedDict, Annotated, Literal
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

# ============================================================
# 시나리오: 메일 100통을 분석하여 보고서 작성
#
# 문제:
# - 메일 100통을 한 번에 컨텍스트에 넣을 수 없음
# - 여러 단계에 걸친 작업 (수집 → 분류 → 분석 → 보고서)
# - 중간에 실패하면 처음부터 다시?
# ============================================================

# 작업 디렉토리 — 스크립트 위치 기준 절대경로 (CWD에 의존하지 않음)
WORKDIR = Path(__file__).resolve().parent.parent / "workspace" / "ch2"
WORKDIR.mkdir(parents=True, exist_ok=True)
WORK_DIR = str(WORKDIR)  # os.path 호환용

# OpenRouter 게이트웨이를 통해 Gemini 3 Flash Preview 사용
llm = ChatOpenAI(
    model="google/gemini-3-flash-preview",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    temperature=0,
)

# ============================================================
# 1. 파일시스템 기반 Tool 정의 (컨텍스트 외부 저장)
# ============================================================

@tool
def save_to_file(filename: str, content: str) -> str:
    """분석 결과를 파일에 저장합니다. 컨텍스트 윈도우를 아끼기 위해 사용합니다.

    Args:
        filename: 저장할 파일명
        content: 저장할 내용
    """
    filepath = os.path.join(WORK_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return f"✅ '{filename}' 저장 완료 ({len(content)}자)"


@tool
def read_from_file(filename: str) -> str:
    """이전에 저장한 파일을 읽어옵니다.

    Args:
        filename: 읽을 파일명
    """
    filepath = os.path.join(WORK_DIR, filename)
    if not os.path.exists(filepath):
        return f"❌ '{filename}' 파일을 찾을 수 없습니다."
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


@tool
def fetch_emails(batch_start: int, batch_size: int = 10) -> str:
    """메일을 배치로 가져옵니다. 한 번에 모든 메일을 로드하지 않습니다.

    Args:
        batch_start: 시작 인덱스
        batch_size: 한 번에 가져올 메일 수
    """
    # 모킹: 100통의 메일
    categories = ["긴급", "일반", "마케팅", "내부공지"]
    senders = ["팀장님", "고객사A", "마케팅팀", "HR팀", "기술지원", "CEO"]

    emails = []
    for i in range(batch_start, min(batch_start + batch_size, 100)):
        import random
        random.seed(i)
        emails.append({
            "id": i + 1,
            "from": random.choice(senders),
            "subject": f"메일 #{i+1}: {random.choice(categories)} 관련 내용",
            "category": random.choice(categories),
            "length": random.randint(50, 500),
        })

    remaining = max(0, 100 - (batch_start + batch_size))
    return json.dumps({
        "emails": emails,
        "total": 100,
        "fetched": len(emails),
        "remaining": remaining,
    }, ensure_ascii=False, indent=2)


# ============================================================
# 2. TODO 관리 Tool (Planning 직접 구현)
# ============================================================

TODO_FILE = os.path.join(WORK_DIR, "todos.json")


@tool
def write_todos(todos: str) -> str:
    """작업 목록을 업데이트합니다. JSON 형식으로 전달하세요.

    Args:
        todos: JSON 배열 형식의 TODO 목록.
               각 항목은 {"task": "설명", "status": "pending|in_progress|completed"} 형태.
    """
    try:
        todo_list = json.loads(todos)
    except json.JSONDecodeError:
        return "❌ JSON 파싱 에러. 올바른 JSON 배열을 전달하세요."

    with open(TODO_FILE, "w", encoding="utf-8") as f:
        json.dump(todo_list, f, ensure_ascii=False, indent=2)

    pending = sum(1 for t in todo_list if t.get("status") == "pending")
    in_progress = sum(1 for t in todo_list if t.get("status") == "in_progress")
    completed = sum(1 for t in todo_list if t.get("status") == "completed")

    return f"📋 TODO 업데이트: {pending} 대기 / {in_progress} 진행중 / {completed} 완료"


@tool
def read_todos() -> str:
    """현재 작업 목록을 읽어옵니다."""
    if not os.path.exists(TODO_FILE):
        return "📋 작업 목록이 비어있습니다."
    with open(TODO_FILE, "r", encoding="utf-8") as f:
        todos = json.load(f)
    return json.dumps(todos, ensure_ascii=False, indent=2)


# ============================================================
# 3. LangGraph Agent 구성
# ============================================================

all_tools = [fetch_emails, save_to_file, read_from_file, write_todos, read_todos]
llm_with_tools = llm.bind_tools(all_tools)

SYSTEM_PROMPT = """당신은 메일 분석 Agent입니다.

목표: 메일 100통을 분석하여 카테고리별 요약 보고서를 작성하세요.

작업 방법:
1. 먼저 write_todos로 작업 계획을 세우세요.
2. fetch_emails로 메일을 배치(10통씩)로 가져오세요. 한 번에 모두 가져오지 마세요!
3. 각 배치의 분석 결과를 save_to_file로 파일에 저장하세요 (컨텍스트 절약).
4. 모든 배치를 처리한 후, read_from_file로 결과를 읽어 최종 보고서를 작성하세요.
5. 각 단계마다 write_todos로 진행 상황을 업데이트하세요.

주의: 컨텍스트 윈도우가 제한되어 있으므로, 중간 결과는 반드시 파일에 저장하세요."""


class LongRunningState(TypedDict):
    messages: Annotated[list, add_messages]
    iteration_count: int


MAX_ITERATIONS = 15  # 무한 루프 방지


def call_model(state: LongRunningState) -> dict:
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {
        "messages": [response],
        "iteration_count": state.get("iteration_count", 0) + 1,
    }


def should_continue(state: LongRunningState) -> Literal["tools", "__end__"]:
    """Tool 호출 여부 + 반복 횟수 체크"""
    if state.get("iteration_count", 0) >= MAX_ITERATIONS:
        print(f"\n⚠️ 최대 반복 횟수({MAX_ITERATIONS}) 도달 - 중단")
        return END
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END


builder = StateGraph(LongRunningState)
builder.add_node("llm", call_model)
builder.add_node("tools", ToolNode(all_tools))
builder.add_edge(START, "llm")
builder.add_conditional_edges("llm", should_continue, ["tools", END])
builder.add_edge("tools", "llm")

graph = builder.compile(checkpointer=MemorySaver())

# ============================================================
# 4. 실행
# ============================================================

print("=" * 60)
print("Step 4: Long-Running Agent 실행")
print("=" * 60)
print("(메일 100통 분석 - 배치 처리 + 파일 저장 + TODO 관리)\n")

config = {"configurable": {"thread_id": "long-running-001"}}

user_msg = ("메일 100통을 분석해서 카테고리별 요약 보고서를 만들어줘. "
            "먼저 계획을 세우고, 배치로 처리해. 이미 진행중이던 작업이 있다면 이어서 처리해.")
print(f"👤 사용자 요청: {user_msg}\n")

result = graph.invoke(
    {
        "messages": [HumanMessage(content=user_msg)],
        "iteration_count": 0,
    },
    config=config,
)

# 결과 출력
print("\n" + "=" * 60)
print("📊 최종 결과")
print("=" * 60)
last_msg = result["messages"][-1]
print(last_msg.content[:500])

# TODO 상태 확인
print("\n📋 최종 TODO 상태:")
if os.path.exists(TODO_FILE):
    with open(TODO_FILE, "r", encoding="utf-8") as f:
        todos = json.load(f)
    for todo in todos:
        status_icon = {"pending": "⬜", "in_progress": "🔄", "completed": "✅"}.get(
            todo.get("status", ""), "❓"
        )
        print(f"  {status_icon} {todo.get('task', 'N/A')} [{todo.get('status', 'N/A')}]")

# 생성된 파일 확인
print(f"\n📁 작업 디렉토리 ({WORK_DIR}):")
for f in os.listdir(WORK_DIR):
    size = os.path.getsize(os.path.join(WORK_DIR, f))
    print(f"  📄 {f} ({size} bytes)")

# Chapter 3에서 DeepAgents로 이 수동 구현을 대체합니다.
