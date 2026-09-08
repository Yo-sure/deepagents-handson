"""공통 정책 데이터와 실제 LLM 연결입니다."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

from .policy_store import load_policies, search_policy

ROOT = Path(__file__).resolve().parents[1]

POLICIES = load_policies()


# region lookup
def lookup_policy(topic: str) -> str:
    """Look up the current internal policy for a business topic."""
    return search_policy(topic)


# endregion lookup


def get_model():
    load_dotenv(ROOT / ".env")
    load_dotenv(ROOT.parent / ".env")
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise RuntimeError(
            "OPENROUTER_API_KEY가 없습니다. workshop/.env를 확인하십시오."
        )
    from langchain_openai import ChatOpenAI

    return ChatOpenAI(
        model=os.getenv("WORKSHOP_MODEL", "google/gemini-3.8-flash"),
        api_key=key,
        base_url="https://openrouter.ai/api/v1",
        temperature=0,
        timeout=45,
        max_retries=1,
        max_tokens=1500,
    )


def trace_messages(messages: list) -> list[dict]:
    return [
        {
            "role": m.type,
            "content": m.content,
            **({"tool_calls": m.tool_calls} if getattr(m, "tool_calls", None) else {}),
        }
        for m in messages
    ]
