"""Ch5 제공 모듈 — 브리프 교정 제안 에이전트(A2A 서버, :9620).

검증 에이전트(verifier_agent.py)가 NEEDS_REVISION을 내면, 그 '누락 항목'을 이 에이전트에
A2A로 넘긴다. 이 에이전트는 브리프를 어떻게 고칠지 구체적 교정문을 만들어 Artifact로 돌려준다.

역할 분담이 곧 A2A의 요지다:
  검증자 = 무엇이 틀렸나(detect)   ·   교정자 = 어떻게 고치나(draft)
두 에이전트는 서로의 내부를 모른 채 Task 메시지만 주고받는다(블랙박스).
재현성을 위해 LLM 없이 규칙으로 동작한다.

실행:
    uv run python3 ch5-a2a/reviser_agent.py        # http://localhost:9620
"""

from __future__ import annotations

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

PORT = 9620
URL = f"http://localhost:{PORT}"


#pragma region draft-revision
def draft_revision(payload: str) -> str:
    """누락 항목(줄마다 'name|amount')을 받아 구체적 교정 제안을 만든다."""
    items: list[tuple[str, str]] = []
    for line in payload.splitlines():
        if "|" in line:
            name, _, amount = line.partition("|")
            items.append((name.strip(), amount.strip()))
    if not items:
        return "교정할 항목이 전달되지 않았습니다."
    lines = ["브리프의 '### 짚을 점'에 아래를 추가하거나 금액을 바로잡으세요:"]
    for name, amount in items:
        try:
            shown = f"{float(amount):,.0f}원"
        except ValueError:
            shown = amount
        lines.append(f"- **{name}** — 카드 명세서 {shown}에 대응 영수증이 없습니다(확인 필요).")
    return "\n".join(lines)
#pragma endregion draft-revision


class ReviserExecutor(AgentExecutor):
    """누락 항목을 받아 교정 제안을 아티팩트로 돌려준다."""

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        payload = context.get_user_input()
        await event_queue.enqueue_event(Task(
            id=context.task_id,
            context_id=context.context_id,
            status=TaskStatus(state=TaskState.TASK_STATE_SUBMITTED),
            history=[context.message] if context.message else [],
        ))
        updater = TaskUpdater(event_queue=event_queue, task_id=context.task_id,
                              context_id=context.context_id)
        await updater.start_work(message=updater.new_agent_message(
            parts=[Part(text="교정 제안을 만드는 중...")]))
        body = "## 교정 제안 (교정 에이전트, A2A 위임)\n\n" + draft_revision(payload)
        await updater.add_artifact(parts=[Part(text=body)], name="revision", last_chunk=True)
        await updater.complete()

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise NotImplementedError("취소는 지원하지 않습니다")


def agent_card() -> AgentCard:
    return AgentCard(
        name="브리프 교정 제안 에이전트",
        description="검증에서 드러난 누락 항목을 받아 브리프를 어떻게 고칠지 구체적으로 제안한다.",
        version="1.0.0",
        capabilities=AgentCapabilities(streaming=False),
        supported_interfaces=[AgentInterface(
            url=URL, protocol_binding="JSONRPC", protocol_version="1.0")],
        default_input_modes=["text/plain"],
        default_output_modes=["text/plain"],
        skills=[AgentSkill(
            id="revise-brief",
            name="브리프 교정 제안",
            description="누락·불일치 항목을 받아 '짚을 점'에 넣을 교정문을 만든다.",
            tags=["revise", "suggest", "draft"],
            examples=["이 누락 항목들로 교정문을 만들어줘"],
        )],
    )


def create_app() -> Starlette:
    card = agent_card()
    handler = DefaultRequestHandler(
        agent_executor=ReviserExecutor(),
        task_store=InMemoryTaskStore(),
        agent_card=card,
    )
    routes = create_agent_card_routes(agent_card=card)
    routes += create_jsonrpc_routes(request_handler=handler, rpc_url="/", enable_v0_3_compat=True)
    return Starlette(routes=routes)


if __name__ == "__main__":
    print(f"브리프 교정 제안 에이전트 시작 → {URL}")
    print(f"Agent Card → {URL}/.well-known/agent-card.json")
    uvicorn.run(create_app(), host="0.0.0.0", port=PORT, log_level="warning")
