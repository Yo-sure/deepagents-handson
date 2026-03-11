"""
Chapter 4 - Agent + Skills + MCP 통합: 완성된 메일 에이전트

이 파일은 Skills(절차적 지식)과 MCP(데이터 접근)를 결합하여
완성된 메일 관리 에이전트를 구현합니다.

아키텍처:
  ┌─────────────────────────────────────────────────┐
  │                    Agent                         │
  │                                                  │
  │  ┌──────────────┐       ┌─────────────────────┐ │
  │  │   Skill      │       │    MCP Client        │ │
  │  │  (SKILL.md)  │       │  (langchain-mcp)     │ │
  │  │              │       │                      │ │
  │  │ "어떻게"     │       │   "무엇을"            │ │
  │  │ 해야 하는가  │       │   할 수 있는가        │ │
  │  └──────────────┘       └──────────┬──────────┘ │
  │                                     │            │
  └─────────────────────────────────────┼────────────┘
                                        │ stdio
                              ┌─────────▼──────────┐
                              │   MCP Server        │
                              │ (mcp_mail_server.py)│
                              │                     │
                              │ check_inbox         │
                              │ get_email_detail    │
                              │ search_emails       │
                              └─────────────────────┘

핵심 개념:
  - Skill은 Agent에게 "절차"를 가르침 (system prompt에 주입)
  - MCP Tool은 Agent에게 "능력"을 부여 (실행 가능한 함수)
  - Agent는 Skill의 절차에 따라 MCP Tool을 선택적으로 호출

실행 방법:
  uv run python3 agent_with_mcp.py

  순서:
    Step A: Skill + 로컬 Tool (MCP 없이) — Skill 역할 먼저 확인
    Step B: Skill + MCP Server (완성) — 같은 Skill, Tool만 MCP로 교체

필요 패키지:
  pip install langchain-openai langchain-mcp-adapters mcp langgraph
"""

import os
import sys
import asyncio
from pathlib import Path

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition

# ============================================================
# 1. Skill 로딩: SKILL.md에서 절차적 지식을 읽어옵니다
# ============================================================
# Skill은 Agent의 행동 방침을 정의하는 마크다운 문서입니다.
# YAML frontmatter에는 메타데이터가, 본문에는 지시사항이 담겨 있습니다.


def load_skill(skill_dir: str) -> dict:
    """Skill 디렉토리에서 SKILL.md를 읽어 파싱합니다.

    Args:
        skill_dir: SKILL.md가 위치한 디렉토리 경로

    Returns:
        dict with keys:
          - "name": Skill 이름
          - "description": 설명
          - "instructions": 본문 지시사항 (마크다운)
          - "metadata": YAML frontmatter의 메타데이터
    """
    skill_path = Path(skill_dir) / "SKILL.md"

    if not skill_path.exists():
        raise FileNotFoundError(f"SKILL.md를 찾을 수 없습니다: {skill_path}")

    content = skill_path.read_text(encoding="utf-8")

    # YAML frontmatter 파싱 (--- 로 구분)
    metadata = {}
    instructions = content

    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            frontmatter_text = parts[1].strip()
            instructions = parts[2].strip()
            metadata = _parse_frontmatter(frontmatter_text)

    return {
        "name": metadata.get("name", "unknown"),
        "description": metadata.get("description", ""),
        "instructions": instructions,
        "metadata": metadata,
    }


