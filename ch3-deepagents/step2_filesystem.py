"""
Chapter 3 - Step 2: Filesystem 백엔드 활용

DeepAgents의 Backend를 교체하여 파일 저장 방식을 바꿉니다.
- StateBackend(기본값): 인메모리 → Step 1에서 확인
- FilesystemBackend: 로컬 디스크 저장 → 이번 Step의 핵심
- CompositeBackend: 경로별 라우팅 (고급)
"""

import json
from pathlib import Path

from deepagents import create_deep_agent
from deepagents.backends import StateBackend, FilesystemBackend, CompositeBackend
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
# 1. FilesystemBackend로 Agent 생성
# ============================================================
# Step 1에서는 기본 StateBackend(인메모리)를 사용했습니다.
# backend만 바꾸면 Agent 코드 변경 없이 디스크 저장으로 전환됩니다.

agent_fs = create_deep_agent(
    model="openai:google/gemini-3-flash-preview",
    backend=FilesystemBackend(root_dir=str(WORKSPACE), virtual_mode=True),
    # virtual_mode=True: root_dir 바깥 경로 접근 차단 (보안)
)

print(f"[INFO] FilesystemBackend Agent 생성 완료 (root_dir: {WORKSPACE})")


# ============================================================
# 2. 실행: 메일 분석 결과를 디스크에 저장
# ============================================================

@tool
def fetch_emails(batch_start: int, batch_size: int = 5) -> str:
    """메일을 배치로 가져옵니다.

    Args:
        batch_start: 시작 인덱스 (0부터)
        batch_size: 한 번에 가져올 메일 수
    """
    import random

    categories = ["긴급", "일반", "마케팅", "내부공지"]
    senders = ["팀장님", "고객사A", "마케팅팀", "HR팀", "기술지원", "CEO"]

    emails = []
    for i in range(batch_start, min(batch_start + batch_size, 20)):
        random.seed(i)
        emails.append({
            "id": i + 1,
            "from": random.choice(senders),
            "subject": f"메일 #{i+1}: {random.choice(categories)} 관련",
            "category": random.choice(categories),
        })

    remaining = max(0, 20 - (batch_start + batch_size))
    return json.dumps({
        "emails": emails,
        "total": 20,
        "fetched": len(emails),
        "remaining": remaining,
    }, ensure_ascii=False, indent=2)


analysis_agent = create_deep_agent(
    model="openai:google/gemini-3-flash-preview",
    tools=[fetch_emails],
    backend=FilesystemBackend(root_dir=str(WORKSPACE), virtual_mode=True),
    system_prompt=(
        "당신은 메일 분석 Agent입니다. "
        "fetch_emails로 메일을 가져온 뒤, "
        "카테고리별로 분류하여 write_file로 결과를 저장하세요. "
        "ls로 현재 파일 목록을 확인할 수 있습니다."
    ),
)

user_msg = (
    "메일 20통을 5통씩 배치로 가져와서 분석해줘. "
    "카테고리별 분류 결과를 'email_analysis.md' 파일에 저장하고, "
    "마지막에 ls로 생성된 파일 목록을 확인해줘."
)

print(f"\n👤 사용자 요청: {user_msg}")
print("[INFO] Agent 실행 중...\n")

result = analysis_agent.invoke({
    "messages": [{"role": "user", "content": user_msg}]
})

# 최종 응답
print("--- Agent 최종 응답 ---")
pretty_print(result["messages"][-1])

# Agent가 호출한 Tool 목록
print("\n--- Agent가 호출한 Tool ---")
for msg in result["messages"]:
    if isinstance(msg, AIMessage) and msg.tool_calls:
        for tc in msg.tool_calls:
            print(f"  - {tc['name']}({', '.join(f'{k}={v!r}' for k, v in tc['args'].items())})")

# 디스크에 실제 파일이 생성되었는지 확인 — 이것이 StateBackend와의 핵심 차이
print(f"\n--- 디스크 확인: {WORKSPACE} ---")
ws_files = list(WORKSPACE.iterdir()) if WORKSPACE.exists() else []
if ws_files:
    for f in ws_files:
        size = f.stat().st_size if f.is_file() else 0
        print(f"  {'📄' if f.is_file() else '📁'} {f.name} ({size} bytes)")
    print("\n  → FilesystemBackend 덕분에 실제 디스크에 파일이 생성되었습니다.")
    print("  → Step 1의 StateBackend에서는 State 딕셔너리 안에만 존재했습니다.")
else:
    print("  (파일 없음 — Agent가 write_file을 호출하지 않았을 수 있습니다)")


# ============================================================
# 3. CompositeBackend: 경로별 다른 백엔드 (참고)
# ============================================================
# 파일 경로에 따라 다른 백엔드를 라우팅하는 고급 패턴입니다.
# 예: /memories/* → FilesystemBackend(영구), 그 외 → StateBackend(임시)

composite_backend = lambda rt: CompositeBackend(
    default=StateBackend(rt),  # 기본: 인메모리
    routes={
        "/memories/": FilesystemBackend(
            root_dir=str(WORKSPACE / "memories"), virtual_mode=True
        ),
    },
)

agent_composite = create_deep_agent(
    model="openai:google/gemini-3-flash-preview",
    backend=composite_backend,
)

print("\n--- CompositeBackend 구성 ---")
print("  /memories/* → FilesystemBackend (디스크 영구 저장)")
print("  그 외       → StateBackend (인메모리, 실행 종료 시 삭제)")
