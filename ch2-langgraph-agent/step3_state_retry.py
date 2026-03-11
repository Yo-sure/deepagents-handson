"""
Chapter 2 - Step 3: 상태·재시도·중단 제어 직접 구현

LangGraph의 Checkpointer와 Human-in-the-Loop를 배웁니다.
- Checkpointer: 상태를 저장하여 대화 연속성 유지
- 조건부 재시도 로직
- interrupt(): 사람 승인 패턴
"""

import os
from typing import Literal, TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition
try:
    from langgraph.checkpoint.memory import InMemorySaver as Checkpointer
    CHECKPOINTER_NAME = "InMemorySaver"
except ImportError:
    from langgraph.checkpoint.memory import MemorySaver as Checkpointer
    CHECKPOINTER_NAME = "MemorySaver"

# ============================================================
# Part A: Checkpointer로 상태 저장
# ============================================================

print("=" * 60)
print("Part A: Checkpointer로 대화 상태 유지")
print("=" * 60)

@tool
def check_inbox(filter: str = "unread") -> str:
    """메일함의 메일 목록을 확인합니다."""
    mock_emails = [
        {"from": "팀장님", "subject": "긴급: 서버 점검 안내", "important": True},
        {"from": "HR팀", "subject": "연말 워크숍 일정", "important": False},
        {"from": "고객사", "subject": "프로젝트 미팅 요청", "important": True},
    ]
    if filter == "important":
        mock_emails = [e for e in mock_emails if e["important"]]
    result = f"📬 {filter} 메일 {len(mock_emails)}통:\n"
    for i, email in enumerate(mock_emails, 1):
        result += f"  {i}. [{email['from']}] {email['subject']}\n"
    return result


@tool
def get_email_detail(email_index: int) -> str:
    """특정 메일의 상세 내용을 가져옵니다."""
    details = {
        1: "팀장님: 내일 오후 2시부터 서버 점검 예정입니다. 작업 저장 바랍니다.",
        2: "HR팀: 12월 20일 연말 워크숍이 진행됩니다. 참석 여부를 회신해주세요.",
        3: "고객사: 다음 주 화요일 프로젝트 진행 상황 미팅 요청드립니다.",
    }
    return details.get(email_index, "해당 메일을 찾을 수 없습니다.")


tools = [check_inbox, get_email_detail]

if not os.environ.get("OPENROUTER_API_KEY"):
    print("⚠️ OPENROUTER_API_KEY가 설정되지 않았습니다.")
    print("   예: export OPENROUTER_API_KEY='sk-or-...'")
    raise SystemExit(0)

# OpenRouter 게이트웨이를 통해 Gemini 3 Flash Preview 사용
llm = ChatOpenAI(
    model="google/gemini-3-flash-preview",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    temperature=0,
)
llm_with_tools = llm.bind_tools(tools)


def call_model(state: MessagesState) -> dict:
    system = SystemMessage(content="당신은 메일 관리 비서입니다.")
    response = llm_with_tools.invoke([system] + state["messages"])
    return {"messages": [response]}


# 그래프 구성
builder = StateGraph(MessagesState)
builder.add_node("llm", call_model)
builder.add_node("tools", ToolNode(tools))
builder.add_edge(START, "llm")
builder.add_conditional_edges("llm", tools_condition)
builder.add_edge("tools", "llm")

# ★ Checkpointer 추가! - 상태를 메모리에 저장
checkpointer = Checkpointer()
graph = builder.compile(checkpointer=checkpointer)
print(f"[INFO] Checkpointer: {CHECKPOINTER_NAME}")

# thread_id로 대화 세션을 구분
config = {"configurable": {"thread_id": "session-001"}}

# 첫 번째 대화
print(f"\n--- 대화 1 [thread=session-001] ---")
try:
    q1 = "메일함 확인해줘"
    print(f"👤: {q1}")
    result1 = graph.invoke(
        {"messages": [HumanMessage(content=q1)]},
        config=config,
    )
    last_msg = result1["messages"][-1]
    print(f"🤖: {last_msg.content}")

    # 두 번째 대화 - 같은 thread_id이므로 이전 대화를 기억
    # ★ Tool로 답할 수 없는 메타 질문 → 대화 기억만으로 답해야 함
    q = "내가 이 대화에서 처음에 뭐라고 요청했어?"
    print(f"\n--- 대화 2 [thread=session-001] (이전 대화 기억) ---")
    print(f"👤: {q}")
    result2 = graph.invoke(
        {"messages": [HumanMessage(content=q)]},
        config=config,
    )
    last_msg = result2["messages"][-1]
    print(f"🤖: {last_msg.content}")

    # 다른 세션 - thread_id가 다르면 대화 기억이 없음
    print(f"\n--- 대화 3 [thread=session-002] (새 세션) ---")
    config_new = {"configurable": {"thread_id": "session-002"}}
    print(f"👤: {q}")
    result3 = graph.invoke(
        {"messages": [HumanMessage(content=q)]},
        config=config_new,
    )
    last_msg = result3["messages"][-1]
    print(f"🤖: {last_msg.content}")