def _parse_frontmatter(frontmatter_text: str) -> dict:
    """SKILL.md frontmatter를 최소 기능으로 파싱합니다.

    지원 범위:
    - key: value
    - key: > / key: | 블록 스칼라
    - key: 아래 중첩 key-value (1 depth)
    """
    metadata: dict = {}
    lines = frontmatter_text.splitlines()
    i = 0

    def strip_quotes(value: str) -> str:
        return value.strip().strip('"').strip("'")

    while i < len(lines):
        raw = lines[i]
        line = raw.rstrip()
        stripped = line.strip()

        if not stripped or stripped.startswith("#"):
            i += 1
            continue

        # 최상위 key만 처리 (들여쓰기 라인은 상위에서 소비)
        if line.startswith(" "):
            i += 1
            continue

        if ":" not in stripped:
            i += 1
            continue

        key, _, value = stripped.partition(":")
        key = key.strip()
        value = value.strip()

        # block scalar (description: >)
        if value in {">", "|", ">-", "|-"}:
            block_lines: list[str] = []
            i += 1
            while i < len(lines):
                next_line = lines[i]
                if next_line.startswith("  ") or not next_line.strip():
                    if next_line.strip():
                        block_lines.append(next_line.strip())
                    else:
                        block_lines.append("")
                    i += 1
                else:
                    break
            if value.startswith(">"):
                metadata[key] = " ".join(s for s in block_lines if s).strip()
            else:
                metadata[key] = "\n".join(block_lines).strip()
            continue

        # nested block (metadata:)
        if value == "":
            nested: dict = {}
            i += 1
            while i < len(lines):
                next_line = lines[i]
                if not next_line.strip():
                    i += 1
                    continue
                if not next_line.startswith("  "):
                    break
                nested_line = next_line.strip()
                if ":" in nested_line:
                    nkey, _, nvalue = nested_line.partition(":")
                    nested[nkey.strip()] = strip_quotes(nvalue)
                i += 1
            metadata[key] = nested
            continue

        metadata[key] = strip_quotes(value)
        i += 1

    return metadata


# ============================================================
# 2. System Prompt 구성: Skill 지시사항을 프롬프트에 통합
# ============================================================


def build_system_prompt(skill: dict) -> str:
    """Skill 정보를 포함한 시스템 프롬프트를 구성합니다.

    Agent의 행동 지침 = 기본 역할 + Skill 지시사항 + Tool 사용 가이드
    """
    return f"""당신은 메일 관리 전문 에이전트입니다.

## 기본 역할
사용자의 메일 관련 요청을 처리합니다.
항상 한국어로 응답하며, 정중하고 명확하게 안내합니다.

## 활성화된 Skill: {skill['name']}

아래는 당신이 따라야 할 작업 절차(Skill)입니다.
이 절차에 정의된 순서와 판단 기준을 반드시 준수하세요.

<skill>
{skill['instructions']}
</skill>

## Tool 사용 규칙
- 반드시 Skill에서 정의한 순서대로 Tool을 호출하세요.
- 한 번의 요청에서 Tool 호출은 최대 5회로 제한합니다.
- Tool 호출 결과를 바탕으로 Skill에서 정의한 형식으로 응답하세요.
"""


# ============================================================
# 3. MCP 연결 및 Agent 구성 (메인 로직)
# ============================================================


