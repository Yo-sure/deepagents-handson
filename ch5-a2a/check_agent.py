"""
Chapter 5 - Check Agent (A2A 서버)

A2A(Agent-to-Agent) 프로토콜을 사용한 메일 확인 Agent입니다.
- a2a-sdk를 활용하여 표준 A2A 서버로 동작
- 메일함을 확인하고 중요 메일을 감지
- 중요 메일 발견 시 Notify Agent에게 A2A 요청으로 알림 위임

실행 방법:
  pip install a2a-sdk uvicorn httpx
  python3 check_agent.py

이 Agent가 실행되면:
  - http://localhost:9501 에서 A2A 서버 시작
  - http://localhost:9501/.well-known/agent-card.json 에서 Agent Card 제공
  - 다른 Agent나 클라이언트가 A2A 프로토콜로 메일 확인 요청 가능

참고: Chapter 2에서 LangGraph로 만들었던 메일 확인 기능을
      이제 A2A 표준 프로토콜 위에서 독립 서비스로 구동합니다.
"""

import json
import logging
from datetime import datetime

import httpx
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
logger = logging.getLogger("CheckAgent")


# ============================================================
# 1. Mock 메일 데이터
# ============================================================
# 이 Agent는 의도적으로 LLM 없이 규칙 기반으로 동작합니다.
# → A2A 프로토콜 구조(Agent Card, JSON-RPC, Task 상태)에 집중하기 위함
# → 프로덕션에서 LLM 메일 분류가 필요하면 execute() 안에서 호출하면 됩니다.
#
# 실제 환경에서는 Chapter 4의 MCP Server를 통해 IMAP/Gmail API 접근
# 여기서는 교육 목적으로 모킹합니다.

MOCK_INBOX = [
    {
        "id": 1,
        "from": "ceo@company.com",
        "sender_name": "CEO 김대표",
        "subject": "[긴급] 내일 이사회 자료 준비 요청",
        "body": "내일 오전 이사회에서 사용할 Q4 실적 자료를 오늘 중으로 준비해주세요.",
        "important": True,
        "timestamp": "2025-01-15T09:00:00",
    },
    {
        "id": 2,
        "from": "hr@company.com",
        "sender_name": "HR팀",
        "subject": "2025년 연차 사용 안내",
        "body": "2025년 연차 사용 계획을 1월 말까지 제출해주세요.",
        "important": False,
        "timestamp": "2025-01-15T10:30:00",
    },
    {
        "id": 3,
        "from": "client-a@partner.com",
        "sender_name": "고객사A 박과장",
        "subject": "프로젝트 마일스톤 지연 관련 긴급 미팅",
        "body": "프로젝트 2차 마일스톤이 1주일 지연되고 있습니다. 긴급 미팅 요청드립니다.",
        "important": True,
        "timestamp": "2025-01-15T11:15:00",
    },
    {
        "id": 4,
        "from": "newsletter@tech.com",
        "sender_name": "Tech Weekly",
        "subject": "이번 주 AI 뉴스 모음",
        "body": "이번 주 주요 AI 뉴스를 정리했습니다...",
        "important": False,
        "timestamp": "2025-01-15T07:00:00",
    },
    {
        "id": 5,
        "from": "security@company.com",
        "sender_name": "보안팀",
        "subject": "[필독] 보안 패치 긴급 적용 안내",
        "body": "심각한 취약점이 발견되었습니다. 오늘 18시까지 패치를 적용해주세요.",
        "important": True,
        "timestamp": "2025-01-15T14:00:00",
    },
]


# ============================================================
# 2. Notify Agent에게 알림 위임 (Client Agent 역할)
# ============================================================
# Check Agent는 Remote Agent(서버)이지만, Notify Agent를 호출할 때는
# Client Agent 역할도 합니다. 하나의 Agent가 상황에 따라 양쪽 역할을 겸합니다.
# 결과 문자열은 Check Agent의 보고서에 포함되어 원래 요청한 Client Agent에게 반환됩니다.
#
# 여기서는 JSON-RPC 구조를 직접 보여주기 위해 httpx로 구현했습니다.
# a2a-sdk의 A2AClient를 사용하는 간결한 방식은 check_and_notify_client.py를 참고하세요.

NOTIFY_AGENT_URL = "http://localhost:9502"


