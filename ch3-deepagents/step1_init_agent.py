"""
Chapter 3 - Step 1: DeepAgents Agent 초기화

Ch2에서 직접 만들었던 Agent를 DeepAgents로 대체합니다.
- create_deep_agent() 한 줄로 Agent 생성
- 기본 내장 Tool 확인 (read_file, write_file, ls, write_todos 등)
- 간단한 메일 확인 작업 수행
"""

# ============================================================
# 0. 설치 안내
# ============================================================
# uv add deepagents langchain-openai
#
# 환경변수 설정 (Ch2 Preflight에서 이미 완료):
#   export OPENROUTER_API_KEY="sk-or-..."
#   export OPENAI_API_KEY="$OPENROUTER_API_KEY"
#   export OPENAI_API_BASE="https://openrouter.ai/api/v1"
# ============================================================

import json

from deepagents import create_deep_agent
from langchain_core.messages import AIMessage
from langchain_core.tools import tool


def pretty_print(message) -> None:
    """메시지의 content를 보기 좋게 출력합니다."""
    content = getattr(message, "content", str(message))
    if isinstance(content, (list, dict)):
        print(json.dumps(content, indent=2, ensure_ascii=False, default=str))
    else:
        print(content)


# ============================================================
# 1. 커스텀 Tool 정의 + Agent 생성
# ============================================================
# create_deep_agent()는 내장 Tool 9개를 자동 포함합니다:
#   read_file, write_file, edit_file, ls, glob, grep,
#   execute, write_todos, task
# 아래에서는 커스텀 Tool(check_inbox, get_email_detail)을 추가합니다.

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
        {"from": "마케팅팀", "subject": "신규 캠페인 보고서", "important": False},
        {"from": "CEO", "subject": "전사 공지: 조직개편 안내", "important": True},
    ]
    if filter == "important":
        mock_emails = [e for e in mock_emails if e["important"]]

    result = f"[메일함] {filter} 메일 {len(mock_emails)}통:\n"
    for i, email in enumerate(mock_emails, 1):
        marker = "[중요]" if email["important"] else "[일반]"
        result += f"  {i}. {marker} [{email['from']}] {email['subject']}\n"
    return result


@tool
def get_email_detail(email_index: int) -> str:
    """특정 메일의 상세 내용을 가져옵니다.

    Args:
        email_index: 메일 번호 (1부터 시작)
    """
    details = {
        1: "팀장님: 내일 오후 2시부터 4시까지 서버 점검 예정입니다. 작업 저장 바랍니다.",
        2: "HR팀: 12월 20일 연말 워크숍이 진행됩니다. 참석 여부를 12/15까지 회신해주세요.",
        3: "고객사: 다음 주 화요일 오전 10시 프로젝트 진행 상황 미팅 요청드립니다.",
        4: "마케팅팀: 11월 신규 캠페인 성과 보고서를 첨부합니다. 검토 부탁드립니다.",
        5: "CEO: 2025년 조직개편 안내 - 세부사항은 첨부 문서를 참고하세요.",
    }
    return details.get(email_index, "해당 메일을 찾을 수 없습니다.")


mail_agent = create_deep_agent(
    model="openai:google/gemini-3-flash-preview",
    tools=[check_inbox, get_email_detail],
    # backend 미지정 → 기본 StateBackend(인메모리) 사용
    # write_file로 저장한 파일은 State 딕셔너리 안에 존재합니다.
    # 디스크에 영구 저장하려면 FilesystemBackend가 필요 → Step 2에서 다룹니다.
    system_prompt=(
        "당신은 메일 관리 비서 Agent입니다. "
        "사용자의 메일 관련 요청을 처리하고, "
        "분석 결과를 파일에 저장할 수 있습니다. "
        "복잡한 작업은 write_todos로 계획을 세우고 진행하세요."
    ),
)


# ============================================================
# 2. Agent 실행: 메일 확인 및 요약
# ============================================================

user_msg = (
    "중요한 메일만 확인하고, "
    "각 메일의 상세 내용을 확인한 뒤 "
    "요약을 write_file로 'mail_summary.md' 파일에 저장해줘."
)
print(f"👤 사용자 요청: {user_msg}")
print("[INFO] Agent 실행 중...\n")

result = mail_agent.invoke({
    "messages": [{"role": "user", "content": user_msg}]
})

# 최종 응답
print("--- Agent 최종 응답 ---")
pretty_print(result["messages"][-1])

# State 전체 확인: 파일이 어디에 저장되었나?
# StateBackend는 파일을 디스크가 아닌 State 딕셔너리 안에 보관합니다.
print("\n--- Agent State (messages 제외) ---")
for key in result:
    val = result[key]
    if key == "messages":
        print(f"  {key}: [{len(val)}개 메시지]")
    else:
        print(f"  {key}: {json.dumps(val, indent=4, ensure_ascii=False, default=str)}")

if result.get("files"):
    print("\n  → write_file로 저장한 파일이 State(메모리) 안에 존재합니다.")
    print("  → 하지만 이 프로세스가 종료되면 사라집니다!")
    print("  → Step 2에서 FilesystemBackend를 사용하면 디스크에 영구 저장됩니다.")
else:
    print("\n  ⚠️  State에 files 키가 비어있습니다.")
    print("     Agent가 write_file을 호출하지 않았을 수 있습니다.")


# ============================================================
# 3. 토큰 사용량 분석
# ============================================================
# 미들웨어가 매 호출마다 ~3,000+ 토큰을 시스템 프롬프트에 자동 주입합니다.
# 이 추가 토큰이 행동 품질을 올려 Terminal Bench 기준
# 동일 모델로 52.8% → 66.5% (+13.7%p) 성능 향상을 가져옵니다.

total_input = 0
total_output = 0
llm_calls = 0

for msg in result["messages"]:
    if isinstance(msg, AIMessage) and msg.usage_metadata:
        total_input += msg.usage_metadata.get("input_tokens", 0)
        total_output += msg.usage_metadata.get("output_tokens", 0)
        llm_calls += 1

print(f"""
  [토큰 사용량]
  LLM 호출 횟수 : {llm_calls}회
  입력 토큰     : {total_input:,}
  출력 토큰     : {total_output:,}
  합계          : {total_input + total_output:,}
""")