except Exception as e:
    print(f"⚠️ Part A 실행 실패: {e}")
    print("   OPENROUTER_API_KEY/네트워크 설정을 확인한 뒤 다시 실행하세요.")

# ============================================================
# Part B: 조건부 재시도 로직
# ============================================================

print("\n\n" + "=" * 60)
print("Part B: 조건부 재시도 로직")
print("=" * 60)

class RetryState(MessagesState):
    retry_count: int
    max_retries: int


@tool
def unreliable_api_call(query: str) -> str:
    """불안정한 외부 API를 호출합니다. 데모를 위해 처음 2번은 실패합니다."""
    attempts = getattr(unreliable_api_call, "_attempts", 0) + 1
    unreliable_api_call._attempts = attempts

    if attempts < 3:
        raise Exception("API 타임아웃: 서버 응답 없음")
    return f"API 결과: '{query}'에 대한 응답입니다. (시도 {attempts}회)"


def call_model_with_retry(state: RetryState) -> dict:
    system = SystemMessage(
        content=(
            "당신은 메일 관리 비서입니다. "
            "문제를 해결할 때 unreliable_api_call 도구를 반드시 사용하세요. "
            "도구 실패 메시지를 받으면 재시도하고, 성공하면 최종 답변을 짧게 정리하세요."
        )
    )
    retry_llm = llm.bind_tools([unreliable_api_call])
    response = retry_llm.invoke([system] + state["messages"])
    # 노드 동작 출력
    if response.tool_calls:
        names = ", ".join(tc["name"] for tc in response.tool_calls)
        print(f"  [LLM] Tool 호출 결정: {names}")
    else:
        preview = response.content[:80]
        print(f"  [LLM] 최종 답변: {preview}")
    return {"messages": [response]}


def handle_tool_with_retry(state: RetryState) -> dict:
    """Tool 실행 시 에러가 나면 재시도 카운터를 증가"""
    from langchain_core.messages import ToolMessage

    last_msg = state["messages"][-1]
    results = []

    for tool_call in last_msg.tool_calls:
        try:
            tool_fn = {"unreliable_api_call": unreliable_api_call}[tool_call["name"]]
            result = tool_fn.invoke(tool_call["args"])
            results.append(ToolMessage(content=str(result), tool_call_id=tool_call["id"]))
            print(f"  [Tool] ✅ 성공: {str(result)[:60]}")
        except Exception as e:
            retry_count = state.get("retry_count", 0) + 1
            error_msg = f"❌ 에러 (시도 {retry_count}/{state.get('max_retries', 3)}): {e}"
            results.append(ToolMessage(
                content=error_msg,
                tool_call_id=tool_call["id"],
            ))
            print(f"  [Tool] {error_msg}")
            return {"messages": results, "retry_count": retry_count}

    return {"messages": results, "retry_count": 0}  # 성공 시 카운터 리셋


def should_retry(state: RetryState) -> Literal["llm", "__end__"]:
    """재시도 여부 판단"""
    retry_count = state.get("retry_count", 0)
    max_retries = state.get("max_retries", 3)

    if retry_count > 0 and retry_count < max_retries:
        print(f"  [분기] ↪ 재시도 {retry_count}/{max_retries} → LLM으로 되돌아감")
        return "llm"
    elif retry_count >= max_retries:
        print(f"  [분기] ❌ 최대 재시도 도달 ({max_retries}회) → END")
        return END
    print(f"  [분기] ✅ 성공 → LLM에게 결과 전달")
    return "llm"


# 재시도 그래프 구성
retry_builder = StateGraph(RetryState)
retry_builder.add_node("llm", call_model_with_retry)
retry_builder.add_node("tools", handle_tool_with_retry)
retry_builder.add_edge(START, "llm")
retry_builder.add_conditional_edges("llm", tools_condition)
retry_builder.add_conditional_edges("tools", should_retry, ["llm", END])
retry_graph = retry_builder.compile()