async def notify_agent_via_a2a(important_emails: list[dict]) -> str:
    """
    Notify Agent에게 A2A로 알림 전송을 요청하고, 결과를 문자열로 반환합니다.

    이 결과는 CheckAgentExecutor.execute()의 보고서에 포함되어
    최종적으로 원래 요청자(클라이언트)에게 전달됩니다.

    흐름:
      Client Agent → Check Agent(Remote) → Notify Agent(Remote)
                                            ↓ 알림 전송
                      보고서에 포함 ←──── 결과 반환
      Client Agent ← 최종 보고서
    """
    # 알림 메시지 구성
    email_summary = []
    for email in important_emails:
        email_summary.append(
            f"- [{email['sender_name']}] {email['subject']}"
        )
    notification_text = (
        f"중요 메일 {len(important_emails)}통이 감지되었습니다!\n"
        + "\n".join(email_summary)
    )

    # A2A JSON-RPC 요청 구성
    # A2A 프로토콜은 JSON-RPC 2.0 기반입니다
    a2a_request = {
        "jsonrpc": "2.0",
        "id": "check-to-notify-001",
        "method": "message/send",
        "params": {
            "message": {
                "role": "user",
                "message_id": f"notify-msg-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "parts": [
                    {"kind": "text", "text": notification_text}
                ],
            },
        },
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{NOTIFY_AGENT_URL}/",
                json=a2a_request,
                headers={"Content-Type": "application/json"},
            )
            result = response.json()
            logger.info(f"Notify Agent 응답: {json.dumps(result, ensure_ascii=False, indent=2)}")
            return f"알림 전송 완료: {result.get('result', {}).get('status', {}).get('state', 'unknown')}"
    except httpx.ConnectError:
        logger.warning(
            "Notify Agent(localhost:9502)에 연결할 수 없습니다. "
            "notify_agent.py가 실행 중인지 확인하세요."
        )
        return "알림 전송 실패: Notify Agent에 연결할 수 없음 (독립 실행 모드)"
    except Exception as e:
        logger.error(f"Notify Agent 호출 중 오류: {e}")
        return f"알림 전송 실패: {e}"


# ============================================================
# 3. Check Agent 실행기 (AgentExecutor 구현)
# ============================================================

