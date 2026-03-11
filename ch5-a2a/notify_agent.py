"""
Chapter 5 - Notify Agent (A2A 서버)

A2A 프로토콜을 사용한 알림 전송 Agent입니다.
- Check Agent로부터 A2A 요청을 받아 알림을 전송
- 콘솔 출력으로 Slack 알림을 시뮬레이션
- 독립된 A2A 서버로 port 9502에서 동작

실행 방법:
  pip install a2a-sdk uvicorn
  python3 notify_agent.py

이 Agent가 실행되면:
  - http://localhost:9502 에서 A2A 서버 시작
  - http://localhost:9502/.well-known/agent-card.json 에서 Agent Card 제공
  - Check Agent가 중요 메일을 감지하면 이 Agent에게 알림 요청

참고: 실제 운영 환경에서는 콘솔 출력 대신 Slack API, Teams Webhook,
      이메일 등 실제 알림 채널을 사용합니다.
"""

import json
import logging
from datetime import datetime

import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.server.tasks.task_updater import TaskUpdater
from a2a.server.events import EventQueue
from a2a.types import (
    AgentCard,
    AgentCapabilities,
    AgentSkill,
    Part,
    TextPart,
)

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")


logger = logging.getLogger("NotifyAgent")


# ============================================================
# 1. 알림 채널 시뮬레이터
# ============================================================
# 이 Agent는 의도적으로 LLM 없이 규칙 기반으로 동작합니다.
# → A2A 프로토콜 구조에 집중하기 위함 (Check Agent와 동일한 설계 의도)
#
# 실제 환경에서는 Slack SDK, Teams Webhook, SendGrid 등을 사용합니다.
# 여기서는 콘솔 출력으로 각 채널을 시뮬레이션합니다.

class NotificationChannel:
    """알림 채널 추상 레이어"""

    @staticmethod
    def send_slack(message: str) -> dict:
        """Slack 알림 시뮬레이션"""
        print()
        print("=" * 50)
        print("  [SLACK 알림 시뮬레이션]")
        print("=" * 50)
        print(f"  채널: #important-alerts")
        print(f"  시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  ---")
        for line in message.split("\n"):
            print(f"  {line}")
        print("=" * 50)
        print()
        return {"channel": "slack", "status": "sent", "channel_name": "#important-alerts"}

    @staticmethod
    def send_console(message: str) -> dict:
        """콘솔 알림 (기본 채널)"""
        print()
        print("*" * 50)
        print("  [콘솔 알림]")
        print("*" * 50)
        for line in message.split("\n"):
            print(f"  {line}")
        print("*" * 50)
        print()
        return {"channel": "console", "status": "sent"}

    @staticmethod
    def send_email_mock(message: str) -> dict:
        """이메일 알림 시뮬레이션"""
        print()
        print("+" * 50)
        print("  [EMAIL 알림 시뮬레이션]")
        print("+" * 50)
        print(f"  To: user@company.com")
        print(f"  Subject: 중요 메일 알림")
        print(f"  ---")
        for line in message.split("\n"):
            print(f"  {line}")
        print("+" * 50)
        print()
        return {"channel": "email", "status": "sent", "to": "user@company.com"}


# ============================================================
# 2. Notify Agent 실행기 (AgentExecutor 구현)
# ============================================================