async def run_mail_agent(user_query: str):
    """MCP 서버에 연결하고 메일 에이전트를 실행합니다.

    Args:
        user_query: 사용자의 메일 관련 요청
    """
    # langchain_mcp_adapters를 사용해 MCP 서버에 연결합니다.
    # MultiServerMCPClient는 여러 MCP 서버를 동시에 연결할 수 있습니다.
    from langchain_mcp_adapters.client import MultiServerMCPClient

    # ----------------------------------------------------------
    # 3-1. Skill 로딩
    # ----------------------------------------------------------
    print("=" * 60)
    print("[1단계] Skill 로딩")
    print("=" * 60)

    # 현재 파일 기준으로 mail_skill 디렉토리를 찾습니다
    current_dir = Path(__file__).parent
    skill_dir = current_dir / "mail_skill"

    skill = load_skill(str(skill_dir))
    print(f"  Skill 이름: {skill['name']}")
    print(f"  Skill 설명: {skill['description'][:60]}...")
    print(f"  지시사항 길이: {len(skill['instructions'])}자")
    print()

    # ----------------------------------------------------------
    # 3-2. MCP 서버 연결
    # ----------------------------------------------------------
    print("=" * 60)
    print("[2단계] MCP 서버 연결")
    print("=" * 60)

    # MCP 서버 설정: 어떤 서버에 어떻게 연결할지 정의합니다
    mcp_server_config = {
        "mail": {
            # stdio transport: subprocess로 MCP 서버를 실행합니다
            "command": sys.executable,
            "args": [str(current_dir / "mcp_mail_server.py")],
            "transport": "stdio",
        }
        # 여러 MCP 서버를 동시에 연결할 수 있습니다:
        # "calendar": {
        #     "command": "python",
        #     "args": ["mcp_calendar_server.py"],
        #     "transport": "stdio",
        # },
        # "slack": {
        #     "url": "http://localhost:8080/mcp",
        #     "transport": "streamable_http",
        # },
    }

    # langchain-mcp-adapters 0.1.0+ 에서는 컨텍스트 매니저가 제거되었습니다.
    # client = MultiServerMCPClient(config) → await client.get_tools()
    client = MultiServerMCPClient(mcp_server_config)
    mcp_tools = await client.get_tools()

    print(f"  연결된 MCP 서버: mail")
    print(f"  사용 가능한 Tool 수: {len(mcp_tools)}")
    for tool in mcp_tools:
        print(f"    - {tool.name}: {tool.description[:50]}...")
    print()

    # ----------------------------------------------------------
    # 3-3. LangGraph Agent 구성
    # ----------------------------------------------------------
    print("=" * 60)
    print("[3단계] Agent 구성 (LangGraph + Skill + MCP Tools)")
    print("=" * 60)

    # LLM 설정
    # OpenRouter 게이트웨이를 통해 Gemini 3 Flash Preview 사용
    llm = ChatOpenAI(
        model="google/gemini-3-flash-preview",
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        temperature=0,
    )
    llm_with_tools = llm.bind_tools(mcp_tools)

    # Skill에서 구성한 시스템 프롬프트
    system_prompt = build_system_prompt(skill)
    print(f"  시스템 프롬프트 길이: {len(system_prompt)}자")
    print(f"  바인딩된 Tool 수: {len(mcp_tools)}")
    print()

    # LangGraph 노드 함수: LLM 호출
    def call_model(state: MessagesState) -> dict:
        """Skill 지시사항이 포함된 프롬프트로 LLM을 호출합니다."""
        messages = [SystemMessage(content=system_prompt)] + state["messages"]
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    # LangGraph 그래프 구성
    builder = StateGraph(MessagesState)
    builder.add_node("agent", call_model)
    builder.add_node("tools", ToolNode(mcp_tools))  # MCP Tool 실행 노드
    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", tools_condition)
    builder.add_edge("tools", "agent")
    graph = builder.compile()

    print("  그래프 구성 완료:")
    print("    START -> agent -> (tool_calls?) -> tools -> agent -> ... -> END")
    print()

    # ----------------------------------------------------------
    # 3-4. Agent 실행
    # ----------------------------------------------------------
    print("=" * 60)
    print(f"[4단계] Agent 실행: \"{user_query}\"")
    print("=" * 60)
    print()

    # MCP Tool은 async 전용이므로 ainvoke를 사용해야 합니다
    result = await graph.ainvoke(
        {"messages": [HumanMessage(content=user_query)]},
    )

    # ----------------------------------------------------------
    # 3-5. 실행 과정 출력
    # ----------------------------------------------------------
    print("-" * 60)
    print("실행 과정 (대화 흐름):")
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
                    print(f"\n[Agent -> Tool 호출 #{tool_call_count}]"
                          f" {tc['name']}({tc['args']})")
            if msg.content:
                print(f"\n[Agent 응답]\n{msg.content}")

        elif role == "ToolMessage":
            # Tool 결과는 길 수 있으므로 미리보기만 표시
            # MCP Tool은 content가 list[dict]로 올 수 있음
            raw = msg.content if isinstance(msg.content, str) else str(msg.content)
            preview = raw[:150].replace("\n", " ")
            print(f"\n[Tool 결과] {preview}...")

    # ----------------------------------------------------------
    # 최종 결과
    # ----------------------------------------------------------
    print("\n" + "=" * 60)
    print("최종 응답:")
    print("=" * 60)

    # 마지막 AI 메시지가 최종 응답입니다
    final_messages = [
        m for m in result["messages"]
        if type(m).__name__ == "AIMessage" and m.content
    ]
    if final_messages:
        print(final_messages[-1].content)

    print(f"\n(총 Tool 호출 횟수: {tool_call_count})")

    return result


# ============================================================
# 4. 실행 예시
# ============================================================


