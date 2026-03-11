"""
Chapter 6 - 통합 데모: 메일 Agent End-to-End

Chapter 2~5에서 배운 모든 개념을 하나로 통합합니다.
실제 인프라(MCP 서버, A2A 서버) 없이도 아키텍처를 체험할 수 있도록
Mock 구현으로 전체 흐름을 시뮬레이션합니다.

전체 아키텍처:
  ┌──────────────┐     Skills     ┌──────────────┐
  │  DeepAgents  │ ──────────── > │   SKILL.md   │
  │   Harness    │                │  (절차 안내)   │
  │   (폴링)     │     MCP        ┌──────────────┐
  │              │ ──────────── > │ MCP Server   │
  │              │                │ (메일 데이터)  │
  └──────┬───────┘                └──────────────┘
         │ A2A
         v
  ┌──────────────┐    A2A        ┌──────────────┐
  │ Check Agent  │ ──────────>   │ Notify Agent │
  │ (메일 감지)   │              │ (알림 전송)    │
  └──────────────┘              └──────────────┘

실행 방법:
  python3 mail_agent_demo.py

이 데모는 외부 서버 없이 단독으로 실행됩니다.
각 컴포넌트를 Mock으로 구현하여 아키텍처를 설명합니다.
"""

import asyncio
import json
from datetime import datetime


# ============================================================
# 1. Mock MCP Server (Chapter 4 참조)
# ============================================================
# 실제 환경에서는 별도 프로세스로 MCP 서버가 실행되고,
# Agent가 MCP 프로토콜로 메일 데이터에 접근합니다.
# 여기서는 동일한 인터페이스를 Mock으로 제공합니다.