class CheckAgentExecutor(AgentExecutor):
    """
    메일 확인 Agent의 핵심 로직입니다.

    AgentExecutor를 상속하여 execute() 메서드를 구현합니다.
    A2A 서버가 요청을 받으면 이 execute()가 호출됩니다.

    처리 흐름:
      Client Agent → [이 Agent (Remote)] → Notify Agent (Remote)
      1. Client Agent 요청 수신 (context에서 메시지 추출)
      2. 메일함 확인 (Mock 데이터)
      3. 중요 메일 필터링
      4. 중요 메일이 있으면 Notify Agent에게 A2A로 알림 위임 (이때 Client Agent 역할)
      5. 알림 결과를 포함한 보고서를 Artifact로 Client Agent에 반환
    """

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        """
        A2A 요청을 처리하는 메인 메서드.

        Args:
            context: 요청 컨텍스트 (사용자 메시지, 태스크 정보 등)
            event_queue: 결과를 전달할 이벤트 큐
        """
        logger.info("=" * 50)
        logger.info("메일 확인 작업 시작")
        logger.info("=" * 50)

        # --- Step 1: 사용자 요청 파싱 ---
        # Part.root는 TextPart | FilePart | DataPart 중 하나
        # 텍스트만 추출하려면 isinstance로 TextPart를 필터링
        user_message = ""
        if context.message and context.message.parts:
            user_message = "".join(
                part.root.text for part in context.message.parts
                if isinstance(part.root, TextPart)
            )

        logger.info(f"수신된 요청: {user_message or '(메일 확인 요청)'}")

        # --- Step 2: TaskUpdater 생성 + 상태 업데이트 → 작업 중 ---
        #
        # TaskUpdater (a2a.server.tasks.task_updater)
        # ─────────────────────────────────────────────
        # A2A SDK가 제공하는 이벤트 발행 헬퍼입니다.
        # execute() 안에서 event_queue에 이벤트를 넣을 때, 직접
        # TaskStatusUpdateEvent / TaskArtifactUpdateEvent를 생성하면
        # taskId, contextId, final, artifactId, messageId, timestamp 등
        # 필수 필드를 매번 수동으로 채워야 합니다.
        #
        # TaskUpdater는 생성 시 task_id, context_id를 한 번만 받고,
        # 이후 메서드 호출만으로 모든 필드를 자동 처리합니다:
        #
        #   updater.start_work(message=...)   → state=working, final=False
        #   updater.add_artifact(parts=...)   → artifactId 자동 UUID 생성
        #   updater.complete(message=...)     → state=completed, final=True (자동)
        #   updater.cancel(message=...)       → state=canceled, final=True (자동)
        #   updater.new_agent_message(parts=...) → role=agent, messageId=UUID 메시지 생성
        #
        # terminal state(completed, canceled, failed, rejected) 도달 후
        # 추가 update를 시도하면 RuntimeError를 발생시켜 이중 완료를 방지합니다.
        #
        updater = TaskUpdater(
            event_queue=event_queue,
            task_id=context.task_id,
            context_id=context.context_id,
        )
        await updater.start_work(
            message=updater.new_agent_message(
                parts=[Part(root=TextPart(text="메일함을 확인하고 있습니다..."))],
            ),
        )

        # --- Step 3: 메일함 확인 (Mock) ---
        logger.info(f"전체 메일 {len(MOCK_INBOX)}통 확인 중...")
        all_emails_summary = []
        for email in MOCK_INBOX:
            marker = "[중요]" if email["important"] else "[일반]"
            all_emails_summary.append(
                f"  {marker} {email['sender_name']}: {email['subject']}"
            )
        logger.info("메일 목록:\n" + "\n".join(all_emails_summary))

        # --- Step 4: 중요 메일 필터링 ---
        important_emails = [e for e in MOCK_INBOX if e["important"]]
        normal_emails = [e for e in MOCK_INBOX if not e["important"]]

        logger.info(
            f"분류 결과: 중요 {len(important_emails)}통 / 일반 {len(normal_emails)}통"
        )

        # --- Step 5: 중요 메일 → Notify Agent에 알림 위임, 결과를 보고서에 포함 ---
        notification_result = ""
        if important_emails:
            logger.info("중요 메일 감지! Notify Agent에게 알림 요청...")
            notification_result = await notify_agent_via_a2a(important_emails)
            logger.info(f"알림 결과: {notification_result}")

        # --- Step 6: 결과 보고서 작성 ---
        report_lines = [
            "=== 메일 확인 결과 보고서 ===",
            f"확인 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"전체 메일: {len(MOCK_INBOX)}통",
            f"중요 메일: {len(important_emails)}통",
            f"일반 메일: {len(normal_emails)}통",
            "",
            "--- 중요 메일 ---",
        ]
        for email in important_emails:
            report_lines.append(
                f"  * [{email['sender_name']}] {email['subject']}"
            )
            report_lines.append(f"    내용: {email['body'][:50]}...")

        report_lines.append("")
        report_lines.append("--- 일반 메일 ---")
        for email in normal_emails:
            report_lines.append(
                f"  - [{email['sender_name']}] {email['subject']}"
            )

        if notification_result:
            report_lines.append("")
            report_lines.append(f"--- 알림 상태: {notification_result} ---")

        report_text = "\n".join(report_lines)

        # --- Step 7: 결과를 Artifact로 전달 ---
        # TaskUpdater.add_artifact()가 taskId, contextId, artifactId를 자동 관리
        await updater.add_artifact(
            parts=[Part(root=TextPart(text=report_text))],
            name="mail-check-report",
        )

        # --- Step 8: 최종 상태 → 완료 ---
        final_message = (
            f"메일 확인 완료: 전체 {len(MOCK_INBOX)}통 중 "
            f"중요 메일 {len(important_emails)}통 감지"
        )
        # TaskUpdater.complete()가 final=True를 자동 설정
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
                parts=[Part(root=TextPart(text="메일 확인 작업이 취소되었습니다."))],
            ),
        )


# ============================================================
# 4. Agent Card 정의
# ============================================================
# Agent Card는 A2A 에코시스템에서 이 Agent의 "명함"입니다.
# 다른 Agent나 오케스트레이터가 이 카드를 보고
# 어떤 능력을 가진 Agent인지 파악합니다.
#
# GET http://localhost:9501/.well-known/agent-card.json 으로 조회 가능

