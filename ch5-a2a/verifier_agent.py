"""Ch5 제공 모듈 — 외부 검증 에이전트(A2A 서버, a2a-sdk 1.1.0).

브리프 작성 경로와 검증 경로가 같으면 같은 가정 때문에 누락을 놓칠 수 있다.
검증을 다른 프로세스로 분리하고 A2A 메시지로 제출한다. 이 검증 에이전트는 과정에서
'제공 모듈'로 주어진다. 재현성을 위해 LLM 없이 규칙으로 동작한다.

A2A 서버 뼈대(공식 1.1.0)
  AgentExecutor 구현 → DefaultRequestHandler(+AgentCard·TaskStore)
  → create_agent_card_routes + create_jsonrpc_routes → Starlette → uvicorn.
Agent Card는 /.well-known/agent-card.json 에 노출되는 메타데이터와 skill 목록이다.

하는 일: 브리프의 '짚을 점'이 실제 분류 레코드와 맞는지 독립 재계산으로 대사한다.

실행:
    uv run python3 ch5-a2a/verifier_agent.py        # http://localhost:9610
"""

from __future__ import annotations

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


#pragma region verify-brief
def verify_brief(brief_text: str) -> tuple[bool, list[str]]:
    """브리프를 레코드와 다시 대사한다 — (통과여부, 근거 목록)."""
    records = load_records()
    receipts = by_type(records, "영수증")
    card = next((r for r in by_type(records, "명세서") if "카드" in r.merchant), None)
    if not card:
        return False, ["카드 명세서를 찾지 못해 검증 불가"]
    real_gaps = [
        (item.name, item.amount or 0)
        for item in card.items
        if not any(abs(r.total - (item.amount or 0)) < 1.0 for r in receipts)
    ]
    missing = [
        name for name, amount in real_gaps
        if name.split("(")[0] not in brief_text
        or (f"{amount:,.0f}" not in brief_text and f"{amount:.0f}" not in brief_text)
    ]
    notes = [f"독립 재계산: 영수증 없는 거래 {len(real_gaps)}건 "
             f"({', '.join(f'{n} {a:,.0f}원' for n, a in real_gaps)})"]
    if missing:
        notes.append(f"브리프가 누락했거나 금액을 틀린 항목: {', '.join(missing)} — 보완 필요")
        return False, notes
    notes.append("누락 항목 없음 — 검증 통과")
    return True, notes
#pragma endregion verify-brief


class VerifierExecutor(AgentExecutor):
    """A2A 요청(브리프 텍스트)을 받아 검증 결과를 아티팩트로 돌려준다."""

#pragma region execute
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        brief = context.get_user_input()
        ok, notes = verify_brief(brief)
        verdict = "PASS" if ok else "NEEDS_REVISION"
        body = (f"## 외부 검증 결과 — {verdict}\n검증 주체: 세무·정합성 검증 에이전트 (A2A)\n\n"
                + "\n".join(f"- {n}" for n in notes))

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
