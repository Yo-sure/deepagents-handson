"""Ch2 산출물 — 인박스 적재 파이프라인을 StateGraph로 묶는다.

Ch1의 단발 추출(classify_one)을 상태·재시도·중단점이 있는 흐름으로 끌어올린다.
문서 한 장이 그래프를 이렇게 통과한다.

    classify ─→ verify ─→ (review?) ─→ persist
                  │           │
                  └ 재시도     └ 고액·저신뢰면 interrupt() 로 사람에게 멈춰 묻는다

핵심 학습점
  - StateGraph : 노드·엣지로 흐름을 명시한다(create_agent의 자율 루프와 대비).
  - checkpointer : thread_id 별 상태를 저장해 interrupt 후 같은 자리에서 재개한다.
  - 재시도 : verify 실패(합계 불일치)면 classify로 되돌린다(상한까지).
  - interrupt() HITL : 고액(≥1,000,000)·저신뢰(<0.7) 건은 자동 통과시키지 않는다.

실행:
    uv run python3 ch2-langgraph-agent/intake_graph.py --mock          # 전체 적재(자동 승인)
    uv run python3 ch2-langgraph-agent/intake_graph.py --mock --doc invoice_photo.png
출력: workspace/classified/<문서>.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

# Ch1 부품을 그대로 재사용한다 — "부품은 갈아끼우고 계약은 재사용".
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analyst import RecordV1  # noqa: E402
from analyst.paths import CLASSIFIED, ensure_workspace  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ch1-llm-basics"))
from classify_one import extract, load_gold, verify_total  # noqa: E402

HIGH_VALUE = 1_000_000  # 고액 기준(원)
LOW_CONFIDENCE = 0.7    # 저신뢰 기준
MAX_RETRY = 2


class IntakeState(TypedDict, total=False):
    doc: str            # sample_inbox 파일명
    mock: bool
    record: dict        # RecordV1 dump(노드 간 직렬화 가능 형태로 운반)
    retries: int
    flagged: str        # 사람 검토가 필요한 사유("" 면 자동 통과)
    sum_ok: bool        # 영수증 합계 검증 결과(분기용)


# ── 노드 ─────────────────────────────────────────────────────────


def classify(state: IntakeState) -> dict:
    """문서 한 장을 RecordV1로 추출한다(Ch1 부품 재사용)."""
    rec = extract(state["doc"], model="google/gemini-3.5-flash", mock=state["mock"], react=False)
    print(f"  [classify] {rec.merchant} · {rec.total:,.0f}원 · 신뢰도 {rec.confidence:.2f}")
    return {"record": rec.model_dump(by_alias=True, mode="json")}  # classified/*.json = 한글 키


def verify(state: IntakeState) -> dict:
    """영수증이면 합계를 검증하고, 검토 플래그를 매긴다."""
    rec = RecordV1.model_validate(state["record"])
    flagged = ""
    if rec.total >= HIGH_VALUE:
        flagged = f"고액({rec.total:,.0f}원)"
    elif rec.confidence < LOW_CONFIDENCE:
        flagged = f"저신뢰({rec.confidence:.2f})"
    ok, item_sum = verify_total(rec)
    if rec.doc_type == "영수증" and not ok:
        print(f"  [verify] 합계 불일치(항목합 {item_sum:,.0f} ≠ {rec.total:,.0f})")
        return {"flagged": flagged, "sum_ok": False}
    print(f"  [verify] 통과{' · 검토 필요: ' + flagged if flagged else ''}")
    return {"flagged": flagged, "sum_ok": True}


def review(state: IntakeState) -> dict:
    """고액·저신뢰 건은 interrupt()로 멈춰 사람의 결정을 받는다."""
    rec = state["record"]
    decision = interrupt({
        "사유": state["flagged"],
        "판매처": rec["판매처"],
        "금액": rec["금액"],
        "문서유형": rec["문서유형"],
        "질문": "이 분류를 그대로 적재할까요? (approve / reject)",
    })
    if decision == "reject":
        print("  [review] 반려 — 적재 보류")
        return {"flagged": "rejected"}
    print("  [review] 승인 — 적재 진행")
    return {"flagged": ""}


def persist(state: IntakeState) -> dict:
    """검증된 레코드를 classified/<문서>.json 으로 떨군다."""
    if state.get("flagged") == "rejected":
        return {}
    ensure_workspace()
    out = CLASSIFIED / (Path(state["doc"]).stem + ".json")
    out.write_text(
        json.dumps(state["record"], ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"  [persist] → {out.relative_to(out.parents[2])}")
    return {}


# ── 엣지(분기) ───────────────────────────────────────────────────


def after_verify(state: IntakeState) -> str:
    if state.get("sum_ok", True) is False:
        if state["retries"] < MAX_RETRY:
            return "retry"
        return "persist"  # 상한 도달 — 일단 적재하고 검토 큐로
    return "review" if state["flagged"] else "persist"


def bump_retry(state: IntakeState) -> dict:
    print(f"  [retry] 재분류 {state['retries'] + 1}/{MAX_RETRY}")
    return {"retries": state["retries"] + 1}


def build_graph():
    g = StateGraph(IntakeState)
    g.add_node("classify", classify)
    g.add_node("verify", verify)
    g.add_node("retry", bump_retry)
    g.add_node("review", review)
    g.add_node("persist", persist)
    g.add_edge(START, "classify")
    g.add_edge("classify", "verify")
    g.add_conditional_edges("verify", after_verify,
                            {"retry": "retry", "review": "review", "persist": "persist"})
    g.add_edge("retry", "classify")
    g.add_edge("review", "persist")
    g.add_edge("persist", END)
    return g.compile(checkpointer=InMemorySaver())


def run_one(graph, doc: str, mock: bool, auto: str = "approve") -> None:
    """문서 한 건을 흘려보낸다. interrupt가 걸리면 auto 결정으로 재개한다."""
    config = {"configurable": {"thread_id": f"intake-{doc}"}}
    print(f"\n▶ {doc}")
    state = {"doc": doc, "mock": mock, "record": {}, "retries": 0, "flagged": ""}
    result = graph.invoke(state, config=config)
    if result.get("__interrupt__"):
        payload = result["__interrupt__"][0].value
        print(f"  ⏸ interrupt — {payload['사유']} · {payload['판매처']} {payload['금액']:,.0f}원"
              f" → 자동 결정 '{auto}'")
        graph.invoke(Command(resume=auto), config=config)


def main() -> None:
    ap = argparse.ArgumentParser(description="인박스 적재 StateGraph")
    ap.add_argument("--doc", help="한 건만 처리(미지정 시 sample_inbox 전체)")
    ap.add_argument("--mock", action="store_true", help="키 없이 gold로 적재")
    ap.add_argument("--reject-flagged", action="store_true", help="검토건을 자동 반려")
    args = ap.parse_args()

    graph = build_graph()
    auto = "reject" if args.reject_flagged else "approve"

    if args.doc:
        run_one(graph, args.doc, args.mock, auto)
    else:
        import yaml

        from analyst.paths import MANIFEST
        docs = [d["file"] for d in yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))["docs"]]
        for d in docs:
            run_one(graph, d, args.mock, auto)
    print(f"\n적재 위치: {CLASSIFIED}")


if __name__ == "__main__":
    main()
