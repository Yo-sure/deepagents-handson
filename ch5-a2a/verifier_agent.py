"""Ch5 제공 모듈 — 외부 검증 에이전트(A2A 서버, a2a-sdk 1.1+).

브리프 작성 경로와 검증 경로가 같으면 같은 가정 때문에 누락을 놓칠 수 있다.
검증을 다른 프로세스로 분리하고 A2A 메시지로 제출한다. 이 검증 에이전트는 과정에서
'제공 모듈'로 주어진다. 재현성을 위해 LLM 없이 규칙으로 동작한다.

A2A 서버 뼈대(1.1+ lockfile 기준)
  AgentExecutor 구현 → DefaultRequestHandler(+AgentCard·TaskStore)
  → create_agent_card_routes + create_jsonrpc_routes → Starlette → uvicorn.
Agent Card는 /.well-known/agent-card.json 에 노출되는 메타데이터와 skill 목록이다.

하는 일: 브리프의 '짚을 점'이 실제 분류 레코드와 맞는지 독립 재계산으로 대사한다.

실행:
    uv run python3 ch5-a2a/verifier_agent.py        # http://localhost:9610
"""

from __future__ import annotations

import re
import sys
import os
from pathlib import Path

import uvicorn
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import create_agent_card_routes, create_jsonrpc_routes
from a2a.server.tasks import InMemoryTaskStore
from a2a.server.tasks.task_updater import TaskUpdater
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentInterface,
    AgentSkill,
    Part,
    Task,
    TaskState,
    TaskStatus,
)
from starlette.applications import Starlette

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ch3-deepagents"))
from research_orchestrator import by_type, load_records

PORT = 9610
URL = f"http://localhost:{PORT}"
REVISER_URL = "http://localhost:9620"   # 교정 제안 에이전트 — 문제가 있을 때만 A2A로 위임


#pragma region verify-brief
def _amount_present(amount: float, text: str) -> bool:
    """금액이 본문에 — 더 큰 수의 일부가 아니라 — 독립된 수로 등장하는지.

    단순 substring이면 '89,000'이 '189,000'의 일부로 우연히 매칭돼
    틀린 금액이 가짜 통과(false PASS)된다. 앞뒤 숫자 경계를 둬 막는다.
    """
    for s in (f"{amount:,.0f}", f"{amount:.0f}"):
        if re.search(rf"(?<!\d){re.escape(s)}(?!\d)", text):
            return True
    return False


def verify_brief(brief_text: str) -> tuple[bool, list[str], list[tuple[str, float]]]:
    """브리프를 레코드와 다시 대사한다 — (통과여부, 근거 목록, 누락 항목[이름·금액])."""
    records = load_records()
    receipts = by_type(records, "영수증")
    card = next((r for r in by_type(records, "명세서") if "카드" in r.merchant), None)
    if not card:
        return False, ["카드 명세서를 찾지 못해 검증 불가"], []
    real_gaps = [
        (item.name, item.amount or 0)
        for item in card.items
        if not any(abs(r.total - (item.amount or 0)) < 1.0 for r in receipts)
    ]
    missing = [
        (name, amount) for name, amount in real_gaps
        if name.split("(")[0] not in brief_text
        or not _amount_present(amount, brief_text)
    ]
    notes = [f"독립 재계산: 영수증 없는 거래 {len(real_gaps)}건 "
             f"({', '.join(f'{n} {a:,.0f}원' for n, a in real_gaps)})"]
    if missing:
        notes.append("브리프가 누락했거나 금액을 틀린 항목: "
                     f"{', '.join(n for n, _ in missing)} — 보완 필요")
        return False, notes, missing
    notes.append("누락 항목 없음 — 검증 통과")
    return True, notes, []
#pragma endregion verify-brief