async def main():
    """다양한 시나리오로 메일 에이전트를 실행합니다."""

    print("\n")
    print("#" * 60)
    print("#  Chapter 4: Skills + MCP 통합 메일 에이전트")
    print("#" * 60)
    print()
    print("이 예제는 다음을 보여줍니다:")
    print("  1. SKILL.md에서 절차적 지식(Skill)을 로딩")
    print("  2. MCP 서버에서 데이터 접근 기능(Tool)을 연결")
    print("  3. Agent가 Skill의 절차에 따라 Tool을 호출하여 작업 수행")
    print()

    # ---- 시나리오 1: 메일 확인 및 요약 ----
    print()
    print("*" * 60)
    print("* 시나리오 1: 메일 확인 및 요약")
    print("*" * 60)
    await run_mail_agent("오늘 온 메일 확인하고 중요한 것 위주로 요약해줘")

    # ---- 시나리오 2: 특정 메일 검색 ----
    print("\n\n")
    print("*" * 60)
    print("* 시나리오 2: 메일 검색")
    print("*" * 60)
    await run_mail_agent("고객사에서 온 메일 찾아서 자세한 내용 알려줘")


# ============================================================
# 5. MCP 없이 실행할 수 있는 데모 모드 (Fallback)
# ============================================================
# MCP 서버 연결이 실패할 경우를 대비한 단독 데모 모드입니다.
# 이 모드에서는 MCP 대신 LangChain @tool을 직접 사용합니다.


def run_demo_without_mcp():
    """MCP 없이 Skill만 사용하는 간이 데모.

    MCP 연결 없이도 Skill의 개념을 이해할 수 있도록
    로컬 Tool로 동일한 동작을 시연합니다.
    """
    from langchain_core.tools import tool

    print("\n")
    print("#" * 60)
    print("#  [Step A] Skill + 로컬 Tool (MCP 없이)")
    print("#  SKILL.md가 절차를 안내, Agent가 로컬 Tool 호출")
    print("#" * 60)
    print()

    # Skill 로딩
    current_dir = Path(__file__).parent
    skill = load_skill(str(current_dir / "mail_skill"))

    print(f"로딩된 Skill: {skill['name']}")
    print(f"설명: {skill['description']}")
    print()

    # 로컬 Tool 정의 (MCP Tool과 동일한 기능)
    @tool
    def check_inbox(filter: str = "unread") -> str:
        """메일함의 메일 목록을 확인합니다."""
        mock_emails = [
            {"id": 1, "from": "김팀장", "subject": "긴급: 서버 점검 안내", "important": True},
            {"id": 2, "from": "HR팀", "subject": "연말 워크숍 일정", "important": False},
            {"id": 3, "from": "박대리(고객사)", "subject": "프로젝트 미팅 요청", "important": True},
            {"id": 4, "from": "DevOps Bot", "subject": "[CI/CD] 빌드 성공", "important": False},
            {"id": 5, "from": "이부장", "subject": "ASAP: 고객 보고서 검토", "important": True},
        ]
        if filter == "important":
            mock_emails = [e for e in mock_emails if e["important"]]
        elif filter == "unread":
            mock_emails = [e for e in mock_emails if e["id"] != 4]  # 4번만 읽음

        result = f"메일함 ({filter}) - {len(mock_emails)}통:\n"
        for e in mock_emails:
            mark = "[중요] " if e["important"] else ""
            result += f"  ID:{e['id']} {mark}{e['from']} - {e['subject']}\n"
        return result

    @tool
    def get_email_detail(email_id: int) -> str:
        """특정 메일의 상세 내용을 반환합니다."""
        details = {
            1: "내일 오후 2시부터 서버 점검 예정. 작업 저장 필수.",
            2: "12월 20일 연말 워크숍. 참석 여부 회신 요망.",
            3: "다음 주 화요일 프로젝트 미팅 요청. 안건: Q1 마일스톤 리뷰.",
            4: "main 브랜치 빌드 #1247 성공. staging 배포 완료.",
            5: "고객 보고서 오늘 중 검토 요청. 내일 오전 미팅 전 최종본 필요.",
        }
        return details.get(email_id, "해당 메일을 찾을 수 없습니다.")

    @tool
    def search_emails(query: str) -> str:
        """메일을 검색합니다."""
        return f"'{query}' 검색 결과: ID:3 박대리(고객사) - 프로젝트 미팅 요청"

    # LangGraph Agent 구성
    tools = [check_inbox, get_email_detail, search_emails]
    # OpenRouter 게이트웨이를 통해 Gemini 3 Flash Preview 사용
    llm = ChatOpenAI(
        model="google/gemini-3-flash-preview",
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        temperature=0,
    )
    llm_with_tools = llm.bind_tools(tools)

    system_prompt = build_system_prompt(skill)

    def call_model(state: MessagesState) -> dict:
        messages = [SystemMessage(content=system_prompt)] + state["messages"]
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    builder = StateGraph(MessagesState)
    builder.add_node("agent", call_model)
    builder.add_node("tools", ToolNode(tools))
    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", tools_condition)
    builder.add_edge("tools", "agent")
    graph = builder.compile()

    # 실행
    print("=" * 60)
    print("데모 실행: \"중요한 메일 확인하고 요약해줘\"")
    print("=" * 60)
    print()

    result = graph.invoke({
        "messages": [HumanMessage(content="중요한 메일 확인하고 요약해줘")]
    })

    # 결과 출력
    print("실행 과정:")
    print("-" * 60)
    for msg in result["messages"]:
        role = type(msg).__name__
        if role == "HumanMessage":
            print(f"\n[사용자] {msg.content}")
        elif role == "AIMessage":
            if msg.tool_calls:
                for tc in msg.tool_calls:
                    print(f"\n[Agent -> Tool] {tc['name']}({tc['args']})")
            if msg.content:
                print(f"\n[Agent 최종 응답]\n{msg.content}")
        elif role == "ToolMessage":
            preview = msg.content[:120].replace("\n", " ")
            print(f"\n[Tool 결과] {preview}...")

    return result


