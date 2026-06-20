"""Ch3 산출물 — 여러 문서를 나눠 동시에 조사하는 fan-out 오케스트레이터.

Ch2까지 인박스가 classified/*.json 으로 정규화됐다. 이제 그 레코드들을 서로
맞대 본다. 카드 명세서의 거래줄마다 영수증이 있나? 은행 입출금은 계약·세금계산서와
이어지나? 한 사람이 순서대로 보면 느리다. 조사 주제를 나눠 동시에 돌린다.

DeepAgents 하네스가 하는 일
  - write_todos : 무엇을 조사할지 계획을 먼저 세운다.
  - task(서브에이전트) : 주제별로 하위 에이전트에 위임해 fan-out.
  - 파일시스템 백엔드 : 긴 중간 결과를 컨텍스트 밖 research_notes/ 로 저장.
  - 종합 : 노트를 모아 brief_draft.md 로 묶는다.

이 파일은 두 길로 돈다.
  - --mock : 키 없이 결정론적 대사 로직으로 같은 노트·브리프를 만든다(동시 실행).
  - 키 있음 : 메인이 task로 세 서브에이전트(card·bank·spend)에 위임해 live fan-out.

실행:
    uv run python3 ch3-deepagents/research_orchestrator.py --mock
출력: workspace/research_notes/*.md, workspace/brief_draft.md
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analyst import RecordV1
from analyst.paths import (
    CLASSIFIED,
    MANIFEST,
    RESEARCH_NOTES,
    WORKSPACE,
    ensure_workspace,
)

MATCH_TOL = 1.0
BRIEF_DRAFT = WORKSPACE / "brief_draft.md"
SAFE_NOTE = re.compile(r"^[a-z0-9_-]{1,64}$")


# ── 입력: classified 레코드(없으면 gold로 보충) ──────────────────


def load_records() -> list[RecordV1]:
    """Ch2가 떨군 classified/*.json 을 읽는다. 비어 있으면 gold에서 만든다."""
    files = sorted(CLASSIFIED.glob("*.json")) if CLASSIFIED.exists() else []
    if files:
        return [RecordV1.model_validate_json(f.read_text(encoding="utf-8")) for f in files]
    import yaml

    print("  (classified 비어 있음 — gold에서 보충. 먼저 Ch2 intake_graph 실행 권장)")
    docs = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))["docs"]
    return [RecordV1.model_validate({**d["gold"], "신뢰도": 1.0}) for d in docs]


def by_type(records: list[RecordV1], t: str) -> list[RecordV1]:
    return [r for r in records if r.doc_type == t]


# ── 조사 주제(서브에이전트가 하나씩 맡는다) ──────────────────────


#pragma region reconcile-card
def reconcile_card(records: list[RecordV1]) -> str:
    """카드 명세서 거래줄 ↔ 개별 영수증 대사. 영수증 없는 줄을 찾는다."""
    receipts = by_type(records, "영수증")
    card = next((r for r in by_type(records, "명세서") if "카드" in r.merchant), None)
    if not card:
        return "# 카드 대사\n\n카드 명세서를 찾지 못했습니다.\n"
    lines = []
    unmatched = []
    for item in card.items:
        amt = item.amount or 0
        hit = next((r for r in receipts if abs(r.total - amt) < MATCH_TOL), None)
        if hit:
            lines.append(f"- ✅ {item.name} {amt:,.0f}원 ↔ 영수증 「{hit.merchant}」")
        else:
            lines.append(f"- ⚠️ {item.name} {amt:,.0f}원 — 매칭 영수증 없음")
            unmatched.append((item.name, amt))
    note = [f"# 카드 명세서 대사 — {card.merchant} ({card.total:,.0f}원)", ""]
    note += lines
    note.append("")
    note.append("## 확인 필요")
    if unmatched:
        for name, amt in unmatched:
            kind = "구독 추정" if amt < 30000 else "영수증 분실 또는 미수령"
            note.append(f"- {name} {amt:,.0f}원 → {kind}")
    else:
        note.append("- 모든 거래줄에 대응 영수증 있음")
    return "\n".join(note) + "\n"
#pragma endregion reconcile-card


def reconcile_bank(records: list[RecordV1]) -> str:
    """은행 입출금 ↔ 계약·세금계산서·카드 대사."""
    bank = next((r for r in by_type(records, "명세서") if "뱅크" in r.merchant or "은행" in r.merchant), None)
    others = [r for r in records if r is not bank]
    if not bank:
        return "# 은행 대사\n\n은행 명세서를 찾지 못했습니다.\n"
    note = [f"# 은행 입출금 대사 — {bank.merchant}", ""]
    for item in bank.items:
        amt = abs(item.amount or 0)
        hit = next((r for r in others if abs(r.total - amt) < MATCH_TOL), None)
        sign = "입금" if (item.amount or 0) > 0 else "출금"
        if hit:
            note.append(f"- ✅ {item.name} {item.amount:,.0f}원({sign}) ↔ 「{hit.merchant}」 {hit.doc_type}")
        else:
            note.append(f"- ⚠️ {item.name} {item.amount:,.0f}원({sign}) — 대응 문서 없음")
    return "\n".join(note) + "\n"


def summarize_spend(records: list[RecordV1]) -> str:
    """영수증 지출을 카테고리로 모은다."""
    cat = {"식비": ["국밥", "스타벅스", "GS25"], "교통": ["택시", "카카오T"], "생활": ["올리브영"]}
    receipts = by_type(records, "영수증")
    note = ["# 지출 요약 — 영수증 기준", ""]
    total = sum(r.total for r in receipts)
    for c, keys in cat.items():
        s = sum(r.total for r in receipts if any(k in r.merchant for k in keys))
        if s:
            note.append(f"- {c}: {s:,.0f}원")
    note.append("")
    note.append(f"영수증 합계 {total:,.0f}원 · {len(receipts)}건")
    return "\n".join(note) + "\n"


THREADS = {
    "card_reconcile": reconcile_card,
    "bank_reconcile": reconcile_bank,
    "spend_summary": summarize_spend,
}


# ── fan-out (mock: 동시 실행) + 종합 ─────────────────────────────


def fan_out_mock(records: list[RecordV1]) -> dict[str, str]:
    """조사 주제를 스레드로 동시에 돌려 노트를 만든다(fan-out 체감)."""
    ensure_workspace()
    print("  [plan] write_todos →", " / ".join(THREADS))

    def run(name_fn):
        name, fn = name_fn
        text = fn(records)
        (RESEARCH_NOTES / f"{name}.md").write_text(text, encoding="utf-8")
        print(f"  [task] {name} → research_notes/{name}.md")
        return name, text

    with ThreadPoolExecutor(max_workers=len(THREADS)) as ex:
        return dict(ex.map(run, THREADS.items()))


def synthesize(notes: dict[str, str], records: list[RecordV1]) -> None:
    """노트를 모아 brief_draft.md 로 종합한다."""
    flags = [ln for t in notes.values() for ln in t.splitlines() if "⚠️" in ln]
    parts = ["# 인박스 브리프 (초안)", "", f"문서 {len(records)}건을 교차 조사했습니다.", ""]
    parts.append("## 짚어야 할 것")
    parts += (flags or ["- 특이사항 없음"])
    parts += ["", "## 조사 노트", ""]
    for name in notes:
        parts.append(f"- research_notes/{name}.md")
    BRIEF_DRAFT.write_text("\n".join(parts) + "\n", encoding="utf-8")
    print(f"  [synthesize] → {BRIEF_DRAFT.relative_to(WORKSPACE.parent)}")


# 서브에이전트 명세 — create_deep_agent에 그대로 배선되는 하네스 구성(--trace로 열어 본다).
SUBAGENT_SPECS = [
    {
        "name": "card_reconcile",
        "description": "카드 명세서 거래줄 ↔ 개별 영수증 대사. 영수증 없는 줄을 찾는다.",
        "system_prompt": (
            "너는 카드 대사 담당이다. list_records로 레코드를 받아 카드 명세서의 "
            "거래줄마다 같은 금액의 영수증이 있는지 맞춰 본다. 영수증 없는 줄은 금액이 "
            "3만원 미만이면 '구독 추정', 이상이면 '영수증 분실/미수령'으로 표시하고 "
            "write_note('card_reconcile', ...)로 저장한다."
        ),
    },
    {
        "name": "bank_reconcile",
        "description": "은행 입출금 ↔ 계약·세금계산서 대사. 대응 문서 없는 거래를 찾는다.",
        "system_prompt": (
            "너는 은행 대사 담당이다. list_records로 레코드를 받아 은행 명세서의 "
            "입출금 줄마다 같은 금액의 계약·세금계산서·카드가 있는지 맞춰 보고, "
            "대응 문서 없는 줄을 표시해 write_note('bank_reconcile', ...)로 저장한다."
        ),
    },
    {
        "name": "spend_summary",
        "description": "영수증 지출을 카테고리(식비·교통·생활)로 집계한다.",
        "system_prompt": (
            "너는 지출 집계 담당이다. list_records로 영수증을 받아 식비·교통·생활로 "
            "묶어 합계를 내고 write_note('spend_summary', ...)로 저장한다."
        ),
    },
]
ORCHESTRATOR_PROMPT = (
    "너는 인박스 리서치 애널리스트의 오케스트레이터다. 직접 조사하지 말고, "
    "write_todos로 세 조사를 계획한 뒤 task로 card_reconcile·bank_reconcile·"
    "spend_summary 서브에이전트에 한 번에 위임해 fan-out 한다. 세 노트가 모이면 "
    "⚠️ 표시된 줄을 모아 '짚어야 할 것'으로 brief 초안을 정리한다."
)


def trace_harness() -> None:
    """create_deep_agent에 무엇이 배선되는지 연다 — 키 불필요(구성만 출력, 호출 안 함)."""
    print("create_deep_agent에 배선되는 하네스 구성 (키 없이 보는 내부):\n")
    print("  [기본 장비] write_todos(계획) · task(서브에이전트 위임)")
    print("             · 파일시스템(ls·read_file·write_file·edit_file·glob·grep)\n")
    print("  [오케스트레이터 system_prompt]")
    print(f"    {ORCHESTRATOR_PROMPT}\n")
    print(f"  [서브에이전트 {len(SUBAGENT_SPECS)}개 — task로 fan-out 위임, 각자 격리 컨텍스트]")
    for s in SUBAGENT_SPECS:
        print(f"    • {s['name']}: {s['description']}")
    print("\n  핵심: 메인은 직접 조사하지 않는다 — task로 세 워커에 위임하고 요약만 돌려받아 종합한다.")
    print("  task 위임에는 워커별 name·description·system_prompt·tools 정의가 필요하다.")


def build_agent(records: list[RecordV1]):
    """키가 있을 때 — DeepAgents live fan-out.

    메인 에이전트는 조사하지 않는다. write_todos로 계획하고 task로 세 서브에이전트
    (card·bank·spend)에 한 번에 위임한다. 각 서브에이전트는 격리된 컨텍스트에서 돌고
    write_note로 결과만 남긴다 — 메인은 요약만 돌려받아 종합한다(인지 부하의 외주).
    """
    from deepagents import create_deep_agent
    from langchain_core.tools import tool

    @tool
    def list_records() -> str:
        """분류된 모든 레코드를 요약해 돌려준다(문서유형 | 판매처 | 총액)."""
        return "\n".join(f"{r.doc_type} | {r.merchant} | {r.total:,.0f}" for r in records)

    @tool
    def write_note(name: str, body: str) -> str:
        """조사 노트를 research_notes/<name>.md 로 저장한다."""
        if not SAFE_NOTE.fullmatch(name):
            return f"invalid note name: {name}"
        ensure_workspace()
        path = (RESEARCH_NOTES / f"{name}.md").resolve()
        try:
            path.relative_to(RESEARCH_NOTES.resolve())
        except ValueError:
            return f"invalid note name: {name}"
        path.write_text(body, encoding="utf-8")
        return f"saved {name}.md"

    shared_tools = [list_records, write_note]
    # 위 SUBAGENT_SPECS(정적 구성)에 이 실행 도구를 붙여 배선한다.
    subagents = [{**spec, "tools": shared_tools} for spec in SUBAGENT_SPECS]

    return create_deep_agent(
        model="openai:google/gemini-3.5-flash",
        tools=shared_tools,
        subagents=subagents,
        system_prompt=ORCHESTRATOR_PROMPT,
    )


def main() -> None:
    ap = argparse.ArgumentParser(description="fan-out 리서치 오케스트레이터")
    ap.add_argument("--mock", action="store_true", help="키 없이 결정론적 대사")
    ap.add_argument("--trace", action="store_true", help="하네스 구성을 열어 본다(키 불필요, 호출 안 함)")
    args = ap.parse_args()

    if args.trace:
        trace_harness()
        return

    records = load_records()
    print(f"▶ 조사 대상 {len(records)}건")

    if args.mock:
        notes = fan_out_mock(records)
        synthesize(notes, records)
        print(f"\n노트: {RESEARCH_NOTES}\n브리프 초안: {BRIEF_DRAFT}")
    else:
        agent = build_agent(records)
        out = agent.invoke({"messages": [{"role": "user",
              "content": "인박스를 교차 조사하고 짚을 점을 brief 초안으로 정리해줘."}]})
        print(out["messages"][-1].content)


if __name__ == "__main__":
    main()