class MockMCPMailServer:
    """
    MCP(Model Context Protocol) 메일 서버 시뮬레이터

    Chapter 4에서 구현한 MCP 서버의 인터페이스를 재현합니다.
    실제 MCP 서버는 IMAP/Gmail API를 통해 메일에 접근하지만,
    여기서는 Mock 데이터를 반환합니다.

    MCP Tool 목록:
      - list_emails: 메일 목록 조회
      - get_email: 메일 상세 조회
      - search_emails: 메일 검색
    """

    def __init__(self):
        self.name = "Mail MCP Server"
        self._emails = [
            {
                "id": "mail-001",
                "from": "ceo@company.com",
                "sender_name": "CEO 김대표",
                "to": "me@company.com",
                "subject": "[긴급] 내일 이사회 자료 준비 요청",
                "body": (
                    "내일 오전 10시 이사회에서 사용할 Q4 실적 자료를 "
                    "오늘 오후 6시까지 준비해주세요. "
                    "매출, 영업이익, 신규 고객 수를 포함해주세요."
                ),
                "timestamp": "2025-01-15T09:00:00",
                "important": True,
                "labels": ["긴급", "이사회"],
                "read": False,
            },
            {
                "id": "mail-002",
                "from": "hr@company.com",
                "sender_name": "HR팀 이과장",
                "to": "all@company.com",
                "subject": "2025년 연차 사용 계획 제출 안내",
                "body": (
                    "2025년도 연차 사용 계획을 1월 31일까지 "
                    "HR 시스템에 등록해주세요."
                ),
                "timestamp": "2025-01-15T10:30:00",
                "important": False,
                "labels": ["HR", "공지"],
                "read": False,
            },
            {
                "id": "mail-003",
                "from": "client-a@partner.com",
                "sender_name": "고객사A 박과장",
                "to": "me@company.com",
                "subject": "프로젝트 마일스톤 지연 관련 긴급 협의",
                "body": (
                    "2차 마일스톤이 1주일 지연되고 있습니다. "
                    "이번 주 금요일까지 긴급 회의를 요청드립니다. "
                    "지연 사유와 대응 방안을 함께 논의하고 싶습니다."
                ),
                "timestamp": "2025-01-15T11:15:00",
                "important": True,
                "labels": ["고객", "긴급", "프로젝트"],
                "read": False,
            },
            {
                "id": "mail-004",
                "from": "newsletter@tech.com",
                "sender_name": "Tech Weekly",
                "to": "subscribers@tech.com",
                "subject": "이번 주 AI/ML 뉴스 모음",
                "body": (
                    "1. OpenAI GPT-5 발표 임박\n"
                    "2. Google A2A 프로토콜 1.0 정식 출시\n"
                    "3. MCP 생태계 확장 현황"
                ),
                "timestamp": "2025-01-15T07:00:00",
                "important": False,
                "labels": ["뉴스레터"],
                "read": True,
            },
            {
                "id": "mail-005",
                "from": "security@company.com",
                "sender_name": "보안팀 최대리",
                "to": "dev-team@company.com",
                "subject": "[필독] 보안 패치 긴급 적용 안내",
                "body": (
                    "CVE-2025-XXXX 취약점이 발견되었습니다. "
                    "오늘 18시까지 반드시 패치를 적용해주세요. "
                    "적용 방법은 첨부 문서를 참고하세요."
                ),
                "timestamp": "2025-01-15T14:00:00",
                "important": True,
                "labels": ["보안", "긴급"],
                "read": False,
            },
            {
                "id": "mail-006",
                "from": "team-lead@company.com",
                "sender_name": "팀장 정수현",
                "to": "me@company.com",
                "subject": "주간 회의 안건 정리",
                "body": (
                    "이번 주 주간 회의 안건입니다:\n"
                    "1. 프로젝트 진행 현황\n"
                    "2. 신규 채용 면접 일정\n"
                    "3. Q1 목표 설정"
                ),
                "timestamp": "2025-01-15T15:30:00",
                "important": False,
                "labels": ["회의", "팀"],
                "read": False,
            },
        ]

    async def call_tool(self, tool_name: str, params: dict) -> dict:
        """
        MCP 프로토콜의 tools/call을 시뮬레이션합니다.

        실제 MCP 호출:
          POST http://mcp-server/
          {"jsonrpc": "2.0", "method": "tools/call", "params": {...}}

        여기서는 동일한 인터페이스를 직접 호출로 제공합니다.
        """
        if tool_name == "list_emails":
            return await self._list_emails(params)
        elif tool_name == "get_email":
            return await self._get_email(params)
        elif tool_name == "search_emails":
            return await self._search_emails(params)
        else:
            return {"error": f"알 수 없는 Tool: {tool_name}"}

    async def _list_emails(self, params: dict) -> dict:
        """메일 목록을 반환합니다."""
        filter_type = params.get("filter", "all")
        if filter_type == "unread":
            emails = [e for e in self._emails if not e["read"]]
        elif filter_type == "important":
            emails = [e for e in self._emails if e["important"]]
        else:
            emails = self._emails

        # 요약 정보만 반환 (MCP는 필요한 데이터만 제공)
        return {
            "total": len(emails),
            "emails": [
                {
                    "id": e["id"],
                    "from": e["sender_name"],
                    "subject": e["subject"],
                    "important": e["important"],
                    "timestamp": e["timestamp"],
                    "read": e["read"],
                }
                for e in emails
            ],
        }

    async def _get_email(self, params: dict) -> dict:
        """메일 상세 내용을 반환합니다."""
        email_id = params.get("email_id")
        for email in self._emails:
            if email["id"] == email_id:
                return {"email": email}
        return {"error": f"메일을 찾을 수 없습니다: {email_id}"}

    async def _search_emails(self, params: dict) -> dict:
        """메일을 검색합니다."""
        query = params.get("query", "").lower()
        results = [
            e for e in self._emails
            if query in e["subject"].lower() or query in e["body"].lower()
        ]
        return {
            "query": query,
            "results": len(results),
            "emails": [
                {"id": e["id"], "from": e["sender_name"], "subject": e["subject"]}
                for e in results
            ],
        }


# ============================================================
# 2. Mock Skills 엔진 (Chapter 4 참조)
# ============================================================
# SKILL.md 파일에 정의된 절차를 Agent에게 안내합니다.
# DeepAgents의 Skills 시스템을 간단히 재현합니다.

