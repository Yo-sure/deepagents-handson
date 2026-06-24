"""Ch5 산출물 — 브리프를 외부 검증 에이전트에 A2A로 보내 검증받는다(a2a-sdk 1.1+).

흐름: brief.md(없으면 brief_draft.md) 를 읽어 → Agent Card 조회 → SendMessage 로 제출 →
검증 결과를 받아 → verified_brief.md 로 떨군다.

서브에이전트(인프로세스 위임, Ch3)와 A2A(프로세스·팀 경계)의 차이가 여기서 드러난다.
검증 에이전트는 별도 프로세스로 떠 있고, 우리는 그 well-known Agent Card를 먼저 읽어
누가 무엇을 하는지 확인한 뒤 SDK 클라이언트로 메시지를 보낸다.

  --mock  : 네트워크 없이 검증 함수를 직접 호출(오프라인). 같은 verified_brief.md.
  --serve : 검증 에이전트(verifier_agent.py)를 자동 기동한 뒤 A2A로 실제 통신.
  기본    : 이미 떠 있는 검증 에이전트(:9610)에 A2A로 통신.

실행:
    uv run python3 ch5-a2a/a2a_verify.py --serve     # 에이전트 자동 기동 + 검증
출력: workspace/verified_brief.md
"""

from __future__ import annotations

import argparse
import asyncio
import subprocess
import sys
import time
import uuid
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analyst.paths import BRIEF, VERIFIED_BRIEF, WORKSPACE, ensure_workspace

BRIEF_DRAFT = WORKSPACE / "brief_draft.md"
VERIFIER_URL = "http://localhost:9610"


def read_brief(use_draft: bool = False) -> str:
    if use_draft and BRIEF_DRAFT.exists():
        return BRIEF_DRAFT.read_text(encoding="utf-8")
    if BRIEF.exists():
        return BRIEF.read_text(encoding="utf-8")
    if BRIEF_DRAFT.exists():
        return BRIEF_DRAFT.read_text(encoding="utf-8")
    return "# 인박스 브리프\n(brief.md 없음 — 먼저 Ch4 okf_store/brief 절차 또는 Ch3 research_orchestrator 실행)\n"


def write_verified(brief: str, verdict_block: str) -> None:
    ensure_workspace()
    VERIFIED_BRIEF.write_text(brief.rstrip() + "\n\n---\n\n" + verdict_block + "\n", encoding="utf-8")
    first_line = next((line for line in verdict_block.splitlines() if "외부 검증 결과" in line), "")
    if "NEEDS_REVISION" in first_line:
        print("  검증 판정: NEEDS_REVISION")
    elif "PASS" in first_line:
        print("  검증 판정: PASS")
    print(f"  → {VERIFIED_BRIEF.relative_to(WORKSPACE.parent)}")


#pragma region a2a-stream
def _has(msg, field: str) -> bool:
    try:
        return msg.HasField(field)
    except (ValueError, AttributeError):
        return bool(getattr(msg, field, None))


def _texts_from_stream(resp) -> list[str]:
    """StreamResponse(task·message·status_update·artifact_update)에서 텍스트를 모은다."""
    out: list[str] = []
    if _has(resp, "task"):
        for art in resp.task.artifacts:
            out += [p.text for p in art.parts if p.text]
        if resp.task.status.message.parts:
            out += [p.text for p in resp.task.status.message.parts if p.text]
    if _has(resp, "message"):
        out += [p.text for p in resp.message.parts if p.text]
    if _has(resp, "artifact_update"):
        out += [p.text for p in resp.artifact_update.artifact.parts if p.text]
    if _has(resp, "status_update") and resp.status_update.status.message.parts:
        out += [p.text for p in resp.status_update.status.message.parts if p.text]
    return out
#pragma endregion a2a-stream


#pragma region a2a-client
async def verify_via_a2a(brief: str) -> str:
    """Agent Card 조회 → ClientFactory → SendMessage. 검증 결과 텍스트를 돌려준다."""
    from a2a.client import A2ACardResolver, ClientConfig, ClientFactory
    from a2a.types import Message, Part, Role, SendMessageConfiguration, SendMessageRequest

    async with httpx.AsyncClient(timeout=30.0) as http:
        card = await A2ACardResolver(httpx_client=http, base_url=VERIFIER_URL).get_agent_card()
        print(f"  Agent Card: {card.name} (skill: {card.skills[0].id})")
        client = ClientFactory(config=ClientConfig(httpx_client=http, streaming=False)).create(card=card)
        req = SendMessageRequest(
            message=Message(
                role=Role.ROLE_USER,
                message_id=str(uuid.uuid4()),
                parts=[Part(text=brief)],
            ),
            configuration=SendMessageConfiguration(return_immediately=False),
        )
        out: list[str] = []
        async for resp in client.send_message(request=req):
            out += _texts_from_stream(resp[0] if isinstance(resp, tuple) else resp)
        # 진행 메시지는 빼고 검증 결과만
        return "\n".join(t for t in out if t and "대사하는 중" not in t).strip()