# ============================================================
# 6. 엔트리포인트
# ============================================================

if __name__ == "__main__":
    # 환경변수에 OPENROUTER_API_KEY가 설정되어 있는지 확인
    if not os.environ.get("OPENROUTER_API_KEY"):
        print("경고: OPENROUTER_API_KEY 환경변수가 설정되지 않았습니다.")
        print("  export OPENROUTER_API_KEY='sk-or-...'")
        print()

    # ── Step A: Skill + 로컬 Tool (MCP 없이) ──
    # Skill이 절차를 안내하고, Agent가 로컬 Tool을 호출하는 단계.
    # MCP 없이도 Skill의 역할을 먼저 확인합니다.
    run_demo_without_mcp()

    # ── Step B: Skill + MCP Server (완성) ──
    # 같은 Skill인데 Tool 제공 방식만 MCP로 교체합니다.
    # Skill 코드는 그대로, Tool만 외부 프로세스(MCP 서버)에서 제공.
    print("\n\n")
    print("#" * 60)
    print("#  [Step B] Skill + MCP Server (완성)")
    print("#  Skill은 동일, Tool만 로컬→MCP로 교체")
    print("#" * 60)
    asyncio.run(main())


# ============================================================
# 핵심 정리
# ============================================================
#
# Skill + MCP의 분리가 중요한 이유:
#
# 1. Skill (SKILL.md) = 절차적 지식 (Procedural Knowledge)
#    - "어떤 순서로 작업할 것인가"
#    - "어떤 기준으로 판단할 것인가"
#    - "결과를 어떤 형식으로 보고할 것인가"
#    -> system prompt에 주입되어 Agent의 "행동 방침"이 됨
#
# 2. MCP Tool = 데이터 접근 능력 (Capability)
#    - "메일함을 읽을 수 있다"
#    - "메일을 검색할 수 있다"
#    - "메일 상세 내용을 조회할 수 있다"
#    -> Tool로 바인딩되어 Agent의 "실행 가능한 기능"이 됨
#
# 3. 분리의 장점:
#    - Skill 교체: 같은 MCP Tool로 다른 절차 적용 가능
#      (예: "메일 요약" Skill -> "메일 분류" Skill)
#    - MCP 서버 교체: 같은 Skill로 다른 데이터 소스 연결 가능
#      (예: Gmail MCP -> Outlook MCP)
#    - 테스트 용이: Skill과 Tool을 독립적으로 테스트 가능
#
# 다음 Chapter에서는:
#    - A2A (Agent-to-Agent) 프로토콜로 여러 Agent 간 협업
#    - 메일 Agent + 일정 Agent + 요약 Agent 연동
