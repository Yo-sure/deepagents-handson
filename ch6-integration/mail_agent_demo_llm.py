"""
Chapter 6 - 통합 데모 (LLM 버전): 메일 Agent End-to-End

Ch2~Ch5의 모든 요소를 하나의 LLM Agent로 통합합니다.
- Ch2 LangGraph: Agent Loop (LLM → Tool → LLM → ...)
- Ch4 Skills:    SKILL.md에서 절차적 지식을 시스템 프롬프트에 주입
- Ch4 MCP:       MCP 서버(mcp_mail_server.py)에서 메일 데이터 접근
- Ch5 A2A:       Notify Agent에게 httpx로 알림 요청

아키텍처:
  ┌──────────────────────────────────────────────┐
  │            LangGraph Agent (LLM)             │
  │                                              │
  │  System Prompt = Skill 지시사항              │
  │  Tools = MCP(메일) + A2A(알림)               │
  └────────┬─────────────────┬───────────────────┘
           │ stdio            │ HTTP (JSON-RPC)
  ┌────────▼────────┐  ┌─────▼──────────────┐
  │  MCP Mail Server │  │  Notify Agent      │
  │  (subprocess)    │  │  (:9502, 별도 실행) │
  └─────────────────┘  └────────────────────┘

실행 방법 (터미널 2개):
  # 터미널 1: Notify Agent
  uv run python3 ch5-a2a/notify_agent.py

  # 터미널 2: 통합 데모
  uv run python3 ch6-integration/mail_agent_demo_llm.py
"""

import os
import sys
import asyncio
import uuid
from pathlib import Path

import httpx
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition


# ============================================================
# 1. Skill 로딩 (Ch4 agent_with_mcp.py에서 재사용)
# ============================================================

def load_skill(skill_dir: str) -> dict:
    """Skill 디렉토리에서 SKILL.md를 읽어 파싱합니다."""
    skill_path = Path(skill_dir) / "SKILL.md"
    if not skill_path.exists():
        raise FileNotFoundError(f"SKILL.md를 찾을 수 없습니다: {skill_path}")

    content = skill_path.read_text(encoding="utf-8")
    instructions = content

    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            instructions = parts[2].strip()

    return {"instructions": instructions}


# ============================================================
# 2. A2A 알림 Tool (Ch5 check_agent.py의 notify_agent_via_a2a 기반)
# ============================================================
# LangChain @tool로 감싸서 LLM이 직접 호출할 수 있게 합니다.

NOTIFY_AGENT_URL = "http://localhost:9502"


@tool
async def notify_important_emails(summary: str) -> str:
    """Send alert for important emails via A2A to Notify Agent.

    중요 메일이 발견되었을 때 Notify Agent에게 알림을 전송합니다.
    summary에는 중요 메일 요약 텍스트를 넣어주세요.

    Args:
        summary: 중요 메일 요약 (예: "긴급 메일 3통: CEO 이사회 자료, 고객사 미팅, 보안 패치")
    """
    # A2A JSON-RPC 요청 구성 (Ch5에서 배운 구조)
    a2a_request = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": "message/send",
        "params": {
            "message": {
                "role": "user",
                "messageId": str(uuid.uuid4()),
                "parts": [{"kind": "text", "text": summary}],
            },
        },
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(f"{NOTIFY_AGENT_URL}/", json=a2a_request)
            result = response.json()

        state = result.get("result", {}).get("status", {}).get("state", "unknown")
        return f"알림 전송 완료 (Notify Agent 응답: {state})"
    except httpx.ConnectError:
        return "알림 전송 실패: Notify Agent(:9502)에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요."
    except Exception as e:
        return f"알림 전송 실패: {e}"


# ============================================================
# 3. 시스템 프롬프트 구성 (Skill + A2A 알림 지침 통합)
# ============================================================

def build_system_prompt(skill_instructions: str) -> str:
    """Skill 지시사항 + A2A 알림 규칙을 포함한 시스템 프롬프트를 구성합니다."""
    return f"""당신은 메일 관리 전문 에이전트입니다.

## 기본 역할
사용자의 메일 관련 요청을 처리합니다.
항상 한국어로 응답하며, 정중하고 명확하게 안내합니다.

## 활성화된 Skill: mail-check

아래는 당신이 따라야 할 작업 절차(Skill)입니다.

<skill>
{skill_instructions}
</skill>

## 추가 규칙: 알림 전송

위 Skill 절차 완료 후, 중요 메일이 1건 이상 발견되면:
1. `notify_important_emails` Tool을 호출하여 Notify Agent에게 알림을 보냅니다.
2. summary 파라미터에 중요 메일 요약을 넣습니다.
3. 알림 전송 결과를 최종 보고에 포함합니다.

## Tool 사용 규칙
- Skill에서 정의한 순서대로 Tool을 호출하세요.
- 한 번의 요청에서 Tool 호출은 최대 7회로 제한합니다.
- Tool 호출 결과를 바탕으로 Skill에서 정의한 형식으로 응답하세요.
"""