class NotifyAgentExecutor(AgentExecutor):
    """
    알림 전송 Agent의 핵심 로직입니다.

    Check Agent로부터 A2A 요청을 받아:
      1. 알림 내용 파싱
      2. 여러 채널로 알림 전송 (Slack, 콘솔, 이메일)
      3. 전송 결과 보고

    A2A 통신 시나리오:
      Check Agent → (A2A JSON-RPC) → Notify Agent
        "중요 메일 3통이 감지되었습니다!"
        → Slack 알림 전송
        → 콘솔 알림 출력
        → 결과 반환
    """

    def __init__(self):
        self.notification_channel = NotificationChannel()
        # 알림 이력 (메모리 저장)
        self.notification_history: list[dict] = []

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        """
        A2A 요청을 처리하여 알림을 전송합니다.

        Args:
            context: 요청 컨텍스트 (Check Agent가 보낸 알림 내용)
            event_queue: 결과를 전달할 이벤트 큐
        """
        logger.info("=" * 50)
        logger.info("알림 전송 작업 시작")
        logger.info("=" * 50)

        # --- Step 1: 알림 내용 추출 ---
        # Part.root는 TextPart | FilePart | DataPart 중 하나
        notification_text = ""
        if context.message and context.message.parts:
            notification_text = "".join(
                part.root.text for part in context.message.parts
                if isinstance(part.root, TextPart)
            )

        if not notification_text:
            notification_text = "(알림 내용 없음)"

        logger.info(f"수신된 알림 내용:\n{notification_text}")

        # --- Step 2: TaskUpdater 생성 + 상태 업데이트 → 작업 중 ---
        # TaskUpdater의 역할과 API 상세 설명은 check_agent.py의 Step 2 주석을 참고
        updater = TaskUpdater(
            event_queue=event_queue,
            task_id=context.task_id,
            context_id=context.context_id,
        )
        await updater.start_work(
            message=updater.new_agent_message(
                parts=[Part(root=TextPart(text="알림을 전송하고 있습니다..."))],
            ),
        )

        # --- Step 3: 멀티 채널 알림 전송 ---
        results = []

        # 3-1. Slack 알림 전송
        logger.info("Slack 알림 전송 중...")
        slack_result = self.notification_channel.send_slack(notification_text)
        results.append(slack_result)

        # 3-2. 콘솔 알림 전송
        logger.info("콘솔 알림 전송 중...")
        console_result = self.notification_channel.send_console(notification_text)
        results.append(console_result)

        # 3-3. 이메일 알림 전송
        logger.info("이메일 알림 전송 중...")
        email_result = self.notification_channel.send_email_mock(notification_text)
        results.append(email_result)

        # --- Step 4: 알림 이력 기록 ---
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "message": notification_text[:100],
            "channels": [r["channel"] for r in results],
            "all_sent": all(r["status"] == "sent" for r in results),
        }
        self.notification_history.append(history_entry)
        logger.info(f"알림 이력 기록 완료 (총 {len(self.notification_history)}건)")

        # --- Step 5: 결과 보고서 작성 ---
        report_lines = [
            "=== 알림 전송 결과 보고서 ===",
            f"전송 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"전송 채널: {len(results)}개",
            "",
        ]

        for result in results:
            status_mark = "[성공]" if result["status"] == "sent" else "[실패]"
            report_lines.append(f"  {status_mark} {result['channel']} 채널")

        report_lines.extend([
            "",
            "--- 원본 알림 내용 ---",
            notification_text,
            "",
            f"--- 알림 이력: 총 {len(self.notification_history)}건 ---",
        ])

        report_text = "\n".join(report_lines)

        # --- Step 6: 결과를 Artifact로 전달 ---
        await updater.add_artifact(
            parts=[Part(root=TextPart(text=report_text))],
            name="notification-report",
        )

        # --- Step 7: 최종 상태 → 완료 ---
        success_count = sum(1 for r in results if r["status"] == "sent")
        final_message = (
            f"알림 전송 완료: {success_count}/{len(results)} 채널 전송 성공"
        )
        await updater.complete(
            message=updater.new_agent_message(
                parts=[Part(root=TextPart(text=final_message))],
            ),
        )

        logger.info(f"작업 완료: {final_message}")

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        """작업 취소 처리"""
        logger.info("작업 취소 요청 수신")
        updater = TaskUpdater(
            event_queue=event_queue,
            task_id=context.task_id,
            context_id=context.context_id,
        )
        await updater.cancel(
            message=updater.new_agent_message(
                parts=[Part(root=TextPart(text="알림 전송 작업이 취소되었습니다."))],
            ),
        )


