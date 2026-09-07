"""LLM 대신 정해진 메시지를 반환하는 테스트 전용 모델."""
from __future__ import annotations
import json
from typing import Any
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult


class ToolCallingStub(BaseChatModel):
    @property
    def _llm_type(self) -> str:
        return "test-tool-calling-stub"

    def bind_tools(self, tools: Any, **kwargs: Any):
        return self

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        if isinstance(messages[-1], ToolMessage):
            content = messages[-1].content
            if isinstance(content, list):
                content = "".join(x if isinstance(x, str) else x.get("text", "") for x in content)
            policy = json.loads(content).get("policy")
            answer = f"{policy['rule']} [근거: {policy['id']}]" if policy else "등록된 규정이 없어 추가 확인이 필요합니다."
            reply = AIMessage(content=answer)
        else:
            request = next(m.content for m in reversed(messages) if m.type == "human")
            try:
                topic = json.loads(request)["topic"]
            except (ValueError, KeyError, TypeError):
                reply = AIMessage(content="테스트용 표현 검토 결과입니다.")
            else:
                reply = AIMessage(content="", tool_calls=[{
                    "name": "lookup_policy", "args": {"topic": topic},
                    "id": "lookup-test", "type": "tool_call",
                }])
        return ChatResult(generations=[ChatGeneration(message=reply)])
