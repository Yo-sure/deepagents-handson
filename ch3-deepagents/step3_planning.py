"""
Chapter 3 - Step 3: Planning 도구 활용 (write_todos)

DeepAgents의 내장 Planning 기능을 살펴봅니다.
- write_todos: 작업 분해 및 진행 추적
- pending -> in_progress -> completed 상태 관리
- TodoListMiddleware가 자동으로 계획 수립을 유도
"""

import json
from pathlib import Path

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langchain_core.messages import AIMessage
from langchain_core.tools import tool

# workspace 경로 — 스크립트 위치 기준 절대경로 (CWD에 의존하지 않음)
WORKSPACE = Path(__file__).resolve().parent.parent / "workspace" / "ch3"
WORKSPACE.mkdir(parents=True, exist_ok=True)


def pretty_print(message) -> None:
    """메시지의 content를 보기 좋게 출력합니다."""
    content = getattr(message, "content", str(message))
    if isinstance(content, (list, dict)):
        print(json.dumps(content, indent=2, ensure_ascii=False, default=str))
    else:
        print(content)


# ============================================================
# 1. 메일 100통 분석 — write_todos로 자동 계획 수립
# ============================================================
# write_todos는 기본 내장 Planning Tool입니다.
# TodoListMiddleware가 복잡한 작업 시 자동으로 계획 수립을 유도합니다.
#   각 항목: {"content": "작업 설명", "status": "pending|in_progress|completed"}
#   상태 전이: pending → in_progress → completed

@tool
def fetch_emails(batch_start: int, batch_size: int = 10) -> str:
    """메일을 배치로 가져옵니다. 한 번에 모든 메일을 로드하지 않습니다.

    Args:
        batch_start: 시작 인덱스 (0부터)
        batch_size: 한 번에 가져올 메일 수 (최대 10)
    """
    import random

    categories = ["긴급", "일반", "마케팅", "내부공지", "프로젝트"]
    senders = ["팀장님", "고객사A", "고객사B", "마케팅팀", "HR팀", "기술지원", "CEO", "외부파트너"]
    priorities = ["높음", "보통", "낮음"]

    emails = []
    for i in range(batch_start, min(batch_start + batch_size, 100)):
        random.seed(i)
        emails.append({
            "id": i + 1,
            "from": random.choice(senders),
            "subject": f"메일 #{i+1}: {random.choice(categories)} 건",
            "category": random.choice(categories),
            "priority": random.choice(priorities),
            "length": random.randint(50, 500),
        })

    remaining = max(0, 100 - (batch_start + batch_size))
    return json.dumps({
        "emails": emails,
        "total": 100,
        "fetched": len(emails),
        "remaining": remaining,
        "hint": f"다음 배치: fetch_emails(batch_start={batch_start + batch_size})" if remaining > 0 else "모든 메일 가져오기 완료",
    }, ensure_ascii=False, indent=2)


planning_agent = create_deep_agent(
    model="openai:google/gemini-3-flash-preview",
    tools=[fetch_emails],
    backend=FilesystemBackend(root_dir=str(WORKSPACE), virtual_mode=True),
    system_prompt=(
        "당신은 메일 분석 Agent입니다. "
        "대량의 메일을 체계적으로 분석하고 보고서를 작성합니다.\n\n"
        "작업 절차:\n"
        "1. 먼저 write_todos로 전체 작업 계획을 세우세요.\n"
        "2. 각 단계를 시작할 때 해당 TODO의 status를 'in_progress'로 변경하세요.\n"
        "3. 단계를 완료하면 status를 'completed'로 변경하세요.\n"
        "4. 중간 결과는 write_file로 파일에 저장하여 컨텍스트를 절약하세요.\n"
        "5. 최종 보고서를 작성하면 작업 완료입니다."
    ),
)

user_msg = (
    "메일 100통을 분석해서 보고서를 만들어줘.\n"
    "1. 먼저 전체 계획을 세워줘 (write_todos 사용)\n"
    "2. 10통씩 배치로 가져와서 분석해\n"
    "3. 카테고리별, 우선순위별 분류 결과를 파일에 저장해\n"
    "4. 최종 보고서를 'final_report.md'로 만들어줘"
)

print(f"👤 사용자 요청: {user_msg}")
print("[INFO] Agent 실행 중...\n")

result = planning_agent.invoke({
    "messages": [{"role": "user", "content": user_msg}]
})

# 최종 응답
print("--- Agent 최종 응답 ---")
pretty_print(result["messages"][-1])

# Agent가 호출한 Tool 목록 — write_todos 호출 여부 확인
print("\n--- Agent가 호출한 Tool ---")
for msg in result["messages"]:
    if isinstance(msg, AIMessage) and msg.tool_calls:
        for tc in msg.tool_calls:
            args_str = ", ".join(f"{k}={v!r}" for k, v in tc["args"].items())
            # write_todos는 args가 길므로 줄여서 출력
            if tc["name"] == "write_todos":
                print(f"  - write_todos(항목 수: {len(tc['args'].get('todos', []))})")
            else:
                print(f"  - {tc['name']}({args_str[:80]})")

# State에서 todos 확인
print("\n--- Agent State (messages 제외) ---")
for key in result:
    if key == "messages":
        print(f"  {key}: [{len(result[key])}개 메시지]")
    elif key == "todos":
        todos = result[key]
        print(f"  {key}: [{len(todos)}개 항목]")
        for todo in todos:
            status = todo.get("status", "unknown")
            icons = {"pending": "⬜", "in_progress": "🔄", "completed": "✅"}
            print(f"    {icons.get(status, '❓')} [{status}] {todo.get('content', '')}")
    else:
        print(f"  {key}: {json.dumps(result[key], indent=4, ensure_ascii=False, default=str)}")

# 디스크 확인
print(f"\n--- 디스크 확인: {WORKSPACE} ---")
ws_files = list(WORKSPACE.iterdir()) if WORKSPACE.exists() else []
if ws_files:
    for f in sorted(ws_files):
        if f.is_file():
            print(f"  📄 {f.name} ({f.stat().st_size} bytes)")