class MockSkillsEngine:
    """
    Skills 엔진 시뮬레이터

    Chapter 4에서 작성한 SKILL.md의 절차를 로드하고,
    Agent에게 단계별 가이드를 제공합니다.

    실제 DeepAgents에서는:
      harness.load_skill("mail_check")
      → SKILL.md를 시스템 프롬프트에 주입
      → Agent가 절차대로 작업 수행
    """

    def __init__(self):
        self.name = "Skills Engine"
        # SKILL.md 내용을 직접 정의 (실제로는 파일에서 로드)
        self.skills = {
            "mail_check": {
                "name": "메일 확인 절차",
                "steps": [
                    {
                        "step": 1,
                        "action": "MCP 서버를 통해 메일 목록을 조회합니다",
                        "tool": "list_emails",
                        "params": {"filter": "unread"},
                    },
                    {
                        "step": 2,
                        "action": "중요 메일을 필터링합니다",
                        "tool": "list_emails",
                        "params": {"filter": "important"},
                    },
                    {
                        "step": 3,
                        "action": "중요 메일의 상세 내용을 확인합니다",
                        "tool": "get_email",
                        "params": {"email_id": "{important_email_id}"},
                    },
                    {
                        "step": 4,
                        "action": "중요 메일이 있으면 Notify Agent에게 알림을 요청합니다",
                        "tool": "a2a_notify",
                        "params": {"target": "notify-agent"},
                    },
                ],
            },
        }

    def get_skill(self, skill_name: str) -> dict | None:
        """Skill 정의를 반환합니다."""
        return self.skills.get(skill_name)

    def get_step_guide(self, skill_name: str, step_num: int) -> str:
        """특정 단계의 가이드 텍스트를 반환합니다."""
        skill = self.skills.get(skill_name)
        if not skill:
            return f"[Skills] '{skill_name}' Skill을 찾을 수 없습니다."
        for step in skill["steps"]:
            if step["step"] == step_num:
                return (
                    f"[Skills 가이드 - Step {step_num}]\n"
                    f"  동작: {step['action']}\n"
                    f"  사용 Tool: {step['tool']}\n"
                    f"  파라미터: {json.dumps(step['params'], ensure_ascii=False)}"
                )
        return f"[Skills] Step {step_num}은 존재하지 않습니다."


# ============================================================
# 3. Mock A2A 통신 (Chapter 5 참조)
# ============================================================
# 실제 환경에서는 HTTP로 A2A 서버와 통신하지만,
# 여기서는 Mock으로 A2A 프로토콜의 흐름을 시뮬레이션합니다.

