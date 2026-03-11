"""
Chapter 2 - Step 2: Tool 호출 / 상태 관리 (LangGraph 기초)

LangGraph의 StateGraph로 Step 1의 수동 루프를 구조화합니다.
- StateGraph: Node + Edge 기반 그래프
- MessagesState: 메시지 상태 자동 관리
- ToolNode & tools_condition: 프리빌트 컴포넌트
"""

import os
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition

# ============================================================
# 1. Tool 정의 (Step 1과 동일)
# ============================================================

@tool
def check_inbox(filter: str = "unread") -> str:
    """메일함의 메일 목록을 확인합니다.

    Args:
        filter: 필터 조건 ("unread", "all", "important")
    """
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
    """특정 메일의 상세 내용을 가져옵니다.

    Args:
        email_index: 메일 번호 (1부터 시작)
    """
    details = {
        1: "팀장님: 내일 오후 2시부터 서버 점검 예정입니다. 작업 저장 바랍니다.",
        2: "HR팀: 12월 20일 연말 워크숍이 진행됩니다. 참석 여부를 회신해주세요.",
        3: "고객사: 다음 주 화요일 프로젝트 진행 상황 미팅 요청드립니다.",
    }
    return details.get(email_index, "해당 메일을 찾을 수 없습니다.")


# ============================================================
# 2. LLM 설정
# ============================================================

tools = [check_inbox, get_email_detail]
# OpenRouter 게이트웨이를 통해 Gemini 3 Flash Preview 사용
llm = ChatOpenAI(
    model="google/gemini-3-flash-preview",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    temperature=0,
)
llm_with_tools = llm.bind_tools(tools)

# ============================================================
# 3. LangGraph StateGraph 구성
# ============================================================

# Node 함수: LLM 호출
def call_model(state: MessagesState) -> dict:
    """LLM을 호출하는 노드"""
    # 시스템 프롬프트 + 현재까지의 메시지
    system = SystemMessage(content="당신은 메일 관리 비서입니다. Tool을 사용해 메일을 확인하고 요약해주세요.")
    response = llm_with_tools.invoke([system] + state["messages"])
    return {"messages": [response]}


# 그래프 빌더 생성
builder = StateGraph(MessagesState)

# 노드 추가
builder.add_node("llm", call_model)        # LLM 호출 노드
builder.add_node("tools", ToolNode(tools))  # Tool 실행 노드 (프리빌트)

# 엣지 정의
builder.add_edge(START, "llm")              # 시작 → LLM

# 조건부 엣지: LLM 응답에 tool_calls가 있으면 tools로, 없으면 END로
builder.add_conditional_edges("llm", tools_condition)

builder.add_edge("tools", "llm")            # Tool 결과 → LLM (다시 판단)

# 그래프 컴파일
graph = builder.compile()

# ============================================================
# 4. 그래프 실행
# ============================================================

print("=" * 60)
print("Step 2: LangGraph StateGraph로 Agent 실행")
print("=" * 60)

# 실행
user_msg = "중요한 메일 확인하고 요약해줘"
print(f"\n👤 사용자 요청: {user_msg}")

result = graph.invoke({
    "messages": [HumanMessage(content=user_msg)]
})

# 결과 출력
print("\n📨 대화 흐름:")
for msg in result["messages"]:
    role = type(msg).__name__
    if role == "HumanMessage":
        print(f"\n👤 사용자: {msg.content}")
    elif role == "AIMessage":
        if msg.tool_calls:
            for tc in msg.tool_calls:
                print(f"\n🤖 LLM → Tool 호출: {tc['name']}({tc['args']})")
        if msg.content:
            print(f"\n🤖 LLM: {msg.content}")
    elif role == "ToolMessage":
        print(f"\n🔧 Tool 결과: {msg.content[:100]}...")

# ============================================================
# 5. 그래프 시각화 (선택사항)
# ============================================================

# Step 3에서 Checkpointer, 재시도, Human-in-the-Loop를 추가합니다.