#pragma endregion a2a-client


def show_protocol() -> None:
    """A2A 동작 원리를 그대로 보여 준다(키·서버 불필요).

    Agent Card는 verifier_agent가 만드는 그 카드(서버가 /.well-known/agent-card.json에
    노출하는 것과 동일), SendMessage 요청 본문은 실제 a2a 타입에서 직렬화한다.
    """
    import json
    import uuid as _uuid

    from google.protobuf.json_format import MessageToDict

    sys.path.insert(0, str(Path(__file__).parent))
    from verifier_agent import agent_card

    print("A2A = Agent Card 발견 + SendMessage 제출 + Task 상태 추적. 세 단계로 본다:\n")

    print("① 발견 — Agent Card: 서버가 /.well-known/agent-card.json 에 메타데이터와 skill 목록을 노출한다.")
    card = MessageToDict(agent_card())
    print(json.dumps(card, ensure_ascii=False, indent=2))
    print("  ※ protocolVersion은 최상위가 아니라 supportedInterfaces[] 안에 있다(흔한 오해).")

    print("\n② 제출 — SendMessage: 클라이언트가 브리프를 Message(parts=[Part(text=…)])로 보낸다.")
    from a2a.types import Message, Part, Role, SendMessageConfiguration, SendMessageRequest
    msg = Message(role=Role.ROLE_USER, message_id=str(_uuid.uuid4()),
                  parts=[Part(text="<brief.md 본문>")])
    req = SendMessageRequest(
        message=msg,
        configuration=SendMessageConfiguration(return_immediately=False),
    )
    req_json = MessageToDict(req)
    req_json.setdefault("configuration", {})["returnImmediately"] = False
    print(json.dumps(req_json, ensure_ascii=False, indent=2))

    print("\n③ 처리 — Task 라이프사이클: 서버가 상태를 단계로 올린다.")
    print("   SUBMITTED → (start_work) WORKING → (add_artifact: verdict) → (complete) COMPLETED")
    print("   클라이언트는 그 Task/artifact 스트림에서 검증 결과 텍스트만 거둔다.")
    print("\n인프로세스 위임(Ch3 서브에이전트)과 다른 점: 상대가 다른 프로세스·다른 팀이라")
    print("먼저 카드로 요청 가능한 skill과 endpoint를 확인하고, 표준 SendMessage 요청으로 보낸다.")


def wait_for_server(url: str, timeout: float = 15.0) -> bool:
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        try:
            resp = httpx.get(f"{url}/.well-known/agent-card.json", timeout=2.0)
            if resp.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(0.4)
    return False


def main() -> None:
    ap = argparse.ArgumentParser(description="브리프 A2A 외부 검증")
    ap.add_argument("--mock", action="store_true", help="네트워크 없이 검증 함수 직접 호출")
    ap.add_argument("--serve", action="store_true", help="검증 에이전트를 자동 기동 후 통신")
    ap.add_argument("--card", action="store_true", help="A2A 동작 원리(Agent Card·SendMessage·Task) 출력, 키·서버 불필요")
    ap.add_argument("--draft", action="store_true", help="workspace/brief_draft.md를 우선 제출")
    args = ap.parse_args()

    if args.card:
        show_protocol()
        return

    brief = read_brief(use_draft=args.draft)
    print("▶ 브리프 제출 → 외부 검증 에이전트")

    if args.mock:
        sys.path.insert(0, str(Path(__file__).parent))
        from verifier_agent import verify_brief
        ok, notes = verify_brief(brief)
        verdict = "PASS" if ok else "NEEDS_REVISION"
        block = (f"## 외부 검증 결과 — {verdict}\n검증 주체: 세무·정합성 검증 에이전트 (직접 호출)\n\n"
                 + "\n".join(f"- {n}" for n in notes))
        print(f"  검증 결과: {verdict}")
        write_verified(brief, block)
        return

    proc = None
    if args.serve:
        if wait_for_server(VERIFIER_URL, timeout=1.0):
            print("  기존 검증 에이전트 재사용")
        else:
            proc = subprocess.Popen([sys.executable, str(Path(__file__).with_name("verifier_agent.py"))])
            if not wait_for_server(VERIFIER_URL):
                print("  검증 에이전트 기동 실패")
                proc.terminate()
                return
    try:
        block = asyncio.run(verify_via_a2a(brief))
        print("  검증 결과 수신 (A2A)")
        write_verified(brief, block)
    finally:
        if proc:
            proc.terminate()


if __name__ == "__main__":
    main()