class MockA2AClient:
    """
    A2A 클라이언트 시뮬레이터

    Chapter 5의 Check Agent/Notify Agent 간 A2A 통신을
    Mock으로 재현합니다.

    실제 A2A 통신:
      POST http://localhost:5002/
      {"jsonrpc": "2.0", "method": "message/send", "params": {...}}

    여기서는 동일한 흐름을 인-프로세스로 시뮬레이션합니다.
    """

    def __init__(self):
        self.name = "A2A Client"
        # Agent Card 레지스트리 (실제로는 .well-known/agent-card.json에서 조회)
        self.agent_registry = {
            "check-agent": {
                "name": "Mail Check Agent",
                "url": "http://localhost:5001",
                "skills": ["check-mail"],
            },
            "notify-agent": {
                "name": "Notify Agent",
                "url": "http://localhost:5002",
                "skills": ["send-notification"],
            },
        }

    async def discover_agent(self, agent_id: str) -> dict | None:
        """
        Agent Card를 조회합니다. (A2A Discovery)

        실제:
          GET http://localhost:5002/.well-known/agent-card.json
        """
        agent = self.agent_registry.get(agent_id)
        if agent:
            print(f"    [A2A Discovery] {agent['name']} 발견 ({agent['url']})")
            print(f"    [A2A Discovery] 스킬: {agent['skills']}")
        return agent

    async def send_task(self, agent_id: str, task_message: str) -> dict:
        """
        Agent에게 A2A 태스크를 전송합니다.

        실제:
          POST http://localhost:5002/
          {
            "jsonrpc": "2.0",
            "method": "message/send",
            "params": {
              "message": {
                "role": "user",
                "message_id": "msg-001",
                "parts": [{"kind": "text", "text": "..."}]
              }
            }
          }
        """
        agent = self.agent_registry.get(agent_id)
        if not agent:
            return {"error": f"Agent '{agent_id}'를 찾을 수 없습니다."}

        print(f"    [A2A] {agent['name']}에게 태스크 전송 중...")
        print(f"    [A2A] URL: {agent['url']}")
        print(f"    [A2A] 메시지: {task_message[:80]}...")

        # Mock 응답 (실제로는 Agent가 처리 후 응답)
        if agent_id == "notify-agent":
            return await self._mock_notify_response(task_message)
        elif agent_id == "check-agent":
            return await self._mock_check_response(task_message)
        else:
            return {"status": "completed", "message": "처리 완료"}

    async def _mock_notify_response(self, message: str) -> dict:
        """Notify Agent 응답 시뮬레이션"""
        # 실제로는 Notify Agent가 Slack, 이메일 등으로 알림 전송
        print()
        print("    " + "=" * 46)
        print("    [SLACK 알림 시뮬레이션]")
        print("    " + "=" * 46)
        print(f"    채널: #important-alerts")
        print(f"    시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"    ---")
        for line in message.split("\n"):
            print(f"    {line}")
        print("    " + "=" * 46)
        print()

        return {
            "status": "completed",
            "channels_notified": ["slack", "console", "email"],
            "message": "알림 전송 완료 (3개 채널)",
        }

    async def _mock_check_response(self, message: str) -> dict:
        """Check Agent 응답 시뮬레이션"""
        return {
            "status": "completed",
            "important_count": 3,
            "total_count": 6,
            "message": "메일 확인 완료",
        }


# ============================================================
# 4. DeepAgents Harness (Chapter 3 참조)
# ============================================================
# DeepAgents의 Harness가 전체 파이프라인을 오케스트레이션합니다.
# 주기적으로 폴링하며, Skills 절차에 따라 작업을 수행합니다.

class MockDeepAgentsHarness:
    """
    DeepAgents Harness 시뮬레이터

    Chapter 3에서 배운 DeepAgents 프레임워크의 Harness 역할을 합니다.
    - 폴링으로 주기적 실행
    - Skills에서 절차를 로드
    - MCP로 데이터 접근
    - A2A로 다른 Agent와 협업

    실제 DeepAgents:
      harness = Harness(config={...})
      harness.register_skill("mail_check", "./skills/SKILL.md")
      harness.register_mcp_server("mail", "http://localhost:3000")
      harness.run()  # 폴링 시작
    """

    def __init__(
        self,
        mcp_server: MockMCPMailServer,
        skills_engine: MockSkillsEngine,
        a2a_client: MockA2AClient,
    ):
        self.mcp_server = mcp_server
        self.skills_engine = skills_engine
        self.a2a_client = a2a_client
        self.poll_count = 0

    async def run_polling_cycle(self) -> dict:
        """
        1회 폴링 사이클을 실행합니다.

        DeepAgents Harness의 폴링 루프 1회차에 해당합니다.
        실제 환경에서는 설정된 간격(예: 5분)마다 자동 실행됩니다.

        폴링 사이클:
          1. Skills에서 절차 로드
          2. 절차에 따라 MCP로 메일 데이터 접근
          3. 중요 메일 분석
          4. 필요 시 A2A로 Notify Agent에게 알림 요청
        """
        self.poll_count += 1
        cycle_result = {
            "cycle": self.poll_count,
            "timestamp": datetime.now().isoformat(),
            "steps": [],
            "important_emails": [],
            "notification_sent": False,
        }

        print()
        print("#" * 60)
        print(f"# 폴링 사이클 #{self.poll_count}")
        print(f"# 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("#" * 60)

        # ---- Step 1: Skills에서 절차 로드 ----
        print()
        print("  [Step 1] Skills 엔진에서 절차 로드")
        print("  " + "-" * 44)
        skill = self.skills_engine.get_skill("mail_check")
        if not skill:
            print("  [오류] mail_check Skill을 찾을 수 없습니다.")
            return cycle_result

        print(f"  Skill 이름: {skill['name']}")
        print(f"  절차 수: {len(skill['steps'])}단계")
        for step in skill["steps"]:
            print(f"    Step {step['step']}: {step['action']}")

        cycle_result["steps"].append({
            "name": "skills_load",
            "status": "완료",
            "detail": f"{skill['name']} 로드됨 ({len(skill['steps'])}단계)",
        })

        # ---- Step 2: MCP로 전체 메일 목록 조회 ----
        print()
        print("  [Step 2] MCP 서버에서 미읽음 메일 조회")
        print("  " + "-" * 44)
        guide = self.skills_engine.get_step_guide("mail_check", 1)
        print(f"  {guide}")
        print()

        unread_result = await self.mcp_server.call_tool(
            "list_emails", {"filter": "unread"}
        )
        print(f"  MCP 응답: 미읽음 메일 {unread_result['total']}통")
        for email in unread_result["emails"]:
            marker = "[중요]" if email["important"] else "[일반]"
            status = "미읽음" if not email["read"] else "읽음"
            print(f"    {marker} [{status}] {email['from']}: {email['subject']}")

        cycle_result["steps"].append({
            "name": "mcp_list_unread",
            "status": "완료",
            "detail": f"미읽음 메일 {unread_result['total']}통 조회",
        })

        # ---- Step 3: MCP로 중요 메일 필터링 ----
        print()
        print("  [Step 3] MCP 서버에서 중요 메일 필터링")
        print("  " + "-" * 44)
        guide = self.skills_engine.get_step_guide("mail_check", 2)
        print(f"  {guide}")
        print()

        important_result = await self.mcp_server.call_tool(
            "list_emails", {"filter": "important"}
        )
        important_emails = important_result["emails"]
        print(f"  MCP 응답: 중요 메일 {important_result['total']}통 감지!")
        for email in important_emails:
            print(f"    * {email['from']}: {email['subject']}")

        cycle_result["important_emails"] = important_emails
        cycle_result["steps"].append({
            "name": "mcp_filter_important",
            "status": "완료",
            "detail": f"중요 메일 {important_result['total']}통 감지",
        })

        # ---- Step 4: 중요 메일 상세 내용 확인 ----
        print()
        print("  [Step 4] 중요 메일 상세 내용 확인")
        print("  " + "-" * 44)
        guide = self.skills_engine.get_step_guide("mail_check", 3)
        print(f"  {guide}")
        print()

        email_details = []
        for email in important_emails:
            detail = await self.mcp_server.call_tool(
                "get_email", {"email_id": email["id"]}
            )
            if "email" in detail:
                e = detail["email"]
                print(f"    [{e['sender_name']}] {e['subject']}")
                print(f"      내용: {e['body'][:60]}...")
                print(f"      라벨: {', '.join(e['labels'])}")
                email_details.append(e)

        cycle_result["steps"].append({
            "name": "mcp_get_details",
            "status": "완료",
            "detail": f"중요 메일 {len(email_details)}통 상세 확인",
        })

        # ---- Step 5: A2A로 Notify Agent에게 알림 요청 ----
        if important_emails:
            print()
            print("  [Step 5] A2A로 Notify Agent에게 알림 요청")
            print("  " + "-" * 44)
            guide = self.skills_engine.get_step_guide("mail_check", 4)
            print(f"  {guide}")
            print()

            # 5-1. Notify Agent Discovery
            print("  5-1. Notify Agent 검색 (A2A Discovery)")
            notify_agent = await self.a2a_client.discover_agent("notify-agent")

            if notify_agent:
                # 5-2. 알림 메시지 구성
                notification_lines = [
                    f"중요 메일 {len(important_emails)}통이 감지되었습니다!",
                    "",
                ]
                for email in important_emails:
                    notification_lines.append(
                        f"- [{email['from']}] {email['subject']}"
                    )
                notification_message = "\n".join(notification_lines)

                # 5-3. A2A 태스크 전송
                print()
                print("  5-2. A2A 태스크 전송")
                notify_result = await self.a2a_client.send_task(
                    "notify-agent", notification_message
                )

                print(f"  5-3. Notify Agent 응답:")
                print(f"    상태: {notify_result.get('status', 'unknown')}")
                print(f"    채널: {notify_result.get('channels_notified', [])}")
                print(f"    메시지: {notify_result.get('message', '')}")

                cycle_result["notification_sent"] = True
                cycle_result["steps"].append({
                    "name": "a2a_notify",
                    "status": "완료",
                    "detail": f"알림 전송 완료 ({notify_result.get('message', '')})",
                })
            else:
                print("    [경고] Notify Agent를 찾을 수 없습니다!")
                cycle_result["steps"].append({
                    "name": "a2a_notify",
                    "status": "실패",
                    "detail": "Notify Agent 미발견",
                })
        else:
            print()
            print("  [Step 5] 중요 메일 없음 - 알림 건너뜀")
            cycle_result["steps"].append({
                "name": "a2a_notify",
                "status": "건너뜀",
                "detail": "중요 메일 없음",
            })

        return cycle_result


# ============================================================
# 5. 통합 데모 실행
# ============================================================

async def run_integration_demo():
    """
    End-to-End 통합 데모를 실행합니다.

    1회 폴링 사이클 + 결과 요약을 수행합니다.
    실제 환경에서는 이 사이클이 설정된 간격으로 반복됩니다.
    """
    print()
    print("=" * 60)
    print("Chapter 6: 메일 Agent 통합 데모")
    print("=" * 60)
    print()
    print("이 데모는 Chapter 2~5의 모든 개념을 통합합니다:")
    print("  - Chapter 2: Agent Loop (LangGraph)")
    print("  - Chapter 3: DeepAgents Harness (오케스트레이션)")
    print("  - Chapter 4: Skills (절차 안내) + MCP (데이터 접근)")
    print("  - Chapter 5: A2A (Agent 간 통신)")
    print()
    print("아키텍처:")
    print("  ┌──────────────┐     Skills     ┌──────────────┐")
    print("  │  DeepAgents  │ ──────────── > │   SKILL.md   │")
    print("  │   Harness    │                │  (절차 안내)   │")
    print("  │   (폴링)     │     MCP        ┌──────────────┐")
    print("  │              │ ──────────── > │ MCP Server   │")
    print("  │              │                │ (메일 데이터)  │")
    print("  └──────┬───────┘                └──────────────┘")
    print("         │ A2A")
    print("         v")
    print("  ┌──────────────┐    A2A        ┌──────────────┐")
    print("  │ Check Agent  │ ──────────>   │ Notify Agent │")
    print("  │ (메일 감지)   │              │ (알림 전송)    │")
    print("  └──────────────┘              └──────────────┘")
    print()
    print("-" * 60)

    # ---- 컴포넌트 초기화 ----
    print()
    print("[초기화] 컴포넌트 생성 중...")
    mcp_server = MockMCPMailServer()
    skills_engine = MockSkillsEngine()
    a2a_client = MockA2AClient()
    harness = MockDeepAgentsHarness(mcp_server, skills_engine, a2a_client)

    print(f"  MCP Server: {mcp_server.name} (메일 {len(mcp_server._emails)}통)")
    print(f"  Skills Engine: {skills_engine.name} (Skill {len(skills_engine.skills)}개)")
    print(f"  A2A Client: {a2a_client.name} (Agent {len(a2a_client.agent_registry)}개)")
    print(f"  Harness: 초기화 완료")

    # ---- 폴링 사이클 1회 실행 ----
    result = await harness.run_polling_cycle()

    # ---- 결과 요약 ----
    print()
    print("=" * 60)
    print("실행 결과 요약")
    print("=" * 60)
    print(f"  폴링 사이클: #{result['cycle']}")
    print(f"  실행 시각: {result['timestamp']}")
    print(f"  수행 단계: {len(result['steps'])}단계")
    print()
    print("  단계별 결과:")
    for step in result["steps"]:
        status_mark = {
            "완료": "[OK]",
            "실패": "[FAIL]",
            "건너뜀": "[SKIP]",
        }.get(step["status"], "[?]")
        print(f"    {status_mark} {step['name']}: {step['detail']}")
    print()
    print(f"  중요 메일: {len(result['important_emails'])}통 감지")
    print(f"  알림 전송: {'완료' if result['notification_sent'] else '미전송'}")

    # ---- 연속 폴링 시뮬레이션 (2회 더) ----
    print()
    print("-" * 60)
    print("연속 폴링 시뮬레이션 (빠른 실행, 결과만 요약)")
    print("-" * 60)

    for i in range(2):
        print(f"\n  --- 추가 폴링 사이클 (요약) ---")
        # 실제로는 시간 간격을 두고 실행
        # await asyncio.sleep(300)  # 5분 대기 (데모에서는 생략)

        # 간단한 요약만 출력
        additional_result = await harness.run_polling_cycle()
        print(f"  사이클 #{additional_result['cycle']}: "
              f"중요 메일 {len(additional_result['important_emails'])}통, "
              f"알림 {'전송됨' if additional_result['notification_sent'] else '없음'}")

    return result


# ============================================================
# 6. 메인 실행
# ============================================================

def main():
    """동기 진입점"""
    result = asyncio.run(run_integration_demo())

    # ---- 핵심 정리 ----
    print()
    print()
    print("=" * 60)
    print("핵심 정리: 전체 아키텍처 복습")
    print("=" * 60)
    print("""
  Harness(Ch3)  : 폴링·오케스트레이션 — "언제, 무엇을"
  Skills(Ch4)   : SKILL.md 절차 가이드 — "어떤 순서로"
  MCP(Ch4)      : 표준 데이터 접근 — "데이터를 어디서"
  A2A(Ch5)      : Agent 간 통신 — "다른 Agent와 어떻게"

  운영 전환: Mock → 실제 MCP 서버(IMAP/Gmail), A2A HTTP, DeepAgents Harness
  장점: 관심사 분리, 독립 배포, 표준 프로토콜(MCP/A2A), Agent Card로 확장
""")


if __name__ == "__main__":
    main()
