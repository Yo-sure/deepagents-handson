"""Ch5 — 진짜 agent가 A2A로 외부 검증자를 발견·선택·호출한다 (작은 LLM 에이전트).

a2a_verify.py의 클라이언트는 카드를 읽고 브리프를 '항상' 보냅니다(고정 절차). 여기서는
LLM 에이전트가 <em>스스로</em> 정합니다: 먼저 검증자를 발견해 verify-brief 능력이 있는지 보고,
있으면 그때 브리프를 A2A로 보내 판정을 받습니다. 도구 두 개(discover·send)만 주고 순서는
모델이 정합니다 — 그래서 '진짜 agent가 A2A를 쓴다'가 됩니다.

전제: 검증자 서버가 떠 있어야 합니다 — 다른 터미널에서 `uv run python3 ch5-a2a/verifier_agent.py`.
실행:
    uv run python3 ch5-a2a/a2a_agent_client.py            # 키 있으면 LLM 에이전트가 판단
    uv run python3 ch5-a2a/a2a_agent_client.py --offline   # 키 없이 같은 발견→호출 흐름(결정만 코드)
"""

from __future__ import annotations

import asyncio
import json
import os
import sys

import httpx
from a2a.client import A2ACardResolver

from a2a_verify import VERIFIER_URL, read_brief, verify_via_a2a, wait_for_server

LIVE_MODEL = "openai:anthropic/claude-haiku-4.5"   # 도구 호출 안정(Ch3·4와 동일)
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


async def discover_verifier() -> str:
    """검증자의 Agent Card를 읽어 이름과 skill 목록을 돌려준다(발견·능력 확인)."""
    async with httpx.AsyncClient(timeout=15.0) as http:
        card = await A2ACardResolver(httpx_client=http, base_url=VERIFIER_URL).get_agent_card()
    return json.dumps({"name": card.name, "skills": [s.id for s in card.skills]}, ensure_ascii=False)


#pragma region a2a-agent
async def run_agent(brief: str) -> None:
    """LLM 에이전트: 카드로 발견 → verify-brief 능력 확인 → A2A로 브리프 보내 판정 받기.

    도구 둘만 주고 시스템 프롬프트로 목표만 준다. '발견하고, 능력을 확인하고, 보낸다'는 순서를
    모델이 스스로 밟는다 — 고정 절차가 아니라 에이전트의 도구 선택으로.
    """
    from langchain.agents import create_agent
    from langchain_core.tools import tool
    from langchain_openai import ChatOpenAI

    @tool
    async def discover() -> str:
        """외부 검증 에이전트의 Agent Card를 읽어 이름과 skill 목록을 확인한다."""
        return await discover_verifier()

    @tool
    async def send_brief_for_verification(brief_text: str) -> str:
        """검증자에게 브리프를 A2A SendMessage로 보내 PASS/NEEDS_REVISION 판정을 받는다."""
        return await verify_via_a2a(brief_text)

    llm = ChatOpenAI(
        model=LIVE_MODEL.removeprefix("openai:"),
        base_url=OPENROUTER_BASE_URL,
        api_key=os.environ["OPENROUTER_API_KEY"],
        temperature=0,
    )
    agent = create_agent(
        llm,
        tools=[discover, send_brief_for_verification],
        system_prompt=(
            "너는 브리프를 외부 검증 에이전트에게 맡기는 에이전트다. 절차를 고정하지 말고 "
            "도구로 판단해라: 먼저 discover로 검증자를 발견해 verify-brief 능력이 있는지 확인하고, "
            "있으면 send_brief_for_verification로 브리프를 보내 판정을 받은 뒤 그 판정을 그대로 보고해라."
        ),
    )
    result = await agent.ainvoke({"messages": [{"role": "user", "content": f"이 브리프를 검증해줘:\n\n{brief}"}]})
    print(result["messages"][-1].content)
#pragma endregion a2a-agent


def offline(brief: str) -> None:
    """키 없는 폴백 — LLM 없이 같은 발견→호출 흐름을 코드로 밟는다(결정만 결정론)."""
    print("① 발견(discover):", asyncio.run(discover_verifier()))
    print("② verify-brief 능력 확인됨 → A2A로 브리프 전송")
    print("③ 판정:\n" + asyncio.run(verify_via_a2a(brief)))


def main() -> None:
    if not wait_for_server(VERIFIER_URL, timeout=2.0):
        print("검증자(:9610)가 안 떠 있습니다. 먼저: uv run python3 ch5-a2a/verifier_agent.py")
        raise SystemExit(1)
    brief = read_brief()
    key = os.environ.get("OPENROUTER_API_KEY")
    if key and key != "sk-or-..." and "--offline" not in sys.argv:
        print("▶ LLM 에이전트가 A2A로 검증자를 발견·호출합니다")
        asyncio.run(run_agent(brief))
    else:
        print("▶ (키 없음/오프라인) 같은 발견→호출 흐름을 코드로")
        offline(brief)


if __name__ == "__main__":
    main()