print("[실행] 재시도 데모 시작")
retry_msg = "외부 API를 사용해 서버 상태를 확인해줘"
print(f"👤 사용자 요청: {retry_msg}\n")
unreliable_api_call._attempts = 0
try:
    retry_result = retry_graph.invoke({
        "messages": [HumanMessage(content=retry_msg)],
        "retry_count": 0,
        "max_retries": 3,
    })
    retry_last = retry_result["messages"][-1]
    print(f"재시도 데모 최종 응답: {retry_last.content}")
    print(f"실제 Tool 호출 횟수: {unreliable_api_call._attempts}회")
except Exception as e:
    print(f"⚠️ Part B 실행 실패: {e}")
    print("   OPENROUTER_API_KEY/네트워크 설정을 확인한 뒤 다시 실행하세요.")

# ============================================================
# Part C: Human-in-the-Loop (interrupt)
# ============================================================

print("\n" + "=" * 60)
print("Part C: Human-in-the-Loop (interrupt 패턴)")
print("=" * 60)

from langgraph.types import interrupt, Command


@tool
def send_reply(to: str, message: str) -> str:
    """메일에 답장을 보냅니다. 보내기 전 사람의 승인이 필요합니다."""
    # ★ interrupt()로 실행을 중단하고 사람의 결정을 기다림
    decision = interrupt({
        "question": "이 메일을 보내시겠습니까?",
        "to": to,
        "message": message,
    })

    if decision == "approve":
        return f"✅ {to}에게 답장을 보냈습니다: {message}"
    else:
        return f"❌ 답장이 취소되었습니다."


hitl_tools = [send_reply]  # send_reply만 제공하여 interrupt 데모에 집중
llm_hitl = llm.bind_tools(hitl_tools)


def call_model_hitl(state: MessagesState) -> dict:
    system = SystemMessage(
        content=(
            "당신은 메일 관리 비서입니다. "
            "사용자가 답장을 요청하면 반드시 send_reply 도구를 즉시 호출하세요. "
            "추가 확인 질문 없이 바로 실행합니다."
        )
    )
    response = llm_hitl.invoke([system] + state["messages"])
    return {"messages": [response]}


builder_hitl = StateGraph(MessagesState)
builder_hitl.add_node("llm", call_model_hitl)
builder_hitl.add_node("tools", ToolNode([send_reply]))
builder_hitl.add_edge(START, "llm")
builder_hitl.add_conditional_edges("llm", tools_condition)
builder_hitl.add_edge("tools", "llm")

# Checkpointer 필수! (interrupt 상태를 저장해야 하므로)
hitl_graph = builder_hitl.compile(checkpointer=Checkpointer())

# interrupt/resume 데모 실행
hitl_config = {"configurable": {"thread_id": "hitl-001"}}

try:
    # Step 1: 실행 → interrupt()에서 멈춤
    hitl_msg = "팀장님께 확인했습니다 답장해줘"
    print(f"👤: {hitl_msg}")
    result = hitl_graph.invoke(
        {"messages": [HumanMessage(content=hitl_msg)]},
        config=hitl_config,
    )

    # interrupt 정보 확인
    interrupts = result.get("__interrupt__", [])
    if interrupts:
        print(f"⏸️  interrupt 발동! 중단 정보:")
        for intr in interrupts:
            print(f"   {intr.value}")
    else:
        print("⚠️  interrupt가 발동하지 않았습니다. LLM이 send_reply를 호출하지 않은 것 같습니다.")
        print(f"   마지막 메시지: {result['messages'][-1].content[:100]}")

    # Step 2: 사용자에게 직접 승인/거부를 입력받아 재개
    if interrupts:
        print()
        decision = input("👤 승인하시겠습니까? (approve / reject): ").strip()
        if not decision:
            decision = "approve"  # 빈 입력 시 기본값
        print(f"\n[재개] Command(resume=\"{decision}\") 전송")
        final = hitl_graph.invoke(
            Command(resume=decision),
            config=hitl_config,
        )
        last = final["messages"][-1]
        print(f"🤖: {last.content}")

except Exception as e:
    print(f"⚠️ Part C 실행 실패: {e}")
    print("   OPENROUTER_API_KEY/네트워크 설정을 확인한 뒤 다시 실행하세요.")

# Step 4에서 Long-Running Agent 패턴을 다룹니다.
