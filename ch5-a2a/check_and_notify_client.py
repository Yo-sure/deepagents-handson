"""
Chapter 5 - Client Agent (테스트용)

이 스크립트는 Client Agent 역할로 Check Agent(Remote Agent)에게 메일 확인을 요청합니다.

Check Agent가 중요 메일을 발견하면 내부적으로 Notify Agent를 호출(이때 Client Agent 역할)하여
알림을 전송하고, 그 결과를 포함한 보고서를 이 스크립트에 반환합니다.

  Client Agent(이 스크립트) → Check Agent(Remote Agent)
                               ↓ 메일 확인 + 중요 메일 발견
                               ↓ Notify Agent 호출 (Client Agent 역할 겸함)
                             ← 알림 결과 포함한 최종 보고서

a2a-sdk의 ClientFactory + Client를 사용하여 JSON-RPC 구성을 SDK에 위임합니다.
(httpx로 직접 구성하는 방식은 check_agent.py의 notify_agent_via_a2a()를 참고)

실행 방법:
  uv run python3 ch5-a2a/check_and_notify_client.py

전제 (터미널 2개에서 먼저 실행):
  uv run python3 ch5-a2a/check_agent.py    # Remote Agent, port 9501
  uv run python3 ch5-a2a/notify_agent.py   # Remote Agent, port 9502
"""

import asyncio
import uuid

import httpx
from a2a.client import A2ACardResolver, ClientFactory, ClientConfig
from a2a.types import Message, Part, TextPart, Role, Task, TaskState

CHECK_AGENT_URL = "http://localhost:9501"

# ============================================================
# 응답 포맷팅 헬퍼
# ============================================================
# client.send_message()가 반환하는 Task 객체를 사람이 읽기 쉬운 형태로 출력합니다.
# Task 구조: status(상태) + artifacts(결과물) + history(대화 이력)

# 상태 아이콘 매핑
_STATE_ICON = {
    TaskState.submitted: "📋",   # 접수됨
    TaskState.working: "⏳",     # 처리 중
    TaskState.completed: "✅",   # 완료
    TaskState.canceled: "❌",    # 취소됨
    TaskState.failed: "💥",      # 실패
    TaskState.unknown: "❓",     # 알 수 없음
}


def print_task_result(task: Task) -> None:
    """Task 응답을 구조화하여 출력합니다."""

    # --- 상태 ---
    state = task.status.state
    icon = _STATE_ICON.get(state, "❓")
    print(f"\n{icon} 상태: {state.value}")

    # 상태 메시지
    if task.status.message and task.status.message.parts:
        for part in task.status.message.parts:
            if isinstance(part.root, TextPart):
                print(f"  → {part.root.text}")

    # --- Artifact (결과물) ---
    if task.artifacts:
        for artifact in task.artifacts:
            name = artifact.name or "결과"
            print(f"\n📄 [{name}]")
            print("-" * 50)
            for part in artifact.parts:
                if isinstance(part.root, TextPart):
                    print(part.root.text)
            print("-" * 50)


async def call_check_agent(message_text: str) -> None:
    """ClientFactory + Client로 Check Agent에게 요청을 보냅니다."""
    async with httpx.AsyncClient(timeout=30.0) as httpx_client:
        # 1) Agent Card 조회 — Remote Agent의 자기소개를 가져옵니다
        resolver = A2ACardResolver(
            httpx_client=httpx_client,
            base_url=CHECK_AGENT_URL,
        )
        card = await resolver.get_agent_card()
        print(f"Agent Card 조회 완료: {card.name}")

        # 2) Client 생성 — ClientFactory가 Agent Card의 transport 정보로 클라이언트를 구성
        factory = ClientFactory(
            config=ClientConfig(
                httpx_client=httpx_client,
                streaming=False,
            )
        )
        client = factory.create(card=card)

        # 3) Message 생성 — role="user"(Client Agent), parts에 텍스트
        msg = Message(
            role=Role.user,
            messageId=str(uuid.uuid4()),
            parts=[Part(root=TextPart(text=message_text))],
        )

        # 4) send_message — SDK가 JSON-RPC 요청을 자동 구성·전송
        print(f"요청 전송: \"{message_text}\"")
        print()

        async for event in client.send_message(request=msg):
            # send_message()는 (Task, UpdateEvent | None) 튜플 또는 Message를 yield
            # non-streaming에서는 최종 결과 (Task, None)이 1회 yield됨
            if isinstance(event, tuple):
                task, update = event
                print_task_result(task)
            elif isinstance(event, Message):
                print(f"\n💬 메시지: ", end="")
                for part in event.parts:
                    if isinstance(part.root, TextPart):
                        print(part.root.text)
            else:
                print(event)


async def main() -> None:
    print("=" * 50)
    print("Client Agent → Check Agent 요청")
    print("=" * 50)
    print("Check Agent에게 메일 확인을 요청합니다.")
    print("중요 메일이 있으면 Check Agent가 내부적으로 Notify Agent를 호출합니다.")
    print()

    try:
        await call_check_agent("메일함 확인해줘")
    except httpx.ConnectError:
        print("Check Agent에 연결할 수 없습니다.")
        print("  → uv run python3 ch5-a2a/check_agent.py")
        print("  → uv run python3 ch5-a2a/notify_agent.py")
        return

    print()
    print("=" * 50)
    print("완료")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
