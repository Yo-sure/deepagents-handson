"""
Chapter 2 - Step 1: 단일 Agent Loop (LangChain 기초)

LangChain으로 가장 간단한 Agent를 만들어봅니다.
- ChatModel + Tool 바인딩
- 기본적인 Tool Calling
"""

import os
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

# ============================================================
# 1. Tool 정의
# ============================================================

@tool
def check_inbox(filter: str = "unread") -> str:
    """메일함의 메일 목록을 확인합니다.

    Args:
        filter: 필터 조건 ("unread", "all", "important")
    """
    # 실제로는 IMAP 등으로 메일 서버에 접속하지만, 여기서는 모킹
    mock_emails = [
        {"from": "팀장님", "subject": "긴급: 서버 점검 안내", "important": True},
        {"from": "HR팀", "subject": "연말 워크숍 일정", "important": False},
        {"from": "고객사", "subject": "프로젝트 미팅 요청", "important": True},
    ]
    if filter == "important":
        mock_emails = [e for e in mock_emails if e["important"]]
    elif filter == "unread":
        pass  # 모두 미읽음으로 간주

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
# 2. LLM에 Tool 바인딩
# ============================================================

# OpenRouter 게이트웨이를 통해 Gemini 3 Flash Preview 사용
llm = ChatOpenAI(
    model="google/gemini-3-flash-preview",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    temperature=0,
)
tools = [check_inbox, get_email_detail]

# bind_tools: LLM이 Tool의 존재를 인식하고 호출할 수 있게 함
llm_with_tools = llm.bind_tools(tools)

# ============================================================
# 3. 단일 호출 (아직 Agent Loop 아님!)
# ============================================================

print("=" * 60)
print("Step 1-A: LLM에게 메일 확인 요청 (단일 호출)")
print("=" * 60)

user_msg = "내 메일함에 뭐가 왔는지 확인해줘"
print(f"\n👤 사용자 요청: {user_msg}")

response = llm_with_tools.invoke([
    SystemMessage(content="당신은 메일 관리 비서입니다. 사용자의 메일 관련 요청을 처리합니다."),
    HumanMessage(content=user_msg),
])

print(f"\nLLM 응답 타입: {type(response).__name__}")
print(f"내용: {response.content}")
print(f"Tool 호출: {response.tool_calls}")

# ============================================================
# 4. 수동 Agent Loop
# ============================================================

print("\n" + "=" * 60)
print("Step 1-B: 수동 Agent Loop (ReAct 패턴)")
print("=" * 60)


def run_simple_agent(user_message: str, max_iterations: int = 5):
    """가장 간단한 Agent Loop 구현"""

    print(f"\n👤 사용자 요청: {user_message}")

    # Tool을 이름으로 찾을 수 있는 딕셔너리
    tool_map = {t.name: t for t in tools}

    # 대화 기록 초기화
    messages = [
        SystemMessage(content="당신은 메일 관리 비서입니다. Tool을 사용해 메일을 확인하고 요약해주세요."),
        HumanMessage(content=user_message),
    ]

    for i in range(max_iterations):
        print(f"\n--- 반복 {i+1} ---")

        # 1) LLM 호출
        response = llm_with_tools.invoke(messages)
        messages.append(response)

        # 2) Tool 호출이 없으면 → 최종 답변
        if not response.tool_calls:
            print(f"✅ 최종 답변: {response.content}")
            return response.content

        # 3) Tool 호출 실행
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            print(f"🔧 Tool 호출: {tool_name}({tool_call['args']})")

            # Step 1은 방어 로직까지 수동으로 구현해야 함
            if tool_name not in tool_map:
                result = f"알 수 없는 Tool 요청: {tool_name}"
            else:
                try:
                    result = tool_map[tool_name].invoke(tool_call["args"])
                except Exception as e:
                    result = f"Tool 실행 실패: {e}"

            print(f"📋 결과: {result}")

            # Tool 결과를 대화 기록에 추가
            messages.append(ToolMessage(
                content=str(result),
                tool_call_id=tool_call["id"],
            ))

    return "최대 반복 횟수에 도달했습니다."


# Agent Loop 실행
result = run_simple_agent("중요한 메일만 확인하고, 첫 번째 메일 상세 내용도 알려줘")

# Step 2에서 LangGraph StateGraph로 이 수동 루프를 구조화합니다.
