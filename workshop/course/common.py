"""공통 데이터·모델 연결. fixed는 실제 LLM이 아닌 결정론 응답 모델입니다."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult

ROOT = Path(__file__).resolve().parents[1]
POLICIES = {
    "정산": {"id": "P-01", "team": "재무지원팀", "rule": "정산 문의는 재무지원팀에 전달합니다."},
    "계정": {"id": "P-02", "team": "IT지원팀", "rule": "계정 잠금은 IT지원팀에 문의합니다."},
}


#pragma region lookup
def lookup_policy(topic: str) -> str:
    """Look up the current internal policy for a business topic."""
    policy = POLICIES.get(topic)
    return json.dumps({"found": bool(policy), "topic": topic, "policy": policy}, ensure_ascii=False)
#pragma endregion lookup


class FixedModel(BaseChatModel):
    """네트워크 없이 tool request→ToolMessage→답변을 관찰하는 제공 모델."""
    @property
    def _llm_type(self) -> str:
        return "workshop-fixed-not-an-llm"

    def bind_tools(self, tools: Any, **kwargs: Any) -> FixedModel:
        return self

    def _generate(self, messages: list, stop=None, run_manager=None, **kwargs) -> ChatResult:
        if isinstance(messages[-1], ToolMessage):
            data = json.loads(messages[-1].content)
            policy = data.get("policy")
            content = (f"{policy['rule']} [근거: {policy['id']}]" if policy else "등록된 규정이 없어 추가 확인이 필요합니다.")
            reply = AIMessage(content=content)
        else:
            request = next(m.content for m in reversed(messages) if m.type == "human")
            topic = json.loads(request)["topic"]
            reply = AIMessage(content="", tool_calls=[{
                "name": "lookup_policy", "args": {"topic": topic}, "id": "lookup-1", "type": "tool_call",
            }])
        return ChatResult(generations=[ChatGeneration(message=reply)])


def get_model(mode: str):
    if mode == "fixed":
        return FixedModel()
    load_dotenv(ROOT / ".env")
    load_dotenv(ROOT.parent / ".env")
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise RuntimeError("OPENROUTER_API_KEY가 없습니다. workshop/.env를 확인하십시오.")
    from langchain_openai import ChatOpenAI
    return ChatOpenAI(model=os.getenv("WORKSHOP_MODEL", "google/gemini-3.1-flash-lite"),
                      api_key=key, base_url="https://openrouter.ai/api/v1", temperature=0,
                      timeout=45, max_retries=1, max_tokens=1500)


def trace_messages(messages: list) -> list[dict]:
    return [{"role": m.type, "content": m.content,
             **({"tool_calls": m.tool_calls} if getattr(m, "tool_calls", None) else {})}
            for m in messages]
