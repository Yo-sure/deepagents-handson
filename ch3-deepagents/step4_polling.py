"""
Chapter 3 - Step 4: 간단한 스케줄/반복 실행(폴링) 구성

Agent를 주기적으로 실행하여 새 메일을 확인하는 패턴을 구현합니다.
- asyncio 기반 폴링 루프
- MemorySaver(checkpointer)로 세션 간 상태 유지
- thread_id로 동일한 대화 컨텍스트 유지
"""

import asyncio
import json
import random
from datetime import datetime
from pathlib import Path

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langgraph.checkpoint.memory import MemorySaver
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
# 1. Mock 메일 시스템 (매 폴링마다 새 메일 도착)
# ============================================================

MAIL_STORE = []
LAST_CHECKED_ID = 0


def generate_new_emails(count: int = 3) -> list:
    """새 메일을 랜덤 생성합니다 (Mock)."""
    categories = ["긴급", "일반", "마케팅", "내부공지", "프로젝트"]
    senders = ["팀장님", "고객사A", "마케팅팀", "HR팀", "CEO", "기술지원"]
    subjects = [
        "서버 점검 공지", "프로젝트 진행 보고", "미팅 일정 변경",
        "월간 리포트 요청", "신규 고객 문의", "보안 업데이트 안내",
        "예산 승인 요청", "팀 회식 일정", "장애 보고서", "제안서 검토 요청",
    ]

    new_emails = []
    for _ in range(count):
        email_id = len(MAIL_STORE) + len(new_emails) + 1
        category = random.choice(categories)
        new_emails.append({
            "id": email_id,
            "from": random.choice(senders),
            "subject": f"[{category}] {random.choice(subjects)}",
            "category": category,
            "priority": random.choice(["높음", "보통", "낮음"]),
            "received_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "read": False,
        })
    return new_emails


@tool
def check_new_emails() -> str:
    """마지막 확인 이후 도착한 새 메일을 가져옵니다.

    이전에 확인한 메일은 제외하고 새 메일만 반환합니다.
    """
    global LAST_CHECKED_ID

    new_emails = [e for e in MAIL_STORE if e["id"] > LAST_CHECKED_ID]

    if not new_emails:
        return json.dumps({
            "new_count": 0,
            "message": "새 메일이 없습니다.",
            "last_checked_id": LAST_CHECKED_ID,
        }, ensure_ascii=False)

    LAST_CHECKED_ID = max(e["id"] for e in new_emails)

    return json.dumps({
        "new_count": len(new_emails),
        "emails": new_emails,
        "last_checked_id": LAST_CHECKED_ID,
    }, ensure_ascii=False, indent=2)


@tool
def get_email_stats() -> str:
    """전체 메일 통계를 반환합니다."""
    if not MAIL_STORE:
        return "메일함이 비어있습니다."

    stats = {
        "total": len(MAIL_STORE),
        "by_category": {},
        "by_priority": {},
        "by_sender": {},
    }

    for email in MAIL_STORE:
        cat = email["category"]
        stats["by_category"][cat] = stats["by_category"].get(cat, 0) + 1
        pri = email["priority"]
        stats["by_priority"][pri] = stats["by_priority"].get(pri, 0) + 1
        sender = email["from"]
        stats["by_sender"][sender] = stats["by_sender"].get(sender, 0) + 1

    return json.dumps(stats, ensure_ascii=False, indent=2)


# ============================================================
# 2. 폴링 Agent 구성
# ============================================================
# 핵심 구성 요소:
#   1. checkpointer=MemorySaver() → 세션 간 상태 유지
#   2. thread_id → 동일 스레드로 이전 대화 이어서 진행
#   3. FilesystemBackend → 폴링 결과를 디스크에 누적 저장
#   4. asyncio.sleep(interval) → 주기적 반복 실행

async def create_polling_agent():
    """폴링용 Agent를 생성합니다."""
    agent = create_deep_agent(
        model="openai:google/gemini-3-flash-preview",
        tools=[check_new_emails, get_email_stats],
        checkpointer=MemorySaver(),
        backend=FilesystemBackend(root_dir=str(WORKSPACE / "polling"), virtual_mode=True),
        system_prompt=(
            "당신은 메일 모니터링 Agent입니다.\n"
            "주기적으로 호출되며, 매번 다음을 수행합니다:\n"
            "1. check_new_emails로 새 메일 확인\n"
            "2. 새 메일이 있으면 카테고리/우선순위별로 간단히 요약\n"
            "3. 긴급 메일이 있으면 명확히 표시\n"
            "4. 결과를 write_file로 'polling_log.md'에 누적 기록\n"
            "5. 새 메일이 없으면 간단히 '새 메일 없음'으로 응답\n\n"
            "이전 대화 기록을 참고하여 중복 보고를 피하세요."
        ),
    )
    return agent


# ============================================================
# 3. 폴링 루프 (asyncio 기반)
# ============================================================

async def polling_loop(interval_seconds: int = 5, max_polls: int = 3):
    """주기적으로 Agent를 실행하는 폴링 루프.

    Args:
        interval_seconds: 폴링 간격 (초)
        max_polls: 최대 폴링 횟수 (데모용, 실제로는 무한 루프)
    """
    agent = await create_polling_agent()
    config = {"configurable": {"thread_id": "mail-poller"}}

    print(f"[폴링 시작] 간격: {interval_seconds}초, 최대 횟수: {max_polls}\n")

    for poll_num in range(1, max_polls + 1):
        current_time = datetime.now().strftime("%H:%M:%S")

        # 새 메일 시뮬레이션 (매 폴링마다 1~4통 도착)
        new_count = random.randint(1, 4)
        new_emails = generate_new_emails(new_count)
        MAIL_STORE.extend(new_emails)

        print(f"[폴링 #{poll_num}] {current_time} - 새 메일 {new_count}통 도착 (총 {len(MAIL_STORE)}통)")

        # Agent 비동기 실행 (동일한 thread_id로 이전 상태 이어서)
        result = await agent.ainvoke(
            {
                "messages": [{
                    "role": "user",
                    "content": (
                        f"[폴링 #{poll_num} - {current_time}] "
                        "새 메일이 도착했는지 확인하고 요약해줘."
                    ),
                }]
            },
            config=config,
        )

        last_message = result["messages"][-1]
        print(f"[Agent 응답] {getattr(last_message, 'content', '')[:200]}\n")

        if poll_num < max_polls:
            await asyncio.sleep(interval_seconds)

    print(f"[폴링 종료] 총 {max_polls}회 폴링 완료, 총 {len(MAIL_STORE)}통 처리")


# ============================================================
# 4. 실행
# ============================================================
# 데모: 3회 폴링, 5초 간격
# 운영 환경에서는 MemorySaver 대신 SqliteSaver/PostgresSaver를 사용합니다.

asyncio.run(polling_loop(interval_seconds=5, max_polls=3))