async def request_revision(missing: list[tuple[str, float]]) -> str | None:
    """에이전트→에이전트 위임 — 누락 항목을 교정 에이전트(:9620)에 A2A로 넘겨 교정 제안을 받는다.

    검증자는 '무엇이 틀렸나'(detect)까지만 하고, '어떻게 고치나'(draft)는 다른 에이전트에 맡긴다.
    교정 에이전트가 안 떠 있으면(None) 검증 결과만 돌려주고 조용히 넘어간다(느슨한 결합).
    """
    import uuid

    import httpx
    from a2a.client import A2ACardResolver, ClientConfig, ClientFactory
    from a2a.types import Message, Part, Role, SendMessageConfiguration, SendMessageRequest

    payload = "\n".join(f"{name}|{amount:.0f}" for name, amount in missing)
    try:
        async with httpx.AsyncClient(timeout=10.0) as http:
            card = await A2ACardResolver(httpx_client=http, base_url=REVISER_URL).get_agent_card()
            print(f"  [위임] 문제 발견 → 교정 에이전트 호출: {card.name} (skill: {card.skills[0].id})",
                  flush=True)
            client = ClientFactory(config=ClientConfig(httpx_client=http, streaming=False)).create(card=card)
            req = SendMessageRequest(
                message=Message(role=Role.ROLE_USER, message_id=str(uuid.uuid4()),
                                parts=[Part(text=payload)]),
                configuration=SendMessageConfiguration(return_immediately=False))
            out: list[str] = []
            async for resp in client.send_message(request=req):
                r = resp[0] if isinstance(resp, tuple) else resp
                if getattr(r, "task", None):
                    for art in r.task.artifacts:
                        out += [p.text for p in art.parts if p.text]
            return "\n".join(out).strip() or None
    except Exception:
        return None   # 교정 에이전트 미연결 — 검증 결과만 반환


class VerifierExecutor(AgentExecutor):
    """A2A 요청(브리프 텍스트)을 받아 검증하고, 문제가 있으면 교정 에이전트에 위임한다."""

#pragma region execute
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        brief = context.get_user_input()
        # A2A 규칙: 상태 갱신 전에 Task를 먼저 enqueue 한다.
        if os.getenv("A2A_BREAK_TASK_ORDER") != "1":
            await event_queue.enqueue_event(Task(
                id=context.task_id,
                context_id=context.context_id,
                status=TaskStatus(state=TaskState.TASK_STATE_SUBMITTED),
                history=[context.message] if context.message else [],
            ))
        updater = TaskUpdater(event_queue=event_queue, task_id=context.task_id,
                              context_id=context.context_id)
        await updater.start_work(message=updater.new_agent_message(
            parts=[Part(text="브리프를 레코드와 대사하는 중...")]))

        ok, notes, missing = verify_brief(brief)
        verdict = "PASS" if ok else "NEEDS_REVISION"
        body = (f"## 외부 검증 결과 — {verdict}\n검증 주체: 세무·정합성 검증 에이전트 (A2A)\n\n"
                + "\n".join(f"- {n}" for n in notes))
        if not ok:
            # 에이전트→에이전트: 문제를 찾았으면 교정 제안은 다른 에이전트에 맡긴다.
            revision = await request_revision(missing)
            body += ("\n\n" + revision) if revision else (
                "\n\n> 교정 에이전트(:9620) 미연결 — 교정 제안 생략. "
                "다른 터미널에서 reviser_agent.py를 띄우면 제안이 함께 붙습니다.")
        await updater.add_artifact(parts=[Part(text=body)], name="verdict", last_chunk=True)
        await updater.complete()
#pragma endregion execute

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise NotImplementedError("취소는 지원하지 않습니다")


def agent_card() -> AgentCard:
    return AgentCard(
        name="세무·정합성 검증 에이전트",
        description="제출된 인박스 브리프를 분류 레코드와 대사해 누락·불일치를 검증한다.",
        version="1.0.0",
        capabilities=AgentCapabilities(streaming=False),
        supported_interfaces=[AgentInterface(
            url=URL, protocol_binding="JSONRPC", protocol_version="1.0")],
        default_input_modes=["text/plain"],
        default_output_modes=["text/plain"],
        skills=[AgentSkill(
            id="verify-brief",
            name="브리프 검증",
            description="브리프의 '짚을 점'이 실제 레코드와 맞는지 독립 재계산으로 확인한다.",
            tags=["verify", "reconcile", "audit"],
            examples=["이 브리프를 검증해줘", "짚을 점이 빠지지 않았는지 확인"],
        )],
    )


def create_app() -> Starlette:
    card = agent_card()
    handler = DefaultRequestHandler(
        agent_executor=VerifierExecutor(),
        task_store=InMemoryTaskStore(),
        agent_card=card,
    )
    routes = create_agent_card_routes(agent_card=card)
    routes += create_jsonrpc_routes(request_handler=handler, rpc_url="/", enable_v0_3_compat=True)
    return Starlette(routes=routes)


if __name__ == "__main__":
    print(f"세무·정합성 검증 에이전트 시작 → {URL}")
    print(f"Agent Card → {URL}/.well-known/agent-card.json")
    uvicorn.run(create_app(), host="0.0.0.0", port=PORT, log_level="warning")