# ============================================================
# 3. Agent Card 정의
# ============================================================
# Notify Agent의 "명함"입니다.
# Check Agent가 이 카드를 보고 알림 전송 능력을 파악합니다.
#
# GET http://localhost:9502/.well-known/agent-card.json 으로 조회 가능

agent_card = AgentCard(
    name="Notify Agent",
    description="알림을 전송하는 Agent입니다. "
                "Slack, 콘솔, 이메일 등 여러 채널로 알림을 보냅니다.",
    url="http://localhost:9502",
    version="1.0.0",
    capabilities=AgentCapabilities(streaming=False),
    skills=[
        AgentSkill(
            id="send-notification",
            name="알림 전송",
            description=(
                "중요 메일이나 이벤트에 대한 알림을 전송합니다. "
                "Slack, 콘솔, 이메일 등 여러 채널을 지원합니다."
            ),
            tags=["notification", "alert", "slack", "email"],
            examples=[
                "중요 메일 알림을 보내줘",
                "Slack으로 알림 전송해줘",
                "긴급 알림을 모든 채널로 보내줘",
            ],
        ),
    ],
    defaultInputModes=["text/plain"],
    defaultOutputModes=["text/plain"],
)


# ============================================================
# 4. A2A 서버 구성 및 실행
# ============================================================

def create_app():
    """A2A 서버 애플리케이션을 생성합니다."""

    # 1) Agent 실행기 생성
    executor = NotifyAgentExecutor()

    # 2) 요청 핸들러 생성
    #    InMemoryTaskStore: Task 상태(submitted→working→completed)를
    #    메모리에 저장하여 task/get 조회 시 진행 상황을 반환합니다.
    handler = DefaultRequestHandler(
        agent_executor=executor,
        task_store=InMemoryTaskStore(),
    )

    # 3) Starlette ASGI 애플리케이션 생성
    application = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=handler,
    )

    return application.build()


# ============================================================
# 5. 메인 실행
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Chapter 5: Notify Agent (A2A 서버)")
    print("=" * 60)
    print()
    print(f"Agent 이름: {agent_card.name}")
    print(f"설명: {agent_card.description}")
    print(f"URL: {agent_card.url}")
    print(f"스킬: {[s.name for s in agent_card.skills]}")
    print()
    print("A2A 엔드포인트:")
    print(f"  Agent Card: http://localhost:9502/.well-known/agent-card.json")
    print(f"  JSON-RPC:   http://localhost:9502/")
    print()
    print("이 Agent는 Check Agent(port 9501)로부터")
    print("중요 메일 알림 요청을 받아 처리합니다.")
    print()
    print("-" * 60)
    print("서버 시작 중...")
    print("-" * 60)

    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=9502)


# ============================================================
# 핵심 정리
# ============================================================
#
# 1. Notify Agent의 역할
#    - Check Agent로부터 A2A 요청을 수신
#    - 알림 내용을 파싱하여 여러 채널로 전송
#    - 전송 결과를 A2A 응답으로 반환
#
# 2. 멀티 채널 알림 패턴
#    - Slack: 실제 환경에서는 slack_sdk 사용
#    - Email: 실제 환경에서는 SendGrid, SES 등 사용
#    - Console: 개발/디버깅 용도
#    → 모두 동일한 인터페이스(send)로 추상화 가능
#
# 3. A2A 서버 구현 패턴 (Check Agent와 동일)
#    AgentExecutor 구현 → DefaultRequestHandler → A2AStarletteApplication
#    → 이 패턴이 A2A 서버의 기본 뼈대!
#
# 4. Agent 간 역할 분리의 장점
#    - Check Agent: 메일 확인에만 집중
#    - Notify Agent: 알림 전송에만 집중
#    - 각자 독립적으로 개발, 배포, 스케일링 가능
#    - 새로운 알림 채널 추가 시 Notify Agent만 수정
#
# 5. Chapter 6 미리보기
#    → 이 두 Agent를 DeepAgents Harness + Skills + MCP와
#      통합하여 End-to-End 메일 관리 시스템을 구축합니다.