agent_card = AgentCard(
    name="Mail Check Agent",
    description="메일함을 확인하고 중요 메일을 감지하는 Agent입니다. "
                "중요 메일 발견 시 Notify Agent에게 A2A로 알림을 요청합니다.",
    url="http://localhost:9501",
    version="1.0.0",
    capabilities=AgentCapabilities(streaming=False),
    skills=[
        AgentSkill(
            id="check-mail",
            name="메일 확인",
            description=(
                "메일함의 모든 메일을 확인하고, 중요 메일을 감지합니다. "
                "발신자, 제목, 중요도를 분석하여 결과 보고서를 생성합니다."
            ),
            tags=["mail", "inbox", "check", "important"],
            examples=[
                "메일함 확인해줘",
                "중요한 메일이 있는지 확인해줘",
                "오늘 받은 메일 요약해줘",
            ],
        ),
    ],
    defaultInputModes=["text/plain"],
    defaultOutputModes=["text/plain"],
)


# ============================================================
# 5. A2A 서버 구성 및 실행
# ============================================================

def create_app():
    """A2A 서버 애플리케이션을 생성합니다."""

    # 1) Agent 실행기 생성
    executor = CheckAgentExecutor()

    # 2) 요청 핸들러 생성
    #    DefaultRequestHandler가 A2A JSON-RPC 요청을 파싱하고
    #    적절한 executor 메서드를 호출합니다.
    #    InMemoryTaskStore: Task 상태(submitted→working→completed)를
    #    메모리에 저장하여 task/get 조회 시 진행 상황을 반환합니다.
    handler = DefaultRequestHandler(
        agent_executor=executor,
        task_store=InMemoryTaskStore(),
    )

    # 3) Starlette ASGI 애플리케이션 생성
    #    - /.well-known/agent-card.json 엔드포인트 자동 등록
    #    - JSON-RPC 요청 라우팅
    application = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=handler,
    )

    return application.build()


# ============================================================
# 6. 메인 실행
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Chapter 5: Mail Check Agent (A2A 서버)")
    print("=" * 60)
    print()
    print(f"Agent 이름: {agent_card.name}")
    print(f"설명: {agent_card.description}")
    print(f"URL: {agent_card.url}")
    print(f"스킬: {[s.name for s in agent_card.skills]}")
    print()
    print("A2A 엔드포인트:")
    print(f"  Agent Card: http://localhost:9501/.well-known/agent-card.json")
    print(f"  JSON-RPC:   http://localhost:9501/")
    print()
    print("Notify Agent(port 9502)가 함께 실행 중이면")
    print("중요 메일 감지 시 자동으로 알림을 전송합니다.")
    print()
    print("-" * 60)
    print("서버 시작 중...")
    print("-" * 60)

    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=9501)


# ============================================================
# 핵심 정리
# ============================================================
#
# 1. A2A 프로토콜 기본 구조
#    - Agent Card: Agent의 메타데이터 (이름, 능력, URL 등)
#    - AgentExecutor: 실제 작업 로직 구현
#    - DefaultRequestHandler: JSON-RPC 요청 라우팅
#    - A2AStarletteApplication: HTTP 서버 구성
#
# 2. Agent 간 통신 흐름
#    클라이언트/오케스트레이터
#      → GET /.well-known/agent-card.json (Agent Card 조회)
#      → POST / (JSON-RPC: message/send)
#      → Agent가 작업 처리
#      → 결과 반환 (TaskStatusUpdateEvent, TaskArtifactUpdateEvent)
#
# 3. 이 Check Agent의 역할
#    - 메일함 확인 및 중요도 분류
#    - 중요 메일 발견 시 Notify Agent에게 A2A로 위임
#    - Chapter 2의 Tool 호출과 다른 점:
#      Tool은 "함수 호출"이지만, A2A는 "서비스 간 통신"
#
# 4. Chapter 2 → Chapter 5 발전 경로
#    Ch2: check_inbox() Tool → LLM이 직접 호출
#    Ch5: Check Agent 서비스 → A2A 프로토콜로 독립 서비스화
#    장점: 언어/프레임워크 무관, 독립 배포, 표준 프로토콜