# ============================================================
# 4. LangGraph Agent 구성 및 실행
# ============================================================

async def run_integrated_agent():
    """Skills + MCP + A2A를 통합한 LLM Agent를 실행합니다."""

    print()
    print("=" * 60)
    print("  Chapter 6: 통합 데모 (LLM 버전)")
    print("  Skills(Ch4) + MCP(Ch4) + A2A(Ch5) + LangGraph(Ch2)")
    print("=" * 60)

    # ---- 4-1. Skill 로딩 ----
    print()
    print("[1] Skill 로딩")
    # Ch4의 mail_skill/SKILL.md를 그대로 사용
    code_dir = Path(__file__).parent.parent
    skill_dir = code_dir / "ch4-skills-mcp" / "mail_skill"
    skill = load_skill(str(skill_dir))
    print(f"    SKILL.md 로드 완료 ({len(skill['instructions'])}자)")

    # ---- 4-2. MCP 서버 연결 ----
    print()
    print("[2] MCP 서버 연결 (stdio, subprocess 자동 기동)")
    from langchain_mcp_adapters.client import MultiServerMCPClient

    mcp_server_path = code_dir / "ch4-skills-mcp" / "mcp_mail_server.py"
    client = MultiServerMCPClient({
        "mail": {
            "command": sys.executable,
            "args": [str(mcp_server_path)],
            "transport": "stdio",
        }
    })
    mcp_tools = await client.get_tools()
    print(f"    MCP Tools: {[t.name for t in mcp_tools]}")

    # ---- 4-3. 전체 Tool 목록 = MCP + A2A ----
    all_tools = mcp_tools + [notify_important_emails]
    print()
    print("[3] Agent 구성")
    print(f"    MCP Tools: {[t.name for t in mcp_tools]}")
    print(f"    A2A Tools: [notify_important_emails]")
    print(f"    총 {len(all_tools)}개 Tool")

    # ---- 4-4. LangGraph 구성 ----
    llm = ChatOpenAI(
        model="google/gemini-3-flash-preview",
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        temperature=0,
    )
    llm_with_tools = llm.bind_tools(all_tools)
    system_prompt = build_system_prompt(skill["instructions"])

    def call_model(state: MessagesState) -> dict:
        messages = [SystemMessage(content=system_prompt)] + state["messages"]
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    builder = StateGraph(MessagesState)
    builder.add_node("agent", call_model)
    builder.add_node("tools", ToolNode(all_tools))
    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", tools_condition)
    builder.add_edge("tools", "agent")
    graph = builder.compile()

    # ---- 4-5. 실행 ----
    user_query = "메일함 확인하고 중요한 메일 요약해줘. 중요 메일이 있으면 알림도 보내줘."

    print()
    print("=" * 60)
    print(f"[4] Agent 실행: \"{user_query}\"")
    print("=" * 60)
    print()

    result = await graph.ainvoke(
        {"messages": [HumanMessage(content=user_query)]},
    )

    # ---- 4-6. 실행 과정 출력 ----
    print("-" * 60)
    print("실행 과정:")
    print("-" * 60)

    tool_call_count = 0
    for msg in result["messages"]:
        role = type(msg).__name__

        if role == "HumanMessage":
            print(f"\n[사용자] {msg.content}")

        elif role == "AIMessage":
            if msg.tool_calls:
                for tc in msg.tool_calls:
                    tool_call_count += 1
                    # MCP Tool인지 A2A Tool인지 표시
                    tool_type = "A2A" if tc["name"] == "notify_important_emails" else "MCP"
                    print(f"\n[Agent → {tool_type} Tool #{tool_call_count}]"
                          f" {tc['name']}({tc['args']})")
            if msg.content:
                print(f"\n[Agent 응답]\n{msg.content}")

        elif role == "ToolMessage":
            raw = msg.content if isinstance(msg.content, str) else str(msg.content)
            preview = raw[:200].replace("\n", " ")
            print(f"\n[Tool 결과] {preview}...")

    # ---- 최종 결과 ----
    print()
    print("=" * 60)
    print("최종 보고:")
    print("=" * 60)

    final_messages = [
        m for m in result["messages"]
        if type(m).__name__ == "AIMessage" and m.content
    ]
    if final_messages:
        print(final_messages[-1].content)

    print(f"\n(총 Tool 호출: {tool_call_count}회)")

    return result


# ============================================================
# 5. 메인 실행
# ============================================================

if __name__ == "__main__":
    if not os.environ.get("OPENROUTER_API_KEY"):
        print("OPENROUTER_API_KEY 환경변수가 설정되지 않았습니다.")
        print("  export OPENROUTER_API_KEY='sk-or-...'")
        sys.exit(1)

    print()
    print("전제 조건:")
    print("  Notify Agent가 실행 중이어야 합니다:")
    print("    uv run python3 ch5-a2a/notify_agent.py")
    print()
    print("  (MCP 서버는 subprocess로 자동 기동됩니다)")
    print()

    asyncio.run(run_integrated_agent())
